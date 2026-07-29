# W2 `scene_common` Surgery — Report v1

Author: W2 scene_common surgeon · 2026-07-29
Branch: `w2-surgeon` · Worktree: `/home/vislab/Desktop/work_sy/Practice_NegObs_w2wt`
Base: `feat/realism-v1` @ `80e1301`
Specs executed: `Docs/briefs/t1_material_layer_spec_v1.md` v1.1 (§1.7, §1.8, §5, §6, T-1~T-4) ·
`Docs/briefs/lighting_camera_variation_spec_v1.md` (scene01 rows of §2.7 / §7)
Supporting: `Docs/briefs/ground_kit_spec_v1.md` §4.5 · §8.4 · §12 ·
`Docs/surveys/props_audit_w1/{A_trees_shrubs,B_groundcover_debris}.md` ·
`Docs/reports/leaf_globalization_budget_v2.md` §3-d · §6

**No GPU, no Isaac, no render, no SMOKE.** Everything below is static analysis, a MagicMock
assembly harness, and pixel/geometry figures read from `assets/veg_manifest_w2.json`
(produced by the parallel procurement agent with `usd-core`).

---

## 0. Result in one table

| Gate | Result | Where |
|---|---|---|
| **R-5** residual `LOOK_V1` references | **PASS — 0** outside the 3-line compat shim (39 files scanned) | §1.2 |
| **R-4** prim-inventory hash, `LOOK_MTL=0` vs `1` | **PASS — 33/33** | §2.3 |
| **R-6** three-way hash incl. `LOOK_V1=1` | **PASS — 33/33** | §2.3 |
| Harness assembly | **33/33 scenes** build under stubs, 27,251 prims, 13 s wall | §2 |
| Negative controls | both R-4 and R-6 **provably fail** on a seeded fault | §2.4 |
| `py_compile` | all 34 touched files | §6 |
| Merge dry-run vs live main tree | **1 trivial conflict** (`sceneN5`, same fix twice) | §7 |

8 commits, 34 files, +1,346 / −302.

---

## 1. LOOK flag split — `LOOK_V1` → `LOOK_MTL` / `LOOK_GEO`

### 1.1 What was done

`NEGOBS_LOOK_V1` moved geometry *and* materials at once, so "V1=0 vs 1" could never be a
material A/B — the two arms differed in prim count. That is the structural cause of the
critical-C3 control-group contamination that has recurred twice.

```python
LOOK_V1  = os.environ.get("NEGOBS_LOOK_V1", "") == "1"          # legacy super-switch
LOOK_MTL = os.environ.get("NEGOBS_LOOK_MTL", "1" if LOOK_V1 else "0") == "1"
LOOK_GEO = os.environ.get("NEGOBS_LOOK_GEO", "1" if LOOK_V1 else "0") == "1"
```

`LOOK_V1=1` still turns both on, so every existing invocation is bit-for-bit unchanged.

All 24 references of §1.7.1 were re-grepped at `80e1301` and matched the table exactly
(line numbers included). Substitution:

| Class | Count | Disposition |
|---|---:|---|
| comment / docstring | 8 | wording updated to `LOOK_MTL` / `LOOK_GEO` |
| META (definition) | 1 | kept — the compat shim |
| META (logging) | 2 | `look_report()` → `LOOK_MTL or LOOK_GEO`; `LOOK_STATS["skipped"]` → `LOOK_MTL` |
| **MTL** | 1 | `make_pbr` look-spec entry |
| **GEO** | 12 | displacement skin, railing height/spacing, balusters, handrail, tree USD, planter shrubs, window inset, **window-row cap `:2143`**, parapet height, **low-rise façade kit `:2187`**, scattered shrubs |
| scene files | 2 | `sceneC2:552`, `sceneN4:723` → `sc.LOOK_GEO` |
| kit comments | 2 | `facade_kit:33`, `building_kit:1635` |

The two references v1 had missed (`:2143` window-row cap, `:2187` low-rise façade kit) are the
dangerous ones: had they kept reading `LOOK_V1`, an A/B run that sets only `MTL`/`GEO` would have
seen `LOOK_V1=False` in **both** arms — the whole low-rise façade would silently vanish from all
24 `build_building` scenes and R-4 could not detect it (both arms equally wrong). R-6 exists
exactly for this, and §2.4 proves it fires.

`look_report()` now stamps `MTL=<0|1> GEO=<0|1>` into every round log, which is the audit trail
rule R-2 asks for.

### 1.2 R-5 evidence — residual references

`scripts/geom_invariance_check.py --assert-no-residual-lookv1`, tokenize-based
(`COMMENT` and `STRING` tokens excluded, so the incident history stays in the comments):

```
[R-5] 스캔 39 파일 · 허용 3 행(호환 심) · 위반 0 건
  · 허용 scene_common.py:182  LOOK_V1 = os.environ.get("NEGOBS_LOOK_V1", "") == "1"
  · 허용 scene_common.py:183  LOOK_MTL = os.environ.get("NEGOBS_LOOK_MTL", "1" if LOOK_V1 else "0") == "1"
  · 허용 scene_common.py:184  LOOK_GEO = os.environ.get("NEGOBS_LOOK_GEO", "1" if LOOK_V1 else "0") == "1"
[R-5] ✔ PASS — 호환 심 밖의 `LOOK_V1` 참조 0
```

Scope: `scene_common.py`, `facade_kit.py`, `building_kit.py`, `infra_kit.py`, `stair_kit.py`,
`ground_kit.py` (when present), `batch1_common.py`, and every non-symlink `scenes/*/*.py`
outside `archive_v3`. The allow-list is keyed on **file + count ≤ 3**, not on line numbers —
line numbers are a snapshot and parallel edits move them.

---

## 2. `scripts/geom_invariance_check.py` (new, 666 lines)

### 2.1 Method

`pxr` / `omni` / `carb` / `isaacsim` are replaced. Only `UsdGeom` and `Gf` are real: `UsdGeom`
is a **recording stub** whose `Cube/Cylinder/Sphere/Mesh/Xform/Cone/Capsule.Define` and whose
xformOp `Set` calls append to a per-scene prim inventory; everything else is `MagicMock`.
`sc.boot` / `capture_pipeline` / `ensure_noon_lookfix` / `check_assets` are stubbed out, and
each scene's `main()` runs down the `NEGOBS_CAPTURE=1` path, which assembles and returns just
before capture.

Recording at the **USD layer** rather than at `sc.add_box` is a deliberate upgrade over the
literal spec text: scene01 defines its own private `add_box`/`add_cylinder`/`add_sphere`
helpers, and `facade_kit` / `scene09` call `UsdGeom.Mesh.Define` directly. A `sc.add_box`
wrapper would have missed all of those. The net now catches every prim-creating path.

Recorded per prim: path, type, ordered xform ops (`T/S/RX/RY/RZ/RXYZ/Q/M` + value rounded to
1e-6), shape attributes (`size/radius/height/axis/extent`), a blake2b digest of
`points`/`faceVertexCounts`/`faceVertexIndices`, and referenced asset basenames. Rows are
sorted before hashing, so creation order cannot mask a difference.

One subprocess per arm (module-level flags are read at import), `PYTHONHASHSEED=0`, and
`random.seed(0)` before each scene so cross-scene ordering cannot leak into the global RNG.

### 2.2 Arms

| Arm | Env |
|---|---|
| `mtl0` | `NEGOBS_LOOK_MTL=0 NEGOBS_LOOK_GEO=1` — the R-2 control group |
| `mtl1` | `NEGOBS_LOOK_MTL=1 NEGOBS_LOOK_GEO=1` — the experiment |
| `v1` | `NEGOBS_LOOK_V1=1` — R-6 reference |

### 2.3 Result — 33/33, 33/33

```
[R-5] ✔ PASS — 호환 심 밖의 `LOOK_V1` 참조 0
[대상] 씬 33개
[실행] arm=mtl0 → 조립 33/33 성공 · flags {'LOOK_V1': False, 'LOOK_MTL': False, 'LOOK_GEO': True}
[실행] arm=mtl1 → 조립 33/33 성공 · flags {'LOOK_V1': False, 'LOOK_MTL': True,  'LOOK_GEO': True}
[실행] arm=v1   → 조립 33/33 성공 · flags {'LOOK_V1': True,  'LOOK_MTL': True,  'LOOK_GEO': True}
...
[R-4] MTL 0/1 해시 일치 33/33  ✔ PASS
[R-6] V1=1 3자 일치   33/33  ✔ PASS
```

Baseline written to `Docs/reports/geom_baseline_w2.json` (per-scene hash for all three arms +
prim counts, `repo_head` stamped). Total 27,251 prims. Wall time 13 s for all three arms.

### 2.4 Negative controls — the gates are not vacuous

Two seeded faults, both reverted afterwards (`grep -c` verified 0 residue):

| Fault | R-4 | R-6 | Interpretation |
|---|---|---|---|
| `par_h = 1.20 if LOOK_MTL else 0.5` (geometry mis-assigned to the material flag) | **FAIL 0/3** | PASS 3/3 | R-4 catches R-1 violations |
| `par_h = 1.20 if globals()['LOOK_'+'V1']` (a leftover `LOOK_V1` read, R-5-invisible) | PASS 3/3 | **FAIL 0/3** | R-6 catches the "both arms equally wrong" mode of §2.5 — the one R-4 is blind to |

That second row is the direct proof that R-6 covers the `:2143` / `:2187` failure class.

### 2.5 Honest limits

- The stub records what the code *asks USD to author*, not what USD would compose. Reference
  payload contents (tree/leaf meshes) are represented by the asset name only.
- `SetActive(False)` (seasonal flower removal) is not part of the hash; it is a prim-visibility
  edit applied identically in both arms, so it cannot bias an A/B, but the harness will not
  regress-test it. Called out rather than papered over.
- Primvar authoring is out of hash scope by design (spec R-4 note on `foot_z`).

---

## 3. Content wiring

Everything here is **outside** the `LOOK_MTL` gate — these are scene-file arguments and shared
ledgers that apply identically to both A/B arms. Per spec §7.2-7 they are before/after items,
judged by a re-render + `regression_check`, never by A/B. **All 33 scenes' pixels change.**

### 3.1 Vegetation ledger

| Item | Before | After | Evidence |
|---|---|---|---|
| `Japanese_Cherry` | weight 5 / 62.5 % | **deleted** | leaf texture green 0.0 % (blossom pixels); Seoul share ≈7 % vs 62.5 % weight = 9x over [A §5, §9] |
| new species | — | `Elm_Sapling` 4 · `Shumard_Oak` 3 · `Chinese_Juniper` 2 | manifest verdict PASS for all three |
| conifer/evergreen share | 37.5 % | **36.4 %**, broadleaf 63.6 % | Seoul top-2 (ginkgo 35.8 + sycamore 20.9 = 56.7 %) are both broadleaf and both unprocurable → surrogates |
| `native_h` basis | bbox total height | **`zmax` (above-ground)** for the 3 new rows | avoids repeating the White_Pine −15 % defect of A §6-c |
| `veg_available()` | "first row's file exists" | **any row exists** (`veg_pool()`) | deleting row 1 would otherwise have wiped vegetation from 30 scenes |
| `SHRUB_ORNAMENT` | Rhododendron, Burning_Bush, Forsythia, Juniper | **Rhododendron, Juniper** | Forsythia = flower-only texture (green 0 %); Burning_Bush = red 30.2 % autumn |
| Rhododendron flowers | on (76.7 % magenta) | `/Root/Flowers` **deactivated** before instancing | `strings` on the USDC confirms prims `Branches / Flowers / Leaves` |
| `VEG_SHRUBS` | 4-tuple, no height | **5-tuple with measured height** | A §6-b |
| `place_shrubs` scale basis | `target_h / native_WIDTH` | `target_h / native_HEIGHT` | aspect ratios span 0.607~1.973 → the old code produced −39 %~+97 % height error while its own docstring capped randomisation at ±8 % |

Weight split is tagged `[추정]`: the statistics give species shares, not surrogate-mapping ratios.

**Rhododendron ordering note.** `SetActive(False)` must precede `SetInstanceable(True)`; once
instanced, the descendants live in a shared prototype and the per-instance edit is ignored.
The code and an AST ordering check both enforce this.

### 3.2 `VEG_DEBRIS` — all five rows (B-audit A3)

`(0.0584, 9175) (0.0239, 2980) (0.0081, 631) (0.0048, 496) (0.0054, 582)`.
Triangle counts already matched; only effective coverage changed. Single-leaf rows were
under-estimated by 40~60 %, clusters over-estimated by 1~7 %. This moves `mean_cov` from
0.0435 to **0.04115**, which changes scatter counts everywhere `scatter_debris` runs.

### 3.3 Ground cover

- `TEX["grass"]`: `aerial_grass_rock` (15 m tile) → **ambientCG Grass001** = `grass_lawn_*`
  (1.40 m tile, CC0, green 98.25 %, linear albedo 0.0932, near-white 0 %). Pixel density
  273 → **2,926 px/m** (×10.7): 4~7 mm blades now resolve to 12~20 px.
- `scale=dict(grass=…)` unified to **1.4** in all 28 scenes that set it (was 4.0, plus scene10 at 2.6).
- `LOOK_CLASS["veg"]["tex_alts"]` → `("grass",)`; `leaf_ground` removed, plus `tex_scale=1.4`
  so the promotion path uses the same physical tile. This kills the 50 promotions across
  24 scenes that were painting **autumn-leaf pixels onto tree canopies** at 52 % scale.
- scene01's **private `TEX` registry** now delegates to `sc.TEX`. It was the last place naming
  `aerial_grass_rock_*`, so without this the Grass001 swap would have landed in 32 scenes and
  skipped scene01 — one scene at a 15 m tile while the rest moved to 1.4 m.

### 3.4 Tone T-1 + `scale_m` (9 scenes, one commit — they are one call)

`plaza_light` tint **×0.72** and `scale_m` **→ 1.80** are arguments of the *same*
`make_pbr` line, so splitting them across rounds would throw away the intervening render.

| Scene | material(s) tinted | `scale_m` before |
|---|---|---:|
| 01 | PlazaLight, PlazaLower | 0.75 |
| 05 | PlazaLight, Stage | 0.75 |
| 14 | PlazaLight | 0.8 |
| 16 | Stair | 0.75 |
| 18 | Upper | 0.75 |
| 19 | Upper, Step | 0.75 |
| 20 | Upper | 0.75 |
| 21 | Plaza | 0.8 |
| N3 | LightStone | 0.75 |

12 tint sites, 9 scale sites — grep tag `[T1 T-1]`. Physical basis: linear albedo 0.469 is in
the white-cement band; grey portland paving is 0.35~0.40 new / 0.20~0.30 aged, so ×0.72 → 0.338
lands at the low end of "new grey".

**`marble_light=1.2` in scenes 14 and 21 was left untouched** — it sits on the same `scale=dict`
line as `plaza_light` in scene21 and is a separate material axis. Verified by grep after the edit.

**Ordering caveat:** spec §8 note 2 wants the `scale_m` change rendered *after* the pilot A/B,
because a 2.25~2.40x texture-period change invalidates the §7.1 thresholds and §2.2 baselines.
The code change is landed now; **the render-order decision belongs to whoever schedules the round.**

### 3.5 Tactile paving — `tactile_yellow` wired at 11 call sites

`scene_common.tactile_pbr()` is the single implementation; `batch1_common.tactile_mtl()` is a
thin alias. Converted from constant colour: scene04, 07, 10, 18, 19, N1, N2, N3, N4, N5 (+ the
default material inside `build_bollard_v51`). The other 13 sites already used the texture.

The role key stays `tactile` and the files stay `tactile_yellow_diff/nor.png` — ground_kit and
the vegetation agent address them by that exact name. Measured: 1024 px, 36 dots (6×6), pitch
50.0 mm, linear albedo 0.4841, i.e. below the 0.55 clamp of §12.5-4, so no extra tint is applied.

A constant-colour fallback with a warning is kept because `assets/scene01/*` is git-ignored: a
missing binding renders black, which is strictly worse than the flat yellow it replaces.
Path token `...Tactile` maps to class `paint` (inviolable — OmniPBR, no MDL promotion, no
detail normal, bevel 0), verified through `_look_spec`.

**Open item for the supervisor** (from the manifest, not introduced here): dot diameter 38.1 mm
has no figure in the spec table, which fixes only count / pitch / height. Against the common
22~25 mm base it is 1.5~1.7x, raising dot area share from 19.6 % to 45.6 %, which works
*against* the §12.5-4 luminance-step goal. Geometry is untouched either way.

### 3.6 MDL `unit_cell` passthrough (contract §4.5 U1~U4)

`make_pbr(..., unit_cell=None)` → `_make_ground_pbr` → `_wire_unit_cell`. Accepts
`(cell_m, (ox, oy))` or `(cell_m, (ox, oy), sigma, accent)`; defaults `sigma=0.10`,
`accent=0.07` per §1.8-3.

**Default is `None` → nothing is authored → the shader is byte-identical.** The wiring exists,
the value injection waits on the ground_kit ledger (spec §8.1 P2).

Contract enforcement, self-tested without USD:

```
None            -> False   (no inputs authored)
(0.600,(0,0))   -> True    (unit_cell_m / unit_cell_origin / sigma / accent authored)
(0.600, None)   -> ValueError   U3: period without phase is not a contract
(0.0,(0,0),0.10)-> ValueError   U4: unmodular profile + jitter on
(0.0,(0,0),0.0) -> False   (explicit "no module", jitter off — legal)
```

U3 is raised rather than defaulted because the MDL's own grid origin is the **UV** origin, not
the scene origin: a matching period with a mismatched phase yields a half-cell offset seam
under the engraved joints, which is the exact double-grid artefact the contract exists to stop.

The live `assets/NegObsGround.mdl` (v1.9.0, from the parallel MDL agent) already declares
`unit_cell_m`, `unit_cell_origin`, `unit_albedo_sigma`, `unit_accent_frac` with the same names
and 0 defaults — the two halves of the contract match. My worktree still carries the tracked
v1.8.0 blob **unmodified**, so the merge keeps v1.9.0.

---

## 4. sceneC2 leaf G2

Five non-overlapping rects, `edge_bias=0` everywhere (the interior-drop path never compensates
`n`, §3-e-1), `seed = 2702 + k`, `fallcluster` pool only, `tilt_max=10`, `ground_fn = surface_z`.
Rect 1 widened to `|y| ≤ 2.60` so mound A (2.40) and drift (2.50) keep a 0.10 m margin.
Lateral extent is `|y| ≤ 3.60` on rects 2–5, which is what makes ground_kit §8.4's relocated
boundary-wear band (`y = ±3.60`, `x −3.76…6.26`) sit on a real edge.

| rect | area | cover | n | cap | |
|---|---:|---:|---:|---:|---|
| core `x −4.20…6.26, \|y\|≤2.60` | 54.39 | 0.55 | 1055 | 1150 | |
| up `x −10.60…−4.20, \|y\|≤3.60` | 46.08 | 0.32 | 432 | 470 | |
| sideN `y 2.60…3.60` | 10.46 | 0.32 | 98 | 110 | |
| sideS `y −3.60…−2.60` | 10.46 | 0.32 | 98 | 110 | |
| down `x 6.26…7.76` | 10.80 | 0.32 | 101 | 110 | |
| **total** | **132.19** | | **1,784** | | 10.84 M logical tris (cap 12 M) |

**The count is 1,784, not the 1,689 in the budget doc — and that is expected, not a miss.**
The doc computed with `mean_cov = 0.0435`; B-audit A3 (§3.2) lowered both cluster rows, so
`mean_cov = 0.04115` and the same target coverage needs ~5.6 % more instances. No rect is
truncated (every `n` stays under its 1.15n cap) and the triangle budget still clears
ground_kit §8.3. Confirmed against the harness: sceneC2 prim count 2,142 → 3,924, i.e. +1,782 =
2 prims per instance × (1,784 − 893).

`material.scale.leaf_ground`: 0.9 → **2.2** (§6-b). The texture plate cannot be deleted —
`LeafMound_A/B/C` + `LeafDrift_N/S` *are* the burial geometry that hides the drop — so it is
demoted to an underlayer at its own physical scale instead of competing with the 3D leaves.

---

## 5. scene01 lighting/camera unification

Four private copies removed. This was a live hazard, not tidying:

| Layer | Before | After |
|---|---|---|
| lookfix | private `_ensure_noon_lookfix`, **RGBA-unsafe** | deleted; alias to `sc.ensure_noon_lookfix` |
| lighting | private `setup_lighting` | `sc.setup_lighting(stage, PARAMS["light"], PARAMS["SUN_AZ_OFFSET"])` |
| camera grid | inline 9-cut loop | `sc.grid_views(-2.75)` |
| textures | private `TEX` dict | `{r: dict(sc.TEX[r]) for r in _ROLES}` |

The lookfix copy did `cv2.imread(...)[..., ::-1]`, which on a 4-channel EXR yields `[A,R,G,B]`;
the horizon lift then raises a broadcast error, the bare `except` swallows it and returns the
**source** path. Result: an uncapped HDRI sun disc *plus* the explicit DistantLight = a silent
double sun, one warning line, render "passes". All three new skies are RGBA, so this was
loaded ammunition.

Verifications: same param keys, same prim paths (`/World/DomeLight`, `/World/NoonSun`), and
`sc.grid_views(-2.75)` compared **byte-identical** (JSON) to the previous inline loop for all
9 cuts; `build_views()` still returns 13 views. Unused `numpy` and `UsdLux` imports dropped.

### Sun cap 1.5° → 0.6°, and the knob that never worked

`_SUN_CAP_DEG_DEFAULT = 0.6`, still overridable by `NEGOBS_SUN_CAP_DEG`.

Separately: **the derivative filename did not include the cap radius**, so setting the env var
returned the already-cached 1.5° EXR. The knob existed and did nothing. Fixed by putting the
cap in the cache key, keeping the legacy name for 1.5 so existing `*_lookfix.exr` files stay valid:

```
unset          -> cap 0.6 -> *_lookfix_cap0.6.exr
=1.5           -> cap 1.5 -> *_lookfix.exr          (legacy, byte-identical to today)
=2.5           -> cap 2.5 -> *_lookfix_cap2.5.exr
```

**This changes the lighting of all 33 scenes** and is the one non-`LOOK`-gated change here that
is not a scene argument. `lighting_camera_variation_spec_v1.md` §7 asks for it to ride along in
the W2 round so one regression pass covers it; `NEGOBS_SUN_CAP_DEG=1.5` restores the old look
exactly. First render will regenerate the derivatives (needs `cv2`).

---

## 6. Self-verification

- `py_compile` on all 34 touched `.py` files — clean.
- Full harness: R-5 → R-4 → R-6, 33/33 / 33/33, baseline JSON refreshed.
- Negative controls for R-4 and R-6 (§2.4), both reverted.
- 26 targeted AST / ledger assertions, all PASS: `VEG_TREES` composition and weights,
  `veg_pool` filtering, `SHRUB_ORNAMENT` contents, `SEASONAL_SUBPRIMS`, `VEG_SHRUBS` arity and
  measured heights, `VEG_DEBRIS` equality with A3, `veg` class `tex_alts`/`tex_scale`,
  `TEX["grass"]` slug, `TEX["tactile"]` names unchanged + files present, sun-cap default,
  `place_shrubs` scaling by `nat_h` with 5-field unpack and correct deactivate/instance order,
  33 scene files, no `grass=` other than 1.4, `plaza_light=1.80` in exactly 9 scenes,
  exactly 12 `[T1 T-1]` sites, zero constant-colour tactile materials, zero
  `aerial_grass_rock` references.
- `unit_cell` U3/U4 contract self-test (§3.6).

### Defect found and fixed in my own work

`sed -i` **destroys symlinks**. My grass-scale sweep over `scenes/*/*.py` converted eight
tracked symlinks (`scenes/{main,batch1}/{scene_common,facade_kit,infra_kit,stair_kit}.py`,
mode 120000) into stale regular copies. Any scene run from its own directory would then have
imported a frozen `scene_common`. Restored from `80e1301` and re-verified
(`git ls-files -s` shows 120000; the 8 paths no longer appear in `git diff 80e1301..HEAD`).
The harness was unaffected — it puts the repo root first on `sys.path` — but production runs
would not have been.

---

## 7. Merge notes for the integrator

Three-way `git merge-file` of every file I touched, base `80e1301`, theirs = the **live**
main-tree working copy (which already contains the other agents' in-flight edits):

- **`scene_common.py`: clean.** The main tree's `SKIN_EXCLUDE` mechanism landed at lines
  746–769 — module constant + `skin_exclude()` + the first-line check inside `_skin_wanted` +
  the `"gkit"` token in `_SKIN_DENY`. I never touched `_skin_wanted`; my nearest edit is its
  *caller* in `add_box` (`if LOOK_V1 …` → `if LOOK_GEO and _skin_wanted(...)`), 11 lines above
  their insertion. Semantically the two agree: skin creation is geometry, so `LOOK_GEO` is the
  correct gate, and with `SKIN_EXCLUDE` empty the behaviour is unchanged in both A/B arms
  (T1 §1.8-1).
- **`assets/NegObsGround.mdl`: not touched by me.** My worktree carries the tracked v1.8.0 blob
  unmodified, so the main tree's v1.9.0 wins on merge — which is what my passthrough needs.
- **`scenes/batch1/sceneN5_flush_grating.py`: 1 conflict, trivial.** The ground_kit agent made
  the *same* fix (constant colour → `tactile_yellow`, same 0.30 tile) inline. Either side is
  functionally equivalent; prefer mine (`bc.tactile_mtl`) only because it keeps one
  implementation. Everything else merges clean.

---

## 8. Blockers / open items

| # | Item | Status |
|---|---|---|
| B1 | `Chinese_Juniper` / `Elm_Sapling` / `Shumard_Oak` USD | **RESOLVED — all present**, manifest verdict PASS |
| B2 | Grass001 (`grass_lawn_diff/nor/rough.jpg`) | **RESOLVED — present**, 1.40 m tile confirmed |
| B3 | `tactile_yellow_diff/nor.png` | **RESOLVED — present**, 36 dots / pitch 50.0 mm measured |
| B4 | `assets/veg_manifest_w2.json` | **RESOLVED — present** |
| B5 | MDL v1.9.0 `unit_cell_*` inputs | **RESOLVED** — names/defaults match my passthrough |
| **B6** | `unit_cell_m` + `unit_cell_origin` **values** per profile | **OPEN — ground_kit owns it** (§4.5 ledger). Wiring is in, defaults 0, no pixels move until the ledger lands |
| **B7** | Tactile dot diameter 38.1 mm vs 22~25 mm common practice | **OPEN — supervisor call.** Spec table fixes count/pitch/height only. Raises dot area 19.6 %→45.6 %, works against §12.5-4 |
| **B8** | Render-order conflict: T-1 tone + `scale_m` are landed, but §8 note 2 wants them rendered **after** the pilot A/B | **OPEN — scheduling decision**, not a code issue |
| **B9** | Sun cap 0.6° changes all 33 scenes' lighting; derivative EXRs regenerate on first run (needs `cv2`) | **OPEN — expected**, `NEGOBS_SUN_CAP_DEG=1.5` reverts |
| **B10** | `build_tree(species=)` (A-audit P0-3) not implemented | **OPEN — out of scope.** The concrete symptom (cherry blossoms in a temple yard) is gone with `Japanese_Cherry`; per-scene species pools remain future work |
| **B11** | White_Pine `native_h` still uses total bbox height (`zmin −0.351` → −15 % exposed height, A §6-c) | **OPEN — out of scope**, left as-is deliberately and flagged in the table comment. The 3 new rows already use `zmax` |
| **B12** | sceneC2 G2 instancing runtime check (`IsInstance()` / prototype count) | **OPEN — needs `pxr` at runtime**, which this environment lacks. Budget doc gate 0 must be run before the render round |
