# T09 · Fusion row (APPENDIX) — complementarity exists on the distance axis only

<!-- LEDGER: experiments/weekend_0823/fusion/FUSION_ROW.md :9,:19-36 method, :81-84 tier axis -->
<!-- LEDGER: FUSION_ROW.md :88-96 twin, :102-106 per-seed E/H, :119-134 distance axis -->
<!-- LEDGER: FUSION_ROW.md :138-149 new cells, :159-163 corpus forcing, :173-191 verdict, :197-219 placement -->

- **Corrected-GT status**: **OLD GT.** Inputs are the published `per_frame.csv` dumps
  (denominator 327, V 180). The E/H = +0.000 result is denominator-independent, but **the V row and
  the cell-series columns would move** under corrected GT. Not yet regenerated — see INDEX
  §재발행 필요 목록.
- **Provenance**: `experiments/weekend_0823/fusion/FUSION_ROW.md`
- **Approval #8**: **appendix only** `[승용]` — must NOT be added to the 4-row main table.
- **Method**: cell-level OR. *Cell c of frame f fires ⟺ `p_unet(f,c) ≥ 0.50` OR `p_yolo(f,c) ≥ 0.25`.*
  **Zero retraining, zero GPU** — all inputs are stored `per_frame.csv`. **No threshold was chosen on
  test.** The φ rescaling identity was asserted on a 100k-point grid *and* on all 16,320 real cells.

---

## 1. Tier axis — no complementarity

| model | V | E | H | det rate | FA (off) | cell_fpr_off | cell_f1 | cell_recall | cell_precision |
|---|---|---|---|---|---|---|---|---|---|
| rgb | 0.796 ± 0.164 | 0.556 ± 0.378 | 0.688 ± 0.141 | 0.730 | 0.359 | 0.047 | 0.450 | 0.385 | 0.566 |
| yolov8n @ τ0.25 | 0.150 ± 0.028 | 0.000 | 0.000 | 0.083 | 0.024 | 0.0015 | 0.026 | 0.014 | 0.472 |
| **rgb ∪ yolo** | **0.822 ± 0.147** | **0.556 ± 0.378** | **0.688 ± 0.141** | 0.744 | 0.368 | 0.048 | 0.455 | 0.395 | 0.558 |
| **Δ (fusion − rgb)** | **+0.026** | **+0.000** | **+0.000** | +0.014 | **+0.009 (worse)** | +0.0015 (worse) | +0.005 | +0.010 | −0.008 (worse) |

**E and H change by exactly 0.000 on all three seeds** (s42 .600→.600 / .594→.594 · s43 .911→.911 /
.875→.875 · s44 .156→.156 / .594→.594). **This is structural, not coincidence** — see §3.

Twin Δ (366 pose-matched pairs): rgb H **0.2852 → 0.2850 (−0.0002 = unchanged)**, E completely
unchanged; the entire +0.009 in Δ(all) comes from the V tier. **Fusion adds not one grain to this
paper's causal evidence.**

The V gain in context: **+0.026 against a seed spread of ±0.164 — about 1/6 of the scatter.** Only
**14** of 981 hazard frames flip miss→hit (6/1/7 by seed), **all 14 are V tier, 0 are E or H**;
**11** frames gain a new false alarm — an exchange ratio of 1 : 0.79.

## 2. Distance axis — **the real finding**

| band | range | rgb cell recall | yolo cell recall | fusion cell recall | Δ | rgb cell FPR(off) | fusion cell FPR(off) |
|---|---|---|---|---|---|---|---|
| **band1** | **[0, 2) m** | **0.000 ± 0.000** | 0.1225 ± 0.0299 | **0.1225 ± 0.0299** | **+0.1225** | 0.0000 | 0.0041 |
| band2 | [2, 5) m | 0.265 ± 0.097 | 0.056 ± 0.007 | 0.297 ± 0.091 | +0.033 | 0.0100 | 0.0118 |
| band3 | [5, 8) m | 0.297 ± 0.103 | 0.0008 | 0.297 ± 0.105 | +0.0008 | 0.0407 | 0.0407 |
| band4 | [8, 12) m | 0.511 ± 0.206 | 0.0005 | 0.511 ± 0.206 | +0.0005 | 0.1363 | 0.1363 |

> **The RGB U-Net never fires a band1 cell at τ = 0.5 — not once. 3 seeds × 4,080 slots = 0 times**
> (`unet_fired_by_band.band1 = 0 / 0 / 0`). The fusion row's band1 recall **0.1225 is entirely
> YOLO's**, matching the YOLO-alone row to four decimals — by definition, because RGB contributes
> nothing in that band.

Of the **217** cells fusion newly lights, **213 (98.2 %) are band1–2**, and **133 (61 %) are false
positives.** The gain is not free.

**Cause hypotheses**: (i) training prior is 10× lower — `train_positive_rate` band1 **0.021–0.023**
vs band4 **0.24–0.36**, and `bias_init` is initialised to that prior; (ii) 0–2 m cells project to a
few dozen pixels at the bottom of the frame and survive the 512² squash thinly.

## 3. Why E/H = +0.000 is forced by the corpus

| tier | band1 GT+ cells | band2 GT+ cells |
|---|---|---|
| V (180 frames) | **117** | 363 |
| E (45 frames) | **0** | 15 |
| **H (96 frames)** | **0** | **0** |

YOLO's recall is confined to bands 1–2; E and H have **no GT-positive cells there at all**. The
zero is arithmetic, not a measurement of detector quality.

---

## CAVEAT LINE — must travel with this table

> **One-line verdict**: *"Complementarity is real on the DISTANCE axis, not on the TIER axis."*
> Tier axis: V +0.026 (inside seed scatter), E +0.000, H +0.000, twin Δ(H) −0.0002.
> Distance axis: the detector fills band1 [0, 2) m from 0.000 → 0.1225, where the U-Net does not
> fire at all. Price: FA +0.009, cell precision −0.008, band1 cell FPR 0.0000 → 0.0041.

> **Cannot go in the main text, cannot be omitted.** Not in the main text — it changes E/H by
> exactly 0.000 and would invite the misreading "fusion improved things." Not omitted — **this is an
> audit, not a result**: it is the answer to *"why didn't you cascade?"* And the band1 blind spot is
> genuinely new information.

> **Default placement**: appendix, one paragraph + §1 table + §2 band table. Main table stays at
> **4 rows**. **One sentence in the limitations section**: *"the [0, 2) m near field is a blind spot
> of the current polar head, consistent with a cell prior imbalance of 0.021 vs 0.36."*

> **If it is ever promoted**, the column header must read **"rgb ∪ yolo (evaluation-only union, no
> retraining)"** and the caption must nail the 0.000 down as **confirmation of no mapping leak**.

> **The band1 blind spot is one of two distinct near-range problems and they must not be conflated.**
> This one is a model/prior artefact. The *other* — the real-world 15-of-20 grid (T14) — is a
> field-of-view artefact of the regulation pose. Neither is the drop-off-specific difficulty, which
> is the **opposite**: far-field vanishing (~1/d²). (`PROJECT_STATE_0823_v2.md` §1-5)
