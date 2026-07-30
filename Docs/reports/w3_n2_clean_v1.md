# W3 · sceneN2 asphalt-patch cleanup — "깔끔하게 작업된 느낌"

**Owner file** `scenes/batch1/sceneN2_asphalt_patch.py` (only)
**Round** `look_check/sceneN2/260730_w3_n2clean` · 13 cuts · PT · judge channel
**Baseline of record** `look_check/sceneN2/260730_w2d_fix` (latest sceneN2 judged round, stamped 2026-07-30 02:57, HEAD `386fc88`)
**Regression JSON** `Docs/reports/regr_260730_w3_n2clean.json` — written to disk, **left
uncommitted**: this WP owns only the scene file and this report, and other workflows were
editing the tree concurrently. Commit it with the round if the reports convention wants it.

---

## 0. Mandate

> "다만 N2 아스팔트 패치는 너무 지저분해.. 아무리 작업했더래도 깔끔하게 작업된 느낌이면
> 좋겠네." — user, 07-30

The scene keeps its identity: the asphalt patch is still the negative-obstacle context cue,
and the 1.5 × 2.0 m feature patch at x 2.6…4.6 still forms the black-rectangle confusion pair
with sceneD2. GT is unchanged — **no drop in any pixel**. What changed is that every repair
mark on the apron now obeys one contractor vocabulary instead of five unrelated ones.

Scope discipline: nothing outside the scene file and this report was written. `ground_kit.py`,
`scene_common.py`, `batch1_common.py` and the GT ledger were **read only**. Everything the
brief asked of the kit was obtained through the scene's own `overrides=` argument.

---

## 1. Research — real Korean road repair *is* regular geometry

| # | Finding | Source |
|---|---|---|
| R-a | **소파보수** (patch repair): the damage is sawn back **at right angles, ~30 cm beyond the broken edge**, and the whole repair area is handled as a **rectangle** | 국토교통부 「아스팔트 콘크리트 포장 시공 지침」 5장 유지보수 |
| R-b | Repair boundaries are **square or rectangular** with a **minimum length and width of 12 in ≈ 0.30 m**; the outline is cut with a straight-line pavement saw at least 12 in beyond the perimeter | Caltrans FPM TAG ch. 5 *Patching and Edge Repair* |
| R-c | **절삭·재포장** in Seoul practice is a **50 mm milling depth** applied by 균열률/소성변형률 threshold | 서울특별시 도로포장 유지관리 매뉴얼 |
| R-d | Milling width is chosen **per lane**: ~1 m class machines for utility cuts, 2 m+ for carriageway; commercial cold mills span 0.35–4.4 m working width in a single pass | Wirtgen cold-milling range / industry practice |
| R-e | A **tack coat of emulsified bitumen is sprayed or brushed onto the vertical cut faces** (never poured) before filling; the perimeter joint is then overbanded with sealant | Caltrans FPM TAG ch. 5; 실란트/오버밴드 practice |

The operative conclusion is the one the supervisor framed: a **messy blob patch is wrong and a
clean rectangle is right**, because the saw is what makes the edge. The failure in the baseline
was never "there are rectangles"; it was that the rectangles shared no datum with each other.

Sources:
[아스팔트 콘크리트 포장 시공 지침 05장 유지보수](http://cyeng.iptime.org/xe/board_moct/33622) ·
[아스팔트 콘크리트 포장 시공 지침 (PDF)](https://files-scs.pstatic.net/2024/12/09/kAIvlJaH85/%EC%95%84%EC%8A%A4%ED%8C%94%ED%8A%B8%20%EC%BD%98%ED%81%AC%EB%A6%AC%ED%8A%B8%20%ED%8F%AC%EC%9E%A5%20%EC%8B%9C%EA%B3%B5%20%EC%A7%80%EC%B9%A8.pdf) ·
[서울특별시 도로포장 유지관리 매뉴얼](https://news.seoul.go.kr/safe/files/2018/04/5ae94ae80a07c5.47801819.pdf) ·
[Caltrans FPM TAG ch.5 — Patching and Edge Repair](https://dot.ca.gov/-/media/dot-media/programs/maintenance/documents/fpmtagchapter5-patching-a11y.pdf) ·
[도로포장 유지보수 실무 편람 (건설교통부)](https://www.codil.or.kr/filebank/original/HB/OTMCHB500849/OTMCHB500849.pdf) ·
[Wirtgen cold milling machines](https://www.wirtgen-group.com/ocs/en-us/wirtgen/cold-milling-machines-61-c/)

---

## 2. Diagnosis — what actually made it read as 지저분

Measured, not asserted. The baseline apron carried **five dark quads plus scribble**:

| source | count | dimensions as shipped |
|---|---|---|
| scene feature patches | 2 | 2.00 × 1.50 · 5.00 × 4.00 |
| `ground_kit` `build_patch_field` | 3 | **0.856 × 0.834 · 0.834 × 0.814 · 0.728 × 0.772** `[measured — dry plan_ground run]` |
| `ground_kit` `build_crack_lines` | 6 polylines (20 prims) | 3-segment zigzags, ±40° direction changes |
| `ground_kit` `build_stain_field` | 4 `tire` + 4 `oil` | `oil` = free-form blots bound to `M["patch"]`, **albedo 0.030** |
| `ground_kit` `_build_weed_band` | 4 | — |

Three mechanisms, in order of how loudly they read:

1. **No shared dimension.** The kit draws each patch from a continuous area draw
   (`patch_area_mean` 0.63 × U(0.85,1.15)) and a continuous aspect draw (`ar` 0.7…1.6).
   `street_asphalt` declares `module=(None, None)`, so `_snap_module` had nothing to snap to.
   Result: three near-squares that differ in the third decimal and align to nothing —
   0.856, 0.834, 0.728 wide, at y offsets −0.417…0.417, −0.107…0.707, −0.686…0.086.
   Five rectangles, five sizes, five offsets, no datum. That is the whole defect.
2. **The cut line read as vector art.** The scene's own lip was a **0.08 m strip at albedo
   0.34** — measured at **mean 181/255** against an apron of 181 in `beauty_oblique`, i.e. a
   bright ruled frame drawn on the ground. `tonglam_v2.md` §2.13-2 had already flagged the
   kit's equivalent stroke; the scene's own was never revisited.
3. **Noise around the work.** 6 crack zigzags + 4 near-black oil blots + 4 weeds turned
   "a maintained car park" into "a neglected one".

`build_patch_field`'s per-call dimensions are **not reachable from a scene** — `_compose_ops`
fixes its kwargs — and `ground_kit.py` is out of scope. So the repairs are drawn scene-side.

---

## 3. The fix — one contractor vocabulary

### 3.1 Four rules

| rule | statement | grounded in |
|---|---|---|
| **R1 rectangle** | every repair is an axis-aligned rectangle, min side ≥ 0.30 m | R-a, R-b |
| **R2 axis** | `street_asphalt` is 무모듈, so the datum is the **lane/stall axis**, not a flag grid: every edge is parallel or normal to +X, yaw ≡ 0 | R-a; `GROUND_DIMENSIONS["unit_cell"]["street_asphalt"] = (None, None, "무모듈")` |
| **R3 drum width** | cross dimensions come from a 3-value mill vocabulary — 1.00 / 1.20 (utility) and 2.00 m (carriageway). The 4.0 m main patch is **two 2.00 m passes** | R-d |
| **R4 sealed joint** | the cut face is tack-coated and the perimeter overbanded: the edge is a **dark 60 mm band with a slight sheen**, not a bright line | R-e |

### 3.2 Geometry as shipped

```
보수 small   x[ +2.60, +4.60] y[ -0.75, +0.75]  2.00×1.50 m  최소변 1.50  톤 fresh  1패스
보수 main    x[ +7.00,+12.00] y[ -4.80, -0.80]  5.00×4.00 m  최소변 4.00  톤 cured  2패스
보수 xing    x[ -4.55, -3.35] y[ -2.10, +2.10]  1.20×4.20 m  최소변 1.20  톤 cured  1패스
보수 soft_a  x[ -1.70, -0.70] y[ -0.50, +0.50]  1.00×1.00 m  최소변 1.00  톤 fresh  1패스
보수 soft_b  x[ -9.40, -8.20] y[ -0.70, +0.30]  1.20×1.00 m  최소변 1.00  톤 aged   1패스
R1 최소변 0.30 m 위반 0건 · R2 축정렬: 전 보수 yaw 0 (구조상)
```

Every dimension is on a 0.10 m grid and drawn from {1.00, 1.20, 1.50, 2.00, 4.00, 4.20, 5.00}
instead of from a continuous draw. **The two feature patches keep their spec'd footprints
exactly** — the sceneD2 confusion pair depends on the 1.5 × 2.0 m at x 2.6…4.6 and it was not
touched.

The three near-window repairs replace the three kit blobs at the same x anchors, so the
d2/d5/d10 near-window coverage is preserved and in fact improved:

| repair | cut | W1 overlap (ground distance) | screen width | % frame |
|---|---|---|---|---|
| `soft_a` | h·d2 | 0.564…1.300 | 1784 px | **92.9 %** |
| `xing` | h·d5 | 0.564…1.650 | 1920 px | **100.0 %** |
| `soft_b` | h·d10 | 0.600…1.800 | 1386 px | **72.2 %** |

`[computed — gk.NEAR_W1 = (0.564, 2.00), gk.cam_wpx, eye = (−d, 0, h)]`. The baseline's
`frame_budget` B2 measured **90.3 %** with a **single** W1 element (d2 only); all three windows
now carry one.

`xing` is a transverse service-crossing reinstatement (횡단 관로 복구) — one 1.20 m mill pass
across the aisle, both saw cuts sealed. Its west edge is at −4.55 rather than a rounder −4.30
for a paint reason: the near stall row starts at x −4.60, and cutting at −4.30 left a **0.21 m
paint stub** west of the trench. A 21 cm orphan of a stall line reads as a botched repaint —
the exact opposite of the brief. At −4.55 the sealant band (−4.61) reaches past the paint start
and the stub is swallowed `[computed — geocheck ①]`.

### 3.3 Tone separation — three dated campaigns

| tone | albedo | roughness | applied to | rendered mean (h0.9_d5 unless noted) |
|---|---|---|---|---|
| `fresh` | 0.030 | 0.92 | `small`, `soft_a` | **77.3** |
| `cured` | 0.050 | 0.90 | `main`, `xing` | **84.4** (xing) · 102.8 (main, at distance) |
| `aged` | 0.068 | 0.88 | `soft_b` | **120.6** (h0.3_d10) |
| — concrete apron | ~0.42 | — | reference | 176.2 (h0.9_d5) · 163.2 (h0.3_d10) |

Ladder: concrete 0.42 ≫ old asphalt roadway 0.16 ≫ aged 0.068 > cured 0.050 > fresh 0.030.
Strictly monotone, and `fresh` is **untouched** because it carries the sceneD2 pair and must
stay the darkest thing in the frame.

**This table was retuned against a render, not guessed.** `Looks/Patch*` classifies as
`asphalt`, so `make_pbr` promotes the constant colour onto the asphalt role texture
(`_promote_const_to_texture`) and the aggregate then carries the albedo — a superlinear
relationship in the bright grains. The first cut of this batch used 0.055 / 0.082 and put
`aged` at **mean 132/255 against an apron of 163** at h0.3_d10, a 1.23:1 step that reads as a
dirty concrete slab rather than an asphalt repair. That arm is kept at
`look_check/_experiments/twins/sceneN2/260730_w3_n2clean_tone0/`; the shipped values are
0.050 / 0.068, measured back at **120.6 vs 163.2 (1.35:1)**.

### 3.4 Sealed joint

`cut_w` 0.08 → **0.06** (실란트 오버밴드 50–80 mm, midpoint) · `cut_color` 0.34 →
**0.018** · `cut_rough` 0.85 → **0.55**.

`CutLine` classifies as **paint**, which is deliberately outside `_CONST_MDL_CLASSES`, so it
is *not* promoted and the constant colour is what ships. Measured at the `soft_a` band,
h0.9_d5:

| round | band mean | mat mean | reads as |
|---|---|---|---|
| baseline `260730_w2d_fix` | **180.9** | 81.7 | bright ruled frame |
| tone0 arm (0.045) | 116.3 | 77.3 | still lighter than the mat it borders |
| **shipped (0.018)** | **99.0** | 77.3 | a seam |

The roughness step (0.55 against the mat's 0.88–0.92) is the single cue that separates a
*sealed* joint from a bare cut, and it survives PT.

### 3.5 Cold joint (종방향 시공이음)

4.0 m of cross dimension is two 2.00 m mill passes, so `main` carries one longitudinal seam at
y = −2.80 running the full 5.0 m, 0.05 m wide, at proud **0.0023** — i.e. **on** the mat
(0.0020), below the manhole frame (0.0026). One prim. It is the detail that says a machine laid
this in passes rather than "a dark rectangle was placed here", and it is visible in
`pt_noon_approach` and `pt_noon_beauty_oblique`.

The z ladder gains one rung and stays strictly increasing — asserted, not commented:

```
z 층서: 줄눈 0.0006 < 도색 0.0010 < 실란트 0.0012 < 패치 0.0020 < 시공이음 0.0023
        < 맨홀 0.0026/0.0032/0.0038
층서 단조증가: 합격
```

### 3.6 Restraint — the noise around the work

`overrides=dict(surface=(("crack", 2), ("stain", ("tire",)), ("weed", 2)))`.

| kit element | before | after | why |
|---|---|---|---|
| `patch` | 3 | **0** | replaced by the scene-side repairs above. The op is *dropped*, not left inert (spec §6.2 K2) |
| `crack` | 6 (20 prims) | **2** (6 prims) | 2 sealed cracks is the "occasional crack-seal squiggle" a maintained apron carries; 6 zigzags is neglect |
| `stain` | `("tire","oil")` = 8 | **`("tire",)` = 4** | the 4 `oil` blots were free-form lobes bound to `M["patch"]`, i.e. near-black splotches on grey concrete. `tire` stays: a wheel track has straight edges because a tyre bounds it, and it is what says vehicles use this aisle |
| `weed` | 4 | **2** | — |

`surface` is a tuple in the profile, so `plan_ground` **replaces** it wholesale rather than
merging (non-dict overrides are assigned). Declaring the full tuple is the only way to drop an
op from a scene; there is no per-op switch.

Marking cuts follow automatically — `paint_line_segments()` now iterates `repair_rects()`
(features + repairs), so the near stall line at y=0 breaks at `xing` and at `soft_a` and
resumes beyond each. An unbroken stall line running straight across a patch is the loudest tell
that a patch is a decal rather than a hole cut in the surface.

---

## 4. The decal-rectangle ban — why N2's repairs are the exception

The library-wide instruction — **"바닥에 이상한 사각형 무늬는 웬만하면 다 제거해"** — targets
**decorative** ground marks: stains, blots, wear mats and soiling decals whose rectangularity
comes from the implementation (an axis-aligned plate) and not from the world. That ban is what
DEC-1 discharged by rebuilding `dirt`/`water`/`oil`/`gum`/`efflorescence`/`drip` as `build_blot`
polygons.

A repair patch is the standing exception, and the spec already words it precisely (§10.6):

> "no decal has a straight edge that is not a construction joint, **a saw cut** or a kerb"

An N2 repair patch has straight edges **because a saw cut made them** (§1 R-a, R-b). The same
clause is why `grime_band` and `tire` stay rectangles — a wall bounds the one and a tyre the
other. The distinction to carry forward is therefore not "rectangles bad" but:

| kind | rectangle legitimate? | test |
|---|---|---|
| repair patch, saw cut, construction/contraction joint, kerb, wheel track, wall-junction band | **yes** | a physical straight edge exists in the world |
| soil / oil / water / gum / efflorescence / drip / generic "stain" | **no** | nothing bounds it — it must be a blot |

This report is the place that distinction is recorded for N2; nothing in `ground_kit.py` was
changed to state it.

---

## 5. Verification floor (spec `w3_execution_spec_v1.md` §6.1) — 4/4 green

| gate | command | result |
|---|---|---|
| 1 | `python3 -m py_compile scenes/batch1/sceneN2_asphalt_patch.py` | **OK** |
| 2 | `NEGOBS_SMOKE=1 python sceneN2_asphalt_patch.py` | **OK** — 조립 완료 · 646 prims · `[ground_kit] 프림 19 · 산포 0 · δmax 0.1021` |
| 3 | `python3 scripts/geom_invariance_check.py --scenes sceneN2` | **exit 0** — R-5 PASS · R-4 1/1 · R-6 1/1 · hash `9e6715a5` identical across MTL=0 / MTL=1 / V1=1 |
| 4 | `python3 scripts/placement_lint.py --scenes sceneN2` | **exit 0** |

Plus the scene's own `NEGOBS_GEOCHECK=1` self-check: marking-cut table 2/2 as expected, R1 0
violations, z ladder monotone, camera burial 합격 (nearest 5.00 m), feature occlusion 전 뷰
무폐색.

### 5.1 `placement_lint` delta

Findings are **identical** before and after — 0 ERROR / 9 WARN / 1 BLOCK, same rules
(LINT-1..7 nodata for the undeclared `PLACEMENT` block, LINT-9 gated on P-7). Only the
inventory line moves:

```
before  sceneN2  prims=600  PLACEMENT=NO  bollard=9 lamp=3 patch=3 planter=2 shrub=4 stain=8 tree=2
after   sceneN2  prims=588  PLACEMENT=NO  bollard=9 lamp=3        planter=2 shrub=4 stain=4 tree=2
```

- `prims 600 → 588` (−12), reconciled exactly:

  | source | Δ | basis |
  |---|---|---|
  | kit ops | **−23** | op-level dry `plan_ground`: patch 3→0 · crack 20→6 · `stain_oil` 4→0 · weed 4→2 `[measured]` |
  | scene repairs | **+16** | 5 mats + 20 sealant strips + 1 cold joint = 26, against the old 2 mats + 8 lips = 10 `[computed from build_patches]` |
  | markings | **−5** | the y=0 near stall line now emits 3 fragments instead of 2, and the 0.9 m tiler plus its fixed-seed 10 % gap draw lands 5 plates short `[derived — the residual, not separately instrumented]` |

- `patch=3 → absent`: the linter's `patch` classifier keys on the **kit** path `GKit/Patch_*`.
  The scene-side repairs are `/World/Scene32/Patch_*` and are not counted under that label.
  This is a **classifier scope artefact, not a loss of repairs** — the apron carried 5 repair
  mats before (2 feature + 3 kit) and carries 5 now (2 feature + 3 scene). Recorded here so a
  future reader does not read the row as "the patches were deleted".
- `stain=8 → 4`: the `oil` drop, as designed.

### 5.2 `frame_budget` B1/B2 flip — declared, not hidden

The kit plan's frame-fill warnings move:

| gate | before | after |
|---|---|---|
| B1 W1 areal element | PASS (1) | **WARN (0)** |
| B2 areal screen width | PASS (90.3 %) | **WARN (0.0 %)** |
| B3 / B5 | already WARN | WARN (unchanged) |
| B6–B12 (hard) | PASS | **PASS** |

`frame_budget` measures the **kit plan only**; it is structurally blind to scene-local
geometry. The repairs did not disappear, they moved out of the kit's ledger — §3.2 measures
92.9 / 100.0 / 72.2 % actual screen width in the three windows, i.e. better coverage than the
single 90.3 % element the gate was passing on. B1–B5 are frame-fill *targets* (WARN) whose
verdict "comes from σ_LF/sd after rendering" by the kit's own docstring; the render is in §6.

---

## 6. GPU pilot round + regression adjudication

Round `260730_w3_n2clean`, all **13 cuts** in `grid_views` order (order-prefix rule respected —
nothing truncated), rendered under `flock -w 7200 /tmp/negobs_gpu.lock`, 42 s, stamped by
`scripts/stamp_round.py`. Channel identical to the baseline stamp:
`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 ·
NEGOBS_DETAIL_ROUGH_GAIN=0`.

`python3 scripts/regression_check.py --before look_check/sceneN2/260730_w2d_fix --after look_check/sceneN2/260730_w3_n2clean`

**13 cuts — FAIL 4 · WARN 2 · INFO 1 · PASS 6.**

| category | verdict | evidence |
|---|---|---|
| **DARK** | **clean 13/13** | `newdark = 0.00` and `newdark_near = 0.00` on **every** cut; `d_dark` ∈ [−0.03, 0.00] pp |
| **BLOWN / WHITE** | **clean 13/13** | `after_clip = 0.00` on every cut; `d_white` ≤ 0 on 11/13, max +0.72 pp |
| **OCCL** | **clean 13/13** | no OCCL issue raised on any cut |
| **FRAME** | **4 FAIL + 3 WARN — the declared deliverable** | block shift 86 / 94 / 40 / 19 % at h0.3_d10 / h0.3_d5 / h0.3_d2 / h0.9_d10 |
| GRAZE | 1 suspicion, **adjudicated non-applicable** | see §6.1 |
| PHOTO | 1 luminance drop, **adjudicated intended** | see §6.2 |

The four FRAME FAILs are exactly the cuts whose near field the repairs occupy. This is the
change the brief asked for; the redraw could not have been done without moving frame occupancy.

### 6.1 GRAZE at `preset_h0.3_d2` — adjudicated non-applicable

> `[GRAZE] [v2.1][의심] 은닉 — 국소도 70.8 · 열 일치율 0.86 · 단차 31.6→22.3 · 최대 변화 y304.
> 낙차행의 선이 무너졌다 → 낙차가 과도하게 은폐·매몰됐을 가능성. 에지대역 y170~312/540
> (낙차 2.0 m 지점 y249). 그 대역만 잘라서 육안 확인(자동 확정 불가)`

**sceneN2 declares `edges=()`** — it is a hard negative with zero drop edges, and `plan_ground`
records no edge at all. The instrument scores a *nominal* 2.0 m drop row that does not exist in
this scene, so "the drop line collapsed" cannot be a finding about a drop here.

What the instrument is actually reading at y304 is the **contrast inversion of the cut line**:
the baseline had a bright 0.34 lip (mean 181) at that row and the shipped round has a 0.018
sealant band (mean 99). A bright line became a dark line, so the row's local structure changed
sign. Visual check of exactly the band the tool asks for:
`look_check/_experiments/gates/sceneN2/260730_w3_n2clean_crop/h0.3_d2_grazeband_y170_312.png` —
concrete, the sealed far edge of `soft_a`, the stall line resuming. No burial, no collapse, no
drop. The tool's own text says 자동 확정 불가; this is the manual adjudication it asks for.

The README's standing rule ("edge integrity is never read from GRAZE alone; the instrument that
attributes it is a same-session `NEGOBS_GKIT=0` twin") does not need invoking, because the
firing element is scene-local, not kit output — the kit no longer draws anything in that window.

### 6.2 PHOTO at `preset_h0.3_d5` — adjudicated intended

`d_mean −25.6` (144.2 → 118.6), `d_dark −0.00 pp`, `newdark 0.00`. Cause is fully attributed:
`xing` occupies the near field of that cut at 100 % screen width from ground distance 0.45 m,
so roughly the bottom half of the frame is asphalt where the baseline had concrete. No pixels
went black — the frame is *materially* darker, not *photometrically* broken, and dark% is
unchanged at 0.1.

For a scene whose entire subject is "dark repair mats on light pavement" this is on-thesis
rather than a defect. It is called out here because a −25 mean on a dataset cut is the kind of
number that must be someone's decision and not a silent side effect. **If the supervisor
prefers the near field of h0.3_d5 to stay predominantly concrete, the one-line lever is
`PARAMS["repairs"]["xing"]` → a longitudinal soft patch like `soft_a` instead of a transverse
crossing**; the cost is losing the most legible "neat contractor work" element in the scene and
re-opening the 0.21 m paint-stub problem of §3.2.

### 6.3 Crops

`look_check/_experiments/gates/sceneN2/260730_w3_n2clean_crop/` (before/after stacked,
before = `260730_w2d_fix`, after = `260730_w3_n2clean`):

| file | what it shows |
|---|---|
| `h0.3_d2_nearfield.png` | `soft_a` — 1.00 × 1.00 square, black sealant band across its far edge, stall line resuming beyond. Baseline: an 0.856 × 0.834 blob with a bright grey lip |
| `h0.3_d5_nearfield.png` | **the headline pair.** Baseline: three unrelated dark quads + two fat grey crack zigzags + the manhole ellipse. Shipped: one transverse sealed reinstatement, one aligned rectangle, one crack |
| `h0.3_d10_nearfield.png` | `soft_b` (aged) — the tone that needed the §3.3 retune, with the sealant band making the read unambiguous |
| `h0.3_d2_grazeband_y170_312.png` | the exact band the GRAZE instrument asks to be inspected (§6.1) |
| `oblique_tone_ladder.png` | `small` (fresh) vs `main` (cured) vs apron — the campaign separation, plus the cold joint across `main` |

Per `look_check/README.md` §2 the crop set carries the `_crop` suffix and lives under
`_experiments/gates/`; the tone iteration lives under `_experiments/twins/` as
`260730_w3_n2clean_tone0`. Neither was rendered into the scene root.

---

## 7. PARKED — not written by this work package

Per the concurrency instruction, nothing outside the scene file and this report was touched.
The following are handed over rather than actioned:

1. **GT ledger — new walked-surface z rung.** The cold joint introduces `seam_proud = 0.0023`
   on the walked surface (apron top + 2.3 mm). It is **inside** the convention — `GT_DELTA` is
   0.020 and the element sits between the existing patch (0.0020) and manhole frame (0.0026)
   rungs — so it changes no GT value and needs no exception. But it is a **new z level on a
   walked surface in a hard-negative scene**, and if the ledger enumerates the N2 z ladder it
   now reads 8 rungs, not 7. Ledger owner's call; **this WP did not write the ledger.**
2. **`ground_kit.build_patch_field` cannot be dimensioned by a caller.** `_compose_ops` fixes
   its kwargs, so `area_mean` / `ar` / `cutline` / `cutline_n` are unreachable from a scene.
   Every other patch-carrying profile (01 · 03 · 05 · 10 · 13 · 15 · D1 · D3 · N5 …) therefore
   still gets the continuous-draw dimensions diagnosed in §2. If the "neat contractor work"
   verdict generalises, the library-level fix is to plumb `area_mean`/`ar` (or a `dims=`
   vocabulary) through `_op("patch", ...)` — a `ground_kit.py` edit, out of scope here.
3. **`frame_budget` is blind to scene-local ground elements.** §5.2. Any scene that draws its
   own ground detail will now under-report B1/B2. Worth a gate note if this pattern spreads.
4. **The manhole still renders as a flat black ellipse** at h0.3_d5/d10 (visible in every crop).
   It is `ground_kit` `_ik_manhole` output, not this file's.

---

## 8. Residual risk

- **`aged` at h0.3_d10 is still the lightest repair in the library** (120.6 vs apron 163.2).
  It is defensible — a two-season repair *does* grey out as the binder film burns off — but if
  the supervisor reads it as gravel rather than asphalt, lower `patch_tones["aged"]` to ~0.055
  and it converges on `cured`, at the cost of the third campaign.
- **Four FRAME FAILs mean the sceneN2 baseline-of-record must be re-pointed** to
  `260730_w3_n2clean` before the next regression sweep, or every future run re-reports this
  redraw. The standing `--before-round` chain in `look_check/README.md` §4 has
  `260730_w2d_judge` at its head; adding `260730_w3_n2clean` is a README edit **outside this
  WP's ownership** and is parked with §7.
- Two kit cracks still start inside the `xing` footprint and are geometrically buried by the mat
  (crack z −0.0094 sits inside the mat solid, −0.048…+0.002), so they emerge from the sealed
  edge and stop. Verified as the physically correct read — a crack runs up to the saw cut and is
  milled out beyond it — and identical in kind to the baseline, where kit `Patch_1`
  (x −4.217…−3.383) overlapped the same two polylines.

---

## §7 Supervisor adjudication (07-31)

- **PHOTO h0.3_d5 d_mean −25.6 — ACCEPTED as intended.** The near field is filled by the
  transverse reinstatement (fresh dark asphalt at 100 % screen width): on-thesis material
  change, `newdark 0.00`, dark% unchanged, DARK/BLOWN/OCCL 13/13 clean. The §6.2 lever stays
  unused.
- **Baseline-of-record**: `260730_w3_n2clean` is sceneN2's latest judgement round in the scene
  root, which per `look_check/README.md` §2 IS the baseline-of-record convention; the stamp
  `regr_260730_w3_n2clean.json` is committed alongside this note. No README chain edit needed.
- **GT ledger**: the 8th z-rung (`seam_proud = 0.0023`, inside `GT_DELTA 0.020`) is queued for
  the supervisor's deferred ledger batch (ledger is locked by the running 07/10 lane).
