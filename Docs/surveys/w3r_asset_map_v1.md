# W3-R R1 — Full Asset-Catalog Map Beyond Vegetation (v1)

> **Wave**: W3-R (structural overhaul) · **Task**: R1 · **Date**: 2026-07-30
> **Branch**: `feat/realism-v1` · **Commits**: none (supervisor commits)
> **Files written**: this file only. No tracked scene file or shared module was touched.
> **Driver**: user verdict *"에셋 활용도 제대로 못한 느낌"* — W2 shipped with S3 `Assets/Vegetation/`
> only (trees, shrubs, debris, rocks). Everything else in the catalog was never opened.

## Evidence tags

| Tag | Meaning |
|---|---|
| `[measured]` | Counted / byte-sized / geometry-parsed in this session. Reproducible with the scripts in §1. |
| `[law]` | Quoted from a licence document fetched this session, or from ZZ §10.6 hard rules. |
| `[stat]` | Derived statistic over a measured population. |
| `[assumed]` | Inference not verified this session. Must be verified before it drives code. |

---

## 0. Executive summary

**The catalog is far larger than we thought, and the part we need most is the part we
never looked at.** `Assets/Vegetation/` (the only tree we have pulled from) is 6 folders.
The DriveSim library hiding under `Assets/Isaac/4.5/NVIDIA/dsready_content/` is
**175,822 keys / 116.7 GB** `[measured]` and contains purpose-built urban street furniture,
Korean regulatory signage, and — critically for W3 — **two tiers of ready-made backdrop
buildings**.

Five findings change W3 planning:

1. **Backdrop buildings exist, at two LODs, cheap.** `props_structures/` holds 27
   `typical_building_*` (mid tier) + 25 `bldgs_0{1,2}_distant/Building_*` (far tier) +
   `apt_complex_assembly` (Korean-reading apartment block). Measured: `typical_building_10`
   = **21,965 tris, 34.74 × 30.17 × 30.33 m**, total download **8.25 MB** including its
   shared textures; `Building_178` = **1,354 tris**, 0.43 MB `[measured]`. That is cheaper
   per building than our current procedural `build_building` window-prim explosion.
2. **A licence trap sits directly on the buildings.** The same 18,905 relative asset paths
   exist under **two** roots: `NVIDIA/dsready_content/…` (general Omniverse **Content**
   licence) and `Isaac/Environments/Outdoor/Rivermark/dsready_content/…` (**Limited Use
   Content**, *"without modifications"*) `[measured]` `[law]`. Same filenames, different
   bytes, different licence. All procurement must be pinned to the `NVIDIA/` root. §2.
3. **korea_mobiltech = 156 signs confirmed, but the poles do not exist.** The 156 count
   verifies exactly `[measured]`. The 13 `props_poles/` folders contain **only
   `mobiltech_manifest.csv` — zero USD geometry — in 4.5, 5.0, 5.1 and 6.0 alike**
   `[measured]`. Signs must be mounted on our own posts. §5.3, §7.
4. **Two units systems inside one library.** `typical_building_10` is `metersPerUnit = 1.0`;
   `bldgs_01_distant/Building_178` is **`metersPerUnit = 0.01`** `[measured]`. Z origins are
   also inconsistent (`typical_building_10` zmin = **−7.904 m**, `Building_178` zmin = 0.000).
   Any building loader needs per-asset unit + Z-base normalisation or scenes will silently
   break. §6.4.
5. **ambientCG 3D models are a dead end; its decals are not.** ambientCG has 34 assets of
   `dataType = 3DModel` and **all but two are food** (apples, bread, pastry) `[measured]`.
   But its `Facade` (26 Materials), `Sign` (26), `LeafSet` (30 Atlas), `Leaking` (39 Decal),
   `RoadLines` (69 Decal), `SurfaceImperfections` (20) categories map straight onto the
   renovation-vocabulary and backdrop workstreams, CC0 and redistributable. §3.4.

**Vegetation gap re-verified as still open**: `ginkgo`, `maidenhair`, `zelkova`, `keyaki`,
`chionanthus`, `lagerstroemia`, `metasequoia` → **0 hits across 275,368 S3 keys +
100,902 dsready file-list lines** `[measured]`. `CREDITS.md`'s ❌ verdicts stand.

**Recommended W3 procurement volume**: **483.20 MB / 760 files** for the lean four-workstream
shortlist (§5.5), versus **5.70 GB** if the same shortlist groups were taken wholesale
`[measured]`. The 11× saving comes from resolving textures per asset instead of pulling
`shared_textures/` (2.61 GB) whole, and from declining three fat outliers
(`apt_complex_assembly` 672 MB, `sct_leaf_pile_04/05` 352 MB, `lightpost_5m_steel_a_*` 480 MB).

---

## 1. Method and reproducibility

All listings were done anonymously over the public S3 REST API with continuation-token
paging (no credentials, no `boto3`).

| Script (scratchpad) | What it does |
|---|---|
| `s3ls.py <prefix> [--delim] [--out F]` | Paged `list-type=2` walk → TSV `KEY/DIR<TAB>key<TAB>size` |
| `dsq.py <prefix>` | Canonical-asset filter over the dsready file list (drops `_base`/`_inst`/`_inst_base`/`_tagged` wrapper variants) |
| `sizes.py <prefix>` / `shortlist.py` | Per-asset-folder byte roll-up from the recursive listing |
| `probe_w3r.py` | Bounded probe download (15 keys, 2.44 MB total) |
| `deps.py` | `pxr`-based asset-path dependency resolution + tri/bbox/units measurement |

**Populations measured**

| Population | Size |
|---|---|
| `Assets/Isaac/4.5/` recursive | **275,368 keys, 302.49 GB** `[measured]` |
| ├─ `NVIDIA/dsready_content/` | 175,822 keys, 116.66 GB |
| ├─ `Isaac/Environments/` (**Limited Use**) | 27,114 keys, 18.17 GB |
| ├─ `NVIDIA/Assets/` | 28,448 keys |
| └─ `NVIDIA/Materials/` | 21,962 keys |
| `dsready_content/file_list.txt` (published index) | 100,902 lines → 92,518 non-thumb → **26,828 USD** `[measured]` |
| `Assets/simready_content/asset_info.json` | **1,029 props**, machine-readable (Extent, Tags, Labels, QCode) `[measured]` |
| Poly Haven `api/assets?t=models` | **521 models**, all CC0 `[measured]` |
| ambientCG `api/v2/full_json` (full) | **2,875 assets**; Material 2005 · HDRI 418 · Substance 209 · Decal 126 · Atlas 60 · **3DModel 34** · PlainTexture 9 · Brush 5 · Terrain 5 `[measured]` |

**Caveat on the published index.** `file_list.txt` lists 100,902 files but the live bucket
returns 175,822 keys under the same root `[measured]`. The index is a subset/older snapshot.
**Treat the live listing as authoritative**; use `file_list.txt` only as a fast search cache.
Likewise `nv_content/manifest.csv` carries only 2,124 rows — it is a SimReady-tagged subset,
not a full inventory.

**Probe budget**: 15 keys, **2.44 MB** `[measured]`. Log in §8. No bulk download occurred.

---

## 2. Licence tier map — read before any download

### 2.1 The dual-root trap (new finding, blocking)

```
Assets/Isaac/4.5/NVIDIA/dsready_content/nv_content/common_assets/props_general/bollard_01/bollard_01.usd   53,841 B
Assets/Isaac/4.5/Isaac/Environments/Outdoor/Rivermark/dsready_content/nv_content/…/bollard_01.usd          43,658 B
```

Identical relative path, **different bytes, different licence** `[measured]`.

| Root | Keys | Size | Licence tier |
|---|---|---|---|
| `Assets/Isaac/4.5/NVIDIA/dsready_content/` | 175,822 | 116.66 GB | Omniverse **Content** (same tier as `Assets/Vegetation/`) |
| `Assets/Isaac/4.5/Isaac/Environments/` | 27,114 | 18.17 GB | **Limited Use Content** |
| └─ `…/Environments/Outdoor/Rivermark/dsready_content/` | 19,600 | 11.63 GB | **Limited Use Content** (a mirror of the library above) |
| Overlapping relative paths between the two roots | **18,905** | — | ⚠️ ambiguity surface |

`environment-supplement-LICENSE.txt` (fetched 2026-07-30, v. November 18, 2021) `[law]`:

> The terms in this supplement govern your use of certain NVIDIA Omniverse USD assets in
> the **/Isaac/Environments** ("Limited Use Content"). […] NVIDIA grants you a
> non-exclusive, non-transferable, non-sublicensable license to install and use copies of
> the Limited Use Content for your use only, **without modifications** […]
> 2. The license grant for Content as described in the Agreement **does not apply to
> Limited Use Content**.

Consequences, stated plainly:

- **"without modifications" makes the entire `/Isaac/Environments` tree unusable for us.**
  Our pipeline scales, re-materials, and re-parents everything it loads. That is
  modification. This is not only about `Rivermark` — it covers `Simple_Warehouse`,
  `Hospital`, `Office`, and (surprisingly) `Environments/Terrains/{flat_plane,slope,stairs,
  rough_plane}.usd` `[measured]`.
- **`props_structures/rivermark_plaza_bldg_01..08` under the `NVIDIA/` root is a separate
  question.** The supplement is scoped by *path* (`/Isaac/Environments`), and these live at
  `NVIDIA/dsready_content/nv_content/common_assets/props_structures/`, outside that scope.
  Textually they are Content, not Limited Use. **But the name is the name of the Limited Use
  environment.** → Recommendation: **do not procure `rivermark_plaza_bldg_*`**. There are 27
  `typical_building_*` with no such ambiguity. Cost of avoidance: zero.
- **Hard rule for the downloader**: the base URL constant must include `NVIDIA/dsready_content/`
  and the manifest must reject any key containing `Environments/`. §6.2.

### 2.2 Tier table for every catalog touched

| Source | Path / API | Licence | ML training | Render publish | USD redistribution | Verdict |
|---|---|---|---|---|---|---|
| NVIDIA S3 — `Assets/Vegetation/` | `…/Assets/Vegetation/` | Omniverse Content | ✅ | ✅ | ❌ | **in use** (W2) |
| NVIDIA S3 — `NVIDIA/dsready_content/` | see §3.1 | Omniverse Content | ✅ | ✅ | ❌ | **USE** (gitignore) |
| NVIDIA S3 — `Assets/simready_content/` | `Assets/simready_content/` | Omniverse Content (no supplement present in the prefix `[measured]`) | ✅ | ✅ | ❌ | **USE** (gitignore) |
| NVIDIA S3 — `Assets/ArchVis/` | `Assets/ArchVis/{Industrial,Residential,Commercial}/` | Omniverse Content | ✅ | ✅ | ❌ | **USE** (gitignore) |
| NVIDIA S3 — `Isaac/Environments/**` | incl. `Outdoor/Rivermark`, `Terrains`, and the 19,600-key dsready mirror | **Limited Use** | — | — | ❌ | **BANNED — "without modifications"** |
| NVIDIA S3 — `Assets/Characters/Reallusion/`, `Isaac/People/` | 3,164 keys under `Isaac/People/` | Content, but **people deferred by project discipline** | — | — | ❌ | **DEFER** (STATUS: 사람·차량 보류) |
| Poly Haven models | `api.polyhaven.com/assets?t=models` (521) | **CC0 1.0** | ✅ | ✅ | **✅ redistributable** | **USE — preferred where it competes** |
| ambientCG | `ambientcg.com/api/v2` (2,875) | **CC0 1.0** | ✅ | ✅ | **✅** | **USE (materials/decals; 3D is food)** |
| Megascans / Quixel | — | NoAI clause | ❌ | ❌ | ❌ | **BANNED** (ZZ §10.6) |
| Mixamo / RenderPeople | — | — | ❌ | ❌ | ❌ | **BANNED** (ZZ §10.6) |
| Brand vehicles | `vehicles/{ford,volvo,piaggio,hero}/` | brand-identified | — | — | — | **BANNED**; `honey`/`tri`/`generic` are fictional → OK |

### 2.3 Third-party provenance inside the NVIDIA library (new, needs a supervisor call)

`nv_content/manifest.csv` (2,124 rows) carries a `_Supplier` column `[measured]`:

| Supplier | Rows | Note |
|---|---|---|
| NVIDIA | 1,956 | in-house |
| Agility3 | 83 | the entire `constr_mov_*` construction set |
| BDesign | 50 | `fence_mod_a/b/c`, `gantry_01`, lamps |
| SimAction | 22 | dumpsters, cans, bookcase |
| Mathworks_Modified | 7 | **`safety_railing_01`**, `double_crossarm_*`, `bollard_02` |
| Kraken / **CGTrader** / **Hum3D** / SpeedTree / Ford / Mobiltech | 1 each | `bike_01` / … / `license_plates` / … |

NVIDIA redistributes these under its own agreement, so our grant comes from NVIDIA, not the
supplier. `[assumed]` — the supplier column is provenance metadata, not a licence grant, and
nothing in the fetched documents contradicts our existing "no ML-restriction clause"
verdict. But `CGTrader` and `Hum3D` are marketplaces whose *own* storefront terms often carry
AI restrictions. **Recommendation**: prefer NVIDIA-supplied assets in the shortlist where a
choice exists, and record `_Supplier` in the procurement manifest so a later audit can filter.
`safety_railing_01` (Mathworks_Modified) is on our shortlist — flagged in §5.2.

### 2.4 Reconciliation with W3-R2 §2.2 — the street-furniture route is **open**, not closed

The sibling package `Docs/surveys/w3r_prop_mapping_v1.md` §2.2 concludes:

> The Rivermark row is the load-bearing one: it is exactly the library that contains a bollard,
> a safety railing, a bench, two trashcans, a bike rack and forty streetlamps — and its
> supplement forbids modification […] the street-furniture asset route is closed and
> **procedural rebuild is the only compliant path** for C1–C7.

That conclusion attributes those assets to `Assets/Isaac/**/Environments/**` (Limited Use).
**Every one of them also exists outside `/Isaac/Environments`, at the general-Content
`NVIDIA/dsready_content/` root, and the two copies are different files** `[measured]`:

| Asset (`common_assets/props_general/…`) | `NVIDIA/dsready_content/` | `Environments/Outdoor/Rivermark/…` |
|---|---|---|
| `bollard_01.usd` | 53,841 B | 43,658 B |
| `bench_curved_01.usd` | 73,849 B | 57,159 B |
| `safety_railing_01.usd` | 84,690 B | 75,229 B |
| `trashcan_cylinder_01.usd` | 49,221 B | 39,040 B |
| `bike_rack_01.usd` | 64,193 B | 52,294 B |
| `planter_round_02.usd` | 51,043 B | 40,757 B |
| `streetlamp_01.usd` | 63,781 B | **absent** |
| `props_poles/**.usd` (count) | **1,454** | 1,018 |
| `props_general/**.usd` (count) | **2,571** | 110 |

The Limited Use supplement is scoped by path — *"certain NVIDIA Omniverse USD assets in the
**/Isaac/Environments**"* `[law]`. `Assets/Isaac/4.5/NVIDIA/dsready_content/` is not in that
path. So the supplement does not reach it, and these assets sit in the same Content tier we
already accepted for the 30 in-repo vegetation USDs: **ML training ✅, render publish ✅, USD
redistribution ❌**.

**Consequence**: the licence argument for "procedural rebuild is the only compliant path" does
not hold. Roughly 20 `rebuild-procedural` verdicts in the W3-R2 map are eligible for
re-adjudication on the asset route. → **Supervisor decision required** (§9.7); I am not
changing another package's verdicts.

**What survives untouched from W3-R2**: its §2.3 Korean-ness test rejects
`modular_street_seating`, `street_lamp_01/02`, `planter_box_01..03`, `modular_electricity_poles`
and `water_manhole_cover` on **form and dimension** grounds against Korean referents, not on
licence. Those rejections are independent of the finding above and I defer to them — my §3.3
and §5.2 list those items as *catalogued and available*, which is not the same as *approved*.
Read the two documents together: §3.3/§5.2 = availability + cost; W3-R2 §2.3 = Korean-ness gate.

### 2.5 CC-BY credit ledger

No CC-BY asset entered the shortlist this round. Poly Haven and ambientCG are both CC0, so
the per-author ledger required by ZZ §10.6 is **not triggered by R1**. Poly Haven authors are
still recorded in §5 for the reproducibility record (courtesy, not obligation) — matching how
`CREDITS.md` already treats HDRIs.

---

## 3. Catalog census

### 3.1 `NVIDIA/dsready_content/nv_content/` — the DriveSim library

Canonical assets (wrapper variants `_base`/`_inst`/`_inst_base`/`_tagged` removed) `[measured]`:

| Category | Canonical USD | What is actually in it |
|---|---|---|
| `common_assets/props_general/` | **645** | street furniture, construction set, utility boxes, debris, AC units, planters, benches, bollards, bike racks, dumpsters, sound barriers (~60 wall/column pieces), fences, lamps, manhole covers |
| `common_assets/props_poles/` | **368** | lamp posts, luminaire arms/heads, signal poles, utility poles, crossarms, advertisement boards, pedestrian signal poles |
| `common_assets/props_structures/` | **103** | 27 `typical_building_*`, 25 `bldgs_0{1,2}_distant/Building_*`, 8 `rivermark_plaza_bldg_*` (⚠️§2.1), `apt_complex_assembly`, `bldg_cml_warehouse_lrg_01..03`, `bldg_electricity_01/02`, `bldg_gen_103..108`, `bldg_modern_library`, `bus_stop_01`, `toll_booth_01`, `wall_resd_0{1,2}_set_{wall,fence,pillar,planter_*}` |
| `common_assets/props_traffic/` | **333** | traffic cones 18/28/36 in × clean/dirt/dam, Type-III barricades 4–12 ft, water-filled barriers, jersey barriers, delineators, sawhorse barriers, guardrails, speed bumps/cushions, wheel stops (~40), road studs, traffic cameras |
| `common_assets/props_vegetation/` | **225** | `veg_tree_*` (~60 species incl. `cherry_japanese`, `sycamore`, `juniper_chinese`, `pine_yellow`), `veg_shrub_hedge_{green,round,yellow}_01`, `veg_grass_clump_*` (14 + med/low variants), `sct_debris_leaves_dry_01..04`, `sct_debris_branch_fallen_01..04` |
| `common_assets/vehicles/` | **448** | `honey` (20 dirs / 191), `tri` (9 / 136), `generic` (2 / 16) — fictional ✅; `ford` 149, `hero` 28, `volvo` 12, `piaggio` 22 — **brands, banned** |
| `common_assets/props_signage/` | 43 | billboards, shop signage |
| `common_assets/traffic_lights/` | 29 | signal heads/housings |
| `common_assets/animals/` | 39 | out of scope |
| `common_assets/shared_textures/` | 1,410 files / **2,609 MB** | texture pool the building assets resolve into (§6.4) |
| `korea/country_assets/` | 8 signs + 2 roadmarks + traffic-light housings + a `scene_uodd_speed_schoolzone` scene | second, smaller Korean pack |
| `korea_mobiltech/country_assets/` | **156 signs** + 158 textures + 9 KR roadmark stencils; **13 pole folders with no geometry** | §5.3 |
| `nv_core/materials/` | 11,112 files / 2,182 GB-scale pool | `SimPBR.mdl` (0.14 MB, 9 files) and `materials/signs/` (16 files, **2.15 MB**) are the only parts our shortlist needs |

### 3.2 `Assets/simready_content/` — 1,029 SimReady props with a machine-readable index

`asset_info.json` (802 KB) gives `Extent` (metres), `Tags`, `Labels{QCode,Class,Hierarchy}`
per asset `[measured]`. **This is the only NVIDIA catalog with published dimensions** — use it
as the metrology source when a class exists in both libraries.

Classes relevant to us `[measured]`:

| Class | n | Measured extents (m) |
|---|---|---|
| traffic cone | 19 | 0.34³→0.46 h, 0.38→0.71 h, 0.50→**0.91 h** (`heavydutytrafficcone_a01..a06`, `coloredtrafficcone_a01`) |
| barricade tape | 59 | spans **2 / 4 / 6 / 8 / 10 / 12 m** × 0.05 or 0.10 m width (`deluxesafetytape_a/b*`) |
| railing | 6 | `metalfencing_a1` 0.23×0.23×**1.07**, `a2` 0.23×1.23×1.07, `a3` 0.44×1.01×1.07, `cornerrail_a1`, `ramplong_a1` 0.35×2.24×0.50, `rampshort_a1` |
| flower box | 3 | `gardenplanter_{small,medium,large}` 0.30³ / 0.36³ / 0.44×0.44×0.48 |
| bench | 2 | `waitingbench` 0.66×1.77×0.84, `willowbench` 0.46×1.40×0.44 |
| inclined plane | 22 | `dockboard_a01..a08+` 0.91–1.83 × 1.37–1.83 × 0.20–0.36 |
| ladder | 4 | `tiltandrollladder_a01..a04` up to 1.11×0.70×2.06 |
| drum / pail / bucket | 21 / 13 / 3 | 0.31–0.63 dia |
| shelf / container / cardboard box / crate / pallet | 250 / 193 / 106 / 101 / 68 | warehouse-only, out of scope |

`metalfencing_a*`, `cornerrail_a1`, `ramp*_a1` are the **same assets** as
`Assets/ArchVis/Industrial/Railing/{MetalFencing_A1..A3,CornerRail_A1,RampLong_A1,RampShort_A1}`
re-tagged `[assumed — name+dimension match, byte identity not checked]`. Prefer the SimReady
path, because it carries the dimensions.

### 3.3 Poly Haven MODELS — 521 CC0, the only redistributable 3D

Poly Haven is the **only** 3D source in this map whose USD/GLB we could ship inside the
repo `[law]` (CC0, `CREDITS.md` already quotes the licence page). Its weakness is polycount:
the photogrammetry rocks and plants run 0.2 M–17 M tris.

The genuinely usable subset for W3, sorted by cost `[measured]` (dimensions X×Y×Z m, author):

| Asset | Tris | Dim (m) | Author(s) | Fits |
|---|---|---|---|---|
| `WetFloorSign_01` | **228** | 0.30×0.36×0.63 | — | props |
| `painted_wooden_bench` | **630** | 1.16×0.50×0.89 | — | midground |
| `rollershutter_door` | 1,104 | 3.08×0.30×2.40 | — | **backdrop (KR shopfront)** |
| `rollershutter_window_01/02/03` | 1,104/1,120/1,120 | 5.10 / 3.60 / 2.98 wide | — | **backdrop (KR shopfront)** |
| `planter_pot_clay` | 3,080 | 0.27×0.26×0.22 | — | midground |
| `utility_box_01` / `_02` | 4,404 / 6,268 | 0.52×0.43×1.12 / 0.92×0.43×1.12 | — | midground vertical |
| `security_light` | 4,668 | 0.32×0.42×0.53 | — | midground |
| `water_manhole_cover` | 6,301 | 0.69×0.69×0.07 | — | props (ground plane) |
| `planter_box_01/02/03` | 8,094/10,944/13,112 | 0.91–1.25 wide | — | midground |
| `korean_fire_extinguisher_01` | 9,913 | 0.28×0.37×0.66 | — | props (**KR-specific**) |
| `modular_fire_escape` | 11,322 | 6.66×1.42×9.76 | — | backdrop (alley) |
| `ocean_buoy` | 12,240 | 1.07×0.95×2.66 | — | **water-adjacent** |
| `lateral_sea_marker` | 13,014 | 3.00×3.00×6.84 | — | **water-adjacent** |
| `metal_trash_can` | 13,960 | 1.85×0.56×0.91 | — | midground |
| `modular_metal_gutter` | 16,490 | 2.27×1.51×1.84 | — | backdrop |
| `exterior_aircon_unit` | 18,986 | 1.80×0.37×0.93 | — | **backdrop (KR facade AC)** |
| `street_lamp_02` / `_01` | 20,338 / 30,610 | 1.68 h / **3.87 h** | — | midground vertical |
| `modular_street_seating` | 25,156 | 4.34×0.77×0.95 | — | midground |
| `tree_stump_01` / `_02` | 41,046 / 62,345 | 1.43×1.59×0.57 / 1.52×1.39×0.52 | Rob Tuytel | props (park/trail) |
| `concrete_road_barrier_02` / `_01` | 42,578 / 80,776 | 1.57×0.44×1.11 / 1.55×0.64×0.84 | — | props |
| `modular_wooden_pier` | 84,780 | 3.10×19.03×7.52 | — | **water-adjacent** |
| `modular_chainlink_fence` | 89,232 | 8.12×2.15×2.52 | — | midground barrier |
| **`modular_urban_apartments_facade`** | **118,215** | **51.53×6.66×17.00** | Kuutti Siitonen et al. | **backdrop, CC0, redistributable** |
| `modular_factory_facade` | 175,014 | 53.33×5.36×29.00 | — | backdrop |
| `modular_electricity_poles` | 200,610 | 13.12×1.96×7.00 | — | midground vertical |

Small-plant subset usable for ground cover (all CC0): `shrub_sorrel_01` 3,319 ·
`shrub_03` 16,955 · `weed_plant_02` 17,062 · `dry_branches_medium_01` 16,803 ·
`nettle_plant` 46,195 · `shrub_04` 47,813 · `dandelion_01` 64,099 · `grass_bermuda_01` 223,596.

**Absent from Poly Haven** `[measured]`: bollards, handrails/guardrails, kerbs, tactile
paving, stairs (only `modular_fire_escape`), bus shelters, road signs.

### 3.4 ambientCG — 3D dead end, decal goldmine

`dataType == 3DModel` → **34 assets, and 32 of them are food** (`3DApple001..003`,
`3DBread001..013`, `3DPastry`, `3DPear`, `3DCake`, `3DCookie`, `3DCucumber`, `3DKiwi`,
`3DLemon`, `3DMango`, `3DMelon`, `3DAvocado`) `[measured]`. Only **`3DTreeStump001`** and
**`3DStick001`** are usable, and Poly Haven's stumps are better.

What *is* worth taking (all CC0, redistributable):

| Category | n | Type | Serves |
|---|---|---|---|
| **Facade** | 26 (`Facade001`…`Facade020C`) | Material | backdrop billboard/facade textures — the cheap alternative to loading building geometry |
| **Sign** | 26 | Material | shop/wall signage plates |
| **Leaking** | 39 (`Leaking001`…`Leaking018*`) | Decal | 개보수 어휘 — water staining, efflorescence |
| **RoadLines** | 69 | Decal | worn road/kerb markings |
| **LeafSet** | 30 | Atlas | leaf-litter atlas — direct input to the W2 leaf-mask rectangle defect |
| SurfaceImperfections | 20 | Material | material layering |
| AsphaltDamage(Set) | 1 Decal + 2 Atlas | Decal/Atlas | pothole/crack overlay for the negative-obstacle cue vocabulary |
| Ground / Gravel / PavingStones / Road / Concrete | 122 / 44 / 155 / 31 / 61 | Material | already the source of our ground kit |

---

## 4. Scene-type × usable-asset map

33 scenes (21 main + 12 batch1). Grouped by what they need; one row per scene type so the
output stays modular per the brief.

| # | Scene type | Scenes | Backdrop need | Midground verticals | Props | Water |
|---|---|---|---|---|---|---|
| A | Campus / plaza stair | 01, 08, 14, 21 | `typical_building_10/11/13` mid tier; `bldg_modern_library` | `bench_park_0*`, `planter_*`, `strt_fxd_bollard_0*`, `lightpost_5m_steel_a_0*`, `bikerack_*` | `utility_cover_01`, `sidewalk_debris_0*`, `sct_leaf_pile_04/05` | — |
| B | Riverfront / embankment | 03, 09, 12, 17 | `bldgs_0{1,2}_distant` far tier (skyline replacement) | `safety_railing_01`, `rail_paintedmetal_lg01`, `veg_shrub_hedge_*`, `veg_grass_clump_*` | `sct_debris_branch_fallen_0*`, `rock_0{1,2}`, PH `ocean_buoy`, `lateral_sea_marker` | **`bridge_01/02`**, PH `modular_wooden_pier` |
| C | Park / trail | 04, 10, 16 | `bldgs_0*_distant` (glimpse only) | `veg_tree_{cherry_japanese,sycamore,juniper_chinese,pine_yellow}`, `veg_shrub_hedge_round_01`, `bench_park_0*` | PH `tree_stump_01/02`, `sct_debris_leaves_dry_0*`, `constr_mov_mound_soil_0*` | `obs_water_fountain_01/02` |
| D | Underpass / overpass | 02, 06, 11 | `wall_resd_01_set_{wall,pillar}`, `strt_fxd_set_sound_barrier_*` | `pole_fxd_pedestrian_signage_0*`, KR signs (§5.3), `strt_fxd_utility_box_sm_01` | `traf_barrier_mov_traffic_cone_28in_*`, `traf_barrier_mov_type3_*`, PH `korean_fire_extinguisher_01` | — |
| E | Alley / low-rise | 15, D4 | **PH `rollershutter_door/window_01..03`**, PH `exterior_aircon_unit`, `ac_unit_04/05/06`, PH `modular_fire_escape`, PH `modular_metal_gutter` | `electricity_box`, `electric_box_lrg_01`, `meter_gas_01`, `trashcan_*`, `obs_dustbin_0*` | `strt_mov_crate_beer_0*`, `obs_trash_bags_01`, `cinder_block`, PH `metal_trash_can` | — |
| F | Apartment / parking entry | 13 | **`apt_complex_assembly`**, `wall_resd_02_set_*` | `traf_barrier_fxd_barriergate_01..03`, `strt_fxd_bollard_0*`, `gen_parking_meter_0*` | KR roadmark stencils `stencil_ko_pattern_colorlane_{pink,lightgreen}`, `traf_barrier_fxd_heightbarrier_01`, `parkingblock_a3_0*` | — |
| G | Amphitheatre / stage | **05** | arc-following backwall → keep procedural; `bldgs_0*_distant` beyond | `veg_shrub_hedge_green_01` band; `bench_park_0*` **only if the openness rule (v5.2 §9) permits** | `utility_cover_01` | — |
| H | Seaside mural stair | 18 | PH `rollershutter_*`, `typical_building_10` (low-rise roofline) | `veg_shrub_*`, `planter_sm_0*` | PH `ocean_buoy` | horizon plate — keep procedural |
| I | Temple / stone path | 07 | — (tree-line) | `veg_tree_juniper_chinese_01`, `veg_shrub_hedge_round_01` | `rock_0{1,2}`, `sct_debris_leaves_dry_0*` | — |
| J | Winder / oblique geometry | 19, 20 | `typical_building_1*` mid tier | `strt_fxd_bollard_0*` (regulated placement only) | `utility_cover_01` | — |
| K | Weather / cue variants | C1, C2, C4 | inherit host scene | inherit | `sct_leaf_pile_04/05` (C2 — replaces the flat leaf decal), `sct_debris_leaves_dry_0*` | — |
| L | Dock / opening / drainage | D1, D2, D3 | `bldg_cml_warehouse_lrg_01..03` | `constr_fxd_fence_cyclone_mod_01`, `constr_mov_fence_section_01`, SimReady `metalfencing_a1..a3` (1.07 m) | SimReady `dockboard_a01..a08`, `deluxesafetytape_*`, `traf_barrier_mov_traffic_cone_28in_*`, `constr_mov_mound_{gravel,asphalt}_0*` | — |
| M | Illusion / flat-cue | N1, N2, N3, N5 | minimal | minimal (cue purity) | `obs_debris_road_0*`, ambientCG `AsphaltDamage*` decals | — |
| N | Downhill ramp | N4 | `bldgs_0*_distant` | `traf_spd_fxd_kerb_ramp_01`, `strt_fxd_bollard_0*` | `speed_bump_01/02`, `speed_cushion_01` | — |

**Deliberately excluded from every row**: people (`ncap_*`, `pedestrian_generic_*`,
`Isaac/People/`) and vehicles (`honey`/`tri`) — STATUS 규율 *사람·차량 보류*. They are
catalogued in §3.1 so the deferral is a decision, not an oversight.

---

## 5. Per-workstream shortlists

Sizes are complete download cost (USD wrapper + `_base` + `_inst` + `_inst_base` + textures)
from the recursive listing `[measured]`.

### 5.1 Workstream: buildings backdrop (5 scenes)

Two tiers plus one CC0 hedge. **Take the mid tier first** — it is the direct replacement for
`build_building`'s window-prim explosion diagnosed in `korean_urban_backdrop.md` §1.1.

| Tier | Asset | Tris | Extent (m) | zmin | mpu | Cost |
|---|---|---|---|---|---|---|
| mid | `typical_building_10` | **21,965** `[measured]` | 34.74 × 30.17 × 30.33 | **−7.904** | 1.0 | **8.25 MB** |
| mid | `typical_building_12` | — | — | — | 1.0 `[assumed]` | 18.45 MB |
| mid | `typical_building_11` | — | — | — | 1.0 `[assumed]` | 24.60 MB |
| mid | `typical_building_13` | — | — | — | 1.0 `[assumed]` | 20.56 MB |
| mid | `typical_building_03` / `_07` / `_08` / `_109` | — | — | — | — | 3.95 / 5.57 / 3.78 / 5.07 MB |
| far | `bldgs_01_distant/Building_178` | **1,354** `[measured]` | 60.39 × 32.86 × 5.68 (unit-converted) | 0.000 | **0.01** | **0.43 MB** |
| far | `Building_181` / `_182` / `_20` | — | — | — | 0.01 `[assumed]` | 0.64 / 0.63 / 0.62 MB |
| far | `Building_180` / `_183` / `_19` | — | — | — | 0.01 `[assumed]` | 1.21 / 1.28 / 1.06 MB |
| KR block | `apt_complex_assembly` | — | — | — | — | 671.86 MB ⚠️ **probe before committing** |
| CC0 | PH `modular_urban_apartments_facade` | 118,215 | 51.53 × 6.66 × 17.00 | — | — | (Poly Haven, redistributable) |
| CC0 | PH `rollershutter_door` + `rollershutter_window_01..03` | 1,104–1,120 ea | 2.98–5.10 wide | — | — | KR shopfront ground floor |
| CC0 tex | ambientCG `Facade001..Facade020C` (26) | — | — | — | — | billboard fallback |

**Recommended v1 pull** `[measured]`: 8 mid (`10, 12, 11, 13, 03, 07, 08, 109`) + 7 far
(`178, 181, 182, 20, 180, 183, 19`):

| Part | Files | Size |
|---|---|---|
| mid-tier USD (8 assets × 4-file chain) | 32 | 47.30 MB |
| mid-tier textures from `shared_textures/` | 48 | 111.25 MB |
| far-tier USD (7 assets × 2-file chain, no textures) | 14 | 5.88 MB |
| **total** | **94** | **164.43 MB** |

Note the mid tier is texture-dominated (68 %), so trimming to 4 buildings roughly halves it.
Skip `apt_complex_assembly` (672 MB) until a render A/B justifies it. Skip all
`rivermark_plaza_bldg_*` (§2.1).

### 5.2 Workstream: midground verticals

| Group | Assets | Cost | Note |
|---|---|---|---|
| benches | `bench_park_01..05` | 29.91 MB | anchor-adjacent placement per v5.1 §3 |
| planters | `planter_{lrg_01,lrg_02,med_01,round_01..03,sm_01..04}` | 16.11 MB | replaces `build_planter` |
| hedges | `veg_shrub_hedge_{green,round,yellow}_01` | **13.26 MB** | **replaces `build_hedge` box+blob in 20 scenes** |
| grass clumps | `veg_grass_clump_*` (14+) | 18.68 MB | candidate fix for the 9/33 σ_LF gate |
| bollards | `strt_fxd_bollard_01/02/03/05/06` | 77.64 MB | must satisfy v5.1 §2 (h 0.8–1.0, Ø0.1–0.2, 1.5 m pitch) — **verify measured heights before wiring** |
| street lamps | `streetlamp_01..03` | **0.51 MB** | cheapest vertical in the catalog |
| light posts | `lightpost_5m_steel_a_01..03` + `light_post_5m_steel_a_01` | 479.92 MB ⚠️ | pull **one** variant, not the group |
| utility boxes | `strt_fxd_utility_box_sm_01`, `electric_box_lrg_01`, `electricity_box` | 36.65 MB | alley/underpass |
| facade AC | `ac_unit_04/05/06` | **4.83 MB** | Korean facade signature |
| bins | `trashcan_{01,cylinder_01,square_01,square01}`, `obs_dustbin_01..06` | 92.40 MB | pull 2–3 only |
| bike racks | `bike_rack_01/02/multi_01`, `bikerack_*` | **4.88 MB** | cheap, high scene-read value |
| railings | `safety_railing_01`, `rail_paintedmetal_lg01` | **0.29 MB** | ⚠️ `safety_railing_01` supplier = Mathworks_Modified (§2.3) |
| railings (alt) | SimReady `metalfencing_a1/a2/a3` (**1.07 m** measured), `cornerrail_a1` | — | dimensioned; prefer for regulation checks |
| bus stops | `bus_stop_01`, `bus_stop`, `busstop_med01`, `busstop_sm01` | 31.58 MB | |
| walls/fences | `wall_resd_01_set_{wall,fence,pillar}`, `wall_resd_02_set_*` | 85.07 MB | apartment-complex boundary (scene 13) |
| CC0 | PH `street_lamp_01` (3.87 m), `utility_box_01/02`, `modular_street_seating`, `planter_box_01..03`, `modular_chainlink_fence` | — | redistributable alternates |

### 5.3 Workstream: props — including the Korean signage decision

**korea_mobiltech signs: 156 USD confirmed** `[measured]`, whole folder (156 USD + 158
textures = 314 files) = **41.92 MB**. Series split `[measured]`: `kr1xx` 42, `kr2xx` 27,
`kr3xx` 39, `kr4xx` 36, plus 12 named (`krschoolzone_1..6`, `krzone30`,
`krspeedmanagementzone_1/2`, `krconstruction_50`, `krroadname`, `krvms_40`).

Measured geometry, `sign_kr101.usd` `[measured]`:
`104 tris`, bbox **0.002 × 0.844 × 0.741 m**, `zmin 0.000`, `mpu 1.0`, faces along +X.
Texture `sign_kr101.png` = 2048 × 1800 RGB, **no alpha** (shape is real geometry, not a
cutout); dominant colours white / red / yellow / black — consistent with the Korean
주의표지 yellow-field red-border family `[measured]`.
Dependencies: local `./textures/sign_kr101.png` + **two USD material libraries**
`../../../../nv_core/materials/signs/general/{metal/metal__steel_galvanized.usd,
retroreflective/retroreflective__base_mod.usd}` `[measured]` — the whole
`nv_core/materials/signs/` tree is only **2.15 MB / 16 files**, so pull it entire.

⚠️ **844 mm side vs the 900 mm 주의표지 standard for general roads** — a ~6 % undersize
`[measured]` `[assumed: the standard]`. Flag before any regulation-adjacent claim. Do **not**
uniformly rescale without checking each series; the 2xx/3xx families have different standard
sizes.

**Per-scene sign shortlist** — series meanings are Korean 도로교통법 시행규칙 별표6
numbering `[assumed — numbering convention, not verified against the rendered plates]`.
**Pixel-verify each plate before wiring**, exactly as the seasonal rule requires:

| Scene type | Signs | Why |
|---|---|---|
| D underpass/overpass (02, 06, 11) | `kr321` 보행자전용도로, `kr322` 횡단보도, `kr211` 진입금지 | v5.2 §8 allows only real 도로교통법 plates — these replace the deleted home-made warning boards |
| F apartment entry (13) | `kr224` 최고속도제한, `kr226` 서행, `kr320`/`kr320_2..4` 자전거주차장, `krzone30` | parking-entry regulation |
| A campus/plaza (01, 08, 14, 21) | `kr324`/`kr324_2` 어린이보호구역, `kr323` 노인보호구역, `kr325` 장애인보호구역 | KR-specific institutional read |
| C park/trail (04, 10, 16) | `kr302` 자전거전용도로, `kr303` 자전거·보행자겸용도로, `kr333` 자전거나란히통행 | shared-path identity |
| B riverfront (03, 09, 12, 17) | `kr303`, `kr321`, `kr126` 미끄러운도로 | embankment path |
| L dock/drainage (D1, D3) | `krconstruction_50`, `kr136` 도로공사중 | works zone |
| M flat-cue (N1, N2, N5) | **none** | cue purity |

**Poles do not exist** (§7). Mount signs on our own procedural post; do not wait for
`sign_pole_750cm`.

**Other props** `[measured]` costs:

| Group | Assets | Cost |
|---|---|---|
| manhole / ground plate | `utility_cover_01` | **4.98 MB** |
| sidewalk litter | `sidewalk_debris_01/02` | 11.70 MB |
| leaf piles | `sct_leaf_pile_04/05` | 352.20 MB ⚠️ (`_base.usd` alone is **110 MB** — pull one, or decline) |
| leaf scatter (cheap alt) | `sct_debris_leaves_dry_01..04` | **5.34 MB** ✅ prefer this |
| fallen branches | `sct_debris_branch_fallen_01..04` | 42.38 MB |
| loose stone | `rock_01`, `rock_02`, `rock_03_broken` | 51.15 MB (we already have 5 lighter `Vegetation/Rocks/*.usda`, 268–438 tris) |
| masonry | `cinder_block`, `concrete_block_01/02` | 17.33 MB |
| earthworks | `constr_mov_mound_{soil_01,soil_02,gravel_01,asphalt_01,asphalt_02}` | 184.59 MB ⚠️ pull 2 |
| cones | `traf_barrier_mov_traffic_cone_28in_orange_{clean,dirt,dam_01,dam_02}_01` | 131.02 MB ⚠️ pull `clean` + `dirt` only |
| barricades | `traf_barrier_mov_type3_{4,6,8}feet_stripe_orange_white_01` | **9.49 MB** ✅ |
| sawhorse | `obs_sawhorse_barrier_01`, `_dam_01` | 42.17 MB |
| KR roadmarks | `stencil_ko_pattern_colorlane_{pink,lightgreen}`, `stencil_ko_arrow_*`, `stencil_ko_pattern_busonlyline_504_*` (9) | small (10–36 KB each) ✅ |
| SimReady, dimensioned | `deluxesafetytape_{a,b}*` (2–12 m spans), `heavydutytrafficcone_a01..a06` (0.46/0.71/0.91 m), `dockboard_a01..a08` | — |
| CC0 | ambientCG `AsphaltDamage001` + `AsphaltDamageSet001/002`, `LeafSet001..030`, `Leaking001..018*` | — |

### 5.4 Workstream: water-adjacent

| Asset | Source | Note |
|---|---|---|
| `bridge_01`, `bridge_02` | NVIDIA `props_general` | 52.79 MB — probe extents first, these may be highway-scale |
| `obs_water_fountain_01/02` | NVIDIA `props_general` | 88.30 MB ⚠️ pull one |
| `sign_plaza_fountain_01` | NVIDIA `props_general` | plaza water feature signage |
| `modular_wooden_pier` (84,780 tris, 3.10 × 19.03 × 7.52 m) | **Poly Haven CC0** | scenes 09, 12 — redistributable |
| `ocean_buoy` (12,240), `lateral_sea_marker` (13,014) | **Poly Haven CC0** | scenes 12, 18 |
| `obs_canoe_01`, `obs_sea_kyak_01`, `obs_stand_up_paddle_board` | NVIDIA `props_general` | riverbank dressing — apply the v5.2 §6 openness cap |
| `rock_moss_set_01/02` (57–63 k tris) | **Poly Haven CC0** | waterline rock, 8 m spans |
| `Ground106` (river/riverbed tags), `Gravel043` | **ambientCG CC0** | waterline material |

Water **surface** stays procedural — no asset in any catalog supplies a Korean stream/river
plane, and the horizon plate in scene 18 is already a solved procedural.

### 5.5 Lean shortlist total — the number to budget against

Every group below is the *trimmed* selection, not the wholesale group from §5.1–5.4
`[measured]`:

| Group | Files | Size |
|---|---|---|
| buildings (8 mid + textures + 7 far) | 94 | 164.43 MB |
| `signs_kr` (all 156 + 158 textures) | 314 | 41.92 MB |
| `roadmarks_kr` (9 KR stencils) | 9 | 0.21 MB |
| hedges (3) | 21 | 13.26 MB |
| grass clumps | 43 | 18.68 MB |
| leaf scatter `sct_debris_leaves_dry_01..04` | 24 | 5.34 MB |
| benches `bench_park_01..05` | 23 | 29.91 MB |
| planters (11) | 44 | 16.11 MB |
| street lamps `streetlamp_01..03` | 12 | 0.51 MB |
| AC units `ac_unit_04..06` | 12 | 4.83 MB |
| bike racks | 28 | 4.88 MB |
| railings (2) | 8 | 0.29 MB |
| utility box `strt_fxd_utility_box_sm_01` | 10 | 26.85 MB |
| manhole `utility_cover_01` | 7 | 4.98 MB |
| sidewalk debris (2) | 8 | 11.70 MB |
| cinder / concrete block (3) | 12 | 17.33 MB |
| Type-III barricades 4/6/8 ft | 39 | 9.49 MB |
| cones 28 in clean + dirt | 26 | 52.35 MB |
| `bridge_01` | 7 | 3.36 MB |
| `obs_water_fountain_01` | 19 | 56.80 MB |
| **subtotal (dsready)** | **760** | **483.20 MB** |
| `nv_core/materials/signs/` (sign dependency) | 16 | 2.15 MB |
| `nv_core/materials/SimPBR*.mdl` (universal dependency) | 9 | 0.14 MB |
| **TOTAL** | **785** | **485.49 MB** |

Plus, separately and **redistributable**: the Poly Haven subset (§3.3) and the ambientCG
decal/facade/leaf sets (§3.4). Those two are the only downloads that could legally ship
inside the repo.

Two groups in this table are worth challenging before the pull: `obs_water_fountain_01`
(56.80 MB for one scene-type) and `cones 28in clean+dirt` (52.35 MB — SimReady
`heavydutytrafficcone_a01..a06` may be cheaper and comes with published extents, §3.2).

---

## 6. Procurement manifest draft

Extends the `assets/download_vegetation.py` contract exactly: re-runnable, size-verified,
`--only <group>` selective, directory structure mirrored, MD5 when the ETag is not multipart.

### 6.1 New file

`assets/download_urban.py` — sibling of `download_vegetation.py`, **new file, does not touch
existing downloaders**. Target root `assets/urban/`.

### 6.2 Constants (licence-load-bearing)

```python
# ONLY this root. The identical relative paths also exist under
#   Assets/Isaac/4.5/Isaac/Environments/Outdoor/Rivermark/dsready_content/
# which is Limited Use Content ("without modifications") and MUST NOT be used.
BASE_DS  = ("https://omniverse-content-production.s3.us-west-2.amazonaws.com/"
            "Assets/Isaac/4.5/NVIDIA/dsready_content/")
BASE_SR  = ("https://omniverse-content-production.s3.us-west-2.amazonaws.com/"
            "Assets/simready_content/")
BANNED_SUBSTRINGS = ("Environments/", "/Rivermark/", "rivermark_plaza_bldg_",
                     "/People/", "/Characters/", "ncap_", "pedestrian_generic_",
                     "/vehicles/ford/", "/vehicles/volvo/", "/vehicles/piaggio/",
                     "/vehicles/hero/")
```

Every key is asserted against `BANNED_SUBSTRINGS` before the request is made — a licence
guard in code, not in a comment.

### 6.3 Group structure

```
GROUPS = {
  "buildings_mid":   [...8 typical_building_* × 4 USD variants + shared_textures/<name>_*],
  "buildings_far":   [...7 Building_* × 2 USD variants],       # no local textures
  "signs_kr":        ["korea_mobiltech/.../country_signs/*.usd", ".../textures/*.png",
                      "nv_core/materials/signs/**"],           # 41.92 + 2.15 MB
  "roadmarks_kr":    ["korea_mobiltech/country_assets/traffic/roadmarks/*.usd"],
  "midground":       [hedges, grass_clumps, benches, planters, streetlamps, ac_units,
                      bike_racks, railings, utility_boxes],
  "props":           [utility_cover_01, sidewalk_debris, sct_debris_leaves_dry_*,
                      type3 barricades, cones clean+dirt, cinder/concrete_block],
  "water":           [bridge_01, obs_water_fountain_01],
  "simready":        [metalfencing_a1..a3, deluxesafetytape_*, heavydutytrafficcone_*,
                      gardenplanter_*, dockboard_a0*],
}
```

`SimPBR.mdl` (9 files, 0.14 MB) is an implicit dependency of every dsready asset and belongs
in a `_core` group pulled by all others.

### 6.4 The three traps the manifest must encode

**(a) Four-file wrapper chain.** A dsready asset is not one USD `[measured]`:

```
X.usd            wrapper: sublayer ./X_base.usd  + payload nv_core/.../thumb_rig_prop.usd
  └─ X_base.usd  reference ./X_inst.usd  + info:mdl:sourceAsset ../../../../nv_core/materials/SimPBR.mdl
       └─ X_inst.usd        sublayer ./X_inst_base.usd  + texture path OVERRIDES
            └─ X_inst_base.usd   the geometry (21,965 tris for typical_building_10)
```

Pull only `X.usd` and you get **0 meshes** — verified: `typical_building_10.usd` alone
resolves to 504 tris, the full chain to **21,965** `[measured]`. The `thumb_rig_prop.usd`
payload is a thumbnail rig and can be left unresolved (warning only, no geometry loss).

**(b) Texture paths differ between the two `_inst` layers, and the outer one wins.**

```
X_inst.usd       inputs:diffuse_texture = ../../../common_assets/shared_textures/X_wall_a.png   ← real
X_inst_base.usd  inputs:diffuse_texture = materials/textures/X_wall_a.png                       ← does not exist
```

`[measured]` for `typical_building_10`. So building textures live in the **shared pool**
(1,410 files / 2,609 MB), and the manifest must pull only the six files matching the asset
name (`typical_building_10` → 6 files, 4.65 MB). **Two of the buildings I sampled
(`typical_building_18`, `typical_building_106`) have zero matching files in
`shared_textures/`** `[measured]` — they resolve elsewhere. **Run the
`download_vegetation.py --discover` procedure per building; do not guess.**

**(c) Cross-folder relative sublayers.** `bench_park_01.usd` sublayers
`../bench_park_03/bench_park_03.usd` `[measured]` — the same directory-escaping pattern as
`Shrub/Boxwood.usd → ../Trees/materials/bark3.mdl`. **Flattening the tree breaks it.** Mirror
`nv_content/` structure verbatim, as `assets/vegetation/` already does.

### 6.5 Units and Z-base normalisation table

The loader needs this, not the downloader — but the manifest should carry it so the values
travel with the asset.

| Asset | `metersPerUnit` | bbox zmin | Placement correction |
|---|---|---|---|
| `typical_building_10` | 1.0 | **−7.904 m** | translate +7.904 in Z to sit on grade |
| `bldgs_01_distant/Building_178` | **0.01** | 0.000 | scale ×0.01 (or set stage mpu); no Z offset |
| `sign_kr101` | 1.0 | 0.000 | none; panel normal is +X |
| `Vegetation/Rocks/rock_small_01` (existing) | 1.0 | −0.128 m | +0.128 (already documented in CREDITS) |

**Do not assume a library-wide convention.** Measure per asset with the `deps.py` recipe.

### 6.6 `.gitignore`

One line, mirroring the existing vegetation rule:

```
# NVIDIA Omniverse urban/dsready USD — 재배포 금지 라이선스 (동일 판정: ZZ §9.2 / §10.6)
assets/urban/
```

Poly Haven and ambientCG downloads are CC0 and **could** be tracked, but for consistency with
`assets/*.exr` / `assets/*.jpg` they should go to `assets/urban_cc0/` and be ignored with a
reproducibility script — size, not licence, is the reason.

### 6.7 `CREDITS.md` additions (author's own section only)

A new section *"도시 에셋 — 건물·가로시설·한국 표지 (담당: W3-R 조달)"* with: the dual-root
licence warning verbatim, the `_Supplier` provenance table (§2.3), and the per-file table.
**Do not edit the existing 하늘/식생/실사 sections.**

---

## 7. Negative findings (measured absences — do not re-search these)

| Claim | Verdict | Evidence |
|---|---|---|
| korea_mobiltech sign poles (`sign_pole_750cm`, `metal_pole_210cm`, `sign_pole_arm_*` ×13) | **Geometry absent.** Each folder holds only `mobiltech_manifest.csv`. Absent in **4.5, 5.0, 5.1 and 6.0** alike. | `[measured]` — the manifest itself lists 4 USD rows per pole flagged `_Zip_CommonInt` (internal zip), none published |
| Ginkgo / 은행나무 | absent | 0 hits for `ginkgo`,`maidenhair` in 275,368 keys + 100,902 lines `[measured]` |
| Zelkova / 느티나무 | absent | 0 hits `zelkova`,`keyaki` `[measured]` |
| 이팝나무 / 배롱나무 / 메타세쿼이아 | absent | 0 hits `chionanthus`,`lagerstroemia`,`metasequoia` `[measured]` |
| ambientCG 3D models useful to us | effectively absent | 34 `3DModel` assets, 32 are food `[measured]` |
| Poly Haven bollards / handrails / kerbs / tactile paving / stairs / bus shelters | absent | keyword sweep over 521 models `[measured]` |
| A Korean water-surface / stream asset anywhere | absent | no hit in any catalog `[measured]` |
| Licence text specific to `simready_content` or `dsready_content` | **no file exists in those prefixes** | `[measured]` — only `/Isaac/Environments/environment-supplement-LICENSE.txt` exists |
| `Assets/Vegetation/` species count grows in newer Isaac | no — `NVIDIA/Assets/Vegetation/` in 4.5 mirrors the top-level `Assets/Vegetation/` | `[measured]` |

**`props_vegetation/` is a genuinely different tree library from `Assets/Vegetation/`** — ~60
`veg_tree_*` species, none of them ginkgo/zelkova, but including `veg_tree_cherry_japanese_01`,
`veg_tree_sycamore_01`, `veg_tree_juniper_chinese_01`, `veg_tree_pine_yellow_01..04` `[measured]`.
Worth an A/B against the `Assets/Vegetation/Trees/` versions we already hold (111.35 MB for
the four-species set).

---

## 8. Probe log

15 keys, **2.44 MB** total, all from the `NVIDIA/dsready_content/` root `[measured]`.

| Key (from `nv_content/`) | Bytes | Result |
|---|---|---|
| `korea_mobiltech/.../country_signs/sign_kr101.usd` | 13.5 KB | 104 tris, 0.002×0.844×0.741 m, mpu 1.0, 3 deps |
| `korea_mobiltech/.../country_signs/textures/sign_kr101.png` | 126.4 KB | 2048×1800 RGB, no alpha, KR yellow/red palette |
| `korea_mobiltech/.../props_poles/sign_pole_750cm/mobiltech_manifest.csv` | 1.0 KB | **proves the 4 pole USDs are declared but unpublished**; `_Supplier=MOBILTECH` |
| `common_assets/props_structures/bldgs_01_distant/Building_178.usd` | 214.8 KB | wrapper; mpu **0.01** |
| `…/bldgs_01_distant/Building_178_inst.usd` | 219.9 KB | **1,354 tris**, 10 meshes, zmin 0.000, 39 asset-path deps |
| `…/typical_building_10/typical_building_10.usd` | 73.1 KB | wrapper → sublayer `_base` |
| `…/typical_building_10/typical_building_10_base.usd` | 1,771.1 KB | 504 tris only; references `_inst` |
| `…/typical_building_10/typical_building_10_inst.usd` | 12.9 KB | **texture overrides → `shared_textures/`** |
| `…/typical_building_10/typical_building_10_inst_base.usd` | 1,737.0 KB | **21,965 tris**, 21 meshes, 34.74×30.17×30.33 m, zmin −7.904 |
| `common_assets/props_general/bench_park_01/bench_park_01.usd` | 17.0 KB | **sublayers `../bench_park_03/…` — cross-folder trap** |
| `…/planter_lrg_01/planter_lrg_01.usd` + `_base.usd` | 16.1 + 91.0 KB | 4-file chain confirmed |
| `…/utility_cover_01/utility_cover_01.usd` + `_base.usd` | 77.1 + 3.9 KB | 4-file chain confirmed |
| `…/props_vegetation/veg_shrub_hedge_green_01/veg_shrub_hedge_green_01.usd` | 29.8 KB | wrapper; `.dds` texture (349.7 KB) — **first `.dds` seen; verify Isaac reads it** |
| `nv_content/manifest.csv` (metadata) | 325.4 KB | 2,124 rows, `_Supplier` provenance |
| `nv_content/mobiltech_manifest.csv` (metadata) | 2.5 KB | mobiltech index |

Also fetched as metadata (not assets): `Assets/simready_content/asset_info.json` (802 KB),
`dsready_content/file_list.txt` (10.9 MB), `environment-supplement-LICENSE.txt` (1.5 KB),
Poly Haven + ambientCG JSON APIs.

---

## 9. Open questions for the supervisor

1. **`rivermark_plaza_bldg_*` under the `NVIDIA/` root** — textually Content, nominally the
   Limited Use environment. My recommendation is to decline (zero cost). Confirm.
2. **`apt_complex_assembly` at 672 MB** — the only asset that reads as a Korean apartment
   complex. Probe-and-A/B, or stay procedural for scene 13?
3. **Third-party suppliers** (§2.3) — is NVIDIA's grant sufficient for `CGTrader` / `Hum3D` /
   `Mathworks_Modified` sourced assets, or do we exclude them on principle? `safety_railing_01`
   is the one shortlist item affected.
4. **`sign_kr101` measures 844 mm against a 900 mm standard.** Rescale, accept, or verify the
   whole series first? This is a regulation-adjacent number and the 연대 3요소 discipline
   applies.
5. **`.dds` textures** in `props_vegetation/` — no other catalog we use ships DDS. Needs a
   one-scene render check before the vegetation A/B is scheduled.
6. **People/vehicles remain deferred** — catalogued (§3.1) so the deferral is explicit. Confirm
   it holds through W3.
7. **Cross-package conflict, highest value in this report (§2.4).** W3-R2 §2.2 closed the
   street-furniture asset route on Limited Use grounds; I measured that all six cited assets
   also exist at the general-Content `NVIDIA/dsready_content/` root (and `streetlamp_01` exists
   *only* there — 1,454 vs 1,018 pole USDs, 2,571 vs 110 `props_general` USDs). If you accept
   the measurement, ~20 `rebuild-procedural` verdicts in that package become re-adjudicable and
   the W3 midground workstream gets much cheaper. **This is the one item worth deciding before
   any W3 code starts**, because the two packages currently prescribe opposite implementations.

---

## Appendix — reproduction

```bash
# 1. recursive listing (≈6 min, 275,368 keys)
python3 s3ls.py "Assets/Isaac/4.5/" --out isaac45.tsv

# 2. published index (fast search cache; a SUBSET of the above)
curl -s "https://omniverse-content-production.s3.us-west-2.amazonaws.com/\
Assets/Isaac/4.5/NVIDIA/dsready_content/file_list.txt" -o ds_file_list.txt

# 3. canonical asset list per category
python3 dsq.py "dsready_content/nv_content/common_assets/props_structures/"

# 4. shortlist size roll-up
python3 shortlist.py

# 5. dependency + geometry measurement (needs pxr; /tmp/usdvenv has usd-core 0.26.8)
/tmp/usdvenv/bin/python deps.py

# 6. CC0 catalogs
curl -s "https://api.polyhaven.com/assets?t=models"          -o ph_models.json
curl -s "https://ambientcg.com/api/v2/full_json?limit=3000"  -o acg_all.json
```

Scratchpad location this session:
`/tmp/claude-1000/-home-vislab-Desktop-work-sy/5ee36dfd-2b10-441f-abd8-7cf6372faec2/scratchpad/`
