# MD micro-batch — FU-1 revert (measured, **not landed**) · GT-25 scene02 planter · F5 stamps · planter census

> **Wave** W3 · **Lane** MD (post-Lane-1 corrections) · **Date** 2026-07-31
> **Branch** `feat/realism-v1` · **HEAD at start** `e1150d6` (verified live; the brief's
> `a7842bc` is four docs-only commits back) · **landed here** `5340d49` (scene02) + this report
> **Owned files** `scenes/main/scene02_underpass.py` · `scenes/main/scene07_temple_stone_path.py`
> · `scenes/main/scene10_park_deck_switchback.py` · the `260731_w3_s04` / `260731_w3_s16` round
> stamps · this report. `Docs/audit_v4/gt_changes_w3.md` was **not** touched (§0-3 — the
> supervisor fills landing records); §3.4 below is the *prepared* text, not a ledger edit.
> **Method** every number is re-executed, never re-read. All assembly proofs and all six GPU
> arms run in **isolated `git archive` trees** with only `assets` symlinked, because another
> lane was writing `ground_kit.py`, `scripts/regression_check.py` and
> `Docs/reports/w3_mc_d14_v1.md` into the worktree throughout this task (§7 **MD-F1**). GPU work
> exclusively under `flock -w 7200 /tmp/negobs_gpu.lock`, `PT_FAST`, judged arm. No humans, no
> vehicles.

## 0. Verdicts

| item | verdict | one-line basis |
|---|---|---|
| **FU-1** scene07 | **NOT LANDED — revert refused on measurement** | the rebind is **art direction**, not an MDL workaround: dropping it moves `side_slope` by **+1.75 LSB** mean against a **0.04 LSB** noise floor, and 3.3 % of pixels by > 16 LSB |
| **FU-1** scene10 | **NOT LANDED — revert refused on measurement** | the rebind masks a **second, different** defect: `rock_moss_set_01`'s MaterialX `ND_normalmap_float` is absent from the Sdr registry, so under instancing red-fallback returns **0.02 % → 4.50 %** |
| **FU-1** mechanism | **CONFIRMED working** | both reverted arms compose the instances they were supposed to: scene07 `IsInstance` **0/30 → 30/30** (prototypes 22 → 25), scene10 **0/4 → 4/4** (20 → 23), `C120` **0** in every arm |
| **GT-25** scene02 | **LANDED** `5340d49` (coordinate deviation declared) | R-3 vs `260731_w3_cb7`: **FAIL 1 · WARN 0 · PASS 12**, the one FAIL being `beauty_overview` PHOTO **87.5 → 146.2 (+58.7)**, recovering C02-P1's −57.5 in full; OCCL **0.0 %** new-dark on all 13 |
| **GT-25** coordinate | **DEVIATION, declared** | the row's `(−11.0, −6.2)` drives the bed through the hedge band (**Hedge_0 2.350 × 0.683 × 1.060 m**); landed at `(−11.0, −5.0)` instead, eye distance 4.000 m vs 4.176 m |
| **F5** | **CLOSED** for both stamps | `260731_w3_s04` and `260731_w3_s16` now carry `baseline_of_record` + `supersedes` + `comparison_baseline_used` + the S10c `dirty_paths` convention. Nothing re-rendered |
| **Census** | **DONE — 10 scenes, 16 beds, 44 judged-eye pairs** | scene02 was **not** unique: **scene08 `beauty_overview` sits inside a planter footprint with a live `Fraxinus.usd` in it**, and scene20 `oblique_overview` is 0.45 m off one with an `Elm_Sapling` |

---

## 1. FU-1 — the scene07 / scene10 MDL workaround revert

### 1.1 What was built, and why it is a fair test of the brief

`w3_k1t4_v1.md` §3 **FU-1** asks for the two in-lane workarounds to be reverted now that
`urban_kit.ensure_mdl_package()` repairs the MDL chain at load time, and predicts that *"the
revert buys back prototype sharing … not appearance"*. The reverted arm implements exactly that
reading:

* `add_urban_asset(..., instanceable=False)` → **`instanceable=True`** (both scenes);
* the scene-side material rebind **dropped** — scene07's ancestor
  `strongerThanDescendants` bind on `/Kerb_*`, scene10's per-mesh `Bind(M["rockface"])` loop
  under `/Outcrop_*/Asset` — so the asset's own, now-repaired, material binds by default.

Applied to an isolated arm (`scratchpad/fu1_revert.py`), never to the worktree. The composed
inventories say the edit is surgical and nothing else moved:

| scene | prims (both arms) | hash HEAD → reverted | rows differing | what differs |
|---|---|---|---|---|
| scene07 | **1420** | `f13fbc03` → `4a8d7b33` | **30** | only `…/Kerb_*/Asset … instanceable=True` |
| scene10 | **2777** | `f8e2670e` → `efac664a` | **4** | only `…/Outcrop_*/Asset … instanceable=True` |

Zero rows differ in path, type, xformOp or shape attribute. `NEGOBS_SMOKE=1` output is
**byte-identical** between the arms for both scenes (`diff` clean), `placement_lint` totals are
identical (ERROR 0 · WARN 14 · BLOCK 2 for the pair), and `geom_invariance` R-4/R-6 pass 2/2 in
each arm.

**The mechanism the revert exists for does work.** Wrapped at the moment the stage is composed
(`scratchpad/probe_wrap.py` — the scene is not edited, `sc.capture_pipeline` is):

| scene | arm | `/…/Asset` prims | `IsInstance()` | stage prototypes | `C120` in log |
|---|---|---|---|---|---|
| scene07 | workaround | 30 | **0** | 22 | 0 |
| scene07 | reverted | 30 | **30** | **25** | 0 |
| scene10 | workaround | 4 | **0** | 20 | 0 |
| scene10 | reverted | 4 | **4** | **23** | 0 |

`C120 could not find module '.::baking_annotations'` — the defect T4 fixed — appears **0 times in
all four arms**. `ensure_mdl_package()` is live and doing its job. That is precisely why the
revert's failure below is *not* an MDL story.

### 1.2 The noise floor first, so the A/B means something

Before comparing arms, the same arm was rendered twice (`s07_wa` vs `s07_wa2`, `s10_wa` vs
`s10_wa2`, same 3 cuts, same lock, same `PT_FAST`):

| scene | worst per-cut \|Δmean\| | pixels > 16 LSB |
|---|---|---|
| scene07 | **0.198 LSB** (`preset_h0.3_d2`; `side_slope` 0.04, `temple_walk` 0.01) | 0.1 – 0.6 % |
| scene10 | **0.003 LSB** | **0.0 %** |

Anything at or under ~0.2 LSB on scene07 and ~0.01 LSB on scene10 is PT noise. Everything below
is measured against that.

### 1.3 scene07 — the rebind is **art direction**, not an MDL workaround

| cut | mean, workaround | mean, reverted | Δmean | > 1 | > 4 | > 16 | max | red-fallback WA → REV |
|---|---|---|---|---|---|---|---|---|
| `preset_h0.3_d2` | 124.21 / 114.58 / 90.51 | 124.33 / 114.79 / 90.88 | +0.11 / +0.21 / **+0.37** | 43.9 % | 17.5 % | **2.2 %** | 179 | 0.00 % → 0.00 % |
| `side_slope` | 99.04 / 95.12 / 83.58 | 99.70 / 96.08 / 85.32 | +0.66 / +0.97 / **+1.75** | 21.6 % | 4.9 % | **3.3 %** | 205 | 0.00 % → 0.00 % |
| `temple_walk` | 72.36 / 67.77 / 55.13 | 72.34 / 67.77 / 55.17 | −0.01 / +0.01 / +0.04 | 8.9 % | 1.3 % | 0.1 % | 127 | 0.00 % → 0.00 % |

**Red-fallback is 0.00 % on both arms and all three cuts** — the MDL repair holds and the
boulders render their own scan albedo correctly. The brief's gate (*"means within ~1 LSB"*) is
nevertheless **failed on `side_slope`: +1.75 LSB, 44× that cut's 0.04 LSB noise floor**, with
3.3 % of the frame moving by more than 16 LSB against a 0.1 % noise share. `preset_h0.3_d2` is
+0.37 against 0.06 noise, 2.2 % vs 0.6 %. Only `temple_walk` — where the kerb boulders are
barely in frame — is genuinely null.

The cause is not a bug, it is the scene's own design. `scene07:2145` labels the block *"two
things are happening here and **both** are load-bearing"*, and (a) is the **moss zone**: §4.1-3
puts 0.70–0.90 moss on boulder tops, so a drawn subset takes `M["stone_moss"]` and the rest a
`M["stone_mid"]` tier — with the pilot's own measured reason for using tinted stone rather than
the raw scan (`rock_moss_set_02` world-projects into a "wet-plastic sheet" on a rounded 0.4–0.9 m
boulder). FU-1 reads that bind as part of the MDL workaround. It is not. **Only
`instanceable=False` is the workaround, and it is *entailed* by the bind** — an ancestor
`strongerThanDescendants` opinion cannot reach into a prototype, which is exactly what the code
comment says and what the 0/30 → 30/30 probe confirms.

So the revert is not appearance-neutral, it is **the deletion of a look decision**, and landing
it would silently move a judged scene's baseline-of-record (`260731_w3_s07`) without a round.
**Not landed.** `scenes/main/scene07_temple_stone_path.py` is unmodified at `5340d49`.

### 1.4 scene10 — the rebind masks a **second, unrelated** asset defect

| cut | mean, workaround | mean, reverted | Δmean | > 16 | **red-fallback WA → REV** |
|---|---|---|---|---|---|
| `from_below` | 145.29 / 136.20 / 105.14 | 146.12 / 136.05 / 105.04 | **+0.82** / −0.15 / −0.10 | 0.9 % | 0.00 % → **0.53 %** |
| `preset_h1.8_d10` | 143.82 / 132.87 / 96.83 | 145.04 / 132.47 / 96.55 | **+1.22** / −0.40 / −0.28 | 1.4 % | 0.03 % → **0.97 %** |
| `preset_h1.8_d5` | 136.44 / 128.16 / 101.80 | 140.68 / 125.89 / 100.23 | **+4.24** / −2.27 / −1.57 | **5.0 %** | 0.02 % → **4.50 %** |

Against a **0.003 LSB** noise floor, every one of these is signal, and the signature is
unmistakable: the mean moves **up in red and down in green and blue**, and the k1t4 red-fallback
metric (`R > 90 ∧ R > 1.8 G ∧ R > 1.8 B`) goes from nothing to **4.50 % of the frame**. That is
the shader-error fallback returning.

The render log names it, and it is **not** MDL:

```
[Error] [omni.hydra] [Network::CreateUpdatedNetwork()]: cannot find SdrNode:
  'ND_normalmap_float' for node:
  '/__Prototype_21/_materials/rock_moss_set_01/NodeGraphs__NESTED__Normal_Map'
  in material: '/__Prototype_21/_materials/rock_moss_set_01'
```

`rock_moss_set_01_1k.usdc` — the largest outcrop, `scale_mul 1.00` at (6.30, 4.15) — ships a
**MaterialX** material whose normal-map node is not in this runtime's Sdr registry. 0 `C120`, 0
missing MDL modules: `ensure_mdl_package()` completes the `.mdl` package and cannot touch a
MaterialX node definition. The scene's per-mesh `Bind(M["rockface"])` replaces that material
outright, which is why the workaround arm is clean — the code comment's claim (*"material
override is mandatory here, not cosmetic"*) is **still true**, just for a different reason than
the one it gives.

**Not landed.** `scenes/main/scene10_park_deck_switchback.py` is unmodified at `5340d49`.

### 1.5 What would actually satisfy FU-1 — handed on, not attempted

Both scenes want the same thing: *a bound-material variant that composes **inside** the
prototype*. The library already has the pattern — K4(0) `e4fc4cf` generalised it as
`sc.veg_wrapper_rel`, where an additive wrapper layer carries the opinion above the instance
boundary so the prototype is composed with it. The urban equivalent is a
`urban_kit.asset_wrapper_rel(asset_id, mtl_key)` that writes an `over` binding into a per-
(asset, material) wrapper `.usda`; 30 scene07 boulders collapse to ~2 tiers × 3 assets = **6
prototypes**, and scene10's four outcrops to three, with the tint and the `rockface` override
intact. `urban_kit.py` is **not this task's file**, so this is written down, not built — see §7
**MD-F2**.

---

## 2. What FU-1 did **not** change

No file under `scenes/main/scene07*` or `scenes/main/scene10*` is modified by this batch, and
neither scene's baseline-of-record round (`260731_w3_s07`, `260731_w3_s10c`) is touched or
re-stamped. The six probe renders live in scratch, not in `look_check/scene07` or
`look_check/scene10`, so no round directory can be mistaken for a judgement round.

---

## 3. GT-25 — scene02 `planters[0]`, landed with a declared coordinate deviation

### 3.1 The declared coordinate collides with the hedge — measured, not argued

`Docs/audit_v4/gt_changes_w3.md` §3 GT-25 declares `PARAMS["planters"][0]` ~~`(-8.0, -5.0)`~~ →
**≈ `(-11.0, -6.2)`**. Four candidate coordinates were assembled in an isolated fake-USD arm and
the `Planter_0` subtree AABB intersected against every other top-level group
(`scratchpad/s02_planter_probe.py`, GPU 0):

| candidate | bed AABB (x, y) | eye→bed edge | eye→centre | interpenetrations beyond the ground plates |
|---|---|---|---|---|
| HEAD `(-8.0, -5.0)` | −9.55 … −6.45 · −6.55 … −3.45 | **0.000 m** | 1.000 m | none |
| **declared `(-11.0, -6.2)`** | −12.55 … −9.45 · **−7.75** … −4.65 | 2.450 m | 4.176 m | **`Hedge_0` 2.350 × 0.683 × 1.060 m · `Hedge_1` 0.885 × 0.660 × 0.898 m** |
| `(-11.0, -5.2)` | −12.62 … −9.44 · −6.82 … −3.64 | 2.440 m | 4.176 m | `Hedge_0` 2.415 × 0.168 · `Hedge_1` 0.895 × 0.218 |
| **landed `(-11.0, -5.0)`** | −12.55 … −9.45 · −6.55 … −3.45 | 2.450 m | **4.000 m** | **none — the same set as HEAD** |

(The four groups every candidate "overlaps" — `Walk_W`, `Grass_W`, `Curb_E`, `Curb_W`, `GKit` —
are the ground plates the bed's buried foot stands in. They are present at HEAD and are not
findings; the table lists only what is new.)

The hedge is not incidental geometry. `scene02:285` defines it at `x -16.0 … 6.8`,
`y = -7.0 ± 0.30` with per-segment `y_var`, and **its own comment records why it is there**:
*"Ends before the road … y -6 → -7 (avoiding the planter)"*. The declared `y = −6.2` puts a
0.45 m granite kerb and a 0.40 m soil box straight through a 1.0 m hedge over 2.35 m of its
length. Keeping `y = −5.0` preserves the clearance the scene engineered and costs **0.176 m** of
eye-to-centre distance (4.000 m instead of the row's re-derived 4.176 m) — on a figure the ledger
row itself rules out as the target: *"the target of this row is the **coordinate**, not that
distance figure"*. Both readings cannot be honoured, so the one that keeps the model sound was
taken and the deviation is declared here and in `scene02:432`'s comment.

**Requested of the supervisor (§3.4):** amend GT-25's coordinate to `(−11.0, −5.0)`, **or** rule
that the hedge may be shortened/notched — which would be a second element AABB move and needs its
own row.

### 3.2 The round

Two 13-cut rounds, both from isolated arms, both under the lock, arm identical to
`260731_w3_cb7`'s own stamp (`pt · PT_FAST · LOOK_V1 · DETAIL_SCALE 2 · DETAIL_ROUGH_GAIN 0`):

* **`260731_w3_gt25_pre`** — arm `e1150d6` exactly, PRE-move. The attribution arm.
* **`260731_w3_gt25`** — the same arm with `scene02_underpass.py` replaced by the landed file
  (verified `diff -q` byte-identical to `5340d49:scenes/main/scene02_underpass.py`).

**Reproduction — the baseline still is what it says it is.**
`regression_check 260731_w3_cb7 → 260731_w3_gt25_pre` = **FAIL 0 · WARN 0 · INFO 1 · PASS 12**,
"회귀 없음"; worst per-cut \|Δmean\| **0.31 LSB** (`beauty_overview` +0.27 / +0.27 / +0.23). The
committed baseline reproduces on this machine today, so the delta below is attributable to one
line and nothing else.

**R-3, the row's own gate — `260731_w3_cb7 → 260731_w3_gt25`, 13 cuts:**

```
FAIL 1 · WARN 0 · INFO 0 · PASS 12
beauty_overview  FAIL  [FRAME] moved-block 90 % (max dev 170/255)
                       [PHOTO] mean 87.5 → 146.2 (+58.7), brightening
```

`Docs/reports/regr_260731_w3_gt25.json`. Every other cut PASSes. **OCCL new-dark 0.0 % and
largest blob 0.0 % on all 13 cuts** — C02-P1 measured **32.8 %** and **19.7 %** on this cut, so
the occlusion defect is gone, not merely reduced. DARK, BLOWN and WHITE do not fire anywhere.
The single FAIL is the deliverable: a composition change on the cut the row exists for, in the
brightening direction, recovering C02-P1's **PHOTO −57.5** with **+58.7**.

**Containment**, the reason the two adjacent judged cuts were rendered:

| cut | Δmean (pre → gt25) | pixels > 16 LSB |
|---|---|---|
| `preset_h0.3_d10` | −0.02 / −0.02 / −0.02 | **0.0 %** |
| `preset_h1.8_d10` | −0.00 / −0.00 / −0.00 | **0.0 %** |

These are the two judged eyes nearest in plan to the vacated and the new footprint (both at
x = −10, 3.45 m from either bed); every cut in the scene looks toward +X, so a bed at
x ≤ −9.45 leaves the frame entirely. The attribution regression `gt25_pre → gt25` returns the
**same** verdict on the only cut that moves and raises `[UNCHANGED]` WARNs on nine others —
the checker's "suspiciously identical" flag, which here **is** the containment proof.

### 3.3 §6.1 floor (scene02)

| gate | result |
|---|---|
| `python3 -m py_compile scenes/main/scene02_underpass.py` | OK |
| `NEGOBS_SMOKE=1 python3 scenes/main/scene02_underpass.py` | **48/48 gates `[OK ]`, 0 failures, rc 0** — `[SELFCHECK] scene02 CB-7 — PASS` |
| `python3 scripts/geom_invariance_check.py --scenes scene02` | **R-4 1/1 · R-6 1/1 PASS**, prims **545 unchanged**, hash `a4c3a5f9` → `cceee473` — an element AABB move, exactly the row's declared class |
| `python3 scripts/placement_lint.py --scenes scene02` | **ERROR 4 · WARN 9 · BLOCK 1 — identical to the HEAD arm**, down to the inventory string (`bench=2 bin=2 bollard=4 lamp=4 patch=2 planter=2 shrub=4 sign=2 sitestack=10 stain=8 tree=2`). The 4 ERRORs are the pre-existing LINT-6 bollard set (CB-7 §8.2), untouched |

All four run in the isolated arms, **not** in the worktree — see §7 **MD-F1** for why that
distinction is load-bearing here.

### 3.4 Prepared landing-record text for GT-25 §4 — **for the supervisor, not written by me**

> | GT-25 | S2 (`main/scene02_underpass.py`) | micro pilot **02** (`beauty_overview`) | `5340d49` | **Landed coordinate `(−11.0, −5.0)`, NOT the declared `(−11.0, −6.2)` — deviation declared in advance by the phase-Code report, not discovered in a diff.** At `y = −6.2` the 3.0 × 3.0 m bed interpenetrates the hedge band (`scene02:285`, whose own comment records that it was moved to `y = −7.0` *"avoiding the planter"*): measured `Hedge_0` **2.350 × 0.683 × 1.060 m** and `Hedge_1` **0.885 × 0.660 × 0.898 m** in an isolated fake-USD arm. At `y = −5.0` the overlap set is byte-identical to HEAD's (ground plates only) and the eye→centre distance is **4.000 m** against the row's re-derived 4.176 m — a 0.176 m shortfall on the figure the row itself excludes from its target. **The second planter `(−13.0, 5.5)` is untouched.** **R-1 / R-2 not owed** (class as declared: no walked surface, no hazard box, no drop edge). **R-3** — round **`260731_w3_gt25`** (13 cuts, PT, under `flock -w 7200 /tmp/negobs_gpu.lock`, arm byte-identical to the baseline stamp: `NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`), then `python3 scripts/regression_check.py --before look_check/scene02/260731_w3_cb7 --after look_check/scene02/260731_w3_gt25 --json Docs/reports/regr_260731_w3_gt25.json` → **FAIL 1 · WARN 0 · INFO 0 · PASS 12**. The single FAIL is `beauty_overview` **[FRAME]** moved-block 90 % + **[PHOTO]** mean **87.5 → 146.2 (+58.7)** — the declared composition change, recovering C02-P1's **−57.5** in full. **OCCL new-dark 0.0 % · largest blob 0.0 % on all 13 cuts** (C02-P1: 32.8 % / 19.7 %); DARK / BLOWN / WHITE do not fire. **Attribution**: `260731_w3_gt25_pre` (same pipeline, PRE-move) reproduces the committed baseline — `cb7 → gt25_pre` **FAIL 0 · WARN 0**, worst \|Δmean\| **0.31 LSB** — so the whole delta is the one line. **Containment**: the two nearest judged eyes are null, `preset_h0.3_d10` Δmean **−0.02 LSB**, `preset_h1.8_d10` **−0.00 LSB**, 0.0 % of pixels beyond 16 LSB on both. **Floor** (§6.1): py_compile ✔ · `NEGOBS_SMOKE=1` **48/48 gates, rc 0** · `geom_invariance --scenes scene02` **R-4 1/1 · R-6 1/1**, prims **545 unchanged**, `a4c3a5f9 → cceee473` · `placement_lint --scenes scene02` **ERROR 4 · WARN 9 · BLOCK 1, identical to the HEAD arm**. **`260731_w3_gt25` is scene02's baseline-of-record from here** — marked on its own stamp; `260731_w3_cb7`'s stamp is **not** this task's file and still claims the title, which the supervisor or the next scene02 owner should close on the S10c precedent. **Owed decision**: amend this row's coordinate to `(−11.0, −5.0)`, or rule that the hedge may move instead (a second element AABB, needing its own row) | 2026-07-31 |

---

## 4. F5 — the two round stamps

`redteam_lane1.md` §9-4 verified the `baseline_of_record` marker **ABSENT** on `260731_w3_s04`
and `260731_w3_s16`, with the status living only in ledger rows. Both stamps now carry it, on
the S10c `260731_w3_s07` precedent — **nothing was re-rendered and no pixel changed; keys only**:

| stamp | keys added | status source (re-read live) |
|---|---|---|
| `look_check/scene04/260731_w3_s04/round_stamp.json` | `baseline_of_record: true` · `supersedes` (`260730_lcfreeze_post`, 13 cuts, `0972b20`) · `comparison_baseline_used` · `dirty_paths` · `dirty_paths_note` · `note_md` | ledger §4 GT-22 (*"`260731_w3_s04` is scene04's baseline-of-record from here"*, and the same row records the missing marker as the F5 class) · `w3_s04_v1.md` §8.3 · `regr_260731_w3_s04.json`'s own `pairs` block |
| `look_check/scene16/260731_w3_s16/round_stamp.json` | same six | ledger §4 GT-23 (*"`260731_w3_s16` is scene16's baseline-of-record from here"*) · `w3_s16_v1.md` §7 / §9 · `regr_260731_w3_s16.json`'s `pairs` block. The s16 note also carries the ledger's own qualifier — hash `4233f62d` → `a9d922f5` is K1's tactile **path move**, 438/439 rows byte-identical, path-normalised hashes EQUAL |

**On `dirty_paths`, the honest part.** S10c's convention is *the paths, not the count*. These two
rounds were stamped on 2026-07-30 at HEADs `0711973` / `f831d61` with `dirty_files` 10 / 5, and a
dirty working tree at a past instant **leaves no trace in git**. The paths are therefore recorded
as **`null` with a note that says why**, rather than reconstructed by inferring from what happened
to be committed afterwards. The convention is written onto the stamps so the next stamp of either
scene carries a real list, and so the gap is visible instead of silent.

**Not committable, by design.** `look_check/**` is gitignored (`.gitignore:23`, `git ls-files
look_check` returns 2 files: `INDEX.md`, `README.md`). These four stamp edits — the two F5 ones
and the two GT-25 ones — are **on-disk artefacts**; this report is their commit record. The same
was true of S10c's stamp work.

---

## 5. Library census — judged eyes within 2.5 m of a planter footprint

C02-P1 asked for *"a one-line census across the 33 scenes"*. Run two ways, both on the composed
stage under the fake-USD harness in the **`LOOK_V1` arm** (the arm the judged rounds render), with
the judged view set taken from each scene's own `capture_pipeline` call rather than re-derived:

* **pass A** wraps `sc.build_planter` — 13 scenes call it, **52** beds;
* **pass C** (reported below) takes the **XY AABB of every `*Planter*` subtree in the composed
  inventory**, so it also catches the two scenes that re-implement the bed locally
  (`scene01.build_planters`, `scene18._plate`) — **15 scenes, 64 bed groups**.

Distance is plan (XY) eye-to-rectangle, 0.0 when the eye is over the box. `kerb` = the
`build_planter` `size × size` footprint the brief names; `AABB` = the whole bed subtree including
the crown.

| scene | nearest judged cut | judged cuts ≤ 2.5 m | kerb (m) | AABB (m) | eye→centre (m) | bed | vegetation referenced |
|---|---|---|---|---|---|---|---|
| **scene02** | `beauty_overview` | 1 | **0.00** | **0.00** | 1.00 | `Planter_0` | `Elm_Sapling.usd`, `Rhododendron_noflower.usda` |
| **scene08** | `beauty_overview` | 1 | **0.00** | **0.00** | 1.50 | `PlazaPlanter_0` | **`Fraxinus.usd`**, `Rhododendron_noflower.usda` |
| scene08 | `facade_court` | 2 | 0.20 | 0.15 | 1.40 | `CourtPlanter_0` | `Rhododendron_noflower.usda` |
| scene08 | `open_gap` | 8 | 0.40 | 0.31 | 2.06 | `GapPlanter_0` | `Juniper.usd` |
| **scene20** | `oblique_overview` | 1 | 0.50 | 0.45 | 2.50 | `Planter_1` | **`Elm_Sapling.usd`**, `Rhododendron_noflower.usda` |
| scene05 | `side_arc` | 1 | 1.39 | 1.33 | 2.59 | `RingPlanter_4` | `Fraxinus.usd`, `Rhododendron_noflower.usda` |
| scene08 | `underground_look` | 1 | 1.40 | 1.35 | 2.60 | `CourtPlanter_1` | `Rhododendron_noflower.usda` |
| scene08 | `preset_h0.3_d2` | 7 | 1.50 | 1.45 | 3.06 | `GapPlanter_1` | `Rhododendron_noflower.usda` |
| sceneN1 | `beauty_oblique` | 1 | 1.50 | 1.45 | 3.16 | `Planter_A` | `Rhododendron_noflower.usda` |
| **scene01** | `preset_h0.3_d5` | **7** | *local* | 1.70 | 3.25 | `Planter_A` | `Elm_Sapling.usd` |
| sceneN3 | `preset_h0.3_d5` | 3 | 2.30 | 2.25 | 3.63 | `Planter_A` | `Elm_Sapling.usd`, `Juniper.usd` |
| sceneC4 | `lower_lookback` | 1 | 2.47 | 2.40 | 3.81 | `Planter_2` | `Rhododendron_noflower.usda` |
| scene14 | `lower_lookup` | 1 | 2.50 | 2.45 | 4.03 | `PlanterLow_0` / `_1` | `Juniper.usd` |
| **scene16** | `preset_h0.3_d5` | **7** | 2.50 | 2.45 | 4.12 | `Planter_A` | `Elm_Sapling.usd`, `Rhododendron_noflower.usda` |
| sceneC4 | `film_closeup` | 1 | 2.50 | 2.45 | 3.42 | `Planter_1` | `Juniper.usd` |

**44 (judged cut × bed) pairs across 10 scenes.** Clear of the radius entirely: scene13 (nearest
3.75 m), scene18 (4.27), scene19 (4.49), sceneN2 (6.25), sceneN5 (4.75), and the 18 scenes with
no bed at all.

**What the census says, for the fanout briefs.**

1. **scene02 was not unique, and it was not even the worst-shaped case.** `scene08`'s
   `beauty_overview` eye `(−12.0, −12.0, 9.0)` sits **inside** `PlazaPlanter_0`'s footprint with a
   live `Fraxinus.usd` in it — the same class as C02-P1. It is 9 m up, so the crown may fall below
   the eye rather than filling the frame; **that is a render question, not a plan question, and
   scene08's owner should measure it** exactly as CB-7 measured C02-P1. `scene20`'s
   `oblique_overview` `(−8.0, −4.0, 3.2)` at 0.45 m from an `Elm_Sapling` bed is the closest
   geometric analogue to the defect this batch just fixed.
2. **Two scenes are exposed on seven judged cuts each**, not one: `scene01 Planter_A` (1.70–2.45 m
   from six presets plus `beauty_overview`) and `scene16 Planter_A` (2.45–2.49 m from six presets
   plus `shadow_band`). Low blast radius per cut, but wide.
3. **A `build_planter`-only census is not sufficient.** `scene01` and `scene18` build their beds
   locally, so pass A is blind to them and pass A's scene01 row is missing entirely — any fanout
   brief that greps for `build_planter` will under-count. The AABB pass is the one to reuse.
4. Every hit that carries a tree carries a **K4(b) USD species**, not a procedural blob. The
   defect class was created by K4(b) + `place_shrubs`, exactly as C02-P1 diagnosed; before that
   round these beds held ellipsoids and none of this was visible.

**Fanout owners fix their own scenes** (C02-P1's own instruction). Nothing outside scene02 was
edited here.

---

## 6. Findings handed on

| # | Sev | Finding | Owner |
|---|---|---|---|
| **MD-F1** | **MED** | A **concurrent lane wrote `ground_kit.py`, `scripts/regression_check.py` and `Docs/reports/w3_mc_d14_v1.md` into the worktree during this task**, contrary to the dispatch's *"no other lane is running"*. It is not inert: assembled against the dirty worktree, **scene02 is 543 prims / `8ac2fa99`**; against the clean HEAD arm it is **545 / `a4c3a5f9`** — the two `sidewalk_block` patches GT-24 deletes. Every measurement in this report was therefore re-run in isolated `git archive` arms. Any lane that measured scene02, 08, 16, C2, C4 or N5 from the worktree in this window measured GT-24 as well | dispatch / GT-24 lane |
| **MD-F2** | MED | **FU-1 is not achievable as a revert** and should be re-scoped, not retried. What it wants — instancing *and* a scene-chosen material — needs a **per-(asset, material) reference wrapper** in `urban_kit`, the urban twin of K4(0)'s `sc.veg_wrapper_rel`. 30 scene07 boulders → ~6 prototypes with the moss tiers intact | K-track / `urban_kit` |
| **MD-F3** | MED | `assets/urban/rock_moss_set_01_1k.usdc` binds a **MaterialX** material whose `ND_normalmap_float` node is missing from this runtime's Sdr registry. Invisible today only because scene10 overrides it per mesh; any *new* call site that instances this asset will render red. `ensure_mdl_package()` does not cover MaterialX — this is FU-2's sibling, not FU-2 | procurement / `urban_kit` |
| **MD-F4** | LOW | **GT-25's declared coordinate is unbuildable** as written (§3.1). The row needs a supervisor amendment to `(−11.0, −5.0)`, or an explicit ruling that the hedge may move | supervisor |
| **MD-F5** | LOW | `260731_w3_cb7`'s stamp still reads as scene02's baseline-of-record now that `260731_w3_gt25` supersedes it. S10c closed the equivalent by writing `baseline_of_record: false` + `superseded_by` on the superseded stamp; that stamp is outside this task's paths | supervisor / next scene02 owner |
| **MD-F6** | LOW | **S10c-F5 / RT F9 bites again**: `scripts/stamp_round.py` still records `dirty_files` as a count and still samples its own process env, so both GT-25 stamps needed the `dirty_paths` / `env_source` workaround by hand, and F5's retroactive stamps can only record `null`. Third round in a row worked around per-round | tooling track |
| **MD-F7** | INFO | **`scene08 beauty_overview` is the census's C02-P1 twin** — eye inside a planter footprint holding a `Fraxinus.usd`. Not measured in pixels here (scene08 is not this task's file); the CB-7 §8.1 method transfers directly | S-lane / scene08 owner |
| **MD-F8** | INFO | The `[UNCHANGED]` WARN in `regression_check` fires on 9 of 13 cuts in a same-arm attribution round, i.e. **containment reads as a warning**. Harmless here because the round that matters is `cb7 → gt25` (WARN 0), but any attribution round will look noisy for the same reason | tooling track |

---

## 7. Reproduction

```bash
# isolated arms (never the worktree) — the whole report depends on this
git archive e1150d6 | tar -x -C <arm>; rm -rf <arm>/assets; ln -s <repo>/assets <arm>/assets
python3 scratchpad/fu1_revert.py <arm_fu1>          # instanceable=True + drop the rebinds

# assembly proofs, GPU 0
python3 scripts/geom_invariance_check.py --scenes scene02          # md arm: 545 / cceee473
python3 scripts/geom_invariance_check.py --scenes scene07,scene10  # fu1 arm: 1420 / 2777
python3 scripts/placement_lint.py --scenes scene02
NEGOBS_SMOKE=1 python3 scenes/main/scene02_underpass.py            # 48 gates
python3 scratchpad/s02_planter_probe.py                            # GT-25 siting / hedge overlap
python3 scratchpad/planter_census.py && python3 scratchpad/planter_census_c.py   # §5

# GPU, all six arms + the two noise controls, one lock
flock -w 7200 /tmp/negobs_gpu.lock bash scratchpad/run_md_renders.sh
flock -w 7200 /tmp/negobs_gpu.lock bash scratchpad/run_noise_ctl.sh
flock -w 7200 /tmp/negobs_gpu.lock bash scratchpad/run_gt25_full.sh   # 13-cut pre + gt25

# adjudication (run from the HEAD arm — the worktree copy was another lane's WIP)
python3 scripts/regression_check.py --before look_check/scene02/260731_w3_cb7 \
    --after look_check/scene02/260731_w3_gt25 --json Docs/reports/regr_260731_w3_gt25.json
python3 scripts/regression_check.py --before look_check/scene02/260731_w3_cb7 \
    --after look_check/scene02/260731_w3_gt25_pre        # reproduction, must be null
python3 scratchpad/imgcmp.py <dirA> <dirB>               # means, LSB bands, red-fallback
```

**Commits.** `5340d49` scene02 (GT-25) · this report. `look_check/**` and the four stamp edits are
gitignored artefacts. `Docs/reports/regr_260731_w3_gt25.json` is this round's adjudication output
and is committed with the report — the one path beyond the literal own-list, declared here rather
than slipped in.
