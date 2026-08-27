# S4 look_check — stage report (2026-08-27)

Branch `chore/reorg-0827`, repo `/home/vislab/Desktop/work_sy/Practice_NegObs`.
Nothing was committed. `Practice_NegObs_edge` was not touched. No GPU work, no
renders, no training. Every count comes from `os.walk` / `find` / `du -sb`, never
from `grep -r` (this shell's `grep` is ugrep with `--ignore-files`, which silently
skips the gitignored `look_check/` and `dataset/` trees).

**Status: PASS.** 322 entries moved, 0 rounds lost, every gate at its documented value.

| headline | measured |
|---|---:|
| entries moved | **322** = 262 rounds + 47 review galleries + `_review_w2` + 12 journals |
| bytes moved | **10.86 GiB** (rounds 10.17 · galleries 0.68 · journals 0.01) |
| round dirs before / after | **639 / 639** (live 377 + `_archive` 262) |
| code-derived pinned rounds | **279** — 0 of them archived |
| code ↔ survey-TSV disagreements | **0** |
| citation edits | **29 files · 126 substitutions** (27 automatic + 2 by hand) |
| `valset.py --corpus history --check` | **94 cuts · FAIL 1 · WARN 2** — matches EXPECTED, rc 0 |
| `valset.py --corpus fp --check` | **156 cuts · FAIL 0 · WARN 0** — matches EXPECTED, rc 0 |
| `resolve_round` over `look_check/scene*` | **33/33**, byte-identical to the pre-move run |
| `smoke_round_sites.py` | **33 PASS · 0 SKIP · 0 FAIL** |
| `import_check.py --all` | 243 modules · OK 205 · EXC 36 · SYSTEMEXIT 2, rc **0** |
| `test_round_dir.py` | **15 / 15** |
| symlinks total / broken | **5,744 / 0** (invariant held) |
| PREREG sha256 | both **unchanged** |
| `look_check/` size | 37.29 → **32.03 GiB** (all of it S1's `lighting_spikes` deletion; **S4 deleted nothing**) |

---

## 1. Snapshots (`Docs/reorg_0827/snapshot_before/`, `snapshot_after/`)

| file | measured |
|---|---|
| `snapshot_before/lookcheck_depth3.txt` | **814** dirs at `find look_check -maxdepth 3 -type d` |
| `snapshot_before/lookcheck_scene_du_sb.tsv` | 33 scene dirs, **30,315,749,059 B = 28.23 GiB** — exact match to survey C |
| `snapshot_before/resolve_round_before.tsv` | 33 scenes, 33 resolved, 0 unresolved, 449 png at the heads |
| `snapshot_before/lookcheck_latest_before.tsv` | `ls -t` head per scene, 639 rounds total |
| `snapshot_before/valset_{history,fp}_before.txt` | the two gates **before** anything moved: 94/1/2 and 156/0/0 |
| `snapshot_after/lookcheck_depth3.txt` | **646** dirs (the tree is one level deeper only under `_archive/`) |

---

## 2. The pinned set was re-derived from code, and the survey was right

`scripts/reorg/lookcheck_pins.py` (new, read-only) rebuilds the pinned set from the
four sources the brief names, and prints the reason per round:

| source | how it is read | pins on disk |
|---|---|---:|
| `scripts/valset.py` | **imported**, so `HISTORY` / `FP` / `T3` are evaluated exactly as the checker evaluates them (list comprehensions over `SCENES`) and every `(scene, before)` + `(scene, after)` pair is taken | **168** of 869 declared |
| `regression_check.py` `resolve_round` chain | the `--before-round` chain is parsed out of `look_check/README.md` §4 (**26** names) and out of `regression_check.py`'s docstring (**6** names, all a subset); a chain member is pinned in **every** scene where it exists, because README §4 keeps the tail "as a safety net for the day one of those directories is pruned" | **130** |
| `round_stamp.json` `baseline_of_record: true` | every stamp under `look_check/<scene>/<round>/` | **22** |
| published anchors | `quality_metrics_probe.py` (4 real string constants) + the docstring anchors in `norm_spec.py` / `near_ground_stats.py` / `skyline.py` that README §3 item 2 declares load-bearing | **7** |
| **union** | | **279** |

**Disagreements with `lookcheck_rounds.tsv`: 0.** No round the code pins was proposed for
archiving. The move script re-checks this at run time and **refuses** to archive a pinned
round, so the two can never drift apart silently. The full derivation is saved as
`Docs/reorg_0827/lookcheck_pinned_from_code.tsv` (279 rows, one flag column per source).

The reverse direction is 99 rounds the TSV keeps that no code source names: **96 W4**
(the current wave — kept by master-plan D3, not by code) and **3 docstring anchors**
(`scene01/v7_pt`, `scene09/v8_pt`, `scene18/v7_pt`). Those three were the reason the
anchor scan was widened from `quality_metrics_probe.py` alone to all four anchor scripts;
after widening, the code-derived set is a strict subset of the TSV's keep set and the
only rounds kept on policy rather than on code are the 96 W4 rounds.

### Two things the survey's "0 citations are paths" claim missed

Both were measured with `os.walk`, both were judged **not** to block the move, and both
are recorded here so S6 and the owner can disagree with the judgement rather than
discover it:

1. **23 `.py`/`.sh` files cite an archived round as a path.** 8 are comments/docstrings in
   `scenes/*.py` naming the frames a design decision was read from (`scene05_amphitheater.py:2578`
   `# [look_check/scene05/260806_w3_allview5/pt_noon_plaza_approach.png, crop …]`). The other
   15 are `scripts/rounds/run_*.sh` **write** paths (`NEGOBS_CAPTURE_DIR=look_check/scene19/r4`)
   in the completed render drivers `Docs/INDEX.md` describes as "완료된 렌더 체인 보관".
   Re-running one would render a *new* flat directory beside the archived one rather than
   fail — a duplicate, not a loss. Not rewritten: rewriting them would falsify the record of
   where a past round was written, and `INDEX.md` §6 resolves them by search.
2. **130 path citations across 30 `.md` files.** Same reasoning: these are the reproduction
   commands and evidence pointers of closed reports (`continuity_audit_v1.md` 33,
   `gt_changes_w3.md` 18, `w3_sb_v1.md` 11 …). The doctrine that governs them is already in
   `README.md` §1: *"Paths that were only past evidence were moved without a symlink;
   `INDEX.md` §6 carries the full old-path → new-path relocation map."*
   **The do-not-move register was checked and does not cover them**: `Docs/INDEX.md:39`
   protects "이 문서가 인용하는 48경로(regr json·보고서·크롭·사양)" — and every one of the
   71 distinct paths `gt_changes_w3.md` cites under that heading is a `Docs/` path
   (reports 62 · surveys 4 · briefs 3 · audit_v4 1 · reference_photos 1). No `look_check/`
   round is on it.

---

## 3. Moves (`Docs/reorg_0827/lookcheck_moves.tsv`, 322 rows)

`scripts/reorg/lookcheck_move.py` — `os.rename` only, one filesystem, `--dry-run` by
default. It refuses the whole batch if **any** source is missing, **any** destination
exists, **any** wave is outside `{w2, w2d, w3, w3fix}`, or **any** round is code-pinned.

| class | entries | size | destination |
|---|---:|---:|---|
| free rounds | **262** | 10.17 GiB | `_archive/<wave>/<scene>/<round>` |
| review galleries | **47** | 0.68 GiB | `_review/{w3,w4}/<round>` (35 w3 · 12 w4) |
| `_review_w2/` | 1 | 4.5 MB | `_review/w2/` |
| render journals | **12** | 5.6 MB | `logs/` (11 `*.log` + `spike_results.json`) |

`_archive` breakdown: `w2` 51 rounds / 25 scenes · `w2d` 8 / 4 · `w3` 72 / 33 ·
`w3fix` 131 / 33. **No back-compat symlink was created inside any scene root** — README §1
constraint 1: a symlink carries a fresh mtime and would re-break `ls -t` latest-round
discovery. The two root symlinks (`_t0_spike`, `spike_probe`) and the `_experiments/` path
are untouched.

**Completeness, verified three ways.** (a) every `old` in the log is gone and every `new`
exists — 0/0. (b) 318 depth-≤3 directories disappeared from the before-snapshot; 310 are
logged rows and the remaining 8 are the sub-directories of one logged round
(`scene20/260730_w3r_bldgab`'s seven `arm_*` + `_crops`), which moved with their parent and
are present at the new path. (c) the round count is conserved: **377 live + 262 archived = 639**,
exactly the before-count.

---

## 4. Citation rewrites (`Docs/reorg_0827/lookcheck_citation_edits.tsv`, 29 rows)

`scripts/reorg/lookcheck_rewrite_citations.py` takes its name lists **from
`lookcheck_moves.tsv`**, so it cannot drift from what was actually moved. One pass per
file, right-boundary guarded, `os.walk` over 10 text extensions. Bare round / gallery /
file **names** are never touched.

| transform | files | occurrences |
|---|---:|---:|
| `_review_w2` → `_review/w2` | 6 | 8 |
| `_review/<gallery>` → `_review/<w3\|w4>/<gallery>` | 7 | 96 |
| `look_check/<name>.log` and `look_check/spike_results.json` → `look_check/logs/…` | 15 | 20 |
| **automatic total** | **27** | **124** |
| hand: `scripts/spike_realism.py` — the **writer** | 1 | 1 |
| hand: `scripts/make_review_gallery.py` — `--out` default tidied to `os.path.join(BASE, "_review", "w2")` | 1 | 1 |

Survey C's estimates were 3 / 6 / 16 / 5; the `os.walk` scan found 6 / 7 / 15 / 5 —
`grep`'s `--ignore-files` had hidden the rest.

**The two live defects this fixed**, as opposed to the documentary ones:

* `scripts/spike_realism.py:596` wrote `os.path.join(OUT_ROOT, "spike_results.json")`,
  i.e. straight back into the `look_check/` root. It is now
  `os.path.join(OUT_ROOT, "logs", "spike_results.json")` with an `os.makedirs(..., exist_ok=True)`
  above it, so the file the 5 citations point at is the file the script writes.
* `scripts/make_review_gallery.py:116` carries a **real default**
  `--out = BASE/_review_w2` (survey C §1.4 says "`--out` is a required CLI arg, no default
  to fix" — that is true of `make_allview_sheet.py`, not of this one). Left alone, the next
  gallery run would have re-created `look_check/_review_w2/` at the root.

**Residual scan: 0.** Re-running the rewriter finds nothing; a wider scan that also reads
the excluded files finds the old forms only in `Docs/reorg_0827/**` (this reorg's own record
of the OLD paths), `scripts/reorg/**` (the tooling names both forms), and the pre-0827 INDEX
copy — all deliberate.

**Behaviour note for S6.** `make_allview_sheet.py:74 views_of()` picks a substitute view by
scanning the round's **siblings under the scene root**, newest mtime first. That fallback
pool is now the 377 live rounds; an archived round can no longer supply a substitute view.
This is a change in what the sheet draws, and it is the direction the README wants
(fallbacks come from judged/current rounds only) — but it is a change, not a no-op.

Backups: 30 `*.s4.bak` files were written. After the full PASS the 28 whose source is
git-tracked were deleted (`git diff` is the revert path); the 2 whose source is untracked or
gitignored (`Docs/experiment/Status/PROJECT_STATE_0826.md`,
`look_check/_experiments/t0_spike/lab_e1e4.log`) were moved into
`Docs/reorg_0827/bak_s4/`. Ledger: `Docs/reorg_0827/S4_bak_disposition.tsv`.

---

## 5. `INDEX.md` — now generated, not hand-patched

`scripts/make_lookcheck_index.py` (new, 415 lines, stdlib only, Korean headings) rebuilds
`look_check/INDEX.md` **from disk** in 0.15 s. The stale 07-30 file is preserved as
`Docs/reorg_0827/INDEX_lookcheck_pre0827.md` (sha256 `d25de6a4…17ef`, byte-identical copy).

New file: **1,356 lines / 93,657 B**, stamped
`generated from disk on 2026-08-27 by scripts/make_lookcheck_index.py`.

| § | content | measured |
|---|---|---|
| §0 | layout, incl. `_archive/`, `_review/<wave>/`, `logs/`, and the no-symlink-in-a-scene rule | |
| §1 | rollup per **wave** and per **scene** | 639 rounds / 28.23 GB / 377 live / 262 archived |
| §2 | live tree per scene: round · wave · cuts · role · **why it is pinned** | 377 rows |
| §3 | archive tree per wave: scene · round · cuts · MB · **old path** | 262 rows |
| §4 | `_experiments/` and `_review/` with last-write dates | 5 + 3 rows |
| §5 | latest-round discovery **and** `resolve_round`, re-verified at generation time | 33 rows, 33/33 |
| §6 | relocation map, accumulated | 56 rows from 07-30 + **322** from 08-27 = 378 |

Three properties worth stating:

* **The wave classifier was validated, not assumed.** `wave_of()` reproduces the `wave`
  column of survey C's 639-row TSV **639/639**, and the §1.1 rollup it produces reproduces
  survey C §1.2 line for line (42/1.39 · 64/2.81 · 72/3.49 · 30/1.27 · 4/0.04 · 7/0.42 ·
  4/0.21 · 74/3.73 · 105/4.89 · 1/0.15 · 135/4.46 · 96/5.11 · 5/0.25) — an independent
  re-measurement, from a different code path, agreeing to the last round.
* **§6 accumulates.** The generator reads the §6 rows out of the INDEX it is about to
  overwrite and merges them with `lookcheck_moves.tsv`, de-duplicated. History cannot be
  lost by a re-run, and a second run is **byte-identical** (verified).
* **`마지막 기록` is a file mtime, never a directory mtime.** A directory's mtime is bumped by
  a *deletion* inside it: `_experiments/gates/` read "2026-08-27" on the first draft purely
  because S1 deleted `lighting_spikes/` out of it. It reads 2026-07-30 now, which is the truth.
  `t0_spike/` genuinely reads 2026-08-27, and the section says why (the 0827 citation rewrite
  edited one line of `lab_e1e4.log`; no render).

`look_check/README.md` §1 gained the `_archive/<wave>/` and `logs/` entries plus two short
paragraphs: what makes a round free to archive, that the leading underscore hides the tree
from every `look_check/scene*` glob (**so an archived round no longer participates in any
check** — that invisibility is the feature and the risk), and that §6 replaces the symlinks
that are deliberately not there. Everything else in the README is unchanged.

---

## 6. Gates

| gate | required | measured | verdict |
|---|---|---|---|
| `valset.py --corpus history --check` | 94 cuts / FAIL 1 / WARN 2 | **94 / 1 / 2**, rc 0, the same three firings at `scene18 h0.3_d2` (FAIL 67.6) · `scene17 h0.3_d2` (WARN 10.2) · `scene19 h0.3_d5` (WARN 11.1) | **PASS** |
| `valset.py --corpus fp --check` | 156 cuts / 0 / 0 | **156 / 0 / 0**, rc 0; series mode 12 · lookAB 42 · ctx 44 · real 40 · P4 18 | **PASS** |
| `valset.py --corpus t3 --check` (bonus) | 0 / 0 | 8 cuts / 0 / 0, rc 0 | PASS |
| `resolve_round` over `look_check/scene*` | 33/33, same head, no cut loss | `diff` of the before/after TSVs is **empty** — same 33 heads, same 449 png | **PASS** |
| `smoke_round_sites.py` | non-zero everywhere | 33 PASS · 0 SKIP · 0 FAIL | PASS |
| `import_check.py --all` | rc 0, nothing unexpectedly moved | 243 modules · 205 OK · 36 EXC · 2 SystemExit · rc 0; the 20 side-effect artifacts restored, `hazgate.json`/`prims2.json` removed | PASS |
| `test_round_dir.py` | 15/15 | 15/15 | PASS |
| symlinks | 5,744 total / 0 broken | **5,744 / 0** | PASS |
| `PREREG_V3.md` | `05f41322…f56a` | unchanged | PASS |
| `PREREG_CUEOFF.md` | `9c4733bb…56b1` | unchanged | PASS |
| `__pycache__` | 0 | 0 | PASS |

Both `valset` gates were also run **before** the move (`snapshot_before/valset_*_before.txt`)
and returned the identical numbers, so the post-move PASS is a comparison, not a coincidence.

**Accounting of every modified tracked file (240):** S2 155 · S3 66 · S4 28 · S1 2 ·
S2's `ACCOUNTING.md` addendum 1 (`gt_changes_w3.md` is in both S2's and S4's set).
**0 unexplained.** Untracked: the 4 pre-existing items + `Docs/reorg_0827/` +
`scripts/{lib,reorg,tests}/` + `scripts/make_lookcheck_index.py`.

---

## 7. What S5 / S6 must know

1. **`look_check/INDEX.md` is generated. Never hand-edit it.** Re-run
   `python3 scripts/make_lookcheck_index.py` after anything is added, moved or removed under
   `look_check/`. It is idempotent and takes 0.15 s. Its absence is what let the old INDEX
   drift for 27 days. **S5 should link it from `Docs/INDEX.md`** (master plan D5) and should
   consider adding the re-run to whatever checklist closes a render wave.
2. **`_archive/` is invisible to every `look_check/scene*` glob** — `valset.py::_scenes()`,
   `regression_check.py --scenes`, `shortcut_audit.py`, `check_data_run.py`. That is the
   design. It also means an archived round silently stops participating in every check, so
   the only safe way to un-archive is to move the directory back and re-run the two gates.
3. **A round is free to archive iff `lookcheck_pins.py` does not name it.** Run
   `python3 scripts/reorg/lookcheck_pins.py` before proposing any further look_check move;
   `lookcheck_move.py` refuses a pinned round by construction.
4. **The `scripts/rounds/run_*.sh` render drivers still write flat paths** for rounds that
   are now archived (15 files, §2 item 1). Re-running one produces a duplicate flat directory
   next to the archived original, not an error. If S5 touches `scripts/rounds/` for D6, this
   is the moment to decide whether those completed drivers should carry a "this round is
   archived, re-running writes a new copy" guard. **S4 deliberately did not add one.**
5. **`Docs/experiment/Status/PROJECT_STATE_0826.md` was edited by S4** (one `_review/` path).
   D5 renames `Docs/experiment/` → `Docs/campaign/` and `Status/` → `status/`; the file is
   still untracked, and its pre-S4 copy is in `Docs/reorg_0827/bak_s4/`.
6. **`Docs/legacy/STATUS_pre_reorg_260814.md` was edited by S4** (5 `_review/` paths). D5
   moves it to `Docs/archive/legacy/`; the edit travels with it.
7. `look_check/` is **32.03 GiB** now. Survey C's headline said "38 GB"; its own itemised
   table sums to 37.29 GiB, and 37.29 − 5.26 (S1's `lighting_spikes`) = **32.03** to the
   hundredth. **S4 deleted nothing** — every byte it touched was moved.

## 8. Files this stage produced

```
Docs/reorg_0827/S4_report.md                    this file
Docs/reorg_0827/lookcheck_moves.tsv             322 rows: old · new · wave · kind · size_bytes · reason
Docs/reorg_0827/lookcheck_citation_edits.tsv    29 rows: file · n_total · per-transform counts · delta_bytes
Docs/reorg_0827/lookcheck_pinned_from_code.tsv  279 rows: scene · round · valset · regr_chain · stamp_bor · anchor
Docs/reorg_0827/S4_bak_disposition.tsv          30 rows: bak · bytes · source · tracked · disposition
Docs/reorg_0827/INDEX_lookcheck_pre0827.md      the stale 07-30 INDEX, kept for the record
Docs/reorg_0827/resolve_round_after.tsv         the post-move resolution, identical to the pre-move one
Docs/reorg_0827/valset_{history,fp}_after.txt   the two gates, post-move
Docs/reorg_0827/snapshot_before/                lookcheck_depth3 · scene du -sb · resolve_round · latest · both gates
Docs/reorg_0827/snapshot_after/                 lookcheck_depth3
Docs/reorg_0827/bak_s4/                         the 2 backups whose source is not git-tracked
scripts/make_lookcheck_index.py                 the INDEX generator (Korean output, stdlib only)
scripts/reorg/lookcheck_pins.py                 the pinned-set derivation (read-only)
scripts/reorg/lookcheck_move.py                 the move, with the refusal rules
scripts/reorg/lookcheck_rewrite_citations.py    the citation rewrite, name lists read from the move log
```
