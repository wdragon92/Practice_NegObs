# Red team — Lane 1 exit verification (kit revival + closures)

> **Wave** W3 · **Scope** Lane-1 exit gate · **Date** 2026-07-31
> **Branch** `feat/realism-v1` · **HEAD at verification** `535926e` (clean tree at run time)
> **Method** adversarial, **re-run not re-read**: every number below was re-executed on this
> machine — isolated `git archive` arms for tree-wide proofs (K4M/RT precedent), real usd-core
> (`/tmp/usdvenv`, 26.8) for composition proofs, the Isaac conda env under
> `flock -w 7200 /tmp/negobs_gpu.lock` for the one GPU re-render. `scenes/main/scene18*` and
> `assets/coastal` were **never touched**; zero writes to any lane-owned file.
> **Targets** LB (`d71e1e3`) · K4 (`e4fc4cf·5be08c7·e4d9cf9·7e26592·5ceb76a·e8e2895`) ·
> K5 (`9c19f25`) · K1T4 (`1a6be6b·7f8b0ec`) · S10c (`a8e8343·becd8f9·dc68e74`) ·
> CB-7 (`6edce66·b7abe89·535926e`) · lane exit.

## 0. Verdicts

| Target | Verdict | One-line basis |
|---|---|---|
| **LB** ledger batch | **CONFIRMED** | all 8 amendments digit-checked against their sources; append-only held except one ~70-char clause tail (RT-2, LOW) |
| **K4** (0)+(a)–(d) | **CONFIRMED** | F1 usd-core trap+fix reproduced 4/4; all four A/B row counts reproduced exactly; mutation test bites; archive-first proven; one **latent** run-end edge found (RT-1) |
| **K5** infra_kit | **CONFIRMED** | self-check re-run all-pass; 0 public-signature changes by AST; GT 0.168 / rhythm / 턱낮춤 / LOD live-verified |
| **K1T4** | **CONFIRMED** | scene16 A/B re-run: 438/439 byte-identical, path-normalised hashes equal; T4 GPU re-render: red-fallback 0.00 %, `IsInstance` 4/4, `C120` 0 |
| **S10c** | **CONFIRMED** | `check_data_run` re-run reproduces PASS/FAIL set verbatim; green share re-measured 7.21→0.01 %; both stamps carry `baseline_of_record` |
| **CB-7** | **CONFIRMED** | one commit, one re-cache verified; 48-gate selfcheck re-run PASS; prims 545 / hash `a4c3a5f9` independently reproduced; deletion checkout 8/8 |
| **Lane exit** | **CONFIRMED** | 0 commits touch scene18/coastal; per-commit ownership clean; unscoped 33/33 at HEAD in an isolated arm; open items enumerated in §8, none blocking |

---

## 1. LB — supervisor ledger batch (`d71e1e3`, + landing commits `dc68e74`/`b7abe89`)

Re-derived, not re-read:

* **GT-3 flip** — sourced to `w3_intake_v2_images.md:1072` ("GT-3 REVERSED — CONFIRMED …
  full-length, enclosed, soffit-lit"); §3 row struck-through + annotated; prim-delta sign ADDED;
  R-3 survives; gate stays CB-7 / pilot 02. ✔
* **GT-4 RETIRED** — sourced to intake `:1090` (§7-6); new `RETIRED` vocabulary row in §2 (ledger
  line 63); §4 record "empty by design"; P-5 gate dies with it. ✔ — with **RT-2** below.
* **GT-14 bed −0.22 → −0.33** — strikethrough amendment; re-verified live this session:
  `scene07_temple_stone_path.py:220 corridor_bed=0.33` (also `:207/:1265/:1962`). ✔
* **GT-20 newels 28/40** — re-run `NEGOBS_SMOKE=1 scene10` prints
  "엄지기둥 28개 (런 끝점 40개에서 중복 제거)". ✔
* **sceneN2 W8** — §7 watch item at ledger line 240 (`seam_proud = 0.0023`), **no row, no
  re-cache**. ✔
* **GT-22 / GT-23** appended as full §3+§4 rows. ✔
* **No scene18 row** — §9-8 explicit; `GT-24` occurs 0 times in the ledger. ✔
* **Floor** — its "33/33 at the committed HEAD" reproduced: my HEAD arm gives scene04
  **1335 / d530f155** exactly; scene16 is 439 / `a9d922f5` at `535926e` because K1's path move
  landed after the batch — path-normalised identity proven in §4 below, so no contradiction.

**Append-only audit (mechanical).** Character-level diff of every modified ledger row across
`d71e1e3`, `dc68e74`, `b7abe89`: the only consumed characters are the status word `OPEN` (the
sanctioned §3 status flip), `—` placeholder dashes in §4 cells, and **RT-2**: in GT-4's re-cache
cell the tail clause "*expect to \*reduce\* per-element counts, \*\*not\*\* raise the cap*" was
dropped instead of struck through (~70 chars; the surrounding cell IS struck through and the row
is retired, so the loss is cosmetic and recoverable from git — but it is the one true deletion in
the batch).

## 2. K4 — `scene_common` + `props_kit`

### 2.1 (0) F1 — independently reproduced, then the fix re-proven in pixels

Own harness, real usd-core 26.8, 4 species × 3 arms (`rt_f1_test.py`, scratch):

```
Gray_Birch      C(plain): leaves gone | A(SetActive→True, then instance): leaves SURVIVE (2 meshes) | B(wrapper+instance): gone
Elm_Sapling     same | same | same
Lombardy_Poplar same | same | same
Rhododendron    C: Flowers gone | A: Flowers SURVIVE (4 meshes) | B: gone      → 4/4 REPRODUCED
```

The legacy arm returns `True` from `SetActive` and the composed prototype keeps the mesh —
the trap is real, and the wrapper route is the fix, exactly as claimed.

* **A/B re-run** (`d71e1e3` vs `e4fc4cf` arms, full 33-scene inventory): **31,013 rows both**,
  **65 differ, all reference-string-only** `Rhododendron.usd → Rhododendron_noflower.usda`,
  scene distribution **matches the report digit-for-digit**
  (02:1 05:9 08:14 13:4 14:8 16:4 19:1 20:3 C4:6 N1:8 N2:1 N3:3 N5:3), tree rows 0. ✔
* **Pixels** (scene10, my metric g>1.15·r ∧ g>1.15·b): `from_below` **7.21 % → 0.01 %**,
  `h1.8_d10` **1.67 % → 0.04 %**, `through_treads` **3.38 → 3.39 %** (the declared F7
  tread-texture carry-over, correctly NOT cured by a leaf-off fix). Juniper control keeps its
  needles in the committed montage. ✔

### 2.2 (a) C0-7 — mutation-tested, and one latent edge found

* `baluster_gap=0.110` probe: **HEAD arm clamps to a realised 0.100 m** (max clear = min clear =
  0.100); the **pre-gate arm realises the illegal 0.110 m** — the gate bites and is new. ✔
* Blast radius +4 prims re-derived independently: 31,013 (`e4fc4cf`) → 31,017 (`e4d9cf9~1`). ✔
* Run-end closure: engineered a 125 mm terminal span — HEAD places the flush terminal baluster
  (terminus opening → 0), pre-gate arm leaves 125 mm open. ✔
* **RT-1 (LOW, latent)**: the terminal baluster sits flush at `x_end − r`, so the opening between
  the last regular baluster and the terminal one is `span − 2r` — up to **118 mm** at the maximum
  span (my probe realised **107 mm** at HEAD). Both real sites land legal (scene20 105→87,
  sceneC4 117→99) and all 16 call sites measure ≤ 99 mm, so this is inert today — but a future
  call site with an unluckier run length can still exceed the 안목 at that one joint. Hand to the
  K-track: place the terminal at `x_last + pitch_max` or re-check the residual opening.

### 2.3 (b) species — every number reproduced

A/B re-run (`1a6be6b` vs `e4d9cf9` arms): **31,017 rows both · 646 differ · xformOp 385 ·
reference 261 · path/type/shape 0 · XY-translate 0 · z-translate 192, all on shrub paths** —
the report's §3.4 table to the digit. Monospecific verified in composition: scene06 = **20 trees,
one reference** (`Shumard_Oak.usd`) ⇒ one prototype under instancing; 03/11/12/13/14/C2/D3 all
collapse 2–5 species → 1; **scene04 has zero differing rows**; scene10/scene18 keep their species
sets. Per-point `randrange` is gone — AST finds exactly one surviving `randrange` in
`scene_common` (`:3439`), the **once-per-bed** draw the design specifies.

**Nuance worth stating plainly** (declared as K4-F2, but the summary's "04/10/18 unmoved" reads
stronger than the rows): scene10 has **16** and scene18 **159** differing inventory rows in this
A/B (yaw/height re-draws + shrub seating z). Species sets are untouched and the S10c attribution
round proves the scene10 delta is below every pixel gate (§5) — but scene18's composed content did
move through the shared library while its lane was live. Nothing to fix; the lane should just not
quote "unmoved" without the census qualifier.

### 2.4 (c)(d) — props_kit, archive-first, split proof

* `python3 props_kit.py` re-run: **32/32 PASS · 427 prims**; consumers 0 (two symlinks only). ✔
* **Archive-first proven at commit granularity**: manifest `archived_at 2026-07-30T18:15:17` at
  `git_head 7e26592` (= commit (c)) — before (d) `5ceb76a` landed 18:22; **67/67 files md5-verified
  on disk today**; copies carry the source round's own mtimes (02:36–02:48). ✔
* **GT-6 split proof re-run**: `7f8b0ec` vs `5ceb76a` arms, 33 scenes — **31,017 rows, 0 differ**.
  EMPTY as the row law requires (the +2 mm rows belong to scene06's pilot, not the library). ✔

## 3. K5 — `infra_kit` (`9c19f25`)

* Self-check re-run end-to-end: **all items pass** — 12 m → **12 × 1.000 m** blocks · 11 joints ·
  top +20 mm rule · exposure 150 mm · **gt_drop = 0.150 + 0.018 = 0.168** · 턱낮춤 realised as
  **150/85/20/85/150 with no block straddling a transition** · scene02's +100 mm **rejected**
  (`strict`) / warning (`strict=False`) · out-of-band exposure rejected · **LOD 141 → 45 prims @
  140 m** with the near window kept at 1 m units · polyline 16 m → 16 blocks · arris = 0 prims via
  `LOOK_CLASS['curb']` + `check_arris_role` present.
* `derive_manholes`: scene05's 11.5 m line → **1, at the upstream head**, camera-blind; 400 m Ø450
  → max gap 66.7 ≤ 75; Ø1200 sparser; junction merge. The "16 m plaza → 0" claim holds under
  `head=False` (run starting at an existing chamber — documented in the docstring and asserted in
  the self-check); the default `head=True` correctly yields 1. Report's own text ("1 or 0") is
  consistent.
* **Signature preservation by AST** vs `9c19f25~1`: changed public signatures **0**, removed **0**
  (the one hit is a nested-closure name collision, not an API change). ✔
* Crops: the macro sheet shows the monolith-vs-jointed A/B and the visible 150→85→20 step-down;
  no humans/vehicles.

## 4. K1T4 (`1a6be6b` · `7f8b0ec`)

* **K1 A/B re-run** (arms at `1a6be6b~1` / `1a6be6b`, scene16): **439/439 rows, 438
  byte-identical**, the single differing row is the same
  `Cube|T=(-0.6,0,-0.027);S=(0.3,1.5,0.033)` at
  `Tactile_StairHead/Base → GKit/Tactile_stair_top/Base`; **path-normalised hashes EQUAL**. ✔
* **EXPECTED_FP computes** (import + print): register **18 rows**, scene16
  `preset_h0.3_d5 rows_work (166,194)` · `preset_h0.3_d10 rows_work (140,160)`,
  `src tactile_stair_top`. `scripts/regression_check.py` contains **no** `EXPECTED_FP`
  reference — **D14 still open**, "prepared-only" is accurately stated. ✔
* **T4 re-rendered by me** (Isaac env, `flock`, PT_FAST, same probe, `instanceable=True`):
  `IsInstance` **4/4**, `C120` count in log **0**, red-fallback (report's own metric)
  **0.00 % on both cuts**, means 169.6/171.7/173.2 vs the report's 170.6/172.1/172.9 —
  within PT noise. `assets/urban/nv_core/materials` holds the 3 repaired modules
  (`baking_annotations`, `OmniUe4Function`, `OmniUe4Base`). Before/after crop authentic
  (flat-red vs bedded granite). ✔

## 5. S10c (`a8e8343` · `becd8f9` · `dc68e74`)

* **`check_data_run 260731_data_s10` re-run by me**: sections **[2][3][4][5] PASS**, section [1]
  **FAIL 2** with the exact recorded strings (`sun-bearing … 0 pairs`, `sunless … 0 scene-pairs`),
  8 cuts · 2.34 s/cut. Reported verbatim, not cured — as claimed. ✔
* **Regression re-runs**: `260731_w3_s10 → s10c` = **FAIL 1 · WARN 7** (= committed JSON);
  `s10 → pre10c` = **no regression** (the Lane-1 kit window is null on scene10's judged cuts);
  `pre10c → s10c` = identical verdict set (attribution). ✔
* **Stamps**: `260731_w3_s07/round_stamp.json` and `260731_w3_s10c/round_stamp.json` both carry
  `baseline_of_record: true`; s10c also `dirty_paths` + `env_source` (F9 workaround); s07 carries
  the F5-closure note. ✔
* GT-18..21 landing records hold real invocations (the R-2/R-3 command lines re-executed above);
  the append-only audit on `dc68e74` consumed only the four `OPEN` status words. The GT-21 §3
  defective clause ("1346b70 … reported success, so the §8.R contingency did not fire") **is still
  in the ledger body at HEAD** — the supervisor amendment the report flags as owed remains owed.

## 6. CB-7 (`6edce66` · `b7abe89` · `535926e`)

* **One commit, one re-cache**: `scenes/main/scene02_underpass.py` is touched by exactly one
  commit in `836ed7f..HEAD`. R-2 data run `dataset/_archive/scene_dev_2607/260731_cb7_recache` exists and re-checks
  **PASS**; R-3 = `260731_w3_cb7` (+ the `_pre` attribution arm). Regression re-run
  `cb7_pre → cb7`: **FAIL 11 · WARN 2**, byte-equal verdict set with the committed JSON, every
  FAIL a `FRAME` code (the declared composition change), OCCL at WARN. ✔
* **48-gate selfcheck re-run PASS**, including: GT-1 riser emitted `kind='up_step'` and excluded
  from drop rows, drop edge 3.380, 20×0.169 lands the foot at −3.2000; GT-2 via
  `infra_kit.build_curb_line` — 40 blocks/41 prims per line, **28 × 1.000 m in the judged
  window**, top +0.020, exposure 0.150, datum −0.130 as the unique solution; GT-3 canopy
  −1.90…+7.15 covering approach 1.90 m + full descent + 0.15 m, 5 column pairs, valance
  1.75…2.70, 10 soffit lights; **deletion checkout 8/8** (porch roof + 4 posts, both old kerbs,
  Building_B) with zero residual path creation and the 4-post porch builder no longer called. ✔
* **Independent cross-check**: my HEAD arm reproduces scene02 **545 prims, hash `a4c3a5f9`** —
  the exact figures the GT-3 landing record quotes (391 → 545, +154). ✔
* **Crops vs G2**: full-length, soffit-lit, column-lined canopy over the whole descent — yes in
  both `approach` and `h1.8_d10`. "Enclosed" is the valance-over-open-vent-band form; the report
  itself raises this as **S02-Q1 needing a ruling** and commits the measured glazing rejection
  (the `glass` material renders as opaque near-black planes in
  `cb7_r1_glazing_rejected_beauty.png` — verified, the rejection is evidence-based). Honest, not
  hidden. ✔

## 7. Lane-wide

* **Do-not-touch**: `git log 836ed7f..HEAD -- 'scenes/main/scene18*' 'assets/coastal'` → **0
  commits**. ✔
* **Ownership/pathspec**: every commit's file list ⊆ its WP's stated paths (full listing checked
  commit-by-commit); no stray files anywhere in the window. The two non-lane commits in the range
  (`45ffaa4`/`ed37b8f`) are the supervisor's user-ruling entries touching only the intake survey. ✔
* **Floor at HEAD, isolated arm**: unscoped `geom_invariance_check` **R-4 33/33 · R-6 33/33 PASS**
  (scene18 assembles: 979 prims `cc26fd97`); `placement_lint` ERROR 30 · WARN 227 · BLOCK 29 —
  consistent with K4(b)'s 66→31 plus the two subsequent scene landings. Beyond HEAD, my six A/B
  arms assembled all 33 scenes at five intermediate commits without error — per-commit floor
  claims are consistent with what re-execution shows. ✔
* **Humans/vehicles**: none in any *rendered* crop (checked k5 macro, s10c montages, cb7 crops,
  t4 sheet). **RT-4 (note)**: `_w3_cb7_crops/G2_matched_crop.png` is the *real-world reference
  photograph* (intake G2) and contains pedestrians — committed as a comparison exhibit, consistent
  with intake precedent, but strictly it is the one crop in the window with humans in it. If the
  no-humans rule is meant to bind `Docs/reports/` exhibits, replace it with a pointer into the
  intake file.

## 8. Findings (new, this review)

| # | Sev | Finding | Owner |
|---|---|---|---|
| **RT-1** | LOW (latent) | Terminal baluster closes the terminus but can itself leave `span − 2r` ≤ **118 mm** between the last two balusters (107 mm realised in an engineered probe at HEAD). All 16 current sites measure ≤ 99 mm — inert today | K-track |
| **RT-2** | LOW | GT-4 amendment dropped one ~70-char clause tail ("expect to *reduce* per-element counts…") instead of striking it — the single true deletion in an otherwise mechanically-verified append-only batch | supervisor/LB |
| **RT-3** | INFO | K4(b) "04/10/18 unmoved" holds for **species sets** (and literally for scene04's rows); scene10/scene18 have 16/159 jitter-re-draw rows in the A/B, declared as K4-F2 and pixel-null on scene10's judged cuts | — (record) |
| **RT-4** | INFO | `G2_matched_crop.png` = reference photo with pedestrians committed under `Docs/reports/` | S2/supervisor |

## 9. Open items carried to lane exit (verified still open at `535926e`)

1. `w3_execution_spec_v1.md` **§1.5 Option-A clause still unstruck** (line ~119) and §9's P-5 row
   — the spec-side edits LB declared owed remain owed (the spec outranks the ledger).
2. **GT-21 §3 body** still carries the "1346b70 reported success" clause — supervisor amendment
   line owed (GT-6 strikethrough precedent).
3. **D14**: `regression_check.py` still does not read `EXPECTED_FP` (verified by grep) — scene16
   will keep manufacturing its two pre-registered GRAZE/FP rows on every new baseline; CB-7 is the
   third live instance.
4. **F5**: `260731_w3_s04` and `260731_w3_s16` round stamps carry **no `baseline_of_record`
   marker** (verified ABSENT) — the status lives only in ledger rows; S10c fixed s07/s10c only.
5. S02-Q1/Q2 and R02-2 rulings (CB-7 §blockers), K4-F3 (T3 amendment), K4-F4 (belts inert until
   S-WPs pass `species=`), T4 FU-1 (scene07/10 workaround revert) and FU-2 (procurement
   `CORE_MDL`), stamp_round F9 root fix — all correctly recorded by their reports, none closed by
   stealth.

## 10. Reproduction

```bash
# arms (never the worktree)
git archive <sha> | tar -x -C <arm> ; rm -rf <arm>/assets ; ln -s <repo>/assets <arm>/assets
# inventory dumps + field-level diff: scratch rtlane1/{dump via scripts' own run_arm, rt_f1_test.py,
#   rt_baluster_drive.py}; pairs: d71e1e3/e4fc4cf · 1a6be6b~1/1a6be6b · 1a6be6b/e4d9cf9 · 7f8b0ec/5ceb76a
python3 scripts/geom_invariance_check.py            # HEAD arm: 33/33 R-4+R-6
python3 scripts/check_data_run.py 260731_data_s10   # PASS 2/3/4/5 · FAIL 2 (zero-sample, declared)
python3 scripts/check_data_run.py 260731_cb7_recache
python3 scripts/regression_check.py --before look_check/scene10/260731_w3_s10  --after look_check/scene10/260731_w3_s10c  --json <tmp>
python3 scripts/regression_check.py --before look_check/scene02/260731_w3_cb7_pre --after look_check/scene02/260731_w3_cb7 --json <tmp>
NEGOBS_SMOKE=1 python3 scenes/main/scene02_underpass.py   # 48 gates
NEGOBS_SMOKE=1 python3 scenes/main/scene10_park_deck_switchback.py
python3 infra_kit.py ; python3 props_kit.py
# T4 GPU re-render: conda env_isaaclab + flock, scratch t4_probe.py → red-fallback 0.00 %, IsInstance 4/4
```
