# W3 intake v2 — user target images + second review → per-scene renovation map

> **Wave**: W3 · **Task**: intake v2 (verify + route, **no code/scene edits**) · **Date**: 2026-07-30
> **Branch**: `feat/realism-v1` (HEAD `cb27bef` at open) · **Written by**: intake-v2 lane
> **Files written by this lane**: this file only.
> **Concurrency notice**: a live workflow is executing the **scene07 / scene10** rebuilds
> (`s3_scene07_10_rebuild_spec_v1.md` §8.R) and is touching `scene_common.py` and
> `Docs/audit_v4/gt_changes_w3.md`. Those two scenes are **recorded here, not routed**, and this
> document **does not amend the GT ledger** — §3(i) declares a ledger amendment that the ledger
> owner (WP T5 / S2) must make **after** the running lane completes.
>
> **Inputs**: the user's second review (§0, verbatim) · 12 user-supplied target images
> (`Docs/reference_photos/Generated Image - SceneNN.jpg`) · the first-review intake rows
> (`w3_intake_01_05.md`, `w3_intake_06_10.md` + its §S addendum) · `w3_execution_spec_v1.md` §4/§5 ·
> `Docs/STATUS.md`.
>
> **Standing rules carried into every row below** (unchanged, not re-litigated):
> **no humans, no vehicles** anywhere in any scene (they appear in the target images as
> *composition only*) · **asset-first** (`w3_execution_spec_v1.md` §1.1) · **era / real-case
> doctrine** — 실사례 > 법령 where they disagree · **Korean archetypes** · **teardown is
> authorised by the user** (*"이미 만들어진 구조라도 갈아엎어도 되니까"*), so a row may propose a
> rebuild rather than a patch · placement jitter abolished (§1.2) · one street-tree species per
> route (§1.3).
>
> **Evidence tags**: `[ref]` = read off a user target image this session ·
> `[measured]` = code read this session · `[cite]` = in-repo document quoted ·
> `[law]` = statute/standard · `[assumed]` = stated inference.

---

## 0. The user's second review — verbatim

> 일단 참고할만한 씬들 다 reference_photos에 담아뒀어. 모든 씬들 다 이미지 생성하진 못했는데, 비슷한 씬들이 있으니까 그거 참조
>
> Scen21까진 계단씬이고, 배치씬은 다른 여러 형태 더 참조해서 확장 전에 만들어 본 느낌이라, 일단 이렇게 진행해두면 될 것 같아.
>
> 다만 N2 아스팔트 패치는 너무 지저분해.. 아무리 작업했더래도 깔끔하게 작업된 느낌이면 좋겠네.
>
> Scene1 계단은 잘 표현했는데, 주변이 좀 미흡해서 차라리 계단 양옆을 자연 느낌으로 표현하고, 환경을 좀 트인 느낌으로 만들면 좋을 것 같아.
>
> Scene2 참조해서 좀 더 지하도 느낌으로 만들어주고
>
> Scene3 도 참조, 강 뷰를 좀 더 넓히는걸 추천
>
> Scene4 침목길 수풀 좀 더 추가하면 나을지도?
>
> Scene6 정체성 그렇게 안 겹치도록 이미지 참조해서 나선 구조 고쳐줘
>
> Scene8 Sunken "광장"인데 광장 느낌이 안나네.. 좀 더 곡선 구조로 제작해주면 좋겠어.
>
> Scene11까지는 아까도 코멘트했으니 적당히 알아서 해
>
> 지하 진입로 같은 경우에는 웬만하면 캐노피 진입로 끝까지 달려있도록 만들도록 하고,
>
> 바닥에 이상한 사각형 무늬는 웬만하면 다 제거해.
>
> 나머지 씬은 앞 씬이랑 코멘트가 겹치는 부분도 많기도 하고 해서 전반적으로 앞 코멘트 따라가는 씬이면 비슷하게 만들면 되긴 해.
>
> 근데 Scene18 같은 경우는 벽화 계단이랑, 바닷가가 짬뽕이 돼서 정체성이 좀 이상해진 것 같은데, 그냥 바닷가 모래사장 진입 계단 처럼 만들면 어떨까 싶네. 바다가 안 보이잖아
>
> Scene16 같은 경우는 노란색 시각장애인 보도가 입구보다 너무 멀리 있는데, 위치 체크하도록 하고, 전반적으로 그런 느낌으로 배경은 수정하면 될 것 같아.
>
> Scene17은 계단 정체성이 좀 사라진 느낌이긴 한데, 수정 깔끔하게 진행해줬으면 좋겠고,
>
> 여튼 Scenes 전반적으로 개보수해서, 좀 더 현실 기반으로 만들 수 있도록 해. 이미 만들어진 구조라도 갈아엎어도 되니까, 너무 현재 뷰에 만족하지 말고 진행하도록 해.

### 0.1 What the message rules, in order

| # | Ruling | Scope |
|---|---|---|
| **U-0** | Reference images are now in `reference_photos`. Not every scene got one — **imageless scenes ride the nearest image** (*"비슷한 씬들이 있으니까 그거 참조"*). | all |
| **U-1** | 01–21 are the **stair scenes**; the batch (batch1) scenes were built as pre-expansion studies and **stay as they are** — *"일단 이렇게 진행해두면 될 것 같아"*. | batch1 |
| **U-2** | **Except N2**: the asphalt patch is *"너무 지저분"* — it must read as **neatly executed work**. | N2 |
| **U-3** | Per-scene directives for 01 · 02 · 03 · 04 · 06 · 08 · 16 · 17 · 18 (below, in §2). | named scenes |
| **U-4** | Through scene 11 the **first review's comments still stand** — *"아까도 코멘트했으니 적당히 알아서 해"*. | 01–11 |
| **U-5** | **Underground approaches: the canopy runs the full length of the approach.** | 02 · 13 · 16 |
| **U-6** | **Remove the odd rectangular patterns on the ground**, as far as practical. | pan-scene |
| **U-7** | Scenes past 11 that repeat an earlier comment get the **same treatment** as that earlier scene. | 12–21 |
| **U-8** | **Overall renovation toward reality. Teardown authorised** — do not settle for the current view. | all |

---

## 1. Image inventory — 12 target images `[ref]`

All twelve opened and read at full resolution this session. `Docs/reference_photos/Generated Image - SceneNN.jpg`.
**Humans and vehicles are recorded for composition only and are excluded from every scene by the standing rule.**

| ID | Scene | Composition | Stair form | Materials | Season / light | Flanks | Backdrop | People / vehicles |
|---|---|---|---|---|---|---|---|---|
| **G1** | 01 | Eye-level, stair fills the lower 2/3 across the **full frame width**; plaza and buildings above the top nosing. | **Very wide monolithic granite flight**, ~7 low risers, deep treads (~0.85–0.95 m), continuous single-piece nosings running the whole frame width, no railing, no cheek wall. | Flamed light-grey granite steps; **grey interlocking block** apron at frame right at stair level; salmon/rose brick-red block band on the upper plaza. | **Autumn**, late-afternoon warm low sun; scattered fallen leaves on treads. | Frame right: the flight simply **ends and the block paving continues at the same level** — an open paved flank, no wall. Frame left: same, off-frame. | Lawn strip with a **row of dark timber benches**, a **circular jet fountain**, one banner lamp-post, clipped conifer/shrub domes, mature broadleaves in autumn colour, **collegiate stone buildings** (steep slate roofs, gables, arched windows) left/centre and a large stone institutional block right. **Open sky above the roofline — no far skyline wall.** | ~30 pedestrians (excluded) |
| **G2** | 02 | Head-on at the entrance, symmetric, eye ~1.6 m. | 6–7 **granite steps** down to an intermediate landing; escalator in the centre bay, stair bays flanking. | **Stainless-steel canopy** (brushed fascia + soffit), **glass side infill**, granite treads, **beige ceramic-tile parapet walls with granite coping**, stainless handrails (both sides + a centre rail), polished dark granite sidewalk. | **Winter**, overcast/rain — wet reflective paving. | Solid tiled parapet walls left and right, running the whole depth of the opening. | Dense downtown street — shopfronts, signage, overhead wires, mid-rise commercial blocks on both sides. | ~15 pedestrians with umbrellas (excluded) |
| | | **Canopy note (load-bearing)**: the canopy is **continuous over the entire opening**, springs from the parapet walls / perimeter columns, and carries **8+ fluorescent tube fixtures** on its soffit. **Yellow tactile dot blocks sit immediately at the stair head**, plus a long **linear guide band** running along the sidewalk in the foreground. | | | | | | |
| **G3** | 03 | Standing eye on the promenade, path receding to a **high horizon**; the river fills the **entire right third** and runs to the vanishing point. | A **wide DG/concrete flight climbing the levee slope diagonally at frame left**, ~13 steps, no railing, cheek formed by the slope itself. | Tan/beige **interlocking block** promenade with a light-grey block edge band; **rough stone (사고석) slope apron** with weeds in the joints; **dark timber post-and-rail fence** (2 rails); **backless dark timber benches**; grey single-arm streetlights. | **Summer**, midday, blue sky with cirrus. | Left: green shrub massing on the levee slope, one broadleaf tree, a **green Korean direction signboard**, a small info marker. Right: fence, reed/grass bank, then water. | **Wide river** with 2 tour boats, a long low **road bridge** on the horizon, **distant apartment towers** on the far bank, **mountain ridge line**. | 2 boats (excluded) |
| **G4** | 04 | Centred, looking **up** the flight; the stair occupies the middle third, litter floor fills the rest. | **Railway-sleeper (침목) steps**, ~14 visible, timber riser edge + compacted soil/DG tread, irregular rise, ragged nosing line. | Weathered grey-brown sleepers with checks; **round timber posts Ø~0.12 m, ~1.0 m tall at ~1.2 m pitch**; **white/cream rope in catenary sag** as the handline (no rails). | **Late autumn**, overcast white sky, flat light. | **Both flanks are a continuous deep carpet of brown oak/beech leaf litter** rising right, falling left; grey bare trunks; a few low green tufts at the right margin. | Bare deciduous woodland, no built structure at all. | none |
| **G6** | 06 | Low three-quarter from the ground beside the road; the spiral tower is at frame right, the deck runs off left. | **White RC helical stair/ramp** wrapping a large white cylinder; **smooth continuous helicoid soffit**; scalloped tread edge visible on the outer rim; a short straight flight lands at grade behind the planting. | **White painted concrete/steel** throughout; **bronze/brown horizontal tube railings** (3–4 rails) on both the helix and the deck; **glass panels** on the approach span; rough-stone (야면석) planter edge; brown timber road guardrail with yellow reflective bands; green mesh fence. | **Summer**, high sun, blue sky. | Landscaped bed at the tower foot: ornamental grasses (miscanthus), flowering shrubs, a young sapling on a **timber tripod support**; block paving. | Forested hill, low-rise village, sky. **Deck is carried on white tapered "V"-form pillars**, not on plain cylinders. | none |
| **G7** | 07 | Centred, looking up the flight through forest to the temple roofs. | **Natural stone slab (자연석) courses**, 2–4 slabs per course, irregular widths, mossy, ragged nosing. | Granite slabs with heavy moss; **boulder kerbs** on both shoulders; forest floor. | **Summer**, dappled sunlight through full green canopy. | Ferns and understory shrubs both sides; huge mossy old trunks framing left and right. | **Tiled hip-and-gable temple roofs (기와)** stepping down beyond the top of the flight. | 1 monk (excluded) |
| **G8** | 08 | **Elevated oblique from a walkway**, looking down into the bowl — the whole plaza reads in one frame. | **Curved amphitheatre bank of ~10 timber-deck tiers** on the far side; a **curved granite ramp/stair sweeping down at frame left** with glass balustrade; a second curved stair at bottom right. | Light-grey granite paving in **concentric curved bands**; warm tan/brick bands; **yellow tactile strips that follow the curves**; warm timber decking; white concrete parapets; **timber-slat soffits**; glass balustrades. | **Summer**, high sun, clear sky. | Left: curved planting beds with trees, shrubs, terracotta pots, **curved timber benches**. Right: a **two-storey retail arcade** under the deck — CAFE, BOOKSHOP, Korean signage, planters, café tables. | **CBD** — glass office towers and apartment towers on all sides; a road corridor with a **glass subway entrance kiosk** at right. **Two curved elevated decks/bridges ring the bowl at ground level.** | a few pedestrians (excluded) |
| **G9** | 09 | **Aerial oblique** over the waterfront; water fills the right half to a wooded far shore. | **Wide light-grey stone/concrete step courses (5–8) parallel to the water edge**, meeting reed beds; a **zigzag timber boardwalk** stepping down to them. | Dry-stone **자연석 terrace retaining walls**; granite step courses; timber deck boards; grey stone-block paving; square stepping-stone slabs in lawn. | **Autumn**, low warm sun, still water. | Left: **terraced planting beds** massed with pink/white cosmos, heather ground cover, ornamental grasses; a **root/stump feature** on a moss bed. Right: reeds, lily pads, water. | Still lake reflecting **full autumn hillside** (ginkgo yellow, maple orange/red) and rolling mountains. One **grey information lectern** beside the deck. | 2 tiny figures (excluded) |
| **G10** | 10 | Three-quarter from above the top landing, looking down the switchback. | **Timber deck switchback** — multiple flights and generous landings that **travel across the slope**, so daylight shows between flights; not stacked. | **Weathered silver-grey 방부목** throughout: **square newel posts with caps**, top + mid rails, **lattice/grid infill of square battens (one bay per panel)**, plank treads with gaps, timber stringers. | **Early spring / late winter**, overcast. | Right: bare earth + brown leaf litter rising. Left: bare deciduous woodland falling away, first green buds. | Woodland only. | none |
| **G11** | 11 | Wide eye-level from the sidewalk; the bridge spans the full frame. | **Straight steel flight (~22 risers)** at frame left with a **solid triangular stringer plate**, tubular handrails both sides, mesh balustrade at the head; a **second stair tower with switchback flights at frame right**, hugging the far sidewalk. | **Beige/khaki painted steel** throughout; vertical-bar deck railing with mesh panels; grey block sidewalk with a **brick-red block band**; asphalt road. | **Summer**, high sun, blue sky with cumulus. | Left: sidewalk, **yellow tactile dot-block band across the walk at the stair foot**, a **large rectangular steel grating gully cover**, a low guardrail and green verge. Right: verge, wooded hill. | Apartment towers, wooded hill, low commercial blocks; **green overhead direction signs (한글)**, a round **100 km/h** speed sign, W-beam median guardrail, lane arrows. | 3 cars (excluded) |
| **G13** | 13 | Head-on at the ramp mouth, symmetric. | No stair — a **wide descending vehicle ramp** into a basement. | **Stainless gantry sign** ("PARKING ENTRANCE") on two square posts spanning the ramp; **dark grey concrete parapet walls curved in plan**, capped with stainless tubular guardrail; **yellow/black diagonal chevron bands** and reflective strips on the wall ends; broom-finished/grooved concrete ramp with a **yellow centre line**; **yellow-black kerb blocks** on both ramp edges; a **linear trench grating across the ramp mouth**. | Spring/summer, overcast-bright. | Left: glass-fronted mall, **ginkgo street trees in tree grates**, grey bollards with yellow bands, stainless pedestrian guardrail. Right: sidewalk, ginkgo, **bus shelter**, guardrail. | Mid-rise commercial street, **utility pole with transformer and wires**, dimly warm-lit garage interior visible through the mouth. | 3 pedestrians, several cars + a bus (excluded) |
| **G18** | 18 | Eye-level on the promenade, running to a distant horizon; **sea fills the right third with the horizon line clearly visible**. | **No stair in frame** — the promenade meets the sand directly along a low granite edge. *(See §2 scene18: the stair is exactly the element the user wants inserted here.)* | Light-grey **granite block promenade**; **yellow tactile guide strip along the left edge**; warm tan band; granite kerb to the raised planting beds; stone benches. | **Late spring / summer**, blue sky with scattered cumulus. | Left: raised planting beds with **evergreen shrubs, palms and umbrella pines**, double-globe streetlights, a low granite retaining edge. Right: **golden sand** sloping to breaking surf. | **Coastal high-rise apartment wall** at left with three twisted blue glass towers; a **long suspension bridge** across the far horizon; headland. | none |

**Cross-cutting reads from the twelve, useful as project defaults** `[ref]`:

1. **Nothing in any image carries a mid-field rectangular ground decal.** Where a ground marking exists it is
   *functional* — a lane line, a tactile strip, a paving band, a trench grating, a chevron band.
2. **Tactile paving is always at the hazard or the guidance line**, never floating (G2 stair head, G8 stair
   heads following the curve, G11 stair foot, G18 promenade edge).
3. **One species per route** holds in every planted image (G3 shrub mass, G13 ginkgo row, G18 palms + pines
   as two distinct beds, G8 one clipped shrub per planter).
4. **Backdrops are open**: G1, G3, G4, G6, G9, G10, G18 all show sky above the roof/ridge line. Only G2, G8 and
   G13 close the horizon, and those are genuinely dense-urban cells.
5. **Railings and fences are the strongest era/identity cue**: rope-on-timber-post (G4), timber post-and-rail
   (G3), square-batten lattice (G10), bronze tube (G6), stainless tube (G2, G13), painted steel bar (G11),
   glass balustrade (G8).

---

## 2. Per-scene renovation rows — 01–21 + N2

Each row: **(a)** user directives (2nd review + carried 1st-review items, quoted) · **(b)** target image or
nearest-image mapping with the archetype justification · **(c)** current-code gap sketch · **(d)** scope
S/M/L · **(e)** kit dependencies · **(f)** GT class guess · **(g)** special rulings needed.

Scope key: **S** = parameter/dressing edit, ≤ ½ day · **M** = one subsystem rebuilt, 1–2 days ·
**L** = archetype-level rebuild, ≥ 3 days.
Kit key: **K1** ground_kit (decals — CB-2 landed) · **K4** scene_common + props_kit (species / prop templates /
arc-helix) · **K5** infra_kit (curbs, gutter, ramp curb, manhole derivation) · **BS-4** building_kit backdrop
kind · **GD** ground decals (scene-side counts and sites).
GT key: **A** = no walked-surface move (props/OCCL only → R-3 re-stamp) · **B** = micro z change (split proof) ·
**FULL** = walked surface moves → R-1+R-2+R-3.

---

### scene01 — campus plaza stair · `scenes/main/scene01_campus_stairs.py`

**(a) Directives.** 2nd review: *"Scene1 계단은 잘 표현했는데, 주변이 좀 미흡해서 차라리 계단 양옆을
자연 느낌으로 표현하고, 환경을 좀 트인 느낌으로 만들면 좋을 것 같아."* → the **flight itself is
approved**; the **flanks** must become natural and the **environment must open up**.
Carried 1st review: **01-A** crooked-rectangle floor pattern (patch/stain decals) · **01-B** *"paving must
run FULLY to edges (find where it stops / mixes with turf)"* · **01-C** *"the mid-plaza shrub/growth …
locate and spec removal"* · **01-D** *"bench alignment"* · G-2 species · G-3 prop-edge · G-4 manhole.

**(b) Image.** **G1**, direct. G1 also *answers* 01-B in the opposite direction to the current plan: in the
photo the paving meets a **lawn strip with benches and a fountain**, not a building plinth — the turf is
designed, kerbed and inhabited, and it is what makes the frame read open. **This is a soft conflict with
GT-4** (see (g)).

**(c) Gap.** Buildings box the plaza on both long sides (`:210-213`, R `y0=9.5` / L `y1=-10.5`) with a raw
`GroundGrass` strip between them and the paving (`:874`) — the closed, unresolved edge the user calls
*"미흡"*. Flanks of the flight are hard plaza edges, not the open block-paved apron of G1. Six benches
carry hard-coded yaw jitter (`:175-177`). `entry_canopy` at `:146` is a free-standing 4×1.4 m porch with
no counterpart in G1. `plaza_granite` prescribes `("patch",1)`+`("weed",6)`; the weed row was deleted
library-wide by A1/GT-9 `[cite]`, the patch row remains.

**(d) Scope. M** — flanks + backdrop opening + carried 1st-review rows. Not L: the flight is approved and
must not move.

**(e) Kits.** K4(b) species (one broadleaf for the plaza row, per G-2 table) · K4(c) bench/planter templates ·
**BS-4** backdrop kind for the collegiate buildings **pushed back and lowered** so sky shows above the
roofline · GD patch count 1 → 0–1 · K5 kerb line where the paving meets the lawn strip.

**(f) GT.** **A** if the flight and plaza top faces are untouched (recommended). **GT-4 is already `HELD`
in the ledger** for the plaza-extension variant — see (g); if GT-4 is retired, the FULL re-cache it declared
is retired with it.

**(g) Rulings needed.** **R01-1**: the user's *"계단 양옆을 자연 느낌으로"* + G1's kerbed lawn strip
**contradicts GT-4's** "extend paving to the building faces, no turf gap". Recommend **retiring GT-4** and
replacing it with a *kerbed lawn + bench + fountain* band — same rule (no undesigned turf), opposite
geometry, and it is what the user's own image shows. GT-4 is `HELD` on an evidence gate that this image
now closes in the other direction. **R01-2**: delete `entry_canopy` (no counterpart in G1; it is not an
underground approach, so U-5 does not protect it).

---

### scene02 — underpass entrance · `scenes/main/scene02_underpass.py`

**(a) Directives.** 2nd review: *"Scene2 참조해서 좀 더 지하도 느낌으로 만들어주고"* and, pan-scene,
*"지하 진입로 같은 경우에는 웬만하면 캐노피 진입로 끝까지 달려있도록 만들도록 하고"*.
Carried 1st review: **02-A** *"entrance canopy (비받이) — only-at-entrance is wrong; real underpasses =
none OR continuous+enclosed"* · **02-B** the flood sill (침수방지 진입 단차) · S06-B curb shape fix.

**(b) Image.** **G2**, direct, and it is the single most consequential image in the set: it **selects
Option B** of 02-A (continuous + enclosed) and thereby **reverses the ruling that produced GT-3**.

**(c) Gap.** `canopy=dict(x0=-1.8, x1=0.6, …, z_roof=2.7)` (`:240`) covers **0.6 m of a ~7.6 m descent** —
a free-standing porch on four posts. `w3_execution_spec_v1.md` §1.5 ruled **deletion**; the ledger carries
that as **GT-3** (`OPEN`, CB-7). The kerb top stands **+0.10 m above the footway** (`:222`) — the only
outright shape error in the S06-B audit. The v8 landing block at `:29-33` is still marked *"DESIGN PROPOSAL
AND IS NOT YET REFLECTED IN THE CODE"*. No flood sill.

**(d) Scope. M–L.** The canopy becomes a real enclosure (roof + side infill + soffit lighting + column
line), the parapet gets tile cladding + granite coping, tactile moves to the head, the sill and the curb
land in the same commit.

**(e) Kits.** **K5** `build_curb_line` (blocked — WINDOW 2 stopped) · K4(c) canopy/handrail templates ·
GD patch count · BS-4 for the dense street backdrop (G2 closes the horizon, so this scene *keeps* its wall).

**(f) GT.** **FULL** — GT-1 (sill) already declares it and carries GT-2 and GT-3. The canopy reversal keeps
GT-3 in the same batch but **flips its content** from deletion to construction; the OCCL move is larger, not
smaller.

**(g) Rulings needed.** **R02-1 (blocking)**: confirm the **GT-3 reversal** — canopy **full-length,
enclosed, soffit-lit**, per G2, superseding `w3_execution_spec_v1.md` §1.5 Option A. See §3(i).
**R02-2**: G2 shows an **escalator** in the centre bay; recommend **declining** it (moving machinery is
outside the project's prop vocabulary and adds no negative-obstacle value) and building **three stair bays**
instead. **R02-3**: G2's tactile is at the **stair head**, which is the statutory position and contradicts
nothing — but scene16 carries a deliberate *no-drop* tactile band (§12.6 quadrant filler). Rule the two
scenes separately; see R16-1.

---

### scene03 — riverbank levee · `scenes/main/scene03_riverbank.py`

**(a) Directives.** 2nd review: *"Scene3 도 참조, 강 뷰를 좀 더 넓히는걸 추천"* — widen the river view.
Carried: **03-A** rectangular decal masks · **03-B** bollards vs PROP-EDGE · **03-C** unnatural tree
planting · **03-D** shrub/bush replacement.

**(b) Image.** **G3**, direct. G3 sets the width target concretely: the water occupies the **entire right
third of the frame and runs to the vanishing point**, with a bridge and a far-bank apartment line closing it.

**(c) Gap.** The v4 rework **narrowed** the channel — `:48` records *"The channel narrows 22.5 → 15.8 m
(far_bank s 40→34, water s1 40→36)"*, which is the exact opposite of the directive. Levee crest is
`x −45…0, y ±40` (`:105`). Bollards sit at `cy=±2.2` on turf, 1.0 m outside the 2.4 m spur they defend
(`:189-193`). Six slope clumps are 3-ellipsoid blobs (`:209-215`). Far-tree row is deliberately irregular
(`:181-183`).

**(d) Scope. M** — channel widening is a parameter move plus a far-bank/bridge re-lay; the rest is the
carried 1st-review list.

**(e) Kits.** K4(b) species — G3 shows **one broadleaf on the crest and a uniform shrub mass**, so the
`Lombardy_Poplar` levee assignment stands · K4(b) `place_shrubs` per bed for the slope clumps · GD
`levee_paved` carries **4 patches** — the highest count in the library and the top candidate for U-6 ·
K5 (03 stays kerbless pending the S06-B photo check).

**(f) GT.** **A** — the stair and crest z ladder do not move. Widening the water plane and moving the far
bank changes no walked surface; expect an **OCCL/σ_LF re-gate only** (GT-13 far-tier albedo interacts).

**(g) Rulings needed.** **R03-1**: confirm the channel goes back **wider than v4** (target: water subtends
≥ 1/3 of the d5 frame width, matching G3) and record that this **supersedes the v4-A1/A2 narrowing**.

---

### scene04 — park sleeper trail · `scenes/main/scene04_parktrail.py`

**(a) Directives.** 2nd review: *"Scene4 침목길 수풀 좀 더 추가하면 나을지도?"* — **more undergrowth**
beside the sleeper path. Carried: **04-A** bush placement logic (row generator → massing) · **04-B** gravel
deposition scatter.

**(b) Image.** **G4**, direct — and it **redefines what "수풀" means here**: the flanks are not shrub domes,
they are a **deep continuous leaf-litter floor with bare trunks and low tufts**, plus the **rope-on-timber-post
handline** that is the actual Korean trail signature. The current shrub-dome banks are the thing to delete,
and the "more" the user wants is **ground layer + trunks + litter**, not more blobs.

**(c) Gap.** `verge=dict(...rows=((1.42,…"tuft"),…(3.85,…"shrub")))` (`:259-265`) — five constant-`cy`
rows of `add_sphere` ellipsoids on both sides, 121 instances; `tonglam_v2` scores the scene FAIL on
*"giant moss-green ellipsoid blobs"* `[cite]`. Gravel is uniform-random over the plan rectangle and lies on
the lawn (`04-B`). **There is no rope handline and no post line in the scene at all** — the single largest
fidelity gap against G4.

**(d) Scope. M–L.** Verge rebuild + a **new rope-and-post handline** prop (which G4 makes mandatory) +
litter floor + gravel masking.

**(e) Kits.** K4(b) `place_shrubs` / groundcover (`Grass_Short_A/B` procured, unused) · **K4(c) new prop
template: 로프 난간 (round timber post + catenary rope)** — this is a genuinely new prop, not a swap ·
K1/G-6 deposition scatter (currently *prepared, gated*) · GD `trail_soil` is stain-only, so U-6 is light here.

**(f) GT.** **A** for the verge and litter. The **rope handline adds new prims beside the walk line** — no
walked-surface move, but declare it like GT-15 did for scene07's boulders: **R-1 registry print + R-3 OCCL
re-stamp**, and assert it is **not** a guard (a rope handline is not a railing under the hazard taxonomy).

**(g) Rulings needed.** **R04-1**: confirm the **rope handline is dressing, not a guard** — it must not
flip this scene's negative-obstacle label. **R04-2**: G4 is **late autumn with bare trunks**; the project
season lock is summer-leaning and `Japanese_Cherry` is deleted. Confirm 04 may sit in the **autumn/leaf-off**
cell using the `BARE_SUBPRIMS` mechanism landed at `1346b70`, or state that the flanks are rebuilt in
summer dress against an autumn reference.

---

### scene05 — amphitheatre · `scenes/main/scene05_amphitheater.py`

**(a) Directives.** No 2nd-review line. U-7 applies: 05 shares an archetype with 08, and 08's directive is
*"좀 더 곡선 구조로"*. Carried: **05-A** paving module discontinuity + stage wedge gaps · **05-B** manhole
derived from a service line.

**(b) Nearest image: G8** (primary) — a **curved stepped seating bank in a modern Korean public plaza** is
exactly this scene's archetype, and G8 supplies the tier material (warm timber deck boards), the curved
paving bands, the tactile-following-the-curve rule and the planter/bench vocabulary. **G1** (secondary) for
the granite plaza module and the open sky above the roofline.

**(c) Gap.** Three different paving modules meet in one frame with no edge band (`05-A`); the stage disc
reads as thousands of ~100 mm radial units. Black wedge gaps where arc steps meet the stage disc
(`tonglam_v2` §4-7) — a real geometry defect. 1 manhole solved from the camera (`:142`, rationale `:111-114`).
The scene has **12 `build_arc_steps` sites** (ledger GT-6) and inherits the constant-chord convention bug.

**(d) Scope. M.**

**(e) Kits.** **K4(d) arc/helix convention** (GT-6 `RELEASED`, T3 published) · K4(b) species for the ring
planters · K5 manhole derivation · GD `plaza_granite` patch 1.

**(f) GT.** **B** — GT-6 already declares the landing/arc top-face +2 mm micro class with a split prim-hash
proof; 05 rides that. Wedge-gap closure is GT-11 (`OPEN`, class A expected).

**(g) Rulings.** **R05-1**: pick the paving option — (a) radial-cut 600 mm granite throughout, or (b)
small-unit fan bond separated by a 150 mm granite edge band. G8 shows **(b)-like banded curves**, which
tilts the earlier recommendation toward (b) + a strong edge band.

---

### scene06 — overpass spiral · `scenes/main/scene06_overpass_spiral.py`

**(a) Directives.** 2nd review: *"Scene6 정체성 그렇게 안 겹치도록 이미지 참조해서 나선 구조 고쳐줘"* —
fix the **spiral structure** against the image, and keep 06's identity distinct from 11's.
Carried: **S06-A** footbridge shape breakage (fascia sawtooth, constant-chord boxes, landing/deck
interpenetration, posts outboard) · **S06-B** curb legibility · **§S** approach-placement check against the
H-plan principle.

**(b) Image.** **G6**, direct. G6 settles three open design questions at once:
1. the spiral is a **smooth white helicoid soffit**, not a stack of boxes with a helical fascia ribbon;
2. the railing is **bronze/brown horizontal tubes**, distinct from 11's painted-steel vertical bars — this
   is the **identity separation the user asked for**;
3. the deck is carried on **white tapered "V"-form pillars**, not plain cylinders.

**(c) Gap.** `fascia` top line is linearly interpolated while treads step → a **±154/−38 mm z sawtooth,
26× round the helix** (`:426-432`, `:155-156`). `build_arc_steps`/`build_helix_steps`/`build_helix_ramp`
use a **constant chord computed at `r_out`**, giving up to **7.08× over-width at `r_in`** on the landing
(`scene_common.py:1637/1847/1891`). Landing and deck **interpenetrate over 9.9 m²** (`:172`, `:165-166`).
Outer railing posts stand **60 mm outboard** of the tread edge (`:238`). T3 has already **struck the
99.0 mm rim-sawtooth figure and measured 7.46 mm** `[cite]` — use T3's numbers, not the intake's.

**(d) Scope. L** — this is the arc/helix convention rebuild plus a fascia/soffit redesign plus a railing
re-section. Teardown is authorised and this scene needs it.

**(e) Kits.** **K4(d) arc/helix (blocking, WINDOW 2 stopped)** · K4(c) railing template (bronze tube, 3–4
rails) · K5 curb legibility (light granite curb, unit-segmented, + L-gutter) · BS-4 for the hill/village
backdrop (G6 is open-sky — the far tier must not close the horizon).

**(f) GT.** **B** — GT-6 (`RELEASED`) covers landing top **4.998 → 5.000**, azimuth clip, stepped fascia,
`outer_r` 3.36 → 3.24, chord margin 1.03 → 1.000, with a **split prim-hash proof**: any non-landing row in
the diff is a defect. The soffit/pillar redesign is above the walking plane → adds an **R-3 OCCL re-stamp**.

**(g) Rulings.** **R06-1**: adopt G6's **continuous helicoid soffit** as the target form (this is what makes
the true-annular-sector mesh mandatory rather than optional — boxes cannot produce it). **R06-2**: confirm
the **06 = bronze-tube / 11 = painted-steel-bar** railing split as the formal identity separation.

---

### scene07 — temple stone path · `scenes/main/scene07_temple_stone_path.py` — **EXECUTING, NOT ROUTED**

**(a) Directives.** No new 2nd-review line. G7 is the fidelity target and is already ruled authoritative.

**(b) Image.** **G7**, already bound as `[ref]` in `s3_scene07_10_rebuild_spec_v1.md` §9.1.

**(c) Status.** A live workflow holds this file. Landed this session: **GT-14** stone archetype rebuild
(28 courses × 2–4 slabs, 89 slabs, open-slope 34.0 % → 0.000 %), **GT-16** canted-knob deletion + jitter
caps, with **GT-15** (boulder kerbs) and **GT-17** (summer re-bind) declared. `[cite]` commits `cd2745b`,
`bbf085d`, `3c84961`.

**(d)–(g).** **Excluded from all routing in §4.** Do not re-plan, do not re-declare GT rows, do not touch
the file. The only cross-lane obligation: §3(ii)'s decal sweep must **not** re-open 07's leaf lobes, which
GT-17 has already re-zoned.

---

### scene08 — sunken plaza · `scenes/main/scene08_sunken_plaza.py`

**(a) Directives.** 2nd review: *"Scene8 Sunken \"광장\"인데 광장 느낌이 안나네.. 좀 더 곡선 구조로
제작해주면 좋겠어."* — it does not read as a **plaza**; make the structure **more curved**.
Carried: **S08-A** remove the temporary bollard + tape barrier (reverses a `tonglam_v2` PASS) · **S08-B**
what replaces it · the x = −18 bollard row · road lines painted with no road.

**(b) Image.** **G8**, direct, and it is a **near-total redesign brief**: curved bowl, curved timber
amphitheatre tiers, curved sweeping stair/ramp with glass balustrade, curved paving bands, curved planting
beds, a retail arcade at the lower level, and **curved elevated decks ringing the bowl at ground level**.
G8 also answers S08-B: the pit edge is guarded by a **continuous parapet with glass balustrade**, and the
opening is at the **stair head** — option **B-1** of the intake.

**(c) Gap.** The pit is a **rectangle**: `stair` south/north at `x0=0.0/8.0`, width 4.0, `parapet` a straight
run with a 1.8 m demolished gap at `gap_y0/gap_y1 = ∓0.9` (`:124-140`). Ground is a 90 × 90 m box (`:120`).
Nothing in the scene is curved. Lane markings are painted onto the plaza plane with **no road slab and no
curb** (S06-B). The tempbar is at `:1324` with params `:195-206`, materials `:906-915`, collision boxes
`:396-400`, self-check `:553-558`.

**(d) Scope. L** — the largest single item in this intake. The pit plan, the parapet, the stair heads, the
tier bank and the paving bands all become curved; the arcade and the ring decks are new.

**(e) Kits.** **K4(d) arc/helix** — curved tiers and a curved parapet are `build_arc_steps` clients, so this
scene **joins 05/06/19/13 in the convention fix's blast radius** · **BS-4** for the CBD wall (G8 legitimately
closes the horizon) · K5 curb line + the road that the markings need · K4(c) glass balustrade + timber
bench templates · GD `sidewalk_block` patch 2.

**(f) GT.** **FULL** — a curved pit plan moves every drop edge in the scene. This is a new ledger row
(GT-7 currently covers only the tempbar's two collision boxes, `R-3`). **Declare before landing**, per §0-1.

**(g) Rulings.** **R08-1 (blocking)**: authorise the **curved-plan rebuild**. It is the most expensive row
in the wave and it invalidates the scene's existing near-window occupancy arithmetic
(`:148-156`), which was solved against a rectangular pit. **R08-2**: confirm the tempbar deletion (already
ruled §1.6) **and** that the replacement is **B-1 continuous parapet, opening at the stair head**, per G8 —
this closes S08-B without needing the n≥5 photo set the intake owed.

---

### scene09 — lake-park waterfront steps · `scenes/main/scene09_ghat_riverfront.py`

**(a) Directives.** No new 2nd-review line; U-4 keeps the 1st review live. Carried: **S09-A** three
diagnostic flank cuts (**landed**, commit `50189e9`) · **S09-B** baseline record · **S09-C** mooring posts
off the stair face (**GT-10, `OPEN`**).

**(b) Image.** **G9**, direct. G9 confirms the reinterpretation the scene already chose (lake park, not
ghat) and adds three concrete targets: **dry-stone 자연석 terrace walls**, **massed flowering ground cover
in terraced beds**, and a **zigzag timber boardwalk stepping down to the step courses**.

**(c) Gap.** 36 steps / 6.12 m drop over a **10 m width** against an 80 m-wide terrace — the flight reads as
a revetment. Mooring posts stand **out of the stair face** at 3–4 heights (`:250`, `:215-217`). Terrace beds
are not massed. `plaza_water` carries **2 patches** on a waterfront — no repair cause.

**(d) Scope. M.**

**(e) Kits.** K4(b) `place_shrubs` per bed + species (`Shumard_Oak` park row) · K4(c) boardwalk/lectern
templates · GD patch 2 → 0 · K5 none.

**(f) GT.** **A** — GT-10 already declares the mooring move (props; R-1 + R-3 if OCCL moves). Terrace bed
massing is dressing.

**(g) Rulings.** **R09-1**: G9 shows **autumn**; same season question as scene04 (R04-2). Recommend
answering both with one policy line rather than per scene.

---

### scene10 — park deck switchback · `scenes/main/scene10_park_deck_switchback.py` — **EXECUTING, NOT ROUTED**

**(a) Directives.** No new 2nd-review line. G10 is the fidelity target and is already ruled authoritative.

**(b) Image.** **G10**, bound as `[ref]` in `s3_scene07_10_rebuild_spec_v1.md` §9.1.

**(c) Status.** Live workflow. **GT-20** (railing rebuild — square sections, capped newels, lattice bay,
1.10 m height on the KNPS n=1,227 built-reality basis) landed at `ed928e5`; **GT-18** (stair re-table:
6 flights, 44 risers, 1.50 m width, rest platform) is `OPEN` in the same batch.

**(d)–(g).** **Excluded from all routing in §4.** One cross-lane note: G10's *"flights travel across the
slope"* read is the same de-stacking principle §2 scene06 needs for its landing/deck overlap — do **not**
try to unify them; they are different builders in different lanes.

---

### scene11 — footbridge stairs · `scenes/main/scene11_footbridge_stairs.py`

**(a) Directives.** 2nd review: *"Scene11까지는 아까도 코멘트했으니 적당히 알아서 해"* — the first
review's rows stand and the lane has discretion. Carried, **§S addendum (verbatim)**: *"육교가 너무
양쪽으로 뻗어있어. 한국 육교는 H형이야"* — **H-plan rebuild**: stair towers rotated 90°, running
**parallel to the carriageway** on each sidewalk, deck crossing between them. Plus S06-B curb legibility.

**(b) Image.** **G11**, direct — and it **complicates the §S ruling in a useful way**. G11 shows the
**left tower as a single straight flight running roughly parallel to the road edge** and the **right tower
as a switchback hugging the far sidewalk**: i.e. a real H-plan, but **asymmetric**, with one straight leg
and one switchback leg. That is a stronger and more specific target than "both towers switchback".

**(c) Gap.** `stair` is `riser 0.125, tread 0.32, n=22, y ±0.90` (`:117`) inline with the deck axis
(`deck x −13.20…13.20, y ±1.20`, `:131`) — the I-plan sprawl the user rejected. Curb is dimensionally
correct (150 mm) but bound to `granite_dark` and built as **one continuous box** with no L-gutter (S06-B
B-1/B-2/B-3).

**(d) Scope. L** — H-plan is a plan-level rebuild of both towers.

**(e) Kits.** **K5** `build_curb_line` + `build_gutter_L` (blocking) · K4(c) painted-steel bar railing +
mesh panel templates · GD `bridge_deck` is crack/stain only.

**(f) GT.** **FULL** — rotating the stair towers moves every tread and landing top face and relocates the
drop edges. New ledger row required; declare before landing.

**(g) Rulings.** **R11-1**: adopt G11's **asymmetric H** (one straight leg + one switchback leg) rather
than a symmetric double-switchback, and record it as a refinement of the §S ruling. **R11-2**: G11's tactile
is a **band across the walk at the stair foot** — confirm this is the standard placement for all footbridge
feet (06 and 11 both).

---

### scene12 — riverside cantilever deck · `scenes/main/scene12_riverside_deck.py`

**(a) Directives.** No direct line. **U-7**: 12 repeats 03's and 17's comment set (river view, levee
promenade, timber deck), so it takes the **same treatment**. Carried: 03-A decal masks (12 is one of the
five F3 scenes), B3 reeds, N-A7 riprap, G-2 species.

**(b) Nearest images: G3** (primary — Hangang levee promenade: block paving, timber post-and-rail fence,
backless benches, streetlight pitch, **wide water**) + **G9** (secondary — timber boardwalk over water,
reed stands, the water-edge junction). Justification: 12's archetype is *"Han River waterfront cantilever
deck walk"*, which is exactly G3's promenade with G9's deck-over-water condition.

**(c) Gap.** `deck_timber` profile is stain-only, so U-6 is light. The scene shares its world with 17
(water / apartment backdrop / bridge / silver grass). The **river-width directive (R03-1) applies here too**
— 12 and 17 must not be re-widened independently of 03 or the three river scenes will disagree.

**(d) Scope. S–M.**

**(e) Kits.** K4(b) species (riverside route) · K4(b) `place_shrubs` for reeds/silver grass · GD light ·
BS-4 far-tier apartment line (GT-13 albedo override applies).

**(f) GT.** **A**.

**(g) Rulings.** none beyond R03-1's inheritance.

---

### scene13 — apartment underground parking entry · `scenes/main/scene13_apartment_parking_entry.py`

**(a) Directives.** 2nd review, pan-scene **U-5**: *"지하 진입로 같은 경우에는 웬만하면 캐노피 진입로
끝까지 달려있도록"*. Carried: **S06-B item 5** — 13 is *"the one scene that must gain a curb outright"*
(`build_ramp_curb` exists and no scene calls it; `walk_north/south proud=0.007` is a 3 mm step); **GT-5**
declares the 150 mm curb (`OPEN`, CB-9).

**(b) Image.** **G13**, direct — and it **re-reads U-5 for this scene**. G13 has **no canopy over the
ramp**: the ramp descends under the building slab, and what spans the mouth is a **stainless gantry sign**.
The "full-length cover" is delivered by the **structure itself**, plus **curved parapet walls with
chevron bands and a stainless guardrail**, and a **trench grating across the mouth**.

**(c) Gap.** `canopy=dict(x0=-1.6, x1=4.2, …)` (`:193`) covers **5.8 m of a ramp that runs to the portal at
x = 24.0** (`:128`) — a porch over 24 % of the approach. Under a literal reading of U-5 the canopy would be
extended 24 m; under G13 the correct move is **delete the porch, build the gantry + the building slab over
the portal**. No ramp curbs. `ramp_parking` carries 2 patches.

**(d) Scope. M.**

**(e) Kits.** **K5** `build_ramp_curb` + `build_curb_line` (blocking) · K4(c) gantry sign + chevron band +
trench grating templates · K4(b) species — G13 shows a **ginkgo street row in tree grates**, a clean
one-species-per-route instance · GD patch 2 → 1.

**(f) GT.** **FULL** — GT-5 already declares the `proud 0.007 → 0.150` walked-surface change, coordinated
with the carried-in ramp-curb record.

**(g) Rulings.** **R13-1 (blocking)**: does U-5 mean *"a canopy over the whole ramp"* (literal) or *"the
approach is covered for its whole length, by whatever real Korean practice uses"* (G13's answer: building
slab + gantry)? Recommend the latter and record it, because the literal reading builds a 24 m canopy that
appears in **none** of the reference images.

---

### scene14 — monumental illusion stair · `scenes/main/scene14_grandstair_illusion.py`

**(a) Directives.** No direct line. **U-7**: 14 repeats 01's and 21's comment set (wide granite civic
flight + plaza + open environment). Carried: 01-A patch snap, 01-B family audit, C6b bollard removal, G-4
manhole, module-per-surface audit from 05-A.

**(b) Nearest image: G1** (primary). Justification: 14 is *"upper viewing plaza → 40 steps with 3 landings
→ lower grand plaza"*, i.e. the same product as G1's flight at civic scale — flamed granite, continuous
nosings, no railing on the main run, plaza above and below. **G8** (secondary) for the modern paving-band
and tactile vocabulary if the scene is pushed contemporary rather than collegiate.

**(c) Gap.** `plaza_granite` (patch 1, weed row already deleted by A1/GT-9). The scene's identity depends on
the landings reading as a terrace, so **the flight geometry must not be touched** — only the surrounds and
the decals. Same "closed backdrop" risk as 01: the two distant buildings can wall the frame.

**(d) Scope. S–M.**

**(e) Kits.** BS-4 (push the backdrop back, expose sky) · GD patch count · K5 kerb line · K4(b) species.

**(f) GT.** **A** — the illusion geometry is frozen.

**(g) Rulings.** **R14-1**: confirm that the *"환경을 트인 느낌으로"* directive (01) propagates to 14 and
21 under U-7 **without** touching the concealment geometry any of them depends on.

---

### scene15 — alley labyrinth · `scenes/main/scene15_alley_labyrinth.py`

**(a) Directives.** No direct line. U-7 applies weakly — 15 has no close sibling. Carried: G-5 shrub swap,
B2d pots, E4 alley dressing cap (3 per segment), G-4 manhole (15 is the near-window pilot's origin).

**(b) Nearest image: G18** (primary, **weak**) — for the **hillside seaside town massing**: low-rise
clustered houses on a slope, which is the 감천/영도 archetype 15 is built from. **G2** (secondary) for
urban ground materials, wet granite, shopfront clutter and the signage density of a real Korean street.
**Stated honestly: this is the weakest mapping in the set.** 15 is a narrow inter-building alley and no
target image shows one. It should be routed **last** and judged conservatively.

**(c) Gap.** v5.1 already stripped the sculptural rooftop objects. `alley_concrete` carries 2 patches +
8 weeds — on a real alley, patches and weeds are **correct**, so U-6 should be applied here with the
lightest hand in the library (see §3(ii)).

**(d) Scope. S.**

**(e) Kits.** K4(b) `place_shrubs` for the pots · GD light-touch · K5 none.

**(f) GT.** **A**.

**(g) Rulings.** **R15-1**: confirm 15 is **exempt from the aggressive part of the U-6 sweep** — a
neglected alley is the one surface where patches, stains and joint weeds are the realism, not the artefact.

---

### scene16 — canopy shadow / underpass entry · `scenes/main/scene16_canopy_shadow.py`

**(a) Directives.** 2nd review: *"Scene16 같은 경우는 노란색 시각장애인 보도가 입구보다 너무 멀리
있는데, 위치 체크하도록 하고, 전반적으로 그런 느낌으로 배경은 수정하면 될 것 같아."* — the yellow
tactile band is **far too far from the entrance**; check the position, and **fix the backdrop to that
feel** (i.e. to G2's). Plus **U-5** (canopy full length). Carried: 02-A named 16 as the **in-library
reference** for the continuous-canopy form; 02-B's sill audit; C6b bollard removal.

**(b) Image.** **G2** (nearest, and effectively direct — 16 and 02 are the same archetype). G2 supplies
both halves of the directive: tactile **at the stair head**, and a **dense downtown backdrop**.

**(c) Gap — the user is measurably right** `[measured]`. The stair head is at `x = 0`
(`stairs=dict(x0=0.0, …)`, `:66-67`). The tactile band is `tactile_entrance=(-6.00, -2.5, -5.40, 2.5)`
(`:145`) — **5.40–6.00 m west of the stair head**, i.e. **~5.4 m away from the entrance**. The code states
this is deliberate: *"0.6 m × full width in front of the **building entrance**, i.e. deliberately at a spot
with **no drop** … this scene is what fills the cue+/label− quadrant (§12.6)"* `[measured]`. So the
directive **collides with a deliberate research-design device**, and cannot be executed silently.
**Canopy status: 16 already complies with U-5** — `canopy=dict(x0=-1.0, x1=4.6, …)` (`:84`) against
`stairs x0=0.0` + 14 × 0.32 = 4.48 m, i.e. the roof covers the **whole descent plus 1.0 m of approach**.
16 is the model, not a defect. Backdrop is currently grass on both sides of the walk, not a street.

**(d) Scope. M** — backdrop rebuild is the bulk; the tactile move is one tuple.

**(e) Kits.** **BS-4** street-wall backdrop (this is the main work) · K5 curb (16 currently has *"colour
without geometry"* — `M["curb"]` bound with no prim) · GD patch 2 · K4(b) species for a street row.

**(f) GT.** **A** — moving a 4 mm-proud tactile band and rebuilding a backdrop move no walked surface.
Element AABBs move → GT-8 class, regression re-stamp only.

**(g) Rulings.** **R16-1 (blocking, research-design)**: the user wants the tactile **at the entrance**; the
scene exists partly to occupy the **cue-present / label-absent** quadrant with a tactile band that marks
**no drop**. Three ways out, pick one: **(i)** move the band to the stair head and **relocate the
cue+/label− role to another scene** (N5 is the existing pilot); **(ii)** keep the far band **and add** a
correct stair-head band, so the scene carries both a true and a false cue — arguably more realistic than
either alone; **(iii)** move the band and accept the loss of the quadrant. Recommend **(ii)**: it satisfies
the user, keeps the quadrant, and is what a real Korean street actually looks like (guidance blocks at a
building entrance *and* warning blocks at the stair head).

---

### scene17 — Hangang ramp/stair pair · `scenes/main/scene17_ramp_pair_hangang.py`

**(a) Directives.** 2nd review: *"Scene17은 계단 정체성이 좀 사라진 느낌이긴 한데, 수정 깔끔하게
진행해줬으면 좋겠고"* — the **stair identity has faded**; make the correction cleanly. Carried: F4 grass,
F5 manhole (*"the worst single prop"* in 17's d5 cut, `tonglam_v2` FIX-5), S06-B kerbless-verify, J4 terrace
bench yaw snap.

**(b) Nearest image: G3** (primary) — the same Hangang levee section: crest path, planted slope, a **wide
flight cutting straight down the bank with no railing**, promenade, fence, benches, wide water, bridge, far
apartments. G3 is the direct answer to *"계단 정체성이 사라졌다"*: in the photo the **flight is the
strongest object in the left third of the frame**. **G9** (secondary) for the water-edge terrace.

**(c) Gap.** `stairs=dict(x0=0.0, riser=0.16, tread=0.32, nsteps=20)` (`:169`) — a 3.2 m drop, **width 3**,
set against a **40 m-long diagonal ramp** (`ramp=dict(p0=(0.0,4.0), length=40.0, width=2.5)`, `:204`). The
ramp is **13× the stair's plan length**, so the contrast pair reads as a ramp scene with a stair in it.
`levee_paved` carries **4 patches**, the joint-highest count.

**(d) Scope. M** — the fix is proportion and framing, not a rebuild: widen and foreground the flight,
shorten or re-site the ramp, re-aim the cuts.

**(e) Kits.** K4(b) species + `place_shrubs` (silver grass already de-boxed in v6) · GD patch 4 → 1 ·
K5 (17 is one of the three kerbless-by-design scenes pending verification) · BS-4 far tier (GT-13).

**(f) GT.** **FULL if the flight is widened or moved** — the drop edge relocates. **A** if only the ramp and
the camera framing change. **Recommend deciding this before the row is written**, because it determines
whether 17 can ride a light gate or needs its own.

**(g) Rulings.** **R17-1 (blocking)**: which lever restores the stair identity — **(i)** widen the flight
(GT-FULL), **(ii)** shorten/re-site the ramp so the pair is legible in one frame (GT-A), or **(iii)**
re-aim the cuts only (GT-A, cheapest, weakest)? G3 supports **(ii)** most strongly: in the photo the ramp is
absent entirely and the flight owns the slope.

---

### scene18 — mural stair · `scenes/main/scene18_wavy_artstair.py`

**(a) Directives.** 2nd review: *"Scene18 같은 경우는 벽화 계단이랑, 바닷가가 짬뽕이 돼서 정체성이 좀
이상해진 것 같은데, 그냥 바닷가 모래사장 진입 계단 처럼 만들면 어떨까 싶네. 바다가 안 보이잖아"* —
the mural-stair and seaside identities are **mixed into incoherence**; make it simply a **beach sand access
stair**; **the sea is not visible**. Carried: 01-A patch family, module-per-surface audit.

**(b) Image.** **G18**, direct — and the mapping needs a stated inference: **G18 contains no stair**. It is
a promenade meeting sand. The renovation is therefore *"take G18's promenade + sand + visible sea, and
insert the granite access flight down to the sand"* — which is the commonest form on Korean beaches
(해운대·광안리 진입 계단) and the literal reading of *"바닷가 모래사장 진입 계단"*. `[assumed]`, stated.

**(c) Gap.** The scene is a **hillside culture-village mural stair** (`:72`, *"neighbourhood mural (painted)
stair"*) that had a coastline bolted on in v6 (`:212-219`: cut the ground at `x1=34`, lay water at
`x0=31.0` with top −3.35, push the town off the view axis to expose the horizon). `_sea_selfcheck()` claims
54–100 % frame openness — **the user still cannot see the sea**, so either the check measures the wrong
thing or the town/paving reads before the water does. The mural itself (7 low-saturation colours × 3 wear
variants, diagonal bands) is the identity the user is asking to **drop**.

**(d) Scope. L** — an archetype swap: hillside village → beach promenade. Teardown authorised.

**(e) Kits.** K4(b) species — G18 shows **palms + umbrella pines as two distinct beds**, which is a
one-species-per-bed instance and needs assets the project may not have (see (g)) · GD `plaza_granite`
patch 1 · BS-4 for the coastal high-rise wall and the bridge on the horizon · K5 granite kerb to the
planting beds.

**(f) GT.** **FULL** — a beach access flight is a different flight at a different place with a different
drop. The current 16 × 0.16 = 2.56 m drop can be **preserved as an invariant** to limit the re-cache (the
scene07/scene10 precedent: keep the total drop, rebuild everything else).

**(g) Rulings.** **R18-1 (blocking)**: confirm the **identity swap** — mural stair is **deleted**, not
relocated. This retires the scene's camouflage-contrast research axis (*"high-contrast colour actually
disrupts drop perception"*), which is a **research-design loss**, not just a look change; if that axis must
survive, it needs a home in another scene. **R18-2**: palms/umbrella pines are almost certainly **not** in
`VEG_TREES` (the pixel-verified green set is Elm / Shumard Oak / Chinese Juniper / two pines). Either
procure, or substitute pines only and accept a less coastal read.

---

### scene19 — fan winder (rooftop) · `scenes/main/scene19_fan_winder.py`

**(a) Directives.** No direct line. U-7: 19 shares the **arc-step** vocabulary with 05 and 08, so it inherits
08's *"곡선 구조"* framing and 05's paving-module row. Carried: F1 membrane rebind, N-A3 rooftop equipment,
era rider B (rail 1.1 m), G-4 manhole.

**(b) Nearest image: G8** (primary) — the only image with **curved concrete/granite steps, curved parapets
and a modern Korean urban complex**; it supplies the arc-step material, the parapet section and the CBD
roofscape 19's rooftop reframing needs. Secondary: **G13** for rooftop/utility hardware realism
(transformer, conduit, mounted equipment).

**(c) Gap.** 12 fan steps, `r_in 1.2 / r_out 4.0`, 7.5° sectors — **4 `build_arc_steps` sites** carrying the
constant-chord bug (`:265` already carries an independent note about the 1.03 factor `[cite]`).
`roof_membrane` prescribes **3 patches** — the second-highest count, on a **roof membrane**, where a repair
patch is genuinely real (membrane patching) but three of them on one small roof is not.

**(d) Scope. M.**

**(e) Kits.** **K4(d) arc/helix (blocking)** · BS-4 for the surrounding roofscape · GD patch 3 → 1 ·
K4(c) rooftop equipment templates.

**(f) GT.** **B** — rides GT-6's split proof (19 is named in the blast radius).

**(g) Rulings.** none blocking.

---

### scene20 — diagonal oblique stair · `scenes/main/scene20_diagonal_oblique.py`

**(a) Directives.** No direct line. U-7: 20 is a plaza stair, so it follows **01** (open environment,
natural flanks) and **01-A** (decals). Carried: F1 ghost patches (20 is named), C6b bollard removal,
G-1 (20's `rot` key is a **scene-wide skew, not jitter** — do not "fix" it), G-4 manhole.

**(b) Nearest image: G1** (primary) — granite plaza, wide low-riser flight, benches, planters, streetlights,
open sky; the archetype is identical, only the 30° rotation differs. **G8** (secondary) for the paving-band
and tactile vocabulary.

**(c) Gap.** `plaza_granite` patch 1 + F1's ghost patches. Three axis-aligned buildings close the horizon —
same "open it up" move as 01 and 14. The 30° rotation is the scene's whole point and is frozen.

**(d) Scope. S–M.**

**(e) Kits.** BS-4 · GD · K5 kerb line · K4(b) species · K4(c) bollard template (C6).

**(f) GT.** **A**.

**(g) Rulings.** **R20-1**: restate in the row that `scene20`'s `rot` and `scene18`'s −2.57° are
**scene-wide skews, not per-instance jitter** (`w3_intake_06_10.md` §1.2), so a later linter pass does not
zero them.

---

### scene21 — monumental self-occlusion stair · `scenes/main/scene21_monumental_selfocclude.py`

**(a) Directives.** No direct line. U-7: follows **01** and **14**. Carried: 01-B family audit, G-4 manhole,
B-F1 glazing (GT-12), module-per-surface audit.

**(b) Nearest image: G1** (primary) — G1's **large stone institutional block at frame right** is the closest
real Korean referent for 21's government-office facade, and G1's flight is the same product (wide, flamed
granite, continuous nosings, self-occluding from a low eye). Secondary: **G8** for contemporary civic
paving if the scene is modernised.

**(c) Gap.** Marble terrace + 4-column facade hint + 18 steps + stone parapets + 2 central stainless railing
lines + lower grand plaza + 2 flagpoles. `plaza_granite` patch 1. The self-occlusion geometry is the
scene's identity and is frozen. Risk: marble is the single brightest material family in the library
(the same defect class as 05's plaza, `tonglam_v2` D5).

**(d) Scope. S–M.**

**(e) Kits.** BS-4 · GD · K5 · K4(b) species (G1 shows clipped conifer domes + broadleaves — a civic
planting instance).

**(f) GT.** **A**.

**(g) Rulings.** none blocking. Note under R14-1.

---

### sceneN2 — asphalt patch (batch1) · `scenes/batch1/sceneN2_asphalt_patch.py`

**(a) Directives.** 2nd review: *"다만 N2 아스팔트 패치는 너무 지저분해.. 아무리 작업했더래도 깔끔하게
작업된 느낌이면 좋겠네."* — the patch is **too messy**; *however much work was done*, it should read as
**neatly executed**. This is the **only batch1 exception** to U-1. Carried: `bc.jit_*` call-site removal
(N2 ×3, landed at `10b3946`), F1 constant-colour materials + crack-kind rebind, C5b tree pit → 수목보호판,
G-4 manhole rule.

**(b) Nearest images: G11** (primary) — asphalt carriageway with **crisp white lane markings, a yellow edge
line, a W-beam guardrail, block sidewalk and a rectangular steel grating** — i.e. the exact surface family
N2 models, photographed as a **clean, maintained** road. **G13** (secondary) — asphalt approach, yellow-black
kerb blocks, trench grating, painted centre line: the *"work done neatly"* look at close range.

**(c) Gap — the mess is a pile-up, not a shape problem** `[measured]`. On one small apron the scene carries:
- its **own 2 repair patches** — already neat: `patches=[small 2.0×1.5 @ x2.6–4.6, main 5.0×4.0 @ x7–12]`
  with a **0.08 m cut line** and a z-stratigraphy that lets the patch swallow the stall paint (`:76-101`);
- **plus 3 more ground_kit repair patches** at `(-1.20,0.00), (-3.80,0.30), (-8.80,-0.30)` — placed by the
  **near-window budget**, one per d2/d5/d10 camera window (`:143-151`), i.e. by the camera, not by a repair;
- **plus 6 near-view cracks, tyre and oil stains, edge weeds, and a manhole at `x=-2.40`** chosen by the
  same 25 %-screen-width rule (`:127`, `:139-141`).

That is **5 patches, 6 cracks, 2 stain kinds, weeds and a manhole in ~12 m of apron**. The scene's own work
is tidy; everything the near-window budget added on top is what reads as 지저분.

**(c-2) What "neat" means in the real product** `[law]` `[assumed]`. Korean asphalt repair is a
**cut-and-fill operation, and its geometry is rectangular by construction**: the damaged area is cut with a
**커터(concrete saw)** *"일정 크기와 깊이로 절단 및 파쇄가공하여 보수 홈을 형성"*, the block is removed,
and new mix is laid flush; at larger scale the same job is done as **절삭 덧씌우기 (mill-and-overlay)**,
which leaves a **machine-straight rectangular milled panel**. So:

> **A real Korean repair patch IS a neat saw-cut rectangle.** The user's *"깔끔하게"* therefore means
> **neat contractor geometry** — one straight-edged rectangle per repair, square corners, a uniform-width
> cut seam, one uniform new-asphalt tone, flush to the surrounding surface, with the surrounding pavement
> left undisturbed. It does **not** mean organic lobes. Turning N2's patches into DEC-1 blots would be the
> **wrong** fix and would destroy the scene's hard-negative premise (a black rectangle that is not a hole).

**(d) Scope. S** — this is a **deletion pass**, not a rebuild. Highest value per hour in the wave.

**(e) Kits.** GD (delete the 3 near-window patches, cut the crack count, drop the stains and weeds) ·
K5 manhole derivation (retire the `x=-2.40` magic value; a 12 m apron correctly yields **0 or 1**) ·
K4(c) C5b 수목보호판.

**(f) GT.** **A** — all of it is decal-class. Element AABBs move (GT-8 class) → **regression re-stamp only**.
N2 is also the scene that carried the **maximum GT-9 exposure (0.1174)**, so re-check that figure after the
weed row changes.

**(g) Rulings.** **R-N2-1**: confirm that the fix is **subtraction plus crisper cut seams**, and that the
**rectangles stay rectangles** — with the §3(ii) distinction recorded so a later U-6 sweep does not
"de-rectangle" the one scene whose rectangles are correct.

---

## 3. Global directives

### 3(i) 지하 진입로 — canopy runs the FULL LENGTH. **This is a reversal of GT-3.**

**User text**: *"지하 진입로 같은 경우에는 웬만하면 캐노피 진입로 끝까지 달려있도록 만들도록 하고"*.

**What is currently on the books** `[cite]`:

| Instrument | Current content |
|---|---|
| `w3_execution_spec_v1.md` §1.5 | scene02 ruling — **Option A: delete the canopy** ("canopy delete · sill · curb · landing-block delete", as **one** CB-7 commit with **one** GT re-cache) |
| `Docs/audit_v4/gt_changes_w3.md` **GT-3** | *"02 · **Canopy deletion** (ruling §1.5, Option A) · No walked-surface z change; **OCCL baseline moves** — four posts and a 2.4 × 4.9 m slab **leave** every cut · **R-3 only** (re-stamp OCCL) · CB-7 · `OPEN`"* |
| `w3_intake_01_05.md` **02-A** | Options A (none) / B (continuous + enclosed) both permitted by 「지하공공보도시설…규칙」 제8조 ⑦; Option A recommended on era grounds |

**What the user has now ruled**: the canopy is **built and continuous**, not deleted. **G2 confirms it in
the target image** — a full-width stainless canopy over the entire opening with soffit lighting, i.e.
exactly **Option B**.

> **REVERSAL — GT-3 must be amended from *deletion* to *full-length enclosure*.**
> The row's re-cache class (**R-3 only**, OCCL re-stamp) survives — a canopy still moves no walked surface —
> but its **content, its prim delta and its sign all flip**: prims are **added**, not removed, and the OCCL
> move is **larger** than the deletion it replaces. `w3_execution_spec_v1.md` §1.5's Option-A ruling is
> superseded on this one clause; the sill, the curb reshape and the landing-block resolution in CB-7 are
> **unaffected**.
>
> **This lane does not touch the ledger.** The running scene07/scene10 workflow owns
> `Docs/audit_v4/gt_changes_w3.md` right now. **Deferred action, for the ledger owner (T5/S2) after that
> workflow completes**: amend GT-3 in place (or supersede it with GT-3a), and **CB-7 must be respec'd**
> before it is cut.

**Enumeration — which scenes have an underground approach, and their canopy state** `[measured]`:

| Scene | Approach | Current canopy | Verdict under U-5 |
|---|---|---|---|
| **02** underpass | 지하보도 stair, pit runs `x 0 → ~8.2` | `x −1.8 … 0.6` (`:240`) — **0.6 m of a ~7.6 m descent**, 4 free posts | **FAILS.** Rebuild as G2: continuous, springing from the parapet walls, soffit-lit, full descent + ≥1 m of approach. **This is the GT-3 reversal.** |
| **16** canopy shadow | 지하보도 stair, `x 0 → 4.48` | `x −1.0 … 4.6` (`:84`) — **whole descent + 1.0 m approach** | **PASSES.** 16 is the in-library reference form. Do not disturb the roof; 16's work is the tactile (R16-1) and the backdrop. |
| **13** parking entry | 지하주차장 ramp, `x −14 → portal x 24` | `x −1.6 … 4.2` (`:193`) — **5.8 m of a 24 m ramp** | **FAILS as built**, but G13 shows the real answer is **building slab + gantry sign**, not a 24 m canopy. See **R13-1**. |
| **08** sunken plaza | pit stair to an underground mall | none | **Excluded** — G8 shows an open sunken bowl with no entrance canopy. A sunken plaza is not a 지하 진입로. |
| **D4** subway platform | underground, no modelled surface approach | n/a | **Excluded** (and batch1 is frozen under U-1). |

Also note: `scene01:146` and `scene05:308` carry `entry_canopy` porches that are **not** underground
approaches. U-5 does not protect them; both are recommended for deletion (R01-2).

---

### 3(ii) Rectangular ground patterns — the sweep, and the N2 reconciliation

**User text**: *"바닥에 이상한 사각형 무늬는 웬만하면 다 제거해."*

**What has already landed** `[measured]`, commit `11d1e56` (CB-2, WINDOW 1 closed):
- **DEC-1** `build_blot` — free-form stains (dirt / water / oil / gum / efflorescence / drip) are now
  **irregular lobes**, not boxes (`ground_kit.py:671`, `:1250-1298`);
- **DEC-2** — leaf / gravel **carpet edges** are blots at low roughness, not rectangles (`:748`);
- **DEC-3** — repair patches are **module-snapped and axis-locked**; `yaw_max` is replaced by a fixed
  `yaw_deg` (`:603-614`, `:931-957`).

So the shape half of the problem is done. **What is left is a placement-and-count problem**, and that is
what the user is seeing.

**Enumeration — rectangular ground elements still shipping, by profile** `[measured]`
(profile → scenes → prescribed patch count; `plaza_granite`'s weed row is already deleted by A1/GT-9):

| Profile | Scenes | Patches | Assessment under U-6 |
|---|---|---|---|
| `levee_paved` | **03 · 17** | **4** | **Worst offender.** A riverside levee promenade has no reason to carry four repair patches. → 1 or 0. |
| `roof_membrane` | **19** | **3** | Membrane patching is real, but three on one small roof is not. → 1. |
| `verge_rural` | **D3** | 3 | batch1 — frozen under U-1. |
| `street_asphalt` | **N2** (+ D3 road region) | 3 | **The pile-up in §2 N2.** → 0 kit patches; the scene's own 2 stay. |
| `plaza_water` | **09** | 2 | A waterfront terrace with two repairs and no cause. → 0. |
| `sidewalk_block` | **02 · 08 · 16** (+ C2 · C4 · N5) | 2 | Plausible on a city footway. → 1 each for the main scenes. |
| `alley_concrete` | **15** | 2 | **Keep.** A neglected alley is where patches belong (R15-1). |
| `ramp_parking` | **13** | 2 | Plausible at a ramp mouth. → 1. |
| `ramp_road` | N4 | 2 | batch1 — frozen. |
| `plaza_granite` | **01 · 05 · 14 · 18 · 20 · 21** (+ C1 · N1 · N3) | 1 | Already minimal; on a maintained civic plaza → 0–1. DEC-3 makes each one a *replaced flag*. |
| stain-only | 04 · 07 · 12 · 10 · 06 · 11 · D1 · D2 · D4 | 0 | Already lobes after DEC-1. Nothing to do. |

**Non-decal rectangles that also read as "이상한 사각형 무늬"** and belong in the same sweep:
1. **`scene16`'s no-drop tactile band** — a 0.60 × 5.0 m yellow rectangle floating in a walk, 5.4 m from the
   entrance. This is the single most conspicuous one, and the user named it independently (R16-1).
2. **`scene08`'s tactile ring** with 2 deliberately missing tiles, on a rectangular pit that G8 says should
   be curved.
3. **`scene18`'s geometric slab joints** (*"slab joints made geometric"*, `:110`) on a surface that is
   being replaced anyway.
4. **Joint grids** (`build_joint_grid`) — orthogonal, axis-aligned, **correct and staying**. A 600 mm
   granite module *is* a grid of rectangles. Do not sweep these; G1 and G18 both show them plainly.

**The N2 reconciliation — state this explicitly in every downstream row:**

> **Repair patches and soiling are different objects and take opposite treatments.**
>
> | Object | Real geometry | Treatment |
> |---|---|---|
> | **Repair patch** (아스팔트 절삭·커팅 보수, 덧씌우기 패치; a replaced paving flag) | **Straight-edged rectangle**, saw-cut with a 커터 or milled by machine, square corners, aligned to the road or the paving module | **Stays rectangular.** DEC-3 module snap + axis lock. Reduce the **count**, place it where a repair has a **cause**, and make the **cut seam crisp and uniform**. |
> | **Soiling, leaf drift, gravel carpet, water/oil/gum blots, silt** | **No straight edge exists** | **DEC-1 / DEC-2 lobes.** Already landed. |
>
> **N2 is the scene where the rectangles are the point.** *"깔끔하게 작업된 느낌"* = **neat contractor
> geometry** — one clean saw-cut rectangle per repair, crisp uniform seam, one tone, flush, surroundings
> undisturbed. It does **not** mean lobes. The sweep therefore **subtracts clutter from around N2's
> patches** and leaves the patches themselves rectangular and sharper than before.

---

### 3(iii) batch1 stays as-is, except N2

**User text**: *"배치씬은 다른 여러 형태 더 참조해서 확장 전에 만들어 본 느낌이라, 일단 이렇게
진행해두면 될 것 같아. 다만 N2 아스팔트 패치는 너무 지저분해…"*

**Ruling**: the 13 batch1 scenes (`C1 · C2 · C4 · D1 · D2 · D3 · D4 · N1 · N2 · N3 · N4 · N5`) are
**frozen for renovation** in this wave. **N2 is the sole exception** and is routed as a small deletion pass.

**Carve-outs that are *not* renovation and therefore still apply** (they are library-wide mechanical work
already ruled and partly landed): `bc.jit_*` call-site removal (landed, `10b3946`) · the DEC-1/2/3 shape
change that arrives through `ground_kit` defaults (landed, `11d1e56`) · the G-4 manhole rule when K5 lands ·
species assignment when K4(b) lands. These change *how a shared builder behaves*, not what a batch1 scene
is. **What is frozen is scene-level redesign**: no archetype changes, no new props, no backdrop rebuilds,
no camera changes in batch1.

**Consequence for `w3_execution_spec_v1.md` §4.3**: **WP S7** (N1 · N2 · N3 · N4) and **WP S8**
(C1 · C4 · D1 · D2 · D4) shrink to the mechanical carve-outs plus N2's deletion pass. Their released
capacity is the obvious source of hands for scene08 and scene18, the two L-scope rows this intake adds.

---

## 4. Execution proposal

**Principle carried from `w3_execution_spec_v1.md` §4**: *every file has at most one owner at any instant.*
The lanes below are **file-disjoint**. Ordering is by dependency, then by evidence value.

### Lane 0 — RUNNING: scene07 / scene10 (do not touch)

Owner: the live S3 workflow. Files: `scenes/main/scene07_temple_stone_path.py` ·
`scenes/main/scene10_park_deck_switchback.py` · `scene_common.py` (K4 micro-commit) ·
`Docs/audit_v4/gt_changes_w3.md`.
**Everything below waits on this lane for `scene_common.py` and for the GT ledger.**
Exit signal: GT-14/15/16/17 and GT-18/20 landing records filled, and `scene_common.py` released.

### Lane 1 — KIT REVIVAL (WINDOW 2 respec + reopen). **Blocks 8 of the 12 scene rows.**

WINDOW 2 was **stopped, not closed** (`s3_scene07_10_rebuild_spec_v1.md` §8.R OQ-3: *"WINDOW 2 is
*stopped* (not closed); `scene_common` has no active owner"*). It must be **respec'd against the images**
before it reopens, because three of its rows now have new, image-derived requirements:

| Sub-lane | Files | Respec required by the images |
|---|---|---|
| **1a · K4(a)+(d)** — baluster gate, then arc/helix convention | `/scene_common.py` | **(d) grows a client**: scene08's curved plaza joins 05 · 06 · 19 · 13. G6's **continuous helicoid soffit** makes the **true annular-sector mesh** (option (a)) mandatory rather than budget-optional. Keep the ordering (a)→(d) and the GT-6 split prim-hash proof. |
| **1b · K4(b)** — species | `/scene_common.py` (same window, sequenced after 1a) | Image-confirmed instances to fold into the `SCENE_SPECIES` table: **G13 ginkgo street row**, **G3 single crest broadleaf + uniform shrub mass**, **G18 palms + umbrella pines as two beds** (R18-2 — procurement may be needed), **G1 clipped conifer domes + broadleaves**. |
| **1c · K4(c)** — prop templates | `/scene_common.py` · `/props_kit.py` *(new)* | **New templates the images force**: 로프 난간 (round timber post + catenary rope, G4) · bronze horizontal-tube railing (G6) · square-batten lattice railing (G10 — but that lands in Lane 0, so **read it, do not write it**) · glass balustrade (G8) · stainless gantry + chevron band + trench grating (G13). |
| **1d · K5** — infra kit | `/infra_kit.py` | Unchanged scope: `build_curb_line` · `build_gutter_L` wiring · `build_ramp_curb` wiring · manhole derivation. **Image support is now strong**: G11 and G13 both show the 보차도 section and the trench grating plainly. Runs in parallel with 1a–1c (different file). |
| **1e · CB-7 respec** — scene02 | `Docs/briefs/w3_execution_spec_v1.md` §1.5 (spec edit, not code) | **Rewrite Option A → Option B**: canopy **full-length + enclosed + soffit-lit**, per G2; keep sill + curb + landing-block resolution in the same commit and the same single GT re-cache. **Then** the ledger owner amends **GT-3** (§3(i)). |

**Gate**: GATE-1 pilots per `§5.2` — CB-5 pilots **03 · 06 · 05 · 01**; CB-6 pilots **06 · 13 · 02**.

### Lane 2 — IMAGE SCENES (one owner per scene, ordered)

Ordered by *(evidence strength × user emphasis) ÷ dependency depth*.

| # | Scene | Image | Scope | Depends on | Pilot / GT plan |
|---|---|---|---|---|---|
| **2.1** | **N2** | G11 · G13 | **S** | none (GD + K5 manhole; K5 optional) | **Ship first.** Pure deletion, class A, regression re-stamp only. Highest value per hour; directly answers a named complaint. Re-check the GT-9 max-exposure figure (0.1174). |
| **2.2** | **16** | G2 | M | BS-4 (landed, `c2676d6`) · K5 for the curb | Tactile move is one tuple; backdrop is the bulk. GT **A**. **Blocked on R16-1** for the tactile decision only — the backdrop can start immediately. |
| **2.3** | **02** | G2 | M–L | **K5** · CB-7 respec (1e) · ledger amendment | Pilot **02** + **FULL** re-cache (GT-1 carries GT-2 + amended GT-3). One commit, one re-cache. |
| **2.4** | **03** | G3 | M | K4(b) · GD | Pilot **03**. GT **A**; expect a σ_LF / far-tier re-gate (GT-13 interaction). Sets the river-width constant that 12 and 17 inherit. |
| **2.5** | **01** | G1 | M | BS-4 · K4(b/c) · GD | Pilot **01**. GT **A** if GT-4 is retired (R01-1); FULL if it is not. |
| **2.6** | **06** | G6 | L | **K4(d)** — hard block · T3's numbers | Pilot **06** + **GT-6 split prim-hash proof** (landing rows only; any other non-empty row is a defect). Archive 05 · 06 · 19 judge baselines **before** `scene_common` is cut. |
| **2.7** | **11** | G11 | L | K5 · K4(c) | Pilot **11**. **FULL** re-cache, **new ledger row required** (H-plan moves every tread). Land after 06 so the shared overpass world is settled once. |
| **2.8** | **13** | G13 | M | **K5** (`build_ramp_curb`) | Pilot **13**. **FULL** — GT-5 already declares the 150 mm curb. **Blocked on R13-1** (canopy reading). |
| **2.9** | **09** | G9 | M | K4(b) | Pilot **09**. GT **A**; GT-10 already declares the mooring move. |
| **2.10** | **08** | G8 | **L** | **K4(d)** · BS-4 · K5 | Pilot **08**. **FULL + new ledger row.** The largest row in the wave; invalidates the scene's near-window arithmetic. **Blocked on R08-1.** |
| **2.11** | **18** | G18 | **L** | K4(b) (+ possible procurement) · BS-4 · K5 | Pilot **18**. **FULL**, with **total drop 2.56 m held invariant** to bound the re-cache (the 07/10 precedent). **Blocked on R18-1.** |
| — | 07 · 10 | G7 · G10 | — | — | **Lane 0. Not routed here.** |

### Lane 3 — IMAGELESS SCENES (ride the nearest image)

Each row states its reference so the executor never invents one. All are **GT class A** unless marked.

| # | Scene | Nearest image(s) | Archetype justification | Scope | Depends on |
|---|---|---|---|---|---|
| **3.1** | **12** | **G3** + G9 | Hangang promenade + deck-over-water; 12 shares its world with 17 | S–M | 2.4 (river width) |
| **3.2** | **17** | **G3** + G9 | Same levee section; G3 shows the flight owning the slope, which is the *"계단 정체성"* answer | M | 2.4 · **R17-1** (decides GT class: A or FULL) |
| **3.3** | **20** | **G1** + G8 | Granite plaza stair; only the 30° rotation differs | S–M | BS-4 · K4(c) |
| **3.4** | **14** | **G1** + G8 | Civic-scale version of the same granite flight | S–M | BS-4 |
| **3.5** | **21** | **G1** + G8 | G1's stone institutional block is the closest real referent for the office facade | S–M | BS-4 |
| **3.6** | **05** | **G8** + G1 | Curved stepped seating bank in a modern Korean plaza | M | **K4(d)** · GT-6 (B) · GT-11 |
| **3.7** | **19** | **G8** + G13 | Only image with curved steps + curved parapets + urban roofscape | M | **K4(d)** · GT-6 (B) |
| **3.8** | **15** | **G18** (weak) + G2 | Hillside seaside town massing; **weakest mapping in the set — route last, judge conservatively** | S | R15-1 |

**Batching for gates**: 3.3–3.5 are one plaza batch (shared BS-4 + GD work, three disjoint files);
3.6–3.7 are one arc-step batch riding GT-6's proof; 3.1–3.2 are one river batch riding 2.4's width
constant; 3.8 rides alone.

### Lane 4 — Judging

`X2` gallery v2 (with the **archetype panel thumbnail beside each h0.3_d5 tile** — now trivially satisfied,
since 12 scenes have a user target image) → `X3` 통람 v3. Note that **GATE-3 is currently suspended** under
the per-scene-image doctrine (§8.R OQ-4); this intake gives the supervisor the material to reopen it, since
the per-scene image requirement is now met for 12 of 21 scenes and mapped by archetype for the other 9.

---

## 5. Open questions for the supervisor

Only genuinely blocking ones. **1–4 block a lane; 5–8 block a single row.**

1. **GT-3 reversal — confirm.** G2 shows a full-length enclosed canopy. Does
   `w3_execution_spec_v1.md` §1.5's **Option A (delete)** become **Option B (build, full length, enclosed,
   soffit-lit)**, with GT-3 amended in place (content flips, `R-3` class survives) and **CB-7 respec'd**?
   *Blocks Lane 1e and 2.3.*
2. **scene08 curved rebuild — authorise?** G8 says the sunken plaza is curved throughout (bowl, parapet,
   tiers, paving bands, ring decks). This is the wave's largest row, needs a **new FULL GT row**, and
   invalidates the scene's existing near-window occupancy arithmetic. Authorise, defer, or scope down to
   "curved tier bank only"? *Blocks 2.10.*
3. **scene18 identity swap — authorise?** Replacing the mural stair with a beach access stair **retires a
   research axis** (colour camouflage vs drop perception). Delete the axis, or rehome it in another scene
   before 18 changes? *Blocks 2.11.*
4. **scene16 tactile vs the cue+/label− quadrant.** The user wants the yellow band at the entrance; the
   scene deliberately places it 5.4 m away, at a **no-drop** location, to fill the cue-present /
   label-absent quadrant (§12.6). Recommend **keeping the far band and adding a correct stair-head band**
   (both cues, which is also what a real street shows). Confirm, or pick move / rehome. *Blocks 2.2's
   tactile half.*
5. **U-5's meaning for scene13.** Literal (*a canopy over all 24 m of ramp*) or real-practice (*the approach
   is covered for its whole length by the building slab, with a gantry sign at the mouth*, which is what
   G13 shows and what appears in **no** image as a long canopy)? Recommend real-practice. *Blocks 2.8.*
6. **scene01 / GT-4 conflict.** The user wants *natural flanks and an open environment*; G1 shows a
   **kerbed lawn strip with benches and a fountain** where GT-4 (`HELD`) plans to **extend paving to the
   building faces and abolish the turf**. Recommend **retiring GT-4** and adopting "kerbed designed lawn,
   no undesigned turf" instead. *Blocks 2.5's GT class.*
7. **scene17 — which lever restores the stair identity?** (i) widen the flight (**FULL** re-cache),
   (ii) shorten / re-site the 40 m ramp so the pair reads in one frame (**A**), or (iii) re-aim the cuts only
   (**A**, weakest). G3 supports (ii). *Blocks 3.2's GT class, so it must be answered before the row is
   written, not at the gate.*
8. **Season policy for the autumn/leaf-off references.** G1 (autumn), G4 (late autumn, bare trunks), G9
   (autumn) and G10 (early spring) are all off the summer lock. The `BARE_SUBPRIMS` / `build_tree(bare=)`
   mechanism landed at `1346b70` (default OFF). One policy line for all four, or per scene? *Blocks 2.5,
   2.9 and the Lane-3 river batch's dressing.*

---

## 7. Supervisor rulings (07-31) — §5's eight questions closed, plus the per-row R-items

1. **GT-3 REVERSED — CONFIRMED.** §1.5 Option A (delete) → **build: full-length, enclosed,
   soffit-lit canopy** per G2/U-5. GT-3's content and prim-delta sign flip; `R-3` class survives.
   CB-7 is respec'd in Lane 1. Ledger amendment DEFERRED until the running 07/10 lane releases
   `gt_changes_w3.md` (no other writer touches it before then).
2. **scene08 curved rebuild — AUTHORIZED IN FULL** (bowl, parapet, tiers, paving bands, ring
   decks per G8). New FULL GT row; near-window occupancy arithmetic re-derived, not patched.
   Scope-down refused — the user's teardown license and the scene06 "쉬운 방향" precedent both
   point the same way. Rides Lane 1 K4(d)'s annular-sector mesh.
3. **scene18 identity swap — AUTHORIZED; the mural axis is DELETED, not relocated.** The
   colour-camouflage/drop-perception axis is retired as a research-design loss accepted under
   the user's explicit directive; the illusion family survives in scene14 + sceneN3. Revisit
   only if the user re-opens coverage planning.
4. **scene16 — R16-1 = (ii) BOTH BANDS.** Keep the far cue+/label− band (research quadrant) AND
   add a correct stair-head warning band at the statutory position (0.30 m from the first riser,
   0.6 m depth, Ø35 truncated-cone dots). This satisfies the user's position check and is what a
   real street shows.
5. **scene13 / U-5 — REAL-PRACTICE reading.** The approach is covered full-length by the
   building slab (G13); gantry + chevron at the mouth. No literal 24 m tube canopy.
6. **scene01 / GT-4 — GT-4 RETIRED.** The user's "natural flanks + open environment" supersedes
   the paving-extension plan; adopt G1's kerbed designed lawn ("no undesigned turf"). P-5's
   evidence gate dies with the row. Ledger amendment deferred as in ruling 1.
7. **scene17 — R17-1 = (ii).** Shorten/re-site the 40 m ramp so the stair-ramp pair reads in one
   frame; no flight widening (GT stays A); judge presets untouched — legibility comes from
   geometry, never from camera edits.
8. **SEASON POLICY — one line for all rows.** Every scene pins the season of its own target
   image; imageless scenes inherit their nearest image's season; leaf-off via the
   `build_tree(bare=)` mechanism (`1346b70`) + dressing; each scene runs an internal seasonal
   audit (the cherry-blossom precedent). The global summer lock is retired.
   → R04-2: scene04 = late autumn / leaf-off. R09-1: scene09 = autumn.

Per-row items: **R04-1** — the rope-on-post handline is **dressing, NOT a guard**: it must not
flip scene04's negative-obstacle label; assert that in the registry print and the report.
**R18-2** — one bounded licensed-procurement attempt (CC0/KOGL doctrine) for palm / umbrella
pine; fallback = pines-only with coastal dressing, stated plainly.

**R16-2 (user directive 07-31, supersedes ruling 4's "both bands" framing).** The user's
design intent, restated as law: **the 21 stair scenes are STAIR-CUE-FIRST**; stop-type
(점형 warning at halt points) cases were always planned as SEPARATE scenes, later — do not
sprinkle stop devices into stair scenes. Door-front tactile is a 관공서-only pattern in
reality — the "building-entrance band" rationale is DEAD. scene16's no-drop band is
re-anchored to a **횡단보도**: the walk meets the carriageway at a zebra crossing — lowered
curb (턱낮춤 ≤ 20 mm, kept clearly sub-threshold), dot warning band at the crossing approach
(0.30 m from the lowered edge, 편의증진법), crossing markings tied into the existing G2
street wall. The stair-head band (true cue) and the canopy-shadow identity stay. The
tactile-ablation withdrawal and the §12.6 re-count note stand.
**EXECUTION HELD (user 07-31: "일단 나중에 씬 번호 다시 메겨야 할 거니까, 일단 냅둬").**
Scene numbering/case taxonomy will be reshuffled later; scene16 stays as landed (stair-head
band added, far band as-is) until the renumbering round. The crosswalk anchor above is the
agreed direction WHEN that round opens — do not execute before it. The patch-vocabulary
sweep is unaffected and stays queued.

**§7.2 Supervisor rulings, batch 2 (post-FANOUT-A, 07-31)** — sources: the eight w3_sNN_v1.md
reports + redteam_fanout_a.md.
- **S03 crest promenade — PAVE, image doctrine wins.** G3's 점토블록 promenade supersedes the
  07-29 "natural" ruling (that ruling predates the target-image doctrine). Executed as a
  follow-up lane with its own FULL GT row. The river-edge post-and-rail fence stays
  **DECLINED** (OQ-2 class: the scene's no-railing × water-anchor research identity outranks
  one image element; divergence documented).
- **S09 — stepping stones ALLOWED** as physical 판석 slabs with 3D relief (the user's ban
  targets decorative rectangle DECALS, not real objects; prefer irregular outlines). Boardwalk
  0.60 m termination **ACCEPTED** (GT-economy). stone_tint 0.64→0.524 measured correction
  authorized (material micro).
- **S13 parapet refusal ACCEPTED** — the designed below-code hazard (3 m missing railing)
  outranks G13's parapet; divergence documented.
- **S11 §10-1 sidewalk narrowing ADOPTED in principle** — execute per the report's filed
  coordinates with an honestly-declared GT class. Shadow/R6: the lane's measured SUN choice
  stands (rule unsatisfiable post-H; record, don't chase).
- **S06 — shipped horizon ACCEPTED**; the G6 forested hill joins the scene07 canopy-tunnel
  item as one "high-crown belt" practice row (polish round). S06-F3 (judge-grid origin
  coupled to deck y0) → X-track decouple queue; the deck y0 move waits for it.
- **S01-F7** (E2 cross-line slot vs future tactile arm) noted for the ablation-arm design
  round. **S08/S13 GRAZE 유보** re-evaluates automatically at the first same-arm successor
  round (GATE-2/final). **S09 autumn/flowering procurement gap** → open row; an
  autumn-leaf-tint TREATMENT wrapper (T4b pattern applied to leaf materials) is the candidate
  mechanism — polish round, measured.

**Dispatch (07-31): 16 · 18 · 04 LAUNCH NOW in parallel** (no Lane-1 dependency in their core
work; K5-curb/species residues explicitly deferred to a Lane-1 follow-up pass and recorded in
each report). N2 already running. 09 · 17 · 03 · 01 · 02 · 06 · 08 · 11 · 13 and Lane 3 wait for
Lane 1. NO lane writes `gt_changes_w3.md` while the 07/10 workflow runs — GT rows are PREPARED
in reports and appended by the supervisor afterwards.

---

## 6. Sources

**User inputs**: the second review (§0, verbatim, relayed by the supervisor) · 12 target images at
`Docs/reference_photos/Generated Image - Scene{01,02,03,04,06,07,08,09,10,11,13,18}.jpg`, all opened and
read this session `[ref]`.

**In-repo `[cite]`**: `Docs/surveys/w3_intake_01_05.md` (G-1…G-6, 01-A…05-B) ·
`Docs/surveys/w3_intake_06_10.md` (P-1, P-2, S06-A/B, S07-A, S08-A/B, S09-A/B/C, S10-A, **§S** H-plan) ·
`Docs/briefs/w3_execution_spec_v1.md` §1.2/§1.3/§1.5/§1.6/§1.8/§1.9/§4.1/§4.2/§4.3/§5.1/§5.2/§5.3 ·
`Docs/briefs/s3_scene07_10_rebuild_spec_v1.md` §8.R · §9.1 · `Docs/audit_v4/gt_changes_w3.md`
§0/§1/§3 (GT-1…GT-20) · `Docs/STATUS.md`.

**Code read this session `[measured]`**: `ground_kit.py` (`:603-614` DEC-3, `:671` DEC-1 `build_blot`,
`:748` DEC-2, `:931-957` `build_patch_field`, `:1250-1298` stain lobes, `GROUND_PROFILES` §5 patch/stain
prescriptions) · `scenes/main/scene0{1,2,3,4,5,6,8,9}*.py` · `scene1{1,3,6,7,8}*.py` ·
`scene2{0,1}*.py` · `scenes/batch1/sceneN2_asphalt_patch.py` · commit history `cd2745b … 10b3946`.

**External `[law]`** — Korean asphalt repair-patch geometry (§3(ii)):

- 건설교통부 「도로포장 유지보수 실무 편람」(1999) — https://www.codil.or.kr/filebank/original/HB/OTMCHB500849/OTMCHB500849.pdf
- 국토교통부 「아스팔트 콘크리트 포장 시공 지침」(2024.07) 제5장 유지보수 — http://cyeng.iptime.org/xe/board_moct/33622
- KR101146729B1 「아스팔트 포장 보수 공법」 — 커터를 이용한 손상부위 단부 절단 — https://patents.google.com/patent/KR101146729B1/ko
- KR20110096519A 「아스팔트 도로 보수 방법 및 그 구조물」 — *"커터기를 이용하여 일정 크기와 깊이로 절단 및 파쇄가공하여 보수 홈을 형성"* — https://patents.google.com/patent/KR20110096519A/ko
- KR101253598B1 「아스팔트 콘크리트 포장도로의 보수공법」 — https://patents.google.com/patent/KR101253598B1/ko
- 「토목기사 요약 / 도로, 포장공」 — 덧씌우기 · 절삭 덧씌우기의 정의 — https://ko.wikiversity.org/wiki/토목기사_요약/도로,_포장공

**Not re-fetched**: the statutes already quoted verbatim in the first-review intakes
(지하공공보도시설 규칙 제8조 ⑤⑦ · 수방기준 고시 제2024-88호 · 도시숲·생활숲·가로수 기준 제2-3조 ·
도로의 구조·시설 기준 제16조 · 교통약자 시행규칙 별표2 · KDS 61 40 00 · KDS 34 60 10). They are cited
here by reference, not re-verified.
