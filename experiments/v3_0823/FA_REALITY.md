# FA 현실 조사 — 낙차 오인 유발원과 N-cue 실세계 목록

> **위치**: `V3_DESIGN_0823.md` §8.1 「FA 이중 트랙」의 **현실 팔**. 시뮬 팔(CPU-2 FA 센서스)과 합류해
> §4.2 **N-cue 군 사양** + 파일럿 Ncue 컷 후보를 확정한다.
> **작성**: 08-23 · **방법**: 문헌·규정·사고사례 웹조사 (출처 전량 §5) · **본문 한국어, 출처 영문 제목 병기**
> **표기 규약**: `[확인]` = 출처로 직접 뒷받침 · `(추정)` = 조사자 추론 · `[내부]` = 본 저장소 문서 근거

---

## 0. 읽기 전에 — 이 문서가 전제하는 두 가지

### 0.1 FA 가족 4종은 아직 **정의되지 않았다**

`장식형 / 지형통계형 / 조명형 / 경계칸형` 네 이름은 저장소 전체에서 **단 한 곳**,
`Docs/experiment/V3_DESIGN_0823.md:333-337`의 괄호 안 나열로만 존재한다. 정의·글로서리·코드 상수가 없다 `[내부]`.
따라서 §1의 「FA 가족 매핑」 열은 **잠정 정의에 근거한 best-effort**이며, CPU-2 센서스가 가족을 확정하면
재매핑해야 한다. 잠정 정의는 선행 자산인 `Docs/reports/dropoff_cue_matrix_v1.md` §4의 12-지름길 가족표에서 역산했다.

| 코드 | 잠정 정의 (추정) | 선행 근거 `[내부]` |
|---|---|---|
| **장식** | 사람이 설치한 **맥락 부재**(난간·가드·블록·소품)의 존재만으로 발화. 위험 기하 없음 | 지름길 가족 #2 「가드·난간 어휘 = 낙차」(14/28씬), #9 「계절 드레싱/리터 = 낙차」(6씬) |
| **지형** | **배경·씬 정체성·경사/깊이 통계**만으로 발화. 특정 부재가 아니라 "이런 데면 낙차"라는 사전 | 지름길 가족 #1 「배경·씬 정체성만으로 라벨 예측」(18씬); sceneC2 판정 "장식이 아니라 고유 기하/depth 통계 요인" |
| **조명** | **암부·저휘도 영역·그림자 밴드·노출**이 임계를 넘으면 발화 | 지름길 가족 #7 「암부/저휘도 임계 = 낙차」(11씬) |
| **경계** | 두 읽기가 경합 — (a) **지면을 가로지르는 대리선**(줄눈·도색·재질 전환)을 진짜 낙차 엣지보다 강하게 읽음(가족 #5, 13씬), (b) 20칸 그리드의 **가장자리 칸에 FA가 몰리는 측정 인공물**(`labels_probe.json:boundary_cells` 필드 존재) | 가족 #5 / probe 주석 스키마 |

> **결재 필요 1건**: `경계칸형`이 (a) 장면 내용 가족인지 (b) 그리드 기하 인공물인지 판정. 본 문서는
> **(a) 대리선 판독**으로 가정하고 매핑했다 — (b)라면 §1의 「경계」 매핑은 전부 「장식」 또는 「조명」으로 흡수된다.
>
> **【Claude 예비 룰링 · 08-23 · 최종 채택 = 승용】** 두 독해를 경합시키지 않고 **가족을 5종으로 분리**한다:
> ① `경계칸형`은 형태소('칸' = 그리드 셀)대로 **(b) 그리드 가장자리 칸 측정 인공물**에 예약하고,
> ② (a)의 내용 가족은 **`대리선형`**(줄눈·도색·재질 전환을 낙차 엣지로 오독)으로 신설한다 — 두 성질은
> 직교라(한 FA 사건이 둘 다일 수 있음) 하나의 이름에 욱여넣으면 CPU-2 센서스가 세지 못한다.
> 본 문서 §1의 「경계」 표기는 **`대리선형`으로 재독**한다(별도 재작성 없음 — 본 각주가 매핑 규칙).
> CPU-2 센서스는 5가족 {장식·지형통계·조명·대리선·경계칸} + 다중 소속 허용으로 설계하고,
> 원 4가족 나열(DZ §8.1)과의 대응을 센서스 문서 서두에 명시한다. D54 등재.

### 0.2 현재 코퍼스에 이미 있는 것 (갭 지도의 기준선)

- **hard negative 5종** (`scenes/batch1/`, GT = 낙차 없음): `N1` 그림자 띠 · `N2` 아스팔트 패치 ·
  `N3` 트롱프뢰유 · `N4` 내림 램프 · `N5` 평면 그레이팅 `[내부]`
- **조건 변주 3종**: `C1` 눈 · `C2` 낙엽 · `C4` 젖음 `[내부]`
- **결정적 결함**: `cue+/label−`(단서 있음·낙차 없음) 칸이 **1/33 = 3%**, 목표 ≥20%.
  `P(낙차|난간) = 17/18 = 0.944` `[내부: cue_expansion_survey_v1.md §2]`
- 즉 **N1–N5는 "단서도 없고 위험도 없는" D팔(무위험−단서)에 가깝다.** V3가 필요로 하는 것은
  **C팔(무위험+단서)** — 이 문서 §3이 그 칸을 채운다.

---

## 1. 오인 유발원 분류표

### 1.1 조명·암부 계열 — 「어두우면 구멍」

| # | 유발원 | 왜 낙차로 읽히는가 (기제) | FA 가족 | 시뮬 재현성 (Isaac Sim RTX) | 출처 |
|---|---|---|---|---|---|
| A1 | **보도·노면을 가로지르는 하드 캐스트 그림자 밴드** (캐노피·가로수·건물) | 낙차의 **내재 단서 중 하나가 함몰부 self-shadow**(하늘 가림으로 생긴 어두운 폐곡선)다. 캐스터 그림자는 **원리상 같은 신호**를 만든다 — 구분 불가가 기본값 | 조명 (+경계: 밴드 경계선) | **높음** — 자산·해는 이미 있음. 다만 **`cue_shadow_caster` 토글 부재**로 "그림자 ⊥ 위험" 독립 강제가 구현 불가 `[내부]` | S1, S9 |
| A2 | **차량 AEB/AV의 오브레이킹(phantom braking)** — 육교·고가·건물이 노면에 그은 날카로운 그림자선 | "도로를 가로지르는 급격한 명암 선이 카메라계에는 **정지 물체처럼 보인다**". 레이더를 뺀 카메라 단독 스택에서 급증 | 조명 | **높음** — 태양고도·캐스터 폭 스윕으로 직접 재현 | S9 |
| A3 | **터널·지하차도 입구 암부 (black hole effect)** | 주간 접근 시 입구 휘도가 눈/센서의 순응 휘도보다 훨씬 낮으면 내부가 **완전한 검은 면**으로 보인다. CIE가 threshold zone 조명을 규정하는 이유가 이것 | 조명 + 지형 | **중** — 렌더는 가능하나 **과노출 금지 조항**과 톤매핑 정책에 걸림. 노출·EV 스윕 필요 | S10 |
| A4 | **실내 문턱의 검은 매트·짙은 카펫** — 청소로봇 cliff 센서의 고전 오작동 | IR cliff 센서는 **반사강도**로 판정 → 검은 표면이 IR을 흡수해 반사가 사라지면 "허공"으로 판정. RGB 쪽에서도 같은 저휘도 패치가 홀로 뜬다 | 조명 (+장식: 매트는 설치물) | **높음** — 평면 저알베도 패치. 단 **실외 도메인 밖** | S6 |
| A5 | **치매 케어의 "visual cliff" 현상** — 검은 매트를 배회 억제용으로 깔면 환자가 **구멍으로 오인해 회피**한다 | 인간 지각에서도 **색·명도의 급변을 깊이·평면 변화로 오독**한다는 임상 관찰. Gibson & Walk(1960) visual cliff의 임상판 | 조명 | **높음** (동일 자산) | S7, S8 |

### 1.2 반사·투과 계열 — 「비치면 뚫려 있음」

| # | 유발원 | 기제 | FA 가족 | 재현성 | 출처 |
|---|---|---|---|---|---|
| B1 | **젖은 노면·물웅덩이의 하늘 경면반사** | 물 표면은 **큰 입사각에서 수평 거울로 동작**하고, 반사율은 거리에 따라 증가(Fresnel). 지평선 **아래**에 하늘색이 나타나는 것이 JPL 수면 검출기의 원리 — 즉 "지면인데 하늘이 보이는 띠" = **낙차 너머 하늘**과 같은 문법 | 조명 + 경계 | **중(난점)** — RTX 반사는 켜지지만 (i) 재질 동결(법6)로 `cue_water_surface` 보류 상태, (ii) RTX **센서** 계통은 물/거울을 불투명체와 동일 취급하는 알려진 한계가 있어 **RGB와 depth 팔의 물리 정합이 깨질 수 있다** — 시각 렌더로만 쓰고 depth GT는 검산 필요 | S11, S18 |
| B2 | **단안 깊이 추정의 non-Lambertian 실패** — 거울·유리·수면 | 모델이 **표면의 깊이**를 낼지 **반사상 물체의 깊이**를 낼지 갈린다(Depth Anything V2/Depth Pro 계열에서 관측). 후자면 평면 위에 **가짜 함몰**이 생긴다 | 조명 + 지형 | **중** — 유리·수면 자산 필요, 법6 저촉 | S12 |
| B3 | **유리 바닥·전망대 스카이워크** | 투명면 아래가 그대로 보여 **지지면이 시각적으로 소거**된다. 사람도 난간을 붙잡고 기어간다 — "공학적 안전 ≠ 지각적 안전"의 가장 순수한 사례 | 조명 + 장식 | **낮음** — 투명 재질 신규 + 법6. 우선순위 하 | S13 |
| B4 | **얕아 보이는 침수 노면** | 반사가 지배하면 **깊이 단서가 소실**되어 사람도 수심을 과소평가한다(홍수 익사의 절반 이상이 차량 진입) | 조명 | **낮음** — 유동수 시뮬 비용 과다 | S14 |

### 1.3 지면 문양·설치물 계열 — 「어두운 원반·격자·직선」

| # | 유발원 | 기제 | FA 가족 | 재현성 | 출처 |
|---|---|---|---|---|---|
| C1 | **맨홀 뚜껑** (보도용 φ648) | 평탄면 위의 **어두운 원반**. 포트홀 검출기의 대표 오탐원 — 데이터셋들이 맨홀을 **명시적 클래스로 추가**해야 했을 만큼 구조적 | 경계 + 조명 | **높음** — `derive_manholes`·`build_manhole` 빌더 존재, 신규 에셋 0 `[내부]` | S15, S16 |
| C2 | **배수 그레이팅·측구·트렌치 커버** | **어두운 평행선 밴드** = 계단 챌면/낙차 림과 같은 저역 신호. 실제 위험도 병존한다(진행방향 평행 슬롯은 자전거 바퀴를 삼킨다) — 즉 **"진짜 위험이 없는데 위험처럼 생긴" 것과 "진짜 위험"이 같은 외형** | 경계 + 조명 | **높음** — `N5` 평면 그레이팅 씬 선례 존재 | S17 |
| C3 | **수목보호 격자(tree grate, flush)** | 평탄 보도 위의 **어두운 정사각 격자**. 낙차 없는 곳에 놓인 낙차 신호의 전형 | 경계 + 조명 | **높음** — 격자 4~8프림, 지면 메시 무수정. **단 리세스·개구부 컷은 hazard로 분리**(법7) `[내부]` | `[내부]` (산림청 고시 2-3(5) / korean_geom §5.3) |
| C4 | **수축줄눈·신축이음** (6 m / 12~20 m 리듬) | 단차 0인데 포장면을 가로지르는 **규칙적 직선**. 1~2단 계단의 riser 밴드와 통계적으로 구분 난망 | 경계 | **높음** — `build_slab_joints`/`build_joint_grid` 기구현 `[내부]` | — (`[내부]` korean_geom §3.4) |
| C5 | **검은 아스팔트 패치·타르 실링 심** | 신·구 포장의 알베도 차 → **저휘도 폐영역**. 포트홀 검출 실패 사례 중 "표면 결함 vs 보수 패치"의 구조적 모호성이 명시적으로 보고됨 (사람도 어렵다고 기술) | 조명 + 경계 | **높음** — `N2` 존재 | S15, S16 |
| C6 | **노면표시** (정지선·횡단보도·차선·황색 연석 도색) | 진행방향에 수직인 **백색 밴드**는 저고도 시점에서 계단코 라인과 같은 신호. 균열 검출기가 백색 도색을 마스킹해야 오탐이 준다고 명시 | 경계 | **높음** — `build_road_marking` 씬별 on/off 기구현, **키 승격만** 필요 `[내부]` | S16 |
| C7 | **3D 착시 횡단보도** (아이슬란드·뉴델리) | **의도적으로** 평면 도색을 공중 부양 블록/구덩이로 보이게 설계 — 실제로 통과 속도가 30 km/h로 떨어짐. "평면 텍스처만으로 깊이 오인을 만들 수 있다"의 **현장 증명** | 경계 + 조명 | **높음** — `N3` 트롱프뢰유가 이 칸 | S19 |
| C8 | **가짜 캐틀그리드**(도로에 줄무늬만 도색) | 가축이 **낙하 착시**를 일으켜 네 발로 급제동. 실물 그리드와 동등한 회피율이 실험적으로 보고됨. 단 진흙에 덮이면 무효, 자갈길에선 무효 | 경계 | **높음** — 평면 텍스처 | S20 |

### 1.4 지형·기하 모호성 계열 — 「얕은 함몰인지 깊은 도랑인지 알 수 없음」

| # | 유발원 | 기제 | FA 가족 | 재현성 | 출처 |
|---|---|---|---|---|---|
| D1 | **기복 지형의 self-occlusion** | JPL 원문: *"멀리서 트렌치를 보면 **주행 가능한 얕은 함몰인지 통과 불가한 깊은 도랑인지 구별할 수 없다**"*. 후행 엣지 상승 사면(trailing-edge upslope)이 보이면 깊이 추정이 되지만, 안 보이면 원리적으로 불가 | 지형 | **높음** — 카메라 pitch·거리·둔덕 곡률로 직접 제어 (씬21 자기차폐 선례) | S3 |
| D2 | **가시 개구의 1/d² 소실** | 양의 장애물 각크기는 1/R로 줄지만 **음의 장애물은 1/R²**로 줄고, *"보이는 부분만으로는 깊이를 거의 알 수 없어 **오경보와 미탐지의 여지가 크다**"* | 지형 | **높음** (기하) | S1 |
| D3 | **강도 불연속을 단서로 쓰면 오경보** | *"가장 명백한 대안인 강도 불연속은 **조명 조건에 크게 의존하고 오경보에 취약**하다고 여겨져"* 기하 기반 연구가 주류가 됐다 — **본 프로젝트의 문제의식을 문헌이 30년 전 예고한 문장** | 조명 | — (해석 근거) | S1 |
| D4 | **지면 위 수평 구조물의 열/명도 서명** | 초기 알고리즘이 *"지면보다 따뜻하지만 지면 **위에** 있는 수평 구조물"*에 오경보. 후속 수정은 **ground-plane 소속 검증**을 추가한 것 → 우리 aux 마스크 설계의 직접 선례 | 지형 | 해당 없음 (열 모달리티) | S2 |
| D5 | **바퀴자국(wheel track) 열 서명 오경보** | 96프레임 중 3프레임이 **주변보다 따뜻한 바퀴자국**에서 오경보 | 조명 | 해당 없음 | S1 |
| D6 | **폐색(occlusion)은 낙차의 충분조건이 아니다** | Heckman 계열의 정식 명칭이 *"**potential** negative obstacle"* 인 이유 — 누적 3D 데이터의 빈 영역은 낙차일 수도, 단순 자기폐색일 수도 있어 **맥락 라벨링(context-based occlusion labeling)** 단계가 별도로 필요하다. "구멍처럼 보이는 것"과 "구멍"을 분리하는 것이 이 문제의 정의 자체 | 지형 | **높음** — 폐색만 만들고 낙차는 없는 배치(둔덕 뒤 평지)로 직접 재현 | S4 |

### 1.5 데이터셋 공백 — 「음의 장애물은 라벨이 없다」

| 관측 | 근거 | 함의 |
|---|---|---|
| **RELLIS-3D**: void 포함 20클래스 — sky, grass, tree, bush, concrete, mud, person, **puddle**, rubble, barrier, log, fence, vehicle, object, pole, water, asphalt, building 등. **hole/ditch/trench/cliff/drop-off 클래스 없음** | S21 | 오프로드 SOTA 데이터셋조차 **음의 장애물을 클래스로 갖지 않는다** |
| **ORFD**: traversable / non-traversable / unreachable 3분류. 낙차는 "unreachable"에 흡수 | S22 | 낙차가 **독립 라벨이 아니라 잔여 범주** |
| **RUGD**: Smooth/Rough/Bumpy/Forbidden/Obstacle/Background로 병합 운용 | S22 | 동일 |
| JPL 계열은 라벨 대신 **열 서명**으로 우회 | S1, S2 | *"기하가 안 보일 때 문헌의 답은 열이었다"* — **RGB 맥락단서 연구의 공백**이 본 프로젝트의 자리 `[내부]` |

> **논문 §관련연구용 한 줄 (확정 가능)**: 음의 장애물은 (i) 기하학적으로 원거리에서 소실되고(1/R²),
> (ii) 강도 단서는 조명 의존·오경보 취약으로 일찍이 기각됐으며, (iii) **주요 공개 데이터셋에 클래스 자체가 없다.**
> 세 문장 모두 1차 출처로 뒷받침된다 (S1, S2, S3, S21, S22).

### 1.6 실세계 사고 — 「단서 없는 위험」이 어디 몰리는가 (④-b 동기)

| 사례 | 요지 | 출처 |
|---|---|---|
| **뚜껑 열린 맨홀 사망** (NYC 2026-05) | 트럭이 뚜껑을 밀어낸 뒤 **12분간 무방비**. 보행자가 하차하다 3 m 아래로 추락, 사망 | S25 |
| 동종 반복 (St. Louis 2026-07, Buffalo) | 인도 위 뚜껑 결실 — 경상/양 발목 골절. **관리 주체 불명확**이 반복 요인 | S25 |
| **배달로봇 운하 추락** (Milton Keynes) | 보도 주행 로봇이 **그대로 수로로 진입**. 로봇 시점에서 수면 경계가 지면 연속으로 읽힌 것과 정합 (추정) | S26 |
| **Cruise 로보택시, 굳지 않은 콘크리트 진입** (SF 2023-08) | 공사구간의 **표면 상태 변화**를 통과 가능면으로 오판, 앞바퀴 매몰 | S27 |
| **굴착 구간 방호 미설치** | OSHA/실무 자료: *"통행 구역의 굴착은 **울타리 등 물리적 방벽으로 격리**해야"* 하나, 굴착 후 방벽 설치 전 이탈·야간 철거 후 미복구가 반복 유형 | S28 |
| **도로 이탈(ROR) 사망의 지방도 집중** | ROR 사망의 **80%가 지방도**, 그 중 약 90%가 **2차로 지방도**. 급사면·낙차 구간에서 방호울타리 유무가 생사를 가름 | S29 |

> **④-b 논지 (문헌 정합)**: 실제 사고는 **단서가 정상 작동하는 곳이 아니라, 단서가 없거나 일시적으로 사라진 곳**
> — 관리 공백(뚜껑 결실), 공사 중 방벽 부재, 미정비 지방도 — 에 몰린다. 따라서 정직한 시스템의 목표는
> "무단서 위험을 확신 탐지"가 아니라 **낮지만 0이 아닌 확률 + 신중 행동**이라는 V3 §2.4-(b)의 설계 결정이
> 사고 통계로도 지지된다 `[내부 + S25~S29]`.

---

## 2. 시뮬-현실 갭 지도

**점수 규칙**: `갭 점수 = 현실 빈도(1–5) × 시뮬 재현성(1–5) × 부재 계수`
(부재 계수: 1.0 = 코퍼스 전무 / 0.6 = 자산은 있으나 **제어면(토글)·분산 배치 없음** / 0.2 = 이미 있음)

| 순위 | 유발원 | 현실 빈도 | 재현성 | 현재 상태 | 갭 점수 | 우선 조치 |
|---|---|---|---|---|---|---|
| **1** | **맨홀 뚜껑** (평탄 보도 위 어두운 원반) | 5 | 5 | **0/33 전무** `[내부]` | **25.0** | `cue_manhole` 신설 — 빌더 존재, 착지만 |
| **2** | **수목보호 격자 (flush)** | 4 | 5 | **0/33 전무** | **20.0** | `cue_tree_grate` 신설. 리세스형은 hazard로 분리 |
| **3** | **배수 그레이팅·측구 (평탄부 성분)** | 5 | 5 | N5 단일 씬. **분산 키 없음** | **15.0** (0.6) | `cue_drainage` 승격 — 평탄부/하부 성분 분리 |
| **4** | **그림자 밴드 캐스터** | 5 | 5 | 자산·씬(N1·16) 있으나 **토글 부재 → 위험과 독립 강제 불가** | **15.0** (0.6) | `cue_shadow_caster` 신설. **양성 씬에도 동일 비율**(음성 전용이면 "그림자=안전" 역지름길) |
| **5** | **줄눈·신축이음 규칙 직선** | 5 | 5 | 빌더 존재, **키 미승격·전 프로파일 미착지** | **15.0** (0.6) | `cue_slab_joint` 승격 |
| **6** | **노면표시 (정지선·횡단보도·연석 도색)** | 5 | 5 | 씬별 on/off는 되나 **키 아님** | **15.0** (0.6) | `cue_road_marking` 키 승격 (신규 기하 0) |
| **7** | **젖은 노면 하늘 경면반사** | 4 | 3 | `C4` 젖음 씬은 **조건 변주**이지 반사-FA 프로브가 아님 | **12.0** | `cue_water_surface` — **법6 해빙 후**. RTX 반사 튜닝 + depth GT 정합 검산 필수 |
| **8** | **터널·지하차도 입구 암부** | 3 | 4 | 씬02 지하도 존재하나 **입구 암부 프로브 아님** | **12.0** | 노출·threshold-zone 휘도 스윕 프로브 (조명 정책 검토 필요) |
| **9** | **기복 지형 self-occlusion (얕은 함몰 vs 깊은 도랑)** | 4 | 5 | 씬21 자기차폐 존재, **얕은-함몰 대조쌍 없음** | **8.0** (0.4, 추정) | **얕은 함몰(깊이 0.05–0.25 m) 무위험 씬**을 깊은 낙차와 페어로 — D팔 최상급 재료 |
| **10** | **실내 문턱 다크 매트** | 3 | 5 | 전무. **실외 도메인 밖** | **7.5** (0.5) | 캠퍼스 실내 로봇 시나리오로 확장할 때만 |
| **11** | **포트홀 vs 보수 패치 모호성** | 4 | 4 | `N2` 아스팔트 패치 존재 | **3.2** (0.2) | 유지. 패치-포트홀 **혼재** 프레임 추가는 저비용 |
| **12** | **유리 바닥·투명 지지면** | 1 | 2 | 전무 | **2.0** | 보류 (법6, 비용 대비 빈도 최저) |

### 2.1 갭 지도의 세 줄 요약

1. **상위 6개 중 4개가 "자산은 이미 있는데 제어면이 없다"** — 신규 모델링이 아니라 **토글 승격 작업**이
   최대 ROI다. 특히 `cue_shadow_caster` 부재는 `cue_arr §2.5`의 "그림자 = base rate 독립 강제"를
   **구현 자체 불가**로 만들고 있다 `[내부]`.
2. **완전 공백은 지면 문양 3종(맨홀·수목격자·그레이팅 분산)** — 모두 "평탄면 위의 어두운 원반/격자"이며
   현실 빈도가 최상위인데 33씬에 0건. 포트홀 검출 문헌이 **맨홀을 별도 클래스로 넣어야 했던 것**과
   같은 이유로 우리도 별도 키여야 한다(원형 vs 직선 밴드는 **FP 기하가 다르다**).
3. **젖은 노면은 "재현이 어렵다"가 아니라 "정합이 어렵다"** — RTX 시각 반사는 되지만 RTX **센서** 계통이
   물을 불투명체로 취급하는 알려진 한계가 있어, RGB 팔과 depth 팔이 **서로 다른 물리를 보게 된다**.
   이건 버그가 아니라 **모달리티 비교 실험의 교락 요인**이므로, 채택 시 반드시 depth GT 검산과 함께 간다 (S18).

---

## 3. N-cue 사양 후보 — 난이도 사다리 12종

**설계 규칙 (전부 준수)**: 낙차 < 0.3 m(대개 0~0.25 m) · 시설은 **온전한 상태만**(법1 = 08-05 독트린,
파손·처짐·결실 표현 금지) · `cue_*` 토글은 **기하 불변**(법7) · 법정 제식 표지만(법2).
난이도 = 「이 씬을 무위험으로 판정하기가 얼마나 어려운가」 1(뻔함) → 5(교묘함).

| # | 난이도 | 씬 한 줄 | 단서 객체 | 왜 위험이 없는가 (제도·실무 근거) | 지름길 모델의 오답 | 제안 키 |
|---|---|---|---|---|---|---|
| **L1** | ★☆☆☆☆ | **평지 화단 둘레 난간** — 잔디 화단을 두르는 낮은 난간, 경계석 0.15 m | 연속 난간선, 녹지경계석, 플랜터 열 | 조경 경계 목적. **추락방지 난간의 법정 의무는 「옥상광장 또는 2층 이상 노대」에 1.2 m 이상**이지, 지상 화단에는 없다 | "연속 수직 부재 + 경계선 = 낙차" → 난간 너머 전 칸 발화 | `cue_planter_edge` |
| **L2** | ★☆☆☆☆ | **평탄 보도의 볼라드 열** — 횡단보도 진입부, 낙차 0 | 볼라드 h 0.8–1.0 m, φ0.1–0.2 m, 간격 ~1.5 m, 반사띠 | 설치 목적이 **차량 보도 진입 억제**. 유효폭 2 m 이상 보도에 설치하는 것이 기준 — 낙차와 무관 | 반사띠 = 경고 도색으로 오독, 볼라드 열 하단 밴드 발화 | `cue_bollard` |
| **L3** | ★★☆☆☆ | **차량용 방호울타리 옆 평탄 보도** — 가드레일 뒤가 같은 높이의 인도/녹지 | W빔 가드레일, 지주 열 | 차량방호울타리의 목적은 **차량의 이탈 방지**이지 보행자 추락 방지가 아니다. 로봇 시점에서 추락 가드와 형태가 동일 | 가드레일 라인 너머 = 낙차로 확신 발화 | `cue_guardrail_road` (N4 템플릿 복제) |
| **L4** | ★★☆☆☆ | **무단횡단 금지 보행자 방호울타리 수백 m 연속** — 평탄 보도 | 파이프 난간, 반사시트 | 도로안전시설 지침이 목적을 **①추락 방지 ②횡단 금지 ③자전거·보행 안전**으로 **병렬 규정** — 같은 외형이 낙차와 무관하게 서는 **제도적 근거** | "가장 긴 난간선 = 가장 큰 낙차" | `cue_pedestrian_fence` |
| **L5** | ★★★☆☆ | **턱낮춤 횡단보도의 점형블록** — 경계 높이차 ≤ 2 cm인데 경고블록은 만발 | 점형블록(폭 = 횡단보도 폭, 세로 60 cm), 선형블록 유도로, 연석경사로 | **교통약자법 시행규칙**: 보도-차도 경계 높이차 **2 cm 이하**로 하고 진입부에 **점형블록 설치 의무**. 즉 **법이 "낙차 없음"과 "경고블록"을 동시에 강제**한다 — N-cue의 교과서 사례. ADA/PROWAG도 동일 구조(flush transition에 truncated dome 의무) | "경고블록 = 낙차 임박" → 횡단보도 전 밴드 전체 고확률 | `cue_tactile` (기존 키 재배치) |
| **L6** | ★★★☆☆ | **버스정류장·승강장 경계 경고블록** — 실제 단차는 연석 0.15–0.25 m | 점형블록 띠, 정류장 시설물 | 승강장 경계 detectable warning은 **승·하차 가장자리 전 구간**에 요구된다. 철도 승강장(진짜 낙차)과 **버스정류장(연석뿐)이 동일 제식** | 철도 승강장에서 학습한 "경고블록 = 큰 낙차"를 그대로 전이 | `cue_tactile` × 정류장 배경 |
| **L7** | ★★★☆☆ | **평지 복도·통로 연속 손잡이** — 계단 없음 | 손잡이 h 0.85 m, 벽 이격 50 mm, 브래킷 리듬 | 편의증진법 시행령 별표2가 **의료·노유자·공공청사·학교의 평지 복도** 손잡이를 의무화 — **손잡이는 계단 전용 부재가 아니다** | "손잡이 = 계단 = 낙차" | `cue_level_handrail` |
| **L8** | ★★★☆☆ | **지상 평면 주차장의 차륜막이 열 + 가장자리 울타리** | 차륜막이 콘크리트 열, 경계 울타리, 주차구획선 | 옥상·데크 주차장 가장자리에는 법정 추락방지 시설이 붙지만, **같은 차륜막이가 지상 평면 주차장 전부에** 있다. 차량 없이 빈 주차면으로 연출(법5) | "낮은 수평 블록 열 + 울타리 = 데크 가장자리" | `cue_wheelstop` |
| **L9** | ★★★★☆ | **돌출형 지하철 환기구가 선 평탄 보도** — 계단 입구는 수십 m 밖 | 투시형 루버 박스(h ~2 m), 안전 난간 | "지하 공간이 근처에 있다"는 **최대치 신호**를 주면서 서 있는 자리는 **완전 평탄 보도**. 계단 입구와 이격되는 것이 정상 배치 | "지하 구조물 = 하행 개구부" → 환기구 주변 칸 발화, 진짜 계단 입구는 놓침 | `cue_vent_shaft` (돌출형 한정) |
| **L10** | ★★★★☆ | **지면 문양 삼중주** — 평탄 보도에 맨홀 + flush 수목격자 + 신축이음이 한 화면에 | 어두운 원반 · 어두운 정사각 격자 · 규칙적 직선 | 셋 다 **단차 0**. 그런데 셋 다 "어두운 폐영역/평행 밴드"라는 **낙차의 저역 신호 문법**을 갖는다. 인공 부재 없이 **지면 문양만으로** 만든 N-cue | 원반·격자·직선을 각각 개구부/그레이팅/계단코로 오독 → **한 프레임에 서로 다른 세 종류 FA**가 동시 발생(가족 분해에 최적) | `cue_manhole` + `cue_tree_grate` + `cue_slab_joint` |
| **L11** | ★★★★☆ | **공사 종료 후 남은 임시 시설** — 굴착 복구는 끝났고 포장은 평탄, 라바콘·PE드럼·가설 휀스만 아직 서 있음 | 라바콘 열, PE드럼, 가설 휀스, 법정 공사 표지 | 실무·규정 모두 **"해당되지 않는 표지는 제거·차폐하라"**고 요구할 만큼 흔한 상태(잔존 표지가 표지 신뢰도를 잠식). **표지는 있고 위험은 이미 사라진** 시간차 사례 | "공사 표지 = 굴착 = 낙차" → 복구된 평탄면에 고확률 | `cue_temp_barrier` (**법1: 온전 상태만**, 등간격 금지) |
| **L12** | ★★★★★ | **약단서 중첩 골목 코너** — 평지에 볼록거울 + 시선유도봉 + 캐노피 그림자 밴드가 동시에 | 볼록거울(면 1.8–2.5 m), 시선유도봉 열, 그림자 캐스터 | 볼록거울의 설치 근거는 **시거 부족**이지 낙차가 아니다. 시선유도봉은 차로 분리용으로 **대량** 쓰여 낙차 상관이 구조적으로 약하다. 여기에 **조명형 FA(그림자 밴드)**를 겹쳐, 어떤 가족이 발화를 주도하는지 분해 | 개별로는 약한 단서 셋이 **합산되어** 임계를 넘김 → "다중 약단서 합"이 지름길인지 검증 | `cue_convex_mirror` + `cue_delineator` + `cue_shadow_caster` |

### 3.1 사다리 사용 지침

- **비율**: V3 §4.1의 C팔 목표(A:B:C:D = 3:2:3:2)를 채우는 재료다. 난이도 하(L1–L4)만 넣으면
  **"난간 무시"라는 반대 방향 지름길**을 학습할 수 있으므로, **L5 이상을 절반 이상** 배치할 것 (추정).
- **필수 페어링**: 각 N-cue 씬은 가능하면 **같은 부지·같은 단서로 위험이 있는 A팔**과 짝지어야
  `FA_C − FA_D = 단서-유발 오경보 몫` 분해가 성립한다 `[내부: §12-3]`.
- **L5·L6이 논문 서술에서 가장 강하다**: "법이 낙차 없는 곳에 경고 단서를 **의무화**한다"는 것은
  N-cue가 데이터 인공물이 아니라 **제도적으로 보장된 현실 분포**임을 뜻한다. 한국(교통약자법 시행규칙)과
  미국(PROWAG/ADA) 양쪽이 같은 구조라는 점에서 **국제적 일반성**도 확보된다.
- **L11 주의**: 법1(파손·열화 금지)과 충돌하기 쉽다. "철거를 안 한 것"이지 "부서진 것"이 아니라는 점을
  룩체크 항목으로 명시 — 콘·드럼은 **신품 상태**, 배치만 잔존.
- **부작용 경보**: `cue_shadow_caster`를 음성 씬에만 넣으면 **"그림자 = 안전"이라는 역지름길**이 생긴다.
  양성 씬에도 동일 비율로 넣어 base rate 독립을 강제해야 한다 `[내부: cue_arr §2.5]`.

---

## 4. 파일럿 Ncue 컷 후보 (실사 6컷)

**촬영 규약** (`REALWORLD_GRID_PROTOCOL.md` §5 준수): 같은 부지·같은 카메라고(1.65 m)·같은 방향대에서
**단서는 있고 0.3 m 이상 낙차는 없는** 지점. `sites.csv`의 `tier` 열에 **`N-cue`** 기재,
`dist_m`은 레이저/보폭 실측, 밴드는 실측 거리로 부여(투영 금지) `[내부]`.
파일럿 20장 구성은 **V4 / E4 / H4 / N-turn4 / N-cue4** — 아래 6컷 중 4컷을 본선, 2컷을 예비로 쓴다.

| 컷 | 장면 | 프레이밍 지시 | 대응 사다리 | 왜 이 컷인가 |
|---|---|---|---|---|
| **P1** | **캠퍼스 화단 둘레 난간** | 난간선이 화면을 **좌→우로 가로지르게**, 난간 너머 평탄 잔디가 **band 2–3a(2–8 m)**에 걸치도록. 경계석 높이를 줄자로 기록 | L1 | V3 §2.4-(a)가 **문서에 명시한 바로 그 예시**. 가장 해석이 명확한 기준컷 |
| **P2** | **정문·교차로 턱낮춤 횡단보도 점형블록** | 점형블록 띠가 **band 1–2**에 오도록 정면. 연석 높이차를 자로 재서 `notes`에 ≤2 cm 기록 | L5 | **법이 강제한 N-cue.** 높이차 실측치가 그대로 "위험 없음"의 증거가 된다 |
| **P3** | **버스정류장 승강장 경계 점자블록** | 정류장 시설물(쉘터·표지주)이 프레임에 들어오게, 블록 띠가 **band 2**. 연석 0.15–0.25 m 실측 | L6 | 철도 승강장(진짜 낙차)과 **동일 제식**이라 전이 오류를 직접 잰다 |
| **P4** | **보도 진입부 볼라드 열** | 볼라드 3–5개가 **band 2–3a에 원근으로** 늘어서게. 반사띠가 보이는 조도 | L2 | 내부 실측에서 `P(낙차\|볼라드) = 0.737`로 **유일하게 탈상관된 단서** — sim의 예측이 실세계에서도 유지되는지 검증 |
| **P5** | **캠퍼스 진입로 차량용 가드레일 + 평탄 보도** | 가드레일이 화면을 가로지르고 **그 너머가 같은 높이의 지면**임이 보이게. 역광 회피 | L3 | `N4`가 sim에서 검증된 유일 템플릿 — **sim↔real 동형 페어**를 만들 수 있는 유일한 컷 |
| **P6** | **평탄 보도의 맨홀 + 수목보호격자 + 줄눈** | 인공 부재를 **프레임에서 배제**하고 지면 문양만. 맨홀이 **band 2**, 격자가 **band 3a** | L10 | 갭 지도 1·2·5위를 한 장에 담는다. **"난간이 없어도 짖는가"** — 장식형 vs 경계형 FA를 실세계에서 분리 |

**예비컷** — 여건이 되면: **P7** 평지 복도 연속 손잡이(건물 내부, L7) · **P8** 지상 평면 주차장 차륜막이 열(L8).

### 4.1 촬영 시 반드시 함께 기록할 것

1. **낙차 없음의 물증**: 경계석/단차 높이 실측치(cm)를 `notes`에. "0.3 m 미만"이 판정의 전제이므로
   숫자가 없으면 그 컷은 N-cue로 못 쓴다.
2. **같은 부지의 A팔 후보**: 같은 장소에 진짜 낙차가 있으면 그 방향도 찍어둔다 —
   **동일 부지 페어**만이 배경 교락 없이 `FA_C − FA_D`를 흉내낼 수 있다.
3. **태양 방위·시각**: 조명형 FA(그림자 밴드)가 우연히 섞이면 가족 분해가 오염된다.
   P1–P6은 **그림자 밴드가 프레임을 가로지르지 않는 시간대**에, 별도로 그림자가 걸친 판본을 1장 더 찍으면
   조명형 FA의 실세계 증거가 공짜로 생긴다 (추정).
4. **N-turn과의 구분**: 몸을 돌린 컷(N-turn)은 배경·재질·노출이 전부 바뀐 **다른 씬**이므로
   낮은 FA를 성능 근거로 쓸 수 없다 — N-cue만이 "단서만 보고 짖는가"를 답한다 `[내부]`.

---

## 5. 출처 목록

### 5.1 음의 장애물 검출 1차 문헌

| ID | 출처 | URL |
|---|---|---|
| S1 | L. Matthies, A. Rankin, *Negative Obstacle Detection by Thermal Signature* (JPL/Caltech; IROS 2003) — negative-obstacle geometry, 1/R² visible-aperture loss, "great potential for false alarms", wheel-track thermal false alarms | https://www-robotics.jpl.nasa.gov/media/documents/matthies-negobs.pdf |
| S2 | A. Rankin, A. Huertas, L. Matthies, *Nighttime Negative Obstacle Detection for Off-Road Autonomous Navigation* (SPIE 6561, 2007) — depression vs drop-off taxonomy, false alarms on above-ground warm horizontal structure, ground-plane filtering | https://www-robotics.jpl.nasa.gov/media/documents/spie2007-rankin-6561-2.pdf |
| S3 | 동 S2, Fig.1 — *"one cannot tell if there is a slight depression that is traversable, or a deep trench"* (terrain self-occlusion ambiguity; trailing-edge upslope) | (동일) |
| S4 | C. Heckman, J.-F. Lalonde, N. Vandapel, M. Hebert, *Potential Negative Obstacle Detection by Occlusion Labeling* (IROS 2007) — 3D data accumulation → occluder propagation → context-based occlusion labeling | https://www.semanticscholar.org/paper/9d74dff3c4d2f8c924e33a7e775588568370d204 |
| S5 | P. Shang et al., *LiDAR Based Negative Obstacle Detection for Field Autonomous Land Vehicles* (Journal of Field Robotics, 2016) | https://onlinelibrary.wiley.com/doi/abs/10.1002/rob.21609 |

### 5.2 지각·오인 (인간·로봇)

| ID | 출처 | URL |
|---|---|---|
| S6 | *Why Robot Vacuums Fail on Dark/Black Flooring* — IR cliff sensor reads absorbed reflection as void; dark rug = false cliff | https://www.expertsinvacuum.com/why-robot-vacuums-fail-on-dark-black-flooring/ |
| S7 | *Dementia Mats and the Visual Cliff* — black mats deliberately used because residents misread darkness as a drop-off | https://www.matshop.com.au/blog/dementia-mats-and-the-visual-cliff |
| S8 | *Visual Cliff Experiment (Gibson & Walk, 1960)* — glass over apparent drop; depth avoidance | https://www.simplypsychology.org/visual-cliff-experiment.html |
| S9 | *Overpass shadow artifact causing braking while in Autopilot* (Tesla Forums) / *Phantom Braking: causes* — sharp shadow line across road reads as a stopped object to camera-only stacks | https://forums.tesla.com/discussion/173114/overpass-shadow-artifact-causing-braking-while-in-autopilot · https://www.mechanicinsights.com/2026/05/phantom-braking-and-tesla-fsd.html |
| S10 | *Traffic Safety Improvement via Optimizing Light Environment in Highway Tunnels* (PMC) — "black hole effect" at tunnel threshold zone; CIE luminance zoning | https://pmc.ncbi.nlm.nih.gov/articles/PMC9318541/ |
| S13 | *The Psychology of Glass Walkways: Why Our Brains Fear What Engineers Trust* | https://www.usglassmag.com/the-psychology-of-glass-walkways-why-our-brains-fear-what-engineers-trust/ |
| S19 | *3D Zebra Stripe Crosswalk in Iceland Slows Traffic with an Optical Illusion* (원형: New Delhi, 평균속도 30 km/h로 저감) | https://mymodernmet.com/3d-crosswalk-iceland/ |
| S20 | *Cattle Fooled by Phoney Grids* — painted stripes create illusion of a drop; naïve cattle avoid as much as real grids | https://www.sheldrake.org/research/morphic-resonance/cattle-fooled-by-phoney-grids |

### 5.3 반사·수면·깊이 추정

| ID | 출처 | URL |
|---|---|---|
| S11 | A. Rankin, L. Matthies, P. Bellutta, *Daytime Water Detection Based on Sky Reflections* (ICRA 2011) — water acts as horizontal mirror at large incidence angles; sky reflected below the horizon; FP ≤ 0.58% | https://www-robotics.jpl.nasa.gov/media/documents/rankin-icra-2011-water-final.pdf |
| S12 | *Towards Robust Monocular Depth Estimation in Non-Lambertian Surfaces* (arXiv 2408.06083) / *Intrinsic Image Decomposition for Robust Self-supervised MDE on Reflective Surfaces* (arXiv 2503.22209) — models split between predicting the surface vs the reflected object | https://arxiv.org/abs/2408.06083 · https://arxiv.org/html/2503.22209 |
| S14 | *The Dangers of Driving on Flooded Roads* (Consumer Reports) — flood water is routinely deeper than it looks; >50 drownings/yr from driving into water | https://www.consumerreports.org/cars/car-safety/the-dangers-of-driving-on-flooded-streets-a8035090841/ |
| S18 | Isaac Sim — *RTX Sensor Non-Visual Materials* docs / issue #547 *"Material-based reflectance ignored — water (reflective) treated the same as others"* / *Configuring Rendering Settings* (`/rtx/reflections/enabled`) | https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_rtx_materials.html · https://github.com/isaac-sim/IsaacSim/issues/547 · https://isaac-sim.github.io/IsaacLab/main/source/how-to/configure_rendering.html |

### 5.4 노면 오탐 (포트홀·맨홀·패치·도색·그레이팅)

| ID | 출처 | URL |
|---|---|---|
| S15 | *YOLOv8 and point cloud fusion for enhanced road pothole detection* (Sci. Rep. 2025) — false positives from manhole covers, patches, stains, shadows; elevation threshold used to filter | https://www.nature.com/articles/s41598-025-94993-0 |
| S16 | *iWatchRoad: Scalable Detection and Geospatial Visualization of Potholes* (arXiv 2508.10945) — "shadow misclassification as a pothole demonstrates the necessity of comprehensive negative sample training"; negative samples include shadows, stains, utility access covers; white paint masked to suppress false cracks | https://arxiv.org/html/2508.10945 |
| S17 | *Parallel stormwater grates can endanger cyclists* (Greater Greater Washington) / FHWA *Correcting Unsafe Drainage Features* | https://ggwash.org/view/67323/ · https://highways.dot.gov/safety/local-rural/maintenance-drainage-features-safety/iv-correcting-unsafe-drainage-features |
| S24 | *Negative obstacle detection and avoidance using YOLOv8 and depth profile analysis* (Discover Applied Sciences, 2026) — 최근 계열도 **깊이 프로파일 검증을 별도로 붙여야** 오탐이 잡힌다는 구조를 재확인 | https://link.springer.com/article/10.1007/s42452-026-08326-5 |

### 5.5 데이터셋 (음의 장애물 라벨 부재)

| ID | 출처 | URL |
|---|---|---|
| S21 | RELLIS-3D (unmannedlab) — 20 classes incl. void; sky/grass/tree/bush/concrete/mud/person/puddle/rubble/barrier/log/fence/vehicle/object/pole/water/asphalt/building. **No hole/ditch/trench/cliff/drop-off class** | https://github.com/unmannedlab/RELLIS-3D |
| S22 | ORFD: *A Dataset and Benchmark for Off-Road Freespace Detection* (ICRA 2022, arXiv 2206.09907) — traversable / non-traversable / unreachable only. RUGD 병합 운용은 arXiv 2603.27931 참조 | https://arxiv.org/pdf/2206.09907 · https://arxiv.org/pdf/2603.27931 |
| S23 | CAVS Off-Road Dataset (Mississippi State) — 12,300 images, traversability-annotated | https://www.cavs.msstate.edu/resources/autonomous_dataset.php |

### 5.6 실세계 사고·사건 (④-b)

| ID | 출처 | URL |
|---|---|---|
| S25 | *Donike Gocaj dies after falling into open manhole in Midtown Manhattan* (ABC7 NY, 2026) — cover dislodged by truck, uncovered ~12 min, 10 ft fall, fatal / *Woman falls into open manhole in north St. Louis* (First Alert 4, 2026-07) | https://abc7ny.com/post/woman-dead-falling-uncovered-manhole-midtown-nyc/19129645/ · https://www.firstalert4.com/2026/07/07/woman-falls-into-open-manhole-north-st-louis-city-says-its-not-their-responsibility/ |
| S26 | *Delivery robot plunges into canal* (FOX 5 NY) — Starship robot drove straight into a Milton Keynes canal | https://www.fox5ny.com/news/delivery-robot-plunges-into-canal |
| S27 | *Cruise Robotaxi Drives Into Wet Concrete* (Forbes, 2023-08) — front wheels sank in freshly poured concrete in a construction zone | https://www.forbes.com/sites/bradtempleton/2023/08/17/cruise-robotaxi-drives-into-wet-concrete-waymo-shows-off-same-route/ |
| S28 | OSHA *Highway Work Zones and Signs, Signals, and Barricades* / NSC *Fall Hazards in Trenching and Excavation* — excavations in traveled areas must be isolated by a physical barrier | https://www.osha.gov/highway-workzones · https://www.nsc.org/getmedia/fbf42b97-5864-4bbf-a46f-956ab09df69a/tt-barricades.pdf |
| S29 | iRAP Road Safety Toolkit *Run Off Road* — 80% of ROR fatalities on rural roads, ~90% of those on rural two-lane; severity rises with embankment/drop height | https://toolkit.irap.org/crash-type/run-off-road/ |
| S30 | *Clear and Consistent Work Zone Signage* — MUTCD: signs must be removed or covered when not applicable; stale signs erode credibility | https://www.trafficsafetystore.com/blog/clear-and-consistent-work-zone-signage/ |

### 5.7 설치 규정 — "낙차 없이 단서가 서는" 제도적 근거 (N-cue의 법적 기반)

| ID | 출처 | URL |
|---|---|---|
| S31 | 「교통약자의 이동편의증진법 시행규칙」 별표2 — **보도·차도 경계 높이차 2 cm 이하**, 횡단보도 진입부 **점형블록 설치**, 연석경사로 유효폭 0.9 m·기울기 1/12 이하. **낙차 제거와 경고블록 설치를 동시에 강제** | https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=106367 |
| S32 | U.S. Access Board, PROWAG Chapter R3 — detectable warning surfaces at curb ramps/**blended transitions**/**flush transition between street and sidewalk**, full width, ≥610 mm depth; truncated dome 23 mm φ / 5 mm h / 60 mm 간격 | https://www.access-board.gov/prowag/proposed/chapter-r3-technical-requirements/ |
| S33 | ADA §705 / 810 Transportation Facilities — detectable warnings at **bus and rail boarding platform edges**, full length of public-use area | https://www.ada-compliance.com/ada-compliance/810-transportation-facilities |
| S34 | 「건축법 시행령」 제40조 — **옥상광장 또는 2층 이상 노대** 주위 **높이 1.2 m 이상 난간**. 즉 지상 화단·평지 난간에는 추락방지 의무가 없다 | https://www.law.go.kr/LSW//lsLinkCommonInfo.do?lsJoLnkSeq=1020322137 |
| S35 | 국토교통부 「도로안전시설 설치 및 관리지침 — 차량방호 안전시설편」 — 차량방호울타리의 목적은 **차량의 도로 이탈 방지**(보행자 추락 방지가 아님) | https://www.codil.or.kr/filebank/moctroadguide/LS/CIKCLS121152/CIKCLS121152.pdf |
| S36 | 행정안전부 볼라드(자동차 진입억제용 말뚝) 설치기준 — h 80–100 cm, φ10–20 cm, 간격 ~1.5 m, 충격흡수 재질, 밝은 색·반사도료. 목적은 **차량 보도 진입 억제** | https://www.newspim.com/news/view/20260804000427 |
| S37 | 국민권익위원회 보도자료 — 점자블록이 **볼라드 앞·신호등 기둥 위·교차로 중앙 방향**으로 잘못 설치된 실태. 민원 유형: 파손 1,257건 / 침범 603건 / 미설치 596건 / **오설치 재시공 요구 325건** | https://www.acrc.go.kr/board.es?mid=a10402010000&bid=4A&act=view&list_no=9757 |

> **S37의 함의**: 한국 현실에서 점자블록은 **낙차와 무관한 위치에도 상당량 설치돼 있다.**
> 이는 L5·L6이 "인위적으로 만든 함정"이 아니라 **실측 가능한 현실 분포**임을 뒷받침한다.

---

## 6. 합류 지점 — 이 문서가 다음에 무엇을 결정하는가

| 산출물 | 소비처 | 상태 |
|---|---|---|
| §1 분류표 (FA 가족 매핑) | CPU-2 시뮬 FA 센서스와 **교차 대조** → §8.1 갭 지도 완성 | **가족 정의 확정 대기** (§0.1 결재 1건) |
| §2 갭 지도 상위 6종 | `cue_*` 토글 신설·승격 백로그 → V3 §4.2 | 즉시 착수 가능 (상위 4종은 신규 에셋 0) |
| §3 사다리 12종 | V3 §4.2 **N-cue 군 사양** 초안 | 비율·페어링 결정 후 확정 |
| §4 실사 6컷 | `REALWORLD_GRID_PROTOCOL.md` §5.3 파일럿 20장 중 N-cue 4장 | 사용자 촬영 대기 |
| §1.5 + §1.6 | 논문 §관련연구 / §서론 ④-b 동기 | 1차 출처 확보 완료 |
