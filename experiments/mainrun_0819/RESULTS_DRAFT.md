# Results (draft) — night-1 provisional results pending grid confirmation

> **Status of this section.** These are *night-1 provisional results pending grid confirmation.*
> The 15-cell polar output grid was **declared** by this run, not recovered from code (no such
> construct exists in the repository); labels are **derived** from a twin height-map difference,
> not authored; and the train/val/test split is **provisional**. Nothing here is a final number.
> Regenerating every table after the grid is confirmed costs ~40 min and reuses the renders.

## 5.1 Setup

We render 33 synthetic scenes × 3 daylight conditions × 8 sampled cameras × 2 hazard arms
(hazard **on** / **off**, identical camera-pose seed), giving 1584 frames. The hazard-off arm is a
counterfactual twin: same pose, same light, same dressing, hazard geometry removed. Four scenes are
held out of every split for label-integrity reasons (§5.6), leaving 29 scenes / 1392 frames, split
scene-wise into 20 train / 2 val / 7 test. Each frame is labelled on a polar grid of 5 azimuth
sectors × 3 distance bands ([0,2), [2,5), [5,12) m); a cell is positive when a ≥0.30 m drop
footprint falls inside its wedge. Frames are stratified by an evidence tier — **V** (drop interior
visible), **E** (only the rim visible), **H** (hazard contributes no visible pixels; *strict* by
construction and stable across all nine (τ_int, τ_edge) settings). Test carries 111 V / 9 E / 21 H
hazard-on frames plus 168 hazard-off frames, 981 positive cells.

Both models are ResNet-34 U-Net encoders with a 15-way pooled classification head (24.4 M params,
512², LR 3e-4, early stopping on val cell-F1). The RGB arm sees colour only; the Depth arm sees the
simulator's clean `distance_to_image_plane` channel. All intervals are 95 % percentile bootstrap,
10 000 resamples, seed 42, resampling frames (paired comparisons resample pairs).

## 5.2 Main table

Operating threshold τ = 0.5. Recall is frame-level (a frame counts as detected when any
GT-positive cell fires); FA is the fraction of hazard-**off** frames firing any cell.

| model | V recall | E recall | H recall | FA (off) ↓ | cell F1 |
|---|---|---|---|---|---|
| RGB U-Net (s42) | 0.667 [0.577, 0.755] | 0.444 [0.111, 0.800] | 0.333 [0.133, 0.545] | 0.274 [0.207, 0.344] | 0.442 [0.380, 0.501] |
| Depth U-Net (s42) | 0.919 [0.865, 0.966] | 0.333 [0.000, 0.667] | 0.714 [0.500, 0.900] | 0.161 [0.107, 0.220] | 0.689 [0.654, 0.721] |
| RGB U-Net (s43) | 0.721 | 0.000 | 0.048 | 0.143 | 0.488 |
| SegFormer-B2 | *tomorrow — code dry-run GREEN, untrained* | | | | |
| — n frames | 111 | 9 | 21 | 168 | 981 cells |

Seed variance (s42 vs s43, same split/config): V is stable (0.667/0.721) but the sparse tiers swing
hard — H 0.333 ↔ 0.048, E 0.444 ↔ 0.000 — at near-identical val F1. Val carries zero H frames by
design (D18), so checkpoint selection cannot see H performance; the RGB row therefore must be
reported as a multi-seed range (or with an H-aware selection protocol) in the final table. The
RGB−Depth gap direction survives both seeds; its magnitude on H does not have a stable RGB point
estimate yet.

Paired over the same 336 test frames, Depth beats RGB on cell F1 by 0.248 [0.190, 0.308] and on
frame-level H recall by 0.381 [0.053, 0.688], while RGB false-alarms more on the off arm by
0.113 [0.041, 0.188] — all three intervals exclude zero. The E tier is the one place RGB is
nominally ahead (+0.111), but with 9 frames its paired interval [0.000, 0.375] includes zero and we
make no claim there. Cell-level H recall (Δ = −0.267 [−0.600, 0.084]) also fails to clear zero,
i.e. the H-tier advantage is established at the frame level and not yet at the cell level.

Threshold behaviour differs by modality: val-fitted thresholds are τ* = 0.36 for RGB (recall up,
FA up to 0.339) and τ* = 0.70 for Depth (precision 0.839, but cell F1 *falls* to 0.583). Because
the 2-scene validation set contains no H frames, we report τ = 0.5 as the headline for both arms
and treat τ* as diagnostic.

## 5.3 Twin-paired analysis: the model uses context, not hazard pixels

The hazard-off arm lets us ask a causal question directly: holding pose, light and dressing fixed,
how much of the model's hazard probability is *caused* by the hazard geometry? For each pose-matched
pair we take Δ = max probability over the frame's GT-positive cells (on arm) − the same cells (off
arm). Of 168 test pairs, 117 are pose-matched; the 51 exclusions are all `ground_z` mismatches
introduced when the sampler re-draws a rejected camera on the modified geometry, and they remove
scene C2 entirely and 21 of 24 scene07 pairs. Across the 117 kept pairs Δ is
**0.348 [0.286, 0.410]** for RGB and **0.561 [0.497, 0.623]** for Depth, positive on 88/93 and
90/93 of the GT-carrying pairs respectively.

The tier breakdown is the result that matters. On **H** frames — where the hazard contributes no
visible pixels at all — removing the hazard still lowers the RGB model's probability by
**0.240 [0.156, 0.331]**. Since no hazard pixel exists in either image of an H pair, the model's
response must be driven by the surrounding context (railing terminations, path truncation, the
change in what the far ground plane does), which is exactly the mechanism this work sets out to
demonstrate. The corresponding Depth value is 0.584 [0.448, 0.714]. One caution: on the
hard-negative scene N3, which has no hazard in either arm, the RGB model's frame-level Δ is still
0.252 while Depth's is 0.000 — the RGB arm is partly responding to the *dressing* that the toggle
removes, and a dressing-invariant control is needed before the causal claim is tightened.

## 5.4 Distance bands: everything is a far-field result

| band | GT cells | RGB recall | Depth recall |
|---|---|---|---|
| 1 near [0, 2) m | 117 | 0.000 [0.000, 0.000] | 0.051 [0.018, 0.089] |
| 2 mid [2, 5) m | 276 | 0.290 [0.198, 0.386] | 0.620 [0.530, 0.707] |
| 3 far [5, 12) m | 588 | 0.583 [0.501, 0.665] | 0.735 [0.675, 0.791] |

Both arms improve monotonically with distance and the near band is unsolved. This is not only a
model property: our own label-side diagnostic (fraction of GT-positive cells that hold at least one
re-projected below-ground pixel) reads 0.029 / 0.475 / 0.715 across the three bands. A drop's floor
immediately behind its lip lies in the camera's view shadow at eye height with a −20…−2° pitch, so
near-band cells are positive by construction with nothing observable in them. Near-band numbers
should be read as a statement about the sensing geometry, not about the network; whether band 1
belongs in the headline metric at all is an open question for the label review.

## 5.5 Qualitative

Twelve panels (RGB frame + GT grid + predicted-probability grid) are in `viz/`. The successful H
detections are uniformly **far-band anticipation**: on scene14, whose drop hides behind a
flat-continuous illusion, the model lights the entire band-3 row at up to p = 0.821. The failures
are cue-poor: the scene15 alley frame carries one GT cell and receives p = 0.093 — the model is not
hedging, it sees nothing. All four selected off-arm false alarms come from a single scene (C2) and
fire at p ≈ 0.98 across 5–8 cells, i.e. the RGB FA rate is concentrated, not diffuse.

## 5.6 Threats to validity

1. **Provisional grid.** The 5×3 polar grid, its azimuth span (±31.1°) and its band edges were
   declared by this run. No grid definition exists in the codebase; the nearest match is a camera
   openness ray-fan. Every number is conditional on those constants surviving review.
2. **Derived labels.** GT is the difference of two AABB/depth-fusion height maps plus a
   near-boundary step gate, not authored ground truth. A step gate withholds 87 positive cells over
   33 frames (39 of them in the test split); the pre-gate labels are preserved, so the decision is
   reversible, but the headline moves if it is reversed. The overall gate report ends in FAILURE
   (one scene legitimately all-negative; the below-ground-visibility target unmet in the near band).
3. **Tier instrument is a substitute.** V/E/H come from depth re-projection, not from the
   semantic-ID instrument the protocol specifies (it does not exist in the repo). Strict-H is
   insensitive to both thresholds across nine settings; the V/E boundary is not (V 417–453).
   Transparent occluders cannot be detected at all, so three scenes need a human check before H
   membership is final.
4. **Simulation only.** All frames are rendered. No real-world evaluation exists yet, and the
   real-shoot protocol asks for camera pitch (−15…+5°) and height (1.5–1.8 m) bands that the
   simulator's sampler never produces (−20…−2°, 0.25–1.90 m, capped at 1.20 m on four scenes).
5. **Clean depth.** The Depth arm reads a noise-free simulated range channel. Its H-tier advantage
   plausibly comes from a "missing floor band" geometric signature that a real stereo or
   time-of-flight sensor — noisy and drop-out-prone at 5–12 m — would carry far more weakly. It
   should be read as what an idealized range sensor can extract, not as a deployable baseline, and
   not as a general geometry upper bound (that reading is scoped to the V tier).
6. **RGB convergence flag.** The RGB run's val F1 peaks at epoch 1 (0.299) and decays while train
   loss falls by an order of magnitude, on a 2-scene / 96-frame / H-free validation set. Either the
   RGB arm learns little past epoch 1, or checkpoint selection was too noisy to rank epochs. RGB
   numbers are therefore a **lower bound**, and the RGB−Depth gap an **upper bound**.
7. **Small H test stratum.** 21 strict-H frames / 90 cells in test. This is why the H intervals are
   wide enough to swallow effects of ±0.3, and why the frame- and cell-level H comparisons disagree.
   A prepared +8-camera re-render of the two test H scenes would roughly double the stratum.
8. **Four held scenes.** `sceneD4` (indoor, dark exposure and roof-blinded height map) and
   `scene11 / scene13 / scene19` (hazard toggle also moves the camera's own ground, or the near
   boundary falls outside depth-fusion coverage) are excluded from every split. Their exclusion
   protects the metric but leaves four hazard types unrepresented in the test set.
9. **Twin pairing is incomplete.** 51 of 168 test pairs (and 183 of 792 corpus-wide) fail the pose
   match on `ground_z`. Scene C2 — the dominant false-alarm scene — contributes zero pairs, so the
   causal analysis and the FA analysis do not cover the same scenes.

---

## Night 0820→0821 update

*Appended 2026-08-21 by the NIGHTRUN 0820 cycle (`Docs/experiment/OVERNIGHT_BRIEF_0820_v1.md`, D1).
**Nothing above this line was modified.** Everything here is CPU re-analysis of the frozen recipe-v2
artefacts under `experiments/dayrun_0820/runs/v2/` (grid `PROVISIONAL-GRID-V1`, 20 cells,
τ_op = 0.5, seeds 42/43/44); the GPU tracks (YOLO s43/44, aux, the C2 control round, the hole probe)
did not run — the GPU was held by another process all night — so the four-row main table is
unchanged. Sources: `nightrun_0820/narrative/diag_v2/DIAG_V2.md`, `TWIN_STRATIFICATION.md`,
`STRADDLE_REPORT.md`, `tau_curves/TAU_CURVES.md`.*

### N.1 Correction to §5.3 — the H-tier claim is a **band-3b** claim

The 8 m band split (v2) makes the far row decomposable for the first time, and the H-tier twin Δ is
**not** uniform across it. On the 96 H-tier pose-matched pairs, RGB's Δ is **+0.293 ± 0.087** in
band 3b `[8,12)` m (s42 point 0.185, 95 % CI [0.138, 0.233], clear of zero) but **−0.031 ± 0.054**
in band 3a `[5,8)` m (s42 −0.049, CI [−0.127, **+0.017**], **containing zero**); on s42 the off arm's
mean probability over those 3a cells is in fact *higher* than the on arm's (0.292 vs 0.243), and only
55 % of the 33 pairs have Δ > 0. Depth is positive in both bands (3a +0.534, 3b +0.411, both CIs
clear of zero) and B2 only in 3b (+0.112 vs +0.058 with a CI containing zero).

**Wording to adopt.** The sentence "removing the hazard still lowers the RGB model's probability on
H frames" must be qualified as *far-band*: RGB's context response to a hazard it cannot see is
demonstrated for band 3b and **is not demonstrated for band 3a**, where its H-tier firing is
consistent with the standing prior rather than with the hazard. Do not state the H result for the
H tier as a whole in the RGB row.

### N.2 New footnote to the twin table — the pairing tolerance does not inflate the headline

D20 rescued 54 test twin pairs under a `|Δground_z| ≤ 0.15 m` tolerance, so those pairs' two arms
differ slightly in input. Re-stratifying (pose audit: `ground_z` is the *only* key that ever differs;
EXACT = all five pose keys equal to 1e-6, n = 312; TOL = the tolerance layer, n = 54):

> **Footnote (draft).** Recomputed on the 312 pairs whose camera pose matches to 1e-6 on all five
> keys, the H-tier twin Δ is **rgb 0.285 / depth 0.407 / b2 0.110** — identical to the published
> values to four decimals, because **none of the 54 tolerance-rescued pairs is H tier** (they are 33
> V and 21 H_weak/none). All nine runs' EXACT-only 95 % CIs exclude zero. The D20 tolerance enlarges
> the V-tier sample; it is not a premise of the H-tier causal claim.

The all-tier Δ is a different matter and needs its own caveat: the published kept-pair value sits
**+0.041 (rgb) / +0.001 (depth) / +0.037 (b2)** above the EXACT-only value, because the TOL layer
concentrates in `scene07` (24 pairs) and `sceneC2` (24 pairs) whose Δ are unusually large (0.740 and
0.688 against 0.26–0.28 in the EXACT layer). `sceneC2`'s off arm is the non-appearance-preserving
toggle, so part of that Δ is "the dressing went away", not "the drop went away". Quote the all-tier
Δ with this caveat, or quote the EXACT-only value.

### N.3 New paragraph for §5.2 — why τ_op = 0.5 is the reported operating point

A full τ sweep (0.05–0.95, three seeds, three models, frozen probability dumps) shows the
(H recall − FA) trade-off is **flat where it matters**: over τ ∈ [0.30, 0.70] its amplitude is 0.095
for RGB, 0.026 for Depth and 0.013 for B2. Moving RGB to the sweep's argmax (τ = 0.35) buys
**0.016** — and that argmax is (i) an artefact of averaging, since the per-seed optima are 0.30 /
0.95 / 0.15, and (ii) fitted **on test**, which this project's protocol forbids (τ* is always fitted
on val). τ = 0.5 is a pre-registered, model-neutral threshold that keeps the four rows comparable.
Two facts belong beside it: Depth's logits are near-saturated, so its curve is essentially flat over
τ ∈ [0.2, 0.7] and its low H recall is a model property, not a threshold choice (H recall 0.667 at
τ = 0.15 against 0.438 at 0.5, but FA rises 0.042 → 0.184); and **B2 never exceeds H − FA = +0.033
at any threshold**, so its absence of H-tier performance is not a thresholding problem.

### N.4 Correction to §5.5 and to the FA narrative — the false alarms moved

§5.5's "all four selected off-arm false alarms come from a single scene (C2), i.e. the RGB FA rate is
concentrated, not diffuse" **does not reproduce at v2**, and its replacement runs the other way:

| RGB off-arm false alarms | v1 (s42, 168 off frames) | v2 (3-seed mean, 408 off frames) |
|---|---|---|
| `sceneC2` frame FA | **0.875** (21/24) | **0.069** — and exactly 0.000 on two of three seeds |
| `sceneC2` share of all cell fires | 47.8 % | **0.5 %** |
| top-2 scene concentration | 86.9 % (C2 + N3) | **54.3 %** (scene15 + N3) |
| scenes with zero fires | 3 | **0** |
| dominant FA source | `sceneC2` | **`scene15`** (0.699 frame FA, 33.4 % of fires) |
| corpus frame FA | 0.274 | **0.359** (and 0.429 on the *identical* 168 main-round frames) |

So v2 traded one scene's confident, localised hallucination for **lower-amplitude firing spread across
every ordinary test scene**, and the total went up rather than down. The rise is not a denominator
effect: it happened on the same 168 frames v1 measured. RGB's residual FA must be argued as a
threshold/prior issue, not as a single-scene defect. **For Depth the opposite holds** — `sceneC2` is
now **76.1 %** of its cell fires (v1: 68.0 %) while its overall frame FA fell 0.161 → 0.042 — so the
"confident C2 hallucination" caveat migrates from the RGB arm to the Depth arm and belongs in the
limitations section as a Depth caveat. The appearance-preserving C2 control (prepared, not yet
rendered) is therefore a control for Depth's residual FA and for RGB's *former* behaviour.

The prior-coupling line also needs softening. Bias initialisation plus the 8 m split did **not**
break the coupling between the per-cell training prior and the off-arm false-alarm geography: the
Spearman ρ is still +0.848 (RGB, 3-seed mean, p ≤ 3.5 × 10⁻⁵), down from v1's +0.963. What halved is
the gain, not the ranking — FA ÷ prior on the far row is **0.234** against v1's 0.377, and on band 2
**0.062** against 0.243. The claim to make is "**the far-band standing bias was reduced roughly
two-fold, not removed**".

### N.5 Draft paragraph for §5.6 — grid straddling and cell over-blocking

Two structural facts about the V1 grid, measured on the on-arm frames that carry at least one
GT-positive cell (test 327 / corpus 1038), belong in the threats-to-validity section.

**(a) Straddling is the default, and it is not a failure mode.** 93.6 % of test frames (96.8 % of the
corpus) light cells in two or more sectors or bands; the median frame lights 8 cells across 5 sectors.
Sector boundaries are crossed 66–86 % of the time; band boundaries depend sharply on range — 8.3 % at
2 m, 28.4 % at 5 m and **65.1 % at the new 8 m boundary**. This is geometry, not a labelling defect:
a ditch or a stair edge is metres wide and a far wedge is large, so one hazard instance covers several
cells. Two consequences. The frame-recall rule ("detected if any GT-positive cell crosses τ") is not a
lenient convention but the smallest measurable unit on this grid; and low cell-level F1 is partly
structural, since a single instance demands a median of 8 cells while the model lights only the ones it
is most confident about. We therefore report frame metrics as primary and cell F1 as secondary. Testing
whether straddled frames are *missed* more often gives no support: the miss-rate difference
(straddling − flat) is −0.309 … +0.084 across seeds, negative in 2 of 3, with **no seed showing a
significantly positive difference**; restricted to the new 8 m boundary it is −0.354 … −0.088. The
honest reading is "no evidence that straddling hurts", not "straddling helps" — the flat stratum is
only 21 frames.

**(b) A positive cell is not a blocked cell.** Using the label's 5 cm height-map-difference footprint
against the analytic sample capacity of each wedge, the median hazard occupancy of a GT-positive cell
is 0.288 in band 1, 0.655 in band 2, 0.610 in band 3a and 0.861 in band 3b — i.e. **over-blocking
(the traversable fraction of a cell that the grid nonetheless marks positive) is worst up close:
71 % in band 1, 34 % in band 2, 14 % in band 3b**. The distribution is bimodal (Q3 ≥ 0.99 in bands
2/3a/3b, Q1 0.16–0.31), so the median alone hides it. Practical statement for the paper: treating
predicted-positive cells as no-go areas would forbid a large share of walkable ground at close range,
which is the quantitative reason this grid is positioned as an **early-warning** representation rather
than a local path-planning one. It is also a warning for drop-type generalisation: a 0.5–1.5 m hole
occupies only **1–3 %** of an `[8,12)` m cell, so "the cell lights up" means something physically
different there than it does for the wide ditches of this corpus, and any hole-probe recall must be
read together with that occupancy gap.

### N.6 One §5.4 clarification — the range axis is camera standoff, not the band label

§5.4 reads the band decomposition as a distance effect. At v2 that reading is only safe for the V
tier. The v2 H set carries **zero GT cells in bands 1 and 2** and every one of its 96 frames has a
GT cell in band 3b, so "H recall" is arithmetically far-band H recall (identical to band-3b H recall
in 8 of 9 runs). Comparing band 3a against band 3b for the H tier compares two *different frame sets*
(33 vs 96) and gives an unstable answer — Depth's 3b − 3a gap is −0.230 / −0.168 / **+0.165** across
seeds, and on the 33 frames carrying GT in both bands Depth is in fact *better* far (0.697 vs 0.515).
The variable that behaves monotonically is the camera standoff `cam.d`: H frame recall runs
0.917 / 0.644 / 0.587 for RGB and 0.833 / 0.733 / **0.000** for Depth over `d < 7` / `7–9` / `≥ 9` m
(n = 24 / 30 / 42, unanimous across the three seeds). Report the standoff form, not the band form.

---

## Resume chain 0821

*Appended 2026-08-21 after the GPU freed at 11:46. **Nothing above this line was modified.** These
are the four GPU tracks that the night cycle left as PREPARED-NOT-RUN (A1 YOLO seeds, A2 aux
ablation, C2 dressing control, C1 hole probe), now measured. Unlike the `Night 0820→0821 update`
section above — which was re-analysis of frozen artefacts — this section contains **new
measurements**, so §5.2's main table gains its fourth row here.*

Provenance, in order of citation:
`experiments/dayrun_0820/runs/yolo_s{42,43,44}/eval_test/metrics.json` ·
`experiments/dayrun_0820/runs/v2/SEED_TABLE.md` §4–§5 ·
`experiments/dayrun_0820/runs/v2/compare_aux_vs_base_s42/METRICS_SECTION.md` §3 ·
`experiments/nightrun_0820/ctrl_dressing/CTRL_TABLE.md` ·
`experiments/probe_holes_0820/{PROBE_TABLE.md, TIER_TABLE.md}`.

### R.1 §5.2 row 4 is final — the detector baseline's ceiling is constructive, and it holds

The YOLOv8n row of the main table now carries three seeds. On the 816-frame v2 test set at the
detector's own confidence threshold τ = 0.25, it reaches **frame recall 0.150 ± 0.028 on the V tier
and exactly 0.000 on both the E and the H tier, on every seed** (0.117 / 0.161 / 0.172 for V;
0.000 / 0.000 / 0.000 for E and H, at cell level as well as frame level). Off-arm frame false alarms
run 0.005 / 0.025 / 0.042.

The zero is the point of the row, and it must be presented as **constructive rather than empirical**.
The detector's output is a set of image-space boxes; the `det2cell` rule projects each box onto the
ground plane to decide which polar cell it occupies. A hazard in the E tier contributes only a rim,
and a hazard in the H tier contributes **no pixels at all** — so there is no box to project, and the
mapping can emit no cell. E and H recall are therefore not merely expected to be near zero, they are
*constructively bounded* at zero, a bound already measured before training via the oracle-box
diagnostic (D22; `METRICS_NOTES_yolo.md` §3). What three seeds add is the assurance that the
implementation honours the bound: **a nonzero E or H number would have been a mapping-leak alarm,
and across three independently trained detectors the alarm never fired.** The one sub-threshold
exception belongs in a footnote and nowhere else — in the τ = 0.10 sweep row, seeds 42 and 44 each
light exactly one hazard frame of 96 (recall 0.0104), which is a single low-confidence box caught by
the mapping's documented near-band bias, not H-tier perception.

The sentence for the paper is therefore not "the detector performs poorly on invisible hazards" —
that would invite the reply that a better detector would do better. It is: **any method whose output
is a bounding box over visible hazard pixels has an identically zero ceiling on the E and H tiers,
independent of detector quality, and this row measures that ceiling rather than a model.** That is
what motivates the cell-classification formulation, and it is the cleanest single justification for
the paper's framing. Do not report the V column as a comparative result: at 0.150 with cell
precision 0.472 ± 0.110 it is a floor on a task the detector was not trained to do, and the FA
column's 8-fold seed range (0.005 → 0.042) will not support any comparison against a U-Net arm.

### R.2 The auxiliary pixel loss trades the E tier for precision and for H-tier localisation

One development-narrative ablation, RGB seed 42 only, adds a per-pixel auxiliary loss on 648 amodal
hazard masks (`aux_lambda` 0.5) to an otherwise byte-identical recipe — same encoder, same selector,
same oversampling, same seed. Paired against its own base arm on the 816 common frames (percentile
bootstrap, 10000×), the result is not "better" or "worse" but a **change of operating character**.

What it buys is confirmed. Cell precision rises **+0.129** [0.089, 0.169] and off-arm frame false
alarms **halve, 0.375 → 0.167** (Δ −0.208 [−0.253, −0.165]); cell FPR falls 0.053 → 0.023. Most
relevant to this paper's thesis, **H-tier cell recall rises +0.355** [0.277, 0.430] — 0.253 → 0.607,
the largest confirmed effect in the comparison — and the independent twin evidence agrees, with the
H-tier on/off Δ nearly doubling from 0.170 to 0.326. Cell F1 improves +0.040, with a CI whose lower
bound is 0.0001; report that as "improved, marginally significant", not as a headline.

What it costs is equally clear and larger in one place: **the E tier collapses completely.** Frame
recall on rim-only hazards goes 0.600 → **0.000** (Δ −0.600 [−0.744, −0.453]), cell recall
0.359 → 0.000. V recall falls 0.828 → 0.639 and the overall frame detection rate follows,
0.731 → 0.563. Supervising the network toward hazard *pixels* appears to sharpen it onto
high-confidence, well-supported evidence and to cost it exactly the marginal-evidence tier.

Two limits must travel with this paragraph. First, the frame-level H gain that reads best in a
summary, +0.125, has a **confidence interval containing zero** ([−0.010, 0.253]); only the
cell-level gain is statistically supported, so the claim must be written at cell level. Second,
**n = 1 seed**, against a base RGB arm whose own three-seed H spread is ±0.141 — a single-seed
frame-level move of +0.125 sits inside seed noise. This belongs in an appendix and a future-work
sentence, never in the main table (approval item #2 default: main table stays at four rows).

### R.3 The C2 false alarms decompose: roughly three quarters dressing, one quarter hazard geometry

§5.6 records an unresolved confound. `sceneC2`'s hazard-off arm deleted not only the stair drop but
the scene's dressing — the leaf mound, the railing — so the on/off difference measured there mixed
"the hazard is gone" with "the scene looks different". A dedicated control round now separates them.
A second off arm was rendered with `keep_dressing`: hazard geometry removed, every dressing element
holding its on-arm transform, and the camera datum strip byte-equal to the on arm so both off arms
pair against the *same* on frames at pose tolerance zero.

The split is large and one-directional. Against the shared on arm, the old off arm's paired frame
delta is **0.699 ± 0.204** across three RGB seeds; the dressing-preserving off arm's is
**0.163 ± 0.062**. Roughly **77 % of what looked like the model's response to the removed hazard was
its response to the removed dressing**, and about **23 % survives as a response to the hazard
geometry itself**. The residual is small but consistent in sign on all three seeds
(0.185 / 0.214 / 0.090).

The control also produces an uncomfortable second number that must be reported with the first. On
the dressing-preserving off arm — frames that carry an all-zero ground truth, so every fire is a
false alarm — the frame false-alarm rate is **0.681 ± 0.208**, against 0.069 ± 0.104 on the old off
arm, with 2.11 cells firing per frame and a mean max probability of 0.651. Read plainly: when the
leaf mound and the railing remain but the drop does not, **the model fires confidently on ground
that is safe**. This is not a contradiction of the previous paragraph, it is its mechanism — the
model is using the dressing as a cue for hazard, which is precisely why removing the dressing
suppressed its response in the old arm. Stated positively it is cue-consistent behaviour; stated
operationally it is a shortcut, and it belongs in the limitations section, not in the results
narrative.

`sceneN3` served as the null control and behaved as designed. Its dressing is a wall mural, 1–2 mm
of paint on flat floor, so the dressing-preserving off arm is *structurally identical* to the on arm;
its twin delta must be zero, and it measures **−0.001 ± 0.001** (per-seed 0.000 / −0.001 / −0.002).
The measurement apparatus introduces no delta of its own, which is what licenses reading C2's 0.163
as signal.

Finally, and importantly for §5.3: **this control does not touch the headline causal claim.** The
twin analysis behind that claim already excludes `sceneC2` entirely — it contributes zero H-tier
pose-matched pairs — and the night cycle's exact-pose stratification showed the H-tier delta
unchanged to four decimals when only byte-identical pose pairs are used. The dressing confound was
always confined to the *all-tier* delta, and it is that number, not the headline, which this control
corrects.

### R.4 The hole probe splits RGB and Depth along a semantic/geometric line

Three purpose-built scenes, never trained on, probe a drop *type* absent from the corpus: a
0.5–1.5 m hole rather than a wide ditch or a stair edge. The tier design landed as specified —
`probeH1` is V-dominant (15 V / 3 E / 6 H of 24 on-frames), `probeH2` is **pure E, all 24 frames**,
`probeH3` is **pure H, all 24 frames** — so for the first time the E and H claims can be tested on
frames that are *only* E or *only* H. All nine frozen recipe-v2 checkpoints were run at the frozen
τ = 0.5, with no refitting (`val` is deliberately empty in the probe split).

**Zero-shot transfer largely fails for RGB and partially succeeds for Depth, and the two failures
have different shapes.** On the pure-H scene, RGB recall is **0.083 / 0.292 / 0.100** across seeds
while Depth reaches **0.500 / 0.625 / 0.375** — Depth roughly triples RGB on the tier where neither
model can see the hazard. This inverts the ordering of the main table, where RGB leads Depth on the
H tier (0.688 vs 0.438), and the inversion is the finding. RGB's H-tier competence on the training
corpus is *semantic context*: it has learned what the surroundings of a ditch or a stair look like,
and a hole in a corridor does not supply those surroundings. Depth's is *geometric*: whatever
range-discontinuity signature it keys on survives the change of drop type, degraded but present.
**The RGB result is scene-vocabulary-bound; the Depth result is closer to type-general.** On the
pure-E scene both collapse almost totally (RGB 0.000 on all three seeds; Depth 0.125 / 0.000 / 0.000),
so the E-tier claim in this paper should be read as corpus-specific until a probe with more E variety
exists.

Two numbers stop this from being read as a clean story. First, **`b2_s43` is a trigger-happy
outlier**: it scores 1.000 frame recall on `probeH1` — but with an off-arm false-alarm rate of
**0.917** on the same scene, and 0.750 on both other scenes. It is not detecting holes, it is firing
almost everywhere, and its apparent recall is an artefact of that. Its sibling seeds `b2_s42` and
`b2_s44` both score 0.000 on `probeH1` with FA 0.000. Any per-seed table must show the FA column
beside the recall column, and no B2 probe number should be quoted as a mean over three seeds.
Second, the false-alarm rates rise with recall throughout the probe — Depth's pure-H recall of
0.500 / 0.625 / 0.375 comes with off-arm FA of 0.500 / 0.625 / 0.500 — which means the probe
demonstrates **transfer of a firing tendency at least as much as transfer of discrimination**, and
should be written that way.

The corridor-preserving scene supplies one further diagnostic. In `probeH2` the hazard occupies a
single lateral sector and the neighbouring sectors in the same band are hazard-free, so firing there
distinguishes angular blur around a correct answer from a scene-level prior. Seven of nine
checkpoints fire on **zero** adjacent cells; the exceptions are `b2_s43` (9 of 48 adjacent cells,
adjacent frame rate 0.375, against a far-cell rate of 0.045) and `depth_s42` (6 of 48, 0.125,
against a far rate of **0.000**). For `depth_s42` the pattern is clean angular blur — misplacement
beside a correct answer, not a broadcast. For `b2_s43` the far rate is nonzero too, consistent with
the trigger-happy reading above.

The probe is evaluation-only by construction and no probe frame may enter training; it changes no
number in §5.2 and its role in the paper is to bound the generalisation claim, in the limitations
section: **the H-tier result is demonstrated for the drop types in this corpus, and the RGB arm's
version of it does not survive a change of drop type.**

> R.4 부기 (panel-audited): Depth's apparent hole-transfer recall is largely saturation
> firing (all far cells at 1.00 on hit frames; probe off-arm FA .5-.625). Honest phrasing:
> neither modality transfers cleanly zero-shot; Depth's recall is partly an OOD broad-firing
> artifact, RGB stays conservative (low recall AND low FA).

---

## RED-TEAM RESPONSE 0823 — draft-text consequences (appended 2026-08-23, D35)

Six new measurements on frozen artefacts change what §5.2–§5.6 and R.1–R.4 are allowed to say.  Numbers, provenance and per-seed tables: `METRICS.md` §RT.1–RT.7 and `experiments/weekend_0823/rt_response/`.  Nothing above this line is edited; each item below names the sentence it replaces.


### RT-A  §5.2 and R.4 — withdraw the "inversion" narrative, keep the weaker claim

**Replaces** R.4's *"This inverts the ordering of the main table, where RGB leads Depth on the H tier (0.688 vs 0.438), and the inversion is the finding."*  There is no ordering to invert: the main table reads RGB's H recall at an off-arm FA of 0.359 and Depth's at 0.042.

> At matched false-alarm rates the Depth arm leads the RGB arm on the hidden tier at every operating point we can read, and the gap widens as the false-alarm budget is tightened (H recall 0.781 vs 0.729 at FA 0.359; 0.510 vs 0.326 at FA 0.10; 0.479 vs 0.243 at FA 0.05).  The apparent RGB advantage in the main table is an artefact of reading two arms at a shared τ rather than a shared operating point.  What survives, and is what this paper is about, is weaker and sufficient: **a monocular RGB model with no hazard pixels available still recovers a third of the hidden-tier frames at a 10 % false-alarm budget (0.326 ± 0.229), where the detector baseline's twin-conditional rate on the same tier is −0.010.**  The hole probe's Depth-over-RGB result is therefore consistent with, not contrary to, the corpus.


### RT-B  §5.3 — the twin evidence, stated per scene and per condition

**Replaces** the pooled *"H Δ > 0, 9/9 CIs exclude zero"* framing.

> The test strict-H set is **two scenes** (scene14 n = 60, scene15 n = 36) and the test E set is **one** (scene18 n = 45).  Frame-level bootstrap intervals over 96 H frames assume 96 independent samples; the frames are 60 + 36 re-photographs of two geometries, and under scene-cluster resampling the false-alarm intervals widen by ×1.7–5.6.  We therefore report **no confidence interval for the H and E tiers** and print the per-scene value beside the same scene's off-arm false-alarm rate instead.  The H-tier twin effect is carried by scene14 (twin Δ: RGB .278/.448/.558, Depth .577–.645); on scene15 it is indistinguishable from zero (RGB −.010/.209/−.058) and two of three RGB seeds fire on more hazard-free frames of that scene than they detect hidden drops in it.

> Applying the twin as a *conditional* — counting a hit only when the model fires on the hazard-ON frame and not on its pose-exact hazard-OFF twin — sharpens the reading into a positive claim: **the Depth arm's hidden-tier response is entirely hazard-conditional (0 of 96 pairs fire on the deleted twin, on all three seeds, so 0.438 → 0.438), while 44.7 % of the RGB arm's hidden-tier firings also occur when the hazard is gone (0.688 → 0.375).**  The two arms were not counting the same event.


### RT-C  §5.1 / §5.6 — what "hidden" means, stated exactly

**Replaces** any use of *"fully occluded"* for the H tier.

> The H tier is defined geometrically: the hazard prism re-projects to **zero contributing pixels** under the frame's depth buffer.  That is not the same as the image being unchanged.  Differencing all 96 test H twin pairs at native resolution, **no pair is identical**: the median pair differs on 4.5 % of the frame at ≥ 32/255, and the quietest pair still differs on 2 211 pixels — 44× the renderer's own nondeterminism floor, which we measured on a geometrically identical render pair.  81 % of that residual lies inside the amodal hazard silhouette.  A positive twin Δ on the H tier therefore needs no exotic explanation; the honest claim is that the model recovers the hazard **without any pixel of the hazard surface itself**, from shading, occlusion and layout evidence that the hazard's presence produces elsewhere in the frame.

> Two qualifiers travel with every twin Δ in this paper.  First, the intervention removes the hazard geometry **and everything the scene builder places inside the same branch** — in scene14 the shoulder massif, side slopes, stair, coursing, parapets, cues and litter — so Δ measures sensitivity to that whole package, not to the drop alone.  Second, the twin identifies **that** the response is caused by the hazard's presence in the scene; it does not identify **which image property** carries the causation.  Separating a real-world cue from a rendering side-effect or a corpus convention requires the cue-level ablation, which is not run here.

> The residual is also graded evidence, and only one arm uses it that way: the rank correlation between a pair's residual pixel count and that pair's twin Δ is positive for the Depth arm in all six within-scene cells (ρ 0.08–0.69, with mean Δ rising from 0.34–0.40 on the quietest third of scene14's pairs to 0.83–0.93 on the loudest), and inconsistent for the RGB arm (ρ −0.13 to +0.39).


### RT-D  §5.2 row 4 — the detector bound, scoped to the adapter

**Replaces** R.1's *"any method whose output is a bounding box over visible hazard pixels has an identically zero ceiling on the E and H tiers, independent of detector quality."*  That generalises to a paradigm; what was measured is our mapping.

> Two distinct bounds apply to the detector row and must not be conflated.  **(i)** Our ground-projection adapter cannot map a box to an E- or H-tier cell at all: feeding the amodal ground-truth boxes in as confidence-1.0 detections yields E = H = 0.000 before any training, so the zeros in the table are a property of the adapter.  **(ii)** Removing the adapter and scoring purely in image space — does any stored detection overlap any amodal ground-truth box — the detector does fire near hidden hazards at a low rate (0.066 of H frames at IoU > 0), but the identical measurement on the hazard-deleted twin of the same cut gives 0.076, so the **twin-conditional rate is −0.010: no hazard-conditional evidence at all**, against +0.337 on the visible tier where the same control shows the detector is strongly conditional.  The defensible statement is (ii), and it is the stronger one — an **amodal-trained** detector, taught to draw boxes over hazards it cannot see, still produces nothing conditional on the hazard when the hazard contributes no pixels.

> We also state the limitation of our own baseline first: for a fully occluded hazard the amodal box is not determined by the image — in scene14 it spans the building facade the drop hides behind — so the detector was given a partly unlearnable target.  At the storage confidence floor (0.05) the twin-conditional H rate rises to 0.142, which we report alongside the operating-point value.


### RT-E  §5.6 / limitations — three numbers to publish before a reviewer finds them

> **(a) A false-alarm tier sits in no denominator.**  19.9 % of hazard-ON test frames (81/408) have the hazard outside the grid, so their ground truth is all-zero and every firing is a false positive — yet they enter neither the recall denominator nor the off-arm false-alarm rate.  On that tier the RGB arm fires on 0.798 ± 0.160 of frames against its reported 0.359, the Depth arm on 0.494 ± 0.074 against 0.042, and the SegFormer arm on 0.638 ± 0.228 against 0.238.  We report this as a fourth false-alarm column rather than a footnote.

> **(b) The null-control scene did not pass; the RGB model failed it.**  `sceneN3` contains no drop-off in either arm, so its twin Δ of −0.001 is correct — but it is zero because both arms are saturated, not because both are silent: the RGB arm fires on 0.75–1.00 of its frames in **both** arms at a mean maximum probability of 0.74–0.95.  The Depth arm is genuinely quiet there (0.000–0.125), and SegFormer-B2 is mixed.  Together with the C2 dressing decomposition — roughly three quarters of that scene's twin delta is removed dressing — this is the clearest single measurement of scene-level shortcut behaviour in the RGB arm, and it belongs in the limitations section rather than in a list of controls that passed.

> **(c) Two published significance claims do not survive scene-cluster resampling.**  The auxiliary pixel-loss arm's `cell_f1` gain, reported as +0.0403 [0.0001, 0.0786], becomes [−0.258, 0.205]; more importantly its `cell_recall_H` gain of +0.3546 — described in the seed table as the largest confirmed effect and the one bearing on this paper's thesis — becomes [−0.143, 0.463].  Both frame-level intervals were measuring variation within the same two H scenes.  The precision and false-alarm gains do survive.


### RT-F  Figures added

| figure | file | what it shows |
|---|---|---|
| recall vs false alarms | `rt_response/figs/fig_f1_recall_vs_fa.png` (+ `.pdf`) | full τ sweep for all three arms and all three seeds on the H, E and V tiers, with the published τ = 0.5 points marked; makes the operating-point mismatch visible in one look |
| strict-H twin residuals | `rt_response/panels/h_diff_contact_sheet.png` and six individual panels | hazard-ON / hazard-OFF / absolute difference for the min, median and max residual pair of each H scene, with the amodal silhouette and GT wedges outlined |
