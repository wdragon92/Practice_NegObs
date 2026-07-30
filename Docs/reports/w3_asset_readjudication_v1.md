# W3 asset re-adjudication v1 — the loader's verdict on spec §3

> **Wave**: W3 · **WP**: T4 (urban asset loader) · **Window**: 0 · **Batch**: CB-0
> **Date**: 2026-07-30 · **Branch**: `feat/realism-v1`
> **Authority above this document**: `Docs/briefs/w3_execution_spec_v1.md`. Where this report
> disagrees with the spec it says so explicitly and **does not act on the disagreement** —
> §3.4's quirks are implemented as written, with the divergence recorded for the supervisor.
> **Instrument**: `urban_kit.py` (this WP) on usd-core 26.8 + PIL 12.3, CPU only.
> **Reproduce**: `/tmp/usdvenv/bin/python urban_kit.py --self-check` (needs `numpy`, `pillow`)
> and `python3 urban_kit.py --sheet` for the full 275-row table.

---

## 0. Headline

**Every asset the spec names loads.** 275 of the 291 procured rows are placeable and all 275
pass the loader's self-check: stage opens, `mpu` reproduces, effective triangle count reproduces
the manifest, the parent-Xform placement composes, the far-tier override binds, the alias table
holds, the banned-path guard fires on nothing. 16 rows are correctly not placeable — 15 `_core`
material libraries with no geometry and the one season-FAIL row.

Four findings change how a W3 row must be read. Each is measured, each names the source row it
corrects, and **none of them is acted on unilaterally**:

| # | Finding | Affects |
|---|---|---|
| **F-A** | The far tier is **already inside** the ≤ 0.55 albedo band once the shipped `diffuse_tint` is counted — worst case **0.534**. §1.11's scale factor computes to **1.000** on all 40 materials. The tier's real material defect is `metallic = 1.0` | §1.11 · N-A4 · the render gate |
| **F-B** | The manifest's `z_advice` field contains **zero** "lift by −zmin" rows, against §3.4-1's "the 28 props that genuinely need `−zmin` are listed there". The field's own metric is structurally blind to single-mesh props | §3.4-1 · C-18 · every prop row |
| **F-C** | Referencing `_inst.usd` (quirk 2, mandatory) **drops the wrapper's emissive night rig** — 22 … 13,320 tri per mid-tier building, including `typical_building_109`'s rooftop **beacon** | §3.4-2 · N-A5 · BS-1…BS-6 |
| **F-D** | Three midground vegetation rows are **PointInstancer** assets whose effective triangle count is 5 – 52× the unique count (`veg_shrub_hedge_green_01` 20,894 → **758,206**) | §3.2 B1b · §12-14 |

---

## 1. Method

Every number below is produced by `urban_kit.py`, not copied from a source document.

- **Traversal**: `Usd.PrimRange.Stage(stage, Usd.TraverseInstanceProxies(Usd.PrimAllPrimsPredicate))`.
  §6.2's T4 trap is reproduced: `bench_park_01` reads **0 triangles** under a plain
  `stage.Traverse()` and **35,396** with instance proxies expanded `[measured]`.
- **Triangles**: `Σ(faceVertexCount − 2)`, with PointInstancers expanded through `protoIndices`
  — the manifest's own definition. Without the expansion two rows disagree with the manifest by
  up to 37× (§4 F-D).
- **Z**: per-triangle centroid z under the composed local-to-world transform, PointInstancer
  instance transforms applied. Reported as *the fraction of an asset's own triangles that sit
  below its own local z = 0*.
- **Albedo**: mean linear-Rec.709 luminance of the decoded sRGB diffuse map (PIL), then
  multiplied by the material's authored `diffuse_tint` — `SimPBR_Model.mdl:91` makes that a
  literal multiply, `base_color = multiply_colors(diffuse_color, diffuse_tint, 1.0)`.
- **Materials**: `UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()` per Mesh, and the
  MDL input set read off the composed `Shader` prim.

Read-only throughout. `assets/urban_manifest_w3.json`, `assets/verify_urban.py`,
`assets/download_urban.py` and `.gitignore` belong to the procurement agent and were not
touched (spec §0, §12-17).

---

## 2. What the loader delivers

`/urban_kit.py` + `scenes/main/urban_kit.py`, `scenes/batch1/urban_kit.py` (symlinks).
Every asset row in W3 goes through one call:

```python
from urban_kit import add_urban_asset
add_urban_asset(stage, f"{ROOT}/Bollard_00", "bollard_01",
                pos_m=(-8.40, -2.60, 0.0), yaw_deg=0.0, scene="01")
```

| §3.4 quirk | Status | How |
|---|---|---|
| 1 · no Z lift on the mid tier; per-asset `z_advice` | **implemented, divergence recorded (F-B)** | `z_mode='grade'` default; `'base'` and `'attach'` explicit; `Z_REVIEW` advisory on 20 rows |
| 2 · reference `_inst.usd` | **implemented, consequence recorded (F-C)** | `resolve_usd()` picks the single `_inst.usd` key from the manifest, never a name guess |
| 3 · `mpu` per asset | **implemented** | scale carries `mpu_asset / mpu_stage`; the 8 far-tier rows at `mpu 0.01` land at their manifest metre size, verified in the self-check |
| 4 · parent-Xform placement | **implemented** | the reference lands on `<path>/Asset`, every op on the parent, T → Rz → (Rx,Ry) → S |
| 5 · 240 dead `materials/textures/*.png` refs | **confirmed, 240 exactly** `[measured]` | never resolved; only the composed winning value is read |
| 6 · mirror `nv_content/` (3 cross-folder aliases) | **implemented + a new trap, §5 A-1** | alias verified against C-26 in the self-check |
| 7 · asset backdrops must still be dressed | **not this WP** | K3's `facade_kit` attachment layer |
| §1.11 far-tier albedo override | **implemented, premise corrected (F-A)** | `_bind_far_override()`, A/B arms `far_override="auto" \| "off"` |

Beyond the quirks, the loader is also the one place three refusals live, so thirteen work
packages cannot each decide differently:

- `veg_shrub_hedge_round_01` — season FAIL (C-21), spec §12-7. **Refused outright.**
- `sct_debris_leaves_dry_01..04` — leaf scenes only (C2 · 07 · 10 · D3). Refused elsewhere when
  `scene=` is passed; warns once when it is omitted.
- `traf_barrier_mov_type3_*` — D2 only. Same mechanism.
- the manifest's 16 `banned_substrings` are re-checked on every resolved path (0 hits across all
  275 rows `[measured]`); the procurement agent's own guard was not touched.

**Self-check result** `[measured 2026-07-30]`:

```
[self-check] manifest rows 290 -> placeable 275
[self-check] mpu ok 275/275 · tri ok 275/275
[self-check] placed 275/275
[self-check] far-tier world height ok (8 rows)
[self-check] far-tier override bound on 63/79 meshes
[self-check] aliases + banned-path guard ok (275 paths, 16 patterns)
[self-check] Z_REVIEW 45 rows re-measured, drift 0
[self-check] PASS — 275 ok, 0 problems
```

`63/79` is the intended number, not a shortfall: the 16 unbound meshes are the eight buildings'
glass and interior-cubemap prims (2 each), which carry no diffuse texture. Replacing a
translucent or emissive material with an opaque OmniPBR would be a worse defect than the one the
override exists to fix.

---

## 3. F-A — the far-tier near-white skyline (§1.11)

### 3.1 The ruling's premise reproduces exactly

`house_wall_001_Diffuse.png` linear albedo **0.874**, 99.58 % of pixels over linear 0.8;
`concrete_014_Diffuse.png` **0.969**, 99.41 % `[measured]`. Both agree with PROC §6.2 to three
decimals. The raw-texture measurement is not in dispute.

### 3.2 The premise omits the shipped tint

Every far-tier SimPBR material authors a `diffuse_tint`, and `SimPBR_Model.mdl:91` multiplies it
into the decoded texture. Effective albedo, all 8 buildings, all 7 material kinds `[measured]`:

| Material | Diffuse map | raw albedo | authored `diffuse_tint` (luma) | **effective** | bound tris |
|---|---|---:|---:|---:|---:|
| `MI_Building_Wall_03` | `house_wall_001` | 0.874 | 0.611 | **0.534** | 31.2 – 81.2 % |
| `MI_Building_Wall_01` | `house_wall_001` | 0.874 | 0.599 | 0.524 | 16.5 – 66.1 % |
| `MI_Building_Wall_02` | `house_wall_001` | 0.874 | 0.531 | 0.464 | 1.0 – 17.5 % |
| `MI_Building_Wall_05` | `house_wall_001` | 0.874 | 0.446 | 0.390 | 1.6 – 2.8 % |
| `MI_Building_Walkway_01` | `concrete_014` | 0.969 | 0.371 | 0.359 | 0.6 – 1.4 % |
| `MI_Building_Roof_01` | `concrete_006` | 0.402 | 0.620 | 0.249 | 0.1 – 0.2 % |
| `MI_Window_Interior_01/02` | `plastic_base` | **0.841** | 0.022 / 0.165 | 0.019 / 0.138 | 6.3 – 71.2 % |
| `MI_Building_Wall_04` | `brick_wall_001` | 0.074 | 1.000 | 0.074 | 21.7 – 25.7 % |

**The tier's maximum effective albedo is 0.534, inside the ≤ 0.55 band with 3 % headroom.** The
scale factor §1.11 asks for computes to **1.000 on all 40 (asset × material) pairs**, and the
loader reports `0 albedo-scaled`.

Two riders on the same table. (i) `plastic_base_Diffuse.png` measures **0.841 raw with 99.15 % of
pixels over cap** and binds **53.2 – 71.2 %** of the triangles on four of the eight buildings —
the largest near-white surface in the tier — yet it appears in **no** near-white WARN. The gate
that produced the WARN list missed the biggest instance of what it was looking for. Its
effective albedo (0.019 / 0.138) is nonetheless the safest in the tier, so nothing is at risk;
the *instrument* is what needs the note. (ii) `MI_Building_Wall_04`'s brick at effective 0.074 is
the tier's dark extreme — an override computed on raw values alone would have left it untouched
while darkening its neighbour, splitting one facade into two exposure families.

### 3.3 The tier's real material defect is metallic, not albedo

Every SimPBR material in the tier authors `metallic_constant = 1.0` with
`metallic_texture_influence = 0.0`, and `SimPBR.mdl:792` evaluates
`metallic = lerp(metallic_constant, ORM.z, influence)` — with influence 0 that is **1.0**
`[measured]`. All eight skyline buildings therefore render as **fully metallic** walls, roofs and
walkways at roughness 1.0. A metal BSDF has no diffuse lobe, so "scale the albedo" cannot reach
the surface the ruling is aiming at; `base_color` acts as the metal's reflectance instead.

The mid tier does **not** share the defect: `metallic_constant` is unauthored on all ten
`typical_building_*` (MDL default 0.0), with a single exception,
`typical_building_12/opaque__concrete__tower_02`, which drives metallic from a texture at
influence 1.0 `[measured]`. **This is a far-tier-only quirk**, and it is a second, independent
reason C-25's "asset backdrops must still be dressed" is right.

### 3.4 What the loader does, and what it needs ruled

The override is implemented and is **not vacuous**: for each far-tier source material that binds
a diffuse texture it authors one shared OmniPBR override under `/World/Looks/UrbanFar/`, which

- **keeps** `diffuse_texture`, `normalmap_texture`, `reflectionroughness_texture` and the source
  `reflection_roughness_constant`, with `project_uvw = False` so the asset's own UVs are used
  (a world projection would smear a 60 m facade);
- **scales** `diffuse_tint` by `min(1, 0.55 / effective)` — factor 1.000 today, so the authored
  tint is carried through unchanged;
- **sets** `metallic_constant = 0.0`, which is what a plaster/concrete facade is, and what
  binding *any* override material implies anyway (OmniPBR's default).

Both arms are exposed for the gate §1.11 requires: `far_override="auto"` (default) and
`far_override="off"`. §1.11 re-gates every far-tier binding change on **B45/B30**, not only
B-HZ, because survey R3 §4.2 measured Δσ_LF **−0.32** ≈ 4× the noise floor on `h0.9_d5`.

> **Ruling requested.** §1.11's stated target — "scale the albedo into the ≤ 0.55 project band"
> — is already met by the shipped material, so the albedo arm of the override is a no-op. The
> override as implemented still changes the tier (metallic 1.0 → 0.0). Confirm that this is
> wanted, or set `far_override="off"` library-wide and re-open the metallic row separately.
> **The 0.5 – 1.1 m boulder band stays unfilled** and is still an open procurement row (§1.11).

---

## 4. F-B — the Z origin (§3.4-1)

### 4.1 The two cited authorities contradict each other

§3.4-1: *"Use the manifest's per-asset `z_advice`; the 28 props that genuinely need `−zmin` are
listed there."* Distribution of the field over all 276 rows that have geometry `[measured]`:

| `z_advice` branch | rows | what it says |
|---|---:|---|
| `zmin ≈ 0 — 접지 보정 불필요` | 227 | no correction needed |
| `**Z 보정 금지**(올리면 파사드가 뜬다)` | 46 | correction **forbidden** |
| `**부속물**이다 … 단독 접지 금지` | 3 | attachment, never grounded alone |
| `접지 시 +N m 올릴 것` | **0** | *the branch §3.4-1 points at* |

The lift branch exists in `assets/verify_urban.py:363-366` but never fires, because its predicate
is `tri_below_grade_frac ≥ 0.25` and that fraction is computed **per mesh, all-or-nothing**:

```python
below = sum(t for zlo, zhi, t in mesh_z if zhi < -0.05)   # verify_urban.py:346
```

A mesh counts only when its **top** is below grade. For every single-mesh prop — `bollard_01`,
`utility_cover_01`, `luminaire_head04`, `old_tyre`, `tree_stump_01/02`, `stone_01` and 20 more —
the fraction is structurally **0.0000**, so the *"Z 보정 금지"* branch fires regardless of the
truth. The metric was designed for the mid-tier buildings, where the foundation genuinely is a
separate mesh, and it silently generalises to props where one mesh spans grade. PROC §5.1's
prose row ("28 props … lift by `−zmin`. Full list in the manifest's `z_advice` field") is
therefore pointing at a field that says the opposite.

### 4.2 Neither authority can be applied blind

- Applying **PROC §5.1's prose** would lift `utility_cover_01` by +0.327 m. That asset measures
  `zmax +0.028 / zmin −0.327` `[measured]` — its origin *is* the road surface and the vault hangs
  below it. The prose would hoist a utility vault out of the road, and `utility_cover_01` is the
  first example the row names.
- Applying the **`z_advice` field** would leave `old_tyre` (50.0 % of its triangles below its own
  origin), `tree_stump_02` (47.5 %), `rock_moss_set_01` (52.4 %) and `power_box_01` (37.8 %) half
  buried — the exact defect `scene_common.py:2296-2300` already documents for the S3 rock family
  ("the origin is the *centre* of the rock, so placing it directly at the ground z buries half of
  it").

### 4.3 What the loader does

Default `z_mode='grade'` — local z = 0 lands on the caller's ground z, **no lift**. This is the
ruled behaviour for the mid tier (C-18) and is trivially correct for the 227 rows whose zmin is
already ≈ 0. `z_mode='base'` lifts by `−zmin`; `z_mode='attach'` refuses to auto-ground the three
mounted rows (`typical_building_08_railings` +11.000, `ac_unit_06` +0.149, `bridge_01` +0.025).

Every row whose origin is measurably inside its own body prints a one-line advisory naming both
numbers and the alternative call, once per process. **20 rows trip it** at the 0.15 threshold —
chosen because it sits above every mid-tier building (max 0.0512) and every buried-anchor row
(max 0.0479), and below the centre-origin scans it is meant to catch (min 0.1750):

| id | frac below own origin | zmin (m) | reading |
|---|---:|---:|---|
| `luminaire_head02` / `04` / `_01` / `01` / `03` | 0.8628 / 0.7809 / 0.7630 / 0.7474 / 0.6562 | −0.207 … −0.060 | **mount-point origin** — the head hangs below its bracket. Never grounded; C2's hybrid mounts it on our own pole |
| `luminaire_arm_6ft` / `8ft` / `10ft` | 0.2809 / 0.2638 / 0.2616 | −0.077 | same class — bracket arms |
| `security_light` | 0.7215 | −0.359 | wall bracket origin |
| `sidewalk_debris_02` / `_01` | 0.5665 / 0.2242 | −0.027 / −0.034 | centre origin — scatter, `z_mode='base'` |
| `rock_moss_set_01` · `old_tyre` · `tree_stump_02` · `tree_stump_01` · `power_box_01` · `stone_01` | 0.5238 · 0.5000 · 0.4753 · 0.3887 · 0.3778 · 0.1936 | −0.661 … −0.015 | centre origin (the `VEG_ROCKS` class) — `z_mode='base'` |
| `modular_fire_escape` · `lateral_sea_marker` | 0.2455 · 0.1750 | −3.649 · −1.282 | needs eyes; both are mounted assemblies |
| `utility_cover_01` | 0.2429 | −0.327 | **keep at grade** — the cover is at grade, the vault below |

Below the threshold and therefore silent, but worth naming because they are the rows the
briefings argue about: `bollard_01` **0.0343** / −0.183, `strt_fxd_bollard_05` **0.0479** /
−0.054, `streetlamp_01` **0.0303** / −0.385, `streetlamp_02` **0.0086** / −1.000,
`pole_fxd_pedestrian_signage_01` **0.0134** / −0.122. All five are **buried anchor stems**, which
is what a real Korean bollard and lamp post have. Grade is right for them.

> **Ruling requested.** Confirm `z_mode='grade'` as the library default and let each S-WP raise
> `z_mode='base'` per call for the centre-origin scans, **or** publish a per-asset table. What
> may not stand is §3.4-1's current wording, which sends implementers to a field that has no
> lift rows in it.

### 4.4 Consequence for C6 (bollards)

§3.1 C6 measures `bollard_01` at **139 × 1003 mm** and calls both dimensions in spec against
교통약자법 시행규칙 별표2 제7호 (h 0.8–1.0 m, Ø 0.1–0.2 m). The 1003 mm is the **bbox** height;
**820 mm of it is above the asset's own origin and 183 mm below** `[measured]`. So the exposed
height is a function of the z decision, not of the asset:

| asset | bbox h | exposed at `grade` | exposed at `base` | statute 0.80 – 1.00 m |
|---|---:|---:|---:|---|
| `bollard_01` | 1003 mm | **820 mm** | 1003 mm | both in spec |
| `strt_fxd_bollard_05` | 845 mm | **791 mm** | 845 mm | grade is **9 mm under** the minimum |
| `strt_fxd_bollard_03` | 721 mm | 721 mm | 721 mm | under the minimum — the intended non-compliance variant |
| `scene_common.build_bollard` (current) | 750 mm | 750 mm | — | 6.3 % under, as C6 states |

`strt_fxd_bollard_05` at grade lands **791 mm**, i.e. 1.1 % below the legal 800 mm — it becomes a
second non-compliance variant rather than the compliant one C6 selected. At `base` it is
compliant at 845 mm. **This single row decides whether C6's asset flip delivers one compliant
bollard or two non-compliant ones**, and it must be settled before K4(c) writes the prop
template. `bollard_01` is safe either way.

---

## 5. F-C, F-D and the rest of §3.4

### 5.1 F-C — `_inst.usd` drops the emissive night rig (quirk 2)

C-25's stated reason for quirk 2 is "the wrapper composes to **504** triangles; `_inst.usd`
composes to **21,965**". Measured, that comparison is a traversal artefact, and the real
difference runs the other way `[measured]`:

| asset | wrapper, `stage.Traverse()` | wrapper, instance proxies | `_inst.usd` | manifest |
|---|---:|---:|---:|---:|
| `typical_building_10` | **504** | **22,469** | 21,965 | 21,965 |
| `typical_building_08` | 13,320 | 25,429 | 12,109 | 12,109 |
| `typical_building_11` | 554 | 133,118 | 132,564 | 132,564 |
| `bollard_01` (prop) | **0** | 2,564 | 2,564 | 2,564 |

The wrapper composes to *more*, not less; 504 is what a plain `stage.Traverse()` can see past the
wrapper's instanceable prim, and on a prop it sees **0**. The manifest's own triangle numbers are
already the `_inst` numbers, so quirk 2 and the manifest agree.

**What the wrapper carries that `_inst.usd` does not is the night-lighting rig.** On all ten
mid-tier buildings the wrapper-only geometry binds `opaque__emissive__*` materials `[measured]`:

| asset | wrapper-only tri | emissive materials |
|---|---:|---|
| `typical_building_08` | 13,320 | `lights001` |
| `typical_building_07` | 3,720 | `lit001` |
| `typical_building_12` | 2,564 | `light01`, `light02`, **`shops`** |
| `typical_building_109` | 1,172 | `lights_001`, `lights_002`, **`beacon_01`** |
| `typical_building_11` | 554 | `light01` |
| `typical_building_10` | 504 | `light01`, `light02` |
| `typical_building_03` | 360 | `light01` |
| `typical_building_13` | 120 | `light01`, `light02`, `light03` |
| `typical_building_106` | 56 | `light001` |
| `typical_building_18` | 22 | `light01`, **`sign`** |

The far tier loses nothing (wrapper and `_inst` compose identically on all 8).

For a daylight library this loss is the right default — night scenes are out of scope since
07-27 — and quirk 2 is implemented as written, with no opt-out. Two rows are worth a second look
before N-A5 / BS-1…BS-6 are cut: `typical_building_109`'s **`beacon_01`** is an aviation
obstruction light on a 135 m tower, a physically present daytime object on the tallest backdrop
building; and `typical_building_12`'s **`shops`** emissive is a shopfront band. Both would have to
be rebuilt procedurally if a scene wants them, which is the project's default posture anyway
(§3.4-7: the backdrop must be dressed regardless).

### 5.2 F-D — three vegetation rows are PointInstancers

`[measured]`, and the manifest agrees once `protoIndices` are expanded:

| asset | instances | unique tri | **effective tri** | ratio |
|---|---:|---:|---:|---:|
| `veg_shrub_hedge_green_01` | 122 (4 instancers) | 20,894 | **758,206** | 36.3× |
| `veg_shrub_hedge_round_01` | 491 | 15,182 | 788,840 | 52.0× | 
| `veg_shrub_hedge_yellow_01` | 5 | 16,116 | 80,580 | 5.0× |

§3.2 promotes `veg_shrub_hedge_green_01` as "the right asset for the h 1.6–2.0 m belts that
`build_hedge` is mis-modelling". It is — and it costs **758 k effective triangles per belt
segment**, against `typical_building_10`'s whole 21,965. §12-14 rules that instanceability, not
triangle count, is the budget, and this row is instanced by construction, so it is admissible.
But nobody may quote 20,894 for it. `veg_shrub_hedge_round_01` is refused by the loader anyway
(season FAIL, C-21).

### 5.3 A-1 — a new alias trap: `bench_park_01` is rotated 90°

C-26's three aliases all verify (`bench_park_01` → `bench_park_03`, `bench_park_05` →
`bench_curved_01`, `concrete_block_02` → `concrete_block_01`) and the loader resolves each to the
target's `_inst.usd`. But the alias wrapper is not a pure pass-through `[measured]`:

| asset | size (mm) | triangles |
|---|---|---:|
| `bench_park_03` | 1735 × 1149 × 1325 | 35,396 |
| `bench_park_01` | **1149 × 1735** × 1325 | 35,396 |

Same geometry, **X and Y swapped** — the wrapper applies a 90° yaw. §3.1 C1 quotes
"`bench_park_03/_01` 1735 × 1149 × 1325" for both. The depth verdict (1.149 m against the Korean
등벤치 0.540 m, **2.13×**) is unaffected and C1's CONFIRM rebuild stands. But a scene that copies a
yaw between the two ids gets a bench across the path instead of along it. Both are rebuild rows,
so nothing ships from this today; it is recorded so the A/B control at the gate is not read
upside down.

### 5.4 Quirk 5 — dead references

**240 exactly**, matching §3.4-5 `[measured]`. All of the form
`<asset>/materials/textures/<name>.png`, all shadowed by the `_inst` layer's winning value, none
resolved by the loader. `typical_building_18` carries 23 of them, of which the genuinely dead
upstream one is `shared_textures/concrete_01_albedo.png` (C-24) — confirmed absent on disk while
the other 22 are the normal inner-layer paths.

---

## 6. §3 re-adjudication — status of every row the spec names

Every id below resolves through the loader and reproduces the spec's measurement unless a
correction is noted. Full table: `python3 urban_kit.py --sheet`.

### 6.1 §3.1 — the 20 R2 rows

| row | verdict in spec | loader status |
|---|---|---|
| **B1a** hedge crowns | CONFIRM rebuild | `veg_shrub_hedge_green_01` 5795 × 3306 × 1924 mm **reproduced**; the 3.3 m depth against a Korean 0.6–1.2 m 생울타리 stands |
| **B2d** scene15 pots | FLIP container | `planter_pot_clay` 266 × 264 × 222 mm · `Barrel_01` Ø563 × 880 — both load |
| **C1** bench | CONFIRM rebuild | all five candidates load; `bench_park_01` axis swap recorded (§5.3); `painted_wooden_bench` 1165 × 496 × 889 reproduced |
| **C1b** D4 platform bench | CONFIRM rebuild | no candidate in the manifest — negative confirmed |
| **C2** streetlight | FLIP to HYBRID | all 5 heads + 3 arms + 3 poles load, **every dimension reproduces** (head03 1009 × 216 × 98 / 256 tri · arm 6/8/10 ft = 1838 / 2448 / 3057 mm · streetlamp_01 3291 · _02 6215 · _03 7072). Heads and arms are mount-origin assets — §4.3 |
| **C3** litter bin | rebuild plaza / asset alley | `trashcan_cylinder_01` Ø722 × 1041 · `trashcan_square_01` 586 × 796 × 1011 · `metal_trash_can` 1847 × 556 × 906 — all reproduced |
| **C4** pergola | CONFIRM rebuild | negative confirmed — no canopy asset in the manifest |
| **C5** planter | SPLIT | `planter_lrg_01` 1500 × 1500 × 700 / 1,668 tri · `planter_round_01` Ø1002 × 988 / 728 tri — reproduced |
| **C5b** 수목보호판 | CONFIRM rebuild | negative confirmed |
| **C6** bollards | FLIP to asset | dimensions reproduce; **the exposed-height question in §4.4 is open** |
| **C7b** signage | SPLIT | 156 `sign_kr*` load, panel 2 mm thick, normal +X; `sign_krroadname` measures **499 × 119 mm** — small for a 도로명판, S-WPs should scale deliberately |
| **C7c** sign post | CONFIRM rebuild | `pole_fxd_pedestrian_signage_01` 373 × 373 × 2122 reproduced |
| **RF-1 / RF-2 / RF-3 / RF-5 / RF-6** | CONFIRM rebuild | negatives confirmed — nothing in the manifest fills them |
| **E2** D2 aggregate | FLIP partial | `rock_01` 316 · `rock_02` 463 · `rock_03_broken` 1714 mm reproduced |
| **E2b** rebar / bags / fence | CONFIRM rebuild | negative confirmed |
| **E3** D3 fence | CONFIRM rebuild | `modular_chainlink_fence` 8115 × 2149 × 2523 reproduced, 89,232 tri |

### 6.2 §3.2 / §3.3 — asset rows

All load: N-A1 **156** `sign_kr*` · N-A2 **9** `stencil_ko_*` (the arrow stencil measures
2793 × 17588 × **0** mm — a zero-thickness 17.6 m decal, so it is a projected mark, not a prop) ·
N-A3 `ac_unit_04/05/06` + `utility_box_01/02` + `power_box_01` · N-A4 the 8 far-tier at
`mpu 0.01` · N-A5 the 10 mid-tier via `_inst.usd` with **no Z lift** · N-A6 3 bike racks ·
N-A7 `rock_02` / `rock_03_broken`. C-27's three polycount corrections reproduce exactly
(`modular_urban_apartments_facade` **877,365** · `stone_01` 53,520 at **147 × 89 × 72 mm** ·
`concrete_road_barrier_02` 23,822). `ac_unit_06` is one of the three attachment rows (zmin
+0.149) and at 1039 × 2111 × 1475 mm it is still ~2.5× a Korean wall 실외기, consistent with
C-22's rejection of the whole `ac_unit_*` family for the facade role.

---

## 7. Carried forward

| id | row | owner |
|---|---|---|
| **T4-Q1** | §1.11: the albedo arm is a no-op (F-A). Confirm the override stays (metallic 1.0 → 0.0) or set `far_override="off"` | supervisor → X3 / the render gate |
| **T4-Q2** | §3.4-1's wording points at a `z_advice` branch that never fires (F-B). Confirm `grade` as the default | supervisor |
| **T4-Q3** | `strt_fxd_bollard_05` is 791 mm exposed at grade — 9 mm under the statutory minimum (§4.4). Decide before K4(c) writes the C6 template | supervisor → K4 |
| **T4-Q4** | `typical_building_109`'s rooftop beacon and `_12`'s shopfront band are lost with the wrapper (F-C). Rebuild or accept | K3 / S-WPs |
| **T4-Q5** | The near-white gate missed `plastic_base_Diffuse.png` (0.841 raw, 99.15 % over cap, up to 71 % of triangles). Instrument note for procurement — no action needed on the tier itself | procurement (informational) |
| **T4-Q6** | The 0.5 – 1.1 m boulder band is still unfilled (§1.11) | open procurement row |

---

## 8. Reproduction

```bash
python3 -m venv /tmp/usdvenv && /tmp/usdvenv/bin/pip install usd-core pillow numpy

/tmp/usdvenv/bin/python urban_kit.py --self-check     # 275 rows, load + traverse + place
/tmp/usdvenv/bin/python urban_kit.py --self-check --fast   # skips the Z_REVIEW re-measure
python3 urban_kit.py --sheet                          # the 275-row resolution table
python3 urban_kit.py --list                           # ids only

# floor (§6.1)
python3 -m py_compile urban_kit.py
python3 scripts/geom_invariance_check.py              # 33/33 unchanged — this WP touches no scene
```
