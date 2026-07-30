# W3-R3 — Building strategy A/B: procedural vs asset vs hybrid (v1)

- Wave **W3-R**, task **R3 (GPU owner)** · date **2026-07-30** · branch `feat/realism-v1`
- Test bed: **scene20** (soundest per `tonglam_v2.md`) via an **untracked** copy
  `scenes/main/_w3r_scene20_arms.py` — **deleted at the end of this round** (§11).
- Round id `260730_w3r_bldgab` · renders `look_check/scene20/260730_w3r_bldgab/arm_{a,b,b2,c,c2,d,a_rep2}/`
- No tracked scene file, no shared module and no committed asset was modified. `git status`
  shows this report only (§11).
- Evidence tags: `[measured]` = produced by a command in this round · `[law]` = statute or
  licence text · `[stat]` = derived from a population · `[assumed]` = judgement, reason stated.

---

## 0. Verdict (read this and §7)

**Hybrid — but not the hybrid the question assumed.** The split is not
"procedural for some scenes, assets for others"; it is **procedural for the mass and the LOD
demotion, assets for the one or two buildings that actually occupy a judged frame, and a
texture-scale fix for everything else.** Three findings force that shape, all measured this
round:

1. **`building_kit` cannot be adopted as-is. Its first render shows every window missing.**
   All glazing is placed at `out = −0.07 … −0.10 m`, i.e. **inside** the solid mass that
   `build_mass` emits — **62 of 376 prims across 5 types × 4 tiers = 100 % of the `GLASS`
   role, invisible** `[measured, §5.1]`. The 135/135 self-check passes because it audits prim
   budgets, ground clearance and path uniqueness, never *outward* visibility. Arm (b) is
   therefore a blank wall, and is **worse than the baseline** on every eye criterion.
2. **62.1 % of `building_kit`'s prims in the 5 target scenes can never reach a judged frame**
   (223 of 359: 133 buried, 150 above the frame ceiling `z = 0.3 + 0.1405·d`) `[measured, §6]`.
   The saving the kit advertises (−59.2 % over 33 scenes) is real but it is **not yet aimed at
   the visible band**. 4 of those 12 buildings are outside the ±30° horizontal frame in *every*
   judged cut and should be `kind="backdrop"` outright.
3. **An asset building beats every procedural arm, decisively, and is licence-clean** at the
   general-Content S3 root R1 found. `typical_building_10` (21,965 tris, 8.2 MB with textures)
   raises the building band's **σ_LF 5.73 → 20.20** and **sd 45.8 → 76.0** — the only arm that
   produces genuine low-frequency structure — at **2.25 × the render wall clock**
   `[measured, §4.1, §4.3, §5.6]`. Its architecture is Western, so it is a *backdrop* solution,
   not a Korean-facade solution — an asset backdrop still needs the `facade_kit` attachment
   layer on top (§7.1 S6).

And the cheapest single win in this whole area is **not a new asset at all**: `brick_red` is
bound at `scale_m = 2.0` in **17 scenes**, which renders each brick course at **154 mm — 2.30 ×
the Korean standard 67 mm** `[measured, §5.4]`. One constant, 17 scenes, zero prims.

---

## 1. Method and the validity gate

### 1.1 Single-variable discipline

All arms are **one file, one code path**, selected by `W3R_ARM`. Only the building call site
differs; ground, props, lighting, materials, camera, PT settings and the ground_kit pass are
byte-identical (`ground_kit` printed `프림 45 · δmax 0.1051` in every arm `[measured]`).

| arm | what changes (nothing else) |
|---|---|
| **a** | baseline — `sc.build_building(..., M["brick"], M["glass"], M["parapet"])` |
| **b** | `building_kit.build_korean_building` with `Mtls(shell=brick, glass=glass, parapet=parapet, decal=<same red>)` → the 3 materials arm (a) uses; `stone/metal/sign` fall back to `parapet`, `dark` to `shell`. **(a)→(b) isolates geometry.** |
| **b2** | (b) + a **scene-side** post-process that pulls the buried glazing 5 mm proud of the wall (§5.1). **(b)→(b2) isolates the glazing defect.** |
| **c** | (b) + facade material upgrade: `shell = plaster 2.4 tint 0.66`, `stone = granite_dark 1.0` (plinth), `parapet = concrete_wall 2.0`, `metal = steel 0.44`, `dark = 0.055`. All CC0 and already local. **(b)→(c) isolates materials.** |
| **c2** | (c) with **one** change: `shell = concrete_wall 2.0 tint 0.50`. **(c)→(c2) isolates the shell texture family.** |
| **d** | (a) with **building C only** — the sole building inside the judged frames — replaced by the NVIDIA dsready asset `typical_building_10`. D and E stay procedural. **(a)→(d) isolates one building, procedural vs asset.** |
| **a_rep2** | arm (a) rendered a second time. **Noise floor control.** |

Materials are created only in the arm that binds them, so arms (a)/(b)/(b2) share an identical
`/Looks` set; (c)/(c2) add 5 material prims (+10 stage prims) and (d) adds the asset's own 2.

### 1.2 Render channel

Identical to the frozen judge round `260730_w2d_judge` / `_w2d_fix`:
`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 ·
NEGOBS_DETAIL_ROUGH_GAIN=0`. GPU exclusive, sequential, one process per arm.

Cuts: `preset_h0.3_d5`, `preset_h0.3_d10`, `preset_h0.9_d5` **as required, plus
`preset_h0.3_d2` and `preset_h0.9_d2` rendered first and discarded** — the judge round renders
all 13 cuts in `grid_views` order and PT/DLSS accumulation carries frame history, so a
truncated list changes the first cut. Rendering the exact **order prefix** is what makes the
next gate pass.

### 1.3 Validity gate — the copy is a faithful arm (a) `[measured]`

`|arm_a − frozen baseline|` per pixel, mean over the whole frame:

| cut | vs `260730_w2d_judge` (pre-F1-fix) | vs `260730_w2d_fix` (current baseline) | noise floor `a` vs `a_rep2` |
|---|---|---|---|
| `h0.3_d5` | 8.751 | **0.230** | 0.689 |
| `h0.3_d10` | 1.046 | **0.641** | 0.661 |
| `h0.9_d5` | 0.701 | **0.478** | 0.486 |

Arm (a) reproduces the **current** frozen baseline within the noise floor on all three cuts.
The 8.75 against the *pre-fix* judge round is confined to the near-ground band
(`row-band mean |diff|`: rows 0–324 → 0.34, rows 540–756 → 23.2 `[measured]`) — i.e. exactly
the W2 **F1** near-white-patch rebind, which the fix round applied. That is a re-confirmation
of F1, not a defect of this copy.

### 1.4 Noise floor for the band metrics `[measured]`

`|a_rep2 − a|` on every band metric used below is **≤ 0.08** (worst: B-HZ `flat` +0.06,
B30 `edge%` +0.08). **Every delta reported in §4 is therefore real, not sampling noise.**

### 1.5 Bands, and why `near_ground_stats` alone cannot answer this question

`near_ground_stats.py` measures **B45/B30 = the bottom 45 %/30 %** of the frame. The three
buildings are all **above the horizon**, so those bands are the wrong instrument — they are used
here as an **invariance check**, not as the verdict. The verdict band is:

> **B-HZ = `rows[0 : 0.35·H]`** — same metric *definitions* as B30
> (σ_LF over 64-px box downsample, `edge%` at |∇L| > 0.02, `w80` on min(R,G,B) > 0.80,
> `flat%` at local σ₅ < 1/255, luma `Y = 0.2126R+0.7152G+0.0722B` on display values).

B-HZ is justified by measurement, not assertion: the arm(a)→arm(b) changed-pixel mask
(|Δ| > 12) puts **97 % of its mass inside the top 35 %** of the frame in all three cuts
(per-5 %-row-band histograms in `look_check/logs/260730_w3r_bldgab.log`) `[measured]`.
The camera geometry agrees — pitch −10°, vFOV 36° puts the horizon at row **240/1080 = 22.2 %**.

---

## 2. What is actually in the judged frames (a constraint, not an opinion)

`facade_kit.frame_ceiling(d) = 0.3 + d·tan 8° = 0.3 + 0.1405·d` `[measured — code]`:

| d [m] | 10 | 16 | 20 | 26 | 31 | 40 | 60 | 90 |
|---|---|---|---|---|---|---|---|---|
| top of frame z [m] | 1.71 | 2.55 | 3.11 | 3.95 | **4.66** | 5.92 | 8.73 | 12.95 |

scene20's three buildings, at the three judged eyes `[measured]`:

| id | facade W × depth | h | floors | true d | horizontally in frame? | inferred | tier |
|---|---|---|---|---|---|---|---|
| **C** | 28.0 × 6.0 | 13.0 | 4 | 31.0 | **YES** (subtends ±24.3° of ±30°) | `shop_house` | mid |
| **D** | 26.0 × 6.0 | 11.0 | 4 | 16.0 | **no** — bearing > 30° from every judged eye | `shop_house` | near |
| **E** | 32.0 × 8.0 | 16.0 | 5 | 22.0 | **no** — behind the camera (x −40…−32) | `office` | mid |

**Only building C is rendered in these cuts.** Of its 13 m height only the bottom **4.66 m
(1.5 storeys)** enters the frame. Everything this round says about pixels is therefore a
statement about **one mid-tier building at 31 m**; the prim/geometry statements cover all three
(§3) and the 5-scene statements cover 12 buildings (§6).

**`lod_dist` is wrong by construction.** `build_korean_building` defaults `dist` to
`|facade plane|`, not the camera distance. Over all **89** bd dicts in the 33 scenes that gives
the **wrong LOD tier for 16 (18.0 %)**; `d_default − d_true` mean **−4.4 m**, median −5.0,
range −49.0 … +10.0 `[measured]`. For scene20: C 26 vs 31, D 16 vs 16, E **32 vs 22**.

---

## 3. Prim / geometry census `[measured — in-stage traversal]`

Per building, under `/World/Scene20/Building_*`:

| arm | C | D | E | total prims | gprims | Cube | Cylinder | Mesh | whole stage |
|---|---|---|---|---|---|---|---|---|---|
| **a** | 44 | 62 | 58 | **164** | 161 | 134 | 21 | 6 | 527 |
| **b / b2 / c / c2** | 28 | 57 | 16 | **101** | 98 | 80 | 11 | 7 | 464 / 464 / 474 / 476 |
| **d** | 18 (ref) | 62 | 58 | **138** | 120 | 99 | 14 | 7 | 501 |

- **−39.1 % prims** for the kit arms (161 → 98 gprims). All geometry is analytic
  `UsdGeom.Cube`/`Cylinder`; the 6–7 `Mesh` prims are `facade_kit`'s fire-access triangles.
  **Triangle counts are not stage-measurable for the procedural arms** (analytic gprims,
  tessellated by the renderer); a Cube lower bound is 12 tris → arm (a) ≈ 1.6 k, kit ≈ 1.0 k.
- Arm (d): the referenced asset is **21,965 triangles** in 61 prims `[measured]`, appearing as
  18 prims / 2 gprims in the composed stage because it is instanced.
- The independent analytic reproduction inside `building_kit._scan_scenes` (`cur_prims()`)
  predicts **43 / 61 / 57** gprims for C/D/E — **exactly the measured 43 / 61 / 57**. That
  cross-validation lets §6 use the analytic formula for scenes we did not render.
- 33-scene scan, unchanged this round: current **4,546** prims (2,137 windows) → kit **1,855**
  (**−59.2 %**) `[measured — `python3 building_kit.py`, 135/135 pass]`.

---

## 4. Metrics

### 4.1 B-HZ — the building band, rows 0…35 % `[measured]`

| cut | arm | mean | sd | σ_LF | edge % | w80 | wht | flat % |
|---|---|---|---|---|---|---|---|---|
| **h0.3_d5** | a | 132.9 | 45.8 | 5.73 | 54.0 | 7.34 | 7.75 | 26.5 |
| | b | 136.1 | 48.1 | 6.67 | 61.0 | 9.80 | 10.18 | 21.2 |
| | b2 | 130.7 | 41.2 | 6.80 | 43.9 | 5.37 | 5.71 | 39.8 |
| | c | 171.4 | 33.7 | 6.82 | 10.9 | 4.07 | 4.40 | 33.7 |
| | c2 | 147.0 | 30.2 | 4.24 | 10.9 | 4.02 | 4.27 | 38.2 |
| | **d** | 125.1 | **76.0** | **20.20** | 27.6 | 4.07 | 22.22 | 44.2 |
| | *a_rep2* | *132.9* | *45.8* | *5.73* | *54.0* | *7.34* | *7.75* | *26.5* |
| **h0.3_d10** | a | 136.2 | 41.3 | 6.27 | 51.1 | 2.36 | 2.54 | 28.0 |
| | b | 138.6 | 43.1 | 7.25 | 55.1 | 3.58 | 4.80 | 22.5 |
| | b2 | 138.7 | 41.8 | 7.30 | 44.4 | 3.68 | 4.86 | 33.2 |
| | c | 170.4 | 34.1 | 9.49 | 13.0 | 2.87 | 3.06 | 34.8 |
| | c2 | 150.2 | 32.5 | 6.57 | 13.1 | 2.78 | 2.93 | 39.9 |
| | **d** | 141.7 | **68.2** | **18.27** | 27.1 | 4.12 | 21.06 | 42.5 |
| **h0.9_d5** | a | 128.4 | 44.8 | 5.98 | 56.3 | 7.30 | 7.57 | 30.2 |
| | b | 131.0 | 46.8 | 8.73 | 64.2 | 9.03 | 9.44 | 23.9 |
| | b2 | 126.4 | 39.6 | 8.61 | 46.3 | 5.17 | 5.53 | 43.4 |
| | c | 173.5 | 32.1 | 6.79 | 4.9 | 3.87 | 4.09 | 39.2 |
| | c2 | 145.6 | 27.3 | 5.55 | 4.9 | 3.76 | 3.91 | 43.1 |
| | **d** | 127.1 | **77.8** | **21.38** | 23.2 | 5.62 | 28.22 | 51.4 |

**How to read `edge %` here — it is not a quality score.** Arms (a) and (b) win it because
`brick_red` at `scale_m 2.0` paints a 154 mm mortar grid over the whole wall (§5.4). That grid
*is* the "brick wallpaper" the user objected to. `edge%` is measuring texture, not structure —
which is why **σ_LF** (64-px blocks) is the discriminating metric: only arm (d) moves it, from
~6 to **18–21**, and only arm (d) reads as a building rather than a wall.

### 4.2 B45 / B30 near-ground invariance `[measured]`

Buildings are above the horizon, so a building-only change must leave the judged ground band
alone. Δ vs arm (a), against a ≤ 0.08 noise floor:

| arm | B45 Δsd | B45 Δmean | B30 Δσ_LF | B30 Δedge % | B30 Δw80 |
|---|---|---|---|---|---|
| b | −0.02 … 0.00 | −0.03 | ≈ 0.00 | −0.06 … 0.00 | −0.24 … −0.18 |
| b2 | −0.01 … +0.01 | −0.04 … −0.03 | ≈ 0.00 | −0.06 … 0.00 | −0.18 … −0.13 |
| c | −0.68 … −0.19 | **+0.30 … +0.42** | −0.10 … −0.03 | **−0.78 … −0.33** | +0.09 … +0.46 |
| c2 | +0.07 … +0.19 | −0.35 … −0.20 | +0.01 … +0.05 | +0.27 … +0.56 | −0.85 … −0.47 |
| **d** | −0.21 | **+0.57** | −0.02 | **−1.34** | **+0.96** |

- Arms (b)/(b2) are **invariant** — pure geometry swaps above the horizon leave the judged
  ground band untouched. Good: they cannot contaminate the σ_LF/w80 gates.
- **A facade albedo change is NOT building-local.** (c) raises the ground band's mean by
  +0.42 and drops its `edge%` by 0.78; (d) is the largest leak (`edge%` −1.34, `w80` +0.96).
  Mechanism: global illumination — a brighter/darker backdrop rebounces onto the plaza. Small
  in absolute terms, but **a backdrop change must be re-gated on the ground band**, not
  assumed neutral. `[measured]`

### 4.3 Render cost `[measured — wall clock, 5 cuts per arm, incl. Isaac boot]`

| arm | a | b | b2 | c | c2 | **d** |
|---|---|---|---|---|---|---|
| s | 27.6 | 26.5 | 27.9 | 38.9 | 28.0 | **63.1** |

- The 161 → 98 gprim reduction is **not** measurable in render time at PT_FAST (a 27.6 vs
  b 26.5 — inside boot-time variance). **Prim count is a stage-budget concern, not a render-time
  one, at this scale.**
- (c) 38.9 s vs (c2) 28.0 s: (c) was the first arm to touch `plaster`/`granite_dark`/
  `concrete_wall`, i.e. cold texture load — **texture set count, not prims, is the cost driver.**
- (d) **63.1 s = 2.25 × baseline** for one asset building: 21,965 tris + 6 PNG (4.65 MB, one
  3.15 MB 4K colour map) + `SimPBR.mdl` compilation.
- Round total: 7 arms × 5 cuts = **35 cuts, 157 MB (renders + crops + archived drivers), ≈ 4 min of GPU** (27.6 + 26.5 + 27.9 + 38.9 + 28.0 + 63.1 + 27.6 s).

### 4.4 Crops (for eyes)

| file | contents |
|---|---|
| `look_check/scene20/260730_w3r_bldgab/_crops/arms6_preset_h0.3_d5.png` | all 6 arms, top 40 % of frame, primary cut |
| `…/_crops/arms6_preset_h0.3_d10.png` · `…/arms6_preset_h0.9_d5.png` | same, other two cuts |
| `…/_crops/zoom_burial_h0.3_d5.png` | a / b / b2 zoom on the facade — the buried-glazing defect |
| `…/_crops/full3_preset_h0.3_d5.png` · `…_h0.9_d5.png` | full frames, a / b2 / d |

Eye notes, `h0.9_d5` (the most informative cut):

- **(a)** three rows of identical blue rectangles on a strict grid + two full-width white sill
  bands + white AC boxes + a door. Articulated but **wallpaper**: the repetition and the
  oversized brick are the two things the user named.
- **(b)** blank brick wall + one white horizontal stripe + two white boxes. The stripe is the
  **signage band** bound to `parapet` (grey-white) because a legacy 3-material call has no
  `sign` role. Reads as a poster, not a building. **Worse than (a).**
- **(b2)** brick + 4 upper windows + the sign band + a **continuous ground-floor glazing band**
  + a door. Clearly the best procedural arm and a plausible Korean shop house — but the glazing
  is **3 bays of 8.93 m butted together with no mullion**, so it reads as one 27 m sheet of
  glass (§5.2).
- **(c)** a nearly featureless bright wall. **(c2)** the same wall, darker and khaki-cast.
  Both destroy the wall's structure (`edge%` 56 → 5).
- **(d)** a real mid-rise: full-height mullioned ground-floor glazing with reveals, ribbon
  windows with sills and shading fins, cream render, louvred shutters. **The only arm where the
  frame reads as a street.** Seated correctly at grade (§5.6). Architecture is Western.

---

## 5. Findings

### 5.1 **F-1 (blocker) — `building_kit` buries 100 % of its glazing inside the solid mass**

`build_mass` emits a **solid** box from the facade plane to the back wall. `Facade.world(u, out, z)`
documents `out` as "the distance **outward** from the wall face (always positive)". Three
builders pass negative values:

| builder | prim | `out` |
|---|---|---|
| `build_window_bands` (bay mode) | `Win_{f}_{b}` | **−0.10** → outer face at −0.08 |
| `build_window_bands` (band mode) | `WinBand_{f}` | **−0.12** → −0.10 |
| `build_window_bands` (curtain) | `CurtainGlass` | −0.10 → **−0.075** |
| `fk.build_shopfront` | `ShopGlass_{i}`, `ShopDoor` | → **−0.10 / −0.07** |
| `build_entrance` | `EntryGlass` | → **−0.07** |

Census over 5 types × 4 tiers (representative bd, `_demo_bd`) `[measured]`:

| kind | tier | prims | buried | of which `GLASS` | visible attachments |
|---|---|---|---|---|---|
| low_shop | near / mid / far / sil | 33 / 14 / 4 / 3 | 4 / 3 / 0 / 0 | 3 / 2 / 0 / 0 | 24 / 6 / 0 / 0 |
| shop_house | near / mid / far / sil | 56 / 27 / 6 / 3 | **17 / 12 / 2** / 0 | 16 / 11 / 2 / 0 | 32 / 9 / 0 / 0 |
| villa | near / mid / far / sil | 54 / 25 / 7 / 3 | **12 / 8 / 2** / 0 | 12 / 8 / 2 / 0 | 35 / 12 / 0 / 0 |
| apt | near / mid / far / sil | 54 / 20 / 12 / 4 | 1 / 1 / 0 / 0 | 0 / 0 / 0 / 0 | 46 / 13 / 6 / 0 |
| office | near / mid / far / sil | 28 / 12 / 8 / 3 | 2 / 2 / 2 / 0 | 2 / 2 / 2 / 0 | 20 / 3 / 0 / 0 |
| **total** | | **376** | **68 (18.1 %)** | **62** | |

62 of 62 `GLASS` prims are invisible. `apt` escapes only because it expresses its facade with
balconies rather than windows. scene20's real bd: **C 12/27, D 17/56, E 2/14 buried** — the
`_unbury_glazing` post-process moved exactly **12 + 17 + 2 = 31** prims `[measured]`, matching
the static audit prim-for-prim.

Why the 135/135 self-check missed it: `[5]` counts prims against a budget, `[7]` checks
`z ≥ base_z − 0.05`, `[8]` checks path uniqueness. **No check asks whether a facade prim is on
the outside of the wall.** Recommended new check: for every prim whose material role is
`glass`/`sign`/`decal`, assert `out_max > 0` against every mass box that overlaps its z range.

*Scene-side repair used for arm (b2)* (no module edit — this is also a legitimate integration
shim if the module fix is deferred): after `build_korean_building`, for each prim named
`Win_* | WinBand_* | ShopGlass_* | ShopDoor | EntryGlass | CurtainGlass`, set the translate on
the facade-normal axis to `plane + fdir·(0.005 + half_thickness)` — the same 5 mm-proud
convention `scene_common.build_building` settled on (`WIN_EPS`). Cost: 0 prims, ~1 ms.

### 5.2 **F-2 (blocker for `near`/`mid`) — bay count is a constant, so wide facades get absurd bays**

`_b_shop_house` uses `nb = 4 (near) / 3 (mid) / 1 (far)` and `bay_w = max(3.0, W/nb)`.
For scene20's C (**W = 28 m**) that is `bay_w = 9.33 m` → three glazing panels of **8.93 m**
each, butted with no pier `[measured]`. Real Korean shopfront bays are **3.0–4.5 m**. Visible
in `arms6_*` arm (b2) as a single continuous 27 m glass band.

Same root cause as the known limitation in `fix_building_kit_v1.md` §7-1 (the budget table has
no `W` term): **`W` is absent from the parameterisation.** Fix: `nb = clamp(round(W / 3.6), 1, …)`
per tier, and extend `prim_budget(kind, tier, W)`.

### 5.3 **F-3 — `lod_dist` defaults to the facade-plane offset, not the camera distance**

**16 of 89 buildings (18.0 %) get the wrong LOD tier** (§2). Fix: derive `dist` from the judged
eye set (`grid_views` d ∈ {2,5,10} at the scene's own gy) as the nearest point of the facade
rectangle, or require scenes to pass `bd["lod_dist"]`. Cheap, pure computation, no prims.

### 5.4 **F-4 (cheapest win in the wave) — `brick_red` is bound at twice its real tile size**

`assets/scene01/brick_red_diff.jpg` (4096², PolyHaven `brick_wall_001`, CC0) contains
**13 courses per tile**, measured two independent ways:

- texture-space FFT of the row-mean profile: dominant vertical period **315.1 px** = 13.0
  courses / 4096 px `[measured]`;
- **in the render**: direct mortar-line minima in a brick-only patch of
  `arm_a/pt_noon_preset_h0.9_d5.png` give a consistent gap of **8.25 px**; at 31 m the frame
  scale is 53.6 px/m, so the rendered course is **154 mm** `[measured]`.

Korean 표준형 벽돌 is **190 × 90 × 57 mm** `[law — KS L 4201]`; with the standard 10 mm bed
joint the course is **67 mm** and the stretcher module 200 mm. So the wall renders at
**154 / 67 = 2.30 × scale**, and the physically correct `scale_m` is **13 × 0.067 = 0.87 m**
(0.98 m if you instead keep the texture's own UK brick honest — 65 + 10 = 75 mm). Either way:
**halve it.**

*Honesty note on the horizontal axis:* the stretcher period is **not reliably measurable** from
this texture — the bricks are reclaimed and heavily cracked, so counting vertical joint runs per
course band returns 15–37 depending on the band `[measured]`. A visual count of the 4096² tile
gives ≈5 stretchers per row (→ 400 mm at `scale_m 2.0`) `[assumed — eye]`. The claim above rests
on the **course** measurement only, which two independent methods agree on to 0.4 %.

Caveat, stated honestly: PolyHaven's own metadata for this texture says **"3 m wide"**
(27.3 px/cm at 8K, self-consistent) `[law — vendor metadata]`, which would make the courses
**231 mm**, i.e. worse. The metadata contradicts the pixel content; the brick geometry is the
authority here, exactly as the W2 grass swap concluded ("`scale_m` must be the real tile size",
`scene_common.py:65`). **Pixel-verify before applying** — the project convention already
requires it.

`grep -rh "brick_red=[0-9.]*"` → **`brick_red=2.0` in 17 scene files, no other value**
`[measured]`: 01, 02, 05, 06, 11, 14, 16, 18, 19, 20, 21, C1, C4, D3, N1, N2, N5.
**One constant change fixes the "brick wallpaper" complaint in 17 scenes at zero prim cost.**
It must be re-gated (it will move B-HZ `edge%` a lot, and via GI the ground band a little, §4.2).

### 5.5 **F-5 — both facade-texture swaps made the wall worse; the problem was never the texture family**

`plaster` (c) and `concrete_wall` (c2) both collapse B-HZ `edge%` from 54–56 to **5–13** and
raise `flat%` by +7…+13. `plaster` additionally pushes the band mean to **171–174**
(Δ +34…+45). Mechanism: at 26–32 m both textures' features are sub-pixel, so the wall averages
to a flat field, whereas `brick_red`'s (over-scaled) mortar grid survives. **A facade material
upgrade that only swaps the diffuse family cannot work at backdrop distance** — what survives
distance is *geometry-scale* articulation (bands, reveals, piers, openings) plus a correctly
scaled unit pattern. This is the measured argument for F-4 + assets over new textures.

Not a total loss: (c)/(c2) also rebind the **plinth** from the `parapet` constant to real
`granite_dark` — the correct Korean lower-floor finish, and one of the constant-colour prims
W2's F1 batch was chasing. Keep that half.

### 5.6 **F-6 — the asset building is licence-clean at the general-Content root, and R1's recipe needs two corrections**

`Docs/surveys/w3r_asset_map_v1.md` (R1, same wave) establishes the dual-root situation and I
confirm both halves independently `[measured]`:

- `Assets/Isaac/*/Isaac/Environments/**` — including `Outdoor/Rivermark` and its 19,600-key
  `dsready_content` mirror — is **Limited Use Content**. I fetched
  `Assets/Isaac/5.0/Isaac/Environments/environment-supplement-LICENSE.txt` (v. Nov 18 2021):
  *"license to install and use copies of the Limited Use Content for your use only, **without
  modifications**"*, and *"The license grant for Content as described in the Agreement does not
  apply to Limited Use Content."* `[law]`. Referencing one building out of an environment and
  transforming it is a modification of the composed content → **BANNED**, and `CREDITS.md`
  already flags this tree. Agreed with R1: do not use `rivermark_plaza_bldg_*`.
- `Assets/Isaac/4.5/NVIDIA/dsready_content/` is **outside** that path scope and carries the
  general Omniverse Content terms: ML-training OK, render publication OK, **USD redistribution
  banned** (`ZZ §9.2/§10.6`, same判 as `assets/vegetation/`) → `.gitignore`. This is the root
  arm (d) used.

**Correction 1 to R1 §6.4(a).** The wrapper is not the entry point for a plain
`Sdf.Reference`. Measured triangle counts through `Usd.PrimRange`:

| referenced layer | prims | triangles |
|---|---|---|
| `typical_building_10.usd` (wrapper) | 18 | 504 |
| `typical_building_10_base.usd` | 15 | 504 |
| **`typical_building_10_inst.usd`** | 61 | **21,965** |
| `typical_building_10_inst_base.usd` | 61 | 21,965 |

The world bbox is **identical in all four cases**, so the wrapper is not broken — the geometry
is behind instance prototypes that `PrimRange` does not descend into by default. But
`_inst.usd` is the layer to reference: it is the one that both resolves without prototypes
*and* carries the real `../../../common_assets/shared_textures/…` overrides (R1 §6.4(b)).

**Correction 2 to R1 §6.5.** The table prescribes "`typical_building_10` → translate **+7.904**
in Z to sit on grade" (from `bbox zmin = −7.904`). That is wrong: the asset's **local z = 0 is
street grade**; the −7.904 is a below-grade volume. Placing at `tz = base_z = −2.15` with no
correction seats it within one pixel — the grass plane at z = −2.15 seen at d = 31 m projects
to row **408.6**, and the first grass row under the building is row **409** in all sampled
columns `[measured]`. Applying +7.904 would have hung the building 7.9 m in the air.

**Correction 3.** The referenced root already owns `[xformOp:translate, rotateXYZ, scale]`, so
`AddTranslateOp()` on it raises `UsdGeom.Xformable.AddXformOp` — a loader must place the
reference under a **parent Xform it owns** (or set the existing ops).

Procurement cost actually paid, in the scratchpad, structure mirrored `[measured]`:
4 USD (3.59 MB) + 6 shared textures (4.65 MB) + 15 `nv_core/materials/*.mdl` (0.28 MB)
= **8.2 MB, 25 files, 0 unresolved geometry references**. Download 4 s. **"Locally-fetchable
cheaply" is confirmed** — the brief's condition for making (c) an asset arm was met, so this
round answers it as arm (d) rather than losing the material comparison.

Content caveat, decisive for the recommendation: `typical_building_10` is **Western
mid-century commercial** (cream render, ribbon windows, louvred shutters, no AC condensers, no
signage band, no exposed stair, no gas riser). It is an excellent *horizon closer* and a poor
*Korean facade*. The survey's top Korean identification cues (`korean_urban_backdrop.md` §4:
AC condensers ranked 3rd) are absent — so an asset backdrop must still be **dressed** with the
`facade_kit` attachment layer, which is exactly the layer `building_kit` renders correctly
today (§5.1: all 32 of building D's non-glazing attachments are outward-correct).

---

## 6. The 5 repeated-brick scenes — where the prims actually go `[measured]`

Per-building, distance from the nearest of the three judged eyes, `cur` from the validated
analytic formula (§3), `kit` from `MockKit`:

### scene01 — 4 buildings (**bespoke inline builder, not `sc.build_building`**)

| # | W × dep | h | fl | d_true | tier | kind | cur | curWin | kit | buried | > ceiling | kit unseen | in frame |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 30.0 × 4.5 | 14.0 | 4 | 9.5 | near | shop_house | 69 | 40 | 56 | 17 | 36 | **41 (73 %)** | YES |
| 1 | 24.0 × 4.5 | 10.0 | 3 | 10.5 | near | shop_house | 51 | 24 | 50 | 13 | 30 | 35 (70 %) | no |
| 2 | 24.0 × 6.0 | 12.0 | 4 | 29.0 | mid | shop_house | 41 | 16 | 26 | 12 | 8 | 16 (62 %) | YES |
| 3 | 24.0 × 6.0 | 9.0 | 3 | 26.0 | mid | shop_house | 41 | 16 | 26 | 12 | 12 | 16 (62 %) | no |

### scene20 — 3 buildings

| # | W × dep | h | fl | d_true | tier | kind | cur | curWin | kit | buried | > ceiling | kit unseen | in frame |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 28.0 × 6.0 | 13.0 | 4 | 31.0 | mid | shop_house | 43 | 18 | 32 | 16 | 13 | 21 (66 %) | YES |
| D | 26.0 × 6.0 | 11.0 | 4 | 16.0 | near | shop_house | 61 | 32 | 56 | 17 | 16 | 25 (45 %) | no |
| E | 32.0 × 8.0 | 16.0 | 5 | 22.0 | mid | office | 57 | 30 | 12 | 2 | 4 | 6 (50 %) | no |

### scene21 — 3 buildings

| # | W × dep | h | fl | d_true | tier | kind | cur | curWin | kit | buried | > ceiling | kit unseen | in frame |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 28.0 × 6.0 | 14.0 | 6 | 41.0 | far | office | 65 | 36 | **8** | 2 | 3 | 5 (62 %) | YES |
| 1 | 24.0 × 6.0 | 11.0 | 4 | 30.8 | mid | shop_house | 61 | 32 | 32 | 16 | 8 | 20 (62 %) | YES |
| 2 | 40.0 × 8.0 | 18.0 | 6 | 49.0 | far | office | 86 | 56 | **7** | 2 | 2 | 4 (57 %) | YES |

### sceneC1 — 2 buildings

| # | W × dep | h | fl | d_true | tier | kind | cur | curWin | kit | buried | > ceiling | kit unseen | in frame |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 28.0 × 6.0 | 12.0 | 4 | 31.0 | mid | shop_house | 43 | 18 | 27 | 12 | 9 | 17 (63 %) | YES |
| 1 | 28.0 × 6.0 | 9.0 | 3 | 30.0 | mid | shop_house | 54 | 27 | 27 | 12 | 9 | 17 (63 %) | no |

### sceneC2 — **0 buildings**

C2 has no `buildings=dict(...)`. Its horizon closure is **hedge rows** (`back_hedge` × 3 +
`far_hedge` × 3) `[measured]`. C2 is not on `tonglam_v2.md`'s brick-repeat list either
(01/02/16/20/21/C1/N1/N2/N3/N5) — it is on the **midground proxy** list (§4-1 hedge-dome rows).
**C2 is not a building problem and must not be given buildings**: it is a park/leaf scene, and
adding urban buildings would repeat the `sceneD3` "urban infrastructure in a natural scene"
conflict already flagged in `fix_building_kit_v1.md` §7-6.

### Totals over the 12 buildings `[measured]`

| | prims |
|---|---|
| current `build_building` | **672** (of which windows 345) |
| `building_kit` | **359** (−46.6 %) |
| of the kit's 359, **unseeable from any judged cut** | **223 = 62.1 %** (buried 133 · above the frame ceiling 150) |
| kit prims that reach a judged frame | **136** |
| buildings outside the ±30° frame in all 3 cuts | **4 of 12** |

---

## 7. Recommendation

### 7.1 Strategy — hybrid, in this order

| # | action | why (measured) | cost |
|---|---|---|---|
| **S1** | **`brick_red` `scale_m` 2.0 → 0.87–1.0** in the 17 scenes, after pixel re-verification, then re-gate B-HZ + B30 | rendered course 154 mm = 2.30 × the Korean 67 mm course (§5.4). Directly answers "brick wallpaper" | 1 constant × 17 files, **0 prims** |
| **S2** | **Fix `building_kit` F-1/F-2/F-3, then adopt it for the mass + LOD layer** | −46.6 % prims on the 5 scenes / −59.2 % on 33, with the mass, plinth, attachment and rooftop layers already correct (all 32 of D's attachments outward-correct) | 3 code fixes + 1 new self-check; integration is 24 call sites (§7.4) |
| **S3** | **Asset backdrop building for the 1–2 buildings per scene that actually occupy a judged frame** (`dsready_content` general root only) | the only arm that moves σ_LF (6 → 18–21) and sd (46 → 76); 8.2 MB, licence-clean (§5.6) | +35 s render per scene · `assets/urban/` gitignored · needs `download_urban.py` (R1 §6) |
| **S4** | **Explicit `kind="backdrop"` for out-of-frame buildings** | 4 of 12 are outside the ±30° frame in every judged cut; backdrop = 3–4 prims | 1 key per bd, **negative** prim cost |
| **S5** | **Keep the granite plinth half of the material upgrade; drop the shell-texture swap** | plinth `parapet` constant → real `granite_dark` is right and cheap; both shell swaps collapsed `edge%` 54 → 5–13 (§5.5) | 1 material per scene |
| **S6** | **Dress asset buildings with the `facade_kit` attachment layer** (AC condensers, signage band, downpipes, gas riser) | the asset is Western and has none of the top Korean cues; `facade_kit`'s attachment layer is the part that already renders correctly | ~10–15 prims per dressed building |

**Rejected: replacing the whole backdrop with asset buildings.** 2.25 × render cost, Western
architecture, USD redistribution banned, and 8 of 12 buildings in the 5 scenes never occupy a
judged frame — spending 21,965 tris on any of those is strictly worse than 3 backdrop prims.

**Rejected: `building_kit` as-is.** Arm (b) is worse than the baseline by eye. This is not a
tuning gap; it is F-1.

### 7.2 Per-scene assignment

| scene | buildings | assignment |
|---|---|---|
| **scene01** | 4 (2 near @ 9.5/10.5 m, 2 mid @ 26/29 m) | #0 (near, in frame, ceiling **1.63 m** — only the plinth/shopfront band is ever visible): **asset backdrop is wasted here; `building_kit` near tier after F-1/F-2, with the whole budget in z ∈ [base, 1.7 m]**. #2 (mid, in frame): **asset backdrop** or kit-mid. #1, #3 (out of frame): **`kind="backdrop"`**. ⚠ scene01 does **not** call `sc.build_building` — it has its own inline `build_buildings()` with a per-building `mat` key (line 768); integrating here is a rewrite, not a one-line swap. |
| **scene20** | 3 (C mid @31 m in frame; D near @16 m; E mid, behind camera) | **C → asset backdrop** (arm (d) is the measured best); **D → `building_kit` near** after F-1/F-2 — D is out of frame in all three preset cuts but **computed** to be in frame for the mise-en-scène cuts `oblique_overview` (bearing offset 11.1°, frame top z 2.57 m at 30 m) and `along_diagonal` (9.7°) `[measured — camera maths, not rendered this round]`; **E → `kind="backdrop"`**. |
| **scene21** | 3 (2 far @41/49 m, 1 mid @30.8 m — **all in frame**) | **Biggest procedural win in the wave**: the two far buildings go 65 → 8 and 86 → 7 prims, and at 41–49 m the visible band is only 6.1–7.2 m. **`building_kit` far tier for #0 and #2** (no asset needed at that distance); **#1 mid → asset backdrop or kit-mid**. Note the existing budget warning `office/mid 16 > 15` is this scene. |
| **sceneC1** | 2 (both mid @30/31 m) | #0 (in frame) **asset backdrop**, but ⚠ **seasonal rule**: C1 is a snow scene — any asset building must be pixel-verified for roof/ledge snow and green foliage before use (`typical_building_10` has neither snow nor foliage, so it is neutral — verified by eye in this round's arm (d) crops, which are the same asset). #1 (out of frame) **`kind="backdrop"`**. |
| **sceneC2** | **0** | **No buildings. Do not add any.** C2's horizon is hedge rows → hand to the **midground** worker (R2). |

### 7.3 Backdrop policy (proposed, one paragraph)

> A building earns geometry only for the band it can occupy. For every bd, compute
> `d_true` = distance from the nearest judged eye to the nearest point of the facade rectangle,
> and `z_ceil = 0.3 + 0.1405·d_true`. **(1)** If no point of the facade falls inside ±30° of any
> judged eye, set `kind="backdrop"` (3–4 prims) — no windows, no attachments. **(2)** Otherwise
> build nothing above `z_ceil` and spend the freed budget in `z ∈ [base_z, z_ceil]`: plinth,
> shopfront, signage band, AC condensers, entrance, downpipes. **(3)** One or at most two
> in-frame buildings per scene may be an asset building from `dsready_content` (general root
> only), dressed with the `facade_kit` attachment layer. **(4)** Any change to backdrop albedo
> must be re-gated on B45/B30 — measured GI leak up to Δ`edge%` −1.34 and Δ`w80` +0.96 (§4.2).

### 7.4 Integration surface `[measured]`

- **23 scenes call `sc.build_building`, 1 site each; scene18 has 2 → 24 call sites** in
  `scenes/main` + `scenes/batch1`.
- **scene01 is the exception** (bespoke inline builder, per-building `mat`).
- `building_kit` needs **no scene-file edit** for the 24 sites (`Mtls.from_legacy` +
  `infer_kind`), but the legacy 3-material call leaves `stone/metal/sign/dark` on fallbacks —
  which is what turned the signage band into a white poster stripe in arm (b). **Passing a
  `sign` and a `stone` material is not optional in practice.**
- `building_kit.py` has **no symlink in `scenes/main`** (it is unintegrated); integration must
  add one, as `ground_kit.py` / `facade_kit.py` already have.

---

## 8. Budget summary

| item | arm a (current) | kit (b/b2/c/c2) | asset (d) |
|---|---|---|---|
| gprims, 3 buildings, scene20 | 161 | **98 (−39 %)** | 120 (C instanced) |
| prims, 12 buildings, 5 scenes | 672 | **359 (−46.6 %)** | n/a |
| of those, reaching a judged frame | — | 136 (37.9 %) | — |
| triangles | not stage-measurable (analytic gprims); Cube lower bound ≈ 1.6 k | ≈ 1.0 k | **21,965** for one building |
| new disk | 0 | 0 | **8.2 MB** per building family (4 USD + 6 tex + 15 mdl) |
| render, 5 cuts | 27.6 s | 26.5–28.0 s | **63.1 s (2.25 ×)** |
| licence | CC0 | CC0 | Omniverse general Content — render OK, **USD redistribution banned**, `.gitignore` |

---

## 9. Limitations — what this round did NOT establish

1. **One building, one tier, one scene of pixels.** Only building C (`shop_house`, mid, 31 m)
   is inside the three judged frames. The **`near` tier was never rendered** — and that is the
   tier where `building_kit` spends 54–56 prims. Geometry-level statements (§3, §5.1, §6) cover
   all types and tiers; **pixel-level statements cover mid @ 31 m only.**
2. **`apt` and `villa` were never rendered at all.** scene20 has none. `apt` is the one type F-1
   does not damage (balconies, not windows), so the kit may well already win there — untested.
3. **`edge%` on a facade is not a quality metric** (§4.1). Do not use it as a gate for backdrops
   without deciding first whether the edges are structure or wallpaper.
4. **B-HZ has no calibrated gate.** Its thresholds do not exist; the σ_LF target 11 / sd 32 are
   near-ground values derived from real photographs of *ground*. B-HZ numbers here are for
   **arm-to-arm comparison only**.
5. **F-4's corrected `scale_m` is derived, not vendor-confirmed** — PolyHaven's metadata
   disagrees with its own pixels (§5.4). Pixel-verify before applying to 17 scenes.
6. **Arm (d) placement is calibrated by hand** for one asset. A real loader needs the per-asset
   units/Z-base normalisation R1 §6.5 asks for, with the two corrections in §5.6.
7. Arm (d)'s asset lives in the **scratchpad**, not in `assets/urban/`; nothing was added to the
   repo. Production use requires R1's `download_urban.py`.
8. **No seasonal pixel-verification was performed on any asset beyond arm (d)'s own crops.** The
   C1 assignment in §7.2 carries that as a precondition, not a clearance.
9. GT / hazard geometry was not touched, and no judged-region pixel changed by more than the
   GI leak in §4.2. No regression run was needed or performed (no tracked file changed).

---

## 10. Reproduction

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
python3 building_kit.py                       # 135/135 + 33-scene scan (CPU, no GPU)
```

The A/B needs the untracked copy, which was deleted. To recreate it, copy
`scenes/main/scene20_diagonal_oblique.py` to `scenes/main/_w3r_scene20_arms.py` and apply five
edits (full detail in §1.1 / §5.1):

1. after `import ground_kit as gk`: append the repo root to `sys.path`, `import building_kit as
   bkit` (the alias **must not** be `bk` — `build_dressing` already binds a local `bk`), read
   `W3R_ARM`;
2. `ASSET_ROLES += ["plaster", "granite_dark", "concrete_wall"]` when `W3R_ARM in ("c","c2")`;
3. at the end of `setup_materials()`, add the 5 `fac_*` materials of §1.1 for `c`/`c2`;
4. replace the 4-line building loop in `build_dressing()` with the arm switch of §1.1;
5. add `_unbury_glazing()` (§5.1) and, for arm (d), a parent-Xform reference placer with
   `tx=43.371, ty=0, tz=-2.15, rotz=0` pointing at `typical_building_10_inst.usd`.

Render (GPU exclusive, sequential, ~30 s per arm):

```bash
unset PYTHONPATH VIRTUAL_ENV; source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab; export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
export NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt NEGOBS_PT_FAST=1 NEGOBS_LOOK_V1=1
export NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0
export NEGOBS_VIEWS=preset_h0.3_d2,preset_h0.3_d5,preset_h0.3_d10,preset_h0.9_d2,preset_h0.9_d5
for A in a b b2 c c2 d; do
  out=look_check/scene20/260730_w3r_bldgab/arm_$A; mkdir -p $out
  NEGOBS_CAPTURE_DIR=$out W3R_ARM=$A python scenes/main/_w3r_scene20_arms.py
done
```

Asset procurement actually used (8.2 MB, mirrored structure, general-Content root only):

```
BASE=https://omniverse-content-production.s3.us-west-2.amazonaws.com/Assets/Isaac/4.5/NVIDIA/dsready_content
  nv_content/common_assets/props_structures/typical_building_10/typical_building_10{,_base,_inst,_inst_base}.usd
  nv_content/common_assets/shared_textures/typical_building_10_{wall,windows}_{a,n,orm}.png
  nv_core/materials/*.mdl                       (15 files, SimPBR chain)
```

Metrics: `scripts/near_ground_stats.py` supplies the metric definitions; the B-HZ band driver
imports `luma / local_std / box_downsample / sobel_mag / stats` from it and applies them to
`rows[0 : 0.35·H]`. The three drivers used this round are archived next to the renders (all under
the `look_check/*` gitignore, so they are round artefacts, not tracked code):

| file | produces |
|---|---|
| `look_check/scene20/260730_w3r_bldgab/_measure_bhz.py` | §4.1–4.2 tables → `_metrics_tables.txt`, `_metrics.json` |
| `…/_buried_audit.py` | §5.1 buried-prim census (CPU only, no GPU) |
| `…/_scene5_census.py` | §6 per-scene building census (CPU only) |
| `…/logs/260730_w3r_bldgab_census.txt` | the in-stage prim census of §3, one block per arm |

`look_check/logs/260730_w3r_bldgab_times.tsv` contains **one failed row** — `d 7.7 s / 0 cuts`,
the `UsdGeom.Xformable.AddXformOp` collision of §5.6 Correction 3, before the parent-Xform fix.
The valid arm-d row is the `63.1 s / 5 cuts` one.

---

## 11. Cleanup

- `scenes/main/_w3r_scene20_arms.py` and its `__pycache__` entry: **deleted**.
- Renders and crops live under `look_check/scene20/260730_w3r_bldgab/` (157 MB) — `look_check/*`
  is `.gitignore`d, and `look_check/logs/260730_w3r_bldgab{,_times,_census}.{log,tsv,txt}` with it.
- Downloaded NVIDIA USD/textures are in the session scratchpad, **not** in the repo. Nothing was
  added to `assets/`.
- No tracked file was modified. This report is the only change this task contributes.
