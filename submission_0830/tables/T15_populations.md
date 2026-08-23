# T15 · Registered populations and denominators — the single reference for every "n"

<!-- LEDGER: experiments/v3_0823/ACCOUNTING.md §3.1 (test-core), §3.2 (v2 corpus), §3.3 (CUE-OFF), §3.4 (v3 TBD) -->
<!-- LEDGER: ACCOUNTING.md §4.2 (corrected recount), §4.4 (arithmetic correction), §4.8 (corrected denominator) -->
<!-- LEDGER: experiments/v3_0823/G7_RELABEL.md :232-249 -->
<!-- SOURCE OF TRUTH: split experiments/dayrun_0820/split_v2_full.json + dataset_manifest_v2_full.json / dataset_manifest_v2corr.json -->

- **Corrected-GT status**: **both columns printed side by side, as the ledger requires.**
- **Rule (`ACCOUNTING.md` §5 / §3.4 append rule)**: a number may not enter a document without
  ① a ledger file path ② the re-aggregation command or script ③ the measurement date.
  **Denominators are cited from ACCOUNTING.md only — never recomputed by hand.**

---

## 1. test-core — 7 scenes, frames invariant, **answer key NOT invariant**

| item | old GT | **corrected GT (B)** |
|---|---|---|
| scenes (7) | `scene05` `scene07` `scene14` `scene15` `scene18` `sceneC2` `sceneN3` | same |
| total frames | **816** | **816** |
| on / off | **408 / 408** (twin pairs exactly matched) | 408 / 408 |
| V | 180 | **219** |
| E | 45 | 45 |
| **H (strict)** | **96** | **96** |
| H_weak | 6 | **9** |
| none_in_fov | 81 | **39** |
| **headline recall denominator** | **327** | **369** |
| conditioning-dropout disclosure (mandatory in the same table) | 81/408 = **19.9 %** | 39/408 = **9.6 %** |
| positive cells (816 frames) | 2,691 | **2,856** |
| **twin KEPT pairs** | 366 (V **165** · E 45 · H **96** · Hw/none) | 366 (V **177** · E 45 · H **96**) |
| twin EXCLUDED pairs | 42 (all scene07, \|Δz\| 3.57 / 4.02 m) | 42 |

Frames per scene: scene05/07/14/15/18 **144 each** (main 48 + boost 96) · sceneC2/sceneN3 **48 each**.
**boost-exposed frames = 480** — i.e. the G7 repair surface touches **59 % of test-core GT**.

**Twin tolerance stratification (408 pairs, independently re-verified)**:
EXACT (≤1e-6) **312** (V 132 · E 45 · **H 96** · Hw/none 39) · TOL (1e-6, 0.15] **54**
(V 33 · Hw/none 21 · **E 0 · H 0**) · EXCL (>0.15) **42**.
⇒ **H and E claims are tolerance-independent** (D27 identity re-confirmed).

## 2. v2 corpus — 2,832 frames

| tier | old GT | **corrected GT (B)** | Δ |
|---|---|---|---|
| V | 693 | **801** | +108 |
| E | 72 | 72 | 0 |
| H (strict) | 243 | **195** | −48 (all scene12) |
| H_weak | 30 | **33** | +3 |
| none_in_fov | 378 | **315** | −63 |
| off | 1,416 | 1,416 | 0 |
| **total** | **2,832** | **2,832** | 0 |

Twin identity: on = 693+72+243+30+378 = **1,416** = off **1,416** ✓ (old GT).
Split decomposition (old GT, measured): train **1,536** · val **288** · test **816** · hold **192**.
Corpus hazard frames (≥1 GT+ cell): **1,038 → 1,101**.
Double-counting audit: **0** (`merge_corpus.py` `::<round>` suffix audit passed).
v1 corpus (reference): V 438 · E 36 · H 45 · Hw 12 · none 261 · off 792 = **1,584** (33 scenes × 48 cuts).

## 3. CUE-OFF verdict population

| population | n | status |
|---|---|---|
| primary leg, all blocks | **30 cells** | **정본 headline** |
| primary leg, A2-7 folded | **21 cells** | **정본 — for replication claims** |
| primary, decidable | 12 cells (40.0 %) | derived |
| secondary B1 leg | 24 cells | **promotion forbidden** |
| frame-level unit | per-cell `n_paired` (0 / 6 / 24 / 27) | **§4.5-3 floor = 10** |

## 4. FA census exposure denominators

| stratum | old GT (§4.5) | **corrected GT (§4.7)** |
|---|---|---|
| OFF exposure | 8,160 cells (408 × 20) | **8,160** (identical) |
| ON_NEG exposure | 5,469 cells | **5,304** |
| `none_in_fov` ON_NEG exposure | 1,620 (= 81 × 20) | **780** (= 39 × 20) |
| total FA events | 6,925 (OFF 2,212 / ON_NEG 4,713) | **6,106** (OFF **2,212** / ON_NEG 3,894) |

**The two strata must never be summed.**

## 5. Populations NOT yet filled (v3, `ACCOUNTING.md` §3.4)

| # | population | status |
|---|---|---|
| 1 | cue-presence threshold **k** (seg cue-pixel floor) | **UNSET — must be gate-fixed before cue-conditional supervision begins** |
| 2–4 | test-ext scene list / frame counts / 4-arm split; test-ext paired-H per scene; FA_C / FA_D denominators | unfilled — at P-5 confirmation |
| 5 | v3 corpus train/val accounting after G7 re-fusion | unfilled |
| 6 | corrected-GT v2 rescore denominator on test-core 816 | **now measurable: 369 (V 219 · E 45 · H 96 · Hw 9)** — ready to append |
| 7 | ignore-mask cell count (**training loss only — evaluation denominator unchanged**) | unfilled |
| 8 | `none_in_fov`-equivalent handling protocol in v3 | **deliberately left open** — the relabel *mostly filled* the hole (56.7 % → 17.5 %) but the residual 39 frames are still in no denominator and `labeler.py:526` is unfixed |

---

## CAVEAT LINE — must travel with this table

> **Do not cite "denominator 372."** `ACCOUNTING.md` §4.2 and D55 both printed none 81→36 /
> 327→372; that is arithmetic error (219+45+96+9+36 = 405 ≠ 408). **Correct: none 39, denominator
> 369** (§4.4, D59 ⑦). `ASSUMPTION_LEDGER` LAB-12's "372" must also be read as 369.

> **`test 327 / corpus 1038` appears in exactly two places** — `METRICS.md:628` and
> `RESULTS_DRAFT.md:269` — and **both must move to 369 / 1101 together.** Every `/327` in
> `METRICS.md:636-664` and every derived percentage in `RESULTS_DRAFT.md:271-284` is downstream of
> that one line.

> **`corpus V 726 → 657`** (the τ_int sweep endpoints) is the **only corpus-V number outside the
> census table** — it lives in `METRICS.md:1235` and `RESULTS_DRAFT.md:146`. **Easiest to miss.**

> **The twin V denominator is 177, NOT 219.** Only 12 of the 39 newly-added V frames pass the pose
> filter; 27 fail on `ground_z`.

> **`none_in_fov` frames are in NO published denominator** — not in recall (no GT-positive cell) and
> not in `frame_fa_off` (they are on-arm frames). The conditioning-dropout share **must be printed
> in the same table as the recall** (R2 method requirement).

> **All v1-scope numbers (336-frame corpus, 15-cell grid) are invariant** — the 42 moving frames come
> from scene07 boost rounds, which do not exist in v1. Two "39"s in v1-scope text are unrelated
> coincidences (`METRICS.md:360`, `RESULTS_DRAFT.md:136-137`); footnote them.
