# W2-D — Comment/docstring translation pass (6 files)

Date 2026-07-30 · branch `feat/realism-v1` · no commit (supervisor commits)

Scope, exactly as assigned: `scene_common.py`, `ground_kit.py`, `infra_kit.py`,
`stair_kit.py`, `facade_kit.py`, `scripts/regression_check.py`.
Korean **comments and docstrings** translated to concise English. **No code changed.**
**No runtime string literal touched** — Korean judgment/diagnostic messages are preserved
verbatim.

---

## 1. What was translated

| file | comments | docstrings | total items |
|---|---:|---:|---:|
| `scene_common.py` | 669 | 48 | 717 |
| `ground_kit.py` | 222 | 55 | 277 |
| `scripts/regression_check.py` | 216 | 17 | 233 |
| `facade_kit.py` | 90 | 22 | 112 |
| `infra_kit.py` | 73 | 22 | 95 |
| `stair_kit.py` | 69 | 9 | 78 |
| **total** | **1,339** | **173** | **1,512** |

Method: comment tokens were located with `tokenize` (COMMENT tokens only) and docstrings
with `ast` (the leading `Expr`/`Constant` of Module/ClassDef/FunctionDef only). Each item
was replaced in place at its exact source span, bottom-up. Nothing else in the file was
rewritten, so no non-docstring string literal was reachable by the tool by construction.

---

## 2. Proof obligations

### 2.1 `py_compile` — 6/6 PASS

```
OK scene_common.py
OK ground_kit.py
OK infra_kit.py
OK stair_kit.py
OK facade_kit.py
OK scripts/regression_check.py
```

### 2.2 `python3 ground_kit.py` — exit 0

`GK_EXIT=0`, and the **full stdout is byte-identical** to the pre-translation run
(`diff` of pre/post capture returned empty). The self-check ends with
`ground_kit 자기검산 — 전 항목 통과` in both runs — i.e. the Korean runtime strings of the
self-check survived unchanged. `[evidence — scratchpad gk_pre.txt vs gk_post.txt, diff empty]`

Additional (not required, run as extra assurance):
* `python3 infra_kit.py` — exit 0
* `python3 scene_common.py` (pure-maths self-check) — exit 0
* `python3 scripts/regression_check.py --help` — exit 0

### 2.3 `ast.dump` equality per file (comments stripped) — the formal check, 6/6 IDENTICAL

Docstrings are also stripped before dumping (a docstring is an AST node, so translating one
would otherwise change the dump). SHA-256 of `ast.dump(tree, annotate_fields=True,
include_attributes=False)`:

| file | pre-translation | post-translation | equal |
|---|---|---|---|
| `scene_common.py` | `5022cd46…98455` | `5022cd46…98455` | ✔ |
| `ground_kit.py` | `c852c547…fb9a9` | `c852c547…fb9a9` | ✔ |
| `infra_kit.py` | `1a2dd55f…6e7de` | `1a2dd55f…6e7de` | ✔ |
| `stair_kit.py` | `40cb4d32…2f2f0` | `40cb4d32…2f2f0` | ✔ |
| `facade_kit.py` | `538965b3…c7afd` | `538965b3…c7afd` | ✔ |
| `scripts/regression_check.py` | `bbac3a92…a4b19` | `bbac3a92…a4b19` | ✔ |

Full digests (post-translation working tree):

```
5022cd46b772c3adc3aa1a381c1dcbd938fc9429eefe761b3e18fe28e8e98455  scene_common.py
c852c547ea114e98e44765cf82f76c890bc630a2f661fd1eb7f2e2f4703fb9a9  ground_kit.py
1a2dd55f77c1740d157163b7be802a262c71cb34169ec657f3d5a825cc16e7de  infra_kit.py
40cb4d328293d094fbe9a16f5b5624a2e94eac6dc88e097c59745a28e952f2f0  stair_kit.py
538965b3208f92f0f0d1fd3224780925188b97fc12711e2ef018db5a325c7afd  facade_kit.py
bbac3a9249ecb988c27ad83c25636e48ce29ff73aecec07e572c1769f6ba4b19  scripts/regression_check.py
```

The same six digests were also computed from `git show HEAD:<file>` (HEAD `7301976`, whose
copies of these 6 files still carry the original Korean) — **all six match**. That is an
independent confirmation that the diff against HEAD is comment/docstring-only.

### 2.4 `scripts/geom_invariance_check.py` — hashes IDENTICAL, 33/33

The check had to be run in a **frozen snapshot** of the repository. See §4 for why.

* Arm A — snapshot with the 6 files restored to their pre-translation (Korean) content
* Arm B — the same snapshot with the translated 6 files
* Everything else (all 33 scene files, `building_kit.py`, `batch1_common.py`, assets)
  byte-identical between arms.

Result:

```
ARM_A_EXIT=0   [R-4] 33/33 PASS   [R-6] 33/33 PASS
ARM_B_EXIT=0   [R-4] 33/33 PASS   [R-6] 33/33 PASS
diff(arm A scene rows, arm B scene rows) → empty      # 33/33 prim counts and hashes identical
```

`[evidence — scratchpad arena_before.txt vs arena_after.txt, diff empty on all 33 rows]`

The only textual difference anywhere in the two reports is the R-5 allow-list line, which
prints the source line it permits and therefore quotes the (now English) trailing comment:

```
- · 허용 scene_common.py:189  LOOK_V1 = … == "1"          # 상위(종전 호환)
+ · 허용 scene_common.py:189  LOOK_V1 = … == "1"          # Umbrella (backwards compatible)
```

R-5 itself still passes (the token count and file are unchanged; the checker works on tokens
with comments stripped).

---

## 3. Runtime strings preserved

Residue census after translation (Hangul remaining, by category):

| file | KO comments | KO docstrings | KO string literals (kept) |
|---|---:|---:|---:|
| `scene_common.py` | 0 | 0 | 62 |
| `ground_kit.py` | 0 | 0 | 353 |
| `infra_kit.py` | 0 | 0 | 194 |
| `scripts/regression_check.py` | 0 | 0 | 96 |
| `stair_kit.py` | 0 | 0 | 41 |
| `facade_kit.py` | 0 | 0 | 1 |
| **total** | **0** | **0** | **747** |

All 747 are runtime output or data-ledger strings and were deliberately left alone, e.g.
* `stair_kit.py:600` `"계단참 %d 개 부족 — 낙차 %.2f m 직통은 한국에 존재할 수 없는 계단"`
* `infra_kit.py:97` `"gutter_L_width": (0.30, "확인", "국도건설공사 설계실무요령 …")` — the
  `INFRA_DIMENSIONS` provenance ledger, read at runtime by the self-check
* `regression_check.py:649` `"[이월 — 악화]"` — verdict tags
* `ground_kit.py` gate messages and the `GROUND_DIMENSIONS` source column

Translation conventions used: em-dashes and `·` separators normalised to ASCII, `[실측]` →
`[measured]`, `[추정]` → `[estimate]`, `[확인]` → `[verified]`, `[근거 없음]` → `[no source]`,
`[계산]` → `[computed]`, `[통계]` → `[statistic]`, `[법령]` → `[statute]`, `[지식]` →
`[knowledge]`. Statute citations keep their article numbers and the §/table references
untouched. Evidence tags on every number were carried over verbatim.

---

## 4. Blocker / risk — concurrent uncommitted edits to the 33 scene files

This must be read before the supervisor commits.

While this task ran, **another agent was editing the same working tree**:

* `HEAD` moved from `3ce77d5` to `7301976` mid-task ("주석 영어화 2차 — 9파일").
* 26 scene files under `scenes/main/` and `scenes/batch1/` are modified in the working tree
  and were still being written during this session (e.g. `scene01_campus_stairs.py` mtime
  21:19, `scene04_parktrail.py` 21:25, while this task was running at 21:29).

Consequences observed:

1. **The scene geometry has changed under us.** Against the baseline taken at the start of
   this task (HEAD `3ce77d5`, clean tree), 26 of 33 scenes now have different prim counts —
   these are large, e.g. `scene04` 525 → 1,035, `scene07` 530 → 1,141, `scene10` 641 → 1,010,
   `sceneN1` 469 → 540. None of this is attributable to W2-D (proved in §2.4: with all else
   held frozen, the translation moves 0 hashes).
2. **A live run of `geom_invariance_check.py` is currently unreliable.** Run against the live
   tree it returned `[R-6] 31/33 ✗ FAIL scene08, scene11` — a race artifact: the checker
   launches three subprocess arms sequentially and the scene files changed between them. The
   same check on a frozen snapshot returns 33/33 PASS on both arms.

Recommendation: re-run `scripts/geom_invariance_check.py` on the live tree once the
concurrent scene work has settled, and treat the 26 changed prim counts as belonging to that
other work item, not to W2-D.

---

## 5. Files touched

Only the six assigned files. `sceneD4` untouched; no scene file, `building_kit.py`,
`batch1_common.py`, brief or spec was modified by this task.

```
facade_kit.py                  +432 −363
ground_kit.py                  +524 −475
infra_kit.py                   +542 −473
scene_common.py                +969 −944
scripts/regression_check.py    +314 −297
stair_kit.py                   +279 −259
```

(Line counts differ from a pure 1:1 replacement because a few multi-line Korean comment
blocks re-wrapped to a different number of English lines; every comment token was replaced
1:1 and no line of code moved — confirmed by the AST equality in §2.3.)
