# intro_4layer_skeleton — Introduction skeleton on the 4-layer framework

- **Status**: SKELETON / MATERIALS. Not final prose. Claude AI + 승용 own the finished text (D58 ⑥).
- **Written**: Claude Code (CPU-6) · 2026-08-23 · target: v3-frame main paper (English).
- **Rule of this file**: every claim carries a source anchor. A bullet with no anchor is a *drafting
  instruction*, not a claim. Pending decisions are marked `[미결: …]` in Korean.
- **Sources**: `Docs/experiment/V3_DESIGN_0823.md` (=DZ) §1 §2 · `Docs/experiment/Status/PROJECT_STATE_0823_v2.md`
  (=PS v2) · `experiments/v3_0823/FA_REALITY.md` (=FAR) §1.5 §1.6 §5 · `experiments/v3_0823/FA_CENSUS.md`
  (=FAC) §3.3 §3.6 · `experiments/mainrun_0819/DECISIONS.md` (=DEC) D54.

---

## 0. Section map — what the introduction has to do, in order

| # | Beat | Job | Anchor |
|---|---|---|---|
| §1 | Signal geometry | Establish that the direct-measurement channel is *provably* weakest exactly where warning is needed | DZ §1 :36-46 |
| §2 | Risk size ∦ signal size + the H tier | Convert the geometry into the paper's central object of study | DZ §1 :41-45; DZ §0.1 tier row |
| §3 | Human inference example | Show the alternative channel exists and is routine for humans | DZ §1 :57-60 |
| §4 | The two July findings | (a) cues are legally mandated ⇒ the causal arrow licenses the inverse inference; (b) accidents concentrate where cues fail ⇒ layer ④ is mandatory, not optional | DZ §1 :62-67; FAR §5.7, §1.6 |
| §5 | The 4-layer framework + Figure 1 | Give the reader the conceptual spine before any method | DZ §2 :78-99 |
| §6 | Related work positioning | Locate the hole this paper sits in | FAR §1.5 :94-105, §5.1, §5.5 |
| §7 | Contributions | Problem definition / dataset with sim-only labels / hypothesis-test instruments — **not** a new architecture | DZ §1 :69-71 |

**Framing constraint, whole section**: the paper is not an architecture paper. `DZ :69-71` —
"the model is a tool and the *question* is the protagonist"; the contribution axis is
① problem definition (4-layer) ② a dataset that can carry that definition (labels only simulation
can supply: depth, undersurface, twin, 2×2) ③ hypothesis testing (instruments + dashboards).
Keep this identity visible from the first paragraph or §6 (architecture-frozen A/B) reads as a weakness.

---

## 1. Signal geometry — why negative obstacles are hard *in principle*

**Beat 1 — the asymmetry between + and − obstacles.** A positive obstacle (wall, pole) supplies its
own body pixels against the background; its angular size falls as ≈ H/d, i.e. **1/d**. A negative
obstacle has **no body** — the only signal is the interior seen down through the aperture.
`DZ :36-39`

**Beat 2 — the shallow grazing angle multiplies the loss.** A forward camera at height h views the
ground at a grazing angle ≈ h/d. For an opening of width w the visible aperture is the product of
two inverse-proportionalities, ≈ **h·w/d²** — the signal vanishes **as the square of distance**.
`DZ :39-41`. This is the classical result of the negative-obstacle literature (the Heckman line was
our July entry point, `DZ :40-41`); the 1/R² visible-aperture loss is carried by S1 (Matthies &
Rankin, IROS 2003) `FAR §5.1 S1`.

**Beat 3 — our own corpus re-derives the exponent.** The v2 false-alarm census fits
**FA rate ∝ R^1.98** across bands (band2 .0100 → band3a .0289 → band3b .0816; ln residuals
[+0.047, −0.115, +0.068]; ON_NEG fits R^1.35) `FAC §3.3 :223-231`. The census reads this as the
mirror image of the same geometry — the model's uncertainty grows exactly as the aperture shrinks —
and notes the exponent **matches the 30-year-old literature prediction** `FAC :233-237`,
registered as ACCOUNTING §4.5 row G (`experiments/v3_0823/ACCOUNTING.md:392`), and re-verified
unchanged under corrected GT (`ACCOUNTING §4.7 :449-450`).
  - *Drafting note*: this is the strongest single sentence available for §1 — a first-principles
    claim and an independent measurement on our own data agreeing to two decimal places. Whether it
    belongs in the Introduction or in Results is a placement call.
    `[미결: R^1.98을 서론에 미리 놓을지, 결과 절에만 둘지 — Claude AI 판단]`

**Beat 4 — a self-occlusion property unique to this class.** A drop-off is the only obstacle class
whose **own edge occludes its own interior** — which is why the E tier's archetype is self-occlusion.
`DZ :41-42`

---

## 2. "Risk size ∦ signal size" and the H tier

**The load-bearing sentence of the whole paper.** For a fixed aperture, increasing depth adds almost
no visible pixels; and the most dangerous drop-offs — cliff-like — converge to **exactly zero
contributing pixels**. `DZ :42-45`

> Draft line (EN, for §1 close): *"For negative obstacles the size of the risk and the size of the
> signal are not proportional. Depth adds hazard without adding pixels, and in the limit — a sheer
> drop seen from a forward-facing camera — the hazard contributes no pixels at all. The direct
> measurement channel does not merely degrade with danger; it disappears."*

**Tier definitions (must appear before first use)** `DZ §0.1 :21`:
- **V** — interior visible.
- **E** — rim only.
- **H** — **exactly 0 contributing pixels**; only surrounding context remains. **H is the core of
  this research.**

**Scope guard that must ride along with every H claim** (PS v2 §1-4 `:34`, 결재 2):
H claims are **3b-only** — the forward-type, cue-accompanied family. **3a** (underfoot type,
twin Δ ≈ 0 uniformly across 11 poses, i.e. not a viewpoint artifact) is **excluded from the claim**.
Do not let the Introduction promise what §3 of `nearfield_limitation_paragraph.md` then withdraws.

**Summary line for the end of §1** `DZ :44-46`: the direct signal switches off first at exactly the
distance where advance warning matters, and it is *poorest* where the hazard is *worst*. That is the
principled ceiling of direct geometric measurement — and the information channel that survives beyond
it is **context cues**.

---

## 3. Human inference — the existence proof for the alternative channel

**Beat.** A person on a mountain path who sees a fence does not measure what is behind it. They read
**why someone put a fence there**, not what the fence *is*. `DZ :57-58`

**Motivating case (승용's origin motivation)**: autonomous-driving accidents where the system fails
to infer past a barrier (the Tesla-FSD-class example 승용 raised) — can contextual inference prevent
that class? `DZ :58-60`
  - *Drafting note*: keep this as motivation, not as a claim about any specific vendor's system.
    The repo carries no first-party incident analysis of that case. `[미결: FSD 사례를 본문에 명시할지
    각주로 내릴지 — 인용 가능한 1차 출처가 repo에 없음]` Adjacent citable incidents that **are**
    sourced: Starship delivery robot into a canal (S26), Cruise robotaxi into wet concrete (S27)
    `FAR §1.6 :113-114`.

**The inference form to state explicitly** `DZ §2.1 :109-111`:
observation (railing) → abduce the *reason* (drop-off protection) → update existence probability.
Corollary that becomes a diagnostic rule later: **if there is no observation there should be no
update** — systematic firing on cue-free frames cannot be explained by layer ①.

---

## 4. The two July findings — the two pillars of the design

### 4.1 Finding 1 — artificial cues are legally mandated installations, so the causal arrow runs hazard → cue

**Claim** `DZ :63-65`: railings, tactile warning blocks, signs are in large part **statutory
installations** — they are tied to hazard **causally**, not decoratively. Direction matters:
**the hazard causes the cue**. That is precisely what licenses the *inverse* inference cue → hazard.

**Regulatory sources (all first-party statute/standard text, `FAR §5.7`)**:

| ID | Instrument | What it mandates | Why it matters here |
|---|---|---|---|
| S31 | 「교통약자의 이동편의증진법 시행규칙」 별표2 | sidewalk/roadway height difference ≤ 2 cm; **점형블록** at crosswalk entries; curb ramp ≥0.9 m, ≤1/12 | **Mandates removing the drop AND installing the warning block at the same place** |
| S32 | U.S. Access Board PROWAG ch. R3 | detectable warning surfaces at curb ramps, **blended transitions**, **flush** street↔sidewalk transitions | Same structure in a second jurisdiction — ADA-side isomorph |
| S33 | ADA §705 / §810 | detectable warnings at **bus and rail boarding platform edges** | Cue at a *platform*, not a *drop* |
| S34 | 「건축법 시행령」 제40조 | ≥1.2 m railing required at **rooftop plazas / balconies 2F+** only | ⇒ ground-level planter railings carry **no** fall-protection duty |
| S35 | 국토교통부 차량방호 안전시설편 | vehicle barriers exist to **stop vehicles leaving the road**, not to stop pedestrians falling | Guardrail ≠ fall cue |
| S36 | 행안부 볼라드 설치기준 | bollards deter **vehicle entry onto sidewalks** | Bollard ≠ fall cue |
| S37 | 국민권익위 보도자료 | tactile blocks mis-installed: 파손 1,257 / 침범 603 / 미설치 596 / **오설치 재시공 325건** | Mis-sited cues are a **measurable real distribution**, not a synthetic trap |

**The double-edged reading — this is what makes the argument non-trivial, and it must be in the
Introduction, not deferred**: the same regulatory corpus that makes cue → hazard inference *valid*
(S31/S32/S33: mandated at real edges) also **guarantees a population of cues standing where there is
no drop at all** (S34/S35/S36: railings, guardrails and bollards installed for entirely different
statutory purposes; S37: measured mis-installation volume). `FAR §5.7 :294-303`, `DEC D54 ④`.
That guaranteed population is the paper's **N-cue** class — the ④-a hard negatives — and its
existence is a *legal* fact before it is an experimental design choice.

> Draft line (EN): *"The regulation that makes the inference sound is the same regulation that makes
> it fallible: it mandates a cue wherever there is a mandated edge, and it mandates cues of identical
> visual form — bollards, vehicle guardrails, planter railings — where there is no edge at all."*

### 4.2 Finding 2 — accidents concentrate exactly where cues are absent or defeated

**Claim** `DZ :66-67`: accidents cluster in natural terrain, poorly maintained stretches, and
removed/worn installations. A system that trusts **cues alone** goes silent in the most dangerous
places. This is the necessity argument for layer ④ (specifically ④-b, cue false-negatives).

**Incident/statistical sources (`FAR §1.6 :107-121`)**:
- Open-manhole fatality, NYC 2026-05 — cover displaced by a truck, **uncovered ~12 min**, 3 m fall,
  fatal; repeat cases St. Louis 2026-07, Buffalo, with **unclear ownership of maintenance** as the
  recurring factor (S25).
- Delivery robot drove straight into a canal, Milton Keynes (S26).
- Cruise robotaxi into freshly poured concrete, SF 2023-08 (S27).
- OSHA/NSC: excavations in traveled areas **must** be isolated by physical barrier — the recurring
  failure type is the window between excavation and barrier, and night-time removal without
  reinstatement (S28).
- iRAP run-off-road: **80 % of ROR fatalities on rural roads**, ~90 % of those on rural two-lane;
  severity rises with embankment/drop height (S29).

**The design consequence to state here (not later)** `FAR :118-121`, `DZ §2.4 (b) :169-173`: for
cue-free hazards the honest target is **not** confident detection — it is a **low but non-zero
calibrated probability plus cautious action**. 승용's formulation, quoted in DZ:
`[승용: "사람도, 처음 보는 환경이면 H라벨에선 추측만 할 수 있지, 직접 보기 전까진 fake인지도 모르니깐"]`
`DZ :171-172`. This single sentence determines the supervision rule (ignore mask for bare-occlusion H,
DZ §5.1) and should be foreshadowed in the Introduction so §Method reads as a consequence rather than
a convenience.

---

## 5. The 4-layer framework and Figure 1

### 5.1 Prose skeleton (the layers, in the order a human actually reasons) `DZ §2 :78-94`

1. **③ Scene prior** — "this is an embankment path" → lays down a **base rate**.
2. **① Existence cue** — "there is a railing; the ground texture terminates over there" → **updates**
   the probability with evidence.
3. **④ Trust degradation** — "but that railing could be a flower-bed surround / it is backlit and
   hard to read" → adjusts the weight of the evidence and makes the **magnitude of confidence honest**
   (= a calibrated probability).
4. **② Severity** — "if it is there, how deep, and what is at the bottom" → scores the **size** of the risk.
5. **Action** — slow / detour / observe more / stop.

**Two propositions that must be nailed before the figure** `DZ :96-99`:
- **(a) A cue is evidence, not an answer.** Therefore the output must be a probability, not a verdict,
  and layer ④ is what makes that probability honest.
- **(b) The four layers are not model modules.** They are a design principle for **data axes,
  supervision rules and evaluation dashboards**. (The only structure-enforced variant is v3-B /
  option C, `DZ §6`.) Misreading (b) produces the "build four modules" error `DZ §2.5-4 :190`.

**Per-layer one-liners for the paper (compressed from DZ §2.1–2.4)**:

| Layer | Definition | Failure mode | How v3 implements it |
|---|---|---|---|
| ① Existence cue | observable signal that raises/lowers the probability of an unobserved drop | miss (cannot read the cue) / false fire (fires with no cue = ③ trespass; fires on any cue = ④ absent) | orthogonal 2×2 (target \|r\| ≤ 0.2, measured value reported) `DZ :117-118` |
| ② Severity | depth, undersurface, entrapment — the magnitude given existence | "detected existence, no severity estimate" was an independent accident mechanism in the July survey | labels emitted in full (`depth_m`/`undersurface`/`entrapment`) + analysis; **no prediction head this round**, to protect A/B attribution `DZ :132-136` |
| ③ Scene prior | base rate from scene type; posterior ∝ evidence × prior | **usurpation** — prior impersonates evidence ("looks like a construction site → hazard"). This is the disease v2 had | scene diversification + unseen-scene eval (test-ext) + hazard-free arms; **FA_D is the direct gauge of pure scene association** `DZ :152-155` |
| ④ Trust degradation | everything that modulates how far a cue may be trusted: (a) N-cue false positives, (b) cue-free hazards, (c) observation degradation (backlight, wear, occlusion, distance) | absent entirely in v2 — "there was no logic for when a cue does *not* mean a drop" `[승용]` `DZ :163-164` | N-cue hard-negative group + cue-conditional supervision + ignore mask + T-scaling with reliability curve / ECE `DZ :178-180` |

### 5.2 Figure 1 — caption draft and drawing spec

**Working title**: *Figure 1 — Four layers of drop-off inference.*

**Caption draft (EN, ~60 words)**:
> *The order in which a person reasons about an unseen drop-off. A scene prior sets the base rate (③);
> observable cues update it as evidence (①); trust-degrading factors reweight that evidence and make
> the resulting confidence honest (④); severity scores the consequence if the hazard is real (②); the
> calibrated probability then drives action. The layers are design axes for data, supervision and
> evaluation — not network modules.*

**Drawing spec** (translate DZ §2's ASCII block `:80-94`):

| Item | Spec |
|---|---|
| Topology | 5 boxes in a **single vertical chain**, top→bottom: ③ → ① → ④ → ② → Action. One arrow between consecutive boxes. **Do not** draw a 2×2 grid or a cycle — the chain order *is* the claim. |
| Box 1 | Label **③ Scene prior**. Example text: "this is an embankment path". Right-side annotation: **"lays down a base rate"**. |
| Box 2 | Label **① Existence cue**. Example: "there is a railing; the ground texture terminates there". Annotation: **"updates the probability with evidence"**. |
| Box 3 | Label **④ Trust degradation**. Example: "but that railing may be a flower-bed surround / backlit and hard to read". Annotation: **"reweights the evidence and makes the confidence honest (= calibrated probability)"**. |
| Box 4 | Label **② Severity**. Example: "if it is there, how deep, and what is below". Annotation: **"scores the size of the risk"**. |
| Box 5 | Label **Action**. Contents: "slow / detour / observe more / stop". Draw with a different outline (dashed or filled) — it is a consumer, not a layer. |
| Emphasis | ④ gets the visual accent (heavier border / accent fill). It is v3's decisive layer (`DZ :163`) and the layer v2 lacked entirely. |
| Ordering note | The numbering (③①④②) is deliberately out of numeric order. Add a small footnote in the caption: *"Numbering follows the original framework, not the reasoning order."* Otherwise a reviewer reads it as a typo. |
| Optional right gutter | A thin second column mapping each layer to its **instrument**: ③→dashboard ① (twin-conditional) & FA_D; ①→dashboard ② (CUE-OFF dose–response); ④→dashboard ③ (N-cue FA) + ECE; ②→severity labels (analysis only, this round). Sourced from `DZ §7.1 :303-312` and the table in §5.1 above. `[미결: 계기판 매핑을 Fig.1에 넣을지 별도 Fig.2로 뺄지 — 밀도 판단]` |
| Colour / theme | Must read in greyscale (print). Use border weight + fill tint, never hue alone, to carry the ④ emphasis. |
| Do-not | Do not label any box with a network component name (encoder/head/decoder). That is exactly misreading (b) `DZ :190`. |

---

## 6. Related work — positioning paragraph skeleton

**Target: one paragraph, three moves, then the claim of position.** All three moves are already backed
by first-party sources; `FAR §1.5 :103-105` states the repo's own certification of this
("세 문장 모두 1차 출처로 뒷받침된다 (S1, S2, S3, S21, S22)").

**Move 1 — the geometry closes the direct channel.** Negative obstacles vanish geometrically at range
(1/R² visible-aperture loss) — S1 (Matthies & Rankin, *Negative Obstacle Detection by Thermal
Signature*, IROS 2003) and S2 (Rankin, Huertas & Matthies, SPIE 6561, 2007). The ambiguity is
intrinsic, not a sensor deficiency: S3 quotes the 2007 paper verbatim —
> ***"one cannot tell if there is a slight depression that is traversable, or a deep trench"***
> — `FAR §5.1 S3 :236` (terrain self-occlusion ambiguity; trailing-edge upslope).

**Move 2 — intensity cues were pre-emptively dismissed, and the field pivoted to thermal.** The
canonical line's answer to invisible geometry was **thermal signature**, on the reasoning that
intensity cues are illumination-dependent and false-alarm-prone. FAR's own summary of the pivot:
*"기하가 안 보일 때 문헌의 답은 열이었다"* — and it explicitly names the resulting hole as this
project's position: **"RGB 맥락단서 연구의 공백"** `FAR §1.5 :101`. Registered in `DEC D54 ⑤`:
*"Matthies&Rankin'03이 우리 단서 채널을 선제 기각하고 열화상으로 우회('조명 의존·오경보') = 본 연구가
앉은 구멍의 문헌적 좌표."*
  - **⚠ QUOTE VERIFICATION REQUIRED — do not draft a verbatim sentence from this yet.** The only
    verbatim fragment the ledger carries from S1 is **"great potential for false alarms"**
    (`FAR §5.1 S1 :234`). The "pre-emptively dismissed intensity cues → pivoted to thermal"
    formulation is a **paraphrase** recorded in `DEC D54 ⑤` and `FAR :101`, **not** a quotation
    present in the repo. Before the paper prints a quotation mark, someone must open the S1 PDF
    (https://www-robotics.jpl.nasa.gov/media/documents/matthies-negobs.pdf) and lift the exact
    sentence with its page.
    `[미결: S1 원문 대조 1회 필요 — 인용부호를 붙일 문장을 확정할 때까지 이 문단은 패러프레이즈로만 쓴다]`
  - Corroborating datum for the same move, if a second citation is wanted: the false-alarm modes the
    thermal line itself reported — above-ground warm horizontal structure (S2) and warm **wheel
    tracks**, 3/96 frames (S1) `FAR §1.4 D4/D5 :90-91`. Useful because it shows the pivot did not
    escape the false-alarm problem, it relocated it.

**Move 3 — the major off-road datasets have no negative-obstacle class at all.** `FAR §1.5 :98-100`:
- **RELLIS-3D** — 20 classes including `void`, `puddle`, `barrier`, `fence`, `water`, `rubble` …
  and **no hole / ditch / trench / cliff / drop-off class** (S21).
- **ORFD** — traversable / non-traversable / **unreachable** only; the drop-off is absorbed into
  "unreachable", i.e. it is a **residual category, not an independent label** (S22).
- **RUGD** — merged operation as Smooth/Rough/Bumpy/Forbidden/Obstacle/Background (S22).
- (CAVS Off-Road, 12,300 images, traversability-annotated — S23, same shape.)

**Move 4 — our position, stated as a positive claim.** Cue-mediated contextual inference, supervised
by **counterfactual labels that only simulation can supply**. Spell out what "only simulation" buys,
because that is the dataset contribution `DZ :70, :132`:
- **depth below the edge / undersurface / entrapment** — unlabelable in the real world by
  construction (you cannot annotate the bottom of a cliff you cannot see);
- **twin pairs** — the same camera cut with the hazard removed and nothing else changed;
- **the orthogonal 2×2** — hazard ⊥ cue, which no real-world capture can enforce.

> Draft line (EN, close of related work): *"Where the literature answered invisible geometry by
> changing the sensor, we keep the sensor and change what the label means: instead of asking a
> monocular model to measure a hazard it cannot see, we ask it to infer one from the context that
> surrounds it — and we build the counterfactual supervision that makes 'inferred' separable from
> 'memorised'."*

**Explicit non-claims to keep in the paragraph (guard against reviewer over-read)**:
- We do **not** claim monocular RGB beats depth. PS v2 §1-1 `:25-28`: at matched false-alarm rate,
  **Depth ≥ RGB at every operating point** (FA .10: .510 vs .326); the surviving sentence is
  "RGB recovers 1/3 of hidden frames within a 10 % FA budget (which is not zero)."
- We do **not** claim a constructive ceiling for detectors. YOLOv8n's E/H = 0.000 is a property of
  **our det2cell adapter**; adapter-free H hit is **0.066** (PS v2 §1-1 `:27-28`, METRICS §RT.3).
- We do **not** claim the July accident survey is exhaustive. `DZ :55` marks it as
  "조사 결과의 인용이지 전수 단정이 아니다" — keep the hedge in translation.

---

## 7. Contribution list — draft bullets

1. **A problem definition**: the 4-layer framework, and the observation that layer ④ — when a cue may
   *not* be trusted — is what the existing formulation of the task omits. `DZ §2`
2. **A corpus that can carry it**: orthogonal 2×2 arms (A/B/C/D) with hazard ⊥ cue enforced by
   construction (`|r|` predicted 0.004 in the render plan, `experiments/v3_0823/RENDER_PLAN_V3.md`;
   measured value to be reported), cue-conditional supervision, and severity labels that only
   simulation can produce. `DZ §4.1, §4.4, §5.1`
3. **Three pre-registered instruments** that separate *inference* from *association*: twin-conditional
   recall (A,C), CUE-OFF dose–response (A,B), N-cue trap FA. `DZ §7.1`
4. **An honest version journey** — v2's headline and its demolition by our own instruments — offered
   as a contribution in its own right (see `version_journey_skeleton.md`).
   `[승용/교수님 지침: "실패 하나하나도 좋은 기여로 담길 수 있으니"]` `DZ :328-329`

---

## 8. Traceability index for this file

| Introduction beat | Primary anchor | Corroborating measurement in repo |
|---|---|---|
| h·w/d² vanishing | `DZ:36-46` | `FAC §3.3` R^1.98 (`ACCOUNTING.md:392`, re-verified `:449-450`) |
| risk ∦ signal, H tier | `DZ:42-45`, `DZ:21` | `SEED_TABLE.md §1` H columns; `V2_RESCORE.md §1.2` |
| 3b-only scope | `PS v2 :34`, 결재 2 (`PS v2 :65`) | `MORNING_REPORT_0823.md` §2 |
| human fence inference | `DZ:57-60` | — (motivational) |
| finding 1 (statutory cues) | `DZ:63-65` | `FAR §5.7` S31–S37 |
| finding 2 (accidents where cues fail) | `DZ:66-67` | `FAR §1.6` S25–S29 |
| 4-layer chain / Fig. 1 | `DZ:78-99` | — |
| ④-b honest-target rule | `DZ:169-173` | `FAR:118-121` |
| thermal pivot | `FAR:101`, `DEC D54 ⑤` | **verbatim quote unverified — see §6 Move 2 warning** |
| no negative-obstacle class | `FAR §1.5:98-100` (S21,S22,S23) | — |
| Depth ≥ RGB at matched FA | `PS v2:25-28` | `V2_RESCORE.md §3.1`; `EVL12_CELL_AXIS.md §2` |
