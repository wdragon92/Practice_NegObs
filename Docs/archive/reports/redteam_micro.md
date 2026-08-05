# Red team — MICRO batch exit verification (MA · MB · MC · MD)

> **Wave** W3 · **Lane** red team (post-Lane-1 micro batch) · **Date** 2026-07-31 (wave-day label;
> git author dates read 2026-07-30) · **Branch** `feat/realism-v1` · **HEAD verified live**
> `8a2bd8a`, tree clean.
> **Targets**: `w3_micro_docs_v1.md` (MA, commits `d4469c1·35b8e39·6f5b24c·4d88923·e1150d6`) ·
> `w3_mb_patch_v1.md` (MB, `8b6baa7·59a944e`) · `w3_mc_d14_v1.md` (MC, `8a2bd8a`) ·
> `w3_md_reverts_v1.md` (MD, `5340d49·ced59dd·570623b`).
> **Method**: adversarial, **re-run not re-read**. Every number below was produced by this session
> — isolated `git archive` arms for the A/Bs, the live tree for the floor, stored render/log
> artefacts recomputed from pixels where GPU work was claimed. Nothing was accepted on a report's
> say-so unless explicitly marked. **Owned file: this report only.** No GPU render was launched
> (all pixel claims were verifiable from committed rounds and surviving arm outputs).

---

## 0. Verdicts

| target | verdict | one line |
|---|---|---|
| **MA** micro-docs batch | **CONFIRMED** | every strike/amendment verified against its source; GT-4 tail byte-verified across 5 revisions; NF-1 math re-derived and exact; declarations precede code by timestamp |
| **MB** GT-24 sweep + `relaid` | **CONFIRMED** | isolated A/B reproduced **digit-for-digit** (31,171→31,157 · 14/0/0 · 11 scenes); MB-F1 (reachable set 11, not 15) independently re-measured TRUE; pilots and crops check out. One new hygiene defect: **RM-1** |
| **MC** D14 `EXPECTED_FP` reader | **CONFIRMED** | full-corpus re-run by this session: **2,050 cuts, exactly 2 verdict changes, both the enumerated register hits, EXPECTED_FP never PASS, metric drift 0, kill switch byte-identical**; 12/12 fabricated-finding mutation tests behave |
| **MD** FU-1 refusal · GT-25 · F5 · census | **CONFIRMED** | FU-1's refusal basis re-verified **from the surviving arm renders and logs to the last decimal**; GT-25 hedge collision re-derived from scene source arithmetic; stamps and census spot-checks pass |
| **micro exit** | **PASS** — with the §6 open items, none of which blocks the batch | pathspec audit clean on all 11 commits; tree-wide floor green at HEAD; no humans/vehicles in any new imagery |

---

## 1. MA — every strike re-run against its source

**Pathspec**: 5 commits, each exactly one file, each the declared one (`git show --stat` all five). ✔

**Spec (`d4469c1`)** — diff inspected line by line: every removed diff line reappears wrapped in
`~~…~~` beside its replacement (§1.5 Option-A clause ×3 · the *"Deleting the canopy makes 02-B
mandatory"* bullet · the one-re-cache bullet · §8 GT-3/GT-4 rows · §9 P-5 row). §14 amendment log
present with MD-1/1b/2/2b. **No original text lost.** The MD-1b/MD-2b extension is strike-only and
revertible as claimed. ✔

**Ledger (`35b8e39`)** — 5 removed lines, all re-emitted with strikes/annotations added:

* **GT-4 tail** (item 3), checked programmatically:
  `— expect to *reduce* per-element counts, **not** raise the cap` is present at `d71e1e3^`,
  **absent** at `d71e1e3` and `35b8e39^`, restored inside `~~…~~` at `35b8e39` and at HEAD.
  RT-2 closed; append-only property restored. (Nit **RM-2**: the tail is **62** characters, the
  report says 63.) ✔
* **GT-21** — the `1346b70` clause is struck in place with the original preserved and the
  MD-3 marker attached. ✔
* **GT-26** — appended `LANDED`; substance matches `w3_s18_v1.md` §8's prepared row (riser 0.160 ·
  tread 0.320 · 2R+T 0.640 · revetment 2.560 · prims 1959→979); `a443d5a` exists and touches
  scene18 + its report + regr JSON. The 18dd6520→cc26fd97 hash-move note is stated in the row. ✔
* **GT-22/GT-23** — the *"33/33 owed"* clauses struck with `SATISFIED` annotations citing the
  `e8e2895` sweep; re-run live at HEAD this session: **unscoped 33/33, R-4 + R-6 PASS** (§5). ✔
* **GT-24/GT-25 declared `OPEN`, §4 empty by design** — verified in the current file; and the
  declaration commit `35b8e39` (20:16:21) **precedes** both code commits `5340d49` (20:49:12) and
  `8b6baa7` (20:52:25). Append-before-land holds. ✔
* **MD-5 / GT-6 cross-note** present in the GT-6 §3 status cell, matching the T3 amendment. ✔

**NF-1 arithmetic (item 5), re-derived from scratch, not transcribed**: with
`z(u) = cz + (t/2)/cosθ + (u−s)·tanθ`, `s = (t/2)sinθ`, requiring `z(0) = z_top` gives
`cz = z_top − (t/2)cosθ`, i.e. z term **+(t/2)(1−cosθ)** — and
`(1−sin²θ)/cosθ − cosθ = 0` makes the residual **exactly zero**. At `t = 0.78`, `θ = 14.05°`:
defect `(t/2)(1/cosθ−1) = +12.03 mm`, tangential `(t/2)sinθ = 94.68 mm`, T3's pair applied
together → `z_top − tanθ·s = −23.69 ≈ −23.7 mm`. **All three published figures are exact.**
The amendment is present at *both* prescription sites (`w3_geom_reverify_v1.md` §3 NF-1 and §7
item 3), insert-only (+28/−0). ✔

**CB-7 appendix (`4d88923`)** — +75/−0, appended after §11, body untouched. ✔

One inherited defect stands against MA's output and is already on record as MB-F1: the GT-24 row
MA wrote carries the **wrong scope figure (15)**, produced by the `SCENE_PLANS` fixture census.
This session measured both sides of that story itself (§2). MA's own report described its census
method honestly, which is what let MB catch it — but the ledger cell is wrong until amended.

---

## 2. MB — the A/B re-run, and it reproduces digit-for-digit

**Arms rebuilt by this session**: `git archive e1150d6` (pre) vs the same archive +
`8b6baa7:ground_kit.py` (post), assets symlinked, full inventory dump via the repo's own
`geom_invariance_check.run_arm(dump=True)`, 33/33 assembled in both arms, field-level Counter
diff:

* **31,171 → 31,157 rows · 14 removed · 0 added · 0 modified.** Every removed row is a `Cube` at
  `…/GKit/Patch/Patch_n`. **Identical to MB §3 to the digit**, including every per-scene prim
  count and every pre/post hash (scene01 354→353 `6947cb33→108cad2f` … sceneN5 1073→1071
  `885ea29c→677c4ffe`).
* **scene09 · scene16 · scene18 · sceneC2 byte-identical** across the arms
  (`840928aa · a9d922f5 · cc26fd97 · a6a170a6`) — **MB-F1 is TRUE by direct measurement: the
  reachable set is 11, not GT-24's declared 15.** The scene-side overrides exist at the cited
  lines (`scene18:1556` `("patch",3)` · `scene09:895` `("patch",int(g["patch_n"]))` ·
  `scene16:719` `("patch",1)` · `sceneC2:398` `surface=()` · scene08 `("patch",3)`).
* **MB-F2 re-measured**: `python3 ground_kit.py` dry run in the two arms gives kit-plan prims
  **1170 → 1149 (−21)** while the real scenes move **−14** — the fixture-drift gap of 7
  reproduces.

**Live at HEAD**: `ground_kit.py` self-check **60/60 OK · 0 FAIL**, including the new
*GT-24 patch-row-0* and *relaid count-0* gates; `SURFACE_KINDS` ValueError path in place;
`TACTILE_OFF_REASON["scene18"]` replaced with the dead reason kept verbatim in the comment above
it. `placement_lint --scenes all` at HEAD: **TOTAL ERROR 30 · WARN 337 · BLOCK 29 · INFO 2**,
and the per-scene inventory is the independent second witness — `patch=` absent in exactly the
11 changed scenes, held at `16:1 · 09:5 · 18:3 · 08:3 · 19:4`. (`redteam_lane1` §7's "WARN 227"
is the per-finding tag count, not the summary TOTAL — both reproduce at HEAD; no drift.)

**Pilots** — round dirs + `_pre` attribution arms on disk for 01/02/09/16; regression JSONs
re-read: scene01 **PASS 5/5** on both baselines and attribution (no FRAME finding), scene16
PASS 4·WARN 1 (null), scene09 PASS 1·WARN 4 (null), scene02 INFO 4·WARN 1 with the single GRAZE
`[의심]` on `h0.3_d2`. The GRAZE adjudication's geometry leg is corroborated by the A/B itself:
the two removed scene02 prims sit at **x = −7.2 and −9.3** — behind a `d2` eye at `x = −2`. The
crop stack (cb7/pre/post) shows no new transverse line; the scene01 crop shows the patch element
gone and the flag pattern continuous. SMOKE spot-checks re-run: scene02 **48/48**, scene05 OK;
the *"scene01 has no SMOKE harness"* claim verified in source (boots Isaac unconditionally,
`scene01:389-391`).

**New finding RM-1 (LOW, hygiene)**: `Docs/reports/w3_mb_patch_v1.md` was committed at `8b6baa7`
— and still reads so at HEAD — with a leaked tool-markup tail: the file's last two lines are
literally `</content>` and `</invoke>`. Content above is intact; fix is a two-line deletion owed
to the MB report owner.

---

## 3. MC — the critical re-run, executed independently

**Corpus proof, rebuilt from zero by this session** (not MC's TSVs): for every stored
`Docs/reports/regr_*.json`, the round's own `pairs` block was converted to a `--list` TSV and run
three ways on the same images — `570623b:scripts/regression_check.py` (pre), HEAD (post), HEAD
`--no-expected-fp` — then diffed on **verdict + (sev,code) multiset + every metric key minus the
additive `gz_work_h`**:

```
compared cuts: 2,050   verdict changes: 2   issue-set changes: 2   metric drift: 0
pre vs --no-expected-fp: differing 0 / 2,050
```

* The two changes are **exactly the enumerated register hits**:
  `regr_260730_w2d sceneC4 preset_h0.3_d5` **FAIL→WARN** (`FAIL/GRAZE`→`INFO/EXPECTED_FP`, the
  `WARN/FRAME` untouched — "waives one line, not the cut" observed in the wild) and
  `regr_260731_w3_s16 scene16 preset_h0.3_d5` **WARN→EXPECTED_FP**. Neither becomes PASS.
* The 13-cut surplus over MC's 2,037 is `regr_260731_w3_gt25.json`, committed by MD **after** MC
  ran — included here, zero collateral in it too.

**Mutation tests, fabricated findings** (12/12 behave): off-register scene FAILs stay loud; rows
at band-edge ±1 stay loud, at the edges waive; wrong cut stays loud; **OCCL on a registered row
is never waived**; axis mismatch (work_h 1080) and missing work axis refuse to match;
**scene02's sill rows (y145 @d5) are NOT waivable** — its register keys carry only the
tactile-band rows, i.e. the §5 refusal is real in code, not just in prose; **scene16 d10 row 176
(far/entrance band) stays loud** — D14-B2 as designed. Register: **18 rows, sha
`3041e031f5c56adb`**, matching the report; `len = 2 × 9` drop-trigger scenes.

`--selftest` **전 항목 통과** (20 items) · `valset --check` all three corpora `[ok] matches
EXPECTED`, exit 0 · `check_view(..., use_expected_fp=False)` default verified and `valset.py:168`
still calls positionally — the structural insulation holds. (Nit **RM-3**: the report says
`+297/−11`; `git diff --numstat` says **+299/−11**.)

---

## 4. MD — refusal, relocation, stamps, census

**FU-1 (refused)** — the surviving isolated-arm outputs (`scratchpad/renders/s07_*,s10_*` +
logs) were **recomputed from pixels by this session**, not read from the report:

* noise floors: scene07 worst |Δmean| **0.198 LSB** (`h0.3_d2`), scene10 **0.003 LSB** — exact;
* scene07 wa→rev: `side_slope` Δmean **+0.66/+0.97/+1.75**, >16 LSB **3.3 %**, red-fallback
  **0.00 % both arms** — the gate fail is real and it is *not* an MDL story;
* scene10 wa→rev: `h1.8_d5` Δmean **+4.24/−2.27/−1.57**, red-fallback **0.02 % → 4.50 %**
  (`from_below` 0.00→0.53, `d10` 0.03→0.97) — every figure to the last decimal;
* the stored `s10_rev` log carries the quoted error verbatim, 3×:
  `cannot find SdrNode: 'ND_normalmap_float' … /_materials/rock_moss_set_01` — **0** hits in the
  workaround arm, **0** `C120` anywhere (MD-F3 confirmed; the asset's usdc does carry a MaterialX
  `NodeGraphs`/`Normal_Map` graph); `[FU1PROBE]` lines show **IsInstance 0/30→30/30 (22→25)** and
  **0/4→4/4 (20→23)** — the mechanism works, the look does not survive it;
* `scenes/main/scene07*` and `scene10*` **byte-unchanged** across `e1150d6..HEAD` (`git diff
  --stat` empty); the `:2145` "two things are happening here" comment and the
  `strongerThanDescendants` entailment are in source as cited. The refusal is the right call and
  nothing wrong landed.

**GT-25 (`5340d49`)** — one tuple + a declared-deviation comment, pathspec clean. The hedge
collision **re-derives from scene source arithmetic alone**: hedge band `y = −7.0 ± 0.30` +
`y_var ≤ 0.08` (`scene02:287-288`, its own comment reads *"y -6 → -7 (avoiding the planter)"*);
a 3.1 m bed at `y = −6.2` spans −7.75…−4.65 → full interpenetration; at −5.2 → ~0.17 m graze
(matches the probe's 0.168); at the landed **−5.0** → clear by ~0.07 m. **MD-F4 confirmed: the
declared coordinate is unbuildable without hedge surgery.** The committed
`regr_260731_w3_gt25.json` reads **FAIL 1 · PASS 12**, the FAIL being `beauty_overview`
FRAME + **PHOTO 87.5 → 146.2 (+58.7)**, `newdark 0.0`/`blob 0.0` — C02-P1's −57.5 recovered; the
render on disk shows the pit unobstructed, no humans/vehicles.

**F5 stamps** — `260731_w3_s04` and `260731_w3_s16` now carry `baseline_of_record: true` +
`supersedes` + `comparison_baseline_used` + `dirty_paths: null` with the note convention;
`260731_w3_gt25` is marked `baseline_of_record: true` with **`dirty_paths` naming the concurrent
lane's four files** — the concurrency record survives on the stamp itself. `260731_w3_cb7`'s
stamp carries no marker either way (MD-F5 stands, owed).

**Census spot-checks (2 rows, re-measured)**: scene08 `PlazaPlanter_0` at (−12, −10.5) size 3.0
→ footprint y −12.0…−9.0, and the `beauty_overview` eye (−12, −12, 9) sits **on the footprint
edge (0.00 m, centre 1.50 m)** with `…/Veg/Asset → Fraxinus.usd` composed inside it; scene20
`Planter_1` (−10, −5.5) vs `oblique_overview` eye (−8, −4, 3.2) → kerb 0.50 m / centre **2.50 m**
with `Elm_Sapling.usd`. Both rows exact.

---

## 5. Cross-cutting

**Pathspec audit — all 11 commits `d4469c1..8a2bd8a`**: every commit's file list is inside its
lane's declared paths; the interleaved history (`5340d49` MD → `8b6baa7·59a944e` MB →
`ced59dd·570623b` MD → `8a2bd8a` MC) never crosses a lane boundary. The three lanes' concurrency
reports (MB-F3 · MC §8 · MD-F1) are mutually consistent and the contested numbers reconcile
completely: scene02 **545/`a4c3a5f9`** (e1150d6) → **`f2d645b8`** (GT-24 only, my arm) →
**545/`cceee473`** (GT-25 only, MD's arm) → **543/`8ac2fa99`** (both, live at HEAD — re-measured
this session). The `assets/assets` symlink is gone; the tree is clean.

**Tree-wide floor at HEAD, run this session**: unscoped `geom_invariance_check` **33/33 · R-4
33/33 · R-6 33/33 PASS**, post-GT-24 hashes matching my post arm; `placement_lint` TOTAL
**30 · 337 · 29 · 2**; `ground_kit.py` 60/60; `regression_check --selftest` pass;
`valset --check` pass; scene02 SMOKE 48/48.

**No humans/vehicles** in any new imagery examined (scene01 crop, scene02 crop stack + gt25
beauty, scene09 pilot render).

---

## 6. Findings and open items after this batch

| # | sev | item | owner |
|---|---|---|---|
| **RM-1** | LOW | `w3_mb_patch_v1.md` ends with leaked tool markup (`</content>`/`</invoke>`), committed at `8b6baa7` | MB report owner — 2-line deletion |
| RM-2 | NIT | GT-4 restored tail is 62 chars, MA report says 63 | record only |
| RM-3 | NIT | MC report `+297/−11` vs actual `+299/−11` | record only |
| — | **HIGH (carried)** | **GT-24 §3 scope cell still reads 15 scenes / pilots 01·16·09; §4 still empty.** MB-F1's amendment (11 scenes, pilots 01·02, plaza_water leg = dead-row deletion) is verified TRUE by this session's own A/B and must precede the §4 record | supervisor |
| — | MED (carried) | **GT-25 §3 still declares `≈(−11.0, −6.2)`; landed is `(−11.0, −5.0)`.** The declared coordinate is measured-unbuildable (§4); amend the row or rule on the hedge | supervisor |
| — | carried | D14-B1 scene02 sill decision (option (a) re-baseline recommended) · D14-B2/R16-2 HELD · F4/rider 5 · D14-B3 README fallback chain · MD-F5 cb7 stamp supersession · MB-F2 fixture drift rows · MB-F4 `levee_paved` · MD-F2 FU-1 re-scope (`urban_kit` wrapper) · MD-F3 MaterialX registry gap · RT-1 · RT-4 · F9 `stamp_round` | their named owners |

**Exit: PASS.** All four lanes' work is confirmed as landed (or, for FU-1, correctly not
landed); the two ledger amendments above are supervisor items the lanes themselves flagged, not
verification failures.

---

## 7. Reproduction

```bash
# MB A/B (arms)
git archive e1150d6 | tar -x -C <arm_pre> ; git archive e1150d6 | tar -x -C <arm_post>
git show 8b6baa7:ground_kit.py > <arm_post>/ground_kit.py     # + symlink assets into both
# run geom_invariance_check.run_arm(dump=True) per arm; Counter-diff the inventories

# MC corpus (three arms per stored round)
git show 570623b:scripts/regression_check.py > rc_pre.py
# per regr_*.json: pairs -> TSV; run rc_pre / HEAD / HEAD --no-expected-fp with
#   --root <repo> --list <tsv> --json <out> --fail-only ; diff on (verdict, multiset, metrics-gz_work_h)
python3 scripts/regression_check.py --selftest ; python3 scripts/valset.py --check

# MA byte checks
git show d71e1e3^:Docs/audit_v4/gt_changes_w3.md | grep -c 'expect to \*reduce\*'   # 1
git show 35b8e39^:Docs/audit_v4/gt_changes_w3.md | grep -c 'expect to \*reduce\*'   # 0

# MD pixels (surviving arms, session scratchpad renders/ + logs/)
#   numpy over pt_noon_*.png: Δmean, LSB bands, red-fallback (R>90 ∧ R>1.8G ∧ R>1.8B)
grep -c ND_normalmap_float logs/s10_rev.log    # 3   (s10_wa.log: 0)

# floor at HEAD
python3 scripts/geom_invariance_check.py            # 33/33 R-4+R-6
python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml
python3 ground_kit.py                               # 60/60
```
