# W2-D — Comment/Docstring Translation, Batch 2 (conflict-free set)

**Date** 2026-07-30 · **Branch** `feat/realism-v1` · **Scope** 9 files
(the conflict-free set; scene files and the 6 core modules are owned by other
agents and were not touched)

Korean comments **and** docstrings translated to concise English. No code
changed. No string literal used in runtime output changed — Korean judgment and
report messages stay exactly as they were.

---

## 1. Result summary

| # | file | lines pre → post | ko comments removed | ko docstrings removed | ko runtime literals (pre = post) |
|---|------|------------------|--------------------:|----------------------:|---------------------------------:|
| 1 | `building_kit.py`                | 1687 → 1856 | 187 → 0 | 38 → 0 | 54 = 54 |
| 2 | `scenes/batch1/batch1_common.py` |  268 →  288 |  24 → 0 | 10 → 0 |  0 =  0 |
| 3 | `scripts/imgstats.py`            |  324 →  344 |  27 → 0 |  7 → 0 |  9 =  9 |
| 4 | `scripts/make_compare_sheet.py`  |  154 →  156 |   4 → 0 |  1 → 0 | 44 = 44 |
| 5 | `scripts/make_hq_sheet.py`       |   87 →   87 |   0 → 0 |  1 → 0 | 46 = 46 |
| 6 | `scripts/make_overview.py`       |   84 →   85 |   2 → 0 |  1 → 0 | 23 = 23 |
| 7 | `scripts/rtx_probe.py`           |  180 →  185 |   2 → 0 |  1 → 0 |  3 =  3 |
| 8 | `scripts/spike_realism.py`       |  593 →  610 |  44 → 0 |  6 → 0 |  9 =  9 |
| 9 | `assets/signs/gen_signs.py`      |   48 →   49 |   4 → 0 |  1 → 0 |  5 =  5 |
| | **total** | **3425 → 3660** | **294 → 0** | **65 → 0** | **193 = 193** |

Nothing was skipped. No file in the assigned set was already fully English —
all nine carried Korean comments or docstrings.

Line-count drift (+235) is entirely from English prose needing more lines than
the Korean it replaced, plus reflowing three over-long lines. This is the
permitted drift; the AST proof below shows no statement moved.

---

## 2. Proof — AST equality (comments and docstrings stripped)

Method: `ast.parse` → strip the leading string-constant `Expr` from every
`Module`/`FunctionDef`/`AsyncFunctionDef`/`ClassDef` body → `ast.dump(...,
include_attributes=False)` → SHA-256. Comments never reach the AST, so this
hash is invariant under any comment-only or docstring-only edit and changes
under any code edit, including a changed literal, default, or line ordering.

| file | AST SHA-256 (pre) | AST SHA-256 (post) | equal |
|------|-------------------|--------------------|:-----:|
| `building_kit.py`                | `fbe5504e62f1eeee…` | `fbe5504e62f1eeee…` | yes |
| `scenes/batch1/batch1_common.py` | `86fa8d2b1c39272d…` | `86fa8d2b1c39272d…` | yes |
| `scripts/imgstats.py`            | `2cb0f027fb60822a…` | `2cb0f027fb60822a…` | yes |
| `scripts/make_compare_sheet.py`  | `c2066822edbf8ccf…` | `c2066822edbf8ccf…` | yes |
| `scripts/make_hq_sheet.py`       | `dccca747b558c23a…` | `dccca747b558c23a…` | yes |
| `scripts/make_overview.py`       | `bf6a737e89c26d65…` | `bf6a737e89c26d65…` | yes |
| `scripts/rtx_probe.py`           | `342fe9303720aba7…` | `342fe9303720aba7…` | yes |
| `scripts/spike_realism.py`       | `57d061d504b500fb…` | `57d061d504b500fb…` | yes |
| `assets/signs/gen_signs.py`      | `f14ccffd41572dac…` | `f14ccffd41572dac…` | yes |

`diff pre_hashes post_hashes` → empty. **AST equality: 9/9 identical.**

Full hashes:

```
fbe5504e62f1eeee0f5785c09250cf1cd2addfc5f1a7f89b46eed36b0c604109  building_kit.py
86fa8d2b1c39272d1f769337111ece6770258d1598846533d7d302b8809ced96  scenes/batch1/batch1_common.py
2cb0f027fb60822a8a34fb25ba599ed951895f5230b6cf6b85c452c67b0595b0  scripts/imgstats.py
c2066822edbf8ccfabc1737e4326b60bdde0f70575891c61c29174f78bc698c2  scripts/make_compare_sheet.py
dccca747b558c23adb5577b72f86902e52d4b6d650333e5dc5a536cb2413598c  scripts/make_hq_sheet.py
bf6a737e89c26d65f9e794626d7f37804fb13a667244d0c3ebe02ebaf56ae1f2  scripts/make_overview.py
342fe9303720aba76b45fe3f8adb995c0fdca491f8bce61dd35c42444d89d047  scripts/rtx_probe.py
57d061d504b500fbdb51c6f1b39c75b8f9b26196a7b907c0c89ebf4116fb1c3f  scripts/spike_realism.py
f14ccffd41572dacfd78db3c9cf58601cb4d2ce56a316fcc6db98b46e5af38d2  assets/signs/gen_signs.py
```

This block is the post-edit run; the pre-edit run produced the identical nine
lines. Truncation in the table above is display-only — the `diff` was run over
the full hashes.

---

## 3. Proof — `py_compile`

```
python3 -m py_compile building_kit.py scenes/batch1/batch1_common.py \
  scripts/imgstats.py scripts/make_compare_sheet.py scripts/make_hq_sheet.py \
  scripts/make_overview.py scripts/rtx_probe.py scripts/spike_realism.py \
  assets/signs/gen_signs.py
```

**PY_COMPILE: 9/9 OK** (exit 0, no output).

---

## 4. Proof — `building_kit.py` self-check

```
$ python3 building_kit.py
...
검사 135/135 통과
==========================================================================
33씬 실측 (89동, scene18 town 13동은 튜플 생성이라 제외)
==========================================================================
  현행 build_building 총 프림 :   4546 (그중 창 2137)
  building_kit  총 프림       :   1855
  증감                        :  -2691 (-59.2 %)
  추론 유형 분포 : {'shop_house': 32, 'office': 34, 'apt': 6, 'backdrop': 8, 'villa': 2, 'low_shop': 7}
  LOD 티어 분포  : {'near': 22, 'mid': 35, 'far': 24, 'silhouette': 8}
EXIT=0
```

| metric | pre-edit baseline | post-edit | match |
|--------|-------------------|-----------|:-----:|
| checks passed | 135/135 | 135/135 | yes |
| exit code | 0 | 0 | yes |
| buildings measured | 89 | 89 | yes |
| current `build_building` total prims | 4546 (2137 windows) | 4546 (2137 windows) | yes |
| `building_kit` total prims | 1855 | 1855 | yes |
| delta | -2691 (-59.2 %) | -2691 (-59.2 %) | yes |
| inferred kind distribution | shop_house 32 / office 34 / apt 6 / backdrop 8 / villa 2 / low_shop 7 | identical | yes |
| LOD tier distribution | near 22 / mid 35 / far 24 / silhouette 8 | identical | yes |

Self-check output is byte-identical to the pre-edit baseline, including the two
known `[예산초과]` advisory lines (`scene13` apt/mid 26>23, `scene21`
office/mid 16>15) which are pre-existing and unrelated to this task.

---

## 5. Proof — `batch1_common` import smoke (AST / `py_compile` only, no Isaac)

`scenes/batch1/batch1_common.py` imports `scene_common` at module level, which
requires an Isaac runtime, so a real `import` is impossible in this
environment. The smoke test is therefore static, and is applied to **all nine
files** rather than just this one.

Method: parse both the pre-edit copy and the post-edit file, then compare the
full module-level API surface — every top-level import, constant assignment
(name **and** unparsed value expression), function and method signature
(positional-only / positional / `*args` / keyword-only / `**kwargs`), plus all
default and keyword-default expressions.

| file | API surface entries | pre vs post |
|------|--------------------:|-------------|
| `building_kit.py`                | 99 | identical |
| `scenes/batch1/batch1_common.py` | 19 | identical |
| `scripts/imgstats.py`            | 26 | identical |
| `scripts/make_compare_sheet.py`  | 19 | identical |
| `scripts/make_hq_sheet.py`       | 17 | identical |
| `scripts/make_overview.py`       | 17 | identical |
| `scripts/rtx_probe.py`           | 23 | identical |
| `scripts/spike_realism.py`       | 49 | identical |
| `assets/signs/gen_signs.py`      |  5 | identical |

`batch1_common` specifics confirmed unchanged:

- top-level imports: `math`, `random as _random`, `scene_common as sc`
- public functions: `tactile_mtl`, `_norm_front`, `build_bollard_v51`,
  `bollard_v51_aabbs`, `bollard_line`, `det_rng`, `jit_yaw`, `jit_pos`,
  `jit_scalar`, `jit_tint`
- module constants: `BOLLARD_V51`, `_BODY_RGB`, `_BAND_RGB`, `_TACT_RGB`,
  `_TACT_TILE_M`, `_TACT_ROUGH` — every numeric value byte-identical
  (verified via the AST hash in §2 and the value-expression comparison above)

---

## 6. Proof — runtime string literals untouched

A tokenizer pass classifies every Hangul-bearing token as a `COMMENT`, a
docstring (a leading string `Expr` of a module/class/function), or a plain
string literal. Docstrings and comments must reach zero; plain literals must
not move.

| file | ko comments | ko docstrings | ko string literals |
|------|------------:|--------------:|-------------------:|
| `building_kit.py`                | 187 → **0** | 38 → **0** | 54 → **54** |
| `scenes/batch1/batch1_common.py` |  24 → **0** | 10 → **0** |  0 → **0** |
| `scripts/imgstats.py`            |  27 → **0** |  7 → **0** |  9 → **9** |
| `scripts/make_compare_sheet.py`  |   4 → **0** |  1 → **0** | 44 → **44** |
| `scripts/make_hq_sheet.py`       |   0 → **0** |  1 → **0** | 46 → **46** |
| `scripts/make_overview.py`       |   2 → **0** |  1 → **0** | 23 → **23** |
| `scripts/rtx_probe.py`           |   2 → **0** |  1 → **0** |  3 → **3** |
| `scripts/spike_realism.py`       |  44 → **0** |  6 → **0** |  9 → **9** |
| `assets/signs/gen_signs.py`      |   4 → **0** |  1 → **0** |  5 → **5** |
| **total** | **294 → 0** | **65 → 0** | **193 → 193** |

**RESULT: PASS — 0 Korean in comments/docstrings, all 193 Korean runtime
literals preserved.**

Categories of preserved Korean literal, by file:

- `building_kit.py` (54) — every `selfcheck()` `print()` header and `chk()`
  check name, the drift report line, the `_scan_scenes()` measurement report,
  and the `AssertionError("자기검사 실패 …")` message.
- `scripts/imgstats.py` (9) — `[에러]`/`[참고]` prefixes, the mode line, the
  group-mean and median headers, the T1 gate verdict lines, and the
  `통과`/`미달` verdict words inside `gate_verdict()`.
- `scripts/make_compare_sheet.py` (44), `make_hq_sheet.py` (46),
  `make_overview.py` (23) — scene display names, sheet titles and subtitles,
  the `합격` badge text, `(렌더 없음)`, `전`/`후` column labels, `[시트]` and
  `[경고]` console output.
- `scripts/spike_realism.py` (9) — `[랩]`, `[캡처]`, `[노트]`, `[예산]`,
  `[결과]` console prefixes and their messages.
- `scripts/rtx_probe.py` (3) — the two numbered section headers printed to the
  console and the `[결과]` line.
- `assets/signs/gen_signs.py` (5) — the sign face texts themselves
  (`추락주의`, `계단주의`, `출구  →`, `안내`, `진입금지`), which are drawn
  into the PNG output.

---

## 7. Translation conventions applied

- **Citation tags** translated in place, comments only:
  `[실측]`→`[measured]`, `[추정]`→`[estimated]`, `[지식]`→`[knowledge]`,
  `[근거없음]`→`[no source]`, `[법령]`→`[statute]`, `법정`→`statutory`,
  `[한계 명시]`→`[limitation stated]`, `[추정·유도]`→`[estimated, derived]`,
  `[W2-C · B7 결재 …]`→`[W2-C · B7 approved …]`.
- **Section and document references kept verbatim**: `§3.2`, `ZZ §10.5`,
  `v5.1 §4`, `Docs/surveys/korean_urban_backdrop.md`, `judge_v*_rt*.md`, etc.
- **Statute names rendered in English** with the article number preserved:
  Building Act Enforcement Decree §119, §86(1), §40; Parking Lot Act
  Enforcement Rule §6; Outdoor Advertisements Act Enforcement Decree §15;
  Housing Construction Standards §14-2, §16; Seoul Outdoor Advertisements
  Ordinance. Circled numerals in article citations became plain parenthesised
  form (`①9` → `(1)9`) since they are ASCII-safe and unambiguous.
- **Technical terms kept**: piloti, parapet, penthouse, plinth, curtain wall,
  mullion, triplanar, catmullClark, crease, grazing, LOD, tier, prim,
  backdrop, split-face, bollard, tactile paving.
- **Numbered list markers** `①②③` inside comments became `(1)(2)(3)` for the
  same ASCII-safety reason; where they label printed output they were left
  alone (they are inside string literals).
- **Line-comment placement preserved** — every trailing `# …` stayed on its
  original statement line. Three comments I wrote exceeded the files' existing
  maximum line width and were wrapped onto a continuation comment line
  (`building_kit.py` `PILOTI_PITCH`, `batch1_common.py` `_BAND_RGB`/`_TACT_RGB`);
  post-edit maximum line lengths are at or below the pre-edit maxima in every
  file.
- Non-ASCII typography already used in the codebase (em dash `—`, `§`) was
  retained; mathematical symbols that read poorly in English prose were
  normalised (`±`→`+-`, `≤`→`<=`, `→`→`->`, `×`→`x`, `Δ`→`delta`, `°`→`deg`)
  inside comments only.

---

## 8. Scope confirmation

Files modified by this task, and only these:

```
 assets/signs/gen_signs.py      |   15 +-
 building_kit.py                | 1141 ++++++++++++++++++++-----------------
 scenes/batch1/batch1_common.py |  172 +++---
 scripts/imgstats.py            |  136 +++--
 scripts/make_compare_sheet.py  |   28 +-
 scripts/make_hq_sheet.py       |    2 +-
 scripts/make_overview.py       |    7 +-
 scripts/rtx_probe.py           |   33 +-
 scripts/spike_realism.py       |  189 ++++---
 9 files changed, 979 insertions(+), 744 deletions(-)
```

`facade_kit.py`, `ground_kit.py`, `infra_kit.py`, `scene_common.py` and all
`scenes/main/*` and `scenes/batch1/scene*.py` files also appear modified in
`git status` — those are **other agents' in-flight work on the same branch**
and were not read from, written to, or otherwise involved here.

No commit was made. The supervisor commits.
