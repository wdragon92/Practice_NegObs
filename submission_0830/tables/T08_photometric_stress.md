# T08 · Photometric stress — no augmentation needed, but over-exposure is irreversible

<!-- LEDGER: experiments/weekend_0823/photometric/PHOTOMETRIC_STRESS.md :15-29 scope, :40-43 design -->
<!-- LEDGER: PHOTOMETRIC_STRESS.md :57-59 params, :73-74 identity gate, :85-99 results, :118-141 tau refit -->
<!-- LEDGER: PHOTOMETRIC_STRESS.md :145-168 seed reversal, :174-176 decision rule, :203-205 pilot rules -->
<!-- Figure: experiments/weekend_0823/photometric/photometric_stress.png (TRACKABLE) -->

- **Corrected-GT status**: **N/A — val split only.** The G7 repair moves val V 75 → 96, so the val
  denominators quoted below are **old GT**. The *decision* (change < 0.1) has a large margin and the
  direction of every effect is unaffected; **but if a val number is printed in the paper it should
  be re-issued under corrected GT.**
- **Provenance**: `experiments/weekend_0823/photometric/PHOTOMETRIC_STRESS.md` · fig `photometric_stress.png`
- **Scope, stated first**: **val only. The 7 test scenes were not read for a single frame** —
  `code/photo_stress.py`'s `--subset` is `choices=["val"]`, so argparse refuses `test`.
- **Design**: 11 variants (identity 1 + brightness 4 + gamma 2 + exposure 4) × 3 seeds = **33
  inferences**, ~66 s per seed. Identity-reproduction gate: **max |Δp| = 5.00e-07** on all 3 seeds.
- **val population (old GT)**: 288 total / 144 on / 144 off · hazard frames with ≥1 GT+ cell **90** ·
  V **75** · E **6** · H **6**. **E and H are 6 frames each, so 1 frame = 0.167.**

---

## 1. Pre-registered decision — PASS with margin

> Rule (brief §6.6, fixed before results): *"if recall drop at ±40 % brightness is < 0.1, that is
> grounds for **no photometric augmentation**; more than that, reconsider augmentation before the
> pilot."*

| variant | hazard recall (any tier) | Δ | V recall | Δ | FA (off) | Δ | cell F1 | Δ |
|---|---|---|---|---|---|---|---|---|
| bright 0.6 (−40 %) | 0.770 ± 0.156 | **−0.011** | 0.804 ± 0.160 | **+0.013** | 0.218 ± 0.156 | −0.093 | 0.422 ± 0.050 | −0.033 |
| **identity** | **0.781 ± 0.089** | — | **0.791 ± 0.100** | — | **0.310 ± 0.306** | — | **0.455 ± 0.010** | — |
| bright 1.4 (+40 %) | 0.737 ± 0.072 | **−0.044** | 0.751 ± 0.060 | **−0.040** | 0.377 ± 0.333 | +0.067 | 0.411 ± 0.032 | −0.044 |
| exp +1 EV | 0.741 ± 0.072 | −0.041 | 0.751 ± 0.073 | −0.040 | 0.382 ± 0.337 | +0.072 | 0.410 ± 0.026 | −0.045 |
| gamma 1.4 | — | **+0.044** | — | **+0.040** | — | — | — | — |

**All four figures are far under 0.1 ⇒ "no photometric augmentation" adopted.**

**FA is roughly 2× more sensitive than recall.** FA rises monotonically b 0.6 → 1.4: 0.218 → 0.377
(span 0.159); exposure moves the same way (−1 EV 0.236 → +1 EV 0.382).

## 2. The mechanism — darkening is a threshold shift, brightening is not

τ* re-fitted on val (**diagnostic only — the main table stays at τ_op = 0.5, approval #1**):

| variant | τ* | cell F1 @ τ* | Δ vs identity | verdict |
|---|---|---|---|---|
| bright 0.6 | 0.33 | 0.4607 | −0.010 | nearly recovered |
| bright 0.8 | 0.46 | 0.4698 | −0.001 | **fully recovered** |
| identity | 0.55 | **0.4704** | — | — |
| bright 1.2 | 0.50 | 0.4557 | −0.015 | partial |
| **bright 1.4** | 0.55 | 0.4215 | **−0.049** | **NOT recovered** |
| gamma 0.7 | 0.44 | 0.4600 | −0.010 | nearly recovered |
| **gamma 1.4** | 0.49 | 0.4727 | **+0.002** | no loss at all |
| **exp −1 EV** | 0.43 | **0.4702** | −0.000 | **fully recovered** |
| exp −0.5 EV | 0.48 | 0.4722 | +0.002 | **fully recovered** |
| exp +0.5 EV | 0.56 | 0.4610 | −0.009 | partial |
| **exp +1 EV** | 0.55 | 0.4229 | **−0.048** | **NOT recovered** |

> At **−1 EV** τ* falls 0.55 → 0.43, and at that τ* the F1 matches the unperturbed value **to the
> fourth decimal (0.4702 vs 0.4704)**. Darkening is a **pure threshold shift**.

> **Only brightening is irreversible.** b1.4 and +1 EV lose −0.049 / −0.048 at **any** τ. Their one
> shared property is **highlight clipping** (`clip(·,0,1)`). **Clipped pixels cannot be recovered.**
> The control that proves it: **gamma 1.4 is the only "darkening" transform with no clipping, and it
> is the only variant whose F1 @ τ* goes UP (+0.002).** The loss comes from clipping, not brightness.

## 3. Pilot rules (verbatim, §5.2)

- **P-1. No over-exposure.** Shoot at correct exposure or **−0.5 EV or lower**. A cut with blown
  highlights is **re-shot**, not post-corrected. *(basis: darkening recovers, Δ −0.000 ~ −0.010;
  brightening does not, −0.048 ~ −0.049)*
- **P-2. Record exposure / EV metadata for every cut**, so τ sensitivity per shooting condition can
  be checked afterwards. *(basis: τ* moves 0.33–0.56 — different lighting, different optimal τ.
  **But this τ is diagnostic; the main table is fixed at τ_op = 0.5, approval #1**)*
- **P-3. At readout, look at FA before recall.** The first symptom of a lighting error is a rise in
  false alarms. *(basis: FA is ~2× more sensitive than recall)*

---

## CAVEAT LINE — must travel with this table

> **"Under 0.1" is a 3-seed MEAN.** Individual seeds reverse sign: s42 is **−0.111** at b1.4 while
> s44 is **+0.022**; s44 is **−0.111** at b0.6 while s42 is **+0.100**. Report the decision as a
> mean-based decision.

> **The seed scatter swallows the FA effect.** Identity val FA is 0.083 / 0.153 / **0.694** across
> seeds (±0.306). The FA change brightness produces (±0.07–0.09) is buried inside that scatter.

> **E and H recall on val are 6-frame denominators** — one frame is 0.167. Do not report a val E or
> H recall as a rate without the denominator.

> **This is a val-only result and cannot speak about test.** Stated in the ledger as a hard
> constraint enforced in code, not a convention.
