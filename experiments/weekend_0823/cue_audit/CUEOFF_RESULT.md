# CUEOFF_RESULT — CUE-OFF intervention read-out

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

