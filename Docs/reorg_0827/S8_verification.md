# S8 — independent adversarial verification (2026-08-27)

Branch `chore/reorg-0827`, repo `/home/vislab/Desktop/work_sy/Practice_NegObs`.
Read-only stage: this file is the **only** thing S8 wrote. Nothing was moved, edited,
deleted, committed, stashed or checked out; `Practice_NegObs_edge` was not touched; no GPU.
`git status --porcelain` is **byte-identical before and after** this stage, `__pycache__`
count **0**, symlinks **5,734 / 0 broken**, both sealed sha256 unchanged, `look_check/INDEX.md`
sha256 unchanged (`f8ac048e…6276`).

Method: every number below was re-derived from the tree with `os.walk` / `find` / `du -sb` /
`sha256sum`, never with `grep -r` (this shell's `grep` is ugrep with `--ignore-files`).
All Python was run with `PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1` so no bytecode was
written; syntax checks use `compile()`, not `py_compile`, for the same reason. The 9-minute
`import_check.py --all` sweep was **not** run — it is not read-only in spirit (it rewrites and
restores 40 artifacts) and checks 7's syntax sweep covers the same ground without touching the tree.

**Verdict: PASS with documentation fixes.** No structural defect, no data loss, no broken
reference, no unexplained byte. Ten owner-facing documentation fixes are listed in §3; three of
them are wrong-as-written statements a reader would act on, and none of them was applied.

---

## 1. PASS / FAIL table

| # | Check | Claimed by the stages | Measured by S8 | Verdict |
|---|---|---|---|---|
| 1a | `dataset/` top level | 9 groups + `ROUNDS.json` + `README.md` | exactly the 11 expected entries, 0 extra, 0 missing | **PASS** |
| 1b | round dirs, depth, uniqueness | 197 (196 + `260827_handson`) | **197**; 8 groups at depth 2 + 7 `_archive/<g>` at depth 3; **0 duplicate names**; no stray file at round depth | **PASS** |
| 1c | `du -sb` sum of the original 196 | 105,648,176,652 B, "0 rounds changed size" | **105,648,057,910 B (−118,742)**; 79 rounds changed size — **fully explained**, see §2.1 | **PASS (note)** |
| 1d | `ROUNDS.json` vs disk | keys == on-disk rounds | 197 == 197, **0** either way, **0** group mismatches | **PASS** |
| 1e | `round_dir()` resolves every round | 197/197 | **197/197**, every result an existing dir; `rounds_matching("")` → 197 | **PASS** |
| 2a | residual old-form `dataset/<round>` | 0 | **4 occurrences in 2 files** — 3 in `Docs/guides/ISAAC_HANDSON.md` (fix D1), 1 in a gitignored render log | **PASS (1 doc fix)** |
| 2b | residual old absolute prefix + round | 0 | **1** (same render log, `look_check/logs/260827_handson.log:12`) | **PASS (note)** |
| 2c | `Docs/experiment/` | 0 outside 2 declared | **6 in 2 files** — sealed `PREREG_V3.md` (2) + its `PREREG_V3_PATHMAP_0827.md` (4). Exactly the declared pair | **PASS** |
| 2d | `Docs/legacy/`, 7 compat names, `Docs/surveys/real_reference_expansion.md`, `PROJECT_STATE_0826` | 0 each | **0 each** (10 patterns) | **PASS** |
| 2e | root `run_*.sh` cited as a path | 0 | **15**, all inside `look_check/**/round_stamp.json` `dirty_paths` git-status snapshots dated 08-14/08-15 — historical records of the working tree at render time, gitignored, not live citations | **PASS** |
| 2f | `_review_w2`, 12 `look_check/` root log names | 0 | **13**, all in `look_check/INDEX.md` §6 (the old→new relocation map — by design) | **PASS** |
| 3 | manifest path existence | 8 pre-existing dangling, 0 new | 10,507 json/csv/txt/yaml walked; **82,747** concrete `dataset/` path strings checked; **4 missing + 4 brace-placeholder = exactly the 8 documented**; **0 NEW** | **PASS** |
| 4a | symlink total / broken | 5,734 / 0 | **5,734 / 0** (5,687 into `dataset/` + 37 kit files + 10 dirs) | **PASS** |
| 4b | no absolute targets | only `/usr/bin/python3`-style allowed | **ZERO absolute targets of any kind** (the venv ones went with `venv_yolo`) | **PASS** |
| 4c | retarget correctness | 5,687 ok | **all 5,687 ledger rows re-verified**: `realpath(link) == map(old_target)`, relative, resolving, 0 bad. 50 g7fix + 50 `yolo_ds` samples resolve to the expected round | **PASS** |
| 5a | `PREREG_V3.md` sha256 | `05f41322…f56a` | **match** | **PASS** |
| 5b | `PREREG_CUEOFF.md` sha256 | `9c4733bb…56b1` | **match** | **PASS** |
| 5c | inverse proof, §4.13 ledgers | inverse(current) == old sha256 | **6/6**: all four sealed manifests + both `v2corr` reproduce the recorded OLD sha256 exactly, and each current file matches the recorded NEW sha256 | **PASS** |
| 5d | sealed ledgers claimed byte-unchanged | 9 files unchanged | **9/9** hold **0** `dataset/` strings and are **byte-equal to `HEAD`** | **PASS** |
| 5e | inverse proof, extended to all rewritten tracked files | (not claimed) | 155 tracked; **137 inverse(current) == HEAD**; 18 mismatches, **all 18 attributable** to a later stage's ledger (S3 ×11, S4 ×1, S5 ×6). 0 unexplained | **PASS** |
| 6a | `look_check/` round conservation | 639 = 377 live + 262 archived | **639 = 377 + 262**; waves w2 51 · w2d 8 · w3 72 · w3fix 131 (exactly S4) | **PASS** |
| 6b | no symlinks in scene roots | 0 | **0** across all 33 scene roots and all archive scene dirs; the only `look_check/` symlinks are the 2 permitted root ones | **PASS** |
| 6c | move ledger applied | 322 rows | **322/322**: every destination exists, every source is gone, 0 empty dirs left | **PASS** |
| 6d | `valset.py --corpus history --check` | 94 / FAIL 1 / WARN 2 | **94 / 1 / 2**, rc 0, output **byte-identical to both** the pre-move and post-move snapshots | **PASS** |
| 6e | `valset.py --corpus fp --check` | 156 / 0 / 0 | **156 / 0 / 0**, rc 0, byte-identical to both snapshots | **PASS** |
| 6f | `INDEX.md` idempotent regen | idempotent | re-ran the generator: **byte-identical**, same sha256 `f8ac048e…6276`. `git diff --quiet` returns **1**, but only because `INDEX.md` is a legitimately modified-vs-`HEAD` tracked file awaiting commit (it is ` M` in `git status`) — the idempotence property itself holds | **PASS (caveat)** |
| 7a | `smoke_round_sites.py` | 33 PASS / 0 FAIL | **33 PASS · 0 SKIP · 0 FAIL**, rc 0 (S3's report body says 32 twice — S3 is self-inconsistent; 33 is right) | **PASS** |
| 7b | `test_round_dir.py` | 15/15 | **15/15**, rc 0 | **PASS** |
| 7c | syntax of every changed `.py` | clean | **115/115** compile clean | **PASS** |
| 7d | `bash -n` of every changed `.sh` | clean | **55/55** clean | **PASS** |
| 7e | `regression_check.py --selftest` | rc 0 | **전 항목 통과**, rc 0 | **PASS** |
| 7f | `stamp_round.py --self-check` | 8/8 | **8/8**, rc 0 | **PASS** |
| 8a | `git status --porcelain` categories | 10 `D`, 21 renames | **333 `M` · 14 `R` · 7 `RM` · 10 `D` · 13 `??`** | **PASS** |
| 8b | the 10 `D` lines | the 10 deleted symlinks | **exactly those 10**, and each is mode **120000** (symlink) in `HEAD` | **PASS** |
| 8c | `git add -A --dry-run` | — | **614 files** (274 new = 5.25 MB · 340 modifications). No `*.pt`, `*.pth`, `*.png`, `*.npy`, `__pycache__`, `venv` | **PASS** |
| 8d | files > 5 MB that would be added | documented only | **2**: `dataset_manifest_v3_seg3.json` (9.58 MB) and `dataset_manifest_v3.json` (9.45 MB) — both **already tracked**, both the §4.13-documented rewrites. No new large blob class | **PASS** |
| 8e | ignore rules | `.pt` closed, gazebo PNGs ignored | `best.pt` → `.gitignore:15 *.pt`; `frames/**/*.png` → `.gitignore:104`; `look_check/*` ignored with `README.md`/`INDEX.md` un-ignored | **PASS** |
| 9 | owner-facing docs | all paths exist, no contradictions | **423 path tokens checked**; every cited real path in `README.md`, `experiments/README.md`, `dataset/README.md` resolves (41/41 experiment files, 22/22 README targets); **3 wrong-as-written statements + 7 stale/imprecise numbers** — §3 | **PASS-with-fixes** |
| 10 | admitted-but-unfixed items | 4 named | **5 confirmed on disk + 4 more**, all LOW severity — §4 | **PASS (note)** |

---

## 2. Discrepancies found

### 2.1 `dataset/` byte total is 118,742 B below the pre-move snapshot — benign, and exactly accounted for

The brief's invariant (`sum du -sb == 105,648,176,652`) **does not hold literally**: the measured
sum over the original 196 rounds is **105,648,057,910 B**, and **79 rounds changed size**. Both
halves are fully explained and neither is data loss:

* **−125,644 B** — the 2,855 g7fix links were retargeted from absolute to relative, and `du -sb`
  counts a symlink's apparent size as the *length of its target string*. Per-round the du delta
  equals the target-length delta from `symlink_retarget.tsv` **exactly**, all 8 trees
  (−18,354 / −4,752 / −18,354 / −4,752 / −32,082 / −7,128 / −32,082 / −8,140). That the deltas
  match to the byte also proves the regular files in those trees are untouched.
* **+6,902 B** — the in-`dataset/` sidecar rewrites. This equals, to the byte, the sum of
  `delta_bytes` over the 109 `dataset/` rows of `rewrite_apply.tsv`.

`−125,644 + 6,902 = −118,742`. **Consequence:** S2 §2's claim *"the sum … is identical to the S1
snapshot, and 0 rounds changed size individually"* was true at the instant S2 measured it (after
the moves, before the rewrite and retarget) but is **stale as a statement about the final tree**.
Nothing needs fixing on disk; the orchestrator should not re-assert that sentence.

### 2.2 One live old-form `dataset/` path remains in a document — `Docs/guides/ISAAC_HANDSON.md:38-40`

The only old-form `dataset/<round>` strings left anywhere outside gitignored logs and the reorg's
own records. See fix **D1**. The one other hit,
`look_check/logs/260827_handson.log:12`, is the render log written *before* the round was filed
into `misc/`; it is a historical record in a gitignored tree and is correct as history.

### 2.3 Counts in the stage reports that do not reproduce

| report | claim | measured | direction |
|---|---|---|---|
| S3 §4(d), §7.2 | `smoke_round_sites.py` = **32** checks | **33** (S3's own headline table says 33) | S3 self-inconsistent; harmless |
| S4 §2 item 1 | **23** `.py`/`.sh` files cite an archived look_check round as a path (8 py + **15** sh) | **17** files (9 py + **8** sh) | S4 over-counted; safe direction |
| S5 §2 table | S5-3 `Docs/experiment/` → **44** files / 83 occurrences | **45** files / 83 (re-derived from `docs_citation_edits.tsv`) | `REORG_0827.md:32` says 45 and is the correct one |
| S6 §1.4 | `git add -An` on `gazebo_wh_0824` = **195 files / 824 KiB** | **196 files / 852,370 B** | trivial drift |

None of these changes a verdict; they are logged so the orchestrator does not quote a number
that cannot be reproduced.

### 2.4 `git diff --quiet look_check/INDEX.md` fails, for a correct reason

The brief's literal test returns 1. The generator is genuinely idempotent (byte-identical output,
same sha256), and the diff is against `HEAD`, where `INDEX.md` is still the stale 07-30 file that
S4 replaced. `INDEX.md` is ` M` in `git status` and is one of the 614 files the commit will stage.
No action.

---

## 3. Documentation fixes needed (NOT applied — `file:line` → change)

Ordered by how likely the owner is to act on the wrong statement. **D1–D3 are statements that are
false today**; D4–D8 are stale numbers; D9–D10 are usability.

**D1 · `Docs/guides/ISAAC_HANDSON.md:38-40`** — the "결과:" block prints
`dataset/260827_handson/manifest.json`, `…/val/scene01/L0__s20260827__0000.png`,
`…/val/scene01/variation.json`. The round was filed into `misc/` by S6, so all three paths return
"No such file or directory" today, in a document whose own line 3 promises "경로·출력은 진짜".
→ Either prefix the block with "(갓 찍었을 때 · 정리 전)" or rewrite the three lines as
`dataset/misc/260827_handson/…` (the form §2 line 68 already uses). Prefer the second: line 47
already explains that a fresh render lands flat, so the block does not need to carry that lesson.

**D2 · `experiments/README.md:16`** — the `gazebo_wh_0824/` row reads
"**중단 상태** — 캡처·추론은 됐고 readout 의 '우리 모델' 열과 보고서가 비어 있다", and its
"여기부터" column lists only `make_wh_worlds.py` / `capture_run.sh` / `infer_ours.sh`, and its
"남은 일" points at `PROJECT_STATE.md §1`. All false since S6: `out/readout.csv` carries all 12
`ours`/`gt` columns with **0 empty or NaN values** (S8 re-verified, and re-computed Table B from
the CSV — it reproduces the report to the last decimal), and
`experiments/gazebo_wh_0824/WAREHOUSE_VARIANT.md` (107 lines) exists.
→ Change the "무엇을 했나" cell to "…**마감(08-27, D102)** — readout 'ours' 열 완성 + 결론 보고서",
and make the "여기부터" cell `WAREHOUSE_VARIANT.md` → `out/readout_tables.md`.

**D3 · `Docs/campaign/status/PROJECT_STATE.md:11`** — "08-27에 **저장소 정리만** 했다.
렌더·학습·커밋 없음." Contradicted by S6 (a 2-cut / 25 s GPU render of `260827_handson` under the
GPU lock, plus a bounded Isaac GUI boot), by `dataset/README.md:6` ("08-27에 실습 렌더 1개가 늘어
197개"), by `Docs/guides/ISAAC_HANDSON.md`, and by D103 in the ledger. This is the file the doc set
itself calls the first-read document, and it contradicts its own §0 line 33 which links the guide.
→ "08-27에 저장소 정리 + 끊긴 두 갈래 마감(창고 변형 D102 · 실습 가이드 D103, 실습 렌더 2컷)을 했다.
학습·커밋 없음."

**D4 · `README.md:167`** — "`experiments/mainrun_0819/DECISIONS.md` — 자율 판단 전체 원장
(**D1~D101**, …)". Measured: the ledger holds **104** D-entries, max **D104**;
`PROJECT_STATE.md:31` already says D1–D104. → `D1~D104`.

**D5 · `README.md:29`** — "`*_kit.py` + `scene_common.py` (루트 **10개** 파일)". Measured: **8**
`*_kit.py` + `scene_common.py` = **9**. `REORG_0827.md:41` says "8개 + `scene_common.py`" and is
correct, so the two maps contradict each other. → `루트 9개 파일`.

**D6 · `REORG_0827.md:7, 9, 14`** — the heading "196칸 → 9칸", the line "196개 라운드", and
"`misc`(**1**)". After S6 filed `260827_handson` the tree holds **197** rounds and `misc` holds
**2**; `dataset/README.md` was updated for this and `REORG_0827.md` was not.
→ at :9 append "(08-27 실습 렌더 1개가 더해져 지금은 197)"; at :14 `misc`(1) → `misc`(2).
Same 196 appears at **`Docs/campaign/status/PROJECT_STATE.md:16`** — fix in the same pass.

**D7 · `REORG_0827.md:60`** — "`dataset/ROUNDS.json` 이 … 대조표다(**196줄**)". Measured **197**
entries; `dataset/README.md:44` already says 197줄. → `197줄`.

**D8 · `REORG_0827.md:65`** — "단계별 보고서 `S1~S5_report.md`". `S6_report.md` exists, and this
`S8_verification.md` now does too. → "`S1~S6_report.md` · 검증 `S2_verification.md`·`S8_verification.md`".

**D9 · `README.md:32` and `README.md:78`** — `look_check/` listed as "**33 GB**". Measured
**32.03 GiB** (S4's own post-deletion figure; 37.29 − 5.26). Every other size in that table is a
correct GiB/MiB value, so this one reads as stale rather than as a unit choice. → `32 GB`.

**D10 · `dataset/README.md:16`** — the `v3_library/` row's "(W1 팔·밴드, W2 h67)" is un-glossed
internal shorthand in the one document written for a reader who cannot browse folders; every other
row in that table glosses its jargon (`segfill(세그 채움)`, `cuecls(단서 분류)`, `CUE-OFF(단서 제거)`).
→ add e.g. "W1·W2 = 라이브러리 렌더 1·2차 물결 · 팔 = 2×2 4팔(A/B/C/D) · h67 = 씬 H6·H7".
(Same class, lower priority: `experiments/README.md:12` "τ 곡선" and `:27` "D35/R3".)

**Verified clean and needing no fix:** every path cited by `experiments/README.md` (41/41 exist),
by `README.md` (22/22), by `dataset/README.md`; every line-number citation in
`ISAAC_HANDSON.md` (`run_data_render.py:603` really is `del math`, `:594` really is the comment
that explains it, `scene01_campus_stairs.py:1602` really is `{"headless": capture_mode, …}`);
all four `_review/w4` galleries; all seven cycle sizes in `experiments/README.md`;
`dataset/README.md`'s training-canon numbers (**3,654 frames · 33 rounds · v3_library 2,742 +
v2_corpus 912** — re-derived from `dataset_manifest_v3_seg3.json`, exact); and both tables of
`WAREHOUSE_VARIANT.md` (re-computed from `out/readout.csv`: fire/centre in Table A and all four
statistics × 8 rows in Table B reproduce, the only difference being 0.051 rounded to 0.050).

---

## 4. Open items (admitted by the stages, or found here) — with severity

| # | item | measured evidence | severity | recommendation |
|---|---|---|---|---|
| O1 | `scripts/run_data_render.py:603` `del math` raises `UnboundLocalError` at teardown of every render | confirmed: `import math` at :304, `del math` at :603, the pre-existing defect documented in-code at :594 and warned about in `ISAAC_HANDSON.md:43-45` | **LOW-MED** | pre-existing and in `HEAD`; artifacts are all on disk before it fires. Not reorg damage. Fix it in a separate, tested change — not during a tidy-up |
| O2 | `yolo_ds` holds 192 stale `train ∩ val` duplicate links | confirmed exactly: train 1,632 / val 384 / test 816 = 2,832, `|train ∩ val| = 192`; all resolve (0 broken) | **LOW** | harmless but `yolo_ds` disagrees with its own `build_report.json`. Cleaning is a 192-file deletion → needs owner approval. Leave |
| O3 | render drivers still write flat paths for archived look_check rounds | **17** files cite an archived round as a path (**8** `scripts/rounds/run_*.sh` + 9 scene `.py` comments) — S4 said 23/15 | **LOW** | re-running writes a duplicate flat dir beside the archive, never an error. S4's decision not to rewrite the historical record is right; a one-line guard in the 8 drivers would be cheap |
| O4 | the parked ambiguous `dataset/260820_boost_{h,e}` | still unrewritten in `logs/boost_render.log` (8) and `scripts/rounds/run_260820_boost.sh:332` (1) | **LOW** | one brace form, two possible groups. Owner decision, or leave — the executable path already resolves through the helper |
| O5 | `experiments/v3_0823/logs/cue_extent_frames.json.bak` still carries 4,872 pre-move paths | confirmed (dated 08-24, gitignored, not on the approved delete list); its sibling `cue_extent_attrib.json.bak` carries 0 | **LOW** | by design. Any future residual scan must keep excluding `*.bak` |
| O6 | 49 dangling `Docs/` citations | `s5_link_check.py` re-run: 279 cited · 49 broken · **0** into a path the reorg created | **LOW** | 48 are the pre-existing ghost-citation backlog. The 49th is the declared one: the **sealed** `PREREG_V3.md` cites `Docs/experiment/V3_DESIGN_0823.md`, resolvable only through `PREREG_V3_PATHMAP_0827.md`. Correct given the seal; make sure the pathmap note is linked from `Docs/INDEX.md` |
| O7 | `make_allview_sheet.py:74 views_of()` substitute-view pool is now live rounds only | S4's own note; unchanged | **LOW** | a behaviour change in the wanted direction, already documented |
| O8 | `verdict_panels.py:559` / `view_overlay.py` will draw grouped paths into future panels | S5's note; existing panels not re-rendered | **COSMETIC** | none |
| O9 | 36 `ModuleNotFoundError` in the full import sweep | S3/S4/S5/S6 all report the same 36, none in an edited file | **NONE** | environmental (torch / isaacsim / sibling-module cwd). Not a reorg effect |

---

## 5. What S8 ran (reproducible)

```
python3 scripts/valset.py --corpus history --check          94 / FAIL 1 / WARN 2   rc 0
python3 scripts/valset.py --corpus fp      --check         156 / FAIL 0 / WARN 0   rc 0
python3 scripts/make_lookcheck_index.py                    byte-identical output   rc 0
python3 scripts/reorg/smoke_round_sites.py                 33 PASS · 0 SKIP · 0 FAIL
python3 scripts/tests/test_round_dir.py                    15/15
python3 scripts/stamp_round.py --self-check                8/8
python3 scripts/regression_check.py --selftest             전 항목 통과            rc 0
python3 scripts/reorg/s5_residual_gate.py                  14/14 PASS · 14,518 files
python3 scripts/reorg/s5_link_check.py                     279 cited · 49 pre-existing · 0 new
find . -type l | wc -l                                     5,734        find . -xtype l   0
git add -A --dry-run                                       614 files
```
plus seven ad-hoc `os.walk` scanners (dataset census · full-repo residual scan over 60,825 files /
14,530 text files · manifest existence over 82,747 path strings · symlink ledger re-verification ·
inverse-transform proof over 155 tracked files · look_check census · owner-doc fact check).
