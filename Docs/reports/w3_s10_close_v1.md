# W3 · S10c — scene10 season closure, round re-baseline, GT-18…21 landed

> **Wave** W3 · **Lane** 1 (kit revival + closures) · **Track** S10c · **Date** 2026-07-31
> **Branch** `feat/realism-v1` · **Baseline HEAD at launch** `e8e2895`
> **Files this task wrote**: `scenes/main/scene10_park_deck_switchback.py` ·
> `Docs/reports/regr_260731_w3_s10c.json` · `Docs/reports/_w3_s10c_crops/` (3 montages) ·
> `Docs/audit_v4/gt_changes_w3.md` (**landing records only**, rows GT-18…21) · this report ·
> round directories + stamps under `look_check/` (gitignored).
> **No shared module. No other scene file. No humans, no vehicles.**
>
> **Commits**, in order: `a8e8343` (the F1 leaf-off fix) · this report's commit.
>
> *Clock note*: the machine clock reads 2026-07-30, so every `round_stamp.json` carries a
> `stamped_at` of `2026-07-30T18:xx`. The round family and the ledger dates are `260731` /
> 07-31 on the lane's own convention (`260731_w3_s10` was stamped the same way). Stated so
> nobody reads the stamps as stale.

---

## 0. Headline

| # | obligation | result |
|---|---|---|
| **1** | flip scene10's 12 leaf-off trees onto the **fixed** K4-0 mechanism | done — `sc.veg_wrapper_rel` → `assets/veg_bare/*_bare.usda`; isolated arms: **2777 rows both, 12 differ, all reference-string, 0 differ in path/type/xformOp/shape-attr** |
| **1** | **verify in pixels** that the foliage is gone (`from_below` + `h1.8_d10`) | done — §2. Green-pixel share on `from_below` **8.18 % → 0.00 %**; the three montages are committed under `Docs/reports/_w3_s10c_crops/` |
| **2** | re-render the full judged preset round, stamp as the new baseline-of-record | **`260731_w3_s10c`**, 14 cuts, arm byte-identical to `260731_w3_s10`; `baseline_of_record: true` |
| **2** | regression declaring **only** the foliage delta | declared and **proven**, not asserted: a pre-fix intermediate round at the same HEAD makes the Lane-1 kit window measurably null (§3.1), and the verdict set is identical against either baseline |
| **3** | R-2 `run_data_render --run 260731_data_s10 --scenes scene10` + `check_data_run` | done — 8 cuts, checks **[2] [3] [4] [5] all PASS**, `[1]` partial with exactly the two GT-14 zero-sample FAILs (§4) |
| **3** | close GT-18/19/20/21 to `LANDED` with the **exact** commands | done — ledger §4, four records, each carrying the invocation actually run |
| **4** | `baseline_of_record` marker on the `260731_w3_s07` stamp (RT **F5**) | done, and carried on the new s10c stamp; RT **F9** answered for this round with `dirty_paths` |
| — | §6.1 floor | `py_compile` ✔ · `NEGOBS_SMOKE=1` rc 0, selfcheck all-OK ✔ · `geom_invariance_check` **unscoped 33/33** R-4 + R-6 ✔ · `placement_lint` verdict delta **0** ✔ |

**The one sentence.** The red team's F1 was right in the pixels as well as in the semantics:
`260731_w3_s10` printed `잎-off 12/12` and rendered twelve trees in full green leaf. The fix is
one function; the work was proving that it changed **nothing else**.

**Bonus, not owed by this task but true at this HEAD**: the tree-wide `geom_invariance_check`
now completes **33/33** — `scene18` assembles. GT-22 and GT-23's records each carry an "owed to
whoever closes the S18 lane" note about that sweep; this is the sweep, reproduced at `e8e2895`
(scene04 1335 `d530f155`, scene18 979 `cc26fd97`). Recorded here as **evidence**, not as closure
of somebody else's row — those rows are not mine to edit.

---

## 1. The fix

### 1.1 What was actually wrong

`_bare_tree` referenced the **leafed** asset, called `_deactivate_seasonal` on
`{path}/Asset/leaves`, then made `{path}/Asset` instanceable. USD discards opinions on
descendants of an instance **regardless of authoring order** (`redteam_s0710_rebuild.md` §1.2,
re-proven by K4(0) on four species). The stage accepted the deactivation, the counter printed
12/12, and the composed prototype still carried `leaves`. **The counter had been counting
authored opinions, never composed results** — which is why the defect survived a self-check, a
lane report and a landing record before eyes caught it.

### 1.2 What landed (`a8e8343`)

```python
wrel = sc.veg_wrapper_rel(rel, sc.BARE_SUBPRIMS.get(rel), kind="bare")
xf = sc.add_vegetation(stage, path, wrel or rel, ...)      # reference the WRAPPER
stage.GetPrimAtPath(f"{path}/Asset").SetInstanceable(True)  # prototype has no leaves
```

Three decisions worth their line in this report:

* **`native` stays the caller's value.** `PARAMS['season']['bare']` already carried the
  trunk-only zmax (3.299 / 3.043 / 13.422). Re-sourcing it from `sc.BARE_NATIVE`
  (3.2960 / 3.0424 / 13.4221) would have been tidier and would have moved every trunk by up
  to 0.09 % of its height — a real, avoidable pixel delta in a round whose whole claim is
  "foliage only". The scale factor `target_h / native` is therefore **bit-identical across the
  fix**, and the self-check asserts the two agree within 5 mm so the divergence cannot rot.
* **The fallback trigger was wrong and is corrected.** `_bare_tree` returned a single int that
  conflated "asset placed" with "leaf-off achieved", so a missing wrapper would have thrown
  away twelve real trunks and replaced the whole row with procedural blobs. It now returns
  `(placed, bare)`; the procedural fallback fires on `placed == 0` only, and a wrapper miss
  prints a loud warning instead.
* **The self-check now asserts the mechanism, not the registry.** Membership in
  `sc.BARE_SUBPRIMS` was already asserted before the fix — and was **true while the trees
  rendered green**. What has to be checked is that the *reference target* is the wrapper:

```
잎-off 경로 = 참조 래퍼 3/3종 → OK : Gray_Birch_bare.usda, Elm_Sapling_bare.usda, Lombardy_Poplar_bare.usda
native_h ↔ sc.BARE_NATIVE 일치(≤5 mm) → OK : Gray_Birch 3.2990/3.2960 · Elm_Sapling 3.0430/3.0424 · Lombardy_Poplar 13.4220/13.4221
```

### 1.3 Proof that nothing else moved

Isolated `git archive` arms (K4M/RT precedent — never the shared worktree, which carries other
lanes' in-flight files; `dirty_paths` on the round stamp names them):

| check | result |
|---|---|
| inventory rows, arm A (`e8e2895`, pre-fix) vs arm B (fixed) | **2777 both** |
| prim count | **2777 → 2777**, unchanged |
| rows differing | **12** |
| of which differ in **path / type / xformOp / shape-attribute** | **0** |
| of which differ in the **reference string only** | **12** — every one `…/Tree_n/Veg/Asset`, `Trees/<species>.usd` → `../veg_bare/<species>_bare.usda` |
| `geom_invariance_check --scenes scene10` | R-4 1/1 · R-6 1/1, hash `ae8b49ff` → **`f8e2670e`** |
| `geom_invariance_check` unscoped | **R-4 33/33 · R-6 33/33** |
| `placement_lint --scenes scene10` | ERROR **0 → 0** · WARN **9 → 9** · BLOCK **1 → 1**; the *only* textual delta is the species census, `Gray_Birch x4` → `Gray_Birch_bare x4` (this is K4-**F5** arriving in a scene, verdict delta 0) |

The hash moves and the prim count does not, which is exactly the signature of a
reference-target swap. `f8e2670e` supersedes GT-21's landed `606edef7` for scene10.

---

## 2. Pixels — the check the red team actually asked for

The red team's F1 was found by eyes, and a semantic argument is not an answer to it. Both cuts
it named were re-rendered pre-fix and post-fix at the same HEAD and cropped side by side
(`Docs/reports/_w3_s10c_crops/`, montages are PRE on top / POST below):

| montage | question | answer |
|---|---|---|
| `s10c_from_below_leafoff.png` | the near-field trail tree — canopy or armature? | **armature.** Full green birch canopy → white bare trunk with fine twig structure; the dappled leaf-shadow on the deck post becomes a hard shadow |
| `s10c_h1.8_d10_upperleft_leafoff.png` | the upper-left canopy mass | **armature**, same read at grid distance |
| `s10c_h1.8_d10_juniper_vs_deciduous.png` | **the control** — do the evergreens stay green? | **yes.** `Chinese_Juniper` keeps its needles beside two now-bare deciduous trees. GT-21's far-belt re-assignment is intact and was not collateral damage |

A crude green-pixel census over all 14 cuts, identical metric on both arms (G dominant over R
and B by ≥12 LSB and G > 45), so only the ratio matters:

| cut | pre % | post % | | cut | pre % | post % |
|---|---|---|---|---|---|---|
| `from_below` | **8.18** | **0.00** | | `preset_h1.8_d10` | 1.55 | 0.00 |
| `preset_h1.8_d5` | 1.44 | 0.00 | | `preset_h1.8_d2` | 1.21 | 0.00 |
| `preset_h0.9_d10` | 0.89 | 0.01 | | `preset_h0.9_d2` | 0.54 | 0.00 |
| `preset_h0.3_d10` | 0.42 | 0.18 | | `preset_h0.9_d5` | 0.39 | 0.01 |
| `preset_h0.3_d2` | 0.15 | 0.00 | | `preset_h0.3_d5` | 0.14 | 0.09 |
| `reversal` | 0.03 | 0.00 | | `broken_rail` | 0.10 | 0.10 |
| **`through_treads`** | **5.06** | **5.02** | | `leaf_edge` | 0.01 | 0.01 |

`through_treads` holding 5.0 % is the census proving itself honest: that cut's green is the
evergreen belt and the tinted hedges, not the trail trees, and the fix does not touch them.

---

## 3. The round

### 3.1 STEP-0 — the attribution round, and why it was not optional

`260731_w3_s10` was rendered at `e3619df`. Between then and `e8e2895` the Lane-1 kit window
landed **K4(a) baluster gate · K4(b) species · K4(c) `props_kit` · K4(d) arc/helix · K5
`build_curb_line` · K1 micro · T4 MDL chain**, and K4(b) in particular re-draws the RNG stream
inside `place_shrubs` (K4-**F2**), which scene10 uses for its 13 shrub clumps. Diffing s10c
straight against s10 would have blamed the foliage fix for whatever that window did — spec
§6.4 trap 2, the same trap `260731_w3_pre10` was invented to avoid.

**`260731_w3_pre10c`** — scene10 at `e8e2895`, **pre-fix**, same 14 cuts, same arm.
Against `260731_w3_s10`:

> **FAIL 0 · WARN 0 · INFO 7 (CAPTURE-class) · PASS 7 — 회귀 없음.**

The whole kit window is **null on scene10's judged cuts**. Everything below is therefore the
foliage fix, and the claim is measured rather than asserted.

### 3.2 The judged round — `260731_w3_s10c`

14 cuts, `NEGOBS_CAPTURE_MODE=pt · PT_FAST · LOOK_V1 · DETAIL_SCALE 2 · ROUGH_GAIN 0`, view
list byte-identical to `260731_w3_s10`, 50 s under `flock -w 7200 /tmp/negobs_gpu.lock`.
`Docs/reports/regr_260731_w3_s10c.json`.

**Declared before the render: FRAME movement on the tree-bearing cuts, and nothing else.**
Result — **FAIL 1 · WARN 7 · INFO 3 · PASS 3**, every FAIL and every WARN a `FRAME` code:

| cut | verdict | block shift | dark % before → after | new-dark % | blob % |
|---|---|---|---|---|---|
| `from_below` | **FAIL** | **56.3** | 7.30 → **4.99** | 0.028 | 0.005 |
| `preset_h1.8_d10` | WARN | 19.4 | 3.41 → **1.57** | 0.012 | 0.005 |
| `preset_h1.8_d2` | WARN | 11.1 | 4.36 → 3.12 | 0.001 | 0.000 |
| `preset_h1.8_d5` | WARN | 9.0 | 3.35 → **1.42** | 0.010 | 0.005 |
| `preset_h0.9_d10` | WARN | 6.9 | 2.39 → **1.11** | 0.010 | 0.005 |
| `reversal` | WARN | 4.9 | 6.40 → 6.14 | 0.001 | 0.000 |
| `preset_h0.3_d10` | WARN | 4.2 | 1.22 → 0.69 | 0.001 | 0.000 |
| `preset_h0.9_d5` | WARN | 2.8 | 2.05 → 1.16 | 0.004 | 0.000 |
| the other 6 | PASS/INFO | ≤ 0.7 | all down | ≤ 0.006 | 0.000 |

Channels that still mean something, all 14 cuts: **DARK falls on every single cut** (a canopy
that leaves the frame takes its shadow with it — the reverse would have been the alarm),
**255-clipping 0.000 % everywhere**, **WHITE max 0.96 %** (`from_below`, +0.57 pp: hillside seen
through the bare armature), **OCCL max new-dark 0.028 % and max blob 0.005 %** against
`260731_w3_s10`'s own 2.1 % / 1.0 % OCCL flag. **Zero OCCL flags, zero DARK flags, zero
BLOWN/WHITE flags.**

`from_below` is the declared FAIL: it is the cut framed on the near-field birch, so removing
that birch's canopy moves 56 % of its blocks. The verdict is correct and the cause is the
deliverable.

**Attribution, stated as a number.** Re-running the same comparison against `260731_w3_pre10c`
instead of `260731_w3_s10` returns the **identical verdict set** — FAIL 1 `from_below`, the same
7 FRAME WARNs, same cuts. The kit window contributes nothing to any of them.

### 3.3 near-ground band (`--gate`, h0.3 triple)

| cut | sd | mean | wht % | flat_gnd | σ_LF |
|---|---|---|---|---|---|
| `h0.3_d2` | 36.7 → **36.7** | 181 → 181 | 7.6 → **7.8** | 0.4 → 0.4 | 2.94 → 2.93 |
| `h0.3_d5` | 28.7 → 28.5 | 133 → 133 | 0.2 → 0.2 | 0.0 → 0.0 | 3.88 → 3.83 |
| `h0.3_d10` | 23.0 → 22.9 | 136 → 136 | 0.2 → 0.2 | 0.0 → 0.0 | 2.49 → 2.48 |

The judged near band does not move, which is what a canopy fix on a scene whose h0.3 band is
deck and litter ought to do. **The two `h0.3_d2` WARNs GT-18 declared are still here and are
still not tuned away** (mean 181 > 170 and wht % 7.8 ≥ 2 — at 2 m the near band is the deck at
its measured 2–5 yr patina albedo under a 49.8° sun), and `σ_LF < 5` on all three is the same
far-field-terrain shortfall the baseline carried. Delta on every gate: none.

---

## 4. R-2 — the re-cache GT-18 recorded as owed

```
flock -w 7200 /tmp/negobs_gpu.lock →
  python3 scripts/run_data_render.py --run 260731_data_s10 --scenes scene10
  python3 scripts/check_data_run.py 260731_data_s10
```

Defaults (`--conds L0 --cams 8 --seed 20260730`) — the same arm scene07's `260731_s07_recache`
used, so the two re-caches are comparable. Run at `a8e8343`, i.e. **at the fixed code**, which
is the point of a re-cache. **8 cuts · 2.34 s/cut · `dataset/_archive/scene_dev_2607/260731_data_s10/test/scene10/`**
(scene10 is a `test`-split scene; scene07 was `train` — `variation_kit`'s assignment, not a
choice made here).

| check | result |
|---|---|
| **[1]** exposure sanity | luma-in-band, dark share, clip share **PASS** 8/8 · **2 FAILs**, both zero-sample — see below |
| **[2]** azimuth ledger | **PASS** — `|d_az| 0.3–34.5` inside the 35 allowance, class C′; per-condition `hdri_sun_rotz_offset` present; sun elevation tracks the sky |
| **[3]** camera placement | **PASS** on all 8 sub-checks — `ground_below == h_rel` worst \|err\| **0.0000 m**, nearest solid to any eye **0.175 m ≥ 0.15**, every sampler truncation respected, focal↔hFOV worst 5e-06 |
| **[4]** file / manifest | **PASS** — 8 files / 8 records, all content-unique, all 1920×1080, **nothing written under `look_check/`** |
| **[5]** throughput | **PASS** — 2.34 s/cut against SP-3's 2.87 |

**The 2 FAILs are the GT-14 convention, recorded and not fixed** (task instruction, and §0-3's
"record the command, do not guess it" applied to results):

```
[FAIL] sun-bearing: ground darkens with net EV, per scene (0 pairs >= 0.3 EV apart) — no comparable pair
[FAIL] sunless: less deep shadow than the L0 reference (0 scene-pairs)
```

Both are **cross-condition** checks with **zero samples**: the run has one condition (`L0`), so
there is no pair ≥ 0.3 EV apart and no sunless scene-pair to compare. They are an artefact of
the mini scope, identical in text and cause to the two that `260731_s07_recache` produced, and
they say nothing about scene10's geometry. Curing them needs `--conds` > 1, which is a
data-channel decision, not an S-lane one. **They are not a reason to hold GT-18…21 open**, and
they are not a licence to widen the scope quietly either — the row records them verbatim.

---

## 5. Stamps

| stamp | change | why |
|---|---|---|
| `scene10/260731_w3_s10c` | `baseline_of_record: true` · `supersedes` · `comparison_baseline_used` · `attribution_round` · `dirty_paths` · note | the new baseline of record |
| `scene10/260731_w3_pre10c` | `baseline_of_record: false` · `role: intermediate` · note | an attribution arm must not read as a judgement round |
| `scene10/260731_w3_s10` | `baseline_of_record: false` · `baseline_of_record_until` · `superseded_by` · note | two rounds cannot both claim the title. Its original note is **kept unedited** |
| `scene07/260731_w3_s07` | `baseline_of_record: true` · `supersedes` · `comparison_baseline_used` · note | **RT F5 closed.** Nothing re-rendered, no pixel touched — three keys and a note |

`260731_w3_s07`'s status was always real (GT-14's landing record, `w3_s07_rebuild_v1.md`, the
commit message, and `regr_260731_w3_s07.json`'s own `pairs` block all say so); what was missing
was the marker on the artefact a later lane reads *first*. That is exactly why F5 was raised and
it is now discharged.

**RT F9, answered for this round only**: the s10c stamp carries `dirty_paths`, not just a count,
so a reviewer can see that the dirty files at stamp time were `scenes/main/scene02_underpass.py`
(another lane's in-flight file) and this task's own regression JSON. The general fix belongs in
`scripts/stamp_round.py`, which is the **tooling track's** file — an S-lane rewriting it would be
exactly the ownership violation the wave is organised to prevent. `env_source` is likewise
recorded: `stamp_round.py` samples its own process env, so the arm was re-exported from the
runner rather than sampled from the render process, and the stamp says so instead of implying
otherwise.

---

## 6. GT-18 · 19 · 20 · 21 → `LANDED`

All four rows were correctly held `OPEN` on two counts: R-2 was owed (RT **F2**) and GT-21's
leaf-off arm was not on screen (RT **F1**). Both are discharged, so all four close together —
GT-18 carries the re-cache and 19/20/21 ride it (§0-2). Each landing record in
`Docs/audit_v4/gt_changes_w3.md` §4 carries **the invocation actually run**, per §0-3, including
the two zero-sample FAILs verbatim.

**What the closure does not claim.** GT-21's row describes the census, the tints and the
placement; those landed at `1962f76` and were confirmed by the red team in numbers and pixels.
What did not land until `a8e8343` is the *mechanism*, and the row is closed with both facts on
it rather than with the second one quietly folded into the first.

---

## 7. Findings handed on

| # | Sev | Finding | Owner |
|---|---|---|---|
| **S10c-F1** | MED | **A registry-membership assertion cannot prove a composition result.** scene10's old self-check asserted `BARE_SUBPRIMS` membership and passed while every tree rendered green. Any other self-check that asserts a *table lookup* where the deliverable is a *composed stage* has the same hole — `place_shrubs`' consumers are the obvious next place to look | S-WPs · T1 |
| **S10c-F2** | MED | The K4-**F1** hand-over predicted 13 scenes / 65 shrub instances will lose visible magenta on their next round. scene10 is not one of them (its pool is `Burning_Bush`/`Juniper`), but **its 13 shrub clumps did re-draw scale and yaw** from K4(b)'s RNG-stream shift, and this round measures that as **null on the judged cuts** (§3.1). Other scenes should re-run the same STEP-0 arm before blaming their own edit | S-WPs of 02·05·08·13·14·16·19·20·C4·N1·N2·N3·N5 |
| **S10c-F3** | LOW | RT **F6** (crest-hedge bald tan domes at `h1.8_d10`) and RT **F7** (tread leaf-band texture green-tinged at `through_treads` macro) **both survive this round untouched** — visible in the committed montages. Neither is a leaf-off defect; both are dressing/tint items for 통람 v3 | 통람 v3 queue |
| **S10c-F4** | LOW | `PARAMS['season']['bare']`'s `native` values differ from `sc.BARE_NATIVE` by up to 3 mm (`Gray_Birch` 3.2990 vs 3.2960). Kept deliberately (§1.2) and now gated at ≤5 mm. Whoever unifies them owes a round, because it moves trunk heights by 0.09 % | S10 next touch |
| **S10c-F5** | LOW | `scripts/stamp_round.py` still records `dirty_files` as a count and still samples its own process env, so a stamp taken outside the render shell silently records `env: {}`. Both were worked around per-round here; the fix is one file in `scripts/` | tooling track (RT F9) |
| **S10c-F6** | INFO | The unscoped `geom_invariance_check` is **33/33 at `e8e2895`** — scene18 assembles. GT-22 and GT-23 each carry an "owed to whoever closes the S18 lane" note about that sweep. The evidence is here; the rows are not mine to close | ledger owner |

---

## 8. Reproduction

```bash
# the fix, isolated arms (never the shared worktree)
git archive e8e2895 | tar -x -C armA && rm -rf armA/assets && ln -s <repo>/assets armA/assets
( cd armA && python3 scripts/dump_inv.py invA.json )     # run_arm(dump=True), scene10 only
( cd <repo> && python3 scripts/dump_inv.py invB.json )   # then diff row-by-row, by field

# floor
python3 -m py_compile scenes/main/scene10_park_deck_switchback.py
flock -w 7200 /tmp/negobs_gpu.lock  NEGOBS_SMOKE=1 python scenes/main/scene10_park_deck_switchback.py
python3 scripts/geom_invariance_check.py                 # unscoped, 33/33
python3 scripts/placement_lint.py --scenes scene10 --rules Docs/briefs/placement_rules_v1.yaml

# the two rounds (identical arm; ROUND = 260731_w3_pre10c pre-fix, 260731_w3_s10c post-fix)
flock -w 7200 /tmp/negobs_gpu.lock bash <scratch>/render_round.sh $ROUND
python3 scripts/stamp_round.py look_check/scene10/$ROUND $ROUND scene10   # with the arm exported
python3 scripts/regression_check.py --before look_check/scene10/260731_w3_s10 \
    --after look_check/scene10/260731_w3_s10c --json Docs/reports/regr_260731_w3_s10c.json
python3 scripts/near_ground_stats.py 'look_check/scene10/260731_w3_s10c/pt_noon_preset_h0.3_*.png' --gate

# R-2
flock -w 7200 /tmp/negobs_gpu.lock →
  python3 scripts/run_data_render.py --run 260731_data_s10 --scenes scene10
  python3 scripts/check_data_run.py 260731_data_s10
```

The measurement scripts (`dump_inv.py`, the crop/green-census tool, the stamp-marker tool) lived
in scratch, per the lane convention that `scripts/` belongs to the tooling track — the same rule
`redteam_s0710_rebuild.md` §2 records for T3's `t3_geom_reverify*.py`. **Nothing in `scripts/`
was written or committed by this task.**
