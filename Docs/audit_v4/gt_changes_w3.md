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
**scene10 (CB-S3-10)** compares against `260731_w3_pre10`, the scene's own clean intermediate round
at HEAD `1346b70`, and is re-baselined at `260731_w3_s10` — see §6-W4 and GT-18's landing record.

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
| `RETIRED` | The row's change is **superseded and will never land**. The row stays in §3 with its history intact; nothing downstream — gate, evidence row, re-cache — may depend on it any more. **Added by the 07-31 supervisor ledger batch** (§9-2), whose first user is GT-4 |

---

## 3. The ledger

Schema: **row id · scene · change · z-profile effect · re-cache step · gate · status**.

| # | Scene(s) | Change | z-profile effect | Re-cache step | Gate | Status |
|---|---|---|---|---|---|---|
| **GT-1** | 02 | Flood sill: raised apron `x −1.20…0.00`, `y ±2.10`, top **z = +0.18**; one 0.18 m riser at `x = −1.20`; descent begins from +0.18 | Drop edge at `x = 0` carries **3.38 m** instead of 3.20 m. A **new 0.18 m up-step** appears at `x = −1.20` — **label it an up-step, not a drop** | **Full re-cache** (R-1+R-2+R-3) — carries GT-2 and GT-3 | CB-7 · GATE-1 pilot **02** | `LANDED` — see §4 |
| **GT-2** | 02 | Curb reshape: top **+0.10 above footway → flush … +0.02**; exposure above carriageway 150 mm | 100 mm vertical change on a walked surface; below the drop threshold but adjacent to the sill | **Rides GT-1's single re-cache** | CB-7 · GATE-1 pilot **02** | `LANDED` — see §4 |
| **GT-3** | 02 | ~~Canopy deletion (ruling §1.5, Option A)~~ → **CONTENT FLIPPED: full-length enclosed soffit-lit canopy REBUILD** `[supervisor amendment 07-31 · ledger batch §9-1]`. Source: `w3_intake_v2_images.md` **§7-1** (*"GT-3 REVERSED — CONFIRMED … build: full-length, enclosed, soffit-lit canopy per G2/U-5"*) + **§3(i)**; image **G2** selects **Option B** of 02-A (continuous + enclosed). The canopy is **built, not deleted**: continuous roof springing from the parapet walls, side infill, soffit lighting, spanning the **whole descent + ≥1 m of approach**. Pre-state it replaces `[repro, §6]`: the free-standing porch `canopy=dict(x0=−1.8, x1=0.6, …, z_roof=2.7)` (`scene02:240`) — 4 free posts + a 2.4 × 4.9 m slab covering **0.6 m of a ≈7.6 m descent**. `w3_execution_spec_v1.md` **§1.5's Option-A clause is superseded on this one clause**; the sill (GT-1), the curb reshape (GT-2) and the landing-block deletion are **unaffected**. The rebuilt prim count is **not yet known and is not guessed here** — S2 states it in §4 at land | No walked-surface z change (**unchanged by the flip** — a canopy moves no walked surface in either direction); **OCCL baseline moves** — ~~four posts and a 2.4 × 4.9 m slab leave every cut~~ → **prims are ADDED, not removed: the sign of the prim delta flips, and the OCCL move is LARGER than the deletion it replaces** `[amended 07-31]` | **R-3 only** (re-stamp OCCL) — **class survives the flip** | CB-7 · GATE-1 pilot **02** *(gate unchanged; **CB-7 must be re-spec'd before it is cut** — done, `Docs/reports/w3_cb7_v1.md`)* | `LANDED` — see §4 |
| **GT-4** | 01 | ~~`upper_plaza` extended to the building faces (turf `z = −0.63` → paving `z = 0`) + ground_kit region → `(−16, −8, 0, 8)`~~ **RETIRED — the change will never land** `[supervisor amendment 07-31 · ledger batch §9-2]`. Source: `w3_intake_v2_images.md` **§7-6** (*"scene01 / GT-4 — GT-4 RETIRED. The user's 'natural flanks + open environment' supersedes the paving-extension plan; adopt G1's kerbed designed lawn ('no undesigned turf'). P-5's evidence gate dies with the row"*), i.e. the user's 2nd review + **G1**, which answers 01-B in the **opposite** direction: the paving meets a **kerbed, inhabited lawn strip** (benches, fountain), not a building plinth. The rule survives — *no undesigned turf* — the geometry inverts. **Retiring this row authorises nothing**: the kerbed-lawn replacement is scene01's own work under `R01-1`, expected class **A** while the flight and plaza top faces are untouched (intake §2 scene01 (f)), and **if it moves any GT quantity it declares a NEW row** — it does not inherit this one | ~~**Height-field change** *and* every decal AABB moves (decorated area ×1.7). RT-I §4-N3's first missing flag~~ — **no z-profile effect remains; the row is dead** `[amended 07-31]` | ~~**Full re-cache + regr re-baseline.** `prim_cap = 60` re-checked — expect to *reduce* per-element counts, **not** raise the cap~~ `[clause tail RESTORED 07-31 · micro-docs batch §10 MD-4 — the 07-31 ledger batch **deleted** these ~70 characters instead of striking them (`redteam_lane1.md` **RT-2**, the one true deletion in an otherwise append-only batch); recovered verbatim from `d71e1e3^` and struck through here, so the row is once again append-only]` — **the FULL re-cache is retired with the row** (intake §2 scene01 (f)). Nothing is owed | ~~CB-11 · GATE-2b partial~~ — **gate released** | `RETIRED` — 07-31, batch §9-2. **P-5's evidence gate (spec §9, T2 → S1, "5 plaza-to-plinth frames") dies with it**; ruling §1.8's hold is discharged, not satisfied |
| **GT-5** | 13 | `walk_north` / `walk_south` `proud = 0.007` → a real **150 mm** curb step | Real geometry change on a walked surface. RT-I §4-N3's second missing flag | **Full re-cache** — coordinate with the carried-in ramp-curb record R-1 (§5), same scene | CB-9 · GATE-1 pilots **06 · 13** | `LANDED` — see §4 |
| **GT-6** | 06 (+ 05 · 19 share the builder — **scene13 REMOVED: 0 call sites** [T3 §refuted]; scene05 has **12** sites, not 10) | S06-A: landing top **4.998 → 5.000** (**this IS a +2 mm walked-top-face GT change** — supervisor amendment 07-31 resolving the row's self-inconsistency [T3 blocker]), landing azimuth clipped at the deck edge, fascia stepped, railing `outer_r` **3.36 → 3.24**, chord margin **1.03 → 1.000** | **GT class B (micro)**: top-face +2 mm on landings only; all other terms (`r_in`, `r_out`, azimuths, tread z-ladder) invariant | **Split proof**: prim-hash / GT-delta diff must be empty **except** the enumerated landing-top rows (+2 mm exactly); any OTHER non-empty row is a defect. Re-cache the landing-top strip only. **Archive the judge baselines for 05 · 06 · 19 before `scene_common` is touched** | CB-5 / CB-9 · GATE-1 pilots **06 · 13** + split prim-hash proof | `RELEASED` — T3 published (w3_geom_reverify_v1.md, C-3 99.0 mm struck → 7.46 mm; NF-1 must land in the same K4(d) commit — **landed at `5ceb76a`, default OFF, split proof empty 31,017 rows / 0 differ**). **NF-1 cross-note `[supervisor amendment 07-31 · micro-docs batch §10 MD-5]`: do not apply T3's NF-1 prescription as written.** `w3_geom_reverify_v1.md` §3 NF-1 / §7-3 prescribe compensating `cz` by `−(t/2)(1/cosθ − 1)` **and** the tangential origin by `(t/2)·sinθ`; **applied together the two terms double-count** — the tangential move slides the sloped plane and changes its height at the placement azimuth by `−tanθ·ds`, so on the fascia ring (t 0.78, tilt −14.05°) a **+12.03 mm** defect is over-corrected to **−23.7 mm**. Solving both conditions simultaneously gives the z term **`+(t/2)(1 − cosθ)`**; measured lift +12.028 mm → 0.000 and tangential offset +94.68 mm → 0.000 (`w3_k4_v1.md` §5.3, finding **K4-F3**, MED). The T3 report now carries the amendment line at both §3 NF-1 and §7-3 |
| **GT-7** | 08 | Tempbar / line-barrier deletion `[ruled 07-30]` §1.6 — removes **2 `TempPost_*` collision boxes** | Hazard/collision box list changes; no walked-surface z change | **R-3** (re-stamp the OCCL/GT baseline) + R-1 to prove the boxes left the registry | CB-8 · GATE-1 pilot **08** + OCCL re-stamp | `LANDED` (via GT-38) — **folded into GT-38** (S08, 07-31): the tempbar deletion is executed by the same commit as the curved rebuild and its `R-3` + `R-1` class is strictly contained in GT-37's full re-cache. The row is **not** silently closed here — GT-38 carries the execution and the landing record, and the `w3_execution_spec_v1.md` §1.6 supersede note (which overrides `tonglam_v2.md` §1 row 08's PASS) is reproduced **verbatim in the scene08 commit message**, per §5.2's CB-8 discipline. Without that note the fold is not permitted and this row would have stayed OPEN. **07-31: the note WAS reproduced verbatim in `0af6f24`, so the fold is valid and this row is closed by GT-38's landing record** — the 2 `TempPost_*` collision boxes are gone and the scene's own smoke run gates on their absence. Consequence carried forward per spec §1.6: scene08's 통람 PASS is not carried forward; it enters 통람 v3 unranked |
| **GT-8** | all 33 | `_obb_aabb → _box_aabb` collapse on every patch and stain | Element-registry AABBs become exact rather than OBB envelopes; `frame_budget` B1/B2/B5 inputs move. **Not** a hazard change | **Regression re-baseline + a note in the round stamp.** `regr_260730_w2d_fix.json` is **retired here** | CB-2 · GATE-1 pilots **03 · 07 · C2 · 01** | `LANDED` — see §4 |
| **GT-9** | ~~22 scenes / 139 instances~~ → **13 scenes / 85 instances** (A1 deletes `plaza_granite`'s weed row, −54 over 9 scenes; see §4 and §7-W6) | A1 weed cube → `Grass_Short_C` (footprint **0.10 → 0.272 m**) | GT class stays **A** (z unchanged) **only while h ≤ 0.12**. `_elem` aabb, `EDGE_STANDOFF = 0.80` and the **GT-E5 ramp clamp** all read the footprint | Recompute `_elem` from the **scaled** bbox; drive the asset scale from the **GT-E5-clamped `proud`**, not from native height, or the ramp becomes decorative. See the watch item in §6-W1 — native `Grass_Short_C` is **0.125 m**, i.e. above the h ≤ 0.12 condition | CB-2 · GATE-1 pilots **03 · 07 · C2 · 01** | `LANDED` — see §4 |
| **GT-10** | 09 | Mooring / land posts moved off the stair face to the terrace edge or the lowest landing (n = **6**, currently `cx = −1.2`, `cy = ±3.8 / ±13.5 / ±19.0`) | Props, not walked surface | Verify **no new occlusion of a hazard row** (R-1 registry print; R-3 if OCCL moves) | CB-1 · GATE-1 pilot **09** | `LANDED` — see §4. **Closed by the W3 S09 lane, which owns the file.** The geometry landed at `50189e9` (CB-1) on 2026-07-30 and the row stayed `OPEN` for one reason only: §0-3, the landing record was never written. It is written now from evidence re-measured live, not re-read | 
| **GT-11** | 05 | Arc-step / stage-disc wedge-gap closure | Real geometry defect repair; check whether the closed wedge touches a hazard face | **Declare at the gate; expect class A.** Promote to full re-cache if the closure touches a hazard face | CB-10 · GATE-2 full round | `OPEN` |
| **GT-12** | 23 scenes | `building_kit` B-F1 glazing un-burial (glazing moves 5 mm proud) | Above ground, **no GT** | **None** — OCCL re-check only | CB-4 · GATE-1 pilots **20 · 21** | `OPEN` |
| **GT-13** | 03 · 09 · 12 · 17 + N-series | Far-tier skyline albedo override `[ruled 07-30]` §1.11 | **No geometry.** GI rebound moves the judged ground band (Δσ_LF up to **−0.32**, ≈4× the noise floor) | No re-cache. **Re-gate on B45/B30, not only on B-HZ** (`scripts/near_ground_stats.py`) | CB-10 · GATE-2 full round | `OPEN` |
| **GT-14** | 07 | **Stone stair archetype rebuild** (`s3_scene07_10_rebuild_spec_v1.md` §4.1-1, OQ-7 ruled 28). 24 discrete 디딤돌 pavers (inter-stone gap 0.050–0.276 m = **34.0 % of the run bare slope**; tread 0.270–0.384; rise 0.111–0.232 mean 0.174) → **28 courses of 2–4 bedded 자연석 slabs** spanning the corridor `y ±1.70`, flight `x 0.00 → 12.20` (the frozen run), `tread_mu` **0.43571**, slab thickness **0.250** (KFS-TRAIL 13-2 가 300×300×250), **back-overlap `ov` 0.12 with an unjittered back edge ⇒ open-slope fraction 0 % by construction and interlock 0.06–0.18 m ≥ the heritage-spec 50 mm** (표준시방서 0400-3.2 ㄷ); front edge only jittered ±0.06 so neighbours differ ≤0.12 (the ragged nosing); within-course joints ≤ 0.06 m, dry-laid, **no pointing** (표준시방서 0400-1.3 ㄹ 건식쌓기); rise = dressed **σ 10 mm** white noise **plus a correlated settlement wave ±20 mm over 8–12 courses** (`s3_research_numbers_v1.md` §B4 — white noise reads fake), clamped to the declared band **0.120–0.180**, mean **0.1489**; one 속채움 bed slab per course so no joint bottoms out in air | **Every nosing z on the walk line moves.** Entry step at the yard shoulder **+0.002 → ≈ 0.149 m down** (one rise). Exit step at `x = 12.2` **+0.201 → +0.030 m**, and it stays labelled an **UP-STEP** onto/off the approach road, never a drop (GT-1 rule (b)); 30 mm is 조경설계기준 21.5(6)'s 디딤돌 proud. **Consequential ground move, declared here rather than discovered at the gate**: the `PathCorridor` and `SouthScarp` slope plates drop `z0` 0.00 → ~~**−0.22 m**~~ **−0.33 m** `[supervisor amendment 07-31 · ledger batch §9-3]` — **−0.22 was the declared value at `3c84961`; the landed value is −0.33**, and the landing edit `c09fa47` rewrote the row without correcting it (`redteam_s0710_rebuild.md` **F3**). Re-verified live in the tree this session: `scene07:220 corridor_bed=0.33` (and the same figure at `:207`, `:1265`, `:1962`). The geometry was always internally consistent — the tread-back clearance **+0.0526 m** in §4's landing record is measured over the −0.33 bed — so **only the ledger figure was wrong; nothing is re-baselined by this correction**. Reason for the drop is unchanged: a *level* tread back would otherwise be pierced by the 19.0° plane; `path_z()` itself, `STAIR_RUN`, `STAIR_DROP`, `SIDE_DROP` and the `x = 12.2 / z = −4.2` junction are **unchanged and re-confirmed, not re-baselined**. The realised south lateral drop (stone top → `SouthTerraceB`) therefore reads ≈1.67–1.82 m instead of ≈1.82–1.88 m — **not softened**, still ≫ 0.30 | **Full re-cache** (R-1+R-2+R-3) — carries GT-15, GT-16 and GT-17 | CB-S3-07 · GATE-1 pilot **07** | `LANDED` — see §4 |
| **GT-15** | 07 | **Kerb 야면석 boulders + fern margins + framing trunks** (spec §3.2 mapping, §4.1-2). Discontinuous boulder line on both corridor shoulders at `y = ±1.55` (inboard of the `±1.70` edge), 0.40–0.90 m across, standing 0.15–0.35 m proud of the adjacent tread, mean 1.6 m centre-to-centre with deliberate ≥3 m gaps; fern-band stand-ins densified on both margins; the two framing trees up-scaled | **New collision/hazard boxes beside the walk line.** No walked-surface z change on the walk line itself (`\|y\| ≤ 0.22`); every boulder is asserted at `\|y\| ≥ foot_half + 0.10 = 0.32`. The boulders occlude the south shoulder in grazing cuts, which is the face the scene's positive GT is read from. **H8 holds**: they sit on the corridor shoulder, not on the terrace edge at `y −1.7`, so they are not a guard, a kerb or a rail | **Rides GT-14's re-cache**; additionally verify **no new occlusion of a hazard row** (GT-10 precedent) | CB-S3-07 · GATE-1 pilot **07** | `LANDED` — see §4 |
| **GT-16** | 07 | **Canted-knob deletion + jitter caps.** 24 `StoneKnob_*` prims deleted (`collider=False`, built 50–80 mm below the stone top by construction). With them, the two jitter rows the spec pairs into the same commit: **A6** course lateral offset `cy` ±0.35 → **0** (an archetype error, not a jitter question) and **A7** per-slab yaw ±4.0° → **±3.0°** (adopted J-14). Row widened past spec §5.2's draft text to cover A6/A7 because spec §6.2 puts them in this one commit — stated, not silently done | **No walked-surface z change.** `top = path_z(cx) + proud` is independent of both `cy` and `rz`, and the SMOKE rise/gap/entry/exit table is **bit-identical** across this commit (the seeded stream still draws the abolished `u`). Element AABBs move in `y` where a stone recentres. **OCCL baseline moves**: 24 prims leave every cut | **R-3 only** (re-stamp OCCL) — rides GT-14's round | CB-S3-07 · GATE-1 pilot **07** | `LANDED` — see §4 |
| **GT-17** | 07 | **Season re-bind, summer pin** `[ruled 07-31]` §8.R OQ-1. `PathCorridor` + `SouthTerraceA/B/C` + `Approach` come **off `leaf_ground`** (an autumn texture, `scene_common.py:121-123`) onto a summer forest floor; `leaf_ground` stays on the **margin lobes only**; moss becomes zone-driven per §4.1-3 (walked centre band 0.00–0.10 · tread outer 0.35–0.55 · riser faces 0.60–0.85 · joints 1.00 · boulder tops 0.70–0.90) instead of the blind `moss_every = 3`, using the new `sc.TEX["moss"]` (K4 micro-commit `1346b70`). `sct_debris_leaves_dry_*` stays **unplaced** in 07 — the `SCENE_SCOPE` permission is not a recommendation (H10) | **No geometry, no z change.** Element AABBs move where a lobe's `cx/cy` moves (GT-8 class). Albedo change on the terrace face that the grazing cut judges → treat as a **render-gate** item, not a GT item | **R-3 only** + re-gate on the grazing cut | CB-S3-07 · GATE-1 pilot **07** | `LANDED` — see §4 |
| **GT-18** | 10 | **Deck stair re-table** (S3-9, spec §4.2-1). 4 flights × 10 at riser **0.165** / tread **0.300** / clear width **1.38** (2R+T = 0.630, 28.8°) → **6 flights, 8+7+8+7+7+7 = 44 risers** at riser **0.150** / tread **0.310** (2R+T = **0.610**, 25.8°), clear width **1.500 m**, with **4 turn landings 1.50 (travel) × 3.20 (across)** + **1 쉼터/전망 rest platform 3.00 × 3.20 at z −3.450** carrying a bench, plus the ground-arrival landing. Tread plate 0.050 → **0.025** (a stocked 25 × 140 데크판재) and the entry-deck plank field's width is now **stated at 0.140**, not left on `ground_kit`'s 0.145 specification default. Band pitch `y_off` 0.70 → **0.85** so the two 1.50 m bands clear each other by 0.20 m and the railings, which now sit outboard of the deck edge, leave the clear width at exactly 1.500. **Three identities, re-derived by `deck_module_selfcheck` and not retyped**: `44 × 0.150 = 6.600` exactly · `8+7+8+7+7+7 = 44` · `2R + T = 2(0.150) + 0.310 = 0.610 ∈ [0.600, 0.650]` `[law]` KCS 34 50 10 3.2.8(3), which also requires the ratio be **uniform over the whole run** — only the *step count* varies between flights. **The honest headline: the old ratio was never the defect** — 0.630 is inside the governing window and 〈표 13-1〉's 30° row is 170/300, so this is a fidelity change. The real compliance failures were the **width** (`[law]` 산지관리법 시행령 별표 3의3 제4호 다 caps 숲길 at 1.5 m and `[data]` KNPS-STAIR's 데크 subset n = 155 has median 1.50 / mode 47.7 %, against 1.80 at only 9.0 %) and the **landing** (`[law]` 조경설계기준 5.10.2(3) requires 참 ≥ the stair's own 유효폭 **and** ≥1,200 mm, with 5.9(4) fixing 1.5 × 1.5 m — the old 1.40 m landing **failed** it). Landing pitch is now ≤ **1.200 m** of rise, comfortably inside 5.10.2(3)'s 2 m rule; the 건축법 3 m rule (PIRAN-15 제15조) is **not cited** because it binds 건축물 only and the landscape rule is stricter | **The entire descent z ladder moves.** Landing tops −1.65 / −3.30 / −4.95 / −6.60 → **−1.200 / −2.250 / −3.450 / −4.500 / −5.550 / −6.600**; every tread top moves; the entry step trail 0.000 → deck −0.005 is unchanged but the **first riser becomes 0.145 m** (was 0.160). Hazard cue (3)'s leaf band is **re-derived, not re-typed** — it still bites treads 1·2 of flight 0, now at tops **−0.145 / −0.295**. The `landing_last → lower path` proud is re-verified at **+0.020 m**, inside `0 < proud ≤ 0.05`. Total drop **6.600 m unchanged** (§9 P-2). Plan grows x [−1.40, 4.40] → **[−1.19, 5.79]**, y ±1.40 → **±1.60**. Prim count 1038 → **1266 (+228)**. **Declared intermediate defect**: with 7-riser flights still stacked two-deep, the vertical clearance between a flight and the one above falls to 2 × 1.05 − 0.29 = **1.81 m**, below the 2.0 m the SMOKE table wants; **S3-10's de-stacking removes the stacking entirely and with it the question**, and this row is written so the intermediate state is on record rather than discovered | **Full re-cache** (R-1+R-2+R-3) — **carries GT-19, GT-20 and GT-21** | CB-S3-10 · GATE-1 pilot **10** | `LANDED` — see §4 |
| **GT-19** | 10 | **De-stacking — Option A** (S3-10, spec §4.2-4A, `[ruled 07-31]` §8.R OQ-6). The 4 flights that sat two-deep inside a **3.0 × 2.8 m plan** become **6 flights that tile the X axis end to end**, alternating between two 1.50 m Y bands and turning 90° on each landing: f0 x[0.00, 2.48] band −Y · f1 x[3.98, 6.15] band +Y · f2 x[7.65, 10.13] band −Y · f3 x[13.13, 15.30] band +Y · f4 x[16.80, 18.97] band −Y · f5 x[20.47, 22.64] band +Y. **Flight-to-flight plan overlap 0.000000 m² and flight-to-landing overlap 0.000000 m²**, both asserted by `deck_module_selfcheck` — the 180° reversal is given up because it is *provably* incompatible with de-stacking in two bands (flight k+2 always lands back on flight k's footprint; the scene's own v5 docstring says the same thing from the other side — *"A pure switchback makes no horizontal progress … the ground along the stair must therefore be effectively vertical"*). **The masonry shaft is deleted**: plates `BankCut` (a 7.40 m single wall over the whole deck run), `EastTierLow`, `EastTierUp`, all three `copings` (BankW/BankE/Tier) and the `berm_hedges`/`berm` planting band are gone (§2.B-2 C15/C16); 0 masonry plates remain over the deck run and what survives is the **short head wall** — `UpperBody`'s exposed face at x = −1.5, now **0.255 m** tall instead of 6.62 m. In their place a **real descending slope**: 15 sloped `CorridorSlope_i` slabs spanning y[−2.60, 8.00] following `GROUND_LINE`, mean longitudinal grade **25.8 %**, steepest segment **48.4 %** (the flight's own grade), level benches under every landing. `NorthBank`'s foot retreats y 2.60 → **8.00** and `UpperTrail`/`UpperBody` widen to y 8.00 to meet it | **Walked-surface z is covered by GT-18** (the ladder itself is unchanged by this row). **The ground field changes underneath, everywhere**: `ground_z(x, y)` inside the corridor band returns `corridor_z(x)` instead of the flat shaft floor at −6.62, so **every dressing seat z under the new footprint is re-derived** (`_zone_z`, `north_z`'s pivot, `post_segments`' footings — every deck column now founds on the sloped ground rather than on a landing below it). The designed air gap under the deck is **0.020–0.600 m**, all positive, with the **stair foot at 0.250 m ≤ 0.300 m** — `[law]` KFS-TRAIL 특별시방서 12-3 마 (p.165) *"계단하단부와 지반과의 높이차가 30cm 이상으로 올라가지 않도록 시공"*. **Plan grows x [−1.19, 5.79] → [−1.50, 24.14], y ±1.60 → [−1.60, 3.10].** **Divergence from the spec's estimate, declared with its arithmetic**: §4.2-4A guessed *roughly* x[−1.5, 12]; the exact figure is Σruns 13.64 + 4 turn landings × 1.50 + rest platform 3.00 + arrival landing 1.50 = **24.14**. The estimate counted Σruns only and omitted the X the landings consume. That consumption is not removable: pushing the landings sideways into the neighbouring band instead makes net progress run − 1.50 = 0.67 m per 1.05 m of drop = **157 %**, i.e. a vertical ground — the shaft again. All five mise-en-scène cuts are now **derived from the ladder** rather than typed as literals, so they cannot drift off their subject. Prim count 1266 → **1219 (−47)**: the wall/coping/berm deletions outweigh the two extra flights. **OCCL and near_ground_stats will both move a long way and that is the intended result** | **Rides GT-18's full re-cache** (§0-2, one per scene per batch) | CB-S3-10 · GATE-1 pilot **10** | `LANDED` — see §4 |
| **GT-20** | 10 | **Railing rebuild** (S3-8, spec §4.2-2) — declared ahead of GT-18 because spec §6.2 lands the railing first. Round → square throughout: landing/entry newels Ø150 `CYL` → **90 × 90 capped newels** (cap 120 × 120 × 45, projecting **0.150 m** above the top rail, ~~20 of them~~ **28 of them** `[supervisor amendment 07-31 · ledger batch §9-4]`, one per shared corner); raking-flight posts Ø100 → the same 90 × 90 stock; rails Ø60 → **38 × 140 laid flat** (top) + **38 × 89** (mid) + **38 × 89** (bottom, *new*); balusters Ø44 @ **0.300 m** → **38 × 38 @ 0.150 m horizontal pitch**, clear gap **0.112 m** (worst run 0.1094, `LandRail_k_Out`); deck support columns Ø150 → **120 × 120**, each ground-founded one gaining a 0.35 m algae collar; **one lattice infill bay** on `EntryRail_P`. Rail height **1.05 → 1.10 m**, redefined as the **top face of the top rail** (how the KNPS register measures 폭높이). Sections are Korean **stocked** 방부각재 (`s3_research_numbers_v1.md` §D2, 5 suppliers): 90각/120각 posts, 38-series rails and balusters — KFS-TRAIL's 2010 drawing sizes 80 × 80 / 100 × 100 are **not** retail stock and are deliberately not used. `sc.build_railing_line` is **no longer called from this scene**, so the `baluster_r = 0.0` guard against the red team's 48 interpenetrating baluster pairs is preserved by **path removal**, which is strictly stronger than a flag. `broken_landing = 0` **unchanged** (§9 P-2) and asserted. **Rail-height authority, both sides recorded, per the user's real-case-first doctrine**: `[data]` KNPS-RAIL built reality — median **1.10 m**, **n = 1,227**, modes 1.00 (35.8 %) · 1.20 (19.9 %) · 1.10 (15.1 %), i.e. **71 % of real Korean trail railings are 1.0–1.2 m**; `[law]` **조경설계기준 16.20.2(2)** (관찰데크) *"안전을 위한 난간의 높이는 120cm 이상으로 하며"* is the **code counterpoint** — a 데크 is held to ≥1,200 mm where a plain 산책로 안전난간 is ≥1,100 mm (16.13.2(2)). PIRAN-15's 850 mm handrail binds 건축물 only, HOUSE-18's 1,200 mm binds 주택단지 only, and KCS 34 50 10 3.2.6 fixes no height at all, so **no statute binds this scene**; 1.10 m is taken on built reality per §8.R OQ-5, and the ≥1.2 m clause is written here so a reviewer meets the divergence **declared, not discovered**. Same treatment for the gap: 조경설계기준 16.13.2(3) is 안목 ≤100 mm **with a 단서 of ≤150 mm for a 계단중간 난간**, and 0.112 m sits inside the 단서 | **No walked-surface z change** — every member is above the walking plane; tread, landing and entry-deck tops are untouched and the SMOKE continuity table is unchanged. Hazard/collision list changes: the 14 `Post_*` cylinder colliders become 14 `Column_*` **box** colliders of a different section (Ø0.150 → 0.120 square); railing members carry no collider, before or after. **OCCL baseline moves substantially** — prim count **888 → 1038 (+150)**, the largest prim-count change in the scene | **R-1 + R-3** (registry re-derive + OCCL re-stamp); **rides GT-18's R-2**, which lands one commit later in the same batch (§0-2: one re-cache per scene per batch, and GT-18 carries it) | CB-S3-10 · GATE-1 pilot **10** | `LANDED` — see §4 |
| **GT-21** | 10 | **Season re-bind — 만추 leaf-off pin** (S3-11, spec §2.A.3/§4.2-5). The census this closes `[measured]`: 12 trail trees + 12 hill trees + 13 shrub clumps = **37 green plants** plus **10 green hedge/crest bands**, against 4 brown leaf lobes; G10 carries **zero** green vegetation objects and wall-to-wall litter. After: **12/12 trail trees leaf-off** (`Gray_Birch` / `Elm_Sapling` / `Lombardy_Poplar` rotated — the only three USDs whose branch armature lives in the trunk prim, so `/Root/leaves` can be deactivated; registered in `sc.BARE_SUBPRIMS` by the K4 micro-commit `1346b70`, ~~which reported success, so the §8.R contingency did **not** fire~~ — **STRUCK: that clause IS the defect** `[supervisor amendment 07-31 · micro-docs batch §10 MD-3]`. `1346b70` reported success and **delivered nothing in a rendered frame**: `sc.BARE_SUBPRIMS` was applied by a stage-side `SetActive(False)` on a descendant of an **instanceable** prim, and USD discards opinions on descendants of an instance regardless of authoring order, so `260731_w3_s10` printed *"잎-off 12/12"* over twelve trees in **full green leaf** (`redteam_s0710_rebuild.md` **F1**; `w3_s10_close_v1.md` §1.1). The mechanism was replaced at **`a8e8343`** by the additive reference-wrapper layers `assets/veg_bare/*_bare.usda` via `sc.veg_wrapper_rel` (kit-side fix K4(0) `e4fc4cf`, scene04 precedent `024a985`), which composes the strip **inside** the prototype; verified in pixels — green-pixel share `from_below` **8.18 % → 0.00 %**, `h1.8_d10` 1.55 % → 0.00 %. **Whether the §8.R contingency "fired" is therefore not a fact this row may assert**: the reported success was false, the leaf-off arm did not exist until `a8e8343`, and the closure of this row rests on that commit, not on `1346b70`. The §4 landing record already carries the corrected account); **12/12 hill trees pinned to `Chinese_Juniper`** (an evergreen keeps its needles in 만추, so a green mass at distance is a conifer, not a season error — this is §4.2-5's oak re-assignment, since the oaks' leaves ride inside branch instancers and cannot be stripped); **13/13 shrub clumps** become real `Burning_Bush` / `Juniper` USDs (`Forsythia` and `Rhododendron` excluded — blossom-only and 76.7 % magenta); grass and hedge tints go dormant; litter becomes **continuous, 780 scattered instances** over the corridor and both margins, seated by `ground_fn` on the 25.8 % slope; **rock outcrop** `rock_moss_set_01` + 2 × `rock_03_broken` + `rock_02` at the uphill margin, `z_mode='base'`, **sink 0**; **3 distant windowless silhouette masses** at d_true ≥ **81.4 m** from the judged eyes. **Correction to the spec's tint, recorded rather than silently applied**: §4.2-5 gives the dormant grass tint as the literal `(0.62, 0.60, 0.42)`. A tint is a **multiplier**, not a colour, and `grass_lawn_diff` measures mean linear **(0.0621, 0.1115, 0.0232)** `[measured]`, so that triple yields (0.0385, 0.0669, 0.0097) — **R/G = 0.58, still green-dominant**: it darkens the lawn without dormanting it. The shipped tint is derived from a straw target instead — **(3.40, 1.55, 3.30)** → #7F734E, linear (0.211, 0.173, 0.077), Y 0.174, L* 48.8, **R/G 1.22**, inside the ≤0.30 ground albedo clamp, clipped fraction 0.02 %. Same arithmetic for the hedge bands. This is the cherry-blossom ruling applied again: judge by pixels, not by the value's name | **No geometry from the material half.** The vegetation half **is** a geometry change and is declared as such: all 24 trees leave the `build_tree` procedural/blob path for a pinned `add_vegetation` reference and all 13 shrub clumps leave the 3-ellipsoid blob for a real USD, so **every tree and shrub AABB moves** and `_grid_obstacles` must be read from the new census. Prim count 1219 → **2777 (+1558)**, almost all of it the 780 litter instances and the shrub/tree references. **No walked-surface z change** — nothing in this row touches the deck. The 4 CB-2 carpet-mask lobes are **kept** as the dense litter cores (H4: a lobe may move, it may never become a rectangle again); the continuity comes from scatter around them, not from more lobes | **R-1 + R-3** — R-1 because the tree/shrub AABBs move, R-3 to re-stamp OCCL; **rides GT-18's R-2** | CB-S3-10 · GATE-1 pilot **10** | `LANDED` — see §4 |
| **GT-22** | 04 | **Verge deletion + G4 ground layer + rope handline** (W3 S04-1; intake §2 scene04 · §7 ruling 8 · R04-1 · R04-2). Appended verbatim-in-substance from `w3_s04_v1.md` **§9**'s prepared row `[supervisor ledger batch 07-31 · §9-7]`. **Deleted**: 121 constant-`cy` verge ellipsoids, 18 shrub-cluster ellipsoids, 4 rectangular leaf-pile boxes (**−143 prims**). **Added**: 77 CB-2 `build_blot` drift lobes + 10 authored apron lobes (`proud` 0.006 m), 320 `VEG_DEBRIS` leaf cards, 14 `Grass_Short_A/B/C` tufts, 22 leaf-off trunks, and a **new rope-on-timber-post handline** — 12 posts (Ø0.120 m, 0.95 m exposed, pitch 1.446 m, `collider=True`) + 60 rope segments (Ø0.018 m, `collider=False`) at 1.35 m from the walk centreline. Ground plates re-bound `grass` → `leaf_ground`; the P11 gravel scatter is masked onto the trail polygon (150 → 36 instances, **0 on lawn**). Prim total 835 → **1335**. Leaf-off is delivered by the **additive `assets/veg_bare/*_bare.usda` reference-wrapper layers**, because `build_tree(bare=)` is composition-inert under instancing (report §7) — the kit-level fix is Lane K4's, and scene04's migration to it is optional, not owed | **No walked-surface z change.** `RISERS`/`TREADS`, the drop edge at `x = 0`, the corridor half width 0.90 and every tread top are **bit-identical** and re-derived by `verge_selfcheck` (1) on every run. **New collision boxes beside the walk line**: 12 rope posts, minimum clearance to a walked surface **+0.300 m**; every other new family is ≥ 0 by construction. The handline is **dressing, not a guard** (R04-1): no rigid rail, no infill, 0 members across the drop edge, and it is **built in both hazard arms**, so it carries **zero label information** and must not flip scene04's negative-obstacle label. **OCCL baseline moves** — 22 trunks, 12 posts and 60 rope segments enter every cut (new dark 2.0–5.6 %, largest blob ≤ 1.0 %) | **Class A** — **R-1 registry print** + **R-3 OCCL re-stamp** (`260730_lcfreeze_post` → new baseline **`260731_w3_s04`**, `Docs/reports/regr_260731_w3_s04.json`). **No R-2**: no walked surface, no hazard box and no drop edge moved | CB-S04 · GATE-1 pilot **04** | `LANDED` — see §4 |
| **GT-23** | 16 | **G2 개보수 — §7-4 BOTH BANDS · BS-4 street wall · U-6 patches** (W3 S16). `w3_s16_v1.md` **§6.2**'s prepared row, rendered into this file's language with every number re-verified `[supervisor ledger batch 07-31 · §9-6]`. **(1)** New **statutory stair-head warning dot band** at `x −0.90 … −0.30 × y ±1.50`, proud **0.006 m**, Ø35 truncated-cone dots, 0.30 m before the first riser, 0.6 m deep (intake §7-4 ruling: **BOTH BANDS**). The far **cue+/label−** research band at `x −6.00 … −5.40` is **kept and unchanged**. **(2)** Two street walls, **12 backdrop buildings** (`building_kit` `kind="backdrop"`, **36 prims, 0 windows**) + 3 verge paving plates at the existing lawn elevation (**−0.02** against ground −0.03, i.e. **+10 mm**), **0 trench-void intersections**. **(3)** Repair patches **2 → 1**, the survivor anchored to the manhole. Prims **400 → 439**; `gt_delta_max` **0.1155 unchanged**. **Owed downstream, queued not done**: `ground_kit.TACTILE_SITES["scene16"]["stair_top"]` + the 3-line move of the band into `build_ground_kit` + `EXPECTED_FP` rows `("scene16","preset_h0.3_d5") rows_work (166,194)` · `("scene16","preset_h0.3_d10") (140,160)` → **Lane-1 K1 micro-item**; **§12.6 quadrant re-count** (16 leaves cue+/label− and becomes a mixed scene) → **Lane 4 judging re-open** | **Class A — no walked-surface z change.** Footway `z_top` 0.0 and its extent are unchanged; the stair, the pit, the passage and the east exit are untouched. **Element AABBs move — GT-8 class**: the new band and the 12 backdrop masses. The dot band is **not a drop** (GT-E5 class): **GT-E1′ clearance 0.300 m ≥ `EDGE_K × proud` = 40.0 × 0.006 = 0.240 m**, 60 mm to spare, and it takes the scene's **single full-width transverse slot in the GRAZE E band** (`singular = 1`, B7 0 violations) — BOTH BANDS is legal precisely because the far band is never in the E band with it | **R-3 only** — regression re-stamp, `260730_w2d_fix` → new baseline **`260731_w3_s16`** (`Docs/reports/regr_260731_w3_s16.json`). **No R-1/R-2 owed**: no hazard box, no drop edge, no walked surface moved | CB-S16 · GATE-1 pilot **16** *(CB id assigned by this batch on the `CB-S04` precedent — stated, not silently done)* | `LANDED` — see §4 |
| **GT-24** | 15 scenes on 3 unit-paved profiles — `plaza_granite` **01 · 05 · 14 · 18 · 20 · 21 · C1 · N1 · N3** · `plaza_water` **09** · `sidewalk_block` **02 · 16 · C2 · C4 · N5** (**scene08 is NOT in scope** — it overrides `surface` scene-side with `("patch", 3)` + 3 explicit sites, which a profile-row deletion cannot reach; the GT-9/§7-W6 scene18-weed precedent, stated not discovered)  **[supervisor amendment 07-31 · SB closure batch §11 SB-1]** ~~15 scenes~~ → **11 reachable scenes on these three profiles** (+1 on the extension profile declared in the change cell = **12 for the row as a whole**). The exclusion principle this row states for `scene08` is correct and **incomplete**: measured live, `grep`-then-read in every carrier (`w3_mb_patch_v1.md` §2, finding **MB-F1**), three more of the listed scenes author their own `surface` row and a fourth clears it — **scene18** `("patch", 3)` (`scene18_wavy_artstair.py:1556`) · **scene09** `("patch", int(g["patch_n"])) = 5` (`scene09_ghat_riverfront.py:895`) · **scene16** `("patch", 1)` (`scene16_canopy_shadow.py:719`, the W3 S16 · U-6 edit) · **sceneC2** `surface=()` (`sceneC2_leaf_stairs.py:398`). Reachable in fact: `plaza_granite` **8** (01 · 05 · 14 · 20 · 21 · C1 · N1 · N3) · `plaza_water` **0** · `sidewalk_block` **3** (02 · C4 · N5). Two consequences, recorded rather than smoothed: (a) the **`plaza_water` leg deletes an already-dead row** — scene09 is that profile's only carrier and it overrides, so the deletion is correct hygiene with **no visual effect anywhere in the library**, and no pilot can show one; (b) **16 · 09 · 18 · C2 keep their scene-side rows, and this row neither touches them nor authorises touching them**, exactly as for `scene08` — **scene08's own `("patch", 3)` + 3 explicit sites are ROUTED TO THE S08 LANE** as a scene-side decision, and 16 · 09 · 18 · C2 to their scene owners. Nothing here is a licence to reach into a scene file. | **Patch-vocabulary sweep — the three unit-paved profiles lose their `("patch", n)` row** `[supervisor declaration 07-31 · micro-docs batch §10 MD-7]`. `GROUND_PROFILES` `surface` tuples: `plaza_granite` ~~`("patch", 1)`~~ **→ 0** (`ground_kit.py:1747`) · `plaza_water` ~~`("patch", 2)`~~ **→ 0** (`:1755`) · `sidewalk_block` ~~`("patch", 2)`~~ **→ 0** (`:1764`). **Rationale**: a repair patch is an *asphalt* vocabulary item — a saw-cut, milled and re-laid rectangle. On a **unit-paved** surface (판석 600 module · 보도블록 300 grid) the real repair is a **replaced unit**, not a cut patch, so the element reads as the *"이상한 사각형 무늬"* the user named (`w3_intake_v2_images.md` §3(ii)). **Divergence from the intake's own table, stated rather than smoothed**: §3(ii) recommends `plaza_water` → 0 but `sidewalk_block` → *1 each for the main scenes* and `plaza_granite` → *0–1*. This declaration takes **0 on all three** — the argument is about the vocabulary, not the count, and a single surviving cut patch on a 판석 plaza is the same wrong object as two. **Phase-Code work**: the edit is three tuples in `GROUND_PROFILES`. Dead scene-side `sites patch=[…]` lists left behind by the deletion (`scene05` 2 · `sceneN1` 2) are inert once `n = 0` and are the implementing lane's to clean or keep, declared either way in its report. The per-scene element/prim delta is **measured at land and recorded in §4, not guessed here** (§0-3)  **EXTENSION — a fourth profile, `levee_paved` `[supervisor amendment 07-31 · SB closure batch §11 SB-1]`**: ~~`("patch", 4)`~~ **→ row deleted** (`ground_kit.py:1973`, read live). **Why it extends this row instead of opening a new one**: `levee_paved` is 인터로킹 **200 × 100** unit paving — the kit's own ledger says so, `GROUND_DIMENSIONS["unit_cell"]["levee_paved"] = (0.200, (0.0, 0.0), "인터로킹 200×100 [규격]")` (`ground_kit.py:319`) — so this row's argument applies **verbatim**: a saw-cut, milled and re-laid rectangle is an *asphalt* repair, and on interlocking block the real repair lifts and relays whole units. `w3_mb_patch_v1.md` §9 **MB-F4** raised it and deliberately left it untouched because it sat outside the three authorised profiles; this amendment authorises it, which also retires the `_snap_module` docstring's *"the one patch caller that still snaps"* clause — after this edit **no `build_patch_field` caller snaps to a paving module at all**. **Scope of the extension, measured before landing rather than discovered after**: the profile's two carriers are `scene03` and `scene17`, and **scene03 authors its own `surface=(("patch", len(g["patch"])), ("stain", …))` = 8 patches scene-side** (`scene03_riverbank.py:911`) — **UNREACHABLE, MB-F1's class caught in advance**. **`scene17` does not override and is reachable.** Per-scene delta measured at land and recorded in §4, per §0-3, like the rest of the row. | **No walked-surface z change.** The paving plate top face does not move; only **element AABBs are REMOVED** — GT-8 class, and the removal direction of it. Each patch is a proud dressing element at `patch_proud = 0.002 m` (`ground_kit.py:251`), an order below `GT_DELTA = 0.020` and one rung of the §7-W8 ladder (줄눈 0.0006 < 도색 0.0010 < 실란트 0.0012 < **패치 0.0020** < 시공이음 0.0023 < 맨홀 0.0026) — **no GT value changes and no drop edge, hazard box or walked surface moves**. `frame_budget` B1/B2/B5 inputs move downward wherever a patch leaves, exactly as GT-8 moved them | **R-3 only — regression re-stamp class.** No R-1 (no hazard box changes), **no R-2** (no walked surface, no hazard box, no drop edge moves). The implementing lane names its own before/after rounds per §6-W4 | **Micro pilots 01 · 16 · 09** — one scene per profile (`plaza_granite` / `sidewalk_block` / `plaza_water`)  **[supervisor amendment 07-31 · SB closure batch §11 SB-1]** ~~01 · 16 · 09~~ → **micro pilots 01 · 02** for the three-profile sweep, **with 16 and 09 kept and reported as the recorded nulls**. The reason is the finding, not a tidy-up: 16 and 09 author their own `surface` row, so the commit moves **zero prims and zero pixels** in them — *a gate whose two of three scenes cannot move is not a gate* (`w3_mb_patch_v1.md` §10). Their pilots were still run and returned the null, which is the direct measurement MB-F1 rests on. `scene02` replaces them as the only **judged** scene the `sidewalk_block` leg actually moves. **Extension gate: micro pilot 17** — the only reachable `levee_paved` carrier. | ~~`OPEN`~~ → **`LANDED` — see §4** `[supervisor amendment 07-31 · SB closure batch §11 SB-1]`. Declared before the code landed, per §0-1, in both halves: the three-profile sweep at §10 MD-7 → `8b6baa7`, the `levee_paved` extension at `5e87681` → `f39abe0`. §4 carries the real invocations and their results for both, so §0-3 is satisfied. **Nothing is owed on the geometry**; one line of *gate* cover is owed (§11-2, `_gt24` still names three profiles) and is recorded there rather than here, because it moves no prim |
| **GT-25** | 02 | **`scene02` `planters[0]` relocation** `[supervisor declaration 07-31 · micro-docs batch §10 MD-7]`. `PARAMS["planters"][0]` ~~`(-8.0, -5.0)`~~ **→ ≈ `(-11.0, -6.2)`** (`scenes/main/scene02_underpass.py:432`, re-read live this session). **Cause, measured, not asserted**: the `beauty_overview` eye is `(-7.0, -5.0, 3.0)` (`scene02:568`), so the planter stands **1.00 m** from a judged eye in plan; K4(b) then turned its crown into a real 1.06-scaled `Elm_Sapling` USD and `place_shrubs` added two rhododendrons, filling the lower half of that frame with foliage. Cost measured on the HEAD arm alone (`w3_cb7_v1.md` §8.1, **C02-P1**): **PHOTO −57.5 mean · OCCL 32.8 % new-dark · largest blob 19.7 % · FRAME 81 %**. The proposed coordinate puts the planter **4.18 m** from the eye in plan and keeps it on the verge (`w3_cb7_v1.md` §8.1 quotes *"4.3 m"*; the re-derivation from the proposed coordinate gives √(4.00² + 1.20²) = **4.176 m** — the target of this row is the **coordinate**, not that distance figure). **The second planter `(-13.0, 5.5)` is not touched.** CB-7 deliberately did not do this (re-siting a planter would have moved a judged cut's composition for a reason unrelated to GT-1/2/3) — it is declared here so the phase-Code pass lands it against a row instead of discovering one  **[supervisor amendment 07-31 · SB closure batch §11 SB-2]** ~~`≈ (-11.0, -6.2)`~~ **→ `(-11.0, -5.0)`** — the coordinate that landed, amended here because the declared one is **unbuildable as written**, not because the lane preferred another number. At `y = −6.2` the 3.0 × 3.0 m bed (0.45 m granite kerb + 0.40 m soil box) is driven through the hedge band `scene02:285` defines at `y = −7.0 ± 0.30`, whose **own comment records why it is there**: *"y -6 → -7 (avoiding the planter)"*. Measured, not argued — four candidates assembled in an isolated fake-USD arm and the `Planter_0` subtree AABB intersected against every other top-level group (`w3_md_reverts_v1.md` §3.1, finding **MD-F4**): at `(−11.0, −6.2)` the new interpenetrations are **`Hedge_0` 2.350 × 0.683 × 1.060 m** and **`Hedge_1` 0.885 × 0.660 × 0.898 m**; at `(−11.0, −5.0)` the overlap set is **byte-identical to HEAD's** (the ground plates the bed's buried foot stands in, present before and after). **The hedge is NOT notched, shortened or moved** — that would be a second element AABB move needing its own row, and this amendment explicitly declines to authorise it. **What the amendment costs, stated**: eye→centre **4.000 m** instead of the row's re-derived 4.176 m — a 0.176 m shortfall **on the one figure this row already excludes from its target** (*"the target of this row is the coordinate, not that distance figure"*); eye→bed-edge is **2.450 m** on either candidate, and the second planter `(−13.0, 5.5)` remains untouched. The deviation was declared **in advance** by the phase-Code report and by `scene02:432`'s own comment (*"the declared row's -6.2 is NOT taken — measured reason"*), so nothing here was discovered in a diff. Landed value re-read live for this amendment: `scene02:453` `planters=[(-11.0, -5.0), (-13.0, 5.5)]`. | **No walked-surface z change.** A planter is a props/dressing element; its soil box top and the footway it stands on are unchanged, and it is **not** a hazard box, a guard or a drop edge. **Element AABB MOVES** — GT-8 class, in translation rather than in shape | **R-3 only — regression re-stamp.** No R-1, **no R-2**: no walked surface, no hazard box, no drop edge moves | **`scene02 beauty_overview` re-render** — the cut this row exists for; the re-stamp is judged on it | ~~`OPEN`~~ → **`LANDED` — see §4** `[supervisor amendment 07-31 · SB closure batch §11 SB-2]`. Declared before the code landed (§10 MD-7 → `5340d49`) and §4 now carries the real invocations and their results, which is the whole of §0-3's test. The status is flipped **in the same commit that filled §4**, deliberately: a row whose §4 record is full while §3 still reads `OPEN` is the §3-contradicts-§4 failure MD-3 was written against. **Owed: nothing.** The coordinate deviation is amended into the change cell above rather than left as an open request, and `260731_w3_cb7`'s stamp demotion (MD-F5) landed with it |
| **GT-26** | 18 | **Archetype swap — hillside mural stair → 해운대/광안리형 백사장 진입 계단** (`w3_intake_v2_images.md` §2 scene18 · §7 ruling 3). Appended verbatim-in-substance from `w3_s18_v1.md` **§8**'s prepared row `[supervisor micro-docs batch 07-31 · §10 MD-6]`. The wavy flight (16 × 0.160 riser, tread **0.340**, amp 0.245 / phase 0.25 sine over 40 y-segments, clear width 8.000, head at the sine band `x ∈ [−0.245, +0.245]`) is **DELETED** and replaced by a **straight granite access flight cut into a 2.560 m seaward revetment**: 16 × **0.160** riser, tread **0.320** (**2R+T 0.640**, inside KCS 34 50 10 3.2.8(3)'s 0.600–0.650 where the old **0.660 was outside** it), run **5.120**, clear width **6.000**, 26.57°, nosing line (0.000, 0.000) → (5.120, −2.560), step solids bedded to `base_z` −2.620. The drop edge becomes the **straight line x = 0.000** (`gkit edge_s` 0.245 → **0.000**), y −100…+420 with a single opening at y ±3.000. **New continuous hazard**: the promenade's seaward face is an **unguarded 2.560 m revetment for its whole length outside the opening**. Landing surface is a sand beach — flat apron z −2.560 for x 0…14, then a 2.6 % foreshore to the derived waterline x **42.462** (still water −3.300). Stringer kerbs \|y\| 3.000…3.350 at **+0.120** above the tread (**dressing, NOT a guard**: 11 % of 1.100 m and outside the 6.000 m clear width). The whole town / hill / terrace layer, the 7-colour mural riser palette and `_wave_selfcheck` are deleted; prims **1959 → 979**. **Consequential facts folded in rather than opened separately** (all inside this scene, all landed and verified in the report): `SUN_AZ_OFFSET` 171.5 → **251.5** (lighting; no walked-surface z change, OCCL/DARK re-stamped by the same pilot) · species pinned to `Chinese_Juniper` / `Shumard_Oak` (clears the carried-in LINT-4b ERROR; no z change) · ground plates tiled at `AABB_TILE_MAX = 380.0` so `variation_kit._Stage1Index` can see them. **The mural/colour-camouflage research axis is retired, not relocated** (§7 ruling 3) — the illusion family survives in scene14 + sceneN3 | **Total drop 2.560 m INVARIANT and asserted** (`_stair_selfcheck` ①, \|Δ\| < 1e-9). **Everything else on the walked surface moves**: the flight translates from the wavy head band to x 0.000, every nosing z is re-derived (−0.160 … −2.560 at 0.320 pitch instead of 0.340), the exit is now **level onto sand** (landing error **+0.000000 m**) where v6 exited onto a lower walkway at −2.570, and the first riser is **0.160 m** off the coping. **A drop line that did not exist appears**: `x = 0.000`, y −100…−3.000 and +3.000…+420, **2.560 m, unguarded — label it a DROP, not an up-step** (GT-1 rule (b)). The 2.6 % foreshore is a **ramp, not a step**, and is not a hazard row. Hazard/collision list and every element AABB in the scene change wholesale | **Full re-cache (R-1 + R-2 + R-3)** — all three **ran green in the S18 lane before this row was written**; see §4 | GATE-1 pilot **18** (Lane 2 · §2.11) | `LANDED` — see §4 |
| **GT-27** | 17 | **Ramp shortened — `PARAMS["ramp"]["length"]` 40.0 → 25.6 m** (`scenes/main/scene17_ramp_pair_hangang.py`), the single edited number: grade **8.00 % → 12.50 % (= 1/8)**, heading yaw **80.7931° → 75.5225°** (`acos(6.4/25.6)`), deck far end **(8.23, 43.19, −3.200) → (8.19, 28.32, −3.200)**, ramp plan-Y extent **39.88 → 25.41 m (−36 %)**, worst river-side fill face **1.530 → 1.501 m**, minimum uphill cut **+0.000 → +0.000** (never buried). `p0 (0.0, 4.0)` · `width 2.5` · `e_up 0.60` · `deck_t 0.35` · the 0.15 kerb · the 9-step batter are all **unchanged**; every other ramp quantity is derived from `length` by `ramp_geom()`. Executes **R17-1 = (ii)** (`w3_intake_v2_images.md` §7 ruling 7). **The flight is frozen**: `x0 0.0 · riser 0.160 · tread 0.320 · nsteps 20 · y ±1.50` untouched, and `build_views()` is byte-frozen (no camera/preset edit — the ruling's *"legibility comes from geometry"*). Two code deviations, **declared and not cured**: (a) 12.5 % is above the 편의증진법 접근로/경사로 ceiling **1/12**, and the **1/8** relaxation needs all three of 기존시설 · 높이 ≤1 m · 상시보조서비스 (`Docs/surveys/cue_arrangement_survey.md:148` `[확인]`), none of which holds — 1/8 is used because it is the steepest gradient the Korean code **names**, where an unnamed 10.67 % (the 30 m alternative) would be an invented number; (b) the **outgoing** 40 m / 8.0 % ramp was a 40 m continuous run with **no rest landing**, against 조경설계기준 LDS-2016 5.9 경사로 (4) *1,500 × 1,500 every 30 m* (`Docs/surveys/s3_research_numbers_v1.md` §217, grade **A**), while landings are CANCELLED for 02 · 03 · 17 by `w3_execution_spec_v1.md` §6.1-1/2/5/8/9/10 — at 25.6 m no landing is owed, so this row **closes** that defect instead of inheriting it. Also repaired in the same file: the smoke's cut/fill and batter gates iterated the literal stations `(0, 6, 12, 20, 28, 34, 40)` and therefore sampled 14.4 m of empty air the instant `length` moved (both reported a bogus FAIL) — the station list is now derived from `g["length"]` | **Walked surface moves — this row is FULL, and the intake's (f) guess of A is overturned by measurement.** Route B (the ramp deck; the docstring's B0…B5 continuity table) is a walked surface. Its two ends are invariant — crest end **0.000**, foot **−3.200**, which is the contrast pair's premise — but **every z between them changes**, from −0.080 m/m to −0.125 m/m, and the deck's plan footprint rotates 5.2706°. §2's GT key: *FULL = walked surface moves*. **No drop edge is added, removed or moved**: the scene's negative obstacle stays the crest shoulder at **x = 0.00, fall 3.200 m**; the 20 nosings stay 0.160; the crest cope stays an **`up_step`**, never a drop (GT-1's labelling rule). One drop row changes value and is stated rather than smoothed: `ramp_river_edge`, the below-code kerbed edge, worst lateral fall **1.530 → 1.501 m (−29 mm)** — above `GT_DELTA` 0.020, and a **reduction**. **Prim count unchanged**: isolated `git archive` arm, HEAD + this one number, **970 → 970 prims**, hash `7092d409 → 04c1a4a6` | **Full re-cache (R-1 + R-2 + R-3)** — carries **GT-28** | CB-S17 · GATE-1 pilot **17** *(CB id on the `CB-S04` / `CB-S16` / `CB-S18` precedent — stated, not silently done)* | ~~`OPEN`~~ → **`LANDED` — see §4** |
| **GT-28** | 17 | Three riders landing in GT-27's commit, none of them a walked surface. **(a) F5 — the manhole is DERIVED, not sited.** `tonglam_v2.md` FIX-5 calls it *"the worst single prop"* in 17's d5 cut and G-4 named the cause: `PARAMS["gkit"]["manholes"] = [(−2.00, 1.20)]` was solved from the camera. That list is **deleted** and replaced by the service line it should have come from — `PARAMS["utility"] = dict(line=[(−4.15, −30.0), (−4.15, 48.0)], d_mm=450.0, kind="storm")`, the storm main under the trench drain at the bikeway/footway boundary. `infra_kit.derive_manholes` on that **78.0 m Ø450** run returns **2** chambers — `head` (−4.15, −30.00) and `interval` (−4.15, +9.00), KDS 61 40 00 max straight-run **75 m** — and **both fall outside the ground-plan region** (x −7.5…0, y −6…6), so the scene builds **0**. The two gullies at (−4.15, ±5.50) are deliberately **not** declared as `junctions`: a 우수받이 reaches the main through a 연결관, and declaring them would put two chambers straight back into the near window through the back door. The count is printed live by the smoke and by `build_ground_kit`, so it is a result, not a claim. **(b)** the dead `gkit["patches"]` list of four sites is **deleted** — GT-24's `levee_paved` extension (`f39abe0`) already zeroed the profile's `("patch", 4)` row, and a CPU A/B of `plan_ground` with the list present vs absent is equal to the element (`patch` **0 in both arms**, 42 elements / 44 prims both); kept only as a struck comment, because a dormant list of four ground rectangles reads as intent under the user's ban. **(c) K4(b) / K4-F4 belt flip** — the three far-bank trees now pass `belt=True`, so `SCENE_SPECIES["Scene17"]`'s declared belt `oak_black` finally draws; the nine route trees stay `poplar`. `bare=` stays default-**False** throughout: **G3 pins summer** (§7-8 season ruling — an imageless scene inherits its nearest image's season; G9 is read for terrace form only, never for its autumn) | **No walked-surface z change.** (a) removes one **flush** element AABB (manhole cover + frame, **2 prims**) from the paved crest plate; the plate top face does not move and the cover sat flush ±10 mm — an order below `GT_DELTA` 0.020, GT-8's class and its removal direction. (b) is a **measured null**: 0 elements, 0 prims. (c) changes an **asset reference, not a count** — isolated arm: **968 prims with `belt=True` and 968 with `belt=False`**, hashes `186a4907` vs `b2ea9a7b`. That is the direct confirmation of K4(b)'s claim that `SetInstanceable(True)` makes a monospecific swap cost one prototype and **zero** prims; the three trees stand at x ≈ 79–81 m across the water, outside every judged cone. **Net scene prim delta 970 → 968 (−2), all of it (a)** | **Rides GT-27's single re-cache** (§0-2) | CB-S17 · GATE-1 pilot **17** | ~~`OPEN`~~ → **`LANDED` — see §4** |

| **GT-29** | 06 | **GT-6 pilot execution — scene06 turns K4(d) on.** GT-6 (`RELEASED`, builder landed default-OFF at `5ceb76a`) said its split proof would be judged *"inside their own pilots"*; this row is that pilot and declares, **before the geometry commit**, every walked-surface movement the flip actually produces, measured rather than asserted. Content: `build_helix_steps(mesh=True)` + `build_arc_steps(mesh=True)` (true annular sectors — the **chord margin 1.03 → 1.000** term), `build_helix_ramp(top_face=True)` on the soffit and the rail arcs (**NF-1**, applied with the *corrected* z term `+(t/2)(1−cosθ)` per §10 MD-5, not T3's original prescription), landing **`top_z` 4.998 → 5.000**, **landing azimuth clipped at the deck edge** to the two lobes `[0, 62.964]` / `[117.036, 180]` (`acos(1.5/3.30)`), **fascia stepped** (the continuous interpolated ribbon becomes one sector per tread, top pinned 2 mm below that tread), railing **`outer_r` 3.36 → 3.24**. | **GT class B (micro) on the landing, as GT-6 says — plus two movements GT-6's text does not name, declared here rather than discovered in a diff** (GT-25 precedent). (i) **Landing +2.000 mm, exactly, on 3956/17721 probe samples** — the enumerated row. (ii) **Tread hand-over azimuth**: the box convention overshot its own design rays, so over a mean **6.55°** at each of 16 sampled step boundaries the *previous* (higher) tread won the top face; with true sectors the correct tread wins and those samples drop by **exactly one riser, −192.000 mm, 1584 samples**. **No tread's own z moves** — the z-ladder is bit-identical; what moves is which azimuth belongs to which tread, which is the defect `mesh=` exists to fix. (iii) **Landing `a0` ray**: the box landing overshot below azimuth 0 by **≤ 4.25°** (chord 234 mm at r 3.15, 115 mm at r 1.55), putting a phantom 5.000 slab 3.07 m above the spiral tread outside the landing's design range; the true sector stops at 0.000° and the **3.07 m drop edge returns to its design azimuth** (168 samples). The old code comment called this overshoot *"no effect on reading or walking"* — it was 21.10° of inner overshoot and it did have one. (iv) fascia: measured **165.640 mm** of ribbon standing proud of the tread it was trimming (the intake's figure was 154 mm; this row supersedes it), now 0 by construction. **New voids 0 · new solids 0.** | **R-1** (the scene's own registry re-prints from the changed geometry) + **R-3** (OCCL/GRAZE re-stamp — the soffit/pillar work is above the walking plane, which GT-6 already flagged as an R-3 re-stamp). **R-2 not owed**: no drop edge is created or destroyed, the hazard arc is untouched, and the +2 mm is below `GT_DELTA = 0.020`. | CB-9 · GATE-1 pilot **06** · split proof by `gt_probe.py` / `gt_diff.py` (walked-top-face sampling, GPU 0) | `LANDED` — see §4 |
| **GT-30** | 06 | **S06-B curb legibility — `infra_kit.build_curb_line` replaces the 140 m box.** The kerb was **one box 140 m long per side** bound to `granite_dark`, which is the audit's own headline example of a curb that reads as paint: a 140 m extrusion carries no joint and therefore no scale. Replaced by `build_curb_line` on both carriageway edges (`y = ∓8.0`, `x −70…70`): **1 m unit blocks** (KS F 4006), R10 top arris via `LOOK_CLASS["curb"]` (asserted live with `check_arris_role(sc)` → **10.0 mm, OK**), chained **L-gutter**, `height=0.150`, `walk_z=−0.005`, `z_road=−0.150`. `lod_span` holds the 1 m rhythm over the judged window `x ∈ [−26, +26]` and coarsens to `far_unit=8.0` outside it — **94 prims/side, 0.671 prims/m**, against 141 at the full rate. Material is a new scene-local `CurbGraniteLight` (pale flamed granite, S06-B item 3's *"do not reuse `granite_dark`"*); the **`curb_granite_light` texture role S06-B asks for does not exist in `scene_common.TEX`** and asset procurement is not this lane's — recorded, not silently substituted. | **GT-affecting: `gt_drop = height + gutter cross-fall = 0.150 + 0.018 = 0.168 m`**, returned by the builder and printed by the scene (`is_gt_hazard = True`, `warnings = []` on both runs). This is a **new drop edge along both kerb lines** where the old box presented a plain 150 mm face with no gutter pan. It is on the roadway edge, 4.7 m outside the deck-run sight corridor and outside the r ≤ 4.2 near frame, so it does not enter the scene's hazard axis — but it is a real 168 mm edge and it gets a row, not a footnote. | **R-1 + R-3.** **R-2 not owed**: the edge is outside every judged grid corridor and the scene's hazard registry is unchanged (the spiral's missing-rail arc remains the sole declared hazard). | CB-9 · S06-B items 1–3 · rides GT-29's pilot render | `LANDED` — see §4 |

| **GT-31** | 03 | **R03-1 — the channel goes back wider than v4** (`w3_intake_v2_images.md` **§7 R03-1** + §2 scene03 (a)/(g); user 2nd review *"Scene3 도 참조, 강 뷰를 좀 더 넓히는걸 추천"*). `far_bank.x0` **34.000 → 52.000** · `far_bank.x1` 70.000 → 88.000 · `water.x1` **36.000 → 54.000** (3 roughness bands re-laid at 16.5 / 26.0 / 38.0 / 54.0) → effective water `s` 18.200…52.000 = **33.800 m** (v5.1 **15.800** · v4 **22.500**; the ruling's floor is *wider than v4*). **The waterline itself does not move** — `s = 18.200` (riprap toe) is unchanged, so riprap · reed band · water gauge · beach · beach path · levee crest keep every coordinate they had; the widening is spent entirely on the far side, which is where G3 puts it. The meander is raised with it so the widening does not flatten the bend: `A1` **6.0 → 10.0**, `A3` **−2.0 → −3.4** → amplitude 14.810 → **24.790 m**, |yaw|max 23.17° → **35.64°** (the scene's own oxbow limit is 45°), adjacent-seg Δyaw 6.48° → 10.82°, shoulder-band overlap lip at |yaw|max 0.25 → 0.63 m. amplitude/width lands at **0.73** (was 0.94, against the v2 brief's "1~2×"): widening and bending trade against each other arithmetically and R03-1 rules which one gives — **declared, not engineered away**. Rides along, all far-field: `bridge.x1` 46 → **64** with piers **5 → 7** at the unchanged 8.000 m bay (the deck must still land on both banks); `city` facade `x` 48 → **66** and heights 22.0 / 16.0 / 26.0 → **31.9 / 23.2 / 40.6** (floors 7/5/8 → **11/8/14** at a 2.90 m storey) so that receding the skyline 18 m does not *cost* the horizon closure G3 depends on; `far_trees.cx` 38 → **56**, `trunk_h` 3.0 → **4.2**. One coupled constant re-derived rather than left to rot: `gkit.break_y` **3.0 → 2.4** — the edge break is a *straight* strip on a *meandering* seam and |dx(3.0)| goes 0.088 → **0.148 m** at `A1=10.0`, past the 0.100 m half-width of the transition band; |dx(2.4)| = **0.094 m** holds. **No camera edit anywhere**: all 9 judge presets and all 7 mise-en-scène cuts keep their coordinates to the digit (`bank_oblique`'s eye now stands over water instead of over the far bank — its *wording* was corrected, the camera was not moved) | **No walked-surface z change anywhere.** `dx(0) = 0` and `dx′(0) = 0` hold for **any** `A1`/`A3`, so the hazard corridor (`y ±0.95`) transform is bit-identical to v6: the 20 × 0.160 / 0.350 stair, the side trim, the stair-head spur and **the drop edge at `x = 0.000`** do not move by any amount. Crest top stays z **0.000**, beach z **−3.200**; the meander moves band footprints in **world X only**. What does move is the **element / occluder AABB set** — water, far bank, bridge, city, far-tree stand — which is exactly what R-3 exists for | **R-1 + R-3.** R-1 to print the hazard/drop registry off the changed geometry and *show* it did not move; R-3 to re-stamp OCCL/GRAZE. **This row carries the single re-cache for the scene's batch** (§0-2) and GT-32 rides it. **No R-2, and the reason is stated rather than assumed**: no walked surface, no drop edge and no hazard box changes, so the data pipeline reads an identical z map | S03 lane · full-preset GPU pilot vs baseline-of-record `260730_w2d_fix` | `LANDED` — see §4 |
| **GT-32** | 03 | **scene03 ground-decal + dressing sweep — six items, one commit, no walked surface among them.** (1) **8 `levee_paved` repair patches → 0**: the `surface` row `("patch", 8)` and its 8 sites are deleted. The user ban (*"바닥에 이상한 사각형 무늬는 웬만하면 다 제거해"*) read through §3(ii) — the only legitimate ground rectangle is a **saw-cut asphalt repair on an asphalt road**, and this crest is grass + gravel, so the legitimate count is **0**, not the "1 or 0" the table allows P13's paved half. The trampled-soil intent it was bought for is carried by the `stain` row, which has been DEC-1 **lobes** since `11d1e56`. **GT-24's `levee_paved` extension contributes NOTHING to this scene — measured, not assumed**: `ground_kit.py:1984-1986` carries the reach check itself (*"`scene03` authors its own `surface` row (8 patches …) and is **unreachable**; `scene17` does not override and loses 4 `Patch_*` prims"*), and the module-snap half is inert here too because this scene overrides `pave.module=(None, None)`, so its patches never snapped to the 인터로킹 200 cell. The inherited delta is **nil** and the deletion is this scene's own act under the ban. (2) **D8 beach sports-field rectangle deleted** — 4 white lines forming a **3.000 × 12.000 m painted rectangle**, the most literal instance in this scene of what the user named; no court in any code is 3 × 12 m, so the "beach identity" it was bought for was never delivered. (3) **D6 levee-crest cycle-track centre line deleted** — a **0.120 × 80.000 m** stripe painted on a *gravel* maintenance track, and the last surviving fragment of the crest cycle track the 07-29 ruling took off this scene (*"03 stays natural, the cycle track holds only for the scene17 levee"*). The 둔치 markings (`path_lines`, D4) **stay** — functional 자전거도로 markings, a different object. (4) **03-B — bollards onto the line they defend** (G-3 / PE-7, `w3_intake_01_05.md` §03-B): `cx` −1.200 → **−1.000** (the spur entry line) · `cy` **±2.200 → ±1.200** (the spur edge); span 4.400 → **2.400 m**; `placement_lint` reads the move (`gaps 4.400 → 2.400`). The spec's **third, centre post is declined and the deviation is declared**: at (−1.000, 0.000) it stands **1.000 m dead ahead of the h0.3/h0.9 d2 judged eye on the sight axis**, spanning z 0.000…0.900, i.e. it fills the near window the drop label is read from; the presets are frozen this window so the spec's own escape hatch ("move the camera or the spur") is unavailable, and H16 forbids trading a live gate for a dressing refinement. Residual, carried knowingly: post interval **2.400 m** against 별표2's "1.5 m 안팎" (LINT PE-6 WARN). (5) **03-D — 18 procedural shrub ellipsoids → 18 real shrub USDs** through `sc.place_shrubs`, **one bed for the whole slope band** (K4(b) S-2: six per-bed calls could stand Holly on three clumps and Privet on the other three — two silhouettes on one continuous 25 m slope), role `hedge_evergreen`, `target_h` **0.850 m**. That height is set by the **instrument**, not by G3: the highest bed sits at slope z **−0.686**, so G3's ~1.5 m mass would top at **+0.814 m — 0.514 m ABOVE the h0.3 judged eye**, cutting into the water band that is this scene type's only drop evidence ("no railing × water-surface anchor"); at 0.850 m the same crown tops at **+0.164 m, 0.136 m BELOW** it. The ellipsoids stay as the assets-absent fallback (scene10 precedent). (6) **03-C / K4-F4 — the declared belt is activated**: `far_trees` pass `belt=True`, so `SCENE_SPECIES["Scene03"]` finally resolves as authored — near bank `poplar`, far bank `oak_black` — giving **one silhouette class per bank**. K4-F4 listed 03 among the scenes whose belt was inert until the S-WP passed the flag; this discharges 03. Prim count **1728 → 1893** (`geom_invariance_check --scenes scene03`, isolated git-archive arm) | **No walked-surface z change.** Patches, field lines and the centre line are ≤ 0.020 m decals carrying no z profile (`GT_DELTA = 0.020`, `ground_kit.py:122`); the bollards and the shrubs stand **beside** the walk, never on it, and the stair/slope/spur z ladder is untouched. Two element-class changes GT reads, stated so R-1 can be checked against them: **8 `Patch_*` + 4 `Field/Line_*` + 1 `LeveeLine` band LEAVE the element registry**, and **2 bollard collision boxes move 1.000 m laterally and 0.200 m toward the shoulder**; the shrub swap replaces 18 ellipsoid AABBs with 18 taller USD AABBs 3.0 m and further off the corridor edge | **Rides GT-31's single re-cache** (§0-2). The two items that need R-1 to *prove* their registry move are the bollard relocation and the shrub swap; the three deletions need R-1 to prove an absence | S03 lane · rides GT-31's pilot | `LANDED` — see §4 |

| **GT-33** | 13 | **`walk_cross` / `walk_spur` ride GT-5, as their own row.** `proud = 0.007` → **0.150** on the two walked plates GT-5 does **not** name (`scenes/main/scene13_apartment_parking_entry.py`, `walk_cross` and `walk_spur`), plus the three **turn-down ramps** that make the raise walkable and the one dimension change they force: `WalkRamp_N` (walk_north face `y = +7.20` → carriageway flare edge `y = +4.20`, run **3.00 m**, **4.9 %**), `WalkRamp_S` (`y = −7.40` → `y = −4.20`, run **3.20 m**, **4.6 %**), `WalkRamp_Spur` (`x 11.40 → 13.40`, run **2.00 m**, **7.5 %**), and `walk_spur.x1` **13.4 → 14.4** so that spur turn-down is 2.0 m and not 1.0 m (at 1.0 m it would have been a **15 %** pedestrian approach). The two crossing arms `Walk_CrossN1` / `Walk_CrossS1` stop being flat plates and **become** those ramps; `Walk_CrossN2` / `Walk_CrossS2` stay plates at +0.150. **Why this is a separate row and not a widening of GT-5**: ledger §7 watch item W2 records that GT-5 names two of scene13's four `proud = 0.007` walks and instructs the owner to *"confirm at CB-9 whether leaving two 7 mm walks beside two 150 mm curbed walks is the intended reading"*, and §12-11 forbids this file widening a row. **It is not the intended reading**: raising only the two named plates leaves a **143 mm step** where `walk_cross` (`x −3.2…−1.2`) and `walk_spur` (`x 11.4…13.4`) abut them — a new *undeclared* drop on a walked route, which is precisely the failure mode §0 exists to stop. So the two unnamed walks move in the same commit, under this row `[declared by S4 07-30, append-before-land]` | **+143 mm on two walked plates.** Three new walked **grades** (4.9 % / 4.6 % / 7.5 %) — a grade is not a drop and is labelled `grade` in the scene's R-1 registry. **One step is removed, not created**: at +0.150 a flat crossing arm would have put a **146 mm** step at the carriageway edge (`\|y\| = 4.20`), and the turn-downs delete it. The four `bollard_rows` prims are re-seated from `z = 0.000` onto the crossing ramp surface (`z = +0.011`) so they keep their statutory 0.90 m exposure | **Rides GT-5's single re-cache** (§0-2, one re-cache per scene per batch) — same scene, same commit batch | CB-9 · GATE-1 pilot **13** | `LANDED` — see §4 |
| **GT-34** | 01 | **Flank + backdrop rebuild — G1's kerbed designed lawn replaces the boxed plaza** (W3 S01). This is the row `GT-4`'s retirement explicitly did **not** authorise: *"if it moves any GT quantity it declares a NEW row — it does not inherit this one"* (§3 GT-4, `[amended 07-31]`). Source: `w3_intake_v2_images.md` **§2 scene01** + **§7-6** (*"GT-4 RETIRED … adopt G1's kerbed designed lawn ('no undesigned turf')"*) + the user's 2nd review (*"계단 양옆을 자연 느낌으로 … 환경을 좀 트인 느낌으로"*). **(1) Deleted walked surface**: `TerraceR` (x −18…14, y 8.0…9.5, top **0.000**, 32.0 × 1.5 m) and `TerraceL` (x −20…14, y −10.5…−8.0, top **0.000**, 34.0 × 2.5 m) — the two paved bands that existed only as a walking margin in front of buildings R and L. **(2) New surface**: a designed lawn platform, top **−0.150** (`LawnN` / `LawnS` x −20…26 × y ±8.20…±20.0, `LawnE` x 14.20…26.0 × y ∓8.20), a 0.20 m granite edge band top **−0.150** along y = ±8.00…±8.20 and x = 14.00…14.20, and a **150 mm unit-block kerb** built by `infra_kit.build_curb_line` (`gutter=False`, `z_road=−0.150`, `walk_z=0.000`, `embed=0.55`) over **x −16.0…0.0 on both flanks** — 16.00 m, **13 blocks/side**, curb top **z = 0.000**, i.e. flush with the upper plaza (S06-B 2.'s "flush … +20 mm", measured **+0 mm**). **(3) Removed near masses**: buildings **R** (y 9.5…14, h 14.0) and **L** (y −15…−10.5, h 10.0) deleted outright — 2 collision shells, 68 prims; **C** and **D** replaced by 6 `building_kit` `kind="backdrop"` silhouettes at d_true **53.6–80.0 m**, 18 prims, **0 windows**, every ridge under its own `z_ceil` (printed at assembly). **(4) Dressing, no z change**: planters A / B / D deleted (3 beds, 33 prims, which also clears this scene's `w3_md_reverts_v1.md` §5 census row), `entry_canopy` deleted (R01-2, 5 prims), the 2 camera-solved manholes re-derived from a declared Ø450 storm branch with `infra_kit.derive_manholes`, 73 autumn leaf-litter instances added, bench yaw jitter zeroed. **The flight does not move**: `upper_plaza`, `stairs`, `lower_plaza`, `flank`, `amphi`, `south_apron`, `west_bank` and the `band` runs are byte-unchanged and `plaza_selfcheck` asserts total drop **0.600000** exactly | **Walked surface moves — three distinct effects, stated separately.** ① **New drop, 2 rows**: a continuous linear **0.150 m** kerb face at y = ±8.20 over x −16.0…0.0 (`gt_drop` returned by the builder = 0.150; `gutter=False`, so the default 0.018 m pan cross-fall is **not** chained in and the figure is not 0.168). ② **New UP-STEP, 3 rows — label it an up-step, not a drop** (§8 append-template rule (b)): the lawn edge band stands **+0.450** above the lower plaza (−0.600) along y = ±8.00 for x 0…14.20 and along x = 14.00 for y −8.20…8.20. ③ **Drop REMOVED**: the previous unguarded **0.630 m** cut from the terrace tops (0.000) to the `GroundGrass` plate (−0.630) at y = 9.50 / −10.50, and the same 0.630 m cut at the lower plaza's east end where raw turf ran from x 14 to the old building C at x 24 (01-B, *"paving must run FULLY to edges"* — answered in G1's direction). **The flank maximum drop therefore falls 0.630 → 0.150**, and the scene's largest drop is still the stair's 0.600. Outer bank: 3 walkable grass treads of 0.160 from −0.150 to −0.630, all ≤ 0.200. Buildings, backdrop, planters, canopy, manholes and litter carry **no walked-surface z change** — OCCL only | **Full re-cache** (R-1 + R-2 + R-3). R-1 = the scene's new `plaza_selfcheck` (boot-free, `NEGOBS_SMOKE=1`), which re-derives the registry from `PARAMS` and asserts the level chain; R-2 = a mini data render of scene01 + `check_data_run.py`; R-3 = a 5-cut GATE-1 pilot against the scene's baseline-of-record **`260731_w3_mb24`** and a new stamp | CB-2 (decal vocabulary) · CB-5 (*"01: benches parallel to their planter faces"*) · GATE-1 pilot **01** | `LANDED` — see §4 |
| **GT-35** | 09 | **G9 renovation — terraced beds in dry-stone 자연석, a zigzag timber boardwalk, the far-bank buildings deleted, and the scene-side `patch` row deleted** (W3 S09; `w3_intake_v2_images.md` §2 scene09 (b)/(c)/(e) + §7 ruling 8 → **R09-1 autumn** + §3(ii)). Seven rows, one commit. **(1)** five terraced planting beds — B1/B2/B3 at `y −9.4…−5.8`, B4/B5 at `y 13.2…18.4`, bed tops **0.50 / 1.00 / 1.50**, soil surface 0.12 below each head — each faced in coursed 자연석 blocks (course 0.220, block 0.36–0.62, batter 1:6, block **depth** 0.26 ± 0.018 with the bedding face pinned to the wall plane) + a 0.10 coping course; **374 blocks**. **(2)** 78 shrubs massed **one species per bed** by a one-member `pool=` (Burning_Bush · Juniper · Holly · Yew · Boxwood), chosen from a measured seasonal audit. **(3)** the straight 2.4 × 44.0 m deck slab → a **3-leg / 2-turn** boardwalk in stocked 방부목 sections (plank 25 × 140 across the leg at 0.146 pitch · joist 38 × 140 at 0.45 · beam 90각 · post 120각 at 2.70 · rim 25 × 140): 175 planks, 18 joists, 26 posts. **(4)** the scene-side `surface` row loses `("patch", 5)` and its 3-site list — MB-F1's unreachable half of GT-24, deleted where it can actually land. **(5)** `SCENE_PLANS["scene09"]` synced to the wired call's `surface`/`extras` (ledger §7 **W9** / MB-F2); kit-plan dry run **1141 → 1137 prims (−4)**, scatter **740 → 670 (−70)**, and the real library moves **0** — the drift W9 exists to name. **(6)** the 2 far-side **building** silhouettes (`x0 66`, h 7.0, collider) are **DELETED** and an autumn hillside belt (6 ridges, 12–19 m) takes over horizon closure. **(7)** `build_tree(belt=True)` on the far-bank row activates `SCENE_SPECIES["Scene09"][1] = "oak_black"` (K4-F4). Also: 50 lily pads on the water at \|y\| ≥ 19.6, reed plumes, the flat sign → an information lectern at (−1.9, −9.4), 3 benches re-sited off the new footprints. Prims **501 → 1411**, hash `840928aa` → `e9c9cd8c` `[measured, isolated git-archive arms]` | **No walked-surface z change, and it is asserted rather than claimed.** The 36-step flight, both landings, the embankment step table, the terrace top face (z 0.000), `lawn_proud` (0.030) and the boardwalk top face (**0.060**, the value the old deck shipped) are all **invariant** — the boardwalk change is planform + members, not height. **No drop edge is added or moved**; the drop anchor is still the waterline at z −5.190. What DOES move: the **hazard/collision box list** (added: 5 bed cores, 26 boardwalk posts, 30 plank colliders, 2 lectern legs; **removed**: the 2 far-building boxes) and every added element AABB — the **GT-15 class**, and the removal direction of GT-8. The beds are **retained planting masses, not walked surfaces**: nothing walks on a bed, and none of them is a drop edge (each is a raised container whose face is a wall — the `build_planter` reading). **Occlusion is structurally impossible in a judged cut**: every element this row adds is asserted **outside the ±30° FOV of all nine `sc.grid_views` presets** by a new `fov_selfcheck()` — smallest margin **+3.2°** (a lily raft), nearest bed corner **38.1°** at eye (−10, 0). That gate is the S09-C posts argument turned from a comment into something that can fail a build | **Full re-cache (R-1 + R-2 + R-3).** Declared full, not subset: the row adds collision boxes, so GT-24's "no hazard box moves" exemption does not apply. R-1 = the scene's own self-check suite (`roof_normal` · `albedo` · **`season_audit`** · **`fov_selfcheck`** · **`horizon_selfcheck`**, spec §6.2 S1–S8). R-3 names its baseline per §6-W4 | CB-S09 · GATE-1 pilot **09** (Lane 2 · intake §2.9) | `LANDED` — see §4 |
| **GT-36** | 11 | **S11-H — the footbridge is rebuilt from I-plan to H-plan; both stair towers rotate 90° onto the carriageway axis** (`w3_intake_06_10.md` **§S · S11-H**, user verbatim *"육교가 너무 양쪽으로 뻗어있어. 한국 육교는 H형이야"*; `w3_intake_v2_images.md` §2 scene11 (c)/(f) + **R11-1** asymmetric H, **R11-2** tactile placement). Pre-state `[repro]`: both stair sets ran **inline with the deck axis** — east head landing `x 13.20…15.00`, flight A `x 15.00…22.04` (5.500 → 2.750), mid landing `x 22.04…23.84` (2.750), flight B `x 23.84…30.88` (2.750 → 0.000), all at `y ±0.90`, and the west set its 180° mirror about pivot `(−7.5, 0)` out to `x −30.88`. Post-state: **east = switchback leg** (head landing `x 13.20…15.00 × y ±1.20`, z 5.500 · flight A `x 13.20…15.00`, `y −1.20…−8.24` · mid landing `x 13.20…16.90`, `y −10.04…−8.24`, z 2.750 · flight B `x 15.10…16.90`, `y −8.24…−1.20`, foot z 0.000) and **west = straight leg** (head landing `x −15.00…−13.20 × y ±1.20` · flight A `y 1.20…8.24` · mid landing `y 8.24…10.04` · flight B `y 10.04…17.08`, all at `x −15.00…−13.20`). Riders landing in the same commit, each named because none is a free consequence: **(a)** S06-B curb legibility on **11** (the 06 half is GT-30) — the two 120 m `granite_dark` boxes `x ±10.50…±11.10` are replaced by `infra_kit.build_curb_line` on the kerb faces `x = ±10.50`, `y −60…60`: **55 unit blocks per side** (1.000 m inside the judged window `s 38…84` = `y −22…+24`, 8 m outside it), 6 mm joint gaps, R = 10 mm arris via `LOOK_CLASS["curb"]`, chained L-gutter, material off `granite_dark` onto a light granite role. **(b)** the two `GratingBand_*` carriageway slabs (`x 15.0…31.5` and its mirror, `y ±1.40`, top `z +0.019`) are **deleted** (user rectangle ban; the H-plan removes their pretext). **(c)** the `bridge_deck` `surface` row `("patch", 2)` and its 2 sites are **deleted** (same ban; the deck is concrete, and the one licensed rectangle is a saw-cut asphalt repair on an asphalt road). **(d)** the 4 bollards move from `sc.build_bollard` (h 0.750, a `placement_lint` ERROR against 교통약자법 시행규칙 별표2 제7호 0.80–1.00) to `props_kit.build_bollard_v2` (h **0.850**) and are re-sited `y ±4.0 → ±5.6`. **(e)** deck noise panels deleted, deck balusters re-pitched to the statutory **0.100 m** clear (was 0.32 m). Prim census **2222 → 3772**, geom hash `2f6121eb → 652ea337` `[measured — isolated git-archive arm]` | **Every tread and landing top face moves in plan.** 88 treads + 4 landings relocate; the top-face z of roughly 1,200 m² of ground plane changes sign of occupancy. **Total drop is INVARIANT and is the proof obligation**: 44 × 0.125 = **5.500 m** per tower, deck `z_top` **5.500** and roadway clearance **5.25 m** both unmoved — the crossing height did not change, only the plan. **New drop edge**: the head landings' outer edges `x = ±15.00`, `y ±1.20`, top **5.500** → sidewalk **−0.005** = a **5.505 m** single fall, which **replaces** the old staged stair-head edge at the same `x = 15.00` coordinate (the grid origin is therefore unmoved). **New sub-threshold step**: the curb line carries `gt_drop = 0.150 + 0.018 = **0.168 m**` continuously along both carriageway edges — `build_curb_line` returns `is_gt_hazard=True` (it declares a drop line), and 0.168 < the 0.30 m negative-obstacle threshold, so **label it a step, not a drop**. Rider (b) removes a **30 mm** proud slab from the carriageway (sub-threshold, up-step on deletion). Rider (c) removes 2 element AABBs from the registry (GT-8 `frame_budget` B1/B2/B5 inputs move). Rider (d) raises 4 collision boxes by **+0.100 m** | **Full re-cache** (R-1 + R-2 + R-3) — a plan-level rebuild of both towers | CB-S11 · GATE-1 pilot **11** | `LANDED` — see §4 |
| **GT-41** | 09 | **P09 — 판석 디딤돌 in the lawn, and the terrace stone tone correction the S09 lane measured but deliberately did not take** (`w3_intake_v2_images.md` **§7.2 S09**: *"stepping stones ALLOWED as physical 판석 slabs with 3D relief … stone_tint 0.64→0.524 measured correction authorized (material micro)"*; the pre-state and the arithmetic are `w3_s09_v1.md` §7 **P1** and §2 row 15 **P6**). **Two items, one commit, and only the first of them is geometry.** **(1) 디딤돌 — 10 irregular 판석 slabs in the −Y lawn band**, one route, `x = −14.6` (staggered ±0.10 m on the stride), `y −12.42 … −17.55` at a **0.57 m** pitch, from the lawn's inner edge to **0.45 m short of boardwalk leg L1's north edge** (`y −18.0`) — the route gives the boardwalk the land approach it has never had, which is what a 디딤돌 line is *for*. Each slab is a **UsdGeom.Mesh n-gon prism authored in-scene** (the `build_hip_roof` precedent), **6 or 7 vertices**, per-vertex radius drawn from **0.235–0.315 m** and per-vertex angle jittered, so **no slab has a rectangular outline and no two are alike** — the supervisor's *"irregular outlines preferred"*, met by construction rather than by assertion. Thickness **0.120 m** (the 화강석 판석 100–150 mm band) — real 3D relief, bedded into the lawn, **not a decal**. **(2) tone** — `stone_tint` **(0.64, 0.63, 0.60) → (0.524, 0.515, 0.491)**, linear factor **0.818**, and `stain_tint` · `moss_tint` · `drystone_tint` · `drystone_cap_tint` scaled by the **same** 0.818 so **every authored ratio is preserved unchanged** (waterline stain/stone 0.4672 → 0.4676 · moss/stone 0.3328 → 0.3321 · drystone/stone 0.8594 → 0.8588 · cap/stone 0.9375 → 0.9370). The waterline contrast — this scene's **only drop anchor** — is therefore held by construction, exactly as v7 held it through the 0.90 → 0.64 step. `gk_crack` (0.055 flat) is **not** scaled: it is a fixed near-black, and darkening the paving only widens the crack contrast. The kit's `joint` and `stain_water` bind to `stain` / `moss` and so ride the same factor | **(1) Element AABBs add — GT-8 class — and NO walked-surface z change is claimed.** Slab top face `z = 0.042` = lawn top `lawn_proud 0.030` + **0.012 m proud**, i.e. **12 mm, below `GT_DELTA` 0.020** (`ground_kit.py:124`) — sub-threshold by the ledger's own constant, and the scene's new `stepstone_selfcheck()` gate **asserts it from the shipped coordinates and FAILs the build otherwise**. A 12 mm-proud flush-set slab is also the correct Korean detail for a **mown** lawn (a 30–60 mm proud 디딤돌 belongs in a planting bed, not under a mower). `collider=False`: the lawn box beneath is already `collider=True` with its top 12 mm lower, so **the hazard/collision box list does not change** — declining the collider is what keeps this an AABB-only row instead of 10 new boxes bought for 12 mm. **No drop edge is added or moved**; the drop anchor is still the waterline. The whole footprint (`x −15.015…−14.185`, `y −17.865…−12.105`) lies **behind every judged preset eye** (all three at `x ≤ −2`, looking +X), so `fov_selfcheck` returns `OUT(전 프리셋 후방)` and the near window cannot see it at all. **(2) No geometry whatever** — a tint is an albedo change on faces that already exist. **GT-17's precedent applies verbatim**: *"Albedo change on the terrace face that the grazing cut judges → treat as a render-gate item, not a GT item."* It moves every cut's photometry, which is why it is declared here at all rather than landed silently | **R-3 only** — regression re-stamp against the scene's own baseline-of-record `260731_w3_s09`, new baseline `260731_w3_p09`. **No R-1/R-2 owed and the reason is stated rather than assumed**: no hazard box, no drop edge and no walked surface moves, and the 10 added prims are 12 mm-proud non-colliders 14 m behind the nearest judged eye, so `check_data_run`'s buried / closed_in / offground / nearest-solid tests have no new input. The scene's own boot-free gates (`fov` · `stepstone` · `albedo` · `season` · `horizon` · `roof_normal`) are re-run and printed regardless | CB-P09 · GATE-1 pilot **09** | `LANDED` — see §4 |
| **GT-42** | 11 | **P11 — the 29.5 m footway is narrowed to the §10-1 filed width, and the whole roadside boundary translates 18.00 m inboard with it** (`w3_intake_v2_images.md` **§7.2** *"S11 §10-1 sidewalk narrowing ADOPTED in principle — execute per the report's filed coordinates with an honestly-declared GT class"*; the filed coordinates are `w3_s11_v1.md` **§10-1**). Pre-state `[repro]`: `walk = dict(xw0 −40.00, xw1 −10.50, xe0 10.50, xe1 40.00, z_top −0.005, thick 0.50)` = **29.50 m** of paving per side against G11's measured **4–6 m**; `verge` (2.40 m planting strip, kerb top +0.14 / soil +0.10) at `x ±40.00…±42.40`; 16 street trees on the strip at `x ±41.20`; 8 filler trees on the paving at `x ±21.0 / ±30.0, y ±23.0`; 2 benches at `x ±38.60`; bus shelter `x 19.60…25.60 × y −9.60…−5.60` (`bench_y −8.60`); stop pole `(27.20, −7.60)`. Post-state: **`xe1 40.00 → 22.00` and `xw0 −40.00 → −22.00`** — the two §10-1 numbers, used verbatim and alone — giving **11.50 m** per side; the strip is *derived* from that edge so it follows to `x ±22.00…±24.40` without a coordinate being typed; the street-tree row moves to the new strip centre `x ±41.20 → ±23.20` (y rhythm untouched); the 8 filler trees, which existed only to break up a 29.5 m expanse, become **one inner row of 4 per side at `x ±18.60`, `y ±23.0 / ±30.0`** — **not** the proportional 11.5/29.5 scaling, because that lands at `x 14.6` which is inside the west tower's x-band `−15.00…−13.20` and would put a tree back on the tower axis 5.9 m in front of the west stair foot, the exact defect GT-36's re-siting removed; benches `x ±38.60 → ±20.60` (the 1.40 m offset from the footway edge is preserved, so they stay beside their street-tree anchors at `y ∓19.2`); the bus shelter keeps its **6.00 × 4.00 m box unchanged** and moves to the kerb clear of the tower in y — `x 11.40…17.40 × y −18.00…−14.00`, 0.90 m back from the kerb block's back face and 3.96 m south of the east tower footprint (`y −10.04`), `bench_y −8.60 → −17.00` — because squeezing it between the tower face 16.90 and the new edge 22.00 would have left a 3.80 m stub stranded 7.4 m from the kerb; the stop pole `(27.20, −7.60) → (11.80, −19.60)`, 1.30 m from the kerb. **Nothing else in the cross-section is re-opened**: the distant tree band stays at `x ±44.50…±48.50` and `buildings.E/W` at `x ±50…±64`, so strip → band is **20.10 m of grass**, which is the other half of what §10-1 filed (*"식재대와 수목 띠 사이는 지면(잔디)로 둔다"*); §10-2 (W-beam median guardrail), §10-3 (the 근접 brick street wall) and §10-4 (lane arrows) stay filed-not-executed. **Camera**: the 9 judge preset `eye`/`tgt` triples are byte-identical (they live on the deck at `z ≥ 5.8` and `grid_views` is untouched); the **mise-en-scène** cut `sidewalk_approach` had its eye at `(24.00, 3.20, 0.90)`, which the narrowing puts 2.00 m **outside** the footway, in the planting bed — the first fix slid it 3.00 m forward along its own ground bearing to `(21.40, 1.70, 0.90)` and **the pilot refuted that**, measured on a 48×27 `_solid_at` raycast: the cut's own subject vanished (footway occupancy **10.9 % → 0.0 %**, tower 12.7 → 21.6 %, eye-to-foot 8.78 → 5.78 m). It landed instead at **`(19.60, 8.60, 0.90)`**, on the footway 2.40 m inside its outer edge, approaching the foot from +Y along the walk, with the **target, the eye height and the frame composition unchanged** (sky 37.3 → 37.3 % · tower 12.7 → 12.5 % · footway 10.9 → **17.2 %** · d 8.78 → 10.31 m). Both pilots are on disk (`260731_w3_p11_pilot0` is the refuted arm). Prim census **3788 → 3788** (a pure translation: no prim is added or deleted), geom hash **`dfa8409a → 4e85d0a8`** `[measured]` | **The walked paving polygon changes over 4 320 m² — this is a walked-surface change and is declared as one, not as an A.** Per side the footway shrinks 29.50 → 11.50 m over its full 120 m run = **−2 160 m²**, resolved exactly: `x 22.00…24.40` (288 m²/side) goes paving → planting bed, `x 24.40…40.00` (1 872 m²/side) goes paving `z −0.005` → site grass `z −0.16` (**−0.155 m**), and the old bed `x 40.00…42.40` (288 m²/side) goes bed → grass. The transverse end faces at `y ±60` shorten 29.50 → 11.50 m. **No drop edge is created and none is deleted.** The only ≥ 0.30 m line in the section is the planting strip's **outer** kerb face (`+0.14 → −0.16 = **0.300 m**`, at the threshold, therefore a drop and not a step) and it **translates 18.00 m inboard, `x ±42.40 → ±24.40`** — declared because it now stands 2.40 m outboard of the footway instead of 20.40 m and is inside the `overview` frame. What a walker on the footway meets at the new edge is an **up-kerb (+0.145)**, not a fall. **Every footbridge hazard is invariant, and that is the proof obligation**: total drop 44 × 0.125 = **5.500 m** per tower, deck `z_top` **5.500**, roadway clearance **5.25 m**, head-landing edge fall **5.505 m**, east mid-landing fall **2.755 m**, `build_curb_line` `gt_drop` **0.168 m** (sub-threshold step) — all re-derived by R-1 *after* the edit; the scene's whole SMOKE output is **byte-identical to the pre-state apart from the new P11 block**. **Element AABBs move** (GT-8 `frame_budget` B1/B2/B5 inputs): 24 trees, 2 benches, the shelter + its 6 sub-prims, the stop pole + sign — 33 registry boxes in all | **Full re-cache (R-1 + R-2 + R-3)** — a walked-surface extent change on both footways | CB-P11 · GATE-1 pilot **11** | `LANDED` — see §4 |
---
| **GT-43** | 12 | **The river-side guard becomes 착색방부목 round post-and-rail — G3's own guard product — and its members move to the repo-verified 방부원형목재 stock sections** (W3 L12; `w3_intake_v2_images.md` §4 Lane-3 row **3.1** *"12 · G3 + G9"*, §2 scene12 (b)). **Pre-state** `[measured, HEAD f5ab284]`: `rail=dict(y=1.15, post_r=0.032, post_h=1.05, spacing=1.5, top_z=1.05, top_r=0.035, mid_z=0.55, mid_r=0.020, gap_x0=−6.0, gap_x1=−3.6, stub_xs=(−5.4,−4.2), stub_h=0.10)`, every member drawn in `M["rail"]` = a **painted-steel** constant-colour PBR (`rail_color (0.30,0.31,0.33) · metallic 0.25 · rough 0.55`; prim `Looks/Rail`, which the look layer classes **metal**) — i.e. **Ø64 posts · Ø70 top rail · Ø40 mid rail**, three steel-pipe diameters wearing a river-deck's job. **Post-state**: **Ø120 posts · Ø80 top rail · Ø80 mid rail** — the only two round preservative-timber sections this repo has verified, `Docs/surveys/s3_research_numbers_v1.md` **§A5** (KFS-TRAIL 그림 3-20, p.72, source grade **A**: 방부원형목재 **Ø120** riser log · **Ø80** stake) — bound to a new `M["guard"]`, the `wood_dark` map × a tint **derived** (not chosen) at the 착색방부목 target read off **G3** this session. Prim renamed `Looks/Rail` → `Looks/DeckGuardWood` so the look layer classes it **wood** and stops applying the metal detail-grain to timber. **The topology is unchanged and that is the point**: posts + top rail + mid rail, **no balusters · no kick plate · the 2.4 m destroyed span · 2 sheared stubs · 1 tape** — which is exactly what G3's levee-edge guard shows at full resolution (round stained log posts, two round rails, no infill of any kind). **scene10's square sawn vocabulary is declared NOT to transfer, with the reason**: `w3_s10_rebuild_v1.md` §2 is a park-deck **방부각재** product (90×90 newel · 38×140 top rail · 38×38 baluster @ 0.150), and G3's river-edge product is a round-log post-and-rail. **Balusters are refused outright** — the h0.3 sight line running out under the mid rail *is* this scene's negative-obstacle premise (docstring §Hazard), so infilling the bay would silently move the research variable (the `w3_intake_v2_images.md` §7.2 S03 fence-decline and S17-F4 precedent). Post pitch stays **1.5 m** against §A5's 1.2 m 통나무펜스 정간: the 2.4 m destroyed span is **two bays of the 1.5 m grid** and the stubs at −5.4/−4.2 are set on it, so re-pitching would move the hazard itself — divergence declared, not absorbed | **No walked surface moves · no drop edge moves · no hazard-registry entry moves.** What does move: **14 collision boxes** (12 posts + 2 stubs, `col=True`) change radius **0.032 → 0.060**, and the guard's element AABBs grow with them. The graze budget is **re-derived rather than asserted**: the open band between the deck top face (z = 0) and the **mid-rail underside** goes **0.530 → 0.510 m** (**−20 mm, −3.8 %**) and the top-rail underside **1.015 → 1.010 m**, so the sight line this scene exists to carry survives the section change with its cost stated in millimetres. **Prim count unchanged** — 12 posts + 4 rail segments + 2 stubs, before and after | **R-1** (the scene's own smoke re-derives and prints the hazard/drop registry **and** the collider radii, so the invariance is a printed result, not a claim) **+ R-3** (OCCL / photometry re-stamp). **Carries GT-44** — one re-cache per scene per batch, §0-2 | CB-L12 · GATE-1 pilot **12** + OCCL re-stamp | `OPEN` |
| **GT-44** | 12 | **The deck timber goes to the measured 2–5 year 방부목 patina band — material only, 0 prims** (W3 L12; the `w3_s10_rebuild_v1.md` §2.2 method, re-derived here rather than copied). **Pre-state** `[measured, HEAD f5ab284]`: `M["deckwood"]` binds the `wood_dark` map **raw, with no tint at all**. The map measures mean linear **(0.0824, 0.0584, 0.0442)**, Y **0.0625**, **L\* 30.03** at full resolution — an independent reproduction of S10's figure — and the scene's own `albedo_selfcheck` prints **알베도 0.081** for it. That is **a third of the band floor, on a walked deck**, and it is the single largest fidelity gap in the file. **Post-state**: target **L\* 55.0 · a\* +1.0 · b\* +6.0** → linear **(0.2537, 0.2258, 0.1925)**, **albedo Y 0.2293**, so **all four clauses of the band hold at once**. **AMENDED before landing, and the deviation is declared rather than discovered**: the row was declared at **L\* 56.0** (albedo 0.2391) and that value was built and rendered first, as round `260731_w3_l12`. Against the reference it read **a shade bleached** — nearer driftwood grey than a 2–5 year patina — and its near-ground band measured **mean 185** where **scene10's landed deck, the same product in the same library under the same 49.79° L0 sun, measures 181**. Corrected **once** by the reference, which is the procedure `w3_s10_rebuild_v1.md` §2.2 records for exactly this situation; 55.0 is scene10's landed value, so the two decks are now numerically level. The reference moved the value **within** the standard; it did not overrule it. The correction is **not** claimed to clear the `near_ground_stats` `mean>170` / `wht%≥2` gates — **no in-band target can**: at the band's own albedo floor (0.220) the band still measures 177–178, and scene10's landed baseline trips the same two gates for the same reason (mean 181 · wht% 7.6). That is **L12-F3**, a threshold-calibration row against a pre-patina library, not a scene12 defect. The band is `L* 53–60 · a* 0…+2 · b* +4…+10 · albedo 0.22–0.28`, and because **L\* 53 ↔ Y 0.2105 is below the albedo clause**, its clauses do not agree at the floor: the effective intersection is **L\* 54.1–59.9**. 56.0 is the lower half of that intersection, which is where an open, unshaded riverside deck under the library's 49.79° L0 sun belongs. **`tint = target / source` = (3.207, 4.030, 4.553)**; clipped texels at that gain **0.0122 %**, so **the shipped map carries the target and no procurement is opened** (S10's G5 / §8.R OQ-8 test — *"only if that visibly fails"* — is not met, and G5 stays unblocked and unspent). The reference read is what set the *half* and is recorded: **G9's boardwalk in diffuse light measures L\* 58.05 · a\* +1.41 · b\* +2.34** `[ref, this session]` — inside the band on L\*, but it is a **rendered pixel under sky illumination and therefore an upper bound on albedo, not an albedo**, which is why the target sits below it instead of at it. Applied to the deck slab, the fascia, the 2 longitudinal beams, the 7 cross beams, the 12 piles and the 7 stair courses — **one weathering state for one product**. A separate darker soffit albedo is **refused with the arithmetic**: the effective band is only **5.8 L\*** wide, so a deck/soffit split inside it would be invisible, and the top-face-vs-vertical-face difference G9 and G10 both show is carried by **shading**, which the renderer already does | **No geometry of any kind** — 0 prims, 0 element AABBs, no collider, no walked surface, no drop edge. Photometry moves hard, and that is the entire row: `albedo_selfcheck` 알베도 **0.081 → 0.260**, 수평 예상 렌더 **105.8 → 177.4** (CAP 222, so the §4 large-area gate still passes with margin) | *(rides **GT-43**'s R-1 + R-3, §0-2)* — this row owes **R-3** alone and GT-43's re-cache strictly contains it | CB-L12 · GATE-1 pilot **12** + OCCL re-stamp | `OPEN` |
| **GT-45** | 20 | **L20 — the closed horizon is opened to a BS-4 far silhouette, the C6 bollard template lands, and the mesa furniture is re-sited off the judged eyes** (W3 Lane-3 row **3.3**; `w3_intake_v2_images.md` §4 *"20 · G1 + G8 · granite plaza stair; only the 30° rotation differs"* + §2 scene20 (c)/(e) + **R20-1**). Four changes, one commit. **(1) BS-4** — the three `sc.build_building` masses `C(x 26…32, h 13.0)` · `D(y 16…22, h 11.0)` · `E(x −40…−32, h 16.0)`, **3 shell colliders + a 128-prim window/attachment layer**, are replaced by ~~5~~ **4 `bk.plan_building(kind="backdrop")` silhouettes** at `d_true` ~~44.00 / 46.00 / 52.00 / 58.08 / 62.03~~ **40.00 / 40.00 / 46.17 / 48.09 m**, ~~15~~ **12** prims, 0 windows, ~~5~~ **4** shell colliders `[amended by the row's owner before the corrected geometry landed, on the first pilot render]`. **Why**: the first solve was sky-correct and **ground-wrong** — E1/E2/W1 stood at 56–76 m, past the east edge of the only ground this scene has (`Valley`, a 100 m box centred at x=+6, i.e. x −44…+56 · y −50…+50), and N1/S1 overhung it in y; the pilot cut shows the plane's own horizon seam running behind them. The blocks are re-solved **inside** the plane with ≥ 2 m margin and the containment is now a gate, not an assumption (`plaza_selfcheck` 지면 포함, 이탈 0건). **W1 is deleted** rather than re-sited: the preset axis is +X (spec §D) and all four mise-en-scène cuts look east, so a −X mass is behind every judged eye. **(1b) mid-ground belt, added in the same amendment**: **20** `elm` trees (`species=` passed explicitly; `SCENE_SPECIES["Scene20"]` belt slot is `None` and is **not** invented) on the valley grass — two east rows at x 24.0 / 32.6 and one row on each flank at y ±18.0, pitch **8.0 m** (`sc.TREE_PITCH_M`), row separation **8.6 m** so `placement_lint` LINT-2 reads two rows and not one zig-zag (scene01's measured value). Trunks are **not** colliders and the belt sits on the valley top face, which does not move; it is recorded here because it lands in the same commit as the backdrop it completes, not because it moves a GT quantity. Acceptance is `ridge = base_z + h + bk.roof_allow(p) < z_ceil` at each block's own `d_true`, printed per block and asserted: **5/5 sky above the roofline** (pre-state: the nearest mass had ridge **13.75 m** against a `h0.3_d2` ceiling of **4.23 m**). **(2) C6** — `build_bollard_std` → `props_kit.build_bollard_v2` on **8** instances (4 at the mesa ramp head `x = −13.6`, 4 in the lower-plaza corridor `lx = 17.0`): the **body collider** goes `r 0.075 → 0.055` · `h 0.90 → 0.85` (both still inside 편의증진법 별표2's 0.80–1.00 m / Ø0.10–0.20 m), plus dome / plate / anchor-cover / band prims which are **not** colliders. **(3) planter re-site** — `(−10.0, ±5.5)` · `(−6.5, 6.2)` → `(−12.3, ±5.6)` · `(−7.0, 5.6)`: **12 kerb boxes** (`collider=True`) move in plan, bed top face z unchanged. Driver is the `w3_md_reverts_v1.md` §5 census row — `oblique_overview` at **0.450 m** from a bed AABB with a live `Elm_Sapling` — plus **4 hard interpenetrations measured pre-edit** (`Planter_2 × Bench_0` **1.450 × 0.400 m**, `Planter_2 × Streetlight_0`, `Planter_1 × Streetlight_1`, `Bench_0 × Streetlight_0`). **(4) bench row + lamp line re-sited** with them (bench seats are colliders, ×3 on the mesa; lamp poles are colliders, ×3). Riders that move **no** GT quantity and are recorded, not declared: the G-4 manhole derivation (2 sites → 2 derived chambers, decal class), the F1 dead `patch` site list + its ghost `patch=M["upper"]` binding (**0 prims emitted since GT-24**), the autumn litter (**69** scatter instances), the `planter_accent` species pin and the turf tint. | **No walked surface moves and no drop edge moves.** `UpperPlaza` / `UpperWedge` / `Stairs` / `LowerPlaza` / `Valley` / `AccessRamp` top faces are byte-unchanged; the drop boundary is still the 30° diagonal `x = −0.5774·y` carrying **2.10 m** over 14 × 0.150 m risers (R20-1: `rot.deg = 30.0` is a scene-wide skew, **frozen**). What moves is the **collision-box list** — 8 bollard bodies (dimension), 12 planter kerbs (plan), 3 near shells → 5 far shells — and the **OCCL baseline**, which moves a lot: the horizon opens from a wall running off the top of frame to sky above every roofline. | **R-3** (re-stamp the OCCL/GRAZE baseline in the next `regr_*.json`) + **R-1** (`plaza_selfcheck` re-derives and **prints** the hazard/collision registry from the changed geometry, and fails the scene loud on any of its ~~four~~ **six** gates — prop interpenetration, judged-eye↔bed, G-4 reject-only occupancy, backdrop ridge < z_ceil, ground-plane containment and the season audit; the last two were added by the amendment above). **R-2 not owed** — class **A**, no walked-surface z change. | GATE-1 pilot **20** vs baseline-of-record `260730_w2d_fix` | `LANDED` — see §4 |
| **GT-46** | 03 | **P03 — the levee-crest walk is PAVED in G3's 점토블록; the 07-29 "03 stays natural" ruling is superseded on this clause only** (`w3_intake_v2_images.md` **§7.2 S03**: *"S03 crest promenade — PAVE, image doctrine wins. G3's 점토블록 promenade supersedes the 07-29 'natural' ruling (that ruling predates the target-image doctrine). Executed as a follow-up lane with its own FULL GT row"*). The conflict was raised, **not** resolved unilaterally, by the S03 lane itself — `w3_s03_v1.md` §7-9 filed it as *"the single largest archetype divergence from the target image"* and refused to pave without a ruling. This row is that ruling executed. **Pre-state** `[repro, HEAD 4af5382]`: `levee_road=dict(x0=-4.000, x1=-1.000, proud=0.0015, embed=0.050)` — a **3.000 m gravel maintenance band** on the crest, full Y through the meander, prim path `/World/Scene03/LeveeRoad` (19 segs), material `gravel`; `levee_spur=dict(x0=-1.000, x1=0.000, y0=-1.200, y1=1.200)` — a **gravel** stair-head apron; every other crest surface mown grass. **Post-state**: `crest_walk=dict(x0=-5.000, x1=-1.000, proud=0.0015, embed=0.050)` — a **4.000 m 점토블록 promenade** (`/World/Scene03/CrestWalk`, 2 sub-bands × 19 segs = 38), plus `crest_band=dict(x0=-5.400, x1=-5.000)` — a **0.400 m light-grey block edge band** = **2 courses of the 200 mm module** (`/World/Scene03/CrestBand`, 19), and the spur takes the same 점토블록. Hard walked surface **3.000 → 4.400 m** wide; **1.400 m × 95.0 m of mown turf becomes walkable paving**. The river-side paving edge stays at **x = −1.000**, unchanged, so the 1.000 m grass shoulder between the paving and the unguarded drop edge survives and no new drop-parallel line enters the near window. **Materials**: `paving_interlock` (ambientCG PavingStones015) at `scale_m` **1.200** = the measured **200 mm** block long side (`scene_common.py:158-163`), tint **(1.000, 0.717, 0.471)** → linear luminance albedo **0.211**; the band takes scene17's own measured `paving_tint` **(0.840, 0.830, 0.810)** → **0.231**, so the sibling levee scene and this one share one grey block value. Both under `ALBEDO_CAP` 0.30 (`ground_kit.py:128`). **This is also the fix for the tone item `w3_s03_v1.md` §7-3 handed on**, and the mechanism is measured at the texture, not asserted: `gravel_diff` reads sRGB luminance **p99 215.4 · >204 3.56 %**, `paving_interlock_diff` reads **p99 173.6 · > 204 0.09 %** at an almost identical mean albedo (0.2855 vs 0.2777) — the near-white field was the gravel scan's **highlight tail**, and unit paving has none. **What this row does NOT do**: no bike road and no centre line — the 07-29 ruling's cycle-track clause (*"the cycle track holds only for the scene17 levee"*) is untouched, only its *natural surface* clause is superseded; and the G3 river-edge **timber post-and-rail fence stays DECLINED** per §7.2 (*"the scene's no-railing × water-anchor research identity outranks one image element"*), divergence documented in `w3_p03_v1.md` | **The drop edge at `x = 0.000` does not move by any amount.** `crest_walk.proud` is deliberately held at **0.0015**, not raised to scene17's 0.006, and the reason is the stair and is arithmetic: `_stair_steps` starts the flight at `z_top = 0.000`, so the **first riser measured from the walked surface is `0.160 + proud`**. At 0.0015 it is **0.1615 m** against 19 uniform 0.160 risers (**+0.94 %**, inside construction tolerance); at 0.006 it would be **0.1660 m** (**+3.75 %**), and 편의증진법 별표1 requires uniform 챌면. The drop from the crest walk to the beach therefore stays **3.2015 m**. What DOES move: **1.400 m × 95.0 m of turf becomes walked surface at z 0.000 → +0.0015 (+1.5 mm)**, and **4.400 m × 95.0 m of walked surface changes material/semantic class** from gravel + turf to unit paving, with the collider set following it — that is a data channel change, which is why this row takes a real **R-2** rather than the R-1+R-3 GT-31 could justify. Element/occluder AABBs: `LeveeRoad` (19) **leaves**, `CrestWalk` (38) + `CrestBand` (19) **enter** (net **+38**), and the pergola moves 0.800 m landward (GT-47) | **Full re-cache (R-1 + R-2 + R-3)** — carries GT-47 (§0-2, one re-cache per scene per batch) | P03 lane · full-preset GPU pilot vs baseline-of-record **`260731_w3_s03`** (the S03 round) | `LANDED` — see §4 |
| **GT-47** | 03 | **The consequences of paving — ground plan, dressing and ablation-arm integrity. Rides GT-46; no walked surface among them.** **(1) `pave.module` `(None, None)` → `(0.200, 0.100)`** — a truthful declaration, because the crest *is* laid in blocks now; `unit_cell` was always **0.200** in the kit ledger (`ground_kit.py:319`) and `_assert_unit_cell`'s U1 check passes. Measured no-op in prims: the only consumers of `pave.module` are `build_patch_field` and `build_relaid_units`, and this scene builds **neither**. **`pave.joint` stays `None`, declined with coordinates, not with a preference**: `joint="interlock"` + the profile's `step_x = 3.0` composes `build_joint_grid` as **x = const grooves spanning the whole y range — parallel to the drop edge at x = 0** — measured sites **x = −12.000 / −9.000 / −6.000 / −3.000** on the old region and **x = −3.000** on the paved band, the last of which sits on the **d10 GT-E2 E-band boundary** [0.7d, 2.2d] = x −3.000…+12.000. Interlocking block has no 3 m 시공줄눈 — its joints are the **3.5 mm sand joints between every unit** (`joint_interlock_w`, `ground_kit.py:250`), which the texture delivers at the module scale set above. **(2) ground-plan region `x0` −12.000 → −5.400** (the paved band's outer edge). CPU A/B on `plan_ground`, both arms: **prims 17 → 17**, elements 17 → 17 — but with the old region **4 of the 8 `stain` decals landed at x ≤ −6.254**, i.e. on mown grass, floating 1.5 mm above turf; with the new region **every stain lands on paving**. `surface` (`stain` dirt/water + `weed` 8), `extras` (`wear_lane` 0.900) and the wear centreline (−3.500, ±10.000) are **unchanged**, so the `SCENE_PLANS` fixture's mirrored fields do not drift (§12-1); `pave` and `region` are **not** mirrored by that fixture and are already named in §12-1's residual list — this row widens that residual and routes it, it does not repair it (kits are frozen this window). **(3) edge break `x` −4.000 → −5.400**, the new hard/soft seam; `break_y` **2.400 unchanged** — |dx(2.400)| = **0.0946 m** < the 0.100 m half-width of the transition band, re-measured this round. **(4) Ablation-arm integrity — a live defect the paving exposed, not a cosmetic.** `cue_material_break = False` bound the stair to `M["gravel"]` *because the crest was gravel*; against a paved crest that arm would render **paving vs gravel = a material break in the arm whose whole purpose is to have none**. Re-bound to the crest paving. The same defect in the `hazard_stairs = False` control: `build_flat_fill` laid **gravel** from x = 0 to x = 18 so that the twin showed **no line at x = 0** where the drop had been; re-bound so that invariant survives the paving. **(5) `wear` material re-bound** `dirt_park` → the paving at **×0.85** (`wear_albedo_gain`, `ground_kit.py:282`) — a dirt-textured wear lane down the middle of a block promenade reads as a mud streak, not as polished blocks. **(6) pergola `x0/x1` −8.000/−5.000 → −8.800/−5.800**: its river post line stood at **x = −5.000, inside the new 0.400 m edge band**, i.e. a prop standing in the walking surface (PROP-EDGE class); moved landward so the posts stand **0.400 m clear** of the paving. `benches[0]` (−6.500, 4.400) stays inside the pergola footprint, checked | **No walked surface, no drop edge, no hazard/collision box moves in this row.** The ground-plan elements are ≤ 0.020 m decals (`GT_DELTA`, `ground_kit.py:122`) and their count is unchanged at 17; the stair material re-binding changes **0 prims** (it is a material, and it fires only in the ablation arm); the pergola is dressing 5.8 m landward of the drop and its 4 post AABBs move 0.800 m in −X | *(rides GT-46's single re-cache — §0-2)*. The two items that need R-1 to **prove** a move rather than an absence are the pergola AABBs and the ground-plan region | P03 lane · rides GT-46's pilot | `LANDED` — see §4 |
| **GT-49** | 15 | **L15 — the alley's material truth, plus two coordinates: the G-4 manhole and the B2d containers** (W3 Lane-3 row **3.8**, `w3_intake_v2_images.md` §4 *"15 · G18 (weak) + G2 · weakest mapping in the set — route last, judge conservatively"* + §2 scene15 (e) *"K4(b) `place_shrubs` for the pots · GD light-touch · K5 none"* + **R15-1**). **Only two items in this row are geometry; they are listed first and the rest is albedo.** **(1) G-4 manhole — the near-window pilot device is retired at its own origin.** Pre-state `[repro, HEAD f5ab284]` `manhole_d5=(-2.40, -0.15)`, and the file states in its own comment that the value was solved from the camera (*"at the d5 window x=−4.0 it is 280 px = 14.6 %"* … *"x=−2.40 gives X=2.60 m · 414 px = 21.6 % at d5"*) — exactly the defect `w3_intake_01_05.md` §G-4 measured library-wide (19/26 sites inside the d2/d5 band, 11/26 at x = −2.40 or −4.00). Post-state `manhole_site=(-2.60, 0.00)`, **derived from the sewer**: KDS 61 40 00 requires a chamber at 방향·경사·관경 변화 or a **합류**, and gives a Ø≤600 straight run **75 m** between chambers, so a 12 m alley owes **zero** interval manholes and exactly one junction chamber — the station where House[0] (cx −2.6, north) and House[1] (cx −2.6, south) put their 오수 branches into the main, on the main's own alignment (the alley centreline y = 0.00, not 0.15 m off it). The 우수 U 측구 keeps its separate line at y = −0.75. Camera arithmetic is retained as a **check, not a driver**, and is asserted by the new gate: d2 **behind the eye** · d5 X = 2.40 m → **23.4 %** of frame · d10 7.6 % `[computed]`. Clearances re-measured: U gutter **+301 mm** · wall grime band **+426 mm** · patch #1 **+1433 mm** · 시공줄눈 JX at x −3.000 **+76 mm**. **(2) B2d containers + K4(b) planting.** Pre-state: 5 × (cylinder r 0.20 × h 0.34, `collider=True`) + 5 × (sphere 0.19 × 0.19 × 0.152, no collider). **This pre-state carried a live interpenetration the file's own comment denied** — *"pot r 0.20 -> never reaches the facade at 0.58"*, but 0.40 + 0.20 = **0.600**, so every |y| = 0.40 container was **20 mm inside a house facade** and every leaf sphere 10 mm inside it (**L15-F1**, found this round). Post-state: three Korean container types — 스티로폼 상자 **0.50 × 0.34 × 0.28** · 고무 대야 **Ø0.350 × 0.20** · 화분 **Ø0.310 × 0.28**, all `collider=True` — plus one real shrub USD per container through `sc.place_shrubs(species=…)`: `edge_weed` (Grass_Short_C) target_h **0.125** in the boxes, `border_narrow` (Cedar_Shrub) target_h **0.45** in 대야·화분. **Sites (x, z, grp) and the count are unchanged**, so no object enters a judged frame that was not already there. Every clearance is now positive and is a gate, not a claim: containers **+5 / +10 / +25 mm**, worst-case crowns (native width × scale × the +8 % draw) **+16 / +100 / +120 mm**. The survey's Ø0.45 고무 대야 is **refused with the arithmetic** — a site at \|y\| = 0.40 facing a facade at 0.58 leaves 0.180 m — and the stocked Ø0.35 is used instead. **(3) Material truth — 0 prims, and it is the bulk of the round.** (a) `Looks/Roof_*` resolved to `LOOK_ROLE["Roof"] = "wood"` (a scene07 temple fix) and `_promote_const_to_texture` bound **`wood_dark_diff.jpg` at base_color (6.842, 5.424, 5.073)** on tint 0 while **refusing** promotion on tint 1 `[measured]` — a 달동네 옥상 shipped as a dark plank deck at a >5× gain. Path → `Looks/Slab_*` (class **concrete**), tints → **녹색 우레탄 방수 (0.115, 0.185, 0.125)** and weathered cement **(0.255, 0.250, 0.240)**. (b) `M["alley"]` binds `concrete_floor` **directly** and so never passed through promotion's mean re-normalisation, shipping the raw texture mean **(0.14645, 0.11021, 0.07334)**, R/B **2.00** — the tan floor in every h0.3 crop, beside a stair bound to the *same* texture through promotion at the authored (0.20, 0.20, 0.19). Corrected by a **luminance-preserving** tint (0.7898, 1.0496, 1.4983): Rec.709 Y **0.115250 → 0.115253** and the hue lands on the scene's own concrete ratio 1 : 1 : 0.95. (c) the 2 repair patches take the same texture at **+20 % Y** so R15-1's "the patches are the realism here" is legible; the saw-cut seam stays dark on `M["stair"]`. (d) the ground stains stop sharing `M["skirt"]` with the **wall dado** — a splash dado and a dirt lobe are different materials — and the dado itself moves off near-black-and-cool (0.10, 0.10, 0.12) onto the Korean grey-green oil paint (0.098, 0.112, 0.100). (e) 알루미늄 새시 (0.72, 0.70, 0.66) metallic 0 → (0.50, 0.50, 0.505) metallic 0.55; 실외기 (0.045, 0.05, 0.045) → (0.360, 0.355, 0.345). (f) **era, `era_consistency_survey_v1.md` §4.4 mismatch 1 executed**: the `cue_railing=True` pipe was *"described as the compliant version"* and built as weathered painted steel; it is now **STS304 retrofit** (metallic 0.9, roughness 0.35 — §5.1's 2000s–2010s row) on a path that actually resolves to metal (`Looks/Pipe` was class **misc**; `Looks/Handrail` is **metal** `[measured]`). **What this row does NOT do, deliberately**: no prop is added. v5.1 stripped this scene on a user verdict and E4's own cap (*"3 per segment, each justified by 'the scene cannot be read without it'"*) points the same way; the E4 census is 1 실외기 per segment and stays there. U-6 is applied at R15-1's lightest hand — **2 patches and 8 weeds are kept**, and the only rectangles in the scene remain the 시공줄눈 and those two saw-cut repairs. Prims **433 → 438**, geom hash `3a0f63a2 → 2e4569a7` `[measured, `geom_invariance_check --scenes scene15`]` | **No walked surface moves, no drop edge is added or moved, and the concealed drop is invariant.** `flight1` 12 × 0.170 + `flight2` 13 × 0.170 = **4.250 m** exactly, top faces 0.000 / −2.040 / −2.040 / −4.250 — all four asserted by the new gate rather than asserted in prose. What DOES move: **5 collision boxes change shape** (Ø0.40 × 0.34 cylinders → one 0.50 × 0.34 × 0.28 box / Ø0.35 × 0.20 / Ø0.31 × 0.28 per site) and **shrink out of a 20 mm facade interpenetration they should never have had**; the 5 foliage prims are replaced by 5 **non-collider** shrub instances (the GT-41 reading — foliage is not something a robot collides with, and buying 5 boxes for a crown would move the hazard list for nothing); and **one element AABB moves 0.20 m in x / 0.15 m in y** (the manhole, a flush ±10 mm kit element whose top face z is unchanged) — the **GT-8 class**. Material items (3a)–(3f) are albedo on faces that already exist: **0 prims, 0 AABBs**. They move photometry, which is why they are declared here rather than landed silently — except the alley tint, which is **photometrically null by construction** (Y held to 3e-6) | **R-1 + R-3.** **R-1** is discharged by a **new boot-free, GPU-free gate**, `alley_selfcheck()` (`NEGOBS_SELFCHECK=1`, the scene03 precedent): scene15 shipped with **no self-check of any kind**, which is why its earlier rows could never show a registry. It re-derives and prints the drop registry from `PARAMS` and asserts the drop invariance, every container/crown clearance against a **derived** facade plane, the four manhole clearances + the frame arithmetic, the summer species pin, the tint's luminance identity and the E4 cap — **17 gates, 17 PASS**. **R-3** re-stamps OCCL/GRAZE against the scene's baseline of record. **R-2 is not owed and the reason is stated rather than assumed**: class **A** — no walked-surface z change, no drop edge, no new collider *class* (5 props stay 5 props in the same 5 places, 0.20–0.28 m tall, beside the stair and never on it), so `check_data_run`'s buried / closed_in / offground / nearest-solid tests take no new input. The GT-45 precedent (*"R-2 not owed — class A, no walked-surface z change"*) is the one followed | L15 lane · full-preset GPU pilot vs baseline-of-record **`260730_w2d_fix`** (scene15 has no post-CB-2 round; the pilot is run as a **pre/post pair at the same HEAD channel** so the 60+ library commits between that baseline and now are not charged to this lane) | `LANDED` — see §4 |
| **GT-50** | 19 | **scene19 turns K4(d) on — the fan winder's treads become true annular sectors.** GT-6 (`RELEASED`, builder landed default-OFF at `5ceb76a`) says 05 · 06 · 19 flip the lever "inside their own pilots where the split proof is judged"; scene06's pilot is GT-29 and **this row is scene19's**. Content: `build_arc_steps(mesh=True, arc_seg=6)` on all four arc families — `Step_i` (12 × `seg` 3 = 36 prims, the walked one), `Parapet_i` (7), `Rail_i` (7, `cue_railing`), `Nosing_i` (12, `cue_nosing`, default OFF but flipped so the ablation arm is not left on the retired convention — GT-40's precedent). **Pre-state** `[repro, HEAD `ba7fded`]`: `winder=dict(r_in=1.2, r_out=4.0, n=12, sector_deg=7.5, seg=3, kite_n=3, riser=0.15, base_z=−2.3)`; `scene19:265` already carried an independent note on the 1.03 chord factor. **The defect, measured**: the box convention lays a Cube of chord `2·r_out·sin(Δθ/2)·1.03` per sub-segment, so at Δθ = 2.5° the half-chord is **89.877 mm** and the angular overshoot past the design ray is `asin(89.877/r) − 1.25°` = **3.0453° at r = 1.2 → 0.0375° at r = 4.0** (arc **63.78 mm → 2.62 mm**). Box corner radii **1.203361 / 4.001010** against the design 1.200 / 4.000. Prims **284 → 292**, geom hash **`4ac6372a` → `3f67f1d5`** `[measured, isolated `git archive` arms, assets symlinked]` — the +8 is GT-51's, not this row's; this row is Cube→Mesh at 1:1 on 62 prims | **One stratum, and it is above `GT_DELTA`, so it is declared as a real movement rather than absorbed.** Split proof (`_arc_split_proof`, in the scene's own smoke run, GPU 0): 57 radii × 3601 azimuths = **205,257 samples** over r 1.10…4.10, az −4…94°. **17,019 differ (8.29 %)**, every one of them **−183.333 mm exactly = one riser**. **new-void 0 · new-solid 0.** (i) **No tread's own z moves** — the ladder (−0.150 ×3 kite, then 9 × 183.333 mm to −1.800) is bit-identical and the **total drop 1.800 m is invariant**; what moves is *which azimuth belongs to which tread*, which is the defect `mesh=` exists to fix. (ii) Attribution: **9 hand-over boundaries, 3\| (22.5°) … 11\| (82.5°)**, 1,869–1,921 samples each. Boundaries **1\| and 2\| contribute 0** — they are the kite landing, where the riser is 0.000 m: the negative control proving the probe measures the hand-over and nothing else. (iii) **The a0 = 0° and a1 = 90° ends contribute 0.** GT-29 had to declare this term for scene06 (its landing `a0` ray overshot ≤ 4.25° into open air, a phantom slab 3.07 m up); here the box overshoot falls **inside `Wall_south` (y −1…0) and `Wall_west` (x −1…0), both `z_top` 3.5**, so it can never win a top face — proved by the probe, not assumed. (iv) **No drop edge is created or destroyed**: the outer arc retracts by **1.010 mm** (box corner bulge → true ray) and the inner radius is unchanged at the mid-ray; both an order below `GT_DELTA = 0.020`. The 1.8 m fall to the corner slab and the hazard arc are untouched. (v) Parapet / Rail / Nosing are **guards and cues above the walking plane** — R-3, not GT | **R-1 + R-3.** **R-2 is owed and is NOT claimed here**: the per-riser nosing azimuth moves by up to **63.78 mm of arc at r_in**, which is above `GT_DELTA`, so GT-29's "below threshold" exemption does not transfer. §4 records what was actually run; an empty R-2 line means the row is not closed (§0-3) | CB-9 successor · GATE-1 pilot **19** · split proof by `_arc_split_proof` in `NEGOBS_SMOKE=1` (walked-top-face sampling over the annulus, GPU 0) | `LANDED` — see §4 |
| **GT-51** | 19 | **Rooftop dressing, guard height and asset sweep — five items, no walked surface among them.** (1) **Era rider §6.2-B executed**: *"Rail height 0.90 m outdoors is the wrong default. Outdoor = 1.10 m … **scene19 → 1.1 m**"*. `parapet.h` **1.00 → 1.10** (7 arc rings, `collider=True`), `access.guard.h_top` **1.00 → 1.10** (`EdgeGuard`, `collider=True`), gate posts `post_h` **1.15 → 1.25** — the posts are **not** a second era move: their feet are buried 0.05 below their step top, so 1.15 put the cap at `top + 1.10`, exactly flush with the old 1.00 parapet + 0.10 proud; against a 1.10 parapet the same 0.10 m gate tell needs 1.25. The **rooftop perimeter** parapet (`roof.pp_h` 1.20) is deliberately NOT moved: it is a different fixture under a different clause (건축법 시행령 제40조 옥상광장 난간 1.2 m), and `roof.pp_h_inner` (1.10) is the datum `roof_skyline`'s sight-line budget is computed against. (2) **N-A3 rooftop equipment, P0 for scene19** (`w3_execution_spec_v1.md` §3.3): the two procedural 0.9 × 0.35 × 0.8 boxes — a wall-hung 가정용 실외기 silhouette standing on a roof deck — become **2 × `exterior_aircon_unit`** (1.800 × 0.374 × 0.928, `zmin −0.320`) on their existing concrete plinths, plus **`power_box_01`** (0.512 × 0.362 × 0.506, `zmin −0.252`) beside the core door and **`utility_box_01`** (0.520 × 0.432 × 1.120) on the east run — G13's transformer/box hardware brought onto the roof. **Declared divergence from N-A3's literal `ac_unit_04`, with the measurement that drove it**: `ac_unit_04` is 3.604 × 4.203 × **1.985** m and every siting on this 12.5 × 12.5 m deck that clears the pipe run (y −8.61), the planter box (x 4.5…7.5) and the U_S parapet puts a 2.105 m mass — **0.2 m above the `roof_context` eye at z 1.9** — in that cut's sight line to the crown, clearance **0.15 m**. All three rows are CC0 MaterialX, so **all three go through `treatment="mtlxoff"`** (T4b-F1: a raw CC0 call site renders red) and all three are `z_mode="base"` (scene09 precedent); wrappers `exterior_aircon_unit__mtlxoff.usda`, `power_box_01__mtlxoff.usda`, `utility_box_01__mtlxoff.usda` are generated and committed. (3) **옥상 플랜터 rebuilt to code and pinned**: `curb_h` 0.45 → **0.90**, soil 0.40 → **0.75 m** — 조경기준(국토교통부 고시) 제12조 인공지반 최소 토심 **교목 0.70 m**, against which a 3.24–3.80 m tree on 0.40 m of substrate was below the standard the drawing would be approved on. Species pinned **`ash` (`Fraxinus.usd`, native 5.341) → `juniper` (`Chinese_Juniper.usd`, native 2.516)** by calling `build_tree` directly at the scene, because `build_planter` forwards `species=` to `place_shrubs` only and the kit is frozen this window; `trunk_h` 2.2 → 1.55 puts the deterministic draw at **2.5065 m**, i.e. scale **0.9961** — native proportions instead of a 1.4× stretch. Crown top **3.2565 m** (declared bound 3.30). Bed shrubs pinned to **`planter_accent` (`Yew.usd`, 주목)**, S-2's one-species-per-bed row; shrub count 2 → 3 because `tree_mtls=None` seats a third at the bed centre, and the tree moves to (−0.62, +0.62) to clear it. **This removes the last `Rhododendron` from scene19, so K4-F1's library-wide magenta loss cannot appear in this scene's next round** — declared, not discovered. (4) **19-4 membrane patches 4 → 2, re-sited and re-materialled to read as 우레탄 덧방.** Both patch roles were bound to `M["coating"]`, **the identical material as the deck**: a 2 mm proud plate in the same green at the same roughness is not a repair, it is nothing. New `patch_coat` (hue held, value +18 %, roughness **0.72 → 0.46** — sheen is the only cue that survives a shadowed frame) and `patch_lap` (the feathered coat edge) replace `coating` / `gk_stain`; `gk_stain` was the dark asphalt saw-cut line, which is the "reads as asphalt" failure the L19 brief names. `build_patch_field(cutline=False)` is the kit default and `apply_ground` never overrides it, so **no cut line is built at all** — the saw-cut vocabulary is absent by construction. Survivors carry two different causes: (11.60, −0.60) the ponding ring of drain 1, and (8.00, 2.60) the maintenance walking line out of the core door. (5) **Season pinned `summer` from G8** (Lane-3 3.7, §7 ruling 8) with a `_season_audit()` that asserts it: evergreen 교목, single-species 관목 with no `SEASONAL_SUBPRIMS` row, no `bare=` call, no leaf scatter in the `roof_membrane` profile | **No walked surface, no drop edge.** What moves and is therefore declared: **8 collision-box AABBs rise 100 mm** (7 `Parapet_i` + `EdgeGuard`) and 4 `Planter_A/Curb_*` collision boxes rise 450 mm — all of them **guards and containers, none a walked top face and none a drop edge**. The plinths, plant boxes and PH boxes are authored `collider=False` (`add_box` default) and enter no hazard list. `patch_proud` is **0.002 m**, two orders below `GT_DELTA = 0.020`. The gate posts, the tree and the shrubs are dressing. Prims **284 → 292** and hash `4ac6372a` → `3f67f1d5` are this row's, attributed prim-by-prim in the isolated-arm inventory diff: **−2** `Patch_2/3`, **+2** `Hvac_*/Asset`, **+2** `PlantBase_*`, **+2** `Plant_*` + **+2** `Plant_*/Asset`, **+2** `Shrub/Sh_2` + `Sh_2/Asset` | *(rides GT-50's single re-cache — §0-2, one re-cache per scene per batch)* | CB-9 successor · GATE-1 pilot **19** | `LANDED` — see §4 |

## 4. Landing record — filled at land, never before

One line per row, appended by the **owning WP** at the moment it commits. A row without a landing
record is not `LANDED`.

| # | Owner WP | CB | Commit | Command actually used | Result (registry / diff / baseline) | Date |
|---|---|---|---|---|---|---|
| GT-1 | S2 | CB-7 | `6edce66` | **R-1** `NEGOBS_SMOKE=1 python3 scenes/main/scene02_underpass.py` (the scene's new `underpass_selfcheck`; boot-free and GPU-free — it prints the hazard/drop registry re-derived from `PARAMS` and asserts 48 gates) · **R-2** `flock -w 7200 /tmp/negobs_gpu.lock` → `python3 scripts/run_data_render.py --run 260731_cb7_recache --scenes scene02 --conds L0,L7,L5 --cams 4` then `python3 scripts/check_data_run.py 260731_cb7_recache` · **R-3** `flock -w 7200 /tmp/negobs_gpu.lock` → 13-cut PT round `260731_w3_cb7` (`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`), `scripts/stamp_round.py`, then `scripts/regression_check.py` | **R-1** registry: **21 drop rows** (1 opening front edge + 20 nosings) · **1 `up_step` row** · 4 flat. Drop edge at `x = 0` = **3.380 m** (was 3.200) `[measured]`; the 0.180 riser at `x = −1.20` is emitted with `kind='up_step'` and is **excluded from the drop rows by construction** — GT-1's *"label it an up-step, not a drop"* is now a code invariant, not a note. Foot lands at **−3.2000** against the lower landing's −3.2000 (20 × 0.169 from `z_top` +0.180), so run 6.400, tread 0.320, the nosing period, the landing, the tunnel and the portal are **bit-identical to the pre-state**; every riser 0.169 ≤ the 0.18 statutory ceiling. Handrail (행안부 3-1-1 *난간 반드시 설치*) φ34 · h0.85 · 4 posts on RF-1 8T plates, RF-2 `sts304_10s`. Manhole moved (−1.20, 0.35) → (−2.90, 1.10) — the old site is **inside the apron footprint**; flush, so no GT change (J-11 keep-at-zero). **R-2** `DATA RUN CHECK PASS` — 12 cuts, 44.8 s, `r_reject 0.0`, nearest solid to any eye 0.277 m, 0 orphans, 0 look_check writes. **R-3** `260731_w3_cb7` is scene02's **new baseline of record**; adjudicated **twice** because 02 had no post-GT-8 baseline — against the stale `260730_w2d_fix` (FAIL 12) *and* against a contemporaneous isolated-arm HEAD round `260731_w3_cb7_pre` rendered in the same channel (FAIL 11 · WARN 2). DARK 0 · BLOWN 0 · OCCL new-dark ≤ 4.8 % except `beauty_overview` 7.1 %. `Docs/reports/regr_260731_w3_cb7.json` (CB-7's own) + `regr_260731_w3_cb7_pre.json` (carried-only). Geom prim census **391 → 545**. Full write-up: `Docs/reports/w3_cb7_v1.md` | 2026-07-31 |
| GT-2 | S2 | CB-7 | `6edce66` | *(rides GT-1's single re-cache — same commands)*; the builder's own numbers are re-derived boot-free by `underpass_selfcheck` block [2], which runs `infra_kit.build_curb_line` on a recording `Kit` for **both** kerb lines | Rebuilt on **`infra_kit.build_curb_line`** (K5). Per line: **40 blocks / 41 prims**, **28 blocks of exactly 1.000 m** inside the judged window (min 0.994) and 7.66 m ≈ `far_unit` outside it — the 1 m product rhythm survives where an eye can resolve it, at 41 prims per 120 m instead of 121. Curb top **+0.0200** (target: flush … +0.020 above the 0.000 footway) · exposure above the carriageway **0.1500** · `gt_drop` **0.1500** · `strict=True` warnings **0** on both lines. `gutter=False`, so there is no cross-fall term to add — this scene switched `gutter_L` off in W2-D with a measured reason. **The carriageway datum had to move −0.020 → −0.130**: it is the only value at which "exposure 150 mm" and "top flush … +20 mm" hold simultaneously, and `walk_a` / `walk_b` follow 7.70/13.30 → 7.80/13.20 so the sidewalk cut face meets the 0.20 m block body with no gap. R = 10 mm arris costs **0 prims** via `LOOK_CLASS['curb'].bevel`, asserted live by `check_arris_role(sc)` = 10.0 mm. Material `Looks/Curb` = `marble_light` — S06-B item 3's `curb_granite_light` role is **not authored** (procurement HOLD), `granite_dark` stays forbidden. The two deleted 120 m extruded kerb boxes carried **no collider and no hazard label**; checked out by self-check block [4] | 2026-07-31 |
| GT-3 | S2 | CB-7 | `6edce66` | *(rides GT-1's single re-cache; the row's own class is **R-3 only** — the OCCL re-stamp is the `260731_w3_cb7` round above)* | **Content flip executed as amended (§9-1): built, not deleted.** Canopy **x −1.90 … 7.15** (9.05 m) × y ±2.45, roof underside z 2.70 — **1.90 m of approach** (GT-3/U-5 require ≥ 1.00; scene16, the in-library reference at `:84`, has exactly 1.00) + the sill riser and its apron + the whole 6.40 m descent + the lower landing + 0.15 m past the pit rear. Roof deck 1 + eaves fascia 3 + **8** transverse beams at 1.30 m + **5 column pairs** at 2.26 m on the wall centre line y ±1.95 (cast-in mortar collars, deliberately **not** RF-1 plates) + **8 side-infill valances** z 1.75 … 2.70 + **10 soffit battens** (2 rows × 5 at 2.20 m) each with its own `SphereLight`. **The prim delta this row declined to guess is now measured: +154 net for the whole CB-7 commit (391 → 545, inventory hash `a4c3a5f9`), of which the canopy line is +45** (5 porch prims out, 50 canopy prims in — deck 1 + fascia 3 + beams 8 + columns 10 + collars 10 + valances 8 + battens 10; the 10 SphereLights are lights, not geometry) `[measured — `geom_invariance_check`, prim census, both arms]`. **OCCL moved as declared and it moved up**: the instrument fires on 13/13 cuts against the contemporaneous HEAD arm, new-dark ≤ 4.8 % everywhere except `beauty_overview` (7.1 %), near-band new-dark 0.0 % on 9 of 13. DARK 0, BLOWN 0. Two interior cuts (`pit_edge`, `inside_looking_up`) take PHOTO — declared: a canopy over a descent is a shading device, and they are the cuts the soffit battens exist for. **No walked surface moved** in either direction, as the row says. One arm was built, rendered and **rejected on measured evidence** — full-height glazing on the library's `glass` material (an opaque dark constant) read as a 9 m black wall and hid the BS-4 street wall; `Docs/reports/w3_cb7_v1.md` §4.2 keeps the crop | 2026-07-31 |
| GT-4 | S1 | ~~CB-11~~ | **n/a — `RETIRED` 07-31** (batch §9-2) | *(none, ever)* | **This record will stay empty by design.** A retired row lands nothing; P-5's evidence gate is discharged with it | — |
| GT-5 | S4 | CB-9 | `1234a51` (geometry) + `5cf0315` (pilot fix + report) | **R-1** `NEGOBS_SMOKE=1 python3 scenes/main/scene13_apartment_parking_entry.py` — the scene's new `hazard_registry()` (boot-free, GPU-free) re-derives the hazard/drop registry from `PARAMS` and the smoke report prints it, together with the kerb, gantry and turn-down gates · **R-2** `flock -w 7200 /tmp/negobs_gpu.lock` → `python3 scripts/run_data_render.py --run 260730_s13_recache --scenes scene13 --conds L0,L7,L5 --cams 4` then `python3 scripts/check_data_run.py 260730_s13_recache` · **R-3** `flock -w 7200 /tmp/negobs_gpu.lock` → 15-cut PT round **`260730_w3_s13b`** (`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`, channel byte-identical to the frozen judge round), `python3 scripts/stamp_round.py <out> 260730_w3_s13b scene13`, then `python3 scripts/regression_check.py --before scenes/main/look_check/scene13/260730_w2d_fix --after scenes/main/look_check/scene13/260730_w3_s13b --json Docs/reports/regr_260730_w3_s13.json` · §6.1 floor `python3 -m py_compile` + `python3 scripts/geom_invariance_check.py` + `python3 scripts/placement_lint.py --scenes scene13`, both **in isolated `git archive` arms** (seven other scene lanes were dirty in this worktree; `scene11` does not even assemble there) | **R-1** registry: **20 rows — 16 `drop` · 4 `grade`** `[measured]`. The four kerb lines enter as `drop 0.150` at `y = +7.20 / +9.20 / −7.40 / −9.40`; the **carried-in R-1 (§5) ramp-cheek kerb survives the re-cache** — `ramp cheek kerb N/P … 0.120` are still in the registry and the in-code handover still prints `[GT 인계 · W4] scene13 ramp_curb 낙차 0.120 m 신설`, so the *"a re-cache that quietly absorbs it is a regression"* condition is met. The three turn-downs are emitted with `kind='grade'` and are **excluded from the drop rows by construction** (the GT-1 `up_step` device). Kerb, as built `[measured — render log]`: **4 lines × 44.0 m · 95 blocks · 119 prims** · unit **1.00 m inside the judged window** (`lod_span (8, 28)`, `far_unit 8.0`; whole-run mean 1.91) · exposure **0.150** · curb top **+0.150 = the footway top, flush** (S06-B 2.) · arris `look` R10 at **0 prims**, asserted before boot by `ik.check_arris_role(sc, 'curb', 0.010)` → `LOOK_CLASS['curb'].bevel = 10.0 mm` (the call **raises** on mismatch) · material `Looks/Curb` ← `marble_light` (S06-B 3.'s `curb_granite_light` role is unauthored — procurement HOLD; same stand-in CB-7 bound, `granite_dark` still forbidden). **`gt_drop = 0.150`, not the builder's default 0.168** — deliberate and recorded: the default's +0.018 is an L-gutter cross-fall, and this kerb faces a **planted verge**, not a carriageway (3 m of lawn separates the footway from the estate road), so `gutter=False`. 턱낮춤 ≤ 20 mm wherever another footway plate abuts, or the kerb would wall off a footway-to-footway junction: `N_in` s 10.8…12.8 + 25.4…28.4, the other three s 10.8…12.8, taper 1.0 m, block boundaries forced so none straddles a transition. **R-2** `DATA RUN CHECK PASS` — 12 cuts / 12 records, every cut content-unique, 1920×1080, 2.85 s/cut vs SP-3's 2.87, nothing written into `look_check/<scene>/`. **R-3** baseline re-stamped: the new **baseline-of-record is `scene13/260730_w3_s13b`** (stamp carries `baseline_of_record: true` · `supersedes: 260730_w2d_fix` · `comparison_baseline_used: 260730_w2d_fix` · `dirty_paths` (13) · `superseded_arm`). **Which baseline it was checked against** (§7 watch item W4): scene13 appears in **no** `regr_*.json` in the tree, so the comparison is the scene's own baseline-of-record **round** `260730_w2d_fix`, A/B, and the result is stamped as `Docs/reports/regr_260730_w3_s13.json`. Verdict **FAIL 14 / PASS 1**, and every finding is adjudicated in `w3_s13_v1.md` §7: all 14 are `FRAME` (composition change — which *is* this batch's deliverable; the one PASS is `portal_look`, the only view in which nothing above grade changed) plus `OCCL` ≤ 3.2 % new-dark with ≤ 0.4 % blob on the presets (street-tree crown shadow; near-band ≤ 0.3 % except h1.8_d2's 1.9 %). `PHOTO` h0.9_d2 +26.3 mean is the deleted canopy shadow — **no lighting value moved**. `DARK` h0.3_d10 is classified by the checker as carried, not a regression. `EXPECTED_FP` h0.3_d10: max-change row y151 ∈ `EXPECTED_FP[('scene13', 'preset_h0.3_d10')]` 140…160@540 (`tactile_stair_foot`) — the D14 reader working as designed. **GRAZE on `h0.3_d2` · `h0.3_d5` · `ramp_graze` is UNDECIDED**: the checker withheld judgement itself because frame photometry moved (Δmean +7.9/+9.2/+8.1, Δdark −29.5/−34.4/−25.5 pp). There is no lighting regression to fix first — the shift is the canopy shadow ruling §7-5 ordered deleted — so the GRAZE verdict is **carried to the next scene13 round**, which will compare against this photometrically stable baseline. Recorded as a watch item in `w3_s13_v1.md` §10-5. `near_ground_stats` moved in the right direction on **all six judged cuts**: `flat_gnd` h0.9_d2 47.2 → **14.6**, h0.3_d5 25.8 → **13.1**; `flat%` h0.9_d2 50.0 → **6.3**; `edg%` h0.3_d2 8.2 → **30.9**. Prims 495 → **674** `[measured, isolated arms]`; `geom_invariance` **33/33 R-4 + R-6**; `placement_lint` scene13 **ERROR 0 and byte-identical finding profile** to the pristine baseline arm | 2026-07-30 |
| GT-6 | K4(d) → S4 | CB-5 / CB-9 | — | — | — | — |
| GT-7 | S6 | CB-8 | — | — | — | — |
| GT-8 | K1 | CB-2 | *(CB-2 batch commit)* | `python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml` · `python3 ground_kit.py` · `python3 scripts/geom_invariance_check.py` | **LINT-8 (no `rotz ≠ 0` on any patch/stain) 295 ERROR → 0**, measured A/B on the same tree at the same instant (every other check byte-identical: 374→79 ERROR total, WARN 359, BLOCK 29, INFO 2 unchanged). `ground_kit.py` 33/33 PASS. `geom_invariance_check` R-4 33/33 · R-6 33/33. **`frame_budget` movement, as the row predicted**: B2 area-share `scene08` 81.9→44.8 % · `scene19` 92.4→68.8 % · `scene15` 87.6→83.2 % · `sceneN1` 76.7→79.9 % · `scene05` 68.2→69.3 %; **B5 near-field decal count `sceneD2` 6→5, so D2 gains a soft B5 warn** — the only new soft-gate warning in the library and exactly the B1/B2/B5 movement spec §6.2-K1 told K1 to expect. **`regr_260730_w2d_fix.json` is retired from this commit**; the new baseline is stamped at CB-2's GATE-1 round `260731_w3_cb2`. R-2 (mini data render) **not owed** — no walked surface, no hazard box and no drop edge moves | 2026-07-31 |
| GT-9 | K1 | CB-2 | *(CB-2 batch commit)* | `python3 ground_kit.py` · per-scene element dump over all 33 `SCENE_PLANS` (`_fixture_plan` → elements of kind `weed`) · `python3 scripts/geom_invariance_check.py` | **Clamp factor, as required by §6-W1**: native exposure `zmax` **0.1229 m** `[measured — veg_manifest_w2.json]`, so the nominal ceiling scale is **s = 0.12 / 0.1229 = 0.9764** → exposure **0.1200 m** (exactly the class-A bound, not above it) and footprint **0.2789 × 0.9764 = 0.2723 m**. Scale is driven by the **GT-E5-clamped** `proud`, written back into the op by `_writeback_weed_heights` after `_clamp_gt_e5`; the largest height actually shipped is **0.1182 m** (`scene13`) → s **0.9618**, footprint **0.2683 m**. **25 of 85 clumps are clamped by the ramp, 0 dropped.** The bigger footprint bites as designed: profile δmax falls (`plaza_granite`-family 0.1182 → 0.0060–0.0103, `sceneC2`/`C4`/`15` 0.1182 → 0.0798, `02` → 0.0867, `08` → 0.0947, `16`/`N5` → 0.1041, `03`/`17`/`D3`/`N2`/`N4` → 0.1121). `_elem` aabb recomputed from the scaled bbox, and re-shrunk for clamped clumps so the registry cannot carry a footprint the stage does not have. **Count correction**: 85 instances / 13 scenes, not 139 / 22 — A1's own text deletes `plaza_granite`'s weed row (§7-W6). Class **A** confirmed: no clump exceeds 0.12 m, so no re-cache | 2026-07-31 |
| GT-10 | S5 | CB-1 | — | — | — | — |
| GT-11 | S1 | CB-10 | — | — | — | — |
| GT-12 | K3 | CB-4 | — | — | — | — |
| GT-13 | T4 → S3 · S4 | CB-10 | — | — | — | — |
| GT-14 | S3 | CB-S3-07 | `cd2745b` (+ pilot fixes `5e134f1`, `c3cebc3`) | **R-1** `NEGOBS_SMOKE=1 python3 scenes/main/scene07_temple_stone_path.py` (new `stone_course_selfcheck`) · **R-2** `flock -w 7200 /tmp/negobs_gpu.lock` → `python3 scripts/run_data_render.py --run 260731_s07_recache --scenes scene07` then `python3 scripts/check_data_run.py 260731_s07_recache` · **R-3** `flock -w 7200 /tmp/negobs_gpu.lock bash <scratch>/run_260731_w3_s07.sh` (14 cuts, PT_FAST · LOOK_V1 · DETAIL_SCALE 2 · ROUGH_GAIN 0, `NEGOBS_VIEWS` unset = full order prefix) then `python3 scripts/regression_check.py --scenes look_check/scene07 --before-round 260731_w3_cb2 --after-round 260731_w3_s07 --json Docs/reports/regr_260731_w3_s07.json` and `python3 scripts/near_ground_stats.py 'look_check/scene07/260731_w3_s07/pt_noon_preset_h0.3_d*.png' 'look_check/scene07/260731_w3_cb2/pt_noon_preset_h0.3_d*.png'` | **Baseline compared against: `260731_w3_cb2`** (§6-W4 — the CB-2-stamped baseline, not the retired `regr_260730_w2d_fix`); the new round **`260731_w3_s07` is stamped as scene07's baseline-of-record** from here. **R-1**: 28 courses / 89 slabs; **open-slope fraction 0.000 %** (was 34.0 %), max course-to-course gap **−0.0936 m** (always overlapping), interlock **0.0602–0.1791 m** ≥ the 50 mm heritage floor, widest within-course joint **0.0482 m** ≤ 0.060, rise **0.1270–0.1745 mean 0.1489 spread 0.0475** inside the declared 0.120–0.180 and summing to 4.170000 exactly, entry **+0.1456** (was +0.002), **exit +0.0300 m labelled UP-STEP** (was +0.201), tread-back clearance over the lowered bed **+0.0526 m** (no plane pierces a level tread), 속채움 underside **−0.0976 m** below the bed top (nothing floats). **R-2**: 8 cuts, `check_data_run` [1] geometry / [2] sampler truncation / [3] EV / [4] manifest-and-file integrity / [5] throughput (3.16 s/cut vs SP-3's 2.87) **all PASS**; the run's 2 FAILs are both zero-sample cross-condition checks (`0 pairs >= 0.3 EV apart`, `0 scene-pairs`) that need `--conds` > 1 and are an artefact of the mini scope, not of the geometry. **R-3**: 14/14 cuts, **2 FAIL only — `preset_h0.9_d2` FRAME 51 %** (the declared result, §6.4) and **`preset_h0.3_d2` GRAZE**, adjudicated by eyes on `look_check/scene07/260731_w3_s07/crops/graze_band_h0.3_d2.png` (the single high-contrast shoulder line is replaced by articulated courses + the statutory 돌깔기 apron; the shoulder step got **73× bigger**, 0.002 → 0.146 m, so the drop is more readable per step, not concealed). **DARK 0 · BLOWN 0 · OCCL max 0.7 %**, and `near_ground_stats` on the h0.3 band is **flat against the baseline** (σ_LF 13.69→13.69 · 22.88→22.97 · 4.08→4.10; edge% 80.8→79.3 · 50.6→50.3 · 90.3→90.3) | 2026-07-31 |
| GT-15 | S3 | CB-S3-07 | `ee4af00` (+ `5e134f1`, `c3cebc3`) | *(rides GT-14's round — same commands)* | 30 야면석 boulders, 15 per flank, **0.423–0.864 m** across standing **0.203–0.306 m** proud, sink 0.035 ≤ the F2 no-sink-ring limit; nearest inner edge **\|y\| 0.816 m** against the §6.5 floor of `foot_half + 0.10 = 0.32`; outer edge **\|y\| 1.680 ≤ 1.70**, so **no boulder overhangs the south drop** (H8) — the spec's fixed `y ±1.55` line was replaced by an edge anchor for exactly that reason and the deviation is stated in the file. Discontinuity: max gap 3.65 / 3.63 m per flank. **Two findings the pilot forced**: (1) scene07 is the first scene in the tree to load an urban asset and `assets/urban/nv_core/materials/SimPBR.mdl` **fails to compile** (`could not find module .::baking_annotations`) — every boulder rendered **flat bright red**; cured in-lane by `instanceable=False` + an ancestor `strongerThanDescendants` bind (an ancestor binding cannot reach inside an instance prototype), the MDL search-path defect itself belongs to whoever owns `assets/urban`; (2) the two framing trunks are **not shipped** — an A/B isolates them as the entire DARK/OCCL delta (`side_slope` 87.9 → 10.1 mean, 24.4 → 93.9 % dark) | 2026-07-31 |
| GT-16 | S3 | CB-S3-07 | `bbf085d` | *(rides GT-14's round — same commands)* | 24 `StoneKnob_*` prims deleted (`collider=False`, built below the stone top by construction) — geom prim census **1090 → 1066, exactly −24**. Jitter caps landed in the same commit: `cy` ±0.35 → **0** (measured max \|cy\| 0.0000) and yaw ±4.0° → **±3.0°**. **The SMOKE rise/gap/entry/exit table is bit-identical across this commit** (rise 0.111–0.232 mean 0.174, gaps 0.050–0.276, entry +0.002, exit +0.201) because the seeded stream still draws the abolished `u` — the walked surface provably did not move, which is what the row claimed. `LINT-10`'s `jitter=` token adjudicated and renamed `tint_jit` (material tint, §12-15), −1 WARN | 2026-07-31 |
| GT-17 | S3 | CB-S3-07 | `120c353` (+ `c3cebc3` albedo lift) | *(rides GT-14's round — same commands)* | `leaf_ground`-bound plates and slopes **5 → 0** (`PathCorridor` · `SouthTerraceA/B/C` · `Approach` → `dirt_park` summer forest floor). Margin lobes retained and re-sited: 6 corridor lobes to \|cy\| ≥ 1.20 (§4.1-5 floor 1.0), each sized to land **inside one tread**, walk line never crossed; feather cover 0.06 → 0.035 on the corridor ring; `sct_debris_leaves_dry_*` **0 placements** (H10). Moss is now zone-driven, achieved vs §4.1-3 target: walked centre **0.037** (0.00–0.10) · tread outer **0.411** (0.35–0.55) · riser **0.848** (0.60–0.85) · joints **1.000** · boulder tops **0.767** (0.70–0.90) — all IN band, printed not gated (research §B4b: no Korean document quantifies tread moss). Riser moss is delivered by a cap/body slab split, **not** by a proud strip along the nosing, which H2 / RF-5 forbid. `TEX["moss"]` gets its first consumer in the tree, `nor` dropped per the K4 GL/EXR caution and the raw scan confined to the flat 속채움 bed after it read as a green camouflage patchwork on curved and slab-sized surfaces. **Render-gate item as declared**: the terrace albedo change is visible and its net effect on the judged h0.3 band is nil (see GT-14's `near_ground_stats` row) | 2026-07-31 |
| GT-18 | S3 | CB-S3-10 | `c2b6841` | `flock -w 7200 /tmp/negobs_gpu.lock` → `NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=look_check/scene10/260731_w3_s10 NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 NEGOBS_VIEWS=<9 preset prefix + reversal,through_treads,broken_rail,leaf_edge,from_below> python scenes/main/scene10_park_deck_switchback.py` · `python3 scripts/stamp_round.py look_check/scene10/260731_w3_s10 260731_w3_s10 scene10` · `python3 scripts/regression_check.py --before look_check/scene10/260731_w3_pre10 --after look_check/scene10/260731_w3_s10 --only <5 preset cuts> --json Docs/reports/regr_260731_w3_s10.json` · `python3 scripts/near_ground_stats.py 'look_check/scene10/260731_w3_s10/pt_noon_preset_h0.3_*.png' --gate` · floor per commit: `python3 -m py_compile` · `NEGOBS_SMOKE=1 python3 scenes/main/scene10_park_deck_switchback.py` · `python3 scripts/geom_invariance_check.py --scenes scene10` · `python3 scripts/placement_lint.py --scenes scene10 --rules Docs/briefs/placement_rules_v1.yaml` · **[S10c 종결 07-31]** **R-2, the invocation this row recorded as owed**, run at `a8e8343` (the fixed code): `flock -w 7200 /tmp/negobs_gpu.lock` → `python3 scripts/run_data_render.py --run 260731_data_s10 --scenes scene10` then `python3 scripts/check_data_run.py 260731_data_s10` (defaults `--conds L0 --cams 8 --seed 20260730`, the arm `260731_s07_recache` used). **R-3 re-run** on the leaf-off fix: `flock -w 7200 /tmp/negobs_gpu.lock` → `NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=look_check/scene10/260731_w3_s10c NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 NEGOBS_VIEWS=<the same 14: 9 preset prefix + reversal,through_treads,broken_rail,leaf_edge,from_below> python scenes/main/scene10_park_deck_switchback.py` · `python3 scripts/stamp_round.py look_check/scene10/260731_w3_s10c 260731_w3_s10c scene10` · `python3 scripts/regression_check.py --before look_check/scene10/260731_w3_s10 --after look_check/scene10/260731_w3_s10c --json Docs/reports/regr_260731_w3_s10c.json` · `python3 scripts/near_ground_stats.py 'look_check/scene10/260731_w3_s10c/pt_noon_preset_h0.3_*.png' --gate`. The pre-fix attribution round `260731_w3_pre10c` was rendered at the same HEAD with the same arm. Floor at `a8e8343`: `python3 -m py_compile scenes/main/scene10_park_deck_switchback.py` · `NEGOBS_SMOKE=1 python scenes/main/scene10_park_deck_switchback.py` · `python3 scripts/geom_invariance_check.py` (**unscoped**) · `python3 scripts/placement_lint.py --scenes scene10 --rules Docs/briefs/placement_rules_v1.yaml` | **Comparison baseline named per §6-W4: `260731_w3_pre10`**, this scene's own clean intermediate round at HEAD `1346b70` — *not* `260730_w2d_fix`, which has 13 cuts and predates CB-2's scene10 edit (`11d1e56`), so a diff against it would have carried CB-2's leaf-lobe delta entangled with the rebuild (spec §6.4 traps 1 and 2). `260731_w3_pre10` vs `260730_w2d_fix` on the 5 shared cuts: **FAIL 0** (1 WARN `[UNCHANGED]` on `h0.3_d2` — mean difference 0.24 LSB, pixels over 4 LSB 0.063 % — 2 INFO, 2 PASS), which **verifies CB-2's scene10 F3 work as null on the judged cuts** rather than leaving it open. `260731_w3_s10` is stamped `baseline_of_record: true`. **GATE-1 P10 result**: FRAME FAIL on all 5 preset cuts — **the declared expected result** (§6.4: both rebuilds intend to move every pixel of the stair). The gates that still mean something: **DARK improved on all five** (dark% 3.0-13.2 → 0.7-3.3), **BLOWN/WHITE 0 flags**, **OCCL one flag** (`h0.9_d2`, new dark 2.1 %, largest blob 1.0 % — the +150 railing prims and the bare-tree canopies shadowing what was open lawn), PHOTO luminance-up on 3 cuts with intent confirmed. `near_ground_stats` B45/B30: **`flat_gnd` cleared on all three h0.3 cuts** (3.5 → 0.4 · 0.1 → 0.0 · 0.7 → 0.0) and `sd` on h0.3_d2 crosses its 32 threshold (24.8 → 36.7); **two new WARNs on h0.3_d2** (mean 181 > 170, wht% 7.6 ≥ 2) declared and not tuned away — at 2 m the near band is the deck, not ground, and the deck is at its measured 2-5 yr patina albedo 0.230 under a 49.8° noon sun. **R-1 done** — `deck_module_selfcheck` re-derives and prints the whole ladder: `44 × 0.150 = 6.600` exactly · `8+7+8+7+7+7 = 44` · `2R+T = 0.610 ∈ [0.600, 0.650]` · clear width 1.500 ± 0.010 · every landing ≥1.500 deep in travel · max rise between level surfaces 1.200 ≤ 2.000 · leaf band re-derived onto treads 1·2 at tops −0.145/−0.295 · last-landing proud +0.020 ∈ (0, 0.05]. **R-3 done** — `260731_w3_s10` stamped as the new baseline-of-record; `Docs/reports/regr_260731_w3_s10.json`. **R-2 OWED** — the mini data render is the data owner's invocation (`scripts/run_data_render.py --run <id> --scenes scene10` + `check_data_run.py`); per §0-3 it is recorded as owed rather than guessed, so this row is **not closed**. Floor per commit: py_compile 0 · SMOKE clean · geom_invariance R-4 1/1 · R-6 1/1 (prims 1266, 3-arm hash `21828c8c`) · placement_lint **delta 0** **[S10c 종결 07-31 — 이 행을 `LANDED` 로 닫는다]** **R-2 DONE**: `dataset/260731_data_s10/test/scene10/`, **8 cuts · 2.34 s/cut**, manifest `git_head a8e8343`. `check_data_run`: **[2] azimuth ledger · [3] camera placement · [4] file/manifest · [5] throughput — ALL PASS** ([3] `ground_below == h_rel` worst \|err\| **0.0000 m**, nearest solid to any eye **0.175 m ≥ 0.15**, every sampler truncation respected; [4] 8 files / 8 records, all content-unique, all 1920×1080, **nothing written under `look_check/`**; [5] 2.34 vs SP-3's 2.87). **[1] carries 2 FAILs and they are recorded, not cured**, exactly as GT-14's did: `sun-bearing: ground darkens with net EV, per scene (0 pairs >= 0.3 EV apart)` and `sunless: less deep shadow than the L0 reference (0 scene-pairs)` — both **zero-sample cross-condition** checks that need `--conds` > 1; an artefact of the mini scope, silent about geometry, and not a reason to hold this row open. **R-3 RE-DONE** on the new baseline-of-record **`260731_w3_s10c`** (14 cuts, arm byte-identical to `260731_w3_s10`): **FAIL 1 · WARN 7 · INFO 3 · PASS 3**, and **every FAIL and WARN is a `FRAME` code** — the FAIL is `from_below` (block shift 56 %), the cut framed on the near-field birch whose canopy this fix removes. Channels that still mean something, all 14 cuts: **DARK falls on every one** (3.41→1.57 · 2.39→1.11 · 7.30→4.99 …), **255-clipping 0.000 %**, **WHITE max 0.96 %**, **OCCL max new-dark 0.028 % / blob 0.005 %** against this round's predecessor flag of 2.1 % / 1.0 %. `near_ground_stats` h0.3 triple flat (sd 36.7→36.7 · 28.7→28.5 · 23.0→22.9, `flat_gnd` unchanged) with **GT-18's two declared `h0.3_d2` WARNs still present and still not tuned away** (mean 181 > 170, wht % 7.6→7.8 ≥ 2). **Attribution, measured not asserted**: the pre-fix intermediate `260731_w3_pre10c` at the same HEAD scores **FAIL 0 · WARN 0 · INFO 7 · PASS 7** against `260731_w3_s10`, so the whole Lane-1 kit window (K4 a–d · K5 · K1 micro · T4) is **null on this scene's judged cuts**; re-running the comparison against `260731_w3_pre10c` instead returns the **identical verdict set**. Floor at `a8e8343`: py_compile 0 · SMOKE rc 0, `deck_module_selfcheck` all-OK · geom_invariance **unscoped 33/33** R-4 + R-6 — scene10 prims **2777 unchanged**, hash `606edef7` (at `e3619df`) → `ae8b49ff` (kit window, no scene10 edit) → **`f8e2670e`** (this fix) · placement_lint **delta 0** (ERROR 0 · WARN 9 · BLOCK 1; the only text delta is the species census spelling `Gray_Birch` → `Gray_Birch_bare`, K4-F5 arriving in a scene). Report: `Docs/reports/w3_s10_close_v1.md`. | 2026-07-31 |
| GT-19 | S3 | CB-S3-10 | `5ce512e` (+ `e3619df`, corridor slab thickness fix) | *(rides GT-18's round — same command)* · **[S10c 종결 07-31]** *(rides GT-18's re-run round and its R-2 — same commands)* | Ground field re-derived and **asserted**: flight↔flight plan overlap **0.000000 m²**, flight↔landing overlap **0.000000 m²**, air gap under the deck 0.020-0.600 m all positive, **stair foot 0.250 m ≤ 0.300 m** (KFS-TRAIL 12-3 마), 0 masonry plates over the deck run, head wall exposure 6.62 → **0.255 m**, corridor mean grade 25.8 % / steepest 48.4 %. Plan x[−1.19, 5.79] → **[−1.50, 24.14]**, y ±1.60 → **[−1.60, 3.10]**; the divergence from §4.2-4A's *roughly* x[−1.5, 12] is arithmetic and is written into the §3 row. **Defect found by the pilot and fixed in a follow-up commit**: the corridor slab at 1.60 m thickness left a **4.8 m see-through band** between its underside at the head (−1.855) and the lower park top (−6.62) — measured on the first `260731_w3_s10` render, `from_below`; thickness → 7.00 and the pilot re-rendered. Floor: py_compile 0 · SMOKE clean · geom_invariance R-4 1/1 · R-6 1/1 (prims 1219, hash `93a5d718`) · placement_lint **delta 0** **[S10c 종결 07-31]** Nothing in this row was touched by the S10c fix: the de-stacking, the corridor slope, the air gap and the head wall are geometry, and the isolated-arm inventory shows **12 differing rows out of 2777, all of them a tree's reference string** — 0 rows differ in path, type, xformOp or shape attribute. The numbers in the record above were re-derived by `deck_module_selfcheck` at `a8e8343` and print unchanged. Closed as `LANDED` on GT-18's R-2, which was the only thing this row was ever waiting for. | 2026-07-31 |
| GT-20 | S3 | CB-S3-10 | `ed928e5` | *(rides GT-18's round — same command)* · **[S10c 종결 07-31]** *(rides GT-18's re-run round and its R-2 — same commands)* | **R-1 done** — the railing block of `deck_module_selfcheck` asserts every member section against the stocked 방부목 set, **round railing members = 0**, rail height 1.10 to the top face, baluster clear gap on every run (worst **0.1094**, target 0.110 ± 0.010), balusters plumb, **the broken bay is exactly `LandRail_0_Out`** with rails and balusters gone and posts and newels remaining, ~~20 newels deduplicated from 28 run endpoints~~ **28 newels deduplicated from 40 run endpoints** `[supervisor amendment 07-31 · ledger batch §9-4]` — 20/28 was a **pre-de-stacking snapshot** written from commit-time state and not re-derived at batch end (`redteam_s0710_rebuild.md` **F4**); re-derived live this session, `NEGOBS_SMOKE=1 python3 scenes/main/scene10_park_deck_switchback.py` prints *"엄지기둥 28개 (런 끝점 40개에서 중복 제거) · 갓 0.120x0.120x0.045 · 난간 위 돌출 0.150 m"*. **No geometry moved with this correction** — GT-19's six-flight de-stacking created the extra run endpoints and is already landed; the prim counts and hashes in this record stand, one lattice bay on `EntryRail_P`. **R-3 done** via GT-18's re-stamped round. Both rail-height authorities are on the §3 row (KNPS median 1.10, n = 1,227 / 조경설계기준 16.20.2(2) ≥1.2 m). Weathering was aimed at the measured CIELAB band and **hit it on the existing map** — clipped fraction 0.02 % — so §8.R OQ-8's G5 procurement attempt was **not** triggered and the row stays open and unspent. Floor: py_compile 0 · SMOKE clean · geom_invariance R-4 1/1 · R-6 1/1 (prims 1038, hash `e0133ccd`) · placement_lint **delta 0** **[S10c 종결 07-31]** The railing is untouched by the S10c fix (no railing prim is among the 12 differing inventory rows) and the R-1 railing block of `deck_module_selfcheck` re-prints identically at `a8e8343`, including the amended **28 newels from 40 run endpoints**. R-3 rides the new baseline-of-record `260731_w3_s10c`. Closed as `LANDED` on GT-18's R-2. | 2026-07-31 |
| GT-21 | S3 | CB-S3-10 | `1962f76` | *(rides GT-18's round — same command)* · **[S10c 종결 07-31]** *(rides GT-18's re-run round and its R-2)* — plus the fix commit `a8e8343` and, as the pixel evidence the closure rests on, the pre/post montages `Docs/reports/_w3_s10c_crops/*.png` cut from `260731_w3_pre10c` and `260731_w3_s10c` | Census closed: **12/12 trail trees leaf-off**, **12/12 far belt pinned to `Chinese_Juniper`**, **13/13 shrub clumps** real autumn-legal USDs, **780** litter instances seated by `ground_fn` on the 25.8 % slope, **4** outcrop rocks at `z_mode='base'` sink 0, **3** windowless silhouettes at d_true ≥ **81.4 m**. The 4 CB-2 carpet-mask lobes are **kept** (H4). **The single largest verification movement in the lane**: `placement_lint` **LINT-4b 9 ERROR → 0** — the retired species (`White_Pine` ×5 with an uncorrected zmin −0.351, `Yellow_Pine` ×4) were coordinate-hash draws from `build_tree`, and pinning the species removed them; trees are still placed at `<prefix>/Veg` so the linter's tree rule still sees all 24 (inventory `tree=24`). **Two corrections recorded rather than silently applied**: (a) §4.2-5's literal grass tint (0.62, 0.60, 0.42) is a *multiplier* on a map whose mean linear is (0.0621, 0.1115, 0.0232), so it yields R/G 0.58 — still green-dominant; the shipped tint is derived to a straw target (3.40, 1.55, 3.30) → #7F734E, Y 0.174, L* 48.8, R/G 1.22, clipping 0.02 %. (b) the T2 rock scans bind `assets/urban/nv_core/materials/SimPBR.mdl`, which **fails to compile in this runtime** (`C120 could not find module '.::baking_annotations'`) and rendered the boulders as a flat saturated red fallback; an ancestor `strongerThanDescendants` bind does **not** reach inside a prototype (re-measured), so the fix is `instanceable=False` + a per-mesh bind, mirroring `urban_kit._bind_far_override`. Floor: py_compile 0 · SMOKE clean · geom_invariance R-4 1/1 · R-6 1/1 (prims 2777, hash `606edef7`) · placement_lint **ERROR 9 → 0**, WARN 9 · BLOCK 1 unchanged **[S10c 종결 07-31 — the leaf-off arm, actually delivered]** **This row's leaf-off arm did not exist in a rendered frame until `a8e8343`.** The mechanism it relied on (`sc.BARE_SUBPRIMS` applied by a stage-side `SetActive(False)` under an instanceable prim) is **composition-inert** — USD discards opinions on descendants of an instance regardless of authoring order — so `260731_w3_s10` printed `잎-off 12/12` and rendered **twelve trees in full green leaf** (`redteam_s0710_rebuild.md` **F1**, found by eyes on `from_below` and `h1.8_d10`). `_bare_tree` now references the additive wrapper layers `assets/veg_bare/*_bare.usda` through `sc.veg_wrapper_rel` (K4(0) `e4fc4cf`, scene04 precedent `024a985`), which composes the strip **inside** the prototype. **Verified in pixels, which is what this row was reopened for**: green-pixel share on `from_below` **8.18 % → 0.00 %**, `h1.8_d10` 1.55 % → 0.00 %, and the near-field birch reads as a bare white armature in the committed montage. **Control**: `Chinese_Juniper` keeps its needles beside two now-bare deciduous trees — the far-belt evergreen re-assignment this row made is intact and was not collateral damage; `through_treads` holds 5.06 → 5.02 % green for the same reason. `native_h` was deliberately **not** re-sourced from `sc.BARE_NATIVE`, so `target_h / native` is bit-identical across the fix and **no trunk moved**; the census, tints, litter, outcrop and silhouettes of this row are unchanged and re-print identically. **Owed, and deliberately not taken by this task**: the §3 row above still reads *"registered in `sc.BARE_SUBPRIMS` by the K4 micro-commit `1346b70`, which reported success, so the §8.R contingency did not fire"* — that clause **is** the F1 defect in one sentence and needs a supervisor amendment line on the GT-6 precedent (strikethrough, no deletion). This task owns landing records only and has not edited the §3 text. | 2026-07-31 |
| GT-22 | S5 | CB-S04 | `024a985` | **R-1** `NEGOBS_SMOKE=1 python3 scenes/main/scene04_parktrail.py` (the scene's own `verge_selfcheck`; boot-free and GPU-free, and it also runs at the end of every assembled scene) · **R-3** pilot round `260731_w3_s04` under `flock -w 7200 /tmp/negobs_gpu.lock`, arm byte-identical to the baseline's `round_stamp.json` env (`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`), then `python3 scripts/regression_check.py --before look_check/scene04/260730_lcfreeze_post --after look_check/scene04/260731_w3_s04 --json Docs/reports/regr_260731_w3_s04.json` and `python3 scripts/near_ground_stats.py` on the h0.3 triple. **§0-3 note**: `w3_s04_v1.md` §8.3 records the round, the arm and the baseline but does **not** paste the literal render/regression invocation; the pair above is read back from `regr_260731_w3_s04.json`'s own `pairs` block rather than guessed, and is marked as such. **Floor** (§6.1): `python3 -m py_compile scenes/main/scene04_parktrail.py` · `NEGOBS_SMOKE=1 …` · `python3 scripts/geom_invariance_check.py --scenes scene04` · `python3 scripts/placement_lint.py --scenes scene04` | **Baseline named per §6-W4: `260730_lcfreeze_post`** — scene04's latest round (13 cuts, git `0972b20`, the "post" arm of the lighting/camera freeze proof); **`260731_w3_s04` is scene04's baseline-of-record from here**. **R-1** — `verge_selfcheck` re-derives and prints: hazard registry **unchanged** (T4 sleeper stair · 9 risers · run 5.550 · drop 1.450 · corridor \|y\| ≤ 0.90 · tread tops −0.160 … −1.450); walk intrusion **0** (lobes 77 +0.051 · cards 320 +0.109 · tufts 14 +0.682 · trunks 22 +1.040 · **posts 12 +0.300**); handline 6 posts/side · 5 spans · pitch 1.446 ≤ 1.80 · Ø0.120 ≥ 0.07 · nearest camera 1.410 ≥ keep-out 1.20 (13 cameras) · **0 rigid rails · 0 infill · 0 members across the drop edge · built in BOTH arms** — R04-1's *dressing, not a guard* is **asserted in construction, not in prose**; grounding embed 0.100 > 0.261 × Ø0.120 = 0.0314; 04-B gravel 6 tiles, max outside trail **+0.000**; seasonal audit 12 rows. **R-3** — 13/13 cuts: cut verdicts **9 FAIL · 4 WARN**, every FAIL **FRAME** and **declared in advance** by the dispatch note (block occupancy 34–70 % after tone normalisation — that movement *is* the verge swap). Channels that still mean something: **DARK 0 · BLOWN 0** (255-clipping **0.000 %** on all 13) **· WHITE 0** (max 1.32 %); **OCCL 8 WARN** (new dark 2.0–5.6 %, largest blob ≤ 1.0 % — the 22 trunks, 12 posts and 60 rope segments the §3 row predicted); **GRAZE 1 WARN** (`h0.3_d10`, rides the same swap). `near_ground_stats` h0.3 median: **sd 22.7 → 31.9** (the metric the ground layer exists to move, +40 %, now at its WARN floor), mean 110 → 85 ≤ 170, p99 192 → 168, >224 % 0.00, flat % 0.00 → 0.05 < 8, wht % 0.1 → **0.0**, flat_gnd 0.0, σ_LF 3.09 → 3.25 (**still short of its ≥5 floor — far-field terrain, not dressing; recorded, not tuned away**). **R-2 not owed** — class A, no walked surface moved. **Floor**: py_compile OK · SMOKE exit 0 · geom_invariance **R-4 1/1 · R-6 1/1**, prims **835 → 1335** · placement_lint **0 ERROR / 17 WARN / 1 BLOCK** against a pre-edit baseline of **4 ERROR** (LINT-4b retired species `Yellow_Pine` via `veg_pool()`) / 18 WARN / 1 BLOCK — the 4 errors are **fixed**, not suppressed. **Two things this record does not hide**: (a) the tree-wide `geom_invariance_check` could **not** complete at landing — `scene18` exits 1 under the still-running S18 lane — so it ran **32/32 PASS** with scene18 excluded, and the ~~**33/33 run is owed** to whoever closes that lane~~ `[batch §9-7: re-run unscoped at the ledger-batch HEAD — **33/33 PASS**, scene04 prims 1335 hash `d530f155` reproduced exactly; evidence, not closure, since S18 is still committing]` **→ SATISFIED, and this note is closed** `[supervisor amendment 07-31 · micro-docs batch §10 MD-8]`: the S18 lane closed at **`ee6990c`**, and the qualifying unscoped sweep was taken **after** it at **`e8e2895`** — **33/33, R-4 + R-6 PASS**, scene04 **1335 prims / `d530f155`**, scene18 **979 / `cc26fd97`** (`w3_s10_close_v1.md` §0; re-run independently at `535926e`, `redteam_lane1.md` §7). Re-verified live at `a7842bc` for this amendment: scene04 **1335 / `d530f155`**, R-4 1/1 · R-6 1/1 — the landed figure reproduces to the digit; (b) `look_check/scene04/260731_w3_s04/round_stamp.json` carries `git_head 0711973` and the matching PT env but **no `baseline_of_record` marker** (the F5 class the red team raised against `260731_w3_s07`) — the status lives in this ledger row alone | 2026-07-31 |
| GT-23 | S2 | CB-S16 | `f831d61` | `python3 -m py_compile scenes/main/scene16_canopy_shadow.py` · `NEGOBS_SMOKE=1 python scenes/main/scene16_canopy_shadow.py` · `python3 scripts/geom_invariance_check.py --scenes scene16` · `python3 scripts/geom_invariance_check.py` (32 of 33) · `python3 scripts/placement_lint.py --scenes scene16` · `python3 scripts/const_color_audit.py` · `python3 scripts/regression_check.py` (baseline → pilot, `Docs/reports/regr_260731_w3_s16.json`) · `python3 scripts/near_ground_stats.py` (h0.3 ×3) · `python3 scripts/stamp_round.py look_check/scene16/260731_w3_s16 …`. Pilot round rendered GPU-exclusive under `flock -w 7200 /tmp/negobs_gpu.lock` (63 s), **13 cuts in full `grid_views` order** — the order-prefix rule satisfied by rendering the same 13 the baseline holds, arm identical on both `round_stamp.json`s (`pt · PT_FAST · LOOK_V1 · DETAIL_SCALE 2 · ROUGH_GAIN 0`) | **Baseline named per §6-W4: `260730_w2d_fix`**, and the apparent conflict with §1/§6-W4 is resolved rather than ignored — **scene16 was not in CB-2's pilot set** (03 · 07 · C2 · 01), so **no `260731_w3_cb2` round exists for it**; GT-8 retires the library-wide comparison **JSON** `regr_260730_w2d_fix.json`, not scene16's own round directory, and per `look_check/README.md` §2 the scene's latest judgement round in its scene root **is** its baseline-of-record. Verified on disk: `look_check/scene16/` holds `260730_w2d_fix`, `260730_w2d_judge`, `260731_w3_s16` and pre-W2 rounds only, and the JSON's own `pairs` block reads `before: look_check/scene16/260730_w2d_fix → after: look_check/scene16/260731_w3_s16`. **`260731_w3_s16` is scene16's baseline-of-record from here.** **R-3** — 13 cuts, **FAIL 0 · WARN 5 · INFO 1 · PASS 7** (counted from the JSON, matching report §7.1). **DARK / BLOWN clean, no new firing**; `under_canopy` INFO is a **carried** defect (baseline 52.7 mean / 40.7 % dark → 48.6 / 51.1 %, i.e. −4.1 and +10.4 pp, both inside the PHOTO WARN band −20/+12 — a street canyon takes sky from a cut that already lives on indirect light). **OCCL clean: 0.0 % newdark and 0.0 % blob on all 13** (round 1 peaked at 4.7 / 1.9). The 5 WARNs are **FRAME**, 10–28 % block shift, every one below the 40 % FAIL line and mostly at or under the 20 % WARN line — the declared backdrop-plus-band composition change, measured after tone normalisation. **R-1 / R-2 not owed** — class A: no hazard box, no drop edge, no walked surface moved. **GT-E1′ and GT-E2 were nevertheless run** by registering the site in a dry `plan_ground` (the band is scene-side, so B6/B7/B9/B11 would never have seen it): clearance **0.300 ≥ 0.240 PASS**, B7 **0 violations** with `singular = 1` at every cut. **Floor**: py_compile ✔ · SMOKE prims 631 · rc 0 · geom_invariance **R-4 1/1 · R-6 1/1**, prims **439**, hash `4233f62d` · placement_lint **ERROR 0 · WARN 8 · BLOCK 1, identical to pre-edit** · const_color_audit 137 wirings · 0 violations. **Not hidden**: the tree-wide `geom_invariance_check` ran **32 of 33** — it aborted at `scene04` (`KeyError: 'hedge'`, another lane's uncommitted in-flight file at the time). scene04 has since landed as **GT-22**, whose own floor run then aborted at `scene18`; ~~the 33/33 sweep is owed to whoever closes the S18 lane~~, and it is owed once for both rows `[batch §9-7: re-run unscoped at the ledger-batch HEAD — **33/33 PASS**, scene16 prims 439 hash `4233f62d` reproduced exactly; evidence, not closure]` **→ SATISFIED, and this note is closed** `[supervisor amendment 07-31 · micro-docs batch §10 MD-8]`: the S18 lane closed at **`ee6990c`** (its last commit; the supervisor adjudication of `w3_s18_v1.md`), and the qualifying unscoped sweep was taken **after** it at **`e8e2895`** — `python3 scripts/geom_invariance_check.py` **unscoped 33/33, R-4 + R-6 PASS**, `scene18` assembling at **979 prims / `cc26fd97`** (`w3_s10_close_v1.md` §0; independently re-run at `535926e` by `redteam_lane1.md` §7). Re-verified live at `a7842bc` for this amendment: **scene16 439 prims**, R-4 1/1 · R-6 1/1. **One honest qualifier**: scene16's hash at and after `1a6be6b` reads **`a9d922f5`**, not the `4233f62d` this record landed with, because K1's micro-commit moved the tactile band's path `Tactile_StairHead/Base → GKit/Tactile_stair_top/Base`; the A/B is **438 of 439 rows byte-identical and the path-normalised hashes are EQUAL** (`redteam_lane1.md` §4), so the geometry is unmoved and only the prim path changed. The round stamp carries `git_head f831d61` but **no `baseline_of_record` marker** (F5 class, still open). **Queued, not done** (report §7 adjudication): the `TACTILE_SITES`/`EXPECTED_FP` registry move → **Lane-1 K1 micro-item**; the §12.6 quadrant re-count → **Lane 4**; scene16 leaves the tactile-ablation set | 2026-07-31 |
| GT-24 | K1 (`ground_kit.py` · `GROUND_PROFILES`) **+ SB (the `levee_paved` extension)** | micro pilots ~~**01 · 16 · 09**~~ → **01 · 02** (16 · 09 kept as the recorded nulls) **+ 17** for the extension `[§11 SB-1]` | `8b6baa7` (sweep) **+ `f39abe0`** (extension, one tuple), declared at §10 MD-7 and **`5e87681`** respectively | **Two landings, one row.** *(A)* **The three-profile sweep, MB lane.** `python3 -m py_compile ground_kit.py` · `python3 ground_kit.py` · `python3 scripts/geom_invariance_check.py` (unscoped) · `python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml` (**both** arms) · `NEGOBS_SMOKE=1 python scenes/<sub>/<scene>.py` ×12 · pilot rounds under `flock -w 7200 /tmp/negobs_gpu.lock` with `NEGOBS_VIEWS=preset_h0.3_d{2,5,10},preset_h0.9_d{2,5}` and the standard judge arm (`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`), then `python3 scripts/stamp_round.py look_check/<scene>/260731_w3_mb24 260731_w3_mb24 <scene>` and `python3 scripts/regression_check.py --before look_check/<scene>/<baseline> --after look_check/<scene>/260731_w3_mb24 --json look_check/<scene>/260731_w3_mb24/regr_vs_<baseline>.json`. Structural numbers were taken in **isolated `git archive` arms**, never in the shared worktree (MB-F3). *(B)* **The `levee_paved` extension, SB closure batch.** Same floor, re-run for this tuple: `python3 -m py_compile ground_kit.py` · `python3 ground_kit.py` · `python3 scripts/geom_invariance_check.py` (unscoped, **in both isolated arms**) + `--scenes scene17,scene03` in the worktree · `python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml` (both arms) · `NEGOBS_SMOKE=1 python3 scenes/main/scene17_ramp_pair_hangang.py`. Pilot 17, three rounds under `flock -w 7200 /tmp/negobs_gpu.lock`, arm `NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0 · NEGOBS_VIEWS=preset_h0.3_d{2,5,10},preset_h0.9_d{2,5}`: **`260731_w3_sb17_pre`** (HEAD `8bf7882`, clean tree, PRE-tuple) → **`260731_w3_sb17`** (HEAD `f39abe0`, POST-tuple) → **`260731_w3_sb17_noise`** under `look_check/_experiments/twins/scene17/` (same HEAD as POST, re-render, the noise floor); each `python3 scripts/stamp_round.py <dir> <round> scene17`; then `python3 scripts/regression_check.py --before look_check/scene17/260731_w3_sb17_pre --after look_check/scene17/260731_w3_sb17 --json look_check/scene17/260731_w3_sb17/regr_attrib.json` and the §6-W4 arm `--before look_check/scene17/260730_w2d_fix --after look_check/scene17/260731_w3_sb17 --json .../regr_vs_260730_w2d_fix.json`, plus `python3 scripts/near_ground_stats.py 'look_check/scene17/260731_w3_sb17{,_pre}/pt_noon_preset_h0.3_*.png' --gate`. **Regression JSONs are written into the round directories** (gitignored) on the MB precedent, because `Docs/reports/regr_*.json` is outside this batch's pathspec — stated, not hidden. | **(A) The three-profile sweep.** `plaza_granite` ~~`("patch", 1)`~~ · `plaza_water` ~~`("patch", 2)`~~ · `sidewalk_block` ~~`("patch", 2)`~~ — all three rows deleted. `python3 ground_kit.py` **60/60 gates OK, 0 FAIL**, incl. the new *"GT-24 단위포장 3종 patch 행 0"* gate; 33-scene dry run 33/33 hard gates, apply round-trip 33/33, kit-plan prim total **1170 → 1149**. **Per-scene delta over the amended scope of 11, not the 15 §3 first declared** (the §3 cell now carries the amendment): one removed `patch` element = one removed prim each — **scene01 354→353 · scene05 1235→1234 · scene14 860→859 · scene20 481→480 · scene21 527→526 · sceneC1 367→366 · sceneN1 529→528 · sceneN3 666→665** (−1) · **scene02 545→543 · sceneC4 638→636 · sceneN5 1073→1071** (−2). Library **31,171 → 31,157 (−14)**; isolated-arm A/B over all 33 scenes **14 rows removed, 0 added, 0 modified**, every removed row a `Cube` at `…/GKit/Patch/Patch_n`. Unchanged and verified so: scene09 `840928aa` · scene16 `a9d922f5` · scene18 `cc26fd97` · sceneC2 `a6a170a6`. `placement_lint` **verdict delta 0** (ERROR 30 · WARN 337 · BLOCK 29 · INFO 2 on both arms, per-check rows identical); only the per-scene inventory moves. Floor: py_compile OK · SMOKE 12/12 rc 0 (scene01 has no SMOKE harness — covered by the A/B arm and its GPU pilot) · `geom_invariance_check` **R-5 ✔ · R-4 33/33 · R-6 33/33 PASS**. **R-3 rounds, named per §6-W4** — new round `260731_w3_mb24` (5 cuts, judge arm) per scene: **scene01** vs `260731_w3_cb2` **PASS 5/5** · **scene16** vs `260731_w3_s16` PASS 5/5 (**pixel-null by construction**) · **scene09** vs `260731_w3_cb1` PASS 3 / INFO 1 / WARN 1 `UNCHANGED` (**pixel-null by construction**) · **scene02** vs `260731_w3_cb7` PASS 1 / INFO 2 / WARN 2 `UNCHANGED`. Attribution arm `260731_w3_mb24_pre` → `mb24`: scene01 PASS 5/5, new-dark 0.00 %, DARK/BLOWN/WHITE/OCCL clean, **no FRAME finding fired**; scene02's one **GRAZE `[의심]`** adjudicated **NEGATIVE** by crop + geometry (both removed prims are 5.2 m and 7.3 m *behind* the `h0.3_d2` eye) + metric triangulation. **Also landed in the same commit and needing their own reading**: the prepared `relaid` vocabulary (registered, count **0 everywhere**, guarded by a self-check that fails if a profile opts in) and the `TACTILE_OFF_REASON["scene18"]` stale-entry replacement (S18 blocker 3). **(B) The `levee_paved` extension** (`f39abe0`, one tuple, declared at `5e87681`). `("patch", 4)` → row deleted. `python3 ground_kit.py` **60/60 OK, 0 FAIL** on both arms — **and this is the one honest gap in the record**: the `_selfcheck` gate reads `_gt24 = ("plaza_granite", "plaza_water", "sidewalk_block")`, so it does **not** cover the fourth profile and a regression that restored `("patch", n)` on `levee_paved` would pass; one line, owed to Lane-1 / `ground_kit`, recorded at §11-2. Dry-run kit-plan prim total **1149 → 1141 (−8)**; the **real library moves −4**, and the 4-prim gap is **scene03's drifted `SCENE_PLANS` fixture** — §7 **W9**, the same MB-F2 class, measured rather than inferred. **Per-scene delta: exactly one scene moves.** **scene17 974 → 970 prims**, hash `5d073f07` → `7092d409`; field-level A/B of the full 974-row inventory: **4 rows removed, 0 added, 0 modified**, all four `Cube` at `/World/Scene17/GKit/Patch/Patch_{0..3}` with `S=(0.5·0.35·0.015)`/`(0.35·0.45·0.015)` at `T.z = −0.007`. **scene03 is unchanged and verified so: 1552 prims / `d6dde846`, `patch=8` still in its inventory** — it authors its own `surface` row, exactly as the amended §3 scope cell predicted **before** the tuple landed. Library **31,157 → 31,153 (−4)**. `geom_invariance_check` **unscoped R-5 ✔ · R-4 33/33 · R-6 33/33 PASS on both arms**, and the per-scene table diff between the arms is **one line long** (scene17); re-run scoped in the worktree it reproduces to the digit. `placement_lint --scenes all` **verdict delta 0** (ERROR 30 · WARN 337 · BLOCK 29 · INFO 2, unchanged), the **only** text delta being scene17's inventory `prims=974 … patch=4` → `prims=970 …` with `patch=` absent. `NEGOBS_SMOKE=1 scene17` rc 0 and **byte-identical output** across the arms. **R-3, pilot 17.** Attribution `260731_w3_sb17_pre → 260731_w3_sb17`: **FAIL 0 · WARN 0 · INFO 0 · PASS 5**, *"회귀 없음"* — new-dark **0.0 %** and largest blob **0.0 %** on all 5, DARK / BLOWN / WHITE / GRAZE do not fire anywhere. Against the §6-W4 baseline-of-record **`260730_w2d_fix`** the 5 rendered cuts are **PASS 5/5**; the other 9 report `[MISSING]` because this round did not render them — **a declared scope, not a regression**, and the reason `260731_w3_sb17` is **deliberately NOT promoted to baseline-of-record** (a 5-cut round would drop 9 cuts from every later comparison; both stamps and `look_check/README.md` §4 say so, and **scene17 stays on `260730_w2d_fix`**). **The PASS is not a null result, and it was proved not to be**: a same-HEAD re-render (`260731_w3_sb17_noise`, under `_experiments/twins/`) puts the PT_FAST noise floor at **≤ 0.001 % of pixels beyond 16 LSB** on every cut (max deviation 15–26 LSB), while the pre→post signal is **7.274 % (h0.3_d2) · 0.914 % (h0.3_d10) · 0.462 % (h0.9_d5) · 0.053 % (h0.3_d5)** beyond 16 LSB with peaks of **160 / 137 / 77 / 74 LSB** — four cuts carry a real, above-noise change and `h0.9_d2` is genuinely null (0.000 %). So the four deleted rectangles were visible, they are gone, and **no channel that matters moved**: the tool PASSes because a dark asphalt cut patch was replaced by the interlocking paving around it, inside the same luminance band. Pixel evidence committed: `Docs/reports/_w3_sb_crops/scene17_preset_h0.3_d{2,10}_ab.png` — at d10 the BEFORE frame shows a **dark rectangle sitting on the light 인터로킹 promenade** and the AFTER frame does not, which *is* the user's *"이상한 사각형 무늬"*; at d2 the BEFORE frame carries the hard straight saw-cut line across the near ground and the AFTER frame does not. `near_ground_stats` h0.3 triple, pre → post: `sd` 26.3 → 27.3 · 22.2 → 22.2 · 48.6 → 48.6, `edge` 100.5 → 108.6, `flat_gnd` 2.3 → 2.2 · 0.0 → 0.1 · 30.6 → 30.6 — **no new gate flag fires and none is cured**; the pre-existing `sd < 32` / `σ_LF < 5` (d2 · d10) and `flat% ≥ 8` / `flat_gnd ≥ 3` (d5) flags are present identically before and after, recorded and not tuned away. **R-1 / R-2 not owed** on either landing — the row's declared class: no walked surface, no hazard box, no drop edge moves; `patch_proud = 0.002 m` is an order below `GT_DELTA = 0.020`. **Concurrency, stated**: `260731_w3_sb17_pre` was rendered at `dirty_files 0`; `260731_w3_sb17` at `dirty_files 2` (`urban_kit.py` modified, `assets/urban_wrap/` untracked — another lane's MD-F2 wrapper work that appeared mid-batch). Neither can reach these pixels: `urban_kit` has **0 references** in `scene17_ramp_pair_hangang.py` and **0** in `scene_common.py`. The paths are on the stamp, per the S10c `dirty_paths` convention. | 2026-07-31 |
| GT-25 | S2 (`main/scene02_underpass.py`) | micro pilot **02** (`beauty_overview`) | `5340d49` | **R-1 / R-2 not owed** — the row's declared class (no walked surface, no hazard box, no drop edge moves). **Floor** (§6.1), all four run in **isolated `git archive` arms**, not the shared worktree (MD-F1): `python3 -m py_compile scenes/main/scene02_underpass.py` · `NEGOBS_SMOKE=1 python3 scenes/main/scene02_underpass.py` (the 48-gate `underpass_selfcheck`) · `python3 scripts/geom_invariance_check.py --scenes scene02` · `python3 scripts/placement_lint.py --scenes scene02`. **R-3**: two 13-cut rounds under `flock -w 7200 /tmp/negobs_gpu.lock`, arm byte-identical to the baseline's own stamp (`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`, no `NEGOBS_VIEWS` filter) — **`260731_w3_gt25_pre`** (arm `e1150d6` exactly, PRE-move, the attribution arm) and **`260731_w3_gt25`** (the same arm with `scene02_underpass.py` replaced by the landed file, verified `diff -q` byte-identical to `5340d49:scenes/main/scene02_underpass.py`); then `python3 scripts/regression_check.py --before look_check/scene02/260731_w3_cb7 --after look_check/scene02/260731_w3_gt25 --json Docs/reports/regr_260731_w3_gt25.json`, and the same call with `--before …/260731_w3_gt25_pre` for the attribution. | **Landed coordinate `(−11.0, −5.0)`, NOT the declared `(−11.0, −6.2)` — the deviation was declared in advance by the phase-Code report and by `scene02:432`'s own comment, not discovered in a diff**; §3 is amended to the landed value by this batch `[§11 SB-2]`, so §3 and §4 do not contradict each other. At `y = −6.2` the 3.0 × 3.0 m bed interpenetrates the hedge band (`scene02:285`, whose comment records that it was moved to `y = −7.0` *"avoiding the planter"*): measured `Hedge_0` **2.350 × 0.683 × 1.060 m** and `Hedge_1` **0.885 × 0.660 × 0.898 m** in an isolated fake-USD arm over four candidates. At `y = −5.0` the overlap set is byte-identical to HEAD's (ground plates only) and eye→centre is **4.000 m** against the row's re-derived 4.176 m — a 0.176 m shortfall on the figure the row itself excludes from its target; eye→bed-edge is 2.450 m either way. **The hedge was NOT notched or shortened** and **the second planter `(−13.0, 5.5)` is untouched**. **R-3** — `260731_w3_cb7 → 260731_w3_gt25`, 13 cuts: **FAIL 1 · WARN 0 · INFO 0 · PASS 12** (`Docs/reports/regr_260731_w3_gt25.json`). The single FAIL is `beauty_overview` **[FRAME]** moved-block **90 %** + **[PHOTO]** mean **87.5 → 146.2 (+58.7)** — the declared composition change on the one cut the row exists for, recovering C02-P1's **PHOTO −57.5** in full. **OCCL new-dark 0.0 % · largest blob 0.0 % on all 13 cuts** where C02-P1 measured **32.8 %** and **19.7 %** — the occlusion defect is **gone, not reduced**; DARK, BLOWN and WHITE do not fire anywhere. **Attribution**: `260731_w3_cb7 → 260731_w3_gt25_pre` is **FAIL 0 · WARN 0 · INFO 1 · PASS 12**, worst per-cut \|Δmean\| **0.31 LSB** — the committed baseline reproduces on this machine today, so the whole delta is attributable to one line. **Containment**: the two judged eyes nearest in plan to the vacated and the new footprint are null — `preset_h0.3_d10` Δmean **−0.02 LSB**, `preset_h1.8_d10` **−0.00 LSB**, **0.0 %** of pixels beyond 16 LSB on both; the attribution run raises `[UNCHANGED]` WARNs on nine other cuts, which here **is** the containment proof. **Floor**: py_compile ✔ · `NEGOBS_SMOKE=1` **48/48 gates `[OK ]`, 0 failures, rc 0** (`[SELFCHECK] scene02 CB-7 — PASS`) · `geom_invariance --scenes scene02` **R-4 1/1 · R-6 1/1 PASS**, prims **545 unchanged**, hash `a4c3a5f9 → cceee473` — an element AABB move, **exactly the class §3 declares** · `placement_lint --scenes scene02` **ERROR 4 · WARN 9 · BLOCK 1, identical to the HEAD arm** down to the inventory string; the 4 ERRORs are the pre-existing LINT-6 bollard set (CB-7 §8.2), untouched. **Baselines-of-record, closed rather than left ambiguous**: `260731_w3_gt25` is scene02's baseline-of-record from here and its stamp says so, and **`260731_w3_cb7`'s stamp now carries `baseline_of_record: false` + `superseded_by: 260731_w3_gt25`** — the MD-F5 item, closed by this batch on the S10c precedent `[§11 SB-3]`, keys only, nothing re-rendered. `look_check/README.md` §4's `--before-round` chain resolves scene02 to `260731_w3_gt25` `[§11 SB-4]`. **One measurement this record does not hide** (MD-F1): assembled against the *dirty* worktree of that session scene02 is **543 prims / `8ac2fa99`**, against the clean HEAD arm **545 / `a4c3a5f9`** — the difference is the two `sidewalk_block` patches GT-24 deletes, which is why every number above comes from an isolated arm. | 2026-07-31 |
| GT-26 | S6 (`main/scene18_wavy_artstair.py`) | CB-S18 · GATE-1 pilot **18** *(CB id assigned by this batch on the `CB-S04` / `CB-S16` precedent — stated, not silently done)* | `a443d5a` (+ supervisor adjudication `ee6990c`) | **R-1** `NEGOBS_SMOKE=1 NEGOBS_LOOK_V1=1 python scenes/main/scene18_wavy_artstair.py` (the new `_stair_selfcheck`, which replaces the deleted `_wave_selfcheck`) · **R-2** `python3 scripts/run_data_render.py --run 260731_data_s18 --scenes scene18 --conds L0,L7,L5 --cams 8 --seed 20260731` then `python3 scripts/check_data_run.py 260731_data_s18` · **R-3** pilot round `260731_w3_s18` rendered GPU-exclusive under `flock -w 7200 /tmp/negobs_gpu.lock`, channel identical to the frozen judge round (`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`), **14 cuts in full `grid_views` order**, `scripts/stamp_round.py`, then `python3 scripts/regression_check.py --before look_check/scene18/260730_w2d_fix --after look_check/scene18/260731_w3_s18 --json Docs/reports/regr_260731_w3_s18.json` · **Floor** (§6.1): `python3 -m py_compile scenes/main/scene18_wavy_artstair.py` · SMOKE · `python3 scripts/geom_invariance_check.py --scenes scene18` · `python3 scripts/placement_lint.py --scenes scene18` | **Baseline named per §6-W4: `260730_w2d_fix`** — scene18 was not in CB-2's pilot set (03 · 07 · C2 · 01), so no `260731_w3_cb2` round exists for it and per `look_check/README.md` §2 the scene's latest judgement round in its scene root is its baseline-of-record (the **GT-23 reasoning, applied again**). **`260731_w3_s18` is scene18's baseline-of-record from here**, superseding `regr_260730_w2d_fix.json` for this scene. **R-1** — `_stair_selfcheck` re-derives and prints the registry: ① total drop **2.560 m = 16 × 0.160**, invariant `\|Δ\| < 1e-9` · ② **2R+T 0.640** (0.600–0.650) · 26.57° · clear width **6.000** · run **5.120** · ③ revetment permanent drop **x = 0.00, y −100…420 minus the y ±3.0 opening = 2.560 m** · ④ first riser **0.160**, landing error **+0.000000 m** · ⑤ stringer kerb top **+0.120** (guard test: 11 % of 1.100 → **not a guard**) · ⑥ foreshore **2.6 % ramp, not a step**; derived waterline **x = 42.462** · ⑦ cue state 난간 False · 계단머리 경고블록 False · 논슬립 False · ⑧ nosing z ladder −0.16 … −2.56. **R-2 PASS** — `run_data_render` 24 cuts, exit 0, **2.77 s/cut**; `check_data_run 260731_data_s18` → **DATA RUN CHECK PASS**. *This is the check that found a real defect and nothing else would have*: the first attempt failed `ground found under every camera — 0/24` because `variation_kit._Stage1Index` (`variation_kit.py:754`) drops any prim whose largest AABB dimension exceeds 400 m, and §2.1's 520–625 m ground plates were therefore invisible to the camera validator. Fixed by tiling the long plates under a named constant **`AABB_TILE_MAX = 380.0`** (10 mm tile overlap); re-run **24/24 ground found, worst \|err\| 0.0000 m, buried 0, closed_in 0, offground 0, nearest solid 0.324 m**. **R-3** — 14 cuts, 43.0 s: **FRAME 13 FAIL + 1 WARN — the DECLARED result** (a full archetype swap moves every block; the tool says so itself). Channels that still mean something: **DARK clean** (frame means rose 105→135 … 152→183, the §3 sun fix) · **BLOWN clean** · **WHITE clean** (and it was not clean before the last pass — a fully sunlit promenade at `granite_tint 0.74` pushed `preset_h0.3_d2` pure-white to **50.8 %**, a v5.1 §4 violation; the required linear factor (0.78/0.85)^2.2 = 0.826 → tint **0.58**, which is also the more faithful value for a 화강석 판석 promenade) · **OCCL one cut** (`color_front`, new dark 4.3 %, largest blob 1.0 %, near-field band 0.3 % — that new dark **is** the hazard: the self-shadowed revetment face and the 16 risers seen from the sand; no camera burial, `check_data_run` independently measured nearest solid 0.324 m) · **GRAZE 3 `[의심]`** on the h0.3 cuts, which the tool declares cannot be auto-confirmed, **adjudicated by crop** (`crops/graze_edge_preset_h0.3_d{2,5,10}.png`): the new line is the **dark granite coping over bright sand — the drop edge reading as it should**. scene18's concealment axis was the mural camouflage and §7 ruling 3 retired it, so a visible drop edge is the intent, not a defect. `near_ground_stats` h0.3: d5/d10 improve on nearly every metric (`wht %` 47.7 → 20.8 and 53.5 → 21.4, `>224 %` collapses 1.78 → 0.05 and 2.16 → 0.07, `flat_gnd` holds); **d2 regresses on `wht %` 19.2 → 33.3** — the direct price of the sun fix that removed the DARK problem, **stated rather than chased**. **Floor**: py_compile OK · SMOKE `SMOKE_OK prims=688` (교목 24 · 관목 112) · geom_invariance **R-5 ✔ · R-4 1/1 · R-6 1/1**, hash `18dd6520` identical on all 3 arms · placement_lint **0 ERROR · 0 WARN · 1 BLOCK** against a v6 (`386fc88`) baseline of 1 ERROR / 7 WARN / 1 BLOCK — the LINT-4b `White_Pine` ERROR is **fixed**, not suppressed, and the surviving BLOCK is the pre-existing evidence-gated LINT-9 (`blocked_on: P-7`), identical before and after. Two rules bit immediately on the scene's new `PLACEMENT` block and were fixed **by moving geometry, not by editing the declaration**: LINT-2 (routes re-declared one-per-bed, bed length derived from the pitch — 15.600 m with 0.800 m end margins holds exactly 3 trees at 7.000 m) and LINT-5 (10 ERRORs on the promenade lanterns; poles moved x −13.95 → **−15.60** so the pole centre sits ≥ 2.000 m back, and `walk_edges` extended to the full plate extent because a short polyline silently exempted 2 of the 12 lanterns). **Two facts this record does not hide.** (a) **The scene18 prim hash is `18dd6520` at landing and `cc26fd97` from `e4d9cf9` onward** — K4(b)'s species pinning moved **159 inventory rows** in this scene through the shared library (yaw/height re-draws + shrub seating z; `w3_k4_v1.md` **K4-F2**, `redteam_lane1.md` **RT-3**). Species sets and every walked surface are untouched and the total drop still asserts at 2.560 m; re-verified live at `a7842bc` for this record: **scene18 979 prims / `cc26fd97`, R-4 1/1 · R-6 1/1 PASS**. (b) `look_check/scene18/260731_w3_s18/round_stamp.json` carries no `baseline_of_record` marker — the **F5** class the red team raised against `260731_w3_s07`; the status lives in this row alone until the stamp convention is applied uniformly. **Owed to other lanes, recorded not actioned** (`w3_s18_v1.md` §9): `ground_kit.TACTILE_OFF_REASON["scene18"]` still reads *"18 = wave-form, irregular"* — **that reason died with the wave**, and the entry is stale (Lane-1 / `ground_kit` owner); the scene-side guide strip uses the library's only tactile texture, which is **점형 (warning)** where G18 shows **선형 (guide)** — built at the correct 0.300 m width and kept **12.20 m clear of the drop edge** so no reader can take it for a stair-head cue (K4/K5); `scene_common.TEX` has no `beach_sand` role (the scene binds absolute paths); K5 `build_curb_line` for the bed kerb, deferred by the dispatch note. **R18-2 procurement returned NEGATIVE** and was adjudicated **ACCEPTED as shipped** (juniper + oak) at `ee6990c` — all three licensed sources returned negative for palm / umbrella pine, the pines-only fallback is retired by the yaml, and the coastal read is carried by sand / surf / revetment / backdrop; the open procurement row stands, adopt a palm **only** if a doctrine-clean CC0/KOGL source surfaces | 2026-07-31 |
| GT-33 | S4 | CB-9 | declared `e8f2053`, landed `1234a51` (+ `5cf0315`) | *(rides GT-5's commands above)* | *(rides GT-5's single re-cache — same scene, same batch, §0-2)*. What this row itself put on the ground `[measured]`: `walk_cross` and `walk_spur` tops **0.007 → 0.150**; `Walk_CrossN1` / `Walk_CrossS1` replaced by `WalkRamp_N` (run 3.00 m, **4.9 %**) and `WalkRamp_S` (run 3.20 m, **4.6 %**), authored under `sc.build_rot_group` because `build_slope` only falls along +X; `WalkRamp_Spur` (run 2.00 m, **7.5 %**) with `walk_spur.x1` 13.4 → **14.4** to carry it (at the original 1.0 m the spur approach would have been **15 %**). All three are `kind='grade'` rows in the R-1 registry, never `drop`. The **146 mm step at the carriageway edge is removed, not created** — the whole reason the row exists. Bollard rows re-seated 0.000 → **+0.011** onto the crossing ramp so they keep 0.90 m exposure. The plate underside now tracks `proud` (`thickness = proud + 0.12`): at the old fixed 0.12 a 0.150-proud plate would have floated **30 mm clear of the ground plate**. Six 150 mm plate edges are left **undressed on purpose** (walk ends x −14 / +30, crossing far ends y ±16) and are listed explicitly in the R-1 registry rather than hidden — they are plates ending at the model limit | 2026-07-30 |
| GT-36 | S11 (`main/scene11_footbridge_stairs.py`) | CB-S11 · GATE-1 pilot **11** | `f05efb5` (rebuild) + `e9d7a50` (mesh re-site) + `afc28f2` (sun adjudication); declared **before** any of them at `bf79549` | **R-1** `NEGOBS_SMOKE=1 python3 scenes/main/scene11_footbridge_stairs.py` — the scene's own boot-free self-check, extended for the H-plan: it re-derives both tower footprints from `PARAMS` and asserts long-axis-along-the-carriageway, on-footway, no-carriageway-intrusion, R11-1 asymmetry, the 10-row walking-continuity table, the 5.500 m per-tower invariant, both `rot_group` placements node-by-node, grid d=2/5/10 standing on structure, corridor intrusion 0, the front profile and the h0.3 concealment arithmetic · **R-2 / R-3** pilot round `260731_w3_s11` under `flock -w 7200 /tmp/negobs_gpu.lock`: `NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 NEGOBS_CAPTURE_DIR=look_check/scene11/260731_w3_s11 python scenes/main/scene11_footbridge_stairs.py` (15 cuts, 56 s) → `python3 scripts/regression_check.py --before look_check/scene11/260730_w2d_fix --after look_check/scene11/260731_w3_s11 --json Docs/reports/regr_260731_w3_s11.json` → `python3 scripts/near_ground_stats.py "look_check/scene11/260731_w3_s11/pt_noon_preset_h0.3_*.png" --json Docs/reports/_w3_s11_ngs.json` → `python3 scripts/stamp_round.py look_check/scene11/260731_w3_s11 260731_w3_s11 scene11` · **floor (§6.1)** `py_compile` · `geom_invariance_check.py --scenes scene11` · `placement_lint.py --scenes scene11` · `const_color_audit.py`, and the tree-wide arm in an **isolated `git archive` worktree** (8 lanes share this one) | **Invariant proved, not asserted**: total drop **5.500 m** per tower (44 × 0.125), deck `z_top` **5.500**, roadway clearance **5.25 m** — all three re-derived by R-1 after the rebuild and unchanged. **Grid origin unmoved**: the 9 preset `eye`/`tgt` triples are byte-identical between the baseline and the pilot `manifest.json`, so no judge preset was edited to make the H-plan legible. Prim census **2222 → 3788**, geom hash `2f6121eb → dfa8409a`, `geom_invariance_check` **33/33** R-4 and R-6 in the isolated arm. `build_curb_line` returned, per side: 55 blocks, exposure 0.150, `face_h_at_kerb` / `gt_drop` **0.168**, 81 prims (0.68/m) — **sub-threshold step, not a drop** (0.168 < 0.30). `placement_lint` bollard-height **ERROR 4 → 0** (0.750 → 0.850, 교통약자법 시행규칙 별표2 제7호); WARN 19 and BLOCKED 1 unchanged. Regression vs `260730_w2d_fix`: **14 FAIL, every one carrying FRAME**, which is the expected verdict for a plan-level rebuild; PHOTO moved **brighter on 13 of 14** and dark collapsed (`under_grating` 68.3 % → **0.2 %**, h0.3_d10 9.9 % → **0.6 %**); the 3 GRAZE items came back as the tool's own **INFO / 판정 유보**, so no `EXPECTED_FP` citation was needed. **Two pilot-driven corrections are recorded rather than hidden**: the first pilot put the G11 mesh panel on the head landing's outer face and it filled h1.8_d2 (mean 122.6 → 76.2, dark +34.3 pp) → moved into the stair plane (`e9d7a50`); and the brief-R6-conforming `SUN_AZ_OFFSET` 56.5 was built, measured over a 3-arm probe (`look_check/_experiments/gates/scene11/260731_sunaz_*`) and **rejected** at −62 mean / +47 pp dark on h1.8_d2 → 171.5 kept and the broken rule declared (`afc28f2`, report §8). New **baseline-of-record** `look_check/scene11/260731_w3_s11`, stamped with `baseline_of_record` · `supersedes_baseline_of_record: 260730_w2d_fix` · `dirty_paths`. Report: `Docs/reports/w3_s11_v1.md` | 2026-07-30 |
| GT-27 | S17 (`main/scene17_ramp_pair_hangang.py`) | CB-S17 · GATE-1 pilot **17** | `25f366c` (declared before the geometry at `884d24c`, per §0-1) | **R-1** `NEGOBS_SMOKE=1 python3 scenes/main/scene17_ramp_pair_hangang.py` — the scene's **new `hazard_registry()`**, boot-free and GPU-free, re-derives every drop / up_step / grade row from `PARAMS` (`slope_z`, `ramp_geom`, the stair ladder) and the smoke prints it, together with the new `_frame_metric()` R17-1 acceptance test and the F5 derivation · **R-2** `flock -w 7200 /tmp/negobs_gpu.lock` → `python3 scripts/run_data_render.py --run 260731_data_s17 --scenes scene17` then `python3 scripts/check_data_run.py 260731_data_s17` · **R-3** `flock -w 7200 /tmp/negobs_gpu.lock bash <scratch>/s17_run_round.sh` — two 14-cut PT rounds from **isolated `git archive` arms** (`assets/`+`look_check/` symlinked), arm byte-identical to the frozen judge channel (`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`, `NEGOBS_VIEWS` **unset** = full order prefix): **`260731_w3_s17_pre`** @ `884d24c` → **`260731_w3_s17`** @ `25f366c`, each `python3 scripts/stamp_round.py <dir> <round> scene17`; then a third round **`260731_w3_s17_noise`** (same arm, same sha) under `look_check/_experiments/twins/scene17/` as the noise floor; then `python3 scripts/regression_check.py` three times — `--before …_pre --after …s17 --json …/regr_attrib.json`, the §6-W4 arm `--before …260730_w2d_fix --after …s17 --json …/regr_vs_260730_w2d_fix.json`, and the inherited-window arm `--before …260730_w2d_fix --after …_pre --json …_pre/regr_inherited.json`; plus `python3 scripts/near_ground_stats.py 'look_check/scene17/260731_w3_s17{,_pre}/pt_noon_preset_h0.3_*.png' --gate`. **Floor per commit (§6.1)**: `python3 -m py_compile` · `NEGOBS_SMOKE=1` rc 0 · `python3 scripts/geom_invariance_check.py --scenes scene17` · `python3 scripts/placement_lint.py --scenes scene17 --rules Docs/briefs/placement_rules_v1.yaml`; **all structural numbers taken in isolated arms** (eight lanes share this worktree and `ground_kit.py` was dirty in it). | **Comparison baseline named per §6-W4: `260730_w2d_fix`** (14 cuts); **`260731_w3_s17` is stamped `baseline_of_record: true`** and `260730_w2d_fix` carries `superseded_by`. **R-1 registry**: **22 `drop` · 1 `up_step` · 1 `grade`** — drop edge still `x = 0.00 / 3.200 m`, all 20 nosings 0.160 (sum 3.200), the crest cope emitted as **`up_step`** not a drop (GT-1's rule now a code assertion), the ramp emitted as a **`grade`** row (descends without an edge), and the one drop value that moves is `ramp_river_edge` **1.530 → 1.501 m**. **Geometry, isolated arms with real assets**: HEAD `970 / 7092d409` → **`length` alone** `970 / 04c1a4a6` (**0 prims**, hash moves — the walked surface really moved, which is why this row is FULL and not PROOF-ONLY) → full lane **968 / 186a4907**; `belt=False` variant **968 / b2ea9a7b** (K4(b) confirmed: species swap = 1 prototype, **0** prims). `placement_lint` **ERROR 0 → 0 · WARN 10 → 11 · BLOCK 1 → 1**, the single new row being LINT-4's census `Lombardy_Poplar ×9 · Black_Oak ×3` — the belt flip visible, declared as **S17-F1**. **R-2 `DATA RUN CHECK`**: 8 cuts, **2.13 s/cut** vs SP-3's 2.87; sections **[1] photometric band · [2] azimuth · [3] camera placement · [4] manifest/file · [5] throughput all PASS** (`ground_below == h_rel` worst \|err\| **0.0000 m**, nearest solid to any eye **0.390 m**, 8/8 unique 1920×1080, nothing written under `look_check/`). Its **2 FAILs are the zero-sample cross-condition checks** (`0 pairs >= 0.3 EV apart`, `0 scene-pairs`) needing `--conds` > 1 — the mini-scope artefact GT-14 and GT-18 recorded, not a geometry result. **R-3**: attribution `pre → s17` **FAIL 0 · WARN 0 · EXPECTED_FP 0 · INFO 1 · PASS 13** *(회귀 없음)*; §6-W4 `260730_w2d_fix → s17` **FAIL 0 · WARN 0 · INFO 1 · PASS 13**; and the inherited window `260730_w2d_fix → pre` **FAIL 0 · WARN 0 · PASS 14**, which is what makes the other two attributable — GT-24's `levee_paved` extension and the whole Lane-1 kit window are **regression-null on this scene**. `newdark` / `newdark_blob` **0.0 % everywhere except `toe_lookup` (0.7 % / 0.4 %)**; **DARK · BLOWN · WHITE · OCCL · GRAZE never fire**, and the D14 `EXPECTED_FP` reader matched **0** pre-registered entries. The single INFO is `preset_h0.3_d2 · CAPTURE — manifest ok=false (캡처 폴링 조기 종료)`, a manifest flag, not a pixel one (`d_mean −0.087 LSB`, `newdark 0.0`, and `check_data_run` §[4] independently proves the frames on disk are complete and unique). **The PASS is proved not to be a null**: the same-sha twin `260731_w3_s17_noise` puts the PT_FAST floor at **≤ 0.003 % of pixels beyond 16 LSB** (peak ≤ 41 LSB) on all 14 cuts, while pre→post measures **0.314 %–9.846 %** beyond 16 LSB with peaks **109–214 LSB** (`ramp_run` 9.846 %, the cut that rides the ramp) — 100× to 10,000× the floor. **`near_ground_stats --gate` h0.3 triple, pre → post**: `sd` 24.2→26.1 · 48.6→48.6 · 22.2→22.2, `σ_LF` 1.48→1.47 · 14.97→14.92 · 1.25→1.25, `flat_gnd` 2.3→2.3 · 30.6→30.2 · 0.1→0.1 — **no gate flag newly raised and none cured**; the pre-existing `sd < 32` / `σ_LF < 5` (d2 · d10) and `flat % ≥ 8` / `flat_gnd ≥ 3` (d5) flags are the signature of the designed concealment and are recorded, not tuned away, and the σ_LF movement is two orders under GT-13's declared −0.32 sensitivity. **Stamp provenance corrected by hand and said so**: `stamp_round.py` reads the *repo* HEAD, which another lane had advanced to `ac7a50c` by stamp time, so both stamps now carry the true arm sha in `git_head`, the shared tree in `worktree_head_at_stamp`, `render_arm`, and the S10c `dirty_paths` (`ground_kit.py · scene03 · scene09 · scene11`) — the arms carry the **committed** `ground_kit.py` of their own sha, identical PRE and POST, so the uncommitted edit never reached these pixels (**S17-F6** asks for a `--sha` override). Pixel evidence committed: `Docs/reports/_w3_s17_crops/` (h0.3 triple vs **G3**, `pair_compare` A/B, the three mise-en-scène cuts, and a `260730_w2d_fix ⟷ pre ⟷ post` three-way that separates the inherited patch removal by eye). Full write-up: **`Docs/reports/w3_s17_v1.md`** | 2026-07-31 |
| GT-28 | S17 (`main/scene17_ramp_pair_hangang.py`) | CB-S17 · GATE-1 pilot **17** | `25f366c` | *(rides GT-27's single re-cache — same commands, §0-2)*. The three riders are each measured on their own arm rather than assumed: **(a)** the F5 derivation is re-run boot-free by the smoke and live by `build_ground_kit`, and a CPU probe ran `gk.plan_ground` for scene17 in both configurations; **(b)** the dead `patches` list was A/B'd through `gk.plan_ground` with the list present vs absent; **(c)** the belt flip was isolated as the `belt=False` variant arm | **(a) F5.** `infra_kit.derive_manholes([(−4.15,−30.0),(−4.15,48.0)], d_mm=450)` → **2** chambers, `head` (−4.15, **−30.00**) `s=0.0` and `interval` (−4.15, **+9.00**) `s=39.0` (KDS 61 40 00, Ø ≤ 600 → **75 m**, run **78.0 m**) — **both outside the ground-plan region** (x −7.5…0, y −6…6) ⇒ **0 manholes built**, against the camera-solved `(−2.00, 1.20)` this deletes. `tonglam_v2.md` FIX-5's *"worst single prop"* is gone by derivation, not by hand. The two gullies at (−4.15, ±5.50) are deliberately **not** `junctions` (a 우수받이 joins by 연결관), so no chamber re-enters the near window through the back door. **−2 prims** (cover + frame), one **flush** element AABB removed, `patch_proud`-class — an order under `GT_DELTA` 0.020. **(b)** `plan_ground` A/B, list present vs absent: `patch` **0 in both**, **42 elements / 44 prims in both** — a **measured null**, deleted only because a dormant list of four ground rectangles reads as intent under the user's ban (GT-24's row hands dead site lists to the implementing lane *"to clean or keep, declared either way"* — this lane cleans). **(c)** `belt=True` **968 prims / `186a4907`** vs `belt=False` **968 prims / `b2ea9a7b`** — **0 prim delta, reference-only**, the direct confirmation of K4(b)'s `SetInstanceable(True)` claim and the closure of **K4-F4** for scene17. `placement_lint`'s census now reads `Lombardy_Poplar ×9 · Black_Oak ×3`. `bare=` remains default-**False** at every call site: **G3 pins summer** (§7-8), and G9 is read for terrace form only, never for its autumn — the scene docstring now says so. **Net scene prim delta 970 → 968 (−2), all of it (a).** No walked surface, no drop edge and no hazard box moves, so **R-1 / R-2 are not owed on this row** and its R-3 is GT-27's. | 2026-07-31 |

Owner column derived from spec §4.2/§4.3 file ownership (GT-1..GT-3 → S2 owns `scene02`; GT-4 → S1
owns `scene01`; GT-5 → S4 owns `scene13`; GT-6 → K4 owns the `scene_common` builders and S4 cuts
scene06; GT-7 → S6 owns `scene08`; GT-8/GT-9 → K1 owns `ground_kit`; GT-10 → S5 owns `scene09`;
GT-11 → S1 owns `scene05`; GT-12 → K3 owns `building_kit`; GT-13 → T4 owns the loader that binds
the override, consumed by S3/S4). **Appended 07-31 by the supervisor ledger batch**: GT-22 → **S5**
owns `main/scene04_parktrail.py`; GT-23 → **S2** owns `main/scene16_canopy_shadow.py` (spec §4.3).
**Appended 07-31 by the micro-docs batch** (§10): GT-24 → **K1** owns `ground_kit.py` and therefore
`GROUND_PROFILES` (the GT-8/GT-9 precedent); GT-25 → **S2** owns `main/scene02_underpass.py`;
GT-26 → **S6** owns `main/scene18_wavy_artstair.py` (spec §4.3).
**Appended 07-30 by S4 (scene13 lane)**: GT-33 → **S4** owns `main/scene13_apartment_parking_entry.py` — the same owner as GT-5, which GT-33 rides (spec §4.3).

---
| GT-31 | S03 | — | `e4862aa` (rows declared first at `892f9b3`, §0-1) | **R-1** `NEGOBS_SELFCHECK=1 python3 scenes/main/scene03_riverbank.py` — the scene's own `river_view_selfcheck` (v6, occluder instrument corrected this round) **+ `river_width_selfcheck` (new)**; boot-free, GPU-free. **R-3** `python3 scripts/regression_check.py --before look_check/_experiments/twins/scene03/260731_w3_s03_pre --after look_check/scene03/260731_w3_s03 --json Docs/reports/regr_260731_w3_s03.json`. Floor, in an **isolated `git archive` arm** (8 lanes share this worktree; the live tree cannot answer — `scene11: KeyError: 'z_top'` from another lane's in-flight file): `python3 -m py_compile scenes/main/scene03_riverbank.py` · `python3 scripts/geom_invariance_check.py --scenes scene03` · `python3 scripts/placement_lint.py --scenes scene03`. Pilot: `look_check/scene03/260731_w3_s03` (16 cuts, PT_FAST, `LOOK_V1=1·DETAIL_SCALE=2·DETAIL_ROUGH_GAIN=0`) | **R-1 green — the hazard registry did not move, as the row asserted.** `geom_invariance_check` prims **1728 → 1901**, hash `92c4f255 → 2bc75d66`, **identical across all three arms** (MTL0/MTL1/V1) so R-4 and R-6 both PASS; `placement_lint` exit 0 with the severity profile **unchanged** (13 WARN · 1 BLOCKED · 0 ERROR before and after) and only numeric diffs. Width self-check: effective water **15.8 → 33.8 m**, amplitude **14.81 → 24.79 m**, |yaw|max **35.64°**, and water **screen-area +31.8…+48.2 % on all 9 judge presets** (+39.1 % `levee_walk`). Meander legibility rose on the same instrument: bow `meander_air` 14.09 → **20.41 %**, `bank_oblique` 14.15 → **28.16 %** (gate ≥5 %). **R-3 re-stamped**: 16 cuts, FAIL 14 · WARN 2 · EXPECTED_FP 0. **All 14 FAILs are FRAME**, which detects *"the composition changed"* — the round's purpose — and carries no defect information here. Adjudicated: **GRAZE `preset_h0.3_d2` = NON-DEFECT** (drop-row step 81.1 → 80.2, **ratio 0.99**; max-change row y211 vs drop row y249, 38 rows apart, so the change is a *different object* — the widened water and the deleted patch — which is exactly why the tool's own persistence test could not auto-quiet it; the shoulder line is unbroken in both arms on the mandated y170–312/540 crop). **WHITE `bank_oblique` 8.4 → 22.1 pp** attributed at pixel level to the **longer bridge deck** (15.1 of 16.0 pp in the bottom third, mean RGB 208/208/209, `BLOWN` silent, clip 0.0 %) meeting a frozen camera — handed on, `w3_s03_v1.md` §7-2. OCCL on 5 cuts, max **3.9 % new-dark / 1.8 % blob**, ~10× under C02-P1's 32.8 %/19.7 %; the three h0.3 judge cuts are 0.3/0.1/0.1 %. **Instrument defect found and fixed in the same round** (`w3_s03_v1.md` §4.1): the bridge occluder was one AABB counting the open space under the deck *and* ±10.43 m of empty skew corner as solid, which alone drove `meander_air` to 44.3 % against a 35 % gate; corrected to a rotated-frame deck + per-pier boxes, and **it moves the v6 arm too** (`bank_oblique` 26 → 15 of 121), which is what makes it a fix and not a tuned gate. **New baseline-of-record `260731_w3_s03`**; the A/B control is a HEAD-arm twin rendered this session (`260731_w3_s03_pre`) because the INDEX baseline `260730_w2d_fix` predates K4(b) species `e4d9cf9` and would have charged four kit landings to this scene | 2026-07-30 |
| GT-32 | S03 | — | `e4862aa` | *(rides GT-31's single re-cache — same commands)*. The two items that needed R-1 to **prove** a registry move: `placement_lint` reads the bollard relocation directly as `gaps 4.400 → 2.400`, and the same inventory line shows **`patch=8` present before and absent after**. Assembly log: `[03-D] 사면 관목 18/18주 (place_shrubs · 1 bed · role hedge_evergreen · h 0.85 m)` · `[ground_kit] scene03 P13(natural) · prims 17 + edge_break 1 · delta_max 0.1198` | **Landed as declared, with one consequence measured that the row did not anticipate and did not hide.** All three rectangles are gone and the h0.3 d2 crop shows it plainly. **But the patch at (−1.10, 0.15) sat 0.90 m in front of the h0.3 d2 judged eye and was carrying the near window's entire tonal budget**: on deletion `near_ground_stats` B30 read `wht%` **6.8 → 39.3**, `σ_LF` **4.34 → 1.02**, `>224%` **0.87 → 5.18** (over its ≤5 gate). Recovery attempted **inside the ban** with the vocabulary §3(ii) explicitly keeps, and **only half of it landed** `[amended at `9b96ea9`, after the render]`. ~~`("weed", 8)` + `scatter` gravel 0.08/130 (under the `trail_soil` 0.10/150 and `courtyard_dg` 0.09/200 precedents): `σ_LF` back to **3.35**, `>224%` back under gate at **4.23**, `sd` **24.2 > HEAD's 23.8**, and `preset_h0.3_d5` `σ_LF` **4.14 → 5.66 = the only fully clean h0.3 cut in either arm**~~ — **those figures are real and the `scatter` row that produced them was REVERTED on the render anyway.** `apply_ground` scatters over the whole plan region (−12…0, ±3), which on this crest is **mostly mown grass**, so d5/d10 filled with pale 0.1–0.2 m stones strewn across a lawn; a levee crest carries stone on its gravel track and none on its verge. **Trading a blank floor for boulders on a lawn is a worse frame, so the statistics lost** — the parameters are left in the source comment so the attempt is not repeated blind, and a **region-restricted scatter** is the ask filed with the kit lane. What LANDED is `("weed", 8)` alone (P13's own row prescribes 6; G3 shows weeds in every revetment joint), correctly seeded on the gravel/grass margin and therefore **outside the d2 near cone**, which is why it buys almost nothing statistically: final `preset_h0.3_d2` **`σ_LF` 0.94 · `wht%` 39.1 · `mean` 194 · `>224%` 5.06**. The residual is the crest gravel's own albedo at 2 m, which the patch had merely been covering — an albedo question no decal can answer, handed to the T1/ground lane (`w3_s03_v1.md` §7-3), and already violating at HEAD (6.8 against <2). Final prim count **1901**, hash `2bc75d66`, three-arm identical; `scatter` contributed 0 to the geometry hash (it is instanced), so the revert leaves R-4/R-6 untouched. GRAZE on `preset_h0.3_d2` re-reads at the pre-scatter values and is graded **FAIL** (`gz_spec 21.50 > 20.0`): the adjudication in GT-31's record is unchanged and rests on `gz_step_ratio` **0.991**, `gz_step_off` **38 > 4** and `gz_step_dom` **3.39 < 3.5**. **03-B deviations declared, not smoothed**: post interval 2.400 m against 별표2's "1.5 m 안팎" (LINT PE-6 WARN, left visible), and the pair now enters the d5/d10 frames it used to fall outside — geometric occupancy 0 → **2.2 % of the d5 frame**, photometric cost **0.1 % new-dark**. **03-C/K4-F4 discharged for 03**: `belt=True` (not a hard-coded `species=`, which would fork the species table), near bank poplar / far bank Black_Oak. **03-D**: one `place_shrubs` call = one bed, because six per-bed calls could stand two species on one continuous 25 m slope; `target_h` 0.850 is set by the instrument — G3's ~1.5 m mass would top **0.514 m above the h0.3 judged eye** and eat the water band that is this type's only drop evidence, 0.850 m tops **0.136 m below** it | 2026-07-30 |
| GT-34 | S01 | CB-2 · CB-5 · GATE-1 pilot **01** | `ac7a50c` → `7fb925a` → `45a76af` → **`f6bb772`** (+ report `9ec1cba`) | **R-1** `NEGOBS_SMOKE=1 python3 scenes/main/scene01_campus_stairs.py` — the scene's **new** `plaza_selfcheck`, boot-free and GPU-free; scene01 had **no** smoke path before this lane (`w3_mb_patch_v1.md` had to record the §6.1 item as having no subject here). **R-2** `flock -w 7200 /tmp/negobs_gpu.lock` → `python3 scripts/run_data_render.py --run 260731_data_s01 --scenes scene01` then `python3 scripts/check_data_run.py 260731_data_s01`. **R-3** `flock -w 7200 /tmp/negobs_gpu.lock` → 13-cut PT round in an **isolated `git archive f6bb772` arm** (`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`, `NEGOBS_VIEWS` **unset** = full order prefix) → `scripts/stamp_round.py` → `python3 scripts/regression_check.py --before look_check/scene01/260731_w3_mb24 --after look_check/scene01/260731_w3_s01 --json Docs/reports/regr_260731_w3_s01.json` → `python3 scripts/near_ground_stats.py 'look_check/scene01/260731_w3_s01/pt_noon_preset_h0.3_*.png' 'look_check/scene01/260731_w3_mb24/pt_noon_preset_h0.3_*.png' --gate`. **Attribution arm** rendered in the same channel from `git archive 1234a51` (= `ac7a50c^`, scene01 file unedited) as `260731_w3_s01_pre`. **Floor** per commit, in isolated arms: `python3 -m py_compile` · SMOKE · `python3 scripts/geom_invariance_check.py --scenes scene01` · `python3 scripts/placement_lint.py --scenes scene01` | **Baseline named per §6-W4: `260731_w3_mb24`** (scene01's baseline of record from the MB patch batch, `e1150d6`); **`260731_w3_s01` is stamped `baseline_of_record: true` and supersedes it**, and `260731_w3_mb24` carries `baseline_of_record: false` + `superseded_by` (the S10c convention, closing the MD-F5 class for this scene). **R-1** — registry re-derived from `PARAMS`: **drop 7 · up_step 3 · walkable 7 · seat_tier 3**. Total stair drop asserts at **0.600000 m** (the approved flight does not move); riser 0.150 ≤ 0.180; kerb top **+0 mm** against the walk (S06-B's flush … +20 mm); kerb exposure 0.150 inside [0.100, 0.250]; lawn top = plaza − exposure to 1e-9; the lower-plaza frontage **+0.450 asserted as an UP-STEP, not a drop**; kerb block bottom −0.700 = the plaza slab's own underside (no void behind the face); every new drop < 0.600; every walkable step ≤ 0.200 (max 0.160); bench yaw jitter **0**; worst judged-eye ↔ planter distance **2.63 m** ≥ 2.5 (the `w3_md_reverts_v1.md` §5 census row for this scene is cleared by deletion, not mitigated); `plaza_granite` `surface` = `('crack', 'stain')`, **no `patch` row** (GT-24). **R-2 PASS on what it measures** — `dataset/260731_data_s01`, 8 cuts, **1.78 s/cut** vs SP-3's 2.87; `check_data_run` **[2] azimuth · [3] camera placement · [4] file/manifest · [5] throughput ALL PASS** (every sampler truncation respected, 8 files / 8 records, all content-unique, all 1920×1080, **nothing written under `look_check/`**). **[1] carries 2 FAILs, recorded not cured**: `sun-bearing (0 pairs ≥ 0.3 EV apart)` and `sunless (0 scene-pairs)` — zero-sample cross-condition checks that need `--conds` > 1, the identical pair GT-14 and GT-18 recorded, silent about geometry. **R-3** — **5 GATE-1 cuts vs the baseline: FAIL 2 · WARN 3, every code `FRAME`** plus one `GRAZE` on `h0.3_d10`; block shift 14–48 %, which is the **declared** result of rebuilding the flanks and the backdrop. **The attribution arm makes that readable**: `260731_w3_s01_pre` vs the same baseline scores **FAIL 0 · WARN 3**, all three `[UNCHANGED]` (mean diff 0.10–0.13 LSB, pixels over 4 LSB **0.003–0.006 %**) — i.e. the entire Lane-1 kit window and every other lane's landing in between is **null on this scene's judged cuts**, so every finding is this lane's. Channels that still mean something, all 13 cuts: **DARK improves everywhere** (`lower_lookback` dark % **32.4 → 5.8**, mean 102.8 → 156.9 — flagged `[PHOTO] 휘도 급상승 · 의도 확인`, and the intent is the deletion of a 9 m brick mass at 42 m); **BLOWN 0**; **WHITE 2 flags, both sky** (`beauty_overview` 34.1 → 50.5 %, `h1.8_d10` 21.3 → 36.4 % — deleting the two buildings that filled the upper half of those frames *is* the directive, and the ground band did not blow: `>224 %` 1.40–2.49); **OCCL 1 cut** (`amphi_view` new-dark 2.5 %, blob 0.1 %, near-field 0.0 % — the fountain and the second tree row), **new-dark ≤ 0.3 % and blob ≤ 0.1 % on every judged cut**. **`near_ground_stats` h0.3: `flat_gnd` CLEARS on all three cuts** (d2 0.7→0.4 · d5 **9.6→0.0** · d10 **3.6→0.0**) and `flat %` on d5 collapses 14.54 → 0.00. Two movements are stated rather than chased and share one cause — the 0.65 m albedo-0.10 manhole lid that filled the d5 near window is gone under the G-4 derivation: **`sd` d5 41.7 → 13.1** and **`mean` d5 185 → 204**. `mean > 170` and `wht % ≥ 2` were already WARNing in the baseline. **GRAZE adjudicated by crop** (`Docs/reports/_w3_s01_crops/s01_graze_band_h0.3_d10.png`, the tool declares it cannot auto-confirm): the stronger cross-screen line in the d10 edge band is **not the stair** — the flight is byte-unchanged — it is the **new east lawn retaining face at x = 14**, 24 m from the eye and 14 m past the drop, which replaced the raw turf-against-granite boundary that occupied the same rows. Handed on as **S01-F7** because it takes a full-width cross line in the band `GT-E2` caps at one. Also handed on: **S01-F1** — `building_kit` emits parapet + penthouse **+2.90 m above** `base_z + h`, so backdrop policy (2)'s `z_ceil` does not bound the ridge; the first two pilots printed “sky above roof 6/6” while the render cut the top edge of `h0.3_d10`, and the check now compares the ridge (predicted 7.97 = emitted 7.97). **Floor at `f6bb772`**: py_compile OK · SMOKE rc 0 (`SMOKE_OK rows=20`, 13/13) · geom_invariance **R-4 1/1 · R-6 1/1**, **431 prims / hash `a9d6c2ba`** identical on all three arms (was 353 / `108cad2f`) · placement_lint **ERROR 0 · WARN 12 → 6 · BLOCK 1 unchanged** (the six cleared WARNs are LINT-7's per-bench yaw findings = 01-D / CB-5). Full write-up: `Docs/reports/w3_s01_v1.md` | 2026-07-30 |
| GT-29 | S06 | CB-9 | `94dc38d` (geometry) · `c48e6e9` · `69c6f9f` | **R-1** `NEGOBS_SMOKE=1 python scenes/main/scene06_overpass_spiral.py` — the scene re-derives and prints its own registry from the changed geometry: continuity **OK** with **26 identical 0.192 risers** and landing→deck **Δ+0.000** (was a 0.190 short riser plus a 2 mm lip), hazard arc [180, 270] open edge **4.909…3.411 m, mean 4.160**, corridor dressing intrusion **0**, camera collision **0 / 15 views × 40 AABBs**, h0.3 concealment unchanged (ground re-emerges y −46.4 / −96.4 / −179.8 at d2/d5/d10). **Split proof** (GPU 0, two isolated `git archive` arms, `assets/` symlinked so the arms are asset-equal): `python3 gt_probe.py <arm> <out.json>` ×2 → `python3 gt_diff.py gt_head.json gt_post.json` — walked-top-face sampling over 9 radii × 1969 azimuths. **R-3** round **`260731_w3_s06`** (15 cuts, PT, 61 s, `flock -w 7200 /tmp/negobs_gpu.lock`, arm byte-identical to the baseline stamp: `NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`), then `python3 scripts/regression_check.py --before look_check/scene06/260730_w2d_fix --after look_check/scene06/260731_w3_s06 --json Docs/reports/regr_260731_w3_s06.json`. **R-2 not owed** (declared class: no drop edge created or destroyed, hazard registry unchanged, +2 mm below `GT_DELTA = 0.020`). | **Split proof: of 17,721 samples the walked surface moves in 5,986, and all 5,986 fall in four strata, every one of them a term GT-6 enumerates** — `landing → landing` **+2.000 mm exactly ×3956** (the row's own +2 mm), `tread → tread` **−192.000 mm exactly ×1584** (the box overshot its design rays by a mean **6.55°**, so the previous higher tread won the top face; true sectors hand over correctly — **no tread's own z moves, the ladder is bit-identical**), `fascia → tread` ×310 (the ribbon stood **165.640 mm** proud of the tread it trimmed; the intake's 154 mm is superseded), `landing → tread` ×168 (the landing's `a0` ray overshot **≤ 4.25°** — chord 234 mm at r 3.15 — a phantom 5.000 slab 3.07 m above the tread outside its design range). **`new-void 0 · new-solid 0`.** Everything else that moved is guard-height (rails / coping / glass caps), which is the row's declared R-3, not a GT change. Landing/deck interpenetration **9.186 → 4.156 m² (−54.8 %)**; the residual is declared, not hidden — closing it needs `_grid_shift` decoupled from `deck["y0"]` first (finding S06-F3), which is camera-adjacent and was not taken unilaterally. **Unscoped invariance**, isolated arms, asset-equal: scene05 `3ac9076a…` n=1234 · scene13 `b0afe7a8…` n=495 · scene19 `4ac6372a…` n=284 — **byte-identical before and after**. **Floor**: py_compile ✔ · SMOKE **rc 0**, 35 OK gates · `geom_invariance_check --scenes scene06` **R-4 1/1 · R-6 1/1** (prims 2025, hash `a51b354c`, identical across MTL=0 / MTL=1 / V1=1) · `placement_lint --scenes scene06` **ERROR 6 · WARN 15 · BLOCK 1**, identical to the asset-equal HEAD arm. **Baseline**: `260730_w2d_fix` named per `look_check/README.md`; **`260731_w3_s06` is scene06's baseline-of-record from here** (stamped, `baseline_of_record` marker set). Regression **FAIL 8 · WARN 5 · PASS 2 · EXPECTED_FP 0**, adjudicated per cut in `Docs/reports/w3_s06_v1.md` §8.1: FRAME (13) is the declared rebuild; OCCL's *"camera swallowed"* hint is **rejected** on blob **2.2–3.7 %** against a smoke camera-collision count of **0**; GRAZE **abstained** (INFO, no edge band) and is **not** recorded as a pass. | 2026-07-31 |
| GT-30 | S06 | CB-9 | `94dc38d` | *(rides GT-29's single re-cache — same R-1 / R-3 commands, same round `260731_w3_s06`)* | `build_curb_line` returns **`gt_drop = 0.168`** (0.150 exposure + 0.018 gutter cross-fall) on both carriageway edges, **`is_gt_hazard = True`, `warnings = []`**, printed live by the scene. **94 prims/side at 0.671 prims/m** (against 141 at the full 1 m rate) via `lod_span` over the judged window x ∈ [−26, +26] with `far_unit = 8.0`. Arris asserted live: `ik.check_arris_role(sc)` → **`LOOK_CLASS['curb'].bevel = 10.0 mm`, OK**. **Owed, recorded rather than substituted**: S06-B item 3's **`curb_granite_light` texture role does not exist** in `scene_common.TEX`; a scene-local `CurbGraniteLight` (granite maps + lightening tint) stands in, and `granite_dark` is not reused. The new 168 mm edge lies on the carriageway line, outside every judged grid corridor and outside the r ≤ 4.2 near frame, so the scene's hazard registry is unchanged — the spiral's missing-rail arc remains its sole declared hazard. | 2026-07-31 |

| GT-35 | S5 (`main/scene09_ghat_riverfront.py` + the `SCENE_PLANS["scene09"]` fixture row) | CB-S09 · GATE-1 pilot **09** | `44ad574` (geometry, declared at `013fe8a` per §0-1) + `02fdfa9` (the three corrections the first pilot render forced) | **Floor (§6.1)** `python3 -m py_compile scenes/main/scene09_ghat_riverfront.py ground_kit.py` · `python3 ground_kit.py` · `NEGOBS_SMOKE=1 NEGOBS_LOOK_V1=1 python -u scenes/main/scene09_ghat_riverfront.py` · `python3 scripts/geom_invariance_check.py` (unscoped, **in both isolated `git archive` arms**) · `python3 scripts/placement_lint.py --scenes scene09 --rules Docs/briefs/placement_rules_v1.yaml` (both arms). **R-1** `NEGOBS_SELFCHECK=1 python3 scenes/main/scene09_ghat_riverfront.py` — the scene's five boot-free gates (`roof_normal_selfcheck` · `albedo_selfcheck` · the three this row adds: `season_audit` · `fov_selfcheck` · `horizon_selfcheck`), exit code 0. **R-2** under `flock -w 7200 /tmp/negobs_gpu.lock`: `python3 scripts/run_data_render.py --run 260731_data_s09 --scenes scene09 --conds L0,L7,L5 --cams 4` then `python3 scripts/check_data_run.py 260731_data_s09`. **R-3** same lock, judge channel (`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`), **18 cuts in full `build_views` order**, `python3 scripts/stamp_round.py look_check/scene09/260731_w3_s09 260731_w3_s09 scene09`, then `python3 scripts/regression_check.py --before look_check/scene09/260731_w3_cb1 --after look_check/scene09/260731_w3_s09 --json look_check/scene09/260731_w3_s09/regr_vs_260731_w3_cb1.json` and `python3 scripts/near_ground_stats.py 'look_check/scene09/260731_w3_{cb1,s09}/pt_noon_preset_h0.3_*.png' --gate` | **Baseline named per §6-W4: `260731_w3_cb1`** (17 cuts, the scene's baseline-of-record per `look_check/README.md` §4). **`260731_w3_s09` is scene09's baseline-of-record from here** — 18 cuts, a superset, so nothing is dropped from later comparisons. **Floor**: py_compile OK · `ground_kit` self-check **all items pass, 33/33 hard gates** · SMOKE rc 0 · `geom_invariance` **R-5 ✔ · R-4 33/33 · R-6 33/33 PASS on both arms**, and the isolated A/B table diff is **one line long**: `scene09 501 → 1507` prims, hash `840928aa` → `46882b0f`; the other 32 scenes are byte-identical, library **31,624 → 32,630**. `placement_lint` **0 ERROR (unchanged) · 12 → 13 WARN · 1 BLOCK (the pre-existing evidence-gated LINT-9) · 0 INFO**; the inventory line loses `patch=5`, which is row (4) made visible. **LINT-10 fired on the wall's `jitter=` kwarg and was adjudicated by moving the code, not the report**: the draw is on the block's *depth* with its bedding face pinned to the wall plane, i.e. size variation under §1.2 X2, and the parameter is renamed `depth_var` so the classification lives at the call site. The one new WARN is **LINT-4's census fallback** — it fires *because* row (7) works: the scene now carries `Gray_Birch x10` (route) + `Black_Oak x8` (belt), and the route-scoped gate has no datum because scene09 has no route to declare (its trees are a park scatter; a fabricated `PLACEMENT['routes']` would assert a pitch the ground does not have and take a LINT-2 ERROR for it). Accepted and explained, not silenced. **Fixture**: kit-plan dry run **1141 → 1137 prims (−4)**, scatter **740 → 670 (−70)**, scene09's fixture **20 → 16**; the real library moves **0** — the W9 drift, measured on both sides for the first time. **R-1**: five gates green — season (7 atlases re-measured, 5 beds all `USE`), FOV (13 added elements, **0 inside** any preset cone, smallest margin **+3.2°**), horizon (`from_river` +9.44° → **+16.85°**, `across_river` +10.57° → **+18.55°**, i.e. closure improved, not merely kept). **R-2 PASS** — `DATA RUN CHECK PASS`, 12 cuts, **2.05 s/cut**, `r_reject 0.0`, nearest solid to any eye **0.948 m**, buried 0 · closed_in 0 · offground 0, 12/12 content-unique. **R-3 — 18 cuts, FAIL 10 · WARN 1 · INFO 3 · PASS 4, and the FAILs are read rather than reported.** Every FAIL is `[FRAME]`, the tool's own tone-normalised *composition changed* channel, and it has exactly two causes, both declared: (a) **the old straight deck slab is gone from under the `d10` preset eye.** It ran `x −10.0…−7.6, y −22…+22`, so the `d10` eye at `(−10, 0, 0.3)` **stood on it** and it filled the lower 60 % of every `*_d10` frame [measured, baseline PNG]. Removing it exposes the granite terrace — and the exposed numbers land **exactly on `d2`/`d5`'s own**: `near_ground_stats` `wht%` d10 **0.0 → 64.6** against d2 **65.6 → 66.0** and d5 **65.1 → 65.2**, `mean` d10 131 → 203 against d2 206 and d5 204. That identity is the proof: `d10` did not acquire a defect, it **stopped being masked** from the one this scene has had at d2/d5 all along. (b) the far-bank skyline changed by design (row (6)). **DARK/BLOWN clean; OCCL fires on one cut**, `park_vista`, new-dark 8.0 % / blob 1.5 % — that cut looks straight at the new bed walls and the boardwalk, so the new dark **is** the new geometry. **GRAZE `[의심]` on `preset_h0.3_d2` adjudicated NEGATIVE** by crop + metric: `Docs/reports/_w3_s09_crops/scene09_graze_edge_h0.3_d2_ab.png` shows the paving, its joints and the paving/water drop line **unchanged**; what moved inside the tool's edge band is the horizon strip *above* it (buildings → ridge, and the new reed plumes), and `near_ground_stats` at d2 is flat on every channel (`sd` 17.9 → 18.1 · `edge` 41.9 → 40.0 · `flat_gnd` 12.5 → 12.6). **The one thing this record does not smooth**: the terrace paving is a **v5.1 §4 large-near-white area and always was** — `wht%` 65 / `p95` 219–223 sRGB on all three h0.3 cuts in **both** rounds. This row neither caused it nor cures it; it removed the object that was hiding it at d10. The measured correction is one number and it is left for the scene's next look pass rather than taken at the end of a lane: `stone_tint` **0.64 → 0.524** (linear factor **0.818**, from p95 0.8745 → 0.80 sRGB), with `stain_tint` and `moss_tint` scaled by the same 0.818 so the waterline contrast ratio — this scene's only drop anchor — is preserved, exactly as v7 did it. **Two defects the lane found in its own work and fixed in the same batch**: `hash(str)` was seeding the wall layout, which CPython randomises per process, so prim hashes would have differed run to run (replaced by `_tag_seed`; verified identical `46882b0f` under `PYTHONHASHSEED=1,2,3`), and the v8 roof probe was querying `specular_level` when the `LOOK_MTL` route authors `specular_level_a`, printing a **false FAIL** on a correctly-set material (now queries both and names the factory). **Concurrency, stated**: seven other lanes share this worktree; every structural number above comes from isolated `git archive` arms, and the pilot was rendered with `dirty_paths` = `scenes/main/scene0{1,3,6}.py`, `scene1{1,3}.py` (other lanes' uncommitted scene files) — none of which is referenced by `scene09_ghat_riverfront.py` or by `scene_common.py` | 2026-07-31 |
| GT-10 | S5 (`main/scene09_ghat_riverfront.py`) | CB-1 · GATE-1 pilot **09** | `50189e9` (*"CB-1 씬09 — 진단 3컷(S09-A) + 석주 계단면 이탈(S09-C)"*, 2026-07-30) | **R-1** the props are re-derived from `PARAMS["land_posts"]` and re-checked live this session: `NEGOBS_SELFCHECK=1 python3 scenes/main/scene09_ghat_riverfront.py` (exit 0) + an explicit bearing recomputation over the four stations against all three preset eyes. **R-3** round **`260731_w3_cb1`** (17 cuts, the round CB-1 itself stamped and the scene's baseline-of-record); re-confirmed against **`260731_w3_s09`** this session under `flock -w 7200 /tmp/negobs_gpu.lock` | **The row's own words — *"to the terrace edge or the lowest landing"* — are satisfied by the terrace-edge option.** All four posts stand at **one height**, `x = −0.80`, `z base 0.000`, `y = ±5.6 / ±12.0`, `r 0.24 · h 2.1`; none of them touches the stair face. The pre-state they replace was two per landing at the landing `x` centres (4.34 / 9.28) on the **revetment** with their bases at the landing top faces **z −2.040 / −4.080** — posts embedded partway up a stair slope, which no 계선주 ever is. Count is **4**, not the 6 §3 quotes: §3's `n = 6` is the `mooring` **pile** row (`cx −1.2`, `cy ±3.8 / ±13.5 / ±19.0`, `r 0.09 · h 0.50`), a different object that this row never moved and still has not — recorded so the next reader does not go looking for two missing posts. **Re-cache result: no new occlusion of a hazard row.** `x = −0.80` sets them **0.56 m back** from the stair-head lip and clears the pavilion eave tip (x −1.15) by **0.11 m** [computed]. **One correction to the scene's own claim, made because it was re-measured instead of re-read**: `scene09:291` states the four posts *"bear ≥ 31.3° from the furthest grid preset eye"* — 31.3° is the **centre** bearing. The figure that decides occlusion is the **silhouette tangent**, `atan2(5.6, 9.2) − asin(0.24/10.77)` = **30.05°**. The claim survives — the posts are outside the ±30° cone — but by **0.05° (≈ 9 mm at 10.77 m)**, not by 1.3°, and any future change to `land_posts.r` or `x` must be checked against 30.05, not 31.3. **The two posts visible near the edges of every `*_d10` preset frame are NOT these**: at bearing 23.4° they are the `mooring` piles at (−1.2, ±3.8), pre-existing, in-frame in the baseline too, and outside this row's scope. **Coupling honoured**: `landing_return` runs at a constant `x = 4.34`, the exact landing-1 centre the old post at (4.34, −5.6) stood on spanning z −2.040…+0.060 — it would have blocked the cut outright, which is why S09-A and S09-C shipped in one commit. The cut renders clean in both `260731_w3_cb1` and `260731_w3_s09` (`PASS`, new-dark 0.1 %). **R-2 not owed** — props only; no walked surface, no drop edge and no hazard row moves, and the flight, landings, embankment and terrace are bit-identical across the move | 2026-07-31 |
| GT-37 | S6 (`main/scene08_sunken_plaza.py`) | CB-8 · GATE-1 pilot **08** + OCCL re-stamp | declared `1edd838`, landed `0af6f24` (+ pilot fixes `f8206de`), report `dd32c01` | **R-1** `NEGOBS_SMOKE=1 python3 scenes/main/scene08_sunken_plaza.py` — the scene's rebuilt self-check, boot-free and GPU-free: **35 gates, 0 failures, rc 0**. It re-derives the hazard geometry from `PARAMS` instead of restating it (bowl arithmetic · both banks landing on one arena radius · the a = 180° walk continuity at 5 cm resolution · L1/R1/D1 · the concealment margins · two h0.3 exposure scans · the sector-bearing table · the near-window occupancy table · the raking-light floor share · camera collision + polar bed clearance · the mise-en-scène ray march · six deletion gates that read the file's own source). **R-2** under `flock -w 7200 /tmp/negobs_gpu.lock`: `python3 scripts/run_data_render.py --run 260731_s08_recache --scenes scene08 --conds L0,L7,L5 --cams 8` then `python3 scripts/check_data_run.py 260731_s08_recache`. **R-3** same lock, judge arm byte-identical to the baseline's own stamped env (`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`, no `NEGOBS_VIEWS` filter), 15 cuts × 4 pilot rounds `260731_w3_s08{,b,c,d}`; `python3 scripts/stamp_round.py look_check/scene08/260731_w3_s08d 260731_w3_s08d scene08`; then `python3 scripts/regression_check.py --before look_check/scene08/260730_w2d_fix --after look_check/scene08/260731_w3_s08d` and `python3 scripts/near_ground_stats.py 'look_check/scene08/260731_w3_s08d/pt_noon_preset_h0.3_*.png' --gate`. **Floor** (§6.1), tree-wide legs in isolated `git archive` arms (MD-F1 — seven other lanes were writing this worktree): `python3 -m py_compile` · `geom_invariance_check --scenes scene08` and unscoped · `placement_lint --scenes scene08`. | **R-1 done.** 35/35 gates, rc 0. The numbers the row turns on, all re-derived rather than quoted: near rim **x = 0.00** (unmoved from v6 by construction, `CX = R_RIM`) · far rim **x = 28.00** · floor **−4.500** = `riser 0.150 × 30` · arena **r 4.10**, reached by BOTH banks (`11 × 0.900 = 9.900 = R_RIM − R_ARENA`, `12 × 0.375 = 4.500`) · walk continuity along a = 180° at 5 cm resolution, worst step **0.1500 m** = exactly one riser · concealment `x_hit` **30.0 / 75.0 / 150.0 m** at d = 2 / 5 / 10 against a far rim of 28.0, margin **+2.0 m** at the binding d = 2 · raking-light floor share **94.6 %** direct sun (sample 2,480). **The sector angles are a gate, not a comment**: at h0.3 the graze cone falls 0.15 m/m, so a *stepped* bowl surface that is both inside the 30° half-frame and above `z = −0.15 x` announces the depth. Scanned at 1° × 0.10 m, the first plan's tier bank at **70…150° gave 369 such points** (outer courses at `a ≈ 70°`, top −2.25 against a cone at −2.59); at **90…150° it gives 0**, and a second gate covers the standing elements the surface scan cannot see (flank rails · bed kerbs · shrub and tree crowns · benches · arcade columns · shopfront heads · the sign) — that gate is what moved the in-bowl bed from a0 216° to **222°**, its 5.4 m Fraxinus crown having measured 29.5° bearing and 1.28 m above the cone. **Stair compliance**: `stair_compliance_v1.md` ranked scene08 **#1 with 2 P0 findings**; both are cleared by geometry — **L1** by a 1.20 m mid landing at −2.250 (worst flight 2.250 m < 3.0) and **R1** by riser **0.150** AND tread **0.300**, the §15①3 단서, which is why the riser is a judgment requirement and not a style choice: it lets the cascade be **14.65 m wide at the head** with no handrail row on the camera axis. Tiers (riser 0.375) are recorded as **seating, not circulation** (scene05 ※). **R-2 done — `DATA RUN CHECK PASS`**, 24 cuts / 3 conditions / 8 cameras, `260731_s08_recache`: ground found under 24/24 cameras, `ground_below == h_rel` worst \|err\| **0.0000 m**, nearest solid to any eye **0.505 m** (≥ 0.15), every sampler truncation respected (h_rel 0.505–1.645 · pitch −16.9…−4.6 · hfov 59.7–64.4 · d 1.43–8.91), 24/24 manifest↔disk, 0 orphans, all content-unique, nothing written under `look_check/`, **2.73 s/cut** against SP-3's 2.87. **R-3 done**: `260730_w2d_fix → 260731_w3_s08d`, 15 cuts, **FAIL 15 · WARN 0 · PASS 0** — the expected shape of a total rebuild, and the reading is which codes fire. **FRAME 15/15** (declared: every prim moved, 62–88 % moved blocks). **PHOTO 12/15**, attributed rather than waved through: v6's `N1` block at `y 24…38, h 28.0` cast a shadow reaching `y = 24 − 28/tan(49.79°) = 0.3` — **it covered the walk axis** — and v7's CBD wall stands back at `y 34…46` (BS-4 + the measured finding that a −18 m facade puts a 32 m tower **8.0 m behind the judged camera**), so the near band is now in direct sun; `near_ground_stats` says the band is objectively richer for it — `sd` 25.4 → **39.4**, `edge` 23.7 → **74.7**, `flat%` 2.22 → **0.02** at d2. **OCCL 7/15**, adjudicated: `d_dark` is **negative on 13 of 15 cuts** (the rebuild removed dark area); the two that gained are inside the bowl — `beauty_overview` +10.9 pp / blob 5.5 % is the 4.5 m-deep bowl's own raking-light shadow on its north-west wall (the *floor* measures 94.6 % sunlit), and the tool's own hypothesis *"new geometry may have swallowed the camera"* is refuted by the collision gate (0 hits over 15 views × 24 AABBs + the polar bed test) and by first-block **1.00** on that cut's ray march; on the judged near cuts the near-band new-dark is **0.06–1.70 %** with **blob 0.00** on all three h0.3 presets. **WHITE 0/15** — and that is the one real defect this lane created and then closed: pilot 1 put **77.4 %** of `h0.3_d2` past 0.8 (`L_mu 0.728 · wht 29.6 %`) by binding `plaza_light` (**measured albedo 0.710**) to the near band, i.e. a plaza brighter than any 화강석 판석 in the field; four pilots later the max WHITE on any cut is **3.28 %** (`stair_south`, against a **baseline of 31.15 %** on that same cut). **GRAZE 3 INFO** `[v2.1] 판정 유보` — the tool withholds a verdict when frame photometry moves, so no GRAZE verdict exists for this round and none is claimed. **Baselines-of-record, closed rather than left ambiguous**: `260731_w3_s08d` is scene08's baseline-of-record and its stamp says so (`baseline_of_record: true` + `supersedes` + `comparison_baseline_used` + `superseded_pilots` + `dirty_paths` + `env_source`), and **`260730_w2d_fix` now carries `baseline_of_record: false` + `superseded_by: 260731_w3_s08d`** on the §11 SB-3 precedent — keys only, nothing re-rendered. **Floor**: py_compile ✔ · SMOKE 35/35 rc 0 · `geom_invariance --scenes scene08` R-4 1/1 · R-6 1/1 PASS, prims **688 → 714**, hash `eac15c7d → bab35b70` · **unscoped 33/33 · 33/33 PASS at BOTH `0af6f24` and `f8206de`**, in isolated arms · `placement_lint --scenes scene08` **ERROR 5 → 0** · WARN 10 → 9 · BLOCK 1 → 1 (the 5 dead ERRORs are LINT-6's v6 bollard row; the 9 survivors are all `nodata`/`[inferred]`, 5 of them LINT-7 yaw findings against the Cartesian set {0, 90, 180, 270}, which on a radial plan is the wrong instrument). Full record `Docs/reports/w3_s08_v1.md` | 2026-07-31 |
| GT-38 | S6 (`main/scene08_sunken_plaza.py`) | CB-8 · GATE-1 pilot **08** + OCCL re-stamp | `0af6f24` | *(rides GT-37's single re-cache — same commands, §0-2)* | **B-1 built and GT-7 executed in the same commit.** Guard over **210…450°**: 0.30 m parapet upstand + coping, then `props_kit.build_glass_balustrade` used **verbatim** — shoe channel, 19 mm laminated panels in **1.35 m** bays with a 12 mm joint, capping rail — **44 panels · 22 caps · 22 shoes**, total guard height **1.40 m** (above the statutory 1.1, where v6 was a sub-code 1.0). Over **150…210° there is no guard at all**: that is the cascade head, and a grand cascade has no guard across its head because the head *is* the way in. The tier-bank head (90…150°) is likewise unguarded — a 0.375 m first riser is not a fall edge — and is closed with a planting bed. **v5's deliberate deviation survives and B-1 is what pays for it**: the opening must sit on the grid axis or 6 of 9 grid shots fill with parapet wall (scene19 d5 blackout); v6 bought that with a demolished run, v7 with a legitimate stair head. **GT-7 deletions, gated in the smoke run**: `build_tempbar`, `PARAMS["tempbar"]`, the **2 `TempPost_*` collision boxes**, the 3 tempbar materials and the tempbar self-check block — all absent, asserted against the file's own source. **The fold's condition was met**: `w3_execution_spec_v1.md` §5.2 CB-8 requires the supersede note *in the message*, and §1.6's note (which overrides `tonglam_v2.md` §1 row 08's PASS) is reproduced **verbatim in `0af6f24`**. Consequence carried forward: scene08's 통람 PASS is **not** carried forward; it enters 통람 v3 unranked. **Finding S08-F1, reported not fixed (kits frozen)**: `build_glass_balustrade` and `build_tube_railing` are **X-axis-only** — panels are `add_box` on world axes, caps are `add_cylinder(rotY=90)` — and their self-checks only exercise `[(0,0),(6,0)]`; scene08 mounts each chord in its own `sc.build_rot_group`, which is the correct client pattern, but the kit owes a `bearing=` kwarg | 2026-07-31 |
| GT-39 | S6 (`main/scene08_sunken_plaza.py`) | CB-8 · GATE-1 pilot **08** + OCCL re-stamp | `0af6f24` | *(rides GT-37's single re-cache)* — the R-1 leg additionally has to show the **new** drop entering the registry, not merely show the registry unchanged | **The new drop is measured, not assumed: `gt_drop` = 0.150 m**, read back from `infra_kit.build_curb_line`'s own return (`gutter=False`, so there is no gutter cross-fall term and `gt_drop == height`) and printed by the scene at assembly. **36 unit blocks over 4 chords, measured unit 1.003 m** at `unit=1.0`, `walk_z = 0.0`, `arris="look"` bound to a **curb-class** role (`plaza_light` + tint — S06-B 3. forbids `granite_dark`, which scene01 recorded as *"reads as a black hole"*). The kerb sits at r = 26.0 about C, a = 20…100°, i.e. **28–38 m from the walk axis and 12 m beyond the bowl rim**, outside every judged near-ground cone and occluded from the h0.3 eye by the far balustrade — declared anyway rather than absorbed. Behind it: an 80° carriageway arc at **z = −0.150** with 10 dashed centre markings **on the road**, and two 34 m radial return kerbs closing its ends. **Deleted with it**: the two 90 m `road_lines` paint strips (a marking with no road is not a drop and never was) and v6's 5-post bollard row at `x = −18`, which separated nothing — re-sited onto the kerb as **6 posts at the statutory 1.5 m arc pitch** (`props_kit.build_bollard_v2`; PE-6/PE-7, 교통약자법 시행규칙 별표2 제7호). That relocation is what turns `placement_lint`'s 5 scene08 ERRORs into 0 | 2026-07-31 |
| GT-40 | S6 (`main/scene08_sunken_plaza.py`) | CB-8 · GATE-1 pilot **08** + OCCL re-stamp | `0af6f24` (+ `f8206de` for the albedo and framing riders) | *(rides GT-37's single re-cache)* | **(1) `("patch", 3)` deleted, `relaid` refused with a reason** — a re-laid unit group needs a *cause* and G8 shows a plaza in its first decade with none; converting would have been cheaper than deleting and would have been dishonest. `ground_kit` plaza-plan prims **47 → 43**; the arena plan is 2 in both arms. **(2) The rectangular tactile ring with `gap_tiles=2` is deleted with the rectangle it was drawn on** and replaced by a single **curved stair-head warning arc** at the statutory 0.30 m setback, 0.60 m deep, on the cascade arc only; `cue_tactile` stays **default OFF** (v5.2 user) so this moves **0 prims in the judged arm** and changes only what the ablation builds. **R16-2 honoured — no stop-type device anywhere in this scene.** **(3) `beauty_overview` re-sited `(−12, −12, 9) → (−14, −16, 11)`**, closing `w3_md_reverts_v1.md` §5 **MD-F7** (the eye sat **INSIDE `PlazaPlanter_0`'s footprint, kerb 0.00 m, with a live `Fraxinus.usd` in it** — the C02-P1 class). Fixed as a plan fix with a **gate**, not a nudge: plan distance from every judged eye to every bed, **annular beds in polar** and square beds by AABB, floor 1.0 m; worst pair now `facade_court ↔ Bed_arena_south` **1.800 m**. The polar test is not fussiness — pilot 3's AABB check reported `facade_court` *inside* that bed while the polar test said 1.800 m clear, because the AABB of a 36…52° arc at r ≈ 15 is a ~20 × 12 m box. **(4) `PLACEMENT` declared** (§10.4): `kerb_lines` = the four real kerb chords as literals; `walk_edges` / `anchors` / `routes` **empty with measured reasons** (a 12.0 m plaza ring makes PE-8's 1.5 m effective-width floor vacuous by two orders of magnitude; a radial plan has no single `face_bearing_deg`) — the scene04/scene07 precedent that an empty datum is a finding, not an omission. **(5) Species and season pinned at the call site**: `species="ash"` on every in-bowl tree and `species="ornament_bed"` on every bed, per `SCENE_SPECIES["Scene08"]`; season **late spring / full leaf** from G8, with **no `bare=` call in the file** and a smoke gate on its absence. Census reads `Rhododendron_noflower ×29 · Fraxinus ×8 · Juniper ×2` — **monospecific per bed** (S-2), the three-species scene total coming from `sc.build_planter`'s internal `place_shrubs`, which has **no `species=` kwarg** (K4(c) is signature-preserving): recorded as **S08-F2**, not worked around. **Riders landed at `f8206de` and each measured, not styled**: the stock diffuse maps sit high (`plaza_light` **0.710** · `paving_interlock` 0.554 · `plaza_lower` 0.494 · `stone_flag` 0.476 · `concrete_wall` 0.523 `[measured, 512 px, Rec.709]`) and were tinted onto ~0.40–0.45, the field band for 화강석 판석 and 보도블록; the floor's concentric bands went **1.30 m at 0.710-vs-0.318 → 2.20 m at 0.494-vs-0.306** because pilot 1 read as a bullseye and **a bullseye is a decorative ground pattern as much as a rectangle is**; the balustrade glass went 0.115 → 0.30 because with no transmission in this material stack a laminated panel seen against sky has to be authored as what it reads as; `kind="backdrop"` was **un-forced** so `plan_building`/`should_backdrop` picks the tier (3 in-frame blocks → `office/far` with windows, 5 out-of-frame → auto-demoted). **No walked surface, no hazard box, no drop edge moves in this row** — patch decals are `patch_proud = 0.002 m`, an order below `GT_DELTA = 0.020`; the tactile arc is 0.006 proud and default-OFF; a camera and a tint are not geometry | 2026-07-31 |
| GT-42 | P11 (`main/scene11_footbridge_stairs.py`) | CB-P11 · GATE-1 pilot **11** | `6ef387d` (narrowing) + `15b63e9` (`sidewalk_approach` re-derivation, pilot-measured); declared **before** either at `efafaf0` | **R-1** `NEGOBS_SMOKE=1 python3 scenes/main/scene11_footbridge_stairs.py` — the scene's boot-free self-check, extended with a new **P11 block**: `_zone_of` + `_footway_census` re-derive the footway width from `PARAMS`, classify **42 ground-standing elements** (24 trees split strip/inner by the same `|x| ≥ xe1` test the builder uses for their base z, 2 benches, 4 bollards, 4 lamps, 2 gratings, shelter, stop pole, 2 signs, 2 deck posts) against walk/verge/road/ground at their **AABB extremes**, and assert every ground-level camera eye stands on the paving · **R-2 / R-3** pilot round `260731_w3_p11` under `flock -w 7200 /tmp/negobs_gpu.lock`: `NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 NEGOBS_CAPTURE_DIR=look_check/scene11/260731_w3_p11 python scenes/main/scene11_footbridge_stairs.py` (15 cuts, 57.8 s) → `python3 scripts/regression_check.py --before look_check/scene11/260731_w3_s11 --after look_check/scene11/260731_w3_p11 --json Docs/reports/regr_260731_w3_p11.json` → `python3 scripts/near_ground_stats.py "look_check/scene11/260731_w3_p11/pt_noon_preset_h0.3_*.png" --json Docs/reports/_w3_p11_ngs.json` → `python3 scripts/stamp_round.py look_check/scene11/260731_w3_p11 260731_w3_p11 scene11 --baseline-of-record --compared-against 260731_w3_s11 --note …` · **floor (§6.1)** `py_compile` · `geom_invariance_check.py --scenes scene11` · `placement_lint.py --scenes scene11` · `const_color_audit.py`, and the tree-wide arm in an **isolated `git archive` worktree** with the gitignored asset payloads symlinked (RT-A7) — 10 lanes share this one | **Invariance proved, not asserted**: the scene's entire SMOKE output is **byte-identical to the pre-state except the new P11 block** (`diff` clean over the walking-continuity table, hazards ①②③, the 5.500 m per-tower invariant, both `rot_group` placements, the grid d=2/5/10 standing test, the front profile's 5.510 m maximum, the h0.3 concealment arithmetic, camera collisions 0 and the mise-en-scène ray march). Prim census **3788 → 3788** — a pure translation — geom hash `dfa8409a → 4e85d0a8`; `geom_invariance_check` **33/33** R-4 and R-6 in the isolated arm; `placement_lint` scene11 **ERROR 0 · WARN 19 · BLOCK 1** unchanged and tree-wide **ERROR 21 · WARN 333 · BLOCK 29 · INFO 2**, identical to the K-micro final-HEAD census, so this row adds no violation anywhere. Footway census **42/42 on their allowed zone, 0 carriageway intrusions**. Regression vs the superseded baseline `260731_w3_s11`: **FAIL 5 · WARN 4 · PASS 6**, and the shape of it is the result: **the three h0.3 judged presets PASS with 0 moved blocks** (mean −0.4/−0.2/−0.3, dark 0.5/0.5/0.6 unchanged) and `near_ground_stats` is flat to the second decimal (d2 sd 62.06 → 62.1 · flat 12.57 → 12.49; d5 sd 30.2 → 30.2 · flat 1.40 → 1.40; d10 sd 31.44 → 31.5 · flat 1.69 → 1.73) — **an 18 m walked-surface change is invisible at the robot's judged height**, because at h0.3 the robot stands on the deck and the narrowed ground is behind the tower. Every FAIL/WARN is on a **higher or wider** eye that can see the middle distance: h0.9/h1.8 and `deck_walk` carry FRAME only; `preset_h1.8_d2` additionally carries PHOTO (mean 139.7 → 118.3) because 15.6 m of bright paving per side became grass and the street-tree row moved 18 m closer — the intended change, measured; `overview` FRAME (mean 112.3 → 96.3, dark 24.5 → 26.8) for the same reason. The one **OCCL** is `sidewalk_approach`, whose eye moved 10.3 m: new-dark 8.01 %, blob 5.77 %, yet total dark **fell** 24.0 → 22.9 % — the dark moved, it did not grow, and the smoke's 0 AABB collisions + first-block 1.00 ray march exclude "the camera was swallowed" by coordinate. **No DARK, no BLOWN, no GRAZE anywhere in the round**, so no `EXPECTED_FP` citation was needed. New **baseline-of-record** `look_check/scene11/260731_w3_p11` (`schema round_stamp/v1`, `baseline_of_record: true`, `compared_against: 260731_w3_s11`, `env_source: render_shell_sidecar`, `dirty_paths` 16). Report: `Docs/reports/w3_p11_v1.md` | 2026-07-31 |
| GT-41 | P09 (`main/scene09_ghat_riverfront.py`) | CB-P09 · GATE-1 pilot **09** | `c935f83`, declared **before** it at `a24c156` (§0-1; the id was re-derived live **inside** `flock /tmp/negobs_ledger.lock`, max was GT-40 at that moment) | **R-3 only, and R-1/R-2 are argued rather than skipped.** `python3 scripts/regression_check.py --before look_check/scene09/260731_w3_s09 --after look_check/scene09/260731_w3_p09 --json Docs/reports/regr_260731_w3_p09.json` on the 18-cut pilot round `260731_w3_p09` (`NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0`, under `flock /tmp/negobs_gpu.lock`). **No R-1 owed**: the row moves no hazard box, no drop edge and no walked surface, and the scene's registry is unchanged — but the six boot-free gates were run and printed anyway (`NEGOBS_SELFCHECK=1` rc 0, and again inside `NEGOBS_SMOKE=1 NEGOBS_LOOK_V1=1` rc 0), including the **new `stepstone_selfcheck()`** which asserts the §7.2 permission's five conditions from the shipped coordinates. **No R-2 owed**: the 10 added prims are 12 mm-proud non-colliders 14 m behind the nearest judged eye, so `check_data_run`'s buried / closed_in / offground / nearest-solid tests take no new input. **Floor** (§6.1) in **isolated `git archive` arms** with the gitignored asset payloads symlinked in (RT-A7): `py_compile` OK · `ground_kit.py` 전 항목 통과 · `geom_invariance_check.py` unscoped **R-4 33/33 · R-6 33/33 PASS** on both arms · `placement_lint.py` unscoped **ERROR 21 · WARN 333 · BLOCK 29 · INFO 2 — identical on both arms, 0 introduced** | **PASS, and the ruling's own verification answered “no”.** Regression **18 cuts · FAIL 0 · WARN 0 · INFO 0 · PASS 18 · 0 issues** — `회귀 없음`. Census `[measured, isolated arms]`: scene09 prims **1507 → 1517** (+10, one mesh per slab), hash `46882b0f` → `aed394ad`, **A/B diff exactly one line of the 33-row table, 32 scenes byte-identical**; determinism `PYTHONHASHSEED=1,2,3` → `aed394ad` all three. `placement_lint --scenes scene09` **0 ERROR · 13 WARN · 1 BLOCK, unchanged**. **(1) 판석 디딤돌**: 10 slabs, radius spread 48.1–75.4 mm (gate 40), lawn containment 10/10, deck clearance min **0.147 m** (gate 0.10), tree clearance min **1.34 m** (gate 1.00), proud **12 mm < GT_DELTA 20 mm**; `fov_selfcheck` returns `OUT(전 프리셋 후방)` — the union footprint is behind **all three** h0.3 preset eyes, so the judged near window cannot see them at any distance. In the render they measure **186.0** sRGB against lawn **70.7** and promenade **196.2** — a stone lot, not a decal and not a piece of the paving. Their only frame effect in the whole round is `g9_oblique` `blk_shift` **0.7 %**; 17 of 18 cuts are **0.0**. **(2) tone**: the standing **WHITE FAIL** (`h0.3_d10` 2.1 → 45.4 % in the previous round) is **cleared** — WHITE falls on **all 18 cuts**, `h0.3_d10` 45.4 → **23.9**, worst improvement **−31.3 pp** (`landing_return`). The **drop anchor survived**: GRAZE drop-row step **76.62 → 75.98, ratio 0.992** on `h0.3_d2` (0.995 / 0.996 / 1.001 on the other three graze cuts), against the previous round's collapse to ratio 0.27 — the ratio-preserving 0.818 is what held it, and GRAZE is **not 유보** in this round. **⚠ The band is NOT reached, and the cause is measured, not guessed**: `wht%` **65 → 34–40** against the v5.1 §1 convention of **< 2**, `p95` **218–223 → 213–218** against P1's target of **204**. Solving `f·0.818 + (1−f) = 0.9144` (the measured linear ratio) gives **f = 0.470** — only **47 %** of the judged near-band radiance is albedo-driven, so tint alone cannot reach the band. The remaining lever is the specular term: `LOOK_CLASS["asphalt"]` states `spec=0.20` for this exact diagnosis and `LOOK_CLASS["stone"]` states none, so OmniPBR's default 0.5 / F0 0.04 survives on every flagstone in the library (the v8 Y1 mechanism, applied to the road and never to the stone). Routed as **P09-F1** to Lane-1 / K4 — library-wide, not a scene defect. New baseline-of-record **`260731_w3_p09`**; `look_check/README.md` §4 and `look_check/INDEX.md` are **owed and NOT taken by this lane** (RT-A2 class, flagged as **P09-F3**) — those files are frozen to K-micro this window | 2026-07-31 |
| GT-45 | S1 (`main/scene20_diagonal_oblique.py`) | GATE-1 pilot **20** | `1a122a5` (BS-4 + C6 + re-site) + `ca2edb5` (ground-plane correction + belt) + `c30b65c` (stain rebind, material only) `[SHAs corrected in place — the first fill quoted `20c5cf1` / `8b8c452`, which are the **tree** HEADs the round stamps recorded, not this lane's commits; ten lanes were pushing between the rounds]` | **R-1** `NEGOBS_SMOKE=1 python scenes/main/scene20_diagonal_oblique.py` — the scene's new `plaza_selfcheck()` re-derives and **prints** the hazard/collision registry from `PARAMS` and fails the scene loud on six gates (prop interpenetration = 0 · judged-eye↔bed ≥ 2.50 m · G-4 reject-only occupancy · backdrop ridge < z_ceil · ground-plane containment · season audit). **R-2 not owed** (class A, no walked surface moves). **R-3** round **`260731_w3_l20c`** (13 cuts, PT, under `flock -w 7200 /tmp/negobs_gpu.lock`, arm byte-identical to the baseline stamp: `NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`), then `python3 scripts/regression_check.py --before look_check/scene20/260730_w2d_fix --after look_check/scene20/260731_w3_l20c --json Docs/reports/regr_260731_w3_l20.json` | **Registry (R-1)**: drop boundary still the 30° diagonal `x = −0.5774·y` carrying **2.10 m** over 14 × 0.150 m risers; `UpperPlaza` / `UpperWedge` / `Stairs` / `LowerPlaza` / `Valley` / `AccessRamp` top faces **unchanged** — printed, not asserted. Collision boxes that moved: **8** bollard bodies (r 0.075→0.055 · h 0.90→0.85) + **12** planter kerbs (plan) + 3 near shells → 4 far shells. Gates: interpenetration **4 → 0** · judged-eye↔bed **0.450 → 2.750 m** · both derived chambers outside every judged frame · sky above roofline **4/4** · ground-plane escapes **0**. **Prims** 480 → **535**, hash `145593c0` → `472137ec`; `geom_invariance_check` unscoped **33/33 R-4 + R-6 PASS**; `placement_lint --scenes scene20` **ERROR 0 · WARN 8 · BLOCK 1 · INFO 1 — identical to the HEAD arm** (LINT-2 does not fire on the new belt). **R-3 result**: **FAIL 2 · WARN 11 · PASS 0 · EXPECTED_FP 0** — every FAIL and every WARN carries **[FRAME]**, the declared composition change (the horizon opening moves 19–42 % of blocks). **DARK / BLOWN / WHITE / OCCL do not fire on any of the 13 cuts** (new-dark ≤ 0.5 %, largest blob ≤ 0.1 %). **3 GRAZE flags (`preset_h0.3_d2` FAIL · `preset_h0.3_d5` and `low_grazing` WARN) are 유보 — photometry moved**: the detector's own text says it cannot confirm automatically and asks for the band to be cropped, and the crop (`Docs/reports/_w3_l20_crops/3_graze_bands.png`, cut at the detector's own rows) shows the plaza, the diagonal drop edge and the railing **pixel-identical** between arms — what changed inside the edge band is the *background behind* the drop line (a dark brick wall at 9.5–26 m became sky + a far silhouette + an elm belt), which is exactly the contrast the GRAZE statistic measures. Re-evaluates automatically at the first same-arm successor round (the S08/S13 precedent). **Attribution**: `260731_w3_l20b → _l20c` (same pipeline, stain rebind only) **FAIL 0 · WARN 0 · INFO 4 · PASS 9**, so the material fix is contained and the whole delta above belongs to the declared geometry. **`260731_w3_l20c` is scene20's baseline-of-record from here** — marked on its own stamp with `compared_against`; `260730_w2d_fix` and this lane's two intermediates are stamped `superseded_by`. | 2026-07-31 |
| GT-49 | L15 | — | `8ba2281` | **R-1** `NEGOBS_SELFCHECK=1 python3 scenes/main/scene15_alley_labyrinth.py` — the scene's **new** `alley_selfcheck()` (boot-free, GPU-free; scene15 previously had **no self-check of any kind**). **R-3** two isolated `git archive` arms rendered back to back inside `flock -w 7200 /tmp/negobs_gpu.lock`, same PT_FAST channel (`NEGOBS_CAPTURE_MODE=pt · PT_FAST=1 · LOOK_V1=1 · DETAIL_SCALE=2 · DETAIL_ROUGH_GAIN=0`, gitignored asset payloads symlinked in per RT-A7): arm `7fb3b34` → `look_check/scene15/260731_w3_l15_pre` (13 cuts, 56.3 s) · arm `8ba2281` → `look_check/scene15/260731_w3_l15` (13 cuts, 51.1 s); `scripts/stamp_round.py --capture-env <out>` called **from the render shell**, then `scripts/stamp_round.py <out> <round> scene15 --baseline-of-record --compared-against …_pre --note …`; then `python3 scripts/regression_check.py --before look_check/scene15/260731_w3_l15_pre --after look_check/scene15/260731_w3_l15 --json Docs/reports/regr_260731_w3_l15.json`. **R-2 declined in the row and not run** — class A, reason recorded there and in `w3_l15_v1.md` §8.1 | **R-1**: registry re-derived and printed — drop edge `x = 0.000`, `flight1` 12 × 0.170 = 2.040, landing −2.040, `flight2` 13 × 0.170 = 2.210 past the 25° bend, lower alley −4.250; **total drop 4.250 m and all four top faces invariant**, asserted not narrated. **17 gates, 17 PASS**, including the five container/crown clearances against **derived** facade planes (+5 / +10 / +25 mm containers · +16 / +100 / +120 mm worst-case crowns — the pre-state was **−20 mm**, i.e. interpenetrating, L15-F1), the four manhole clearances (U 측구 +301 · grime band +426 · patch#1 +1433 · 줄눈 JX +76 mm) with d5 frame width **23.4 %**, the summer species pin (reachable species ∩ {Rhododendron, Forsythia, Burning_Bush} = ∅), and the tint's luminance identity (Rec.709 Y **0.115250 → 0.115253**). **R-3**: **FAIL 0 · WARN 2 · EXPECTED_FP 0 · INFO 3 · PASS 8**. WARN `beauty_overview` **FRAME 30 %** = the intended output (that frame is ~40 % roof, and **white % falls 15.28 → 1.96**, a factor of 7.8); WARN `narrow_up` DARK+PHOTO (mean 23.2 → 17.3) adjudicated as the arithmetic consequence of retiring roofs whose albedo (0.3545 / 0.4215) was **above `ALBEDO_CAP = 0.30`** — a non-judging mise-en-scène cut that was already 70.8 % dark in the pre arm, remedy filed as an owed composition item, **0 lighting parameters touched**. The two `CAPTURE` INFOs are `capture_pipeline`'s 40-update size poll, both frames opened and verified complete at 1920 × 1080. The **h0.3 judging band is invariant** (mean −0.5 / +3.4 / −0.2; `near_ground_stats` sd +0.1…+0.6, flat % ≤ +0.02 pp). Geom **433 → 438 prims**, hash `3a0f63a2 → 2e4569a7`, R-4/R-6 3-arm identical; `placement_lint` ERROR 0 · WARN 1 · BLOCK 0 · `patch=2 stain=6` **unchanged** (R15-1 held: 0 patches and 0 weeds deleted). New baseline of record **`260731_w3_l15`**, superseding `260730_w2d_fix` (which predates CB-2 and still ships pre-A1 cube weeds). Full write-up: `Docs/reports/w3_l15_v1.md` | 2026-07-31 |
| GT-48 | L21 (Lane-3 3.5) | GATE-1 pilot **21** | `d462cfc` (declaration) + `7fe6d8c` (geometry) + `90e90fd` (pilot fix — the rendered baseline) | **R-1** `NEGOBS_SMOKE=1 python3 scenes/main/scene21_monumental_selfocclude.py` — the scene's new `_l21_selfcheck`, boot-free and GPU-free: it re-derives the frozen hazard geometry, the judged-eye ↔ planting census over 13 cuts × 14 beds, the BS-4 frame-ceiling arithmetic per block and the C6 statutory band from the changed `PARAMS`, prints them, and exits non-zero on any failure. · **R-3** two isolated `git archive` arms under `flock -w 7200 /tmp/negobs_gpu.lock`, channel `NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`, `NEGOBS_VIEWS` unset: `260731_w3_l21_pre` (arm `d462cfc`, scene21 UNEDITED = attribution) and `260731_w3_l21` (arm `90e90fd`), 13 cuts each; `python3 scripts/regression_check.py --before look_check/scene21/260730_w2d_fix --after look_check/scene21/260731_w3_l21 --json Docs/reports/regr_260731_w3_l21.json`; `python3 scripts/near_ground_stats.py 'look_check/scene21/260731_w3_l21/pt_noon_preset_h0.3_d*.png' --gate`; `python3 scripts/stamp_round.py look_check/scene21/260731_w3_l21 260731_w3_l21 scene21 --baseline-of-record --compared-against 260730_w2d_fix`. · **R-2 not owed** (class A). | **R-1**: `_l21_selfcheck` **14 PASS · 0 FAIL**; the frozen identity re-derives to **2.700000 m** over 18 × 0.150 at tread 0.320 / width 8.0, and the 300-prim non-touched core is unchanged. **Prims 526 → 559 (+33)**, inventory hash `3c0105cb` → `35ff369a`, **R-4 1/1 · R-6 1/1 PASS** scoped and **33/33 · 33/33** unscoped in an isolated arm at `90e90fd`. `placement_lint --scenes scene21` **ERROR 0 → 0 · WARN 4 → 7 · BLOCK 1 → 1** — the three new WARNs are LINT-1/2/3, all `nodata` (the scene has trees now and still no `PLACEMENT` block; L21-F3). BS-4 acceptance printed at assembly: **sky above roof 3/3**, `ridge < z_ceil` by +0.577 / +0.660 / +0.585 m at `d_true` 50.00 / 54.15 / 56.46 m, against a pre-state of **+10.31 / +7.27 / +11.62 m OVER** the ceiling. **R-3 baseline**: `260730_w2d_fix` → `260731_w3_l21` = **FAIL 10 · WARN 2 · INFO 1**, **every FAIL and WARN carries `FRAME`** (block shift 38–68 %, the declared expected result of deleting 212 prims from the upper frame). **DARK improves on 12 of 13 cuts** (`h0.3_d5` 2.11 → 0.63), **BLOWN 0.0000 on 12 of 13** (the remaining 0.0036 % on `facade_front` is pre-existing and identical in the baseline), WHITE falls on 12 of 13 (`h0.3_d2` 12.30 → 2.18), **no `OCCL` code on any cut**. **3 `GRAZE` flags, all adjudicated NON-DEFECT** by crop (`Docs/reports/_w3_l21_crops/l21_graze_band_*.png`) **and by a two-band measurement**: on the severe cut (`h0.3_d5`, tool step 12.1 → 84.0) the **walked** side of the drop row moves **−0.4 LSB** while the **background** side moves **−50.6 LSB**, i.e. the step is across an unmoved line whose two sides now differ in tone — the concealment is intact. `near_ground_stats` on the h0.3 band is flat to < 1 % on every column (sd 39.2 → 39.3 / 30.6 → 30.7 / 39.5 → 39.6), the numeric twin of "no walked surface moved". **Attribution arm rendered and NOT null**: `260730_w2d_fix` → `260731_w3_l21_pre` (scene21 untouched) already scores **FAIL 1 · WARN 3**, all `FRAME`, so the Lane-1 + FANOUT-A + K-micro window is quantified before anything is attributed to this lane. Stamps: `260731_w3_l21` `baseline_of_record: true` (`compared_against: 260730_w2d_fix`), `260730_w2d_fix` flipped to `false` + `superseded_by`, keys only. Report `Docs/reports/w3_l21_v1.md`; **9 findings handed on (L21-F1…F9)**, of which **L21-F1 (MED)** is an undeclared unguarded **2.75 m** terrace-flank drop that this row deliberately does not touch. | 2026-07-31 |
| GT-46 | P03 | — | `639e212` | **R-1** `NEGOBS_SELFCHECK=1 python3 scenes/main/scene03_riverbank.py` — the scene's own `river_view_selfcheck` + `river_width_selfcheck`, boot-free and GPU-free, re-derived off the changed geometry. **R-2** `python3 scripts/run_data_render.py --run 260731_s03_recache --scenes scene03 --conds L0,L7,L5 --cams 4 --seed 20260730` then `python3 scripts/check_data_run.py 260731_s03_recache`. **R-3** `flock -w 7200 /tmp/negobs_gpu.lock bash scripts/rounds/run_260731_w3_p03.sh` (16 cuts, PT_FAST, `LOOK_V1=1 · DETAIL_SCALE=2 · DETAIL_ROUGH_GAIN=0`) then `python3 scripts/regression_check.py --before look_check/scene03/260731_w3_s03 --after look_check/scene03/260731_w3_p03 --json Docs/reports/regr_260731_w3_p03.json`. Floor, in an **isolated `git archive` arm** (10 lanes share this worktree): `python3 -m py_compile scenes/main/scene03_riverbank.py` · `python3 scripts/geom_invariance_check.py --scenes scene03` · `python3 scripts/placement_lint.py --scenes scene03` · `python3 ground_kit.py` | **Landed as declared on the quantity that mattered: the drop edge did not move.** **R-1 green** — `NEGOBS_SELFCHECK=1` prints 사행 OK · 강폭 OK, and `meander_air` 40/131 · `bank_oblique` 26/119 occlusion are **identical to the S03 arm**, so the pergola relocation cost neither judging cut anything. `geom_invariance_check` prims **1901 → 1977** (+76, fully attributed: `river_band` emits 1 rot group + 1 slope box per seg × 19 segs — LeveeRoad 1×19×2 = 38 out, CrestWalk 2×19×2 = 76 in, CrestBand 1×19×2 = 38 in), hash `2bc75d66 → e9c1449a`, **identical across all three arms** so R-4 and R-6 both PASS. `placement_lint` exit 0 with the severity profile **unchanged** (13 WARN · 1 BLOCKED · 0 ERROR before and after) — a full text diff of the two arms' output differs on **exactly one line**, the prim count. `python3 ground_kit.py` all pass. **R-2 green** — `check_data_run.py 260731_s03_recache` → **DATA RUN CHECK PASS**, 12 cuts (L0 · L7 · L5 × 4 cams), all five checks, 2.32 s/cut against SP-3's 2.87. R-2 was taken rather than argued away because the walked surface changes **class** (gravel + turf → unit paving) and gains 1.400 × 95.0 m of extent, which is exactly what the data channel reads. **R-3 re-stamped**: 16 cuts, **FAIL 4 · WARN 1 · EXPECTED_FP 0 · INFO 2 · PASS 9** — against the S03 round's FAIL 14 · WARN 2 · PASS 0 on the same instrument. **Photometry never fired**: no DARK, no BLOWN, no PHOTO on any cut; **OCCL new-dark 0.00 % on 13 of 16 cuts**, maximum anywhere `river_along` 0.67 % new-dark / 0.17 % blob, and the three h0.3 judge cuts are 0.00 / 0.00 / 0.00 %. Three FRAME FAILs + one FRAME WARN are the composition change this row *is* (`d_mean` **−8.98 at h0.3_d2**, paving darker than the gravel it replaced, and **+19.14 at h0.3_d5**, paving brighter than the lawn it replaced — the two opposite signs are what the geometry predicts, cut by cut). **GRAZE `preset_h0.3_d10` adjudicated NON-DEFECT** with the tool's own discriminators and pixel evidence: `gz_row` **166** vs `gz_haz_row` **149** → `gz_step_off` **17 > ROWTOL 4**, i.e. *"a different object in the E band"* in the tool's own words; `gz_step_dom` **1.47 < 3.5**; `newdark` **0.00**. Row-band profile with each row mapped to a world x: **everything beyond the drop (rows 120–148) is unchanged at ratio 0.998**, the max-change row is a **brightening** at x ≈ −4.6 (y170 **93.5 → 160.4**) which is precisely the 1.4 m turf strip this row converts to paving, and the mandated visual crop (`_w3_p03_crops/graze_band_h03_d10.jpg`, rows y124–177/540) shows the shoulder line and its 1.0 m grass shoulder **unbroken across the full frame width in both arms**. **One real consequence is declared rather than absorbed**: the crest→beyond luminance contrast at that shoulder falls **67.8 → 47.7 (−30 %)** because the crest is now mid-tone paving instead of near-white gravel. That is the *reduction of an accidental cue*, not of a declared one (this type's drop evidence — water, far bank, crowns below eye height — is untouched, water screen area identical), and it moves the render toward G3; **flagged for the supervisor, not decided by the lane** (`w3_p03_v1.md` §8-2). **The S03 tone item §7-3 is closed at its cause and measured**: `h0.3_d2` B30 `wht%` **39.1 → 8.6**, B45 `>224%` **5.06 → 0.34** (back inside its ≤5 gate), `σ_LF` **0.94 → 3.11**, `mean` 194 → 178, `sd` 22.6 → 25.8, `p99` 232 → 219. Mechanism measured at the texture, not asserted: `gravel_diff` luminance p99 **215.4** / >204 **3.56 %** against `paving_interlock_diff` **173.6** / **0.09 %** at the same 0.28 mean albedo — the near-white field was the gravel scan's highlight tail. The paving lands at luminance **179–181 against G3's own promenade at 177–184** `[ref, measured]`, so the `mean ≤ 170` gate miss is the reference photograph's miss too and **the tint was NOT tuned down to pass it**. The residual `wht% 8.6` is re-attributed from albedo to **specular** by a pixel test: the >204 set is desaturated toward the illuminant (saturation **0.140** vs **0.232** overall, B/R 0.860 vs 0.781) — filed to T1 with a handle instead of as an unanswerable albedo question. **S03's region-restricted-scatter ask is withdrawn as scene03's blocker** — no `gravel`-bound prim falls in any h0.3 near window any more (d2 x −1.50…−0.30 and d5 −4.50…−3.30 are wholly inside the paved band; d10 is turf in both arms). **New baseline-of-record `260731_w3_p03`**, stamped with `baseline_of_record: true` and `compared_against: look_check/scene03/260731_w3_s03`; env captured **inside the render shell** (`env_source: render_shell_sidecar`, K-micro item 10) | 2026-07-31 |
| GT-47 | P03 | — | `639e212` · `3d9f8e4` (P03-F2) | *(rides GT-46's single re-cache — same commands)*. The two items that needed R-1 to **prove** a move rather than an absence: the pergola AABBs (`x0/x1 −8.000/−5.000 → −8.800/−5.800`, verified by the unchanged judging-cut occlusion above — the move cost `meander_air` and `bank_oblique` nothing) and the ground-plan region, whose CPU A/B on `plan_ground` reads **prims 17 → 17 · elements 17 → 17**. Assembly log: `[ground_kit] scene03 P13(paved crest · no urban infra) · prims 17 + edge_break 1 · delta_max 0.0000` | **One clause of this row's §3 text is corrected here rather than left to be discovered.** The row said the region change puts *"every stain on paving"*. Measured: with the old 12 m region **4 of 8** stain lobes were centred at x ≤ −6.254, on mown grass; with the new region **1 of 8** still is — the lobe spanning x[−5.358, −4.812], which *straddles* the band's outer edge at −5.400. A dirt stain lapping from turf onto a paving edge is correct, so the geometry is right and the wording was absolute where the measurement is not. **P03-F2, found on the pilot's first pass and fixed before the round was kept**: the two `stain` kinds were bound to `dirt_park` and `concrete_dark`, which were right against gravel and wrong against 점토블록 — measured on `pt_noon_levee_walk.png`, the `concrete_dark` water lobes rendered sRGB **(202,185,160) against paving at (199,181,156)**, i.e. **lighter than the surface they soil**, flat and untextured (they read as spilled cement), and the `dirt_park` lobe read as a heap of loose gravel on the blocks. Both are now derived from `paving_tint` (wet ×0.70 → albedo 0.148 · soil ×(0.78,0.70,0.56) → 0.161) and keep the block pattern showing through, which also removes the decal read. **Proof it is material-only**: `geom_invariance_check` reads prims **1977** · hash **`e9c1449a`** before and after the fix, byte-identical. The pilot was therefore rendered **twice** and `w3_p03_v1.md` §2.4 says so. **Ablation-arm integrity, the row's substantive item, landed as declared**: `cue_material_break=False` and `build_flat_fill` both followed the crest instead of a literal `gravel`, so neither control arm acquired a material break the paving would otherwise have smuggled in — a defect the judge channel could never have caught, because it never renders those arms. **Fixture drift declared and routed**: `SCENE_PLANS["scene03"]`'s mirrored fields (`surface` / `extras` / `extras_args`) are **byte-identical** after this round, so they do not drift; `pave` and `region` are not mirrored by that fixture and are already in §12-1's residual list, which this round widens — kits are frozen, so it is routed to `ground_kit`'s owner. Same for `ground_kit.py:3167-3170`'s comment (*"scene03 forces module=(None,None) because a 둔치 levee is not laid in blocks there"*), which GT-46 makes false | 2026-07-31 |
| GT-50 | S6 (L19) | CB-9 successor | `09c2d36` (geometry) · `42122cc` (report) | **R-1** `NEGOBS_SMOKE=1 python scenes/main/scene19_fan_winder.py` — the scene re-derives and prints its own geometry report from the changed geometry, and the **split proof runs inside it** (`_arc_split_proof`, GPU 0, 0.6 s, new this commit): walked-top-face sampling on a 57 x 3601 polar grid over r 1.10…4.10, az −4…94°, evaluating **both conventions from the same `PARAMS`** and taking the max against every other solid that bids for the same (x, y). Total drop re-printed **1.80 m** invariant; eye burial 0; `roof_skyline` E동 38.9 %; `radial_nosing` 단 83.7 % / 12 단 / 백색 0.0 %; `lower_lookup` 단 87.7 % / 7 단 / 백색 0.0 %. **R-3** round **`260731_w3_l19`** (16 cuts, PT, **56 s**, `flock -w 7200 /tmp/negobs_gpu.lock`, arm byte-identical to the baseline stamp: `NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`), then `python3 scripts/regression_check.py --before look_check/scene19/260730_w2d_fix --after look_check/scene19/260731_w3_l19 --json Docs/reports/regr_260731_w3_l19.json`. **R-2 OWED AND NOT TAKEN** — recorded as an open obligation, not quietly dropped: the per-riser nosing azimuth moves by up to **63.78 mm of arc at r_in**, above `GT_DELTA`, so GT-29's below-threshold exemption does not transfer. `scripts/run_data_render.py --run <id> --scenes scene19` + `scripts/check_data_run.py` remain outstanding. **By ledger §0-3 this row is therefore not fully closed**, and it says so rather than claiming a green it does not have. | **Split proof: of 205,257 samples the walked surface moves in 17,019 (8.29 %), and every one of them is a single stratum — `−183.333 mm` exactly, one riser.** `new-void 0 · new-solid 0`. **No tread's own z moves**: the ladder (−0.150 x3 kite, then 9 x 183.333 mm to −1.800) is bit-identical and the **total drop 1.800 m is invariant**; what moves is which azimuth belongs to which tread. Attribution: **9 hand-over boundaries, 3\| (22.5°) … 11\| (82.5°)**, 1,869–1,921 samples each. **Boundaries 1\| and 2\| contribute 0** — the merged kite landing, riser 0.000 m: the negative control proving the probe measures the hand-over and nothing else. **The a0 = 0° and a1 = 90° ends contribute 0** — the box overshoot there falls inside `Wall_south` (y −1…0) and `Wall_west` (x −1…0), both `z_top` 3.5, so it can never win a top face; GT-29 had to declare this term for scene06 and here it is **proved absent**. Outer arc retracts **1.010 mm** (box corner bulge → true ray), inner radius unchanged at the mid-ray — both an order below `GT_DELTA = 0.020`, **no drop edge created or destroyed**. **Unscoped invariance**, isolated `git archive` arms with assets symlinked: HEAD `9df8f0c` scene19 **284 / `4ac6372a`** → **292 / `3f67f1d5`**; `4ac6372a` / 284 **reproduces GT-29's own recorded value for scene19**, an independent check that the arm is honest. The **+8 is GT-51's**, attributed prim-by-prim (§2.5 of the report); GT-50 itself is Cube→Mesh at 1:1 on 62 prims. **Floor**: py_compile ✔ · SMOKE **rc 0**, `prims=275`, `ground_kit δmax 0.0023` · `geom_invariance --scenes scene19` **R-4 1/1 · R-6 1/1**, hash identical across MTL=0 / MTL=1 / V1=1 · `placement_lint --scenes scene19` **ERROR 0 · WARN 7 · BLOCK 0**, **identical to the HEAD arm** (both measured). **Baseline**: `260730_w2d_fix` named per `look_check/README.md`; **`260731_w3_l19` is scene19's baseline-of-record from here** (stamped, `baseline_of_record` marker set, `env_source: render_shell_sidecar`, `dirty_paths` listed and containing **no tracked file**). Regression **FAIL 3 · WARN 2 · EXPECTED_FP 0 · INFO 2 · PASS 9**, adjudicated per cut in `Docs/reports/w3_l19_v1.md` §5.3: all three FAILs are **FRAME** on declared composition changes; the single **OCCL** WARN on `roof_context` is **rejected** on blob **0.77 %** against a smoke camera-burial count of **0** (S06 rejected the same hint at 2.2–3.7 %); **GRAZE abstained and is NOT recorded as a pass** — photometry moved on this scene, so GRAZE stays **유보** for scene19 and re-evaluates at the first same-arm successor round. **Attribution is separated rather than assumed** (GT-25 precedent): a third round `260731_w3_l19_pre`, same pipeline on an isolated arm at `9df8f0c`, gives baseline→pre **FAIL 0 · WARN 5** with **three cuts bit-identical** (Δmean 0.02–0.17 LSB), so the headline delta is this commit and not nine lanes of drift. | 2026-07-31 |
| GT-51 | S6 (L19) | CB-9 successor | `09c2d36` (geometry, same commit) · `42122cc` (report) | *(rides GT-50's single re-cache — ledger §0-2, one re-cache per scene per batch; same commands)* | **No walked surface, no drop edge, and the movements that DO occur are enumerated rather than absorbed**: 8 collision-box AABBs rise **100 mm** (7 `Parapet_i` + `EdgeGuard` — verified `Parapet_3/Seg_0` mesh extent z `−0.4333…+0.7667`, `EdgeGuard` top `1.000 → 1.100`) and 4 `Planter_A/Curb_*` boxes rise **450 mm**; all are guards and containers, none a walked top face. The plinths, the four urban scans and the PH boxes are `collider=False` and enter no hazard list. `patch_proud` **0.002 m**, two orders below `GT_DELTA`. Prims **284 → 292** / `4ac6372a → 3f67f1d5`, attributed prim-by-prim in the isolated-arm inventory diff: **−2** `GKit/Patch/Patch_2·3`, **+2** `Hvac_*/Asset`, **+2** `PlantBase_*`, **+2** `Plant_*`, **+2** `Plant_*/Asset`, **+2** `Planter_A/Shrub/Sh_2` + `Sh_2/Asset`. **N-A3 live confirmation** from the SMOKE run: `[옥상 설비] N-A3 실측 스캔 4/4점 · treatment=mtlxoff · z_mode=base · instanceable`; three wrapper layers generated and committed. **Declared divergence** from N-A3's literal `ac_unit_04` with the measurement that drove it (3.604 x 4.203 x **1.985** m; every legal siting puts a 2.105 m mass **0.2 m above** the `roof_context` eye at z 1.9, clearance **0.15 m** on the ray to the crown) — GT-25's declare-in-advance precedent, not a discovery in a diff. **Planter** verified in the arm diff: `Planter_A/Veg` → `(5.38, −6.18, 0.75)`, scale **0.996071**, `Chinese_Juniper.usd` (was `(6.0, −6.8, 0.40)`, scale 0.616683, `Fraxinus.usd`); crown top **3.2565 m** against a declared bound 3.30. **`Rhododendron` count in scene19 is now 0**, so **K4-F1's library-wide magenta loss cannot appear here** — declared, not discovered. **19-4**: the 덧방 measures **L 185.4** against the adjacent deck **L 178.0** = contrast **1.041**, i.e. present but not a stencilled plate; `cutline=False` is the kit default and `apply_ground` never overrides it, so **no saw-cut line is built at all**. **Season pinned `summer`** from G8 and **asserted** by a new `_season_audit()` that fails the build on a deciduous pinned tree, a multi-species bed role, or any `SEASONAL_SUBPRIMS` shrub. Judged-eye × planter census **re-measured, not cited**: nearest judged eye still **4.49 m** after the bed doubled in height. | 2026-07-31 |


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
- **W8 · sceneN2's z ladder now reads 8 rungs, and no GT value changed.** `[supervisor ledger
  batch 07-31 · §9-5 — source `w3_n2_clean_v1.md` §7-1 and its §7 adjudication]` The N2-CLEAN
  commit `ec76030` introduces a longitudinal cold joint (종방향 시공이음) at `y = −2.80`, 5.0 m
  long, 0.05 m wide, one prim, at **`seam_proud = 0.0023`** — a **new z level on a walked
  surface in a hard-negative scene**, which is why it is written down. It is **inside** the
  convention: `GT_DELTA = 0.020` (`ground_kit.py:122`) and the rung lands between the existing
  패치 **0.0020** and 맨홀 **0.0026** rungs. The scene asserts the ladder rather than commenting
  it: `줄눈 0.0006 < 도색 0.0010 < 실란트 0.0012 < 패치 0.0020 < 시공이음 0.0023 < 맨홀
  0.0026/0.0032/0.0038` — **strictly increasing, 8 rungs where the ledger's reader would
  previously have counted 7**. **No GT value changes, no row is created and no re-cache is
  owed**; sceneN2's baseline-of-record is `260730_w3_n2clean` (the scene's latest judgement
  round in its scene root, per `look_check/README.md` §2 — no README chain edit needed).
  Recorded here because §3 carries no N2 row to hang it on, not because anything is pending.
- **W9 · `SCENE_PLANS` fixture drift — a live census hazard, five instances, routed to the
  FINAL SWEEP.** `[supervisor watch item 07-31 · SB closure batch §11 SB-6 — source
  `w3_mb_patch_v1.md` §2/§9 **MB-F2**, extended by this batch's own measurement]`
  `SCENE_PLANS` is a **self-check fixture**, and its stated doctrine (v1.4) is *"Now mirrors the
  wired call"*. Five fixtures no longer do: **scene16 · scene09 · scene18 · sceneC2** (MB-F2, the
  drift that produced MB-F1) and **scene03** (found by this batch while scoping GT-24's
  `levee_paved` extension). Each omits the `overrides=dict(surface=…)` its scene file actually
  passes, so **a census taken from `ground_kit.py` alone cannot see the override** — which is
  exactly how GT-24 came to declare 15 in-scope scenes when 11 were reachable. The drift is
  **measurable, and both halves of it are now measured**: on the three-profile sweep the fixture
  dry run moved **1170 → 1149 (−21)** while the real scenes moved **−14**, the 7-prim gap
  decomposing exactly onto scene18 1 · scene09 2 · scene16 2 · sceneC2 2; on the `levee_paved`
  extension the fixture dry run moves **1149 → 1141 (−8)** while the real library moves **−4**,
  and the 4-prim gap lands entirely on **scene03**, whose fixture still carries the profile's
  `("patch", 4)` while the scene overrides to 8 of its own. **Not fixed by this batch, and the
  reason is the batch's own rule**: repairing five fixture rows is a different edit with its own
  prim numbers and its own declaration, and this closure was authorised for **one tuple** in
  `ground_kit.py`. The exact replacement rows for 16 · 09 · 18 · C2 are written out in
  `w3_mb_patch_v1.md` §10; **scene03's must mirror `scene03_riverbank.py:900-916`**, i.e. add
  `surface=(("patch", 8), ("stain", ("dirt", "water")))` and `extras=(("wear_lane",
  dict(width=0.90)),)` to the fixture's existing `overrides=dict(natural=True, infra=None)`.
  Owner **Lane-1 / `ground_kit`**; **the dry-run prim total changes when it lands and must be
  declared**, per §0-1. Until then the rule this watch item exists to enforce: *no row may take a
  scope figure from `SCENE_PLANS` without reading the scene file that carries the profile.*
  **LANDED — `[K-micro 07-31 · §12-1]`.** All five fixtures synced; dry-run geometric prims
  **1137 → 1109 (−28)**, scatter instances **670 → 670**, per-scene decomposition and the
  `ast` proof that all five `surface=` literals now match their scene files are in **§12-1**.
  **This bullet's own scene03 replacement text is superseded**: it prescribes
  `surface=(("patch", 8), ("stain", …))` from `:900-916`, but FANOUT A's S03 rebuild deleted the patch
  row, and the landed fixture mirrors the file at `4bae470` instead. The `region` / `edges` /
  `origin` / sceneC2 `infra`+`pave` / scene09 `pave` residue is **not** closed and the rule in
  the sentence above stays in force for it.
- **W5 · GT-6 has two gates, one proof.** The builder change lands in CB-5 (`scene_common`, K4-d)
  and the scene cut lands in CB-9 (S4, blocked on T3). The invariance proof belongs to whichever
  lands first and must be **re-run** at the second — 05 · 19 · 13 share the builder and are not in
  CB-9's pilot set.

---

## 8. Append template

Copy, fill, append to §3 (and to §4 at land). Delete nothing.

```
| **GT-nn** | <scene(s)> | <change, with the numbers> | <z-profile effect; say "no walked-surface
| **GT-37** | 08 | **FULL CURVED REBUILD — the rectangular pit is deleted and a circular bowl replaces it** (`w3_intake_v2_images.md` **§7-2** *"scene08 curved rebuild — AUTHORIZED IN FULL (bowl, parapet, tiers, paving bands, ring decks per G8)"* + §2 scene08 (b)/(d)/(g) **R08-1**; user 2nd review *"Scene8 Sunken 「광장」인데 광장 느낌이 안나네.. 좀 더 곡선 구조로 제작해주면 좋겠어"*). **Pre-state** `[repro, HEAD e4862aa]`: `pit=dict(x0=0.0, x1=12.0, y0=−4.5, y1=4.5, floor_z=−4.498, ring_t=0.4)` — a 12 × 9 m rectangle, drop edges at `x = 0` / `x = 12` and `y = ±4.5`; two straight flights `build_straight_stairs` in ±90° rotation groups at `x 0…4` and `x 8…12`, riser **0.173** × 26, tread 0.300, width 4.0, **no landing**; plaza slab a 40 × 30 rectangle in 4 boxes; ground frame 4 asphalt boxes at `z −0.15`. **Post-state**: bowl centre **C = (14.0, 0.0)**, rim radius **14.0** (near rim on the walk axis at `x = 0` — *unchanged*; far rim `x = 28.0`, was 12.0), floor **z = −4.500** (was −4.498), arena disc **r ≤ 4.10**. Four angular sectors about C, every one built from **K4(d) annular-sector meshes** (`build_arc_steps(seg=1, mesh=True)`): **cascade 150…210°** — 29 built courses + a **1.20 m mid landing** at −2.250, riser **0.150** / tread **0.300**, 30 risers = 4.500, r 14.0 → 4.10; **tier bank 90…150°** — 11 timber seating courses riser 0.375 / tread 0.900, r 14.0 → 4.10; **arcade 210…270°** — forecourt floor r 4.10 → 17.0 at −4.500 under a ring deck whose edge is the rim, 6 columns at r 14.60, wood-slat soffit at −0.80; **control wall 270…450°** — a plain curved retaining wall r 13.4 → 14.0, `bank_base −4.90` → 0.0. Upper plaza is now an **annulus r 14.0 → 26.0** (16 sectors, thickness 0.80) with 4 concentric paving bands; the surround is an annulus r 26.0 → 60.0. **Sector angles are a judgment constraint, not styling**: at h0.3 the graze cone falls only 0.15 m/m, so a *stepped* bank that is both inside the 30° half-frame and above `z = −0.15 x` announces the depth — the scene's own smoke run scans every bowl point at 1° × 0.10 m and gates on **0** such points | **Every drop edge in the scene moves.** Near rim stays at `x = 0` (the one quantity deliberately preserved, because the h0.3 grid is defined against it); far rim `x 12.0 → 28.0`; floor `−4.498 → −4.500`; the two 4.0 m-wide straight flights (26 × 0.173) are **deleted** and replaced by one 14.65 m-wide radial cascade (30 × 0.150 + landing) plus an 11-course seating bank; the arcade forecourt at −4.500 is new walked surface. Concealment re-derived and **still holds with margin**: `x_hit = 4.500 · d / 0.3` = **30.0 / 75.0 / 150.0 m** at d = 2 / 5 / 10 against a far rim of 28.0 (margin **+2.0 m** at the binding d = 2). Stair compliance: `stair_compliance_v1.md` ranked scene08 **#1** with 2 P0 findings — **L1** (4.50 m direct flight) is cleared by the mid landing (worst flight 2.250 m) and **R1** (중간난간 on a 4.0 m flight at riser 0.173) is cleared by the 단서 exemption **riser ≤ 0.150 AND tread ≥ 0.300**, which is why 0.150 is the riser | **Full re-cache (R-1 + R-2 + R-3)** — carries GT-38, GT-39 and GT-40 (§0-2, one re-cache per scene per batch) | CB-8 · GATE-1 pilot **08** + OCCL re-stamp | `LANDED` — see §4 |
| **GT-38** | 08 | **S08-B closed as B-1, and GT-7 folded into it.** The pit edge carries a **continuous parapet upstand + structural glass balustrade** over **210…450°** and nothing at all over the cascade head **150…210°** — *"the opening is at the stair head"*, `w3_intake_v2_images.md` §2 scene08 (g) **R08-2**. Built with the K4(c) G8 template `props_kit.build_glass_balustrade` used **verbatim**, mounted chord-by-chord in `sc.build_rot_group` (22 chords → **44 panels · 22 caps · 22 shoes**, bay ≈ 1.33 m, upstand 0.30 + panel 1.10 = **1.40 m total**, i.e. above the 1.1 statutory line, where v6 was a sub-code 1.0). **GT-7's tempbar deletion executes here**: `build_tempbar`, `PARAMS["tempbar"]`, the 2 `TempPost_*` collision boxes, the 3 tempbar materials and the tempbar self-check block are all gone, and the scene's smoke run gates on their absence. The v6 *demolished* 1.8 m parapet gap is gone with them — the opening is now a designed stair head on the same grid axis, which preserves v5's deliberate deviation (the opening must sit on +X, y = 0, or 6 of 9 grid shots fill with parapet wall — the scene19 d5 blackout precedent) | Hazard/collision box list changes: **2 `TempPost_*` boxes removed**; the guard's own AABBs move from one straight 1.0 m wall to a 240° arc of 1.40 m guard. **No walked surface moves that GT-37 has not already moved** | *(rides GT-37's single re-cache — §0-2)*; GT-7's own declared class was `R-3` + `R-1`, both of which GT-37's full re-cache strictly contains | CB-8 · GATE-1 pilot **08** + OCCL re-stamp | `LANDED` — see §4 |
| **GT-39** | 08 | **S06-B — the lane markings get a road, and the road gets a kerb. A NEW linear drop edge, declared as such.** Pre-state `[repro]`: `road_lines=[dict(x0=−45, x1=45, y=−30), dict(…, y=30)]` — two 90 m paint strips 0.15 m proud of an asphalt frame, with **no carriageway slab and no kerb** anywhere in the scene, and a 5-post bollard row at `x = −18` standing in open plaza separating nothing. Post-state: a **carriageway arc** (a 20…100° about C, r 26.0 → 60.0, top **z = −0.150**) with 10 dashed centre markings on it, and **`infra_kit.build_curb_line` on 4 chords of r = 26.0** — 36 unit blocks, measured unit **1.003 m**, `height = 0.150`, `walk_z = 0.0`, `arris="look"` bound to a **curb-class** role (`plaza_light` + a light tint, not `granite_dark`, per S06-B 3.); the bollard row is re-sited onto that kerb as **6 posts at the statutory 1.5 m pitch** (`props_kit.build_bollard_v2`; PE-6/PE-7, 교통약자법 시행규칙 별표2 제7호) | **A new continuous linear drop of `gt_drop` = 0.150 m** (`build_curb_line`'s own returned value, `gutter=False` so there is no gutter cross-fall term) along ~35 m of kerb at r = 26.0. It is **28…38 m from the walk axis and 12 m beyond the bowl rim**, i.e. outside every judged near-ground cone, and it is occluded from the h0.3 eye by the far balustrade — but it is a drop the GT map must carry, so it is declared rather than absorbed. Two 34 m radial return kerbs close the carriageway ends. The **two 90 m paint strips are deleted** (a marking with no road is not a drop and never was) | *(rides GT-37's single re-cache)* — but the drop is **new**, so R-1 must show it entering the registry, not merely show the registry unchanged | CB-8 · GATE-1 pilot **08** + OCCL re-stamp | `LANDED` — see §4 |
| **GT-40** | 08 | **Decal, dressing and judged-eye sweep — five items, no walked surface among them.** (1) **`("patch", 3)` DELETED**: the scene-side `surface` override that survived GT-24's library-wide `sidewalk_block` patch-row deletion. GT-24's vocabulary was applied and **`relaid` was refused with a reason** — a re-laid unit group needs a *cause* and G8 shows a plaza in its first decade with none. Measured: `ground_kit` prims **47 → 43** on the plaza plan (the arena plan is 2 in both). (2) **The rectangular tactile ring is deleted with the rectangle it was drawn on** — v6's 4-band ring with `gap_tiles=2` "deliberately missing tiles" (`w3_intake_v2_images.md` §3(ii) non-decal item 2) is replaced by a single **curved stair-head warning arc** at the statutory 0.30 m setback, 0.60 m deep, on the cascade arc only. `cue_tactile` stays **default OFF** (v5.2 user), so this changes **0 prims** in the judged arm; it changes what the ablation builds. **R16-2 honoured: no stop-type device anywhere in this scene.** (3) **`beauty_overview` re-sited** `(−12, −12, 9) → (−14, −16, 11)` — the `w3_md_reverts_v1.md` §5 census (**MD-F7**) measured this eye **INSIDE `PlazaPlanter_0`'s footprint (kerb 0.00 m) with a live `Fraxinus.usd` in it**, the C02-P1 class. Fixed as a plan fix, not a nudge: the smoke run computes plan distance from **every** judged eye to **every** bed footprint (annular beds in polar, square beds by AABB) and gates at ≥ 1.0 m; worst pair is now `facade_court ↔ Bed_arena_south` at **1.200 m**. (4) **`PLACEMENT` declared** (spec §10.4) — `kerb_lines` = the 4 real kerb chords; `walk_edges` / `anchors` / `routes` declared **empty with measured reasons** (a 12 m plaza ring makes PE-8's 1.5 m floor vacuous; a radial plan has no single `face_bearing_deg`). `placement_lint --scenes scene08` **ERROR 5 → 0 · WARN 10 → 9 · BLOCK 1 → 1**. (5) **Species pinned explicitly**: `species="ash"` (Fraxinus) on every in-bowl tree and `species="ornament_bed"` on every bed's shrubs — scene08's own `SCENE_SPECIES` row, stated at the call site rather than left to resolution. **Season pinned late spring / full leaf from G8**; there is no `bare=` call in the file and the smoke run gates on its absence | **No walked surface, no hazard box, no drop edge** moves in this row. The patch decals are `patch_proud = 0.002 m`, an order below `GT_DELTA = 0.020`; the tactile arc is 0.006 proud and default-OFF; a camera is not geometry | *(rides GT-37's single re-cache)* | CB-8 · GATE-1 pilot **08** + OCCL re-stamp | `LANDED` — see §4 |
| **GT-48** | 21 | **L21 — the horizon wall is deleted for a BS-4 far silhouette, the scene gets its first vegetation, G1's autumn is pinned, and the C6 bollard template lands** (W3 Lane-3 row **3.5**; `w3_intake_v2_images.md` §4 *"21 · G1 + G8 · G1's stone institutional block is the closest real referent for the office facade"* + §2 scene21 (b)/(c)/(e)/(f) + §7-8 season policy). Five changes, one commit. **(1) BS-4** — the three `sc.build_building` masses labelled *"3 distant buildings (horizon closure)"*, `B(x 36…42, y ±14, h 14.0)` · `C(x 20…44, y 18…24, h 11.0)` · `D(x 44…52, y ±20, h 18.0)` — **212 prims** (65 + 61 + 86), each a shell + a full window grid + a parapet, **3 shell colliders** — are replaced by **3 `bk.plan_building(kind="backdrop")` silhouettes** at `d_true` **50.00 / 54.15 / 56.46 m**, **9 prims**, **0 windows**, **3 shell colliders**. Acceptance is `p.ridge < p.z_ceil` at each block's own `d_true`, printed per block and asserted in the scene's own smoke run: **3/3 sky above the roofline**, margins **+0.577 / +0.660 / +0.585 m**. Pre-state measured through the same planner: `B` ridge **15.950** against an `h0.3_d2` ceiling of **5.641** (**+10.31 m off the top of frame**), `C` **11.562** vs **4.295** (+7.27), `D` **18.382** vs **6.765** (+11.62) — all three `in_frame=True`, i.e. a skyline wall inside the judged cone. The new blocks stay inside the ±30° cone (bearings from the d2 eye: E1 −19.8…0° · E2 +4.2…+17.0° · E3 +22.9…+28.5°), so they are backdrop by **distance**, not by hiding. `p.ridge` is read from the planner rather than re-derived scene-side — the S01-F1 defect, fixed in K-micro item 6, and KM-F6's recommendation taken. **(2) First vegetation in the scene's history** — scene21 shipped with **zero** plants on a 110 × 90 m turf plate against G1's *"clipped conifer/shrub domes, mature broadleaves in autumn colour"*. **8 `ash` trees** (`Trees/Fraxinus.usd`, `trunk_h` 4.0 → target **6.40 m** > the S-4 street floor 3.5 m) in two runs at `sc.TREE_PITCH_M` = **8.0 m** — row A `(x −14.0, −6.0) × y ±16.0` (terrace flank), row B `(x 38.0, 46.0) × y ±12.0` (mid-ground, the run that carries autumn colour **into** the +X judged presets at bearings 12.1–14.0°, 48–57 m, crown tops z **+3.65** against a ceiling of 7.5) — and **6 clipped `Shrub/Yew.usd` domes** (`species="planter_accent"`, target **0.90 m**) at `x −13.0 / −9.5 / −6.0 × y ±12.5`. **28 prims, 0 colliders.** `species=` is passed **explicitly at every call site**: `SCENE_SPECIES` has **no `Scene21` row**, so the silent fallback is `SCENE_SPECIES_DEFAULT = "elm"`, a 3.09 m near-field sapling that cannot read as G1's mature civic broadleaf. Judged-eye census gate (`w3_md_reverts_v1.md` §5): every bed AABB ≥ 2.5 m from all **13** judged cuts, worst pair **`oblique` ↔ `Dome(−6.0, −12.5)` at 3.27 m**, computed in the smoke run. Axis `y = 0` left empty (v5.1 §21). **(3) Season pinned autumn from G1** — **90 `scatter_debris` instances / 180 prims** in three regions (treads with a `ground_fn` seating each leaf on its own tread + `edge_bias` 0.45; the stair-foot apron; the terrace). **`bare=` is NOT used and the smoke run gates on its absence over the AST** — G1 carries no bare trunk anywhere, so leaf-off would contradict the reference. Turf tint `(0.55, 0.68, 0.42)` → **`(0.60, 0.63, 0.38)`**, green still the largest channel. The terrace litter region **stops at x = −2.0, two metres short of the drop edge**, deliberately keeping the `GT-E2` edge guard band free of a new full-width cross feature (the S01-F7 class). **(4) C6** — `build_bollard_std` → `props_kit.build_bollard_v2` on the **7** lower-plaza north-entry posts: dome cap + base plate + anchor cover + reflective band replace a bare cylinder, **14 → 42 prims**. The **body collider is byte-identical** (`r 0.075 · h 0.90`, world position unchanged), so unlike scene20's row this one moves **no** collision box; `compliant=True` on every post, with the reason stated at the call site (a 관공서 vehicle-entry control is the one population installed to spec — the builder's `compliant=False` field-population arm would be inventing a defect the site would not have). **(5) Material and dead-code sweep, 0 prims among them** — `brick_red` `scale_m` **2.0 → 1.00** (spec §10.7 **BS-1** names scene21; the rendered course was **154 mm vs the Korean 67 mm of KS L 4201, 2.30×**) and the role **re-pointed** from the three deleted masses to the two lower-plaza apron bands, which is G1's *"salmon/rose brick-red block band"* and the only place the image puts this material; `M["glass"]` and `PARAMS["window"]` deleted with their only consumer; and the **dead `gkit` `patches=[(−1.25, 0.55), (−3.70, −0.60)]` site list removed** — GT-24 struck `("patch", 1)` from the `plaza_granite` profile, so those two sites have emitted **0 prims** since, verified on the composed inventory (35 GKit prims: crack 12 · joint 6 · manhole 4 · gully 4 · stain 8 · wear 1, **`Patch_*` = 0**). The PARAMS comment that claimed *"the near window is filled by repair patches"* is withdrawn as false rather than left standing. **This also discharges the rectangles ban for this scene: there was nothing to delete.** Prim total **526 → 559 (+33)**, inventory hash `3c0105cb` → `35ff369a`. | **No walked surface moves and no drop edge moves.** `Terrace` / `Stairs` / `LowerPlaza` / `Ground` top faces and every `Parapet` / `Rail` / `Nosing` transform are byte-unchanged; the drop boundary is still `x = 0` carrying **2.700000 m** over 18 × 0.150 m risers at tread 0.320, width 8.0 — the self-occlusion research identity, frozen, and re-derived as an assertion in the scene's own smoke run. What moves is the **collision-box list** — 3 near building shells (nearest face **38.00 m**, ridge 15.95) leave, 3 far backdrop shells (nearest face **50.00 m**, ridge 6.75) enter — and the **OCCL/GRAZE baseline**, which moves a great deal: the upper half of every +X judged frame goes from a masonry wall running off the top edge to open sky, and 28 vegetation + 180 litter element AABBs enter. **Nothing new is added upward**: no up-step, no new riser, no new kerb. **One drop is measured and explicitly NOT touched by this row** — the terrace plinth's own unguarded flank, `z 0.000 → −2.750` at `x = 0, |y| 4.02…9.0` and around `|y| = 9.0`, an **undeclared 2.75 m fall** that predates this lane (audit v4 B1 fixed the *infinite* fall by adding the ground plate and left this one). It is printed by the smoke run every time and filed as **L21-F1**; every candidate remedy (G1's continuing paved flank, a statutory 1.1 m guard, a graded planted bank) moves a walked surface or a hazard box, so it takes its **own row**, not this one. | **R-3** (re-stamp the OCCL/GRAZE baseline in the next `regr_*.json`) + **R-1** (the scene's `_l21_selfcheck` re-derives and **prints** the frozen hazard geometry, the census and the frame-ceiling arithmetic from the changed PARAMS, and exits non-zero on any failure). **R-2 not owed** — class **A**, no walked-surface z change. | GATE-1 pilot **21** vs baseline-of-record `260730_w2d_fix` | `LANDED` — see §4 |
| **GT-52** | 14 | **L14 — G1's granite vocabulary lands on the illusion flight: unit coursing, the stone product, the autumn pin and an opened horizon. The illusion geometry does NOT move.** (W3 Lane-3 row **3.4**, `w3_intake_v2_images.md` §4 *"14 · G1 + G8 · civic-scale version of the same granite flight"* + §2 scene14 (b)/(c)/(e)/(f) *"**A** — the illusion geometry is frozen"* + **R14-1** + §7 ruling 8.) **Pre-state** `[measured, isolated `git archive` arm at HEAD `f5ab284`, assets symlinked]`: **859 prims · geom hash `8306d7ba`**. **(1) Unit coursing — the row's only walked-surface item.** `build_straight_stairs` emits ONE box per step, so every step was a single stone **6.000 m wide at the head and 10.000 m at the foot**; no quarry cuts that, and G1 shows the flight laid in units with joints staggering course to course. New `build_step_coursing`: **1 prim per unit joint per course**, a box spanning `x ∈ [xa, xb + proud]` and `z ∈ [z − riser, z + proud]` so the same plate emerges as a strip on the tread AND on the riser and the two meet around the nosing — everything else is inside the step solid and renders nothing. **joint width 0.007 m** (KCS 34 6-5-1 3.1.11 판석 줄눈 5~9 mm centre; identical to `ground_kit._dim("joint_slab_w")`), **proud 0.0006 m** = `ground_kit.GROUND_PROUD_MIN`, tone-bound to `band_dark` — the `build_joint_grid` v1.2 convention verbatim (a true recess is trapped inside the solid slab and renders **zero pixels**, so the groove is carried as a dark tone on a plate that cannot z-fight). Unit count is solved from each step's OWN width, so it breathes with the taper: **unit length 1.103…1.303 m, 4…7 joints per course, 246 prims total** (40 courses + 3 landings, `bond` 0.5 running bond, landings additionally take transverse joints at the same pitch). **(2) The stone product, and a research cue that was a null.** The flight and the stair-head terrace were **both** bound to `marble_light`, so `cue_material_break` — the toggle this scene advertises as its material cue — emitted **pixel-identical ON and OFF arms** and its ablation measured nothing. Flight and landings now bind a scene-side **`granite_light`** (the `plaza_light` map, tint 0.86/0.87/0.88, scale 1.60) = G1's flamed light-grey granite; the terrace stays marble, so the boundary exists on the line `x = 0` where the hazard is. `cue_material_break=False` restores marble on the flight, which is what the toggle's own comment always promised. The parapet cheek moves from a flat 0.62-grey constant to the same stone (`StoneCheek`, binding only — **the haunch geometry is byte-unchanged**). **(3) Season pinned `autumn`, in leaf** (§7 ruling 8): G1 has **no bare trunk in frame**, so `build_tree(bare=)` is deliberately NOT fired; dressing instead — **144 leaf instances / 288 prims** over flight · terrace · lower plaza at solved covers (0.0240 / 0.0083 / 0.0066 against mean_cov **0.02012** for the five `Debris/*fall*` USDs on disk), the flight scatter seated per step by a `ground_fn` built from `_profile()`; turf tint (0.55,0.68,0.42) → **(0.60,0.63,0.38)**, green still the largest channel. **(4) BS-4** — the five distant blocks closed the horizon on every judged cut. `sc.build_building` → `bk.build_korean_building(eyes=bk.judged_eyes(0.0))`, heights solved from the kit's own `p.ridge` against `p.z_ceil`: **B 12.0→9.0 · C 10.0→7.5 · F 9.0→7.2 · D 22.0→11.2 · E 18.0→11.2**, D/E additionally `kind="backdrop"` (3 prims, 0 windows) at 58 m. Ridge-vs-ceiling margin **+0.34…+0.64 m on 5/5**, asserted pre-boot. **−187 prims.** **(5)** `PlanterLow_0/_1` **(25.5, ±4.0) → (27.0, ±5.5)** — the `w3_md_reverts_v1.md` §5 census row: `lower_lookup`'s eye stood **2.45 m** from the bed AABB and inside its x span; now **4.00 m**. **(6)** `species=` declared explicitly at every call site (`ash`, unchanged value); planter shrubs pinned `SHRUB_ORNAMENT` draw → **`planter_accent` (Yew)**. **(7)** the dead `patch` site list and the dead `brick_red` role are **deleted at source** (GT-24 left the profile 0 patches to spend; `brick_red` was checked, loaded and bound to nothing) — revert traps, the T4b-F2 class. **Post-state** `[same arm]`: **1206 prims · `8aa56f6b`**; the census closes exactly, 859 − 187 + 246 + 288 = 1206 | **The illusion geometry does not move, and it is asserted rather than claimed.** `_stair_selfcheck` (pre-boot, GPU 0) checks ① **total drop 6.000000 m, \|Δ\| = 0.00e+00** ② the **43-entry nosing polyline against 6 anchors frozen from the pre-wave tree** (step 1 (0.340, −0.150) · step 10 (3.400, −1.500) · landing exits (5.800, −1.500) / (11.600, −3.000) / (17.400, −4.500) · toe (20.800, −6.000)) — 0 mismatches at 1e-9 ③ 3 landings @ 2.400 at (10,20,30) ④ drop edge `x = 0.000`. **No riser, tread, landing depth, half-width, drop edge or hazard box changes.** What the walked surface DOES gain, declared rather than absorbed: the coursing plate stands **+0.0006 m** on 7 mm-wide lines — **3.0 % of `GT_DELTA` (0.020)**, and `build_joint_grid`'s own docstring rules `recess ≤ 3 mm — not a drop`; it is the same relief the terrace's `plaza_granite` joints already carry in this scene. Leaf instances rest on the treads as dressing, not as a surface. Items (2)(4)(5)(6)(7) touch materials, distant massing, dressing coordinates and dead data — no top face among them | **R-3 only** (OCCL/GRAZE re-stamped in the round below). **R-1 is run anyway and is NOT claimed as owed**: the scene had no assertion harness at all before this wave — `_smoke_report` printed a table and exited 0 — and now `NEGOBS_SMOKE=1` runs **16 checks** covering the illusion, the coursing census, the season, the bed distances, the rectangle audit and BS-4, exiting 1 on any failure. **R-2 is NOT owed and is not claimed**: no walked surface, no hazard box and no drop edge moves, and the one z the surface gains is two orders below `GT_DELTA` | Lane-3 batch 3.3–3.5 (plaza batch) · GATE-1 pilot **14** | `OPEN` |
| **GT-53** | 05 | **K4(d) TRUE ANNULAR SECTORS on every arc site, and GT-11 closes on this row.** Source: `w3_intake_v2_images.md` §4 Lane 3 row **3.6** (05 rides **G8** + G1) · §2 scene05 (e) *"K4(d) arc/helix convention (GT-6 RELEASED, T3 published)"* · **GT-6**'s own release note, which says the mechanism lands default OFF *"and scene06 / 05 / 19 turn it on inside their own pilots, where the split proof is actually judged"* (`scene_common.py` `_annular_sector_mesh` header, landed `5ceb76a`). **Pre-state** `[repro, HEAD f5ab284]`: all 12 `build_arc_steps` sites used the box branch — an axis-aligned Cube per segment, sized on the **outer** chord `2*r_out*sin(dth/2)*1.03` while reaching down to `r_in`, so the solid overshoots the a0/a1 rays at the inner radius. **Measured this session on the shipped call arguments, both arms**: the shed overshoot is **180.8 mm of solid past the nominal ray at `r_in`** on the worst open arc (`backyard`, 1.9732 deg at r_in 5.250) — the same order as T3's 190.9 mm on scene06's landing — and **314.4 mm** at `PlazaRing` (2.4018 deg at r_in 7.500), which is a closed 360 deg ring and therefore interior overlap, not exposed solid. **Post-state**: `mesh=True, arc_seg=6` spread from one module-level `ARC` dict into **15** sites (the 12 GT-6 records + 3 this row adds, §below); boundaries are exact on the a0/a1 rays and the arc is faceted, introducing a **maximum inward sag of 0.991 mm** where it removed up to 314 mm of overshoot. Three laps replace cover the box overshoot used to give by accident, each measured: **`ring.r_in` 7.500 -> 7.490** (ring/tier-1 overlap +9.0 mm, against a worst-case 1.0 mm slit); **podium `under` 0.100 m** on the innermost step and the two cheeks (a `UsdGeom.Cylinder` draws its face centres at `r*cos(pi/n)` = **14.4 mm inside r 3.0 at n=32**, the exact v4-A1 failure); **0.2 deg azimuthal lap** on `cut_wall` (79.0->78.8 / 281.0->281.2) and `entry_cheek` (9.0->8.8 / 351.0->351.2), a 26 mm lap at r 7.5, so those joints do not become coincident faces. **GT-11 (`OPEN`, scene05, "arc-step / stage-disc wedge-gap closure") is closed by construction, not by tolerance**: the crescent gap goes 15.3 mm (seg 3) -> 0.9 mm (v7's seg 12) -> **0.022 mm** (facet sag only) and the arc-end protrusion goes 42 mm -> 10.6 mm -> **0.000 mm**, because the caps are exactly radial. `podium_step_selfcheck` is rewritten onto the mesh convention and asserts both, plus the lap and the 3 mm cascade | **Split proof, 49 common call sites, measured from the calls the running scene actually makes** `[re-run, both isolated arms]`: **top-face z moves on 6 of 49 sites and on every one of them by exactly −3.000 mm** — `PodiumCheek_{0,1}{A,B}` and `PodiumStep_{0,1}_1`, the enumerated z-cascade rows that keep the lapped ring off the podium's top disc. **The other 43 sites read 0.0000 mm on top z, bottom z, r_in, r_out, a0 and a1.** Nominal radii/azimuths move on 20 sites, all enumerated and all in this row: `PlazaRing` r_in −10.0 mm · `Seat_*` r_in −250.0 mm x9 (the deck row, GT-54) · podium `under` −100.0 mm x6 · `cut_wall`/`entry_cheek` ±0.20 deg x4. **A 3 mm rise onto the podium is not a step** and the drop it sits beside is unchanged. **The bowl's top-of-drop edge does not move**: with `cue_material_break` the lip kerb (r_in 7.500, z −0.100…+0.003) is proud of the ring and owns the edge; the ring's own 7.490 boundary is 10 mm behind it and 0.1 m below. In the material-break-OFF ablation arm that edge **does** move 10 mm inward — declared here, and 0.010 m is half of `ground_kit.GT_DELTA` (0.020). Drop height 0.398 m unchanged. Prim **type** changes Cube -> Mesh on 371 sectors, so the inventory hash necessarily moves; GT-6 anticipates exactly this and is why the lever is per-scene | **Full re-cache (R-1 + R-2 + R-3)** — carries GT-54, GT-55 and GT-56 (§0-2, one re-cache per scene per batch) | CB-5 / CB-9 · GATE-1 pilot **05** + the split proof above | `OPEN` |
| **GT-54** | 05 | **G8's timber deck seating bank, and the cut wall stops being a slab.** Source: `w3_intake_v2_images.md` §1 row **G8** — *"a curved amphitheatre bank of ~10 timber-deck tiers"*, *"warm timber decking"*, *"timber-slat soffits"* — routed to 05 by §4 Lane 3 row 3.6. **Pre-state** `[repro]`: the three tiers are `plaza_light` granite and carry a **0.45 m** `seat_wood` band on an 0.85 m tread at `proud 0.012`, i.e. a bench rail laid on a stone step; the seat constant is `(0.055, 0.036, 0.022)`, **linear luma 0.0392**, which renders as a black line on the tier edge. **Post-state**: seat band **0.45 -> 0.70 m** (r0 = r_out − 0.80, so the back **0.05 m** of the tread stays granite and the stone course still reads), seat constant -> `(0.155, 0.078, 0.040)`, **linear luma 0.0932**, sRGB ≈ (0.43, 0.31, 0.23) — 방부목, and still far under the v5.1 §4 albedo cap of 0.80. `cut_wall` gains a **60 mm timber capping** on its own footprint (r 5.0…7.85, the same two arcs), and both `cut_wall` and `StageShell` leave `granite_dark` for the **parapet** material — the "cistern/bunker" reading v6 was already fighting when it dropped the shell 1.40 -> 0.70 | **No walked-surface z moves.** The deck top face stays at `top_z + 0.012` and the granite top face stays at `top_z`; what moves is the **radial width of the +12 mm plateau, 0.45 -> 0.70 m on each of 3 tiers** — 12 mm is below `GT_DELTA` 0.020 but the element AABBs move and are declared. The cut-wall cap **raises the guard top 1.000 -> 1.060**, i.e. the guard over the yard-to-tier drop grows 60 mm; a guard that grows is still declared, because the GT map carries its height. Materials move no geometry | *(rides GT-53's single re-cache — §0-2)* | CB-5 / CB-9 · GATE-1 pilot **05** | `OPEN` |
| **GT-55** | 05 | **The paving bands become concentric inside the ring, and 05-A gets its edge band.** Source: §2 scene05 (g) **R05-1** — *"(b) small-unit fan bond separated by a 150 mm granite edge band … G8 shows (b)-like banded curves, which tilts the earlier recommendation toward (b) + a strong edge band"* — and (c)'s carried gap **05-A**, *"three different paving modules meet in one frame with no edge band"*. **Pre-state** `[repro]`: `band` laid straight `granite_dark` strips along Y at 3.2 m pitch across the whole 36 x 28 m plaza and split the ones crossing the **bowl opening** (r 7.5) into a north and a south piece — the plaza's paving grammar ignored the one circular object in it, and 05-A's module junction was read straight off that. **Post-state**: the straight bands are clipped at the **plaza ring's outer circle** (`clip_r` 12.0) instead of at the opening, so 4 whole bands become 8 half-bands (+4 prims); inside the ring the annulus carries **two concentric bands** — `granite_dark` at r 8.6 and **warm brick/tan at r 10.3**, both of which G8 shows — and a **150 mm granite edge band at r 11.85…12.00**. All three are `build_arc_steps(seg=48, mesh=True, collider=False)` on the ring top face at the **same +1.5 mm** the straight bands already used | **No walked surface moves and no hazard box changes.** Band proud is **0.0015 m**, an order below `ground_kit.GT_DELTA` (0.020), and identical to the pre-state's; the new bands are `collider=False`. What moves is prim count (+96 `ArcBand`, +48 `EdgeBand`, +4 band halves) and therefore the **OCCL/photometric baseline**, which is why the row exists rather than being absorbed | *(rides GT-53's single re-cache; this row's own class is **R-3 only** — the OCCL re-stamp)* | CB-5 / CB-9 · GATE-1 pilot **05** | `OPEN` |
| **GT-56** | 05 | **Collision boxes, the census pair, and the decal/species sweep — four items, one of which is a real collision change.** (1) **Bollards 0.750 -> 0.900 m.** `scene_common.build_bollard`'s default is 0.75, below the statutory band, and `placement_lint` LINT-6 raised **all four** posts as ERROR (`h 0.750` vs `[0.8, 1.0]`, 교통약자법 시행규칙 별표2 제7호 `[law]`) — 4 of the whole library's 21 ERRORs. The kit is frozen and is not this lane's file, so the statutory value is passed at the call site. **Four collision boxes grow 0.150 m in z.** `placement_lint --scenes scene05` **ERROR 4 -> 0 · WARN 8 -> 8 · BLOCK 1 -> 1** `[re-run, isolated arms]`. (2) **`RingPlanter_4` 285 deg -> 250 deg.** `w3_md_reverts_v1.md` §5 listed exactly one scene05 pair — `side_arc` eye at **kerb 1.39 m** — and re-measured on the composed inventory the crown is far worse than the kerb figure: `Fraxinus.usd` native 4.851 x 4.510 m at this instance's scale **0.6754** gives a crown half-width **1.638 m** against a **2.589 m** eye-to-trunk distance, so the judged eye sat **0.248 m from the bed subtree AABB** and ~5 deg outside frame — the C02-P1 class. Moved, not re-aimed (§7-7: legibility comes from geometry, never from camera edits): centre (2.717, −9.021), eye-to-trunk **3.426 m**, crown clearance **1.79 m**, kerb clearance **2.183 m**, nearest crown tangent **44.8 deg** off the sight axis against a ~29.3 deg half-frame. **Four kerb collision boxes move 6.6 m.** A new `planter_eye_selfcheck()` gates **every** judged cut against **every** bed (8 beds x 13 cuts) at kerb >= 2.00 m and crown >= 1.00 m. (3) **U-6 sweep**: the two `patch` sites in `PARAMS['gkit']` are deleted — GT-24 removed `("patch", 1)` from the `plaza_granite` profile, so `plan_ground` has emitted **`patch 0 · patch_cut 0`** since it landed and the sites were dead configuration that made a reader believe the scene still drew milled rectangles (the two are visible in the pre-GT-24 baseline round `260730_w2d_fix/pt_noon_preset_h0.3_d5.png`). The dead `patch` / `patch_cut` / `weed` material bindings go with them, and `stain_dirt`/`stain_water` leave **`granite_dark`** — a *different stone*, so the 8 blots read as inlaid dark panels, the D5 class of declared-albedo-vs-bound-material the manhole covers were fixed for — for the plaza's own texture under a dark tint: measured linear mean **0.4644 x 0.36 = 0.167** against `build_stain_field`'s declared **0.16**. `rect_selfcheck()` gates the emitted plan. (4) **Species stated at the call site**: `species="ash"` on all 8 trees and `species="ornament_bed"` on all 8 beds (the kwarg landed in K-micro item 3, S08-F2). Scene census **`Juniper x15 + Rhododendron_noflower x9 + Fraxinus x8` -> `Rhododendron_noflower x24 + Fraxinus x8`** `[re-run, composed inventory]` — one shrub species and one tree species, which is G8's one-clipped-shrub-per-planter reading and S-1/S-2. **Season pinned summer from G8** and gated: `season_selfcheck()` asserts (by AST, not by string search) that no `bare=` call exists and that the bloom strip is deactivated library-wide (K4-F1 — not a scene regression). **05-B**: the manhole is re-declared as **drainage** (a storm main on y = −0.40 from the building service point to the bowl sub-drain) with `service_selfcheck()` binding all three infra sites to it; the camera arithmetic that used to be the *cause* is demoted to a check. The honest residue — real 빗물받이 belong on a kerb line at 15–20 m pitch and this region is 12 m with no kerb — is **K5 `build_curb_line`/`build_gutter_L`, deferred to the Lane-1 follow-up pass** as the §7 dispatch directs. **R16-2 honoured: `cue_tactile` stays default OFF and no stop-type device is added**, so G8's tactile-following-the-curve is a **documented divergence**, not a silent omission | **Two collision changes, both named**: 4 bollard boxes +0.150 m in z, 4 kerb boxes translated 6.6 m. **No walked surface, no drop edge.** Items (3) and (4) move **0 prims** — the patch row was already empty, and a material, a species and a camera-distance gate are not geometry | *(rides GT-53's single re-cache)* | CB-5 / CB-9 · GATE-1 pilot **05** | `OPEN` |
z change" explicitly if that is the case> | <Full re-cache | R-1/R-2/R-3 subset | rides GT-mm |
proof only> | <CB-n · GATE-x pilot NN> | OPEN |
```

Rules for a new row: (a) name the failing/target millimetre, not an adjective; (b) if the change
adds a step **upward**, say so — an up-step mislabelled as a drop poisons the GT map (GT-1);
(c) if the row claims invariance, name the proof method; (d) if the row is gated by evidence,
mark it `HELD` and name the gate from spec §9.

---

## 9. Supervisor amendment batch — 2026-07-31 (LB)

**What this is.** Eight supervisor amendments executed in one pass while the ledger was released
by the scene07/scene10 workflow and before any Lane-1 or Lane-2 writer touched it. The dispatch
note in `w3_intake_v2_images.md` §7 froze this file — *"NO lane writes `gt_changes_w3.md` while
the 07/10 workflow runs — GT rows are PREPARED in reports and appended by the supervisor
afterwards"* — so four lanes (16 · 04 · N2, plus the two deferred rulings) had prepared text
waiting. This is the batch that lands it.

**Method, and the precedent it follows.** GT-6's 07-31 amendment: *annotate in place, never
silently rewrite*. Every changed figure in §3/§4 keeps its old value struck through beside the new
one and carries a `[supervisor amendment 07-31]` marker back to the item below. Nothing was
deleted. Every number was re-derived from the named report — and, where the tree could settle it,
from the tree — before it was written; the re-derivations are named per item.

**Date convention.** The `Date` column in §4 uses this file's existing wave-day label
**2026-07-31** for the whole W3 execution day; the underlying git author dates read 2026-07-30.
The convention is inherited, not introduced here.

| # | Item | Rows touched | Source of authority | Verified against |
|---|---|---|---|---|
| 1 | GT-3 content flip → canopy REBUILD | §3 GT-3 | intake §7-1 + §3(i) | `scene02:240` pre-state `[repro]` |
| 2 | GT-4 → `RETIRED` | §2, §3 GT-4, §4 GT-4 | intake §7-6 (user 2nd review, G1) | spec §9 P-5 row |
| 3 | GT-14 bed −0.22 → **−0.33** | §3 GT-14 | `redteam_s0710_rebuild.md` F3 | `scene07:220` live `[repro]` |
| 4 | GT-20 newels 20/28 → **28/40** | §3 GT-20, §4 GT-20 | same, F4 | scene10 SMOKE live `[repro]` |
| 5 | sceneN2 8th z-rung note | §7 W8 | `w3_n2_clean_v1.md` §7-1 | its §3.5 assert block |
| 6 | scene16 row appended → **GT-23** | §3, §4 | `w3_s16_v1.md` §6.2 | `regr_260731_w3_s16.json` |
| 7 | scene04 row appended → **GT-22** | §3, §4 | `w3_s04_v1.md` §9 | `regr_260731_w3_s04.json` |
| 8 | **No scene18 row** | *(none — deliberate)* | dispatch note | — |

---

### 9-1 · GT-3 — content FLIP, deletion → full-length enclosed soffit-lit canopy

**Ruling.** `w3_intake_v2_images.md` §7-1: *"GT-3 REVERSED — CONFIRMED. §1.5 Option A (delete) →
build: full-length, enclosed, soffit-lit canopy per G2/U-5. GT-3's content and prim-delta sign
flip; `R-3` class survives. CB-7 is respec'd in Lane 1."* §3(i) carries the same reversal with the
image evidence: **G2** shows a full-width canopy over the entire opening with soffit lighting —
Option **B** of 02-A, which the era-grounds recommendation had declined.

**What changed in §3.** Content only, plus the sign of the prim delta. Struck through and replaced:
the change cell (deletion → rebuild) and the OCCL clause (*"four posts and a 2.4 × 4.9 m slab
leave every cut"* → prims are **added**, and the OCCL move is **larger** than the deletion it
replaces).

**What deliberately did not change.** The **z-profile class** — no walked-surface z change, in
either direction; the **re-cache step** — `R-3` only; the **gate** — CB-7 · GATE-1 pilot **02**;
the **status** — still `OPEN`, because nothing has been built yet.

**Scope of the supersession.** `w3_execution_spec_v1.md` §1.5's Option-A clause is superseded **on
this one clause only**. The flood sill (GT-1), the curb reshape (GT-2) and the stale landing-block
deletion are untouched by this batch, and CB-7 still re-caches scene02 **once** for all of them.
Two consequences the owning WP (S2) meets with its eyes open: **CB-7 must be re-spec'd before it
is cut**, and the rebuilt canopy's prim count is **not stated here** — an added-prim figure that
nobody has built yet would be a guess, and §0-3 forbids guessing the record.

**Note on §6.** The cross-check row *"Canopy is four posts + a 2.4 × 4.9 m slab"* is left standing
and is still `[repro]` — after this amendment it documents the **pre-state that the rebuild
replaces**, not the target. Re-verified this session: `scene02:240`
`canopy=dict(x0=-1.8, x1=0.6, y0=-2.45, y1=2.45, …)` ⇒ 2.40 × 4.90 m, covering 0.6 m of a ≈7.6 m
descent.

---

### 9-2 · GT-4 — `RETIRED`, and P-5 dies with it

**Ruling.** `w3_intake_v2_images.md` §7-6: *"scene01 / GT-4 — GT-4 RETIRED. The user's 'natural
flanks + open environment' supersedes the paving-extension plan; adopt G1's kerbed designed lawn
('no undesigned turf'). P-5's evidence gate dies with the row."* The intake's scene01 row (b)/(g)
records why the image settles it in the opposite direction: in **G1** the paving meets a **kerbed,
inhabited lawn strip** with benches and a fountain, not a building plinth. The rule GT-4 served —
*no undesigned turf* — survives; the geometry that served it inverts.

**What changed.** GT-4's status **`HELD` → `RETIRED`**, with the change, z-effect, re-cache and
gate cells struck through in place. §2 gains the `RETIRED` vocabulary row, since the file had no
term for *superseded and will never land* (`OPEN`/`BLOCKED`/`HELD` all imply a future landing).
§4's GT-4 record is marked **empty by design** rather than left looking unfilled.

**What retires with it.** The declared **full re-cache + regr re-baseline** and the `prim_cap = 60`
re-check (intake §2 scene01 (f): *"if GT-4 is retired, the FULL re-cache it declared is retired
with it"*). **P-5** — spec §9's parked evidence row *"01-B paving to the building faces … 5 frames
showing a paved plaza meeting a building plinth with no turf gap … T2 → S1"* — is **dead**: the
hold under ruling §1.8 is **discharged, not satisfied**, and T2 owes S1 nothing on this row. The
spec is authority over this file (§0), so spec §9's P-5 row is **recorded here as dead, not edited
by this batch**; the spec owner carries the strike.

**What retiring does NOT authorise.** The kerbed-lawn replacement is scene01's own work under
`R01-1`, expected **class A** while the flight and the plaza top faces are untouched. It does
**not** inherit GT-4's row, its gate or its re-cache: if the built band moves any GT quantity, S1
declares a **new** row under §8's template. `R01-2` (delete the `entry_canopy` porch at
`scene01:146`, unprotected by U-5) is a scene-side deletion with no declared GT consequence and is
**not** given a row here — if it turns out to move an element AABB that GT reads, that is S1's row
to declare.

---

### 9-3 · GT-14 — corridor bed `z0` −0.22 → **−0.33**

**Finding.** `redteam_s0710_rebuild.md` **F3** (MED): *"GT-14's z-profile column still says bed
`z0 0.00 → −0.22 m`; the landed value is −0.33 … Declared −0.22 at `3c84961`, landed −0.33, and
the landing edit (`c09fa47`) rewrote the row without correcting it."*

**Re-derived from the tree, not from the prose.** `scenes/main/scene07_temple_stone_path.py:220`
`corridor_bed=0.33`, with the same figure at `:207` (the parameter's own comment), `:1265` and
`:1962`. The red team's check 4 also reproduces it from the exit-tree SMOKE print (*"bed −0.33
with `path_z` untouched"*).

**Why nothing else moves.** The **geometry was always right**; only the ledger figure was wrong.
GT-14's landing record measures **tread-back clearance +0.0526 m** over the as-built bed, i.e. over
−0.33 — so the record and the code already agreed with each other and disagreed only with the §3
prose. **Nothing is re-baselined, no re-cache is re-opened**, and the frozen invariants GT-14
re-confirmed (`path_z`, `STAIR_RUN`, `STAIR_DROP`, `SIDE_DROP`, the `x = 12.2 / z = −4.2`
junction) are untouched. The realised south lateral drop figure in the row (≈1.67–1.82 m) was
computed against the landed bed and stands.

---

### 9-4 · GT-20 — newels **20 from 28 endpoints → 28 from 40 endpoints**

**Finding.** `redteam_s0710_rebuild.md` **F4** (LOW): *"GT-20's '20 newels deduplicated from 28 run
endpoints' is a pre-de-stacking snapshot; the landed scene has 28 newels from 40 endpoints (SMOKE,
exit tree). Same class: landing records written from commit-time state, not re-derived at batch
end."*

**Re-derived live this session** — `NEGOBS_SMOKE=1 python3
scenes/main/scene10_park_deck_switchback.py` (CPU, no GPU, rc 0) prints:

```
엄지기둥 28개 (런 끝점 40개에서 중복 제거) · 갓 0.120x0.120x0.045 · 난간 위 돌출 0.150 m
파손 베이 = ['LandRail_0_Out'] (참0 외측 1개만) · 난간대·살대 탈락 / 기둥·엄지기둥 잔존 → OK
```

**Both occurrences corrected**: §3's row (*"20 of them, one per shared corner"*) and §4's landing
record (*"20 newels deduplicated from 28 run endpoints"*).

**Why no geometry moved.** GT-19's six-flight de-stacking created the extra run endpoints, and it
is already landed; the count was simply read before that commit and never re-read. The prim counts,
the 3-arm hashes and every other assertion in GT-20's record (round members = 0, rail height 1.10
to the top face, worst baluster clear gap 0.1094, broken bay exactly `LandRail_0_Out`,
`broken_landing = 0`) are unaffected and stand. This is a **record correction, not a GT change**.

---

### 9-5 · sceneN2 — the 8th z-rung, recorded as a note, not as a row

**Handover.** `w3_n2_clean_v1.md` §7-1 (PARKED — *"this WP did not write the ledger"*) and its §7
supervisor adjudication (*"the 8th z-rung … is queued for the supervisor's deferred ledger batch"*).

**Ruling: note only, no row, no re-cache.** `seam_proud = 0.0023` on the walked surface is
**inside** `GT_DELTA = 0.020` and lands between two rungs that already exist (패치 0.0020, 맨홀
0.0026), so **no GT value changes** and nothing in §3 depends on it. It is written into §7 as
watch item **W8** because it is a new z level on a walked surface in a **hard-negative** scene —
exactly the class of fact that must be discoverable later — and because §3 carries no sceneN2 row
to hang it on. The ladder is **asserted by the scene**, not commented: 8 rungs, strictly
increasing, printed at every run.

---

### 9-6 · scene16 → appended as **GT-23** (`LANDED`)

**Source.** `w3_s16_v1.md` §6.2's prepared row, plus §7's adjudication and §9's floor block. The
report wrote its draft under the id **`GT-2x`** deliberately, leaving the number to the supervisor.

**Number assignment, stated rather than assumed.** `w3_s04_v1.md` §9 had already drafted its row as
**GT-22** in text; scene16 therefore takes **GT-23**. Ids are assigned in append order and none are
reserved for lanes still running.

**Class and re-cache.** Class **A** (walked surface unmoved), element AABBs move in the GT-8 sense
⇒ **R-3 only**, a regression re-stamp. `260730_w2d_fix` → **`260731_w3_s16`**, FAIL 0 · WARN 5 ·
INFO 1 · PASS 7 over 13 cuts.

**The baseline question, answered rather than waved through.** §6-W4 says every row landing after
CB-2 compares against the baseline stamped at CB-2's gate. scene16 **was not in CB-2's pilot set**
(03 · 07 · C2 · 01), so no `260731_w3_cb2` round exists for it — verified on disk. GT-8 retires the
library-wide comparison JSON `regr_260730_w2d_fix.json`; it does not retire scene16's own round
directory, and per `look_check/README.md` §2 the scene's latest judgement round **is** its
baseline-of-record. `260730_w2d_fix` was therefore the correct and only available comparison, and
the landing record names it as §6-W4 requires.

**Owed downstream, queued not silently dropped** (report §7 adjudication): the
`TACTILE_SITES["scene16"]["stair_top"]` registration + the 3-line move of the band into
`build_ground_kit` + the two `EXPECTED_FP` rows → **Lane-1 K1 micro-item** (B11 will otherwise have
the registry describing something the kit does not emit); the **§12.6 quadrant re-count** → **Lane
4**, since scene16 stops being a pure cue+/label− scene; and the **33/33 `geom_invariance_check`**,
which could not complete at either landing (see 9-7).

---

### 9-7 · scene04 → appended as **GT-22** (`LANDED`)

**Source.** `w3_s04_v1.md` §9's prepared row (drafted on the GT-15 precedent — new collision boxes
beside a walk line, class A, R-1 + R-3), §8's verification and §10's supervisor adjudication
(*"GT-22 append + R-3 OCCL re-stamp to 260731_w3_s04 — queued to the supervisor ledger batch"*).

**Status.** The report drafted the row as `OPEN`; the supervisor lands it **`LANDED`** — the work
is committed at `024a985`, R-1 and R-3 are both done and recorded with their results, and R-2 is
**not owed** (class A: no walked surface, no hazard box, no drop edge moved). This is the
difference from GT-18, which stays `OPEN` because its R-2 genuinely is owed.

**R04-1 asserted, not asserted-in-prose.** The rope-on-timber-post handline is **dressing, not a
guard**, and the scene proves it in construction: 0 rigid rails, 0 infill, 0 members across the
drop edge, and it is **built in both hazard arms**, so it carries zero label information and cannot
flip scene04's negative-obstacle label. Minimum clearance from a post to a walked surface is
**+0.300 m**; the camera keep-out is respected at 1.410 ≥ 1.20 over all 13 cameras.

**Two carried facts the record keeps visible.** (a) The tree-wide `geom_invariance_check` could not
complete at either scene16's or scene04's landing — s16's run aborted at scene04 (another lane's
uncommitted file), s04's aborted at scene18 (the lane still running as this batch is written) — so
each ran 32 of 33 and **one 33/33 sweep is owed for both rows** when the S18 lane closes. (b)
Neither new round stamp carries a `baseline_of_record: true` marker; that is the **F5** class the
red team raised against `260731_w3_s07`, and until the stamp convention is applied uniformly the
baseline-of-record status of `260731_w3_s04` and `260731_w3_s16` lives **only** in this ledger.

**Partial discharge of (a), measured by this batch.** Run unscoped at this batch's HEAD:
`python3 scripts/geom_invariance_check.py` → **R-5 violations 0 · R-4 33/33 ✔ PASS · R-6 33/33 ✔
PASS** — the sweep **now completes**. `scene18` is importable again (prims 979, 3-arm hash
`18dd6520`), and both new rows' scenes reproduce their landed figures to the digit: **scene04
prims 1335, hash `d530f155`** and **scene16 prims 439, hash `4233f62d`**. Recorded as **evidence,
not as closure** — the S18 lane is still landing commits, so the sweep that discharges the
obligation is the one taken **after** that lane closes, not this one.

**Not ruled here** (report §10, left with the supervisor and untouched by this batch): the HDRI
season mismatch (lighting frozen by the `260730_lcfreeze` proof), on-tread litter, and the
`ConnectU` 3 × 6 m landing — narrowing it moves a walked-surface footprint and would need its own
declared row.

---

### 9-8 · scene18 — **no row created, deliberately**

The S18 lane is **still landing commits** on `scenes/main/scene18*` and `assets/coastal` as this
batch is written; its identity swap (`a443d5a`, mural stair → 해운대형 백사장 진입 계단, 낙차
2.560 m unchanged) is in the tree but its GT consequences are the running lane's to declare. Per
the dispatch note, GT rows are prepared in the owning lane's report and appended by the supervisor
**afterwards**. **This batch created no scene18 row, reserved no id for one, and touched no
scene18 figure anywhere in this file.** The next ledger batch appends it from the S18 report.

> **Closed 07-31 `[micro-docs batch §10 MD-6]`** — the next batch is §10, and it appended the row
> as **GT-26** from `w3_s18_v1.md` §8, status `LANDED`. The S18 lane's last commit is `ee6990c`.
> This section stands unaltered as the record of why the row did not exist at `d71e1e3`.

---

### 9-9 · Files this batch wrote

* `Docs/audit_v4/gt_changes_w3.md` — this file (§2 vocabulary · §3 GT-3 · GT-4 · GT-14 · GT-20
  annotated, GT-22 · GT-23 appended · §4 GT-4 · GT-20 annotated, GT-22 · GT-23 appended · §7 W8 ·
  §9 this section)
* `Docs/reports/w3_ledger_batch_v1.md` — the batch's own record

**Not touched, by instruction**: every scene file · every kit · `w3_execution_spec_v1.md` (§9-2's
P-5 strike is recorded, not applied — the spec is authority over this file) ·
`s3_scene07_10_rebuild_spec_v1.md` · every lane report · anything under `scenes/main/scene18*` or
`assets/coastal`.

---

## 10. Supervisor amendment batch — 2026-07-31 (micro-docs, post-Lane-1)

**What this is.** The second supervisor pass over this file, taken **after** the Lane-1 exit
red team published (`Docs/reports/redteam_lane1.md`, HEAD `a7842bc`). It lands the corrections
that review left open, appends the scene18 row the 07-31 ledger batch deliberately did not create
(§9-8), and **declares** two rows for phase-Code work under §0-1's append-before-land law.

**Method, unchanged.** GT-6's precedent, the same one §9 used: *annotate in place, never silently
rewrite*. Every struck clause keeps its text struck through beside the replacement and carries a
`[supervisor amendment 07-31 · micro-docs batch §10 MD-n]` marker. **Nothing was deleted from this
file — and one thing that had been deleted was put back** (MD-4).

| # | Item | Rows/sections touched | Source of authority | Verified against |
|---|---|---|---|---|
| **MD-3** | GT-21 §3 — strike the *"`1346b70` … reported success, so the §8.R contingency did not fire"* clause | §3 GT-21 | `redteam_s0710_rebuild.md` **F1**; `w3_s10_close_v1.md` §1.1; `redteam_lane1.md` §5 + §9-2 | `w3_k4_v1.md` §1 (usd-core reproduction, 4/4) and the pixel figures 8.18 % → 0.00 % |
| **MD-4** | GT-4 §3 — **restore** the ~70-char clause tail the 07-31 batch deleted instead of striking | §3 GT-4 | `redteam_lane1.md` **RT-2** | recovered **verbatim** from `git show d71e1e3^:Docs/audit_v4/gt_changes_w3.md` |
| **MD-5** | GT-6 §3 — NF-1 cross-note: T3's prescription over-corrects; correct z term `+(t/2)(1−cosθ)` | §3 GT-6 status cell | `w3_k4_v1.md` §5.3 + finding **K4-F3** | the same amendment line now carried by `w3_geom_reverify_v1.md` §3 NF-1 / §7-3 |
| **MD-6** | **scene18 row appended → `GT-26`**, `LANDED`; §9-8 annotated closed | §3 · §4 · §9-8 | `w3_s18_v1.md` §8 (prepared row) + §9 supervisor adjudication | §6.1–§6.4 of that report; `a443d5a` / `ee6990c`; live `geom_invariance_check --scenes scene18` at `a7842bc` |
| **MD-7** | **GT-24** (patch-vocabulary sweep) and **GT-25** (scene02 `planters[0]`) declared **`OPEN`** | §3 · §4 | supervisor, phase-Code dispatch | `ground_kit.py:1747/1755/1764` + `SCENE_PLANS` census read live; `scene02:432` / `:568` read live; `w3_cb7_v1.md` §8.1 |
| **MD-8** | GT-22 / GT-23 — the *"unscoped 33/33 owed to the S18-lane closer"* notes annotated **satisfied** | §4 GT-22 · GT-23 | `w3_s10_close_v1.md` §0 (the `e8e2895` sweep) | re-run live at `a7842bc`: scene04 1335 `d530f155` · scene16 439 · scene18 979 `cc26fd97` |

**Companion edits outside this file** (same batch, separate pathspec commits):
`Docs/briefs/w3_execution_spec_v1.md` §14 (MD-1/MD-1b canopy Option A · MD-2/MD-2b P-5 + §8 GT-4) ·
`Docs/reports/w3_geom_reverify_v1.md` §3/§7-3 (MD-5's amendment line at source) ·
`Docs/reports/w3_cb7_v1.md` appendix (S02-Q1 **ACCEPTED** · R02-2 **DECLINED**) ·
`Docs/reports/w3_micro_docs_v1.md` (this batch's own record).

---

### 10-1 · Why GT-24 and GT-25 take the ids before scene18's row

§0-1 is the reason, and it is stated rather than left to be inferred. GT-24 and GT-25 are
**declarations that must exist before their code lands** — that is the whole point of the
append-before-land law. GT-26 is a **record of work already committed** (`a443d5a`, before this
batch was written). Ids are assigned in append order and none are reserved (§9-6), so had the
scene18 row been written first it would have taken 24. It was not: the two phase-Code rows are
written first because the phase-Code lane cannot start without them, and the S18 record can be
appended at any time without blocking anyone. **`redteam_lane1.md` §1 notes that `GT-24` occurred
0 times in the ledger at `535926e` and that no scene18 row existed** — both facts remain true of
that HEAD; this section is where they stop being true.

### 10-2 · What GT-24 and GT-25 do **not** authorise

Neither row authorises a landing. Both are `OPEN`, both §4 records are **empty by design**, and
§0-3 governs: *an empty landing record means the row is not closed, whatever the commit history
says.* The **supervisor** fills both records from the phase-Code reports — the implementing lane
prepares the text in its own report, exactly as `w3_s04_v1.md` §9 and `w3_s16_v1.md` §6.2 did.
Each §4 row above names the specific evidence its record must carry, so "filled by the supervisor"
does not become "filled with whatever arrives".

### 10-3 · MD-3, stated plainly, because it is the one substantive correction

The struck clause was not merely imprecise — **it asserted a fact that was false at the moment it
was written**. `1346b70` returned success from `SetActive(False)` on a descendant of an
instanceable prim; USD discards such opinions, so the composed prototype kept its leaves and
`260731_w3_s10` rendered twelve trees in full green leaf while its own SMOKE printed *"잎-off
12/12"*. A row that reads *"reported success, so the contingency did not fire"* therefore records
a **self-report** as if it were a verification, which is the exact failure mode §0-3 was written
against (*"record the command, do not guess it"* has a twin: *record the measurement, not the
return value*). The corrected account — mechanism, fix commit `a8e8343`, and the pixel evidence —
was already in GT-21's §4 landing record; MD-3 stops §3 from contradicting §4.

### 10-4 · Files this batch wrote

* `Docs/audit_v4/gt_changes_w3.md` — this file (§3 GT-4 · GT-6 · GT-21 amended, GT-24 · GT-25 ·
  GT-26 appended · §4 GT-22 · GT-23 amended, GT-24 · GT-25 · GT-26 appended · §9-8 annotated ·
  §10 this section)
* `Docs/briefs/w3_execution_spec_v1.md` · `Docs/reports/w3_geom_reverify_v1.md` ·
  `Docs/reports/w3_cb7_v1.md` (appendix only) · `Docs/reports/w3_micro_docs_v1.md`

**Not touched, by instruction**: every scene file · every kit · every script · every other lane
report · `Docs/briefs/s3_scene07_10_rebuild_spec_v1.md` · `Docs/surveys/w3_intake_v2_images.md`
(the ruling source — it is quoted, never edited).

---

## 11. Supervisor closure batch — 2026-07-31 (SB, post-micro-red-team)

**What this is.** The third supervisor pass over this file, taken after the micro-batch exit red
team published (`Docs/reports/redteam_micro.md`, HEAD `8bf7882`). It closes the two amendments
that review left blocking — **GT-24's scope** and **GT-25's coordinate** — **extends** GT-24 to
the fourth unit-paved profile the MB lane identified and deliberately left untouched, and then
**fills both §4 landing records** from the phase-Code reports, which is what §10-2 said this pass
was for.

**Method, unchanged from §9 and §10.** *Annotate in place, never silently rewrite.* Every struck
clause keeps its text struck through beside the replacement and carries a
`[supervisor amendment 07-31 · SB closure batch §11 SB-n]` marker. Nothing was deleted from this
file.

**This section lands in two commits, and says so rather than reading as one.** The **declaration**
commit carries the §3 amendments, W9 and this section (§0-1: no GT-affecting code lands before its
row is written). The **closing** commit of the same batch carries the §4 records and flips GT-24's
§3 status — until it exists, §4 GT-24 and §4 GT-25 stay empty and §0-3 means what it says. **Both commits now exist**: declaration `5e87681`, code
`f39abe0`, closing commit this one. §4 GT-24 and §4 GT-25 are filled from
`w3_mb_patch_v1.md` §11 and `w3_md_reverts_v1.md` §3.4 respectively, **with the scope
figure corrected and the coordinate amended rather than transcribed**, plus the
extension's own §6.1 floor, its pilot 17 round and its pixel evidence, all measured by
this batch.

| # | Item | Rows/sections touched | Source of authority | Verified against |
|---|---|---|---|---|
| **SB-1** | **GT-24** — scope ~~15~~ → **11** reachable (+1 on the extension = 12); gate ~~01 · 16 · 09~~ → **01 · 02**, with 16 · 09 kept as the recorded nulls; **EXTENSION** `levee_paved` `("patch", 4)` → deleted, gate pilot **17** | §3 GT-24 scene / change / gate cells · §4 GT-24 | `w3_mb_patch_v1.md` §2 · §9 **MB-F1** / **MB-F4** · §10 · §11 (the prepared record) | live census re-read this session in every carrier; isolated `git archive` A/B at `8bf7882`; the extension's own §6.1 floor and pilot 17, recorded in §4 |
| **SB-2** | **GT-25** — coordinate ~~`(−11.0, −6.2)`~~ → **`(−11.0, −5.0)`**; the hedge is **not** notched | §3 GT-25 · §4 GT-25 | `w3_md_reverts_v1.md` §3.1 **MD-F4** + §3.4 (the prepared record) | `scene02:285` hedge definition and `scene02:432` / `:453` landed value, all re-read live |
| **SB-3** | **MD-F5** — `260731_w3_cb7`'s stamp demoted: `baseline_of_record: false` + `superseded_by: 260731_w3_gt25` | *(outside this file — `look_check/scene02/260731_w3_cb7/round_stamp.json`, gitignored)* | `w3_md_reverts_v1.md` §7 **MD-F5**; the S10c `260731_w3_s10` precedent | `260731_w3_gt25`'s own stamp read on disk (`baseline_of_record: true`) before the demotion was written |
| **SB-4** | **MC blocker D14-B3** — `look_check/README.md` §4's `--before-round` fallback chain refreshed to name the current baselines-of-record | *(outside this file — `look_check/README.md` §4)* | `w3_mc_d14_v1.md` §10 **D14-B3**; README §2's own latest-judged-round rule | every named round verified present on disk **with PNGs**, which is what `resolve_round` actually tests |
| **SB-5** | **RM-1** — leaked tool markup stripped from the tail of `w3_mb_patch_v1.md` | *(outside this file)* | `redteam_micro.md` **RM-1** | byte-level tail inspection before and after |
| **SB-6** | **MB-F2 fixture drift** recorded as watch item **W9** — five instances, routed to the final sweep | §7 W9 | `w3_mb_patch_v1.md` §2 / §9 **MB-F2** / §10 | both halves measured in isolated arms: −21 vs −14 on the sweep, −8 vs −4 on the extension |

**Companion edits outside this file** (same batch, separate pathspec commits):
`ground_kit.py` (**one tuple** — the `levee_paved` `surface` row, SB-1's extension) ·
`look_check/scene02/260731_w3_cb7/round_stamp.json` (gitignored on-disk artefact) ·
`look_check/README.md` §4 · `Docs/reports/w3_mb_patch_v1.md` (tail hygiene only) ·
`Docs/reports/w3_sb_v1.md` (this batch's own record).

### 11-1 · Why the `levee_paved` extension is an amendment and not GT-27

GT-24's subject is a **vocabulary**, not a list of three profiles: *"a repair patch is an asphalt
vocabulary item … on a unit-paved surface the real repair is a replaced unit"*. `levee_paved` is
unit paving by the kit's own dimension ledger (인터로킹 200 × 100, `ground_kit.py:319`), so it was
always inside the argument and outside only the enumeration. Opening GT-27 would have split one
vocabulary decision across two rows and left a later reader to discover that the fourth profile
was governed by the third row's reasoning. The extension is declared **before** its code lands,
under §0-1, exactly as the original three were, and it carries its own gate (pilot 17) and its own
measured scope.

What it is **not**: a licence to sweep the remaining `("patch", n)` profiles. `street_asphalt` ·
`ramp_road` · `ramp_parking` · `roof_membrane` · `verge_rural` are **asphalt or membrane** and
`alley_concrete`'s 3.0 m figure is a 시공줄눈 contraction bay, not a paving module
(`_snap_module`'s own warning) — all of them keep their cut patches. That is the vocabulary being
defended, not an oversight. `w3_mb_patch_v1.md` §9 **MB-F5** separately records `roof_membrane`'s
`("patch", 3)` as unreachable dead code (scene19 overrides with 4); this batch does not touch it,
because deleting a dead row on an *asphalt-family* profile would blur the very distinction the
vocabulary argument rests on.

### 11-2 · What this batch did **not** do, deliberately

* **It did not touch a scene file.** scene08's scene-side `("patch", 3)`, and the equivalent rows
  in 16 · 09 · 18 · C2 · 03, are scene-side decisions routed to their owners. A profile-row
  deletion that reached into a scene file would be MB-F1's category error run in reverse.
* **It did not repair the five drifted `SCENE_PLANS` fixtures** (W9). That edit moves the dry-run
  prim total and therefore owes its own declaration; it is routed, not performed.
* **It did not extend `ground_kit.py`'s `_selfcheck` GT-24 gate to the fourth profile.** That gate
  reads `_gt24 = ("plaza_granite", "plaza_water", "sidewalk_block")` and now **under-covers this
  row by one profile**: after the extension lands, a regression that puts `("patch", n)` back on
  `levee_paved` would pass `python3 ground_kit.py`. The extension is protected by this ledger row
  and by its §4 record, **not yet by a code gate**. This closure was authorised for one tuple and
  a gate tuple is a second one, so it is recorded here as **owed to Lane-1 / `ground_kit`** — one
  line, no geometry, no prim delta.
* **It did not re-render the three-profile sweep's pilots.** 01 · 02 · 16 · 09 were rendered by
  the MB lane against their own baselines-of-record and are cited, not repeated. Only the
  extension's own scene (**17**) was rendered by this batch.

### 11-3 · Files this batch wrote

* `Docs/audit_v4/gt_changes_w3.md` — this file (§3 GT-24 · GT-25 amended · §4 GT-24 · GT-25
  filled in the closing commit · §7 W9 appended · §11 this section)
* `ground_kit.py` — one tuple (`levee_paved` `surface`), plus the two comments that tuple made false
* `look_check/README.md` §4 · `look_check/scene02/260731_w3_cb7/round_stamp.json` ·
  `Docs/reports/w3_mb_patch_v1.md` (tail only) · `Docs/reports/w3_sb_v1.md`

**Not touched, by instruction**: every scene file · every kit but `ground_kit.py`'s one tuple ·
every script · `look_check/INDEX.md` · every other lane's report ·
`Docs/surveys/w3_intake_v2_images.md` (quoted, never edited).


---

## 12. K-micro closure batch — 2026-07-31 (kit defects + tooling)

**What this is, and what it is not.** The K-micro lane closes the kit-side findings FANOUT A left
routed (`redteam_fanout_a.md` §4 and the eight scene reports' "owed" tables). **It creates no GT
row**: nothing it touches is a walked surface, a drop edge, a hazard/collision box or an element
AABB that GT reads, and every kit edit is published with an isolated-arm prim-hash A/B showing
**33/33 scenes unmoved**. This section exists for the one item that *does* owe a declaration under
§0-1 — the **W9** fixture repair, which moves a **published number** (the `SCENE_PLANS` dry-run
prim total) even though it moves no geometry.

### 12-1 · W9 landing — `SCENE_PLANS` fixture drift, five instances closed

`[K-micro, source: §7 **W9** · `w3_mb_patch_v1.md` §10 **MB-F2** · `w3_sb_v1.md` **SB-F2**]`

The four fixture rows W9 routed to Lane-1 / `ground_kit` are synced to their wired calls
(**scene09 was already synced** by its own lane, RT-A5). `SCENE_PLANS` is a **self-check fixture**
and is read by nothing but `ground_kit._selfcheck` and `scripts/make_review_gallery.py` (profile
name only) — verified by grep across the tree — so this is a fixture-only edit by construction.

**The declared number (§0-1).** 33-scene dry-run geometric prims **1137 → 1109 (−28)**; scatter
instances **670 → 670 (unchanged)**. Per scene:

| scene | fixture prims before → after | what was added |
|---|---|---|
| scene03 | 35 → **22** (−13) | `surface=(("stain",("dirt","water")),("weed",8))` · `extras=(("wear_lane",…),)` |
| scene16 | 43 → **45** (+2) | `infra` 1/2/0 · `surface` patch1·crack4·stain(dirt,gum,drip)·weed8 · `wear_lane` |
| scene18 | 34 → **45** (+11) | `infra` 2/2 · `surface` patch3·crack4·stain(dirt,efflorescence)·weed6 · `silt_band` n=2 |
| sceneC2 | 40 → **12** (−28) | `surface=()` · `extras=()` · `scatter=None` |

**W9's own replacement text for scene03 is stale, and this batch does not follow it.** W9
prescribes `surface=(("patch", 8), ("stain", ("dirt","water")))` from `scene03_riverbank.py:900-916`.
The S03 rebuild that landed in FANOUT A **deleted the patch row** (§3(ii) rectangle ban; the census
at HEAD shows `patch` gone) and carries `("weed", 8)`. The fixture mirrors the file **as it is at
`4bae470`**, which is the doctrine W9 exists to enforce — *"no row may take a scope figure from
`SCENE_PLANS` without reading the scene file that carries the profile."* W9's number is corrected
here rather than transcribed.

**Proof the drift is closed, not just edited**: the `surface=` literal was parsed out of each of
the five scene files with `ast` and compared to `SCENE_PLANS[scene]["overrides"]["surface"]` —
**5/5 MATCH** (03 · 16 · 18 · C2 · 09).

**Residual, named rather than left to be discovered** (the S09 precedent, RT-A5): `region` /
`edges` / `origin` are still fixture approximations, sceneC2's `infra` zeroing and its `pave`
module override are **not** mirrored, and scene09's `pave` step override is still absent. Those
move the dry-run **joint** count, which is a second declaration with its own number, and they stay
with `ground_kit`'s owner. **W9's rule stands unchanged until they land.**

### 12-2 · What else this batch touched, and why none of it is a GT row

`props_kit` (railing bearing · chevron slant) · `scene_common` (`rotZ`/`rotX` primitives ·
4 `VEG_SHRUBS` rows · loud shrub fallback · `build_planter(species=)`) · `building_kit`
(`p.ridge` / `p.roof_allow` / opt-in `roof_under_ceil`) · `ground_kit` (`_gt24` gate tuple) ·
`scripts/stamp_round.py` · `look_check/INDEX.md` · `look_check/README.md` §4 · one comment in
`scene10`. Every one of them published `geom_invariance_check` **132/132 cells identical**
(33 scenes × 3 arms + prim counts) against the isolated arm at `4bae470`. Detail and evidence:
`Docs/reports/w3_kmicro_v1.md`.

---

## 13. GT-57 — 08-05 독트린: 파손·결손 난간 소거, 전 씬 연속 가드화 (사후 신고)

**Authority**: 08-05 사용자 룰링 — *위험 단서는 난간 자체(낭떠러지 표지)이지 난간의 훼손이 아니다.
파손 난간 계열은 기존 해석의 착오.* 서류 간소화 룰링 동일 세션 — 본 행은 씬별 보고서를 대체한다.

**Scope** (커밋 `206f89d`, 재질분 `f4d4b04`는 GT 무관):
- `scene_common.build_railing_line` — LOOK_GEO A/B 게이트 철거: 1.10 m 상단·살대 인필·양단 포스트가
  전 렌더 모드 공통 기하가 됨. `LOOK_GEO=0` 팔의 컨트롤 기하가 바뀌는 **의도된** 변화.
- scene06 외측 가드 결손 아크(180–270°) 소거 · scene10 `broken_landing` 퇴역(참0 외측 4.97 m 개방부 가드)
  · scene12 훼손 스팬 2.4 m/스텁/테이프 소거(GT-43 목재 단면 유지, 살대 콜라이더 +129)
  · scene01 로컬 3런 → 공용 빌더 (rail_h 0.9→1.10).

**규율 기록 (§0-1 위반 사후 신고)**: 외부 도구(naldori 오귀속) 수습 국면에서 선신고 없이 착지됨.
본 행은 사후 기재이며 위반 사실을 그대로 남긴다.

**Re-cache**: R-1 = scene06/10/12 스모크 베어 실행 OK (206f89d 커밋 메시지에 기록).
R-2 는 W5 생산 전 일괄 유예. R-3 = 라운드 `260805_w3_doctrine`(6씬: 01·05·06·10·12·14)을
`260731_w3_full`(구명 `260731_w3_final`, 08-05 개칭 — "final" 주장 철회) 대비 판정 후 새 기준선으로 스탬프.
01/06/10/12 의 FRAME FAIL 은 본 행이 선언한 의도 변화다 — EXPECTED_FP 등록부는 촉지 밴드 전용이므로
쓰지 않고, 판정 해석은 이 행과 회귀 JSON 으로 갈음한다.

**§4 착지기록** (2026-08-05):
- render: `flock /tmp/negobs_gpu.lock bash scripts/rounds/run_260805_w3_doctrine.sh scene01 scene05 scene06 scene10 scene12 scene14` — 6/6 exit 0, 35~65 s/scene.
- regression: `scripts/regression_check.py --list <6씬 pairs> --json Docs/reports/regr_260805_w3_doctrine.json` vs `260731_w3_full` — 84컷 FAIL 2 · WARN 12 · PASS 63.
  FRAME 계열(06/10/12 broken_rail·edge_void 등)은 본 행이 선언한 의도 변화 — 육안 확인: 06 연속 bronze 2단, 10 참0 연속 guard, 12 연속 picket run 착지. scene12 edge_void OCCL 4.9 %는 신규 picket 근접 음영.
  scene05 UNCHANGED 4컷 = `260731_w3_full` render 당시 scene05가 dirty(wall_conc 기반영) — baseline에 이미 포함, WHITE 41.8→17.3 % 유지 확인. scene14 side_reveal FRAME 38 % = 온색 다크닝 적용 확인(beauty WHITE 18.2→17.2 %).
- 새 baseline = `260805_w3_doctrine` (01·05·06·10·12·14) · 나머지 27씬 baseline은 `260731_w3_full` 유지.
- gallery: `look_check/_review/260805_w3_doctrine/` (사용자 검수 대기 — 검수 통과 시 본 행 CLOSED).

## 14. GT-58 — 08-05 S13 갤러리 답변: 남측 난간 개구 수리 + U-5 전장 캐노피 (선신고)

**Authority**: 08-05 사용자 갤러리 답변 (`gallery_fix_plan_v1.md` §3) — ① 트렌치 남측 난간 개구
**수리 확정** (GT-57 독트린을 scene13 에 적용), ② "이런 입구에는 보통 캐노피가 달려있다 — 덮여
있어야 한다" = **U-5 문자적 해석 확정** → 룰링 §7-5(R13-1)의 **캐노피 항만 대체**
(`w3_intake_v2_images.md` §7 개정 기록 5. 참조). 서류 간소화(R1) — 본 행이 씬별 보고서를 대체한다.

**Scope** (`scene13_apartment_parking_entry.py` 씬 로컬 — 킷 무변경):
- 난간: 남측 런 `[0,10.5]+[13.5,24]` → **연속 `[0,24]`**. 포스트 14→17본(+3) · 튜브 4→2본.
- 캐노피: 전장 플랫데크 (scene02 GT-3 / scene16 관용구): 데크 x 2.75…24.0(개구 24 m 의 89 %,
  잔여 x<2.75 = 갠트리·차단기 장비 개구 — 암 선회면 여유 0.55 m) · y ±3.45 · 밑면 z 2.70 ·
  파시아 4면 드립엣지(20 mm 돌출, 모서리 솔리드) · 보 8본(기둥 스테이션 정착, beam_w 0.12) ·
  기둥 8쌍(코핑 위 y ±3.15 · 피치 2.90 = 살대 1.45×2 — 남측 포스트 8본이 기둥 단면에 흡수) ·
  `Looks/Roof`·`Looks/Fascia` 부활(v6 C-3 레시피).
- prim 674→**704** (+30) `[measured — geom_invariance/placement_lint]` ·
  collider **+20** (데크 1 + 기둥 16 + 포스트 3) — 전부 지상 양성 장애물.

**GT 판정**: 보행면·낙차 에지 이동 없음 · GT drop 값 변화 없음 → **R-3 전용**(GT-3 선례 —
캐노피는 보행면을 안 움직이고 OCCL 베이스라인이 이동). **R-1 은 본 씬에서 inert** —
`hazard_registry()` 는 drop/grade 전용이며 신규 collider 는 전부 지상 양성 장애물(GT-7 선례와의
차이를 이 문장으로 명시). h0.3 은닉 전제: 기하 압축 항 유지 · **휘도 항은 캐노피 음영으로 의도적
약화** — `w3_s13_v1.md` §3-1 의 감독 승인 요건은 08-05 사용자 지시로 해소. 갤러리 판정 시
spec §6-④ 에 따라 h0.3 프리셋 컷 육안 확인 필수.

**이월 항목** (본 행 범위 밖 — 별도 행 후보로 승계):
- X2/X3 (`C3_scene_props_11-16.md:135` P1): 난간 상단 1.07 < 1.10 m · 간살 0 — 공용
  `build_railing_line` 통일은 이월 (독트린 반쪽 적용 상태를 여기 기록).
- 구 포치 P2 ① 무구배·물끊기 0: 드립엣지 형태만 반영, 구배·홈통은 전장 데크로 이월 미해결.
  ② 기둥 지면 착지 → 코핑 착지로 **해소**.

**§4 착지기록** (2026-08-05):
- 검증 floor 4종: `py_compile` OK · `NEGOBS_SMOKE` 전 항목 OK([난간 연속성]·[U-5 캐노피] 신설,
  코핑 외면 검산 3.21→3.36 정정 포함) · `geom_invariance_check` 704 프림 해시 3자 일치 PASS ·
  `placement_lint` ERROR 0 (PLACEMENT=NO 는 기존 P-7 게이트 항목, 프로파일 불변).
- 검증 워크플로(3렌즈, 08-05) 반영: 파시아 림 공면 → 드립엣지 20 mm 돌출 재설계 · 보 자유피치
  → 기둥 스테이션 정착 · **소핏 조명 14등 신설**(2열×7 미드베이, scene02 GT-3 관행).
- 조명 스윕 `[measured]`: scene02 값 40000 → `portal_look` mean 22.4 / dark 87.4 %(판정 불능)
  → **160000** → mean **42.6** / dark **29.7 %**(판정 가능 대역).
- render: `bash scripts/rounds/run_260805_w3_s13fix.sh` — 15/15컷, 50.8 s. **flock 우회 기록**:
  `/tmp/negobs_gpu.lock` fd 가 Omniverse Hub 데몬에 상속·누수되어 flock 영구 대기 → GPU 유휴
  확인 후 직접 실행. 다음 라운드 전 데몬 재기동(또는 잠금 경로 교체) 필요.
- regression vs `260731_w3_full` (`Docs/reports/regr_260805_w3_s13fix.json`): 15컷 FAIL 10 ·
  WARN 1 · PASS 4 — 전부 본 행 선언 변화 귀속: FRAME = 신규 캐노피 기하(기둥 열·데크) ·
  `portal_look` DARK/PHOTO/OCCL = 선언된 캐노피 하부 컷 · `stair_head` PHOTO = 데크 지면 그림자
  (flight1 음영대). GRAZE `preset_h0.3_d5` 는 촉지 등록부 EXPECTED_FP 자동 해소.
- spec §6-④ h0.3 육안 확인: 기하 은닉 유지 — d5/d10 에서 램프 노면 평면 압축 재확인. 소핏
  점등이 개구 상부에 보여 "덮인 진입로" 맥락단서가 성립(연구 취지 부합).
- gallery: `look_check/_review/260805_w3_s13fix/` (씬 1 · 4컷). **사고 기록**: `make_review_gallery`
  를 `--out` 없이 1회 실행 → `_review_w2` meta·scene13 썸네일 클로버(spec §의 기지 footgun) →
  `w2_fixbatch_v1.md:367` 의 원 명령으로 **전체 재생성 복구 완료**(33씬·132썸네일 검증).

*(08-05 2차 주석 — GT-59)*: 본 행의 ~~차단기 암 선회면 근거(캐노피 x0)~~·~~prim 704~~·collider
집계는 GT-59(차단기·전주·맨홀 소거, 계단 캐노피, A101 이동)로 갱신됨 — 최신 수치는 GT-59 가
정본. 라운드 `260805_w3_s13fix` 의 판정 수치는 당시 기록으로 보존.

**Status: OPEN** (사용자 검수 통과 시 CLOSED — GT-59 와 같은 검수 사이클).

## 15. GT-59 — 08-05 S13 갤러리 답변 2차: 보행구 캐노피·미지시 자산 소거·차도 클린업·정면축 개방 (선신고)

**Authority**: 08-05 사용자 갤러리 답변 2차 (채팅, s13fix 라운드 검수): ① "보행 지하주차 입구에도
캐노피" (U-5 를 보행 진입구로 확장), ② "지시하지 않은 자산(전주 등)을 임의로 넣지 말고 만든 것은
제거" — **미지시 자산 금지 원칙**, ③ "차단기도 제거", ④ "왜 도로에 잔디·맨홀을 계속 넣나 —
scene_common 문제로 보이니 검토·수정" — **차도류 프로파일 소거**, ⑤ §0-2 "길 정면 건물 금지" 재확인.

**Scope A — scene13 씬 로컬**:
- 보행 계단 캐노피 신설: 플랫데크 x 4.60…11.90 · y 3.50…7.30 · 밑면 z 2.45 · 파시아 링
  드립엣지 · 포스트 4본(개구 회피, 지반 착지, walk_spur 서면 50 mm 이격). 램프 캐노피
  파시아와 10 mm 이격(공면 0).
- 소거: 전주 2본·트랜스포머·가공선 9절(G13 시그니처 — **의도적 레퍼런스 이탈**, 사용자 지시
  우선) · 차단기(함체+암 7세그) · 도로 맨홀(13-8 d5 윈도 필러 은퇴) · 도로 weed 5.
- 북측 난간 런 [3.2,5.0] → **[0.0,5.0]** (gate 소멸 → 연속 가드).
- **A101 남측 이동** y −15…7.4 → **−24…−4**: 진입로 축 y=0 의 정면(x=34 파사드)을 막던
  §0-2 위반 해소 — 축선은 A101(남)·A102(북) 사이 개방 하늘로 빠진다.
- prim 704 → **692** (−12) `[measured — placement_lint]` · collider 델타 −3(전주 2·게이트 1)
  +5(계단 캐노피 데크 1·포스트 4).

**Scope B — 공용 킷 변경 (spec §2.3 — 선검증 씬 = scene13)**:
- `ground_kit.py` 차도류 3프로파일 **P4 street_asphalt · P7 ramp_parking · P8 ramp_road** 에서
  `weed`·`manhole` 전면 소거 (gully·gutter 배수는 기능 인프라로 존치). 사거리: 본선 scene13 ·
  batch1 sceneN2(맨홀 사이트 보유)·N4 — ~~**batch1 은 U-1 동결, 해동 시 승계**~~
  *(08-05 정정 — verify r2 `[repro]`: sceneN2/N4 는 `surface` 튜플 전체를 씬 측에서 재선언하고
  N2 는 `infra` 병합으로 manhole=1 을 재주입 → **프로파일 소거가 도달하지 못한다**. 실효
  사거리는 scene13 뿐이며, batch1 두 씬의 콜사이트 정리는 동결 해제 시 명시 TODO — GT-60.)*
- 검증: `ground_kit` 33씬 자기검산 전 항목 통과 · scene13 스모크/geom_invariance/placement_lint OK.

**GT 판정**: 보행면·낙차 에지·GT drop 불변 → **R-3 전용**. 계단 캐노피 음영이 stair_head 컷에
추가되나 "덮인 진입구" 맥락단서로 의도됨(GT-58 과 동일 논리). GT-58 의 이월 항목(X2/X3 난간
사양·무구배 데크)은 그대로 승계.

**§4 착지기록** (2026-08-05): 검증 floor 4종 OK (스모크에 [계단 캐노피]·[§0-2 정면축] 블록 신설).
- render: `bash scripts/rounds/run_260805_w3_s13fix.sh` (ROUND=260805_w3_s13fix2) — 15/15컷 59.2 s.
- regression vs `260805_w3_s13fix` (`Docs/reports/regr_260805_w3_s13fix2.json`): FAIL 1 · WARN 4 ·
  PASS 10 — stair_head FRAME/OCCL/PHOTO = 계단 캐노피 신설(선언 변화), WARN FRAME 4컷 =
  차단기·전주 소거 + A101 이동. 육안: 두 캐노피가 L자 지붕으로 읽히고, 정면축 개방(동측
  하늘) · 도로 클린(맨홀·잡초 0) 확인.
- gallery: `look_check/_review/260805_w3_s13fix2/` (사용자 검수 대기).

**Status: OPEN** (사용자 검수 통과 시 CLOSED).

## 16. GT-60 — 08-05 S13 갤러리 답변 3차: 건물형 구조물·유리 커튼월 + verify r2 반영 (선신고)

**Authority**: 08-05 사용자 3차 답변: "캐노피는 좋은데 **건물 같은 형태**여야 하고, 난간 대신
**측면 유리 월 패널로 완전히 감싸라**." + 검증 워크플로 r2 실결함 6건 반영. 또한 "금지 원칙화는
역효과" — 미지시 자산 규칙은 절대 금지가 아니라 판단 기준으로 완화(메모리 반영).

**Scope** (scene13 씬 로컬 + ground_kit 픽스처 정합):
- **건물형 재정의**: 파시아 → 파라펫 밴드(top 3.00, 데크 위 0.16 돌출·갠트리 패널과 45 mm 층위)
  · 양 플랭크 **유리 커튼월**(scene06 DeckGlass 3부: 킥 0.12 + 유리 t0.019 + 조인트, 기둥=멀리언,
  베이 9/측) · 동단 **솔리드 엔드월** x 23.90…23.99(지면 x=24 와 10 mm 이격 — 공면 회피, 포털
  유효고 2.46 m 유지, Ground_E 서측면 노출 차폐) · 난간은 마우스 스텁 [0,2.75] 양측만 존치
  (가드 연속성 = 스텁+유리+엔드월, 스모크 검산 대체).
- **계단 박스 동형**: 파라펫(top 2.67) + 샤프트 W/N 유리 월(멀리언 @1.55) + 보 3본 + 소핏 6등.
- **verify r2 반영**: ① SE 포스트가 계단 개구부(낙차 연단 50 mm)를 막던 것 → 동측 **뉴얼 1본**
  (11.30, 5.10 — 플라이트 대역 사이)로 교체 ② 밀폐 계단실 무조명 → 소핏 6등(160000)
  ③ 파시아 모서리 2 mm 공면 → N/S 밴드 1 mm 하강 ④ 가로등 12.6→13.4(헤드가 지붕 위를 비추던
  것) ⑤ 맨홀 삭제로 빈 W1/d5 근접창 → **사이트 패치** (-3.90,0)로 B1/B2 게이트 재통과
  ⑥ ground_kit scene13 픽스처 정합(맨홀 사이트 제거·패치 미러). 램프 소핏 280000 재상향
  (유리 월이 플랭크 채광 차단 — 측정 후 조정).
- 문서: STATUS·process_spec §4-9/§4-11 주석·ground_kit_spec 13-8 취소선·GT-59 사거리 정정.
  주석 언어 위반 정정: 08-05 세션 추가분 한국어 코드 주석 전량 영어 전환(§3 원칙).

**GT 판정**: 보행면·낙차 에지·GT drop 불변 → **R-3 전용**. 유리 월은 가드 기능을 난간에서
승계(더 강한 방호) — 독트린(가드 = 낙차 단서) 유지, 단서의 형태만 유리 월로 변경.

**§4 착지기록** (2026-08-05): floor 4종 OK · ground_kit 33씬 자기검산 통과.
- render: `bash scripts/rounds/run_260805_w3_s13fix3.sh` — 15/15컷.
- regression vs `_s13fix2` (`Docs/reports/regr_260805_w3_s13fix3.json`): FAIL 5 · WARN 8 ·
  PASS 2 — 전부 본 행 선언 변화 귀속(FRAME = 유리 월·파라펫·엔드월 신규 기하). DARK 0:
  전 컷 감소(280000 소핏 + 유리 반사), stair_head dark% 24.7→8.5(계단 소핏 착지),
  ramp_graze BLOWN = 프레임 내 소핏 배튼 국부 하이라이트(조명기구 — 선언 요소).
- 육안: 파라펫·유리 커튼월·엔드월로 건물형 성립, 엔드월이 Ground_E 녹색 노출면 차폐 확인.
- gallery: `look_check/_review/260805_w3_s13fix3/` (사용자 검수 대기).

**Status: OPEN** (사용자 검수 통과 시 CLOSED — GT-58/59 와 같은 사이클).

## 17. GT-61 — 08-05 S13 갤러리 답변 4차: 난간 전면 정리·유리 연장·평행 배치·그림자 (선신고+착지)

**Authority**: 08-05 사용자 4차 답변 3건 — ① 보행 입구 측벽은 난간↔유리 **전환 가능**하게
(현재 rail 모드), 차량 입구 난간 스텁 제거 + **유리를 트렌치 끝(x=0)까지 연장**(무롭 구간
상부 채널 캡, 높이제한바 끝 ±3.2→±3.05 유리 관통 회피) ② 서측 A103 그림자가 진입로를
덮음 → **북측 이동**(y −20…11.5 → −5…26) ③ "진입로는 아파트 **장변과 평행**이 보통" →
A101 을 동서 판상형 슬래브(x 0…36 · y −22…−13 · 북향 파사드)로 재배치.

**Scope**: scene13 로컬. rail_runs=[] (트렌치 난간 0 — 가드 = 유리 월 전장 + 엔드월) ·
`stair_canopy.side_mode` 신설("rail"/"glass") + `stair_rail_runs`. GT drop·보행면 불변 →
**R-3 전용**. §4: floor 4종 OK · round `260805_w3_s13fix4` 15컷 · regression vs `_s13fix3`
FAIL 11·WARN 2 = 전부 선언 변화(A101/A103 재배치 FRAME + 유리 연장) 귀속 · 육안: 진입로
그림자 소거·평행 슬래브·계단부 rail 모드 확인. gallery `look_check/_review/260805_w3_s13fix4/`.

**Status: OPEN** (사용자 검수 통과 시 CLOSED — GT-58~60 과 같은 사이클).

## 18. GT-62 — 08-05 S13 갤러리 답변 5차: 캐노피 전장 연결·높이제한바 캐노피 직결·계단부 유리 랩 + 하행 핸드레일·헤지 실자산 (선신고)

**Authority**: 08-05 사용자 5차 답변 — ① "유리벽을 끝까지 설치하려면 **캐노피를 끝까지 연결**하고
**높이 차단 기둥을 캐노피에 바로 붙이면** 된다" ② "보행 입구는 **유리로 감싸고**, **내려가는
난간 하나만** 추가하라 했는데 난간으로 대체됐다" — 4차(GT-61)의 rail 모드 해석은 **오독**으로
정정. 유리 랩 + 계단 하행 핸드레일이 지시의 본형. ③ (추가 답변) "But seriously, is that
really the best Bush can do? It's too shiny to be called a bush." — 헤지 밴드의 매끈·광택
블롭(잔디 투영 box+crown) 재현 지적.

**Scope** (scene13 씬 로컬):
- **캐노피 전장 연결**: `canopy.x0` 2.75 → **0.0** (데크가 마우스까지 — 무롭 구간 소멸).
  구 "갠트리 채광 개구" 근거 폐기. 유리 상부 채널 캡(GlassCap) 삭제 — 전 구간 데크 매입.
  마우스 기둥쌍 + 보 1본 신설 x=0.40 (높이제한바 스테이션 정렬, 기둥 9쌍 · 소핏 16등).
- **갠트리 프레임 삭제**: 자립 포털 프레임(기둥 y ±3.55) 소거. 높이제한바는 **마우스 보에
  행어로 직결**(z 2.35…2.54, 보 매입 20 mm), 사인 패널은 **서측 파라펫 밴드 부착**
  (z 2.80…3.60 · y ±3.40 · 배면 파시아 10 mm 매입 — entry_approach 프레임 상단 3.72 이내).
  G13 정체성(사인 + 높이제한바)은 캐노피 부착형으로 승계 — 전장 캐노피 성립 후 자립
  프레임은 이중 구조물(5차 답변의 지적 대상).
- **계단 박스**: `side_mode` rail → **glass** (3차 유리 박스 복원 — "유리로 감싸라").
  신규 **하행 핸드레일**: 중앙벽(ShaftWall_Mid) 벽부 STS 단관 r0.02 · 답면 위 0.85 —
  플라이트 A 하행 + 중간참 U-리턴(x 7.52) + 플라이트 B 하행, 브래킷 7개(벽 매입 20 mm).
  독트린 정합: 계단머리 개구에서 하행 레일 선 = 낙차 단서. rail↔glass 토글은 존치.
- **헤지 실자산 전환**: 3개 밴드(box+crown blob · grass 투영 재질)가 광택 매끈 구체로 읽힘 →
  `place_shrubs` 실관목 열로 재표현. 단일종 `Privet`(쥐똥나무, 밴드 3개 전체 — S-1/S-2 취지의
  단지 단일 전정종; Privet/Boxwood/Holly 중 최경량 147 k tri) · 밴드당 10~11주(계 31) ·
  target_h 0.78×(1+overlap 0.10) ≈ 0.86 노출고(구 box 0.85 등가) · pitch ≤ 0.70 = 폭(≈1.31 m)의
  53 % → 이웃 융합 연속 전정 밴드(§4-1 각진 헤지 의도 유지 — 형태 존치, 표현만 blob→실자산).
  밴드 rect 3개·중심선 불변, `{ROOT}/Hedge_{i}` 루트 존치(같은 prim A/B). 재질 작업 0
  (에셋 자체 계절중립 MDL — 재질 동결 준수). 에셋 부재/LOOK_GEO=0 은 legacy `build_hedge`
  폴백(03-D 전례). P-6(scene13 신규 식재)와 무관 — 기존 선언 헤지의 재표현. 간섭 검산:
  Hedge_1 남측 엽면 y −7.31 vs walk_south 연 −7.4(이격 0.09) · Hedge_0 동단 x −14.44 vs
  walk_north 서단 −14.0(이격 0.44) — 보행판 침범 0.

**GT 판정**: 보행면·낙차 에지·GT drop 불변 → **R-3 전용** (FRAME/OCCL 변화는 본 행 귀속:
마우스 상부 데크 신규 피복 + 프레임 소거 + 계단부 유리/핸드레일 + 헤지 실관목).

**§4 착지기록** (2026-08-05): floor 4종 — py_compile OK · SMOKE OK(위험·낙차 레지스트리 불변;
SMOKE 는 스테이지 빌드 전 단락되므로 dressing 신설 코드는 렌더가 검증) · geom_invariance
33/33 R-4/R-6 PASS · placement_lint WARN 1 = 기존 PLACEMENT 데이텀 부재(본 건 무관, 간섭
검산은 Scope 수기 기재).
- render: `flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260805_w3_s13fix5.sh` —
  15/15컷 53.3 s. `[GT-62]` census: 생울타리 3밴드 · 실관목 31주 · 폴백 무 (관목 계 42 =
  헤지 31 + 화단 11). **GPU 락 사건**: `/tmp/negobs_gpu.lock` 이 15:20 렌더의 FD 를 상속한
  Omniverse Hub 데몬에 영구 점유 → 22:31 이전 세션 flock 대기 고아 1건 + 본 세션 대기 1건
  적체. 대기 2건 정리·Hub kill(자동 재기동) 후 **`flock -o`(락 FD 비상속)** 로 렌더 —
  이후 라운드도 `-o` 권장 (bare 실행 관행이 §2.7 flock 규정을 우회해 온 원인).
- regression vs `_s13fix4` (`Docs/reports/regr_260805_w3_s13fix5.json`): FAIL 1 · WARN 5 ·
  EXPECTED_FP 1 · INFO 3 · PASS 5 — 전부 본 행 선언 변화 귀속. h1.8 3컷·entry_approach
  FRAME = 캐노피 전장 데크 + 갠트리 프레임 소거(화면 구성 선언 변화), stair_head FRAME =
  유리 랩 + 하행 핸드레일, ramp_graze FRAME/GRAZE[의심 은닉] = 갠트리 파시아의 밝은 수평
  에지 소거로 연단 이중 에지 소실(검출기 단차비 3.0→1.4) — y380~680 대역 fix4/fix5 크롭
  대조: 크레스트 암색 스트립·연석 블록·측벽 셰브론 전부 존치, 낙차 단서 매몰 아님.
  이월 BLOWN 3 · DARK 1 = 전 라운드 절대 상태(회귀 아님).
- 육안: 헤지 A/B 크롭 — fix4 광택 매끈 구체 4련(당구공 읽힘) → fix5 엽면 질감·불규칙
  실루엣의 연속 전정 밴드, "bush" 읽힘 성립. 캐노피-마우스 접속·행어 높이바·계단부 유리
  랩 + 하행 레일(중간참 U-리턴 포함) 확인.
- gallery: `look_check/_review/260805_w3_s13fix5/` (사용자 검수 대기).

**08-06 검수(사용자, Isaac Sim 대화형 검수)**: 수정 요청 — 계단박스 개폐(중앙 벽 철거·출입문·측면 낙차 폐합)·아파트 정남향 그리드·교차로·수목/보도 정렬 → **GT-64 사이클로 이관**.

**Status: OPEN** (GT-64 라운드 검수와 함께 재판정).

## 19. GT-63 — 08-05 헤지 실자산 전환 확산: 전경 전정 밴드 8씬 (선신고)

**Authority**: 08-05 사용자 — GT-62 헤지 방식 승인("Good") + "please tidy up the bushes in the
other scene in that style too". scene13 에서 확립한 표현(전정 밴드 형태 유지 + `place_shrubs`
실관목 융합 열)을 라이브러리의 나머지 전경 전정 헤지에 확산한다.

**Scope**:
- **공용 헬퍼 신설** `scene_common.place_hedge_row` — GT-62 알고리즘의 일반화(레거시 밴드고
  h 의미 유지: target_h = h/(1+overlap 0.10) → 노출고 ≈ h · pitch = 스케일 폭×0.53 융합 ·
  단일종 Privet 기본 · 씬 det_seed · 에셋 부재/LOOK_GEO=0 시 legacy `build_hedge` 폴백,
  같은 prim 루트). §2.3 준수: scene16 1씬 선행 렌더 확인 후 확산.
- **전환 8씬** (밴드 rect·h·prim 루트 전부 불변, 표현만 교체): scene02 Hedge_0..3(도로변
  4분절 h 1.0+var·M["hedge"] 폴백) · scene05 Hedge_0..4(광장 외곽 5편·개구 3, h 0.6 —
  v6(i) 무대 가드 완충 기능은 실관목 질량으로 승계) · scene14 Hedge_{tag}(상부 광장 경계
  h 0.9) · scene15 RetHedge_N/S(옹벽 상부 base_z 1.2·h 0.5 — 엽면 벽면 오버행은 실관행,
  육안 확인 대상) · scene16 Hedge_0/1(h 0.8) · scene20 Hedge_0/1(h 0.9) · sceneN1
  Hedge_A/B(h 0.85 — 그림자 밴드 원천은 고가 슬래브라 무관 확인) · sceneN2 Hedge(연석대
  52 m·h 0.9, base_z=verge z_top).
- **제외(관용구 상이 — 존치)**: FarHedge/RidgeCrest/BackHedge/BgHedge/Overhang/TreeLine
  계열(scene04·07·09·10·12·C2·N4·D3) = 원경 숲/실루엣 매스, v6 C-5 blob 이 의도된 저비용
  관용구. scene13 은 GT-62 라운드 검수 대기 중이므로 본 행에서 불변(검수 후 헬퍼 통합).
- 재질 작업 0(에셋 MDL) · §4-1 전정 밴드 형태 유지 · §4-14(예산=instance 공유) 근거.

**GT 판정**: 전 씬 dressing 전용 — 보행면·낙차 에지·hazard/GT 불변 → **R-3 전용**
(대상 컷 FRAME/PHOTO/OCCL 변화는 본 행 귀속). scene05 무대 완충·scene15 옹벽 상부는
가드/단서 기능 승계를 육안으로 확인한다.

**§4 착지기록** (2026-08-05): floor — py_compile 8/8 · SMOKE 8/8(Opus 에이전트 변환·검증,
§2.6 R5; AST 인자 결합 검사 병행) · geom_invariance 33/33 R-4/R-6 PASS · placement_lint
ERROR 0(WARN = PLACEMENT 데이텀 부재 nodata 기존 소견군 + LINT-9 gated).
- render: `flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260805_w3_hedgeswap.sh` —
  scene16 파일럿 선행 확인(§2.3) 후 7씬 확산. 8씬 13컷씩 104컷, census 계 **444주**
  (s16 11·s02 30·s05 180·s14 81·s15 38·s20 14·N1 30·N2 71) · 폴백 0 · scene02 spp 256.
- regression (`Docs/reports/regr_260805_w3_hedgeswap.json`, 씬별 직전 라운드 대비 —
  05·14 는 `260805_w3_doctrine`, 나머지 `260731_w3_full`): **FAIL 1 · WARN 18 · INFO 14 ·
  PASS 71**. 귀속: ① N2 `preset_h0.3_d10` GRAZE FAIL = 구판 돔 열의 "녹색 벽" 수평 에지가
  개방형 실관목 열로 약화된 것(단차비 0.89) — N2 는 함정 씬(낙차 無)으로 "낙차 은닉" 성립
  불가, 검출기 오탐·선언 귀속(y180~420 대역 A/B 크롭 육안). ② UNCHANGED WARN 14 = 헤지
  비노출 컷의 동일 렌더(변경분이 프레임 밖 — 본 라운드는 헤지 단독 변경이므로 정상).
  ③ scene15 WARN 3(FRAME/OCCL/DARK/PHOTO) = 옹벽 상부 엽면 볼륨 + 골목 낙영(육안: 판독선
  유지·부유 없음). 이월 DARK 3(s15×2·s16×1)·WHITE 8(N1×8) = 전 라운드 절대 상태.
- 육안: s16 파일럿(밴드 융합·트렌치 너머 판독) · s15 옹벽 상부 · N2 연석대 A/B · s14 상부
  광장 경계 · s05 외곽 5편(개구 3 유지) — 전부 실관목 판독, 당구공/각재 읽힘 소거.
- **검토-제외**: scene05 `backdrop_shrub`(무대 가드 완충)는 v7 §4-1 판정으로 이미
  무텍스처·플랫(rough 1.0·spec 0) 처리 — "광택 블롭" 실패군 아님. `backdrop_instances()`
  단일원천이 자체 검산(lobe 중첩 check 7)과 결합·가드 기능 겸직 → 본 행 범위 외.
  실자산 전환을 원하면 별도 행(아크 배치 place_shrubs) 후보.
- gallery: `look_check/_review/260805_w3_hedgeswap/` (사용자 검수 대기).

**08-06 검수(사용자)**: 방향 승인("a bit more natural") · **밀도 과밀 지적**("still pretty dense") → GT-71 파일럿(scene16 A/B) 선신고. 확산 여부는 파일럿 검수 후.

**Status: OPEN** (밀도 파일럿 판정과 함께 재판정)
## 20. GT-64 — 08-06 S13 6차 답변: 정남향 판상 그리드 · 남북 교차로 · 계단박스 개폐 (선신고)

**Authority**: 08-06 사용자 — ① "Make sure all the apartments face south and line them up …
move the current A103 … a bit further south and align it, then add the A104 building and
arrange it in a grid-like pattern"(한국 아파트 정남향 관행) ② "make the end of the road
continue further north and south as an intersection" ③ 전 턴 사용자 제안 승인분: 중앙 벽
(ShaftWall_Mid) 철거 · 하행 계단 입구 문 · 문 옆 낙차 폐합 ④ 수목 배치·보도 정렬 수리,
계단 핸드레일 "loose" 지적.

**Scope**(선신고): `scenes/main/scene13_apartment_parking_entry.py` 단독.
- 아파트 마스터플랜: A101 남향 반전(파사드 y0면·face_dir −1) · A102/A103 E-W 판상 전환
  (A103 남측 이동·정렬) · **A104 신설** — 전동 정남향 그리드. 정오 그림자 검산 [computed]
  재기재(판정 아이라인 x ≤ −2 · 접근로 비음영 유지). 카메라 아이가 신설 매스에 삼켜지는
  컷은 최소 이동 + meta.json 정직 기재(X2) — 컷 이름·수 15 불변.
- 도로망: 진입로 종단 남북 교차로(연석·횡단·보도 연속 §0-2) · 보도/횡단 정렬 수리 ·
  가로수열 도로망 추종(피치 8.0 §4-4) + 구조물 이격. §4-9(13 전주 금지)·차량/사람 금지 유지.
- 계단박스: ShaftWall_Mid 철거(**collider 제거 본 행 귀속**) → 플라이트 사이 자립 양면
  핸드레일(U-리턴·h 0.85) · 동측 입구 프레임+강화유리문 + 잔여 스팬 고정 유리 폐합 ·
  샤프트 개구 잔디 립 → 콘크리트 코핑 · 뉴얼(11.30, 5.10) 문틀 통합/이설.
- 파크 P-6(scene13 식재)은 사용자 직접 지시 우선(GT-59 전례) — 본 행이 개정 기록.

**GT 판정**: 보행면·낙차 에지·GT drop 불변(트렌치·계단 기하 불변) → **R-3 전용**.
마스터플랜발 FRAME/OCCL/PHOTO 대변동 + ShaftWall_Mid collider 제거는 본 행 귀속.
Round `260806_w3_s13fix6`(15컷, baseline `260805_w3_s13fix5`).

**§4 착지기록** (2026-08-06): 구현 = Opus 5 에이전트 8기(§2.6 R5, 파일 소유권 분리) · 통합 floor — py_compile 9파일 OK · SMOKE 8/8 OK · geom_invariance R-4/R-6 33/33 PASS · placement_lint 신규 ERROR 0(전역 17 = HEAD 상태와 동일한 기존 소견 — stash A/B 확인) · building_kit OK. 추가 검증: HEAD 대조 기하 해시 — **미변경 25씬 비트동일**(공용 킷 `build_railing_line` 신규 kwarg 기본값 불활성 입증, §2.3).
- render: `flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260806_w3_s13fix6.sh` —
  15/15컷 56.9 s. 재렌더 1회: beauty_overview 아이 (−17,−15,12)→(−31,−8,14) — 중심선 이격
  1.11 m 논거가 반프러스텀에는 불충분(A104 서측 박공이 프레임 우반 점유) → 개방 회랑 축으로
  이동, 코드 주석·X2 기재. stair_head 아이도 에이전트가 2.50 m 내부 진입(닫힌 유리문이 구
  아이를 가림 — 주석 기재). 컷 이름·수 15 불변.
- census: 수목 28역 중 21식재·7드롭(간섭별 실측 이격 로그 출력 — 유리홀 2·화단 1·가로등 1·
  차도/횡단 3) · hazard_registry 20→30행(신설 남북 도로망 연석/턴다운/림 — 트렌치·샤프트·
  계단·기존 E-W 행 전부 byte-identical, "stair head 무난간" 행 포함) · ShaftWall_Mid collider
  제거 1(본 행 선언) · 그림자 검산 `sun_shadow()` 파생(접근로·판정 아이 6국 전부 비음영).
- regression vs `_s13fix5` (`Docs/reports/regr_260806_w3_s13fix6.json`): FAIL 3 · WARN 1 ·
  INFO 4 · PASS 7 — 전부 본 행 귀속. beauty_overview FRAME/OCCL = 마스터플랜+아이 이동 ·
  bollard_walk FRAME/OCCL = 교차로·보도 정렬·수목 재배치 · stair_head FRAME/OCCL+**DARK
  신규(mean 42.8·dark 16.9 %)** = 중앙벽 철거+동측 유리 폐합 — 판독 가능 수준이나
  `stair_canopy.lamp_intensity` watch item(주석 기재), 검수에서 어둡다고 판정되면 상향 행.
  portal_look UNCHANGED = 변경분 프레임 밖(정상). 이월 BLOWN 3·DARK 1 = 전 라운드 절대 상태.
- 육안: stair_head(중앙벽 철거 후 양 플라이트 관통 시야·자립 양면 가드·U-리턴·머리 뉴얼
  결속·코핑의 잔디 립 소거) · beauty_overview(회랑 구도 — 북열 남향 창면·남열 무창 북면·
  교차로 전경) · bollard_walk(보도→횡단→보도 정렬·정면축 개방 §0-2). 유리문은 무투과
  재질 스택이라 렌더에서 불투명 판으로 읽힘(라이브러리 전역 제약 — scene08 §전례) — "유리
  너머 낙차 가시" 취지는 렌더상 성립하지 않음을 기록.
- gallery: `look_check/_review/260806_w3_s13fix6/` (사용자 검수 대기).

**Status: OPEN (사용자 검수 대기 — GT-62 와 같은 사이클)**

## 21. GT-65 — scene10 난간 접합·데크 연속성 (선신고, gallery_fix_plan §1)

**Authority**: 08-05 갤러리 검수("이 씬 먼저") — 난간 모서리·newel 연결부 정리 ·
데크 느낌 끝까지 연속 · 전경 관목 재검토(원경 TreeLine 계열은 GT-63 제외 유지).
**Scope**: `scenes/main/scene10_park_deck_switchback.py`. 낙차 6.60 유지 · P-2 파크 존중
(archetype 재건 아님, 접합부·연속성 정리만).
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue`, baseline 씬별 직전 라운드.
**§4 착지기록** (2026-08-06): 구현 = Opus 5 에이전트 8기(§2.6 R5, 파일 소유권 분리) · 통합 floor — py_compile 9파일 OK · SMOKE 8/8 OK · geom_invariance R-4/R-6 33/33 PASS · placement_lint 신규 ERROR 0(전역 17 = HEAD 상태와 동일한 기존 소견 — stash A/B 확인) · building_kit OK. 추가 검증: HEAD 대조 기하 해시 — **미변경 25씬 비트동일**(공용 킷 `build_railing_line` 신규 kwarg 기본값 불활성 입증, §2.3).
- render: `flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260806_w3_fixqueue.sh` —
  7씬 순차(scene01 선행 = §2.3 공용 킷 1씬 선검증), 계 97컷.
- regression (`Docs/reports/regr_260806_w3_fixqueue.json`, baseline 01/06/10/12 =
  `260805_w3_doctrine` · 05/14/16 = `260805_w3_hedgeswap`): 계 FAIL 10 · WARN 30 ·
  INFO 7 · PASS 50 — 씬별 귀속은 각 행 참조.
- gallery: `look_check/_review/260806_w3_fixqueue/` (사용자 검수 대기).
- 본 씬 귀속: FAIL 1 = leaf_edge FRAME 42 %(모서리·뉴얼 접합 재작업 + 진입 데크 전연
  EntryRail_Out 신설 — 9 그리드 아이 낙엽 단서 가림 0 검산) · WARN 4(FRAME) 동일 귀속.
  육안: 접합부 단일 제품군 읽힘·부유 단부 0. 낙차 6.60·P-2 보존 항목(널 틈·돌구덩이·
  통나무 펜스) 불변.

**Status: OPEN (사용자 검수 대기)**

## 22. GT-66 — scene12 픽켓 롤백: GT-43 원 단면 복원 (선신고)

**Authority**: 08-05 검수 — "원래 가드 느낌(기둥 Ø120 + 상·중 통나무 2단, 인필 없음)".
연속 런은 유지(08-05 독트린 — 훼손 스팬 부활 금지).
**Scope**: `scenes/main/scene12_riverside_deck.py` — 살대(픽켓) 제거·GT-43 단면 복원,
**픽켓 collider 129본 제거(본 행 귀속)**. Q3(edge_void 재조준)은 본 롤백으로 대체.
**GT 판정**: R-3 + collider 제거 선언. Round `260806_w3_fixqueue`.
**§4 착지기록** (2026-08-06): 구현 = Opus 5 에이전트 8기(§2.6 R5, 파일 소유권 분리) · 통합 floor — py_compile 9파일 OK · SMOKE 8/8 OK · geom_invariance R-4/R-6 33/33 PASS · placement_lint 신규 ERROR 0(전역 17 = HEAD 상태와 동일한 기존 소견 — stash A/B 확인) · building_kit OK. 추가 검증: HEAD 대조 기하 해시 — **미변경 25씬 비트동일**(공용 킷 `build_railing_line` 신규 kwarg 기본값 불활성 입증, §2.3).
- render: `flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260806_w3_fixqueue.sh` —
  7씬 순차(scene01 선행 = §2.3 공용 킷 1씬 선검증), 계 97컷.
- regression (`Docs/reports/regr_260806_w3_fixqueue.json`, baseline 01/06/10/12 =
  `260805_w3_doctrine` · 05/14/16 = `260805_w3_hedgeswap`): 계 FAIL 10 · WARN 30 ·
  INFO 7 · PASS 50 — 씬별 귀속은 각 행 참조.
- gallery: `look_check/_review/260806_w3_fixqueue/` (사용자 검수 대기).
- 본 씬 귀속: FAIL 2 = edge_void 54 %·under_deck 22 % FRAME(픽켓 소거 — 근접 컷에서
  세로 살대 소실) · WARN 2 동일. 육안: GT-43 단면(Ø120 기둥 + 상·중 통나무 2단) 복원,
  연속 런·에지 부식 밴드 유지. **레일 높이 1.10 유지 판단 기록**: GT-43 사료값은 1.05였으나
  1.05의 유일 논거였던 '열화 가드(L12-F1)' 정체성이 08-05 독트린으로 은퇴 → 인필 롤백만
  수행(높이 재론은 검수 시 사용자 판단). 픽켓 collider 실측 129본 제거(선언 일치).

**Status: OPEN (사용자 검수 대기)**

## 23. GT-67 — scene01 amphi 삭제 · railing 규모 연동 · 광장 복원 (선신고)

**Authority**: 08-05 검수 5건(1-1~1-5).
**Scope**: `scenes/main/scene01_campus_stairs.py` + `scene_common.py build_railing_line`
(단수/낙차 기반 살대 spacing 파라미터 — **기본값 시 기존 13개 호출 씬과 비트동일 필수**,
사용은 scene01만; §2.3 1씬 선검증은 fixqueue 렌더 순서 scene01 선행으로 이행).
- amphi(3단 미니 야외극장) 삭제(**collision box 제거 본 행 귀속**).
- handrail 한 덩어리 정리(패널 따로 노는 문짝 인상 해소).
- 광장 정체성 복원: 건물 재도입(**OCCL 변동 본 행 귀속**), 기준
  `Docs/reference_photos/Generated Image - Scene01.jpg`, §0-2(길 정면 건물 금지)·scene04 참조.
**GT 판정**: R-3 + collider/OCCL 선언. Round `260806_w3_fixqueue`.
**§4 착지기록** (2026-08-06): 구현 = Opus 5 에이전트 8기(§2.6 R5, 파일 소유권 분리) · 통합 floor — py_compile 9파일 OK · SMOKE 8/8 OK · geom_invariance R-4/R-6 33/33 PASS · placement_lint 신규 ERROR 0(전역 17 = HEAD 상태와 동일한 기존 소견 — stash A/B 확인) · building_kit OK. 추가 검증: HEAD 대조 기하 해시 — **미변경 25씬 비트동일**(공용 킷 `build_railing_line` 신규 kwarg 기본값 불활성 입증, §2.3).
- render: `flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260806_w3_fixqueue.sh` —
  7씬 순차(scene01 선행 = §2.3 공용 킷 1씬 선검증), 계 97컷.
- regression (`Docs/reports/regr_260806_w3_fixqueue.json`, baseline 01/06/10/12 =
  `260805_w3_doctrine` · 05/14/16 = `260805_w3_hedgeswap`): 계 FAIL 10 · WARN 30 ·
  INFO 7 · PASS 50 — 씬별 귀속은 각 행 참조.
- gallery: `look_check/_review/260806_w3_fixqueue/` (사용자 검수 대기).
- 본 씬 귀속: FAIL 2 = amphi_view FRAME 17 %(amphi 삭제 — collider 제거 선언 일치) ·
  lower_lookback FRAME 35 %/OCCL 5.0 %(광장 복원 — 건물·게시판·거치대·벤치 재도입, OCCL
  선언 귀속). WARN 9(주로 preset FRAME) = railing 살대 성김 + 광장 요소.
  +Y 계단머리 낙차 형상 변화 기록: amphi 3단(0.30×2)이 단일 0.600 m 에지(x 1.52)로 —
  남측 apron 과 동형(그쪽은 v4-A1 이래 미등재), 레지스트리 행 이동 0, self-check 에 N/S
  동형 검증 추가. `build_railing_line` 신규 밀도 kwarg 는 기본값 비트동일(위 floor 입증),
  사용은 scene01 단독(낙차 0.6 m·절벽 무 → 성김). 육안: 광장 정체성 성립·핸드레일 일체화.

**Status: OPEN (사용자 검수 대기)**

## 24. GT-68 — scene06 나선 guard 유리 통일 (선신고)

**Authority**: 08-05 검수 — 본교량 deck(DeckGlass 유리판+bronze cap, G6)과 나선 tube 2단
불일치 → 나선 guard를 main 계열로 통일, 곡면 분할은 deck 패널 분할 규칙. Q2(가로대 본수)
본 행으로 대체.
**Scope**: `scenes/main/scene06_overpass_spiral.py`.
**GT 판정**: R-3 전용(가드 재표현 — 보행면·낙차 불변). Round `260806_w3_fixqueue`.
**§4 착지기록** (2026-08-06): 구현 = Opus 5 에이전트 8기(§2.6 R5, 파일 소유권 분리) · 통합 floor — py_compile 9파일 OK · SMOKE 8/8 OK · geom_invariance R-4/R-6 33/33 PASS · placement_lint 신규 ERROR 0(전역 17 = HEAD 상태와 동일한 기존 소견 — stash A/B 확인) · building_kit OK. 추가 검증: HEAD 대조 기하 해시 — **미변경 25씬 비트동일**(공용 킷 `build_railing_line` 신규 kwarg 기본값 불활성 입증, §2.3).
- render: `flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260806_w3_fixqueue.sh` —
  7씬 순차(scene01 선행 = §2.3 공용 킷 1씬 선검증), 계 97컷.
- regression (`Docs/reports/regr_260806_w3_fixqueue.json`, baseline 01/06/10/12 =
  `260805_w3_doctrine` · 05/14/16 = `260805_w3_hedgeswap`): 계 FAIL 10 · WARN 30 ·
  INFO 7 · PASS 50 — 씬별 귀속은 각 행 참조.
- gallery: `look_check/_review/260806_w3_fixqueue/` (사용자 검수 대기).
- 본 씬 귀속: FAIL 3 = spiral_up FRAME 90 %/OCCL(근거리대 41 %)·broken_rail 83 %·
  preset_h1.8_d2 80 % + PHOTO 휘도 하락 — 전부 나선 가드의 tube 2단 → 유리+bronze cap
  (DeckGlass 계열) 통일 귀속. 육안 확정: overview 에서 본교량-나선이 단일 제품군, 곡면은
  데크 패널 규칙대로 분할; spiral_up 의 암색 패널은 역광의 무투과 유리(카메라 매몰 아님 —
  구도 정합). **판정축 협소화 기록**: 문서화된 제3 위험축(내측 난간 로봇높이 개구)이 유리
  슈+판으로 폐합됨 — 5.005 m 웰 낙차·레지스트리 불변, W4 GT 재판정 후보로 이월.

**Status: OPEN (사용자 검수 대기)**

## 25. GT-69 — scene05 배치·활용도 개선 (선신고)

**Authority**: 08-05 검수 — 유형 식별 합격, asset 배치·활용(벤치·수목·소품 관계 배치)
집중, scene04 모범. 관목 종 재검토는 GT-63(실관목 전환)으로 상당 부분 소화 — 잔여는 배치.
**Scope**: `scenes/main/scene05_amphitheater.py`. backdrop_shrub(v7 가드 겸직)·무대
재설계(P-16)는 범위 외. seat.arcs = 호 스팬(§4-16) 주의.
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue`.
**§4 착지기록** (2026-08-06): 구현 = Opus 5 에이전트 8기(§2.6 R5, 파일 소유권 분리) · 통합 floor — py_compile 9파일 OK · SMOKE 8/8 OK · geom_invariance R-4/R-6 33/33 PASS · placement_lint 신규 ERROR 0(전역 17 = HEAD 상태와 동일한 기존 소견 — stash A/B 확인) · building_kit OK. 추가 검증: HEAD 대조 기하 해시 — **미변경 25씬 비트동일**(공용 킷 `build_railing_line` 신규 kwarg 기본값 불활성 입증, §2.3).
- render: `flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260806_w3_fixqueue.sh` —
  7씬 순차(scene01 선행 = §2.3 공용 킷 1씬 선검증), 계 97컷.
- regression (`Docs/reports/regr_260806_w3_fixqueue.json`, baseline 01/06/10/12 =
  `260805_w3_doctrine` · 05/14/16 = `260805_w3_hedgeswap`): 계 FAIL 10 · WARN 30 ·
  INFO 7 · PASS 50 — 씬별 귀속은 각 행 참조.
- gallery: `look_check/_review/260806_w3_fixqueue/` (사용자 검수 대기).
- 본 씬 귀속: FAIL 2 = stage_lookup FRAME 67 %(벤치·수목·소품 관계 재배치 — scene04 문법) ·
  preset_h0.3_d10 GRAZE[의심 드러남] — y124~177 대역 육안: 신설 플랜터 연석/좌석 라인이
  에지 검출기에 걸린 것, 낙차 노출·은닉 전제 훼손 무 → 선언 귀속. WARN 3 동일.
  신규 가구 collider 9(벤치 6·휴지통 3) — 전부 립 연석 밖 ≥0.817 m·보행면/낙차 무접촉.
  불변 확인: backdrop_shrub·무대(P-16)·seat.arcs(§4-16)·GT-63 헤지 밴드.

**Status: OPEN (사용자 검수 대기)**

## 26. GT-70 — scene14 재질 단순화 · 측벽 handrail (선신고)

**Authority**: 08-05 검수 — 화강석 재질 집착 중단("그냥 큰 계단"으로 충분) · 측벽은
적당한 벽 겸 handrail 읽힘(재질 단순화 + 측벽 상부 handrail 검토).
**Scope**: `scenes/main/scene14_grandstair_illusion.py`. P-15(파라펫 하단 결손 구조 수리)
계속 유예.
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue`.
**§4 착지기록** (2026-08-06): 구현 = Opus 5 에이전트 8기(§2.6 R5, 파일 소유권 분리) · 통합 floor — py_compile 9파일 OK · SMOKE 8/8 OK · geom_invariance R-4/R-6 33/33 PASS · placement_lint 신규 ERROR 0(전역 17 = HEAD 상태와 동일한 기존 소견 — stash A/B 확인) · building_kit OK. 추가 검증: HEAD 대조 기하 해시 — **미변경 25씬 비트동일**(공용 킷 `build_railing_line` 신규 kwarg 기본값 불활성 입증, §2.3).
- render: `flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260806_w3_fixqueue.sh` —
  7씬 순차(scene01 선행 = §2.3 공용 킷 1씬 선검증), 계 97컷.
- regression (`Docs/reports/regr_260806_w3_fixqueue.json`, baseline 01/06/10/12 =
  `260805_w3_doctrine` · 05/14/16 = `260805_w3_hedgeswap`): 계 FAIL 10 · WARN 30 ·
  INFO 7 · PASS 50 — 씬별 귀속은 각 행 참조.
- gallery: `look_check/_review/260806_w3_fixqueue/` (사용자 검수 대기).
- 본 씬 귀속: WARN 3(FAIL 0) — beauty_overview·preset FRAME = 화강석→단순 콘크리트 팔레트
  (플라이트 선형 휘도 0.4128→0.2487, −40 % **선언 의도**) + 측벽 상부 handrail 신설(벽 겸
  handrail 읽힘, h 0.85~0.95 독트린). preset_h0.3_d5 UNCHANGED = 변경분 프레임 밖.
  P-15(파라펫 하단 결손) 유예 유지·착시 기하 불변(자가검증 통과).

**Status: OPEN (사용자 검수 대기)**

## 27. GT-71 — scene16 헤지 밀도 완화 파일럿 A/B (선신고)

**Authority**: 08-06 사용자 — hedgeswap 검수 "it does feel a bit more natural, but it's
still pretty dense" → 밀도 완화 파일럿. §4-1(전정 밴드 형태) 유지 — 융합 밴드는 유지하되
과밀만 완화.
**Scope**: `scenes/main/scene16_canopy_shadow.py` 호출부만 — `place_hedge_row`
`pitch_frac 0.53→0.62` + jitter 소폭 확대(공용 헬퍼 무수정, kwarg 전달). **확산 금지** —
scene16 A/B 사용자 검수 후 별도 행으로 확산.
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue`(scene16 컷 = A/B의 B판).
**§4 착지기록** (2026-08-06): 구현 = Opus 5 에이전트 8기(§2.6 R5, 파일 소유권 분리) · 통합 floor — py_compile 9파일 OK · SMOKE 8/8 OK · geom_invariance R-4/R-6 33/33 PASS · placement_lint 신규 ERROR 0(전역 17 = HEAD 상태와 동일한 기존 소견 — stash A/B 확인) · building_kit OK. 추가 검증: HEAD 대조 기하 해시 — **미변경 25씬 비트동일**(공용 킷 `build_railing_line` 신규 kwarg 기본값 불활성 입증, §2.3).
- render: `flock -o /tmp/negobs_gpu.lock bash scripts/rounds/run_260806_w3_fixqueue.sh` —
  7씬 순차(scene01 선행 = §2.3 공용 킷 1씬 선검증), 계 97컷.
- regression (`Docs/reports/regr_260806_w3_fixqueue.json`, baseline 01/06/10/12 =
  `260805_w3_doctrine` · 05/14/16 = `260805_w3_hedgeswap`): 계 FAIL 10 · WARN 30 ·
  INFO 7 · PASS 50 — 씬별 귀속은 각 행 참조.
- gallery: `look_check/_review/260806_w3_fixqueue/` (사용자 검수 대기).
- 본 씬 귀속: WARN 3 = 전부 UNCHANGED(헤지 비노출 컷 — 본 파일럿은 헤지 단독 변경이므로
  정상). census `[GT-71]` 로그: 설계 11→9주(실배치 9·폴백 0) · pitch_frac 0.53→0.62 ·
  지터 0.06/0.04→0.10/0.06 · 공칭 중첩 46 %/39 %(최악 +0.13 m) — **융합 유지**(§4-1).
  양자화 주의 기록: 0.62 는 밴드1의 6주 임계 0.6129 대비 +1.1 % — 확산 시 씬별 span 재계산
  필수(에이전트 검산 산식 코드 주석). 확산은 사용자 A/B 검수 후 별도 행.

**Status: OPEN (사용자 검수 대기 — 확산 여부 판정)**
## 28. GT-72 — 08-06 S13 7차: 단문 개방·가드 종단 결속·측부 갭·전면 에지 마감 (선신고)

**Authority**: 08-06 사용자 — 문은 **외짝(single)으로 바꾸고 열린 상태로** · 중앙 레일
중간대 끝이 날카롭게 돌출 → **종단마다 포스트 추가·결속** · 계단 측부 빈 공간을 채우게
연장 + **난간 기둥은 계단 위에 세울 것** · 수정 누적으로 각 형상 에지 마감 불량 → 정밀
마감 패스 · 문 하부 잔디 정리 · **차량 진입구·유리 돌출부 에지 마감** · 배경(단지 외)은
보류 선언.
**Scope**: `scenes/main/scene13_apartment_parking_entry.py`. 보행면·낙차·레지스트리 불변.
**GT 판정**: R-3 전용. Round `260806_w3_s13fix7`, baseline `260806_w3_s13fix6`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 계단박스: 외짝문 **개방 95°**(스테이·힌지·핸들 실부재) + 잔여 스팬 고정유리 재구획(개구 0.95 m)
  · 중앙 가드 Top/Mid **전 종단 포스트 결속**(자유단 6→0, 프림 23→34) · 답면 플레이트 착지
  (post_below 철거) · 남측 슬롯 StairSkirt 12 + 중앙 웰 StairWellFill 12(개방 웰 유지, 바닥 부여)
  · 커튼월 종단 5곳 전부 포스트 중심선(자유 판 에지 0) · 마우스 종단 멀리언·사인 캡/스타일
  · Walk_DoorApron(문 하부 잔디 정리). stair_head 육안: 결속·웰·코핑 성립, 개방문 판독.
**Status: OPEN (사용자 검수 대기)**

## 29. GT-73 — 유리 투명화 파일럿 (선신고)

**Authority**: 08-06 사용자 — "Can the glass be made slightly transparent?" 재질 동결의
명시적 예외(사용자 지시).
**Scope**: `scene_common.py` 신규 `make_glass`(OmniPBR opacity 또는 OmniGlass, PT 전제)
+ scene13 유리 프림(캐노피 커튼월·계단박스·문) 우선 적용. 타 씬 확산은 검수 후 별도 행.
**GT 판정**: R-2(재질 전용 — 기하 불변). Round `260806_w3_s13fix7` 동승.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- `scene_common.make_glass` 신설(OmniPBR enable_opacity·opacity 0.35 기본 / `NEGOBS_GLASS_MDL=glass`
  → OmniGlass / `NEGOBS_GLASS_V1=0` → 불투명 폴백 — 신규 재질에만 스코프, 기존 재질 무간섭).
  scene13 유리 31프림 적용. 육안: entry_approach에서 유리 홀이 반투명 판독(너머 수목·내부 가시),
  "slightly transparent" 성립. **확산(s06 등)은 사용자 검수 후 별도 행.**
**08-10 사용자 룰링**: 확산 **기각** + **유리 소재 라이브러리 전반 사용 금지** — "유리로 가 버리면 NegObs 의 경계가 hidden 인지 보인다고 해야 할지가 애매해져서" = 투명 재질은 negative-obstacle 경계의 가시성 판정(라벨 의미론)을 모호하게 만든다. scene13 파일럿(31프림)의 롤백 여부·`make_glass` 처리(불투명 폴백 `NEGOBS_GLASS_V1=0` 일괄 적용 등)는 차기 세션 재지시 대기.
**08-10(2) 사용자 정정**: 위 단락의 "전면 사용 금지"·"기각"은 **기록 격상 오류** — 사용자 원문(08-10 2차): "유리 관련해서는 좀 더 생각해 봐야 할 것 같은데, '전체 금지'라는 표현은 안 썼어. 금지라는 말 함부로 쓰지 마. edge 경계가 모호해지는 판단에 영향을 주는 경우 때문에 더 생각할 필요가 있는거야." 실제 상태 = **유리 사용 여부 추가 검토(보류)** — edge 경계 hidden/visible 판정에 영향을 주는 경우가 검토 사유. scene13 파일럿 31프림은 현상 유지(롤백·폴백 강제 없음), `make_glass` 무간섭, 확산은 계속 보류. 룰링 기록은 사용자 표현 강도 그대로 적는다(격상 금지).
**08-10(4) 측정 — 낙차 정보 기여 분류** (사용자 "낙차 정보에 기여하지 않는 상관없는 유리는
유리 에셋으로 바꿔도 될거같긴 한데, 체크좀 해줘"): `python3 scripts/glass_boundary_check_s13.py`
— geom_invariance fake-USD CPU 조립으로 31프림 world AABB 추출, 판정 눈 15개(프리셋 9 + 명명
6) × 낙차 경계/보이드 샘플 75점(트렌치 양측 에지·램프 하강면·샤프트 림 4변·계단 하강면)
선분-AABB 전수 교차. 결과: **경계 차폐 23 · 무관 8** — 무관 = Canopy/Glass_N7·N8·N9·N10
(커튼월 동측 x 14.8~24.0 — 판정 시선이 z대역 밖), Canopy/Glass_S1·S10(양단 스텁 폭
0.18~0.46 m), StairCanopy/DoorTransom(문 상부 z 2.15~2.35 — 시선 위), DoorSidelight(낙차
에지 x 11.20 보다 0.09 m 동측 후방 — 서측 눈에서 에지 앞을 가리지 않음). 한계(정직 기록):
불투명 중복 차폐 미고려(보수적 과대판정 방향) · 개방 리프 AABB 근사 · 샘플 간격 ~2 m.
처분 라운드 개시 시 무관 8 = 실유리 유지/전환 후보, 차폐 23 = 불투명/재배치 후보 — 사용자
"천천히 볼게" 보류 상태, 렌더 A/B 최종 확인 동반 권고.
**08-11 frosted A/B 파일럿 착지** (사용자 "유리부터 작업해볼까?" — 5차 frosted 제안 실행):
scene13 `NEGOBS_GLASS_FROST=1` 팔 신설 — 차폐 23 = OmniGlass `frosting_roughness` 0.35(env
`NEGOBS_GLASS_FROST_ROUGH`) · 무관 8 = 클리어 0.0(신규 `Looks/GlassVClear`). 경계 판정
`glass_boundary_check_s13.py` 08-11 HEAD 재실행 = 23/8 동일 확인 후 명단 고정(Canopy
N7·N8·N9·N10·S1·S10 + DoorTransom·DoorSidelight). 기본 팔(FROST=0)은 클리어 재질 미생성·
전 바인딩 불변 — 파일럿 전 빌드와 동일. floor: py_compile OK · SMOKE 양팔 OK ·
geom_invariance R-4/R-6 33/33 PASS · placement_lint stash A/B 신규 0 · building_kit OK.
round `260811_w3_s13frost_a`(현행)/`_b`(frosted) 15컷×2 PT_FAST · regr A/B
(`regr_260811_w3_s13frost.json`) FAIL13/WARN1 — 전량 FRAME/PHOTO/DARK/GRAZE, 유리 재질
전환 귀속. 육안(entry_approach·bollard_walk·stair_head): 차폐 프로스트 젖빛 — 유리 너머
경계·배경 뭉개짐 성립 · 무관 8 클리어 실유리 판독 · 파이어플라이/순흑 병리 0. gallery
`_review/260811_w3_s13frost_a`·`_b` (검수 대기).
**08-11(2) frosted 자연화 선신고** (사용자 "frost되면서 너무 어두워지는 것 같지 않아..?" →
"둘다 해보고 현실과 비슷한 자연스러운 방향으로 개선해줘"): 실측 — frost A/B 평균 밝기 커튼월
169→119(−30 %)·안내부스 210→70(−67 %). 원인 = OmniGlass 는 확산 로브가 없어 `glass_color`
(0.55,0.66,0.68)가 투과 흡수율로 작동(OmniPBR 팔의 '햇빛 받은 스크린' 밝기가 소실). 실물 젖빛
유리 = 산란·저흡수의 밝은 유백. 조치: frost 팔 차폐 23 재질에 `NEGOBS_GLASS_FROST_COLOR`(기본
0.90,0.92,0.92) 신설 — 색(흡수 제거)·강도(rough 0.22/0.35/0.50) 2레버 3팔
`260811_w3_s13frost_c/d/e` 렌더 후 자연안을 frost 팔 기본값으로 확정. 클리어 8·기본 팔(FROST=0)
비트동일 유지. GT-107(데칼 정온) 동승 — 팔 간 비교는 같은 HEAD env 차이만(순수 A/B).
**08-11(2) §4 착지기록**: 구현 = `NEGOBS_GLASS_FROST_COLOR`(기본 0.90,0.92,0.92 — frost 팔
차폐 23 전용; 클리어 8·기본 팔 FROST=0 비트동일). floor(배치 공통): py_compile 7파일 OK ·
SMOKE 4씬+frost 팔 rc0 · geom_invariance R-4/R-6 33/33 PASS · placement_lint stash A/B 신규 0
(7E/63W 동일) · building_kit rc0. rounds `260811_w3_s13frost_c`(rough 0.35)/`_d`(0.22)/`_e`(0.50)
각 15컷 PT_FAST. 실측(entry_approach 크롭): 부스(순수 frosted) 70→**102/103/107**(+46 %) ·
커튼월 크롭 119→126/120/127(클리어 8 혼입 평균 — 유백 회복은 부스 값이 대표). regr vs `_b`
3쌍 **FAIL 0 · WARN 18** — 전량 유리 유백화 + GT-107 데칼 정온 귀속. **판정: c(0.35 · 유백
0.90) 채택 = frost 팔 기본값**(d/e 는 검수 대체안으로 보존). 육안(X3, entry_approach):
젖빛 밝음 회복·배경 뭉개짐 유지·클리어 8 실유리 판독·병리 0. gallery
`_review/260811_w3_s13frost_c`·`_d`·`_e` (구 `_a`/`_b` 는 참고 보존).
**08-14 사용자 검수(원문)**: "c가 이쁘긴 하네 좋아. 다른 씬 확산하면 어디어디 하게 되지?
여기선 괜찮긴 한데, 다른 씬은 상황별로 다를 거라 확인 좀 해봐야할 것 같네" → **c안(rough
0.35 · 유백 0.90) 승인 — frost 팔 기본값 확정**(코드 기본값 = c 이미 일치, 추가 변경 0).
확산은 **씬별 상황 조사 선행 지시**: 유리 재질 참조는 23씬이나 실질 후보 = 낙차 경계 인접
유리(가드/스크린) 보유 씬 — s06 DeckGlass(데크 난간), s08 유리 발러스트레이드(선큰 림),
s12(수변 데크), s01 신설 로비(경계 무관 추정), 건물 창호(무관). 난간 유리는 실관행상 클리어가
정상이라 frosted 확산이 역효과인 씬이 있음 — glass_boundary_check 방법론의 씬별 확장(차폐/
무관/관행 매트릭스)을 별도 행으로.
**Status: HELD (frosted c안 사용자 승인 08-14 — 확산은 씬별 유리 조사 후 판정)**

## 30. GT-74 — scene01 광장 2차: 양측 건물·이중 중간레일 버그·부유 기둥 (선신고)

**Authority**: 08-06 사용자 — "buildings again on both sides … Is that a field or a
square?"(광장 미성립) · 중간 레일 2본 겹침 원인 확인·수정 · "pillar … still hanging in
midair" — 계단 결속 재지시.
**Scope**: `scenes/main/scene01_campus_stairs.py` + `scene_common.py` `build_railing_line`
영역 한정(겹침 버그 원인일 경우). collider/OCCL 변동 본 행 귀속.
**GT 판정**: R-3 + OCCL 선언. Round `260806_w3_fixqueue2`, baseline `260806_w3_fixqueue`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 1차(Opus): 이중 중간레일 근원 수정(merged 경로 RailMid 억제 — 3본→2본) · 살대 접지
  (PICKET_EMBED 12 mm, 18본 부유 소거) · 구근 캡/스타일 마감 · 8동 배치.
- **2차(오케스트레이터, 08-06 사용자 3차 지시)**: "기본이 최고" — merge/그립 전면 철거
  (`handrail=False`), top 1.10 + mid 0.65 2본 + 접지 살대 + ext 0.3 기본형 복원 ·
  **양측 근접 건물 R1/L1 복원**(원 브리프 y 9.5..14 / −15..−10.5, h 14/10, facade 정면 —
  **BS-4 "밀어내고 낮추라" 룰링 사용자 지시로 개정**, GT-59 전례; 자가검증 3행 개정 동반:
  축 회랑 |y|<9.4 개방·측방 밴드 facade 허용·기본형 난간). 육안: 광장 성립·기본 난간 판독.
  regr FAIL2(amphi_view·lower_lookback FRAME/OCCL) = 본 행 귀속.
**Status: OPEN (사용자 검수 대기)**

## 31. GT-75 — scene05 side_arc 돌출 오브젝트·무대 계단 정리 (선신고)

**Authority**: 08-06 사용자 — side_arc 컷의 돌출(popped-out) 오브젝트 수리 · 무대 계단
접속 정리("stand out too much").
**Scope**: `scenes/main/scene05_amphitheater.py`. P-16(무대 재설계)은 계속 범위 외 —
계단 접속·마감 한정.
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue2`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- side_arc 돌출체 = backdrop_shrub 로브가 cut_wall 방위각 대역과 간섭(검산기 사각) → 로브
  방위 재배치 + selfcheck에 방위 간섭 검사 신설. 무대 계단 접속 정리(단 리듬 연속·재질 톤
  통일, P-16 범위 밖 유지). regr 본 씬 FAIL 0.
**Status: OPEN (사용자 검수 대기)**

## 32. GT-76 — scene06 나선 재정밀·에지 마감·양측 통일 (선신고)

**Authority**: 08-06 사용자 — "start over and rebuild the spiral … or pay attention
again. It's sloppy" · 에지 마감 · 반대측 상행 계단 동일 처리 — **단일 육교 제품군 읽힘**.
**Scope**: `scenes/main/scene06_overpass_spiral.py`. 5.005 m 웰·보행면·낙차 불변.
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue2`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 1차(Opus): 나선·북측 계단 정밀 재구축 — 업스탠드+슈+판+캡 1계열, 등각 분절, 노출 킥
  상수화(0.120), 데크 캡 단일부재화, 랜딩 뉴얼 공유(중간 베이 교차 소거).
- **2차(오케스트레이터)**: 랜딩 메시 UV 부재로 타일 평균색 혀가 데크면 침입 →
  `DeckApronTile`(+4 mm, 직선 문지방 에지)로 재질 전환을 의도화. 육안: deck_entry 연속 판독.
  regr FAIL3(deck_entry·h0.3_d2·h0.9_d5 FRAME) = 가드 재구축 귀속.
**Status: OPEN (사용자 검수 대기)**

## 33. GT-77 — scene10 데크 접속 경로 자연화 (선신고)

**Authority**: 08-06 사용자 — "the path the deck connects to flows naturally".
**Scope**: `scenes/main/scene10_park_deck_switchback.py`. 낙차 6.60·P-2 보존 유지.
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue2`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 데크 양단 접속 경로 신설·접지 전이(§0-2 씬 끝까지) — 08-06 감사 "무맥락 매트" 해소.
  P-2 보존 항목 불변. regr FAIL1(h0.9_d10 FRAME) 귀속.
**Status: OPEN (사용자 검수 대기)**

## 34. GT-78 — scene14 측벽 handrail 제거 (GT-70 부분 롤백, 선신고)

**Authority**: 08-06 사용자 — "Why did you add a handrail on the wall? Remove it".
GT-70 의 측벽 상부 handrail 항을 사용자 지시로 롤백(재질 단순화는 유지).
**Scope**: `scenes/main/scene14_grandstair_illusion.py`.
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue2`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- GT-70 측벽 handrail 전면 철거(사용자 지시 — 재질 단순화는 유지). regr FAIL 0.
**Status: OPEN (사용자 검수 대기)**

## 35. GT-79 — scene16 정체성 재구축: 도로 횡단 지하보도 (선신고)

**Authority**: 08-06 사용자 — "I don't know Scene16's identity … it should feel like it
crosses the road, like an underpass". T20(캐노피 그림자 계단) 정체성 위에 **상부 횡단
도로**를 신설해 '도로 밑을 지나는 지하보도'로 재문맥화.
**Scope**: `scenes/main/scene16_canopy_shadow.py`. 계단·하부 통로·그림자 밴드 단서(씬
정체성 T20)·GT 불변 — 상부 도로·연석·접속 보도가 신설 dressing.
**GT 판정**: R-3 + FRAME/OCCL 대변동 선언. Round `260806_w3_fixqueue2`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 상부 **횡단 차도 신설**(연석·차선·§0-2 접속 보도) — "도로 밑을 지나는 지하보도" 정체성 성립
  (육안: beauty_overview). T20 그림자 밴드·계단·통로 기하 불변. **GT 재캐시 선언**: 신설 연석
  낙차 2열(x 7.80/13.80) + 트렌치 대역 x 7.55–14.05 지붕화 → R-1/R-3 재캐시 다음 데이터
  라운드에서. **결정 대기 2건**: 하부 유효고 1.75 m(표준 2.3–2.5 미달 — 통로 심도는 T20 동결
  이라 씬 차원 결정) · 가드레일 x=0 종단 포스트(판정 밴드 내 신규 기하라 별도 행 요망).
  regr FAIL8(approach·프리셋·under_canopy FRAME) 귀속.
**Status: OPEN (사용자 검수 대기)**

## 36. GT-80 — scene11 H형 육교 복원·접속 자연화 (선신고)

**Authority**: 08-06 사용자 — "I asked to fix it into an H-shaped overpass, but it looks
like they just removed the stairs and rushed the fix. Fix it neatly so it connects
naturally." (S11-H 법령: "한국 육교는 H형이야").
**Scope**: `scenes/main/scene11_footbridge_stairs.py` — H-plan 4지 계단 접속 완결(막다른
데크 금지), 접합 마감. 낙차·그레이팅 축 불변.
**GT 판정**: R-3 + FRAME 선언. Round `260806_w3_fixqueue2`, baseline `260731_w3_full`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 1차(Opus): H 완성 — 4지 계단(서측 직선 2련·동측 되돌음 2련), 데크 말단 막다름 해소,
  connuous 가드 폴리라인(코너 공유 포스트·너클 캡·중간 가로대), +1,790프림(§4-14 예산 근거).
- **2차(오케스트레이터, 사용자 "접속을 왜 저렇게밖에" 직접 재작업)**: 1.95 m 펜스 → 1.10 m
  랜딩 가드 급단차를 **말단 베이 2단 계단식 테이퍼**(1.667/1.383)로 전이 — hazard①(랜딩 외연
  1.10 저난간 = 판정 단서)은 불변 유지. 육안: deck_walk 캐스케이드 판독. regr FAIL5 귀속.
**Status: OPEN (사용자 검수 대기)**

## 37. GT-81 — scene17 본선-램프 이격 확장·정리 (선신고)

**Authority**: 08-06 사용자 — "The main road is right next to the slope, so please widen
the distance and trim it neatly."
**Scope**: `scenes/main/scene17_ramp_pair_hangang.py`. 램프 쌍 기하(씬 정체성)·무난간
관행(§4-2) 불변 — 본선 이설·완충 정리.
**GT 판정**: R-3 + FRAME 선언. Round `260806_w3_fixqueue2`, baseline `260731_w3_full`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 본선-램프 이격 확장 + 램프 상·하단 접속(제방로/강변로) + 보도 연속화(§0-2) — "고립 슬래브"
  해소. §4-2 무난간·P-13 무연석 유지. regr FAIL5(프리셋 FRAME) 귀속.
**Status: OPEN (사용자 검수 대기)**

## 38. GT-82 — scene19 잉여 건물 제거·계단 조도·출입 폭 (선신고)

**Authority**: 08-06 사용자 — 옥상 하행 계단만 있으면 되는 씬에 건물 추가 이유 불명 →
제거 · 계단부 과암 개선 · 출입구 협소 확대.
**Scope**: `scenes/main/scene19_fan_winder.py`. 부채꼴 계단 기하(T7)·낙차 불변.
**GT 판정**: R-3 + OCCL/DARK 개선 선언. Round `260806_w3_fixqueue2`, baseline `260731_w3_full`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 잉여 배경 건물 제거(brick_red 소비자 소멸) · 순흑 무텍스처면 재질 바인딩(L19-F1 레버 실행 —
  사용자 지적 = HIGH 미결 승인에 해당) · 부유 조명판 마운트 · 출입 폭 확대. 부채꼴 기하 불변.
  regr FAIL8(전 계열 FRAME — 대변동 선언) 귀속.
**Status: OPEN (사용자 검수 대기)**

## 39. GT-83 — scene03 교량 상향·측면 이동 (선신고)

**Authority**: 08-06 사용자 — levee_walk 의 교량 위치 모호 → "make it even higher and
move it to the side"(육교 문법).
**Scope**: `scenes/main/scene03_riverbank.py`. 제방·수면·낙차 불변 — 교량 이설.
**GT 판정**: R-3 + FRAME 선언. Round `260806_w3_fixqueue2`, baseline `260731_w3_full`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- **3패스 계보**: 1차 상향+측방 이설(u/half 0.85–0.92 이탈) → 2차 시공성(교대 12부재 해체·
  원측 23 m 접속교·거더 분절 9부재 단면) → **3차 근측 접속(08-06 사용자 "어떻게든" 룰링)**:
  좌 90° **곡선 남향 고가 42.40 m**(17현·마이터 겹침 29이음·종곡선 8 m 후 2.0 %·전현 동일
  단면 — "자연 연속 형태 최우선" 이행). 낙차선 x=0 미횡단(+0.33)·산책로 +1.33·자전거도로
  +0.75/+3.01·최소 하부 여유 1.40 m·파라펫 ≤3.9985(<4.00 아이 천장). 양안 교대 → 벽식 교각
  (무결절면 7.45→5.30 m). R_min 7.53 m(연결로 15 미달 — 산책로 불가침의 대가, 선언).
- **셀프체크 FAIL 1 수용**: meander_air 차폐 38.9 %(기준 35) — 사용자 룰링 귀속. 가시 표본
  기준 수선 65.0 m·만곡 18.37 %(기준 40 m/5 %)로 지표 목적은 충족, 임계값 무수정.
  프림 1827→2049. regr FAIL9(전 계열 FRAME) 귀속. 육안: 곡선 리본 연속·파셋 무감지.
**Status: OPEN (사용자 검수 대기)**

## 40. GT-84 — scene07 안내판 제거 (선신고)

**Authority**: 08-06 사용자 — "Remove the guide sign"(사찰 입구 sign_info).
**Scope**: `scenes/main/scene07_temple_stone_path.py` — cue_sign 기본 OFF(어블레이션 경로
보존, v5.2 전례).
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue2`, baseline `260731_w3_full`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- sign_info 기본 OFF(어블레이션 경로 보존, v5.2 전례) + 자가검증 표 갱신. regr FAIL1
  (h0.3_d5 FRAME = 표지 소거) 귀속.
**Status: OPEN (사용자 검수 대기)**

## 41. GT-85 — scene08 부유 핸드레일 정리 (선신고)

**Authority**: 08-06 사용자 — "tidy up the handrails that are hanging in midair"
(08-06 감사: 림 가로대 밑 기둥 부재 + 기둥-가로대 높이 불일치).
**Scope**: `scenes/main/scene08_sunken_plaza.py` — 기둥·가로대 결속 체계 수리. P-3(파라펫
개구 폐합)은 별도 gate 유지.
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue2`, baseline `260731_w3_full`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 원인 = 킷 가로대가 '세그 중점 1점 지반 수평 실린더'인데 호출부가 4.5 m 하강 런을 2점
  폴리라인으로 전달(파손 독트린 무관한 순수 버그) → 림 가드 재시공(기둥-가로대 결속·등간격·
  종단 마감). P-3 개구 폐합은 계속 파크. regr FAIL 0.
**Status: OPEN (사용자 검수 대기)**

## 42. GT-86 — scene09 대안 원경 매스 재표현 (선신고)

**Authority**: 08-06 사용자 — "What's that cloud-like thing across the lake?"
(= far_hills/far_hedge 실루엣 매스 — 밑면 절단 부유·풍선형 판독, 08-06 감사 일치).
GT-63 의 원경 매스 존치 판정을 본 씬에 한해 사용자 지시로 개정.
**Scope**: `scenes/main/scene09_ghat_riverfront.py` — 대안 매스 재표현(접지·실루엣·질감).
**GT 판정**: R-3 전용. Round `260806_w3_fixqueue2`, baseline `260731_w3_full`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- far_hills/far_hedge 접지(밑면 절단 부유 소거)·실루엣 불규칙화·지평 폐쇄 기능 유지
  (B-09-2 인피니티 풀 회귀 방지 — horizon_selfcheck PASS). regr FAIL1(g9_oblique FRAME) 귀속.
**Status: OPEN (사용자 검수 대기)**

## 43. GT-87 — scene20 계단 양측 방호 신설 (선신고)

**Authority**: 08-06 사용자 — "some kind of handrail or something on both sides of the
stairs..? Even a wall.. It looks way too dangerous..?" (08-05 독트린: 난간=낙차 표지).
**Scope**: `scenes/main/scene20_diagonal_oblique.py` — 사선 계단 양측 난간 또는 측벽.
계단 기하·낙차 불변, §4-9(전주 금지) 유지.
**GT 판정**: R-3 + OCCL 선언. Round `260806_w3_fixqueue2`, baseline `260805_w3_hedgeswap`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 실체 = 계단 좌우가 아니라 **사선 메사 연단 전장 무방호**(감사 '경미' 미승계 건) → 연단
  방호 신설(08-05 독트린: 난간=낙차 표지), 계단 기하 불변. regr FAIL1(along_diagonal FRAME)
  귀속.
**Status: OPEN (사용자 검수 대기)**

## 44. GT-88 — sceneC4 수막 투명·표현 개선 (선신고)

**Authority**: 08-06 사용자 — "The water looks strange … water must be clear, so there's
no need to occlude the pad … Put a bit more effort into expressing the water."
**Scope**: `scenes/batch1/sceneC4_wet_stairs.py` — 수막 플레이트 투명화(opacity/글래스 경로,
GT-73 과 동일 기법 계열)·미러 과장 완화·트레드 가시성 회복. 젖음 단서(씬 정체성) 유지.
**GT 판정**: R-2/R-3(재질 중심). Round `260806_w3_fixqueue2`, baseline `260731_w3_full`.
**§4 착지기록** (2026-08-06/07): 구현 = Opus 14기 + s03 전담 3패스 + **오케스트레이터 직접 패스**(s01·s06·s11 — 08-06 사용자 "Fable5 max로 직접" 지시). 통합 floor — py_compile 17파일 OK · SMOKE 게이트 씬 8/8 OK · geom_invariance R-4/R-6 33/33 PASS(패스마다 재실행) · placement_lint 신규 ERROR/WARN 0(HEAD stash A/B) · building_kit OK · HEAD 기하 해시 격리 = 정확히 16씬만 변경. round: `260806_w3_s13fix7`(15컷, regr FAIL11/WARN2 — 유리 투명화·계단박스 재마감 귀속, 육안 합격) · `260806_w3_fixqueue2`(15씬 210컷, regr FAIL44/WARN66/INFO27/PASS78 — 전량 FRAME 계열 선언 변화, GRAZE/DARK 신규 0; 씬별 귀속 각 행). gallery: `_review/260806_w3_s13fix7` · `_review/260806_w3_fixqueue2` (검수 대기).
- 수막 투명화(로컬 opacity 재질 — GT-73 계열)·미러 과장 완화·트레드 가시성 회복(젖음 단서
  유지: 스침각 반사 잔존 — grazing_mirror 육안 확인). **캡처 안정화 레이스 기록**: 3컷이
  '[캡처] FAIL' 로그를 남겼으나 파일 완전성 검증(1920×1080·정상 평균) — scene_common 대기
  40루프 한계, GT-89 하네스 정비 후보. regr FAIL 0(WARN 4 귀속).
**08-10(2) 사용자 판정**: "수막 같은 경우에는 hazard 형태니까, 그냥 그대로 사실성을 유지하면
될 것 같고" — **수막 표현 방향 승인(현상 유지, 추가 수정 불요)**. 유리 일반론(GT-73 추가
검토)과 별개로 수막은 hazard 표현으로서 존치. round 검수 자체는 사용자 보류("일단 내버려둬").
**Status: OPEN (사용자 검수 대기)**


## 45. GT-89 — 구형 씬 템플릿 일괄 현행화: SMOKE 게이트·하네스 정비 (선신고)

**Authority**: 08-06 사용자 — "Please also do a neat batch upgrade on the old skins as well"
+ GUI 부팅 사고(에이전트 SMOKE 시도가 게이트 없는 구형 씬에서 Isaac GUI를 부팅 — scene03
확인·scene09/19 유사, 감시자 임시 운용으로 봉합).
**Scope**(선신고): 전 씬 감사 후 부팅 전 `NEGOBS_SMOKE` 조기 종료 게이트 부재 씬에 일괄 삽입
(기하·재질 무변경 — HEAD 해시 비트동일로 증명) + 캡처 안정화 대기 한계(scene_common 40루프,
GT-88 레이스) 상향. 시각 "스킨" 재작업 의미로 판독될 경우 별도 웨이브(사용자 확인 대기 기록).
**GT 판정**: R-0 인프라(레지스트리·렌더 무영향). round 불요(해시 증명), SMOKE 전수 재실행.
**§4 착지기록** (2026-08-07): 감사 = 정적 스캔(main() 내 boot 호출 이전 NEGOBS_SMOKE 조기 종료
유무). 게이트 정상 10씬(01·02·06·08·11·12·13·14·17·21) · **함정 23씬** — main 11씬
(03=SMOKE 부재·04·05·07·09·10·15·16·18·19·20 = boot(headless) 인자로만 소비) + batch1 12씬
전부(동일 템플릿). 조치 = ①23씬 main() 선두에 균일 게이트 블록 일괄 삽입(프린트 1행+return,
`[GT-89]` 태그) ②scene_common 캡처 안정화 대기 40→**160루프**(`NEGOBS_CAPTURE_WAIT` 환경
가변, 크기 안정 시 조기 break 유지 — GT-88 레이스 귀속 해소). 증명(실행 기록) =
①`py_compile` 24파일 OK ②SMOKE 전수 `NEGOBS_SMOKE=1 timeout 90` 33/33 rc0, 전 씬 0.1~1.0 s
— **부팅 0건** ③기하 해시 비트동일: `geom_invariance_check.py --baseline` 사전/사후 JSON 대조
— 33씬 × 3암(mtl0/mtl1/v1) 해시·프림수 **전부 동일**(HEAD c8c7e2d, R-4/R-6 33/33 PASS 양측)
④`placement_lint --scenes all` rc0 ⑤`building_kit.py` rc0. 의미 변화 기록: 07/09/10 등
'부팅 후 조립 스모크' 경로는 게이트 뒤 도달 불가 — 조립 검증은 geom_invariance(CPU 조립
33/33)가 전담, 심층 팔(NEGOBS_SELFCHECK)은 불변. "old skins"가 비주얼 재작업 의미였는지는
별도 웨이브 질문으로 유지(STATUS).
**08-10(2) 잔여 질문 해소**: "old skins" = 비주얼 재작업 의도 아니었음을 사용자 확인("원래
의도는 아니었긴 한데") — 본 행의 인프라 판독 유효. 비주얼 갱신으로 가능한 레버(재질 층
스왑·웨더링/decal·프로시저럴 잔재의 실자산 재표현 — 전부 기하 불변급, R-2 재질 전용) 설명은
08-10(2) 회신으로 전달. 별도 웨이브는 사용자 발의 시만.
**Status: LANDED (R-0 인프라 — round 불요)**

## 46. GT-90 — scene16 상부 도로 확폭·구조 스케일업 (통로 심도 동결 해제) (선신고)

**Authority**: 08-07 사용자 — "widen s16's road a bit and scale it up more so it can be
worked on neatly. Since I'm trying to keep the existing framework intact, it looks messy."
→ GT-79 가 지킨 기존 틀(통로 심도 동결)이 지저분함의 원인이라는 진단 = **동결 해제 승인**.
원장 행 35 잔여 결정(하부 유효고 1.75 m 표준 미달)을 본 행이 흡수·해소한다.
**Scope**: `scenes/main/scene16_canopy_shadow.py` — 상부 도로 확폭 + 구조 전반 스케일 상향,
하부 통로 유효고 표준(≥2.5 m) 회복. 캐노피 그림자 밴드(T20 정체성)·계단·GT 라벨 불변.
§4-9(전주 금지)·§4-10(차량 금지)·P4/P7/P8 소거 상태 유지. x=0 종단 포스트(판정 밴드 내)
본 행에서 재판정. **주의 기록**: GT-71 헤지 A/B 파일럿(같은 씬, 검수 대기)은 본 개편으로
A/B 대조 오염 — 사용자 지시 우선(GT-59 전례), 파일럿은 개편 후 재스테이지 필요.
**GT 판정**: R-1 + R-3 + FRAME 선언. Round `260807_w3_fixqueue3`, baseline `260806_w3_fixqueue2`.
**08-10 사용자 정정**: 본 행의 착지분(commit 8b919eb, round `260807_w3_fixqueue3`)은 사용자 지시로 **전면 revert**(commit f40e13c — 4씬 기하 해시가 라운드 이전 베이스라인과 비트동일 복원 확인, GT-89 게이트 유지). 구현이 사용자 의도와 불일치. 재지시 대기 — 구판독으로 재착지 금지.
**Status: WITHDRAWN (revert — 재지시 대기)**

## 47. GT-91 — scene03 곡선 접속교 재정형 (GT-83 3차 기각) (선신고)

**Authority**: 08-07 사용자 — "What is s03 talking about? … What is that shape.." —
GT-83 3차의 곡선 남향 고가(42.40 m·17현·R_min 7.53)를 형태 불명으로 기각.
**Scope**: `scenes/main/scene03_riverbank.py` — 근측 접속을 읽히는 문법으로 재정형.
백드롭 거더교 본체(7피어 8.0 m 등간격·저형 거더 = v4-D1 강 정체성) 보존(비판-의도 지도
CROSS-scene03). 낙차선 x=0 미횡단·산책로 불가침(08-06 룰링 승계)·§4-8 대기원근 금지·
P-13 무연석 유지. meander_air 차폐 38.9 % 귀속분은 재정형 결과로 재측정.
**GT 판정**: R-3 + FRAME 선언. Round `260807_w3_fixqueue3`, baseline `260806_w3_fixqueue2`.
**08-10 사용자 정정**: 본 행의 착지분(commit 8b919eb, round `260807_w3_fixqueue3`)은 사용자 지시로 **전면 revert**(commit f40e13c — 4씬 기하 해시가 라운드 이전 베이스라인과 비트동일 복원 확인, GT-89 게이트 유지). **판독 오류의 본체**: Authority 인용문("What is s03 talking about? … What is that shape..")은 곡선 남향 고가의 **기각이 아니라 meander_air 차폐 38.9 % 수치의 의미 설명 요청(질문)**이었다. 롤백 지시가 아니었으므로 본 행의 전제 자체가 무효 — 씬은 GT-83 3차 상태(곡선 고가 + 선언 FAIL 38.9 %)로 복원됨. 퍼센트 설명은 08-10 세션 보고로 전달.
**Status: WITHDRAWN (오판독 — 행 무효)**

## 48. GT-92 — scene06 육교 계단 접속 차폐 해소 (선신고)

**Authority**: 08-07 사용자 — "In s06, the stair connection at the overpass is blocked,
isn't it." + "두 육교 씬에 Fable 서브에이전트" — 본 행은 그 판독을 기록한다:
**두 육교 씬 = scene06(overpass_spiral)·scene11(footbridge)** (라이브러리의 실제 육교 2씬;
scene03 교량은 백드롭 거더교로 육교 아님). 판독이 다르면 사용자 정정으로 재범위.
**Scope**: `scenes/main/scene06_overpass_spiral.py` — 육교↔계단 접속 차폐 해소(통행 연속).
축1 결손 난간·축3 개방 환형 보이드 부활 금지(GT-57 독트린), 5.005 m 웰·보행면·낙차 불변,
GT-68 유리+bronze cap 가드 계열 유지. W4 재판정(로봇높이 개구) 입력 이동 여부 기록.
구현 = **Fable 서브에이전트**(08-07 사용자 지시) + 오케스트레이터 접속부 렌더 검수(08-06 교훈).
**GT 판정**: R-3 선언. Round `260807_w3_fixqueue3`, baseline `260806_w3_fixqueue2`.
**08-10 사용자 정정**: 본 행의 착지분(commit 8b919eb, round `260807_w3_fixqueue3`)은 사용자 지시로 **전면 revert**(commit f40e13c — 4씬 기하 해시가 라운드 이전 베이스라인과 비트동일 복원 확인, GT-89 게이트 유지). 구현이 사용자 의도와 불일치("왜 이리 내 말을 이해를 못했는지"). 재지시 대기 — 구판독으로 재착지 금지.
**Status: WITHDRAWN (revert — 재지시 대기)**

## 49. GT-93 — scene11 철물 과다 감량 (선신고)

**Authority**: 08-07 사용자 — "S11 is way too full of iron bars and all that.."
**Scope**: `scenes/main/scene11_footbridge_stairs.py` — 난간·가드·부재 과밀 감량·정리
(H-plan 정체성·보행 연속성 유지). 불변: 판정 원점 (15.00, 0, 5.50)·데크 런 축 +X·
hazard①(랜딩 외연 1.10 저난간 = 판정 단서)·그레이팅 축. 기하로 가독성 확보, 카메라
프리셋 무수정(R17-1 일반 원칙). GT-80 테이퍼(1.667/1.383)는 감량 후 재평가 대상.
구현 = **Fable 서브에이전트**(08-07 사용자 지시) + 오케스트레이터 접속부 렌더 검수.
**GT 판정**: R-3 + FRAME 선언. Round `260807_w3_fixqueue3`, baseline `260806_w3_fixqueue2`.
**08-10 사용자 정정**: 본 행의 착지분(commit 8b919eb, round `260807_w3_fixqueue3`)은 사용자 지시로 **전면 revert**(commit f40e13c — 4씬 기하 해시가 라운드 이전 베이스라인과 비트동일 복원 확인, GT-89 게이트 유지). 구현이 사용자 의도와 불일치. 재지시 대기 — 구판독으로 재착지 금지.
**Status: WITHDRAWN (revert — 재지시 대기)**

## 50. GT-94 — scene06 상부 접속부 재구성: 반원 랜딩 칼라 정리 (선신고)

**Authority**: 08-10 사용자(3·4차 회신) — "계단이랑 통로랑 연결되는 반원으로 만들어 둔 부분
있잖아. 그 부분 이상한 거 못 느끼겠어? 디자인이야?" · "잘 정리해주면서, 통로도 깔끔하게
자연스럽게 마감해줘. 차라리 ref 사진처럼 통로를 그냥 연장해서 다른 지점에 끝을 만들어서
계단으로 마감해도 좋아." (GT-92 구판독과 무관한 새 판독 — 대상은 300° 나선이 아니라 상부
반원 랜딩.)
**대상 진단**: `landing=dict(r_in 0.48, r_out 3.30, a0=0, a1=180)` — 기둥을 감싸는 북반원
환형 랜딩 + 원호 가드. 동선은 계단 최상단(방위 180°)→데크 서변(117.036°)의 서측 로브만
사용; GT-6 클립이 데크 관통 쐐기(62.964°~117.036°)만 제거해 **동측 로브 [0°, 62.964°]는
어떤 동선도 나르지 않는 죽은 발코니**로 잔존(overview 렌더에서 데크 폭 밖으로 불룩 튀어나와
기둥 뒤로 감기는 혹 — G6 참조에 없는 형태, 파라미터 잔재이지 디자인 아님).
**Scope**(선신고): scene06 상부 접속부 재구성 — 구조 감사 후 두 안 중 택1을 본 행 갱신으로
확정: **1안(국소)** 동측 로브 제거 + 동선 섹터(117.036°~180°, "원 1/4"급)로 축소, 데크 남단
접합 직절 마감. **2안(G6 정합, 사용자 허용)** 데크 남측 연장 + 단부(다른 지점)에서 계단
마감 — 나선 상두를 데크 측면/단부에 접선 접속, 환형 랜딩 폐지. 공통: 랜딩 가드
`_landing_guard_arcs`·소핏·필로티·랜딩 시임(7.08125x tooth)·캐노피 하부 재유도, 300° 나선
본체·5.005 m 웰·h0.3 원통 실루엣 은닉축 유지.
**GT 판정**: 보행면 AABB 변경(랜딩 축소 또는 데크 연장) — R-1(레지스트리 재유도) + R-2 +
R-3. 실루엣 은닉축 유지 확인을 착지기록에 명기.
**§4 착지기록** (2026-08-10, 사용자 5차 "더 깔끔하게 떨어지는 쪽으로 깔끔하게 공사해. 공사
진행해도 좋아" 수령 후): **1안 채택**(동측 로브 삭제 + 1/4 섹터 연결부) — 2안(데크 연장+단부
계단)은 나선 위상(a0=180 기준 파시아/소핏/베이 전 산식)·데크 지지 연쇄를 흔들어 블라스트
반경이 크고, 1안이 참조 G6 의 "데크 옆구리에서 접선으로 감기는 나선" 판독을 그대로 성립시킴.
구현 = `_landing_arcs`/`_landing_guard_arcs` 단일 원천 2함수에서 동측 반환 제거([GT-94] 주석)
+ 로브 수 가변 셀프체크 재작성(ga[1] 고정 인덱스 제거) + 가드 요약 프린트 동적화 + PARAMS·
독스트링·조립부 주석 현행화. 동측 자유단 뉴얼 분기는 휴면 보존(기록용). **floor**:
py_compile OK · SMOKE rc0(연속성표 9행 OK · 랜딩 가드 호 [117.578,180.000]⊂[117.036,180.000]
OK · h0.3 은닉 3거리 OK · 카메라 충돌 0 · 시선 차단 0) · geom_invariance --scenes scene06
R-4/R-6 3암 해시 일치(05f0676a) · placement_lint 신규 ERROR/WARN 0(프림 1506→**1489**,
판정 델타 0) · building_kit rc0. CPU 조립 델타 **−17프림** = 동측 Landing_1 세그 8 +
LandingParapet_1 7부재 + LandingNewel_0 2부재 — 정확히 동측 로브 일습. **round**
`260810_w3_s06collar`(15컷, 63.8 s, HEAD 04cb137+working — 커밋은 본 기록과 동승), stamp OK.
**R-3**: `Docs/reports/regr_260810_w3_s06collar.json` vs `260806_w3_fixqueue2` — **FAIL 0 ·
WARN 0 · INFO 1(ground_graze GRAZE, 정보성) · PASS 14, "회귀 없음"**. 육안(X3):
`pt_noon_overview` — 데크 남단의 반원 칼라 혹 소거, 나선 가드가 단부에서 연속 캡 한 줄로
감겨 내려감 · `pt_noon_deck_entry` — 접합부가 데크 연단→커넥터→나선 캡 연속선으로 읽힘,
슬래브 단부 직절 정상 · `pt_noon_spiral_up` — 동측 소핏 소거로 프레임 상부 개방(FRAME 선언
변화), 원경 파사드 침입 없음(하늘). **은닉축**: SMOKE h0.3 검산 3거리 전부 "전 구간 은닉
OK" — 원통 실루엣 축 유지. **R-1**: 셀프체크 재유도 출력 FAIL 0(s=0 낙차 에지·웰 불변,
개구 확대는 동측 — 판정축 밖, 위 SMOKE 로그 명기). gallery:
`_review/260810_w3_s06collar`(regr JSON 연동). R-2(mini data run)는 W4 재판정 라운드와 동승
예정 — 본 행 R-1/R-3 완료 상태로 검수 대기.
**08-10 사용자 검수(6차)**: "1안이 맞다고 생각했으면, 그래도 뭔가 어색한 느낌이라서, 1/4
섹터도 제거하고, 계단을 통로 끝부분에 바로 연결하면 안 되나? … 지금도 보면 계단으로의
연결성이 막혀있잖아" — 1/4 섹터 잔존도 어색 판정, **직결 재작업 지시** → GT-95(행 51)로
대체. 본 행의 동측 로브 삭제 자체는 유효(GT-95 가 승계).
**Status: CLOSED (검수 — GT-95 로 대체)**

## 51. GT-95 — scene06 나선 상두 직결: 1/4 섹터 폐지·위상 재정렬·데크 남서 베벨 (선신고)

**Authority**: 08-10 사용자(6차) — "1/4 섹터도 제거하고, 계단을 통로 끝부분에 바로 연결하면
안 되나? 너비 안 맞으면 사이즈 좀 조절해서 말이야. 지금도 보면 계단으로의 연결성이
막혀있잖아. 수정 좀 부탁해."
**Scope**(선신고): scene06 — ① **랜딩 일습 완전 폐지**(`landing` dict·`_landing_arcs`·
`_landing_guard_arcs`·`_in_landing`·빌드/가드 루프·관련 셀프체크 항) ② **나선 위상 재정렬**
`spiral.a0` 180 → **117.0357°** [= 180 − acos(r_deck_half 1.5 / r_out 3.3), 상두 디딤 방위선
= 데크 서연 림 교차선] — 감김 방향·sweep 300°·26단·riser 불변, 파시아/소핏/가드 파생 자동
③ **데크 남서 모서리 베벨**: 슬래브 오각형 재구성 [(2,13)(5,13)(5,−13)(3.5,−13)(2,−10.0606)]
— 절취 에지가 상두 디딤 에지와 공유선 = "계단을 통로 끝부분에 바로 연결" ④ 가드 재유도:
서측 데크 레일 에이프런(y −13~−10.128) 삭제·서측 뉴얼(2,−10.128)에서 나선 외측 가드
직결(외측 상두 종단 117.578° = 가드 r 3.24 의 x=2 교차, GT-76 뉴얼 합류 패턴), 나선 내측
가드 상두(117.04°, r 1.56) → 기둥면 폐합 패널 ~1.0 m(동일 가드 계열 — 베벨 내측 r 0.5~1.5
개구 폐합) ⑤ 동측 에이프런·개방 단부(x 3.5~5, s=0 낙차 에지) **유지 — 함정 정체성 불변**
⑥ 지상: 진입 개구가 [120,180](서면)→[57.04,117.04](북면·데크 하부, 유효고=데크 소핏 4.65)
로 회전 — 서측 보도(y=−13, x −30~0.2)는 상두권 계단 하부 통과 진입(az180 하부 여유 ~3.5 m)
으로 전환, 서측 gully (2.35,−11)→(2.35,−9.6)·wear lane 시점 −12.2→−10.0(베벨 절취부 부유
방지) ⑦ 연속성표 재작성(단0 4.808 → 데크 5.000 직결 Δ0.192).
**GT 판정**: 보행면·hazard 개구 형상 변경(랜딩 소멸·베벨·진입 개구 회전) — R-1(레지스트리
재유도) + R-3(round + regr 재스탬프). s=0 낙차 에지(동반, 그리드 축 x 3.5)·5.005 m 웰·
h0.3 원통 실루엣 은닉축 유지를 착지기록에 명기. FRAME 선언: ground_approach·ground_graze·
spiral_up 등 구도 변화 예상.
**§4 착지기록** (2026-08-10): 구현 = ① 랜딩 일습 삭제(`_landing_arcs`/`_in_landing` 폐지,
`_landing_guard_arcs`→`_outer_guard_top_az` 대체, 빌드/가드 루프·DeckApronTile 제거)
② `spiral.a0` 117.0357°(= 180 − acos(1.5/3.3) [computed] — 감김·sweep 300°·26단·riser 불변,
파시아/소핏/가드/뷰 검산 전부 파생 재유도) ③ 데크 오각형 3분할 — 북 BOX(y≥−10.0606) +
남동 BOX(x 3.5~5) + 남서 삼각 프리즘(`_tri_prism` 신설, collider 보유 — 보행면) ④ 가드:
서측 레일 에이프런 폐지(k_lo=1)·서측 E뉴얼 폐지, 외측 나선 가드 상두 117.578°에서
DeckNewel_S0 합류(GT-76 단일 뉴얼 패턴), 내측 상두 뉴얼(민 raked/deck 기초) + **헤드 폐합
패널**(기둥면→내측 뉴얼 ~1.0 m, 동일 슈·판·캡 — 베벨 내측 r 0.5~1.5 개구 폐합) ⑤ GKit
포장 영역 y_apex 북측 한정(직선 재질 경계 = 계단 헤드 콘크리트 문턱 슬래브; 남측 배수구쌍
y −11→−9.6·wear 시점 −12.2→−10.0 — 절취부 부유 방지; 그리드 원점/`well_edge` s=0 데이텀
= y −13 불변) ⑥ 씬 로컬 BOX 래퍼 rotZ 지원(폐합 패널 방사 배치). **floor**: py_compile OK ·
SMOKE rc0 — 직결 Δ0.192 OK·진입 개구 [57.04,117.04] 데크 하부 유효고 4.655·서측 어귀(계단
하부) 3.441·베벨 정합 0.0 mm·캡 3자 6.100 Δ0·h0.3 은닉 3거리 전구간·카메라 충돌 0·시선
차단 0 · geom_invariance R-4/R-6 3암 해시 일치(74b65337) · placement_lint 신규 ERROR/WARN
0(프림 1489→**1473**, 판정 델타 0) · building_kit rc0. **round** `260810_w3_s06direct`(15컷
60.1 s; 포장 경계 수정 후 재렌더 1회 — 1차 렌더의 남단 타일/콘크리트 패치워크 육안 적발 →
⑤ 적용). **R-3**: `Docs/reports/regr_260810_w3_s06direct.json` vs `260810_w3_s06collar` —
FAIL 10 · WARN 2 · INFO 1 · PASS 2, **전량 FRAME/OCCL/PHOTO 선언 변화 귀속**(위상 회전으로
전 컷 구도 이동 — spiral_up 개방 +36.4 휘도(개선 방향)·h0.3_d2 신규 암부 19.1 % = 신설 헤드
폐합 패널 근접 역광면, 육안 귀속·GRAZE/DARK 신규 0). **육안(X3)**: `pt_noon_overview` —
통로가 단부에서 나선으로 접선 유입(G6 판독 성립), 칼라·커넥터 완전 소거 ·
`pt_noon_deck_entry` — 헤더 슬래브 직선 경계·S뉴얼/폐합 패널 접합 정리, 동측 개방 단부(함정)
유지 · `pt_noon_ground_approach` — 데크 하부 개구 아케이드 + 계단 하부 어귀 성립(소핏
스캘럽 가독) · `pt_noon_preset_h0.3_d2` — 연단 은닉 전제 유지(백색 문턱 → 배경 연속 판독).
**R-1**: SMOKE 재유도 FAIL 0 — s=0 낙차 에지(x 3.5~5 동반)·5.005 m 웰·원통 실루엣 축 불변,
진입 개구 회전(서면→북면 데크 하부)은 선언 변화. gallery: `_review/260810_w3_s06direct`.
**08-10 사용자 검수(7차)**: "그런식으로 억지로 잇지 말고, 통로 남쪽 끝이 어짜피 뚫려있잖아.
거길 바로 연결할 수 있도록 계단부를 통째로 동쪽으로 이동해서 연결할 순 없냐는 말이었어.
다시 작업해" — 접선 유입(베벨) 기각, **단부 정면 접속 + 타워 동측 이동** 재지시 → GT-97
(행 53)로 대체.
**Status: CLOSED (검수 기각 — GT-97 로 대체)**

## 53. GT-97 — scene06 나선 타워 동측 이동·통로 단부 정면 접속 (선신고)

**Authority**: 08-10 사용자(7차) — "통로 남쪽 끝이 어짜피 뚫려있잖아. 거길 바로 연결할 수
있도록 계단부를 통째로 동쪽으로 이동해서 연결할 순 없냐는 말이었어. 다시 작업해."
**Scope**(선신고): scene06 — ① **타워 전체 +3.0 m 동측 이동**: `spiral.cx` 3.5 → **6.5**
(= deck.x1 + r_in — 상두 디딤 내단이 데크 남동 모서리 (5,−13) 에 정확히 닿는 위치),
파시아·소핏·기둥·가드·진입 코트 전부 파생 이동 ② **위상 원복** `a0` 117.0357 → **180.0**:
상두 디딤(방위 180~191.5°)의 시작 에지 = 방위-180 방사선 = **y −13 단부 선 위 x 3.2~5.0**
— 통로 남단에서 남향 직진으로 계단 진입(정면 접속), 감김·300°·26단 불변 ③ **GT-95 국소
장치 철거**: 데크 오각형→단일 BOX 복원, `_deck_bevel`/`_tri_prism`/`_outer_guard_top_az`/
헤드 폐합 패널 삭제, GKit region·wear·배수구 원복, 서측 레일 에이프런·E뉴얼 복원(양측 대칭)
④ 접속 가드: 나선 내측 가드 상두(az 180, x 4.94) → 데크 동측 E뉴얼(5,−13) 합류(Δ60 mm ⊂
뉴얼), 외측 가드 상두(az 180, x 3.26) → 단부 선 위 자립 종단 뉴얼 = 계단대/함정 경계 포스트
⑤ **함정 잔부 유지**: 단부 서반 x 2.0~3.26(폭 1.26 m)은 계속 개방 낙차(5.005 m — 웰이
아니라 지면까지, 동일 심도) ⑥ **판정축 이동**: 그리드/GKit 원점 x 3.5 → **2.6**(잔부 중앙,
양측 이격 ≥0.6 m) — 축상 GT 를 '계단 하강'이 아닌 **순수 단부 낙차로 보존**하기 위한 강제
이동(X2 선언; 축이 계단대에 들면 등록 GT 5.005 낙차와 불일치) ⑦ 타워 추종 뷰(spiral_up·
ground_approach·ground_graze 등) eye/tgt +3.0 x 이동(X2 — 동일 피사체 추종), 지상 진입
[120,180](타워 북서 개방 코트 — 원설계 위치로 복귀, 서측 보도 어귀 자연 연장) ⑧ 드레싱
충돌 검사(신규 원 footprint x 3.1~9.9, y −16.4~−9.6) 및 필요시 이동.
**GT 판정**: hazard 개구·보행면·판정축 이동 — R-1(레지스트리 재유도) + R-3 + 전 컷 FRAME
선언(눈 이동 포함). 은닉축(원통 실루엣·h0.3 단부 은닉)은 신규 축 x 2.6 에서 재검증해 기록.
**§4 착지기록** (2026-08-10): 구현 = ①`spiral.cx` 6.5·`a0` 180 복원 ②GT-95 장치 전면 철거
(`_deck_bevel`·`_tri_prism`·`_outer_guard_top_az`·헤드 폐합 3부재·오각형 분할·GKit 문턱 —
데크 단일 BOX·양측 에이프런·E뉴얼·wear/배수구 원복) ③`deck.grid_x` 2.6 신설 —
`_grid_shift`/GKit origin 공유(판정축 = 함정 잔부 중앙, X2 선언) ④타워 추종 뷰 4개 +3.0 x
이동(spiral_up·broken_rail·ground_approach·ground_graze)·deck_entry tgt 상두 직전 재조준
(피사체인 디딤이 자체 차단 게이트에 걸리지 않게) ⑤드레싱 충돌 없음(신규 footprint 내 기존
프롭 무존재 — placement_lint 판정 델타 0). **floor**: py_compile OK · SMOKE rc0 — [정면
접속] 상두 에지 x [3.200,5.000]·y −13.000 ⊂ 단부 OK · 함정 잔부 [2.00,3.26] 폭 1.26 m,
축 2.6 이격 0.60/0.66 OK · 내측 상두 x 4.940 ↔ E뉴얼 Δ60 mm · 연속성표 OK(단0→데크 직결
Δ0.192) · h0.3 은닉 3거리 전구간(신규 축) · 카메라 충돌 0·차단 컷 0 · geom_invariance
R-4/R-6 3암 일치 · placement_lint 신규 0(프림 1473) · building_kit rc0. **round**
`260810_w3_s06endstair`(15컷 63.6 s). **R-3**: regr vs `260810_w3_s06direct` — **FAIL 15/15
전량 FRAME 계열 선언 변화**(타워 +3.0 이동 + 판정축 −0.9 이동 + 추종 눈 이동 = 전 컷 재구도;
GRAZE/DARK 신규 축 기준 재스탬프). **육안(X3)**: `pt_noon_overview` — 교량→단부→계단 타워가
실물 육교 문법으로 읽힘, 데크 가드가 타워까지 직행 · `pt_noon_deck_entry` — **상두 디딤이
단부 정면에 보이는 head-on 접속 성립**(연결성 막힘 해소 — 7차 지적의 표적) ·
`pt_noon_preset_h0.3_d2`(신규 축 2.6) — 단부 뒤 배경 연속 판독, 5.005 m 낙차 은닉 성립 ·
백색 밴드 = GKit well_edge 에지 처리 + 헤드 슬래브 판독(의도 귀속). gallery:
`_review/260810_w3_s06endstair`.
**Status: OPEN (착지 — 사용자 검수 대기)**
**08-11 사용자 검수(8차)**: "좋아. 일단 S06 계단으로 넘어가는 부분에서 너비가 안 맞잖아.
계단 전반적으로 수정할 수 있도록 하고, 원형 기둥이 무쓸모한 느낌인데, 계단 지지대 역할을
하는 것처럼 보이게 축을 좀 달아줘볼래?" — 방향 승인 + 후속 2건 → GT-98(행 54).

## 54. GT-98 — scene06 계단 전폭 광폭화·중앙 기둥 방사 지지 리브 (선신고)

**Authority**: 08-11 사용자(8차) — 위 인용.
**Scope**(선신고): scene06 — ① **계단 광폭화**: `r_out` 3.3 → **4.5**(= cx 6.5 − deck.x0
2.0 [computed]) — 디딤 대역 1.8→**3.0 m**, 상두 에지가 **단부 전폭 x [2.0, 5.0]** 을 받아
통로 폭과 일치("너비가 안 맞잖아" 해소). 함정 잔부 소멸 — s=0 의 GT 는 순수 낙차 →
**나선 계단 하강형 negative obstacle** 로 재분류(R-1 재유도 + W4 재판정 후보 선언),
판정축 `grid_x` 2.6 → 3.5(통로 중심 복원). 파생: 가드 `outer_r` 4.44 · 파시아 4.40/4.50 ·
소핏 r_out 4.54 · **가드 베이 26**(`steps_per_bay` 2→1 — r 4.44 에서 2단 베이는 판 새기타
90 mm 로 80 mm 게이트 초과; 데크 13 베이와 2:1 정수비로 리듬 유지) · 나선 상두 뉴얼 폐지
(양 런 상두가 데크 E뉴얼 (2,−13)/(5,−13) 에 Δ60 mm 로 합류 — 대칭 단일 뉴얼 접합) ·
시선 회랑 반경 갱신 ② **방사 지지 리브**: 중앙 기둥(r 0.5)→소핏 내연(r 1.46) 사이 환형
공백 1.0 m 에 **베이당 1본(13본) 경사 콘크리트 리브**(기둥 럽 0.05·소핏 저면 접합·헬릭스
경사 추종) — 기둥이 나선을 받치는 마스트로 읽히게("계단 지지대 역할").
**GT 판정**: 보행면 확장(디딤 대역 +1.2 m)·hazard 재분류 — R-1 + R-3 + 전 컷 FRAME 선언.
h0.3 은닉(계단 하강 은폐)·실루엣 축을 신규 축 3.5 에서 재검증 기록. Round
`260811_w3_s06wide`, baseline `260810_w3_s06endstair`.
**§4 착지기록** (2026-08-11): 구현 = ①`r_out` 4.5·가드 `outer_r` 4.44·파시아 4.40/4.50·
소핏 r_out 4.54·`steps_per_bay` 1(26 베이 = 데크 13×2 정수비 — 검산 갱신)·상두 뉴얼 폐지
(외측→서측 E뉴얼·내측→동측 E뉴얼 각 Δ60 mm 대칭 합류)·`grid_x` 3.5 복원·시선 회랑 반경
r_out+0.9 파라미터화 ②지지 리브 13본 중 **10본 생성**(하부 3본은 소핏이 지면에 잠겨 생략 —
프린트 기록), 레벨 방사재 0.16×0.24, 기둥 럽 0.05·소핏 저면 접합 ③볼라드 동측 3본
9/12/15→10.6/12.8/15.0(확폭 림 r 4.47 침입 해소, 2.2 m 등피치). **floor**: py_compile OK ·
SMOKE rc0 — 정면 접속 x [2.000,5.000] 전폭 OK·대칭 뉴얼 합류 OK·베이 정수비 OK·판 새기타
22.5/7.9 mm(≤80)·기둥 여유 +0.150 OK·회랑 침입 0·h0.3 은닉 3거리·충돌 0·차단 0 ·
geom_invariance R-4/R-6 3암 일치 · placement_lint 신규 0(프림 1473→**1531**) · building_kit
rc0. **round** `260811_w3_s06wide`(15컷 63.9 s). **R-3**: regr vs `260810_w3_s06endstair` —
FAIL 11·WARN 2·INFO 1·PASS 1, **전량 FRAME 계열 선언 변화 귀속**(림 +1.2 m 확폭으로 전 컷
재구도, GRAZE/DARK 신규 0). **육안(X3)**: `pt_noon_deck_entry` — **전폭 부채꼴 디딤이 통로
너비를 그대로 받음**(8차 지적 '너비가 안 맞잖아' 해소), 연속 리본 가드 · 
`pt_noon_ground_approach` — **리브 10본이 기둥→소핏을 규칙적으로 결속, 마스트가 나선을
받치는 구조로 판독**(8차 지적 '무쓸모 기둥' 해소) · `pt_noon_preset_h0.3_d2`(축 3.5) —
계단 하강형 은닉 성립(연단 뒤 디딤 소실). gallery: `_review/260811_w3_s06wide`.
**Status: OPEN (착지 — 사용자 검수 대기)**
**08-11 사용자 검수(9차)**: "확장은 잘 했는데, 연결부 오른쪽 난간에 빈공간이 생겼네. 마감
깔끔하게 해줄 수 있도록 하고, 지지 리브가 아래쪽으로 좀 날카롭게 튀어나온 것처럼 보이는데
깔끔하게 마감해줘" — 확장 승인 + 마감 2건 → GT-99(행 55).

## 55. GT-99 — scene06 마감 2건: 가드 베이 상단 개구 폐합·리브 코벨 재마감 (선신고)

**Authority**: 08-11 사용자(9차) — 위 인용.
**진단**: ① 개구 = 평판 판이 확폭 원호를 현으로 질러(베이 중앙 새기타 22.5 mm, r 4.44)
판 상단(랩 25 mm)과 나선형 캡 사이로 내측 상방 시선이 새는 렌즈형 띠 — 매 베이 상단
(`deck_entry` 육안) ② 리브 = 0.24 깊이 단일 블레이드의 외측 하단 모서리가 소핏 림 밖에서
날카롭게 노출.
**Scope**(선신고): ① `rail_bay.cap_grip` 0.025→**0.065**(판-캡 랩 65 mm — 부각 ≥19° 전
판정 눈에서 폐합 [computed]; 캡 프림 높이 85→125 mm) ② 리브 → **계단식 코벨**: 상부
슬래브 0.10(전장, 외단은 소핏 림 20 mm 안쪽으로 턱) + 기둥측 55 % 헌치 0.14 — 날 선 외단
소멸. R-3 전용(난간·리브 — 보행면·낙차 불변). Round `260811_w3_s06trim`, baseline
`260811_w3_s06wide`.
**§4 착지기록** (2026-08-11): 구현 = 선신고 그대로(캡 물림 65 mm — SMOKE "유리 물림 캡
65 mm" 확인 · 코벨 = SpiralRib+SpiralRibHaunch 쌍, 외단 소핏 림 20 mm 안쪽). floor:
py_compile OK · SMOKE rc0 · geom_invariance R-4/R-6 3암 일치 · placement_lint 신규 0 ·
building_kit rc0. round `260811_w3_s06trim`(15컷). **R-3**: regr vs `260811_w3_s06wide` —
**FAIL 0 · WARN 0 · INFO 2 · PASS 13, "회귀 없음"**. 육안(X3): `pt_noon_deck_entry` 확대 —
베이 상단 개구 띠 폐합(배경 투과 소멸, 판 상단이 캡 그늘 안으로) · `pt_noon_ground_approach`
확대 — 코벨 프로파일 정착(날 선 블레이드 소멸). gallery: `_review/260811_w3_s06trim`.
**Status: OPEN (착지 — 사용자 검수 대기)**

## 56. GT-100 — scene06 서측 접합 완화: 외측 가드 수평 시작 베이 (선신고)

**Authority**: 08-11 사용자(10차) — "확장을 하다 보니까 서쪽 연결부 난간을 깔끔하게
못 이은 것 같아 … 난간이 끊기지 않고 다 잘 연결되어 있는지 확인해볼래?"
**진단**: 서측 접합에서 수평 데크 캡과 나선 외측 캡이 자유 코너 한 점에서 평면 곡률과
종단 경사를 동시에 꺾어 미해결 노치로 판독(동측은 내측 가드가 데크 레일 뒤로 감겨 정상
판독 — 사용자 확인). 기하 연속성 자체는 성립(캡 6.100 Δ0)이나 조형 미해결.
**Scope**(선신고): 외측 가드 상두에 **수평 시작 베이 1개**(방위 180~191.54° = 디딤0
스팬, 레벨 섹션·캡 6.100) 삽입, 이후 첫 포스트에서 0.192 너클 후 레이크 — 북측 계단
가드의 참(landing) 디테일과 동일 문법. 내측 가드는 현행 유지(동측 정상 판독). R-3 전용.
Round `260811_w3_s06weld`, baseline `260811_w3_s06trim`.
**§4 착지기록** (2026-08-11): 구현 = RailOuterHead(레벨 베이, bays[:2], 캡 6.100) +
RailPostOuterHead(너클 포스트, skip 0) + 외측 레이크 런 bays[1:] 재시작. floor: py_compile
OK · SMOKE rc0 · geom_invariance 3암 일치 · placement_lint 신규 0(1531→1543) · building_kit
rc0. round `260811_w3_s06weld`(15컷). R-3: regr vs s06trim — FAIL 1·WARN 1·INFO 2·PASS 11,
접합부 국소 FRAME 귀속. 육안: overview 크롭 — 서측 캡이 수평으로 이어진 뒤 포스트에서
0.192 너클 후 레이크(북측 계단 참 디테일과 동일 문법), 노치 판독 소멸. 전 접합 연속성:
SMOKE 캡 라인 3자 6.100 Δ0·정면 접속 OK·대칭 뉴얼 합류 OK. gallery:
`_review/260811_w3_s06weld`.
**Status: OPEN (착지 — 사용자 검수 대기)**

## 57. GT-101 — scene06 이음 곡선화·리브 전수 상향·타워 남측 3 m 이동 (선신고)

**Authority**: 08-11 사용자(11차) — "좀 더 부드럽게 이어봐. 결국엔 삐죽삐죽 됐잖아.
난간을 손으로 잡고 간다고 생각했을 때 이어서 잡을 수 있겠어? … 리브는 … 조금씩만 더
올리면 쉽게 풀리는 문제 아니야? 왜 굳이 잘랐어? … 구조물 받침도 겹치는 부분 해결해줘.
울타리랑도 겹치고 계단이랑도 겹쳐버리네..? 통로를 좀 더 남쪽으로 연장해서 차도랑 틈을
좀 벌려야겠다."
**Scope**(선신고): ① GT-100 레벨 베이+너클 **철회** → 외측 가드 z-함수를 **C1 이즈**
(a0 에서 접선 0, 2베이에 걸쳐 헬릭스 경사로 블렌드 — 캡이 한 손흐름) ② 리브: 계단식
코벨 철회 → 단일 부재 0.14 깊이, **13본 전수**(저부는 바닥 위 클램프 — 생략 금지)
③ **타워 −3.0 m 남측 이동**(cy −13→−16) + 데크 남단 연장(y0 −13→−16): 데크 받침
V-기둥(3.5,−9)의 동측 레그 헤드(r 4.49)가 확폭 림 4.5/가드 4.44/최하부 디딤과 겹치던
것 해소(신규 이격 3.1 m), 차도(y −8)-타워 림 이격 3.5 m. 그리드 원점/s=0 데이텀 y −16
으로 이동(파생 자동), 타워 추종 뷰 4개 −3 y. R-1 + R-3 + 전 컷 FRAME 선언. Round
`260811_w3_s06ease`, baseline `260811_w3_s06weld`.
**08-11 사용자 추가(12차, 이즈 1차 렌더 검수)**: "옆에서 봤을 때 바닥면 라인도 연결부가
삐죽 튀어나온 느낌 … 난간 유리판도 빈틈 안 보이게" — Scope 증보: ④ 측면 실루엣 — 데크
남/서 노출 연단에 **스커트 밴드**(슬래브 소핏 4.65 → 파시아 저선 ≈4.19, 두께 0.25)로
하부선을 링에 연속 ⑤ 유리 개구 — 이즈 곡선(캡)/판 현(직선) 불일치가 베이 중앙 최대
~50 mm 개구를 열던 것을 **이즈를 베이 경계 폴리라인화**(2차 곡선을 포스트에서 샘플)로
캡·판이 동일 선을 타게 — 구조적 0-갭.
**§4 착지기록** (2026-08-11): 구현 = 선신고+증보 그대로(①C1→폴리라인 이즈 ②리브 13본
전수·저부 클램프 — SMOKE "리브 13/13" ③cy/y0 −16·뷰 4개 −3 y·기둥 여유 +2.77
④스커트 S/W ⑤0-갭). floor: py_compile OK·SMOKE rc0·3암 일치·lint 신규 0·building_kit
rc0. rounds: `260811_w3_s06ease`(이즈 1차 — 12차 검수로 증보) → **`260811_w3_s06glass`**
(최종 15컷). R-3: regr(glass vs ease) **FAIL 0**·WARN 3·PASS 10 — 접합 국소 귀속; (ease
vs weld) FAIL 5 전량 타워 −3 이동 FRAME 귀속. 육안(X3): overview 확대 — 이즈 구간 판
상단 개구 소멸(캡-판 동일 폴리라인)·캡 손흐름 연속·스커트로 슬래브 하부선이 파시아
저선에 연속. gallery: `_review/260811_w3_s06glass`.
**08-11 사용자(13~14차)**: 13차 "모서리가 튀어나온 부분이 없어야지 … 코벨 철회가 아니라
코벨 자체를 조금씩 올리라는 말이었어. 이해 다시 해서 작업 다시해" → 3판(블렌드 캡·
스무스스텝·outer_r 4.46·코벨 복원, commit 9aa79f2, round `260811_w3_s06sweep`) 시공 →
14차 "왜 이해를 점점 못할까..? 롤백하고 메모리 정리해" · "방금것만 철회해" — **3판 전면
철회**(revert, 2판 상태 비트 복원 — SMOKE rc0·3암 일치 확인). s06sweep 라운드/갤러리는
참고용 보존(비검수). **s06 이음·코벨은 재지시 전까지 동결**. 오독 방지 프로토콜은 메모리
shape-feedback-protocol 등재(크롭→시각 의도 한 문장 재진술→확인 후 시공) · **선택지
UI(AskUserQuestion) 사용 금지** 룰링 기록.
**Status: OPEN (2판 상태 — 사용자 검수 대기 · 이음/코벨 동결)**

**08-14 사용자 검수 회신(원문)**: "리프 좀 더 올리고 더 일체성 있게 만들어야 할 것 같아." →
14차 철회로 동결됐던 이음/코벨에 대한 **재지시 도착으로 판정 — 동결 해제**: ① 리브(코벨)
상향("좀 더 올리고" — 13차 '코벨 자체를 조금씩 올리라는 말' 계보) ② 전체 일체성. 시공 전
[[shape-feedback-protocol]] 의무(이 주제가 4회 오독 이력의 진원지): 크롭 → '리브를 어디서
얼마나 올리는지' 한 문장 재진술 → 확인 후 기하 변경(신규 세션, 새 선신고).

## 58. GT-102 — scene11 받침 대형 기둥 통일 (선신고)

**Authority**: 08-11 사용자(11차) — "구조물 받침도 일관성 있게 정리해줘. 구조물 전체
구조 확인해서, 큰 기둥들만 받치도록 해줘. 네 기둥으로 받치고.. 큰 기둥으로 받치고..
왔다갔다 하는게 보기 안좋아."
**감사**: 데크 = r 0.40 대형 피어 2본(±11.8) · 랜딩(헤드/미드) = `_pad` 가 **모서리
슬림 기둥 4본**(TW.col_r) — 두 어휘 혼재.
**Scope**(선신고): `_pad` 기둥을 **패드당 대형 단일 기둥 1본**(r = deck_posts.r 0.40,
패드 중심)으로 통일 — 전 랜딩 동일 어휘, cols 리스트 의미 유지. R-3 전용(받침 —
보행면·낙차 불변). Round `260811_w3_s11piers`, baseline `260811_w3_s11flip`.
**§4 착지기록** (2026-08-11): 구현 = `_pad` 모서리 4본(TW.col_r) → 패드 중심 대형 1본
(r=deck_posts.r 0.40). floor: py_compile OK·SMOKE rc0·3암 일치·lint 신규 0(4610→4430,
−180 = 슬림 기둥 일습)·building_kit rc0. round `260811_w3_s11piers`(15컷). R-3: regr vs
s11flip **FAIL 0·WARN 0·PASS 15**. 육안(X3): overview 확대 — 데크 피어·헤드·미드 랜딩이
r0.40 원기둥 단일 어휘, 4본 클러스터 소멸. gallery: `_review/260811_w3_s11piers`.
**Status: OPEN (착지 — 사용자 검수 대기)**

## 59. GT-103 — scene16 대공사: 왕복 6차로 확폭·중앙분리대·지하통로 전면 재유도 (선신고)

**Authority**: 08-10 2차 사용자 — s16 "**6차로 이상, 더 커도 됨**" + 지하통로 전면 대공사
확정(STATUS 08-10 2판 기록) · 08-11 사용자 — "s16 대공사 진행해도 되고". GT-90 WITHDRAWN
후 재지시 이행 — 구판독 재착지 금지 준수(본 행 판독 = 명시 6차로+ 수치·전면 재유도).
원장 행 35(GT-79) 잔여 결정 2건(하부 유효고 1.75 표준 미달 · 가드레일 x=0 종단 포스트)
본 행이 흡수.
**Scope**: `scenes/main/scene16_canopy_shadow.py` 전반(PARAMS 재유도 + build_road
중분대·차로 마킹 + 동측 일괄 재배치). **T20 정체성 불변** — 캐노피 그림자 밴드·서측 계단
x0=0·SUN_AZ_OFFSET 146.5·판정 눈. 서측 판정 대역(x ≤ 7.8) 기하 불변 — 확장 전량 동측(+X).
§4-9 전주 금지·§4-10 차량 금지·P4/P7/P8 소거 유지. 헤지 = 동측 밴드 위치 이동만(밀도
확산 보류 유지, GT-71 파라미터 불변).
**수치**: 차도 car0 7.80(불변)…car1 30.00 = **22.20 m** — 편도 3차로 × 3.50 ×2 +
**중앙분리대 1.20**(x 18.30…19.50, 연석 2선 + 포장 상면 +0.015, y 림 전장 = 무단횡단 물리
차단 → '왜 지하보도인가' 강화). 차로 구분선 백색 점선 4선(3 m 도색/5 m 공백) · 중분대측
황색 실선 2선 · 측선 백색 2선. 통로 z_top −2.10 → **−3.00**(**유효고 2.65 ≥ 2.5 표준
회복** — row-35 해소, 소핏 −0.350 불변), base_z −3.50. 양측 계단 14×0.15 → **20×0.15**
(낙차 2.10 → 3.00 ≤ 참 불요 3.0, run 4.48 → 6.40). 동측 계단 x0 30.20(= kb1)…머리 36.60.
트렌치·wall·둘레난간 x1 36.60. walk x_e 40.0 · ground gx1 37.2 · 건물 C 42…48 · 가로벽
동측 4동 x 32.2…42.2 재배치(회랑 개구 5.60…32.20 = fw0…fw1) · 볼라드 x 38.6 · 플랜터
B/C cx 33.8 · 벤치 (33.8, 6.9) · 가로등 (31.2, −6.5) · 동측 헤지 (32.5…36.5, −7.3…−6.5).
캐노피 x1 4.6 → 6.6(연장된 하강 전 구간 계속 커버 — T20 그림자 소유 유지). **perim rail
서런 x0=0 종단 포스트 신설**(row-35 재판정 — 스텁 종단 해소; 판정 밴드 내 신규 기하 본 행
선언).
**GT 판정**: 보행면·낙차 에지 대변동 — R-1(self-check 재유도 출력) + R-2(다음 데이터
라운드에서 mini run 재실행 선언) + R-3(baseline `260806_w3_fixqueue2` →
`260811_w3_s16road6` 재스탬프) + FRAME/OCCL 대변동 선언. `EXPECTED_FP` scene16 프리셋 행
재검토 필요(트렌치 연장·심화). Round `260811_w3_s16road6`.
**§4 착지기록** (2026-08-11, 오케스트레이터 직접): 구현 = PARAMS 재유도(xroad 6차로+중분대
·passage −3.00·계단 20단·wall/rail/walk/ground/건물 C/가로벽/가구 동측 전이) + build_road
중분대 2연석+필·점선 4선 루프·황색 중분대변 2선 + 둘레난간 서런 종단 포스트. floor:
py_compile OK · SMOKE OK(GT-89 게이트) · geom_invariance R-4/R-6 33/33 PASS(scene16 722프림
3자 일치) · placement_lint stash A/B 신규 ERROR/WARN 0 · building_kit OK. 렌더 self-check
(로그 `260811_w3_s16road6.log`): 차도 22.20 m = 편도 3×3.50 ×2 + 중분대 1.20(림 전장) ·
구분 점선 4선×18절 · 연석 4선 136블록 top +0.020 · 복개 박스 22.70 m · **유효고 2.650 ≥ 2.5
충족(row-35 해소)** · 둘레난간 끝기둥 8(x 0.00 종단 포스트 신설) · 캐노피 −1.00…+6.60 vs
하강 0…6.40(전 구간+여유 0.20 커버) · 계단머리 점자 밴드 x −0.90…−0.30 불변(GT-E1′ 0.300 ≥
0.240 충족·BOTH BANDS 유지). round `260811_w3_s16road6`(13컷 PT_FAST), regr vs
`260806_w3_fixqueue2`(`regr_260811_w3_s16road6.json`) FAIL11/WARN1 — 전량 FRAME(+GRAZE 2·
OCCL 3) 선언 변화 귀속, 신규 DARK 0. 육안(beauty_overview·approach·h0.3_d5·under_canopy):
6차로+중분대 '큰길' 판독 · 동측 계단 도로 건너 36.6 상승 판독 · h0.3 낙차 은닉 전제 유지 ·
그림자 밴드·노징 저대비 시그니처 유지 · 파이어플라이/순흑 병리 0. gallery
`_review/260811_w3_s16road6` (검수 대기). R-2(mini data run)는 다음 데이터 라운드에서.
**Status: OPEN (사용자 검수 대기)**

## 52. GT-96 — scene11 울타리 전면 정돈: G11 단일 리본 팬스 통일 (선신고)

**Authority**: 08-10 사용자(4·6차) — "s11은 육교 울타리가 깔끔하게 정돈되지 않았다는 말이야.
전체적인 구조 다시 확인해서 수정할 수 있도록 해줘. 대공사로 진행해도 좋고" · "전반적으로
일관성 유지하면서 깔끔하게 만들어봐" · "s11도 같이 작업하면 돼".
**감사 진단**(08-10, 코드+렌더+G11 재판독): 현행 가드 어휘 4종 혼재가 '정돈 안 됨'의 실체 —
① 데크 = **1.95 m** 수직살대 팬스(`rail_z` 1.95, 구 방음레일 높이 잔재) ② 계단·랜딩 =
**1.10 m** 파이프+살대(`build_railing_line`/`build_guard_run`) ③ 양단 베이 **2단 스텝
테이퍼**(1.667/1.383 — 1.95→1.10 낙차 무마용) ④ 타워 헤드 **HeadMesh 사다리꼴 빌보드**
(가드 위 +0.90 돌출, overview 에서 고립 격자판 판독). 참조 G11 실물은 **단일 높이(~1.2 m)
프레임+세밀 격자 인필 팬스가 데크→계단 레이크→랜딩을 한 줄로 감는 연속 리본** — 높이 단차도
빌보드도 없다.
**Scope**(선신고): scene11 — ① 데크 팬스 `rail_z` 1.95 → **~1.25 단일 높이**, 베이 프레임 +
세밀 격자 인필(기존 `build_mesh_panel` 바 격자 기법을 팬스 인필로 전용) ② 계단 레이크·랜딩
가드를 같은 프레임+격자 어휘로 통일(파이프 병용 폐지), 접속점 공유 포스트·캡 라인 연속
③ 2단 스텝 테이퍼 폐지(단일 높이로 소멸) ④ HeadMesh 빌보드 → 팬스 라인 내 삼각 인필로
재정착(레이크-수평 사이 삼각형, G11 위치) ⑤ 지상부 이중 팬스/게이트 정리 ⑥ **판정축 예외**:
동측 헤드 랜딩 자유연의 1.10 m 저난간(hazard ① 판정 단서, GT-93 행 기록)은 **현 높이·현
위치 유지** — 통일 대상에서 명시 제외. 도장 beige-tan(G11)·그레이팅 정체성 불변.
**08-10 사용자(7차) 추가 지시**: "S11은 ㅇㅋ 작업해서 보여줘봐. 그리고 계단 다이아 형태로
할 거 같으면 한쪽은 없애면 좋겠어. 굳이 저렇겐 안 만들거든" — 승인 + **동측 타워의 이중
스위치백(다이아 판독) 중 한쪽 레그 제거** 추가. Scope 증보: ⑦ 동측 타워 레그 2→1(판정
컷이 참조하는 레그 존치, 제거 레그의 플라이트·가드·메시·지상 에이프런 절반 동반 철거,
비운 헤드 랜딩 면은 리본 팬스로 폐합 — GT-80 의 "4피트 H" 전제는 사용자 지시로 개정:
동측 3피트).
**GT 판정**(승급): 레그 제거 = 보행면 철거 — R-1(레지스트리 재유도) + R-3 + FRAME 선언
(팬스 −0.7 m 전 컷 상부 개방 + 동측 매스 절반 소거). hazard ①(동측 헤드 랜딩 1.10 저난간)
존치 확인을 착지기록에 명기. Round `260811_w3_s11ribbon`, baseline `260806_w3_fixqueue2`.
**§4 착지기록** (2026-08-11): 구현 = ① `deck.rail_z` 1.95→**1.25**·`rail_bay.post_h`
1.98→1.29 — 데크 리본 단일 높이, 상부 레일 전장 복원 ② 양단 2단 스텝 테이퍼 일습 삭제
(1.25→1.10 포크 단차 0.15 는 공유 단부 포스트에서 너클) ③ HeadMesh 빌보드(+0.90) →
팬스 라인 정착(상단 = rail_z 1.25, run 3.0→1.6 — G11 급 소형 삼각 인필) ④ **동측 미러
레그(east_N) 삭제** — `_tower_legs` 단일 원천 수정(동측 1레그 반환), C1c 모델에
HeadGuardBack/Head_back 신설 + 빌드 측 HeadGuardOuter 를 L-런으로 확장(비운 두부면 폐합,
공유 코너 포스트), H 4각 검사 → 개정 3각 검사(발 착지 3/3), 독스트링 표 갱신 ⑤ hazard
①(동측 헤드 랜딩 자유연 1.10 저난간) **존치 확인** — 판정 레그(east_S, midlanding 컷 피사)
불변. **floor**: py_compile OK · SMOKE rc0(개정 3각 OK·보행 연속성 3루트 OK) ·
geom_invariance R-4/R-6 3암 일치 · placement_lint **HEAD-stash A/B 판정 델타 0**(프림
5598→**4610**, −988 = east_N 일습) · building_kit rc0. **round** `260811_w3_s11ribbon`
(15컷 58.4 s). **R-3**: regr vs `260806_w3_fixqueue2` — FAIL 2 · WARN 7 · PASS 6, **전량
FRAME 계열 선언 변화 귀속**(팬스 −0.70 m 전 컷 상부 개방 + 동측 매스 소거; GRAZE/DARK 신규
0). **육안(X3)**: `pt_noon_overview` — 단일 높이 리본이 데크→계단→랜딩을 한 줄로 감고,
동측이 실물 육교 문법의 단일 스위치백으로 읽힘(다이아 소거), 테이퍼·빌보드 소멸. gallery:
`_review/260811_w3_s11ribbon`.
**Status: OPEN (착지 — 사용자 검수 대기)**
**08-11 사용자 정정(10차)**: "다이아몬드 깨라고 했던건 버스정류장이 있어서 반대껄
살렸으면 좋았을 것 같아" — 존치 레그 스왑 재지시: east_S(남측, 버스정류장 발치 간섭)
제거 → **east_N(북측) 존치**. 판정 컷(midlanding 등 남측 조준)은 미러 재조준(X2).
**[2판 착지]** (08-11, round `260811_w3_s11flip`): `_tower_legs` east → legs[1:]
(east_N 존치) · `_plan_lines` with_head 를 타워별 첫 레그로 정정(구 i%2 는 3레그에서
서측 헤드를 미러 레그에 오귀속 — 대칭이라 세그 동일했으나 구조 결함, 동반 수리) ·
midlanding/stair_head 뷰 미러 재조준(`_local_to_world` 가 존치 레그 프레임을 자동
추종 — 고정 좌표 컷 under_grating/sidewalk_approach 만 +Y 미러) · 독스트링 표 갱신.
2판 floor: SMOKE rc0(개정 3각·발 착지 3/3) · 3암 일치 · lint 신규 0(4610프림) · round
`260811_w3_s11flip`(15컷) regr vs s11ribbon FAIL 3·WARN 7·PASS 5 — 전량 레그 미러 FRAME
귀속. 육안: overview — 동측이 북향 단일 스위치백, 버스정류장 발치 개방 확인. gallery:
`_review/260811_w3_s11flip`.

## 60. GT-104 — scene06 데크 난간 재모듈화: 판폭 원모듈 회복 (선신고)

**Authority**: 08-11 사용자(갤러리 검수 회신) — "s06 통로 확장한 건 좋은데, 난간 유리도 길게
늘리면 어떡해? 난간이 일관성이 떨어져 버렸잖아. 이 점도 확인하고 실측해서 고쳐줄 수 있도록 해."
**실측(2차 정정 — 스모크 HEAD 실측으로 확정, 문서 잔존값 −10.128 기각)**: 뉴얼
yj = **−11.821**(= cy −16 + √(4.44² − 1.5²) — GT-98 outer_r 4.44 기준). `_deck_rail_y()` 는
필드 yj…+13.0(24.821 m)만 `n_bay` 13 분할(판폭 **1.909 m**, GT-101 이전 1.679 에서 +13.7 %),
남측 에이프런 y0…yj 는 **단일 베이 4.179 m 통판**(원설계부터 필드와 이질 — GT-101 이 y0·cy 를
같이 −3 해 길이는 불변, 필드 판만 늘어남). '길게 늘어난 유리·일관성 저하' = 필드 +13.7 % 와
상존하는 4.18 m 통판의 합.
**Scope**(선신고 2차 정정판): ① 에이프런 y0…yj **2베이 분할**(판폭 4.179/2 = **2.089 m**)
② 필드 `n_bay` 13 → **12**(판폭 24.821/12 = **2.068 m**) — 전 런 Δ21 mm(1.0 %)로 단일
모듈 ≈2.08 m(원설계 모듈 2.0 근방), 뉴얼 yj 베이 경계 유지(GT-76 핸드오버 불변) ③
`build_deck_rail` 뉴얼 인덱스 일반화(0·apron_bays·nb) ④ GT-98 '2:1 정수비' 리듬 검산은
**판폭 균일성 검산(런 내 최대−최소 ≤ 0.10)** 으로 대체(자가검증 갱신 동반 — GT-74 전례).
파생: 포스트 양측 각 +1본·DeckGlass +1판(에이프런 1→2). 이음 폴리라인·코벨 동결 유지(비접촉),
보행면·낙차·hazard·판정축 불변.
**GT 판정**: R-3 전용(난간 프림 한정). Round `260811_w3_s06bay14`, baseline `260811_w3_s06glass`.
데칼 정온(GT-107) 라운드 동승 — regr 귀속 분리 선언.
**§4 착지기록** (2026-08-11): 구현 = `apron_bays` 2 신설·`n_bay` 13→12·`_deck_rail_y` 에이프런
분할·`build_deck_rail` 뉴얼 인덱스 일반화(0/na/nb)·검산 2건 대체([가드 통일] 판폭 균일성 ·
[데크 레일 분절 · GT-104]). SMOKE 실측 = 판폭 **2.068~2.089 m (Δ21 mm ≤ 100) OK** · 뉴얼
−11.821 베이 경계 [2] OK. floor: 배치 공통(위 GT-73 기록). round `260811_w3_s06bay14`(15컷).
R-3: regr vs `260811_w3_s06glass` — **FAIL 0 · WARN 3(UNCHANGED — 데크 레일 비가시 컷) ·
INFO 1 · PASS 11**. 육안(X3): `pt_noon_overview` — 전 런 단일 모듈 판독, 남단 통판(4.18 m)
소멸, 브론즈 캡 연속. 이음/코벨 동결 무접촉 유지. gallery `_review/260811_w3_s06bay14`.
**Status: OPEN (착지 — 사용자 검수 대기)**

## 61. GT-105 — scene11 하강 가드 중간 가로대 소거: 리본 단일 언어 (선신고)

**Authority**: 08-11 사용자(갤러리 검수 회신) — "S11도 내려가는 난간 언어 다시 확인하고 일관성
유지해줘. 통로 중간에 바가 또 생기는게 부자연스러워."
**진단**: GT-96 리본 팬스(프레임+살대, 단일 상부 레일 1.25)와 달리 하강 경로 가드가 이중 수평재
유지 — 플라이트 `build_railing_line`(kit)의 RailMid(top −0.52)·랜딩/헤드 `build_guard_run`(씬
로컬)의 MidRail·`build_rail_end` CapMid. 살대가 킥→상부 레일 전고를 법정 안목(0.100)으로 이미
채우고 있어 중간 가로대는 방호 기여 없이 픽켓 패널을 가로지르는 이질 수평재("통로 중간의 바")로만
판독.
**Scope**(선신고): ① kit `scene_common.build_railing_line` — `rail_mid_r <= 0` 이면 RailMid/미드
너클 미작성(**가드 절 — 기본값·양수 호출 비트동일**, 기존 호출 씬 무영향, GT-67 Scope 승계)
② s11 플라이트 호출부 `rail_mid_r=0` ③ 씬 로컬 `build_guard_run`/`build_rail_end` 미드 부재 삭제
(랜딩·헤드가드·풋 뉴얼 일괄) ④ hazard ①(동측 헤드 랜딩 1.10 저난간·판정 그리드 원점
15.00/0/5.50)·데크 리본·킥플레이트 대조쌍·판정 눈 불변. 상부 레일 원형 단면 어휘는 존치 — 소거
대상은 '중간' 가로대만.
**GT 판정**: R-3 전용(가드 부재만). Round `260811_w3_s11clean`, baseline `260811_w3_s11piers`.
GT-107 파일럿 동승(regr 귀속 분리 선언).
**§4 착지기록** (2026-08-11): 구현 = 선신고 그대로(① kit 가드 절 `mid_wanted` — 양수 호출
비트동일, 그립 실패 폴백에도 `rail_mid_r>0` 조건 병기 ② 플라이트 `rail_mid_r=0` ③ 씬 로컬
`build_guard_run` TopRail/TopCap 단일화·`build_rail_end` CapTop 단일화 ④ hazard ① 판독 프린트를
살대 스크린 담체로 정정 — z 0.58 중간 가로대는 h0.3 눈높이 위라 은닉축 비담체). floor: 배치
공통. round `260811_w3_s11clean`(15컷). R-3: regr vs `260811_w3_s11piers` — **FAIL 0 · WARN 5**
(FRAME 4 + GRAZE 1). **GRAZE `preset_h0.3_d2` 크롭 판정(X3)**: 변화 = 픽켓 사이 배경(수목·
전벽) 노출 증가 + 패드 재질 정온뿐 — 신규 낙차 에지 노출 0, '바닥 연속' 은닉 담체(살대 안목
0.100 통과 시선) 불변 → GT-105/107 귀속. 육안(X3): `stair_head`·`midlanding` — 하강 가드가
픽켓+단일 상부 레일 리본 언어로 통일, 패널 횡단 가로대 소멸. gallery
`_review/260811_w3_s11clean`.
**Status: OPEN (착지 — 사용자 검수 대기)**

**08-14 사용자 검수 회신(원문)**: "난간 다시한번 확인해줄래? **철창살이 왜 아직 있지...?**
그리고 **주 통로랑 계단이랑 따로 노는 느낌**이잖아. 전반적으로 일체감이 있게끔 만들어
달라고." → 재작업 지시(신규 세션): ① '철창살' 지칭 대상 확정부터([[shape-feedback-protocol]]
— 크롭·한 문장 재진술·확인 후 시공; 후보: 촘촘한 수직 살대 스크린 자체 / GT-96 리본의 격자
인필 미구현분) ② 데크 리본(1.25)과 계단·랜딩 가드(1.10)의 어휘·높이 이원화가 '따로 노는'
판독의 유력 원인 — 단일 제품군으로 일체화. 중간 가로대 소거(본 행)는 유지된 채 그 위에서
재작업.

## 62. GT-106 — scene16 대공사 2차: 포털 차량 방호·지하보도 가독성·통로 조명 (선신고)

**Authority**: 08-11 사용자(갤러리 검수 회신) — "차도에서 차가 삐끗하면 추락하겠는데..? 차도
아래로 내려가는 건 맞는데.. 지하도는 다르게 읽히도록 하면서, 지하도 아래가 조명을 좀 추가하면서
보여야지.. 일단 한번 더 다시 생각하고 실측하고 판단해서 대공사 진행해."
**실측**: 개방 트렌치 서 x 0…7.55(복개 pv0)·동 30.25…36.60(pv1), 연석 뒷면 kb0 7.60/kb1 30.20 —
**포털 립 ↔ 연석 뒷면 이격 0.05 m**(연석 노출 0.150 뿐) = 차도 이탈 차량 무방호 낙하(바닥 −3.00).
통로 인공조명 0등 — 정오 PT approach 컷에서 통로 내부 순흑 판독. 포털 = 헤드월 없는 나지 개구 —
'지하보도' 읽힘 부재.
**Scope**(선신고 정정판 — 초판의 '연석 옆 5 cm 헤드월+가드레일' 안 폐기, 구조로 해소):
① **복개 연장** — 서측 pv0 7.55 → **6.40**(계단 발치까지 — 개방 슬롯 1.15 m 소멸, 슬롯 상면은
보행 데크 0.00·소핏 −0.35 유지, 연석 뒤 1.0 m 가 전부 구조체가 되어 보행 동선도 회복) · 동측
pv1 30.25 → **31.15**(최하 ~4단 상부 복개 — 해당 구간 계단 유효고 최소 2.20 ≥ 2.1) ② **포털
헤드월** — 신규 복개 양단 입면 위 x 6.40…6.60 / 30.95…31.15(t 0.20), y −1.80…+1.80, 상단
+0.90 콘크리트 난간벽 = 차량 방호(연석 뒤 강성 배리어) 겸 포털 프레임('지하보도' 읽힘); 연석
충돌 없음(서 이격 1.00 m·동 0.55 m [computed]), 캐노피 동측 기둥 (6.6, ±2.0) 과 간섭 없음;
perim_rail 은 헤드월 단부 결속으로 재구간(서런 x 0…6.40 — x0=0 종단 포스트 유지, 동런
31.35…36.60) ③ **표지** — `sign_underpass`("지하보도" 청색 유도판, gen_signs 신규 — 실존
관행물·v5.2 방침 정합) 서측 포털변 1식 ④ **통로 조명** — 복개 소핏(−0.350) 중앙열 매입 배튼
5기(x 9.8/14.3/18.8/23.3/27.8 · 1.20×0.14×0.06) + SphereLight r 0.10 · 강도 160000 · 색
(0.93,0.96,1.0) — scene02 GT-3·scene13 밀폐부 전례 ⑤ **T20 불변** — 캐노피·그림자 밴드·서측
계단 x0=0·판정 눈·계단머리 점자 밴드 무접촉(헤드월 그림자는 +X 로 떨어져 계단 비침범
[computed: 그림자 방위 0°]). GT-103 의 '서측 판정 대역(x ≤ 7.8) 기하 불변' 선언은 본 행 ①·②가
사용자 재지시로 개정(신규 기하 x 6.40…7.60 대역 — h0.3 은닉 3거리 재검증 기록 의무).
**GT 판정**: R-1(둘레 방호 재유도 출력) + R-3 + 국소 FRAME 선언(h0.3 시선 헤드월 진입 가능) +
신규 광원 DARK 재스탬프 선언. Round `260811_w3_s16under`, baseline `260811_w3_s16road6`.
GT-107 동승.
**§4 착지기록** (2026-08-11): 구현 = 선신고 정정판 그대로 + `sign_underpass.png` 생성(gen_signs
등재·TEX 등록, 청색 유도판 "지하보도/UNDERPASS") + 둘레난간 재구간. 렌더 self-check(로그
`260811_w3_s16under.log`): 복개 x **6.40…31.15**(도로부 22.70 + 포털 데크 서 1.15/동 0.90) ·
소핏 −0.350 · 통로 유효고 **2.650 ≥ 2.5** · 동측 복개 디딤 3단 최소 유효고 **2.20 ≥ 2.1 OK** ·
헤드월 2기 h 0.90 — 연석 이격 서 1.00/동 **0.75**(선신고의 '동 0.55' 는 계산 오기 — 본 기록으로
정정) · 둘레난간 지주 26·끝기둥 8(서런 0…6.40/동런 31.15…36.60 헤드월 결속, x0 종단 포스트
유지) · 통로 조명 5등 · 태양 검증: 신규 부재 최서단 = 서측 헤드월(그림자 +X 낙하) → 판정
계단대역 신규 그림자 0(T20 캐노피 소유 유지). floor: 배치 공통. round `260811_w3_s16under`
(13컷). R-1/R-3: regr vs `260811_w3_s16road6` — **FAIL 3**(preset_h0.9_d2/d5·under_canopy —
통로 점등·헤드월·데크 연장의 선언 재구성) **· WARN 7**(FRAME) **· PASS 3**, 신규 DARK 0.
육안(X3): `approach` — 통로 내부 순흑 해소(조명 판독)·'지하보도' 표지 성립 · `under_canopy` —
계단 T20 그림자 밴드 유지 + 점등 통로 가독 · `preset_h0.3_d5` — h0.3 은닉 전제 유지·헤드월
정면 판독. gallery `_review/260811_w3_s16under`.
**Status: OPEN (착지 — 사용자 검수 대기)**

**08-14 사용자 검수 회신(원문)**: "지하보도가 도로랑 너무 가깝다니까.. **차도 옆에 인도 공간은
확보하면서** 지하보도가 있어야지.. 아니면 **지하보도를 차도랑 나란하게** 만들거나 말이야..
전반적으로 나아지긴 했는데, **내가 표지 멋대로 넣지 말랬지**. 조사 다시하고 작업할 필요가
있어보여." → ① 방향 부분 긍정("나아지긴 했는데") ② 잔여 결함 = 차도-지하보도 이격 자체:
연석 뒤 인도 폭 확보 또는 통로를 차도와 **평행** 배치로 재구상 — 실물 지하보도·차도·인도
관계 재조사 선행 후 대공사 3차(신규 세션, 새 선신고) ③ **표지 질책**: `sign_underpass` 신설은
"멋대로 넣지 말랬지" 위반 판정 — v5.2 '실존 관행물 유지'를 신설 허가로 확대 해석한 오류.
**룰링 격상 기록: 사인/표지 신설은 사용자 사전 승인 필수.** 재작업 시 `sign_underpass` 제거
(텍스처·TEX 등록·gen_signs 항 포함 롤백 후보).

## 63. GT-107 — 전 씬 바닥 이산 데칼 정온화: 크랙 선·스테인 컷·발자국 소거 (선신고)

**Authority**: 08-11 사용자(갤러리 검수 회신) — "전반적으로 자꾸 바닥에 카펫 이상한 모양 자른
것처럼 노이즈 만들어버리는데, 이걸 좀 더 자연스럽게 만들던지, 아니면 좀 없애든지 해줘." GT-24
전례('이상한 사각형 무늬' → 판석 컷패치 어휘 삭제)의 확장.
**진단**: 판정 눈 거리(2~10 m)·PT_FAST 에서 이산 형상 데칼이 '오려붙인 조각'으로 판독 — ① crack
폴리라인(각선 와이어, s16 shadow_band 좌측) ② stain 컷아웃(고대비 명/암 패치 — s11 랜딩 백화
얼룩·s16 광장 담색 패치) ③ footprint 점열(s16 접근로) ④ scene13 진입로 타이어 폴리시 밴드(자갈
텍스처 대형 스케일 → 판석 줄 판독).
**Scope**(선신고): ① `ground_kit.plan_ground` surface 디스패치 정온 가드 — **crack·stain 행 전
프로파일 미발행**(어휘·빌더·z 래더 존치, `NEGOBS_DECAL_FULL=1` 복원 팔), footprint/edge_litter
발행처 동반 점검·동일 처분 ② wear_lane(동일 재질 저대비 답압 띠)·weed·relaid·아스팔트 patch
(실존 절삭 사각) 존치 ③ scene13 로컬 — 판석 러너의 근인 확정: 룩 레이어 stone 패밀리 토큰에 "polish" 가
등재되어 `Looks/Polish`(휠 트랙 밴드)가 **판석 텍스처로 승격**되고 있었음(씬 상수는 화면
미도달). 조치 = 재질 경로 `Looks/Polish` → **`Looks/TyreTrack`** + 지오메트리 프림
`DrivePolish/XRoadPolish` → **`DriveTrack/XRoadTrack`**(경로 토큰 전면 소거 — 재질 개명만으로는
지오메트리 경로의 "polish" 가 재승격) + `polish_color` 0.048→**(0.082,0.079,0.073)**·
`polish_rough` 0.46→**0.88**(필드 러프 동일) · `polish_color` 최종 (0.055,0.055,0.056).
**드라이 프로브 확정(4차)**: 개명·러프 정합 후에도 남던 담색 러너의 실체 = 밴드 프림이 아니라
**Drive_Main 아스팔트 승격 재질의 매크로 패치 변이**(러너 위치 y ±1.48 에 프림 부재 —
fake-USD 전수 프로브). 워름 탠 틴트(0.215,0.210,0.198)가 패치 명암을 증폭 → **중성 회색
(0.148,0.150,0.154)** 으로 정정(라이브러리 차도 톤 — s11/s16 차도에서 러너 판독 부재가 증거,
한국 진입로 실관행 = 회색 아스팔트). `asphalt_scale` 은 0.35 **유지**(인자 = 타일
한 변 m — 2.8 1차 시도는 의미 오독, 동일 세션 원복·라운드 재실행) ④ sceneD4 낡은 tactile 띠
(§4-13)·P-4(scene04 퇴적) 무접촉. 공유 킷 변경 §2.3 준수 — **s11 파일럿 렌더 선행 육안** 후 동일
배치 s06/s13/s16 확산, 잔여 씬 육안은 차기 allview 라운드로 선언.
**08-11 파일럿 소견(1차 렌더 후 Scope 증보)**: crack·stain 정온으로 s16 계열 아티팩트는
소거되나, s11 랜딩·데크의 백화 얼룩은 데칼이 아니라 **보행 슬래브 재질이 벽용 텍스처
(`concrete_wall` — 백화 변이 큼)를 물려받은 소스 오지정**으로 확인 → ⑤ scene11
`M["concrete"]`(데크 슬래브·랜딩 패드·기둥 캡 — 보행/수평면 계열)를 `concrete_floor` 로
교체(수직 파라펫의 concrete_wall 은 유지 — 용도 정합) ⑥ 동 씬 강재 패드/계단 `M["metal"]`
albedo 압축 강화(brightness/add/desat 0.587/0.213/0.78 → **0.42/0.30/0.92** — 잔존 러스트맵
변이가 보행 패드에서 백화 조각으로 판독되던 것을 도장강 판으로 정리, 평균 알베도 보존
0.477→0.489 [computed], 릴리프는 nor/rough 전담). 타 씬 동일 오지정 여부는 차기 allview
라운드에서 점검 선언.
**GT 판정**: R-2 계열(데칼/재질 전용 — 기하·GT 불변, geom_invariance 33/33 증빙). Rounds:
`260811_w3_s11clean`(파일럿) + `s06bay14`/`s13frost_c~e`/`s16under` 동승, regr 귀속 분리 선언.
**§4 착지기록** (2026-08-11): 구현 = ①②⑤⑥ 선신고+증보 그대로(정온 스킵은 로그에 명시 출력 —
s11 4행·s13 2행·s16 2행 확인, footprint/edge_litter 는 호출처 0 의 준비 어휘로 무발행 확인)
④ 무접촉 유지. §2.3 준수: s11 파일럿 렌더·육안 후 확산. **s13 ③ 최종 소견(드라이 프로브)**:
판석 러너의 최종 실체 = 씬 프림이 아니라 **룩 레이어 asphalt 클래스가 Drive_Main 위에 그리는
매크로 패치 변이**(y ±1.48 러너 위치에 프림 부재 — fake-USD 전수 프로브; 씬측 `asphalt_tint`
는 승격 재질에 미도달 확인). 씬 범위 조치(스테인 오프·stone 승격 소거·트랙 상수화)로 판석
무늬·점열·크랙 선·백화 조각은 소거 완료; **잔여 필드 톤·매크로 패치 대비는 레버1(공통 재질
재보정, 08-10 승인) 슬롯의 룩 클래스 차원 항목으로 이월 선언**. floor: 배치 공통. rounds/regr:
각 행 기록 참조(s13 3쌍 WARN 18 중 데칼 정온 성분 동승 귀속). 육안(X3): s16 `shadow_band` —
크랙 각선·점열 소거 · s11 `midlanding` — 백화 조각 소거(잔여 저대비 도장면 변이) · s13
`entry_approach` — 판석 러너 무늬 소거. 잔여 29씬 육안은 차기 allview 라운드 선언.
**Status: OPEN (착지 — 사용자 검수 대기 · 레버1 이월 소견 1건)**

## 64. GT-108 — 품질 확산 파일럿 A(레버1 1차): 룩 클래스 톤·입도 재보정 + s16/s11 틴트 분화 (선신고)

**Authority**: 08-13 사용자 — "S04도 카펫 문제가 완전 해결된 건 아니야..(현상 유지 룰링, 보고서
§9 정정) 일단 **다른 씬들도 관련 부분 퍼져나갈 수 있게 어떻게 좀 해봐**" + 08-10 5차 레버1
승인("사실화 작업이면 진행"). 설계 근거 = `reports/s04_quality_gap_survey_v1.md` §5~§7
(F2 상수색·F3 입도 붕괴·F4 채도·F8 원경 — 파일럿 A 사양·합격선 그대로) + GT-107 이월 소견
(asphalt 매크로 패치·등화 틴트 — s13 차도 micro_sd 0.52 실측 본체).
**Scope**(선신고): ① `scene_common` LOOK_CLASS — paving/concrete/stone 알베도 상한 하향(목표
w80 ≤ 5·하단 평균휘도 ≤ 0.62) ② asphalt 클래스 매크로 패치 강도·등화 틴트 재보정(목표 노면
micro_sd 0.52 → ≥ 6) ③ s16·s11 씬 틴트 분화(동일 롤 × 2~3틴트)·원경 잔디 상수면 → 텍스처+
암틴트(F8) ④ 이름–역할 감사(접촉 씬 s16/s11 한정) ⑤ 헥스 타일링(F7)은 **미구현 신규라 본 행
제외**(별도 행 후보) ⑥ E14 `brick_red` scale 2.0→0.87 은 **본 배치 접촉 씬 한정** 교정, 잔여
씬은 레버1 확산분 선언 ⑦ 검측 스크립트 `scripts/quality_metrics_probe.py` 신설(보고서 §1.2
지표 재현). **R-2 순수** — 기하 0, geom_invariance 33/33 비트동일 증빙 의무. 합격선: 근경
micro_sd ≥ 8 · gnd_flat ≤ 5 % · gnd_chroma ≥ 0.05 · w80 ≤ 5 · tile_peak@8px ≤ 0.7 · regr FAIL
증가 0 · DARK 신규 0. Rounds `260813_w4_s16tone`/`s11tone`/`s13tone`(확인) — baselines
`260811_w3_s16under`/`s11clean`/`s13frost_c`. 검수 대기 갤러리들과 체인 명시(귀속 분리).
**GT 판정**: R-2(재질 전용). 시공 = Opus 병렬(파일 소유: scene_common LOOK 구역+s16+s11).
**§4 착지기록** (2026-08-13): 구현 = ①`_albedo_band`(유효 선형 알베도 기준·스칼라 스케일 —
paving/concrete/stone alb_max 0.34) ②asphalt alb_min 0.10 기하평균 연성 하한(N2 패치 사다리
보존 실측)·patch 1.0→0.45·macro 0.12→0.06·bump 2.1·tri_dither 0.55·det_scale 3.0 ②′paving/
concrete 입도(det_scale 4.0·dither 0.50·bump 1.8/2.0 — s16 판정 크롭이 광장 포장이라 asphalt
단독으론 무효과, 판단 근거 기록) ③s16 Walk 3틴트(±5~7 %)·s11 2틴트·GrassFar 암틴트 ④사장
LOOK_ROLE 2키 삭제·s11 Mesh→MeshSteel ⑤헥스 무접촉 ⑥brick_red 0.87(s16/s11) ⑦검측
`scripts/quality_metrics_probe.py`(§1.2 재현·A/B군 분리 — 판정은 자체 baseline 대비).
floor: py_compile·SMOKE(s16/s11/s04/s13) rc0 · **geom_invariance R-4/R-6 33/33 + 4씬 해시
문자 동일(R-2 순수 증빙)** · lint stash A/B 6씬 E1=1·W52=52 신규 0 · building_kit rc0.
rounds `260813_w4_s16tone/s11tone/s13tone`. regr: s16 **PASS 12·INFO 1**, s11 **PASS 15**,
s13 WARN 4(FRAME d10) — FAIL 0·DARK 신규 0 ✓. **합격선 실측(정직 판정)**: 예고대로 대체 미달 —
s16 approach micro_sd 4.89→4.93·w80 1.4→1.3·mean_lum 0.641→0.640(불변), s11 stair_head
gnd_micro_sd 9.57→10.18(+6 %)·tile_peak 0.42→0.37. 원인 확정: 밴드는 정상 작동(로그
알베도밴드 — 전 코퍼스 22씬 32재질 교합)하나 **s16/s11 판정 크롭의 밝기 주인은 밴드 제외
대상**(curb 0.748/0.385 제외 준수 · s16 Roof→wood 오분류 방치[under_canopy dark 게이트 충돌
회피] · 승격 등화 구조). 파일럿의 결론 = 레버가 닿는 곳/안 닿는 곳의 실측 지도. **레버1 2차
후보 3건 이월**: curb 클래스 포함 여부 · Roof 분류 정정(+dark 게이트 재판정) · 등화 타깃
직접 이동. 타 씬 파급(32재질) 육안은 차기 allview 선언. 부수 기록: s16 Looks/Lamp 중복 정의
(GT-106 착지값 876행에 사장 — 검수 판정 보호 위해 무접촉 보고).
**Status: OPEN (착지 — 사용자 검수 대기 · 레버1 2차 이월 3건)**

## 65. GT-109 — scene01 강의동 재유형(K5′): office 커튼월 → 석조 수직창 강의동 (선신고)

**Authority**: 08-13 사용자 — "(건물) 일단 한번 만들어서 나한테 보여줘봐". 설계 원본 =
`briefs/building_typology_proposal_v1.md` §3.1(사용자 08-11 "각 씬에 맞는 건물 유형의 디자인
위주" 반영). 결재 7-1 기본 처리 적용 — **평지붕+두꺼운 코니스(K5′)**, BS-4 override 초과폭
불변.
**Scope**(선신고): R1/L1 씬 로컬 재건(킷 동결 — 갭은 기록만): 깊이 4.5→11.0/9.0 · 층고
3.90/3.70(처마고 15.00/11.30) · 수직창 1.60×2.20 7련(**커튼월 25.2×13.1 m 단일 프림 대체**) ·
기단 1.20 · 중앙 아치 출입 베이 4.80(박스 2단 근사) · 코니스 0.60 돌출 · 동판 명패(간판 금지).
재질 = 기존 롤(marble_light/stone_flag·granite_dark — 신규 조달 없음, 결재 7-5 기본 처리).
§0-2 corridor 5.5 불가침 · 축선 개구 20.0 유지 · 판정 눈 불변.
**GT 판정**: R-3 + FRAME 선언(근접 2동 매스 변화 — 전 컷 재구도 가능). Round
`260813_w4_s01k5`, baseline `260806_w3_fixqueue2`(13컷 완전 라운드 — 확인 확정).
**§4 착지기록** (2026-08-13): 구현 = 씬 로컬 K5′(`lecture_geometry`/`lecture_prims` 순수 함수 —
SMOKE 가 실물 실측) R1 47→50·L1 30→33프림(씬 520→566): 깊이 11.0/9.0(배면 확장)·층고
3.90/3.70·수직창 7련/5련(1.60×2.20, **CurtainGlass 25.2×13.1/17.2×9.1 대체**)·기단 1.20
granite_dark·아치 출입(4.80, 2단 내접)·코니스 0.60·명패 2·간판/옥탑/식생 0. **BS-4 초과폭
감소**(+13.25/+10.18 — 이전 +14.25/+10.88, 구 옥탑 소멸). §0-2 corridor 5.5·개구 20.0 유지.
검산 28→40행(GT-109 12행 신설). **착지 검수 보완 2건(오케스트레이터)**: amphi_view(포털
4~5 m 정면)에서 4.80×2.80 통유리가 '검푸른 대판'을 국소 재현 → 5b 로비 분할(전고 문설주
2+트랜섬 1 ×2동, +6프림 — 동결선 77→83 재실측 이동), 1차 분할이 하부만 갈라 상부 3.1 m
통판 잔존 → 문설주 전고 연장(2차). floor 배치 공통 + 재렌더 2회. regr vs fixqueue2:
**FAIL 2(amphi_view·h1.8_d2)·WARN 4** — 전량 K5′ 재건 FRAME 귀속(육안 X3: amphi_view —
석재 셸+기단+분할 로비 그리드 판독, 대판 소멸 확인). gallery `_review/260813_w4_s01k5`.
**Status: OPEN (착지 — 사용자 검수 대기)**
**08-14 사용자 검수 회신(원문 그대로)**: "s01 건물 저게 최선이야..? **통유리는 좋았는데**, 좀 더
이쁘게 만들어줄래? 자꾸 1층 라인이랑 상부라인 연결 흐름이 부자연스러워지는 경향이 있어. 물론
끊어서 만드는건 맞는데, 진짜 기계적으로 끊어서 만들어진 느낌..? 통유리에 십자가 그리다 만
느낌이잖아. 벽이 왜 저렇게 끊어져 있어. 그리고 **광장 확장 좀 더 하는게 차라리 나을 것 같아.
건물이랑 거리 간격 좀 생각해서 배치해줘.**" → 판정 갱신: ① 커튼월 통유리는 **긍정**(본 행의
'대판 = 판독 문제' 전제는 사용자 취향과 불일치 — 통유리 유지·발전 방향으로 재작업) ② 분할·
분절이 기계적('십자가 그리다 만' 로비 그리드, 끊긴 벽 피어) — 1층 라인↔상부 라인의 연결 흐름
우선 ③ 광장 확장 + 건물-거리 이격 재배치 지시(기하 변경 — 신규 세션에서 새 선신고로). 총평
룰링 동반: "**벽면 위주로** 신경썼어야" — 건물 트랙 공통 방향 정정(§총평, 행 65~68 공유).

## 66. GT-110 — sceneN3 가로벽 1층 띠(최소판): 근생 개구·기단·간판대 (선신고)

**Authority**: 08-13 사용자(위와 동일 발화). 설계 원본 = 제안서 §3.4 입면 문법 + §3.9 N3 행
(근접 2동 d_true 10.0·z_ceil 1.71·in_frame — 코퍼스 최근접 가로벽). 결재 7-2 기본 처리 —
**킷 티어 신설 없이 씬 로컬 최소판**.
**Scope**(선신고): 근접 2동 1층 대역(z ≤ 4.0)만 — 상가 베이 3.0~4.5 · 개구 상단 3.20·유리면
0.05 후퇴 · 기단 화강석 1.10 · 간판대 h 0.80(하단 3.15, 돌출 ≤ 0.30) · 차양 0.70(하단 2.60) ·
셔터 1베이(`assets/urban_cc0/rollershutter_door` 보유분). 층고 배분 1층 4.00+잔여 등분
(`plan_levels` 지원 확인됨). 상부 실루엣·높이 불변. 판정축(바닥 착시) 직교 — 무접촉.
**GT 판정**: R-3(드레싱·프림 추가, 동당 +6~8). Round `260813_w4_n3wall`, baseline
`260731_w3_full`(개별 13컷 — 실측 확정).
**§4 착지기록** (2026-08-13): 구현 = 포디움 1장 → 기둥4·멀리언7·걸레받이·개구 유리(0.05
후퇴)·인방·차양10·간판대3(Fascia 명명 — lint sign 오집계 회피)·셔터 1베이(박스 근사 —
`rollershutter_door` 66프림/치수 불합 사유 도크스트링 기록), 동당 31→36(+5)·씬 643→653.
필지 3분절(12/16/12 — 매스 분할 0)·층고 1층 4.00 재배분(`relevel_floors` — 상부 실루엣
불변)·brick_red 0.87. `_streetwall_report()` 신설(판정축 여유 7.35 m·Z파이팅 오프셋 사다리
전항 OK)·`_geometry_report` 문구 정밀화·BANNER 10행. floor 배치 공통 + GEOCHECK rc0 ·
lint 653 판정 동일(E0/W10/B1). regr vs 260731_w3_full: **PASS 12·WARN 1**(beauty_overview
FRAME — 1층 띠 신설 귀속, 육안 X3: 상가 개구 연속+차양 성립·바닥 착시 무접촉). gallery
`_review/260813_w4_n3wall`. **Status: OPEN (착지 — 사용자 검수 대기)**
**08-14 사용자 검수 회신(원문)**: "상가 거리 느낌은 나는데 **문이 왜 없니..?** 그리고 너무
천막도 캐노피처럼 설치해둔 느낌..? 의도한게 아니라면 좀 더 조사해서 생각해서 그려줘" →
재작업 지시: ① 상가 출입문 부재 해소(개구·유리만 있고 문짝 없음) ② 어닝이 강체 캐노피처럼
읽힘 — 실물 어닝(천막 折 구조·처짐·프레임) 조사 후 재표현. 신규 세션 몫.

## 67. GT-111 — scene15 다세대(K2) 2동 신설 + K7 옥상 난간·물탱크 (선신고)

**Authority**: 08-13 사용자(동일 발화). 설계 원본 = 제안서 §3.3(코퍼스 79동 중 다세대 1동 —
"달동네를 달동네로 만드는 대비" 부재의 정면 해소).
**Scope**(선신고): ① K2 2동 — **골목 벽선 밖 배후에만**(A-15-1/2 y ±0.58/±0.88 불가침):
4층(필로티 2.90 + 2.80×3 = 11.30 + 파라펫 1.20) · 폭×깊이 9.0×8.0 · 일조사선 상부 1.60 후퇴 ·
필로티 개구 4.60×2.10 · 노출 가스 입상관(황색 띠 2줄·층당 +1.00·주밸브 1.60~2.00) · 계량기함 ·
옥외 계단 1련 · 창 세대당 침실 1.50×1.40+거실 2.10×1.50 ② K7 기존 주택 — 옥상 난간(살대)
h 1.00~1.10(연대 정합) + 물탱크 1~2기. 재질 = 기존 plaster 틴트 계열(신규 타일 롤 조달 안 함 —
결재 7-5 기본 처리). 씬 로컬 빌더 확장(킷 미배선 상태 유지).
**GT 판정**: 신설 매스 collider 발생 — **R-1(레지스트리 재유도 출력) + R-3 + FRAME 선언**.
골목 판정축·낙차 은닉 불변(배후 배치 증빙). Round `260813_w4_s15villa`, baseline
`260806_w3_allview5`(4컷 — 실측 확정).
**§4 착지기록** (2026-08-13): 구현 = K2 2동 +222프림(A 월드 cx −6.60·B 회전군 로컬 11.05 —
§3.3 표 전 수치: 4층 11.30+파라펫·9.0×8.0·일조 후퇴 1.60·필로티 4.60×2.10 뒷길향(골목 진입
불가 사유 기록)·가스 입상관 4개소+황색 띠·계량기·옥외계단 16단·창 층당 4·측벽 무창 E8) +
K7 옥상 난간 3동 69프림(h 1.00~1.08 살대 — 파사드 안쪽 0.10 후퇴, 골목 침범 0)·물탱크 2기
(치수 상이 — v5.1 '12동 동일 복제' 실패와의 차이를 게이트로 어서션). 씬 448→743. 이격 증빙:
골목 회랑 A 3.60/2.77·B 3.30/2.47 m, 기존 파사드 y 무접촉, 석축-뒷벽 0.08 매몰 3건(공면
회피 의도). `alley_selfcheck` +20 어서션(§8/§9 — villa_parts 공유 유도). floor 배치 공통 +
SELFCHECK rc0 · lint E0/W1(기존) — prims 743. regr vs allview5: **INFO 9·PASS 1·WARN 3**
(top_compress FRAME + d10 DARK 2 — 전량 신설 매스 프레임/그림자 귀속, 육안 X3:
beauty_overview — B동 매스가 우측 근경 진입[예측대로], 골목 협곡·낙차 은닉 불변 판독 ·
측벽 무창 대비가 달동네 스톡 대비 성립). gallery `_review/260813_w4_s15villa`.
**Status: OPEN (착지 — 사용자 검수 대기)**
**08-14 사용자 검수 회신(원문)**: "얘는 **골목 시점에선 굳이 건드릴 필요가 크게 없었을 것
같은데..?**" — 헤지 판정(철회 지시 아님): 판정 컷 관점에서 신설 K2 의 기여가 작다는 소견.
처분(존치/축소/철회)은 확정 판정 대기 — 격상 금지.

## 68. GT-112 — scene21 관공서(K6) 정합: 층수 3→2·기단 롤 분리·수평 3분절 (선신고)

**Authority**: 08-13 사용자(동일 발화). 설계 원본 = 제안서 §3.8 — h 상향 불가(여유 0.58 m
실측·`plaza_selfcheck` 게이트) → **높이 불변·층수 하향**이 유일 경로.
**Scope**(선신고): 원경 3동(E1~E3) floors 3→**2**(층고 3.3~3.75 정상화) · 수평 3분절(기단
1.60/신부/코니스 0.40) · 개구율 0.20 · 기단 `granite_dark` 롤 분리(E6 저위험 시험 — E3 동
한정 가능) · 열주 신설 없음(기존 build_facade 존치). 높이·backdrop 강제·판정 게이트 불가침.
**GT 판정**: R-3(원경 입면 프림). Round `260813_w4_s21civic`, baseline `260806_w3_allview5`
(4컷 — 실측 확정).
**§4 착지기록** (2026-08-13): 구현 = E1~E3 floors 3→2(층고 3.30/3.55/3.75)·수평 3분절(기단
1.60/신부/코니스 0.40)·개구율 0.200 정밀 역산·창 2열(코니스 하부 여백 0.70 균일)·E3 배면
1면 추가(축소면적비 0.44 기준 초과 유일면)·기단 E3=granite_dark/E1·E2=marble_light 비교쌍
(E6 시험). 킷 backdrop 9프림 **bit-identical**(+씬 로컬 42: Win36·Cornice3·Plinth3, 543→585).
**시공 중 적발**: `_seed_of` 가 floors 를 시드에 포함 — 3→2 만으로 옥탑 지터가 재추첨되어
2.4~4.7 m 이동(비선언 스카이라인 변화) → `seed_floors=3` 고정으로 비트동일 복원(사유 코드
기록). ridge 여유 +0.58/+0.66/+0.58 **베이스라인 동일 수치**·plaza_selfcheck 23 PASS(신설
9행). floor 배치 공통 · lint E0/W7/B1 판정 동일. regr vs allview5: **INFO 9·PASS 4** — 매치
4컷 전부 PASS(원경 41~57 m 입면 변화가 판정 역치 이하, 육안 X3: facade_front — 열주+2층
분절+석재 청사 판독 성립, 지붕선 위 하늘 유지). gallery `_review/260813_w4_s21civic`.
**Status: OPEN (착지 — 사용자 검수 대기)**
**08-14 사용자 검수 회신(원문)**: "씬 자체가 **기념관 느낌**이 아니었나..? 왜 관공서 판독을
하라고 하지..? **씬 정체성 파악해서 다시 작업**해야 할 것 같은데?" → 제안서 §3.8 의 K6 관공서
배정(코드 주석 «G1 stone institutional block»·연대조사 '청사·도서관' 근거)이 사용자 정체성
판정(기념관)과 불일치 — 사용자 우선. 재작업 = 기념관 유형(전시·추모 계열 어휘) 재조사 후
신규 세션에서. 본 회신으로 건물안 §3.8 s21 절은 무효.

## 69. GT-113 — R1 룩 레이어 배선 수리 W1~W7: 감사 확정 결함의 정식 처리 (선신고)

**Authority**: 08-14 사용자 — "해당 폴더에 대해 전권 줄테니까 3일동안 네가 차근차근 확인하면서
프로젝트 향상시켜봐 … 일단 지금 있는 씬들 집중 … drop-off 계열에 집중 … cue랑 현실성, 그리고
생각해야 할 요소들 체계적으로 잘 검토" (3일 자율 개선 위임). 설계 원본 =
`reports/scene_audit_realism_survey_v1.md` §2.1 (배선·봉인 결함 W1~W7, 코드 대조 확정) —
레버1 2차 이월 3건(행 64) 중 curb/등화의 기계적 원인이 W1·W2 에 귀속됨을 실측 특정.
**Scope**(선신고 — 전부 scene_common/MDL/도구 층, 씬 파일 무수정):
① W1 `make_pbr` OmniPBR 분기에 `_albedo_band`/`_effective_sat` 배선 — 상수색은 밴드+탈채도,
   텍스처는 tint 밴드. **현 클래스 값 기준 비트동일**(omni 상수색 잔여 클래스 = metal·water·
   glass·paint·sign·misc 전부 sat 1.0·밴드 미보유 — 값 부여는 GT-114 별행).
② W2 `NEGOBS_DETAIL_SCALE` 강제 해소 — `run_data_render.py` 의 상시 설정 제거, `_DETAIL_MAP`
   패밀리 기본 mineral 12.5→4.0 · granular 8.0→3.0(GT-108 클래스 값·RTX 조사 권장 1~4 대역
   정합; metal 25.0 유지). env 는 A/B 스윕 전용으로 복원. `look_report()` 에 실효 det/override
   1행 노출(사장 재발 방지 계기).
③ W3 `wire_unit_cell_to(mtl, unit_cell)` 헬퍼 신설(기존 `_wire_unit_cell` 재사용, 기본 미호출
   = 비트동일) + **파일럿 s21 1씬** 되먹임 1줄(plaza_granite 0.600 원장 값) — 확산은 검수 후.
④ W4 `use_blend` 하드코딩 False → `_make_ground_pbr(blend=None)` 선택 인자 개방(기본 None =
   비트동일, 값 주입은 후속 파일럿).
⑤ W5 `_LOOK_RULES` 지형·배경·목재·배관 어휘 추가(hill/shore/bank/scrub/forest/terrain →
   soil·veg / plank/joist → wood / pipe/gaspipe → metal) — misc 낙하 해소. ⑥ W6 키워드 충돌
   4건(canopy→veg 제거·band 접미 한정·awning/membrane 분리·tread 분리 검토 — tread 는 nosing
   유지가 옳은지 실측 후 결정). ⑦ W7 발광 재질 비발광 채널(bevel) 룩 통과 — emission 보존.
**GT 판정**: 전 항목 R-2(재질 전용, 기하 해시 불변 — `geom_invariance_check` 33/33 증빙).
위험 기하·보행면·낙차 에지 접촉 0. 파일럿 렌더 1~2씬(s21 + s13) A/B 후 확산(§2.3).
Round: GPU 가용 시 `260814_w4_r1wiring`(RT 파일럿 + PT 판정). baseline 최신 라운드.
**§4 착지기록** (2026-08-14 저녁): 코드 착지 commit fb5448f. 검증 = py_compile ·
geom_invariance MTL 0/1 **33/33 비트동일** · lint ERROR 17=17(A/B 동일) · 분류 diff
전수(24건 전부 의도 변경, 도장 밴드 5종 정확일치 핀). 파일럿 렌더는 GT-114 와 합동
`260814_w4_r1r2pilot`(5씬 PT-fast) — s21 unit_cell 배선 발현 확인(테라스 판별 톤차
육안 성립), regr FAIL 19 전량 선언 변화 귀속(`regr_260814_w4_r1r2pilot.json`).
R0 프로브(`260814_w4_r0probe`, scene04 2컷 × 5팔): **PT-fast 등가성 실측 재확정**
(md5 전부 상이 = 진짜 재렌더에서 slope Δ≤0.008·노이즈 플로어 동등 — 스파이크의
md5 동일은 하네스 사고, 등가 결론 자체는 유효) · filterRadius 0.5 효과 +0.02(미미)
· 디노이저 slope 영향 ≈0 → **현행 렌더 설정 유지 판정**. 확산 육안은 차기 allview.
**Status: OPEN (착지 — 검수 대기)**

## 70. GT-114 — R2 클래스 재보정 1차: 낙차 에지 단서 클래스(nosing·curb) + snow·metal 밴드 + macro 파장 (선신고)

**Authority**: 08-14 사용자 3일 자율 위임(행 69 동일 발화 — "drop-off 계열에 집중").
설계 원본 = 감사 §2.2(클래스 처방 공백) + RTX 조사 레버 0(macro_wavelength 대역) —
GT-108 레버1 2차 이월 중 curb 항의 정식 처리.
**Scope**(선신고 — LOOK_CLASS 표·build_nosing 기본색·macro_wl 스펙화, 전부 R-2):
① **nosing**: tex="concrete_floor" 승격 경로 개통 + det_scale 4.0 + alb_max 0.50 +
   bevel 0.012→0.003(W6 으로 tread/step 이 concrete 로 분리된 뒤라 이 클래스는 논슬립
   스트립 전용 — 두께 6 mm 부재에 12 mm 반경은 형상 왜곡. IBC 12 mm 는 답면 코 근거였음).
   `build_nosing` 기본색 (0.85,0.72,0.10)→(0.60,0.48,0.10) — 선형휘도 0.703→0.478
   (감사 권고 0.40~0.50 대역 [derived], 파스텔 레몬 해소). 폭 통일(KS 50 mm)은 기하라
   별행 이월. ② **curb**: tex="concrete_floor"+tex_alts(granite_dark)+det_scale 3.0+
   alb_max 0.34 — 연석 승격 경로 개통(이월 항 본체). ③ **snow**: alb_max 0.62(코드 자필
   TODO 0.55~0.62 상단 — C1 순백 81.6% 대응) + patch 유지. ④ **metal**: alb_max 0.50 —
   W1 배선 경유 첫 발현(난간 0.818·등주 0.877·순백 계열 클램프. 도장 밴드·사인은 별
   클래스라 불변). ⑤ **macro_wavelength_a** 14.0 하드코딩 → spec "macro_wl" 스펙화 +
   paving/concrete/asphalt/stone 에 0.55 부여(RTX 실측: slope 실효 대역 지상 2~10 cm,
   14 m 는 19배 위 — 레버 0). 타 클래스 기본 14.0 유지 = 비트동일.
**GT 판정**: R-2 순수(기하 불변 — geom_invariance 33/33 증빙 예정). 낙차 에지 재질만
접촉, 기하·보행면 불변. 파일럿 렌더(s13·s16·s21·C1·D4) 후 확산 판정. Round:
`260814_w4_r1r2pilot`(R0 프로브 후 GPU 대기열). baseline 최신 라운드.
**§4 착지기록** (2026-08-14 저녁): 코드 착지 commit 260fb91, 파일럿 렌더
`260814_w4_r1r2pilot` 5씬. 실측(shortcut_audit, h0.3_d5 기준 전→후):
**s13 지면대 암부 31.9→1.4 %·clipLo 10.2→0.3** (asphalt macro_wl+밴드 발현) ·
**s21 clipHi 47.3→21.5**(테라스 순백 해소) · **C1 clipHi 60.9→15.3**(snow 밴드) ·
s16 불변(0.8/18.8→0.3/18.5 — GT-108 실측대로 크롭 밝기 주인은 잔여 이월분) ·
D4 는 알베도만으로 부족(암부 100 % 잔존) → GT-116 ②-2 로 이관. 육안: C1 눈이
클립 없는 실설로, s21 이 판별 톤차 있는 석재 광장으로, s16 난간이 도장강으로 판독.
regr FAIL 전량 선언 귀속. nosing/curb 발현 육안은 차기 allview(파일럿 컷에 근접
노징 없음). **Status: OPEN (착지 — 검수 대기)**

## 71. GT-115 — R4 씬별 기계 결함 수리 1차(비-hazard): 관통·부유·허공 종결·물리 불성립 (선신고)

**Authority**: 08-14 사용자 3일 자율 위임(행 69). 근거 = 감사 확정 지적(전건 크리틱
valid-new + 본 세션 크롭 재검증 확정, `scene_audit_findings_v1.json`).
**Scope**(선신고 — 위험 기하·보행면·낙차 에지 무접촉 항목만. hazard 접촉 건은 별행):
① s05 조명 타워: 등기구 3기 지주 관통 해소(헤드 오프셋+브래킷, 무대향 틸트) — 지주
   상단 마감. 스피커 전례(v6 삭제) 판정과의 정합은 형상 완성으로 응답. ② s13 계단실
   핸드레일 허공 사각 프레임 → 랜딩 정착 마감(벽 물림 또는 하향 절곡). ③ s16 캐노피-
   게이트 이중 기둥(이격 10 mm) 해소 — 게이트 린텔을 캐노피 기둥에 지지(기둥 1벌화).
④ sceneC4 디딤판 위 정체불명 검은 상자 5+ — 코드 원인 규명 후 소거/접지(낙차 판정컷
   정면 CG 아티팩트). ⑤ sceneD1 파렛트 스택 물리 불성립 — 단별 오프셋 지지면 내 클램프
   +상하면 접촉. ⑥ sceneD2 piles 단일 타원체 → mounds 전례(r2 판정)와 동일 3-로브 분할
   +토우; 철근 훅 허공 종단 정리. ⑦ s12 수변 볼라드 정리 — v5.1 §2(볼라드 = 차량 진입
   우려 지점만)·s18 전례(차도 무 → 제거) 근거로 잔디/수변 고립 볼라드 소거, 가로등
   등기구 큐브 → 하향 틸트+렌즈면 최소 형상, 배경 교량 방호벽 1단(원경 실루엣 —
   판정 밴드 밖). ⑧ (공용) build_planter 관목 억제 스위치 — N1 반사연못 위 관목 3주
   해소; build_plinth 문 개구 컷 — N1~N4 기단 띠의 출입문 절단 해소.
**GT 판정**: 전 항목 R-3(프림 추가·이동·소거 — 보행면/낙차 에지/hazard box 불변).
regr FRAME/OCCL 변동은 선언 변화 귀속. 검증 = py_compile + SMOKE(지원 씬) + geom/lint
floor + 차기 파일럿/allview 라운드 육안. 시공 = 파일 소유권 분리 병렬(씬당 1기).
**Scope 추기(2026-08-14 심야 — 같은 Authority·같은 비-hazard 기준)**: ⑨ s09 확정
지적 8건(갈대 재질·형상 / 원경 블롭 알베도 선언대역 복귀 / 정자 마루 / 석주 재질·치수 /
지붕·절병통 / 조경석 묻힘 / 관목 채도 / 오리배 마감 — 수제선 코핑·수면 반사·원측 흑띠는
제외) ⑩ s08 옹벽 분절(줄눈 13·배수공 28·갓돌 1 — infra_kit 수치 준용, P-3 개구 무접촉
게이트化, 3㎡당 1공 미달은 연구 판독 사유로 선언 후 1열만) ⑪ s18 크랙 리본 재바인딩
(s16 기지 해법 이식)·모래 톤·스와시 밴드 발현·수면 수평선·포말 형상 ⑫ s19 도막 상수색
재보정(승격 무죄 실측 — M2 대역 내 0.16)·심 대비·덧방 3로브(+2.5 mm 낙차 아님)·방사
줄눈은 조사만(texture_rotate_a 미배선 발견 — 후보 기록) ⑬ C2 낙엽 이중층 정합·잔디
채도·보도 줄눈·판자 클립 ⑭ s10 난간-바위 이격·종단 마감·클러스터 다양화·파고라 구조·
향 의존 풍화·손잡이(순흑 슬롯은 별행 유보) ⑮ s17 수면 러프니스·갈대 실물화·대안 관목열
실자산 이관(GT-63 제외 목록 밖 실측 확인)·사면 UV 분리(배터 빗살은 별행 유보).
sceneC4 ④의 볼라드 tactile OFF 는 §4-6(볼라드 아래 패드 금지) 정합이나 **P-12(12/42 ON
사용자 소유)와 긴장** — 타 batch1 5씬 기 OFF 실측을 근거로 시공하되 본 행에 표기,
사용자 재확인 대상.
**§4 착지기록** (2026-08-15): 15씬 시공 완료(commit fb12e5f — 병렬 15기, SMOKE 15/15
· geom 33/33 · lint 17→16). 검증 렌더 `260815_w4_r4batch`(17씬, PT-fast 전 컷) —
regr **FAIL 1**(s10 through_treads FRAME = 바위 재배치·핸드레일 신설 선언 귀속) ·
WARN 7(FRAME/DARK 전량 선언 귀속, `regr_260815_w4_r4batch.json`), gallery
`_review/260815_w4_r4batch`(68컷). 육안 X3: s09 across_river — 갈대 분홍 소멸·오리배
콕핏·정자 기와 성립 / s10 reversal — 관통 0·라운드 손잡이·리턴 종단 성립 / sC4
lower_lookback — 검은 상자 0·수막 유지 / s18 wave_raking — 수평선 폐합·스와시 밴드
성립. **잔여 소견 3건**(차기 처리 후보): s10 사면 카키 상수면(휴면 잔디 텍스처 —
감사 high 미배정분), s16 맨홀 무늬 없는 원반(역할-재질 접힘 — kit 재질 분리 항 잔여),
s09 관목 마젠타(프로토타입 봉인 — ⑨에 기록). s08 좌판 판열(⑤·commit 6424758)은 본
라운드 렌더 시점과 교차 — 차기 라운드 육안. **Status: OPEN (착지 — 검수 대기)**

## 72. GT-116 — sceneD4 실내 광 예산 정상화: 반사면 알베도·등기구 3부재·궤도 대역·라이트박스 (선신고)

**Authority**: 08-14 사용자 3일 자율 위임(행 69 — drop-off 집중). 근거 = 감사 §2.3
(D4 는 룩 레버 사정거리 밖 — 조명 구조 문제) + 지름길 실측(`shortcut_audit.py` 신설,
260806_w3_allview5 기준 **D4 지면대 암부 100%·심암부 85.2%** — 코퍼스 낙차-휘도 상관의
최대 단일 기여 씬. 목적은 미학이 아니라 **"깊을수록 어둡다" 탈상관**이다).
**Scope**(선신고): ① 천장 알베도 0.20→백색 패널 대역(실측 지하철 천장 = 백색 마감) ·
벽 타일 실효 알베도 0.21(웜베이지)→백색 타일 대역 0.55+ — 코드 자필 진단("완전 흑이면
intensity 가 아니라 벽 알베도/바운스를 의심하라") 집행. ② 등기구 발광판 1장 → 하우징+
디퓨저(+발광면) 3부재 — 광 pool 성립 조건. ③ 궤도 대역: 도상 0.052→0.10~0.20·침목
0.10 내외·레일 웹 녹갈(실측 대역), 터널 개구에 라이닝 링 실루엣 최소 프림 — "아래에
무엇이 있는가" 단서 복원. ④ 라이트박스 순백(>0.8 픽셀 94.96%) → 프레임 깊이+발광값
하향(무문자 컨벤션 유지 — 사인 신설 아님, 기존 요소 톤 정정). ⑤ tactile 낡은 회황토는
**재질로 고정**(마모 틴트) — 조명이 밝아져도 D13 기준("유일하게 올바른 닳은 띠")이
유지되도록. 승강장 연단·낙차 에지·보행면 z 불변.
**GT 판정**: R-3(등기구·라이닝 프림) + R-2(알베도·발광). 검증 = 파일럿 렌더 후
shortcut_audit 재실측(지면대 암부 100%→하락 목표) + 육안(승강장이 폐역이 아니라
운영역으로 읽히는가). regr DARK/FRAME 변동은 선언 귀속.
**§4 착지기록 1차** (2026-08-14 저녁): ①③④⑤ 시공 + 파일럿 렌더. 육안 = 승강장이
폐역에서 운영역(dim)으로 판독 전환(tunnel_vista — 바닥·벽 밴드·기구·벤치 성립).
실측 = 판정컷 h0.3_d5 지면대 암부 100 % 잔존 → **광량 자체 부족 확정**, ②-2 로
패널 12000→28000 상향 반복(`260814_w4_d4iter` 단독 재렌더) 진행.
**§4 착지기록 완결** (2026-08-15): ②-2 렌더 실측 — 판정컷 h0.3_d5 **표시역 클립
(clipLo <0.10) 97.7→27.7 %** · 심암부(선형 <0.02) 100→82 %(잔존분 = 궤도·터널·천장
— 의도 암부). 육안 tunnel_vista: 바닥 결·마모 tactile·녹갈 레일·침목·벤치 판독 성립,
터널 개구는 암부 유지(목표대로). 탈상관 관점: 승강장 지면대가 "낙차 앞 암부" 신호에서
분리됨. 후속 여지(패널 추가 상향·조명 프리셋 축)는 검수 판정 사항으로 이월.
**Status: OPEN (착지 — 검수 대기)**

## 73. GT-117 — MDL v1.10.0: 물리 파라미터 개방(diffuse_roughness·grazing 감쇠·rough_wl 스펙화) (선신고+착지)

**Authority**: 08-14 사용자 3일 자율 위임(행 69). 근거 = RTX 조사(감사 §5.3): 확산 BSDF
순수 램버시안 → 접지각 자기음영 원리 부재(slope 잔여 격차 후보 1순위·미시험) ·
grazing_reflectivity 1.0 하드코딩 → h0.3 지면 하늘광택("젖은 마루") · rough_noise 파장
1.2 m 하드코딩.
**Scope**: `assets/NegObsGround.mdl` v1.9.0→v1.10.0 — `diffuse_roughness_a`(기본 0.0 =
램버시안)·`grazing_reflectivity_a`(기본 1.0) 노출 + BSDF 배선. `scene_common.py` —
스펙 키(diff_rough/grazing/rough_wl) 배선, rough_noise_wavelength_a 스펙화(기본 1.2).
**어느 클래스에도 값을 적지 않음 = 전 코퍼스 픽셀 동일**(v1.5→v1.6 무영향 규약 준용).
값 부여 파일럿(s13 차도 diff_rough 0.3~0.5 후보)은 별도 선신고.
**GT 판정**: R-2 · 기본값 비트동일이라 re-cache 불요. py_compile OK.
**§4 착지기록** (2026-08-14): 개방만 착지(값 0건). 검증 = 차기 라운드 룩 로그
detX=class 표기 + 파일럿에서 A/B. **Status: CLOSED (개방 — 값 부여는 별행)**

## 74. GT-118 — veg/turf 클래스 분할: 대면적 잔디를 지면 MDL 계열로 (선신고)

**Authority**: 08-14 사용자 3일 자율 위임(행 69). 근거 = 감사 §2(systemic:look-layer —
veg 가 3-D 수관과 대면적 잔디를 한 클래스로 묶어 잔디가 OmniPBR 로 가고, s17 은
`TurfSoil` 개명으로 이미 우회한 전례) + s21 파일럿 육안(잔디 여전히 균질 녹면).
**Scope**: ① LOOK_CLASS 신설 `turf`(mdl="ground"·patch 1.0·sat 0.76·tex "grass"·
macro 0.10 @ macro_wl 1.6 [derived — 예초 밴드 대역]·detail False) ② LOOK_ROLE
Grass/GrassB → turf, 키워드 "grass"/"turf"/"lawn" → turf 규칙(veg 앞 순서) — 수관
(CanopyA/B·Leaf·Hedge·Shrub·Reed·Moss)은 veg 잔류 ③ `_CONST_MDL_CLASSES` +turf ·
`_SKIN_CLASSES` +turf(잔디 지면 기복 허용 — 낙차 에지 아님). 텍스처 잔디가 omni
평면 투영에서 MDL 트라이플래너+매크로+패치 회전으로 이동 = **전 잔디면 룩 변화**
(의도 — F8·"녹색 사포" 해소). 위험 기하 불변(R-2).
**GT 판정**: R-2. 파일럿 렌더(s21·s14 — 대면적 잔디 씬) 후 확산 판정.
**Status: OPEN (선신고 — 시공 중)**

## 75. GT-119 — R4 hazard 인접 배치: 낙차선 주변 형상 결함 6건 (선신고)

**Authority**: 08-14 사용자 3일 자율 위임(행 69 — 08-15 사용자 정정: 8/18 화 오전까지).
근거 = 감사 확정 지적 중 touches_hazard_geometry 표시분. **공통 불변 조건**: 낙차
에지 x/y 좌표·보행면 z·hazard/collision box AABB·판정 시점 — 전부 비트 불변을
셀프체크로 증빙. 형상은 에지 "옆·아래·위 덮개"만 접촉한다.
**Scope**(선신고 — 건별):
① **s03 치크-디딤판 개방 슬롯**(크롭 재검증 확정): 치크 내측면을 디딤판 끝단과
   겹치게 확장(폭/반경 — 계단 답면·낙차선 불변). h0.3 정면 판정컷의 관통 검은 홈 해소.
② **s10 순흑 슬롯**(x1380-1500 창 RGB(0,0,0) 16.8%): 사면 지형 슬래브 간 미접합 틈
   — 인접 슬래브 겹침 마진 확보(사면 = 비보행면, 데크·계단 불변). 슬롯 내 부유
   회청 판 정체 규명 포함.
③ **C1 계단 눈 형상**: 단 눈 캡을 라이저 안쪽으로 물리고 코를 둥근 융기선으로 —
   씬 자기 목표("단 에지가 둥근 융기선으로만 암시") 집행. 콘크리트 계단 기하·GT
   낙차 불변, 눈 캡은 시각 요소(collider 여부 확인·기록). 좌우 흰 탭(크롭 확정)
   클립 동반.
④ **D4 tactile 실기하**: 4 mm 평판+노멀맵 → 근경 대역 돌기 실기하(절두구 h 5~6 mm,
   법령 6±1) — h0.3 그레이징 실루엣 복원. 띠 위치·에지 이격 0.30·보행면 z 불변
   (돌기는 상향 돌출만). 프림 예산: 인스턴싱 규율(§4-14) 준수.
⑤ **s08 좌판 통판 분할**: GT-104(s06 데크 판열) 전례 준용 — 원호 좌판을 데크재
   길이(≤4 m 호장) 단위로 분할+판 간 틈. 좌판 상면 z 불변(틈은 하향 홈).
⑥ **s17 배터 빗살**: 낱개 slope 밴드 9장 → 단일 계단형 솔리드(밴드 사이 틈 원리적
   소멸). 램프 보행면·낙차 불변, 사면 외형 동일 낙차 계단형 유지.
**GT 판정**: R-1(각 씬 셀프체크가 hazard/drop 레지스트리 재유도·전후 비트 대조 출력)
+ R-3. regr FRAME/OCCL 변동 선언 귀속. 검증 라운드 260815_w4_r4batch 후속 컷 또는
차기 라운드에서 육안.
**Status: OPEN (선신고 — 시공 중)**

## 76. GT-120 — R3 위치규칙 데칼 파일럿(s16): 앵커 발행 어휘 신설 (선신고)

**Authority**: 08-14 사용자 3일 자율 위임(행 69). GT-107 Authority 원문("…좀 더
자연스럽게 만들던지, 아니면 좀 없애든지")의 **미선택 갈래(자연스럽게)의 opt-in 구현**
— 정온(전역 산포 미발행)은 유지하고, "왜 거기 있는지 한 문장으로 설명되는" 앵커
위치에만 발행하는 새 어휘를 별도 경로로 신설한다. 근거 = 실세계 조사(감사 §5.2):
실물 오염은 규칙적(낙수선·연석 하류·지주 베이스) + 밀도는 ㎡ 단위 소수.
**Scope**: ① ground_kit `build_anchored_stains`(신규, DEC-1 로브 재사용, DECAL_QUIET
독립·기본 미호출 = 전 씬 비트동일) ② **s16 파일럿 3종**: 캐노피 낙수선 밴드(씬이
scene16:339-343 에서 자체 설계했다가 가드에 잃은 그 항목의 복원 — 감사 부수 소견 6),
연석 접합 토사 라인(횡단경사 1/50 하류 = 연석변), 등주 베이스 drip. 재질 = 기존
텍스처 롤 암틴트(s18 재바인딩 전례 — 상수색 리본 금지). 확산(s11 등)은 갤러리
검수 후 별행.
**GT 판정**: R-3(데칼급, proud ≤ 기존 stain 사다리) · 낙차 에지·보행면 불변.
Round: 차기 검증 라운드에 s16 포함. **Status: OPEN (선신고 — 시공 중)**

## 77. GT-121 — 어두운 씬 탈상관 2차: s02 계단실·s15 골목 그늘 광 예산 (선신고)

**Authority**: 08-14 사용자 3일 자율 위임(행 69). 근거 = GT-116(D4) 방법론의 확장 —
감사 실측: s02 계단실 정오 컷 46 % 준암흑(선형 <0.02), s15 그늘면 41~47 % <0.05
(narrow_up/bend_landing). "깊을수록 어둡다" 탈상관 축(지하도·골목 그늘 = 낙차 인접
암부가 GT 와 상관될 위험) — 미학이 아니라 연구 타당성.
**Scope**: 실효 알베도 실측 → 실물 마감 대역 복귀(D4 전례: 벽 타일·스투코의 텍스처
×틴트 곱을 계산해 근인 특정 후 틴트 보정). 조명 파라미터(태양·돔 강도)는 씬 공통
광학이라 불변 — 반사면 알베도만. 보행면·낙차 에지·기하 불변(R-2).
**GT 판정**: R-2. regr DARK 변동 선언 귀속. 검증 = shortcut_audit 암부 비율 전후.
**Status: OPEN (선신고 — 시공 중)**

## 78. GT-122 — build_building 창 리빌 프레임(근경 티어): 개구 표현 = 후퇴가 아니라 프레임 (선신고)

**Authority**: 08-14 사용자 3일 자율 위임(행 69) + 08-14 건물 총평 룰링("벽면 위주 —
입면 표면·연결 흐름 우선")의 킷 공통 최소 이행분. 근거 = 감사 systemic:building-facade:
셸 솔리드 구조상 창 후퇴 상한 15 mm → 그림자선 불가, 최소 처방 = **창당 4부재 리빌
프레임**(문설주 2·인방 1·창대 1, 벽면 밖 돌출 0.03) — 유리 좌표 불변이라 차폐 % 영향
최소, 근경 티어(lod_dist ≤ 30 m)에만 발행(LOD 규율).
**Scope**: `scene_common.build_building` 창 루프 — LOOK_GEO 게이트 내 프레임 4박스/창.
프림 +4×창수(근경 동 한정). 재질 = parapet_mtl(셸 트림 계열). N1~N4·s11·s16 등
build_building 사용 씬 전체 발현(LOOK_GEO 팔 한정 — OFF 팔 비트동일).
**GT 판정**: R-3(프림 추가) · 유리·벽·보행면 불변. regr FRAME 선언 귀속.
**Status: OPEN (선신고 — 시공 중)**
