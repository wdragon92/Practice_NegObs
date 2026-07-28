# 옥외 하행 계단 유형 서베이 v2 — 세계 명소 광역 서베이 (T9~T21)

- 작성일: 2026-07-25
- 목적: negative obstacle(낙차) 맥락단서 연구용 **인공 씬 라이브러리 20종+ 확장**. 현재 5종 구현(scene01 캠퍼스 광장 T1 / 지하도 T3 / 하천 제방 T5 / 공원 침목 T4 / 앰피시어터 T6). v1의 T1~T8과 **단서 4계열 체계**(①설비 ②기하 ③스케일앵커 ④조명)를 상속하되, **기하 형태(축A)** 와 **실존 명소(축B)** 두 축으로 세계의 독특한 하행/승강 계단을 조사하여 신규 유형 T9~T21을 추가한다.
- 선행 문서: `Practice_NegObs/Docs/stair_typology_survey.md` (T1~T8, 단서 축 A~F). **중복 회피 기준**: 신규 유형은 T1~T8 대비 최소 1개 축(기하 정렬 D / 재질 B / 스케일 C / 자연물 E / 조명 F / 설비 A)이 달라야 함.
- 방법: WebSearch 16회. 수치는 출처 있는 것만 확정, 없으면 (추정).
- 사용자 특별 요구 대응: **"사원처럼 돌계단 울퉁불퉁"** → T16(마추픽추/불국사 마모 부정형 석단). **"원형으로 돌면서 올라가는 계단"** → T9(나선/헬리컬 석탑·등대). 한국 사례 우선 포함(불국사·북한산성·감천문화마을·한강공원).

---

## §1. 신규 형태 매트릭스 (T9 ~ T21)

riser=단높이, tread=디딤폭. 확정치는 출처 인용, 그 외 (추정).

| 유형 | 대표 명소(출처) | 전형 기하 수치 | 재질·마모 | 동반 단서 / 은폐 기전 | 기존 T1~T8과의 차별 축 |
|---|---|---|---|---|---|
| **T9. 나선/헬리컬 석조 계단** (등대·성탑) | 등대·성탑 내외부 나선; 일반 나선 규격 [Arch2O](https://www.arch2o.com/the-complete-guide-to-spiral-staircase-dimensions-code-compliance-and-design-standards/), [Dimensions.com](https://www.dimensions.com/element/spiral-stairs-open-risers) | 중심기둥 반경 0.6~1.5 m, riser 0.16~0.22 m, 16단/1회전 시 **단당 22.5°**, walkline=안쪽에서 tread의 2/3 지점, 헤드룸 ≥1.98 m | 석재·주철, 안쪽 마모 편중 | 원통 벽·중심기둥이 시야 차단, 아래 단이 **곡률 뒤로 말려 완전 은폐**; 소실점이 나선 축으로 붕괴 | **기하 정렬 D 극단(3D 나선)** — T7 부채꼴은 평면 곡률뿐, T9는 수직 회전축까지. 신규 |
| **T10. 헬리컬 주차 램프(계단 병설)** | 나선 주차램프 [BibLus](https://biblus.accasoftware.com/en/how-to-design-a-garage-access-ramp-the-complete-technical-and-professional-guidelines/), [Alibaba 가이드](https://carinterior.alibaba.com/question/car-parking-ramp-slope-design-guide) | 램프 내측 반경 ≥15 m, 경사 ≤12%(1:12), 폭 3.0~3.6 m(1차선); 병설 대피계단 riser 0.15~0.18 m | 콘크리트·에폭시 도장, 균일 | 램프의 **연속 곡면**과 계단이 병존 → 경사(램프)와 낙차(계단)의 구분이 시각적으로 모호, 차선 도색이 유일 앵커 | **램프 병설(경사 vs 낙차 혼동)** — 기존 전무. 조명 실내·균일 |
| **T11. 스텝웰(계단식 우물)** | Chand Baori, Abhaneri [Wikipedia](https://en.wikipedia.org/wiki/Chand_Baori), [Outlook](https://www.outlooktraveller.com/destinations/india/architectural-marvel-of-chand-baori-geometry-design-and-highlights-for-visitors) | 깊이 ~30 m·13층, 한 변 35 m, **3,500단** 삼각/쌍계단이 다이아몬드 격자로 대칭 반복, 하부에 수면 | 사암, 건조·정연(마모 적음) | 좌우 대각 계단 뱅크가 **격자 무늬로 반복** → 개별 단코가 반복 패턴에 흡수되어 낙차 경계가 착시; 최하부 물면 재출현 | **격자 반복 기하 + 하강형 우물(위→아래 수렴)** — 지상 상승형과 반대. E+(물) 겸비. 신규 |
| **T12. 가트(수변 계단)** | 바라나시 갠지스 가트 [Wikipedia](https://en.wikipedia.org/wiki/Ghats_in_Varanasi), [UNESCO](https://whc.unesco.org/en/tentativelists/6526/) | 가트당 약 **40~60단**, 폭·높이 **불균등**(리듬 가변), 6.4 km 연속, 하부에 강물 | 사암·석회암·대리석, **순례로 마모되어 매끈** | 넓은 부정형 테라스가 물가로 하강, 하부 수면 재출현(밀도점프) + 계절 수위선 얼룩 | **초광폭 불균등 수변(T5 제방의 광폭·부정형 변형)** — T5는 좁은 직선 1열, T12는 광폭 다열 불균등 |
| **T13. 스위치백/절벽 철제 계단** | Haʻikū Stairs(하와이) [Wikipedia](https://en.wikipedia.org/wiki/Haiku_Stairs), [oahuhike](http://www.oahuhike.com/haikustairs) | **3,922단**, 8 ft 세그먼트를 훅·스파이크로 연결, 난간 폭 **18~24 in(0.46~0.61 m)**, 구간 거의 수직, 갈지자 | 아연도 강재, 미끄럼·부식 | 산릉을 따라 **급경사 갈지자**로 접힘, 하부가 사면 아래로 소실; 개방 철골이라 배경 하늘·계곡 투과 | **산악 스위치백 + 개방 철골(수직에 가까운 대경사)** — 기존 계단 경사 범위 밖. D+(방향 반전 반복) |
| **T14. 초광폭 기념 계단(착시형)** | 스페인 계단 [Wikipedia](https://en.wikipedia.org/wiki/Spanish_Steps); 포템킨 계단 [Wikipedia](https://en.wikipedia.org/wiki/Potemkin_Stairs) | 스페인: **135단**, 3연·나비형, 높이 29 m. 포템킨: **192단**·10연, 높이 27 m, **상단 폭 12.5 m→하단 21.7 m 점증**(원근 착시) | 사암·트래버틴 | 폭 점증·계단참 다단 → **위에서는 계단참만/아래서는 단코만 보이는 착시**(단서 소실 설계). 기존 T2 확장 | **의도적 원근 착시(폭 그라디언트·나비형 분기)** — T2 기념계단의 착시·분기 극단 변형 |
| **T15. 협소 골목 계단(언덕 미로)** | 부산 감천문화마을 [SoulofSeoul](https://thesoulofseoul.net/gamcheon-culture-village-busan/); 리스본 알파마 [Medium](https://medium.com/@moretoexplore/lisbons-hidden-staircases-uncovering-the-city-s-best-views-step-by-step-4cd6106251b4) | 감천 "별보러가는계단" **148단**, 폭 좁고 급경사; 리스본 칼사다 모자이크 포장, 불균등 | 콘크리트·타일·칼사다(흑백 모자이크), **젖으면 미끄럼** | 좌우 벽·주택이 밀착해 **협곡형 시야**, 계단이 골목과 융합, 소실점이 벽면으로 압축; 벽 그림자 대비만 단서 | **초협소 측벽 밀착 + 급경사 도시 미로** — T1 광폭의 정반대(폭 최소). 벽 앵커 |
| **T16. 마모 부정형 사원·성곽 석단** | 마추픽추 [Peruways](https://peruways.com/climbing-the-steps-of-machu-picchu-exploring-inca-architectural-wonders/); 불국사 청운교·백운교 [Wikipedia Dabotap](https://en.wikipedia.org/wiki/Dabotap); 북한산성 [Wikipedia](https://en.wikipedia.org/wiki/Bukhansanseong) | 마추픽추 ~2,000단·100+ 불규칙 flight, **돌 형상 따라 riser·tread 제각각**; 불국사 33단(깨달음 상징); 북한산성 성벽 7 m | 화강암·안산암, **울퉁불퉁·마모·이끼**, 모서리 둥긂 | 단코가 **직선이 아니고 돌 윤곽 따라 물결** → 텍스처 절단선·소실점 가정 붕괴, 그림자도 부정형 | **부정형 마모 석재(불규칙 riser/tread·둥근 모서리)** — 사용자 핵심 요구. T4보다 마모·비정형 강함, 석조 |
| **T17. 절벽 잔도(플랭크 워크)** | 화산 창공잔도(중국) [ChinaDiscovery](https://www.chinadiscovery.com/shaanxi-tours/mount-hua-tours/huashan-plank-walk.html), [Wikipedia](https://en.wikipedia.org/wiki/Chang_Kong_Cliff_Road) | 길이 100 m+·3구간, 절벽에 강철 핀 박고 **목판 폭 ~0.3 m**, 발판 홈, 낙차 1,000 m | 목재+강철 핀, 마모·풍화 | 한쪽은 수직 암벽, 반대쪽은 **허공(무한 낙차)** → 난간 없는 편측 개방, 발판 폭이 극소라 tread 소실 | **편측 무한 낙차(수직 벽+허공)** — 기존 유형의 유한 낙차와 위상 다름. 극협 tread |
| **T18. 물결/비정형 예술 계단** | 16th Ave 타일계단(SF) 163단 [mymodernmet](https://mymodernmet.com/stunning-stair-art/); 슈트루들호프슈티게(빈) [Wikipedia](https://en.wikipedia.org/wiki/Strudlhofstiege); 게리 AGO 138단 [Eittem](https://eittem.com/blogs/journal/frank-gehry-sculptural-staircase) | 단코 라인이 **사인파상 굴곡**, 곡면 참·분기, riser 0.15~0.17 m 유지 | 타일 모자이크·석재·목재, 고채색 | 화려한 모자이크·곡선이 **단 경계를 위장**(색이 낙차 대비를 교란), 굴곡 단코가 소실점 붕괴 | **비정형 곡선 단코 + 고채색 위장** — 색·패턴이 기하 단서를 능동적으로 방해. 신규 위장축 |
| **T19. 개방 그레이팅 철제 계단** | 옥외 비상계단 [Lapeyre](https://www.lapeyrestair.com/applications/fire-escape-stairs/), [Section 303](https://up.codes/s/fire-escapes-b) | 폭 ≥0.56 m, riser ≤0.21 m, tread ≥0.23 m, **그레이팅 개방판(투과)**, 계단참 1.0×0.9 m | 아연도 강재 그레이팅·체커판 | **디딤판이 투과성** → 아래 배경이 보여 tread 면이 사라지고 riser 없음(개방), 그림자가 격자 무늬로 투영 | **투과 디딤판(riser 부재·배경 투시)** — 불투명 재질 전제를 위반. F(격자 그림자) 특이 |
| **T20. 캐노피/지붕형 계단** | 지하철 입구·모듈러 캐노피 [Duo-Gard](https://www.archiexpo.com/prod/duo-gard/product-58207-979761.html), [Upside](https://upsideinnovations.com/canopies-awnings/) | 계단 위 폴리카보네이트·알루미늄 지붕, 경사 배수 루프, 폭 1.2~2.4 m | 콘크리트 단+금속·투광 지붕 | 지붕이 **상부에 짙은 그림자 띠**를 드리워 상단 단코가 암부로 소실(T3 지하 암부를 지상 캐노피로 재현) | **오버헤드 구조 그림자(상단 암부)** — 조명축 F+를 지상에서. T3는 하부 암부, T20은 상부 |
| **T21. 램프 병설 제방 계단(한강형)** | 여의도·뚝섬 한강공원 [WorthyGo](https://worthygo.com/destination-new-yeouido-han-river-park-seoul-south-korea/), [KoreaByBike](https://www.koreabybike.com/routes/hangang-bicycle-path/seoul-north-side/) | 계단 옆 **휠체어 램프 병설**(폭 ≥1.2 m), 자전거도로↔둔치 짧은 단차, 계단 riser 0.15 m | 콘크리트·석재, 균일 | 계단과 완경사 램프가 **나란히** → 램프의 완만함이 인접 계단 낙차 인지를 상쇄(주변 완경사에 낙차가 묻힘) | **완경사 램프 인접(낙차 대비 희석)** — 한강 사례, 실측 접근성 개선 문서 근거 |

### 한국 사례 요약(축B 우선 포함)
- **불국사 청운교·백운교**: 33단(깨달음 33천 상징), 석교형 계단, 국보 22·23호. 화강암 정교 가공이나 세월 마모. [Google A&C](https://artsandculture.google.com/story/bulguksa-harmony-in-stone-and-wood-province-of-gyeongsangbuk-do/eAXRYTIo2skKQA)
- **북한산성**: 성벽 7 m·둘레 8 km(1711 완성), 등산로에 다수 계단·암반 구간(부정형 석단). [Wikipedia](https://en.wikipedia.org/wiki/Bukhansanseong)
- **감천문화마을**: 언덕 미로, "별보러가는계단" 148단, 급경사·협소·불균등. [SoulofSeoul](https://thesoulofseoul.net/gamcheon-culture-village-busan/)
- **한강공원(여의도·뚝섬)**: 물가 계단 교체·휠체어 램프 병설, 제방도로로 도심과 단절. [WorthyGo](https://worthygo.com/destination-new-yeouido-han-river-park-seoul-south-korea/)

---

## §2. 인공 씬 후보 16종+ 리스트

*(기구현 5종 = scene01 T1 광장 / T3 지하도 / T5 제방 / T4 침목 / T6 앰피. 아래 후보는 그 5종 및 후보끼리도 최소 1개 축이 서로 다르게 선정. 텍스처 슬러그는 PolyHaven=PH / ambientCG=aCG, 미검증은 (후보).)*

1. **scene_spiral_towerstone (T9)** — 원형으로 돌며 오르내리는 석탑 나선. 사용자 직접 요구.
   기하: 중심기둥 반경 0.9 m, r_out 2.4 m, riser 0.18 m, 22.5°/단×32단(2회전). 신규 빌더: **spiral_helix**. 텍스처: PH `castle_stone`/aCG `Rock023`(후보). 특색: 아래 단이 곡률 뒤로 말려 완전 은폐되는 3D 나선 자기폐색.

2. **scene_wornstone_temple (T16)** — 사원처럼 울퉁불퉁 마모된 부정형 돌계단. 사용자 직접 요구.
   기하: 18단, riser 0.13~0.24 지터, tread 0.28~0.55 지터, 폭 2.0 m, 단코 물결. 신규 빌더: **worn_stone_jitter**. 텍스처: PH `rock_ground`+이끼 데칼/aCG `Ground037`(후보). 특색: 돌 윤곽 따라 단코가 비직선 → 소실점·텍스처 절단 동시 붕괴.

3. **scene_stepwell_lattice (T11)** — 다이아몬드 격자로 하강하는 스텝웰 우물.
   기하: 좌우 대각 뱅크 각 13열, riser 0.28 m, 대칭 삼각 반복, 최하부 물면. 신규 빌더: **stepwell_lattice** + water_plane. 텍스처: PH `sandstone_..`(후보)/aCG `Bricks_sand`. 특색: 격자 반복이 개별 단코를 흡수해 낙차 경계를 착시로 소거.

4. **scene_ghat_riverfront (T12)** — 광폭 불균등 수변 가트, 하부 수면 재출현.
   기하: 폭 8 m, 50단 불균등(riser 0.1~0.25), 수위선 얼룩, 하단 물. 신규 빌더: **ghat_terrace**(불균등 광폭). 텍스처: aCG `PavingStones` 마모/PH `worn stone`(후보). 특색: T5보다 광폭·다열·마모 강, 계절 수위 얼룩 밴드.

5. **scene_switchback_cliff (T13)** — 산릉 갈지자 개방 철제 계단.
   기하: 6 flight×8단, 참마다 180° 반전, 폭 0.6 m, riser 0.2 m, 급경사. 신규 빌더: **switchback_flights** + grating. 텍스처: aCG `Metal009`/PH `metal_grate`(후보). 특색: 방향 반전 반복 + 배경 계곡 투과로 낙차가 사면에 접힘.

6. **scene_grating_fireescape (T19)** — 투과 디딤판 옥외 비상계단.
   기하: 12단, riser 0.2 m, tread 0.24 m 그레이팅, 폭 0.9 m, 계단참. 신규 빌더: **grating_open_riser**(알파 투과). 텍스처: aCG `Metal049A` 그레이팅 알파(후보). 특색: 디딤판 투시로 tread 소실·riser 부재, 격자 그림자 투영.

7. **scene_cliff_plankwalk (T17)** — 절벽 편측 무한낙차 잔도.
   기하: 길이 12 m, 목판 폭 0.3 m, 발판 홈, 한쪽 수직 암벽·반대쪽 허공. 신규 빌더: **plank_ledge**(편측 캔틸레버). 텍스처: PH `wood_planks`+aCG `Rock_cliff`(후보). 특색: 난간 없는 편측 개방, 극협 tread로 발판 경계 소실.

8. **scene_helical_parkingramp (T10)** — 나선 주차램프+병설 대피계단(경사vs낙차 혼동).
   기하: 램프 내경 15 m·경사 10%, 병설 계단 riser 0.16 m, 실내 균일광, 차선 도색. 신규 빌더: **spiral_helix**(재사용)+ramp_surface. 텍스처: aCG `Concrete034`+도색 데칼(후보). 특색: 연속 경사면과 계단이 병존해 낙차·경사 구분 모호.

9. **scene_grandstair_illusion (T14)** — 초광폭 기념계단, 폭 점증 원근 착시.
   기하: 40단, 상단 폭 6 m→하단 10 m 점증, 계단참 3단, 나비형 분기. 신규 빌더: **tapered_grand**(폭 그라디언트). 텍스처: PH `travertine`/aCG `Marble`(후보). 특색: 위=참만/아래=단코만 보이는 의도적 단서 소실 착시.

10. **scene_alley_labyrinth (T15)** — 감천/알파마형 협소 급경사 골목 계단.
    기하: 폭 1.0 m, 25단, 좌우 벽 밀착, riser 0.18 m, 젖은 타일. 신규 빌더: 없음(측벽 프리팹)+wet 셰이더. 텍스처: aCG `Tiles`/PH `painted_plaster` 측벽(후보). 특색: 협곡형 벽 밀착으로 소실점이 벽면 압축, 벽 그림자만 단서.

11. **scene_canopy_shadow (T20)** — 캐노피 지붕이 상단에 암부 띠를 드리운 계단.
    기하: 14단, riser 0.16 m, 폭 1.8 m, 폴리카보네이트 지붕, 상단 그림자 밴드. 신규 빌더: **canopy_roof**(오버헤드+그림자). 텍스처: PH `concrete_floor`+투광 지붕 머티리얼(후보). 특색: T3 하부암부를 뒤집은 상부암부 소실.

12. **scene_ramp_pair_hangang (T21)** — 한강형 계단+휠체어 램프 병설 제방.
    기하: 계단 12단 riser 0.15 m 옆에 완경사 램프 1:12, 둔치·자전거도로. 신규 빌더: **ramp_pair**. 텍스처: aCG `Concrete030`/PH `stone_tiles`(후보). 특색: 인접 완경사가 낙차 대비를 희석(주변 완만함에 낙차 은폐).

13. **scene_wavy_artstair (T18)** — 사인파 단코·고채색 모자이크 예술 계단.
    기하: 20단, 단코 라인 진폭 0.4 m 사인 굴곡, riser 0.16 m, 타일 고채색. 신규 빌더: **undulating_wave**(단코 변위). 텍스처: aCG `Tiles_mosaic`/PH `tiled`(후보). 특색: 색·패턴이 낙차 대비를 능동 위장 + 곡선 단코 소실점 붕괴.

14. **scene_fan_winder (T7 미구현)** — 부채꼴 winder 곡선 계단.
    기하: 12단, 내경 1.2 m 외경 3.5 m, 부채꼴 사다리꼴 tread(내측 짧고 외측 김), riser 0.16 m. 신규 빌더: **winder_fan**. 텍스처: PH `granite`/aCG `PavingStones`(후보). 특색: 단코가 직선 소실점을 안 그림(평면 곡률 하드케이스).

15. **scene_diagonal_oblique (T8 미구현)** — 광장 코너를 사교로 가로지르는 대각 계단.
    기하: 6단, riser 0.15 m, tread 0.4 m, 진행축과 30° 사교, 폭 가변. 신규 빌더: 없음(배치 회전만). 텍스처: scene01 재사용 `granite`. 특색: 정면 소실점 밖 측면에서 낙차 출현(정렬 가정 위반).

16. **scene_monumental_selfocclude (T2 미구현)** — 건물 진입 다단 기념계단, 하부 완전 접힘.
    기하: 18단, riser 0.15 m, tread 0.33 m, 폭 6 m, 양측 난간·파라펫. 신규 빌더: 없음(파라펫 프리팹). 텍스처: PH `marble`/aCG `Concrete_precast`(후보). 특색: 상단 1~2 단코+난간 하강선만 남는 고전 자기폐색.

17. **scene_bulguksa_bridge (T16 한국 변형)** — 불국사형 석교 계단(33단·석축 아치).
    기하: 33단 2연(백운교+청운교), riser 0.17 m, 하부 석축 아치, 화강암 마모. 신규 빌더: **worn_stone_jitter**(재사용)+arch_substructure. 텍스처: PH `granite`+이끼(후보). 특색: 석교 아치 하부 공동과 마모 석재의 이중 단서.

**커버리지 점검(후보 상호 차별):** 나선(1,8) / 부정형석(2,17) / 격자우물(3) / 수변광폭(4) / 스위치백(5) / 투과철골(6) / 편측무한(7) / 경사혼동(8) / 착시광폭(9) / 협소미로(10) / 상부암부(11) / 램프희석(12) / 색위장(13) / 평면곡률(14) / 사교(15) / 다단자폐(16). 각 후보는 최소 1개 축(D기하/B재질/C스케일/E자연물/F조명/A설비/위장)에서 서로·기존 5종과 구분됨. 총 유형 T1~T21 = **21종**(목표 20+ 달성).

---

## §3. 신규 빌더 요구 요약

후보들이 공통 요구하는 지오메트리 빌더와 수학적 정의. (i=단 인덱스 0..N−1)

1. **spiral_helix** (후보 1,8 — 나선/헬리컬)
   파라미터 방정식: 단 i의 각 `θ_i = i·Δθ`, `Δθ = 2π / n_rev`(예 22.5°=16단/회전). 반경구간 `[r_in, r_out]`, 상면 z `z_i = i·riser`. tread는 `θ_i~θ_{i+1}` × `[r_in,r_out]`의 환형 섹터. walkline 반경 `r_w = r_in + (2/3)(r_out−r_in)`, walkline tread 깊이 `= r_w·Δθ`. 중심기둥 = 반경 r_in 원기둥. 입력: r_in, r_out, riser, n_rev, N, 회전방향(±).

2. **worn_stone_jitter** (후보 2,17 — 마모 부정형 석재)
   기준 단(riser0, tread0)에 지터 테이블 적용. 열 사양: `[step_idx, d_riser~N(0,σ_r), d_tread~N(0,σ_t), d_lateral~N(0,σ_l), yaw_tilt~U(−a,a), edge_round~U(r_min,r_max)]`. 권장 σ_r=0.03 m, σ_t=0.05 m, σ_l=0.02 m, a=4°. 단코 라인은 노드별 lateral 오프셋으로 비직선화, 모서리는 edge_round 반경 챔퍼/필렛, 표면은 변위맵(진폭 0.5~2 cm). 시드 고정으로 재현.

3. **switchback_flights** (후보 5 — 스위치백/갈지자)
   flight k(각 m단) + 계단참 L_k의 반복. 방향 heading `ψ_k = ψ_0 + k·Δψ`(Δψ=180° 반전 또는 90° 도그레그). 위치 누적: 각 flight는 진행방향으로 m·tread 전진·m·riser 상승, 참에서 heading 갱신. 입력: flight수, m, tread, riser, Δψ, 참 크기.

4. **winder_fan** (후보 14 — 부채꼴 winder)
   tread = 환형 섹터. 각폭 `Δφ = φ_total / N`. 내측 tread 깊이 `t_in = r_in·Δφ`, 외측 `t_out = r_out·Δφ`(내측 짧고 외측 김), riser 일정. 입력: r_in, r_out, φ_total, N, riser.

5. **stepwell_lattice** (후보 3 — 스텝웰 격자)
   좌우 대칭 대각 뱅크. 한 뱅크는 계단 열을 수평 오프셋 `dx`, 수직 `−riser`로 반복해 다이아몬드 격자 생성. 미러링으로 V자 대칭. 최하부 water_plane. 입력: 층수, 열당 단수, riser, 대각 오프셋, 대칭축.

6. **ghat_terrace** (후보 4 — 광폭 불균등 수변)
   광폭 단(폭 W)의 riser_i·tread_i를 불균등 샘플(`U(0.1,0.25)` 등), 최하단에서 water_plane과 접함. 수위선 얼룩 = z 기준 텍스처 밴드. 입력: W, N, riser범위, tread범위, water_z.

7. **grating_open_riser** (후보 6 — 개방 그레이팅)
   tread를 알파 투과(격자) 머티리얼로, riser 생략(개방). 디딤판 간 수직 갭 존재. 격자 그림자는 방향광 하 자동 투영. 입력: N, riser(공간만), tread, 그레이팅 셀 크기, 알파맵.

8. **plank_ledge** (후보 7 — 편측 절벽 잔도)
   편측 캔틸레버: 한쪽은 수직 암벽 프리팹, 반대쪽 개방(무한낙차). 폭 극소(0.3 m) 목판을 강철 핀 서포트로 배치. 입력: 길이, 판폭, 핀 간격, 암벽 높이.

9. **canopy_roof** (후보 11 — 캐노피 지붕)
   계단 상부에 경사 루프 평면 + 지주. 상단 단에 그림자 밴드 생성(광원 각도 의존). 투광/불투광 지붕 옵션. 입력: 루프 높이·경사·투광도, 지주 위치.

10. **ramp_pair** (후보 12 — 램프 병설)
    계단 옆에 완경사 평면(1:12) 병치. 계단과 램프의 상·하단 레벨 정합. 입력: 계단 사양, 램프 경사·폭, 측방 간격.

11. **tapered_grand** (후보 9 — 폭 점증 착시)
    단 폭을 상단 W_top→하단 W_bot로 선형 점증 `W_i = W_top + (W_bot−W_top)·i/(N−1)`. 계단참 다단 삽입, 나비형 분기(선택). 입력: W_top, W_bot, N, 참 위치, 분기 여부.

12. **undulating_wave** (후보 13 — 물결 단코)
    단코 라인을 폭방향 좌표 x에 대해 `y_offset(x) = A·sin(2π x/λ)`로 변위(진폭 A, 파장 λ). riser 일정, 단코만 사인 굴곡. 입력: A, λ, N, riser.

**공통 인프라 요구:** water_plane(3·4·후보), 측벽/파라펫/암벽 프리팹(10·15·7·16), 알파 투과 머티리얼(6), 변위맵/이끼 데칼(2·17), wet/미끄럼 셰이더(10 골목·젖은 타일). 재사용: spiral_helix(1↔8), worn_stone_jitter(2↔17).

---

## 출처(신규)

**기하 형태(축A)**
- 나선: [Arch2O Spiral Guide](https://www.arch2o.com/the-complete-guide-to-spiral-staircase-dimensions-code-compliance-and-design-standards/), [Dimensions.com Spiral](https://www.dimensions.com/element/spiral-stairs-open-risers), [EVstudio](https://evstudio.com/residential-spiral-stairs-guidelines-criteria-and-dimensions/)
- 주차램프: [BibLus Garage Ramp](https://biblus.accasoftware.com/en/how-to-design-a-garage-access-ramp-the-complete-technical-and-professional-guidelines/), [Alibaba Ramp Slope](https://carinterior.alibaba.com/question/car-parking-ramp-slope-design-guide)
- 스텝웰: [Wikipedia Chand Baori](https://en.wikipedia.org/wiki/Chand_Baori), [Outlook Traveller](https://www.outlooktraveller.com/destinations/india/architectural-marvel-of-chand-baori-geometry-design-and-highlights-for-visitors)
- 가트: [Wikipedia Ghats in Varanasi](https://en.wikipedia.org/wiki/Ghats_in_Varanasi), [UNESCO Varanasi](https://whc.unesco.org/en/tentativelists/6526/), [MachuPicchu.org 84 steps](https://www.machupicchu.org/varanasi-ghats-walking-guide-84-sacred-steps.htm)
- 스위치백/철제 산악: [Wikipedia Haiku Stairs](https://en.wikipedia.org/wiki/Haiku_Stairs), [oahuhike](http://www.oahuhike.com/haikustairs)
- 착시 기념계단: [Wikipedia Spanish Steps](https://en.wikipedia.org/wiki/Spanish_Steps), [Wikipedia Potemkin Stairs](https://en.wikipedia.org/wiki/Potemkin_Stairs)
- 협소 골목: [SoulofSeoul Gamcheon](https://thesoulofseoul.net/gamcheon-culture-village-busan/), [Medium Lisbon Staircases](https://medium.com/@moretoexplore/lisbons-hidden-staircases-uncovering-the-city-s-best-views-step-by-step-4cd6106251b4)
- 마모 부정형 석단: [Peruways Machu Picchu Steps](https://peruways.com/climbing-the-steps-of-machu-picchu-exploring-inca-architectural-wonders/), [Wikipedia Dabotap](https://en.wikipedia.org/wiki/Dabotap)
- 절벽 잔도: [ChinaDiscovery Huashan Plank](https://www.chinadiscovery.com/shaanxi-tours/mount-hua-tours/huashan-plank-walk.html), [Wikipedia Chang Kong Cliff Road](https://en.wikipedia.org/wiki/Chang_Kong_Cliff_Road)
- 예술 계단: [MyModernMet Stair Art](https://mymodernmet.com/stunning-stair-art/), [Wikipedia Strudlhofstiege](https://en.wikipedia.org/wiki/Strudlhofstiege), [Eittem Gehry AGO](https://eittem.com/blogs/journal/frank-gehry-sculptural-staircase)
- 그레이팅 비상계단: [Lapeyre Fire Escape](https://www.lapeyrestair.com/applications/fire-escape-stairs/), [UpCodes Section 303](https://up.codes/s/fire-escapes-b)
- 캐노피: [ArchiExpo Duo-Gard Canopy](https://www.archiexpo.com/prod/duo-gard/product-58207-979761.html), [Upside Canopies](https://upsideinnovations.com/canopies-awnings/)

**실존 명소(축B) 한국**
- [Google A&C Bulguksa](https://artsandculture.google.com/story/bulguksa-harmony-in-stone-and-wood-province-of-gyeongsangbuk-do/eAXRYTIo2skKQA), [Wikipedia Bukhansanseong](https://en.wikipedia.org/wiki/Bukhansanseong), [WorthyGo Yeouido Hangang](https://worthygo.com/destination-new-yeouido-han-river-park-seoul-south-korea/), [KoreaByBike Hangang](https://www.koreabybike.com/routes/hangang-bicycle-path/seoul-north-side/)

**내부 문서**
- `Practice_NegObs/Docs/stair_typology_survey.md` (T1~T8, 단서 축 A~F)
