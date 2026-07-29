# scene15 railing realism fix v1 — the alley stair had a code guardrail it never needed

- Written 2026-07-30 · branch `feat/realism-v1`
- Owned files: `scenes/main/scene15_alley_labyrinth.py` (§0–§7) and, after the §6 flags were assigned
  back, `scenes/main/scene02_underpass.py` + `scenes/main/scene16_canopy_shadow.py` (**§8**).
- **No GPU / no render / no SMOKE run.** Self-verification is byte-compile + `ground_kit.py` self-check +
  `scripts/geom_invariance_check.py` (fake-USD, GPU 0). The visual verdict rides the upcoming
  **33-scene W2-D round** — this fix is queued for it, not judged here (§5.4).
- No git commit. No other scene file touched (W2-D editors hold them).
- Trigger: user finding, validated by the supervisor — scene15 is a Korean hillside alley stair maze
  carrying a code-standard freestanding guardrail (top + mid rail, posts @1.1 m, 3 rail lines).
- Evidence tags: `[measured]` = read out of the code/AST · `[computed]` = derived arithmetic ·
  `[survey]` = photograph tally below · `[statute]` = primary legal text · `[estimate]` · `[no source]`.

---

## 0. Verdict in one line

The corridor is walled on **both sides for the entire 4.25 m descent**, so no side was ever open to the
drop; the statute answers that geometry with a **handrail**, not a guardrail; and 12 photographs of
Korean hillside alley stairs contain **zero** two-sided code guardrails. The guardrail was deleted
(116 prims → 0), `cue_railing` now defaults **False** (bare stair, walls guard), and the ON state
builds one wall-bracketed φ34 pipe handrail over the upper flight only.

---

## 1. Evidence pass — photograph tally `[survey]`

N = 12 stair photographs of Korean hillside/alley stairs (달동네 · 골목 계단 · 산복도로), each viewed
directly, plus 8 non-stair alley photographs as context. No images were copied into the repo.

### 1.1 Tally

| Bucket | Count | % |
|---|---|---|
| NONE — no rail; flanking walls / retaining walls are the guard | 1 | 8 % |
| WALL_PIPE — single pipe bracketed to the flanking wall | **0** | **0 %** |
| POST_RAIL_MINIMAL — minimal rail on slim posts (one-sided or centre) | 11 | 92 % |
| **FREESTANDING_CODE — two-sided guardrail, top + mid rail, posts ~1.1 m** | **0** | **0 %** |

Sub-breakdown of the 11 POST_RAIL_MINIMAL:

| Form | Count |
|---|---|
| Single pipe line, no infill — one edge **or down the centre of the flight** | 5 |
| One-sided, top + mid rail or balusters | 6 |
| **Railed on both flanks simultaneously** | **0** |

**Two zeros carry this report.** Zero two-sided code guardrails, and zero stairs railed on both flanks.
The rail, when present, is *always* one-sided or a single centre pipe.

### 1.2 Per-photo list

Tourist-renovated villages (openly licensed, Wikimedia Commons):

| # | URL | Location | Bucket | Note |
|---|---|---|---|---|
| S1 | `commons.wikimedia.org/wiki/File:Stairs_in_the_Gamcheon_Culture_Village_1.jpg` | Gamcheon, Busan | POST_RAIL_MINIMAL | Left side only, top + lower rail on posts, low. Wall-flanked both sides. CC BY-SA 4.0 |
| S2 | `commons.wikimedia.org/wiki/File:Stairs_in_the_Gamcheon_Culture_Village_2.jpg` | Gamcheon, Busan | POST_RAIL_MINIMAL | Right side only, above a retaining wall; left flank is bare brick house wall |
| S3 | `commons.wikimedia.org/wiki/File:Stairway_at_Huinnyeoul_Culture_Village_in_Busan,_South_Korea.jpg` | Huinnyeoul, Yeongdo | **NONE** | Painted concrete retaining walls both sides act as the guard. Renovated *and still no rail* |
| S4 | `commons.wikimedia.org/wiki/File:Korea-Seoul-Ihwa_Mural_Village-P1210581.jpg` | Ihwa-dong, Seoul | POST_RAIL_MINIMAL | Single slim pipe on low posts, left only; walls both sides |

Ordinary / un-renovated hillside alleys (news photography — **copyrighted, cite-and-link only, do not reuse**):

| # | URL | Location | Bucket | Note |
|---|---|---|---|---|
| S5 | `ojsfile.ohmynews.com/STD_IMG_FILE/2025/1203/IE003556118_STD.jpg` | Seo-dong "Sanmandi", Busan | POST_RAIL_MINIMAL *(moderate confidence)* | Single thin line up one side of a long steep flight; tight wall-flanking both sides |
| S6 | `ojsfile.ohmynews.com/STD_IMG_FILE/2025/1203/IE003556120_STD.jpg` | Busan 산복도로 | POST_RAIL_MINIMAL | One-sided stainless, top + mid + balusters, on the retaining-wall side only; house side bare |
| S7 | `ojsfile.ohmynews.com/STD_IMG_FILE/2025/1203/IE003556109_STD.jpg` | Sujeong-dong, Busan | POST_RAIL_MINIMAL | Thin posts + **wire-mesh infill**, visibly aged and leaning. One-sided |
| S8 | `ojsfile.ohmynews.com/STD_IMG_FILE/2025/1203/IE003556113_STD.jpg` | Sujeong-dong, Busan | POST_RAIL_MINIMAL | One-sided stainless on the drop side |
| S9 | `busan.com/nas/wcms/wcms_data/photos/2022/09/13/2022091310424259724_l.jpg` | Choryang 180 stairs | POST_RAIL_MINIMAL | Right side only, on a low concrete curb; left is wall, no rail |
| S10 | `busan.com/nas/wcms/wcms_data/photos/2022/09/13/2022091310443886466_l.jpg` | Choryang 180 stairs | POST_RAIL_MINIMAL | **Single centre pipe**, no infill; walls both sides |
| S11 | `busan.com/nas/wcms/wcms_data/photos/2022/09/13/2022091310452835351_l.jpg` | Choryang 180 stairs | POST_RAIL_MINIMAL | **Single centre pipe** ~0.85 m splitting the flight; walls both sides |
| S12 | `img.seoul.co.kr/img/upload/2026/02/25/SSC_20260225180744_O2.jpg` | Daejeon Dong-gu 달동네 | POST_RAIL_MINIMAL | Single pipe on posts, one side; chain-link boundary fence opposite |

Context set — 8 non-stair alley photographs (Gamcheon backstreet, Bongnae-dong, Gamcheon-dong,
Daedong Mural Village, Ihwa 24, Haebangchon Itaewon-ro 23-gil, Dongpirang 11). **Five were NONE** —
flanking walls only. The three with rails all had them **one-sided on a drop edge**, never on the wall side.

### 1.3 Sampling bias — and it cuts against the tally's own NONE count

1. Tourist villages over-represent rails, as expected — but weakly: Huinnyeoul (S3), fully renovated,
   still has no stair rail at all.
2. **The larger bias runs the other way.** The "ordinary alley" photographs come from news articles
   *about stair-safety retrofit programmes*, so they structurally over-sample stairs that have just
   received a rail. Busan Ilbo states the baseline outright: **"아직도 계단 손잡이가 없는 골목이 많아"**
   ("many alleys still have no stair handrail"), reporting a **147-location** priority retrofit list —
   a list that only exists because the untreated baseline is bare.
3. Therefore **NONE is under-counted at 8 %.** For an un-renovated 달동네 maze, NONE and single-pipe
   are the two realistic states.
4. Wikimedia Commons is a weak corpus here — it skews to panoramas and mural tourism, and its
   Korean-language index returned zero hits for 계단/골목.

### 1.4 Handrail specification

**Statute** `[statute]` — 건축물의 피난·방화구조 등의 기준에 관한 규칙 제15조 (law.go.kr):

- **§15(3)** — "양쪽에 벽 등이 있어 난간이 없는 경우에는 **손잡이**를 설치하여야 한다."
  *Where walls on both sides mean there is no railing, a handrail must be installed.*
  **This is scene15's exact geometry, and the code's answer is a handrail — not a guardrail.**
  It is the single most decisive finding in this report and it was not in the original brief.
- **§15(4)** — diameter **32–38 mm**, circular/elliptical · **≥50 mm** clear of the wall ·
  **850 mm** above the stair · horizontal end extension **≥300 mm** past the end of the flight.
- 장애인·노인·임산부 등의 편의증진법 — single handrail 0.80–0.90 m; if doubled, upper ≈0.85 / lower ≈0.65;
  same 32–38 mm diameter and 50 mm wall gap.

**What is actually built** — the honest gap: code grip is 32–38 mm, but the stainless tube used in these
retrofits is commercial structural stock, commonly **42.4 mm STS304** (`drain.kr/pipe_sts1.php`,
`sudo.info/sts.htm`) — i.e. field installs routinely exceed the code grip dimension. `[estimate]` — no
authoritative municipal spec for alley-handrail retrofit bracket spacing or diameter was found
`[no source]`. Treat 42–48 mm as observation, not citation. The scene keeps **φ34** (code-valid); the
42.4 mm field figure is logged as a variation candidate in §6.

### 1.5 What could not be verified

- Mapillary / OpenStreetMap street-level imagery and Google Street View were not reachable with the
  available tooling; **no coordinates are cited**.
- S5's bucket is moderate confidence only (black-and-white, long lens, thin rail).
- `[unfetched]` — appeared in genuine search results, never retrieved: `namu.wiki/w/달동네`,
  `namu.wiki/w/산복도로`, `woodplanet.co.kr/news/view/1065539494940811`,
  `seouland.com/arti/culture/culture_general/3608.html`, `ajunews.com/view/20260610115302472`,
  `nld.go.kr/upload/contents02/seoul_menual(2016).pdf`, `balance.go.kr` 새뜰마을 pages.

---

## 2. What was there, and why it read artificial

### 2.1 The corridor is walled on both sides for the whole descent `[measured]`

| Run | x (world / bend-local) | North flank | South flank | Stair edge |
|---|---|---|---|---|
| Upper alley | −12.0 … 0.0 | retaining wall, inner face y = +0.90 | y = −0.90 | ±0.90 |
| flight1 | 0.0 … 3.6 | House[4] facade y = **+0.58** | House[6] y = **−0.58** | ±0.60 |
| Landing | 3.6 … 5.1 | House[5] y = +0.58 | House[7] y = −0.58 | ±0.60 |
| flight2 (rot_group local) | 5.1 … 9.0 | House[8] local y = +0.58 | House[10] local y = −0.58 | ±0.60 |
| Lower alley (local) | 9.0 … 13.1 | House[9] local y = +0.88 | House[11] local y = −0.88 | ±0.90 |

The house facades sit **20 mm *inside* the stair edge** for the entire run. **No side is ever open to
the 4.25 m drop.** So:

- **§15(1)2 (양옆 난간, required above a 1 m drop) is satisfied by "벽"** — the same reading that passed
  scene05's entry arc stair on its cheek walls (`Docs/reports/stair_compliance_v1.md` §1, row
  "scene05 앰피 진입 아크계단 … 적합, 양측 치크월이 §15①2 '벽'에 해당").
- **No guardrail was ever required anywhere in this scene**, and §15(3) says the part that *is* required
  is a handrail. The old A-15-5 fix answered the wrong question: it extended a guardrail along a
  corridor that never lacked a guard.

### 2.2 The old assembly, measured `[measured]`

`SCENE_CONFIG.cue_railing=True` built three `sc.build_railing_line` calls at `y_side = 0.55` — i.e.
**10 mm from the House[4] facade at y = 0.58** — one per flight:

| Subtree | Balusters | Guardrail posts | Rail segments | LOOK_GEO handrail | Total |
|---|---|---|---|---|---|
| `Rail1` (flight1) | 33 | 4 | 4 | 7 | 48 |
| `RailLanding` | 13 | 2 | 2 | 5 | 22 |
| `Bend/Rail2` (flight2) | 33 | 4 | 2 | 7 | 46 |
| **Total** | 79 | 10 | 8 | 19 | **116** |

**116 prims = 21.3 % of the scene's 545**, every one of them inside the 30 mm slot between y = 0.55 and
the wall at y = 0.58. Three rail lines per flight (top rail + mid rail + the LOOK_GEO handrail), posts
at 1.1 m, balusters at 0.116 m pitch. A statutory fall barrier bolted onto a wall it does not need to
protect, halving a 1.2 m alley stair.

### 2.3 Three concrete defects it was also hiding `[computed]`

1. **Coaxial duplicate posts / Z-fighting.** `build_railing_line` places guardrail posts from
   `x_start` at 1.1 m, and under LOOK_GEO it *additionally* calls `stair_kit.build_handrail` at the
   **same y = 0.55** with its own posts at 1.2 m and the **same `post_r = 0.02`**. On `Rail1` both
   sequences start at x = −0.3 → two identical-radius cylinders sharing an axis and a ground foot,
   heights 0.92 and 0.85 → coincident lateral surfaces over z 0…0.85. Recurs on `Bend/Rail2` at
   x = 8.4 (guardrail 5.1 + 3×1.1; handrail 4.8 + 3×1.2).
2. **A floating unsupported stub over the bend.** `RailLanding`'s handrail `ExtBot` runs world
   x 5.1…5.4 at y = 0.55, past the landing edge and into the **25°-rotated** flight2 region. The
   rotated House[8] facade at world x = 5.25 is at y = 0.710, so the stub hangs 0.16 m inside the
   corridor with no post or bracket anywhere near it (nearest handrail post is x = 4.5).
3. **The drop edge's own occluder.** The x = 0 drop edge — the one the whole scene is built to
   hide — carried a 33-baluster picket fence 50 mm to its side.

---

## 3. Redesign

### 3.1 Decision

| | Before | After |
|---|---|---|
| `cue_railing` default | `True` | **`False`** |
| OFF state | flat-control only | **bare stair; flanking walls are the guard** (§15(1)2 "벽") |
| ON state | 3 × freestanding code guardrail + 3 × coaxial handrail | **1 × wall-bracketed φ34 pipe handrail**, upper flight + landing only |
| Both flanks railed | yes (implicitly — a full barrier either side of a 1.2 m stair) | **never** |
| Lower flight (past the bend) | guardrail | **bare in both states** |

Default OFF is carried by four independent lines: the tally (0/12 code guardrails, NONE under-counted,
§1.3), the geometry (§2.1 — nothing to guard against), the statute (§15(1)2 satisfied by wall), and the
scene's own research identity — a 4.25 m drop hidden in a narrow frame should not be pre-announced by a
cue the real world does not install.

### 3.2 The ON state, and an honest gap

`PARAMS["rail"]` now drives `stair_kit.build_handrail` in wall-mounted mode:

| Key | Value | Basis |
|---|---|---|
| `wall_y` / `wall_side` | 0.58 / −1.0 | House[4]/[5] facade plane; corridor on the y < 0.58 side `[measured]` |
| `dia` | 0.034 | §15(4)1 φ32–38 `[statute]` |
| `height` | 0.85 | §15(4)2, above the nosing line `[statute]` |
| `wall_gap` | 0.050 | §15(4)2 `[statute]` |
| `bracket_spacing` / `bracket_r` | 1.20 / 0.011 | no clause regulates handrail support spacing `[no source]` |
| `ext_top` | **0.0** | forced — the flanking wall itself only starts at x = 0, so there is nothing to bracket to before the drop edge. Statutory minimum is 300 mm → **deliberate H3 shortfall** |
| `ext_bot` | 1.50 | runs flat over the landing x 3.6…5.1 on House[5]'s wall → H3 met at the bottom |
| `lower_flight` | `False` | the piecemeal resident install stops at the landing |

Built geometry, from the fake-USD inventory `[measured]`:

```
WallPipe/Slope    T=(1.800, 0.513, −0.170)  RY=119.539  h=4.1378  r=0.017
WallPipe/ExtBot   T=(4.350, 0.513, −1.190)  RY= 90.000  h=1.5000  r=0.017
WallPipe/Brk_0..4 x = 0.0 / 1.2 / 2.4 / 3.6 / 4.8, y = 0.5465, RX=90, h=0.067, r=0.011
```

Pipe axis y = 0.58 − (0.050 + 0.017) = **0.513**; surface spans y 0.496…0.530. All five brackets land on
solid wall (the house shells are solid down to the valley slab at z = −4.35, so the wall face exists at
every bracket z) `[computed]`. `strict=False`, so the one statutory shortfall is printed, never raised:

```
[cue_railing] 규정 미달(의도) — ext_top 0.000 m < 법정 수평 연장 0.30 m (피난방화 §15④3)
```

**The gap, stated plainly.** The tally found **0/12 wall-bracketed pipes in alleys** (§1.1). The
wall-bracket form is what §15(3)/(4) prescribes and what public-facility stairs use (scene02's underpass
comment already calls for it), but field alley retrofits use **slim posts** — plausibly because the
flanking walls are private houses `[estimate]`. The highest-fidelity option for this exact geometry is a
**single centre pipe** (S10/S11: Choryang 180 stairs — walls both sides, one pipe down the middle, two
independent photographs). It was rejected on one specific ground: a post line on **y = 0** is the camera
axis of every `grid_views` preset, so in a 1.2 m corridor it would stand in the middle of every h0.3
grazing frame — a live GRAZE-regression risk that cannot be assessed without a render. Logged as
reversible in §6.

### 3.3 Invariants held

- **GT.** A pipe above the treads creates no terrain z — `stair_kit.build_handrail`'s documented "drop
  label invariant". No `z(x,y)` in the scene changed; every stair, landing, wedge, alley and valley
  transform is byte-identical.
- **Grazing / drop-edge exposure.** The `ground_kit` wiring from the W2-B pilot (`cb40ae8`) is
  untouched: `edges=[("stair_top", PARAMS.flight1.x0)]`, `manhole_d5=(−2.40, −0.15)`,
  `patch_sites`, `gutter_y`, `grating_local`, `_edge_guard_ticks` dropping the x = 0 joint — all
  byte-identical, and `M["rail"]` is still created and still feeds `manhole` / `gutter` / `trench` /
  `trench_frame`. The change to the x = 0 edge is purely subtractive: it loses a 33-baluster occluder,
  so grazing exposure of the drop edge can only improve. **Directional claim, render-unverified.**
- **Cue toggle integrity.** `cue_railing` ON/OFF changes only `/World/Scene15/WallPipe/*`; no other
  prim, transform or extent moves (§5.2).

### 3.4 Known residual — the pipe passes two door bays `[computed]`

In the ON state the pipe crosses in front of two doorways. It never intersects them:

| Wall | Door frame x | Door frame z | Pipe z at those x | Frame outer face y | Clear |
|---|---|---|---|---|---|
| House[4] | 0.890 … 1.910 | −0.260 … 1.760 | +0.346 … −0.232 | 0.550 | **0.020 m** |
| House[5] | 3.440 … 4.460 | −1.960 … 0.060 | −1.099 … −1.190 | 0.550 | **0.020 m** |

All four window frames clear the pipe by more than 0.5 m. Kept deliberately: a wall handrail running
past a gate is ordinary in real alleys, and the 20 mm clear at those two bays is itself a genuine
§15(4)2 shortfall (statutory clear is 50 mm) — another "규정 미달의 현실" data point rather than a
modelling error. Bracket 0 sits exactly on House[4]'s west corner (x = 0.0) and overhangs the wall face
by its own radius, 11 mm.

---

## 4. Cue ledger — the P(낙차 | 난간) change

`Docs/surveys/cue_arrangement_survey.md` §4.1 counts scene15 in the **난간 있음 / 낙차 +** cell:

|  | 낙차 + | 낙차 − |
|---|---|---|
| 난간 있음 | 17 (01·02·06·08·10·11·12·13·**15**·16·19·20·21 · C1·C2·C4·D4) | 1 (N4) |

**P(낙차 | 난간) = 17/18 = 0.944** against a §2.5 target of 0.25–0.35 — the project's top validity risk.

**Change to book.** scene15's default render now shows **no railing at all**, and even in the ON state
what it shows is a §15(4) 손잡이 bracketed to a wall, not a §15(1)2 난간. Under either reading the scene
leaves the numerator:

| Reading | Numerator | Denominator | P(낙차 \| 난간) | Δ |
|---|---|---|---|---|
| Before | 17 | 18 | 0.9444 | — |
| **After (default OFF — book this)** | 16 | 17 | **0.9412** | −0.0032 |
| If the ON variant is rendered and counted as "any visible pipe" | 17 | 18 | 0.9444 | 0 |
| After the §8 scene02 + scene16 conversion as well | 16 | 17 | **0.9412** | 0 further |

> The last row is not a typo. scene02 and scene16 **keep** their pit perimeter guardrails, which are
> genuine 난간 and are those scenes' primary cue, so only their *stair* lines changed and neither scene
> leaves the numerator. The 15/16 figure anticipated when those scenes were assigned does not
> materialise — see §8.4.

**Do not oversell this.** −0.003 is a rounding error against a 0.25–0.35 target. The honest arithmetic
`[computed]`: with 28 drop scenes and 5 no-drop scenes, reaching P ≤ 0.35 needs `k/(k+5) ≤ 0.35`, i.e.
**k ≤ 2** — at most **two** of the 28 drop scenes may carry a visible railing. That is flatly impossible
for realism (footbridges, overpasses and sunken plazas must have railings, and this report's whole
argument is that railing presence must follow reality). **The scene-level target is unreachable by
construction.** It can only be met at the render-variation level — the `cue_railing` ON/OFF pairing
already named as option ⓐ in `Docs/briefs/ground_kit_spec_v1.md` M10, decoupled from scene count.

What this fix genuinely buys: (a) scene15 becomes a clean **cue− / label+** sample — a 4.25 m drop with
no cue, which is the quadrant the survey §4.1 measures at 25 % and wants held at 20–25 %; (b) the ON/OFF
pair is now a *realistic* pair, so the variation-level route in M10 is no longer building on a cue that
would never exist; (c) the survey's own priority 1 (add no-drop railings to N1·N2·N3·N5) is unaffected
and remains the larger lever — 17/22 = 0.773 on its own, 16/21 = 0.762 combined with this fix.

---

## 5. Self-verification

### 5.1 Gates

| Check | Command | Result |
|---|---|---|
| Byte-compile | `python3 -m py_compile scenes/main/scene15_alley_labyrinth.py` | **exit 0** |
| Lint | `python3 -m pyflakes scenes/main/scene15_alley_labyrinth.py` | 3 findings, **all pre-existing** (`sys`, `math`, local `H`) — none introduced |
| ground_kit self-check | `python3 ground_kit.py` | **exit 0** · 33/33 hard gates · "전 항목 통과" |
| Geometry invariance | `python3 scripts/geom_invariance_check.py` | **exit 0** · R-5 PASS · **R-4 33/33** · **R-6 33/33** |

### 5.2 Prim delta `[measured]`

| State | Prims | Hash | Rail prims |
|---|---|---|---|
| Before (`cue_railing=True`, code guardrail) | **545** | `02611f19` | 116 |
| After, default (`cue_railing=False`) | **429** | `e1e86da1` | **0** |
| After, `cue_railing=True` (wall pipe) | 436 | `8e08a5b5` | 7 |
| After, `hazard_stairs=False` control | 402 | `e585c2b0` | 0 |

**Δ = −116 prims (−21.3 %)** at the default; −109 with the cue ON. The cue toggle moves exactly 7 prims
and nothing else — ON and OFF differ only by `/World/Scene15/WallPipe/*`, confirming toggle integrity
(BANNER checklist item 4). The `hazard_stairs=False` control still assembles.

The three geom-invariance arms (`MTL=0`, `MTL=1`, `V1=1`) agree on `e1e86da1` for scene15 and on their
prior hashes for all other 32 scenes, which also confirms this edit touched nothing outside scene15
(`git diff --stat` = 1 file).

**Note for the baseline keeper:** `Docs/reports/geom_baseline_w2.json` still holds scene15 at
`02611f19`. That entry is now intentionally stale and needs a refresh to `e1e86da1` — not done here,
since the baseline file is shared and other scenes are under concurrent W2-D edit.

### 5.3 Statutory position after the fix

| Code | Rule | Before | After |
|---|---|---|---|
| R2 §15(1)2 | side railing above a 1 m drop | "P1 R2 편측 난간" in `stair_compliance_v1.md` | **satisfied by "벽"** — both flanks walled for the whole run (scene05 precedent) |
| §15(3) | both-sides-walled stair → handrail required | not implemented | **implemented** when `cue_railing=True`; deliberately absent when OFF |
| H1 §15(4)1 | φ32–38 | n/a | **met** (φ34) |
| H2 §15(4)2 | h 850, ≥50 mm wall clear | n/a | **met** at the wall; **20 mm at two door frames** (§3.4) |
| H3 §15(4)3 | end extension ≥300 mm | n/a | **top end 0 mm — deliberate shortfall**; bottom end 1500 mm met |

`stair_compliance_v1.md` records that a handrail is "**33씬 전부 미구현**". scene15's ON state is now the
**first** implemented 손잡이 in the corpus. That document's scene15 row and its §1 "손잡이 H1~H3" note
both need updating — **not done here** (file is shared; flagged in §6).

### 5.4 What is explicitly NOT verified

No render was run — no GPU, no SMOKE, per the task constraints. Unverified until the **33-scene W2-D
round** picks this up: the pipe's read at h0.3/d2–d10, whether the removed balusters change the GRAZE
band statistic at the x = 0 edge (predicted improvement, §3.3), and whether the φ34 pipe is even
resolvable at d10. The fix is queued for that round; it is not judged here.

---

## 6. Railing appropriateness across the other 32 scenes — assessment only, no edits

Method: `SCENE_CONFIG.cue_railing` + `PARAMS.rail/railing/guard` + `build_railing_line` call sites read
from each file, cross-checked against the `stair_compliance_v1.md` R2 column. Two archetypes:
**STD** = standard code guardrail is what the real place has (campus / plaza / station / bridge /
engineered deck) · **WEAK** = the real place has a minimal rail, a wall doing the guarding, or nothing
(temple / park trail / alley / riverbank / embankment / industrial).

### 6.1 Table

| Scene | Setting | Archetype | `cue_railing` | Builds | Verdict |
|---|---|---|---|---|---|
| scene01 campus stairs | campus plaza, w 11.0, drop 0.60 | STD | True | centre + 2 side handrails, h 0.9, sp 1.2 | match — **flag-low**, see 6.2 |
| scene02 underpass | 지하보도, stair **wall-to-wall** (w 3.50 = 2 × y_in 1.75) | STD | True | 2 freestanding lines at y ±1.65, **0.10 m off the wall**, + pit perimeter | **MISMATCH — flag** |
| scene03 riverbank | 하천 제방 | WEAK | False | — (identity: 무난간) | match |
| scene04 park trail | 공원 흙계단 | WEAK | False | — (log handrail reserved) | match |
| scene05 amphitheater | bowl + arc entry on cheek walls | WEAK | False | — | match (walls credited under §15(1)2) |
| scene06 overpass spiral | 도심 보행육교 | STD | True | h 1.05 + 90° dropout variant | match |
| scene07 temple stone path | 산사 배석로 | WEAK | False | — (무방호 관행) | match |
| scene08 sunken plaza | plaza pit | STD | True | parapet h 1.0 + permanent 1.8 m gap | match |
| scene09 ghat riverfront | 수변 관람계단 | WEAK | False | — | match |
| scene10 park deck switchback | 목재 데크로드 | STD | True | h 1.05, one span broken | match |
| scene11 footbridge stairs | 육교 | STD | True | h 1.10, sp 1.00 | match |
| scene12 riverside deck | cantilever waterfront deck | STD | True | river-side line, 2.4 m damaged span | match |
| scene13 apartment parking entry | 주택단지 | STD | True | h 0.95, 3 m demolished | match |
| scene14 grandstair illusion | monumental, open | WEAK | False | — (R2 "난간 전무" at drop 6.00) | match |
| **scene15 alley labyrinth** | 달동네 골목 계단 | **WEAK** | **False** (was True) | wall pipe when ON | **fixed by this report** |
| scene16 canopy shadow | 보도 + 하강계단, wall y_in 1.5 | STD | True | 2 lines at y ±1.4, **0.10 m off the wall** | **flag-low**, see 6.2 |
| scene17 ramp pair hangang | 한강 제방 | WEAK | False | — (무난간 관행) | match |
| scene18 wavy art stair | 예술계단, open | WEAK | False | — | match |
| scene19 fan winder | public corner stair | STD | True | handrail **on top of an outer parapet** | match — good exemplar of "wall guards, rail grips" |
| scene20 diagonal oblique | 광장 | STD | True | 2 lines at y ±2.4, open plaza | match |
| scene21 monumental self-occlude | 관공서 대계단 | STD | True | **centre** 2 lines only, no side rails | match |
| C1 snow stairs | generic outdoor straight stair | STD | True | one-sided pipe, h 0.90 | match |
| C2 leaf stairs | **공원 석계단** | WEAK-ish | True | one-sided line, h 0.90, freestanding posts | match-borderline — one-sided is right |
| C4 wet stairs | 광폭 화강암, w 6.0 | STD | True | cheek bands + 2 SS lines | match |
| D1 loading dock | industrial | WEAK | False | — (무방호가 현실) | match |
| D2 floor opening | 골조 공사 슬래브 개구 | WEAK | False | — (무방호가 특색) | match |
| D3 drainage channel | 노변 개거 | WEAK | False | — | match |
| D4 subway platform | 승강장 | STD | True | platform-end barrier; edge deliberately unguarded | match |
| N1 shadow band | 평지 광장 | n/a (낙차 0) | False | — | match — **ledger flag**, see 6.3 |
| N2 asphalt patch | 평지 노면 | n/a | False | — | match — **ledger flag** |
| N3 trompe-l'œil | 평지 바닥그림 | n/a | False | — | match — **ledger flag** |
| N4 downhill ramp | 완경사 + 옹벽 | n/a | False (dressing supplies the rail) | 옹벽 상단 guardrail via dressing | match — the corpus's only cue+/label− sample |
| N5 flush grating | 평지 | n/a | False | — | match — **ledger flag** |

### 6.2 Realism mismatches flagged for 통람 v2

> **Both scene02 and scene16 were subsequently assigned to me and converted — see §8.**
> §8 also corrects the prediction below: the conversion is **post-mounted, not wall-bracketed**,
> because these scenes' flanking walls are low parapets, and the ledger impact predicted here
> **does not materialise**. §6.2 is left as written so the reasoning trail stays honest.

**scene02 underpass — same defect class as scene15, one flag.**
`PARAMS.wall.y_in = 1.75` and the stair width is **3.50 = 2 × 1.75** `[measured]`, i.e. the stair runs
**wall to wall**, exactly the §15(3) geometry. Its own `PARAMS` comment already says
"계단 양측 **벽부착** 경사 레일" — but the code calls `sc.build_railing_line` at y = ±1.65, which builds a
**freestanding** guardrail (top + mid rail + posts to the ground + LOOK_GEO balusters + a coaxial
handrail) standing 0.10 m off each wall. Doc says wall-mounted; code builds freestanding. Korean
underpass stairs use wall-bracketed pipe handrails for precisely this reason. Recommended v2 action:
convert both lines to `stair_kit.build_handrail(wall_y=±1.75, wall_side=∓1)`. Ledger impact: scene02
would move from 난간 to 손잡이 → with scene15 already out, **15/16 = 0.9375** (Δ −0.007 from today).
*Not touched — scene02 is under W2-D edit.*

**scene16 canopy shadow — flag-low, same pattern, weaker case.**
Rails at y = ±1.4 against `wall.y_in = 1.5` — 0.10 m off the wall, same freestanding-against-a-wall
shape. Weaker than scene02 because the stair is in an open sidewalk and the walls are a partial pit
surround rather than a full flanking pair. Verify the wall extent before acting.

**scene01 campus stairs — flag-low, statutory rather than visual.**
Total drop 0.60 m, below the §15(1)2 1 m threshold, so `stair_compliance_v1.md` already records its
three rail lines as "법정 의무가 아닌 **초과 설비**". Korean campus stairs of that width genuinely do
carry centre handrails, so this is **not** a realism defect — it is listed only as the cheapest
remaining cue-ledger lever. If v2 chose to drop it: **14/15 = 0.9333**.

**C2 leaf stairs — reviewed, no action.** A 공원 석계단 with a one-sided rail matches survey bucket
POST_RAIL_MINIMAL and the rail is the scene's identity ("매몰 구간 유일 단서"). Keep.

**Net:** across 32 scenes, **one true archetype mismatch (scene02)** plus two low-severity flags.
scene15 was the only WEAK-archetype scene carrying a full code guardrail, and it is fixed.

### 6.3 Ledger flags (not realism)

N1 · N2 · N3 · N5 remain the **cue+ / label−** hole that `cue_arrangement_survey.md` §5 already ranks
priority 1 — adding no-drop railings (planter-edge rail, jaywalking fence, flat-deck rail). Combined
best case with everything in §6.2: **14/(15+4) = 0.737**. Still far above the 0.25–0.35 target, which
re-confirms §4: the target is reachable only at the render-variation level, not by scene counting.

---

## 7. Carry-over — owned by others, do not action from here

1. `Docs/reports/stair_compliance_v1.md` — scene15 row ("P1 R2 편측 난간" → R2 satisfied by 벽; H3 top-end
   shortfall) and the §1 note "손잡이 … 33씬 전부 미구현" (scene15 is now the first implementation).
2. `Docs/surveys/cue_arrangement_survey.md` §4.1 — move scene15 out of 난간 있음; book 16/17 = 0.941.
3. `Docs/reports/geom_baseline_w2.json` — scene15 `02611f19` → `e1e86da1`.
4. **scene02** wall-mounted handrail conversion (§6.2) — the one remaining archetype mismatch.
5. Variation candidates logged, not built: φ42.4 field-stock pipe (§1.4), the single **centre** pipe
   for this exact geometry (§3.2, blocked on a GRAZE read), and a broken/aged segmented pipe per the
   v5 "난간 훼손" direction — all cheap once the W2-D round gives a render to judge against.

---

## 8. Extension — scene02 underpass + scene16 canopy shadow

Assigned after §6 flagged them. Same constraints: English comments, evidence tags, **no render, no
commit**. Files owned for this pass: `scenes/main/scene02_underpass.py`,
`scenes/main/scene16_canopy_shadow.py`.

### 8.1 The measurement that changed the fix

§6.2 predicted a **wall-bracketed** conversion, on the scene15 model. Verifying the wall extent — the
check the supervisor required for scene16, and which turns out to matter just as much for scene02 —
falsified that prediction for **both** scenes.

scene15's flanking walls are house facades 2.7–4.6 m tall. scene02's and scene16's are **retaining
walls capped at `wall.parapet_top` = +0.15**, i.e. a low kerb at sidewalk level. They only become tall
*relative to the descending stair*. So the 850 mm handrail line starts **0.70 m above the wall top** at
the stair head `[computed]`:

| | parapet top | rail line meets wall at | off-wall run | on-wall run |
|---|---|---|---|---|
| scene02 | +0.15 | nose_z ≤ −0.70 → step 5 → **x ≥ 1.60** | 1.60 m (**25 %** of 6.40) | 4.80 m (75 %) |
| scene16 | +0.15 | nose_z ≤ −0.70 → step 5 → **x ≥ 1.60** | 1.60 m (**36 %** of 4.48) | 2.88 m (64 %) |

Wall brackets would have floated in mid-air over the first quarter/third of every run — exactly the
modelling error refused in scene15 §3.2. **Horizontal** extent was never the problem: scene16's walls
span x 0…18.48 (`Lx = wall.x1 − pit.x0`) and cover every rail span, and scene02's span x 0…7.0 and
cover the whole stair. The blocking dimension was vertical.

**What was converted instead: a single-line, post-mounted statutory handrail.** The §15(3) reading from
§0 still holds — both stairs are wall to wall (scene02 width 3.50 = 2 × `wall.y_in` 1.75; scene16
width 3.00 = 2 × 1.50), so §15(1)2 is satisfied by "벽", no stair guardrail is required, and what is
required is a **손잡이**. Only the mounting method differs from scene15, and post-mounting is also what
open-cut underpass entrances are actually built with — a fabricated stainless line whose posts stand on
the treads. Posts additionally make the statutory ≥300 mm end extensions *buildable*, which a wall
mount here could not do; scene15 had to accept an H3 shortfall precisely because its wall stopped at
the drop edge.

### 8.2 What changed, per scene

Both scenes replaced `sc.build_railing_line` with `stair_kit.build_handrail` (free-standing mode) at
φ34 / h850 / ext 300, `y = wall.y_in − 0.07` → pipe face 53 mm and post face 50 mm clear of the wall,
both ≥ the statutory 50 mm (§15(4)2) `[computed]`.

| | scene02 | scene16 |
|---|---|---|
| Lines converted | 2 (stair S/N) | **4** (west stair S/N + east exit stair S/N, the latter in the 180° rot_group) |
| Old per line | top + mid rail + **59** balusters + 6 posts + coaxial LOOK_GEO handrail (6 more posts) = 78 | same shape, **43** balusters = 60 |
| Old total | **156 prims = 29.8 % of the scene** | **240 prims = 39.7 % of the scene** |
| New per line | ExtTop + Slope + ExtBot + 7 posts = 10 | ExtTop + Slope + ExtBot + 5 posts = 8 |
| New total | **20** | **32** |
| Pit perimeter guard | **untouched** (19 prims) | **untouched** (34 prims) |

Built geometry, from the fake-USD inventory `[measured]` — scene02 `StairRail_N`:

```
ExtTop  T=(−0.15, 1.68, +0.85) RY=90   h=0.30  r=0.017
Slope   T=( 3.20, 1.68, −0.75) RY=116.565  h=7.1554  r=0.017
ExtBot  T=( 6.70, 1.68, −2.35) RY=90   h=0.60  r=0.017
Post_0..6  x = −0.3 / 0.9 / 2.1 / 3.3 / 4.5 / 5.7 / 6.9,  r=0.020
```

Post heights run 0.85–1.00 m: the rail follows the **linear nosing line** while the feet land on the
**stepped** tread surface, so mid-tread posts are naturally taller. Correct, not a defect.

**The pit perimeter guardrails were deliberately not touched.** In both scenes that rail is the real
fall protection — a 3.2 m / 2.1 m hole in a public sidewalk — and in scene02 it is the scene's whole
identity: the docstring's hazard is that from h0.3 at distance "피트가 완전한 평지로 보이고 난간·
점자블록만 떠 있는 그림". The stair lines never carried that read: their rail line drops below the
sidewalk plane by x = 1.7 `[computed]`, so only the perimeter rail is visible at grazing angle. Removing
stair infill cannot damage the grazing cue.

### 8.3 Statutory position, and the two clearances that improved

All three handrails are **fully H1–H3 compliant** — `build_handrail(strict=False)` returns **zero**
warnings for each (φ34 ∈ 32–38 · h850 · ext_top 300 · ext_bot 600/300) `[measured]`. `stair_compliance_v1.md`
records handrails as "**33씬 전부 미구현**"; scene02 and scene16 are now the first two **fully compliant**
implementations in the corpus (scene15's is deliberately partial).

Two pre-existing defects were removed as a side effect:

1. **Posts standing in the statutory tactile band.** scene02's ground_kit `stair_top` band occupies
   x −0.90…−0.30 (spec §12.4). The old build put a guardrail post at **x = −0.50 — fully inside it** —
   plus a LOOK_GEO handrail post at x = −0.30. The new build has a single post at x = −0.30, grazing
   the downhill edge by 20 mm `[computed]`. Two intrusions → one graze. (The band is gated on
   `cue_tactile`, default OFF, so this matters in the tactile-ON variant.)
2. **The duplicate coaxial post line.** `build_railing_line` posts at 1.2 m from x = −0.5 *and* its
   internal LOOK_GEO handrail posts at 1.2 m from x = −0.3 gave two parallel post rows a constant
   0.20 m apart, same radius, on every line — "double posts" in silhouette. Gone; one row remains.

**What was NOT fixed, and stays open.** scene02's `stair_compliance_v1.md` P0s are untouched and remain
violations: **L1** (계단참 1개 부족, 낙차 3.20 직통) and **R1** (중간난간 1열 부족 — width 3.50 > 3.00 with
riser 0.160 > 0.150, so the §15(1)3 AND-exemption fails). Converting the *side* lines to handrails does
not satisfy R1, which requires a genuine **mid railing** at y = 0. The v8 landing + mid-rail design is
already written into scene02's docstring and explicitly flagged there as not yet implemented; it is a
separate work item and I did not touch it. Note the interaction: once that mid rail exists, each 1.75 m
bay has a wall on one side and a railing on the other, and these wall-side handrails remain correct.

### 8.4 Cue ledger — the expected 15/16 does not materialise

**P(낙차 | 난간) stays at 16/17 = 0.941.** Neither scene leaves the numerator, because both **keep their
pit perimeter guardrails** — unambiguously 난간 under the survey's own definition ("파이프 난간·가드레일·
킥플레이트 계열"), visible in the default render, and in scene02's case the scene's primary cue. Only the
stair lines converted, and a scene with any visible railing counts once.

The 15/16 = 0.9375 figure anticipated at assignment assumed scene02 would drop out entirely. It cannot,
unless its pit guard is deleted — which would be both a code violation (an unguarded 3.2 m opening in a
public sidewalk) and the destruction of the scene's hazard concept. Not recommended.

So the extension's ledger delta is **zero**. What it does buy is qualitative: cue *strength* fell
sharply in both scenes (a guardrail with mid rail and 43–59 balusters per line → a single φ34 pipe),
which matters if the ledger ever moves beyond binary presence to a weighted cue measure. §4's
conclusion is unchanged and, if anything, reinforced: the scene-level target is unreachable by
construction, and the render-variation route (M10 ⓐ) is the only one that reaches it.

### 8.5 Self-verification

| Check | Result |
|---|---|
| `py_compile` scene02 / scene16 | **exit 0** both |
| `pyflakes` scene02 | 3 findings, all pre-existing — and **one fewer than baseline**: `stair_kit as sk` was an unused import at HEAD and is now used |
| `pyflakes` scene16 | 2 findings (`sys`, `math`), **identical to baseline** |
| `python3 ground_kit.py` | **exit 0** — 33/33 hard gates |
| `scripts/geom_invariance_check.py` | **exit 0** · R-5 PASS · **R-4 33/33** · **R-6 33/33** |

| Scene | Prims before | after | Δ | Hash before → after |
|---|---|---|---|---|
| scene02 | 523 | **387** | **−136** (−26.0 %) | `cb430e00` → `f9087314` |
| scene15 | 545 | **429** | **−116** (−21.3 %) | `02611f19` → `e1e86da1` |
| scene16 | 604 | **396** | **−208** (−34.4 %) | `b3f31a1c` → `a40275ae` |
| **Total** | 1672 | 1212 | **−460** | — |

All three arms (`MTL=0`, `MTL=1`, `V1=1`) agree per scene, and the other 30 scenes hold their prior
hashes — confirming the edits stayed inside the three owned files.

**GT invariant.** Handrails and guardrails alike are members above the walking surface; no `z(x,y)`
changed in either scene. `stair_kit.build_handrail`'s documented "drop label invariant" applies, and the
horizontal end extensions float over level ground outside the stair, contributing no pixel to the drop
mask.

**ground_kit wiring untouched.** scene02's `plan_ground("sidewalk_block", …)` call — region, `edges=[("pit_edge", pit.x0)]`,
`manhole [(−1.20, 0.35)]`, the two gullies at x −0.95, `gutter_L=0`, the `tactile=("stair_top",) if
cue_tactile` gate and the three `slabs` — is byte-identical, as is scene16's `tactile=("entrance",)`
plan (its band sits at x −6.00…−5.40, nowhere near any rail `[measured]`). `M["rail"]` is still created
and still feeds `manhole` / `gully` in both scenes.

**Not verified — no render.** Whether a φ34 pipe reads at d5/d10, and whether removing 396 balusters
across the two scenes moves the GRAZE band statistic (predicted neutral-to-better, since all of it sits
below the sidewalk plane), are for the 33-scene W2-D round.

### 8.6 Carry-over added by this extension

6. `stair_compliance_v1.md` — scene02 and scene16 rows: R2 now satisfied by "벽" + compliant 손잡이;
   the §1 note "손잡이 … 33씬 전부 미구현" is now wrong for three scenes.
7. `geom_baseline_w2.json` — scene02 `cb430e00` → `f9087314`, scene16 `b3f31a1c` → `a40275ae`
   (plus scene15 from §5.2).
8. **scene02 P0 L1 + R1 remain open** — the landing and mid-rail design already drafted in the scene's
   own docstring. Unowned by this pass.
