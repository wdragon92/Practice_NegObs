# W3 intake — scenes 06–10 + two pan-scene policy reversals

> **Wave**: W3 · **Task**: intake (verification + spec drafting, **no code / scene edits, no commits**)
> **Date**: 2026-07-30 · **Branch**: `feat/realism-v1` · **Repo**: `/home/vislab/Desktop/work_sy/Practice_NegObs`
> **Renders inspected**: `look_check/scene{06..10}/260730_w2d_fix/` — 13 preset + 4–5 miseen cuts per scene
> (17 · 15 · 16 · 14 · 14 PNG respectively, all read at full res; crops re-rendered at 2.4–8× for edge reads).
> **Method**: renders read at native + magnified crops; scene `PARAMS` extracted by AST-exec without booting USD
> (`pxr` is **not installed on this machine** — every geometric claim below is analytic, recomputed from the
> authoring code, not measured off a stage); shared builders re-derived by hand and cross-checked numerically.
> **Files written**: this file only.
>
> **Evidence tags**: `[measured]` recomputed/re-read this session · `[render]` read off a named cut in
> `260730_w2d_fix` · `[law]` statute or standard text fetched this session · `[photo]` real photograph opened and
> looked at this session (URL + licence in §8.1) · `[cite]` in-repo document quoted · `[assumed]` stated inference.
>
> **The bar for this wave (user, overriding)**: not "plausible" — **each scene must match real Korean samples**
> ("실제 표본 확인해서 똑같게"). Rows below carry an **EV** grade: `EV-A` = photo-backed at n≥5 or statute;
> `EV-B` = photo-backed at n<5, needs topping up; `EV-C` = **evidence gap, do not execute until closed**.

---

## 0. Spec rows at a glance

| # | Row | Scene(s) | Kind | EV | Blocks on |
|---|---|---|---|---|---|
| **P-1** | Placement jitter **abolished** — sources found from the 06–10 side (**merge into `w3_intake_policy.md` §3.2**, see §1.0) | pan | policy reversal | A `[cite]` | — |
| **P-2** | Street trees = **one species per scene/route** (**also in `w3_intake_policy.md` §4**, see §2 note) | pan (13 scenes, 20 call sites) | policy reversal | A | — |
| **S06-A** | Footbridge/spiral **shape breakage** — 3 stacked causes | 06 (+05, 19 share the builder) | defect | A `[measured]` | — |
| **S06-B** | Korean road/sidewalk **curb step** — 06 is compliant, 5 scenes are not | 06 + pan audit | defect | A `[law]` | — |
| **S07-A** | Temple stone stair = **wrong archetype** (groundwork only) | 07 | rebuild | B → user refs | **user refs — DO NOT FINALIZE** |
| **S07-B** | Stone yaw/tilt/lateral jitter (folds into P-1) | 07 | policy | A | P-1 |
| **S08-A** | Plaza **bollard + tape barrier** — remove | 08 | removal | A `[photo]` | supervisor (reverses `tonglam_v2` §1) |
| **S08-B** | What replaces it at those positions | 08 | spec | B | S08-A |
| **S09-A** | **Stair-side diagnostic cuts** — 3 new miseen cuts | 09 | cuts | A `[measured]` | — |
| **S09-B** | What the ghat stairs currently are (baseline record) | 09 | record | A `[measured]` | — |
| **S09-C** | Mooring posts embedded in the stair face (bonus) | 09 | defect | B | — |
| **S10-A** | Deck reads as **apartment emergency stair** — diff (groundwork) | 10 | rebuild | B → user refs | **user refs — DO NOT FINALIZE** |

---

## 1. Policy reversal P-1 — placement jitter is abolished

**Ruling (supervisor, this wave)**: aligned / orthogonal is the real default. The prior rule that created every
source below is `Docs/audit_v4/user_feedback_v5_1.md` §전역 현실성 규약 3 `[cite]`:

> "**배치 비정형**: 벤치·조형물은 앵커(나무 그늘·벽·화단) 옆에, 격자 정렬·등간격 금지, **yaw ±3~8° 지터**."

That clause is now void for **yaw**. The anchor half of the clause ("beside a tree / wall / planter, not
mid-field") is **not** reversed — it is a placement-*location* rule, not an orientation rule.

### 1.0 Consolidation with the sibling wave docs — read this first

Two other W3 intake documents exist in this same directory and were written in parallel this session:
`Docs/surveys/w3_intake_policy.md` (agent: policy) and `Docs/surveys/w3_intake_01_05.md` (agent: scenes 01–05).
**`w3_intake_policy.md` §3.2 is the authoritative pan-scene jitter inventory** — it covers 225 grep hits including
`scenes/batch1/` (`batch1_common.jit_yaw` / `jit_pos`, 18 call sites), which this document did not scan.
My §1.1 must be **merged into** it, not shipped alongside it. Mapping:

| My ID | Their ID | Status |
|---|---|---|
| J1 (stain ±22°) | J-2 | **duplicate** — identical finding, identical line |
| J2 (patch ±14°) | J-1 | **duplicate** |
| J3 (footprint ±6°, KEEP) | (b) #18 | **agreement**, and they additionally found an AABB bug (their §3.6) — defer to them |
| J4 bench literals 01/03/04/06 | J-5 rows 5,6,8,9 | **duplicate for 01/03/04/06** |
| J4 bench literals **09 / 13 / 17 / 05 planters** | — | **NEW — not in their inventory.** Carry these rows across. |
| J5 (scene07 stones rz/rx) | — | **NEW.** See ruling correction below. |
| J6 (scene07 knob rz/rx) | — | **NEW** |
| J7 (leaf-patch rz 07/10) | — | **NEW** |
| J8 (tree yaw 0–360, KEEP) | (b) #17 | **duplicate, agreement** |
| J9 (tree-band, KEEP) | (b) #10-16 family | **agreement** |

> **Ruling correction on J5, to stay consistent with an already-adopted decision.**
> `w3_intake_policy.md` §3.2(b) #19 adopts "A's J14 ruling": `build_worn_stone_stairs(jyaw=3.0)` is **KEPT**,
> because *hand-set masonry genuinely is laid a few degrees out*. scene07's stones are a different code path
> (the scene explicitly declines that builder, `scene07:44-46`) but they are **the same physical object class**.
> I therefore withdraw the blanket "abolish yaw" on J5 and restate it: **the archetype errors in scene07 are the
> 0.05–0.29 m inter-stone gaps and the ±0.35 m lateral `cy` offset, not the ±4° yaw.** Cap yaw at the adopted
> ±3° and keep a small bedding tilt; abolish the gap and the lateral offset. This is a **scene07 archetype
> question (S07-A), not a P-1 question**, and it is on hold for the user's reference images either way.

### 1.1 Every jitter source found `[measured]`

| Src | File:line | What it rotates | Range | Verdict |
|---|---|---|---|---|
| J1 | `scenes/main/ground_kit.py:1027` | free-form stain decals (soil / water / oil / gum blots) | `rotz = ±22.0°` | **ABOLISH** — this is the "W2-D decal yaw ±22°" the ruling names |
| J2 | `scenes/main/ground_kit.py:689` (`build_patch_field`, default `yaw_max=14.0`), applied at `:734` | repair patches (아스팔트 덧씌우기 패치) | `rotz = ±14.0°` | **ABOLISH** — this is the "±14°" the ruling names |
| J3 | `scenes/main/ground_kit.py:1072` | footprint decals | `ang ± 6.0°` about the path bearing | **KEEP** — a footprint is not a laid object; it has no build axis. Flag to supervisor rather than delete silently. |
| J4 | per-scene `PARAMS` bench / planter yaw literals (see 1.2) | benches, planters, terrace benches | −11° … +5° off-orthogonal | **ABOLISH** — snap to 0 / 90 / 180 / 270 (or the scene's own `rot`) |
| J5 | `scenes/main/scene07_temple_stone_path.py:168` `stones=dict(… rz=4.0, rx=2.5 …)` + `cy` offset ±0.35 (`:500`), consumed `:485-486`, applied `:1116-1120` | every stepping stone | yaw ±4.0°, tilt ±2.5°, lateral ±0.35 m | **CAP yaw at ±3.0°** (adopted J14 ruling, see §1.0) · **keep bedding tilt** · **ABOLISH the ±0.35 m lateral offset**. Moved to S07-A — this is an archetype question, not a jitter question. |
| J6 | `scene07:178-179` `knob=dict(rz=(10,20), rx=(3,9))`, applied at `:1123-1127` | the "canted knob" lump on each stone | yaw ±10–20°, tilt ±3–9° | **ABOLISH with the knob itself** — see S07-A; the knob exists only to break a rectangular silhouette that the correct archetype does not have. |
| J7 | `scene07:242,248` (`leaf_band.sub_rz=26.0`, `yard_leaf.rz=30.0`), applied `:558-559, 1140-1148`; `scene10:284` (`leaf_patch.rz=32.0`), applied `:1284-1291` | leaf-drift decal patches | ±26° / ±30° / ±32° | **ABOLISH as a rotation**, but do **not** simply axis-align — see note below |
| J8 | `scenes/main/scene_common.py:2456` `yaw_deg=rnd.uniform(0, 360)` | whole-tree yaw | 0–360° | **KEEP** — a tree has no build axis. Explicitly exempt in the spec so nobody "fixes" it later. |
| J9 | `scene06:1427-1436` tree-band height/offset jitter | distant tree band | h ±1.2 m, dy ±0.8, dx ±1.5 | **KEEP** — vegetation, not placed objects. |

**Note on J7 (leaf/stain/patch decals)**: `tonglam_v2.md` §2.13-2 `[cite]` records that these decals were rotated
*because* axis-aligned ones read as "photographic rectangles laid on the DG". Deleting the rotation without
touching the mask reinstates that defect. The correct execution is **rotation → 0, and the rectangle stops being
a rectangle** (irregular / feathered mask, already scoped as fix **F3** in `tonglam_v2.md` §3). **P-1 and F3 must
land in the same commit for 03 · 07 · 10 · D3 · C2**, or those scenes regress.

### 1.2 Bench / planter yaw literals to snap (J4) `[measured]`

Values are the yaw field of each per-scene tuple (index verified per scene against the builder call):

| Scene | Field | Current yaws | Snap to |
|---|---|---|---|
| 01 | `benches[i][4]` | −6, +4, −5, +3.5, −7, +5 | 0 / 90 / 180 |
| 03 | `benches[i][3]` | +5, 172, 93 | 0 / 180 / 90 |
| 04 | `benches[i][3]` | 96, 94, 4.5, 93, 87 | 90 / 90 / 0 / 90 / 90 |
| **06** | `benches[i][2]` | **−6, +5, 175** | 0 / 0 / 180 |
| **09** | `benches[i][2]` (`scene09:269-270`) | **86.5, 274.0, 93.5, 265.5** | 90 / 270 / 90 / 270 |
| 13 | `benches[i][2]` | 174, −6, +3 | 180 / 0 / 0 |
| 17 | `terrace_benches[i][2]` | 96, −84, 93, −86 | 90 / −90 / 90 / −90 |

**Not jitter — do not touch**: `scene18` benches/planters all carry **−2.57°** and `scene20` carries a `rot` key;
these are a *scene-wide skew* (the whole quay/diagonal is rotated), not per-instance jitter. Verify against each
scene's `rot`/`quay` param before editing. `scene05 seat.arcs` angles (80.5, 99.5, 112.5) are **arc spans in
degrees**, not yaws.

**Regression risk**: yaw feeds `_obb_aabb` in `ground_kit.py:564-572`, which feeds `_elem(...)` region containment
and the GT-E2 verdict. Setting yaw→0 **changes every decal AABB** and therefore can move GRAZE/OCCL verdicts.
Budget a full 33-scene judgement round after P-1, not a spot check.

---

## 2. Policy reversal P-2 — one street-tree species per scene/route

**Current mechanism (the thing to change)** `[measured]` — `scenes/main/scene_common.py:2441-2444`:

```python
if LOOK_GEO and veg_available():
    # The species is decided by a coordinate hash - identical on re-running the same scene, and different per tree.
    pool = [t for t in veg_pool() for _ in range(t[2])]
    rel, native, _ = pool[rnd.randrange(len(pool))]
```

`rnd` is seeded **per tree** from that tree's own coordinates (`scene_common.py:2438-2439`), so **every tree draws
its species independently**. The pool is the weight-expanded `VEG_TREES` (`scene_common.py:2118-2125`):
Elm_Sapling ×4, Shumard_Oak ×3, Chinese_Juniper ×2, White_Pine ×1, Yellow_Pine ×1 = **11 slots, 5 species**.

- P(a 20-tree row is monospecific) = (4/11)^20 ≈ **1.4 × 10⁻⁹** `[measured]`. Mixing is not a tuning problem, it
  is guaranteed by construction.
- scene06 alone plants **20 street trees** on one verge row (`scene06:255-260`), built through this path at
  `scene06:1393`. `[render]` `pt_noon_ground_approach.png` shows a conifer standing between two broadleaves in
  that single row.
- **20 call sites over 13 scenes** in `scenes/main/` route through `build_tree` `[measured]`: 01, 03, 04, 05, 06,
  07 (×3), 09 (×2), 10 (×2), 11, 12, 13, 14 (×2), 17 (×3). **`w3_intake_policy.md` §4.1 finds 25 sites over 17
  scenes** — it also scanned `scenes/batch1/` (`bc.build_tree`) and caught `build_planter`'s internal call at
  `scene_common.py:2564`, which I missed. **Take their count**, not mine.
- Worst semantic case: `scene07:1268` builds prims literally named `Pine_{name}` for a **temple courtyard pine
  group** — and then draws elm / oak / juniper for them.

**Real-sample basis** `[law]` `[assumed]`: Korean street-tree practice is route-uniform — 「도시숲·생활숲·가로수
조성·관리 기준」 and 산림청 「가로수 조성·관리 추진계획」 both direct 가로변 planting to be selected for
**경관의 조화와 연속성** (landscape harmony and continuity) so that a "조잡한 경관" is not produced. The
statistical corollary is already in our own code comment (`scene_common.py:2107`): Seoul 2019, 306,313 street
trees, **ginkgo 35.8 % + London plane 20.9 %** — a concentration only reachable if routes are monocultures.
→ **EV note — superseded, in a good way.** The wording I reached is only a *continuity* directive.
`w3_intake_policy.md` §4.2 `[cite]` found the explicit clause I could not: 조례 제7조1호라
***"같은 노선과 도로 양측에는 같은 수종"*** (same species on the same route and on both sides of the road),
plus 시행규칙 *"노선별·구간별로 수관의 모양과 높이를 일정하게 유도"* and a 산림청 고시
*"동일 노선 동일 수종 권장"*. **Cite theirs, not mine.** That moves P-2 to a clean **EV-A `[law]`** and the
photo top-up becomes optional rather than blocking.

**Build spec (P-2)**

1. `build_tree(...)` gains `species=None` (a `VEG_TREES` relative path, e.g. `"Trees/Elm_Sapling.usd"`).
   When set, skip the pool draw at `scene_common.py:2443-2444` and use it directly. Signature stays
   backward-compatible, so no scene is forced to change (`build_tree` already advertises signature stability at
   `scene_common.py:2433`).
2. Per-scene **route → species** table in each scene's `PARAMS` (e.g. `veg=dict(street="Trees/Elm_Sapling.usd",
   backdrop=None)`), one entry per *named row*, not per tree.
3. **Keep the pool for backdrop woodland only** — `treeband` / `far_trees` / `RidgeTree_*` / `HillTree_*` are a
   forest, and a mixed forest is correct. The rule is per **street row / allée / courtyard group**.
4. Species per scene must respect the season lock and the pixel-verified green set
   (`scene_common.py:2126-2129`): Elm_Sapling, Shumard_Oak, Chinese_Juniper are PASS; `Japanese_Cherry` is
   **deleted, not deprioritised** (`scene_common.py:2101`) — do not reintroduce it as a "Korean" species.
5. Leave `yaw_deg=rnd.uniform(0,360)` (`scene_common.py:2456`) untouched — see J8.
6. Per-instance height variation (`±8 %`, `scene_common.py:2449`) stays: real rows are one species at varying age.

**Suggested assignments** (needs the supervisor's sign-off, one line each):
06 street row → `Elm_Sapling` (near-field 3 m, zelkova substitute — the correct Korean street reading);
07 courtyard "pines" → `Chinese_Juniper` (the code's own note at `scene_common.py:2122` calls it "most common in
temple, government and school landscaping"); 09 park row → `Shumard_Oak`; 10 trail → `Elm_Sapling`.

---

## 3. scene06 — `/World/Scene06`

### S06-A · Footbridge shape breakage

**User quote**: "footbridge shape breakage — find it in renders (which cut, which prim) + root cause".

**Where it is** `[render]`

| Cut | What breaks |
|---|---|
| `look_check/scene06/260730_w2d_fix/pt_noon_broken_rail.png` | **worst**. Frame centre is the spiral outer edge at azimuth 225°, r 3.3, z 4.16 (from `build_views`, `scene06:979-980`). The rim of the tread ribbon is not a curve: it breaks into **overlapping trapezoidal flaps at mismatched heights**, with open triangular gaps between them showing the shadowed drum below. |
| `pt_noon_deck_entry.png` | The landing/deck plateau bulges into a lumpy dome, and at frame-right the slab tears open into **V-shaped notches** that open onto the void. |
| `pt_noon_ground_graze.png` | Same rim, read from below: the "concrete" edge silhouette is scalloped instead of helical. |

**Which prims** — `/World/Scene06/Spiral/Step_*`, `/World/Scene06/SpiralFascia/Seg_*`,
`/World/Scene06/Landing/Seg_*`, `/World/Scene06/Deck`, `/World/Scene06/RailPostOuter_*`.

**Root cause — three independent defects stacked, all analytic** `[measured]`

**(A-1) The fascia top line ramps while the treads step — a 192 mm sawtooth upstand, 26× round the helix.**
`scene06:426-432`:

```python
def _fascia_z(a_deg):
    return _spiral_z_at(a_deg) + sp["riser"] * PARAMS["fascia"]["z_off"]
```

The fascia (`scene06:155-156`, r 3.22–3.33, i.e. it **overlaps the outer 80 mm of every 3.30 m tread**) is built by
`build_helix_ramp` with a **linearly interpolated** top line, while `build_helix_steps` gives each tread a
**constant** top z. With `riser 0.192`, `z_off 0.30`:

- at each step **start** the fascia stands **+153.6 mm above** the tread face;
- at each step **end** it sits **−38.4 mm below** it.

So the outer rim is a lip that rises to 154 mm, tapers to zero, inverts to a 38 mm overhang, and jumps back —
**26 times**. That is exactly the flap-and-notch pattern in `pt_noon_broken_rail`. The docstring claims it "erases
the chord sawtooth"; it does, and replaces it with a **z sawtooth an order of magnitude larger**.

**(A-2) Constant-chord segment boxes — the shared arc/helix convention is geometrically wrong at the inner radius
and overshoots at the outer one.** `scene_common.py:1637` (`build_arc_steps`), `:1847` (`build_helix_steps`),
`:1891` (`build_helix_ramp`) all use one tangential width for the whole radial span:

```python
chord = 2.0 * r_out * math.sin(dth / 2.0) * 1.03   # constant for r_in..r_out
```

A true annular sector's width grows linearly with radius. Measured consequences:

| Element | r_in..r_out | Δθ | box width | true width @r_out | **@r_in** | outer corner radius | **rim sawtooth** |
|---|---|---|---|---|---|---|---|
| `Spiral/Step_*` (26) | 1.50–3.30 | 11.538° | 683.3 mm | 663.4 mm (1.030×) | 301.5 mm → **2.27×** | 3.3176 m | **+17.6 mm** past r_out |
| `Landing/Seg_*` (24) | 0.48–3.30 | 7.500° | 444.6 mm | 431.7 mm (1.030×) | 62.8 mm → **7.08×** | 3.3075 m | +7.5 mm; union outer radius swings **3.3000 → 3.3990 = 99.0 mm** |
| `SpiralFascia` (150) | 3.22–3.33 | 2.000° | 119.7 mm | 116.2 mm | 111.9 mm (1.07×) | 3.3305 m | +0.5 mm (fine — fine segmentation hides it) |

Plus **23 coplanar overlap bands** of 12.9 mm along the landing top face (all segments at exactly z 4.998) — two
coincident surfaces with the same material, which is what produces the surface acne and the shard slivers.
This is **not a new discovery in the repo**: `scene05:37-40` `[cite]` already diagnosed the same convention
("the build_arc_steps chord length (based on r_out) reaches down to r_in, giving a crescent gap (15.3 mm) and an
arc-end sliver (42 mm)") and fixed it *locally* by raising `seg 3→12`. scene06's landing at `seg=24` over 180° is
**still in the failure regime** and nobody carried the lesson across. `scene19:265` `[cite]` carries a third
independent note about the same 1.03 factor.

**(A-3) The landing slab passes straight through the deck slab.** `[measured]`
`Deck` (`scene06:172, 1287-1291`) = box x 2..5, y −13..13, top 5.000, bottom 4.650.
`Landing` (`scene06:165-166, 1240-1242`) = half-annulus, centre (3.5, −13), r 0.48–3.30, azimuth 0–180 → footprint
x 0.20..6.80, y −13.00..−9.70, top 4.998, base 4.498. Overlap footprint **3.0 m × 3.3 m = 9.9 m²**; the landing's
top face sits **2 mm** under the deck's, and its body runs **348 mm** up through the deck box. Two solid slabs,
same concrete-family materials, interpenetrating over ten square metres.

**(A-4, minor, same family) Outer railing posts stand outboard of the walking surface.**
`scene06:238` sets `railing.outer_r = 3.36`; `_posts("Outer", rl["outer_r"], …)` at `scene06:1521` therefore
places post centres 60 mm **outside** the tread edge (r 3.30) and 30 mm outside the fascia face (3.33). In
`pt_noon_broken_rail` the teal posts read as piercing the rim and standing on the drum. Real RC spiral footbridge
railings are set **inboard** of the nosing line.

**Build spec (S06-A)**

1. **Fix the shared convention, once, in `scene_common.py`** — replace the constant-chord box in
   `build_arc_steps` / `build_helix_steps` / `build_helix_ramp` with either
   (a) a **true annular-sector mesh** (4 radial corners per segment, no scale-op box), or
   (b) if prim-budget rules forbid meshes, keep boxes but **cap Δθ so the r_in overwidth ≤ 1.05×**:
   `seg ≥ (a1−a0)/Δθ_max` with `Δθ_max = 2·asin(1.05 · r_in / r_out · sin(Δθ/2))` — for scene06's landing that is
   `seg ≈ 165` (r_in 0.48/r_out 3.30 is a 6.9:1 ratio, so boxes are simply the wrong primitive here), and for the
   spiral treads `seg` per step ≈ 3. **Recommend (a).**
   *GT invariance*: r_in, r_out, azimuths and top-face z must be unchanged, exactly as `scene05` §37-40 required.
2. **Drop the 1.03 margin to 1.000 once (a) lands** — the margin exists only to close wedge gaps that a true
   sector does not have. Keeping it is what creates the 23 coplanar overlap bands.
3. **Fascia**: make the top line *stepped*, matching the tread it wraps — one fascia segment per tread, top z =
   that tread's z + a fixed 20–30 mm nib, riser face vertical. This is also what a real RC spiral looks like
   (a stepped 옆판/거푸집 line, not a helicoid). Delete `z_off` or repurpose it as the nib height.
4. **Landing ↔ deck**: cut the landing's azimuth span so it stops at the deck edge, or subtract the deck
   footprint from it. Non-negotiable: **one walking surface at one z** across x 2..5, y −13..−9.7. Set landing
   `top_z = 5.000` (equal to the deck), not 4.998 — the 2 mm was a Z-fight dodge that no longer applies once the
   overlap is gone.
5. **Railing**: `outer_r` 3.36 → **3.24** (post centre 60 mm inboard of the nosing, standard for a 1.1 m guard on
   a 1.8 m-wide flight). Re-derive `_pipe_arc` radii from it.
6. Add a `spiral_selfcheck()` in the scene, in the house style
   (`scene05.podium_step_selfcheck` / `scene09.roof_normal_selfcheck`), asserting:
   rim radius spread < 5 mm · no two slabs with |Δz_top| < 20 mm sharing footprint · fascia top ≥ tread top for
   the whole span · every post centre ≤ r_out − 0.05.

**Affected scenes**: 06 primarily. The convention fix touches **05** (10 `build_arc_steps` call sites),
**19** (4 sites), **13** (`build_helix_ramp`, the car-park ramp). Those three must be re-rendered and re-judged in
the same round — expect silhouette changes, so **archive the current judge baselines before touching
`scene_common.py`**.

**Dependency**: none upstream. Downstream: any GT recompute that reads tread/landing top faces (values are
designed to be invariant — prove it with a prim-hash / GT-delta diff, as commit `96968f3` did for the comment
translation).

---

### S06-B · Korean road/sidewalk curb step (보차도 단차) — and the pan-scene audit

**User quote**: "the missing Korean road/sidewalk curb step (보차도 단차 — statutory 100-250mm, check what
scene06 actually builds between road and walk; likely a pan-scene audit)".

**Statutory basis** `[law]` — 「도로의 구조·시설 기준에 관한 규칙」 제16조(보도): where a curb separates
carriageway from footway, its height is to be **25 cm or less**; the customary built range is **15–25 cm**
(MOLIT 「보도 설치 및 관리지침」; see §8.2 for URLs). Our own `scene_common.py:304` already records the companion
detail from **MOLIT directive no. 321, 보도설치 지침 figure 2.17**: *vertical curb, R = 10 mm* `[cite]`.

**Finding 1 — scene06 is compliant. The item is not "missing" here.** `[measured]`

`scene06:213, 222-224` and the builder at `scene06:1170-1176`:

```
road.z_top = -0.150   walk.z_top = -0.005   curb = dict(w=0.60, z_top=0.0, thick=0.40)
→ curb top 0.000  |  exposure above carriageway = 150 mm  ✔ (statutory ≤250, customary 150–250)
→ curb stands 5 mm proud of the footway  ✔ (real curbs are flush to +20 mm)
→ curb face at y = ±8.00 = the carriageway edge  ✔
```

`scene11` is identical. `[render]` at 8× on `pt_noon_ground_approach.png` the curb **is** visible as a continuous
dark band at both road edges. So the scene06 row is not "add a curb" — it is **three legibility defects**:

- **B-1 material**: `M["curb"]` is bound to `granite_dark` (`scene06:1091-1094`). Korean 연석 is
  화강석 or precast concrete — a **light grey**. `scene01:235` `[cite]` already recorded that "granite_dark
  (kerb, bands) reads as a black hole". At distance the curb reads as a painted black stripe, not a 150 mm step.
- **B-2 monolith**: the curb is **one box 140 m long** (`scene06:1174-1176`). Real 연석 is a unit product
  (typically 1 m lengths); the joint rhythm is the single strongest cue that it is a curb and not paint. Segment
  it and give it the R=10 top arris the repo's own §304 note calls for.
- **B-3 no L-type gutter**: `infra_kit.py:409-410` states the real Korean section plainly `[cite]`:
  *"asphalt → L-type gutter → curb (trapezoidal) → sidewalk block … while our scenes go 'asphalt → curb box →
  sidewalk' with no gutter."* `build_gutter_L` exists (`infra_kit.py:399-523`) and is **switched off in every
  scene that could use it** — `gutter_L=0` in 02, 03, 08, 16, 17 `[measured]`; 06 and 11 never request it.

**Finding 2 — the pan-scene audit is where the real defect is.** `[measured]`

| Scene | Road-adjacent surface | Carriageway top | Walk top | Curb | Verdict |
|---|---|---|---|---|---|
| 02 underpass | `road` x 8..13 | −0.020 | 0.000 | `curb_top +0.10`, base −0.50 (`scene02:222`), built `scene02:869-876` | **WRONG SHAPE** — exposure above road = 120 mm ✔, but the curb top is **100 mm above the footway**. Real curbs are flush with the footway; the step belongs on the carriageway side only. The scene's own docstring says it out loud: *"Kerb top face +0.10 (10 cm above the sidewalk at 0.0)"* `scene02:860-861`. As built it is a 100 mm trip line running the length of the walk. |
| **06** overpass | `road` y −8..8 | −0.150 | −0.005 | 150 mm | **OK** (see B-1/B-2/B-3) |
| **11** footbridge | `road` x −10.5..10.5 | −0.150 | −0.005 | 150 mm | **OK** (same three legibility defects) |
| 03 riverbank | `levee_road` x −4..−1 | `proud=0.0015` | — | **none** | 1.5 mm. Levee crown road — arguably kerbless in reality; **verify**, do not auto-fix. |
| 08 sunken plaza | `road_lines` at y ±30 | — | plaza 0.000 | **none** | Lane markings are painted **onto the plaza ground plane with no road slab and no curb**. Either build the road properly or delete the markings. |
| 12 riverside deck | `bikeroad` | `proud=0.002` | — | **none** | 2 mm. A 자전거도로 beside a 산책로 genuinely is near-flush in Korea; **verify**. |
| **13** apartment entry | `drive` x −14..0 | `proud=0.004` | `walk_north/south proud=0.007` | **none** | **FAIL.** A 3 mm step between an apartment driveway and its footway. `infra_kit.py:18` `[cite]` already flags this scene: *"scene13 is missing the ramp-side curbs mandated by the Parking Lot Act"*, and `infra_kit.py:846+` ships `build_ramp_curb` (주차장법 시행규칙 §6①5다, **10–15 cm**) that **no scene calls**. |
| 17 Hangang levee | `crown_walk` | `proud=0.006` | — | **none** | 6 mm. `scene17:1026` builds a `/Curb` but it is a **ramp-edge slope**, not a 보차도 연석. |
| 16 underpass entry | `walk` | — | 0.000 | `M["curb"]` material only, no prim | Colour without geometry. |

**Build spec (S06-B)**

1. **New shared builder** `infra_kit.build_curb_line(kit, path, p0, p1, mtl, height=0.15, width=0.20, unit=1.0,
   arris_r=0.010, gutter=True)` — emits **unit-length** curb blocks along a polyline with a 10 mm top arris and,
   when `gutter=True`, calls the existing `build_gutter_L` on the carriageway side. One builder, so the 보차도
   section becomes identical everywhere.
2. **Height rule**: exposure above carriageway **150 mm default**, 250 mm max, 100 mm min; curb top **flush to
   +20 mm** relative to the footway. Fix `scene02` to this rule (its +100 mm is the only outright shape error).
3. **Material**: new `curb_granite_light` role — do **not** reuse `granite_dark`.
4. **Depressed curb (턱낮춤)**: wherever a crossing, a bollard row or a plaza entry meets the carriageway,
   real Korean practice drops the curb to **≤ 20 mm** over the crossing width. scene06 has a bollard row at
   `y = −9.30` (`scene06:264-265`) with **no** corresponding curb drop. Add `build_curb_line(..., drop_spans=[…])`.
5. **scene13** is the one scene that must gain a curb outright — call the existing `build_ramp_curb`
   (10–15 cm, ≥30 cm off each wall face) and raise `walk_north/south` from `proud=0.007` to a real 150 mm step.
6. Scenes 03 / 12 / 17 stay kerbless **only if** a photo check confirms it (levee crown roads and 자전거도로 in
   Hangang parks often are). **EV-C until checked** — this is the one sub-row of S06-B that is not evidence-closed.

**Affected scenes**: 02 (shape fix), 06 · 11 (legibility), 08 · 13 (build), 03 · 12 · 17 (verify), 16 (material).
**Dependency**: the new builder lands in `infra_kit.py`, which 8 scenes import → single-commit, full re-judge.

---

## 4. scene07 — `/World/Scene07` · temple stone stairs

### S07-A · Wrong archetype — **groundwork only, DO NOT FINALIZE**

**User quote**: "temple stone stairs = wrong archetype (user bringing reference images — do NOT finalize; do the
groundwork)".

**What we build now** `[measured]` (`scene07:165-172`, layout `scene07:477-505`, build `scene07:1111-1127`):

| Parameter | Value |
|---|---|
| count / run / drop | 24 stones · x 0.06 → 12.05 m · 4.20 m (19.0° slope) |
| per stone | tread depth **0.27–0.39 m**, width **0.50–1.10 m**, thickness 0.12–0.26 m (proud 0.02–0.08 + embed 0.10–0.18) |
| **gap between stones** | **0.05 – 0.29 m of bare leaf-covered slope** |
| lateral offset `cy` | ±0.35 m, per stone |
| rotation | yaw ±4.0°, tilt ±2.5° (J5) + one "canted knob" lump per stone at yaw ±10–20°, tilt ±3–9° (J6) |
| edging / cheek stones / handrail | **none** |
| primitive | `sc._oriented_box` — a rectangular slab |

**What it reads as** `[render]` (`pt_noon_stone_rhythm.png`, `pt_noon_grazing_edge.png`): a row of **loose
rectangular pavers dropped on a leaf slope**, each isolated, several visibly cantilevered over open shadow. This
is the **디딤돌 / 박석 (garden stepping-stone)** archetype applied to a 19° gradient. Korean temples do not do that
— a stepping-stone path is a *level* garden device.

**The two real Korean archetypes** `[photo]` (images opened this session; URLs + licences in §8.1):

**Archetype 1 — 장대석 계단 (dressed long-bar granite).** Ref **P07-1** (Buseoksa, CC0) and **P07-2** (Bulguksa
청운교·백운교, CC BY-SA 2.0):
- Each riser is **one long dressed granite bar spanning the full flight width** (2.5–3.5 m), or 2 bars butted.
- **Zero gap** between courses — riser face and tread are the same stone; joints are hairline.
- Tread ≈ 0.35–0.40 m, riser ≈ 0.15–0.18 m; courses perfectly parallel, **no yaw, no tilt**.
- Bounded by **소맷돌** (solid sloping cheek stones both sides) and a wider **지대석** bottom course; on
  monumental flights (P07-2) a central divider bar as well.
- Pale grey weathered granite; the *ends* of the bars are irregular/rough, the *bedding planes* are true.

**Archetype 2 — 자연석 계단 (bedded natural stone).** Ref **P07-3** (팔공산 갓바위, CC BY-SA 4.0):
- Each step is **2–4 irregular split blocks laid side by side across the width**, packed tight against the
  neighbours. Again **no gaps** — earth and leaf litter fill only the joints.
- Blocks are chunky (0.3–0.6 m across, 0.15–0.25 m thick), not thin slabs; they are **bedded**, so no block
  overhangs open air.
- Width narrows and widens with the terrain; the flight still reads as one continuous rising surface.
- Flanked by a **timber post-and-rail handrail** (round posts ≈ 100 mm, two rails) on the exposed side — near
  universal on Korean temple approach stairs.

**Both archetypes contradict our build on the same four points**: (i) no inter-stone gap; (ii) no per-stone yaw or
tilt; (iii) blocks bedded, never floating; (iv) an edge condition exists (cheek stone or handrail).

**Three candidate rebuilds to test against the user's refs when they arrive**

| Cand | Archetype | Geometry | Keeps the negative-obstacle cue? |
|---|---|---|---|
| **C1** | 장대석 | 24 → **26 courses**, riser 0.162 (4.20/26), tread 0.47 to hold the 12.05 m run, each course = 1 bar 3.40 × 0.47 × 0.30 spanning the corridor (y −1.7..1.7), gap 0, yaw/tilt 0. Add 소맷돌: two solid sloping cheek prisms at y ±1.75, top following the 19° line, 0.35 wide × 0.45 tall. Add 지대석: bottom course 0.20 wider and 0.10 lower. | Yes — the drop is now a *clean* 162 mm edge, which is the harder and more realistic hazard. The current 0.05–0.29 m gaps were doing cue work the archetype forbids; they must be replaced by **worn/rounded nosings + moss in the joints**, not by voids. |
| **C2** | 자연석 | Same 26 rises, but each course built from **2–4 blocks across the width** (`build_worn_stone_stairs` already does exactly this — `scene_common.py:1907-1922`, per-block yaw ±3°, z ±0.02, front/back ±0.10 — **and scene07 explicitly refuses to use it**, `scene07:44-46`). Blocks butt with 1 mm overlap; base solid to `base_z` so nothing floats. Add the timber handrail on the downhill side. | Yes — the irregular nosing line is the cue, and it is the *real* cue. |
| **C3** | Hybrid (likeliest match for a 산사 approach) | 장대석 for the lower formal flight (nearest the gate) + 자연석 for the upper natural section, with a landing between. Matches the sequence in P07-1/P07-3 where the formal courtyard stair and the mountain path stair are different. | Yes, and it gives the scene two drop textures in one frame. |

**Also delete with the archetype**: the "canted knob" (`scene07:174-179, 1121-1127`, 24 extra prims). Its stated
purpose is "breaks the rectangular silhouette" — a symptom-treatment for the wrong primitive. Neither real
archetype has anything like it.

**Adjacent, already-known, same scene** `[cite]` `tonglam_v2.md` §1 row 07 (**FAIL**): boulder-scale D-5 rocks in
dark sink-rings (fix F2) and razor-edged leaf-litter rectangles (fix F3). **F2/F3 and S07-A touch the same
frames** — sequence them into one scene07 commit.

**DO NOT FINALIZE.** Hold C1/C2/C3 until the user's reference images land; then pick, measure the refs, and only
then write dimensions into the execution spec.

**Dependency**: user refs (blocking) · P-1 (J5/J6 die with the archetype) · F2/F3 (`tonglam_v2` §3).

---

## 5. scene08 — `/World/Scene08` · sunken plaza

### S08-A · Remove the bollard + line barrier

**User quote**: "plaza bollard+line barrier — user: no real plaza does this; locate the builder call, spec removal".

**Where it is** `[measured]`

| Item | Location |
|---|---|
| params | `scenes/main/scene08_sunken_plaza.py:195-206` — `tempbar=dict(x=-0.72, post_r=0.045, post_h=1.0, nband=5, band_ov=1.02, tape=dict(z_end=0.85, sag=0.11, nseg=8, w=0.09, t=0.004, tie_h=0.05), post_color=(0.60,0.14,0.10), post_color_b=(0.78,0.78,0.75), tape_color=(0.75,0.62,0.10))` |
| builder | `scene08:1199-1243` `def build_tempbar(M)` |
| **call site** | **`scene08:1324`**, inside `if cfg["cue_sign"]:` |
| materials | `scene08:906-915` — `M["tempost"]`, `M["tempost_b"]`, `M["tape"]` |
| hazard/collision boxes | `scene08:396-400` — 2 `TempPost_{i}` entries in the box list |
| self-check | `scene08:553-558` — the v6 C-6 dimension check |
| positions | 2 posts at `x = −0.72`, `y = parapet.gap_y0/gap_y1 = ∓0.90` (`scene08:133`) — i.e. straddling the **1.8 m gap deliberately left in the pit parapet**, on the west (approach) side |
| call guard | `cfg["cue_sign"]` — `build_tempbar(M)` then `build_signs(M)` (`scene08:1323-1325`) |

`[render]` `pt_noon_open_gap.png` and `pt_noon_pit_edge.png` show it unmistakably: two red/white banded posts with
a sagging yellow strap slung across the only gap in an otherwise continuous parapet, in a finished, planted,
paved plaza.

**Why it must go** `[photo]` `[assumed]`: banded post + strap is Korean **temporary works** signalling
(공사·점검 중), not permanent plaza furniture. A finished 선큰광장 protects a pit edge with a **permanent**
guard, and where there is an opening it is a stair head with its own railings. Nothing in the frame says
"maintenance in progress" — no cones, no work zone, no notice — so the barrier reads as a modelling artefact.

> **Reversal notice — flag to the supervisor.** `Docs/reports/tonglam_v2.md` §1 row 08 `[cite]` graded scene08
> **PASS** and specifically praised this element: *"barrier tape + striped bollards (strong Korean cue)"*. That
> verdict is now overturned by the user. Whoever executes S08-A must (a) annotate `tonglam_v2.md` row 08 as
> superseded, and (b) expect scene08's eyes-verdict to need re-establishing, since one of the two things that
> earned it a PASS is being deleted.

**Build spec (S08-A)** — pure deletion, 6 edits, no geometry moves:
1. delete `scene08:1324` (`build_tempbar(M)`);
2. delete `scene08:1199-1243` (the builder);
3. delete `scene08:195-206` (params);
4. delete `scene08:906-915` (3 materials);
5. delete `scene08:396-400` (2 collision boxes) — **this changes the hazard-box list, so the GT/OCCL baseline
   moves; re-stamp it**;
6. delete `scene08:553-558` (the self-check block that prints tempbar dimensions).
`cue_sign` still governs `build_signs(M)` (the 출구 sign), so the toggle keeps a job.

### S08-B · What real sunken plazas put at those positions

The parapet gap at y ∓0.90 exists as the scene's negative-obstacle cue. Removing the barrier leaves **an
unguarded 4.5 m drop with a 1.8 m opening** — which is *more* hazardous and, importantly, still needs to read as
something real. Three options, in order of realism:

| Opt | What | Real basis | Cue effect |
|---|---|---|---|
| **B-1** (recommended) | **Close the gap** — continuous parapet + coping the whole way round — and move the cue to the **stair head**: the pit's own stair opening (`stair` = 26 risers × 0.173, tread 0.30, 4.0 m wide, `scene08:124-127`) already is the negative obstacle. | This is what every finished Korean sunken plaza does: continuous 난간벽 or 안전난간 (≥1.1 m), opening only at the stair. | Strongest — the drop is where a walker actually meets it. |
| **B-2** | Keep the gap, guard it with a **stainless 안전난간** (1.1 m, 2 rails + verticals) matching the pit rails already built at `build_parapet` / `build_stair_rails` (`scene08:1319-1320`). | KDS/건축법 요구 1.1 m guard at any drop ≥ 1.2 m. | Weakest cue, most correct building. |
| **B-3** | Keep the gap **and** make the *guard itself* the defect — one **missing/removed railing panel** with the post stubs left in place (the pattern scene06 already uses: `railing.broken=(180,270)`, "posts remain", `scene06:238-239`). | Genuinely common in Korean public space (damaged railing awaiting repair) — and it is a *permanent-furniture* failure, not a temporary-works prop. | Strong cue, and defensible as real. |

**EV grade B** — B-1/B-2/B-3 are argued from Korean practice and from the repo's own statutory notes, but I did
not close an n≥5 photo set on Korean 선큰광장 edge treatment this session (Commons coverage is thin;
road-view services are banned). **Before execution**: 5+ photos of finished Korean sunken plazas
(청계광장 · 서울광장 sunken level · 광화문광장 · COEX/영동대로 sunken · 시청역/을지로 sunken entries), from
news or municipal press releases. Budget ~30 min.

**Note, separate row**: `scene08:193-194` plants a **5-bollard row at x = −18.0** (`ys` −4.8…+4.8, spacing 2.4 m),
mid-plaza with no carriageway in front of it. Under v5.1 §2 `[cite]` bollards are functional only at
vehicle-entry risk points and must be spaced ~1.5 m with a tactile band in front. Either justify it against the
plaza's west road edge or delete it. Fold into the S08 commit.

**Dependency**: supervisor sign-off on the `tonglam_v2` reversal · B-2/B-3 need the S08-B photo set.

---

## 6. scene09 — `/World/Scene09` · ghat riverfront

### S09-B · What the stairs currently are (baseline record) `[measured]`

From `scene09:141-150` and `compute_steps()` (`scene09:428-450`), recomputed:

| Quantity | Value |
|---|---|
| steps | 36 |
| riser table | `[0.14, 0.16, 0.18, 0.20, 0.18, 0.16]` repeating (mean 0.170, sum 1.02 / 6 steps) |
| tread | 0.34 m (landings 1.20 m at step index 11 and 23) |
| **total run / drop** | **13.96 m / 6.12 m** → mean gradient 0.438 (23.6°) |
| width | y −5.0 … +5.0 = **10.0 m only** (the terrace behind it is 80 m wide in y) |
| landings | step 11 at x 3.74–4.94, top z −2.040 · step 23 at x 8.68–9.88, top z −4.080 |
| waterline | z **−5.240** at x ≈ 11.92 — bottom 6 steps submerged |
| flanks | `land_posts` r 0.24, h 2.10 at y ±5.6 (`scene09:250`); `mooring` list, 6 posts at x −1.2 (`scene09:215-217`) |

**Why the user cannot judge it** `[render]`: all five non-preset cuts look **along or head-on to the flight
axis** (`build_views`, `scene09:856-899`):
`ghat_walk` (−4,0,1.4 → +X), `waterline`, `from_river` (+X side, looking −X), `across_river` (mid-river, −X),
`park_vista` (NW, oblique but framed on the pavilion). **Not one cut crosses the flight axis.** At the distances
used, 140–200 mm risers on a 10 m-wide flight foreshorten into a flat masonry wall — in `pt_noon_across_river.png`
the 36-step ghat reads as **a plain white revetment with faint horizontal courses**. That is the entire complaint.

### S09-A · Three diagnostic cuts (miseen only — no preset changes)

**Lighting constraint, derived, not assumed** `[render]` `[measured]`: `scene09` sets `SUN_AZ_OFFSET = 0.0` with
`hdri_sun_rotz_offset = 233.5` and the scene's own note (`scene09:383-384`) says this azimuth "lights the +X
risers frontally". Confirmed against pixels: in `pt_noon_across_river.png` the camera looks −X (so frame-left is
+Y), and the mooring-post shadows fall **to frame-left**, i.e. toward +Y ⇒ **the sun is on the −Y (south) side**.
Therefore a flank camera must sit at **+X and −Y** to keep both the risers and the flank front-lit.

| Name | eye | tgt | What it proves |
|---|---|---|---|
| **`stair_flank_raking`** | `[15.00, -11.00, -2.20]` | `[5.50, 0.00, -3.60]` | **Primary.** Bearing **130.8°**, pitch **−5.5°**, range **14.60 m**; eye is over water (waterline x ≈ 11.92), 3.04 m above it — a boat/mast height. Gives the whole 36-riser stack in raking profile against the water, **both landings visible as breaks in the rhythm**, and the waterline cutting the flight. This is the cut the user is asking for. |
| **`stair_flank_grazing`** | `[1.20, 4.60, 0.55]` | `[11.00, 4.60, -4.60]` | Eye stands on **step 3** (x 1.02–1.36, top z −0.680), **1.23 m above the tread**, 0.4 m in from the north edge, looking straight down the flight (+X). By construction the risers face **away** from the camera — that is the point: this is the concealment case, the same read the h0.3 grid tests, without touching a preset. Does the nosing line collapse into one plane? |
| **`landing_return`** | `[4.34, -8.20, 0.20]` | `[4.34, 0.60, -2.10]` | Cross-flight close-up on **landing 1** (x 3.74–4.94, top z −2.040): bearing 90° (looking +Y), pitch **−14.7°**, range 9.10 m. Eye is set at z +0.20 (above terrace top 0.0) deliberately, so the **south side slope cannot occlude** — verify against the side-slope profile (`scene09:185`) before committing. Shows the 1.20 m landing tread against the 0.34 m steps, the flank/cheek condition, and the terrace junction. Front-lit from the south. |

All three are `out["<name>"] = dict(eye=[...], tgt=[...])` additions inside `build_views` (`scene09:856-899`),
after the existing `views["park_vista"]` line. **No `sc.grid_views` call changes, no preset heights/distances
touched** — the 13 preset cuts stay byte-identical, so the judgement baseline is unaffected.
Add matching checklist lines to the scene `BANNER` in the house style.

### S09-C · Bonus defect found while reading the cuts `[render]` `[measured]`

`pt_noon_across_river.png` and `pt_noon_from_river.png` show the **mooring posts (계선주) embedded in the middle
of the stair face**, standing out of the revetment at 3–4 different heights partway up the slope
(`land_posts` `scene09:250`, r 0.24 h 2.10 at y ±5.6; `mooring` `scene09:215-217`, 6 posts at x −1.2). Real 계선주 sit on
the **quay top / landing deck**, at the level where a boat is tied — never on a stair slope. Move them to the
terrace edge (z 0.0) or to the lowest landing. Cheap, high-yield; fold into the S09 commit.

**Dependency**: none. S09-A is additive and safe to execute first, before anything else in this document —
it is what lets the user judge the rest.

---

## 7. scene10 — `/World/Scene10` · park deck switchback

### S10-A · Reads as an apartment emergency stair — **groundwork, DO NOT FINALIZE**

**User quote**: "deck reads as apartment emergency stair (user refs coming) — groundwork: survey Korean park deck
switchback forms, diff vs our geometry/materials (galvanized-look? riser proportions?)".

**What we build now** `[measured]` (`scene10:187-201`, materials `scene10:362-379`, `:1004-1007`):

| Parameter | Value | Note |
|---|---|---|
| flights | **n = 4**, 10 steps each | 4 × 10 × 0.165 = **6.60 m total drop** |
| riser / tread | **0.165 / 0.300** | 2R+T = **0.630** |
| flight width | `half_w 0.69` → **1.38 m** | |
| landing | **1.40 (X) × 2.80 (Y)** m, 0.12 thick (`size=1.4`, `y0/y1 = ∓1.40`) | covers both width bands |
| plan footprint | 10 × 0.30 = 3.00 m run × ≈2.8 m across | **4 flights folded into ~3 × 2.8 m** |
| posts | r 0.075 (Ø150 mm), `half_y 1.25` | |
| rail | h 1.05, post r 0.05, bar 0.06, balusters r 0.022 @ 0.30 | |
| deck material | `wood_dark` texture, `wood_color = (0.30, 0.20, 0.12)`, `deck_tint (1.00,0.96,0.90)`, `stringer_tint (0.72,0.70,0.66)` | dark red-brown |

**The diff — five things that make it read as a fire escape** `[render]` (`pt_noon_from_below.png`,
`pt_noon_reversal.png`) `[measured]`:

1. **Vertical stacking — the scissor.** `compute_flights()` / `band()` (`scene10:455-476`) alternate each flight
   between two 1.38 m-wide Y bands (`y_off 0.70`, 20 mm apart) and reverse it in X. So **flight 1 and flight 3 sit
   directly above one another**, and **flight 2 above flight 4** — four flights inside a **3.0 × 2.8 m plan**,
   against a masonry wall. That is the defining silhouette of an 아파트 외부 피난계단 (scissor stair). A park deck
   switchback **travels across the slope**: successive flights step *sideways* as well as down, so daylight and
   planting show through between them and the structure reads as landscape, not as a shaft.
2. **Riser/tread ratio is a building stair, not an outdoor one.** 0.165/0.300 (2R+T = 0.630) is an interior
   ratio. Korean outdoor/trail deck stairs run **riser ≈ 0.15, tread ≈ 0.35–0.40** (2R+T ≈ 0.65–0.70) — noticeably
   shallower and longer-treaded. 조경설계기준 KDS 34 treats 단높이 ≤ 15 cm / 단너비 ≥ 30 cm as the *outdoor*
   comfort case `[law — clause located, exact text not fetched this session, see EV note]`.
3. **Flight width too narrow.** 1.38 m. Korean park deck stairs and 데크로드 are built at **1.5–2.0 m**
   (two-way pedestrian flow is the design case; 개화산 데크로드, 470 m, is a typical 1.8 m section
   `[news]`).
4. **No rest platform.** 4 × 1.65 m of continuous descent with only turn-landings. Real park decks put a wide
   **쉼터/전망 platform** (with a bench) at least once in a 6.6 m drop — that platform is *the* visual signature
   that separates a park deck from an egress stair.
5. **Tone.** `wood_color (0.30, 0.20, 0.12)` on a `wood_dark` texture reads near-black in shadow — see the
   `pt_noon_from_below.png` frame, where the whole structure is a dark lattice. Korean park decks are
   **방부목 (ACQ-treated pine, warm tan weathering to silver-grey)** or **합성목재/WPC (light brown or grey)**.
   The metalwork question the user raises ("galvanized-look?") answers itself here: our stringers/posts are
   *timber-textured*, but real Korean deck stairs of this height are almost always **hot-dip galvanised steel
   stringers + steel posts carrying timber treads** — so the honest fix is to *add* galvanised structure, not
   remove it. That is a strong, checkable hypothesis to put to the user's refs.

**Candidate direction (one, to be tested against the refs — not a decision)**

> **D1 — "slope-traversing deck with a mid rest platform, galvanised frame + timber tread."**
> 2 flights of 14 steps (riser 0.150, tread 0.360, width 1.80 m) + **one 1.8 × 3.0 m rest platform with a bench**
> at mid-height, the second flight **offset 3.0 m along the slope** from the first so the two do not overlap in
> plan. Structure: Ø101.6 galvanised steel posts + C-channel stringers (light grey, metallic 0.4, rough 0.45);
> treads 2× 38 mm 방부목 planks with a 10 mm gap (the existing `flights.gap = 0.02` and plank read were graded
> **excellent** in `tonglam_v2.md` §2.4 `[cite]` — **keep them**); railing 1.1 m, galvanised posts + timber
> top rail. Total drop stays **6.60 m** so the terrain and the GT drop are untouched.

**Explicitly keep** (do not regress): the plank gaps (`flights.gap = 0.02`; 2–3 mm read, `tonglam_v2` §2.4 PASS);
the stone pit / log fence, which the same report calls "excellent"; and **`rail.broken_landing = 0`**
(`scene10:199-201`) — the missing railing bay at landing 0 is this scene's negative-obstacle cue and must survive
any rebuild. **Also in this scene**: `tonglam_v2` §1 row 10 flags D-5 rocks
on the trail legs (F2) and the leaf-patch outline stroke (F3) — same commit.

> **Reversal notice**: `tonglam_v2.md` §1 row 10 `[cite]` reads *"Timber deck switchback + stone pit + log fence
> read excellent"* and graded the scene FLAG-on-minors. The user's read is the opposite on the switchback itself.
> Record the override; the plank/pit/fence praise still stands.

**EV grade B**: the diff above is measured against our code and argued from Korean practice, but I did **not**
close an n≥5 photo set on Korean 목재 데크 계단 this session — Wikimedia coverage of Korean park decks is
essentially empty (`Category:Boardwalks in South Korea` holds **3 files** `[measured]`), and road-view services
are banned. **Before execution**: 8+ photos of 목재 데크 계단 / 데크로드 / 전망데크 from 구청·시청 press
releases, 산림청/국립공원공단 galleries, and news — the user's incoming refs may satisfy this on their own.

**DO NOT FINALIZE.** Hold D1 until the refs land.

**Dependency**: user refs (blocking) · P-1 (J7 leaf-patch rotation) · F2/F3.

---

## 8. Evidence ledger

### 8.1 Photographs opened and looked at this session `[photo]`

| ID | Subject | Commons page | Licence | Date |
|---|---|---|---|---|
| **P07-1** | Buseoksa (부석사) courtyard **장대석 계단** — 5 full-width dressed granite courses, zero gaps | `commons.wikimedia.org/wiki/File:Buseoksa_Temple_01.jpg` | **CC0** (Bernard Gagnon) | 2022-10-09 |
| **P07-2** | Bulguksa 청운교·백운교 — monumental 장대석 flight with 소맷돌 cheek stones + central divider | `commons.wikimedia.org/wiki/File:Blue_and_White_Cloud_Bridges_청운교_백운교_佛國寺_靑雲橋_白雲橋_(5281872665).jpg` | CC BY-SA 2.0 (InSapphoWeTrust) | 2008-11-17 |
| **P07-3** | 팔공산 갓바위 계단 — **자연석 계단**: 2–4 packed blocks per step, timber post-and-rail handrail | `commons.wikimedia.org/wiki/File:팔공산_갓바위_계단.jpg` | CC BY-SA 4.0 (HwangHuang) | 2023-04-25 |
| P09-1 | Ttukseom Hangang Park — Korean pedestrian structure underside, curb + banded bollards in a real street context | `commons.wikimedia.org/wiki/File:20260416_뚝섬_한강_공원_풍경_01.jpg` | **CC0** (Wikihyo) | 2026-04-16 |
| P10-1 | Seonyudo Park — Korean park hard-landscape reference (timber footbridge, granite sett paving, bedded boulders) | `commons.wikimedia.org/wiki/File:Korea_Seonyudo_Summer_20140805_17_(14655658708).jpg` | CC BY-SA 2.0 (Korea.net) | 2014-08-05 |

Additional candidates located but **not opened** (for the executor to top up n): `File:Baegungyo_Bulguksa.JPG`
(CC BY-SA 3.0), `File:Korea-Gyeongju-Bulguksa-09.jpg` (CC BY-SA 2.0), `File:유달산 이등바위로 오르는 돌계단`,
`File:Stairs of Pyeongchon Central Park` (×8), `File:인천시청역 2호선 승강장 출입 계단.jpg`,
`Category:Bulguksa` (subcats *Blue Cloud bridge and White Cloud Bridge*, *Sokgyemun*), `Category:Buseoksa`
(subcat *Anyangnu of Buseoksa*), `Category:Seonyudo Park` (24 files), `Category:Cheonggyecheon in 2024/2025`.

**CC-BY / CC-BY-SA obligation**: P07-2, P07-3, P10-1 are share-alike. They are *reference material* for modelling,
not redistributed assets — but if any derivative sheet is published, the attribution ledger rule in
`w3r_prop_mapping_v1.md` §D6 `[cite]` applies. P07-1 and P09-1 are CC0 and carry no obligation.

### 8.2 Statute / standard `[law]`

| Ref | Text used | Where |
|---|---|---|
| L1 | 「도로의 구조·시설 기준에 관한 규칙」 제16조(보도) — curb separating carriageway from footway: **height ≤ 25 cm**; customary built range **15–25 cm** | S06-B |
| L2 | MOLIT 「보도 설치 및 관리지침」 (codil.or.kr `CIKCLS121103.pdf`) — footway section, curb detail | S06-B |
| L3 | MOLIT directive no. 321, 보도설치 지침 **figure 2.17** — vertical curb **R = 10 mm** (already recorded in-repo at `scene_common.py:304`) | S06-B |
| L4 | 주차장법 시행규칙 §6①5다 — ramp side curbs **10–15 cm**, ≥30 cm off each wall face (already coded, uncalled: `infra_kit.py:122-124, 846+`) | S06-B / scene13 |
| L5 | 「도시숲·생활숲·가로수 조성·관리 기준」 / 산림청 「가로수 조성·관리 추진계획」 — roadside planting for **경관의 조화와 연속성**. **Superseded for citation purposes** by `w3_intake_policy.md` §4.2, which quotes 조례 제7조1호라 *"같은 노선과 도로 양측에는 같은 수종"* directly | P-2 |
| L6 | 조경설계기준 **KDS 34 00 00** (MOLIT 고시 2024-743, 2024-12-16) — outdoor stair 단높이/단너비. **Clause located, verbatim text not fetched this session — fetch before quoting a number in the execution spec.** | S10-A |

### 8.3 In-repo cross-references consumed `[cite]`

`Docs/audit_v4/user_feedback_v5_1.md` §전역 3 (jitter origin), §2 (bollards), §6-9 (v5.2) ·
`Docs/reports/tonglam_v2.md` §1 rows 06/07/08/09/10, §2.4, §2.6, §2.13, §3 (F2/F3), §4 (items 1, 9) ·
`Docs/surveys/w3r_asset_map_v1.md` (licence tiers, banned roots) · `Docs/surveys/w3r_prop_mapping_v1.md` §2.2,
§D6 · `Docs/surveys/w3r_building_ab_v1.md` · `Docs/reports/redteam_w3r.md` §0–1.5 (dual-root licence correction
confirmed; `rivermark_plaza_bldg_*` declined) · `Docs/surveys/era_consistency_survey_v1.md` ·
`Docs/surveys/stair_typology_survey_v2.md` · `scenes/main/scene05_amphitheater.py:30-45, 588-600` (the
`build_arc_steps` wedge lesson, not carried across) · `scenes/main/infra_kit.py:18, 52-55, 409-410`.

---

## 9. Blockers, gaps, sequencing

### 9.1 Hard blockers

1. **S07-A and S10-A cannot be finalised** — the user's reference images are the deciding input, by explicit
   instruction. Candidates C1/C2/C3 and D1 are staged, not chosen.
2. **S08-A reverses a published PASS verdict** (`tonglam_v2` §1 row 08 praised the barrier tape + striped
   bollards as a "strong Korean cue"). Needs the supervisor's explicit override before the deletion lands, and
   `tonglam_v2.md` needs a superseded-note.
3. **S10-A reverses a published "excellent"** on the same scene's switchback (`tonglam_v2` §1 row 10).

### 9.2 Evidence gaps to close before execution (EV-B / EV-C rows)

| Gap | Row | What is needed |
|---|---|---|
| Korean sunken-plaza edge treatment | S08-B | n≥5 photos of finished 선큰광장 pit edges (news / municipal press releases; Commons is thin, road-view banned) |
| Korean park deck stair | S10-A | n≥8 photos of 목재 데크 계단 / 데크로드 / 전망데크 — `Category:Boardwalks in South Korea` holds only **3 files** |
| Kerbless-by-design confirmation | S06-B rows 03 / 12 / 17 | photo check that levee crown roads and Hangang 자전거도로 really are near-flush before we lock them as "correct" |
| ~~Street-tree monoculture~~ | ~~P-2~~ | **CLOSED** by `w3_intake_policy.md` §4.2 — 조례 제7조1호라 quotes the rule verbatim `[law]` |
| KDS 34 stair clause verbatim | S10-A | fetch the actual 단높이/단너비 text before putting a number in the spec |

### 9.3 Environment note

**`pxr` (usd-core) is not installed on this machine** `[measured]` — `import pxr` fails. Every geometric number in
this document is **analytic**, recomputed from the authoring code, not measured off a built stage. The W3-R wave
verified its USD claims with usd-core 26.8 on a machine that has it; the S06-A numbers (99.0 mm landing rim
sawtooth, 17.6 mm tread-corner projection, 153.6/−38.4 mm fascia lip, 348 mm deck interpenetration) should be
re-confirmed against a built stage there before code is cut. They are simple closed-form results and I expect them
to reproduce exactly, but they are not yet `[measured on stage]`.

### 9.4 Suggested execution order

1. **S09-A** (3 additive cuts, zero risk, no baseline movement) — ship first; it is what lets the user judge
   everything else in the next gallery.
2. **S08-A** (pure deletion, pending supervisor override) + the x = −18 bollard row decision.
3. **P-2** (one shared-signature change + per-scene tables; visually large, geometrically inert).
4. **S06-A** — the `scene_common.py` arc/helix convention fix. **Highest blast radius** (06 · 05 · 19 · 13);
   archive judge baselines first, full 33-scene re-judge after.
5. **S06-B** — new `infra_kit.build_curb_line`; 8 scenes import `infra_kit`, so single commit + full re-judge.
6. **P-1** — must land together with `tonglam_v2` **F3** for scenes 03 · 07 · 10 · D3 · C2, or the decal
   rectangles regress.
7. **S07-A / S10-A** — after the user's refs arrive; each bundled with its scene's F2/F3 fixes.

---

## §S — Supervisor addendum (2026-07-31, user feedback round 2)

**S11-H (user, verbatim intent): Korean footbridges are H-plan.** "육교가 너무 양쪽으로
뻗어있어. 한국 육교는 H형이야" — stair towers run PARALLEL to the carriageway on each
sidewalk (often switchback flights hugging the road edge), the deck crosses between them:
an H in plan. Our scene11 (and the scene06 approach layout) extends stairs INLINE with the
deck axis (I-plan), sprawling along the bridge direction — wrong archetype.
→ S4 rows: **S11-H rebuild** (stair towers rotated 90°, parallel-to-road switchback,
footprint per real H-form photos n≥6 — harvest via scripts/harvest_refs.py conventions);
**S06 approach check** against the same principle (spiral tower placement relative to road).
Differentiation stands (user: "양쪽으로 다르게 읽힐 수 있잖아"): 06 = spiral identity,
11 = H-form + grating see-through identity.
