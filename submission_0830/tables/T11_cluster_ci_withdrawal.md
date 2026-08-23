# T11 · Scene-cluster bootstrap — which confidence intervals survive

<!-- LEDGER: experiments/mainrun_0819/METRICS.md:1150-1200 (§RT.5) -->
<!-- LEDGER: experiments/weekend_0823/rt_response/F5_CLUSTER_CI.md -->
<!-- LEDGER: experiments/dayrun_0820/runs/v2/SEED_TABLE.md:125,132,162-165 (withdrawal footnote) -->
<!-- Script: rt_response/code/f5_cluster_ci.py — the canonical code/bootstrap.py is NOT modified -->

- **Corrected-GT status**: **unaffected.** These are resampling-unit results on the frozen 816-row
  test set; the corrected GT does not change cluster structure (7 scene clusters; H = 2, E = 1).
- **Provenance**: `experiments/mainrun_0819/METRICS.md` §RT.5 · `rt_response/F5_CLUSTER_CI.md`
- **Method**: `code/bootstrap.py` pairs correctly but resamples **frames** i.i.d. Test frames are
  clustered by scene — one scene contributes up to 72 frames that are the same geometry under
  different lighting and camera cuts. Recomputed with `scene_id` as the resampling unit, 10,000 draws.

---

## 1. Off-arm FA — 7 clusters, CI **is** reportable (but 1.7–5.6× wider)

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

## 2. H and E — the CI is **WITHDRAWN, not widened**

test H spans **2** scene clusters (scene14 n = 60, scene15 n = 36); test E spans **1** (scene18
n = 45). With 2 clusters the bootstrap can draw only **3 distinct multisets**, so any interval it
returns is an artefact of that enumeration. **The replacement is the per-scene value printed beside
that same scene's off-arm FA.**

| run | H recall (pooled) | scene14 recall (n=60) | scene14 off-FA | scene15 recall (n=36) | scene15 off-FA |
|---|---|---|---|---|---|
| rgb_s42 | 0.594 | 0.467 | 0.181 | 0.806 | **0.889** |
| rgb_s43 | 0.875 | 0.983 | 0.542 | 0.694 | 0.500 |
| rgb_s44 | 0.594 | 0.667 | 0.083 | 0.472 | **0.708** |
| depth_s42 | 0.406 | 0.650 | 0.000 | 0.000 | 0.083 |
| depth_s43 | 0.469 | 0.650 | 0.000 | 0.167 | 0.000 |
| depth_s44 | 0.438 | 0.700 | 0.000 | 0.000 | 0.208 |
| b2_s42 | 0.083 | 0.133 | 0.125 | 0.000 | 0.014 |
| b2_s43 | 0.396 | 0.100 | 0.069 | 0.889 | **0.986** |
| b2_s44 | 0.208 | 0.333 | 0.000 | 0.000 | 0.014 |

> On **scene15**, two of three RGB seeds fire on **more** hazard-free frames of that scene than they
> detect hidden drops in it (0.806 vs 0.889 · 0.472 vs 0.708), and b2_s43 is 0.889 vs 0.986.
> scene15 supplies **37.5 %** of the H denominator and close to no discriminative evidence;
> **scene14 carries the effect for both arms.**

## 3. Correction to `SEED_TABLE.md` §5.1/§5.2 (aux ablation, rgb seed 42, appendix row)

| metric | Δ | frame-i.i.d. 95 % CI | scene-cluster 95 % CI | verdict |
|---|---|---|---|---|
| cell_f1 | +0.0403 | [0.0001, 0.0786] | [−0.2580, 0.2054] | **significance does not survive clustering** |
| cell_precision | +0.1291 | [0.0885, 0.1690] | [−0.1620, 0.2458] | **significance does not survive clustering** |
| **cell_recall_H** | **+0.3546** | [0.2768, 0.4302] | **[−0.1429, 0.4625]** | **significance does not survive clustering** |
| frame_det_rate | −0.1682 | [−0.2296, −0.1064] | [−0.4818, 0.1594] | **significance does not survive clustering** |
| frame_recall_H | +0.1250 | [−0.0096, 0.2526] | [−0.4167, 0.4500] | was not significant either way |
| frame_fa_off | −0.2083 | [−0.2531, −0.1646] | [−0.3627, −0.0613] | **survives** |
| cell_fpr_off | −0.0297 | [−0.0372, −0.0222] | [−0.0650, −0.0048] | **survives** |
| frame_recall_V | −0.1889 | [−0.2551, −0.1257] | [−0.4444, −0.0290] | **survives** |
| frame_recall_E | −0.6000 | [−0.7436, −0.4528] | [−0.6000, −0.6000] | **degenerate** — support is 1 scene (scene18); report no CI |
| cell_recall_E | −0.3592 | [−0.4556, −0.2626] | [−0.3592, −0.3592] | **degenerate** — support is 1 scene (scene18); report no CI |

---

## CAVEAT LINE — must travel with this table

> **Two published significance claims are withdrawn.** (a) `cell_f1` +0.0403 [0.0001, 0.0786] becomes
> [−0.258, 0.205]. (b) — the more consequential — `cell_recall_H` **+0.3546**, described in
> `SEED_TABLE.md` §5.2 as *"the single largest confirmed effect in the table, and the one that
> matters for this paper's thesis"*, becomes **[−0.1429, 0.4625]** and **includes zero**. Both
> frame-level intervals were measuring variation *within the same two H scenes*. **The precision and
> false-alarm family survives.**

> **The old "9/9 CIs exclude zero" framing is dead.** `PROJECT_STATE_0823.md` §5.2 is superseded by
> `PROJECT_STATE_0823_v2.md` §1-3: H and E CIs are **withdrawn (not narrowed)**, and the aux
> "significant gain" claim is withdrawn with them.

> **σ convention change ahead.** `mean ± range/2` (n = 3) under-estimates σ by ~15 %
> (E[range] = 1.693σ). v3 pre-registration standardises on **sample sd, ddof = 1**
> (`ACCOUNTING.md` §4.9-1). If the paper reports both v2 and v3 spreads, say which estimator each uses.

> **Never cite an H_weak σ.** In the corrected-GT rescore its σ is **0 (degenerate)** and citation is
> explicitly forbidden (D59 ②).
