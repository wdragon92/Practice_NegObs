# W3 intake — scenes 01–05 (verification + spec drafting)

> **Wave**: W3 · **Task**: intake (verify + spec, **no code/scene edits, no commits**) · **Date**: 2026-07-30
> **Branch**: `feat/realism-v1` (HEAD `578d406`) · **Renders inspected**: `look_check/scene0{1..5}/260730_w2d_fix/` (17 cuts opened)
> **Standing bar (new, overriding)**: not "plausible" — **each scene must MATCH real Korean samples**
> ("실제 표본 확인해서 똑같게"). A row that cannot name a real sample is not a spec row.
> **Policy reversals already ruled by the supervisor and encoded here**:
> (R1) **placement jitter ABOLISHED** — aligned / orthogonal is the real default;
> (R2) **street trees = ONE species per scene/route**.
>
> **Evidence tags**
> `[law]` statute / national standard text fetched or quoted this session ·
> `[measured]` code read or render pixel-read this session ·
> `[stat]` derived over a measured population in this repo ·
> `[photo]` an enumerated, individually-citable photo set ·
> `[assumed]` stated inference, flagged as such.
>
> **Cross-reference**: `w3r_asset_map_v1.md` · `w3r_prop_mapping_v1.md` · `w3r_building_ab_v1.md` ·
> `redteam_w3r.md` · `tonglam_v2.md` · `era_consistency_survey_v1.md` · `audit_v4/user_feedback_v5_1.md`

---

## 0. Verdict summary

| # | Row | Scenes | Kind | Evidence strength | Blocking? |
|---|---|---|---|---|---|
| **G-1** | Jitter abolition — full inventory of yaw/pos jitter call sites | all 33 | policy → code | `[measured]` complete | **yes** — gates 01-A/01-D/03-A/03-B |
| **G-2** | One species per scene/route (street trees) | 01·03·04·05 + 8 more | policy → code | `[law]` verbatim + `[measured]` | **yes** — gates 03-C |
| **G-3** | PROP-EDGE-DISTANCE rule (derived) | all with furniture | new rule | `[law]` verbatim ×3 | **yes** — gates 03-B |
| **G-4** | Manhole placement rule (retires the near-window pilot) | 19 scenes | new rule | `[law]` + `[stat]` decisive | **yes** — gates 05-B |
| **G-5** | Shrub/bush asset swap — 6 verified assets, `place_shrubs` is dead code | 02·03·04·05·11·12·15 | asset | `[measured]` complete | **yes** — gates 03-D/04-A |
| **G-6** | Gravel deposition scatter (replaces uniform random) | 04·07·10·12·D2 | new rule | `[measured]` + `[assumed]` | no |
| 01-A | Crooked-rectangle floor pattern — source identified | 01 + 18 scenes | fix | `[measured]` decisive | no |
| 01-B | Paving must run fully to the edge; turf gap removed | 01·02·05 | fix | `[law]` + `[assumed]` | no |
| 01-C | Mid-plaza weed cubes — removal / relocation | 01 + 21 scenes | fix | `[measured]` decisive | no |
| 01-D | Bench alignment (jitter removal + anchor rule) | 01·03·04·09·11 + batch1 | fix | `[measured]` + G-1 | no |
| 02-A | Entrance canopy rework — none **or** continuous+enclosed | 02 (·16) | redesign | `[law]` verbatim | no |
| 02-B | Entrance flood sill (침수방지 진입 단차) | 02 (·16) | **new geometry** | `[law]` verbatim ×2 | no |
| 03-A | Rectangular decal masks — F3 follow-through (shape, not outline) | 03·07·10·12·D3·C2 | fix | `[measured]` decisive | no |
| 03-B | Pole/bollard positions vs G-3 | 03·05·02 | fix | G-3 | no |
| 03-C | Unnatural tree planting (species mix + placement) | 03·04·01·05 | fix | G-2 | no |
| 03-D | Shrub/bush replacement — hedge stays boxy, foliage becomes real | 03·04·05·02 | asset | G-5 | no |
| 04-A | Bush placement logic (row generator → massing) | 04·03 | redesign | `[measured]` + `[assumed]` | no |
| 04-B | Gravel scatter naturalism | 04 | fix | G-6 | no |
| 05-A | Paving reconsideration (module scale + radial wrap) | 05 | fix | `[measured]` + `[law]` | no |
| 05-B | Manhole audit result for 05 + global application | 19 scenes | fix | G-4 | no |

**Headline**: three of the six global rows (G-1, G-2, G-4) are *decisively* evidenced — the code
contains explicit, quotable statements of the very design intent the supervisor has now reversed,
so no interpretation is needed. G-5 is a pure inventory finding: **the six verified shrub assets
exist on disk and in the `VEG_SHRUBS` table, and no scene calls `place_shrubs` at all** — every
"bush" in scenes 02/03/04/05 is a procedural blob. The two rows still short of the photo bar
(01-B, G-6) are itemised in §5.

---

## 1. Global rows

### G-1 — Placement jitter: ABOLISHED. Complete inventory.

**Item** — Remove every deliberate yaw/position jitter that exists to "break axis-parallel
placement". Aligned / orthogonal is the real default.

**User quote** — supervisor ruling relayed in this intake: *"placement jitter ABOLISHED
(aligned/orthogonal is the real default — find every jitter source)"*. The lineage being reversed
is `Docs/audit_v4/user_feedback_v5_1.md` §3, verbatim:

> **배치 비정형**: 벤치·조형물은 앵커(나무 그늘·벽·화단) 옆에, 격자 정렬·등간격 금지, yaw ±3~8° 지터.

**Root cause in code (file:line)** — complete inventory, all verified this session `[measured]`:

| # | Source | file:line | Magnitude | Applies to |
|---|---|---|---|---|
| J1 | `build_patch_field` yaw | `ground_kit.py:689` (default `yaw_max=14.0`), `ground_kit.py:733` | ±14° | repair patches — **18 ground profiles** |
| J2 | `build_stain_field` yaw | `ground_kit.py:1027` | ±22° | dirt/water/oil/gum/efflorescence blots |
| J3 | `build_footprints` yaw | `ground_kit.py:1072` | ±12° about the walk tangent | footprints (**keep** — see ruling below) |
| J4 | `batch1_common.jit_yaw` | `scenes/batch1/batch1_common.py:248` | ±3–8° (default `lo=3.0, hi=8.0`) | benches, streetlights, fences — batch1 |
| J5 | `batch1_common.jit_pos` | `scenes/batch1/batch1_common.py:256` | ≤0.20 m isotropic | same |
| J6 | scene01 bench yaw, hard-coded | `scenes/main/scene01_campus_stairs.py:175–177` | −6.0 / +4.0 / −5.0 / +3.5 / −7.0 / +5.0° | 6 benches |
| J7 | scene03 riverside block yaw | `scenes/main/scene03_riverbank.py:232`, `:1076` | ±4° | levee prop blocks |
| J8 | scene04 bench yaw, hard-coded | `scenes/main/scene04_parktrail.py:276–278` (rationale `:267–275`) | 96/94/4.5/93/87° (non-integer by design) | 5 benches |
| J9 | scene04 verge instance jitter | `scenes/main/scene04_parktrail.py:259` (`jit_pos=0.22, jit_scale=0.18, jit_step=0.35, skip=0.12, swap=0.5`) | — | 121 verge blobs |
| J10 | scene17 / scene13 dressing jitter | `scene17_ramp_pair_hangang.py:256`, `scene13_apartment_parking_entry.py:223` | ±3–8° | dressing props |
| J11 | scene09 / scene11 bench jitter | `scene09_ghat_riverfront.py:266,:1422`, `scene11_footbridge_stairs.py:232` | ±3–8° | benches |
| J12 | sceneD1 crate yaw | `scenes/batch1/sceneD1_loading_dock.py:855` | ±9° (`crng.uniform(-9.0, 9.0)`) | stacked crates |
| J13 | sceneD1/D2 hard-coded off-axis props | `sceneD1_loading_dock.py:153` (`yaw=-14.0`), `sceneD2_floor_opening.py:210` (`yaw=-22.0`) | −14° / −22° | 2 props |
| J14 | `build_worn_stone_stairs` block yaw | `scene_common.py:1909` (`jyaw=3.0`), `:1935` | ±3° | worn stone steps |
| J15 | vegetation yaw `uniform(0,360)` | `scene_common.py:2388`, `:2456`, `:2832` | 0–360° | trees / shrubs / debris |

**Build spec**

1. **Abolish** J1, J2, J4, J5, J6, J7, J8, J10, J11, J12, J13. Mechanism: change the *defaults*
   (`yaw_max=0.0` at `ground_kit.py:689`; the literal `22.0` at `:1027` → `0.0`;
   `jit_yaw(lo=0.0, hi=0.0)` and `jit_pos(amp=0.0)` at `batch1_common.py:248/256`), then delete the
   per-scene hard-coded yaw values (J6/J8/J13) and set them to the **structural** angle
   (parallel to the kerb / wall / path tangent the object actually sits against). Do **not**
   delete the arguments — a scene that later proves a real off-axis case keeps the hook.
2. **Keep, with justification** — J3 (footprints follow the gait, not a grid), J14 (worn stone
   blocks are individually laid, and the jitter is ±3° on *hand-set masonry*, which is what real
   worn steps show), J15 (a tree's or a leaf's rotation about its own vertical axis is not
   "placement jitter" — it is the object's own arbitrary orientation, and it is what stops one
   USD reference reading as a stamped clone). J9 keeps `jit_scale` and `skip`, loses `jit_pos` —
   see 04-A.
3. **Replacement rule for what jitter was substituting for.** Jitter was introduced to kill
   "clone rows". The real cure is *structural*: objects align to the thing they belong to
   (kerb line, wall face, planter edge, path tangent) and vary by **size, model and spacing**,
   not by angle. Where a run of identical furniture would read as clones, vary the **interval**
   against a real cause (a tree pit, a manhole, a doorway) — never the angle.

**Real-sample evidence** — the reversal is doctrinal (supervisor), so the evidence needed is
that the *real* default is orthogonal, not that jitter is banned:

- `[law]` 「도시숲·생활숲·가로수 조성·관리 기준」 제2-3조 나(6): *"교목의 종간 식재간격은 4∼8m,
  횡간 식재간격은 보도ㆍ차도 경계선으로부터 최소 1m 이상의 거리를 확보한다"* — street planting is
  specified as a **regular interval measured off a boundary line**, i.e. by construction aligned.
- `[law]` 「교통약자의 이동편의 증진법 시행규칙」 별표2 (보행안전시설물): bollards are specified at
  **"설치간격은 1.5m 안팎"** — again a regular interval off a line, with no angular tolerance.
- `[measured]` The code's own commentary already records that the jitter *causes* the artefact it
  was meant to cure: `ground_kit.py:709–712` says the un-jittered patches read as "a set of
  rectangles laid on the ground"; the fix chosen was rotation, and `tonglam_v2.md` §2.13-2 then
  logged the rotated result as **"leaf/soil decal rectangles with razor edges"** in 03/07/10/D3.
  Rotation moved the artefact, it did not remove it.

**Affected scenes** — all 33 (J1/J2 are in the shared ground profile table). Scenes 01–05 in
scope here; 06–21 + batch1 inherit automatically once the kit defaults change.

**Dependency** — must land **before** 01-A, 01-D, 03-A, 03-B, 04-A. It is a defaults change in
two shared modules, so it must be sequenced ahead of any per-scene edit that would otherwise be
written against the jittered coordinates.

---

### G-2 — Street trees: ONE species per scene/route

**Item** — Assign one street-tree species per scene (or per route inside a scene) and remove the
per-tree independent species draw.

**User quote** — *"street trees = ONE species per scene/route (find the current mixing mechanism
in `build_tree`/VEG weights and spec the per-scene species assignment)"*.

**Root cause in code (file:line)** `[measured]`

```
scene_common.py:2443   pool = [t for t in veg_pool() for _ in range(t[2])]
scene_common.py:2444   rel, native, _ = pool[rnd.randrange(len(pool))]
```

`rnd` is seeded at `scene_common.py:2438–2439` from the **coordinate hash of that one tree**
(`cx*73856093 ^ cy*19349663`). Every tree therefore draws its species **independently** from the
weighted pool `VEG_TREES` (`scene_common.py:2118–2125`):

| species | weight | share |
|---|---|---|
| `Trees/Elm_Sapling.usd` | 4 | 36.4 % |
| `Trees/Shumard_Oak.usd` | 3 | 27.3 % |
| `Trees/Chinese_Juniper.usd` | 2 | 18.2 % |
| `Trees/White_Pine.usd` | 1 | 9.1 % |
| `Trees/Yellow_Pine.usd` | 1 | 9.1 % |

With 5 species and independent draws, the probability that a row of *n* trees is monospecific is
Σwᵢⁿ/11ⁿ — **1.8 % at n = 5** `[stat]`. Confirmed in pixels: `scene03/260730_w2d_fix/pt_noon_preset_h1.8_d5.png`
shows a broadleaf, a columnar conifer, a spruce-form conifer and a poplar-form broadleaf **in one
frame**; `scene04/pt_noon_trail_approach.png` shows juniper + elm + oak + a columnar conifer along
a single trail; `scene01/pt_noon_lower_lookback.png` shows a broadleaf and a cypress-form conifer
flanking the same plaza `[measured]`.

**Real-sample evidence** `[law]` — 「도시숲·생활숲·가로수 조성·관리 기준」 제2-3조 가, verbatim:

> **"도로의 동일 노선과 도로 양측에는 통일성이 갖춰질 수 있도록 동일한 수종을 권장한다. 다만, 도로의
> 방향이 바뀌거나 도로가 신설ㆍ확장되는 경우에는 동일 노선일지라도 다른 수종으로 식재할 수 있다"**

This is the exact rule the supervisor stated, in the governing national standard: same route,
both sides, one species; the only permitted break is a **change of route direction** or a
newly built / widened section. It also gives the change *rule* — a species change must be
**justified by a route event**, not scattered per tree.

`[law]` supporting frequency data already in-repo: Seoul 2019 street-tree census, 306,313 trees,
ginkgo 35.8 % + London plane 20.9 % — i.e. two species carry **57 %** of the city's street trees
(cited at `scene_common.py:2107–2111`). A real Korean street reads as a *repetition of one
species*, not as an arboretum.

**Build spec**

1. Add a per-scene species assignment. Preferred shape: an optional `species=` argument on
   `build_tree` (default `None` = current behaviour, so the 33-scene signature contract of
   `scene_common.py:2431–2434` survives), plus a scene-level constant, e.g.
   `PARAMS["street_tree"] = "Trees/Shumard_Oak.usd"`, threaded through each scene's tree loop.
2. Where a scene has two genuinely different planting contexts (e.g. scene03 levee crest vs
   far bank; scene04 trail vs background woodland), that is a **route change** under the standard
   — allow **one species per route**, not per tree, and record the route boundary in PARAMS.
3. **Per-scene assignment for 01–05** (broadleaf-dominant, matching the Seoul mix; the two pine
   entries stay available only for the background woodland role, per the asset roles in
   `Docs/reports/w2_veg_procurement_v1.md` §2.1):

   | scene | context | species | basis |
   |---|---|---|---|
   | 01 | campus plaza planters | `Shumard_Oak` (mid/far), `Elm_Sapling` for the 3 m near-field planters | oak = pin-oak substitute; the elm is the declared near-field 3 m substitute (`scene_common.py:2120`) |
   | 02 | sidewalk street trees | `Elm_Sapling` | zelkova/fringe-tree substitute; urban footway scale |
   | 03 | levee crest route | `Lombardy_Poplar` (already procured, role tagged *"riverside (03·12·17)"*, `w2_veg_procurement_v1.md` §2.1) | riverside route identity |
   | 03 | far-bank woodland (separate route) | `Yellow_Pine` | background woodland role |
   | 04 | park trail route | `Shumard_Oak` | broadleaf park route |
   | 04 | background woodland (separate route) | `Yellow_Pine` | background role |
   | 05 | plaza ring planters | `Elm_Sapling` | uniform ring; ring planters are one route |

4. Keep the per-tree **form** variation that `build_tree` already does (height ±8 %, yaw 0–360°,
   trunk taper/lean) — that is within-species variation and is what a real row shows.

**Affected scenes** — 01, 02, 03, 04, 05 in scope; also 09, 10, 11, 12, 16, 17, 20, C2 (all call
`build_tree` more than 3×). Global once the argument exists.

**Dependency** — independent of G-1. Gates 03-C. Should land with G-5 (both touch
`scene_common` vegetation).

---

### G-3 — PROP-EDGE-DISTANCE rule (derived, new)

**Item** — A survey-derived rule for how far street furniture sits from a path edge, replacing
ad-hoc per-scene placement.

**User quote** — *"pole/bollard positions vs a researched PROP-EDGE-DISTANCE rule (user wants a
survey-based rule for how far props sit from path edges — derive it with photo measurements)"*.

**Root cause in code (file:line)** — there is no rule; each scene places furniture by a
**camera-occlusion check**, not by a setback. Verbatim from `scenes/main/scene01_campus_stairs.py:169–177`:

> `camera numeric check (grid eye x −2/−5/−10 @ y −2.75, FOV ±30 deg; the pass rule is the same as
> N-4 — zero hits of "near (<1.2 m) and inside the FOV")`

and from `scenes/main/scene03_riverbank.py:189–192`:

> `[v6 ruling (3)] "in the levee_walk near view the two posts take up 1/3 of the frame height" …
> spread them off the sight axis (laterally)`

Both scenes therefore encode a **frame-composition** constraint where a **setback** belongs.

**Real-sample evidence** `[law]` — three national instruments, fetched this session, together
give the rule without needing photo measurement:

1. 「도로의 구조·시설 기준에 관한 규칙」 제16조(보도): the sidewalk is **유효폭 + 노상시설 폭**.
   *"보도의 폭은 가로수, 가로등 등 노상시설의 설치에 필요한 폭과 보도의 유효폭을 더한 값"*, and
   *"보도의 유효폭은 … 최소 2미터 이상"*. → Street furniture does **not** stand in the walking
   width; it stands in a **dedicated furniture strip (노상시설대)** that is added on top of it.
2. 「도시숲·생활숲·가로수 조성·관리 기준」 제2-3조 나(6): *"횡간 식재간격은 **보도ㆍ차도 경계선으로부터
   최소 1m 이상**의 거리를 확보한다"*; where there is no sidewalk, *"갓길 끝으로부터 수평거리
   **2m 이상** 떨어지도록 식재"*. Tree grate/cover: *"최소폭 **1.5m**"*, cover set *"지면과 높이 차이를
   5cm 이상 이격"*.
3. 「교통약자의 이동편의 증진법 시행규칙」 별표2 (보행안전시설물): bollards **h 0.8–1.0 m ·
   Ø 0.1–0.2 m · 간격 1.5 m 안팎 · 밝은 색 반사도료 · 충격흡수 재질**, and *"볼라드의 0.3m 전면에는
   … 점형블록"*.

**Build spec — the PROP-EDGE-DISTANCE rule (project constant `PROP_EDGE`)**

| class | position | distance from the **path edge line** | basis |
|---|---|---|---|
| Street tree (교목) | in the furniture strip, centred on a Ø1.5 m grate | **≥ 1.00 m** from the paving/carriageway boundary line to the trunk axis; where no kerb exists, **≥ 2.00 m** from the shoulder end | `[law]` 2 |
| Bollard | **on** the boundary line it defends (kerb line / plaza entry line), interval **1.5 m**, only at a vehicle-intrusion point | offset **0.00 m** — a bollard that stands back from the line it guards guards nothing | `[law]` 3 + `[law]` 1 |
| Streetlight / sign post / pole | in the furniture strip | **0.35–0.60 m** from the boundary line to the pole axis (nominal 0.45 m) — derived as ½ the 0.60–1.20 m furniture-strip width used when the strip carries poles but no trees, so the pole sits on the strip centreline | `[assumed]` from `[law]` 1 |
| Bench | **outside** the 유효폭, back to an anchor (wall, planter, hedge), seat face toward the route | ≥ 0.50 m clear behind, and the bench footprint entirely outside the effective walking width | `[law]` 1 |
| Litter bin / bike rack | furniture strip, adjacent to a bench or an entrance | as poles | `[assumed]` |

**Two absolute clauses**, both from `[law]` 1: (a) **no prop may reduce the effective walking
width below 2.0 m** (1.5 m absolute minimum for a wheelchair pass); (b) props of different
classes **share one strip** — they do not scatter across the surface. Consequence for this
project: a prop's coordinate is derived from *the boundary line it belongs to*, and the camera
check becomes a **verification** step, never the generator.

**Affected scenes** — every scene with furniture. In scope: 01 (benches, bins, bike racks,
boards, streetlights), 02 (bollards, benches, bins, streetlights, sign), 03 (bollards, benches),
04 (benches, bins, signpost, board), 05 (bollards, planters, streetlights).

**Dependency** — needs G-1 landed first (the setback is measured to a prop's *axis*, which is
ambiguous while the prop is rotated). Gates 03-B.

---

### G-4 — Manhole placement: retire the near-window pilot, adopt the utility rule

**Item** — Audit every scene's manhole position against real placement logic; adopt a global rule;
this retires the near-window-manhole device.

**User quote** — *"manholes keep appearing in odd spots across scenes"*; *"audit every scene's
manhole position vs real placement logic (utility alignment, not 'near-window filler'); spec the
global rule; note this may retire the near-window-manhole pilot device"*.

**Root cause in code (file:line)** — the code states the defect in its own words. Verbatim,
`scenes/main/scene08_sunken_plaza.py:148–156`:

> `Near-window budget - one area element per preset cut, and the manhole is deliberately NOT in W1:`
> `d2 W1 x -1.436..0 -> patch #0 at x -1.25` … `manhole x -2.40 -> d5 W2 (X=2.60) = 414 px = 21.6 % frame width.`
> `In W1 the phi 0.648 cover is >=28.1 % at any distance, which is the near-window monopoly the`
> `scene15 pilot had to undo. W2 is the only placement that satisfies both "1 manhole" and "<=25 %".`

and `scenes/main/scene05_amphitheater.py:111–114`:

> `manhole (-3.90, -0.40) -> X = 2.60 m at d5, screen width 414 px = 21.6 % of frame. Same`
> `construction as the scene15 pilot fix (M9-b): inside the W1 window a 0.648 m cover cannot stay`
> `under 25 % (28.1 % even at the far end), so it goes to the 2nd-priority W2 window.`

The manhole coordinate is therefore **solved from the camera**, not from a drainage network.

**Measured consequence** `[stat]` — extracted from `ground_kit.py` `SCENE_PLANS` (the fixture that
mirrors the shipped scene coordinates), this session:

- **26 manhole sites across 19 scenes.**
- **19 / 26 = 73 %** sit at **x ∈ [−4.5, −1.0]** — precisely the d2/d5 near-window band.
- **11 / 26** sit at **exactly x = −2.40 or x ∈ [−4.00, −3.80]** — six different scenes converge on
  x = −2.40 alone (08, 15, N1, and the scene PARAMS of C1, C4, N2).
- **Every** site has **|y| ≤ 2.4**, i.e. inside the camera corridor; **x is negative in 26/26**,
  i.e. always on the approach side.
- Range of x is −10.00 … −1.00; nothing anywhere else on any plaza.

A drainage network laid under a 16 m × 16 m plaza does not put every access chamber inside one
3.5 m band on one axis.

**Real-sample evidence** `[law]` — 「하수도설계기준 KDS 61 00 00 / KDS 61 40 00 (관로시설 · 맨홀)」.
Manholes are required **where the sewer line does something**, and otherwise at a fixed maximum
interval on a straight run:

| trigger | rule |
|---|---|
| 관거 **방향** 변화 지점 | manhole required |
| 관거 **경사** 변화 지점 | manhole required |
| **관경** 변화 지점 | manhole required |
| 관거 **합류** 지점 (junction) | manhole required |
| 직선부 최대 간격 | Ø ≤ 600 mm → **75 m** · 600 < Ø ≤ 1,000 → **100 m** · 1,000 < Ø ≤ 1,500 → **150 m** · Ø ≥ 1,650 → **200 m** |

Supporting `[law]`: KS D 4040 cover dimensions are already correctly implemented
(`infra_kit.py:115–120`: Ø648 carriageway / Ø766 / Ø918, thickness 110 t, flush ±10 mm).
The dimensions are right; the **positions** are not.

**Build spec — the global manhole rule**

1. **Delete the near-window budget as a placement generator.** The near-window occupancy check
   stays as a **render-composition assertion** (it protects the h0.3 judgement cuts), but it may
   only *reject* a position, never *produce* one.
2. **Each scene declares a service line, not a manhole coordinate.** New PARAMS shape:
   `PARAMS["utility"] = dict(line=[(x0,y0),(x1,y1),…], d_mm=450, kind="storm")`. The line is
   drawn where a real one would run: **along the plaza's long axis toward the low point / the
   building's service side / under the footway, parallel to the kerb** — never diagonally across
   an open plaza.
3. **Manholes are then derived**, not authored: one at each vertex of the polyline (direction
   change), one at each junction, and otherwise at the KDS interval for the declared diameter.
   Because a 16 m plaza is far shorter than the 75 m minimum interval, a small plaza correctly
   yields **1 or 0** manholes — several scenes should lose one.
4. **Alignment**: covers sit **on the line**, and the line runs **parallel to the paving joint
   grid** (which is itself parallel to the kerb). This also makes the cover's own orientation
   determinate — see G-1.
5. **Gully relationship**: gullies (빗물받이) collect, manholes access. A gully at the low point
   must connect to the line; a manhole with no line and no gully is scenery and should be deleted.
6. **Also retire** the *"near-window filler"* rationale wherever it selected a patch or crack
   coordinate (`scene05_amphitheater.py:116–119`, `scene08_sunken_plaza.py:166`) — same defect
   class, smaller prop.

**Affected scenes** — 19 with manholes: 01, 02, 05, 08, 13, 14, 15, 16, 17, 18, 20, 21, C1, C2,
C4, N1, N2, N3, N5. Scenes 03, 04, 07 correctly have zero (natural profiles) and must stay at zero.

**Dependency** — must land before 05-B. Interacts with `tonglam_v2.md` FIX-5 (manhole silhouette
segments ≥ 24 + dark-iron albedo), which is a *material/mesh* fix on the same prop and can be
done in the same pass.

---

### G-5 — Shrub / bush: the 6 verified assets, and the dead code path

**Item** — Verify the 6 shrub assets cover the hedge and bush roles; spec the scene-side swap.

**User quote** — *"SHRUB/BUSH replacement — verify the 6 verified shrub assets
(Privet/Boxwood/Juniper/Holly/Yew/Cedar) cover the hedge/bush roles and spec the scene-side swap
(hedges stay boxy per pruning rule — but material/foliage must be real)"*.

**Verification result** `[measured]` — all six exist on disk at `assets/vegetation/Shrub/`
(`Privet.usd`, `Boxwood.usd`, `Juniper.usd`, `Holly.usd`, `Yew.usd`, `Cedar_Shrub.usd`), plus
`Rhododendron`, `Burning_Bush`, `Forsythia`, `Grass_Short_A/B/C`, `Switchgrass`.
Measured geometry (`Docs/reports/w2_veg_procurement_v1.md` §2.2 / `props_audit_w1/A_trees_shrubs.md` §6-b):

| asset | native W × **H** (m) | z_min | tri | leaf hue | role fit |
|---|---|---|---|---|---|
| `Privet.usd` | 1.704 · **1.114** | −0.067 | 147 k | green 100 % | **hedge, 1st choice** (쥐똥나무 = the standard Korean hedge species) |
| `Boxwood.usd` | 1.009 · **0.741** | −0.019 | 178 k | green 100 % | **hedge, low** (회양목) — shares `hollyprivet_basecolor.png` with Privet |
| `Holly.usd` | 2.316 · **1.526** | −0.084 | 361 k | green 100 % | **hedge, tall / planter mass** — same texture again |
| `Yew.usd` | 1.227 · **0.728** | −0.013 | 144 k | green 100 % | **formal planter, kerb height** (주목) |
| `Cedar_Shrub.usd` | 0.287 · **0.876** | ≈0 | 186 k | green 97 % | **narrow planter / boundary** (측백류) |
| `Juniper.usd` | 0.455 · **0.898** | −0.013 | 200 k | green 80 % + yellow-green 20 % | **flower-bed shrub** (향나무) |

**Coverage verdict: yes.** Hedge role → Privet (h 1.11) / Boxwood (h 0.74) / Holly (h 1.53) gives
a 0.7–1.5 m clipped-hedge ladder; bush/planter role → Yew / Cedar_Shrub / Juniper. All six are
**evergreen**, so the season-neutrality rule cannot be re-violated by a later re-render
(`w2_veg_procurement_v1.md` §2.2). Caveat `[measured]`: **Privet, Boxwood and Holly share one leaf
texture** (`hollyprivet_basecolor.png`) — they are distinguishable by silhouette and scale only,
so do not use two of them side by side expecting a species contrast.

**Root cause in code (file:line)** — the swap has never been wired.

```
scene_common.py:2796   def place_shrubs(stage, prefix, pts, target_h, pool=None, seed=1234, ...)
scene_common.py:2559   place_shrubs(...)        # <- the ONLY call site in the repo
```

`scene_common.py:2559` sits inside `build_planter`, so real shrub USDs are placed **only inside
planter boxes**. `grep -rn place_shrubs scenes/` returns **zero hits** `[measured]`. Everything
else is procedural:

| scene | "bush" implementation | file:line |
|---|---|---|
| 02 | `build_hedge` (box + crown ellipsoid blobs) | `scene02_underpass.py:898` |
| 03 | 3 overlapping flattened **ellipsoids** per clump, grass texture, ±5 % tint | `scene03_riverbank.py:209–215`, `:1123–1136` |
| 04 | 5 **rows** of `add_sphere` ellipsoids ("verge"), constant tuft/shrub colours | `scene04_parktrail.py:259–265`, `:418–447` |
| 04 | 5 benches, hard-coded off-axis yaw | `scene04_parktrail.py:276–278` |
| 04 | `build_hedge` background band | `scene04_parktrail.py:699` |
| 05 | `build_hedge` × 5 perimeter pieces | `scene05_amphitheater.py:1339–1341` |

`VEG_SHRUBS` (`scene_common.py:2268–2276`) currently lists **Privet, Boxwood, Juniper,
Rhododendron, Burning_Bush, Forsythia** — i.e. it still carries the two assets audit A P0-2
**removed** (`Forsythia` blossom-only, `Burning_Bush` 30.2 % red autumn) and **omits Holly, Yew,
Cedar_Shrub entirely**. `SHRUB_HEDGE = [Privet, Boxwood]` and `SHRUB_ORNAMENT = [Rhododendron,
Juniper]` (`:2279`, `:2288`).

**Real-sample evidence** — `[law]`/`[measured]` the pruning premise the supervisor set is already
recorded in the code and is correct: `scene_common.py:2277–2278` — *"A clipped hedge really is
box-shaped (it is trimmed). What the blob gets wrong is the untrimmed shrubs of a flower bed."*
The Korean maintenance basis is 「도시숲·생활숲·가로수 조성·관리 기준」's pruning provision, which
directs *"노선별, 구간별로 수관의 모양과 높이를 일정하게 유도"* — uniform crown shape and height per
section, i.e. clipping to a form is the specified practice `[law]`.

**Build spec**

1. **Fix the table first.** `VEG_SHRUBS` → drop `Forsythia` and `Burning_Bush` (already
   adjudicated); add `Holly (1.526)`, `Yew (0.728)`, `Cedar_Shrub (0.876)` with their measured
   `native_h` and `z_min`. Roles: `SHRUB_HEDGE = [Privet, Boxwood, Holly]`,
   `SHRUB_ORNAMENT = [Yew, Cedar_Shrub, Juniper]`, `Rhododendron` retained **only** with
   `/Asset/Flowers` deactivated (existing `SEASONAL_SUBPRIMS` path).
2. **Hedges keep their box, lose their skin.** `build_hedge` keeps the clipped-box silhouette
   (correct per the pruning rule) but the surface becomes **real foliage**: replace the grass-texture
   PBR box + crown blobs with a **row of overlapping `place_shrubs` instances of one hedge species**
   clipped to the box envelope, or — if the triangle budget forbids it (Privet is 147 k tri each) —
   keep the box as the *body* and place real shrubs **only along the visible face and top edge**,
   the body acting as an occluder. Decide by budget, not by look, and record the decision.
3. **Free-standing bushes become real assets.** scenes 03 / 04 / 05 clumps → `place_shrubs` with
   `pool=SHRUB_ORNAMENT`, one species per clump group (same logic as G-2 — a real planting bed is
   massed by species), `target_h` from the existing clump height so the composition is unchanged.
4. **One species per bed, and the species is stated in PARAMS** — do not let `place_shrubs`
   draw per instance (`scene_common.py:2819` currently does `avail[rnd.randrange(len(avail))]`
   per point, which is the same defect as G-2 at shrub scale).
5. **Groundcover.** `Grass_Short_A/B/C` and `Switchgrass` are procured and unused; they are the
   correct replacement for scene04's tuft rows and for the `_build_weed_band` cubes (see 01-C).

**Affected scenes** — 02, 03, 04, 05 in scope; also 11, 12, 15 (`tonglam_v2.md` §4-4 lists
"shrub sphere clusters (02/03/05/11/12/15)" as a W3 asset item), plus 06/09/10/17/C2/N2/N4/D3
for the "hedge-ball/dome rows" midground item.

**Dependency** — triangle budget must be checked against `w2_veg_procurement_v1.md` §7.1 before
step 2 (a 60 m hedge of Privet at 147 k tri is not affordable). Gates 03-D and 04-A.

---

### G-6 — Gravel scatter: deposition pattern, not uniform random

**Item** — Replace the uniform-random scatter field with a deposition-pattern scatter.

**User quote** — *"real gravel accumulates (edges, low points, wheel/foot tracks), not uniform
random; spec a deposition-pattern scatter (with photo evidence)"*.

**Root cause in code (file:line)** `[measured]`

```
scene_common.py:2357-2359   for i in range(n):
                                px = xa + rng.random() * w
                                py = ya + rng.random() * h
```

Pure uniform sampling over the **axis-aligned bounding rectangle**. The only non-uniform option is
`edge_bias` (`scene_common.py:2360–2364`), a coarse rejection test that skips the interior with
65 % probability — and **the field call does not pass it**:

```
ground_kit.py:2459-2462   n = scatter(stage, f"{prefix}/Scatter_Field", x0, y0, x1, y1,
                                      plan["ctx"]["z"], cover=float(sp.get("cover", 0.15)),
                                      seed=det_seed("gkit.scatter.field", prefix),
                                      max_count=int(sp.get("count", 0)), **pool_kw)
```

`edge_bias` appears only on the `Scatter_Edge_*` calls (`ground_kit.py:2454`). So the **entire
gravel field is uniform random over a rectangle**. Two visible consequences in
`scene04/260730_w2d_fix/pt_noon_trail_approach.png` `[measured]`: gravel lies on the **lawn** as
densely as on the trail (the region rectangle spans both — `scene04_parktrail.py:124`,
`gkit=dict(x0=-12.0, y0=-3.0, y1=1.0, …)`), and the density is flat everywhere with no relation to
the path centreline, the edges, or any low point. `tonglam_v2.md` scored scene04 **FAIL** on
exactly this: *"dozens of near-white φ0.2–0.4 m boulders strew the grass/trail — reads as a rubble
yard, not a gravel path"*.

**Real-sample evidence** — the physical mechanism is uncontroversial but this row is the weakest
in photo terms; see §5. The mechanism: on a 마사토 (decomposed-granite) trail the **fines are
transported and the coarse fraction is left behind (armouring)**, so exposed aggregate concentrates
(a) in the **runoff line** — the trail centre or the downslope shoulder, (b) at the **toe** of any
cross-slope, (c) in **ruts and foot tracks** where the surface is compacted and washed, (d) at the
**edge** where sheet flow leaves the compacted bed and drops its load, and it is **absent** from
the vegetated surface, because turf traps and buries it. This is the standard 노면 세굴 / 유실
description in Korean trail-maintenance practice (산림청 등산로 정비, 사방기술교본) `[law-adjacent]`.

**Build spec**

1. **Mask the scatter to the surface it belongs to.** Add a `mask_fn(x,y) -> bool` (or a polygon)
   to `scatter_debris` and pass the *trail polygon*, not the plan rectangle. Zero gravel on turf.
   This alone removes the worst half of the artefact.
2. **Density field instead of a constant.** Replace `cover` with a callable
   `cover_fn(x, y) -> float` and give the profile a **deposition template** built from three
   additive terms, each with a stated cause:
   - **edge term**: `+w_e · exp(−d_edge / λ_e)`, λ_e ≈ 0.25 m — the sheet-flow drop line.
   - **track term**: `+w_t · exp(−d_track² / 2σ_t²)` on the wear-lane centreline that
     `build_wear_lane` already computes (`ground_kit.py:1081`), σ_t ≈ 0.35 m — armouring in
     the walked line.
   - **low-point term**: `+w_l` where the local `z_fn` gradient reverses (already available —
     `plan_ground` accepts `z_fn`).
   Normalise so the **mean** cover equals the profile's declared `cover` (0.10 for `trail_soil`,
   `ground_kit.py:1548`), which keeps the existing instance budget and the `inst_cap` 400 intact.
3. **Size sorting.** Deposition sorts by size: the coarse fraction stays at the top of the wash
   and the fines travel. Bind `scale_jitter` to the density term — large instances only where the
   density term is high, small instances in the tail. Cheap version: two `scatter_debris` calls
   with different `scale_jitter` ranges on different density masks.
4. **Keep** the W2 F2 parameters (`scale_jitter=(0.38, 0.62)`, `burial=0.38`) — `tonglam_v2.md`
   FIX-4 already tuned those and they are not the problem.

**Affected scenes** — 04 (P11 `trail_soil`), 07 (P12 `courtyard_dg`), 10, 12, D2. The mask fix
(step 1) is per-scene; steps 2–4 are one shared change in `scene_common.scatter_debris` +
`ground_kit.apply_ground`.

**Dependency** — independent. Should follow `tonglam_v2` FIX-4 (already scoped) so the two do not
re-tune the same numbers.

---

## 2. Scene 01 — campus stairs / plaza

### 01-A — The crooked-rectangle floor pattern: source identified

**Item** — Identify and remove the source of the tilted grey rectangles lying on the plaza.

**User quote** — *"identify the crooked-rectangle floor pattern source (candidates: patch_field/stain
decals w/ yaw jitter, joint grid) from code+render; spec aligned redesign or removal"*.

**Root cause in code (file:line)** — **candidate confirmed: patch_field + stain_field, not the
joint grid** `[measured]`.

- `ground_kit.py:687–738` `build_patch_field` — emits `kit.B(...)`, i.e. a **solid box**, at
  `yaw = ±14°` (`:733`), 2 per plaza (`plaza_granite` profile, `ground_kit.py:1456`).
  In `scene01/260730_w2d_fix/pt_noon_lower_lookback.png` these are the mid-grey rotated
  rectangles on the plaza field; in `pt_noon_beauty_overview.png` there are four of them at
  four different angles.
- `ground_kit.py:979–1036` `build_stain_field` — same, `yaw = ±22°` (`:1027`) for the
  non-directional kinds (`dirt`, `water`, `oil`, `gum`, `efflorescence`, `drip`).
- The **joint grid is exonerated**: `build_joint_grid` (`ground_kit.py:606–669`) emits
  axis-aligned plates with `jitter` defaulting to `0.0` and no rotation argument. The regular
  grid visible in the renders is correct.

Note that the object is a **box**, so its footprint is a hard-edged rectangle regardless of angle;
rotation only makes the rectangle read as *deliberately placed art*. Both W2-F3 changes
(`ground_kit.py:702–712`) are implicated: killing the cut-line outline was right, adding yaw was
not.

**Real-sample evidence** — `[law]` KCS 34 6-5-1 / KDS 34 60 10 (보도포장) and the paving-joint
practice they specify: a granite flag plaza is set out on an orthogonal module (this project uses
600 × 600 mm, `ground_kit.py:1452`), and **a repair patch is cut along the joint lines** — a saw
cut follows the module, because cutting across flags wastes stone and leaves unsupported slivers.
A real repair in flagstone paving is therefore **an integer number of whole or half flags**, and
its outline is *invisible except as a tonal step*, which is exactly what W2-F3 already established
by removing the drawn outline.

**Build spec**

1. `yaw_max` default → **0.0** (G-1). Patches become axis-aligned.
2. **Snap patches to the paving module.** New behaviour in `build_patch_field` when the profile
   declares a `pave.module`: quantise `w`, `h` to an integer multiple of the module (600 mm for
   P1), and quantise `cx`, `cy` so the patch edges land **on joint lines** (using the plan's
   `unit_cell_origin`, which already exists for the T1 MDL contract, `ground_kit.py:288–289`).
   A patch is then a *replaced flag or pair of flags* — which is what one looks like.
3. **Stains stop being rectangles at all.** A soiling blot has no straight edge. Two options,
   in preference order: (a) replace the box with a **thin disc/ellipse** primitive
   (`infra_kit` already has an analytic disc path used for manhole lids,
   `infra_kit.py:810`) — cheap, correct silhouette, zero new tooling; (b) if the mask must stay
   quadrilateral, drive it from an MDL alpha mask with a feathered irregular boundary (this is the
   W3-sized part of 03-A). **For scene01 specifically, (a) is sufficient** and should be taken.
4. Reduce the plaza patch count from 2 to **1** for a 16 × 16 m campus plaza — two repairs on one
   small plaza reads as damage, not maintenance `[assumed]`.

**Affected scenes** — every scene using a profile with `("patch", n)` or `("stain", …)`:
**18 of 22 profiles**. In scope: 01, 02, 03, 05 (04 is `trail_soil`, stains only).

**Dependency** — G-1 (the yaw default). Step 2 needs the plan's `unit_cell_origin`, which exists.

---

### 01-B — Paving must run fully to the edges

**Item** — Find where the paving stops / mixes with turf, and run it to the edge.

**User quote** — *"paving must run FULLY to edges (find where it stops / mixes with turf)"*.

**Root cause in code (file:line)** `[measured]` — two separate stops, and they are different bugs:

1. **A real turf gap between the plaza and the buildings.**
   `scenes/main/scene01_campus_stairs.py:62` `upper_plaza=dict(x0=-16.0, x1=0.0, y0=-8.0, y1=8.0, …)`
   vs `:210-213` `buildings.R = dict(… y0=9.5 …)` and `buildings.L = dict(… y1=-10.5 …)`.
   → a **1.5 m** and **2.5 m** strip of `GroundGrass` (a 120 × 120 m grass box at z = −0.63,
   `:874`) is exposed between the paving edge and every building face. In
   `pt_noon_beauty_overview.png` this is the saturated green band running along the base of both
   brick walls — the single most artificial element in that frame.
2. **The decoration stops short of the paving.** `:1022-1023`
   `region=(g["x0"], st["y0"], st["x0"], st["y1"])` = **(−12.0, −5.5, 0.0, 5.5)**, while the paving
   is (−16, −8, 0, 8). Joints, patches, cracks, stains and weeds therefore exist only on a
   12 × 11 m sub-rectangle of a 16 × 16 m plaza; outside it the granite is pristine and
   un-jointed. The visible seam is the boundary of the decorated region, not of anything real.

**Real-sample evidence** `[law]` + `[assumed]` — 「도로의 구조·시설 기준에 관한 규칙」 제16조 and
KDS 34 60 10 (보도포장, 횡단경사 2 % 표준, 최대 5 %) both describe a paved surface that terminates
at a **kerb, a building plinth, a planting bed edge or a drainage line** — a paved area does not
fade into turf. The Korean campus/plaza convention is that the paving runs to the **building
plinth** and any planting sits in a **kerbed bed** cut into the paving (this is also why the
project already has `build_planter` with a kerb + cap: `scene_common.py:2526`). A free grass strip
between a plaza and a building face occurs only where there is a *designed* planting bed, and
then it has a kerb.

`[photo]` — **evidence gap**, see §5. This row is currently `[law]` + `[assumed]` only.

**Build spec**

1. Extend `upper_plaza` to meet the building faces: `y1: 8.0 → 9.5`, and the L building side to
   `y0: −8.0 → −10.5`. Where the design wants planting, **cut a kerbed bed into the paving**
   (`build_planter`), do not leave raw turf.
2. Extend the ground_kit region to the **full paved rectangle** so joints, patches and stains run
   to the paving edge: `region=(-16.0, -8.0, 0.0, 8.0)`. Watch the interaction with
   `_trim_region` / `_edge_guard_ticks` (`ground_kit.py:2563`) — the guard will drop the ticks
   near the drop edge as designed; that is correct and should be left alone.
3. Add a **plinth / kerb line** where the paving meets each building — a 150 mm granite kerb or a
   flush plinth course. This is also the correct place for the `grime_band` stain kind, which is
   already implemented (`ground_kit.py:1005-1009`) and currently unused in scene01.
4. Apply the same audit to scene02 (`half_y=4.0`, `scene02_underpass.py:158`, against a paved
   sidewalk that visibly ends in turf at the wall base in `pt_noon_approach.png`) and scene05
   (`plaza=dict(y0=-14.0, y1=14.0)` vs the turf visible above the retaining wall in
   `pt_noon_preset_h1.8_d5.png`).

**Affected scenes** — 01, 02, 05 confirmed by render; audit 08, 14, 16, 20, 21 for the same shape.

**Dependency** — step 2 raises the decorated area by ~1.7×, so the prim budget
(`prim_cap=60`, `ground_kit.py:1440`) must be re-checked; expect to *reduce* per-element counts
rather than raise the cap.

---

### 01-C — Mid-plaza shrub/growth: located

**Item** — Locate and spec removal of the growth the user flagged in the middle of the plaza.

**User quote** — *"the mid-plaza shrub/growth the user flagged — locate and spec removal"*.

**Root cause in code (file:line)** `[measured]` — **found: it is the ground_kit weed band, and it
is emitting green cubes on the plaza field.**

```
ground_kit.py:2781-2804  def _build_weed_band(kit, path, region, z, mtl, n=6, seed=0, h_max=None):
ground_kit.py:2796           cx = x0 + 0.05 + rng.random() * max(1e-6, (x1 - x0) - 0.10)
ground_kit.py:2797           cy = (y0 if i % 2 == 0 else y1) + (0.05 if i % 2 == 0 else -0.05)
ground_kit.py:2800           kit.B(p, (cx, cy, float(z) + hh / 2.0), (0.10, 0.10, hh), mtl)
```

Three compounding faults:

1. **Geometry**: `kit.B` = a 0.10 × 0.10 m **box** with the scene's hedge material bound
   (`scene01_campus_stairs.py:1036`, `weed=M["hedge"]`). It renders as a small green cube — visible
   at plaza mid-field in `pt_noon_beauty_overview.png` and at the right edge of
   `pt_noon_lower_lookback.png`. `tonglam_v2.md` §4-4 logs the same object as *"D3 weed cubes
   (12+ scenes)"* and it is separately flagged in 15, 20, 21, N1, N4, D3.
2. **Placement**: `cy` is pinned to `y0` / `y1` — **the ground_kit region boundary**. For scene01
   that boundary is y = ±5.5 (the stair width), which is an **invisible line in the middle of a
   16 m-wide plaza**. There is nothing there for a weed to grow out of.
3. **Count**: `plaza_granite` prescribes `("weed", 6)` (`ground_kit.py:1457`) — six weed clumps on
   a maintained campus plaza.

**Real-sample evidence** — a weed grows where the surface is **discontinuous and un-trafficked**:
in a joint, at a kerb line, at a wall base, in the gap around a manhole frame or a tree grate.
It does not grow in the field of a jointed granite plaza that people walk on. The builder's own
docstring already states the correct rule and the code then ignores it —
`ground_kit.py:2782`: *"**Boundary weed band** — clump by clump in joint lines and gutter cover
gaps."* `[measured]`

**Build spec**

1. **scene01: set `weed` count to 0** for `plaza_granite`. A maintained campus plaza has no weeds
   in the field. (`ground_kit.py:1457` — or override per scene, which is the safer edit.)
2. **Fix the placement contract for every other user.** Weeds must be seeded on a **real
   discontinuity** — pass the actual line set (joint lines from `build_joint_grid`, the kerb
   polyline, the manhole/gully frame perimeters) instead of the region bounding box. Concretely:
   `_build_weed_band(..., lines=[...])` and sample along the lines.
3. **Replace the cube with the procured asset.** `Shrub/Grass_Short_C.usd` (h 0.125 m, 1,598 tri)
   is already procured for exactly this role — `w2_veg_procurement_v1.md` §2.3 states
   *"edge weed tuft … spec §5.4 15-8 wants h ≤ 0.12 → scale 0.96"*. At 1,598 tri it is affordable
   at 6–8 per scene. The GT-E5 ramp clamp (`ground_kit.py:2050`, `exc="weed"`) stays a
   placement-side job and is unaffected.

**Affected scenes** — 22 scenes carry a `("weed", n)` prescription. In scope: 01 (6), 02 (8),
03 (6 — but scene03 forces `natural=True, infra=None`, so verify), 05 (6). 04 has none.

**Dependency** — step 3 needs G-5's table update (`Grass_Short_C` is not in `VEG_SHRUBS`).

---

### 01-D — Bench alignment

**Item** — Benches align to their anchor; the yaw jitter goes.

**User quote** — *"bench alignment"*; and the reversed v5.1 §3 line *"벤치·조형물은 앵커 … 옆에,
격자 정렬·등간격 금지, yaw ±3~8° 지터"*.

**Root cause in code (file:line)** `[measured]`

```
scene01_campus_stairs.py:156   #   (§3: next to an anchor · no grid or even spacing · yaw +-3~8 deg jitter).
scene01_campus_stairs.py:175-177   benches=[(-11.05, 2.35, 0.0, "y", -6.0), (-13.40, -0.15, 0.0, "x", 4.0),
                                            (-9.35, 4.05, 0.0, "x", -5.0), (-4.65, -4.05, 0.0, "x", 3.5),
                                            (5.00, -5.80, -0.6, "y", -7.0), (10.30, 2.05, -0.6, "x", 5.0)]
scene01_campus_stairs.py:890    # [v5.1] yaw jitter (degrees) - seat and legs all rotate about the …
```

The 5th tuple element is the jitter angle, hard-coded per bench. The comment block at `:158-161`
even computes the *clearance lost to the rotation* (`half_len·sin|yaw|`), which is the tell that
the angle is decorative: it costs clearance and buys nothing.

**Real-sample evidence** `[law]` + `[measured]` — the anchor half of the v5.1 rule survives the
reversal; only the angle dies. A Korean plaza bench sits **parallel to the planter kerb, the wall,
or the walking line** because it is bolted to the paving through a fixed base plate and because it
must not intrude on the effective walking width (「도로의 구조·시설 기준에 관한 규칙」 제16조,
유효폭 ≥ 2.0 m — a rotated bench sweeps a larger footprint and eats that width, which is precisely
what `:158-161` computes). The project's own G-3 rule (§1) supplies the setback.

**Build spec**

1. Delete the 5th tuple element (or set all six to the **structural** angle): benches beside a
   square planter take yaw ∈ {0, 90, 180, 270}; benches along a wall take the wall's angle.
2. Keep the **anchor** placement from v5.1 (all six are already beside planters A–E) and keep the
   **irregular spacing** — irregular spacing has a real cause (planters are irregularly spaced)
   whereas irregular *angle* does not.
3. Apply G-3: verify each bench footprint lies wholly outside the effective walking width and
   ≥ 0.50 m clear of the planter cap face (the current clearances at `:162-167` are 0.175–0.375 m
   *before* the yaw bite — under the new rule they should be re-derived at ≥ 0.50 m).
4. Same edit for scene03 (`scene03_riverbank.py:197-200`, 4 benches with yaw 5.0 / 172.0 / 93.0 /
   187.0) and scene04 (`scene04_parktrail.py:276-278`, 5 benches with yaw 96 / 94 / 4.5 / 93 / 87).

**Affected scenes** — 01, 03, 04 in scope; 09, 11, C1, C2, D4, N1, N3 use the `jit_yaw` path (G-1 J4).

**Dependency** — G-1 and G-3.

---

## 3. Scene 02 — underpass entrance

### 02-A — Entrance canopy: none, or continuous and enclosed

**Item** — Rework the entrance canopy.

**User quote** — *"entrance canopy (비받이) — only-at-entrance is wrong; real underpasses = none OR
continuous+enclosed"*.

**Root cause in code (file:line)** `[measured]`

```
scene02_underpass.py:239-241   # D5 canopy over the stair head (subway-entrance silhouette)
                               canopy=dict(x0=-1.8, x1=0.6, y0=-2.45, y1=2.45, z_roof=2.7,
                                           post_r=0.08, roof_t=0.14, base_z=0.0)
scene02_underpass.py:901-905   sc.build_canopy(stage, f"{ROOT}/EntryCanopy", …)
```

A **2.4 m × 4.9 m flat slab at z = 2.7 on four Ø0.16 m posts**, spanning x = −1.8 … +0.6. The
stair opening starts at x = 0 and the pit runs to x ≈ 8.2. So the canopy covers **0.6 m of the
descent** and 1.8 m of the approach apron, and the remaining ~7.6 m of open pit is uncovered. It
is a free-standing porch that neither keeps rain out of the stair nor encloses the entrance.
Visible in `scene02/260730_w2d_fix/pt_noon_beauty_overview.png`: the white slab floats over the
approach with the pit fully open behind it, and the four posts read as unrelated columns.

**Real-sample evidence** `[law]` — 「지하공공보도시설의 결정·구조 및 설치기준에 관한 규칙」 제8조 ⑦,
verbatim:

> **"출입구에는 빗물 등이 직접 지하공공보도시설 내부에 떨어지지 아니하도록 안전한 구조의 지붕 또는
> 덮개시설을 설치하여야 한다"** (may be waived on 도시계획위원회 approval)

The statute's test is **"rainwater must not fall directly into the interior"** — a roof that stops
0.6 m into a 7.6 m descent fails that test outright. So the statute rules out exactly the form
currently built, and permits the two forms the user named:

- **(a) None** — permitted where the urban-planning committee waives it, which is why very many
  older Korean 지하보도 entrances have no canopy at all; the waterproofing duty then falls entirely
  on 제8조 ⑤ (see 02-B).
- **(b) Continuous and enclosed** — the roof follows the stair down and lands on the parapet walls,
  giving the closed "entrance house" silhouette. `[law/news]` The Seoul 수색역 지하보도 upgrade is a
  documented instance: *"캐노피를 통해 우천 상황을 대비했고, 핸드레일은 어르신이 잡고 천천히 걸을 수
  있도록 했다"* (Seoul mediahub, 서울시 보도자료 archive 2013101) — canopy + handrail + universal
  design + barrier-free guide blocks, i.e. the modern enclosed retrofit type.

Definition note `[law]`: 제2조 defines **출입구** as *"지하도출입시설 중 지상의 도로등에 접하는 부분"*
and 제8조 ① sets the entrance width at **≥ 2 m** per entrance. The current 4.9 m opening is legal.

**Build spec** — pick **one** identity and build it fully; do not keep the porch.

- **Option A (era-consistent, cheapest, recommended for scene02):** delete the canopy entirely.
  Scene02's era assignment (see `era_consistency_survey_v1.md` §2.1) and its retrofit-style pipe
  handrails already read as an older facility; an uncovered 지하보도 entrance with a perimeter guard
  rail is the commonest real form. Removing it also removes four unexplained posts from every cut.
  **This makes 02-B mandatory** — with no roof, the statutory waterproofing duty is entirely on
  the entrance sill.
- **Option B (modern retrofit):** build a continuous enclosure — a roof that starts 1.0 m *outside*
  the opening and runs the full length of the descent to where the head clearance is achieved
  (≈ x = 4.4 m, the statutory landing already computed at `scene02_underpass.py:41-47`), springing
  from the **parapet walls** (not free posts), with side panels down to the parapet top and an
  open end. Materials per `w3r_prop_mapping_v1.md`: powder-coated steel frame + polycarbonate or
  laminated-glass infill. Cost: ~1 roof surface + 2 side surfaces + 1 end frame.

Either way, keep the perimeter guard rail and the 출구 sign, which read correctly.

**Affected scenes** — 02; scene16 (지하보도 입구, which `tonglam_v2.md` scores **PASS** and whose
canopy is explicitly praised) is the **in-library reference** for Option B and must not be
disturbed. Compare the two before choosing, so the library does not end up with two scenes of the
same type and the same canopy.

**Dependency** — Option A forces 02-B. Option B interacts with the *unimplemented* v8 landing
design still sitting in the scene02 header as a **"DESIGN PROPOSAL AND IS NOT YET REFLECTED IN THE
CODE"** block (`scene02_underpass.py:29-33`) — that block must be resolved (implement or delete)
before the canopy is re-geometried, because it moves the pit end from x = 7.0 to x = 8.2.

---

### 02-B — Entrance flood sill (침수방지 진입 단차)

**Item** — Answer the flood-sill question and spec the entrance rework.

**User quote** — *"the FLOOD SILL question (입구 홍수 문턱/살짝 솟은 진입부 — user asked for real-case
check; also check 지하공공보도시설 규칙 + flood-design guidance)"*.

**Answer: yes — the raised entrance is real, it is legally required, and its height is a
1–3 step multiple of 0.18 m.**

**Root cause in code (file:line)** `[measured]` — there is **no sill**. The approach apron is flat
at z = 0 right up to the opening: `scene02_underpass.py:56-58` z-ladder row 0 reads
*"ground sidewalk ≤ 0.00, +0.000, flat (opening front edge = drop 3.200)"*. Surface water on the
sidewalk drains straight into the pit. Confirmed visually in `pt_noon_approach.png` — the block
paving runs level into the opening with no step, no upstand and no channel.

**Real-sample evidence** — two independent national instruments, both fetched this session:

1. `[law]` 「지하공공보도시설의 결정·구조 및 설치기준에 관한 규칙」 **제8조 ⑤**, verbatim:
   > **"지상에 접하는 출입구 끝부분의 바닥은 지표수가 지하공공보도시설 내부로 유입되지 아니하는
   > 구조로 하여야 한다"**

   The floor at the ground-level end of the entrance **must be structured so that surface water
   does not flow into the facility**. This is a mandatory clause with no waiver, unlike 제8조 ⑦.
2. `[law]` 「지하 공간 침수방지를 위한 수방기준」 (행정안전부 고시 제2024-88호) and its 실무 매뉴얼
   (행정안전부):
   - *"출입구 방지턱의 높이는 … 지하공간 출입구의 **침수높이를 감안**하여 설정하여야 한다"*;
   - *"침수높이보다 낮게 설치하는 경우 방지턱을 넘어 지하로 유입되는 물을 방지하기 위하여 **방수판**
     등을 설치하거나 비상시 활용할 **모래주머니**를 준비"*;
   - **the practical dimension**: *"실제 출입구 높이 설정은 … **18cm 높이의 계단 1~3개** 정도를 많이
     이용"* — i.e. the built form is a raised entrance of **0.18 / 0.36 / 0.54 m**, reached by 1–3
     steps up before you start going down. The 0.18 m riser matches 「지하도로시설기준에 관한 규칙」's
     18 cm stair-height limit.
   - The manual's own entrance diagram names three elements: **계단폭 (acting as a levee crest) ·
     난간 · 침수방지턱 높이**.

**Build spec** — add the sill; it is cheap geometry with a strong real-world payoff, and it also
gives the h0.3 grazing cut a genuine near-field silhouette.

1. **Raise the entrance apron by one 0.18 m step.** New geometry: a raised platform
   x = −1.20 … 0.00, y = ±2.10 (0.35 m wider than the 1.75 m opening half-width each side), top
   z = **+0.18**, reached from the sidewalk by a **single 0.18 m riser** across the full apron
   width at x = −1.20. Then the descent begins from +0.18, so the **total drop becomes 3.38 m**.
2. **GT consequence — this is a geometry change and must be re-cached.** The drop edge at x = 0
   now carries 3.38 m instead of 3.20 m, and a **new 0.18 m up-step** appears at x = −1.20 (an
   up-step, not a drop — label accordingly). Coordinate with the same GT-regeneration work the
   unimplemented v8 landing block already requires (`scene02_underpass.py:64-79`), so the cache is
   rebuilt once.
3. **Accessibility**: the manual requires the sill to be negotiable by 노약자·장애인, so a single
   0.18 m step needs a companion — either a 1:12 ramp on one side of the apron, or take the sill as
   **2 × 0.09 m** risers. Recommend the ramp: it is a real Korean detail and it reads immediately.
4. **Add the drainage that makes the sill legible**: a linear grating (트렌치) immediately in front
   of the riser at x = −1.30, connected to the gully already prescribed at
   (`scene02_underpass.py:158`). Without a collector the sill looks arbitrary; with it, the whole
   entrance reads as an engineered thing.
5. **Do not** add a 차수판 (drop-in flood barrier) as visible geometry — it is stored, not
   installed, outside a flood event; its guide channels in the jamb are the only permanent trace
   and are below the resolution that matters here `[assumed]`.

**Affected scenes** — 02; **audit 16** (지하보도 입구) for the same clause — if 16 also lacks a sill,
it is the same statutory gap in the library's currently-best scene.

**Dependency** — GT re-cache (step 2). Mandatory if 02-A takes Option A.

---

## 4. Scene 03 — riverbank / levee

### 03-A — Rectangular mat/decal recurrence: confirmed, and the fix is the mask

**Item** — Confirm that F3 killed the outlines but left rectangular masks, and spec the W3-sized
mask fix.

**User quote** — *"rectangular mat/decal recurrence (F3 killed outlines but masks are still
rectangles — confirm and spec the mask-feather/shape fix W3-sized)"*.

**Confirmation: yes, exactly.** `[measured]`

- What F3 did: `cutline` default → `False` (`ground_kit.py:702-708`) — the four 20 mm perimeter
  strokes are gone. This was correct and is visible: the decals no longer carry a drawn frame.
- What F3 did **not** do: the decal is still `kit.B(...)`, a **box**. `ground_kit.py:735`
  (patch) and `ground_kit.py:1029` (stain) both emit boxes. A box has four straight edges and four
  right-angle corners regardless of rotation, so the mask is a **hard rectangle** at every
  distance.
- In pixels: `scene03/260730_w2d_fix/pt_noon_preset_h1.8_d5.png` — a single large tan rectangle
  sits in the centre of the near field of the levee walk, with dead-straight edges and square
  corners; `pt_noon_levee_walk.png` shows two more at different angles; `pt_noon_meander_air.png`
  shows a scatter of white/tan rectangles **lying on the grass**. `tonglam_v2.md` §2.13-2 logged
  the identical class independently: *"Leaf/soil decal rectangles with razor edges (NEW):
  03/07/10/D3 … 03 adds an edge shadow offset."*

**Real-sample evidence** — a soiling or litter deposit has **no straight edge**; a repair patch
has straight edges but they **follow the paving module or the saw cut** (see 01-A). So the fix
splits by kind, and the split is already encoded in the builder — `ground_kit.py:1022-1026` states
it: *"`grime_band` and `tire` are directional … the soil / water / oil / gum blots have no axis"*.
The code drew the right conclusion and then applied it to the *angle* instead of the *shape*.

**Build spec (W3-sized, in three tiers so it can be cut to budget)**

| tier | change | cost | clears |
|---|---|---|---|
| **T1 — shape swap** | `stain` kinds without a `line` → **elliptical disc prim** instead of a box (the analytic-disc path already exists in `infra_kit.py:810`). `tire` and `grime_band` keep the box (they are genuinely rectangular). | ~1 day, no new tooling | most of the artefact in 03/07/10/12/D3 |
| **T2 — module snap** | `patch` quantised to the paving module and snapped to joint lines (01-A step 2). | ~1 day | the patch half of the artefact |
| **T3 — feathered mask** | An MDL opacity mask with an irregular, feathered boundary bound to the decal prim; the prim geometry stays a quad but the *rendered* mask is soft and irregular. Needs the T1 material layer and a noise-mask MDL. | ~3–4 days | the residual "photograph laid on the ground" read at d2 |

**Recommended**: T1 + T2 now; T3 only if the eyes round still calls it. The three tiers are
independent, so T3 can be deferred without blocking.

Additional item from the same pixels: `tonglam_v2.md` notes scene03 *"adds an edge shadow offset"*
— the decal stands proud enough to cast a visible drop shadow. Check the R3 z-ladder value for
scene03's stain kinds (`ground_kit.py:150-170`, `stain_proud` 0.6 mm + rank 5 × `DECAL_Z_EPS`) at
the actual sun elevation; if the shadow is visible at h1.8/d5 the proud value is too large for a
stain and should be cut to the `GROUND_PROUD_MIN` floor.

**Affected scenes** — 03, 07, 10, 12, D3, C2 (decal masks); 01, 02, 05, 18, 20, N1, N3, N4, N5
(patch masks).

**Dependency** — T2 needs 01-A; T3 needs the T1 material layer.

---

### 03-B — Pole / bollard positions vs the PROP-EDGE-DISTANCE rule

**Item** — Apply G-3 to scene03.

**User quote** — *"pole/bollard positions vs a researched PROP-EDGE-DISTANCE rule"*.

**Root cause in code (file:line)** `[measured]`

```
scene03_riverbank.py:189-193   # [v6 ruling (3)] "in the levee_walk near view the two posts take up
                               #   1/3 of the frame height … spread them off the sight axis (laterally)"
                               bollards=[dict(cx=-1.2, cy=2.2), dict(cx=-1.2, cy=-2.2)]
                               bollard=dict(h=0.90, r=0.075, band_z=0.74, band_h=0.10)
```

The pair sits at **y = ±2.2** while the spur they defend is **y = ±1.2** — i.e. **1.0 m outside**
the edge, and **4.4 m apart**. Under G-3 this is wrong on both counts: a bollard belongs **on**
the line it defends (offset 0.00 m), and the statutory interval is **1.5 m 안팎**, so a 2.4 m-wide
spur needs a **row of 2–3 at 1.5 m**, not two posts standing in the grass 1 m off each side.
Confirmed visually in `pt_noon_preset_h1.8_d5.png`: the two posts stand clear of the paving
entirely, on turf, and read as free-standing monuments.

Dimensionally the bollard is **correct**: h 0.90 m ∈ [0.8, 1.0], Ø 0.15 m ∈ [0.1, 0.2], with a
reflective band at z 0.74–0.84 — all matching 별표2 `[law]`.

**Real-sample evidence** — G-3 §1, all three instruments. Additionally `[law]` 별표2:
*"볼라드의 0.3m 전면에는 시각장애인이 미리 알 수 있도록 점형블록을 설치"* — a dot-block strip 0.3 m
in front. Note the project has 점자블록 **default-OFF** by supervisor ruling
(`user_feedback_v5_1.md` §7: *"규정상 옳아도 현실 빈도 낮음"*), so this clause is **knowingly
declined** and that decision should be restated in the W3 spec rather than silently re-litigated.

**Build spec**

1. Move the pair **onto the spur edge line**: `cy = ±1.2` → i.e. flush with the paving edge, and
   add a third on the centreline, giving a **1.2 m interval** across the 2.4 m spur (inside "1.5 m
   안팎"). If the frame-occupancy problem the v6 ruling was solving recurs, solve it by **moving the
   camera or the spur**, not the bollard — G-3's absolute clause.
2. Re-run the near-window occupancy check as a **verification**, not a generator (G-3).
3. Audit the other two scenes in scope: scene02 `bollards=[(-1.0,-6.0), (-1.0,-4.3), (-1.0,4.3),
   (-1.0,6.0)]` (`scene02_underpass.py:255`) — four posts at 1.7 m / 8.6 m / 1.7 m spacing, which
   is not a row and does not defend a line; and scene05
   `bollards=dict(x=-17.2, spacing=1.5, n=4, base_z=0.0)` (`scene05_amphitheater.py:322`, built at
   `:1344-1349`) — 4 gate posts at the regulation 1.5 m, which **passes** and is the in-library
   reference form.
4. Streetlights (`scene03` has none; `scene01:225` and `scene02:288` do) take the 0.35–0.60 m pole
   setback from G-3.

**Affected scenes** — 03, 02, 05 in scope; 13, 16, 18, 20, N5 also carry bollards.

**Dependency** — G-1 (bollards are rotationally symmetric so jitter does not apply, but the
setback is measured to an axis) and G-3.

---

### 03-C — Unnatural tree planting

**Item** — Fix species mixing and placement.

**User quote** — *"unnatural tree planting (species mixing + placement)"*.

**Root cause in code (file:line)** — species: G-2 (`scene_common.py:2443-2444`). Placement:
`scene03_riverbank.py:181-183`, the far-tree row —

```
far_trees=[dict(cx=38.0 + dxo, cy=cy) for dxo, cy in
           ((0.0, -31.0), (1.8, -22.5), (-1.2, -13.0), (2.4, -3.0),
            (-0.6, 7.5), (1.5, 16.0), (-1.8, 27.5), (0.9, 35.0))]
```

with the comment at `:180`: *"An even 10 m spacing would break global convention 3 (no grids), so
spacing·offset are irregular."* That is the reversed rule, applied to a **street/levee tree row**,
which is precisely the case the standard says must be regular.

**Real-sample evidence** `[law]` — G-2's 제2-3조 가 (one species per route) **and** 제2-3조 나(6)
(*"교목의 종간 식재간격은 4∼8m"*, and ≥ 1 m from the 보도·차도 경계선). A levee-crest tree line in a
Korean 하천 park is planted on a **regular interval off the path edge, in one species** — that is
what the standard prescribes and what makes such a route legible from a distance.

**Build spec**

1. **Species**: `Lombardy_Poplar` for the levee route, `Yellow_Pine` for the far-bank woodland
   (G-2 table). Two routes, two species, no mixing inside either.
2. **Spacing**: replace the irregular offsets with a **regular 6.0 m interval** (mid-range of the
   statutory 4–8 m) along the route; where the row must break (a bench, an access ramp, a light
   column), **omit a tree** rather than shift one — omission is the real mechanism and it reads as
   irregular without being arbitrary.
3. **Offset**: trunk axis **≥ 1.00 m** from the path edge line (G-3). Currently the far-tree row is
   at x ≈ 38 with |dxo| up to 2.4 m of lateral wander — collapse to a single line.
4. **Grate**: where a tree stands in paving, give it the statutory **Ø/□ 1.5 m grate** with the
   cover **≥ 5 cm clear of the ground** (제2-3조 나(5)). Scene03's levee-crest trees stand in turf,
   so no grate is needed there; scene01/02/05 planters do need the dimension checked.

**Affected scenes** — 03, 04, 01, 05 in scope; the far-tree / tree-line generators in 09, 10, 12,
17, C2, D3 use the same "irregular by design" comment and need the same edit.

**Dependency** — G-2.

---

### 03-D — Shrub / bush replacement

**Item** — Swap the ellipsoid clumps for real assets; hedges keep the box.

**User quote** — *"SHRUB/BUSH replacement … hedges stay boxy per pruning rule — but
material/foliage must be real"*.

**Root cause in code (file:line)** `[measured]` — `scene03_riverbank.py:209-215` +
`:1123-1136`: six clumps, each **3 overlapping flattened ellipsoids** (`rx,ry,rz` up to
0.40 · 0.62 · 0.34) with the grass texture at uv 1.2 and ±5 % tint jitter. In
`pt_noon_meander_air.png` these are the dark green domes along the levee slope; `tonglam_v2.md`
scene03 row calls them *"sphere-cluster shrubs in `meander_air` [W3-asset]"*.

**Real-sample evidence** — G-5, plus the two-way split the supervisor stated: **a clipped hedge is
box-shaped because it is clipped** (「도시숲·생활숲·가로수 조성·관리 기준」 pruning: *"수관의 모양과
높이를 일정하게 유도"*), whereas a free-standing bank shrub on a 하천 levee is **not clipped** and
has no box or dome silhouette.

**Build spec**

1. Scene03's six slope clumps are **unclipped bank planting** → replace with `place_shrubs`,
   `pool=SHRUB_ORNAMENT`, **one species for all six** (recommend `Juniper` — Ø0.455 native, the
   listed 향나무 flower-bed shrub, and evergreen so the season lock holds), `target_h` = the
   current clump height so the slope-concealment geometry the v5.1 re-fix computed
   (`:203-208`, `rz·embed ≥ rx·grad(0.457)`, rx capped at 0.40) is preserved.
2. Where a **clipped** hedge is genuinely wanted (scene02's perimeter, scene05's plaza perimeter),
   keep `build_hedge`'s box but re-skin it per G-5 step 2 — the grass texture at uv 1.2 on a
   1.4 m lump is the direct cause of the *"mossy rock"* read the code itself diagnosed
   (`scene04_parktrail.py:226-231`, `scene05_amphitheater.py:361-366`).
3. Triangle budget: 6 clumps × 3 blobs → 6 × 1 Juniper at 200 k tri = 1.2 M tri. Instanced
   (`place_shrubs` sets `SetInstanceable(True)` at `scene_common.py:2840`) this is **one**
   prototype, so the memory cost is 200 k; the draw cost is 6 instances. Affordable.

**Affected scenes** — 03, 04, 05, 02 in scope; 11, 12, 15 per `tonglam_v2.md` §4-4.

**Dependency** — G-5 (table update + one-species-per-bed).

---

## 5. Scene 04 — park trail

### 04-A — Bush placement logic

**Item** — Rework the verge bush placement.

**User quote** — *"bush placement logic"*.

**Root cause in code (file:line)** `[measured]`

```
scene04_parktrail.py:259-265   verge=dict(embed=0.50, jit_pos=0.22, jit_scale=0.18, jit_step=0.35,
                                          skip=0.12, swap=0.5,
                                          rows=((1.42, 0.30, 0.30, 0.17, 0.26, -0.80, 6.40, "tuft"),
                                                (1.92, 0.42, 0.36, 0.24, 0.40, -0.75, 6.35, "tuft"),
                                                (2.45, 0.46, 0.40, 0.26, 0.50, -0.60, 6.25, "tuft"),
                                                (3.05, 0.60, 0.66, 0.32, 1.10, -0.50, 6.20, "shrub"),
                                                (3.85, 0.55, 0.62, 0.30, 1.75, -0.20, 6.00, "shrub")))
scene04_parktrail.py:418-447   def verge_instances(): …  add_sphere(…)
```

The generator is **five constant-`cy` rows** stepping along x — a rank of ellipsoids at five fixed
distances from the stair, on both sides. That is a *striping* generator, and it produces the
strongest artefact in the whole library: `tonglam_v2.md` scores scene04 **FAIL** with *"giant
moss-green ellipsoid blobs, cotton-candy hedge"*, and `pt_noon_step_detail.png` shows the two
banks reading as **mossy boulder fields** flanking the steps. The material was already
de-textured to 3 constant tuft colours (`:318-324`) to kill the "mossy rock" read; the shape
survived.

**Real-sample evidence** — the real Korean 침목계단 among grass has **two** legible planting
patterns, and neither is a row of domes:
- **massed groundcover** (a continuous low turf/grass band, not discrete objects), and
- **clumped shrub massing** (irregular groups of 3–7 of one species, with gaps, following the
  slope contour rather than a fixed offset from the stair).

`[measured]` The project already procured the assets for both:
`Grass_Short_A (1.289 × 0.162 m, 32.5 k tri)` / `B (0.662 × 0.164, 11.1 k)` / `C (0.279 × 0.125,
1.6 k)` are described in `w2_veg_procurement_v1.md` §2.3 as the *"direct replacement for the 121
verge blobs (A §4)"* — this row has already been specified once and never executed.

**Build spec**

1. **Delete the 3 `tuft` rows.** Replace with a **continuous groundcover band** built from
   `Grass_Short_A/B` instances scattered by area (not by row), one species, density falling off
   with distance from the stair. All three are instanced and share one material
   (`w2_veg_procurement_v1.md` §2.3), so 121 blobs → ~150 instances of 2 prototypes is a **net
   triangle win**.
2. **Replace the 2 `shrub` rows with 3–4 clumps.** Each clump: 3–7 instances of **one** species
   (recommend `Cedar_Shrub`, 0.287 m wide × 0.876 m tall, 186 k tri — the narrow boundary form),
   placed to **follow the slope contour**, with real gaps between clumps. Keep the existing
   grounding arithmetic (`rz·embed ≥ rx·grade`, `:250-256`) as the seating rule.
3. **Keep** `jit_scale` (size variation within a species is real) and `skip` (gaps are real).
   **Drop** `jit_pos` and `swap` (G-1 — `swap` exists only because `add_sphere` has no rotation
   argument, which is moot once the object is a USD reference with its own yaw).
4. **Keep the concealment duty**: the verge exists to hide the cut slope
   (`scene04_parktrail.py:19-23`). Re-run `verge_selfcheck()` (`:448`) after the rework — it is
   already written to verify 0 stair intrusion / 0 floating / concealment continuity, and it is
   the right gate for this change.

**Affected scenes** — 04; scene03's slope clumps (03-D) are the same defect at smaller scale.

**Dependency** — G-5 (table update), G-1 (jitter). `verge_selfcheck` must pass.

---

### 04-B — Gravel scatter naturalism

**Item** — Deposition-pattern scatter.

**User quote** — *"gravel scatter naturalism — real gravel accumulates (edges, low points,
wheel/foot tracks), not uniform random"*.

**Root cause in code (file:line)** — G-6, plus the scene-side region:
`scene04_parktrail.py:124` `gkit=dict(x0=-12.0, y0=-3.0, y1=1.0, scatter_x1=-2.40, …)`. The
region is a **4 m × 10 m rectangle spanning trail and lawn**; the profile
(`ground_kit.py:1546-1550`, `trail_soil`) asks for `cover=0.10, count=150`; the field call
(`ground_kit.py:2459`) scatters uniformly over the whole rectangle with **no `edge_bias`**.
Result in `pt_noon_trail_approach.png`: ~20 white cobbles lie on the green lawn in the near field,
at the same density as on the trail, and one sits on top of a decal patch on the grass.

**Build spec** — G-6 steps 1–4, with the scene-specific parameters:

1. **Mask** = the trail polygon. The trail is already a polyline with rot-group segments
   (`scene04_parktrail.py:143` `path=dict(width=1.8, …)`, assembled at `:777` `_seg(f"{ROOT}/PathU", …)`;
   the measured centreline runs y −2.46 @ x=−9.3 → −1.36 @ x=−3.5, `:120-121`), so the polygon is
   derivable; if that is expensive, an interim `|y − y_centre(x)| ≤ half_width` test on the same
   polyline is exact enough.
2. **Density template**: edge term λ_e = 0.25 m on the two trail edges; track term σ_t = 0.35 m on
   the wear-lane centreline already declared at `:125`
   (`wear=((-3.0, 0.0), (-0.6, 0.0)), wear_w=0.90`); low-point term at the stair toe, where the
   trail meets the sleeper steps and runoff concentrates.
3. **Mean cover stays 0.10** and `count` stays 150 / `inst_cap` 400 — this is a *redistribution*,
   not an increase, so the D-5 scatter budget and the `tonglam_v2` FIX-4 tuning survive intact.
4. **Size sorting**: the 0.38–0.62 `scale_jitter` band splits — upper half on the high-density
   terms, lower half elsewhere.

**Affected scenes** — 04 primarily; 07 (`courtyard_dg`), 10, 12, D2 inherit the shared change.

**Dependency** — G-6; sequence after `tonglam_v2` FIX-4.

---

## 6. Scene 05 — amphitheatre

### 05-A — Paving reconsideration

**Item** — Reconsider the paving.

**User quote** — *"paving reconsideration"*.

**Root cause in code (file:line)** `[measured]` — a **module-scale discontinuity** between three
adjacent surfaces in one frame:

- Upper plaza: `plaza_granite` profile, module **600 × 600 mm** (`ground_kit.py:1452`), rendered as
  large flags — correct.
- Bowl floor / stage disc: built by `build_arc_steps` / the stage disc
  (`scene05_amphitheater.py:172` `stage=dict(radius=4.9, top_z=-1.207, height=0.4, …)`) with a
  **fine brick-scale module wrapped radially**. In `pt_noon_rim_view.png` and
  `pt_noon_preset_h1.8_d5.png` the stage reads as thousands of ~100 mm units laid in concentric
  rings — a texture-space artefact, not a paving pattern.
- Tier treads: a third module again.

Second issue, already on the W3 list: the **black wedge gaps** where the arc steps meet the stage
disc (`tonglam_v2.md` §4-7, *"scene05 stage black wedge gaps (already-named W3 item; confirmed
visible in 2 cuts)"*) — clearly visible in both cuts above as hard black triangles.

**Real-sample evidence** `[law]` — KDS 34 60 10 (보도포장) / KCS 34 6-5-1: a paved plaza uses **one
declared module per surface**, and a curved surface is paved either with **radial cut flags of the
same module family** (so the unit size stays constant and only the shape varies) or with a **small
unit paver laid in a fan/ring bond** (so the small unit is the *declared* module for that surface,
and the boundary between the two systems is marked by a **kerb or an edge band**). What does not
happen is a large-flag plaza silently becoming a small-unit surface with no edge treatment.
KDS 34 also sets 광장 기울기 ≤ 3 % and 보도 횡단경사 2 % 표준 (max 5 %) — worth checking the bowl
floor's fall while the surface is being reworked.

**Build spec**

1. **Declare the module per surface and mark the joint between them.** Either
   (a) pave the bowl floor and stage in **radial-cut 600 mm granite** matching the plaza — one
   module family throughout, the cut lines radiating from the bowl centre and a concentric joint
   ring at each tier nosing; or
   (b) pave the bowl in a genuine **small unit (200 × 100 mm interlocking block, fan bond)** and
   separate it from the plaza with a **150 mm granite edge band** at the lip. Option (a) is more
   Korean for a civic amphitheatre; option (b) is cheaper and reads as a park.
2. **Fix the wedge gaps** — this is a real geometry defect, not a look issue: the arc-step end
   segments and the stage disc do not close. Close them with an explicit end-cheek prim, or extend
   the disc radius to overlap.
3. **Recheck the plaza tone.** `scene05_amphitheater.py:918` records that this paving is *"the
   single brightest prop in the library (defect D5)"*; the W2 tone round improved it
   (`tonglam_v2.md` scene05: *"tone win visible (no chalk)"*) but the surface is still a large
   near-white field in `pt_noon_preset_h1.8_d5.png`. Any re-paving must not undo the tone win —
   carry the same albedo target forward.
4. **Rock band on the retaining wall.** The green-grey rounded boulders capping the wall in both
   cuts are `build_hedge` crown blobs (`:1339-1341`) reading as river cobbles. Fix under 03-D /
   G-5 — a plaza perimeter hedge on a retaining wall top should be a **clipped Boxwood/Privet
   hedge in a kerbed planter**, not a dome row.

**Affected scenes** — 05; the module-per-surface audit applies to 08, 14, 20, 21.

**Dependency** — step 2 is independent and should be done regardless. Step 1 is a larger surface
rebuild — sequence after the G-rows.

---

### 05-B — The manhole question, applied

**Item** — Apply G-4 to scene05 and record the audit result.

**User quote** — *"THE MANHOLE QUESTION (manholes keep appearing in odd spots across scenes) —
audit every scene's manhole position vs real placement logic … note this may retire the
near-window-manhole pilot device"*.

**Audit result for scene05** `[measured]` — `scene05_amphitheater.py:142` places **1 manhole at
(−3.90, −0.40)**, and `:111-114` states in full that the coordinate was solved from the d5 frame
occupancy (21.6 % of frame width) by the scene15 M9-b construction. There is **no drainage
rationale in the file at all**. The two gullies at (−10.00, 0.00) and (−6.00, −3.00) (`:143`) are
likewise placed by window, and neither connects to the manhole.

**Global audit result** — §1 G-4: 26 sites / 19 scenes, 73 % inside the near-window band, 11 at
two magic x-values, all |y| ≤ 2.4, all x < 0.

**Real-sample evidence** — G-4 `[law]` (KDS 61 40 00 manhole triggers and intervals; KS D 4040
dimensions already correct).

**Build spec for scene05**

1. **Declare the service line.** The upper plaza falls toward the bowl; a storm line under the
   plaza would run **parallel to the plaza's long axis on the building side**, collecting from the
   gullies and discharging away from the bowl. Author
   `PARAMS["utility"] = dict(line=[(-13.5, -3.0), (-2.0, -3.0)], d_mm=450, kind="storm")` (a
   straight run parallel to the paving grid, offset off the walking axis).
2. **Derive the manhole from it.** The run is 11.5 m — far under the KDS 75 m interval for
   Ø ≤ 600 mm — so the correct count is **1**, placed at the run's **upstream head** or at the
   junction with the gully branch, i.e. around (−10.0, −3.0), **not** at (−3.90, −0.40) on the
   camera axis.
3. **Connect the gullies.** Move (−6.00, −3.00) onto the line; move (−10.00, 0.00) to the line or
   delete it. A gully with no line is scenery.
4. **Re-run the near-window occupancy check as verification.** If the derived position lands in
   W1 and exceeds the 25 % occupancy limit, the correct remedy is to **adjust the camera preset or
   accept the occupancy**, not to move the manhole — record whichever is chosen.
5. **Same treatment for the other 18 scenes**, in the same pass. Expect several to lose a manhole
   entirely (a 12 m plaza does not need one), which is a *gain*: `tonglam_v2.md` FIX-5 names the
   manhole as *"the worst single prop"* in 17 d5 and a minor in 01, 02, 05, 15, N5, N1, 13.

**Affected scenes** — 19 (list in G-4). Scenes 03, 04, 07 must stay at zero.

**Dependency** — G-4. Pairs naturally with `tonglam_v2` FIX-5 (silhouette segments ≥ 24 +
dark-iron albedo), which fixes the same prop's *appearance* while this fixes its *position*.

---

## 7. Evidence ledger — honest status against the n ≥ 5 photo bar

The user bar is **"실제 표본 확인해서 똑같게"** with **n ≥ 5 real photos per claim where feasible**.
This is where each row actually stands. **No photo citation in this document is invented**; rows
without an enumerated photo set are marked as such.

| Row | Statute / standard | Photo set enumerated | Status |
|---|---|---|---|
| G-1 | 3 instruments, verbatim | — | **Standard-backed.** The rule is doctrinal (supervisor ruling); the standards show the real default is a regular interval off a line. Photo set not required. |
| G-2 | 「도시숲…기준」 제2-3조 가, **verbatim** | — | **Decisive without photos.** The standard states the exact rule in one sentence. |
| G-3 | 3 instruments, verbatim (도로구조규칙 §16 · 도시숲기준 §2-3 · 교통약자 별표2) | — | **Standard-backed.** One derived figure (pole 0.35–0.60 m) is `[assumed]` and marked. |
| G-4 | KDS 61 40 00 triggers + interval table | — | **Decisive without photos** — reinforced by a 26-site `[stat]` census of our own code. |
| G-5 | 「도시숲…기준」 pruning clause + in-repo measured asset table | — | **Measured.** Asset geometry is measured, not claimed. |
| G-6 | mechanism only | — | ⚠ **WEAKEST ROW.** Physical mechanism is standard, but no Korean 마사토 trail photo set was obtained. See procurement plan below. |
| 01-A | KCS 34 6-5-1 module + saw-cut practice | — | Standard-backed. |
| 01-B | 도로구조규칙 §16 · KDS 34 60 10 | — | ⚠ **Needs photos.** The "no turf gap at the building face" claim is `[assumed]` from the standards. |
| 01-C | builder's own docstring + `tonglam_v2` | — | Decisive from code. |
| 01-D | 도로구조규칙 §16 유효폭 | — | Standard-backed. |
| 02-A | 지하공공보도시설 규칙 **제8조⑦ verbatim** + 서울시 수색역 보도자료 (1 documented case) | 1 documented case, 0 images enumerated | **Strong on law, thin on samples.** |
| 02-B | 지하공공보도시설 규칙 **제8조⑤ verbatim** + 수방기준 고시 제2024-88호 + 실무매뉴얼 (18 cm × 1–3 단) | — | **Strong.** Two independent instruments give the rule *and* the dimension. |
| 03-A | as 01-A | — | Standard-backed + decisive code evidence. |
| 03-B | 교통약자 별표2 verbatim + G-3 | — | Standard-backed. |
| 03-C | 「도시숲…기준」 제2-3조 가·나(6) verbatim | — | **Decisive.** |
| 03-D | pruning clause + measured assets | — | Measured. |
| 04-A | in-repo procurement doc | — | ⚠ **Needs photos** for the "clumped massing, not rows" claim. |
| 04-B | as G-6 | — | ⚠ as G-6. |
| 05-A | KDS 34 60 10 / KCS 34 6-5-1 | — | Standard-backed. |
| 05-B | KDS 61 40 00 + `[stat]` census | — | **Decisive.** |

**Why the photo sets are thin, measured this session** `[measured]`: Wikimedia Commons has
effectively no Korean street-level coverage of these subjects —
`Category:Pedestrian_underpasses_in_South_Korea` **does not exist**;
`Category:Street_trees_in_South_Korea` **is empty**; a Commons media search for `지하보도` returns
**zero results**; `incategory:"Manhole covers in South Korea"` returns **4 files**. The one
Korean category with real depth is `Category:Hangang Park` (**~60 files**, enumerated this
session), which is directly useful for scene03 and partly for 04.

**Procurement plan for the gap rows** (executable, no new tooling):

1. **G-6 / 04-B (gravel deposition)** — 산림청 「등산로 정비 매뉴얼」 and 「사방기술교본」
   (`forest.gg.go.kr/wp-content/uploads/sites/6/2018/11/20181119_sabaing.pdf`, fetched-URL known)
   both carry 노면 세굴/유실 photo plates. Target: 5 plates showing armouring / rill / edge
   deposition on a 마사토 surface. Also 서울시 「등산로 정비 매뉴얼」
   (`news.seoul.go.kr/env/archives/527421`).
2. **01-B (paving to building face)** — `Category:Hangang Park` (60 files) plus
   `Category:Universities in South Korea` subcategories on Commons; target 5 frames showing a
   paved plaza meeting a building plinth with no turf gap.
3. **02-A/02-B (underpass entrance + sill)** — 행정안전부 「지하공간 침수방지를 위한 수방기준 실무
   매뉴얼」 PDF (`mois.go.kr/cmm/fms/FileDown.do?atchFileId=FILE_00071165hOZn4gq&fileSn=0`, direct
   link known) contains the entrance figure with 침수방지턱 dimensioned; 서울시 mediahub carries
   before/after photos of the 수색역 지하보도. Target 8 entrance photos as the user asked.
4. **04-A (shrub massing)** — 산림청 「가로수 조성관리 매뉴얼」 PDF (19.4 MB,
   `forest.go.kr` 자료실 `nttId=3147093`) has planting-pattern plates.

**Recommendation**: these four fetches are ~1 hour of work and would lift six rows from
"standard-backed" to "standard + photo". They should be done **before** the W3 execution spec is
frozen, but they do **not** block starting on G-1/G-2/G-4/G-5, all four of which are decisive on
the evidence already in hand.

---

## 8. Sequencing and dependencies

```
G-1 jitter abolition  ──┬──> 01-A  ──> 03-A (T2)
   (ground_kit + batch1)│
                        ├──> 01-D
                        ├──> 03-B  <── G-3 prop-edge rule
                        └──> 04-A  <── G-5

G-2 one species/route ─────> 03-C
                              (also 01/04/05 tree assignment)

G-5 shrub assets ──────┬──> 03-D
   (VEG_SHRUBS table)  ├──> 04-A
                       ├──> 05-A step 4
                       └──> 01-C step 3 (Grass_Short_C)

G-4 manhole rule ──────────> 05-B  ── pairs with tonglam FIX-5

G-6 deposition scatter ────> 04-B  ── sequence after tonglam FIX-4

independent: 01-B (region + geometry) · 02-A/02-B (needs the scene02 v8 block resolved first)
             05-A step 2 (wedge gaps — real geometry defect, do anytime)
```

**Hard prerequisite outside these rows**: `scenes/main/scene02_underpass.py:29-33` still carries a
block marked **"DESIGN PROPOSAL AND IS NOT YET REFLECTED IN THE CODE"** (the statutory landing +
mid rail, which moves the pit end 7.0 → 8.2 m). Both 02-A and 02-B change geometry in the same
region and both require a GT re-cache. **Resolve that block (implement or delete) before touching
scene02**, or the GT cache will be rebuilt twice.

---

## 9. Open questions for the supervisor

1. **02-A**: Option A (no canopy, era-consistent, forces the sill) or Option B (continuous enclosed
   retrofit)? Note scene16 already ships the Option-B form and is the library's joint-best scene —
   two scenes of the same type with the same canopy may be redundant.
2. **03-B / 별표2 점형블록**: the bollard clause requires a dot-block strip 0.3 m in front, but
   점자블록 is default-OFF by ruling (`user_feedback_v5_1.md` §7). Confirm the decline stands so it
   is not re-litigated per scene.
3. **G-5 step 2**: real foliage on hedges — full instancing (expensive: Privet 147 k tri each) or
   box-body-plus-visible-face? This is a budget call, not a look call.
4. **05-A**: bowl paving option (a) radial-cut granite or (b) small-unit fan bond with an edge band?
5. **G-1 exceptions**: confirm the three keeps (footprints J3, worn-stone-block J14, vegetation
   self-yaw J15) are acceptable, since they are technically "jitter".
6. **G-4 count reduction**: several scenes will correctly drop to **zero** manholes. Confirm that
   losing the prop is acceptable — it is currently doing double duty as a near-field scale anchor
   (`infra_kit.py:963`: *"stall paint, crosswalk paint, doors and manholes — catches half of all
   scale errors"*). If a scale anchor is still wanted in those frames, it must come from something
   with a real reason to be there.

---

## 10. Sources

**Statutes and national standards** (all fetched or quoted 2026-07-30)

- 「지하공공보도시설의 결정·구조 및 설치기준에 관한 규칙」 제2조 · 제8조 ①④⑤⑦ —
  https://ko.wikisource.org/wiki/지하공공보도시설의_결정·구조_및_설치기준에_관한_규칙 ·
  https://www.law.go.kr/LSW/nwRvsLsInfoR.do?lsiSeq=118414
- 「지하 공간 침수방지를 위한 수방기준」(행정안전부 고시 제2024-88호) —
  https://www.law.go.kr/행정규칙/지하%20공간%20침수방지를%20위한%20수방기준 ·
  https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000016&nttId=114046
- 「지하공간 침수방지를 위한 수방기준 실무매뉴얼」(행정안전부) —
  https://www.mois.go.kr/cmm/fms/FileDown.do?atchFileId=FILE_00071165hOZn4gq&fileSn=0 ·
  https://mois.go.kr/frt/bbs/type001/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000012&nttId=59077
  (출입구 방지턱 = 18 cm 계단 1~3개; 방수판·모래주머니 보완) · 해설 https://hydroft.com/309
- 「도시숲·생활숲·가로수 조성·관리 기준」 제2-3조 가·나(5)(6) —
  https://www.ulex.co.kr/법률/2100000225394-85883-도시숲생활 ·
  「가로수 조성 및 관리규정」 https://www.law.go.kr/LSW/admRulInfoP.do?admRulSeq=2000000017655 ·
  산림청 「가로수 조성관리 매뉴얼」 https://www.forest.go.kr/kfsweb/cop/bbs/selectBoardArticle.do?bbsId=BBSMSTR_1069&nttId=3147093
- 「도로의 구조·시설 기준에 관한 규칙」 제16조(보도) —
  https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=138166 · 해설('21.12)
  https://www.molit.go.kr/USR/I0204/m_45/dtl.jsp?idx=17894
- 「보도 설치 및 관리 지침」(국토교통부예규 제321호, 2021-07-23) —
  https://www.law.go.kr/admRulLsInfoP.do?chrClsCd=010202&admRulSeq=2100000203352 ·
  https://www.codil.or.kr/viewDtlMoctRoadGuide.do?pMetaCode=CIKCLS121045
- 「교통약자의 이동편의 증진법 시행규칙」 별표2 (보행안전시설물 구조·시설 기준) — 볼라드 h 0.8–1.0 m ·
  Ø 0.1–0.2 m · 간격 1.5 m 안팎 · 반사도료 · 충격흡수 재질 · 전면 0.3 m 점형블록 —
  https://www.law.go.kr/법령/교통약자의이동편의증진법시행규칙 · reporting:
  https://www.goodkyung.com/news/articleView.html?idxno=149324 ·
  https://www.ablenews.co.kr/news/articleView.html?idxno=96686
- 「하수도설계기준 KDS 61 00 00 / KDS 61 40 00(관로시설·맨홀)」 — 맨홀 설치 위치(방향·경사·관경 변화,
  합류) 및 직선부 최대간격 75/100/150/200 m —
  https://files-scs.pstatic.net/2024/08/30/FEFOlqHQAr/하수도설계기준(2023).pdf ·
  https://www.codil.or.kr/filebank/moct2014//201901/MOCT1852_2.PDF?nserialno=1852
- 「조경설계기준 KDS 34 00 00 / 보도포장 KDS 34 60 10 / 조경공사 표준시방서 KCS 34 00 00」 —
  https://www.law.go.kr/LSW/admRulLsInfoP.do?admRulSeq=2100000251100

**News / government press**

- 서울시 mediahub, 「청량리 청과물시장 앞·수색역 지하보도, 더 안전해졌다! 그 비결은?」 (수색역 지하보도
  캐노피·핸드레일·CPTED·점자유도블록 리모델링) — https://mediahub.seoul.go.kr/archives/2013101
- 서울시 「등산로 정비 매뉴얼」 — https://news.seoul.go.kr/env/archives/527421
- 「사방기술교본」(경기도 산림환경연구소 배포본) —
  http://forest.gg.go.kr/wp-content/uploads/sites/6/2018/11/20181119_sabaing.pdf

**Photo corpora enumerated this session**

- Wikimedia Commons `Category:Hangang Park` — ~60 files, enumerated
  (https://commons.wikimedia.org/wiki/Category:Hangang_Park)
- Wikimedia Commons `Category:Pedestrian underpasses` — 39 files + 6 subcategories, **no Korean
  entries** (https://commons.wikimedia.org/wiki/Category:Pedestrian_underpasses)
- Negative results, recorded so they are not re-attempted: `Category:Pedestrian underpasses in
  South Korea` does not exist; `Category:Street trees in South Korea` is empty; MediaSearch
  `지하보도` returns zero; `incategory:"Manhole covers in South Korea"` returns 4.

**In-repo (verified this session)**

`ground_kit.py` · `scene_common.py` · `infra_kit.py` · `scenes/main/scene0{1,2,3,4,5,8}*.py` ·
`scenes/batch1/batch1_common.py` · `Docs/reports/tonglam_v2.md` ·
`Docs/reports/w2_veg_procurement_v1.md` · `Docs/surveys/props_audit_w1/A_trees_shrubs.md` ·
`Docs/audit_v4/user_feedback_v5_1.md` · `Docs/surveys/era_consistency_survey_v1.md` ·
`Docs/surveys/w3r_{asset_map,prop_mapping,building_ab}_v1.md` · `Docs/reports/redteam_w3r.md` ·
renders `look_check/scene0{1..5}/260730_w2d_fix/`.
