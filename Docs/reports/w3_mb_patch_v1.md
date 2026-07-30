# MB — patch-vocabulary sweep (GT-24) + the prepared `relaid` vocabulary

> **Wave** W3 · **Lane** MB (micro batch, post-Lane-1) · **Date** 2026-07-31 (wave-day label;
> git author date reads 2026-07-30) · **Branch** `feat/realism-v1`
> **HEAD at work** `e1150d6` (verified live; the brief's `a7842bc` is five docs commits back —
> `d4469c1 · 35b8e39 · 6f5b24c · 4d88923 · e1150d6`, all Markdown, no code)
> **Landed at** `8b6baa7`, whose parent is `5340d49` — a **concurrent lane's** GT-25 scene02
> commit that appeared mid-task (MB-F3). Every A/B arm in this report is cut from `e1150d6`, so
> the isolation is of `ground_kit.py` alone and is unaffected by that commit; `5340d49` touches
> `scenes/main/scene02_underpass.py` only.
> **Owned files, and only these**: `ground_kit.py` · this report · the pilot rounds under
> `look_check/scene{01,16,09,02}/260731_w3_mb24{,_pre}/` (gitignored by policy).
> **Authority**: `gt_changes_w3.md` §3/§4 **GT-24** `OPEN`, declared 07-31 by the micro-docs batch
> (§10 MD-7) + the user's own words *"벽돌 바닥에 패치라니"* (`w3_intake_v2_images.md` §3(ii)).
> **Method**: every number below was produced by re-execution in an **isolated `git archive` arm**
> (the worktree is not trustworthy this session — see §9 **MB-F3**), never by reading another report.

---

## 0. Verdicts

| item | verdict | one-line basis |
|---|---|---|
| (1) three unit-paved `("patch", n)` rows deleted | **LANDED** | `GROUND_PROFILES` `plaza_granite` / `plaza_water` / `sidewalk_block`; A/B removes **14 `Patch_*` prims in 11 scenes and nothing else** |
| (2) semantics recheck (`roof_membrane` · `verge_rural`) | **KEEP both**, dispositions in §4 | the material role actually bound is **concrete** (`Coating`, `conc`) and **asphalt** (`asphalt`) — never soil, never unit paving |
| (3) `relaid` prepared vocabulary | **REGISTERED, count 0** | builder + `SURFACE_KINDS` + `DECAL_Z_ORDER` + 2 ledger dims + dispatch; **0 profile rows, 0 scene opt-ins**, proven by a self-check gate |
| (4) `TACTILE_OFF_REASON["scene18"]` stale entry | **REPLACED** | the wave died at `a443d5a`; the entry now states the reason that is still true |
| §6.1 floor | **PASS** | py_compile · `ground_kit.py` **60/60** · SMOKE 12/12 (scene01 has no SMOKE harness) · geom_invariance **R-4 33/33 · R-6 33/33** · `placement_lint` verdict delta **0** |
| GPU pilots 01 · 16 · 09 (+02) | **PASS / null / null / PASS** | scene01 **PASS 5/5**; 16 and 09 are **pixel-null by construction** — and that null is itself the evidence for **MB-F1** |
| **MB-F1 — GT-24's declared scope is wrong** | **NEW, blocking the ledger record** | 3 of the 15 declared scenes (**18 · 09 · 16**) author their own `surface` row, so the profile-row deletion cannot reach them. **2 of the 3 declared pilots are inert.** |

---

## 1. What the commit changes in `ground_kit.py`

| # | edit | where |
|---|---|---|
| 1a | `plaza_granite` `surface` — `("patch", 1)` **deleted** | was `:1747`, now `:1856` |
| 1b | `plaza_water` `surface` — `("patch", 2)` **deleted** | was `:1755`, now `:1865` |
| 1c | `sidewalk_block` `surface` — `("patch", 2)` **deleted** | was `:1764`, now `:1878` |
| 2 | `_snap_module` docstring — the "five patch-carrying profiles that declare a cell / four snap" sentence was **true before this commit and false after it**; rewritten with the post-GT-24 caller split | `:618` |
| 3a | `SURFACE_KINDS` registry + `plan_ground` raises on an unregistered `surface` row | new, next to `_URBAN_INFRA_KEYS` |
| 3b | `DECAL_Z_ORDER["relaid"] = 6` (R3 ladder, append-only) | `:153` |
| 3c | `GROUND_DIMENSIONS` — `relaid_area_mean` 1.44 `[추정]` · `relaid_albedo` 0.24 `[추정]` | `patch_*` block |
| 3d | `build_relaid_units()` — module-snapped tone-shift rectangle, **1 prim each, no cut line** | after `build_patch_field` |
| 3e | `plan_ground` dispatch branch `elif what == "relaid"` | `_compose_ops` surface loop |
| 3f | 10 new self-check gates (registry · GT-24 rows · prepared-count-0 · builder · 3 guards) | `_selfcheck` [2] and [4] |
| 4 | `TACTILE_OFF_REASON["scene18"]` replaced, with the dead reason quoted in the comment above it | `:2103` block |

**Nothing else.** No scene file, no other kit, no script, no ledger, no other report. The dead
scene-side `sites patch=[…]` lists GT-24 predicted (`scene05` 2 · `sceneN1` 2 — and in fact also
`14 · 20 · 21 · C1 · N3 · C4`) are **kept**, inert at `n = 0`: they live in scene files, which are
outside this lane's pathspec, and deleting them would be a second lane's edit smuggled in.

---

## 2. Scope, re-measured from the tree — and it is not GT-24's scope

GT-24 states 15 in-scope scenes and excludes **only** `scene08`, on the correct principle that a
scene-side `surface` override cannot be reached by a profile-row deletion. The principle is right;
the census behind it is incomplete. Measured live, `grep`-then-read, in every scene that carries one
of the three profiles:

| profile | GT-24 says in scope | authors its own `surface` row | **actually affected** |
|---|---|---|---|
| `plaza_granite` | 01 · 05 · 14 · **18** · 20 · 21 · C1 · N1 · N3 (9) | **18** — `scene18_wavy_artstair.py:1556` `("patch", 3)` | **8** |
| `plaza_water` | **09** (1) | **09** — `scene09_ghat_riverfront.py:895` `("patch", int(g["patch_n"]))` = 5 | **0** |
| `sidewalk_block` | 02 · **16** · **C2** · C4 · N5 (5) *(08 already excluded)* | **16** — `scene16_canopy_shadow.py:719` `("patch", 1)` (the W3 S16 · U-6 edit) · **C2** — `sceneC2_leaf_stairs.py:398` `surface=()` (already empty) | **3** |
| | **15** | | **11** |

**Consequences, stated plainly.**

1. **Two of GT-24's three declared micro pilots are inert.** `16` and `09` were chosen as "one
   scene per profile", but both author their own row, so the commit changes **zero prims and zero
   pixels** in them. Their pilots below are still run — as declared — and they return the null. The
   null is not a formality: it is the direct measurement that proves this finding.
2. **The `plaza_water` leg deletes a row that was already dead.** `scene09` is the profile's only
   carrier and it overrides. The deletion is correct hygiene (a live row would have been the wrong
   object) but it has **no visual effect anywhere in the library**, and no pilot can show one.
   Recorded here rather than presented as a win.
3. **`scene18` is out of scope too** — the same argument the row already makes for `scene08`,
   applied to a scene the row lists. Its hash is unchanged at `cc26fd97` in the A/B (§3).

**Root cause, so the next census does not repeat it (MB-F2).** The declaration's census was read
from `GROUND_PROFILES` + `SCENE_PLANS`. `scene08`'s override is visible there because the
**fixture** carries it (`ground_kit.py:3566`); `scene16` · `scene09` · `scene18` · `sceneC2`
override only in their scene files, and their `SCENE_PLANS` fixtures do **not** mirror the wired
call. The fixture's own v1.4 doctrine is *"Now mirrors the wired call"*. The drift is measurable:
`python3 ground_kit.py`'s 33-scene dry run drops **1170 → 1149 prims (−21)** while the real
scenes drop **−14** — and the 7-prim gap decomposes exactly onto the four drifted fixtures:
**scene18 1 · scene09 2 · scene16 2 · sceneC2 2 = 7**, i.e. every scene whose fixture still
carries the profile's row while the scene itself has overridden it away.
**Not fixed here**: repairing four fixture rows is a
different edit with its own numbers, and GT-24 authorises three tuples. Owed, with the exact rows,
in §10.

---

## 3. Isolated-arm A/B — only the patch rows moved

Arms: `git archive e1150d6` (pre) vs the same archive with **only `ground_kit.py`** replaced
(post); `assets` symlinked into both; inventory taken with the repo's own
`geom_invariance_check.run_arm` (`_DUMP_INV=1`, arm `LOOK_MTL=1 LOOK_GEO=1`), 33 scenes both arms,
0 assembly errors both arms.

**Row census: 31,171 → 31,157 · 14 removed · 0 added · 0 modified.** Every removed row is a
`Cube` at `…/GKit/Patch/Patch_n`. No `xformOp`, reference, path, type or shape row differs
anywhere else in the library.

| scene | profile | prims pre → post | Δ | hash pre → post |
|---|---|---|---|---|
| scene01 | plaza_granite | 354 → **353** | −1 | `6947cb33` → `108cad2f` |
| scene02 | sidewalk_block | 545 → **543** | −2 | `a4c3a5f9` → `f2d645b8` |
| scene05 | plaza_granite | 1235 → **1234** | −1 | `351f44d1` → `3ac9076a` |
| scene14 | plaza_granite | 860 → **859** | −1 | `da26a38b` → `8306d7ba` |
| scene20 | plaza_granite | 481 → **480** | −1 | `05dbc1c9` → `145593c0` |
| scene21 | plaza_granite | 527 → **526** | −1 | `a71d79cc` → `3c0105cb` |
| sceneC1 | plaza_granite | 367 → **366** | −1 | `e821aa7d` → `8bafe396` |
| sceneC4 | sidewalk_block | 638 → **636** | −2 | `f815a3f5` → `93cbff2b` |
| sceneN1 | plaza_granite | 529 → **528** | −1 | `d250bb9a` → `dd9191e2` |
| sceneN3 | plaza_granite | 666 → **665** | −1 | `b8d9a0b6` → `b9cd9d39` |
| sceneN5 | sidewalk_block | 1073 → **1071** | −2 | `885ea29c` → `677c4ffe` |
| **11 scenes** | | **31,171 → 31,157** | **−14** | |
| *scene09 · scene16 · scene18 · sceneC2* | *declared, unaffected* | *501 · 439 · 979 · 3940* | **0** | *`840928aa` · `a9d922f5` · `cc26fd97` · `a6a170a6` — identical* |

**Independent second witness.** `placement_lint --scenes all`'s per-scene inventory, run in the same
two arms, reports `patch=` dropping to zero in exactly those 11 scenes and holding at `patch=1` for
scene16, `patch=5` for scene09, `patch=3` for scene18 and scene08, `patch=4` for scene19 — the
census of §2 re-derived by a tool that knows nothing about this edit.

**Why the removal cannot cascade.** Each builder draws from its own `det_rng("gkit.<kind>", …)`
stream, so dropping the `patch` op cannot re-roll a crack, stain or weed; `_weed_seed_lines` seeds
from joint ticks and manhole/gully frames, never from `sites["patch"]`. The A/B's "0 modified rows"
is the measurement of that claim, not a restatement of it.

---

## 4. Semantics recheck — one line each, with the material role that is actually bound

The role is decided by the **material prim name** through `scene_common`'s `LOOK_RULES`
(`:578` `("asphalt", ("asphalt", "road", "patch"))`), not by the kit's `mtl_key`. So the question
"does this patch read as asphalt?" is answered by what the scene binds, and that was read live.

| profile | row | material actually bound | disposition |
|---|---|---|---|
| **`roof_membrane`** | `("patch", 3)` | scene19 `patch=M["coating"]` → `/World/Looks/Coating` → **concrete** family (W2-F1 added `coating`); `patch_cut=M["gk_stain"]`, and `cutline` is **False** by default (W2-F3), so no saw lip is drawn | **KEEP.** The rectangle reads as a re-coated area — 우레탄 **덧방**, which is the real membrane repair. Vocabulary question handed to 통람, not acted on: `build_patch_field`'s docstring calls its rectangle a *"절삭·덧씌우기"* saw cut, which is asphalt-only prose; on P6 the identical geometry means an overcoat. Rename the *concept in prose*, never the geometry. **Also note the row is unreachable**: scene19, the profile's only consumer, overrides it with `("patch", 4)` (`scene19_fan_winder.py:800`) |
| **`verge_rural`** | `("patch", 3)` | sceneD3 runs the profile **twice**: cover slab `patch=M["conc"]` / `patch_cut=M["dark"]` (`:1040`), roadway `patch=M["asphalt"]` / `patch_cut=M["paint"]` (`:1047`) | **KEEP.** The drawn look is a **concrete repair on the 복개 슬래브** and an **asphalt cut patch on the carriageway** — neither is soil. The batch's "bare-soil worn patch" reading is not what the code draws; if soil scour is wanted it is `stain`/`wear_lane`, a different builder. And `unit_cell["verge_rural"] = None` → no module → no snap, so this is *by construction* a non-unit surface, exactly where a cut patch belongs |
| `street_asphalt` (3) · `ramp_road` (2) · `ramp_parking` (2) · `alley_concrete` (2) · `levee_paved` (4) | kept, per the batch | — | **KEEP**, untouched |

**One tension recorded and deliberately not acted on.** `levee_paved` is **인터로킹 200×100** —
unit paving — and after this commit it is the *only* surviving patch caller that module-snaps
(`_snap_module`, cell 0.200). GT-24's own argument ("on unit paving the real repair is a replaced
unit") applies to it verbatim. It is outside the three profiles the row authorises, so it stays,
and it is listed in §10 as the natural first customer of `relaid`.

---

## 5. The prepared `relaid` vocabulary

`build_relaid_units(kit, path, region, z, mtls, n=0, …)` — a rectangle of paving whose units were
**lifted and re-bedded**: same module, same joint pattern, different tone.

* **`module` is required.** Without a paver module a "re-laid unit" is meaningless, so the builder
  **raises** rather than degrading into a floating lozenge. That guard is what stops the new
  vocabulary drifting back into the asphalt one it replaces. `MODULE_SNAP_MAX_CELL` applies, so
  `alley_concrete`'s 3.0 m 시공줄눈 bay is rejected too.
* **`_snap_module` (DEC-3)** quantises size *and* position to whole/half flags — the group's
  boundary **is** a joint line. Self-check measures it: 1.200×1.200 · 1.200×1.500 · 1.500×0.900 on
  a 0.600 module, all multiples of the half-flag 0.300, low edges on module lines.
* **No cut line.** The four 20 mm perimeter strokes of `build_patch_field` are a saw lip; there is
  no saw here. The read is carried by material tone (T1), which is the fix W2-F3 already made for
  the "drawn dark outline frame" defect (`tonglam_v2.md` §2.13-2).
* **Relief 1.8 mm** = `decal_proud("relaid")`, rank 6 on the R3 ladder — below the patch's 2.0 mm
  절삭 lip, an order under `GT_DELTA`. The ladder is **append-only** (every existing family's z is
  baked into 33 committed hashes), and rank 6 is also the physically honest place: re-bedded units
  are the newest intervention and sit fractionally proud of the settled field. Ladder span and max
  are unchanged (1.7 mm / 2.3 mm), so the R3 gate reads the same number as before.
* **Prepared only, and gated as such.** No profile row, no scene opt-in, `n=0` default. The
  self-check asserts *"relaid 준비 어휘 — 프로파일 선언 0건"*, which **fails on purpose** the day a
  profile opts in — so the sentence "count 0 everywhere" cannot go stale silently.

**Bonus defect closed while registering it.** Until now an unknown `surface` row name fell through
`plan_ground`'s `if/elif` chain **silently** — a typo, or a scene opting into a vocabulary the kit
does not have, produced zero elements and zero complaint. `SURFACE_KINDS` + a `ValueError` closes
that path. Verified against the tree: all 33 scenes assemble, and the only names in use are
`patch · crack · stain · weed`.

---

## 6. `TACTILE_OFF_REASON["scene18"]`

Old: *"파형 비정형 — 300 그리드 부설 미관행"*. That reason **died with the wave** — `a443d5a`
replaced the mural wave stair with a 해운대형 백사장 진입 계단 on a flat granite promenade (GT-26),
so "irregular wave-form" describes nothing in the scene, while the string is what the **B11
diagnostic prints** when a scene tries to place tactile paving without a registry entry.

New entry states the reason that is still true, sourced to `w3_s18_v1.md` §9 and
`scene18_wavy_artstair.py:1319`: G18's landward strip is **선형(유도)** while the library's only
tactile texture is **점형(warning)**, so registering a kit site would paint 120 m of statutory
warning surface where none belongs; the strip is therefore built scene-side at the correct 0.300 m
width and kept 12.20 m clear of the drop edge, and the 계단머리 점형 is the `cue_tactile` ablation
toggle's business (`SCENE_CONFIG["cue_tactile"] = False`), not the registry's. The dead sentence is
kept verbatim in the comment above the entry — annotate, never silently rewrite.

**No behaviour changes**: `TACTILE_SITES` has no `scene18` key before or after, `plan_ground(tactile=())`
is untouched, and scene18's hash is `cc26fd97` in both A/B arms.

---

## 7. Verification floor (spec §6.1)

| floor item | result |
|---|---|
| `python3 -m py_compile ground_kit.py` | **OK** |
| `python3 ground_kit.py` (the kit's own gate) | **60/60 OK · 0 FAIL** — "전 항목 통과". Was 50 gates before; the 10 new ones are §5's. 33-scene dry run 33/33 hard gates, apply-round-trip 33/33, unsubstituted material refs 0 |
| `NEGOBS_SMOKE=1 python scenes/<scene>.py` for touched scenes | **12/12 rc=0** — 02 · 05 · 14 · 21 on the CPU path; 20 · C1 · C4 · N1 · N3 · N5 · 16 · 09 under `env_isaaclab`. **scene01 has no SMOKE harness at all** (it boots Isaac unconditionally, `:389`), so the floor item has no subject there and the A/B assembly + the GPU pilot stand in its place. Stated, not skipped |
| `python3 scripts/geom_invariance_check.py` | **R-5 ✔ · R-4 33/33 ✔ PASS · R-6 33/33 ✔ PASS**, run **in the isolated post arm** (see MB-F3), 3-way hash agreement on every scene incl. all 11 changed ones |
| `python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml` | **verdict delta 0.** Pre and post arms give a byte-identical summary table: **ERROR 30 · WARN 337 · BLOCK 29 · INFO 2** (per-check rows identical too). Only the per-scene *inventory* moves, and only by the 14 patches |

---

## 8. GPU pilots

All under `flock -w 7200 /tmp/negobs_gpu.lock`, channel identical to the frozen judge round
(`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 ·
NEGOBS_DETAIL_ROUGH_GAIN=0`), **5 cuts** (`preset_h0.3_d{2,5,10}` + `preset_h0.9_d{2,5}` — CB-2's
GATE-1 cut set, a subset of every baseline used), `scripts/stamp_round.py` on each.

Two rounds were rendered, because one was not enough to attribute anything:

* **`260731_w3_mb24`** — this commit's tree.
* **`260731_w3_mb24_pre`** — the *attribution* arm: `ground_kit.py` reverted to `e1150d6` and
  nothing else, re-rendered in the same session (CB-7 `_pre` precedent). Without it, the pilots
  would be comparing across K4(b)'s species pinning, K5, K1 and CB-7 as well as this edit.

### 8.1 Attribution arm — `mb24_pre → mb24` (this commit and nothing else)

| scene | leg | verdict | DARK / BLOWN / WHITE / OCCL | notes |
|---|---|---|---|---|
| **scene01** | plaza_granite, −1 patch | **PASS 5/5** | all clean · new-dark **0.00 %** · blob **0.00 %** · block-shift **0** on 4 cuts, 1 on `h0.3_d5` | **no FRAME finding at all** — the declared FRAME never fired, because a single 0.6×0.6 m dressing element is below the block-occupancy threshold |
| **scene16** | sidewalk_block | **PASS 4 · WARN 1** | clean | the WARN is `UNCHANGED` on `h0.3_d2` (0.10 LSB mean, 0.005 % of pixels) — **the null**, exactly as §2 predicts |
| **scene09** | plaza_water | **PASS 1 · WARN 4** | clean | four `UNCHANGED` WARNs (0.06–0.38 LSB) — **the null** |
| **scene02** | sidewalk_block, −2 patches | **INFO 4 · WARN 1** | DARK/BLOWN/OCCL clean, new-dark 0.00 % | one **GRAZE `[의심]`** on `h0.3_d2`, adjudicated below |

**The scene02 GRAZE, adjudicated (the tool declares it cannot be auto-confirmed).** Two
independent grounds, then a crop.

1. **Geometry**: `preset_h0.3_d2`'s eye is `(-2.0, gy, 0.3)` looking **+X** (`scene_common.grid_views`).
   The two removed prims sit at `x = -7.2` and `x = -9.3` — **5.2 m and 7.3 m behind the camera**.
   They cannot be in that frame, so they cannot have drawn a line in it.
2. **Metric triangulation**: the edge-band step is `13.05` in the CB-7 baseline-of-record, `12.84`
   in `mb24` — and `3.41` in `mb24_pre`. Against CB-7, `mb24` moves **0.29 % of pixels** while
   `mb24_pre` moves **3.99 %**. The arm that deviates is the **pre** arm, i.e. the finding is PT
   sampling variance on that one capture, not a change introduced by this commit.
3. **Crop** (`look_check/scene02/260731_w3_mb24/crops/graze_edge_preset_h0.3_d2.png`, rows 339–624
   = the tool's own `gz_band`, three rounds stacked): the paving, the joint lines and the drop-edge
   coping are visually identical in CB-7, pre and post. **No new or thickened transverse line.**
   Adjudicated **NEGATIVE**.

### 8.2 Against the baselines-of-record (§6-W4)

| scene | baseline named | result on the 5 shared cuts |
|---|---|---|
| scene01 | `260731_w3_cb2` (CB-2 GATE-1 pilot set is 03 · 07 · C2 · **01**) | **PASS 5/5** · FAIL 0 · WARN 0 |
| scene16 | `260731_w3_s16` (`baseline_of_record: true`) | **PASS 5/5** |
| scene09 | `260731_w3_cb1` | PASS 3 · INFO 1 (`CAPTURE`) · WARN 1 (`UNCHANGED`) |
| scene02 | `260731_w3_cb7` | PASS 1 · INFO 2 (`CAPTURE`) · WARN 2 (`UNCHANGED`) |

The 8–12 `MISSING` FAILs each run prints are the arithmetic of a **5-cut round against a 13/17-cut
baseline**, not findings; they are excluded above and named here so nobody reads them as regressions.

### 8.3 The picture the user asked for

`look_check/scene01/260731_w3_mb24/crops/patch_removed_preset_h0.3_d5.png` — the same cut before
and after. On the left, a smooth grey rectangle with a hard straight edge butts into the 판석
paving beside the planter: the *"이상한 사각형 무늬"*. On the right it is gone and the flag
pattern runs continuous. That is the whole point of GT-24, in one 0.6 × 0.6 m element.

### 8.4 Why scene02 was added as a fourth pilot

GT-24 gates on "one scene per profile", but §2 shows the `sidewalk_block` pilot it names (16) is
inert and the `plaza_water` leg has **no** affected scene in the library. scene02 is the
sidewalk_block scene that actually loses patches, and it is the profile's only judged scene with a
fresh baseline-of-record (CB-7, `dc68e74`). Rendering it is the only way the sidewalk_block leg
gets pixel evidence at all. Declared as an addition to the declared gate, not a substitution:
01 · 16 · 09 were all run as the row asks.

---

## 9. Findings

| # | sev | finding | owner |
|---|---|---|---|
| **MB-F1** | **HIGH** | **GT-24's in-scope set is 15 but the reachable set is 11.** `scene18` · `scene09` · `scene16` author their own `surface` row; `sceneC2` clears `surface` entirely. Two of the three declared pilots (16 · 09) are pixel-null, and the whole `plaza_water` leg deletes an already-dead row. The §4 landing record **must not** be written with the 15-scene figure | supervisor (row amendment) |
| **MB-F2** | MED | **`SCENE_PLANS` fixture drift is what produced MB-F1.** The fixtures for `scene16` · `scene09` · `scene18` do not mirror the wired call's `overrides=dict(surface=…)`, so a census taken from `ground_kit.py` alone cannot see the overrides. Measured: the fixture dry run moves −21 prims where the real scenes move −14 | Lane-1 / `ground_kit` owner (see §10) |
| **MB-F3** | **HIGH** | **Another lane is writing this worktree right now.** The tree was clean at `e1150d6` when this task started; during it, `scenes/main/scene02_underpass.py` (GT-25 planter move, citing an unseen `w3_md_reverts_v1.md`) and `scripts/regression_check.py` (D14 `EXPECTED_FP` reader, md5 changed **twice** mid-session: `5dce6da…` → `2d0bfe1…`) appeared as uncommitted modifications, plus an untracked **self-referential symlink `assets/assets → …/assets`** that will make any recursive walk of `assets/` loop. The brief said no other lane was running. Consequences are contained but must be known: every structural number in this report comes from isolated `git archive` arms and is unaffected; the **GPU pilots and the regression verdicts were produced against that dirty worktree**, with `scene02_underpass.py` byte-identical (`e4095102…`) across both render arms so the pre→post attribution holds | supervisor / lane dispatch |
| **MB-F4** | LOW | `levee_paved` (인터로킹 200×100) keeps `("patch", 4)` and is now the only module-snapping patch caller. GT-24's vocabulary argument applies to it verbatim; it is outside the three authorised profiles, so it was not touched | next patch-vocabulary round |
| **MB-F5** | INFO | Two profile `patch` rows are **unreachable dead code**: `plaza_water` (only carrier scene09 overrides — deleted by this commit) and `roof_membrane` `("patch", 3)` (only carrier scene19 overrides with 4 — kept, per §4) | record |

---

## 10. Owed, and to whom

| owed | owner | why |
|---|---|---|
| **Amend GT-24's §3 scope cell**: in-scope 15 → **11**, and add `scene18` · `scene09` · `scene16` to the same exclusion sentence that already carries `scene08`; note that the `plaza_water` leg is a dead-row deletion | supervisor | MB-F1 — the row's own principle, applied to the full census |
| **Amend GT-24's gate**: pilots `01 · 16 · 09` → `01 · 02` (+ keep 16 · 09 as the recorded nulls). A gate whose two of three scenes cannot move is not a gate | supervisor | MB-F1 |
| `SCENE_PLANS` fixture rows for **scene16** (`surface=(("patch",1),("crack",4),("stain",("dirt","gum","drip")),("weed",8))` + `infra` + `wear_lane`), **scene09** (`surface=(("patch",5),("crack",4),("stain",("water",)))`, `extras=()`), **scene18** (`surface=(("patch",3),…)`) and **sceneC2** (`surface=()`, `extras=()`, `scatter=None`) — to mirror the wired calls. Changes the dry-run prim total; declare the new number | Lane-1 / `ground_kit` owner | MB-F2 |
| Dead `sites patch=[…]` lists in `scene05 · 14 · 20 · 21 · C1 · N1 · N3 · C4` (scene files) | the scene owners | inert at `n = 0`; kept deliberately (§1) |
| `levee_paved` patch-vs-relaid decision | next round | MB-F4 |
| First `relaid` customer, if any — needs a profile row **and** a `relaid` material key bound scene-side | future | §5 |
| Resolve the concurrent-lane collision and the `assets/assets` symlink | supervisor | MB-F3 |

---

## 11. GT-24 landing-record text, **prepared** for the supervisor

> Not written to `gt_changes_w3.md` by this lane. §0-3 governs: the supervisor fills §4 from this
> report. The row's §4 cell names five things it must carry; all five are below, with the scope
> figure **corrected** rather than transcribed.

**§4 GT-24 — landing record (prepared):**

> **Owner** MB (micro batch) · **CB id** — (no CB gate; micro pilots) · **Commit** `8b6baa7`
> (`ground_kit.py` + `Docs/reports/w3_mb_patch_v1.md`, pathspec).
> **The three `GROUND_PROFILES` tuple edits**: `plaza_granite` ~~`("patch", 1)`~~ → row deleted ·
> `plaza_water` ~~`("patch", 2)`~~ → row deleted · `sidewalk_block` ~~`("patch", 2)`~~ → row
> deleted.
> **`python3 ground_kit.py`** → **60/60 gates OK, 0 FAIL** ("전 항목 통과"), incl. the new
> *"GT-24 단위포장 3종 patch 행 0"* gate; 33-scene dry run 33/33 hard gates, apply round-trip
> 33/33, kit-plan prim total **1170 → 1149**.
> **Per-scene element and prim delta — the scope is 11 scenes, not the 15 §3 declares.**
> `scene18` (`:1556`), `scene09` (`:895`) and `scene16` (`:719`) author their own `surface` row and
> `sceneC2` clears it, so the profile-row deletion cannot reach them — the same exclusion the row
> already states for `scene08` (`w3_mb_patch_v1.md` §2, **MB-F1**). Affected, one removed `patch`
> element = one removed prim each: **scene01 354→353 · scene05 1235→1234 · scene14 860→859 ·
> scene20 481→480 · scene21 527→526 · sceneC1 367→366 · sceneN1 529→528 · sceneN3 666→665**
> (−1 each) · **scene02 545→543 · sceneC4 638→636 · sceneN5 1073→1071** (−2 each). Library total
> **31,171 → 31,157 prims (−14)**; isolated-arm A/B over all 33 scenes: **14 rows removed, 0 added,
> 0 modified**, every removed row a `Cube` at `…/GKit/Patch/Patch_n`. Unchanged and verified so:
> scene09 `840928aa` · scene16 `a9d922f5` · scene18 `cc26fd97` · sceneC2 `a6a170a6`.
> **`placement_lint` verdict delta = 0** (`--scenes all --rules placement_rules_v1.yaml`, both
> arms: ERROR 30 · WARN 337 · BLOCK 29 · INFO 2, per-check rows identical); only the per-scene
> inventory moves, `patch=` → absent in exactly those 11 scenes.
> **Floor**: `py_compile` OK · SMOKE 12/12 rc=0 (scene01 has no SMOKE harness — its assembly is
> covered by the A/B arm and its GPU pilot) · `geom_invariance_check` **R-5 ✔ · R-4 33/33 ·
> R-6 33/33 PASS**.
> **R-3 rounds, named per §6-W4** — new round `260731_w3_mb24` (5 cuts, PT_FAST, judge channel) in
> each case: **scene01** vs baseline-of-record **`260731_w3_cb2`** → **PASS 5/5** · **scene16** vs
> **`260731_w3_s16`** → PASS 5/5 (**pixel-null by construction**) · **scene09** vs
> **`260731_w3_cb1`** → PASS 3 / INFO 1 / WARN 1 `UNCHANGED` (**pixel-null by construction**) ·
> **scene02** (added, the only judged scene the `sidewalk_block` leg actually moves) vs
> **`260731_w3_cb7`** → PASS 1 / INFO 2 / WARN 2 `UNCHANGED`. Attribution arm
> **`260731_w3_mb24_pre`** (this commit reverted, same session) → `mb24`: scene01 **PASS 5/5,
> new-dark 0.00 %**, DARK/BLOWN/WHITE/OCCL clean, **no FRAME finding fired**; scene02 one
> **GRAZE `[의심]`** adjudicated **NEGATIVE** by crop + geometry (both removed prims are 5.2 m and
> 7.3 m *behind* the `h0.3_d2` eye) + metric triangulation (the deviating arm is `mb24_pre`, at
> 3.99 % changed pixels vs CB-7 against `mb24`'s 0.29 %).
> **Also landed in the same commit, and needing their own reading**: the prepared `relaid`
> vocabulary (registered, **count 0 everywhere**, guarded by a self-check that fails if a profile
> opts in) and the `TACTILE_OFF_REASON["scene18"]` stale-entry replacement (S18 lane blocker 3).
> **Status** → `LANDED` once the §3 scope cell is amended per MB-F1; the record above is written
> against the measured scope, so landing it unamended would leave §3 and §4 contradicting each
> other — the exact failure MD-3 was written against.

---

## 12. Reproduction

```bash
# isolated arms (never the worktree — MB-F3)
git archive e1150d6 | tar -x -C <arm_pre>  ; rm -rf <arm_pre>/assets  ; ln -s <repo>/assets <arm_pre>/assets
git archive e1150d6 | tar -x -C <arm_post> ; cp <repo>/ground_kit.py <arm_post>/ ; ln -s ... (same)
# inventory A/B: geom_invariance_check.run_arm(dump=True) on each arm, field-level Counter diff
python3 ground_kit.py                                   # 60/60, 0 FAIL
python3 scripts/geom_invariance_check.py                # R-5 · R-4 33/33 · R-6 33/33   (in <arm_post>)
python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml   # both arms
NEGOBS_SMOKE=1 python scenes/main/scene16_canopy_shadow.py     # + 11 more, env_isaaclab for 8 of them
# pilots (both rounds; _pre = ground_kit.py reverted, nothing else)
flock -w 7200 /tmp/negobs_gpu.lock <round script>       # NEGOBS_VIEWS=preset_h0.3_d{2,5,10},preset_h0.9_d{2,5}
python3 scripts/stamp_round.py look_check/<scene>/260731_w3_mb24 260731_w3_mb24 <scene>
python3 scripts/regression_check.py --before look_check/scene01/260731_w3_cb2 \
        --after look_check/scene01/260731_w3_mb24 --json look_check/scene01/260731_w3_mb24/regr_vs_260731_w3_cb2.json
python3 scripts/regression_check.py --before look_check/scene02/260731_w3_mb24_pre \
        --after look_check/scene02/260731_w3_mb24 --json look_check/scene02/260731_w3_mb24/regr_attrib.json
```

Regression JSONs are written **into the round directories** (a stated path, gitignored), not into
`Docs/reports/regr_*.json`, which is outside this lane's pathspec.

## 13. Sources

* `Docs/audit_v4/gt_changes_w3.md` — §3/§4 **GT-24** (the declaration this lane implements) · §10
  MD-7 / 10-1 / 10-2 · §0-1 append-before-land · §0-3 empty-record law · §6-W4 baseline rule
* `Docs/reports/w3_micro_docs_v1.md` §1.6 — the census this report corrects, and the reasoning it used
* `Docs/surveys/w3_intake_v2_images.md` §3(ii) — the user's *"이상한 사각형 무늬"* and the count table
  GT-24 diverges from
* `Docs/reports/redteam_lane1.md` §7 (floor at HEAD) · §8 RT-1..4 · §9 open items
* `Docs/reports/w3_s18_v1.md` §9 + `§9 supervisor adjudication` — the `TACTILE_OFF_REASON` blocker
* `Docs/reports/w3_ledger_batch_v1.md` · `w3_k4_v1.md` · `w3_k5_v1.md` · `w3_k1t4_v1.md` ·
  `w3_s10_close_v1.md` · `w3_cb7_v1.md` · `w3_n2_clean_v1.md` §7 — read for the window's state
* Live tree, this session: `ground_kit.py` · `scene_common.py:578` (`LOOK_RULES`) ·
  `scene09:884-901` · `scene16:706-727` · `scene18:1549-1566` · `scene19:795-816` ·
  `sceneC2:380-399` · `sceneD3:373-400,1033-1050` · `grid_views:3900`
</content>
</invoke>
