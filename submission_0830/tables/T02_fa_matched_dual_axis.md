# T02 · FA-matched recall — **DUAL AXIS** (frame axis + cell axis)

<!-- LEDGER frame axis: experiments/weekend_0823/rt_response/F1_FA_MATCHED.md:27-32 (§2 exact-quantile), :36-73 (per-seed), :87-92 (V/E) -->
<!-- LEDGER cell axis:  experiments/v3_0823/redteam/EVL12_CELL_AXIS.md:56-61 (frame), :65-70 (cell), :105-111 (tau=0.5 flip), :84-91 (alarm burden) -->
<!-- LEDGER obligation: experiments/v3_0823/ACCOUNTING.md §4.8 #1 (D62) + §4.9-2 (D64) -->
<!-- LEDGER corrected-GT invariance: EVL12_CELL_AXIS.md:124-135 -->
<!-- Scripts: rt_response/code/f1_fa_matched.py · v3_0823/redteam/evl12_cell_axis.py -->

- **Corrected-GT status**: **BOTH GT AGREE — verified, not asserted.** The H-96 / E-45 GT rows and
  the whole off arm are **byte-identical** across old and corrected GT; the full sweep was re-run on
  the old-GT ledger and matched **to 3 decimals**. (`EVL12_CELL_AXIS.md:124-135`)
  **Exception: the V rows move** — see §4 of this file.
- **Provenance**: `experiments/weekend_0823/rt_response/F1_FA_MATCHED.md` (frame axis, published) ·
  `experiments/v3_0823/redteam/EVL12_CELL_AXIS.md` (cell axis, NEW — D65)
- **Method**: τ taken from **empirical order statistics** of the off arm (exact-quantile), giving the
  largest achieved FA at or under target. Frame axis τ population = 408 off-frame max probabilities
  (resolution 1/408 = 0.0025). Cell axis τ population = **8,160 off cells** (408 × 20; resolution
  1/8160 = 0.000123), matching `ACCOUNTING.md` §4.5 row A. No retraining, no re-render.

---

## 0. THE OBLIGATION (do not print one axis alone)

> **이중 축 규약 / dual-axis rule.** FA-matched recall is reported on **both** the frame axis
> (`frame_recall_H` @ `frame_fa_off`) and the cell axis (`cell_recall_H` @ `cell_fpr_off`).
> Registered in `ACCOUNTING.md` §4.8 #1 (RT-A blocking finding EVL-12) and re-affirmed for
> Dashboard ① in §4.9-2. `bundle()` already emits both, so the extra cost is zero.

---

## 1. Frame axis — H recall at matched off-arm frame FA (3-seed mean ± half-range)

| matched FA | achieved FA (R/D/B) | **RGB H** | **Depth H** | B2 H | Δ(Depth−RGB) | seeds Depth>RGB |
|---|---|---|---|---|---|---|
| 0.359 | .358 / .353 / .358 | 0.729 ± 0.135 | **0.781** ± 0.078 | 0.399 ± 0.078 | **+0.052** | 2/3 |
| 0.200 | .199 / .199 / .199 | 0.483 ± 0.172 | **0.562** ± 0.031 | 0.198 ± 0.141 | **+0.080** | 1/3 |
| 0.100 | .098 / .096 / .098 | 0.326 ± 0.229 | **0.510** ± 0.078 | 0.097 ± 0.099 | **+0.184** | 3/3 |
| 0.050 | .049 / .044 / .049 | 0.243 ± 0.208 | **0.479** ± 0.094 | 0.031 ± 0.036 | **+0.236** | 3/3 |

V and E at the same matched frame-FA points (3-seed mean):

| matched FA | RGB V | Depth V | B2 V | RGB E | Depth E | B2 E |
|---|---|---|---|---|---|---|
| 0.359 | 0.809 | 0.994 | 0.800 | 0.570 | 0.733 | 0.193 |
| 0.200 | 0.669 | 0.983 | 0.746 | 0.296 | 0.600 | 0.126 |
| 0.100 | 0.530 | 0.956 | 0.646 | 0.081 | 0.600 | 0.089 |
| 0.050 | 0.443 | 0.939 | 0.552 | 0.015 | 0.600 | 0.022 |

## 2. Cell axis — H **cell** recall at matched off-arm **cell** FPR (NEW, D65)

Registered mapping **MAP-C**: anchor = RGB's published operating point (τ = 0.5) `cell_fpr_off`
3-seed mean **0.046732**, then the *same* reduction ratios as the frame axis (×.200/.359,
×.100/.359, ×.050/.359). Fully determined by already-published quantities; no rounding, no new
judgement, fixed before results were seen. (`EVL12_CELL_AXIS.md:31-36`)

| matched cell FPR | **RGB cH** | **Depth cH** | B2 cH | Δ(Depth−RGB) | seeds Depth>RGB |
|---|---|---|---|---|---|
| 0.046732 | 0.352 ± 0.125 | **0.671** ± 0.076 | 0.221 ± 0.125 | **+0.319** | **3/3** |
| 0.026035 | 0.258 ± 0.130 | **0.631** ± 0.080 | 0.110 ± 0.087 | **+0.373** | **3/3** |
| 0.013017 | 0.156 ± 0.119 | **0.584** ± 0.089 | 0.050 ± 0.053 | **+0.428** | **3/3** |
| 0.006509 | 0.111 ± 0.104 | **0.510** ± 0.162 | 0.018 ± 0.021 | **+0.399** | **3/3** |

**Verdict**: "Depth ≥ RGB at every matched-FA point" **survives the axis change and gets stronger** —
Δ grows from +0.052…+0.236 to +0.319…+0.428, and seed consistency rises from 1–3/3 to **3/3 at all
four points**. *Axis choice does not change the sign or the ordering — only the magnitude and the
robustness.* (`EVL12_CELL_AXIS.md:13-16`)

## 3. Alarm burden — what the frame axis hides

| axis | operating point | RGB cells/FA-frame · cellFPR | Depth cells/FA-frame · cellFPR | B2 | Depth/RGB cellFPR |
|---|---|---|---|---|---|
| frame | FA .359 | 3.08 · .0552 | 7.31 · **.1290** | 3.81 · .0682 | **2.34×** |
| frame | FA .200 | 2.10 · .0209 | 3.25 · .0322 | 2.56 · .0254 | 1.54× |
| frame | FA .100 | 1.76 · .0086 | 2.90 · .0138 | 1.91 · .0094 | 1.60× |
| frame | FA .050 | 1.60 · .0039 | 4.33 · .0096 | 1.90 · .0047 | **2.46×** |
| cell | cellFPR .0467 | 2.68 (frame FA **.353**) | 3.90 (frame FA **.243**) | 3.20 (.295) | 1.00× (by definition) |
| cell | cellFPR .0065 | 1.79 (frame FA .073) | 4.82 (frame FA .039) | 1.95 (.068) | 1.00× (by definition) |

Matching on the frame axis **hides a 2.3–2.5× difference in cell-level alarm volume**. The mirror is
also true: matching on the cell axis re-opens the frame axis (.0467 → RGB .353 vs Depth .243). **The
two axes cannot be reconciled — which is exactly why both must be printed.**
(`EVL12_CELL_AXIS.md:93-95`)

## 4. τ = 0.5 — **the unit flips the winner** (the single most citable result of D65)

Same checkpoints, same frames, same GT. Only the unit of "a detection" changes.

| model | frame H recall | **cell H recall** | frame FA | cell FPR |
|---|---|---|---|---|
| RGB | **0.688** | 0.344 | .359 | .0467 |
| Depth | 0.438 | **0.537** | .042 | .0089 |
| B2 | 0.229 | 0.096 | .238 | .0347 |

> **On the frame axis RGB wins (0.688 > 0.438); on the cell axis Depth wins (0.537 > 0.344).**
> Cause: `any-hit` recall (EVL-08) and `any-fire` FA (EVL-12) stack in the same direction and reward
> "hit one correct cell, then spray the rest" — which is precisely RGB's behaviour.
> **If the paper prints only the frame-axis H column, this inversion is invisible.**
> (`EVL12_CELL_AXIS.md:113-116`)

## 5. Corrected-GT impact — V rows only

| check | result |
|---|---|
| frame_id order | identical |
| probabilities `p_*` | **exactly identical** (same checkpoint, same images) |
| rows whose GT differs | **42** |
| tier transitions of those 42 | `none_in_fov → V` **39** · `none_in_fov → H_weak` **3** |
| **H 96 rows GT** | **byte-identical** |
| E 45 rows · old V 180 rows GT | **byte-identical** |

| operating point | RGB V old→corr | Depth V old→corr | B2 V old→corr |
|---|---|---|---|
| frame FA .359 | 0.809 → **0.784** (−.025) | 0.994 → 0.995 (+.001) | 0.800 → 0.823 (+.023) |
| frame FA .050 | 0.443 → **0.399** (−.044) | 0.939 → 0.927 (−.012) | 0.552 → 0.556 (+.004) |
| cell FPR .0467 | 0.401 → 0.392 | 0.857 → 0.865 | 0.505 → 0.529 |

Corrected GT **widens the Depth–RGB gap on the V row too**. **Any table quoting a V row must be
re-drawn under corrected GT** (`EVL12_CELL_AXIS.md:145-146`; regeneration in INDEX §재발행 필요 목록).

---

## CAVEAT LINE — must travel with this table

> **RGB's surviving claim is the weak one, and it is enough.** *"A monocular RGB model with no hazard
> pixels available still recovers a third of the hidden-tier frames at a 10 % false-alarm budget
> (0.326 ± 0.229)"* — **not** "RGB leads Depth". The main table's H ordering is an operating-point
> artefact. (`METRICS.md:1036` · `RESULTS_DRAFT.md` RT-A)

> **Citation accident to avoid — the alarms-per-FA-frame figure has two estimators.** Depth is
> **4.29 (seed-pooled)** or **5.50 (mean of per-seed ratios)**; the spread comes from depth_s43
> (3 frames, 27 cells = 9.00; s42 1.71 / s44 5.78). RGB is 2.60 / 2.61 — effectively the same either
> way. **State which estimator you are quoting.** D65's summary line cites 4.29 without the label.
> (`EVL12_CELL_AXIS.md:96-99`)

> **Seed unanimity is not uniform on the frame axis.** At FA .359 and .200 the frame axis is 2/3 and
> 1/3 (rgb_s43 reaches .812/.615, above Depth). The cell axis is 3/3 at all four points.
> (`EVL12_CELL_AXIS.md:74-76`)

> **Red-team self-correction, on the record.** RT_LEDGER_A's EVL-12 guessed the frame axis favoured
> Depth. **That direction was wrong** — Depth clusters its false alarms into few frames (1.6–2.4×
> more cells per frame than RGB), so frame-level `any-fire` counts Depth *unfavourably*. The
> substance of the objection (the unit was never derived, and it is load-bearing) stands.
> (`EVL12_CELL_AXIS.md:20-22`)
