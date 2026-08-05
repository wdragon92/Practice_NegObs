# Red team — W3 intake verification (01–05 · 06–10 · policy)

> **Task**: independent verification of the three W3 intake documents before the execution spec freezes.
> **Date**: 2026-07-30 · **Branch**: `feat/realism-v1` (HEAD `578d406`) · **No commits, no code/scene edits** — this file only.
> **Targets**:
> A = `Docs/surveys/w3_intake_01_05.md` (1,476 ln) · B = `Docs/surveys/w3_intake_06_10.md` (733 ln) ·
> C = `Docs/surveys/w3_intake_policy.md` (1,014 ln)
> **Method**: 229-point file:line claim audit (script, exact-line ±2 then whole-file), independent greps for
> jitter/species/manholes/bollards/curbs, arithmetic recomputation, live Wikimedia-Commons API + statute fetches,
> license ledger re-read, render-file existence check. Evidence tags as per project convention:
> `[measured]` re-executed here · `[law]` fetched live here · `[repro]` their own repro script re-run here.

---

## 0. Verdict summary

| Doc | Verdict | One line |
|---|---|---|
| **A** `w3_intake_01_05.md` | **PARTIAL — high confirm rate, 6 factual slips** | All 6 G-rows verified decisively at the code level; slips are peripheral but two (patch-profile scope, scene02 species row) leak into the exec spec if copied as-is. |
| **B** `w3_intake_06_10.md` | **PARTIAL — high confirm rate, 4 slips + 1 unreproducible number** | S06-A/B, S07, S08, S09, S10 all substantiated from code and renders; the headline "99.0 mm landing rim swing" does not reproduce from its own construction; scene18 "−2.57°" is a misread. |
| **C** `w3_intake_policy.md` | **PARTIAL — mechanism/inventory work confirmed, lineage argument REFUTED** | The §0/§3.1 chronology claim ("survey written before v5.1") is false by the survey's own header; the 10/19 patch-profile count and the 24-site jit list are exactly right; "18 call sites" prose is wrong against its own list. |

**Bottom line**: every load-bearing *code* claim I re-executed reproduces — the three docs are safe to build
an execution spec from **after** the corrections in §3 and the cross-doc conflicts in §5 are resolved.
No fabricated file:line citation was found (229 checks: 213 exact, 16 drift ≤ 12 lines, 0 missing).
No spec row silently contradicts a user quote; every carve-out (jitter keeps, backdrop-belt species,
D1 crate cap) is explicitly flagged to the supervisor by the docs themselves.

---

## 1. File:line audit `[measured]`

229 claims across the three docs were re-checked by script (pattern within ±2 lines of the cited line,
else whole-file search). Result: **213 exact, 16 minor drift, 0 not-found, 0 wrong-file**.

Drifts worth recording (all substance-correct, line number off):

| Doc | Claim | Cited | Actual |
|---|---|---|---|
| A 01-B | `buildings.R y0=9.5 / L y1=−10.5` | scene01:210-213 | **scene01:123-128** (values exact: R y0=9.5, L y1=−10.5 → 1.5 m / 2.5 m turf strips confirmed) |
| A 01-C | ramp clamp `exc="weed"` | ground_kit:2050 | ground_kit:2058 (`if exc not in ("weed", "scatter")`) |
| B S08-A | tempbar params | scene08:195-206 | comment 195-199 + dict 200-206 (range OK **only if** the comment block is included; builder/boxes/self-check ranges each drift 3–5 lines) |
| B S10-A | `compute_flights` | scene10:455-476 | def at scene10:443 |
| C S-2 | `SHRUB_ORNAMENT` | scene_common:2292 | scene_common:2288 |

**Consequence**: S08-A is written as a *line-range deletion* recipe (6 edits). The ranges must be re-derived
from anchors (prim names / dict keys), not taken literally — and the material key is **`M["temtape"]`**, not
`M["tape"]` as B's table says (`scene08:913` `[measured]`).

---

## 2. Load-bearing findings independently reproduced `[measured]`

### 2.1 Jitter (G-1 / P-1 / §3.2)
- `ground_kit.py:689` `yaw_max=14.0` default, applied :733/:735 — **confirmed**.
- `ground_kit.py:1027` `yaw = 0.0 if line is not None else (rng.random()*2−1)*22.0` — **confirmed**, incl. the
  directional exemption (`grime_band`/`tire`) exactly as C §3.2(d) states.
- `ground_kit.py:1072-1075` footprint prim gets `ang ± 6°`, registry AABB gets `ang` — **the AABB bug is real**
  (C §3.6 confirmed; a genuine registry/geometry divergence invisible to `geom_invariance_check`).
- `batch1_common.py:248` `jit_yaw(lo=3.0, hi=8.0)`, `:256` `jit_pos(amp=0.20)` — confirmed. Call sites:
  **24, not 18** — see §3-R3.
- Bench/planter yaw literals: scene01:175-177 (−6/+4/−5/+3.5/−7/+5) · scene03:197-200 (5/172/93/**187**) ·
  scene04:276-277 (96/94/4.5/93/87) · scene06:262 (−6/+5/175) · scene09:269-270 (86.5/274.0/93.5/265.5) ·
  scene11:233 (86/−94) · scene13:235 (174/−6/+3) · scene17:270-271 (96/−84/…) · sceneD1:855 (`crng.uniform(−9,9)`) ·
  sceneD1:153 (−14.0) · sceneD2:210 (−22.0) — **all confirmed** at the digit.
- scene03 city-block `jyaw` 3.5/−4.0/2.5 (:235/237/239) + pavilion −3.0 (:257) — confirmed (C row 8 exact).
- scene06 20-tree verge row confirmed (11 south + 9 north, pitches 6.6–7.2 m); scene11 file at x ±41.2,
  pitches 7.4–7.6 m — J-6 numbers confirmed.
- Keep-at-zero params (`infra_kit:403/434/479`, `531/557/592`, `ground_kit:607/648/660`) — confirmed, defaults 0,
  non-zero only in the infra_kit self-check (:1437), exactly as C states.
- scene05 `seat.arcs=((80.5,99.5,3),(112.5,247.5,12),(260.5,279.5,3))` (:331) — B's "arc spans, not yaws"
  exclusion is **correct**.

### 2.2 Species (G-2 / P-2 / S-1..S-4)
- `scene_common.py:2443-2444` per-tree draw from the 11-slot pool, seeded per tree at :2437-2438
  (`cx*73856093 ^ cy*19349663`) — **confirmed verbatim**; `VEG_TREES` weights 4/3/2/1/1 at :2118-2125 confirmed.
- **Call-site census resolves to C's exact numbers**: scene01's 3 grep hits are 1 real `sc.build_tree` call
  (:732) + a local wrapper; live sites = 20 (main, 13 scenes) + 4 (batch1: C2·D3·N4·N5) = **24**, + `build_planter`
  internal at `scene_common.py:2564` = **25 sites / 17 scenes** ✔ (B's "20 over 13 in scenes/main" ✔).
- `place_shrubs` per-point draw at :2819 — confirmed; `SetInstanceable(True)` at :2840 confirmed.
- **`place_shrubs` has zero call sites in `scenes/`** — the only caller in the tree is `scene_common.py:2559`
  inside `build_planter`. G-5's "dead code path" claim **confirmed** by grep.
- `VEG_SHRUBS` (:2268-2276) still tabulates Forsythia + Burning_Bush and omits Holly/Yew/Cedar_Shrub —
  confirmed (nuance: the *ban* is live via `SHRUB_HEDGE`/`SHRUB_ORNAMENT` pools :2279/:2288, which exclude them;
  the table is the stale part).
- All 11 never-wired assets exist on disk (`assets/vegetation/{Trees,Shrub}/`), `veg_manifest_w2.json` has
  **17 rows, all PASS**, White/Yellow_Pine absent from it — confirmed. Manifest `zmax_m` matches C §4.3's table
  to 4 decimals (Fraxinus 5.3408 · Gray_Birch 3.3294 · Lombardy_Poplar 13.6709 · Douglas_Fir 6.0263 ·
  Colorado_Spruce 3.8713 · Scarlet_Oak 12.4089 · Black_Oak 19.7389); Colorado_Spruce `tri_effective`
  **15,597,637 exact**.
- **Season-pixel law check on the proposed species table — PASS**: `foliage_uv_hue` red = 0.0 for every proposed
  route species, including the alarmingly-named Scarlet_Oak (green 0.743 + yellow-green 0.257) and Black_Oak
  (0.870/0.130). Cedar_Shrub orange 2.6 % (negligible). Rhododendron stays flowers-off (`SEASONAL_SUBPRIMS`) in
  both docs — consistent with audit A P0-1/P0-2.

### 2.3 Manholes (G-4 / 05-B)
- The code confesses the generator in its own comments — **confirmed verbatim** at `scene08:148-156`,
  `scene05:111-114`, and additionally (my find) `sceneC4:98` and `sceneC1:143` carry the *same sentence*
  ("W2 window (d5 X=2.6 m · 21.6 % of frame width)"), and `scene17:153` says "1 unit, d5 near window",
  `scene21:104` "avoids the central axis". The near-window construction is written into at least 6 scene files.
- Magic-value clustering confirmed: x=−2.40 at scene08/scene15(plan)/N1/C1/C4 `[measured]`; x∈[−4.0,−3.8] at
  01/05/13(plan)/16/18/21. All scene-side sites x<0. scene03 `infra=dict(manhole=0…)` confirmed (natural stays 0).
- KS D 4040 Ø648/766/918 at `infra_kit.py:115-120` confirmed.
- **Caveat (§3-R11)**: the census source `SCENE_PLANS` does *not* exactly mirror shipped PARAMS — scene01 plan
  says (−3.8,−2.4)/(−8.0,**1.6**) vs PARAMS (−3.80,−2.40)/(−8.40,**−2.60**), so "every site |y| ≤ 2.4" is false
  for the shipped scene01 (2.60), and N5's flush-grating *subject* manholes sit at **positive** x (6.0/9.5)
  outside the census's implied scope. Direction of G-4 unaffected.

### 2.4 scene06 geometry (S06-A)
- `_fascia_z` ramp-vs-step: **the code's own docstring states the ±lip** — scene06:427-429:
  *"t(a) − tread face ∈ [−riser·(0.5−z_off), +riser·(0.5+z_off)] → with z_off 0.30 that is +0.154 (step start) …
  −0.038 (step end)"* — B's +153.6/−38.4 mm sawtooth ×26 **confirmed from source** (it is a *documented design
  device* that the renders show failing, which strengthens rather than weakens the row).
- Constant-chord convention `chord = 2.0*r_out*math.sin(dth/2)*1.03` present at `scene_common.py:1637` (arc),
  :1847 (helix steps), :1891 (helix ramp) — confirmed. Recomputed: tread box 683.3 mm vs 301.5 mm true width at
  r_in (2.27×) ✔ · landing 444.6 vs 62.8 mm (7.08×) ✔ · tread corner r 3.3176 (+17.6 mm) ✔ · landing corner
  3.3075 (+7.5 mm) ✔ · adjacent-segment overlap 13.0 mm ≈ B's 12.9 ✔.
- Landing (r 0.48–3.30, a 0–180, seg 24, top 4.998/base 4.498) vs Deck (x 2..5, y −13..13, top 5.0, thick 0.35):
  z-interpenetration 4.65→4.998 = **348 mm ✔**, plan overlap bbox 3.0×3.3 m ✔. Nuance: the 2 mm top offset and the
  column embedment are *deliberate* Z-fight avoidance per the scene's own comments (:164-166) — the fix must not
  reintroduce coplanarity.
- `railing.outer_r=3.36` = 60 mm outboard of tread r_out 3.30 — confirmed (:238, code comment says so itself).
- **Not reproducible**: the "99.0 mm rim swing / union outer radius 3.3000 → 3.3990" figure — see §3-R4.

### 2.5 Curbs (S06-B)
Every row of B's pan-scene table re-read from PARAMS `[measured]`:
scene06 road −0.150 / walk −0.005 / curb 0.0 (150 mm, 5 mm proud) ✔ · scene11 identical ✔ ·
scene02 `curb_top=0.10, curb_base=−0.5`, road top −0.02 → 120 mm above road, **100 mm above the footway** ✔
(docstring :860-861 confirms) · scene03 `levee_road.proud=0.0015` ✔ · scene12 `bikeroad.proud=0.002` ✔ ·
scene13 `drive.proud=0.004` vs `walk_*.proud=0.007` = 3 mm ✔, `infra_kit.py:18` scene13 note ✔,
`build_ramp_curb` exists (:846+) with **zero scene callers** ✔ · scene17 `crown_walk.proud=0.006` ✔ ·
scene16 `M["curb"]` material with no 보차도 curb prim ✔ (nuance: scene16 has **no `road=dict` at all**, so
"colour without geometry" is true but there is also no carriageway to curb) · scene08 `road_lines` at y=±30
painted with **no road slab** ✔ (:224, :942) · `gutter_L=0` in exactly 02/03/08/16/17 ✔ ·
`build_gutter_L` exists `infra_kit:399+` and `infra_kit:409-410` states the real Korean section ✔ ·
`scene_common.py:304` R=10 mm curb arris note ✔.

### 2.6 scene07 / scene08 / scene09 / scene10 parameters
- scene07 `stones`: n=24, x 0.06→12.05, w (0.50,1.10), **depth (0.28,0.40)** [B wrote 0.27–0.39 — see §3-R13],
  gap (0.05,**0.30**) [B wrote 0.29], proud/embed (0.02,0.08)/(0.10,0.18), rz 4.0 rx 2.5, knob rz (10,20)
  rx (3,9) — confirmed; the knob comment literally says "breaks the rectangular silhouette" ✔ and
  scene07:44-46 declines `build_worn_stone_stairs` ✔.
- scene08 `tempbar` full param set ✔ (:200-206), builder `build_tempbar` ✔ (:1199), call under `cue_sign` ✔
  (:1324), 2 TempPost collision boxes ✔ (:398-401), 5-bollard row at x=−18, ys −4.8..4.8 ✔ (:193-194),
  parapet gap ±0.90 ✔, `railing.broken=(180,270)` posts-remain pattern in scene06 ✔ (:238-239).
- scene09: `_RISER_CYCLE [0.14,0.16,0.18,0.20,0.18,0.16]` sum 1.02 ✔, 36 steps, tread 0.34, width ±5.0,
  landings [11,23] @1.2 m, submerge 6 ✔; run 36×0.34+2×0.86 = 13.96 m ✔ drop 6.12 ✔; `SUN_AZ_OFFSET`/233.5 note
  at :383-384 ✔; mooring/land_posts at :215-217/:250 ✔. (Waterline −5.240 not recomputed — inside
  `compute_steps`; B's own §9.3 flags every S06/S09 analytic for usd-core re-confirmation, which stands.)
- scene10: flights n=4 × 10 × 0.165/0.300, half_w 0.69, y_off 0.70, landing 1.4×2.8×0.12, post r0.075,
  rail h1.05/bal r0.022@0.30, `broken_landing=0` ("landing0 outer = the break") — **all confirmed**;
  `wood_color (0.30,0.20,0.12)` + `wood_dark` ✔ (:366-379 region).

### 2.7 Statute + photo evidence `[law]` `[measured — live fetch 2026-07-30]`
- 「지하공공보도시설…규칙」 **제8조⑤ and ⑦ re-fetched from ko.wikisource — verbatim match** to A's quotes,
  and 제8조① "각 출입구의 너비는 2미터 이상" ✔. A's 02-A/02-B statutory core is genuine.
- 「도시숲·생활숲·가로수 조성·관리 기준」 "동일 노선 … 동일한 수종을 권장" — corroborated via public mirrors
  (lbox/ulex hits) + the independent in-repo quote at `korean_pedestrian_geometry.md:466-470` (which also carries
  *"한국 보도에서 랜덤 배치는 존재하지 않는다"* verbatim ✔). Seoul 조례 제7조 text not re-fetched live
  (law.go.kr body is JS-rendered); citation trail exists (ulex URL + in-repo).
- `user_feedback_v5_1.md` §3 jitter directive ✔ verbatim (:14-15); §7 점자블록 기본 OFF "규정상 옳아도 현실
  빈도 낮음" ✔ (:51) — A's "knowingly declined" framing for the 별표2 dot-strip is accurate.
- `tonglam_v2.md` quotes: scene04 FAIL "rubble yard" ✔ · scene08 PASS "barrier tape + striped bollards (strong
  Korean cue)" ✔ verbatim · scene10 "read excellent … plank gaps 2–3 mm real" ✔ · §2.13-2 razor-edge rectangles
  03/07/10/D3 ✔ · C2 "perfect rectangle from the air" ✔ · F5 manhole "worst single prop … 17 d5 + 01·02·05·15·
  N5·N1·13" ✔ · scene16 PASS "Strongest main scene" (canopy listed) ✔ · PASS set 08·16·D1·D4 ✔.
- `redteam_w3r.md`: tactile **12 of 42 ON (C4 6 + N5 6)** ✔ verbatim; +7.904 refutation ✔; dual-root licence ✔ —
  C's dependency rows 9/10 are faithful.
- **Wikimedia Commons API, exact counts**: Damyang Metasequoia Road **12 files** ✔ · Benches in South Korea
  **25 files** ✔ · Sidewalks in South Korea 17 files + 1 subcat (C said 18 — total members) ✔ ·
  Street furniture in South Korea **14 files + 22 subcats** ✔ exact · Boardwalks in South Korea **3 files** ✔ ·
  Bollards in South Korea **empty/nonexistent** ✔ · Pedestrian underpasses in South Korea **empty** ✔ ·
  Hangang Park 65 files (A said ~60) ✔.
- **Photo licences re-fetched**: P07-1 `Buseoksa Temple 01.jpg` = **CC0, Bernard Gagnon** ✔ (verified — this was
  the one I most doubted) · P07-3 `팔공산 갓바위 계단.jpg` = CC BY-SA 4.0, HwangHuang ✔ · P09-1
  `20260416 뚝섬…01.jpg` = CC0, Wikihyo ✔.
- `Docs/reference_photos/expanded/LICENSES.csv`: **54 data rows, licence column = 8 CC0 / 8 CC BY / 36 CC BY-SA /
  2 KOGL Type 1, zero NC/ND** ✔.
- **Road-view ban respected**: no Kakao/Naver/GSV citation appears anywhere in the three docs ✔.
- All 19 named render cuts spot-checked **exist on disk**, including C's six (`scene06 pt_noon_overview`,
  `scene07 pt_noon_temple_walk`, `scene10 pt_noon_leaf_edge`, `scene11 pt_noon_sidewalk_approach`, …) ✔.

---

## 3. Refuted / corrected claims

| # | Doc | Claim | Finding | Severity |
|---|---|---|---|---|
| **R1** | C §0, §3.1 | *"korean_pedestrian_geometry.md §5.1 — written **before** v5.1 … The W1 survey was right; v5.1 §3 overrode it"* | **REFUTED.** kpg's own header: **"작성 2026-07-28"**; first git commit `bc87292` 2026-07-28 23:52. v5.1 is dated **2026-07-27 저녁** (header + file mtime 07-27 20:28). The survey **post-dates** the directive by a day; nothing "overrode" it — it was written into a tree that already had the jitter order and the conflict was never reconciled. The *substance* (statute vs jitter, documented in-repo) survives; the chronological argument and the "we are applying the user's older instruction" framing must be deleted from the exec spec. | **High** — it is the doc's stated justification for reversing a user directive |
| **R2** | A G-1/01-A | patch decal applies to "**18 ground profiles**" / "18 of 22 profiles" | **REFUTED; C is right.** Re-ran C's Appendix-B AST-exec `[repro]`: **19 profiles total; `patch` in 10/19** (list matches C's exactly); `stain` 19/19; (`weed` 8/19, my extra). A's 18 and 22 are both wrong. | Medium — scope number feeds the exec spec |
| **R3** | C §0.1/§3.2 prose (echoed by B §1.0) | "the exact **18** `bc.jit_yaw`/`bc.jit_pos` call sites" | **Count is 24** `[measured grep]` — and C's *own line list* (N1×4 · N2×3 · N3×3 · N5×1 · C1×3 · C2×4 · C4×2 · D2×2 · D4×2) already sums to 24, as does its Appendix A (J-3 "10 sites" + J-4 "14 sites"). Only the prose "18" is wrong. | Low |
| **R4** | B S06-A (A-2) + report headline | "union outer radius swings 3.3000 → **3.3990 = 99.0 mm** landing rim swing" | **Unreproducible from the stated construction.** With chord 444.6 mm the landing box corner radius is √(3.30² + 0.2223²) = **3.3075** — which the *same table row* itself lists — giving a **7.5 mm** union swing. 3.3990 = 3.30 × 1.03, i.e. the tangential margin appears mis-applied to the radius. The other A-2 numbers (2.27× / 7.08× / 17.6 mm / 12.9 mm overlap / 348 mm) all reproduce. B already mandates usd-core re-confirmation before cutting code (§9.3) — do it, and strike "99.0 mm" from summaries until then. | Medium — it is quoted in B's summary as a headline number |
| **R5** | B §1.2 note | "scene18 benches/planters all carry **−2.57°** … a scene-wide skew" | **Misread.** −2.57 is the **z coordinate** (lower plaza `top_z=−2.57`, scene18:104-105); scene18 bench tuples are (x, y, **z**, yaw) with yaws **0.0 / 90.0** — already orthogonal. The "do not touch" instruction is right by accident; the stated reason is wrong. scene20 `rot=dict(deg=30)` half of the note is correct. | Low (instruction harmless) |
| **R6** | A 03-B | "13, 16, **18**, 20, N5 also carry bollards" | scene18's bollards were **removed entirely** (v5.1 §2; scene18:159-163 comment). 13/16/20/N5 confirmed carriers (+ 05/06/08/11/12/14/21/C4/N1-N4/D1). | Low |
| **R7** | A G-2 table | scene02 assigned `Elm_Sapling` for "sidewalk street trees" | **scene02 has no `build_tree` call** `[measured]` (C's no-tree list is right). The row either hallucinates existing trees or silently proposes new planting — either way it cannot ship as written. | Medium — per-scene species table feeds S-1 |
| **R8** | A G-2 / C §4.1 | "monospecific row of 5 = **1.8 %**" / "(4/11)²⁰ ≈ 1.4×10⁻⁹" | Σ(wᵢ/11)⁵ = 1301/161051 = **0.81 %** (A off ×2.2); (4/11)²⁰ = **1.63×10⁻⁹** (C's ≈1.4 is the right order). Conclusions unchanged. | Trivial |
| **R9** | A 02-A | "the pit runs to x ≈ **8.2**", "remaining ~7.6 m of open pit" | As-built `pit=dict(x0=0.0, x1=**7.0**)` (scene02:132); 8.2 is the **unimplemented v8 proposal** A itself flags at 02-A's dependency. Open pit behind the canopy is ~6.4 m as-built. Conclusion (canopy covers 0.6 m of the descent) unchanged. | Low |
| **R10** | B header | renders "17 · 15 · 16 · 14 · 14 PNG" for 06–10 | On disk: **15 · 14 · 15 · 14 · 14** PNG. All *named* cuts exist; only the counts are off. | Trivial |
| **R11** | A G-4 | census "extracted from `SCENE_PLANS` (the fixture that **mirrors** the shipped scene coordinates)"; "**every** site has \|y\| ≤ 2.4" | The fixture does **not** mirror scene01: plan (−8.0, **1.6**) vs shipped PARAMS (−8.40, **−2.60**) → the \|y\| bound fails on the shipped scene (2.60). Also N5's grating-subject "manholes" sit at **+x** (6.0/9.5) and are silently out of census scope. Clustering/x<0/near-window conclusions unaffected. | Low–Medium (the build spec derives lines from PARAMS, not the fixture) |
| **R12** | B S08-A | materials "M[\"tempost\"], M[\"tempost_b\"], **M[\"tape\"]**" | Actual key **`M["temtape"]`** (scene08:913). Line ranges drift 3–5 lines (§1). Re-derive the 6-edit recipe from anchors. | Low |
| **R13** | B §1.2 / S07-A | scene03 bench yaws "+5, 172, 93" (3 values) · scene07 "tread depth 0.27–0.39", "gap 0.05–0.29" | scene03 has **4** benches (the 187° one is missed; A has all 4). scene07 params are depth **(0.28,0.40)**, gap **(0.05,0.30)**. | Trivial |

---

## 4. Gaps none of the three docs caught `[measured]`

| # | Finding | Where | Why it matters |
|---|---|---|---|
| **N1** | **Uninventoried jitter source: `facade_kit.py:563`** — AC-unit u-position `+= rng.uniform(−0.35, 0.35)` with the comment *"Deterministic micro offset … avoids a ruler-straight look"*; also `facade_kit.py:840` gas-valve z `uniform(*GAS_VALVE_Z)` (that one has a stated real basis, "floor +1.6–2.0 (confirmed)"). | facade_kit (shared by building scenes) | C claims a "**complete** inventory of stochastic geometry" and the supervisor asked for *every* jitter source. The AC offset is exactly the reversed doctrine's lineage ("avoid ruler-straight"). Probably a justified KEEP (real AC units follow room layouts) — but it must be **ruled**, not missed. |
| **N2** | KEEP-class randomness sites absent from all inventories: scene12:1277 riprap rock yaw `U(0,90)` · sceneD2:726 debris `rotz U(0,90)` · scene17:599-604/1108-1116 far-hedge clump spacing/position jitter · scene09:1368-1369 reed spread · scene11:1448 distant tree-band dx · `ground_kit:1289`/`infra_kit:802` manhole flush `±10 mm` (KS D 4040 tolerance — arguably *should* be listed as a justified keep). | various | All deposition/vegetation-class (defensible keeps), but the exec spec's "complete inventory" claim should either list them or narrow itself to "abolish-class complete". |
| **N3** | **Missing GT/baseline flags** on geometry-changing rows: A 01-B (extending `upper_plaza` to the building faces replaces a turf strip whose top sits at z=−0.63 with paving at z=0 — a height-field change — and enlarging the ground_kit region moves every decal AABB → `regr_260730_w2d_fix.json` comparison breaks); B S06-B step 5 (scene13 walks 7 mm → 150 mm is a real geometry change) and step 2 (scene02 curb reshape). By contrast 02-B, S06-A, S08-A and P-1/J-1 *do* carry their GT/re-baseline duties. | A 01-B · B S06-B | Project GT-invariance law: geometry edits without a declared GT/re-judge consequence are exactly how W2 regressions happened. Add the flags before freezing. |
| **N4** | **`era_consistency_survey_v1.md:881` already rules "02 landing (L1) — CANCEL"** ("지하보도 = 도로 부속물 … landings are geometry and are never retrofitted"). Both A (blocker) and B treat the scene02 v8 landing block (scene02:29-33/64-79, pit 7.0→8.2) as an open implement-or-delete decision; neither cites this existing ruling, which is direct evidence for **delete**. | scene02 dependency chain | Resolves (or at least pre-loads) the one hard prerequisite A names for all scene02 work. |
| **N5** | The `.gitignore` edit + `assets/download_urban.py`/`verify_urban.py` in the worktree are the **W3-R urban-asset lane** (the new .gitignore hunk cites `redteam_w3r §1.5-1` and `assets/urban_manifest_w3.json`). Both A and C correctly disclaim authorship; ownership is now identified, so the "coordinate before editing shared modules" blocker can name its counterpart. | worktree | Closes A's open blocker about unexplained files. |

---

## 5. Cross-doc conflicts that must be resolved before the exec spec freezes

| # | Conflict | Detail | Recommendation |
|---|---|---|---|
| **X1** | **Per-scene species tables disagree (A G-2 vs C §4.3)** — despite C §0.1 declaring "A's per-scene detail governs 01–05". | 01: A = Shumard_Oak (+Elm near-field) vs C = elm only · 03 far bank: A = **Yellow_Pine** vs C = oak_black · 04: A = Shumard_Oak (+Yellow_Pine backdrop) vs C = oak_red (+oak_black) · 05: A = Elm vs C = ash. Worse: **A assigns Yellow_Pine, which C's S-3 retires** (not in the W2 PASS manifest; White_Pine has the zmin −0.351 defect — the retirement is the better-evidenced position). | Take C's S-3 asset base (manifest-PASS only), then re-derive the 01–05 assignments once, jointly, at ratification (C §10-Q1). Do **not** let two tables into the spec. |
| **X2** | **scene04 verge `jit_pos`**: A G-1/04-A abolishes it ("keeps `jit_scale` and `skip`, loses `jit_pos` and `swap`"); C §3.2(b) row 13 lists the same generator (scene04:420-440) as blanket **KEEP** ("grass tufts really are irregular"). | Same code path, opposite instructions. | A's split is the finer ruling (scale/skip = within-vegetation variation; position row-offset = placement). Adopt A's, annotate C's row 13. |
| **X3** | **tonglam fix-ID dual numbering**: tonglam_v2 §1 rows use FIX-1…FIX-6 while its §3 table renumbers F1…F5 (FIX-4≈F2 scatter, FIX-6≈F3 decal boundary, FIX-5=F5 manhole). A cites "FIX-4/FIX-5", B/C cite "F2/F3/F5". | Both docs are internally correct but an executor grepping one label will miss the other. | Exec spec must normalise to one set (suggest §3's F-numbers) with a mapping note. |
| **X4** | **J-6 scope**: C includes scene13 in "street-tree pitch regularisation", but scene13's 8 trees (:231-232) are scattered apartment-court landscaping (x −24.7…30.6, y −12.3…12.4), not a street row; blanket 7.0 m pitch would be its own realism error under the match-the-sample bar. | C J-6 vs the user bar | Split J-6: rows (06/11/12/D3/N5) regularise; scene13 goes to the archetype panel (apartment landscaping) for photo-based treatment. |
| **X5** | **Bollard scene lists**: A 03-B says "13, 16, 18, 20, N5" (18 wrong, see R6); C E-3 says "11·12·14·16·20·21·C4·D1·N1-N5" (correct but omits 02/03/05/06/08/13 which also carry bollards and are covered elsewhere in A). | Neither list is the full carrier set: 02·03·05·06·08·11·12·13·14·16·20·21·C4·D1·N1·N2·N3·N4·N5 (18 = removed). | Use the full set for the P-6 gate. |

---

## 6. Project-law compliance of the spec rows

| Law | Check | Result |
|---|---|---|
| **Season pixels** | Every proposed route/bed species pixel-checked against `veg_manifest_w2.json` hue (incl. Scarlet_Oak red 0.0), Rhododendron flowers-off retained, no Forsythia/Burning_Bush/Japanese_Cherry reintroduction anywhere. D-2's leaf feather ring reuses the already-adjudicated Debris assets in already-leaf scenes. | **PASS** |
| **Bollard law (별표2)** | Rule values consistent across A G-3 and C R6/R7 (h 0.8–1.0 · Ø0.1–0.2 · 1.5 m 안팎 · on the defended line). C correctly flags the shared default `build_bollard(height=0.75)` (scene_common:2936-2937) as −6.25 % vs the floor `[measured ✔]`; A correctly rates scene03's override (h 0.90/Ø0.15/band) compliant and scene05's 1.5 m row as the reference form. | **PASS** (E-3 fix justified) |
| **Tactile ledger** | Both docs restate 점자블록 default-OFF (user_feedback §7 ✔ verified) rather than re-litigating 별표2's dot strip; C dependency 10 carries redteam_w3r's corrected **12-of-42 HOLD** verbatim ✔; T-3 checklist phrased "matches the panel", not "must be present". | **PASS** |
| **GT invariance** | Declared where required by S06-A (invariant tread/landing faces + prim-hash proof), 02-B (re-cache + label the new up-step), S08-A (hazard-box list → OCCL re-stamp), P-1/J-1 (AABB → full 33-scene re-judge + regr re-baseline). **Gaps at A 01-B and B S06-B** — see §4-N3. | **PARTIAL** — add 2 flags |
| **No people / no vehicles** | No spec row introduces either (D1 crates are goods; S08-B options are railings; S10-A D1 adds galvanised structure). Reference-photo panels are evidence, not scene content. | **PASS** |
| **User-quote fidelity** | No silent contradictions found. All deviations from the literal ruling are explicit supervisor questions: jitter keeps J3/J14/J15 (A §9-Q5), sceneD1 crate ±2.5° cap (C §10-Q7, reverses "abolished" for one prop class and says so), backdrop-belt second species (C §10-Q2), scene07 ±3° worn-stone cap (B §1.0, tied to S07-A refs). The n≥5 photo bar is honestly failed where it is failed (A §7, B EV-B/C, C `[근거 없음]` rows) with procurement plans instead of invented numbers — which is what the bar demands. | **PASS** |

---

## 7. What must happen before the W3 execution spec freezes

1. **Strike the chronology argument** (R1) from C §0/§3.1 wherever the exec spec inherits it. The defensible
   framing is: *the statute survey (kpg, 07-28) documented the contradiction one day after v5.1 (07-27) and it
   was never reconciled; the supervisor has now reconciled it in the statute's favour.*
2. **Adopt C's counts** where the docs disagree on scope: patch = **10/19 profiles** (R2), `bc.jit_*` = **24 sites**
   (R3), build_tree = **25 sites / 17 scenes** (verified exact).
3. **Resolve X1–X5** (species tables, verge jit_pos, fix-ID normalisation, J-6 scene13, bollard set).
4. **Add the two missing GT flags** (A 01-B, B S06-B — §4-N3) and re-derive S08-A's deletion recipe from anchors
   with the `M["tape"]→M["temtape"]` key fix (R12).
5. **Rule on `facade_kit.py:563`** (N1) so the "complete inventory" claim is true.
6. **Cite era ruling `era_consistency_survey_v1.md:881`** in the scene02 v8-block decision (N4).
7. Re-confirm the S06-A analytics on the usd-core machine as B itself requires, and correct/confirm the 99 mm
   figure (R4) before it is quoted anywhere else.
8. The photo-procurement plans (A §7, B §9.2, C §7.5 harvester) are genuinely executable — the Commons ground
   truth they describe reproduced exactly here, including the negatives (Bollards/Pedestrian-underpasses/
   Street-trees empty). Fund the ~1 h of gov-PDF fetches A lists before freezing rows 01-B, 04-A, G-6/04-B,
   S08-B, S10-A.

## 8. Sources touched this session

In-repo: the three intake docs · `scenes/main/{ground_kit,scene_common,infra_kit,facade_kit}.py` ·
`scenes/main/scene0{1..9}*.py`, `scene1{0..8}*.py`, `scene2{0,1}*.py` · `scenes/batch1/{batch1_common.py, scene*}` ·
`assets/veg_manifest_w2.json` · `assets/vegetation/{Trees,Shrub,Debris}/` ·
`Docs/reference_photos/expanded/LICENSES.csv` · `Docs/reports/{tonglam_v2,redteam_w3r,w2_veg_procurement_v1}.md` ·
`Docs/audit_v4/user_feedback_v5_1.md` · `Docs/surveys/{korean_pedestrian_geometry,era_consistency_survey_v1}.md` ·
`scripts/geom_invariance_check.py` · `look_check/scene{01..11}/260730_w2d_fix/` · git history.

Live: Commons API (`categorymembers`, `imageinfo/extmetadata` — 8 queries listed in §2.7) ·
ko.wikisource 지하공공보도시설 규칙 · law.go.kr admRulSeq=2000000017655 (body JS-blocked, noted) ·
web search corroborating 「도시숲·생활숲·가로수 조성·관리 기준」 동일수종 clause (ulex/lbox mirrors).
