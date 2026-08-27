# version_journey_skeleton — the honest version-journey narrative (v1 → v2 → demolition → v3)

- **Status**: SKELETON / MATERIALS. Not final prose. Claude AI + 승용 own the finished text (D58 ⑥).
- **Written**: Claude Code (CPU-6) · 2026-08-23 · target: v3-frame main paper (English).
- **Why this section exists at all**: 교수님 지침 — the failure journey is itself a contribution.
  `[승용: "실패 하나하나도 좋은 기여로 담길 수 있으니"]` `DZ:328-329`; PS v2 §4 `:84`
  ("논문 프레임: 4층 서론 → v1→v2 진단(버전 여정) → v3 처방·검증").
- **Rule of this file**: every number has a ledger path. **No number appears in the paper without one.**
  Pending items marked `[미결: …]`.

**Abbrevs**: DZ = `Docs/campaign/V3_DESIGN_0823.md` · PS v2 = `Docs/archive/campaign_status/PROJECT_STATE_0823_v2.md` ·
ACC = `experiments/v3_0823/ACCOUNTING.md` · DEC = `experiments/mainrun_0819/DECISIONS.md` ·
ST = `experiments/dayrun_0820/runs/v2/SEED_TABLE.md` · F1 = `experiments/weekend_0823/rt_response/F1_FA_MATCHED.md` ·
F2 = `experiments/weekend_0823/rt_response/F2_TWIN_CONDITIONAL.md` ·
CO = `experiments/weekend_0823/cue_audit/CUEOFF_RESULT_v2.md` ·
GZ = `experiments/weekend_0823/gazebo/GAZEBO_TRACK.md` · RS = `experiments/v3_0823/V2_RESCORE.md` ·
E12 = `experiments/v3_0823/redteam/EVL12_CELL_AXIS.md` · FAC = `experiments/v3_0823/FA_CENSUS.md` ·
CC = `experiments/v3_0823/CUE_COVERAGE.md` · MR23 = `experiments/weekend_0823/MORNING_REPORT_0823.md`.

---

## 0. The shape of the section — six beats, one thesis

**Thesis to state up front (one sentence, before any chronology)**:
> *We report a result we then destroyed with our own instruments, and the destruction is what
> produced the design. The instruments — a counterfactual twin, a cue-removal intervention and a
> cross-simulator transfer — are the reusable part; the corpus that made them uninformative is the
> lesson.*

| Beat | Content | Where the numbers live |
|---|---|---|
| §1 | v1 → v2: what was built and what it was for | ACC §3.2 `:282-303` |
| §2 | The v2 headline | ST §1; RS §1.2 |
| §3 | Three-instrument demolition | F1/F2 · CO · GZ (§3.1–3.3 below) |
| §4 | Diagnosis: causes A / B / C | DZ §3 `:204-209` |
| §5 | v3 prescription, cause-by-cause | DZ §4.1 · §5.1 · §4.3-3 |
| §6 | Pre-registration and the dashboards | DZ §7 · ACC §2, §4.9 |
| §7 | Language constraints on every claim in this section | §7 below |

**Tone constraint** (applies to the whole section): the execution discipline held — the team
demolished its own headline — but the upstream data logic was frozen while still half-baked.
DZ's own words `:201-202`: `[승용: "너무 결과물을 위한 실험을 강행한 느낌"]` … "실행 규율은 지켜졌으나
… **상류의 데이터 논리가 설익은 채 동결된 것**이 사실이다." Do not write this as a triumph narrative,
and do not write it as an apology. It is a mechanism report.

---

## 1. Beat 1 — v1 → v2

- **July**: the 4-layer frame was designed and the **twin (counterfactual pair) instrument** was
  invented. Original intent: **verify layer ①**. `DZ:196-197`
- **v1 corpus** (reference figures): 33 scenes × 48 cuts = **1,584 frames**
  (V 438 · E 36 · H 45 · H_weak 12 · none_in_fov 261 · off 792). `ACC §3.2 :303`
- **Early August — corpus v2 built.** Here the off arm, in deleting the hazard, **deleted the cues
  along with it** (this generation is called 구off / old-off). *The layer-① verification instrument
  had become, unintentionally, a confounder generator.* `DZ:197-198`
- **v2 corpus**: **2,832 frames** — V 693 · E 72 · H(strict) 243 · H_weak 30 · none_in_fov 378 ·
  off 1,416. Twin identity holds: on-arm 1,416 = off-arm 1,416. Splits: train 1,536 / val 288 /
  test 816 / hold 192. `ACC §3.2 :289-301`, independently re-verified at
  `experiments/weekend_0823/redteam/R3_repro.md:26-38`.
- **test-core** = the 7-scene, frame-invariant common yardstick for all v2/v3 A/B:
  816 frames, 408 on / 408 off, tiers V 180 · E 45 · H 96 · H_weak 6 · none_in_fov 81 (old GT).
  `ACC §3.1 :271-281`

> Sentence to carry forward: **the instrument that was supposed to prove inference is the same
> instrument that, wired one way, guaranteed there was nothing to infer.**

---

## 2. Beat 2 — the v2 headline

**What was published** (τ_op = 0.5, 3 seeds, `mean ± range/2`), `ST §1`:
- RGB `frame_recall_H` **0.688 ± 0.141** vs Depth **0.438 ± 0.031** vs B2 0.229 ± 0.156.
- The headline sentence at the time: *"RGB .688 beats Depth .438 on the hidden (H) tier."*
- 4th main-table row: YOLOv8n @ τ0.25, `frame_recall_H = frame_recall_E = 0.000 ± 0.000` on all three
  seeds. `ST §4`

**What the same table already contained and the headline ignored** — the two models were being read
at **different operating points**: off-arm FA **0.359 vs 0.042**, an 8.6× gap. `ST §1` reading banner.

  - *Drafting note*: this is the cleanest available illustration of "threshold illusion" for a general
    audience. Consider presenting the headline and its own footnote **on the same page** rather than
    revealing the flaw later — it reads as honesty rather than as a reveal.

---

## 3. Beat 3 — three independent instruments, three demolitions

**Framing**: three *independent* instruments (a re-analysis, an intervention, and a cross-simulator
transfer) converged on the same diagnosis. PS v2 §1-2 `:29-31` calls this "씬 연합 진단(3중 수렴)".
The convergence is the argument — no single instrument would carry it.

### 3.1 Instrument 1 — FA-matching + twin-conditional re-analysis (a re-analysis, zero new renders)

**(a) FA-matched comparison — the threshold illusion, quantified.** Exact-quantile τ taken from the
off arm's per-frame max-probability order statistic (resolution 1/408 = 0.0025), then H recall read at
that τ. `F1 §2`; re-run on corrected GT at `RS §3`.

| Matched FA | RGB H | Depth H | B2 H | Δ(D−R) |
|---|---|---|---|---|
| .359 | 0.729 ±0.135 | 0.781 ±0.078 | 0.399 ±0.078 | **+0.052** |
| .200 | 0.483 ±0.172 | 0.562 ±0.031 | 0.198 ±0.141 | **+0.080** |
| .100 | 0.326 ±0.229 | 0.510 ±0.078 | 0.097 ±0.099 | **+0.184** |
| .050 | 0.243 ±0.208 | 0.479 ±0.094 | 0.031 ±0.036 | **+0.236** |

Ledger: `F1 §2`, corrected-GT reproduction `RS §3.1 :288-298` (identical to 3 decimals — *"살아남는다.
그것도 수치가 완전히 동일하게"*). **Depth ≥ RGB at every matched point.** The surviving RGB sentence:
*"RGB recovers ~1/3 of hidden frames inside a 10 % FA budget — which is not zero."* `PS v2 :25-28`

**(b) Twin-conditional recall — how much of the hit was unconditional.** Definition
`hit(frame) = [max_on_gt ≥ τ] ∧ [max_off_gt < τ]`, τ = 0.5, on KEPT pose-matched pairs. `F2 :1-11`

| model | published H recall | twin-conditional H | off-arm twin fire rate | **share of fires that are unconditional** |
|---|---|---|---|---|
| rgb | 0.688 ±0.141 | **0.375 ±0.115** | 0.330 | **0.447** |
| depth | 0.438 ±0.031 | **0.438 ±0.031** | 0.000 | **0.000** |
| b2 | 0.229 ±0.156 | 0.122 ±0.068 | 0.118 | 0.305 |

Ledger: `F2 §1` (n = 96 kept H pairs per run); verified against R2's published values, `F2 §2`.
**44.7 % of RGB's H hits also fired on the twin from which the hazard had been deleted.**
Depth: 96/96 hazard-conditional (twin fire rate exactly 0.000).

> ⚠ **Generation warning that must appear wherever 44.7 % / 0 % is printed.** These are **(A,D)**
> generation numbers — the old-off arm deleted hazard **and** cue. Under the v3 naming convention
> (ACC §2-2 `:166-183`) the twin-conditional dashboard's pair is **(A,C)** (hazard removed, cue
> preserved). Therefore **44.7 % / 0 % are demoted to reference values** and the canonical (A,C)
> baseline is created by re-scoring v2 checkpoints on the test-ext C arm. `DZ §12-2 :380-384`,
> `ACC §2-2 :181-182`. Never place an (A,D) number and an (A,C) number in the same table cell.
> Additional refinement: the v2 off arm is **not a single generation** — 8 scenes keep their cues
> (≈C-like) and 25 delete them with the hazard (≈D-like). `ACC §4.1 :335-343`, ledger `CC §0-6, §2.1`.

### 3.2 Instrument 2 — CUE-OFF, a pre-registered intervention

**Design**: remove the cue while holding the hazard geometry invariant (arm B), plus a placebo arm C
that removes non-cue objects. Pre-registration: `experiments/weekend_0823/cue_audit/PREREG_CUEOFF.md`.

**Result — the pre-registered primary rule returned ZERO CUE EVIDENCE across 30 cells, of which only
12 were judgeable at all.** `CO §6.4 :720-723`. Census provenance: primary leg all-blocks **30 cells**
is the canonical headline, A2-7-folded **21 cells** must be printed alongside; the "24" figure that
appears elsewhere is the same population minus the 6 s20fix repair-round cells (all VOID) — an
**inclusion relation, not a disagreement**. `ACC §1 :17-150`, `DEC D53`.
  - **Citation rule registered in D53**: never quote a bare number — always `leg + folded? + n`.
    "24" and "VOID 12" each occur with two different meanings inside a single document. `ACC §1.7 :137-150`

**The dose–response that killed the "cue vocabulary" reading** — four scene-rounds, one variable
(how far arm C's surgery moved the picture from the hazard-off round), `CO §4.4 :436-453`:

| scene · band | optical distance from off-round (≥32/255) | FA(C) rgb | FA(C) b2 | cue vocabulary preserved? |
|---|---|---|---|---|
| scene12 · `boost_e2` | 58.35 % | 1.000 | 0.958 | yes |
| scene12 · `boost_e` | 36.60 % | 1.000 | 1.000 | yes |
| scene20 · `boost_e2` | 13.09 % | 0.361 | 0.181 | yes |
| **scene17 · `boost_h`** | **1.02 %** | **0.042** | 0.056 | **yes — full vocabulary** |

**Monotone in optical distance, flat in vocabulary.** scene17 keeps every cue noun and does not fire
(.042). The false-alarm rate measures **how different the picture is**, not **how many cue nouns are
in it**. D46's "the model fires on cue vocabulary" was withdrawn (D49 ①; this is the mass-resolved
version of the same retraction). `CO :447-453`

**The disqualified candidate — report it, with its number, twice.** The one candidate that would have
qualified was disqualified first by our own sample-size floor and then, after GPU time was spent
removing that floor, by our own geometry-invariance rule. We print **+0.506** next to the reason it
does not count. `CO §6.4 :720-726`
  - *Drafting note*: this is the single most persuasive integrity artifact in the whole journey. It
    belongs in the paper body, not an appendix.

**The confound we cannot resolve and must say so** `CO §6.4 :735-741`: *"'cues' and 'a third of the
picture' are perfectly confounded in every arm we built, and our best-matched placebo removes
non-cue objects and does more damage than removing the guard does."*

**Why coverage was so thin — the honest mechanism** (this is also the v3 requirement): 33/33 scenes
carry ≥1 removal toggle, but the filter chain 33 → strict-H 6 scenes → non-test 4 → s09 drops out →
**3**, and post-hoc adjudication leaves **1 effective scene (s17)**. The bottleneck is not wiring, it
is **strict-H availability**. s14's guard is *structural* (parapet builds unconditionally) so it
cannot be toggled at all. `DEC D56`, ledger `CC`; registered as ACC §2-6 `:220-228`.

### 3.3 Instrument 3 — Gazebo cross-simulator transfer

**Purpose**: a layer-③ cross-domain stress test in a *different renderer*, where the hazard prism is
verified at **0 px** by an independent leak check. `GZ §3 :53-88`

- **Firing on a hazard-0-pixel world**: `gz_drop3` contains **0 pixels** of hazard geometry; both arms
  are "cue-only" probes. Detection rate rgb **0.524**, b2 **0.905** (11/21 and 19/21). Twin Δ is 0 by
  construction and measures max |Δ| = 0.090 across all model × view. `GZ §4.4 :159-179`
- **Tier-ladder inversion in 5 of 6 models**: the ladder's order follows **the scene's furniture
  order, not the geometry**. `gz_drop3` (H, hazard 0 px, warning block + railing + planter wall all
  visible) is scored **above** `gz_drop2` (V, no warning block) by 5 of 6 models. `GZ §4.3 :128-152`
  - **Correction that must ride along**: D48's recorded "4/6" was a miscount; the ledger's own
    re-count is **5/6**. `GZ :147-149`
  - **Scope limit the ledger itself imposes** `GZ :155-157`: this section claims **the observation of
    ladder-order inversion** and no more. It does **not** establish "the model reads cue vocabulary" —
    §3.2's dose–response is the reason that reading was withdrawn.

**Convergence sentence** (the one CO §6.4 authorises, `:723-733`):
> ***"These detectors respond to whether the picture looks like the hazard scene, not to whether the
> hazard is in it."***
> Delete the drop and nothing else and the frame still changes by 4.3–13.6 % of its pixels —
> 10³–10⁵× the renderer noise floor — because a hazard is never optically alone.

**The instrument-contribution framing** `CO §6.4 :742-746`: we ship the pre-registration, the five
arms, the placebo protocol, the datum-preservation argument and the gate suite **as a reusable
instrument — together with the places it broke in our own hands, the measurements that caught each
break, and the amendment that repairs them.**

### 3.4 A fourth demolition landed during the v3 window — the unit flip

Not one of the three July/August instruments, but it belongs in this section because it retires
another way of reading the headline. `E12` (D65).

At τ = 0.5 — **same checkpoint, same frames, same GT**, only the unit of "detection" changed:

| model | frame H recall | **cell H recall** | frame FA | cell FPR |
|---|---|---|---|---|
| rgb | **0.688** | 0.344 | .359 | .0467 |
| depth | 0.438 | **0.537** | .042 | .0089 |
| b2 | 0.229 | 0.096 | .238 | .0347 |

**RGB wins on the frame axis; Depth wins on the cell axis.** Cause: `EVL-08` (any-hit recall) and
`EVL-12` (any-fire FA) stack in the same direction and reward "hit one correct cell and scatter the
rest" — which is exactly RGB's behaviour. `E12 §4 :103-116`
- The FA-matched conclusion is **not** overturned by the axis change — it **strengthens**:
  Δ(D−R) grows from +0.052/+0.080/+0.184/+0.236 (frame) to +0.319/+0.373/+0.428/+0.399 (cell), and
  seed unanimity goes from 1–3/3 to **3/3 at every point**. `E12 §0, §2`
- **Alarm burden is genuinely hidden by the frame axis**: matching frame FA at .359 leaves Depth's
  cell FPR at **2.34×** RGB's (0.1290 vs 0.0552). `E12 §3 :84-93`
- **Red team self-correction, to be reported as such**: `RT_LEDGER_A`'s EVL-12 guessed the *direction*
  of the bias (that the frame axis favoured Depth). **That guess was wrong** — Depth bursts its false
  alarms into few frames, so any-fire counting penalises it. The substance stands; the direction was
  reversed. `E12 :20-22`

---

## 4. Beat 4 — diagnosis: three causes, each paired with one v3 spec

`DZ §3 :204-209`. Present as a three-row table; it is the hinge of the whole section.

| Cause | Mechanism | Evidence | Cured by |
|---|---|---|---|
| **A. Confounding** | Cue ⊥ hazard not separated, so ③ could substitute for ① with **no penalty**. In training data cue and hazard were effectively perfectly co-present (old-off deleted cues too, so both present or both absent). **If the correlation is 1, the incentive to learn inference is 0** — memorising the picture's overall impression scores full marks. | CUE EVIDENCE 0 (`CO §6.4`); FA follows optical change, not cue count (`CO §4.4`); firing on Gazebo 0-px hazard world (`GZ §4.4`) | **DZ §4.1** orthogonal 2×2 |
| **B. Forced supervision** | Ground truth demanded on frames carrying **zero information** ⇒ memorisation is the only surviving strategy. | DZ's own statement of the principle `:206`; 승용's H-tier sentence `DZ:171-172` | **DZ §5.1** cue-conditional supervision + ignore mask for bare-occlusion H |
| **C. H-blind selection** | The checkpoint-selection score's H term had a **6-frame val strict-H denominator** — a 6-question exam where "fire on everything" scores 1.0. Surfaced as convnext collapsing to constant output on 2 of 3 seeds (off-max span 8e-5 / 2e-4; s43 selected an **epoch-1** checkpoint). **This selection rule is recipe v2's and the main table's resnet34 used it too.** | `DEC D52 (월 조립)`; PS v2 §1-7 `:41-42` | **DZ §4.3-3** selection-metric repair: val strict-H ≥ 30 + FA term + constant-output rejection gate |

**Three lessons, verbatim from DZ `:210-211`** (translate, keep the aphoristic form):
1. *No inference without orthogonalisation.*
2. *Do not force an answer that has no on-screen basis.*
3. *The selection metric is part of the experiment — if the metric is sick, every model it picked is sick.*

**A fourth, methodological lesson earned twice during this window** `DEC D61` (and D53 before it):
two of the "three-way inconsistencies" the audit raised turned out to be **misattributed citations
across run generations**, not real defects. *Quoting a number without checking the lineage of the file
it came from manufactures phantom defects.* Both phantoms were resolved to zero published-number
movement (`ACC §4.6 :400-421`, `TWIN_TOL_RESOLUTION.md`).
  - *Drafting note*: this is a good "limitations of self-auditing" note, and it protects the paper
    from the reviewer question "how do we know your other defects are real?" — the answer is that two
    of them were not, and we say which.

---

## 5. Beat 5 — the v3 prescription

Present **cause → spec** as a one-to-one map; that pairing is the section's payoff.

### 5.1 Cause A → orthogonal 2×2 `DZ §4.1 :222-231`
- Four arms per target scene: **A** (hazard + cue) · **B** (hazard − cue) · **C** (no hazard + cue) ·
  **D** (no hazard − cue).
- **Pedagogical role of each arm** (state these; they explain the ratios):
  A = learn the normal binding · B = "do not be confident without a cue" · C = penalty supply for
  "cue ⇒ fire" (layer ④-a) · D = base contrast.
- Draft ratio **3:2:3:2** — C is set equal to A deliberately, to push the expected payoff of the
  shortcut ("cue = fire") toward zero.
- Target **|r| ≤ 0.2** for the training corpus's cue↔hazard point correlation, **measured value
  reported** — this is the quantitative evidence for the sentence "we orthogonalised".
- **Render plan status**: 40-scene matrix, 5,848 new cuts, 9.5 GPU-h (p90 12.4), **predicted |r| = 0.004**.
  `experiments/v3_0823/RENDER_PLAN_V3.md`, `render_plan_v3.json` (P-5, D58 ⑧ release).
  The key judgement: reading Q1 literally gives arm × scene-origin correlation of **1.00 (complete
  confounding)**, so B arms were rendered onto the existing 18 scenes too, driving it to **0.003** —
  enabled by `cue_material_break`, the one clean B-arm lever (material rebinding only, height-map bits
  guaranteed identical). `DEC D56, D58`, ledger `CC`.
- **|r| reporting protocol (RT-B, adopted)**: arm-level φ is **automatically 0 by construction** (it
  cannot distinguish degeneracy from success) ⇒ report ① marginals alongside ② restricted to togglable
  keys ③ **per-key r**. Of the 13 cue keys, 5 have no toggle at all and are flagged as "constant keys".
  `ACC §4.9-3 :493-494`

### 5.2 Cause B → cue-conditional supervision `DZ §5.1 :267-274`
- Positive supervision **only on H frames where a cue is present in frame**; presence is decided
  mechanically from scene config + render output, no human in the loop.
- **Bare-occlusion H (zero cues) → ignore mask** (excluded from the loss) by default. Philosophy:
  *the moment you force an answer with no on-screen basis, memorisation is the model's only survival
  strategy — we do not ask of the model what we would not ask of a person.*
- Alternative (scene base-rate soft target) is compared **as a 1-run ablation only**, because a soft
  target is a path for re-injecting layer ③ into the target (base rate = prior). The ablation exists
  to *measure* that worry, not to adopt it.
- **Unit of the cue-presence decision is the FRAME, not the scene** — segmentation cue-class pixels
  ≥ k, with **k frozen by gate before use and hashed**; scene-level judgement (the weekend's
  `H_CUE_AUDIT` method) is an **upper-bound reference only**. Scene-level supervision would give
  positives to frames whose cue is off-screen and partially re-create the forced supervision.
  `ACC §2-5 :209-218`. **k is still unset** — ACC §3.4 open item 1; frame-level supervision does not
  start until k is fixed. `[미결: k 미확정 — 지도 착수 전 게이트 고정 필요]`
  - Feasibility now confirmed: the seg sidecar smoke test PASSED (`instance_id_segmentation` returns
    prim paths directly, 48 KB/cut, **zero extra render cost**) — so both the k decision and the
    edge-ownership gate are implementable. `STATUS.md` (P-5), D58 ⑨.
- **Range of the ignore mask — a firewall sentence for the paper** `ACC §2-4 :201-207`: the mask
  applies to the **training loss only**. Evaluation denominators, recall and FA definitions stay
  identical to v2. **A recall obtained by shrinking the denominator is not an improvement, it is an
  artifact.**

### 5.3 Cause C → selection repair `DZ §4.3-3 :254-256`
- val strict-H expanded to **≥ 30** + an **FA term** in the score + a **constant-output rejection gate**.
- **What "v2 reproduction check" means** — and it is not what it sounds like `ACC §2-7 :230-238`:
  not the reappearance of the same numbers, but **proof that swapping the metric did not manufacture
  the result**. Apply the new metric to the *existing* v2 runs (re-select from stored epoch
  checkpoints; retrain resnet34 ×3 only if unavailable) and report the difference against old-metric
  selection. **Pass if the difference is within seed σ.**
- Known trap carried into P-4: the selection denominator is **doubly defined** in code
  (`n_val_strict_h` with a toggle check vs `h_frame_recall` without) — if the new formula inherits
  that split the repair is hollow. `ACC §4.3 row 3 :368` (D57 defect ③). RT-B's re-adjudication adds
  the v3-specific form of the same risk: **checkpoints selected because they fire on ignore-masked
  frames**. `ACC §4.9 :508-509`
- **⚠ P-4 landed while these materials were being written** — `experiments/v3_0823/P4_SELECTION.md`
  (2026-08-23, concurrent agent). It supplies the concrete numbers this beat was written to leave
  blank: the proposed formula `S = (1−β)·val_F1 + β·Ĥ − 1.0·val_FPR` with β = n_H/(n_H+30) (the old
  0.5/0.5 recovered as the special case n_H = 30), the "fire on everything" strategy going from
  beating **283 of 430 epochs (65.8 %)** under the old rule to **0** under the new one, and the
  constant-output rejection gate **VG-1**. **The formula is submitted for approval and was not
  self-adopted.** The reproduction check splits by unit: **PASS at model-average** (rgb max 0.91σ,
  depth exactly 0) but **FAIL for run rgb_s42** (H −0.427 = 2.63σ), because §2-7 never fixed whether
  "성적" means per-model or per-run — both verdicts are recorded and the unit question is escalated.
  Rewrite this bullet from that ledger rather than from this skeleton.
  `[미결: §2-7 "성적" 단위(모델평균 vs 런) 결재 대기 — P4_SELECTION §승용요약 4]`

### 5.4 Two more repairs that ride along (mention briefly, they gate credibility)
- **G7 re-fusion + re-label** (`DZ §4.3-1`): boost-round height maps never passed the fusion stage, so
  GT was fragmented; the consequence was that scene12's 48 "strict-H" frames were **actually tier V**.
  Measured: defects are exactly 5 pairs across 3 scenes; corpus strict-H 243 → **195** (all scene12,
  and scene12 is in **train**); **test H = 96, unchanged**; but test V 180 → **219** and the headline
  recall denominator 327 → **369**. `DEC D55`, `G7_RELABEL.md`, `ACC §4.2 :345-360` **as corrected by
  ACC §4.4 :371-377**.
  - **Fairness rule that must be stated in the paper's method** `ACC §2-1 :155-164`: "test-core frames
    are invariant" means **images are invariant, not the answer key**. Every A/B compares **both sides
    on corrected GT**; scoring only v3 on corrected GT voids the A/B. The delta against the published
    (old-GT) v2 table goes in a **separate report**, never into the A/B table.
  - The re-score closed the mechanism completely: on the **old** 327-frame denominator, corrected GT
    reproduces the published values to **4 decimal places on every cell** ⇒ G7 repair changed *no
    existing frame's label*, and 100 % of the recall delta is the **42-frame inflow** (V 39 +
    H_weak 3, all scene07). `RS §1.3 :174-196`
- **Sequence hook** (`DZ §4.3-4`): per-scene continuous pose trajectories stored at render-parameter
  level — the raw material for the video-propagation roadmap (see `nearfield_limitation_paragraph.md`).

---

## 6. Beat 6 — pre-registration and the three dashboards

### 6.1 Why the verdict rule is *relative*, and what pre-registration is actually for
`DZ §7.2 :316-322`. `[승용: "그 수치의 타당성을 현재로썬 내가 판단할 근거가 없는 것 같은데"]` — correct.
We do not invent absolute thresholds out of thin air. Pre-registration has exactly **one** purpose:
**to make it impossible to move the goal line after seeing the result**, and registering the *method*
achieves that. Success = **"v3 moves in the correct direction, by more than the seed dispersion σ,
relative to v2."** Only structural gates (constant output, 1-epoch collapse, denominator accounting)
carry absolute numbers, and those numbers are derived from v2 measurements and submitted for approval
with their derivation. **σ is a yardstick for seed dispersion (run reproducibility), not a claim about
a scene-population confidence interval.**

### 6.2 The three dashboards `DZ §7.1 :303-312`

| # | Dashboard | Layer measured | Counterfactual pair | v2 baseline |
|---|---|---|---|---|
| ① | Twin-conditional recall | ③ detection | **(A,C)** | created by re-scoring v2 checkpoints on (A,C); the published 44.7 %/0 % are **(A,D)** reference only |
| ② | CUE-OFF dose–response | ①↔③ | **(A,B)** | optical-mass following (the scene17 paradox) |
| ③ | N-cue trap FA | ④-a | arms C and D alone (§FA_C/FA_D) | **created by zero-shot re-scoring v2 checkpoints on test-ext**; the decoration-preserving off-arm FA **.681** is demoted to an auxiliary reference |

**Venue rule (non-negotiable)** `ACC §2-9 :253-259`: dashboards ①②③ are measured **only on the
test-ext 4 arms**, which **neither** v2 nor v3 has trained on. Measuring the dashboards on the training
corpus's B/C arms makes v3 in-distribution and structurally tilts the comparison. **test-core is for
the headline table and the FA-matched table only.**

### 6.3 Reporting conventions registered during this window (all must appear in the paper's method)

| # | Convention | Source |
|---|---|---|
| 1 | **σ = sample standard deviation, ddof = 1.** range/2 under-estimates σ by ~15 % at n = 3 (E[range] = 1.693σ). All pre-registered verdict σ use this definition. **Note the friction**: `ST §1` and `RS §1.2` print `mean ± range/2`; verdict tests use ddof=1. Captions must say which. | `ACC §4.9-1 :488-489` |
| 2 | **Dashboard ① must carry FA-matching.** "Every recall claim is printed with FA-matching" is this project's own law (`DZ:189`) — applied to the dashboard itself. Dashboard ① is produced at the τ_op single point **and** at the FA-matched points, **on both axes**. | `ACC §4.9-2 :490-492` |
| 3 | **Dual-axis FA-matching is mandatory; printing one axis only is a violation.** Frame axis {.359, .20, .10, .05} + cell axis MAP-C {0.046732, 0.026035, 0.013017, 0.006509}. Every FA citation prints `frame_fa_off`, `cell_fpr_off` **and** cells-per-FA-frame on the same row. | `E12 §6 :150-157`, `ACC §4.8 row 1 :480` (D65) |
| 4 | **FA_C / FA_D always reported separately.** FA_D = the direct gauge of pure scene association; **FA_C − FA_D = the cue-induced false-alarm share**. | `ACC §2-3 :185-199` |
| 5 | **Gate name prefixes**: labeler gates `LG*`, CUE-OFF gates `CG*`, new v3 gates `VG*`. No retroactive renaming; cite old documents as "(구 G2 = LG2)". | `ACC §4.3 row 4 :369` |
| 6 | **Denominators come from ACCOUNTING, single reference.** A number without ① ledger path ② recount command ③ measurement date does not enter. | `ACC §3.4 :328-329` |

---

## 7. Scoped-claim language constraints — the checklist every sentence in this section must pass

These are the **corrected** claim landscape (D52–D65). Each row gives the sentence that is *withdrawn*
and the sentence that *survives*.

| # | Withdrawn | Surviving formulation | Source |
|---|---|---|---|
| 1 | "RGB .688 beats Depth .438" as a modality comparison | "The τ=0.5 single-column comparison is a **threshold illusion**; at matched FA, **Depth ≥ RGB at every point** (FA .10: .510 vs .326). What survives: **RGB recovers 1/3 of hidden frames inside a 10 % FA budget — not zero.**" | PS v2 §1-1 `:25-28` |
| 2 | "YOLO's E/H = 0 is a constructive ceiling" | "**E/H = 0.000 is a property of our `det2cell` adapter**, verified by an oracle-box diagnostic before training; **adapter-free H hit is 0.066**." Every YOLO row is adapter-scoped. | PS v2 §1-1 `:27-28`; `ST §4.2`; METRICS §RT.3 |
| 3 | "H recall implies cue inference" (old §6-4) | Withdrawn outright. Replaced by the three-instrument scene-association diagnosis. | PS v2 §1-2 `:31` |
| 4 | "9/9 CI excludes 0" (old §5.2); any H/E confidence interval | **H/E scene-cluster CIs are WITHDRAWN, not narrowed.** H lives on 2 test scenes with the effect concentrated in scene14; E is a single scene. Scene-generalisation is strengthened by **adding scenes in test-ext**, never by statistics. | PS v2 §1-3 `:32-33`; `DZ §7.2 :320-321`; `ST §2` note |
| 5 | "the aux amodal head gives a significant gain" | Withdrawn (R6-d). The head remains and is used **diagnostically**. **Further**: all 9 main-table runs were measured to have **aux OFF** — DZ §0.1's "it is trained" premise is **false for the main-table models**; DZ correction is Claude AI/승용's to make. Do not describe main-table models as having a trained aux head. | PS v2 §1-3 `:33`; `ACC §4.9-4 :497-501` (RT-B N-5) `[미결: DZ §0.1 정정 대기]` |
| 6 | H claims in general | **3b-only** (forward type, cue-accompanied). **3a (underfoot) is excluded**; its twin Δ ≈ 0 is uniform across 11 poses, i.e. **not a viewpoint artifact**. | PS v2 §1-4 `:34`; 결재 2 `:65` |
| 7 | any near-field performance promise | Out of claim scope, and **for two distinct reasons** — see `nearfield_limitation_paragraph.md`. | PS v2 §1-5 `:35-38`; `DZ §3 :213-218` |
| 8 | "the model fires on cue vocabulary" (D46) | Withdrawn (D49 ①, mass-resolved in `CO §4.4`). Replacement: **"the false-alarm rate is monotone in optical distance and flat in cue inventory."** | `CO §4.4 :447-453` |
| 9 | Gazebo "4/6 ladder inversion" | **5/6.** D48's 4/6 was a miscount, corrected in the ledger. And the section claims **the inversion observation only** — not a vocabulary reading. | `GZ §4.3 :147-157` |
| 10 | any single-axis FA-matched table | **Violation.** Both axes, always. And at τ=0.5 the H ordering **flips with the unit**: frame RGB .688 > Depth .438 ↔ cell Depth .537 > RGB .344. A footnote on both axes is **obligatory** wherever "RGB .688" is written. | `E12 §4`, D65 ⑤ |
| 11 | quoting the CUE-OFF census with a bare number | Always `leg + folded? + n`. Canonical = **primary leg, all blocks, n = 30**; folded (A2-7) **n = 21** printed alongside. | `ACC §1.7 :137-150`, D53 |
| 12 | "v2's FA_C > FA_D shows cues cause false alarms" | **Directional evidence only.** Two classification rules give C 48/D 360 (primary) vs C 264/D 144 (secondary), both printed; RGB's signal is carried entirely by **sceneN3** (a trompe-l'œil hard negative) and **flips sign** when N3 is removed (−0.279); C group is 2 scenes, i.e. effective n ≈ 2. **A pure no-hazard-no-cue FA_D sample does not exist in v2** — building it is the reason arm D exists. | `RS §4.1-4.3 :315-386` |
| 13 | "the corpus denominator is 372" / "none 81→36" | **Arithmetic error, corrected**: none_in_fov 81 → **39**, headline recall denominator 327 → **369** (check: 219+45+96+9+39 = 408). ACC §4.2 is left uncorrected in place per append-only convention — **§4.4 is authoritative.** | `ACC §4.4 :371-377`, D59 ⑦ |
| 14 | "none_in_fov is a large hole in the denominator" | Corrected: under corrected GT the hole is largely **filled**, not merely reduced — ON_NEG event share 56.7 % → **17.5 %**, lift 1.91× → **1.19×**. The agent's own headline recommendation was self-demoted. The residual 39 frames still sit in **no published denominator**, and `labeler.py:526` (post-gate attribution) is **unresolved**. | `ACC §4.7 :461-464`, D63 |
| 15 | present-tense claims about the sim→real pilot | The pilot is unshot. Also blocking: **inference hfov 69° vs training 62.2°** must be fixed before capture (SCOPE-08, blocking-grade). Real-world scoring is **15 of 20 cells** (band1 not annotatable — excluded from the denominator, though model output exists); the asymmetry must be stated in the method section. | `ACC §4.8 row 4 :483`; PS v2 §1-5 `:38`, 결재 7 `:70` |

---

## 8. Optional closing move — "what a failed dashboard would still buy us"

If the dashboards come in under target, `DZ §7.3 :324-329` pre-commits the fallback and it is worth
stating in the paper *before* the results, as a credibility device:
- Exactly **one** spare lever may be pulled autonomously (cue-attribution auxiliary supervision).
  Anything further needs approval — *the moment levers can be pulled without limit, pre-registration
  is meaningless.*
- Even under-target, the **dose–response narrative** — how far it got and what was missing — is itself
  the results section.

**And one asset that already exists regardless of outcome** — the fusion headroom finding, the FA
census's largest single return (`FAC §4 :349-405`, `ACC §4.5 row H`):
- In the OFF stratum, seed-majority FA cells shared by all three models: **0 of 362**.
  `rgb ∩ depth` is **exactly empty** (Jaccard **0.000**). 88.4 % of cells are unique to one architecture.
- ⇒ AND-gating would in principle **annihilate** off-arm FA; 2-of-3 consensus leaves 42/362 (11.6 %).
- **Stated limit**: this is a **ceiling on FA reduction, not a performance guarantee** — if the same
  non-overlap holds for recall, consensus gating kills detection too. The census establishes the
  numerator side only. The cheap next measurement (recall overlap with the same code, using the
  existing `fused_or`/`fused_max` runs) is named in the ledger. `FAC §4.4 :396-405`
- Unchanged under corrected GT: the OFF stratum's 2,212 rows are **row-for-row identical** across both
  GTs, family flags and `method` column included. `ACC §4.7 :447-450`
