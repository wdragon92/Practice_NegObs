# T13 · FA census — "the false alarms are locked to the grid, not to the scene"

<!-- LEDGER: experiments/v3_0823/FA_CENSUS.md :32,38-39,49 defs · :72-83 headline · :96-114 appendix/convnext -->
<!-- LEDGER: FA_CENSUS.md :122-139 seed persistence · :199-237 families+R^1.98 · :241-310 dose-response -->
<!-- LEDGER: FA_CENSUS.md :317-345 grid-locked · :351-403 fusion headroom · :460-507 none_in_fov + verdict -->
<!-- LEDGER: FA_CENSUS.md :678-693 §8 registration proposal · :697-882 §9 corrected GT -->
<!-- LEDGER: experiments/v3_0823/ACCOUNTING.md §4.5 (old GT rows) + §4.7 (corrected GT rows) -->

- **Corrected-GT status**: **BOTH — and the ledger registers them separately.** `ACCOUNTING.md` §4.5
  is the **old-GT** row set (frozen, for comparison with published `eval_test`); **§4.7 is the
  corrected-GT canonical row set.** The **entire OFF layer is byte-identical between the two** —
  measured, not asserted.
- **Provenance**: `experiments/v3_0823/FA_CENSUS.md` · events `fa_events.csv` /
  `fa_events_v2corr.csv` · ledgers `logs/{fa_recount,fa_census_tables,fa_dose_response}.json`
- **Unit**: 1 FA event = **(checkpoint, frame, cell)** with `score ≥ τ_op` AND `GT == 0`. τ_op = 0.5.
  **The two strata must never be summed.** OFF exposure = **8,160 cells** (408 × 20); ON_NEG
  exposure = 5,469 (old GT) / **5,304** (corrected).
- **GPU 0** — pure re-aggregation of on-disk artefacts. Clean re-run: **7.1 s**.

---

## 0. Headline and validation

| item | old GT | **corrected GT (B)** |
|---|---|---|
| total FA events | **6,925** (OFF 2,212 / ON_NEG 4,713) | **6,106** (OFF **2,212** / ON_NEG 3,894) |
| published-value cross-check | **27/27 match, 0 mismatches** | **27/27 match** |
| `off_gt_nonzero_cells` | 0 in all 9 runs | 0 in all 9 runs |

**The OFF layer is byte-identical across the two GTs** — all 2,212 rows agree including family flags
and the `method` column, **0 differing rows**. Everything below that rests on the OFF layer is
therefore valid under both GTs.

## 1. FUSION HEADROOM — the largest actionable result

OFF layer, seed-majority (≥2 of 3 seeds) (frame, cell) sets:

| pair | \|A\| | \|B\| | intersection | union | **Jaccard** |
|---|---|---|---|---|---|
| **rgb ∩ depth** | 269 | 42 | **0** | 311 | **0.000** |
| rgb ∩ b2 | 269 | 93 | 40 | 322 | 0.124 |
| depth ∩ b2 | 42 | 93 | 2 | 133 | 0.015 |

| 3-model simultaneous | union | exactly 1 model | exactly 2 models |
|---|---|---|---|
| **0** | 362 | **320 (88.4 %)** | 42 (11.6 %) |

> **Not a single off-arm false-alarm cell is shared by all three architectures, and rgb ∩ depth is
> exactly empty (Jaccard 0.000 — and 0.000 in all four families separately).** AND-gating would
> eliminate off-arm FA in principle; a 2-model consensus still leaves 42/362 (11.6 %).
> **This is an FA upper bound, not a performance guarantee.**

## 2. GRID-LOCKED — the single measurement that falsifies the most families at once

If FA tracked scene content, pulling the camera back 6 m would move the firing band by 6 m
(|slope| ≈ 1). Measured slope of mean fired-band midpoint vs `cam_d`, OFF layer:

| scene | n | slope | scene | n | slope |
|---|---|---|---|---|---|
| scene05 | 376 | **−0.005** | scene18 | 239 | +0.387 |
| scene07 | 135 | +0.011 | sceneC2 | 191 | −0.058 |
| scene14 | 211 | +0.243 | sceneN3 | 372 | +0.006 |
| scene15 | 688 | −0.053 | | | |

**All 7 scenes sit near zero; range −0.058 ~ +0.387.** Content-following would require ≈ ±1.

**scene05 is the decisive case.** Its `arc_bands` sit at radii 8.0 / 9.5 / 11.0 m and fall in bands
1·2·3a at nearly every viewpoint — yet **367 of 376 OFF FA events (97.6 %) land in band 3b**, and at
`d = 1.50` **all 18 events are 3b**, at which point the amphitheatre lip is 1.5 m ahead and the
8–12 m zone is **outside the theatre entirely**.

> **The v2 model barks at "8–12 m ahead" regardless of what is there.**
> No (scene, cell) passes the grid-locked test. scene18 (+0.387) is the only partial exception.

## 3. The distance law — FA rate ∝ **R^1.98** (OFF layer)

| band | R_mid | OFF FA rate | local slope d(ln rate)/d(ln R) |
|---|---|---|---|
| 2 [2,5) m | 3.5 m | .0100 | — |
| 3a [5,8) m | 6.5 m | .0289 | 1.72 |
| 3b [8,12) m | 10.0 m | .0816 | 2.41 |

Global fit **∝ R^1.98**; ON_NEG is R^1.35 (corrected: R^1.15 — **OFF's R^1.98 is canonical**).
Band 2 → 3b is an **8.2×** rise. Truncation-artefact rebuttal: zero-visible-pixel share is 0.184
(band 3b) vs 0.167 (band 3a) — essentially flat.

> **The exponent matches the literature.** `FA_REALITY.md` D2 cites the JPL result that a negative
> obstacle's angular size shrinks as **1/R²**, leaving wide room for false alarms and misses. Our
> corpus **reproduces the exponent a 30-year-old paper predicted** — this is geometry, not a grid
> artefact. It is the mirror image of the far-field vanishing that defines the problem (DZ §1).

> ⚠ **No R² / goodness-of-fit statistic is reported anywhere for this fit.** The only fit-quality
> figure in the ledger is the ln-residual triple **[+0.047, −0.115, +0.068]**. **Do not write "R²".**

## 4. Family verdicts (D54 5-family schema) — one survivor, and it is optical

| layer · family | n_FA | P(f\|FA) | n_exposed | P(f\|exposed) | **LIFT** |
|---|---|---|---|---|---|
| OFF · boundary-cell (registered union) | 1,607 | .726 | 4,488 | .550 | 1.32 |
| OFF · ├ **radial component** (band 3b) | 1,498 | .677 | 2,040 | .250 | **2.71** |
| OFF · └ **azimuthal component** (sector A/E) | 315 | .142 | 3,264 | .400 | **0.36** |
| OFF · lighting | 73 | .033 | 194 | .024 | 1.39 |
| OFF · proxy-line | 168 | .076 | 512 | .063 | 1.21 |
| OFF · terrain-statistic (unseen only) | 136 | .061 | 1,179 | .144 | 0.43 |
| ON_NEG · ├ radial | 2,011 | .427 | 714 | .131 | **3.27** |
| ON_NEG · └ azimuthal | 1,445 | .307 | 2,337 | .427 | 0.72 |
| ON_NEG · lighting | 504 | .107 | 288 | .053 | 2.03 |
| ON_NEG · proxy-line | 363 | .077 | 193 | .035 | 2.18 |

**Decorative — REJECTED.** Localised to 2 of 7 scenes; in the clean OFF layer the in-region /
out-of-region lift is **1.01 (sceneC2) and 0.98 (sceneN3)** — no effect.

**Proxy-line — no OFF effect.** `line_frac` quintiles are flat in OFF (.0295/.0377/.0312/.0373); and
in **sceneN3's band 3b — the corpus's strongest proxy-line scene — more lines means FEWER false
alarms (.3657 → .1296).** The trompe-l'œil painting is **not** where FA actually happens.

**Lighting — U-shaped and sign-flipping.** OFF `lum_ratio` quintiles dark→bright:
.0395 / .0181 / .0225 / .0385 / .0466 — both ends rise, the middle is the minimum. And the sign
**flips** by scene and layer (`scene07|band3b` OFF .0602→.0062 vs ON_NEG .3901→.5012).
**"Dark ⇒ barks" does not hold.**

**The ONE monotonic driver — within-cell luminance dispersion (`lum_sd`):**

| slice | Q1 | Q2 | Q3 | Q4 | Q5 | Q5/Q1 |
|---|---|---|---|---|---|---|
| OFF overall | .0268 | .0193 | .0250 | .0382 | **.0558** | 2.1× |
| **OFF band 2** | .0006 | .0033 | .0077 | .0182 | **.0204** | **34×** |
| OFF band 3a | .0127 | .0174 | .0192 | .0451 | **.0530** | 4.2× |
| OFF band 3b | .0479 | .0492 | .0685 | .0999 | **.1548** | 3.2× |

**Fully monotone in every band.** What predicts FA in the clean OFF layer is **distance (R^1.98) and
within-cell optical dispersion** — not darkness, not lines, not decoration.

### 4.1 Boundary-cell: the registered family does not exist as registered

The radial half (lift 2.71 / 3.27) and the azimuthal half (lift **0.36** / 0.72) point in **opposite
directions**. Edge sectors A/E are where FA is **least** concentrated, not most. OR-ing them dilutes
the lift to 1.32. **Preliminary ruling**: reject `경계칸형`, absorb its volume into the
**terrain-statistic subtype "far-field aperture vanishing."** (Final ruling: 승용.)

### 4.2 Unplanned positive control

convnext_tiny's collapsed constant output lands on **`C3b` (s42, 408/408 frames, `cell_fpr_off`
= 0.0500 = exactly 1/20)** and **`B3b`·`C3b`·`D3b` (s43, 0.1500 = exactly 3/20)** — i.e. **the
default of a model that learned nothing is precisely "centre sector × outermost band."** That is the
**same max-prior cell** the census identified independently (OFF top B3b .1533, C3b .1356).
**A free positive control for §2–§3.** resnet50 weakly reproduces the profile (OFF band 3b 568 /
3a 170 / 2 61 / 1 2).

## 5. `none_in_fov` — the headline that destroyed itself

| # | quantity | old GT | **corrected GT (B)** | Δ |
|---|---|---|---|---|
| B′ | ON_NEG exposure | 5,469 cells | **5,304** | −165 |
| C′ | `none_in_fov` exposure share | 1,620/5,469 = 29.6 % | **780/5,304 = 14.7 %** | −14.9 pp |
| D′ | **`none_in_fov` EVENT share** | 2,673/4,713 = **56.7 %** (lift 1.91×) | **683/3,894 = 17.5 %** (lift **1.19×**) | **−39.2 pp** |
| E′ | total FA events | 6,925 | **6,106** | −819, **all ON_NEG, all scene07** |

The claim *"more than half of on-arm FA comes from outside the accounting"* was **an artefact of the
defective GT.** The agent **demoted its own recommendation N4** on the record (priority 상 → 중,
protocol-cleanup item). Two depth runs went from 396/327/357 `none_in_fov` FA events to **15/0/0**.

**Not closed, though**: the residual 39 frames (9.6 %) are still in **no published denominator**, and
the underlying defect — `none_in_fov` adjudicated **post-gate** (`labeler.py:526`) — survives the
relabel.

**Nothing flipped sign under the corrected GT**: boundary radial 3.27→3.05, azimuthal 0.72→0.74,
lighting 2.03→2.06, terrain-statistic 1.25→1.30, 3-model simultaneous 5.8 %→5.2 %, depth seed
persistence .623→.578. **Only proxy-line weakened meaningfully, 2.18 → 1.60** — a *strengthening*
correction (much of the apparent ON_NEG proxy-line enrichment was GT defect).

## 6. N-cue targeting rule (operational, v3)

Seed persistence (≥2/3 seeds): rgb|OFF .328 · **depth|ON_NEG .623 (3/3 = .313)** · b2|OFF .126
(3/3 = **.022**, 16 of 740 cells). **Only depth's ON_NEG FA is structural; b2's OFF FA is nearly
pure noise** (its `frame_fa_off` spans .1078–.3946 across seeds, a 3.7× range).

> **Any intervention aimed at reducing FA must target seed-persistent FA. Designing scenes from a
> single-seed FA list means chasing noise — v3 §4.2 N-cue targets must pass a `≥2/3` filter.**

---

## CAVEAT LINE — must travel with this table

> **The census is the third instrument, and it points the same way as the other two — in reverse.**
> CUE-OFF removed cues and firing did not die (CUE EVIDENCE 0/30). The census adds cues and firing
> does not rise (decorative lift 1.0). Two independent experiments, one conclusion:
> **v2's false alarms follow "optical change × distance", not "number of cues."**
> *(Note: the ledger frames this as the second, reverse-direction instrument; Gazebo (T05) is the
> independent third. Choose one framing and keep it consistent.)*

> **Honest limit of the OFF arm.** v2's off arm is "hazard removed, dressing preserved" — it
> approximates **FA_C, not FA_D**. The comparison is *by position*, not *by presence*. A presence
> contrast needs a real D arm, which is v3's job.

> ⚠ **Internal inconsistency to resolve before printing.** The same old-GT `none_in_fov`
> concentration lift is printed as **1.92×** (§5.3, §8 row D) and **1.91×** (§9.1 row D, §9.4).
> Exact quotient .567/.296 = 1.9155… **Pick one and use it everywhere.**

> **`ACCOUNTING.md` §8 registration is a PROPOSAL, not yet entered.** The agent explicitly did not
> modify the append-only ledger. If a census number is cited, cite it as
> **§4.5 (old GT)** or **§4.7 (corrected GT)**, per the leg+fold+n discipline of §1.7.

> **The appendix arms (resnet50, convnext_tiny) are OLD GT only** — no corrected dumps exist, and
> the script enforces `--corr` / `--appendix` as mutually exclusive.
