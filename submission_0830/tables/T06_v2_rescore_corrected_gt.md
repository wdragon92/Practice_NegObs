# T06 · Corrected-GT rescore — which published numbers MOVE and which are INVARIANT

<!-- LEDGER: experiments/v3_0823/V2_RESCORE.md — §0 gates :86-93, :97-109 · §1.1 denominators :122-132 -->
<!-- LEDGER: V2_RESCORE.md §1.2 corrected headline :157-172 · §1.3 closure :180-193 · §2 sigma :238-271 -->
<!-- LEDGER: V2_RESCORE.md §3 FA-matched survival :283-311 · §4 C/D :315-383 · §5 twin :387-444 -->
<!-- LEDGER: V2_RESCORE.md §6.2 move/invariant index :481-520 · §6.3 :524-605 -->
<!-- LEDGER: experiments/v3_0823/ACCOUNTING.md §4.4 (arithmetic correction: none 39, denominator 369) -->
<!-- Regeneration: code/rescore_v2corr.sh (GPU, 2m33s) + code/rescore_twin.sh (CPU) + code/rescore_tables.py -->

- **Corrected-GT status**: **this file IS the corrected-GT ledger.** Canonical manifest = 정본 B
  (`experiments/v3_0823/dataset_manifest_v2corr.json`).
- **Provenance**: `experiments/v3_0823/V2_RESCORE.md` · aggregate `eval_v2corr/rescore_tables.json`
- **Method**: same 9 checkpoints, same call as `run_queue_v2.sh` **except exactly two lines** —
  (1) `--manifest` → corrected, (2) `--tau-star <published fixed value>` (**re-fitting forbidden**;
  rgb .63/.71/.31 · depth .36/.21/.60 · b2 .45/.45/.45). τ_op = 0.5 frozen. GPU 2 min 33 s.

---

## 0. Integrity gates — 4/4 PASS

| gate | expectation | measured | verdict |
|---|---|---|---|
| G-1 pixel-invariant ⇒ prob-invariant | published `p_*` == rescored `p_*` | **9/9 runs, max abs(Δp) = 0.000e+00** (bit-identical) | ✅ |
| G-2 frame_id set identical | 816 ids exact | 9/9 True | ✅ |
| G-3 **H row invariant** | `frame_recall_H` · `cell_recall_H` == published | **9/9 completely identical**, 0 mismatches | ✅ |
| G-4 off arm invariant | `frame_fa_off` · `cell_fpr_off` == published | **9/9 Δ = 0.0000** | ✅ |

## 1. Denominators — old GT → corrected GT (test-core 816)

| item | old GT | **corrected GT (B)** | Δ |
|---|---|---|---|
| total / on / off | 816 / 408 / 408 | 816 / 408 / 408 | 0 |
| V | 180 | **219** | **+39** |
| E | 45 | 45 | 0 |
| **H (strict)** | **96** | **96** | **0** |
| H_weak | 6 | **9** | +3 |
| none_in_fov | 81 | **39** | **−42** |
| **headline recall denominator** | **327** | **369** | **+42** |
| conditioning-dropout disclosure | 81/408 = **19.9 %** | 39/408 = **9.6 %** | −10.3 pp |
| positive cells (816 frames) | 2,691 | **2,856** | +165 |

> ⚠ **Arithmetic correction on the record.** `ACCOUNTING.md` §4.2 (and D55) printed
> *"none 81→36 · denominator 327→372"*. That is **wrong** (219+45+96+9+36 = 405 ≠ 408). The correct
> values are **none 81→39 · denominator 327→369** (`ACCOUNTING.md` §4.4, D59 ⑦). **Do not cite 372.**

**Mechanism closure.** Rescoring on the *old* 327 frames reproduces the published values to 4
decimals ⇒ the G7 repair **changed no label on any pre-existing frame**. 100 % of every frame-recall
delta is the single mechanism of **42 frames entering**: `260820_boost_e_on` scene07 n=18 → V 18, and
`260820_boost_e2_on` scene07 n=24 → V 21 + H_weak 3. **Total 42 = V 39 + H_weak 3. Leaving frames = 0**
— old 327 is a **proper subset** of new 369. Cell-series metrics move for a different reason:
**+165 positive cells**.

## 2. Corrected headline table (τ_op = 0.5, denominators V 219 · E 45 · H 96 · Hw 9 · det 369 · off 408)

| model | cell_f1 | frame_det_rate | frame_recall_V | frame_recall_E | **frame_recall_H** | **frame_fa_off** | cell_fpr_off |
|---|---|---|---|---|---|---|---|
| rgb | 0.456 ± 0.117 | 0.717 ± 0.199 | **0.760 ± 0.203** | 0.556 ± 0.378 | **0.688 ± 0.141** | **0.359 ± 0.127** | 0.047 ± 0.016 |
| depth | 0.704 ± 0.030 | 0.729 ± 0.016 | **0.900 ± 0.041** | 0.600 ± 0.000 | **0.438 ± 0.031** | **0.042 ± 0.029** | 0.009 ± 0.008 |
| b2 | 0.367 ± 0.087 | 0.526 ± 0.149 | **0.735 ± 0.119** | 0.178 ± 0.267 | **0.229 ± 0.156** | **0.238 ± 0.143** | 0.035 ± 0.029 |

cell_recall / cell_precision, published → corrected:
rgb 0.385 ± 0.125 → **0.381 ± 0.133** / 0.566 ± 0.021 → **0.592 ± 0.039** ·
depth 0.652 ± 0.031 → **0.659 ± 0.029** / 0.705 ± 0.031 → **0.756 ± 0.031** ·
b2 0.276 ± 0.121 → **0.292 ± 0.131** / 0.527 ± 0.108 → **0.590 ± 0.115**

### 2.1 σ-exceeding moves — exactly TWO, both depth

1. **depth `cell_precision` 0.7049 → 0.7557, Δ = +0.0508, σ = 0.0307 ⇒ 1.65 σ.** Mechanism: 165 new
   positive cells appear on the scene07 boost frames, so cells depth was **already firing on** get
   reclassified **FP → TP**. *The model did not improve — the answer key moved toward the model.*
   This is a direct trace of the G7 defect. Same direction but buried in seed scatter:
   rgb +0.026 (0.63 σ), b2 +0.063 (0.55 σ).
2. **depth `frame_recall_H_weak` 0.0000 → 0.3333, σ = 0.0000. ⚠ CITATION FORBIDDEN.** σ = 0 because
   all 3 seeds share a value, **not** because it is precise; denominator is **9** (below the
   pre-registered floor of 10) and the column did not exist in the published table.

> **rgb is 판정 불가, not "unmoved".** rgb's σ is V 0.204 · det 0.199 · E 0.380 — large enough to
> swallow any delta (s43 is an outlier). "No σ exceedance in rgb" must be written as **"cannot be
> adjudicated with 3 seeds"**. Only depth (σ 0.017–0.042) has discriminating power.

> **V-drop arithmetic (rgb_s42, measured)**: old 180 frames 149/180 = 0.8278; new 39 frames
> 21/39 = 0.538; combined **170/219 = 0.7763**. The numerator grew, the denominator grew faster.

### 2.2 Exactly-zero cells — phrase them correctly

`frame_recall_H` · `frame_recall_E` · `frame_fa_off` · `cell_fpr_off` are Δ = 0.0000 in 9/9 runs.
Write **"verified unchanged by rescoring"**, never "would not change".

## 3. FA-matched survival — numbers **completely identical**

| matched FA | RGB H pub→corr | Depth H pub→corr | B2 H pub→corr | Δ(D−R) |
|---|---|---|---|---|
| 0.359 | 0.729 → **0.729** | 0.781 → **0.781** | 0.399 → **0.399** | +0.052 |
| 0.200 | 0.483 → **0.483** | 0.562 → **0.562** | 0.198 → **0.198** | +0.080 |
| 0.100 | 0.326 → **0.326** | 0.510 → **0.510** | 0.097 → **0.097** | +0.184 |
| 0.050 | 0.243 → **0.243** | 0.479 → **0.479** | 0.031 → **0.031** | +0.236 |

**Structural reason** (not luck): τ is drawn only from the **408 off-arm frames** (correction-
irrelevant) and the value read is recall on the **96 H frames** (correction-irrelevant). The
FA-matched table has **empty intersection** with the G7 defect surface. `SEED_TABLE.md:9` banner
needs **no edit**.

**But the V/E columns of the same table do move** (E invariant, V moves):
@.359 RGB V 0.809→**0.784** · Depth 0.994→**0.995** · B2 0.800→**0.823** ·
@.200 0.669→**0.632** · 0.983→**0.973** · 0.746→**0.760** ·
@.100 0.530→**0.496** · 0.956→**0.941** · 0.646→**0.647** ·
@.050 0.443→**0.399** · 0.939→**0.927** · 0.552→**0.556**.
Depth V ≥ RGB V holds at all four points and the **gap widens** (+0.185→+0.211 @.359; +0.496→+0.528 @.05).

## 4. Twin re-analysis — H invariant, V denominator changes

Same tool, `--tol 0.15`, `--n-boot 10000`. **kept 366 / excluded 42 identical before and after**
(the pose filter is GT-independent).

| model | Δ all pub→corr | **Δ H (n 96→96)** | Δ V (n **165→177**) |
|---|---|---|---|
| rgb | 0.314 → **0.333** | 0.285 → **0.285** | +0.010 ~ +0.032 |
| depth | 0.608 → **0.607** | 0.407 → **0.407** | −0.011 ~ −0.020 |
| b2 | 0.234 → **0.232** | 0.110 → **0.110** | −0.020 ~ −0.001 |

- **"Depth H 96/96 hazard-conditional" survives.** scene12's 48 H→V move is a **train** move;
  scene12 is not in the 7 test scenes. The H basis stays scene14 60 + scene15 36 = 96. Depth's
  off-arm twin firing rate is **0.000 on all 96 H pairs** before and after.
- **Twin V denominator is 177, not 219.** Of the 39 new V frames only **12 pairs** pass the pose
  filter; **27 are excluded on `ground_z` mismatch** (the toggle moves the camera's own ground).
  **Say 177 when citing the twin V tier.**
- **Δ H_weak citation forbidden** (denominator 6 → 9).
- Only `SEED_TABLE.md:21` `twin delta (all) rgb 0.314` → **0.333** actually needs editing.

## 5. THE MOVE / INVARIANT INDEX (this is what the draft author needs)

### 5.1 MUST be updated

| target | item | old → corrected |
|---|---|---|
| `SEED_TABLE.md:13` rgb | V · det · cell_f1 · cell_precision | 0.796→**0.760** · 0.730→**0.717** · 0.450→**0.456** · 0.566→**0.592** |
| `SEED_TABLE.md:14` depth | V · det · cell_f1 · cell_precision | 0.917→**0.900** · 0.716→**0.729** · 0.677→**0.704** · 0.705→**0.756** |
| `SEED_TABLE.md:15` b2 | V · det · cell_f1 · cell_precision | 0.730→**0.735** · 0.499→**0.526** · 0.340→**0.367** · 0.527→**0.590** |
| `SEED_TABLE.md:21-23` | §2 twin Δ (all) | 0.314/0.608/0.234 → **0.333 / 0.607 / 0.232** |
| `SEED_TABLE.md:31-39` | §3 per-seed V/det/cell columns | → `rescore_tables.json:runs.*.corrected` |
| `SEED_TABLE.md:60,69-71,93-95` | §4 **YOLO row V 0.150 ± 0.028** + prose | **UNMEASURED — needs corrected-GT rescore** |
| `SEED_TABLE.md:116-119` | §5 aux appendix V · cell_f1 · cell_precision | **UNMEASURED — `rgb_s42_aux` needs 1 rescore** |
| `F1_FA_MATCHED.md:5` | "V n=180" | **V n=219** |
| `F1_FA_MATCHED.md:79-81,87-92,38-73` | §3/§4 V columns, §2 per-seed V column | see §3 above |
| `F2_TWIN_CONDITIONAL.md:33,37-39,55-79` | "V tier n = 165 kept pairs" + V rows | **n = 177** |
| `METRICS.md:628` **and** `RESULTS_DRAFT.md:269` | "test **327** / corpus **1038**" | **369 / 1101** — **must move together** |
| `METRICS.md:1103-1131` | **entire RT.4 `FA_in-scene` section** (n 81×9, means 0.798/0.494/0.638, scene07 n=51) | none 81→**39**, scene07 51→**9**, all three means recomputed |
| `METRICS.md:1105` · `RESULTS_DRAFT.md:552` | "81 of 816 test rows, **19.9 %** of 408 hazard-ON" | **39/816 · 9.6 %** |
| `METRICS.md:698-699` | "test's 96/327 = **29.4 %**" | 96/369 = **26.0 %** |
| `METRICS.md:671-677` · `RESULTS_DRAFT.md:286-291` | occupancy tables, `n GT+ cells 2691` | **2,856** |
| `METRICS.md:1239-1247` | RT.7-c split table, corpus census | **V 801 · H 195 · Hw 33 · none 315** |
| `METRICS.md:1235` **and** `RESULTS_DRAFT.md:146` | "corpus **V 726 → 657**" (τ_int sweep) | **must move together** — the only corpus-V number outside the census table, therefore the easiest to miss |
| `ACCOUNTING.md` §3.1 (:276-280) | V 180 · Hw 6 · none 81 · denominator 327 · 19.9 % | label "old GT" and print corrected alongside: V 219 · Hw 9 · none 39 · **369** · 9.6 % |
| `ACCOUNTING.md` §3.4 row 6 | "corrected-GT rescore denominator — 미기입" | **369 (V 219·E 45·H 96·Hw 9)** |

### 5.2 CONFIRMED INVARIANT — do not touch

- `SEED_TABLE.md:13-15` **`frame_recall_H` 0.688/0.438/0.229 · `frame_recall_E` 0.556/0.600/0.178 ·
  `frame_fa_off` 0.359/0.042/0.238 · `cell_fpr_off` 0.047/0.009/0.035** — Δ = 0.0000 in 9/9 runs.
- `SEED_TABLE.md:9` the FA-matched reading banner — all four points identical.
- `SEED_TABLE.md:21-23` `twin delta (H tier)` 0.285/0.407/0.110 and the whole `tau*` column.
- `SEED_TABLE.md:25` "2 scenes, scene14 60 · scene15 36" — 60+36 = 96 unchanged.
- `F1_FA_MATCHED.md:14-19, 27-32, 83` — H columns, Δ(Depth−RGB), the 8.6× sentence.
- `F2_TWIN_CONDITIONAL.md:17-23 (H, n=96), 25-31 (E, n=45), 43-47, 85-102` — **completely identical**.
- `METRICS.md` RT.1 H table · RT.2 H+E blocks (0.688→0.375 · 0.438→0.438 · 44.7 %) · N.3 · N.5 off-arm
  FA · N.6 τ sweep · N.8 val · RT.5 cluster CI · RT.6 · "0 of 96 pairs fire on the deleted twin".
- `RESULTS_DRAFT.md` RT-A ~ RT-D in full · RT-E(b) sceneN3 · RT-F figure table ·
  RT-E(c)'s `cell_recall_H` portion (only the `cell_f1` portion moves).
- **All v1-scope numbers** (`RESULTS_DRAFT.md` §5.1–5.6, `METRICS.md` §1–13, the 336-frame v1 corpus):
  the 42 frames come from scene07 `boost_e/boost_e2`, **rounds that do not exist in v1**.

### 5.3 Two misquote traps

1. **`METRICS.md:360`** — a v1 sentence reads *"scene07 18 fr / **39 cells** (test) … +39 positive
   cells"*. **v1 scope = invariant.** Same scene, same "39" as the corrected-GT V move. **#1 misquote
   risk in the whole corpus.** Footnote recommended.
2. **`RESULTS_DRAFT.md:136-137`** — "39 of them in the test split" is a **v1 step-gate** number,
   unrelated to G7's 39.

## 6. C/D decomposition (first ever produced for v2) — **directional evidence only**

Frame FA(off) @ τ 0.5, primary rule (C-like n = 48 · D-like n = 360):

| model | FA_C-like | FA_D-like | C − D |
|---|---|---|---|
| rgb | 0.438 ± 0.125 | 0.348 ± 0.144 | **+0.089** |
| depth | 0.167 ± 0.094 | 0.025 ± 0.025 | **+0.142** |
| b2 | 0.451 ± 0.177 | 0.209 ± 0.151 | **+0.242** |

**FA_C > FA_D on all three models — but rgb's signal is carried entirely by sceneN3**, a
trompe-l'œil (fake-staircase painting) built as a hard negative. **Removing N3 flips rgb's sign:
FA(C2 only) 0.069 vs FA_D 0.348 = −0.279.** depth (+0.267) and b2 (+0.194) keep their sign without
N3. Group C is **2 scenes** ⇒ scene-cluster effective n = 2. v2's off arm is **not a true D arm**:
among the 5 D-like scenes, s05·s14·s15·s18 keep `cue_scene_dressing` free, so **no pure
hazard-free / cue-free FA_D sample exists in v2**.

> **Grade: directional evidence only. This table does NOT claim "cues cause false alarms."**
> A quantitative FA_C/FA_D decomposition requires v3's counterfactual (A,C)/(A,D) pairs.

---

## CAVEAT LINE — must travel with this table

> **The corrected GT did not rescue or damage the paper's H claim — it left it untouched, and that
> is a structural fact, not a coincidence.** The defect surface (scene07/08/12 boost heightmaps) and
> the H-96 test set (scene14 + scene15) have **empty intersection**.

> **What the corrected GT *does* change is the V row and every denominator derived from 327.**
> Two numbers (`test 327 / corpus 1038` and `corpus V 726 → 657`) each live in two files and must be
> updated **simultaneously** or the draft becomes internally inconsistent.

> **Two rows are still UNMEASURED under corrected GT**: the YOLO main-table row and the aux appendix
> row. Both need a rescore before submission — see INDEX §재발행 필요 목록 (D65 ④).
