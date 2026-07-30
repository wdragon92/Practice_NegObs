# W3 micro batch — docs + ledger corrections (post-Lane-1)

> **Wave** W3 · **Lane** MA (supervisor micro-docs batch) · **Date** 2026-07-31 (wave-day label;
> git author dates read 2026-07-30) · **Branch** `feat/realism-v1`
> **HEAD at start** `a7842bc` (verified live, clean tree) · **Predecessor** the 07-31 supervisor
> ledger batch `d71e1e3` (`w3_ledger_batch_v1.md`) and the Lane-1 exit red team `a7842bc`
> (`redteam_lane1.md`)
> **Owned files, and only these**: `Docs/briefs/w3_execution_spec_v1.md` ·
> `Docs/audit_v4/gt_changes_w3.md` · `Docs/reports/w3_geom_reverify_v1.md` ·
> `Docs/reports/w3_cb7_v1.md` **(appendix only)** · this report.
> **No code, no scene, no kit, no script was read for edit or written.**
> **Method**: GT-6 precedent throughout — *annotate in place, never silently rewrite*. Every
> superseded clause keeps its text struck through beside the replacement and carries an amendment
> marker. **Nothing was deleted; one thing that had been deleted was put back.**

---

## 0. The batch in one table

| # | Item | Where it landed | Authority | Independently verified against |
|---|---|---|---|---|
| **1** | spec §1.5 **Canopy Option A** struck → Option B (build full-length) | spec §1.5 (×3 clauses) + §8 GT-3 row + §14 | `w3_intake_v2_images.md` §7-1 | `w3_cb7_v1.md` §4 built figures; `gt_changes_w3.md` §3 GT-3 `LANDED` |
| **1** | spec §9 **P-5 row** struck — GT-4 `RETIRED` | spec §9 + §8 GT-4 row + §14 | `w3_intake_v2_images.md` §7-6 | `gt_changes_w3.md` §3 GT-4 `RETIRED` + §9-2 |
| **2** | ledger **GT-21 §3** — the *"`1346b70` reported success, so the §8.R contingency did not fire"* clause struck | ledger §3 GT-21 + §10 MD-3 | `redteam_s0710_rebuild.md` **F1** · `redteam_lane1.md` §5/§9-2 | `w3_s10_close_v1.md` §1.1 · §2 pixel figures · `w3_k4_v1.md` §1 |
| **3** | ledger **GT-4** — the ~70-char clause tail **restored** and struck | ledger §3 GT-4 + §10 MD-4 | `redteam_lane1.md` **RT-2** | recovered **verbatim** from `git show d71e1e3^` |
| **4** | ledger — **scene18 row appended as `GT-26`, `LANDED`**; §9-8 annotated closed | ledger §3 · §4 · §9-8 + §10 MD-6 | `w3_s18_v1.md` §8 (prepared row) + §9 adjudication | that report §6.1–§6.4; live `geom_invariance_check --scenes scene18` |
| **4** | ledger — GT-22 / GT-23 *"unscoped 33/33 owed to the S18-lane closer"* notes annotated **satisfied** | ledger §4 GT-22 · GT-23 + §10 MD-8 | `w3_s10_close_v1.md` §0 (`e8e2895` sweep) | re-run live at `a7842bc` |
| **5** | **NF-1 amendment line** — T3's prescription over-corrects; correct z term `+(t/2)(1−cosθ)` | `w3_geom_reverify_v1.md` §3 NF-1 · §7-3; cross-noted at ledger §3 GT-6 | `w3_k4_v1.md` §5.3 / finding **K4-F3** | the closed-form derivation, re-checked here |
| **6** | **S02-Q1 ACCEPTED** · **R02-2 DECLINED** | `w3_cb7_v1.md` **Appendix A** (appended, nothing above it edited) | supervisor ruling, this batch | `w3_cb7_v1.md` §4.2 measured rejection · §8.2 · spec §1.5 · `era_consistency_survey_v1.md:881` |
| **7** | **GT-24** (patch-vocabulary sweep) and **GT-25** (scene02 `planters[0]`) declared **`OPEN`** | ledger §3 · §4 + §10 MD-7 / 10-1 / 10-2 | supervisor, phase-Code dispatch (§0-1 append-before-land) | `ground_kit.py` + `SCENE_PLANS` census read live; `scene02:432`/`:568` read live; `w3_cb7_v1.md` §8.1 |

**Ledger amendment ids** are `MD-3 … MD-8` in `gt_changes_w3.md` §10. **Spec amendment ids** are
`MD-1 · MD-1b · MD-2 · MD-2b` in `w3_execution_spec_v1.md` §14. The two id spaces are deliberately
one sequence so a reader can follow the batch across both files.

---

## 1. Verification — what was re-derived before it was written

Nothing in this batch was copied from a report without a check. Where the tree could settle a
question, the tree settled it.

### 1.1 Item 3 — the restored clause, byte-for-byte

`redteam_lane1.md` **RT-2** found the single true deletion in the otherwise mechanically
append-only 07-31 batch: GT-4's re-cache cell lost a clause tail instead of striking it. Recovered
from git, not retyped:

```
git show d71e1e3^:Docs/audit_v4/gt_changes_w3.md
  → | **GT-4** | 01 | … | **Full re-cache + regr re-baseline.** `prim_cap = 60` re-checked
      — expect to *reduce* per-element counts, **not** raise the cap | CB-11 · GATE-2b partial | …
```

The dropped substring is **63 characters** (`— expect to *reduce* per-element counts, **not** raise
the cap`), matching RT-2's *"~70-char"* estimate. It is now inside the row's strikethrough, so the
cell reads exactly as it did at `d71e1e3^` with `~~` around it. **Checked programmatically**: the
verbatim tail is present in `d71e1e3^` **and** in the amended file. The row stays `RETIRED` and
nothing downstream changes — this is a **restoration of the append-only property**, not a
resurrection of the clause.

### 1.2 Item 2 — why the GT-21 clause is a defect and not a wording preference

The struck clause asserted: *"registered in `sc.BARE_SUBPRIMS` by the K4 micro-commit `1346b70`,
**which reported success, so the §8.R contingency did not fire**"*. Three independent sources say
that sentence was false when it was written:

* `redteam_s0710_rebuild.md` **F1** — found by eyes on `from_below` and `h1.8_d10`.
* `w3_s10_close_v1.md` §1.1 — the mechanism: a stage-side `SetActive(False)` on a **descendant of
  an instanceable prim**; USD discards opinions on descendants of an instance regardless of
  authoring order, so `260731_w3_s10` printed *"잎-off 12/12"* over **twelve trees in full green
  leaf**.
* `w3_k4_v1.md` §1 — the trap reproduced independently on real usd-core 26.8, **4 species × 3 arms,
  4/4**, and the wrapper route proven as the fix.

Pixels, which is what the row was reopened for: green-pixel share `from_below` **8.18 % → 0.00 %**,
`h1.8_d10` **1.55 % → 0.00 %**, with `Chinese_Juniper` keeping its needles as the control. The
leaf-off arm this row claims **did not exist in a rendered frame until `a8e8343`**.

So the amendment does two things: it strikes the false clause, and it says **why** the row must not
assert whether §8.R's contingency fired — the input to that judgement was a self-report, not a
measurement. GT-21's §4 landing record already carried the corrected account; §3 was contradicting
§4, and now does not. (`gt_changes_w3.md` §10-3 states this in the file itself.)

### 1.3 Item 5 — the NF-1 arithmetic, re-checked rather than transcribed

T3's §3/§7-3 prescription is *"compensate `cz` by `(t/2)(1/cos θ − 1)` **and** the tangential origin
by `(t/2)·sin θ`"*. Applied together the terms double-count: the tangential move slides the sloped
plane, changing its height at the placement azimuth by `−tan θ · ds`. Solving both conditions at
once,

```
z(u) = cz + (t/2)/cosθ + (u − s)·tanθ ,   s = (t/2)·sinθ ,   z(0) = z_top
  ⇒  cz = z_top − (t/2)/cosθ + s·tanθ = z_top − (t/2)·cosθ        ⇒  z term = +(t/2)(1 − cosθ)
```

K4(d)'s measurement on the fascia ring (`t` 0.78, tilt −14.05°): raw defect **+12.03 mm**, T3's
pair **over-corrects to −23.7 mm** — larger than the defect and of the opposite sign; the corrected
term gives lift **+12.028 → 0.000 mm** and tangential **+94.68 → 0.000 mm**. The amendment is
written **at both places T3 states the prescription** (§3 NF-1 and §7 item 3) so neither can be read
alone, and cross-noted in the ledger at §3 GT-6 — the only row that cites NF-1. **Everything else in
NF-1 stands**; the fix landed at `5ceb76a`, default OFF, with GT-6's split proof empty (31,017 rows
compared across 33 scenes, 0 differ).

### 1.4 Item 4 — the scene18 row, and the two facts its record does not hide

`w3_s18_v1.md` §8 wrote the row to §8's append template and left the id to the supervisor. It is
appended as **GT-26**, `LANDED`, because both landing conditions hold (§2 vocabulary): committed at
**`a443d5a`**, and §4's record filled with the **real** commands and their results. R-1, R-2 **and**
R-3 all ran green in that lane — this is only the **second** W3 row (after GT-14) whose R-2 was
actually executed rather than recorded as owed.

Two things the record states rather than smooths:

* **The prim hash moved after landing.** scene18 is `18dd6520` at `a443d5a` and **`cc26fd97`** from
  `e4d9cf9` onward, because K4(b)'s species pinning moved **159 inventory rows** in this scene
  through the shared library (`w3_k4_v1.md` **K4-F2**; `redteam_lane1.md` **RT-3** is explicit that
  *"04/10/18 unmoved"* holds for **species sets**, not for row counts). Species sets and every
  walked surface are untouched, and the total drop still asserts at 2.560 m. Re-verified live for
  this batch at `a7842bc`: **scene18 979 prims / `cc26fd97`, R-4 1/1 · R-6 1/1 PASS**.
* **No `baseline_of_record` marker** on `260731_w3_s18`'s round stamp — the **F5** class. The status
  lives in the ledger row alone, as it does for `260731_w3_s04` and `260731_w3_s16`.

The row also carries scene18's own R-2 discovery, because it is the kind of fact that must be
findable later: `variation_kit._Stage1Index` (`variation_kit.py:754`) drops any prim whose largest
AABB dimension exceeds 400 m, so the scene's 520–625 m ground plates were invisible to the camera
validator and 24/24 cameras were reported as floating. Fixed by tiling under `AABB_TILE_MAX = 380.0`;
re-run **24/24 ground found, worst |err| 0.0000 m**.

### 1.5 Item 4 (second half) — the 33/33 sweep, and why it is now discharged

GT-22 and GT-23 each carried *"the 33/33 `geom_invariance_check` is owed to whoever closes the S18
lane"*. The chain, verified in git rather than assumed:

| fact | evidence |
|---|---|
| the S18 lane's **last** commit is `ee6990c` (the supervisor adjudication of `w3_s18_v1.md`) | `git log -- scenes/main/scene18* Docs/reports/w3_s18_v1.md` |
| the qualifying **unscoped** sweep was taken **after** it, at `e8e2895` — 33/33, R-4 + R-6 PASS, scene04 **1335 / `d530f155`**, scene18 **979 / `cc26fd97`** | `w3_s10_close_v1.md` §0 |
| re-run independently at `535926e` — unscoped 33/33, scene18 assembles | `redteam_lane1.md` §7 |
| re-run **live for this batch** at `a7842bc` | §2 below |

So the obligation is satisfied and both notes are annotated closed. **One honest qualifier is
written into GT-23's record**: scene16's hash reads **`a9d922f5`** at and after `1a6be6b`, not the
`4233f62d` the row landed with, because K1's micro-commit moved the tactile band's prim path
(`Tactile_StairHead/Base → GKit/Tactile_stair_top/Base`). The A/B is **438 of 439 rows
byte-identical with path-normalised hashes EQUAL** (`redteam_lane1.md` §4) — the geometry did not
move, only the path. Closing the note without recording that would have made the ledger's own
figure look reproduced when it is not literally reproducible at HEAD.

### 1.6 Item 7 — the two declared rows, and the census behind GT-24

Both rows are **`OPEN` with empty §4 records** and neither authorises a landing. §0-3 governs: *an
empty landing record means the row is not closed, whatever the commit history says.*

**GT-24 scope, measured from `ground_kit.py` this session, not from the intake's prose:**

| profile | current `surface` row | line | scenes carrying the profile | in scope |
|---|---|---|---|---|
| `plaza_granite` | `("patch", 1)` | `:1747` | 01 · 05 · 14 · 18 · 20 · 21 · C1 · N1 · N3 | **9** |
| `plaza_water` | `("patch", 2)` | `:1755` | 09 | **1** |
| `sidewalk_block` | `("patch", 2)` | `:1764` | 02 · 08 · 16 · C2 · C4 · N5 | **5** |

**`scene08` is NOT in scope**, and the row says so: it overrides `surface` scene-side with
`("patch", 3)` plus 3 explicit sites, which a profile-row deletion cannot reach. This is the
GT-9 / §7-W6 scene18-weed precedent arriving again, recorded **before** the sweep runs instead of
being discovered in a diff. Two dead scene-side `sites patch=[…]` lists (`scene05` 2 · `sceneN1` 2)
are left inert by `n = 0` and are the implementing lane's to clean or keep, declared either way.

**The divergence from the intake is stated, not smoothed.** `w3_intake_v2_images.md` §3(ii)'s table
recommends `plaza_water` → 0 but `sidewalk_block` → *"1 each for the main scenes"* and
`plaza_granite` → *"0–1"*. This declaration takes **0 on all three**: the argument is about the
**vocabulary**, not the count — a cut-and-relaid asphalt patch is the wrong object on a 판석 600
module or a 보도블록 300 grid, where the real repair is a **replaced unit** — and one surviving
patch on a granite plaza is the same wrong object as two.

**Class**, argued rather than asserted: each patch is a proud dressing element at `patch_proud =
0.002 m` (`ground_kit.py:251`), one rung of the §7-W8 ladder (줄눈 0.0006 < 도색 0.0010 < 실란트
0.0012 < **패치 0.0020** < 시공이음 0.0023 < 맨홀 0.0026) and an order below `GT_DELTA = 0.020`.
Removing it removes an **element AABB**; the paving plate it sat on does not move. Hence
**no walked-z, R-3 only**, gate = micro pilots **01 · 16 · 09** (one scene per profile).

**GT-25**, verified live: `scenes/main/scene02_underpass.py:432` `planters=[(-8.0, -5.0), (-13.0,
5.5)]` and `:568` `views["beauty_overview"] = dict(eye=[-7.0, -5.0, 3.0], …)` — **1.00 m** in plan
between the planter and a judged eye. `w3_cb7_v1.md` §8.1 measured the cost on the HEAD arm alone:
**PHOTO −57.5 mean · OCCL 32.8 % new-dark · blob 19.7 % · FRAME 81 %**. One arithmetic note carried
into the row: the report quotes *"4.3 m"* for the proposed `(−11.0, −6.2)`, and the plan
re-derivation gives **√(4.00² + 1.20²) = 4.176 m** — the target of the row is the **coordinate**,
and the row says so, so nobody chases the distance figure.

**Landing records for both are filled by the supervisor from the phase-Code reports**, and each §4
row **names the evidence its record must carry** so that "filled by the supervisor" cannot become
"filled with whatever arrives".

### 1.7 Item 6 — the two CB-7 rulings

**S02-Q1 ACCEPTED.** The valance-over-open-vent-band reading of *"side infill"* is accepted as
built, on two independent grounds. (a) **The vent-band form is the real Korean underpass canopy
form** — a roof on columns with a valance and an open band at hand height; a sealed flank is a
different object and building it would be *plausible* rather than *sampled*, which is the one thing
this wave's bar forbids. (b) **The measured glazing rejection stands**: the r1 arm was built,
rendered and measured, the library's `glass` is an opaque dark constant `(0.06, 0.09, 0.12)`, and at
9 m × 1.35 m it took `beauty_overview` to DARK, `preset_h1.8_d2` to PHOTO −45.8, and **hid the BS-4
street wall the same commit had just built** — the opposite of G2, where the shops read *past* the
flanks. `canopy.infill_z0` stays 1.75; GT-3 needs no amendment.

**R02-2 DECLINED.** Three stair bays are **not** built. It is not user-ordered — intake §7 ruling 1
named exactly what to build and §7's eight rulings are the closed set, so re-planning the stair from
a *recommendation* would be a lane inventing scope. And it would re-open the **mid-rail** question
that the v8 docstring deletion closed with evidence (spec §1.5's *"DELETE the stale landing
docstring proposal"*, carrying `era_consistency_survey_v1.md:881`'s **02 landing (L1) = CANCEL**).
Declining it means **no GT row is owed**: a bay re-count would have moved walked surfaces and drop
edges and would have needed a new FULL row.

Both are appended as **Appendix A** of `w3_cb7_v1.md`. **No figure, verdict, table or crop above the
appendix line was edited** — the report's authorship stays intact and the rulings are visibly the
supervisor's.

---

## 2. Verification floor (spec §6.1) — scoped, and the scoping is stated

This batch changes **four Markdown files and no code**, so two of the four floor items have no
subject. Recorded the same way the 07-31 ledger batch recorded its own.

| floor item | result |
|---|---|
| `python3 -m py_compile <files touched>` | **n/a** — no `.py` in any commit |
| `NEGOBS_SMOKE=1 python scenes/<scene>.py` | **n/a** — no scene touched |
| `python3 scripts/geom_invariance_check.py` | **run, unscoped, at `a7842bc`** — see below |
| `python3 scripts/placement_lint.py --scenes all` | **delta 0 by construction** — the commits contain no code, so no lint verdict can move. Not re-run tree-wide; the standing figure at this HEAD is `redteam_lane1.md` §7's isolated-arm sweep (**ERROR 30 · WARN 227 · BLOCK 29**) |

**Scoped runs taken as evidence for specific claims** (each one backs a sentence written into a
row, and none was copied from another report):

```
python3 scripts/geom_invariance_check.py --scenes scene18
   → R-5 ✔ · scene18  979  cc26fd97  cc26fd97  cc26fd97  ✔ · R-4 1/1 PASS · R-6 1/1 PASS
python3 scripts/geom_invariance_check.py --scenes scene04,scene16
   → scene04 1335  d530f155 ×3 ✔     scene16  439  a9d922f5 ×3 ✔ · R-4 2/2 · R-6 2/2 PASS
```

The first backs GT-26's *"hash moved to `cc26fd97` under K4(b)"* note. The second backs MD-8 on both
rows — scene04 reproduces its landed `d530f155` **to the digit**, and scene16's `a9d922f5` is the
K1-path-move value whose path-normalised identity with `4233f62d` the red team proved.

**Unscoped sweep at `a7842bc`** (this batch's HEAD, taken for the record so a later reader does not
have to trust `e8e2895`):

```
python3 scripts/geom_invariance_check.py            # 33 scenes × 3 arms, CPU, rc 0
[R-5] ✔ PASS — LOOK_V1 references outside the compat shim: 0
   arm=mtl0 → 33/33 assembled · arm=mtl1 → 33/33 · arm=v1 → 33/33
scene01  354 6947cb33 | scene02  545 a4c3a5f9 | scene03 1552 d6dde846 | scene04 1335 d530f155
scene05 1235 351f44d1 | scene06 1619 0c077f41 | scene07 1420 f13fbc03 | scene08  688 eac15c7d
scene09  501 840928aa | scene10 2777 f8e2670e | scene11 2222 2f6121eb | scene12  803 847e197c
scene13  495 b0afe7a8 | scene14  860 da26a38b | scene15  433 3a0f63a2 | scene16  439 a9d922f5
scene17  974 5d073f07 | scene18  979 cc26fd97 | scene19  284 4ac6372a | scene20  481 05dbc1c9
scene21  527 a71d79cc | sceneC1 367 e821aa7d | sceneC2 3940 a6a170a6 | sceneC4 638 f815a3f5
sceneD1  341 f13ec42a | sceneD2 236 68845547 | sceneD3  715 6609c2e2 | sceneD4 314 b7ac8403
sceneN1  529 d250bb9a | sceneN2 588 4302306c | sceneN3  666 b8d9a0b6 | sceneN4 1241 11dcec9c
sceneN5 1073 885ea29c
[R-4] MTL 0/1 hash match 33/33  ✔ PASS
[R-6] V1=1 three-arm match 33/33  ✔ PASS
```

**Cross-checks this sweep settles**, all against figures written elsewhere in the tree and all
reproducing: **scene02 545 / `a4c3a5f9`** (CB-7's landed census, `w3_cb7_v1.md` §0 and GT-3's
landing record) · **scene04 1335 / `d530f155`** and **scene10 2777 / `f8e2670e`** (GT-22 and the
S10c closure) · **scene18 979 / `cc26fd97`** (GT-26's post-K4(b) value) · **scene16 439 /
`a9d922f5`** (the K1 path-move value, path-normalised-identical to the landed `4233f62d`). The
sweep is recorded as **evidence for MD-8's closure**, and it is also the third independent
confirmation — after `e8e2895` and `535926e` — that the tree assembles 33/33 with `scene18` in it.

**Sources read for edit, and only these**: `redteam_lane1.md` · `w3_ledger_batch_v1.md` ·
`w3_k4_v1.md` · `w3_k5_v1.md` · `w3_k1t4_v1.md` · `w3_s10_close_v1.md` · `w3_cb7_v1.md` ·
`w3_s18_v1.md` (§8, §9) · `w3_n2_clean_v1.md` §7 · `w3_intake_v2_images.md` §7 (incl. **R16-2
HELD**) · `w3_geom_reverify_v1.md` · `gt_changes_w3.md` · `w3_execution_spec_v1.md` ·
`ground_kit.py` and `scenes/main/scene02_underpass.py` **read-only, for the two census checks**.

---

## 3. Scope — one extension, declared

**MD-1b and MD-2b are an extension of the two mandated spec items, and this section exists so that
it is not discovered.**

The mandate named spec **§1.5** and spec **§9's P-5 row**. §8's **GT-3** and **GT-4** rows carry the
*same* superseded content — GT-3 still read *"Canopy deletion … four posts and a 2.4 × 4.9 m slab
leave every cut"*, GT-4 still read `HELD`/CB-11 with the full re-cache live. Because **the spec
outranks the ledger** (`gt_changes_w3.md` §0: *"This file never overrides it"*), leaving them would
mean a reader following §8 deletes a canopy that CB-7 has already built and holds a row the user
retired. Both are struck in place, both keep their original text, and either is revertible in one
edit if the supervisor did not want the extension.

**What was deliberately NOT touched, though it was in an owned file:**

* `Docs/reports/w3_cb7_v1.md` §0–§11 — appendix only, by instruction.
* `Docs/reports/w3_geom_reverify_v1.md` §0's verdict table and every measured column — the NF-1
  **diagnosis** is correct and reproduces; only the **prescription** is amended.
* spec §1.8 — the ruling that created P-5's evidence gate. It stays as the record of *why* the hold
  existed; killing the parked row does not rewrite the history that parked it.
* spec §1.5's sill build, curb fix and landing-block deletion — all three landed at `6edce66`.
* Every GT row not named above; every lane report; `w3_intake_v2_images.md` (quoted, never edited);
  `s3_scene07_10_rebuild_spec_v1.md`; every scene, kit and script.

---

## 4. What is still open after this batch

Carried forward from `redteam_lane1.md` §8–§9, with this batch's effect marked.

| item | state after this batch |
|---|---|
| **RT-2** — GT-4's deleted clause tail | **CLOSED** (MD-4, restored verbatim) |
| red team §9-1 — spec §1.5 Option-A clause + §9 P-5 unstruck | **CLOSED** (MD-1/MD-1b/MD-2/MD-2b) |
| red team §9-2 — GT-21 §3's `1346b70` clause | **CLOSED** (MD-3) |
| GT-22/GT-23 — unscoped 33/33 owed to the S18 closer | **CLOSED** (MD-8) |
| scene18 GT row owed to the next ledger batch | **CLOSED** (MD-6 → GT-26 `LANDED`) |
| **K4-F3** — T3's NF-1 prescription | **CLOSED** at source (MD-5, both §3 and §7-3) |
| **S02-Q1** · **R02-2** | **CLOSED** (Appendix A: ACCEPTED / DECLINED) |
| **C02-P1** — the planter 1.0 m from a judged eye | **promoted** from a report finding to ledger row **GT-25** `OPEN`; the fix is phase-Code work |
| **RT-1** — terminal-baluster residual opening up to 118 mm (latent; all 16 live sites ≤ 99 mm) | **OPEN**, K-track — not a docs item |
| **D14** — `regression_check.py` still does not read `EXPECTED_FP` | **OPEN**, T1/X — CB-7 is the third live instance |
| **F5** — `260731_w3_s04` / `_s16` / `_s18` stamps carry no `baseline_of_record` marker | **OPEN**, round lane (X1); now recorded on three rows instead of two |
| **S02-Q2** (parapet height vs the perimeter guard on a 3.38 m drop) | **OPEN**, supervisor |
| **R02-3** / **R16-2** tactile | **HELD** until the scene-renumbering round — untouched by this batch, by instruction |
| **K4-F4** (belts inert until S-WPs pass `species=`) · **T4 FU-1/FU-2** · `stamp_round` **F9** root fix | **OPEN**, their named owners |
| **RT-4** — `G2_matched_crop.png` is a reference photo containing pedestrians, under `Docs/reports/` | **OPEN**; recorded in Appendix A-3, not ruled |
| **GT-24** · **GT-25** | **OPEN by design** — declared here, landed by the phase-Code lane, records filled by the supervisor |
| **GT-5 · 7 · 10 · 11 · 12 · 13** | untouched and still `OPEN` — none is a docs item |

---

## 5. Commits

Pathspec per file group, as instructed. No commit touches a path outside the group named in its
message, and no commit contains code.

| commit | pathspec | items |
|---|---|---|
| 1 | `Docs/briefs/w3_execution_spec_v1.md` | 1 (+ the MD-1b/MD-2b extension) |
| 2 | `Docs/audit_v4/gt_changes_w3.md` | 2 · 3 · 4 · 5 (cross-note) · 7 |
| 3 | `Docs/reports/w3_geom_reverify_v1.md` | 5 (at source) |
| 4 | `Docs/reports/w3_cb7_v1.md` | 6 (appendix only) |
| 5 | `Docs/reports/w3_micro_docs_v1.md` | this report |

---

## 6. Reproduction

```bash
# the restored clause, byte-for-byte
git show d71e1e3^:Docs/audit_v4/gt_changes_w3.md | grep -o \
  '\*\*Full re-cache + regr re-baseline\.\*\*.\{0,90\}'

# the S18 lane's last commit, and the sweep that comes after it
git log --oneline -- scenes/main/scene18_wavy_artstair.py Docs/reports/w3_s18_v1.md
git log --oneline 836ed7f..HEAD          # ee6990c … e8e2895 … a7842bc

# the three claims this batch measured itself
python3 scripts/geom_invariance_check.py --scenes scene18
python3 scripts/geom_invariance_check.py --scenes scene04,scene16
python3 scripts/geom_invariance_check.py          # unscoped, §2

# the GT-24 census (profiles + scene-side overrides), read from the tree
python3 - <<'PY'
import re
src = open('ground_kit.py', encoding='utf-8').read()
blk = src[src.find('    "scene01": _S('):]
blk = blk[:blk.find('\n}\n')]
cur, d = None, {}
for line in blk.split('\n'):
    m = re.match(r'\s*"(scene\w+)": _S\("(\w+)"', line)
    if m:
        cur = m.group(1); d.setdefault(m.group(2), []).append([cur, False])
    if cur and re.search(r'surface=\(', line):
        for v in d.values():
            for e in v:
                if e[0] == cur: e[1] = True     # scene-side surface override
for p in ('plaza_granite', 'plaza_water', 'sidewalk_block'):
    print(p, d.get(p))
PY

# GT-25's two live figures
grep -n 'planters=' scenes/main/scene02_underpass.py     # :432  (-8.0, -5.0)
grep -n 'beauty_overview"\] = dict' scenes/main/scene02_underpass.py   # :568  eye (-7,-5,3)
```
