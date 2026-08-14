# `look_check/` cleanup v1 — corpus-aware pruning + naming index

Written 2026-07-30 · CPU only (numpy + PIL) · **GPU 0 · render 0 · Isaac 0** ·
no git commit/push/checkout. Repo files created = `look_check/README.md`,
`look_check/INDEX.md`, this report; one file edited = `.gitignore` (§5-7, required so the
two index documents can be committed at all). No source file was modified.

Evidence tags: `[measured]` computed this mission from repo bytes · `[doc]` read from a
committed report · `[assumed]` judgement.

| | before | after | freed |
|---|---:|---:|---:|
| `look_check/` | **17 523 MB** (17.11 GB) | **12 070 MB** (11.79 GB) | **5 453 MB = 5.33 GB** `[measured]` |
| repo total | 20 369 MB (19.89 GB) | 14 915 MB (14.57 GB) | 5 454 MB |
| rounds under `look_check/<scene>/` | 417 | **291** | **126 deleted** |
| `__pycache__` dirs | 7 (3 MB) | 0 | 3 MB (regenerable) |

**Corpus proof: every figure reproduces exactly.** `diff` of the corpus driver output
before and after deletion is empty; the 4 + 12 + 23 published measurement anchors of
`w2_tools_v1.md` all still land on their published values. Details in §4.

---

## 1. Dependency extraction — what the corpora actually name

`w2_tools_v1.md` §4.3 records the corpora only as **counts per series**, not as pair
lists, and states that the drivers (`valset.py`, `inject.py`) lived in a session
scratchpad that is gone. The pair membership was therefore re-derived here and
**validated by reproducing the published counts and verdicts** — §4.

### 1.1 The three v2.1 validation corpora `[doc: w2_tools_v1.md §4.3–4.4]`

| corpus | series | published cuts | rounds it pins |
|---|---|---:|---|
| **False-positive set** | mode swap (RT↔PT · PT sample count) | 12 | `scene07/{scene07_ptlegacy,scene07_ptfast}` · `sceneD3/{sceneD3_ptlegacy,sceneD3_ptfast}` · `{scene02,scene13,sceneD4}/p2dark_{legacy,fast64,fast256}` · `scene07/{v8_rt,v8_pt}` |
| | look A/B (material · vertex-displacement toggle) | 42 | `scene01/{p2g1,p2g2,p2g3,p2rf}_{off,on}` · `scene01/p2mat_{before,after}` · `scene01/p2c_{a,b}` · `scene07/{p2g1,p2g2,p2g3}_{off,on}` · `sceneD3/{p2g1,p2g2,p2g3}_{off,on}` · `sceneD3/p2ctrl_{a,b}` · `sceneD3/p2det_{a,b}` |
| | context dressing `ctx1→ctx2` | 44 | `ctx1`,`ctx2` in sceneC1/C2/C4, D1–D4, N1–N5 (12 scenes) |
| | realism `r1_on→r2_on` | 40 | `r1_on`,`r2_on` in scene01–scene13 |
| | P4 near-field | 19 | `sceneC2/{r2_on,balust,leaf3d,handrail,fix1}` · `scene05/{r2_on,shrub,facade}` |
| **History set** | `v6_rt→v7_rt` | 68 | `v6_rt`,`v7_rt` in scene01–scene21 |
| | `v7_rt→v8_rt` | 26 | `v7_rt`,`v8_rt` in scene05/06/07/09/10/11/12/17 |
| **T3 pairs** | must stay quiet under v2.1 | 2 | `scene13/{v6_rt,v7_rt}` · `scene07/{r1_on,r2_on}` |

The series→round mapping is not guesswork; each was fixed by matching the published cut
count exactly against the GRAZE-adjudicable cuts (`is_graze_view` = `h0.3` presets +
the `*graz*` mise-en-scène family, intersected between the two rounds) `[measured]`:

- `ctx1→ctx2` → **44** (published 44) · `v6_rt→v7_rt` → **68** (68) · `v7_rt→v8_rt` → **26** (26)
- `r1_on→r2_on` → **40** (40; scene13's `r1_on` holds only `d2`/`d5`, which is exactly the
  −2 that separates 42 naive from the published 40)
- look A/B → **42** (42), from 14 twin pairs
- mode swap → **12** (12), and its RT↔PT slot is `scene07 v8_rt→v8_pt`, which
  `regression_check.py`'s own header names as control (b): *"a render mode swap
  (scene07 v8_rt->v8_pt)"* `[doc]`
- P4 near-field → **18** against the published 19. The missing cut sits inside the
  07-29 near-field family, every member of which is on the hard-keep list, so it cannot
  affect a deletion decision. Recorded honestly rather than padded.

**Consequence for the delete plan:** `v6_rt`, `v7_rt` and `v8_rt` are corpus members
and were **not** deleted, even though the brief listed them as candidates.
`v5_rt`/`v5_pt` appear in no corpus at any count and were deleted.

### 1.2 Other cited rounds (grep of `Docs/**/*.md`) `[measured]`

- **Measurement anchors** — `near_ground_stats.py` §2.3 and `skyline.py` §3.2 name
  `scene01/v7_pt`, `scene18/v7_pt`, `scene03/v7_pt`, `scene09/v8_pt`, `scene12/v8_pt`,
  `scene17/v8_pt`, `scene11/v8_pt`, `sceneD3/r2_on`, `sceneN5/r2_on`, `sceneN4/wall`,
  `sceneC1/r2b_on`, `sceneC2/fix1`, plus the eleven `r2_on` rounds of the `flat_gnd` median.
- **2026-07-29 reports** — `t0_spike_report_v1.md` (`_t0_spike/*`),
  `w2_gate_preflight.md` (`{scene02,sceneN3}/wininset_*`, `scene14/parapet_crop`),
  `w2_pilot_ground_v1.md` (`{scene13,scene15,sceneN5}/w2_pilot*`),
  `w2c_merge_t1_v1.md` (`w2c_*`, `sceneC2/w2c_g2`), `w2_materials_v1.md` (`t1_mtl_*`).
- **Control pairs named inside `regression_check.py`** — `sceneD3 r2→r3` is the
  documented "small-fix round" control for the DARK/OCCL/FRAME thresholds. `sceneD3/r2`
  and `r3` were therefore **kept** despite falling in the `r1/r2/r3` delete class `[doc]`.
- `graze_recalibration_v1.md` §7 defends `scene19 r4→r5 h0.3_d10` as a genuine FAIL →
  `scene19/r4`, `r5` **kept**.
- `scene01/pair_cues_off` is the cue-off counterpart grid evidenced in
  `scene01_completion_report.md` §58 → **kept**.
- `p2g4_on` (scene01/07/D3) is the "latest" dead-pixel measurement round in
  `doc_consistency_audit_v1.md` §301–306 → **kept**.

---

## 2. Decision table

### 2.1 Deleted — 126 rounds, 5 518 MB

| delete class | rounds | MB |
|---|---:|---:|
| early P2/P3 rounds (`r1`/`r2`/`r3`/`r4`), superseded by full re-runs | 69 | 2 861 |
| v5 judgement ladder (`v5_rt`/`v5_pt`) — in no corpus at any count | 30 | 1 449 |
| v3-era finals (`final_pt`/`final_pt_r2`) — superseded by `v7_pt`/`v8_pt` | 26 | 1 166 |
| stray `auto/` round (scene01) | 1 | 42 |
| **total** | **126** | **5 518** |

| scene | deleted rounds | MB |
|---|---|---:|
| `scene01` | `auto`, `final_pt`, `r2`, `r3`, `v5_pt`, `v5_rt` | 277 |
| `scene02` | `final_pt`, `r2`, `r3`, `v5_pt`, `v5_rt` | 263 |
| `scene03` | `final_pt`, `r1`, `r2`, `r3`, `v5_pt`, `v5_rt` | 287 |
| `scene04` | `final_pt`, `r1`, `r2`, `r3`, `r4`, `v5_pt`, `v5_rt` | 348 |
| `scene05` | `final_pt`, `r1`, `r2`, `r3`, `v5_pt`, `v5_rt` | 301 |
| `scene06` | `final_pt`, `r1`, `r2`, `r3` | 145 |
| `scene07` | `final_pt`, `r1`, `r2` | 148 |
| `scene08` | `final_pt`, `final_pt_r2`, `r1`, `r2` | 170 |
| `scene09` | `final_pt`, `r1`, `r2`, `v5_pt`, `v5_rt` | 172 |
| `scene10` | `final_pt`, `final_pt_r2`, `r1`, `r2`, `r3` | 165 |
| `scene11` | `final_pt`, `r1`, `r2`, `r3`, `r4` | 129 |
| `scene12` | `final_pt`, `r1`, `r2`, `r3` | 204 |
| `scene13` | `final_pt`, `r1`, `r2`, `r3`, `v5_pt`, `v5_rt` | 255 |
| `scene14` | `final_pt`, `r1`, `r2`, `r3`, `v5_pt`, `v5_rt` | 203 |
| `scene15` | `final_pt`, `final_pt_r2`, `r1`, `r2`, `r3`, `r4`, `v5_pt`, `v5_rt` | 303 |
| `scene16` | `final_pt`, `r1`, `r2`, `v5_pt`, `v5_rt` | 268 |
| `scene17` | `final_pt`, `final_pt_r2`, `r1`, `r2`, `r3`, `v5_pt`, `v5_rt` | 340 |
| `scene18` | `final_pt`, `r1`, `r2`, `r3`, `v5_pt`, `v5_rt` | 237 |
| `scene19` | `final_pt`, `final_pt_r2`, `r1`, `r2`, `r3`, `v5_pt`, `v5_rt` | 244 |
| `scene20` | `final_pt`, `r1`, `v5_pt`, `v5_rt` | 227 |
| `scene21` | `final_pt`, `r1`, `v5_pt`, `v5_rt` | 177 |
| `sceneC1` | `r1`, `r2` | 49 |
| `sceneC2` | `r1`, `r2` | 123 |
| `sceneC4` | `r1`, `r2` | 110 |
| `sceneD1` | `r1` | 52 |
| `sceneD3` | `r1` | 56 |
| `sceneN1` … `sceneN5` | `r1` (each) | 265 |

Plus 7 `__pycache__` directories (3 MB, regenerable).

**Execution discipline.** Every path was enumerated (`os.listdir`) and written to a log
*before* `shutil.rmtree`, one directory at a time, asserted to live under
`look_check/` and asserted absent afterwards. **No wildcard spanned a scene.** A
pre-flight cross-check refused to proceed if any delete entry matched the keep set:
it reported `conflicts: none` `[measured]`.

### 2.2 Kept, and why — 291 rounds, 11 832 MB

| keep rule | rounds | note |
|---|---:|---|
| baseline-of-record (`v7_pt` ×13, `v8_pt` ×8, batch1 `ctx2`-family) | 21 + 30 | next W2-D regression compares against these |
| history corpus (`v6_rt`, `v7_rt`, `v8_rt`, `v8_rt2`) | 51 | §1.1 |
| false-positive corpus (`ctx1`/`ctx2`, `r1_on`/`r2_on`, `p2*`, `*_ptfast`/`*_ptlegacy`, near-field) | 100+ | §1.1 |
| created 2026-07-29 or later | 70 | `w2*`, `t1_*`, `wininset*`, `*_hoff`, `_t0_spike/*`, `c2_A_base`, `leaf3d`, `shrub`, `facade`, `planterfix`, `fix1`, `handrail`, `wall`, `graze_warn_crop` |
| named control in `regression_check.py` header | 2 | `sceneD3/r2`, `sceneD3/r3` |
| defended FAIL evidence (`graze_recalibration_v1.md` §7) | 2 | `scene19/r4`, `scene19/r5` |
| **ambiguous → kept** (RT↔PT mode-swap slot not uniquely resolvable) | 9 | `sceneD2/{r1,r1_pt,r2,r2_pt}`, `sceneD4/{r1,r1_pt,r2_pt}`, `sceneC1/{r3_pt,r4_pt}` — 281 MB of deliberate insurance |
| `look_refs/` | — | user's reference images; **not entered** |

Flat directories (`diag_*`, `spike_e*`, `spike_budget`, `spike_probe`, `logs`) were left
untouched: they are the cited evidence of `realism_phase1.md` and the two
`deadpixel_diag_*` reports.

`_t0_spike/prev0728_spike_{e1,e4,probe}` were **checked for redundancy and are not
duplicates** — the file *names* match the top-level `spike_{e1,e4,probe}` but the file
*contents* differ (`md5sum` over the sorted file list differs for all three) `[measured]`.
They are genuine pre-re-run backups per `t0_spike_report_v1.md` §420 and were kept.

---

## 3. What "per scene the survivors should be few" ran into

Per-scene survivor counts land at **3–21**, not 2–4. That is a *finding*, not a
shortfall: the floor is set by the corpora, not by clutter. A main scene must retain at
minimum `v6_rt`, `v7_rt`, `v7_pt`/`v8_pt`, `r1_on`, `r2_on` (+ `v8_rt` where it exists) —
six rounds, all load-bearing. The three heaviest folders are the three that *hosted* the
look-layer experiments: `sceneD3` (21), `scene01` (20), `scene07` (19) — those `p2*`
twins **are** the 42-cut look-A/B corpus and the 12-cut mode-swap corpus.

No surviving round was renamed or folded. Every candidate for it turned out to be
protected by rule 1 of the brief (corpus / report evidence / baseline-of-record); the
remaining 37 "evidence-only" rounds were each traced to a citing report (listed in
`INDEX.md` column *judged / used by*) and none qualified as a role-less orphan.
The naming problem is instead solved by **documentation, not renaming**:

- **`look_check/README.md`** — the going-forward convention `<yymmdd>_<wave>_<purpose>`
  (e.g. `260730_w2d_judge`, `260730_w2d_hoff`, `260730_t1ab_scene19`), the twin-suffix
  rule, the "no version numbers" rule, a legacy-name decoder table, and the explicit
  statement of why old names are frozen.
- **`look_check/INDEX.md`** — 291 rows (+ 11 flat dirs): scene · round · date · MB · cuts ·
  era/phase · kind · status · judging report. Era buckets are P2/P3-early, v5–v8 judge,
  batch1 ctx, P1 spike, P2 gate, P4 realism, W2. Status is
  baseline-of-record / corpus / anchor / active / evidence.
  Since `look_check/` is gitignored, `INDEX.md` is the only committed record of what
  exists on the render machine — regenerate it whenever rounds are added or removed.

---

## 4. Proof — the corpora reproduce exactly

A driver was written that rebuilds all three corpora from the round directories and
counts GRAZE verdicts per series. It was run **before** the deletion and **after**, and
the two JSON outputs are byte-identical (`diff` empty) `[measured]`.

| corpus | series | cuts | v2.1 GRAZE result (before **and** after) | `w2_tools_v1.md` §4.4 |
|---|---|---:|---|---|
| False-positive | mode swap | 12 | FAIL 0 · WARN 0 · deferred 2 | |
| | look A/B | 42 | FAIL 0 · WARN 0 · deferred 0 | |
| | `ctx1→ctx2` | 44 | FAIL 0 · WARN 0 · deferred 4 | |
| | realism `r1_on→r2_on` | 40 | FAIL 0 · WARN 0 · deferred 3 | |
| | P4 near-field | 18 | FAIL 0 · WARN 0 · deferred 0 | |
| | **total** | **156** (pub. 157) | **FAIL 0 · WARN 0** | **FAIL 0 · WARN 0** ✔ |
| History | `v6_rt→v7_rt` | 68 | FAIL 1 · WARN 2 · deferred 17 | |
| | `v7_rt→v8_rt` | 26 | FAIL 0 · WARN 0 · deferred 5 | |
| | **total** | **94** (pub. 94) | **FAIL 1 · WARN 2 · deferred 22 (+1 quieted = 23)** | **FAIL 1 · WARN 2 · deferred 23** ✔ |
| T3 | `scene13 v6_rt→v7_rt d5` | 1 | **quiet** | quiet ✔ |
| T3 | `scene07 r1_on→r2_on d2` | 1 | **quiet** | quiet ✔ |

The three surviving firings are exactly the three §4.4 defends as genuine `[measured]`:

```
FAIL  scene18  v6_rt→v7_rt  preset_h0.3_d2  spec 67.6 (edge 71.3 − near 3.7) agree 0.89
WARN  scene17  v6_rt→v7_rt  preset_h0.3_d2  spec 10.2 (edge 10.2 − near 0.0) agree 0.89
WARN  scene19  v6_rt→v7_rt  preset_h0.3_d5  spec 11.1 (edge 11.3 − near 0.2) agree 0.73
```

### 4.1 `w2_tools_v1.md` §6 reproduction commands, re-run after deletion `[measured]`

| command | published | after cleanup |
|---|---|---|
| `norm_spec.py` × 4 anchors | −0.71/4.1/18.9/0.056 · −0.66/3.2/13.3/0.294 · −2.46/58.4/2.5/0.192 · −1.98/52.3/4.8/0.449 | **all 4 exact** |
| `near_ground_stats.py look_check/scene01/v7_pt/…h0.3_d2 --gate` | `L_mu` 0.865 · `wht%` 98.2 · `σ_LF` 0.72 · `edge%` 16.4 · `struct%` 5.0 | **all exact** |
| `near_ground_stats.py look_check/scene14/r2_on/…h0.3_d* --median` | `flat_gnd` 31.3 | **31.3 exact** |
| `skyline.py look_check/scene18/v7_pt/…h0.3_d5 --bands` | 하늘열% 98.8 · edge_med 345 · edge_std 110.0 · **runmax 844** | **all exact** |
| skyline E-table, all 23 rows | 844 … 27 | **23/23 exact** |
| `regression_check.py --before scene13/v6_rt --after scene13/v7_rt --only preset_h0.3` | GRAZE quiet | **quiet** |
| `regression_check.py --before scene07/r1_on --after scene07/r2_on --only preset_h0.3` | GRAZE quiet | **quiet** |

The full 23-row skyline sweep is the strongest single check here: it touches
`v7_pt` in 10 scenes, `v8_pt` in 7, `r2_on` in 2, plus `sceneN4/wall`, `sceneC1/r2b_on`,
`sceneC2/fix1` and `sceneD3/r2_on` — i.e. it exercises the whole keep list at once.

### 4.2 Reproducing this proof later

The driver is a scratchpad file (synthetic-free; it only reads repo PNGs). To rebuild it,
the series membership in §1.1 is sufficient — feed each `(scene, before, after)` triple to
`scripts/regression_check.py --list` and count issues with `code == "GRAZE"` over the
graze views present in **both** rounds. **Recommendation:** promote the driver to
`scripts/valset.py` so the corpora stop being a scratchpad artefact — this is the second
time they have had to be reconstructed (`w2_tools_v1.md` §5-7 flags the same risk).

---

## 5. Consequences and open items

1. **`final_pt` / `final_pt_r2` are gone**, and three places still name them:
   `regression_check.py`'s module docstring, `regression_tool_v1.md` §220/§243
   (`--before-round final_pt_r2,final_pt,ctx2_pt,ctx2`), and, as visual-inspection
   evidence, `Docs/audit_v4/{judge_v5_rt_09-18, judge_v5_rt_16-21, audit_scene11-15,
   audit_scene16-21}.md` and `Docs/surveys/realism_gap_2026-07-28/F_…md` §949.
   The fallback chain now resolves to `ctx2_pt,ctx2` for batch1 and to **nothing** for the
   main scenes, so the tool prints *"이전 라운드 폴더 없음 — 절대 검사만 수행"* rather
   than failing silently. The current standing baseline is `r2_on`
   (`graze_recalibration_v1.md` §9), which supersedes that chain. **No source file was
   edited** — updating the docstring and `regression_tool_v1.md` is left to the supervisor,
   and is noted in `look_check/README.md` §3.
2. **The v5 judgement ladder is gone.** `judge_v5_rt_*.md` verdicts remain readable but
   their frames are no longer on disk. v5 is two generations superseded (v5→v6→v7→v8) and
   sits in no corpus at any count.
3. **P4 near-field reconstructs to 18 cuts, not 19** (§1.1). Cannot affect this cleanup —
   every candidate for the 19th cut is on the hard-keep list — but it means the
   false-positive corpus is a 156/157 reconstruction, exactly as `w2_tools_v1.md` §5-7
   already warns. If the original pair lists resurface, re-run and compare.
4. **The RT↔PT mode-swap slot is not uniquely resolvable.** `scene07 v8_rt→v8_pt` fits the
   count and is named in the tool header, but `sceneD2 r1→r1_pt`, `sceneD2 r2→r2_pt` and
   `sceneD4 r1→r1_pt` each fit the count equally. All four were kept (281 MB). Resolve by
   recording pair lists in code (item 4.2) and the insurance can be dropped.
5. **`look_check/` is gitignored** — nothing deleted here was ever in git, and nothing is
   recoverable. That is why the pre-flight cross-check and the before/after corpus diff
   were run in that order.
6. **NOTE — not acted on.**
   `/home/vislab/Desktop/work_sy/_negobs_git_backup_20260728_2253.tar.gz`
   (the 105 MB 2026-07-28 backup tarball) was **left untouched** — and in fact
   **no longer exists at that path**: `ls` and a `find` over
   `/home/vislab/Desktop/work_sy` (depth 2) return nothing, and there is no `*.tar.gz`
   anywhere in that tree `[measured]`. It appears to have been removed before this
   mission. Nothing was deleted outside `Practice_NegObs/`. Whether to re-create a
   backup remains a **user decision**.
7. **One repo file was edited: `.gitignore`.** `look_check/` was ignored wholesale, so
   the two new index documents could not have been committed at all. The rule is now
   `look_check/*` + `!look_check/README.md` + `!look_check/INDEX.md` (the trailing-slash
   form stops git descending into the directory, so the negations require `/*`).
   Verified: `git status --porcelain -uall` lists exactly those two paths under
   `look_check/` and still ignores every PNG, `manifest.json`, log and
   `spike_results.json` `[measured]`. No commit was made.

---

## §5 extension — grouping the experimental artefacts (2026-07-30, same session)

Supervisor follow-up: *"group the experimental stuff together; more structure."* No
deletion in this pass — **65 directories moved, 2 symlinks created, 0 bytes lost.**
`look_check/` stays at 12 070 MB.

### E1. Structure adopted

```
look_check/
  <scene>/<round>/            judgement grids · corpus members · anchors · baselines-of-record
  _experiments/
    t0_spike/<round>/         T0 spike tree (incl. its conc* throughput arms)
    spike_p1/<dir>/           P1 realism spikes + the sample-count / time-budget probe
    diag/<dir>/               dead-pixel and per-scene diagnostics
    gates/<scene>/<round>/    gate probes and zoom crops
    twins/<scene>/<round>/    A/B twin arms
  _t0_spike   -> _experiments/t0_spike               (symlink)
  spike_probe -> _experiments/spike_p1/spike_probe   (symlink)
  logs/, *.log, spike_results.json                   render journals, left at root
```

| location | entries | MB |
|---|---:|---:|
| `<scene>/` — judgement · corpus · anchors · baselines | 223 | 9 981 |
| `_experiments/t0_spike/` | 17 | 1 204 |
| `_experiments/twins/` | 27 | 435 |
| `_experiments/spike_p1/` | 9 | 243 |
| `_experiments/gates/` | 24 | 212 |
| `_experiments/diag/` | 4 | 139 |
| **total** | **304** | **12 214** |

Per-scene experimental rounds keep a scene level (`_experiments/twins/scene19/t1_mtl_on_s2/`)
because round names collide across scenes — `wininset_gate` exists in both `scene02` and
`sceneN3`, `t1_crop` in four scenes. A flat `<topic>/<original-name>` would have silently
overwritten them.

The suggested `throughput` topic was **not** created as a separate directory. Its members
are `_t0_spike/conc{1,2,3}` — and `t0_spike_report_v1.md` cites
`look_check/_t0_spike/conc1` and `conc2` by path. Splitting them out of the `_t0_spike`
tree would have broken those citations for a cosmetic gain, so throughput lives inside
`_experiments/t0_spike/` (and `spike_budget`, the PT sample-count / time-budget probe,
sits in `spike_p1/`). Recorded rather than silently re-scoped.

### E2. Corpus protection — 0 corpus rounds moved

The move manifest was cross-checked against the status field of every round before any
`mv` ran. Any round tagged `corpus`, `anchor` or `baseline-of-record` was refused:
the checker reported **`blocked (corpus/anchor/baseline — NOT moved): 0`** `[measured]` —
i.e. the pattern-based move set never even proposed one. All `p2*`, `ctx*`, `r*_on`,
`v6_rt`/`v7_rt`/`v8_rt`, `v7_pt`/`v8_pt`, `*_ptfast`/`*_ptlegacy`, `p2dark_*` and the P4
near-field rounds stayed physically in place, so **no corpus command needed a symlink**.

Judgement-grade W2 grids also stayed at the scene root — `w2_pilot` (scene13/15/N5),
`sceneC2/w2c_g2`, `sceneN4/wall`, `scene05/facade`, `shrub`, `sceneD3/p0_base_pt` — while
their arms (`w2_pilot_r1`, `w2_pilot_hoff`, `w2c_c2_g{on,off}`, `t1_mtl_*`) and every
`*_crop` moved out.

### E3. Symlinks — 2, both root-level

| symlink | target | why load-bearing | resolves |
|---|---|---|---|
| `look_check/_t0_spike` | `_experiments/t0_spike` | `t1_material_layer_spec_v1.md` §7 cites `_t0_spike/c2_A_base/` as the A/B baseline convention; `t0_spike_report_v1.md` cites `_harness`, `c2_B_mdl`, `c2_C_lookv1`, `conc1`, `conc2`, `stats_*.json`, `rtx_settings.json` | **OK**, 34 entries; `c2_A_base/` = 30 PNG |
| `look_check/spike_probe` | `_experiments/spike_p1/spike_probe` | `lighting_camera_variation_spec_v1.md` §513 reads `spike_probe/rtx_settings.json` | **OK**, `rtx_settings.json` present |

`find look_check -xtype l` returns **nothing** — no broken symlink anywhere `[measured]`.

One symlink covers the whole `_t0_spike/*` citation set, which is why moving the tree
wholesale was preferred over flattening its rounds into the topic directory.

**Symlinks are deliberately root-level only.** A symlink inside a scene folder carries a
*fresh* mtime, so it would land first in `ls -t <scene>/*/` and immediately re-break the
latest-round hygiene this pass just fixed (§E4). Past-evidence paths were therefore moved
without symlinks; `INDEX.md` §6 carries the complete old→new relocation map.

### E4. Proof — latest-round discovery now surfaces judgement rounds

`ls -t <scene>/*/ | head -1`, before vs after. **12 of 33 scenes changed, all in the
improving direction; 0 regressed** `[measured]`:

| scene | was | now |
|---|---|---|
| `scene01`, `scene04`, `scene10` | `veg_test` (prop twin, 2–3 cuts) | **`r2_on`** |
| `scene19` | `t1_mtl_on_nodetail` (material arm) | **`r2_on`** |
| `scene02`, `sceneN3` | `wininset_crop` (2–5 cut crop) | **`r2_on`** |
| `scene07`, `scene14`, `sceneC2` | `t1_crop` (1–4 cut crop) | **`r2_on`** / **`w2c_g2`** |
| `scene13`, `scene15`, `sceneN5` | `w2c_c2_crop` (5–12 cut crop) | **`w2_pilot`** |

The remaining 21 scenes already resolved to `r2_on` / `r2b_on` / `facade` / `wall` and are
unchanged. This was a real hazard, not a cosmetic one: `w2c_c2_crop` is a 5-cut zoom set
with no `manifest.json` geometry, so adopting it as a regression baseline would have
compared a crop against a 13-cut grid and produced `MISSING` FAILs across the board.

### E5. Proof — corpora still reproduce, byte-identically

The §4 driver was run a third time, after the moves. Both diffs are empty `[measured]`:

```
diff corpus_before.json corpus_after_move.json   -> identical (pre-cleanup baseline)
diff corpus_after.json  corpus_after_move.json   -> identical (post-delete run)
```

False-positive set 156 cuts **FAIL 0 · WARN 0** · history set 94 cuts
**FAIL 1 · WARN 2** · both T3 pairs **quiet** · the same three firings (scene18 spec 67.6,
scene17 10.2, scene19 11.1) with identical values. Three runs, one number.

### E6. Stray experimental scene files — none found

`scenes/` and the repo root were scanned for untracked experimental scene files
(`_t0_*.py`, `veg_test*`, spike copies, `*.bak`, `*.orig`, `*_copy*`) `[measured]`:

- **`scenes/` is entirely tracked.** All 21 `scenes/main/scene*.py` and 12
  `scenes/batch1/scene*.py` are in `git ls-files`; `assets`, `look_check`,
  `scene_common.py` and the four `*_kit.py` entries are **tracked symlinks** to the repo
  root (created by `scripts/rounds/reorg_scenes_main.sh`) and resolve correctly. Nothing untracked.
- `scenes/archive_v3/` — 7 tracked v3 scene files, already segregated. **Not touched.**
- `scripts/spike_realism.py` matched the `spike*` pattern but is **tracked** and is the
  live driver for `scripts/rounds/run_p1_spike.sh` — a tool, not debris. Left alone.
- **No `scenes/_experiments/` was created**, because there was nothing to put in it.
- The only untracked non-`look_check` files in the repo are five
  `Docs/reports/w2d_edit_g{1,2,3,b}.md` / `w2d_translation.md` — W2-D reports from another
  session, not experimental scene files. **Not touched**, flagged here for the supervisor.

Note that `scenes/main/look_check` and `scenes/batch1/look_check` are symlinks to the same
`look_check/`, so the new structure is visible identically through all three paths.

### E7. Docs updated

- **`look_check/README.md`** — new §1 *Structure* (layout diagram, the scene-root-vs-
  `_experiments` rule, the "do not render gates/crops into the scene root" rule, and the
  symlink policy with its two constraints); §2 naming examples now show arms going
  straight into `_experiments/`; the legacy decoder gained relocation columns.
- **`look_check/INDEX.md`** — rebuilt: §0 layout + rules, §1 location rollup, §2 era
  rollup, §3 the 223 scene rounds **with a `location` column**, §4 the 81 `_experiments`
  entries by topic, §5 the before/after latest-round table, §6 the full old→new
  **relocation map** for every path cited by a pre-07-30 report.

### E8. Incidental find — two pre-existing broken symlinks, fixed

A repo-wide `find . -xtype l` (run to verify E3) turned up two dangling symlinks that
**predate this mission** (both stamped 2026-07-27 17:06, both tracked in git) `[measured]`:

| symlink | was | now |
|---|---|---|
| `Docs/legacy/multi_scene_brief_v3.md` | `briefs/multi_scene_brief_v3.md` (dangling) | `../briefs/multi_scene_brief_v3.md` |
| `Docs/legacy/realism_rubric_v1.md` | `reports/realism_rubric_v1.md` (dangling) | `../reports/realism_rubric_v1.md` |

Both were missing the `../` hop out of `Docs/legacy/`; the real files were always present
at `Docs/briefs/` and `Docs/reports/`. Fixed with `ln -sfn`; both now resolve
(71 and 262 lines). **`find . -xtype l` over the whole repo now returns 0** — the two
symlinks created in E3 are the only ones added by this mission and both resolve.

### E9. Note on git state

Between the two passes of this session a **concurrent session committed pass 1** as
`0f4fced` ("look_check 정리 — 5.33GB 확보…"). `look_check/README.md` and `INDEX.md` are
therefore now tracked (the `.gitignore` negation of §5-7 is what made that possible), and
this pass leaves them as unstaged modifications. **This mission made no commit**, as
instructed. Remaining unstaged/untracked, for the supervisor:

- ` M look_check/README.md`, ` M look_check/INDEX.md` — this pass's rewrites
- ` M Docs/legacy/{multi_scene_brief_v3,realism_rubric_v1}.md` — the symlink fixes (E8)
- ` M Docs/reports/cleanup_lookcheck_v1.md` — this extension
- `?? Docs/reports/w2d_edit_g{1,2,3,b}.md`, `?? Docs/reports/w2d_translation.md` — another
  session's W2-D reports, untouched
