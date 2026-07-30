# W3 Procurement — manifest v3, assets local and verified (v1)

> **Wave**: W3 · **Task**: procurement · **Date**: 2026-07-30 · **Branch**: `feat/realism-v1`
> **Doctrine**: asset-first — maximise use of available assets; rebuild procedurally only where an
> asset clearly breaks the Korean archetype.
> **Files written**: `assets/download_urban.py`, `assets/verify_urban.py`,
> `assets/urban_manifest_w3.json`, `.gitignore` (+2 rules), this report.
> **No scene file and no shared module was touched. No render, no Isaac, no GPU.**
> The assets themselves are untracked by design (licence for NVIDIA, size for CC0).
> **Inputs**: `surveys/w3r_asset_map_v1.md` (R1) · `surveys/w3r_prop_mapping_v1.md` (R2) ·
> `surveys/w3r_building_ab_v1.md` (R3) · `reports/redteam_w3r.md` (RT) ·
> `assets/veg_manifest_w2.json` (schema + gate definitions).
> Evidence tags: `[measured]` executed this session · `[law]` licence text · `[assumed]` inference.

---

## 0. Verdict

**1,160 files / 1.301 GB on disk, 291 assets, 0 download failures.** Budget was ≤ ~1.5 GB.
Verification: **PASS 258 · WARN 17 · FAIL 1 · SKIP 15**. Every USD that carries geometry opens
under usd-core and yields meshes — the only zero-triangle entries are the six sign *material
libraries*, which have no geometry by design. Re-running the downloader downloads **zero bytes**
(`ok 0 · skip 2323 · fail 0`) and reproduces a byte-identical tree.

Five things changed relative to the survey wave, all `[measured]`:

1. **The unresolved-texture blocker is cleared, and it was three buildings, not two.**
   `typical_building_18` → 20 generically-named `shared_textures/` maps (`brick_white_01_*`,
   `plaster_white_01/02_*`, `tile_roof_01_*` …); `typical_building_106` → 8 maps named
   `opaque_building_106_*` / `opaque_metal_ac_unit_{4,5,6}_*`; and **`typical_building_109`, which
   nobody flagged, also has zero prefix matches**. Per-asset `--resolve` finds all three; the
   prefix heuristic loses them silently. §3.
2. **R1 §6.5's Z-placement table is wrong for the whole mid tier, not just `typical_building_10`.**
   All ten `typical_building_*` measure **0.0 % of triangles below grade** despite bbox `zmin`
   of −1.08 … −10.34 m: the negative extent is a foundation/basement box and **local z = 0 is
   street grade**. Applying the tabulated lift would hoist every facade. RT was right about tb10
   and the finding generalises. §5.1.
3. **`veg_shrub_hedge_round_01` fails the season rule — and `veg_shrub_hedge_yellow_01` passes.**
   RT-4 asked for a pixel gate on the *yellow* hedge on the strength of its name. Measured at the
   mesh-binding level, the yellow hedge binds a **green** atlas over 89.4 % of its triangles
   (green 0.941, warm 0.002 → PASS), while `hedge_round` binds a **dry straw/orange** atlas over
   **74.6 %** of its triangles (green 0.000, yellow-green 0.494, orange 0.467 → FAIL) plus a
   **fruit** atlas on 1.3 %. The name was the wrong instrument; the binding share is the right one. §6.1.
4. **All eight far-tier `bldgs_01_distant/Building_*` violate the near-white rule.** They share
   `house_wall_001_Diffuse.png` (linear albedo **0.874**, 99.6 % of pixels above linear 0.8) and
   `concrete_014_Diffuse.png` (albedo **0.969**, 98.7 %). The project cap is albedo ≤ 0.8 on large
   areas. These are 30–130 m skyline objects. **Do not ship them untinted.** §6.2.
5. **Three procured "assets" are aliases, and one of them re-imports an asset R2 declined.**
   `bench_park_01` → `../bench_park_03`, `concrete_block_02` → `../concrete_block_01`, and
   **`bench_park_05` → `../bench_curved_01`** — the last being one of the six items R2 §5.3 lists
   as explicitly *not* procured. Buying `bench_park_05` buys `bench_curved_01` under a different
   name. §5.3.

Two items need a supervisor ruling before W3 implementation. §9.

---

## 1. What shipped

`cost_if_alone` = what that group costs if fetched with `--only`, **including** shared
dependencies. Those shared files are counted once on disk, which is why the group column sums to
more than the total. The `unique` row is the one that matches `du`.

| Group | Assets | Files (solo) | MB (solo) | PASS | WARN | FAIL | SKIP |
|---|---:|---:|---:|---:|---:|---:|---:|
| `_core` (SimPBR MDL family) | 9 | 9 | 0.1 | 0 | 0 | 0 | 9 |
| `buildings_mid` | 11 | 146 | 272.6 | 11 | 0 | 0 | 0 |
| `buildings_far` | 8 | 216 | 118.7 | 0 | **8** | 0 | 0 |
| `signs_kr` (156 plates + 6 material USD) | 162 | 1100 | 112.5 | 155 | 1 | 0 | 6 |
| `roadmarks_kr` | 9 | 81 | 352.4 | 9 | 0 | 0 | 0 |
| `midground` | 17 | 160 | 86.7 | 16 | 0 | **1** | 0 |
| `poles` | 12 | 134 | 308.5 | 12 | 0 | 0 | 0 |
| `props` | 13 | 121 | 58.0 | 7 | 6 | 0 | 0 |
| `rocks_gap` | 3 | 24 | 51.3 | 3 | 0 | 0 | 0 |
| `water` | 2 | 28 | 60.2 | 2 | 0 | 0 | 0 |
| `reopened` | 12 | 95 | 153.2 | 10 | 2 | 0 | 0 |
| `polyhaven_cc0` (CC0) | 33 | 209 | 337.1 | 33 | 0 | 0 | 0 |
| **TOTAL (unique on disk)** | **291** | **1160** | **1301.5** | **258** | **17** | **1** | **15** |

Split by root: **NVIDIA 951 files / 964.4 MB → `assets/urban/`** (redistribution forbidden);
**Poly Haven 209 files / 337.1 MB → `assets/urban_cc0/`** (CC0 1.0, redistributable; ignored for
size only). Both `.gitignore` rules landed **in the same commit as the downloader**, per RT §1.5-1.

Against R1 §5.5's lean estimate of 485.49 MB / 785 files: the NVIDIA half came in at 964.4 MB /
951 files. The difference is not scope creep — it is dependencies R1's per-asset roll-up did not
include (the `nv_core/materials/markings_road/` library behind the KR road stencils, the
`props_poles` texture sets, and the `usa/scene_nvidia_campus/` brick maps the far tier reaches
into). Everything R1 declined stayed declined: `apt_complex_assembly` (672 MB), `sct_leaf_pile_04/05`
(352 MB), the `lightpost_5m_steel_a_*` group (480 MB), all `rivermark_plaza_bldg_*`.

### 1.1 Reproduction

```bash
python assets/download_urban.py --list                 # groups, cost, totals
python assets/download_urban.py                        # fetch (re-run safe)
python assets/download_urban.py --only signs_kr        # selective
python assets/download_urban.py --retotal              # recompute unique totals

# these two need usd-core (NOT Isaac):
#   python3 -m venv /tmp/usdvenv && /tmp/usdvenv/bin/pip install usd-core
/tmp/usdvenv/bin/python assets/download_urban.py --resolve
/tmp/usdvenv/bin/python assets/download_urban.py --verify
/tmp/usdvenv/bin/python assets/download_urban.py --discover <s3-key>
/tmp/usdvenv/bin/python assets/verify_urban.py --sheet  # 158-plate contact sheet
```

### 1.2 Idempotency `[measured]`

| Run | Result |
|---|---|
| 2nd `--resolve` (independent re-derivation from local layers) | every group byte-identical to the 1st: `buildings_mid` 146 f / 272.62 MB · `signs_kr` 1100 f / 112.51 MB · `roadmarks_kr` 81 f / 352.40 MB · … |
| 2nd `download_urban.py` | **`ok 0 · skip 2323 · fail 0`** — zero bytes fetched |
| structural header check | **0 failures** over 1,160 unique files (USD magic / PNG / JPEG / DDS / MDL version pragma) |
| tree fingerprint (sha256 over sorted `relpath:size`) | **`3cbeaef97a420f5b`**, 1,160 files, 1,301,465,229 B — identical before and after |

Per-file byte log: `assets/urban/_verify/per_file_bytes.tsv` (untracked, regenerated on demand).

---

## 2. The licence guard is code, not a comment

`BANNED_SUBSTRINGS` raises `LicenceViolation` **before the request is made**. Nothing is skipped
quietly — a silent skip would leave a silently incomplete manifest. A self-test runs at the top of
every `--resolve` / fetch and asserts 7 known-bad keys are rejected **and** 4 known-good keys are
not (over-blocking is a bug too). It printed `[guard] BANNED_SUBSTRINGS self-test OK` on every run
this session `[measured]`.

| Class | Substrings | Why |
|---|---|---|
| Limited Use mirror | `Environments/` · `/Rivermark/` · `Isaac/4.5/Isaac/` | `environment-supplement-LICENSE.txt`: Limited Use Content is licensed *"for your use only, **without modifications**"*, and our pipeline scales / re-materials / re-parents everything `[law]` |
| Supervisor decline (name) | `rivermark_plaza_bldg_` | textually Content, but named for the Limited Use environment. 27 `typical_building_*` cover the need at zero cost |
| Supervisor decline (supplier) | `streetlamp_led_03` (CGTrader) · `bollard_02`, `safety_railing_01`, `double_crossarm` ×5 (Mathworks_Modified) · `/piaggio/` (Hum3D) | resolved to exact asset names by parsing `nv_content/manifest.csv`'s `_Supplier` column, 2,124 rows `[measured]` |
| Project discipline | `/People/` · `/Characters/` · `ncap_` · `pedestrian_generic_` · `/vehicles/{ford,volvo,hero}/` | STATUS 규율 (사람·차량 보류) + brand vehicles |

Supplier resolution `[measured]` — the survey said "1 each" without naming them:
CGTrader = `props_poles/streetlamp_led_03` (a **streetlamp**, i.e. it sat directly in the
category we were shopping in); Hum3D = `vehicles/piaggio/ape_50`; Mathworks_Modified = 7 rows
(`bollard_02`, `safety_railing_01`, `double_crossarm_{full,half}_{med,sm}` in both `props_general`
and `props_poles`). Agility3 (83), BDesign (50), SimAction (22), Kraken (1), SpeedTree (1) are
**not** declined and are unaffected.

### 2.1 One licence item the guard deliberately does *not* block — needs a ruling

Three procured assets pull **rivermark-named shared textures** as transitive dependencies:

| Asset | Textures |
|---|---|
| `concrete_block_01` / `concrete_block_02` | `opaque__concrete__rivermarkConcreteBlocks_{Albedo,Normal}.png` |
| `trashcan_cylinder_01` | `urban_b_atlas_rivermark_{albedo,normal,orm}.png` |
| `bench_park_05` (= `bench_curved_01`) | `T_opaque__concrete__rivermarkEntranceSign_{Albedo,Normal}.png` |

These live at `NVIDIA/dsready_content/nv_content/common_assets/shared_textures/` — the **general
Content root**, outside the `/Isaac/Environments` path the supplement scopes `[law]`. So they are
not a licence violation. But the supervisor's decline was phrased by *name*, so this is surfaced
rather than decided: blocking them by name would silently break three assets' materials (missing
maps → default shading), not merely drop them. Recorded per-asset in the manifest as
`rivermark_named_transitive` and carried as WARN. **Ruling needed.** §9.

---

## 3. Blocker cleared — the unresolved-texture buildings

R1 §6.4(b) recorded that `typical_building_18` and `_106` have **zero** matching files in
`shared_textures/` under a name-prefix search, and required per-asset `--discover` before the
manifest could be finalised. Done, and one more case found.

| Building | Prefix matches | Textures actually referenced (from `_inst.usd`) | Resolved |
|---|---:|---|---|
| `typical_building_10` | 6 | 4: `..._wall_{a,n}.png`, `..._windows_{a,n}.png` | the 2 `_orm` maps are in the pool but **no layer references them** |
| `typical_building_18` | **0** | 21: `brick_white_01_{a,n}` · `concrete_slab_01_{a,n}` · `door_wood_01_{a,n}` · `metal_painted_rusty_01_{a,n}` · `metal_steel_galvanized_01_{a,n}` · `plaster_white_01_{a,n}` · `plaster_white_02_{a,n}` · `roof_gravel_01_{a,n}` · `tile_roof_01_{a,n}` · `wood_planks_01_{a,n}` · `_base/swatch_kelvin_01_c.png` | ✅ generic material names, no relation to the asset name |
| `typical_building_106` | **0** | 8: `opaque_building_106_{a,n}` · `opaque_metal_ac_unit_{4,5,6}_{a,n}` | ✅ prefix is `opaque_building_106`, not `typical_building_106` |
| `typical_building_109` | **0** | `opaque_concrete_building_109_{a,n}` · `opaque_building_109_accessories_{a,n}` · … | ✅ **not previously flagged** — the same failure mode |

One genuinely dead upstream reference: `typical_building_18_inst.usd` points at
`shared_textures/concrete_01_albedo.png`, which returns 404 at the source `[measured]`. That is a
publisher-side gap, not a procurement error; the other 20 maps resolve.

**Material-slot finding, relevant to look.** `typical_building_10_inst.usd` wires only
`inputs:diffuse_texture` and `inputs:normalmap_texture` — **there is no ORM/roughness texture input
at all**, and the glass material has a normal map with no diffuse `[measured]`. Roughness and
metalness come from MDL constants, so the whole facade presents one specular response under noon
sun. R3's conclusion that an asset backdrop "must still be dressed" is reinforced: the flat
roughness is a second reason, independent of Korean-ness.

Also confirmed: reference the **`_inst.usd`** layer, not the wrapper. Opening
`typical_building_10.usd` composes to **504 triangles**; `typical_building_10_inst.usd` composes to
**21,965** `[measured]` — matching R1/R3 exactly. This is also why the verifier measures `_inst`.

---

## 4. Verification method

| Check | Instrument | Result |
|---|---|---|
| structural | first-8-byte magic per type (USD / PNG / JPEG / DDS / MDL) | 0 failures / 1,160 files |
| loads | `Usd.Stage.Open` + traversal **including instance proxies** | 276 / 276 geometry assets yield meshes; only the 6 material libraries are empty (by design) |
| geometry | Σ(faceVertexCount − 2); PointInstancer protoIndices expanded; world bbox over default+render+proxy | recorded per asset |
| units / Z | `UsdGeomGetStageMetersPerUnit`; **fraction of triangles below grade** | §5 |
| season | HSV bands (saturation > 0.15), sRGB→linear Rec.709 — *identical definitions to `veg_manifest_w2.json`* | §6.1 |
| near-white | fraction of pixels with linear luminance > 0.8, cap 5 %, colour maps only | §6.2 |
| sign faces | resolution + tone count + glyph fraction; plus a 158-plate contact sheet read by eye | §6.3 |

**Instance-proxy traversal is load-bearing.** `stage.Traverse()` alone reports `bench_park_01` as
**0 triangles**; with `Usd.TraverseInstanceProxies` it reports **35,396**, and `_inst.usd`
measurements are unchanged (21,965 = 21,965), so there is no double-counting `[measured]`.

Four gate definitions were **corrected against the population** rather than assumed — each
correction is recorded in the code with the measurement that forced it:

1. `min(px) ≥ 512` rejected `sign_krroadname` (2048 × 463, a long thin road-name plate). → judge the
   **long** side.
2. `n_tone ≥ 3` rejected two-tone regulatory plates that are obviously legible (`kr408`: ink 0.29,
   edge 4.70). → `n_tone ≥ 2`.
3. `ink_frac` alone rejected **13 blue 지시표지 with white arrows** — they have no *dark* ink at all.
   → `glyph_frac`, the fraction of pixels far from the modal luminance, which catches light glyphs
   on dark fields as well as the reverse.
4. Near-white fired on `brick_wall_001_Roughness.png`; the season gate silently skipped every
   `.dds` (i.e. **every** `props_vegetation` leaf atlas). → an explicit non-colour-map list, and
   `.dds` added to the texture extensions.

---

## 5. Quirks ledger — what a W3 integrator must know

### 5.1 Z origin — do not lift buildings from `zmin`

| Asset | bbox `zmin` | tris below grade | advice |
|---|---:|---:|---|
| `typical_building_{03,07,08,10,11,12,13,18,106,109}` (all 10) | −1.080 … **−10.340 m** | **0.0 %** | **local z = 0 is street grade. Do not apply a Z lift.** The negative extent is a foundation/basement box whose *upper* face is at or above grade. |
| `typical_building_08_railings` | **+11.000 m** | — | attachment — sits on its parent building, never grounded alone |
| `bldgs_01_distant/Building_*` (all 8) | 0.000 | 0 % | no correction |
| `sign_kr*` (156) | 0.000 | 0 % | no correction; panel normal is +X |
| 28 props (`utility_cover_01` −0.327, `bollard_01` −0.183, `luminaire_head04` −0.462, `streetlamp_01` −0.385, hedges −0.048…−0.122, …) | −0.015 … −0.462 | 0 % | genuine origin-below-base — lift by `−zmin`. Full list in the manifest's `z_advice` field. |

R1 §6.5 prescribed "translate +7.904 in Z" for `typical_building_10`. RT refuted that row; this
round shows the error is **systematic across the tier** — the same lift would have been applied to
nine more buildings, up to +10.34 m.

### 5.2 Units

`metersPerUnit = 0.01` on exactly one group: **the 8 far-tier `bldgs_01_distant/Building_*`**.
Everything else measured — all 10 mid-tier buildings, all 156 signs, all street furniture, and
**all 33 Poly Haven models** — is `1.0` `[measured]`. R2 §5.2's warning "do not assume 0.01" for
Poly Haven is settled in the safe direction: Poly Haven USD is uniformly 1.0, but read it anyway.

### 5.3 Aliases — three assets are other assets

| Bought | Actually is | Triangles |
|---|---|---:|
| `bench_park_01` | `../bench_park_03` | 35,396 (identical) |
| `bench_park_05` | **`../bench_curved_01`** | 608 |
| `concrete_block_02` | `../concrete_block_01` | 256 |

`bench_curved_01` is on R2 §5.3's "explicitly not procured" list. It arrives anyway if you procure
`bench_park_05`. Recorded as `alias_of` in the manifest. This is also the mechanism behind R1
§6.4(c)'s cross-folder-sublayer warning — mirroring `nv_content/` verbatim is what keeps it working.

### 5.4 Dead references are normal

240 dead references across the manifest, **all** of the form
`<asset>/materials/textures/<name>.png` — the inner `_inst_base` layer's texture paths, which never
exist and are overridden by the outer `_inst` layer `[measured]`. R1 §6.4(a) predicted exactly this.
They are recorded per asset as `dead_refs` so a future reader does not mistake them for breakage.
The one exception is `concrete_01_albedo.png` (§3), which is genuinely missing upstream.

### 5.5 Triangle counts that differ from the survey

| Asset | Survey figure | Measured | Note |
|---|---:|---:|---|
| PH `modular_urban_apartments_facade` | 118,215 (Poly Haven API) | **877,365** | 147 meshes, no instancing, single `default` purpose `[measured]`. **7.4×**. At this cost the CC0 backdrop is 40× `typical_building_10` (21,965). |
| PH `stone_01` | 71,916 | 53,520 | and it is only **147 × 89 × 72 mm** — a pebble, not a boulder |
| PH `concrete_road_barrier_02` | 42,578 | 23,822 | |
| the other 30 Poly Haven assets | — | **exact match** | API polycount is reliable in general, but not universally |

---

## 6. Pixel verification against project law

### 6.1 Season rule — no blossom, no autumn on anything with leaves

Judged on the **atlas actually bound to the mesh**, with the binding's triangle share attached.

| Asset | Bound albedo atlas | Mesh share | green | yg | orange | red | pink | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `veg_shrub_hedge_green_01` | `opaque__leaf__hedge_green_a.dds` | **97.8 %** | 0.952 | 0.047 | 0.001 | 0.001 | 0 | **PASS** |
| `veg_shrub_hedge_yellow_01` | `opaque__leaf__hedge_green_a.dds` | **89.4 %** | 0.941 | 0.058 | 0.001 | 0.001 | 0 | **PASS** — the name is not a season flag |
| `veg_shrub_hedge_round_01` | `opaque__plant__hedge_round_a.dds` | **74.6 %** | 0.000 | 0.494 | 0.467 | 0.039 | 0 | **FAIL** (green+yg 0.494 < 0.75) |
| ” | `opaque__plant__fruit_01_a.dds` | 1.3 % | 0.563 | 0.196 | 0.078 | 0.149 | 0.014 | **FAIL** (warm 0.241 > 0.06) — berries |
| ” | `opaque__leaf__hedge_round_a.dds` | 24.2 % | 0.995 | 0.005 | 0 | 0 | 0 | (the green quarter) |
| `veg_grass_clump_*` (7) | `veg_cover_grass_clump_01_a.dds`, `tile_cover_grass_01_a.dds` | 100 % | 0.58–0.66 | 0.25–0.30 | 0.09–0.12 | 0.000 | 0 | **PASS** (turf gate) |
| `sct_debris_leaves_dry_01..04` | `debris_leaves_BaseColor.png` | 100 % | 0.000 | 0.002 | 0.343 | 0.655 | 0 | **SEASON-SCOPED** — leaf scenes only (C2 · 07 · 10 · D3); banned elsewhere |

**Action for W3**: `veg_shrub_hedge_round_01` must not be wired as an evergreen Korean 생울타리.
Use `veg_shrub_hedge_green_01` (97.8 % green) or `_yellow_01` (89.4 % green). RT-4's requirement is
discharged, with the opposite outcome to the one its naming heuristic predicted.

No Poly Haven plant was procured, consistent with R2 §2.4 (none clears both the season gate and
Korean-ness). `tree_stump_01/02` are exempt from the foliage gate — a stump is brown year-round and
the gate is a leaf-colour instrument, so applying it there is a category error.

### 6.2 Near-white on large surfaces (cap: 5 % of pixels above linear luminance 0.8)

37 large-surface colour maps checked; **3 over cap** `[measured]`:

| Texture | px | albedo (lin) | lin > 0.8 | sRGB > 0.8 | Used by |
|---|---|---:|---:|---:|---|
| `house_wall_001_Diffuse.png` | 1024² | **0.874** | **99.55 %** | 100.00 % | **all 8 far-tier `Building_*`** |
| `concrete_014_Diffuse.png` | 1024² | **0.969** | **98.73 %** | 99.91 % | far tier |
| `T_opaque__concrete__rivermarkEntranceSign_Albedo.png` | 1024² | 0.294 | 15.40 % | 15.58 % | `bench_park_05` |

Everything else is comfortably clear — the mid-tier buildings are the good news:
`typical_building_08_a.png` 3.08 %, `_12_shops_a.png` 2.48 %, `_13_a.png` 0.07 %, and
`plaster_white_01_a.png` — despite its name — **0.00 %** at albedo 0.365.

**The far tier is the problem.** These are the skyline replacements for scenes 03·09·12·17 and the
N-series, at 30–130 m across, and their wall albedo is 0.874–0.969 against a project cap of 0.8.
W2 spent a whole fix batch removing near-white surfaces; loading these untinted would reintroduce
the defect at the largest scale in the frame. They need an albedo multiplier or a material
override before use. The verifier already flags all eight.

### 6.3 Sign faces — 158 plates, all legible

| Metric | Median | Min |
|---|---:|---:|
| resolution (long side) | 2048 px | 1024 px |
| contrast (p95 − p05, sRGB luma) | 232 | 47 |
| glyph fraction | 0.3167 | 0.0240 |

**FAIL 0.** Two WARN, both the same plate: `sign_kr224_110` and its `_emissive` companion are a
**variable-message speed sign** whose diffuse map is near-black by design (contrast 56 / 47) —
the numerals live in the emissive channel. They are legible only if the emissive material is bound;
flagged rather than failed.

The 158-plate contact sheet (`assets/urban/_verify/sign_contact_sheet.png`, untracked) was read by
eye: every plate carries a real Korean regulatory face with genuine Hangul —
진입금지 · 정지 STOP · 양보 YIELD · 횡단보도 · 어린이보호구역 SCHOOL ZONE · 노인보호 · 장애인보호 ·
자전거전용 · 주차 P · 속도를 줄이시오 · 생활도로구역, plus route boards and school-zone assemblies.
Nothing blank, nothing placeholder. The whole shortlist R1 §5.3 specified (18 names) exists and
renders correctly.

Carried forward unchanged: `sign_kr101` measures **0.844 m** against the 900 mm 주의표지 standard —
re-measured this session at 0.002 × 0.8444 × 0.7414 m, 104 tris, mpu 1.0, zmin 0 `[measured]`.
Held at the 연대-3요소 gate; **no uniform rescale**, because the 2xx/3xx families have different
standard sizes.

---

## 7. Re-opened prop rows

R2's verdicts were rejected on **Korean-ness**, which is licence-independent, so those stand. But
two rows recorded **licence** as the only barrier to the asset route, and three more were swept up
by a blanket sentence in R2 §5.3 without the DriveSim asset ever being dimensioned. All are now
measured, so the W3 spec can judge on numbers instead of on a catalogue claim.

### 7.1 Tier 1 — licence was the *only* stated barrier

**C6 · Bollards.** R2: *"No CC0 bollard exists (521-model index enumerated); Rivermark's is Limited
Use. Procedural is the only path."* The Limited Use clause does not reach the general root, so the
route re-opens. Measured against 교통약자법 시행규칙 별표2 제7호 (h 0.8–1.0 m, Ø 0.1–0.2 m) `[law]`:

| Asset | Ø × h (mm) | tris | Verdict against the statute |
|---|---|---:|---|
| **`bollard_01`** | **139 × 1003** | 2,564 | **both in spec** |
| **`strt_fxd_bollard_05`** | **133 × 845** | 2,628 | **both in spec** |
| `strt_fxd_bollard_03` | 207 × 297 × 721 | 5,984 | h below minimum, non-circular |
| `strt_fxd_bollard_01` | 269 × 262 × 1293 | 3,574 | over on both |
| *repo* `scene_common.build_bollard` | 120 × **750** | 3 prims | **6.3 % below the legal minimum** (R2 §C6) |

Two catalogue bollards are dimensionally legal for Korea; the repo's own builder is not. That does
not settle the row — R2's form objections (dome cap, base plate, anchor cover, impact-absorbing
material, and the deliberate 75 % non-compliance jitter drawn from 한국시각장애인연합회 2023) are
about *features*, not size, and a US DriveSim bollard has none of them. But "procedural is the only
path" is no longer true, and an A/B is now cheap. `bollard_02` remains **declined** (Mathworks).

**C2 · Streetlight, luminaire-head-only borrow.** R2 §2.2 named this as the one option its own
licence correction re-opened. The heads exist, and they are cheap:

| Asset | mm | tris |
|---|---|---:|
| `luminaire_head03` | 1009 × 216 × 98 | **256** |
| `luminaire_head04` | 469 × 471 × 495 | **639** |
| `luminaire_head02` | 728 × 303 × 240 | **532** |
| `luminaire_head_01` / `head01` | 700 × 346 × 148 / 206 | 3,844 / 4,184 |
| `luminaire_arm_{6,8,10}ft` | 1838 × 152 × 662 (6 ft) | 858 |

These are real cobra-head luminaire bodies — precisely the *"luminaire body, not a flat plate"*
that R2's C2 spec demands — at 256–4,184 triangles, mountable on our own tapered Korean pole.
**This is the highest-value re-opened row in the map.** Whole-lamp alternatives are weaker:
`streetlamp_01` is 3.29 m (below the 4.5 m pedestrian minimum, the same failure as PH
`street_lamp_01` at 3.87 m), `streetlamp_03` is 7.07 m and arterial-scale; only `streetlamp_02`
(6.22 m, 4,634 tris) lands near the band, at its top edge.

### 7.2 Tier 2 — Korean-ness asserted, but the DriveSim asset was never dimensioned

| Row | Asset | Measured (mm) | Korean referent | Gap |
|---|---|---|---|---|
| C1 bench | `bench_park_03` (= `_01`) | 1735 × 1149 × 1325 | 등벤치 1600 × 540 × 700 `[stat]` | depth **2.13×**, height **1.89×** |
| C1 bench | `bench_park_02` | 2589 × 1198 × 1347 | ” | length 1.62×, depth 2.22× |
| C1 bench | `bench_park_05` (= `bench_curved_01`) | 4091 × 2170 × 442 | ” | a 4 m curved cluster, not a bench |
| C3 bin | `trashcan_cylinder_01` | Ø722 × 1041 | 가로 휴지통 Ø450–560, 2-gang | Ø **1.29–1.60×**, not 2-gang |
| C3 bin | `trashcan_square_01` | 586 × 796 × 1011 | ” | over on both |
| C5 planter | `planter_lrg_01` | 1500 × 1500 × 700 | KS F 4006 화단경계석 150 × 150 × 1000 `[law]` | different type (freestanding vs kerb bed) — **but not the "farmhouse timber crate" that sank the CC0 option** |
| C5 planter | `planter_round_01` | Ø1002 × 988 | ” | ditto |

**R2's rejections survive contact with the measurements** for benches and bins — the numbers are
worse than the catalogue implied, not better. The planters are the one place where the DriveSim
option is materially different from the CC0 option R2 rejected, and worth a look.

### 7.3 Rocks — the 0.31–1.10 m gap (`asset_audit_v1` §2, carried in R2 §A2)

Existing `Vegetation/Rocks/*` top out at **0.314 m**; scene12's riprap band runs 0.30–1.10 m.

| Candidate | Longest dim | tris | Fills the gap? |
|---|---:|---:|---|
| `rock_02` | **0.463 m** | 4,758 | ✅ lower half |
| `rock_01` | 0.316 m | 3,104 | no — at the existing ceiling |
| `rock_03_broken` | 1.714 m | 9,832 | above the band; usable as a boulder |
| PH `stone_01` | 0.147 m | 53,520 | **no** — a pebble, and 53 k tris for it |
| PH `rock_moss_set_01/02` | 8.0 / 8.3 m | 63,127 / 57,647 | multi-rock *sets*; individual stones would have to be extracted |

**The 0.5–1.1 m single-boulder band is still unfilled.** Honest residual.

---

## 8. Korean-ness rejections that stand (with the failed dimension)

Re-measured from the local USD this session, so the W3 spec can re-judge from numbers rather than
from a catalogue field. **Every dimension in R2 §2.3 reproduces exactly** against the downloaded
USD; the polycounts mostly do too, with the three exceptions in §5.5 (including
`concrete_road_barrier_02`, 23,822 measured vs 42,578 in R1 §3.3).

| Candidate | Measured (mm) | tris | Korean referent | Failed dimension |
|---|---|---:|---|---|
| PH `painted_wooden_bench` | 1165 × 496 × 889 | 630 | 등벤치 1600 × 540 × 700 | length **−27 %**, height **+27 %** |
| PH `modular_street_seating` *(not procured)* | 4340 × 770 × 950 | 25,156 | ” | length **2.71×** |
| PH `street_lamp_01` *(not procured)* | 704 × 386 × 3871 | 30,610 | 등주 4500–6000 | height **−14 %** below minimum |
| PH `metal_trash_can` | 1847 × 556 × 906 | 13,960 | 가로 휴지통 Ø450–560 2-gang | width **3.30×** → alley/yard dressing only, never a plaza |
| PH `planter_box_01..03` *(not procured)* | 913 × 414 × 425 | 8,094 | KS F 4006 150 × 150 × 1000 masonry | form: farmhouse timber crate |
| PH `modular_electricity_poles` *(not procured)* | 13119 × 1957 × 7000 | 200,610 | KS F 4304 PC pole 10–16 m | height **−30 %** |
| PH `water_manhole_cover` *(not procured)* | Ø691 × 68 | 6,301 | KS D 4040 Ø648 / 766 / 918 | falls between standard sizes; no Hangul lettering |
| PH `modular_chainlink_fence` | 8115 × 2149 × 2523 | 89,232 | 가설울타리 steel panel | form → yard boundary only (D1 · D2) |
| PH `concrete_road_barrier_02` | 1565 × 442 × 1112 | 23,822 | 방호벽 1000/2000 × h800–1000 | allowed, P3 |
| **PH `korean_fire_extinguisher_01`** | 280 × 367 × 659 | 9,913 | 국내 소화기 | **accepted** — an explicitly Korean scanned product |

### 8.1 A new Korean-ness failure, found by measuring

**`ac_unit_04/05/06` are not Korean facade air-conditioners.** R1 §5.2 listed them as the "Korean
facade signature" at 4.83 MB. Measured, `ac_unit_04` is **3604 × 4203 × 1984 mm** — a rooftop
chiller package, roughly 4 × 4 m `[measured]`. A Korean wall-mounted 실외기 is ≈ 800 × 300 × 600 mm.
PH `exterior_aircon_unit` (1800 × 374 × 928) is closer but still about twice the wall unit.
The facade-AC row needs either a different asset or a procedural unit; the assets are still useful
as **rooftop plant** on the mid-tier buildings.

`utility_cover_01` is likewise misnamed for our purpose: **1499 × 954 × 355 mm**, i.e. a utility
vault, not a Ø648–918 KS D 4040 manhole cover. W2's procedural manhole (fix batch F5) stands;
R2 §A3's "keep" verdict is confirmed by measurement rather than by inference.

---

## 9. Open items for the supervisor

1. **rivermark-named shared textures** (§2.1) — three assets pull them transitively from the
   general Content root. Not a licence breach by path; the decline was by name. Keep (recommended:
   the alternative is silently broken materials) or drop the three assets?
2. **Far-tier near-white** (§6.2) — the eight `Building_*` need an albedo override before they can
   ship. This is an implementation decision (material override vs. decline the tier vs. tint at
   load), and it interacts with RT's finding that an asset backdrop moves the judged ground band's
   σ_LF by up to −0.32.

Not blocking, but worth recording: `bench_park_05` re-imports `bench_curved_01`, which R2 listed as
not-procured (§5.3). If that list is meant to be binding, `bench_park_05` should be dropped.

---

## 10. Deliberately not procured, and why

| Item | Cost | Reason |
|---|---:|---|
| `apt_complex_assembly` | 672 MB | R1's own recommendation: probe/A-B before committing. Nothing this round justifies it. |
| `sct_leaf_pile_04/05` | 352 MB | `sct_debris_leaves_dry_01..04` covers the need at **5.3 MB** |
| `lightpost_5m_steel_a_*` group | 480 MB | `luminaire_head*` (§7.1) is the same function at 0.3–4 MB |
| `rivermark_plaza_bldg_*` (9 dirs, incl. `06a`) | — | supervisor decline; guard-enforced |
| ambientCG decals / facades / LeafSet / AsphaltDamage | — | CC0 and genuinely useful (Facade 26 · Sign 26 · Leaking 39 · RoadLines 69 · LeafSet 30 · SurfaceImperfections 20), but **outside this brief's named scope**. A separate `--only` group would be a ~15-line addition. |
| SimReady props (`metalfencing_a*`, `deluxesafetytape_*`, `heavydutytrafficcone_a*`, `dockboard_a*`) | — | `asset_info.json` already publishes their extents, which is what they were wanted for; the geometry can wait for a row that needs it |
| `wall_resd_0{1,2}_set_*` (scene 13 apartment boundary) | 85 MB | not in the brief's named set; a 3-line `GROUPS` addition if W3 wants it |
| all 16 CC0 plant scans | — | R2 §2.4 — none clears both the season gate and Korean-ness |

---

## 11. What was not verified (scope honesty)

- **No render.** Every pixel judgement is on the source texture, not on a rendered frame. The
  near-white and season numbers are necessary conditions, not sufficient ones.
- **DDS at the Isaac reader level.** PIL reads every `.dds` in `props_vegetation/` fine, which
  answers R1 §9-5 at the *file* level. Whether Isaac's MDL loader reads them is a GPU question and
  is untested here.
- **Texture bindings for Poly Haven assets** were not traced per mesh — `texture_bindings` is
  populated where the USD carries `MaterialBindingAPI`; PH assets bind through their own shading
  graph and report fewer bindings.
- **`tri_below_grade_frac`** counts mesh triangles only; PointInstancer prototypes are excluded from
  that one statistic (they are included in `tri_effective`).
- **The 900 mm 주의표지 standard** itself is still `[assumed]` — only the asset's 844 mm is measured.
- **No A/B render** of `veg_shrub_hedge_green_01` against `build_hedge`, of the DriveSim bollards
  against `build_bollard`, or of the luminaire heads against the procedural streetlight. Those are
  W3 implementation work; this round only makes them possible.
