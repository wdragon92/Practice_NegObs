
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
