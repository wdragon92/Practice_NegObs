# nearfield_limitation_paragraph — the unified near-field limitation paragraph

- **Status**: SKELETON / MATERIALS. Not final prose. Claude AI + 승용 own the finished text (D58 ⑥).
- **Written**: Claude Code (CPU-6) · 2026-08-23 · target: v3-frame main paper (English).
- **Where it goes**: §Limitations (primary). A 2-sentence variant is also needed early — in the
  Introduction's scope statement — so the paper never promises near-field and then withdraws it.
- **Sources**: `DZ` = `Docs/experiment/V3_DESIGN_0823.md` §1 `:48-51`, §3 `:213-218` ·
  `PS v2` = `Docs/experiment/Status/PROJECT_STATE_0823_v2.md` §1-5 `:35-38`, 결재 7 `:70` ·
  `ST` = `experiments/dayrun_0820/runs/v2/SEED_TABLE.md` §1 (band1 columns) ·
  `ACC` = `experiments/v3_0823/ACCOUNTING.md` §4.8 row 4 `:483`.

---

## 0. The three observations being unified

| # | Observation | Measured value / status | Ledger |
|---|---|---|---|
| ⓐ-1 | **band1 blindness** — the innermost distance band (underfoot, 0–2 m) is never recalled by the RGB model | `band1_cell_recall` = **0.000 ± 0.000** (rgb), **0.000 ± 0.000** (b2), 0.188 ± 0.064 (depth); `band1_cell_fpr_off` = 0.000 for all three | `ST §1` |
| ⓐ-2 | **3a non-response** — the underfoot H family shows twin Δ ≈ 0 | uniform across **11 poses** ⇒ **not** the artifact of one unlucky viewpoint | `PS v2 §1-4 :34` |
| ⓑ | **near-field E geometric non-existence** — a close drop-off is essentially never rim-only | at close range the grazing angle stands up and the interior becomes visible (it becomes V); rim-only at close range would require an aperture of **1–3 cm = a crack** | `DZ :215-217`, `PS v2 §1-5 :36` |

**Fidelity constraint — do not flatten DZ's distinction.** `DZ :213-214` explicitly says the two
reasons must be kept apart: *"이유가 둘로 갈리므로 정확히 구분한다."* ⓐ is a **field-of-view artifact of
the observation regulation** (forward, fixed pose). ⓑ is a **geometric impossibility** of the tier
definition at short range. The unified paragraph may share a *root* — both are consequences of
evaluating the same grazing-angle geometry at small d under a pose we chose — but it must not claim
they are the *same mechanism*. A reviewer who has read the tier definitions will notice.

**The unifying root, stated precisely**: at short range the term h·w/d² is *large* — the direct signal
is abundant, not scarce. Nothing about the negative-obstacle class is hard near the robot. What is
missing near the robot is **coverage**: a forward-fixed camera simply does not point there, which is
the same constraint that makes a nearby rim-only view geometrically vacuous. Both are properties of
**our observation regulation**, not of the hazard. The hazard's own intrinsic difficulty is the
**opposite regime** — far-field vanishing at ~1/d². `DZ :48-51`, `DZ :217-218`

**The human disanalogy that makes it obviously a pose problem**: a person solves this by **looking
down**. `DZ :50`

---

## 1. The paragraph (primary version — §Limitations)

> **Near-field limitation.** Our system makes no claim about hazards within roughly two metres of the
> robot, and the three ways this shows up in our results have a single root. The innermost distance
> band is never recalled by the RGB model (band-1 cell recall is exactly 0.000 across all three
> seeds); the underfoot family of hidden drop-offs (3a) shows a counterfactual twin response of
> essentially zero, uniformly across all eleven camera poses rather than at one unlucky viewpoint;
> and the rim-only (E) tier is close to geometrically vacuous at short range, because as the grazing
> angle stands up the interior of the opening becomes visible — a nearby drop-off is a V-tier
> observation, and producing a genuine rim-only view at that distance would require an aperture of one
> to three centimetres, i.e. a crack rather than a drop. None of these is a property of negative
> obstacles. They are properties of the observation regulation we adopted: a single forward-facing
> camera at a fixed pose does not look at the ground beneath itself, and at the ranges where it does
> not look, the signal it is missing is abundant rather than scarce — the visible aperture scales as
> h·w/d², so near-field geometry is the easy regime, not the hard one. A person resolves it by
> lowering their head. The difficulty that is intrinsic to this hazard class is the opposite one, and
> it is the one this paper addresses: the far-field regime, where the visible aperture vanishes as
> 1/d² exactly at the distances where advance warning has any value. We therefore scope our claims to
> forward-field E and H (3b) and defer the near field to the temporal axis — carrying evidence from
> the frames in which a hazard *was* visible into the frames in which it no longer is. Our renderer
> already stores per-scene continuous pose trajectories for this purpose; video propagation is the
> declared next step, not a caveat we intend to leave open.

**Length**: ~250 words. If §Limitations needs to be tighter, cut the sentence beginning "A person
resolves it" and the clause "rather than at one unlucky viewpoint".

---

## 2. Short variants

### 2.1 Two-sentence variant — for the Introduction's scope statement
> *We scope this work to the far field. Near-field blindness in our results — an empty innermost
> distance band, a null counterfactual response for underfoot hidden drops, and a rim-only tier that
> is geometrically vacuous at short range — is a consequence of our forward-fixed single-camera pose
> rather than of the hazard class, whose intrinsic difficulty is the opposite regime: a visible
> aperture that vanishes as 1/d² precisely where advance warning matters.*

### 2.2 Three-sentence variant — for §Method (evaluation scope) or a figure caption
> *Our observation regulation is a single forward-facing camera at a fixed pose, and it does not cover
> the ground immediately beneath the robot. Consequently band 1 carries no recall, the underfoot
> hidden-drop family (3a) is excluded from our H claims, and the rim-only tier is treated as a
> far-field construct — at close range the grazing angle stands up and the opening's interior becomes
> directly visible. This is a coverage limit of the sensor pose, not an information limit of the
> problem; the information limit runs the other way, with the visible aperture falling as 1/d².*

### 2.3 One-sentence variant — for the abstract or a rebuttal
> *Near-field blindness in our results is a field-of-view consequence of a forward-fixed camera pose,
> not a property of negative obstacles, whose intrinsic difficulty is the far-field 1/d² vanishing of
> the visible aperture that this work targets.*

---

## 3. Facts the paragraph must stay consistent with

| Fact | Value | Ledger | Consequence for wording |
|---|---|---|---|
| band-1 RGB cell recall | 0.000 ± 0.000 (all 3 seeds) | `ST §1` | may be quoted as "exactly zero"; **do not** quote depth's 0.188 in the same breath without saying it is the depth arm |
| band-1 off-arm FPR | 0.000 for all models | `ST §1` | the band is not merely miscalibrated — the models are silent there in both directions |
| 3a twin Δ ≈ 0 | uniform across 11 poses | `PS v2 §1-4 :34` | phrase as "not the artifact of a single viewpoint"; **do not** phrase as "not an artifact" — it *is* an artifact of the pose regulation as a class (`DZ :214-215`) |
| near E aperture requirement | 1–3 cm | `DZ :216`, `PS v2 :36` | keep the "crack, not a drop" gloss — it is what makes the geometric argument land in one clause |
| H claim scope | **3b only** | `PS v2 §1-4 :34`, 결재 2 `:65` | the paragraph is the place that *earns* this restriction; the Introduction merely announces it |
| far-field law | visible aperture ≈ h·w/d² | `DZ :39-41` | the paragraph's pivot; also independently re-derived by our own FA census as **FA ∝ R^1.98** (`FA_CENSUS.md §3.3`) — optional supporting clause |
| real-world scoring asymmetry | **15 of 20 cells** scored; band 1 is not annotatable and is excluded from the denominator, **though model output exists there** | `PS v2 §1-5 :38`, 결재 7 `:70` | if the pilot section is in the paper, this paragraph should point at it: the near-field limit also shapes how the real-world evaluation is scored |
| roadmap status | video propagation is 승용's roadmap; the **sequence hook** (per-scene continuous pose trajectories, stored at render-parameter level, minimal cost) is already specified as v3's raw material | `DZ §3 :218`, `DZ §4.3-4 :257` | write the roadmap as *declared and already provisioned*, not as speculation. **Do not** claim any measurement of it — none exists |

---

## 4. Two things this paragraph must NOT say

1. **Do not** say band-1 blindness "will be fixed by video propagation." No such result exists.
   The defensible form is: the near field is deferred to the temporal axis, and the corpus already
   stores the trajectories that would make that experiment possible.
   `[미결: 동영상 전파는 로드맵 단계 — 성능 약속 금지]`
2. **Do not** merge ⓐ and ⓑ into one mechanism (see §0, fidelity constraint). Shared root, distinct
   mechanisms. `DZ :213-214`

---

## 5. Placement note

The paragraph does double duty: it discharges a limitation **and** it converts the far-field framing
of §Introduction from an assumption into a derived scope. Placing it only at the end of the paper
wastes that. Recommended: the two-sentence variant (§2.1) in the Introduction's scope statement, the
full paragraph (§1) in §Limitations, cross-referenced.
`[미결: 서론 스코프 문단과 한계 절 사이 배치 — Claude AI 편집 판단]`
