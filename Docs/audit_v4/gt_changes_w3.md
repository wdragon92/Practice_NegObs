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
