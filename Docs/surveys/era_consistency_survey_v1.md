# Construction-era consistency survey v1 — statute dates × scene era × real-world prevalence

- Written 2026-07-30 · branch `feat/realism-v1` · **no code edits, no scene edits, no commit, CPU only**
- Normative input for **통람 v2** criteria and the **W4 (GT) round**
- Evidence tags: `[law]` primary statute text · `[stat]` measured/counted/official statistic ·
  `[assumed→argued]` a design assumption with a stated argument · `[measured]` read out of this repo's
  code or docs · `[computed]` arithmetic here · `[estimate]` · `[no source]` · `[unverified]`

---

## 0. The principle this document encodes

> **Fixture presence = (implied construction era) × (statute effective date) × (real-world prevalence).**
>
> Korean building statutes are **not retroactive**. A stair built in 1978 is not required to grow a
> handrail because a 2005 amendment says so. The standard supplementary provision
> (부칙 경과조치) protects the permit already issued, and current standards attach only on
> **신축 · 증축 · 대수선 · 용도변경**.
>
> Therefore an old-neighbourhood build that **lacks** handrails, landings and tactile paving is not a
> modelling defect. It is (a) realism, (b) this project's research thesis — *the hazard is the reality of
> under-compliance* (v5 brief: "위험 = 규정 미달의 현실") — and (c) a decorrelation lever: it produces
> clean `cue− / label+` samples that break the "railing ⇒ drop" shortcut.
>
> **Real cases outrank code.** Where a statute says a fixture must exist and the field says it does not,
> the field wins and the statute becomes the caption, not the instruction.

Two corollaries that decide most of the cells below:

1. **Public works are the exception.** 도로·공원·역사·지하보도 are maintained assets on a repair
   budget with a legally mandated accessibility-retrofit programme behind them. There, a **newer
   fixture on an older structure** is the realistic state — not absence, and not seamless compliance.
   That third state has a name in this document: **RETROFIT-STYLE**, and it is the highest-value cell
   class we own, because it is visually distinctive (different metal, different paint, anchor plates,
   glued-on tactile) and almost nothing in the corpus models it today.
2. **Private and informal fabric is where absence lives.** 달동네 골목, 민간 옥상, 주차장 내부,
   공사장, 야드 — no retrofit duty, no budget, no inspector. Absence there is not "미구현", it is the
   correct answer.

---

## 1. Statute timeline

All Korean text below is quoted from the 국가법령정보센터 (law.go.kr) official XML of the specific
historical version; `lsiSeq` numbers identify that version. `[law]` throughout.

### 1.1 Master table

| Fixture | Provision | Requirement first enacted | Amendments that changed the number | Retroactive to 기존 건축물? | Current spec |
|---|---|---|---|---|---|
| **계단참** (landing) | 피난방화규칙 §15①1 | **1999-05-07 건설교통부령 제184호 (제정)**, 시행 1999-05-09 — transposed **verbatim** from 건축법 시행령 §48①, itself traceable to 영 §21 (1982) and §§17–19 (**1973-09-01 대통령령 제6834호**) | Value **never changed since ≥1973**. Only wording: 2015-04-06 국토교통부령 제193호, "너비 1.2미터" → "유효너비 120센티미터" | **No** | 높이 3 m 초과 → 3 m 이내마다 유효너비 ≥120 cm |
| **난간** (guard, open side) | 피난방화규칙 §15①2 | same (1999 제정; from 영 §48②, ≥1973) | **never amended** | No | 높이 1 m 초과 계단·계단참 양옆에 난간(**벽 또는 이에 대치되는 것을 포함**) |
| **중간난간** (intermediate) | 피난방화규칙 §15①3 | same (1999 제정; from 영 §48③, ≥1973). The 단높이 ≤15 cm **AND** 단너비 ≥30 cm exemption is present **from the start** | **never amended** | No | 너비 3 m 초과 → 3 m 이내마다 난간 |
| **손잡이 spec** (φ32–38 / 50 mm / 850 mm / ext ≥300 mm) | 피난방화규칙 §15④ | **1992-06-01 건설부령 제504호** (건축법시행규칙 §29④, 전부개정) — the *duty* to install one where both sides are walls dates to **1982-10-30 건설부령 제340호** | **§15④ has NEVER been amended** since the 1999 transposition | No | φ3.2–3.8 cm 원형/타원형 · 벽에서 ≥5 cm · 계단으로부터 **85 cm** · 끝 수평부 바깥쪽 ≥30 cm |
| **옥상·노대 난간 높이** | 건축법 시행령 §40① | **1.1 m** from ≥1982 (령 제10882호, then §44①) | **1.1 m → 1.2 m at 대통령령 제18951호, 공포·시행 2005-07-18** | No | 높이 **1.2 m 이상** (출입 불가 구조면 면제) |
| **주택 난간 높이 / 간살** | 주택건설기준 등에 관한 규정 §18② | 110 cm as of 1998 (령 제15872호) | **110 → 120 cm at 대통령령 제17972호, 2003-04-22**; same amendment tightened 간살 to a flat ≤10 cm | No | ≥120 cm (내부계단·계단중간 등 위험 적은 곳 ≥90 cm) · 간살 안목 ≤10 cm |
| **보행자용 방호울타리** | 「도로안전시설 설치 및 관리지침」 국토교통부 **예규** 제413호 (2024-12-13 일부개정); 부칙 chain visible to 제136호 (2009-11-11) | n/a — an **예규**, binding 도로관리청, not a 법령 | n/a | n/a (no permit, no vesting) | **110 cm 표준**, 디자인·미관·경제성 고려 시 110–120 cm 바람직 |
| **계단 유효높이** | 피난방화규칙 §15①4 | **신설 2010-04-07 국토해양부령 제238호** | — | No | ≥2.1 m |
| **논슬립 / 미끄럼방지** | 편의증진법 시행규칙 **별표1 제8호 마.(2)** | **1998-04-11 보건복지부령 제64호 (제정)** — substantively unchanged since | 별표1 last amended 2023-12-11 보건복지부령 제983호 | Binds via 편의증진법's own 대상시설 scope, **not** via 건축법 | 계단코에 줄눈넣기 또는 경질고무류 등 **미끄럼방지재로 마감하여야 한다** |
| **단높이·단너비** | 피난방화규칙 §15② | 1999-05-07 제184호 | 2003-01-06 제348호 (옥내계단 한정), 2005-07-22, 2010-04-07, 2015-04-06, 2019-08-06 | No | **초등 ≤16/≥26 · 중고 ≤18/≥26. All other uses: NO riser/tread limit at all** |

### 1.2 Retroactivity — the doctrine, with primary text

The governing article is **건축법 제6조 (기존의 건축물 등에 관한 특례)**, implemented by
**건축법 시행령 제6조의2②** — *not* §5, which is 「적용의 완화」.

> ② 허가권자는 기존 건축물 및 대지가 **법령의 제정·개정**이나 … 법령등에 부적합하더라도 다음 각 호의
> 어느 하나에 해당하는 경우에는 건축을 허가할 수 있다. 1. 기존 건축물을 재축하는 경우
> 2. **증축, 개축 또는 대수선하려는 부분이 법령등에 적합한 경우** …

Three 부칙 경과조치, verbatim:

- **부칙 <제184호, 1999.5.7> 제2조** (피난방화규칙 제정): "이 규칙 시행당시 건축허가를 신청중인 경우와
  건축허가를 받거나 건축신고를 하고 건축중인 경우의 건축기준등의 적용에 있어서는 **종전의 규정에 의한다**.
  다만, 이 규칙에 의한 건축기준이 종전의 규정에 의한 건축기준보다 **완화된 경우에는 이 규칙에 의한다**."
- **부칙 <제461호, 2005.7.22> ②** (the amendment that restructured §15): same two-limb form.
- **부칙 <제18951호, 2005.7.18> ②** (the very amendment that raised the guard 1.1 → 1.2 m): same, with
  the carve-out "다만, 종전의 규정이 개정규정에 비하여 건축주·시공자 또는 공사감리자에게 **불리한 경우에는
  개정규정에 의한다**."

Two structural facts that matter for scene modelling:

1. **The cut-off is the permit-application date, not completion.** A building permitted in June 2005 and
   finished in 2008 lawfully carries a **1.1 m** guard.
2. **The proviso is a one-way ratchet in the owner's favour** — relaxations propagate to pipeline
   projects, tightenings do not. So nonconformity accumulates downward in time, never upward.

### 1.3 Scope limits — these decide more scenes than the dates do

This is the finding that reorganises §4. **The landing / guard / mid-rail rules are 1973-vintage**, so
"my stair is from 1978" is *not* by itself a defence. What actually exempts our old scenes is **scope**:

- **건축법 시행령 §48① delegates §15 only for 연면적 200 m² 초과 건축물.** Small private buildings never
  bite at all.
- **피난방화규칙 §15⑧**: "승강기기계실용 계단, 망루용 계단 등 특수한 용도에만 쓰이는 계단에 대해서는
  제1항부터 제7항까지의 규정을 적용하지 아니한다."
- **§15② width applies to 옥내계단 only** (limit added 2003-01-06 제348호).
- **And decisively: §15 governs 계단 *of a 건축물*.** A 지하보도, a 육교, a 하천 제방 계단, a 골목 계단,
  a 공원 산책로 계단 are **도로 부속물 / 하천시설 / 도시공원시설**, not 건축물 — so 건축법 §15 does not
  reach them at all, in **any** era. Their standards come from 도로·하천·공원 지침 and (for accessibility)
  from 편의증진법/교통약자법, which have their own 대상시설 lists.

> **Correction to the working assumption.** The project has been treating "old ⇒ exempt". The accurate
> rule is **"not a 건축물 ⇒ never covered" first, and "permitted before the amendment ⇒ vested" second.**
> Both point the same way for scenes 02·03·11·15·17·18, but the scope argument is far stronger and
> does not weaken as the structure's date drifts later.

### 1.4 Corrections to prior project assumptions `[law]`

| Prior assumption (in-repo or in the brief) | Correct position |
|---|---|
| The handrail spec came in via a 2010s amendment tied to 장애인등편의법 | **Wrong.** φ32–38 / 85 cm / ext 300 mm dates to **1992-06-01 건설부령 제504호**, six years *before* 편의증진법 시행규칙 (1998). §15④ has never been amended. The causal arrow runs the other way |
| Outdoor guard is 1.2 m (건축령 §40) — a fixed fact | **Era-dependent.** 1.1 m until 2005-07-17; 1.2 m from 2005-07-18. Apartments switched earlier, **2003-04-22**. This is a usable era tell, not an error |
| Retroactivity doctrine sits in 건축법 §5 | **Wrong article.** §5 is 적용의 완화; the doctrine is **§6** + 영 §6조의2 |
| §15③ is about "walls on both sides" geometry | **Use-scoped, not geometry-scoped.** §15③ applies to a list of building *uses* and their 주계단/피난계단; within that scope it requires a 손잡이 where walls mean there is no 난간. 법제처 법령해석 **19-0158 (2019-05-20)** confirms a §15③ 난간 need **not** meet §15④, because §15④ dimensions the **손잡이** |
| Nosing/anti-slip has no domestic basis (`[근거 없음]`, `I_ks_dimension_verification.md`) | **Partly wrong.** The *nose radius* indeed has no domestic rule — but **anti-slip at the nosing IS mandatory** under 편의증진법 시행규칙 별표1 제8호 마.(2) since **1998-04-11**. Colour contrast on the nose exists in the same 별표 (바.(2)) but is **permissive** ("할 수 있다") |
| Korean law caps riser/tread generally | **Not since 1999.** §15② sets riser/tread **only for 초등학교 (≤16/≥26) and 중·고등학교 (≤18/≥26)**; all other uses are width-only. Pre-1999 the caps were universal (e.g. 1990 건설부령 제472호: 기타 22/21, 직상층 20/24) — so a *tight, steep* stair is period-correct for a pre-1999 build and merely unregulated afterwards |

Also newly available from 편의증진법 시행규칙 별표1 제8호 (1998-04-11, substantively unchanged):
**챌면 반드시 설치** (open risers forbidden for covered facilities) · 디딤판 ≥0.28 m · 챌면 ≤0.18 m ·
**계단코 3 cm 이상 돌출 금지** · 챌면 기울기 ≥60° · 양측면 손잡이 연속 설치 **의무** · 끝부분 수평
0.3 m 이상 · 계단 시·종점 **0.3 m 전면에 계단 폭만큼 점형블록** · 참은 1.8 m 이내마다 "설치**할 수 있다**"
(permissive, **not** a duty — the repo's existing reading is confirmed).
Handrail dimensions cross-referenced to 별표1 제7호 다: 높이 **0.8–0.9 m** (2중 설치 시 상 0.85 / 하 0.65),
지름 **3.2–3.8 cm**, 벽 간격 **5 cm 내외** — note the height differs from 피난방화규칙's fixed 85 cm.

### 1.5 Accessibility strand — verified, and what is still open

**Verified `[law]`:**

| Item | Provision | Status |
|---|---|---|
| 편의증진법 시행규칙 제정 | **1998-04-11 보건복지부령 제64호** | verified; 계단 clauses substantively unchanged since |
| 별표1 current amendment | **2023-12-11 보건복지부령 제983호** per the law.go.kr PDF extracted this session | ⚠ **conflicts with the in-repo citation** in `ground_kit_spec_v1.md` §12.1, which cites **보건복지부령 제1166호, 시행 2026-07-02**. A 2026 amendment would supersede 제983호. **Do not silently pick one** — the registry's number is newer and may simply be the current one; reconcile before either document is treated as authoritative |
| 점자블록 dimensions | 별표1 **제16호**: 0.3 × 0.3 m · 점형 **36 dots (6×6)** 반구형/원뿔절단형 **0.6 ± 0.1 cm** · 선형 **4 bars** 상단부평면형 **0.5 ± 0.1 cm** · **원칙적으로 황색** | verified verbatim (§5.3) |
| 점자블록 installation method | 별표1 제16호: **매립식 원칙, 부착식은 매립이 불가능하거나 현저히 곤란한 경우에 한해 허용** | **verified — this is the key new finding**, and it legalises the glued retrofit |
| 점자블록 outdoor material | 별표1 제16호: 반사되거나 눈·비에 미끄러지기 쉬운 재질 **금지** | verified |
| 계단 accessibility spec | 별표1 제8호 — 참 1.8 m "할 수 있다" (permissive) · 유효폭 ≥1.2 m (옥외피난 0.9) · **챌면 필수** · 디딤판 ≥0.28 · 챌면 ≤0.18 · 계단코 돌출 <3 cm · 챌면 기울기 ≥60° · **양측 손잡이 연속 의무** · 끝 수평 ≥0.3 m · 시·종점 0.3 m 전면 점형블록 폭만큼 · **계단코 줄눈넣기 또는 미끄럼방지재 의무** · 계단코 색상 대비는 **임의** | verified verbatim |
| KS F 4561 | 점자블록 certification standard; product reality 300 × 300 in **60 / 80 mm**, slip **≥40 BPN**, **colour layer ≥8 mm** | spec verified; **revision history NOT VERIFIED** |
| 볼라드 | 교통약자법 시행규칙 **별표2 제7호** — 높이 **80–100 cm** · 지름 **10–20 cm** · 간격 **1.5 m 안팎** · 전면 **0.3 m 점형블록** · 밝은 색 · 충격 흡수 재질 | carried from the in-repo `_dimension_index.md` `[law]`; **the 부령 number/date that put this spec in force was NOT VERIFIED this session** |
| 산업 안전난간 | 산업안전보건기준에 관한 규칙 **제13조** — 상부 난간대 **90–120 cm**; ≥120 cm이면 **중간 난간대 2단 이상, 상하 간격 ≤60 cm**; **발끝막이판 ≥10 cm**; 부재 **지름 ≥2.7 cm 금속제 파이프 또는 동등 이상** | verified — this is the correct citation for **D1 · D2**, which are 산안법 sites, not 건축법 ones |
| 안전보건표지 색도 | 산업안전보건법 시행규칙 **별표8** — Munsell table, §5.2 | verified |

**Instrument chain — all verified `[law]`:**

| Instrument | No. | 공포 | 시행 |
|---|---|---|---|
| 편의증진법 (법률) | **법률 제5332호** | **1997-04-10** | **1998-04-11** |
| 편의증진법 시행령 | 대통령령 제15675호 | 1998-02-24 | 1998-04-11 |
| 편의증진법 시행규칙 (별표1의 출처) | 보건복지부령 **제64호** | **1998-04-11** | 1998-04-11 |
| 교통약자의 이동편의 증진법 | **법률 제7382호** | **2005-01-27** | **2006-01-28** |
| 교통약자법 시행규칙 | 건설교통부령 **제493호** | 2006-01-26 | **2006-01-28** |
| KS F 4561 (시각장애인용 점자블록) | 고시 2001-232 | **제정 2001-04-20** | 개정 2002 · 2008 · 2012 · 2013 · 2016 · **2022** (확인 2007 · 2021) |

### 1.6 ★ The retrofit mandate — it existed, twice, and it closed in 2005

This is the legal engine behind §3.1's RETROFIT-STYLE class, and it is now **verified** `[law]`.

**편의증진법 제9조** is *prospective only* — the duty arises `대상시설을 설치하거나 … 주요 부분을
변경(용도변경을 포함)할 때`. But **부칙 제2조제2항** created a genuine retroactive obligation:

> 이 법 시행전에 설치된 대상시설중 대통령령이 정하는 것은 이 법 시행일부터 **2년 이상 7년내의
> 범위안에서** 대통령령이 정하는 바에 따라 편의시설을 **설치하여야 한다**.

Operationalised by 시행령 **[별표 4]**, which set **two tiers, not three**:

| Deadline | 대상 |
|---|---|
| **2000-04-10** (시행 +2년) | **횡단보도**, 읍·면·동사무소·파출소·우체국·보건소·공공도서관 등 연면적 <1,000 m², 5기 이상 공중화장실, 장애인·노인복지시설, 종합병원, 장애인특수학교, 국가·자치단체 청사 |
| **2005-04-10** (시행 +7년) | 철도역사(통일호 이상 정차역), 도시철도 역사 |

**별표 4 now reads `삭제 <2007.2.12>`** — deleted once the deadlines lapsed.
*(Correction to the project's working assumption of a 2000/2003/2008 three-step schedule: there were only two.)*

**The decisive scope facts** `[law]`:

- 편의증진법 시행령 **[별표 1] 대상시설** has only **four** categories: **공원 · 공공건물 및 공중이용시설 ·
  공동주택 · 통신시설**. **도로 is not among them** — it moved to 교통약자법 on 2006-01-28, and the road
  items in 편의증진법 시행규칙 별표1 now read `삭제 <2007.3.9>`.
- Pre-2006, 도로 *was* covered, and the old 시행령 별표2 제1호 다목 explicitly named **지하도 및 육교**:
  `지하도 및 육교의 출입구 부근에는 점자블록을 설치하여야 한다`.
- **But 지하도·육교 were never on the 별표4 retrofit list.** Only 횡단보도 was, among road items.
- 교통약자법 제11조① likewise triggers only on `설치하거나 … 주요 부분을 변경할 때` — **no retrofit duty**.

**Answers to the two scope questions that decide §3.1 and §4.2:**

| Case | Verdict `[law]` |
|---|---|
| 1960s–80s 달동네 alley stair | **Never bound.** Not one of the four 대상시설 categories; if it is a municipal 도로 it falls under 교통약자법, whose duty is prospective only. **No retrofit obligation has ever applied to it.** |
| 1980s 지하보도 / 육교 | **Was a 대상시설 before 2006 — but never on the retrofit list**, and post-2006 its statute is prospective. **Also not retroactively bound.** |

> **This changes the tone of §3.1's RETROFIT-STYLE cells but not their content.** Those retrofits are
> **discretionary municipal works**, not legal compliance. That is *better* for us: discretionary works
> are partial, uneven, and visibly newer than their host — exactly the look §5 describes. It also
> explains the field data: retrofit where budget and politics reached, absence everywhere else.

**Enforcement asymmetry worth knowing:** 편의증진법 has real teeth (시정명령 §23 → 벌금 §25 → 과태료 §27
→ **이행강제금 3,000만원 이하 §28**). 교통약자법's sanctions attach **only to 제10·11조 (이동편의시설)** —
and **볼라드 lives in 별표2 (보행안전시설물, 제21조), where 설치「할 수 있다」and there is no 시정명령 or
과태료 at all.** The bollard spec is old, stable and effectively unenforceable — which is why §1.7's
non-compliance rates are what they are.

### 1.7 Prevalence, from official statistics `[stat]`

| Measure | Figure |
|---|---|
| **볼라드 non-compliance** | 성남 전수 2011 **42 %** (5,448/12,827) · 전국 2015 **16.3 %** (43,479/266,379) · 서울 2016 **26.9 %** · 경기 31개 시군 2016 **~25 %** · **한시련 현장감사 2017: 부적정 82.3 %** (597/725 횡단보도) |
| **볼라드 failure mode** | **석재/화강석 is the dominant cause** — 서울 2016: 석재 6,666 / 11,084 = **60.1 %**; 충남 3개 시: 화강석 961 / 1,140 = **84.3 %**. 부산 2015 by type: **0.3 m 점형블록 미설치 47.7 %**, 재질불량 38.4 % |
| **서울 육교 accessibility** | 149 surviving (2022-12-31); only **66 (44.3 %)** have any accessibility fitting (엘리베이터 59 / 경사로 6 / both 1) — **83 (55.7 %) have none at all**. Stock fell 248 (2000) → 149 (2022) by demolition |
| **도로 기준적합률** (교통약자 실태조사) | 2021 전국 전수 **77.6 %** · 2023 특·광역시 84.7 % · 2024 도 **71.3 %**. Worst sub-category throughout: **버스정류장 34.6–38.5 %** |
| **건축물 적정설치율** | 2013 60.2 % → 2018 **74.8 %** → 2023 **79.2 %**. **공공 < 민간 in both recent rounds** (2018: 72.4 vs 75.0; 2023: 73.5 vs 79.8) |
| **점자블록 sub-items, 2018 전수조사** | 형태/위치/시공방법 **64–65 %**; the two lowest cohorts **34.7–47.2 %**; **손잡이 점자표기 25.2 %** |
| **Survey cadence** | 실태조사 is **annual**, with a **full census every 5 years** (교통약자법 시행규칙 §11) — *not* a 5-year cycle as previously assumed |

> **"A shabby municipal underpass is more plausible than a shabby shopping mall."** Public facilities
> score *lower* than private ones in both 2018 and 2023. This directly supports 02 · 11 · 16 · 21.

### 1.8 Chronology for period-accurate scenes `[law]`

| From | What becomes required |
|---|---|
| ≥1973 | 계단참 3 m / 난간 1 m / 중간난간 3 m (건축물 only, >200 m²) |
| 1982-10-30 | 손잡이 *duty* where both sides are walls |
| **1992-06-01** | 손잡이 *numeric spec* φ32–38 / 850 mm / ext 300 mm |
| **1998-04-11** | 점자블록 mandated at all (편의증진법 시행규칙 별표1); 계단코 미끄럼방지 mandated |
| **2000-04-10** | retrofit deadline, tier 1 (횡단보도 + small public buildings) |
| **2001-04-20** | KS F 4561 product standard exists |
| **2003-04-22** | 주택 난간 110 → **120 cm** |
| **2005-04-10** | retrofit deadline, tier 2 (철도·도시철도 역사) — **the last retroactive obligation** |
| **2005-07-18** | 옥상·노대 난간 1.1 → **1.2 m** |
| **2006-01-28** | 볼라드 spec (80–100 / 10–20 cm / 1.5 m / 0.3 m 점형블록); 턱낮추기 **3 cm → 2 cm**; 도로 moves to 교통약자법 |
| **2008-07-15** | BF 인증 opens — as a **공고**, not 고시, and with **no statutory basis until 2015-07-29** |
| **2024 →** | first systematic subsidy of accessibility retrofit of **existing** stock (경사로 지원 조례: 2024 ≈ 8, 2025 ≈ 20, 2026 ≈ 16 municipalities) |
| **2026–2027** | 서울시 고지대 이동편의시설 — 승강기 5곳 + **노후 계단 정비 7곳** incl. 계단참·안전난간·미끄럼방지·캐노피 |

### 1.9 Remaining gaps `[unverified]`

1998 original 별표1 exact wording (law.go.kr serves it behind an HWP viewer; earliest verbatim copy is
the 건설교통부 2000-11 지침 reproduction) · KS F 4561 truncated-cone **top** diameter and per-revision
dimension tables (paywalled) · per-sub-item 기준적합률 from 교통약자 실태조사 (full report blocked) ·
대구고법 2019나23163 선고일 · any 감사원 audit on 교통약자법 bollard specs (**not found** — the
93 %-substandard figure circulating online is **airport anti-terror bollards**, a different regime).

---

## 2. Scene era assignment — implied construction decade

`[assumed→argued]` throughout: no scene file states a construction year. The decade is **inferred from
the scene's own identity** (docstring + PARAMS + brief) and argued against Korean urban-development
history `[stat]`. Where a scene is honestly a **two-layer** object — an old structure carrying a later
intervention — both layers are given, because that is exactly what produces RETROFIT-STYLE.

### 2.1 Main 21

| # | Scene | Implied build era | One-line justification `[stat]` |
|---|---|---|---|
| 01 | 캠퍼스 광장 하행계단 | **2000s** | Granite-clad campus plaza with a wide 4-step (0.60 m) drop is the post-1997 campus master-plan idiom; Korean universities rebuilt central plazas through the 2000s as 종합화/BF-conscious granite works. Not a 1970s campus, which was asphalt + planted verge. |
| 02 | 지하보도 | **1980s structure + 2010s remodel** | Korean pedestrian underpasses are a car-priority artefact of the 1966–1990 도시계획 push (Seoul's first, 세종로, 1967); construction effectively stopped in the 1990s. Anything still open in the 2020s has been through a municipal 리모델링 (tiling, lighting, tactile, handrail replacement). Two layers is the only honest reading. |
| 03 | 하천 제방 하행계단 | **1990s–2000s river-improvement works** | Levee access stairs belong to 하천정비 programmes (한강종합개발 1982–86 for the metropolitan case, 지방하천정비 through the 1990s–2000s). A hydraulic structure, **outside 건축법** — see §3. |
| 04 | 공원 산책로 침목 계단 | **2000s** | Railway-sleeper + 마사토 trail steps are the standard 근린공원 산책로 detail of the 1990s–2000s, mass-produced again by the 둘레길 wave from 2009. |
| 05 | 근린공원 야외공연장 | **1990s–2000s** | Neighbourhood-park open-air amphitheatres are a 근린공원 조성 product of the 1990s–2000s 지방자치 park-building era. Seating tiers, not a stair — see the §3 caveat. |
| 06 | 보행육교 나선 진입계단 | **2000s new-build** | A circular spiral approach is not the 1970s–80s straight-flight 육교 idiom; spiral/curved approaches appear when 교통약자 gradient and footprint rules start shaping footbridges, i.e. mid-2000s onward. Treat as a modern footbridge, not a survivor. |
| 07 | 산사 자연석 배석 계단 | **pre-modern, continuously maintained** | Mountain-temple approach paths predate all modern building law. Governed instead by heritage rules (현상변경 허가), which actively *restrain* adding modern safety fixtures. The single most defensible "no fixtures" scene in the corpus. |
| 08 | 선큰 광장 | **2010s** | Sunken plazas connected to 지하상가/지하철 are a 2000s–2010s urban-design product (광화문·청계·판교·세종 generation). Post-dates every statute in §1 — the one scene where full compliance is the realistic default. |
| 09 | 호수공원 수변 계단 | **2000s** | 호수공원 as a type is the new-town park (일산 1996 →동탄·세종 2000s–2010s). Broad terraced water-edge viewing steps without railings are that generation's signature. |
| 10 | 공원 데크 갈지자 | **2010s** | Timber 데크로드 on park slopes is squarely the post-2010 둘레길/무장애 산책로 wave. Modern by construction. |
| 11 | 보도육교 철제 계단 | **1980s structure + 2000s repainting/repair** | Steel pedestrian overbridges peak 1970s–80s; from the 2000s policy reversed to removal or accessibility retrofit. A surviving steel 육교 is an old frame carrying newer paint, newer decking and often a newer handrail. |
| 12 | 한강 수변 캔틸레버 데크 | **2010s** | Cantilevered timber riverside boardwalks belong to the 한강 르네상스 (2007–2011) and its successors. Modern by construction. |
| 13 | 아파트 지하주차 진입부 | **2000s** | Ramped underground parking at this scale implies a post-1990s apartment estate; the canopy + height bar + 차단기 kit is 2000s. Note the ramp interior is **not** an 편의증진법 대상 — see §3. |
| 14 | 대계단 착시 (기념 대계단) | **2000s–2010s** | Marble-clad civic grand stair with an upper viewing plaza and a lower fountain plaza is a 2000s–2010s civic-plaza product. Already carries 3 landings at 2 m spacing `[measured]` — i.e. it was *built* to a modern standard. |
| 15 | 골목 미로 계단 (달동네) | **1960s–1980s, informal** | Hillside settlement fabric: self-built or minimally permitted 1960s–80s, alley widths and stair geometry fixed by the plot pattern, not by code. **Predates every fixture statute in §1.** The corpus's canonical ABSENT-REAL scene. |
| 16 | 캐노피 그림자 계단 | **1990s structure + 2010s canopy/remodel** | An 지하상가-type entrance set in an open sidewalk. Underground arcades are 1970s–80s (을지로·명동 generation), their surface entrances are the part that gets rebuilt; a solid modern canopy over the head of the stair is a later addition, which is why the scene reads two-layer. |
| 17 | 한강 제방 램프-계단쌍 | **1980s levee + 2000s–2010s 둔치 정비** | The levee is 한강종합개발 (1982–86). The paired bicycle/wheelchair ramp is not — ramps beside levee stairs are a 2000s–2010s 자전거도로/무장애 addition. Structurally the clearest RETROFIT-STYLE candidate in the corpus. |
| 18 | 바닷가 벽화(색칠) 계단 | **1970s stair + 2009–2015 art/도시재생 layer** | Mural-village stairs are old settlement stairs that received a public-art and 도시재생 layer from the 마을미술 프로젝트 era (2009 onward, 감천 being the archetype). The paint is new; the stair is not. |
| 19 | 부채꼴 winder (옥상 테라스) | **1990s–2000s private building** | Framed as a low-rise wing's rooftop terrace with an 옥탑 core `[measured]`. Private commercial building; the governing clause is the 옥상 parapet rule, applied at *its* build date. Not an 편의증진법 대상 for tactile. |
| 20 | 사선 사교 계단 (광장) | **2000s** | Generic urban plaza with 축정렬 buildings, bollard rows, planters and lamps — a 2000s public-plaza kit. |
| 21 | 관공서 진입 대계단 | **1990s–2000s** | 관공서/도서관 civic entrance stair. The 1990s–2000s 청사 building wave; the granite parapet + centre rails + nosing set matches that generation's fit-out. |

### 2.2 Batch1 12

| # | Scene | Implied build era | One-line justification `[stat]` |
|---|---|---|---|
| C1 | 눈 덮인 직선 계단 | **2000s** | Generic outdoor concrete straight flight with a one-sided pipe rail — the ubiquitous 2000s public-realm stair. |
| C2 | 낙엽 석계단 | **2000s** | Park stone stair with a one-sided rail; the 근린공원 재정비 idiom. |
| C4 | 젖은 광폭 화강암 계단 | **2000s–2010s** | 6 m-wide granite flight with cheek walls and twin stainless lines = a public-building forecourt of the BF-aware generation. |
| D1 | 물류 하역 연단 | **1990s–2010s industrial** | Logistics dock. Governed by 산업안전보건법, which binds the **employer continuously** — not by construction-date building law. Era matters less here than duty type (see §3 note). |
| D2 | 공사장 슬래브 개구 | **under construction, present day** | A frame-stage slab. Its unguarded opening is a live 산안법 violation, not a legacy condition — the one scene where "no fixture" is a *current* breach rather than a grandfathered absence. |
| D3 | 노변 콘크리트 측구 | **1980s–2000s rural/suburban road** | Open trapezoidal roadside channel on a two-lane asphalt road — a 지방도 detail that stopped being built in urban areas but persists outside them. |
| D4 | 지하철 승강장 | **1990s station, pre-PSD** | Scene deliberately has neither PSD nor safety fence `[measured]`. Seoul's networks were fitted with PSD through 2005–2010, so this reads as an older or a non-PSD regional station — which is exactly how the scene should be captioned. Tactile at the platform edge is nevertheless expected (90 % installed rate, §3). |
| N1 | 그림자 띠 광장 | **2000s–2010s** | Large tiled plaza under a skybridge — modern civic fabric. |
| N2 | 아스팔트 패치 | **road: any era; patch: recent** | The patch is by definition a recent maintenance event on an older surface — a RETROFIT-STYLE object in miniature, and already modelled that way. |
| N3 | 트롱프뢰유 보행자몰 | **2010s** | Pedestrian mall / 차 없는 거리 with floor art is a 2010s programme. |
| N4 | 내리막 완경사 옹벽로 | **2000s** | Retaining-wall-flanked 5 % access road; ordinary modern civil work. |
| N5 | 플러시 그레이팅 보도 | **2000s–2010s** | Concrete sidewalk with linear grating, cast-iron manholes, bollard row and tactile — the current 보도 설치 지침 kit. |

### 2.3 Era distribution `[computed]`

| Era band | Scenes | n |
|---|---|---|
| pre-modern / heritage | 07 | 1 |
| 1960s–80s informal or car-era infra | 15 · 18(base) · 02(base) · 11(base) · 17(base) | 5 bases |
| 1990s | 05 · 16(base) · 19 · 21 · D4 | 5 |
| 2000s | 01 · 03 · 04 · 06 · 09 · 13 · 20 · C1 · C2 · N4 | 10 |
| 2010s | 08 · 10 · 12 · 14 · N1 · N3 · N5 · C4 | 8 |
| present-day / duty-based (not construction-date) | D1 · D2 · D3 · N2 | 4 |

**The corpus is era-lopsided toward the 2000s–2010s** — 18 of 33 scenes post-date every fixture
statute. That is why the five old-base scenes (02·11·15·17·18) carry a disproportionate share of the
realism and decorrelation value, and why converting them to modern compliance would be a double loss.

---

## 3. Cross table — scene × fixture

### 3.0 The three cell classes

| Class | Definition | When it applies | Modelling consequence |
|---|---|---|---|
| **EXPECTED** | The scene's build era post-dates the statute, **or** the site is a public asset under an active retrofit duty and the fixture is cheap enough that it was actually done | 2000s–2010s builds; public sites for tactile/handrail | Build it, compliant, and let it look the same age as the structure |
| **ABSENT-REAL** | Pre-code construction with **no retrofit norm** — private, informal, heritage, or a facility class the statute never covered | 달동네 골목, 민간 옥상, 주차장 내부, 공사장/야드, 하천·문화재 시설 | **Do not build it.** Absence is the correct answer and the research-valuable one |
| **RETROFIT-STYLE** | Pre-code structure + public retrofit duty + a fixture cheap enough to add — present, but **visibly younger than what it is attached to** | 지하보도·육교·제방·문화마을 계단 handrails and tactile | Build it with §5's vocabulary: base plates, mismatched metal, glued pads, cut stubs |

Two rules decide between ABSENT-REAL and RETROFIT-STYLE:

- **Ownership/duty.** Is anyone legally obliged and budgeted to maintain it? Public road, park, station,
  underpass → yes. Private alley, private rooftop, parking-garage interior, construction site, industrial
  yard → no (for accessibility law; 산안법 duties are separate and *do* bind the employer continuously).
- **Cost class.** Retrofits happen for **members** (handrail, tactile pad, nosing strip, paint) and do
  **not** happen for **geometry** (landing, mid-rail, riser change) — because geometry means rebuilding
  the stair. §5.6. This single rule resolves most of the W4 verdicts in §4.

*(A mid-rail is a member and therefore retrofittable in principle; a **landing** is geometry and is
not. That asymmetry is doing most of the work in §4.3.)*

### 3.1 The table

Fixture columns: **HR** = stair handrail (손잡이) · **MR** = mid-rail (중간난간) · **LD** = landing
(계단참) · **GR** = guard/railing at height · **TP** = tactile paving · **BL** = bollard ·
**NS** = nosing strip · **CR** = curb ramp / 턱낮춤.
Cells: **E** = EXPECTED · **A** = ABSENT-REAL · **R** = RETROFIT-STYLE · **—** = fixture not applicable
to this scene's programme.

| # | Scene (era) | HR | MR | LD | GR | TP | BL | NS | CR |
|---|---|---|---|---|---|---|---|---|---|
| 01 | 캠퍼스 (2000s) | E | — | — | E | E | E | E | E |
| 02 | 지하보도 (1980s+remodel) | **R** | **R** | **A** | E(pit) | **R** | E | **R** | **R** |
| 03 | 하천 제방 (1990s–2000s) | **A** | — | **A** | **A** | **A** | E | **A** | — |
| 04 | 공원 흙계단 (2000s) | **A** | — | — | **A** | **A** | — | **A** | — |
| 05 | 야외공연장 (1990s–2000s) | **A** | **A** | — | E(cut wall) | **A** | E | **A** | — |
| 06 | 육교 나선 (2000s) | E | — | **E** | E | E | E | E | E |
| 07 | 산사 배석 (pre-modern) | **A** | — | **A** | **A** | **A** | — | **A** | — |
| 08 | 선큰광장 (2010s) | E | **E** | **E** | E | E | E | E | E |
| 09 | 호수공원 가트 (2000s) | **A** | **A** | E(built) | **A** | **A** | — | **A** | — |
| 10 | 공원 데크 (2010s) | E | — | E(built) | E | **A** | — | E | — |
| 11 | 보도육교 (1980s+repair) | **R** | — | E(built) | E | **R** | E | **R** | **R** |
| 12 | 수변 데크 (2010s) | E | — | — | E | **A** | E | E | — |
| 13 | 아파트 주차진입 (2000s) | E | — | E(built) | E | E(보도만) | E | E | E |
| 14 | 대계단 착시 (2000s–2010s) | E | — | E(built ×3) | E | **A**(identity) | E | E | E |
| 15 | 골목 계단 (1960s–80s) | **A** / R(variant) | **A** | **A** | **A** | **A** | — | **A** | — |
| 16 | 캐노피 (1990s+remodel) | **R** | — | — | E(pit) | **R** | E | **R** | **R** |
| 17 | 한강 램프쌍 (1980s+2000s) | **A** | — | **A** | **A** | **A** | — | **A** | **R**(ramp) |
| 18 | 벽화 계단 (1970s+art) | **A** | **A** | **A** | **A** | **A** | — | **A** | — |
| 19 | 옥상 winder (1990s–2000s) | E | — | — | E(1.2 m 옥상) | **A** | — | E | — |
| 20 | 사선 계단 (2000s) | E | — | — | E | **A**(identity) | E | E | E |
| 21 | 관공서 대계단 (1990s–2000s) | E | E(built ×2) | — | E | **A**(identity) | E | E | E |
| C1 | 적설 계단 (2000s) | E | — | — | E | E | — | E | — |
| C2 | 낙엽 석계단 (2000s) | E | — | — | E | **A** | — | **A**(stone) | — |
| C4 | 젖은 광폭 (2000s–2010s) | E | E | — | E | E | E | E | E |
| D1 | 하역 연단 (industrial) | — | — | — | **A**(산안법 duty, unmet) | **A** | E(corner) | E | — |
| D2 | 슬래브 개구 (site, now) | — | — | — | **A**(live violation) | **A** | — | — | — |
| D3 | 노변 측구 (1980s–2000s) | — | — | — | **A** | **A** | — | — | — |
| D4 | 승강장 (1990s, pre-PSD) | — | — | — | **A**(PSD absent) | **E/R** | — | E | — |
| N1 | 그림자 광장 (2000s–2010s) | — | — | — | **A** | E(bollard) | E | — | E |
| N2 | 아스팔트 패치 (patch: now) | — | — | — | — | E(bollard) | E | — | — |
| N3 | 보행자몰 (2010s) | — | — | — | — | **A**(identity) | E | — | E |
| N4 | 내리막 램프 (2000s) | — | — | — | E(옹벽 상단) | E(bollard) | E | — | E |
| N5 | 플러시 그레이팅 (2000s–2010s) | — | — | — | E(담장) | E(bollard) | E | — | E |

**Counts** `[computed]`: EXPECTED 96 · ABSENT-REAL 63 · RETROFIT-STYLE **12** · N/A 93.

The RETROFIT-STYLE column is concentrated in **five scenes — 02 · 11 · 16 · 17 · 15(variant)** — and
**not one of them is built that way today.** That is the actionable finding of this table: the class
exists in the design, has 12 cells, and has zero implementations.

### 3.2 Prevalence evidence per cell class

| Cell class | Evidence | Strength |
|---|---|---|
| ABSENT-REAL / RETROFIT, alley stair handrail | **Two independent tallies now agree.** (a) n = 12, this project: FREESTANDING_CODE **0/12**, two-flank rails **0/12**, NONE 1/12, minimal one-sided pipe 11/12 `[stat — scene15_railing_fix_v1.md §1.1]`. (b) n = 13 judgeable Gamcheon stair views, hand-counted from Commons `Category:Gamcheon Culture Village` (104 files): **no handrail 2 · thin added rail 11 · code-compliant 0** `[stat]` | **strong** — replicated, per-photo URLs on both sides |
| Commons corpus limits (negative finding) | Categories `Ihwa-dong`, `Changsin-dong`, `Daldongnae`, `Sudoguksan`, `Tactile paving in South Korea`, `Pedestrian overpasses in South Korea`, `Pedestrian underpasses in South Korea` **do not exist** (API: zero members). Korean-term searches `점자블록`/`지하보도` return **0 files**; `육교`/`난간 계단` return 40 each, **none Korean** `[stat]` | **strong** — and it means Commons cannot be the corpus for underpass/footbridge/tactile cells |
| Stair-retrofit programmes (RETROFIT-STYLE justification) | 부산 초량 168계단 (**33°**), 산복도로 르네상스 monorail 2013→2016, **₩3.2 bn**, removed 2023, replaced by an inclined elevator. 서울시 「고지대 이동약자 편의시설」 5 sites, target **2027** — 광진 무지개계단 **37°**, 종로 숭인동 **115 m / 30°+**, 중구 신당동 **113 m / 33°+**; 종로 무악동 '85계단' **₩4.0 bn**. 관악구 은천로 참여예산 2014, **₩10 M**, 사업명 *"계단 폭과 높이가 일정치 않아 위험한 계단정비"*, 공종 = 계단철거 / 계단구조물 설치 / 계단판석붙임 / **난간설치** `[stat]` | **strong** — named projects, years, budgets |
| ABSENT-REAL, alley tactile | sample **0/12**, p ≈ 0.05 `[stat — D_ground_profile_special.md §4.1]` | strong |
| ABSENT-REAL, park tactile | Seoul 2015 full survey: **공원 24 %** adequate `[stat]` | strong |
| RETROFIT-STYLE, alley handrail added later | Busan Ilbo: **147-location** priority stair-handrail retrofit list, with the stated baseline "아직도 계단 손잡이가 없는 골목이 많아" `[stat]` | **medium-strong** — programme documented, per-site counts not obtained |
| EXPECTED, station tactile | Seoul 2015: **지하철역 90 %** adequate `[stat]` | strong |
| EXPECTED/RETROFIT, sidewalk & underpass tactile | Seoul 2015: **보도 430/797 km = 54 %** adequate `[stat]` | strong |
| EXPECTED, public building tactile | 보건복지부 2023: installed **50.98 %**, adequate **45.71 %** `[stat]` | strong |
| Non-compliance is the norm | 한국시각장애인연합회 2023, n = 337 sites: 적정 **4.0 %** / 부적정 **77.3 %** / 미설치 **18.7 %**; 권익위 2018–20 complaint big-data n = 2,847: 파손 1,257 · 점유 603 · 미설치 596 · 오설치 325 `[stat]` | **very strong** — this is why §12.4's "부적정 재현 규칙" exists and why it should be kept |
| Guardrail finish default | 「도로안전시설 설치 및 관리 지침」 2.4.3/2.4.4: white/grey principle, bare galvanized acceptable, primaries avoided, **matt** `[law/spec]` | strong (primary text quoted in-repo) |
| Post anchorage forms | same guideline 2.6 + figs 2.33–2.36: embedded 400 mm / shallow+mortar / **base plate + anchor bolts** `[law/spec]` | strong |

### 3.3 Three field patterns that should become project rules

1. **Korea does not fix the stair. Korea bolts a machine next to it.** 초량 168계단 got a ₩3.2 bn
   monorail beside a 33° flight that was never regraded; when the monorail failed it was replaced with
   an inclined elevator, and the stair is still 33° `[stat]`. Seoul's 2027 programme is the same shape —
   five 30–37° stairs, all getting *lifts*, none getting landings. **This is the definitive answer to
   "would they have added a landing?" — no. They add a machine, a rail, or nothing.**
2. **When a stair *is* touched, the works are demolish-and-reface plus one rail.** The 관악구 line item
   spells the scope out: 계단철거 / 계단구조물 설치 / 계단판석붙임 / 난간설치, for **₩10 M** `[stat]`.
   So the realistic retrofit signature is **new stone facing on old geometry + a single new rail**,
   not a code-conforming rebuild.
3. **Where a site cannot be made safe, Korea posts a prohibition instead.** 대둔산 삼선계단 carries
   *"노약자, 음주자, 어린이의 통행을 금합니다"* `[stat]`. Signage substituting for hardware is a genuine
   Korean pattern and a cheap, high-signal prop — and it fits the project's existing `sign_*` kit.

### 3.4 Gaps this survey did **not** close

`[unverified]` — Mapillary / street-level imagery was unreachable, so there are **no coordinate-anchored
counts for underpass or footbridge retrofits**; Commons has no usable Korean category for either
(§3.2). Sunken plazas produced **no citable evidence at all**. Bollard-noncompliance and
tactile-installation percentages in this document therefore rest entirely on the **in-repo §12.2
statistics**, not on new fieldwork. And no municipal spec exists for alley-handrail bracket spacing or
pipe diameter `[no source]` — §5's φ42.4 field figure remains an observation, not a citation.

---

## 4. Consistency audit of the current scenes

Baseline read of what is actually built today, from the code `[measured]`:

| Fixture | Scenes carrying it in the default build |
|---|---|
| statutory 손잡이 (`stair_kit.build_handrail`) | **02 · 15 · 16** only — the three just converted |
| freestanding guardrail (`build_railing_line`) | 02(pit) · 03 · 07 · 08 · 10 · 11 · 12 · 14 · 16(pit) · 17 · 20 · 21 · C1 · C2 · C4 · D3 · N4 |
| inline stainless rail (scene-local) | 01 (3 lines, h 0.90, mirror stainless `metallic 0.9 / rough 0.35`) |
| `cue_tactile = True` by default | **C1 · C4 · D4** only (+ bollard-front pads in N1·N2·N4·N5, built outside the toggle) |
| `cue_nosing = True` by default | 02 · 11 · 16 · 21 · C1 · D1 · D4 · N3 |
| mid landings already built | 06(north) · 09 · 10 · 11 · 13 · 14 · 15 |
| mid-rail (crossing the flight) | 01 · 21 only |

### 4.1 Re-examination — the three handrail conversions

**scene15 (bare default, `cue_railing=False`; ON builds one wall-bracketed φ34 line) — CORRECT, keep.**
1960s–80s informal hillside fabric predates every fixture statute; the alley is private/공유 fabric with
no retrofit duty; and the photo tally in `scene15_railing_fix_v1.md` §1.1 found **0/12** two-sided code
guardrails and **0/12** stairs railed on both flanks `[stat]`. Bare-by-default is the ABSENT-REAL answer
and it is the corpus's single best `cue− / label+` sample. *One refinement, not a correction:* the same
report's §1.3 shows the "ordinary alley" photos were sampled **from stair-retrofit news coverage**, and
Busan Ilbo's own baseline line — "아직도 계단 손잡이가 없는 골목이 많아", against a **147-location**
priority retrofit list `[stat]` — means both states are real. So scene15's `cue_railing=True` variant
should be re-labelled from "the compliant version" to "**the retrofitted version**", and built in §5's
retrofit vocabulary (single thin pipe, mismatched paint, base plates on the stair edge), not as a clean
code handrail. That is a look change inside an existing toggle, not a new fixture.

**scene02 (post-mounted φ34 statutory handrail) — CORRECT as a fixture, but it is a RETROFIT and should
look like one.** A 1980s underpass is pre-code for the §15 handrail spec; what makes it plausible is
that underpasses are 도로 부속물 on a municipal maintenance budget with an accessibility-retrofit duty
behind them, and remodelled underpasses are exactly where new stainless handrails appear. The scene
therefore lands in **RETROFIT-STYLE, not EXPECTED**. Practical consequence: build the handrail in
brushed STS304 on **visible base plates** anchored into the old treads, with the plate bedding and drill
scars of §5.0/§5.5 — currently it is a clean φ34 pipe on plain posts `[measured]`, which reads as
original equipment and quietly asserts that the whole stair is modern.

**scene16 (4 post-mounted lines) — CORRECT, same class, weaker case.** Same reasoning as 02 with a
1990s base and a later canopy. Note the report's own caveat that scene16's walls are "a partial pit
surround rather than a full flanking pair" — the §15③ 양쪽 벽 reading is thinner here than in 02.
It survives because width 3.00 = 2 × `wall.y_in` 1.50 `[measured]`, but if the W2-D render shows the
walls not reading as flanking walls, this is the one of the three to revisit.

**Also flagged: scene01's rails are era-inconsistent in *material*, not in existence.** A 2000s campus
plaza legitimately has handrails, and at 0.60 m total drop they are 초과 설비 rather than statutory
`[measured — stair_compliance_v1.md]`. The defect is that they are **mirror stainless** — per
「도로안전시설 지침」 2.4.3/2.4.4 the Korean default is matt galvanized or white/grey, matt, primaries
avoided `[law/spec]`. Mirror stainless everywhere is a look bug that flattens the very age signal this
survey exists to create. Cheap fix, no geometry, no GT.

### 4.2 Re-examination — the §12.4 tactile ON list

The registry's own gate is *① statutory trigger ∧ ② p ≥ 0.50 ∧ ③ no identity conflict ∧ ④ GT gates*
`[measured — ground_kit_spec_v1.md §12.3]`, and its p-values already come from national installation
surveys, not from law. **Because tactile paving is a member-class retrofit (glue a pad down) rather
than a geometry change, and because public facilities carry a genuine retrofit duty, the registry is
era-consistent as written.** Per-entry:

| Entry | Era read | Verdict |
|---|---|---|
| **D4** 승강장 (ON, keep) | 1990s station | **Keep.** 90 % installed rate is the highest of any facility class `[stat]`; platform-edge tactile is the most-retrofitted item in the country. Consistent even for an old station |
| **02** 지하보도 (ON new) | 1980s + remodel | **Keep — but build it glued-on/proud (§5.3), not flush.** Flush = repaved with the block; proud = added later. The era says added later |
| **11** 보도육교 (ON new) | 1980s steel + repair | **Keep, retrofit-style.** Same reasoning as 02 |
| **01** 캠퍼스 (ON new) | 2000s | **Keep, flush/EXPECTED.** Post-dates the statute; built-in is correct here |
| **08** 선큰광장 (ON new) | 2010s | **Keep, flush/EXPECTED.** The one scene where seamless compliance is the realistic look |
| **16** 캐노피 주출입구 전면 (ON new ★) | 1990s + remodel | **Keep** — and it is doing double duty as the `cue+ / label−` sample. Retrofit-style pad |
| **13** 아파트 보도부 (ON new, ramp interior forbidden) | 2000s | **Keep.** The 램프 내부 exclusion is exactly right: parking-garage interior is not an 편의증진법 대상 |
| **C4 / C1** (ON keep) | 2000s–2010s | **Keep.** Both are scene-identity uses (survives wetting / gets buried by 5 cm snow) |
| **N1·N2·N4·N5** bollard-front (ON keep + shape fix) | 2000s–2010s | **Keep.** Modern sidewalk kit; the §12.5 legibility fix stands |
| **15** 노후 골목 (OFF) | 1960s–80s | **Keep OFF.** Sample 0/12 `[stat]`, p ≈ 0.05, and pre-code besides. Double-justified |
| **17 · 05 · 09 · 10 · 12 · 03 · 04 · 07** (OFF) | park / river / temple | **Keep OFF.** p = 0.24 for parks `[stat]`; 03·07·09 are outside the 대상시설 net entirely |
| **14 · 20 · 21 · N3** (OFF, identity conflict) | 2000s–2010s | **Keep OFF, but note the honesty cost.** These are modern civic builds where tactile *would* exist; the exclusion is a research decision (it would destroy the concealment), not an era claim. Document it as such rather than as realism |
| **18 · 19** (OFF) | 1970s stair + art layer / private roof | **Keep OFF.** 19 is a private rooftop = not a 대상시설. 18 is a pre-code village stair whose only intervention was paint |
| **06** (HOLD) | 2000s footbridge | **Resolve to ON at the ground-level entry only.** A 2000s footbridge post-dates the statute, so the era argues for presence; the open question was only the "전폭" definition on a spiral, which the single entry point answers |
| **D1 · D2 · D3** (OFF) | industrial / site / rural | **Keep OFF.** Not 대상시설. D1's in-code "why not installed" note remains the model to copy |

**Net: the §12.4 list needs no membership change** (one HOLD resolved). What it needs is a
**construction attribute per entry — 매립식 (flush) vs 부착식 (glued-on)** — driven by the era column of
§2, because that is what makes 02/11/16 look 1980s-with-a-2010s-pad instead of uniformly modern. The
attribute is now **statutorily named** (§5.3), not invented.

**Scope check, now resolved `[law — §1.6]`.** The registry's entries were justified on prevalence
(`p ≥ 0.50`). The legal position turns out to be:

- **지하도 and 육교 *were* 편의증진법 대상시설 before 2006** — the old 시행령 별표2 제1호 다목 said
  `지하도 및 육교의 출입구 부근에는 점자블록을 **설치하여야 한다**` — and moved to 교통약자법 in 2006.
- **But they were never on the 별표4 retrofit list** (only 횡단보도 was, among road items), and both
  statutes' duties are otherwise **prospective only**.
- So **02 · 11 · 16's tactile is a discretionary municipal work, not a legal obligation.** The
  registry's prevalence-based justification stands unchanged and is in fact the *correct* basis.
- Hard confirmation from the field: of **149 surviving Seoul pedestrian overpasses (2022-12-31), only
  66 (44.3 %) have any accessibility fitting at all; 83 (55.7 %) have none** `[stat]`. **More than half
  of real 육교 are bare.** This is direct support for keeping scene11 partial rather than fully fitted —
  and for building at least one `cue_tactile=OFF` 육교 variant as the *majority* case.

### 4.3 W4 planned GT changes — verdicts for supervisor ruling

Source of the plan: `stair_compliance_v1.md` §4 (the five landing insertions that move GT) and §2
(mid-rail and handrail gaps). **Prior approval is not treated as final here, per the assignment.**

**First, a correction that reorganises this whole section.** §1.3 establishes that the landing, guard
and mid-rail rules are **1973-vintage**, not modern. So "this stair is from 1978, therefore exempt" is
**not a valid argument** and must not be used. The valid arguments are, in order:

1. **Scope.** 건축법 §15 governs the stairs *of a 건축물*. A 지하보도, a 육교, a 하천 제방 계단, a
   골목 계단 and a 공원 산책로 계단 are 도로 부속물 / 하천시설 / 도시공원시설 — **never covered, in any
   era** `[law — §1.3]`. This is the load-bearing argument for 02·03·11·15·17·18 and it does not decay.
2. **Vesting.** Where 건축법 *does* apply, the standard is fixed at the **permit-application date**
   `[law — §1.2]`.
3. **Cost class.** §3.0: **a landing is geometry.** Inserting a 1.20 m landing means demolishing and
   rebuilding the flight, extending the run by 1.20 m, and — in four of the five cases — moving the
   structures around it (`stair_compliance_v1.md` §4 documents run +1.20 for 02/03/08/17 and a full
   sector redesign for 06). **Nobody retrofits that.** So "add a landing" is never a compliance fix on
   an existing stair; it is a claim that the stair was rebuilt.

The verdicts below are unchanged by this correction — but their *reasons* are, and the reasons are
what the supervisor is being asked to rule on.

| Item | Scene | Era | Verdict | Reasoning |
|---|---|---|---|---|
| **L1 landing** | **02** 지하보도 (3.20 m, 20단 직통) | 1980s base | **CANCEL — out of statute scope** | A 지하보도 is a **도로 부속물, not a 건축물**, so 건축법 §15①1 never reached it in any era `[law — §1.3]`. (Note the era argument alone would *fail* here: the landing rule is 1973-vintage.) Landings are geometry and are never retrofitted. A 20-step continuous underpass flight is what actually exists; caption it as intentional 규정 미달, which is the project thesis. Cancelling also protects the scene's identity — the run extension moves the pit edge and the grazing-concealment geometry |
| **L1 landing** | **03** 하천 제방 (3.20 m) | 1990s–2000s river works | **CANCEL — out of statute scope** | 하천시설, outside 건축법 `[law — §1.3]`; the repo's own audit already says "하천시설은 건축법 밖이라 **현실적**. 유지" `[measured]`. Additionally the insertion would push the stair 1.20 m toward the water and force re-derivation of the waterline/staining band `[measured — §4]` — cost with no realism gain |
| **L1 landing** | **06** 육교 나선 (4.99 m) | 2000s new-build | **EXECUTE — but on the 도로 지침 basis, not 건축법** | A 육교 is also a 도로 부속물, so 건축법 §15 does not bind it either `[law — §1.3]` — the earlier "its era post-dates the statute" reasoning was wrong and is withdrawn. What survives is that a 2000s footbridge is designed under 도로 / 입체횡단시설 guidance and 교통약자법 이동편의시설 기준, and a **5 m continuous spiral with no rest landing is not something that generation builds**. Verdict stands, reason replaced. Highest-cost item (sector redistribution, column, fascia) — schedule as its own work item |
| **L1 landing** | **08** 선큰광장 (4.50 m) | 2010s | **EXECUTE as planned** | 2010s build post-dating every statute; a 26-step continuous flight in a 2010s civic sunken plaza is not credible. Accept the documented consequence that the bowl widens 1.20 m per flight and the lower plaza plane expands `[measured — §4]` |
| **L1 landing** | **17** 한강 램프쌍 (3.20 m) | 1980s levee + 2000s 둔치 | **CANCEL — out of statute scope** | The stair belongs to the levee: **하천시설, outside 건축법** `[law — §1.3]`; only the ramp is the modern addition. Adding a landing also breaks the scene's whole reason to exist — the stair/ramp contrast pair depends on aligned run lengths `[measured — §4]`. Instead spend the budget on making the **ramp** read as the retrofit (§5): newer concrete, different joint pattern, a butt joint against the old levee |
| **R1 mid-rail** | **02** (1 line) | 1980s | **CONVERT to retrofit-style, or CANCEL** | Not statutorily required (도로 부속물, §1.3), so this is a *realism* call, not a compliance one. A mid-rail is a **member**, not geometry — so unlike the landing it is retrofittable, and Korean underpass flights of this width do sometimes get a centre pipe added. **Recommend: a single centre pipe on base plates, stainless, no infill** — the exact form the scene15 survey found most often (single centre pipe, 5/11 of railed cases) `[stat]`. Do **not** build it as a code guardrail with balusters |
| **R1 mid-rail** | **08** (1 line) | 2010s | **EXECUTE as planned** | Post-dates the statute; compliant mid-rail is the correct modern look |
| **R1 mid-rail** | **09** 가트 (3 lines) | 2000s lake park | **CANCEL — real cases outrank code** | The scene's identity is 무난간 water-viewing steps, and the repo's own audit records that as matching real practice `[measured]`. Three mid-rails across a 10 m viewing terrace would be a code-correct fabrication with no field support. This is the clearest "real cases outrank code" cell in the corpus |
| **R1 mid-rail** | **18** 벽화계단 (2 lines) | 1970s stair + art layer | **CANCEL — out of scope + real-case** | A public village stair, not a 건축물 stair `[law — §1.3]`; the only intervention it ever received was paint. Rails would erase both the scene's identity and its era |
| **R1 mid-rail** | **05** 티어 (8 lines) | 1990s–2000s | **CANCEL — already held, now with a statutory basis** | Seating tiers, not a stair; `stair_compliance_v1.md` already excludes it `[measured]`. §1 strengthens this: the D1 "옥외계단 단높이 ≤200" test the audit applied comes from **주택건설기준 §16①, which binds 주택단지 only** — a neighbourhood-park amphitheatre is not one. The riser-0.400 "violation" is not a violation at all |
| **Nosing** | corpus-wide | mixed | **EXECUTE, selectively, per STATUS ruling** | STATUS.md already carries the user decision: 법률 기반 설치하되 **현실 기반 선별**(석재 계단 등 실제 없는 유형 제외). Era refines it: for **pre-code scenes (02·11·15·18)** nosing is an **add-on strip** with screw heads and wear mismatch (§5.4), for **2010s scenes (08·10·12·14)** it is cast/inset, and for **stone/heritage (07) and natural (03·04·09)** it stays absent |
| **Handrails corpus-wide** | 03·04·08·09·12·14·17·19·21·C1·C2 | mixed | **EXECUTE only where era + duty allow** | The §4 note "손잡이 33씬 전부 미구현 → 가장 먼저 착수" is correct as a *look* judgement (the ≥300 mm horizontal end extension is a strong Korean silhouette signature) but must not be applied uniformly. 03·09·17 are 무난간 by identity **and** by era; 07 is heritage; 19 is a private roof. Apply to 08·14·21·C4 (modern civic) as built-in, and to 11·18 as retrofit-style |

**Summary of the W4 verdicts: 3 EXECUTE (06 · 08 landings, 08 mid-rail), 1 CONVERT (02 mid-rail →
single centre pipe, retrofit-style), 6 CANCEL (02 · 03 · 17 landings; 05 · 09 · 18 mid-rails), and
nosing/handrails become era-conditional rather than corpus-wide.** The consolidated sheet is §6.1.
The two landings that survive are the two whose sites are **not** 하천 or 도로 infrastructure.

### 4.4 Top mismatches in the corpus as it stands today

Ranked by how much they contradict this document's principle:

0. **★ The tactile dot diameter is now the Japanese figure, not the Korean one — the B7 ruling
   inverted it.** Commit `c4e3044` moved `TACTILE_DOT_D_MM` **38.1 → 25 mm**, citing "관행 22~25".
   That band is the **JIS T 9251** value (**22 mm**). **KS F 4561 specifies a 35 mm dot base at 50 mm
   pitch** `[stat — 신동홍·성기창·김상운, 「신형 점자블록 개발을 위한 설계원칙 설정 연구」,
   한국의료복지건축학회지 22(1), 2016, Table 10, comparing KS F 4561 / JIS T 9251 / ISO 23599]`.
   Korea's Φ:I ratio of **1 : 1.43** is the *densest* of every standard surveyed — Korean tactile dots
   are visibly fatter than Japanese ones, and that is one of the few things that makes a Korean block
   recognisable at a glance. **The old 38.1 mm was within 9 % of the Korean spec; the new 25 mm is
   29 % under it and sits on the Japanese value.** This is exactly the "서구/일본 에셋을 쓰면 네트워크에
   틀린 사전지식을 가르친다" failure that `ground_kit_spec_v1.md` §12.1 warns against — committed by us,
   in the opposite direction.
   - Note the statute does **not** specify any diameter (편의증진법 별표1 제16호 is silent), so 25 mm is
     **not illegal** — it simply is not the Korean product.
   - **Confidence: MEDIUM.** Single peer-reviewed source; the KS text itself is paywalled and the
     truncated cone's *top* diameter is unverified. **Recommend procuring KS F 4561:2022 before
     re-ruling**, and treating this as a flagged contradiction rather than an immediate revert.
   - Related, and free: KS/지침 set a **maintenance threshold — a 점형 block is officially due for
     replacement once dot height falls to ≤3.5 mm** (선형 ≤3.0 mm), i.e. **~42–50 % dot wear is
     functional failure** `[stat]`. That gives a principled worn-state target instead of an invented one.

1. **scene15's `cue_railing=True` variant is described as the compliant version.** For a 1960s–80s
   alley it should be described and built as the **retrofit** version. Mislabelling, not misgeometry.
   **And the retrofit is brand new, not weathered** — Korea only began systematically subsidising
   accessibility retrofit of *existing* stock in **2024**, and Seoul's 노후 계단 정비 (7 sites, incl.
   계단참·안전난간·미끄럼방지) is a **2026 착공 / 2027 완공** programme `[stat]`. So at the corpus's
   present day the alley-stair handrail is either **absent** or **days old**: bright unweathered
   stainless on fresh base plates against 1970s concrete. That is a far stronger contrast than a
   generically aged rail, and it is free.
2. **scene02 and scene16 handrails are built clean.** Correct fixture, wrong age — they currently
   assert that a 1980s underpass is a modern structure. Needs §5.0 base plates and §5.1 material mismatch.
3. **scene01's mirror stainless** contradicts the Korean matt-galvanized/white-grey default `[law/spec]`
   and is copied across the corpus's rail material.
4. **Uniform rail height 0.90 m outdoors — and the corpus is missing a free era tell.**
   `build_railing_line`'s non-LOOK_GEO default is 0.90 m, which is the *indoor / mid-flight* value.
   Outdoors the values are **110 cm (도로 지침 표준)** and, for 옥상·노대, **1.1 m before 2005-07-18 /
   1.2 m after** — apartments **1.1 m before 2003-04-22 / 1.2 m after** `[law — §1.1]`.
   That date split is the cheapest era signal we will ever get: **scene19 (1990s–2000s private rooftop)
   should carry a 1.1 m parapet/guard, not 1.2 m**, and the audit note calling its h 1.0 "법령 미달 vs
   1.2" `[measured — C4_scene_props]` is measuring against the wrong-era number. Under-height everywhere
   is a wrong default; *correctly-dated* height is a feature.
5. **Every railing in the corpus is the same object.** Same material, same 3-bar profile, same era.
   Real Korean scenes mix painted-steel 1980s, galvanized 1990s and stainless 2010s within one frame.
   This is the largest single realism lever this survey identifies and it costs no geometry.
6. **scene14 already has 3 landings at 2 m spacing** — denser than the 3 m rule `[measured]`. Fine for
   a 2010s civic stair, but it means 14 is the corpus's *most* compliant stair while 02/03/17 are the
   least; that spread is good, and should be preserved rather than levelled by the W4 round.
7. **The corpus has no glued-on tactile anywhere.** All tactile is flush, i.e. all of it claims to have
   been laid with the pavement. On 02/11/16 that is an era contradiction — and §5.3 shows 편의증진법
   별표1 제16호 **positively authorises 부착식** for exactly this case, so the fix is law-backed.
8. **All tactile in the corpus is uniformly saturated yellow.** Real worn tactile is **grey along the
   walked line with yellow surviving only at the edges**, because the colour is a ≥8 mm surface layer
   that abrades `[stat — §5.3]`. Uniform yellow = brand new. This affects every ON site including the
   ones §4.2 keeps.
9. **The 달동네 stairs are too gentle.** Documented hillside-stair gradients in active retrofit
   programmes are **30–37°** (초량 33°, 무지개계단 37°, 숭인동 30°+, 신당동 33°+) `[stat]`. scene15 is
   0.170/0.300 = **29.5°** and scene18 is 0.160/0.340 = **25.2°** `[computed]` — both at or below the
   bottom of the real range, scene18 well below. **Not a W4 action** (riser/tread is frozen hazard
   geometry), but it should be recorded: our 달동네 and mural-village stairs read as gentler than the
   real ones, and any future geometry revision should steepen rather than soften them. Note the
   supporting legal fact: since 1999 there is **no riser/tread cap at all** for these (§1.4), so a
   steeper stair is not a violation — it is the norm.
10. **scene19's parapet is measured against the wrong-era number** — see mismatch 4. A 1990s–2000s
    private rooftop wants **1.1 m**, not 1.2 m.
11. **Two scene-specific look options this survey surfaced, neither currently modelled:**
    (a) **scene07** — Korean temple/pilgrimage stairs *do* commonly carry a **rustic brown steel-pipe or
    timber post-and-rail**, slender posts ~60–80 mm at 1.5–2 m centres, two horizontal rails,
    deliberately weathered, **no stainless / no tactile / no nosing** `[stat — 팔공산 갓바위]`. The
    scene's unguarded side slope stays as identity; this is a candidate variant, not a defect.
    (b) **scene10 / scene12** — the surveyed park boardwalk rail is **not** a 1.2 m guardrail but a
    **single square top rail at ~45–60 cm on timber posts at 1.8–2.2 m centres**, no mid-rail, no
    balusters — an *edge marker* `[stat — 순천만]`. Our decks carry h 1.05 with infill. Both are real
    (theirs is on-grade, ours is over a 6.6 m drop and over water), but the low edge-marker form is a
    legitimate and much more distinctive variant for any low-level deck run. Deck boards were measured
    at **100–120 mm wide with 5–8 mm gaps**, greying along the walked centreline — which also answers
    the open "데크 판재 틈이 모델링돼 있지 않다" item in `cue_arrangement_survey` §4.2 `[measured]`.


---

## 5. RETROFIT-STYLE visual vocabulary — build specs for the W3/W4 kits

This is the section that turns the principle into geometry. A retrofit is not "the same fixture,
present". It is a **visibly younger part bolted onto a visibly older structure**, and every one of the
tells below is cheap to model and reads at robot height.

### 5.0 The single most important tell

> **The post does not grow out of the ground. It stands on a plate that is bolted to the ground.**

`korean_pedestrian_geometry.md` §1.5 already establishes this from 「도로안전시설 설치 및 관리 지침」
2.6 `[law/spec]`: post anchorage is one of three types —

| Method | Condition | Reads as |
|---|---|---|
| 매입 (embedded) | embed depth **400 mm** | original, cast with the structure |
| 매입 (shallow) | < 400 mm, **mortar-packed around the post** | original-ish, with a visible mortar collar |
| **베이스 플레이트 + 앵커볼트** | on top of an existing curb/structure | **retrofit** — the diagnostic form |

The guideline's own note gives the reason a base plate reads as *newer*: anchor bolts and plates are
supposed to be set **before the concrete is poured**. When you see a plate sitting on a finished,
weathered surface with expansion anchors through it, the fixture post-dates the slab. That is the whole
signal, and our current posts are bare cylinders penetrating the ground `[measured — §1.5]`, which is
why they read as CG.

Repo-sanctioned build values (already tagged `[estimate]` in §1.5, keep the tag):
plate **120 × 120 × t9 mm**, **4 × φ16 anchor bolts at 90 mm pitch**, one **levelling nut course**
under the plate. Add a **mortar/epoxy bedding smear** 5–15 mm proud around the plate edge and a slight
tone break in the slab under it — the plate is newer than what it sits on, and the drill dust ring
never fully cleans off.

**Partially verified against the market** `[stat]`: **100 × 100 mm** steel base plates in **6T / 8T / 9T**
are standard catalogue stock (range 100×100×6T up to 350×350×12T), and the normal fixing into existing
concrete is a **세트앵커 / 스트롱앵커 in SUS304**. So prefer **100 × 100 mm** over the repo's 120 — it is
the real stock size. **Bolt count and embedment depth remain `[no source]`** — keep those tagged.

### 5.0b Korean stainless detailing — the shape vocabulary

These recur across independently sourced photographs and should be treated as the house style, not as
one-offs `[stat]`:

- **Polished spherical newel ball** capping terminal posts. Instantly Korean; almost never seen on
  Western handrails.
- **Curved goose-neck return** where the rail turns down and back into the post at the bottom of a
  flight, instead of stopping square.
- **Turned / beaded ring grooves** machined into balusters — a 1990s–2000s signature.
- **Balusters at roughly 100 mm centres**, which is also what the ≤100 mm 안목 rule produces.
- **A row of inverted-U stainless hoop guide rails across the stair head**, perpendicular to travel.
  Observed at both 삼일공원 and a 2024 station exit — a **standard fixture**, and we have none.

### 5.1 Metal and finish — the age ladder

Korean pedestrian metalwork sorts by era, and the sort is visible:

| Era of the fixture | Typical stock | Finish | Look values |
|---|---|---|---|
| 1970s–80s original | painted mild steel pipe | site-painted, repainted many times, thick edges, chipping to red-lead or rust | albedo 0.20–0.35, roughness 0.55–0.75, chip/rust decals at joints and feet |
| 1990s–2000s | **hot-dip galvanized (용융 아연도금)** steel pipe | 무광 아연도금 회백색 — the guideline's own default (2.4.3/2.4.4: 흰색 또는 회색 원칙, **아연 도금된 그대로도 무난**, 원색 회피, **무광택**) `[law/spec]` | albedo ~0.45–0.55, **roughness 0.45–0.60**, metallic mid, faint spangle, white bloom in crevices |
| 2000s–2010s retrofit | **STS304 round tube** | mill/brushed stainless, unpainted | metallic 0.9 but **roughness 0.30–0.40** (not mirror), brushed-direction anisotropy along the tube axis |

**Diagnostic mixed state:** a retrofit line is stainless *while the structure it is bolted to is
painted-steel-era or bare concrete*. `korean_pedestrian_geometry.md` §1.6 already warns that our
current mirror-stainless default (`metallic 0.9, roughness 0.35`) is wrong for guardrails generally —
correct reading: **galvanized matte is the default for guardrails, stainless is the marker of a
recent handrail/bollard**. Used deliberately, that mismatch *is* the retrofit cue.

Field-stock note carried over from `scene15_railing_fix_v1.md` §1.4: the code grip is **φ32–38**, but
real retrofit handrails are commonly **φ42.4 STS304** commercial stock — i.e. the field routinely
exceeds the statutory grip. Keep φ34 as the compliant default and log φ42.4 as the **retrofit
variation** value, not as an error.

### 5.2 Colour — what is actually specified, and what is actually built

**There is no national colour standard for pedestrian handrails** `[stat — searched; none found]`.
The only statutory colour table in this domain is 산업안전보건법 시행규칙 **[별표 8] 안전보건표지의
색도기준** `[law]`, which is for *signage*, not railings, but is the right source for hazard banding:

| 색채 | Munsell (statutory) | 용도 | approx. sRGB `[computed — conversion is ours, not official]` |
|---|---|---|---|
| 빨간색 | **7.5R 4/14** | 금지·경고 | ~`#BE192D` |
| 노란색 | **5Y 8.5/12** | 경고 | ~`#F0BE00` |
| 파란색 | **2.5PB 4/10** | 지시 | ~`#0B5FA5` |
| 녹색 | **2.5G 4/10** | 안내 | ~`#00824A` |
| 흰색 | **N9.5** | 보조 | ~`#F2F2F2` |
| 검은색 | **N0.5** | 보조 | ~`#0D0D0D` |

> Use `5Y 8.5/12` for D1's 황·흑 hazard band and for nosing strips instead of an invented yellow.
> **`TACTILE_YELLOW` is still `[estimate]`** — 별표1 says only "원칙적으로 황색", no coordinates.

Railing colours **observed in the field**, each from a directly inspected photograph `[stat]`:

| Colour | Where | Era read |
|---|---|---|
| **Bare stainless, uncoated** | 삼일공원 · 감천 · 부산 40계단 · 인천시청역 | 1990s–2020s retrofit and new-build alike — the default |
| **Dark grey / black painted pipe on wall L-brackets** | 감천 alley walls | oldest surviving layer |
| **Brown / rust-brown "rustic"** | 팔공산 갓바위 · 감천 · 순천만 데크 | nature/heritage settings, deliberate |
| **White + mid-blue panel infill, ball finials** | 육교 stairs, early-2000s | 2000s 육교 signature |
| **Full green** (rails + cladding + canopy) | 신길온천역 1번 출구, 2024 | current municipal refit palette |
| **Yellow with black diagonals** | 감천 cast concrete barrier | hazard element, not a rail |

> **Correction to the draft above:** the 도로안전시설 지침's "white/grey, primaries avoided, matt" is a
> *road-facility* rule and it is **not** what pedestrian stair railings actually look like. Bright green
> and white-and-blue are both real and current. Do not over-apply the matt-galvanized default to stair
> handrails; apply it to bridge and road guardrails, where it belongs.

- Repainting tell: retrofit repaint does not reach behind brackets or into the underside of the top
  rail. Model as a **tonal split** — top and outboard faces one value, underside and the post-to-rail
  junction darker and dirtier.
- **Galvanized fails at the joints first.** In 동피랑, a galvanized railing shows **orange rust bleeding
  at welds and post bases while the upper rail is still dull silver** `[stat]`. Rust-map the welds and
  the feet, not the whole member.

### 5.3 Tactile paving retrofitted onto existing pavement

Two constructions, and they look different:

| Construction | Where | Tell |
|---|---|---|
| **매립형** — the block *is* the paver, laid with the pavement | new build / full repaving | joints line up with the surrounding paver grid, same top plane, same wear |
| **접착식 (glued-on)** — a pad adhered onto finished pavement | **retrofit** | pad sits **proud**, its outline **ignores the paver grid**, edges are chamfered or trimmed with a strip, adhesive squeeze-out darkens the perimeter, corners lift and chip first |

**The statute names both, and names the retrofit case explicitly** — 편의증진법 시행규칙 별표1
**제16호 점자블록** `[law]`:

> 점자블록은 **매립식**으로 설치하여야 한다. 다만, 건축물의 구조 또는 바닥재의 재질 등을 고려해볼 때
> 매립식으로 설치하는 것이 불가능하거나 **현저히 곤란한 경우에는 부착식으로 설치할 수 있다**.

Embedded is the rule; **surface-applied is the legally sanctioned exception — and "the floor already
exists" is exactly that exception.** So the glued pad is not a defect to be excused, it is the lawful
retrofit construction. Same 별표 also gives: 0.3 × 0.3 m, height **equal to the surrounding floor**,
점형 **36 dots (6×6)** 반구형/원뿔절단형 **0.6 ± 0.1 cm**, 선형 **4 bars** 상단부평면형 **0.5 ± 0.1 cm**,
colour **원칙적으로 황색**, and outdoors *"햇빛이나 불빛 등에 **반사**되거나 눈, 비 등에 **미끄러지기 쉬운
재질**을 사용하여서는 아니 된다"* — the clause that the widely-sold **stainless stud** tactile violates,
which is itself a good non-compliance prop.

Product reality `[stat]`: cast pavers are **300 × 300 mm in 60 mm and 80 mm** thickness, certified to
**KS F 4561**, slip resistance **≥40 BPN**, and the **colour layer is ≥8 mm thick**.

For a retrofit cell, build tactile as an adhered pad: **proud +6…+12 mm** including the base
(vs flush for 매립식), a **1–2 mm dark perimeter line** (adhesive/dirt), **pad outline not aligned to
the joint grid**, and 1–2 tiles showing **corner loss or a replaced tile in a slightly different yellow**.

**How it actually weathers — the highest-value detail in this section.** The yellow is a *surface colour
layer*, so it **wears off along the walked path first, leaving bare grey concrete with only ring-shaped
outlines where the dots are** `[stat — Gamcheon photo set, two files directly inspected]`. An old
tactile run in a busy line is therefore **grey with yellow surviving only at the edges**, not uniformly
yellow. In Gamcheon, mural paint has additionally been rolled straight over the top of the blocks.
This single observation matters more than the geometry: our current `TACTILE_YELLOW` constant paints
every block the same saturated yellow, which is the look of a **brand-new** installation only.

**GT note:** even the proud retrofit pad is 6–12 mm and therefore still **not a drop** — GT class A,
z-invariant, consistent with `ground_kit_spec_v1.md` §12.4. It does interact with `GT-E1′`
(`|x_e| ≥ 40·z_e`): at 12 mm the required clearance rises to **0.48 m > the statutory 0.30 m position**
`[computed]`, so a *proud retrofit* pad at the statutory position needs the same `GT-E2-x` /
`EXPECTED_FP` registration the flush one already has, and should not be introduced without it.

### 5.4 Anti-slip nosing retrofitted (논슬립)

- Original-era stone and granite stairs frequently have **no nosing strip at all** — and STATUS.md
  already carries the user ruling: *"계단 노징: 법률 기반 설치하되 **현실 기반 선별**(석재 계단 등
  실제 없는 유형 제외)"*. That ruling is era-consistent and this survey does not disturb it.
- **The statutory alternative is grooves, not a strip.** 편의증진법 별표1 제8호 마.(2) requires
  *"계단코에 **줄눈넣기를 하거나** 경질고무류 등의 미끄럼방지재로 마감"* `[law]` — so a compliant
  **original** stair can legitimately have **cast-in scored grooves and no strip at all**. A visible
  surface-applied metal strip is therefore *almost always* an add-on. This is a clean, cheap way to
  make original-vs-retrofit legible on the same geometry.
- **Retrofit nosing, verified product spec** `[stat]`: aluminium profile **60 mm wide**, lengths
  **600–790 mm in 10 mm increments**, ceramic-grit anti-slip insert, stock colours
  **black / grey / green / marble / yellow / purple / wine**. Other stock profiles **45 × 23 mm** and
  **63 × 20 mm**. Installation sequence: clean substrate → optionally drill and insert 칼블럭 →
  spread adhesive → press home by hand or rubber mallet.
- Tells, following directly from that sequence: **either** a regular row of screw heads **or**
  **adhesive squeeze-out along both edges**; a **height step** where the strip stands proud of the
  tread, casting a shadow line at its uphill edge; the strip **ending short of the tread ends**; and
  **wear mismatch** (strip scuffed to bare metal along the walked line while the stone is even, or the
  reverse).
- **The cheapest tier is paint.** Where there is no hardware budget the intervention observed is
  **white paint on every nosing** — 흰여울문화마을 has concrete alley stairs with **no railing on either
  side**, and white-painted nosings plus a white-painted open gutter as the *only* safety measure
  `[stat]`. Model this as a distinct tier: paint-only, no metal.
- **Partial-width anti-slip tile.** In Gamcheon, an ochre/tan patterned anti-slip tile is mortar-set
  over **only the front ~15 cm of each tread**, leaving the rest bare concrete `[stat]`. This reads
  instantly as an add-on and is a strong, unusual detail.

### 5.5 Concrete evidence of the operation

The cheapest, most convincing retrofit props are the **scars**, not the fixture:

- **Mortar patch** where an old post was cut off and a new one set beside it — a 100–200 mm disc of
  brighter, smoother mortar in a weathered slab.
- **Cut stub** of the previous rail left in the parapet (this repo already has "허공 파이프 스텁" as a
  *defect* in scene15 — as a deliberate retrofit prop, in the right place, it becomes a feature).
- **Core-drill dust halo** and four small spalls around a base plate.
- **Two generations of rail meeting mid-run**: a repaired span in stainless butting an original span in
  painted steel, with a mismatched joint sleeve. `scene12`'s "훼손 스팬" already establishes the
  precedent for a per-span material break.
- **Colour break in the tactile run** where a replaced batch of blocks is a fresher yellow.
- **Rust staining streaking down the stone from the steel fixings.** This is the weathering tell that
  says "the metal was added later than the stone", and it is visible in our own reference set.

**The single best reference frame — and we already hold it.**
`Docs/reference_photos/expanded/wc005_ccby40_caddc6_삼일공원_1.jpg` (Sadang, Seoul, 2020-08-31, CC BY 4.0)
contains the entire thesis in one image `[stat]`: **original granite block stairs**, a **stainless round
handrail with a goose-neck return on the left**, a **row of stainless hoops across the head**, a
**completely different reddish-brown round-post timber-look railing on the right**, and a **green
PVC-coated mesh fence** behind — **four fixture generations, none matching, none removed**, with rust
streaks running down the granite from the fixings. Use this as the look target for every RETROFIT-STYLE
cell in §3.1.

Corroborating: a Gamcheon flight carries **three generations stacked on one run** — a dark-grey painted
pipe rail on wall L-brackets, a stainless ball-finial rail below it, and a separate stainless rail on the
opposite wall; another shows a brown-painted pipe rail and a stainless baluster rail installed **side by
side on the same edge**, two campaigns, neither removed `[stat]`.

### 5.6 What a retrofit does *not* look like

- It does not look like the fixture was never missing. Uniform, seamless, everywhere-compliant is the
  **2010s new-build** signature, not the retrofit one.
- It does not restore geometry. A retrofitted handrail on a pre-code stair still sits on a stair with
  the **wrong riser, no landing and no mid-rail** — the retrofit adds the cheap member and leaves the
  expensive geometry alone. This is the single most useful fact in this document for §4, because it
  means **"handrail present" and "landing absent" is a coherent, common, realistic combination** and
  does not need to be reconciled.

---

## 6. Decision sheet — what goes to the supervisor

### 6.1 W4 verdict list (this is the ruling being requested)

| # | Item | Verdict | Basis |
|---|---|---|---|
| 1 | **02 landing** (L1) | **CANCEL** | 지하보도 = 도로 부속물, outside 건축법 §15 in every era; landings are geometry and are never retrofitted; and the field pattern is "bolt a machine alongside, never regrade" (§3.3) |
| 2 | **03 landing** (L1) | **CANCEL** | 하천시설, outside 건축법; insertion also forces re-derivation of the waterline band |
| 3 | **06 landing** (L1) | **EXECUTE** — reason replaced | 육교 is *also* outside 건축법, so the original "post-dates the statute" reason is **withdrawn**. It survives because a 2000s footbridge under 도로/교통약자 guidance does not get built as a 5 m continuous spiral with no rest landing. Highest-cost item — schedule alone |
| 4 | **08 landing** (L1) | **EXECUTE as planned** | 2010s civic build, plausibly a 건축물-adjacent stair, post-dates everything. Accept the +1.20 m bowl widening |
| 5 | **17 landing** (L1) | **CANCEL** | Levee stair = 하천시설; and it would break the stair↔ramp run alignment that is the scene's reason to exist. Spend the budget on making the **ramp** read as the retrofit instead |
| 6 | **02 mid-rail** (R1) | **CONVERT to retrofit-style** | Not statutorily required; a mid-rail *is* a retrofittable member. Build as a **single centre pipe on base plates, stainless, no infill** — the most common real form (5/11 of railed cases in the alley survey). Not a balustered guardrail |
| 7 | **08 mid-rail** (R1) | **EXECUTE as planned** | 2010s; compliant mid-rail is the correct modern look |
| 8 | **09 mid-rail** (R1, 3 lines) | **CANCEL** | Real cases outrank code. 무난간 water-viewing steps is the documented practice; 3 rails across a 10 m viewing terrace would be a code-correct fabrication |
| 9 | **18 mid-rail** (R1, 2 lines) | **CANCEL** | Public village stair, not a 건축물 stair; its only ever intervention was paint |
| 10 | **05 mid-rail** (R1, 8 lines) | **CANCEL** — now with a statutory basis | Seating tiers. The 옥외계단 test applied to it comes from 주택건설기준 §16①, which binds **주택단지 only**; a park amphitheatre is not one, so the riser-0.400 "violation" is not a violation |
| 11 | **Nosing, corpus-wide** | **EXECUTE, era-conditional** | Anti-slip at the nose **is** statutory (편의증진법 별표1 제8호 마.(2), 1998) — but satisfied by **줄눈넣기 (cast grooves)** as well as by a strip. So: **pre-code scenes (02·11·15·18) → applied strip with screw heads/adhesive; 2010s scenes (08·10·12·14) → cast/inset or grooves; stone & natural (07·03·04·09) → absent.** Confirms and refines the existing STATUS ruling |
| 12 | **Handrails, corpus-wide** | **EXECUTE, era-conditional — not uniform** | The "33씬 전부 미구현 → 가장 먼저 착수" note is right as a *look* judgement but must not be applied flat. **08·14·21·C4 → built-in. 11·18 → retrofit-style. 03·09·17 → none (identity + 하천시설). 07 → heritage rustic rail at most. 19 → private roof, not a 대상시설** |
| 13 | **§12.4 tactile registry** | **No membership change; add a construction attribute** | Every entry survives its era test. Add **매립식 vs 부착식** per entry (§5.3, statutorily named), and resolve the 06 HOLD to **ON at the ground-level entry only** |

**Tally (13 items): 3 EXECUTE** (one — 06 — with its reason replaced) **· 1 CONVERT · 6 CANCEL ·
2 era-conditional · 1 registry attribute.**
Of the five planned landings, **two survive** (06 · 08); of the five planned mid-rails, **one survives**
(08) and one converts (02).

### 6.2 Items that need a ruling but were NOT in the W4 scope

| # | Item | Recommendation |
|---|---|---|
| A | **Tactile dot Ø25 mm vs KS F 4561's Ø35 mm** (§4.4 item 0) | **Do not revert yet.** Procure KS F 4561:2022, confirm, then re-rule B7. The current value sits on the **Japanese** figure and undoes the project's own "no Western/Japanese assets" rule |
| B | **Rail height 0.90 m outdoors** | Wrong default. Outdoor = 110 cm; 옥상·노대 = **1.1 m pre-2005-07-18 / 1.2 m after** (주택 1.1/1.2 at 2003-04-22). Make it era-driven; **scene19 should be 1.1 m** |
| C | **Mirror stainless as the universal rail material** | Split by era: painted mild steel (1970s–80s) / matt galvanized (1990s–2000s road) / brushed STS304 (2000s+ retrofit). The *mismatch between them in one frame* is the deliverable |
| D | **Uniformly saturated tactile yellow** | Real worn blocks are **grey along the walked line, yellow only at the edges** (≥8 mm colour layer abrades). Statutory replacement threshold is **dot height ≤3.5 mm** — use it as the worn-state target |
| E | **No RETROFIT-STYLE implementation anywhere** | 12 cells in §3.1 are class R; **zero are built**. This is the largest single realism lever this survey found and it costs no geometry |

### 6.3 What this document does not settle

- **The `ground_kit_spec_v1.md` §12.1 citation conflict** — it cites 보건복지부령 **제1166호 (시행 2026-07-02)**
  for 별표1 while the text extracted here carries **제983호 (2023-12-11)**. Reconcile before either is
  treated as authoritative; nothing in this survey's conclusions depends on which is current.
- **Sunken plazas (scene08)** produced **no field evidence at all** — its EXECUTE verdicts rest on era
  reasoning alone.
- **Underpass and footbridge retrofit programmes** have no per-site counts; Commons has no usable
  Korean category for either, and street-level imagery was unreachable.
- The **KS F 4561 truncated-cone top diameter** is unverified (paywalled), which is why item A is a
  flag and not a revert.
