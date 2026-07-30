# MC · D14 — `regression_check.py` learns to read `EXPECTED_FP`

> **Wave** W3 · **Batch** micro, post-Lane-1 corrections · **Date** 2026-07-31
> **Branch** `feat/realism-v1` · **HEAD at start** `e1150d6` → gates re-taken at `59a944e` →
> **this commit's parent** `570623b` (a concurrent lane landed `5340d49` · `8b6baa7` · `59a944e`
> · `570623b` mid-session — §8; the last two are report-only, and every gate was re-taken at
> `59a944e`, the last HEAD that moved code, with the result unchanged)
> **Owns** `scripts/regression_check.py` · this report. **Nothing else was opened for writing.**
> **Law / sources** `w2d_round_v1.md` §3.2 + §7 D14 (the defect, and the two costed options) ·
> `w3_k1t4_v1.md` §1.2 · §1.6 · FU-3 (the 2 scene16 rows, and D14 left parked) ·
> `w3_cb7_v1.md` §7.3 (the third live instance) · `redteam_lane1.md` §9-3 (still open at
> `535926e`) · `redteam_w2d_edits.md` F4 / rider 5 (sceneC4 setback) ·
> `ground_kit_spec_v1.md` §12.3 · §6.2 (GT-E2-x) · `w3_intake_v2_images.md` §7 **R16-2 HELD**
> **Method** CPU only, no GPU, no Isaac, no `flock` needed — this tool renders nothing. Every
> number below was produced by re-running the checker on this machine, never re-read.
>
> **Method note — the dispatch's premise "no other lane is running" turned out to be false.**
> Another workflow began writing this worktree mid-session (§8). Every tree-wide claim below was
> therefore **re-executed on an isolated `git archive HEAD` arm** (assets and `look_check`
> symlinked, this batch's file copied in), the K4M / red-team precedent — never on the shared
> worktree. Both arms are reported where they differ.

---

## 0. Verdict in one table

| # | Item | Verdict | Evidence |
|---|---|---|---|
| **D14** | the adjudicator reads `ground_kit.EXPECTED_FP` | ✅ landed | §1 |
| D14-a | suppression is **exact** `(scene, cut, row-band)` only | ✅ 20-item self-test, incl. both band edges and both misses | §2 |
| D14-b | a waived finding is reported as **`EXPECTED_FP`**, never as `PASS` | ✅ verdict token + summary block + the original text preserved in-issue | §1.3 |
| D14-c | **no collateral** — full re-run over every stored round | ✅ **2,037 cuts, exactly 2 changes, both enumerated register hits**; 0 metric drift | §3 |
| D14-d | kill switch reproduces the pre-D14 output | ✅ `--no-expected-fp` = pre, **2,037 / 2,037 identical** | §3.3 |
| D14-e | the parked "corpus recalibration" risk | ✅ closed **structurally**, not by luck — `valset.py` can no longer see the waiver | §4 |
| — | scene02 sill rows added to the register | ❌ **NOT DONE — BLOCKER**, and the reason is not laziness | §5 |
| — | scene16 `d10` / W2-era `16 d10` waived | ❌ **not covered by the register, correctly** — it is a different line | §6 |
| — | §6.1 floor | ✅ py_compile · self-test · full re-run · geom_invariance **33/33** · placement_lint **Δ0** | §7 |
| — | worktree integrity | ⚠️ **BLOCKER — a concurrent lane is editing `ground_kit.py` live**; proof re-taken on a clean HEAD arm, register proven unaffected | §8 |

**Ownership check, run before a single character was edited.** `git log -- scripts/regression_check.py`
→ last touch **`fc69706`** (W2-D preflight, 2026-07-30 00:25). Nothing in W3 has touched it; the
file has been unowned since W2 exactly as the dispatch said. Working tree was clean
(`git status --porcelain -uall` empty) **at that moment** — it did not stay that way, see §8.
No lane has touched `scripts/regression_check.py` at any point, including the concurrent one.

---

## 1. What landed

### 1.1 The reader, and why it is three rules and not four

`ground_kit.EXPECTED_FP` is a **derived** registry (`_build_expected_fp()` over `TACTILE_SITES` ×
`tactile_fp_rows()`): 18 rows = 9 drop-trigger scenes × `{d5, d10}`, each carrying the row band on
**both** axes — `rows` @1080 (spec §12.3 notation) and `rows_work` @540 (the axis this checker
works on), the latter already widened by the step-response footprint `GRAZE_FOOTPRINT_WORK = 8`.
The reader consumes it and computes nothing of its own — no hard-coded row appears anywhere in
`scripts/`.

```
expected_fp_register()   ground_kit.EXPECTED_FP, imported once per process, 22 ms, silent,
                         numpy-only  ->  the tool's "no GPU, no Isaac" contract survives
expected_fp_match()      exact (scene, cut) key  AND  rows_work[0] <= gz_row <= rows_work[1]
apply_expected_fp()      one post-pass over the finished issue list — the single place in the
                         tool where a finding can be waived
```

The three rules, each of which is a decision that could have gone the other way:

1. **Exact, or nothing.** No fuzzy band, no per-scene tolerance, no "close enough". A registered
   scene whose finding lands outside its registered rows **stays loud** — that is a *different*
   line and must be judged by a human. This is what makes §6 come out the way it does, and §6 is
   the reason the rule is worth stating.
2. **Never `PASS`.** The suppressed issue keeps its full original message, and its original
   severity and code are preserved in the JSON (`issue.was`, `issue.fp`). The cut is labelled
   `EXPECTED_FP`, and the round summary prints a dedicated block listing every waiver. A waiver
   the record does not show would be a worse defect than the false positive it replaces.
3. **No guessing across axes.** If the registry's `scale_work` and the run's actual GRAZE working
   height disagree, **no match is attempted**; the finding stays loud and gains a diagnostic.
   `ground_kit` §7 carries a v1.2 amendment precisely because the register and its consumer once
   lived on different axes (`w2_pilot_ground_v1.md` §1.1, spec A4) — the reader refuses to be the
   place that mistake reappears. To make this checkable at all, `gz_work_h` is now recorded in the
   metrics: `gz_row` is meaningless without the axis it was measured on.

### 1.2 Only findings with a row anchor can ever match

```python
FP_ROW_METRIC = {"GRAZE": "gz_row"}
```

The registry's unit is a **row band**, so only a finding anchored to a row can be matched against
it. Today that is **GRAZE alone**. The dispatch said "GRAZE/OCCL", so this is stated plainly
rather than quietly: **OCCL cannot be waived by this register and no OCCL path was written.**
`newdark`, `newdark_near` and `newdark_blob` are frame-global fractions with no row coordinate —
an "exact row-band match" against them does not exist, and inventing one (e.g. intersecting the
blob's bounding box with the band) would be new adjudication policy, not a reader. The table above
is the honest statement of that, and it is one line to extend the day an OCCL row anchor exists.
The self-test asserts an OCCL finding on a registered row is **not** waived (§2).

### 1.3 What a waiver looks like in the round record

```
총평 — 13 컷 중 FAIL 0 · WARN 4 · EXPECTED_FP 1 · INFO 1 · PASS 7

EXPECTED_FP — GT-E2-x 사전등재로 유보한 소견 1 건 (무시가 아니라 **면제**. 등록부: ground_kit.EXPECTED_FP):
  scene16    preset_h0.3_d5           WARN/GRAZE → EXPECTED_FP  y185 ∈ 166~194@540  (tactile_stair_top)
```

The waiver block prints **unconditionally**, is never folded into the `INFO` count, and is never
removed by `--fail-only`. A cut is labelled `EXPECTED_FP` only when the registry is the **whole**
reason it stopped being loud; if anything else is still WARN/FAIL that grade stands, because the
registry waives *one line*, not the cut. (Measured: CB-7's `scene02 preset_h0.3_d5` would stay
`FAIL` on FRAME + OCCL even if its GRAZE were registered.)

**Exit code.** A cut that was `FAIL` on a registered GRAZE alone now grades `EXPECTED_FP`, so the
gate exit code can legitimately flip 1 → 0. That is the intended effect of closing D14 and is
recorded here rather than discovered later. No stored round actually flips (§3.2).

---

## 2. Self-test — the §6.1 smoke for a `scripts/` file

`python3 scripts/regression_check.py --selftest` (no images, no GPU, exit 1 on any failure).
It runs against the **live** registry rather than a fabricated one, so it also proves the registry
is importable and shaped the way the reader assumes.

```
regression_check EXPECTED_FP 자기검사
  ✔ 등록부 적재  [18 행 · /home/vislab/Desktop/work_sy/Practice_NegObs/ground_kit.py]
  ✔ 작업 축 = 등록부 소비자 축  [540 행]
  ✔ 모든 행이 (lo ≤ hi) 2원소 밴드 + 출처
  ✔ 표본 키 존재 (K1 이 착지시킨 행)  [rows (348, 371) · rows_work (166, 194) · tactile_stair_top]
  ✔ 밴드 하단 경계 포함        ✔ 밴드 상단 경계 포함
  ✔ 밴드 밖(하단−1) 불일치     ✔ 밴드 밖(상단+1) 불일치
  ✔ 다른 씬 불일치             ✔ 다른 컷 불일치
  ✔ 행 없음 → 불일치           ✔ 축 불일치는 매치가 아니라 진단
  ✔ 등재행 GRAZE FAIL → EXPECTED_FP 판정
  ✔ 원 소견 텍스트·등급·코드 보존(감사성)
  ✔ 등재행이라도 PASS 로 죽지 않는다
  ✔ 다른 소견이 남으면 컷 등급은 유지
  ✔ 등재 밖 GRAZE 는 그대로 크게 남는다
  ✔ 행 앵커 없는 코드(OCCL)는 절대 면제되지 않는다
  ✔ 이미 조용한 소견은 건드리지 않는다
  ✔ 작업 축 미기록이면 면제하지 않는다

전 항목 통과
```

The boundary pair (`lo`, `hi` in · `lo−1`, `hi+1` out) is the test that keeps rule 1 honest, and
the last four are the ones that keep the reader from becoming a blanket waiver.

---

## 3. No collateral — the full corpus re-run

**The demand.** The W2-era parked concern was corpus recalibration: wiring `EXPECTED_FP` into the
adjudicator "changes the verdict function that the 250-cut validation corpora calibrate"
(`w2d_round_v1.md` §3.2). So the proof is not an argument, it is a diff.

### 3.1 Method

Every stored `Docs/reports/regr_*.json` was re-executed **twice on the same images**: once with
the pre-change file (`git show HEAD:scripts/regression_check.py`, kept aside before editing) and
once with the landed file. Each round's `pairs` block was converted to a `--list` TSV, so the
re-run reproduces the round's own before→after pairing exactly.

| stored round | cuts | round dirs on disk |
|---|---:|---|
| `regr_r2_on` · `regr_baseline_pre_groundkit` · `regr_260730_w2d` · `regr_260730_w2d_fix` | 452 each | 33/33 |
| `regr_260730_lcfreeze` | 52 | 4/4 |
| `regr_260731_w3_cb2` | 56 | 4/4 |
| `regr_260731_w3_s07` · `_s10` · `_s10c` · `_s18` | 14 each | 1/1 |
| `regr_260731_w3_cb7` · `_cb7_pre` · `_s04` · `_s16` · `regr_260730_w3_n2clean` | 13 each | 1/1 |
| **total** | **2,037** | **no round missing** |

**The pre-change arm reproduces the stored verdicts.** 12 of 15 rounds match the committed JSON
digit for digit. The three that differ do so for reasons that predate this batch and were checked,
not assumed:

* `regr_260731_w3_cb2` (stored 20 vs re-run 56) and `regr_260731_w3_s10` (5 vs 14) were committed
  from `--only`-filtered runs. **All 20 and all 5 common cuts match exactly**; the re-run is a
  strict superset.
* `regr_r2_on` differs on 30 of 452 — it is the **pre-v2 GRAZE** corpus (its `results` carry
  `gz_spec 0.0`, `gz_row null`), captured before the 2026-07-29 recalibration
  (`graze_recalibration_v1.md`). Nothing to do with this batch.

### 3.2 The diff — 2,037 cuts compared on verdict **and** issue set

```
compared cuts: 2037   verdict changes: 2   issue-set changes: 2   metric drift: 0
```

| round | scene · cut | pre | post | issues pre → post | register row |
|---|---|---|---|---|---|
| `regr_260730_w2d` | `sceneC4 preset_h0.3_d5` | **FAIL** | **WARN** | `FAIL/GRAZE` + `WARN/FRAME` → `INFO/EXPECTED_FP` + `WARN/FRAME` | y**173** ∈ 166–194@540 (=348–371@1080), `tactile_stair_top` |
| `regr_260731_w3_s16` | `scene16 preset_h0.3_d5` | **WARN** | **EXPECTED_FP** | `WARN/GRAZE` → `INFO/EXPECTED_FP` | y**185** ∈ 166–194@540, `tactile_stair_top` |

**Nothing else moved.** The comparison is not verdict-only: every cut's `(sev, code)` multiset was
compared, and every metric key was compared with the single new additive key `gz_work_h` excluded.
Both changes are enumerated register hits. Both keep their full original GRAZE text inside the
JSON. `sceneC4`'s cut stays **WARN**, not PASS — its FRAME finding is untouched, which is the
"waives one line, not the cut" rule doing its job in the wild.

Neither round's exit code changes (both remain 1 on other FAILs), so no gate result was altered by
this batch.

### 3.3 The kill switch is byte-exact

`--no-expected-fp` re-run over the same 2,037 cuts, compared against the pre-change arm:

```
pre  vs  --no-expected-fp : identical 2037   differing 0
```

So the pre-D14 behaviour is not merely recoverable from git, it is one flag away at runtime — which
is what a red team will want, and what makes the §3.2 table falsifiable by anyone.

---

## 4. The parked corpus-recalibration risk — closed structurally, and it was **not** inert

This is the one finding of this batch that was not on the dispatch list, and it is the reason the
landed default is what it is.

`scripts/valset.py` — the file that exists so the GRAZE calibration corpora "stop being a
scratchpad artefact" — **imports `regression_check` and calls `check_view` positionally**:

```python
r = rc.check_view(scene, v, bb, aa)                      # valset.py:168
gz = [i for i in r["issues"] if i["code"] == "GRAZE"]    # valset.py:169
sev = gz[0]["sev"] if gz else "PASS"
```

A waived finding becomes `code == "EXPECTED_FP"`, so `gz` empties and the cut silently counts as
`PASS`. Had the reader defaulted on, **a registered row landing in any corpus pair would have
deleted a FAIL/WARN from the corpus that licenses every GRAZE threshold, invisibly** — the exact
recalibration failure W2 parked D14 to avoid. Measured today it does not bite (`--check` passes
either way), but "it happens not to bite" is not a guarantee.

**Landed instead:** `check_view(..., use_expected_fp=False)` — the waiver is a *round-adjudication*
policy, not part of the metric. The CLI opts in; `valset`'s positional 4-argument call therefore
keeps the raw detector **without `valset.py` being edited at all** (it is not this batch's file).
The flag is carried per job rather than in a module global, so its value is identical in the parent
and in every pool worker regardless of start method.

Verification, both directions:

* CLI output after the default flip is **identical on all 2,037 cuts** to §3.2 — the opt-in works.
* `python3 scripts/valset.py --check` → `history` FAIL 1 · WARN 2 · deferred 23 (94 cuts) ·
  `fp` FAIL 0 · WARN 0 (156 cuts) · `t3` FAIL 0 · WARN 0 (8 cuts) — **all three `[ok] matches
  EXPECTED`**, exit 0. The 250-cut corpora are untouched, and now cannot be touched.

---

## 5. BLOCKER — scene02's sill rows were **not** added, and this is a supervisor call

The dispatch said: *"scene02's sill rows: if not yet in the register, ADD them via the proper
register mechanism (not a hardcode) with the CB-7 report as source."* They are **not** in the
register, and they were **not** added. Three reasons, in increasing order of importance.

**First, the measurement — so the next owner does not have to redo it.** CB-7's two firings are
identified, not guessed. Inverting `cam_row` at `h = 0.3`:

| cut | measured `gz_row` @540 | read as **ground** (z = 0) | verdict |
|---|---:|---|---|
| `preset_h0.3_d2` | **181** | 4.41 m — but the edge is 2 m away | no ground feature there |
| `preset_h0.3_d5` | **145** | 11.86 m — but the edge is 5 m away | no ground feature there |

Neither row is explicable as ground at all, which is the clue. Read as elevated geometry instead,
both land on one object. `PARAMS["sill"]` = apron
`x −1.20…0.00`, `top = +0.180`; the drop edge is `x = 0` (scene02 uses `sc.grid_views(0.0)` with
no datum shift). The apron's **far lip at `x = 0, z = +0.180`** projects to
`cam_row_z(d, 0.18, 0.3)`:

| cut | lip row @1080 | @540 | ± footprint 8 | measured | in window |
|---|---:|---:|---|---:|---|
| `preset_h0.3_d2` | 348.6 | 174.3 | **166 – 183** | 181 | ✔ |
| `preset_h0.3_d5` | 287.8 | 143.9 | **135 – 152** | 145 | ✔ |
| `preset_h0.3_d10` | 267.3 | 133.7 | **125 – 142** | (no firing) | — |

Existing scene02 register rows are `d5 (166,194)` / `d10 (140,160)` from `tactile_stair_foot` — a
different band at different rows, which is why the reader correctly leaves both CB-7 firings loud.

**Second, the mechanism does not exist and building it is a `ground_kit.py` refactor.**
`EXPECTED_FP` is derived from `TACTILE_SITES` filtered by `_FP_TRIGGERS`. The sill is a statutory
flood barrier (행안부), an **UP-STEP** that `hazard_registry()` labels as such and that "must never
be written into a drop list" — it is not tactile paving and no `_T(...)` site can express it.
Adding it needs, at minimum: (a) a second registry vocabulary for statutory non-drop transverse
lines; (b) a **schema change** — `("scene02","preset_h0.3_d5")` already exists with different rows,
so a key must carry a *list* of bands, which ripples into `ground_kit.py:2518` and into this
reader; (c) an amendment to `ground_kit`'s own self-check invariant
`len(EXPECTED_FP) == 2 × (drop-trigger scenes)` (`ground_kit.py:3687`), which **any** addition
breaks today. `ground_kit.py` is outside this batch's stated paths, the dispatch's standing
instruction is to stay strictly inside them, and — as §8 discovered — **another lane is editing
that exact file right now**. Merging the sill window into the existing key instead — `(135,194)`
at d5 — would waive **60 of the ~81 rows** of that cut's whole E band (`y 130.6…211.8`): a blanket
amnesty wearing a registry's clothes. It was considered and rejected.

**Third, and decisive: the sill firing is not the same failure class as a tactile band, and
registering it would buy a real blind spot.** The GT-E2-x semantic is *"the transverse line at
these rows is a mandated tactile band, **not the drop edge**"*. Here the line **is** the drop edge —
raised 0.18 m. CB-7 §7.3's own numbers say so: at the old drop row the step collapses
`54.3 → 2.0 (ratio 0.04)` while a new line appears 30 rows higher. The detector is reading a
**relocated** drop edge as a buried one. Registering rows 135–152 / 166–183 as expected false
positives would make the checker permanently blind to burial at exactly the rows where scene02's
drop cue now lives — on the library's flagship *"from a low viewpoint the pit reads as completely
flat ground"* scene. That is a detection-power trade, and this batch has no mandate to make it.

**Two options, costed, for the supervisor:**

* **(a) Re-baseline, and register nothing.** GRAZE measures *change between rounds*. The sill is a
  one-time geometry event: once `260731_w3_cb7` is scene02's baseline-of-record, post-sill vs
  post-sill has no moved line and nothing fires. Cost: zero code. Risk: a future round that
  resolves scene02 back to a pre-sill round through the `--before-round` fallback chain
  (`look_check/README.md` §4) re-manufactures it — the same trap `w3_n2_clean_v1.md` §8 flagged for
  sceneN2. **Recommended.**
* **(b) Build the second registry** — vocabulary + list-valued bands + self-check amendment, in
  `ground_kit.py`, by its owner, with the §5 table above as the source and CB-7 §7.3 as the
  rationale. The reader landed here consumes it **unchanged** the day the rows appear: it reads
  `rows_work` from whatever `EXPECTED_FP` contains. Cost: a `ground_kit` refactor + a re-run of
  §3. Buys: immunity to the fallback-chain trap. Pays: the blind spot above.

---

## 6. The other two cited instances are **not** register hits, and the register is right

The dispatch enumerated `scene16 preset_h0.3_d10 rows (140,160)` and the "W2-era known-legit 16
d10". They are the same case, and it did **not** flip. That is correct, and the arithmetic says why.

* The register's `scene16 d10 (140,160)@540` describes the **stair-head** band added by GT-23
  (`x −0.90…−0.30` → ground 9.1–9.7 m from a 10 m eye → rows 151.5–149.8, widened ±8). **No stored
  round contains a loud d10 GRAZE from that band** — it is a register row waiting for a firing,
  not a live instance.
* The only live `scene16 d10` firing (`regr_260730_w2d`, FAIL spec 23.40) sits at **row 176**,
  which inverts to 4.84 m from the eye = `x = −5.16` — the tail of the **far / entrance** band
  (`x −6.00…−5.40` → rows 186.9–178.7, footprint ±8 → 170.7–194.9). `w2d_round_v1.md` §3.2
  attributed it to exactly that band by a `NEGOBS_GKIT=0` twin arm. It is a **different object**,
  32 rows away from the registered band.
* The registry declines to register it **by its own rule**: the far band's trigger is `주출입구`,
  not in `_FP_TRIGGERS`, and `TACTILE_SITES` marks it `★ 낙차와 무관 — cue+/label−`. Registering
  it now would also pre-empt a **held user decision**: `w3_intake_v2_images.md` §7 **R16-2** kills
  the door-front rationale outright and re-anchors the band to a 횡단보도, with **EXECUTION HELD**
  until the scene-renumbering round. Writing a registry row for a band whose statutory basis the
  user has just retired is the last thing this batch should do.

This is rule 1 of §1.1 earning its keep: a fuzzy or per-scene-widened match would have swallowed
row 176 into the stair-head band's window and reported a clean flip. It stays loud instead.

`sceneC4 d5` (§3.2) did flip, and one honest qualifier goes with it: **F4 / rider 5 remains open**
— the register computes C4's rows at the nominal **0.30 m** setback while the scene ships the
**1.00 m** position-error defect, whose true rows the red team measured at d5 `(348,374)@1080`
(→ `(166,195)@540`) and d10 `(297,308)` (→ `(140,162)`). Row 173 falls inside **both** windows, so
this particular waiver is correct either way; F4 is not closed by this batch and stays a supervisor
item.

---

## 7. §6.1 floor — run **twice**, on both HEADs

Once in an isolated `git archive e1150d6` arm (because the shared worktree was dirty at the time,
§8), then again on the worktree at the commit HEAD `59a944e` after the concurrent lane landed.
**Every gate gives the same answer in both.**

| gate | result |
|---|---|
| `python3 -m py_compile scripts/regression_check.py` | ✔ |
| SMOKE for touched scenes | **none touched** — no scene, kit or asset file was opened. Per the dispatch, the substitute is the self-test + the full re-run below |
| `python3 scripts/regression_check.py --selftest` | ✔ **전 항목 통과** (20 items), both HEADs — §2 |
| full re-run over all stored rounds | ✔ **2,037 cuts · 2 changes · 0 metric drift** — same two rows in the `e1150d6` arm and at `59a944e` — §3 |
| `python3 scripts/valset.py --check` | ✔ `history` 1F/2W · `fp` 0/0 · `t3` 0/0, all `[ok] matches EXPECTED`, exit 0, both HEADs — §4 |
| `python3 scripts/geom_invariance_check.py` (unscoped) | ✔ **R-4 33/33 · R-6 33/33 PASS** on both. scene04 **1335 / `d530f155`**, scene16 **439 / `a9d922f5`**, scene18 **979 / `cc26fd97`** identical on both and equal to `redteam_lane1.md`. **scene02 moves `545 / a4c3a5f9` → `543 / 8ac2fa99`** — that is the concurrent lane's **GT-25** landing (`5340d49`), not this batch: no file this batch touched can move a prim (below) |
| `python3 scripts/placement_lint.py` | **ERROR 30 · WARN 337 · BLOCK 29 · INFO 2** — **delta 0**, byte-identical totals on both HEADs |

**The placement_lint delta claim is structural, not a before/after eyeball.** `regression_check.py`
is imported by exactly one module in the tree (`scripts/valset.py`, §4) and by no scene, kit or
asset file — `grep -rn regression_check --include=*.py` returns comments everywhere else. It
cannot move a prim. The absolute counts are recorded so the next batch has a baseline.

**Not hidden:** the *first* invocation of the unscoped `geom_invariance_check` — run on the shared
worktree before §8 was discovered — aborted at the `mtl0` arm with an empty stdout **and** empty
stderr (the worker subprocess was killed, not a Python error). It did not reproduce, in either
tree. Recorded as a transient harness abort on this machine, not a finding — but recorded, because
a green re-run after a red run is exactly the thing a reader is entitled to know about.

---

## 8. BLOCKER — the worktree is **not** exclusive, and the file this reader depends on is being edited

The dispatch opens with *"No other lane is running"*. It is not so. `git status --porcelain -uall`
was **empty** when this batch started and, without a single write from this batch outside its two
paths, went to:

```
 M ground_kit.py                       (+215 / −9)   mtime minutes old, still moving
 M scenes/main/scene02_underpass.py    (+23)
?? assets/assets                                     → appeared and vanished within the session
A  Docs/reports/w3_mb_patch_v1.md      (staged in that lane's index)
?? Docs/reports/regr_260731_w3_gt25.json
```

and then, still mid-session, that lane **committed three times**:

```
5340d49  GT-25 착지 — scene02 planters[0] (-8.0,-5.0) → (-11.0,-5.0)
8b6baa7  GT-24 패치 어휘 정리 — 단위포장 3종의 ("patch", n) 행 삭제        [ground_kit.py +224]
59a944e  MB 보고서 착지 기록 보강
```

The scene02 edit is the **GT-25 / C02-P1 planter move** that `w3_cb7_v1.md` §8.1 handed on and
that the ledger still declares **OPEN**; it cites a report `w3_md_reverts_v1.md` which appeared on
disk only later and is untracked. So a `w3_mb_patch` / `w3_md_reverts` lane is live in this
worktree and is shipping into `ground_kit.py`.

**Why this batch caught it rather than shipping past it.** The first tree-wide
`geom_invariance_check` gave **scene02 543 / `8ac2fa99`**, while `w3_cb7_v1.md` §1 and
`redteam_lane1.md` §0 both record **545 / `a4c3a5f9`** — with `git diff --stat 535926e..HEAD -- '*.py'`
**empty**. A prim-count drift with no committed code change is not a thing that happens; chasing it
found the concurrent lane. In the clean HEAD arm scene02 reads **545 / `a4c3a5f9`**, reproducing
both reports exactly, so the drift is entirely the in-flight edits. sceneN1 (528 → 529 in the arm),
sceneN3 (665 → 666) and sceneN5 (1071 → 1073) move the same way.

**Why this batch's result stands anyway.** The reader's *only* input from that file is
`EXPECTED_FP`. It was dumped from the clean `e1150d6` arm and from the live tree and compared
field by field **three times** — before that lane's last write, after it, and after its three
commits landed:

```
ARM  (e1150d6)  register rows: 18   sha256 3041e031f5c56adb
LIVE (59a944e)  register rows: 18   sha256 3041e031f5c56adb
REGISTER IDENTICAL: True
```

and `git diff e1150d6..59a944e -- ground_kit.py` matches **0** lines mentioning `EXPECTED_FP`,
`TACTILE_SITES`, `_FP_TRIGGERS`, `tactile_fp_rows` or `_build_expected_fp` — its 224 lines are
`DECAL_Z_ORDER`, `GROUND_DIMENSIONS`, `build_patch_field`, `GROUND_PROFILES`,
`TACTILE_OFF_REASON` and `_compose_ops`. The §3 corpus proof was run to completion **in the clean
arm and again at `59a944e`**: both give 2,037 cuts, 2 changes, the same two rows.

**What the supervisor needs to decide.** (1) Whether `w3_mb_patch` is sanctioned — if so the
"no other lane is running" line in the dispatch is stale and the next batch must not trust it
either; two agents editing one worktree is how a pathspec slip becomes a lost commit.
(2) That lane ships into `ground_kit.py`, the registry's home: **if a future diff reaches
`TACTILE_SITES` / `EXPECTED_FP`, §3's no-collateral proof must be re-run before it lands** — the
command is in §11, it is CPU-only and takes about four minutes.
(3) This batch committed **pathspec-only**, so nothing of that lane's was consumed or disturbed —
verified after the fact in §9.

---

## 9. Files

| path | change |
|---|---|
| `scripts/regression_check.py` | +297 / −11. Module docstring note · `FP_ROW_METRIC` + `expected_fp_register` / `expected_fp_match` / `apply_expected_fp` · `gz_work_h` metric · `check_view(..., use_expected_fp=False)` · `EXPECTED_FP` verdict token, widened verdict column, summary waiver block · `--no-expected-fp` · `--selftest` + `selftest()` |
| `Docs/reports/w3_mc_d14_v1.md` | this report |

**Not touched:** `ground_kit.py` (§5, §8) · `scripts/valset.py` (§4) ·
`Docs/audit_v4/gt_changes_w3.md` · any scene, kit or asset · `look_check/**` (read-only
throughout) · every committed `Docs/reports/regr_*.json` — the re-runs of §3 wrote **only** to the
session scratchpad and to the isolated arm. No humans, no vehicles. English comments in the edited
module, Korean runtime strings preserved.

**Commit hygiene, given §8.** `git add` + `git commit -F <msg> --` restricted to exactly the two
paths above. At no point were the concurrent lane's files staged: its `ground_kit.py` /
`scene02` index entries and its untracked `regr_260731_w3_gt25.json` ·
`w3_md_reverts_v1.md` were never added, and it committed them itself (`5340d49` … `570623b`)
before this commit landed. Verified by `git show --stat HEAD` — **2 files, both this batch's** —
and by `git status` reading clean afterwards.

---

## 10. Handed on

| id | item | owner |
|---|---|---|
| **D14-B1** | **scene02 sill rows** — choose §5 option (a) re-baseline or (b) build the second registry. Rows computed in §5; the landed reader consumes them unchanged if (b) is taken | supervisor → `ground_kit` owner |
| **D14-B2** | `scene16` far-band `d10` GRAZE stays loud on any round baselined before GT-23. Deliberate: R16-2 is **HELD** and the band's statutory basis is being replaced. Revisit at the scene-renumbering round, not before | supervisor |
| F4 / rider 5 | sceneC4 register rows are nominal-setback, not the shipped 1.00 m defect. Not closed here (§6) | supervisor |
| D14-B3 | `look_check/README.md` §4 `--before-round` fallback chain still has `260730_w2d_judge` at its head; `260730_w3_n2clean`, `260731_w3_cb7`, `260731_w3_s16`, `260731_w3_s18` are baselines-of-record that the chain does not name. Every re-manufactured GRAZE in §3 traces to a stale resolution. README is outside this batch's paths | supervisor |
| D14-B4 | `valset.py` counts by `code == "GRAZE"` (§4). Insulated by default-off, but if a future caller opts in, the count must be taught about `EXPECTED_FP` first | whoever opts `valset` in |
| **D14-B5** | **A `w3_mb_patch` lane is editing `ground_kit.py` (+215) in this worktree while the dispatch says no lane is running** (§8). Sanction it or stop it; if its diff ever reaches `TACTILE_SITES` / `EXPECTED_FP`, re-run §3 before it lands | supervisor |
| D14-B6 | That lane is also shipping the **GT-25 / C02-P1** scene02 planter move that the ledger still declares `OPEN`, and cites `w3_md_reverts_v1.md`, which is not on disk (§8) | supervisor / ledger owner |

## 11. Reproduction

```bash
# §8 — the worktree is shared, so every tree-wide number was taken in an isolated arm
git archive HEAD | tar -x -C <arm>
rm -rf <arm>/assets <arm>/look_check
ln -s $PWD/assets <arm>/assets ; ln -s $PWD/look_check <arm>/look_check
cp scripts/regression_check.py <arm>/scripts/regression_check.py     # the only file this batch owns
# register identity, arm vs live worktree — the reader's sole ground_kit input
python3 -c "import ground_kit,json,hashlib; print(hashlib.sha256(json.dumps({f'{k[0]}|{k[1]}':{a:(list(b) if isinstance(b,tuple) else b) for a,b in v.items()} for k,v in ground_kit.EXPECTED_FP.items()},sort_keys=True).encode()).hexdigest()[:16])"
#   -> 3041e031f5c56adb in both

python3 -m py_compile scripts/regression_check.py
python3 scripts/regression_check.py --selftest            # 20 items, exit 1 on any failure
python3 scripts/valset.py --check                         # 3 corpora, exit 0
python3 scripts/geom_invariance_check.py                  # 33/33 R-4 + R-6
python3 scripts/placement_lint.py                         # ERROR 30 · WARN 337 · BLOCK 29 · INFO 2

# the §3 no-collateral proof — one --list TSV per stored round, built from its own `pairs` block
git show HEAD:scripts/regression_check.py > /tmp/rc_pre.py
for n in Docs/reports/regr_*.json; do  # pairs -> "<scene dir>\t<before round>\t<after round>"
  python3 - "$n" > /tmp/$(basename $n .json).tsv <<'PY'
import json,os,sys
for x in json.load(open(sys.argv[1]))['pairs']:
    if x.get('after'):
        print(f"{os.path.dirname(x['after'])}\t{os.path.basename(x.get('before') or '')}\t{os.path.basename(x['after'])}")
PY
done
# then, per TSV:  pre arm / landed arm / landed arm with --no-expected-fp
python3 /tmp/rc_pre.py                 --root $PWD --list <tsv> --json <pre.json>  --fail-only
python3 scripts/regression_check.py    --root $PWD --list <tsv> --json <post.json> --fail-only
python3 scripts/regression_check.py    --root $PWD --list <tsv> --json <off.json>  --fail-only --no-expected-fp
# diff pre vs post on (verdict, sorted (sev,code) multiset, metrics minus gz_work_h) -> 2 changes / 2037
# diff pre vs off  on the same                                                       -> 0 changes / 2037
```
