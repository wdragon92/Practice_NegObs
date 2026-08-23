# SCENE_H67_BUILD — `sceneH6_berm_levee2` · `sceneH7_bend_walk2` 저작 보고

- **작성**: Claude Code · 2026-08-23 · **과업**: RENDER_PLAN_V3 **WP-5 (Wave A)** 중
  §3.5 「val strict-H ≥ 30 회계」의 **공급원 2씬**
- **지위**: 이 두 씬은 **선택지표 수리(DZ §4.3-3)의 전제**다. 현 val strict-H = 6(scene20 단독)이
  D52가 잡아낸 "6문제 시험"의 물리적 정체이고, test-ext 프레임을 val로 돌려쓰는 것은 §12-9
  위반이므로 **val 배정 전용 paired-H 씬 신설 외에 경로가 없다**(계획 §3.5).
- **GPU 사용**: 스모크 4컷 + H밴드 프로브 32컷 + 세그 검증 재렌더 16컷 = **52컷 ≈ 0.09 GPU-h**
  (실측 wall 약 12분, 부팅 8회 포함). 전부 `flock -o /tmp/negobs_gpu.lock` 직렬화.
- **정본 무수정 원칙**: 기존 씬 파일 **0바이트 수정**. kit(`scene_common`·`ground_kit`·
  `variation_kit`)·드라이버(`run_data_render.py`) **0바이트 수정**. 신규 씬을 AZ 원장에 넣는 일은
  **런타임 패치**로만 했다(§6.1).

---

## 0. 결론 세 줄

1. **두 씬 다 착지했고 H 밴드 실측 strict-H는 각각 7/8 = 0.875다** — 계획 §3.5가 가정한 H 밴드
   수율 **0.60의 1.46배**, 개정 발동선(pro-rata의 60 % = 0.36)의 **2.4배**. 기하 개정 **0회**.
2. 프로브가 붙인 게이트는 전부 통과했다 — **VG-datum `datum_exact` 32/32**(max |Δground_z| =
   **0.000000 m**) · **VG-10 포즈 불일치 0** · **VG-void 커버리지 1.0000** (4팔 전부) ·
   **VG-06 모서리 소속: 낙차 구조물 화면 기여 0 px** · VG-13 과노출 0.
3. **부수 발견 1건이 계획에 반영돼야 한다** — `NEGOBS_SEG_SIDECAR=1`의 `idseg_fetch="t0"`
   빠른 경로는 **1컷 라운드에서만 유효**하다. 8컷 라운드에서 `.idseg.npz` 8개가 **바이트
   동일**했다(§7). VG-06과 DZ §12-5의 단서 임계 k는 둘 다 **컷별** 마스크를 요구하므로,
   이 결함이 남으면 두 게이트가 조용히 첫 컷 하나만 검사한다.

---

## 1. 산출물

| 파일 | 행 | 무엇 |
|---|---|---|
| `scenes/main/sceneH6_berm_levee2.py` | 1,491 | **둔덕형** 제방·수변 씬 (val · base+H+H2) |
| `scenes/main/sceneH7_bend_walk2.py` | 1,369 | **복도 굴절형** 보도 씬 (val · base+H) |
| `experiments/v3_0823/code/h67_probe.py` | 190 | 신설 씬 렌더 진입점 (AZ 원장 런타임 확장 + `scene_proc` 직호출) |
| `experiments/v3_0823/code/run_h67_probe.sh` | 130 | flock·conda·사이드카 규율을 담은 라운드 러너 |
| `experiments/v3_0823/code/h67_yield.py` | 171 | 실측 strict-H 수율 · VG-datum/10/08/void 대조 |
| `experiments/v3_0823/annotations/h67_probe_labels.json` | — | 프로브 32프레임 라벨 (gridspec_v1) |
| `experiments/v3_0823/annotations/h67_rev_labels.json` | — | 세그 검증 라운드 32프레임 라벨 |
| `experiments/v3_0823/logs/h67_probe.log` | — | 렌더 로그 |
| `Docs/briefs/placement_rules_v1.yaml` | +6행 | C-9 볼라드 보유 씬 레지스트리에 sceneH6·H7 추가 (§5-4) |

데이터 라운드(코퍼스 아님 — **증거로만 보존**):
`dataset/260823_v3p5_h67smoke_A` (2컷) · `…_h67probe_A` (16컷) · `…_h67probe_C` (16컷) ·
`…_h67rev_A` (16컷, 세그 검증).

---

## 2. sceneH6_berm_levee2 — 둔덕형

### 2.1 설계 요지

보행자가 진입 보행로에서 **제방 어깨 잔디 둔덕**을 넘어 호안 상단 관리통로로 내려서고,
통로 끝은 **호안 옹벽 2.60 m 노출면 · 수면까지 2.80 m 낙차**다. 은닉체는 **둔덕 마루
(`BermCrest`)** — 낙차 개구보다 카메라에 **가깝고 높다**(계획 §2.1 표의 요구 그대로).

종단면 (walk axis +X · 카메라는 x = −d):

| x | z | 무엇 | 프림 |
|---|---|---|---|
| ≤ −10.05 | 0.000 | 진입 보행로 (인터로킹 200×100) | `Ground/Approach` |
| −10.05 → −4.45 | 0.00 → 0.95 | 제방 어깨 잔디 사면 1:5.89 | `Ground/BermRise_00..47` |
| −4.45 → −3.85 | 0.950 | **둔덕 마루** | **`BermCrest`** |
| −3.85 → −2.35 | 0.95 → 0.45 | 화강석 3단 (R 0.1667 · T 0.50) | `Ground/ShoulderStep_0..2` |
| −2.35 → −0.78 | 0.450 | 호안 상단 관리통로 (폭 1.57) | `Ground/ServiceWalk` |
| −0.78 → −0.33 | 0.450 | 옹벽 갓돌 — 통로와 **동일 z** | `RetainWall/Coping` |
| ≥ −0.33 | −2.15 → −2.42 → −2.35 | 사석 2단 + 수면 | `Riprap/T0,T1` · `Water/Surface` |

**낙차 = 0.450 − (−2.350) = 2.800 m** (브리프 "2.5–3.0 m" 준수).

### 2.2 H 판정식 — 그리고 설계 예측이 틀린 지점

가림은 **마루 모서리 C = (−3.85, 0.95)** 를 스치는 시선의 기울기 s 하나로 닫힌다.

| 조건 | 부등식 | 임계 |
|---|---|---|
| 낙차 **내부**(수면) 은닉 | 0.95 + 17.85·s ≥ −2.35 | s ≥ **−0.1849** |
| 낙차 **림**(갓돌 상면) 은닉 | 0.95 + 3.520·s ≥ 0.45 | s ≥ **−0.1420** |

설계 시에는 scene14 on팔 72프레임이 전부 `edge_visible = 0` 인 것을 근거로
`[measured: dataset_manifest_v2corr]` **내부 조건이 실효 구속**이라고 적었다. **프로브가 이를
반증했다** — 8컷 중 1컷이 `int_px = 0` 인데 `edge_visible 126/149 (ratio 0.846)` 로 **E 티어**가
됐다. 이 씬의 림은 화강석 갓돌 상면이라 scene14의 계단 노즈선보다 깊이 불연속이 커서 라벨러의
3×3 깊이 창(RIM_TOL 0.35 m)에 먹히지 않는다. ⇒ **실효 구속은 림 조건**이며, 씬 파일의
`_h_max(d, crit="rim")` 이 기본값으로 그 쪽을 쓴다. 두 모형을 병기해 둔다.

| d | z(−d) | h_max(내부) | h_max(림) | H밴드 통과율(림) |
|---|---|---|---|---|
| 5.0 | 0.857 | 0.306 | 0.257 | 0.01 |
| 6.0 | 0.687 | 0.660 | 0.568 | 0.42 |
| 7.0 | 0.517 | 1.015 | 0.880 | 0.84 |
| 8.0 | 0.348 | 1.369 | 1.192 | 1.00 |
| ≥ 8.5 | ↓ | ↑ | ↑ | 1.00 |

밴드 적분(림 모형): **H 0.911 · base 0.206** — CPU 자기검사가 매 실행 인쇄한다.
근거리(d ≲ 4.5)는 카메라가 둔덕 위에 올라서므로 낙차가 그대로 보인다 → V.
**base 수율이 0.21에 머무는 것이 퇴화(전 프레임 H) 방지 장치**다.

### 2.3 실측 (라운드 `260823_v3p5_h67probe_A` · H 밴드 8컷 · L0)

| 항목 | 값 |
|---|---|
| tier 분포 | **H 7 · E 1** |
| **strict-H** | **7/8 = 0.875** · Wilson 95 % CI [0.53, 0.98] |
| 계획 가정 (H 밴드 0.60) 대비 | **1.46 배** |
| 개정 발동선 (pro-rata의 60 % = 4.8×0.6 = 2.88컷) 대비 | **2.43 배** |
| non-H 1컷의 정체 | `int_px 0 · edge_visible 126/149 (0.846)` → **E** (림만 보인 프레임) |
| VG-datum | `datum_exact` **8/8** · max \|Δground_z\| **0.000000 m** |
| VG-10 포즈 (d·h·yaw·pitch·roll·hfov) | 불일치 **0** |
| VG-08 세그 사이드카 | 8/8 `.idseg.npz` (단, §7 결함 참조) |
| VG-void 커버리지 | on **1.0000** (103,041/103,041) · off **1.0000** |
| 발자국 | `cells_raw` 92,127 · `cells_kept` 92,127 · `max_diff` **2.87 m** |
| VG-13 과노출 | mean 111.4 · clip 0.057 % · dark 1.62 % — BLOWN/DARK 임계 밖 |

**A팔 72컷 외삽** = 24·0.206 + 48·0.875 = **46.9** (계획 §3.5 기대 33.6).

### 2.4 CUE_CLASS 선언 (렌더 **전** · ACCOUNTING §2-6)

```python
CUE_CLASS = {
    "cue_railing":        "decorative",   # 화강석 동자기둥 난간
    "cue_tactile":        "decorative",   # 갓돌 후방 0.32 m 점형블록 (proud 4 mm)
    "cue_nosing":         "decorative",   # 화강석 3단 논슬립 띠 (proud 12 mm)
    "cue_material_break": "decorative",   # 재질 재바인딩 전용 — 프림 집합 불변
    "cue_sign":           "decorative",   # 하천구역 법정 안내표지 1매
    "cue_scene_dressing": "decorative",   # 억새·벤치·가로등·원경 대안
    "cue_shadow_caster":  "decorative",   # 양버들 열 + 가로등주
    "cue_manhole":        "decorative",   # 관리통로 배수 맨홀 (flush)
    "cue_tree_grate":     "decorative",   # 진입 보행로 수목보호격자 (flush)
    "cue_slab_joint":     "decorative",   # 줄눈·신축이음 (flush)
    "cue_drainage":       "decorative",   # 빗물받이 3개 (flush)
    "cue_bollard":        "decorative",   # 보차도 경계 볼라드 5본
    "cue_delineator":     "decorative",   # 시선유도봉 (기본 OFF — 법4)
    "_structural":        ["BermCrest", "RetainWall", "Riprap", "Water",
                           "Ground/ShoulderStep", "Ground/ServiceWalk"],
}
```

**이 선언이 왜 기계적으로 방어되는가**: 모든 `cue_*` 프림은 x ≤ −0.78(보행 가능측)에 서고,
낙차 발자국(x ≥ −0.33)을 덮는 단서 프림이 **0개**다 — 씬 자기검사 (4)가 매 조립마다
스테이지 전수 AABB로 확인한다(실측 **0건**). 따라서 라벨러 `cells_raw`·`polar_gt`는 `cue_*`
토글에 **구성상 불변**이고, 이것이 VG-01의 실효 내용이다.

### 2.5 개정 이력 (기하 개정 **0회** · 나머지는 착지 전 결함 수정)

| # | 무엇이 잡혔나 | 어떻게 잡혔나 | 조치 |
|---|---|---|---|
| R0 | `ground_kit` 횡단 트렌치가 하드 게이트 **B7(GT-E2)** 위반 — 낙차 모서리 1.8 m 앞 긴 직선 밴드 | `plan_ground` 예외 | 트렌치 제거, 배수 단서를 빗물받이(점 요소) 3개로 조달 |
| R1 | `GKitWalk` region이 잔디 사면까지 덮어 줄눈이 z=0.45에 **떠 있었다** | 씬 자기검사 (2) 전수 AABB — `JX_0` dz **0.2725 m** | region을 관리통로(x −2.35…−0.80)로 축소 · `step_x` 3.0 → **1.6**(U2 유닛셀 정수배) |
| R2 | 잔디 사면을 축정렬 스트립(pitch 0.15 · 라이즈 25 mm)으로 근사 → **가로 줄무늬 논밭**으로 렌더 | 1차 스모크 육안 (h 0.80 · d 10.2) | **같은 평면 위 회전 슬래브 48장**으로 교체 — 면 완전 연속, AABB 오차 ≤ 0.034 m |
| R3 | `Looks/RailStone` 이 이름의 "rail" 토큰 때문에 **metal**(alb_max 0.50)로 분류 → 화강석 동자기둥이 흰 금속 기둥 | 1차 스모크 육안 + `sc._look_spec` 확인 | `Looks/GraniteBaluster`(stone, 0.34) · 볼라드는 별도 `Looks/Bollard`(metal) |
| R4 | 원경 아파트 매스가 상단을 흰 판으로 채움 (alb 0.44 · misc 클래스 = 무처방 상수색) | 육안 + 픽셀 측정 (상단 200행 평균 145–155) | alb **0.29** + `Looks/BgConcrete`(concrete 클래스 → 텍스처 승격·상한 0.34) |

**기하(낙차·둔덕·카메라 밴드) 개정은 한 번도 필요하지 않았다** — 첫 프로브가 곧바로 0.875를
냈다. §3.5의 톱업 규칙(씬당 상한 2회)은 **미발동**.

---

## 3. sceneH7_bend_walk2 — 복도 굴절형

### 3.1 설계 요지

유효폭 3.40 m 보도가 옹벽 사이를 지나다가 (−1.00, −1.70)에서 **직각으로 굴절**하고, 굴절 너머에
**12단 × 0.17 = 2.04 m 하행 계단**이 있다. 은닉체는 **`BendWall`** — `Along`(x ≤ −1.00 · y
−2.34…−1.70)과 `Flank`(x −1.64…−1.00 · y ≤ −1.70)가 만나는 **수직 모서리**다.
브리프의 명시 요구대로 **옹벽 4매·성토 3매는 전부 `hazard_*` 밖**에서 지어지므로 B팔에서도 불변이다.

### 3.2 H 판정식 — 평면 문제 하나로 닫힌다

눈 E = (−d, y_c)에서 낙차점 T = (tx, ty)로 가는 선분은 두 경계선을 반드시 순서대로 지난다.

```
t_y = (y_c + 1.70) / (y_c − ty)      ← y = −1.70 도달 매개변수
t_x = (d − 1.00)  / (d + tx)         ← x = −1.00 도달 매개변수
은닉 ⇔ t_y ≤ t_x
```

최악 T = 발자국 중 **tx 최대 · ty 최대** = **(+2.40, −3.37)** (2단째 상면 −0.34가 hazard_depth
0.30을 처음 넘는 지점의 북쪽 경계).

| y_c | 은닉 성립 최소 d |
|---|---|
| −0.90 | 2.63 |
| −0.45 | 3.55 |
| 0.00 | 4.47 |
| +0.45 | 5.38 |
| +0.90 | 6.30 |

수직 방향은 **항상** 막힌다 — 최대 눈높이 0.34 + 1.90 = **2.24 m** < 옹벽 마루 **2.45 m**.
둔덕형(H6)이 **종단면** 문제 하나로 닫히고 굴절형(H7)이 **평면** 문제 하나로 닫힌다는 점이
두 씬을 별개 계열로 두는 이유이자, 서로 다른 실패 모드를 갖는 이유다(계획 §3.5의 "2계열").

수율은 `_yield_mc()`가 **실제 샘플러**(d LogU · h U · y trunc-N(0,0.35,±0.90) ·
yaw trunc-N(0,8,±20))로 MC 적분하고 폴라 격자 포함(±31.1°·반경 12 m)까지 함께 본다:

| 밴드 | H | none_in_fov | 가시(V/E) |
|---|---|---|---|
| base (d 1.2–12 · h 0.25–1.9) | 0.394 | 0.418 | 0.188 |
| **H** (d 6–12 · h 0.25–1.0) | **0.947** | 0.053 | 0.000 |

### 3.3 실측 (라운드 `260823_v3p5_h67probe_A` · H 밴드 8컷 · L0)

| 항목 | 값 |
|---|---|
| tier 분포 | **H 7 · none_in_fov 1** |
| **strict-H** | **7/8 = 0.875** · Wilson 95 % CI [0.53, 0.98] |
| 계획 가정 (0.60) 대비 | **1.46 배** · 개정 발동선 대비 **2.43 배** |
| non-H 1컷의 정체 | `int_px 0 · edge_projected 0` → **`none_in_fov`** (발자국이 폴라 섹터 밖) — MC 예측 0.053과 표본오차 안에서 일치 |
| **가시(V/E) 컷** | **0** — 이 밴드에서 굴절 은닉은 예외 없이 성립 |
| VG-datum | `datum_exact` **8/8** · max \|Δground_z\| **0.000000 m** |
| VG-10 포즈 | 불일치 **0** |
| VG-void 커버리지 | on **1.0000** · off **1.0000** |
| 발자국 | `cells_raw` 6,221 · `cells_kept` 6,219 · `max_diff` **2.623 m** |
| VG-13 과노출 | mean 132.3 · clip 0.000 % · dark 0.17 % |

**`max_diff` 2.623 m 가 낙차 2.04 m 보다 큰 이유** — **벽면 손잡이**다. A팔에서 계단 경사를
따라 내려가고 C팔에서 수평(z 0.90)을 따르므로, 손잡이가 덮는 폭 0.083 m × 2줄 구간에서
`z_off − z_on` 이 2.6 m로 읽힌다. 그 셀들은 **어차피 발자국 안(슬롯)** 이므로 발자국 면적은
늘지 않고 영향은 `cell_mean_drop` 통계에만 남는다. 씬 자기검사 (4)가 이 초과분을
**사전 선언분 28건 / 미선언 0건**으로 인쇄한다.

**A팔 48컷 외삽** = 24·0.394 + 24·0.875 = **30.5** (계획 §3.5 기대 19.2).

### 3.4 CUE_CLASS 선언

```python
CUE_CLASS = {
    "cue_railing":        "decorative",   # 벽면 계단 손잡이 2줄
    "cue_level_handrail": "decorative",   # 평지 복도 손잡이 (FA_REALITY L7 ★3)
    "cue_tactile":        "decorative",   # 계단 상단 점형블록 (계단참 위)
    "cue_nosing":         "decorative",   # 종단 2단 + 계단 12단 나이징
    "cue_material_break": "decorative",   # 재질 재바인딩 전용
    "cue_sign":           "decorative",   # 지하보도 유도표지 1매 (WallE 벽면)
    "cue_scene_dressing": "decorative",   # 성토 상단 관목·벤치·원경
    "cue_shadow_caster":  "decorative",   # 성토 상단 가로수 열 (전부 북측)
    "cue_manhole":        "decorative",   # 보도 맨홀 (flush)
    "cue_tree_grate":     "decorative",   # 기본 OFF — 코드 경로·좌표 보유
    "cue_slab_joint":     "decorative",   # 줄눈 (flush)
    "cue_drainage":       "decorative",   # 횡배수 트렌치 x=−5.00 (flush)
    "cue_bollard":        "decorative",   # 회랑 입구 2본
    "_structural":        ["BendWall", "WallN", "WallE", "Bank",
                           "Walk/Landing", "Walk/Step"],
}
```

> **프림 경로 접두어 주의** — 이 씬에는 `…/Walk/Lower`(상부 보도 하단 구간, 구조물)와
> `…/Lower/Floor`(하부 통로, 낙차)가 **동시에** 있다. `cue_prim_map.json` 과 VG-06 구현은
> 계획 §6.3이 규정한 **루트 앵커 접두어 매칭**(`/World/SceneH7/Lower/`)을 써야 하며,
> 부분문자열 매칭(`"/Lower"`)을 쓰면 두 프림이 섞인다. 본 보고의 §4 측정은 앵커 매칭으로 냈다.

### 3.5 단서를 양팔에 살려 둔 두 장치 (VG-03 전제)

`cue_nosing`·`cue_railing`은 위험 기하에 붙기 쉬운 단서다. 그대로 두면 C팔(위험 OFF)에서
사라져 **VG-03(단서 마스크 불변)** 이 깨진다. 두 가지로 해결했다:

- **`cue_railing`** — 벽면 손잡이는 A팔에서 계단 경사를, C·D팔에서 **수평(z 0.90)** 을 따른다.
  평지 통로에 수평 손잡이가 서는 것은 **편의증진법 시행령 별표2가 의무화**하는 실제 구성이므로
  대체물이 아니라 같은 부재의 같은 용도다.
- **`cue_nosing`** — 보도에 **종단 2단 단차(x −9.10…−8.46 · 라이즈 0.17)** 를 **팔 불변 지형**으로
  두고 나이징을 먼저 거기에 놓는다. 계단 12단 위의 띠만 위험 기하에 종속되며, 그 사실을
  조립 로그가 매 팔마다 `보도 종단 2단(팔 불변) + 계단 12단` 으로 인쇄한다.

같은 이유로 H6의 `cue_nosing`은 **화강석 3단(둔덕 사면, 팔 불변 지형)** 에 붙는다.

---

## 4. VG-06 모서리 소속 — ID 마스크 실측

계획 §2.1이 두 씬에 요구한 것은 *"가시 종단 모서리의 주인이 가림체이고, 낙차 림·내부 기여가
0 px"* 이다. `instance_id_segmentation` 마스크를 **루트 앵커 접두어**로 집계했다.

| 씬 | 가림체 접두어 | 가림체 화면 기여 | 낙차 구조물 접두어 | 낙차 구조물 화면 기여 |
|---|---|---|---|---|
| sceneH6 | `/World/SceneH6/BermCrest` | 17,873 px | `/RetainWall/` · `/Riprap/` · `/Water/` | **0 px** |
| sceneH7 | `/World/SceneH7/BendWall/` | 390,576 px | `/Stair/` · `/Lower/` | **0 px** |

⇒ **strict-H 프레임에서 낙차 구조물은 화면에 단 한 픽셀도 없고, 가시 지면의 종단선은 가림체가
소유한다.** 두 씬 다 VG-06 적합.

> **위 표는 `…probe_A`(§7 결함으로 마스크가 첫 컷에 고정) 기준이라 증거력이 1컷이었다.**
> `…rev_A` 재렌더로 **컷별 신선 마스크 8컷 × 2씬** 을 다시 재어 §7.5에 실었다 —
> 결론 동일: **strict-H 7/7 컷에서 낙차 구조물 화면기여 0 px**, 가림체 기여 7/7.

---

## 5. §2.0 공통 표준 적합성 체크리스트

| # | 표준 (계획 §2.0) | sceneH6 | sceneH7 | 근거 |
|---|---|---|---|---|
| 1 | **생활권 유형** 4종 중 하나 | ✅ 제방·수변 | ✅ 보도 | 파일 상단 선언 |
| 2 | **씬 조립 공식** ①경로 ②위험 ③토글 단서 ④은닉 | ✅ | ✅ | 파일 상단 4요소 표 |
| 3 | *"주변 환경은 장식이 아니라 단서 ③ 그 자체"* | ✅ 억새·맨홀·격자·볼라드·표지 | ✅ 손잡이·표지·줄눈·측구·가로수 그림자 | `[cue]` 조립 로그 |
| 4 | **법1** 손상·노후 표현 금지 | ✅ 잡초 데칼도 `surface=None` 으로 끔 | ✅ 동상 | `plan_ground(overrides=surface=None)` |
| 5 | **법2** 임의 경고판 금지 | ✅ 법정 제식 1매(`sign_info`) | ✅ 법정 제식 1매(`sign_underpass`) | `build_sign` 호출 1회 |
| 6 | **법4** 기능 필수성 · 비움이 기본값 | ✅ 조형물 0 · `cue_delineator` 기본 OFF | ✅ 조형물 0 · `cue_tree_grate` 기본 OFF | SCENE_CONFIG |
| 7 | **법5** 차량·계절소품 금지 | ✅ 0 | ✅ 0 | 프림 인벤토리 |
| 8 | **법6** 재질 동결 (신규 역할 0) | ✅ 기존 TEX 역할만 | ✅ 동상 | `ASSET_ROLES` |
| 9 | **법7** `cue_*` 기하 불변 | ✅ 최대 융기 12 mm(나이징) | ✅ 동상 | 자기검사 (1)(2) |
| 10 | **법8** 근거 태그 | ✅ `[규격]`/`[계획]`/`[computed]`/`[측정]` | ✅ | 파일 전역 |
| 11 | **조명/HDRI** L0–L7 · 과노출 금지 | ✅ clip 0.057 % | ✅ clip 0.000 % | `img` 레코드 |
| 12 | **재질 3단** (지면·구조물 / 식생·목재 / 금속·도색·수면) | ✅ | ✅ | `setup_materials` |
| 13 | **props 규율** 볼라드 h 0.8–1.0·φ0.1–0.2·간격 ~1.5·반사띠 | ✅ h 0.88·φ0.15·피치 **1.50** | ✅ h 0.88·φ0.15 (2본, 개구 2.24 — §5-3) | LINT-6 |
| 14 | **props** 격자·등간격 금지 | ⚠️ **의도적 정렬** — §5-2 | ⚠️ 동상 | LINT-10 |
| 15 | **props** 순백(>0.8) 대면적 금지 | ✅ 상단 200행 평균 145–155/255 | ✅ | 픽셀 측정 |
| 16 | **표준 장비 16키** · 사문 0 | ✅ 16키 전부 읽고 전부 프림/재질 생성 | ✅ 16키 | 자기검사 |
| 17 | **v3 신설 3키** 배선 | ✅ shadow_caster·manhole·tree_grate 전부 ON | ✅ shadow_caster·manhole ON · tree_grate 코드 보유(기본 OFF) | SCENE_CONFIG |
| 18 | **프림 위생** — 단서는 자립 프림, `hazard_*` 분기 밖 | ✅ hazard 분기 2줄, 단서 0줄 | ✅ 동상 | `grep 'cfg\["hazard_stairs"\]'` |
| 19 | **카메라 데이텀** — 단서를 x<0·\|y\|≤0.90·d∈[1.2,12] 스트립에 세우지 말 것 | ✅ `datum_fail` 0 · 실측 Δ **0.000000 m** | ✅ 동상 | VG-datum |
| 20 | **void 커버리지 1.0** (개방 바닥 금지) | ✅ 103,041/103,041 | ✅ 103,041/103,041 | `heightmap_meta` |
| 21 | **커밋 전 검증 4종** | ✅ 4/4 green | ✅ 4/4 green | §5-1 |
| 22 | **룩체크 R7 사용자 게이트** | ⬜ **미실시 — 사용자 검수 대기** | ⬜ 동상 | §8 |

### 5-1. 커밋 전 검증 4종 (`process_spec_v1.md:32-40`)

| 게이트 | 결과 |
|---|---|
| `py_compile` | **PASS** (2/2) |
| `NEGOBS_SMOKE=1` 씬 실행 | **PASS** — 두 씬 다 CPU 자기검사 전항목 통과 |
| `geom_invariance_check.py` | **PASS** — R-5 잔존참조 0 · R-4/R-6 해시 3자 일치 (sceneH6 256프림 · sceneH7 234프림) |
| `placement_lint.py` | **PASS** (exit 0) — ERROR 0 · WARN 2 · BLOCKED 2 |

### 5-2. LINT-10 「배치 지터」 판정 — 정렬을 택했다

`user_feedback_v5_1 §2`는 *"격자·등간격 금지, yaw ±3–8° 지터"* 를 요구하고, 07-30 룰링
**J-3/J-5(배치 지터 폐지)** 는 그 반대를 요구하며 `placement_lint` LINT-7/LINT-10이 후자를
강제한다. 두 씬은 **후자를 따랐다**:

- 볼라드 피치 **1.50 m**는 교통약자법 시행규칙 별표2 제7호의 **법정 수치**다 — 규칙성이
  결함이 아니라 요건이다. 위치 지터를 넣으면 LINT-6의 피치 규칙을 스스로 깬다.
- 화강석 동자기둥도 정렬해 세운다(석재 난간의 실제 시공).
- 벤치·표지 yaw는 **축값만**(0/90/180/270) 쓴다 — LINT-7 declared 게이트 통과.

불규칙성은 대신 **재질·그림자·지면 문양**이 담당한다(`ground_kit` 줄눈·맨홀, 가로수 그림자 밴드).

### 5-3. sceneH7 볼라드 개구 2.24 m (LINT-6 WARN 1건, 사전 선언)

유효폭 3.40 m 회랑에서 볼라드 2본의 중앙 개구를 1.5 m로 좁히면 **카메라 데이텀 스트립
(|y| ≤ 0.95)** 을 침범해 `datum_fail` 이 된다. 개구 2.24 m는 ⓐ 휠체어 유효폭과 ⓑ VG-datum을
동시에 만족시키는 최소값이고, 그 대가로 LINT-6이 **추론 런에 대한 advisory 경고 1건**을 남긴다
(하드 규칙 아님). 사전 선언분이다.

### 5-4. `placement_rules_v1.yaml` C-9 레지스트리 추가 (**정본 문서 수정 1건**)

LINT-6의 `carrier_set`은 볼라드를 가진 씬의 **레지스트리**다 — 목록에 없는 씬이 볼라드를
조립하면 ERROR, 목록에 있는데 조립하지 않아도 ERROR. 신설 씬 2개를 추가했다(+6행, 주석 포함).
**가산적 변경**이므로 기존 33씬의 판정은 한 칸도 움직이지 않는다. 규칙 파일 자신의 원칙
(*"thresholds are data, not code, so a spec change is a YAML diff"*)에 부합한다.

**회귀 확인** — `placement_lint.py --scenes all` (35씬) 실측: ERROR 16 · WARN 346 · BLOCKED 31.
ERROR 16건은 전부 기존 씬 소유다 — `scene02` 볼라드 4 · `scene06` 볼라드 6 · `scene12` 1 ·
`sceneC2` jit_pos/jit_yaw 4 · `sceneN5` jit_pos 1. **sceneH6·sceneH7 의 ERROR 기여는 0건**이다.

### 5-5. LINT-5 `walk_edges` 미선언 (sceneH6, WARN 1건 — 의도)

LINT-5는 「도로의 구조·시설 기준에 관한 규칙」 제16조의 **보도 유효폭**을 재는 규칙인데
sceneH6의 접근부는 보도가 아니라 제방 진입 **광장**이다. 없는 데이텀을 지어내면 그 규칙은
검사가 아니라 허구가 되므로 **선언하지 않고 `nodata`로 남긴다**. sceneH7은 진짜 보도이므로
`walk_edges`를 선언했고 LINT-5는 **live로 통과**한다.

> 참고: 기존 33씬은 `PLACEMENT` 블록을 **0개** 선언해 LINT-1/1b/3/5/9가 구조적으로 죽어 있다
> (`placement_rules_v1.yaml` `known_gaps`). 신설 2씬은 그 상태를 승계하지 않고 블록을 선언했다 —
> 프림을 하나도 만들지 않는 순수 선언이라 기하·GT·높이맵 영향이 **0**이다.

---

## 6. 신설 씬을 어떻게 렌더했나 (정본 무수정)

### 6.1 AZ 원장 런타임 확장

정본 드라이버의 부모 절반은 씬 목록을 `vk.AZ_LEDGER`(33씬)에서 가져오고 자식 절반은
`vk.ledger()`·`vk.split_of()`를 부른다. 신설 씬은 아직 그 원장에 없고, 더 나쁜 것은
`split_map()`이 `sorted(AZ_LEDGER)`를 시드 셔플하므로 **씬 하나만 추가해도 기존 33씬의
디렉터리 분할이 전부 재배치된다**는 점이다.

`h67_probe.py`는 원장을 **런타임에만** 확장한다 — ① 먼저 `split_map(0)`을 호출해 기존 33씬의
분할을 캐시에 확정시키고 ② 그 캐시에 sceneH6/H7을 `val`로 **핀**한 뒤 ③ 원장에 두 행을 넣고
④ 확장 전후를 비교해 **기존 씬 분할 이동 0건**을 기계 확인한다(로그: `기존 33씬 분할 불변 확인`).

그리고 `run_data_render.scene_proc()`를 **같은 프로세스 안에서** 직접 부른다 —
CUE_COVERAGE §4-4 (6)이 *"신설 씬을 정본 라이브러리에 넣기 전까지는 이 경로가 유일하다"* 고
적어 둔 그 경로다. 부모 `drive()`가 자식을 새 인터프리터로 띄우면 런타임 패치가 전달되지 않는다.

> **W2/W3 본렌더 전에 해야 할 일**: 원장 등재는 결국 `variation_kit.py`를 건드려야 하고,
> 그때 `split_map`의 셔플이 기존 33씬을 재배치하지 않도록 **핀 테이블이 필요하다**.
> 본 프로브의 `register()`가 그 요구사항의 실행 가능한 명세다.

### 6.2 라운드 스탬프 가드 (VG-12)

`h67_probe.py`가 허용목록 6개(`260823_v3p5_h67{smoke,probe,rev}_{A,C}`) 밖의 스탬프를 렌더 **전에**
거부한다. 러너는 rc만으로 성공을 판정하지 않고 **산출물 수(png/depth/idseg/heightmap)** 로
판정한다 — Isaac의 `fastShutdown` 경로는 씬이 예외로 죽어도 종료코드 0을 돌려주는 일이 있고
(실측: sceneH6의 `ground_kit` U2 위반이 rc=0으로 보고됐다), 그 함정에 두 번 빠졌다.

---

## 7. 부수 발견 — **ID 마스크 사이드카의 stale-frame 결함** (계획 반영 필요)

### 7.1 증상

`260823_v3p5_h67probe_A` 는 씬당 8컷을 찍었는데 `.idseg.npz` **8개가 바이트 동일**했다:

| 씬 | idseg blake2b(6B) | 고유 id 수 | 파일 크기 |
|---|---|---|---|
| sceneH6 | `47a05438f412` × **8컷 전부** | 56 | 50.4 KB |
| sceneH7 | `1b18fb37a803` × **8컷 전부** | 24 | 27.9 KB |

같은 라운드의 `.depth.npy` 는 컷마다 다르다(`6c807d94e3ab` / `07459e9b59d0` / `b9c69767cb81` /
`8fac08e98f9c` …). 즉 **깊이는 갱신되고 ID 마스크만 첫 컷에 고정**된다.

### 7.2 원인

`run_data_render._seg_fetch` 의 에스컬레이션 사다리 첫 단 **`t0`(추가 tick 0회)** 가
`instance_id_segmentation` 애노테이터를 **다시 평가시키지 않는다**. shape이 맞고 `max() > 0`
이므로 사다리는 성공으로 보고 상위 단(`t1`/`t4`/`orch`)으로 올라가지 않는다.
`sim_app.update()` 만으로는 이 애노테이터가 갱신되지 않고 Replicator **orchestrator step**이
필요하다 — depth는 `"orch"`가 필요했다고 계획 §6.3이 이미 적어 두었으므로, **세그만 `t0`로
끝난 것이 오히려 신호**였다.

### 7.3 왜 P-5 스모크가 못 잡았나

그 스모크는 **1컷**이었다(`--cams 1`). 1컷 라운드에서는 stale과 fresh가 **구별되지 않는다.**
계획 §6.3의 *"추가 렌더 비용 0 — `idseg_fetch = "t0"`, 즉 추가 tick 0회·orchestrator step 불필요"*
는 그래서 **1컷 관측으로부터의 과잉 일반화**다.

### 7.4 파급

- **VG-06(모서리 소속)** 은 A팔 H 프레임 **각각**에서 가림체 소속을 검사해야 한다.
- **DZ §12-5의 단서 임계 k** 는 **컷별** cue 픽셀 수를 요구한다(§4.4.1의 X 정의가 그 위에 선다).
- 두 게이트 모두 이 결함이 남으면 **조용히 첫 컷 하나만 검사**하고 나머지 프레임에는
  같은 판정을 복제한다. `idseg_n_ids` 필드도 전 컷 동일값이 되므로 **로그만 봐서는 안 보인다.**

### 7.5 검증 (프로브 로컬 우회 · 정본 무수정)

`h67_probe.py --seg-strict` 는 `_seg_fetch` 를 **프로세스 로컬로** 감싸 `t0`/`t1`/`t4` 단을
건너뛰고 곧장 `rep.orchestrator.step()` 을 부른다. 같은 시드·같은 밴드·같은 기하로 A팔만
재렌더한 라운드가 `260823_v3p5_h67rev_A` 다.

**결과 — 결함 확정, 우회 유효:**

| 라운드 | `idseg_fetch` | `.idseg.npz` 서로 다른 해시 | `idseg_n_ids` | s/컷 |
|---|---|---|---|---|
| `…probe_A` sceneH6 | `t0` | **1 / 8** | `[56]` — **전 컷 동일** | 5.101 |
| `…probe_A` sceneH7 | `t0` | **1 / 8** | `[24]` — 전 컷 동일 | 5.689 |
| `…rev_A` sceneH6 | `orch_forced` | **8 / 8** | `[39, 41, 45, 54, 56, 82, 92, 93]` | 5.225 |
| `…rev_A` sceneH7 | `orch_forced` | **8 / 8** | `[18, 20, 21, 24, 26, 27, 29]` | 5.050 |

- **렌더 비용은 사실상 0이다** — 5.101 → 5.225 (+2.4 %) · 5.689 → 5.050 (−11 %), 즉 라운드 간
  잡음 안이다. 계획 §6.3의 *"추가 렌더 비용 0"* 결론 자체는 살아남고, **틀린 것은 `t0` 단
  하나**다.
- **tier 판정은 바뀌지 않았다** — `rev_A` 를 `probe_C` 와 짝지어 다시 라벨링한 결과
  `sceneH6 {H 7, E 1}` · `sceneH7 {H 7, none_in_fov 1}` 로 **컷별 tier 전부 동일**.
  즉 §2·§3의 strict-H 수율 수치는 이 결함과 무관하게 유효하다(라벨러는 세그를 쓰지 않는다).
- **VG-06 재측정 (컷별 신선 마스크 8컷 × 2씬)**:

| 씬 | strict-H 컷 | 가림체 화면기여 > 0 | **낙차 구조물 화면기여 > 0** | 단서 픽셀 범위 |
|---|---|---|---|---|
| sceneH6 | 7 | **7 / 7** | **0 / 7** | 24,629 – 112,747 px |
| sceneH7 | 7 | **7 / 7** | **0 / 7** | 16,392 – 105,537 px |

  내부 정합성 증거 하나 더 — sceneH6의 **E 티어 1컷(cut 0001)** 은 ID 마스크에서 낙차 구조물
  **77,916 px** 을 보유한다. 라벨러의 tier 판정(깊이 재투영)과 ID 마스크(렌더러 인스턴스)가
  **서로 독립인 경로인데 같은 답**을 냈다.

### 7.6 권고

1. **`_seg_fetch` 의 사다리에서 `t0` 단을 제거**하고 첫 단을 `orch` 로 둔다. 실측 비용이
   잡음 안(§7.5)이므로 "빠른 경로"를 지킬 이유가 없다. (대안: `t0` 결과를 직전 컷과 비교해
   동일하면 승급 — 코드가 늘고 이득은 없다.)
2. `check_data_run.py` 에 **"라운드 안에서 `idseg_n_ids` 가 전 컷 동일하면 FAIL"** 규칙을
   넣는다. 이 필드는 **이미 `variation.json` 에 있고** stale일 때 상수, 정상일 때 컷마다
   다르다(§7.5 표) — 파일을 열지 않고도 도는 **저비용 상시 탐지기**다.
3. 계획 §6.3의 *"추가 렌더 비용 0 — `idseg_fetch = "t0"`"* 문장을 갱신한다: 비용 0 결론은
   유효하나 **`t0` 는 1컷 라운드에서만 유효**하고, 다컷 라운드는 `orch` 가 필요하다.
4. VG-08(세그 사이드카 존재)의 검사 항목에 **"컷별 마스크가 실제로 다른가"** 를 추가한다 —
   현행 정의(`.idseg.npz` 존재 + `idseg_fetch ≠ "empty"`)는 이 결함을 통과시킨다.

---

## 8. 남은 것 (사용자 게이트 / 후속 WP)

| # | 항목 | 성격 |
|---|---|---|
| 1 | **룩체크 R7 사용자 검수** — `make_review_gallery.py --round 260823_v3p5_h67probe_A` 후 체크리스트 5항 | **사용자 게이트** (process_spec §27-31) |
| 2 | §7의 세그 사이드카 결함 — 정본 `run_data_render.py` 수정 | **결재 대상** (정본 드라이버 수정) |
| 3 | `variation_kit` AZ 원장 정식 등재 + `split_map` 핀 테이블 | W2/W3 본렌더 전 필수 (§6.1) |
| 4 | B팔 레버 확정 — 두 씬은 `cue_material_break` 가 **재바인딩 전용**이라 높이맵 비트 동일이 구성상 보증된다. 나머지 12키는 W0 VG-CLS 판정 대상 | W0 후속 |
| 5 | base·H2 밴드 실렌더 (본 프로브는 **H 밴드만**) | W2 |
| 6 | `sceneH6` 의 `cue_delineator`, `sceneH7` 의 `cue_tree_grate` 는 기본 OFF — 어블레이션 팔에서만 켜진다 | 설계 의도 |

---

## 부록 A — 재현 명령

```bash
# CPU 자기검사 (pxr·GPU 불필요)
NEGOBS_SMOKE=1 python3 scenes/main/sceneH6_berm_levee2.py
NEGOBS_SMOKE=1 python3 scenes/main/sceneH7_bend_walk2.py

# 커밋 전 검증 4종
python3 -m py_compile scenes/main/sceneH{6,7}_*.py
python3 scripts/geom_invariance_check.py --scenes sceneH6,sceneH7
python3 scripts/placement_lint.py       --scenes sceneH6,sceneH7

# GPU — 스모크 → H밴드 프로브 (tmux h67build · flock 직렬화)
bash experiments/v3_0823/code/run_h67_probe.sh smoke
bash experiments/v3_0823/code/run_h67_probe.sh probe
bash experiments/v3_0823/code/run_h67_probe.sh segstrict     # §7 검증

# 라벨 + 수율 측정
PY=/home/vislab/miniconda3/envs/env_seg/bin/python
cd experiments/mainrun_0819/code/labeling
$PY labeler.py --on-round  $PWD/../../../../dataset/260823_v3p5_h67probe_A \
               --off-round $PWD/../../../../dataset/260823_v3p5_h67probe_C \
               --grid gridspec_v1.json \
               --out ../../../v3_0823/annotations/h67_probe_labels.json --workers 4
cd - && python3 experiments/v3_0823/code/h67_yield.py \
        --labels experiments/v3_0823/annotations/h67_probe_labels.json \
        --on dataset/260823_v3p5_h67probe_A --off dataset/260823_v3p5_h67probe_C --band H
```

## 부록 B — val strict-H 회계 갱신 (계획 §3.5 대비)

| 공급원 | 분리 | 계열 | 밴드 | A팔 컷 | 계획 기대 | **본 보고 실측 기반 추정** |
|---|---|---|---|---|---|---|
| sceneH6_berm_levee2 | val | 둔덕형 | base+H+H2 | 72 | 33.6 | **46.9** (base 0.206 모형 · H 0.875 실측) |
| sceneH7_bend_walk2 | val | 복도 굴절형 | base+H | 48 | 19.2 | **30.5** (base 0.394 MC · H 0.875 실측) |
| scene20 (기존) | val | — | base+E+E2 | 72 | 6 `[measured]` | 6 |
| **합** | | **2계열** | | **192** | **58.8** | **83.4** |

| 안전 여유 | 계산 |
|---|---|
| 요구 (DZ §4.3-3) | **30** |
| 본 보고 추정 | **83.4** (여유 **2.78 배**) |
| 수율이 추정의 60 %로 무너져도 | **52.4** ✅ |
| 수율이 추정의 40 %로 무너져도 | **37.0** ✅ |

⇒ 계획 §3.5의 톱업 규칙(미달 시 H 밴드 1개 추가, 씬당 상한 2회)은 **현 시점 미발동**이다.
단, 위 추정의 base 밴드 항은 **모형값**이고 실렌더가 아니다 — W2에서 base·H2 밴드가
착지하면 이 표를 실측으로 갱신해야 한다.
