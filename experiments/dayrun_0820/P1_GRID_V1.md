# P1_GRID_V1 — V0→V1 grid transition, invariant proof and boost targeting

grid V0: `PROVISIONAL-GRID-V0` — 3 bands [0.0, 2.0, 5.0, 12.0] m × 5 sectors = **15 cells**
grid V1: `PROVISIONAL-GRID-V1` — 4 bands [0.0, 2.0, 5.0, 8.0, 12.0] m × 5 sectors = **20 cells**  (`code/labeling/gridspec_v1.json`; cell index = band*5 + sector)

labels V0: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819/annotations/labels_v0.json`
labels V1: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/annotations/labels_v1.json`
manifest : `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2.json`

V1 is a strict refinement: bands 1 and 2 keep their V0 cell indices and meaning, V0's band 3 `[5,12)` m is cut at 8 m into `3a [5,8)` + `3b [8,12)`. The outer radius and the angular coverage do not move, so the set of ground inside the grid is identical and the comparison below is apples-to-apples.

## 1. INVARIANT GATE (mandatory) — tier map must be identical

V/E/H are frame properties: they say what the camera can SEE of a drop, and the only tier with any grid dependence is `none_in_fov` (fires when no cell is positive), which depends on grid COVERAGE, not on how the coverage is tiled. Retiling inside an unchanged outer radius therefore must move zero frames.

**scope: all 33 scenes, both arms, 1584 frames — every frame compared, not the 29-scene eligible view.**

| tier | V0 | V1 | Δ |
|---|---|---|---|
| V | 438 | 438 | +0 |
| E | 36 | 36 | +0 |
| H | 45 | 45 | +0 |
| H_weak | 12 | 12 | +0 |
| none_in_fov | 261 | 261 | +0 |
| off | 792 | 792 | +0 |
| **frames** | **1584** | **1584** | **+0** |

- frame-by-frame `tier_strict(V1) == tier_strict(V0)` mismatches: **0**
- any-cell-positive mismatches (the only channel by which a retile could move `none_in_fov`): **0**
- nesting-law violations (`V1` folded 3a|3b back onto V0 ≠ V0): **0**

**VERDICT: IDENTICAL — PASS.** The tier map is untouched by the grid change, so every V0 headline number (V 438 · E 36 · H 45 · H_weak 12) carries over unaltered and the V0↔V1 comparison is legitimate.

Restated on the **29 eligible scenes** (the view the brief quotes as `V438 E36 H45 H_weak12 none 165`):

| tier | V0 | V1 | Δ |
|---|---|---|---|
| V | 438 | 438 | +0 |
| E | 36 | 36 | +0 |
| H | 45 | 45 | +0 |
| H_weak | 12 | 12 | +0 |
| none_in_fov | 165 | 165 | +0 |
| off | 696 | 696 | +0 |

held scenes (scene11, scene13, scene19, sceneD4) contribute only `none_in_fov` and `off`, which is why the 33-scene and 29-scene views differ in exactly those two columns and in neither V, E nor H.

## 2. 20-cell positive-count heatmap — TRAIN frames, ELIGIBLE scenes

train scenes (20): `scene01 scene02 scene03 scene04 scene06 scene08 scene09 scene12 scene16 scene17 scene20 scene21 sceneC1 sceneC4 sceneD1 sceneD2 sceneN1 sceneN2 sceneN4 sceneN5`
counted frames: **480** hazard-ON train frames (the 480 twin off-arm frames are structurally all-negative and are excluded; including them would just halve every number).

Cell value = how many of those frames have that cell GT-positive.

| band \ sector | **A** | **B** | **C** | **D** | **E** | band total | share of frames |
|---|---|---|---|---|---|---|---|
| **1** (0.0–2.0 m) | 39 | 42 | 42 | 39 | 36 | 198 | 8.2% |
| **2** (2.0–5.0 m) | 144 | 156 | 141 | 138 | 114 | 693 | 28.9% |
| **3a** (5.0–8.0 m) | 177 | 225 | 237 | 213 | 186 | 1038 | 43.2% |
| **3b** (8.0–12.0 m) | 231 | 267 | 321 | 294 | 240 | 1353 | 56.4% |
| **sector total** | 591 | 690 | 741 | 684 | 576 | 3282 | |

The same table under V0, for reference (band 3 is the row V1 splits):

| band \ sector | **A** | **B** | **C** | **D** | **E** | band total |
|---|---|---|---|---|---|---|
| **1** (0.0–2.0 m) | 39 | 42 | 42 | 39 | 36 | 198 |
| **2** (2.0–5.0 m) | 144 | 156 | 141 | 138 | 114 | 693 |
| **3** (5.0–12.0 m) | 249 | 294 | 345 | 324 | 258 | 1470 |

## 3. mean positive cells per frame — V0 → V1

| subset | frames | V0 mean | V1 mean | Δ | V0 % of cells | V1 % of cells |
|---|---|---|---|---|---|---|
| train, eligible, on-arm | 480 | 4.919 | 6.838 | +1.919 | 32.8% | 34.2% |
| all eligible, on-arm | 696 | 4.987 | 7.026 | +2.039 | 33.2% | 35.1% |
| all 33 scenes, on-arm | 792 | 4.383 | 6.174 | +1.792 | 29.2% | 30.9% |
| train, on-arm, positives only (none_in_fov frames dropped) | 351 | 6.726 | 9.350 | +2.624 | 44.8% | 46.8% |

The mean rises by **+1.92 cells/frame** purely because a far footprint that filled one V0 band-3 cell now fills up to two V1 cells (duplication factor **×1.63** on band 3, §4). It is resolution, not new positives — the nesting law holds on every frame (§1).

Per-cell label DENSITY barely moves: **32.8% → 34.2%** of cells positive per frame. The V1 head therefore faces the same class balance it did under V0 (so the D19 bias-initialisation recipe transfers directly), while gaining the ability to say *how far* — which is the whole point of the split: under V0 a positive anywhere in 5–12 m was one label, and 5 m vs 11 m is the difference between braking now and noting a distant edge.

## 4. band 3 → 3a / 3b decomposition

Every (frame, sector) pair that was positive in V0's band 3, classified by where its footprint landed under V1. Train on-arm frames, eligible scenes; **1470** such pairs.

| where the old band-3 positive went | pairs | share |
|---|---|---|
| 3a only | 117 | 8.0% |
| 3b only | 432 | 29.4% |
| 3a+3b | 921 | 62.7% |
| LOST | 0 | 0.0% |
| **total** | **1470** | |

- band 3a `[5,8)` m positives: **1038** cell-frames
- band 3b `[8,12)` m positives: **1353** cell-frames
- V0 band 3 positives: **1470** cell-frames → V1 far total **2391** (×1.63 — the duplication factor of the split)
- `LOST` must be 0: a V0 band-3 positive with neither 3a nor 3b set would be a labeler bug. Observed: **0**.

Per sector:

| sector | 3a only | 3b only | 3a+3b |
|---|---|---|---|
| A | 18 | 72 | 159 |
| B | 27 | 69 | 198 |
| C | 24 | 108 | 213 |
| D | 30 | 111 | 183 |
| E | 18 | 72 | 168 |

## 4.1 two side effects of the refinement — both resolution gains

### (a) the D14 step-gate exclusion ledger gets sharper

| | V0 | V1 |
|---|---|---|
| frames losing ≥1 GT cell to the step gate | 33 | **48** |
| GT cells excluded (sum) | 87 | **147** |

**15 frames record an exclusion under V1 that V0 recorded as none.** This is not the gate behaving differently — the footprint, the gate and the survivors are byte-identical, and the pre-gate nesting law holds on every frame (**0** violations). It is a coarse cell hiding an exclusion: when the gate dropped a component at ~6 m while another survived at ~10 m, V0's single band-3 cell stayed positive and logged nothing. V1 puts them in 3a and 3b and the loss becomes visible.

Worked example — `on/scene03/L0__s20260819__0000.png`:

```
V0  pregate [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
V0  trained [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]   gate_excluded n=0  <- nothing logged
V1  pregate [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1]
V1  trained [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]   gate_excluded [11, 12]
```

Same footprint, same gate; V0's band-3 cell was positive either way, so the excluded near-half left no trace. **Consequence for the morning ruling: the D14 revert ledger was under-reporting, and the V1 number (48 frames / 147 cells) is the honest one.**

### (b) G5 agreement resolves into a clean distance trend

G5 = the fraction of GT-positive cells that hold at least one reprojected below-ground pixel. D19⑤ demotes it to a reference metric on the argument that it measures view shadow, not label quality. V1 makes that argument checkable, because the far band splits:

| grid | band | agreement | positive cells |
|---|---|---|---|
| V0 | 1 (0.0–2.0 m) | 0.029 | 309 |
| V0 | 2 (2.0–5.0 m) | 0.475 | 948 |
| V0 | 3 (5.0–12.0 m) | 0.715 | 1782 |
| **V1** | **1** (0.0–2.0 m) | **0.029** | 309 |
| **V1** | **2** (2.0–5.0 m) | **0.475** | 948 |
| **V1** | **3a** (5.0–8.0 m) | **0.595** | 1332 |
| **V1** | **3b** (8.0–12.0 m) | **0.696** | 1659 |

Agreement rises monotonically with range — 0.03 → 0.47 → 0.59 → 0.70 — which is exactly what the view-shadow explanation predicts and what a labeling defect would not produce. The near band's 0.029 is geometry: standing at the lip of a drop, the floor immediately below is occluded by the lip itself.

Note the far row does not merely subdivide: V0 scored 0.715 over 1782 band-3 cells, V1 scores 0.595 / 0.696 over 2991 cells. **V0's pooling flattered the far band**: one below-ground pixel anywhere in 5–12 m satisfied the whole 7 m-deep cell, whereas V1 asks the question separately of 5–8 m and 8–12 m. Both readings are honest about their own grid — which is precisely why a threshold on the pooled number was never a gate-worthy quantity, and D19⑤'s demotion is the right call.

## 5. SPARSE CELLS — boost-render targeting basis

### 5.1 the brief's criterion: < 10 positive train frames

**None. All 20 cells clear the bar.** The least-populated cell is **1E** with **36** positive train frames of 480, 4× the threshold.

That is a real result and it is the *expected* one: V1 splits band 3, the most-populated band, so the split creates no frame-count sparsity — it creates 3b (8–12 m) out of the far half of an already dense row. **Frame count is therefore the wrong targeting signal for this corpus**, and §5.2 gives the one that is not.

### 5.2 scene diversity per cell — the sparsity that actually bites

A cell can hold hundreds of positive frames and still be sparse in the only way that matters: if they all come from one scene, the head memorises that scene's geometry instead of learning the cell. Of the 20 train scenes, **15** ever produce a positive at all; the 5 that never do are `scene06`, `sceneN1`, `sceneN2`, `sceneN4`, `sceneN5` (the designed hard negatives plus the out-of-FOV scene06 — all correct zeros).

| cell | band | sector | positive train frames | distinct train scenes | val+test frames | verdict |
|---|---|---|---|---|---|---|
| 1E | 1 | E | 36 | **7**/15 | 27 | ok |
| 1A | 1 | A | 39 | **7**/15 | 21 | ok |
| 1D | 1 | D | 39 | **7**/15 | 30 | ok |
| 1B | 1 | B | 42 | **8**/15 | 27 | ok |
| 1C | 1 | C | 42 | **8**/15 | 30 | ok |
| 2E | 2 | E | 114 | **12**/15 | 51 | ok |
| 2C | 2 | C | 141 | **13**/15 | 69 | ok |
| 2A | 2 | A | 144 | **13**/15 | 54 | ok |
| 3bE | 3b | E | 240 | **13**/15 | 99 | ok |
| 2D | 2 | D | 138 | **14**/15 | 63 | ok |
| 2B | 2 | B | 156 | **14**/15 | 69 | ok |
| 3aA | 3a | A | 177 | **14**/15 | 90 | ok |
| 3aE | 3a | E | 186 | **14**/15 | 78 | ok |
| 3bA | 3b | A | 231 | **14**/15 | 120 | ok |
| 3aD | 3a | D | 213 | **15**/15 | 105 | ok |
| 3aB | 3a | B | 225 | **15**/15 | 114 | ok |
| 3aC | 3a | C | 237 | **15**/15 | 129 | ok |
| 3bB | 3b | B | 267 | **15**/15 | 138 | ok |
| 3bD | 3b | D | 294 | **15**/15 | 135 | ok |
| 3bC | 3b | C | 321 | **15**/15 | 159 | ok |

**No cell is fed by fewer than 5 distinct train scenes.**

Scenes currently feeding the three thinnest cells (this is who a boost render would be duplicating, so prefer OTHER scenes):

- **1E** (36 frames): `scene01`, `scene08`, `scene09`, `scene17`, `scene21`, `sceneD1`, `sceneD2`
- **1A** (39 frames): `scene01`, `scene02`, `scene08`, `scene17`, `scene21`, `sceneD1`, `sceneD2`
- **1D** (39 frames): `scene01`, `scene08`, `scene09`, `scene17`, `scene21`, `sceneD1`, `sceneD2`

**Reading for Phase 2:** the thin end of this table is band **1**, not the new 3b. The five thinnest cells are 1E, 1A, 1D, 1B, 1C — all of them in the near bands, because a hazard within 2 m of the eye fills a small solid angle and only the closest cuts see one at all. 3b, the cell the split created, is the **densest** row in the grid (1353 positives vs 198 for band 1). So the V1 split introduced no sparsity, and E-boost cameras placed at 6–12 m will land in the already-dense rows: their value is tier diversity (E frames), **not** cell coverage. Cell coverage is not a problem this corpus has.

### 5.3 evaluation-side coverage (val / test, on-arm)

A cell with no positive in val+test cannot be scored, however well it is trained.

| split | scenes | frames | cells with 0 positives | thinnest cells |
|---|---|---|---|---|
| val | 2 | 48 | 1 (1A) | 1A=0, 1B=3, 1C=3, 2A=3 |
| test | 7 | 168 | 0 (—) | 1A=21, 1E=21, 1B=24, 1D=24 |

**FLAG for Phase 4 (split v2):** `val` has no positive at all in 1A, so per-cell metrics are undefined there and a cell-F1 averaged over all 20 cells silently drops 1 of them. This matters because the D19 checkpoint selector reads **val cell F1** — worth checking when Phase 4 picks the train→val scene to move.

## 6. per-scene tier E + far-visible-rim potential (E-boost basis, D19③)

All eligible scenes, hazard-ON frames. Columns:

- `E/V/H` — tier counts today.
- `far GT` — frames whose GT reaches band 3a/3b (5–12 m): the scene HAS hazard at the range a far camera would shoot.
- `far only` — ... and nothing in bands 1–2: the pure rim-at-distance geometry, the E生成 case.
- `rim proj` — frames where ≥8 lip points projected into frame at all (an E call is even possible).
- `near-miss E` — far-GT frames where the lip projected but the visible fraction stayed under τ_edge=0.05 (or interior pixels dominated): a lower/farther camera is the single change that converts these.
- `far cam` — frames already shot from `cam.d ≥ 6.0 m`, and how many of those came out E (the empirical hit rate of the boost geometry).

| scene | split | frames | E | V | H | far GT | far only | rim proj | near-miss E | far cam (d≥6.0) | far-cam E |
|---|---|---|---|---|---|---|---|---|---|---|---|
| scene01 | train | 24 | 0 | 24 | 0 | 24 | 12 | 24 | 3 | 12 | 0 |
| scene02 | train | 24 | 9 | 15 | 0 | 24 | 9 | 24 | 0 | 9 | 0 |
| scene03 | train | 24 | 0 | 18 | 0 | 18 | 15 | 18 | 18 | 9 | 0 |
| scene04 | train | 24 | 0 | 24 | 0 | 24 | 12 | 24 | 15 | 9 | 0 |
| scene05 | test | 24 | 0 | 24 | 0 | 24 | 6 | 21 | 21 | 6 | 0 |
| scene06 | train | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 0 |
| scene07 | test | 24 | 0 | 21 | 0 | 21 | 15 | 21 | 0 | 6 | 0 |
| scene08 | train | 24 | 0 | 21 | 0 | 24 | 6 | 18 | 15 | 6 | 0 |
| scene09 | train | 24 | 0 | 6 | 15 | 24 | 15 | 24 | 21 | 6 | 0 |
| scene10 | val | 24 | 0 | 15 | 0 | 15 | 15 | 15 | 15 | 9 | 0 |
| scene12 | train | 24 | 0 | 24 | 0 | 24 | 12 | 21 | 12 | 12 | 0 |
| scene14 | test | 24 | 0 | 6 | 18 | 24 | 21 | 21 | 21 | 9 | 0 |
| scene15 | test | 24 | 0 | 21 | 3 | 24 | 12 | 21 | 21 | 3 | 0 |
| scene16 | train | 24 | 0 | 24 | 0 | 24 | 15 | 24 | 0 | 9 | 0 |
| scene17 | train | 24 | 0 | 12 | 9 | 24 | 12 | 24 | 21 | 6 | 0 |
| scene18 | test | 24 | 9 | 15 | 0 | 24 | 9 | 24 | 3 | 6 | 6 |
| scene20 | train | 24 | 0 | 21 | 0 | 21 | 21 | 21 | 21 | 3 | 0 |
| scene21 | train | 24 | 3 | 21 | 0 | 24 | 3 | 15 | 0 | 3 | 3 |
| sceneC1 | train | 24 | 0 | 21 | 0 | 24 | 15 | 24 | 24 | 12 | 0 |
| sceneC2 | test | 24 | 0 | 24 | 0 | 24 | 12 | 24 | 24 | 6 | 0 |
| sceneC4 | train | 24 | 0 | 24 | 0 | 24 | 21 | 24 | 24 | 12 | 0 |
| sceneD1 | train | 24 | 0 | 24 | 0 | 24 | 3 | 21 | 15 | 6 | 0 |
| sceneD2 | train | 24 | 9 | 15 | 0 | 21 | 18 | 21 | 0 | 12 | 6 |
| sceneD3 | val | 24 | 6 | 18 | 0 | 24 | 9 | 21 | 12 | 9 | 6 |
| sceneN1 | train | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 |
| sceneN2 | train | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| sceneN3 | test | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 |
| sceneN4 | train | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 0 |
| sceneN5 | train | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| **total** | | 696 | 36 | 438 | 45 | 528 | 288 | 495 | 306 | 231 | 21 |

### E-boost TRAIN scene candidates (ranked, data-driven — D19③)

Ranking by far-GT fraction alone is useless here: **12 train scenes reach 5–12 m on 100% of their cuts**, so they all tie. The discriminating question is how many frames sit **one camera change away from an E call**:

`convertibility = (0.6·near-miss E + 0.4·far-only) / frames`, damped by `1/(1+E_now)` because a scene already supplying E needs the boost least.

| rank | scene | far-GT frac | E now | near-miss E | far only | convertibility | verdict |
|---|---|---|---|---|---|---|---|
| 1 | `sceneC4` | 100% | 0 | 24 | 21 | 0.95 | **PRIME** — zero E, most frames already near-miss |
| 2 | `scene20` | 88% | 0 | 21 | 21 | 0.88 | **PRIME** — zero E, most frames already near-miss |
| 3 | `sceneC1` | 100% | 0 | 24 | 15 | 0.85 | **PRIME** — zero E, most frames already near-miss |
| 4 | `scene09` | 100% | 0 | 21 | 15 | 0.78 | **PRIME** — zero E, most frames already near-miss |
| 5 | `scene17` | 100% | 0 | 21 | 12 | 0.72 | **PRIME** — zero E, most frames already near-miss |
| 6 | `scene03` | 75% | 0 | 18 | 15 | 0.70 | **PRIME** — zero E, most frames already near-miss |
| 7 | `scene04` | 100% | 0 | 15 | 12 | 0.58 | **PRIME** — zero E, most frames already near-miss |
| 8 | `scene12` | 100% | 0 | 12 | 12 | 0.50 | **PRIME** — zero E, most frames already near-miss |
| 9 | `scene08` | 100% | 0 | 15 | 6 | 0.48 | **PRIME** — zero E, most frames already near-miss |
| 10 | `sceneD1` | 100% | 0 | 15 | 3 | 0.42 | **PRIME** — zero E, most frames already near-miss |
| 11 | `scene01` | 100% | 0 | 3 | 12 | 0.28 | **STRONG** — zero E, real near-miss population |
| 12 | `scene16` | 100% | 0 | 0 | 15 | 0.25 | weak — far hazard, but no lip currently near the τ_edge line (interior dominates; a far cam may not tip it) |
| 13 | `sceneD2` | 88% | 9 | 0 | 18 | 0.30 | marginal — E already supplied, nothing near the line |
| 14 | `scene02` | 100% | 9 | 0 | 9 | 0.15 | marginal — E already supplied, nothing near the line |

**Recommended train E-boost set (top 6 by convertibility): `sceneC4`, `scene20`, `sceneC1`, `scene09`, `scene17`, `scene03`**

Render the D19① E-boost override (d∈[6,12] m, h∈[1.2,1.9] m) on these. The empirical warrant is in the table above: the three train scenes that already produce E (`scene02`, `scene21`, `sceneD2`) produce **9 of their 21 E frames from cameras already at d ≥ 6.0 m** — far cameras are where E comes from in this corpus, so the override is aimed at a demonstrated mechanism, not a guess.

Scenes deliberately NOT recommended, with the reason:

| scene | why not |
|---|---|
| `scene04` | ranked below the cut (convertibility 0.58) |
| `scene12` | ranked below the cut (convertibility 0.50) |
| `scene08` | ranked below the cut (convertibility 0.48) |
| `sceneD1` | ranked below the cut (convertibility 0.42) |
| `scene01` | ranked below the cut (convertibility 0.28) |
| `scene16` | far hazard present but no frame is near the τ_edge line — its rims are either fully visible (V) or not projecting; low expected yield |
| `sceneD2` | already supplies 9 E frames; spend the render budget elsewhere |
| `scene02` | already supplies 9 E frames; spend the render budget elsewhere |
| `scene21` | already supplies 3 E frames; spend the render budget elsewhere |
| `scene06` | no far-range hazard at all (hard negative / out-of-FOV) — a far camera would add frames with nothing to see |
| `sceneN1` | no far-range hazard at all (hard negative / out-of-FOV) — a far camera would add frames with nothing to see |
| `sceneN2` | no far-range hazard at all (hard negative / out-of-FOV) — a far camera would add frames with nothing to see |
| `sceneN4` | no far-range hazard at all (hard negative / out-of-FOV) — a far camera would add frames with nothing to see |
| `sceneN5` | no far-range hazard at all (hard negative / out-of-FOV) — a far camera would add frames with nothing to see |

> Test-side E-boost targets are fixed by the brief ({05,07,15,18}+s14) and are not re-derived here; this table is the TRAIN half D19③ asked for. For the record the same measurement on those test scenes reads: `scene05` near-miss 21/24; `scene07` near-miss 0/24; `scene15` near-miss 21/24; `scene18` near-miss 3/24; `scene14` near-miss 21/24 — s05/s14/s15 are strongly convertible, s07 and s18 much less so.

## 7. what changed in the labeling stack

- `gridspec_v1.json` — new, 4 bands × 5 sectors, `cell_index = band*5+sector`, `hazard_depth_m 0.3`, positive rule unchanged, plus a `nested_in` field the tests read to check the refinement law.
- `labeler.py` — `n_cells(grid)` is now the only place a cell count is computed; `grid_slug`/`gt_source_of` derive the provenance string from the gridspec, so V1 labels are stamped `derived-heightmapdiff-gridv1-PROVISIONAL` (the V0 spelling is reproduced byte for byte, asserted in the test suite). `meta.n_cells` added.
- `build_manifest.py` — reads gt_source / tier_source / gate_policy / n_cells back from the labels file instead of re-declaring them, and refuses a labels file whose `polar_gt` length disagrees with its own gridspec.
- `gates.py` — report header and a new `n_cells` cross-check follow the gridspec (a mismatch between `--grid` and the manifest is now a hard error, not a silently wrong report); G1 additionally rejects a frame whose `polar_gt` is the wrong length.
- `gates.py` **D19⑤ verdict reform** — G5 is a REFERENCE metric, excluded from pass/fail and reported per band; G2's zero-positive failure list skips scenes in the new `EXPLAINED_ZERO` table (`scene06`: out-of-FOV, D17), which are printed on their own annotated line; the verdict is recomputed from the binding gates only (G1/G2/G3/G4) and prints a per-gate ledger naming which gates bind.
- `gates.py` **new D19 split-band audit quota** — 4 overlays reserved for frames positive in exactly one of the refined pair (`3a` xor `3b`), the only view that audits the boundary V1 introduced. The `3a`-not-`3b` case is 12 frames in the whole corpus, so without a reserved quota the audit would never show one.
- `gates.py` **bug fixed while adding that quota**: the D12 far-E block did `picks = [...]` where it meant `picks += [...]`. Harmless when far-E was the first quota, but it silently discarded everything reserved before it. Caught because the split-band overlays did not appear on disk while the report claimed 4/4.
- `synth_test.py` — parameterised on `--grid` and run on EVERY gridspec by default (117 checks: 58 on v0, 59 on v1); no cell index or count is a literal any more. The v1 run asserts the fixture pit lands in band `3a` and that `3b` is empty (its farthest corner is 7.62 m), and that folding `3a|3b` back together reproduces the v0 GT exactly.
- No hard-coded 15 remains anywhere in the labeling stack.

Rollback is a json swap: point `--grid` at `gridspec_v0.json` and re-run the same two commands.

