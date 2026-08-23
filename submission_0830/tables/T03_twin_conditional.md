# T03 · Twin-conditional recall — is the response conditional on the hazard?

<!-- LEDGER: experiments/weekend_0823/rt_response/F2_TWIN_CONDITIONAL.md:5-11 (definition), :17-23 (H), :25-31 (E), :33-39 (V), :43-47 (verification), :53-79 (per-run), :81-102 (by scene) -->
<!-- LEDGER: experiments/v3_0823/V2_RESCORE.md §5.2 :415-432 (corrected-GT invariance), §5.3 :436-444 (V denominator 165->177) -->
<!-- Script: rt_response/code/f2_twin_conditional.py — CPU, read-only over frozen v2 twin dumps -->

- **Corrected-GT status**: **H and E tables are completely identical** under corrected GT
  (`F2_TWIN_CONDITIONAL.md:17-23, 25-31, 43-47, 85-102` all verified invariant).
  **The V table must be re-issued** — its denominator moves **165 → 177 kept pairs**.
- **Provenance**: `experiments/weekend_0823/rt_response/F2_TWIN_CONDITIONAL.md`
- **Definition** (verbatim): a hazard-ON frame counts as a *twin-conditional* hit iff the model fires
  on a GT-positive cell **and** the byte-paired hazard-OFF twin of the same camera cut does **not**
  fire on those same cells: `hit(frame) = [max_on_gt ≥ τ] ∧ [max_off_gt < τ]`, τ = 0.5. Pairs are the
  KEPT (pose-matched) pairs. **Costs no extra render and no extra inference.**

---

## 1. H tier — n = 96 kept pairs per run (3 seeds)

| model | recall (published rule) | **twin-conditional recall** | off-arm twin fire rate | share of fires that are unconditional |
|---|---|---|---|---|
| rgb | 0.688 ± 0.141 | **0.375 ± 0.115** (.229/.438/.458) | 0.330 (.385/.438/.167) | **0.447** |
| depth | 0.438 ± 0.031 | **0.438 ± 0.031** (.406/.469/.438) | **0.000** (.000/.000/.000) | **0.000** |
| b2 | 0.229 ± 0.156 | **0.122 ± 0.068** (.073/.083/.208) | 0.118 (.042/.312/.000) | **0.305** |

> **The Depth arm's hidden-tier response is entirely hazard-conditional: 0 of 96 pairs fire on the
> deleted twin, on all three seeds, so 0.438 → 0.438. 44.7 % of the RGB arm's hidden-tier firings
> also occur when the hazard is gone (0.688 → 0.375). The two arms were not counting the same event.**

## 2. E tier (n = 45) and V tier (n = 165 old GT / **177 corrected GT**)

| tier | model | recall | twin-conditional | off-arm fire | unconditional share |
|---|---|---|---|---|---|
| E | rgb | 0.556 ± 0.378 | **0.207 ± 0.111** | 0.370 | 0.572 |
| E | depth | 0.600 ± 0.000 | **0.600 ± 0.000** | 0.000 | 0.000 |
| E | b2 | 0.178 ± 0.267 | **0.133 ± 0.200** | 0.059 | 0.250 |
| V | rgb | 0.820 ± 0.136 | **0.440 ± 0.055** | 0.382 | 0.446 |
| V | depth | 0.927 ± 0.036 | **0.873 ± 0.045** | 0.055 | 0.059 |
| V | b2 | 0.711 ± 0.115 | **0.410 ± 0.073** | 0.303 | 0.422 |

**Verification against R2's independently published values**: rgb 0.375 = 0.375 ✓ · depth 0.438 =
0.438 ✓ · b2 published 0.121, recomputed 0.122 ✓.

## 3. Where the unconditional firing actually lives — **scene15**

| run | scene | n | plain recall | twin-conditional | off-arm fire |
|---|---|---|---|---|---|
| rgb_s42 | scene15 | 36 | 0.806 | **0.028** | **0.833** |
| b2_s43 | scene15 | 36 | 0.889 | **0.056** | **0.833** |
| rgb_s44 | scene14 | 60 | 0.667 | **0.667** | **0.000** |

Depth is 0.000 off-arm in **all six** scene cells. The RGB arm's unconditional firing is not spread
evenly — it is concentrated in scene15, the same scene that T11 shows carries no discriminative
evidence.

---

## CAVEAT LINE — must travel with this table

> **CITATION TRAP — the "46.7 %" figure for b2 is not in the ledger.** `MORNING_REPORT_0823.md`
> §2.3 prints b2's unconditional share as 46.7 %; that is the **relative drop** (0.229 → 0.122), not
> the quantity in the other two rows. The ledger's printed share for b2 is **0.305**
> (`F2_TWIN_CONDITIONAL.md:23`). RGB's 0.447 → "44.7 %" is correct and *is* the printed share.
> **Use 0.305 for b2, or say explicitly which quantity you mean.**

> **Twin V denominator is 177, not 219.** Of the 39 frames the corrected GT adds to V, only **12
> pairs** pass the pose filter; **27 are excluded on `ground_z` mismatch** (the toggle moves the
> camera's own ground — the known D15/D17 mechanism). State 177 whenever citing the twin V tier.

> **What the twin identifies, and what it does not.** The twin identifies **that** the response is
> caused by the hazard's presence in the scene; it does **not** identify **which image property**
> carries the causation. The intervention also removes *everything the scene builder places inside
> the same branch* (in scene14: shoulder massif, side slopes, stair, coursing, parapets, cues,
> litter), so Δ measures sensitivity to that whole package. (caveat C4 · T-frag F04)

> **This is one of three independent measurements pointing the same way** — with the CUE-OFF census
> (T04) and the Gazebo cross-renderer track (T05). Its agreement with them is the argument; none of
> the three alone is sufficient.

> **The Depth 96/96 result survives the corrected GT for a structural reason**: scene12's 48 H→V
> move is a **train** move, and scene12 is not among the 7 test scenes. The H basis stays
> scene14 60 + scene15 36 = 96.
