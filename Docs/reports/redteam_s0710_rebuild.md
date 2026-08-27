# Red team — S3 scene07/10 rebuild, adversarial exit verification

> **Wave**: W3 · **Lane**: S3 07/10 REBUILD exit gate · **Date**: 2026-07-31 (round family `260731_w3_*`)
> **Branch**: `feat/realism-v1` · lane range audited `564cd3d..1333581`; verification snapshot at `0711973`
> **Method**: re-run, not re-read. Every load-bearing claim was re-executed on clean `git archive`
> snapshots (assets symlinked) or against the on-disk rounds; nothing below is quoted from a lane
> report without an independent reproduction, except where explicitly marked *(record-only)*.
> **Verdicts**: K4M **PARTIAL** · S07 **CONFIRMED** · S10 **PARTIAL** · lane exit **PARTIAL** (§7).

---

## 0. What was re-executed

| # | Check | How | Result |
|---|---|---|---|
| 1 | K4M 33-scene prim-hash A/B | two `git archive` arms — A = `564cd3d`, B = `1346b70` — `scripts/geom_invariance_check.py --baseline` in each, JSON diff | **99/99 hashes identical · 33/33 prim counts identical · Σ 29,245 prims both arms** — the report's numbers reproduced exactly |
| 2 | K4M blob identity | `git rev-parse 1346b70:scene_common.py` vs `git hash-object scene_common.py` | both `147f78a…` — the proven arm **is** the live file; no drift since |
| 3 | §6.1 floor at exit | clean snapshot of `0711973`: `py_compile` (07 · 10 · scene_common) · `NEGOBS_SMOKE=1` both scenes · **unscoped** `geom_invariance_check` · `placement_lint --scenes scene07,scene10` | all green — **R-4 33/33 · R-6 33/33 unscoped** (closes `w3_s07_rebuild_v1.md`'s open item: the 33-scene run that had failed on scene10's in-flight `KeyError: algae` now passes with scene07 = 1420 prims, scene10 = 2777) |
| 4 | GT-14 R-1 numbers | scene07 SMOKE at exit snapshot | bit-for-bit: open-slope **0.000 %**, max inter-course gap −0.0936, interlock 0.0602–0.1791 ≥ 0.050, rise 0.1270–0.1745 mean 0.1489 Σ 4.170000, entry +0.1456, **exit +0.0300 labelled UP-STEP** (GT-1 rule (b) cited in the print), bed −0.33 with `path_z` untouched, junction −4.200 intact |
| 5 | GT-18/19/20 R-1 numbers | scene10 SMOKE at exit snapshot | 8+7+8+7+7+7 = 44 · 2R+T 0.610 ∈ [0.600, 0.650] · width 1.50 · plan overlap 0.000000 m² both kinds · air gap 0.020–0.600, stair foot 0.250 ≤ 0.300 · leaf band re-derived to −0.145/−0.295 · broken bay exactly `LandRail_0_Out` · round members 0 · rail 1.100 · lattice 1 bay `EntryRail_P` · silhouettes 3, windows 0, d_true 81.4 |
| 6 | GT-14 R-2 | `check_data_run.py 260731_s07_recache` re-run; `dataset/_archive/scene_dev_2607/260731_s07_recache` on disk (8 PNG + manifest) | [1]–[5] all PASS, 3.16 s/cut; the only 2 FAILs are the zero-sample cross-condition checks (`0 pairs ≥ 0.3 EV`, `0 scene-pairs`) — exactly as recorded verbatim in the ledger |
| 7 | STEP-0 pre-round adjudication | `regression_check.py --before 260730_w2d_fix --after 260731_w3_pre10 --only <5 preset cuts>` re-run | **FAIL 0 · WARN 1 `[UNCHANGED]` (0.24 LSB mean · 0.063 % > 4 LSB) · INFO 2 · PASS 2** — identical to the GT-18 record. CB-2's scene10 delta (`11d1e56`, **+29/−23 re-measured by numstat**) is thereby verified null on the judged cuts, so the s10-vs-pre10 diff is attributable to the rebuild alone |
| 8 | near-ground band claims | `near_ground_stats.py` re-run, 07 (s07 vs cb2) and 10 (s10 vs pre10), h0.3 band | 07 flat as claimed (σ_LF 13.69→13.69 · 22.88→22.97 · 4.08→4.10; edge% 80.8→79.3 · 50.6→50.3 · 90.3→90.3). 10: `flat_gnd` 3.5→0.4 · 0.1→0.0 · 0.7→0.0 cleared; the two declared h0.3_d2 WARNs (mean 181 > 170, wht 7.6 ≥ 2) present and not tuned away |
| 9 | Regression JSONs | parsed `regr_260731_w3_s07.json` / `regr_260731_w3_s10.json` | 07: pair cb2→s07, **FAIL 2 only** (`h0.9_d2` FRAME declared · `h0.3_d2` GRAZE), 9 extra cuts came back **NEW-VIEW/INFO** — the §6.4 5-vs-13-cut MISSING-FAIL trap did not fire. 10: pair pre10→s10, FRAME 5/5 declared, OCCL 1 WARN (`h0.9_d2`), BLOWN/WHITE 0 |
| 10 | placement_lint delta | scoped run in **both** trees (pre-lane `1346b70` arm vs exit snapshot) | scene10 ERROR **9 → 0** (LINT-4b species pinning, as claimed), WARN 9 → 9, BLOCK 1 → 1 · scene07 ERROR 3 → 3 (pre-existing, delta 0), WARN 9 → 6 |
| 11 | Leaf-off mechanism | usd-core 26.8 isolation test on `Gray_Birch.usd` + material audit of all three bare species + pixel check of the round | **defect found — §1.2/§5** |
| 12 | Eyes | both target images first, then 8 round frames + 2 committed crop montages | §5 |

---

## 1. K4M (`1346b70`) — verdict **PARTIAL**

### 1.1 The commit's license holds (all four task checks pass)

- **33/33 prim-hash A/B re-run** (check 0-1): geometry provably untouched; the license for the
  §8.R OQ-3 micro-commit is genuine, and the committed blob is the proven arm (check 0-2).
- **`TEX["moss"]` consumers**: exactly one real consumer in the tree — `scene07:1892`
  (`make_pbr` with `nor=None`, honouring the commit's own GL/EXR caution); everything else is
  comments. No other scene binds the role. The three files named in the registry exist on disk
  with exactly the committed names (`diff` JPG · `nor_gl` EXR · `rough` **JPG** — the spec's
  `.exr` roughness correction is real).
- **Kwarg discipline**: `build_tree(..., bare=False)` appended last, default OFF;
  `_deactivate_seasonal(..., table=None)` defaulting to the legacy registry — both
  signature-preserving; the `bare` branch is dead in the commit (that is what the 99/99 proves).
- Exactly two files in the commit; no scene file, no GT row, no render. Pathspec-only.

### 1.2 But the mechanism it ships cannot do its job on instanced trees — **CONFIRMED DEFECT**

Isolation test (usd-core 26.8, same stage semantics as the render runtime), reference
`Gray_Birch.usd` on `/X/Asset`, then traverse with instance proxies:

```
plain reference, leaves deactivated        → visible meshes ['trunk']            (works)
deactivate FIRST, then SetInstanceable     → visible meshes ['trunk', 'leaves']  (silently undone)
SetInstanceable first, deactivate after    → hard error: "authoring to an instance proxy is not allowed"
```

USD composition ignores local opinions beneath an instanceable prim **regardless of authoring
order** — ordering only converts the loud failure into a silent one. The K4M code comment
("Leaf-off BEFORE instancing… order matters") and the `place_shrubs` precedent it cites are
therefore wrong as semantics: `scene_common.py:2924` (`place_shrubs`) has carried the same
deactivate-then-instance pattern all along, so the Rhododendron flower-strip has been
composition-inert for instanced shrubs too — **the trap is library-wide and predates K4M; K4M
copied a broken in-repo precedent and its "exercised separately against a real USD stage" test
verified the pre-instancing state, not the composed result.**

Material audit: all three bare species bind **bark-only** materials in the trunk subtree
(`Gray_Birch_Bark_Mat`, `bark3`, `bark3`), so a *composed* bare tree cannot show green. The
pilot round shows green birch canopies (§5.2) — pixels agree with the semantics: the
deactivation did not survive.

Blast radius: `build_tree(bare=True)` (nobody calls it yet), scene10's `_bare_tree`
(12 trees — see §5.2), any instanced `SEASONAL_SUBPRIMS` strip. Fix direction (not executed —
K4 territory): author the strip **inside** a scene-local over-layer of the reference target, or
reference with an excluded prim, or leave bare trees un-instanced (12 × ~118 k tri is far below
§12-14's threshold of concern), or `SetInstanceable(False)` + per-mesh treatment as the MDL
workaround already does.

---

## 2. Ownership audit (`git log --stat 564cd3d..0711973`) — **CLEAN**

29 commits in the audited range; every one classified:

- **This lane (22)**: 12 scene commits — 8 × `scene07_temple_stone_path.py` only, 6 ×
  `scene10_park_deck_switchback.py` only (two commits touch each scene's pilot fixes) — every
  scene commit touches **exactly one** scene file; 1 × K4M (`scene_common.py` + its report);
  5 × ledger-only; 3 × reports/regr/crops (+ ledger landing rows). Nothing else.
- **Foreign, separately authorized (7)**: intake v2 lane (`cb27bef` reference photos,
  `6d2d2af`/`bfda63d` survey docs — Docs only) and N2-CLEAN lane (`ec76030` sceneN2 + report,
  `c06ffda`/`f831d61`/`0711973` report/stamp commits). Not S3 07/10 files; noted, not charged
  to this lane.
- **sceneC2: 0 commits** — the §8.R scope-guard deferral held.
- **`scene_common.py`: exactly 1 commit** (`1346b70`) — the single authorized micro-commit.
- **`scripts/`: 0 commits**; `scripts/rounds/`: no new files (newest mtime 07-28; the R-3
  runner lived in scratch, per the ledger record — convention honoured).
- **assets/**: no commits at all — the additive-asset allowance went unused (both texture sets
  were already on disk). Untracked `assets/coastal/` in the worktree belongs to another lane.
- **Pathspec discipline**: no commit in the lane sweeps in the concurrently-dirty files
  (scene04/16/18, intake drafts) — every `--stat` matches its message.
- **Timeline coherence**: `260731_w3_pre10` stamped 15:24 at head `1346b70`, inside the
  15:20–15:37 gap before the first scene07 commit — the §6.4-1 "render the intermediate round
  at HEAD **before S3-8**" ordering is real, not narrated. All 8 GT rows show
  declare-commit ordering (3c84961→cd2745b/bbf085d · ce31b51→ed928e5 · ffc9d39→c2b6841 ·
  376f622→5ce512e · 584f1d0→1962f76) — **§0-1 append-before-land held 8/8**.

---

## 3. GT ledger — protocol held; two stale figures need an amendment line

**Held**: rows GT-14…GT-21 all present; GT-14…17 `LANDED` with §4 records carrying the real
commands; GT-18…21 correctly held **OPEN** because **scene10's R-2 is owed** — no
`dataset/` run for scene10 exists, and the record says so instead of guessing the data owner's
invocation (§0-3). Both landing records name their comparison baselines (`260731_w3_cb2` /
`260731_w3_pre10`) per §6-W4. scene07's exit lip is labelled **up-step** in the row, the
landing record, and the live SMOKE print. Frozen invariants (07 `path_z`·`SIDE_DROP`·junction;
10 total drop 6.600·broken bay·leaf band) re-confirmed live at the exit tree — none
re-baselined. scene07's full re-cache is genuinely full: R-1 reproduced (check 0-4), R-2
re-checked on disk (0-6), R-3 committed and re-parsed (0-9).

**Findings** (accuracy, not protocol):

- **F3 — GT-14's z-profile column still says bed `z0 0.00 → −0.22 m`; the landed value is
  −0.33** (`scene07:220 corridor_bed=0.33`, report §, commit message, and the SMOKE print all
  say −0.33). Declared −0.22 at `3c84961`, landed −0.33, and the landing edit (`c09fa47`)
  rewrote the row without correcting it. Geometry is internally consistent (tread-back
  clearance +0.0526 re-verified); the ledger figure is what's wrong. One amendment line owed.
- **F4 — GT-20's "20 newels deduplicated from 28 run endpoints" is a pre-de-stacking
  snapshot**; the landed scene has **28 newels from 40 endpoints** (SMOKE, exit tree). Same
  class: landing records written from commit-time state, not re-derived at batch end. One
  amendment line owed.

---

## 4. Regression legitimacy — **CONFIRMED** (one process nit)

- 07 adjudicated against `260731_w3_cb2` (5-cut, git_head `c2676d6`, stamped) — pair named in
  the JSON; **FAIL 2 = the declared FRAME + the GRAZE that was adjudicated by eyes**; the crop
  (`crops/graze_band_h0.3_d2.png`) supports the adjudication — the shoulder is *more* readable
  (articulated courses + apron + kerb), not concealed. The 9 cuts absent from the 5-cut
  baseline surfaced as `NEW-VIEW/INFO`, not MISSING FAILs — trap §6.4-2 avoided.
- 10 adjudicated against **its own stamped intermediate round** `260731_w3_pre10`
  (exists · stamped · git_head `1346b70` · view list byte-identical to cb2's). Its
  adjudication carries CB-2's +29/−23 delta by *verifying it null* — and I re-ran that
  comparison from the on-disk rounds and reproduced it to the LSB (check 0-7). FRAME 5/5
  declared in advance; DARK improved on all five; BLOWN/WHITE 0; OCCL a single WARN with the
  declared cause; near-ground movements re-measured and matching (check 0-8).
- New baselines-of-record: `260731_w3_s10`'s stamp carries `baseline_of_record: true`,
  `comparison_baseline_used`, and a supersedes note — exemplary. **`260731_w3_s07`'s stamp
  carries no such marker** (F5); its baseline-of-record status lives only in the ledger,
  report and commit message. Minor, but the next lane will read the stamp first.
- Process nit (F9): `round_stamp.json` records `dirty_files: 5–7` as a bare count — with four
  lanes sharing the worktree, the stamp should list the paths so a reviewer can prove the
  dirty files were foreign. (Here the SMOKE bit-for-bit reproductions at the committed tree
  make the point moot for 07/10 geometry.)

---

## 5. Eyes — against the two target images (viewed first, per lane law)

### 5.1 scene07 vs G7 — **reads as the archetype; declared residuals stand**

`stone_rhythm` / `h0.9_d2` / `h0.3_d2` band / `gate_frame` / before-after-target montage:
courses of 2–4 bedded slabs with ragged 0.06–0.12 m front-edge offsets, tight soil joints,
**zero open slope** — the 디딤돌-path read is gone; discontinuous 야면석 kerb both flanks
standing proud; summer floor (autumn `leaf_ground` off the corridor/terraces, lobes re-sited
inside single treads at the margins); switchgrass fern stand-ins at the walls; moss legible
mostly at joints/risers per the zone table (subtle at grid distances — matches the printed
fractions, not a defect). Roof cluster + wooden pole appear **only** in `gate_frame`
(structurally impossible in the +X presets — §0.2 honoured, H16 respected). No nosing strip;
kerb boulders sit on the shoulder, terrace edge unguarded (H2/H8). **Zero humans, zero
vehicles in every frame viewed.** Residual gaps are the report's own: no canopy tunnel
(measured DARK/OCCL trade, A/B on record), moss greener in G7 than ours, gate_frame's roofs
read procedural at close inspection — all declared, all in-lane decisions.

### 5.2 scene10 vs G10 — geometry/materials **CONFIRMED**; season pin **PARTIALLY UNDELIVERED**

`reversal` / `broken_rail` / `through_treads` / `from_below` / `leaf_edge` / `h1.8_d10`:
a genuine traversing switchback on an open litter slope — flights tile +X, 90° turn landings,
nothing stacked, daylight under the deck; masonry shaft **gone** (short head wall only);
square-section timber throughout — capped newels proud of the rail, flat-laid top rail, dense
plumb 38 × 38 balusters, one lattice bay (in-frame in the preset cuts, as designed); silvered
grey-brown patina with darker verticals, measured-band; `broken_landing = 0` bay present with
posts standing; **open risers present** (`through_treads`), the declared research divergence
from G10's closed boards; continuous brown 3-D litter + kept CB-2 lobes; bench/waymarker/
pergola anchors kept (H12). **Zero humans, zero vehicles in every frame viewed.**

**F1 — the "12/12 leaf-off" arm of GT-21 is not what the pixels show.** The trail trees at
e.g. (16.0, −5.0) and (−6.0, 5.5) — Gray_Birch slots of the census — render with **green
foliage** (`from_below` foreground, `h1.8_d10` upper-left). Cause is §1.2: the `/Root/leaves`
deactivation is discarded when `_bare_tree` makes the prim instanceable; the `n_bare = 12/12`
log counted *authored* opinions, not composed results — made in good faith, wrong in effect.
Consequences contained: far-belt junipers/shrubs/tints/litter are real (the straw R/G 1.22
ground reads correctly), DARK/OCCL/near-ground results are measured off the actual (leafed)
pixels, and no walked surface is involved — but the 만추 pin's defining element ("the ref's
defining element is leaflessness", spec §2.A.4) is only partially on screen. Needs a K4-side
fix + a scene10 re-render of the 5 preset cuts + `from_below`; GT-21 should not be closed to
LANDED before that.

Secondary eyes notes: **F6** — the dormant-tinted crest-hedge blobs read as bald tan domes in
`h1.8_d10` (a cut with no baseline this round, hence unadjudicated); flag for 통람 v3.
**F7** — the tread leaf-band texture (`M["leaf"]`, C2 role) reads distinctly green-tinged at
`through_treads` magnification — fine at grid distance, spring-ish at macro; consider the
GT-21 tint arithmetic for this band too. **F8** — scene07 carries 3 pre-existing LINT-4b
retired-species ERRORs (`BackTree_0`/`Pine_S2`/`RidgeTree_2`, White_Pine/Yellow_Pine draws)
that the rebuild neither fixed nor mentioned; scene10 fixed its 9 by pinning species without
waiting for K4(b), so the same in-file route is open to 07.

---

## 6. Findings, ranked

| # | Sev | Finding | Owner / action |
|---|---|---|---|
| **F1** | **HIGH** | Leaf-off (`BARE_SUBPRIMS` / `bare=` / `_bare_tree` / `place_shrubs` seasonal strip) is composition-inert on instanced prims — order does not save it; scene10's 12 "leaf-off" trees render leafed; the trap is library-wide (`scene_common.py:2537-2553`, `:2924`) | K4 micro-fix + scene10 re-render of judged cuts; GT-21 stays OPEN; audit other `SEASONAL_SUBPRIMS` consumers |
| **F2** | MED | scene10 R-2 owed → GT-18…21 correctly OPEN; lane cannot claim FULL re-cache for 10 until the data owner runs `run_data_render --scenes scene10` + `check_data_run` | data owner; then T5 closes rows |
| **F3** | MED | GT-14 ledger row says bed −0.22; landed −0.33 (code/report/SMOKE) | T5/S3: one amendment line, append-only |
| **F4** | LOW | GT-20 record's "20 newels / 28 endpoints" is pre-de-stacking; landed = 28/40 | same amendment commit |
| **F5** | LOW | `260731_w3_s07` stamp lacks the `baseline_of_record` marker that s10's stamp carries | X1: restamp or note |
| **F6** | LOW | Crest-hedge dome read at `h1.8_d10` (unadjudicated tier) | 통람 v3 queue |
| **F7** | LOW | Tread leaf-band texture green-tinged at macro (`through_treads`) | S3 follow-up with F1's re-render |
| **F8** | LOW | scene07's 3 pre-existing LINT-4b ERRORs survive the lane un-flagged | S3 next 07 touch (scene10's pinning route works without K4(b)) |
| **F9** | INFO | Round stamps record dirty-file count, not list | tooling nicety |

**Verified-good** (each independently re-executed): 99/99 A/B identity · blob identity ·
single-consumer moss role · ownership/pathspec/sceneC2/scripts clean 29/29 commits ·
declare-before-land 8/8 · baselines named · up-step labels · R-1 bit-for-bit both scenes ·
R-2(07) re-checked · pre10 STEP-0 reproduced to the LSB · near-ground claims reproduced ·
NEW-VIEW trap avoided · unscoped geom 33/33 at exit · lint 9→0 (10) / delta 0 (07) ·
zero humans/vehicles in all viewed frames · frozen invariants intact.

---

## 7. Verdicts

| Target | Verdict | One line |
|---|---|---|
| **K4M** | **PARTIAL** | Commit license fully re-proven (99/99 · additive · default-OFF · signature-preserving; zero geometry) — but the leaf-off mechanism it introduces is provably inert under instancing (F1), and its "real USD stage" test missed exactly that |
| **S07** | **CONFIRMED** | Every claim re-executed and reproduced (R-1/R-2/R-3, 0 % open slope, up-step, flat near-ground, declared FAILs, eyes match); residuals are declared decisions; two ledger-figure nits (F3 shared, F8) |
| **S10** | **PARTIAL** | Rebuild/railing/de-stacking/terrain/materials confirmed in numbers and pixels; but R-2 owed (rows OPEN, correctly) and GT-21's leaf-off arm is not on screen (F1) — season pin partially undelivered |
| **Lane exit** | **PARTIAL** | Process exemplary (ownership, pathspec, GT protocol, baseline discipline, honest owed-items); exit blocked on: F1 fix + scene10 re-render, scene10 R-2, and the F3/F4 ledger amendment lines |

*Floor for this report's own commit: Docs-only — no Python touched; the §6.1 floor was
nonetheless executed in full on the exit snapshot (check 0-3) and is recorded above.*
