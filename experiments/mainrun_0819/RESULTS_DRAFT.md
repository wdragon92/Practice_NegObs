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
