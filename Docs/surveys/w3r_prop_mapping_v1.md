# W3-R2 — Prop de-proxying map v1

Author: W3-R2 (prop de-proxying). 2026-07-30. Branch `feat/realism-v1`, no commits.
Scope: every **proxy primitive** and every **form-template** in the prop layer — verdict
(`replace-with-asset` / `rebuild-procedural` / `keep`), the spec or asset that discharges it, the
scenes it touches, and a priority. Ground-attached infrastructure, buildings, midground fill,
water and the scene05 stage are **other agents' packages**; where a builder is shared across the
boundary the row says so and stops there.

Inputs: `reports/tonglam_v2.md` §4 (W3 input list) · `surveys/props_audit_w1/C1–C5` (form-template
findings) · `surveys/era_consistency_survey_v1.md` §3.1 + §5 (retrofit vocabulary and verified
build specs) · `audit_v4/user_feedback_v5_1.md` (realism conventions v5.1 + v5.2 §6–9) ·
`surveys/realism_gap_2026-07-28/{D,ZZ}` §10.6 (licence law).

Evidence tags: `[measured]` = read out of this repo's code/JSON/renders or measured over the wire
this session · `[law]` = statute / KS / national spec · `[stat]` = field statistic or product
catalogue · `[assumed]` = practice inference with no primary source.

**Boundary with the sibling W3-R packages.** R1 (`surveys/w3r_asset_map_v1.md`) owns the *catalogue*
— what exists, at what licence tier, at what cost — and the road-sign shortlist. This map owns the
*verdicts* — what each existing proxy becomes. Where the two touch: R1's **dual-root licence
correction** is adopted in §2.2 and re-based the *reason* (not the outcome) of every C-row rejection;
R1's `korea_mobiltech` road-sign find is bounded against C7b in §3-C7; the **buildings**, **midground
fill**, **grass/turf system**, **water** and **scene05 stage** rows of `tonglam_v2.md` §4 are other
agents' and appear here only as hand-offs (B1b · B2c · E5).

---

## 0. The one-paragraph verdict

The map has **36 rows**. **4 are discharged by a USD already sitting in `assets/vegetation/`** and 1
more by a CC0 download set; **20 must be rebuilt procedurally**; **2 are outright deletions**;
**2 are `keep`**; **1 is a mixed new-build set** (D1's empty apron); **3 are blocked on a supervisor
ruling**; **3 belong to other packages**. The reason `replace-with-asset` loses most of the time is
not budget, and — after R1's dual-root licence correction, adopted in §2.2 — not licence either. It
is **Korean-ness**. Every candidate street-furniture asset in the two reachable libraries is either a
**US DriveSim form** or a **European / farmhouse form on Poly Haven**
`[measured — 521-model index enumerated this session]`. The
objects our audits flag (bench slat count, bollard cap + flange + impact band, tapered lamp pole
with hand-hole, 2-gang sort bin, pergola rafters, KS F 4006 planter curb) are **Korea-specific
hardware whose verified dimensions we already hold**, so procedural rebuild is both cheaper and
more accurate. Where an asset *does* win it wins overwhelmingly: the **139 weed cubes across 22
scenes** are discharged by `Shrub/Grass_Short_C.usd`, which is **already downloaded, already
pixel-verified PASS, and 1,598 triangles** — versus 1,746,764 triangles for the nearest CC0
equivalent `[measured]`. Highest-value single row in the map is not a prop at all: it is
**§D1 base plates + anchor bolts**, the retrofit tell that the era survey calls "the largest single
realism lever … and it costs no geometry", present in 12 design cells across 02·11·15·16·17 and
built **zero** times `[measured — era §3.1, §6.2-E]`.

---

## 1. Master map

Priority: **P0** = in a primary `h0.3_d{2,5,10}` cut of ≥3 scenes or a named FAIL contributor ·
**P1** = in a primary cut of 1–2 scenes, or a large mise-en-scène occupancy · **P2** = mise-en-scène
only · **P3** = optional polish · **HOLD** = blocked on a supervisor ruling.

| # | Item (measured form) | Verdict | Spec / asset | Affected scenes | Pri |
|---|---|---|---|---|---|
| **A1** | Weed cube — `_build_weed_band` Box 0.10×0.10×(0.06–0.12) | **replace-with-asset** | `Shrub/Grass_Short_C.usd` (local, 1,598 tri, 0.28×0.30×0.12 m, PASS) | **22 scenes / 139 instances** | **P0** |
| A2 | D-5 gravel/rock scatter | **keep** | already real `Rocks/rock_small_*.usda`; W2 F2 re-parameterised | 04·07·10·11·12 | — |
| A3 | Manhole / gully disc | **keep** | W2 F5 landed: 32-segment prism + albedo 0.10 | 11 scenes rebound | — |
| **B1a** | Hedge crown blobs at h ≤ 1.2 m (4–48 spheres/band) | **rebuild-procedural** | `rounded=False` + segment breaks (C3 X9 — the box is the convention) | 01·02·05·13·16·20·N1·N2 | **P1** |
| B1b | "Hedge" used at h 1.6–4.0 m | **handoff → midground** | supply `Privet` / `Elm_Sapling` / `Gray_Birch` instanced belts | 07·09·10·12·17·C2·D3·N4 | P0¹ |
| **B2a** | Slope-shrub sphere clumps (3 ellipsoids × 6) | **replace-with-asset** | `place_shrubs(SHRUB_ORNAMENT, target_h≈0.68/0.72)` — function exists, unused here | 03 (18 spheres) · 04 (18) | **P1** |
| **B2b** | scene05 backdrop shrub lobes | **replace-with-asset** | `Boxwood`+`Privet` ring, target_h 1.02/1.24 → 52 instances, 2 protos | 05 (**337 spheres → 52**) | **P1** |
| B2c | scene11 far TreeBlob | **handoff → midground** | — | 11 | P2¹ |
| **B2d** | scene15 pot + PotLeaf sphere (r0.19) | **rebuild + asset** | 3–4 Korean container types + `Boxwood`/`Grass_Short_A` foliage | 15 (5 pots) | **P1** |
| **B3** | Reed straw — cylinder r0.022, density 6/m² | **replace-with-asset** | `Shrub/Switchgrass.usd` (local, 8,934 tri, 2.01×2.03×1.37 m, PASS) | 09 (10 bands) · 12 (5, 164 stalks) · 17 (4) | **P1** |
| **C1** | `build_bench` — 5 prims, single 60 mm slab + 4 × 60 mm legs | **rebuild-procedural** | 5-slat seat 45 mm/12 mm gap on 2 end frames; 1600×540×700 | **14 scenes / 58 instances** from `PARAMS`, + 11·14·C1·D4 from audits | **P0** |
| C1b | D4 platform bench (timber, wrong class) | **rebuild-procedural** | stainless/plastic 3–4-gang bucket seat, wall-fixed | D4 (7) | **P0** |
| **C2** | Streetlight — pole taper 0, box head, no base, 3 copy-pasted impls | **rebuild-procedural** | Ø139.8→Ø76.3 taper + 100×100×6–9T plate + hand-hole + luminaire body; single arm | **≈53 poles / 14 scenes** | **P0** |
| **C3** | Litter bin — 2-prim lidded drum Ø520–560 | **rebuild-procedural** | 2-gang sort bin: frame + opening ring + lid + label + anchors | 01·02·04·C2 — 11 bins / 4 scenes | **P1** |
| **C4** | `build_canopy` — flat 0.14 slab, slope 0, no rafters | **rebuild-procedural** | beams + **rafters @300–450**, slope, fascia, eaves ≥0.15; entry variant depth 2–3 m | C2·01·13·16·10 | **P1** |
| **C5** | `build_planter` — curb t0.25 h0.45, soil 0.10 *below* cap | **rebuild-procedural** | curb t 0.15 (KS F 4006 150×150×1000), albedo ≤0.5, soil ≥ cap, wire `place_shrubs` | **12 scenes / 47 instances** | **P1** (P0 on 01) |
| C5b | N2 raised bed used as a street-tree pit | **rebuild-procedural** | 수목보호판 grate, min width **1.5 m**; N5 1.20 → 1.50 | N2·N5 | P1 |
| **C6** | Bollard — 3 impls; `scene_common` h0.75 (<0.80 legal min); no cap/flange; mirror stainless | **rebuild-procedural** | dome cap + base plate + anchor cover + impact band material + **75 % non-compliance jitter** | 41 (batch1) + ≥19 (main), ≥10 scenes | **P1** |
| C6b | Bollards with no carriageway in the scene | **remove** | X8 — delete in 14 (10) · 16 (6) · 12 (2); re-place in 11 | 12·14·16·11 | **P1** |
| C6c | Bollard front tactile pad (`tactile=True` on 39/41) | **HOLD** | open conflict §2.13① — user owns the tactile-OFF decision | batch1 ×5 | HOLD |
| **C7a** | Text-less colour-panel "signs" — 6 *types* with no real referent | **remove** | 3 immediately-deletable independent blocks: N4 `wall_plates` (3 panels) · C1 `signpost` · C4 `sculpture`; then D2 pillar slogan ×2 | N4·C1·C4·D2 | **P0** |
| C7b | Identity-critical blank signage | **rebuild + new texture** | 2-post frame Ø60.5–101.6 @0.6–0.7, panel t 40–80 mm, Hangul texture (pipeline exists) | D4 (11) · D1 (4) · 17 · 19 | **P1** |
| C7c | `build_sign` panel bottom 1.40–1.75 m | **rebuild-procedural** | 2 posts, or panel ≤0.6 m; pedestrian signage bottom 2.5–3.0 m | 11·13·14·16·21 | P2 |
| **D1** | **Post has no base plate** — bare cylinder penetrating the slab | **rebuild-procedural** | plate **100×100×6/8/9T** + 4×Ø16 @90 + levelling nuts + 5–15 mm bedding smear + dust ring | **02·11·15·16·17** (R-cells) | **P0** |
| **D2** | One mirror-stainless material for all metalwork | **rebuild-procedural (material)** | 3-rung age ladder; the *mismatch in one frame* is the deliverable | 02·11·15·16·17 + all rails | **P0** |
| **D3** | Korean stainless shape vocabulary absent | **rebuild-procedural** | newel ball · goose-neck return · beaded rings · **inverted-U hoop row across the stair head** | 02·11·16·17·15 | **P1** |
| D4 | Retrofit tactile as a glued pad | **HOLD** | spec recorded; blocked by tactile-OFF + GT-E1′ (12 mm ⇒ 0.48 m > 0.30 m statutory position) | 02·11·16·D4 | HOLD |
| **D5** | Nosing: one chrome yellow, one construction | **rebuild-procedural** | 3 tiers (Al profile 60 mm / paint-only / partial-width tile) + **5Y 8.5/12** ≈ `#F0BE00` | 16·C4·N4·18·21·02·11 | **P1** |
| **D6** | No "scars of the operation" | **rebuild-procedural** | mortar patch · cut stub · drill halo · mid-run generation joint · rust streaks from fixings | 02·11·15·16·17 | **P1** |
| **E1** | D1 apron — 65 % of d5 frame, **zero** standing props | **new-build (mixed)** | T-11 pallet 1100×1100 + wheel guide + stopper + trench; CC0 for the loose items | D1 | **P0** |
| **E2** | D2 aggregate pile — single ellipsoid 3.4×2.3×0.84 | **rebuild-procedural** | multi-lobe ridge + top relief (outside `mounds` already fixed; `piles` is unfixed residue) | D2 | **P0** |
| E2b | D2 rebar stubs / cement bags / safety fence | **rebuild-procedural** | ribs+rust+grid · kraft grey-brown not white · bar pitch 250 → 100–150 | D2 | P1 |
| **E3** | D3 fence — one 118 m × 0.12 t box, no posts/gaps/gate | **rebuild-procedural** | posts @1.8–2.4 m, panel breaks, one gate | D3 | **P0** |
| E3b | D3 utility poles (white, constant section, no insulators) | **rebuild-procedural / HOLD** | KS F 4304 PC pole, tapered grey + cross-arm + 2–6 insulators — **§2.13② scene class open** | D3 | HOLD |
| E4 | scene15 alley service dressing | **replace-with-asset (CC0)** | aircon / gutter / rollershutter / utility box / security light — **max 3 objects per segment** | 15 | P2 |
| E5 | scene05 stage wedge gaps | **out of scope** | stage-redesign package | 05 | — |

¹ B1b/B2c are ranked here for the midground package's benefit; this map only supplies the assets.

Counts over the 36 rows: `replace-with-asset` **5** (A1 · B2a · B2b · B3 · E4) ·
`rebuild-procedural` **20** (incl. B2d, which is rebuild-container + asset-foliage) · `remove` **2**
(C6b · C7a) · `keep` **2** (A2 · A3) · `new-build (mixed)` **1** (E1) · `HOLD` **3** (C6c · D4 · E3b) ·
`handoff / out of scope` **3** (B1b · B2c · E5).

---

## 2. Why the judging came out this way

### 2.1 Triangle count is not the budget — unique data is `[measured]`

`leaf_globalization_budget_v2.md` §0 settles this with an A/B: **+845 instances / +5.13 M logical
triangles measured −0.255 s per cut**, against a round-to-round σ of 0.109 s; restoring instancing
cut unique data 595 MB → 0.69 MB, a factor of 863. So the budget question for every row below is
**"is there one instanceable prototype?"**, not "how many instances?". Two consequences:

- A 337-sphere backdrop (scene05) replaced by **52 instances of 2 prototypes** is a budget *win*
  even though each prototype is 147k–178k triangles.
- The 139 weed cubes become 139 instances of **one** 1,598-triangle prototype — 222k logical
  triangles, 1,598 unique. That is noise.
- The CC0 photogrammetry plants are the only real budget trap: `celandine_01` is **1,746,764
  triangles** and `grass_medium_02` **1,043,926** `[measured — Poly Haven API polycount]`, i.e.
  1,093× and 653× the S3 shrub we already own. Rejecting them is a budget decision as well as a
  season decision.

### 2.2 Licence closes the street-furniture asset route `[law]`

| Source | Status for this project | Consequence for props |
|---|---|---|
| Poly Haven | **CC0 1.0**, redistribution + ML explicitly permitted (CREDITS.md quotes the licence page) | usable without limit; **ships native `.usdc`** `[measured]` |
| ambientCG | CC0 | textures/decals only for our purposes |
| S3 `Assets/Vegetation/**` | no LICENSE file; upper Omniverse licence; **not** under the Environments supplement `[assumed]` | render + dataset publish OK; **do not redistribute the USD** — the regime already accepted for the 30 in-repo vegetation USDs |
| S3 `Assets/Isaac/**/Environments/**` (the Rivermark mirror) | **Limited Use Content — "for your use only, without modifications"** | ⇒ **banned** for a pipeline that scales / re-materials / re-parents |
| S3 `Assets/Isaac/4.5/NVIDIA/dsready_content/**` — the **same** `props_general` / `props_poles` at a different root | Omniverse **Content** (same tier as `Assets/Vegetation/`) `[measured — R1 §2.1]` | usable in principle; **rejected here on Korean-ness alone** (§2.3), not on licence |
| Quixel Megascans | **NoAI tag → banned** | — |
| Mixamo / RenderPeople | banned | — |

**Correction adopted from R1 (`w3r_asset_map_v1.md` §2.1), read after this map's first draft.** The
DriveSim library exists at **two roots with different bytes and different licences**, and 18,905
relative paths overlap: `Isaac/Environments/Outdoor/Rivermark/dsready_content/…` is Limited Use,
while `Isaac/4.5/NVIDIA/dsready_content/…` is ordinary Content `[measured — R1]`. So the bollard,
bench, trashcans, bike rack, safety railing and forty streetlamps are **not licence-blocked after
all** — provided the downloader pins the `NVIDIA/dsready_content/` root and rejects any key
containing `Environments/`.

**This does not change a single verdict in this map**, because C1–C7 were rejected on **Korean-ness**
(§2.3), which is licence-independent: a US DriveSim bench is still 1,600 mm-standard-Korea's wrong
shape whichever root it is fetched from. What it does change is the *reason* recorded against each
row, and it re-opens one genuine option worth a supervisor note: `props_poles` has 238 entries, so if
WP-1's streetlight rebuild proves expensive, a **luminaire-head-only** borrow from the `NVIDIA/` root
(head asset on our own tapered Korean pole) becomes licence-clean. R1 also flags a provenance
caveat: `safety_railing_01` and `bollard_02` are `_Supplier = Mathworks_Modified`, and CGTrader /
Hum3D-sourced rows exist in the same manifest, so prefer NVIDIA-supplied assets and record
`_Supplier` in any procurement manifest `[measured — R1 §2.3]`.

### 2.3 Korean-ness test, applied `[measured]`

Every CC0 street-furniture candidate was dimensioned over the wire and compared against the
Korean referent our audits already established:

| CC0 candidate | Measured dims (mm) | tri | Korean referent | Verdict |
|---|---|---|---|---|
| `modular_street_seating` | 4340 × 770 × 950 | 25,156 | 옥외 등벤치 **1600 × 540 × 700** `[stat]` | reject — 2.7× length, contemporary Western module |
| `street_lamp_01` | 704 × 386 × **3871** | 30,610 | 보행공간 등주 **4.5–6.0 m**, tapered tube, cobra/post-top | reject — European alley lamp, sub-height |
| `street_lamp_02` | 386 × 807 × 1675 | 20,338 | — | reject — wall bracket lamp |
| `planter_box_01` (`_02`/`_03` same family) | 913 × 414 × 425 | 8,094 | KS F 4006 화단경계석 150×150×1000 masonry bed | reject — farmhouse timber crate |
| `metal_trash_can` | **1847** × 556 × 906 | 13,960 | 가로 휴지통 2-gang framed, Ø450–560 | reject for plaza; **allow** as alley/yard dressing (15·D1·D2) |
| `water_manhole_cover` | Ø691 × 68 | 6,301 | KS D 4040 frame Ø648 / 766 / 918 `[law]` | near-miss; superseded by W2 F5 — **not now** |
| `modular_electricity_poles` | 13119 × 1957 × **7000** | 200,610 | KS F 4304 PC pole **10–16 m**, tapered grey | reject — form and height |
| `modular_chainlink_fence` | 8115 × 2149 × 2523 | 89,232 | 가설울타리 steel panel more common `[assumed]` | allow as **yard boundary** only (D1/D2) |
| `concrete_road_barrier` | 1545 × 641 × 835 | 80,776 | 방호벽 1000/2000 × h800–1000 | allow (18 already has procedural Jersey barriers judged good) — P3 |
| **`korean_fire_extinguisher_01`** | 280 × 367 × 659 | 9,913 | 국내 소화기 — **an explicitly Korean scanned product** | **accept** (D1·D2·D4) |
| `exterior_aircon_unit` · `modular_metal_gutter` · `rollershutter_window_01–03` · `utility_box_01/02` · `power_box_01` · `security_light` · `old_tyre` · `Barrel_01/03` · `plastic_crate_03` · `cardboard_box_01` · `hand_truck` · `trashbag` | see §5.2 | 1,104–21,740 each | culture-neutral urban service objects | **accept as dressing**, capped (see §4) |

### 2.4 Season pixel rule, applied `[measured]`

The project's own gates were re-run this session on the 1k diffuse atlas of every plant candidate
(`gate_woody`: green+yellow-green ≥ 0.75 **and** red+pink+orange ≤ 0.06; `gate_turf`: green+yg ≥
0.75 **and** red+pink ≤ 0.02 **and** orange ≤ 0.25). Method note: our veg team judged UV-sampled
foliage pixels; this pass judges the **whole atlas**, so a FAIL here means "not clearable without a
UV-sampled re-run", not "banned outright".

| Candidate | G | YG | O | R | P | albedo_lin | Gate |
|---|---|---|---|---|---|---|---|
| `celandine_01` | .619 | .328 | .010 | .020 | .001 | .081 | **PASS** (but 1.75 M tri, European spring herb) |
| `potted_plant_02` (leaves) | .929 | .026 | .002 | .012 | .004 | .136 | **PASS** (tropical foliage — wrong plant for a Korean alley) |
| `weed_plant_02` | .651 | .228 | .084 | .025 | .001 | .040 | FAIL (O+R = .109 > .06) |
| `nettle_plant` | .436 | .371 | .110 | .056 | .002 | .039 | FAIL |
| `dandelion_01` | .280 | .513 | .098 | .086 | .001 | .085 | FAIL (+ yellow flowers) |
| `periwinkle_plant` | .288 | .165 | .291 | .095 | **.139** | .064 | FAIL (flowering) |
| `shrub_sorrel_01` | .802 | .038 | .019 | .023 | **.118** | .154 | FAIL (flowering) |
| `shrub_01` / `_02` / `_03` / `_04` | .519/.199/.073/.102 | .215/.295/.718/.521 | .112/.262/.135/.159 | .153/.244/.074/.218 | 0 | — | FAIL (Verdant-Trail autumn set) |
| `grass_bermuda_01` | .637 | .138 | .048 | .081 | .003 | .008 | FAIL turf (R+P .084 > .02) |
| `grass_medium_01` | .474 | .343 | .064 | .064 | .006 | .016 | FAIL turf |
| `grass_medium_02` | .430 | .240 | .158 | .125 | .002 | .030 | FAIL turf (G+YG .670 < .75) |
| `moss_01` | .286 | .433 | .088 | .122 | .003 | .006 | FAIL turf |
| `potted_plant_04` | .281 | .282 | **.410** | .027 | 0 | .272 | FAIL (succulent) |

**Conclusion:** no CC0 plant clears both the season gate and the Korean-ness test. The vegetation
rows in this map are therefore discharged **entirely from assets already in
`assets/vegetation/`**, all of which carry a recorded PASS in `assets/veg_manifest_w2.json`.

---

## 3. Item cards

### A. Ground-scatter proxies (ground_kit-owned, but they read as props)

#### A1 · Weed cube → `Shrub/Grass_Short_C.usd` — **P0**

**Measured form.** `ground_kit._build_weed_band` emits one axis-aligned Box per clump,
**0.10 × 0.10 × h**, `h = weed_h_max · U(0.5, 1.0)` with `weed_h_max = 0.12` ⇒ 60–120 mm, material
`@weed`, declared albedo 0.15 `[measured — ground_kit.py:2781]`.

**Spread.** `GROUND_PROFILES` carries a `("weed", n)` surface op on 8 of 19 profiles; crossed with
`SCENE_PLANS` that is **22 scenes / 139 cubes**: `plaza_granite` n=6 → 01·05·14·18·20·21·C1·N1·N3;
`sidewalk_block` n=8 → 02·08·16·C2·C4·N5; `alley_concrete` n=8 → 15; `levee_paved` n=6 → 03·17;
`ramp_parking` n=5 → 13; `street_asphalt` n=4 → N2; `ramp_road` n=4 → N4; `verge_rural` n=4 → D3
`[measured — computed from the two tables]`. 통람 v2 observed them in 12+ primary cuts; the
difference is GT-E5 clamping and framing.

**Replacement.** `Shrub/Grass_Short_C.usd` — already at `assets/vegetation/Shrub/`, **1,598
triangles**, bbox **0.28 × 0.30 × 0.12 m**, role `edge_weed`, `verdict: PASS`, foliage hue green
1.0 `[measured — veg_manifest_w2.json]`. Licence: the accepted `Assets/Vegetation` regime — render
and dataset publish OK, USD not redistributed `[law]`.

**Implementation constraints (do not skip).**
1. `exc="weed"` and the **GT-E5 ramp** must survive: `_clamp_gt_e5` rewrites `proud` to
   `edge_gap / EDGE_K` and drops the element below 5 mm. The asset's scale must be driven by the
   **clamped** value, not by native height, or the ramp becomes decorative.
2. Footprint grows 0.10 → 0.28 m (2.8×). `_elem`'s aabb must be recomputed from the scaled bbox,
   and `EDGE_STANDOFF = 0.80` re-checked per instance.
3. `add_vegetation` applies a **uniform** `Vec3f` scale, so height-clamping a 0.28 m-wide asset
   also shrinks its footprint. If a clump must stay 0.28 m wide at 60 mm tall, the props kit needs
   a non-uniform variant.
4. GT class stays **A** (z unchanged) as long as h ≤ 0.12 — same standing as today.
5. Per-profile `prim_cap` / `inst_cap` gates: 1 prim → 1 referenced prim, so counts are unchanged.

**Rejected alternatives.** `weed_plant_02` (CC0, 17,062 tri) fails the woody gate at .109;
`celandine_01` passes but is 1.75 M tri and a European spring herb `[measured]`.

#### A2 · D-5 scatter — **keep**

`VEG_ROCKS` already binds real `Rocks/rock_small_*.usda`; W2 F2 re-parameterised scale jitter,
burial 0.38 and count caps, and the re-render judgement is the ground team's. **Do not re-open.**
Carried gap for their record: S3 rocks top out at **0.31 m**, so scene12's 0.30–1.10 m band has no
asset `[measured — asset_audit_v1 §2]`. If one is needed: `stone_01` (71,916 tri) or
`rock_moss_set_01` (63,127 tri), both CC0 usdc.

#### A3 · Manhole / gully — **keep**

W2 fix batch F5 replaced the analytic disc with a **32-segment prism** through `kit.D` (frame, lid,
boss, plus the scene-local triple-disc manholes of N2/N5) and rebound the albedo to 0.10 dark iron
across 11 scenes `[measured — w2_fixbatch_v1 §F5]`. `water_manhole_cover` (CC0, Ø691 × 68 mm,
6,301 tri, 0.32 MB usdc) would add real cast-iron relief, but Korean covers carry Hangul lettering
and a different pattern, and the swap perturbs a **GT-registered** element's aabb/proud. **P3 at
most; recommend not now.**

### B. Vegetation-shaped proxies that live in the prop layer

#### B1a · Hedge crown blobs at h ≤ 1.2 m — **rebuild-procedural**, P1

**Measured form.** `scene_common.build_hedge(rounded=True)` lowers the body box to `0.72 h` and
overlays a row of flattened ellipsoids of long-radius `pitch · U(0.56, 0.70)` and half-height
`h · U(0.26, 0.34)` `[measured — scene_common.py:2852]`. Crown counts computed from the builder's
own formula, per band: 01 30 · 02 11/segment × 4 · 05 19 · 13 14 · 16 4 · 20 9 · N1 14 ·
**N2 48 over one unbroken 52 m band** `[measured]`.

**Why rebuild and not replace.** C3 **X9** is explicit: the settled convention is *"생울타리 각진
상자는 의도적 유지 (한국 전정 관행)"*, and `rounded=True` **violates it** — the rounding was a fix
for the v6 "haystack box" verdict and it produced the "ball row" the user is now objecting to. C4
§1.5 independently rules `build_hedge` **유지 ✔ — 손대지 말 것**.

**Spec.** (i) Revert to `rounded=False` for this height band. (ii) Deliver the top-edge fuzz at the
right scale: crown elements **0.08–0.12 m**, not `0.26–0.34 h` (at h 0.9 that is 0.23–0.31 m — the
ball). (iii) C5 1-E's breaks: a **0.6–1.2 m gap every 6–12 m** plus **±10 %** per-segment height,
because real hedge runs are interrupted by street trees, entrances and species changes; N2's 52 m
and D3's 26 m × 4 have zero interruptions `[measured]`.

#### B1b · `build_hedge` at h 1.6–4.0 m — **handoff → midground**

A Korean clipped hedge is not 4 m tall. These bands are **tree/shrub belts mis-modelled as
hedges**, which is precisely why 통람 v2 reads them as "green mega-domes", "black hedge-ball
silhouette row", "giant flat green walls": 07 h2.0/2.4 · **09 h3.6** · **10 h4.0** · 12 h1.6 ·
17 h1.7 · C2 h1.7/1.8 · D3 h1.6 · N4 h1.8 `[measured]`. Assets to hand them, all local, all PASS:
`Shrub/Privet.usd` (h 1.114 m, 147k tri) for 1.6–2.0 m belts; `Trees/Elm_Sapling.usd` (h 3.09 m,
113k tri) and `Trees/Gray_Birch.usd` (h 3.33 m, 257k tri) for 3.3–4.0 m belts `[measured]`. This
map does not schedule the work.

#### B2a · Slope-shrub sphere clumps (03 · 04) — **replace-with-asset**, P1

03: `PARAMS["hedges"]` 6 clumps × `hedge["blobs"]` 3 ellipsoids = **18 spheres**, radii
0.30–0.40 × 0.40–0.62 × 0.25–0.34, `embed 0.55`. 04: 6 clumps × 3, `embed 0.25`, blobs to 0.72
`[measured]`. **`place_shrubs()` already exists** (scene_common.py:2796), already disables
`Rhododendron`'s magenta flower prims, already fixes the width-vs-height scale bug, and is simply
**not called by these scenes**. Call it with `pool=SHRUB_ORNAMENT`, `target_h` 0.68 (03) / 0.72
(04), seeds from the existing clump coordinates. Prims 18 → 6 references, 2 prototypes.

#### B2b · scene05 backdrop shrub buffer — **replace-with-asset**, P1

Exact port of `backdrop_instances()` run this session: **52 clumps → 337 lobe spheres** over two
arc rows (r 5.85/6.25, steps 0.44/0.52, 6/7 lobes, skip 0.12) `[measured]`. This is the "even row
of mossy boulders" / "green ellipsoids perched on the bowl walls" flag. Replace with a
`place_shrubs` ring at the same 52 clump coordinates, `target_h` 1.02 (row 0) / 1.24 (row 1),
`pool=SHRUB_HEDGE` (`Privet` 1.114 m + `Boxwood` 0.741 m — both natively in the target band).
337 prims → **52 instances / 2 prototypes / 325k unique triangles**. The v6 access-deterrence
function (crown tops clearing the arc wall at +0.70) is preserved by the target heights.

#### B2d · scene15 flower pots — **rebuild + asset**, P1

`pot` = cylinder r 0.20 × h 0.34; `PotLeaf` = one sphere 0.19 × 0.19 × 0.152 — 2 prims × 5
`[measured]`. C3 P1 #11 asks for 3–4 container types with size jitter. **Korean-ness is the entire
point of this prop**: alley pots are 스티로폼 박스 (≈0.50 × 0.35 × 0.30), 고무 대야 (Ø0.45), 스텐
대야 (Ø0.40) and glazed 화분, planted with 고추 / 상추 / 화초 `[assumed]`. Foliage from
`Boxwood` scaled to 0.30–0.40 or `Grass_Short_A` (32,504 tri, 1.29 m native, PASS). CC0
`potted_plant_02` passes the season gate but is a tropical houseplant — **reject**.

#### B3 · Reed straws → `Shrub/Switchgrass.usd` — **replace-with-asset**, P1

**Measured form.** `PARAMS["reed"]` r **0.022** m cylinders, density 6/m², tilt 9°; heights 0.80–1.12
(12 · 17) and 1.1–1.9 (09). 09 has 10 bands; 12 has 5 bands and its own selfcheck prints **164
stalks**; 17 has 4 bands `[measured]`.

**Replacement.** `Shrub/Switchgrass.usd` — local, **8,934 triangles**, bbox 2.01 × 2.03 × 1.37 m,
role `riparian_grass`, `verdict: PASS` `[measured]`. At 6 stalks/m² a 6 m × 0.85 m band is ~31
cylinders; one asset instance covers ~2 m of band, so a band becomes 3–4 instances of one
prototype. 09's 1.9 m target needs scale 1.39× — acceptable because **reed height is not a scale
anchor for the drop cue**, unlike tree height `[assumed]`. Rejected CC0: `grass_medium_02` fails the
turf gate and is 1.04 M tri.

### C. `scene_common` form-templates

#### C1 · `build_bench` — **rebuild-procedural**, P0

Measured: Box(Seat) 1.800 × 0.400 × 0.060 with top at z 0.450, plus 4 × 0.060 × 0.060 × 0.390 legs
= **5 prims**; no backrest, no armrest, **zero seat slats**, no frame, no chamfer, no drainage gap
`[measured — scene_common.py:2913]`. Real referent: outdoor 등벤치 **1,600 × 540 × 700 mm** catalogue
standard, seat of 4–6 timber slats (45–50 mm stock) on cast-iron or steel-tube end frames `[stat]`.
The audits agree across three independent passes (C1 C0-1, C3 X4, C4 §1.1, C5 1-A) that this reads
as **a table**.

Spec: seat **5 slats × 45 mm wide × 12 mm gap** on **2 end frames** (Ø48.6 tube or 50 × 50 SHS),
seat top 0.42–0.45, overall depth 0.54, backrest 3 slats to 0.70; backless variant (plaza,
platform) = slats only. Prims 5 → ~16. **Keep the signature**
(`cx, cy, base_z, mtl, length, width, height, yaw`) — `build_tree` set the precedent that a
signature-preserving swap propagates to all 33 scenes with no scene edits. The slat gaps' thin
shadow stripes are the read signal that a uniform brown slab cannot produce under noon sun.

Independent instance cross-check from `PARAMS` across 33 scenes: **58 benches whose coordinates are
declared in `PARAMS`, in 14 scenes** (01 6 · 02 2 · 03 4 · 04 5 · 09 4 · 12 4 · 13 3 · 16 3 · 17 4 ·
18 6 · 20 6 · C2 2 · N1 5 · N3 4) `[measured]`; 11 · 14 · C1 · D4 also call `build_bench` from
non-`PARAMS` coordinate sources, so the true total is higher and matches the audits' partial tallies
(batch1 22 · scenes 11–16 22 · 01 6 · 17/18/20/21) `[measured]`.

**D4 is a different object.** A subway platform seat is a stainless or plastic **3–4-gang bucket
seat with armrest dividers, wall-fixed** — a timber picnic bench does not exist on a platform
`[measured — C5 §2.12]`. Separate variant, P0 for D4's 7 units.

#### C2 · Streetlight — **rebuild-procedural**, P0

No shared builder exists; the same 5-prim assembly is copy-pasted at `scene01:805`, `scene02:815`,
`scene05:1125` and inline in every other scene. Measured: pole Ø120–180 with **taper 0**, h 4.6–6.0;
arm(s) 1.0 m at a **right-angle joint**; head = a flat 0.25–0.35 box; **no base plate, no
hand-hole, no luminaire body**; 18/20/21 use a **symmetric twin arm**, which is a median form
standing at a plaza edge with no justification `[measured — C1 C0-6, C3 X5, C4 §1.2, C5 1-B]`.
Independent count from `PARAMS`: **53 poles across 14 scenes** (01 4 · 02 4 · 05 5 · 08 4 · 12 2 ·
13 3 · 16 2 · 17 7 · 18 5 · 20 3 · 21 4 · N1 4 · N2 3 · N4 3) `[measured]`, consistent with the
three audits' partial tallies (11–16: 17 · batch1: 17 · 17–21: 19).

Height 4.5–6.0 m is **correct** for pedestrian space and must not be "fixed" `[stat]`. What is
wrong is form and material:

- tapered tube **Ø139.8 → Ø76.3** (or 165.2 → 60.5) `[assumed — practice]`
- **base plate 100 × 100 mm in 6T / 8T / 9T** + set-anchor (스트롱앵커) SUS304 — market stock size,
  **preferred over the repo's 120 × 120 × t9** `[stat]`
- hand-hole door 100 × 300 at z 0.6–1.0 `[assumed]`
- curved or 15–45° inclined bracket, **single arm** except true median forms
- luminaire body (cobra-head or post-top), not a flat plate
- matt galvanized: albedo 0.45–0.55, roughness 0.45–0.60, primaries avoided `[law — 도로안전시설
  지침 2.4.3/2.4.4]`

Note the defence line: **equal pole spacing is correct** — the "no equal spacing" convention is
about decorative placement, not photometric design `[measured — C4 §8-4]`.

#### C3 · Litter bin — **rebuild-procedural**, P1

Three copy-pasted 2-prim assemblies (`scene01:960`, `scene02:804`, `scene04:840`): body cylinder
Ø520–560 × h 0.85–0.90 + a rim cylinder at r × 1.1, h 0.04. It reads as a **water tank** in
scene02's beauty overview `[measured — C1 C0-3]`. A Korean street bin's identity is the **2-gang
(일반/재활용) frame + opening + lid + separation label + fixing bolts** `[assumed — 관행]`. New
`props_kit.build_binsort`. **11 bins in 4 scenes** (01 4 · 02 2 · 04 3 · C2 2) `[measured]`. CC0
`metal_trash_can` is allowed **only** as alley or yard dressing (15 · D1 · D2), never in a plaza.

#### C4 · `build_canopy` → pergola — **rebuild-procedural**, P1

Measured: roof = one flat Box t 0.14 with **slope 0**, 4 posts Ø160–200 = 5 prims; **no rafters, no
gutter, no eaves** `[measured — scene_common.py:2011]`. A pergola's form identity **is** the
beam + rafter lattice at **300–450 mm pitch**; without it the object is "a floating plate", not a
pergola `[assumed — sourced in C5 §8]`. C5 ranks it #4 by occupancy (4 % of C2's beauty frame).
Spec: beams + rafters @300–450, drainage slope, fascia/gutter, eaves ≥ 0.15. Entry-canopy variant:
depth 2–3 m (scene01's 1.4 m sheds no rain), or the **wall-cantilever post-free** form that
dominates Korean low-rise public buildings `[assumed]`.

#### C5 · `build_planter` — **rebuild-procedural**, P1 (P0 on scene01)

Measured: 4 curb boxes + 4 cap boxes + 1 grass slab = **9 prims**; curb **t 0.250 × h 0.450**, cap
overhang 0.050 × t 0.050, soil top **0.100 below the cap top** `[measured]`. Three defects
compound: (a) t 0.25 is **1.67×** KS F 4006 화단경계석 **150 × 150 × 1000**, so it reads as a
retaining wall `[law]`; (b) `curb_color` 0.72–0.75 renders near-white under noon sun — 18 and 20
show "white box walls", while scene19's `granite_dark` is correct `[measured]`; (c) the sunken soil
makes it an **empty stone box** — and the shrub fill is behind an `if LOOK_V1 and veg_available()`
gate that renders **zero** shrubs in 13/14/16 `[measured — C3 X6]`.

Spec: curb t 0.15; albedo ≤ 0.5 (granite 0.35–0.55 / concrete 0.30–0.45) + cap drip groove; soil
top **at or above** cap top; wire the existing `place_shrubs`. **47 planters in 12 scenes** (01 5 ·
02 2 · 05 8 · 13 5 · 15 5 · 16 4 · 18 3 · 20 3 · N1 4 · N2 2 · N3 4 · N5 2) `[measured]`; scene01's 5
planters are the **single highest h0.3 occupancy prop in the library at 5–8 % of frame area**
`[measured — C1 §1]` — hence P0 there.

**Typology error to fix separately:** a sidewalk street tree gets a **수목보호판 (tree grate)**, not
a 42–52 cm raised bed — minimum width **1.5 m**, cover **≥5 cm clear of grade** `[law — 산림청 고시
2023-48]`. N2 must convert; N5's grate is **1.20 m, sub-legal → 1.50** `[law]`.

#### C6 · Bollards — **rebuild-procedural** + **remove**, P1; tactile **HOLD**

Three implementations: `scene_common.build_bollard` (r 0.060 / **h 0.750**, below the 0.80 statutory
minimum by 6.3 % `[law — 교통약자법 시행규칙 별표2 제7호]`, used by 11 and 12);
`scene20/21 build_bollard_std` (Ø150 × h0.900 + band — legal); `bc.build_bollard_v51` in batch1
(41 units, **all dimensions legal** `[measured]`). What every one of them lacks: **top dome or
chamfer cap, base plate, anchor-bolt cover**, and the statute's *"보행자 충격을 흡수할 수 있는
재료"* — current `metallic 0.9 / roughness 0.35` is mirror stainless, which is non-compliant
`[law]`. At magnification they read as "white plastic sticks" `[measured — C5 §3]`.

**The second half of this row is more important than the first.** 41 out of 41 batch1 bollards are
fully compliant, and that is **statistically unreal**: 한국시각장애인연합회 2023, n = 337 sites,
**볼라드 부적정 96.0 %** `[stat]`. Spec: keep ~25 % fully compliant; split the rest into measured
non-compliance types — h 0.6–0.7, spacing 2.0–2.5 m, worn reflective band, missing front tactile,
one leaning.

**Removals first (cheapest, and a convention fix):** X8 finds **no carriageway, parking bay or
vehicle path anywhere** in 14 (10 bollards) or 16 (6), and 12's pair is unrelated to its bike path;
11's pair at y ±4.0 is 8 m apart and forms no barrier `[measured]`. Delete in 14 · 16 · 12,
re-place in 11.

**HOLD:** `build_bollard_v51(tactile=True)` is on for 39 of 41 while the mainline 21 are all OFF —
and the rendered yellow is **55 px = 0.0027 %** of N5's beauty frame, i.e. simultaneously against
the convention and invisible `[measured]`. §2.13① is an open supervisor conflict; the tactile-OFF
decision is the user's. **Do not touch.**

No CC0 bollard exists (521-model index enumerated `[measured]`); Rivermark's is Limited Use.
Procedural is the only path.

#### C7 · Signage — **remove** 6, **rebuild + texture** the rest

**C7a — remove, P0.** C5 1-C identifies **6 types** of "text-less colour panel" that have no real
referent and violate the v5.2 §8 rule that only real 도로교통법 signs and readable facility signage
may exist (N4 옹벽 안내판 ×3 · C1 표지판 · D1 dock numbers ×4 · D4 역명판 ×5 · D4 hanging signs ×4 ·
D2 pillar slogan ×2). Of those, the ones with **no identity function** get deleted outright:

- **N4 `wall_plates` (3 panels)** — 0.55 × 0.38 navy backing + 0.42 × 0.26 white face, reading as
  "a white sheet in a blue frame"; **C5's #1 ranked item overall** at 1.6 % of d2 and 4 % of
  `wall_run` `[measured]`
- **C1 `signpost`** — panel **60 mm thick**, "blue paper on a stick" `[measured]`
- **D2 pillar slogan ×2**

Plus one non-sign removal in the same class: **C4 `sculpture`** (규약 위반, 근거 0). All four are
**independent functions with zero side effects**, which makes this the cheapest measurable win in
the whole map `[measured — C5 §7.1]`. D1 and D4's panels go to C7b instead, because deleting them
would delete the scene's identity.

**C7b — rebuild + new texture, P1.** D4's 역명판 ×5, ceiling hanging signs ×4 and ad lightboxes ×2
are **identity-critical** for an underground platform — remove them and the scene stops being a
station. Their dimensions are already in the real band (1.6–2.4 m × 0.45–0.6) `[measured]`; the
defect is that they carry **no characters**. The Hangul texture pipeline already exists
(`assets/signs/sign_*.png`, bound in 11 scenes) `[measured]`. Same for D1's dock numbers ×4,
scene17's blank 이정표, scene19's four blank billboards.

**Boundary with R1, so the work is not done twice.** R1 §5.3 found **156 Korean 도로교통법 sign
USDs** (`korea_mobiltech`, 41.92 MB, `sign_kr101` measured at 104 tris / 0.844 × 0.741 m) and owns
the **road-sign** shortlist per scene type `[measured — R1]`. Those are regulatory plates. **C7b is
the complement**: station name plates, platform hanging signs, ad lightboxes, dock numbers and
facility 안내 boards, none of which exist in that catalogue. Carry R1's caveat forward if a
regulation-adjacent claim is ever made about the road plates: `sign_kr101`'s 844 mm side is ~6 %
under the 900 mm 주의표지 standard, and the 2xx/3xx families have different standard sizes, so no
uniform rescale.

**C7c — dimension, P2.** `build_sign` hangs a 1.0 m panel on a **single Ø80 post** (structurally
unreal) with the panel bottom at **1.40–1.75 m** against 2.5–3.0 m for pedestrian signage
`[law — 주소정보시설규칙; measured — C3 X7]`. Spec: 2 posts Ø60.5–101.6 at 0.6–0.7 m, or panel width
≤ 0.6; panel thickness 40–80 mm (current 120 mm is 1.5–3× over).

### D. Retrofit vocabulary — 12 design cells, 0 implementations

`era_consistency_survey_v1.md` §3.1 classifies each scene × fixture as EXPECTED / ABSENT-REAL /
**RETROFIT-STYLE**. RETROFIT-STYLE has **12 cells, concentrated in 02 · 11 · 16 · 17 · 15(variant)**,
and **not one is built that way today**; §6.2-E calls this "the largest single realism lever this
survey found and it costs no geometry" `[measured]`. The governing rule that makes it cheap:
**retrofits happen for members (handrail, tactile pad, nosing, paint) and never for geometry
(landing, riser, mid-rail)** — so "handrail present, landing absent" is a coherent, common,
realistic combination that needs no reconciliation `[law/stat — §3.0, §5.6]`.

#### D1 · Base plate + anchor bolts — **P0, the single highest-value row**

> The post does not grow out of the ground. It stands on a plate that is bolted to the ground.

「도로안전시설 설치 및 관리 지침」 2.6 gives three anchorage types: embedded 400 mm (reads
original) / shallow + mortar collar (original-ish) / **base plate + anchor bolts (reads retrofit)** —
because plates and anchors are meant to be set *before* the pour, so a plate on a weathered slab
proves the fixture post-dates it `[law/spec]`. Our posts are bare cylinders penetrating the ground
`[measured — korean_pedestrian_geometry §1.5]`, which is why they read as CG.

Spec (3 prims + 1 decal per post): plate **100 × 100 mm, 6T / 8T / 9T** (market stock, preferred
over the repo's 120 × 120 × t9) `[stat]`; **4 × Ø16 anchors at 90 mm pitch** `[assumed — no
source, keep the tag]`; one levelling-nut course under the plate; mortar/epoxy bedding smear
**5–15 mm proud** around the plate edge; slight tone break in the slab beneath plus the drill-dust
ring that never fully cleans off. Apply to the **retrofit** posts of 02 · 11 · 15 · 16 · 17; leave
embedded-with-mortar-collar posts on the EXPECTED scenes (01 · 06 · 08 · 13 · 14 · 20 · 21) — the
**contrast between the two** is the deliverable, not the plate alone.

#### D2 · Metal age ladder — **P0**

| Era | Stock | Look values |
|---|---|---|
| 1970s–80s original | painted mild steel pipe | albedo 0.20–0.35, roughness 0.55–0.75, chip/rust decals at joints and feet |
| 1990s–2000s | hot-dip galvanized | albedo 0.45–0.55, **roughness 0.45–0.60**, faint spangle, white bloom in crevices |
| 2000s–2010s retrofit | STS304 round tube | metallic 0.9 but **roughness 0.30–0.40**, brushed anisotropy along the tube axis |

`[law/spec + stat]`. Our universal `metallic 0.9 / roughness 0.35` mirror stainless is wrong **as a
default**: matt galvanized is the default for road and bridge guardrails, and stainless is the
**marker** of a recent handrail or bollard `[measured — korean_pedestrian_geometry §1.6]`. Field
colours that are real and current and must not be flattened: bare stainless, dark-grey painted pipe
on wall L-brackets, rust-brown "rustic" in nature/heritage settings, white + mid-blue panel infill
with ball finials (2000s 육교 signature), **full green** (2024 municipal refit), yellow-with-black
diagonals as a hazard element `[stat]`. Two more rules: repaint **does not reach behind brackets or
under the top rail** → model as a tonal split; **galvanizing fails at the welds and feet first** →
rust-map those, not the whole member `[stat]`. Grip: keep Ø34 as the compliant default and log
**Ø42.4 STS304** as the *retrofit variation* value, not an error `[stat]`.

#### D3 · Korean stainless shape vocabulary — **P1**

House style, recurring across independently sourced photographs `[stat]`: polished **spherical
newel ball** on terminal posts (almost never seen on Western handrails); **curved goose-neck
return** where the rail turns down into the post at a flight's foot; **turned / beaded ring
grooves** machined into balusters (a 1990s–2000s signature); balusters at ~100 mm centres (which is
also what the ≤100 mm 안목 rule produces `[law]`); and **a row of inverted-U stainless hoop guide
rails across the stair head**, perpendicular to travel — observed at both 삼일공원 and a 2024
station exit, a **standard fixture, and we have none**. The hoop row is the highest-value single
*new* prop in this map: a standard Korean street object with zero instances in 33 scenes.

#### D4 · Retrofit tactile as an adhered pad — **HOLD**

Statute names both constructions and sanctions the retrofit one: *"점자블록은 매립식으로 설치하여야
한다. 다만 … 현저히 곤란한 경우에는 부착식으로 설치할 수 있다"* — 편의증진법 시행규칙 별표1
제16호 `[law]`. So a glued pad is not a defect to excuse, it is the **lawful retrofit
construction**: proud **+6…+12 mm**, 1–2 mm dark adhesive perimeter, **outline not aligned to the
paver joint grid**, chamfered or strip-trimmed edges, 1–2 tiles with corner loss or replaced in a
fresher yellow. Product reality: 300 × 300 mm cast pavers in 60/80 mm, KS F 4561, ≥40 BPN, colour
layer ≥8 mm `[stat]`. Weathering, the highest-value detail: the colour layer abrades, so an old run
in a walked line is **grey with yellow surviving only at the edges**, not uniformly yellow
`[stat — Gamcheon photo set]` — which is exactly the D-rider that `TACTILE_YELLOW` currently
contradicts by painting every block brand-new saturated yellow.

**Blocked, two ways.** (1) Tactile is default-OFF by user decision and must not be flipped by an
implementer. (2) A proud 12 mm pad interacts with **GT-E1′** (`|x_e| ≥ 40 · z_e`): at 12 mm the
required clearance becomes **0.48 m > the statutory 0.30 m position**, so it needs the same
`GT-E2-x` / `EXPECTED_FP` registration as the flush case and must not be introduced without it
`[measured — era §5.3]`. Record the spec, build nothing.

#### D5 · Nosing tiers — **P1**

Three tiers, all real, currently collapsed into one chrome yellow:

1. **Retrofit metal**, verified product: aluminium profile **60 mm wide**, lengths **600–790 mm in
   10 mm increments**, ceramic-grit insert, stock colours black/grey/green/marble/yellow/purple/wine;
   other stock profiles 45 × 23 and 63 × 20 `[stat]`. Tells that follow from the install sequence:
   a regular row of screw heads **or** adhesive squeeze-out along both edges; a height step casting
   a shadow line at the uphill edge; the strip **ending short of the tread ends**; wear mismatch
   (strip scuffed to bare metal along the walked line while the stone is even, or the reverse).
2. **Paint only** — where there is no hardware budget: white paint on every nosing. 흰여울문화마을
   has concrete alley stairs with **no railing on either side** and white-painted nosings plus a
   white-painted open gutter as the *only* safety measure `[stat]`.
3. **Partial-width tile** — Gamcheon: ochre/tan patterned anti-slip tile mortar-set over **only the
   front ~150 mm of each tread**, the rest bare concrete `[stat]`. Reads instantly as an add-on.

And the statutory alternative that licenses *absence*: 편의증진법 별표1 제8호 마.(2) requires
*"계단코에 줄눈넣기를 하거나 …"* — **cast-in scored grooves and no strip at all is compliant**, so a
visible surface strip is almost always an add-on `[law]`. Colour: use **5Y 8.5/12 ≈ `#F0BE00`** from
산업안전보건법 시행규칙 별표8 for hazard bands and nosings instead of an invented yellow `[law]`.
This row also discharges 통람 v2's "chrome-yellow uniformity" flags on 16 · C4 · N4.

#### D6 · The scars of the operation — **P1**

The cheapest convincing retrofit props are not fixtures, they are damage `[stat]`: a **mortar
patch** disc 100–200 mm of brighter smoother mortar where an old post was cut off and a new one set
beside it; the **cut stub** of the previous rail left in the parapet (this repo already logs "허공
파이프 스텁" as a *defect* in scene15 — placed deliberately it becomes a feature);
**core-drill dust halo** plus four small spalls around a base plate; **two generations meeting
mid-run**, a stainless repaired span butting a painted-steel original with a mismatched joint
sleeve (scene12's 훼손 스팬 is the in-repo precedent for a per-span material break); a **colour break
in the tactile run** where a replaced batch is fresher; and **rust staining streaking down the stone
from the steel fixings** — the weathering tell that says the metal was added after the stone.

Look target, already held in-repo:
`Docs/reference_photos/expanded/wc005_ccby40_caddc6_삼일공원_1.jpg` (Sadang, 2020-08-31, **CC BY
4.0**) — original granite block stairs, stainless round handrail with a goose-neck return, a row of
stainless hoops across the head, a completely different reddish-brown timber-look railing on the
right, and a green PVC-coated mesh fence behind: **four fixture generations, none matching, none
removed**, with rust streaks down the granite `[stat]`. If any derivative of this photo is
published, the **CC-BY per-author credit ledger** entry is mandatory `[law]`.

### E. Site-specific empty-frame sets

#### E1 · D1 loading apron — **new-build (mixed)**, P0

The apron is **~65 % of the d5 frame with zero standing props** — the reason 통람 v2 still calls it
"pristine vector-clean" despite a PASS `[measured — C5 §2.9]`. Procedural (Korean specificity
required): **T-11 pallet 1,100 × 1,100 × 140–150** — KS T 1002, 2003 international standard; the
current 1,200 × 1,000 is the **EUR** size and not the Korean workhorse `[law/KS]`; wheel guides
3.4–3.6 m per dock with curb h 100–150; wheel stoppers 1,600 × 150 × 100; drainage trench +
grating 400 × 500 × 50 at 20–25 m `[law]`; roll containers 800 × 600 × 1,700; 200 L drums Ø572 ×
851; outdoor hydrant/extinguisher cabinet 700 × 800 × 250; Ø89 two-rail pipe guard h 900–1,100
`[stat]`. Also fix: dock bumpers are laminated **250 × 250 × ~500, two per door**, not a continuous
1.2 m array; roller-shutter slat pitch **80–120 mm**, not 300; ISO container dimensions are already
exactly right — add **corrugation + corner castings**, do not touch the dims `[measured]`.

CC0 drop-ins, all native usdc: **`korean_fire_extinguisher_01`** (9,913 tri — an explicitly Korean
scanned product), `Barrel_01` (2,682), `barrel_03` (1,473), `plastic_crate_03` (21,740),
`cardboard_box_01` (16,952), `hand_truck` (13,220), `old_tyre` (2,880), `power_box_01` (21,272),
`utility_box_01/02` (4,404 / 6,268), `trashbag` (4,482) `[measured]`. **No vehicles, no people** —
no forklift, no truck `[convention]`.

#### E2 · D2 construction slab — **rebuild-procedural**, P0

The internal `piles` are **single ellipsoids 3.4 × 2.3 × 0.84 m and 2.4 × 1.8 × 0.60 m**, ~5 % of
the d5 frame, reading as "a giant smooth bean". The external `mounds` were already fixed to a
3-lobe form in v2 — **`piles` is unrepaired residue of the same defect** `[measured]`. Rebuild as a
multi-lobe ridge with top relief. Then: rebar stubs Ø12 × 360 need **ribs, rust and a grid layout**
instead of random smooth copper rods; cement-bag pallets must be **kraft grey-brown**, not white
(currently adjacent to the near-white large-area prohibition); safety-fence bar pitch **250 → 100–150
mm** or mesh 50 × 150, and the chrome 0.50 colour → matt galvanized 0.6–0.7 `[measured]`. Keep: wire
reel, tower crane (far silhouette is sufficient). CC0 option for the **yard boundary only**:
`modular_chainlink_fence` (89,232 tri) — but a Korean site more often uses steel-panel 가설울타리,
so prefer procedural for anything in the primary cuts `[assumed]`.

#### E3 · D3 rural verge — **rebuild-procedural**, P0 / **HOLD**

The boundary fence is **one Box spanning x −22 … +96 = 118 m**, t 0.12, h 1.75, with **zero posts,
zero breaks, zero gates** — ~10 % of the d5/d10 background, and the reason it reads as a stage flat
`[measured]`. Rebuild: posts at 1.8–2.4 m, panel breaks, one gate `[assumed]`.

The four utility poles (Ø0.23 × h8.5, **white, constant section**, cross-arm box, **no insulators,
no transformer, no service drop**) should become KS F 4304 PC poles — grey, tapered (말구 Ø190 →
원구 ~Ø300 class), steel cross-arm with 2–6 insulators, earth wire `[law/KS]`. **HOLD**: §2.13② is
an open conflict — the convention bans urban infrastructure in "natural" scenes and lists D3 as
natural, while the scene header defines itself as *"도시 콘크리트 측구 / 교외 아스팔트 차도"* and the
지중화율 statistic (arterials 94.16 %, **all roads 59.2 %**) makes poles on a suburban back road
statistically normal `[stat]`. Either the classification or the convention needs amending; do not
start until it is ruled. CC0 `modular_electricity_poles` is rejected anyway (7 m, Western form,
200,610 tri).

#### E4 · scene15 alley service dressing — **replace-with-asset (CC0)**, P2

C3 P1 #10 asks for 1–2 utility poles + 보안등 + wires reintroduced to the alley — and alley scenes
(15 · 18) are the **only** place poles are permitted, since arterial 지중화율 is 94.16 %
`[stat, convention]`. CC0 objects that are place- and era-plausible for a 달동네 alley, all native
usdc: `exterior_aircon_unit` (18,986 tri, 1800 × 374 × 928 mm), `modular_metal_gutter` (16,490),
`rollershutter_window_01` (1,104), `utility_box_01/02`, `security_light` (4,668), `old_tyre`,
`Barrel_02` as a water drum `[measured]`. Korean-ness is *moderate* — these are generic urban
service objects rather than Korean-specific ones, and the audit's own defence line warns against
over-dressing (v5.1 told us to **cut** scene15 rooftop props). **Cap: 3 objects per alley segment,
each justified by "the scene cannot be read without it"** `[convention — v5.2 §6]`.

---

## 4. Work packages, modular per scene-type

Each package is independently schedulable and independently revertible, so a user gallery comment
on one scene type re-prioritises only its own package.

| Pkg | Scene type | Scenes | Rows | Blast radius |
|---|---|---|---|---|
| **WP-1 GLOBAL-KIT** | all | 33 | C1 bench · C2 streetlight · C3 bin · C4 pergola · C5 planter · C6 bollard form | `scene_common` / new `props_kit.py`. **Signature-preserving only.** Needs a supervisor-approved freeze window: shared-module edits are frozen during measurement, and `build_bollard`'s default change is a global-effect item |
| **WP-2 GROUND-VEG** | all | 22 | A1 weed → `Grass_Short_C` | `ground_kit._build_weed_band` + `_elem`/GT-E5 wiring. Touches the GT path → regression v2.1 + `geom_invariance` mandatory |
| **WP-3 PLAZA / CIVIC** | plaza, grand stair | 01 · 05 · 08 · 14 · 20 · 21 · N1 · N3 · C4 | B1a hedge un-rounding · B2b scene05 backdrop · C5 planter (01 = P0) · C6b bollard removals (14 · 20 · 21) · C7c sign posts | scene-local; no shared module |
| **WP-4 RETROFIT-5** | underpass / footbridge / levee / alley | **02 · 11 · 15 · 16 · 17** | **D1 base plates · D2 age ladder · D3 shape vocabulary · D5 nosing tiers · D6 scars** | scene-local + material constants. **Highest value per hour in the map.** D4 excluded (HOLD) |
| **WP-5 PARK / NATURAL** | park, riverside, temple, lake | 03 · 04 · 07 · 09 · 10 · 12 | B2a slope shrubs · B3 reeds · C4 pergola (C2) · B1b assets handed to midground | scene-local; `place_shrubs` already exists |
| **WP-6 ALLEY / VILLAGE** | 달동네, mural stair | 15 · 18 | B2d pots · E4 dressing (cap 3) · C2 pole → 벽부 보안등 (18) | scene-local |
| **WP-7 INDUSTRIAL / SITE** | yard, construction, rural | **D1 · D2 · D3** | E1 apron set · E2 piles + rebar + fence · E3 fence (poles HOLD) | scene-local; largest new-geometry volume |
| **WP-8 PLATFORM** | subway | D4 | C1b bucket seat · C7b 역명판/hanging/lightbox textures | scene-local; D4 is the library's only *worn* tactile reference — do not "clean" it |
| **WP-9 ROOFTOP** | rooftop | 19 | C7b blank billboards; rooftop equipment is the scene's own P0 package | boundary only |
| **WP-0 DELETIONS** | mixed | N4 · C1 · C4 · D2 · 12 · 14 · 16 | C7a (N4 `wall_plates` · C1 `signpost` · C4 `sculpture` · D2 slogan ×2) · C6b bollard removals (14 ×10 · 16 ×6 · 12 ×2) | **Do this first.** Smallest diff, resolves convention violations outright, zero side effects |

Recommended order: **WP-0 → WP-2 → WP-4 → WP-1 → WP-3/5/6/7/8**. WP-0 is free. WP-2 is one builder
for 22 scenes. WP-4 is the largest realism-per-hour ratio and touches no geometry. WP-1 must wait
for a freeze window because it edits shared modules.

---

## 5. Procurement ledger

### 5.1 Nothing to procure for the vegetation rows

All four vegetation replacements use USDs **already in `assets/vegetation/`**, all with a recorded
`verdict: PASS` in `assets/veg_manifest_w2.json` `[measured]`:

| Row | Asset | tri | native bbox (m) | Role in manifest |
|---|---|---|---|---|
| A1 weed | `Shrub/Grass_Short_C.usd` | **1,598** | 0.28 × 0.30 × 0.12 | `edge_weed` |
| B3 reed | `Shrub/Switchgrass.usd` | **8,934** | 2.01 × 2.03 × 1.37 | `riparian_grass` |
| B2a/B2b shrub | `Shrub/Boxwood.usd` / `Privet.usd` | 178,000 / 147,000 | h 0.741 / 1.114 | `SHRUB_HEDGE` |
| B2a ornament | `Shrub/Rhododendron.usd` / `Juniper.usd` | 55,000 / 200,000 | h 2.013 / 0.898 | `SHRUB_ORNAMENT`, flower prims auto-disabled |
| B1b hand-off | `Trees/Elm_Sapling.usd` / `Gray_Birch.usd` | 113,268 / 256,625 | h 3.09 / 3.33 | midground belts |

Licence line for all of the above: **NVIDIA Omniverse `Assets/Vegetation` — render and dataset
publication permitted; USD not redistributed; no ML-restriction clause found** `[law]`. This is the
regime already in force for the repo's 30 vegetation USDs, so **no new licence exposure is created
by any row in this map's vegetation set.**

### 5.2 CC0 downloads worth making (Poly Haven, all native `.usdc`)

Poly Haven is **CC0 1.0**, redistribution and ML use explicitly permitted; attribution is
appreciated but not required, and CREDITS.md already carries the quoted licence text `[law]`. New
CREDITS.md rows are therefore a **reproducibility record**, not an obligation.

| Asset | tri | dims (mm) | usdc | Author | Used by |
|---|---|---|---|---|---|
| `korean_fire_extinguisher_01` | 9,913 | 280 × 367 × 659 | 0.54 MB | UM JOORIN | E1 (D1), D2, D4 |
| `Barrel_01` | 2,682 | Ø563 × 880 | 0.22 MB | Jorge Camacho | E1, E4 |
| `barrel_03` | 1,473 | Ø639 × 930 | 0.08 MB | Serhii Khromov | E1 |
| `plastic_crate_03` | 21,740 | 481 × 265 × 266 | 1.09 MB | Pacific Penguin | E1 |
| `cardboard_box_01` | 16,952 | 387 × 516 × 342 | 0.84 MB | Rahul Chaudhary | E1 |
| `hand_truck` | 13,220 | 593 × 693 × 1403 | 0.58 MB | Mutanzom3D | E1 |
| `old_tyre` | 2,880 | 600 × 165 × 600 | 0.15 MB | MP | E1, E4 |
| `power_box_01` | 21,272 | 377 × 418 × 503 | 1.05 MB | Rico Cilliers, Yann Kervran | E1, E4 |
| `utility_box_01` / `_02` | 4,404 / 6,268 | 520/920 × 432 × 1120 | 0.23 / 0.33 MB | James Ray Cock | E1, E4 |
| `trashbag` | 4,482 | 528 × 463 × 575 | 0.07 MB | Benny Weimer | E1, E4 |
| `exterior_aircon_unit` | 18,986 | 1800 × 374 × 928 | 0.50 MB | Monsta3D | E4 |
| `modular_metal_gutter` | 16,490 | 2268 × 1515 × 1843 | 0.82 MB | Maxim Domnin | E4 |
| `rollershutter_window_01` | 1,104 | 5100 × 300 × 1851 | ~0.04 MB | MP | E4 |
| `security_light` | 4,668 | 323 × 417 × 531 | 0.24 MB | Maximilian Schuster | E4 |
| `metal_trash_can` | 13,960 | 1847 × 556 × 906 | 0.68 MB | GurJas Studios | C3 (alley/yard only) |
| `modular_chainlink_fence` | 89,232 | 8115 × 2149 × 2523 | 4.35 MB | James Ray Cock, Amal Kumar | E2 boundary only |

Total if all taken: **~11.8 MB usdc + textures, ~253k triangles**. Two integration notes: Poly Haven
model URLs return **403 without a User-Agent header**, and `metersPerUnit` must be read per asset
exactly as `add_vegetation` already does — do not assume 0.01 `[measured]`.

### 5.3 Explicitly not procured

- **DriveSim street furniture** — `bollard_01`, `bench_curved_01`, `bench_wrought_iron_02`,
  `trashcan_cylinder_01/square_01`, `bike_rack_01`, `planter_round_02`, `safety_railing_01`,
  40+ `streetlamp_*`. Rejected on **Korean-ness**, not licence (see the R1 dual-root correction in
  §2.2). If any is ever fetched, it must come from `Isaac/4.5/NVIDIA/dsready_content/`, never from
  `Isaac/Environments/Outdoor/Rivermark/` `[law]`.
- **Anything under `Isaac/Environments/**`** — Limited Use, "without modifications" `[law]`.
- Quixel Megascans (NoAI) · Mixamo / RenderPeople · brand vehicles `[law — ZZ §10.6]`.
- All 16 CC0 plant scans (§2.4 — season gate and/or 1.0–1.75 M tri).
- `modular_street_seating`, `street_lamp_01/02`, `planter_box_01–03`, `modular_electricity_poles`,
  `water_manhole_cover` (§2.3).

---

## 6. Do-not-touch line

Carried from `C4 §8` and extended by this map. An implementer who "fixes" any of these is
introducing a regression.

1. **Angular hedge box form** — deliberate (Korean 전정 관행). Only the crown blobs and the missing
   breaks are in scope `[convention + C4 §1.5]`.
2. **scene17 stairs with no handrail** — 한강 제방 practice; `cue_railing=False` stays `[stat]`.
3. **scene18 has no bollards** — no carriageway, so the v5.1 deletion was correct `[law]`.
4. **Equal streetlight spacing is correct** — the "no equal spacing" rule is about decorative
   placement, not photometric or street-tree design (street trees are legally 4–8 m on centre)
   `[law, assumed]`.
5. **No water tank on scene19** — the evidence runs the other way `[stat]`.
6. **Do not switch tactile ON**, and do not add tactile pads under bollards — the conflict is real
   and the resolution is the supervisor's, not the implementer's `[convention]`.
7. **No seasonal or event-specific element** in any prop proposed here — verified: nothing in this
   map introduces blossom, autumn colour or holiday dressing, and every plant row uses a
   pixel-verified PASS asset `[measured]`.
8. **No atmospheric perspective** to hide far detail — measured Seoul extinction gives only
   2.6–7 % contrast loss at 90 m `[measured]`.
9. **No poles on 17 / 20** (arterial and plaza; 지중화율 94.16 %); 15 and 18 only `[stat]`.
10. **No people, no vehicles** — including forklifts and trucks in D1 `[convention]`.
11. **Manhole is closed** (W2 F5). **D-5 scatter is closed** (W2 F2/F3). Do not re-litigate.
12. **ISO container dimensions in D1 are exactly right** — add corrugation and corner castings, do
    not adjust the box `[measured]`.
13. **sceneD4's worn grey-ochre tactile strip is the library's only correct worn tactile** and the
    reference target for D5/§6.2-D. Do not clean it up `[measured]`.
14. **Triangle count is not the budget** — instanceability is. Do not reject a row on instance
    count `[measured]`.

---

## 7. Method and evidence

- **Code measurement, no boot, no GPU.** `PARAMS` blocks were AST-parsed and module-level
  assignments evaluated in isolation (the convention used by `verge_instances`); builder bodies were
  read for prim composition and dimensions; `scene05.backdrop_instances()` and
  `build_hedge`'s crown formula were **re-implemented and run** to get exact counts (52 clumps /
  337 lobes; 4–48 crowns per band). `GROUND_PROFILES × SCENE_PLANS` was crossed to get the weed
  spread (22 scenes / 139 cubes).
- **Asset measurement over the wire.** Poly Haven `/assets`, `/info`, `/files` were enumerated this
  session: 521 models, 333 keyword hits, 207 outdoor-category entries; `polycount`, `dimensions`
  (mm) and per-format file sizes are the API's own values. `usd` format availability was confirmed
  per asset.
- **Season pixel verification.** 1k diffuse atlases were downloaded for 16 plant candidates and run
  through a re-implementation of the project's `gate_woody` / `gate_turf` (HSV hue bands, saturation
  > 0.15, sRGB → linear Rec.709 luma), matching `veg_manifest_w2.json`'s stated method at the
  texture level. Difference from the veg team's pass: they sampled **UV-mapped foliage pixels**;
  this pass reads the **whole atlas**, so a FAIL is a conservative screen, not a final ban.
- **Not done:** no render, no Isaac, no Isaac-python, no `pxr` (usd-core is absent from the project
  venv, so no triangle count was measured from a downloaded USD — Poly Haven's `polycount` is used
  instead, and the in-repo counts come from `veg_manifest_w2.json`). No tracked scene file or shared
  module was modified. No commit.

### Open questions for the supervisor

1. **§2.13① bollard front tactile** (a/b) — blocks C6c and half of D4.
2. **§2.13② sceneD3 classification** (natural vs suburban) — blocks E3b.
3. **§2.13③ sceneD4 PSD absence** — does not block this map, but decides whether D4's signage
   should read as a 1990s pre-PSD station (which would change the C7b texture design).
4. **`build_bollard` / `build_bench` / `build_canopy` / `build_planter` default changes are
   33-scene-global** and require an approved shared-module window (WP-1). `build_railing_line`'s
   baluster gate (C1 C0-7) is the same class of change and is the other agents' P0 — coordinate so
   the two do not collide in the same freeze window.
5. **Era rider B** (rail height 0.90 → 1.10 outdoors, scene19 → 1.1 m) overlaps C6/D-rows and is
   listed in era §6.2 as needing a ruling; this map assumes it lands and does not pre-empt it.
