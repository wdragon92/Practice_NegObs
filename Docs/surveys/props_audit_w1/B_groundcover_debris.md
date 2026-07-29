# B. 지피(잔디·흙·자갈)·낙엽·지면 텍스처 전수 감사

작성 2026-07-29 · NegObs 사실화 W1 병렬 편대 / B 담당
대상: `scene_common.TEX` 지면 역할 23종 · `VEG_DEBRIS` 5종 · 33씬 전체 · scene04·sceneC2 h0.3 렌더

> 근거 태그: [실측] 이 감사에서 픽셀·지오메트리를 직접 계산 / [법령] 국내 법정·표준시방
> [통계]·[논문] 공개 문헌 / [추정] 근거가 불충분한 판단. 태그 없는 주장은 쓰지 않았다.

---

## 0. 한 문단 결론

**"낙엽 장판"과 "잔디 사각 이음매"는 텍스처 품질 문제가 아니라 (a) 원본 텍스처의 물리
크기를 무시한 스케일 오류, (b) 재질 경계에 전이대가 0인 축정렬 직육면체 프림, (c) 지면
산포물의 부재 — 이 세 가지의 합이다.** 그리고 감사 도중 더 큰 것이 나왔다: `NEGOBS_LOOK_V1=1`
에서 **24개 씬 50개 식생 재질이 `leaf_ground`(= PolyHaven `forest_leaves_03`, 태그 `autumn`)
로 승격**된다. 즉 계절 규약이 금지한 **가을 낙엽 텍스처가 전 씬의 나무 수관·관목에 씌워져 있다**
(§8). 이건 룩 문제가 아니라 규약 위반이다.

---

## 1. 방법·재현

| 항목 | 도구 | 비고 |
|---|---|---|
| 텍스처 픽셀 | PIL + numpy (1024² LANCZOS 리샘플, sRGB→선형 IEC 61966-2-1) | GPU 미사용 |
| USD 지오메트리 | `usd-core 26.8` (스크래치패드 venv, Isaac 미사용) | `UsdGeom.Mesh` 전수 순회 + XY 투영 래스터화 |
| 래스터라이저 검증 | 단위정사각형 fill=1.0000, 64각형 fill=0.7840(이론 0.7854) | [실측] 오차 0.2% |
| 수렴 확인 | N=256/512/1024/2048 에서 fill 동일(±0.1%) | 격자 해상도 의존 없음 |
| 원본 물리 크기 | PolyHaven API `https://api.polyhaven.com/info/{slug}` · ambientCG API v2 | [실측] 2026-07-29 조회 |
| 렌더 판독 | `look_check/scene04/{v7_pt,r2_on}` · `look_check/sceneC2/{leaf3d,fix1}` h0.3 컷 | 1920×1080 |

렌더 실행·GPU·Isaac 은 전혀 돌리지 않았다. 기존 PNG 판독과 CPU 계산만 썼다.

---

## 2. 지면 텍스처 픽셀 실측표 [실측]

diffuse 맵 1024² 리샘플 기준. `alb` = 선형 휘도 평균(= 실효 알베도), `순백` = 휘도>0.8 픽셀 비율
(sRGB 표시값 / 선형 알베도 두 기준), `seam` = 랩어라운드 불연속 ÷ 내부 평균 기울기
(1.0 = 완전 이음매 없음, >1.3 = 육안 이음매), `반복` = 1/8 블록 최대편차 ÷ 전역 표준편차
(**타일 반복이 눈에 띄는 정도** — 1.0 이상이면 특징 블롭이 주기적으로 되풀이된다).

| 역할 | 해상도 | alb | 채도 | 순백(sRGB/선형) | seam x/y | macroCV16 | **반복** |
|---|---|---|---|---|---|---|---|
| **grass** (aerial_grass_rock) | 4096² | 0.127 | **0.693** | 0.02% / 0.00% | 0.94 / 1.01 | 0.069 | **1.25** |
| **dirt_park** (park_dirt) | 4096² | 0.142 | 0.503 | 0.00% / 0.00% | 1.00 / 1.07 | 0.040 | 0.48 |
| **gravel** (gravel_floor) | 4096² | 0.277 | 0.390 | 2.51% / 0.06% | 1.03 / 0.97 | **0.011** | **0.04** |
| **leaf_ground** (forest_leaves_03) | 4096² | **0.050** | 0.576 | 0.00% / 0.00% | 1.04 / 1.06 | 0.080 | 0.28 |
| soil brown_mud_03 *(미사용)* | 4096² | 0.076 | 0.295 | 0.00% / 0.00% | 1.07 / 0.94 | 0.128 | 1.07 |
| soil brown_mud_dry *(미사용)* | 4096² | 0.132 | 0.481 | 0.24% / 0.02% | 1.11 / 1.16 | 0.063 | 0.33 |
| paving_interlock (PavingStones131) | 2048² | 0.272 | 0.026 | 0.05% / 0.00% | **1.75 / 1.75** | 0.018 | 0.24 |
| asphalt (asphalt_02) | 4096² | 0.110 | 0.071 | 0.01% / 0.00% | 0.95 / 1.10 | 0.038 | 0.29 |
| stone_flag | 4096² | 0.196 | 0.073 | 0.01% / 0.00% | 1.04 / 1.01 | 0.018 | 0.19 |
| concrete_floor | 4096² | 0.118 | 0.284 | 0.00% / 0.00% | 0.97 / 0.84 | 0.010 | 0.07 |
| snow (snow_01) | 4096² | 0.477 | 0.021 | 2.87% / 0.00% | 1.16 / 1.10 | 0.041 | 1.24 |
| plaza_light (Tiles038) | 4096×2048 | 0.466 | 0.027 | **4.73%** / 0.01% | **2.19** / 1.08 | 0.023 | 0.57 |
| granite_dark | 4096² | 0.077 | 0.027 | 0.00% / 0.00% | **1.53** / 1.09 | 0.015 | 0.31 |
| wood_dark | 4096² | 0.062 | 0.265 | 0.00% / 0.00% | **1.60** / 1.15 | 0.040 | 0.44 |
| sandstone | 4096² | 0.106 | 0.258 | 0.00% / 0.00% | 0.99 / **2.05** | 0.052 | 1.00 |
| marble_light | 4096² | 0.350 | 0.316 | 0.00% / 0.00% | 1.13 / 1.41 | 0.033 | **1.50** |
| leafUSD BaseColor (2048²) | 2048² | 0.065 | 0.519 | 0.00% / 0.00% | 0.22 / 0.31 | 0.089 | 1.73 |

판정:
- **순백(>0.8) 대면적 규약 위반은 지피 계열에 없다.** 선형 알베도 기준 최대가 gravel 0.06%,
  snow 0.00% 다. sRGB 표시값 2.5~4.7% 는 톤매핑 상단이지 알베도 위반이 아니다. **[실측]**
- **지피 4종은 전부 랩어라운드 이음매가 없다**(seam 0.94~1.07). 즉 scene04 의 "사각 이음매"는
  **텍스처 타일링이 아니다**(§4). 이음매가 있는 건 `plaza_light`(2.19)·`wood_dark`(1.60)·
  `granite_dark`(1.53)·`sandstone` y축(2.05)·`paving_interlock`(1.75) 쪽이다 — 별도 항목.
- **grass 는 채도 0.693 으로 전 지면 재질 중 1위**다. 씬은 여기에 다시 `grass_tint`
  (0.55,0.68,0.42) 를 곱한다. 과채도 지적의 물리적 출처가 여기다.
- **gravel 은 macroCV16 0.011 · 반복지수 0.04 로 사실상 저주파 성분이 0** 이다. 즉 어떤
  스케일로 깔아도 **완전 균질한 모래판**으로 읽힌다. 실제 마사토 포장은 다짐 자국·물길·
  바퀴 자국이 있는데 그 대역이 통째로 비어 있다.
- **grass·snow·marble·brown_mud_03 은 반복지수 ≥1.0** — 특징 블롭이 타일 주기로 되풀이된다.
  grass 는 4 m 주기로 회색 바위 패치가 반복된다(§3, §4 렌더에서 확인).

---

## 3. 물리 스케일 감사 — **원본 실측 크기 vs 사용 scale_m** [실측]

`make_pbr` 은 `texture_scale = 1/scale_m` 을 넣으므로 **`scale_m` = 타일 한 변의 미터**다
(`scene_common.py:1058`). 원본 제작자가 스캔한 실제 크기는 PolyHaven API 로 직접 조회했다.

| 역할 | 원본 슬러그 | **원본 실측 크기** | 씬에서 쓰는 scale_m | **비율(사용/원본)** |
|---|---|---|---|---|
| grass | `aerial_grass_rock` | **15.0 × 15.0 m** | 4.0 (27씬) · 2.6 (s10) | **0.27 / 0.17** |
| dirt_park | `park_dirt` | 3.0 × 3.0 m | 3.0 (s04·D2) · 2.0 (C1) · 1.1 (s10) · 1.0 (s03·C2) | 1.00 / 0.67 / 0.37 / **0.33** |
| gravel | `gravel_floor` | 2.25 × 2.25 m | 0.9 (D2) · 0.6 (s03·s12·N2) · 0.5 (s04·D4) · 0.35 (s07) | 0.40 / 0.27 / 0.22 / **0.16** |
| leaf_ground | `forest_leaves_03` | 2.30 × 2.30 m | 2.0 (s07) · 1.05 (s10) · 0.9 (C2) · 0.8 (D3) | 0.87 / 0.46 / **0.39 / 0.35** |
| asphalt | `asphalt_02` | 3.0 × 3.0 m | 승격 기본값 1.2 (`spec.get("tex_scale",1.2)`) | **0.40** |
| snow | `snow_01` | 2.0 × 2.0 m | 승격 기본값 1.2 | **0.60** |
| stone_flag | `stone_tiles_02` | 2.0 × 2.0 m | 0.9 (C4) · 1.2 (N3) | 0.45 / 0.60 |
| concrete_floor | `brushed_concrete_03` | 2.0 × 2.0 m | 0.8 ~ 1.5 | 0.40 ~ 0.75 |
| paving_interlock | `PavingStones131`(ambientCG) | **API 가 0 × 0 반환(치수 미기재)** | 1.0 ~ 1.5 | 검증 불가 |

출처: `https://api.polyhaven.com/info/aerial_grass_rock` 외 (2026-07-29 조회) ·
`https://ambientcg.com/api/v2/full_json?id=PavingStones131`

### 3-a. 판정 — **자연 지피는 전부 원본의 1/3 ~ 1/6 로 축소돼 있다**

**`aerial_grass_rock` 은 잔디 텍스처가 아니다.** PolyHaven 이 붙인 카테고리는
`terrain / rock / outdoor / natural / **aerial**`, 태그는 `moss / grass / **cliff** / **cave** /
**rock face**`, 작가는 Rob Tuytel. **15 m 상공에서 찍은 이끼 낀 암반 항공 스캔**이다. **[실측]**
- 이걸 4 m 타일로 쓰면 원본의 모든 특징이 **3.75배 축소**된다. 원본 2 m 급 바위 노두가
  화면에서 0.53 m 돌덩이가 되고, 이게 `반복지수 1.25` 로 4 m 주기로 되풀이된다.
- 원본 해상도 4096 px / 15 m = **273 px/m** 이다. 들잔디(Zoysia japonica) 잎 나비는
  **4~7 mm**([통계] 산림청 『관상산림식물류』) 이므로 원본에서 **1.1~1.9 px** — 즉
  **잎 자체가 원본에 기록돼 있지 않다.** 어떤 스케일로 깔아도 잔디 잎은 나올 수 없다.
- h0.3·D=0.6 m 근경에서 화면 배율은 2771 px/m 이라 **원본을 10.2배 확대**해 보게 된다.
  근경 지면이 화면의 55~75% 인 판정 시점에서 최악의 조합이다.
- 이 한 텍스처를 **28개 씬**이 같은 scale_m 4.0 · 같은 `grass_tint` (0.55,0.68,0.42) 로 쓴다.
  데이터셋 전체의 "잔디"가 물리적으로 동일한 이끼 암반 한 장이다.

**`gravel` 은 마사토가 아니다.** 원본 2.25 m 에서 자갈알이 화면상 ~55 mm 이고,
scene04 의 0.5 m 배율에서 **12.2 mm**, scene07 의 0.35 m 에서 8.6 mm 가 된다. 국토교통부
『조경공사 표준시방서』(2016) 흙포장 항은 마사토를 **KS A 5101-1 눈 크기 4.75 mm 체를 통과**
하는 입도로 규정한다 [법령]. 즉 현재 값은 마사토 규격 대비 **1.8~2.6배 과대**다. 반대로
규격에 맞추려면 scale_m ≈ 0.2 가 필요한데, 그러면 4 m 시야에 타일이 20번 들어가 반복이 드러난다.
**해법은 배율 조정이 아니라 텍스처 교체**다(§10).

**`dirt_park` 은 scene04·sceneD2 에서만 물리적으로 옳다**(3.0 = 원본 3.0). scene03·sceneC2 는
1/3 로 축소해 쓴다. 같은 흙 알갱이가 씬마다 3배 다른 크기로 나오는 것은 로봇 시점에서
**스케일 단서 자체를 오염**시킨다 — 이 프로젝트가 학습시키려는 게 낙차 크기 추정이라 치명적이다.

**`leaf_ground` 은 sceneC2 에서 2.56배 축소**(0.9 / 2.3)돼 있다. 이것이 §5·§7 의 크기 불일치
직접 원인이다.

---

## 4. "잔디 사각 이음매" (scene04) — 실증과 원인

### 4-a. 실증 [실측]

`look_check/scene04/v7_pt/pt_noon_preset_h0.3_d5.png` (LOOK_V1 OFF) 과
`look_check/scene04/r2_on/pt_noon_preset_h0.3_d5.png` (LOOK_V1 ON, 07-28 22:46) 둘 다에서
화면 y≈470~500 에 **완전 직선 2개가 직각 코너를 이루며 만난다**.

- 경계 양측 재질 색차: 흙쪽 `L*=64.5 a*=+2.4 b*=+32.2` / 잔디쪽 `L*=53.3 a*=−8.6 b*=+42.8`
  → **ΔE76 = 18.9** (ΔE>5 면 명백히 다른 색으로 읽힌다).
- 경계 수직 단면에서 최대 휘도 기울기 **15.1~16.4 L*/px** — 전이대가 사실상 **0 px** 다.
- LOOK_V1 을 켠 r2_on 에서도 **경계는 조금도 부드러워지지 않는다**(같은 위치·같은 직선).

### 4-b. 원인 — UV도 스케일도 아니다 [실측 + 코드 추적]

1. **텍스처 타일링이 아니다.** grass·dirt_park 의 랩어라운드 이음매 지표는 0.94~1.07 로
   완전 무이음이다(§2). 게다가 `make_pbr` 은 `project_uvw=True, world_or_object=True` 로
   **월드 스페이스 투영**을 쓴다(`scene_common.py:1054-1058`) — 같은 재질·같은 scale_m 이면
   프림이 몇 개로 쪼개져 있어도 텍스처가 월드 좌표로 연속한다. **프림별 UV 이음매는 원리적으로 없다.**
2. **원인은 축정렬 직육면체 재질 패치다.**
   - `scene04_parktrail.py:739-748` — 계단 전후 접속부를 `add_box(..., (L, 2*hy, th), M["dirt_path"])`
     로 놓는다. `connect=dict(length=3.0, half_y=3.0)` 이므로 **정확히 3.0 m × 6.0 m 직사각형**이다.
     이게 h0.3_d5 화면의 그 사각형이다.
   - 바닥은 `_flat(f"{ROOT}/UpperFlat", PARAMS["upper"], M["grass"])`, `upper=dict(x0=-35, x1=0,
     y0=-25, y1=25)` — 70 × 50 m 사각 슬래브.
   - 길은 `add_box(..., (L, ws, th), M["dirt_path"])` 회전 세그(폭 1.8 m ±10%, `proud=0.001`).
   - **세 층 전부 하드 에지 박스이고, 재질 사이에 블렌딩·데칼·페더링·정점컬러 전이가 하나도 없다.**
3. **부차 원인**: 접속부 박스는 `thick=0.06`(길) / `proud=0.001` 로 지면 위에 얹혀 있어
   근경에서 **측면 절단면**(수직 띠)이 보인다. h0.3_d2 좌우 가장자리 y≈460~520 에서 확인된다.

### 4-c. 해소 방향 (구현 없음, 근거만)

- **경계 자체를 없앨 수는 없다**(재질이 실제로 다르다). 실물 공원은 경계에 ① 답압으로 잔디가
  죽어가는 폭 10~30 cm 의 전이대, ② 노면에서 잔디로 튄 흙, ③ 잔디가 노면을 침범한 불규칙 톱니,
  ④ 노면 가장자리 자갈 노출 — 이 4개가 반드시 있다 [추정 — 국내 실측 문헌 미확인].
- 코드적으로 가장 싼 해법 순서: **(1) 경계선에 3D 산포물(§6 `scatter_debris`)을 edge_bias 로 깔아
  선을 물리적으로 부수기 → (2) 경계 프림을 직사각형에서 폴리라인 오프셋(사행)으로 → (3) MDL 에
  경계 노이즈 마스크(NegObsGround 에 이미 `patch_mix`·`negobs_noise` 인프라가 있다)**.
  (1) 은 씬 파일 3~5줄, (3) 은 MDL 입력 1개 추가로 끝난다.

---

## 5. "낙엽 장판" (sceneC2) — 실증과 원인

### 5-a. 실증 [실측]

`look_check/sceneC2/fix1/pt_noon_preset_h0.3_d5.png` (07-29 00:48, 최신):

- 화면 y=469 에서 **한 행 만에 선형 휘도 +29.0%**, y=458 에서 −17.1% — 낙엽 마운드
  슬래브의 **절단면(수직 측면)이 프레임 전폭에 걸친 수평 직선 띠**로 보인다.
  `build_leaf_mound` 가 `build_slope(...)` 로 만든 두께 있는 판 3매 + `_oriented_box`
  드리프트 2매의 옆면이다(`sceneC2_leaf_stairs.py:486-502`). **이게 "장판"의 문자 그대로의 증거**다.
- 근경 지면은 `leaf_ground` 가 아니라 **`dirt_park`(베이지 모래 + 형광 녹/황 부스러기)** 다.
  하단 1/3 평균 sRGB (0.668, 0.597, 0.467). 3D 낙엽은 그 위에 **군집으로 뭉쳐** 있고 군집
  사이는 맨 모래다 — `fallcluster1` 이 0.42 m 덩어리 하나여서 생기는 패턴이다.
- **3D 낙엽 색상 표준편차 3.4°** (평균 39.9°, 5~95%tile 35.9~45.8°). 5종 USD 가 전부
  `Debris/materials/fallleaves.mdl` 단일 재질 + 단일 2048² BaseColor 를 공유하고,
  `scatter_debris` 는 인스턴스별 틴트를 전혀 주지 않는다(`scene_common.py:1869-1879`).
  **낙엽 수천 장이 색이 전부 같다.**

### 5-b. `dirt_park` 이 근경을 덮고 있는 것 자체가 문제

PolyHaven `park_dirt` 태그는 `sand / park / dirt / leaves / twigs / debris / **seaside** / ground`.
1 m 크롭을 열어 보면 **해변 모래 위에 선명한 초록·노랑·주황 잎 조각**이 흩어져 있다(§2 크롭).
scene04 h0.3_d2 에서 이게 화면 하단 60% 를 채우며 **오공 보드/테라조 같은 색종이 반점**으로 읽힌다.
가을 낙엽 씬(C2)에 **초록 생잎**이 섞여 있는 것은 계절 일관성도 깬다. **[실측]**

---

## 6. `VEG_DEBRIS` 5종 재실측 [실측]

`usd-core` 로 5개 USD 를 열어 전 메시의 삼각형을 세고, 로컬→월드 변환 후 XY 평면에
투영해 불리언 래스터화(N=1024, 256~2048 수렴 확인)했다.

| 에셋 | 바운딩박스 | 삼각형 | 박스 채움률 | **유효피복(본 감사)** | 현행 코드(수정 반영 후) | `asset_audit_v1` |
|---|---|---|---|---|---|---|
| `Debris/fallcluster1.usd` | 0.419 × 0.395 m | **9,175** | 35.3% | **0.0584 m²** | 0.0628 | 0.0628 |
| `Debris/fallcluster2.usd` | 0.241 × 0.266 m | **2,980** | 37.3% | **0.0239 m²** | 0.0242 | 0.0242 |
| `Debris/maplefall1.usd` | 0.103 × 0.172 m | **631** | 45.6% | **0.0081 m²** | 0.0051 | 0.0051 |
| `Debris/oakfall1.usd` | 0.080 × 0.175 m | **496** | 34.6% | **0.0048 m²** | 0.0030 | 0.0030 |
| `Debris/oakfall2.usd` | 0.094 × 0.190 m | **582** | 30.1% | **0.0054 m²** | **0.0038, 582** ← 수정 반영됨 | **0.0038** |

### 6-a. oakfall2 대조 결과 — **타 에이전트 수정 (0.0038, 582) 중 삼각형은 맞고 피복은 여전히 부족하다**

작업 트리 확인 결과 `scene_common.py:1772` 는 이미 `("Debris/oakfall2.usd", 0.0038, 582)` 로
갱신돼 있다(구값 0.0030, 520). 본 감사는 이 값과 독립 대조했다.

- **삼각형 582 = 완전 일치.** 구값 520 이 오기였다는 판정은 확정이다. **[실측]**
- **유효피복은 0.0038 이 아니라 0.0054 다**(+42%). `asset_audit_v1.md` 의 0.0038 도 본 감사와
  다르다. 나머지 4행도 낱장 계열(maplefall1 +59%, oakfall1 +60%)에서 계통적으로 어긋난다.
- 본 감사 쪽이 옳다고 보는 근거: ① 래스터라이저를 해석해 검증(단위정사각 1.0000 / 원 0.7840 vs
  이론 0.7854), ② N=256~2048 에서 결과 불변, ③ 실루엣 PNG 를 직접 육안 확인(단풍잎·참나무잎
  형상이 정확히 나옴). 감사표 쪽 계산 코드는 저장소에 남아 있지 않아 원인 규명은 불가.
- **실무 영향은 작다**: 5종 균등 풀 평균 유효피복이 표 0.01978 vs 재실측 0.02012 로 **+1.7%**
  차이뿐이다(낱장의 과소평가와 클러스터의 과대평가가 상쇄). 다만 **낱장만 쓰는 풀**을
  구성하면 개수가 최대 60% 과대 산출된다.

### 6-b. sceneC2 낙엽 예산 재계산 [실측]

`sceneC2` 는 `fallcluster` 2종만 쓰고 영역은 x∈[−4.20, 6.26] × y∈[−2.20, 2.20] = **46.02 m²**.

| 기준 | mean_cov | 필요 개수 | max_count 900 적용 | 실제 피복 | 삼각형 |
|---|---|---|---|---|---|
| 현행 표 | 0.04350 | 845 | 845 | 0.550 | **~5.14 M** |
| 본 감사 재실측 | 0.04115 | 893 | 893 | 0.550 | **~5.43 M** |

레드팀 R7 이 지적한 5.23 M 과 정합한다. **상한 900 에 이미 붙어 있으므로 피복을 조금만 더
올리면 조용히 잘린다**(`scatter_debris` 는 경고를 찍지만 렌더는 그대로 나간다).

### 6-c. 낙엽 에셋 자체의 함정 3건 [실측]

1. **`fallleaves.mdl` 은 `enable_opacity: false` 다.** 이건 이 에셋에 한해 **올바르다** —
   BaseColor PNG 의 알파는 전 픽셀 1.0 이고(2048² 전수 확인), 잎 윤곽이 지오메트리로 잘려 있다
   (실루엣 채움률 30~46%). 컷아웃 쿼드였다면 이게 "장판"의 진짜 원인이었겠지만 **아니다.**
2. **5종이 재질 1개를 공유**한다 → §5-a 의 색상 sd 3.4°.
3. **인스턴싱이 여전히 무효**일 가능성. `scatter_debris` 는 `{prefix}/Deb_{i}/Asset` 에
   `SetInstanceable(True)` 를 건다(`scene_common.py:1877`) — 레드팀 R6 이 지적한 위치 수정이
   이미 반영돼 있다. **다만 이 환경에 Isaac 이 없어 런타임 `IsInstance()` 확인은 못 했다.**

---

## 7. `leaf_ground` 텍스처 ↔ 3D 낙엽 톤 일치 [실측]

재질 수준(조명 무관, diffuse 앨비도 공간):

| 대상 | 선형 알베도 | L* | a* | b* | 채도 |
|---|---|---|---|---|---|
| `leaf_ground` 원본 | 0.0503 | 23.3 | +3.4 | +15.7 | 0.576 |
| `leaf_ground` × sceneC2 `leaf_tex_tint`(0.95,0.72,0.48) | **0.0320** | 18.2 | +9.7 | +18.8 | **0.786** |
| `fallleaves_1_BaseColor` 잎 픽셀(상위 35% 휘도) | **0.0804** | 33.8 | +9.2 | +20.5 | 0.524 |

- **틴트 적용 후 ΔE76 = 15.7, 알베도 비 2.51배.** 3D 낙엽이 침대보다 2.5배 밝다.
- **틴트가 상황을 악화시킨다**: 원본끼리는 ΔE76 13.0 / 알베도 비 1.60 인데, `leaf_tex_tint`
  를 곱하면 15.7 / 2.51 로 벌어진다. 이 틴트는 "오텀 보정" 의도지만 **어둡고 과채도(0.786)로 밀어
  3D 낙엽에서 더 멀어진다.**
- **크기도 어긋난다**: `forest_leaves_03` 을 0.9 m(원본 2.3 m)로 쓰므로 침대 낙엽이 2.56배
  축소돼 화면상 3~8 cm 인데, 3D 참나무잎은 **19.0 cm**(oakfall2 실측)다. **2.5~5배 크기 단절**.
- 렌더에서의 확인(`sceneC2/leaf3d` h0.3_d2): 침대 텍스처 면 L*=39.5 / 양광 3D 낙엽 L*=59.1,
  **ΔE76 = 27.0**. 두 층이 다른 계절·다른 수종으로 보인다.

**최소 수정 3줄**: `leaf_ground` scale_m 0.9 → **2.3**(원본 크기), `leaf_tex_tint` 제거(1,1,1)
또는 밝기 보정형으로 교체, `leaf_rough` 0.90 유지. 그러면 ΔE76 15.7 → 13.0, 알베도 비 2.51 → 1.60,
크기 단절 2.56배 → 1.0배가 된다. (완전 일치를 원하면 §10 의 대체 텍스처.)

---

## 8. **치명 — LOOK_V1 승격이 24개 씬 식생에 가을 낙엽 텍스처를 씌운다** [실측]

`LOOK_CLASS["veg"]` 는 `tex="grass", tex_alts=("grass","leaf_ground"), max_gain=7.0` 이고
주석은 *"낙엽(갈색 0.042)만으로는 잔디(초록)에 못 씌운다 — 라이브러리의 grass 를 1순위로"*
라고 적혀 있다(`scene_common.py:277-281`). **실제 동작은 정반대다.**

`_promote_const_to_texture` 의 채택 조건은 `max(ratio) ≤ max_gain` **그리고**
`spread = max(ratio)/min(ratio) ≤ 4.0` 다(`scene_common.py:576-579`).

- `grass`(aerial_grass_rock) 선형 평균 RGB = **(0.1688, 0.1210, 0.0240)** — **적/청 비 7.03**.
  청 채널이 극단적으로 비어 있다. **[실측]**
- 초록 수관 상수색(예 `canopy_a = (0.025, 0.045, 0.015)`)을 넣으면
  `ratio = (0.15, 0.37, 0.62)`, `spread = 4.22 > 4.0` → **grass 탈락**.
- `leaf_ground` 선형 평균 = (0.0614, 0.0386, 0.0150), 적/청 비 4.09 →
  `ratio = (0.41, 1.17, 1.00)`, `spread = 2.86` → **leaf_ground 채택**.

전 33씬 식생 상수색을 전수 시뮬레이션한 결과:

| 승격 결과 | 건수 | 내용 |
|---|---|---|
| **`leaf_ground`(가을 낙엽)** | **50건 / 24씬** | 모든 씬의 `canopy_a`·`canopy_b`, scene04·07·10 `shrub`, C4 `shrub_color` |
| `grass` | 3건 | scene09 `reed_color`, sceneC2 `canopy_a/b`(가을 갈색이라 통과) |
| 승격 실패(상수 MDL) | 43건 | `grass_tint`·`hedge_tint` 등 — 이건 텍스처 재질이라 승격 대상이 아님 |

승격 시 scale_m 은 `spec.get("tex_scale", 1.2)` = **1.2 m** 이므로, 원본 2.3 m 낙엽이
**52% 크기**로 나무 수관 위에 붙는다.

**결과**: `look_check/scene04/r2_on/pt_noon_preset_h0.3_d5.png`(LOOK_V1 ON)에서 관목 블롭과
수관이 v7_pt(OFF)의 평탄한 초록에서 **낙엽 더미 무늬**로 바뀐 것이 육안으로 확인된다.

**규약 관점**: 확정 규약은 "벚꽃·단풍 등 계절/이벤트 특정 요소 금지 — 수종명이 아니라 잎 텍스처
픽셀을 직접 열어 판정" 이다. `forest_leaves_03` 의 PolyHaven 태그는 `leaves / **autumn** / dry /
forest / ground` 이고 픽셀은 갈적 낙엽이다(선형 알베도 0.050, 색상 34.5°). **여름·상록으로 읽혀야
할 24개 씬의 수관이 가을 낙엽 픽셀로 칠해져 있다 = 규약 위반.**

**수정 후보(택1, 전부 1~2줄)**
1. `LOOK_CLASS["veg"]["tex_alts"]` 에서 `leaf_ground` 제거 → 승격 실패 시 상수 MDL 로 폴백.
   (가장 안전. 다만 flat_gnd 개선을 잃는다.)
2. `grass` 를 청 채널이 살아 있는 실물 잔디 텍스처로 교체(§10) → spread 가 4.0 아래로 내려가
   의도대로 grass 가 채택된다. **근본 해결이며 §3-a 도 동시에 해결한다.**
3. `spread` 상한을 veg 클래스에서만 5.0 으로 올린다. (증상만 가림 — 비권장.)

---

## 9. 부수 발견 — 만개 철쭉이 가을 씬에 서 있다 [실측]

sceneC2(낙엽 계단)의 h0.3 컷에 **분홍 만개 관목 2주**가 프레임 상단을 차지한다.
규약대로 수종명이 아니라 **텍스처 픽셀을 열어** 판정했다:

| Shrub 텍스처 | 평균 RGB | **분홍/마젠타 픽셀 비율** |
|---|---|---|
| `rhododendron_basecolor.png` | (0.657, 0.423, 0.623) | **76.7%** |
| `burningbush_leaf_basecolor.png` | (0.654, 0.462, 0.430) | 30.2% |
| `forsythiaflower_basecolor.png` | (0.795, 0.706, 0.213) | 0.0% |
| `hollyprivet_basecolor.png` | (0.222, 0.344, 0.100) | 0.0% |

`VEG_SHRUBS` 의 `Shrub/Rhododendron.usd` 는 **꽃이 만개한 상태로 스캔된 에셋**이다(잎 텍스처
픽셀의 76.7%가 마젠타). 개화기는 봄이므로 낙엽 씬과 **계절이 정면 충돌**한다.
`Burning_Bush`(화살나무)도 30.2%가 적색 — 이쪽은 가을 단풍이라 C2 에는 맞지만 **여름 씬에는
금지 대상**이다. 관목 담당 에이전트로 이관 권고. **[실측]**

---

## 10. 대안 조달 — 후보 목록

### 10-a. NVIDIA Omniverse S3 (`Assets/Vegetation/`) 전수 열거 [실측 · 2026-07-29 ListBucket]

`https://omniverse-content-production.s3.us-west-2.amazonaws.com/?list-type=2&prefix=Assets/Vegetation/`

| 폴더 | 실제 파일 | 보유 | 비고 |
|---|---|---|---|
| `Debris/` | **USD 5개가 전부** (fallcluster1/2, maplefall1, oakfall1/2) | 5/5 | **더 받을 낙엽이 없다** |
| `Leaves/` | cluster_1/2, maple, oak_1/2 (5개) + `material.mdl` + basecolor.png/normal.{jpg,png}/roughness.{jpg,png} | 0/5 | Debris 와 **동일 지오메트리, 재질만 다름**. `cluster_2.usd` 가 참조하는 `basecolor.jpg` 는 버킷에 없음(있는 건 .png) → 미조달 판정은 타당. 단 **`Leaves/basecolor.png` 는 Debris 와 다른 톤일 수 있어 §7 톤 매칭용 후보로 남는다**(미검증) |
| `Rocks/` | `rock_small_01` ~ `rock_small_15` (**15개**) | **5/15** | 10개 미조달. 자갈·잡석 다양성 확보처 |
| `Shrub/` | 37 USD | 6 | — |
| `Trees/` | 44 USD | 3 | — |
| `Plant_Tropical/` | 17 USD | 0 | 한국 부적합, 조달 금지 유지 |
| **`Grass/`** | **존재하지 않음** | — | **S3 에 3D 잔디는 없다.** 잔디는 텍스처+카드로만 가능 |

라이선스: NVIDIA 에셋은 CC0 아님 — 원본 재배포 금지, 렌더 공개는 가능(`Docs/CREDITS.md`).

### 10-b. ambientCG (CC0) — 잔디·낙엽

**잔디 (`type=Material&category=Grass`, n=8)** [실측 · API v2]

| ID | 실측 타일 | 태그 | 적합성 |
|---|---|---|---|
| **`Grass001`** | **1.40 × 1.40 m** | dark, dense, fresh, garden, **lawn**, natural, **park**, short, soft | ★ 공원 잔디 1순위 |
| **`Grass004`** | **1.40 × 1.40 m** | dense, garden, green, **lawn**, lush, natural, **park**, short, suburban | ★ 1순위 대안 |
| `Grass002` / `Grass003` | 1.40 × 1.40 m | grass, green, ground | 예비 |
| `Grass007` | 미기재 | grass, lawn, **moss, weeds** | 잡초 섞인 관리 소홀 잔디 — verge 용 |
| `Grass005/006/008` | 미기재 | grass, lawn | 예비 |

1.4 m 타일 4K 면 **2926 px/m** — 들잔디 잎 나비 4~7 mm 가 **12~20 px** 로 실제 해상된다.
현행 aerial_grass_rock 의 273 px/m 대비 **10.7배**. 청 채널도 정상이라 §8 의 spread 문제도 해소된다.

**낙엽 아틀라스 (`type=Atlas`, n=60 중 잎 계열 39)** [실측]
- `LeafSet001`~`LeafSet030` (30종) + `Foliage001`~`Foliage008` (8종) + `PineNeedles001`.
- **가을 태그 보유**: `LeafSet006, 007, 008, 011, 012, 015, 021, 027, 028, 030` (10종).
  이 중 `LeafSet030`(autumn/beige/brown/dried), `LeafSet012`(autumn/brown/fall),
  `LeafSet011`(autumn/brown/fall) 이 §5-a 의 색상 sd 3.4° 를 깨는 **다색 낙엽 소스**로 1순위.
- 용도: ① 3D 낙엽 인스턴스별 재질 변주(2~4종 추가) ② 잔디 사이 잡초·잡엽 카드
  ③ 경계 전이대용 데칼.
- 주의: `LeafSet014`(spring), `LeafSet016`(oak, spring), 녹색 계열은 여름 씬 전용.
  **씬별 계절 태그를 지켜 배분해야 §8 을 되풀이하지 않는다.**

### 10-c. PolyHaven (CC0) — 지피·낙엽 대체 후보 [실측 · API `?t=textures`]

| 후보 슬러그 | 실측 크기 | 태그 | 대체 대상 |
|---|---|---|---|
| **`sparse_grass`** | 2.0 m | grass, sparse, roots, vegetation, soil | grass(성긴 잔디·버지) |
| **`withered_grass`** | 2.0 m | grass, dead grass, dry, discolored | 겨울·건조기 잔디(D3 `dry_grass_tint` 대체) |
| `leafy_grass` | 2.0 m | grass, green, foliage, leaves, twigs | grass(수풀형) |
| `grass_path_2` / `grass_path_3` | 1.0 m | grass, pathway, path, stones, sidewalk | **잔디↔노면 전이대 전용** (§4-c 정확히 이 용도) |
| `grassy_cobblestone` | 2.0 m | ground, dirt, grass, trampled, pathway | 답압 전이대 |
| **`forest_ground_05`** | 2.0 m | dirt, soil, compact soil, scattered rocks, **scattered leaves** | dirt_park 대체(공원 다짐 흙) |
| **`forest_ground_06`** | 2.11 m | dirt, soil, compact soil, loose earth, scattered leaves | dirt_park 대체 |
| `dirt_floor` | 2.07 m | dirt, ground, brown, uneven, mud, debris | dirt_park 대체 |
| `baseball_playground` | 3.0 m | dirt, playground, sand, **trampled** | 다짐 흙 광장 |
| **`gravel_ground_01`** | 3.0 m | gravel, **pathway**, path, stones, sidewalk | gravel 대체(산책로) |
| `sandy_gravel_02` | 2.53 m | sand, gravel, stony, dusty, ground | **마사토 1순위** — 모래+세립 자갈 |
| `gravelly_sand` | 2.48 m | sand, gravel, stony, coarse, debris | 마사토 대안 |
| `ground_grey` | 1.0 m | gravel, grey, gravelly, coarse | 미세 입도(4.75 mm 대응 가능) |
| **`leaves_forest_ground`** | 1.26 m | dirt, forest, leaves, twigs, **yellow, green**, autumn | leaf_ground 대체 — **1.26 m 원본이라 축소 없이 쓸 수 있다** |
| `forest_leaves_04` | 1.50 m | leaves, ground, dirt, debris, dry, autumn, sticks | leaf_ground 대체 |
| `forest_floor` | 2.14 m | sand, leaves, autumn, forest, dirt, dry | leaf_ground 대체 |
| `dry_decay_leaves` | 2.0 m | leaves, forest, dry, sticks, winter, dead grass | 겨울 낙엽(C1 주변) |

**이미 디스크에 있는데 안 쓰는 것**: `assets/brown_mud_03_*`(1.3 m) · `assets/brown_mud_dry_*`(1.3 m)
— 6개 파일 **54.3 MB**. `TEX` 어디에도 등록돼 있지 않고 씬 참조 0건 **[실측 grep]**.
1.3 m 원본이라 **근경 흙 노출부에 배율 조정 없이 바로 쓸 수 있는 유일한 보유 자산**이다.

---

## 11. 씬 × 지피 실태 표 [실측]

괄호 안은 **사용 scale_m / 원본 실측 크기** 비율. 1.00 이 물리적으로 정확.

| 씬 | grass | dirt_park | gravel | leaf_ground | 3D 산포 |
|---|---|---|---|---|---|
| scene01·02·05·06·08·09·11·13·14·16·18·19·20·21 | 4.00 (0.27) | – | – | – | 없음 |
| scene03 riverbank | 4.00 (0.27) | 1.00 (0.33) | 0.60 (0.27) | – | 없음 |
| **scene04 parktrail** | 4.00 (0.27) | **3.00 (1.00)** | 0.50 (0.22) | – | 없음 |
| scene07 temple | 4.00 (0.27) | – | **0.35 (0.16)** | 2.00 (0.87) | 없음 |
| scene10 park deck | **2.60 (0.17)** | 1.10 (0.37) | – | 1.05 (0.46) | 없음 |
| scene12 riverside | 4.00 (0.27) | – | 0.60 (0.27) | – | 없음 |
| scene15 alley | – | – | – | – | 없음 |
| scene17 | 4.00 (0.27) | – | – | – | 없음 |
| sceneC1 snow | – | 2.00 (0.67) | – | – | 없음 |
| **sceneC2 leaf** | 4.00 (0.27) | 1.00 (0.33) | – | **0.90 (0.39)** | **fallcluster ×845 (5.14 M tri)** |
| sceneC4 wet | 4.00 (0.27) | – | – | – | 없음 |
| sceneD1 dock | – | – | – | – | 없음 |
| sceneD2 opening | – | **3.00 (1.00)** | 0.90 (0.40) | – | 없음 |
| sceneD3 drainage | 4.00 (0.27) | – | – | 0.80 (0.35) | 없음 |
| sceneD4 platform | – | – | 0.50 (0.22) | – | 없음 |
| sceneN1~N5 | 4.00 (0.27) | – | 0.60 (0.27)(N2) | – | 없음 |

집계:
- **grass 28씬 / dirt_park 6씬 / gravel 7씬 / leaf_ground 4씬.**
- **3D 지피 산포물이 있는 씬은 sceneC2 단 1개 (3.0%)**. 나머지 32씬의 지면은 100% 평면 텍스처다.
- **물리적으로 정확한 스케일(비율 1.00)은 scene04·sceneD2 의 dirt_park 2건뿐** (전체 45건 중 4.4%).

### 11-a. h0.3 판정 시점에서의 화면 점유 [실측+추정]

Isaac 기본 원근 카메라(focal 18.147 mm / aperture 20.955 mm → **HFOV 60.0° · VFOV 36.0°**) [추정],
h=0.3 · pitch −10° 기준. 지면은 D≈0.56 m 부터 수평선까지, **화면 세로의 78%** 를 차지한다.

| 거리 D | 가로 px/m | 깊이 1 m 당 px |
|---|---|---|
| 0.6 m | 2771 | 477 |
| 1.0 m | 1663 | 238 |
| 2.0 m | 831 | 82 |
| 5.0 m | 333 | 17 |
| 10.0 m | 166 | 4.6 |

→ `grass` 원본 273 px/m 이므로 **D < 3.0 m 구간 전체가 원본 확대 영역**이다(D=0.6 m 에서 10.2배).
근경 지면이 판정 1순위인 이 프로젝트에서 가장 나쁜 지점에 가장 나쁜 텍스처가 있다.

---

## 12. 조치 목록 (영향 × 비용 순)

| # | 조치 | 근거 | 비용 | 영향 |
|---|---|---|---|---|
| **A1** | `TEX["grass"]` 를 ambientCG **`Grass001`/`Grass004`(1.4 m, CC0)** 로 교체하고 전 씬 `scale=dict(grass=…)` 를 **1.4** 로 | §3-a, §10-b | 조달 스크립트 1항 + 씬 28개 상수 1개씩 | **28씬 지면 + §8 규약 위반 동시 해결** |
| **A2** | `LOOK_CLASS["veg"]["tex_alts"]` 에서 `leaf_ground` 제거 (A1 적용 전까지의 즉시 차단책) | §8 | 1줄 | 24씬 가을 낙엽 오염 즉시 중단 |
| **A3** | `VEG_DEBRIS` 를 본 감사 실측값으로 교체: `(0.0584,9175) (0.0239,2980) (0.0081,631) (0.0048,496) (0.0054,582)` | §6 | 5줄 | 산포 개수 정확도. **oakfall2 삼각형 582 는 이미 반영됨(일치), 피복만 0.0038→0.0054 재정정.** 낱장 3종은 40~60% 과소평가 상태 |
| **B1** | sceneC2 `scale=dict(leaf_ground=0.9→2.3)` + `leaf_tex_tint` 제거 | §7 | 2줄 | ΔE76 15.7→13.0, 크기 단절 2.56배→1.0 |
| **B2** | scene04·C2 경계에 `scatter_debris(edge_bias>0)` 로 흙/잔디 경계선 물리 파괴 | §4-c | 씬당 3~5줄 | "사각 이음매" 1차 해소 |
| **B3** | `scatter_debris` 에 **인스턴스별 틴트 지터** 추가(3~5색) | §5-a (색상 sd 3.4°) | `add_vegetation` 에 tint 인자 + 재질 변주 5개 | 낙엽 단색 문제 해소 |
| **C1** | `gravel` → PolyHaven `sandy_gravel_02`(2.53 m) 또는 `ground_grey`(1.0 m) 로 교체, scale_m 은 KS A 5101-1 4.75 mm 통과 입도에 맞춰 산정 | §3-a [법령] | 조달 1항 + 7씬 | 마사토 규격 정합 |
| **C2** | `dirt_park` scale_m 을 전 씬 **3.0** 으로 통일(또는 `brown_mud_dry` 1.3 m 로 근경 교체) | §3, §10-c | 4씬 상수 | 씬 간 스케일 단서 일관성 |
| **C3** | S3 `Rocks/rock_small_02~07,11~14` 10개 추가 조달 | §10-a | 스크립트 1항 | 자갈·잡석 다양성 |
| **D1** | `Shrub/Rhododendron.usd`(만개 76.7% 마젠타)를 계절 중립 관목으로 교체 | §9 | 관목 담당 이관 | 계절 규약 |
| **D2** | 미사용 `brown_mud_03/_dry` 6파일 54.3 MB — 사용하거나 정리 | §10-c | — | 저장소 위생 |

---

## 13. 확인하지 못한 것 (정직한 한계)

- **인스턴싱 런타임 유효성**: 이 환경에 `pxr` 런타임(Isaac)이 없어 `IsInstance()` 확인 불가.
  코드상 `SetInstanceable` 대상은 `/Asset` 로 이미 옮겨져 있다(레드팀 R6 수정 반영 확인).
- **`asset_audit_v1.md` 유효피복표의 계산 오차 원인**: 해당 스크립트가 저장소에 없어 규명 불가.
  본 감사 값은 검증·수렴을 거쳤으므로 이쪽을 채택 권고.
- **`PavingStones131` 물리 크기**: ambientCG API 가 `0×0` 을 반환한다(치수 미기재).
  현행 주석의 "정사각 유닛 170 px/2048 → 12반복" 은 픽셀 계측이지 실물 치수 근거가 아니다.
- **경계 전이대 폭 10~30 cm**: 국내 실측 문헌을 찾지 못해 [추정] 으로만 적었다. 수치를 코드에
  넣으려면 별도 근거가 필요하다.
- **`Leaves/basecolor.png`(S3)의 톤**: 다운로드하지 않아 §7 톤 매칭 대안으로서의 적합성 미검증.

---

## 부록 A. 출처 URL

- PolyHaven 텍스처 실측 크기: `https://api.polyhaven.com/info/aerial_grass_rock` ·
  `/park_dirt` · `/gravel_floor` · `/forest_leaves_03` · `/brown_mud_03` · `/brown_mud_dry` ·
  `/asphalt_02` · `/snow_01` · `/stone_tiles_02` · `/brushed_concrete_03`
- PolyHaven 후보 목록: `https://api.polyhaven.com/assets?t=textures&c=terrain` (terrain 129종)
- ambientCG 잔디: `https://ambientcg.com/api/v2/full_json?type=Material&category=Grass&include=dimensionsData,tagData`
- ambientCG 아틀라스: `https://ambientcg.com/api/v2/full_json?type=Atlas&limit=200&include=tagData`
- NVIDIA S3 목록: `https://omniverse-content-production.s3.us-west-2.amazonaws.com/?list-type=2&prefix=Assets/Vegetation/{Debris,Leaves,Rocks}/`
- 들잔디 잎 나비 4~7 mm: 산림청 『관상산림식물류 — 잔디』
  `https://www.forest.go.kr/kfs/images/data/down/imsan/imsan_06_04.pdf`
- 들잔디 초장·깎기: 「한국잔디(Zoysia japonica)의 깎기주기 결정을 위한 지상부 생육 조사」
  `https://scienceon.kisti.re.kr/srch/selectPORSrchArticle.do?cn=JAKO201030853095048&dbt=NART`
- 마사토 입도(KS A 5101-1 4.75 mm 통과): 국토교통부 『조경공사 표준시방서』(2016)
  `https://www.codil.or.kr/filebank/construction/SS/CIGCSS190036/CIGCSS190036.pdf`

## 부록 B. 참조한 코드 위치

| 내용 | 위치 |
|---|---|
| `TEX` 지면 역할 정의 | `scene_common.py:46-134` |
| `LOOK_CLASS["veg"]` (문제의 tex_alts) | `scene_common.py:277-281` |
| `_texture_mean` (선형 평균) | `scene_common.py:505-531` |
| `_promote_const_to_texture` 채택 조건 | `scene_common.py:534-580` (특히 `spread <= 4.0` = 578) |
| `make_pbr` 의 `texture_scale = 1/scale_m` | `scene_common.py:1054-1058` |
| `VEG_DEBRIS` | `scene_common.py:1767-1773` (oakfall2 수정 반영 후 기준) |
| `scatter_debris` (피복 역산·인스턴싱) | `scene_common.py:1805-1891` |

> 주의: `scene_common.py` 는 이 웨이브에서 다른 에이전트가 동시 편집 중이라 행 번호가
> 밀린다. 위 번호는 2026-07-29 15:0x 시점 기준이며, 검색은 심볼명으로 하는 편이 안전하다.
| scene04 흙 접속부 3.0×6.0 m 박스 | `scenes/main/scene04_parktrail.py:739-748` |
| scene04 재질 스케일 | `scenes/main/scene04_parktrail.py:278` |
| sceneC2 낙엽 마운드(장판 판) | `scenes/batch1/sceneC2_leaf_stairs.py:486-502` |
| sceneC2 3D 낙엽 산포 호출 | `scenes/batch1/sceneC2_leaf_stairs.py:552-568` |
| sceneC2 재질 스케일·틴트 | `scenes/batch1/sceneC2_leaf_stairs.py:207-216` |
