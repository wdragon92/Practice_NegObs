# 에셋 전수 조사 v1 — "평면으로 때운 것" 판정과 3D 조달

담당: 에셋 전수 조사·조달 / 2026-07-28
지시: *"에셋 사용한 거 전수 조사해서, 가급적 전부 실사화할 수 있도록 해줘."*
      *"낙엽도 장판 깐 것처럼 만드는거에서 탈피시켜주고"*

관련: `Docs/CREDITS.md`(라이선스) · `assets/download_vegetation.py`(조달 스크립트)

---

## 0. 요약 (먼저 읽을 것)

1. **감독 실측치 정정.** S3 `Assets/Vegetation/` 의 "Debris 26 · Rocks 75 · Shrub 312"
   는 `.thumbs/` 를 뺀 **전체 파일 수**(MDL·텍스처 포함)이지 에셋 종수가 아니다.
   실제 **USD 종수**는 Debris 5 · Leaves 5 · Rocks 15 · Shrub 37 · Trees 44 ·
   Plant_Tropical 17 이다. 이하 전부 이 실측 기준.
2. **낙엽이 장판인 이유는 텍스처가 아니라 기하다.** 지금 낙엽은
   ① `leaf_ground` 텍스처를 입힌 **평판**(`build_slope` 3매 + `_oriented_box` 2매)과
   ② **두께 6 mm 납작 타원체 900개**다. ②의 총 피복 면적은 **0.96 m²** 뿐이라
   화면의 낙엽은 사실상 전부 ①, 즉 무늬다.
3. S3 `Debris/` 5종은 **실제 잎 지오메트리**다. 조달 완료.
   fallcluster1 은 0.42 m 사방 덩어리이고 **1 m² 완전 피복에 15.9개**가 필요하다.
4. 조달 완료: 낙엽 5 · 바위 5 · 관목 5(신규) = **USD 19개, 337 MB, 참조 미해결 0건**.
5. `.gitignore` 는 `assets/vegetation/` 전체를 이미 제외하고 있어 **누락 없음**
   (신규 `Debris/`·`Rocks/` 도 커버됨을 `git check-ignore` 로 확인). 단, 주석의
   용량 표기 "~128MB" 가 이제 337 MB 라 사실과 어긋난다 — **보고만 하고 수정 안 함**.

---

## 1. 현행 에셋 전수표

### 1-a. 텍스처 (PBR 3종 세트: diff / nor / rough)

`scene_common.py` `TEX` 레지스트리 전 항목. "사용 씬"은 33개 씬 소스를 grep 한 실측.
**판정** 열: `평면 OK` = 본질적으로 평면이라 텍스처가 옳다 /
`입체여야` = 입체물을 평면으로 때웠다 / `혼합` = 용도에 따라 갈린다.

| 역할 | 파일(prefix) | 출처 | 씬 수 | 무엇을 표현하나 | 판정 |
|---|---|---|---|---|---|
| `plaza_light` | `plaza_light_*` (ambientCG Tiles038) | ambientCG CC0 | 13 | 광장 밝은 포장 타일 | 평면 OK |
| `band_dark` | `band_dark_*` (PavingStones127) | ambientCG CC0 | 6 | 광장 어두운 띠 | 평면 OK |
| `plaza_lower` | `plaza_lower_*` (PavingStones111) | ambientCG CC0 | 10 | 하부 광장 포장 | 평면 OK |
| `paving_interlock` | `paving_interlock_*` (PavingStones131) | ambientCG CC0 | 7 | 한국 보도 인터로킹 블록 | 평면 OK |
| `granite_dark` | `granite_dark_*` (PH granite_tile) | PolyHaven CC0 | 11 | 화강석 계단·연석 | 평면 OK |
| `brick_red` | `brick_red_*` (PH brick_wall_001) | PolyHaven CC0 | 21 | 벽돌 벽·건물 셸 | 평면 OK |
| `concrete_wall` | `concrete_wall_*` (concrete_wall_008) | PolyHaven CC0 | 15 | 지하도 옹벽·터널 | 평면 OK |
| `concrete_floor` | `concrete_floor_*` (brushed_concrete_03) | PolyHaven CC0 | 15 | 지하도 계단·바닥 | 평면 OK |
| `asphalt` | `asphalt_*` (asphalt_02, 3.0 m 타일) | PolyHaven CC0 | 14 | 차도·주차장 노면 | 평면 OK |
| `plaster` | `plaster_*` (painted_plaster_wall) | PolyHaven CC0 | 5 | 골목 주택 회벽 | 평면 OK |
| `marble_light` | `marble_light_*` (marble_01) | PolyHaven CC0 | 4 | 기념석·대리석 | 평면 OK |
| `sandstone` | `sandstone_*` (red_sandstone_pavement) | PolyHaven CC0 | **0** | 스텝웰·가트(미사용) | 평면 OK |
| `stone_worn` | `stone_worn_*` (stone_wall_05) | PolyHaven CC0 | 1 | 사원 마모석 | 평면 OK |
| `stone_flag` | `stone_flag_*` (stone_tiles_02) | PolyHaven CC0 | 4 | 자연석 판석 | 평면 OK |
| `wood_dark` | `wood_dark_*` (weathered_planks) | PolyHaven CC0 | 10 | 데크·침목 | 평면 OK |
| `metal_rust` | `metal_rust_*` (rusty_metal_04) | PolyHaven CC0 | 1 | 녹슨 철판 | 평면 OK |
| `tactile` | `tactile_yellow_*` (생성) | 자체 생성 | 25 | 점자블록(돌기는 노멀맵) | 평면 OK(주1) |
| `sign_*` 5종 | `assets/signs/sign_*.png` | 자체 생성 | 11/3/0 | 한글 사인 패널 | 평면 OK |
| `snow` | `snow_*` (snow_01, 2.0 m 타일) | PolyHaven CC0 | 3 | C1 적설면(단일 최대 면적 88.5%) | 평면 OK(주2) |
| `dirt_park` | `dirt_park_*` (park_dirt) | PolyHaven CC0 | 8 | 공원 흙길 | 평면 OK |
| **`gravel`** | `gravel_*` (gravel_floor) | PolyHaven CC0 | **10** | 마사토·자갈·사찰 마당 | **혼합 → 근경 입체여야** |
| **`rock_wall`** | `rock_wall_*` (rock_wall_08) | PolyHaven CC0 | **5** | 석축·사석 호안 | **혼합 → 잡석은 입체여야** |
| **`rock_face`** | `rock_face_*` (rock_surface) | PolyHaven CC0 | 2 | 절벽 암반 | 평면 OK(대형이라 정당) |
| **`grass`** | `aerial_grass_rock_*` | PolyHaven CC0 | **30** | 잔디·버지·생울타리 틴트 | **혼합 → 생울타리는 입체여야** |
| **`leaf_ground`** | `leaf_ground_*` (forest_leaves_03) | PolyHaven CC0 | **6** | 낙엽 지면·퇴적 마운드 | **입체여야 (최우선)** |

> 주1: 점자블록 돌기는 실제로는 5 mm 돌출이라 근접 시 노멀맵으로는 부족하다.
> 다만 33씬 전부에서 로봇 카메라가 0.3~1.8 m 라 현 수준으로 충분하다 [추정].
> 주2: 눈은 평면이 맞으나 **눈 덮인 관목/난간의 적설 볼륨**은 별개 문제다(범위 밖).

### 1-b. HDRI (6종 + 파생본)

| 파일 | 출처 | 사용 |
|---|---|---|
| `qwantani_noon_puresky_4k.exr` (+ `_lookfix`, `_sunless`) | PolyHaven CC0 | **기본값** — 31개 씬이 명시 지정 |
| `kloofendal_overcast_4k.exr` | PolyHaven CC0 | C1 눈 · C4 젖은 석재 (무태양) |
| `qwantani_dawn_puresky_4k.exr` (+ `_sunless`) | PolyHaven CC0 | 저고도 태양 변형 |
| `kloofendal_48d_partly_cloudy_puresky_4k.exr` (+ `_lookfix`) | PolyHaven CC0 | 하늘 조달 v1 — 산개 적운 |
| `sunflowers_puresky_4k.exr` (+ `_lookfix`) | PolyHaven CC0 | 하늘 조달 v1 — 층적운 밴드 |
| `farm_field_puresky_4k.exr` (+ `_lookfix`) | PolyHaven CC0 | 하늘 조달 v1 — 부분 흐림 |

HDRI 는 정의상 평면 문제가 없다. **조치 불요.**

### 1-c. MDL

| 파일 | 용도 |
|---|---|
| `assets/NegObsGround.mdl` | 지면 전용 커스텀 MDL(자체 작성) |
| `OmniPBR.mdl` (Isaac 동봉) | 전 재질의 기반. Rocks USD 도 이걸 검색경로로 참조 |

### 1-d. USD — **조사 전 상태: 4개뿐이었다**

| 파일 | 사용처 |
|---|---|
| `Trees/Japanese_Cherry.usd` | `build_tree` (가중치 5) — `NEGOBS_LOOK_V1=1` 일 때만 |
| `Trees/White_Pine.usd` | `build_tree` (가중치 2) |
| `Trees/Yellow_Pine.usd` | `build_tree` (가중치 1) |
| `Shrub/Boxwood.usd` | `VEG_SHRUB` 에 등록만 되어 있고 **호출부가 없다** (주3) |

> 주3: `grep -rn VEG_SHRUB` 결과 정의 1곳뿐, 사용 0곳. 즉 회양목은 받아만 놓고
> 실제로는 한 씬에서도 안 쓰이고 있다. `build_hedge`/`build_planter` 는 여전히
> 박스+블롭이다.

---

## 2. 평면으로 때운 것 — 우선순위 (화면 점유율 × 부자연스러움)

### ★★★ P0. 낙엽 — `leaf_ground`
- **어디**: sceneC2(낙엽 매몰 석계단, 씬 전체가 이 주제) · scene07 · scene10 · sceneD3
- **현행 기하**:
  - `sceneC2.build_leaf_mound()` → `build_slope` 경사판 3매 + `_oriented_box` 드리프트 2매.
    전부 `leafbed`(= `leaf_ground` 텍스처) 를 입힌 **단일 평면 덩어리**.
  - `sceneC2.build_leaf_scatter()` → `add_sphere` 로 **0.038×0.028×0.006 m 납작
    타원체 900개**. 개당 투영 면적 0.00107 m² → 900개 합계 **0.96 m²**.
    낙엽 밴드가 수 m² 인데 낱알이 1 m² 도 못 덮으니, 화면의 낙엽은 사실상 전부
    평판 텍스처다. **이것이 "장판"의 정확한 원인.**
- **대응 에셋**: `Debris/` 5종 (§4 실측표) — 조달 완료.
- **부자연스러움**: 최상. 낙엽은 정의상 낱장이 겹쳐 쌓인 것이라 실루엣과
  자기그림자가 전부다. 평면화하면 그 둘이 동시에 사라진다.

### ★★★ P1. 관목·생울타리·화단 — `grass` 텍스처 + `build_hedge`
- **어디**: `build_hedge` **20개 씬** · `build_planter` **17개 씬** · `grass` 역할 **30개 씬**
- **현행 기하**: `build_hedge` = 육면체(h×0.72) + 눌린 타원체 crown 열.
  v6 판정 C-5 가 이미 "단일 육면체는 건초 더미/흙벽돌 상자로 렌더된다"고
  지적해 crown 블롭을 얹었지만, **여전히 잎이 없다**. `build_planter` 도 동일.
- **대응 에셋**: `Shrub/Privet`(쥐똥나무, 1.70 m — 한국 생울타리 1위) ·
  `Boxwood`(1.01 m) · `Rhododendron`(철쭉) · `Juniper`(상록) — 조달 완료.
- **부자연스러움**: 높음. 화면 점유율은 낙엽보다 크나(30씬), 대개 중경·원경이라
  단위 면적당 위화감은 낙엽보다 낮다.

### ★★ P2. 잡석·호안 — `rock_wall` / `gravel` 근경
- **어디**: scene12(잡석 낱개 **96개**) · scene03(riprap 사석 띠) · scene07(마당 자갈)
- **현행 기하**: scene12 `build_rocks()` = `_oriented_box` 로 **랜덤 회전 박스**
  96개(0.30~1.10 m). scene03 riprap = `river_band` 평판.
- **대응 에셋**: `Rocks/rock_small_*` 15종 (0.128~0.314 m) — 대표 5종 조달 완료.
- **주의**: S3 바위는 **최대 0.31 m** 다. scene12 가 쓰는 0.30~1.10 m 대역의
  상단을 못 채운다 → 큰 놈은 스케일 업(질감 늘어남) 또는 여러 개 군집으로
  대체해야 한다. **평면 문제는 해결되지만 크기 문제는 남는다.**

### ★ P3. 잔디 낱포기 (`Verge_*`, `tuft`) — scene04
- `scene04_parktrail.py` 가 `add_sphere` 로 버지·헤지 블롭을 만든다.
- 대응 에셋: `Shrub/Grass_Short_A~C`(0.85~2.46 MB) · `Grass_Trimmed_A~C`(0.06~1.16 MB) ·
  `Fountain_Grass_Short/Tall`(수크령, 한국 자생) — **미조달**(이번 범위 밖).

### ─ 조치 불요 (평면이 옳다)
아스팔트 · 콘크리트 · 보도블록 · 인터로킹 · 화강석 · 벽돌 · 회벽 · 대리석 ·
판석 · 목재 데크 · 녹슨 철판 · 점자블록 · 사인 · 눈 · 흙길 · 절벽 암반.
이들은 **실제로도 연속면**이라 텍스처가 물리적으로 정확한 표현이다.
여기에 3D 를 넣으면 폴리곤만 늘고 사실감은 오히려 떨어진다.

---

## 3. S3 카탈로그 — 한국 환경 적합성 선별

전 페이지 페이징(3 페이지, 2082 키) 후 `.thumbs/` 제외 → 780 키.

| 카테고리 | 전체 파일 | **USD 종수** | 조치 |
|---|---|---|---|
| `Debris/` | 9 | **5** | **전 5종 조달** |
| `Leaves/` | 16 | 5 | **조달 안 함** (아래 사유) |
| `Rocks/` | 75 | **15** | 대표 5종 조달 |
| `Shrub/` | 152 | **37** | 대표 5종 신규 조달(+기존 Boxwood) |
| `Trees/` | 323 | **44** | 기존 3종 유지 |
| `Plant_Tropical/` | 205 | 17 | **전량 부적합, 조달 안 함** |

### 3-a. `Leaves/` 를 버린 이유 (중요)
`Leaves/` 5종은 `Debris/` 5종과 **바운딩박스가 소수점까지 동일**하다 —
같은 지오메트리이고 재질만 다르다. 그런데 `Leaves/` 쪽은 결함이 있다:
- `Leaves/cluster_2.usd` 의 `reflectionroughness_texture` 가 `./basecolor.jpg` 를
  가리키는데 **그 파일은 S3 에 없다**(있는 건 `basecolor.png`).
- 같은 파일에서 normal 슬롯에 `roughness.jpg` 가 물려 있다(슬롯 교차).

→ `Debris/` 만 쓴다. 조달 스크립트 docstring 에도 명기했다.

### 3-b. `Plant_Tropical/` 전량 부적합 — 종별 사유
| 에셋 | 부적합 사유 |
|---|---|
| Cuban_Royal_Palm · Fan_Palm · Golden_Malay_Palm · Hurricane_Palm · Travelers_Palm · Grass_Palm | 야자 — 한국 노지 월동 불가 |
| Windmill_Palm (당종려) | 제주·남해안 일부만. 도시 보행환경 일반성 없음 |
| Japanese_Fiber_Banana (파초) | 남부 일부 정원 한정, 도로/공원 표준 아님 |
| Buddha_Belly_Bamboo | 열대 대나무. 한국 대나무(왕대·조릿대)와 실루엣 다름 |
| Australian_Tree_Fern · Japanese_Painted_Fern | 목본 양치 — 한국 도시 조경 부재 |
| Agave · Dagger (유카) | 다육/사막계 |
| Honey_Myrtle · Japanese_Flame · Jungle_Flame · Crane_Lily | 아열대 화목 |

### 3-c. `Shrub/` 37종 한국 적합성 판정

**A급 — 한국 조경/자생 흔함 (권장)**
| 에셋 | 국명 | MB | 비고 |
|---|---|---|---|
| **Privet** | 쥐똥나무 | 19.6 | **생울타리 1위. `build_hedge` 직접 대체** ✅조달 |
| **Rhododendron** | 철쭉/진달래 | 7.2 | 공원·아파트 화단 최다. 가장 가벼움 ✅조달 |
| **Boxwood** | 회양목 | 24.2 | 연석·화단 경계 ✅보유 |
| **Juniper** | 향나무/눈향 | 29.7 | 상록 — C1 겨울 씬에 유일하게 유효 ✅조달 |
| **Burning_Bush** | 화살나무 | 18.7 | 자생. 가을 홍엽 → C2 낙엽 씬과 계절 정합 ✅조달 |
| **Forsythia** | 개나리 | 53.7 | 사면 녹화 최다. 3.5 m 로 큼 ✅조달(선택) |
| Meadowlark | 개나리 품종 | 10.3 | Forsythia 와 재질 공유(`Meadowlark_flowers.mdl`) |
| Yew | 주목 | 21.2 | 상록 정형수 |
| Holly | 호랑가시/사철나무류 | 47.8 | Privet 과 재질 공유 |
| Hydrangea | 수국 | 27.3 | 여름 화단 |
| Lilac | 라일락/수수꽃다리 | 10.9 | 자생종 있음 |
| Vibernum | 가막살나무·분꽃나무 | 34.7 | 자생 |
| Sweet_Mock_Orange | 고광나무 | 26.1 | 자생 |
| Goldflame_Spirea | 조팝나무류 | 7.3 | 도로 사면 다용 |
| Cedar_Shrub | 측백류 | 11.4 | 상록 생울타리 |
| Barberry | 매자나무 | **0.79** | 최경량. 붉은잎 품종 흔함 |
| Fountain_Grass_Short/Tall | 수크령 | 27.5/38.9 | **자생 억새류 — `build_hedge` 억새 밴드 대체 후보** |
| Grass_Short_A~C, Grass_Trimmed_A~C | 잔디 패치 | 0.06~2.46 | 범용. **매우 가벼움** |

**B급 — 조건부**
| 에셋 | 사유 |
|---|---|
| Magnolia | 목련은 한국에 흔하나 **교목**이다. 이 에셋은 관목형이라 용도 제한 |
| Fraser_Photina | 홍가시나무 — 남부 지방 한정 |
| Pampas_Grass | 팜파스그라스. 외래이나 최근 조경 유행. 억새 대용 가능 [추정] |
| Prairie_Dropseed · Switchgrass | 북미 초원종. 억새 실루엣 대용은 가능 [추정] |
| Daphne | 서향/백서향 — 남부 |
| Pearl_Bush | 가침박달 유사(Exochorda). 자생 근연종 있음 [추정] |
| Hibiscus | 무궁화(*H. syriacus*)면 A급이나 **열대 히비스커스일 가능성** — 조달 전 렌더 확인 필요 [추정] |
| Lupin | 루피너스 — 외래 화단초. 한국 도시 흔치 않음 |

**C급 — 부적합**
| 에셋 | 사유 |
|---|---|
| Century (Century Plant) | 용설란 — 사막 다육 |
| Thevetia | 노랑협죽도 — 열대 |
| Oleander | 협죽도 — 제주/남부 한정 |
| Acacia | 사바나 아카시아 계통(잎 재질 `acacialeaves_*`). 한국 "아카시아"(아까시나무)와 **다른 나무** |

### 3-d. `Trees/` 44종 — 향후 확장 후보 (미조달)
현행 3종(벚나무·소나무 2)은 유지. 한국 가로수 실적 기준 **추가 우선순위**:

| 순위 | 에셋 | 국명 | MB | 사유 |
|---|---|---|---|---|
| 1 | **Sycamore** | 버즘나무(플라타너스) | **7.8** | 한국 가로수 최다급인데 미보유. 게다가 최경량 |
| 2 | **Chinese_Juniper** | 향나무 | **3.7** | 관공서·학교 조경 최다. 초경량 |
| 3 | Kousa_Dogwood | 산딸나무 | 35.9 | 자생, 공원 다용 |
| 4 | Lombardy_Poplar | 양버들 | 55.5 | 하천변(scene03·12 배경) |
| 5 | Japanese_Maple(+`_Fall`) | 단풍나무 | 81.8/62.6 | `_Fall` 은 C2 낙엽 씬 계절 정합 |
| 6 | Gray_Birch(+`_fall`) | 자작나무류 | 33.8 | |
| 7 | Red_Oak / Shumard_Oak(+`_Fall`) | 참나무류 | 11.4/12.9 | 낙엽 에셋(oakfall)과 수종 정합 |
| 8 | Elm_Sapling | 느릅나무 | 14.8 | |

**S3 에 없는 한국 주요종**: 은행나무 · 느티나무 · 이팝나무 · 회화나무 ·
메타세쿼이아 (전수 확인). 기존 CREDITS 의 대조표와 일치.
`_Fall` 접미 수종 7쌍(Black_Oak · Gray_Birch · Honey_Locust · Japanese_Maple ·
Lombardy_Poplar · Red_Ash · Scarlet_Oak · Shumard_Oak)은 **가을 변형본**이라
C2 낙엽 씬 · 계절 대응쌍 실험에 바로 쓸 수 있다.

---

## 4. 조달 결과 + 네이티브 치수 실측표

`assets/download_vegetation.py --only leaf_litter,rocks` · `--only shrub` 실행.
치수는 `usd-core`(스크래치패드 venv, Isaac 미사용) 로 `UsdGeom.BBoxCache` 실측.
**전 에셋 `metersPerUnit = 0.01`** — USD reference 는 단위 변환을 하지 않으므로
`scene_common.add_vegetation` 처럼 **0.01 배 스케일이 필수**다. 안 걸면 100배로 들어온다.

| 파일 | X (m) | Y (m) | Z (m) | z최소 | z최대 | 삼각형 | MB |
|---|---|---|---|---|---|---|---|
| **Debris/fallcluster1.usd** | 0.419 | 0.395 | 0.042 | −0.003 | 0.039 | 9,175 | 0.51 |
| **Debris/fallcluster2.usd** | 0.241 | 0.266 | 0.042 | −0.002 | 0.039 | 2,980 | 0.18 |
| **Debris/maplefall1.usd** | 0.103 | 0.172 | 0.023 | 0.001 | 0.024 | 631 | 0.05 |
| **Debris/oakfall1.usd** | 0.080 | 0.175 | 0.023 | 0.000 | 0.023 | 496 | 0.04 |
| **Debris/oakfall2.usd** | 0.094 | 0.190 | 0.018 | −0.002 | 0.016 | 582 | 0.04 |
| Rocks/rock_small_01.usda | 0.314 | 0.302 | 0.253 | **−0.128** | 0.125 | 268 | 0.04 |
| Rocks/rock_small_15.usda | 0.228 | 0.224 | 0.173 | **−0.084** | 0.089 | 410 | 0.06 |
| Rocks/rock_small_08.usda | 0.223 | 0.197 | 0.162 | **−0.086** | 0.076 | 438 | 0.07 |
| Rocks/rock_small_10.usda | 0.162 | 0.151 | 0.116 | **−0.055** | 0.061 | 374 | 0.06 |
| Rocks/rock_small_09.usda | 0.128 | 0.113 | 0.067 | **−0.031** | 0.036 | 426 | 0.06 |
| Shrub/Juniper.usd | 0.455 | 0.451 | 0.898 | −0.013 | 0.885 | 199,580 | 29.73 |
| Shrub/Boxwood.usd | 1.009 | 1.012 | 0.741 | −0.019 | 0.722 | 177,721 | 24.21 |
| Shrub/Privet.usd | 1.704 | 1.638 | 1.113 | −0.067 | 1.046 | 147,380 | 19.60 |
| Shrub/Rhododendron.usd | 2.547 | 2.372 | 2.013 | **−0.416** | 1.596 | 54,704 | 7.15 |
| Shrub/Burning_Bush.usd | 2.642 | 2.601 | 1.604 | −0.193 | 1.412 | 140,570 | 18.71 |
| Shrub/Forsythia.usd | 3.539 | 3.650 | 2.317 | −0.007 | 2.310 | 403,841 | 53.71 |
| Trees/Japanese_Cherry.usd | 4.887 | 5.697 | 4.641 | 0.000 | 4.641 | 269,945 | 35.52 |
| Trees/White_Pine.usd | 2.000 | 2.123 | 2.350 | **−0.351** | 1.999 | 10,846 | 0.85 |
| Trees/Yellow_Pine.usd | 17.144 | 18.043 | 26.994 | 0.000 | 26.994 | 112,736 | 15.94 |

### 4-a. **z최소가 음수인 에셋은 원점이 지면이 아니다**
`Rocks/*` 는 원점이 **바위 중심**이라 그대로 놓으면 **절반이 묻힌다**.
`Rhododendron` 은 −0.416 m, `White_Pine` 은 −0.351 m 로 뿌리분이 원점 아래에 있다.
→ 배치 시 `z += -zmin * scale` 로 올리거나(바위), 의도적으로 묻는다(관목 뿌리분은
살짝 묻히는 게 오히려 자연스럽다). `scene_common.VEG_TREES` 의 `native_h` 값
(4.64 / 2.35 / 26.99)은 **Z 전체 높이**와 일치함을 재확인했다 — 기존 코드 정합.

### 4-b. 낙엽 피복 밀도 (산포 계산용 — 감독 요청 항목)
삼각형을 XY 평면에 투영해 256×256 격자로 래스터화한 실측.

| 에셋 | 바운딩박스 면적 | 박스 내 채움률 | **유효 피복** | **1 m² 완전피복 필요 수** |
|---|---|---|---|---|
| fallcluster1 | 0.1653 m² | 38.0 % | 0.0628 m² | **15.9개** |
| fallcluster2 | 0.0640 m² | 37.7 % | 0.0242 m² | **41.4개** |
| maplefall1 | 0.0177 m² | 29.0 % | 0.0051 m² | 194.8개 |
| oakfall1 | 0.0140 m² | 21.5 % | 0.0030 m² | 331.8개 |
| oakfall2 | 0.0179 m² | 21.1 % | 0.0038 m² | 264.1개 |

**폴리곤 예산**: fallcluster1 을 1 m² 완전피복(15.9개)하면 **146k 삼각형/m²**.
sceneC2 낙엽 밴드가 대략 6 m² 이므로 완전피복은 ~880k 삼각형.
현행 낙엽 타원체 900개(≈115k 삼각형)의 8배지만, 관목 하나(Forsythia 404k)보다
적으므로 **감당 가능**하다. 다만 아래 3층 전략을 권장한다.

### 4-c. 참조 무결성
받은 19개 USD 전부를 열어 `Sdf.AssetPath` → MDL → `texture_2d()` 3단을 재귀 확인:
**참조 113개 전부 해결, 미해결 0건.** `Rocks/*.usda` 의 `@OmniPBR.mdl@` 는
검색경로 MDL(Isaac 동봉)이라 조달 대상이 아니다.

`assets/vegetation/` 총 **337 MB** (Debris 65 · Rocks 1.9 · Shrub 165 · Trees 107).

---

## 5. 감독이 바로 쓸 배치 코드

> 아래는 **제안 스니펫**이다. `scene_common.py` 는 이번 담당 범위 밖이라
> 수정하지 않았다. 기존 `add_vegetation()` 이 단위 변환·T→R→S 순서를 이미
> 올바르게 처리하므로 그대로 재사용한다.

### 5-a. 낙엽 산포 — 3층 전략 (핵심)
현행 `build_leaf_scatter` 의 900개 납작 타원체를 아래로 대체한다.
**평판 `leafbed`(build_leaf_mound)는 남긴다** — 밑바탕(썩은 잎 층)으로는 여전히
옳고, 그 위에 낱장이 얹혀야 "장판"이 아니라 "퇴적"으로 읽힌다.

```python
# scene_common.py 에 추가할 상수 (실측치)
VEG_LEAF = [
    # (상대경로, 유효피복 m², 가중치)  — 유효피복은 asset_audit_v1.md §4-b 실측
    ("Debris/fallcluster1.usd", 0.0628, 5),   # 바탕 깔개
    ("Debris/fallcluster2.usd", 0.0242, 4),   # 성긴 산포
    ("Debris/maplefall1.usd",   0.0051, 2),   # 낱장(단풍)
    ("Debris/oakfall1.usd",     0.0030, 2),   # 낱장(참나무)
    ("Debris/oakfall2.usd",     0.0038, 2),   # 낱장(참나무)
]


def scatter_leaves(stage, prefix, x0, x1, y0, y1, surface_z_fn,
                   density=0.75, seed=2702, scale_jit=(0.85, 1.20),
                   tilt_deg=8.0, budget=None):
    """낙엽 3D 산포. density = 목표 피복률(1.0 = 완전피복, 겹침 없음 가정).

    surface_z_fn(x, y) -> 그 지점의 지형 상면 z. sceneC2 의 `surface_z` 를
    그대로 넘기면 된다(부유·매몰 없이 안착).

    권장 density:  0.35 = 흩뿌림 / 0.75 = 낙엽길 / 1.2 이상 = 매몰(계단코 은폐)
    budget 지정 시 그 개수를 넘지 않는다(폴리곤 상한).
    """
    import random as _random
    from pxr import UsdGeom
    rnd = _random.Random(int(seed))
    UsdGeom.Xform.Define(stage, prefix)
    area = abs(x1 - x0) * abs(y1 - y0)
    pool = [a for a in VEG_LEAF for _ in range(a[2])]
    # 가중 평균 유효피복 → 목표 개수
    mean_cov = sum(a[1] * a[2] for a in VEG_LEAF) / sum(a[2] for a in VEG_LEAF)
    n = int(round(area * density / mean_cov))
    if budget:
        n = min(n, int(budget))
    for i in range(n):
        rel, _, _ = pool[rnd.randrange(len(pool))]
        px = rnd.uniform(x0, x1)
        py = rnd.uniform(y0, y1)
        pz = surface_z_fn(px, py) + 0.002       # 2 mm 리프트(z-fighting 방지)
        s = rnd.uniform(*scale_jit)
        # add_vegetation 은 target_h/native_h 로 스케일한다. 낙엽은 높이가
        # 아니라 '크기 지터'가 필요하므로 둘 다 넘겨 비율만 s 가 되게 한다.
        sc.add_vegetation(stage, f"{prefix}/Leaf_{i}", rel, (px, py, pz),
                          yaw_deg=rnd.uniform(0, 360),
                          target_h=s, native_h=1.0)
    return n
```

**sceneC2 적용 예** (기존 `build_leaf_scatter` 호출 지점을 교체):

```python
ls = PARAMS["leaf_scatter"]
n = scatter_leaves(
    stage, f"{ROOT}/Leaves",
    x0=ls["x0"], x1=ls["x0"] + ls["x_pad"] + RUN,
    y0=-ls["y_wide"], y1=ls["y_wide"],
    surface_z_fn=surface_z,          # 기존 함수 그대로 재사용
    density=1.10,                    # 매몰 씬이므로 완전피복 초과
    seed=ls["seed"], budget=1200)
print(f"[C2] 낙엽 3D {n}개 (구: 납작 타원체 900개)")
```

> **기울기(tilt)**: `add_vegetation` 은 yaw 만 받는다. 낙엽이 계단코·경사에
> 얹히려면 rotX/rotY 지터가 있어야 자연스럽다. `add_vegetation` 에
> `rotXY=(a, b)` 인자를 추가하고 `AddRotateXYZOp` 으로 T→R(XYZ)→S 순서를
> 유지하는 게 최소 변경이다. 지금은 yaw 만으로도 평판보다 훨씬 낫다 [추정].

### 5-b. 잡석 (scene12 `build_rocks` 대체)
```python
VEG_ROCK = [   # (상대경로, 장변 m, z최소 m) — 원점이 바위 '중심'이라 z 보정 필수
    ("Rocks/rock_small_01.usda", 0.314, -0.128),
    ("Rocks/rock_small_15.usda", 0.228, -0.084),
    ("Rocks/rock_small_08.usda", 0.223, -0.086),
    ("Rocks/rock_small_10.usda", 0.162, -0.055),
    ("Rocks/rock_small_09.usda", 0.128, -0.031),
]

def place_rock(stage, path, rel, native_long, zmin, cx, cy, ground_z,
               target_long, yaw=0.0, embed=0.35):
    """target_long = 원하는 장변(m). embed = 지면에 묻히는 비율(0.35 권장)."""
    s = float(target_long) / float(native_long)
    z = ground_z + (-zmin) * s * (1.0 - embed)   # 중심 원점 보정 + 매입
    return sc.add_vegetation(stage, path, rel, (cx, cy, z), yaw_deg=yaw,
                             target_h=target_long, native_h=native_long)
```
scene12 는 0.30~1.10 m 를 요구하는데 에셋 최대가 0.31 m 다.
→ `target_long > 0.45 m` 는 **스케일 업 대신 2~3개 군집**으로 만드는 편이
질감 늘어짐을 피한다. 0.30 m 이하는 1:1 로 대체 가능.

### 5-c. 생울타리 (`build_hedge` 대체)
```python
def hedge_shrubs(stage, prefix, x0, y0, x1, y1, h, base_z=0.0, seed=None):
    """관목 열로 생울타리. Privet(1.70 m 폭)이 기본 — 한국 생울타리 1위 수종.
    스케일은 '폭' 기준으로 잡는다(높이로 잡으면 열 사이가 벌어진다)."""
    import random as _random
    rnd = _random.Random(seed if seed is not None
                         else (int(x0 * 100) * 73856093) ^ (int(y0 * 100) * 19349663))
    L = max(abs(x1 - x0), abs(y1 - y0))
    W = min(abs(x1 - x0), abs(y1 - y0))
    along_x = abs(x1 - x0) >= abs(y1 - y0)
    NATIVE_W, NATIVE_H = 1.704, 1.113          # Privet 실측
    s = max(float(h) / NATIVE_H, float(W) / NATIVE_W)
    pitch = NATIVE_W * s * 0.62                 # 38 % 겹침 → 틈 없음
    n = max(2, int(round(L / pitch)))
    t0 = (min(x0, x1) if along_x else min(y0, y1))
    u = (y0 + y1) / 2.0 if along_x else (x0 + x1) / 2.0
    for i in range(n):
        t = t0 + (i + 0.5) * (L / n)
        cx, cy = (t, u) if along_x else (u, t)
        sc.add_vegetation(stage, f"{prefix}/Shrub_{i}", "Shrub/Privet.usd",
                          (cx + rnd.uniform(-0.05, 0.05),
                           cy + rnd.uniform(-0.05, 0.05),
                           base_z - 0.05),          # 5 cm 매입 = 뿌리분 은폐
                          yaw_deg=rnd.uniform(0, 360),
                          target_h=float(h) * rnd.uniform(0.92, 1.08),
                          native_h=NATIVE_H)
    return n
```
**폴리곤 경고**: Privet 은 147k 삼각형이다. 10 m 생울타리(≈10개) = 1.5 M.
원경 생울타리는 기존 `build_hedge` 블롭을 유지하고, **로봇 근접 구간(≤6 m)만**
관목 에셋으로 바꾸는 하이브리드를 권한다.

### 5-d. `build_planter` 화단
`Boxwood`(1.01 m 폭, 0.74 m 높이)를 3×3 격자로 넣으면 3.0 m 화단이 채워진다.
`Rhododendron` 은 z최소 −0.416 m 라 `base_z` 그대로 놓으면 뿌리분이 화단 흙에
자연스럽게 묻힌다 — 별도 보정 불필요.

---

## 6. 이월·미해결

1. **`VEG_SHRUB` 가 정의만 되고 호출부가 없다.** Boxwood 를 받아만 놓고
   한 씬도 안 쓴다. §5-c/5-d 적용 시 함께 해소된다.
2. **`add_vegetation` 에 rotX/rotY 가 없다.** 낙엽·잡석이 경사면에 눕지 못한다.
3. **바위 크기 상한 0.31 m** — scene12 의 1.10 m 대석은 대체 불가(군집으로 우회).
4. **`sandstone` 역할이 어느 씬에서도 안 쓰인다**(refs=0). `sign_warn_fall` ·
   `sign_caution_step` · `sign_no_entry` 도 refs=0 — 생성해 놓고 미사용.
5. **`.gitignore` 주석 용량 표기**가 "~128MB" 인데 실제 337 MB.
   (수정 권한 밖이라 보고만 함.)
6. Plant_Tropical 은 부적합이지만 **Windmill_Palm 은 제주 씬을 만들 경우** 유일한
   현실적 후보다. 현 33씬에 제주 시나리오가 없어 이번엔 제외했다.
