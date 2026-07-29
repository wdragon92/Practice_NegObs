# W2-A1 — Measurement tools rebuild + regression checker v2.1

Written 2026-07-29 · CPU only (numpy + PIL) · **GPU 0 · render 0 · Isaac 0 · SMOKE 0** ·
no git commit/push/checkout · repo files touched = the 4 scripts below + this report.

Evidence tags on every number: `[measured]` this mission computed it from repo pixels/code ·
`[law]` statute/administrative rule · `[stat]` published statistics · `[assumed]` derivation or judgement.

| Deliverable | Path | State |
|---|---|---|
| Normal-map tangent spectrum | `scripts/norm_spec.py` | **new** — 4/4 spec anchors reproduced `[measured]` |
| Near-ground band metrics | `scripts/near_ground_stats.py` | **new** — 31/35 published anchors reproduced `[measured]` |
| Skyline / mid-ground | `scripts/skyline.py` | **new** — 23/23 E-table anchors reproduced `[measured]` |
| Regression checker | `scripts/regression_check.py` | **v2 → v2.1** — second-stage discriminator added (persistence + direction split) |

The three measurement scripts had been lost with a previous scratchpad session
(`redteam_w1_design.md` §2.6 · §5 · §8-1: *"measurement tools gone — a hole common to both specs"*).
They are now authored under `scripts/`, i.e. **the definitions live in code, not in prose**, which
was the stated purpose of `t1_material_layer_spec_v1.md` v1.1 §3.4.

---

## 0. Headline results

| Check | Requirement | Result |
|---|---|---|
| `norm_spec.py` anchors (t1 §3.4(a)) | 4 maps, 1-decimal agreement | **4/4 exact** (+ the §3.2 `plaster` row as a 5th) `[measured]` |
| `near_ground_stats.py` anchors | reproduce published values | **31/35 exact**, 4 near-misses explained (§2.3) `[measured]` |
| `skyline.py` anchor | scene18 runmax = 844 | **844 exact**; 23/23 E §1.6 rows reproduced `[measured]` |
| v2.1 · 92-cut history set | no new FAIL, FAIL ≤ 1 | **FAIL 1 (same cut as v2), WARN 3 → 2, new fires 0** `[measured]` |
| v2.1 · 157-cut false-positive set | WARN ≤ 1 | **WARN 1 → 0, FAIL 0** `[measured]` |
| v2.1 · the two T3 WARN pairs | become quiet | **both quiet** (second-stage persistence rule) `[measured]` |
| v2.1 · injection detection | ≥ 70 % | **NOT MET — 70.4 % → 65.8 %** (retention 93.4 %). Diagnosed in §4.5; escalated as a blocker `[measured]` |
| `GRAZE_SLACK` | stays 2 | **unchanged at 2** (T3's "2→3" option rejected, §4.2c) |

---

## 1. `scripts/norm_spec.py` — normal-map tangent spectrum

### 1.1 What it implements

`t1_material_layer_spec_v1.md` v1.1 **§3.4(a)**, literally, step by step: load without sRGB
de-gamma → tangent components `nx = 2R−1, ny = 2G−1` → **central N=1024 crop at native
resolution, no resampling** → separable Hann with the **window-weighted mean removed first**
(the documented point where every red-team reproduction attempt diverged) → `P = |F_nx|² + |F_ny|²`
→ integer radial rings → **ring-sum weighted** normalisation with DC excluded →
`macro%`, `hf%`, `slope_n`, tangent `RMS`.

`--gate` applies the §3.1 v1.1 thresholds (`macro% < 10`, `−0.9 < slope_n ≤ +0.3`,
`0.12 ≤ RMS ≤ 0.35`, `hf% ≥ 10` advisory) and returns the FAIL count as exit code.

### 1.2 Anchor reproduction `[measured]`

`python3 scripts/norm_spec.py assets/scene01/concrete_wall_nor_dx.jpg assets/scene01/asphalt_nor_dx.jpg assets/scene01/stone_flag_nor_dx.jpg assets/paving_interlock_nor.jpg`

| Anchor map | N | slope_n | macro% | hf% | RMS | published (§3.4(a)) | verdict |
|---|---:|---:|---:|---:|---:|---|---|
| `assets/scene01/concrete_wall_nor_dx.jpg` | 1024 | **−0.71** | **4.1** | **18.9** | **0.056** | −0.71 / 4.1 / 18.9 / 0.056 | **exact** |
| `assets/scene01/asphalt_nor_dx.jpg` | 1024 | **−0.66** | **3.2** | **13.3** | **0.294** | −0.66 / 3.2 / 13.3 / 0.294 | **exact** |
| `assets/scene01/stone_flag_nor_dx.jpg` | 1024 | **−2.46** | **58.4** | **2.5** | **0.192** | −2.46 / 58.4 / 2.5 / 0.192 | **exact** |
| `assets/paving_interlock_nor.jpg` (2048²) | 1024 | **−1.98** | **52.3** | **4.8** | **0.449** | −1.98 / 52.3 / 4.8 / 0.449 | **exact** |

All four agree to the printed precision on every one of the four metrics. A fifth, independent
check: §3.2's adopted `mineral` fallback `assets/scene01/plaster_nor_dx.jpg` reads
**−0.89 / 3.9 / 16.6 / 0.159** against the published −0.89 / 3.9 / 16.6 / 0.159, and `--gate` returns
PASS — including the noted 0.01 margin on the `slope_n > −0.9` floor `[measured]`.
Runtime 1.1 s for four 4K/2K JPEGs, single process `[measured]`.

**Consequence:** the §1.2 library table, the §3.1 gate calibration and the §3.3 β=2.0 procedural
convention (`power ∝ f^−β`, `slope_n ≈ 2 − β`) are all now re-derivable from a committed script.
`assets/gen_detail_normal.py` (spec step 3) can `import scripts.norm_spec` for its self-check
exactly as §3.3 requires.

---

## 2. `scripts/near_ground_stats.py` — near-ground band metrics

### 2.1 What it implements

t1 v1.1 **§3.4(b)** bands and formulas — `B45 = rows[int(0.55·H):]`, `B30 = rows[int(0.70·H):]`,
luminance on **sRGB display values 0–255 (no linearisation)** — plus the two indicators the mission
required that live in other documents:

- **`σ_LF`** = `100 · std(box_downsample(Y/255, 64))` on B30. Box-mean downsample, **no
  interpolation, no padding**; the right/bottom remainder is cropped, because padding manufactures
  fake low-frequency energy at the border (§3.4(b) rule, implemented in `box_downsample`).
- **`flat_gnd`** = `100 · mean(local_std(luma,5)[h//3:] < 1/255)` measured under the `imgstats.py`
  convention (long side resized to 1024, LANCZOS) — the **sole pass/fail indicator** declared by
  t1 v1.1 T1. Reproducing `imgstats` numbers requires reproducing its resize, so the resize is
  in the tool.
- D-team grain/structure columns `edge%` (`|∇L| > 0.02` at native resolution) and `struct%`
  (same threshold after 8× box downsample) on B30, per `D_ground_profile_urban.md` §1.4.
- A `0–5 m` band (`rows[349:]` at 1920×1080 = the h0.3 projection row of 5 m) reproducing
  `D_ground_profile_special.md` §1.2 / Appendix B ①.

Gates (§3.4(b) + `D_ground_profile_natural.md` §2.2): `sd ≥ 32` (target 45) `[stat: real-photo
n=10 minimum]` · `mean ≤ 170` `[stat]` · `>224% ≤ 5` `[stat]` · `wht% < 2` `[project convention
v5.1 §1]` · `flat% < 8` · `σ_LF ≥ 5.0` (target 11.0) `[stat: real-photo n=8 range 5.41–21.56,
median 11.0]` · `flat_gnd < 3.0` `[stat: real-photo n=54, mean 3.881 ± 5.005, median 1.79]`.

> **W2 rule honoured:** `ground_kit_spec_v1.md` §7.1 froze these as **WARN only, never FAIL, in W2**
> (the precedent being the `imgstats` flat%/slope gates set from n=2 and overturned at n=54).
> `--gate` therefore always exits 0 and only prints violations.

### 2.2 A definition conflict found and resolved (honest note)

§3.4(b) writes `wht% = 100·mean(min(R,G,B)/255 > 0.80)` and calls it *"the same definition as §2.2
`w80`"*. The D-team tables it is supposed to reproduce use **luminance L > 0.80**. The two differ:
`scene01 v7_pt h0.3_d2` gives **98.2 (luminance)** vs **97.1 (min-channel)** `[measured]`, and the
published D_urban §2.1 value is **98.2**. The tool therefore reports **both**: `wht%` = luminance
(matches the D tables and this mission's brief) and `w80` = min-channel on the bottom 2/3
(matches t1 §2.2). No number was silently reinterpreted.

### 2.3 Anchor reproduction `[measured]`

Primary anchors — the four indicators the mission named:

| Cut | Metric | Tool | Published | Source | Verdict |
|---|---|---:|---:|---|---|
| `scene01/v7_pt/pt_noon_preset_h0.3_d2` | `L_mu` | 0.865 | 0.865 | D_urban §2.1 | exact |
| 〃 | **`wht%`** | 98.25 | 98.2 | D_urban §2.1 | exact |
| 〃 | **`σ_LF`** | 0.722 | 0.72 | D_urban §2.1 | exact |
| 〃 | `edge%` | 16.39 | 16.4 | D_urban §2.1 | exact |
| 〃 | `struct%` | 5.04 | 5.0 | D_urban §2.1 | exact |
| `scene18/v7_pt/…d2` | **`sd`** / `mean` | 5.72 / 220.8 | 5.7 / 221 | D_natural §2.2 | exact |
| `scene09/v8_pt/…d2` | **`sd`** / `mean` / `>224%` | 13.26 / 208.9 / 3.556 | 13.3 / 209 / 3.56 | D_natural §2.2 | exact |
| `scene17/v8_pt/…d2` | **`sd`** / `mean` | 4.20 / 166.3 | 4.2 / 166 | D_natural §2.2 | exact |
| 〃 | `flat%` | 99.78 | 99.78 | D_natural §2.1 | exact |
| `scene03/v7_pt/…d5` | **`sd`** / `mean` | 35.69 / 144.3 | 35.7 / 144 | D_natural §2.2 | exact |
| `scene12/v8_pt/…d2` | **`sd`** / `mean` | 12.72 / 111.8 | 12.7 / 112 | D_natural §2.2 | exact |

`flat_gnd` — median of the three `h0.3` cuts of `r2_on`, exactly as t1 §2.2 measured `[measured]`:

| Scene | Tool | Published (t1 §2.2) | | Scene | Tool | Published |
|---|---:|---:|---|---|---:|---:|
| scene01 | **1.04** | 1.0 | | scene14 | **31.33** | 31.3 |
| scene06 | **5.65** | 5.6 | | scene19 | **10.03** | 10.0 |
| scene07 | **1.68** | 1.7 | | scene21 | **40.39** | 40.4 |
| scene11 | **10.37** | 10.4 | | sceneC1 | **98.30** | 98.3 |
| scene13 | **12.15** | 12.1 | | sceneC4 | **19.55** | 19.6 |
| sceneD4 | **7.41** | 7.4 | | | | |

**12/12 exact.** Note scene19's three judgement cuts are `d2 / d3.5 / d5` (not `d2/d5/d10`) — using
the wrong triple gives 10.6 instead of 10.0, which is how the correct round/preset set was
confirmed `[measured]`.

Secondary anchors (`D_special` §1.2 0–5 m band): `scene19 r2_on d2` flat 12.94 / >0.8 97.95 vs
published 12.9 / 97.9 — exact; `scene15 r2_on d2` flat 2.55 vs 2.6 — exact. Four rows land close
but not exact (`scene02 d2` 7.03 vs 7.5 · `scene15 d5` 3.67 vs 3.6 · `sceneN5 d2` 92.96 vs 91.6 ·
`sceneD1 d5` 3.86 vs 3.8) `[measured]`. These are cross-round differences, not definition
differences: the D_special table names only `r2_on` while several of those scenes have more than
one `r2*` round, and the same four cuts reproduce exactly on the primary metrics. Recorded as an
open item rather than papered over.

### 2.4 One published number that does **not** reproduce

`D_ground_profile_urban.md` §2.1 carries a `flat%` column (scene01 41.3, scene05 42.2, …) whose
definition is **absent from that document's §1.4 metric table**. No band (B30 / B45 / 0–5 m /
full frame) and no resolution (native / 1024) under the `local_std(·,5) < 1/255` rule reproduces
41.3 — the closest candidates give 0.03–10.2 `[measured]`. Since `flat%` is not one of the four
indicators this mission was told to rebuild, and since the same table's `wht%`, `edge%`, `struct%`
and `σ_LF` all reproduce exactly, the column is flagged for the D-team rather than reverse-engineered.
**Do not use D_urban §2.1 `flat%` as a gate input until its definition is recovered.**

---

## 3. `scripts/skyline.py` — skyline / mid-ground

### 3.1 What it implements

`E_midground_profile.md` §1.6: for each column whose **topmost pixel is sky**, scan down for the
first non-sky row; columns where the sky never opens are excluded from the skyline statistics.
Outputs `sky%` (pixel), `skycol%` (E's *"하늘열%"*), `edge_med`, `edge_std`, `runmax`, `flat_sky`,
and with `--bands` a left/middle/right column split (the S1 three-distance-band labelling needs
prim distances and stays out of scope, as §3.4(c) says).

**Two findings that were required to reproduce the anchor** `[measured]`:

1. **Sky rule.** t1 §3.4(c) prescribes `(B>R) ∧ (B>G) ∧ min(R,G,B)/255 > 0.35`; E §1.6 used
   `(B−R)/255 > 0.030 ∧ (B−G)/255 > 0.012 ∧ B/255 > 0.40`. On `scene18 v7_pt h0.3_d5` these give
   runmax **1269** and **844** respectively. The published anchor is 844, so the **E rule is the
   default** and the t1 rule is kept behind `--sky t1`.
2. **`runmax` requires column adjacency.** "Longest run of columns where the horizon stays flat
   within ±2 rows" has to also require `cols[i] − cols[i−1] == 1`; otherwise the chain hops over
   columns where the sky never opened. Without adjacency, scene16 reads 132 (anchor 66),
   scene03 160 (89), scene10 101 (69), sceneN4 429 (281). With adjacency **all 23 E-table rows
   match exactly**.

### 3.2 Anchor reproduction — E §1.6, `pt_noon_preset_h0.3_d5` `[measured]`

| Scene | Round | 하늘열% | edge_med | edge_std | **runmax** | published runmax |
|---|---|---:|---:|---:|---:|---:|
| **18** | v7_pt | 98.8 | 345 | 110.0 | **844** | **844** |
| 12 | v8_pt | 34.9 | 300 | 27.0 | **664** | 664 |
| 19 | v7_pt | 41.2 | 121 | 39.6 | **452** | 452 |
| 14 | v7_pt | 62.4 | 36 | 54.7 | **405** | 405 |
| D3 | r2_on | 91.1 | 103 | 57.5 | **337** | 337 |
| 09 | v8_pt | 100.0 | 197 | 29.5 | **302** | 302 |
| 04 | v7_pt | 80.2 | 208 | 60.4 | **295** | 295 |
| N4 | wall | 35.3 | 36 | 11.2 | **281** | 281 |
| 17 | v8_pt | 52.4 | 35 | 11.3 | **241** | 241 |
| 01 | v7_pt | 48.7 | 41 | 88.4 | **234** | 234 |
| 06 | v8_pt | 26.4 | 198 | 112.9 | **225** | 225 |
| 05 | v8_pt | 25.3 | 156 | 35.7 | **193** | 193 |
| 02 | v7_pt | 53.2 | 148 | 76.5 | **188** | 188 |
| 20 | v7_pt | 17.7 | 315 | 89.5 | **178** | 178 |
| 21 | v7_pt | 39.2 | 63 | 99.3 | **117** | 117 |
| 13 | v7_pt | 11.3 | 49 | 19.8 | **91** | 91 |
| 03 | v7_pt | 45.1 | 172 | 128.0 | **89** | 89 |
| 10 | v8_pt | 8.3 | 4 | 2.9 | **69** | 69 |
| 16 | v7_pt | 38.7 | 55 | 108.2 | **66** | 66 |
| 11 | v8_pt | 45.2 | 44 | 38.5 | **64** | 64 |
| N5 | r2_on | 23.5 | 62 | 43.9 | **57** | 57 |
| C1 | r2b_on | 15.2 | 5 | 26.0 | **44** | 44 |
| C2 | fix1 | 91.9 | 110 | 54.8 | **27** | 27 |

**23/23 exact on runmax; 23/23 on 하늘열%/edge_med/edge_std as well** once the correct round is used
(scene11 = `v8_pt`, sceneC1 = `r2b_on` — both identified by matching all four columns simultaneously).
The tool prints `OK` / `칼절단` against the E §1.6 target `runmax ≤ 320` `[assumed: E derivation,
frame width ÷ 6 = 10.0°]`, and `n/a` when the sky opens in fewer than 20 % of columns.

---

## 4. `scripts/regression_check.py` v2.1

### 4.1 Scope of the change

**Only the GRAZE verdict path changed.** The band geometry (E/guard/N), the signal
(`Δcoh` = column mean of the vertical-step field difference after global tone matching), the
thresholds (`SPEC_WARN 8.0`, `SPEC_FAIL 20.0`, `AGREE_MIN 0.70`, `BAND_MU_MIN 35`, photometry
deferrals) and **`GRAZE_SLACK = 2`** are v2 verbatim. DARK/BLOWN/WHITE/OCCL/FRAME/PHOTO/UNCHANGED
are untouched. The CLI is unchanged.

### 4.2 What was added

The two additions collapse into **one second-stage rule** applied to a firing that already passed the
v2 stage. This is what T3 §3.4-2 itself asked for (*"implementing proposal 2 in this form solves the
burial direction as well"*).

**Measurement.** At the **hazard row ± `GRAZE_SLACK`** — *not* at the row of maximum change — the
checker records the absolute vertical step in the before frame (`gz_step_b`) and in the after frame
(`gz_step_a`), both from the same smoothed column-mean step profile the v2 signal is built from,
plus `gz_step_ratio = after/before`, `gz_step_off = |max-change row − hazard row|` and
`gz_step_dom = step_after / dE`. Using the hazard row is literal T3 (*"at the drop row ± slack"*)
and it matters: measured this way the tool reads **98.9 → 65.4** for scene13 and **101.1 → 95.6** for
scene07, against T3's manual native-resolution readings of 115.9 → 67.8 and 109.6 → 86.4 `[measured]`.

**(a) Edge-persistence.** `step_before ≥ GRAZE_STEP_MIN = 25` **and** `step_after ≥ 25` — the line
is present in both rounds, so what changed is the albedo on either side of it, not the occlusion state.

**(b) Direction split by step ratio.** `ratio > 1.0` (the line got *stronger*) is exposure and always
fires — the v2 column-agreement gate decides it, untouched. `ratio ≤ 1.0` is the burial direction and
is quieted only while `ratio > GRAZE_BURY_RATIO = 0.50`, i.e. the line weakened but did not collapse.
T3 measured 0.585 / 0.788 for realism albedo swaps; a real burial goes to ≈ 0 (the directed test in
§4.6 measures **0.01**) `[measured]`. Note this also **reclassifies scene07**: v2's `up` flag called it
exposure from the max-change row, but at the hazard row its step *fell* (101.1 → 95.6), which is the
signal T3 read by hand. Verdict wording now follows the hazard-row ratio for the same reason.

**Two guards beyond the brief — required, and measured.** T3's claim that *"detection power is
preserved, because a real burial collapses the after step"* holds only for the burial direction and was
never checked against the §6 exposure injections. An unguarded literal reading drops injection
detection from **70.4 % to 46.8 %** `[measured]`. Two necessary conditions restore it to 65.8 %:

- `gz_step_off ≤ GRAZE_PERSIST_ROWTOL = 4` — the change must sit **on** the persisting line.
  T3's two cases measure 3.3 and 3.7 rows; the firings that must survive measure 74.7 (scene17),
  36.7 (scene18) and 30.3 (scene19), i.e. their change is a *different* structure in the E band `[measured]`.
- `gz_step_dom ≥ GRAZE_PERSIST_DOM = 3.5` — the surviving line must dominate the change.
  T3's cases measure 3.97 and 6.41; a newly revealed riser has a change comparable to the line's own
  contrast, so its dominance is low `[measured]`.

**FAIL is never demoted.** The second stage only touches WARN-level firings, per the brief's wording
(*"quiet the GRAZE warn"*). scene18's FAIL is structurally untouchable.

**(c) `GRAZE_SLACK` stays 2.** T3's third proposal (2 → 3) is **rejected**: the persistence rule already
silences the scene07 boundary case, and T3 itself conditioned the slack change on *"re-running the
844-cut injection trial first"*. Changing the slack would invalidate the v2 detection evidence for no
additional benefit.

All judgements are stamped `[v2.1]`; new JSON metric keys `gz_step_b`, `gz_step_a`, `gz_step_ratio`,
`gz_step_off`, `gz_step_dom` join the existing `gz_*` set (no key removed).



### 4.3 Validation — corpus reconstruction (honest note)

`graze_recalibration_v1.md` §5 records only the **counts** per series, not the pair membership, so
the two validation corpora were rebuilt from the round directories and cross-checked against the
published v2 outcome. The reconstruction is exact on the false-positive set and +2 cuts on the
history set `[measured]`:

| Corpus | Series | Cuts (this rebuild) | Cuts (doc) |
|---|---|---:|---:|
| **False-positive set** | mode swap · look A/B · ctx1→ctx2 · realism r1_on→r2_on · P4 near-field | 12 · 42 · 44 · 40 · 19 = **157** | 11 · 42 · 44 · 39 · 21 = 157 |
| **History set** | `v6_rt→v7_rt` (68) + `v7_rt→v8_rt` (26) | **94** | 67 + 25 = 92 |

Running **v2 unchanged** on these corpora returns the published v2 result exactly — false-positive
set `FAIL 0 · WARN 1`, history set `FAIL 1 · WARN 3` `[measured]` — which is what licenses the
reconstruction as a valid baseline. The +2 on the history set are cuts the original enumeration
apparently dropped; they are PASS under both versions, so they do not affect any conclusion.

### 4.4 Validation — results `[measured]`

| Corpus | v2 | **v2.1** | Requirement | Met |
|---|---|---|---|---|
| History set (94 cuts) | FAIL 1 · WARN 3 · deferred 22 | **FAIL 1 · WARN 2 · deferred 23** | no new FAIL, FAIL ≤ 1 | **yes** |
| False-positive set (157 cuts) | FAIL 0 · WARN 1 · deferred 10 | **FAIL 0 · WARN 0 · deferred 11** | WARN ≤ 1 | **yes** |
| T3 pair scene13 `v6_rt→v7_rt d5` | WARN (spec 15.7) | **quiet** | quiet | **yes** |
| T3 pair scene07 `r1_on→r2_on d2` | WARN (spec 12.4) | **quiet** | quiet | **yes** |

**New firings introduced by v2.1: 0** — every v2.1 WARN/FAIL was already a v2 WARN/FAIL `[measured]`.

Per-cut disposition of every v2 firing in the two corpora:

| Pair · cut | spec | agree | step before → after | ratio | v2 | v2.1 | why |
|---|---:|---:|---|---:|---|---|---|
| scene18 `v6_rt→v7_rt` `h0.3_d2` | 67.6 | 0.89 | 11.1 → 14.8 | 1.33 | FAIL | **FAIL** | FAIL is never demoted; also no line at the hazard row (11.1 < 25) and the change sits 36.7 rows away — genuine content change (E-band buildings removed) |
| scene17 `v6_rt→v7_rt` `h0.3_d2` | 10.2 | 0.89 | 38.4 → 41.5 | 1.08 | WARN | **WARN** | ratio > 1 (exposure) **and** the change sits 74.7 rows off the hazard row — a different structure really did change |
| scene19 `v6_rt→v7_rt` `h0.3_d5` | 11.1 | 0.73 | 0.58 → 0.56 | 0.96 | WARN | **WARN** | there is no line at the hazard row at all (0.58 < 25); change 30.3 rows away. Kept — v2 and v2.1 agree |
| scene13 `v6_rt→v7_rt` `h0.3_d5` | 15.7 | 0.97 | **98.9 → 65.4** | 0.66 | WARN | **quiet** | line persists (off 3.3, dominance 4.0) — albedo swap |
| scene07 `r1_on→r2_on` `h0.3_d2` | 12.4 | 0.82 | **101.1 → 95.6** | 0.95 | WARN | **quiet** | line persists (off 3.7, dominance 6.4) — albedo swap |

The three surviving firings are the ones the recalibration report itself defended as genuine
(`graze_recalibration_v1.md` §7: scene18 *"real change… the warning is correct"*, scene17
*"pure edge-band change with 0.0 near-field change… plausible for a fill round"*).

### 4.5 Validation — detection power (injection trial)

`graze_recalibration_v1.md` §6 injects a riser of height δ revealed at distance d: the band between
`row(d,h)` and `row(d,h+δ)` is multiplied by a self-shadow factor f ∈ {0.70, 0.80, 0.90}. The model was
re-implemented literally and applied to **33 scenes × 3 `h0.3` presets × 3 f × 6 δ = 1,782 synthetic
cuts** (`r2_on` as the base round). Synthetic images live in the scratchpad only.

**The reconstruction validates itself against the published v2 figure.** Counting only cuts where
GRAZE actually adjudicates (deferrals excluded, as the published 844-cut set did — §6 notes
*"20 cuts were deferred outright"*), **v2 scores 70.4 %** against the published **70.5 %**, and two
per-riser rows land exactly on the published values `[measured]`:

| Riser δ | cuts | **v2** | published v2 | **v2.1** |
|---:|---:|---:|---:|---:|
| 0.03 m | 288 | 82.3 % | 85.4 % | **78.5 %** |
| 0.05 m | 288 | **86.8 %** | **86.8 %** | **84.4 %** |
| 0.10 m | 288 | **86.1 %** | **86.1 %** | **83.0 %** |
| 0.20 m | 288 | 75.7 % | 79.2 % | **68.8 %** |
| 0.40 m | 288 | 60.1 % | 54.9 % | **51.7 %** |
| 0.80 m | 248 | 25.0 % | 24.2 % | **22.2 %** |
| **all** | **1,688** | **70.4 %** | **70.5 %** | **65.8 %** |

**Requirement not met.** v2.1 retains **93.4 %** of v2's detections but lands at **65.8 %**, 4.6 pp
below the 70 % floor. This is reported rather than tuned away, and the cause is specific:

> **The §6 injection darkens the strip *below* the lip row.** In most scenes that strip is the bright
> near ground, so the injection makes the hazard-row step **smaller**, not larger — median step ratio
> 0.8 over the injected corpus `[measured]`. That is the same signature as the T3 albedo swaps
> (0.66, 0.95). Any gate that silences T3 therefore silences part of the synthetic corpus; the two
> populations are not separable by step magnitude, step ratio, row offset, agreement or spec
> (an exhaustive sweep over those five features is in the session scratchpad) `[measured]`.

The two guards documented in §4.2 recover most of the loss — an unguarded literal reading of the
edge-persistence rule collapses detection to **46.8 %** `[measured]`. What remains is concentrated
where §6 itself delegates authority elsewhere: the 0.40/0.80 m rows (*"deliberately delegated to
PHOTO/OCCL/FRAME"*) lose 8.4 and 2.8 pp, while the band §6 calls the important one — 3 to 10 cm,
*"the size a human scanning a grid sheet is most likely to miss"* — stays at **78.5 / 84.4 / 83.0 %**.

Excluding the two delegated rows, v2.1 scores **78.7 %** on δ ≤ 0.20 m (v2: 82.7 %) `[measured]`.

**Escalated for a supervisor decision** — three options, in order of the author's preference:

1. **Accept 65.8 % and re-derive on a rendered positive.** §11-3 of the recalibration report already
   states that one real hidden-drop regression is worth more than the whole injection table. The
   injection model is a synthesis whose artefact is now measured and documented.
2. **Fix the injection model** so the revealed riser *replaces* rather than *darkens* the strip
   (i.e. removes the near-ground content it occludes). That needs a GPU-owner or an agreed synthesis
   rule; it changes the evidence base for v2 as well, so it cannot be done unilaterally here.
3. **Scope the second stage to the burial direction only.** Detection would be preserved exactly,
   but scene07 `r1_on→r2_on d2` would keep firing — i.e. one of the two T3 requirements would fail
   instead. The two requirements are mutually exclusive under the current injection model.


### 4.6 Directed test of gate (b)

The validation corpora contain **no natural burial-direction case** that survives stage 1, so the
burial branch was exercised with a controlled synthetic triple built on a real cut's camera
(`scene12 r2_on`, three presets). Two-tone frames: above the lip row L=60, below L=180 (step 120).

| Variant | construction | step before → after | ratio | v2.1 verdict |
|---|---|---|---:|---|
| **burial** | lip row ±30 rows overpainted with the upper tone — **the line is destroyed** | 106.7 → 1.2 | **0.01** | **FAIL** (spec 70.9–81.5) `[measured]` |
| **albedo swap** | 60→75 above, 180→150 below — **the line survives** | 106.7 → 106.7 | 1.00 | **PASS** `[measured]` |

Two things are confirmed: (i) a destroyed edge line is still caught, at FAIL severity, with the step
ratio pinned at 0.01 — the second stage does not block burial detection; (ii) a *global* two-tone
albedo swap never reaches the second stage at all, because v2's percentile tone matching already
removes it (spec ≈ 0). The T3 cases survived stage 1 precisely because their albedo change was
**spatially partial**, which is what the second stage exists to adjudicate.


---

## 5. Limits and open items

1. **Injection detection lands at 65.8 %, not ≥ 70 %** (§4.5). Under the §6 synthesis model the
   T3 albedo swaps and the synthetic exposures are not separable, so quieting the former necessarily
   costs some of the latter. **Supervisor decision needed** — accept and re-derive on a rendered
   positive / fix the injection model (needs the GPU owner) / scope the second stage to burial only
   and give up the scene07 requirement. Nothing was tuned to hide this.
2. **The burial branch has no natural corpus.** Across 251 validation cuts every silenced firing was
   an albedo-swap case; the `GRAZE_BURY_RATIO` boundary itself never decided a real event
   `[measured]`. Its calibration rests on two T3 field measurements plus the directed test in §4.6.
   The first genuine burial-direction regression should be used to re-derive it
   (`graze_recalibration_v1.md` §11-3 already says a single real positive is worth more than the
   whole injection table).
3. **`GRAZE_PERSIST_ROWTOL` and `GRAZE_PERSIST_DOM` are fitted to n=2.** Both guards separate T3's
   two cases (3.3/3.7 rows, dominance 3.97/6.41) from the survivors and the injections, but two
   positive examples is exactly the sample size that produced the `imgstats` gate reversal this
   project already lived through. Re-derive when more adjudicated cases exist.
4. **`D_urban` §2.1 `flat%` is unreproducible** (§2.4). Flagged to the D-team; not usable as a gate.
5. **Four `D_special` §1.2 secondary anchors are close but not exact** (§2.3) — almost certainly a
   round-naming ambiguity in that table, not a definition problem.
6. **The two sky rules disagree** (§3.1). `skyline.py` defaults to the rule that reproduces the
   published anchors; t1 §3.4(c) should be amended to match, or the E table re-measured. Either way
   **both rules break if the HDRI changes** — the `qwantani_noon_puresky` dependency is now a
   documented, testable assumption instead of a buried one.
7. **The validation corpora are reconstructions** (§4.3), validated by reproducing the published v2
   outcome. If the original pair lists resurface, re-run and compare.
8. `near_ground_stats.py` gates stay **WARN-only** by the §7.1 ruling. Do not wire them to a
   non-zero exit code before W4 without a supervisor decision.

## 6. Reproduction commands (all CPU)

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs

# §1 normal-map spectrum (4 anchors)
python3 scripts/norm_spec.py assets/scene01/concrete_wall_nor_dx.jpg \
        assets/scene01/asphalt_nor_dx.jpg assets/scene01/stone_flag_nor_dx.jpg \
        assets/paving_interlock_nor.jpg
python3 scripts/norm_spec.py 'assets/**/*_nor*.jpg' --gate      # §3.1 pass/fail sweep

# §2 near-ground band (anchors + flat_gnd median)
python3 scripts/near_ground_stats.py \
        'look_check/scene01/v7_pt/pt_noon_preset_h0.3_d2.png' --gate
python3 scripts/near_ground_stats.py \
        'look_check/scene14/r2_on/pt_noon_preset_h0.3_d*.png' --median

# §3 skyline (anchor scene18 = 844)
python3 scripts/skyline.py 'look_check/scene18/v7_pt/pt_noon_preset_h0.3_d5.png' --bands

# §4 regression v2.1 — the two T3 pairs are now quiet
python3 scripts/regression_check.py --before look_check/scene13/v6_rt \
        --after look_check/scene13/v7_rt --only preset_h0.3
python3 scripts/regression_check.py --before look_check/scene07/r1_on \
        --after look_check/scene07/r2_on --only preset_h0.3
```

The corpus drivers and the injection synthesiser live in the session scratchpad
(`valset.py`, `inject.py`, `gate_b_test.py`) — synthetic images are never written into the
repository, per `graze_recalibration_v1.md` §6.
