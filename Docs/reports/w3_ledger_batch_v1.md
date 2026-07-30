# W3 supervisor ledger batch — eight amendments to `gt_changes_w3.md`

> **Wave**: W3 · **Lane**: LB (supervisor ledger batch) · **Date**: 2026-07-31 (wave-day label;
> git author dates read 2026-07-30) · **Branch**: `feat/realism-v1`
> **Owned files, and only these**: `Docs/audit_v4/gt_changes_w3.md` · this report.
> **Window discipline**: the ledger was frozen by `w3_intake_v2_images.md` §7's dispatch note
> (*"NO lane writes `gt_changes_w3.md` while the 07/10 workflow runs — GT rows are PREPARED in
> reports and appended by the supervisor afterwards"*). That workflow has exited (red-team exit
> verification landed at `ed7a4d0`), so this batch is the first ledger write of the window and it
> runs **before** any Lane-1/Lane-2 writer touches the file.

---

## 0. The batch in one table

| # | Item | Where it landed in the ledger | Authority | Independently verified against |
|---|---|---|---|---|
| 1 | **GT-3 content FLIP** — canopy deletion → full-length enclosed soffit-lit canopy **rebuild**; prim delta sign flips to **ADDED** | §3 GT-3 (annotated in place) | `w3_intake_v2_images.md` §7-1 + §3(i) | `scene02:240` pre-state re-read `[repro]` |
| 2 | **GT-4 → `RETIRED`** — superseded by the user's 2nd review (scene01 kerbed designed lawn per G1); **P-5's evidence gate dies with it** | §2 (new vocabulary row) · §3 GT-4 · §4 GT-4 | `w3_intake_v2_images.md` §7-6 | spec §9's P-5 row read verbatim |
| 3 | **GT-14 amendment** — corridor bed `z0` **−0.22 → −0.33** | §3 GT-14 (annotated) | `redteam_s0710_rebuild.md` F3 | `scene07:220 corridor_bed=0.33` live `[repro]` |
| 4 | **GT-20 amendment** — newels **20/28 → 28/40** | §3 GT-20 · §4 GT-20 (both annotated) | `redteam_s0710_rebuild.md` F4 | scene10 SMOKE re-run live `[repro]` |
| 5 | **sceneN2 z-ladder note** — 8th rung `seam_proud = 0.0023`, inside `GT_DELTA 0.020`, **no GT value change** | §7 watch item **W8** | `w3_n2_clean_v1.md` §7-1 + its §7 adjudication | the scene's own assert block, §3.5 |
| 6 | **scene16 row appended → `GT-23`**, `LANDED` | §3 · §4 | `w3_s16_v1.md` §6.2 (prepared) | `regr_260731_w3_s16.json` re-parsed |
| 7 | **scene04 row appended → `GT-22`**, `LANDED` | §3 · §4 | `w3_s04_v1.md` §9 (prepared) | `regr_260731_w3_s04.json` re-parsed |
| 8 | **No scene18 row** — deliberate non-action | *(nothing written)* | dispatch note; S18 lane still committing | — |

**Method, stated once.** GT-6's 07-31 amendment is the precedent: **annotate, never silently
rewrite**. Every changed figure keeps its old value struck through beside the new one and carries a
`[supervisor amendment 07-31 · ledger batch §9-n]` marker pointing at the new §9 section, which
holds the reasoning. Nothing was deleted from the file. The batch's own section is §9; the eight
items are §9-1 … §9-8.

---

## 1. Verification — every number re-derived before it was written

Item 3 and item 4 are corrections of the ledger's own prose, so the tree is the only acceptable
witness for them. Both were re-derived live in this session rather than copied from the red team's
report.

### 1.1 Item 3 — the corridor bed

```
scenes/main/scene07_temple_stone_path.py:220   corridor_bed=0.33
                                        :207   # corridor_bed 0.33  the `PathCorridor` / `SouthScarp` slope plates drop by this much.
                                       :1265   bed = float(cp["corridor_bed"])
                                       :1962   bed = float(PARAMS["courses"]["corridor_bed"])
```

Four independent occurrences, all **0.33**. The declared value **−0.22** entered at `3c84961`; the
landed value is **−0.33**; the landing edit `c09fa47` rewrote GT-14's row without fixing it.

**The geometry was never wrong** — GT-14's landing record already measures **tread-back clearance
+0.0526 m**, which is only true over a −0.33 bed. So this amendment corrects prose, re-baselines
nothing, and re-opens no re-cache. GT-14's frozen invariants (`path_z`, `STAIR_RUN`, `STAIR_DROP`,
`SIDE_DROP`, the `x = 12.2 / z = −4.2` junction) are untouched.

### 1.2 Item 4 — the newel census

`NEGOBS_SMOKE=1 python3 scenes/main/scene10_park_deck_switchback.py` (CPU, no GPU, rc 0):

```
엄지기둥 28개 (런 끝점 40개에서 중복 제거) · 갓 0.120x0.120x0.045 · 난간 위 돌출 0.150 m
파손 베이 = ['LandRail_0_Out'] (참0 외측 1개만) · 난간대·살대 탈락 / 기둥·엄지기둥 잔존 → OK
```

**28 newels from 40 endpoints.** The ledger's 20/28 was a **pre-de-stacking snapshot**: GT-19's
six-flight rebuild created the extra run endpoints, and the count was written from commit-time
state instead of being re-derived at batch end. Corrected in **both** places it appears (§3 row and
§4 landing record). No geometry moved; every other figure in GT-20's record — round members = 0,
rail height 1.10 to the top face, worst baluster clear gap 0.1094, `broken_landing = 0`, prims
1038, hash `e0133ccd` — is unaffected and stands.

### 1.3 Items 6 and 7 — the two landed rows, checked against their JSON, not their prose

Both regression JSONs were re-parsed rather than trusted:

| row | JSON `pairs` | cuts | verdicts read from the JSON | report claim |
|---|---|---|---|---|
| **GT-23** scene16 | `260730_w2d_fix` → `260731_w3_s16` | 13 | **PASS 7 · WARN 5 · INFO 1 · FAIL 0** | §7.1 identical |
| **GT-22** scene04 | `260730_lcfreeze_post` → `260731_w3_s04` | 13 | **FAIL 9 · WARN 4** | §8.3 identical (all FAILs FRAME, declared in advance) |

Round directories were listed on disk to settle the baseline question in item 6 (§2.2 below), and
both round stamps were read: matching PT arms, `git_head f831d61` / `0711973`, and **neither
carries a `baseline_of_record` marker** — the F5 class the red team raised against
`260731_w3_s07`. That is recorded in both landing records rather than smoothed over.

### 1.4 Item 1 — the pre-state the flip replaces

`scene02:240` `canopy=dict(x0=-1.8, x1=0.6, y0=-2.45, y1=2.45, …, z_roof=2.7)` ⇒ a 2.40 × 4.90 m
slab on 4 free posts covering **0.6 m of a ≈7.6 m descent**. The ledger's §6 cross-check row for
GT-3 is left standing and is still `[repro]`; after the flip it documents the **pre-state**, which
is now what the rebuild replaces rather than what leaves the frame. Said explicitly in §9-1 so a
later reader does not read a stale target out of it.

---

## 2. The two judgement calls this batch had to make, and how they were made

### 2.1 GT-22 / GT-23 land as `LANDED`, not as `OPEN`

`w3_s04_v1.md` §9 drafted its row as `OPEN` (a report cannot land a row). The ledger's own
vocabulary settles it: `LANDED` = *committed **and** §4's landing record filled with the real
command and its result*. Both conditions hold — scene04 at `024a985`, scene16 at `f831d61`, with
R-1 and/or R-3 done and their results recorded. **R-2 is not owed by either**: both are class A,
so no walked surface, no hazard box and no drop edge moved, and §1's re-cache scope only demands a
mini data render where one of those does. This is exactly the distinction that keeps **GT-18**
`OPEN` — that row's R-2 genuinely is owed and the record says so instead of guessing the data
owner's invocation (§0-3).

### 2.2 scene16's comparison baseline is `260730_w2d_fix`, and that is not a §6-W4 violation

§6-W4 says every row landing after CB-2 compares against the baseline stamped at CB-2's gate. The
apparent conflict is resolved on the facts rather than waved through:

* CB-2's GATE-1 pilot set is **03 · 07 · C2 · 01**. scene16 is not in it, so **no
  `260731_w3_cb2` round exists for scene16** — confirmed by listing `look_check/scene16/`, which
  holds `260730_w2d_fix`, `260730_w2d_judge`, `260731_w3_s16` and pre-W2 rounds only.
* GT-8 retires the **library-wide comparison JSON** `regr_260730_w2d_fix.json`. It does not retire
  scene16's own round directory of the same name.
* `look_check/README.md` §2: a scene's latest judgement round in its scene root **is** its
  baseline-of-record.

So `260730_w2d_fix` was the correct and only available comparison, and the landing record **names
the baseline** as §6-W4 actually requires. The same reasoning is what makes sceneN2's
`260730_w3_n2clean` its baseline-of-record with no `look_check/README.md` chain edit (item 5).

**One id note, stated rather than assumed**: `w3_s04_v1.md` §9 had already drafted scene04's row as
**GT-22** in text, so scene16 — whose report deliberately left its id as `GT-2x` — takes **GT-23**.
Ids are assigned in append order; none are reserved for lanes still running.

---

## 3. Item 8 — the deliberate non-action

The S18 lane is **still landing commits** on `scenes/main/scene18*` and `assets/coastal`. Its
identity swap is in the tree (`a443d5a`, mural stair → 해운대형 백사장 진입 계단, 낙차 **2.560 m**
unchanged), but the GT consequences are the running lane's to declare in its own report, and the
supervisor appends them **afterwards**.

**This batch created no scene18 row, reserved no id for one, and changed no scene18 figure anywhere
in the ledger.** No file under `scenes/main/scene18*` or `assets/coastal` was read for content,
written, or staged.

---

## 4. Verification floor (spec §6.1) — scoped, and the scoping is stated

This commit changes **two Markdown files and no code**, so two of the four floor items have no
subject:

| floor item | result |
|---|---|
| `python3 -m py_compile <files touched>` | **n/a** — no `.py` in the commit |
| `NEGOBS_SMOKE=1 python scenes/<scene>.py` | **n/a** — no scene touched. *(scene10's SMOKE was nevertheless run, as the witness for item 4 — rc 0.)* |
| `python3 scripts/geom_invariance_check.py` | **run unscoped, and it completes: R-5 violations 0 · R-4 33/33 ✔ PASS · R-6 33/33 ✔ PASS** |
| `python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml` | **run tree-wide for the record: 65 ERROR / 238 WARN at this HEAD.** This commit's delta is **0 by construction** — it contains no code |

**The unscoped `geom_invariance_check` is worth reporting on its own.** Both new rows' reports could
only obtain **32 of 33** — `w3_s16_v1.md` §9's run aborted at `scene04` (another lane's uncommitted
file at the time), `w3_s04_v1.md` §8.1's run aborted at `scene18` (the S18 lane). At this batch's
HEAD the sweep **completes**, and the two rows' own scenes reproduce their landed figures to the
digit:

```
scene04      1335  d530f155  d530f155  d530f155  ✔
scene16       439  4233f62d  4233f62d  4233f62d  ✔
scene18       979  18dd6520  18dd6520  18dd6520  ✔
[R-4] MTL 0/1 해시 일치 33/33  ✔ PASS
[R-6] V1=1 3자 일치   33/33  ✔ PASS
```

Recorded in the ledger (§9-7 and both landing records) as **evidence, not closure**: S18 is still
committing, so the sweep that discharges the obligation is the one taken **after** that lane
closes. The 65 tree-wide lint ERRORs are likewise **not** this commit's — they belong to whichever
files carry them at this instant, and they are named here only so that a later reader does not
mistake a docs commit for their cause.

---

## 5. What this batch did **not** touch

* Every scene file, every kit, every script — **no code in the commit**.
* `Docs/briefs/w3_execution_spec_v1.md` — §9-2's **P-5 strike is recorded, not applied**. The spec
  is authority over the ledger (§0: *"This file never overrides it"*), so the ledger records that
  P-5 is dead and the spec owner carries the edit. Same for §1.5's Option-A clause: the ledger
  records the supersession, the spec owner re-writes the clause.
* `Docs/briefs/s3_scene07_10_rebuild_spec_v1.md` — items 3 and 4 correct the **ledger's**
  transcription, not the spec's text.
* Every lane report — the prepared rows in `w3_s16_v1.md` §6.2 and `w3_s04_v1.md` §9 are
  transcribed **into** the ledger and left standing where they are.
* `scenes/main/scene18*`, `assets/coastal` — the running lane's paths.
* `ground_kit.py` — scene16's `TACTILE_SITES` / `EXPECTED_FP` rows are **queued to Lane-1 K1** by
  its own supervisor adjudication, and the ledger records them as owed. Registering the site
  without moving the band's build into `build_ground_kit` would leave B11 describing something the
  kit does not emit, so the registry row and the scene's 3 lines land **together**, in Lane 1.

---

## 6. What is now owed, and by whom

| owed | owner | source |
|---|---|---|
| **CB-7 re-spec** before it is cut — GT-3 is now a build, not a deletion; the rebuilt prim count is stated at land, not guessed now | S2 | §9-1 |
| Spec-side strike of **§1.5 Option A** (this clause) and of **§9's P-5 row** | spec owner (T5) | §9-1 / §9-2 |
| scene01's kerbed-lawn band (`R01-1`) — expected class **A**; **declares a new row** if it moves any GT quantity. It does not inherit GT-4 | S1 | §9-2 |
| **GT-18's R-2** — the mini data render for scene10; still the only thing keeping that row `OPEN` | data owner → S3 | ledger §4 GT-18 |
| `TACTILE_SITES["scene16"]["stair_top"]` + the 3-line `build_ground_kit` move + 2 `EXPECTED_FP` rows, **in one commit** | Lane-1 **K1** | §9-6 |
| **§12.6 quadrant re-count** — scene16 leaves the pure cue+/label− quadrant | Lane 4 (judging re-open) | §9-6 |
| **33/33 `geom_invariance_check`** taken *after* the S18 lane closes | whoever closes S18 | §9-7 |
| `baseline_of_record` markers on the `260731_w3_s04` / `260731_w3_s16` stamps (**F5** class) | round lane (X1) | §9-7 |
| **scene18's GT row** | S18 lane → next ledger batch | §9-8 |

---

## 7. Sources

* `Docs/audit_v4/gt_changes_w3.md` — the file amended (§0 append-before-land, §1 re-cache scope,
  §2 vocabulary, §6-W4 baseline rule)
* `Docs/surveys/w3_intake_v2_images.md` — **§7-1** (GT-3 reversal) · **§7-6** (GT-4 retirement) ·
  §3(i) (the canopy enumeration) · §2 scene01 / scene02 rows · §7 dispatch note
* `Docs/briefs/w3_execution_spec_v1.md` — §1.5 (superseded clause) · §4.3 (row ownership: S5 owns
  scene04, S2 owns scene16) · §6.1 (the floor) · §8 (ledger law) · §9 (P-5)
* `Docs/reports/redteam_s0710_rebuild.md` — **F3** (bed −0.33) · **F4** (newels 28/40) · F5 (stamp
  marker)
* `Docs/reports/w3_s16_v1.md` — §2.5 (GT-E1′/GT-E2/EXPECTED_FP arithmetic) · §6.2 (prepared row) ·
  §7.1 (round) · §9 (floor) · §7 adjudication
* `Docs/reports/w3_s04_v1.md` — §8.1–8.3 (floor, `verge_selfcheck`, round) · §9 (prepared row) ·
  §10 adjudication
* `Docs/reports/w3_n2_clean_v1.md` — §3.5 (the cold joint and the asserted ladder) · §7-1 (the
  handover) · §7 adjudication
* Live tree, this session: `scene07:220`, `scene02:240`, scene10 SMOKE, `geom_invariance_check`
  (33/33), `placement_lint --scenes all`, `look_check/scene{04,16,N2}/` listings,
  `regr_260731_w3_s04.json`, `regr_260731_w3_s16.json`, both `round_stamp.json`s
