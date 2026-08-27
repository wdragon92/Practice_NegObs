# Lighting / camera round — implementation + validation report v1

- Date **2026-07-30** · branch `feat/realism-v1` · commits `3136ad4` (implementation),
  `f010400` (validation) · Isaac Sim 4.5.0 / Kit 106.5 · RTX 4090 24 GB · GPU exclusive,
  sequential, single instance · `NEGOBS_PT_FAST=1`.
- Commissioned by `Docs/briefs/lighting_camera_variation_spec_v1.md` (design D1-D9). Every
  hypothesis of that spec that `Docs/reports/lighting_spikes_v1.md` measured is taken from the
  **measured** table, and where the two disagree the disagreement is stated rather than smoothed.
- Tags: `[measured]` measured this session · `[calc]` pure arithmetic · `[local]` verified against
  local files/code · `[unmeasured]` carried forward without measurement, labelled as such.

---

## 0. One page

| # | item | state |
|---|---|---|
| **1** | render-role split, judge frozen by exception | **done** — gate fires before Isaac boots, proven live |
| **2** | per-scene azimuth ledger = SP-2 measured | **done** — 33 scenes, two allowances per scene, provenance per row |
| **3** | 8-condition catalogue + physical intensity model + in-process HDRI swap | **done** — computed, not transcribed; reproduces the spec's dome table to **0.29 %** |
| **4** | camera sampler, stage-1 prefilter demoted, `flat_near` per channel | **done** — ground-relative height error **0.0000 m** over 72 cuts |
| **5** | data-run driver, seed ledger, manifest, resumable, measured budget | **done** — `scripts/run_data_render.py` |
| **6** | judge presets bit-frozen; `geom_invariance` + R-5 still pass | **done** — regression v2.1 **FAIL 0** on 52 cuts, noise floor only |
| **V** | mini data-run validation, 72 cuts | **PASS** — after the validator caught 2 real bugs |
| — | **GO / NO-GO for full data production** | **GO, with 3 conditions** (§8) |

**The blocker the spikes raised is cleared.** `lighting_spikes_v1.md` §3.4 reported "the sky ladder
is not procured — 9 of 15 absent, this is the only hard blocker". The 8-condition catalogue in spec
§4.3 binds only **8** of those 15 skies, of which 3 were missing; all 3 are now procured (237 MB,
CC0) and their `cap0.6` lookfix derivatives pre-generated. The other 6 absent skies are ladder
alternatives that no condition binds.

**Four things this round found that neither the spec nor the spikes had.**

1. **`L0` is inadmissible on the two season-locked scenes** (§3.4). The spec mandates both "L0: all
   33 scenes, the judge reference" and "sceneC1 snow locked to elev ≤ 32, sceneC2 leaf to 35-45".
   L0's sun is at 49.83°, in neither band. The scenes were already saying so — C1 runs 28.0 and C2
   runs 42.0 and neither ever used 49.79 — so each gets its own reference condition
   (`ref_cond_for()`: C1 → L4, C2 → L2). Using L0 blindly drops two scenes from the reference arm
   **silently**.
2. **A sunless condition does not make azimuth free** (§7.1). Caught by the validator on real
   renders: spec §4.6's readability floor puts a widened 4° soft sun back, so overcast still casts
   soft shadows, and the first implementation let |Δaz| reach 34° on `sceneN1` — the one scene whose
   *label is the shadow band*. Only the three scenes SP-2 measured as azimuth-insensitive earn the
   bypass.
3. **"A darker condition has a lower frame mean" is physically false** (§7.2), and this run
   disproved it: `sceneN1`'s ground mean *rises* 160.4 → 206.4 under overcast despite overcast being
   0.86 EV darker, because half its ground is deliberately in cast shadow and overcast removes the
   shadow. The frame mean also mixes in sky, and an overcast sky is brighter than a clear one
   (measured `Esky` 4.05 vs 0.52). The exposure gate now asserts the two signatures that *are* sound.
4. **L5 low-sun cannot be honest inside the ledger's measured range** (§3.3). Seoul's noon altitude
   floor is 29.0°, so a 19.08° sun needs |Δaz| ≥ 36.9° — just past the sweep's widest arm (35°). The
   data channel is allowed to extrapolate to 60° for exactly those conditions, and not for scenes
   where criterion C bound (`scene15`) or where the label is the shadow (`sceneN1`), which is why
   `sceneN1 × L5` is refused rather than fudged.

---

## 1. Judge freeze — the proof, with numbers

Round `260730_lcfreeze_pre` / `_post`: the same 4 scenes rendered twice on a **byte-identical arm**
to the standing round `260730_w2d_fix` (`NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1 NEGOBS_DETAIL_SCALE=2
NEGOBS_DETAIL_ROUGH_GAIN=0`, `CAPTURE_MODE=pt`, 1920×1080), once before the implementation landed and
once after. 4 scenes × 13 views = **52 cuts** per arm, 33/33 exit 0.

`scripts/regression_check.py` v2.1, pre → post `[measured]`:

| | result |
|---|---|
| **verdicts** | **FAIL 0** · WARN 14 · INFO 11 · PASS 27 |
| every WARN | `UNCHANGED` — the tool's own "this cut did not move" code |
| `blk_shift` (FRAME) | **0.0 on all 52** (WARN at 20, FAIL at 40) |
| `newdark` (OCCL) | **0.0 on all 52** (WARN 2.0, FAIL 8.0) |
| `newdark_blob` | **0.0 on all 52** (WARN 1.5, FAIL 5.0) |
| pixel `diff_mean` | 0.15 – 3.92 LSB, median **0.35** |
| `d_mean` | −0.014 – +0.935, median **−0.0002** |
| carried-over defect | WHITE on sceneN1 × 8 — present in **both** arms, flagged by the tool itself as absolute state, not regression |

The spike round's **null control** — the same scene re-rendered in a fresh process with *no code
change at all* — measured that floor at 0.08–3.42 LSB with every decision metric at zero
(`lighting_spikes_v1.md` §1.2). This round's 0.15–3.92 LSB with every decision metric at zero is the
same distribution.

**The single outlier is a pre-registered one.** `scene04 preset_h0.3_d2` at `diff_mean` 3.92 /
`diff_frac` 30.98 % is exactly the cut the spike report already named: *"scene04 h0.3_d2 is the one
cut that is not bit-reproducible across processes — meanΔ 3.42 LSB, 28.3 % of pixels off by > 4 LSB,
while every other cut sits below 1.2 LSB"*. It moved no decision metric here either (`blk_shift`
0.0), and it reproduced independently — which is a small confirmation of that open W3 item, not a
consequence of this change.

Static freeze checks, no GPU:

- `python3 scene_common.py --variation` → **PASS**: all 9 `grid_views` preset eye/tgt pairs
  bit-identical to a hardcoded expectation (including the `2.9240387650610398` target-x float);
  the `h0.3` token `regression_check.is_graze_view()` greps for still present; `gy` shifts y only;
  **29 of 33** scenes' `PARAMS["light"]` match catalogue `L0` field-for-field and the only 4 that
  differ are the known-divergent C1/C2/C4/D4.
- `python3 variation_kit.py` → **PASS**, 80 assertions.
- `scripts/geom_invariance_check.py` → **R-5 PASS** (0 residual `LOOK_V1` outside the 3-line shim),
  **R-4 33/33**, **R-6 33/33**.
- **No scene file was modified.** `git status scenes/` is clean apart from the two new
  `variation_kit.py` symlinks, which mirror the existing `ground_kit`/`stair_kit` convention.

### 1.1 What made the freeze cheap: a callable object instead of a tuple

Spec §6.3 sketched `setup_lighting()` returning `(apply_dome_rot, apply_light_cond)`. All 33 scene
files do `apply_dome_rot = sc.setup_lighting(...)`, so a tuple would have required 33 edits inside
the very round that has to prove nothing changed. `setup_lighting` instead returns a
`LightingControl` whose `__call__` **is** the old `apply_dome_rot`, with `.apply_cond()` alongside.
Zero scene edits, and the freeze became provable rather than argued.

### 1.2 What was deliberately *not* frozen-in

Spec §5.4's tone-mapping block is split by role, because half of it can move pixels:

| key | judge | reason |
|---|---|---|
| `/rtx/post/histogram/enabled` = False | **set** | AE is already off (`t0_spike_report_v1.md` §7) — a re-assertion, and the one key that would invalidate every A/B verdict this project has made if it flipped |
| `/rtx/post/tonemap/op` = 6 (ACES) | **set** | already 6 in the runtime dump `[local]` |
| `colorcorr/enabled`, `colorgrad/enabled` = False | **set** | already False in the dump `[local]` |
| `tonemap/colorMode`, `tonemap/dither`, `ecoMode/enabled` | **data only** | `dither` adds sub-LSB noise **by design**; `colorMode` and `ecoMode` appear in no dump, so their current values are unverified. Setting them on the judge channel would forfeit the bit-freeze for no gain |

---

## 2. Render-role split (D1 / D2)

```
NEGOBS_RENDER_ROLE = judge (default, = today) | data | sweep
```

Under `judge`, any of `NEGOBS_LIGHT_COND · CAM_MODE · CAM_N · SEED · DAZ · EXPO_VARY` set to a
non-default value raises **`SystemExit`** — checked in `boot()` *and* in `capture_pipeline()`,
because `boot()` is where it is cheapest to catch and the GUI path never reaches
`capture_pipeline` at all.

**Live proof** `[measured]` — a scene run directly, role unset:

```
$ NEGOBS_CAPTURE=1 ... NEGOBS_LIGHT_COND=L7  python scenes/batch1/sceneN1_shadow_band.py
[variation] role=judge but variation env is set: NEGOBS_LIGHT_COND=L7
  The judge channel is frozen (spec D1/D2): ...
$ test -d $NEGOBS_CAPTURE_DIR  ->  NO        # no directory, no boot, no GPU touched
```

Same for `NEGOBS_SEED=42`. The import of `variation_kit` inside the gate is **unguarded**: a gate
that disables itself when its module is missing is worse than no gate, so `variation_kit.py` is
symlinked into `scenes/main` and `scenes/batch1` exactly like `ground_kit`, with a realpath fallback.

**Output trees.** Judge stays at `look_check/<scene>/<round>/` with the filename convention
untouched. Data goes to `dataset/<run>/<split>/<scene>/`, which `regression_check.py` cannot reach —
it is only ever pointed at `--scenes 'look_check/scene*'` `[local]`. The validator asserts both
directions: nothing condition-named under `look_check/<scene>/`, and the data root outside that glob.
`dataset/` is gitignored; its `manifest.json` is the record.

Split assignment is **scene-level only** (spec B5) and deterministic: sort, shuffle with a fixed
`crc32` seed, slice 70/15/15 → **23 / 5 / 5**. A per-scene hash would have given 21/4/8 on 33
scenes.

---

## 3. Condition catalogue — computed, not transcribed

### 3.1 The model, and an independent measurement of what feeds it

`variation_kit.CONDITIONS` evaluates spec §4.3's model rather than storing its output table:

```
E_rel(c)          = cloud · (sin h_c / sin 49.83°)^1.15        cloud = 1.0 | 0.20 (sunless)
sun_intensity(c)  = 2450 / f_dir_ref · E_rel(c) · f_dir(c)
dome_intensity(c) = 1000 · E_rel(c) · (1−f_dir(c))/(1−f_dir_ref) · Esky_ref / Esky(c)
ΔEV               = −log2 E_rel(c)              ev_comp = 0.75 · ΔEV
```

That needs three measured numbers per sky — elevation, `f_dir`, `Esky` — and the spec published
`Esky` for the **reference sky only**, so the three newly procured skies' dome intensities are not
derivable from the document at all. `scripts/measure_sky.py` (new, GPU 0) measures all three by
reproducing spec §4.2's method independently: solid-angle-weighted centroid of the top 0.01 %
luminance → sun direction; `cap` = p90 of the ring [0.6, 1.0]°; `E` = cos-weighted upper-hemisphere
integral. Output `assets/sky_photometry.json` (tracked — the EXRs are not).

Agreement with the design session's independent measurement `[measured]`:

| sky | our elev | Δ vs spec | our `f_dir` | Δ | our `Esky` | rotz |
|---|---|---|---|---|---|---|
| `qwantani_noon` (ref) | 49.83 | **+0.00** | 0.9152 | +0.0032 | 0.5204 | 233.82 |
| `kloofendal_48d` | 47.87 | **+0.00** | 0.6672 | +0.0082 | 1.5980 | 235.74 |
| `sunflowers` | 43.01 | **+0.00** | 0.6644 | +0.0024 | 1.4526 | 233.84 |
| `kloofendal_38d` | 37.96 | **+0.00** | 0.4560 | +0.0180 | 1.6728 | 234.04 |
| `kloofendal_28d_misty` | 28.50 | **+0.00** | 0.0652 | +0.0162 | 3.9496 | **280.85** |
| `qwantani_late_afternoon` | 19.08 | **+0.01** | 0.6492 | +0.0042 | 1.3482 | 233.87 |
| `farm_field` | (51.05) | — | 0.0006 | +0.0006 | 4.3092 | 233.75 |
| `kloofendal_overcast` | (22.77) | — | 0.0001 | +0.0001 | 4.0508 | 236.94 |

The misty sky's azimuth outlier is confirmed exactly: φ 169.15 → `hdri_sun_rotz_offset` **280.85**.
Using the scene constant 233.5 there would throw its shadows 47° off, so each condition carries its
own rotz and the validator asserts it per cut.

`Esky_ref` measures **0.5204** here against the spec's 0.5390 (3.5 %). The dome formula uses the
*ratio* `Esky_ref/Esky(c)`, so the whole set must come from one pass; mixing would be inconsistent.

### 3.2 The catalogue, and how far it lands from the spec's published table

Self-checked `[calc, measured]`:

| ID | name | sky | elev | lookfix | **dome** | spec | Δ | **sun** | spec | ΔEV | ev_comp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L0 | ref | qwantani_noon | 49.83 | T | **1000.0** | 1000 | 0.0 % | **2450.0** | 2450 | 0.000 | 0.000 |
| L1 | cumulus | kloofendal_48d | 47.87 | T | **1234.9** | 1234 | 0.1 % | **1725.7** | 1709 | +0.050 | +0.037 |
| L2 | stratocumulus | sunflowers | 43.01 | T | **1244.3** | 1244 | 0.0 % | **1560.9** | 1559 | +0.188 | +0.141 |
| L3 | autumn_noon | kloofendal_38d | 37.96 | T | **1555.1** | 1554 | 0.1 % | **951.2** | 916 | +0.360 | +0.270 |
| L4 | winter_noon | kloofendal_28d_misty | 28.50 | **F** | **845.1** | 845 | 0.0 % | **101.6** | 77 | +0.781 | +0.586 |
| L5 | low_sun | qwantani_late_afternoon | 19.08 | T | **601.4** | 601 | 0.1 % | **654.5** | 652 | +1.409 | +1.057 |
| L6 | overcast_bright | farm_field | — | **F** | **290.5** | 290 | 0.2 % | **400.0** | 0 → floor | +2.293 | +1.720 |
| L7 | overcast | kloofendal_overcast | — | **F** | **138.6** | 139 | 0.3 % | **400.0** | 0 → floor | +3.451 | +2.588 |

- **dome: worst deviation 0.29 %** across all 8. `ΔEV` and `ev_comp` match to < 0.01 everywhere.
- **sun on L3 / L4 differs by 3.8 % / 32 %, and it is a measurement difference, not a model one.**
  Sun intensity is linear in `f_dir`, and on those two hazy skies we measure 0.456 / 0.0652 where the
  spec measured 0.438 / 0.049 (the disc/halo split is threshold-sensitive when there is no crisp
  disc). The self-check separates the two claims: it asserts the model identity on our own
  photometry **and** that the same model fed the spec's constants returns the spec's published
  integers to within their rounding (worst 0.54 %, L4's "77" being a 2-significant-figure rounding of
  76.6). Both pass; the residual is then reported as an `[info]` line, not asserted away.
- **Overcast conditions are PT-only** and the assertion is enforced in the runner: *"a sunless dome
  alone is flat light under RT — judge on PT"* (`sceneC1:239` `[local]`). The soft-direct floor of
  400 with `angle` 4.0° is `[unmeasured]` — SP-5 was not among the four spikes that ran, so 4.0° is
  the spec's midpoint and 400 is C1's 420 precedent, not a measurement.
- **Exposure compensation rides on `filmIso`, not `exposureTime`** — a declared deviation from spec
  §5.4. `filmIso` is the only exposure key **measured** to work in this repository (`t0` §7: ISO
  100 → 800 moved the frame mean 127 → 214 with AE off). `exposureTime` appears in no runtime dump —
  what the dump carries is the legacy alias `cameraShutter = 50.0` — so writing 1/500 s to a key
  whose live name is unverified risks a 100× exposure error. Exposure compensation is a pure stop
  offset, so which of the three controls carries it is immaterial to the image; `fNumber` stays 5.0
  so no depth of field appears (§3.5).

### 3.3 Seoul astronomy (D6) and the low-sun exception

`min_abs_daz` is derived per condition from appendix B: Seoul's noon altitude floor is 29.0°, so
L5's 19.08° sun needs **|Δaz| ≥ 37.0°** `[calc]`. That is past the sweep's widest measured arm (35°),
so `DAZ_DATA_EXTRAP = 60°` lets the data channel reach it — for forced-off-noon conditions only,
and **not** where criterion C bound (`scene15` at ±20) or where the label is the shadow (`sceneN1`
at 0). Consequence: L5 is admissible on 30 of 33 scenes and refused on `scene15`, `sceneC2`,
`sceneN1`, each with a printed reason.

### 3.4 Scene × condition admissibility over all 264 pairs

`[calc]` **253 of 264 admissible (96 %)**, 11 refusals, every one traceable to a season lock or the
D6 floor:

| condition | admissible | refused |
|---|---|---|
| L0 ref | **31/33** | `sceneC1`, `sceneC2` — **see below** |
| L1 cumulus | 31/33 | `sceneC1`, `sceneC2` |
| L2 stratocumulus | 32/33 | `sceneC1` |
| L3 autumn_noon | 32/33 | `sceneC1` |
| L4 winter_noon | 31/33 | `sceneC2`, `sceneN1` |
| L5 low_sun | 30/33 | `scene15`, `sceneC2`, `sceneN1` |
| L6 / L7 overcast | **33/33** | — |

**L0 being inadmissible on two scenes is a real conflict inside the spec**, not an implementation
artefact: §4.3 says "L0: all 33 scenes, the judge reference" and also locks sceneC1 to elev ≤ 32 and
sceneC2 to 35-45, while L0 sits at 49.83. The scenes had already resolved it — C1 runs elev 28.0 and
C2 runs 42.0, neither has ever used 49.79 — so `ref_cond_for(scene)` maps **C1 → L4** (28.50 vs its
own 28.0) and **C2 → L2** (43.01 vs its own 42.0). A production plan that asks for "L0 on everything"
loses those two scenes from the reference arm **silently**; the self-check now asserts every scene has
an admissible reference. This is validated by self-check only — neither C1 nor C2 was in the mini
run's scope.

Scene-specific lighting balances still win (spec §4.3): `sceneC1` 800/420, `sceneC4` 1150/600,
`sceneD4` 8.0/0 are hand-tuned, so `apply_cond` scales them by the condition's **relative**
illuminance instead of overwriting them — a snow scene under overcast still gets darker without
losing its own balance.

---

## 4. Azimuth ledger — SP-2 measured, with provenance

`variation_kit.AZ_LEDGER`, 33 rows, replacing spec §4.5's hypothesis classes. Class counts
**S 1 · A′ 7 · B′ 2 · C′ 23**, and **two allowances per scene** because the sweep established the
question differs by channel (spike §1.5 caveat 2):

| class | `daz_judge` | `daz_data` | scenes |
|---|---|---|---|
| **S** identity | **0** | **0** | `sceneN1` — drop line collapses to ratio 0.40 at ±10 `[measured]` |
| **A′** edge-sensitive | **10** | 35 | `scene02·05·07·11·13·15·21` |
| **B′** | **20** | 35 | `scene06`, `sceneN4` |
| **C′** | **35** | 35 | remaining 23 |

- `daz_judge` = criterion **B** (a GRAZE FAIL counts only when it is about the drop row) merged with
  criterion **C** (absolute readability), taking the tighter. Criterion A — the brief's literal
  "no FAIL in DARK/OCCL/GRAZE" — is **not used**, because OCCL is *defined* as "pixels that were ≥ 60
  and are now < 25", which is the definition of a cast shadow, and between two arms of an azimuth
  sweep the only stage delta is a rotate op on two light prims.
- `daz_data` = 35 for all but two: `sceneN1` (0, the label is the shadow) and `scene15` (20, where
  criterion C genuinely bound — at ±35 the alley loses its raking light, `h0.3_d5` mean 110.4 → 42.9,
  dark 22.9 % → 73.5 % `[measured]`).
- The two spec-S scenes that measured ±35 with no firing at any arm — `scene16 canopy_shadow` and
  `sceneD2 floor_opening` — are freed to the full range. The spec forbade variation on two scenes
  that demonstrably tolerate it.
- Caveat carried forward: the grid was {0, 10, 20, 35}, so a measured "10" means "10 passed, 20
  failed" and the spec's ±15 for its A tier is **not excluded** by this data.

---

## 5. Camera sampler

Spec §3.2 distributions, sampled exactly as SP-3 sampled them so the measured `r_reject` still
applies: `h ~ U(0.25, 1.90)` **above ground**, `pitch ~ N(−10°, 4°) ∈ [−20, −2]`,
`roll ~ N(0, 1.5°) ∈ [−5, 5]`, `hFOV ~ N(62.2°, 1.5°) ∈ [58, 66]`,
`y ~ N(gy, 0.35) ∈ gy ± 0.9`, `yaw ~ N(0, 8°) ∈ [−20, 20]`, `d ~ LogU(1.2, 12)`.
4 000-sample self-check: pitch mean −10.01, hFOV mean 62.20, `d < 1.5` share 10.8 % (the bin SP-3
measured 19 % `flat_near` in).

- **`UsdGeom.Camera`, one `xformOp:transform`**, SP-7's convention preserved verbatim — it removes
  every rotation-order question, and SP-7 measured hFOV error ≤ 0.047° and roll error ≤ 0.005° with
  the principal point dead centre. `focalLength = aperture / (2 tan(hFOV/2))`; the self-check pins all
  three arms SP-7 actually rendered to < 1e-4. (SP-7's quoted 17.36949 for hFOV 62.2 is the exact
  answer for aperture 20.9559; ours is 17.36875 for 20.9550. Both round to spec §3.1's 17.369, which
  is the claim that matters.)
- **Heights are ground-relative.** `grid_views` uses absolute eye z, and a naive randomiser buries
  the camera in the 7 descending scenes (`fixlog_W7` §0: "new geometry swallowing the preset camera —
  4 recurrences"). The ground is found per sample by a downward ray through the AABB world, and the
  validator asserts `ground_below == h_rel`: **worst error 0.0000 m over 72 cuts** `[measured]`.
  CAM-3 therefore reduces to documentation of which scenes would have broken.
- **CAM-2** narrow/low scenes (`scene02·11·15`, `sceneD4`) get height ceiling 1.20 m and lateral
  σ 0.15 m.
- **The stage-1 analytic prefilter was demoted, per SP-3.** It fired once in 600 samples and that
  once was a false positive, so it has zero demonstrated true positives. It is kept (0.8 ms/sample),
  **recorded**, and given **no rejection power** — the image decides, which is the way the one
  observed disagreement went. It is not credited in any budget.
- **`flat_near` is a judge filter, not a data filter.** It was the entire rejection mechanism in SP-3
  (5 of 6) and fires only at `d ∈ [1.2, 1.5)` — the closest, most safety-critical range, where "the
  ground ahead is a smooth textureless slab" is a real hard input, not a corrupt one. Default on for
  judge, off for data. Consequence visible in §7: measured `r_reject` **0.0** on all three mini-run
  scenes.
- **`ground_kit.frame_budget` is reused as an advisory** near-field read wherever a scene has a ground
  plan, fed the sampled (h, d, y). Recorded, **not enforced**: its gates are calibrated for the h0.3
  presets. On the mini run it produced **hard-gate flags 0** and fill-target flags on 72/72 — i.e.
  the hard gates are meaningful and the fill targets are not, at arbitrary camera poses. Weak signal,
  reported as such.

---

## 6. Data-run driver

`scripts/run_data_render.py` — `scenes (one process each) → conditions (one boot, runtime swap) →
cameras`. Conditions outside the camera loop, so the sky is swapped `N_light − 1` times per scene
rather than once per cut (spec §6.3, confirmed by SP-4's `t_swap` 1.4 s and SP-2's measured 3.29×).
Driver and in-process halves live in one file so they cannot drift.

- **Seed ledger**: `zlib.crc32(f"{scene}|{stream}|{idx}|{base}")`, streams `cam`/`light`/`expo`/`split`
  separated, on a private `random.Random` so scene assembly's global RNG is untouched. Never `hash()`
  — this repository has already lost a round to `PYTHONHASHSEED` randomising a displacement seed.
- **Manifest**: run-level `manifest.json` (git HEAD, seed, refusals, per-scene time/exit/cuts,
  per-invocation wall time) + per-scene `variation.json` carrying one record per cut with the full
  re-render recipe — camera pose and focal, condition and its dome/sun/elev/angle/rotz/Δaz, exposure,
  render settings, stage-1 record, image measurement, frame-budget advisory.
- **Resumable** at cut granularity (file present *and* `ok`) and at condition granularity
  (`done_conds`). Verified live: a second invocation added 8 cuts to a scene that already had 16.
- **Robust capture**: the 40-update poll `capture_pipeline` uses is too small for a loop that
  re-authors the camera matrix *and* `focalLength` every cut — in SP-3 it declared 35 of 200 captures
  failed when all 35 files had been written moments later (spike §6.7). The data path raises the
  budget to 150 with a 6-update settle, and `ok=False` means **absent**, not "not yet stable". The
  mini run captured **72/72**. *The judge path's poll is left alone on purpose* — fixing it there
  would have been an unrequested change to the channel this round has to prove frozen. It remains an
  open W3 item.
- **Pre-flight**: every condition's `lookfix` derivative is generated before the run, because the
  first call per new sky costs 2.0 s of CPU and an 18 MB write and would otherwise be a silent stall
  on the first cut of each condition (SP-4 §3.4).
- **Budget printout** from the measured constants (`t_cut` 2.87 · `t_boot` 34.3 · `t_swap` 1.4 ·
  `r_reject` 0.02). Full-production projections `[calc]`, matching spike §5:

| scenario | cuts | total | overhead |
|---|---|---|---|
| 4 cond × 20 cam | 2 693 | **2.50 h** | 14 % |
| 8 cond × 40 cam (spec recommended) | 10 771 | **8.99 h** | 4 % |
| 8 cond × 68 cam (20 k target) | 18 311 | **15.00 h** | 3 % |

---

## 7. Mini data-run validation — 72 cuts

Round `260730_data_mini`, 3 scenes one per measured azimuth class × 3 conditions × 8 cameras:

| scene | class | split | conditions | cuts | s/cut | `r_reject` |
|---|---|---|---|---|---|---|
| `sceneN1` shadow_band | **S** (daz 0) | train | L0, **L1**, L7 | 24 | 0.96 | 0.0 |
| `scene02` underpass | **A′** | val | L0, L7, L5 | 24 | 2.67 | 0.0 |
| `sceneN4` downhill_ramp | **B′** | train | L0, L7, L5 | 24 | 2.93 | 0.0 |

`sceneN1 × L5` was **refused by design** and that refusal is part of what the run validates. Its 8
cuts went to L1 instead, declared in the round script rather than substituted inside the driver — a
silent substitution is how a condition distribution stops being independent of the label (spec B6).

`scripts/check_data_run.py` (new, GPU 0) → **PASS on all 5 groups** `[measured]`:

| group | result |
|---|---|
| **1 exposure** | 72/72 inside criterion C (mean ∈ [30, 235], dark ≤ 70 %, clip ≤ 1 %). Deep-shadow share **L0 4.28 % → L1 0.54 → L5 1.13 → L7 0.12 %** — the direct fraction (`f_dir` 0.915 → 0.667 → 0.649 → 0.000) showing up in the image. Sun-bearing ground band darkens with net EV per scene (2 pairs ≥ 0.3 EV); sunless has less deep shadow than L0 on all 3 scenes |
| **2 azimuth** | 72/72 inside the ledger. `sceneN1` **0.0 on every condition**; `scene02`/`sceneN4` × L5 land at 39.5–59.6°, above the forced 37.0° floor. Each condition carries its own rotz (L7 236.94), sun elevation tracks the sky's measured elevation on every cut — no double shadow |
| **3 camera** | `ground_below == h_rel` to **0.0000 m** on 72/72. Buried / closed-in / off-ground flags **0**; nearest solid to any eye 0.277 m. Every sampled quantity inside its truncation; `focalLength` consistent with hFOV to 4.8e-6 |
| **4 integrity** | manifest ↔ disk 1:1, **72/72 content-unique md5**, all 1920×1080, filename convention exact, **0** condition-named files under `look_check/<scene>/`, data root outside `regression_check`'s only glob |
| **5 throughput** | in-scene **0.96 – 2.93 s/cut** against SP-3's pooled 2.87 s. `sceneN1` at 0.96 s is a simple scene; `sceneN4` at 2.93 s sits on SP-3's figure |

### 7.1 Bug the validator caught #1 — a sunless condition unlocked the azimuth

`sample_daz` treated `sunless` as "azimuth has no consequence" and took the wide ±35° branch. But
spec §4.6 deliberately restores a **widened 4° soft sun** at the readability floor, so an overcast
condition still casts soft shadows and rotating the dome still moves them. Measured effect: `sceneN1`
— the one scene whose *label is the shadow band*, allowance 0 — received |Δaz| up to **34.0°** on its
L7 arm. Fixed so only the three scenes SP-2 measured as azimuth-insensitive (`sceneC1`, `sceneC4`,
`sceneD4`; sceneD4's |Δmean| ≤ 0.22 LSB across ±35°) get the bypass. Regression case added to the
self-check; the 8 affected cuts were re-rendered and now read 0.0 on all of them.

### 7.2 Bug the validator caught #2 — the exposure gate itself was physically wrong

The first gate asserted "a condition N EV darker must have a lower frame mean". It failed, and it was
right to fail — the assertion is wrong `[measured]`:

| scene | ground mean L0 | ground mean L7 | |
|---|---|---|---|
| `sceneN1` | 160.4 | **206.4** | ground is deliberately half in cast shadow; overcast **removes** it |
| `scene02` | 175.8 | 171.5 | |
| `sceneN4` | 124.1 | 114.5 | |

Removing a cast shadow raises the mean far more than an 0.86 EV illuminance drop lowers it, and the
frame mean also mixes in sky, which is *brighter* under overcast (measured `Esky` 4.05 vs 0.52; sky
band 130.9 → 167.1). The gate now asserts the two signatures that are physically sound: among
sun-bearing conditions the **ground band** darkens with net EV *per scene* (so albedo cancels), and a
sunless condition has **less deep shadow** than the L0 reference. Both hold, and the reasoning is
recorded in the checker so it is not re-broken.

---

## 8. GO / NO-GO for full data production

### **GO** — with three conditions, none of them blocking

The machinery is measured end-to-end: the judge channel is provably frozen, the ledger and catalogue
are encoded from measurement with their provenance, the sampler places cameras correctly in the
scenes that used to break it, the driver is resumable and its budget is built on measured constants,
and the acceptance checker is strong enough to have found two real bugs in its first use.
**Full production is W5-adjacent and has NOT been started.**

**Condition 1 — use `ref_cond_for(scene)`, not `L0`, for the reference arm.** Otherwise `sceneC1` and
`sceneC2` drop out of it silently (§3.4). Validated by self-check only; neither scene has yet been
data-rendered, so their first production run should be eyeballed.

**Condition 2 — fix `capture_pipeline`'s flush poll before the run, on the judge path too.** The data
path already has the fix. In the standing judge round the old poll yields `ok=false` on 15.7 % of cuts
with every PNG decoding fine, so **a full run would under-report its own yield by roughly a sixth**
(spike §6.7). It was deliberately left alone here to keep the bit-freeze provable; it should land as
its own change with its own regression pass.

**Condition 3 — `t_cut` is the only thing left to optimise, and it is worth ~35 %.** Overhead is now
3 % of a 20 k-cut run, so the 15.00 h projection is essentially all render time. About 1.0 s of every
cut is the async PNG write settling rather than rendering (spike §5, measured on the cheapest scene).
Either accept 15 h or spend the tuning first — but decide before starting, not during.

**Two things to carry, not fix.** The soft-direct profile for sunless conditions (`angle` 4.0°,
intensity 400) is `[unmeasured]` — SP-5 never ran, so the first L6/L7 batch is the de facto readability
test. And `scene04 preset_h0.3_d2`'s cross-process irreproducibility reproduced again here (§1); it is
a W3 item and it touches nothing in this round.

**One judgement to make that this round cannot make.** The mini run measured `r_reject` = **0.0** on
all three scenes, because `flat_near` is off on the data channel by design (SP-3 rider 2). That means
the data channel currently has **no active rejection mechanism at all** — `dark` and `blown` never
fired in SP-3's 600 samples or this round's 72, and stage 1 has no rejection power. This is defensible
(the image filter's remaining job is to catch a broken render, and nothing was broken) but it should
be a decision rather than a discovery: at production scale, either accept that every rendered cut
enters the dataset, or introduce a data-appropriate quality gate that is not an inherited
render-failure detector.

---

## 9. Artefact index

| path | contents |
|---|---|
| `variation_kit.py` | role gate · seeds · azimuth ledger · condition catalogue · camera sampler · 2-stage filters · split · self-check |
| `scene_common.py` | `LightingControl` (callable, `.apply_cond()`) · role gate in `boot`/`capture_pipeline` · exposure freeze · `_variation_selfcheck()` |
| `scripts/run_data_render.py` | data-run driver + in-process half |
| `scripts/check_data_run.py` | 5-group acceptance gate for a data run |
| `scripts/measure_sky.py` | sky photometry → `assets/sky_photometry.json` |
| `scripts/rounds/run_260730_lcfreeze.sh` | judge-freeze pre/post round |
| `scripts/rounds/run_260730_data_mini.sh` | the validated mini data run |
| `assets/download_sky.py` | `--ladder` / `--only-ladder` for the L3/L4/L5 skies |
| `Docs/reports/regr_260730_lcfreeze.json` | the freeze regression output |
| `look_check/{scene02,scene04,sceneN1,sceneN4}/260730_lcfreeze_{pre,post}/` | 2 × 52 judge cuts (gitignored) |
| `dataset/_archive/scene_dev_2607/260730_data_mini/` | 72 data cuts + manifests (gitignored) |

Reproduction:

```bash
python3 variation_kit.py                       # variation self-check
python3 scene_common.py --variation            # preset / ref-lighting freeze check
python3 scripts/geom_invariance_check.py       # R-5 / R-4 / R-6
python  scripts/measure_sky.py                 # sky photometry (needs cv2)
bash    scripts/rounds/run_260730_lcfreeze.sh pre|post
python3 scripts/regression_check.py --scenes 'look_check/scene*' \
        --before-round 260730_lcfreeze_pre --after-round 260730_lcfreeze_post
bash    scripts/rounds/run_260730_data_mini.sh
python3 scripts/check_data_run.py
python3 scripts/run_data_render.py --plan --scenes <...> --conds <...> --cams <n>
```
