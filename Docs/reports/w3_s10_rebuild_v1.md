# W3 · S10-EXEC — scene10 park deck switchback, archetype rebuild

> **Wave** W3 · **Track** S3, lane **S10-EXEC** · **Batch** CB-S3-10 · **Date** 2026-07-31
> **Branch** `feat/realism-v1` · **Files this lane wrote**: `scenes/main/scene10_park_deck_switchback.py`,
> `Docs/audit_v4/gt_changes_w3.md` (rows GT-18/19/20/21 + landing records), this report, and
> round dirs under `look_check/`. **No other scene file, no shared module** (§8.R scope guard).
> **Authority** `Docs/briefs/s3_scene07_10_rebuild_spec_v1.md` §2 · §4.2 · §8.R ·
> `Docs/surveys/s3_research_numbers_v1.md` · `Docs/briefs/w3_execution_spec_v1.md` §6.1 / §7 / §12.
> **Fidelity target** `Docs/reference_photos/Generated Image - Scene10.jpg` (**G10**).

---

## 0. Headline

Five commits landed on scene10 (four spec items plus one defect fix found by the pilot), each with
its GT row declared first and each passing the §6.1 floor.

| # | commit | item | GT | prims |
|---|---|---|---|---|
| 1 | `ed928e5` | **S3-8** railing rebuilt in square sawn timber + measured weathering patina | GT-20 | 888 → 1038 |
| 2 | `c2b6841` | **S3-9** stair re-table — 6 flights, 44 risers, 1.500 m clear width, rest platform | GT-18 | 1038 → 1266 |
| 3 | `5ce512e` | **S3-10** de-stacking, Option A — masonry shaft deleted, real 25.8 % corridor slope | GT-19 | 1266 → 1219 |
| 4 | `1962f76` | **S3-11** season re-bind — 만추 leaf-off, continuous litter, outcrop, far silhouettes | GT-21 | 1219 → 2777 |
| 5 | `e3619df` | corridor slab thickness 1.60 → 7.00 — a see-through hillside the pilot exposed | (rides GT-19) | 2777 |

**Verification floor, every commit**: `py_compile` clean · `NEGOBS_SMOKE=1` clean with
`deck_module_selfcheck` all-OK · `geom_invariance_check` R-4 1/1 and R-6 1/1 (three-arm prim hash
identical every time) · `placement_lint` delta stated below and **never negative**.

**The single number that summarises the lane**: `placement_lint` on scene10 went
**9 ERROR → 0 ERROR** (WARN 9 · BLOCK 1 unchanged). Every error was a retired tree species
(`White_Pine` ×5, `Yellow_Pine` ×4) drawn by `build_tree`'s coordinate hash; pinning the species
was a side effect of the season pin, not a separate fix.

---

## 1. STEP 0 — the intermediate round, and why it was mandatory

Spec §6.4 trap 1: scene10's newest images predated its own code. CB-2 (`11d1e56`) changed scene10
(+29/−23, 12 leaf rectangles → 4 `build_carpet_mask` lobes, gravel scatter re-tuned) but scene10 was
**not** in CB-2's pilot set (03 · 07 · C2 · 01), so `260730_w2d_fix` (13 cuts, `git_head 386fc88`)
was rendered before that change. Diffing the rebuild against it would have carried CB-2's delta
entangled with the archetype work.

**Round `260731_w3_pre10`** — scene10 at HEAD `1346b70`, 5 cuts, the exact view list of
`260731_w3_cb2` so the two scenes share a comparison basis. `look_check/scene10/260731_w3_pre10/`.

**Adjudication against `260730_w2d_fix`** (the 5 shared cuts only, `--only`):

| cut | verdict | reading |
|---|---|---|
| `preset_h0.3_d2` | WARN `[UNCHANGED]` | mean difference **0.24 LSB**, pixels over 4 LSB **0.063 %** |
| `preset_h0.3_d5` | INFO | block shift 6, CAPTURE-class |
| `preset_h0.3_d10` | INFO | block shift 8, CAPTURE-class |
| `preset_h0.9_d2` | PASS | — |
| `preset_h0.9_d5` | PASS | — |

**FAIL 0.** The finding worth recording: **CB-2's scene10 edit is real in code and invisible in the
five preset cuts.** The four surviving leaf drifts sit at `cx` −3.2 / −5.6 / 1.4 / 5.0, i.e. at the
camera's feet or down in the lower park, and the gravel re-tune moved a scatter that the near band
barely samples. So the "unrendered CB-2 delta" that §6.7 flagged as a wave-long risk is now
**verified as null on the judged cuts** rather than left open. GT-8's `frame_budget` movement did
not name scene10 either (its landing record lists 08 · 19 · 15 · N1 · 05 for B2 and D2 for B5), and
nothing in this round contradicts that.

**This round, not `260730_w2d_fix`, is the rebuild's baseline**, and every regression figure in §6
names it (spec §6.4 trap 2 — never "the baseline" unqualified).

---

## 2. S3-8 — railing rebuilt in square sawn timber (GT-20)

§4.2-2 calls this the highest-value single change in the scene, and the render agrees: the
before/after at `preset_h0.9_d5` is the difference between a steel-looking balustrade and a Korean
park deck.

| member | before | after | basis |
|---|---|---|---|
| newel | Ø150 `CYL`, no cap | **90 × 90**, cap **120 × 120 × 45**, projecting **0.150 m** | stocked 90각, research §D2 |
| line post | Ø100 round | **90 × 90**, stopping under the top rail | same |
| top rail | Ø60 round | **38 × 140 laid flat** | stocked; "a hand rests on it" §2.A.1-3 |
| mid rail | Ø60 round | **38 × 89** at 0.50 h | |
| bottom rail | **absent** | **38 × 89** at 0.12 above the walk | present in most G10 bays |
| baluster | Ø44 @ 0.300 | **38 × 38 @ 0.150 horizontal**, clear **0.112** | §8.R OQ-5 |
| deck column | Ø150 round | **120 × 120** + 0.35 m algae collar at grounded feet | stocked 120각 |
| lattice bay | absent | **one**, on `EntryRail_P`, 0.12 pitch, 30 × 30 battens | E10-8 |
| rail height | 1.05 (centre) | **1.10 to the top face** | §8.R OQ-5 |

**Section discipline.** KFS-TRAIL's 2010 drawings dimension 80 × 80 and 100 × 100 방부각재; research
§D2 (five suppliers cross-checked, 2026) records those as **drawing sizes that are not Korean retail
stock** — Korean posts are metric-planed 90각 / 120각 / 140각 and the small sections are the
38-series. The build uses stock, and the self-check asserts every section against the stocked set,
so a later "tidy-up" to 100 × 100 fails visibly.

**Rail height — both authorities on the record** (GT-20's row carries the full text). Built reality:
KNPS-RAIL median **1.10 m**, **n = 1,227**, modes 1.00 (35.8 %) · 1.20 (19.9 %) · 1.10 (15.1 %), so
71 % of real Korean trail railings are 1.0–1.2 m. Code counterpoint: 조경설계기준 **16.20.2(2)** puts
a 관찰데크 at **≥1,200 mm** (a plain 산책로 안전난간 is ≥1,100 under 16.13.2(2)). Neither PIRAN-15
(85 cm, 건축물) nor HOUSE-18 (1.2 m, 주택단지) binds a trail deck and KCS 34 50 10 3.2.6 fixes no
number, so **no statute binds this scene**; 1.10 m is taken on built reality per §8.R OQ-5 and the
≥1.2 m clause is written into the ledger so a reviewer meets the divergence declared. The baluster
gap gets the same treatment: 조경설계기준 16.13.2(3) is 안목 ≤100 mm **with a 단서 of ≤150 mm for a
계단중간 난간**, and 0.112 m sits inside the 단서.

**Balusters stay plumb** — KCS 34 50 10 3.2.6(3), *"비탈면에 설치되는 계단난간의 세로부재는 계단면에
수직"*. The scene was already compliant; what changed is that the pitch is now measured
**horizontally** on level and raking runs alike, so the clear gap is one number (0.112) everywhere
instead of shrinking by cos(pitch) on the flights. Recorded so nobody "fixes" it to a raked baluster.

### 2.1 `sc.build_railing_line` is no longer called — and why that is the stronger guard

The lane brief says to keep `baluster_r=0.0` at `scene10:1207`, the flag that stops the shared
builder duplicating this scene's own balusters (the red team found **48 interpenetrating pairs**).
`build_railing_line` emits `add_cylinder` posts and rails by construction, so it cannot coexist with
S3-8's square-section mandate, and editing it is a `scene_common` change this lane may not make
(§12-H15, and the one authorised micro-commit was K4M's).

**Resolution, stated rather than assumed**: the call is removed. The guard is preserved by **path
removal** instead of by a flag — there is no shared-baluster code path left to switch on, which is
strictly stronger than `baluster_r=0.0`. The scene-local raking builder uses `sc.build_slope`
(a rotate-Y box) for the three rails and plain boxes for the plumb balusters. The self-check prints
`난간 원형부재 수 = 0` so a regression is visible without a render.

### 2.2 Timber patina — aimed at the measured target, then corrected once by the reference

`wood_dark_diff.jpg` measures mean linear **(0.0824, 0.0584, 0.0442)**, Y 0.0625, **L\* 30.0**
`[measured]`. With the shipped tints that produced L\* 30.2 (deck) and L\* 26.2 (frame) — §4.2-3's
"reads near-black in shadow" defect, in numbers.

Target = the **measured** 2–5 year 방부목 patina (research §D4/D5, CIELAB from *Forests* 9(8) 488 and
*Wood Research* 62(5) 737): **L\* 53–60, a\* 0…+2, b\* +4…+10, albedo 0.22–0.28, #86837C–#96938B**.
Fresh ACQ starts *dark* (L\* ≈ 46) with a\* only +3…+5 — the "green" read is low lightness plus
moderate yellow, not negative a\*, so no green was painted on.

The band centre (#8E8B84, L\* 57.9) was built and rendered first; against G10 it read a shade
bleached under this scene's 49.8° noon sun, so the walked deck was moved to the band's lower half,
**L\* 55.0 (#86847D)**, one step off the band floor, with the frame timber at the floor itself
(**L\* 53.0**) because G10 reads silvered top faces over darker vertical faces. **Both stay inside
the measured band — the reference moved the value within the standard, it did not overrule it.**

Tints are therefore derived, not chosen: `tint = target / source`, giving deck **(2.91, 3.92, 4.64)**
and frame **(2.67, 3.60, 4.30)**. The map is dark and low-contrast (p95 linear 0.122), so even at
4.6× the clipped fraction is **0.02 %** `[measured]` — **the existing map carries the target without
procurement**, so §8.R OQ-8's G5 test ("only if that visibly fails") is not met and **no CC0
weathered-plank procurement attempt was made**. G5 stays an open row, unblocked and unspent.

---

## 3. S3-9 — stair re-table (GT-18)

**The honest headline first: the old riser/tread was never the defect.** 2R + T = 2(0.165) + 0.300 =
**0.630** is inside KCS 34 50 10 3.2.8(3)'s 600–650 window and 〈표 13-1〉's 30° row is 170/300, so
the intake's "an interior ratio, not an outdoor one" is refuted. This commit is a *fidelity* change.
The real compliance failures were the **width** and the **landing**.

**Three identities, re-derived by the self-check and never retyped**:

```
44 × 0.150 = 6.600 m exactly          (total drop frozen, §9 P-2)
8 + 7 + 8 + 7 + 7 + 7 = 44
2R + T = 2(0.150) + 0.310 = 0.610 ∈ [0.600, 0.650]     [law] KCS 34 50 10 3.2.8(3)
```

The same clause requires the ratio be **uniform over the whole run**, so only the *step count* varies
between flights — riser and tread are single scene constants and the self-check says so.

| row | before | after | authority |
|---|---|---|---|
| clear width | 1.38 | **1.500 m** | `[law]` 산지관리법 시행령 별표 3의3 제4호 다 caps 숲길 at 1.5 m; `[data]` KNPS-STAIR 데크 subset n = 155, median 1.50, **1.50 = 47.7 %** vs 1.80 = 9.0 % — the intake's "typical 1.8" is corrected |
| landing | 1.40 × 2.80 | **1.50 (travel) × 3.20 (across)** | `[law]` 조경설계기준 5.10.2(3) 참 ≥ the stair's 유효폭 **and** ≥1,200 mm, 5.9(4) 1.5 × 1.5 — **the old 1.40 failed it** |
| rest platform | absent | **1**, 3.00 deep at z −3.450, with a bench | C5; `[law]` SANJI-183 단서 2) 휴식·대피 장소 is the only licence to exceed the width |
| landing pitch | — | max **1.200 m** of rise between level surfaces | `[law]` 조경설계기준 5.10.2(3)'s 2 m rule. The 건축법 3 m rule (PIRAN-15 제15조) is **not cited**: it binds 건축물 only and the landscape rule is stricter |
| tread plate | 0.050 | **0.025** = a stocked 25 × 140 데크판재 | `[law]` 산림청고시 2014-2 제8조 thickness series 21+/3 mm, width series 90–300/10 mm; `[data]` §D2 stock 21×120 · 25×140 · 27×140 |
| plank field width | kit default 0.145 | **stated 0.140** | 0.145 is the KCS *specification* width, not a stocked one |

**Railing offset, a consequence worth naming.** The railing was moved **outboard** of the deck edge
by half a baluster so the clear width between the two railings is exactly 1.500 m. A railing set
inboard, as the old one was, quietly eats ~120 mm off the statutory 너비. Band pitch went 0.70 →
0.85 so the inner newels of two adjacent flights clear each other by 0.072 m.

**Hazard cue (3) is re-derived, not re-typed**: the leaf band still bites treads 1 · 2 of flight 0,
now at tops **−0.145 / −0.295**. The last landing's proud over the lower path re-verifies at
**+0.020 m**, inside `0 < proud ≤ 0.05`.

**Declared intermediate defect**: at this commit the flights were still stacked two-deep, so the
vertical clearance fell to 2 × 1.05 − 0.29 = **1.81 m**, below the 2.0 m the SMOKE table wants. S3-10
removes the stacking entirely and with it the question. It is on the record rather than discovered.

---

## 4. S3-10 — de-stacking, Option A (GT-19)

### 4.1 The 180° reversal had to go, and the reason is arithmetic

§8.R OQ-6 rules Option A. **A pure 180° reversal in two Y bands provably cannot de-stack**: flight
*k*+2 always returns to flight *k*'s footprint, because the odd flight runs back the way the even one
came. The scene's own v5 docstring states the same fact from the other side —
*"A pure switchback makes no horizontal progress … the ground along the stair must therefore be
effectively vertical"* — which is exactly why the ground under it was a masonry shaft. **That
sentence is the diagnosis, not the design.**

What is built is G10's actual form (§2.A.1-6/7): **every flight descends +X, each landing turns the
run 90° and hands it to the other Y band, and the assembly traverses the slope.**

```
f0 x[ 0.00,  2.48] band −Y      L0 x[ 2.48,  3.98]  z −1.200
f1 x[ 3.98,  6.15] band +Y      L1 x[ 6.15,  7.65]  z −2.250
f2 x[ 7.65, 10.13] band −Y      L2 x[10.13, 13.13]  z −3.450   ← 쉼터/전망, 3.00 deep, bench
f3 x[13.13, 15.30] band +Y      L3 x[15.30, 16.80]  z −4.500
f4 x[16.80, 18.97] band −Y      L4 x[18.97, 20.47]  z −5.550
f5 x[20.47, 22.64] band +Y      L5 x[22.64, 24.14]  z −6.600   ← ground arrival
```

**Flight-to-flight plan overlap 0.000000 m² · flight-to-landing overlap 0.000000 m²**, both asserted
by `deck_module_selfcheck` — C1 is the scene's headline defect, so the property is asserted rather
than budgeted; without an assertion the next coordinate edit puts a flight back over another and
nothing notices.

### 4.2 Divergence from the spec's plan estimate, with its arithmetic

§4.2-4A estimates *roughly* `x[−1.5, 12] × y[−2.6, 1.6]`. The built plan is
**x[−1.50, 24.14] × y[−1.60, 3.10]**.

```
Σ runs 13.64  +  4 turn landings × 1.50  +  rest platform 3.00  +  arrival landing 1.50  =  24.14
```

The estimate counted Σruns only and omitted the X the landings consume. **That consumption is not
removable.** Pushing the landings sideways into the neighbouring band instead makes net progress
`run − 1.50 = 0.67 m` per **1.05 m** of drop — a **157 %** ground slope, i.e. vertical ground, i.e.
the shaft again. Growing the plan is what Option A *is*. For scale, KNPS-STAIR's 데크 subset has
median run length 16.0 m and p75 28 m, so a 24 m traversing deck stair is ordinary built reality,
not an outlier.

### 4.3 The masonry shaft is gone; the ground is a real slope

Deleted: `BankCut` (a 7.40 m single wall over the whole deck run), `EastTierLow`, `EastTierUp`, all
three `copings`, and the `berm_hedges`/`berm` planting band (§2.B-2 C15/C16). **0 masonry plates
remain over the deck run.** What survives is the **short head wall** — `UpperBody`'s exposed face at
x = −1.5, now **0.255 m** tall instead of 6.62 m.

In their place, 15 `CorridorSlope_i` slabs on `GROUND_LINE`, spanning y[−2.60, 8.00]:

* mean longitudinal grade **25.8 %**, steepest segment **48.4 %** (the flight's own grade),
  **level benches under every landing** — a cut-and-fill trail bench;
* air gap under the deck **0.020 – 0.600 m**, all positive, with the **stair foot at 0.250 m ≤ 0.300 m**
  — `[law]` KFS-TRAIL 특별시방서 12-3 마, *"계단하단부와 지반과의 높이차가 30cm 이상으로 올라가지
  않도록 시공"*. The rest platform, which is not a stair foot, is allowed its 0.600 m and reads as a
  projecting 전망대.

A straight ground ramp was tried first and rejected on measurement: the deck falls at 48 % on a
flight and 0 % on a landing while a straight ground falls at the 25.8 % mean, so the deck dives
**0.085 m below grade** at the first flight foot. The bench profile is the only one that holds the
gap.

`ground_z(x, y)` now returns `corridor_z(x)` inside the corridor band, so **every dressing seat z is
re-derived** (`_zone_z`, `north_z`'s pivot 2.60 → 8.00, and `post_segments`' footings — every deck
column founds on the sloped ground instead of on a landing below it).

**All five mise-en-scène cuts are now derived from the ladder rather than typed as literals.**
Landing 0 moved from x[3.0, 4.4] z −1.65 to x[2.48, 3.98] z −1.20; a literal eye/target would have
drifted silently off its subject, which is precisely the failure mode §6.4 warns about. All five
re-check front-lit in SMOKE (lambert +0.41 … +0.62) with their park anchors in frame.

### 4.4 A defect the pilot found, and the fix

The first `260731_w3_s10` render showed a **4.8 m see-through band** in `from_below`: the corridor
slab was only 1.60 m thick, so between its underside at the head (−1.855) and the lower park top
(−6.62) the hillside was hollow and the camera looked straight through it to the sky. Thickness
1.60 → **7.00** (the highest corridor top is −0.255, so 7.00 clears −6.62 with margin). Committed
separately as `e3619df` and the pilot re-rendered. A residual sliver remains at one segment junction
on the right of `from_below`; it is small, it is recorded here, and it is a wedge-junction artefact
rather than a hole through the terrain.

---

## 5. S3-11 — season re-bind, 만추 leaf-off (GT-21)

**The census this closes** `[measured]`: 12 trail trees + 12 hill trees + 13 shrub clumps =
**37 green plants**, plus 10 green hedge/crest bands, against 4 brown leaf lobes. G10 carries **zero**
green vegetation objects and wall-to-wall litter.

| element | result |
|---|---|
| trail trees | **12/12 leaf-off**, `Gray_Birch` · `Elm_Sapling` · `Lombardy_Poplar` rotated |
| hill / ridge belt | **12/12 pinned to `Chinese_Juniper`** |
| shrub clumps | **13/13** real `Burning_Bush` / `Juniper` USDs |
| litter | **780** scattered instances, seated by `ground_fn` on the 25.8 % slope |
| rock outcrop | **4** — `rock_moss_set_01` + 2 × `rock_03_broken` + `rock_02`, `z_mode='base'`, **sink 0** |
| distant city | **3** windowless silhouette masses, nearest **d_true 81.4 m** from the judged eyes |

**The K4M contingency did not fire.** `w3_k4micro_v1.md` reports the leaf-off mechanism landed with
a 33/33 prim-hash proof, so the opt-in was taken. But `build_tree(bare=True)` **alone is not enough,
and its own docstring says so**: the species is drawn by coordinate hash from `VEG_TREES` and only
`Elm_Sapling` of the three bare-capable assets is in that pool, so `bare=True` yields a *mixed*
frame. The planned K4(b) `species=` kwarg was never executed. The scene therefore takes the route the
docstring names and calls `sc.add_vegetation` itself, deactivating `/Root/leaves` **before**
`SetInstanceable(True)` — once a prim is instanced its descendants live in a shared prototype and
per-instance edits are silently ignored.

**Oaks re-assigned per §4.2-5.** Their leaves ride inside branch `PointInstancer`s and cannot be
stripped. The far belt takes `Chinese_Juniper` instead: an evergreen keeps its needles in 만추, so a
green mass at distance is a conifer, not a season error. Side effect, and it is the lane's largest
lint movement: **LINT-4b 9 ERROR → 0**, because the coordinate-hash draw was producing retired
species (`White_Pine` ×5 with an uncorrected `zmin −0.351`, `Yellow_Pine` ×4).

**Trees are still placed at `<prefix>/Veg`.** `placement_lint`'s tree rule is
`pattern: '/Veg$'` with `species_from: '<self>/Asset'`. Referencing the asset directly under
`Tree_n` made all 24 plantings invisible to LINT-1/2/3 and to the LINT-4b species gate — the numbers
improved by **dropping out of the check**, which is the wrong kind of green. The convention is kept
and the inventory reports `tree=24` again.

### 5.1 Correction to the spec's dormant-grass tint, recorded rather than silently applied

§4.2-5 gives the dormant grass tint as the literal **(0.62, 0.60, 0.42)** `[assumed]`. A tint is a
**multiplier, not a colour**, and `grass_lawn_diff` measures mean linear **(0.0621, 0.1115, 0.0232)**
`[measured]`. That triple therefore yields (0.0385, 0.0669, 0.0097) — **R/G = 0.58, still
green-dominant.** It darkens the lawn without dormanting it.

Shipped instead, derived from a straw target: **(3.40, 1.55, 3.30)** → **#7F734E**, linear
(0.211, 0.173, 0.077), Y 0.174, **L\* 48.8**, **R/G 1.22**, inside the project's ≤0.30 ground albedo
clamp, clipped fraction **0.02 %**. Same arithmetic for the hedge and crest bands (#6C6244). The
self-check asserts the **product**, not the triple, so the check cannot be satisfied by a
plausible-looking number.

This is the cherry-blossom ruling applied again: *judge by pixels, not by the value's name.*

### 5.2 A runtime defect in the T2 rock scans, measured and worked around

The rock outcrop first rendered as **flat saturated red masses**. Cause, from the render log: the T2
scans bind `assets/urban/nv_core/materials/SimPBR.mdl`, and that module fails to compile in this
runtime — `C120 could not find module '.::baking_annotations'` — so the meshes fall back to the
shader default. Binding the scene's rock material on the Xform **above** `/Asset` with
`strongerThanDescendants` (the device `scatter_debris(mtl=…)` uses) **did not reach inside the
prototype** — re-measured on a second probe. The fix is `instanceable=False` plus a **per-mesh**
bind, which is what `urban_kit._bind_far_override` itself does. Four placements, so nothing is lost
by not sharing a prototype. This is a finding about the T2 pool, not about scene10, and it is the
first time any scene in the tree has referenced an urban asset outside `batch1_common.py`.

**F2 discipline held**: `sink = 0`, `z_mode='base'`, asserted. `tonglam_v2` §1 row 10 already failed
this scene once for *"boulder-scale D-5 rocks in dark sink-rings"*; a boulder in a hole is the defect
and a boulder on the slope is the fix.

### 5.3 The distant city glimpse — BS-4 contract met as a product, not as a call

The three masses honour `building_kit`'s BS-4 backdrop contract — **distant silhouette only, 0
windows, ≤4 prims per mass, beyond the `d_true > 80 m` auto-demote** — but are built scene-side as
plain windowless boxes. **No scene in the tree calls `building_kit`** (K3 owns it), and wiring a
shared kit from an S-lane would create a dependency this lane cannot verify. The product is the same:
"faint" is exactly what 0 windows and 3 prims mean.

---

## 6. GATE-1 pilot P10

**Round `260731_w3_s10`** — `look_check/scene10/260731_w3_s10/`, `git_head e3619df`, **14 cuts**:
the full 9-cut preset prefix (order-prefix rule §4.4 X1 — PT/DLSS accumulation carries frame history,
so the whole prefix is rendered and the extras kept) plus `reversal` · `through_treads` ·
`broken_rail` · `leaf_edge` · `from_below`. Channel identical to the frozen judge round:
`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 ·
NEGOBS_DETAIL_ROUGH_GAIN=0`. Every render segment ran inside `flock -w 7200 /tmp/negobs_gpu.lock`,
sequential, one process. The stamp records `baseline_of_record: true` and names the comparison
baseline.

### 6.1 Regression vs **`260731_w3_pre10`** (this scene's own intermediate round)

`Docs/reports/regr_260731_w3_s10.json`.

| cut | verdict | DARK | BLOWN / WHITE | OCCL new-dark / blob | FRAME blocks |
|---|---|---|---|---|---|
| `preset_h0.3_d2` | FAIL | dark% 8.4 → **0.7** | — | 0.1 / 0.0 | 49 % |
| `preset_h0.3_d5` | FAIL | 4.9 → **1.4** | — | 0.3 / 0.1 | 60 % |
| `preset_h0.3_d10` | FAIL | 3.0 → **1.2** | — | 0.3 / 0.0 | 44 % |
| `preset_h0.9_d2` | FAIL | 13.2 → **3.3** | — | **2.1 / 1.0** | 79 % |
| `preset_h0.9_d5` | FAIL | 7.0 → **2.1** | — | 0.8 / 0.1 | 88 % |

**Declared in advance** (§6.4): both rebuilds are *intended* to move every pixel of the stair, so
**FRAME deviation on every cut is the expected result, not a failure.** The gates that still mean
something:

* **DARK — improved on all five cuts**, 3.0–13.2 % → 0.7–3.3 %. The near-black timber is gone.
* **BLOWN / WHITE — 0 flags.** The regression checker's own WHITE gate did not fire on any cut.
* **OCCL — one flag**, `preset_h0.9_d2`, new dark 2.1 % with a 1.0 % largest blob. Attributable:
  that cut looks straight down the entry deck, and the +150 railing prims (capped newels, lattice
  bay, dense balusters) plus the bare-tree canopies cast shadow where there was open lawn. It is
  well inside the "declare it and re-stamp" class, and this round **is** the re-stamp (GT-18's R-3).
* **PHOTO** — luminance up on three cuts ("brightening, usually an improvement — confirm intent").
  Confirmed intent: the deck moved from L\* 30 to L\* 55 and the ground from lawn-green to straw.

### 6.2 `near_ground_stats` — B45/B30 band, `preset_h0.3_*`

| cut | sd | mean | flat% | σ_LF | **flat_gnd** | notes |
|---|---|---|---|---|---|---|
| `h0.3_d2` before → after | 24.8 → **36.7** | 106 → **181** | 4.04 → **2.81** | 3.03 → 2.94 | **3.5 → 0.4** | 2 new WARN, 1 cleared |
| `h0.3_d5` | 29.3 → 28.7 | 132 → 133 | 0.10 → 0.07 | 4.01 → 3.88 | 0.1 → **0.0** | — |
| `h0.3_d10` | 23.4 → 23.0 | 135 → 136 | 0.00 | 2.52 → 2.49 | 0.7 → **0.0** | — |

**Cleared**: `flat_gnd` **3.5 → 0.4** on `h0.3_d2` (the ≥3 WARN is gone) and 0.7 / 0.1 → 0.0 on the
other two — the flat-ground defect the T0 spike identified as the real lever is now absent on all
three h0.3 cuts. `sd` on `h0.3_d2` also crosses its 32 threshold (24.8 → 36.7).

**New, and declared rather than tuned away**: `h0.3_d2` reports `mean 181 > 170` and `wht% 7.6 ≥ 2`.
Cause is understood — at 2 m the near band is filled by the **deck**, not by ground, and the deck is
now at its measured patina albedo (0.230) under a 49.8° noon sun. The band gates are WARN-only (the
tool's exit code is always 0) and the render-gate's own WHITE check did not fire. Moving the timber
off the measured 53–60 band to satisfy a ground-band heuristic would be aiming at the instrument
instead of the standard, so it was not done. **Available lever if 통람 v3 flags it**: drop the deck
to the band floor (L\* 53.0, tint (2.67, 3.60, 4.30)) — a ~7 % reduction, still inside the measured
band, one line.

### 6.3 h0.3 crops against G10

`Docs/reports/_w3_s10_crops/` holds the three h0.3 crops and the matching crop of G10.

**Reads that now agree with the reference**: square capped newels with the cap projecting above the
rail · a wide flat top rail with mid and bottom rails · dense square balusters · one lattice infill
bay · silvered grey-brown timber with darker vertical faces · dormant straw ground with brown litter
· leafless deciduous trunks with fine twig structure · a traversing run that steps sideways as it
descends, with daylight under it · rock outcrop on the uphill margin.

**Reads that still diverge, stated**:

1. **Open risers, by ruling.** G10 shows closed riser boards; this scene keeps open risers per
   §8.R OQ-2. Hazard cue (2) and the whole `through_treads` cut are research design, not looks.
   Named again in §7.
2. **The near band is deck, not litter.** At `h0.3_d2` the frame is the entry deck; G10's equivalent
   is also decking, but the reference is overcast and this scene is a hard noon sun, so the tonal
   spread differs even though the albedos agree.
3. **The hedge and crest bands** still read as a row of smooth domes at distance (the v6 C-4 device
   that cured a straight-horizon "stage backdrop"). H12 forbids deleting a working v6/v7 fix on the
   strength of one reference frame, so they were re-tinted dormant and otherwise left alone.
4. **Litter density on the open corridor** is continuous but thinner than G10's matted blanket at
   mid distance. The lever is `season.litter_cover` / `litter_max`; raising it is cheap and was left
   at 0.34 / 260-per-region so the first judged round is not over-dressed.

---

## 7. Constraints held, and the divergences declared

| # | constraint | status |
|---|---|---|
| **H1** | no humans, no vehicles, any cut, any distance | **held** — nothing placed; G10 has no figure anyway |
| **H3** | tactile stays default-OFF | **held** — `cue_tactile=False`, untouched |
| **H4** | do not undo CB-2 | **held** — the 4 `build_carpet_mask` lobes are kept as the dense litter cores; continuity comes from scatter around them, not from more lobes, and no lobe became a rectangle |
| **H5** | rebuilt in place, no new scene | **held** |
| **H6** | total drop frozen 6.600 | **held and asserted** — `44 × 0.150 = 6.600` exactly |
| **H7** | `rail.broken_landing = 0` survives | **held and asserted** — one broken run, `LandRail_0_Out`, rails and balusters gone, posts and newels remain |
| **H9** | no seasonal / event-specific element | **held** — 만추 pin; the early-spring signals G10 also shows (green leaf flush, green ground shoots) are **excluded**; no flowering shrub in the pool |
| **H10** | `sct_debris_leaves_dry_*` legal in 10 | **not used** — the continuous cover is `VEG_DEBRIS` scatter; the near-field hero patches are an available follow-up |
| **H11** | banned ids | **held** — no banned substring placed; `_check_banned()` not routed around |
| **H12** | do not delete a working v6/v7 fix | **held** — `SUN_AZ_OFFSET = 216.5`, the waymarker, the bench, the pergola and the crest-band horizon closure all survive; the crest bands were re-tinted, not removed |
| **H14** | do not re-litigate the D-5 rock prop | **held** — placement only (`sink 0`, no dark sink-rings) |
| **H15** | signature-preserving only in shared builders | **held** — **no shared module touched**; the lane's one shared-module need (square railings) was solved scene-side |
| **§8.R scope guard** | only scene07/scene10 files may change | **held** — S3-1 (sceneC2 hygiene) not touched |

**The one ruled divergence from the target image, stated in both the report and the S3-8 commit
message as required**: G10 reads **closed riser boards**; scene10 **keeps its open risers**
(§8.R OQ-2). The docstring hazard cue and the `through_treads` cut are research design, not looks,
and the emergency-stair read is cured by the railing, the de-stacking and the season instead. If the
user later orders riser boards that is an **additive follow-up, not a rework**.

---

## 8. GT ledger

Rows **GT-18 / GT-19 / GT-20 / GT-21** appended to `Docs/audit_v4/gt_changes_w3.md` §3, each in its
own commit **before** the scene commit it governs (§0-1). GT-18 carries the full re-cache
(R-1 + R-2 + R-3) and GT-19/20/21 declare that they ride it (§0-2, one re-cache per scene per batch).

**R-1 and R-3 are satisfied in this lane**: the self-check re-derives and prints the registry
(`deck_module_selfcheck`, four blocks), and this round is stamped as the new baseline-of-record so
the OCCL/GRAZE baseline is re-stamped. **R-2 — the mini data render — is not run here.** Per §0-3
the ledger records the command actually used, and `scripts/run_data_render.py` is the data owner's
invocation; the landing records state R-2 as **owed** rather than guessing at it.

---

## 9. Open items handed on

1. **R-2 (mini data render) owed** for GT-18's full re-cache —
   `python3 scripts/run_data_render.py --run <id> --scenes scene10` then
   `scripts/check_data_run.py`. Not this lane's to invent (§0-3).
2. **G5 procurement row stays open and unspent** — the measured target was reached on the existing
   map with 0.02 % clipping, so §8.R OQ-8's "only if that visibly fails" condition was never met.
3. **`h0.3_d2` band WARNs** (mean 181, wht% 7.6). Lever documented in §6.2 if 통람 v3 asks.
4. **T2 rock scans bind an uncompilable `SimPBR.mdl`** in this runtime. scene10 works around it
   per-mesh; **any other scene that references a T2 asset will hit the same fallback.** Worth a
   T4/procurement row.
5. **`from_below` wedge-junction sliver** at one corridor segment boundary (§4.4).
6. **PLACEMENT block** still absent for scene10 (LINT-1/2/3/7 report `nodata`). §6.6 says both
   scenes need one and that it is additive and geometry-free; it was left out of this batch to keep
   the four rebuild commits attributable. WARN count is unchanged from the baseline.
7. **Litter density and `sct_debris_leaves_dry_*` hero patches** — cheap dressing levers if the
   first judged round reads thin (§6.3-4).
