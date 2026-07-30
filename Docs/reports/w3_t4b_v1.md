# T4b — urban material wrapper: instancing **and** a scene-chosen material, and the MaterialX gap

> **Wave** W3 · **Lane** T4b (kit) · **Date** 2026-07-30
> **Branch** `feat/realism-v1` · **HEAD at start** `f39abe0` (verified live; the brief's
> `8bf7882` is four commits back — three GT-24 lane commits and one other lane's report
> landed in between)
> **Owned files** `urban_kit.py` · `assets/urban_wrap/*` · this report ·
> `Docs/reports/_w3_t4b_crops/*`. **No scene file is touched** — §4's revert recipe is
> written down, not applied, exactly as the dispatch requires.
> **Method** every number is re-executed, never re-read. Tree-wide gates run in isolated
> `git archive` arms at pinned HEAD `f39abe0` (seven other lanes share this worktree and it
> was dirty with `Docs/reports/w3_mb_patch_v1.md`, `look_check/README.md` and
> `Docs/reports/_w3_sb_crops/` throughout). All GPU work under
> `flock -w 7200 /tmp/negobs_gpu.lock`, `PT_FAST`, one channel for every arm. No humans,
> no vehicles.

## 0. Verdicts

| item | verdict | one-line basis |
|---|---|---|
| **MD-F2** — instancing + chosen material | **LANDED** — `urban_kit` §[8b] `asset_wrapper()` + `add_urban_asset(..., treatment=)` | 10 placements, `IsInstance()` **10/10**, **5 prototypes for 5 (asset, treatment) pairs**, no scene-side binding anywhere |
| **MD-F3** — the MaterialX gap | **CLOSED, and re-scoped** | not one asset: **all 33 Poly Haven CC0 rows, 50 materials** carry `ND_normalmap_float` `[measured]`. Red-fallback **9.02 / 11.09 / 18.53 % → 0.00 / 0.00 / 0.00 %** on three cuts, `cannot find SdrNode` **4 → 0** |
| **the route** | **corrected against the proposal, on measurement** | MD-F2's sketch binds on the wrapper's root prim. Measured: a property on the wrapper root composes onto the **instance prim**, not into the prototype, and the bind is inert. The asset hangs under `Root/Geom` instead — §1.2 |
| **two treatment kinds** | both work, `mtlxoff` is the default | on **identical geometry under identical light**, `mtlxoff` (keeps the asset's normal map) carries **+17.7 % / +4.4 % gradient energy** over the normal-free OmniPBR `scan` arm and reads 2.2–7.7 LSB darker; frame-wide the two differ by **1.13 LSB** |
| **geometry** | **unchanged, vertex-exact** | 31,548 transformed points, world bounds identical to **1e-6 m** across raw / `mtlxoff` / `stone_moss`; tree-wide `geom_invariance` output **byte-identical** between arms |
| **FU-1 revert recipe** | **recorded, not applied** | scene07's 30 binds are **art, on 3 NVIDIA assets with no MaterialX gap at all**; scene10's four are **one workaround + three art** — §4 |
| **§6.1 floor** | **green** | py_compile ✔ · self-check **275 rows, 0 problems** · `geom_invariance` unscoped **R-4 33/33 · R-6 33/33, byte-identical A vs B** · `placement_lint --scenes scene07,scene10` **byte-identical** · `NEGOBS_SMOKE=1` rc 0 on both scenes |

---

## 1. What landed

### 1.1 The two defects, and why one module closes both

`w3_md_reverts_v1.md` §1.5 handed on **MD-F2**: a scene that wants its own material on an
urban asset must bind it from the scene, and a scene-side binding cannot reach inside a
prototype — so scene07 (30 kerb boulders) and scene10 (4 outcrops) both pass
`instanceable=False`. The FU-1 arm reverted that and lost the look; the report's conclusion
was that the fix is *"the urban twin of K4(0)'s `sc.veg_wrapper_rel`"*, not a revert.

**MD-F3** is the second half: `rock_moss_set_01` binds a MaterialX material whose
`ND_normalmap_float` node is missing from this runtime's Sdr registry, so instancing it
returns the red error fallback. `ensure_mdl_package()` (section [1b]) completes the `.mdl`
package and cannot touch a MaterialX node definition — different subsystem, different gap.

Both are the same shape of problem — *an opinion that has to live inside the prototype* —
so both are closed by the same device:

```
add_urban_asset(stage, path, "rock_moss_set_01", ..., treatment="mtlxoff",
                instanceable=True)
```

`urban_kit.asset_wrapper(asset_id, treatment)` authors (on demand, atomically) a wrapper
layer `assets/urban_wrap/<asset>__<treatment>.usda` that references the asset and carries
the opinion. The wrapper is a normal composition, so the opinion composes; the scene then
references **the wrapper** and instances that, so the opinion is already inside the
prototype. `assets/urban_wrap/` sits deliberately outside the gitignored `assets/urban/`
(NVIDIA) and `assets/urban_cc0/` (size) trees — one relative reference, a few `over`s and
at most one material, so the layers are trackable while the geometry stays procured. That
is `assets/veg_bare/`'s arrangement, for `assets/veg_bare/`'s reason.

**Naming, deliberately not MD-F2's.** The proposal calls it `asset_wrapper_rel`. The
vegetation twin returns a *relative* path because `add_vegetation` joins it onto `VEG_DIR`;
`add_urban_asset` composes the absolute path `resolve_usd()` hands it, so a "rel" return
here would be a parallel with nothing to join to. The function is `asset_wrapper()` and
returns an absolute path.

### 1.2 The trap the proposal walks into — measured, and routed around

MD-F2's sketch is *"an `over` binding into a per-(asset, material) wrapper"*, which reads
as: reference the asset on the wrapper's root prim and bind the material there. **That does
not work, and it fails silently.** The first cut of this section did exactly it. Measured
on usd-core 26.8:

| where the binding was authored | inside `/__Prototype_1` | what the 6 meshes resolved to |
|---|---|---|
| wrapper's `Root` (= the instance prim) | **no `material:binding` at all** | the asset's own material — the bind is inert |
| wrapper's `Root/Geom` (a prim *inside* the prototype) | present | `/__Prototype_N/WrapLooks/Mtl` on **6/6** |

USD shares an instance root's *children*; the instance root's own properties stay on the
instance, and material resolution for a prim inside a prototype does not walk out of the
prototype. So a binding on the wrapper root is the same failure as the scene-side binding
it was supposed to replace, one namespace level further in. Both treatment kinds therefore
put the reference under `def Xform "Geom"` and author there, and the composed path for a
treated asset is `<prim>/Asset/Geom/…`. Both kinds use the same shape so a scene can change
treatment without its composed paths moving.

This is the same class of defect as K4(0)'s **F1** (`SetActive(False)` on a descendant of
an instance, which reported success and rendered green leaves): an authored opinion that
composition discards. It is recorded here because the next reader of MD-F2 would otherwise
implement the proposal as written and get a wrapper that changes nothing.

### 1.3 The registry

A **treatment is a look decision, not an asset fact**, so it is registered once and applies
to any asset that has what it needs. Two kinds:

| kind | what the wrapper carries | portability |
|---|---|---|
| `mtlx_off` | blocks the material's `outputs:mtlx:surface` connection (`.connect = None`), so the renderer falls back to the **`outputs:surface` UsdPreviewSurface** terminal the same material already carries — the asset's own diffuse, roughness **and normal** | no material authored, no absolute path — byte-portable |
| `omnipbr` | one OmniPBR material from the asset's own texture set (`ASSET_TEXTURES`) plus the treatment's tint / roughness / metallic, bound `strongerThanDescendants` | names the local `OmniPBR.mdl`; self-heals (§1.4) |

`mtlx_off` is only safe because **every one of the 50 CC0 materials also carries a
UsdPreviewSurface terminal** — re-measured, not assumed, and the self-check FAILs if any
material ever has a MaterialX terminal without the fallback.

Shipped treatments: `mtlxoff` · `scan` (neutral tint — the MDL arm of the MD-F3 repair) ·
`stone_moss` / `stone_mid` / `stone_dry` (scene07's own measured `PARAMS["stone_mtl"]`
tints, `scene07:257-258`) · `rockface` (scene10's `rockface_tint`, `scene10:645`). The
stone tiers carry the scenes' shipped numbers rather than new ones invented here, so §4's
recipe is a migration and not a re-design.

**Normal-free on purpose, for the `omnipbr` kind** `[measured]`. The CC0 sets ship
`*_nor_gl_*` — OpenGL green convention — while this project feeds OmniPBR `*_nor_dx_*`
throughout. A GL map in a DX slot lights every crevice from the wrong side, which is worse
than no normal. `use_normal=True` exists for a set that ships DX and is **off on every
shipped row**; §3.3 measures what it costs.

**Multi-material rows are refused, not flattened.** One wrapper material bound
`strongerThanDescendants` over `modular_urban_apartments_facade`'s five materials would
collapse five looks into one. `omnipbr` returns `None` for those rows and the caller falls
back; `mtlxoff` handles them fine (it blocks all five terminals and keeps five looks).

### 1.4 Two things that could have made this un-committable, and what was done

**A machine-specific path in a tracked file.** An `omnipbr` wrapper names the absolute
`OmniPBR.mdl` — the same absolute path `scene_common.py` and `urban_kit.py` already
hard-code. The layer carries a `customLayerData` stamp of its *content identity* (format,
asset, treatment, registry parameters) that deliberately **excludes** that path, and
`asset_wrapper()` rewrites the file only when (a) the stamp no longer matches the registry,
or (b) an asset path the file names does not resolve on this machine. A checkout on this
machine leaves the tree clean; a checkout on a machine with Kit elsewhere self-heals on
first use.

**A gate that dirties the tree it gates.** `self_check()` exercises all **45** (asset,
treatment) pairs. Writing 45 files into a tracked directory on every self-check would make
the gate a source of noise, so `NEGOBS_URBAN_WRAP` redirects the authored layers and the
self-check points it at a temp dir. Only the pairs a scene actually references belong in
the repo; **7 are committed** (the 6 the rendered arms used, plus
`rock_moss_set_01__stone_moss` as §4's worked example), and everything else authors on
demand.

---

## 2. MD-F3 is library-wide — the finding is bigger than the row that reported it

`[measured — this session, usd-core 26.8]` Every Poly Haven CC0 asset in the tree opens a
MaterialX branch that reaches an `ND_normalmap_float` node:

| | count |
|---|---|
| CC0 assets carrying an `outputs:mtlx:surface` terminal | **33 / 33** |
| materials across them | **50** |
| of those, materials that also carry `outputs:surface` (the safe fallback) | **50 / 50** |
| NVIDIA `nv_content` rows affected | **0** — their materials are MDL, i.e. section [1b]'s business |

MD-F3 named one asset because one asset is all that is wired today (`scene10`'s outcrop,
masked by its per-mesh bind). `scene07` references `modular_wooden_pier`'s **textures**,
never its USD, so it is not a second live call site. **Every future CC0 call site renders
red**, which — with `props_kit`'s 16 builders and the C-series props now live — is a
standing trap rather than a historical one. The table is `MTLX_MATERIALS`, and self-check
step 7 re-measures it against the assets on disk, so a re-procured tree that renames a
material FAILs the gate instead of silently un-blocking the terminal.

---

## 3. Proof, under the GPU lock

### 3.1 The arms

One test stage (`scratchpad/t4b_probe.py`), 10 placements, all `instanceable=True`, on a
neutral grey ground under the project noon sky — **`rock_moss_set_01` plus three other
urban assets**, two placements each so prototype sharing is measurable:

| row | asset | supplier | treatment (wrap arm) |
|---|---|---|---|
| 0 | `rock_moss_set_01` × 2 | Poly Haven CC0 | `mtlxoff` |
| 1 | `rock_moss_set_01` × 2 | Poly Haven CC0 | `scan` |
| 2 | `tree_stump_01` × 2 | Poly Haven CC0 | `mtlxoff` |
| 3 | `tree_stump_02` × 2 | Poly Haven CC0 | `scan` |
| 4 | `rock_03_broken` × 2 | NVIDIA `rocks_gap` | none — the untreated control |

Three arms, same layout, same channel
(`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1`), all inside one
`flock -w 7200 /tmp/negobs_gpu.lock`: **`raw`** (no treatment anywhere — the defect),
**`wrap`** (the table above), **`swap`** (`mtlxoff` ↔ `scan` exchanged between rows, so the
two kinds can be compared on identical geometry).

Three cuts: `wrap_d3` (standing, whole stage), `wrap_h0.3` (the project's near-ground eye),
`rocks_close`.

**No `look_check/` round was created and no scene baseline was touched.** T4b owns no
scene; the frames live in scratch, exactly as T4's own probe did, so no directory can be
mistaken for a judgement round.

### 3.2 The repair

| arm | `cannot find SdrNode` in the log | `IsInstance()` | stage prototypes | wrapper refs |
|---|---|---|---|---|
| `raw` | **4** (`ND_normalmap_float`, ×1 per CC0 material in frame) | 10/10 | 4 | — |
| `wrap` | **0** | 10/10 | **5** (= the 5 (asset, treatment) pairs) | 8 — `mtlxoff` 4 · `scan` 4 |
| `swap` | **0** | 10/10 | **5** | 8 — `mtlxoff` 4 · `scan` 4 |

Red-fallback is the k1t4 metric, `R > 90 ∧ R > 1.8 G ∧ R > 1.8 B`:

| cut | mean `raw` | mean `wrap` | Δmean | **red `raw`** | **red `wrap`** |
|---|---|---|---|---|---|
| `wrap_d3` | 167.26 / 159.80 / 168.17 | 156.58 / 161.94 / 166.81 | −10.68 / +2.14 / −1.35 | **9.02 %** | **0.00 %** |
| `wrap_h0.3` | 155.83 / 149.17 / 162.47 | 142.71 / 151.64 / 160.69 | −13.12 / +2.48 / −1.79 | **11.09 %** | **0.00 %** |
| `rocks_close` | 170.34 / 147.52 / 156.55 | 148.27 / 152.13 / 154.17 | −22.06 / +4.61 / −2.38 | **18.53 %** | **0.00 %** |

The delta's signature is MD's §1.4 signature run backwards — red down, green up — which is
the shader-error fallback leaving.

Per asset group, on the `wrap_h0.3` frame (boxes in `scratchpad/t4b_crops.py`):

| region | red `raw` | red `wrap` |
|---|---|---|
| `rock_moss_set_01` · `mtlxoff` | **41.54 %** | **0.00 %** |
| `rock_moss_set_01` · `scan` | **34.21 %** | **0.00 %** |
| `tree_stump_01` · `mtlxoff` | **27.34 %** | **0.00 %** |
| `tree_stump_02` · `scan` | **28.40 %** | **0.00 %** |
| `rock_03_broken` · untreated NVIDIA control | **0.35 %** | **0.00 %** |

The control is the point of the fifth row: the NVIDIA asset is unaffected in both arms
(its 0.35 % is a sliver of a neighbouring CC0 stump inside the box edge, not its own
shading), so the defect and the repair are both confined to the CC0 supplier.

**Crops.** `Docs/reports/_w3_t4b_crops/t4b_wrapper_before_after.png` — three cuts × raw |
wrap, same frame, red share printed on each tile.
`Docs/reports/_w3_t4b_crops/t4b_h03_zooms.png` — the five regions above at h0.3, raw over
wrap. In the wrap tiles the scans' own bedded albedo, moss and roughness are legible; the
stumps' bark and the `rock_03_broken` fracture face read normally.

### 3.3 The two treatment kinds, on identical geometry

`wrap` vs `swap` exchanges only the treatment kind — same asset, same position, same
rotation, same light. Frame-wide the two arms differ by **worst |Δmean| 1.133 LSB**
(`rocks_close` −0.48 / −0.61 / −0.84; `wrap_d3` +0.03 / +0.01 / −0.02), and red is
**0.00 %** in both. On matched rock-body patches (`rocks_close`, no ground, no sky):

| patch | treatment | mean RGB | mean \|∇\| |
|---|---|---|---|
| A | `mtlxoff` | 133.37 / 108.30 / 71.23 | **7.537** |
| A | `scan` | 139.10 / 115.29 / 78.89 | 6.401 |
| B | `scan` | 143.03 / 136.53 / 127.82 | 5.282 |
| B | `mtlxoff` | 140.82 / 133.72 / 124.21 | **5.516** |

Consistent in both directions: the normal-free OmniPBR arm is **2.2–7.7 LSB brighter** and
carries **4.4 – 17.7 % less gradient energy** — the asset's normal map is doing visible
work, and dropping it flattens the surface. `Docs/reports/_w3_t4b_crops/t4b_treatment_ab.png`
shows it directly: under `mtlxoff` the boulder holds its relief and moss micro-detail;
under `scan` the same pixels read waxier.

**Therefore `mtlxoff` is the default recommendation**, and `omnipbr` is for the case where
the scene wants a *chosen* look and not merely a working one. An earlier, unmatched
comparison of the two arms in the `wrap` frame alone suggested a larger difference; it was
comparing two different rocks of the set and is discarded — the `swap` arm exists because
that measurement was not admissible.

### 3.4 What the wrapper does not change, and the one caution

**Geometry: vertex-exact.** Transforming every mesh point of one placement to world space:

| arm | points | world min | world max |
|---|---|---|---|
| raw | 31,548 | (−0.762200, 0.616229, 0.000010) | (2.519133, 3.603687, 0.618922) |
| `mtlxoff` | 31,548 | identical | identical |
| `stone_moss` | 31,548 | identical | identical |

**One caution, measured, for whoever migrates a scene.** The extra `Geom` level changes how
`UsdGeom.BBoxCache` *accumulates* a bound. At yaw 0 the two arms return the identical box.
Under rotation the raw arm returns the union of the six individually-rotated sub-boxes and
the wrapped arm returns the rotation of the union — for `rock_moss_set_01` at yaw 37° and
`scale_mul` 0.35 the x-span goes **3.542 → 3.7011 m** and the y-span **3.252 → 3.6284 m**.
The wrapped figure is the arithmetically exact rotated AABB (3.7014 / 3.6288 from the
2.8018 × 2.4322 box), so the wrapper's box is the *conservative* one and the raw box was
the tighter approximation. **No vertex moves**; only a cached bbox does. The three tree-wide
instruments are unaffected — `geom_invariance` and `placement_lint` run on the fake-USD
harness and returned byte-identical output between arms (§5) — but a scene that derives an
obstacle or hazard box from `BBoxCache` on a rotated multi-mesh asset should re-read it
after migrating, and declare the move if it lands.

---

## 4. The scene07 / scene10 revert recipe — recorded, **not applied**

`urban_kit.py` and `assets/urban_wrap/` are this lane's files; `scenes/main/scene07*` and
`scenes/main/scene10*` are not, and both are byte-unchanged by this batch. This section is
the handover the dispatch asked for: **which binds are art, which are workaround, and the
exact migration if their owner wants it.**

### 4.1 Per bind — art or workaround

| scene | binds | assets | MaterialX gap? | classification |
|---|---|---|---|---|
| **scene07** `Kerb_*` (`scene07:2145-2178`) | 30 × ancestor `strongerThanDescendants` on the parent Xform, drawing `M["stone_moss"]` (2 variants) or `M["stone_mid"]` (3 variants) | `rock_03_broken` · `rock_02` · `rock_01` — **all NVIDIA `rocks_gap`** | **No.** Not one CC0 row in the pool | **ART, all 30.** FU-1 already measured it (+1.75 LSB on `side_slope` against a 0.04 LSB floor, red 0.00 % on both arms). The moss zone is §4.1-3's specified quantity; the code comment's *"two things are happening here and both are load-bearing"* is correct, and only the `instanceable=False` half is the workaround — **entailed by the bind**, not independent of it |
| **scene10** `Outcrop_0` (`scene10:2432-2444`) | per-mesh `Bind(M["rockface"])` | `rock_moss_set_01` — **CC0** | **Yes** | **WORKAROUND + art.** The bind is the only reason this scene is not rendering red today (FU-1's revert measured 0.02 % → **4.50 %**). Its tint half is a separate, surviving art decision |
| **scene10** `Outcrop_1..3` | per-mesh `Bind(M["rockface"])` | `rock_03_broken` ×2 · `rock_02` — **NVIDIA** | **No** | **ART only.** Since `ensure_mdl_package()` landed, the workaround function of these three is gone; what remains is `rockface_tint (0.80, 0.80, 0.78)`, i.e. *"jointless natural rock, greyed"* (`scene10:410-414, 645`). Dropping them is a look change, not a cleanup |

**The scene10 code comment at `:2426-2431` is right for the wrong reason, and the reason
matters.** It says the ancestor bind *"does not reach inside a prototype (measured — the
`s311b` probe still rendered the SimPBR fallback)"*. The conclusion is correct and §1.2
reproduces it from the composition side; the *cited* cause (the SimPBR/MDL fallback) was
fixed by `ensure_mdl_package()` and is no longer what the fallback in that scene is. Today
the fallback there is MaterialX. Any owner reading that comment as "MDL, therefore fixed by
T4" would revert and land the 4.50 % red MD measured.

### 4.2 The migration, if the owners want it

**scene10** — the smallest and the most valuable, because it is the one masking a live
defect:

```python
uk.add_urban_asset(stage, f"{ROOT}/Outcrop_{i}", aid, ...,
                   z_mode="base", scene="10",
                   instanceable=True, treatment="rockface")     # ← replaces the loop
# and DELETE the `for pr in Usd.PrimRange(ap): ... Bind(M["rockface"])` block
```

`treatment="rockface"` is already registered with `scene10:645`'s own tint. Effects, all of
which the owner must round: the per-mesh bind's world-projected `make_pbr` material is
replaced by an asset-UV OmniPBR one (a **look change**, not a null edit); 4 placements
become 3 prototypes (`rock_moss_set_01`, `rock_03_broken` ×2 shared, `rock_02`); the
`rock_moss_set_01` MaterialX network is blocked inside the prototype instead of merely
being unbound. §3.4's BBoxCache caution applies to `Outcrop_0` (multi-mesh, yaw 22°).

**scene07** — bigger, and it is a look decision before it is a mechanical one:

* the tier materials are `make_pbr` **world-projected** with per-variant UV offsets and
  `tint_jit` 0.06; a wrapper material samples the asset's own UVs. The pilot's own note
  says world projection smeared `rock_moss_set_02` into a *"wet-plastic sheet"* on a
  rounded boulder, so asset UVs are arguably the better answer — but that is the scene
  owner's round to run, not a kit claim;
* the pair count: the smoke census measures **30 boulders at 0.767 moss coverage = 23 moss
  / 7 mid**, over 3 assets, so at most **3 × 2 = 6** moss pairs and at most 7 distinct mid
  pairs — **≤ 13 wrappers in practice, 15 in the worst case**. This corrects MD-F2's
  estimate of *"~2 tiers × 3 assets = 6 prototypes"*, which counted one variant per tier
  where the scene ships 2 and 3;
* what is bought: 30 non-instanced placements of 3,104 / 4,758 / 9,832 triangles collapse
  to ≤ 13 shared prototypes, which is §12-14's rule (*"triangle count is not the budget,
  instanceability is"*) honoured for the first time in this scene;
* what is **not** owed: nothing. FU-1 is a refusal that stands. This is an offer, and it
  needs a judged round on `260731_w3_s07` before it lands.

**Neither migration is authorised by this report and neither is started.** Both need their
scene's GT class declared first (a material-only change with the projection moving is an
R-3, and the BBoxCache note may make it an R-1 for scene10's `Outcrop_0`).

---

## 5. §6.1 floor

Isolated `git archive` arms at pinned HEAD **`f39abe0`** — arm A = archive, arm B =
archive + this lane's `urban_kit.py`; `assets` symlinked into both:

```
python3 -m py_compile urban_kit.py                                     ✔ (both arms)
/tmp/usdvenv/bin/python urban_kit.py --self-check                      ✔ PASS — 275 rows, 0 problems
python3 scripts/geom_invariance_check.py   (unscoped, both arms)       ✔ R-4 33/33 · R-6 33/33,
                                                                          output BYTE-IDENTICAL A vs B
python3 scripts/placement_lint.py --scenes scene07,scene10 (both arms) ✔ scene07 prims=1420 ·
                                                                          scene10 prims=2777,
                                                                          output BYTE-IDENTICAL A vs B
NEGOBS_SMOKE=1 python3 scenes/main/scene07_temple_stone_path.py        ✔ rc 0
NEGOBS_SMOKE=1 python3 scenes/main/scene10_park_deck_switchback.py     ✔ rc 0
```

The byte-identical `geom_invariance` and `placement_lint` outputs are the point, and they
are the same proof T4 published: **this lane changes no geometry anywhere in the tree.**

Self-check, with the three §[8b] steps added (the T4 §6.2 obligation extended to the
wrapper route):

```
[self-check] MDL package OK — added none (already complete)
[self-check] manifest rows 290 -> placeable 275
[self-check] mpu ok 275/275 · tri ok 275/275
[self-check] placed 275/275
[self-check] far-tier world height ok (8 rows)
[self-check] far-tier override bound on 63/79 meshes
[self-check] aliases + banned-path guard ok (275 paths, 16 patterns)
[self-check] Z_REVIEW 45 rows re-measured, drift 0
[self-check] MTLX_MATERIALS 33/33 rows re-measured (50 materials)
[self-check] wrappers 45/45 composed inside the prototype · prototypes 45 for 90 placements
[self-check] PASS — 275 ok, 0 problems
```

The three added assertions, in the order in which a wrong answer costs the most:

1. **`MTLX_MATERIALS` is re-measured against the assets** — a re-procured tree that renamed
   a material would otherwise leave a wrapper that composes and a frame that is still red.
   The step also FAILs if any MaterialX material ever lacks the `outputs:surface` fallback
   `mtlx_off` depends on.
2. **the opinion is checked *inside the prototype***, not on the stage — the MaterialX
   terminal must be gone there and the UsdPreviewSurface terminal must survive; for
   `omnipbr`, a mesh in the prototype must resolve to the wrapper's material. This is the
   assertion that would have caught §1.2 on the first cut.
3. **prototype sharing** — 45 pairs at 2 placements each must produce exactly 45
   prototypes.

---

## 6. Findings handed on

| # | Sev | Finding | Owner |
|---|---|---|---|
| **T4b-F1** | **HIGH** | **MD-F3 is library-wide**: all **33** CC0 rows / **50** materials carry `ND_normalmap_float`, not just `rock_moss_set_01`. Any new CC0 call site renders red unless it passes a `treatment=`. `props_kit`'s 16 builders and the C-series props are the exposure | every scene lane wiring a CC0 asset |
| **T4b-F2** | **MED** | `scene10:2426-2431`'s comment attributes its own workaround to the **MDL** fallback that T4 fixed. It is now MaterialX. An owner who reads it as "fixed upstream" and reverts lands FU-1's **4.50 %** red | scene10 owner |
| **T4b-F3** | **MED** | A property authored on a wrapper's **root** prim composes onto the instance, not into the prototype (§1.2). MD-F2's `asset_wrapper_rel` sketch, implemented literally, produces an inert wrapper. Same class as K4(0)-F1 | recorded here; no action |
| **T4b-F4** | **LOW** | The wrapper's extra `Geom` level changes `UsdGeom.BBoxCache` accumulation on **rotated multi-mesh** assets (+4.5 % / +11.6 % span at yaw 37°, in the conservative direction). Vertices unchanged; the fake-USD instruments are blind to it by construction. A migrating scene that derives obstacle boxes from `BBoxCache` must re-read them | scene07 / scene10 owners, at migration |
| **T4b-F5** | **LOW** | MD-F2's *"~6 prototypes"* estimate for scene07 counts one variant per tier; the scene ships `n_moss=2` / `n_mid=3`, so the real figure is **≤ 13** (15 worst case) | recorded here |
| **T4b-F6** | **INFO** | The `omnipbr` kind is **normal-free** because the CC0 sets ship OpenGL-convention normals into a DirectX pipeline. Measured cost: **4.4 – 17.7 %** of gradient energy and 2.2 – 7.7 LSB of brightness. If procurement ever converts the `_nor_gl_` maps, flip `use_normal=True` on the affected treatments and re-measure | procurement / future T-lane |
| **T4b-F7** | **INFO** | `assets/urban_wrap/` is a **new tracked asset directory**. It holds composition only (references + `over`s + one OmniPBR material), no third-party geometry or texture bytes, so it raises no redistribution question — the CC0 and NVIDIA trees stay gitignored and procured | licence audit, for the record |

---

## 7. Reproduction

```bash
# wrappers, composition and the self-check (CPU, usd-core 26.8)
/tmp/usdvenv/bin/python urban_kit.py --self-check          # 275 rows, 0 problems

# isolated arms for the tree-wide numbers (never the worktree — 7 lanes share it)
git archive f39abe0 | tar -x -C <arm>; rm -rf <arm>/assets; ln -s <repo>/assets <arm>/assets
cp urban_kit.py <armB>/urban_kit.py
( cd <arm> && python3 scripts/geom_invariance_check.py )                  # 33/33, A == B
( cd <arm> && python3 scripts/placement_lint.py --scenes scene07,scene10 )# A == B
( cd <armB> && NEGOBS_SMOKE=1 python3 scenes/main/scene07_temple_stone_path.py )
( cd <armB> && NEGOBS_SMOKE=1 python3 scenes/main/scene10_park_deck_switchback.py )

# GPU, three arms, one lock
flock -w 7200 /tmp/negobs_gpu.lock bash scratchpad/run_t4b.sh          # raw + wrap
flock -w 7200 /tmp/negobs_gpu.lock bash scratchpad/run_t4b_swap.sh     # swap

# adjudication
python3 scratchpad/imgcmp.py scratchpad/t4b_raw  scratchpad/t4b_wrap  RAW  WRAP
python3 scratchpad/imgcmp.py scratchpad/t4b_wrap scratchpad/t4b_swap  WRAP SWAP
python3 scratchpad/t4b_crops.py            # the three sheets + per-region red + |grad|
```

**Commits.** `urban_kit.py` + `assets/urban_wrap/*.usda` + this report +
`Docs/reports/_w3_t4b_crops/*` — pathspec-only, in one commit. `Docs/audit_v4/gt_changes_w3.md`
was **not** touched: this lane declares **no GT row** (no geometry, no walked surface, no
hazard box, no drop edge — §5's byte-identical `geom_invariance` output is that claim's
proof). `look_check/**` is untouched and no round was stamped.

**`scenes/main/scene07_temple_stone_path.py` and
`scenes/main/scene10_park_deck_switchback.py` are byte-unchanged across this batch**, which
is §4's verdict expressed in the tree rather than only in prose.
