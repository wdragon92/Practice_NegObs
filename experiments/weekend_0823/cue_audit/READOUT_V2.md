# READOUT_V2 — CUE-OFF intervention read-out under PREREG amendment A2

**Machine-generated.** `CUEOFF_RESULT.md` (v1) is preserved unchanged; the authored re-adjudication is `CUEOFF_RESULT_v2.md`. Hypotheses, arms, thresholds and primary-leg locks are exactly those of `PREREG_CUEOFF.md` + A1. A2 changes only how the code counts, and every change is a post-hoc correction made after the results were seen -- declared as such here and in every verdict it touches.

tau_op **0.5** · seeds `[42, 43, 44]` · retraining **0** · frozen `runs/v2/{rgb,depth,b2}_s{42,43,44}/best.pt`

```
PRE-REGISTERED DECISION RULE (D36 / R2 sec.5.3-3), A2 COUNTING
  D_cue     = recall_H(A) - recall_H(B)
  D_placebo = recall_H(A) - recall_H(P)
  VOID         :  paired-H < 10      -- no verdict at all (A2-2)
  NO-EFFECT    :  every seed's D_cue == 0  -- own category, power bound printed (A2-1)
  CUE EVIDENCE : (D_cue - D_placebo) >= 0.15  AND  same-sign, >=1 non-zero
  SHORTCUT     :  D_cue < 0.1          AND  same-sign, >=1 non-zero
  otherwise    :  UNDECIDED -- table only
```

## scene12 · stem `260823_cueoff` · label set `lineage`

> **Primary D_cue = D(A, B2)** · placebo ADMISSIBLE  
> GT = the declared-degenerate 50-cell footprint in the `lineage` set (PREREG A1.1; G7 puts the same frames at 50,278 cells in the `twin` set, 1006x). Band `boost_e`.  
> **Rendered mass on the judged frames (A2-5, >=32/255):** A-vs-B1 34.81% of frame · A-vs-B2 5.34% of frame · A-vs-P 3.09% of frame  
> **Placebo/cue ratio:** P/B1 = 0.089 -> **SEVERELY ANTI-CONSERVATIVE** · P/B2 = 0.578 -> **ANTI-CONSERVATIVE**

### arm C — false alarms, against the lineage-off FLOOR (H2)

| model | FA(off) s42/43/44 | FA(off) mean | FA(C) s42/43/44 | FA(C) mean | delta | n frames |
|---|---|---|---|---|---|---|
| rgb | 0.042 / 0.042 / 0.000 | 0.028 | 1.000 / 1.000 / 1.000 | 1.000 | **+0.972** | 24 |
| depth | 0.000 / 0.000 / 0.000 | 0.000 | 0.500 / 0.500 / 0.000 | 0.333 | **+0.333** | 24 |
| b2 | 0.000 / 0.000 / 0.000 | 0.000 | 1.000 / 1.000 / 1.000 | 1.000 | **+1.000** | 24 |

_FA(off) = the lineage hazard-off round (hazard off AND dressing off) evaluated on the same cuts -- the true baseline for arm C. It has been inside `per_frame.csv` since 06:03 and was never printed (R4 F7)._

**H2 verdict for scene12/260823_cueoff/lineage** (PREREG sec.4.4 accepts at FA >= 0.40): rgb 1.000 · depth 0.333 · b2 1.000 -> **ACCEPTED**. (v1 printed the 0.40 baseline under every table and never issued the verdict -- R5 D-8.)

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 0.792 | 0.958 | 0.125 | +0.208 | +0.042 | +0.875 | +0.375 | SAME-SIGN | none (G4-verified) |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.208, +0.042, +0.875 · guard share of the full cue effect = 0%

> ### VERDICT (rgb, primary D_cue = D(A,B2), placebo-corrected): **NO-EFFECT**
> D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

> twin-conditional (twin = arm C, R2 P3 primary metric): **NO-EFFECT** — D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

_secondary D_cue = D(A,B1): **CUE EVIDENCE** — (D_cue +0.375) - (D_placebo +0.000) = +0.375 >= 0.15, D_cue non-zero and 3/3 same sign  (placebo/cue ratio 0.089 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 1.000 | 0.625 | 0.875 | 0.750 | 0.750 | +0.125 | +0.250 | -0.125 | +0.083 | MIXED | none (G4-verified) |
| A vs B1 | 24 | 1.000 | 1.000 | 0.625 | 0.875 | 0.750 | 0.875 | +0.125 | +0.250 | -0.250 | +0.042 | MIXED | none (G4-verified) |
| A vs P | 24 | 1.000 | 1.000 | 0.625 | 1.000 | 1.000 | 0.625 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.000, -0.125 · guard share of the full cue effect = — (D(A,B1) changes sign across seeds, so its sum is not a magnitude and cannot be a denominator -- R5 D-6)

> ### VERDICT (depth, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> seed signs disagree (+0.125, +0.250, -0.125) -- PREREG sec.4.5-4

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue -0.042 < 0.1, non-zero and same-sign (placebo-corrected -0.042)

> **The twin-conditional verdict DISAGREES with the raw recall verdict. PREREG sec.4.4 says the twin-conditional reading wins the body text and the raw one goes to the appendix.**

_secondary D_cue = D(A,B1): **UNDECIDED** — seed signs disagree (+0.125, +0.250, -0.250) -- PREREG sec.4.5-4  (placebo/cue ratio 0.089 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 0.917 | 1.000 | +0.000 | +0.083 | +0.000 | +0.028 | SAME-SIGN | none (G4-verified) |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 0.083 | 0.000 | 0.000 | +0.917 | +1.000 | +1.000 | +0.972 | SAME-SIGN | none (G4-verified) |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 0.667 | 0.792 | 0.875 | +0.333 | +0.208 | +0.125 | +0.222 | SAME-SIGN | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.917, +0.917, +1.000 · guard share of the full cue effect = 3%

> ### VERDICT (b2, primary D_cue = D(A,B2), placebo-corrected): **SHORTCUT**
> D_cue +0.028 < 0.1, non-zero and same-sign (placebo-corrected -0.194)

> twin-conditional (twin = arm C, R2 P3 primary metric): **NO-EFFECT** — D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

> **The twin-conditional verdict DISAGREES with the raw recall verdict. PREREG sec.4.4 says the twin-conditional reading wins the body text and the raw one goes to the appendix.**

_secondary D_cue = D(A,B1): **CUE EVIDENCE** — (D_cue +0.972) - (D_placebo +0.222) = +0.750 >= 0.15, D_cue non-zero and 3/3 same sign  (placebo/cue ratio 0.089 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

## scene17 · stem `260823_cueoff` · label set `lineage`

> **Primary D_cue = D(A, B1)** · placebo ADMISSIBLE  
> A1.2-2 primary placebo-corrected leg. Footprint 65,833 cells, no sidecar oracle. B2 does not exist (no railing in this scene).  
> **Rendered mass on the judged frames (A2-5, >=32/255):** A-vs-B1 29.73% of frame · A-vs-P 16.51% of frame  
> **Placebo/cue ratio:** P/B1 = 0.555 -> **ANTI-CONSERVATIVE**

### arm C — false alarms, against the lineage-off FLOOR (H2)

| model | FA(off) s42/43/44 | FA(off) mean | FA(C) s42/43/44 | FA(C) mean | delta | n frames |
|---|---|---|---|---|---|---|
| rgb | 0.000 / 0.042 / 0.000 | 0.014 | 0.000 / 0.125 / 0.000 | 0.042 | **+0.028** | 24 |
| depth | 0.125 / 0.000 / 0.000 | 0.042 | 0.125 / 0.000 / 0.000 | 0.042 | **+0.000** | 24 |
| b2 | 0.042 / 0.000 / 0.000 | 0.014 | 0.125 / 0.000 / 0.042 | 0.056 | **+0.042** | 24 |

_FA(off) = the lineage hazard-off round (hazard off AND dressing off) evaluated on the same cuts -- the true baseline for arm C. It has been inside `per_frame.csv` since 06:03 and was never printed (R4 F7)._

**H2 verdict for scene17/260823_cueoff/lineage** (PREREG sec.4.4 accepts at FA >= 0.40): rgb 0.042 · depth 0.042 · b2 0.056 -> **REJECTED**. (v1 printed the 0.40 baseline under every table and never issued the verdict -- R5 D-8.)

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 0.750 | 0.917 | 1.000 | +0.250 | +0.083 | +0.000 | +0.111 | SAME-SIGN | none (G4-verified) |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (rgb, primary D_cue = D(A,B1), placebo-corrected): **UNDECIDED**
> (D_cue +0.111) - (D_placebo +0.000) = +0.111: between 0.1 and 0.15

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.083 < 0.1, non-zero and same-sign (placebo-corrected +0.083)

> **The twin-conditional verdict DISAGREES with the raw recall verdict. PREREG sec.4.4 says the twin-conditional reading wins the body text and the raw one goes to the appendix.**

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 0.875 | 0.875 | 1.000 | 0.875 | 0.875 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |
| A vs P | 24 | 1.000 | 0.875 | 0.875 | 1.000 | 0.875 | 0.875 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (depth, primary D_cue = D(A,B1), placebo-corrected): **NO-EFFECT**
> D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

> twin-conditional (twin = arm C, R2 P3 primary metric): **NO-EFFECT** — D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (b2, primary D_cue = D(A,B1), placebo-corrected): **NO-EFFECT**
> D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

> twin-conditional (twin = arm C, R2 P3 primary metric): **NO-EFFECT** — D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

## scene20 · stem `260823_cueoff` · label set `lineage`

> **Primary D_cue = D(A, B2)** · placebo ADMISSIBLE  
> A2-6: placebo RESTORED (post-hoc). PREREG sec.3.3 excluded it on a furniture measurement that is correct but describes objects arm P does not remove; the rendered arm P removes backdrop E1/E2.  
> **Rendered mass on the judged frames (A2-5, >=32/255):** A-vs-B1 32.37% of frame · A-vs-B2 8.38% of frame · A-vs-P 7.61% of frame  
> **Placebo/cue ratio:** P/B1 = 0.235 -> **SEVERELY ANTI-CONSERVATIVE** · P/B2 = 0.909 -> **MATCHED**

### arm C — false alarms, against the lineage-off FLOOR (H2)

| model | FA(off) s42/43/44 | FA(off) mean | FA(C) s42/43/44 | FA(C) mean | delta | n frames |
|---|---|---|---|---|---|---|
| rgb | 0.000 / 0.667 / 0.083 | 0.250 | 0.083 / 1.000 / 0.000 | 0.361 | **+0.111** | 24 |
| depth | 0.000 / 0.000 / 0.000 | 0.000 | 0.000 / 0.000 / 0.000 | 0.000 | **+0.000** | 24 |
| b2 | 0.208 / 0.042 / 0.125 | 0.125 | 0.458 / 0.083 / 0.000 | 0.181 | **+0.056** | 24 |

_FA(off) = the lineage hazard-off round (hazard off AND dressing off) evaluated on the same cuts -- the true baseline for arm C. It has been inside `per_frame.csv` since 06:03 and was never printed (R4 F7)._

**H2 verdict for scene20/260823_cueoff/lineage** (PREREG sec.4.4 accepts at FA >= 0.40): rgb 0.361 · depth 0.000 · b2 0.181 -> **REJECTED**. (v1 printed the 0.40 baseline under every table and never issued the verdict -- R5 D-8.)

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | +0.667 | +0.000 | +0.000 | +0.222 | SAME-SIGN | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.167 | 0.000 | +1.000 | +0.833 | +1.000 | +0.944 | SAME-SIGN | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.833 | +0.000 | +0.000 | +0.167 | +0.056 | SAME-SIGN | none (G4-verified) **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.333, +0.833, +1.000 · guard share of the full cue effect = 24%

> ### VERDICT (rgb, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.235 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.000, +0.000 · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (depth, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.235 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.333 | 0.333 | +1.000 | +0.667 | +0.667 | +0.778 | SAME-SIGN | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | +1.000 | +1.000 | +1.000 | +1.000 | SAME-SIGN | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.667 | +0.000 | +0.000 | +0.333 | +0.111 | SAME-SIGN | none (G4-verified) **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.333, +0.333 · guard share of the full cue effect = 78%

> ### VERDICT (b2, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.235 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

## scene12 · stem `260823_cueoff2` · label set `lineage`

> **Primary D_cue = D(A, B2)** · placebo ADMISSIBLE  
> GT = the declared-degenerate 50-cell footprint in the `lineage` set (PREREG A1.1). Band `boost_e2` -- a DIFFERENT round from `260823_cueoff`, with its own masses; v1 printed boost_e's constants here (R5 D-5).  
> **Rendered mass on the judged frames (A2-5, >=32/255):** A-vs-B1 38.30% of frame · A-vs-B2 6.16% of frame · A-vs-P 2.47% of frame  
> **Placebo/cue ratio:** P/B1 = 0.065 -> **SEVERELY ANTI-CONSERVATIVE** · P/B2 = 0.401 -> **ANTI-CONSERVATIVE**

### arm C — false alarms, against the lineage-off FLOOR (H2)

| model | FA(off) s42/43/44 | FA(off) mean | FA(C) s42/43/44 | FA(C) mean | delta | n frames |
|---|---|---|---|---|---|---|
| rgb | 0.000 / 0.000 / 0.000 | 0.000 | 1.000 / 1.000 / 1.000 | 1.000 | **+1.000** | 24 |
| depth | 0.000 / 0.000 / 0.000 | 0.000 | 0.375 / 0.375 / 0.000 | 0.250 | **+0.250** | 24 |
| b2 | 0.000 / 0.000 / 0.000 | 0.000 | 1.000 / 0.875 / 1.000 | 0.958 | **+0.958** | 24 |

_FA(off) = the lineage hazard-off round (hazard off AND dressing off) evaluated on the same cuts -- the true baseline for arm C. It has been inside `per_frame.csv` since 06:03 and was never printed (R4 F7)._

**H2 verdict for scene12/260823_cueoff2/lineage** (PREREG sec.4.4 accepts at FA >= 0.40): rgb 1.000 · depth 0.250 · b2 0.958 -> **ACCEPTED**. (v1 printed the 0.40 baseline under every table and never issued the verdict -- R5 D-8.)

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 0.417 | 1.000 | 0.458 | +0.583 | +0.000 | +0.542 | +0.375 | SAME-SIGN | none (G4-verified) |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 0.875 | 1.000 | 1.000 | +0.125 | +0.000 | +0.000 | +0.042 | SAME-SIGN | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.583, +0.000, +0.542 · guard share of the full cue effect = 0%

> ### VERDICT (rgb, primary D_cue = D(A,B2), placebo-corrected): **NO-EFFECT**
> D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

> twin-conditional (twin = arm C, R2 P3 primary metric): **NO-EFFECT** — D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

_secondary D_cue = D(A,B1): **CUE EVIDENCE** — (D_cue +0.375) - (D_placebo +0.042) = +0.333 >= 0.15, D_cue non-zero and 3/3 same sign  (placebo/cue ratio 0.065 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 1.000 | 0.875 | 1.000 | 1.000 | 0.750 | +0.000 | +0.000 | +0.125 | +0.042 | SAME-SIGN | none (G4-verified) |
| A vs B1 | 24 | 1.000 | 1.000 | 0.875 | 1.000 | 1.000 | 0.750 | +0.000 | +0.000 | +0.125 | +0.042 | SAME-SIGN | none (G4-verified) |
| A vs P | 24 | 1.000 | 1.000 | 0.875 | 0.875 | 1.000 | 0.875 | +0.125 | +0.000 | +0.000 | +0.042 | SAME-SIGN | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.000, +0.000 · guard share of the full cue effect = 100%

> ### VERDICT (depth, primary D_cue = D(A,B2), placebo-corrected): **SHORTCUT**
> D_cue +0.042 < 0.1, non-zero and same-sign (placebo-corrected +0.000)

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.042 < 0.1, non-zero and same-sign (placebo-corrected +0.000)

_secondary D_cue = D(A,B1): **SHORTCUT** — D_cue +0.042 < 0.1, non-zero and same-sign (placebo-corrected +0.000)  (placebo/cue ratio 0.065 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 0.833 | 1.000 | 0.875 | 0.708 | 0.875 | +0.125 | +0.125 | +0.125 | +0.125 | SAME-SIGN | none (G4-verified) |
| A vs B1 | 24 | 1.000 | 0.833 | 1.000 | 0.417 | 0.292 | 0.250 | +0.583 | +0.542 | +0.750 | +0.625 | SAME-SIGN | none (G4-verified) |
| A vs P | 24 | 1.000 | 0.833 | 1.000 | 0.833 | 0.708 | 0.833 | +0.167 | +0.125 | +0.167 | +0.153 | SAME-SIGN | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.458, +0.417, +0.625 · guard share of the full cue effect = 20%

> ### VERDICT (b2, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> (D_cue +0.125) - (D_placebo +0.153) = -0.028: between 0.1 and 0.15

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.028 < 0.1, non-zero and same-sign (placebo-corrected +0.042)

> **The twin-conditional verdict DISAGREES with the raw recall verdict. PREREG sec.4.4 says the twin-conditional reading wins the body text and the raw one goes to the appendix.**

_secondary D_cue = D(A,B1): **CUE EVIDENCE** — (D_cue +0.625) - (D_placebo +0.153) = +0.472 >= 0.15, D_cue non-zero and 3/3 same sign  (placebo/cue ratio 0.065 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

## scene12 · stem `260823_cueoff` · label set `twin`

> **Primary D_cue = D(A, B2)** · placebo ADMISSIBLE  
> GT = the declared-degenerate 50-cell footprint in the `lineage` set (PREREG A1.1; G7 puts the same frames at 50,278 cells in the `twin` set, 1006x). Band `boost_e`.  
> **Rendered mass on the judged frames (A2-5, >=32/255):** A-vs-B1 34.81% of frame · A-vs-B2 5.34% of frame · A-vs-P 3.09% of frame  
> **Placebo/cue ratio:** P/B1 = 0.089 -> **SEVERELY ANTI-CONSERVATIVE** · P/B2 = 0.578 -> **ANTI-CONSERVATIVE**

### arm C — false alarms, against the lineage-off FLOOR (H2)

| model | FA(off) s42/43/44 | FA(off) mean | FA(C) s42/43/44 | FA(C) mean | delta | n frames |
|---|---|---|---|---|---|---|
| rgb | — | — | 1.000 / 1.000 / 1.000 | 1.000 | — | 24 |
| depth | — | — | 0.500 / 0.500 / 0.000 | 0.333 | — | 24 |
| b2 | — | — | 1.000 / 1.000 / 1.000 | 1.000 | — | 24 |

_FA(off) suppressed: in the `twin` label set the OFF round IS arm C, so the floor would be the same number as the FA (A2-3)._

**H2 verdict for scene12/260823_cueoff/twin** (PREREG sec.4.4 accepts at FA >= 0.40): rgb 1.000 · depth 0.333 · b2 1.000 -> **ACCEPTED**. (v1 printed the 0.40 baseline under every table and never issued the verdict -- R5 D-8.)

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (rgb, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.089 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (depth, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.089 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (b2, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.089 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

## scene17 · stem `260823_cueoff` · label set `twin`

> **FOLDED (A2-7).** Every judged number in this block is byte-identical to `scene17 · 260823_cueoff · lineage` above: the two label sets tier and score these frames identically, so this is not an independent replication and must not be counted as one.

> **Primary D_cue = D(A, B1)** · placebo ADMISSIBLE  
> A1.2-2 primary placebo-corrected leg. Footprint 65,833 cells, no sidecar oracle. B2 does not exist (no railing in this scene).  
> **Rendered mass on the judged frames (A2-5, >=32/255):** A-vs-B1 29.73% of frame · A-vs-P 16.51% of frame  
> **Placebo/cue ratio:** P/B1 = 0.555 -> **ANTI-CONSERVATIVE**

### arm C — false alarms, against the lineage-off FLOOR (H2)

| model | FA(off) s42/43/44 | FA(off) mean | FA(C) s42/43/44 | FA(C) mean | delta | n frames |
|---|---|---|---|---|---|---|
| rgb | — | — | 0.000 / 0.125 / 0.000 | 0.042 | — | 24 |
| depth | — | — | 0.125 / 0.000 / 0.000 | 0.042 | — | 24 |
| b2 | — | — | 0.125 / 0.000 / 0.042 | 0.056 | — | 24 |

_FA(off) suppressed: in the `twin` label set the OFF round IS arm C, so the floor would be the same number as the FA (A2-3)._

**H2 verdict for scene17/260823_cueoff/twin** (PREREG sec.4.4 accepts at FA >= 0.40): rgb 0.042 · depth 0.042 · b2 0.056 -> **REJECTED**. (v1 printed the 0.40 baseline under every table and never issued the verdict -- R5 D-8.)

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 0.750 | 0.917 | 1.000 | +0.250 | +0.083 | +0.000 | +0.111 | SAME-SIGN | none (G4-verified) |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (rgb, primary D_cue = D(A,B1), placebo-corrected): **UNDECIDED**
> (D_cue +0.111) - (D_placebo +0.000) = +0.111: between 0.1 and 0.15

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.083 < 0.1, non-zero and same-sign (placebo-corrected +0.083)

> **The twin-conditional verdict DISAGREES with the raw recall verdict. PREREG sec.4.4 says the twin-conditional reading wins the body text and the raw one goes to the appendix.**

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 0.875 | 0.875 | 1.000 | 0.875 | 0.875 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |
| A vs P | 24 | 1.000 | 0.875 | 0.875 | 1.000 | 0.875 | 0.875 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (depth, primary D_cue = D(A,B1), placebo-corrected): **NO-EFFECT**
> D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

> twin-conditional (twin = arm C, R2 P3 primary metric): **NO-EFFECT** — D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (b2, primary D_cue = D(A,B1), placebo-corrected): **NO-EFFECT**
> D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

> twin-conditional (twin = arm C, R2 P3 primary metric): **NO-EFFECT** — D_cue = (+0.000, +0.000, +0.000) -- the metric did not move on a single frame in any seed. 0 flips in 24 paired frames bounds the per-frame flip rate at p95 = 0.117 (one-sided 95%). The pre-registered SHORTCUT threshold is 0.1, which this bound DOES NOT RESOLVE (0.117 > 0.1): H0-consistent but under-powered. Seeds do not enlarge n -- all three read the same frames.

## scene20 · stem `260823_cueoff` · label set `twin`

> **FOLDED (A2-7).** Every judged number in this block is byte-identical to `scene20 · 260823_cueoff · lineage` above: the two label sets tier and score these frames identically, so this is not an independent replication and must not be counted as one.

> **Primary D_cue = D(A, B2)** · placebo ADMISSIBLE  
> A2-6: placebo RESTORED (post-hoc). PREREG sec.3.3 excluded it on a furniture measurement that is correct but describes objects arm P does not remove; the rendered arm P removes backdrop E1/E2.  
> **Rendered mass on the judged frames (A2-5, >=32/255):** A-vs-B1 32.37% of frame · A-vs-B2 8.38% of frame · A-vs-P 7.61% of frame  
> **Placebo/cue ratio:** P/B1 = 0.235 -> **SEVERELY ANTI-CONSERVATIVE** · P/B2 = 0.909 -> **MATCHED**

### arm C — false alarms, against the lineage-off FLOOR (H2)

| model | FA(off) s42/43/44 | FA(off) mean | FA(C) s42/43/44 | FA(C) mean | delta | n frames |
|---|---|---|---|---|---|---|
| rgb | — | — | 0.083 / 1.000 / 0.000 | 0.361 | — | 24 |
| depth | — | — | 0.000 / 0.000 / 0.000 | 0.000 | — | 24 |
| b2 | — | — | 0.458 / 0.083 / 0.000 | 0.181 | — | 24 |

_FA(off) suppressed: in the `twin` label set the OFF round IS arm C, so the floor would be the same number as the FA (A2-3)._

**H2 verdict for scene20/260823_cueoff/twin** (PREREG sec.4.4 accepts at FA >= 0.40): rgb 0.361 · depth 0.000 · b2 0.181 -> **REJECTED**. (v1 printed the 0.40 baseline under every table and never issued the verdict -- R5 D-8.)

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | +0.667 | +0.000 | +0.000 | +0.222 | SAME-SIGN | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.167 | 0.000 | +1.000 | +0.833 | +1.000 | +0.944 | SAME-SIGN | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.833 | +0.000 | +0.000 | +0.167 | +0.056 | SAME-SIGN | none (G4-verified) **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.333, +0.833, +1.000 · guard share of the full cue effect = 24%

> ### VERDICT (rgb, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.235 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | NO-EFFECT | none (G4-verified) **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.000, +0.000 · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (depth, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.235 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.333 | 0.333 | +1.000 | +0.667 | +0.667 | +0.778 | SAME-SIGN | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | +1.000 | +1.000 | +1.000 | +1.000 | SAME-SIGN | {'none_in_fov->H': 9} **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.667 | +0.000 | +0.000 | +0.333 | +0.111 | SAME-SIGN | none (G4-verified) **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.333, +0.333 · guard share of the full cue effect = 78%

> ### VERDICT (b2, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 6 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.235 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

## scene12 · stem `260823_cueoff2` · label set `twin`

> **Primary D_cue = D(A, B2)** · placebo ADMISSIBLE  
> GT = the declared-degenerate 50-cell footprint in the `lineage` set (PREREG A1.1). Band `boost_e2` -- a DIFFERENT round from `260823_cueoff`, with its own masses; v1 printed boost_e's constants here (R5 D-5).  
> **Rendered mass on the judged frames (A2-5, >=32/255):** A-vs-B1 38.30% of frame · A-vs-B2 6.16% of frame · A-vs-P 2.47% of frame  
> **Placebo/cue ratio:** P/B1 = 0.065 -> **SEVERELY ANTI-CONSERVATIVE** · P/B2 = 0.401 -> **ANTI-CONSERVATIVE**

### arm C — false alarms, against the lineage-off FLOOR (H2)

| model | FA(off) s42/43/44 | FA(off) mean | FA(C) s42/43/44 | FA(C) mean | delta | n frames |
|---|---|---|---|---|---|---|
| rgb | — | — | 1.000 / 1.000 / 1.000 | 1.000 | — | 24 |
| depth | — | — | 0.375 / 0.375 / 0.000 | 0.250 | — | 24 |
| b2 | — | — | 1.000 / 0.875 / 1.000 | 0.958 | — | 24 |

_FA(off) suppressed: in the `twin` label set the OFF round IS arm C, so the floor would be the same number as the FA (A2-3)._

**H2 verdict for scene12/260823_cueoff2/twin** (PREREG sec.4.4 accepts at FA >= 0.40): rgb 1.000 · depth 0.250 · b2 0.958 -> **ACCEPTED**. (v1 printed the 0.40 baseline under every table and never issued the verdict -- R5 D-8.)

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | {'V->H': 54} **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (rgb, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.065 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | {'V->H': 54} **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (depth, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.065 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | sign class | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | {'V->H': 54} **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | EMPTY | none (G4-verified) **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = — (|sum D_B1| < 0.05 -- a share of a near-zero denominator is not a share -- R5 D-6)

> ### VERDICT (b2, primary D_cue = D(A,B2), placebo-corrected): **VOID**
> paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

> twin-conditional (twin = arm C, R2 P3 primary metric): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).

_secondary D_cue = D(A,B1): **VOID** — paired-H 0 < 10 -- PREREG sec.4.5-3 says this scene is NOT JUDGED. No verdict is issued (A2-2; v1 issued one anyway).  (placebo/cue ratio 0.065 = SEVERELY ANTI-CONSERVATIVE; PREREG sec.3.1 forbids promoting this leg to decisive evidence)_


## Verdict census (A2 counting)

| population | CUE EVIDENCE | SHORTCUT | NO-EFFECT | UNDECIDED | VOID | n |
|---|---|---|---|---|---|---|
| primary, all blocks | 0 | 2 | 6 | 4 | 12 | 24 |
| primary, folded blocks removed | 0 | 2 | 4 | 3 | 9 | 18 |
| primary, non-VOID only | 0 | 2 | 6 | 4 | 0 | 12 |
| secondary (promotion forbidden) | 4 | 1 | 0 | 1 | 12 | 18 |
| twin-conditional | 0 | 5 | 7 | 0 | 12 | 24 |

_v1 reported 5 SHORTCUT verdicts in the primary lineage leg. All five were exactly (0.000, 0.000, 0.000) and reached SHORTCUT only through `same_sign((0,0,0)) == True`. Under A2-1 they are NO-EFFECT with an explicit power bound; under A2-2 the scene20 ones are VOID as well._

