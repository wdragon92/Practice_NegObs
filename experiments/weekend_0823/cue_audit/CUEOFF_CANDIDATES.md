# CUEOFF_CANDIDATES — CUE-OFF 대조(GPU-2 / 브리프 §6.2)용 씬 선정과 팔 설정

**목적 한 줄**: "본 표의 frozen 모델이 단서에 의존하는가"를 개입으로 묻기 위해,
**비-test 씬 중** 배선된 `cue_*` 토글이 많고 strict-H 프레임을 가진 씬을 순위와 근거와 함께 고르고,
삼각 팔 {위험+단서 / 위험−단서 / 무위험+단서}의 실행 가능한 설정을 준다.

- **작성**: Claude Code (CPU-1) 2026-08-23 · **소비자**: GPU-2 실행 세션
- **왜 이 문서가 필요한가**: `H_CUE_AUDIT.md` §6 — 관찰(층화)로는 결론이 나지 않는다.
  단서 축과 시점 축이 코퍼스 안에서 분리되지 않기 때문이다.
  **같은 씬·같은 포즈에서 단서만 지우면 시점 축이 자동으로 고정된다.**

---

## 1. 전제 — `cue_*` 토글의 실제 배선 상태 (33씬 전수)

`SCENE_CONFIG` 키는 전 씬 공통 6개(`cue_railing` · `cue_tactile` · `cue_nosing` ·
`cue_material_break` · `cue_sign` · `cue_scene_dressing`) + 위험 토글 4종(`hazard_stairs` ·
`hazard_shadow_band` · `hazard_asphalt_patch` · `hazard_flush_grating`) + 씬 고유 조건 4종
(`snow_cover` C1 · `leaf_cover` C2 · `wet_surface` C4 · `grass_overhang` D3) = **14키**(PS §2와 일치).
여기에 D25에서 sceneC2·N3에만 추가된 `keep_dressing`이 15번째로 존재한다.

**"배선됨"의 정의**: 씬 파일 안에서 그 키를 실제로 읽는 코드(`cfg["key"]` 참조)가 1회 이상 존재.
선언만 있고 읽는 코드가 없으면 **사문화(dead)** — 토글을 꺼도 그림이 바뀌지 않는다.
전수 결과는 `scene_toggle_inventory.csv`(33행). 33씬 기준 집계:

| 키 | ON·배선 | OFF·배선 (끄기용으로는 무의미, 켜면 단서 신설) | 사문화(선언만) |
|---|---|---|---|
| `cue_scene_dressing` | **33** | 0 | 0 |
| `cue_material_break` | **32** | 0 | 1 (s19) |
| `cue_railing` | **15** | 11 | 7 |
| `cue_nosing` | 8 | 14 | 10 |
| `cue_sign` | **5** (s01·s08·s11·s13·s14) | 1 (s07) | **27** |
| `cue_tactile` | **3** (C1·C4·D4 — 전부 비-H 씬) | 17 | 13 |

읽는 법:
- **끌 수 있는 단서의 대부분은 `cue_scene_dressing` + `cue_material_break`다**(거의 전 씬 ON·배선).
- `cue_sign`은 27씬에서 **선언만 있고 읽는 코드가 없다** — 끄든 켜든 그림이 안 바뀐다.
  매트릭스가 "배선된 토글이 렌더 믹스에 투입된 적 없다"(B1, 14씬)고 지적한 것과는 **다른 층위의 문제**이니
  섞지 말 것: 여기는 *코드에 아예 없다*는 뜻이다.
- `cue_railing` ON·배선 15씬 중 **strict-H를 가진 것은 scene12와 scene20 둘뿐**이다.
- **scene14의 가드는 토글이 아니다**: matrix의 `railing_or_guard`(scene14, 중)는 비행 측면의
  **경사 파라펫**이고, `cue_railing`(기본 False)은 그 위에 파이프 레일을 *추가*하는 키다(GT-78이 철회).
  즉 scene14는 test인 것과 무관하게 **가드 어블레이션 자체가 불가능**하다.

## 2. 후보 풀 — 조건을 만족하는 씬은 4개뿐이다

조건 = (a) 비-test, (b) strict-H 프레임 보유, (c) 배선된 `cue_*` 토글 보유.
`H_CUE_AUDIT.md` §2.1에 따라 strict-H는 6씬에서만 나오고 그중 2씬(scene14·scene15)이 test다.
**따라서 후보 풀은 아래 4개가 전부다** — 선택지가 아니라 열거다.

| 씬 | 분리 | H | 평균 가시 단서 (0–13) | ON·배선 `cue_*` | H가 나오는 카메라 밴드 |
|---|---|---|---|---|---|
| **scene12** 리버사이드 데크 | train | **48** | **8.75 (코퍼스 H씬 최고)** | railing · material_break · scene_dressing | `boost_e` 24/24 H · `boost_e2` 24/24 H |
| **scene20** 사교 30° | val | 6 | 2.00 (최저) | railing · material_break · scene_dressing | `boost_e2` 6 H / 24컷 |
| scene17 한강 램프쌍 | train | 33 | 6.27 | material_break · scene_dressing (**난간 자체가 없음**) | `boost_h` 24/24 H · main 9 H |
| scene09 호안 계단 | train | 60 | 4.25 | material_break · scene_dressing | `boost_h` 24/24 H · `boost_e` 21 H |

---

## 3. 권고 — scene12(주) + scene20(외과적) + scene17(무가드 대조, 여력)

### 3.1 순위 1 — **scene12** (주 표적)

- **왜**: 후보 중 유일하게 **가드·재질·드레싱 세 토글이 모두 ON·배선**이고, H 프레임이 48장이며,
  가시 단서 수가 8.75로 코퍼스 H씬 최고다. 즉 **지울 것이 가장 많고, 지웠을 때 남는 것이 가장 적다.**
- **각 토글이 지우는 단서** (근거: `dropoff_cue_matrix_v1` scene12 항 + 씬 파일):

  | 토글 → False | 코드가 지우는 것 | 죽는 13단서 | 매트릭스 강도 |
  |---|---|---|---|
  | `cue_railing` | `build_railing` (씬 파일 1922–1933행): Ø120 포스트 + Ø80 상·중 레일, y=1.15, x −18…0 | `railing_or_guard` | **강(S)** — 9프리셋 전부 비차폐. 본 감사 M1: **H 48/48 프레임에서 화면 안** |
  | `cue_scene_dressing` | `build_skyline` + `build_dressing` (1943행~): 갈대·벤치·가로등·자전거도로 백선·교량·아파트 배경 | `vegetation_edge`(M, 비차폐) · `signage_or_marking`(w, 자전거도로 백선) · `geometry_silhouette` 일부(밑동 잘린 교각) · `far_side_visible_depth` 일부 | M·w |
  | `cue_material_break` | 계단·데크 재질을 `deckwood` → `gravel`로 통일 (1849·1895행) | `texture_change_across_edge` | **강(S)** |

- **기대 효과(사전 등록)**: 가시 단서 8.75 → 대략 3–4(수면·에지선·정반사만 잔존).
  단서 의존이면 H recall이 큰 폭으로 붕괴해야 한다. 유지되면 씬 정체성/기하 사전확률이 근거라는 뜻.
- **위험 기하 불변성**: 가드는 낙차를 가리는 물체가 **아니다**(낙차는 데크 엣지 자기가림).
  따라서 티어 뒤집힘 위험이 후보 중 가장 낮다. 그래도 §5 게이트는 전부 돌린다.
- **렌더 규모**: 2밴드 × 24컷 = **48컷/팔**. 실측 4.0 s/컷(`variation.json` `sec_per_cut`) → 렌더 3.2분/팔.

### 3.2 순위 2 — **scene20** (가장 날카로운 단일 단서 개입)

- **왜**: 매트릭스가 scene20의 h0.3 증거를 **"치크월(가드) 웨지 실루엣이 사실상 유일"**이라고 판독했고
  (`railing_or_guard` 강, 9프리셋 전부 비차폐 · `geometry_silhouette` 강),
  본 감사에서 **val H 6장의 recall이 RGB·Depth·B2 전부 1.000**이다(§4.5).
  **천장에서 시작하므로 떨어지는 것밖에 없고, 단일 토글로 "유일 증거"를 지울 수 있다.**
- **지우는 것**: `cue_railing=False` → `build_stair_walls`(748행, 8프림) 소거 →
  `railing_or_guard`(S) + `geometry_silhouette`(S)의 주 성분이 함께 사라진다.
  scene20의 가시 단서는 이미 2.00으로 최저라 **거의 0으로 간다.**
- **주의 2건 (반드시 기록)**:
  1. `cue_railing=False`는 낙엽 스캐터 인셋도 바꾼다(1047행: 벽이 없으면 전 폭 사용) —
     **드레싱 부수효과**. 기하 불변이지만 픽셀은 바뀐다. 로그에 남길 것.
  2. 치크월은 비행 측면에 붙어 있어 **제거 시 계단 픽셀이 노출될 수 있다** → H가 E로 이동할 수 있다.
     이건 실패가 아니라 결과다. §5의 티어 재도출에서 **이동 프레임 수를 반드시 보고**한다.
- **표본 보강(권고)**: 기본 `boost_e2` 밴드는 24컷 중 H가 6장뿐이다. 격리 라운드에서
  `NEGOBS_CAM_BAND_OVERRIDE='{"d_min":4,"d_max":8,"h_min":0.25,"h_max":0.6}'`로 h0.3 대역을 집중시키면
  H 수율이 오른다. scene20은 **val**이라 test 불가침(브리프 §3-1)에 걸리지 않는다.
  단 **모든 팔이 동일 밴드·동일 시드**여야 한다.
- **렌더 규모**: 1밴드 × 24컷 = **24컷/팔**, 4.2 s/컷 → 1.7분/팔.

### 3.3 순위 3 — **scene17** (무가드 대조, 여력 있을 때)

- **왜**: scene17에는 **난간·점자·노징이 설계상 아예 없다**(below-code reality).
  그래서 "가드 어휘 없이도 단서를 읽는가"를 볼 수 있는 유일한 H씬이다.
  `cue_scene_dressing=False`가 지우는 것은 가로등 폴·km 표지판 — 매트릭스가
  "밑동이 가려진 채 마루 지평을 뚫는 수직물 = 간접적 하부 레벨 힌트"로 판독한 바로 그것들
  (`geometry_silhouette` M · `signage_or_marking` w), `cue_material_break=False`는
  콘크리트↔포장 톤 대비(`texture_change_across_edge` w)를 죽인다.
- **기대 효과**: 원래 h0.3_d10에서 이미 bare-H(6장)인 씬이라, **드레싱을 지우면 h0.9 대역도 bare로 내려간다** —
  "단서를 지웠을 때 bare-H가 늘어난다"를 **감사 표와 개입이 같은 축에서 만나는** 유일한 케이스.
- **렌더 규모**: `boost_h` 밴드 1개 × 24컷(24/24가 H) = **24컷/팔**, 4.7 s/컷 → 1.9분/팔.

### 3.4 채택하지 않은 것 — **scene09** (근거를 남긴다)

H 60장으로 수는 가장 많지만, scene09의 강 단서는 `water_surface`·`far_side_visible_depth`이고
**이 둘은 어떤 `cue_*` 토글에도 물려 있지 않다**(`build_river`는 항상 ON, 수평 폐합용).
배선된 ON 토글은 `cue_scene_dressing`(정자·데크 말뚝·갈대·먼 숲)과 `cue_material_break`뿐이라
**지워도 주 증거가 남는다 = 기대 효과가 가장 작다.** 여력이 남으면 순위 4로 돌린다.

---

## 4. 삼각 팔 설정 (그대로 복사해 쓸 수 있는 형태)

렌더 설정은 `NEGOBS_SCENE_CONFIG` 환경변수에 실리는 **JSON 한 줄**이며 `SCENE_CONFIG`에 병합된다
(`scripts/run_data_render.py:999`, 사용례 `scripts/rounds/run_260819_main.sh:231`).
격리 라운드 이름 제안: **`260823_cueoff`** · 설정 디렉터리 제안:
`experiments/weekend_0823/cue_audit/render_configs/`(정본 `experiments/mainrun_0819/render_configs/`는 무수정).

### 4.1 팔 정의

| 팔 | 이름 | 뜻 | scene12 설정 JSON |
|---|---|---|---|
| **A** | `hz1_cue1` | 위험 + 단서 (기준선) | `{"hazard_stairs": true}` |
| **B1** | `hz1_cue0` | 위험 유지, **단서 전부 제거** | `{"hazard_stairs": true, "cue_railing": false, "cue_material_break": false, "cue_scene_dressing": false}` |
| **B2** | `hz1_rail0` | 위험 유지, **가드만 제거** (해석 가능한 단일 단서 개입) | `{"hazard_stairs": true, "cue_railing": false}` |
| **C** | `hz0_cue1` | **무위험 + 단서 유지** (= 신off) | `{"hazard_stairs": false, "keep_dressing": true}` — §4.3의 코드 이식 필요 |

scene20: A `{"hazard_stairs": true}` · B2 `{"hazard_stairs": true, "cue_railing": false}` ·
B1 `{"hazard_stairs": true, "cue_railing": false, "cue_material_break": false, "cue_scene_dressing": false}` ·
C `{"hazard_stairs": false, "keep_dressing": true}`.
scene17(난간 없음이라 B2 없음): A · B1 `{"hazard_stairs": true, "cue_material_break": false, "cue_scene_dressing": false}` · C.

> **단서를 새로 켜는 팔은 넣지 않는다.** scene20의 `cue_tactile`은 배선돼 있지만 OFF가 기본이고,
> 켜면 **에지 위 마킹 신설** = 씬 난이도 정체성 변경 → 브리프 §3-4(사인·표지 신설 = 임의 확정 금지)에 걸린다.
> 결재란 안건으로만 올린다.

### 4.2 포즈 재현 (팔 간 완전 동일 포즈가 성립 조건)

| 밴드 | 시드 | cams | `NEGOBS_CAM_BAND_OVERRIDE` | 쓰는 씬 |
|---|---|---|---|---|
| main | 20260819 | 8 | (없음) | 참고용 |
| boost_h | 20260820 | 8 | `{"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}` | scene17 |
| boost_e | 20260820 | 8 | `{"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}` | scene12 |
| boost_e2 | 20260820 | 8 | `{"d_min":4,"d_max":9,"h_min":0.3,"h_max":0.9}` | scene12 · scene20 |

조명 조건은 각 씬의 기존 3종(`variation.json` `conds`)을 그대로 쓴다.

> **경고(D25 계보)**: 포즈 샘플러는 `ground_z`를 씬 AABB 하향 레이로 잡는다(CAM_CONVENTION §1).
> 오브젝트를 지우면 **카메라 지면 기준이 움직일 수 있고**, 실제로 sceneC2 구off에서
> 지면 기준이 0.130 → 0.0163 m로 이동해 **트윈 쌍이 0개**가 된 전례가 있다(`ctrl_dressing/CTRL_TABLE.md`).
> 따라서 §5-③ 포즈 동일성 게이트는 **선택이 아니라 성립 조건**이다.

### 4.3 팔 C만 코드 이식이 필요한 이유와 방법

scene12·17·20 모두 `build_railing` / `build_dressing` / `build_stair_walls` 호출이
`if cfg["hazard_stairs"]:` **안쪽**에 있다(scene12: 2066·2073–2076행 / scene17: 2721–2734행 /
scene20: 880행은 `build_diagonal` 내부, 1360–1363행). 그래서 `hazard_stairs=False`만 주면
**구off(위험+장식 동반 제거)**가 되고 신off가 되지 않는다.

**이식 원본**: `scenes/batch1/sceneC2_leaf_stairs.py` 496–520행 —
모듈 스코프 상수 `KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))` +
모순 설정에 대한 **FATAL 종료**(`keep_dressing=True` ∧ `hazard_stairs=True`는 즉시 SystemExit) +
장식 호출을 `if cfg["hazard_stairs"] or KEEP_DRESSING:`로 완화 +
하부 앵커 드레싱은 채워진 지면(z=0)에 올려붙이기.

**이식 대상 경로**: `experiments/weekend_0823/cue_audit/scenes_cueoff/<scene>.py`(정본 씬 무수정 —
브리프 §3-2). 45분 룰에 걸리면 **A·B1·B2만으로 착지해도 1차 질문에는 답이 나온다**;
C는 FA 해석(“장식만 있어도 발화하는가”)의 세 번째 다리이고, sceneC2 신off FA .681의
**비-test 재현**이라는 별도 가치가 있다.

---

## 5. 착수 전 게이트 (하나라도 실패 = 중단·기록·롤백)

1. **1프레임 실렌더 스모크** — 브리프 §3-6. 부팅 후 코드로 검증한다.
2. **위험 기하 불변 해시** — 팔 A와 팔 B의 `heightmap_meta.json` · `heightmap_fused_meta.json`이
   비트 동일해야 한다. 프레임별 `polar_gt`도 동일해야 한다. 다르면 `cue_*`가 기하를 건드린 것 = 규약 위반.
3. **포즈 동일성** — 팔 간 컷별 `cam.eye`·`yaw`·`pitch`·`hfov` 차이 < 1e-6.
   실패 시 원인(=`ground_z` 이동) 기록 후 중단(§4.2 경고).
4. **티어 재도출** — 팔별 V/E/H/H_weak/none_in_fov 5범주 카운트를 다시 뽑는다(PS §6-7).
   H→E 이동이 있으면 **이동 프레임 수를 보고**하고, 주 판정은 **양 팔에서 모두 H인 프레임(paired)** 위에서 한다.
5. **평가는 추론만** — frozen 체크포인트 무수정, 재훈련 0, 3시드, τ_op 0.5
   (`experiments/dayrun_0820/runs/v2/{rgb,depth,b2}_s{42,43,44}/best.pt`).

## 6. 판독 사전 등록 (결과 보기 전에 고정 — 브리프 §6.2와 동일 취지)

| 관측 (paired H 프레임 기준, A → B) | 판독 |
|---|---|
| H recall 붕괴 (3시드 전부 하락, Δ가 시드 산포보다 큼) | **개입 증거: 모델이 단서를 쓴다** |
| H recall 유지 (Δ ≈ 0) | **지름길 신호** — 프레임에서 정당한 단서를 지워도 발화가 남는다 |
| 시드 부호 갈림 | 판정 불가 → 표본(밴드·씬) 확대 후 재시도 |
| 팔 C(무위험+단서)에서 FA가 높다 | **"단서 어휘만으로 발화"의 비-test 재현** (sceneC2 신off .681의 일반화) |

보조 판독: **B2(가드만 제거)와 B1(전부 제거)의 차이**가 곧 가드 단독 기여분이다.
이 값이 B1 전체 효과의 대부분이면 "가드 어휘 = 낙차"(매트릭스 지름길 패밀리 2위, 14씬)의
**직접 정량**이 된다 — 논문 본문 후보.

## 7. 비용 요약

| 씬 | 팔 | 컷/팔 | 실측 s/컷 | 렌더 시간(팔당) | 비고 |
|---|---|---|---|---|---|
| scene12 | A·B1·B2·C | 48 (2밴드) | 4.0 | ~3.2분 | Isaac 부팅이 컷 시간보다 크므로 실질 5–7분/팔로 잡을 것 |
| scene20 | A·B1·B2·C | 24 (1밴드) | 4.2 | ~1.7분 | 표본 보강 밴드 쓰면 동일 |
| scene17 | A·B1·C | 24 (1밴드) | 4.7 | ~1.9분 | |

권고 세트(scene12 4팔 + scene20 4팔 + scene17 3팔) 총 렌더 ≈ **11개 팔 · 400컷 미만**.
추론은 3모델 × 3시드 × 수백 프레임으로 분 단위. **브리프의 "렌더 소량 + 추론 ~1h" 상자 안에 들어간다.**
