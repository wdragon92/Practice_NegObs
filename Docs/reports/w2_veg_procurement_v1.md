# W2-A4 — Vegetation & Texture Procurement with Pixel Verification

Author: W2 parallel wave / A4 (vegetation assets) · 2026-07-29
Scope: MAIN tree/shrub/groundcover assets, the grass texture swap, and the tactile-block
texture check. Deliverables: files on disk + `assets/veg_manifest_w2.json` + this report.
No GPU, no render, no Isaac, no SMOKE — `usd-core` (CPU) + numpy/PIL only.

> Evidence tags on every number: `[measured]` = computed in this session from the actual
> file · `[law]` = statute/standard · `[stat]` = published statistic · `[assumed]` =
> reasoned inference (rationale given). Untagged claims are not made.

---

## 0. Bottom line (read this first)

1. **Everything the downstream agents were waiting on is on disk.** 20 new USD assets
   (10 trees + 3 shrubs + 4 groundcover + rocks) + the new grass texture set. Re-running
   the procurement scripts reports **132/132** (vegetation) and **75/75** (scene01 texture
   library, was 69/69 before this task added 6 grass files) `[measured]`.
2. **Every foliage texture was pixel-verified by UV sampling, not by species name.**
   17 assets PASS, **6 REJECTED and deleted from disk** so no other agent can pick them up
   by accident (§4). The rejects are not listed in the downloader manifest either — a
   re-run will not resurrect them.
3. **A name-blind hue gate is not sufficient — it produced a false PASS.**
   `Trees/White_Ash.usd` has foliage that is 100 % yellow-green and 0 % red/pink, so it
   passes the W1 gate verbatim, yet the texture it binds is literally
   `ashleaves1_fall2.png` with linear albedo **0.4045** and mean sRGB (0.717, 0.684, 0.099)
   — autumn yellow ash `[measured]`. I added a third test (yellow-green dominant ⇒ linear
   albedo ≤ 0.55) that catches it, and rejected the asset (§3.3).
4. **The grass swap is not just a texture upgrade — it repairs a stated convention
   violation.** Reproducing `_promote_const_to_texture` exactly: current `grass`
   (`aerial_grass_rock`) gives spread **4.22 > 4.0** for a canopy constant colour, so the
   promoter falls through to `leaf_ground` (autumn leaves) on 24 scenes. With
   ambientCG **Grass001** the spread is **1.63**, so `grass` wins as first-priority
   candidate `[measured]`. §5 shows the full table.
5. **The "Chinese_Juniper is 1/10 the polygons of the cherry" claim in
   `A_trees_shrubs.md` §P1 is wrong, and the error class affects 7 of 10 new trees.**
   That 27,098 figure is prototype-only; the asset is a `PointInstancer` with 436
   instances, so the **effective triangle count is 5,709,460** `[measured]` — 21× the
   Japanese_Cherry's 269,945 (which has no instancer). Full corrected budget in §7.1.
6. **`tactile_yellow_*` already exists and is geometrically correct on the regulated
   items** (36 dots, 6×6, pitch 50.0 mm) `[measured]`. One unregulated dimension deviates
   (dot diameter 38.1 mm) with a quantified consequence for the GT-E3 luminance gate —
   supervisor decision requested, no file changed (§6).

---

## 1. Method (reproducible, CPU-only)

| Step | Tool | Detail |
|---|---|---|
| Catalogue | S3 `?list-type=2` ListBucket | `Trees/` 44 USD, `Shrub/` 37 USD re-enumerated 2026-07-29 `[measured]` |
| Dependency derivation | `usd-core 26.8` + `Sdf.Layer` | USD → `info:mdl:sourceAsset` → MDL text → `texture_2d("…")`. **No guessing**; the same procedure the existing `--discover` flag uses |
| Geometry | `UsdGeom.Mesh` traverse | Σ(faceVertexCount − 2) per mesh; `PointInstancer.protoIndices` expanded for the effective count; size from stage-wide `BBoxCache` (default+render+proxy) |
| Leaf pixels | `UsdShade.MaterialBindingAPI.ComputeBoundMaterial` + numpy | mesh `primvars:st` sampled **into the bound texture** — an atlas holding both flowers and leaves is judged by *what the mesh actually samples* |
| Colour classes | HSV hue angle | green 65–170° · yellow-green 40–65° · orange 25–40° · red 0–25/340–360° · pink 280–340°; only S > 0.15 counted as chromatic |
| Albedo / near-white | sRGB→linear IEC 61966-2-1, Rec.709 | texture-level, 1024² LANCZOS resample (same as the W1 B audit) |

**Gates.**

```
woody   : green+yellow_green >= 0.75  AND  red+pink+orange <= 0.06
          AND (if yellow_green dominant > 0.5) linear albedo <= 0.55      ← new, §3.3
turf    : green+yellow_green >= 0.75  AND  red+pink <= 0.02  AND  orange <= 0.25
```

The separate **turf gate is mine and is tagged `[assumed]`**: straw-coloured blades in a
lawn are present year-round (thatch), so the ≤ 0.06 chromatic-defect limit — designed to
catch autumn canopies — would reject every real lawn atlas. The red/pink limit is
*tightened* to 0.02 in exchange. It changes exactly one verdict pair: `Grass_Short_*`
passes (green+yg 0.83, orange 0.18), `Grass_Trimmed_*` still fails (green+yg 0.72 < 0.75).

**Control run.** The pipeline was run against `Trees/Japanese_Cherry.usd` first:
pink 53.5 % / red 44.3 % / **green 0.0 %** → FAIL `[measured]`, and the underlying
`cherryblossom.png` measures pink 78.1 % `[measured]`. This reproduces the W1 finding from
an independent implementation, so the tooling is trusted for the new assets.

---

## 2. What was delivered

### 2.1 Trees — `assets/vegetation/Trees/` (10 new, all PASS)

Size is the **stage-wide world bounding box in metres** (instances included). `tri_uniq` =
unique geometry, `tri_eff` = after instance expansion. `z_min` matters because
`build_tree` does **not** apply the grounding correction that `place_shrubs` does
(A §6-c) — anything with a negative `z_min` will sink.

| Asset | Role | X·Y·**Z** (m) `[measured]` | z_min | tri_uniq | **tri_eff** | inst | leaf hue g/yg `[measured]` | leaf tex albedo |
|---|---|---|---|---|---|---|---|---|
| `Chinese_Juniper.usd` | temple / civic evergreen | 1.077 · 1.060 · **2.544** | −0.028 | 27,098 | **5,709,460** | 436 | 1.00 / 0.00 | 0.192 |
| `Elm_Sapling.usd` | street, near field (zelkova stand-in) | 1.742 · 1.750 · **3.087** | −0.000 | 113,268 | **113,268** | 0 | 1.00 / 0.00 | 0.078 |
| `Shumard_Oak.usd` | street broadleaf, main | 10.301 · 10.466 · **11.438** | **−0.539** | 99,509 | **4,552,624** | 450 | 0.75 / 0.25 | 0.127–0.144 |
| `Fraxinus.usd` | street (Chionanthus stand-in) | 4.851 · 4.510 · **5.341** | −0.000 | 97,528 | **1,251,064** | 26 | 1.00 / 0.00 | 0.118 |
| `Gray_Birch.usd` | park / apartment | 2.672 · 2.563 · **3.332** | −0.003 | 256,625 | **256,625** | 0 | 1.00 / 0.00 | 0.068 |
| `Lombardy_Poplar.usd` | riverside (03·12·17) | 4.839 · 4.491 · **13.671** | 0.000 | 417,906 | **417,906** | 0 | 1.00 / 0.00 | 0.122 |
| `Douglas_Fir.usd` | temple / hillside conifer | 3.023 · 2.771 · **6.026** | 0.000 | 24,336 | **1,232,864** | 549 | 1.00 / 0.00 | 0.192 |
| `Colorado_Spruce.usd` | **far background only** | 3.579 · 3.763 · **4.061** | −0.189 | 140,587 | **15,597,637** | 454 | 1.00 / 0.00 | 0.254 |
| `Scarlet_Oak.usd` | park broadleaf variety | 10.410 · 10.258 · **12.753** | **−0.344** | 49,899 | **2,230,425** | 270 | 0.74 / 0.26 | 0.127–0.144 |
| `Black_Oak.usd` | **background mature only** (25 m) | 25.424 · 24.067 · **19.739** | 0.000 | 86,878 | **2,953,010** | 3,735 | 0.87 / 0.13 | 0.127–0.144 |

Red / pink / orange fractions are **0.000 for all ten** `[measured]`.

### 2.2 Shrubs — `assets/vegetation/Shrub/` (3 new, all PASS, all evergreen)

Chosen deliberately as evergreens: an evergreen has no seasonal axis at all, so the
"no seasonal assets" rule cannot be re-violated by a later re-render.

| Asset | Role | X·Y·**Z** (m) | z_min | tri_uniq | tri_eff | hue g/yg/o | leaf texture |
|---|---|---|---|---|---|---|---|
| `Holly.usd` | hedge / planter | 2.316 · 2.378 · **1.526** | −0.084 | 361,070 | 664,658 | 1.00/0/0 | `hollyprivet_basecolor.png` (alb 0.086) |
| `Yew.usd` | formal planter, kerb-height | 1.227 · 1.235 · **0.728** | −0.013 | 144,320 | 144,320 | 1.00/0/0 | `pine_needles.png` (alb 0.192) |
| `Cedar_Shrub.usd` | narrow planter / boundary | 0.287 · 0.288 · **0.876** | −0.000 | 186,446 | 186,446 | 0.97/0/0.03 | `cedar_atlas1_basecolor.png` (alb 0.169) |

`Cedar_Shrub` has no authored `extent`, so `BBoxCache` returns an empty range; the size
above is from a direct local→world transform of the mesh points `[measured]`.

### 2.3 Groundcover / edge weeds — for `ground_kit` §5 weed bands and the scene04 verge

| Asset | Role | X·Y·**Z** (m) | tri | hue g/yg/o | Notes |
|---|---|---|---|---|---|
| `Grass_Short_A.usd` | verge turf, large | 1.289 · 1.294 · **0.162** | 32,504 | 0.54/0.29/0.18 | direct replacement for the 121 verge blobs (A §4) |
| `Grass_Short_B.usd` | verge turf, medium | 0.662 · 0.675 · **0.164** | 11,137 | 0.53/0.29/0.18 | |
| `Grass_Short_C.usd` | **edge weed tuft** | 0.279 · 0.304 · **0.125** | 1,598 | 0.54/0.28/0.18 | spec §5.4 15-8 wants h ≤ 0.12 → scale 0.96; the GT-E1′ ramp clamp stays a placement-side job |
| `Switchgrass.usd` | riparian grass band | 2.009 · 2.027 · **1.372** | 8,934 | 1.00/0/0 | no flower-spike mesh; candidate for the scene09 reed band |

All four share **one** material (`lawngrass_a_mat` / `Switchgrass_Mat`), so mixing sizes
costs no extra material `[measured]`.

### 2.4 Textures — `assets/` root (ambientCG, CC0)

| File set | Source | Tile | Green | Linear albedo | near-white(>0.8) |
|---|---|---|---|---|---|
| `grass_lawn_{diff,nor,rough}.jpg` | **Grass001** | **1.40 × 1.40 m** `[measured — API dimensionX/Y]` | **98.25 %** | 0.0932 | 0.000 |
| `grass_lawn_b_{diff,nor,rough}.jpg` | Grass004 (alternate) | 1.40 × 1.40 m | 70.4 % | 0.1465 | 0.000 |
| *(incumbent, for contrast)* `aerial_grass_rock` | PolyHaven | 15.0 × 15.0 m | **0.00 %** (yellow-green 81.4 %, orange 18.4 %) | 0.127 | 1.2e-05 |

The incumbent "grass" texture contains **zero green chromatic pixels** `[measured]` — an
independent confirmation of the W1 B audit's finding that it is a mossy rock scan, from a
completely different measurement (hue histogram vs. tag/px-density argument).

`Grass007` (tagged moss/weeds) was **not** procured: the ambientCG API returns
`dimensionX = dimensionY = 0` `[measured]`, so no physically defensible `scale_m` can be
set — procuring it would repeat exactly the mistake being fixed.

### 2.5 Rocks — `Rocks/rock_small_{02..07,11..14}` (10 added → 15/15 complete)

Closes B audit action **C3**. Non-foliage, so no hue gate applies; they are riprap
diversity for scene12 (96 stones) and scene03. 40 files, all size+MD5 verified `[measured]`.

---

## 3. Pixel verification — full results

### 3.1 Trees: what each canopy actually samples

Every accepted tree binds one of six leaf textures, and each was opened and measured:

| Texture | px | green | yellow-green | orange | red | pink | linear albedo |
|---|---|---|---|---|---|---|---|
| `beech_leaf_basecolor.png` (Elm_Sapling) | 512² | 1.000 | 0 | 0 | 0 | 0 | **0.078** |
| `hollyprivet_basecolor.png` (Gray_Birch, Holly) | 1024² | 1.000 | 0 | 0 | 0 | 0 | 0.068–0.086 |
| `fraxinus_basecolor.png` | 1024² | 1.000 | 0 | 0 | 0 | 0 | 0.118 |
| `lombardypoplar_leaf_basecolor.png` | 256² | 0.9997 | 0.0003 | 0 | 0 | 0 | 0.122 |
| `oakleaves1/2/3/4_basecolor.png` | 1024² | 1.0 / **0.0** / 1.0 / 1.0 | 0.0 / **1.0** / 0.0 / 0.0 | 0 | 0 | 0 | 0.127–0.144 |
| `pine_needles.png` (Juniper, Douglas_Fir, Yew) | 256² | 0.802 | 0.198 | 0 | 0 | 0 | 0.192 |
| `spruce_needles.png` | 256² | 1.000 | 0 | 0 | 0 | 0 | 0.254 |
| `cedar_atlas1_basecolor.png` | 4096² | 0.972 | 0.019 | 0.009 | 0.0002 | 0 | 0.169 |
| `switchgrass_basecolor.png` | 512² | 1.000 | 0 | 0 | 0 | 0 | 0.209 |
| `lawngrass_a_basecolor.png` | 2048² | 0.236 | 0.322 | 0.438 | 0.004 | 0 | 0.321 |

`oakleaves2` is the one yellow-green sheet of the four-variant oak atlas; it is olive
foliage (mean sRGB 0.438, 0.402, 0.205, luma 0.395), not autumn yellow — that is why the
albedo side-condition, not the hue bin, is what separates it from `ashleaves1_fall2`
(luma 0.649) `[measured]`.

### 3.2 Leaf albedo vs. the physical reference — A §6-e needs re-scoping

A §6-e proposed a blanket `diffuse_tint ≈ 0.45` on leaf materials because canopy albedo
should be ~0.15–0.20. Against the new set that prescription would **over-darken most of
it**: beech 0.078 → 0.035, hollyprivet 0.086 → 0.039 `[measured, calculated]`.

| Band | Textures | Action |
|---|---|---|
| Below reference (0.068–0.122) | beech, hollyprivet, fraxinus, poplar | **no attenuation** — already dark |
| Inside reference (0.127–0.169) | oakleaves 1–4, cedar_atlas1 | no attenuation |
| Above reference (0.192–0.321) | pine_needles, switchgrass, spruce_needles, lawngrass_a | attenuation 0.6–0.8 is defensible `[assumed]` |

Recommendation: make the tint **per-texture, not per-class**, and apply it only to the
third band. This is a T1/material-layer decision, flagged here with the numbers attached.

### 3.3 The false PASS that forced a third gate condition

| Signal | `White_Ash.usd` | Verdict |
|---|---|---|
| W1 hue gate (green+yg ≥ 0.75, bad ≤ 0.06) | yg 1.000, bad 0.000 → **passes** | insufficient |
| Bound texture filename | `ashleaves1_fall2.png` | name-based *reject* signal only |
| Linear albedo of the leaf texture | **0.4045** (reference 0.15–0.20) | 2.0–2.7× too bright |
| Mean sRGB | (0.717, 0.684, 0.099) → luma 0.649 | autumn yellow |

Three independent signals agree; the asset is rejected. The gate now carries
"yellow-green dominant ⇒ albedo ≤ 0.55", which also catches `Barberry` (albedo 0.263,
golden cultivar) while leaving `oakleaves2` (albedo 0.127) and `Shumard/Scarlet/Black_Oak`
untouched `[measured]`.

---

## 4. Rejections and their substitutes

| Rejected | Measured reason | Substitute already procured |
|---|---|---|
| `Trees/White_Ash.usd` | binds `ashleaves1_fall2.png`; albedo 0.4045, luma 0.649 | `Fraxinus.usd` — same genus, green 100 %, albedo 0.118 |
| `Shrub/Barberry.usd` | `barberry_basecolor.png` yellow-green 99.9 %, albedo 0.263, green **0 %** | `Yew` / `Cedar_Shrub` / `Holly` (evergreen ornamentals) |
| `Shrub/Grass_Trimmed_A/B/C.usd` | green+yg **0.717 / 0.714 / 0.719 < 0.75**, orange 0.28 — samples the straw region of the shared atlas ⇒ reads as dormant turf | `Grass_Short_A/B/C` (same material, green region) |
| `Shrub/Fountain_Grass_Short.usd` | plume mesh is **60.3 %** of triangles and its texture `pampas_flower.png` has **41.5 % of pixels above linear luminance 0.8** and albedo 0.641 ⇒ **violates the large-near-white rule**, plus a flowering-season signature | `Switchgrass.usd` (green 100 %, no flower mesh) |

All six USDs and their exclusive textures were **deleted from `assets/vegetation/`** and
are absent from the downloader manifest, so a re-run cannot restore them `[measured — the
re-run reports 132/132 with none of them present]`.

`Fountain_Grass_Short` could be rescued by deactivating the `Pampas_flower_Mat` prim
(the same treatment A §P1 proposed for `Rhododendron`/`Kousa_Dogwood`) — that is a
supervisor call, not mine, and it is listed in §10.

**The W1 rejects were deliberately left on disk.** `Japanese_Cherry`, `Forsythia`,
`Burning_Bush` and `Rhododendron` failed the W1 audit but are still referenced by
`VEG_TREES` / `VEG_SHRUBS` in `scene_common.py`; deleting the files would make
`veg_available()` fail and break every current render before the table is edited.
Removal must be the **second** step, after the table owner drops the entries. The six
assets *I* rejected were never referenced by any table, so deleting them is safe and
prevents accidental adoption.

---

## 5. The grass swap repairs the LOOK_V1 promotion violation (§8 of the B audit)

`_promote_const_to_texture` accepts a candidate only if `max(ratio) ≤ max_gain` **and**
`spread = max(ratio)/min(ratio) ≤ 4.0`. Reproducing the exact code path (64² thumbnail,
sRGB→linear mean) against three vegetation constant colours:

| Texture used for role `grass` | linear mean RGB | R/B | canopy_a (0.025,0.045,0.015) | canopy_b | shrub |
|---|---|---|---|---|---|
| **incumbent** `aerial_grass_rock` | (0.1688, 0.1210, 0.0240) | 7.03 | spread **4.22 → reject** | 4.69 reject | 4.42 reject |
| **`grass_lawn` (Grass001)** | (0.0582, 0.1061, 0.0216) | 2.69 | spread **1.63 → accept** | 1.79 accept | 1.80 accept |
| `grass_lawn_b` (Grass004) | (0.1185, 0.1523, 0.0303) | 3.92 | 2.35 accept | 2.61 accept | 2.46 accept |
| `leaf_ground` (autumn leaves) | (0.0614, 0.0386, 0.0150) | 4.09 | 2.86 accept ← *what currently wins* | 2.92 | 2.73 |

`[measured — all six numbers recomputed here; the incumbent row reproduces B §8 exactly,
which cross-validates both implementations]`

Because `_promote_const_to_texture` tries `spec["tex"]` (= `grass`) **first**, swapping the
files makes `grass` win and `leaf_ground` never gets reached for the `veg` class. That
removes the autumn-leaf-on-canopy condition on 24 scenes **without** editing
`LOOK_CLASS`. Wiring is the table agent's call; the files and the numbers are here.

**Handoff snippet** (not applied by me — `scene_common.py` is owned by the worktree agent):

```python
grass=dict(dir=ASSETS_DIR, diff="grass_lawn_diff.jpg",
           nor="grass_lawn_nor.jpg", rough="grass_lawn_rough.jpg"),
# scale_m must become 1.4 in every scene that sets scale=dict(grass=…)
# (currently 4.0 in 27 scenes, 2.6 in scene10) — 1.4 is the measured tile size.
```

---

## 6. Tactile block texture — verified present, one deviation

`assets/scene01/tactile_yellow_diff.png` and `_nor.png` **already exist** (1024², procedurally
generated by `download_scene01_assets.py:build_tactile`), so no new generator was written.
I measured the actual pixels by connected-component analysis of the normal map:

| Item | Spec §12.1 `[law]` | Measured `[measured]` | Verdict |
|---|---|---|---|
| Dot count | 36 (6×6) | **36**, 6 columns × 6 rows | ✔ |
| Pitch | 50 mm | **50.0 mm** (170.67 px @ 0.293 mm/px, tile = 0.30 m) | ✔ |
| First column centre | 25 mm | **26.4 mm** (+1.4 mm) | ✔ within tolerance |
| Dot form | hemisphere / truncated cone | hemispherical height field `h = √(1−(d/r)²)` | ✔ |
| Height | 6 ± 1 mm | not encoded in the texture (relief comes from `build_tactile_pair`) | n/a |
| Colour | yellow | mean sRGB (0.874, 0.700, 0.008), **linear albedo 0.484** | ✔ and under the §12.5 ④ 0.55 clamp |
| **Dot diameter** | **not specified in §12.1** | **38.1 mm** | see below |

The spec table regulates count, pitch, first-column offset and height, but not diameter.
At 38.1 mm the dot area fraction is **45.6 %** of the tile versus **19.6 %** if the commonly
cited 22–25 mm base diameter were used `[calculated]`; a larger yellow fraction raises the
mean panel luminance and therefore **works against the GT-E3 luminance-step gate** that
§12.5 ④ already flags as tight. I did **not** change the file — it is wired into scene01
and batch1 today, and a silent change mid-wave would invalidate other agents' renders.
One-line change if approved: `dot_d = N / 8.0` → `N / 12.0` (= 25.0 mm).
Whether a Korean legal diameter exists is `[assumed]` — I could not verify a statutory
figure in-session, only the derived area consequence.

---

## 7. Corrections to prior documents

### 7.1 Triangle budgets in `A_trees_shrubs.md` are prototype-only

7 of the 10 new trees are `PointInstancer` assets. Unique geometry and rendered geometry
differ by up to **111×** `[measured]`:

| Asset | unique tri | instances | **effective tri** | ratio |
|---|---|---|---|---|
| `Colorado_Spruce` | 140,587 | 454 | **15,597,637** | 111× |
| `Chinese_Juniper` | 27,098 | 436 | **5,709,460** | 211× |
| `Shumard_Oak` | 99,509 | 450 | 4,552,624 | 46× |
| `Black_Oak` | 86,878 | 3,735 | 2,953,010 | 34× |
| `Scarlet_Oak` | 49,899 | 270 | 2,230,425 | 45× |
| `Fraxinus` | 97,528 | 26 | 1,251,064 | 13× |
| `Douglas_Fir` | 24,336 | 549 | 1,232,864 | 51× |
| `Elm_Sapling`, `Gray_Birch`, `Lombardy_Poplar` | 113,268 / 256,625 / 417,906 | 0 | same | 1× |

Consequences for `ground_kit_spec` §8 (per-scene prim/triangle budget) and for A §P1's
"Chinese_Juniper = 1/10 the polygons" recommendation:

- **`Elm_Sapling` is the genuinely cheap near-field tree** (113 k, no instancer), not
  Chinese_Juniper.
- **`Colorado_Spruce` must not be placed in the near field**; one instance is ~15.6 M
  triangles, which alone exceeds any plausible per-scene budget. Marked optional in the
  manifest and labelled "far background only".
- Instanced triangles are cheap in *memory* but not in *raster* work; whether the budget
  should count unique or effective triangles is a spec question for the budget owner.

### 7.2 Leaf-texture duplication is wider than A §6-d reported

A §6-d noted Boxwood and Privet share `hollyprivet_basecolor.png`. Adding the new set,
**four assets now share that one texture**: `Privet`, `Boxwood`, `Holly` (Shrub copy) and
**`Gray_Birch`** (Trees copy) `[measured — MDL text]`. A birch with privet leaves is not a
seasonal violation, but "species diversity" claims based on asset count are void.
Similarly `pine_needles.png` is shared by White_Pine, Yellow_Pine, Juniper,
Chinese_Juniper, Douglas_Fir and Yew — six assets, one needle texture.

### 7.3 A latent bug in the existing verifier (fixed, my file)

`download_vegetation.verify()` tested `head8.startswith(b"mdl ")`, which flags a **valid**
MDL that begins with a newline. `Trees/materials/Scarlet_Oak_leaf_Mat.mdl` starts with
`b"\nmdl 1.4"` and was reported as corrupt `[measured]`. Fixed to `head8.lstrip()
.startswith(b"mdl")`; the run then reports "All vegetation assets downloaded and verified".

---

## 8. Handoff — what other agents need from this

| Consumer | What it needs | Where |
|---|---|---|
| `scene_common` table owner | `VEG_TREES` / `VEG_SHRUBS` rows: native **height** (not width), `z_min`, triangle cost | §2.1–2.3 tables + `assets/veg_manifest_w2.json` → `geometry` |
| same | `TEX["grass"]` swap + `scale_m = 1.4` | §5 snippet |
| `ground_kit` §5 weed bands | `Shrub/Grass_Short_C.usd`, h = 0.125 m | §2.3 |
| `ground_kit` §12 tactile wiring | `TEX["tactile"]` files verified present, albedo 0.484 < 0.55 | §6 |
| scene04 / scene07 blob replacement | `Grass_Short_A/B`, `Holly`, `Yew`, `Cedar_Shrub` | §2.2–2.3 |
| Budget owner | effective-vs-unique triangle table | §7.1 |

Reproduce everything:

```bash
python assets/download_vegetation.py --only trees_neutral,shrub_neutral,groundcover,rocks_extra
python assets/scene01/download_scene01_assets.py        # includes Grass001/Grass004
```

Both are idempotent (size + MD5 skip). Current state: **132/132** and **75/75** `[measured]`.

---

## 9. Constraint compliance

| Constraint | Status |
|---|---|
| No seasonal / event-specific assets; verify leaf pixels, never trust species names | **Enforced by measurement.** `Japanese_Maple` was *not* procured despite A §P1 listing it as a pass — 82 MB for a species whose non-fall/fall pair invites exactly the naming confusion that produced the `White_Ash` false positive; the broadleaf role is covered by 6 verified assets. All 6 rejects were name-blind decisions backed by pixels |
| No large near-white (> 0.8) | Checked on **every** new texture. Max among accepted assets: `pampas_flower.png` 41.5 % → **rejected on this ground**. All accepted assets: ≤ 0.003 % |
| No atmospheric haze / utility poles / urban infra in nature scenes / bollards / tactile paving policy | Out of scope for this task; nothing placed, no scene file touched |
| Files touched | `assets/download_vegetation.py`, `assets/scene01/download_scene01_assets.py`, `assets/veg_manifest_w2.json`, this report, and binary assets under `assets/`. **`scene_common.py` and all scene files untouched** |
| GPU / render / Isaac / SMOKE | Not run. `usd-core` (pip) parsing + numpy/PIL only |
| Git | No commit, no push, no checkout |
| Licensing | NVIDIA S3 assets are **not** CC0 — redistribution of the USD/textures is prohibited; `assets/vegetation/` is already git-ignored, and the new `assets/*.jpg` grass files fall under the existing `assets/*.jpg` ignore rule `[measured — .gitignore]`. ambientCG Grass001/004 are CC0 |

Note for the repo owner: the `.gitignore` comment still says the vegetation directory is
"~128 MB"; it is now **918 MB** across 192 files `[measured]`. `.gitignore` is not my file,
so I did not edit it.

---

## 10. Open items / supervisor decisions

1. **Sycamore (plane tree) gap.** Seoul's #2 street species at 20.9 % `[stat — W1 A §5-b]`
   has no season-neutral asset: `Sycamore.usd` geometry is correct but all four leaf
   sheets are brown litter (green 0 %) `[measured — W1]`. A §P4 proposed hue-rotating the
   texture into a green derivative. I did **not** do it — a recoloured derivative is a new
   asset class needing a ruling, and ginkgo (35.8 %) has no S3 asset at all.
2. **`Fountain_Grass_Short` conditional rescue** by deactivating the plume prim (would add
   a native ornamental grass); same pattern as the `Rhododendron` flower-off ruling.
3. **Tactile dot diameter** 38.1 mm vs. the 19.6 %/45.6 % area consequence (§6) — change or keep.
4. **Triangle budget basis** — unique vs. effective triangles for `ground_kit` §8.
5. **Leaf-albedo attenuation should be per-texture, not per-class** (§3.2); A §6-e's
   blanket 0.45 would over-darken 4 of the 10 new leaf textures.

---

## Appendix A — inventory

- `assets/vegetation/`: 192 files, 918 MB — 13 `Trees/*.usd` + 13 `Shrub/*.usd` +
  5 `Debris/*.usd` + 15 `Rocks/*.usda` `[measured]`
- `assets/grass_lawn_{diff,nor,rough}.jpg` 26.3 / 41.3 / 11.8 MB; `grass_lawn_b_*` 28.1 / 41.5 / 12.3 MB `[measured]`
- `assets/veg_manifest_w2.json` — 17 accepted + 6 rejected assets + 3 textures, with
  per-asset hue statistics, geometry and reject reasons

## Appendix B — sources

- NVIDIA Omniverse vegetation bucket (no auth):
  `https://omniverse-content-production.s3.us-west-2.amazonaws.com/?list-type=2&prefix=Assets/Vegetation/`
- ambientCG API v2: `https://ambientcg.com/api/v2/full_json?id=Grass001&include=dimensionsData,tagData`
  (dimensionX/Y = 140 cm), download `https://ambientcg.com/get?file=Grass001_4K-JPG.zip`
- Prior audits reproduced/corrected here: `Docs/surveys/props_audit_w1/A_trees_shrubs.md`,
  `Docs/surveys/props_audit_w1/B_groundcover_debris.md`, `Docs/briefs/ground_kit_spec_v1.md` §5·§8·§12
