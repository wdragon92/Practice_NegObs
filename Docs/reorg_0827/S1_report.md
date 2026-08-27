# S1 prep — stage report (2026-08-27)

Branch `chore/reorg-0827`, repo `/home/vislab/Desktop/work_sy/Practice_NegObs`.
Nothing was moved, nothing was committed, `Practice_NegObs_edge` was not touched.
Every count below was produced by `os.walk`/`find`, never by `grep -r` (this shell's
`grep` is ugrep with `--ignore-files` and silently skips `dataset/`, `look_check/*`,
`*.log`, `yolo_ds/`, `annotations/amodal/`).

**Status: PASS** — all six S1 gates met.

---

## 1. Snapshots (`Docs/reorg_0827/snapshot_before/`)

| file | measured |
|---|---|
| `dataset_du_sb.tsv` | 196 rounds, **105,648,176,652 B = 98.39 GiB** — exact match to survey A |
| `dataset_toplevel_ls.txt` | 196 entries: 196 dirs, 0 files, 0 symlinks |
| `lookcheck_depth2_dirs.txt` | 740 dirs at `find look_check -maxdepth 2 -type d` |
| `symlinks_all.tsv` | **5,748** symlinks with targets (`%p\t%l`) |
| `symlinks_broken.txt` | **0** broken (`find . -xtype l`) — the baseline invariant |
| `git_status_porcelain.txt` | 7 entries (all `??`) |
| `git_ls_files.txt` / `_count.txt` | **5,986** tracked files |
| `prereg_sha256.txt` | `PREREG_V3.md` `05f41322…f56a` ✔ · `PREREG_CUEOFF.md` `9c4733bb…56b1` ✔ |

Both sealed hashes were re-verified at the end of the stage and are **unchanged**.

---

## 2. Deletions (`Docs/reorg_0827/deletions.tsv`, 36 rows, all DELETED, 0 skipped)

| target | bytes | files |
|---|---:|---:|
| `experiments/dayrun_0820/venv_yolo/` | 5,567,247,435 | 29,499 |
| `look_check/_experiments/gates/lighting_spikes/` | 5,647,638,745 | 1,649 |
| `experiments/v3_0823/reselect/rgb_s42_repro/{ep9,ep10,last}.pt` | 293,847,790 | 3 |
| 20 `__pycache__/` outside `.git` (incl. the root one) | 7,211,088 | 154 |
| 11 empty `look_check/` dirs | 0 | 0 |
| **total freed** | **11,515,945,058 B = 10.73 GiB** | |

* The 1,026 further `__pycache__` dirs were inside `venv_yolo` and went with it.
* All 11 look_check dirs (`probeH1-3`, `sceneH1/2/3/6/7`, `sceneL1`, `sceneN9`, `sceneN11`)
  were verified to hold **0 entries** immediately before `rmdir`. None was skipped.
* `reselect/rgb_s42_repro/` kept `best.pt`, `metrics.csv`, `config.json`, `REPRO_CHECK.json`,
  `TRAIN_DONE`.
* Nothing deleted was git-tracked (checked before deleting).

### venv_yolo rebuild recipe (recorded before deletion)
* `pyvenv.cfg`: `home = /usr/bin`, `include-system-site-packages = false`, **`version = 3.10.12`**
* `experiments/dayrun_0820/code/yolo/requirements_yolo.txt` is **tracked** (5,316 B), pins
  `torch==2.13.0`, `torchvision==0.28.0`, `ultralytics==8.4.123`, `ultralytics-thop==2.1.6`,
  `numpy==2.2.6`, `opencv-python==5.0.0.93`.
* Rebuild: `python3.10 -m venv experiments/dayrun_0820/venv_yolo && \
  experiments/dayrun_0820/venv_yolo/bin/pip install -r experiments/dayrun_0820/code/yolo/requirements_yolo.txt`,
  then re-fetch `weights/yolov8n.pt`.

### Symlink accounting after the deletions
`5,748 − 4 = 5,744`, broken still **0**. The 4 were all inside `venv_yolo`
(`lib64`, `bin/python`, `bin/python3` → `/usr/bin/python3`, `bin/python3.10`).
**The post-move invariant for S2 is now 5,744, not 5,748.**

---

## 3. `.gitignore`

Line 15 `**/runs/**/*.pt` → two lines `*.pt` and `*.pth`. The `# runs/: keep text artifacts
public (D35/R3); exclude binaries below` comment and every other rule were kept; 3,985 → 3,980 B.
Backup: `Docs/reorg_0827/gitignore.bak`.

* Before: `git ls-files | grep -E '\.(pt|pth)$'` → **empty** (no tracked checkpoint to orphan).
* After: same, still empty; `git status --porcelain` no longer lists
  `experiments/v3_0823/reselect/rgb_s42_repro/best.pt` (was `??`, 374 MB one `git add -A` from history).
* `git check-ignore -v` confirms `best.pt` is now caught by `.gitignore:15 *.pt`, and
  `experiments/dayrun_0820/yolo26n.pt` is still caught by its own explicit rule at line 95.

---

## 4. Code helper

**Decision: the helper lives in `variation_kit.py` itself — no new module.**
`variation_kit.py` is Isaac-free by design (its module docstring: *"nothing here imports `pxr`,
`omni`, `carb` or `cv2` at module scope"*), and `python3 -c "import variation_kit"` on a bare
interpreter was verified before and after the edit. A separate `negobs_paths.py` would also have
had to be symlinked into the 4 scene dirs that currently symlink `variation_kit.py`
(`scenes/{batch1,main,probe}`, `experiments/weekend_0823/cue_audit/scenes_cueoff`), adding a
failure mode for no gain.

Added to `variation_kit.py` (backup `Docs/reorg_0827/variation_kit.py.bak`, 1155 → 1271 lines):

* `DATASET_ROOT = os.environ.get("NEGOBS_DATASET_ROOT") or os.path.join(REPO, "dataset")`
  — `REPO` is the module's existing `os.path.dirname(os.path.abspath(__file__))`, reused unchanged.
* `round_dir(name, dataset_root=None)` — search order (a) flat `<root>/<name>`,
  (b) `<root>/ROUNDS.json`, (c) `<root>/*/<name>` and `<root>/_archive/*/<name>`.
  Candidates are collapsed by `realpath`; **exactly one** existing hit is required.
  0 hits → `FileNotFoundError` naming the round and all roots searched.
  \>1 hits → `RuntimeError` listing them. It never returns a non-existent path.
* `rounds_index()`, `round_candidates()`, `_subdirs()` — supporting, mtime-cached index read.
* `data_root(run_stamp)` — **signature unchanged**. An existing stamp returns wherever it lives;
  a new stamp still returns the flat `<DATASET_ROOT>/<stamp>`, which is what
  `scripts/run_data_render.py:112` `os.makedirs()`. An ambiguous stamp raises rather than guessing.
  `scripts/run_data_render.py --help` still exits 0; `check_data_run.py` still executes.

`scripts/lib/negobs_paths.sh` — `negobs_round <name>` shells `python3 -c` into
`variation_kit.round_dir`, prints the absolute dir on stdout, prints the error on stderr and
returns **1** on a miss (`return`, not `exit`, so sourcing a script cannot kill the caller's
shell; run directly, the same code path `exit`s 1). Works both sourced and executed — both tested.

`scripts/tests/test_round_dir.py` — plain asserts, temp-dir fixtures, **11/11 PASS on the current
flat tree**: flat hit · grouped-via-`ROUNDS.json` · grouped-via-glob · `_archive/<g>/<round>`
second level · stale index falls through to the real dir · miss raises · ambiguity raises ·
symlink alias counts as one hit · `NEGOBS_DATASET_ROOT` override · new stamp stays flat ·
live tree (`round_dir('260819_main_on')`).

`python3 variation_kit.py` self-check: **PASS**. `import variation_kit, scene_common`: ok.

---

## 5. ROUNDS map

`scripts/reorg/build_rounds_map.py` (from `dataset_reorg_plan.tsv` + the `du -sb` snapshot) wrote
`dataset/ROUNDS.json` (196 entries) and `Docs/reorg_0827/dataset_moves.tsv` (196 rows:
round, old_path, new_path, action, size_bytes).

Validation, all passing, or the script exits 1: 196 rows · every `old_path` exists on disk ·
no duplicate `new_path` · every parent inside the allowed set · **9 top-level entries** ·
plan round set == `dataset/` dir set · every round has a measured size.

| new parent | rounds | bytes | GiB |
|---|---:|---:|---:|
| `v2_corpus` | 16 | 25,009,191,560 | 23.29 |
| `v3_library` | 29 | 29,792,617,937 | 27.75 |
| `v3_test_ext` | 16 | 10,064,412,249 | 9.37 |
| `v3_aux` | 10 | 9,423,925,478 | 8.78 |
| `cueoff` | 15 | 6,003,405,655 | 5.59 |
| `v3_scene_build` | 22 | 3,727,669,199 | 3.47 |
| `v2_probes` | 3 | 1,730,256,886 | 1.61 |
| `misc` | 1 | 6,273,313 | 0.01 |
| `_archive/v3_scene_build` | 41 | 10,219,824,743 | 9.52 |
| `_archive/v2_probes` | 4 | 3,963,251,632 | 3.69 |
| `_archive/v3_library` | 4 | 2,645,591,589 | 2.46 |
| `_archive/pilots` | 3 | 1,094,015,608 | 1.02 |
| `_archive/scene_dev_2607` | 11 | 885,799,345 | 0.82 |
| `_archive/_delete_candidates` | 19 | 778,232,793 | 0.72 |
| `_archive/v3_aux` | 2 | 303,708,665 | 0.28 |
| **total** | **196** | **105,648,176,652** | **98.39** |

Top level after the move: `v2_corpus, v2_probes, cueoff, v3_scene_build, v3_library, v3_test_ext,
v3_aux, misc, _archive` = **9**, exactly D1.
By action: keep 112 · archive 64 · delete_candidate 20 (survey A's split, unchanged).

**One deliberate deviation to note:** `_archive/_delete_candidates` holds **19** rounds, not 20.
`260816_dataall` is both a delete_candidate (empty dir) and one of the 3 pilots, and the master
plan's explicit pilot rule wins, so it went to `_archive/pilots` with
`260815_datapilot{,_aug}`. The action column still says `delete_candidate` in
`dataset_moves.tsv`, so nothing is lost.

`ROUNDS.json` now sits in the still-flat tree; all 196 rounds were re-resolved through
`round_dir()` **196/196** with the (currently stale) index present, and the test suite still
passes 11/11 — the index cannot mislead the helper because a candidate must exist to be returned.

---

## 6. Rewriter dry-run

`scripts/reorg/rewrite_dataset_paths.py --dry-run` → `Docs/reorg_0827/rewrite_dryrun.tsv`
(288 rows: file, tracked, n_abs, n_rel, delta_bytes). 7 s over 13,947 text files.

| class | count |
|---|---:|
| absolute, repo prefix `/home/…/Practice_NegObs/dataset/<round>` | **77,621** |
| literal-relative `dataset/<round>` | **7,843** |
| variable-rooted absolute (`$REPO/dataset/…`, `$R/…`, `$PWD/../../../../dataset/…`) | 21 |
| repo-relative cross-repo prose (`Practice_NegObs/dataset/…`) | 1 |
| **total substitutions** | **85,486** |
| **byte delta** | **+893,221** |
| files hit | 288 |

### Reconciliation with reference_inventory §1 (77,624 absolute + 7,804 literal-relative)
Reconciled **per file** against `refs_by_file.tsv` (247 main-repo rows with breakable refs).
Every difference is accounted for; there is no unexplained residue.

* **absolute 77,621 = 77,624 − 3.** The 3 are citations of the dataset **root with no round after
  it**: `experiments/mainrun_0819/code/labeling/README_LABELING.md:7` (`D=/home/…/dataset`),
  `experiments/weekend_0823/redteam/R3_repro.md:162` (prose `/home/…/dataset/...`),
  `experiments/weekend_0823/redteam/r4_pixdiff.py:19` (`DS = "/home/…/dataset"`). The root does
  not move, so the rewriter correctly leaves them; `r4_pixdiff.py` is an **S3 code site**
  (survey B's single ABS-HARDCODED entry), not a text-rewrite site.
* **literal-relative 7,843 = 7,804 + 38 + 1.**
  +38 are in-`dataset/` sidecars survey B counted in its §1.3 table (523 occurrences) but did not
  put in `refs_by_file.tsv`: 29 `idseg_backfill.json` + 9 `heightmap_fused_meta.json`. The 71
  `manifest.json` (485 occurrences) *were* in the TSV and are already inside the 7,804.
  +1 is `scripts/rounds/run_260820_boost.sh:180`, which names both orphan rounds in one echo
  (`dataset/260820_boost_h and dataset/260820_boost_e.`); survey B's scan counted 3 there, the
  right-boundary matcher finds 4. Mine is the correct count.
* **+22 not in survey B's §1.2 at all** (21 variable-rooted + 1 cross-repo prose). Survey B filed
  these under §2 *code sites* rather than §1.2 *path styles*. They carry a literal round name after
  `dataset/`, so the string rewrite fixes them correctly and for free — see §7 note for S3.
* **The junk deletion cost 0 references.** No row of `refs_by_file.tsv` lies under `venv_yolo/`
  or `lighting_spikes/`; the 5 remaining `look_check/logs/*.log` files still carry their 8 abs +
  4 rel. `*.pt` and `__pycache__` are binary/derived.
* PREREG exclusions cost nothing numerically: `PREREG_V3.md` has **0** `dataset/` occurrences and
  `PREREG_CUEOFF.md`'s 4 are all non-round glob forms (`260823_cueoff*`,
  `260820_boost_e2_*/*/scene*/variation.json`, `260823_cueoff_s20fix_*` ×2) that a name-keyed
  matcher never touches. Both files keep their sealed bytes; the pathmap note is S2's job.

### Correctness evidence for the transform
A sandbox at `…/scratchpad/sandbox/` exercised the whole cycle end to end:
prefix collision (`260820_boost_e` → `_archive/v2_probes` while `260820_boost_e_on` → `v2_corpus`
in the same file), both path styles, a bare `"round":` field left untouched, `mydataset/…` left
untouched (left boundary), a brace expansion left untouched, then
`--apply` → `--verify` residual **0** → `--inverse-check` **PASS** (byte-identical to the backup)
→ a second `--dry-run` finding **0** (single-pass idempotence).

Two defects were found and fixed there rather than in S2:
1. the backup suffix is now **`.pre0827.bak`**, because two unrelated `*.bak` files from 08-24
   already sit in `experiments/v3_0823/logs/`, and `--inverse-check` would have compared against
   the wrong baseline. `--inverse-check` is now driven by the `--apply` report, never by globbing.
2. the inverse transform used `split("/", 1)`, which corrupts two-segment groups
   (`_archive/<group>`); it is now `rsplit("/", 1)`.

### Pre-move baseline for `--verify`
`--verify` on the untouched tree: **82,752** dataset path strings checked in json/csv/txt/yaml
under `experiments/` and `dataset/`, **8 missing — all pre-existing**, recorded in
`Docs/reorg_0827/verify_baseline_missing.txt` so S2 can tell a pre-existing dangling citation from
damage. They are 4 brace-expansion fragments in a documentation field of
`dataset_manifest_v2corr{,_roundown}.json` (`"g7_shadow_render_trees": ["dataset/260820_boost_e_{on,off}_g7fixM", …]`
— hand-rewrite cases, survey B §6.3 R2) and 4 scene names never rendered
(`scene{N3,C2}` in `experiments/weekend_0823/rt_response/f7b_noisefloor.json`'s prose provenance).
The residual half of `--verify` correctly reports **85,486 in 288 files** today: nothing has been
rewritten yet, so a pre-move `VERIFY FAIL` is the expected negative control.

### Not fixable by the name-keyed rewriter (for S2's hand pass)
`--dry-run` also prints every `dataset/<token>` whose first segment is not a known round:
**95 distinct forms, 337 occurrences**. The largest are `dataset/260826_v3a_segfill_smoke` (38, in
`experiments/v3_0823/logs/segfill_render.log` — a round name that is **not** among the 196 and has
no directory on disk), shell variables (`dataset/${run}` 20, `dataset/$r` 18, `dataset/${STAMP}` 12,
`dataset/$run` 9, `dataset/${pre}` 9, `dataset/${RUN}` 7, `dataset/$1` 6 …), doc placeholders
(`dataset/<run>` 12, `dataset/<round>` 7, `dataset/<정본…>` 6), brace expansions
(`dataset/260820_boost_{h,e}` 10, `dataset/260819_main_{on,off}` 4,
`dataset/260820_boost_<band>_<arm>_g7fix{,M}` 2+2), and the two rounds that never rendered
(`dataset/260819_dataall_on{,_aug}` 4, survey B R9). Variables are S3's job; brace expansions and
placeholders are S2's hand list — each brace expansion must be checked for whether its expansion
crosses a group boundary.

### One file outside the allow-list
A full scan of non-allow-listed, non-binary files found exactly one holding old-form paths:
`experiments/v3_0823/logs/cue_extent_frames.json.bak` (4,872 occurrences, a stale backup from
2026-08-24, with `cue_extent_attrib.json.bak`). Both are pre-existing, are **not** on the approved
deletion list, and are left untouched — they will keep pre-move paths by design. A residual scan
that includes `*.bak` will therefore report them; S6 should exclude the extension or the owner
should decide their fate separately.

---

## 7. What S2 and S3 must know

1. **Symlink invariant is 5,744**, not 5,748 (4 venv symlinks went with `venv_yolo`). Broken must stay **0**.
2. `dataset/ROUNDS.json` exists and is authoritative; it is gitignored (`dataset/` is), so
   `Docs/reorg_0827/dataset_moves.tsv` is its tracked twin. Rebuild either with
   `scripts/reorg/build_rounds_map.py <plan.tsv> <du_sb.tsv>`.
3. `_archive/_delete_candidates` gets **19** rounds; `260816_dataall` is in `_archive/pilots`.
4. The rewriter **excludes** `Docs/reorg_0827/` (this reorg's own record of the OLD paths) and the
   two PREREG files, and skips symlinks and non-allow-listed extensions. Run order per survey B
   §6.1: move → `--apply` → symlink retarget → `bboxes.json` check → `yolo_ds` regen → `--verify`
   → `--inverse-check`. Expected: 85,486 substitutions, +893,221 bytes, 288 files.
5. Backups are written as `<file>.pre0827.bak` and the apply report `rewrite_apply.tsv` is the
   list `--inverse-check` reads. Do not delete the backups before `--verify` **and**
   `--inverse-check` both pass.
6. `--verify` PASSes only when residual == 0 **and** no NEW missing path appears beyond the 6
   baseline entries in `verify_baseline_missing.txt`.
7. **21 shell/doc sites are already fixed by the text rewrite** (`$REPO/dataset/<round>` and
   friends in `run_phase1.sh`, `run_ctrl_eval.sh`, `run_ctrl_eval_depth.sh`, `w0_label.sh`,
   `eval_cueoff.sh`, `G7_RELABEL.md`, `SCENE_H67_BUILD.md`, `HARNESS_NOTES.md`). S3's 225-site
   list shrinks accordingly — re-measure before converting.
8. Two cosmetic rewrites S2 should eyeball but not worry about:
   `run_260820_boost.sh:26` `dataset/260819_main_on|off/` → `dataset/v2_corpus/260819_main_on|off/`
   and `:180`'s guard message, which will name the archive paths of the two orphan stamps.
9. `.gitignore` needs no round-path fix: its only `dataset` lines are the bare `dataset/` rule and
   a `dataset/<run>/manifest.json` placeholder in a comment.
10. S1's two `.bak` copies (`gitignore.bak`, `variation_kit.py.bak`) are **kept**, even though the
    stage passed: both files are git-tracked, so `git diff` is the real revert path and these are
    belt-and-braces. S2 may delete them once its own verification passes.

## 8. Final state

```
broken symlinks   0          symlinks 5,744        dataset/ 196 rounds + ROUNDS.json
PREREG_V3.md      05f41322e52b8e085b4d678c57dba4ee984deff3bfcea960123ae586e9fcf56a  (sealed, unchanged)
PREREG_CUEOFF.md  9c4733bb4baeabdf119a56e01b1e41439b96993ab1b73056892b262a1d2756b1  (sealed, unchanged)
test_round_dir.py 11/11 PASS       variation_kit.py self-check PASS
git status        M .gitignore · M variation_kit.py · ?? Docs/reorg_0827/ · ?? scripts/{lib,reorg,tests}/
                  (+ the 3 pre-existing untracked items; reselect .pt files no longer listed)
```
