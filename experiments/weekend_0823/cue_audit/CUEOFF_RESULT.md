# CUEOFF_RESULT — CUE-OFF intervention read-out  ·  **v1, SUPERSEDED**

> # ⚠ SUPERSEDED BY `CUEOFF_RESULT_v2.md` (2026-08-23, PREREG amendment A2)
>
> **This file is preserved unedited as the record of what was reported at 06:03 on
> 2026-08-23 and what decision D46 was taken on. Do not cite a number from it.**
> Red-team waves R4 and R5 and decision D49 found the following defects in the
> instrument that produced it. None of them is an arithmetic error — R5 re-computed
> 15 spot values and a wide sweep and everything matched to four decimals — all of
> them are counting and reporting defects:
>
> 1. **Five SHORTCUT verdicts here are `(0.000, 0.000, 0.000)`** and reached that
>    label only because `same_sign((0,0,0))` returned `True`. In v2 they are
>    NO-EFFECT, printed with the power bound that shows this sample cannot resolve
>    its own 0.10 threshold (p95 = 0.117 at n = 24).
> 2. **Twelve verdict blocks were issued for scene20**, whose paired-H = 6 < 10 had
>    already voided it under PREREG §4.5-3. The table rows said VOID; the verdicts
>    underneath them did not. In v2 the gate is inside the verdict.
> 3. **The placebo admissibility grades quoted here come from AABB silhouette upper
>    bounds and all four are wrong**, three anti-conservatively. Measured on the
>    renders, no leg in this study is conservative. See A2-5.
> 4. **scene20's placebo was excluded on a true measurement of the wrong objects.**
>    The rendered arm P removes backdrop blocks E1/E2, not the mesa furniture §3.3
>    measured at 0 px. See A2-6.
> 5. **The hazard-off false-alarm floor was never printed**, so arm C's FA appears
>    here as an absolute number. With the floor, scene12 reads .028 → 1.000 and
>    scene17 reads .014 → .042. See A2-3.
> 6. **G2 was reported as 8 failures and adjudicated from one case** (D44). All
>    eight are adjudicated individually in v2.
> 7. **G4, G5 and G2's `polar_gt` clause had never executed** — `load_labels` was
>    looking for a filename the labeller does not write — so every
>    `tier migration | none` printed below is an unverified default.
> 8. **Half of this file is duplicated or empty**: scene17/scene20 `twin` blocks are
>    byte-identical copies of their `lineage` blocks, and both scene12 `twin` blocks
>    are all-`nan`.
>
> The re-adjudication of every scene under A2 is `CUEOFF_RESULT_v2.md`; the machine
> tables are `READOUT_V2.md`; the amendment is `PREREG_CUEOFF.md` § AMENDMENT A2.


Pre-registration: `PREREG_CUEOFF.md` (+ amendment A1). Every threshold below was fixed before the first cut was rendered; this file only substitutes numbers into it.

tau_op **0.5** · seeds `[42, 43, 44]` · retraining **0** · frozen `runs/v2/{rgb,depth,b2}_s{42,43,44}/best.pt`

```
PRE-REGISTERED DECISION RULE (D36 / R2 sec.5.3-3)
  D_cue     = recall_H(A) - recall_H(B)
  D_placebo = recall_H(A) - recall_H(P)
  CUE EVIDENCE : (D_cue - D_placebo) >= 0.15  AND  3/3 seeds same sign
  SHORTCUT     :  D_cue < 0.1          AND  3/3 seeds same sign
  otherwise    :  UNDECIDED -- table only
  paired-H must be >= 10; effects below 0.1 are not interpreted
```

## scene12 · stem `260823_cueoff` · label set `lineage`

> **Primary D_cue = D(A, B2)** · placebo ADMISSIBLE  
> GT = the declared-degenerate 50-cell footprint in the `lineage` set (PREREG amendment A1.1); placebo is 12-30x the guard's pixel mass = conservative. D(A,B1) is SECONDARY and anti-conservative.

### arm C — false alarms on the cue vocabulary alone (H2)

| model | s42 | s43 | s44 | mean | n frames |
|---|---|---|---|---|---|
| rgb | 1.000 | 1.000 | 1.000 | 1.000 | 24 |
| depth | 0.500 | 0.500 | 0.000 | 0.333 | 24 |
| b2 | 1.000 | 1.000 | 1.000 | 1.000 | 24 |

_H2 accepted at FA >= 0.40 (PREREG sec.4.4); compare sceneC2 new-off FA .681._

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 0.792 | 0.958 | 0.125 | +0.208 | +0.042 | +0.875 | +0.375 | yes | none |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.208, +0.042, +0.875 · guard share of the full cue effect = 0%

> ### VERDICT (rgb, primary D_cue = D(A,B2), placebo-corrected): **SHORTCUT**
> D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

_secondary D_cue = D(A,B1): **CUE EVIDENCE** — (D_cue +0.375) - (D_placebo +0.000) = +0.375 >= 0.15 and 3/3 same sign  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 1.000 | 0.625 | 0.875 | 0.750 | 0.750 | +0.125 | +0.250 | -0.125 | +0.083 | **no** | none |
| A vs B1 | 24 | 1.000 | 1.000 | 0.625 | 0.875 | 0.750 | 0.875 | +0.125 | +0.250 | -0.250 | +0.042 | **no** | none |
| A vs P | 24 | 1.000 | 1.000 | 0.625 | 1.000 | 1.000 | 0.625 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.000, -0.125 · guard share of the full cue effect = 200%

> ### VERDICT (depth, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> seed signs disagree (+0.125, +0.250, -0.125) -- PREREG sec.4.5-4

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — seed signs disagree (+0.000, +0.000, -0.125) -- PREREG sec.4.5-4

_secondary D_cue = D(A,B1): **UNDECIDED** — seed signs disagree (+0.125, +0.250, -0.250) -- PREREG sec.4.5-4  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 0.917 | 1.000 | +0.000 | +0.083 | +0.000 | +0.028 | **no** | none |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 0.083 | 0.000 | 0.000 | +0.917 | +1.000 | +1.000 | +0.972 | yes | none |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 0.667 | 0.792 | 0.875 | +0.333 | +0.208 | +0.125 | +0.222 | yes | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.917, +0.917, +1.000 · guard share of the full cue effect = 3%

> ### VERDICT (b2, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> seed signs disagree (+0.000, +0.083, +0.000) -- PREREG sec.4.5-4

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

> **The twin-conditional verdict DISAGREES with the raw recall verdict. PREREG sec.4.4 says the twin-conditional reading wins the body text and the raw one goes to the appendix.**

_secondary D_cue = D(A,B1): **CUE EVIDENCE** — (D_cue +0.972) - (D_placebo +0.222) = +0.750 >= 0.15 and 3/3 same sign  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

## scene17 · stem `260823_cueoff` · label set `lineage`

> **Primary D_cue = D(A, B1)** · placebo ADMISSIBLE  
> primary placebo-corrected leg (A1.2-2). Footprint 65,833 cells, no sidecar oracle, placebo ~18x the cue mass = strongly conservative.

### arm C — false alarms on the cue vocabulary alone (H2)

| model | s42 | s43 | s44 | mean | n frames |
|---|---|---|---|---|---|
| rgb | 0.000 | 0.125 | 0.000 | 0.042 | 24 |
| depth | 0.125 | 0.000 | 0.000 | 0.042 | 24 |
| b2 | 0.125 | 0.000 | 0.042 | 0.056 | 24 |

_H2 accepted at FA >= 0.40 (PREREG sec.4.4); compare sceneC2 new-off FA .681._

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 0.750 | 0.917 | 1.000 | +0.250 | +0.083 | +0.000 | +0.111 | **no** | none |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (rgb, primary D_cue = D(A,B1), placebo-corrected): **UNDECIDED**
> seed signs disagree (+0.250, +0.083, +0.000) -- PREREG sec.4.5-4

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — seed signs disagree (+0.250, +0.000, +0.000) -- PREREG sec.4.5-4

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 0.875 | 0.875 | 1.000 | 0.875 | 0.875 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |
| A vs P | 24 | 1.000 | 0.875 | 0.875 | 1.000 | 0.875 | 0.875 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (depth, primary D_cue = D(A,B1), placebo-corrected): **SHORTCUT**
> D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (b2, primary D_cue = D(A,B1), placebo-corrected): **SHORTCUT**
> D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

## scene20 · stem `260823_cueoff` · label set `lineage`

> **Primary D_cue = D(A, B2)** · placebo **NOT ADMISSIBLE**  
> NO admissible placebo (PREREG sec.3.3): every piece of mesa furniture measures 0 px in 6/6 H frames. Reported EXPLORATORY; contributes via B2 surgery and arm-C FA.

### arm C — false alarms on the cue vocabulary alone (H2)

| model | s42 | s43 | s44 | mean | n frames |
|---|---|---|---|---|---|
| rgb | 0.083 | 1.000 | 0.000 | 0.361 | 24 |
| depth | 0.000 | 0.000 | 0.000 | 0.000 | 24 |
| b2 | 0.458 | 0.083 | 0.000 | 0.181 | 24 |

_H2 accepted at FA >= 0.40 (PREREG sec.4.4); compare sceneC2 new-off FA .681._

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | +0.667 | +0.000 | +0.000 | +0.222 | **no** | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.167 | 0.000 | +1.000 | +0.833 | +1.000 | +0.944 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.833 | +0.000 | +0.000 | +0.167 | +0.056 | **no** | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.333, +0.833, +1.000 · guard share of the full cue effect = 24%

> ### VERDICT (rgb, primary D_cue = D(A,B2), NO placebo): **UNDECIDED**
> seed signs disagree (+0.667, +0.000, +0.000) -- PREREG sec.4.5-4

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — seed signs disagree (+0.667, +0.000, +0.000) -- PREREG sec.4.5-4

_secondary D_cue = D(A,B1): **UNDECIDED** — D_cue +0.944 but no admissible placebo, so the cue-evidence branch cannot be evaluated_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.000, +0.000 · guard share of the full cue effect = —

> ### VERDICT (depth, primary D_cue = D(A,B2), NO placebo): **SHORTCUT**
> D_cue +0.000 < 0.1 and 3/3 same sign (no placebo available -- exploratory)

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (no placebo available -- exploratory)

_secondary D_cue = D(A,B1): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (no placebo available -- exploratory)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.333 | 0.333 | +1.000 | +0.667 | +0.667 | +0.778 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | +1.000 | +1.000 | +1.000 | +1.000 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.667 | +0.000 | +0.000 | +0.333 | +0.111 | **no** | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.333, +0.333 · guard share of the full cue effect = 78%

> ### VERDICT (b2, primary D_cue = D(A,B2), NO placebo): **UNDECIDED**
> D_cue +0.778 but no admissible placebo, so the cue-evidence branch cannot be evaluated

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — D_cue +0.778 but no admissible placebo, so the cue-evidence branch cannot be evaluated

_secondary D_cue = D(A,B1): **UNDECIDED** — D_cue +1.000 but no admissible placebo, so the cue-evidence branch cannot be evaluated_

## scene12 · stem `260823_cueoff2` · label set `lineage`

> **Primary D_cue = D(A, B2)** · placebo ADMISSIBLE  
> GT = the declared-degenerate 50-cell footprint in the `lineage` set (PREREG amendment A1.1); placebo is 12-30x the guard's pixel mass = conservative. D(A,B1) is SECONDARY and anti-conservative.

### arm C — false alarms on the cue vocabulary alone (H2)

| model | s42 | s43 | s44 | mean | n frames |
|---|---|---|---|---|---|
| rgb | 1.000 | 1.000 | 1.000 | 1.000 | 24 |
| depth | 0.375 | 0.375 | 0.000 | 0.250 | 24 |
| b2 | 1.000 | 0.875 | 1.000 | 0.958 | 24 |

_H2 accepted at FA >= 0.40 (PREREG sec.4.4); compare sceneC2 new-off FA .681._

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 0.417 | 1.000 | 0.458 | +0.583 | +0.000 | +0.542 | +0.375 | **no** | none |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 0.875 | 1.000 | 1.000 | +0.125 | +0.000 | +0.000 | +0.042 | **no** | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.583, +0.000, +0.542 · guard share of the full cue effect = 0%

> ### VERDICT (rgb, primary D_cue = D(A,B2), placebo-corrected): **SHORTCUT**
> D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected -0.042)

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

_secondary D_cue = D(A,B1): **UNDECIDED** — seed signs disagree (+0.583, +0.000, +0.542) -- PREREG sec.4.5-4  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 1.000 | 0.875 | 1.000 | 1.000 | 0.750 | +0.000 | +0.000 | +0.125 | +0.042 | **no** | none |
| A vs B1 | 24 | 1.000 | 1.000 | 0.875 | 1.000 | 1.000 | 0.750 | +0.000 | +0.000 | +0.125 | +0.042 | **no** | none |
| A vs P | 24 | 1.000 | 1.000 | 0.875 | 0.875 | 1.000 | 0.875 | +0.125 | +0.000 | +0.000 | +0.042 | **no** | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.000, +0.000 · guard share of the full cue effect = 100%

> ### VERDICT (depth, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> seed signs disagree (+0.000, +0.000, +0.125) -- PREREG sec.4.5-4

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — seed signs disagree (+0.000, +0.000, +0.125) -- PREREG sec.4.5-4

_secondary D_cue = D(A,B1): **UNDECIDED** — seed signs disagree (+0.000, +0.000, +0.125) -- PREREG sec.4.5-4  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 24 | 1.000 | 0.833 | 1.000 | 0.875 | 0.708 | 0.875 | +0.125 | +0.125 | +0.125 | +0.125 | yes | none |
| A vs B1 | 24 | 1.000 | 0.833 | 1.000 | 0.417 | 0.292 | 0.250 | +0.583 | +0.542 | +0.750 | +0.625 | yes | none |
| A vs P | 24 | 1.000 | 0.833 | 1.000 | 0.833 | 0.708 | 0.833 | +0.167 | +0.125 | +0.167 | +0.153 | yes | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.458, +0.417, +0.625 · guard share of the full cue effect = 20%

> ### VERDICT (b2, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> (D_cue +0.125) - (D_placebo +0.153) = -0.028: between 0.1 and 0.15

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — seed signs disagree (+0.000, +0.083, +0.000) -- PREREG sec.4.5-4

_secondary D_cue = D(A,B1): **CUE EVIDENCE** — (D_cue +0.625) - (D_placebo +0.153) = +0.472 >= 0.15 and 3/3 same sign  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

## scene12 · stem `260823_cueoff` · label set `twin`

> **Primary D_cue = D(A, B2)** · placebo ADMISSIBLE  
> GT = the declared-degenerate 50-cell footprint in the `lineage` set (PREREG amendment A1.1); placebo is 12-30x the guard's pixel mass = conservative. D(A,B1) is SECONDARY and anti-conservative.

### arm C — false alarms on the cue vocabulary alone (H2)

| model | s42 | s43 | s44 | mean | n frames |
|---|---|---|---|---|---|
| rgb | 1.000 | 1.000 | 1.000 | 1.000 | 24 |
| depth | 0.500 | 0.500 | 0.000 | 0.333 | 24 |
| b2 | 1.000 | 1.000 | 1.000 | 1.000 | 24 |

_H2 accepted at FA >= 0.40 (PREREG sec.4.4); compare sceneC2 new-off FA .681._

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (rgb, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> only 0/3 seeds available

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — only 0/3 seeds available

_secondary D_cue = D(A,B1): **UNDECIDED** — only 0/3 seeds available  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (depth, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> only 0/3 seeds available

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — only 0/3 seeds available

_secondary D_cue = D(A,B1): **UNDECIDED** — only 0/3 seeds available  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (b2, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> only 0/3 seeds available

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — only 0/3 seeds available

_secondary D_cue = D(A,B1): **UNDECIDED** — only 0/3 seeds available  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

## scene17 · stem `260823_cueoff` · label set `twin`

> **Primary D_cue = D(A, B1)** · placebo ADMISSIBLE  
> primary placebo-corrected leg (A1.2-2). Footprint 65,833 cells, no sidecar oracle, placebo ~18x the cue mass = strongly conservative.

### arm C — false alarms on the cue vocabulary alone (H2)

| model | s42 | s43 | s44 | mean | n frames |
|---|---|---|---|---|---|
| rgb | 0.000 | 0.125 | 0.000 | 0.042 | 24 |
| depth | 0.125 | 0.000 | 0.000 | 0.042 | 24 |
| b2 | 0.125 | 0.000 | 0.042 | 0.056 | 24 |

_H2 accepted at FA >= 0.40 (PREREG sec.4.4); compare sceneC2 new-off FA .681._

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 0.750 | 0.917 | 1.000 | +0.250 | +0.083 | +0.000 | +0.111 | **no** | none |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (rgb, primary D_cue = D(A,B1), placebo-corrected): **UNDECIDED**
> seed signs disagree (+0.250, +0.083, +0.000) -- PREREG sec.4.5-4

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — seed signs disagree (+0.250, +0.000, +0.000) -- PREREG sec.4.5-4

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 0.875 | 0.875 | 1.000 | 0.875 | 0.875 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |
| A vs P | 24 | 1.000 | 0.875 | 0.875 | 1.000 | 0.875 | 0.875 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (depth, primary D_cue = D(A,B1), placebo-corrected): **SHORTCUT**
> D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |
| A vs P | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (b2, primary D_cue = D(A,B1), placebo-corrected): **SHORTCUT**
> D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (placebo-corrected +0.000)

## scene20 · stem `260823_cueoff` · label set `twin`

> **Primary D_cue = D(A, B2)** · placebo **NOT ADMISSIBLE**  
> NO admissible placebo (PREREG sec.3.3): every piece of mesa furniture measures 0 px in 6/6 H frames. Reported EXPLORATORY; contributes via B2 surgery and arm-C FA.

### arm C — false alarms on the cue vocabulary alone (H2)

| model | s42 | s43 | s44 | mean | n frames |
|---|---|---|---|---|---|
| rgb | 0.083 | 1.000 | 0.000 | 0.361 | 24 |
| depth | 0.000 | 0.000 | 0.000 | 0.000 | 24 |
| b2 | 0.458 | 0.083 | 0.000 | 0.181 | 24 |

_H2 accepted at FA >= 0.40 (PREREG sec.4.4); compare sceneC2 new-off FA .681._

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 0.333 | 1.000 | 1.000 | +0.667 | +0.000 | +0.000 | +0.222 | **no** | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.167 | 0.000 | +1.000 | +0.833 | +1.000 | +0.944 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.833 | +0.000 | +0.000 | +0.167 | +0.056 | **no** | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.333, +0.833, +1.000 · guard share of the full cue effect = 24%

> ### VERDICT (rgb, primary D_cue = D(A,B2), NO placebo): **UNDECIDED**
> seed signs disagree (+0.667, +0.000, +0.000) -- PREREG sec.4.5-4

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — seed signs disagree (+0.667, +0.000, +0.000) -- PREREG sec.4.5-4

_secondary D_cue = D(A,B1): **UNDECIDED** — D_cue +0.944 but no admissible placebo, so the cue-evidence branch cannot be evaluated_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | +0.000 | +0.000 | +0.000 | +0.000 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.000, +0.000 · guard share of the full cue effect = —

> ### VERDICT (depth, primary D_cue = D(A,B2), NO placebo): **SHORTCUT**
> D_cue +0.000 < 0.1 and 3/3 same sign (no placebo available -- exploratory)

> twin-conditional (twin = arm C, R2 P3 primary metric): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (no placebo available -- exploratory)

_secondary D_cue = D(A,B1): **SHORTCUT** — D_cue +0.000 < 0.1 and 3/3 same sign (no placebo available -- exploratory)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.333 | 0.333 | +1.000 | +0.667 | +0.667 | +0.778 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 6 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | +1.000 | +1.000 | +1.000 | +1.000 | yes | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |
| A vs P | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.667 | +0.000 | +0.000 | +0.333 | +0.111 | **no** | none **VOID (paired-H 6 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +0.000, +0.333, +0.333 · guard share of the full cue effect = 78%

> ### VERDICT (b2, primary D_cue = D(A,B2), NO placebo): **UNDECIDED**
> D_cue +0.778 but no admissible placebo, so the cue-evidence branch cannot be evaluated

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — D_cue +0.778 but no admissible placebo, so the cue-evidence branch cannot be evaluated

_secondary D_cue = D(A,B1): **UNDECIDED** — D_cue +1.000 but no admissible placebo, so the cue-evidence branch cannot be evaluated_

## scene12 · stem `260823_cueoff2` · label set `twin`

> **Primary D_cue = D(A, B2)** · placebo ADMISSIBLE  
> GT = the declared-degenerate 50-cell footprint in the `lineage` set (PREREG amendment A1.1); placebo is 12-30x the guard's pixel mass = conservative. D(A,B1) is SECONDARY and anti-conservative.

### arm C — false alarms on the cue vocabulary alone (H2)

| model | s42 | s43 | s44 | mean | n frames |
|---|---|---|---|---|---|
| rgb | 1.000 | 1.000 | 1.000 | 1.000 | 24 |
| depth | 0.375 | 0.375 | 0.000 | 0.250 | 24 |
| b2 | 1.000 | 0.875 | 1.000 | 0.958 | 24 |

_H2 accepted at FA >= 0.40 (PREREG sec.4.4); compare sceneC2 new-off FA .681._

### rgb — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (rgb, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> only 0/3 seeds available

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — only 0/3 seeds available

_secondary D_cue = D(A,B1): **UNDECIDED** — only 0/3 seeds available  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

### depth — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (depth, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> only 0/3 seeds available

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — only 0/3 seeds available

_secondary D_cue = D(A,B1): **UNDECIDED** — only 0/3 seeds available  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

### b2 — paired strict-H recall and deltas

| pair | paired-H | R_A s42 | R_A s43 | R_A s44 | R_B s42 | R_B s43 | R_B s44 | D s42 | D s43 | D s44 | mean D | same sign | tier migration |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A vs B2 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs B1 | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |
| A vs P | 0 | nan | nan | nan | nan | nan | nan | +nan | +nan | +nan | +nan | **no** | none **VOID (paired-H 0 < 10, PREREG sec.4.5-3)** |

**H3 guard standalone** — D(A,B1) - D(A,B2) = +nan, +nan, +nan · guard share of the full cue effect = —

> ### VERDICT (b2, primary D_cue = D(A,B2), placebo-corrected): **UNDECIDED**
> only 0/3 seeds available

> twin-conditional (twin = arm C, R2 P3 primary metric): **UNDECIDED** — only 0/3 seeds available

_secondary D_cue = D(A,B1): **UNDECIDED** — only 0/3 seeds available  (placebo UNDER-matches B1's pixel mass ~3.2x -> anti-conservative; not promoted to decisive, PREREG sec.3.1)_

