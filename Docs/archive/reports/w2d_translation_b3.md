# W2-D — Comment/docstring translation, pass 3 (all 33 scene files)

Date 2026-07-30 · branch `feat/realism-v1` · **no commit** (supervisor commits)

Scope, exactly as assigned: every `.py` under `scenes/main/` and `scenes/batch1/`
that is a scene file — 21 main + 12 batch1 = **33 files**. `batch1_common.py` was
already done in pass 2 and was not touched; neither was any kit module, script,
doc or asset.

Korean **comments and docstrings** translated to concise English. **No code
changed.** **No runtime string literal touched** — all 1,579 Korean string
literals (scene names, judgment text, `print()` output, checklist banners, sign
face texts) are byte-identical.

---

## 0. Headline

| obligation | result |
|---|---|
| items translated | **6,508** (6,144 comments + 364 docstrings) |
| per-file AST SHA-256 (comments+docstrings stripped) pre = post | **33 / 33 identical** |
| `py_compile` | **33 / 33 OK** (exit 0) |
| `python3 ground_kit.py` | **exit 0**, stdout **byte-identical** to the pre-translation run |
| `scripts/geom_invariance_check.py` | **exit 0** · R-4 **33/33** · R-6 **33/33** |
| per-scene prim counts + prim hashes vs pre-translation run | **33 / 33 IDENTICAL** (full report byte-identical) |
| Korean residue in comments / docstrings | **0 / 0** (wide Unicode sweep, 8 Hangul blocks) |
| Korean string-literal multiset per file, pre vs post | **33 / 33 unchanged** |
| numeric tokens preserved | 15,088 measured; **0 coordinate/dimension values lost** |

`git diff --shortstat scenes/` → `33 files changed, 8999 insertions(+), 8753 deletions(-)`.

---

## 1. Method

Every replacement was made **at the exact source span of a single token**, never by
rewriting a file. The pipeline:

1. `tokenize` locates every `COMMENT` token; `ast` locates every docstring (the
   leading `Expr`/`Constant` of a `Module`/`ClassDef`/`FunctionDef`). Tokens
   containing Hangul become the work list — 6,508 items with their
   `(line, col, end_line, end_col)` spans.
2. Each item is translated, then spliced back **bottom-up** at its recorded span,
   after re-reading the current slice and asserting it still equals the recorded
   original. A mismatch aborts the whole file.
3. Before splicing, every replacement is validated: a comment replacement must
   start with `#`; a **trailing** comment replacement may not contain a newline
   (so trailing comments stay trailing); a docstring replacement must
   `ast.literal_eval` to a `str` **and** tokenize to exactly one `STRING` token
   (so a runaway quote cannot smuggle in code); and no replacement may still
   contain Hangul.
4. Coverage is enforced: if any Hangul item of a touched file is missing from the
   patch map, the apply refuses outright.

Because only comment/docstring token spans are ever written, no non-docstring
string literal is reachable by the tool **by construction**.

Comment replacements were required to be **single-line**, so every comment is a
strict 1:1 line substitution and no line of code moved. All line-count drift
(+246 lines total) comes from docstrings, where English prose needed more lines
than the Korean it replaced.

### A byte/char bug worth recording

`ast` reports `col_offset` as a **UTF-8 byte** offset while `tokenize` and Python
string slicing use **character** offsets. On lines containing Hangul these differ.
The first version of the extractor compared the two directly and therefore
mis-classified 286 single-line Korean docstrings as ordinary string literals — it
would have skipped them and inflated the "literals to preserve" count. This was
found and fixed **before any baseline was taken**; all figures in this report come
from the corrected tooling.

---

## 2. Proof — AST equality (the formal check)

Method: `ast.parse` → strip the leading string-constant `Expr` from every
`Module`/`FunctionDef`/`AsyncFunctionDef`/`ClassDef` body → `ast.dump(...,
annotate_fields=True, include_attributes=False)` → SHA-256. Comments never reach
the AST, and docstrings are stripped, so this digest is invariant under any
comment-only or docstring-only edit and changes under any code edit — including a
changed literal, a changed default, or reordered statements.

**Result: 33/33 identical.** Table B below.

**Independent cross-check.** The working tree was clean when this task started
(`git status` showed only one untracked doc), so `HEAD` holds the pre-translation
content of all 33 files. The 33 baseline digests were recomputed from
`git show HEAD:<file>` blobs and **all 33 match** the digests taken from the
working tree. The post-translation digests equal those same values, which proves
the diff against `HEAD` is comment/docstring-only for all 33 files.

**Concurrent commit — checked, no interaction.** `HEAD` moved during this task from
`02b3310` to `acfd4d4` ("점자 돌기 Ø25→35mm 재결재 … + 연대 정합성 조사 v1", another
session). That commit touches exactly two files:

```
Docs/surveys/era_consistency_survey_v1.md   (new)
assets/scene01/download_scene01_assets.py
```

**No scene file and no kit module** — in particular not `ground_kit.py`, so the
byte-identical self-check output in §4 is not an artefact of a stale binary. The
cross-check above was re-run against the *new* `HEAD` after that commit landed and
still reports **0 / 33 mismatches**, i.e. this pass and that commit are disjoint and
neither overwrote the other.

---

## 3. Proof — `py_compile`

```
python3 -m py_compile $(cat filelist.txt)      # 33 scene files
```

**PY_COMPILE: 33/33 OK** (exit 0, no output).

---

## 4. Proof — `python3 ground_kit.py`

```
GK_POST_EXIT=0
ground_kit 자기검산 — 전 항목 통과
```

`diff` of the pre-translation and post-translation stdout capture is **empty** —
the full self-check output is byte-identical, including its Korean runtime
strings. `[evidence — scratchpad gk_pre.txt vs gk_post.txt]`

---

## 5. Proof — `scripts/geom_invariance_check.py`

Run on the live tree after all 33 files were edited. No scene file or kit module had
any other editor during this pass (§2 confirms the one concurrent commit was
disjoint), so unlike pass 1 no frozen snapshot was needed.

```
GEOM_POST_EXIT=0
[R-5] 스캔 40 파일 · 허용 3 행(호환 심) · 위반 0 건 → ✔ PASS
[R-4] MTL 0/1 해시 일치 33/33  ✔ PASS
[R-6] V1=1 3자 일치   33/33  ✔ PASS
```

**Prim-hash invariance — the comment-only proof.** The pre-translation run of the
same checker was captured before any edit. `diff geom_pre.txt geom_post.txt` is
**empty**: the entire report is byte-identical, which means all 33 scene rows —
prim count and all three hash columns (`mtl0`, `mtl1`, `v1`) — are unchanged.

```
$ diff geom_pre.txt geom_post.txt        # empty
$ diff <(grep -E '^scene' geom_pre.txt) <(grep -E '^scene' geom_post.txt)
33/33 SCENE ROWS IDENTICAL
```

The checker was then run a **third** time, after the last content edit in this task
(the `sceneC1` unit fix in §7), so the proof covers the exact tree being handed over:

```
GEOM_FINAL_EXIT=0
diff geom_pre.txt geom_final.txt  → empty        # byte-identical, R-4 33/33, R-6 33/33
```

Sample of the unchanged rows (count, mtl0, mtl1, v1):

```
scene17       972  03af0404  03af0404  03af0404  ✔
scene18      1957  da1139ac  da1139ac  da1139ac  ✔
scene19       288  e4d47876  e4d47876  e4d47876  ✔
sceneC2      3929  036c74f7  036c74f7  036c74f7  ✔
sceneN4      1241  25724f2a  25724f2a  25724f2a  ✔
```

Note that pass 1 could not achieve this: it was running against a tree that other
agents were editing, and had to fall back to a frozen two-arm snapshot. This pass
has the stronger result — identical hashes on the **live** tree.

---

## 6. Proof — Korean residue and preserved literals

A wide sweep classifies every Hangul-bearing token as `COMMENT`, docstring, or
plain string literal. The sweep covers **eight** Unicode blocks, not just the
syllable range: Hangul Jamo (U+1100–11FF), Compatibility Jamo (U+3130–318F),
**Parenthesised Hangul (U+3200–321E)**, **Circled Hangul (U+3260–327E)**, Jamo
Extended-A/B, Syllables (U+AC00–D7AF) and Halfwidth Hangul (U+FFA0–FFDC).

The circled/parenthesised blocks matter: `㉠㉡㉢` (U+3260…) are Hangul letters used
as enumerators throughout these files, and they fall **outside** the syllable range
that the apply-time validator tests. They were translated to `(a)(b)(c)` /
`(i)(ii)(iii)` and the wide sweep confirms none survive.

```
Korean residue in COMMENTS   : 0
Korean residue in DOCSTRINGS : 0
Korean STRING LITERALS (preserved, expected non-zero): 1579
```

Per-file Korean string-literal multisets (the sorted list of literal token texts,
not just the count) are compared pre vs post: **33/33 unchanged**. Table A.

---

## 7. Proof — numeric fidelity

Comment prose can be rewritten freely, but a coordinate or dimension must never
move. For each file the multiset of numeric tokens across all of its translated
items is compared before and after.

| measure | value |
|---|---|
| numeric tokens in the Korean source items | **15,088** |
| tokens absent after translation | 137 |
| tokens introduced by translation | 460 |
| **of the absent tokens: decimal or 2+ digit (i.e. capable of being a real measurement)** | **3** |

The 460 introduced tokens are overwhelmingly the enumerator conversion
(`①②③` → `(1)(2)(3)`) plus counts that Korean expressed with a counter word.

All **3** candidate losses were inspected individually; none was a lost value:

| file | Korean | English as written | verdict |
|---|---|---|---|
| `sceneC1_snow_stairs.py` | `적설 0.05 m` | *(was)* `5 cm of snow` | unit conversion — **corrected back to `Snow depth 0.05 m`** so it matches the `PARAMS` value literally |
| `sceneC2_leaf_stairs.py` | `10월 말~11월 중순` | `late Oct ~ mid Nov` | month names, not measurements — kept |

The `scene02` v8 design-spec docstring (§8) was checked on its own and is exact:
**225 numeric tokens pre, 225 post, none lost, none added.**

---

## 8. SPECIAL CARE — `scene02_underpass.py` module docstring

This docstring carries the **v8 landing design spec** that W4 will implement. It is
load-bearing documentation, so it was translated by hand with two extra rules.

**The unimplemented-warning block keeps its full semantics** — that it is a
proposal, that it is *not* in the code, the date, and the instruction to delete the
block once implemented. The `⚠️` glyph and both `====` rulers are preserved:

```
===========================================================================
⚠️ What follows is a **DESIGN PROPOSAL AND IS NOT YET REFLECTED IN THE CODE**
   (2026-07-29). The session that was writing it was cut off by a usage limit.
   The coordinate check is finished, so the next session can implement it
   exactly as tabulated here. **Delete this warning block once implemented.**
===========================================================================
```

**Inside the tables and measurement lines the original mathematical typography is
preserved byte-for-byte** — `− ± × ≤ … ⇒ → ← ² · °` and the `┌ │ └` box glyphs —
and only the label prose is translated, re-padded so the columns still line up:

```
[Walking-continuity z ladder]  enter → descend → landing → descend → exit (every step ≤ 0.160)
  ┌ #  section            x range          top z       step / verdict
  │ 0  ground sidewalk     ≤ 0.00          +0.000      flat (opening front edge = drop 3.200)
  │ 3  flight0 step 10  2.88 … 3.20        −1.600      0.160 × 5   ← end of flight0
  │ 4  **landing**      3.20 … 4.40        −1.600      0.000 (flat 1.200)
  └ 9  tunnel floor     8.20 … 12.20       −3.200      0.000 (flush)
```

Three digits had initially been absorbed into English words (`1열` → "one line",
`1회` → "once", `불연속 0` → "Zero discontinuity"). Because this block is a spec,
they were restored as literal digits (`**1 line at y = 0.000**`, `broken exactly
1 time`, `Discontinuity 0:`), which is what brings the count to an exact 225 = 225.

The same treatment was applied to every other scene docstring carrying a
coordinate table, z-ladder or camera-occlusion check (`scene03`, `scene06`,
`scene07`, `scene08`, `scene10`, `scene11`, `scene12`, `sceneD1`, `sceneN4`, …):
prose translated, numbers and box glyphs byte-exact, columns re-padded.

---

## 9. Translation conventions

Carried forward from passes 1 and 2 and issued to every worker as a single binding
style guide, so the 33 files read as one document set.

* **Citation tags**, comments only: `[실측]`→`[measured]`, `[추정]`→`[estimated]`,
  `[계산]`→`[computed]`, `[확인]`→`[verified]`, `[통계]`→`[statistic]`,
  `[법령]`→`[statute]`, `[지식]`→`[knowledge]`, `[근거 없음]`→`[no source]`,
  `[한계 명시]`→`[limitation stated]`, `[신규]`→`[new]`, `[선택]`→`[optional]`,
  `[감사vN]`→`[audit vN]`, `[v5.2 사용자]`→`[v5.2 user]`, `결재`→`approved`.
* **Statutes** rendered in English with the article number preserved: Fire Safety /
  Evacuation Rule §15(1)1, §15(3); Building Act Enforcement Decree §119; Parking
  Lot Act Enforcement Rule §6(1)5(c); Enforcement Rule of the Act on Promotion of
  Mobility Convenience for the Mobility Impaired, Tables 1 and 2; Occupational
  Safety and Health Standards Rules §43.
* **Section and document references kept verbatim**: `§5.1`, `§12.4`,
  `Docs/reports/stair_compliance_v1.md`, `judge_v*_rt*.md`, `fixlog_I5`.
* **Enumerators**: `①②③`→`(1)(2)(3)`, `ⓐⓑ`→`(a)(b)`, `㉠㉡㉢`→`(a)(b)(c)` (or
  `(i)(ii)(iii)` where `(a)` was already taken in the same block), `★`→`*`.
* **Math symbols normalised in comment prose**: `±`→`+-`, `≤/≥`→`<=`/`>=`, `→`→`->`,
  `×`→`x`, `≈`→`~`, `Δ`→`delta`, `°`→`deg`. **Docstrings keep the original glyphs**,
  because their coordinate tables and z-ladders depend on the column widths.
  U+2212 `−` inside numbers is preserved everywhere.
* **Rulers** (`# ─── … ───`, `# ═══ … ═══`) were re-padded to the original
  **display** width — Hangul is double-width, so an equal glyph count would have
  shifted the closing column.
* **Line-comment placement preserved** — every trailing `# …` is still trailing on
  its original statement line, enforced by the validator rather than by review.

### Domain glossary settled across all 33 files

낙차 → drop · 단차 → step height · 계단참 → landing · 계단코 → nosing ·
손잡이 → handrail · 중간난간 → mid rail · 난간 → railing/guardrail ·
점자블록 → tactile paving · 점형블록 → dot tactile paving · 은닉 → hidden ·
차폐 → occlusion · 자기폐색 → self-occlusion · 개구 → opening · 피트 → pit ·
옹벽 → retaining wall · 파라펫 → parapet · 드레싱 → dressing · 산포 → scatter ·
지터 → jitter · 프림 → prim · 검산 → numeric check · 감사 → audit ·
미장센 → mise-en-scene · 보행축 → walk axis · 대조군/쌍둥이 → control/twin ·
소거 실험 → ablation · 축정렬 → axis-aligned · 사교/사선 → oblique/diagonal ·
마사토 → decomposed granite · 논슬립 → anti-slip · 초석 → plinth ·
둔치 → floodplain (scene12) / beach (scene03, matching `build_beach`) ·
호안 → revetment · 사석 → riprap · 억새 → silver grass · 계단정 → stair well ·
연단 → platform edge (sceneD4) / dock edge (sceneD1) · 소단 → berm ·
갓돌 → coping · 측구 → roadside channel · 개거 → open channel · 헌치 → haunch ·
백화 → efflorescence · 먹줄 → ink snap line · 달동네 → hillside slum.

### Known terminology variance (inherited or deliberate)

* **판정** is rendered `judgment` in some files and `ruling` in others. Both were
  chosen to match pre-existing English already in that same file (`scene01` and
  `scene12` already said "ruling"). Not unified, because unifying would have made
  each file inconsistent with its own untranslated English.
* **자전거도로** is `bike road` in `scene17`, matching the pre-existing English on
  line 117; line 116 of the same file (untouched, no Hangul) says `bikeway`. That
  inconsistency is inherited, not introduced.
* A few pre-existing all-English comments still carry `★` (`scene14` lines 84/92,
  `scene17`, `scene18` lines 113–128, `scene21`). They contain no Hangul, so they
  were out of scope and were left alone; their translated neighbours use `*`.
* Comments that cross-reference a Korean `print()` label are now in English while
  the label itself is still a Korean literal (e.g. `[v6 태양]` → `[v6 sun]` beside
  a Korean printed header). This is unavoidable while literals stay Korean, and is
  flagged here in case a later pass translates the runtime strings too.
* `"완전 적정"` in a `scene02` comment quotes a `note=` value that lives in
  `ground_kit.py`. The comment now says `"fully sound"`; the `ground_kit` literal is
  untouched, so the two no longer match verbatim.

---

## 10. Files touched and line drift

Only the 33 assigned scene files. `batch1_common.py`, every kit module, every
script, every doc and every asset is untouched by this task.

| file | lines pre | lines post | drift | diff |
|---|---:|---:|---:|---|
| `scenes/batch1/sceneC1_snow_stairs.py` | 1038 | 1039 | +1 | +243 −242 |
| `scenes/batch1/sceneC2_leaf_stairs.py` | 1086 | 1090 | +4 | +248 −244 |
| `scenes/batch1/sceneC4_wet_stairs.py` | 1118 | 1126 | +8 | +278 −270 |
| `scenes/batch1/sceneD1_loading_dock.py` | 1165 | 1165 | +0 | +244 −244 |
| `scenes/batch1/sceneD2_floor_opening.py` | 1174 | 1174 | +0 | +258 −258 |
| `scenes/batch1/sceneD3_drainage_channel.py` | 1181 | 1198 | +17 | +265 −248 |
| `scenes/batch1/sceneD4_subway_platform.py` | 920 | 924 | +4 | +207 −203 |
| `scenes/batch1/sceneN1_shadow_band.py` | 969 | 984 | +15 | +266 −251 |
| `scenes/batch1/sceneN2_asphalt_patch.py` | 1025 | 1033 | +8 | +207 −199 |
| `scenes/batch1/sceneN3_trompe_loeil.py` | 1210 | 1215 | +5 | +249 −244 |
| `scenes/batch1/sceneN4_downhill_ramp.py` | 1108 | 1111 | +3 | +254 −251 |
| `scenes/batch1/sceneN5_flush_grating.py` | 1088 | 1088 | +0 | +186 −186 |
| `scenes/main/scene01_campus_stairs.py` | 1222 | 1236 | +14 | +271 −257 |
| `scenes/main/scene02_underpass.py` | 1067 | 1072 | +5 | +249 −244 |
| `scenes/main/scene03_riverbank.py` | 1336 | 1339 | +3 | +344 −341 |
| `scenes/main/scene04_parktrail.py` | 1090 | 1096 | +6 | +302 −296 |
| `scenes/main/scene05_amphitheater.py` | 1541 | 1559 | +18 | +484 −466 |
| `scenes/main/scene06_overpass_spiral.py` | 1668 | 1679 | +11 | +356 −345 |
| `scenes/main/scene07_temple_stone_path.py` | 1469 | 1475 | +6 | +324 −318 |
| `scenes/main/scene08_sunken_plaza.py` | 1408 | 1411 | +3 | +253 −250 |
| `scenes/main/scene09_ghat_riverfront.py` | 1628 | 1631 | +3 | +519 −516 |
| `scenes/main/scene10_park_deck_switchback.py` | 1458 | 1480 | +22 | +339 −317 |
| `scenes/main/scene11_footbridge_stairs.py` | 1546 | 1560 | +14 | +302 −288 |
| `scenes/main/scene12_riverside_deck.py` | 1592 | 1635 | +43 | +372 −329 |
| `scenes/main/scene13_apartment_parking_entry.py` | 1282 | 1288 | +6 | +236 −230 |
| `scenes/main/scene14_grandstair_illusion.py` | 1082 | 1084 | +2 | +271 −269 |
| `scenes/main/scene15_alley_labyrinth.py` | 914 | 920 | +6 | +246 −240 |
| `scenes/main/scene16_canopy_shadow.py` | 890 | 892 | +2 | +137 −135 |
| `scenes/main/scene17_ramp_pair_hangang.py` | 1292 | 1299 | +7 | +268 −261 |
| `scenes/main/scene18_wavy_artstair.py` | 1188 | 1188 | +0 | +286 −286 |
| `scenes/main/scene19_fan_winder.py` | 1150 | 1153 | +3 | +247 −244 |
| `scenes/main/scene20_diagonal_oblique.py` | 690 | 694 | +4 | +134 −130 |
| `scenes/main/scene21_monumental_selfocclude.py` | 780 | 783 | +3 | +154 −151 |
| **total** | **39375** | **39621** | **+246** | **+8999 −8753** |

Every comment was a strict single-line 1:1 substitution, so all drift is docstring
prose. The AST equality in §2 confirms no statement moved.

---

## 11. Scope confirmation

```
 M scenes/batch1/sceneC1_snow_stairs.py
 M scenes/batch1/sceneC2_leaf_stairs.py
 M scenes/batch1/sceneC4_wet_stairs.py
 M scenes/batch1/sceneD1_loading_dock.py
 M scenes/batch1/sceneD2_floor_opening.py
 M scenes/batch1/sceneD3_drainage_channel.py
 M scenes/batch1/sceneD4_subway_platform.py
 M scenes/batch1/sceneN1_shadow_band.py
 M scenes/batch1/sceneN2_asphalt_patch.py
 M scenes/batch1/sceneN3_trompe_loeil.py
 M scenes/batch1/sceneN4_downhill_ramp.py
 M scenes/batch1/sceneN5_flush_grating.py
 M scenes/main/scene01_campus_stairs.py
 M scenes/main/scene02_underpass.py
 M scenes/main/scene03_riverbank.py
 M scenes/main/scene04_parktrail.py
 M scenes/main/scene05_amphitheater.py
 M scenes/main/scene06_overpass_spiral.py
 M scenes/main/scene07_temple_stone_path.py
 M scenes/main/scene08_sunken_plaza.py
 M scenes/main/scene09_ghat_riverfront.py
 M scenes/main/scene10_park_deck_switchback.py
 M scenes/main/scene11_footbridge_stairs.py
 M scenes/main/scene12_riverside_deck.py
 M scenes/main/scene13_apartment_parking_entry.py
 M scenes/main/scene14_grandstair_illusion.py
 M scenes/main/scene15_alley_labyrinth.py
 M scenes/main/scene16_canopy_shadow.py
 M scenes/main/scene17_ramp_pair_hangang.py
 M scenes/main/scene18_wavy_artstair.py
 M scenes/main/scene19_fan_winder.py
 M scenes/main/scene20_diagonal_oblique.py
 M scenes/main/scene21_monumental_selfocclude.py
```

The only untracked file besides this report is nothing of this task's making — the
listing above was captured mid-task, and `Docs/surveys/era_consistency_survey_v1.md`
has since been committed by the concurrent session described in §2. The final state
is **33 modified scene files + this report**, nothing else:

```
 M scenes/batch1/sceneC1_snow_stairs.py … (33 scene files)
?? Docs/reports/w2d_translation_b3.md
```

**No commit was made — the supervisor commits.**


---

## Table A - per-file item counts and residue census

| file | comments | docstrings | items | KO comments after | KO docstrings after | KO string literals (pre = post) |
|---|---:|---:|---:|---:|---:|---:|
| `scenes/batch1/sceneC1_snow_stairs.py` | 202 | 9 | 211 | 0 | 0 | 17 = 17 OK |
| `scenes/batch1/sceneC2_leaf_stairs.py` | 201 | 6 | 207 | 0 | 0 | 28 = 28 OK |
| `scenes/batch1/sceneC4_wet_stairs.py` | 216 | 12 | 228 | 0 | 0 | 21 = 21 OK |
| `scenes/batch1/sceneD1_loading_dock.py` | 182 | 8 | 190 | 0 | 0 | 31 = 31 OK |
| `scenes/batch1/sceneD2_floor_opening.py` | 194 | 7 | 201 | 0 | 0 | 31 = 31 OK |
| `scenes/batch1/sceneD3_drainage_channel.py` | 159 | 10 | 169 | 0 | 0 | 47 = 47 OK |
| `scenes/batch1/sceneD4_subway_platform.py` | 119 | 8 | 127 | 0 | 0 | 26 = 26 OK |
| `scenes/batch1/sceneN1_shadow_band.py` | 189 | 12 | 201 | 0 | 0 | 38 = 38 OK |
| `scenes/batch1/sceneN2_asphalt_patch.py` | 154 | 12 | 166 | 0 | 0 | 34 = 34 OK |
| `scenes/batch1/sceneN3_trompe_loeil.py` | 165 | 11 | 176 | 0 | 0 | 58 = 58 OK |
| `scenes/batch1/sceneN4_downhill_ramp.py` | 196 | 9 | 205 | 0 | 0 | 61 = 61 OK |
| `scenes/batch1/sceneN5_flush_grating.py` | 144 | 11 | 155 | 0 | 0 | 42 = 42 OK |
| `scenes/main/scene01_campus_stairs.py` | 195 | 17 | 212 | 0 | 0 | 12 = 12 OK |
| `scenes/main/scene02_underpass.py` | 164 | 6 | 170 | 0 | 0 | 14 = 14 OK |
| `scenes/main/scene03_riverbank.py` | 229 | 20 | 249 | 0 | 0 | 17 = 17 OK |
| `scenes/main/scene04_parktrail.py` | 227 | 13 | 240 | 0 | 0 | 20 = 20 OK |
| `scenes/main/scene05_amphitheater.py` | 356 | 16 | 372 | 0 | 0 | 56 = 56 OK |
| `scenes/main/scene06_overpass_spiral.py` | 219 | 20 | 239 | 0 | 0 | 119 = 119 OK |
| `scenes/main/scene07_temple_stone_path.py` | 168 | 19 | 187 | 0 | 0 | 88 = 88 OK |
| `scenes/main/scene08_sunken_plaza.py` | 156 | 14 | 170 | 0 | 0 | 78 = 78 OK |
| `scenes/main/scene09_ghat_riverfront.py` | 311 | 23 | 334 | 0 | 0 | 80 = 80 OK |
| `scenes/main/scene10_park_deck_switchback.py` | 182 | 12 | 194 | 0 | 0 | 105 = 105 OK |
| `scenes/main/scene11_footbridge_stairs.py` | 191 | 12 | 203 | 0 | 0 | 88 = 88 OK |
| `scenes/main/scene12_riverside_deck.py` | 203 | 16 | 219 | 0 | 0 | 139 = 139 OK |
| `scenes/main/scene13_apartment_parking_entry.py` | 155 | 7 | 162 | 0 | 0 | 69 = 69 OK |
| `scenes/main/scene14_grandstair_illusion.py` | 154 | 12 | 166 | 0 | 0 | 29 = 29 OK |
| `scenes/main/scene15_alley_labyrinth.py` | 201 | 5 | 206 | 0 | 0 | 17 = 17 OK |
| `scenes/main/scene16_canopy_shadow.py` | 108 | 6 | 114 | 0 | 0 | 17 = 17 OK |
| `scenes/main/scene17_ramp_pair_hangang.py` | 189 | 6 | 195 | 0 | 0 | 88 = 88 OK |
| `scenes/main/scene18_wavy_artstair.py` | 213 | 9 | 222 | 0 | 0 | 32 = 32 OK |
| `scenes/main/scene19_fan_winder.py` | 175 | 9 | 184 | 0 | 0 | 37 = 37 OK |
| `scenes/main/scene20_diagonal_oblique.py` | 103 | 4 | 107 | 0 | 0 | 12 = 12 OK |
| `scenes/main/scene21_monumental_selfocclude.py` | 124 | 3 | 127 | 0 | 0 | 28 = 28 OK |
| **total (33 files)** | **6144** | **364** | **6508** | **0** | **0** | **1579 = 1579** |


## Table B - AST SHA-256 (docstrings stripped), pre vs post

| file | AST SHA-256 (pre) | AST SHA-256 (post) | equal |
|---|---|---|:---:|
| `scenes/batch1/sceneC1_snow_stairs.py` | `1f712342be71b927…` | `1f712342be71b927…` | yes |
| `scenes/batch1/sceneC2_leaf_stairs.py` | `bee774dcfb659045…` | `bee774dcfb659045…` | yes |
| `scenes/batch1/sceneC4_wet_stairs.py` | `ee17bb587326c12f…` | `ee17bb587326c12f…` | yes |
| `scenes/batch1/sceneD1_loading_dock.py` | `c45b7c5117e998dd…` | `c45b7c5117e998dd…` | yes |
| `scenes/batch1/sceneD2_floor_opening.py` | `a5b36c5618c0b477…` | `a5b36c5618c0b477…` | yes |
| `scenes/batch1/sceneD3_drainage_channel.py` | `35489a7e0a7ac9e1…` | `35489a7e0a7ac9e1…` | yes |
| `scenes/batch1/sceneD4_subway_platform.py` | `a2519bb74177a670…` | `a2519bb74177a670…` | yes |
| `scenes/batch1/sceneN1_shadow_band.py` | `062c7388c02645e5…` | `062c7388c02645e5…` | yes |
| `scenes/batch1/sceneN2_asphalt_patch.py` | `3a8b04d6222e6cf5…` | `3a8b04d6222e6cf5…` | yes |
| `scenes/batch1/sceneN3_trompe_loeil.py` | `6dc53e455f9fec1f…` | `6dc53e455f9fec1f…` | yes |
| `scenes/batch1/sceneN4_downhill_ramp.py` | `0fcf3bc19a751edf…` | `0fcf3bc19a751edf…` | yes |
| `scenes/batch1/sceneN5_flush_grating.py` | `ed3428fb8fe0fba2…` | `ed3428fb8fe0fba2…` | yes |
| `scenes/main/scene01_campus_stairs.py` | `9a2db710a44c025b…` | `9a2db710a44c025b…` | yes |
| `scenes/main/scene02_underpass.py` | `efbb97814348b366…` | `efbb97814348b366…` | yes |
| `scenes/main/scene03_riverbank.py` | `c6d96f41060d1540…` | `c6d96f41060d1540…` | yes |
| `scenes/main/scene04_parktrail.py` | `fc5040b1cf379fa9…` | `fc5040b1cf379fa9…` | yes |
| `scenes/main/scene05_amphitheater.py` | `1ca5e9e116691ca6…` | `1ca5e9e116691ca6…` | yes |
| `scenes/main/scene06_overpass_spiral.py` | `ffec43507a615a24…` | `ffec43507a615a24…` | yes |
| `scenes/main/scene07_temple_stone_path.py` | `4beda0df6c35e2f3…` | `4beda0df6c35e2f3…` | yes |
| `scenes/main/scene08_sunken_plaza.py` | `4332bc1f668e1e9d…` | `4332bc1f668e1e9d…` | yes |
| `scenes/main/scene09_ghat_riverfront.py` | `3359f9e3f51d5c48…` | `3359f9e3f51d5c48…` | yes |
| `scenes/main/scene10_park_deck_switchback.py` | `053553d8e4dfbc05…` | `053553d8e4dfbc05…` | yes |
| `scenes/main/scene11_footbridge_stairs.py` | `729934fe6ea1a94e…` | `729934fe6ea1a94e…` | yes |
| `scenes/main/scene12_riverside_deck.py` | `cc4060da89288e14…` | `cc4060da89288e14…` | yes |
| `scenes/main/scene13_apartment_parking_entry.py` | `557fd95bc6beeb85…` | `557fd95bc6beeb85…` | yes |
| `scenes/main/scene14_grandstair_illusion.py` | `529a7bc6bf220880…` | `529a7bc6bf220880…` | yes |
| `scenes/main/scene15_alley_labyrinth.py` | `369c29f76b4d68fe…` | `369c29f76b4d68fe…` | yes |
| `scenes/main/scene16_canopy_shadow.py` | `671225675eb12c86…` | `671225675eb12c86…` | yes |
| `scenes/main/scene17_ramp_pair_hangang.py` | `9db586d5c9e33b72…` | `9db586d5c9e33b72…` | yes |
| `scenes/main/scene18_wavy_artstair.py` | `604ace76ec7af9de…` | `604ace76ec7af9de…` | yes |
| `scenes/main/scene19_fan_winder.py` | `28118bd995f33ba8…` | `28118bd995f33ba8…` | yes |
| `scenes/main/scene20_diagonal_oblique.py` | `83aafb24df3322ac…` | `83aafb24df3322ac…` | yes |
| `scenes/main/scene21_monumental_selfocclude.py` | `7b6ab99efe3692df…` | `7b6ab99efe3692df…` | yes |

**AST equality: 33/33 identical.**

Full post-translation digests:

```
1f712342be71b92792118c1306e441b5baec6b9229a9b1ee7bb0589e7776c595  scenes/batch1/sceneC1_snow_stairs.py
bee774dcfb6590455ed400bf347b645eaf9efaa78af780d3dafe9f68e19d81e1  scenes/batch1/sceneC2_leaf_stairs.py
ee17bb587326c12f642b4984f4927b1afc856db1d6ce394c3dd40d12317e2dbf  scenes/batch1/sceneC4_wet_stairs.py
c45b7c5117e998dde01f8a2454d9c5977263a3308f02ee2c7b21857072e1e159  scenes/batch1/sceneD1_loading_dock.py
a5b36c5618c0b477992477c14b44a8505600178dc79e4dd77d7dbca024a68871  scenes/batch1/sceneD2_floor_opening.py
35489a7e0a7ac9e17fef072c0b3420429ef14422d1605b96deb5e57d663fe8b3  scenes/batch1/sceneD3_drainage_channel.py
a2519bb74177a6707725784aabbe2570a7301e1a78c0a3b278b203165c7854ad  scenes/batch1/sceneD4_subway_platform.py
062c7388c02645e5976b21e5a1a196c6c54b300474d955a3a4b025b710d85690  scenes/batch1/sceneN1_shadow_band.py
3a8b04d6222e6cf57830f4bdcb5ff90d20a2b65fa6a2af25cae05d540b0309c1  scenes/batch1/sceneN2_asphalt_patch.py
6dc53e455f9fec1f06246448957d2ca94292b5528d245f493bd170607c8d7a72  scenes/batch1/sceneN3_trompe_loeil.py
0fcf3bc19a751edf1faf4aa8d9e8f7503275c6ea934198b4920a3aa49e6ba874  scenes/batch1/sceneN4_downhill_ramp.py
ed3428fb8fe0fba28874437587c45db5952bd25c353d7f91b6a30e7e2d7394e6  scenes/batch1/sceneN5_flush_grating.py
9a2db710a44c025b832991c08617f0541f63659c87d14599764b6807898218a0  scenes/main/scene01_campus_stairs.py
efbb97814348b36679555d9304607379b6c2387411af9ce592f801060fe9adea  scenes/main/scene02_underpass.py
c6d96f41060d15405dfe7363e4d7f6762d5741e50c007a8487a70101b4656e0f  scenes/main/scene03_riverbank.py
fc5040b1cf379fa9781b9bc5cba43b1cadcc51973ef8ec75b6cc98364b1286e9  scenes/main/scene04_parktrail.py
1ca5e9e116691ca61076db1d2f6a8983c71fce2c1a90a3b477a7f8d12f6ebe3c  scenes/main/scene05_amphitheater.py
ffec43507a615a249531295c17250e36c91e95e9aa27ad178be2edee9dd0d476  scenes/main/scene06_overpass_spiral.py
4beda0df6c35e2f30cc4a5742db615d76b17f56f42b1f2bbb1ec5352b3ec7491  scenes/main/scene07_temple_stone_path.py
4332bc1f668e1e9d60262ec9ac1950f5d49b3f0abcb2afbcf0675d414f7f0e54  scenes/main/scene08_sunken_plaza.py
3359f9e3f51d5c48a30153eaa1b033ace2d029bfa30bd801ee56a78568051fcc  scenes/main/scene09_ghat_riverfront.py
053553d8e4dfbc05fc1fc579b6c7b02282478fd0d684b6c30ff665b097843120  scenes/main/scene10_park_deck_switchback.py
729934fe6ea1a94eb248c74fb330d94d7fc5a1bd1f45b30152d226efc241ac90  scenes/main/scene11_footbridge_stairs.py
cc4060da89288e14bb4a806bd250e612d4a90588516e8af07a2caa03a6c4734a  scenes/main/scene12_riverside_deck.py
557fd95bc6beeb85c354ce9b90ffdf24e45a8f2d7d7de108f6493e5f25cdede2  scenes/main/scene13_apartment_parking_entry.py
529a7bc6bf2208806f665600956ca86b91b2cff9a166009b1b58f36775c25345  scenes/main/scene14_grandstair_illusion.py
369c29f76b4d68fe1d008bc8ce7c7dae796dc5f38eeb341ec1c83d33edf5875b  scenes/main/scene15_alley_labyrinth.py
671225675eb12c86d83ccaa006643adeeb113d29d8f74344d8734aca301d289b  scenes/main/scene16_canopy_shadow.py
9db586d5c9e33b72911778af8af4225f04ef85187fee02a58e3d87f15e3cc2b2  scenes/main/scene17_ramp_pair_hangang.py
604ace76ec7af9deb4958d72eaabb52b0d4d287c7d9e483dcf03e05836ab4c9e  scenes/main/scene18_wavy_artstair.py
28118bd995f33ba82b8cba0b2ced7ee1f760ee6636446479bfce27ccd1334d0b  scenes/main/scene19_fan_winder.py
83aafb24df3322ac4ddf08ab18db7eb81b94131b6c3d12ebd5235590280ed9fa  scenes/main/scene20_diagonal_oblique.py
7b6ab99efe3692df64eeed445d63bb151c5e5d41553ce6d03d1392a84eb1d498  scenes/main/scene21_monumental_selfocclude.py
```

