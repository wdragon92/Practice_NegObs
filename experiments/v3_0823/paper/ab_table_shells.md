# ab_table_shells — A/B result table shells (NUMBERS DELIBERATELY BLANK)

- **Status**: SKELETON / MATERIALS. Not final prose, not results. Claude AI + 승용 own final layout
  and prose (D58 ⑥).
- **Written**: Claude Code (CPU-6) · 2026-08-23 · target: v3-frame main paper (English).
- **Why blank**: v3 has not been rendered or trained. Every cell is `___`. **Filling a cell before the
  run is a pre-registration violation** (`DZ §7.2 :316-322`, `DZ §9 :357`). The shells exist so that
  the table *shape* is frozen before the numbers arrive — that is the point of pre-registration.
- **Universal rules applied to every table below** (do not restate them per-table in the paper — put
  them once in §Method and reference):

| Rule | Statement | Ledger |
|---|---|---|
| R-1 | **Denominators come from `ACCOUNTING.md`, single reference.** A number without ① ledger path ② recount command ③ measurement date does not enter. | `ACC §3.4 :328-329` |
| R-2 | **Both A/B sides scored on corrected GT (정본 B).** Images invariant ≠ answer key invariant. Scoring only v3 on corrected GT **voids** the A/B. Old-GT deltas go in a separate report. | `ACC §2-1 :155-164` |
| R-3 | **σ = sample standard deviation, ddof = 1** for every verdict. `range/2` under-estimates σ by ~15 % at n = 3. Where a table prints `± range/2` (legacy convention of `SEED_TABLE.md §1`, `V2_RESCORE.md §1.2`) the caption must say so explicitly. | `ACC §4.9-1 :488-489` |
| R-4 | **Dual-axis FA reporting is mandatory.** Frame axis {.359, .20, .10, .05} + cell axis MAP-C {0.046732, 0.026035, 0.013017, 0.006509}. **Printing one axis only is a violation.** Every FA citation carries `frame_fa_off`, `cell_fpr_off` and cells-per-FA-frame on the same row. | `E12 §6 :150-157`; `ACC §4.8 row 1 :480` |
| R-5 | **Cells-per-FA-frame estimator must be named**: "seed-pooled" or "seed-averaged". They differ (Depth: 4.29 pooled vs 5.50 averaged; RGB 2.60/2.61, effectively identical). `[미결: 정본 추정량 미확정 — E12 §6-3이 결재 요청]` | `E12 §3 :96-99` |
| R-6 | **Dashboards ①②③ are measured on test-ext 4 arms only** (neither v2 nor v3 trained on them). test-core is for the headline table and FA-matching **only**. | `ACC §2-9 :253-259` |
| R-7 | **Verdict form** (all dashboards): success = *v3 moves in the pre-registered correct direction by more than σ (ddof=1, over 3 seeds) relative to v2*. No absolute thresholds except structural gates. | `DZ §7.2 :316-322` |
| R-8 | **"Twin" is never written without naming the pair.** (A,C) = hazard removed / cue kept · (A,B) = cue removed / hazard kept · (A,D) = old-off generation, comparative narration only. | `ACC §2-2 :166-183` |
| R-9 | **All recall claims print FA-matching alongside** — including the dashboards themselves. | `DZ :189`; `ACC §4.9-2 :490-492` |

**Legend used in every shell**: `___` = to be measured · `n=___` = denominator pending ACCOUNTING
append · **bold** = the cell the verdict rule reads.

---

## Table 1 — Dashboard ① · Twin-conditional recall on the (A,C) pair

### 1.1 Caption draft
> **Table 1. Twin-conditional recall, (A,C) pair, test-ext.** A hazard-ON frame counts as a hit only
> if the model fires on a GT-positive cell **and** its byte-paired counterfactual twin — the same
> camera cut with the hazard removed and the cue preserved — does **not** fire on those same cells.
> Both v2 and v3 checkpoints are scored on the identical test-ext arms, which neither model trained
> on. Recall is reported at the operating point τ_op = 0.5 and at the pre-registered FA-matched
> points on both axes; a recall figure without its FA-matched companion is not interpretable
> (Section [Method]). Dispersion is the sample standard deviation over three seeds (ddof = 1).

### 1.2 Shell — τ_op single point

| tier | arm | model | v2 recall (published rule) | v2 **twin-cond. (A,C)** | v3 recall | v3 **twin-cond. (A,C)** | Δ (v3−v2) | σ_v2 | σ_v3 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| H (3b) | A vs C | rgb | ___ | **___** | ___ | **___** | ___ | ___ | ___ | ___ |
| H (3b) | A vs C | depth | ___ | **___** | ___ | **___** | ___ | ___ | ___ | ___ |
| H (3b) | A vs C | b2 | ___ | **___** | ___ | **___** | ___ | ___ | ___ | ___ |
| E (far) | A vs C | rgb | ___ | **___** | ___ | **___** | ___ | ___ | ___ | ___ |
| E (far) | A vs C | depth | ___ | **___** | ___ | **___** | ___ | ___ | ___ | ___ |
| E (far) | A vs C | b2 | ___ | **___** | ___ | **___** | ___ | ___ | ___ | ___ |
| V | A vs C | rgb | ___ | **___** | ___ | **___** | ___ | ___ | ___ | ___ |
| V | A vs C | depth | ___ | **___** | ___ | **___** | ___ | ___ | ___ | ___ |
| V | A vs C | b2 | ___ | **___** | ___ | **___** | ___ | ___ | ___ | ___ |

Auxiliary columns to print with the above (they are what made the v2 diagnosis legible):
`off-arm (C) twin fire rate` and **`share of fires that are unconditional`** — one column pair per
model. `F2 §1` is the exact column set to mirror.

### 1.3 Shell — FA-matched companion (R-4, R-9), dual axis

| axis | target FA | achieved FA | model | v2 twin-cond. H | v3 twin-cond. H | Δ | σ (ddof=1) | seeds v3>v2 | verdict |
|---|---|---|---|---|---|---|---|---|---|
| frame | .359 | ___ | rgb / depth / b2 | ___ | ___ | ___ | ___ | _/3 | ___ |
| frame | .200 | ___ | ″ | ___ | ___ | ___ | ___ | _/3 | ___ |
| frame | .100 | ___ | ″ | ___ | ___ | ___ | ___ | _/3 | ___ |
| frame | .050 | ___ | ″ | ___ | ___ | ___ | ___ | _/3 | ___ |
| **cell** | .046732 | ___ | ″ | ___ | ___ | ___ | ___ | _/3 | ___ |
| **cell** | .026035 | ___ | ″ | ___ | ___ | ___ | ___ | _/3 | ___ |
| **cell** | .013017 | ___ | ″ | ___ | ___ | ___ | ___ | _/3 | ___ |
| **cell** | .006509 | ___ | ″ | ___ | ___ | ___ | ___ | _/3 | ___ |

Cell-axis targets are **MAP-C**, derived from published quantities alone: anchor = RGB's published
operating point cell FPR (3-seed mean **0.046732**), then the same reduction schedule as the frame
axis (×.200/.359, ×.100/.359, ×.050/.359). No rounding, no new judgement. `E12 §1 :31-36`

### 1.4 Denominator source
- **Pending**: `ACC §3.4` open item **2** (test-ext scene list, frame counts, 4-arm decomposition) and
  item **3** (test-ext paired-H count per scene). Both fill at P-5 render completion.
- test-ext paired-H target ≥ 10 scenes; H statistics currently trapped in 2 scenes (effectively
  scene14). `DZ §4.2 :235-236`
- **Every existing v2 scene fails the 4-arm requirement** (all 8 scenes that admit 4 arms without
  modification have v2 train/test history) ⇒ **paired-H ≥ 10 is entirely new scenes**. `DEC D56`
- v2 reference figures for the same quantity on **test-core** (old (A,D) generation, **reference
  only**): n = 96 kept H pairs/run; RGB twin-conditional H 0.375, unconditional share 0.447; Depth
  0.438 / 0.000. `F2 §1`. **These must not be placed in a v3 A/B cell** — different generation
  (R-8, `ACC §2-2 :181-182`).

### 1.5 Pre-registered verdict rule
- **Direction**: twin-conditional H recall **UP** for v3 vs v2, and **unconditional-fire share DOWN**.
- **Magnitude**: |Δ| > σ, σ = sample sd (ddof = 1) over the 3 seeds. `ACC §4.9-1`
- **Must hold on both axes** to be reported as a clean win; a frame-axis-only movement is reported as
  axis-dependent and labelled as such. `E12 §0, §4`
- **Failure is still a result**: report the dose–response narrative (`DZ §7.3 :328-329`).
- **Gates before the table is admissible**: `VG-datum` — |Δground_z| check on every C-arm pair
  (v2 precedent: 183/792 pairs dropped on ground_z movement). `ACC §4.9-5 :502-503`. Plus the D58 ①
  precision conditions: ⓐ tier purity (per-frame machine predicates; re-adjudicate tier after arm-A
  render) ⓑ **edge-ownership gate** (a visible edge in an A-arm H frame must belong to the occluder
  geometry, checked mechanically with the ID mask; unjudgeable → boundary bucket, **not counted as H**)
  ⓒ real-vs-sim qualitative panel.

---

## Table 2 — Dashboard ② · CUE-OFF dose–response, (A,B) pair

### 2.1 Caption draft
> **Table 2. CUE-OFF dose–response, (A,B) pair, test-ext.** The intervention removes the cue while
> holding the hazard geometry invariant (hash-gated). The question the table answers is not whether
> false alarms exist but **what they track**: the number of cues removed, or the optical mass of the
> change to the picture. In v2 the answer was optical mass — a scene retaining its full cue vocabulary
> but differing from the hazard-off round by 1.02 % of pixels produced a false-alarm rate of .042,
> while scenes differing by 36.6–58.4 % produced 1.000. A model that has learned layer ① should show
> the opposite ordering: response monotone in cue count and flat in optical mass.

### 2.2 Shell — the dose–response body

| scene · band | Δ optical mass vs off-round (≥32/255) | # cues removed | cue vocabulary preserved? | v2 FA(arm) rgb | v2 FA(arm) depth | v2 FA(arm) b2 | v3 FA(arm) rgb | v3 FA(arm) depth | v3 FA(arm) b2 |
|---|---|---|---|---|---|---|---|---|---|
| ___ | ___ % | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| ___ | ___ % | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| ___ | ___ % | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| ___ | ___ % | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |

### 2.3 Shell — the two competing regressions (this is the actual verdict object)

| model | version | slope vs **optical mass** | R² | slope vs **cue count** | R² | which dominates | σ (ddof=1) |
|---|---|---|---|---|---|---|---|
| rgb | v2 | ___ | ___ | ___ | ___ | ___ | ___ |
| rgb | v3 | ___ | ___ | ___ | ___ | ___ | ___ |
| depth | v2 | ___ | ___ | ___ | ___ | ___ | ___ |
| depth | v3 | ___ | ___ | ___ | ___ | ___ | ___ |
| b2 | v2 | ___ | ___ | ___ | ___ | ___ | ___ |
| b2 | v3 | ___ | ___ | ___ | ___ | ___ | ___ |

### 2.4 Denominator source and census-citation rule
- **Pending**: `ACC §3.4` items 2 and 4.
- **v2 baseline census, canonical citation form** (R: never a bare number): **primary leg, all blocks,
  n = 30 cells**, of which **12 judgeable**; folded (A2-7) **n = 21** printed alongside; the "24" that
  appears elsewhere is the same population minus the six s20fix repair cells (all VOID) — an inclusion
  relation, not a disagreement. `ACC §1 :17-150`, `ACC §1.7 :137-150`, `DEC D53`
- v2 result to state as the baseline: **CUE EVIDENCE = 0** under the pre-registered primary rule.
  `CO §6.4 :720-723`
- v2 dose–response reference row set (`CO §4.4 :440-445`): 58.35 %→1.000 · 36.60 %→1.000 ·
  13.09 %→0.361 · **1.02 %→0.042**, cue vocabulary preserved in all four.
- **Coverage caveat to print with the v2 side**: the v2 intervention had **1 effective scene (s17)**
  after adjudication; the bottleneck was strict-H availability, not toggle wiring (33/33 scenes carry
  ≥1 removal toggle). s14's guard is *structural* and cannot be toggled. `DEC D56`, `ACC §2-6 :220-228`
- **Confound that survives into v3 and must be printed**: "cues" and "a third of the picture" were
  perfectly confounded in every v2 arm, and the best-matched placebo (removing non-cue objects) did
  *more* damage than removing the guard. `CO §6.4 :735-738`. v3's answer is the hash-gated
  `cue_material_break` lever (material rebinding only, height-map bits guaranteed identical) — the
  optical-mass axis must still be *measured and printed*, not assumed to be zero. `DEC D56`, `CC`

### 2.5 Pre-registered verdict rule
- **Direction**: for v3, the **cue-count slope rises** and the **optical-mass slope falls** relative to
  v2 (i.e. the dominant regressor flips). This is a *pattern* verdict, not a single scalar.
- **Magnitude**: each slope's change exceeds σ (ddof = 1) over 3 seeds.
- **Reported regardless**: the four-point curve itself. Even an under-target result yields the
  dose–response narrative that `DZ §7.3` pre-commits as a results section.
- **Disqualified-candidate protocol (inherited, keep it)**: if a candidate cell fails a gate, print
  the number it *would* have given next to the reason it does not count — v2 precedent **+0.506**,
  disqualified twice. `CO §6.4 :721-726`

---

## Table 3 — Dashboard ③ · N-cue trap FA, with FA_C / FA_D decomposition

### 3.1 Caption draft
> **Table 3. N-cue trap false alarms and the cue-induced share, test-ext.** Arms C (cue present,
> no hazard) and D (neither) are scored alone. FA_D is the direct gauge of pure scene association:
> with neither cue nor hazard in frame, whatever remains is atmosphere. **FA_C − FA_D isolates the
> cue-induced false-alarm share.** The v2 baseline is produced by zero-shot re-scoring the frozen v2
> checkpoints on the same test-ext arms, which neither model trained on; the decoration-preserving
> off-arm figure of .681 quoted in earlier work is an auxiliary reference only. Lower is better in
> every column.

### 3.2 Shell — main body

| version | model | **FA_C** (arm C) | n_C | **FA_D** (arm D) | n_D | **FA_C − FA_D** | σ (ddof=1) | cell FPR_C | cell FPR_D | cells/FA-frame (estimator: ___) |
|---|---|---|---|---|---|---|---|---|---|---|
| v2 (zero-shot) | rgb | ___ | n=___ | ___ | n=___ | ___ | ___ | ___ | ___ | ___ |
| v2 (zero-shot) | depth | ___ | n=___ | ___ | n=___ | ___ | ___ | ___ | ___ | ___ |
| v2 (zero-shot) | b2 | ___ | n=___ | ___ | n=___ | ___ | ___ | ___ | ___ | ___ |
| v3-A | rgb | ___ | n=___ | ___ | n=___ | ___ | ___ | ___ | ___ | ___ |
| v3-A | depth | ___ | n=___ | ___ | n=___ | ___ | ___ | ___ | ___ | ___ |
| v3-A | b2 | ___ | n=___ | ___ | n=___ | ___ | ___ | ___ | ___ | ___ |
| v3-B (attn) | rgb | ___ | n=___ | ___ | n=___ | ___ | ___ | ___ | ___ | ___ |

### 3.3 Shell — N-cue difficulty ladder stratification (the ④-a discriminative view)

The N-cue group is specified as a 12-rung difficulty ladder, ★1 (obvious) → ★5 (subtle), each rung
carrying its statutory justification for why a cue stands with no drop behind it. `FAR §3 :159-193`

| rung | ★ | scene (N-cue) | statutory basis | v2 FA_C | v3 FA_C | Δ | σ |
|---|---|---|---|---|---|---|---|
| L1 | ★☆☆☆☆ | flat planter-bed railing | 「건축법 시행령」제40조 — fall-protection railings are mandated only at rooftop plazas / 2F+ balconies, **not** at ground-level planters (S34) | ___ | ___ | ___ | ___ |
| L2 | ★☆☆☆☆ | bollard row on flat sidewalk | 행안부 bollard standard — purpose is deterring **vehicle** entry (S36) | ___ | ___ | ___ | ___ |
| L3 | ★★☆☆☆ | vehicle guardrail beside flat sidewalk | 국토부 차량방호 지침 — purpose is preventing **vehicles** leaving the road, not pedestrian falls (S35) | ___ | ___ | ___ | ___ |
| … | … | … | … | ___ | ___ | ___ | ___ |
| L11 | ★★★★☆ | intact temporary works left after excavation is restored | MUTCD-line practice: signage not applicable must be removed or covered; stale signage erodes credibility (S30) | ___ | ___ | ___ | ___ |
| L12 | ★★★★★ | weak-cue superposition at an alley corner (convex mirror + delineators + shadow band) | convex mirror is installed for **sight distance**, delineators for lane separation; a lighting-family FA is superposed to decompose which family drives the firing | ___ | ___ | ___ | ___ |

*(Full 12 rungs at `FAR §3`; the table above is the shape, not the final selection.)*
`[미결: 사다리 12종 중 test-ext 편입 개수·비율·페어링 미확정 — FAR §6 "비율·페어링 결정 후 확정"]`

### 3.4 Denominator source
- **Pending**: `ACC §3.4` item **4** — FA_C / FA_D denominators (no-hazard frame counts per arm),
  fills at test-ext render completion.
- **v2 has no true FA_D sample.** The v2 off arm is heterogeneous: 8 scenes keep their cues (≈C-like)
  and 25 delete them with the hazard (≈D-like); even among the "D-like" five test scenes, four keep
  free-standing `cue_scene_dressing`. **Building a pure no-hazard-no-cue sample is arm D's reason for
  existing.** `ACC §4.1 :335-343`; `RS §4.3 :380-384`
- **The v2 directional-only decomposition, if quoted at all, must carry its four caveats**
  (`RS §4.1-4.3 :315-386`): (i) two classification rules, both printed — primary C 48 / D 360,
  secondary C 264 / D 144; (ii) all three models show FA_C-like > FA_D-like, matching the §2-3
  prediction; (iii) **RGB's signal is carried entirely by sceneN3** (a trompe-l'œil hard negative) and
  **flips sign to −0.279** when N3 is removed, while depth (+0.267) and b2 (+0.194) keep their sign;
  (iv) the C group is **2 scenes**, effective n ≈ 2. **Grade: directional evidence only. Do not claim
  "cues cause false alarms" from v2.**
- **`none_in_fov` handling is still open.** Under corrected GT the hole shrank from 56.7 % → **17.5 %**
  of ON_NEG events (lift 1.91× → 1.19×), but the residual **39 frames sit in no published denominator**
  and the `labeler.py:526` post-gate attribution defect is unresolved. `ACC §3.4 item 8`;
  `ACC §4.7 :461-464`. `[미결: v3의 none_in_fov 상당 tier 처리 규약 — test-ext 정의 시 확정]`
- **`gt_void` must be separated in v3 labels** (void cells were printed as GT-negative; on-arm 42.4 %
  of frames contain in-grid void). Denominator treatment is fixed at the same time as test-ext.
  `ACC §4.8 row 2 :481`

### 3.5 Pre-registered verdict rule
- **Direction**: **FA_C DOWN** and **(FA_C − FA_D) DOWN** for v3 vs v2. FA_D down is desirable but is
  a layer-③ statement, reported separately.
- **Magnitude**: |Δ| > σ (ddof = 1) over 3 seeds.
- **Degenerate-solution guard**: an all-silent model trivially minimises every column. The verdict is
  admissible **only** jointly with Table 1's recall not falling by more than σ, and with the
  constant-output rejection gate passed. `DZ §4.3-3 :254`; `DZ §2.5-3 :189` ("every recall claim is
  printed with FA-matching" — the converse also holds).
- **Stratified reading**: a v3 that fixes ★1–★2 rungs and still fails ★4–★5 is the expected partial
  result and should be reported as a ladder position, not a binary. `FAR §3.1`

---

## Table 4 — Headline table, test-core (corrected GT), v2 | v3 sides

### 4.1 Caption draft
> **Table 4. Headline results on test-core (816 frames, 7 scenes), corrected ground truth.** Frames
> are identical across v2 and v3; the ground truth is the G7-repaired canonical label set (B), and
> **both** sides are scored against it — scoring only v3 on corrected labels would void the
> comparison. Recall columns are conditioned on frames carrying at least one in-grid positive cell;
> the fraction excluded by that conditioning is printed. Because the τ = 0.5 column compares models at
> different false-alarm rates, it must be read together with the FA-matched table (Table 5); and
> because the frame and cell axes can order the same checkpoints differently, both are printed.

### 4.2 Shell

| side | model | n seeds | recall **H (3b)** | recall E | recall V | recall H_weak † | frame_det_rate | cell_f1 | cell_recall | cell_precision | **frame_fa_off** | **cell_fpr_off** | cells/FA-frame |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 | rgb | 3 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| v2 | depth | 3 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| v2 | b2 | 3 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| v2 | yolov8n @ τ0.25 ‡ | 3 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| **v3-A** | rgb | 3 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| **v3-A** | depth | 3 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| **v3-A** | b2 | 3 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| v3-B | rgb (cell-query attn) | 3 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |

† **H_weak denominator is 9 (≤ 10) — accounting column only, must not be cited in body text.**
`RS §1.2 :167`
‡ **Adapter-scoped row.** YOLO's E/H behaviour is a property of the `det2cell` adapter (bottom-edge
ground-plane projection; the oracle-box diagnostic fixes E = H = 0.000 before training). Adapter-free
H hit is **0.066**. State this in the caption, not a footnote — it was previously mis-read as a
constructive ceiling. `PS v2 §1-1 :27-28`; `ST §4.2`; METRICS §RT.3

### 4.3 Denominator source — `ACCOUNTING §3.1` + `§4.8` (corrected-GT companion row)

| item | old GT (published) | **corrected GT (canonical B)** | note |
|---|---|---|---|
| total / on / off frames | 816 / 408 / 408 | 816 / 408 / 408 | unchanged |
| V | 180 | **219** | +39, all scene07 boost inflow |
| E | 45 | 45 | unchanged (property of canonical B; variant A gives 48) |
| **H (strict)** | **96** | **96** | **unchanged** |
| H_weak | 6 | **9** | +3 |
| none_in_fov | 81 | **39** | −42 |
| **headline recall denominator** | **327** | **369** | old 327 is a **proper subset** of new 369; zero frames leave |
| conditioning-exclusion disclosure (mandatory) | 81/408 = 19.9 % | **39/408 = 9.6 %** | must be printed in the same table |
| positive cells (816 frames) | 2,691 | **2,856** | drives the cell-series columns |

Ledger: `ACC §3.1 :271-281` · corrected companion `ACC §4.8 :473-474` · full census `RS §1.1 :117-151`.
**⚠ Internal ledger conflict — read §4.4 as authoritative**: `ACC §4.2 :359` still reads
"none 81→36 · denominator 327→372"; that is an arithmetic error corrected in `ACC §4.4 :371-377`
(check: 219+45+96+9+39 = 408). `DEC D55` and `DEC D59 ⑦` carry the same trail. Append-only convention
leaves §4.2 uncorrected in place.

**The accounting fact that makes the corrected GT safe to adopt** (worth one sentence in the paper):
restricted to the old 327-frame denominator, corrected GT reproduces the published values to **four
decimal places in every cell** ⇒ the repair changed no existing frame's label, and 100 % of the recall
delta is the 42-frame inflow. `RS §1.3 :174-196`

### 4.4 Pre-registered verdict rule
- **Primary judgement is v3-A only** — resnet34 U-Net **completely frozen**, corpus and supervision
  the only changes. If the architecture changes too, the causal attribution "data design creates
  inference" is permanently broken. v3-B is parallel and diagnostic. `DZ §6 :293-297`
- **Direction**: H (3b) recall UP **at matched FA**, on both axes, with FA not worse.
- **Magnitude**: > σ (ddof = 1).
- **Structural gates (absolute, derived from v2 measurements, submitted with derivation)**: constant
  output rejection, 1-epoch-collapse rejection, denominator accounting. `DZ §7.2 :318-320`
- **Do NOT** promote bare-occlusion H recall to a success metric — that is `DZ §2.5-5` violation and
  the only way to achieve it is memorisation. Correct target for bare-occlusion H: **a calibrated low
  probability**, which Table 6 measures. `DZ :191-192`, `DZ :357-358`

---

## Table 5 — FA-matched comparison, dual axis (companion to Table 4)

### 5.1 Caption draft
> **Table 5. H recall at matched false-alarm rate, both axes.** The τ = 0.5 column of Table 4
> compares models at different operating points (v2 off-arm FA differed by 8.6× between the RGB and
> depth arms), so the comparison is repeated with thresholds chosen from the off-arm's empirical order
> statistic to hit each target rate from below. The frame axis counts a false alarm once per frame
> regardless of how many cells fired; the cell axis counts cells. The two axes cannot be matched to
> each other simultaneously, so both are printed — in v2 they ordered the same checkpoints differently
> at τ = 0.5.

### 5.2 Shell

| axis | target | achieved (r/d/b) | side | RGB H | Depth H | B2 H | Δ(D−R) | seeds D>R | σ (ddof=1) |
|---|---|---|---|---|---|---|---|---|---|
| frame | .359 | ___ | v2 | ___ | ___ | ___ | ___ | _/3 | ___ |
| frame | .359 | ___ | **v3** | ___ | ___ | ___ | ___ | _/3 | ___ |
| frame | .200 | ___ | v2 / v3 | ___ | ___ | ___ | ___ | _/3 | ___ |
| frame | .100 | ___ | v2 / v3 | ___ | ___ | ___ | ___ | _/3 | ___ |
| frame | .050 | ___ | v2 / v3 | ___ | ___ | ___ | ___ | _/3 | ___ |
| **cell** | .046732 | ___ | v2 / v3 | ___ | ___ | ___ | ___ | _/3 | ___ |
| **cell** | .026035 | ___ | v2 / v3 | ___ | ___ | ___ | ___ | _/3 | ___ |
| **cell** | .013017 | ___ | v2 / v3 | ___ | ___ | ___ | ___ | _/3 | ___ |
| **cell** | .006509 | ___ | v2 / v3 | ___ | ___ | ___ | ___ | _/3 | ___ |

**Alarm-burden companion columns (mandatory, R-4)**: per row, `cells/FA-frame` and `cell_fpr_off` for
each model, plus the ratio. v2 precedent: at frame FA .359, Depth's cell FPR is **2.34×** RGB's
(0.1290 vs 0.0552); mirrored, matching on the cell axis re-opens a frame-axis gap (.353 vs .243 at
cell FPR .0467). `E12 §3 :84-95`

### 5.3 Method / denominator source
- τ from the **exact quantile** (empirical order statistic), giving the highest achieved rate ≤ target
  (`nextafter`). Frame-axis τ population = off-arm per-frame max probability, 408 values, resolution
  1/408 = 0.0025. Cell-axis τ population = all off-arm cell probabilities, **8,160** (408 × 20),
  resolution 1/8160 = 0.000123. Denominator matches `ACC §4.5 row A` (OFF stratum, 8,160 cells).
  `E12 §1 :38-44`
- **Procedure gate before this table is admissible**: the frame-axis half of the computation must
  reproduce `F1 §2` to 3 decimals across 4 points × 3 models. `E12 §1 :46-48`
- **V-tier rows must be re-issued on corrected GT** — the corrected GT adds 39 frames to the V
  denominator that are relatively hard for RGB, moving RGB V by up to −0.044 while Depth moves −0.012.
  E and H rows are byte-identical across GTs. `E12 §5 :137-146`; `RS §3.2 :301-313`
- Numerator/denominator must move to the cell axis **together**; the paired metrics are
  `frame_recall_H` @ `frame_fa_off` and `cell_recall_H` @ `cell_fpr_off`. `E12 §1 :43-44`

### 5.4 Pre-registered verdict rule
- **Direction**: v3's H at each matched point ≥ v2's, on both axes.
- **Magnitude**: > σ (ddof = 1); **report per-seed unanimity** (x/3) alongside, because v2's frame axis
  was not unanimous at its two loosest points (2/3 and 1/3) while the cell axis was 3/3 everywhere.
  A reviewer opening the per-seed table will find this. `E12 §2 :72-76`
- **Axis-disagreement protocol**: if the two axes disagree in sign, report the disagreement as the
  result. Do not select the favourable axis. `E12 §6-1 :152-153`

---

## Table 6 — Calibration: reliability, ECE, and selective firing

### 6.1 Caption draft
> **Table 6. Calibration before and after temperature scaling.** Layer ④'s output format is a
> calibrated probability, not a verdict, so the paper reports expected calibration error and the
> reliability diagram alongside raw and scaled outputs. Temperature scaling is monotone: it moves
> calibration and leaves recall, false-alarm rate and every ranking unchanged. The selective-firing
> curve reports performance when only the most confident x % of cells are answered, i.e. it prices the
> option of saying "I don't know."

### 6.2 Shell — ECE / reliability

| side | model | T (fitted on val) | ECE raw | ECE scaled | ΔECE | max-calibration-error raw | scaled | Brier raw | scaled | σ (ddof=1) |
|---|---|---|---|---|---|---|---|---|---|---|
| v2 | rgb / depth / b2 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| v3-A | rgb / depth / b2 | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |
| v3-B | rgb | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ | ___ |

### 6.3 Shell — the ④-b test: bare-occlusion H should be *calibrated low*, not silent and not confident

| side | model | mean p on bare-occlusion H cells | empirical hazard frequency of that stratum | \|gap\| | fire rate @ τ_op | verdict |
|---|---|---|---|---|---|---|
| v2 | rgb / depth / b2 | ___ | ___ | ___ | ___ | ___ |
| v3-A | rgb / depth / b2 | ___ | ___ | ___ | ___ | ___ |

This is the table that operationalises `DZ §2.5-5 :191-192`: the correct target for bare-occlusion H
is **a calibrated low probability, not a firing**. Without this row, an under-target H recall on that
stratum looks like a failure when it is the specified behaviour.

### 6.4 Shell — selective firing ("the value of I-don't-know")

| coverage (top x % by confidence) | side | model | cell precision | cell recall | H frame recall | FA |
|---|---|---|---|---|---|---|
| 100 % | v2 / v3 | ___ | ___ | ___ | ___ | ___ |
| 75 % | v2 / v3 | ___ | ___ | ___ | ___ | ___ |
| 50 % | v2 / v3 | ___ | ___ | ___ | ___ | ___ |
| 25 % | v2 / v3 | ___ | ___ | ___ | ___ | ___ |

`[미결: coverage 격자 {100,75,50,25} 잠정 — 사전등록 전 확정 필요]`

### 6.5 Denominator source and known risk
- T is fitted on **val**, and val is the weak point: v2's val is 288 frames over 2–3 scenes with
  **strict-H = 6 frames**. **If P-4's val expansion (strict-H ≥ 30) does not land first, T is
  estimated on 6 frames.** This is the pre-registered red-team target for this table.
  `ASSUMPTION_LEDGER.md V3-04 :228`; `DZ §4.3-3 :254`
  - **P-4 landed concurrently** (`experiments/v3_0823/P4_SELECTION.md`, 08-23) and its own honesty
    record states that **val H = 6 is not fixed by the selection repair** — the val expansion has to
    come from the render side (test-ext/train-side paired-H scenes, `ACC §4.9-2` item 2). Until it
    does, this table's T is estimated on 6 H frames and must say so.
- Val denominators: `ACC §3.2 :300-301` (v2 val 288: V75 · E6 · H6 · Hw3 · none54 · off144;
  corrected GT moves val V 75 → **96**, `ACC §4.2 :360`). v3 val accounting: `ACC §3.4` item 5.
- **Do not let readers infer that calibration changed the comparison.** T is monotone ⇒ recall/FA
  curves are unchanged; only ECE and the reliability diagram move. State it in the caption.
  `ASSUMPTION_LEDGER.md V3-04`; `RT_LEDGER_B.md:262`
- **Mandatory companion paragraph** (`DZ §5.2 :279`): one practical paragraph reading the probability
  map as a traversability cost map — "if you use this probability map as a costmap…" — connecting the
  output format to deceleration / active perception. This is the ④-layer's action channel and 승용
  ruled it in (결재 1, practical-information view).

### 6.6 Pre-registered verdict rule
- **Direction**: ECE **DOWN** for v3 vs v2 after scaling; bare-occlusion H mean-probability gap
  **DOWN**; selective-firing curve **dominating** v2's at equal coverage.
- **Magnitude**: > σ (ddof = 1) over 3 seeds.
- **No CI on ECE.** The scene-cluster CI withdrawal applies here too: with H on 2 scenes and E on 1,
  attaching confidence intervals to ECE re-opens exactly the objection that forced the withdrawal.
  `RT_LEDGER_B.md:80`; `PS v2 §1-3 :32-33`

---

## 7. Cross-table checklist before any of these tables is printed

- [ ] Every denominator traced to an `ACCOUNTING.md` row with path + recount command + date (R-1).
- [ ] Both A/B sides on corrected GT (R-2); old-GT delta in a separate report.
- [ ] σ definition stated in every caption; verdicts use ddof = 1 (R-3).
- [ ] Both FA axes present in every FA-bearing table (R-4); cells/FA-frame estimator named (R-5).
- [ ] Dashboards on test-ext only; headline + FA-matched on test-core only (R-6).
- [ ] Every "twin" names its pair (R-8); no (A,D) number in an (A,C) cell.
- [ ] Conditioning-exclusion fraction printed in the headline table (9.6 % corrected).
- [ ] YOLO row captioned as adapter-scoped, with the 0.066 adapter-free figure.
- [ ] H claims restricted to 3b; 3a excluded and said to be excluded.
- [ ] No confidence intervals on H/E scene-level quantities.
- [ ] No claim that the main-table models have a trained aux amodal head
      (`ACC §4.9-4` — all 9 main-table runs measured aux OFF).
      `[미결: DZ §0.1 서술 정정 대기 — Claude AI/승용]`
- [ ] `|r|` reported with marginals + togglable-key restriction + per-key r; the 5 non-togglable keys
      flagged as constant keys (`ACC §4.9-3`).
- [ ] Cue-presence threshold **k** fixed by gate and hashed **before** supervision started
      (`ACC §2-5`, §3.4 item 1) — and said so.
