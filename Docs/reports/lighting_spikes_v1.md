# Lighting / camera spike round — measured report v1 (SP-2, SP-3, SP-4, SP-7)

- Date **2026-07-30** · branch `feat/realism-v1` (W2 closed) · Isaac Sim 4.5.0 / Kit 106.5 ·
  RTX 4090 24 GB · host RAM 32 GB · GPU exclusive, sequential, single instance.
- Commissioned by `Docs/briefs/lighting_camera_variation_spec_v1.md` §9. SP-1 (auto-exposure)
  was already settled in `Docs/reports/t0_spike_report_v1.md` §7 — AE is **OFF**.
- Render arm for every GPU spike is **byte-identical to the standing judgement round**
  `260730_w2d_fix`: `NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 NEGOBS_DETAIL_SCALE=2
  NEGOBS_DETAIL_ROUGH_GAIN=0`, `NEGOBS_CAPTURE_MODE=pt`, 1920×1080.
- **No tracked file was modified.** Harness lives in `look_check/_experiments/gates/
  lighting_spikes/_harness/` (gitignored), renders in `look_check/_experiments/gates/
  lighting_spikes/{sp2,sp3,sp4,sp7}/`. Judge presets and scene files untouched.
- Tags: `[measured]` measured this session · `[local]` verified against local files/code ·
  `[calc]` pure arithmetic · `[inferred]` reasoned judgement.

---

## 0. One page

| # | spike | one-line verdict | gate |
|---|---|---|---|
| **SP-2** | azimuth tolerance, 33 scenes × Δaz {0,±10,±20,±35} × h0.3 3 cuts = **693 cuts / 44.2 min** | The spec's S/A/B/C class table is **wrong in both directions** — too loose on 10 scenes, too tight on 7, and **only 1 of its 3 "identity" S scenes behaves like one**. But the criterion it was to be judged by is itself invalid: see §1.3 | **measured, table replaced** |
| **SP-3** | camera-sample rejection rate, **600** samples over 3 scenes (spec asked for 1) | `r_reject` = **2.0 %** worst case, 1.0 % pooled, vs the 25 % redesign threshold — a **12× margin**, and 6× below the spec's own 8–15 % prior. But the stage-1 analytic prefilter fired **once in 600**, and that once was a **false positive** — it is unvalidated, not validated (§4.3) | **GO** — no distribution redesign |
| **SP-4** | HDRI runtime swap cost | **t_swap = 1.4 s** (set 0.001 s + 8 updates), vs the 30 s split threshold. Swapping the sky is **cheaper than moving the camera** | **GO** — runtime loop, no process split |
| **SP-7** | `UsdGeom.Camera` roll / FOV | Works exactly. hFOV error **≤ 0.05°**, roll error **≤ 0.005°**, principal point dead centre. `focalLength` unit convention is a **non-issue** | **GO** |

**The four things that change the implementation design**

1. **`regression_check` v2.1 cannot arbitrate azimuth tolerance** (§1.3). Two of the three codes
   the brief named — OCCL and GRAZE — are *defined* as before/after deltas, and in SP-2 the only
   thing that differs between "before" and "after" is the rotation of two light prims. Every one
   of their firings is therefore a lighting effect **by construction**, and a null control proves
   the metric floor is zero (§1.2). Judged on **absolute readability** instead, **31 of 33 scenes
   tolerate ±35°** (§1.5).
2. **The lighting loop must be inside the boot, and now there is a number for it** (§3.3):
   the 693-cut sweep took 44.2 min in one boot per scene against **145 min** for the same cuts as
   7 separate rounds — a measured **3.3×**. Combined with t_swap = 1.4 s the spec's §6.4 sky
   overhead falls **7×**.
3. **The sky ladder does not exist yet.** 9 of the 15 HDRIs in spec §4.2 are **not in `assets/`**,
   and only `qwantani_noon` has the `cap0.6` lookfix derivative the current default requires
   (§3.4). Procurement + derivative generation is a prerequisite the spec assumes is done.
4. **The data-render budget is ~3× the spec's, and for the opposite reason the spec expected**
   (§5). Every overhead term the spec worried about came in cheaper — `t_swap` 7×, `r_reject` 6×,
   `t_boot` 1.2× — but `t_cut` on the random-camera path measures **2.87 s against an assumed
   0.7 s**, so the 20 k-cut target is a **~15 h** run, not the ~5 h §6.4 projects. Overhead is now
   3 % of the total: there is nothing left to optimise *except* `t_cut`, of which ~1.0 s per cut is
   the capture-flush poll waiting on an async PNG write — a tunable worth ~35 % of the whole run.

---

## 1. SP-2 — azimuth tolerance sweep

### 1.1 Method

`apply_dome_rot(user_off)` — the callback `setup_lighting()` already returns for the GUI `[` `]`
keys — adds `user_off` straight onto `noon_dome_rot + SUN_AZ_OFFSET` and rotates the **dome and
the DistantLight together**, so HDRI and sun stay coherent. That makes it exactly the Δaz knob
(spec §4.1 "A is free") `[local]`.

The harness (`sp2_runner.py`) monkey-patches two `scene_common` entry points in a wrapper process
and then runs the scene file untouched under `runpy`:

- `setup_lighting()` — intercepted only to capture the returned callback;
- `capture_pipeline()` — replaced by a loop that, per Δaz, calls the callback, repoints
  `NEGOBS_CAPTURE_DIR` and delegates to the **original** `capture_pipeline` with the
  `preset_h0.3_*` views only. Views are selected by prefix, not hard-coded: scene19 uses
  d{2, 3.5, 5}, not d{2, 5, 10} `[local]`.

One boot per scene, 7 conditions inside it. 33 scenes × 7 × 3 = **693 cuts, 2651 s (44.2 min)**,
33/33 exit 0 `[measured]`. Renders: `look_check/_experiments/gates/lighting_spikes/sp2/<scene>/
260730_spike_az{p,m}NN/`. Machine output: `.../sp2_analysis/{regr_az*.json, sp2_measured.json}`.

> **Deviation from the brief, declared.** Spec §9 specifies RT for SP-2. PT-fast was used instead,
> because `t0_spike_report_v1.md` §5 measured PT-fast (0.90–0.99 s/cut) **faster than RT warm-up 90**
> (1.03–1.17) with a **3× smaller residual** (meanΔ 1.3 vs 3.0 LSB), and because it is the arm the
> standing baseline `260730_w2d_fix` was rendered on — so the sweep and the baseline are comparable.

### 1.2 Null control — the metric floor is zero

Δaz = 0 was re-rendered in a **fresh process** for 5 scenes (scene02/04/05/07/N1) and compared
against the sweep's own Δaz = 0 arm. 15 cuts `[measured]`:

| metric | null-control range | WARN | FAIL |
|---|---|---|---|
| OCCL `newdark` | **0.0000 % on all 15** | 2.0 | 8.0 |
| OCCL largest blob | **0.000 % on all 15** | 1.5 | 5.0 |
| FRAME `blk_shift` | **0.0 % on all 15** (max block deviation 2.00/255) | 20 | 40 |
| GRAZE `spec` | **−0.02 … 2.36** | 8.0 | 20.0 |
| pixel meanΔ | 0.08 … 3.42 LSB | — | — |

Verdicts: **FAIL 0**, and several cuts correctly raised `UNCHANGED`. So the decision metrics have a
floor of essentially zero under a pure re-render: **every non-zero reading in the sweep is
attributable to the azimuth, not to sampling noise.**

(Side finding: scene04 `h0.3_d2` is the one cut that is not bit-reproducible across processes —
meanΔ 3.42 LSB, 28.3 % of pixels off by >4 LSB, while every other cut sits below 1.2 LSB. It moved
no decision metric, but something in scene04's near field is process-dependent. Worth a look in W3.)

### 1.3 The finding that matters more than the table

**The criterion the brief specified cannot answer the question it was asked.**

Between a Δaz = 0 render and a Δaz = X render, the geometry is *literally identical* — the only
delta in the stage is a rotate op on `/World/DomeLight` and `/World/NoonSun`. Yet:

- **OCCL** is defined as "pixels that were ≥ 60 and are now < 25". That is the definition of a cast
  shadow. It was designed to catch "new geometry swallowed the camera" (`fixlog_W7` §0, 4 recurrences)
  and there is no new geometry here.
- **GRAZE v2.1** measures the horizontal-coherence change of the vertical step field inside the drop
  edge band. A shadow boundary sliding through that band is a full-width horizontal line change.

The clean proof is scene05 `h0.3_d2` at Δaz = +10 `[measured]`:

```
gz_spec 68.1  (FAIL threshold 20)   agree 1.00  (a full-width line changed)
gz_step_b 86.37 -> gz_step_a 86.60  ratio 1.003   <- the drop edge is UNTOUCHED
gz_step_off 26 rows                  <- and the change is 26 rows away from it
```

The drop-row step is unchanged to 0.3 %, and the thing that moved is 26 rows off it (tolerance 4).
This is a shadow edge, reported as suspected concealment at FAIL grade.

v2.1 **already contains** the discrimination that would quiet it — the "edge persistence" gate —
but applies it only to WARN-grade firings ("a FAIL is never demoted"). That rule is right for a
geometry round and wrong for a lighting sweep. This is the STATUS open item *"GRAZE will over-fire
once the render becomes photoreal"* arriving early, on the lighting axis.

Three criteria are therefore reported, not one:

| | criterion | what it actually measures |
|---|---|---|
| **A. literal** | no FAIL in DARK/OCCL/GRAZE vs Δaz = 0 — **exactly as the brief specified** | how much the shadow pattern moved |
| **B. corrected** | as A, but a GRAZE FAIL counts only when it is about the **drop row**: `step_b ≥ 25 and ratio ≤ 0.50` (the line collapsed), or `step_off ≤ 4 and ratio > 1.10` (a line thickened on the drop row). Same constants v2.1 already uses | whether the drop-edge cue itself changed |
| **C. absolute** | the arm's **own** photometry only, no reference: `30 ≤ mean ≤ 235`, `dark ≤ 70 %`, `clip ≤ 1 %` | whether the frame is still judgeable at all |

B keeps the true positives. sceneN1 (`shadow_band`, the canonical identity-is-the-shadow scene)
still fails at every arm with ratio 0.07–0.40 — the drop line genuinely collapses. scene05 at ±20
still fails with step 86.4 → 34.0 (ratio 0.394). Only the off-row shadow motion is quieted.

### 1.4 Measured table — all 33 scenes

Legend: `ok` = arm passes · `ok·D/O/G` = passes with a WARN on that code · **X**`DOG` = FAILs on
those codes · superscript = number of cuts where the GRAZE verdict was **withheld** (frame
photometry moved past the tool's own `GRAZE_PHOTO_DMEAN` guard — absence of evidence, not evidence
of absence). ⚠ marks a scene the spec's allowance is **too loose** for under criterion A.

| scene | tier | spec | **A. literal** | **B. corrected** | **C. absolute** | +10 | -10 | +20 | -20 | +35 | -35 | first fail |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `scene01` campus_stairs | B | ±35 | **±35** | **±35** | ±35 | ok·O | ok | ok·O | ok | ok·O<sup>3</sup> | ok |  |
| `scene02` underpass | B | ±35 | **±10** ⚠ | **±10** | ±35 | ok | ok | **X**G | ok | **X**G | ok | +20: GRAZE |
| `scene03` riverbank | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok | ok·G | ok·G | ok·G |  |
| `scene04` parktrail | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok | ok |  |
| `scene05` amphitheater | B | ±35 | **±0** ⚠ | **±0** | ±35 | **X**G | **X**G | **X**G | **X**G | **X**G<sup>1</sup> | **X**G | -10: GRAZE |
| `scene06` overpass_spiral | A | ±15 | **±20** | **±20** | ±35 | ok·O | ok | ok·O | ok | **X**O<sup>3</sup> | ok | +35: OCCL |
| `scene07` temple_stone_path | A | ±15 | **±0** ⚠ | **±0** | ±35 | ok·O<sup>1</sup> | **X**O | **X**O<sup>1</sup> | **X**O<sup>1</sup> | **X**O<sup>3</sup> | **X**O<sup>1</sup> | -10: OCCL |
| `scene08` sunken_plaza | A | ±15 | **±0** ⚠ | **±35** | ±35 | ok<sup>3</sup> | **X**G<sup>2</sup> | ok<sup>3</sup> | ok<sup>3</sup> | ok<sup>3</sup> | ok·O<sup>3</sup> | -10: GRAZE |
| `scene09` ghat_riverfront | A | ±15 | **±35** | **±35** | ±35 | ok·G | ok·G | ok·G | ok·G | ok·G | ok·G |  |
| `scene10` park_deck_switchback | A | ±15 | **±35** | **±35** | ±35 | ok | ok | ok·O<sup>3</sup> | ok | ok·O<sup>3</sup> | ok |  |
| `scene11` footbridge_stairs | B | ±35 | **±0** ⚠ | **±0** | ±35 | **X**O | ok | **X**O<sup>2</sup> | ok·O | **X**O<sup>3</sup> | ok·O | +10: OCCL |
| `scene12` riverside_deck | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok·O | ok |  |
| `scene13` apartment_parking | B | ±35 | **±0** ⚠ | **±0** | ±35 | ok<sup>2</sup> | **X**OG<sup>1</sup> | ok·O<sup>3</sup> | **X**OG<sup>1</sup> | **X**O<sup>3</sup> | **X**OG<sup>1</sup> | -10: GRAZE, OCCL |
| `scene14` grandstair_illusion | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok·G | ok | ok·G | ok |  |
| `scene15` alley_labyrinth | A | ±15 | **±0** ⚠ | **±0** | ±20 | **X**O | ok·O | **X**O<sup>2</sup> | **X**O | **X**DO<sup>3</sup> | **X**O<sup>3</sup> | +10: OCCL |
| `scene16` canopy_shadow | S | ±0 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok | ok |  |
| `scene17` ramp_pair_hangang | B | ±35 | **±20** ⚠ | **±35** | ±35 | ok | ok·G | ok | ok | **X**G | ok | +35: GRAZE |
| `scene18` wavy_artstair | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok | ok |  |
| `scene19` fan_winder | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok | ok·G | ok·G | ok |  |
| `scene20` diagonal_oblique | B | ±35 | **±20** ⚠ | **±35** | ±35 | ok·G | ok | ok·G | ok·G | **X**G | ok·G | +35: GRAZE |
| `scene21` monumental_selfocclude | A | ±15 | **±0** ⚠ | **±0** | ±35 | ok | **X**O<sup>1</sup> | ok·G | **X**O<sup>1</sup> | ok·OG | **X**O<sup>1</sup> | -10: OCCL |
| `sceneC1` snow_stairs | C | ±free | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok | ok |  |
| `sceneC2` leaf_stairs | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok·O | ok |  |
| `sceneC4` wet_stairs | C | ±free | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok | ok |  |
| `sceneD1` loading_dock | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok·G | ok·G |  |
| `sceneD2` floor_opening | S | ±3 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok | ok |  |
| `sceneD3` drainage_channel | A | ±15 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok | ok |  |
| `sceneD4` subway_platform | C | ±free | **±35** | **±35** | ±0 (n/a) | ok<sup>3</sup> | ok<sup>3</sup> | ok<sup>3</sup> | ok<sup>3</sup> | ok<sup>3</sup> | ok<sup>3</sup> |  |
| `sceneN1` shadow_band | S | ±0 | **±0** | **±0** | ±35 | **X**G | **X**G | **X**G | **X**G | **X**G<sup>1</sup> | **X**G<sup>1</sup> | -10: GRAZE |
| `sceneN2` asphalt_patch | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok | ok |  |
| `sceneN3` trompe_loeil | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok·O | ok |  |
| `sceneN4` downhill_ramp | A | ±15 | **±20** | **±20** | ±35 | ok | ok | ok·G | ok | **X**G | ok | +35: GRAZE |
| `sceneN5` flush_grating | B | ±35 | **±35** | **±35** | ±35 | ok | ok | ok | ok | ok | ok·G |  |

### 1.5 What this says about the spec's class table

Under **criterion A** (the literal instruction), `Δaz_max` distribution over 33 scenes:
`0°: 8 scenes · 10°: 1 · 20°: 4 · 35°: 20`.

- **Spec too loose (measured tighter) — 10 scenes**: scene02, scene05, scene07, scene08, scene11,
  scene13, scene15, scene17, scene20, scene21.
- **Spec too tight (measured wider) — 7 scenes**: scene06, scene09, scene10, **scene16**, **sceneD2**,
  sceneD3, sceneN4.
- **The S tier does not survive.** Of the three scenes the spec calls "azimuth is the scene's
  identity", `scene16 canopy_shadow` (spec ±0) and `sceneD2 floor_opening` (spec ±3) both measure
  **±35 with no firing at any arm**. Only `sceneN1 shadow_band` behaves like an S scene — it fails
  at ±10 already, with a genuine drop-line collapse.
- **The C tier does survive.** sceneC1/C4/D4 pass every arm. sceneD4 (sealed indoor) is the proof
  case: |Δmean| ≤ 0.22 LSB across the whole ±35° range — azimuth has **literally no effect** `[measured]`.

Under **criterion C** (absolute judgeability) the picture is completely different and much simpler:

> **31 of 33 scenes stay judgeable across the full ±35° range.** The two that do not:
> - `scene15 alley_labyrinth` → **±20**. At ±35 the alley loses its raking light: `h0.3_d5` mean
>   110.4 → 42.9, dark 22.9 % → 73.5 % `[measured]`. This is a real physical bound, and it
>   independently vindicates the spec's A-tier rationale for scene15 (its ±15 allowance is safe).
> - `sceneD4 subway_platform` fails the floor at **every** arm including Δaz = 0 (mean ≈ 19,
>   dark ≈ 81 %) — it is below the readability floor at baseline, so this is not an azimuth
>   constraint and is marked `n/a`.

**Recommended replacement class table.** The physically-grounded bound is C; B is the guard for the
drop-edge cue; A should not be used. Merging B and C (the tighter of the two, which is B wherever
they differ):

| class | allowance | scenes | basis |
|---|---|---|---|
| **S** (identity) | **±0** | `sceneN1` | drop line collapses to ratio 0.40 at ±10 `[measured]` |
| **A′** (edge-sensitive) | **±10** | `scene02`, `scene05`, `scene07`, `scene11`, `scene13`, `scene15`, `scene21` | criterion B first-fail at ±10–±20; scene15 additionally bounded by C at ±20 |
| **B′** (standard) | **±20** | `scene06`, `sceneN4` | criterion B first-fail at ±35 |
| **C′** (free to ±35) | **±35** | remaining 23 scenes | no firing under B, judgeable under C |

Two caveats on this table, stated plainly:

1. The sweep grid is {0, 10, 20, 35}. A measured "±10" means *"±10 passed, ±20 failed"* — the true
   bound lies in between and the spec's ±15 for the A tier is **not excluded** by this data for the
   A′ scenes. If ±15 matters, it needs its own arm.
2. `Δaz_max` here is *"the azimuth beyond which the drop-edge cue stops matching the reference"*.
   For the **judge** channel that is the right bound. For the **data** channel it is arguably the
   wrong question: an azimuth at which the edge stops reading is a **hard example**, not an invalid
   one, as long as the label still describes the scene. Recommendation: apply this table to
   `role=judge` and to any `role=data` scene whose *label* depends on the shadow (sceneN1), and let
   the rest of the data channel run the full ±35.

---

## 2. SP-7 — `UsdGeom.Camera` roll and FOV

### 2.1 Method

A controlled lab rather than a production scene (`sp7_camera_lab.py`): bare stage, one DistantLight
travelling +X, five white spheres at **exactly known** world positions on the marker plane 10 m
ahead, at horizontal angles θ ∈ {0, ±10, ±20}°. The projection then *solves for* the rendered hFOV
instead of it being eyeballed:

```
u_k = W/2 · (1 + tan θ_k / tan(hFOV/2))        [calc]
```

Camera pose is authored as a **single matrix xform op** built from an explicit look-at basis, which
removes every question about `rotateXYZ` ordering.

> Measurement correction, disclosed: the first pass segmented every pixel above half the frame
> maximum and so also caught the markers' **specular reflection in the ground plane** (bright pixels
> ran from row 530 down to 972 while the markers sit in rows 536–543). That dragged the centroids
> and produced a spurious 0.8° tilt at roll = 0. The **same PNGs** were re-measured
> (`sp7_remeasure.py`) with band-restricted segmentation, choosing the band anchor by best fit to
> the projection model — an assumption-free selection. No re-render was needed.

### 2.2 Measured — the camera is exact

| roll set | hFOV set | focalLength set | **hFOV measured** | error | **roll measured** | error | fit RMS |
|---|---|---|---|---|---|---|---|
| 0° | 58° | 18.90191 | 57.956° | −0.044° | +0.001° | +0.001° | 0.54 px |
| 0° | 62° | 17.43749 | 61.953° | −0.047° | +0.002° | +0.002° | 0.52 px |
| 0° | 66° | 16.13394 | 65.967° | −0.033° | −0.003° | −0.003° | 0.53 px |
| 3° | 58° | 18.90191 | 58.032° | +0.032° | 3.000° | 0.000° | 0.50 px |
| 3° | 62° | 17.43749 | 62.020° | +0.020° | 2.995° | −0.005° | 0.47 px |
| 3° | 66° | 16.13394 | 66.033° | +0.033° | 2.998° | −0.002° | 0.50 px |

Worst hFOV error **0.047°**, worst roll error **0.005°**, and the centre marker lands at
(959.4, 539.5) in every arm — the principal point is dead centre of the 1920×1080 frame with no
offset `[measured]`.

### 2.3 The viewport really uses our camera

- `vp.camera_path`: `/OmniverseKit_Persp` → `/World/SpikeCam`, read back after assignment `[measured]`.
- Behavioural proof, which the read-back alone would not give: at `focalLength = 30.0` (hFOV 38.5°)
  only **3** of the 5 markers remain in frame, at columns 474.5 / 959.5 / 1444.5. Predicted from
  `u = 960·(1 ± tan10°/tan19.26°)` = 475 / 960 / 1445 `[calc]`. The ±20° markers fall outside because
  `tan 20° = 0.364 > tan 19.26° = 0.349`. The frustum physically narrowed — the default perspective
  camera was not silently in use.

### 2.4 The `focalLength` unit question is a non-issue

Spec §9 flags "confirm the `focalLength` unit convention (1/10 stage unit)". Measured answer `[measured]`:

- `stage metersPerUnit = 1.0`; `focalLength` type `float`; authored `horizontalAperture = 20.955`,
  `verticalAperture = 11.7872` (= 20.955 × 1080/1920).
- `Gf.Camera.GetFieldOfView(FOVHorizontal)` returns **66.000°** for focal 16.1339 / aperture 20.955,
  matching the rendered image to 0.03°.

**FOV depends only on the aperture : focal ratio**, so whatever unit both are nominally in cancels;
no conversion is needed anywhere. The unit would matter only for physical depth of field, and
`fStop = 0.0` / `focusDistance = 0.0` — DoF is off, which is what spec §3.5 requires anyway.

**Implementation lines this licenses** `[calc, verified]`:

```python
cam.CreateHorizontalApertureAttr(20.955)
cam.CreateVerticalApertureAttr(20.955 * 1080/1920)          # = 11.787187
cam.CreateFocalLengthAttr(20.955 / (2*math.tan(math.radians(hfov)/2)))
#   hFOV 62.2 (real IMX219, spec §3.1) -> focalLength 17.36949
```

Spec §3.1's proposed `focalLength = 17.369` for hFOV 62.2° is confirmed correct to 3 decimals.

---

## 3. SP-4 — HDRI runtime swap cost

### 3.1 Method

One boot of `scene04_parktrail`, one fixed sky-heavy view, PT-fast. Per sky the swap was repeated
for each N so that convergence could be measured against that sky's own 120-update soak reference,
with a **control arm** that moves the camera instead of swapping — separating swap-specific cost
from ordinary PT re-accumulation.

### 3.2 Measured

| arm | n=1 | n=2 | n=4 | **n=8** | n=16 | n=32 |
|---|---|---|---|---|---|---|
| **control** (camera move, no swap) — PSNR vs soak | 13.36 | 36.85 | 36.85 | **47.46** | 47.46 | 47.32 |
| L1 `kloofendal_48d` swap | 18.32 | 35.87 | 35.87 | **49.54** | 50.05 | 50.06 |
| L2 `sunflowers` swap | 18.39 | 36.12 | 36.12 | **49.55** | 49.44 | 49.40 |
| L6 `farm_field` swap (lookfix off) | 31.46 | 35.12 | 35.12 | **54.89** | 54.90 | 54.67 |

| cost component | measured | note |
|---|---|---|
| `textureFile.Set()` | **0.0004 – 0.0014 s** | USD authoring is free |
| first update after Set (cold GPU texture load, 74–76 MB EXR) | **0.079 – 0.199 s** | |
| next 7 updates (the standard `PT_FAST` warm-up) | **1.24 – 1.26 s** | |
| **t_swap, derivative cached** | **1.32 – 1.45 s** | = `t_set` + 8 updates (L1 1.32 · L2 1.37 · L6 1.45) |
| `ensure_noon_lookfix()` first call per new sky | **1.97 – 2.00 s** | CPU, one-off, writes an 18 MB derivative |
| `ensure_noon_lookfix()` cached | **0.000 s** | |

### 3.3 Verdict — GO for the runtime loop, by a factor of 21

**t_swap = 1.4 s against a 30 s split threshold.** Swapping the sky is *cheaper* than moving the
camera (control 1.72 s at n=8), which makes sense: a sky swap changes no geometry and so causes no
disocclusion. Convergence plateaus at exactly **n = 8**, the warm-up `PT_FAST` already uses — i.e.
**a swap costs nothing beyond the cut it precedes.**

Spec §6.3's structural decision is confirmed, and SP-2 measured it end-to-end as a by-product
`[measured]`:

| | wall time |
|---|---|
| 693 cuts, 7 lighting conditions **inside one boot per scene** (what SP-2 actually did) | **2651 s (44.2 min)** |
| the same 693 cuts as **7 separate rounds** (33 × 7 boots), at the measured `t_boot` 34.3 s / `t_cut` 1.14 s | **8713 s (145.2 min)** |
| **saving** | **3.29×** — 101 minutes avoided on a 693-cut sweep |

### 3.4 ⚠ Blocker — the sky ladder is not procured

The task brief states the spec's ladder files are in `assets/`. They are not `[local]`. Of the 15
skies in spec §4.2:

| status | count | slugs |
|---|---|---|
| base 4k present | 6 | `qwantani_noon`, `kloofendal_48d_partly_cloudy`, `sunflowers`, `farm_field`, `kloofendal_overcast`, `qwantani_dawn` |
| **absent** | **9** | `kloofendal_43d_clear`, `qwantani_afternoon`, `qwantani_mid_morning`, `kloofendal_38d_partly_cloudy`, `kloofendal_28d_misty`, `qwantani_morning`, `qwantani_late_afternoon`, `syferfontein_18d_clear`, `kloofendal_misty_morning` |

This kills **L3 `autumn_noon`, L4 `winter_noon` and L5 `low_sun`** outright — 3 of the 8 catalogue
conditions have no asset. SP-4 was therefore run on the skies that exist (L1/L2/L6).

Second, subtler: `_SUN_CAP_DEG_DEFAULT` moved to **0.6** in W2, but **only `qwantani_noon` has a
`_lookfix_cap0.6.exr`** — the other three lookfix derivatives on disk are the legacy 1.5° ones
`[local]`. Confirmed live: both L1 and L2 reported `derivative_existed = False` and paid the 2.0 s
generation `[measured]`. Harmless at 2 s each, but it means **every new sky needs its derivative
generated once**, and that must happen *before* a data run rather than inside it, or the first
cut of each condition silently carries a 2 s stall and an 18 MB disk write.

Download recipe is unchanged (spec §4.2, CC0):
`https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/4k/<slug>_4k.exr`

---

## 4. SP-3 — camera-sample rejection rate

### 4.1 Method

200 samples drawn from the spec §3.2 distribution, seeded with the spec §2.4 `var_seed`
(`zlib.crc32`, never `hash()`) on a private `random.Random` so scene assembly's global RNG is
untouched — which also validates that recipe. Camera authored as a `UsdGeom.Camera` with the
matrix convention SP-7 verified, so roll and hFOV are genuinely applied.

Distribution as sampled `[measured, matches spec §3.2]`: `d ~ LogU(1.2, 12)`,
`h ~ U(0.25, 1.90)`, `y ~ N(0, 0.35) ∈ [−0.9, 0.9]`, `yaw ~ N(0, 8°) ∈ [−20, 20]`,
`pitch ~ N(−10°, 4°) ∈ [−20, −2]`, `roll ~ N(0, 1.5°) ∈ [−5, 5]`,
`hFOV ~ N(62.2°, 1.5°) ∈ [58, 66]`.

> The brief writes "pitch N(0, 4°)"; the spec table writes `N(−10°, 4°)` truncated `[−20°, −2°]`.
> Read as the same thing — a N(0, 4°) jitter about the preset −10° — and sampled per the spec table.

**Scene choice, since the spec names none.** SP-3 needs a scene with `_solid_at`/`_obstacle_boxes`
so the generic AABB prefilter can be cross-checked against an exact analytic solid test (spec §3.4
names 5 such scenes: 06, 08, 11, 12, 19). Of those, only **scene06** and **scene08** are CAM-1
standard tier, and scene06's spiral interior is pathologically dark (mean 2.7 per
`regression_check`'s own note), which would bias the image filter. → **scene08 sunken_plaza**.

The spec asks for one scene. **Three were run (600 samples)**, because a single scene cannot
distinguish "the distribution is sound" from "this scene is forgiving":

| arm | scene | why |
|---|---|---|
| primary | `scene08` sunken_plaza | CAM-1 standard, has `_solid_at` → the generic AABB prefilter can be cross-checked against an exact analytic solid test |
| generality | `sceneN2` asphalt_patch | CAM-1 standard, wide open, no walls — the easy end of the range |
| stress | `scene15` alley_labyrinth | **CAM-2 narrow/low.** The CAM-1 distribution is applied deliberately where the spec says it must not be, to see whether the filters catch the mismatch |

**All 200 per scene were rendered**, including the ones stage 1 rejected — the only way to detect a
prefilter that over-rejects.

> Measurement repair, disclosed. scene08's first run used `capture_pipeline`'s 40-update flush poll,
> which is too small for a 200-cut loop that re-authors the camera matrix *and* `focalLength` every
> cut: 35 of 200 records came back `captured=false, img=null`, silently deflating `r_reject` to
> 1.5 %. The files had in fact been written — the async flush merely finished after the poll gave up
> — so all 200 are on disk. Stage 2 is a pure function of the PNG, so the 35 gaps were filled
> **offline** (`sp3_backfill.py`), with no re-render. Two integrity checks: stage 2 re-run on the
> 165 records that already carried a measurement reproduced **all 165 exactly** (0 mismatches), and
> all 200 PNGs are **content-unique** (200/200 distinct md5), so no record was measured against a
> stale or duplicated frame. Corrected `r_reject` = **2.0 %**; one further rejection was hiding in
> the lost 35. The poll budget was raised for the sceneN2/scene15 runs, which captured 200/200.

### 4.2 Measured — 600 samples, 3 scenes

| scene | role | samples | rendered | **stage 1 rejects** | **stage 2 rejects** | **r_reject** | s/cut |
|---|---|---|---|---|---|---|---|
| `scene08` | CAM-1 standard, has `_solid_at` — **primary** | 200 | 200 (35 backfilled offline) | **0** (0.0 %) | **4** (flat_near 4) | **2.0 %** | 3.394 s |
| `sceneN2` | CAM-1 standard, open asphalt — generality | 200 | 200 | **0** (0.0 %) | **0** (—) | **0.0 %** | 2.280 s |
| `scene15` | **CAM-2** narrow/low — stress, wrong-tier on purpose | 200 | 200 | **1** (0.5 %, buried + closed_in) | **1** (flat_near 1) | **1.0 %** | 2.936 s |
| **pooled** | | **600** | **600** | **1** (0.17 %) | **5** (flat_near 5) | **1.0 %** | 2.870 s |

**Every rejection in the round, itemised** `[measured]` — 6 of 600:

| scene | idx | d | h | pitch | stage 1 | stage 2 | `bot_local_std` |
|---|---|---|---|---|---|---|---|
| `scene08` | 8 | **1.34** | 1.08 | −10.2° | pass | `flat_near` | 0.868 |
| `scene08` | 18 | **1.45** | 1.03 | −9.8° | pass | `flat_near` | 0.432 |
| `scene08` | 119 | **1.21** | 1.00 | −13.9° | pass | `flat_near` | 0.116 |
| `scene08` | 152 | **1.49** | 1.06 | −6.2° | pass | `flat_near` | 0.895 |
| `scene15` | 109 | 1.86 | 0.30 | −10.1° | **`buried`+`closed_in`** (near 0.072 m, 4/15 open rays) | **pass** — image fine | 1.601 |
| `scene15` | 163 | 3.18 | 1.78 | −8.7° | pass | `flat_near` | 0.955 |

**Why stage 1 almost never fires — the prefilter's own numbers** `[measured]`

| scene | AABB prims / build | nearest solid to eye (reject < 0.15 m) | ground below eye (reject outside 0.05–3.0 m) | open rays of 15 (reject < 6) | stage-1 time |
|---|---|---|---|---|---|
| `scene08` | 627 / 0.04 s | min **0.251 m** | **0.251 – 1.891 m** | min **7**, median 15 | 0.16 s for 200 |
| `sceneN2` | 575 / 0.03 s | min **0.254 m** | **0.254 – 1.891 m** | min **10**, median 15 | 0.15 s for 200 |
| `scene15` | 423 / 0.07 s | min **0.072 m** | **0.256 – 1.889 m** | min **4**, median 15 | 0.14 s for 200 |

The prefilter costs **0.8 ms per sample** — free. `scene08`'s exact `_solid_at(eye)` returned True
for **0/200**, agreeing with the generic AABB prefilter's 0 burial rejects: the two tests concur
where both exist `[measured]`.

**Image filter distribution** `[measured]` — only one of the three sub-filters is live:

| scene | frame mean (fail < 30) | frame dark % (fail > 70) | frame clip % (fail > 1.0) | near-field local std (fail < 1.0): min / p05 / median |
|---|---|---|---|---|
| `scene08` | 42.8 – 113.8 | max 25.8 | max 0.072 | **0.116** / 1.507 / 3.354 |
| `sceneN2` | 130.1 – 171.2 | max 4.0 | max 0.000 | **1.063** / 5.226 / 6.913 |
| `scene15` | 60.0 – 135.7 | max 60.8 | max 0.000 | **0.955** / 1.522 / 6.624 |

`dark` and `blown` **never fired in 600 samples** and are not close to firing — the nearest approach
is scene15's 60.8 % dark against a 70 % threshold. With AE off and a fixed noon sky this is expected:
exposure does not wander, so photometric rejection has nothing to catch. **`flat_near` is the entire
rejection mechanism.**

**The rejections are a `d_min` effect, not a distribution-wide one** `[measured]`. Binning scene08 by
sampled distance:

| `d` bin | share of `LogU(1.2, 12)` | n | rejected | rate in bin |
|---|---|---|---|---|
| **[1.2, 1.5)** | 9.7 % | 21 | **4** | **19.0 %** |
| [1.5, 2.0) | 14.6 % | 30 | 0 | 0.0 % |
| [2.0, 4.0) | 30.1 % | 57 | 0 | 0.0 % |
| [4.0, 12.0] | 45.6 % | 92 | 0 | 0.0 % |

**All four** of scene08's rejections fall in the nearest 10 % of the distance range. At d ≈ 1.2–1.5 m
with h ≈ 1.0 m and pitch ≈ −10°, the bottom third of the frame is a single smooth plaza slab with no
feature in it. The filter is working correctly; the distribution's lower bound is what generates the
work.

**`r_reject` is as much a property of the threshold as of the distribution** `[measured]`. Recomputing
with `FLAT_STD_MIN` varied and everything else held:

| `FLAT_STD_MIN` | 1.0 (spec) | 1.25 | 1.5 | 2.0 | 3.0 |
|---|---|---|---|---|---|
| `scene08` | **2.0 %** | 2.5 % | 4.5 % | 13.0 % | 39.0 % |
| `sceneN2` | **0.0 %** | 1.0 % | 1.5 % | 2.5 % | 3.5 % |
| `scene15` | **1.0 %** | 1.5 % | 5.5 % | 13.5 % | 16.5 % |

The measured 2.0 % sits on a steep part of that curve: the 25 % gate is comfortably met at the spec's
1.0, would still be met at 2.0, and is **breached at 3.0** on scene08. The number to quote is
"2.0 % **at `FLAT_STD_MIN` = 1.0**", not "2.0 %".

### 4.3 Verdict — GO, with the prefilter marked unvalidated

**`r_reject` = 2.0 % worst case, 1.0 % pooled over 600 samples, against a 25 % redesign
threshold — a 12× margin. No distribution redesign** `[measured]`. Spec §3.2's camera distribution
survives contact with three scenes, including one it was explicitly not designed for.

The spec's own prior was **8–15 %** (§6.2, `[추정]`), and §6.4 budgeted `r_reject = 0.12`. Measured,
it is **6× smaller than the low end of that estimate**. Use **0.02** in the budget.

Three qualifications, in decreasing order of how much they should change anyone's plans.

**1. The analytic prefilter has zero demonstrated true positives — it is unvalidated, not
validated.** Stage 1 fired **exactly once in 600 samples**, and that one firing was a **false
positive**: `scene15` idx109 was flagged `buried` (nearest solid 0.072 m) *and* `closed_in` (4 of 15
open rays), yet its rendered frame passed every image test with `bot_local_std` = 1.601 and mean
63.08 `[measured]`. So the round produced 1 stage-1 firing, 1 stage-1 error, and no evidence
whatsoever that the prefilter catches a genuinely unusable camera.

This is a *sampling* outcome, not a code defect: with `h ≥ 0.25 m`, `d ≥ 1.2 m` and the camera placed
on the −X axis looking in, the distribution essentially never puts the eye inside geometry, so there
was nothing for stage 1 to find. The consequence for the implementation is specific:

- **Keep stage 1** — it costs 0.8 ms/sample, and its purpose is to catch the rare pathological
  placement cheaply, which is worth having even unexercised.
- **Do not credit it in the budget.** `r_reject` is, on this evidence, entirely a stage-2 quantity.
- **Give it a real test before trusting it**, by deliberately sampling into geometry (e.g. `d` down to
  0.3 m, or a scene with interior volume such as scene06's spiral) and confirming it rejects what the
  image filter also rejects. Until that exists, treat `buried`/`closed_in` as unproven and let the
  image filter be the authority — which the measured data supports, since it caught 5 of the 6.
- The one observed disagreement points the same way: where the two disagreed, **the image was right
  and the prefilter was wrong.** A stage-1 rejection should therefore not be final; the cheapest
  correct policy is to render stage-1 rejects anyway (they are ~0.2 % of samples) and let stage 2
  decide.

**2. The rejection is concentrated at `d_min`, which makes it a design choice rather than a defect.**
All 4 of scene08's rejections are in `d ∈ [1.2, 1.5)` — 19 % rejection inside the nearest 10 % of the
range, 0 % everywhere else (§4.2). Two readings, and the project should pick one deliberately:

- *As a filter:* a featureless near field carries no drop-edge cue, so discarding it is right.
- *As a loss of hard examples:* d ≈ 1.2 m is exactly where a negative obstacle is closest and most
  safety-critical, and "the ground ahead is a smooth textureless slab" is a **real** and hard input,
  not a corrupt one. `flat_near` was inherited from `regression_check`, where its job is to detect a
  *rendering* failure, not to curate training data.

Recommendation: apply `flat_near` on the `role=judge` path (where a featureless frame really is
unjudgeable) and **not** on the `role=data` path, where it removes the hardest 2 % of near-range
samples for a reason that does not apply. This costs nothing to implement — it is one flag — and it
is worth deciding now rather than discovering later that the near field is underrepresented.

**3. `r_reject` is threshold-bound.** At `FLAT_STD_MIN` = 3.0 scene08 rejects 39 % and the gate would
fail (§4.2). The measured 2.0 % is valid for the spec's 1.0 and should be re-measured if that constant
is ever retuned. Note also that 1.0 sits *below* sceneN2's observed minimum (1.063) and just below
scene15's (0.955) — for two of the three scenes the threshold is at or under the bottom of the
observed distribution, i.e. it is calibrated to reject almost nothing.

**Cost note.** The data path's `t_cut` measured **2.28 – 3.39 s** across the three scenes (pooled
**2.87 s**), tracking scene complexity — sceneN2 open asphalt cheapest, scene08 sunken_plaza dearest.
§5 uses the pooled figure; the earlier single-scene value of 2.28 s was the cheapest of the three and
understated the budget by 26 %.

---

## 5. Budget constants, rebuilt from measurement

Spec §6.2's unknowns are now measured, and two of its assumed constants are wrong `[measured]`:

| constant | spec | **measured** | source |
|---|---|---|---|
| `t_boot` | 40 s | **34.3 s** | least-squares over the 33 `260730_w2d_fix` scenes (cuts 13–16, sec 33.7–66.5) |
| `t_cut` — **preset** path, PT-fast | 0.7 s | **1.14 s** | same regression. The spec's 0.7 came from a 2-view lab, not a production round |
| `t_cut` — **random-camera data** path | (not in spec) | **2.87 s** (range 2.28–3.39) | SP-3, 600 cuts / 1 722 s over 3 scenes. Tracks scene complexity: sceneN2 2.28 · scene15 2.94 · scene08 3.39 |
| `t_swap` | 10 s `[estimate]` | **1.4 s** | SP-4 |
| `r_reject` | 0.12 `[estimate]` | **0.020** (scene08) / 0.010 (scene15) / **0.000** (sceneN2) | SP-3 |

The data path costs **2.0–3.0× a preset cut**. Part of the gap is not rendering but the capture-flush
poll: all paths do the same 8 accumulation updates (SP-4: 1.24–1.26 s), so on the cheapest scene
(sceneN2, 2.28 s) roughly **1.0 s per cut is waiting for the async PNG write to settle** — a
**tunable**, not a physical cost. The spread above that floor is genuine scene cost.

Spec §6.4 rebuilt with the measured constants (data rows use the pooled `t_cut` = 2.87 s and
`r_reject` = 0.02):

| scenario | N_cut | T_render | T_boot | T_sky | **T_total** | overhead | spec said |
|---|---|---|---|---|---|---|---|
| judge 1 round (preset) | 459 | 0.15 h | 0.31 h | — | **0.46 h** | 68 % | 0.45 h |
| data min (4 cond × 20) | 2 693 | 2.15 h | 0.31 h | 0.05 h | **2.51 h** | 15 % | 1.2 h |
| **data recommended (8 × 40)** | 10 771 | 8.59 h | 0.31 h | 0.10 h | **9.00 h** | 5 % | 3.3 h |
| data 20 k (8 × 68) | 18 311 | 14.60 h | 0.31 h | 0.10 h | **15.02 h** | 3 % | 4.9 h |
| data 20 k + 5× scene instances | 18 311 | 14.60 h | 1.57 h | 0.51 h | **16.68 h** | 12 % | 9.0 h |

Two structural corrections to spec §6:

- **The spec's headline warning is inverted.** §6.4's last row warns that *"overhead is 56 % of the
  total"* when scene instances are multiplied. Measured, it is **12 %** — because `t_swap` is 7×
  cheaper than assumed and `r_reject` **6×** smaller. Instance multiplication is **not** the expensive
  axis, and §6.2's advice to "cut the number of conditions when instances grow" is unnecessary.
- **The binding constraint is `t_cut`, and it is 4.1× worse than the spec assumes for the data
  path** (2.87 vs 0.7). The 20 k target is a **~15 h** run, not a ~5 h run. The single highest-leverage
  optimisation available is the capture-flush poll: ~1.0 s of every cut is spent waiting on the async
  PNG write (measured on the cheapest scene), worth roughly **35 % of the data-render wall time** if
  the write can be awaited rather than polled.

---

## 6. Consequences for the implementation design

1. **Do not gate the lighting round on `regression_check` DARK/OCCL/GRAZE deltas.** (§1.3) They are
   shadow detectors when the sun moves. Concretely, for the implementation:
   - the `role=data` path must not be regression-checked at all (spec B2 already says this — this is
     the measurement that proves it necessary rather than tidy);
   - if a lighting round is ever to be gated automatically, the gate must be **criterion C**
     (absolute readability of the arm) plus **criterion B** (drop-row step ratio), both of which are
     computable from metrics `regression_check` already emits (`after_mean`, `after_dark`,
     `after_clip`, `gz_step_b`, `gz_step_a`, `gz_step_off`).
   - the v2.1 "a FAIL is never demoted" rule should gain a documented exception for lighting-only
     rounds. **Not changed here** — that is an adjudicator revision and carries corpus
     re-calibration, which STATUS has the supervisor holding (item D14).
2. **Replace the §4.5 class table with §1.5's**, and re-run at ±15 if the A tier's exact value
   matters. The two S-tier scenes that measured ±35 (scene16, sceneD2) are the most actionable
   correction: the spec forbids azimuth variation on two scenes that demonstrably tolerate the full
   range, i.e. it is leaving decorrelation on the table for no reason.
3. **Lighting stays an inner runtime loop** (spec §6.3 confirmed, 3.3× measured). No per-condition
   process split. `setup_lighting()` should return `apply_light_cond` alongside `apply_dome_rot`
   exactly as spec §6.3 sketches — the SP-2 harness is a working proof that the callback pattern
   drives condition changes correctly from inside `capture_pipeline`.
4. **The camera work is unblocked and cheap.** SP-7 removes every uncertainty in spec §3.1/D3: the
   matrix-xform look-at + `focalLength` formula is exact to 0.05°, and the viewport binding is
   verified behaviourally. Author it as a single `xformOp:transform`, not as `rotateXYZ`.
5. **No camera-distribution redesign** (§4.3) — `r_reject` 2.0 % against a 25 % gate. Three riders:
   - **The stage-1 analytic prefilter is unvalidated.** It fired once in 600 samples and was wrong
     that once. Keep it (0.8 ms/sample), but do not credit it in the budget, and **render stage-1
     rejects anyway** rather than dropping them — at ~0.2 % of samples that costs nothing and the one
     observed disagreement went the image filter's way. Give it a real test by sampling into geometry
     (`d` → 0.3 m, or scene06's interior) before relying on it.
   - **Decide `flat_near`'s role per channel.** It is the entire rejection mechanism, and it fires
     only at `d ∈ [1.2, 1.5)` — the closest, most safety-critical range. On `role=judge` that is
     correct; on `role=data` it discards the hardest 2 % of near-range samples for a reason imported
     from a render-failure detector. Recommend `judge` only.
   - **Re-measure `r_reject` if `FLAT_STD_MIN` moves.** 2.0 % holds at 1.0; at 3.0 scene08 rejects
     39 % and the gate fails.
6. **Procure the 9 missing skies and pre-generate their `cap0.6` derivatives** before any data run
   (§3.4). This is the only hard blocker in this report.
7. **Two loose threads for W3**, both incidental to these spikes:
   - scene04 `h0.3_d2` is not reproducible across processes (§1.2);
   - **`capture_pipeline`'s 40-update size-stabilisation poll is too small and reports failure
     wrongly — fix before any data run.** In the standing round it yields `ok=false` on 15.7 % of cuts
     (17.2 % of h0.3 cuts) with every PNG decoding fine — the known-harmless case from
     `t0_spike_report_v1.md` §5.3 — but under the tighter SP-3 loop it declared **35 of 200 captures
     failed** when in fact all 35 files were written correctly moments later (proven here: the
     offline backfill measured all 35 and the 165 controls reproduced exactly, §4.1). The poll does
     not distinguish *"slow"* from *"never written"*, and on a 200-cut loop the error rate is 17.5 %.
     Two fixes: raise the budget (done in the SP-3 harness — 150 updates plus a 6-update settle, which
     captured 200/200 on both later scenes), and make `ok=false` mean "absent", not "not yet
     stable". Left as it is, a data run will under-report its own yield by roughly a sixth.

---

## 7. Artefact index (all untracked, under `look_check/_experiments/gates/lighting_spikes/`)

| path | contents |
|---|---|
| `_harness/sp2_runner.py` · `run_sp2.sh` | SP-2 sweep driver (monkey-patch + per-boot Δaz loop) |
| `_harness/sp2_analyse.py` · `sp2_table.py` | criteria A/B/C evaluation and the markdown table |
| `_harness/sp3_runner.py` | SP-3 sampler + 2-stage filter |
| `_harness/sp3_backfill.py` | offline stage-2 backfill of the 35 lost scene08 measurements, with the 165-record self-validation |
| `_harness/sp3_report.py` | SP-3 measured tables |
| `_harness/sp4_runner.py` | SP-4 swap-cost protocol |
| `_harness/sp7_camera_lab.py` · `sp7_remeasure.py` | SP-7 lab and its offline re-measurement |
| `_harness/run_sp347.sh` | SP-7 → SP-3 → SP-4 sequential driver |
| `sp2/<scene>/260730_spike_az{p,m}NN/` | 693 cuts + `manifest.json` (33 scenes × 7 arms) |
| `sp2/<scene>/260730_spike_azp00_null/` | null control, 5 scenes × 3 cuts |
| `sp2_analysis/regr_az*.json` · `sp2_measured.json` | per-arm regression output, measured table |
| `sp3/<scene>/cuts/` · `sp3.json` | 200 random-camera cuts + per-sample records, × 3 scenes (scene08, sceneN2, scene15) |
| `sp4/` · `sp4.json` | swap convergence ladder + timings |
| `sp7/` · `sp7.json` · `sp7_remeasure.json` | 8 lab cuts + solved hFOV/roll |
| `look_check/logs/sp2_azsweep{,_times}.{log,tsv}` · `sp3_*.log` · `sp4.log` · `sp7.log` | render journals |

Reproduction:

```bash
bash look_check/_experiments/gates/lighting_spikes/_harness/run_sp2.sh          # 693 cuts, 44 min
python3 look_check/_experiments/gates/lighting_spikes/_harness/sp2_analyse.py   # criteria A/B/C
python3 look_check/_experiments/gates/lighting_spikes/_harness/sp2_table.py     # report table
bash look_check/_experiments/gates/lighting_spikes/_harness/run_sp347.sh all    # SP-7, SP-3, SP-4
python3 look_check/_experiments/gates/lighting_spikes/_harness/sp3_backfill.py  # offline, idempotent
python3 look_check/_experiments/gates/lighting_spikes/_harness/sp3_report.py    # SP-3 tables
```

`sp3_backfill.py` is idempotent and re-validating: on an already-complete `sp3.json` it re-measures
every record, reports 0 mismatches and writes nothing.
