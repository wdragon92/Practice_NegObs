# Red-team Verification — W2 Foundations (pre-GPU gate)

Date 2026-07-29 · Mission RT · CPU only (numpy + PIL; **GPU 0 · render 0 · Isaac 0 · SMOKE 0**).
No git commit/push/checkout. Files touched by this mission: **this report only** (all scratch
work in the session scratchpad; one throwaway regeneration of the detail-normal PNGs was
written to scratchpad, never to the repo).

Method: **re-execution, not re-reading.** Every table below was produced by running the
builders' deliverables (or an independent reimplementation) in this session and comparing
against the published numbers and the governing spec text.
Tags: `[measured]` computed here · `[calc]` closed-form from the verified frame model ·
`[law]` statute/spec-mandated · `[assumed]` stated inference.

## 0. Verdicts

| Builder | Deliverable | Verdict | One line |
|---|---|---|---|
| W2-A1 tools | `scripts/{norm_spec,near_ground_stats,skyline,regression_check}.py` | **CONFIRMED** | Every anchor and corpus claim reproduces; the self-declared injection-floor failure is real (my independent rerun: 65.7 % vs their 65.8 %) and honestly reported |
| W2 surgeon | worktree `Practice_NegObs_w2wt` (branch `w2-surgeon`) | **CONFIRMED** | R-5/R-4/R-6 re-run 0 · 33/33 · 33/33; ledger edits match the audits and the manifest; main tree untouched |
| W2-A3 ground_kit | `ground_kit.py` + 3 pilot scenes + `scene_common` P-A | **PARTIAL** | Code and gates verify (self-check exit 0; independent B6/B7/B8 clean), but two published GPU-phase gate numbers are wrong/ambiguous and must be read from §4 of this report instead |
| W2-A4 vegetation | 20 USD assets + grass swap + manifest | **CONFIRMED** | 17 textures pixel-re-verified here, hue tables reproduce, rejects really deleted, downloader idempotency re-run 132/132 + 75/75 |
| W2-A5 materials | `gen_detail_normal.py` + 3 maps + MDL v1.9.0 | **CONFIRMED** | Byte-reproducible 3/3 MD5, all §3.1 gates re-measured PASS, MDL parameter surface 66-identical + 8 appended, default-inertness verified in source |

CONFIRMED = the GPU pilot phase may consume it as delivered. PARTIAL = consumable **with the
corrections in §4.4 applied** (one-line report fixes, no code change required before pilots;
one supervisor ruling requested).

---

## 1. W2-A1 — measurement tools + regression v2.1

### 1.1 Anchors, all re-run `[measured]`

- `norm_spec.py`: **4/4 spec anchors exact** (`concrete_wall` −0.71/4.1/18.9/0.056 ·
  `asphalt` −0.66/3.2/13.3/0.294 · `stone_flag` −2.46/58.4/2.5/0.192 ·
  `paving_interlock` −1.98/52.3/4.8/0.449) plus `plaster` −0.89/3.9/16.6/0.159 → PASS.
  Formula diff against t1 v1.1 §3.4(a): step-for-step faithful (no de-gamma, native N=1024
  central crop, window-weighted mean removed before Hann, ring-sum normalisation, DC excluded,
  slope over 3 ≤ r < N/4, RMS pre-window).
- `near_ground_stats.py`: primary anchors **exact** — scene01 `v7_pt d2` L_mu 0.865 /
  wht% 98.2 / σ_LF 0.72 / edge% 16.4 / struct% 5.0; sd/mean rows for scenes 18 (5.7/221),
  09 (13.3/209, >224 % 3.56), 17 (4.2/166 + flat% 99.78), 03 d5 (35.7/144), 12 (12.7/112);
  `flat_gnd` medians **11/11 exact** on `r2_on` (01 1.0 · 06 5.6 · 07 1.7 · 11 10.4 ·
  13 12.1 · 14 31.3 · 19 10.0 · 21 40.4 · C1 98.3 · C4 19.6 · D4 7.4; scene19 uses its real
  d2/d3.5/d5 triple). Formula diff vs §3.4(b): faithful, incl. crop-not-pad σ_LF and the
  imgstats 1024-resize convention for flat_gnd.
- `skyline.py`: **23/23 runmax rows exact** (scene18 = 844) together with 하늘열 %/edge_med/
  edge_std, using the E §1.6 sky rule and the column-adjacency runmax the builder documented.

### 1.2 The two definition conflicts the builder reported are real `[measured]`

- `wht%`: t1 §3.4(b) prescribes min-channel; the D-tables it must reproduce are luminance
  (98.25 luminance vs 97.1 min-channel on the scene01 anchor). Tool emits both — correct call.
- Sky rule: t1 §3.4(c) vs E §1.6 give runmax 1269 vs 844 on the same cut; the published
  anchor is 844. Tool defaults to the E rule with `--sky t1` retained — correct call.
- `D_urban §2.1 flat%` (41.3): my own sweep over band × resolution × threshold under the
  `local_std(·,5) < 1/255` rule found nothing near 41.3 (gradient-rule variants land 45–52,
  also not 41.3) — **unreproducible, do not gate on it** — builder's claim stands.

### 1.3 Regression checker v2.1 `[measured]`

- Code diff HEAD(v2) → v2.1: **92 changed lines, all inside the GRAZE path**; band/signal/
  thresholds (`SPEC_WARN 8 · SPEC_FAIL 20 · AGREE_MIN 0.70 · BAND_MU_MIN 35 · GRAZE_SLACK 2`)
  byte-identical; step measured at hazard row ± slack as T3 §3.4-1 words it; FAIL never
  demoted (second stage requires `sev == WARN`); JSON keys added, none removed.
- T3 pairs: scene13 `v6_rt→v7_rt d5` (v2 WARN spec 15.7) and scene07 `r1_on→r2_on d2`
  (v2 WARN 12.4) both **quiet under v2.1** — re-run here, verdict lines inspected.
- History set re-run (`--scenes` v6_rt→v7_rt 68 cuts + v7_rt→v8_rt 26): v2 GRAZE = FAIL 1
  (scene18 d2) + WARN 3 → v2.1 = FAIL 1 + WARN 2 (scene13 quieted). **New fires: 0.**
- FP-set series re-run: ctx1→ctx2 44 cuts — 0 fires both versions; realism r1_on→r2_on
  (112 GRAZE-target cuts, superset of the builder's 40) — v2 WARN exactly 1 (scene07 d2),
  v2.1 **0**. Structurally v2.1 can only quiet, never add (verified in the diff), so the
  builder's "no new fires anywhere" claim holds by construction and by measurement.
- **Injection trial independently re-implemented** (my own §6 synthesis on `r2_on`, 33 scenes
  × 3 h0.3 cuts × 3 f × 6 δ = 1,782 rows; deferral structure reproduced **exactly** at
  1,688 adjudicated / 94 deferred):

| δ (m) | my v2 | builder v2 | published v2 | my **v2.1** | builder v2.1 |
|---:|---:|---:|---:|---:|---:|
| 0.03 | 84.4 | 82.3 | 85.4 | 79.9 | 78.5 |
| 0.05 | 87.5 | 86.8 | 86.8 | 84.0 | 84.4 |
| 0.10 | 84.4 | 86.1 | 86.1 | 80.6 | 83.0 |
| 0.20 | 76.7 | 75.7 | 79.2 | 68.4 | 68.8 |
| 0.40 | 61.1 | 60.1 | 54.9 | 51.7 | 51.7 |
| 0.80 | 25.0 | 25.0 | 24.2 | 23.8 | 22.2 |
| **all** | **70.9** | 70.4 | 70.5 | **65.7** | 65.8 |

  Two independent implementations agree to ≤ 1.5 pp per row. **The ≥ 70 % requirement is
  genuinely not met by v2.1** (−5.2 pp vs v2 in my rerun), the loss concentrates in the
  0.2–0.8 m rows §6 delegates to PHOTO/OCCL/FRAME, and the 3–10 cm band stays ≈ 80–84 %.
  The three supervisor options in `w2_tools_v1.md` §4.5 are the correct decision frame; the
  failure is a property of the §6 synthesis overlapping the T3 albedo-swap signature, exactly
  as diagnosed. (The "unguarded 46.8 %" and the five-feature separability sweep were not
  re-executed — scratchpad-only artifacts `[assumed]`.)

**Finding T-1 (minor, latent).** `norm_spec.verdict()` counts `hf% < 10` toward the FAIL
exit code, but §3.1 marks hf% "판정용 아님 — 교차 확인용" (cross-check only). No anchor or
delivered map flips today (all hf failures co-occur with primary-gate failures), but a future
map could FAIL on the advisory metric alone. One-line fix when convenient.

---

## 2. W2 surgeon — worktree

- **Harness re-run by me** in the worktree: R-5 **0 violations** outside the 3-line compat
  shim (39 files) · assembly 33/33 on all three arms · **R-4 33/33 · R-6 33/33** `[measured]`.
  sceneC2 records 3,924 prims — consistent with the G2 +1,782 instance claim (2 prims ×
  (1,784 − 893)). Negative-control (seeded-fault) runs were not repeated — they require
  editing worktree files, which this mission forbids; §2.4 of the surgeon report documents them.
- **R-5/R-6 semantics checked in source**: tokenize-based scan excludes comments/strings;
  allow-list keyed on file+count (line drift observed 182→189 confirms that design choice).
- **Veg ledger vs audits** `[measured]`: `VEG_DEBRIS` equals B-audit A3 verbatim
  ((0.0584, 9175) (0.0239, 2980) (0.0081, 631) (0.0048, 496) (0.0054, 582)); Japanese_Cherry
  removed from `VEG_TREES`; the three new rows' `native_h` equal manifest z_max
  (3.0867 / 10.8989 / 2.5164 — cross-checked against manifest z-size − z_min); `veg_pool()`
  filters by file existence (the file-deletion trap is closed); `SHRUB_ORNAMENT` =
  {Rhododendron, Juniper}; `place_shrubs` unpacks 5 fields, scales by native **height**,
  grounds with `zmin·s`, and calls `_deactivate_seasonal` (Rhododendron → "Flowers")
  **before** `SetInstanceable(True)`. No scene passes Burning_Bush/Forsythia pools.
- **Grass/LOOK**: `TEX["grass"]` → `grass_lawn_*`; zero `aerial_grass_rock` references in the
  worktree tables; `LOOK_MTL/GEO` split present with `LOOK_V1=1` compat.
- **Leaf G2 vs ground spec §8.4** `[measured/calc]`: 5 non-overlapping rects, `edge_bias=0`,
  fallcluster-only pool, per-rect seeds, caps ≈ 1.15 n; side rects at 2.60 ≤ |y| ≤ 3.60 make
  the relocated wear band (`y = ±3.60`, x −3.76…6.26) sit on a real boundary. The 1,784 vs
  1,689 delta is exactly the A3 coverage re-ledger (1,689 × 0.0435/0.04115 = 1,786 ≈ 1,784).
  Note: §8.4's own rect-1 range column says "|y| ≤ 3.60" while its n = 998 implies |y| ≤ 2.60
  — spec-table typo, the implementation matches the n-consistent geometry.
- **scene01 unification vs lighting spec §2.7/§7** `[measured]`: local lookfix deleted
  (aliased to `sc.ensure_noon_lookfix`), `sc.setup_lighting` / `sc.grid_views(−2.75)` /
  `sc.TEX` delegation in the file; sun cap default 0.6° with the env-overridable cache-key fix
  (`_lookfix.exr` legacy for 1.5, `_lookfix_cap{x}.exr` otherwise) — precisely §7 item 3.
- **Nothing outside the worktree touched** `[measured]`: main-tree `scene_common.py` contains
  zero `LOOK_MTL/LOOK_GEO/grass_lawn` tokens and its whole diff is the ground_kit P-A hunk
  (§3.1); the worktree's untracked asset entries are **symlinks into** the main tree, not
  copies; surgeon's touched-file list (33 scene/kit files) excludes sceneD4/D1/D2/15.
- Cosmetic: report header says "34 files, +1,346/−302"; `git diff --stat` shows 35 files,
  +1,767/−302 (the baseline JSON + report itself account for the difference).

---

## 3. W2-A3 — ground_kit (verdict PARTIAL; corrections in §4.4)

### 3.1 What re-executes cleanly `[measured]`

- `python3 ground_kit.py` **exits 0**; 33/33 hard gates; pilot rows match the report
  (scene15 47 prims / B2 83.2 %; scene13 δmax 0.1200 with the single `gt_changes` record;
  apply/plan prim round-trip equal; all prims under `GKit`).
- Main-tree `scene_common.py` diff is **exactly** the P-A mechanism: `SKIN_EXCLUDE` set +
  `skin_exclude()` + 3-line guard as the first statement of `_skin_wanted` + `"gkit"` appended
  to `_SKIN_DENY` (+20/−1, nothing else). `py_compile` clean on all five touched files;
  `scenes/{main,batch1}/ground_kit.py` are real symlinks.
- **M4**: the only GT change anywhere is scene13 `ramp_curb` h 0.12; `apply_ground` raises
  unless the `gt_changes` ledger carries it (code path read); handoff print present.
- **M9-ⓑ**: scene15 manhole at (−4.00, −0.15) sits inside the d5 W1 window
  x ∈ [−4.436, −3.0] `[calc]`; the d2 window is carried by patch #1 (−1.20).
- **§12**: pilots place tactile only where ruled — N5 bollard band ON (0.60 m × 7.0 m,
  `tactile_yellow` texture role), scene15 OFF (p ≈ 0.05), scene13 wired but behind
  `cue_tactile=False`. Registry counts (K_h 9 / K_n 4 / P = 0.321) match §12.6.
- **Independent B6/B7/B8 recompute** from the scene-diff coordinates (my own trigonometry,
  no gk helpers): B6 GT-E1′ violations **0**; B8 void intersections **0**; scene13
  beyond-crest elements are **all d2-only** (8 elements; h/d = 0.150/0.060/0.030 vs grade
  0.085) `[calc]`; B7 violations **0 under the spec's own worked-example convention** — see
  finding G-1. N5 manhole width 1,267.6 px = 66.02 % at d2 and scene13 manhole 979.6 px =
  51.0 % at d5 reproduce to the pixel `[calc]`.

### 3.2 Finding G-1 — GT-E2 "16 rows" is applied at half its derived strength (spec defect, not implementation defect)

The spec derives 16 from GRAZE-checker constants "(HW 3 + SMOOTH 3 + SLACK 2) × 2" — those
constants live on the checker's **960-px/540-row** working image (T3 prints bands as
"y131~212/**540**"). But the spec's own worked example C-1′ computes rows at **1080** scale
("row 297.97 … Δ = 16.05행 → PASS"), and `ground_kit.cam_row` follows the worked example
(CAM_H = 1080). 16 rows @1080 = **8 rows @540 = exactly the filter footprint radius**, i.e.
adjacent lines are allowed to sit where the two responses have just stopped overlapping —
not the "fully separated" 16-@540 the derivation argues. Measured on the pilots: three lines
sit inside the half-separation zone Δ@540 ∈ [8, 16) — scene13 `Joints/JX_3` d10 (10.9),
scene13 `Trench_0/Frame` d2 (9.1), scene15 `Joints/JX_3` d10 (10.9) `[measured]`; all pass
at @1080 (21.8 / 18.2 / 21.8). The implementation is faithful to C-1′; the **spec must state
the row scale** (and if 540 is ruled normative, `GRAZE_ROW_SEP` effectively doubles and those
three pilot lines plus the C-1′ trench itself need re-layout). Supervisor ruling requested.

Corollary: **`EXPECTED_FP` rows are published at 1080 scale** (d5 → (348, 356)) while their
consumer — GRAZE JSON — reports `gz_row`/bands at 540 scale. Any round-judge matching the
registry literally against checker output will never match a row. The GPU-phase judge must
halve the registry rows (or the registry should be emitted at 540).

### 3.3 Finding G-2 — the report's scene15 d5 manhole number is the old position's

`w2_groundkit_v1.md` §4.2/§5.2 claim the relocated manhole occupies "280 px = 14.6 %" at d5.
280 px corresponds to X = 3.85 m — the **old** x = −1.15 seen from the d5 eye. The **new**
x = −4.00 at the d5 eye is X = 1.00 m → **1,662.8 × 0.648/1.00 ≈ 1,078 px = 56.1 %** of frame
width `[calc]`; ground_kit's own B2 (83.2 %) is only consistent with the 56 % figure. The
§5.2 "expected gate values" table would therefore mis-brief the GPU owner by 3.9×. Note the
near-window design intent itself is §2.2-conformant (any W1 disc is large by construction);
only the published expectation number is wrong.

### 3.4 Smaller notes

- Report §4.3's "Δ = 24.7 rows" for the scene13 entry trench is the **centre**-line figure;
  GT-E2 binds on the **near boundary**, which measures Δ@1080 ≈ 18.2 (still ≥ 16; margin is
  2.2 rows, not 8.7) `[calc]`. The code itself judges boundaries (min over sa/sb) — correct.
- Report §4.3 quotes 52 prims for scene13; rebuilding the plan from the actual scene-diff
  arguments yields 53 (the fixture `SCENE_PLANS` — tactile on, no lane markings, drop 4.4 —
  is what produces 52; §7.4 declares the fixture non-authoritative, but the report mixes the
  two) `[measured]`.
- `cue_tactile` stays False in scene13 with the blocker citing "M10 pending"; the ruling
  list marks **M10 as decided** (render-mix via hazard-off twins). The one-line flip is now a
  scheduling decision, not an open analysis question — supervisor should direct it explicitly.
- B1–B5 as WARN-only: consistent with §9.2 step 1's blocking list and §7.1's W2 WARN freeze;
  the B5 threshold-unreachability argument (≈22 decals needed vs 4–12 budget) checks out.

---

## 4. W2-A4 — vegetation procurement

- **Pixel re-verification, 17 textures, independent implementation** `[measured]`: hue-bin
  fractions reproduce the report to ≤ 0.003 everywhere sampled — beech/hollyprivet/fraxinus/
  poplar/oak1/oak3/oak4 green 1.000; **oak2 yellow-green 1.000** (the albedo side-condition
  case); pine 0.804/0.196; spruce 1.000; cedar 0.972/0.019/0.008; switchgrass 1.000;
  lawngrass 0.236/0.320/0.440; Grass001 green 0.983; Grass004 0.706/0.281; incumbent
  `aerial_grass_rock` **green 0.000** (yg 0.814, orange 0.183) — the W1 finding confirmed
  again; control `cherryblossom.png` pink 0.781/red 0.217/green 0.000. Near-white ≈ 0 on all
  accepted textures. Albedo values differ from the report by a constant convention (my
  channel-mean vs their linear-luma) with identical ranking — e.g. tactile 0.401 channel-mean
  = 0.478 luma vs their 0.484; no verdict changes under either convention.
- **Rejects really gone** `[measured]`: no White_Ash/Barberry/Grass_Trimmed_*/
  Fountain_Grass_Short USDs, no `ashleaves*/barberry*/pampas*` textures on disk; W1 rejects
  (Japanese_Cherry, Forsythia, Burning_Bush) deliberately retained on disk and now dropped
  from the live tables by the surgeon — the two-step deletion order is intact.
- **Manifest**: 17 accepted / 6 rejected / 3 textures; every accepted `local_path` exists;
  Colorado_Spruce carries the far-background-only warning in-manifest.
- **Downloader reproducibility re-run** `[measured]`: `download_vegetation.py --only …`
  completes with skips only, "All vegetation assets downloaded and verified" (the
  `lstrip()` MDL-header fix demonstrably in effect — Scarlet_Oak MDLs no longer flagged),
  132 files; `download_scene01_assets.py` reports 75/75.
- **Tactile texture re-measured independently** `[measured]`: 36 blobs (6×6), pitch 170.7 px
  = 50.0 mm on the 0.30 m tile, mean sRGB (0.874, 0.700, 0.008); area-equivalent dot diameter
  ≈ 35.5 mm (their 38.1 mm is the outer base incl. rim — same conclusion: far above the
  22–25 mm practice, dot-area fraction concern stands).
- **Limit of this verification**: mesh-UV-level sampling and instanced-triangle counts could
  not be re-executed — no `usd-core`/`pxr` exists in any environment reachable this session.
  Texture-level pixels, manifest congruence and the surgeon's independent AST checks are the
  coverage; the PointInstancer effective-triangle table is taken as reported `[assumed]`.

---

## 5. W2-A5 — materials

- **Byte-reproducibility** `[measured]`: regenerated all three maps to scratchpad —
  **MD5 identical 3/3** to the repo files (`3265277a… / 75d8179d… / 7a0f0440…`).
- **Gates re-measured through `scripts/norm_spec.py`** (the independent module; banner
  confirms "외부 정본" is the operative measurer): mineral +0.040/0.43/69.5/0.180 · granular
  +0.231/0.28/72.7/0.280 (3 clipped texels) · brushed −0.034/0.51/68.8/0.140, aniso
  1.015/0.997/**0.122**, seam 1.05/1.00/0.97 — all PASS, granular's +0.231 vs +0.3 ceiling
  is the one thin margin as reported. Anchor gate 4/4 inside `--verify-anchors` `[measured]`.
- **MDL v1.9.0 inertness audited in source** `[measured]`: comment-stripped parameter parse —
  **first 66 params byte-identical**, 8 appended at the tail with the exact claimed defaults
  (`texture_2d()` invalid, bump 0.0, rough_gain 0.0, `unit_cell_m float2(0)`); body diff is
  the claimed sites only (hash2/unit_gain/detail fn block; pw_w/nw_w hoist whose bound
  expressions are character-identical to the previously inlined ones; `× color(unit_g)`;
  DET call + `(DET.nrm − n)` term; `rough_d`). Early returns verified: `negobs_unit_gain`
  → 1.0 when `cell ≤ 0 ∨ sigma ≤ 0`; `negobs_detail_normal` → `{state::normal(), 0.0}` when
  `det_bump ≤ 0 ∨ !texture_isvalid` (both uniform); `rough_w` already emerges from
  `clamp(…, 0.02, 1.0)` (line 931) so the re-clamp is idempotent. The remaining risk is
  exactly what the builder scoped out: backend argument-block layout — needs the GPU owner's
  defaults-only A/B plus an MDL compile check before any pilot.
- **§4.5 contract**: MDL declares `unit_cell_m` + `unit_cell_origin` (+ sigma/accent) with
  zero defaults; ground_kit's ledger carries `(cell_m, (ox, oy), source)` per profile and its
  self-check asserts U1–U4 (ran in §3.1's exit-0 run); U4 remains consumer-side as both
  builders state. Contract halves match.
- R1 (sub-pixel at spec tile scales): the geometric chain re-checked — 24 px/° ⇒ 1 px =
  0.727·d mm; 8 cm tile ⇒ 0.078 mm/texel `[calc]` — the pilot must A/B
  `detail_texture_scale` (2–4) and/or non-zero `detail_rough_gain` or it will measure a null.

---

## 6. Cross-checks

- **Tactile texture name**: `tactile_yellow_diff/nor.png` consistent across main
  `scene_common.TEX`, worktree `tactile_pbr()`, ground_kit §12.5 wiring, the N5 pilot
  (`sc.tex_path("tactile", …)`) and the veg report; files exist in `assets/scene01/`.
- **M8 (D4 untouched)**: sceneD4 files clean in the main tree and absent from the surgeon's
  33-file touched list; ground_kit's D4 profile exists only in the self-check fixture — no
  scene wiring `[measured]`.
- **No seasonal asset slipped in**: all newly procured foliage re-measured green/yg with
  red+pink+orange ≤ 0.008; the only pink-blossom texture on disk is the legacy
  `cherryblossom.png` whose asset is now table-dropped; Rhododendron's `Flowers` subprim is
  deactivated before instancing in the worktree. The sceneC2 pink-shrub render observed by
  the recalibration report (§10) is a **pre-existing round artifact** whose code path is now
  closed; it will clear on the next render.
- **Main-tree dirty set** maps 1:1 to the four main-tree builders' declared files; nothing
  unaccounted `[measured — git status]`.

## 7. Consolidated supervisor items (deduplicated across builders, verified real)

1. **GRAZE v2.1 injection floor** — 65.7 % `[measured, independent]` vs ≥ 70 %: pick one of
   the three options in `w2_tools_v1.md` §4.5 (accept + re-derive on a rendered positive /
   fix the §6 synthesis / burial-only scope). Blocks nothing in the pilot render itself
   (GT-E4 re-baselines GRAZE anyway) but blocks trusting WARN-level silence on future rounds.
2. **GT-E2 row scale** (finding G-1): declare 540 or 1080 normative; today's B7 enforces
   half the derived separation, and `EXPECTED_FP` rows are in the wrong coordinate system
   for their consumer.
3. **Corrections to `w2_groundkit_v1.md` before the GPU owner asserts §5**: 15-4 manhole
   d5 ≈ **1,078 px / 56.1 %** (not 280 px / 14.6 %); 13-4 entry-trench binding margin is the
   near boundary (Δ@1080 ≈ 18.2), not 24.7.
4. **`cue_tactile` flips** (13/01/02/08/11/16): M10 is decided per the ruling list — direct
   the flip (or its deferral) explicitly; the current blocker text treats it as pending.
5. Standing items re-verified as real and still open: tactile `relief="geom"` vs prim cap;
   dot-diameter 38.1→25 mm one-liner; hue-rotated Sycamore/ginkgo derivative; triangle-budget
   basis (unique vs instance-expanded); per-texture leaf-albedo attenuation; `norm_spec`
   hf%-in-exit-code one-liner (finding T-1); wht%/sky-rule spec amendments; MDL compile +
   defaults-only A/B as the GPU owner's first action.
