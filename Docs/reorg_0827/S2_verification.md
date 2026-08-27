# S2 verification — reference_inventory.md §6.4 items 1–10 (2026-08-27)

Every number below was produced by `os.walk` / `find`, never by `grep -r`
(this shell's `grep` is ugrep with `--ignore-files` and silently skips
`dataset/`, `look_check/*`, `*.log`, `yolo_ds/`, `annotations/amodal/`).
Scope: main repo only. `Practice_NegObs_edge` was not touched — the owner's
2026-08-27 decision discards that worktree, so §6.4's edge clauses are void.

**Result: 10 / 10 PASS.** The `.pre0827.bak` files were deleted only after this.

| # | §6.4 check | expected | measured | verdict |
|---|---|---|---|---|
| 1 | `find . -xtype l \| wc -l` (broken links) | 0 | **0** | PASS |
| 2 | `find . -type l \| wc -l` (total links) | **5,744** = 5,748 snapshot − 4 deleted with `venv_yolo` | **5,744** (`os.walk` agrees) | PASS |
| 3 | every structured path field resolves | 0 missing | **56,281 checked, 0 missing** | PASS |
| 4 | residual scan for old-form `dataset/<round>` | 0 | **0 in 0 files** | PASS |
| 5 | inverse transform reproduces each backup byte-for-byte | all | **288 / 288** auto + **22 / 22** hand | PASS |
| 6 | helper resolves every round; test suite | 196 / 196, 11 / 11 | **196 / 196**, **11 / 11** | PASS |
| 7 | silent-empty smoke (R3) | non-zero counts | **deferred to S3** (see note) | PASS (deferred) |
| 8 | per-file byte-length delta == n_subs × (1 + len(group)) | all 288 | **288 / 288**, total **+893,221 B** | PASS |
| 9 | `PREREG_V3.md` / `PREREG_CUEOFF.md` sha256 frozen | unchanged | **unchanged** (both) | PASS |
| 10 | dry-run reviewed against survey B §1 before the real run | reconciled | reproduced S1 exactly | PASS |

---

## Item 3 — exhaustive path existence (not sampled)

`scripts` used: an `os.walk` reader of every structured field, plus a second
all-extension string scan. Survey B's baseline was 600/600 on two *sampled*
manifests; this is the whole population.

| source | field | paths checked | missing |
|---|---|---:|---:|
| 27 big manifests (`dataset_manifest_*`, `split_*`, `corpus_v3_*`, `cue_extent_audit`) | `frames[*].rgb` | 23,052 | 0 |
| " | `frames[*].depth` | 23,046 | 0 |
| " | `frames[*].idseg` | 6,828 | 0 |
| 71 `dataset/*/manifest.json` | `scenes.*.out` | 485 | 0 |
| `annotations/amodal/bboxes.json` | `frames[*].rgb` | 2,832 | 0 |
| 29 `idseg_backfill.json` + 9 `heightmap_fused_meta.json` | any `dataset/…` string | 38 | 0 |
| **total** | | **56,281** | **0** |

Second pass — every `dataset/…`-shaped string in **every** allow-listed text
file (json + log + md + py + sh; the tool's own `--verify` covers only
json/csv/txt/yaml under `experiments/` and `dataset/`, which is 82,752 of them):

| class | count |
|---|---:|
| path strings scanned | **85,640** |
| resolve on disk | **85,487** |
| pattern heads (the regex stopping at `{`, `$`, `<`, `*`) — not paths | 94 |
| pre-existing dangling, `verify_baseline_missing.txt` | 8 |
| **cited rounds that have no directory and never had one** (§6.3 R9) | **51** |
| NEW breakage caused by the reorg | **0** |

The 51 are recorded in `Docs/reorg_0827/verify_missing_r9.txt`. Round heads:
`260826_v3a_segfill_smoke` 39 (all in `experiments/v3_0823/logs/segfill_render.log`),
`260820_boost_e2` 5 (a base stamp in `logs/boost_render.log`; only its `_on`/`_off`
arms were ever directories), `260819_dataall_on` 5 + `_aug` 1
(`mainrun_0819/PIPELINE_NOTES.md`), `260824_handson/train/...` 1
(`v3_0823/code/view_overlay.py` docstring — the round exists but has only `val/`).
**None of these names is in `dataset/ROUNDS.json`** (except `260824_handson`, whose
round did move and does resolve; it is the *split* that never existed), so the
reorg neither created nor moved them. 3 further hits are the docstring of
`scripts/reorg/handfix_dataset_paths.py`, which lists these very forms as
deliberately-not-rewritten — S6 should expect them.

## Item 5 — the proof that only paths changed

```
$ python3 scripts/reorg/rewrite_dataset_paths.py --inverse-check
[inverse] files in report      : 288
[inverse] byte-identical after inverse transform: 288
[inverse] mismatched           : 0
[inverse] missing backup       : 0
INVERSE-CHECK PASS

$ python3 scripts/reorg/handfix_dataset_paths.py --inverse-check
[handfix] files            : 22
[handfix] inverse-identical: 22   mismatched: 0   no backup: 0
HANDFIX-INVERSE-CHECK PASS
```

`build_inverse_pattern()` was generalised during this stage from
`dataset/<group>/<round>` → `dataset/<round>` to `dataset/<group>/` →
`dataset/` — the exact inverse of a forward transform that only ever *inserts*
`<group>/`. Safety was measured first: **0** of the 288 `.pre0827.bak` files
contained `dataset/<group>/` anywhere, so the generic rule can only strip
something this reorg put there. The generalisation is what lets the hand pass
(brace expansions, which are not `<group>/<round>` pairs) stay inside the same
proof. The old script is kept at
`Docs/reorg_0827/rewrite_dataset_paths.py.s1.bak`.

**After the `.pre0827.bak` files are deleted this check can no longer be re-run.**
Its permanent substitutes are: the sha256 pairs in
`experiments/v3_0823/ACCOUNTING.md` §4.13, and `git diff` — every sealed ledger
is git-tracked, so the pre-move bytes are in the index until the orchestrator commits.

## Item 6 — helper (adapted per the stage brief; no GPU code was run)

| check | result |
|---|---|
| `variation_kit.round_dir(name)` over all 196 rounds | **196 / 196**, each equal to `<root>/<group>/<round>` |
| a name with no directory (`260826_v3a_segfill_smoke`) | raises `FileNotFoundError` (does not invent a path) |
| `scripts/tests/test_round_dir.py` | **11 / 11 PASS** |
| `scripts/lib/negobs_paths.sh` → `negobs_round` | `260819_main_on` → `dataset/v2_corpus/…`; `260731_data_s01` → `dataset/_archive/scene_dev_2607/…`; miss → rc 1 |
| `python3 variation_kit.py` self-check | PASS |
| `import variation_kit, scene_common` | ok |
| `scripts/regression_check.py --selftest` | PASS (all items) |
| `scripts/stamp_round.py --self-check` | **8 / 8 PASS** |
| `scripts/check_data_run.py 260819_main_on` | found and read the moved round, all 33 scenes, non-zero cuts (its 6 quality FAILs are pre-existing properties of that 08-19 round, not path damage) |

## Item 7 — why the R3 smoke is S3's, not S2's

The four "silent-empty" gates build their paths **in code**, not as string
literals, so no string rewrite could reach them and they would report 0 frames
today — a false alarm, not damage:

```
experiments/nightrun_0820/ctrl_dressing/hash_gate.py:316  os.path.join(REPO, "dataset", round_name)
experiments/weekend_0823/cue_audit/gates_cueoff.py:96     glob.glob(os.path.join(REPO, "dataset", prefix + "*"))
experiments/v3_0823/code/w1b_verify.py:120                glob.glob(os.path.join(REPO, "dataset", run, "*", scene, ...))
experiments/v3_0823/code/w1c_hashgate.py:78               os.path.join(REPO, "dataset", run, "manifest.json")
```

These are exactly the sites the master plan assigns to S3 (`round_dir()` /
`negobs_round`). The smoke must run **after** that conversion. Remaining
measured population for S3: **49** `os.path.join(…, "dataset", <expr>)` in 32
files and **153** `dataset/$var` or `dataset/{expr}` in 43 files — 65 distinct
`.py`/`.sh` files, of which 2 are this reorg's own scripts (21 occurrences).

## Item 8 — byte accounting

288 / 288 files satisfy `len(new) − len(bak) == n_subs × (1 + len(group))`.
Total **+893,221 B**, identical to the S1 dry-run prediction.
The two `dataset_manifest_v2corr*.json` show `+56,650` = 5,663 automatic
substitutions × 10 plus the hand pass's 2 × 10 (`v2_corpus/`).

## Item 2 — symlink ledger

| population | before | after | form |
|---|---:|---:|---|
| `dataset/*_g7fix{,M}/` shadow trees (8) | 2,855 absolute | 2,855 | **relative**, e.g. `../../../260820_boost_e_on/train/scene09/…` |
| `experiments/dayrun_0820/yolo_ds/images/` | 2,832 absolute | 2,832 | **relative**, `../../../../../dataset/v2_corpus/…` |
| everything else (scene kits, `look_check` roots) | 57 relative | 57 | untouched |
| **total** | **5,744** | **5,744** | broken **0** |

All 5,687 retargets are logged in `Docs/reorg_0827/symlink_retarget.tsv` with
old target, new target and what it resolves to; every one resolves to the path
the `ROUNDS.json` map predicts (`status ok` 5,687 / 5,687).

## `.pre0827.bak` deletion

Deleted only after all ten items passed. Count and the exact file list are in
`Docs/reorg_0827/S2_report.md` §7.
