# SB — supervisor closure batch (GT-24 scope + `levee_paved` extension · GT-25 coordinate · four hygiene items)

> **Wave** W3 · **Lane** SB (supervisor closure, post-micro-red-team) · **Date** 2026-07-31
> (wave-day label; git author date reads 2026-07-30) · **Branch** `feat/realism-v1`
> **HEAD at start** `8bf7882` (verified live, tree clean at that instant) ·
> **Landed at** `5e87681` (ledger declaration) → `f39abe0` (`ground_kit.py`, one tuple) →
> `8f402fa` (ledger §4 records) → `0825f48` (GT-25 §3 status) → this report.
> **Owned files, and only these**: `Docs/audit_v4/gt_changes_w3.md` · `ground_kit.py`
> (**one tuple** + the two comments that tuple made false) ·
> `look_check/scene02/260731_w3_cb7/round_stamp.json` · `look_check/README.md` §4 ·
> `Docs/reports/w3_mb_patch_v1.md` (tail only) · this report and its crops ·
> the pilot rounds under `look_check/scene17/260731_w3_sb17{,_pre}/` and
> `look_check/_experiments/twins/scene17/260731_w3_sb17_noise/` (gitignored by policy).
> **Method**: every structural number was produced by re-execution in **isolated `git archive`
> arms** (seven other lanes share this worktree — MB-F3 recurred during this batch, §7), never by
> reading another report. Where a number is quoted from another lane it is marked as quoted.

---

## 0. Verdicts

| item | verdict | one-line basis |
|---|---|---|
| **SB-1a** GT-24 scope `15 → 11` reachable | **AMENDED** | the row's own exclusion principle applied to the full census; 18 · 09 · 16 author their own `surface` row, C2 clears it |
| **SB-1b** GT-24 gate `01 · 16 · 09 → 01 · 02` (+17) | **AMENDED** | 16 and 09 are pixel-null by construction; kept and reported as the recorded nulls |
| **SB-1c** GT-24 **extension** — `levee_paved` `("patch", 4)` deleted | **LANDED** | one tuple at `f39abe0`; **scene17 −4 prims, scene03 unreachable and unchanged**; pilot 17 PASS 5/5 above a measured noise floor |
| **SB-1d** GT-24 §4 landing record | **FILLED** | both halves, with the scope figure **corrected** rather than transcribed |
| **SB-2** GT-25 coordinate `(−11.0, −6.2) → (−11.0, −5.0)` + §4 record | **AMENDED · FILLED** | hedge interpenetration measured; **hedge not notched**; §3 status flipped in the same batch |
| **SB-3** MD-F5 — `260731_w3_cb7` stamp demoted | **CLOSED** | `baseline_of_record: false` + `superseded_by: 260731_w3_gt25`, S10c precedent, keys only |
| **SB-4** MC blocker D14-B3 — README §4 chain | **CLOSED** | 18-name chain, **33/33 scenes resolve, 0 unresolved**, every name verified on disk |
| **SB-5** RM-1 — leaked tool markup | **STRIPPED** | the two closing harness XML lines off the tail of `w3_mb_patch_v1.md` (§6.3 — named, not reproduced) |
| **SB-6** MB-F2 fixture drift → ledger watch item | **RECORDED as W9** | five instances, not four: **scene03 joins 16 · 09 · 18 · C2**, found by this batch |
| **MB-F3** — untracked `assets/assets` self-referential symlink | **ALREADY ABSENT** | `os.path.lexists('assets/assets')` is **False**; nothing to delete (§6) |
| §6.1 floor on the one tuple | **PASS** | py_compile · `ground_kit.py` 60/60 · geom_invariance 33/33 both arms · `placement_lint` verdict delta **0** |
| **New finding SB-F1** | **recorded, owed** | the `_selfcheck` GT-24 gate still names **three** profiles and does not cover the fourth |

---

## 1. What the commit changes in `ground_kit.py`

| # | edit | where |
|---|---|---|
| 1 | `levee_paved` `surface` — `("patch", 4)` **deleted** | `:1973` before, `:1980` after |
| 2 | the same tuple's `[W3 GT-24 EXTENSION]` comment block, carrying the reach measurement | above `:1980` |
| 3 | `_snap_module` docstring — *"and `levee_paved` (0.200 interlocking, **the one patch caller that still snaps**)"* was **true before this commit and false after it**; struck through, not deleted, with the consequence stated | `:632-641` |

**Nothing else.** No scene file, no other kit, no script, no fixture. The `_gt24` self-check tuple
was **not** extended — see **SB-F1** (§8) for why that is recorded rather than done.

The dead scene-side `sites patch=[…]` list in `scene17`
(`gkit["patches"]`, 4 coordinates, `scene17_ramp_pair_hangang.py:156`) is **kept**, inert at
`n = 0`, on the MB precedent: it lives in a scene file, which is outside this batch's pathspec.

---

## 2. Scope of the extension, measured before it landed

`levee_paved`'s carriers are `scene03` and `scene17` — the whole population, from
`SCENE_PLANS` **and** re-read in both scene files:

| carrier | authors its own `surface` row? | reachable | measured effect |
|---|---|---|---|
| `scene03` | **yes** — `surface=(("patch", len(g["patch"])), ("stain", ("dirt","water")))` = **8** patches, `scene03_riverbank.py:911` | **no** | 1552 prims / `d6dde846` **unchanged**; `placement_lint` inventory still reads `patch=8` |
| `scene17` | no | **yes** | **974 → 970 prims**, hash `5d073f07 → 7092d409` |

This is **MB-F1's class, caught before the tuple landed instead of after it**. MB found the
same pattern in 18 · 09 · 16 · C2 only after the sweep was committed and the ledger row had to be
amended around it; here the census was taken first and the §3 declaration (`5e87681`) already
states that scene03 is unreachable. That is the only methodological claim this batch makes for
itself.

**Field-level A/B, isolated arms cut from `8bf7882`** (`geom_invariance_check.run_arm(dump=True)`,
`Counter` diff over the full 974-row inventory):

```
REMOVED rows: 4        ADDED rows: 0        MODIFIED rows: 0
  - /World/Scene17/GKit/Patch/Patch_0 | Cube | T=(-1.3,  -0.55, -0.007); S=(0.5,  0.35, 0.015)
  - /World/Scene17/GKit/Patch/Patch_1 | Cube | T=(-5.6,   2.15, -0.007); S=(0.5,  0.35, 0.015)
  - /World/Scene17/GKit/Patch/Patch_2 | Cube | T=(-3.05, -3.35, -0.007); S=(0.35, 0.45, 0.015)
  - /World/Scene17/GKit/Patch/Patch_3 | Cube | T=(-6.4,  -1.15, -0.007); S=(0.5,  0.35, 0.015)
```

Library total **31,157 → 31,153 (−4)**. The pre-arm figure reproduces MB's post-sweep 31,157
exactly, which is the cheapest available check that the two arms are the trees they claim to be.

### 2.1 The fixture disagrees with the library, and by how much

`python3 ground_kit.py`'s 33-scene dry run moves **1149 → 1141 (−8)** while the real library moves
**−4**. The 4-prim gap is entirely **scene03**, whose `SCENE_PLANS` fixture
(`ground_kit.py:3534`) carries `overrides=dict(natural=True, infra=None)` and **does not mirror
the scene's `surface` override**, so the fixture still holds the profile's `("patch", 4)` that the
scene replaced with 8 of its own. Per-scene: **scene03 39 → 35**, **scene17 48 → 44**.

This is exactly MB-F2, one instance further on, and it is why the drift is now a ledger watch item
(**§7 W9**) rather than a paragraph in a report. **Not fixed here**: five fixture rows is a
different edit that moves the dry-run prim total and owes its own §0-1 declaration; this batch was
authorised for one tuple.

---

## 3. Verification floor (spec §6.1)

Both arms cut from `8bf7882` with `assets` symlinked; the worktree runs are the scoped
reproduction, taken at `f39abe0`.

| gate | pre arm | post arm | verdict |
|---|---|---|---|
| `python3 -m py_compile ground_kit.py` | OK | OK | **PASS** |
| `python3 ground_kit.py` | **60 OK / 0 FAIL**, 33/33 hard gates, apply round-trip 33/33 | **60 OK / 0 FAIL**, 33/33, 33/33 | **PASS** — *"전 항목 통과"* on both |
| kit-plan dry-run prims | 1149 | **1141** | −8 (§2.1) |
| `python3 scripts/geom_invariance_check.py` (unscoped) | **R-5 ✔ · R-4 33/33 · R-6 33/33** | **R-5 ✔ · R-4 33/33 · R-6 33/33** | **PASS**; per-scene table diff between the arms is **one line long** |
| `… --scenes scene17,scene03` (worktree, `f39abe0`) | — | scene17 **970 / `7092d409`**, scene03 **1552 / `d6dde846`**, R-4 2/2 · R-6 2/2 | reproduces the arm to the digit |
| `python3 scripts/placement_lint.py --scenes all` | ERROR 30 · WARN 337 · BLOCK 29 · INFO 2 | ERROR 30 · WARN 337 · BLOCK 29 · INFO 2 | **verdict delta 0**; per-check rows identical |
| `… ` text delta | — | — | **one line**: `scene17  prims=974 … patch=4 …` → `prims=970 …` with `patch=` absent. `scene03  … patch=8` unchanged |
| `NEGOBS_SMOKE=1 … scene17_ramp_pair_hangang.py` | rc 0 | rc 0 | **byte-identical output** across pre arm, post arm and worktree |

`scene03` has no SMOKE harness (`NEGOBS_SMOKE` does not appear in its source); its assembly is
covered by the geom-invariance arms, which is where its invariance was actually proved.

---

## 4. Pilot 17 — the R-3, and why its PASS is not a null

Three rounds under `flock -w 7200 /tmp/negobs_gpu.lock`, arm identical on all three
(`pt · PT_FAST · LOOK_V1 · DETAIL_SCALE 2 · DETAIL_ROUGH_GAIN 0`, five preset cuts):

| round | HEAD | dirty | role |
|---|---|---|---|
| `260731_w3_sb17_pre` | `8bf7882` | **0** | attribution arm, PRE-tuple |
| `260731_w3_sb17` | `f39abe0` | 2 (§7) | the pilot |
| `_experiments/twins/scene17/260731_w3_sb17_noise` | `f39abe0` | 2 | **re-render of the pilot** — the PT_FAST noise floor |

**Verdicts.** `260731_w3_sb17_pre → 260731_w3_sb17`: **FAIL 0 · WARN 0 · INFO 0 · PASS 5**,
*"회귀 없음"*. New-dark **0.0 %** and largest blob **0.0 %** on all five; DARK, BLOWN, WHITE and
GRAZE do not fire anywhere, so there is nothing to adjudicate and no `EXPECTED_FP` verdict is
cited. Against the §6-W4 baseline-of-record `260730_w2d_fix` the five rendered cuts are
**PASS 5/5**; the other nine report `[MISSING]` because this round did not render them — a
declared scope, not a regression (§5).

**A PASS from a regression tool can mean "nothing happened", so it was measured.** The
same-HEAD re-render gives the noise floor; the pre→post pair gives the signal:

| cut | noise: pixels > 16 LSB | signal: pixels > 16 LSB | signal max dev |
|---|---|---|---|
| `preset_h0.3_d2` | 0.000 % | **7.274 %** | 160 LSB |
| `preset_h0.3_d10` | 0.001 % | **0.914 %** | 137 LSB |
| `preset_h0.9_d5` | 0.000 % | **0.462 %** | 77 LSB |
| `preset_h0.3_d5` | 0.001 % | **0.053 %** | 74 LSB |
| `preset_h0.9_d2` | 0.000 % | **0.000 %** | 20 LSB |

Four of the five cuts carry a change **three to four orders of magnitude above the floor**, and
`h0.9_d2` is genuinely null. So the four rectangles were visible, they are gone, and **no channel
that matters moved** — the tool PASSes because a dark asphalt cut patch was replaced by the
interlocking paving that surrounds it, inside the same luminance band. That is the intended
outcome of a vocabulary deletion, and it is the reason a FRAME finding would have been wrong here.

**The pixels, committed.** `Docs/reports/_w3_sb_crops/scene17_preset_h0.3_d10_ab.png` is the
argument in one frame: BEFORE carries a **dark rectangle sitting on the light 인터로킹 200 × 100
promenade**, AFTER does not. That rectangle *is* the user's *"이상한 사각형 무늬"*
(`w3_intake_v2_images.md` §3(ii)) — an asphalt saw-cut repair drawn onto unit paving.
`scene17_preset_h0.3_d2_ab.png` shows the near-field half of the same object: a hard straight
saw-cut line running across the h0.3 ground band, gone after.

**`near_ground_stats` h0.3 triple, pre → post** — `sd` 26.3 → 27.3 · 22.2 → 22.2 · 48.6 → 48.6;
`edge` 100.5 → 108.6 · 98.8 → 98.8 · 41.2 → 41.2; `flat_gnd` 2.3 → 2.2 · 0.0 → 0.1 · 30.6 → 30.6.
**No new gate flag fires and none is cured.** The pre-existing `sd < 32` / `σ_LF < 5` flags on
d2 · d10 and the `flat% ≥ 8` / `flat_gnd ≥ 3` flags on d5 are present identically before and after
— recorded, not tuned away. A patch removal has no business moving a near-ground statistic and it
did not.

---

## 5. Why `260731_w3_sb17` is **not** promoted to baseline-of-record

`260730_w2d_fix` holds **14 cuts** for scene17; this pilot holds **5**. `resolve_round` returns
the first chain entry that exists, and `regression_check` compares only the views the two rounds
share — so promoting a 5-cut round would silently drop **9 cuts** from every later scene17
comparison, and the drop would be invisible in the output. **scene17's baseline-of-record stays
`260730_w2d_fix`.** Both `260731_w3_sb17` stamps say so in a `baseline_of_record_note`, the ledger
§4 record says so, and `look_check/README.md` §4 says so and keeps `sb17` out of the chain
entirely.

The same reasoning is why the MB lane's 5-cut `260731_w3_mb24` rounds sit **below** the full grids
in the refreshed chain rather than at its head, and why `scene16 → 260731_w3_s16` (13 cuts) and
`scene09 → 260731_w3_cb1` (17 cuts) beat `mb24` even though `mb24` is newer: on both scenes
`mb24` is **pixel-null by construction**, so the older, fuller round hides nothing and shows more.

---

## 6. The four hygiene closures

### 6.1 SB-3 · MD-F5 — the superseded stamp

`look_check/scene02/260731_w3_cb7/round_stamp.json` gained `baseline_of_record: false`,
`superseded_by: 260731_w3_gt25`, `baseline_of_record_until: "2026-07-31 (GT-25)"` and a
`note_md_f5` recording that the round is **superseded, not distrusted**: `260731_w3_gt25_pre`
reproduces it today (`cb7 → gt25_pre` = FAIL 0 · WARN 0 · PASS 12 · INFO 1, worst per-cut
\|Δmean\| 0.31 LSB), so every verdict ever read from it stands. **Keys only — nothing was
re-rendered and no pixel changed**, exactly as `260731_w3_s10`'s demotion did it.
`260731_w3_gt25` was read on disk first and does carry `baseline_of_record: true`, so the two
stamps now agree instead of both claiming the title.

### 6.2 SB-4 · MC blocker D14-B3 — the `--before-round` chain

The chain head was still `260730_w2d_judge` while **eight** W3 rounds had become
baselines-of-record, so every re-judged scene was silently compared against a pre-W3 grid — which
is what D14-B3 found and why every re-manufactured GRAZE in that report traced to a stale
resolution. The refreshed chain is 18 names; **order is priority, not date**, because
`resolve_round` returns the first entry that exists as a directory containing `*.png`.

Verified by resolution over `look_check/scene*`: **33/33 resolve, 0 unresolved** —
02→`gt25` · 10→`s10c` · 07→`s07` · 04→`s04` · 16→`s16` · 18→`s18` · N2→`n2clean` ·
09→`cb1` · 01→`mb24` · 03·C2→`cb2` · the other 22→`260730_w2d_fix`. Two things the README now
says out loud: everything after `260730_w2d_fix` (`w2d_judge`, `w2c_g2`, `w2_pilot`, `r2b_on`,
`wall`, `facade`, `r2_on`) is **unreachable** while that 33-scene round survives and is kept only
as a safety net; and `sb17` is deliberately absent (§5).

### 6.3 SB-5 · RM-1 — the leaked tool markup

`Docs/reports/w3_mb_patch_v1.md` ended with its last real source bullet
(`… · \`grid_views:3900\``) followed by **two lines of harness XML** — a closing `content` tag and
a closing `invoke` tag, reproduced here by name rather than verbatim so this report does not
recreate the defect it is closing. Both lines removed; the file now ends at that bullet, verified
at byte level before and after (`od -c` on the tail). **Tail only** — no other line of that report
was touched, and its `git diff --stat` reads `2 --`.

### 6.4 MB-F3 · the `assets/assets` symlink — nothing to delete

Checked three ways at the start of this batch and again at the end:
`os.path.lexists("assets/assets")` is **False**, `os.path.islink` is **False**,
`find assets/ -maxdepth 2 -type l` returns nothing, and `git status --porcelain` has never listed
it in this session. **The self-referential symlink is not on disk**, so the deletion item is
satisfied with no action. It is reported as *absent*, not as *deleted*, because this batch did not
remove it and cannot say who did — MB observed it live, and it is gone.

---

## 7. Concurrency, stated

MB-F3 recurred, and it is recorded rather than assumed harmless. The tree was **clean at
`8bf7882`** when this batch started and when `260731_w3_sb17_pre` was rendered (`dirty_files 0` on
that stamp). During the batch another lane's work appeared: `urban_kit.py` **modified (+631/−4)**,
then untracked `assets/urban_wrap/` and `Docs/reports/_w3_t4b_crops/`. That is the MD-F2 /
T4b urban-wrapper work, not this batch's.

**Contained, and the containment is measured, not asserted**: every structural number above comes
from isolated `git archive` arms, and the one GPU pilot rendered against the dirty tree cannot
reach it — `urban_kit` has **0 references in `scenes/main/scene17_ramp_pair_hangang.py` and 0 in
`scene_common.py`**, and `assets/urban_wrap/` is a directory created after scene17's code was
written and named nowhere in it. The paths (not just the count) are on the
`260731_w3_sb17` stamp per the S10c `dirty_paths` convention. Every commit in this batch is
**pathspec-scoped**, so no other lane's file was captured.

---

## 8. Findings

| # | sev | finding | owner |
|---|---|---|---|
| **SB-F1** | **MED** | **`ground_kit.py`'s GT-24 self-check gate under-covers the amended row by one profile.** `_gt24 = ("plaza_granite", "plaza_water", "sidewalk_block")` asserts *"단위포장 3종 patch 행 0"*; after the extension there are **four** unit-paved profiles under the rule, and a regression that restored `("patch", n)` on `levee_paved` would pass `python3 ground_kit.py` 60/60. The extension is protected by ledger §3/§4 and by this report, **not yet by a code gate**. One line, no geometry, no prim delta — deliberately not taken because this closure was authorised for one tuple and a gate tuple is a second one | Lane-1 / `ground_kit` |
| **SB-F2** | MED | **`SCENE_PLANS` fixture drift has five instances, not four.** `scene03` joins MB-F2's 16 · 09 · 18 · C2. Measured: the fixture dry run moves −8 where the library moves −4. Landed as ledger **§7 W9** with the exact replacement row; it changes the dry-run prim total and therefore owes its own §0-1 declaration | Lane-1 / `ground_kit` |
| **SB-F3** | LOW | **`scene17`'s dead `sites patch=[…]` list survives the deletion**, inert at `n = 0` (`scene17_ramp_pair_hangang.py:156`, 4 coordinates). Same disposition MB gave the eight other dead lists: kept, because scene files are outside the kit lane's pathspec | the scene17 owner |
| **SB-F4** | LOW | **`look_check/scene04/260731_w3_s04b` and `scene18/260731_w3_s18{b,c,d,e}` sit at the scene root without `baseline_of_record` markers**, beside the rounds the ledger names (`s04`, `s18`). README §1 reserves the scene root for judgement grids, corpus members, anchors and baselines-of-record; five unmarked 13/14-cut rounds there make `ls -t` ambiguous, which is the exact hazard §1 was written against. Not moved by this batch — they are other lanes' artefacts | the S04 / S18 owners, or the final sweep |
| **SB-F5** | INFO | **`260731_w3_mb24` was never stamped `baseline_of_record` in any of its four scenes**, so the only record of what those rounds are is MB's §11 text and now the refreshed README chain. Consistent with the standing F5 class (`s04`, `s16`, `s18` had the same gap) rather than a new defect | record |

---

## 9. Owed, and to whom

| owed | owner | why |
|---|---|---|
| Extend `_gt24` to `("plaza_granite", "plaza_water", "sidewalk_block", "levee_paved")` and re-word the gate string to *"4종"* | Lane-1 / `ground_kit` | **SB-F1** |
| Repair the five drifted `SCENE_PLANS` fixtures and **declare the new dry-run prim total** | Lane-1 / `ground_kit` | **SB-F2** / ledger §7 W9 |
| scene08's scene-side `("patch", 3)` + 3 sites — the patch-vocabulary decision on a `sidewalk_block` scene | **the S08 lane** | routed by ledger §3 GT-24; a profile row cannot reach it and this batch did not try |
| The equivalent scene-side rows in 16 · 09 · 18 · C2 · 03 | their scene owners | same reason |
| Move or mark `scene04/260731_w3_s04b` and `scene18/260731_w3_s18{b..e}` | S04 / S18 owners | **SB-F4** |
| `roof_membrane`'s unreachable `("patch", 3)` (MB-F5) | left where it is | §11-1: it is an *asphalt-family* profile; deleting a dead row there would blur the vocabulary distinction the extension rests on |

---

## 10. Reproduction

```bash
# isolated arms (never the worktree — seven lanes share it)
git archive 8bf7882 | tar -x -C <arm_pre>  ; rm -rf <arm_pre>/assets  ; ln -s <repo>/assets <arm_pre>/assets
git archive 8bf7882 | tar -x -C <arm_post> ; rm -rf <arm_post>/assets ; ln -s <repo>/assets <arm_post>/assets
#   then delete the levee_paved ("patch", 4) row in <arm_post>/ground_kit.py

python3 -m py_compile ground_kit.py                                   # both arms
python3 ground_kit.py                                                 # 60/60, 0 FAIL, 33/33
python3 scripts/geom_invariance_check.py                              # R-5 · R-4 33/33 · R-6 33/33
python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml
NEGOBS_SMOKE=1 python3 scenes/main/scene17_ramp_pair_hangang.py       # rc 0, identical output
# inventory A/B: geom_invariance_check.run_arm(..., dump=True) per arm, Counter diff of the row list

# pilot 17 — three rounds, GPU-exclusive
flock -w 7200 /tmp/negobs_gpu.lock <round script>   # NEGOBS_VIEWS=preset_h0.3_d{2,5,10},preset_h0.9_d{2,5}
python3 scripts/stamp_round.py look_check/scene17/260731_w3_sb17 260731_w3_sb17 scene17
python3 scripts/regression_check.py --before look_check/scene17/260731_w3_sb17_pre \
        --after look_check/scene17/260731_w3_sb17 --json look_check/scene17/260731_w3_sb17/regr_attrib.json
python3 scripts/regression_check.py --before look_check/scene17/260730_w2d_fix \
        --after look_check/scene17/260731_w3_sb17 --json look_check/scene17/260731_w3_sb17/regr_vs_260730_w2d_fix.json
python3 scripts/near_ground_stats.py 'look_check/scene17/260731_w3_sb17/pt_noon_preset_h0.3_*.png' --gate

# README §4 chain — the check that matters is resolution, not spelling
#   resolve_round() over look_check/scene* with the 18-name chain -> 33/33 resolve, 0 unresolved
```

Regression JSONs are written **into the round directories** (a stated path, gitignored), not into
`Docs/reports/regr_*.json`, which is outside this batch's pathspec — the MB precedent.

---

## 11. Sources

* `Docs/audit_v4/gt_changes_w3.md` — §0-1 append-before-land · §0-3 empty-record law · §3/§4
  **GT-24** · **GT-25** · §6-W4 baseline rule · §7 **W9** · §10 MD-7 / 10-2 · §11 (this batch)
* `Docs/reports/w3_mb_patch_v1.md` §2 · §9 **MB-F1 / F2 / F3 / F4 / F5** · §10 · §11 (the prepared
  GT-24 record, corrected here rather than transcribed)
* `Docs/reports/w3_md_reverts_v1.md` §3.1 **MD-F4** · §3.2 · §3.3 · §3.4 (the prepared GT-25
  record) · §4 (the F5 stamp convention) · §7 **MD-F1 / F5**
* `Docs/reports/redteam_micro.md` §2 (RM-1 raised) · §6 (the findings/open-item table this batch
  drains: RM-1 · MD-F5 · MB-F2 · MB-F4 · D14-B3)
* `Docs/reports/w3_mc_d14_v1.md` §10 **D14-B3** (the README chain blocker)
* `Docs/reports/w3_s10_close_v1.md` §5 — the `dirty_paths` / supersession stamp convention
* `Docs/surveys/w3_intake_v2_images.md` §3(ii) — *"이상한 사각형 무늬"*, the user's own words the
  vocabulary argument implements
* `look_check/README.md` §1 (what may sit at a scene root) · §2 (latest-judged-round rule) · §4
* Live tree, this session: `ground_kit.py:319 · :632-641 · :1968-1985 · :3534 · :3616 · :3802` ·
  `scene03_riverbank.py:105-140, 891-916` · `scene17_ramp_pair_hangang.py:130-160, 920-955` ·
  `scene02_underpass.py:285, 432, 453` · `scripts/regression_check.py` `resolve_round`
