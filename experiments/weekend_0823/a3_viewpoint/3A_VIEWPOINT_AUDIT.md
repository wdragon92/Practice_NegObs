> **⚠ 정정 배너 (08-23 R6-b)**: 본 문서의 H-티어 밴드별 CI 주장(+0.293 'CI 0 배제', −0.031 'CI∋0', L230/L250 조건부 CI)은 test H가 2씬 클러스터라는 RT.5 철회 대상에 해당 — **구간 주장 전부 철회**, 부호·크기 대비와 포즈-클러스터 점추정만 유효. 안A/안B 문장의 CI 표현은 사용 전 클러스터 문구로 교체할 것.

# 3A_VIEWPOINT_AUDIT — is the H-tier band-3a twin Δ ≈ 0 uniform, or viewpoint-concentrated?

**Queue item.** CPU-2 of `Docs/experiment/WEEKEND_BRIEF_0823.md` §6.5 (material for 결재 #4).
**Author.** Claude Code, 2026-08-23. **Reader.** someone (or some AI) seeing this project for the
first time — everything needed to read this file is defined in it or in the ledger it names.
**Compute.** CPU only, `env_seg`, `PYTHONNOUSERSITE=1`. No re-training, no re-rendering, no GPU.

---

## 0. Purpose, in one line

Decide whether the near-zero H-tier twin Δ in **band 3a** is a property of *all* viewpoints (→ the
paper keeps its "band-3b only" restriction) or the average of a mixture in which some viewpoint
does show a real effect (→ the paper could state a viewpoint-conditional claim instead).

## 1. Inputs and prior facts (all frozen, read-only)

| what | path |
|---|---|
| per-frame cell probabilities + GT, 9 runs | `experiments/dayrun_0820/runs/v2/{rgb,depth,b2}_s{42,43,44}/eval_test/per_frame.csv` |
| twin pair list (`kept` flag, `delta_score`) | `…/runs/v2/{run}/twin/twin_pairs.csv` |
| camera fields `d`, `h_rel`, light `cond`, render `round` | `experiments/dayrun_0820/dataset_manifest_v2_full.json` |
| scene split (test = 7 scenes, untouched) | `experiments/dayrun_0820/split_v2_full.json` |
| **definition ledger for 3a / 3b** | `experiments/nightrun_0820/narrative/diag_v2/DIAG_V2.md` §0.6 · §2.2 |
| dressing-control ledger (referenced, not used here) | `experiments/nightrun_0820/ctrl_dressing/CTRL_TABLE.md` |
| old C2 anatomy (referenced, not used here) | `experiments/dayrun_0820/narrative/diag_v1/DIAG_V1.md` §3 |

**Definitions are taken from the ledger and are not restated in a new form.** Per `DIAG_V2.md`:
grid `PROVISIONAL-GRID-V1` = 20 cells = 5 sectors × 4 distance bands, `1=[0,2) · 2=[2,5) ·
3a=[5,8) · 3b=[8,12)` m, cell index = `band·5 + sector`. The twin Δ of a band `b` is

> `Δ_b = max p over the GT-positive cells of band b on the hazard-ON frame − max p over the SAME
> cells on its pose-matched hazard-OFF twin.`

**Tier H** = the hazard contributes **zero** visible pixels (`DIAG_V2` §0.1). **τ = 0.5.**

**The number under audit** (`DIAG_V2` §2.2, 96 kept H-tier pairs): RGB Δ_3a = **−0.031 ± 0.054**
(s42 point −0.049, 95 % CI [−0.127, **+0.017**], contains 0) against Δ_3b = **+0.293 ± 0.087**
(CI [+0.138, +0.233], clear of 0). This is what made the paper's H claim band-3b-only
(`experiments/mainrun_0819/RESULTS_DRAFT.md` §N.1).

**Sanity gate.** This audit recomputes Δ from the raw per-frame probabilities and reproduces
`twin_pairs.csv` `delta_score` to **max |dev| = 0.0000 over all 9 runs**, and reproduces every
`DIAG_V2` §2.2 cell exactly (RGB 3a −0.0305 ± 0.0541 / 3b +0.2930 ± 0.0868 · Depth +0.5336 ±
0.1830 / +0.4107 ± 0.0308 · B2 +0.0578 ± 0.0598 / +0.1119 ± 0.0639). **Nothing below is a second
measurement; it is the published statistic, split.** Source of every number: `a3_viewpoint_numbers.json`
in this directory (produced by `a3_viewpoint.py`, ~9 min), per-pair dump `a3_strata.csv`, figure
`a3_viewpoint.png`.

## 2. What the H test set actually contains — read this before any stratum table

This is the single most important section, because three structural facts limit what any
stratification can say, and two of them were not on record before.

**(a) Only two scenes carry test H frames.** scene14 (60 pairs) and scene15 (36 pairs). So
**"occluder type" is perfectly confounded with scene id** and cannot be estimated separately:

| scene | occluder mechanism (from the scene source header) | H pairs | of which have band-3a GT |
|---|---|---|---|
| `scene14_grandstair_illusion` | **tread/landing self-occlusion** — a 40-step, 6.0 m descent read as a flat terrace because only the landings are visible | 60 | 21 |
| `scene15_alley_labyrinth` | **lateral wall + 25° bend** — a 4.25 m descent hidden behind a corridor bend inside a 1.2 m wide walled alley | 36 | 12 |

**(b) The 96 H pairs are 32 camera poses × 3 light conditions; the 33 band-3a pairs are only
11 camera poses × 3 light conditions.** Every pose appears exactly three times (once per light
condition), verified. A frame-level bootstrap therefore treats three renders of *one viewpoint* as
three independent samples. **Every headline in this file is therefore reported at the camera-pose
level as well** (pose = sampling unit, light replicates averaged inside the pose), and the
pose-level CI is the one to quote.

**(c) The h × scene design is not crossed — it is nearly nested.** `scene15` is a `CAM-2` scene
(`variation_kit.py: CAM2_SCENES`), so its camera height is capped at 1.20 m; and inside the band-3a
subset the two scenes occupy disjoint height bins:

| band-3a subset (33 pairs / 11 poses) | h_lo `[0.25,0.60)` "robot ≈0.3" | h_mid `[0.60,1.20)` "≈0.9" | h_hi `[1.20,1.90]` "≈1.8" |
|---|---|---|---|
| scene14 | **0** | 15 (5 poses) | 6 (2 poses) |
| scene15 | 12 (4 poses) | **0** | structurally impossible (CAM-2 cap) |

So in band 3a, **"low camera" and "scene15" are the same stratum**, and "mid camera" and "scene14"
are the same stratum. Any height effect found in band 3a is *identically* a scene effect. This is
the gap the optional GPU-5 probe in §7 is designed to close. (In the full 96-pair H set the design
is better: scene14 does have 9 h_lo pairs and scene15 9 h_mid pairs, which is what lets §5 separate
them for band 3b.)

**(d) Band 3a is not a far-standoff set.** All 33 band-3a pairs sit at camera standoff
`d ∈ [4.59, 7.51]` m; the band-3b set spans `d ∈ [4.59, 11.21]` m. Band membership and standoff are
strongly coupled, exactly as `DIAG_V2` §0.3 warned.

## 3. Result 1 — band 3a is uniformly null for RGB. No stratum rescues it.

Cluster-level (pose = sampling unit), 3-seed mean of the per-pose Δ, s42 percentile bootstrap over
poses, 10 000 resamples. `n` = poses (frames = 3 × poses).

| stratum | poses | RGB Δ_3a (3-seed) | median pose | poses +/− | s42 cluster CI |
|---|---|---|---|---|---|
| **ALL H** | 11 | **−0.031** | **+0.017** | 7 / 4 | [−0.187, +0.043] **contains 0** |
| scene14 (tread self-occlusion) | 7 | −0.070 | −0.021 | 3 / 4 | [−0.293, +0.061] contains 0 |
| scene15 (wall + bend) | 4 | +0.039 | +0.034 | 4 / 0 | [−0.011, +0.032] contains 0 |
| h_lo ≈ robot 0.3 m ( ≡ scene15) | 4 | +0.039 | +0.034 | 4 / 0 | [−0.011, +0.032] contains 0 |
| h_mid ≈ 0.9 m ( ≡ scene14) | 5 | −0.108 | −0.095 | 1 / 4 | [−0.418, +0.042] contains 0 |
| h_hi ≈ 1.8 m | 2 | +0.024 | +0.024 | 2 / 0 | *n < 5 — not read* |
| d < 7 m | 8 | −0.050 | +0.003 | 4 / 4 | [−0.260, +0.052] contains 0 |
| d 7–9 m | 3 | +0.022 | +0.017 | 3 / 0 | *n < 5 — not read* |
| d ≥ 9 m | 0 | — | — | — | band 3a has no pair beyond 7.51 m |

**Not one stratum has a band-3a CI clear of zero, in either direction.** Two further checks kill any
remaining "it is concentrated somewhere" reading:

1. **Leave-one-pose-out.** The single most influential pose is `scene14 · main round · d = 4.594 m ·
   h = 0.954 m`, whose 3-seed Δ_3a is **−0.353**. Dropping it moves the whole-set estimate from
   **−0.031 to +0.0017** — i.e. to zero from the other side, not to a positive effect. The jackknife
   range over all 11 poses is only **[−0.042, +0.002]**. And that pose is not even self-consistent:
   its per-seed values are **−0.656 / −0.648 / +0.246**.
2. **Continuous dependence.** Spearman ρ between per-pair Δ_3a and the viewpoint variables, computed
   per run (permutation p, no scipy): RGB Δ_3a vs `h_rel` gives ρ = **+0.018 / −0.501 / +0.216** and
   vs `d` gives **+0.489 / +0.738 / −0.123** — **the sign does not survive a change of seed** in
   either case. For contrast, the same test on band 3b gives RGB Δ_3b vs `h_rel` ρ =
   **+0.520 / +0.380 / +0.663** (sign-consistent) and Depth Δ vs `d` ρ ≈ **−0.83 / −0.87**
   (sign-consistent, and the twin counterpart of `DIAG_V2` §0.3's Depth-recall collapse beyond 9 m).
   So the method *can* detect a viewpoint dependence when there is one; there is none in RGB's 3a.

**Depth and B2 in band 3a, for completeness.** Depth is positive at every pose (11/11 poses > 0,
pose-mean +0.534, cluster CI [+0.369, +0.891]) — its 3a claim is *not* fragile and is not what
ruling #4 is about. B2's 3a pose-mean is +0.058 with cluster CI [−0.155, +0.071] — null, as
`DIAG_V2` already said.

**A control that tells us what the 3a null *is*.** Band 3a is not a dead region of the grid. On the
same 20-cell grid, same pairs file, same τ, RGB's twin Δ in band 3a by evidence tier is

| RGB Δ_3a by tier | V (n = 144 pairs) | E (n = 24) | **H (n = 33)** |
|---|---|---|---|
| 3-seed mean ± range/2 | **+0.405 ± 0.044** | +0.131 ± 0.106 | **−0.031 ± 0.054** |
| (same, band 3b) | +0.371 ± 0.061 | +0.153 ± 0.081 | +0.293 ± 0.087 |

So RGB responds causally to a hazard in band 3a perfectly well **when the hazard is visible**. The
null is a property of **occlusion at short standoff**, not of the band or the grid. That is exactly
the statement the paper needs, and it is stronger than "we did not measure an effect".

## 4. Result 2 (unlooked-for, and it matters more) — inside band 3b the RGB claim is **scene-concentrated**

The same machinery applied to band 3b, where the paper's H claim lives:

| stratum | poses | RGB Δ_3b (3-seed) | per-seed | poses +/− | s42 cluster CI |
|---|---|---|---|---|---|
| **ALL H** | 32 | **+0.293** | 0.185 / 0.359 / 0.335 | 28 / 4 | [+0.108, +0.265] **clear of 0** |
| **scene14** (tread self-occlusion) | 20 | **+0.441** | 0.302 / 0.448 / 0.571 | **20 / 0** | [+0.208, +0.398] **clear of 0** |
| **scene15** (wall + bend) | 12 | **+0.047** | −0.010 / **+0.209** / −0.058 | 8 / 4 | [−0.022, +0.001] **contains 0** |
| h_lo ≈ robot 0.3 m | 12 | +0.120 | 0.049 / 0.272 / 0.038 | 8 / 4 | [−0.010, +0.129] **contains 0** |
| h_mid ≈ 0.9 m | 12 | +0.343 | — | 12 / 0 | [+0.116, +0.340] clear of 0 |
| h_hi ≈ 1.8 m | 8 | +0.478 | — | 8 / 0 | [+0.139, +0.519] clear of 0 |
| d < 7 m | 8 | +0.343 | — | 8 / 0 | [+0.106, +0.453] clear of 0 |
| d 7–9 m | 10 | +0.371 | — | 10 / 0 | [+0.080, +0.360] clear of 0 |
| d ≥ 9 m | 14 | +0.209 | — | 10 / 4 | [+0.026, +0.214] clear of 0 |

Two things follow.

- **The 3b H claim is carried by scene14.** scene15's Δ_3b is +0.047, its sign flips across seeds
  (−0.010 / +0.209 / −0.058), 4 of its 12 poses are negative, and its cluster CI contains zero. The
  mechanism is visible in the raw rates: in scene15 the **hazard-OFF** arm already fires in band 3b
  on **50 %** of frames (RGB, 3-seed) against **21.7 %** in scene14, while on-arm recall is similar
  (0.657 vs 0.706). The alley scene's *appearance alone* is enough to make the model fire, so
  removing the hazard changes little — the same shortcut signature `CTRL_TABLE.md` documents for
  sceneC2/sceneN3, now visible inside the headline H rows.
- **Height, not standoff, is the reproducible viewpoint axis for 3b** (ρ̄ = +0.52, sign-consistent
  over 3 seeds), and the **robot-height stratum is the weak one**: +0.120 with a pose-clustered CI
  that contains zero. (A frame-level bootstrap, which double-counts light replicates, would have
  reported [+0.010, +0.095] and called it significant. This is exactly why §2(b) matters.) But h_lo
  is 9/12 scene15 poses, so this is partly the same scene effect; within scene14 alone the h_lo
  poses give **+0.348** (3 poses — below the n ≥ 5 reading floor, reported for direction only).
- **Depth's band-3b Δ collapses beyond 9 m standoff**: **+0.009** over 14 poses, pose-clustered CI
  **[−0.005, +0.037] containing zero**, per-seed 0.012 / 0.001 / 0.013 — the causal twin of
  `DIAG_V2` §0.3's "Depth H recall is exactly 0 beyond 9 m on all three seeds". RGB's does **not**
  collapse there (**+0.209**, CI [+0.026, +0.214], clear of zero). This is worth one sentence in the
  paper's robustness paragraph: it is the one stratum where the RGB-vs-Depth story inverts cleanly,
  and it is a *range* effect (reproducible) rather than a scene effect.

## 5. Verdict

> **The band-3a Δ ≈ 0 is uniform, not concentrated.** Across 11 camera poses, 2 scenes, 3 height
> bins and 3 standoff bins, **no stratum shows an RGB band-3a twin Δ whose CI clears zero**, in
> either direction. The whole-set point estimate is negative only because of one camera pose
> (`scene14`, d 4.59 m, h 0.95 m, Δ = −0.353) whose own sign flips across seeds; removing it gives
> **+0.002**. Δ_3a has no reproducible dependence on camera height or standoff (Spearman sign flips
> across seeds on both axes), whereas the same test does recover the known height dependence in
> band 3b and the known Depth range collapse. And the tier control shows RGB's band-3a response is
> strongly causal when the hazard is **visible** (V tier +0.405), so the null is a property of
> *occlusion at short standoff*, not of the band.
>
> **Therefore ruling #4 should be re-affirmed as "3b 한정 유지", not converted into a
> viewpoint-conditional claim** — the viewpoint decomposition removes the "maybe it is just the
> viewpoint" escape route rather than opening it.
>
> **But the audit found a different restriction that the paper does not yet carry**: inside band 3b
> the RGB causal evidence is **scene/occluder-concentrated** (scene14 +0.441, 20/20 poses positive
> vs scene15 +0.047, CI ∋ 0, sign-unstable), and the **robot-height** stratum loses its clearance of
> zero once light replicates of one viewpoint stop being counted as independent samples. That
> belongs in the limitations set, not in the headline.

**Claude 예비 판정 (preliminary reading, per WEEKEND_BRIEF §5.3 — the decision is 승용's).**
Adopt **"3b 한정 유지"** *and* add one limitation sentence about the scene concentration and the
robot-height stratum. Confidence: **high** for the 3a verdict (three independent checks agree, and
the negative direction is the one that cannot help the claim); **medium** for the scene-concentration
caveat (12 poses in one scene; the seed instability is real but the sample is small).

**무응답 시 기본값 (default if no reply).** Keep the RESULTS_DRAFT §N.1 wording as it stands, append
the §6 limitation sentence, and do **not** run the GPU-5 probe (§7) — it cannot change the 3a
verdict, only tighten the confound behind the *secondary* caveat.

## 6. Both draft sentences (양안) — for RESULTS_DRAFT §N.1

Sentence A is the recommended one. Both are written to drop into the existing §N.1 paragraph.

### 안 A — "3b 한정 유지" (recommended)

> **English (paper).** On the 96 pose-matched H-tier pairs the RGB model's counterfactual response
> is confined to the far band: Δ = **+0.293 ± 0.087** in band 3b `[8,12)` m (95 % CI clear of zero)
> against **−0.031 ± 0.054** in band 3a `[5,8)` m (CI [−0.127, +0.017]). A viewpoint stratification
> shows this is not an averaging artefact: decomposed over the 11 camera poses that carry band-3a
> ground truth — 2 scenes, 3 camera-height bins, 2 standoff bins — **no stratum yields a band-3a Δ
> whose interval clears zero**, the per-pose sign vote is 7 positive / 4 negative with median
> **+0.017**, and the negative point estimate is driven by a single pose whose own sign is not
> reproducible across seeds (leave-one-pose-out: −0.031 → +0.002). Δ_3a shows no seed-reproducible
> dependence on camera height or standoff, while the same test does recover the model's known height
> dependence in band 3b. The null is specific to occluded hazards: on the same band and the same
> pairs, RGB's Δ is **+0.405 ± 0.044** for tier V, where the drop is visible. **We therefore state
> the RGB context-response result for band 3b only**, and report band 3a as a measured null rather
> than as missing evidence.
>
> **한국어 (내부 판독문).** H 96쌍의 RGB 반사실 반응은 원거리 밴드에 한정된다 — 3b `[8,12)` m에서
> +0.293 ± 0.087(CI 0 배제), 3a `[5,8)` m에서 −0.031 ± 0.054(CI ∋ 0). 시점 층화 결과 이것은 평균화
> 착시가 아니다: 3a GT를 가진 카메라 포즈 11개(씬 2 × 높이 3구간 × 거리 2구간) 어느 층에서도 CI가
> 0을 배제하지 않고, 포즈 부호 투표는 7 대 4(중앙값 +0.017), 음수 점추정은 시드마다 부호가 뒤집히는
> 단일 포즈가 만든 것이다(해당 포즈 제거 시 −0.031 → +0.002). Δ_3a는 카메라 높이·거리 어느 쪽으로도
> 시드 재현되는 의존성이 없다(같은 검정이 3b의 높이 의존성은 재현해 낸다). 이 널은 **가려진** 위험에
> 국한된다 — 같은 밴드·같은 쌍에서 V 티어(낙차가 보이는 경우) Δ는 +0.405 ± 0.044이다. 따라서 RGB
> 맥락 반응 주장은 **3b 한정**으로 서술하고, 3a는 "증거 없음"이 아니라 **측정된 널**로 보고한다.

### 안 B — "시점 조건부 서술" (the alternative; **evidence does not support it — kept for the 결재란 record**)

> **English (paper).** The RGB model's counterfactual H-tier response depends on viewpoint rather
> than on band alone: it is present at mid and high camera heights (Δ_3b = +0.343 and +0.478, both
> CIs clear of zero) and at every standoff bin out to 12 m, but is not demonstrated at robot camera
> height (h < 0.6 m, Δ_3b = +0.120, pose-clustered CI [−0.010, +0.129]) nor anywhere in band 3a
> (Δ_3a = −0.031, CI [−0.127, +0.017]). We therefore state the result as conditional on viewpoint:
> *for cameras at ≥ 0.6 m and hazards at ≥ 8 m, removing the hazard measurably lowers the model's
> probability on frames where the hazard's own surface and rim contribute no pixels — a geometric
> condition, not an optically empty one (§RT.6).*
>
> **한국어 (내부 판독문).** RGB의 H 티어 반사실 반응은 밴드가 아니라 **시점**에 의존한다 — 중·고
> 카메라 높이에서는 성립(Δ_3b = +0.343 / +0.478, CI 0 배제)하고 12 m까지 모든 거리 구간에서
> 성립하지만, 로봇 눈높이(h < 0.6 m, Δ_3b = +0.120, 포즈 군집 CI [−0.010, +0.129])와 3a 전 구간
> (−0.031, CI ∋ 0)에서는 입증되지 않는다. 따라서 "카메라 ≥ 0.6 m, 위험 ≥ 8 m 조건에서" 조건부로
> 서술한다.
>
> **Why B is not recommended.** (i) It buys nothing for band 3a — B still cannot state 3a, so the
> "3b 한정" restriction survives inside it anyway. (ii) It *adds* an exclusion (robot height) that
> rests on 12 poses of which 9 are one scene, so the height axis and the scene axis are not
> separated; stating a height condition would over-attribute a scene effect to the camera.
> (iii) The robot viewpoint is the deployment-relevant one (`scripts/make_review_gallery.py`
> calls h0.3 the primary judging view), so a sentence that formally excludes it is a strictly
> worse claim than a sentence that does not mention height — while the underlying weakness is
> still disclosed in the limitations set. B is the honest fallback **only if** the GPU-5 probe (§7)
> later separates height from scene and the height effect survives.

### 6.1 Limitation sentence to add under **either** option (new, from §4)

> **English (limitations).** The H-tier evidence is not evenly distributed over the test set. All 96
> H pairs come from two scenes, and the causal effect is concentrated in the tread-self-occlusion
> scene (`scene14`, Δ_3b = +0.441, 20/20 camera poses positive) while the corridor-occlusion scene
> (`scene15`) gives +0.047 with a pose-clustered interval containing zero and a sign that flips
> across seeds. In `scene15` the hazard-**off** arm already fires in band 3b on 50 % of frames
> (against 21.7 % in `scene14`), i.e. the scene's appearance alone suffices — the same shortcut
> signature we document for the dressing-preserving control arm. The H claim should be read as
> demonstrated for one occlusion mechanism, not for occlusion in general.
>
> **한국어.** H 증거는 test 전체에 고르게 분포하지 않는다. H 96쌍은 씬 2개에서만 나오고, 인과 효과는
> **디딤판 자기가림** 씬(scene14, Δ_3b = +0.441, 포즈 20/20 양수)에 집중되며 **복도 굴절** 씬
> (scene15)은 +0.047·포즈 군집 CI가 0 포함·시드별 부호 반전이다. scene15에서는 위험 **off** 팔이
> 이미 3b에서 프레임의 50 %를 발화시킨다(scene14는 21.7 %) — 즉 씬 외관만으로 발화한다는, 장식보존
> 대조군에서 본 것과 같은 지름길 서명이다. H 주장은 "가림 일반"이 아니라 **하나의 가림 기제에 대해
> 입증된 것**으로 읽어야 한다.

## 7. Optional render probe spec (GPU-5) — **conditional; it cannot change the §5 verdict**

The brief's render branch is triggered only by a concentration signal. **There is none in band 3a**,
so the probe is *not* required for ruling #4. It is specified here because a *different* signal did
emerge — the scene/height confound behind §4 — and the orchestrator may want it for the limitation
sentence. Recommendation: **run only if GPU-5 is otherwise idle after GPU-0…4.**

**Question it answers.** In band 3b, is the weak robot-height stratum a *camera-height* effect or a
*scene/occluder* effect? Today they cannot be separated: 9 of the 12 h_lo poses are `scene15`, and
in band 3a the two factors are perfectly nested (§2c).

**Design — fill the two structurally empty design cells, hazard geometry untouched.**

| arm | scene | camera height `h_rel` (m) | standoff `d` (m) | why |
|---|---|---|---|---|
| P1 | `scene14` (tread self-occlusion) | **0.28 – 0.58** (h_lo) | 4.6 – 7.5 | cell `scene14 × h_lo × band 3a` is **empty** (0 poses); `scene14 × h_lo × 3b` has only 3 |
| P2 | `scene15` (wall + bend) | **0.62 – 1.15** (h_mid, CAM-2 cap 1.20) | 6.0 – 7.6 | cell `scene15 × h_mid × band 3a` is **empty** (0 poses) |

**Counts.** 8 accepted camera poses per arm × 3 light conditions × 2 hazard arms (on/off, pose- and
light-identical) = **96 frames**. Tier H and band-3a GT are *derived*, not requested, so over-sample
the pose grid ×2.5 and keep only poses whose ON frame lands `tier == H` with ≥ 1 GT-positive cell in
band 3a → render budget **≤ 240 frames**. Light conditions: `L0 · L5 · L7` for `scene14` and
`L0 · L4 · L7` for `scene15`, matching each scene's existing corpus conditions exactly.

**Gates, in order (any failure = stop and record).**
1. **1-frame real-render smoke first** (WEEKEND_BRIEF §3-6, the 08-21 lesson).
2. **`ground_z` parity between arms**, `|Δground_z| ≤ 1e-6` per cut. This is the `sceneC2` failure
   mode from `DIAG_V1.md` §3.3 — if the hazard toggle moves the ground under the camera, the pairs
   are excluded or rescued only under the D20 0.15 m tolerance and the arms' inputs differ.
3. **Hazard-geometry invariance hash** on the ON arm against the frozen test render, so the probe is
   provably the same scene seen from new cameras.
4. Yield check: ≥ 5 accepted poses per arm, else report the empty cell as *unfillable* and stop
   (that is itself the answer — the geometry may not admit those viewpoints).

**Absolute-line compliance and how the output may be used.** `scene14` and `scene15` are **test**
scenes (WEEKEND_BRIEF §3-1). The probe **does not modify either scene** — it only adds camera poses
— and it is **evaluation-only, zero-shot, frozen checkpoints, no threshold or model selection may
touch it**. Its numbers go to a **diagnostic annex only** and must never enter the main table or the
τ decision. Isolated output path: `experiments/weekend_0823/a3_viewpoint/probe_render/`.
**Flagged for the orchestrator: confirm this reading of §3-1 before rendering.** A zero-risk
alternative that needs no test scene at all is in §8.

## 8. Zero-render extension proposed instead (EXT candidate, CPU, no GPU lock)

**Genealogy.** §2(a) of this file — "only 2 scenes carry test H frames" — plus WEEKEND_BRIEF §8.

The **train** split contains **81 H frames with band-3a GT across 3 further scenes** (`scene09` 30,
`scene12` 24, `scene17` 27) at `h ∈ [0.28, 1.76]`, `d ∈ [1.52, 7.64]`, **all with an off-arm twin
already rendered**. Running the frozen checkpoints over those 162 frames (CPU inference only, no
GPU, no re-training) would triple the occluder-mechanism coverage and fully cross the h × scene
design for band 3a — at zero render cost. **Caveat that must be stated on every number it produces:
these are training scenes, so the model has seen them; the result is an in-sample upper bound and a
*negative* control only.** Its discriminating power: if RGB's Δ_3a is ≈ 0 even on scenes it was
trained on, the 3a null is a property of occlusion-at-short-standoff and not of the test scenes —
which is the strongest available form of the §3 tier-control argument. (Val is useless here:
6 H frames, none with band-3a GT.) Not executed in this window; queued as an EXT proposal.

## 9. Files written by this track

| file | content |
|---|---|
| `experiments/weekend_0823/a3_viewpoint/a3_viewpoint.py` | the analysis (reads frozen artefacts, writes only into this directory) |
| `experiments/weekend_0823/a3_viewpoint/a3_viewpoint_numbers.json` | every number quoted above, incl. the 11- and 32-pose cluster tables |
| `experiments/weekend_0823/a3_viewpoint/a3_strata.csv` | per-pair dump, 9 runs × 96 H pairs, with cam `d`/`h`/`pitch`/`hfov`, bins, Δ_3a, Δ_3b, on/off max-p |
| `experiments/weekend_0823/a3_viewpoint/a3_viewpoint.png` | Δ by stratum (3a, 3b) + Δ_3a vs camera height scatter |
| `experiments/weekend_0823/a3_viewpoint/3A_VIEWPOINT_AUDIT.md` | this file |

**Reproduce.** `conda activate env_seg && PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="" python
experiments/weekend_0823/a3_viewpoint/a3_viewpoint.py` (~9 min, CPU).

## 10. Next actions

1. Put §6 안 A + §6.1 into `MORNING_REPORT_0824.md` 결재란 as the ruling #4 re-proposal, with 안 B
   attached and its rejection reason.
2. Patch `RESULTS_DRAFT.md` §N.1 with 안 A's English paragraph and add §6.1 to the limitations set
   (**pending 결재** — do not overwrite the existing §N.1 text until then).
3. GPU-5: run the §7 probe only if the queue is otherwise idle, and only after the §7 gate list is
   confirmed against WEEKEND_BRIEF §3-1.
4. Consider the §8 zero-render extension before the §7 probe — it is cheaper and touches no test scene.
