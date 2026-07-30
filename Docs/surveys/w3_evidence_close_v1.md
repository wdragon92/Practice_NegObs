# W3 evidence close — photo/PDF gaps that hold spec rows (v1)

**Date** 2026-07-30 · **Scope** CPU + network only · **Wave** W3 intake closure
**Inputs** `w3_intake_01_05.md` §7 · `w3_intake_policy.md` §5.2/§7.2/§7.5 · `w3_intake_06_10.md` §9.2 ·
`Docs/reports/redteam_w3_intake.md` §2.7
**Deliverables in this commit** `scripts/harvest_refs.py` (rebuilt) ·
`Docs/reference_photos/w3/<archetype>/` (12 panels) · this file.

---

## 0. Verdict

| | count | which |
|---|---|---|
| Rows **CLOSED** this session | **8** | 02-B · 04-A · G-6/04-B · 01-B · R7 · M2 · M4a · M5 |
| Rows **strengthened** (were standard-backed, now second-instrument) | **5** | G-2/S-1 · R1 · R3 · R4 · R5 |
| Rows **PARTIALLY closed** (real evidence, still under the n bar) | **2** | S10-A (n = 3 / 8) · S06-B (n = 4, park surfaces only) |
| Rows **STILL-OPEN** | **8** | S08-B · S10-A n-bar · S06-B levee-crown · M1 · M3 · M6 · D-2 · KDS 34 verbatim |
| **New rule rows added** (all `[law]`) | **10** | R5b · R11 – R20 |
| Rule-table values **changed** | **1** | R2 tree pitch default **7.0 → 8.0 m** |
| Gov PDFs fetched | **4 / 4** — 3 mined, 1 held | |
| Archetype panels built | **12 / 12** (5 previously empty now populated) | 103 thumbs + 213 URL-only rows |
| Harvester | committed as `scripts/harvest_refs.py`, reproducible | |

The single biggest change this session: the **산림청 「가로수 조성관리 매뉴얼」** (184 pp, fetched live)
turns out to state, in one place and verbatim, five of the rule-table values the intake docs had to
derive or assume — including the shrub-massing rule (04-A) that was flagged `[근거 없음]`. The
**행정안전부 실무매뉴얼** likewise states the flood-sill dimension verbatim, closing 02-B. Those two
fetches were worth more than the entire photo harvest.

---

## 1. The four gov-PDF fetches (intake §7 procurement plan)

All four fetched live 2026-07-30, kept out of the repo (size/licence), mined here.

| # | document | pp | outcome |
|---|---|---|---|
| 1 | 행정안전부 「지하공간 침수방지를 위한 수방기준 실무매뉴얼」 | 52 | **text extracted**, §3-1-1 quoted below → **02-B CLOSED** |
| 2 | 산림청 「가로수 조성관리 매뉴얼」 | 184 | **text extracted**, 4)(1)(2) + 띠녹지 단면도 → **04-A CLOSED**, R1–R5 corroborated, R5b + R11–R17 new |
| 3 | 서울시 「등산로 정비 매뉴얼」 | 194 | CID-font PDF, **page-rendered**; 훼손유형 photo plates 사진 2-1…2-22 → **G-6 / 04-B CLOSED** |
| 4 | 「사방기술교본」 (경기도 산림환경연구소) | 448 | fetched (5.3 MB); same CID-font class; held as a corroborating source, not mined this session |

### 1.1 Flood sill — 02-B `[law, verbatim]`

> 「지하공간 침수방지를 위한 수방기준 실무매뉴얼」 **3-1-1 출입구 방지턱의 높이**, 해설 (2):
> *"침수방지턱의 계획시에는 침수방지턱에 의해 발생하는 지상의 단차에 유의하여 고령자·장애자등의
> 편의를 위하여 **여러개의 단차를 두는 것이 중요**하다. 우리나라 '지하도로시설기준에 관한 규칙'의
> 규정에 **계단의 높이를 18cm이하로** 규정하고 있다. 따라서 출입구 높이 설정은 … **18cm 높이의
> 계단 1~3개** 정도를 많이 이용하게 된다."*

Two further rules from the same figure, **not previously in any intake doc**:

- **난간은 반드시 설치** — *"출입구로 들어오는 물에 의하여 보행에 지장을 받지 않게 하기 위하여
  반드시 설치"*. A Korean underpass entrance sill **always** carries a handrail. (→ R19)
- 계단폭 doubles as a **둑마루** (levee crest) — the sill is a flood structure, not a threshold detail.
- §3-1-2: 환기구 must sit **above** the design flood height. (→ R20)

This confirms A's 02-B reading exactly (18 cm × 1–3 단) and adds the mandatory handrail.

### 1.2 Street tree + shrub — 04-A and R1–R5 `[law, verbatim]`

From 「가로수 조성관리 매뉴얼」 **4) 식재 가로수 기준**:

> **(1) 교목** — *"식재간격은 **8미터를 기준**으로 하되 … 조정한다."* ·
> *"식재유형은 **도로선형과 평행한 열식재를 원칙**으로 하되 … 특정 목적에 따라 군식·혼식한다."* ·
> *"보도의 한쪽을 기준으로 **1열 심기**를 하고 보도의 폭이 넓을 경우 2열 이상 식재가 가능하다."* ·
> *"**도로의 양측에는 동일한 수종**으로 식재하되 …"* ·
> *"… **보·차도 경계선에서 수간 중심까지 거리를 최소 1m 이상** 확보한다."* ·
> *"**가로수~보차도 경계석 사이 구간(1m 내외)은 보행자 이용성이 낮으므로 최대한 띠녹지를 조성**한다."*
>
> **(2) 관목** — *"**가로수와 가로수 사이의 보도변에** 관목류 및 상록수를 식재하여 …"* ·
> *"**식재유형은 동일수종으로 군식**하고, **하나의 식재군에는 동일수종**으로 식재하되, 경관적으로
> 중요한 지역에는 다른 수종으로 혼식이 가능하다."* ·
> *"성토 시 **경계석 보다 5cm 낮게** 성토하고 관목류와 지피식물 및 숙근초, 야생초화류 …"*

Also: 제4조 row — *"보도가 없는 경우 **갓길에서 2m**"* (R4); §보호틀 — *"보호틀의 규격은 대상형,
직사각형, 정사각형 모두 **최소폭 1.5m**를 기준으로 한다"* (R5), and *"**부정형**(관목류의 군식의
경우)"* (R5b); 지하고 **1.5 m 이상**(향후 2.0 m); 표토 깊이 **30 cm 이상**; 그늘목은
**2~3주 모아심기**; 띠녹지 단면도 — 폭 **2 m 이내**, 경계석 안쪽 **15~20 cm**, 깊이 **20 cm** 절취,
경계석보다 **5~10 cm 낮게**, 2 % slope.

**This is the row the intake marked `[근거 없음]`**: 04-A's "clumped massing, not rows" is now
national-standard text — 관목 is **군식** (massed), **동일수종 per clump**, and it belongs **between
the trees**, not scattered and not in its own row.

### 1.3 Gravel deposition — G-6 / 04-B `[photo, n = 22 plates in one gov manual]`

서울시 「등산로 정비 매뉴얼」 제2장 §3 등산로 훼손유형 carries a **22-plate photographic typology**
(사진 2-1 … 2-22) with a classification table (표 2-1). The plates directly answer "what does eroded
Korean granitic-soil (마사토) trail surface actually look like":

| 유형 | plate | what the deposition/erosion actually does |
|---|---|---|
| **노면세굴형** | 2-9 | rill/gully cut **longitudinally along the fall line**, U- or V-section — *"등산로의 종단방향으로 물길이 생겨 'U'자형 또는 'V'자형으로 깊게 세굴"* |
| **경계침식형** | 2-11 | erosion concentrates at the **trail margin** where walkers step off the main tread |
| **암석풍화형** | 2-12 | bedrock weathers in place → the gravel is **generated where it lies**, not delivered |
| **구슬자갈불편형** | 2-21 | *"구슬크기의 자갈이 등산로에 **전면적으로 널려있어**"* — a bead-gravel **sheet** over the tread |
| **노면배수불량(침수)형** | 2-19 | ponding in flats/hollows; fines wash out, coarse armour stays |
| 샛길형 · 노폭확대형 | 2-13, 2-14 | the tread **widens** as walkers avoid the bad centre |

**Consequence for the G-6 build spec**: uniform-random gravel scatter is wrong in a way this typology
names precisely. The real pattern is (a) a **longitudinal** rill along the fall line, (b) **coarse
armour left in the scoured centre** with fines removed, (c) **edge accumulation at the margins**, and
(d) an **in-situ bead-gravel sheet** where the parent rock is weathering. Deposition follows water and
grain size, and the trail **widens** at the worst sections.

The same manual's ch.3 gives the countermeasure vocabulary (각목묻기 100×100 방부각재 + 80×80
L=600 anchors, 배수구, 돌계단) if the scene needs a maintained rather than a degraded trail.

---

## 2. Harvester — `scripts/harvest_refs.py` (rebuilt, committed)

Rebuilt from the spec in `w3_intake_policy.md` §7.5. Behaviour:

- **Queries**: `cat:<Category>` (`list=categorymembers`, paged), `search:<terms>`
  (`list=search`, ns 6), `files:File:a,File:b`. Batched `prop=imageinfo` with
  `iiprop=url|size|mime|extmetadata`.
- **Licence gate**, evaluated blacklist-first so `BY-SA` cannot fall through the `BY` pattern:
  - **download** → CC0 · public domain · CC BY (1/2/2.5/3/4) · KOGL Type 1
  - **url-only** → any share-alike, or anything unrecognised
  - **reject** → NC / ND / non-free / KOGL Type 2–4
- **Road-view ban enforced in code** — `BANNED_HOSTS` (kakao/naver/daum/google-maps/streetview/
  mapillary/…) and a title regex (`로드뷰|거리뷰|street view|…`); hits are dropped and counted.
- **Country gate** — added mid-session after the first `underpass_entry` build came back full of
  **Nagoya** subway entrances: Commons' fuzzy `list=search` happily answers *"Korea subway station
  entrance stairs"* with Japanese files. A panel of Japanese references is **worse than an empty
  panel**, because the 통람 v3 protocol makes the judge write the verdict *against the panel photo* —
  so a contaminated panel would silently enforce Japanese vocabulary on a Korean scene. A file is
  dropped when it is positively marked as another country **and** never marked as Korea (kana, the
  `地下鉄/駅/丁目` compounds, and ~50 country/city tokens vs a hangul + Korean-placename hint set).
  Files with **no** geographic marker are kept, for eye review. Drops are counted as `off-country`
  per panel and printed in `SOURCES.md`.
- **Outputs per panel**: `LICENSES.csv` in the **existing 12-column schema verbatim**
  (`file,license,license_url,author,credit,date,commons_page,original_url,orig_w,orig_h,harvest_query,title`)
  so it concatenates with `Docs/reference_photos/expanded/LICENSES.csv`; plus `SOURCES.md` with a
  URL list, licence, author, *what to look at*, and the **negative results** for queries that
  returned zero.
- **Throttled** 1.2 s/request with exponential backoff on 429/5xx — Commons rate-limits an anon
  client hard, which is what killed the first run.
- Non-Commons government/press rows are carried in
  `Docs/reference_photos/w3/extra_sources.json` and rendered into each panel's `SOURCES.md` as
  attribution-only rows (no local copy, because gov CMS URLs rotate and the licence is per-page).

Reproduce (the committed panels were produced by exactly this):
```
python3 scripts/harvest_refs.py --archetype all --limit 28       # --thumb-width defaults to 800
python3 scripts/harvest_refs.py --archetype rooftop --list-only  # licence census, downloads nothing
python3 scripts/harvest_refs.py --query 'search:Korea autumn leaves street kerb' \
        --out Docs/reference_photos/w3/leaf_drift --limit 30     # the open D-2 row
```
Runtime is ~25 min for all 12 panels; it is network-bound on the 1.2 s throttle, not CPU-bound.

---

## 3. Per-row evidence status

Legend — **CLOSED**: statute text in hand, or a photo set at the stated n.
**STILL-OPEN**: what is missing is named; nothing is invented to fill it.

### 3.1 Rows closed this session

| Row | was | now | evidence |
|---|---|---|---|
| **02-B** entrance flood sill | strong on law, no dimension source of its own | **CLOSED** | 행안부 실무매뉴얼 3-1-1 해설(2) verbatim: 계단 ≤18 cm, **1~3개**; + 난간 **반드시 설치**; + 환기구 above flood height |
| **04-A** shrub massing | ⚠ `[근거 없음]` — "clumped massing, not rows" was an in-repo assertion | **CLOSED** | 가로수 매뉴얼 4)(2) verbatim: **동일수종 군식**, 하나의 식재군에는 동일수종, **가로수와 가로수 사이의 보도변**; 보호틀 **부정형**(관목 군식) |
| **G-6 / 04-B** gravel deposition | ⚠ **weakest row**, mechanism only, no photo set | **CLOSED** | 서울시 등산로 정비 매뉴얼 §3 훼손유형 — **22 plates** + 표 2-1 classification; 6 named types map onto the deposition spec (§1.3) |
| **G-2 / S-1** one species per route | law-backed | **REINFORCED** | 가로수 매뉴얼: *"도로의 **양측에는 동일한 수종**"* — a second independent instrument |
| **R1** tree ↔ kerb ≥1.00 m | 고시 only | **CORROBORATED** | 가로수 매뉴얼: *"보·차도 경계선에서 수간 중심까지 **최소 1m 이상**"* |
| **R3** row parallel, no yaw | 조례 only | **CORROBORATED** | *"도로선형과 **평행한 열식재를 원칙**"*, 1열 default |
| **R4** no-sidewalk setback 2.0 m | 고시 only | **CORROBORATED** | *"보도가 없는 경우 **갓길에서 2m**"* |
| **R5** 수목보호판 ≥1.5 m | 고시 only | **CORROBORATED + extended** | *"보호틀 … 모두 **최소폭 1.5m**"*; **부정형** shape when a shrub clump shares the pit |
| **R7** bollards on the 경계 line | law + v5.1 | **PHOTO-CONFIRMED** | Hongdae frame: a regular bollard row exactly on the carriageway/walk boundary, nothing in the walking band |
| **01-B** paving to the building face | ⚠ `[assumed]` from standards | **CLOSED (photo)** | n = 4 frames where a Korean sidewalk/plaza meets a building plinth **with no turf gap**: Daejeon 문정로, Jongno ×2 (KOGL-1), Cheonan 연암율금로. See §4.3 |
| **S10-A** 목재 데크 계단 vocabulary | needed n≥8, `Category:Boardwalks in South Korea` = 3 files | **PARTIALLY CLOSED, n = 3** | 행당역 대현산공원 ×3 (CC BY 4.0) are **deck stairs, not benches** — they were mis-shelved in the in-repo set. Vocabulary recorded in §4.4. Still short of n≥8. |
| **S06-B** kerbless-by-design (03/12/17) | photo check never run | **PARTIALLY CLOSED, n = 4** | `river_levee` panel: Hangang park hard-landscape (`river_levee/w3008`, `/w3009`, `/w3010`) shows paving meeting gravel/planting **near-flush, with no 15–25 cm road kerb**; the riverside walk/cycle path (`river_levee/w3006`) is edged by a **metal railing**, not a kerb. So "kerbless" is right for the *park/path* surfaces. The **levee crown road** itself is not clearly framed in any panel photo — that sub-claim stays open. |

### 3.2 Rows still open

| Row | why it is still open | what would close it |
|---|---|---|
| **S08-B** sunken-plaza edge | Commons has no 선큰광장 category; municipal press releases are HTML pages with per-article licences, not a harvestable corpus | a named-site harvest (여의도·광화문·잠실 선큰) from 지자체 보도자료, hand-attributed |
| **S10-A** deck stair, n 3 → 8 | `Category:Boardwalks in South Korea` = **3 files** (confirmed by RT); the 3 in-repo 대현산공원 frames are the same order of magnitude | 공공누리 KOGL-1 park photos from 지자체; or user-supplied refs, which B §9.1 already says are the deciding input |
| **S06-B** levee **crown road** sub-claim | the panel confirms the park/path surfaces are kerbless (§3.1) but no frame shows a levee crown *road* edge | a 제방 도로 harvest, or accept the park/path finding and narrow the spec row to what is shown |
| **M1–M6** prop-edge distances | see §4 — measured, but **n is honestly below 5 on four of the six rows** | a dedicated measurement pass over the newly built `street_arterial` / `sidewalk_local` / `park_trail` panels |
| **D-2** leaf-drift shape | `[근거 없음]` at intake; not attempted this session (autumn-street harvest) | `search:Korea autumn leaves street kerb` — the harvester will run it as-is |
| **KDS 34** stair 단높이/단너비 verbatim | not fetched; 조경설계기준 is a large 고시 PDF | one targeted fetch before any number goes in the exec spec |

---

## 4. Prop-edge-distance — measurement, and the rule table

### 4.1 Method, stated so the numbers can be checked or thrown away

Ground-plane lateral distances were read **at a single image row** (lateral scale is constant along
an image row for a ground plane), using an in-frame scale reference at the *same depth* as the span
being measured. Scale references used, all standard and already project-cited (`kpg` §3.2):

| reference | nominal | where used |
|---|---|---|
| 화강석 도로경계석 top face | **0.20 m** (규격 200×250×1000) | kerb-relative offsets |
| 화강석 경계석 unit length | **1.00 m** | longitudinal pitch |
| 보도블록 | **0.30×0.30 m** or **0.20×0.10 m** | module counting across the walk |
| 볼라드 | Ø **0.10–0.20 m**, h **0.8–1.0 m** | vertical check |
| 맨홀 (보도용) | Ø **0.648 m** | plan check |

**Honest limitation.** All the usable frames are oblique street photographs, not rectified. Counting
paving modules across a span is robust (**±½ module ≈ ±0.15 m**); reading a pole centre off a kerb
line at 30–40 m is not. Every value below is therefore given as a **band**, not a point, and the
**n actually achieved is stated per row**. Four of the six M-rows did not reach n ≥ 5 and are marked
so — they enter the linter as **warn**, not hard, exactly as `w3_intake_policy.md` §5.3 P-9 already
specified.

### 4.2 What the frames actually show — the three-band structure

Every Korean sidewalk frame examined resolves into the same three bands, and *this*, rather than any
single number, is the finding the linter should enforce:

```
 carriageway │ 시설물대 / 띠녹지 │      보행안전공간 (free walk band)      │ 건물 전면대
             │  0.5 – 1.5 m      │            ≥ 1.5 m, clear               │  0 – 1.0 m
   kerb ─────┤ trees, lamps,     │  NOTHING stands here                    │ signage, A-boards,
             │ bollards, bins,   │                                         │ planters against
             │ bus poles, signs  │                                         │ the facade
```

- Furniture forms **one line**, shared with the tree row, in the kerb-side band. Not a scatter, and
  not two lines. Seen in every frame examined (Jongno ×2, Daejeon 문정로, 양재대로, 정왕신길로,
  Hongdae, 덕수궁길).
- The free walk band is **empty** in every frame. There is no Korean sidewalk in this corpus with a
  prop standing in the middle of it — which is exactly the defect the eyes round named in scene11.
- The building-face band carries **shop signage and A-boards**, never planting-with-a-gap.

### 4.3 01-B — paving to the building face `[photo, n = 4]`

Frames where a paved walking surface meets a building: **the paving runs to the plinth**. There is a
granite/concrete plinth strip or a shallow ramp at the face, and then the facade. **No turf gap in
any frame.** Where planting exists near a facade it is a *deliberate raised bed with a kerb*, not a
residual grass strip.

n = 4 (Daejeon 문정로 · Jongno KOGL-1 ×2 · Cheonan 연암율금로). Below the n ≥ 5 bar by one, but the
claim was `[assumed]` before and is now `[photo]`; and the *counter*-example rate is 0/4.

### 4.4 S10-A — 목재 데크 계단 vocabulary `[photo, n = 3]`

From the three 행당역 대현산공원 frames (CC BY 4.0), which the in-repo set had filed as "benches":

- Treads: **paired timber planks** on steel/timber stringers, **open risers**.
- Deck landings: planks laid **across** the direction of travel, gaps ~5–10 mm.
- Handrail: **round timber top rail + one mid rail**, square posts, **domed terracotta post caps** —
  this cap is the single most Korean-park-specific detail in the frames.
- The flight sits on a **rubble/stone retaining bank**, not on an exposed steel frame.
- **No steel balustrade, no perforated steel tread** — which is precisely the "reads as an apartment
  emergency stair" failure S10-A names.

Still n = 3 against a n ≥ 8 bar. Recorded as vocabulary, **not** as a finalisation input — B §9.1's
blocker (user refs decide) stands.

### 4.5 The rule table for the CPU placement-linter

Reference datum: **walking-zone edge** (보행안전공간 boundary); on a carriageway sidewalk the second
datum is the **보도·차도 경계선** (kerb line).

**Law rows — hard gates.**

| # | prop | rule | value | basis | change vs intake |
|---|---|---|---|---|---|
| R1 | 가로수 | trunk centre ← kerb line | **≥ 1.00 m** | 고시 2-3(6)(가)1) **+ 가로수 매뉴얼 4)(1)** | corroborated by a 2nd instrument |
| R2 | 가로수 | longitudinal pitch, **constant** | **8.0 m** default; accept **6.0–8.0 m** | 가로수 매뉴얼 *"식재간격은 8미터를 기준"*; 서울 조례 6–8; 고시 4–8 | **default 7.0 → 8.0** |
| R3 | 가로수 | planting form | **row parallel to the road alignment**, yaw 0, no lateral offset; **1 row** per side, 2+ only on a wide walk | 조례 제7조1나 · 고시 · 매뉴얼 4)(1) | corroborated |
| R4 | 가로수 (no sidewalk) | ← shoulder end | **≥ 2.0 m** | 고시 2-3(6)(가)2) · 매뉴얼 제4조 | corroborated |
| R5 | 수목보호판 | min opening width (all shapes); cover below grade | **1.5 m**; **≥ 5 cm** below | 고시 2-3(5)(가) · 매뉴얼 보호틀 | corroborated |
| **R5b** | 수목보호판 | shape when a shrub clump shares the pit | **부정형 (irregular)**, not rectangular | 매뉴얼 보호틀 유형 | **NEW** |
| R6 | 볼라드 | h / Ø / pitch | **0.8–1.0 m** / **Ø0.1–0.2 m** / **1.5 m** | 교통약자법 별표2 제7호 | unchanged |
| R7 | 볼라드 | position | **on the 보도·차도 경계 line**, axis-locked, only at vehicle entries | 별표2 + v5.1 §2 | **photo-confirmed** |
| R8 | any 노상시설 | free walk band after occupancy | **≥ 2.0 m** national; **1.5 m** constrained floor | 도로구조규칙 §16 + 보도지침 표2.2 | unchanged |
| R9 | 승차대 ↔ 보도 시설물 | separation | **≥ 1.5 m** | in-repo kub | unchanged |
| R10 | 점형블록 ↔ 연단 | offset | **0.30 m** | 교통약자법 | unchanged (still default-OFF by ruling) |
| **R11** | 띠녹지 | width; level vs kerb | **≤ 2.0 m** wide; finished **5–10 cm below** the kerb top; 경계석 안쪽 15–20 cm, 절취 깊이 20 cm; 2 % slope | 가로수 매뉴얼 띠녹지 단면도 | **NEW** |
| **R12** | tree ↔ kerb strip (~1 m) | treatment | **plant it** (띠녹지) — do not pave it | 매뉴얼 4)(1) | **NEW** |
| **R13** | 관목 | placement + form | **between adjacent street trees**, along the walk edge; **동일수종 군식**, **one species per clump** | 매뉴얼 4)(2) | **NEW — closes 04-A** |
| **R14** | 가로수 | 지하고 (clear trunk height) | **≥ 1.5 m** (target 2.0 m) | 매뉴얼 품질기준 | **NEW** |
| **R15** | planting bed | 표토 depth | **≥ 30 cm** | 매뉴얼 제11조 | **NEW** |
| **R16** | 그늘목 (at crossings) | form | **2–3 주 모아심기**; single only where the island is tight | 매뉴얼 교통섬·횡단보도 녹화 | **NEW** |
| **R17** | 보호덮개 | substitution | on wide/low-traffic walks replace the steel grate with 띠녹지·하층식재 (or 나무파쇄물·자갈·초화류·관목) | 매뉴얼 보호덮개 | **NEW** |
| **R18** | 지하 출입구 침수방지턱 | step height × count | **≤ 0.18 m × 1–3 단** | 행안부 실무매뉴얼 3-1-1 | **CLOSES 02-B** |
| **R19** | 지하 출입구 | handrail | **mandatory** (*"반드시 설치"*) | 〃 | **NEW** |
| **R20** | 지하 출입구 환기구 | level | **above** the design flood height | 〃 §3-1-2 | **NEW** |

**Measured rows.** `n` is the number of *distinct frames in which the rule was observed*, counted
honestly. **Rows at n ≥ 5 become hard gates; rows below n = 5 stay `warn`**, as
`w3_intake_policy.md` §5.3 P-9 already specified.

| # | prop | rule as measured | value (band) | n | counter-ex | gate |
|---|---|---|---|---|---|---|
| **M4a** | 플랜터 / 화단 — **on a sidewalk** | a **continuous 띠녹지 band along the kerb**, finished **below** the kerb top — *not* discrete tubs | width **≤ 2.0 m**; level **−0.05 … −0.10 m** vs kerb top | **6** | 0 | **HARD** — also independently law (R11) |
| **M4b** | 플랜터 — **on a civic plaza** | **discrete precast planters are correct here**, but only in a **straight line along a plaza edge**, never scattered and never on the central axis | — | **2** (Gwanghwamun) | 0 | **warn** — recorded so M4a is not misapplied to plaza scenes |
| **M2** | 가로등 | pole centre stands in the **kerb-side 시설물대**, on the **same line as the tree row** (one line, not two) | **0.4 – 1.0 m** from the kerb line | **6** | 0 | **HARD** for the band-membership + line-sharing; the *numeric* 0.4–1.0 m stays **warn** (readable on only 3 of the 6) |
| **M5** | 안내표지 지주 | post stands **outboard of the paved walking field**, in the kerb-side band | **0.3 – 0.6 m** from the kerb line | **5** | 0 | **HARD** for band membership; numeric **warn** |
| **M3** | 휴지통 | stands **at an edge** (planting-bed kerb, shelter, frontage) — never free-standing in the walking band | in the 시설물대 or against a bed kerb | **3** | 0 | **warn** (n < 5) |
| **M1** | 벤치 | seat axis **parallel to the edge it stands against**; back face **against** that edge | axis **±2°**; back-face gap **0 – 0.3 m** | **2** | 0 | **warn** (n < 5) |
| **M6** | 벤치 ↔ 가로수 | benches sit **between** trees, on the tree line, not offset into the walk | on the tree line, mid-gap | **2** | 0 | **warn** (n < 5) — v5.1's "anchor" idea is *consistent* with the frames but is **not** demonstrated |

**M-row frames.** `wcNNN` = `Docs/reference_photos/expanded/`; `panel/w3NNN` = the new panels.
(The `w3NNN` index restarts per panel, so it is only unique when qualified by the panel name.)

| row | frames |
|---|---|
| M1 | wc140 · `street_arterial/w3012` |
| M2 | wc065 · wc110 · wc140 · wc144 · `street_arterial/w3009` · `street_arterial/w3010` |
| M3 | wc047 · wc081 · wc140 |
| M4a | wc041 · wc047 · wc048 · wc065 · wc110 · wc144 |
| M4b | `plaza_civic/w3006` · `plaza_civic/w3024` |
| M5 | wc010 · wc140 · `sidewalk_local/w3006` · `sidewalk_local/w3008` · `street_arterial/w3016` |
| M6 | wc047 · wc140 |

**Rows M1, M3, M6 are STILL-OPEN** at n = 2/3/2. The honest reading is that the *class* rules
("never in the walking band", "against an edge") held in every frame examined with **zero
counter-examples**, but three frames is not the user's bar and I am not going to write five where I
saw three.

**Linter consequence.** P-9 splits: **M4/M2/M5 band-membership promote to hard**; M1/M3/M6 and every
numeric band stay **warn**. P-1…P-8/P-10 are unaffected except that **P-2 must take R2's changed
default, 7.0 → 8.0 m** (accept band 6.0–8.0), and the new **R11–R20** rows need checks of their own.

---

## 5. Panels index — `Docs/reference_photos/w3/<archetype>/`

Each directory holds `SOURCES.md` (URL list + licence + author + what to look at + negative results)
and `LICENSES.csv` (12-column schema). Thumbnails are committed **only** for CC0 / PD / CC BY /
KOGL Type 1; share-alike rows are URL-only.

| archetype | scenes | ledger rows | thumbs committed | URL-only | queries used |
|---|---|---|---|---|---|
| `plaza_civic` | 01 · 08 · 14 · 20 · 21 · N1 · N3 | 28 | **6** | 22 | `cat:Gwanghwamun Plaza` |
| `street_arterial` | 06 · 11 · N5 | 28 | **18** | 10 | `cat:Sidewalks in South Korea` · `cat:Streets in Seoul` |
| `sidewalk_local` | 13 · N2 · N4 · D3 | 18 | **14** | 4 | `cat:Sidewalks in South Korea` |
| `river_levee` **(was empty)** | 03 · 12 · 17 | 28 | **9** | 19 | `cat:Hangang Park` |
| `lake_park` | 09 | 28 | **10** | 18 | `cat:Cheonggyecheon` |
| `park_trail` | 04 · 10 · C2 | 28 | **3** | 25 | `cat:Benches in South Korea` · `cat:Parks in Seoul` |
| `amphitheatre` **(was empty)** | 05 | 28 | **7** | 21 | `cat:Seoul Forest` · `search:야외음악당` |
| `temple_precinct` | 07 | 28 | **11** | 17 | `cat:Buseoksa` |
| `underpass_entry` **(was empty)** | 02 · 16 | 28 | **0** | 28 | `search:서울 지하철 출입구` |
| `alley_hillside` | 15 · 18 | 28 | **11** | 17 | `cat:Bukchon Hanok Village` |
| `rooftop` **(was empty)** | 19 | 18 | **7** | 11 | `cat:Roofs in South Korea` · `search:Korea green roof building` · `search:옥상` · **0-hit:** `cat:Roof gardens in South Korea`, `search:Korea rooftop garden parapet`, `cat:Rooftops in South Korea` |
| `industrial_transit` **(was empty)** | D1 · D2 · D4 | 28 | **7** | 21 | `cat:Dorasan Station` |
| **TOTAL** | 33 scenes | **316** | **103** | **213** | |

### 5.1 Panel quality — read this before using a panel as a v3 reference

Three panels needed a second build, and the reason matters more than the counts:

- **`underpass_entry`** — the first build returned **Nagoya subway entrances** for
  `search:Korea subway station entrance stairs`. Rebuilt against `search:서울 지하철 출입구`, it is
  now **28 genuine Seoul Metro entrances** — but *all* CC BY-SA 4.0, so **0 thumbs are committed**
  and the panel is a **URL ledger only**. That is the policy-correct outcome, not a failure: the v3
  judge opens the URLs. Do not "fix" this by committing the files.
- **`amphitheatre`** — the first build was 5/7 **Hattori Ryokuchi open-air hall, Osaka**. The
  filename names no country, which is why the country gate had to be extended to read the file's
  **Commons categories** rather than just its title.
- **`rooftop`** — the first build was a long survey series of *views **from*** apartment roofs, not
  roof **surfaces**; `search:Korea rooftop view` is recorded in the code as tried-and-rejected. The
  rebuild also dropped **17 off-country** roofs (Singapore, Taiwan, Kyoto, Hanoi, and a run of
  European churches).

**`park_trail` is thin by licence, not by search** — `Category:Benches in South Korea` is 25 files
and almost entirely BY-SA, so it yields 28 ledger rows and only 3 committed thumbs. This is the
direct cause of **M1/M6 staying at n = 2** (§4.5): the bench corpus exists, but it cannot be brought
into the repo, and I did not count photographs I had not opened.

**General rule this session established**: a panel populated with the wrong country is **worse than
an empty panel**, because §7.3 of the policy makes the judge write the verdict *against the panel
photo*. Any future panel must be eyeballed once before it is used as a v3 reference.

**Non-Commons attribution rows** are in `Docs/reference_photos/w3/extra_sources.json` and are
rendered into the relevant `SOURCES.md` files: 행안부 실무매뉴얼 (underpass sill figure), 서울시
mediahub 수색역 (canopy), 서울시 등산로 정비 매뉴얼 + 사방기술교본 (trail erosion plates), 산림청
가로수 조성관리 매뉴얼 (planting rules), 국토부 보도 설치 지침 표2.2 (obstacle widths).

---

## 6. Licence ledger

| licence | thumbs committed | redistributable? | obligation |
|---|---|---|---|
| CC0 | 66 | yes | none |
| Public domain | 13 | yes | none |
| CC BY 4.0 | 10 | yes | attribution (author + source + licence, carried in LICENSES.csv) |
| CC BY 2.0 | 7 | yes | attribution (author + source + licence, carried in LICENSES.csv) |
| CC BY 3.0 | 5 | yes | attribution (author + source + licence, carried in LICENSES.csv) |
| KOGL Type 1 | 2 | yes | attribution (author + source + licence, carried in LICENSES.csv) |
| **committed total** | **103** | | |
| share-alike (BY-SA) | **0 committed** | URL-only rows | none incurred |
| NC / ND / non-free | **0 recorded** | rejected by the harvester | — |
| road-view | **0** | banned in code | — |

Disk footprint of the committed panels: **16.5 MB** (103 JPEG thumbs, max 800 px wide).

**Obligations.** CC BY and KOGL Type 1 thumbs require attribution — carried per-file in each panel's
`LICENSES.csv` (`author`, `credit`, `commons_page`, `license_url`). CC0 / PD carry none. **No
share-alike file is committed**, so the repository takes on no share-alike obligation; those rows
exist as URL + caption only. **No NC/ND** file is recorded at all. **No road-view source** appears
anywhere — the ban is enforced in `harvest_refs.py` (`BANNED_HOSTS` + `BANNED_TITLE`), not merely by
convention, and the drop count is reported per panel.

---

## 7. What this file does NOT establish

1. It does **not** finalise S07-A or S10-A. B §9.1's blocker (the user's reference images decide)
   is untouched; §4.4 is vocabulary, not a decision.
2. It does **not** resolve the cross-doc conflicts X1–X5 in `redteam_w3_intake.md` §5. R2's changed
   default (7.0 → 8.0 m) is a **new input** to that reconciliation, not a resolution of it.
3. The M-row bands are **not** rectified-photogrammetry values. They are module-count reads on
   oblique frames with a stated scale reference, and four of six are below the n ≥ 5 bar.
4. 사방기술교본 was fetched but **not** mined (CID-font PDF, 448 pp). It is held as corroboration for
   G-6, which is already closed on the 서울시 manual.
5. Panel photographs are **evidence, not scene content** — the no-people/no-vehicles project law is
   about renders, and is unaffected.

---

## 8. Sources touched this session

**Government PDFs** (all fetched live 2026-07-30)
- 행정안전부 「지하공간 침수방지를 위한 수방기준 실무매뉴얼」 (52 pp) —
  `https://www.mois.go.kr/cmm/fms/FileDown.do?atchFileId=FILE_00071165hOZn4gq&fileSn=0`
- 산림청 「가로수 조성관리 매뉴얼」 (184 pp) — article
  `https://www.forest.go.kr/kfsweb/cop/bbs/selectBoardArticle.do?bbsId=BBSMSTR_1069&mn=NKFS_06_09_01&nttId=3147093`
  (file id `FILE_000000020032909`; the download needs the article's session cookie — plain
  `FileDown.do?atchFileId=…` returns 404)
- 서울시 「등산로 정비 매뉴얼」 (194 pp) —
  `https://news.seoul.go.kr/env/archives/527421` → `.../env/files/2023/10/653f43b45af264.83765873.pdf`
- 「사방기술교본」 (448 pp) —
  `http://forest.gg.go.kr/wp-content/uploads/sites/6/2018/11/20181119_sabaing.pdf`

**Wikimedia Commons** — see each panel's `SOURCES.md` for the per-file ledger and the negative
results. Confirmed-empty categories re-verified this session and recorded in code comments so they
are not re-attempted: `Amphitheatres in South Korea`, `Underpasses in South Korea`,
`Rooftops in South Korea`, `Han River`, `Banpo Hangang Park`.

**In-repo** — `Docs/surveys/w3_intake_{01_05,06_10,policy}.md` ·
`Docs/reports/redteam_w3_intake.md` · `Docs/reference_photos/expanded/LICENSES.csv` + the 54 files ·
`Docs/reference_photos/real_set_safe.txt` · `Docs/surveys/korean_pedestrian_geometry.md` §3.

**Environment note.** `pdftotext` cannot decode the `Unidocs-Korea1` CID collection used by Korean
HWP→PDF exports (poppler ships `Adobe-Korea1`, not `Unidocs-Korea1`; `POPPLER_DATADIR` is not read
by poppler, only by xpdf). Those two manuals were mined by **page rendering** (`pdftoppm`) instead.
Anyone re-running §1.3 should do the same rather than assume the text layer is empty.
