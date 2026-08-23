# CUE_COVERAGE — `cue_*` 배선 로컬 커버리지 감사 (P-3 CPU / DZ §12-6)

> **[정정 배너 — 2026-08-23 추가 · W1-B2 / DECISIONS D75 ③]** **이 문서 §0-3은 처음부터 옳았다.**
> `cue_material_break` **32/33 토글 가능**과 §2.1의 `ON (비가드)` 표기가 정확한 값이다.
> 틀린 것은 **`code/hazgate.json`에서 파생된 하류 표들**이다 — `hazgate.py`가 cue 읽기를 `if` 문
> 조건절에서만 수집해 `mtl = M[a] if cfg["cue_material_break"] else M[b]` 형태의 **삼항 읽기 23칸**
> (T 20 · Ta 2 · N 1)을 "배선無"로 오기록했고, 그 손실이 W0 프로브 → W1-D 재판정 →
> W1D_REPORT §6.6 `ON·배선` 열 → W1-B 레시피까지 4단계를 타고 가 **T키 \|r\| = 0.3100**(VG-09 위반)을
> 만들었다(W1B_REPORT §8.1 · §7). 수리본은 `code/hazgate_full.json`(`hazgate.py --mode full`)이고
> 옛 계보 재현용으로 `code/hazgate.json`은 그대로 둔다. 참고: §0-2가 이미 정정한
> `cfg.get("key")` 미검출 11칸과 **같은 계통의 오류가 2세대째다**.

**목적 한 줄**: v3 2×2 렌더 계획(P-5)과 가드 구조물/장식 분류(P-3 렌더분)의 **선행 입력**으로,
디스크에 실제로 존재하는 모든 씬 파일의 `cue_*` 배선 상태·제거 대상 프림·해저드 기하 결속을
전수 열거한다.

- **작성**: Claude Code (CPU, P-3) · 2026-08-23 · **소비자**: P-5 렌더 계획서 · P-3 렌더 분류 큐
- **방법**: CPU 전용. Isaac 미기동·GPU 미사용·git 명령 미사용. 씬 `.py` 46개를 **AST 파싱**해
  `SCENE_CONFIG` 기본값, 키를 읽는 코드(`cfg["k"]` · `cfg.get("k")` · 삼항/kwarg 형태 전부),
  if-가드 본문의 호출 함수와 생성 프림 경로, 그리고 가드가 `hazard_*` 분기 **안**에 있는지를 뽑았다.
- **정본 참조**: 단서 13키 = `Docs/reports/dropoff_cue_matrix_v1.md` · 분리 =
  `experiments/dayrun_0820/split_v2_full.json` · 코퍼스 = `experiments/dayrun_0820/dataset_manifest_v2_full.json`
- **정본 파일 무수정.** 본 문서와 그 근거 스크립트 외에 아무것도 쓰지 않았다.

> **한계 (한 번만 적는다).** 이것은 **씬 설정 판독**이다. "구조물이냐 장식이냐"의 최종 판정은
> 설정만으로는 나지 않는다 — `CUEOFF_RESULT_v2.md` §6.3이 확정한 기계 판정은
> **두 팔 라벨러의 `cells_raw` 차이**다. 본 문서는 (a) 설정만으로 확정 가능한 칸을 확정하고
> (b) 나머지를 **렌더 분류 큐**로 넘긴다. §3-(b)가 그 큐다.

---

## 0. 헤드라인 (읽고 나갈 여섯 줄)

1. **디스크 위 씬 정의 파일은 46개**(`SCENE_CONFIG = {` 보유 기준). 그중 **정본 드라이버가
   해석할 수 있는 것은 33개뿐**이다 — `scripts/run_data_render.py:53 scene_files()`가
   `scenes/{main,batch1}/scene*.py`만 글롭한다. 나머지 13개(프로브 3 · archive_v3 7 · 주말 격리본 3)는
   `--scene-proc <file>` 직접 호출로만 렌더된다.
2. **주말 인벤토리(`scene_toggle_inventory.csv`)에 오탐 11칸(6씬)이 있다.** 그 표는
   `cfg["key"]` 형태만 세고 **`cfg.get("key")` 형태를 못 봤다.** 실제로는 배선돼 있는데 "사문화"로
   찍힌 칸: s05 railing·tactile·nosing·sign / s19 railing·tactile·nosing / s02·s09·s16·s21 sign.
   본 문서 §2.1이 정정본이다.
3. **끌 수 있는(=default True + 배선) 토글 집계(33씬):** `cue_scene_dressing` **33** ·
   `cue_material_break` **32** · `cue_railing` **16** · `cue_sign` **9** · `cue_nosing` **8** ·
   `cue_tactile` **3**. 즉 "≥1개 끌 수 있는 단서"는 **33/33 전 씬**이다 —
   주말의 "3씬뿐"은 배선 부족이 아니라 **strict-H 프레임 부족**이 만든 수다(§3-a).
4. **13 단서 중 6개는 코퍼스 어디에도 토글이 없다** — `edge_line_contrast`(부분 예외) ·
   `shadow_line` · `far_side_visible_depth` · `water_surface` · `specular_change` ·
   `geometry_silhouette`(부분 예외). B팔(단서 제거)이 원리적으로 건드릴 수 없는 축이다(§2.3).
5. **`cue_material_break`가 유일하게 "구성상 기하 불변"이 보증되는 토글이다** — 32씬 중 **24씬**에서
   프림을 만들거나 지우지 않고 **재질 바인딩만** 바꾼다. 나머지 8씬(s05·s06·s11·s18·D4·N1·N2·N5)은
   프림을 만들므로 큐로 간다.
6. **C팔(무위험+단서)은 현 코퍼스에서 8씬만 무개조로 성립한다**(s01·s04·s09·C2·N1·N3·N4·N5).
   **25씬은 단서 빌더가 `hazard_*` 분기 안에 있어** `hazard_stairs=False`가 단서까지 같이 지운다
   (=구off). `keep_dressing` 이식이 필요하다. 그리고 무개조 8씬 중 **C2·N3는 test-core**다.

---

## 1. 씬 인벤토리 — 디스크 위 전수

### 1.1 그룹별 요약

| 그룹 | 경로 | 파일 수 | 정본 드라이버 해석 | v2 코퍼스 |
|---|---|---|---|---|
| **본편 33씬 라이브러리 (a)** | `scenes/main/scene*.py` | 21 | ✅ `scene_files()` | ✅ 전량 |
| **본편 33씬 라이브러리 (b)** | `scenes/batch1/scene*.py` | 12 | ✅ `scene_files()` | ✅ 전량 |
| 프로브 씬 | `scenes/probe/probeH*.py` | 3 | ❌ (`probe_driver.py` 별도) | ❌ |
| 구판 아카이브 | `scenes/archive_v3/scene*.py` | 7 | ❌ | ❌ |
| 주말 CUE-OFF 격리본 | `experiments/weekend_0823/cue_audit/scenes_cueoff/*.py` | 3 | ❌ (`--scene-proc`) | ❌ |
| **합계** | | **46** | **33** | **33** |

`.gitignore`에 `scenes/` 규칙은 **없다**(무시되는 것은 `assets/*` · `dataset/` · `look_check/` 계열).
DZ §12-6의 "씬 설정은 git 미포함"은 최소한 `scenes/`에 대해서는 성립하지 않는다 —
다만 감사를 **디스크 기준**으로 수행하라는 지시 자체는 그대로 따랐고, 결론은 어느 쪽이든 동일하다.

### 1.2 본편 33씬 — 파일 경로 · 분리 · v2 코퍼스 지위

분리 정본 = `experiments/dayrun_0820/split_v2_full.json` (v2 체크포인트 9개 전부가 이 파일을 씀 —
`runs/v2/*/config.json`의 `split` 필드로 확인). 프레임 수 = `dataset_manifest_v2_full.json`
(2,832 프레임 · 라운드 `260819_main_{on,off}` + `260820_boost_{h,e,e2}_{on,off}`).

| 씬 | 파일 (모두 `scenes/…` 상대) | 분리(v2 정본) | v2 프레임 | strict-H | 비고 |
|---|---|---|---|---|---|
| scene01 | `main/scene01_campus_stairs.py` | train | 48 | 0 | |
| scene02 | `main/scene02_underpass.py` | train | 48 | 0 | |
| scene03 | `main/scene03_riverbank.py` | train | 144 | 0 | boost |
| scene04 | `main/scene04_parktrail.py` | train | 144 | 0 | boost · **사용자 보류 씬** |
| scene05 | `main/scene05_amphitheater.py` | **test-core** | 144 | 0 | boost |
| scene06 | `main/scene06_overpass_spiral.py` | train | 48 | 0 | |
| scene07 | `main/scene07_temple_stone_path.py` | **test-core** | 144 | 0 | boost · G7 재라벨 영향 |
| scene08 | `main/scene08_sunken_plaza.py` | val | 96 | 0 | |
| scene09 | `main/scene09_ghat_riverfront.py` | train | 144 | **60** | boost |
| scene10 | `main/scene10_park_deck_switchback.py` | train | 48 | 0 | |
| scene11 | `main/scene11_footbridge_stairs.py` | **hold** | 48 | 0 | 건물 재작업 큐 |
| scene12 | `main/scene12_riverside_deck.py` | train | 144 | **48** | boost · **H는 퇴화 풋프린트의 산물**(§3-a 주) |
| scene13 | `main/scene13_apartment_parking_entry.py` | **hold** | 48 | 0 | |
| scene14 | `main/scene14_grandstair_illusion.py` | **test-core** | 144 | **60** | boost · 가드=구조물(§2.4) |
| scene15 | `main/scene15_alley_labyrinth.py` | **test-core** | 144 | **36** | boost · 건물 재작업 큐 |
| scene16 | `main/scene16_canopy_shadow.py` | train | 48 | 0 | |
| scene17 | `main/scene17_ramp_pair_hangang.py` | train | 144 | **33** | boost |
| scene18 | `main/scene18_wavy_artstair.py` | **test-core** | 144 | 0 | boost |
| scene19 | `main/scene19_fan_winder.py` | **hold** | 48 | 0 | 판정 그리드 d{2,3.5,5} |
| scene20 | `main/scene20_diagonal_oblique.py` | val | 144 | **6** | boost · 가드=구조물(실측) |
| scene21 | `main/scene21_monumental_selfocclude.py` | train | 48 | 0 | 건물 재작업 큐 |
| sceneC1 | `batch1/sceneC1_snow_stairs.py` | train | 96 | 0 | `snow_cover` |
| sceneC2 | `batch1/sceneC2_leaf_stairs.py` | **test-core** | 48 | 0 | `leaf_cover` · **`keep_dressing` 기배선** |
| sceneC4 | `batch1/sceneC4_wet_stairs.py` | train | 144 | 0 | boost · `wet_surface` |
| sceneD1 | `batch1/sceneD1_loading_dock.py` | train | 48 | 0 | |
| sceneD2 | `batch1/sceneD2_floor_opening.py` | train | 48 | 0 | |
| sceneD3 | `batch1/sceneD3_drainage_channel.py` | val | 48 | 0 | `grass_overhang` |
| sceneD4 | `batch1/sceneD4_subway_platform.py` | **hold** | 48 | 0 | |
| sceneN1 | `batch1/sceneN1_shadow_band.py` | train | 48 | 0 | 무낙차 · `hazard_shadow_band` |
| sceneN2 | `batch1/sceneN2_asphalt_patch.py` | train | 48 | 0 | 무낙차 · `hazard_asphalt_patch` |
| sceneN3 | `batch1/sceneN3_trompe_loeil.py` | **test-core** | 48 | 0 | 무낙차 · **`keep_dressing` 기배선** |
| sceneN4 | `batch1/sceneN4_downhill_ramp.py` | train | 48 | 0 | 무낙차 · `hazard_stairs` |
| sceneN5 | `batch1/sceneN5_flush_grating.py` | train | 48 | 0 | 무낙차 · `hazard_flush_grating` |

**분리 집계**: train 19 · val 3 · **test-core 7**(scene05·07·14·15·18·C2·N3) · hold 4(scene11·13·19·D4).
strict-H 243장은 **6씬**에서만 나온다(`H_CUE_AUDIT.md` §0-1): s09 60 · s12 48 · s14 60 · s15 36 · s17 33 · s20 6.

> **분리 버전 주의.** `split_v1.json`(mainrun)·`split_v2.json`(dayrun)·`split_v2_full.json`이 셋 다
> 디스크에 있고 **train/val 배정이 서로 다르다**(예: scene08 = v1 train / v2 train / v2_full **val**,
> scene17 = v1 train / v2 **val** / v2_full train). v2 체크포인트가 실제로 학습한 것은
> **`split_v2_full.json`** 이고 위 표는 그것을 쓴다. 주말 `CUEOFF_CANDIDATES.md`의 분리 열도 같은 파일이다.
> **test-core 7씬은 세 버전에서 동일**하므로 헤드라인 비교는 영향받지 않는다.

### 1.3 비-라이브러리 씬 13개

| 씬 | 경로 | 성격 | v3에서의 쓸모 |
|---|---|---|---|
| probeH1 / H2 / H3 | `scenes/probe/probeH{1,2,3}_*.py` | `hazard_hole` 단일키 · 441–528행의 미니 씬 | **test-ext 신설 씬의 최소 템플릿.** 프림 수가 적어 2×2 배선·해시게이트 검증이 싸다 |
| archive_v3 7종 | `scenes/archive_v3/scene{06,07,08,10,11,12,13}_*.py` | v3 구판(600–850행). 현 scene06·07·08·10·11·12·13이 대체 | **폐기 대상.** 같은 `sceneNN` 키를 쓰므로 새 드라이버가 실수로 잡지 않도록 주의 |
| cueoff 격리본 3종 | `experiments/weekend_0823/cue_audit/scenes_cueoff/scene{12,17,20}_*.py` | 정본 복사본 + `keep_dressing`/`placebo_remove` 배선 | **v3 2×2 배선의 정본 레퍼런스**(§4.2) |

격리본은 kit 파일을 **심링크**로 끌어 쓴다(`scene_common.py` · `ground_kit.py` … 전부 `../../../../`).
따라서 씬 파일 하나만 복사하면 격리본이 성립한다 — v3에서 팔별 격리본을 만들 때 같은 패턴을 쓰면 된다.

---

## 2. 씬 × 단서 — 배선 상태 · 제거 대상 · 해저드 결속

### 2.1 마스터 표 (33씬 × 6키)

**상태 코드**
- `ON` = 기본값 `True` **이면서** 읽는 코드 존재 → **끄면 단서가 사라진다**(B팔에 쓸 수 있다)
- `off` = 읽는 코드는 있으나 기본값 `False` → **끄는 용도로는 무의미**(켜면 단서 신설 = 난이도 정체성 변경)
- `사문` = 선언만 있고 읽는 코드가 없다 → 켜도 꺼도 그림이 안 바뀐다
- `—` = 키 자체가 선언돼 있지 않다

**결속 코드** (그 키의 빌더가 `hazard_*` 분기 안에 있는가 — 호출 그래프까지 추적)
- `자유` = 해저드와 무관하게 지어진다 → `hazard=False`에서도 단서가 남는다(**C팔 가능**)
- `HZ` = 전부 해저드 분기 안 → `hazard=False`가 단서까지 지운다(**구off**, C팔 불가)
- `HZ부분` = 일부만 해저드 분기 안

| 씬 | railing | tactile | nosing | material_break | sign | scene_dressing | C팔 결속 |
|---|---|---|---|---|---|---|---|
| scene01 | **ON** 자유 | off | — | **ON** 자유 | **ON** 자유 | **ON** 자유 | **자유(무개조 C팔 가능)** |
| scene02 | **ON** HZ | off HZ | **ON** HZ | **ON** (비가드) | **ON** HZ | **ON** HZ부분 | HZ |
| scene03 | off 자유 | off 자유 | off 자유 | **ON** (비가드) | 사문 | **ON** **HZ** | HZ |
| scene04 | off 자유 | off 자유 | off 자유 | **ON** (비가드) | 사문 | **ON** 자유 | **자유** |
| scene05 | off 자유 | off 자유 | off 자유 | **ON** HZ부분 | off 자유 | **ON** 자유 | HZ부분(LipCurb만) |
| scene06 | **ON** HZ | off HZ | off HZ | **ON** 자유 | 사문 | **ON** 자유 | HZ부분 |
| scene07 | off HZ | off HZ | off HZ | **ON** 자유 | off HZ부분 | **ON** **HZ** | HZ |
| scene08 | **ON** HZ | off HZ | off HZ | **ON** (비가드) | **ON** HZ | **ON** 자유 | HZ부분 |
| scene09 | 사문 | 사문 | 사문 | **ON** (비가드) | **ON** 자유 | **ON** 자유 | **자유** |
| scene10 | **ON** HZ | off HZ | off HZ | **ON** (비가드) | 사문 | **ON** 자유 | HZ부분 |
| scene11 | **ON** HZ부분 | off 자유 | **ON** 자유 | **ON** 자유 | **ON** 자유 | **ON** 자유 | HZ부분 |
| scene12 | **ON** **HZ** | 사문 | off HZ | **ON** (비가드) | 사문 | **ON** 자유¹ | HZ부분 |
| scene13 | **ON** HZ | off HZ | off HZ | **ON** (비가드) | **ON** HZ | **ON** 자유 | HZ부분 |
| scene14 | off HZ | off HZ | off HZ | **ON** (비가드) | **ON** 자유 | **ON** 자유 | HZ부분 |
| scene15 | off HZ | 사문 | 사문 | **ON** (비가드) | 사문 | **ON** 자유 | HZ부분 |
| scene16 | **ON** HZ | off HZ부분 | **ON** HZ | **ON** (비가드) | **ON** 자유 | **ON** 자유 | HZ부분 |
| scene17 | off HZ | 사문 | off HZ | **ON** (비가드) | 사문 | **ON** 자유¹ | HZ부분 |
| scene18 | off HZ | off HZ | off HZ | **ON** 자유 | 사문 | **ON** 자유 | HZ부분 |
| scene19 | **ON** HZ | off HZ | off HZ | **사문** | 사문 | **ON** 자유 | HZ부분 |
| scene20 | **ON** HZ부분 | off HZ부분 | 사문 | **ON** (비가드) | 사문 | **ON** HZ부분 | HZ부분 |
| scene21 | **ON** HZ | off HZ부분 | **ON** HZ | **ON** (비가드) | **ON** 자유 | **ON** 자유 | HZ부분 |
| sceneC1 | **ON** HZ | **ON** (비가드) | **ON** HZ | **ON** (비가드) | 사문 | **ON** 자유 | HZ부분 |
| sceneC2 | **ON** 자유 | off 자유 | off 자유 | **ON** (비가드) | 사문 | **ON** 자유 | **자유 + `keep_dressing` 기배선** |
| sceneC4 | **ON** HZ | **ON** (비가드) | off HZ | **ON** (비가드) | 사문 | **ON** 자유 | HZ부분 |
| sceneD1 | off HZ | 사문 | **ON** HZ | **ON** (비가드) | 사문 | **ON** 자유 | HZ부분 |
| sceneD2 | off HZ | 사문 | off HZ | **ON** 자유 | 사문 | **ON** 자유 | HZ부분 |
| sceneD3 | off HZ | off HZ | 사문 | **ON** (비가드) | 사문 | **ON** 자유 | HZ부분 |
| sceneD4 | **ON** 자유 | **ON** 자유 | **ON** 자유 | **ON** **HZ** | 사문 | **ON** 자유 | HZ부분(fascia만) |
| sceneN1 | 사문 | 사문 | 사문 | **ON** 자유 | 사문 | **ON** 자유 | **자유** |
| sceneN2 | 사문 | 사문 | 사문 | **ON** HZ부분 | 사문 | **ON** 자유 | HZ부분 |
| sceneN3 | 사문 | 사문 | **ON** (비가드) | **ON** 자유 | 사문 | **ON** 자유 | **자유 + `keep_dressing` 기배선** |
| sceneN4 | off 자유 | 사문 | 사문 | **ON** (비가드) | 사문 | **ON** 자유 | **자유** |
| sceneN5 | 사문 | 사문 | 사문 | **ON** 자유 | 사문 | **ON** 자유 | **자유** |

¹ scene12·scene17의 `cue_scene_dressing` 가드 자체는 자유지만 **본문 안쪽에 `if cfg["hazard_stairs"]`가 한 겹 더 있다**
(s12 L2073→L2075, s17 L2731→L2733): `build_skyline`은 살고 `build_dressing`은 해저드와 함께 죽는다.
주말 격리본이 `keep_dressing`을 이식한 지점이 정확히 여기다.

**"(비가드)"** = if-블록이 아니라 **삼항식/kwarg**로 배선된 경우. 배선이 없는 게 아니다 —
예: `stair_mtl = M["stair"] if cfg["cue_material_break"] else M["walk"]`(s16 L1792),
`tactile=("stair_top",) if cfg["cue_tactile"] else ()`(C1 L578, `gk.plan_ground` 인자),
`nosing=cfg["cue_nosing"]`(N3 L1346, `paint_fake_stairs` 인자).
**주말 인벤토리가 놓친 형태는 이것이 아니라 `cfg.get("k")` 쪽이다**(§2.5).

### 2.2 토글별 상세 — 무엇이 실제로 지워지는가

#### (1) `cue_railing` — ON·배선 **16씬**

| 씬 | 가드 위치 | 지우는 함수 | 프림 루트 | 13단서 | 기하 결속 판단 |
|---|---|---|---|---|---|
| scene01 | L2609 | `build_railing_line` | `/World/Scene01/Rail_{j}` (중앙+양측 φ 스테인리스, h0.9, 계단+상부 1 m 연장) | R | 자립 파이프 → **장식 유력**, 단 상부 1 m 연장이 카메라 기준면 근처 → 큐 |
| scene02 | L1603 | `build_handrail` | `{ROOT}/StairRail_{tag}/{Top,Mid,Post_n}` | R | 자립 파이프 → 장식 유력. 방호 본체는 **좌우 옹벽**(토글 없음) |
| scene06 | L2649 | `_guard_run` `_guard_posts` `_newel` `build_deck_rail` `build_north_guard` | `{ROOT}/Rail{tag}` `RailPost{tag}` `Newel{tag}_{k}` | R, G | **upstand가 계단 솔리드 안에 묻히도록(−0.300…+0.108) 설계**됨 → 제거 시 데크 립 노출 가능 · **구조 의심** |
| scene08 | L2459 (해저드 안) | `build_guard` `build_flank_rails` | (그룹 프림) | R, G | 캐스케이드 헤드 개방부 가드 → **구조 의심** |
| scene10 | L4232 | `_rake_rail` `build_newel` `build_handrail` | `{ROOT}/Newel_{i}` `FlightGrp_{k}/Rail_{side}` `{grp}/Bal_{tag}_{i}` | R | 데크 난간(자립) → 장식 유력 |
| scene11 | L2398 + L2793 | `build_railing_line` `build_guard_run` `build_mesh_panel` `build_deck_rails` | `{prefix}/RailA_{k}` `HeadGuardOuter` `HeadMesh` `MidGuard_{g_i}` `MidKick{nm}` `{tag}Newel` `DeckRail_{i}` `DeckKick_{i}_{k}` | R | **`MidKick`/`DeckKick` = 킥플레이트**(바닥 접합) → 구조 의심 |
| scene12 | L2066 (해저드 안) | `build_railing` | `{ROOT}/Rail/Post_{i}` `{ROOT}/Rail/{Top,Mid}` (y 1.09–1.21, x −18…0) | R (**강**) | **실측 장식** — heightmap 54셀·최대 5 mm·풋프린트 0셀·`polar_gt` 24/24 동일 |
| scene13 | L3806 (해저드 안) | `build_railings` | `{ROOT}/Rail_{i}/{tag,Post_n}` | R | 트렌치 상부 난간 → 큐 |
| scene16 | L1253 + L1324 | `build_handrail` | `{grp}/EastRail_{tag}` `{ROOT}/StairRail_{tag}` `{ROOT}/PerimRail_{tag}` | R | 자립 파이프 + **둘레 난간** → 큐 |
| scene19 | L2021 (`cfg.get`) | `build_arc_steps` | `/World/Scene19/Rail_{i}` (파라펫 **위** 아크 캡) | R | 파라펫 본체는 토글 밖 → **장식 유력** |
| scene20 | L880 + L1197 | `build_stair_walls` | `{grp}/StairWall_{tag}/{Body,Haunch,Newel,EndCap,Cap_Head,Cap_Rake,Cap_Toe}` | R (**강**), G (**강**) | **실측 구조물** — heightmap 12,656셀·최대 **3.160 m**·풋프린트 **+1,302셀**(60,659→61,961) |
| scene21 | L1446 | `build_railing_line` | `{ROOT}/Rail_{k}` | R (**강**) | 파라펫 위 레일 → 큐(파라펫 자체는 `build_parapets`, 토글 밖) |
| sceneC1 | L1124 | `build_railing_line` `build_rail_snow` | `{ROOT}/StairRail_P` + `{ROOT}/Snow/RailStrip{Flat,Slope}` | R (**강**) | 레일 + **레일 위 적설 스트립 동반 제거**(부수효과 기록 필요) |
| sceneC2 | L1042 | `build_railing_line` | `{ROOT}/Rail` | R (**강**) | 매트릭스가 "설계상 유일 단서 = 난간"으로 판독한 씬 → **최우선 큐** |
| sceneC4 | L1034 | `build_railing_line` | `{ROOT}/StairRail_{tag}` | R (**강**) | 큐 |
| sceneD4 | L720 | (인라인) | `{ROOT}/EndRail_{k}/{tag,Post_j}` | R (약) | 승강장 **단부** 난간 — 낙차 에지에서 떨어져 있음 → 장식 유력 |

`off`·배선 **12씬**(끄기용으로는 무의미 — 켜면 가드 신설): s03·s04·s05·s07·s14·s15·s17·s18·D1·D2·D3·N4.
`사문` **5씬**: s09·N1·N2·N3·N5. (16 + 12 + 5 = 33 ✓)

#### (2) `cue_nosing` — ON·배선 **8씬**

| 씬 | 프림 | 위치 | 판단 |
|---|---|---|---|
| scene02 | `{ROOT}/Nosing` | 계단 노징 | **에지 위 프림** → 큐 |
| scene11 | `{pfx}/Nosing_{j}` (`build_nosing_tier`) | 계단 노징 | 큐 |
| scene16 | `{grp}/Nosing` · `{ROOT}/Nosing` (2곳) | 계단 노징 | 큐 |
| scene21 | `{ROOT}/Nosing` | 계단 노징 | 큐 |
| sceneC1 | `{ROOT}/Nosing` | 황색 노징 밴드 (**5 cm 눈에 완전 매몰**) | 큐 · 매트릭스 §7 "존재하나 불가시" 2셀 중 하나 |
| sceneD1 | `{ROOT}/Band_{name}_Base` `Band_{name}_S_{i}` | 황흑 사선 도장 밴드 | **도장(데칼성)** → 장식 유력, 단 GT 에지를 정확히 추종(매트릭스 지름길 #8) |
| sceneD4 | `{ROOT}/Nosing_{i}` | 승강장 노징 | 큐 |
| sceneN3 | (`paint_fake_stairs(nosing=…)`) | **페인트** — 무낙차 씬의 착시 노징 | 순수 도장 → 장식 확정 |

노징은 정의상 **에지 위**에 있으므로 전 건이 구조 판정 큐 대상이다(도장형 2건 제외 가능).

#### (3) `cue_tactile` — ON·배선 **3씬**

| 씬 | 배선 | 프림 | 판단 |
|---|---|---|---|
| sceneC1 | `gk.plan_ground(tactile=("stair_top",) …)` L578 | ground_kit 300격자 점자블록 (에지 후방 setback) | 접근면 포장 → **장식 유력** |
| sceneC4 | 동상 L447 | 동상 | 장식 유력 |
| sceneD4 | L687 `build_tactile` + `_dots_relief` | `{ROOT}/Tactile_{k}` `TactileDots_{k}/proto` | **돌기 릴리프 = 실제 기하** · 승강장 에지 인접 → 큐 |

`off`·배선 19씬은 **끄는 대상이 아니라 켜면 마킹 신설**이다 — 브리프 §3-4(사인·표지 신설 금지)에 걸린다.

#### (4) `cue_material_break` — ON·배선 **32씬** (사문 1: scene19)

| 유형 | 씬 수 | 씬 | 무엇이 바뀌나 |
|---|---|---|---|
| **재질 바인딩 전용 (프림 생성·삭제 없음)** | **24** | s01·s02·s03·s04·s07·s08·s09·s10·s12·s13·s14·s15·s16·s17·s20·s21·C1·C2·C4·D1·D2·D3·N3·N4 | `stair_mtl = M["stair"] if … else M["walk"]` 형태. **프림 집합이 동일하므로 heightmap 비트 동일이 구성상 보증된다** |
| 프림 생성형 | **8** | s05·s06·s11·s18·D4·N1·N2·N5 | 아래 |

프림 생성형 상세:

| 씬 | 생성 프림 | 위치 | 판단 |
|---|---|---|---|
| scene05 | `/World/Scene05/LipCurb` (`build_arc_steps`, top_z/base_z 솔리드) | **립 개구부 바깥 링 = 낙차 에지 위** | **구조 의심 — 최우선 큐** |
| scene06 | `{ROOT}/CenterLine_{i}` `Dash_{j}_{k}` (`build_lanes`) | 노면 차선 | 평면 데칼 → 장식 유력 |
| scene11 | `{ROOT}/CenterLine_{i}` `Dash_{j}_{k}` | 노면 차선 | 장식 유력 |
| scene18 | `{ROOT}/Band_tan` (`_plate`) | 에지 밴드 | 큐 |
| sceneD4 | `{ROOT}/Facade_{i}` (`build_facade`) | **승강장 낙차 면(fascia)**, 슬래브에 0.06 매입·궤도 쪽 0.01 돌출 | **구조 의심 — 큐** · 또한 `hazard_stairs` 안에 있음 |
| sceneN1 | `{ROOT}/JointX_{n}` `JointY_{m}` | 포장 줄눈 격자(평면) | 장식 확정 유력 |
| sceneN2 | `{ROOT}/JointX_{i}` `JointY_{i}` + `CutLine_*` 실란트 오버밴드 | 평면 | 장식 유력 |
| sceneN5 | `{ROOT}/JointX_{i}_{k}` `JointY_{i}_{k}` | 평면 | 장식 유력 |

#### (5) `cue_sign` — ON·배선 **9씬** (s01·s02·s08·s09·s11·s13·s14·s16·s21)

전부 자립 표지판(`{ROOT}/Sign_{tag}` + `/World/Looks/Sign{tag}`, s09는 `LecternBody`).
낙차 에지에서 떨어진 자립물 → **풋프린트 영향 없음이 강하게 예상**되나 프림이므로 명목상 큐(저순위).
**사문 22씬**이 최대 공백이다 — 켜도 꺼도 그림이 안 바뀐다.

#### (6) `cue_scene_dressing` — ON·배선 **33씬 전부**

지우는 것: 배경 건물·수목·헤지·벤치·볼라드·가로등·화분·자전거도로 백선·교량·리터 등.
프림 루트 예: s12 `{ROOT}/Bridge/{Deck,Pier_i,PierCap_i,Parapet_tag}` `FarBuilding_{key}` `BikeRoad` ·
s17 `KmSign/{Pole,Panel}` `TerraceTree_{i}` `CrownTree_{i}` · s20 `Streetlight_{i}` `Bollard_{i}`
`Planter_{i}` `Bench_{i}` `Hedge_{i}` `AccessRamp` `Band_{i}` `Litter_{Tread,Foot,Plaza}`.

**실측 판정 3건**:
- s12 dressing = heightmap 14,467셀 · 최대 5 mm · 풋프린트 0셀 → **장식**
  (5 mm 돌출 드레싱 스킨 = 자전거도로 백선·재질전이 밴드)
- s17 dressing + material_break = **heightmap sha256 동일 · 0셀** → **장식(완전)**
- s20 dressing = 단독 판정 없음. B1(가드+재질+드레싱 동시 제거) 16,012셀 vs B2(가드만) 12,656셀이므로
  **3.16 m급 차이의 주범은 치크월이고 드레싱 몫은 나머지 ~3,356셀**이다. 드레싱 단독 팔이 없어 분리 판정 불가 → 큐 유지.

### 2.3 13 단서 ↔ 토글 도달 가능성

| # | 단서(13키) | 이 단서를 끄는 토글 | 도달 가능 씬 수 | 비고 |
|---|---|---|---|---|
| R | `railing_or_guard` | `cue_railing` | 16 / present 18 | 도달률 최고 |
| Ta | `tactile_paving` | `cue_tactile` | 3 / present 4 | C1은 눈에 매몰(화면 기여 0) |
| N | `nosing_strip` | `cue_nosing` | 8 / present 7 | present 초과는 토글이 있으나 매트릭스가 `·`로 찍은 칸 |
| T | `texture_change_across_edge` | `cue_material_break` | 32 / present 27 | **코퍼스 전역 유일 무결 레버** |
| Sg | `signage_or_marking` | `cue_sign`(9) + `cue_scene_dressing`(차선·백선·NamePlate) | ~14 / present 14 | 사문 22씬 때문에 `cue_sign` 단독으로는 5–9씬 |
| V | `vegetation_edge` | `cue_scene_dressing` | 18 / present 18 | 드레싱과 분리 불가 |
| C | `curb_or_upstand` | 부분: s05 `LipCurb`(mb) · s08 `build_curb`(dressing) · N5 `Curb_`(dressing) | 3 / present 15 | **전용 토글 없음** |
| G | `geometry_silhouette` | 부분: s20 치크월(railing) · 배경 건물(dressing) | 부분 / present 28 | 대부분 해저드 기하 자체 |
| **E** | `edge_line_contrast` | 부분(s05 LipCurb · s18 Band_tan) | ~2 / present 27 | **사실상 토글 없음** |
| **Sh** | `shadow_line` | **없음** | 0 / present 18 | 태양각 축(B2)으로만 조작 |
| **F** | `far_side_visible_depth` | **없음** | 0 / present 28 | 기하 자체 |
| **W** | `water_surface` | **없음** | 0 / present 6 | s09 `build_river`는 항상 ON(수평 폐합용) |
| **Sp** | `specular_change` | **없음**(C4 `wet_surface`는 조건 토글) | 0 / present 14 | |

**결론**: 13키 중 **5키(E·Sh·F·W·Sp)는 코퍼스 전역에서 토글이 0**이고, `C`·`G`도 사실상 없다.
v3의 B팔이 "단서를 지웠다"고 말할 수 있는 축은 **R·Ta·N·T·Sg·V 6개**뿐이며,
그중 전 씬 커버는 **T(재질전이)와 V/Sg(드레싱)** 둘뿐이다. 이것이 v3 사양이 정면으로 다뤄야 할 제약이다.

### 2.4 scene14 — 가드가 구조물이라는 주장의 설정 근거 (검증됨)

- `SCENE_CONFIG["cue_railing"] = False`, 주석: *"A monumental stair is open-sided — True → **pipe rail on top of the side parapets**"* (L117).
  즉 이 키는 **가드를 지우는 키가 아니라 파이프 레일을 얹는 키**다.
- 매트릭스가 scene14에 준 `railing_or_guard`(중)의 실체는 **비행 측면의 경사 파라펫**이고,
  그것은 `build_parapets(M)`이 `if cfg["hazard_stairs"]:` 블록(L1885–1893) 안에서 무조건 짓는다.
  **어떤 `cue_*` 키도 파라펫을 참조하지 않는다.**
- 파라펫 파라미터(`PARAMS["parapet"] = dict(width=0.5, z0=0.35, thick=1.6, cap_t=1.4)`, L260)는
  계단 폭·측면 사면과 좌표를 공유한다. 씬 파일 스스로 L835 부근에 *"a removal that silently drags the
  parapet with it would pass an [assertion]"* 라고 적어 두었다.

⇒ **scene14의 가드 어블레이션은 설정 수준에서 불가능**하다. 브리프의 알려진 사실이 그대로 확인된다.
scene14는 test-core이자 strict-H 60장의 최대 보유 씬이므로, **H 위에서의 가드 개입은 현 코퍼스에서 원천 불가**다.

### 2.5 주말 인벤토리 정정 — 오탐 11칸 / 6씬

`experiments/weekend_0823/cue_audit/scene_toggle_inventory.csv`는 `cfg["key"]` 구독 형태만 셌고
**`cfg.get("key")` 호출 형태를 놓쳤다.** 그 결과 아래 11칸이 "사문화"로 잘못 찍혔다.

| 씬 | 키 | 실제 배선 위치 | CSV | 정정 |
|---|---|---|---|---|
| scene02 | `cue_sign` | L1940 `cfg.get("cue_sign") and cfg["hazard_stairs"]` | 사문 | **ON·배선** |
| scene05 | `cue_railing` | L2669 `cfg.get("cue_railing")` | 사문 | off·배선 |
| scene05 | `cue_tactile` | L2686 | 사문 | off·배선 |
| scene05 | `cue_nosing` | L2690 | 사문 | off·배선 |
| scene05 | `cue_sign` | L2739 | 사문 | off·배선 |
| scene09 | `cue_sign` | L3890 | 사문 | **ON·배선** |
| scene16 | `cue_sign` | L1828 | 사문 | **ON·배선** |
| scene19 | `cue_railing` | L2021 | 사문 | **ON·배선** |
| scene19 | `cue_tactile` | L2032 | 사문 | off·배선 |
| scene19 | `cue_nosing` | L2038 | 사문 | off·배선 |
| scene21 | `cue_sign` | L1479 | 사문 | **ON·배선** |

집계 영향: `cue_railing` ON 15 → **16**, `cue_sign` ON 5 → **9**, `cue_sign` 사문 27 → **22**.
**CUE-OFF 후보 선정 결론은 바뀌지 않는다**(추가된 씬은 전부 strict-H 0), 그러나
**v3 배선 공백 산정은 바뀐다** — 새로 배선해야 할 칸이 11개 줄어든다.

---

## 3. 요약표

### (a) CUE-OFF 가용 집합과 "3씬뿐"의 재조정

**설정 기준으로는 33/33 전 씬이 "≥1개 끌 수 있는 단서"를 가진다.** 주말의 "3씬뿐"은
단서 배선이 아니라 **개입을 판정할 프레임이 없다**는 제약에서 나온 수다. 조건을 순서대로 적용하면:

| # | 조건 | 남는 씬 | 탈락 사유 |
|---|---|---|---|
| 0 | 33씬 라이브러리 | **33** | — |
| 1 | ≥1 ON·배선 `cue_*` 보유 | **33** | 탈락 0 (`cue_scene_dressing`·`cue_material_break`가 거의 전 씬 ON) |
| 2 | ≥1 ON·배선 **비-드레싱** 단서 보유 | **33** | 탈락 0 (`cue_material_break` 32 + s19는 railing) |
| 3 | **strict-H 프레임 보유** | **6** | 27씬 탈락 — s09·s12·s14·s15·s17·s20만 H를 낸다(`H_CUE_AUDIT` §0-1) |
| 4 | 비-test (test-core 불가침) | **4** | s14·s15 탈락(test-core) |
| 5 | 주 단서가 토글에 물려 있을 것 | **3** | **s09 탈락** — 강 단서가 `water_surface`·`far_side_visible_depth`이고 **이 둘은 어떤 토글에도 물려 있지 않다**(§2.3). `build_river`는 항상 ON |
| — | **최종** | **scene12 · scene17 · scene20** | |

**즉 병목은 배선이 아니라 (3) strict-H 프레임이다.** 그리고 사후에 밝혀진 사실 둘이 이 표를 더 나쁘게 만든다:

- **scene12의 H 48장은 퇴화 풋프린트의 산물이었다**(`CUEOFF_RESULT_v2.md` 배너):
  `lineage` 라벨셋에서 `cells_raw = 50`(x=1.6 m의 5 cm × 2.45 m 슬리버), 교정 참조(`twin`)에서는
  **50,278셀 · 같은 48프레임이 tier V**. ⇒ **scene12는 strict-H 씬이 아니다.**
- **scene20의 H는 6장**이라 사전등록 하한(n≥10)에 미달했고, 카메라 밴드 수리 후 27장으로 늘렸더니
  이번엔 **치크월이 구조물이라 §4.5-2(폰트프린트 불변)에서 VOID**가 났다.

⇒ 실효 strict-H 개입 가능 씬은 **scene17 하나**였다. v3가 `paired-H ≥ 10`(DZ §4.2)을 신설 요구하는 이유가 이것이다.

### (b) 렌더 분류 큐 — 두 팔 라벨러 `cells_raw` 차이 검사가 필요한 씬 × 단서

판정 규칙(`CUEOFF_RESULT_v2.md` §5.4·§6.3 확정): 팔 A와 팔 B를 같은 시드·같은 밴드로 렌더하고
라벨러를 두 번 돌려 **`cells_raw`(풋프린트 셀 수)와 프레임별 `polar_gt`**를 비교한다.
`cells_raw` 동일 + `polar_gt` 비트 동일 = **장식** / 하나라도 다르면 = **구조물(토글 금지 목록 등재)**.

**이미 판정 끝난 4건 (재검사 불필요)**

| 씬 · 단서 | 판정 | 근거 수치 |
|---|---|---|
| scene12 `cue_railing` | **장식** | heightmap 54셀 · 최대 5 mm · 풋프린트 0셀 · `polar_gt` 24/24 동일 |
| scene12 `cue_scene_dressing` | **장식** | 14,467셀 · 최대 5 mm · 풋프린트 0셀 · `polar_gt` 24/24 동일 |
| scene17 `cue_scene_dressing` + `cue_material_break` | **장식(완전)** | heightmap **sha256 동일** · 0셀 · `polar_gt` 24/24 동일 |
| scene20 `cue_railing` | **구조물** | 12,656셀 · 최대 **3.160 m** · 풋프린트 **+1,302셀** · `polar_gt` 6/27 프레임 상이 |

**고순위 큐 — 33 (씬 × 단서) 쌍** (에지 인접 프림 = 풋프린트를 움직일 수 있는 것)

| 단서 | 쌍 수 | 씬 |
|---|---|---|
| `cue_railing` | **14** | s01 · s02 · s06 · s08 · s10 · s11 · s13 · s16 · s19 · s21 · C1 · **C2** · C4 · D4 |
| `cue_nosing` | **8** | s02 · s11 · s16 · s21 · C1 · D1 · D4 · N3 |
| `cue_tactile` | **3** | C1 · C4 · **D4** |
| `cue_material_break` (프림 생성형) | **8** | **s05** · s06 · s11 · s18 · **D4** · N1 · N2 · N5 |

굵은 표시 = **구조 의심 최상위**(에지 위 솔리드 또는 낙차 면에 붙은 프림):
**s05 `LipCurb`**(립 개구부 바깥 아크 솔리드) · **D4 `Facade_{i}`**(승강장 낙차 면 fascia) ·
**D4 `TactileDots`**(돌기 릴리프) · **C2 `Rail`**(설계상 유일 단서) ·
**s06 guard upstand**(계단 솔리드에 −0.300…+0.108로 매입) · **s11 `MidKick`/`DeckKick`**(킥플레이트).

**저순위 큐 — 39 쌍** (풋프린트 영향은 없을 것으로 예상, **포즈 게이트**만 필요)

| 단서 | 쌍 수 | 씬 |
|---|---|---|
| `cue_scene_dressing` | 30 | 33씬 − 이미 판정된 s12·s17·s20 |
| `cue_sign` | 9 | s01 · s02 · s08 · s09 · s11 · s13 · s14 · s16 · s21 |

저순위의 검사 목표는 `cells_raw`가 아니라 **`ground_z` 데이텀 이동**이다.
`variation_kit.AabbPrefilter.ground_z`는 **모든 Gprim의 월드 AABB**에 대해 z=60 m에서 하향 레이를 쏜다
(`variation_kit.py:781–785`). 카메라 기준면은 `gz = pre.ground_z(-d, y)`(`run_data_render.py:458`)이고
샘플러는 `d ∈ [1.2, 12] m` · `|y| ≤ 0.90 m`를 뽑는다. 따라서 **카메라 데이텀 스트립 = x<0 · |y|≤0.90**
안에 서 있는 드레싱 프림(볼라드·벤치·화분)을 지우면 포즈가 어긋나 A/B 페어링이 깨진다.
전례: 구 sceneC2 off팔의 `build_flat_fill` 잔디 슬래브가 `ground_z`를 0.130 → **0.0163 m**로 밀어
**트윈 쌍이 0개**가 됐다(`nightrun_0820/ctrl_dressing/README.md`).

**구성상 안전한 것(검사 면제 가능)**
- `cue_material_break` **재질 전용 24씬** — 프림 집합 불변 ⇒ heightmap 비트 동일이 보증된다.
  (권고: 24씬 중 3씬만 표본 검사해 이 논증을 실증하고, 나머지는 면제)
- `cue_nosing` · `cue_tactile`의 **데이텀** 리스크 — 노징은 x ≥ 0(답면 위), 점자블록은 에지 후방
  0.3–0.6 m에 놓이는데 샘플러 최소 거리가 d = 1.2 m이므로 **카메라 컬럼을 덮지 않는다**.
  (풋프린트 리스크는 남으므로 고순위 큐에는 그대로 둔다)

**큐 총계: 72 쌍** (고순위 33 + 저순위 39), 이미 판정 4건 제외.

### (c) 배선 공백 — v3 2×2 팔별로 무엇이 없나

DZ §4.1의 4팔: **A**(위험+단서) **B**(위험−단서) **C**(무위험+단서) **D**(무위험−단서).

| 팔 | 현 코퍼스 가용 | 없는 것 | 신규 배선 |
|---|---|---|---|
| **A** | **33 / 33** | — | 0 |
| **B** | **33 / 33** 명목 · **24 / 33** 무결(재질 전용) | 나머지 9씬은 프림 생성형이라 §3-(b) 판정 선행 | 0 (판정만) |
| **C** | **8 / 33** (s01·s04·s09·**C2**·N1·**N3**·N4·N5) | 25씬은 단서 빌더가 `hazard_*` 안 → 구off | **`keep_dressing` 이식 25건** |
| **D** | **33 / 33** | — | 0 (`hazard=False` + `cue_*=False`) |

> **v2 "off" 팔은 균질한 팔이 아니다.** 위 C열이 그 이유다 — `hazard_stairs=False` 하나만 준
> v2 off 프레임은 **자유 8씬에서는 사실상 C팔**(단서가 남는다)이고 **HZ 25씬에서는 D팔에 가깝다**.
> DZ §12-2가 "트윈이라는 낱말을 쌍 명시 없이 쓰지 말라"고 한 것의 코드 수준 근거다.
> v2의 44.7 %/0 %가 (A,D) 기반이라는 서술은 25씬에 대해서만 정확하다.

**공수 추정 (씬당)**

| 등급 | 작업 | 대상 | 씬당 공수 | 근거 |
|---|---|---|---|---|
| **T1 · 사소** | `keep_dressing` 이식 | 25씬 | **0.5–1 h** | 원본 `scenes/batch1/sceneC2_leaf_stairs.py:496–520` — 모듈 상수 `KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))` + 모순 설정 FATAL 종료 + 장식 호출을 `if cfg["hazard_stairs"] or KEEP_DRESSING:`로 완화 + 하부 앵커 드레싱을 채워진 지면(z=0)에 재부착. 격리본 3종이 이미 이 패턴으로 돌아갔다 |
| **T1 · 사소** | `placebo_remove` 이식 (플라시보 팔) | 팔 P를 쓰는 씬만 | **0.5 h** | `scenes_cueoff/scene20_diagonal_oblique.py:496–533, 1046, 1473` |
| **T2 · 보통** | 사문 `cue_*` 키를 실제 배선으로 | `cue_sign` 22 · `cue_tactile` 11 · `cue_nosing` 8 · `cue_railing` 5 | **2–4 h** | **주의: 대상 오브젝트가 씬에 없으면 이것은 "배선"이 아니라 "단서 신설"이다.** 브리프 §3-4(사인·표지 신설 금지)·DZ의 난이도 정체성 규칙에 걸리므로 **결재 없이 착수 불가** |
| **T3 · 재설계** | 구조물 가드를 자립 가드로 분리 | s20(치크월) · s14(파라펫, 토글 자체 없음) · s21·s06(파라펫/upstand 매입) · s15(골목 벽) 등 | **1–2 d** | 낙차 발자국을 바꾸지 않는 자립 가드 프림을 새로 만들고 기존 구조물은 낙차 정의에 남긴다. **s14는 test-core라 기하 변경 자체가 금지 대상** |
| **T4 · 신설** | test-ext 4팔 전용 씬 | 신규 | — | §4-4 |

---

## 4. P-5 입력 — v3 렌더 계획에 대한 함의

### 4-1. 무개조로 지금 공급 가능한 팔

| 팔 조합 | 즉시 가능한 씬 | 규모 |
|---|---|---|
| **A + B(재질전이) + D** | **24씬** (재질 전용 `cue_material_break`) | 33씬 중 24 · 배선 0 · 해시게이트 통과가 구성상 보증 |
| **A + B(드레싱) + D** | 33씬 (단, 포즈 게이트 필수) | 저순위 큐 통과 후 |
| **A + B(가드) + D** | **1씬 확정**(scene12) + 판정 대기 14 | scene20은 **금지**(구조물 실측) |
| **A + C + D** (4팔 완비) | **8씬**(s01·s04·s09·C2·N1·N3·N4·N5) | 그중 **C2·N3는 test-core**, s04는 사용자 보류 씬 ⇒ **실질 train 가용 5씬**(s01·s09·N1·N4·N5) |
| **A+B+C+D 4팔 + strict-H** | **0씬** | H 보유 6씬 중 C팔 무개조 가능은 s09뿐이고, s09는 주 단서가 토글 밖(§3-a 조건 5) |

### 4-2. 그래서 P-5가 계획서에 반드시 반영해야 할 것 5가지

1. **`keep_dressing` 이식 25건을 렌더 전 CPU 작업으로 먼저 세울 것.** 이것 없이는 C팔이
   8씬(그중 2씬 test-core)에 갇히고, DZ §4.1의 비율 초안 **3:2:3:2**(C를 A와 동율)를
   훈련 코퍼스에서 만들 수 없다. 씬당 0.5–1 h · GPU 0.
2. **B팔의 1차 축은 `cue_material_break`로 잡을 것.** 24씬에서 프림 불변이 보증되므로
   해시게이트(팔 A/B의 `heightmap_meta.json` 비트 동일)가 **설계상 통과**한다.
   가드 제거는 §3-(b) 판정이 끝난 씬에서만 2차 축으로 얹는다.
3. **가드 사전 분류(DZ §4.3-2)를 렌더 계획의 선행 스테이지로 예산화할 것.**
   고순위 33쌍 × 2팔 × (밴드 1개 24컷) ≈ **1,584컷**. 실측 4.0–4.7 s/컷 + Isaac 부팅이 컷 시간보다 크므로
   씬당 5–7분으로 잡으면 대략 **3–5 GPU-h**(라벨러 CPU 별도). 이 지출을 안 하면
   "구조물을 단서로 지웠다"는 무효화 위험을 v3 전체가 떠안는다.
4. **계기판용 test-ext 씬은 기존 33씬에서 조달할 수 없다.** DZ §12-9는 계기판 ①②③을
   **양 모델이 미학습한 test-ext 4팔**에서만 재라고 했는데, 4팔이 무개조로 서는 8씬 중
   **C2·N3는 test-core**(잣대 불가침), s04는 보류, 나머지 5씬은 전부 train이다.
   ⇒ **test-ext 씬은 신설이 유일한 경로**이고, 신설 시 `cue_*` 6키 + `keep_dressing` + `placebo_remove`를
   **표준 장비로 처음부터** 넣어야 한다(DZ §12-6 후단). 템플릿은 `scenes/probe/probeH*.py`(441–528행)가
   가장 싸다.
5. **`paired-H ≥ 10`은 신설 씬으로만 달성된다.** 현 코퍼스의 strict-H 6씬 중 s12는 퇴화 풋프린트 산물,
   s20은 구조물 가드로 VOID, s14·s15는 test-core, s09는 주 단서가 토글 밖 ⇒
   **B팔 개입을 H 위에서 잴 수 있는 기존 씬은 s17 하나.** DZ §4.2의 "paired-H ≥ 10" 신설 요구는
   선택이 아니라 이 감사의 필연이다.

### 4-3. 렌더 계획이 반드시 켜야 할 게이트 (이 감사에서 도출)

| 게이트 | 무엇을 | 실패 시 |
|---|---|---|
| G-해시 | 팔 A/B의 `heightmap.npy` · `heightmap_meta.json` 비트 동일 | 그 `cue_*`는 구조물 → 토글 금지 목록 등재 |
| G-풋프린트 | 라벨러 `cells_raw` A == B | 동상. **`polar_gt` 비트 동일까지 판정 프레임 위에서 확인**(s20 사례: 씬 스코프 breach가 판정 스코프에서는 무해했다) |
| G-포즈 | 컷별 `cam.eye`·`yaw`·`pitch`·`hfov`·`ground_z` 차 < 1e-6 | `ground_z` 데이텀 이동. 원인은 카메라 스트립(x<0 · abs(y)≤0.90)에 선 프림 제거 |
| G-티어 | 팔별 V/E/H/H_weak/none_in_fov 재도출 | `H→E`뿐 아니라 **`V→H`·`none_in_fov→H`도 보고**(주말에 실제로 나온 방향은 이 둘이었다) |

### 4-4. 신설 씬의 표준 장비 목록 (DZ §12-6 후단의 구체화)

1. `SCENE_CONFIG` 14키 + `keep_dressing` + `placebo_remove` = **16키**를 전부 선언하고 **전부 읽는 코드**를 둘 것
   (사문 0). 특히 `cue_sign`은 현 코퍼스에서 22씬이 사문이다.
2. 단서 오브젝트는 **자립 프림**으로 짓고, 낙차를 지지하는 구조물(옹벽·파라펫·치크월·킥플레이트)과
   **프림 계층을 분리**할 것. 같은 그룹에 넣지 말 것.
3. 단서 빌더를 `if cfg["hazard_*"]` 안에 넣지 말 것 — 넣어야 하면 `or KEEP_DRESSING`을 같은 줄에 함께 쓸 것.
4. 단서 프림을 **카메라 데이텀 스트립(x<0 · |y|≤0.90 · d∈[1.2,12])** 안에 세우지 말 것.
   세워야 하면 그 사실을 씬 파일 상단에 명시하고 포즈 게이트 허용 오차를 사전 선언할 것.
5. 씬 파일 하나만 복사하면 격리본이 되도록 kit 의존을 **심링크 전제**로 쓸 것
   (`scenes_cueoff/`가 그 형태다).
6. 렌더 진입점은 `run_data_render.py --scene-proc <file> <scene_key> <out_dir> <conds> <cams> <seed>`.
   정본 드라이버는 `scenes/{main,batch1}/scene*.py`만 글롭하므로, 격리본·신설 씬을 정본 라이브러리에
   넣기 전까지는 이 경로가 유일하다.

---

## 5. 이 감사가 만든 다음 큐

1. **`scene_toggle_inventory.csv` 정정본 발행** — 오탐 11칸(§2.5). 원본은 배너 1줄 append로 대체 표시.
2. **고순위 33쌍 렌더 분류 착수 승인** — 3–5 GPU-h. 산출 = `cue_*` 구조물/장식 대장 + 토글 금지 목록.
3. **`keep_dressing` 이식 25건 착수 승인** — CPU 전용, 씬당 0.5–1 h. 정본 씬 수정이므로 결재 대상.
4. **사문 키 배선 정책 판정** — `cue_sign` 22씬 등은 "배선"이 아니라 "단서 신설"이 되는 경우가 많다.
   대상 오브젝트가 이미 씬에 있는 칸과 없는 칸을 분리해 목록화해야 한다(본 감사 미수행).
5. **s19 판정 그리드(d{2,3.5,5}) 처리** — 매트릭스 §6-4의 미결 항목. v3 밴드 설계에 걸린다.

---

## 부록 A. 근거 스크립트

본 문서의 모든 수치는 아래 CPU 스크립트로 재생성된다.
경로 = `experiments/v3_0823/code/`. **정본 씬 트리는 읽기 전용으로만 열었다.**

| 스크립트 | 출력 | 무엇을 |
|---|---|---|
| `audit_cue.py` | `cue_audit.json` | 46개 씬의 `SCENE_CONFIG` 기본값 · 키별 읽기 라인 · if-가드 범위/호출/프림 |
| `prims2.py` | `prims2.json` | 가드 본문 + 호출된 로컬 `build_*` 함수 본문의 프림 경로(f-string 재구성 포함) |
| `hazgate.py` | `hazgate.json` | 호출 그래프 추적으로 각 `cue_*` 가드가 `hazard_*` 분기 안에 있는지 판정 |

실행: `python3 experiments/v3_0823/code/audit_cue.py <out.json>` · `python3 …/prims2.py` ·
`python3 …/hazgate.py` (전부 표준 라이브러리만 씀 — Isaac·GPU·torch 불필요).

판정 규칙 요약: **"배선됨"** = 씬 파일 안에서 그 키를 읽는 코드가 1회 이상 존재
(`cfg["k"]` · `SCENE_CONFIG["k"]` · `cfg.get("k")` · 삼항식 · kwarg 전달 전부 포함) **이면서**
그 코드가 실제로 호출되는 함수 안에 있을 것. 선언만 있고 읽는 코드가 없으면 **사문화**.
