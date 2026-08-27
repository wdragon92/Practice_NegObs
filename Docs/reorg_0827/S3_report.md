# S3 code sites — stage report (2026-08-27)

Branch `chore/reorg-0827`, repo `/home/vislab/Desktop/work_sy/Practice_NegObs`.
Nothing was committed. `Practice_NegObs_edge` was not touched. No GPU work, no
renders, no training. `PREREG_V3.md` / `PREREG_CUEOFF.md` were not opened for
writing and their sealed sha256 are re-verified below. Every count comes from
`os.walk` / `find`, never from `grep -r` (this shell's `grep` is ugrep with
`--ignore-files`).

**Status: PASS.** 66 files converted, 178 sites; every edited file passes its
import/syntax check; 33/33 silent-empty smokes returned a NON-ZERO count.

| headline | measured |
|---|---:|
| files converted | **66** (35 `.py` + 31 `.sh`) + `variation_kit.py` |
| sites converted | **178** (93 python + 85 shell) |
| helper wiring added | 35 python import blocks + 31 `source` lines |
| python import check | **36 / 36 OK** (`scripts/reorg/import_check.py`; 35 edited + `variation_kit.py`) |
| shell syntax check | **31 / 31** `bash -n` clean |
| silent-empty smoke | **33 PASS · 0 SKIP · 0 FAIL**, every one non-zero |
| `test_round_dir.py` | **15 / 15** (was 11; 4 added for the new helpers) |
| `stamp_round.py --self-check` | **8 / 8** |
| `regression_check.py --selftest` | **전 항목 통과** (rc 0) |
| `git diff --stat` (S3 files only) | **67 files, +745 / −196** |
| `git diff --stat` (whole tree, S1+S2+S3) | **213 files, +52,743 / −52,159** |
| symlinks total / broken | **5,744 / 0** (invariant held) |
| `.s3.bak` deleted after PASS | **66** files, 1,006,463 B |

---

## 1. The site list was re-derived, not reused

Survey B's "225 sites in 80 files" is a pre-S2 number. S2 already fixed 21 sites
by the text rewrite and 35 more by hand, so the list was re-measured today with
`os.walk` over every `*.py`/`*.sh` in the repo (664 lines mentioning `dataset`
in 173 files), then classified. What remained for S3:

| class | sites | how it was converted |
|---|---:|---|
| `os.path.join(REPO, "dataset", <expr>, …)` | 80 | parser → `round_dir_or_flat(<expr>)` |
| glob by **pattern**, not prefix (`*reg_[ABCD]`, `*_v3p5_*`, a pattern in a variable) | 3 | `rounds_matching(<pattern>)` — see §2 |
| `os.path.join(<DS/DATA const>, <expr>, …)` | *(in the 80)* | same |
| prefix glob `glob(<root>/<prefix>*)` | 2 | `rounds_matching(<prefix>)` |
| `os.path.isdir(<root>/<name>)` feature switch | 2 | `has_round(<name>)` |
| f-string path `join(REPO, f"dataset/{arm}/…")` | 1 | `round_dir_or_flat(arm)` |
| hardcoded absolute root (`r4_pixdiff.py`) | 4 | `DATASET_ROOT` + helper |
| `arm_dir(root, stamp, …)` (serves `--root dataset`) | 1 | resolve by name inside the helper |
| cosmetic re-wraps caused by the shorter call | 3 | same code, re-wrapped |
| shell `"$REPO/dataset/$x"`, `"$D/$1"`, `dataset/${S}_A` | 85 | `negobs_round` / `negobs_round_or_flat` |

**Two shell root constants survey B never listed** were found this way and are
now converted: five label runners set `D="$REPO/dataset"` and then build
`"$D/$1"` — a line that contains no literal `dataset/` at all, so neither the
text rewrite nor a `dataset/`-keyed scan could see it
(`run_h12_label.sh`, `run_h3l1_label.sh`, `run_w2_label.sh`, `run_w3_label.sh`,
`run_n911_label.sh`). `run_n911_label.sh` had **no other** `dataset` line and
would have been missed entirely.

**A pattern is not a round name — audited, one site was wrong.** The parser
converts `os.path.join(<root>, <expr>, …)` on the assumption that `<expr>` is a
round NAME. It skips a literal containing `*`, but it cannot see a *variable*
holding a pattern. Exactly one such site existed —
`cue_extent_audit.py:2018`, `for pat in ("*_v3w1_lib_C*", "*_v3w1c_*",
"*cwave*"): glob.glob(os.path.join(DATA, pat))` — and the parser turned it into
a round lookup that would have silently returned nothing. It was caught by
re-reading every remaining use of the root constants, and all three of that
function's registry globs now go through `rounds_matching()`. Every one of the
**33 distinct arguments** now passed to `round_dir_or_flat()` was then listed
and checked by hand: all are round names (`rnd`, `run`, `round_name`, `brun`,
`f"{stamp}_{arm}"`, `"260820_ctrloff"`, …); `pat` was the only pattern.

## 2. The helper grew three functions (`variation_kit.py`)

S1 landed `DATASET_ROOT`, `rounds_index()`, `round_candidates()`, `round_dir()`
and `data_root()`. S3 added, in the same module (no new file, so the 34 kit
symlinks keep working):

* **`rounds_matching(pattern)`** — the group-aware replacement for
  `glob(<root>/<pattern>)`, the one idiom the regrouping breaks *silently*.
  Returns existing round dirs across flat, `<group>/` and `_archive/<group>/`,
  sorted by round name, each resolved through `round_dir()` so the result can
  never contain a path that does not exist. Group directories are excluded by
  name using `ROUNDS.json`, so `rounds_matching("")` returns **196** rounds —
  exactly the index, verified. The argument is matched against the round NAME
  only: a plain string is a prefix, and one containing `* ? [` is an `fnmatch`
  pattern, because `cue_extent_audit.py`'s registry scan globs `*reg_[ABCD]`
  (10 rounds) and `*_v3p5_*` (71) — wildcards in the middle, which no prefix
  can express and which a flat glob cannot carry across a group directory.
  Live-tree values: `260820_boost_` 16 · `*reg_[ABCD]` 10 · `*_v3p5_*` 71 ·
  `*_v3w1_lib_C*` 5.
* **`has_round(name)`** — the group-aware `os.path.isdir()` for the two places
  that use existence as a *feature switch* (`w1b2_repro_control.py:142,146`).
* **`round_dir_or_flat(name)`** — `round_dir()` when the round exists, else the
  flat `<root>/<name>`. `data_root()` is now defined as exactly this, which is
  the point: **the two must agree**, see §4.

**Why `round_dir_or_flat` and not the strict `round_dir` at most sites.** Nearly
every converted site already owns an "this round is absent" branch — a
`MISSING` verdict row, `note("… absent -- skipped")`, `[skip] not present`, a
`sdir()` that returns `None` and a caller that prints `디렉터리 없음`. Those
branches are the loud part and they are already correct for a round that truly
does not exist. What the move broke is the *other* half: an **existing** round
that a flat path can no longer see, which turns into the same "absent" message
and reads as data loss. `round_dir_or_flat` fixes exactly that half and changes
nothing else. The strict `round_dir` is used where a miss is a bug: the labeller
invocations in the five label runners, `w0_label.sh` / `w1d_label.sh`, and
`relabel_v2s.sh` (which runs under `set -euo pipefail`, so the assignment is
split from the declaration or `local` would swallow the exit status).

`scripts/lib/negobs_paths.sh` gained the shell twin **`negobs_round_or_flat`**;
`negobs_round` is unchanged and still returns non-zero with a message on stderr.

## 3. Renderers: what stays flat and what does not

The rule "a renderer keeps writing flat `dataset/<STAMP>`" is kept — for a
**new** stamp. It is not kept as a blanket rule, and the reason is measured:

`local outdir="$REPO/dataset/${run}/${split}/${scene}"` is **not** where the
frames are written. The frames are written by `run_data_render.py --run <stamp>`,
which computes its root with `variation_kit.data_root()` — and `data_root()`
returns the **grouped** directory for a stamp that already exists. `outdir` is
`mkdir -p`'d, `stamp_round.py --capture-env` writes the env sidecar into it, and
`run_cueoff.sh` / `run_260827_v3w1c_hashgate.sh` read it back
(`ls "$outdir"/*.png`, `scene_ok "$outdir"`).

So a flat `outdir` would disagree with the renderer it precedes: on a re-run of
an existing round the frames land in the group while the sidecar and the
verification look at an empty flat directory — and that stray flat directory
would make `round_dir()` **ambiguous** for every reader of that round.
`negobs_round_or_flat` is `data_root()`'s own rule, so the 12 `outdir` sites now
use it: a brand-new stamp still yields `dataset/<STAMP>/<split>/<scene>`, an
existing one yields where the round actually lives.

Left untouched on purpose: the `case`-pattern **"refusing run stamp" guards**
(they match `$1` against `$STAMP`, no path involved) and the
`[dry] … -> dataset/${run}/…` progress messages (they are text). The guards were
tested on their real bytes — all seven accept their own stamp and refuse a
foreign one with rc 4, `run_260825_v3w0_cuecls.sh` correctly refusing the bare
stamp because its allow-list is the six arms.

## 4. Tests

**(a) imports** — `scripts/reorg/import_check.py`: **36/36 OK** for the files
this stage edited (the 35 converted modules plus `variation_kit.py`), on a bare
`python3` with `PYTHONNOUSERSITE=1`. `--all` widens the sweep to every `*.py`
under `experiments/` + `scripts/` — **239 modules · 201 OK · 2 `SystemExit(0)` ·
36 `ModuleNotFoundError`**, exit code 0 (its before/after sha1 sweep of the tree
found nothing unexpected moved). All 36 are pre-existing and environmental, and
**none is in an edited file**:

| exception | count | what it is |
|---|---:|---|
| `ModuleNotFoundError: torch` | 23 | training / inference modules; no torch on this interpreter |
| `ModuleNotFoundError: labeler` | 5 | `mainrun_0819/code/labeling/*` — run from inside their own directory (re-tried with that cwd: import fine) |
| `ModuleNotFoundError: common_rt` | 5 | `rt_response/code/f1..f5` — same, a sibling module |
| `ModuleNotFoundError: isaacsim` | 2 | `rtx_probe.py`, `spike_realism.py` |
| `ModuleNotFoundError: segmentation_models_pytorch` | 1 | `model_factory.py` |
| `SystemExit(0)` | 2 | `w1c_seg_stale_test.py`, `check_manifest_paths.py` — they run and exit |

**(b)** `scripts/tests/test_round_dir.py` — **15/15 PASS** (11 from S1 plus
`has_round`, `rounds_matching_across_groups`, `rounds_matching_pattern`,
`rounds_matching_live_tree`; the new ones assert the negative controls too — a
group directory is never returned as a round and never matched by a pattern, a
flat not-yet-grouped round is still found, a miss is `[]`).

**(c)** `stamp_round.py --self-check` 8/8 · `regression_check.py --selftest`
rc 0 · `python3 variation_kit.py` self-check PASS · `run_data_render.py --help`
rc 0. (`check_data_run.py --help` exits 1 — pre-existing, it has no argparse.)

**(d) the silent-empty smoke (survey B §6.3 R3) — `scripts/reorg/smoke_round_sites.py`, 32 PASS / 0 SKIP / 0 FAIL.**
A check that returns zero or empty is a FAIL, never a pass. Highlights:

```
hash_gate.PROTECTED (rounds_matching)   PROTECTED=18 (boost 16)
gates_cueoff.round_dirs (prefix glob)   15 (stem,arm) units · 24 scene dirs
12 × sdir()/scene_dir() variation.json  24 png (v2/W1) · 4 png (W0) per unit
w1b2_repro_control isdir switch         has_round A=True · B_smoke=True · 19/15 scenes
w1c_hashgate.unit_dir (manifest read)   1/1 scenes resolve through the manifest
h12_gates.arm_dir (--root dataset)      _archive/v3_scene_build/…_h12probe_A/test/sceneH1 (8 png)
cue_extent_audit                        360 idseg sidecars in 260826_v3w1_lib_B
cue_extent_audit registry patterns      *reg_[ABCD]=10 · *_v3p5_*=71 · *_v3w1_lib_C*=5
c2_audit.heightmap_meta (f-string)      33 scenes over 3 arms
r4_pixdiff (was ABS-HARDCODED)          3 cueoff_A + 3 lineage_on scene dirs
w1b_rimpact module-level glob           648 landed frames over 15 scenes
negobs_paths.sh                         round ok · or_flat ok · strict miss returns non-zero
```

**(e)** `bash -n` on all **31** edited shell scripts: clean. One converted line
was additionally executed verbatim out of the real file
(`w0_label.sh:37`) and returned 19 / 9 / 5 scene dirs for arms A / Brail / Bnose.

## 5. One incident, found and repaired inside the stage

The first import sweep imported **every** `*.py` under `experiments/`, and a
handful of those modules do their work at **module level** and rewrite their
artifact as a side effect of being imported. The sweep therefore was not
read-only: **20 tracked artifacts were regenerated** (6 PNG curve/panel figures,
`w1b_rimpact.json`, `f7_hpair_pixdiff.json`, three `rt_response` markdown
appendices, a PDF, 7 `h_diff` panels, `scene_overview_v4.png`), and two new
files `hazgate.json` / `prims2.json` appeared at the repo root.

Repair, all verified:

* S1's snapshot records **0 modified tracked files** at the start of the reorg,
  and none of the 20 is in S2's 300-file rewrite set — so `HEAD` is exactly
  their correct content. All 20 were restored from `git show HEAD:<path>`
  (byte-compared after writing). No `git checkout`/`reset` was used.
* `hazgate.json` and `prims2.json` were absent from S1's `git_status_porcelain.txt`,
  so they are pure debris and were removed.
* Three files that the sweep also rewrote — `dataset_manifest_v2_full.json`,
  `dataset_manifest_v2s_full.json`, `f7b_noisefloor.json` — are in S2's rewrite
  set and their regenerated bytes satisfy `inverse(current) == HEAD` exactly,
  with the same `delta_bytes` S2 recorded (56,630 / 56,630 / 60). They are
  equivalent to S2's output; nothing to repair.
* Both re-runnable scripts now **protect** the artifacts they would clobber:
  `SIDE_EFFECT_FILES` (all 20, plus the two root debris files, which are deleted
  again when they did not exist before) are read into memory first and written
  back byte-for-byte, and `import_check.py --all` sha1s the tree before and
  after and fails loudly if anything else moved. Proven: a real
  `import_check.py --all` run afterwards reported the 20 restores and the 2
  removals and exited **0**, and the tree sha1 sweep showed no other change.
* Proof that it is fixed: a sha1 sweep of **11,852 files** before and after a
  full `smoke_round_sites.py` run shows **zero** content differences, and the
  same for `import_check.py`.

**Accounting of every modified tracked file** (213): 155 in S2's rewrite/handfix
set · 67 edited by S3 · `.gitignore` + `variation_kit.py` from S1 ·
`experiments/v3_0823/ACCOUNTING.md` (S2's §4.13 addendum). **0 unexplained.**
Re-checked at the end of the stage against the three stage ledgers: 213 modified
· 155 S2 · 67 S3 · 2 S1 · **0 unexplained**. `__pycache__` count 0,
`*.s3.bak` count 0.

## 6. Left as-is, deliberately

* **Doc placeholders** in docstrings and `--help` text — `dataset/<run>`,
  `dataset/<round>`, `dataset/<split>`, `dataset/<정본 A 라운드>` — in
  `run_data_render.py`, `sensor_augment.py`, `view_overlay.py`,
  `probe_driver.py`, `w1b2_segfill.py`, `verdict_panels.py`,
  `build_h_cue_table.py`. They document a convention, not a path. **S5** should
  update the convention once rather than 20 times.
* **`scripts/reorg/`** — this reorg's own tooling deliberately contains
  `dataset/<token>` literals and walks the dataset root directly. Not a residue.
* **Root constants** (`DS = os.path.join(REPO, "dataset")`, `D="$REPO/dataset"`)
  are left in place: the dataset **root did not move**, so they are still
  correct. Only the joins that append a *round name* were converted. Six of them
  are now unused; removing them would be churn beyond path resolution.
  `r4_pixdiff.py` is the exception — its root was a hardcoded absolute string
  and is now `DATASET_ROOT`, so `NEGOBS_DATASET_ROOT` works there too
  (survey B §2.3 rule 3).
* The three sites survey B lists as **safe by construction** (a full path
  arrives as an argument): `labeler.py:758`, `stamp_round.py:313`,
  `regression_check.py:1290`, plus `yolo/common.py:88 round_dir_of()` which
  derives the round dir upward from the frame path. Unchanged, re-checked.

## 7. What S4 / S5 / S6 must know

1. **The API is four names**: `round_dir(name)` (raises on miss),
   `round_dir_or_flat(name)`, `has_round(name)`, `rounds_matching(prefix)` —
   plus `DATASET_ROOT` and the env var `NEGOBS_DATASET_ROOT`. Shell:
   `negobs_round` / `negobs_round_or_flat` from
   `scripts/lib/negobs_paths.sh`. **New code must not spell a round path.**
2. **Re-runnable, and tree-neutral**: `scripts/reorg/smoke_round_sites.py`
   (32 checks), `scripts/reorg/import_check.py [--all]`,
   `scripts/tests/test_round_dir.py`. Re-run them after S4/S5 move anything.
3. **S6's residual scan for `*.py` / `*.sh`**: the only remaining
   `dataset/<non-group-token>` strings in code are (a) the doc placeholders in
   §6, (b) `scripts/reorg/*`, (c) the injected `# … dataset/<group>/<round>`
   comment on 66 files, (d) `[dry] … -> dataset/${run}/…` progress messages and
   the `refusing run stamp` message, (e) `local outdir` — which no longer exists,
   every one was converted. Nothing else.
4. **`experiments/dayrun_0820/code/run_phase1.sh` and the other files S2 fixed by
   text rewrite were not touched again** — they carry literal grouped paths and
   need no helper.
5. **An import sweep of this repo is NOT read-only** — about 20 tracked
   artifacts are regenerated merely by importing the module that produces them.
   If S6 wants to re-import everything, use `scripts/reorg/import_check.py
   --all`, which protects those artifacts, deletes the two files an unprotected
   sweep creates at the repo root (`hazgate.json`, `prims2.json`), sha1s the
   tree before and after, and exits non-zero if anything else moved. **Do not
   roll your own sweep.**
6. **The parked decisions from S2 are still parked** and S3 did not guess at
   them: the ambiguous `dataset/260820_boost_{h,e}` prose (note that
   `run_260820_boost.sh`'s *summary* line now resolves `260820_boost_${boost}`
   through the helper, which lands on the two orphan rounds in
   `_archive/v2_probes` — the same directories the flat path used to reach, so
   behaviour is unchanged), and the 192 stale `yolo_ds` duplicates.
7. **`.s3.bak` are gone** (66 files, 1,006,463 B, listed in
   `Docs/reorg_0827/S3_bak_deleted.tsv`) — deleted only after the full PASS
   above, and only after checking that **all 66 sources are git-tracked**, so
   `git diff` is the revert path. The two UNTRACKED helper files S3 also edited
   (`scripts/lib/negobs_paths.sh`, `scripts/tests/test_round_dir.py`) were
   changed **additively only** (one new shell function, three new tests); their
   pre-S3 copies are outside the repo at
   `…/scratchpad/s3/{negobs_paths.sh,variation_kit.py}.pre_s3`.
8. **Invariants at the end of S3**: symlinks **5,744** / broken **0** ·
   `dataset/` top level = 9 groups + `ROUNDS.json` + `README.md` ·
   `__pycache__` count **0** · `PREREG_V3.md`
   `05f41322e52b8e085b4d678c57dba4ee984deff3bfcea960123ae586e9fcf56a` and
   `PREREG_CUEOFF.md`
   `9c4733bb4baeabdf119a56e01b1e41439b96993ab1b73056892b262a1d2756b1`
   both **unchanged**.

## 8. Files this stage produced

```
Docs/reorg_0827/S3_report.md        this file
Docs/reorg_0827/S3_edits.tsv        66 rows: file · kind · sites · wiring · breakdown · test result
Docs/reorg_0827/S3_bak_deleted.tsv  66 rows: bak · bytes · source · source_git_tracked
scripts/reorg/convert_code_sites.py   the python conversion, rule table included (--dry-run/--apply)
scripts/reorg/convert_shell_sites.py  the shell conversion, rule table included (--dry-run/--apply)
scripts/reorg/smoke_round_sites.py    the R3 silent-empty smoke (32 checks)
scripts/reorg/import_check.py         the import sweep, with artifact protection
```
