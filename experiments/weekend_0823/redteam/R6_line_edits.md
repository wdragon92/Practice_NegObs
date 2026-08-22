# R6 — stale-sentence line-edit list (paper-draft coherence sweep, post-weekend appends)

작성 2026-08-23 · red-team wave 2, R6 · **읽기 전용 감사 — 어떤 파일도 편집하지 않았다.**
근거: `experiments/mainrun_0819/{RESULTS_DRAFT.md, METRICS.md}` 전문 · `experiments/dayrun_0820/runs/v2/SEED_TABLE.md` ·
`Docs/experiment/Status/PROJECT_STATE_0823.md` §5–§6 (사용자 저작 — **편집 대상 아님, 대조용으로만 읽음**) ·
`DECISIONS.md` D41–D48 · `weekend_0823/{rt_response, redteam, v2s, cue_audit}/`.

각 항목: **파일 · 줄 · 현재 문장 · 교체 문장**. 문서 언어를 따른다(EN 문서는 EN, KR 문서는 KR).

---

## 0. 범주 legend & 집계

| 코드 | 범주 | 무효화 근거 | 건수 |
|---|---|---|---|
| **(a)** | '완전가림 / fully occluded / contributes no pixels' 계열 | **F7** (RT.6): 96/96 H 쌍 전부 광학적으로 다름, 중앙값 프레임의 4.51 %가 ≥32/255, 최소쌍도 노이즈 바닥의 44× | **18** |
| **(b)** | 'RGB가 H에서 Depth를 이긴다' 잔재 | **R1-F1 / RT.1** (D41①): FA 정합 시 전 지점 Depth ≥ RGB, 격차는 FA를 조일수록 벌어짐 | **14** |
| **(c)** | 'YOLO 구성적 0 / constitutional zero' 잔재 | **F3 철회** (RT.3, D41③): 상한은 `det2cell` 어댑터의 성질, 패러다임의 성질 아님 | **12** |
| **(d)** | aux 유의성 잔재 | **D41⑤ / RT.5**: 씬-클러스터 재표집에서 `cell_f1`·`cell_recall_H` 모두 0 포함 | **9** |
| **(e)** | N3 널 대조군 blanket 서술 | **RT.4**: 팔 한정 — RGB는 양팔 포화(0.75–1.00) = 탈락, Depth만 진짜 통과 | **6** |
| **(f)** | V2S / 20칸 채택 전제 서술 | **D43**: V2S = ROLLBACK(사전등록), V1 20칸이 정본, 채택 결재 없음 | **7** |
| **(g)** | H·E 헤드라인 CI 주장 | **RT.5**: test H = 2 클러스터, E = 1 클러스터 → CI는 **철회**(확대가 아니라) | **18** |
| **(h)** | 기타(τ_edge 표기 오류·공허한 민감도 논증·이미 닫힌 "대기 중" 표기) | RT.7 · R.1/R.5 | **3** |
| | **범주 태그 합계** | | **87** |
| | **고유 문장(중복 태그 8건 제외)** | | **79** |

파일별 고유 건수: `RESULTS_DRAFT.md` **22** · `METRICS.md` **18** · `SEED_TABLE.md` **7** ·
`brief_prof_0820.md` **9** · 우리 소유 부차 문서 12종 **23**.
(§6에 (a)–(h) 어디에도 넣지 않은 별도 권고 4건이 추가로 있다.)

> 우선순위 표기: **[P0]** = 논문 본문에 그대로 들어가면 심사에서 즉사 · **[P1]** = 반드시 고쳐야 함 ·
> **[P2]** = 용어/표기 정합.

---

## 1. `experiments/mainrun_0819/RESULTS_DRAFT.md`

### L18 — (a) [P1]
**현재**: `**H** (hazard contributes no visible pixels; *strict* by construction and stable across all nine (τ_int, τ_edge) settings).`
**교체**: `**H** (the hazard prism re-projects to **zero contributing pixels** — no interior surface, no visible rim; *strict* by construction). This is a **geometric** predicate on the hazard's own projection and it does **not** mean the two twin arms render the same image: all 96 test H pairs differ optically (§RT-C). The nine-setting (τ_int, τ_edge) sweep is not evidence of robustness — `tier_of` defines H as `int_px == 0 ∧ edge_vis == 0`, which neither threshold enters (§RT.7-b).`

### L47–49 — (g) [P0]
**현재**: `Paired over the same 336 test frames, Depth beats RGB on cell F1 by 0.248 [0.190, 0.308] and on frame-level H recall by 0.381 [0.053, 0.688], while RGB false-alarms more on the off arm by 0.113 [0.041, 0.188] — all three intervals exclude zero.`
**교체**: `Paired over the same 336 test frames, Depth beats RGB on cell F1 by 0.248 [0.190, 0.308] and false-alarms less on the off arm by 0.113 [0.041, 0.188]; both intervals exclude zero under frame resampling and the FA interval survives scene-cluster resampling. The frame-level H difference is +0.381 as a point estimate and we print **no interval for it**: the 21 v1 H frames come from two scenes (scene14, scene15), and a two-cluster bootstrap can enumerate only three distinct multisets (§RT.5).`

### L49–52 — (g) [P1]
**현재**: `The E tier is the one place RGB is nominally ahead (+0.111), but with 9 frames its paired interval [0.000, 0.375] includes zero and we make no claim there. Cell-level H recall (Δ = −0.267 [−0.600, 0.084]) also fails to clear zero, i.e. the H-tier advantage is established at the frame level and not yet at the cell level.`
**교체**: `The E tier is the one place RGB is nominally ahead (+0.111), on 9 frames drawn from a **single** scene; we print no interval and make no claim there. The cell-level H difference (−0.267) likewise carries no reportable interval. Nothing about the H tier is "established at the frame level" — the frame-level and cell-level readings simply differ, and neither is supported by a resampling unit coarser than the frame.`

### L70–72 — (a)(g) [P0] **— 상위 5 중 1**
**현재**: `On **H** frames — where the hazard contributes no visible pixels at all — removing the hazard still lowers the RGB model's probability by **0.240 [0.156, 0.331]**.`
**교체**: `On **H** frames — where the hazard's own surface and rim project to zero pixels, though the frame is *not* unchanged (§RT-C) — removing the hazard still lowers the RGB model's probability by **0.240** (no interval: two scene clusters, §RT.5).`

### L72–75 — (a) [P0] **— 상위 5 중 2**
**현재**: `Since no hazard pixel exists in either image of an H pair, the model's response must be driven by the surrounding context (railing terminations, path truncation, the change in what the far ground plane does), which is exactly the mechanism this work sets out to demonstrate.`
**교체**: `No pixel of the hazard *surface* exists in either image, but the two images are not identical: the median H pair differs on 4.51 % of the frame at ≥ 32/255, 1 872× the renderer's own nondeterminism floor, and the toggle removes every object the scene builder places in the same branch (in scene14 the shoulder massif, side slopes, coursing, parapets, cues and litter). The twin therefore establishes **that** the response is caused by the hazard's presence in the scene; it does **not** establish **which** image property carries the causation, and the CUE-OFF intervention (D46) shows the RGB arm firing at FA 1.000 on the cue vocabulary with the drop absent. The honest claim is **cue association, not cue inference**.`

### L75–78 — (e) [P1]
**현재**: `One caution: on the hard-negative scene N3, which has no hazard in either arm, the RGB model's frame-level Δ is still 0.252 while Depth's is 0.000 — the RGB arm is partly responding to the *dressing* that the toggle removes, and a dressing-invariant control is needed before the causal claim is tightened.`
**교체**: `One caution, now measured rather than anticipated: the dressing-invariant control was run (§R.3). On the hard-negative scene N3 the RGB arm fires on **0.75–1.00 of frames in *both* arms** at mean max p 0.74–0.95, so its Δ ≈ 0 records saturation, not silence; the Depth arm is genuinely quiet there (0.000–0.125) and B2 is mixed. The caution is **arm-specific** and belongs in the limitations section as the clearest single measurement of scene-level shortcut behaviour in the RGB arm.`

### L116–117 — (h) [P2]
**현재**: `Strict-H is insensitive to both thresholds across nine settings; the V/E boundary is not (V 417–453).`
**교체**: `Strict-H is invariant to both thresholds **by definition**, not by measurement — the sweep could not have moved it (§RT.7-b). What the corpus shows instead is that `edge_ratio` is bimodal (exactly 0, or ≥ 0.44), so the E/H boundary is independent of τ_edge and the swept grid {0.02, 0.05, 0.10} lies entirely inside an interval containing no data. τ_int = 50 px is the threshold that does move results (V 726 → 657, H_weak 0 → 57 over a 1 → 200 sweep).`

### L132–133 — (g) [P1]
**현재**: `This is why the H intervals are wide enough to swallow effects of ±0.3, and why the frame- and cell-level H comparisons disagree.`
**교체**: `This is why no H interval is reportable at all: 21 frames from two geometries are not 21 independent samples, and the frame- and cell-level H readings disagree because both are dominated by the same two scenes.`

### L165–169 — (b)(g) [P1]
**현재**: `**Wording to adopt.** The sentence "removing the hazard still lowers the RGB model's probability on H frames" must be qualified as *far-band*: RGB's context response to a hazard it cannot see is demonstrated for band 3b and **is not demonstrated for band 3a** ...`
**교체**: `**Wording to adopt.** Three qualifications travel with the sentence, not one. (i) *far-band*: demonstrated for band 3b, not for band 3a. (ii) *viewpoint*: not demonstrated at robot camera height (h < 0.6 m, Δ_3b = +0.120, pose-clustered CI [−0.010, +0.129]; `weekend_0823/a3_viewpoint/`). (iii) *scene*: carried by scene14; on scene15 the RGB Δ is −.010/.209/−.058 (§RT-B). State it as "for cameras at ≥ 0.6 m and hazards at ≥ 8 m, in the scene that carries the effect".`

### L180 — (g) [P1]
**현재**: `All nine runs' EXACT-only 95 % CIs exclude zero.`
**교체**: `All nine runs' EXACT-only point estimates are positive; the accompanying 95 % intervals were computed with frames as the resampling unit over two H scenes and are **withdrawn** (§RT.5). Report the per-scene value beside that scene's off-arm false-alarm rate instead.`

### L303 — (c) [P1]
**현재**: `The zero is the point of the row, and it must be presented as **constructive rather than empirical**.`
**교체**: `The zero is the point of the row, and it must be presented as **a property of our ground-projection adapter**, measured — not as a property of detection.`

### L305–309 — (a)(c) [P0] **— 상위 5 중 3**
**현재**: `A hazard in the E tier contributes only a rim, and a hazard in the H tier contributes **no pixels at all** — so there is no box to project, and the mapping can emit no cell. E and H recall are therefore not merely expected to be near zero, they are *constructively bounded* at zero, a bound already measured before training via the oracle-box diagnostic (D22; `METRICS_NOTES_yolo.md` §3).`
**교체**: `A hazard in the H tier contributes no pixels **of its own surface**, and `det2cell` projects a box's bottom edge onto the ground plane; feeding the amodal ground-truth boxes in as confidence-1.0 detections therefore yields E = H = 0.000 **before any training** (D22 oracle diagnostic). That fixes the zero as a property of **this adapter**. It is not a bound on detectors: with the adapter removed and scoring done in image space, the detector does place boxes near hidden hazards at 0.066 of H frames (IoU > 0) — see §RT-D for the bound that actually holds.`

### L316–320 — (c) [P0] **— 상위 5 중 4**
**현재**: `It is: **any method whose output is a bounding box over visible hazard pixels has an identically zero ceiling on the E and H tiers, independent of detector quality, and this row measures that ceiling rather than a model.** That is what motivates the cell-classification formulation, and it is the cleanest single justification for the paper's framing.`
**교체**: `It is: **an amodal-trained detector — taught to draw boxes over hazards it cannot see — produces no hazard-conditional evidence on the hidden tier: its image-space hit rate on hazard-ON frames (0.066) is indistinguishable from its rate on the hazard-deleted twin of the same cut (0.076), a twin-conditional rate of −0.010, against +0.337 on the visible tier.** That is the bound this row supports, it is stronger than the adapter statement, and it is what motivates the cell-classification formulation. Do not generalise to "any method whose output is a bounding box".`

### L316 — (a) [P2]
**현재**: `The sentence for the paper is therefore not "the detector performs poorly on invisible hazards"`
**교체**: `The sentence for the paper is therefore not "the detector performs poorly on hazards that contribute no pixels"` *(용어: "invisible hazards"는 F7이 폐기한 계열 — H 프레임은 광학적으로 비어 있지 않다.)*

### L333–335 — (d) [P0]
**현재**: `Most relevant to this paper's thesis, **H-tier cell recall rises +0.355** [0.277, 0.430] — 0.253 → 0.607, the largest confirmed effect in the comparison — and the independent twin evidence agrees, with the H-tier on/off Δ nearly doubling from 0.170 to 0.326.`
**교체**: `H-tier cell recall rises **+0.355** (0.253 → 0.607) with a frame-i.i.d. interval of [0.277, 0.430] that **does not survive scene-cluster resampling** ([−0.143, 0.463], §RT.5) — the interval was measuring within-scene variation across the same two H scenes. Report the point estimate as suggestive and **withdraw the significance claim**. The twin evidence moves in the same direction (H-tier Δ 0.170 → 0.326) and is subject to the same two-scene limitation.`

### L336–337 — (d) [P1]
**현재**: `Cell F1 improves +0.040, with a CI whose lower bound is 0.0001; report that as "improved, marginally significant", not as a headline.`
**교체**: `Cell F1 improves +0.040; its frame-i.i.d. interval [0.0001, 0.0786] becomes [−0.258, 0.205] under scene resampling, so report it as **not significant**, not as "marginally significant".`

### L344–347 — (d) [P1]
**현재**: `First, the frame-level H gain that reads best in a summary, +0.125, has a **confidence interval containing zero** ([−0.010, 0.253]); only the cell-level gain is statistically supported, so the claim must be written at cell level.`
**교체**: `First, **neither** H gain is statistically supported. The frame-level +0.125 contains zero under both resampling units ([−0.010, 0.253] frame-i.i.d.; [−0.417, 0.450] scene-cluster), and the cell-level +0.355 contains zero under scene resampling. What survives clustering is the false-alarm/precision family only (`frame_fa_off`, `cell_fpr_off`, `frame_recall_V`).`

### L379–383 — (e) [P0]
**현재**: `` `sceneN3` served as the null control and behaved as designed. ... The measurement apparatus introduces no delta of its own, which is what licenses reading C2's 0.163 as signal. ``
**교체**: `` `sceneN3` behaved as designed **in the narrow sense that the apparatus introduces no delta of its own** — its dressing is a wall mural, 1–2 mm of paint on flat floor, the dressing-preserving off arm is structurally identical to the on arm (heightmap max |Δ| = 0.000000 m), and the twin delta measures **−0.001 ± 0.001**. That licenses reading C2's 0.163 as signal. It does **not** mean the models passed: Δ ≈ 0 here because **both arms are saturated for the RGB arm, not because both are silent** — RGB fires on 0.75–1.00 of these pure-negative frames at mean max p 0.74–0.95. Depth is genuinely quiet (0.000–0.125) and B2 is mixed. The null control is a **pass for the apparatus and a failure for the RGB model**, and it must not be written as a blanket "control passed". ``

### L385 — (g) [P2]
**현재**: `Finally, and importantly for §5.3: **this control does not touch the headline causal claim.**`
**교체**: `Finally, and importantly for §5.3: **this control does not touch the H-tier twin claim** (as scoped by §RT-B — per scene, no interval).`

### L403–405 — (b) [P0] **— 상위 5 중 5**
**현재**: `This inverts the ordering of the main table, where RGB leads Depth on the H tier (0.688 vs 0.438), and the inversion is the finding.`
**교체**: `There is no ordering to invert. The main table reads RGB's H recall at an off-arm FA of 0.359 and Depth's at 0.042; at matched false-alarm rates Depth leads RGB on the hidden tier at **every** operating point (0.781 vs 0.729 at FA 0.359; 0.510 vs 0.326 at FA 0.10; 0.479 vs 0.243 at FA 0.05). The probe's Depth-over-RGB result is therefore **consistent with** the corpus, not contrary to it (§RT-A).`

### L405–409 — (b)(a) [P1]
**현재**: `RGB's H-tier competence on the training corpus is *semantic context*: it has learned what the surroundings of a ditch or a stair look like, and a hole in a corridor does not supply those surroundings.`
**교체**: `RGB's H-tier firing on the training corpus is **association with the corpus's cue vocabulary**, not inference from it: 44.7 % of its H-tier fires also occur on the hazard-deleted twin (§RT-B), and the CUE-OFF arms show it firing at FA 1.000 on the cue vocabulary alone with no drop present (D46). A hole in a corridor supplies neither the vocabulary nor the drop, and the arm does not transfer.`

### L436–437 — (b) [P2]
**현재**: `**the H-tier result is demonstrated for the drop types in this corpus, and the RGB arm's version of it does not survive a change of drop type.**`
**교체**: `**the H-tier result is demonstrated for the drop types, the cue vocabulary and the scenes of this corpus; the RGB arm's version of it survives neither a change of drop type nor removal of the cue vocabulary (D46), and it is not a claim of advantage over the range arm at a matched false-alarm rate (§RT-A).**`

---

## 2. `experiments/mainrun_0819/METRICS.md`

### L99–101 — (h) [P1]
**현재**: `strict-H is **τ-insensitive**: 45 frames at all 9 combinations of τ_int ∈ {1, 50, 200} px × τ_edge ∈ {0.02, 0.05, 0.10}. Only the V/E boundary moves (V 417–453, E 33–42). Operating point used everywhere below: τ_int = 50, τ_edge = 0.02.`
**교체**: `strict-H is τ-**invariant by definition** — `labeler.tier_of` defines H as `int_px == 0 ∧ edge_vis == 0`, a predicate neither threshold enters, so the nine-combination sweep could not have moved it. The substantive fact is that `edge_ratio` is bimodal in this corpus (0 or ≥ 0.44), so the E/H boundary is independent of τ_edge and {0.02, 0.05, 0.10} all sit inside an empty interval. Operating point used everywhere below: **τ_int = 50, τ_edge = 0.05** (`labeler.py` `TAU_INT_DEF, TAU_EDGE_DEF = 50, 0.05`; `dataset_manifest_v2_full.json` `meta.tau_strict`). The 0.02 printed here is a documentation error and changes no number (§RT.7-a).`

### L140–141 (표 행) — (g) [P1]
**현재**: `| frame recall E (n=9) | 0.4444 [0.1111, 0.8000] | 0.3333 [0.0000, 0.6667] |` · `| frame recall H (n=21) | 0.3333 [0.1333, 0.5455] | **0.7143 [0.5000, 0.9000]**|`
**교체**: 두 행의 CI를 **삭제**하고 점추정만 남긴 뒤 표 각주 추가 — `E and H carry no interval: the v1 test E stratum is one scene and the H stratum two (scene14/scene15). Frame-i.i.d. intervals over these strata are artefacts of a 1–2 cluster bootstrap (§RT.5); the per-scene value beside that scene's off-arm FA replaces them.`

### L151–152 (§4.1 표) — (g) [P1]
**현재**: `| E | 0.3077 [0.0400, 0.5833] | 0.2308 [0.0000, 0.4286] | 39 |` · `| H | 0.2667 [0.0909, 0.4590] | 0.5333 [0.3548, 0.7121] | 90 |`
**교체**: 같은 처리 — CI 삭제 + §RT.5 각주.

### L154–156 — (g) [P2]
**현재**: `With 9 frames / 39 cells its CI spans a third of the unit interval and it is **not** a finding (see §6: paired CI includes 0).`
**교체**: `With 9 frames from a single scene it carries no reportable interval and is **not** a finding.`

### L206–210, L218–221 (§6) — (g) [P1]
**현재**: `Note the split verdict on the H tier: the **frame-level** H advantage clears 0 (−0.3810 [−0.6875, −0.0526]) but the **cell-level** one does not (−0.2667 [−0.6000, 0.0844]).`
**교체**: `The H and E rows of this table carry no reportable interval (§RT.5): both strata are 1–2 scene clusters. The frame-level H difference is −0.381 and the cell-level −0.267 as point estimates; do not describe either as "clearing zero". The V-tier, cell-F1 and false-alarm rows are unaffected and their intervals survive clustering.`

### L259–263 — (a)(g) [P0] **— 상위 5 후보(동점)**
**현재**: `Every CI in the table excludes 0, including the RGB **H** row — i.e. on frames where the hazard contributes no directly visible pixels, removing the hazard still lowers the RGB model's probability by 0.24 [0.16, 0.33]. That is the night's cleanest evidence that the RGB arm reads *context*, not the hazard's own pixels.`
**교체**: `Sign consistency is the reportable statistic here; the intervals in the H and E rows are withdrawn (§RT.5, 1–2 scene clusters). On frames where the hazard's own surface and rim project to zero pixels — but where the frame is **not** unchanged (§RT.6: 0 of 96 pairs identical, median 4.51 % of the frame at ≥ 32/255) — removing the hazard lowers the RGB model's probability by **0.24**. That is evidence that the response is **caused by the hazard's presence in the scene**; it is not evidence about *which* image property carries the causation, and 44.7 % of the same arm's H-tier fires also occur on the deleted twin (§RT.2).`

### L277–279 (§7.1) — (e) [P1]
**현재**: `` `sceneN3` is a hard negative with zero GT cells in both arms; its Δ_frame is 0.2521 for RGB but 0.0001 for Depth — the RGB model's output moves when the *illusion dressing* is removed even though no hazard exists, which is a shortcut-sensitivity signal worth a line in the paper. ``
**교체**: `` `sceneN3` is a hard negative with zero GT cells in both arms. Under the **old** off arm (which also deleted the mural) RGB's Δ_frame is 0.2521 against Depth's 0.0001; under the dressing-preserving off arm (§R.3) RGB's Δ is −0.001 — because RGB fires on 0.75–1.00 of the frames in **both** arms at mean max p 0.74–0.95, i.e. it is saturated, not sensitive. This is the paper's clearest scene-level shortcut measurement and it is **RGB-specific**: Depth fires on 0.000–0.125, B2 is mixed. ``

### L460 — (g) [P1]
**현재**: `**9/9 exclude 0.**`
**교체**: `All nine point estimates are positive. The intervals are frame-i.i.d. over a two-scene H stratum and are **withdrawn** (§RT.5); the per-scene decomposition (scene14 rgb .278/.448/.558 · scene15 rgb −.010/.209/−.058) replaces them.`

### L481 — (b)(g) [P1]
**현재**: `**The H claim is a band-3b claim for RGB and must not be stated for band 3a.**`
**교체**: `**The H claim for RGB is a band-3b claim, at camera heights ≥ 0.6 m, carried by scene14** — it must not be stated for band 3a, not at robot eye height (`a3_viewpoint`, Δ_3b = +0.120, CI [−0.010, +0.129]), and not for scene15 (Δ −.010/.209/−.058).`

### L731–735 — (a)(c) [P0]
**현재**: `**D22 ceiling — confirmed, zero leak.** ... This is the constructive bound of the `det2cell` rule (a box over hazard pixels cannot exist for a hazard with no visible pixels), measured before training by the oracle-box diagnostic ... Nonzero here = mapping leak; the alarm did not fire on any seed.`
**교체**: `**D22 adapter ceiling — confirmed, zero leak.** E and H recall are identically 0 on all three seeds at both frame and cell level. This is the bound of **our `det2cell` adapter**, not of detection: the adapter projects a box's bottom edge to the ground plane, and the oracle-box diagnostic fixes E = H = 0.000 before any training. A nonzero value here would have been a mapping leak, and the alarm did not fire on any seed. **The paradigm-level claim is made in §RT.3, on the adapter-free image-space metric, and it is a twin-conditional claim (H −0.010 vs V +0.337) — not a claim that boxes cannot exist.**`

### L767 (표 행) — (d) [P1]
**현재**: `| **cell_recall_H** | 0.6072 | 0.2527 | **+0.3546** [0.2768, 0.4302] | yes |`
**교체**: `| **cell_recall_H** | 0.6072 | 0.2527 | **+0.3546** [0.2768, 0.4302] frame-i.i.d. · **[−0.1429, 0.4625] scene-cluster** | **no (significance withdrawn, §RT.5)** |`

### L786–788 — (g) [P2]
**현재**: `Δ_score by tier — V 0.4927 [0.4302, 0.5528]\* · E 0.0337 [0.0119, 0.0611]\* · **H 0.3256 [0.2701, 0.3826]\***`
**교체**: 별표(=CI 0 배제) 표기를 E·H 행에서 제거하고 각주 추가 — `\* marks intervals that exclude zero under frame resampling; the E and H rows carry 1–2 scene clusters and their intervals are withdrawn (§RT.5).`

### L790–792 — (d) [P1]
**현재**: `(i) The frame-level H gain +0.1250 has a CI containing zero — quote the cell-level +0.3546 or nothing.`
**교체**: `(i) Neither H gain is significant. The frame-level +0.1250 contains zero under both resampling units; the cell-level +0.3546 contains zero under scene resampling ([−0.1429, 0.4625]). Quote both as point estimates or neither; the surviving aux effects are precision and false alarms only.`

### L830–833 — (e) [P1]
**현재**: `**sceneN3 null control.** ... Expected twin Δ ≈ 0; measured **−0.001 ±0.001**. The apparatus contributes no delta of its own.`
**교체**: `**sceneN3 null control — the apparatus passes, the RGB model does not.** ... Expected twin Δ ≈ 0; measured **−0.001 ± 0.001**, so the apparatus contributes no delta of its own. But Δ ≈ 0 here is **saturation, not silence** for the RGB arm: it fires on 0.75–1.00 of these pure-negative frames in both arms at mean max p 0.74–0.95 (§RT.4). Depth is genuinely quiet (0.000–0.125); B2 is mixed (0.208–0.917). Any statement of this control must name the arm.`

### L839–841 — (g) [P2]
**현재**: `so the §5.3 headline H claim is untouched — N.1 already showed the H-tier Δ unchanged to four decimals under exact-pose-only stratification.`
**교체**: `so the §5.3 H-tier twin claim — as re-scoped by §RT-B (per scene, no interval, band 3b, camera height ≥ 0.6 m) — is untouched by this control.`

### L899–902 — (b) [P0]
**현재**: `Depth roughly triples RGB. This **inverts the main table**, where RGB leads Depth on the H tier (0.688 ± 0.141 vs 0.438 ± 0.031, §4 / `SEED_TABLE.md` §1).`
**교체**: `Depth roughly triples RGB. This is **consistent with**, not contrary to, the main table: the 0.688 / 0.438 pair is read at off-arm false-alarm rates of 0.359 and 0.042 respectively, and at matched FA Depth leads RGB on the H tier at every point we can read (§RT.1). There is no inversion to explain.`

### L1059 — (a) [P2]
**현재**: `for a fully occluded hazard that box necessarily covers the occluder`
**교체**: `for a hazard that contributes zero pixels of its own surface, that box necessarily covers the occluder` *(F7이 "fully occluded"를 폐기한 이상, RT 본문 자체도 그 단어를 쓰지 않는다.)*

### L1181 — (a) [P2]
**현재**: `but note that for a fully occluded hazard the amodal silhouette necessarily covers the occluder too`
**교체**: `but note that when the hazard contributes zero pixels of its own surface the amodal silhouette necessarily covers the occluder too`

---

## 3. `experiments/dayrun_0820/runs/v2/SEED_TABLE.md`

### L11–13 (§1 헤드라인 표) — (b) [P0]
**현재**: rgb H `0.688 ± 0.141` / FA `0.359 ± 0.127` 와 depth H `0.438 ± 0.031` / FA `0.042 ± 0.029` 가 **같은 열**에 병렬로 인쇄됨(각주 없음).
**교체(각주 신설, 표 위/아래 어디든 1회)**: `> **읽는 법(필수).** H 열의 rgb 0.688과 depth 0.438은 **서로 다른 운용점**의 값이다 — off팔 FA가 0.359 대 0.042로 8.6배 차이난다. FA를 맞추면 전 지점에서 Depth ≥ RGB이다(FA .359: .781 vs .729 · FA .10: .510 vs .326 · FA .05: .479 vs .243, `rt_response/F1_FA_MATCHED.md`). 이 표의 H 열을 모델 간 비교로 인용할 때는 반드시 FA 정합 표를 병기한다.`

### L19–21 (§2 twin delta) — (g) [P2]
**현재**: `| rgb | 3 | 0.314 ± 0.007 | 0.285 ± 0.094 | ...` (H tier 열, 주석 없음)
**교체(열 각주)**: `twin delta (H tier)는 **2개 씬(scene14 60 · scene15 36)** 위에서 계산된 pooled 값이다. 씬별로는 scene14가 효과를 전담하고 scene15는 0과 구별되지 않는다(rgb −.010/.209/−.058). 신뢰구간은 보고하지 않는다(§RT.5).`

### L71–76 (§4.2) — (a)(c) [P0]
**현재**: `**The D22 constructive ceiling is confirmed on all three seeds, with zero mapping leak.** ... Per `METRICS_NOTES_yolo.md` §1 and §3 this is the *required* result, not a disappointment: the `det2cell` mapping projects a detected box onto the ground plane, so a hazard with no visible pixels can produce no box and therefore no cell.`
**교체**: `**The D22 adapter ceiling is confirmed on all three seeds, with zero mapping leak.** ... this is the *required* result for **our adapter**: `det2cell` projects a detected box's bottom edge onto the ground plane, and the oracle-box diagnostic already fixes E = H = 0.000 before training. `METRICS_NOTES_yolo.md` §0 states the scope explicitly — *"every property of that adapter is a property of the adapter"*. **This row is not evidence that detection has a zero ceiling**; that question is answered adapter-free in `METRICS.md` §RT.3, where the image-space H hit rate is 0.066 and its twin-conditional value is −0.010.`

### L117 (표 행) — (d) [P1]
**현재**: `| cell_f1 | 0.5255 | 0.4852 | **+0.0403** [0.0001, 0.0786] | yes (barely) |`
**교체**: `| cell_f1 | 0.5255 | 0.4852 | **+0.0403** [0.0001, 0.0786] frame-i.i.d. · [−0.2580, 0.2054] scene-cluster | **no (withdrawn, §RT.5)** |`

### L124 (표 행) — (d) [P0]
**현재**: `| **cell_recall_H** | 0.6072 | 0.2527 | **+0.3546** [0.2768, 0.4302] | yes |`
**교체**: `| **cell_recall_H** | 0.6072 | 0.2527 | **+0.3546** [0.2768, 0.4302] frame-i.i.d. · **[−0.1429, 0.4625] scene-cluster** | **no (withdrawn, §RT.5 / D41⑤)** |`
> 주: L151–154의 D41 정정 부기는 이미 붙어 있으나 **표 행 자체가 아직 `yes`를 인쇄**한다. 표만 읽는 독자에게는 철회가 보이지 않는다.

### L134–138 (§5.2) — (d) [P0] **— 상위 5 후보(RT.5가 "더 중대"로 명시)**
**현재**: `while *raising the H-tier cell recall by +0.355* — the single largest confirmed effect in the table, and the one that matters for this paper's thesis. The twin evidence agrees independently: the H-tier twin Δ nearly doubles, 0.170 → 0.326.`
**교체**: `while raising the H-tier cell recall by **+0.355** as a point estimate. This was previously described as the largest *confirmed* effect in the table; that description is **withdrawn** — under scene-cluster resampling the interval is [−0.1429, 0.4625] and includes zero, because the frame-level interval was measuring variation within the same two H scenes. The twin evidence moves the same way (H-tier Δ 0.170 → 0.326) and rests on the same two scenes. What survives clustering is the precision / false-alarm family only.`

### L145–147 (§5.2 caveats) — (d) [P1]
**현재**: `(i) The headline-sounding H gain at *frame* level, +0.125, has a **CI containing zero** ([−0.010, 0.253]); only the *cell*-level H gain is confirmed. Write the claim at cell level or not at all.`
**교체**: `(i) Neither H gain is confirmed. Frame level +0.125 contains zero under both units; cell level +0.355 contains zero under scene resampling. Write the H claim as a point estimate with the two-scene caveat, or not at all.`

---

## 4. `experiments/dayrun_0820/narrative/brief_prof_0820.md` (교수 대면 브리핑 — 노출도 최고)

### L16 — (a) [P1]
**현재**: `H  ● ──시선──▶  ▔▔▔▔▔▉▉▉▉▉▉     낙차 픽셀이 단 한 장도 없음           45장 (test  21)`
**교체**: `H  ● ──시선──▶  ▔▔▔▔▔▉▉▉▉▉▉     낙차 자체의 기여 픽셀 0(내부면·림 모두)   45장 (test  21)`
+ 도식 아래 한 줄 신설: `※ "기여 픽셀 0"은 낙차 표면의 투영에 대한 **기하 술어**다. 두 팔의 이미지가 같다는 뜻이 아니다 — test H 96쌍 전부가 픽셀 단위로 다르다(중앙값 프레임의 4.51 %가 ≥32/255, 렌더러 노이즈 바닥의 1,872배).`

### L34 — (a) [P0] **— 상위 5 후보(브리핑의 pull-quote)**
**현재**: `> **낙차 픽셀이 어느 팔에도 없는데 반응이 떨어진다 = 맥락 사용의 인과 증거.**`
**교체**: `> **낙차 표면의 픽셀이 어느 팔에도 없는데 반응이 떨어진다 = "씬에 낙차가 있다는 사실"이 원인이라는 인과 증거.** 단 여기까지다 — 트윈은 *무엇이* 원인인지(그림자·간접광·함께 지워진 구조물·코퍼스 단서 규약 중 어느 것인지)를 가르지 못한다. 08-23 CUE-OFF 개입 결과는 RGB가 **단서 어휘만 있고 낙차가 없는** 프레임에서 FA 1.000으로 발화함을 보인다 → 현재 정확한 표현은 **"단서 연합이지 단서 추론이 아니다"**.`

### L25–32 (트윈 Δ 표 + "CI가 0 배제" 열) — (g) [P0]
**현재**: `| **H** | **21** | **0.2398 [0.1556, 0.3313]** | **예** |` (및 E 행 `0.1891 [0.0402, 0.3337] | 예`)
**교체**: E·H 행의 CI와 "예"를 제거하고 점추정만 남긴 뒤 표 각주 — `※ E·H 행은 신뢰구간을 싣지 않는다. v1 test의 E는 1개 씬, H는 2개 씬(scene14·scene15)에서 나온다 — 프레임을 독립 단위로 본 부트스트랩은 클러스터 2개짜리 열거의 산물이다. 씬별 값을 그 씬의 off팔 FA와 나란히 싣는 것이 대체 보고 형식이다(scene14 rgb .278/.448/.558 · scene15 rgb −.010/.209/−.058).`

### L35 — (e) [P1]
**현재**: `> (단서: 하드 네거티브 씬 N3에서는 낙차가 양쪽 다 없는데도 RGB Δ_frame이 0.252 — 장식(dressing) 자체에도 반응한다. 장식 불변 대조군이 다음 과제.)`
**교체**: `> (장식 불변 대조군은 08-21에 실행됐고 결과는 더 강하다: N3에서 RGB는 **양쪽 팔 모두** 0.75–1.00의 프레임에서 평균 최대확률 0.74–0.95로 발화한다 — Δ≈0은 침묵이 아니라 **포화**다. Depth는 실제로 조용하고(0.000–0.125) B2는 혼재. 즉 널 대조군은 **장치는 통과, RGB 모델은 탈락**이며 이 사실은 팔 한정으로 서술해야 한다.)`

### L41 — (a) [P2]
**현재**: `이 프레임의 낙차 기여 픽셀은 0장(H)인데, 모델은 5–12 m 밴드 한 줄(A3–E3)을 **max p 0.821** 로 켰다.`
**교체**: `이 프레임의 낙차 기여 픽셀은 0장(H)인데 — 그렇다고 낙차 있음/없음 두 렌더가 같은 것은 아니다(scene14 잔차 중앙값 프레임의 7.57 %) — 모델은 5–12 m 밴드 한 줄(A3–E3)을 **max p 0.821** 로 켰다.`

### L57 / L66 — (b) [P0]
**현재**: 본 표 rgb H `**0.688 ± 0.141**` (굵게) · 머리기사 `RGB U-Net의 H recall이 v1의 0.048–0.333에서 v2의 0.594–0.875로 올라갔고`
**교체(표 각주 + 머리기사 보강)**: `> **H 열을 모델 간 비교로 읽지 말 것.** rgb 0.688은 FA 0.359에서, depth 0.438은 FA 0.042에서 읽은 값이다. FA를 맞추면 전 지점에서 Depth ≥ RGB(FA .10에서 .510 vs .326). 살아남는 주장은 더 약하고 충분한 쪽이다 — **"FA 10 % 예산에서도 단안 RGB가 은닉 티어 프레임의 1/3(0.326 ± 0.229)을 회수하며, 같은 티어에서 검출기 기준선의 트윈-조건부 회수율은 −0.010"**. 또한 RGB의 H 발화 중 44.7 %는 낙차를 지운 트윈에서도 발화한다(트윈-조건부 recall 0.688 → 0.375).`

### L60, L62 — (c) [P0] **— 상위 5 후보**
**현재**: `> † **YOLO의 E·H = 0은 구성적 상한이지 실측 실패가 아니다.** ... 박스 하단변을 지면에 투영하는 매핑 규칙 아래에서 비가시 낙차는 원리상 셀을 켤 수 없다.`
**교체**: `> † **YOLO의 E·H = 0은 우리 어댑터(`det2cell`)의 성질이다** — 검출 패러다임 일반의 상한이 아니다. GT 박스를 conf 1.0으로 넣은 오라클 천장도 E·H 0.000이므로, 이 0은 학습 이전에 이미 고정돼 있다. **어댑터를 제거하고 이미지 공간에서 직접 재면 0이 아니다**(H 프레임의 0.066이 amodal GT 박스와 IoU>0). 실제로 성립하는 더 강한 진술은 트윈-조건부 형태다: 같은 컷의 낙차 삭제 트윈에서의 값이 0.076이므로 **위험-조건부 회수율은 −0.010**(가시 티어는 +0.337). 즉 "amodal로 학습시킨 검출기조차 기여 픽셀 0 상황에서는 위험에 조건부인 증거를 전혀 만들지 못한다"가 논문에 쓸 문장이다. (`METRICS.md` §RT.3)`
+ 표 행 L60의 `0.000 †`는 3시드 값 `**0.000 ± 0.000**`으로 갱신(아래 L64 참조).

### L64 — (h) [P1]
**현재**: `> **YOLO 행은 seed 42 단일 시드다** — seed 43/44는 GPU 점유(다른 세션) 때문에 보류 중이며, 완료되면 다른 세 행과 같은 평균±범위로 교체한다. aux 픽셀 손실 ablation(1런)도 같은 이유로 대기 중이다.`
**교체**: `> **YOLO 행은 3시드로 확정됐다**(08-21, `SEED_TABLE.md` §4): V 0.150 ± 0.028 · E·H 0.000 ± 0.000(프레임·셀 양쪽, 3/3 시드) · off FA 0.005/0.025/0.042. aux 픽셀 손실 ablation도 완료됐으나 **부록 전용**이며 유의 주장은 철회됐다(§RT.5).`

### L68 ⓑ — (b) [P0]
**현재**: `ⓑ Depth의 H가 v1(0.714, test H 21장 단일 시드)보다 낮아진 것은 퇴보가 아니라 **확장된 H셋이 원거리 위주**여서다. 멀수록 depth의 불연속 신호가 묻히고 RGB의 맥락 단서가 상대적으로 유리해진다 — RGB 역전과 같은 현상의 양면이다.`
**교체**: `ⓑ Depth의 H가 v1(0.714)보다 낮아진 것은 퇴보가 아니라 **test 구성 변화 100 %**다 — v1의 바로 그 21장 위에서 v2-Depth는 0.857로 v1-Depth를 이긴다. 확장된 75장이 원거리(`cam.d` 평균 8.57 m)이고, `d ≥ 9 m` 구간에서 Depth의 H recall은 3시드 모두 정확히 0.000이다. **"RGB 역전"이라는 표현은 쓰지 않는다** — 두 팔은 같은 τ에서 읽혔을 뿐 같은 운용점에서 읽힌 적이 없고, FA를 맞추면 역전은 사라진다(§RT.1).`

---

## 5. 우리 소유 문서의 PS 잔재 (부차 — 논문 본문 경로는 아니나 인용원이 된다)

### `experiments/dayrun_0820/DAYRUN_REPORT.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 107 | (c) [P1] | `**YOLO 어댑터 오라클 천장 (D22)** … = **완벽한 검출기의 상한**` | `**YOLO 어댑터 오라클 천장 (D22)** … = **완벽한 검출기라도 이 어댑터로는 이 이상 못 간다**는 어댑터 상한. 검출 패러다임의 상한이 아니다(§RT.3)` |
| 110–115 | (c)(a) [P1] | `> **YOLO의 H = 0은 "구성적"이다, 실측이 아니다.** … 이 매핑 규칙 아래에서는 E·H가 **0이 아닐 수가 없다**. 그러니 YOLO 행의 0은 … "가시성 검출기 + 이 어댑터로는 원리상 불가"다.` | `> **YOLO의 H = 0은 이 어댑터의 성질이다.** … 이 매핑 규칙 아래에서는 E·H가 0이 아닐 수가 없다 — 그러나 이는 `det2cell`에 대한 진술이지 검출기에 대한 진술이 아니다. 어댑터를 빼고 이미지 공간에서 재면 H 0.066이며, 성립하는 진술은 **트윈-조건부 −0.010**(가시 티어 +0.337)이다.` |
| 144 | (c) [P2] | `**"구성적 0"으로 명기.**` | `**"어댑터 상한 0"으로 명기**(D41③ 철회 반영).` |
| 167–172 | (b) [P1] | `**(4) Depth의 H recall이 v1보다 떨어졌다 — RGB 역전의 다른 면이다.** … **즉 "Depth 하락"과 "RGB 역전"은 하나의 현상이지 두 개가 아니다.**` | `**(4) Depth의 H recall이 v1보다 떨어졌다 — 전적으로 test 구성 변화다.** … v1의 21장 위에서는 v2-Depth가 0.857로 v1-Depth(0.714)를 이긴다. **"RGB 역전"이라는 프레임은 폐기한다** — 두 팔은 서로 다른 FA에서 읽혔고, FA 정합 시 전 지점 Depth ≥ RGB다(§RT.1).` |
| 222 | (c) [P2] | `E·H=0 구성적 상한은 불변.` | `E·H=0 어댑터 상한은 불변(패러다임 상한 주장은 D41③에서 철회).` |

### `experiments/dayrun_0820/STATUS.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 42 | (b) [P1] | `RGB가 확장 H셋에서 Depth 역전(0.59-0.88 vs 0.41-0.47)` | `RGB의 H가 확장 H셋에서 Depth를 앞서 보이나 **FA가 8.6배 다른 지점의 비교**다(RGB .359 / Depth .042). FA 정합 시 역전 없음 — 사후 D41① 정정.` |

### `experiments/nightrun_0820/MORNING_REPORT_0821.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 221–223 | (b) [P0] | `이건 **본표의 순서를 뒤집는다** — 본표에서는 H 티어에서 RGB(.688)가 Depth(.438)를 앞선다. **이 역전이 발견의 핵심이다.**` | `본표의 .688/.438은 서로 다른 FA(0.359 / 0.042)에서 읽힌 값이므로 **뒤집을 순서가 애초에 없다**. FA를 맞추면 본표에서도 프로브에서도 Depth ≥ RGB다 — **프로브 결과는 본표와 모순이 아니라 일관**이다(§RT.1). 발견의 핵심은 역전이 아니라 **RGB의 H 능력이 씬 어휘에 묶여 있다는 점**이다.` |
| 225–229 | (b)(a) [P1] | `RGB가 코퍼스에서 보여준 H 티어 능력은 **의미적 맥락**이다` | `RGB가 코퍼스에서 보여준 H 티어 발화는 **코퍼스 단서 어휘와의 연합**이다 — H 발화의 44.7 %가 낙차 삭제 트윈에서도 일어나고(§RT.2), CUE-OFF의 단서 전용 팔에서 FA 1.000으로 발화한다(D46).` |
| 18, 37 | (c) [P2] | `**D22 상한(E·H = 0)이 세 시드 전부에서 누수 0으로 확인**` | `**D22 어댑터 상한(E·H = 0)이 세 시드 전부에서 누수 0으로 확인**` |

### `experiments/nightrun_0820/STATUS.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 84 | (b) [P1] | `**본표 순서 역전**(본표는 H에서 RGB .688 > Depth .438)` | `**본표와 일관**(본표의 .688 > .438은 FA 0.359 vs 0.042의 산물 — FA 정합 시 Depth ≥ RGB, D41①)` |
| 81 | (e) [P1] | `sceneN3 널 대조군 **−.001±.001** 확증(신≡ON 구조 동일).` | `sceneN3 널 대조군 **−.001±.001** — **장치 확증, 모델은 아님**: RGB는 양팔 0.75–1.00 포화(RT.4), Depth만 실제로 조용함.` |
| 56, 73 | (c) [P2] | `D22 상한 확정` / `**D22 상한 확인, 매핑…**` | `D22 **어댑터** 상한 확정` (패러다임 상한 표현 제거) |

### `experiments/dayrun_0820/narrative/diag_v1/DIAG_V1.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 146 | (a) [P1] | `Removing a 0.3 m+ drop that contributes no visible pixels still costs the RGB model 0.35 of probability in band 3.` | `Removing a 0.3 m+ drop whose own surface and rim project to zero pixels still costs the RGB model 0.35 of probability in band 3 — noting that the removal also deletes everything the scene builder places in the same branch, and that the two renders are not pixel-identical (§RT.6).` |

### `experiments/dayrun_0820/METRICS_NOTES_yolo.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 167–168 | (a) [P2] | `**One honest ugliness.** For a fully occluded hazard the amodal box necessarily covers whatever stands in front of it` | `**One honest ugliness.** When the hazard contributes zero pixels of its own surface, the amodal box necessarily covers whatever stands in front of it` |

### `experiments/weekend_0823/a3_viewpoint/3A_VIEWPOINT_AUDIT.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 246 | (a) [P1] | `removing the hazard measurably lowers the model's probability on frames where the hazard contributes no pixels.` | `removing the hazard measurably lowers the model's probability on frames where the hazard's own surface and rim contribute no pixels — a geometric condition, not an optically empty one (§RT.6).` |

### `experiments/mainrun_0819/SPEC_EXTRACTED.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 66 | (a) [P2] | `H = hazard contributes no pixels; tier decided in the order V→E→H.` | `H = hazard contributes no pixels **of its own surface or rim** (`int_px == 0 ∧ edge_vis == 0`); tier decided in the order V→E→H.` (사양 추출본이므로 원문 인용 표기 + 각주로 처리해도 무방) |

### `experiments/mainrun_0819/realworld/PROTOCOL_SHOOT.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 26–28 | (f) [P1] | `> **V2S 예고**: 섹터를 5→10으로 쪼갠 `PROVISIONAL-GRID-V2S`가 테스트 중이며, **채택 결재가 나면 격자가 다시 바뀐다**(PS §12.6). 그래도 촬영·주석은 지금 V1 20칸으로 진행한다 …` | `> **V2S 처분(2026-08-23, D43)**: 섹터 5→10 테스트 트랙은 사전등록 판정에서 **ROLLBACK**됐다(D34 부등식 9칸 중 3칸 위반 + 국소화 이득 공허 통과). **V1 20칸이 정본이고, 이번 파일럿 구간에 격자 변경은 없다.** 재도전은 §12.5 연장 우선순위 (1)로 복귀했으며 선결 조건은 test 분할에 측방 씬을 넣는 것이다. 촬영·주석은 V1 20칸으로 진행한다.` |

### `experiments/mainrun_0819/realworld/REALWORLD_GRID_PROTOCOL.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 19 | (f) [P2] | `V1 20칸 주석은 V2S로 폴딩 가능하다(§10).` | `V1 20칸이 정본이다(V2S는 D43에서 롤백; 폴딩 경로는 9월 재도전용으로 §10에 보존).` |
| 385–387 | (f) [P1] | `## 10. V2S(10섹터) 전방 호환 … `gridspec_v2s.json`은 **테스트 트랙**이며 **채택 결재 전까지** V1이 정본이다` | `## 10. V2S(10섹터) 전방 호환 — **보류된 확장 경로** … `gridspec_v2s.json`은 2026-08-23 사전등록 판정에서 **롤백**됐고(D43), V1이 정본이다. 이 절은 9월 재도전을 위한 폴딩 계약으로만 유지한다.` |
| 391 | (f) [P1] | `V2S가 채택되면 실사진 GT는 폴딩 채널에서 그대로 재사용된다. **재주석 0.**` | `V2S가 **장래에** 채택될 경우 실사진 GT는 폴딩 채널에서 그대로 재사용된다(재주석 0). 현재 채택 계획은 없다.` |
| 393 | (f) [P2] | `→ V2S 채택 시 §3.2-(d) 캘리브레이션 컷은 **선택이 아니라 필수**가 된다.` | `→ 롤백으로 이 조건은 현재 발동하지 않는다. 재도전 시 §3.2-(d) 캘리브레이션 컷이 필수가 된다는 사실만 기록해 둔다.` |

### `experiments/weekend_0823/fusion/FUSION_ROW.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 269 | (f) [P2] | `4. V2S가 채택되면 본 트랙은 **재실행이 필요하다** …` | `4. V2S는 D43에서 롤백됐으므로 이 재실행 조건은 **발동하지 않는다**. 9월 재도전 시에만 유효하다(입력이 V1 그리드 저장 CSV이므로).` |

### `experiments/weekend_0823/redteam/R2_method.md`
| 줄 | 범주 | 현재 | 교체 |
|---|---|---|---|
| 120 | (f) [P2] | `(V2S 채택 시 10섹터로 또 바뀌므로, 주석은 V1 20칸으로 받고 …)` | `(V2S는 D43에서 롤백됐다 — 주석은 V1 20칸이 정본이며 격자 변경 예정 없음.)` |

---

## 6. 이번 스윕에서 같이 걸렸으나 (a)–(g)에 속하지 않는 것 — 별도 처리 권고

1. **CUE-OFF(D46) 이후 "맥락을 읽는다"류 서술 전반.** 위 (a) 항목들에서 문장 단위로 교정했으나, §5.3의 절 제목 자체(`5.3 Twin-paired analysis: the model uses context, not hazard pixels`, RESULTS_DRAFT L59)가 이미 결론을 선언한다. 권고 제목: `5.3 Twin-paired analysis: the response is conditional on the hazard's presence, not on its pixels — and not yet on inference`.
2. **RESULTS_DRAFT L37** `| SegFormer-B2 | *tomorrow — code dry-run GREEN, untrained* |` — 3시드 완주(0821). v1 표의 역사적 스냅숏으로 남길 것이면 그렇게 명시.
3. **METRICS.md §11 / RESULTS_DRAFT §5.2** 의 "morning lever / 아침 결정" 류 미래 시제 — 해당 결정은 D18–D21에서 이미 내려졌다.
4. **`band1` 서술** — U-Net 3시드 0/4080 발화(D47). band1 열은 YOLO 단독이라는 한계 문장이 아직 어느 초안에도 없다.

---

## 7. 가장 위험한 스테일 문장 5개 (심사자 노출 순)

| # | 파일·줄 | 문장 | 왜 치명적인가 |
|---|---|---|---|
| 1 | `RESULTS_DRAFT.md` L72–75 | *"Since no hazard pixel exists in either image of an H pair, the model's response **must** be driven by the surrounding context … which is exactly the mechanism this work sets out to demonstrate."* | 논문의 **중심 주장**을 반사실이 지지하지 않는 강도로 진술한다. F7이 전제("이미지가 같다")를 직접 반증했고(96/96 픽셀 차, 중앙값 4.51 %), 토글이 낙차 외 구조물까지 지우며, D46 CUE-OFF는 단서만 있어도 FA 1.000으로 발화함을 보였다. 전제·추론·결론이 모두 무너진 한 문장. |
| 2 | `RESULTS_DRAFT.md` L316–320 | *"**any method** whose output is a bounding box over visible hazard pixels has an identically zero ceiling on the E and H tiers, **independent of detector quality**"* | 논문 프레이밍의 "가장 깨끗한 정당화"로 자칭된 문장이 **패러다임 일반화**인데, 측정된 것은 우리 `det2cell` 어댑터뿐이다. 어댑터를 빼면 H 0.066으로 0이 아니다. 심사자가 30분이면 잡는 strawman이며, 대체 문장(트윈-조건부 −0.010)이 더 강하다는 점에서 순손해다. |
| 3 | `SEED_TABLE.md` L134–138 (+ L124 표 행) | *"the single largest confirmed effect in the table, and the one that matters for this paper's thesis"* (`cell_recall_H +0.3546`) | 논문 논지에 직결된다고 **스스로 명시한** 효과의 유의성이 씬-클러스터에서 [−0.143, 0.463]로 사망. RT.5가 "둘 중 더 중대"로 지목. L151의 철회 부기는 붙었으나 **표 행이 아직 `yes`를 인쇄**해 표만 읽는 독자에게는 철회가 보이지 않는다. |
| 4 | `brief_prof_0820.md` L34 (+ L25–32 CI 표) | *"낙차 픽셀이 어느 팔에도 없는데 반응이 떨어진다 = 맥락 사용의 인과 증거."* + H 행 `0.2398 [0.1556, 0.3313] · CI 0 배제 **예**` | **교수 대면 문서의 pull-quote**이고 노출도가 가장 높다. 폐기된 용어 + 철회된 CI + CUE-OFF가 부정한 결론이 한 화면에 같이 있다. 외부로 나간 유일한 문서 계열이라 정정 지연 비용이 가장 크다. |
| 5 | `METRICS.md` L259–263 / `RESULTS_DRAFT.md` L403–405 (동률) | *"Every CI in the table excludes 0 … That is the night's cleanest evidence that the RGB arm reads context"* / *"the inversion is the finding"* | 전자는 철회된 CI를 **"가장 깨끗한 증거"**로 명명하고, 후자는 존재하지 않는 순서 역전을 **"발견"**으로 명명한다. 둘 다 "발견"이라는 단어를 잘못된 대상에 붙였고, 각각 §RT.5·§RT.1이 정면으로 대체 문장을 지정해 둔 상태다. |

---

## 8. 감사 범위 및 제외

- **읽고 편집 대상에서 제외**: `Docs/experiment/**` (사용자 저작 — PS `PROJECT_STATE_0823.md` §5.1의 `RGB .688 / YOLO 구성적 상한`, §5.2의 `9/9 CI 0 배제`, §6-4의 H recall 해석은 위와 **같은 스테일 계열**이나, 본 목록은 손대지 않는다. 승용 결재란에 "PS §5.1·§5.2·§6-4 동반 정정" 1건으로 올릴 것을 권고).
- **이미 정본인 문장은 교체 대상이 아니다**: `RESULTS_DRAFT` RT-A~RT-F(L446–502), `METRICS` RT.1–RT.8(L968–1219), `SEED_TABLE` L151–154 부기, `rt_response/APPEND_*.md`. 단 RT 본문 안에서도 **"fully occluded"라는 단어 자체**는 F7이 폐기한 용어이므로 §2 L1059·L1181, `F7_HPAIR_PIXDIFF.md` L49에서 표현만 교체한다.
- **append-only 규율**: 위 교체는 전부 "해당 줄을 고친다"로 적었으나, 동결 규율상 원문 보존이 필요하면 **각 파일 말미에 `## R6 정오표` 절을 append하고 줄 번호로 지시**하는 형태가 대안이다. 어느 쪽을 택할지는 결재 사항.
