# PREREG_CUEOFF — CUE-OFF 개입 대조의 사전 등록

**작성 시각(고정): 2026-08-23T03:55:45+09:00 · repo HEAD `99562b0` (feat/realism-v1)**
**이 문서는 CUE-OFF 팔이 단 한 컷도 렌더되기 전에 작성됐다.** 렌더 산출물
(`dataset/260823_cueoff*`)의 최초 생성 시각이 위 시각보다 늦다는 것이 그 증거다
(`gates_cueoff.py --prereg-check`가 이 조건을 기계로 검사한다).

- 작성: Claude Code (GPU-2 준비 세션) · 상위 근거: `H_CUE_AUDIT.md` §6 · `CUEOFF_CANDIDATES.md` ·
  DECISIONS **D30**(데이텀 보존 수술) · **D31**①(CUE-OFF = 본 창의 과학적 중심) ·
  **D35**(레드팀 1파 수용: 플라시보 팔 + 포즈 5키 게이트 + 판정식 편입) ·
  **D36**(단서 감사 착지 + 팔 확정) · `redteam/R2_method.md` §5.3
- 재훈련 0. frozen 체크포인트 무수정. 정본 씬 파일 무수정(격리 사본만 씀).

---

## 0. 이 개입이 답하려는 질문 (한 문장)

> 본 표의 frozen 모델이 strict-H 프레임에서 내는 발화는 **프레임 안에 남아 있는 낙차 단서를
> 읽은 결과인가**, 아니면 **씬 정체성·거리 사전확률 위의 지름길인가?**

관찰 층화(`H_CUE_AUDIT.md` §4)는 이 질문에 답하지 못했다 — 단서 축과 시점 축이 코퍼스 안에서
분리되지 않기 때문이다(§4.4에서 씬+band를 고정하면 격차가 소멸). **같은 씬·같은 포즈에서
단서만 지우면 시점 축이 자동으로 고정된다.** 그것이 이 개입이다.

---

## 1. 가설 (결과를 보기 전에 고정)

| # | 가설 | 예측 (paired strict-H 프레임 기준) |
|---|---|---|
| **H1 (단서 사용)** | 모델의 H 발화는 프레임 안 낙차 단서에 의존한다 | 단서를 지우면 H recall이 **하락**하고, 그 하락은 같은 픽셀 질량의 **비단서** 제거가 만드는 하락보다 **크다** |
| **H0 (지름길)** | 모델의 H 발화는 씬 정체성/기하 사전확률에 의존한다 | 단서를 지워도 H recall이 **유지**된다(Δ ≈ 0). 혹은 하락하더라도 플라시보 하락과 **구별되지 않는다** |
| **H2 (어휘 발화)** | 모델은 "가드·드레싱 어휘"만 보고도 발화한다 | **무위험+단서 팔(C)** 의 FA가 높다. sceneC2 신off FA .681의 비-test 재현 |
| **H3 (가드 단독)** | "가드 = 낙차" 지름길(매트릭스 지름길 패밀리 2위, 14씬)이 정량화 가능하다 | **B1 − B2** 가 가드 단독 기여분. 이 값이 B1 전체 효과의 대부분이면 H3 성립 |

---

## 2. 설계

### 2.1 씬 (비-test 3씬 — 선택이 아니라 열거)

`CUEOFF_CANDIDATES.md` §2: 조건(비-test · strict-H 보유 · 배선된 `cue_*` 보유)을 만족하는 씬은
4개뿐이고, 그중 기대효과가 가장 큰 3개를 쓴다. **scene14는 test이자 가드가 토글이 아니어서
원천적으로 불가능하고**(D36), scene09는 주 증거(수면·먼 둑)가 어떤 토글에도 물려 있지 않아 제외.

| 씬 | 분리 | strict-H | 계보 라운드(=밴드) | 시드 | 역할 |
|---|---|---|---|---|---|
| **scene12** 리버사이드 데크 | train | **48** (24+24) | `boost_e` + `boost_e2` | 20260820 / **20260821** | 주 표적 (가드·재질·드레싱 3토글 전부 ON·배선) |
| **scene17** 한강 램프쌍 | train | 33 (24 + main 9) | `boost_h` (+ `main`) | 20260820 (+20260819) | **무가드 대조** — 난간이 설계상 없다 |
| **scene20** 사교 30° | val | 6 | `boost_e2` | **20260821** | 외과적 단일 개입 (h0.3 유일 증거 = 치크월) |

> **시드에 대한 정직한 이탈 기록.** 브리프/과제 지시는 "seed 20260820"이라고 적었으나,
> 계보 라운드의 실측 시드는 `boost_e`/`boost_h` = 20260820, **`boost_e2` = 20260821**이다
> (`dataset/260820_boost_e2_*/*/scene*/variation.json`). 본 개입은 **밴드별 계보 시드**를 쓴다.
> 이유: (a) 성립 조건은 "한 씬×밴드 안의 모든 팔이 같은 시드"이며 이는 그대로 지켜진다,
> (b) 계보 시드를 쓰면 **팔 A가 감사 대상 프레임의 비트 단위 재현**이 되어, 팔 A 자체가
> "격리 사본이 정본과 같은 그림을 만든다"는 무료 검증이 된다(§5 게이트 G0).
> 20260820을 강제하면 (b)를 잃고 새 프레임을 만들 뿐이며, 얻는 것이 없다.

### 2.2 팔 (5팔 — D36 4팔 + D35 플라시보)

씬 설정은 `NEGOBS_SCENE_CONFIG` JSON 한 줄(`render_configs/<scene>_<arm>.json`).

| 팔 | 이름 | 뜻 | scene12 | scene17 | scene20 |
|---|---|---|---|---|---|
| **A** | `hz1_cue1` | 위험 + 단서 (기준선) | `{"hazard_stairs":true}` | 〃 | 〃 |
| **B2** | `hz1_rail0` | 위험 유지, **가드만 제거** | `+{"cue_railing":false}` | **없음**(난간 부재) | `+{"cue_railing":false}` |
| **B1** | `hz1_cue0` | 위험 유지, **단서 전부 제거** | `+{"cue_railing":false,"cue_material_break":false,"cue_scene_dressing":false}` | `+{"cue_material_break":false,"cue_scene_dressing":false}` | scene12와 동일 |
| **P** | `hz1_placebo` | 위험 + 단서 유지, **비단서 오브젝트 제거** | `+{"placebo_remove":true}` | 〃 | 〃 |
| **C** | `hz0_cue1` | **무위험 + 단서 유지**(신off) | `{"hazard_stairs":false,"keep_dressing":true}` | 〃 | 〃 |

**단서를 새로 켜는 팔은 없다**(`cue_tactile` 등 = 에지 위 마킹 신설 = 씬 난이도 정체성 변경,
브리프 §3-4 위반). 결재란 안건으로만 남긴다.

### 2.3 조건·카메라

- 조명 조건 **L0, L5, L7** (계보 라운드와 동일). 씬 원장이 거부하는 조합은 없다
  (scene12/17/20 모두 `conds_sub` 치환 대상이 아니다 — `run_260820_boost.sh:191-197` 확인).
- `--cams 8` × 3조건 = **24컷/팔·밴드**. 시드·밴드가 같으므로 컷 idx 0..7은 팔 간 동일 표본이다.
- `NEGOBS_CAM_BAND_OVERRIDE`(계보 그대로):
  `boost_e {"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}` ·
  `boost_h {"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}` ·
  `boost_e2 {"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}` · `main` = 오버라이드 없음.
- 라운드 스탬프: `260823_cueoff_<arm>`(각 씬의 1차 밴드) · `260823_cueoff2_<arm>`(scene12 2차 밴드
  `boost_e2`) · `260823_cueoff3_<arm>`(선택: scene17 `main` 밴드, H 9장 추가).

---

## 3. 플라시보 팔 — 씬별 선정과 그 근거 (D35/R2 §5.3-2 필수 요건)

**요건**: 13단서 어휘에 **속하지 않고**, GT 웨지의 증거 사슬 **밖**에 있으며, 제거되는 단서와
**비슷한 픽셀 질량**을 가진 오브젝트.

픽셀 질량은 형용사가 아니라 수치이므로 **렌더 전에 CPU로 측정했다**(`pixel_mass.py`):
각 후보의 월드 AABB를 그 컷의 **실제** 카메라 기저(`CAM_CONVENTION.md` §2)로 투영해
프레임 클리핑한 볼록껍질 면적. **크레스트 은폐**(x>0에서 z < −h·x/d 인 점은 씬 자신의 마루가
가린다 — H_CUE_AUDIT §2.2가 확인한 코퍼스 유일 가림 기제)를 반영했다.
**상한값**이며(AABB ≥ 실물, 크레스트 외 차폐 미반영) 순위 매기기 용도로만 쓴다.
전수: `PLACEBO_PIXEL_MASS_crest.csv`.

### 3.1 scene12 — **채택 (GREEN)**

**제거 대상**: 상부 홍수터 **벤치 2기**(−13.0/−6.5, y −1.90) + **가로등 2주**(−15.0/−2.0,
y −2.30/−2.60, 폴 4.5 m) + **먼 생울타리 3열**(cy −16…−19).

| 근거 | 내용 |
|---|---|
| 13단서 무크레딧 | 매트릭스 scene12 항이 `cue_scene_dressing`에 부여한 단서는 **갈대**(vegetation_edge) · **자전거도로 백선**(signage_or_marking) · **교각**(geometry_silhouette 일부) · far_side 일부다. 벤치·가로등·생울타리에는 **어떤 단서도 부여돼 있지 않다**. |
| 증거 사슬 밖 | 셋 다 **상부 보행면 z=0**(카메라와 같은 레벨) 위, 낙차 반대쪽(−Y)에 있다. 매트릭스가 "하부 레벨 전용"으로 지목한 것은 **하부 벤치**와 **백선 자전거도로**이며(§2.4 s12 행), 이 둘은 **제거하지 않는다**. |
| 레드팀 원형 | R2 §5.3-2가 든 플라시보 예시가 정확히 "벤치·화분·전신주". 매트릭스 B6 행은 **"s12 상부 프롬나드 벤치"를 비해저드 반례 오브젝트로 신설하자**고 제안한다 — 즉 정본 판독이 상부 벤치를 "낙차와 무관"으로 분류한다. |
| 픽셀 질량 | `boost_e` **186 k px (8.95 % 프레임)** · `boost_e2` **115 k px (5.57 %)** |

**정합성 등급**
- vs **B2**(가드만 제거, 6.3 k / 9.9 k px): 플라시보가 **12–30× 크다 → 보수적**.
  Δ_cue − Δ_placebo ≥ 0.15가 나오면 강한 결과다.
- vs **B1**(전체 ~600 k px, 교각 456 k가 지배): 플라시보가 **~3.2× 작다 → 반보수적**.
  이 대비에서의 통과는 **결정적 증거로 승격하지 않는다**(§4 참조).

### 3.2 scene17 — **채택 (GREEN, 보수적)**

**제거 대상**: 대안(對岸) **아파트 4동**(`far_buildings` E·F·G·H, x 85.5–98.5 m). **교량은 유지**.

| 근거 | 내용 |
|---|---|
| 13단서 무크레딧 | 감사가 scene17의 `cue_scene_dressing` 단서로 지목한 것은 **가로등 폴·km 표지판**("밑동이 가려진 채 마루 지평을 뚫는 수직물", geometry_silhouette M · signage_or_marking w)이며, 이들은 **제거하지 않는다**. `far_side_visible_depth`(M)는 낙차의 **건너편**(테라스·강)을 보는 것이고 그것은 `build_river`/`build_terrace`가 만든다 — 항상 ON, 팔과 무관. |
| 증거 사슬 밖 | 아파트는 **강 건너 86–98 m**, 밑동을 가리는 것은 근경 마루가 아니라 **대안 둑**이다. 6–12 m 앞 3.2 m 낙차에 대해 아무 말도 하지 않는다. |
| 픽셀 질량 | **427 k px (20.6 % 프레임)**, strict-H **33/33 프레임에서 화면 안**(0 프레임 결측) |

**정합성 등급**: B1이 지우는 총 질량은 크레스트 은폐 반영 후 **~23 k px**(갈대 22 k + 나무 0.44 k
+ 폴 0.09 k + 표지 0.13 k). 플라시보가 **~18× 크다 → 강하게 보수적**. 이 씬에서
Δ_cue − Δ_placebo ≥ 0.15가 나오면 그것은 매우 강한 H1 증거다.
**선언할 부작용**: 배경을 지우면 하늘 비율이 오른다(전역 노출 통계 변동). 이는 B1도 겪는
변동이며, 플라시보가 그것을 **더 크게** 겪는다는 점에서 방향이 보수적이다.

### 3.3 scene20 — **정직한 결론: 1차 판정용 플라시보는 없다 (AMBER)**

측정 결과(strict-H 6프레임, 크레스트 은폐 반영):

| 후보 | 평균 px | 0 px인 프레임 |
|---|---|---|
| 메사 화분 3 / 벤치 3 / 가로등 3 / 볼라드 4 / 생울타리 2열 | **0** | **6/6** |
| 벨트 수목(동측 2열) | 13.4 k | 0/6 |
| 백드롭 동측 2동 (E1·E2) | 240 k | 0/6 |

- **메사 가구는 전부 화면 밖이다.** 볼라드(x −13.6)는 카메라 뒤(x −9…−4), 화분·벤치·가로등·
  생울타리는 62° 전방 화각 밖 측방에 있다. **제거해도 픽셀이 0이므로 플라시보가 될 수 없다.**
- 화면 안에서 지울 수 있는 유일한 질량은 **백드롭 동측 2동**인데, 이들은 **골짜기 바닥
  (base_z −2.15)에 서서 밑동이 메사 립에 잘린 수직물**이다. 즉 매트릭스가
  `geometry_silhouette`로 판독하는 **형태 자체**를 공유한다.
- 반론 근거는 하나뿐이다 — 정본 매트릭스 §2.4 s20 행이 "`cue_railing=False` 팔의 h0.3는
  **사실상 낙차 무증거**"라고 판정했고, 그 판정은 **백드롭이 있는 상태에서** 내려졌다.
  즉 정본은 백드롭에 단서 크레딧을 주지 않았다.

**사전 등록 결정**: scene20의 P팔은 **렌더하고 표에 싣되, §4의 1차 판정식에는 넣지 않는다**
(탐색적). scene20은 **B2(치크월 단독 절제)의 외과적 결과**와 **C팔 FA**로만 1차에 기여한다.
플라시보를 우겨 넣어 "통과"를 만드는 것보다, 없다고 적는 쪽이 이 프로젝트의 규율이다.

---

## 4. 판정식 (결과를 보기 **전에** 고정 — D35/D36/R2 §5.3-3)

### 4.1 지표

- **1차 결과 지표**: `frame_recall_H` — GT 양성 셀 중 하나라도 p ≥ τ_op이면 hit. τ_op = **0.5** 고정.
- **병기(R2 P3)**: **트윈-조건부 H recall** = `[max_on_gt ≥ τ] ∧ [max_twin_gt < τ]`.
  트윈의 정의를 본 개입에 맞춰 **사전 등록**한다:
  - `twin=C` (**1차**): 같은 컷의 **팔 C**(무위험 + 단서 전부 유지). "이 포즈에서 단서 어휘만으로는
    발화하지 않는다"를 조건으로 건다. 단서 질문에 가장 직접적인 조건부다.
  - `twin=off` (보조): 계보 off 라운드(`260820_boost_*_off`, 무위험 + 드레싱 없음).
    B1의 사실상 정확한 트윈.
- **FA 지표**(팔 C): `frame_fa` = GT 전셀 음성인 프레임에서 어떤 셀이든 p ≥ τ_op인 비율.
- 모델 3종(RGB / Depth / B2-DINOv2) × 시드 {42, 43, 44} = 9런. **재훈련 0**,
  `experiments/dayrun_0820/runs/v2/{rgb,depth,b2}_s{42,43,44}/best.pt` 무수정.

### 4.2 판정 모집단 — paired H

주 판정은 **양 팔에서 모두 strict-H인 프레임(paired)** 위에서만 한다.
티어는 팔마다 다시 도출한다(§5 G4). H→E 이동 프레임은 **수를 반드시 보고**하고 판정에서 제외한다
(`CUEOFF_CANDIDATES.md` §5-4, scene20 치크월 절제 시 계단 픽셀 노출 가능성).

### 4.3 1차 판정식 (D36 그대로)

```
Δ_cue      = recall_H(A) − recall_H(B)         # B = 단서 제거 팔
Δ_placebo  = recall_H(A) − recall_H(P)
개입 증거(H1 채택):  (Δ_cue − Δ_placebo) >= 0.15  AND  3/3 시드 동부호
지름길(H0 채택)  :   Δ_cue < 0.10               AND  3/3 시드 동부호
그 사이 / 부호 갈림:  판정 유보 — 표만 싣는다
```

**어느 B를 1차로 쓰는가 — 씬별로 사전 등록한다** (§3의 픽셀 질량 정합성이 결정):

| 씬 | 1차 Δ_cue | 이유 | 2차 (캐비앗 병기) |
|---|---|---|---|
| **scene12** | **Δ(A, B2)** (가드 단독) | 플라시보가 B2보다 12–30× 크다 = 보수적 | Δ(A, B1) — 플라시보가 ~3.2× 작다(**반보수적**, 통과해도 결정적 증거로 승격 금지) |
| **scene17** | **Δ(A, B1)** | B2 부재(난간 없음). 플라시보가 ~18× 크다 = 강하게 보수적 | — |
| **scene20** | (플라시보 없음) | §3.3 | Δ(A,B2)·Δ(A,B1) 자체는 보고하되 플라시보 보정 없이 = **탐색적** |

**합산 금지**: 씬을 풀링해 하나의 Δ를 만들지 않는다(R2 P2, Simpson). 씬별로 내고 씬별로 판정한다.
**최소검출효과 선언**(R2 P6): paired H가 24–48 프레임인 씬에서 0.10보다 작은 차이는 해석하지 않는다.

### 4.4 보조 판정 (사전 등록)

| 관측 | 판독 |
|---|---|
| **B1 − B2**(scene12·scene20) | **가드 단독 기여분**. B1 전체 효과의 과반이면 "가드 어휘 = 낙차"(지름길 패밀리 2위, 14씬)의 직접 정량 = 논문 본문 후보(H3) |
| **팔 C의 FA** | H2. sceneC2 신off FA .681과 나란히 놓는다. **FA ≥ 0.40이면 "단서 어휘만으로 발화"의 비-test 재현으로 인정** |
| 팔 C의 FA가 **플라시보 팔 C**보다 유의하게 낮으면 | (본 라운드에는 P의 무위험 트윈이 없다 — **측정 불가로 선언**하고 추정하지 않는다) |
| 트윈-조건부와 현행 recall의 **부호가 다르면** | 현행 recall 쪽 결론을 채택하지 않는다. 트윈-조건부를 본문, 현행을 부록 |

### 4.5 무효 조건 (하나라도 걸리면 그 씬은 판정하지 않는다)

1. 포즈 동일성 게이트(§5 G3) 실패 프레임이 그 씬 컷의 **> 25 %**
2. `polar_gt` 바이트 동일성(§5 G2) 실패 — `cue_*`가 위험 기하를 건드렸다는 뜻
3. paired H 프레임 수 < **10** (H_CUE_AUDIT 사전 등록 §3.3 조건 3과 동일 기준)
4. 3시드 부호 갈림 → "판정 불가"로 기록하고 표만 싣는다 (감사 §4.2와 같은 처분)

---

## 5. 착수 전 게이트 (`gates_cueoff.py` — 하나라도 실패 = 중단·기록·롤백)

| # | 게이트 | 합격 기준 |
|---|---|---|
| **G0** | **격리 사본 무해성** — 팔 A가 계보 정본 라운드를 재현하는가 | `variation.json`의 `cam` 5키 + `eye` 3성분이 `260820_boost_*_on`과 **완전 일치**. PNG 바이트 동일은 **가산점이지 조건이 아니다**(PT 렌더의 비결정성을 사전에 인정) |
| **G1** | 1프레임 실렌더 스모크 | 포팅한 3씬 각각 **팔 C**(유일한 신규 코드 경로)에서 1컷 실렌더 성공 + `cam.ground_z`가 정본 on팔과 일치 |
| **G2** | **위험 기하 불변** | A vs {B1, B2, P}의 프레임별 `polar_gt` **바이트 동일**. `heightmap.npy` 해시 동일 |
| **G3** | **포즈 동일성** (R2 §5.3-1: 5키) | 팔 간 컷별 `eye`·`yaw`·`pitch`·`roll`·`hfov`·`d`·`h_rel`·`ground_z` 차 < **1e-6**. 위반은 3층으로 분리 보고: `pose_exact`(<1e-6) / `pose_tol`(≤0.02 m) / `pose_fail`(>0.02 m) |
| **G4** | 티어 재도출 | 팔별 V/E/H/H_weak/none_in_fov 5범주 카운트. **H→E 이동 프레임 수 보고** |
| **G5** | **C팔 GT 전영(全零)** | 팔 C의 모든 프레임에서 `polar_gt` 합 = 0. 하나라도 양성이면 신off 수술이 낙차를 남긴 것 = 중단 |
| **G6** | 평가는 추론만 | frozen ckpt의 mtime/해시가 렌더 전후 동일 |

### 5.1 이미 알고 있는 G3 위반 — 선언 (숨기지 않는다)

**scene20의 `Band_*`(메사 차콜 줄무늬)는 `cue_scene_dressing` 안에 있고, 그 상면은 z = +0.0085 다.**
계보 데이터에서 실측된다: `260820_boost_e2_on` 컷 0000·0001의 `ground_z` = **0.0085**,
같은 컷의 off팔은 **0.0** — 즉 **8.5 mm의 데이텀 이동이 정본 코퍼스에 이미 존재한다**.
따라서 **팔 B1(scene20)** 은 밴드가 사라지므로 밴드 위에 선 컷(밴드 폭 0.45 / 간격 2.0 →
기대 22.5 %, 24컷 중 5–6컷)에서 `eye.z`가 8.5 mm 이동한다. 이것은
- **은폐하지 않고** `pose_tol` 층으로 분리 보고하며,
- 1차 판정은 `pose_exact` 층에서만 하고,
- §4.5-1(위반 > 25 %)에 걸리면 scene20 B1은 **판정하지 않는다**.

**팔 C(scene20)** 에서는 이 이동을 **정당하게** 제거한다: 밴드는 드레싱이므로 `keep_dressing`
팔이 그것을 보존하는 것이 팔의 정의와 일치한다(§6.3).

scene12·scene17에는 이 문제가 없다(§6.1·§6.2의 데이텀 논증 + 계보 실측).

---

## 6. 데이텀 보존 논증 (D30 계보 — 성립 조건이지 선택이 아니다)

포즈 샘플러는 `gz = pre.ground_z(-d, y)`를 씬 AABB 하향 레이로 잡는다
(`run_data_render.py:458`, `CAM_CONVENTION.md` §1). **오브젝트를 지우면 카메라 지면 기준이
움직일 수 있고**, 실제로 sceneC2 구off에서 0.130 → 0.0163 m로 이동해 트윈 쌍이 0개가 된 전례가
있다(D17 → D30이 원인을 `build_flat_fill`의 복도 관통 슬래브 + 16 mm 변위 스킨으로 규명).

**카메라 스트립** = `x ∈ [−d_max, −d_min]`, `y ∈ [gy−0.9, gy+0.9]`, 세 씬 모두 `gy = 0`.

### 6.1 scene12 (스트립 x ∈ [−12, −4], y ∈ [−0.9, 0.9])

- 스트립 위 첫 AABB는 **언제나 `Deck/Slab`**(x −18…0, y −1.25…1.25, 상면 z = **정확히 0.000**).
  이 프림은 `sc.skin_exclude`로 등록돼 있고 경로 토큰 `deck`이 `_SKIN_DENY`에 있어
  **변위 스킨을 두 번 거부한다** → 상면이 흔들릴 수 없다.
- **B1/B2/P가 지우는 것 중 스트립 위를 지나는 프림은 하나도 없다**(전수 확인):
  난간 y 1.09–1.21 · 상부 벤치 y −1.90 · 가로등 y −2.30/−2.60 · 나무 y ≤ −8.5 ·
  생울타리 cy ≤ −16 · 갈대 y ≥ 1.40 또는 x > 0 · 자전거도로 y −8…−5.
  최근접이 난간의 y 1.09 로, 스트립 상한 0.9와 **0.19 m 여유**.
- **팔 C**: `build_flat_fill`(x −40…48 × y −22…1.25 를 덮는 88 × 23 m 잔디 슬래브)을
  **호출하지 않는다** — 그것이 sceneC2가 밟은 함정의 scene12판이다.
  대신 `build_terrain` · `build_deck` · `build_ground_kit`을 **팔 A와 완전히 같은 인자·같은 순서로**
  부르고, 위험(계단)만 짓지 않으며, 채움 슬래브는 **x ≥ 0 으로 한정**한다
  (`build_lower_fill`). x ≥ 0 슬래브는 x < 0 의 어떤 (x, y)에서도 하향 레이의 첫 히트가 될 수 없다.
  ⇒ **팔 C의 카메라 데이텀은 팔 A와 구성적으로 동일하다.** G1 스모크가 이를 실측한다.
- **추가 함정 (본 포팅이 새로 발견)**: `run_data_render.SIDECAR_ORACLES["scene12"] = _solid_at`.
  이 오라클은 하이트맵 AABB 읽기를 **아래로** 행진시켜 보정하는데, 정본 `_solid_at`은
  cfg와 무관한 순수 함수여서 **위험이 꺼진 팔에서도 ON팔 계단 프로파일을 되살린다**.
  방치하면 팔 C의 `heightmap.npy`가 그림에 없는 −0.68 m 계단을 담고, 라벨러의
  `diff = z_off − z_on`이 **팔 C에 양성 GT를 만들어낸다**(게이트 G5가 잡을 자리이지만,
  잡히기 전에 고치는 것이 맞다). 격리 사본에서 `_solid_at`을 **팔 인지형**으로 고쳤다:
  위험이 꺼진 팔에서 `x ≥ 0` 채움 영역은 `z ∈ [−1.4, 0]`을 solid로 답한다.

### 6.2 scene17 (스트립 x ∈ [−12, −6], y ∈ [−0.9, 0.9])

- 스트립 위 첫 AABB는 `Levee` · `WalkBand`(x −10.5…−7.5, proud **+0.006**) ·
  `GreenStrip`(x −7.5…−7.0, top 0.0) — **전부 `build_levee`가 만들고, `build_levee`는
  어떤 cfg 게이트 밖에 있다**(위험/드레싱 토글과 무관하게 항상 호출).
  ⇒ **5팔 전부에서 데이텀이 구성적으로 동일하다.**
- 계보 실측이 이를 확인한다: `260820_boost_h_on`과 `_off`의 `ground_z` 집합이 둘 다
  `{−0.0, 0.006}`이고 컷 0000의 `eye`가 소수 4자리까지 일치.
- 드레싱 중 스트립 근처에 오는 것은 `crown_lights` x −10.9 뿐인데 y ∈ {−12, 9.5, 31}로
  최소 **9.5 m** 떨어져 있다. `crown_trees`도 최근접 y −8.4.
- 팔 C는 정본 `build_flat_fill`(상면 0.0, 두께 3.6 m → `_skin_wanted`가 `sz > 0.8`로 스킨 거부)을
  그대로 쓴다. 밴드(+0.006)가 그 위에 남으므로 데이텀 불변.

### 6.3 scene20 (스트립 x ∈ [−9, −4], y ∈ [−0.9, 0.9])

- 스트립 위 첫 AABB는 `UpperPlaza`(상면 0.0, `skin_exclude`) 또는 그 위의
  `Band_i`(상면 **+0.0085**).
- **밴드는 `build_upper` 안의 `cue_scene_dressing` 분기에 있다** → B1과 (정본) C에서 사라진다.
  → §5.1의 선언된 G3 위반. **B1은 층 분리 보고, C는 포팅으로 해소**:
  격리 사본은 밴드 루프를 `build_bands(M, top)`로 분리하고, `keep_dressing` 팔에서
  `build_flat_fill` 직후 `top = upper.z_top = 0.0`으로 **다시 세운다**. 밴드의 y 클램프는
  x만의 함수(`min(y_half, mesa_slope·|x|)`)라 팔 A와 **좌표까지 동일**하다.
  ⇒ 팔 C의 데이텀 = 팔 A의 데이텀.
- `FlatPlaza`는 정본에서 이미 `sc.skin_exclude` 등록돼 있다(scene20:736) — 스킨 함정 없음.

---

## 7. 비용·리스크

| 항목 | 값 |
|---|---|
| 렌더 컷 | scene12 2밴드 × 5팔 = 240 · scene17 1밴드 × 4팔 = 96 · scene20 1밴드 × 5팔 = 120 → **456컷** (+ 선택 scene17 main 4팔 96컷) |
| 실측 s/컷 | scene12 4.07 · scene17 4.7 · scene20 4.2 |
| 렌더 순수 시간 | ≈ **33분** |
| Isaac 부팅 | 19회 × 60–90 s ≈ **25분** |
| 스모크 | 3회 × < 3분 = **9분** (V2S 큐 슬롯 사이) |
| **GPU 총계** | **≈ 65–75분** (선택 라운드 포함 시 +15분) |
| 추론 | 3모델 × 3시드 × 19라운드-씬 ≈ 수천 프레임, GPU **수 분** |

**리스크**

1. **scene20 B1의 8.5 mm 데이텀 이동** — 선언됨(§5.1). 층 분리로 처리.
2. **scene20 P가 1차 판정에 못 들어간다** — 선언됨(§3.3). scene20은 B2 외과 결과와 C팔 FA로만 기여.
3. **scene12 B1 대비의 플라시보 과소 정합** — 선언됨(§3.1). 2차로 강등.
4. **팔 C의 은폐 관계 손실** — 무위험 팔에는 마루가 없으므로 "밑동이 가려진 기둥"이라는
   *관계*는 원리적으로 보존 불가다. 팔 C가 보존하는 것은 **드레싱 오브젝트**이지 그 은폐 관계가
   아니다. sceneC2 신off도 같은 성질이며, 그것이 이 팔이 FA를 재는 팔인 이유다.
5. **PT 렌더 비결정성** — G0을 "포즈·GT 일치"로 정의하고 PNG 바이트 동일은 가산점으로 둔 이유.
6. **V2S 큐와의 GPU 경합** — 모든 호출이 `flock -o -w 3600 -E 201`. 락 타임아웃(rc 201)은
   FAIL-요약에 남고 재실행이 안전하다(레주메).

---

## 8. 이 문서가 잠그는 것 (사후 변경 금지 목록)

1. τ_op = 0.5, 시드 {42,43,44}, frozen ckpt 경로
2. 1차 지표 = `frame_recall_H`, 병기 = 트윈-조건부(twin=C)
3. 씬별 1차 Δ_cue의 선택(§4.3 표) — **결과를 본 뒤 B1↔B2를 바꾸지 않는다**
4. 임계 0.15 / 0.10, 3/3 동부호, 최소검출효과 0.10, paired H 최소 n = 10
5. 플라시보 오브젝트 집합(§3) — 결과가 마음에 들지 않는다고 다시 고르지 않는다
6. scene20은 플라시보 보정 판정에서 제외

---

# AMENDMENT A1 — 2026-08-23T04:08:51+09:00 (여전히 렌더 0컷)

**적법성**: 이 개정은 **CUE-OFF 데이터가 아니라 이미 출하된 코퍼스의 하이트맵 사이드카를
CPU로 읽어서** 나왔다. 개입 결과를 본 뒤의 기준 변경이 아니므로 사전 등록의 효력을 깨지 않는다.
원문은 지우지 않고 아래에 덧붙인다.

## A1.1 발견 — boost 라운드는 `fuse_heightmap.py`를 통과한 적이 없고, 그 결과 scene12의 낙차 발자국이 **50셀**이다

`labeling/labeler.py`의 GT는 **트윈 하이트맵 차분** `footprint = {z_off − z_on ≥ 0.3}`이다.
`run_data_render.SIDECAR_ORACLES`는 6씬(**scene06·07·08·11·12·19**)에서 씬 자신의 `_solid_at`
오라클로 AABB 읽기를 **아래로** 보정하는데, 그 오라클들은 **`hazard_stairs`를 모르는 순수 함수**다.
따라서 **위험이 꺼진 팔에서도 ON팔 프로파일이 되살아나고 트윈 차분이 상쇄된다.**

실측(`heightmap_meta.json` · `annotations/labels_*.json`, 전부 읽기 전용):

| 씬 | 분리 | 오라클 | `main` 라운드 `cells_raw` | `boost` 라운드 `cells_raw` | boost의 `max_diff` |
|---|---|---|---|---|---|
| **scene12** | train | **YES** | **33 605** (`hm_source: fused`) | **50** (`aabb`) | **0.3394** |
| scene07 | **test** | **YES** | 18 874 (`fused`) | **0** (`aabb`) | 0.0 |
| scene08 | val | **YES** | 66 547 (off만 `fused`) | **0** (`aabb`) | 0.0007 |
| scene17 | train | no | 65 833 | 65 833 | 3.2 |
| scene20 | val | no | 60 659 | 60 659 | 2.15 |

- `main` 라운드에는 `heightmap_fused.npy`가 있어(깊이 사이드카 재측정) 정상 발자국이 나온다.
  **boost 라운드에는 그 파일이 없다** — 융합 단계가 boost에 적용되지 않았다.
- 그 결과 **scene12의 boost 프레임 GT는 x = 1.6 m 한 줄, 5 cm × 2.45 m, 50셀짜리 조각**이다
  (오라클 격자 양자화가 계단 챌판 하나에서 남긴 잔차 0.3394 m). 프레임당 양성 셀 2–5개,
  전부 band 3b.
- **감사가 CUE-OFF 주 표적으로 고른 scene12의 strict-H 48장이 전부 이 50셀 조각에 대해 채점됐다.**
  scene12는 가시 단서 8.75로 코퍼스 H씬 최고인데, 정작 GT는 코퍼스 최소다.
- scene07(**test**)·scene08(val)의 boost 프레임은 발자국 0 → `tier none_in_fov` → V/E/H 티어
  회계에서 조용히 사라진다. 헤드라인 수치를 오염시키지는 않지만 **표본이 소리 없이 줄어든다**.

> 이 발견은 CUE-OFF보다 **먼저** 결재란에 올라가야 한다. 본 개정은 이를 기록만 하고
> **아무것도 고치지 않는다** — 라벨을 고치면 동결 모델이 학습한 세계가 바뀐다(절대규칙).

## A1.2 개정 (3건)

**(1) 라벨을 두 벌 만든다. 1차는 계보 충실판.**

| 라벨 세트 | z_off 출처 | 성격 |
|---|---|---|
| **`lineage` (1차)** | 계보 off 라운드(`260820_boost_<band>_off`, 읽기 전용, `aabb`) | 감사의 H recall이 계산된 것과 **같은 GT**. 팔 A가 코퍼스를 비트 재현하는지 검사 가능(G0/G7). scene12 = 50셀 조각(**퇴화 선언**) |
| **`twin` (선언된 민감도)** | **팔 C** (같은 시드·같은 포즈의 무위험 트윈, 내 라운드 안에만 씀) | 정확 포즈·동일 계측기의 진짜 반사실면. `fuse_heightmap.py`를 **내 라운드에만** 적용(정본 무접촉) |

두 세트 모두 산출하고 **둘 다 싣는다**. 판정식(§4.3)은 **각 세트 안에서 따로** 적용하며,
**두 세트의 결론이 갈리면 "판정 불가"로 기록한다**(어느 한쪽을 고르지 않는다).

**(2) 씬 가중치 조정 — scene17을 1차 다리로 승격.**
원문 §2.1은 scene12를 "주 표적"이라 적었다(감사의 판단). A1.1에 비추어 **`lineage` 세트에서
scene12의 결과는 5 cm 조각에 대한 recall**이므로, **플라시보 보정 1차 판정의 주 다리는
scene17**(발자국 65 833셀 · 오라클 없음 · 플라시보 GREEN·18× 보수적 · paired-H 24–33)로 옮긴다.
scene12는 계속 렌더·보고하되 **모든 scene12 수치 옆에 "GT = 50셀 조각" 캐비앗을 붙인다**.
scene20은 원문대로 플라시보 보정 제외(발자국 60 659셀은 건전하므로 B2 외과 결과는 유효).

**(3) 게이트 G7 신설 — 발자국 건전성.**
팔별·씬별 `cells_raw` · `max_diff` · `hm_source`를 표로 뽑고,
`cells_raw < 1000`이면 그 씬-라벨세트에 **DEGENERATE 딱지**를 붙여 보고서 상단에 인쇄한다.
숨기지 않는 것이 목적이고, 자동 중단은 하지 않는다(퇴화 자체가 결과이므로).

---

# AMENDMENT A2 — 2026-08-23T07:42+09:00 (POST-HOC — the results had already been read)

**Legality, stated first and without softening.** A1 was legal because it was written
before a single cut had rendered. **A2 is not.** It is written after
`CUEOFF_RESULT.md` was produced, after D46 read it, and after red-team waves R4 and
R5 attacked it. Anything in A2 that changed a number could have been chosen to
change that number, and the reader is entitled to assume it was until shown
otherwise. Three things limit the damage, and they are checkable:

1. **No hypothesis, arm, threshold, metric or primary-leg lock moves.** τ_op stays
   0.5, the seeds stay {42,43,44}, the checkpoints stay frozen (G6 re-verified),
   `Δ_cue ≥ 0.15 − Δ_placebo` and `Δ_cue < 0.10` stay, `n ≥ 10` stays, and
   §8-3's "do not swap B1↔B2 after seeing the result" is obeyed: scene12 and
   scene20 keep **B2** as primary, scene17 keeps **B1**.
2. **Every A2 clause fixes something a gate or a definition got wrong, not
   something a result got wrong.** Each is listed below with the defect it
   repairs and the direction it pushes the census.
3. **The direction is against us.** Under A2 the primary census goes from
   *0 CUE EVIDENCE / 5 SHORTCUT / 7 UNDECIDED* to
   *0 CUE EVIDENCE / 2 SHORTCUT / 6 NO-EFFECT / 4 UNDECIDED / 12 VOID*. A2 deletes
   claims; the one clause that could add a claim (A2-6) is the one flagged hardest.

## A2-1 `same_sign((0,0,0))` — zero is not a direction

`readout_cueoff.py` v1 L182-186 returned **True** for `all(x == 0)`, so a cell where
the metric never moved was counted as "3/3 seeds agree on a sign" and fell into the
SHORTCUT branch. All five v1 SHORTCUT verdicts in the primary lineage leg were
exactly `(+0.000, +0.000, +0.000)`. That operational definition is nowhere in this
pre-registration.

The same predicate was **also wrong in the opposite direction**, which matters for
judging whether A2-1 was chosen for its effect: `all(x > 0)` is False when one seed
is exactly 0, so `(0.000, +0.083, 0.000)` was rejected as "seeds disagree" even
though no seed disagrees with anything. The corrected definition removes six
verdicts and adds two. It was not tuned.

A2 defines:

- **SAME-SIGN** — at least one non-zero Δ, and all non-zero Δ share a sign. The
  count of non-zero seeds is printed in the label (`SAME-SIGN 1/3nz`), because
  `(+0.667, 0, 0)` and `(+1.000, +0.667, +0.667)` are both same-sign under the
  pre-registered rule and only the second is three seeds agreeing.
- **NO-EFFECT** — every Δ is exactly 0. Its own verdict label, never SHORTCUT.

Every NO-EFFECT verdict prints the one-sided 95 % upper bound on the per-frame flip
rate given 0 flips in *n* paired frames, `p95 = 1 − 0.05^(1/n)`:
n = 24 → **0.117**, n = 12 → 0.221, n = 6 → 0.393. **Seeds do not enlarge n** — the
three seeds read the same frames, so pooling them would manufacture sample size.
At n = 24 the bound (0.117) does **not** resolve this document's own SHORTCUT
threshold (0.10); resolving 0.10 with zero flips needs n ≥ 29. §4.3's declared
minimum detectable effect was therefore optimistic, and every NO-EFFECT cell says so
on its face.

## A2-2 `paired-H < 10` voids the VERDICT, not only the table row

v1 stamped `VOID` on the table row and printed a verdict block underneath it anyway
(R5 D-1: 12 verdict blocks on scene20, four of them positive SHORTCUT calls, from a
scene §4.5-3 had already disqualified). A2 moves the gate inside `verdict()`.

## A2-3 the hazard-off FALSE-ALARM FLOOR is published beside arm C

Every `per_frame.csv` already carried the lineage hazard-off round as its
`toggle_state == "off"` rows. v1's reader dropped them at the door, so arm C's FA was
printed as an absolute number with no baseline. A2 prints the floor, the FA and the
difference. It cuts both ways and both are reported: scene12 gains a far stronger
contrast (rgb **.028 → 1.000**, b2 **.000 → 1.000**), and scene17 loses its claim
outright (**.014 → .042**, i.e. nothing). In the `twin` label set the off rows *are*
arm C, so the floor is constitutively equal to the FA and is suppressed rather than
printed as if it meant something.

## A2-4 `PRIMARY` is keyed by (scene, round stem)

v1 keyed on scene alone, so `260823_cueoff` (band `boost_e`) and `260823_cueoff2`
(band `boost_e2`) — different rounds, different camera bands, different masses —
received the same hard-coded caption constants (R5 D-5).

## A2-5 admissibility is graded on RENDERED pixel mass, not on AABB silhouettes

§3 graded the placebo with `pixel_mass.py`, which projects a world AABB and reports
the clipped hull area. That is an upper bound on a *silhouette*; it cannot see the
shadow, ambient occlusion, GI bounce or shading a removed object was producing —
which `rt_response/F7_HPAIR_PIXDIFF.md` had already shown dominates in this corpus.
**All four grades in §3 are wrong, three of them anti-conservatively.** They are
retracted here and replaced by `RENDER_MASS_SUMMARY.csv` (per-frame `max` channel
absolute difference on the judged frames, thresholds ≥8/255 and ≥32/255, the F7
canon). §3's text is left in place; this table overrides it.

| leg | §3 claimed | rendered ≥32/255 | ratio P/cue | A2 grade |
|---|---|---|---|---|
| s12 `boost_e` P vs B2 | placebo 12–30× larger → conservative | 64,012 / 110,667 | **0.578** | ANTI-CONSERVATIVE |
| s12 `boost_e` P vs B1 | placebo ~3.2× smaller → anti-conservative | 64,012 / 721,912 | **0.089** | SEVERELY ANTI-CONSERVATIVE |
| s12 `boost_e2` P vs B2 | (inherited boost_e's constants) | 51,242 / 127,832 | **0.401** | ANTI-CONSERVATIVE |
| s12 `boost_e2` P vs B1 | (inherited boost_e's constants) | 51,242 / 794,278 | **0.065** | SEVERELY ANTI-CONSERVATIVE |
| s17 P vs B1 | placebo ~18× larger → strongly conservative | 342,269 / 616,554 | **0.555** | ANTI-CONSERVATIVE |
| s20 P vs B2 | "no admissible placebo" | 157,834 / 173,690 | **0.909** | **MATCHED** |
| s20 P vs B1 | "no admissible placebo" | 157,834 / 671,123 | **0.235** | SEVERELY ANTI-CONSERVATIVE |

Grade ladder (fixed here, applied uniformly): ratio ≥ 1.25 CONSERVATIVE ·
≥ 0.80 MATCHED · ≥ 0.25 ANTI-CONSERVATIVE · < 0.25 SEVERELY ANTI-CONSERVATIVE.
**No leg in this study is conservative.** The G0 noise floor these ratios sit on is
8 / 272 / 1 px ≥32/255 (s12 / s17 / s20), i.e. every mass above is 10³–10⁵× the
floor and is real signal.

## A2-6 scene20's placebo is restored — with the conflict of interest declared

§3.3 excluded scene20's placebo from the primary rule. Its stated ground was that
every piece of scene20 mesa furniture measures **0 px in 6/6 strict-H frames**.

**That measurement is correct and A2 does not overturn it.** Verified corner by
corner on the two judged eyes (x = −5.104 and x = −6.716, looking down +X): planters
x = −12.3/−7.0, benches x = −12.9/−9.65/−5.4, streetlights x = −12.6/−7.0/−9.5,
bollards x = −13.6, hedges x = −14.0 … −9.0. Every one is behind the camera or
outside the 62° forward FOV. There is no projection bug in that row of the table.

**The error is in the inference, not the measurement.** The arm that was actually
rendered does not remove furniture. `scenes_cueoff/scene20_diagonal_oblique.py:1046`
under `placebo_remove` removes **backdrop blocks E1 and E2** — a group §3.3's own
table measures at 240 k px = 11.6 % of frame. §3.3 measured a non-removable set,
found it empty, and concluded the arm was impossible, while the code removed a
different, large, in-frame set. On the six judged frames the rendered arm P differs
from arm A by **157,834 px ≥32/255 = 7.61 %**, which is **0.909×** arm B2's rendered
mass: the best-matched cue/placebo pair in this study, on both thresholds.

**The conflict of interest, stated plainly.** We already know what restoring this
placebo does: it converts scene20's b2 leg into the only CUE EVIDENCE candidate the
primary rule has ever produced (Δ_cue − Δ_placebo = +0.667). A restoration decided
after seeing that is not a pre-registration. Three constraints are therefore
attached, and they are binding:

- **(a) The leg is not promoted by A2 alone.** At paired-H = 6 the scene stays VOID
  under §4.5-3, which A2-2 now enforces on the verdict itself. A2-6 changes no
  verdict in the existing rounds.
- **(b) The only route to a verdict is a repair round**, `260823_cueoff_s20fix`
  (§A2-10), whose decision rule is this document's §4.3 unchanged.
- **(c) §3.3's original objection survives and is restated as a limitation**: the E
  blocks stand on the valley floor with their feet cut by the mesa lip, which is the
  same *form* the cue matrix reads as `geometry_silhouette`. A 0.909× mass match does
  not make an object semantically inert. Any CUE EVIDENCE from this leg must be
  reported with that sentence attached.

## A2-7 byte-identical label-set blocks are folded

scene17 and scene20 tier and score identically in both label sets, so their `twin`
blocks were byte-for-byte copies of their `lineage` blocks (R5 D-5: 124 duplicated
lines). Presented as eight scene×label-set blocks they read as eight replications;
they are four. A2 folds them with the reason printed, and the census reports both
the folded and unfolded counts.

## A2-8 G2 is adjudicated at three scopes, and only one of them can void a pair

`GATES_CUEOFF.md` logged **FAIL 8**, all of them `heightmap.npy differs`, and D44
examined one case (s12 P-vs-A, 42 cells) and let the other seven inherit its
verdict. A2 forbids inheritance. The scopes are:

1. **heightmap sha256** — global, geometry-only, what the 8 FAILs actually measured.
2. **`polar_gt` over all on-frames** — scene scope.
3. **`polar_gt` over the PAIRED-H frames** — the judged population.

**Only scope 3 can void a pair**, because §4.2 judges on paired-H frames and on
nothing else, and §4.5-2's criterion is `polar_gt` byte identity, not heightmap
identity. Scope 1 and 2 differences are reported as declared limitations on any
*scene-level* claim. Per-case results are in `G2_ADJUDICATION.csv`.

A separate defect is recorded here because it changes what R4 F5 concluded:
`gates_cueoff.py::load_labels` looked for `labels/<stem>_<arm>.json`, a filename the
labeller has never written (it writes `<set>__<stem>_<arm>__<scene>.json`). G2's
`polar_gt` clause, **G4 and G5 were therefore never evaluated at all**, and would
not have been however many times the battery was re-run. R4 read the 27-minute gap
between the gate run and the label files as the cause; the cause is a path, and the
gap is incidental. Fixed; G4/G5 now run.

## A2-9 G4 reports EVERY tier migration, not only H→E

§4.2 obliged reporting `H→E` migrations. The re-run finds **zero H→E anywhere** —
and finds migrations in the other direction that §4.2 never asked about and that
matter more:

- `scene20 A→B1` and `A→B2`: **`none_in_fov → H` on 3 frames** (cut 0005, all three
  light conditions). Removing the cheek wall re-exposes ground that the labeller's
  twin difference then scores as drop footprint, enlarging `cells_raw` from
  **60,659 to 61,961** and turning 3 GT-empty frames into strict-H frames. This is
  the real content of R4's "different scoresheets" finding.
- `twin / scene12 / boost_e2, A→B1`: **`V → H` on 18 frames.** The intervention
  changes the *tier* of the frame, not only the score on it.

A2 obliges reporting all of them. The pre-registered judged population is unaffected
in every case (see A2-8 scope 3), but a claim about a scene's H census is not.

## A2-10 the repair round `260823_cueoff_s20fix` — declared before it rendered

At the moment of writing, `dataset/260823_cueoff_s20fix_*` contains **0 PNG files**
(checked: `find dataset/260823_cueoff_s20fix_* -name '*.png' | wc -l` → 0, 07:41:57).
The render was queued behind the GPU lock at 07:40:30 and the following is fixed
before any cut of it exists.

- **Scene, arms, seed, toggles, models, checkpoints, τ_op: identical to §2.** Same
  five arms, same `render_configs/scene20_*.json`, same seed 20260821, same frozen
  checkpoints, retraining 0.
- **The only change is the camera band**, from `boost_e2`
  `{"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}` to
  `{"d_min":4,"d_max":8,"h_min":0.25,"h_max":0.6}`, with `--cams 16` instead of 8.
  Lower, nearer eyes graze the mesa lip more often, and grazing concealment is the
  mechanism that makes a frame strict-H in this corpus (`H_CUE_AUDIT.md` §2.2). The
  purpose is to raise paired-H past §4.5-3's n ≥ 10, and nothing else.
- **Consequence accepted:** arm A of this round is no longer a bit-for-bit re-render
  of the shipped corpus, so **gate G0 does not apply to it**. G0 remains verified on
  the original rounds. G1–G7 all apply unchanged.
- **Decision rule: §4.3 verbatim**, with primary `Δ_cue = Δ(A, B2)`, placebo
  correction admissible per A2-6, A2-1/A2-2 counting.
- **Pre-committed outcomes, all four written now:**
  - paired-H ≥ 10 **and** (Δ_cue − Δ_placebo) ≥ 0.15 with same-sign non-zero Δ →
    **CUE EVIDENCE**, reported as the study's first primary-rule positive, carrying
    A2-6(c)'s limitation sentence and a "post-hoc restored placebo" flag.
  - paired-H ≥ 10 and the corrected difference lands in [0.10, 0.15) → **UNDECIDED**.
    It will not be rounded up, and the b2 leg will not be swapped for the rgb leg.
  - paired-H ≥ 10 and Δ_cue < 0.10 with same-sign non-zero Δ → **SHORTCUT**.
  - **paired-H still < 10 → VOID, and scene20 is abandoned as a judged scene.** We
    will not re-roll the camera band a third time looking for a tenth frame. One
    repair attempt, declared here, is the whole allowance.
- **Reporting duty regardless of outcome:** the new paired-H count, the H yield of
  the new band versus the old, and the rendered placebo/cue mass ratio recomputed on
  the new frames, are published whether they help or not.

## A2-12 appending A2 broke `G_PREREG`, and this is how that was handled

Until this amendment existed, `PREREG_CUEOFF.md`'s **mtime** was the registration
time, and `gates_cueoff.py::g_prereg` compared every rendered PNG against it — a
clean mechanical proof that no artifact predated the registration. Appending A2
moved that mtime to 07:43, **later than the 05:01 renders of the original rounds**,
so the naive comparison would now fail on artifacts that are in fact in perfect
order.

The tempting fix is `touch -d '2026-08-23 04:09:35'`. **That was not done**, and it
is recorded here that it was considered and rejected: rewriting a provenance
timestamp to the value that makes the gate pass is the one operation a provenance
gate must never perform, and nobody reading the file afterwards could tell it had
happened.

What was done instead:

1. `g_prereg` now reads the timestamps the **document declares** — the original
   `2026-08-23T03:55:45+09:00` and this amendment's `2026-08-23T07:42+09:00` — and
   checks each round against the registration that covers it. Result: **504 rendered
   frames, all postdating their registration** (456 vs the original, 48 vs A2).
2. It prints a standing note that the **mtime form of the proof is no longer
   available** for the pre-A2 rounds, and points at the independent corroboration on
   record: red-team R4 verified the 03:55-prereg / 05:01-render ordering *before* A2
   existed, from a file it did not write.
3. `PREREG_HASHES.json` now freezes this document's sha256 the way `CKPT_HASHES.json`
   freezes the checkpoints. It was recorded **after** A2 and therefore certifies the
   file only from this moment on — it is not retroactive evidence and is not offered
   as any.

A2-12 is a weakening of the apparatus, not a repair of one, and it is listed with
the others so that the ledger is complete.

**A second custody failure in the same session, recorded for the same reason.** At
~07:33 a diagnostic re-run of the patched gate battery was launched without `--out`.
`gates_cueoff.py`'s default output path was `GATES_CUEOFF.md`, so **the original
05:24:12 gate record was overwritten in place.** There was no backup and this
repository is not under version control. The file has been reconstructed from a read
taken earlier in the same session and is labelled **RECONSTRUCTED, NOT THE ORIGINAL
BYTES**, with the corroborating quotations in `redteam/R4_cueoff.md` §F5 named on its
face; the accidental output is kept outside the audit directory rather than deleted.
The script's default output has been moved to `GATES_CUEOFF_v2.md` and it now refuses
`--out GATES_CUEOFF.md` outright. A tool must not be able to destroy the record it
supersedes by being run with no arguments, and the fact that this one could is a
finding about the apparatus, not a footnote about a typo.

## A2-11 what A2 does NOT repair

- The degenerate scene12 footprint (A1.1) is untouched — fixing it would relabel the
  world the frozen models learned. G7 now separates it from the constitutive zeros of
  arm C and prints a banner.
- Arm C's three different surgeries (§6) remain three different surgeries. A2 adds
  the measurements (`A vs C` = 6.64 % / 4.32 % / 13.55 % / 11.19 % of frame at
  ≥32/255 for s12·e / s12·e2 / s17 / s20) so the reader can see that arm C's
  false-alarm rate tracks the optical size of its surgery.
- **Two of the three scenes are training scenes** (scene12 train, scene17 train,
  scene20 val; zero test scenes). No amendment can repair that, and A2 requires the
  sentence to appear in the results document.

---

# AMENDMENT A2-13 — 2026-08-23T08:30+09:00 · the repair round hits §4.5-2, ruled before inference

**State of the evidence at the moment of writing, so the reader can check what was and
was not known.** `260823_cueoff_s20fix` has finished rendering arms A, B1, B2, P
(arm C is still queued behind the GPU lock). The `lineage` labels for A/B1/B2/P exist.
**No model has been run on this round: `find eval -path '*s20fix*' -name per_frame.csv`
returns 0 at 08:29:15.** So at the time this ruling is fixed we know the ground truth
and the tier census exactly, and we know **no recall number whatsoever**.

## What the labels say

| pair | paired-H | tier migrations | `polar_gt` differs on judged frames | footprint `cells_raw` |
|---|---|---|---|---|
| A vs **B1** | **27** | `V→H_weak` 6 | **6 / 27** | 60,659 → **61,961** |
| A vs **B2** | **27** | none | **6 / 27** | 60,659 → **61,961** |
| A vs **P** | **27** | none | **0 / 27** | 60,659 → 60,659 |

The camera repair worked exactly as A2-10 intended: strict-H yield rose from 6/24
(25 %) to **27/48 (56 %)**, and paired-H = 27 clears §4.5-3's n ≥ 10 with room to
spare. **But a second voiding condition has appeared that A2-10 did not anticipate.**
On six of the twenty-seven judged frames, arms B1 and B2 carry **one extra positive
far-band cell** (3 → 4; `C3b` on cut 0005, `D3b` on cut 0014, in all three light
conditions). That is §4.5-2's exact criterion — `polar_gt` byte identity — failing on
the **judged** population, which A2-8 named as the only scope that can void a pair.

## The ruling

1. **PRIMARY: `Δ(A, B2)` and `Δ(A, B1)` in `260823_cueoff_s20fix` are VOID under
   §4.5-2.** The scene is not judged on its primary leg. This is the literal reading of
   the pre-registration, it is the reading A2-8 fixed before this round existed, and it
   is applied here even though it costs the study its only cue-evidence candidate.
2. **SECONDARY, pre-specified: re-score both arms on ARM A's GT cells.** This was
   written into `CUEOFF_RESULT_v2.md` §2.2 at ~07:55, before these labels existed, as
   the remedy to apply "had they differed". Scoring both arms on one scoresheet is
   precisely §4.5-2's stated *purpose*, so the number is meaningful — but the rule as
   written voids, and a purpose-based reading substituted for a text-based one after
   the fact is how pre-registrations die. It is therefore reported as **SECONDARY /
   EXPLORATORY and never promoted to a primary CUE EVIDENCE verdict, whatever it
   shows.**
3. **SENSITIVITY: the same re-scored on the INTERSECTION GT** (cells positive in both
   arms). Published beside the secondary reading.
4. **`Δ(A, P)` is unaffected** — GT byte-identical on all 27 judged frames — so the
   placebo term is computed normally and the placebo/cue mass ratio is re-measured on
   the new frames.
5. **A2-10's one-repair allowance is spent.** We do not re-roll the camera band again,
   and we do not go looking for a scene20 camera band whose B arms happen not to move
   the footprint.

## What this actually shows, and it is not a nuisance

`cue_railing` in scene20 removes a **cheek wall**: a solid structure standing on the
hazard, whose removal re-exposes ground that the labeller's twin difference
`z_off − z_arm ≥ 0.30` then counts as part of the drop. The footprint grows by 1,302
cells and one far-band polar cell lights up. **The guard is not a separable appearance
cue in this scene; it is load-bearing for the hazard's own definition.**

The pre-registration assumed `cue_railing` was an appearance-only toggle. **For
scene20 that assumption is false**, it was false in the original round (§A2-8 cases
7–8) and it is false in the repair round, and it is false for a geometric reason that
no camera band can fix. That is a finding about the intervention design — the
strongest kind, because it says which questions this apparatus cannot ask — and it
should be reported as one rather than buried as a gate failure.
