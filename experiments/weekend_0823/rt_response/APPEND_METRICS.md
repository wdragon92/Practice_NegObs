
---

## RED-TEAM RESPONSE 0823 (appended 2026-08-23 — D35)

Everything in this block is **new measurement on frozen artefacts**: no re-training, no re-render, no GPU, and **no number above this line is edited**.  Where a figure here contradicts one above, the correction is stated explicitly and the older text is left in place as the record.  Source scripts and full tables: `experiments/weekend_0823/rt_response/` (`code/*.py`, `F*.md`, `*.json`).  Consolidated finding→response→residual-risk ledger: `experiments/weekend_0823/redteam/REDTEAM_0823.md`.


### RT.1 FA-matched tier recall (R1-F1) — the H column of §4 is read at two different operating points

§4 prints RGB's H recall at an off-arm frame FA of 0.359 and Depth's at 0.042 in the same column — an 8.6× difference in false-alarm rate.  Sweeping τ per run so the off-arm FA hits a common target and reading tier recall there (`rt_response/code/f1_fa_matched.py`, τ from the empirical order statistics of the off-arm per-frame max probability, FA resolution 1/408 = 0.0025):

**H frame recall at matched off-arm FA, 3-seed mean ± half-range** (n = 96 H, 408 off)

| matched FA | RGB | Depth | B2 | Δ (Depth − RGB) |
|---|---|---|---|---|
| 0.359 | 0.729 ± 0.135 | **0.781 ± 0.078** | 0.399 ± 0.078 | +0.052 |
| 0.200 | 0.483 ± 0.172 | **0.562 ± 0.031** | 0.198 ± 0.141 | +0.080 |
| 0.100 | 0.326 ± 0.229 | **0.510 ± 0.078** | 0.097 ± 0.099 | +0.184 |
| 0.050 | 0.243 ± 0.208 | **0.479 ± 0.094** | 0.031 ± 0.036 | +0.236 |

Same sweep, V and E:

| matched FA | RGB V | Depth V | B2 V | RGB E | Depth E | B2 E |
|---|---|---|---|---|---|---|
| 0.359 | 0.809 | 0.994 | 0.800 | 0.570 | 0.733 | 0.193 |
| 0.200 | 0.669 | 0.983 | 0.746 | 0.296 | 0.600 | 0.126 |
| 0.100 | 0.530 | 0.956 | 0.646 | 0.081 | 0.600 | 0.089 |
| 0.050 | 0.443 | 0.939 | 0.552 | 0.015 | 0.600 | 0.022 |

**Reading.** Depth ≥ RGB at every matched point, and the gap widens as FA is tightened (+0.052 at FA 0.359 → +0.236 at FA 0.05).  The H-column ordering printed in §4 is an operating-point artefact, not an effect.  **What survives is the weaker and still useful claim: RGB is not zero** — 0.326 ± 0.229 at FA 0.10, against a twin-conditional adapter-free detector rate of 0.038 on the same tier (RT.3).  Per-seed τ and per-tier values: `rt_response/F1_FA_MATCHED.md`.  Full recall–FA curves for all three arms and all three seeds: `rt_response/figs/fig_f1_recall_vs_fa.png`.


### RT.2 Twin-conditional recall (R2 §4.3-F2) — separating conditional from unconditional firing

The twin is this corpus's intervention device; applying it to recall itself costs no extra render and no extra inference.  A hazard-ON frame is a **twin-conditional hit** iff `max_on_gt ≥ τ` **and** `max_off_gt < τ` on the pose-exact twin of the same cut (τ = 0.5, KEPT pairs, `rt_response/code/f2_twin_conditional.py`).


**H tier** (n = 96 kept pairs)

| model | recall as published | **twin-conditional recall** | off-arm twin fire rate | share of fires that are unconditional |
|---|---|---|---|---|
| rgb | 0.688 ± 0.141 | **0.375 ± 0.115** (0.229/0.438/0.458) | 0.330 | 0.447 |
| depth | 0.438 ± 0.031 | **0.438 ± 0.031** (0.406/0.469/0.438) | 0.000 | 0.000 |
| b2 | 0.229 ± 0.156 | **0.122 ± 0.068** (0.073/0.083/0.208) | 0.118 | 0.305 |

**E tier** (n = 45 kept pairs)

| model | recall as published | **twin-conditional recall** | off-arm twin fire rate | share of fires that are unconditional |
|---|---|---|---|---|
| rgb | 0.556 ± 0.378 | **0.207 ± 0.111** (0.222/0.311/0.089) | 0.370 | 0.572 |
| depth | 0.600 ± 0.000 | **0.600 ± 0.000** (0.600/0.600/0.600) | 0.000 | 0.000 |
| b2 | 0.178 ± 0.267 | **0.133 ± 0.200** (0.000/0.400/0.000) | 0.059 | 0.250 |

**V tier** (n = 165 kept pairs)

| model | recall as published | **twin-conditional recall** | off-arm twin fire rate | share of fires that are unconditional |
|---|---|---|---|---|
| rgb | 0.820 ± 0.136 | **0.440 ± 0.055** (0.479/0.370/0.473) | 0.382 | 0.446 |
| depth | 0.927 ± 0.036 | **0.873 ± 0.045** (0.891/0.909/0.818) | 0.055 | 0.059 |
| b2 | 0.711 ± 0.115 | **0.410 ± 0.073** (0.345/0.491/0.394) | 0.303 | 0.422 |

**Reading.** **Depth's H response is entirely hazard-conditional** — 0 of 96 pairs fire on the hazard-deleted twin, on all three seeds, so its twin-conditional recall equals its published recall exactly.  **RGB's does not**: 44.7 % of its H fires also fire when the hazard is gone, and its H recall falls 0.688 → 0.375.  The two arms were not counting the same thing.  Per-run and per-scene decomposition: `rt_response/F2_TWIN_CONDITIONAL.md`.


### RT.3 Adapter-free detector metric (R1-F3) — correcting the scope of the R.1 "constructive zero"

R.1 reads the YOLO row's E/H = 0.000 as a bound on *the detection paradigm*.  `METRICS_NOTES_yolo.md` §0 already says the opposite — *"every property of that adapter is a property of the adapter"* — and §3 proves it: the amodal GT boxes injected as conf-1.0 detections also score E = H = 0.000 **before any training**.  The bound as printed is therefore a bound on `det2cell`, not on detectors.

This section removes the adapter.  A hazard-ON frame is an **image-space hit** iff some stored detection (conf ≥ τ_conf) has IoU > t with some amodal GT box of that frame — no grid, no ground projection (`rt_response/code/f3_adapter_free_yolo.py`, 3 seeds).

| tier | n | any detection | **IoU > 0** | IoU > 0.1 | IoU > 0.3 | mean best IoU | mean largest GT box area |
|---|---|---|---|---|---|---|---|
| V | 180 | 0.393 ± 0.103 | **0.378 ± 0.086** | 0.356 | 0.317 | 0.239 | 0.434 |
| E | 45 | 0.259 ± 0.233 | **0.259 ± 0.233** | 0.259 | 0.259 | 0.182 | 0.585 |
| H | 96 | 0.167 ± 0.094 | **0.066 ± 0.036** | 0.052 | 0.031 | 0.016 | 0.193 |
| H_weak | 6 | 0.167 ± 0.250 | **0.167 ± 0.250** | 0.000 | 0.000 | 0.003 | 0.024 |
| none_in_fov | 81 | 0.214 ± 0.136 | **0.012 ± 0.012** | 0.008 | 0.000 | 0.002 | 0.145 |

τ_conf = 0.25, the adapter's operating point.  **The H rate is not zero.**  The bound is recovered only by adding the hazard-blind control: score the **off twin's** detections against the **on** frame's amodal GT boxes (same scene, same cut, same dressing, hazard geometry deleted).

| tier | n | on-arm IoU>0 | off-twin IoU>0 (hazard-blind) | on − off | **twin-conditional IoU>0** |
|---|---|---|---|---|---|
| *τ_conf = 0.25* | | | | | |
| V | 180 | 0.378 | 0.041 | +0.337 | **0.346 ± 0.064** |
| E | 45 | 0.259 | 0.148 | +0.111 | **0.170 ± 0.156** |
| H | 96 | 0.066 | 0.076 | -0.010 | **0.038 ± 0.010** |
| *τ_conf = 0.05* | | | | | |
| V | 180 | 0.615 | 0.156 | +0.459 | **0.487 ± 0.008** |
| E | 45 | 0.593 | 0.422 | +0.170 | **0.311 ± 0.022** |
| H | 96 | 0.302 | 0.233 | +0.069 | **0.142 ± 0.062** |

**Reading, and the sentence R.1 must be replaced by.** Two bounds apply to row 4 and they must not be conflated.  (i) *Our* ground-projection adapter cannot map a box to an E- or H-tier cell at all — the oracle-box diagnostic fixes that at 0.000 before training, so the published 0 is a property of the adapter.  (ii) With the adapter removed, the detector *does* place boxes near hidden hazards at a low rate (H 0.066 at IoU > 0), but the hazard-blind twin rate is 0.076, so the **twin-conditional rate is −0.010 — indistinguishable from zero — against +0.337 on the V tier**, where the same control shows the detector is strongly hazard-conditional.  At the storage floor τ_conf = 0.05 the H twin-conditional rate rises to 0.142 and must be reported alongside.

**One further honesty note.** This detector is not visibility-trained but **amodal-trained**: all 96 test H frames carry a non-empty GT box, and for a fully occluded hazard that box necessarily covers the occluder (in scene14 the plaza and the building facade — `METRICS_NOTES_yolo.md` §4).  Asking a detector to reproduce an image-undetermined target is itself a limitation of the baseline, and it is ours to state first.  Adapter ceiling for the V column, for the same reason: frame-det 0.404 / V 0.514 / cell recall 0.074.  Parameter counts are asymmetric too (yolov8n 3.2 M · ResNet34-U-Net 24.4 M · SegFormer-B2 ≈ 27 M).


### RT.4 `FA_in-scene` — the false-alarm tier that is in no denominator (R1-F4), and a correction to N.3 / R.3

`none_in_fov` is a hazard-ON frame whose hazard falls outside the grid (past 12 m or outside ±31.1°).  Its GT row is all-zero, so **every firing is a false positive** — yet it is in neither published denominator: not in recall (no GT-positive cell) and not in `frame_fa_off` (it is an on-arm frame).  **81 of the 816 test rows, 19.9 % of the 408 hazard-ON rows.**  τ = 0.5, `rt_response/code/f4_none_in_fov.py`.

| run | n | **`FA_in-scene`** | reported `frame_fa_off` | ratio | cells/frame | mean max p |
|---|---|---|---|---|---|---|
| rgb_s42 | 81 | **0.790** | 0.375 | ×2.1 | 4.22 | 0.758 |
| rgb_s43 | 81 | **0.963** | 0.478 | ×2.0 | 3.16 | 0.881 |
| rgb_s44 | 81 | **0.642** | 0.223 | ×2.9 | 1.86 | 0.627 |
| depth_s42 | 81 | **0.593** | 0.051 | ×11.5 | 4.89 | 0.561 |
| depth_s43 | 81 | **0.444** | 0.007 | ×60.4 | 4.04 | 0.409 |
| depth_s44 | 81 | **0.444** | 0.066 | ×6.7 | 4.41 | 0.483 |
| b2_s42 | 81 | **0.519** | 0.211 | ×2.5 | 1.74 | 0.546 |
| b2_s43 | 81 | **0.926** | 0.395 | ×2.3 | 7.17 | 0.839 |
| b2_s44 | 81 | **0.469** | 0.108 | ×4.4 | 1.51 | 0.472 |

3-seed mean: RGB **0.798 ± 0.160** vs reported 0.359 (×2.2) · Depth **0.494 ± 0.074** vs 0.042 (×11.9) · B2 **0.638 ± 0.228** vs 0.238 (×2.7).  By scene: scene07 n=51 · scene14 n=6 · sceneN3 n=24.

| run | scene07 | scene14 | sceneN3 |
|---|---|---|---|
| rgb_s42 | 0.725 | 0.500 | 1.000 |
| rgb_s43 | 1.000 | 1.000 | 0.875 |
| rgb_s44 | 0.608 | 0.500 | 0.750 |
| depth_s42 | 0.882 | 0.000 | 0.125 |
| depth_s43 | 0.706 | 0.000 | 0.000 |
| depth_s44 | 0.706 | 0.000 | 0.000 |
| b2_s42 | 0.608 | 0.000 | 0.458 |
| b2_s43 | 1.000 | 0.333 | 0.917 |
| b2_s44 | 0.588 | 0.500 | 0.208 |

**CORRECTION to R.3 (and to the N.3 reading of the null control).** R.3 records `sceneN3` as *"behaved as designed … the apparatus contributes no delta of its own"*, on the strength of a twin Δ of −0.001.  The Δ ≈ 0 statement is correct and the apparatus claim stands.  What the sentence does not say is **why** Δ is 0, and for the RGB arm the answer is not "both arms are quiet":

| run | sceneN3 on-arm fire rate | off-arm fire rate | on mean max p | on cells/frame |
|---|---|---|---|---|
| rgb_s42 | **1.000** | **1.000** | 0.946 | 6.83 |
| rgb_s43 | **0.875** | **0.708** | 0.745 | 1.88 |
| rgb_s44 | **0.750** | **0.708** | 0.738 | 3.21 |
| depth_s42 | **0.125** | **0.125** | 0.111 | 0.12 |
| depth_s43 | **0.000** | **0.000** | 0.002 | 0.00 |
| depth_s44 | **0.000** | **0.000** | 0.101 | 0.00 |
| b2_s42 | **0.458** | **0.375** | 0.468 | 1.58 |
| b2_s43 | **0.917** | **0.917** | 0.789 | 4.62 |
| b2_s44 | **0.208** | **0.208** | 0.230 | 0.88 |

`sceneN3` contains **no drop-off in either arm** (its hazard is a trompe-l'œil mural, 1–2 mm of paint on flat floor), so both arms are pure negatives.  **RGB fires on 0.75–1.00 of them at mean max p 0.74–0.95** — the null control did not pass, the RGB model failed it, and Δ ≈ 0 records saturation on both arms rather than silence on both.  **Depth is genuinely quiet there (0.000–0.125 on both arms), and B2 is mixed** (0.208–0.917), so the correction is arm-specific and must not be written as a blanket statement.  This belongs in the limitations section as the single clearest measurement of scene-level shortcut behaviour in the RGB arm, next to the C2 dressing decomposition (≈ 77 % dressing) already in R.3.


### RT.5 Scene-cluster bootstrap (R2 §4.2) — which confidence intervals survive

`code/bootstrap.py` handles pairing correctly (one shared resample index across both arms) but resamples **frames** i.i.d.  Test frames are clustered by scene: one scene contributes up to 72 frames that are the same geometry under different lighting and camera cuts.  Recomputed with `scene_id` as the resampling unit, 10 000 draws (`rt_response/code/f5_cluster_ci.py`; **the canonical `bootstrap.py` is not modified** — the cluster function exists only in that isolated script).

**Off-arm FA — 7 clusters, CI reportable:**

| run | FA | frame-i.i.d. 95 % CI | **scene-cluster 95 % CI** | width ratio |
|---|---|---|---|---|
| rgb_s42 | 0.375 | [0.328, 0.422] | **[0.162, 0.647]** | **×5.2** |
| rgb_s43 | 0.478 | [0.430, 0.527] | **[0.284, 0.643]** | **×3.7** |
| rgb_s44 | 0.223 | [0.183, 0.263] | **[0.061, 0.458]** | **×5.0** |
| depth_s42 | 0.051 | [0.031, 0.074] | **[0.012, 0.125]** | **×2.6** |
| depth_s43 | 0.007 | [0.000, 0.017] | **[0.000, 0.029]** | **×1.7** |
| depth_s44 | 0.066 | [0.043, 0.092] | **[0.006, 0.158]** | **×3.2** |
| b2_s42 | 0.211 | [0.172, 0.251] | **[0.064, 0.380]** | **×4.0** |
| b2_s43 | 0.395 | [0.348, 0.442] | **[0.172, 0.699]** | **×5.6** |
| b2_s44 | 0.108 | [0.079, 0.139] | **[0.011, 0.261]** | **×4.2** |

**H and E — the CI is withdrawn, not widened.**  test H spans **2** scene clusters (scene14 60, scene15 36); test E spans **1** (scene18 45).  With 2 clusters the bootstrap can draw only 3 distinct multisets, so any interval it returns is an artefact of that enumeration.  Per §5.2/§5.3 of the draft, the replacement is the per-scene value printed beside the **same scene's** off-arm FA:

| run | H recall (pooled) | scene14 recall (n=60) | scene14 off-FA | scene15 recall (n=36) | scene15 off-FA |
|---|---|---|---|---|---|
| rgb_s42 | 0.594 | 0.467 | 0.181 | 0.806 | 0.889 |
| rgb_s43 | 0.875 | 0.983 | 0.542 | 0.694 | 0.500 |
| rgb_s44 | 0.594 | 0.667 | 0.083 | 0.472 | 0.708 |
| depth_s42 | 0.406 | 0.650 | 0.000 | 0.000 | 0.083 |
| depth_s43 | 0.469 | 0.650 | 0.000 | 0.167 | 0.000 |
| depth_s44 | 0.438 | 0.700 | 0.000 | 0.000 | 0.208 |
| b2_s42 | 0.083 | 0.133 | 0.125 | 0.000 | 0.014 |
| b2_s43 | 0.396 | 0.100 | 0.069 | 0.889 | 0.986 |
| b2_s44 | 0.208 | 0.333 | 0.000 | 0.000 | 0.014 |

On `scene15` two of three RGB seeds fire on **more** hazard-free frames of that scene than they detect hidden drops in it (0.806 vs 0.889 · 0.472 vs 0.708), and `b2_s43` is 0.889 vs 0.986.  scene15 supplies 37.5 % of the H denominator and close to no discriminative evidence; scene14 carries the effect for both arms.


**CORRECTION to `runs/v2/SEED_TABLE.md` §5.1/§5.2 (auxiliary pixel-loss ablation).** Same 816 rows, paired aux − base on rgb seed 42, one resample draw shared by both arms:

| metric | Δ | frame-i.i.d. 95 % CI | scene-cluster 95 % CI | verdict |
|---|---|---|---|---|
| cell_f1 | +0.0403 | [0.0001, 0.0786] | [-0.2580, 0.2054] | **significance does not survive clustering** |
| cell_precision | +0.1291 | [0.0885, 0.1690] | [-0.1620, 0.2458] | **significance does not survive clustering** |
| cell_recall_H | +0.3546 | [0.2768, 0.4302] | [-0.1429, 0.4625] | **significance does not survive clustering** |
| frame_det_rate | -0.1682 | [-0.2296, -0.1064] | [-0.4818, 0.1594] | **significance does not survive clustering** |
| frame_recall_H | +0.1250 | [-0.0096, 0.2526] | [-0.4167, 0.4500] | was not significant either way |
| frame_fa_off | -0.2083 | [-0.2531, -0.1646] | [-0.3627, -0.0613] | survives |
| cell_fpr_off | -0.0297 | [-0.0372, -0.0222] | [-0.0650, -0.0048] | survives |
| frame_recall_V | -0.1889 | [-0.2551, -0.1257] | [-0.4444, -0.0290] | survives |
| frame_recall_E | -0.6000 | [-0.7436, -0.4528] | [-0.6000, -0.6000] | **degenerate** — support is 1 scene (scene18); report no CI |
| cell_recall_E | -0.3592 | [-0.4556, -0.2626] | [-0.3592, -0.3592] | **degenerate** — support is 1 scene (scene18); report no CI |

Two consequences.  (a) The `cell_f1 +0.0403 [0.0001, 0.0786] yes (barely)` row must have its significance claim withdrawn — under scene resampling it is [-0.2580, 0.2054].  (b) **More seriously**, §5.2 calls `cell_recall_H` **+0.3546** *"the single largest confirmed effect in the table, and the one that matters for this paper's thesis"*; under scene resampling that interval is [-0.1429, 0.4625] and **includes zero**.  The frame-level interval was measuring within-scene variation across the same two H scenes.  That sentence needs the same withdrawal, and it is the more consequential of the two.


### RT.6 strict-H twin pixel-difference audit (R1-F7) — what remains visible when the hazard contributes zero pixels

strict-H is a **geometric** predicate: `int_px == 0 ∧ edge_vis == 0`, i.e. the hazard prism re-projects to zero pixels.  It does not forbid the hazard from changing the image through shadow, ambient occlusion, GI bounce or mesh seams.  All 96 test H twin pairs were re-read at native 1920×1080 and differenced, `d = max_c |on_c − off_c|` (`rt_response/code/f7_hpair_pixdiff.py`; all 96 verified pose-exact to 1e-6, consistent with N.1's H 96 EXACT / 0 TOL / 0 EXCL).

**Calibration first.** `sceneN3`'s `keep_dressing` off arm is geometrically identical to its on arm (R.3: heightmap `max |Δ| = 0.000000 m`), so its render-to-render difference is pure path-tracer / denoiser nondeterminism:

| reference pair | n | median px ≥ 2/255 | median px ≥ 8/255 | **median px ≥ 32/255** | median magnitude over changed px |
|---|---|---|---|---|---|
| renderer noise floor (N3, identical geometry) | 24 | 916,841 (**44.2 % of frame**) | 27571 | **50** | 3.19 |
| hazard-only (C2 `keep_dressing`, drop deleted, dressing kept) | 24 | 1,270,241 | 875,005 | 698,078 | 61.87 |

A 2/255 threshold flips 44 % of the frame on two renders of the *same* geometry, so ≥ 32/255 is the level that carries scene content (floor: 50 px of 2 073 600).

| set | n | pairs with zero difference | median px ≥ 32/255 | min | % of frame | × noise floor |
|---|---|---|---|---|---|---|
| all test strict-H | 96 | **0** | 93,606 | 2,211 | 4.51 % | ×1872 |
| scene14 | 60 | **0** | 156,977 | 42,797 | 7.57 % | ×3140 |
| scene15 | 36 | **0** | 7,106 | 2,211 | 0.34 % | ×142 |

**strict-H is never optically empty in this corpus.**  0 of 96 pairs are identical and the quietest still carries 2,211 pixels at ≥ 32/255, 44× the noise floor.  The zero-difference consistency gate has no pair to run on.  81.2 % of the residual falls inside the amodal hazard silhouette (the prism projected ignoring occlusion) and 44.5 % inside the GT-positive wedges — but note that for a fully occluded hazard the amodal silhouette necessarily covers the occluder too, so containment means *co-located with the hazard's line of sight*, not *the hazard's own pixels*.

**The scene split matches the twin-Δ split exactly.**  scene14's residual is 22.1× larger in count and 7.6× larger in per-pixel magnitude than scene15's; scene15's mean magnitude over changed pixels (4.78) is only 1.5× the renderer noise floor (3.19).  That is the same 60/36 split that carries the H twin Δ (scene14 rgb .278/.448/.558, depth .577–.645; scene15 rgb −.010/.209/−.058).  **Two independent measurements — model response and raw pixels — pick out the same scene.**

**Does the residual grade the response?**  Spearman ρ between log10(residual px ≥ 32/255) and that pair's `delta_score` is positive in all nine runs (0.27–0.83 pooled).  Within scene, **Depth is positive in all six cells (0.08–0.69) and its scene14 quiet→loud residual tercile moves Δ from 0.34–0.40 to 0.83–0.93; RGB is inconsistent** (−0.13 to +0.39).  The residual optical evidence is what the Depth arm tracks; the RGB arm's H response is not graded by how much is visible — the same diagnosis RT.2 reaches from the twin-conditional side.

**Scope limit this imposes on every twin Δ in this document (R1-F12).**  The toggle is `SCENE_CONFIG['hazard_stairs']`.  In `scene14` that branch builds the shoulder massif, the side slopes, the stair, the step coursing, the parapets, the cues **and** the autumn litter, and `False` replaces all of it with a flat fill (`scenes/main/scene14_grandstair_illusion.py:1885-1898`); in `scene15` it removes the stair and the bend and extends the alley flat (`scenes/main/scene15_alley_labyrinth.py:2301-2304`).  Every Δ is therefore a sensitivity to {the drop's indirect optics} ∪ {every object inside that branch}, not to the drop geometry alone.  Figures: `rt_response/panels/h_diff_contact_sheet.png` (six pairs = min/median/max residual within each scene, selection rule fixed before inspection).


### RT.7 Document corrections (R3 §1.4, §1.5) — append-only, nothing above is edited

**(a) §2.4 τ_edge is printed as 0.02; the value used everywhere is 0.05.**  `code/labeling/labeler.py` has `TAU_INT_DEF, TAU_EDGE_DEF = 50, 0.05`, and `dataset_manifest_v2_full.json` `meta.tau_strict` is `{tau_int: 50, tau_edge: 0.05}`.  **No number changes** — see (b) for why.

**(b) The τ_edge sensitivity argument in §2.4 is vacuous as written, and the honest version is stronger.**  "strict-H is τ-insensitive: 45 frames at all 9 combinations" is true but tautological: `labeler.tier_of` defines H as `int_px == 0 and edge_vis == 0`, a predicate neither threshold enters, so no sweep could have moved it.  What the data actually shows is that **τ_edge is unconstrained by this corpus**: `edge_ratio` is bimodal — exactly 0 or ≥ 0.44 (v1 n = 93: 57 zeros, 36 non-zero with min 0.505; v2_full n = 345: 273 zeros, 72 non-zero with min 0.44), and the swept grid {0.02, 0.05, 0.10} lies entirely inside an interval containing no data.  Replacement sentence: *"Lip visibility is effectively binary in this corpus (edge_ratio = 0 or ≥ 0.44), so the E/H boundary is independent of τ_edge; 0.05 is an arbitrary representative of the empty interval (0, 0.44) and there is nothing to tune.  τ_int = 50 px is the threshold that does move results — it defines the V/H_weak boundary and shifts corpus V 726 → 657 and H_weak 0 → 57 across a 1 → 200 sweep — while headline strict-H is invariant to both by definition."*

**(c) `dayrun_0820/SPLIT_PROPOSAL_v2_full.md` — the `frames` column is not the split size.**  That column holds the `V+E+H+off` subtotal, which omits `H_weak` and `none_in_fov`.  Recomputed directly from `dataset_manifest_v2_full.json` + `split_v2_full.json`:

| split | V | E | H | H_weak | none_in_fov | off | **true frames** | doc's `frames` |
|---|---|---|---|---|---|---|---|---|
| train | 438 | 21 | 141 | 21 | 147 | 768 | **1536** | 1368 |
| val | 75 | 6 | 6 | 3 | 54 | 144 | **288** | 231 |
| test | 180 | 45 | 96 | 6 | 81 | 408 | **816** | 729 |
| hold | 0 | 0 | 0 | 0 | 96 | 96 | **192** | 192 |
| **non-hold total** | 693 | 72 | 243 | 30 | 282 | 1320 | **2640** | 2328 |

The same document's `PROOF-4` states *"every non-held frame resolves to exactly one split: 0 bad of **2640**"*, so the file asserts both 2640 and 2328; the difference 312 = H_weak 30 + none_in_fov 282.  §N of this file already writes `test 816 = 408 on + 408 off` correctly.  Fix: rename the column `V+E+H+off` and add the two missing tier columns.  This is exactly the frame-count audit trap §12.3-⑥ predicted a reviewer would spring.


### RT.8 What this block does **not** close

| # | open item | why it cannot close in this window |
|---|---|---|
| RR1 | test strict-H rests on **2 scenes, 1 of which carries the effect** | test set is frozen; no new test scene can be rendered.  The response is claim scope, not data |
| RR2 | `SEED_TABLE` §5.2's `cell_recall_H` significance claim | needs an edit to that file (append-only rule) — flagged in RT.5, sign-off item |
| RR3 | decomposing the strict-H residual into shadow vs co-removed structure | needs the CUE-OFF render arm with a placebo arm (D35) |
| RR4 | monocular-depth baseline (R1-F9) | not run; limitations sentence is the minimum response |
| RR5 | related-work paragraph on amodal completion / BEV layout hallucination (R1-F5) | writing task, GPU 0 |
| RR6 | no experiment treats a cue as a manipulated variable (R1-F6) | needs the B1 cue-OFF render |
