# W2-D — the 33-scene final judgement round `260730_w2d_judge`

Author: W2-D (MAIN tree, branch `feat/realism-v1`) · 2026-07-30 · GPU exclusive, sequential
single-instance renders, `NEGOBS_PT_FAST=1`, `MODE=pt`, arm `NEGOBS_LOOK_V1=1` +
`NEGOBS_DETAIL_SCALE=2` + `NEGOBS_DETAIL_ROUGH_GAIN=0` (W2-C §7 GO item 1).
Every number is `[measured]` from a PNG or from code executed this session, `[calc]` from the
verified frame model, or `[assumed]` with the reason stated.

---

## 0. Verdict in one paragraph

All 33 scenes rendered clean — **452 cuts, 27.7 min wall, 3.68 s/cut, zero non-zero exits** — and
the five preflight items landed green before a frame was made (`ground_kit.py` exit 0 · 33/33 hard
gates · R-4/R-5/R-6 33/33 · the three validation corpora reproduce `w2_tools_v1.md` §4.4 to the
digit). **The round does not meet the mission's literal `GRAZE FAIL 0` bar: there are 8.** But the
same-HEAD `NEGOBS_GKIT=0` A/B that ruling §7.5 A3 mandates attributes only **2 of the 8** to
ground_kit, and neither of those two is a burial — in both the drop line **survives at 97–99 % of
its own strength** (ratio 0.97 / 0.99) while a *different*, legally mandated transverse element
enters the E band. **No cut anywhere in the round shows the destroyed-line signature** (the directed
test in `w2_tools_v1.md` §4.6 measures ratio 0.01 for a real burial; this round's minimum against
the OFF arm is 0.97). The two attributable firings are one single structural gap, and it is already
on the supervisor's list: **`EXPECTED_FP` — the GT-E2-x registry that tells the adjudicator "this
transverse line is a mandated tactile band, not the edge" — is never read by
`regression_check.py`.** It exists only inside `ground_kit`'s plan-time B7. That is filed here as
**D14**. Beyond the hazard gates the round is the strongest tone result the project has produced:
`w80` falls 88→31 (scene01), 95→27 (05), 97→41 (18), 98→0 (19), 79→29 (20), 86→18 (C1), and the
restored σ_LF WARN gate goes from **5/33 to 11/33 scenes clear**, improving in 26/33. Two scenes
bought that with a new defect: **scene11 and scene19 now carry large dead-flat, untextured
near-field planes** (`flat_gnd` 10.4→53.1 and 10.0→94.8), and scene19's de-whitening overshoots to
**near-black** on two mise-en-scène cuts (mean −47 / −57, dark +22 / +18 pp). Those three are the
round's real blockers — and not one of them is a hazard gate.

---

## 1. Preflight — 5 items, one commit `fc69706`, all green `[measured]`

| # | item | result |
|---|---|---|
| **P1** | scene05 joint-region clamp `x1 = −3.70` → **−1.50** (the lip) | ground_kit v1.3's origin-aware guard drops exactly `{−3.6, −1.8}` by itself: **joint prims 6 → 6, plan prims 48 → 48, δmax 0.1019 unchanged, gates identical** (WARN `B4,B5`, FAIL none). The gain is real and measurable: the near-most surface element moves from **x −2.208 to −1.500** and **31 of 45 elements shift into the reclaimed 1.4 m** (16 cracks, 8 stains, 6 weeds, 1 joint run). The clamp was pure loss. |
| **P2** | `SCENE_PLANS` fixture drift on 05/08/19/N1 | Fixtures now mirror the recorded live calls. Fixture prims **1,324 → 1,329**, hard gates **33/33**. scene05 origin `(0,0,0)` → `(−1.5,0,0)` (the reason the fixture never exercised D-1 for scene05); scene08 drops the kit-emitted `opening_ring` the scene keeps on its own path and gains its void + overrides; scene19 leaves the **phantom lip** (origin 9.04 / edge s=0) for the real 11.6 / s=7.6; sceneN1 drops the defective 56.1 %-width spec manhole `(−1.0, 0.4)` and gains `pave=dict(joint=None)`. |
| **P3** | σ_LF ≥ 5.0 restored as a WARN gate | `near_ground_stats.py --round-class {post_t1,ground_only}`. §7.5 A1's round grading lived **only in prose**; it is now a declared input, default `post_t1` = σ_LF/sd fire. `ground_only` prefixes them `[i]` and drops them from the violation count. Anchors still reproduce exactly (scene01 v7_pt σ_LF 0.72 · scene14 r2_on `flat_gnd` 31.3). |
| **P4** | corpus driver → `scripts/valset.py` | Third reconstruction prevented. `--check` compares against an `EXPECTED` block in the file: **history 94 cuts FAIL 1 · WARN 2 · deferred 23**, **false-positive 156 cuts FAIL 0 · WARN 0**, **T3 both quiet** — identical to `w2_tools_v1.md` §4.4 and `cleanup_lookcheck_v1.md` §4, including the three defended firings (scene18 `d2` spec 67.6 FAIL · scene17 `d2` 10.2 · scene19 `d5` 11.1). It also **corrects the P4 series membership**: the scratchpad driver had guessed `sceneC2/r2` and `scene05/r3`, two rounds that do not exist, under-counting the series 18 → 13. |
| **P5** | dead baseline chain | `final_pt_r2,final_pt,ctx2_pt,ctx2` resolved to **nothing at all for the 21 main scenes** after the 07-30 cleanup — i.e. the standing supervisor command was comparing against no baseline. Replaced by `w2c_g2,w2_pilot,r2b_on,wall,facade,r2_on`, verified to resolve every scene to its own latest judged round **33/33**. |

Standing checks after the batch: `python3 ground_kit.py` **exit 0**, hard gates **33/33** · R-5 PASS,
R-4 **33/33**, R-6 **33/33**, exit 0 · `py_compile` 5/5 · `valset --check` exit 0.

---

## 2. Render round `[measured]`

| | |
|---|---|
| round | `look_check/<scene>/260730_w2d_judge/` (README §2 naming) |
| scenes / cuts | **33 / 452** — 19 scenes at the 13-cut default, plus the scenes carrying more mise-en-scène: **16** cuts (03 · 12 · 19), **15** (06 · 08 · 13), **14** (07 · 09 · 10 · 11 · 17 · 18 · D1 · D3) `[calc: 19×13 + 3×16 + 3×15 + 8×14 = 452]` |
| wall | **1,663 s = 27.7 min** · mean **50.4 s/scene** · **3.68 s/cut incl. boot** |
| exits | **0/33 non-zero** |
| stamp | `round_stamp.json` in every directory — HEAD `fc69706`, MDL md5 `16bba896…` v1.9.0, full `NEGOBS_*` arm |

The mission's "13-cut preset + 4 REVIEW cuts" is one set, not two: `preset_h0.3_d5`,
`preset_h0.9_d5` and `preset_h1.8_d10` are members of the 3 × 3 preset grid and the beauty/overview
cut is one of the scene's own mise-en-scène shots, so the four review cuts are a **selection from**
the scene's default view set, which is what was rendered. The only scene where a review cut does not
exist is **scene19**, whose preset distances are 2 / 3.5 / 5 — `h1.8_d10` is substituted by
`h1.8_d5` and the substitution is recorded in `meta.json`, not hidden.

A second, diagnostic arm was rendered for the GRAZE adjudication (§3.2):
`look_check/_experiments/twins/<scene>/260730_w2d_goff/` — 6 scenes, 21 cuts, 144 s, `NEGOBS_GKIT=0`
at the same HEAD. Per README §1 it is under `_experiments/`, never in a scene root.

Drivers: `scripts/rounds/run_260730_w2d_judge.sh` · `scripts/rounds/run_260730_w2d_goff.sh` ·
`scripts/stamp_round.py`.

---

## 3. Per-scene gate table `[measured]`

`regression_check.py` v2.1, `--before-round w2c_g2,w2_pilot,r2b_on,wall,facade,r2_on`
→ `Docs/reports/regr_260730_w2d.json`. 452 cuts in **21 s**.
**FAIL / WARN are cut counts** (a cut takes its worst code); the per-code `F/W` columns are
**issue counts**, so they sum higher — one cut can carry FRAME and OCCL at once.
`occl_new` / `occl_blob` are the scene's worst cut (WARN 2.0 / 1.5, FAIL 8.0 / 5.0).

| scene | base | cuts | FAIL | WARN | OCCL F/W | FRAME F/W | PHOTO F/W | GRAZE F/W | occl_new | occl_blob | σ_LF | Δσ_LF | flat_gnd | Δ |
|---|---|---:|---:|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|
| scene01 | r2_on | 13 | **0** | 6 | 0/0 | 0/6 | 0/0 | 0/0 | 1.40 | 1.08 | 1.45 | +0.53 | 3.3 | +2.3 |
| scene02 | r2_on | 13 | 1 | 3 | 0/0 | 1/3 | 0/0 | 0/1 | 0.26 | 0.08 | 3.21 | +2.12 | 0.1 | +0.1 |
| scene03 | r2_on | 16 | 3 | 11 | 0/0 | 3/11 | 0/0 | 0/2 | 1.12 | 0.62 | 4.14 | +1.94 | 0.0 | 0.0 |
| scene04 | r2_on | 13 | 4 | 7 | 0/1 | 4/7 | 0/0 | 0/0 | 2.97 | 0.82 | 3.10 | +0.71 | 0.0 | 0.0 |
| scene05 | facade | 13 | 2 | 4 | 0/0 | 2/3 | 0/1 | 0/1 | 0.79 | 0.43 | **3.76** | **+2.87** | 0.6 | −1.0 |
| scene06 | r2_on | 15 | 5 | 3 | 0/0 | 5/3 | 0/3 | 0/0 | 0.64 | 0.16 | 1.00 | +0.32 | 4.5 | −1.1 |
| scene07 | r2_on | 14 | 5 | 9 | 0/5 | 5/8 | 0/0 | 0/0 | 4.92 | 1.30 | **14.92** | **+13.59** | 0.7 | −0.9 |
| scene08 | r2_on | 15 | 8 | 2 | 0/0 | 8/2 | 0/3 | 0/0 | 1.11 | 0.53 | 3.69 | **−20.55** | 1.6 | +0.3 |
| scene09 | r2_on | 14 | **0** | **0** | 0/0 | 0/0 | 0/0 | 0/0 | 0.02 | 0.00 | 3.23 | +0.15 | 1.8 | −0.3 |
| scene10 | r2_on | 14 | 1 | 4 | 0/1 | 1/4 | 0/0 | 0/0 | 2.22 | 1.40 | **5.72** | +3.89 | 0.6 | +0.2 |
| scene11 | r2_on | 14 | 3 | 8 | 0/2 | 3/8 | 0/2 | 0/0 | 5.62 | 0.73 | **9.49** | +2.69 | **53.1** | **+42.7** |
| scene12 | r2_on | 16 | 1 | 4 | 0/0 | 1/4 | 0/0 | 0/0 | 0.31 | 0.09 | 1.92 | +0.70 | 2.0 | +0.1 |
| scene13 | w2_pilot | 15 | **0** | 1 | 0/0 | 0/1 | 0/0 | 0/0 | 0.17 | 0.09 | 0.99 | +0.01 | 17.0 | −0.2 |
| scene14 | r2_on | 13 | 2 | 2 | 0/0 | 1/2 | 0/0 | **1/0** | 0.16 | 0.04 | 2.38 | +1.28 | **18.6** | **−12.7** |
| scene15 | w2_pilot | 13 | **0** | 1 | 0/0 | 0/1 | 0/0 | 0/0 | 0.83 | 0.71 | 0.69 | −0.00 | 2.4 | −0.6 |
| scene16 | r2_on | 13 | 1 | 8 | 0/0 | 0/8 | 0/0 | **1/0** | 1.21 | 0.27 | 1.17 | +0.03 | 1.2 | +1.1 |
| scene17 | r2_on | 14 | 12 | 2 | 0/0 | 12/2 | 0/6 | 0/1 | 0.17 | 0.04 | 1.48 | −0.90 | 2.7 | +2.7 |
| scene18 | r2_on | 14 | **0** | 9 | 0/0 | 0/9 | 0/0 | 0/0 | 1.74 | 0.34 | 1.82 | +0.89 | 1.7 | +0.5 |
| scene19 | r2_on | 16 | **16** | 0 | **2/8** | 7/6 | 11/4 | 0/0 | **14.97** | **15.01** | 2.42 | +1.21 | **94.8** | **+84.8** |
| scene20 | r2_on | 13 | 7 | 5 | 0/0 | 6/5 | 0/0 | **3/1** | 0.15 | 0.03 | **13.07** | **+12.12** | 4.9 | +4.2 |
| scene21 | r2_on | 13 | 6 | 4 | 0/0 | 5/5 | 0/2 | **1/0** | 0.14 | 0.07 | **10.54** | **+9.01** | **9.9** | **−30.5** |
| sceneC1 | r2b_on | 13 | 6 | 7 | 0/0 | 5/8 | 2/2 | 0/0 | 0.00 | 0.00 | 0.84 | −1.36 | 0.5 | −1.5 |
| sceneC2 | w2c_g2 | 13 | **0** | **0** | 0/0 | 0/0 | 0/0 | 0/0 | 0.00 | 0.00 | **12.94** | +0.03 | 0.7 | −0.0 |
| sceneC4 | r2_on | 13 | 4 | 6 | 0/0 | 3/7 | 0/0 | **1/2** | 0.02 | 0.00 | **6.16** | +4.47 | 22.6 | +3.1 |
| sceneD1 | r2_on | 14 | **0** | **0** | 0/0 | 0/0 | 0/0 | 0/0 | 0.04 | 0.00 | 0.90 | +0.01 | 3.3 | +0.8 |
| sceneD2 | r2_on | 13 | 1 | 2 | 0/0 | 1/2 | 0/0 | 0/0 | 0.07 | 0.01 | 2.71 | +1.95 | 0.1 | +0.1 |
| sceneD3 | r2_on | 14 | **0** | 9 | 0/0 | 0/9 | 0/0 | 0/0 | 0.69 | 0.47 | 3.74 | +2.60 | 0.4 | 0.0 |
| sceneD4 | r2_on | 13 | **0** | **0** | 0/0 | 0/0 | 0/0 | 0/0 | 0.00 | 0.00 | 0.59 | −0.01 | 6.9 | −0.5 |
| sceneN1 | r2_on | 13 | **0** | 8 | 0/0 | 0/8 | 0/0 | 0/1 | 1.13 | 0.44 | 2.21 | +1.27 | 1.4 | +0.7 |
| sceneN2 | r2_on | 13 | 6 | 6 | 0/0 | 6/6 | 0/1 | 0/0 | 0.00 | 0.00 | **12.88** | **+11.56** | 1.7 | +1.7 |
| sceneN3 | r2_on | 13 | 6 | 6 | 0/0 | 5/7 | 0/0 | **1/0** | 1.43 | 0.42 | **6.83** | +5.30 | 3.0 | +3.0 |
| sceneN4 | wall | 13 | **0** | 5 | 0/0 | 0/5 | 0/0 | 0/0 | 0.32 | 0.07 | **11.81** | −0.38 | 5.4 | +3.3 |
| sceneN5 | w2_pilot | 13 | 2 | 1 | 0/0 | 2/1 | 0/0 | 0/0 | 1.48 | 0.34 | **5.10** | −0.00 | 2.2 | +0.0 |

**Totals**: DARK 0/4 · WHITE 0/1 · **OCCL 2/17** · FRAME 86/151 · PHOTO 13/24 · **GRAZE 8/9**.
**11 scenes FAIL 0**; 4 of them (09 · C2 · D1 · D4) are **FAIL 0 · WARN 0**.
σ_LF ≥ 5.0 clears in **11/33** scenes, against **5/33** on the same scenes' baselines, and improves
in **26/33** — the first reading of the gate since it was restored (P3).

### 3.1 Adjudication by class

| class | count | verdict and evidence |
|---|---:|---|
| **FRAME** | F 86 · W 151 | **Expected — the whole expected-change list at once.** FRAME is block occupancy *after* global tone normalisation, so it measures composition, and this round changed composition in every scene: ground fill (1,393 kit prims across 37 plans), the veg swap, the ×0.72 plaza tone + `scale_m` 1.80, the leaf globalisation on C2, the railing surgery on 02/15/16 and the tactile Ø35 re-ruling. `w2c_merge_t1_v1.md` §4.2 already ruled FRAME "not a hazard gate in a round whose purpose is a content change". Not adjudicated further per-cut. |
| **PHOTO** | F 13 · W 24 | **Expected — tone.** Every FAIL is a mean drop ≥ 45 LSB and they cluster exactly where the tone work was aimed: scene19 (11 of 16 cuts), sceneC1 (2), plus WARN-level drops of 20–44 on 08/11/17/21/N2. The direction is the intended one — `w80` falls 88→31 (01), 95→27 (05), 97→41 (18), 98→0 (19), 79→29 (20), 86→18 (C1). |
| **OCCL** | **F 2** · W 17 | **Both FAILs are scene19, and both are a photometric collapse on an existing surface, not new geometry.** `entry_gate` 14.97 % new dark / 15.01 % blob (PHOTO mean **108.2 → 61.3**, dark **+22.0 pp**) and `upper_approach` 10.12 / 6.11 (mean **165.7 → 109.0**, dark **+18.1 pp**). The A/B crop shows the change plainly: a large contiguous paved surface that read as bright flagstone in `r2_on` now reads **near-black**, in the same round that removed the only near-white constant in the whole W2-D diff (g3's parapet **(0.90, 0.90, 0.87) → (0.40, 0.40, 0.385)**) and re-toned the membrane. OCCL is computed on raw luminance with no tone matching, so a 2–3× albedo cut on a large surface *is* a large contiguous "new dark" with a large blob — the metric cannot tell that from an occluder, which is why PHOTO fires on the same cut. **It is nonetheless the round's second-worst finding after §4.1**: an intended de-whitening that lands at near-black is a different defect from the one it fixed. Which prim went black is an eyes/owner call — the crop is `s19_flat_membrane_d2.png` plus the `entry_gate` pair. The 17 WARNs are all ≤ 5.62 % new dark with blob ≤ 1.40 %, i.e. the dispersed-shadow signature (rock scatter, veg swap) that §7.2 S4 separates from burial by the blob. |
| **GRAZE** | **F 8** · W 9 | See §3.2 — the only class where the round does not meet its bar. |
| DARK / WHITE / CAPTURE | W 4 / W 1 / INFO | DARK WARNs are scene19's two dark mise-en-scène cuts and the known dark scenes; the single WHITE WARN is the scene20 ON/OFF twin. CAPTURE INFO is the known `manifest ok=false` false positive — all 452 PNGs decode and measure. |

### 3.2 GRAZE — the 8 FAILs, adjudicated by the ruling's own instrument

Ruling §7.5 A3 is explicit: *GRAZE silence is not evidence, and edge integrity is established by a
same-session, same-HEAD ground_kit ON/OFF A/B.* The 8 FAILs are against baselines that predate ~20
W2 commits, so the same test was run in the attribution direction: `NEGOBS_GKIT=0` at HEAD
`fc69706`, same arm, same session `[measured]`.

| scene · cut | vs stale baseline | step b → a (ratio) | vs same-HEAD **GKIT=0** | attribution |
|---|---:|---|---|---|
| `sceneN3 h0.3_d2` | FAIL spec 57.8 | 1.7 → 62.2 (**35.6**) | **UNCHANGED** — mean diff 0.09 LSB, 0.006 % of pixels differ by > 4 LSB; hazard-row step **90.21 → 90.21** | **not ground_kit.** The kit renders essentially zero pixels in this cut; the new line is the trompe-l'œil painting itself re-rendered under the material layer. A *stronger* painted line is the scene's whole purpose (hard negative). |
| `sceneC4 h0.3_d5` | FAIL spec 49.8 | 97.0 → 39.2 (0.404) | **FAIL** spec 60.6, **39.94 → 39.70 (ratio 0.994)**, agree 1.00, dom 0.62 | **ground_kit** — and the line is intact. The 0.404 against the stale baseline is the *baseline's* line, not this one. |
| `scene20 h0.3_d2/d5/d10` | FAIL ×3, spec 43.2 / 37.6 / 48.3 | 4.6→6.3 · 60.3→31.1 · 20.2→23.3 | **PASS ×3** (only a WHITE WARN at d5) | **not ground_kit** — baseline drift, same class as the D2 closure in `w2c_merge_t1_v1.md` §2.1. |
| `scene21 crown_graze` | FAIL spec 33.3 | 10.8 → 10.7 (0.989), **off 54 rows, dom 0.17** | GRAZE deferred, FRAME WARN only | **not ground_kit.** The change sits 54 rows from the hazard row and does not dominate — the v2.1 signature of *a different structure in the E band*, the same reading `w2_tools_v1.md` §4.4 defends for scene17/scene18. |
| `scene14 h0.3_d2` | FAIL spec 25.9 | 42.7 → 58.8 (1.375) | **PASS**, 0.0 % new dark, block shift 1 % | **not ground_kit** — and worth its own line: scene14's 50 kit prims move ~nothing at h0.3. |
| `scene16 h0.3_d10` | FAIL spec 23.4 | 14.3 → 24.8 (1.729) | **FAIL** spec 30.0, **30.13 → 29.30 (ratio 0.972)**, agree 0.95, dom 0.86 | **ground_kit** — the mandated entrance tactile band (−6.0 … −5.4, full walk width) entering the d10 E band. Line intact. |

**The two attributable firings are one gap, and it is structural — filed as D14.**
`ground_kit.EXPECTED_FP` is the GT-E2-x registry whose entire job is to tell the adjudicator *"the
transverse line at these rows is a mandatory tactile band, not the drop edge"*. `grep` over
`scripts/regression_check.py`: **it never reads it** `[measured]`. The registry is consumed only by
`ground_kit`'s own plan-time B7. So every registered mandatory element is, by construction, an
unexplained line to the image-side GRAZE. The two cuts are the two ways that bites:

* **sceneC4** *is* registered — `EXPECTED_FP[('sceneC4','preset_h0.3_d5')] = rows (348, 371)@1080` —
  but the rows are computed at the nominal **0.30 m** setback while the scene deliberately ships the
  **1.00 m** position-error defect, whose true rows the red team measured at d5 **(348, 374)** and
  d10 (297, **308**). This is defect **F4** and `redteam_w2d_edits.md` rider 5 verbatim
  (*"extend the FP window to the actual 1.00 m setback rows … or waive"*) — a **supervisor item**,
  not a new regression.
* **scene16** is *not* registered at all, correctly by the registry's own rule: its trigger is
  `주출입구` (main entrance), which is not in `_FP_TRIGGERS` because a main entrance has no drop
  edge. The band is marked `★ 낙차와 무관 — cue+/label−` in `TACTILE_SITES`. So a deliberately
  drop-unrelated element is judged by the drop detector.

**Not fixed in-round, deliberately.** Wiring `EXPECTED_FP` into the GRAZE adjudicator changes the
verdict function that the 250-cut validation corpora calibrate, so it needs a `valset --check` re-run
and, per rider 5, a supervisor ruling. Two options, costed: **(a)** teach `graze_v2` to mask
registered FP rows — ~30 lines + a corpus re-run, and it also closes F4; **(b)** waive both cuts by
registration and record it. Recommendation: **(a)**, because the registry already carries everything
needed and leaving it inert means every future tactile installation manufactures a GRAZE FAIL.

**Safety statement, stated plainly.** The twin arm's 21 cuts give GRAZE **FAIL 2 · WARN 1 ·
deferred 3 · PASS 15**. The two FAILs sit at hazard-row step ratios **0.972** and **0.994** — the
line is intact to within 3 %. The lowest ratio anywhere in the twin arm is **0.729** (scene21 d10,
GRAZE deferred), and the single WARN is sceneC4 `grazing_mirror` at 0.734 with the change **52 rows
off** the hazard row and dominance **0.09**, i.e. a different structure. The directed burial test in
`w2_tools_v1.md` §4.6 puts a destroyed edge line at **0.01**. sceneN3's d2 pair is the cleanest
single number in the round: ON vs OFF the hazard-row step is **90.21 → 90.21**, dominance 2358 —
the kit does not touch that line at all. **Nothing in this round has the signature of a buried
drop edge.**

---

## 4. Findings that are not gate firings

### 4.1 Blockers — two dead-flat near-field planes `[measured]`

| scene | `flat_gnd` | `flat%` | what the pixels show |
|---|---|---|---|
| **scene19** | **10.0 → 94.8** | 1.5 → 97.3 | The roof membrane renders as an almost pure constant colour: `sd` 9.0 → 7.3, `edge%` 14.3 → 1.4, `struct%` 15.5 → 2.6, `w80` 97.7 → **0.00**. The tone target is met with 40 pp of margin and the surface is now *dead*. Crop `s19_flat_membrane_d2.png`. |
| **scene11** | **10.4 → 53.1** | 9.3 → 64.9 | A large untextured mid-grey plate covers the deck near field with a hard rectangular boundary, where `r2_on` had textured concrete with stains and patches. Crop `s11_flat_plate_d2.png`. |

Both are the failure mode `deadpixel_diag_*.md` exists for, and both are *new this round*. They are
the reason the §7.3 re-baseline below cannot simply celebrate the tone win.

### 4.2 D-5 rock scatter reads as rubble, exactly as predicted

`w2d_kitfix_v1.md` §9-2 warned the pool is 0.16–0.24 m native against the `φ ≤ 0.12` the trail
statistic describes. Confirmed by eye at d5 in **04 / 07 / 10**: the scatter reads as boulders, not
gravel — most starkly on scene10's park trail. The plan side is correct and verified this session
`[measured — recorder harness]`: pool = the 10 procured `Rocks/rock_small_*`, `sink = 0.0121`, and
the D-5 second mechanism is fixed (scene07 `max_count` **270** not the profile's 330, scene10 **120**
not 180); applied instances **04 250 · 07 223 · 10 118 = 591**, matching the kitfix report exactly.
scene10's `LeafRing` correctly still scatters leaves (§9-3). **The lever is `scale_jitter`, a look
call.** Crops `s04/s07/s10_rock_scale_d5.png`.

### 4.3 Carried defects, re-confirmed with fresh evidence

| id | status this round | evidence |
|---|---|---|
| **D3** weeds as olive cubes | **re-confirmed** | `s15_weed_cube_d5.png` — two solid olive boxes at the alley edge. Distant shrubs join the family: scene11's shrub row renders as pale grey lumps where `r2_on` had green foliage (`s11_shrub_grey.png`) — plausibly the `place_shrubs` `/Asset/Flowers` de-activation leaving bare Rhododendron branches. |
| **D4** polygonal manholes | **re-confirmed, worst case is scene01** | `s01_manhole_d5.png` — an unmistakable light-grey **octagon**. Also `sN5_manhole_d2.png`. |
| **D5** declared vs bound albedo | **re-confirmed** | scene01 and scene15 manholes render near-white against a declared 0.10 (`s15_manhole_d5.png`). scene12 adds a variant: the near-field silt/stain decal on a timber deck renders as a **cobblestone** texture. |
| **D11** scene14 parapet V-notch | **re-confirmed at this HEAD** | `s14_vnotch_lower_lookup.png` — both side parapets are a clean saw-tooth against the sky. Unchanged by the material layer, as W2-C §5.6 established. |
| seasonal / bloom | **present but small** | Full-frame pink-bloom census with `graze_recalibration_v1.md` §10's own mask: max **1.05 %** (scene15 `bend_landing`), then 0.96 (18), 0.44 (08), 0.33 (C4); 20 scenes read 0.00. Rhododendron survives `SHRUB_ORNAMENT` on the premise that its flower prims are disabled, and the census says the premise mostly holds. Crop `s16_bloom_planter.png` for the eyes call. |

### 4.4 Positives worth recording

* **R1 (deck planks) is visibly fixed.** `s10_deck_plank_d2.png` and `s12_deck_plank_d2.png` show
  the gaps as clean continuous dark lines. The plate is no longer buried.
* **Railing surgery reads.** 02 and 16 show slender legal handrails where balustrades were;
  15's alley is clean with the meaningless guardrail gone.
* **scene21** `flat_gnd` **40.4 → 9.9** — the worst scene in the library on that metric is now
  among the best. **scene14** 31.3 → 18.6 clears its §7.3 gate.
* **σ_LF** improves in 26/33 and doubles the count of scenes clearing 5.0.
* The single σ_LF regression, **scene08 −20.55**, is not content: `r2_on` scored 24.24 on a
  **diagonal shadow boundary** — the exact inflation `w2_tools_v1.md` §7.1 warns about
  (*"scene08 24.97 = 대각 그림자"*). This round's frame is uniformly shadowed, so the metric returns
  to the material's own figure. Its `mean` 49 does deserve an eyes call on overall darkness.

---

## 5. A1 — §7.3 absolute conditions, re-baselined against this round `[measured]`

Convention reproduced from `t1_material_layer_spec_v1.md` §2.2: median of the scene's three `h0.3`
preset cuts, `imgstats.analyze(lower=False)` for `slope`/`sat_mu`/`flat_gnd`, `near_ground_stats`
for `w80`. Verified against the published triple before use — scene19 `r2_on` reproduces
**−2.66 / 0.028 / 10.0** exactly.

| scene | condition (v1.1) | control at baseline | **this round** | old verdict | **re-baselined condition** |
|---|---|---:|---:|---|---|
| **scene19** | `w80 < 40` | 97.71 | **0.00** | ✘ (87.5 at W2-C) | **MET — retire the condition** |
| | `sat > 0.10` | 0.0282 | **0.1074** | ✘ | **MET — retire** |
| | `slope > −2.45` | −2.6578 | −2.8298 | ✔ at W2-C | **`slope > −2.60`** — the tone work moved it *away*; −2.45 is two steps off |
| | `flat_gnd` ≤ 10.0 | 10.03 | **94.81** | ✔ at W2-C | **`flat_gnd < 20` — promoted to the scene's blocking condition** (§4.1) |
| **scene07** | `slope ≥ −2.25` | −2.3780 | −2.2913 | ✘ | **keep `≥ −2.25`** — 0.036 short, reachable |
| | `sat < 0.24` | 0.2536 | 0.2503 | ✘ | **`sat < 0.26`** — the old line sat 0.0036 from the control; it discriminates nothing |
| | `flat_gnd` ≤ 1.7 | 1.68 | **0.73** | ✔ | **`flat_gnd < 1.0`** |
| **scene14** | `flat_gnd < 20` | 31.33 | **18.63** | ✘ | **MET → `flat_gnd < 15`** |
| | slope toward target | −1.9739 | −2.0004 | ✘ | **MET** — now inside the `imgstats` −2.2…−2.0 band |
| **scene21** (alt) | `flat_gnd < 26` | 40.39 | **9.91** | — | **MET → `flat_gnd < 12`** |
| **sceneC2** | slope not steeper than **−1.75** | −2.0188 | −2.0246 | ✘ (**D13**) | **not steeper than −2.10** |

**D13 closed as a re-baseline.** sceneC2's slope is −2.02 at both the post-merge control and this
round (Δ **−0.0058** over the whole W2-D content round; T1's own contribution was −0.0003). The
−1.75 line was set before leaf globalisation and grass replacement and therefore measures *content*,
not the material layer — which is precisely what W2-C rider 2 predicted would "manufacture
failures". The new line is the control plus a 0.08 working margin.

Spec amendment written to `Docs/briefs/t1_material_layer_spec_v1.md` §7.3 as a `[W2-D]` block; no
other spec text touched.

---

## 6. Artefacts

| what | where | count |
|---|---|---|
| judgement grids | `look_check/<scene>/260730_w2d_judge/` | 33 dirs · **452 PNG** + `manifest.json` + `round_stamp.json` |
| GKIT-off twins | `look_check/_experiments/twins/<scene>/260730_w2d_goff/` | 6 dirs · 21 PNG |
| review gallery | `look_check/_review_w2/<scene>_{h03d5,h09d5,h18d10,beauty}.jpg` + `meta.json` | **132 JPEG** (600 px, q80) · 33 scene records with id / name / profile / one-line gate status / flags / substitution notes |
| eyes-agent crops | `look_check/_experiments/gates/w2d_crops/` + `index.json` | **23 PNG**, each captioned with the single question it answers |
| library sheets | `Docs/audit_v4/library_main21_260730_w2d_judge.png` (3840×3798) · `library_batch1_260730_w2d_judge.png` (3840×1974) | 2 |
| machine gate output | `Docs/reports/regr_260730_w2d.json` | 452 cut records |

`look_check/**` is gitignored — the sheets, this report and `regr_260730_w2d.json` are the committed
record.

### 6.1 Crop index (the eyes agent's worklist)

| crop | question |
|---|---|
| `s10_deck_plank_d2` · `s12_deck_plank_d2` | plank gap reads 2–3 mm (R1 un-burial) |
| `s07_stain_overlap_d2` · `s10_stain_overlap_d2` | R3 residual — is the 0.1 mm inter-stain step big enough to stop shimmer |
| `s04/s07/s10_rock_scale_d5` | D-5 rock scale — rubble vs gravel (§4.2) |
| `sN5_manhole_d2` · `s01_manhole_d5` · `s15_manhole_d5` | D4 octagon · D5 albedo |
| `s15_weed_cube_d5` · `s11_shrub_grey` | D3 proxy geometry |
| `s13_ramp_curb_entry` | gate 13-1 (redefined) — curbs legible in `entry_approach` |
| `s14_vnotch_lower_lookup` | D11 V-notch (both prior analyses in §4.3) |
| `s05_charcoal_d10` · `s05_nearfield_d2` | red-team rider 2 (charcoal band in the d10 E band) · P1 near-field gain |
| `sC4_tactile_d2` · `sN5_tactile_band` | tactile Ø35 — 36 dots, pitch 50 mm |
| `s11_flat_plate_d2` · `s19_flat_membrane_d2` | §4.1 blockers |
| `s16_bloom_planter` | seasonal bloom call |
| `s19_tone_d2` · `s21_tone_d2` | tone targets `w80` |

---

## 7. Open flags handed to the eyes agent and the supervisor

| # | item | who |
|---|---|---|
| **B1** | **scene19 roof membrane is a constant-colour plane** — `flat_gnd` 94.8, `edge%` 1.4, `struct%` 2.6. Blocking. | eyes → fix owner |
| **B2** | **scene11 near-field untextured grey plate** — `flat_gnd` 53.1, hard rectangular boundary. Blocking. | eyes → fix owner |
| **B3** | **scene19 `entry_gate` / `upper_approach` go near-black** — mean −46.9 / −56.7, dark +22.0 / +18.1 pp, a single 15 % contiguous blob. The de-whitening overshot on some prim. Blocking. | eyes → fix owner |
| **D14** | **`EXPECTED_FP` is inert on the consumer side** — `regression_check.py` never reads the GT-E2-x registry, so every mandated tactile band manufactures a GRAZE FAIL (§3.2). Two options costed. | supervisor |
| F4 / rider 5 | sceneC4 FP rows are computed at the 0.30 m nominal setback, not the shipped 1.00 m defect (d5 → 374, d10 → 308) | supervisor |
| rider 2 | scene05 charcoal bands sit inside the d10 E band and GRAZE will fuse them — round judgement still owed (`s05_charcoal_d10`) | supervisor |
| D-5 look | rock scatter reads as rubble in 04/07/10 — lever is `scale_jitter` or dropping rows 02/04/14 | eyes |
| D3 / D4 / D5 | proxy weeds, octagonal manholes, near-white manhole albedo — all re-confirmed with crops | eyes |
| D11 | scene14 V-notch confirmed at this HEAD; scene14 now *passes* its §7.3 `flat_gnd` gate anyway (18.63 < 20), so the §7.3 ★ branch can be closed in favour of keeping scene14 | supervisor |
| §6.2 | default-arm tactile census `P(점형\|낙차) ≈ 3/28` vs §12.6's 0.30–0.45 target — M10 variant renders are load-bearing | supervisor |
| scene08 | frame mean 49 (uniformly shadowed); σ_LF −20.55 is a baseline artefact, not content (§4.4) | eyes |
| bloom | pink-bloom max 1.05 % full-frame; is Rhododendron acceptable in an all-season library | supervisor |

**Not touched, per the mission's exclusions**: D4 ground (M8), hazard-off twins (W5), any spec beyond
the §7.3 table, and no eyes verdict is recorded here — every §4 observation is stated as evidence
plus the measurement, and the verdict is left to the agent that follows.

---

## 8. Commits

| hash | contents |
|---|---|
| `fc69706` | preflight ×5 — scene05 clamp removal, 4 fixture alignments, σ_LF round grading, `valset.py`, baseline chain |
| *(this)* | round drivers + `stamp_round.py` + gallery/sheet/crop tooling + this report + `regr_260730_w2d.json` + the §7.3 amendment |

## 9. Reproduce

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

python3 ground_kit.py                       # exit 0 · 33/33 · fixture prims 1329
python3 scripts/geom_invariance_check.py    # R-5 · R-4 33/33 · R-6 33/33
python3 scripts/valset.py --check           # 3 corpora reproduce w2_tools §4.4

bash scripts/rounds/run_260730_w2d_judge.sh          # 33 scenes, 452 cuts, 27.7 min
bash scripts/rounds/run_260730_w2d_goff.sh           # the 6-scene GKIT=0 attribution arm

python3 scripts/regression_check.py --scenes 'look_check/scene*' \
  --before-round w2c_g2,w2_pilot,r2b_on,wall,facade,r2_on \
  --after-round 260730_w2d_judge --fail-only --json Docs/reports/regr_260730_w2d.json
python3 scripts/near_ground_stats.py \
  'look_check/scene07/260730_w2d_judge/pt_noon_preset_h0.3_d*.png' --median --gate

python3 scripts/make_hq_sheet.py --round 260730_w2d_judge --set main21
python3 scripts/make_hq_sheet.py --round 260730_w2d_judge --set batch1
python3 scripts/make_review_gallery.py --round 260730_w2d_judge \
  --out look_check/_review_w2 --status-json Docs/reports/regr_260730_w2d.json
python3 scripts/rounds/crops_260730_w2d.py
```
