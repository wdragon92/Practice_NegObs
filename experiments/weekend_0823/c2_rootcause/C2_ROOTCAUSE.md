# C2_ROOTCAUSE — why `sceneC2` behaves unlike every other test scene

**Queue item.** CPU-3 of `Docs/campaign/WEEKEND_BRIEF_0823.md` §6.3 (ruling #7 follow-up).
**Author.** Claude Code, 2026-08-23. **Reader.** someone (or some AI) seeing this project for the
first time. **Compute.** CPU only, `env_seg`, `PYTHONNOUSERSITE=1`. **No scene file was edited, no
render was produced, nothing outside this directory was written.**

---

## 0. Purpose, in one line

`sceneC2` is the corpus's designated anomaly — it produced the v1 "confident hallucination"
(a 16 mm surface scored 0.98), it carries **76.1 %** of the Depth arm's v2 off-arm false alarms,
and under the dressing-preserving OFF arm its RGB false-alarm rate jumps to **0.681**. This file
lists, in evidence order, *what is actually different about it* and, for each hypothesis, **which
result decides it**.

## 1. Terms used here (WEEKEND_BRIEF §1 convention)

| term | meaning |
|---|---|
| **구off / 신off** | the two generations of the hazard-OFF twin arm. 구off (`dataset/v2_corpus/260819_main_off`) removes hazard **and** dressing; 신off (`dataset/v2_probes/260820_ctrloff`, `keep_dressing:true`) removes the hazard geometry only. Ledger: `experiments/nightrun_0820/ctrl_dressing/CTRL_TABLE.md`. |
| **FA_frame** | fraction of hazard-OFF frames on which at least one of the 20 grid cells crosses τ = 0.5. Every OFF frame carries an all-zero label, so this is a pure false-alarm rate. |
| **twin Δ (`d_frame`)** | max cell probability on the ON frame − max on its pose-matched OFF twin. |
| **camera pose** | one sampled camera `(round, d, h_rel, yaw, pitch)`. Each pose is rendered under 3 light conditions. |
| **band 1/2/3a/3b** | the grid's distance bands `[0,2)·[2,5)·[5,8)·[8,12)` m (ledger: `diag_v2/DIAG_V2.md`). |

## 2. Inputs

Frozen, read-only: `experiments/dayrun_0820/runs/v2/{rgb,depth,b2}_s{42,43,44}/eval_test/` ·
`…/dataset_manifest_v2_full.json` · `…/split_v2_full.json` · depth sidecars under
`dataset/v2_corpus/260819_main_{on,off}/` and `dataset/v2_probes/260820_ctrloff/` · `heightmap_meta.json` per scene/arm ·
scene sources `scenes/batch1/sceneC2_leaf_stairs.py` etc. · `variation_kit.py` (camera and light
samplers) · `experiments/nightrun_0820/ctrl_dressing/eval_*` (the GPU-1 outputs, see §5) ·
prior ledgers `DIAG_V1.md` §3, `DIAG_V2.md` §3, `CTRL_TABLE.md`.

Reproduce: `conda activate env_seg && PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="" python
experiments/weekend_0823/c2_rootcause/c2_audit.py` (~4 min). Every number below is in
`c2_audit_numbers.json`; the per-frame depth features are in `c2_depth_stats_perframe.csv`.

**Integrity gate.** All quoted control-arm numbers reproduce the frozen v2 evaluation exactly:
max |Δp| over shared on-arm and 구off rows = **0.0** for RGB and Depth on all three seeds
(`ctrl_arm_audit.qc`), and the RGB rows reproduce `CTRL_TABLE.md` §1–§2 to four decimals.

---

## 3. The difference audit — every axis the brief named, measured

### 3.1 Sampling: `sceneC2` is the smallest and the least-replicated test scene

| test scene | ON frames | OFF frames | render rounds | light conditions | **distinct camera poses (OFF)** |
|---|---|---|---|---|---|
| scene05 / 07 / 14 / 15 / 18 | 72 | 72 | 3 | L0 + L5(or L4) + L7 | **24** |
| **sceneC2** | **24** | **24** | **1** | **L2 + L3 + L7** | **8** |
| sceneN3 | 24 | 24 | 1 | L0 + L5 + L7 | 8 |

**And light does not enter the Depth channel at all.** Verified by hashing the sidecars: `sceneC2`'s
24 OFF frames are **8 distinct depth maps, each repeated 3×** (identical bytes); same for `sceneN3`;
`scene05`'s 72 OFF frames are 24 distinct maps. So the whole 408-frame test OFF arm is only
**136 distinct inputs** for the Depth model, of which `sceneC2` supplies **8 (5.9 %)**.

### 3.2 Components, materials, dressing density

From the scene sources (comment lines stripped) and the per-arm `heightmap_meta.json`:

| scene | dressing call sites | dominant dressing | prims ON | prims 구off | prims 신off |
|---|---|---|---|---|---|
| **sceneC2** | **16** (highest of the test set) | `build_leaf_scatter` ×4 · `build_leaf_mound` ×3 · `build_leaf_sections` ×2 · `build_hedge` ×2 | **404** | **279** | **388** |
| scene07 | 14 | trees ×4, hedges ×3 | 763 | 368 | — |
| scene14 | 12 | trees ×3, benches ×2 | 911 | 431 | — |
| scene05 | 8 | cues ×2, signs ×2 | 1473 | 614 | — |
| scene18 | 4 | cues ×2 | 851 | 803 | — |
| sceneN3 | 3 | planter, bench, sign | 962 | 748 | 962 |
| scene15 | 1 | handrail | 631 | 604 | — |
| *(family controls)* sceneC1 / sceneC4 | 5 / 3 | snow ×2 / cues ×2 | 490 / 778 | 315 / 508 | — |

Reading: `sceneC2` is the **most densely and most narrowly dressed** test scene (leaf-dominated,
16 call sites) while carrying **fewer prims than the corpus median (763)**. "Dressing density" is
therefore an *appearance* property here, not a geometry-count property. All 33 scenes expose the
same six `cue_*` toggles, so the cue vocabulary is not what differs.

### 3.3 Depth statistics — what the Depth model actually sees

Depth input pipeline (`experiments/mainrun_0819/code/polar_dataset.py`): `clip(d, 0, 10 m)/10`.
Sky is `inf` and therefore lands on the **saturated value 1.0**, and **everything in band 3b
`[8,12)` m is at or beyond the clip.** Per-scene means over the *distinct* depth maps:

| scene_arm | n distinct | inf frac | saturated frac | mean (norm) | **vgrad p99** | **hgrad mean** |
|---|---|---|---|---|---|---|
| sceneC2_on | 8 | 0.040 | 0.513 | 0.659 | **4.287** | **0.1433** |
| sceneC2_구off | 8 | 0.039 | 0.341 | 0.567 | 0.904 | 0.0275 |
| sceneC2_**신off** | 8 | — | — | 0.569 | **1.252** | **0.0822** |
| scene05_off | 24 | 0.069 | 0.394 | 0.633 | 0.928 | 0.0156 |
| scene07_off | 24 | 0.002 | 0.403 | 0.645 | 0.436 | 0.0011 |
| scene14_off | 24 | 0.172 | 0.396 | 0.629 | 0.475 | 0.0010 |
| scene15_off | 24 | 0.002 | 0.036 | 0.282 | 0.367 | 0.0357 |
| scene18_off | 24 | 0.232 | 0.380 | 0.600 | 0.535 | 0.0013 |
| sceneN3_off | 8 | 0.000 | 0.313 | 0.543 | 0.572 | 0.0131 |

(`vgrad`/`hgrad` = mean absolute vertical / horizontal first difference of the clipped, normalised
depth map on an 8× decimated grid — a scale-free measure of how much depth *structure*, as opposed
to a smooth receding plane, the frame contains.)

Two facts stand out.

1. **`sceneC2` has by far the largest ON→OFF change in depth structure of any test scene**:
   `vgrad_p99` 4.287 → 0.904 (**×0.21**) and `hgrad` 0.143 → 0.028 (**×0.19**). No other test
   scene changes by more than ×1.7 in either direction; `sceneN3`'s two arms are byte-identical.
   This is the depth-channel measurement of the defect `DIAG_V1.md` §3.1 described in words — the
   C2 toggle is not appearance-preserving, and it is not depth-preserving either.
2. **`sceneC2`'s OFF arm still has the second-highest lateral depth structure of the seven test OFF
   arms** (`hgrad` 0.0275, behind `scene15`'s 0.0357 and 25× `scene14`'s 0.0010) — the surviving
   near-field leaf scatter plus the far dressing that sinks but does not disappear.

### 3.4 Camera presets and h0.3 visibility

| scene | h_rel range (mean) | frac h < 0.6 m | d range | tiers of the ON frames |
|---|---|---|---|---|
| **sceneC2** | 0.31 – 1.70 (0.99) | **0.38** | 1.25 – 8.32 | **V ×24** (the drop is *visible* from all 8 cameras) |
| sceneN3 | 0.26 – 1.39 (0.85) | 0.38 | 1.39 – 9.18 | none_in_fov ×24 |
| scene05 | 0.31 – 1.89 (1.13) | 0.29 | 1.50 – 10.15 | V ×72 |
| scene15 | 0.33 – 0.99 (0.65) | 0.46 | 1.37 – 10.99 | H ×36, H_weak ×6, V ×30 |
| scene18 | 0.25 – 1.88 (0.99) | 0.33 | 1.25 – 11.24 | E ×45, V ×27 |

`sceneC2`'s camera distribution is **not** unusual — its robot-height share (0.38) sits mid-pack,
its standoff range is the shortest but not by much. What *is* unusual is a single camera inside it
(§4, H2). Note also that all 24 C2 ON frames are tier **V**, so `sceneC2` contributes nothing to the
H-tier headline rows — consistent with `DIAG_V2` §2.3.

### 3.5 Illumination — `sceneC2` is the only test scene lit by conditions the model never trained on

`sceneC2` is **season-locked to autumn** (`variation_kit.py: SCENE_REF_COND["sceneC2"] = "L2"`,
because L0's 49.8° sun sits outside the 35–45° autumn band), so it uses **L2** (stratocumulus, its
reference proxy) + **L3** (`autumn_noon`, the catalogue entry written *for* C2's leaf litter) + L7.
Corpus-wide frame counts by condition:

| condition | train | val | test | hold | which scenes use it at all |
|---|---|---|---|---|---|
| **L2** | **0** | 0 | 16 | 0 | **`sceneC2` only** |
| **L3** | **16** | 0 | 16 | 0 | `sceneC2` (test) + `sceneN1` (train) |
| L0 | 480 | 96 | 256 | 64 | most |
| L4 | 32 | 0 | 48 | 0 | `sceneC1`, `scene15` |
| L5 | 496 | 96 | 208 | 64 | most |
| L7 | 512 | 96 | 272 | 64 | most |

So **2 of `sceneC2`'s 3 light conditions are out-of-distribution for the RGB and B2 arms** — L2 has
literally zero training frames. This was not previously on record and it is a corpus-hygiene fact
worth stating regardless of what it explains. **It does not explain C2's behaviour** — see §4 H5,
where it is tested and refuted.

---

## 4. Ranked hypotheses, with evidence status and the discriminating result

Ranked by how much of `sceneC2`'s anomaly each accounts for, given the evidence now in hand.
The IDs below are stable labels, **not** the rank; the rank is this:

| rank | id | one line | status |
|---|---|---|---|
| **1** | **H1** | the 76.1 % concentration is 1–3 camera poses, because light does not enter the depth channel | **CONFIRMED** (counting fact, no experiment can move it) |
| **2** | **H4** | restored dressing is answered as hazard — 77 % of the RGB response, 44 % of the Depth response | **CONFIRMED & quantified**; discriminator #1 (GPU-1) has run |
| **3** | **H3** | Depth fires on OFF frames that still carry lateral depth structure (`hgrad`) | **CONFIRMED**, and it predicted H4's outcome in advance |
| **4** | **H7** | the toggle is not appearance- (or depth-) preserving; `ground_z` drifts | **CONFIRMED**, on record, already mitigated by 신off + D20 |
| **5** | **H2** | far-band evidence starvation at a low camera → the far-band prior speaks | **PARTIAL** — a tail effect at the extreme, **not** a corpus-wide law (discriminator #2, below) |
| **6** | **H6** | dressing density / scene identity as such | supporting context only — refuted as a standalone predictor by `scene15` |
| **7** | **H5** | out-of-distribution illumination (L2 has zero training frames) | **REFUTED** as a cause; kept as a corpus-hygiene caveat |

### H1 — The "76.1 % Depth FA concentration" rests on ≤ 3 distinct inputs. **CONFIRMED (reporting artefact).**

`sceneC2`'s 24 OFF frames are 8 distinct depth maps (§3.1). Localising Depth's OFF-arm firing to the
camera pose:

| Depth, 구off | s42 | s43 | s44 |
|---|---|---|---|
| `sceneC2` poses firing / 8 | **3** (`0001`,`0002`,`0005`) | **1** (`0005`) | **3** (`0001`,`0002`,`0005`) |
| C2 cells fired | 24 | 27 | 96 |
| **all-test Depth cells fired (408 OFF frames, 136 distinct inputs)** | 36 | **27** | 156 |
| **C2 share** | 66.7 % | **100 %** | 61.5 % |

On **seed 43 the Depth arm's entire test-set false-alarm budget is one camera pose in `sceneC2`**,
counted three times because three light conditions share one depth map. The published 76.1 % is
arithmetically correct and it is the 3-seed mean of the last row — but it describes **one to three
camera geometries**, not a scene-wide property.

**Discriminator: already resolved — no experiment can change it, it is a counting fact.**
**Action:** report Depth OFF-arm FA at the distinct-input level alongside the frame level, and add
the pose count to the caveat sentence. If a scene-level claim about C2 is wanted, C2 needs more
render rounds (probe **P-C2-C**, §6).

### H2 — Far-band evidence starvation at a low camera: the one pose that always fires is the most far-starved input in the test set. **PARTIAL — a tail effect, not a corpus-wide law.**

Ranking all **136 distinct OFF-arm depth inputs** by the fraction of pixels falling in bands 3a+3b:

| rank | scene | cam | h_rel | d | far-band pixel share | band-1 share | fires (Depth)? |
|---|---|---|---|---|---|---|---|
| **1 / 136** | **`sceneC2`** | **0005** | **0.310 m** | 4.55 m | **0.0261** | 0.673 | **YES, all 3 seeds** |
| 2 | scene15 | 0001 | 0.48 | 1.86 | 0.0357 | 0.674 | no |
| 3 | scene15 | 0003 | 0.99 | 1.37 | 0.0406 | 0.604 | no |
| 4 | scene18 | 0006 | 0.25 | 5.96 | 0.0424 | 0.621 | no |
| … | | | | | | | |
| 78 / 102 | `sceneC2` | 0001 / 0002 | 1.02 / 1.43 | 6.86 / 8.32 | 0.163 / 0.258 | | YES (2 of 3 seeds) |

Cam `0005` sits at the **robot eye height (h = 0.310 m)** with pitch −13.9°, so 67 % of its pixels
are inside 2 m and only **2.6 % of the frame lies in bands 3a+3b** — and that is exactly where it
fires, at p = 0.980 / 0.998 / 0.988 across seeds, lighting up 4 → 9 → 15 cells. With almost no pixel
evidence in the far cells the head falls back on the far-band prior, which `DIAG_V2` §1 measured at
ρ̄ = **+0.848** against the train prior. `sceneC2` *as a scene* is not far-starved (mean far share
0.179, mid-pack); **one camera in it is the extreme of the whole test set.**

**Discriminator #2, run here (zero cost): the corpus-wide version of the claim FAILS.** Over all
136 distinct OFF inputs, Spearman ρ between far-band pixel share and the 3-seed mean max probability
over the ten far cells is **−0.077 (permutation p = 0.375)** for Depth, −0.074 for RGB, +0.101 for
B2 — no monotone relation. What survives is a **tail** effect:

| far-band pixel-share decile group | n | mean max far-cell p (Depth) | inputs with p ≥ 0.5 |
|---|---|---|---|
| **bottom 10 (most starved)** | 10 | **0.239** (0.158 with C2 `0005` excluded) | 1 |
| ranks 11–30 | 20 | 0.076 | 0 |
| ranks 31–105 | 75 | 0.076 | 1 |
| top 31 (most far-rich) | 31 | 0.057 | 0 |

So far-band starvation elevates the far-cell response **only in the extreme tail**, roughly 2–3×,
and 5 of the 10 tail members are `scene15` (a walled alley, near-field by construction) — i.e. the
tail is itself confounded with scene. **Reading:** H2 is a real but small effect that explains *why
cam `0005` is the one pose that fires on every seed*, and it is **not** a general law about the grid.
It should be reported as an observation about the worst case, not as a mechanism.
**Remaining render discriminator:** probe **P-C2-A** (§6) — a camera-height sweep inside C2 with the
scene untouched, which would say whether `0005` is a reproducible viewpoint class or one draw.

### H3 — Residual lateral depth structure in the OFF arm predicts Depth firing corpus-wide. **CONFIRMED, and it predicted §5 in advance.**

Pooling all 136 distinct OFF inputs and splitting them by whether the Depth model fires
(5 fire: 3 × `sceneC2`, 2 × `scene15`; 131 quiet), the strongest separating feature by a wide margin
is the **mean horizontal depth gradient**:

| feature | firing inputs | quiet inputs | Cohen's d |
|---|---|---|---|
| **`hgrad_mean`** | **0.043** | **0.011** | **+1.98** |
| `vgrad_p99` | 1.049 | 0.552 | +0.94 |
| `frac_band2` (pixels 2–5 m) | 0.403 | 0.304 | +0.92 |
| `sat_frac` (pixels at/over the 10 m clip) | 0.197 | 0.327 | −0.77 |
| `inf_frac` (sky) | 0.010 | 0.089 | −0.75 |

The Depth model false-alarms on OFF frames that still contain **lateral depth structure at mid
range**, and is quiet on frames dominated by saturated far depth and sky. `sceneC2`'s 구off arm has
`hgrad` 0.0275 — second-highest of the seven OFF arms — because the leaf scatter survives in the
near field and the far dressing sinks without vanishing (`DIAG_V1` §3.1).

**This hypothesis made a prediction before §5 was read**: the 신off render restores the leaf mound
and railing, so its `hgrad` should rise and its FA with it. Measured: `hgrad` **0.0275 → 0.0822**
(×3.0) and Depth FA **0.292 → 0.667** (§5). Prediction held.

### H4 — Dressing read as hazard ("가드 어휘 = 낙차"). **CONFIRMED and quantified — discriminator #1 has already run.**

The brief names GPU-1 (Depth 신off evaluation) as discriminator #1. **Its outputs already exist**
(`experiments/nightrun_0820/ctrl_dressing/eval_new_depth_s4{2,3,4}` and `twin_new_depth_s4*`,
written 2026-08-23 03:16) and pass the integrity gate (§2). Result:

| `sceneC2` | arm | RGB | **Depth** |
|---|---|---|---|
| FA_frame (3-seed ± half-range) | 구off | 0.069 ± 0.104 | **0.292 ± 0.125** |
| | **신off** | **0.681 ± 0.208** | **0.667 ± 0.125** |
| camera poses firing / 8, per seed | 구off | 2 / 0 / 0 | **3 / 1 / 3** |
| | **신off** | 4 / 5 / 8 | **6 / 4 / 6** |
| twin Δ `d_frame` (3-seed) | 구off | +0.699 ± 0.204 | **+0.554 ± 0.253** |
| | **신off** | +0.163 ± 0.062 | **+0.308 ± 0.158** |
| **dressing share of the response** = 1 − 신off/구off | | **76.7 %** | **44.4 %** |

Three readings, in increasing order of usefulness.

1. Literal, per the brief's rule ("신off에서 FA 잔존 → 기하/렌더 요인"): **Depth FA does not vanish
   — it more than doubles.** So a geometry/render factor is present.
2. **Correction the brief's rule needs.** For a *depth* input, "dressing" **is** geometry: the leaf
   mound is a real +0.084…+0.20 m relief and the railing is a real solid. So "FA survives ⇒
   geometry, not dressing" is not a valid inference on the Depth arm — both hypotheses predict
   survival. The rule is sound for RGB (where dressing is appearance) and must be restated for Depth.
3. **The statistic that does discriminate: which camera poses are recruited.** 구off fires on
   `{0001, 0002, 0005}`; 신off fires on those **plus** `{0004, 0006, 0007}` (and `0003` on s43).
   So for Depth the response splits roughly in half — **~3 poses fire on the bare flattened
   geometry alone (render/scene factor, H2+H3) and ~3 more are recruited only when the dressing is
   restored (dressing factor)**. The twin-Δ ratio agrees: **44 % of the Depth response is
   dressing-attributable against 77 % for RGB.** In plain terms: *the RGB arm's C2 problem is
   mostly a shortcut on autumn dressing; the Depth arm's is roughly half a shortcut on the dressing
   as 3-D relief (an ≤0.20 m mound read as a ≥0.30 m drop — a **severity/sign confusion**) and half
   a response to the bare render itself.*

### H5 — Out-of-distribution illumination (L2 has zero training frames). **REFUTED as a cause; retained as a corpus-hygiene caveat.**

Discriminator run here (zero cost): split C2's OFF-arm FA by light condition. Because all three
conditions share the same 8 camera poses, this is a within-pose comparison.

| `sceneC2` OFF FA by condition | L2 (**0** train frames) | L3 (16 train frames) | L7 (512 train frames) |
|---|---|---|---|
| RGB, 구off (frozen v2 test) | 0.042 | 0.083 | 0.083 |
| RGB, 신off | 0.667 | 0.667 | 0.708 |
| B2, 구off | 0.375 | 0.375 | 0.458 |
| Depth (light-invariant by construction) | 0.292 | 0.292 | 0.292 |

**The never-seen condition behaves like the fully-trained one**, in both arms and both OFF
generations. Illumination novelty is therefore not the driver. **Keep it as a stated limitation**
(“16 of the 816 test frames — 8 hazard-on and 8 hazard-off, all in `sceneC2` — are lit by a sky
condition that appears in **zero** training frames; a further 16 use a condition seen in 16 training
frames”) and, if the corpus is ever re-rendered, give `sceneC2` an in-distribution third condition.

### H6 — Dressing density / scene identity as such. **SUPPORTING CONTEXT, not a standalone cause.**

C2 leads the test set on dressing call sites (16, §3.2) and is the corpus's extreme case of *cue
burial* (`DIAG_V1` §3.1: leaf mound crest **+0.084 m at x = 0**, above the approach plane, erasing
the stair's start edge; only one diagonal railing line survives). It is genuinely the scene whose
identity is most concentrated in one dressing family. But dressing density does not by itself
predict false alarms: `scene15`, with **one** dressing call site, is the RGB arm's **largest** FA
source in v2 (frame FA 0.699, 33.4 % of all RGB fires). The causal variable is what the dressing
does to the *input signal* (H3 for Depth, appearance co-occurrence for RGB), not how much of it
there is.

### H7 — The non-appearance-preserving toggle and the `ground_z` drift. **CONFIRMED, on record, already mitigated.**

`DIAG_V1` §3.1/§3.3: the C2 hazard toggle deletes the leaf mound and railing along with the stair,
and moves the ground under the camera (`ground_z` differs on 24/24 cuts, by 0.0164 m or 0.1137 m),
which excluded C2 from v1's twin analysis entirely. Mitigations already applied: the D20 `≤0.15 m`
tolerance (v2 recovers all 24 pairs) and the 신off render (`keep_dressing`). §3.3 adds the depth
measurement of the same defect (ON→OFF `vgrad_p99` ×0.21, the largest change in the test set), and
§5 shows the 신off arm restores **388 of the ON arm's 404 prims** — the toggle is now near
appearance-preserving in *both* channels. **Residual caveat:** even 신off keeps a `ground_z` offset,
so C2's twin pairs still live under the tolerance layer, not exact pose equality.

### Not a hypothesis, but the fact that reframes the caveat

For **RGB**, `sceneC2` is *no longer* the FA problem at v2: frame FA 0.875 → **0.069**, cell share
47.8 % → **0.5 %**, and **two of three seeds never fire on it at all** (`DIAG_V2` §3.2). The live C2
caveats are (i) the **Depth** concentration, which §4 H1 shows is 1–3 camera poses, and (ii) the
**신off** rates for both arms, which are a statement about dressing, not about C2's geometry.

---

## 5. Discriminator status board — what each pending result would decide

| # | result | status | what it discriminates |
|---|---|---|---|
| 1 | **GPU-1 · Depth 신off evaluation** | **DONE** — outputs present and gate-clean (§4 H4) | H4 vs H2/H3: gives the 44 % / 77 % dressing split and the pose-recruitment table. **Brief's binary reading must be restated for the Depth arm** (dressing = geometry there). |
| 2 | far-band pixel-share regression over the 136 distinct OFF inputs | **DONE** (§4 H2) | H2: **answered — no corpus-wide relation** (ρ = −0.077, p = 0.375); only a 2–3× tail effect, itself confounded with `scene15`. H2 downgraded to an observation about the worst case. |
| 3 | probe **P-C2-A** (camera-height sweep, §6) | conditional | H2 vs H1: is cam `0005` reproducible as a *class* of viewpoint, or a single unlucky draw? |
| 4 | probe **P-C2-B** (element-wise dressing toggles, §6) | conditional | inside H3/H4: **which** element — leaf mound, leaf scatter, railing, sunk far dressing — carries the response. |
| 5 | probe **P-C2-C** (2 extra render rounds for C2/N3) | conditional | H1: turns an 8-pose statistic into a 24-pose statistic, at which point a scene-level claim about C2 becomes sayable. |
| 6 | CUE-OFF contrast (GPU-2, brief §6.2) on a non-C2 scene | queued elsewhere | whether the "dressing recruits false alarms" mechanism generalises beyond C2/N3. |

## 6. Probe specs (element-wise, isolated) — **conditional; none is needed for the §4 conclusions**

All three are **diagnostic-only**, evaluation-only, frozen checkpoints, zero re-training, and are
rendered into **new isolated round directories**; the canonical scene file is **not edited**
(WEEKEND_BRIEF §3-2, §6.3). `sceneC2` is a **test** scene, so nothing produced here may enter the
main table, the τ decision, or model selection. Every probe requires the standard gates: **1-frame
real-render smoke first** (§3-6), `ground_z` parity check per cut (the `DIAG_V1` §3.3 failure mode),
and a hazard-geometry invariance hash against the frozen arm.

**P-C2-A · viewpoint sweep (tests H2).** Scene `sceneC2`, geometry frozen at the 구off
configuration (`{"hazard_stairs": false}`). Cameras on a grid `h_rel ∈ {0.30, 0.45, 0.60, 0.90,
1.30, 1.70}` × `d ∈ {3.0, 4.5, 6.0, 8.0}` = 24 poses, pitch fixed at the corpus mean (−12.5°), yaw 0.
One light condition is enough (**L7**, the in-distribution one) because the Depth arm is
light-invariant. **48 frames** (24 poses × 1 cond × {구off, 신off}); ≤ 96 with a second condition
for the RGB arm. Read-out: Depth FA and max-p as a function of far-band pixel share. Decides whether
cam `0005` is a reproducible viewpoint class.

**P-C2-B · element-wise dressing toggles (tests H3/H4, isolates *which* element).** Scene `sceneC2`,
hazard off, cameras **fixed to the existing 8 corpus poses** so the result is directly comparable to
§4 H4. Five arms, one element added at a time on top of 구off:
`{+leaf_mound}`, `{+leaf_scatter}`, `{+railing}`, `{+far dressing at true z}`, `{all = 신off}`.
**8 poses × 3 conds × 5 arms = 120 frames** (or 40 with L7 only for the Depth arm). Read-out: FA
and the pose-recruitment set per element. This is the only experiment that names the culprit object
rather than "the dressing". *Implementation note:* the toggles must be added as **new render
configs**, i.e. `build_leaf_mound` / `build_cues` moved out of the `hazard_stairs` branch behind
independent flags in an **isolated copy** of the scene module — the canonical
`scenes/batch1/sceneC2_leaf_stairs.py` stays untouched, and the change is logged in a 변경 대장.

**P-C2-C · sample repair (tests H1).** Two additional render rounds for `sceneC2` (and `sceneN3`)
with fresh camera draws, matching the boost rounds' recipe: **+16 poses × 3 conds × 2 arms = 96
frames per scene**. This is the only way the 76.1 % number becomes a scene-level statement rather
than a 1–3-pose one. **Caution:** these are test scenes; adding frames changes the test denominator,
so the output must be reported as a **separate diagnostic set**, never merged into the frozen v2
test corpus (WEEKEND_BRIEF §3-1, §3-2).

**Priority if GPU time exists:** P-C2-B (names the object, feeds the paper's limitation sentence
directly) > P-C2-A (cheap, decides a grid-level caveat) > P-C2-C (largest, and it perturbs the
test-set bookkeeping).

## 7. Recommended wording for the paper (Claude 예비 판정 — decision is 승용's)

Ruling #2 and #7 place the 신off FA and the Depth-C2 hallucination in the limitations section. §4
lets those sentences be written with real mechanism instead of a shrug. Proposed:

> **Limitation (Depth false alarms).** The Depth arm's residual false-alarm rate (0.042 over 408
> hazard-off test frames) is concentrated in one scene, `sceneC2` (76.1 % of fired cells). That
> concentration is narrower than it looks: because the depth channel is invariant to illumination,
> `sceneC2`'s 24 hazard-off frames are only **8 distinct inputs**, and the fires come from **one to
> three camera poses** — on one seed of three, a single pose accounts for the model's entire
> test-set false-alarm budget. The pose that fires on every seed is the most far-band-starved input
> in the test set — 2.6 % of its pixels fall in the two bands it fires on — so at least in the worst
> case the response is the far-band prior speaking where there is no evidence, rather than a misread
> of a surface. (Across the test set as a whole, far-band pixel share does not predict far-cell
> firing, ρ = −0.08; the effect appears only in the extreme tail.)
>
> **Limitation (dressing as a shortcut).** With a dressing-preserving hazard-off arm — hazard
> geometry removed, leaf mound and railing kept — false alarms rise on both arms: RGB 0.069 →
> **0.681**, Depth 0.292 → **0.667**. Comparing the twin Δ across the two off arms attributes
> **77 % of the RGB response and 44 % of the Depth response to the dressing alone**. For the RGB
> arm this is appearance shortcutting; for the Depth arm it is a severity confusion, since the
> retained dressing is real relief of ≤ 0.20 m being answered as a ≥ 0.30 m drop.

**무응답 시 기본값.** Adopt both paragraphs; run no C2 probe; do not modify `sceneC2` this cycle
(the 신off render already supplies the appearance-preserving control the v1 report asked for).

## 8. Files written by this track

| file | content |
|---|---|
| `experiments/weekend_0823/c2_rootcause/c2_audit.py` | the audit (read-only over frozen artefacts) |
| `experiments/weekend_0823/c2_rootcause/c2_audit_numbers.json` | every number quoted above |
| `experiments/weekend_0823/c2_rootcause/c2_depth_stats_perframe.csv` | per-distinct-input depth features for all 7 test scenes × 2 arms (272 rows) |
| `experiments/weekend_0823/c2_rootcause/C2_ROOTCAUSE.md` | this file |

## 9. Next actions

1. Fold §7's two paragraphs into `RESULTS_DRAFT.md` limitations **pending 결재**.
2. Tell the orchestrator that **GPU-1 is already complete and gate-clean**, and that the brief's
   §6.3 discriminator wording needs the §4 H4-(2) correction for the Depth arm (for a depth input,
   dressing *is* geometry, so "FA survives ⇒ geometry factor" does not discriminate).
3. Extend `CTRL_TABLE.md` with the Depth rows (§4 H4) — that is the orchestrator's GPU-1 deliverable;
   the numbers here are ready to paste and reproduce the RGB rows exactly.
4. No `sceneC2` edit is proposed this cycle. If one is later approved, it should be the
   element-separation refactor that **P-C2-B** (§6) needs — moving `build_leaf_mound` and
   `build_cues` out of the `hazard_stairs` branch behind independent flags, in an **isolated copy**
   of the scene module, with a 변경 대장 entry. The canonical scene file stays untouched.
