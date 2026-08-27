# S5 Docs / top level / living onboarding doc — stage report (2026-08-27)

Branch `chore/reorg-0827`, repo `/home/vislab/Desktop/work_sy/Practice_NegObs`.
Nothing was committed. `Practice_NegObs_edge` was not touched. No GPU work, no
renders, no training. Every count comes from `os.walk` (`scripts/reorg/s5_scan.py`),
never from `grep -r` — this shell's `grep` is ugrep with `--ignore-files` and silently
skips `dataset/`, `look_check/`, `*.log`.

**Status: PASS.** All 10 gates green.

| headline | measured |
|---|---:|
| entries moved / deleted | **22 files moved · 10 symlinks deleted** (`docs_moves.tsv`, 44 rows = 27 move hops + 10 deletions + 2 dir rows + 5 new files) |
| citation edits | **113 files · 198 substitutions** (`docs_citation_edits.tsv`, 158 rows) |
| symlinks total / broken | **5,734 / 0** — **the invariant changed on purpose: 5,744 − 10** |
| `PREREG_V3.md` sha256 | `05f41322…f56a` **unchanged** (edited once by mistake, reverted, guard added) |
| `PREREG_CUEOFF.md` sha256 | `9c4733bb…56b1` unchanged |
| retired-path residual scan | **14 patterns · 0 hits** outside `Docs/reorg_0827/` + 2 declared |
| `smoke_round_sites.py` | **33 PASS · 0 SKIP · 0 FAIL** |
| `import_check.py --all` | 246 modules · OK 208 · EXC 36 · SYSTEMEXIT 2 · **0 files changed content**, rc 0 |
| `test_round_dir.py` | **15 / 15** |
| `py_compile` / `bash -n` | 52 `.py` OK · 8 `.sh` OK |
| `Docs/` link resolution | 278 cited paths · **0 broken into any path S5 created** |
| `__pycache__` | 0 |
| modified tracked files | **339**, of which S1 2 · S2 156 · S3 66 · S4 27 · S5 110 — **0 unexplained** |

---

## 1. What moved (`Docs/reorg_0827/docs_moves.tsv`, 44 rows)

| # | move | rows |
|---|---|---:|
| 1 | `Docs/legacy/{5 real files}` → `Docs/archive/legacy/` (`git mv`) | 5 |
| 1 | `Docs/legacy/{multi_scene_brief_v3,realism_rubric_v1}.md` — symlinks into **current** docs — deleted; `Docs/legacy/` removed | 2 |
| 2 | the 7 root compat symlinks `Docs/<name>.md` — deleted after the citation rewrite | 7 |
| 2 | `Docs/surveys/real_reference_expansion.md` (symlink) — deleted, real file kept at `Docs/reports/` | 1 |
| 3 | `Docs/experiment/` → `Docs/campaign/` · `Status/` → `status/` (`git mv`) | 12 + 2 dir rows |
| 4 | `PROJECT_STATE_{0820,0823,0823_v2,0823_v3}.md` → `Docs/archive/campaign_status/` | 4 |
| 4 | `PROJECT_STATE_0826.md` (untracked) → `Docs/campaign/status/PROJECT_STATE.md` | 1 |
| 6 | the 5 root `run_*.sh` → `scripts/rounds/` (`git mv`) | 5 |
| new | `experiments/README.md` · `REORG_0827.md` · `experiments/v3_0823/PREREG_V3_PATHMAP_0827.md` · `scripts/reorg/s5_{residual_gate,link_check}.py` | 5 |

The 5 `PROJECT_STATE_*` files each moved **twice** (into `Docs/campaign/status/` with the
directory rename, then on to their final home), which is why 22 distinct files produce 27
rows. `git status` shows exactly **10 `D` lines — the 10 deleted symlinks — and nothing
else**; every moved file appears as `R`/`RM` paired with its old path (14 `R` + 7 `RM` = 21
tracked renames; the 22nd file, `PROJECT_STATE.md`, is untracked).

## 2. What was rewritten (`docs_citation_edits.tsv`, 158 rows / 113 files / 198 substitutions)

| tag | files | occurrences |
|---|---:|---:|
| S5-1 `Docs/legacy/` → `Docs/archive/legacy/` | 3 | 9 |
| S5-2 the 8 compat paths → their real paths | 46 | 54 |
| S5-3 `Docs/experiment/` → `Docs/campaign/` (`Status/` → `status/`) | 44 | 83 |
| S5-4 dated `PROJECT_STATE_*` → archive / the living file | 15 | 20 |
| S5-6 `run_p2_all33.sh` → `scripts/rounds/run_p2_all33.sh` | 11 | 15 |
| S5-9 `dataset/<run>` doc placeholders → `dataset/<group>/<run>` | 7 | 10 |
| S5-HAND record-keeping edits (see §3) | 7 | 7 |

The rewriter is `scripts/reorg/s5_rewrite.py`: literal, byte-exact, longest-first, one pass
per file, optional left/right boundary guards, `os.walk` over 14,041 text files,
`Docs/reorg_0827/` always excluded. It appends its own ledger rows, so the ledger cannot
drift from what was written.

**Counting note.** The brief said 46 files cite the 7 compat paths; the `os.walk` scan found
**47 files / 62 occurrences** — the 47th is `Docs/reports/repo_reorg_v1.md`, which is the
08-14 record *of the symlinks themselves* and was fixed by hand instead (§3), leaving 46/54
for the mechanical pass. 32 of the 46 are `scenes/*.py` docstrings; all still compile.

## 3. Four documents where a mechanical rewrite would have falsified the record

These are the judgement calls of this stage. Each was fixed by hand so that the historical
statement stays true **and** the residual scan still comes back 0.

1. **`Docs/reports/repo_reorg_v1.md` §1.1** is the table of the 8 compat symlinks the 08-14
   reorg *created*. Rewriting its left column to the real paths would have produced rows
   reading "`Docs/briefs/multi_scene_brief_v3.md` → `briefs/`". The column header now says
   "심링크 (`Docs/` 아래 파일명)" and the cells carry bare filenames, plus a dated note that
   all 8 were retired on 08-27 and why the 08-14 decision was reversed.
2. **`Docs/reports/repo_reorg_v1.md` §2 anchor 3** declared root `run_p2_all33.sh`
   **이동 금지** because `s04_quality_gap_survey_v1.md:690` cites it by line number `:36`.
   The anchor is now marked released, with the reason it is safe: the file is **87 lines
   before and after** — only three usage-comment paths changed, no line was added — so every
   `:11-13` / `:29-30` / `:36` citation still lands on the same text.
3. **`Docs/reports/cleanup_lookcheck_v1.md` §E8** records fixing the two `legacy/` symlinks
   on 08-05. The mechanical prefix pass turned its table cells into
   `Docs/archive/legacy/multi_scene_brief_v3.md` — a path that has never existed, because
   those two entries were symlinks that were deleted, not files that were moved. The table
   now carries bare filenames under a header naming the folder, plus a dated addendum saying
   both were deleted and where the real files are. `s5_link_check.py` is what caught this.
4. **`Docs/archive/README.md`** gained a "3차 이동" section: one line per archived legacy
   file, plus the rule that there is now exactly one archive.

## 4. The one real mistake, and the guard added

`Docs/experiment/` also appears **inside the sealed `experiments/v3_0823/PREREG_V3.md`**
(lines 9 and 863). The S5-3 pass rewrote it and broke the sha256 invariant. Caught by the
per-step hash check, reverted byte-exactly, hash restored to `05f41322…f56a` — verified
three times since. Two things came out of it:

* `scripts/reorg/s5_rewrite.py` now carries a hard `SEALED = {...}` set and **refuses to
  write** those two files, printing `# SEALED, not written: <file> (n hits)`.
* `experiments/v3_0823/PREREG_V3_PATHMAP_0827.md` (new) is the old→new note for its 2
  stale citations, mirroring S2's `PREREG_CUEOFF_PATHMAP_0827.md`. `PREREG_V3.md` cites
  **no** `dataset/` path (checked), so that is its whole exposure.

The ledger row for the file records `(REVERTED - file is sha256-sealed)` rather than a
substitution, so the record shows the attempt as well as the undo.

## 5. The four maps the owner asked for

* **`Docs/campaign/status/PROJECT_STATE.md`** — the one living onboarding doc. First line
  `최종 갱신 2026-08-27`; no date in the filename. New `§0 2026-08-27 재편 후 현황`
  (7-row table: dataset · finding a round by name · look_check · Docs · top level · what was
  deleted · what was deliberately not touched) and a 6-item "다음에 읽을 것" list. The whole
  08-26 inventory is kept verbatim below a divider — it is the record of where work stopped.
  The **끊긴 세 갈래** table gained a `상태 (2026-08-27)` column; all three read
  "**결론: S6에서 기록**" (DECISIONS.md D102+), which is the owner's standing instruction.
  Three stale claims inside it were corrected in place (README reading order — now fixed;
  finding #25 문서 낡음 — now 수리됨; the `.pt` ignore hole — now closed and the 3 spare
  checkpoints deleted).
* **`experiments/README.md`** (new, 37 lines, Korean) — one row per cycle: dates, one plain
  sentence of purpose, where to start, size. Every file it names was verified to exist.
  Conventions: `DECISIONS.md` is the one ledger; `runs/**` binaries gitignored but the text
  artifacts deliberately tracked; the `venv_yolo` rebuild recipe (python 3.10.12, tracked
  `requirements_yolo.txt`); `yolo_ds/` links are **relative** since S2; resolve rounds by name.
* **`README.md`** (root) — rewritten head: "어디서부터 보나" (8 rows) + "최상위 폴더 한 줄 설명"
  (10 rows with measured sizes), then the original content below a divider. The stale
  cycle-2 reading order (`MORNING_REPORT_0821`, `D1~D30`) is replaced by the current one
  (`PROJECT_STATE.md` → `NEGOBS_STUDY_0823.md` → `MORNING_REPORT_V3.md` → `VERDICT_V3.md` →
  `DECISIONS.md` D1–D101). The `구조` block now shows `_archive/`, `dataset/<group>/<round>`,
  `scripts/{lib,tests,rounds}` and the moved driver.
* **`REORG_0827.md`** (new, 80 lines, Korean) — what moved where, the deletion table with
  sizes and rebuild recipes, how to find a round by name, where the ledgers and revert notes
  are, and §8 "일부러 안 건드린 것".

`Docs/INDEX.md` now opens with a "지도 다섯 장 (Docs 밖)" table linking all four plus
`look_check/INDEX.md` — with the warning that it is **generated**, and the re-run command,
per S4's note 1. It also gained the `campaign/` section, folded `legacy/` into `archive/`,
and replaced the compat-symlink trailer with the record of their deletion.

## 6. Docstring / `--help` placeholders (7 files)

`dataset/<run>` · `dataset/<round>` · `dataset/<정본 A 라운드>` → `dataset/<group>/<run>` etc.,
each with one sentence saying the group is never spelled by hand — `dataset/ROUNDS.json`,
`variation_kit.round_dir(name)`, shell `negobs_round`. English docstrings got an English
sentence, Korean ones a Korean sentence.

`scripts/{sensor_augment,run_data_render}.py` · `experiments/probe_holes_0820/probe_driver.py` ·
`experiments/weekend_0823/cue_audit/build_h_cue_table.py` ·
`experiments/v3_0823/code/{verdict_panels,w1b2_segfill,view_overlay}.py`.
All 7 `py_compile` clean; `run_data_render.py --help` still exits 0.

One is a **behaviour** change, not just a comment: `view_overlay.py`'s `png` argument help
string is now two lines, and `verdict_panels.py:559` is drawn into the panel footer, so the
next `panel_a_fourarm.png` will carry the grouped path. Both are correct; neither was re-rendered.

## 7. Gates

| gate | required | measured | verdict |
|---|---|---|---|
| residual: `Docs/experiment/`, `Docs\experiment` | 0 outside `Docs/reorg_0827/` | **0** (2 declared exceptions) | PASS |
| residual: `Docs/legacy/` | 0 | **0** | PASS |
| residual: the 7 compat names + `Docs/surveys/real_reference_expansion.md` | 0 | **0** each | PASS |
| residual: `PROJECT_STATE_0826`, `Docs/campaign/status/PROJECT_STATE_08*` | 0 | **0** | PASS |
| residual: root `run_*.sh` cited without `scripts/rounds/` | 0 | **0** | PASS |
| `smoke_round_sites.py` | non-zero everywhere | 33 PASS · 0 SKIP · 0 FAIL | PASS |
| `import_check.py --all` | rc 0, nothing moved | 246 modules, rc 0, `!!` lines 0 | PASS |
| `test_round_dir.py` | 15/15 | 15/15 | PASS |
| `py_compile` on every edited `.py` | clean | 52/52 | PASS |
| `bash -n` on every edited/moved `.sh` | clean | 8/8 | PASS |
| symlinks | broken 0 | 5,734 total / **0 broken** | PASS |
| `PREREG_V3.md` / `PREREG_CUEOFF.md` | sha256 unchanged | both unchanged | PASS |
| `__pycache__` | 0 | 0 | PASS |
| `git status --porcelain` | `D` only for the deleted symlinks | 10 `D` = the 10 symlinks; 14 `R` + 7 `RM` = the 21 moves | PASS |
| `s5_link_check.py` | every `Docs/…` path S5 created resolves | 278 cited · 49 broken, **all 49 pre-existing** (absent from `HEAD` too); **0** into an S5-created path | PASS |

**The one broken citation S5 is responsible for is the declared one**: `PREREG_V3.md` and its
path-map note name `Docs/experiment/V3_DESIGN_0823.md`, which no longer exists. It is the
only path in the whole repo that (a) S5 moved and (b) is still cited by a live file — and it
is cited only by the sealed document that may not be edited and by the note that resolves it.
The other 48 dangling `Docs/` citations are the pre-existing 유령 인용 대장 that
`repo_reorg_v1.md` §3 already registers; each was verified absent from `HEAD` as well, so
S5 created none of them and repairing that backlog stays out of scope.

The residual scan is shipped as **`scripts/reorg/s5_residual_gate.py`** (re-runnable,
4 s, `os.walk` over 14,511 files including the gitignored trees, binary extensions skipped).
It encodes the two declared exceptions and says why in its module docstring. The link check is
**`scripts/reorg/s5_link_check.py`** (2 s). **S6 should run both as-is.**

## 8. Two things S6 must know

1. **The symlink invariant is now 5,734, not 5,744.** S5 deleted exactly 10 symlinks — 7 root
   compat + 2 in `Docs/legacy/` + `Docs/surveys/real_reference_expansion.md` — which the brief
   itself instructed. `5,744 − 10 = 5,734`, and **broken is still 0**. Every one is a `D` line
   in `git status` and a row in `docs_moves.tsv`.
2. **Do not interrupt `import_check.py --all`.** It reads its 40 `SIDE_EFFECT_FILES` into
   memory *before* the sweep and writes them back *after*; a run killed in the middle leaves
   15 regenerated artifacts modified, and the **next** run then "restores" them to that
   modified state. That happened here (a 2-minute tool timeout killed the first attempt) and
   was repaired by rewriting all 15 from `HEAD` (`git show HEAD:<path>` — no `checkout`),
   confirmed by re-running the sweep to completion: 0 files changed content, `git status`
   identical before and after. A full `--all` sweep takes about **9 minutes** on this machine.

## 9. Files this stage produced

```
Docs/reorg_0827/S5_report.md                     this file
Docs/reorg_0827/docs_moves.tsv                   44 rows: old · new · kind · bytes · note
Docs/reorg_0827/docs_citation_edits.tsv          158 rows: file · old · new · n · tag
scripts/reorg/s5_scan.py                         os.walk literal scanner (read-only)
scripts/reorg/s5_rewrite.py                      the rewriter, with the SEALED refusal
scripts/reorg/s5_residual_gate.py                the re-runnable residual gate for S6
scripts/reorg/s5_link_check.py                   the re-runnable Docs/ link-resolution gate
experiments/README.md                            cycle map (Korean, 37 lines)
REORG_0827.md                                    reorg map (Korean, 80 lines)
experiments/v3_0823/PREREG_V3_PATHMAP_0827.md    old→new note for the sealed PREREG
Docs/campaign/status/PROJECT_STATE.md            the one living onboarding doc (renamed + §0)
```
