# T04 · CUE-OFF intervention — verdict census (정본 회계)

<!-- LEDGER: experiments/v3_0823/ACCOUNTING.md §1.1-§1.7 (census reconciliation, D53) -->
<!-- LEDGER: experiments/weekend_0823/cue_audit/CUEOFF_RESULT_v2.md:57 (cell def), :61-67 (census), :28-30 (v1 restricted) -->
<!-- LEDGER: experiments/weekend_0823/cue_audit/VERDICT_CENSUS_v2.csv (row-level source) -->
<!-- LEDGER: experiments/weekend_0823/cue_audit/PREREG_CUEOFF.md:195 (no-promotion), :215 (paired-H>=10), :548-554 (fold both counts), :596-627 (s20fix pre-registration) -->

- **Corrected-GT status**: **census verdicts are unaffected** by the G7 repair. The repair's effect
  on this track is *diagnostic*: it is what proved the s12 "strict-H" frames were tier V, i.e. the
  primary CUE-OFF target scene was **not a strict-H scene**. VOID reason #3 already encodes it.
- **Provenance**: `experiments/weekend_0823/cue_audit/CUEOFF_RESULT_v2.md` (정본; v1 preserved with
  banner) · reconciliation `experiments/v3_0823/ACCOUNTING.md` §1
- **Cell definition** (registered): **1 cell = (label set × band × scene × model)**. `leg` is *not*
  a cell dimension — `primary` / `primary-twinconditional` / `secondary` are three verdicts on the
  *same* cells, so the census is reported **per leg**. Frame-level population = **paired frames that
  are strict-H in both arms** (`PREREG_CUEOFF.md:175-177`).

---

## 1. Census (정본)

| population | CUE EVIDENCE | SHORTCUT | NO-EFFECT | UNDECIDED | VOID | n | status |
|---|---|---|---|---|---|---|---|
| **primary, all blocks** | **0** | 2 | 6 | 4 | **18** | **30** | **정본 headline** |
| **primary, A2-7 folded** | **0** | 2 | 4 | 3 | 12 | **21** | **정본 — use this for "independent replication"** |
| primary, decidable only (VOID excluded) | 0 | 2 | 6 | 4 | — | 12 | derived (numerator) |
| twin-conditional leg | 0 | 5 | 7 | 0 | 18 | 30 | separate leg |
| secondary B1 leg | 4 | 1 | 0 | 1 | 18 | 24 | **promotion forbidden** (`PREREG_CUEOFF.md:195`) |
| *(reference)* v1 comparison-restricted population | 0 | 2 | 6 | 4 | 12 | 24 | **not a census** — §1.3 |

- **Decidable fraction = 12/30 = 40.0 %** (folded: 9/21 = 42.9 %).
- **The answer to the pre-registered primary rule is CUE EVIDENCE 0** — identical in v1 and v2.
  The 4 CUE EVIDENCE verdicts are all on the **secondary B1 leg**, whose promotion the
  pre-registration forbids.
- **A2-7 obliges printing 30 and 21 together** (`PREREG_CUEOFF.md:548-554`). Printing the headline
  alone is a protocol violation.

### 1.1 Why 30 and not 24 (the reconciliation)

30 and 24 are **not competing** — they are **nested**. 24 = 30 − the 6 cells of the `s20fix` repair
round, which had **0 PNG files** at the v1 readout (07:20) and therefore could not be counted then
(`PREREG_CUEOFF.md:598-599`). The registered population includes `s20fix`, because it was registered
as A2-10 **before it was rendered**. The 6 added cells are **all VOID**, so VOID 12 → 18 and n 24 → 30
while the other four verdict values do not move at all (0/2/6/4 unchanged).

### 1.2 The fold (A2-7)

scene17 and scene20 have identical tier and score under both label sets, so the `twin` block is a
**byte copy** of the `lineage` block. 8 apparent scene×labelset blocks are really **4**. Folded cells
= twin×scene17 (3) + twin×scene20 original (3) + twin×scene20 repair (3) = 9 → 30 − 9 = **21**.
Check: NO-EFFECT 6−2=4 · UNDECIDED 4−1=3 · VOID 18−6=12 → 0/2/4/3/12, n=21. ✓

## 2. VOID 18 — full enumeration of causes

| # | cells (label set × stem × scene × 3 models) | n_paired | reason |
|---|---|---|---|
| 1 | lineage + twin × `260823_cueoff` × scene20 | **6** | paired-H 6 < 10 (`PREREG_CUEOFF.md:215`, forced inside `verdict()`) |
| 2 | lineage + twin × `260823_cueoff_s20fix` × scene20 | 27 | `polar_gt` byte-identity failure (decision frames 6/27) — **blind pre-ruling A2-13**, decided *before any model was run* (`PREREG_CUEOFF.md:697`) |
| 3 | twin × `260823_cueoff` + `cueoff2` × scene12 | **0** | paired-H 0 — the A-arm frames are **tier V under the corrected footprint** |

The largest candidate effect, `s20fix` b2 **+0.506** (3/3 seeds), falls under rule #2: **printed but
not counted**. That is the pre-registration working, not a result being discarded after the fact.

---

## CAVEAT LINE — must travel with this table

> **CITATION RULE (mandatory, `ACCOUNTING.md` §1.7).** Always cite a census as
> **leg + folded-or-not + n** — e.g. *"primary leg, unfolded, n = 30"*. **Bare numbers are
> forbidden**, because `n = 24` and `VOID = 12` each appear in **two different populations** inside
> the same document (24 = v1-restricted *and* secondary B1 leg; VOID 12 = v1-restricted *and* the
> A2-7 folded census).

> **The verdict is NEUTRAL, and the contribution is the instrument, not the outcome.** The correct
> framing is: a pre-registered 5-arm intervention with placebo and a gate suite returned
> **CUE EVIDENCE 0**. The contribution is (a) the **apparatus** — pre-registration, 5 arms, placebo,
> a G0 noise floor against manipulation mass 10³–10⁵× larger, and adherence to the non-promotion
> rule — and (b) the **diagnosis** it produced (the two corpus defects). It is **not** evidence that
> the model reads a cue vocabulary; D46's claim to that effect is **withdrawn**.

> **The false alarms follow the optical size of the surgery, not the number of cues.** See T04b
> (§4.4 dose–response): scene17 keeps **every** cue and sits at the bottom (FA 0.042).

> **40 % decidability is itself a finding to state first.** *"A study that can decide only 40 % of
> its own cells must change the scene set, not the readout, in the next round."* (caveat C7)

> **Approval #3 disposition**: adopted as *neutral result + instrument contribution*, and promoted
> to the **"before" measurement of v3** (`PROJECT_STATE_0823_v2.md` §3).
