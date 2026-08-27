# S2 dataset move — stage report (2026-08-27)

Branch `chore/reorg-0827`, repo `/home/vislab/Desktop/work_sy/Practice_NegObs`.
Nothing was committed. `Practice_NegObs_edge` was not touched (owner decision:
that worktree is to be discarded, so D2's edge clause is void). No GPU work, no
renders, no training. Every count comes from `os.walk` / `find`, never from
`grep -r` — this shell's `grep` is ugrep with `--ignore-files`.

**Status: PASS.** Steps 2–5 all pass; §6.4 items 1–10 are 10/10 in
`Docs/reorg_0827/S2_verification.md`.

| headline | measured |
|---|---:|
| rounds moved | **196** (16 `v2_corpus` first, as one unit) |
| files rewritten | **300** distinct (288 automatic + 22 hand, 10 in both) |
| substitutions | **85,521** (85,486 automatic + 35 hand) |
| byte delta | **+893,221 B** automatic (predicted exactly by the S1 dry-run) + 372 B hand |
| path strings verified to exist | **85,651** scanned · **56,281** structured manifest fields · 0 new breakage |
| symlinks retargeted | **5,687** (2,855 g7fix + 2,832 yolo_ds), all to relative targets |
| symlinks total / broken | **5,744 / 0** (invariant held) |
| `.pre0827.bak` deleted | **300** files, 112,012,914 B |

---

## 1. Pre-checks (all clear before anything moved)

* `tmux ls` → no server running. `nvidia-smi` compute-apps list → **empty**
  (only Xorg / gnome-shell / a browser hold graphics memory). No render or
  training job to race with.
* `find . -xtype l` → **0** broken.
* `find . -type l` → **5,744**. Expected = 5,748 (S1 snapshot) − 4 deleted with
  `venv_yolo`. Verified by diffing the snapshot against the live tree: exactly
  those 4 gone (`venv_yolo/bin/python{,3,3.10}`, `venv_yolo/lib64`), **0 new**.
* `--dry-run` reproduced S1 to the byte: 288 files, 77,621 abs + 1 xrepo + 21
  other-abs + 7,843 rel = **85,486**, **+893,221 B**; the report TSV is
  byte-identical to `Docs/reorg_0827/rewrite_dryrun.tsv`.
* `dataset/` held 197 entries (196 round dirs + `ROUNDS.json`); every
  `old_path` in `dataset_moves.tsv` existed, no `new_path` did, `st_dev` equal.
* Both PREREG sha256 matched the seal.

## 2. Physical moves

`scripts/reorg/do_dataset_move.py` — `os.rename` per round after asserting
`st_dev(old) == st_dev(new parent) == st_dev(dataset/)`. `os.rename`, not
`shutil.move`: atomic per round, and it preserves every inode, which is why the
2,855 links inside the g7fix shadow trees needed a *target* rewrite and not a
copy. The 16 `v2_corpus` rounds went first as one unit so the 8 g7fix shadows
and the 8 rounds they shadow could never be split across a half-finished move.

* 196/196 renamed, log `Docs/reorg_0827/dataset_move_log.tsv`;
  `dataset_moves.tsv` now carries a **`done`** column, 196 × `yes`.
* Every `new_path` exists, every `old_path` is gone.
* `dataset/` top level = **9 dirs** (`v2_corpus v2_probes cueoff v3_scene_build
  v3_library v3_test_ext v3_aux misc _archive`) + `ROUNDS.json` + `README.md`.
* **Nothing was copied**: the sum of `du -sb` over all 196 rounds is
  **105,648,176,652 B**, identical to the S1 snapshot, and **0** rounds changed
  size individually.
* `_archive/_delete_candidates` holds **19** rounds (S1's deliberate deviation:
  `260816_dataall` is a pilot and went to `_archive/pilots`).

## 3. Text rewrite

`rewrite_dataset_paths.py --apply` → 288 files, 85,486 substitutions,
+893,221 B, one `.pre0827.bak` per file. Then `--verify` and `--inverse-check`.

| check | result |
|---|---|
| residual old-form `dataset/<round>` | **0 in 0 files** |
| `--verify` existence (json/csv/txt/yaml under `experiments/` + `dataset/`) | 82,752 checked, 8 missing, **all 8 pre-existing**, **0 NEW** → VERIFY PASS |
| all-extension scan (adds log/md/py/sh) | 85,651 checked → 85,490 exist, 102 pattern heads, 8 baseline, **51 R9 rounds that never had a directory**, **0 new breakage** |
| structured fields (27 big manifests + 71 round manifests + bboxes + 38 sidecars) | **56,281 checked, 0 missing** |
| per-file byte delta == `n_subs × (1 + len(group))` | **288 / 288** |
| `--inverse-check` (inverse reproduces the backup byte-for-byte) | **288 / 288 PASS** |
| PREREG_V3 / PREREG_CUEOFF sha256 | unchanged |

## 4. Hand pass (the forms a name-keyed rewriter cannot see)

`scripts/reorg/handfix_dataset_paths.py` — a table of 32 explicit
(file, literal, group) rules, **22 files, 35 substitutions**, report
`Docs/reorg_0827/handfix_apply.tsv`. Every rule carries the glob whose
expansion was checked against `ROUNDS.json`; `--check-groups` re-derives it and
refuses to run if any rule spans two groups. Examples:
`dataset/260819_main_{on,off}` → `v2_corpus`, `dataset/2607xx_*` →
`_archive/scene_dev_2607`, `dataset/260823_cueoff{,2,3,_s20fix}_{A,B1,B2,P,C}`
→ `cueoff`, `dataset/260824_v3w2_h67{base,h,h2}_{A,B,C,D}` → `v3_library`,
`dataset/260820_boost_<band>_<arm>_g7fix{,M}` → `v2_corpus`.

To keep the proof intact, `build_inverse_pattern()` was generalised from
`dataset/<group>/<round>` → `dataset/<round>` to `dataset/<group>/` →
`dataset/` — the true inverse of a transform that only inserts `<group>/`.
**Measured first: 0 of the 288 pre-move backups contained `dataset/<group>/`**,
so the generic rule cannot strip anything pre-existing. Both checks still pass
afterwards (288/288 automatic, 22/22 hand). Old script kept at
`Docs/reorg_0827/rewrite_dataset_paths.py.s1.bak`.

**Deliberately left as-is** (93 forms / 354 occurrences, classified in
`Docs/reorg_0827/handfix_skipped.tsv`): 158 shell/py **variables** (S3's job —
a string edit cannot fix `dataset/${run}`), 62 **doc placeholders**
(`dataset/<run>`, `dataset/<round>` — S5 updates the convention once), 54
**rounds that have no directory** (§6.3 R9), 33 non-path tokens, and these
judgement calls:

* `dataset/260820_boost_{h,e}` — 8 in `logs/boost_render.log`, 1 in
  `run_260820_boost.sh:332`. **Ambiguous**: line 21 of the same script says the
  output trees are `dataset/260820_boost_{h,e}_{on,off}/` (→ `v2_corpus`, and
  *that* form was rewritten), but two bare orphan rounds `260820_boost_h`/`_e`
  also exist (→ `_archive/v2_probes`). One brace form, two possible groups, so
  it was not guessed. **Needs an owner/S5 decision.**
* `experiments/v3_0823/ACCOUNTING.md:82` quotes the sealed `PREREG_CUEOFF.md`
  verbatim; the quote must keep matching the sealed bytes, so it keeps the old
  spelling and the new location is recorded in the path-map note instead.

## 5. Symlinks

**(a) g7fix shadow trees — 2,855, retargeted.** `readlink` → map the old
absolute `dataset/<round>` through `ROUNDS.json` → assert the new target exists
→ `os.path.relpath` from the link's own directory → write a temp link and
`os.replace` it (atomic; the link count never dips). Example:
`dataset/v2_corpus/260820_boost_e_on_g7fix/train/scene09/X.depth.npy` →
`../../../260820_boost_e_on/train/scene09/X.depth.npy`.

**(b) `experiments/dayrun_0820/yolo_ds` — 2,832, retargeted in place, NOT
regenerated.** Route and reason, recorded as asked:

1. `annotations/amodal/bboxes.json` after the rewrite: **0** old-form paths,
   2,832 `rgb` paths, **all 2,832 resolve**. (The precondition for R8 was met.)
2. `make_yolo_dataset.py` **does** run on system `python3` 3.10.12 without the
   deleted venv — it is stdlib plus `numpy` 1.21.5 (via `code/yolo/common.py`,
   which pulls `gridspec`/`labeler`); no ultralytics, no torch. A full
   regeneration into a scratch directory succeeded.
3. **But regeneration is not byte-stable, and the reason is a pre-existing
   defect, not the move.** The live `yolo_ds` is a *two-build layer cake*: it
   holds 2,832 images (train 1,632 / val 384 / test 816) while its own
   `build_report.json` records 2,640 (1,536 / 288 / 816). 192 files sit in both
   `train/` and `val/` — leftovers from an earlier build against
   `split_v2.json`, which put scene08/scene20 in train and scene10/scene17 in
   val; the recorded build used `split_v2_full.json`, which swaps them. The
   builder never cleans its output, so a rebuild **in place** would leave those
   192 links pointing at pre-move paths (→ 192 broken links), and a rebuild in a
   clean directory would drop 192 files — a deletion that is not on the approved
   list and would move the symlink invariant from 5,744 to 5,552.
4. So the links were **retargeted**, preserving everything, and the
   regeneration was kept as *evidence*: the fresh build's 2,640 label `.txt`
   files are **byte-identical** to the live ones (0 differing, 0 only-in-fresh),
   and all 2,640 fresh image links resolve to **exactly the same realpath** as
   the retargeted live links. `data.yaml` needed no edit — its only path is
   `path: …/experiments/dayrun_0820/yolo_ds`, which did not move, and it holds
   no `dataset/<round>` string (it is correctly absent from the rewrite report).
5. **Open item for the owner/S6:** the 192 stale duplicates are still there.
   They are harmless (they resolve) but they mean `yolo_ds` disagrees with its
   own build report. Cleaning them = re-running
   `make_yolo_dataset.py --split split_v2_full.json` into a fresh directory,
   which is a 192-file deletion and therefore needs approval.

After (a)+(b): `find . -xtype l` → **0**; `find . -type l` → **5,744**; all
5,687 retargets logged in `Docs/reorg_0827/symlink_retarget.tsv` with
old target, new target and resolved path, **5,687/5,687 `status ok`**; the 57
relative links (scene kits, `look_check` roots) were untouched and none of them
points into `dataset/`.

## 6. Bookkeeping written

* `experiments/v3_0823/ACCOUNTING.md` **§4.13** (Korean) — which sealed ledgers
  changed, old→new sha256, and the one-sentence proof. Only **4** sealed
  ledgers actually changed (`dataset_manifest_v3.json`,
  `dataset_manifest_v3_seg3.json`, `dataset_manifest_v3_textext.json`,
  `dataset_manifest_v3_textext_bd.json`); `split_v3*.json`,
  `corpus_v3_{quarantine,census}{,_seg3}.json` and `cue_extent_audit.json` hold
  **no** `dataset/` path and are byte-unchanged — their hashes are recorded as
  unchanged rather than invented. The two `dataset_manifest_v2corr*.json`
  (rewritten, not sealed) are listed too.
* `experiments/weekend_0823/cue_audit/PREREG_CUEOFF_PATHMAP_0827.md` (Korean,
  16 lines) — the 4 stale `dataset/` spellings inside the sealed PREREG and
  where they live now.
* `dataset/README.md` (Korean, 58 lines) — the 9 groups with size and round
  count, the training canon and which groups it draws from, three ways to find a
  round by name, the stamp-vs-render-date warning pointing at `ROUND_LEDGER.md`,
  what `_archive/` and `_archive/_delete_candidates/` (0.7 GiB, safe to wipe)
  mean, and that new renders still land flat at `dataset/<stamp>`.

## 7. `.pre0827.bak` deletion

Deleted **after** 10/10 verification: **300** files, **112,012,914 B**, listed
in `Docs/reorg_0827/bak_deleted.tsv` (path, size, source-file-exists). 0 remain.

**Kept on purpose**: `Docs/reorg_0827/{gitignore,variation_kit.py}.bak` from S1
— S1 offered them for deletion, but an agent hand-off is not the owner's
approval and the ground rules forbid deleting anything off the approved list, so
they stay (60 KB). `Docs/reorg_0827/rewrite_dataset_paths.py.s1.bak` is kept
because `scripts/reorg/` is untracked and it is the only record of the
pre-generalisation inverse. The two stale 08-24 backups
(`experiments/v3_0823/logs/cue_extent_{frames,attrib}.json.bak`) are untouched
and still carry pre-move paths by design — **S6's residual scan must exclude
`*.bak`** or it will report 4,872 false positives.

## 8. What S3 and later stages must know

1. **Symlink invariant is still 5,744, broken 0.** Both g7fix and `yolo_ds`
   links are now **relative**; a future `make_yolo_dataset.py` run would write
   absolute ones again, which is harmless but worth knowing.
2. **`dataset/` top level is 9 dirs + `ROUNDS.json` + `README.md`.** New renders
   still land flat at `dataset/<stamp>`; `round_dir()` finds both layouts.
3. **Re-measured code sites for S3** (`.py`/`.sh`, `os.walk`): **49**
   `os.path.join(…, "dataset", <expr>)` in 32 files and **153**
   `dataset/$var` / `dataset/{expr}` in 43 files — 65 distinct files, of which 2
   are this reorg's own scripts (21 occurrences). Survey B's 225-site list must
   be re-derived from this, not reused: 21 shell/doc sites were already fixed by
   the text rewrite, and 35 more by the hand pass.
4. **The R3 silent-empty smoke is still owed** and belongs to S3. The four
   gates (`hash_gate.py`, `gates_cueoff.py`, `w1b_verify.py`,
   `w1c_hashgate.py`) build paths in code, so they would report 0 frames today.
   That is expected, not damage — smoke them after the `round_dir()` conversion.
5. **`--inverse-check` can no longer be re-run** (its backups are gone). The
   permanent proofs are ACCOUNTING §4.13's sha256 pairs and `git diff` — all six
   rewritten manifests are git-tracked, so the pre-move bytes stay in the index
   until the orchestrator commits. 158 tracked files are modified
   (52,138 insertions / 51,987 deletions, almost all path prefixes).
6. **Two decisions are parked**: the ambiguous `dataset/260820_boost_{h,e}`
   (§4) and the 192 stale `yolo_ds` duplicates (§5).
7. **Re-runnable checkers left in `scripts/reorg/`**: `check_manifest_paths.py`
   (the 56,281-field existence check), `rewrite_dataset_paths.py --verify`
   (residual + existence), `handfix_dataset_paths.py --dry-run`
   (re-derives the group-boundary check without writing), `retarget_symlinks.py`
   (dry-run by default). 6 `__pycache__` dirs created by these runs were removed
   (approved deletion class); the tree ends with 0.
8. `Docs/reorg_0827/verify_missing_r9.txt` lists the 51 citations of rounds that
   have no directory, so S6 can tell them from damage.
   `Docs/reorg_0827/handfix_skipped.tsv` does the same for the 93 unrewritten
   `dataset/<token>` forms. Note that
   `scripts/reorg/handfix_dataset_paths.py` deliberately *contains* old-form
   examples in its rule table and docstring — that is its record, not a residue.

## 9. Final state

```
dataset/          9 group dirs + ROUNDS.json + README.md   196 rounds   98.39 GiB
symlinks          5,744 total · 0 broken · 5,687 retargeted to relative
text              300 files rewritten · 85,521 substitutions · residual 0
paths verified    56,281 structured fields + 85,651 strings · 0 new breakage
backups           300 .pre0827.bak deleted (112 MB) after 10/10 PASS
PREREG_V3.md      05f41322e52b8e085b4d678c57dba4ee984deff3bfcea960123ae586e9fcf56a  (sealed, unchanged)
PREREG_CUEOFF.md  9c4733bb4baeabdf119a56e01b1e41439b96993ab1b73056892b262a1d2756b1  (sealed, unchanged)
```
