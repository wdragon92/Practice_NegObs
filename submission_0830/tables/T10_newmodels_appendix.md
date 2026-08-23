# T10 · New encoders (APPENDIX) — no gain, and one training failure that indicts the recipe

<!-- LEDGER: experiments/weekend_0823/newmodels/FA_MATCHED.md :7 inputs, :18-32 FA-matched, :36-42 tau0.5 -->
<!-- LEDGER: FA_MATCHED.md :88-93 E/V, :99-111 collapse diagnosis, :115-126 selector, :133-144 scope -->
<!-- LEDGER: experiments/mainrun_0819/DECISIONS.md D52 (corrects D51) -->

- **Corrected-GT status**: **OLD GT — and no corrected dumps exist for these runs.** The census
  script enforces `--corr` and `--appendix` as mutually exclusive (`ACCOUNTING.md` §4.7 ④). The
  FA-matched H figures are structurally corrected-GT-invariant (τ from the off arm, recall on the
  96 H frames), but this has **not been verified by rescoring** for the appendix arms.
- **Provenance**: `experiments/weekend_0823/newmodels/FA_MATCHED.md`
- **Approval #8**: **appendix only** `[승용]`.
- **Method**: identical to T02's frame axis — exact-quantile τ from the off arm (resolution
  1/408 = 0.0025). 3 seeds each.

---

## 1. FA-matched H recall — both new encoders are BELOW the baseline at every point

| matched FA | **resnet34 (baseline)** | resnet50 | convnext_tiny | Δ(r50) | Δ(cnx) |
|---|---|---|---|---|---|
| 0.359 | **0.729 ± 0.135** | 0.479 ± 0.198 | 0.358 ± 0.177 | **−0.250** | **−0.372** |
| 0.200 | **0.483 ± 0.172** | 0.267 ± 0.172 | 0.160 ± 0.120 | **−0.215** | **−0.323** |
| 0.100 | **0.326 ± 0.229** | 0.115 ± 0.089 | 0.073 ± 0.078 | **−0.212** | **−0.253** |
| 0.050 | **0.243 ± 0.208** | 0.056 ± 0.062 | 0.031 ± 0.036 | **−0.188** | **−0.212** |

Achieved FA: resnet34 .358/.199/.098/.049 · resnet50 .358/.199/.098/.049 · convnext .341/.180/.084/.043.

E and V at the same budgets:

| matched FA | r34 V | r50 V | cnx V | r34 E | r50 E | cnx E |
|---|---|---|---|---|---|---|
| 0.359 | 0.809 | 0.819 | 0.252 | 0.570 | 0.511 | 0.711 |
| 0.200 | 0.669 | 0.759 | 0.104 | 0.296 | 0.370 | 0.348 |
| 0.100 | 0.530 | 0.654 | 0.039 | 0.081 | 0.267 | 0.185 |
| 0.050 | 0.443 | 0.524 | 0.013 | 0.015 | 0.059 | 0.074 |

## 2. Why the unmatched τ = 0.5 column is a trap

| arm | H | E | V | **off-arm FA** |
|---|---|---|---|---|
| resnet34 (baseline, RGB) | 0.688 ± 0.141 | 0.556 | 0.796 | **0.359** |
| resnet50 (RGB) | 0.309 ± 0.125 | 0.430 | 0.778 | 0.249 |
| convnext_tiny (RGB) | **0.823 ± 0.188** | 0.956 | 0.824 | **0.909** |

convnext_tiny reads its H at **FA 0.909** while resnet34 reads its at **FA 0.359** — printed in the
same column, a **2.54×** false-alarm difference disappears. Per-seed convnext FA = **1.000, 1.000,
0.728** (s43 is 1.000 on every metric = always firing).

> **⚠ The ledger forbids citing the unmatched τ = 0.5 numbers (H .63–1.0) in any form.**

## 3. It is not an architecture result — it is a **training failure**

Off-arm max-probability range over 408 frames:

| run | min | median | max | **range** | mean per-cell sd |
|---|---|---|---|---|---|
| resnet34_s42 | 0.000137 | 0.270656 | 0.987679 | 9.88e-01 | 1.93e-01 |
| resnet34_s43 | 0.002474 | 0.476847 | 0.999933 | 9.97e-01 | 1.75e-01 |
| resnet34_s44 | 0.000004 | 0.038274 | 0.985855 | 9.86e-01 | 1.65e-01 |
| resnet50_s42/43/44 | — | — | — | ~1.00e+00 | 1.6–2.4e-01 |
| **convnext_tiny_s42** | 0.501409 | 0.501472 | 0.501490 | **8.10e-05** | **7.91e-06** |
| **convnext_tiny_s43** | 0.631690 | 0.631810 | 0.631894 | **2.04e-04** | **4.36e-05** |
| convnext_tiny_s44 | 0.233064 | 0.529481 | 0.621995 | 3.89e-01 | 4.12e-02 |

**2 of 3 convnext seeds emit a near-constant output regardless of input.** Change the picture, the
output does not change. And **convnext_s43's selected checkpoint is epoch 1** (16 epochs trained).

### 3.1 Root cause — and it applies to the MAIN TABLE too

Selector = `0.5·val_f1 + 0.5·val_H_frame_recall`, and **val has only 6 strict-H frames**
(`runs/*/config.json::n_val_strict_h = 6`). On a 6-frame denominator, H recall is a coin flip with
six steps (0 / .167 / .333 / .5 / .833 / 1.0) — and it is **half the selector**. "Fire on
everything" earns H recall = 1.0 for free, so **the metric actively prefers an always-firing
checkpoint.** Every selected epoch in the table has val_H_recall = **1.000**.

> **This selection rule belongs to recipe v2 and the resnet34 baseline used it identically.** It is
> not a defect of the new models — it is a **known weakness of the recipe** that surfaced first in
> the less stable encoder. **Promoted to caveat C3, which applies to the main table.**

---

## CAVEAT LINE — must travel with this table

> **What may be said**: "running convnext_tiny under *this recipe and this selector*, 2 of 3 seeds
> collapsed to constant output"; "the one seed that did not collapse (s44) is still below resnet34
> at every FA-matched point"; "the selector's H term has a 6-frame denominator and rewards always
> firing."
> **What may NOT be said**: "convnext_tiny is unsuited to this task"; "n = 1 supports an architecture
> ranking"; "the collapse was the encoder rather than the learning rate or schedule."

> **D51 is corrected by D52.** The earlier note *"resnet50 ≈ resnet34, comparable"* held **only at
> the unmatched τ = 0.5**. Under FA matching, resnet50 is −0.19 to −0.25 everywhere.

> **The answer to D45's question** ("is cue learning general across backbones?") is:
> **"under this recipe, changing the encoder buys nothing — the table stays at three resnet34 rows."**

> **The failure is a gift to the paper.** It is the cleanest available demonstration of caveat C3
> (H-blind checkpoint selection), which the main table shares. That is the reason to include this
> appendix at all — not the encoder comparison.

> **Unplanned bonus (from T13)**: convnext's constant output lands **exactly on the max-prior cell**
> (centre sector × outermost band), which the FA census independently identified. It functions as a
> **free positive control** for the grid-locked finding.
