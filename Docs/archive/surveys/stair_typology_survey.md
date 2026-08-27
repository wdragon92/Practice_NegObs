# 옥외 하행 계단(Descending Outdoor Stairs) 유형 서베이 v1

- 작성일: 2026-07-24
- 목적: RGB 맥락단서 기반 negative obstacle(낙차) 탐지 연구의 인공 씬 다양화. "정형화된 계단 1종"(scene01 = 캠퍼스 광장 광폭 저단차형) 편향을 깨고, **시각적 단서 구성이 서로 다른 유형**을 체계적으로 커버하기 위한 유형 분류.
- 상위 근거 문서: `Project_NegObs/Docs/negobs_context_scenario_survey_v1.md` — 특히 §3(맥락단서 4계열: ①설비 / ②기하 / ③스케일앵커 / ④조명)과 S4(도시 단차형). 본 서베이는 그 §3 단서 체계를 **유형별 단서 조합 프로파일**로 전개한 것이다.
- 방법: WebSearch 8회로 유형·기하·설계기준·사고사례를 수집. 수치는 출처 있는 것만 확정 표기, 없는 것은 (추정) 표기.

---

## 0. 왜 "유형"이 중요한가 — grazing 은폐와 단서 조합

하행 계단의 낙차는 낮은 시점(grazing angle, 카메라 높이 0.3~2.0 m, 피치 −15°~+5°)에서 **디딤면(tread)이 원근으로 압축되어 상판과 하판이 하나의 평면처럼 융합**되며 사라진다(자기폐색). 은폐가 "얼마나 완전한가"와 "무엇을 단서로 남기는가"는 유형에 따라 크게 다르다:

- **단높이(riser)가 낮을수록** grazing 은폐가 강하다(광폭 저단차형이 최악).
- **상·하판 재질이 같을수록** 명도·텍스처 불연속 단서가 사라진다.
- **난간/점자블록/논슬립** 등 규격 설비의 유무가 "설계기준 역추론" 단서(계열①)의 존재를 결정한다.
- **자연물(수목·물·낙엽)** 임베딩 여부가 스케일앵커(계열③)와 재질대비(계열②)의 성격을 바꾼다.

따라서 씬 세트는 "계단"이라는 한 클래스가 아니라, **단서 조합 축의 코너 케이스들**을 표본해야 학습 다양성이 확보된다.

---

## §1. 유형 매트릭스

수치 표기: 확정치는 출처 인용, 그 외 (추정). riser=단높이, tread=디딤폭.

| 유형 | 전형 기하 (단수·riser·tread·폭·곡률) | 재질 구성 | 동반 단서 (난간·점자블록·논슬립·측벽·조경) | 은폐 기전 (grazing에서 사라지는 방식) | 사고 관련성 | 출처 |
|---|---|---|---|---|---|---|
| **T1. 광장 광폭 저단차형** (civic/campus plaza) — *scene01 기구현* | 3~5단, riser 0.15 m·tread 0.35~0.45 m, 폭 5~15 m, 직선(곡률 0) | 화강암 판재 등 상·하판 **동일 계열**(고대비 없음) | 난간 종종 **없음**(1 m 미만이라 법정 의무 밖), 점자블록 유무 혼재, 측벽 로우월, 앰피좌석·화단 인접 | riser가 낮고 상·하 동일 재질 → **grazing 은폐 최악**, 텍스처·명도 불연속 모두 약함. 저단차 편안함이 오히려 시각 소실 유발 | 광장 실족은 절대 빈도 큼(계단 부상 미 연 108만 건 중 상당). 로봇 저단차 오인 다발 | [pps.org sitwalls](https://www.pps.org/article/sitwalls), scene01_design_brief |
| **T2. 건물 진입 기념 계단** (monumental entrance) | 8~20+단, riser 0.13~0.17 m·tread 0.30~0.38 m, 폭 넓음, 직선(간혹 대칭 분기) | 화강암·대리석·프리캐스트 콘크리트, **일관 고급 재질**(상·하 대비 낮음) | 양측 난간·기념 파라펫 흔함, 논슬립 노징, 점자블록(공공청사) | 단수가 많아 **하부가 아래로 완전히 접혀 사라짐**; 상단 1~2 단코와 난간의 하강선만 남음(고전 단서) | 다중 이용·군중 실족, 우천 시 미끄럼 | [Grokipedia Stairs](https://grokipedia.com/page/Stairs), [High Line monumental stair (KCI)](https://www.mgmclaren.com/projects/the-high-line-monumental-stair/), [Great Lakes monumental stairs](https://stair.com/staircase-gallery/monumental-stairs/) |
| **T3. 지하도/지하철 입구 하강 계단** (underground entrance) | 12~30+단(중간참 포함), riser 0.15~0.165 m·tread 0.30~0.33 m, 폭 1.2 m+, 직선 하강 | 콘크리트·타일, **하부로 갈수록 어두워짐**(무조명 지하) | 난간 의무(1 m 초과), **점자블록 상단 0.3 m 앞 규격 배치**, 논슬립, 측벽/캐노피, "지하·B1" 표지 | 상부 개구부 너머가 **어둠으로 소실**(계열④ 암부 띠 + 계열② 텍스처 절단이 동시). 위치 정밀도 최고 단서군 | 승강장·지하 진입 실족, 치명도 상위. 로봇 진입 금역 | [장애인편의 세부기준 (law.go.kr)](https://law.go.kr/LSW/flDownload.do?gubun=&flSeq=86050237&bylClsCd=110201), [계단 설치기준 (midascad)](https://www.midascad.com/cad_archive/buildingact-4) |
| **T4. 공원 산책로 자연석·침목 계단** (park/trail natural steps) | 불규칙 5~30단, riser 0.13~0.23 m·tread 0.33~0.9 m(불균등), 폭 0.9~1.8 m, 완만한 곡률·굴곡 | 자연석(quarry/화강암 조각), 침목·목재, **주변 토양·낙엽과 재질 융합** | **난간 자주 없음**, 점자블록 없음, 목재 논슬립 간혹, 식생·수목이 계단에 임베딩 | 낙엽·흙·이끼가 단코를 덮어 **텍스처 절단선이 모호**; 수목 수관이 눈높이 이하로 내려가는 스케일앵커(계열③)가 주 단서 | 등산로 실족 구조 1위(§배경 S3와 연계), 젖은 목재 미끄럼 | [CA State Parks Trail Steps Ch.17](https://www.parks.ca.gov/pages/1324/files/Chapter%2017%20-%20Trail%20Steps.FINAL.12.27.18.pdf), [Delgado natural stone steps](https://www.delgadostone.com/blog/natural-stone-steps-what-to-know-about-the-three-types), [pavingexpert steps](https://www.pavingexpert.com/featur01) |
| **T5. 하천 제방·호안 접근 계단** (levee/riverside access) | 긴 직선 1열 10~40단, riser 0.15~0.18 m·tread 0.30~0.40 m, 폭 1~3 m, 직선(비탈 경사 따라) | 콘크리트·석축, 하부에 **수면/둔치**가 재출현 | **난간 자주 없음**(개방 제방), 점자블록 없음, 측벽 없음, 수변 식생 띠 | 계단 하부 너머 **물면 또는 둔치가 재출현**(계열② "건너편 지면 재출현 + 밀도 점프", 계열③ 물=최저부). 개방 사면이라 하늘·수면 인접 | 수변 추락→수몰(연안사고 사망 연 130명, §배경 S6), 무방호 낙차 | [Wikipedia Flood embankment](https://en.wikipedia.org/wiki/Flood_embankment), [King's Stairs Gardens](https://en.wikipedia.org/wiki/King%27s_Stairs_Gardens), [ARFCD levee slope](https://www.arfcd.org/improving-the-river-park-levee-slope) |
| **T6. 앰피시어터/sunken plaza 좌석 겸용 계단** (amphitheater/sunken) | 방사형/직선 계단좌석, **riser 0.30~0.45 m·tread 0.60~1.20 m**(좌석 규격), 폭 넓음, 원호 곡률 큼 | 화강암·콘크리트 좌석 블록, 일관 재질 | **난간 없음**(좌석 겸용이라 의도적 배제), 점자블록 없음, 사발형 측벽/조경 경계 | riser가 커 **개별 단은 보이나 방사 곡률로 원근 왜곡** 심함; 무난간·무점자로 설비 단서 전무, 곡률이 소실점 판정을 교란 | 좌석↔통행 경계 실족, 야간 미끄럼 | [Layak amphitheatre design](https://layakarchitect.com/architecture-architecture-details-amphitheatre-definition-types-examples/), [pps.org sitwalls](https://www.pps.org/article/sitwalls), [Audience risers (Wikipedia)](https://en.wikipedia.org/wiki/Audience_risers) |
| **T7. 부채꼴/곡선 계단** (fan/curved) | 5~15단, riser 0.15~0.17 m·tread 안쪽 짧고 바깥 김(winder), 폭 가변, **강한 곡률(타원·다중곡률)** | 석재·콘크리트, 조경 곡선 경계 | 곡선 난간(있으면), 점자블록 드묾, 논슬립 노징 | 곡률 때문에 **단코 선이 직선 소실점을 안 그림** → 기하 단서(계열②)의 표준 가정이 깨짐; 학습 하드 케이스 | 회전 이동 시 헛디딤 | [arch2o staircase types](https://www.arch2o.com/design-of-staircase-8-different-types/), [Keuka curved stairs](https://www.keuka-studios.com/types-of-stairs-2/), [Grokipedia Stairs](https://grokipedia.com/page/Stairs) |
| **T8. 대각 접근 계단** (diagonal/oblique approach) | 광장 코너를 대각으로 가로지르는 3~8단, riser 0.15 m·tread 0.35 m+, 폭 가변, 직선이나 진행축과 사교 | 광장 재질과 동일 | 부분 난간, 점자블록 코너 배치 혼재 | 진행축과 **단코가 사교**하여 카메라 정면 소실점 밖에서 낙차가 나타남 → 정렬 가정 붕괴, 측면 은폐 | 사선 보행 실족, 코너 사각 | [Grokipedia Stairs](https://grokipedia.com/page/Stairs), [oldstation outdoor stairways](https://oldstationlandscapesupply.com/outdoor-stairways/) |

### 한국 설계기준 (설비 단서 역추론의 근거, 확정치)
- 계단 riser **15~16.5 cm**, tread(단너비) **30~33 cm**, 유효폭 **1.2 m 이상**(옥외피난계단 0.9 m 이상): 장애인편의 세부기준 및 피난·방화구조 규칙. [law.go.kr 세부기준](https://law.go.kr/LSW/flDownload.do?gubun=&flSeq=86050237&bylClsCd=110201), [midascad 요약](https://www.midascad.com/cad_archive/buildingact-4)
- **난간 의무: 높이 1 m 초과 계단·계단참 양옆.** 경사 손잡이 끝 **0.3 m 이상 수평 연장.** → 난간 존재 = 낙차 ≥1 m의 준공식 증거. [피난·방화구조 규칙](https://www.law.go.kr/LSW/lsLinkCommonInfo.do?lspttninfSeq=124056&chrClsCd=010202)
- **논슬립(미끄럼방지재)** 계단코 설치(경질 고무류 등), **점형 점자블록** 계단 상단 모서리 앞 규격 이격(≈0.3 m). [장애인편의 매뉴얼](https://www.nld.go.kr/upload/contents02/seoul_menual(2016).pdf)
- 조경 계단·산책로 상세: [조경시설물 상세설계 매뉴얼 (codil)](https://www.codil.or.kr/filebank/original/MA/OTKNMA000324//OTKNMA000324.pdf)

### 사고 사례 — 로봇 관점 (어떤 유형에서 실제로 떨어졌나)
- Starship 배달로봇: **저시점 카메라로 계단을 못 보고 계단에서 낙하(airborne)** 사례, 화단에 끼어 계단에서 떨어짐(UCLA), 연석·차량 충돌 등. 원격 조작자의 단차 미인지가 반복 요인 → **T1·T3형(광폭 저단차/입구 하강)에서 전형적**. [AI Incident 519](https://incidentdatabase.ai/cite/519/), [AI Incident 813 (ASU 부상 소송)](https://incidentdatabase.ai/cite/813/), [Futurism 실패 모음](https://futurism.com/robots-and-machines/delivery-robot-fail-compilation)

---

## §2. 시각 단서 축 정리 — 씬 세트가 커버해야 할 다양성 축

scene01(T1)이 하나의 코너(광폭·저단차·동일재질·설비혼재)를 차지한다. 유형 간 **무엇이 달라지는가**를 축으로 정리하면, 학습 데이터가 편향되지 않으려면 각 축의 양극단을 표본해야 한다.

**축 A — 설비 단서(계열①) 유무:** 완비(T3 지하입구: 난간+점자블록+논슬립+표지) ↔ 전무(T4 자연석, T5 제방, T6 앰피). 설비가 있으면 "규격 역추론"으로 쉬운 라벨, 없으면 순수 기하·앵커에 의존. **양극단 모두 필요.**

**축 B — 재질 대비(계열②):** 상·하판 동일(T1·T6) ↔ 재질/명도 급변(T3 암부, T5 물면 재출현). 동일 재질은 hard case, 급변은 강한 단서. scene01은 동일 재질쪽이므로 **급변형이 보완되어야 함.**

**축 C — 단높이 스케일(은폐 강도):** 저단차 0.15 m(T1·T2·T5, grazing 은폐 최강) ↔ 대단차 0.30~0.45 m 좌석형(T6, 개별 단 가시). 스케일앵커(사람 상반신만 보임)의 작동도 riser에 좌우.

**축 D — 기하 정렬(계열② 소실점 가정):** 직선·정렬(T1·T2·T3) ↔ 곡률/사교(T6 방사, T7 부채꼴, T8 대각). 표준 소실점·정렬 가정을 깨는 **곡선·대각형은 반드시 1종 이상** 필요(현재 전무).

**축 E — 자연물 임베딩(계열③ 앵커 종류):** 인공 순수(T1·T2·T3) ↔ 수목/낙엽(T4) ↔ 물면(T5). 앵커의 종류(사람 vs 수관 vs 수면)가 달라짐. scene01은 인공 순수쪽.

**축 F — 조명 상태(계열④ 확증):** 균일 주광(T1·T6) ↔ 하부 암부 소실(T3 지하) ↔ 역광·수면 글리터(T5). 암부 소실은 T3에서만 강하게 나온다.

> **커버리지 결론:** scene01은 (A:혼재, B:동일, C:저단차, D:직선, E:인공, F:주광)의 한 점. 세트 다양성을 위해 **설비 전무(A−) / 재질 급변(B+) / 대단차(C+) / 곡선·대각(D+) / 자연물(E+) / 암부(F+)** 를 각각 커버하는 후보를 선정해야 한다.

---

## §3. 인공 씬 후보 6종 제안

*(기구현: scene01 = T1 캠퍼스 광장 광폭 저단차형 — 4단 riser 0.15/tread 0.38, 화강암 동일재질, 난간·점자블록·재질대비 cue 토글. 아래 6종은 이와 다른 단서 코너를 겨냥.)*

1. **Scene02 — 지하철/지하도 입구 하강 계단 (T3).**
   컨셉: 도심 보도에서 지하로 꺼지는 12~20단, 하부가 어둠으로 소실.
   핵심 차별: **설비 완비(A+) × 재질/암부 급변(B+, F+)** — 점자블록 상단 0.3 m·난간·논슬립·"B1" 표지 + 하부 무조명 암부. scene01의 정반대(설비·대비 최강) 코너. 라벨링 최易.

2. **Scene03 — 하천 제방 접근 계단 (T5).**
   컨셉: 둔치 산책로에서 강물 쪽으로 내려가는 긴 직선 무난간 계단, 하부에 수면 재출현.
   핵심 차별: **설비 전무(A−) × 물면 앵커(E+) × 하부 지면 재출현(B+ 밀도점프)** — 난간·점자 전무, 계열③ 물=최저부 + 계열② 건너편 둔치 재출현. §배경 S6(수변) 직결.

3. **Scene04 — 공원 산책로 자연석·침목 계단 (T4).**
   컨셉: 수목 사이 굴곡진 자연석/침목 계단, 낙엽·흙이 단코를 덮음.
   핵심 차별: **자연물 임베딩(E+) × 재질 융합(B−, 텍스처 절단 모호) × 완만 곡률(D 중간)** — 눈높이 이하 수관 앵커가 주 단서, 설비 없음. hard negative(관목 vs 낙차)와도 연계. §배경 S3(산길).

4. **Scene05 — 앰피시어터/sunken plaza 좌석 겸용 계단 (T6).**
   컨셉: 사발형 광장의 방사형 대단차 좌석 계단, 무난간.
   핵심 차별: **대단차 riser 0.3~0.45(C+) × 방사 곡률(D+) × 설비 전무(A−)** — 개별 단은 보이나 곡률로 원근 왜곡, 규격 설비 부재. scene01의 앰피 좌석 모티프를 "주역"으로 승격한 대비쌍.

5. **Scene06 — 건물 진입 기념 계단 (T2).**
   컨셉: 관공서/캠퍼스 건물 정면 넓고 긴 다단(12~20단) 기념 계단, 하부가 완전히 접혀 소실.
   핵심 차별: **다단 자기폐색 극대(하부 완전 소실) × 난간·파라펫 존재(A+) × 동일 고급재질(B−)** — 상단 1~2 단코+난간 하강선만 남는 "고전 단서" 학습. 단수 스케일이 scene01(4단)과 대비.

6. **Scene07 — 대각 접근 / 부채꼴 곡선 계단 (T8+T7).**
   컨셉: 광장 코너를 사선으로 가로지르거나 부채꼴로 휘는 계단 — 진행축과 단코가 사교.
   핵심 차별: **기하 정렬 붕괴(D+ 극단)** — 직선 소실점·정렬 가정을 정면 위반하는 유일 후보. 곡선·사교 낙차는 현 세트에 전무하므로 일반화 검증용 하드 케이스. (T7·T8을 한 씬에서 두 배치 변형으로 다뤄도 됨.)

**커버리지 점검:** 위 6종으로 §2의 6축 양극단이 모두 채워짐 — A+(S02,S06)/A−(S03,S04,S05), B+(S02,S03)/B−(S04,S06), C+(S05), D+(S05,S07), E+(S03물·S04수목), F+(S02암부). scene01과 합쳐 7종이 단서 조합 공간을 격자로 표본한다.

---

## 출처 (전체)

**유형·기하·설계**
- [Project for Public Spaces — Sitwalls, Ledges & Steps](https://www.pps.org/article/sitwalls)
- [Layak Architect — Amphitheatre Design (standards/types)](https://layakarchitect.com/architecture-architecture-details-amphitheatre-definition-types-examples/)
- [Audience risers — Wikipedia](https://en.wikipedia.org/wiki/Audience_risers)
- [Arch2o — 8 Types of Staircase Design](https://www.arch2o.com/design-of-staircase-8-different-types/)
- [Keuka Studios — Types of Stairs (curved)](https://www.keuka-studios.com/types-of-stairs-2/)
- [Grokipedia — Stairs](https://grokipedia.com/page/Stairs)
- [MG McLaren/KCI — The High Line Monumental Stair](https://www.mgmclaren.com/projects/the-high-line-monumental-stair/)
- [Great Lakes Stair — Monumental Stairs gallery](https://stair.com/staircase-gallery/monumental-stairs/)
- [Old Station — Outdoor Stairways guide](https://oldstationlandscapesupply.com/outdoor-stairways/)
- [Pavingexpert — Hard Landscape Steps](https://www.pavingexpert.com/featur01)
- [Delgado Stone — Natural Stone Steps (3 types/dimensions)](https://www.delgadostone.com/blog/natural-stone-steps-what-to-know-about-the-three-types)
- [CA State Parks — Trail Steps (Chapter 17)](https://www.parks.ca.gov/pages/1324/files/Chapter%2017%20-%20Trail%20Steps.FINAL.12.27.18.pdf)
- [Wikipedia — Flood embankment](https://en.wikipedia.org/wiki/Flood_embankment)
- [Wikipedia — Embankment](https://en.wikipedia.org/wiki/Embankment)
- [Wikipedia — King's Stairs Gardens (riverside steps)](https://en.wikipedia.org/wiki/King%27s_Stairs_Gardens)
- [American River FCD — River Park levee slope](https://www.arfcd.org/improving-the-river-park-levee-slope)

**한국 설계기준**
- [건축물 피난·방화구조 등의 기준에 관한 규칙 (law.go.kr) — 난간 1 m 초과·수평연장 0.3 m](https://www.law.go.kr/LSW/lsLinkCommonInfo.do?lspttninfSeq=124056&chrClsCd=010202)
- [장애인편의시설 세부설치기준 별표2 (law.go.kr) — riser 15~16.5·tread 30~33·유효폭 1.2 m](https://law.go.kr/LSW/flDownload.do?gubun=&flSeq=86050237&bylClsCd=110201)
- [계단 설치기준 요약 (midascad)](https://www.midascad.com/cad_archive/buildingact-4)
- [장애인편의시설 설치 매뉴얼 (국립장애인도서관) — 점자블록·논슬립](https://www.nld.go.kr/upload/contents02/seoul_menual(2016).pdf)
- [조경시설물 상세설계 매뉴얼 (codil)](https://www.codil.or.kr/filebank/original/MA/OTKNMA000324//OTKNMA000324.pdf)

**로봇 사고 사례**
- [AI Incident 519 — Starship campus terrain(계단 낙하 포함)](https://incidentdatabase.ai/cite/519/)
- [AI Incident 813 — Starship ASU 부상 소송](https://incidentdatabase.ai/cite/813/)
- [Futurism — 배달로봇 실패 모음](https://futurism.com/robots-and-machines/delivery-robot-fail-compilation)

**내부 문서**
- `Project_NegObs/Docs/negobs_context_scenario_survey_v1.md` (§3 단서 4계열, S4 도시 단차형)
- `Practice_NegObs/Docs/briefs/scene01_design_brief.md` (T1 기구현 사양)
