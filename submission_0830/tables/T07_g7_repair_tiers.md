# T07 · G7 corpus repair — tier re-census and what it means for the H claim

<!-- LEDGER: experiments/v3_0823/G7_RELABEL.md :13-14 scope, :76-96 scan, :100-103 mechanism -->
<!-- LEDGER: G7_RELABEL.md :196-198 control gate, :206-213 footprint, :219-228 per-scene, :232-249 census -->
<!-- LEDGER: G7_RELABEL.md :266-295 scene12 verdict, :303-354 gates, :366-384 downstream, :462-480 provenance -->
<!-- LEDGER: experiments/v3_0823/ACCOUNTING.md §4.2 (recount) + §4.4 (arithmetic correction) -->

- **Corrected-GT status**: **this file defines the corrected GT.** Canonical = **variant B**
  (`dataset_manifest_v2corr.json`); sensitivity variant A = `dataset_manifest_v2corr_roundown.json`.
- **Provenance**: `experiments/v3_0823/G7_RELABEL.md` · manifest `experiments/v3_0823/dataset_manifest_v2corr.json`
- **Scope of the repair**: 240 frames (on 120 / off 120) = **8.5 % of the corpus**. Fields replaced:
  `polar_gt` · `polar_gt_pregate` · `gate_excluded` · `raw_vis` · `tier`. Preserved: `rgb` · `depth` ·
  `round` · `cam` · `cond` — **not one pixel changed.** No re-render was needed (all fusion inputs
  already existed; missing fusion inputs = 0 across all 26 pairs × 2 arms).

---

## 1. The defect — 5 (band, scene) pairs, 3 scenes, 2 rounds

`boost_e × {scene07, scene08, scene12}` and `boost_e2 × {scene07, scene12}`. `boost_h` is clean.
All 26 (band, scene) pairs were scanned exhaustively.

| round × scene | split | cells the instrument USED | cells a FUSED reference gives |
|---|---|---|---|
| `boost_e` × scene07 | test | **0** | 19,274 |
| `boost_e` × scene08 | val | **0** | 458 |
| `boost_e` × scene12 | train | **50** | 24,920 |
| `boost_e2` × scene07 | test | **0** | 12,950 |
| `boost_e2` × scene12 | train | **50** | 1,172 |

**Mechanism.** In scene12 the AABB ray passes through the river and reads the **bed (−2.40 m)** while
the camera sees the **water surface (−1.80 m)** — a **0.6 m instrument offset**. With AABB on both
arms the twin difference cancels and only **50 cells = a 5 cm × 2.45 m sliver** survives (the
quantisation residue of one stair riser, `max_diff` 0.3394 m). No pixel can land on that sliver ⇒
`int_px = 0` ⇒ `tier_of` awards **strict-H**.

> **"H was evidence of missing ground truth, not of occlusion."**

Coverage was **all 24 cuts (8 cameras × 3 conditions)** in each defective scene-arm — not partial
damage. Honesty note: D42 recorded "oracle **6 scenes**"; the measured count is **3 scenes / 5 pairs**
(D42's individual numbers were correct).

## 2. Tier re-census — corpus 2,832 frames

| tier | old GT | **corrected GT (B)** | Δ |
|---|---|---|---|
| V | 693 | **801** | +108 |
| E | 72 | 72 | 0 |
| **H (strict)** | 243 | **195** | **−48 (all scene12)** |
| H_weak | 30 | **33** | +3 |
| none_in_fov | 378 | **315** | −63 |
| off | 1,416 | 1,416 | 0 |

Per split:

| split | V | E | H | H_weak | none_in_fov | off |
|---|---|---|---|---|---|---|
| train BEFORE | 438 | 21 | 141 | 21 | 147 | 768 |
| train **AFTER B** | **486** | 21 | **93** | 21 | 147 | 768 |
| val BEFORE | 75 | 6 | 6 | 3 | 54 | 144 |
| val **AFTER B** | **96** | 6 | 6 | 3 | 33 | 144 |
| **test BEFORE** | 180 | 45 | **96** | 6 | 81 | 408 |
| **test AFTER B** | **219** | 45 | **96** | **9** | **39** | 408 |

Per-scene strict-H, BEFORE → AFTER B: test scene14 60→60 · test scene15 36→36 · train scene09 60→60 ·
**train scene12 48→0** · train scene17 33→33 · val scene20 6→6.

## 3. **THE HEADLINE FOR THE PAPER: test H 96 is invariant**

The corpus loses 48 strict-H frames — **all of them scene12, which is a TRAIN scene.** The test
strict-H set is scene14 (60) + scene15 (36) = **96 before and after**. The paper's H-row denominator
does not move.

What *does* move: **test V 180 → 219 (+21.7 %)**, **val V 75 → 96 (+28 %)**, test H_weak 6 → 9,
test none_in_fov 81 → 39, headline recall denominator **327 → 369**.

> The earlier statement *"the recall denominator is uncontaminated"* is **true for the H row only**.
> Published V recalls sit on a different denominator. (banner appended to `PROJECT_STATE_0823_v2.md`)

## 4. Verification — why this is a measurement, not a claim

| gate | result |
|---|---|
| **Control gate** | all **816 frames** from scene-arms with no fused sidecar are **byte-identical JSON** to the 08-20 labels — the pipeline moves no label for any reason other than fusion |
| **Naive gate REJECTED** | "count strict-H frames where the hazard contributes pixels" is 0 by definition of `tier_of` — it returns 0 for the **defective** set too (243→0), so it is not a gate at all. Stated explicitly rather than quietly passed |
| **Substantive gate (footprint degeneracy)** | rule: FLAG if fused ≥ 500 cells **and** ratio = used/fused < 0.10. Pre-repair scene12 = 50/33,605 = **0.0015**. Residual strict-H pairs: **FLAG 0 / 12** |
| **The decisive sign** | genuine strict-H scenes have **ratio ≥ 1.0** (1.04 … ∞) — the camera cannot see the drop, so fusion measures *less*. **That is the physical signature of occlusion.** scene12 was the opposite: the camera saw fine and the AABB ray was blind |
| **Cross-reference gate** | re-deriving tiers under **both** corrected references (A and B): frames that are strict-H in one but not the other = **0**. H status does not depend on reference choice |

## 5. scene12 verdict and downstream contamination

**48/48 scene12 frames lose strict-H; under canonical variant B all 48 become tier V** — exactly as
D50 predicted before the repair was run. (Variant A: V 12 / H_weak 3 / none 33 — the difference is
reference coverage, B 0.748 vs A 0.277 on scene12 ON.)

Training contamination measured: scene12's 48 train frames carried **wrong GT** (2–3 cells/frame
instead of the correct 4–8); scene07 + scene08's 72 frames entered training with **0 GT cells, i.e.
as negatives**. Downstream GT+ cells: test·scene07·on 0 → **165**, val·scene08·on 0 → **108**,
train·scene12·on 126 → **252**.

---

## CAVEAT LINE — must travel with this table

> **The single most important sentence: the repair did not touch the paper's H claim.** The defect
> surface (scene07/08/12 boost heightmaps) and the test H-96 set (scene14 + scene15) have **empty
> intersection**. This is structural, not lucky — and it is why every H, E and off-arm number in the
> main table is verified byte-identical after rescoring (T06 §0).

> **The repair is also the finding.** It is what proved that CUE-OFF's primary target scene
> (scene12) was **not a strict-H scene** — its H tier was a labelling artefact of a 50-cell sliver.
> The two corpus defects are the *diagnostic* contribution of the intervention track (T04).

> **Approval #4 disposition changed**: G7 repair was promoted from "September work" to **v3 stage 1**
> `[승용]`. The v2 table footnote stays.

> **Do not cite "denominator 372."** `ACCOUNTING.md` §4.2 and D55 both printed none 81→36 /
> denominator 327→372; that is arithmetic error. Correct: **none 81→39 · denominator 327→369**
> (§4.4, D59 ⑦).

> **Do not cite "oracle 6 scenes"** (D42). Measured: **3 scenes, 5 pairs.**

> **The 1006× and 672× footprint figures are the same phenomenon.** `CUEOFF_RESULT_v2.md`'s banner
> says 50 → 50,278 cells (**1006×**); `G7_RELABEL.md` measures 50 → 33,605 (**672×**, variant B).
> They differ only because the reference round differs. Cite one with its reference named.
