# W3 intake — policy reversals and the "match the real sample" bar (v1)

> **Wave**: W3 · **Task**: intake (verification + spec drafting, no implementation) · **Date**: 2026-07-30
> **Branch**: `feat/realism-v1` · **Repo state at intake**: clean tree, HEAD `578d406`
> (W3-R survey wave), no untracked source `[measured]`. **During the session** a sibling agent
> landed `Docs/surveys/w3_intake_01_05.md`, `assets/download_urban.py`, `assets/verify_urban.py`
> and a `.gitignore` edit `[measured]` — consolidated in §0.1; I touched none of them.
> **Scope discipline**: this file is the only file written. **No scene file, no shared module, no
> asset, no commit.** Every "build spec" below is a *proposal for the W3 execution spec*, not an
> applied change.
> **Cross-references**: `w3r_asset_map_v1.md` (R1) · `w3r_prop_mapping_v1.md` (R2) ·
> `w3r_building_ab_v1.md` (R3) · `redteam_w3r.md` (RT) · `tonglam_v2.md` (eyes) ·
> `era_consistency_survey_v1.md` · `korean_pedestrian_geometry.md` (kpg) ·
> `user_feedback_v5_1.md` (the superseded directive) · `real_reference_expansion.md`.

## Evidence tags

| tag | meaning |
|---|---|
| `[measured]` | re-executed in this session — file read, grep, AST-exec, render viewed, or live HTTP fetch |
| `[law]` | statute / ordinance / gov guideline text fetched **or** quoted from an in-repo document whose source URL I re-read this session |
| `[photo]` | a real-photograph population identified this session, with source URL and count |
| `[stat]` | derived over a measured population |
| `[derived]` | arithmetic consequence of two `[law]`/`[measured]` facts, stated as such |
| `[assumed]` | inference with no source — must not be treated as verified |
| `[근거 없음]` | searched for and **not found**; the row needs photo measurement before it can be built |

---

## 0. The one-paragraph verdict

The two policy reversals are **both correct and both cheap**, and the code evidence says they are
*regressions to be undone*, not new features. **Jitter**: every geometric jitter in the tree comes
from one directive (`user_feedback_v5_1.md` §3, 2026-07-27) which contradicts a statute the project
had already surveyed and written down **before** that directive was issued
(`korean_pedestrian_geometry.md` §5.1, quoting 산림청 고시 제2023-48호: *"가로수 식재 유형은 도로선형과
평행한 열식재를 원칙"* — and the survey's own conclusion line reads **"한국 보도에서 랜덤 배치는 존재하지
않는다"**) `[law]` `[measured]`. The W1 survey was right; v5.1 §3 overrode it; W3 restores it.
**Species**: `build_tree` draws a species **per tree** from one global weighted pool
(`scene_common.py:2443-2444`), so a 20-tree street row in scene06 is a random mix of oak, juniper
and pine — while 「서울특별시 가로수 조성 및 관리 조례」 제7조1호라 says *"도로의 같은 노선과 도로 양측에는
같은 수종으로 식재한다"* `[law]`. Both defects are visible in the shipped `260730_w2d_fix` renders
`[measured]`. Scope: geometric jitter = **9 code sites + 18 batch1 call sites + ~30 baked-in yaw
literals**; species mixing = **1 function, 17 scenes**; decal yaw = **2 builders, all 33 scenes**
(stain) / **10 of 19 ground profiles** (patch). Nothing here needs new assets — the 10 verified
trees and 7 shrub/grass rows are already on disk and **none of the 7 new trees is wired into
`VEG_TREES`** `[measured]`.

**The one thing that must be decided before any of it is built**: the prop-edge-distance rule table
(§5) has 4 statutory rows and 6 rows that are `[derived]` or `[근거 없음]`. The user's bar
("실제 표본 확인해서 똑같게") means those 6 rows must be **pixel-measured from the photo panels in §5.4
before** the CPU gate is allowed to enforce them. Enforcing a guessed setback is worse than none.

### 0.1 Consolidation with `Docs/surveys/w3_intake_01_05.md` (agent A, same wave)

A's file landed mid-session and covers the **same three global policies for scenes 01–05**
(its G-1 jitter, G-2 species, G-3 prop-edge-distance) plus per-scene rows. The two files agree on
every load-bearing conclusion. What follows is the reconciliation; **A's per-scene detail governs
01–05, this file governs the library-wide mechanism, the tooling and the 통람 v3 upgrade.**

**Agreements (no action needed)** — the v5.1 §3 lineage; `ground_kit.py:689/733` ±14° and
`:1027` ±22° as the decal sources; `batch1_common.py:248/256` as the furniture source;
`scene_common.py:2443-2444` as the species-mixing mechanism; keep vegetation `yaw 0–360°` and
footprint splay; "align to the structural line, vary by size/model/interval, never by angle".

**A found, this file adopts** `[measured — A's citations spot-checked]`:

| A's ID | source | why it matters here |
|---|---|---|
| J8 | `scene04_parktrail.py:266-274` — 5 bench yaws 96/94/4.5/93/87° | adds scene04 to J-5's scope |
| J10 | `scene17:256`, `scene13:223` dressing jitter ±3–8° | adds 13·17 to J-5 |
| J11 | `scene09:266,1422`, `scene11:232` bench jitter | already in J-5's scene list, now with line refs |
| J12 | `sceneD1_loading_dock.py:855` crate yaw `U(−9°,+9°)` | **new to this file** — stacked crates; abolish (a stacked crate is squared to the dock) |
| J13 | `sceneD1:153` `yaw=-14.0`, `sceneD2:210` `yaw=-22.0` | **new** — two hard-coded off-axis props; abolish |
| J14 | `scene_common.py:1909` `build_worn_stone_stairs(jyaw=3.0)`, `:1935` | **new, and I agree with A's KEEP**: hand-set masonry really is laid ±3°. Add to §3.2(b) |
| G-3 law 1 | 「도로의 구조·시설 기준에 관한 규칙」 제16조 — 보도폭 = **유효폭 + 노상시설 폭**, 유효폭 **≥2.0 m** | **stronger than the source I had.** Adopt as R8's primary basis; the Seoul manual's 1.5 m becomes the *constrained-condition* floor, not the target |
| G-3 pole row | streetlight/sign pole **0.35–0.60 m** (nominal 0.45) from the boundary line, `[assumed]` from the strip width | becomes the **interim value for M2**, still to be photo-confirmed before the gate enforces it |
| G-2 law | 「도시숲·생활숲·가로수 조성·관리 기준」 제2-3조 가 — 동일 노선 동일 수종 **+ the break rule** ("도로의 방향이 바뀌거나 신설·확장되는 경우") | this is the missing justification for my `▸` backdrop-belt exception: a species change must be caused by a **route event**. Adopt the wording into §4.3 and into the T-3 checklist |

**This file found, A does not carry**: the `build_footprints` AABB/prim divergence (§3.6); the
keep-at-zero parameters `infra_kit.py:403/531` and `ground_kit.py:607` and the gate that bans
non-zero values (J-11); the exact 18 `bc.jit_yaw`/`bc.jit_pos` call sites; the `place_shrubs`
per-shrub draw at `scene_common.py:2819` (S-2); the **`ori_axis` hazard** (§3.7); the linter's
harness (§5.3); the whole 통람 v3 package (§7).

**Two discrepancies to resolve before the execution spec is frozen**:

1. **Patch scope.** A says `build_patch_field` applies to "**18 ground profiles**"; I measure
   **10 of 19** profiles carrying a `("patch", n)` row (`plaza_granite, plaza_water,
   sidewalk_block, street_asphalt, alley_concrete, roof_membrane, ramp_parking, ramp_road,
   levee_paved, verge_rural`), by AST-exec of `GROUND_PROFILES` — reproduction in Appendix B
   `[measured]`. `stain` **is** in all 19. My reading is that A's 18 conflates the two. Low
   stakes (both mean "change the default once"), but the W3 spec should carry the correct number.
2. **Abolition mechanism.** A changes the *defaults* (`jit_yaw(lo=0.0, hi=0.0)`) and keeps the
   call sites; I delete the call sites and deprecate the helpers. **Recommend both, in A's
   order**: flip the defaults first (one edit, library-wide, immediately verifiable by the
   linter), then remove the now-inert call sites in the same work package so the code does not
   accumulate dead calls that read as intent.

---

## 1. What the new bar changes

| | old bar (W2, `tonglam_v2.md`) | **new bar (W3 intake)** |
|---|---|---|
| question | "does this read as a real Korean place at the robot viewpoint?" | **"is this the same as the real sample?"** — user: *"실제 표본 확인해서 똑같게"* |
| unit of judgment | the frame, holistically | the **object class**: species, alignment, pitch, setback, silhouette |
| evidence admitted | the judge's eyes | eyes **+ a named photo panel** the frame is compared against, side by side |
| what "plausible" buys | a PASS | **nothing** — plausible-but-not-matching is now a FAIL |
| burden of proof | reviewer must show it is wrong | **builder must show the real sample it matches** |

Operational consequence, and the reason §7 exists: a spec row is not shippable until it names the
photograph population it reproduces. Where I could not find one, the row is marked `[근거 없음]` and
carries a measurement task instead of a number.

**Road-view services (Kakao/Naver roadview, Google Street View) are banned as evidence** per the
intake brief; every `[photo]` population below is Wikimedia Commons, a government publication, or
the repo's own licence-audited reference set.

---

## 2. Spec-row index

Full 7-field cards are in §3–§7. Priority: **P0** = blocks the W3 render round · **P1** = must land
in W3 · **P2** = W3 if budget allows.

| ID | item | policy | verdict | affected scenes | prio |
|---|---|---|---|---|---|
| **J-1** | `build_patch_field` decal yaw ±14° | jitter | **abolish** | 10 of 19 profiles (≈22 scenes) | **P0** |
| **J-2** | `build_stain_field` blot yaw ±22° | jitter | **abolish + reshape** (→ D-1) | 19 of 19 profiles = all 33 | **P0** |
| **J-3** | `bc.jit_yaw` on benches / fences / lamps (batch1) | jitter | **abolish** | C1·C2·D2·D4·N1·N3 | **P1** |
| **J-4** | `bc.jit_pos` on benches / planters / lamps / bins (batch1) | jitter | **abolish** | C1·C2·C4·D2·D4·N1·N2·N3·N5 | **P1** |
| **J-5** | baked-in yaw literals ±3–22° on main-scene / batch1 furniture | jitter | **abolish** | 01·03·04·06·09·11·13·17·D1·D2·(14·16·20·21 bollards) | **P1** |
| **J-6** | street-tree row pitch irregularity baked into coordinate tuples | jitter | **regularise to constant pitch** | 06·11·12·13·D3·N5 | **P1** |
| **J-7** | `build_footprints` per-step yaw ±12° | jitter | **keep** (+ fix AABB bug) | D2 (+ C1 snow) | P2 |
| **J-8** | scatter `scale_jitter` / verge / backdrop-shrub / reed jitter | jitter | **keep** | 04·05·07·10·12·17 etc. | — |
| **J-9** | `build_tree` lean / canopy-blob / 0–360° yaw | jitter | **keep** | all tree scenes | — |
| **J-10** | `jit_tint` ±5 % per-instance tint | jitter | **keep** (explicitly out of scope) | all | — |
| **J-11** | `build_joint_grid` / `gully_positions` `jitter=` params | jitter | **keep at 0, ban >0 by gate** | none live | P2 |
| **S-1** | per-tree species draw from one global pool | species | **replace with per-scene assignment** | 17 tree scenes | **P0** |
| **S-2** | per-shrub species draw inside one bed | species | **replace with per-bed assignment** | all `place_shrubs`/hedge scenes | **P1** |
| **S-3** | 7 verified trees + 4 shrub/grass rows never wired in | species | **wire `VEG_TREES` → `VEG_SPECIES` table** | library-wide | **P0** |
| **S-4** | within-species variation (height / form) | species | **keep ±8 %, add statutory floor** | 17 tree scenes | P1 |
| **E-1** | street-tree lateral setback + longitudinal pitch | edge-dist | **new rule + gate** | 06·11·12·13·D3·N5 | **P1** |
| **E-2** | bench / bin / lamp / planter setback from walking-zone edge | edge-dist | **new rule + gate**, 6 rows need photo measurement | 15 scenes | **P1** |
| **E-3** | bollard line: on the kerb line, 1.5 m pitch, axis-locked | edge-dist | **rule exists, gate missing** | 11·12·14·16·20·21·C4·D1·N1–N5 | **P1** |
| **E-4** | placement linter (CPU, no GPU) | edge-dist | **new tool** `scripts/placement_lint.py` | tooling | **P0** |
| **D-1** | stain blots are rectangles | decal | **N-gon irregular mask** | all 33 | **P0** |
| **D-2** | leaf / gravel / soil carpets have ruler-straight edges | decal | **N-gon mask + scatter feather ring** | 03·07·10·C2·D3 | **P1** |
| **D-3** | repair patches keep the rectangle but lose the yaw | decal | **axis-lock to pavement module** | 10 profiles | **P0** (with J-1) |
| **T-1** | per-scene reference-photo panels | 통람 v3 | **new** `Docs/reference_photos/w3/<archetype>/` | 33 scenes → 12 archetypes | **P0** |
| **T-2** | side-by-side comparison protocol | 통람 v3 | **new** | judging | **P0** |
| **T-3** | "identical to sample" checklist per scene type | 통람 v3 | **new** | judging | **P0** |
| **T-4** | numeric assist band from the n=54 photo set | 통람 v3 | **adopt, advisory only** | judging | P1 |

---

## 3. Policy P1 — JITTER ABOLITION

### 3.1 Lineage: where the jitter came from, and what it overrode

`user_feedback_v5_1.md` §3 (2026-07-27 evening), verbatim `[measured]`:

> **3. 배치 비정형**: 벤치·조형물은 앵커(나무 그늘·벽·화단) 옆에, 격자 정렬·등간격 금지,
> yaw ±3~8° 지터. 사인은 실제 부착 방식(기둥 지주 h2.2 or 벽부착)만.

Three sub-directives are bundled in that one line, and **they are not equally right**:

| sub-directive | W3 verdict | why |
|---|---|---|
| "앵커 옆에" (place beside an anchor — tree, wall, planter) | **KEEP** — it is the correct half | real furniture *is* placed against edges and anchors, not mid-field |
| "격자 정렬 금지" (no grid alignment) | **KEEP, narrowed** | applies to *composition* (do not build a symmetric parade); does **not** license per-object rotation |
| "yaw ±3~8° 지터" | **ABOLISHED** | contradicts statute and photographs; see §3.3 |

The decisive point is chronological. `korean_pedestrian_geometry.md` §5.1 — written **before** v5.1 —
already quoted 산림청 고시 제2023-48호 「도시숲·생활숲·가로수 조성·관리 기준」 2-3(6)(가)(나) and drew the
conclusion in its own words `[law]` `[measured]`:

> (나) 가로수 식재 유형은 **도로선형과 평행한 열식재를 원칙**으로 하되 … 도로의 동일 노선과 도로 양측에는
> 통일성이 갖춰질 수 있도록 **동일한 수종을 권장**
>
> **→ 씬 규칙**: 가로수는 **4~8 m 등간격 열식**, **연석에서 1 m 이상 안쪽**, **한 노선은 한 수종**.
> 현재 우리 씬은 나무를 랜덤 산포하는 경우가 있는데, **한국 보도에서 랜덤 배치는 존재하지 않는다.**

So the project surveyed the rule, wrote it down, then built the opposite. W3 is not adopting a new
opinion; it is closing a documented gap. **This lineage should be stated in the W3 execution spec**,
because it is the answer to "why are we undoing a user directive": we are not — we are applying the
user's *older and better-sourced* instruction (연대 3요소, 실사례 우선) over a later heuristic.

### 3.2 Complete inventory of stochastic geometry

Method: `grep -rn "jitter\|jit_"` over all `*.py` (225 hits), then every hit read in context; plus
`grep -n "rotz="` in `ground_kit.py` (12 hits, each read) and `uniform(` in the shared kits
`[measured]`. Tint jitter is listed for completeness and is **out of scope** (the brief: "tint OK to
keep — this is about GEOMETRY alignment").

#### (a) ABOLISH — built objects, decals, furniture

| # | site | what it randomises | amplitude | ID |
|---|---|---|---|---|
| 1 | `ground_kit.py:689` (default) → `:733` | repair-patch yaw | `U(−14°,+14°)` | J-1 |
| 2 | `ground_kit.py:1027` | free-form stain blot yaw (`dirt/water/oil/gum/efflorescence/drip`) | `U(−22°,+22°)` | J-2 |
| 3 | `scenes/batch1/batch1_common.py:248` `jit_yaw()` | furniture yaw, `\|Δ\|∈[lo,hi]`, random sign | default `[3°,8°]` | J-3 |
| 4 | `scenes/batch1/batch1_common.py:256` `jit_pos()` | furniture position, isotropic | `\|d\|≤amp`, amp 0.12–0.20 m | J-4 |
| 5 | `scene01_campus_stairs.py:175-177` | 6 bench yaw literals | −6, +4, −5, +3.5, −7, +5 ° | J-5 |
| 6 | `scene06_overpass_spiral.py:262` | 3 bench yaw literals | −6, +5, 175 ° | J-5 |
| 7 | `scene11_footbridge_stairs.py:233` | 2 bench yaw literals | 86, −94 ° (= ⟂ ± 4°) | J-5 |
| 8 | `scene03_riverbank.py:235,237,239,257` | 3 city-block + 1 pavilion `jyaw` | +3.5, −4.0, +2.5, −3.0 ° | J-5 |
| 9 | `scene04_parktrail.py:266-274` | 5 bench yaw literals | 96, 94, 4.5, 93, 87 ° | J-5 |
| 10 | `scene17_ramp_pair_hangang.py:256` · `scene13_apartment_parking_entry.py:223` | dressing-prop yaw | ±3–8° | J-5 |
| 11 | `scenes/batch1/sceneD1_loading_dock.py:855` | stacked-crate yaw `crng.uniform(-9,9)` | ±9° | J-5 |
| 12 | `sceneD1_loading_dock.py:153` (`yaw=-14.0`) · `sceneD2_floor_opening.py:210` (`yaw=-22.0`) | hard-coded off-axis props | −14° / −22° | J-5 |
| 13 | `scene06:255-260` / `scene11:229-233` / 12 · 13 · D3 · N5 tree tuples | street-tree **pitch** irregularity baked into literals | 6.6–7.2 m (06), 7.4–7.6 m (11) | J-6 |

Rows 9–12 are A's J8/J10/J12/J13; every line reference re-opened and confirmed this session
`[measured]` (`scene04:276` `benches=[(11.7,2.55,"lower",96.0), …]`; `sceneD1:855`
`rotz=yaw + crng.uniform(-9.0, 9.0)`; `sceneD1:153` `yaw=-14.0`; `sceneD2:210` `yaw=-22.0`).

> **One dissent inside row 11.** `sceneD1`'s crates are **handled goods, not built objects** — a
> forklift-stacked pallet run really does sit a couple of degrees out, and sceneD1 is one of the
> four eyes-**PASS** scenes (`tonglam_v2.md` §1). Abolishing to exactly 0° risks trading a PASS for
> a CAD read. Recommend: **cap at ±2.5° and align the stack's base yaw to the dock edge**, rather
> than zero. Same reasoning does **not** apply to `sceneD1:153` / `sceneD2:210`, which are fixed
> site props and should go to 0°. Supervisor call — flagged in §10.

`jit_yaw` / `jit_pos` call sites, all 18, from `grep -rn "bc.jit_yaw\|bc.jit_pos"` `[measured]`:
`sceneN1:337,338,348,349` · `sceneN2:351,352,361` · `sceneN3:583,584,589` · `sceneN5:386` ·
`sceneC1:811,812,837` · `sceneC2:801,802,821,837` · `sceneC4:377,381` · `sceneD2:293,294` ·
`sceneD4:649,650`. Objects touched: benches, planters, street lamps, litter bins, a safety fence.

#### (b) KEEP — natural deposition and organic form

| # | site | what | why keep |
|---|---|---|---|
| 10 | `scene_common.py:2390` `scale_jitter` (`place_scatter`) | leaf / rock / debris size | deposition, not placement |
| 11 | `scene_common.py:2385-2388` scatter `yaw 0–360°`, tilt | leaf / debris orientation | a fallen leaf has no axis |
| 12 | `ground_kit.py:1549,1561,1619` `scale_jitter=(0.38,0.62)` | D-5 rock scatter (W2 F2) | ditto; already re-parameterised by the eyes round |
| 13 | `scene04_parktrail.py:420-440` `verge_instances` | verge tuft position/scale/step/dropout | grass tufts on a soil verge really are irregular |
| 14 | `scene05_amphitheater.py:494-510` `backdrop_instances` | backdrop shrub lobes | an unclipped shrub mass has no axis |
| 15 | `scene12:254` / `scene17:1162` reed stalks | height/tilt jitter | ditto |
| 16 | `scene_common.py:2477-2496` `build_tree` lean 0–4°, canopy blob scatter, canopy scale | tree form | a tree trunk genuinely leans |
| 17 | `scene_common.py:2456` `yaw_deg=U(0,360)` on the tree asset | tree crown bearing | a crown has no front |
| 18 | `ground_kit.py:1072` `build_footprints` step yaw `±6°` | footprint splay | a walker's feet really do splay — **but see the bug in §3.6** |
| 19 | `scene_common.py:1909,1935` `build_worn_stone_stairs(jyaw=3.0)` | per-block yaw ±3° on worn stone steps | hand-set masonry genuinely is laid a few degrees out — A's J14 ruling, adopted |
| 20 | `jit_tint` (`batch1_common.py:270`) and all `tint_jitter()` scene copies | colour | out of scope by instruction |

#### (c) KEEP-AT-ZERO — parameters that exist but are not used

| # | site | note |
|---|---|---|
| 20 | `infra_kit.py:403,434,479` `build_railing(jitter=0.0)` | the docstring already says *"real joints are exactly evenly spaced — the jitter recommendation in §3.4 concerns **placed objects**"*. Default 0, no caller overrides `[measured]`. The **docstring is now wrong in its second clause** and should be corrected when touched. |
| 21 | `infra_kit.py:531,557,592` `gully_positions(jitter=0.0)` | non-zero only inside the module self-check (`:1437,1439`). Keep default 0; the linter should **ban** a non-zero value in scene code. |
| 22 | `ground_kit.py:607,648,660` `build_joint_grid(jitter=0.0)` | paving joints; same treatment. |

#### (d) Directional yaw — **not** jitter, must not be swept up

`ground_kit.py:1102` (`wear_lane`), `:1130` (`edge_litter`), `:1166` (`edge_break`), `:816/825/836`
(patch cut lines), `:863/877` (gutters) all take `yaw = atan2(...)` **from a centreline**. These are
*alignments*, and the abolition pass must not touch them `[measured]`. Same for
`build_stain_field`'s `grime_band` and `tire` kinds, which are already forced to `yaw = 0.0` by the
`line is not None` branch at `ground_kit.py:1027`.

### 3.3 Real-sample evidence for abolition

**Statute** `[law]` (fetched live 2026-07-30):

| source | clause | text |
|---|---|---|
| 「서울특별시 가로수 조성 및 관리 조례」 (제9970호, 시행 2026-01-05) | 제7조 1호 **나** | *"식재유형은 **도로선형과 평행한 열식**을 원칙으로 하되…"* |
| 〃 | 제7조 1호 **가** | *"식재간격은 **6~8미터**를 기준으로 한다…"* |
| 〃 | 제7조 1호 **라** | *"도로의 같은 노선과 도로 양측에는 **같은 수종**으로 식재한다."* |
| 「서울특별시 가로수 조성 및 관리 조례 시행규칙」 (규칙 제4056호, 2015-10-22) | — | *"**노선별, 구간별로 수관의 모양과 높이를 일정하게 유도**"* / 규격 *"나무높이 **3.5 m 이상**·가슴높이지름 **10 cm 이상**(근원지름 12 cm 이상)"* |
| 산림청 고시 제2023-48호 「도시숲·생활숲·가로수 조성·관리 기준」 2-3(6)(가)(나) | — | 종간 **4~8 m** · 횡간 **보도·차도 경계선에서 ≥1 m** · **도로선형과 평행한 열식재 원칙** · 동일 노선 **동일 수종 권장** (in-repo quote at kpg §5.1, source URL re-read this session) |
| 산림청 「가로수 조성·관리 추진계획」 | — | 기본 **8 m**, 가로등주 간격에 맞춘 **등간격 배치**를 위해 최소 **6 m**까지 조정 |

Sources: [서울 조례](https://www.ulex.co.kr/%EB%B2%95%EB%A5%A0/1772859-2001522-%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C%EA%B0%80%EB%A1%9C%EC%88%98%EC%A1%B0) ·
[서울 시행규칙](https://www.ulex.co.kr/%EB%B2%95%EB%A5%A0/1194320-2001628-%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C%EA%B0%80%EB%A1%9C%EC%88%98%EC%A1%B0) ·
[가로수 조성 및 관리규정 (국가법령정보센터)](https://www.law.go.kr/LSW/admRulInfoP.do?admRulSeq=2000000017655) ·
[산림청 추진계획](https://www.forest.go.kr/kfsweb/cmm/fms/FileDown.do?atchFileId=FILE_000000020068117&fileSn=0&bbsId=BBSMSTR_1069)

The Korean word 열식 (列植) means *planting in a file*. There is no legal or practice room for a
per-tree yaw or a per-tree position offset on a street.

**Photographs** `[photo]` — populations, not cherry-picks:

| claim | population | n | URL |
|---|---|---|---|
| street trees stand in a straight file at constant pitch, one species | Commons `Category:Damyang Metasequoia Road` | **12** | https://commons.wikimedia.org/wiki/Category:Damyang_Metasequoia_Road |
| sidewalk furniture and trees run parallel to the kerb at a constant offset | Commons `Category:Sidewalks in South Korea` (Okcheon ×7, Hwaseong ×2, Cheonan, Jeongwangsingil, Daejeon Munjeong-ro ×2, `Row of trees on sidewalk.jpg`) | **18** | https://commons.wikimedia.org/wiki/Category:Sidewalks_in_South_Korea |
| park benches sit in a file, seat axis parallel to the path edge | Commons `Category:Benches in South Korea` (Pyeongchon Central Park ×8, 오금공원 ×3, 대현산공원, 행당역, 독특한 형태의 하얀 벤치…) | **25** | https://commons.wikimedia.org/wiki/Category:Benches_in_South_Korea |
| Korean street-furniture inventory and its alignment | Commons `Category:Street furniture in South Korea` + 22 subcategories (`Street lights…`, `Waste containers…`, `Bus shelters…`, `Information boards…`, `Streethole covers…`) | 14 direct + 22 subcats | https://commons.wikimedia.org/wiki/Category:Street_furniture_in_South_Korea |
| in-repo, already licence-audited | `Docs/reference_photos/expanded/` — Streets in Seoul ×5, Sidewalks ×7, Insadong ×6, Bukchon ×5, Jongno (KOGL-1) ×2 | **54** with `LICENSES.csv` | in repo |

Three of these five populations are already in the repo with a verified licence ledger
(`Docs/reference_photos/expanded/LICENSES.csv`, 54 rows, 0 NC/ND) `[measured]`. The two Commons
categories are new and must be harvested by T-1.

### 3.4 What the shipped renders actually show `[measured]`

I viewed 6 cuts from `look_check/<scene>/260730_w2d_fix/` (scene01 `beauty_overview`, scene03
`levee_walk`, scene06 `overview`, scene07 `temple_walk`, scene10 `leaf_edge`, scene11
`sidewalk_approach`). Not the whole 13+4-cut set — see §9.

- **scene01 `beauty_overview`** — the two benches beside planters read as *knocked askew*: each sits
  at a visible few degrees to the planter's cap face and to the paving joint grid, which is exactly
  the read a photograph of a Korean campus plaza never produces. In the same frame the grey repair
  patches are **rotated rectangles** — the ±14° is legible as a tilted quad against the orthogonal
  slab joints. Both J-1 and J-5 are visible in one frame.
- **scene07 `temple_walk`** — the leaf-litter carpets are unmistakable rotated rectangles with razor
  edges lying on the decomposed granite; the boundary is a straight line at an angle to everything
  else in the frame. J-2/D-2 in one frame.
- **scene06 `overview`** — the verge street-tree row contains at least three different crown types
  within ~40 m: a large dark broadleaf, a small pale sapling, another broadleaf. S-1 visible.
- **scene03 `levee_walk`** — within one frame of one riverbank: a broadleaf, a narrow columnar
  conifer, a broad conical conifer, another broadleaf, another columnar conifer. **Five silhouette
  classes on one bank.** This is the single most damaging S-1 frame in the library.

### 3.5 Build spec — abolition

**A. Decals (J-1, J-2, D-3)**

```
ground_kit.build_patch_field(..., yaw_max=14.0)        →  yaw_max=0.0
ground_kit.build_stain_field  yaw = ±22° on free blots →  yaw = 0.0 for every kind
```
- `build_patch_field`: keep the rectangle (real 아스팔트 절삭·덧씌우기 patches **are** saw-cut
  rectangles), but **align it to the pavement module axis**, not to nothing: take the yaw from the
  profile's `unit_cell` origin/axis where one exists (`ground_kit.py:288-289` already carries the
  per-profile `unit_cell` ledger), else 0. Keep `cutline=False` (W2 F3).
- `build_stain_field`: yaw becomes meaningless once the blot stops being a rectangle → D-1.
- **Registry consequence, free**: `_obb_aabb(...)` collapses to `_box_aabb(...)`, so every patch and
  stain AABB becomes exact rather than an OBB envelope. `frame_budget` B1/B2/B5 numbers will move
  slightly — **expected, not a regression**; the W3 round must re-baseline
  `Docs/reports/regr_*.json` and say so in the round stamp.

**B. Furniture (J-3, J-4, J-5)**

- Delete the `jit_yaw` / `jit_pos` calls at all 18 batch1 sites; **keep the helpers** in
  `batch1_common.py` (they are also the seed source for `jit_tint`, which stays) and mark
  `jit_yaw`/`jit_pos` deprecated in their docstrings with a pointer to this file.
- Replace each yaw literal with the **anchor's own bearing**: a bench against a planter takes the
  planter face bearing; a bench on a verge takes the kerb bearing; a fence takes the opening
  bearing. In practice for the current 33 scenes this is `0 / 90 / 180 / 270` plus scene03's
  meander tangent, which is a *legitimate* alignment (the levee curves, so the furniture on it
  curves with it) and must be preserved.
- Replace each `jit_pos` offset with **0**, and move the *authored* coordinate instead if the
  object then reads badly. The point of the policy is that irregularity must be **authored and
  justified**, never sampled.
- **scene03 `jyaw` (city blocks)**: these are backdrop buildings, not furniture. Real Korean city
  blocks along a river *are* skewed to each other because the street grid is skewed. **Keep, but
  re-author**: set each block's yaw from a stated street-grid bearing (e.g. two blocks share one
  bearing, the third belongs to a different street), not from a ±4° wobble around the frame axis.

**C. Street-tree rows (J-6)** — see E-1 in §5; the pitch and the setback are one rule.

**D. Gate** — the linter (E-4) hard-fails on: any `rotz` on a `patch`/`stain` element; any furniture
prim whose yaw is not within 0.5° of an anchor bearing declared by the scene; any street-tree row
whose successive pitches differ by more than 1 %.

### 3.6 Defect found while enumerating — `build_footprints` AABB mismatch

`ground_kit.py:1071-1075` (jittered `rotz` at `:1072`, AABB at `:1074-1075`) `[measured]`:

```python
kit.B(p, (ox, oy, float(z) + pr - 0.004), (0.27, 0.10, 0.008), mtl,
      rotz=ang + (rng.random() - 0.5) * 12.0)          # prim gets ang ± 6°
elems.append(_elem("footprint", p,
                   _obb_aabb(ox, oy, float(z) + pr - 0.004,
                             0.27, 0.10, 0.008, ang),  # registry gets ang
```

The prim is rotated by `ang ± 6°`; the AABB handed to the element registry uses `ang`. The registry
therefore under-reports the footprint footprint by up to ~10 mm in each axis. Consequence is small
(footprints are `decal=True`, B5 counting only), but it is a **real registry/geometry divergence of
exactly the class `geom_invariance_check` was built to catch, and it is invisible to it** because
both arms produce the same wrong number. J-7 keeps the ±6° (feet really splay) and fixes the AABB
to use the jittered angle. **Owner: whoever touches `ground_kit` first in W3.**

### 3.7 Risk I am obliged to flag — `ori_axis`

`Docs/reports/real_reference_expansion.md` §3.1 measured, over the licence-safe photo set (n=54) and
the then-current renders (n=114) `[stat]` `[measured]`:

| | photos (n=54) | renders (n=114) | uniform expectation |
|---|---|---|---|
| `ori_axis` (share of edge orientations on the 0°/90° axes) | **0.252 ± 0.074** (p90 0.344, **p95 0.371**) | **0.311 ± 0.101** | 0.111 |

Read this two ways, both true:

1. **It supports abolition.** Real Korean scenes measure **2.3× the uniform expectation** — the
   built world *is* orthogonal. The premise behind v5.1 §3 ("axis-parallel reads as CG") is
   quantitatively wrong.
2. **It is a hazard for the W3 round.** Renders are *already* above the photo mean. Removing
   jitter pushes `ori_axis` up further, toward and possibly past the photo **p95 = 0.371**.

Resolution, and it must be written into the W3 spec: the correct source of orientation entropy in a
real frame is **clutter, wear and vegetation**, not rotated furniture. W3 adds exactly that (props
de-proxying R2, midground, decal masks D-1/D-2). **Instrument, do not gate**: measure `ori_axis`
before and after the abolition batch; if the post-batch median exceeds 0.371, that is a signal the
*scene is under-dressed*, not that the furniture should be re-rotated. `ori_axis` stays advisory
(the same report's own ruling: "게이트에는 넣지 말고 보조 지표로 유지하라").

---

## 4. Policy P2 — ONE SPECIES PER ROUTE

### 4.1 The current mixing mechanism, exactly

`scene_common.py:2118-2125` `[measured]`:

```python
VEG_TREES = [
    ("Trees/Elm_Sapling.usd",      3.0867, 4),
    ("Trees/Shumard_Oak.usd",     10.8989, 3),
    ("Trees/Chinese_Juniper.usd",  2.5164, 2),
    ("Trees/White_Pine.usd",       2.35,   1),
    ("Trees/Yellow_Pine.usd",     26.99,   1),
]
```

`scene_common.py:2441-2444`, inside `build_tree`:

```python
if LOOK_GEO and veg_available():
    pool = [t for t in veg_pool() for _ in range(t[2])]      # 4+3+2+1+1 = 11 slots
    rel, native, _ = pool[rnd.randrange(len(pool))]          # ← per-TREE draw
```

`rnd` is seeded from the tree's own `(cx, cy)` (`:2438-2439`), so the draw is deterministic **and
independent per tree**. There is **no scene parameter, no route parameter, no species argument** in
the signature (`:2417-2420`). Every one of the **25 live `build_tree` call sites across 17 scenes**
(24 via `sc.`/`bc.`, plus `build_planter`'s internal call at `scene_common.py:2564`) `[measured]`
therefore gets an i.i.d. draw from the same 11-slot pool — and each call site usually sits inside a
loop over a coordinate list, so the number of *trees* is far higher (scene06 alone places 20).

Probability that scene06's 20-tree verge row is monospecific under the current pool:
`Σ_i (w_i/11)^20 ≈ (4/11)^20 = 1.4×10⁻⁹` `[derived]`. It is not a tuning problem; it is a missing
concept.

**Identical defect in the shrub layer**: `place_shrubs` (`scene_common.py:2796`, draw at `:2819`)
does `avail[rnd.randrange(len(avail))]` per shrub, so one flower bed mixes Privet, Boxwood, Juniper
and Rhododendron. `SHRUB_HEDGE` / `SHRUB_ORNAMENT` (`:2280,2292`) narrow the pool but never to one.

**Never-wired inventory** `[measured]` — `assets/veg_manifest_w2.json` carries **17 PASS rows**;
`grep` for each name across all `*.py` excluding the downloader returns **0 hits** for
`Fraxinus`, `Gray_Birch`, `Lombardy_Poplar`, `Douglas_Fir`, `Colorado_Spruce`, `Scarlet_Oak`,
`Black_Oak`, `Holly`, `Yew`, `Cedar_Shrub`, `Switchgrass`, `Grass_Short_*`. **11 verified assets,
615 MB on disk, are dead weight.** Meanwhile `White_Pine` and `Yellow_Pine` — the two still wired —
are *not* in the W2 manifest's PASS list, and `White_Pine` carries a known uncorrected `zmin −0.351`
defect noted in the table's own comment.

### 4.2 Real-sample evidence

Statute: §3.3 above — 조례 제7조1호라 *"같은 노선과 도로 양측에는 같은 수종"* `[law]`; 시행규칙
*"노선별·구간별로 수관의 모양과 높이를 일정하게 유도"* `[law]`; 산림청 고시 *"동일 노선 동일 수종 권장"*
`[law]`. The 시행규칙 clause is the sharper one for us: it targets **crown shape and height
uniformity**, which is precisely what a random oak/juniper/pine mix destroys.

Photographs `[photo]`:

| claim | population | n | URL |
|---|---|---|---|
| a Korean tree route is one species, one crown form, one pitch | `Category:Damyang Metasequoia Road` | **12** | https://commons.wikimedia.org/wiki/Category:Damyang_Metasequoia_Road |
| 〃 (second, non-tourist site) | `Category:Metasequoia glyptostroboides in South Korea` (incl. `Two metasequoias in Dongil-ro.jpg`) | 3 + the 12 above | https://commons.wikimedia.org/wiki/Category:Metasequoia_glyptostroboides_in_South_Korea |
| ordinary urban sidewalk tree file, single species | `Category:Sidewalks in South Korea` — `Row of trees on sidewalk.jpg` (already in repo as `wc047_cc0_a694ef_…`), Okcheon Jungang-ro ×3, Cheonan Yeonamyulgeum-ro, Jeongwangsingil-ro | **≥6** | https://commons.wikimedia.org/wiki/Category:Sidewalks_in_South_Korea |
| Seoul statistics: the route mix is dominated by a few species | ginkgo 35.8 % + London plane 20.9 % of 306,313 Seoul street trees (2019), already carried as a comment at `scene_common.py:2107-2109` | — | in repo `[stat]` |

**Gap I could not close**: no Commons category for 은행나무 가로수 as a *route* returned ≥5 usable
frames this session (`incategory:"Trees in South Korea"` returns mostly single specimen trees).
T-1 must harvest one for the `street_arterial` archetype panel — candidate queries in §7.4.

### 4.3 Build spec

**S-3 — replace the global pool with a species table**

```python
# scene_common.py — replaces VEG_TREES as the source of truth
VEG_SPECIES = {
    # key                 rel path                        native_h(zmax)  role
    "elm":       ("Trees/Elm_Sapling.usd",      3.0867, "street_nearfield"),
    "oak_pin":   ("Trees/Shumard_Oak.usd",     10.8989, "street_broadleaf"),
    "ash":       ("Trees/Fraxinus.usd",         5.3408, "street_broadleaf"),
    "birch":     ("Trees/Gray_Birch.usd",       3.3294, "park_apartment"),
    "poplar":    ("Trees/Lombardy_Poplar.usd", 13.6709, "riverside"),
    "juniper":   ("Trees/Chinese_Juniper.usd",  2.5164, "temple_office_evergreen"),
    "fir":       ("Trees/Douglas_Fir.usd",      6.0263, "temple_mountain_conifer"),
    "oak_red":   ("Trees/Scarlet_Oak.usd",     12.4089, "park_broadleaf"),
    "oak_black": ("Trees/Black_Oak.usd",       19.7389, "far_background_broadleaf"),
    "spruce":    ("Trees/Colorado_Spruce.usd",  3.8713, "far_background_conifer"),
}
```
All ten rows are `verdict: PASS` in `assets/veg_manifest_w2.json` with measured `zmax`, `tri_unique`
and UV-sampled foliage hue `[measured]`. `White_Pine` / `Yellow_Pine` are **retired** from the
street/park roles (not deleted — they may serve a backdrop belt after a pixel re-check).

Signature change, one keyword, backward-compatible:
```python
def build_tree(stage, prefix, cx, cy, gz, wood_mtl, canopy_a_mtl, canopy_b_mtl,
               ..., species=None):     # None → scene default, resolved from SCENE_SPECIES
```
and a module-level `SCENE_SPECIES` map keyed by the scene's `ROOT` token, so the 25 call sites need
**no edit** unless a scene has two legitimately different routes (6 do — the `▸` rows below).

**S-1 — per-scene / per-route assignment table (proposal)**

Rule: **one species per route**. A scene may declare a second species only for a *physically
separate* planting that is not the same route — a mountain backdrop belt, a far-bank woodland — and
the table records which. Backdrop belts are marked `▸`.

| scene | identity | route species | backdrop belt `▸` | why this species |
|---|---|---|---|---|
| 01 | 캠퍼스 계단 | **elm** (느티나무 대용) | — | zelkova is the canonical Korean campus/plaza tree; 3.09 m suits the 3.0 m planters and the h0.3 near field |
| 03 | 하천 제방 | **poplar** (양버들) | ▸ oak_black (far bank) | 양버들/미루나무 is the signature Korean riverbank silhouette; kills the 5-silhouette frame |
| 04 | 공원 침목길 | **oak_red** | ▸ oak_black | park broadleaf stand |
| 05 | 야외공연장 | **ash** (이팝나무 대용) | — | civic plaza standard since the 2000s |
| 06 | 보행육교 나선 | **oak_pin** (대왕참나무 대용) | — | the library's flagship arterial street row (20 trees, 2 verges) |
| 07 | 산사 돌계단 | **juniper** (향나무) | ▸ fir (산지 침엽) | 향나무 is the temple/관공서 landscaping species; the mountain behind is a different stand |
| 09 | 호수공원 수변 | **birch** | ▸ oak_black | lake-park amenity planting |
| 10 | 공원 데크 갈지자 | **oak_red** | ▸ oak_black (hill_trees) | same park family as 04 |
| 11 | 보도육교 | **ash** | ▸ (existing TreeBlob band → R2 B2c midground) | arterial sidewalk file, 16 trees on 2 strips |
| 12 | 수변 데크길 | **poplar** | — | riverside, matches 03/17 |
| 13 | 지하주차 진입부 | **birch** | — | apartment-complex landscaping |
| 14 | 착시 대계단 | **ash** | — | civic |
| 17 | 한강 제방 | **poplar** | ▸ oak_black | Han river levee |
| C2 | 낙엽 매몰 계단 | **oak_red** | — | **must match the debris asset**: `assets/vegetation/Debris/` ships `oakfall1/2.usd` `[measured]` — an oak leaf blanket under an oak |
| D3 | 노변 배수로 | **oak_pin** | — | rural arterial verge |
| N4 | 완경사 램프 | **elm** | — | near-field, ramp corridor |
| N5 | 플러시 그레이팅 | **ash** | — | street trees A/B/C on one verge |

Scenes with no `build_tree` call (02, 08, 15, 16, 18, 19, 20, 21, C1, C4, D1, D2, D4, N1, N2, N3)
are unaffected by S-1 but several are affected by S-2 (hedges/planters).

**S-2 — shrubs, one species per bed / per band**

| role | asset | verified | use |
|---|---|---|---|
| clipped evergreen hedge | `Shrub/Holly.usd` (h 1.44) or `Privet.usd` (h 1.11) | manifest PASS / in-repo | **one species per continuous band**, never mixed inside one band |
| formal planter accent | `Shrub/Yew.usd` (h 0.71) | PASS | one per bed |
| narrow border | `Shrub/Cedar_Shrub.usd` (h 0.88) | PASS | one per border run |
| verge turf patch | `Shrub/Grass_Short_A/B.usd` | PASS | scatter — mixing allowed (it is turf, not planting) |
| edge weed | `Shrub/Grass_Short_C.usd` (1,598 tri) | PASS | R2 A1 — scatter, mixing allowed |
| riparian band | `Shrub/Switchgrass.usd` | PASS | one species per band |

Change: `place_shrubs(..., pool=...)` gains `species=` (single key) and the `randrange` at `:2819`
is removed. `Rhododendron` keeps its `_deactivate_seasonal` treatment and is only admissible as a
**single-species** ornament bed.

**S-4 — variation *within* the species (this is what replaces the mixing)**

`build_tree` already varies form deterministically; the spec keeps all of it and adds a floor:

| lever | current | W3 spec |
|---|---|---|
| total height | `trunk_h × 1.60 × U(0.92,1.08)` (`:2449`) | **keep** — ±8 % is the documented scale-anchor budget |
| statutory floor | none | street-tree scenes: **≥3.5 m** and trunk Ø ≥0.10 m at breast height (서울 시행규칙) `[law]`; park/temple scenes exempt |
| lean | `U(0°,4°)` (`:2478`) | **keep** for park/riverside; **cap at 1.5°** on street rows (staked nursery stock stands straight) `[assumed — needs photo check, T-1]` |
| crown bearing | `U(0,360)` (`:2456`) | **keep** |
| canopy blobs | procedural fallback only | unchanged |

Honest limitation: `add_vegetation` applies **one uniform scale**, so height and trunk diameter
cannot be varied independently — a ±8 % height instance is also ±8 % in DBH `[measured]`. That is
acceptable (isometric) and preserves the height cue, but it means "same species, different age" is
**not** expressible with the current pipeline. Do not promise it.

**Budget** `[measured, from `veg_manifest_w2.json`]`: `Colorado_Spruce` is `tri_effective`
**15,597,637** — far-background instanced use **only**, never in a route. `Black_Oak` 2.95 M,
`Scarlet_Oak` 2.23 M, `Shumard_Oak` 4.55 M are all PointInstancer-expanded figures; the per-scene
instancing path (`SetInstanceable(True)` on `{prefix}/Veg/Asset`, `:2468`) already shares prototypes,
so a 20-tree monospecific row costs **one** prototype instead of the current ~4. **One species per
route is a memory win, not a cost.**

---

## 5. Policy P3 — PROP-EDGE-DISTANCE RULE TABLE + CPU GATE

### 5.1 Why one global table

R2 handled props object-by-object (36 rows) and the A-agent's scene03 work handles one scene. The
failure mode both miss is the *relationship*: a bench that is a correct bench, in a correct place
relative to nothing. The eyes round names it directly — scene11's sign post standing mid-plaza,
scene01's benches drifting off their planter faces. A single rule table plus a machine check is the
only way this stays fixed after the next 20 edits.

### 5.2 The rule table

Reference datum: **the walking-zone edge** = the boundary of the 보행안전공간 (clear walking band).
On a sidewalk with a carriageway, the other datum is the **보도·차도 경계선** (kerb line).

| # | prop | rule | value | basis |
|---|---|---|---|---|
| R1 | 가로수 (street tree) | lateral: trunk centre from kerb line | **≥ 1.00 m** | 산림청 고시 2-3(6)(가)1) `[law]` |
| R2 | 가로수 | longitudinal pitch, **constant** along a route | **6–8 m** (Seoul 조례 제7조1가), 4–8 m (고시) → use **7.0 m** default | `[law]` |
| R3 | 가로수 | planting form | **row parallel to the road alignment**, no yaw, no lateral offset | 조례 제7조1나 · 고시 (나) `[law]` |
| R4 | 가로수 (no sidewalk) | from the shoulder end | **≥ 2.0 m** (conditionally 1–2 m) | 고시 2-3(6)(가)2) `[law]` |
| R5 | 수목보호판 | opening min width, all shapes; cover offset from grade | **1.5 m**; **≥ 5 cm** below (≤5 cm where vehicles) | 고시 2-3(5)(가) `[law]` |
| R6 | 볼라드 | height / diameter / pitch / front tactile | **0.8–1.0 m** / **Ø0.1–0.2 m** / **1.5 m** / 0.3 m 점형블록 | 교통약자법 시행규칙 별표2 제7호 `[law]` |
| R7 | 볼라드 | position | **on the 보도·차도 경계 line**, axis-locked to it; only at vehicle-entry points | 별표2 + v5.1 §2 `[law]` |
| R8 | any 노상시설 | occupied width must not eat the effective walking width; furniture stands in a **dedicated 노상시설대 added on top of it**, not in it | effective width **≥ 2.0 m** (national); **1.5 m** only as the constrained-condition floor (Seoul manual) | 「도로의 구조·시설 기준에 관한 규칙」 제16조 `[law — via A's G-3]`; obstacle widths from 보도 지침 표2.2 `[law]` |
| R9 | 승차대 ↔ neighbouring 보도 시설물 | separation | **≥ 1.5 m** | in-repo `korean_urban_backdrop.md` §, source re-read `[law]` |
| R10 | 점형블록 ↔ 연단 | offset | **0.30 m** | 교통약자법 `[law]` |

Obstacle widths, 「보도 설치 및 관리 지침」(국토부 예규 제321호) 표2.2 `[law]` (in-repo kpg §3.1, source
`https://www.codil.or.kr/filebank/moctroadguide/LS/CIKCLS121103/CIKCLS121103.pdf` p.19):

| 노상시설 | 장애 폭 (m) | 노상시설 | 장애 폭 (m) |
|---|---|---|---|
| 가로등 | 0.8–1.0 | 휴지통 | 0.9 |
| 교통신호등 지주 | 0.9–1.2 | 지하철환기구 | 0.8 |
| 교통안전표지판 | 0.6–1.8 | **가로수** | **0.9–1.2** |
| 우체통 | 1.0–1.1 | **가로수보호지주** | **1.5** |
| 공중전화박스 | 1.2 | 신문가판대 | 1.2–2.0 |

**Derived setback rule (R8 made computable)** `[derived]`:
> `setback_far_edge ≤ sidewalk_width − 1.5 m` and `setback_near_edge ≥ 0`, where the prop's
> occupied width is the 표2.2 value. For a 3.0 m sidewalk this puts a 0.9 m 휴지통 entirely inside a
> 1.5 m 시설물대 hard against the kerb, which is what the photographs show.

**Rows the statutes do not fix — these are the `[근거 없음]` rows the user's bar demands photos for:**

| # | prop | what is missing | measurement task |
|---|---|---|---|
| M1 | 벤치 | seat back-face offset from the walking edge; seat axis convention | measure on ≥5 Pyeongchon/오금공원 frames |
| M2 | 가로등 | pole-centre offset from the kerb (only the 0.8–1.0 *occupancy* is legislated) | ≥5 `Street lights in South Korea` frames |
| M3 | 휴지통 | offset and whether it pairs with a lamp/bench | ≥5 `Waste containers in South Korea` frames |
| M4 | 플랜터 / 화단 | curb face vs paving module registration | ≥5 sidewalk frames |
| M5 | 안내표지 지주 | post offset; panel clear height over a walking surface | ≥5 `Information boards in South Korea` frames |
| M6 | 벤치 ↔ 가로수 | do benches sit *between* trees, on the tree line, or offset? (v5.1's "anchor" idea, unverified) | ≥5 park frames |

Scale references available in the photos for pixel measurement, all standard and already used by
the project: 보도블록 300×300 or 200×100 mm, 점자블록 300×300 mm, 볼라드 Ø100–200 mm, 맨홀 Ø648 mm
(보도용) `[law — kpg §3.2]`.

### 5.3 Build spec — the linter (E-4)

**Reuse, do not invent.** `scripts/geom_invariance_check.py` already runs every scene's `main()`
**with no GPU** by substituting a fake `pxr` whose `UsdGeom` is a recording stub: it captures
`Define()` per prim path and every `AddTranslateOp/AddRotateZOp/AddScaleOp().Set(...)` into
`_PRIMS[path]["ops"]`, plus `size/radius/height/extent` into `["attrs"]`
(`scripts/geom_invariance_check.py:130-240`) `[measured]`. That is precisely a
(path → world position, yaw, extent) table — everything the rule table needs.

```
scripts/placement_lint.py            # new; imports the harness from geom_invariance_check
  --scenes scene01,...               # default: all 33
  --rules  Docs/briefs/placement_rules_v1.yaml
  exit 0 = clean · 1 = violation · 2 = harness error
```

Inputs the scenes must expose (small, additive, no geometry change):
```python
PLACEMENT = dict(
    walk_edges = [((x0,y0),(x1,y1)), ...],   # walking-zone boundary polylines
    kerb_lines = [((x0,y0),(x1,y1)), ...],   # 보도·차도 경계
    anchors    = {"planterA": dict(face_bearing_deg=0.0, ...), ...},
    routes     = {"verge_S": dict(pts=[...], species="oak_pin", pitch_m=7.0), ...},
)
```

Checks (hard = exit 1):

| check | rule | hard? |
|---|---|---|
| P-1 tree lateral offset from `kerb_lines` ≥ 1.00 m | R1 | hard |
| P-2 route pitch constant within 1 %, in [6.0, 8.0] m | R2 | hard |
| P-3 route bearing = kerb bearing ± 0.5°; per-tree yaw offset = 0 | R3 | hard |
| P-4 one species per `routes[*]` | S-1 | hard |
| P-5 free walk width ≥ 1.5 m after subtracting 표2.2 occupancy | R8 | hard |
| P-6 bollard pitch 1.5 ± 0.1 m, Ø∈[0.1,0.2], h∈[0.8,1.0], yaw = kerb bearing | R6/R7 | hard |
| P-7 furniture yaw ∈ {anchor bearings} ± 0.5° | J-3/J-5 | hard |
| P-8 no `rotz ≠ 0` on any `patch`/`stain` GKit element | J-1/J-2 | hard |
| P-9 bench/lamp/bin setback within the measured band | M1–M6 | **warn until §5.4 lands** |
| P-10 `jitter=` kwarg > 0 anywhere in scene code | J-11 | hard |

**Relationship to `frame_budget`**: do **not** extend it. `frame_budget` reads
`plan["elements"]`, which is the ground-kit element registry only — props are scene-owned prims and
are structurally absent from it (`ground_kit.py:2080-2100`, `_elem` at `:526`) `[measured]`. The two
tools answer different questions (pixel occupancy vs geometric legality) and should stay separate;
`placement_lint` runs in the same pre-flight slot as `geom_invariance_check`.

### 5.4 Photo panels backing §5.2

| rows | population | n | URL |
|---|---|---|---|
| R1–R4, R8, M2–M4 | `Category:Sidewalks in South Korea` | 18 | https://commons.wikimedia.org/wiki/Category:Sidewalks_in_South_Korea |
| M1, M6 | `Category:Benches in South Korea` | 25 | https://commons.wikimedia.org/wiki/Category:Benches_in_South_Korea |
| M2, M3, M5 | `Category:Street furniture in South Korea` + subcats (`Street lights…`, `Waste containers…`, `Information boards…`) | 14 + 22 subcats | https://commons.wikimedia.org/wiki/Category:Street_furniture_in_South_Korea |
| R2, R3 | `Category:Damyang Metasequoia Road` | 12 | https://commons.wikimedia.org/wiki/Category:Damyang_Metasequoia_Road |
| all, in-repo | `Docs/reference_photos/expanded/` (Streets in Seoul 5, Sidewalks 7, Insadong 6, Bukchon 5, Jongno KOGL-1 2) | 54 | in repo, `LICENSES.csv` |
| R6, R7, R10 | **`[근거 없음]`** — `Category:Bollards in South Korea` returns HTTP 404 `[measured]` | 0 | must be harvested by keyword; see §7.4 |

---

## 6. Policy P4 — DECAL MASKS

### 6.1 The defect

Every ground decal in the library is an **axis-aligned box prim 8 mm thick** with a bound material
(`ground_kit.py:1029, 733, 1102, 1130, 1166`) `[measured]`. Its silhouette is therefore a rectangle,
always. W2-D's F3 batch attacked the *symptoms* (killed the cut-line stroke, lowered `proud` to kill
the rim shadow, added the yaw) but not the cause. `tonglam_v2.md` §2.13-2 lists the survivors:
"leaf/soil decal rectangles with razor edges (03/07/10/D3, +C2 mass edges)"; §2.12 records the C2
leaf mass as "a perfect rectangle from the air". The user has now promoted the deferred mask tooling
to a W3 priority.

Scope `[measured, AST-exec of `GROUND_PROFILES`]`: `stain` appears in **19 of 19** profiles → every
scene; `patch` in **10 of 19** (`plaza_granite, plaza_water, sidewalk_block, street_asphalt,
alley_concrete, roof_membrane, ramp_parking, ramp_road, levee_paved, verge_rural`), n = 2–4 each.

### 6.2 What the real thing looks like — and the split it forces

| decal kind | real Korean form | W3 treatment |
|---|---|---|
| 아스팔트 절삭·덧씌우기 patch | **saw-cut rectangle or trapezoid, aligned to the carriageway**, tonal step at the lip | **keep the rectangle, kill the yaw** (D-3) — the ±14° made it *less* real, not more |
| 유류·물·때 blot (`dirt/water/oil/gum/drip/efflorescence`) | irregular, lobed, no straight edge anywhere | **N-gon mask** (D-1) |
| 낙엽·토사 carpet | drift shape — accumulates against kerbs, risers, walls; feathers out on the open side | **N-gon mask + one-sided scatter feather** (D-2) |
| grime band / tire track / wear lane / edge litter | genuinely straight and directional | **unchanged** — these already take a centreline bearing |

### 6.3 Build spec

**D-1 — `build_blot()`, a new ground_kit primitive (geometry, no texture pipeline)**

```python
def build_blot(kit, path, cx, cy, rx, ry, mtl, *, n=16, rough=0.35, seed=0, z, proud):
    """Irregular flat lobe. A closed N-gon whose radii are r_i = r·(1+U(−rough,rough)),
    once-smoothed (r_i ← (r_{i−1}+2r_i+r_{i+1})/4) so no vertex spikes. 1 Mesh prim."""
```
- **1 prim**, same as today → no budget change, `frame_budget` B-row arithmetic unaffected in count.
- AABB = the polygon bbox, exact.
- Deterministic from `(path, seed)` via the existing `det_rng`.
- **No alpha, no opacity, no texture** — chosen deliberately: `add_vegetation`'s own comment records
  that `enable_opacity` breaks the vegetation assets (ZZ §10.2), and an alpha-masked ground quad
  would add a sorting surface at grazing angles, which is exactly the viewpoint the dataset lives at.
- Rejected alternative: procedural mask texture. It costs a texture-generation step, a UV convention
  and an alpha path, for a silhouette an N-gon already gives.

**D-2 — carpet edges**
- Replace the carpet rectangle with `build_blot` at low `rough` (0.15–0.20) and high `n` (24).
- Add a **feather ring**: reuse `place_scatter` to lay individual leaf cards in a band straddling
  the mask boundary (inner 0.3 m / outer 0.5 m), density falling to zero outward. The leaf assets
  are already on disk (`assets/vegetation/Debris/{oakfall1,oakfall2,maplefall1,fallcluster1,2}.usd`)
  and the W2 leaf-globalisation work already made 1,784 cards affordable
  (`leaf_globalization_budget_v2.md`).
- **Drift bias** (this is the part that makes it read as real): the mask centroid must be pulled
  toward the nearest vertical obstruction (kerb, riser, wall) and the mask elongated along it.
  Leaves and soil accumulate *at* things. A leaf carpet floating in the middle of an open DG
  forecourt is wrong at any silhouette.
- scene C2 specifically: the buried risers currently render the leaf texture as "compressed-leaf
  laminate print" on vertical faces (`tonglam_v2` §2.12) — that is a **separate** binding problem
  (vertical faces should not receive the plan-view leaf texture) and must be listed in the same work
  package or C2 will still fail on the same crop.

**D-3 — patch axis lock**: yaw from the profile's `unit_cell` axis where present
(`ground_kit.py:288-289` carries `profile → (cell_m, (ox,oy), source)`), else 0.

**Photo evidence** `[photo]`: patch shape and asphalt repair geometry are visible in
`Category:Sidewalks in South Korea` (Okcheon Jungang-ro ×3, National Route 4 Okcheon-ro) and in the
in-repo set (`wc041 Jeongwangsingil-ro`, `wc042/043 Okcheon Bridge`, `wc010 Hwaseong-ro`) — **n ≥ 7**.
Leaf-drift shape: **`[근거 없음]` this session** — needs an autumn-street harvest (§7.4). Do not
build D-2's drift bias without it; build D-1/D-3 first, they are already evidenced.

---

## 7. Policy P5 — 통람 v3 criteria upgrade

### 7.1 What changes from v2

v2's bar was "reads as a real Korean place at the robot viewpoint", judged from the frames alone, and
it produced PASS 4 / FLAG 23 / FAIL 6. v3 keeps the method (h0.3 cuts first, whole frame, then the
beauty cut) and adds **the panel**: every verdict is rendered next to 3–5 real photographs of the
same archetype, and the verdict is written against them, not against the judge's memory.

### 7.2 Archetype panels — `Docs/reference_photos/w3/<archetype>/`

33 scenes collapse to 12 archetypes. Each panel directory contains `SOURCES.md` (a URL list with
licence, author, and *what to look at*), and thumbnails **only for CC0 / CC BY / KOGL Type 1** —
BY-SA stays URL-only so the repo does not acquire a share-alike obligation. This continues the rule
already established in `Docs/reference_photos/real_set_safe.txt` `[measured]`.

| archetype | scenes | seed population (this session) | n |
|---|---|---|---|
| `plaza_civic` | 01 · 08 · 14 · 20 · 21 · N1 · N3 | in-repo Gwanghwamun, Seoullo 7017, Jongno KOGL ×2, Korean War Veterans Plaza | 5 |
| `street_arterial` | 06 · 11 · N5 | `Category:Sidewalks in South Korea` | 18 |
| `sidewalk_local` | 13 · N2 · N4 · D3 | 〃 + in-repo Jeongwangsingil-ro, Cheonan | 18 |
| `river_levee` | 03 · 12 · 17 | **`[근거 없음]`** — needs 한강공원 harvest | 0 |
| `lake_park` | 09 | in-repo Cheonggyecheon; needs 1 more | 1 |
| `park_trail` | 04 · 10 · C2 | `Category:Benches in South Korea` (오금공원, 대현산공원, Pyeongchon) | 12 |
| `amphitheatre` | 05 | **`[근거 없음]`** | 0 |
| `temple_precinct` | 07 | in-repo Changdeokgung; needs 3 more | 1 |
| `underpass_entry` | 02 · 16 | **`[근거 없음]`** | 0 |
| `alley_hillside` | 15 · 18 | in-repo Bukchon ×5, Insadong ×6, Gamcheon ×2 | 13 |
| `rooftop` | 19 | **`[근거 없음]`** | 0 |
| `industrial_transit` | D1 · D2 · D4 | in-repo `Dorasan Station.jpg` candidate; needs 4 | 1 |

**5 of 12 archetypes have no panel.** T-1 is therefore a real task, not a formality, and it gates
the round: **no scene may be judged v3 without its panel.**

### 7.3 Side-by-side protocol (T-2)

1. **Pair**: the scene's `pt_noon_preset_h0.3_d5` cut against the panel photo whose ground-plane
   share is closest (the panel records each photo's ground share once, at harvest).
2. **Crop both** to the bottom 2/3 (sky excluded) — the same convention
   `real_reference_expansion.md` §7 already uses for the numeric metrics `[measured]`.
3. **Compare on six named axes, in this order** (stop at the first FAIL; record it):
   `species & silhouette` → `alignment & pitch` → `setback & free width` → `surface content`
   → `edge & boundary treatment` → `tone`.
4. **Write the verdict as a sentence naming the photo**: "the tree row matches
   `Damyang_Metasequoia_Road_3.JPG` in pitch and species but not in trunk clear height".
   A verdict with no photo name is not a v3 verdict.
5. **Numeric assist, advisory only** (T-4), from the n=54 photo distribution `[stat]`:
   `slope` −2.03 ± 0.18 · `grad_k` 10.8 ± 5.3 · `flat_pct` 10.2 ± 8.8 · `flat_gnd` 3.9 ± 5.0 ·
   `ori_axis` p95 **0.371** (alarm line). **Do not gate on `sat_mu`/`sat_sd`/`chroma_sd`** — the
   same report measured their separability at 0.098/0.093/0.138, i.e. none.

### 7.4 "Identical to sample" checklist (T-3)

Per scene type; every line is a yes/no with a photo reference. Any **no** = FAIL.

**All scenes**
- [ ] Every object class visible in the panel photos is present in the frame, and no class is present that is absent from all panel photos ("no invented objects").
- [ ] No built object is rotated off its anchor's bearing.
- [ ] No decal has a straight edge that is not a construction joint, a saw cut, or a kerb.
- [ ] Surfaces the panel shows as worn are worn; surfaces it shows as clean are clean.

**Scenes with a tree route** (01·03·04·05·06·07·09·10·11·12·13·14·17·C2·D3·N4·N5)
- [ ] **One species** on the route; a second species only if it is a declared separate belt.
- [ ] Pitch constant, 6–8 m, gaps only at crossings/driveways/entrances.
- [ ] Trunk centres ≥1 m from the kerb line, on one straight (or one smoothly curving) line.
- [ ] 수목보호판 present where the tree stands in paving: ≥1.5 m opening, cover ≥5 cm below grade.
- [ ] Street-tree height ≥3.5 m, trunk Ø ≥0.10 m.

**Scenes with a sidewalk** (06·11·13·D3·N2·N4·N5·16·02)
- [ ] Free walking band ≥1.5 m after every 노상시설.
- [ ] Furniture forms a **single line** parallel to the kerb, not a scatter.
- [ ] Bollards only where a vehicle could enter; pitch 1.5 m; Ø0.1–0.2 m; h0.8–1.0 m.

**Scenes with a plaza** (01·05·08·14·20·21·N1·N3)
- [ ] Benches sit against an edge (planter, wall, level change), seat axis parallel to it.
- [ ] The central axis is empty (v5.1 씬21 ruling) unless the panel shows otherwise.

**Scenes with water** (03·09·12·17)
- [ ] Bank vegetation is one species along the reach.
- [ ] Water is not a mirror plane (carried W3 item, `tonglam_v2` §4-5).

**Scenes with a stair** (all hazard scenes)
- [ ] Nosing, handrail and tactile treatment match the panel's era vocabulary (`era_consistency_survey_v1.md` §6.2).

### 7.5 Harvest tooling (blocking dependency)

`real_reference_expansion.md` §7 records that the Commons harvest pipeline **was run in a scratchpad
and never committed** `[measured]`. T-1 therefore needs it rebuilt as
`scripts/harvest_refs.py` (Commons API `list=categorymembers` + `prop=imageinfo|extmetadata`,
licence whitelist regex, `LICENSES.csv` writer — the CSV schema already exists and should be reused
verbatim: `file,license,license_url,author,credit,date,commons_page,original_url,orig_w,orig_h,harvest_query,title`).
Queries to run for the 5 empty archetypes and the 3 `[근거 없음]` rule rows:
`cat:Han River Parks` variants, `cat:Hangang`, `search:한강공원 자전거도로`, `cat:Amphitheatres in South Korea`,
`search:Korea underpass entrance stairs`, `cat:Rooftops in South Korea`, `search:bollard Korea sidewalk`,
`search:Korea autumn leaves street kerb`, `cat:Streets in Seoul` (deeper page), `cat:Ginkgo biloba` ∩ Korea.

---

## 8. Dependencies, sequencing, and conflicts

| # | dependency | detail |
|---|---|---|
| 1 | **T-1 gates everything judged** | 5 of 12 archetypes have no panel. Harvest first; it is CPU/network only and can run in parallel with code work. |
| 2 | **E-4 (linter) before J-* and E-*** | the linter is what makes the abolition permanent. Building it first also means the abolition batch can be verified without a render. |
| 3 | **S-3 before S-1** | the species table must exist before per-scene assignment. |
| 4 | **J-1/J-2/D-3 land together** | they touch the same two `ground_kit` builders; splitting them means two AABB re-baselines. |
| 5 | **Re-baseline after the decal batch** | `_obb_aabb → _box_aabb` changes B1/B2/B5 inputs. `regr_260730_w2d_fix.json` is no longer the comparison baseline; stamp the new one. |
| 6 | **Shared-module freeze conflict** | `ground_kit.py`, `scene_common.py` and `batch1_common.py` are all touched. STATUS 규율 forbids editing shared modules during measurement. Sequence: linter → ground_kit batch → render → scene_common batch → render. |
| 7 | **Collision with R2 work packages** | R2's C1 (bench rebuild), C2 (streetlight), C5 (planter) rebuild the *same prims* J-3/J-4/J-5 re-orient. **Merge them**: rebuild and re-orient in one edit per prop class, or the second pass will re-introduce the yaw from a stale template. |
| 8 | **Collision with R2 B1b/B2a** | the shrub/hedge de-proxying supplies the assets S-2 assigns. S-2 must consume R2's output, not run first. |
| 9 | **R1 §6.5 correction is live** | RT refuted the `+7.904` Z row; if the urban downloader lands in W3, it must carry R3's correction. Not this file's scope, but it shares the W3 window. |
| 10 | **Tactile HOLD is untouched** | RT corrected the count to **12 ON of 42** (C4 6 + N5 6). Nothing in this file changes it; the checklist line above is written as "matches the panel", not "must be present". |
| 11 | **σ_LF carry-over** | 9/33 passing. The decal masks and one-species routes change ground and midground content; expect σ_LF movement in both directions. Do not attribute it to the lighting work. |
| 12 | **Agent A's `w3_intake_01_05.md`** | landed mid-session; reconciled in §0.1. Its G-3 is the 01–05 instance of §5.2's table and supplies R8's primary statute and M2's interim value. **Sequencing**: A's G-1 defaults change lands first (it is a two-module edit that everything else is written against); this file's linter (E-4) must exist before it, so that the defaults change is verified without a render. Resolve the two §0.1 discrepancies before freezing the execution spec. |

---

## 9. Limitations — what this file does NOT establish

1. **I viewed 6 of the ~450 cuts** in `260730_w2d_fix` (scene01·03·06·07·10·11, one cut each). The
   jitter/species/decal findings are *demonstrated* on those frames, not surveyed across the round.
   A full per-scene visual pass belongs to the 통람 v3 round, not to intake.
2. **No setback in §5.2 rows M1–M6 has been pixel-measured.** I identified the photo populations and
   the scale references; the measurement itself is a W3 task. Any number invented before that
   measurement violates the user's bar as surely as the jitter did.
3. **`build_tree`'s street-row lean cap (1.5°) is `[assumed]`.** It sounds right for staked nursery
   stock and I found no source. It must be photo-checked or dropped.
4. **The per-scene species assignments in §4.3 are a proposal, not a measurement.** Each is justified
   by Korean planting practice and by the asset's verified role in `veg_manifest_w2.json`, but only
   03/07/12/17 (riverside poplar, temple juniper) and C2 (oak, forced by the debris asset) rest on
   something stronger than judgment. The supervisor should ratify the table, or T-1's panels should
   settle it per archetype.
5. **I did not run any render, any Isaac process, or any GPU work**, and did not execute
   `geom_invariance_check` or `placement_lint` (the latter does not exist). The harness capability
   claim in §5.3 is from **reading** `scripts/geom_invariance_check.py:125-240`, not from running it.
6. **`SCENE_PLANS` would not AST-exec** (it references `_RAMP13_PROFILE`, defined outside the literal),
   so the patch/stain scene lists in §6.1 are stated at **profile** granularity (10 of 19 / 19 of 19).
   The scene expansion is mechanical and R2 has already demonstrated the method.
7. **`Category:Bollards in South Korea` does not exist** (HTTP 404, verified twice) `[measured]`, so
   R6/R7's photo backing is currently zero. The statutes are solid; the photographs are not there yet.
8. **Licence posture of the new panels**: I checked only that the two new Commons categories exist
   and enumerated their files. **Per-file licence verification has not been done** — that is part of
   T-1's harvester, which must apply the same whitelist that produced the clean 54-row ledger.
9. **Agent A's file was spot-checked, not verified.** I re-opened the 7 code lines I adopted in
   §0.1 and confirmed each `[measured]`; I did **not** re-execute A's statute fetches, its
   per-scene rows for 01–05, or its G-4/G-5/G-6. Those remain A's claims under A's tags. The one
   number I actively dispute is the patch profile count (§0.1 discrepancy 1).
10. **The `.gitignore` edit and `assets/{download,verify}_urban.py` in the working tree are not
   mine.** I wrote exactly one file and made no code, asset or configuration change.

---

## 10. Open questions for the supervisor

1. **Ratify the §4.3 species table?** Or defer each scene's species to its T-1 archetype panel? The
   second is more rigorous and one round slower.
2. **Second species per scene** — the table allows a backdrop belt (`▸`) in 6 scenes. Is that inside
   or outside "ONE species per scene/route"? My reading: a mountain stand behind a temple is not the
   temple's route, and forbidding it would look *less* real. Confirm.
3. **v5.1 §3's "anchor" clause** — I keep it and abolish only the yaw/offset. Confirm that reading;
   the alternative (abolish the whole directive, return furniture to authored positions with no
   anchor requirement) would undo work the user liked.
4. **`White_Pine` / `Yellow_Pine`** — retire from routes, or pixel-verify and keep for backdrops?
   Neither is in the W2 PASS manifest and `White_Pine` has a known `zmin` defect.
5. **P-9 (setback checks) warn-only until measured** — accept, or block the W3 round on the
   measurement?
6. **BY-SA thumbnails** — keep the URL-only rule (my recommendation, continues `real_set_safe.txt`),
   or admit BY-SA thumbnails into `Docs/reference_photos/w3/` with attribution?
7. **sceneD1 crates (§3.2 row 11 dissent)** — abolish to 0°, or cap at ±2.5° on the dock bearing?
   D1 is an eyes-PASS scene; this is the one row where abolition might cost more than it buys.
8. **Discrepancy 1 in §0.1** — confirm the patch scope is **10 of 19** profiles (my AST-exec), not
   A's 18, before the execution spec quotes a number.

---

## Appendix A — machine-readable spec rows

One line per row: `ID | item | user quote | root cause | evidence | build spec | scenes | dependency`.
Quotes marked ★ are from the W3 intake brief; the rest from `user_feedback_v5_1.md`.

```
J-1 | patch decal yaw ±14° | ★"placement jitter ABOLISHED (aligned/orthogonal is the real default)" | ground_kit.py:689,733 | 조례 제7조1나 열식 [law]; Commons Sidewalks n=18; scene01 beauty_overview [measured] | yaw_max=0.0, axis-lock to unit_cell | 10/19 profiles | with J-2,D-3; re-baseline regr
J-2 | stain blot yaw ±22° | ★same | ground_kit.py:1027 | scene07 temple_walk [measured]; blots have no axis | yaw=0 for all kinds; shape → D-1 | 19/19 profiles = 33 | with D-1
J-3 | batch1 furniture yaw jitter | "yaw ±3~8° 지터" (v5.1 §3, superseded) | batch1_common.py:248 + 10 call sites | Commons Benches n=25; kpg §5.1 "랜덤 배치는 존재하지 않는다" [law] | delete calls, yaw := anchor bearing | C1 C2 D2 D4 N1 N3 | after E-4; merge with R2 C1/C2/C5
J-4 | batch1 furniture pos jitter | ★same | batch1_common.py:256 + 14 call sites | same | delete calls, author the coordinate | C1 C2 C4 D2 D4 N1 N2 N3 N5 | as J-3
J-5 | baked yaw literals ±3–8° | "격자 정렬·등간격 금지" (superseded) | scene01:175-177, scene06:262, scene11:233, scene03:235-257 | same | yaw := anchor/kerb bearing; scene03 city blocks re-authored to street-grid bearings | 01 03 06 09 11 13 14 16 20 21 | as J-3
J-6 | street-row pitch irregularity | ★"aligned/orthogonal is the real default" | scene06:255-260, scene11:229-233, 12 13 D3 N5 tuples | 조례 제7조1가 6–8 m; 고시 4–8 m; 산림청 계획 등간격 [law]; Damyang n=12 | constant 7.0 m pitch, gaps only at crossings | 06 11 12 13 D3 N5 | with E-1
J-7 | footprint yaw ±6° + AABB bug | — | ground_kit.py:1071-1075 | feet splay | KEEP yaw; fix _obb_aabb to use the jittered angle | D2 C1 | opportunistic
S-1 | per-tree species draw | ★"street trees = ONE species per scene/route" | scene_common.py:2443-2444 | 조례 제7조1라 [law]; 시행규칙 수관 일정 [law]; scene03 levee_walk 5 silhouettes [measured] | species= kwarg + SCENE_SPECIES map | 17 tree scenes | after S-3
S-2 | per-shrub species draw | ★same | scene_common.py:2819 | 시행규칙 수관 일정 [law] | species= kwarg, one per bed/band | all hedge/planter scenes | after R2 B1b/B2a
S-3 | 7 trees + 4 shrubs never wired | ★"the verified asset set incl. the 10 new trees" | scene_common.py:2118-2125; grep 0 hits [measured] | veg_manifest_w2.json 17 PASS rows [measured] | VEG_SPECIES table, retire White/Yellow_Pine | library-wide | blocks S-1
S-4 | within-species variation | ★"variation via build_tree deterministic size/form" | scene_common.py:2449,2478 | 시행규칙 3.5 m / Ø10 cm [law] | keep ±8 %; add statutory floor; cap street lean 1.5° [assumed] | 17 | with S-1
E-1 | tree setback + pitch | ★"one global rule table" | no rule exists | 고시 2-3(6)(가)1) ≥1 m, 4–8 m [law] | P-1..P-4 in linter | 06 11 12 13 D3 N5 | with J-6
E-2 | furniture setback | ★same | no rule exists | 보도 지침 표2.2 [law]; free walk ≥1.5 m [law]; M1–M6 need photos | rule table + P-5, P-9 warn-only | 15 scenes | photo measurement first
E-3 | bollard line | "볼라드 규정화" (v5.1 씬16/20) | scene_common.py:2936-2937 height=0.75 (−6.25 % vs the 0.80 legal minimum; Ø0.12 is legal) | 교통약자법 별표2 제7호 [law] | P-6; Ø0.1–0.2, h0.8–1.0, pitch 1.5, kerb-locked | 11 12 14 16 20 21 C4 D1 N1-N5 | R2 C6b overlaps
E-4 | placement linter | ★"enforced by a CPU gate" | none | — | scripts/placement_lint.py on the geom_invariance harness | tooling | blocks J-*, E-*
D-1 | stain rectangles | ★"feathered/irregular masks" | ground_kit.py:1029 box prim | tonglam_v2 §2.13-2 [measured] | build_blot() N-gon, 1 prim, no alpha | 33 | with J-2
D-2 | carpet edges | ★same | ground_kit.py patch/leaf boxes | tonglam_v2 §2.12 "perfect rectangle from the air" | N-gon + scatter feather ring + drift bias toward obstructions | 03 07 10 C2 D3 | drift bias needs photos [근거 없음]
D-3 | patch axis lock | ★same | ground_kit.py:733 | real saw-cut patches are rectangles aligned to the carriageway | yaw from unit_cell axis | 10 profiles | with J-1
T-1 | reference panels | ★"per-scene reference-photo panel (3-5 photos)" | none exist | 5 of 12 archetypes empty [measured] | Docs/reference_photos/w3/<archetype>/SOURCES.md; CC0/BY/KOGL thumbs only | 33 → 12 | blocks all v3 judging; needs scripts/harvest_refs.py
T-2 | comparison protocol | ★"side-by-side comparison protocol" | none | real_reference_expansion §7 crop convention [measured] | 5-step, 6 ordered axes, verdict must name a photo | judging | after T-1
T-3 | identical-to-sample checklist | ★"the identical to sample checklist per scene type" | none | §7.4 | per scene type, any NO = FAIL | judging | after T-1
T-4 | numeric assist | — | scripts/imgstats.py GATE | n=54: slope −2.03±0.18, ori_axis p95 0.371 [stat] | advisory only; drop sat_mu/sat_sd/chroma_sd | judging | —
```

## Appendix B — reproduction

```bash
# jitter inventory
grep -rn "jitter\|jit_" --include=*.py .              # 225 hits
grep -n  "rotz=" ground_kit.py                        # 12 hits, all read
grep -rn "bc.jit_yaw\|bc.jit_pos" --include=*.py .    # 18 call sites

# species mechanism
sed -n '2118,2146p;2417,2476p;2796,2830p' scene_common.py
python3 -c "import json;m=json.load(open('assets/veg_manifest_w2.json'));print(len(m['assets']),len(m['rejected']))"
for n in Fraxinus Gray_Birch Lombardy_Poplar Douglas_Fir Colorado_Spruce Scarlet_Oak Black_Oak \
         Holly Yew Cedar_Shrub Switchgrass Grass_Short; do
  printf '%-18s ' "$n"; grep -rn "$n" --include=*.py . | grep -v download_vegetation | wc -l; done

# decal scope (profile granularity; SCENE_PLANS does not AST-exec — see §9-6)
python3 - <<'PY'
import ast; src=open('ground_kit.py',encoding='utf-8').read()
G={'_dim':lambda k:0.0,'dict':dict}
class R(dict):
    def __init__(s,*a,**k): super().__init__(k); s['_pos']=a
for n in ('_P','_S','_E0','_E','_G','_X'): G[n]=lambda *a,**k: R(*a,**k)
for nd in ast.parse(src).body:
    if isinstance(nd,ast.Assign) and getattr(nd.targets[0],'id','')=='GROUND_PROFILES':
        gp=eval(compile(ast.Expression(nd.value),'<x>','eval'),G,{})
for tag in ('patch','stain'):
    print(tag, sum(1 for v in gp.values() if any(r and r[0]==tag for r in (v.get('surface') or ()))), '/', len(gp))
PY

# linter harness capability
sed -n '125,240p' scripts/geom_invariance_check.py

# renders viewed
look_check/{scene01/pt_noon_beauty_overview,scene03/pt_noon_levee_walk,scene06/pt_noon_overview,
            scene07/pt_noon_temple_walk,scene10/pt_noon_leaf_edge,scene11/pt_noon_sidewalk_approach}.png
#   (each under 260730_w2d_fix/)

# law / photo sources — all fetched 2026-07-30
#   서울 조례        https://www.ulex.co.kr/법률/1772859-2001522-서울특별시가로수조
#   서울 시행규칙     https://www.ulex.co.kr/법률/1194320-2001628-서울특별시가로수조
#   국가법령정보센터   https://www.law.go.kr/LSW/admRulInfoP.do?admRulSeq=2000000017655
#   Commons          Category:{Damyang_Metasequoia_Road, Sidewalks_in_South_Korea,
#                             Benches_in_South_Korea, Street_furniture_in_South_Korea,
#                             Metasequoia_glyptostroboides_in_South_Korea}
#   404 (recorded)   Category:{Bollards_in_South_Korea, Ginkgo_biloba_in_South_Korea,
#                             Tactile_paving_in_South_Korea, Han_River_Parks}
```
