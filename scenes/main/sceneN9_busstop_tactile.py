# -*- coding: utf-8 -*-
"""
sceneN9_busstop_tactile.py — NegObs 신규 씬 N9: **버스정류장 승강장 경고블록**
                             (④-a 함정 표본 · Isaac Sim 4.5)

계열    : **N-cue (단서 有 · 위험 無)** · 생활권 = **보도**
사다리  : **FA_REALITY §3 L6** — *"버스정류장·승강장 경계 경고블록 — 실제 단차는 연석
          0.15–0.25 m"* · 난이도 **★★★☆☆ (★3)**
정본    : `experiments/v3_0823/RENDER_PLAN_V3.md` §2.0(공통 표준) · §2.4 표
          `sceneN9_busstop_tactile` · §2.6(CUE_CLASS 사전 분류) · §3.1–3.2(test-ext 사양)
분리    : **test-ext** — v2·v3 **양 모델 모두 미학습**. 훈련·검증에 절대 넣지 않는다(§3.1).
          **4팔 전부 제작 의무**(DZ §4.2 `:243`) — A·B·C·D 완비.
밴드    : base · base2 (둘 다 기본 `CAM_DIST` 지지집합 · 시드만 다른 2차 draw)
          씬당 팔당 48컷 · 4팔 합 192

════════════════════════════════════════════════════════════════════════════
**이 씬이 존재하는 이유** — ④-a 함정 표본

계획 §2.4 표: *"승강장 경계 detectable warning 은 전 구간 요구. **철도 승강장(진짜 낙차)과
버스정류장(연석 0.15–0.25 m)이 동일 제식**"* / 지름길 모델의 오답 = *"철도에서 배운
'경고블록 = 큰 낙차' 전이"*.

즉 이 씬은 **단서가 있고 위험이 없는** 칸(C팔)을 채우는 표본이며, 판정 기준이 H 씬과 다르다:

  · H 씬   — strict-H 수율 · paired-H · 모서리 소속(VG-06)
  · **N 씬 — 전 팔·전 프레임 GT 올-음성 + 단서 가시성(§12-5 k) + (C,D) 광학차**

`h67_yield.py` 를 이 씬에 돌리면 *"strict-H 0 — 미달"* 을 인쇄하는데 **그 문장은 이 씬에
대해 무의미하다**(sceneL1 의 섹터 게이트와 같은 구조 — SCENE_TEXT_BUILD §12-9).

D58 ③ 이 이 씬에 거는 유일한 실질 요구는 **함정의 무죄가 눈으로 읽혀야 한다**는 것이다:
*"화단 난간은 화단으로 읽혀야 한다 — 절약은 씬 품질에서 하지 않는다."*
여기서는 **정류장으로 읽혀야 한다** — 승차대(쉘터)·벤치·노선안내판·정류장 표지주·
정차대 노면표시가 전부 있어야 점형블록 띠가 "승강장 경계 경고"로 읽히고,
그것이 없으면 이 씬은 그냥 "노란 띠가 그려진 보도"이고 함정으로 성립하지 않는다.

════════════════════════════════════════════════════════════════════════════
**팔 사상 (계획 §1.0 — 팔의 이름은 레시피, 판정은 사실)**

계획 §1.0: *"무낙차 씬의 `hazard_*` 키는 낙차가 아니라 **함정을 짓는다**. 따라서 이 씬들의
on팔이 이미 C팔(단서 有·위험 無)이며 여기서 'A팔'이라는 말은 성립하지 않는다."*

이 씬의 `hazard_platform_edge` 는 **승강장 경계 단차** = 차도면을 연석 높이만큼 내리는
토글이다. 그 단차는 **0.200 m** — `gridspec_v1.hazard_depth_m = 0.30` 미만이므로
라벨러의 발자국 `z_off − z_on ≥ 0.30` 은 **한 셀도 켜지지 않는다**(`cells_raw = 0`).

  | 렌더 레시피 팔 | `hazard_platform_edge` | `cue_*` | **사실 판정** |
  |---|---|---|---|
  | A | True  | 전부 ON  | **C (단서 有·위험 無)** |
  | B | True  | 전부 OFF | **D (단서 無·위험 無)** |
  | C | False | ON 유지(`keep_dressing`) | **C** |
  | D | False | 전부 OFF | **D** |

⇒ **네 팔 전부 GT 올-음성**이고, 계기판 ③(용량-반응)이 쓰는 대조는 위험 축이 아니라
   **단서 축 (C,D)** 다. (A,C) 광학차(VG-07)는 "차도가 0.20 m 내려가 있나"만 재므로
   이 씬에서는 부수 로그다.

**왜 0.200 m 인가 (사후 선택 아님 · 렌더 전 선언)**: FA_REALITY §3 L6 이 명시한 실측 밴드가
`연석 0.15–0.25 m` 다. 그 밴드의 중앙값을 쓰고, 임계 0.30 m 까지 **0.100 m 여유**를 남긴다.
「도로의 구조·시설 기준에 관한 규칙」의 보도 연석 표준 높이(0.15~0.25 m)와 같은 밴드다.

════════════════════════════════════════════════════════════════════════════
씬 조립 공식 (4요소 — 브리프 §2.0)
  ① 경로   간선도로변 보도 유효폭 **3.40 m** (z 0.000) — 승강장·시설물대와 같은 레벨
  ② 위험   **없다.** 유일한 표고차는 **연석 0.200 m** 이고 임계 0.30 m 미만이다.
           `hazard_platform_edge` 는 그 연석을 짓는 토글이지 낙차 토글이 아니다.
  ③ 단서   **승강장 경계 점형블록 띠(L6 · 이 씬의 주 단서)** · 선형블록 유도로 ·
           **보행자 방호울타리(L4)** · 승차대 쉘터 · 벤치 · 노선안내판 · 정류장 표지 ·
           볼라드 · 정차대 노면표시 · 맨홀 · 수목보호격자 · 줄눈 · 빗물받이 · 가로수 그림자
  ④ 은닉   **없다.** 은닉할 낙차가 없다. `BermCrest`·`BendWall` 같은 가림체 프림 0개.

*"주변 환경은 장식이 아니라 단서 ③ 그 자체다"* — 점형블록만 깔면 이 씬은 실패다.

────────────────────────────────────────────────────────────────────────────
좌표계 · 횡단면 (walk axis = +X, Z-up, m. 카메라는 x = −d, |y| ≤ 0.90 에서 +X 를 본다)

   y
  +40.0 ┌──────────────────────────────────────────────────────┐
        │  상가 건물동 (원경 · 높이맵 격자 |y| ≤ 8 **밖**)      │  Dress/Shop
  +8.80 ├──────────────────────────────────────────────────────┤
        │  상가 전면 공지 (화강석 판석)          z = 0.000      │  Ground/Frontage
  +4.10 ├──────────────────────────────────────────────────────┤
        │  건물측 시설물대 2.40 — 가로수·수목보호격자·가로등   │  Ground/Furnish
  +1.70 ├──────────────────────────────────────────────────────┤  z = 0.000
   0.00 │  ① 보도 유효폭 3.40 (인터로킹 블록)    z = 0.000     │  Ground/Walk
  −1.70 ├──────────────────────────────────────────────────────┤
        │  **승강장 대기공간** (화강석 판석)     z = 0.000      │  Ground/Platform
        │     쉘터 · 벤치 · 노선안내판 · 정류장 표지주          │
  −3.12 ├──────────────────────────────────────────────────────┤
        │  **③ 점형블록 띠 세로 0.60 m** (proud 4 mm)          │  Tactile/Edge  ← 주 단서
  −3.72 ├──────────────────────────────────────────────────────┤
        │  연석 배면 여유 0.30 m — 방호울타리·볼라드 자리       │  Ground/Setback
  −4.02 ├──────────────────────────────────────────────────────┤
        │  **연석** (화강석 B형 폭 0.18) 상면 z = 0.000         │  Curb
  −4.20 ├──────────────────────────────────────────────────────┤
        │  **차도 · 정차대** 아스팔트  z = **−0.200**           │  Road   ← ② 유일한 표고차
  −40.0 └──────────────────────────────────────────────────────┘

  종단(보행축): **전 구간 z = 0.000 · 계단 0단 · 경사 0**. 평탄 승강장이므로
                `cue_nosing` 은 대상 기하가 없다(법4 "비움이 기본값" → 기본 OFF, 코드 보유).

  **표고차 = 0.000 − (−0.200) = 0.200 m < 0.300 m (gridspec_v1 hazard_depth_m)**
  ⇒ 발자국 `cells_raw = 0` · `polar_gt` 올-제로 · tier `none_in_fov` (전 팔·전 프레임)

────────────────────────────────────────────────────────────────────────────
**D78 측방 사각과의 관계** (SCENE_TEXT_BUILD §12-9.3)

라벨러 `step_gate` 의 `_outward()` 8이웃 양자화는 **보행축과 나란한** 위험을
`d ≤ −x₀ + √3·y_lip` 밖에서 보지 못한다. 이 씬의 연석선(y = −4.20)은 정확히 그런
축방향 선이고 한계는 `d ≤ 2 + √3 × 4.20 = 9.27 m` 다.

**그러나 이 씬에서는 그 사각이 발동하지 않는다** — 발자국은 스텝 게이트 **이전에**
이미 비어 있기 때문이다(`cells_raw` 는 카메라 무관량이고 0 이다). 이것이 중요한 이유:
*"GT 가 0 인 것이 게이트의 사각 때문인가, 정말 위험이 없어서인가"* 를 구분할 수 있는
유일한 기계 증거가 `cells_raw` 이며, 본 씬의 게이트 배터리는 그 값을 반드시 인쇄한다.
(`cells_kept = 0` 만 보고 "음성"이라고 하면 그것은 사각과 구별되지 않는다.)

────────────────────────────────────────────────────────────────────────────
**격자 안 최저점 회계** — 이 씬이 인쇄해야 하는 수치

높이맵 격자 x ∈ [−2, 14] · |y| ≤ 8 안에서 보행면(z = 0.000) 대비 가장 낮은 지점:

  | 요소 | 최저 z | 보행면 대비 | 임계 0.30 대비 |
  |---|---|---|---|
  | 차도·정차대 아스팔트 | −0.200 | **0.200 m** | −0.100 (여유) |
  | 빗물받이 그레이팅 (보도측 · flush) | −0.008 | 0.008 m | — |
  | 수축줄눈 recess | −0.003 | 0.003 m | — |
  | 그 밖 전부 | 0.000 | 0 | — |

⇒ **격자 안 어디에도 0.30 m 이상의 하강이 없다.** 이것이 ④-a 함정의 정의다.

────────────────────────────────────────────────────────────────────────────
프림 위생 · 데이텀 (CUE_COVERAGE §4-4 (2)(3)(4))

1. 단서 빌더가 `if cfg["hazard_*"]` 안에 있는 것은 **0개**. 조립부 hazard 분기는 2줄뿐이다.
2. **연석 상면 = 승강장 레벨 = 반사실 채움면 = 0.000.** 그래서 연석 위/배면에 서는
   모든 단서 프림(방호울타리·볼라드·시선유도 대상)이 **팔 불변**이다 — hazard OFF 팔에서
   연석이 사라져도 그 자리의 지면 z 가 그대로 0.000 이기 때문이다.
   유일한 예외는 **차도 노면표시**이며, 그것은 노면을 따라 내려간다(`_road_z()`).
   hazard OFF 팔의 그 상태는 **고원식(플랫폼형) 정류장** — 실재하는 공법이므로
   반사실 팔도 그럴듯하다(계획 §2.4 "위험 변형도 독립적으로 그럴듯해야 한다"의 역방향).
3. 카메라 데이텀 스트립 `x ∈ [−12.05, −1.15] · |y| ≤ 0.95` 안에서 상면을 움직이는 토글
   프림은 줄눈(recess 3 mm)·맨홀(7.7 mm)·빗물받이(flush)뿐 — 전부 `datum_tol`(≤ 0.02 m).
   점형블록·쉘터·울타리·가로수는 전부 스트립 **밖**이다.
4. **void 커버리지 1.0** — 차도·연석·연석배면·점형블록·승강장·보도·시설물대·전면공지가
   x ∈ [−2, 14] × y ∈ [−8, 8] 을 빈틈없이 덮는다. 개방 바닥 0.
5. **수관·지붕이 높이맵을 **올릴** 수는 있어도 내릴 수는 없다.** 높이맵은 수직 레이의
   최초 히트이므로 수관·쉘터 지붕이 덮은 셀은 z 가 그 상면이 된다. sceneL1 에서는 그것이
   **낙차 발자국을 지우는** 사고였지만(수관이 개거 위를 덮으면 발자국 소실), 이 씬에는
   지울 발자국이 없고 **상방 이동은 최저점 회계를 오염시키지 않는다** — 위 표는
   `z_max` 의 **최소값**을 재기 때문이다. 그래서 가로수 수관이 보도 유효폭 위로 뻗는
   것을 허용한다(그것이 `cue_shadow_caster` 가 만들려는 **그림자 밴드** 그 자체이고,
   실제 가로수는 보도 위로 뻗는다). 규율은 **줄기 위치**에만 건다 — 가로수는 전부
   시설물대(y ∈ [1.70, 4.10]) 안, 쉘터는 전부 승강장(y ∈ [−3.12, −1.70]) 안.

표준법: 법1 온전 상태만(파손·처짐·결실 표현 0) · 법2 법정 제식 표지만 · 법4 기능 필수성
(방호울타리 = 무단횡단 금지 · 볼라드 = 차량 진입 억제 · 점형블록 = 교통약자법 의무) ·
법5 차량·계절소품 0 · 법6 신규 재질 역할 0 · 법7 `cue_*` 최대 융기 12 mm · 법8 근거 태그.

**법2 특기**: 정류장 표지는 「도로교통법 시행규칙」 별표6 계열의 법정 제식 안내판 1매만
쓰고 임의 경고 문구("추락주의" 등)를 **한 글자도 넣지 않는다**. 임의 경고판을 넣으면
그것이 곧 낙차 단서가 되어 이 씬의 실험 목적을 스스로 파괴한다.

실행
    unset PYTHONPATH VIRTUAL_ENV; conda activate env_isaaclab; export PYTHONNOUSERSITE=1
    python scenes/main/sceneN9_busstop_tactile.py                 # GUI 룩체크
    NEGOBS_SMOKE=1 python scenes/main/sceneN9_busstop_tactile.py  # CPU 조립 스모크
데이터 렌더 진입점 (신설 씬은 AZ 원장 등재 전까지 이 경로가 유일 — CUE_COVERAGE §4-4 (6)):
    python experiments/v3_0823/code/h67_probe.py --scene sceneN9 --run <stamp> ...
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk


# [계획 §2.0] 생활권 = 보도. 계절은 **초여름** — 같은 생활권의 sceneH3(늦봄)·
#   sceneN11(초가을)과 톤을 분리한다(§3.2 "부지·드레싱을 겹치지 않게").
SEASON = "early_summer"


# ===========================================================================
# [A0] CUE_CLASS — 렌더 **전** 사전 분류 (RENDER_PLAN_V3 §2.6 / ACCOUNTING §2-6)
#
#   이 씬에는 **구조물(토글 금지) 낙차 부재가 없다** — 낙차 자체가 없기 때문이다.
#   `_structural` 에는 그 대신 **팔 불변이어야 하는 지형 프림**을 싣는다.
# ===========================================================================
CUE_CLASS = {
    "cue_railing":         "decorative",   # 보행자 방호울타리(L4) — 무단횡단 금지용
    # [D82 ⓐ 근거 조항] 「교통약자의 이동편의증진법 시행규칙」 **별표1** —
    #   **점형 = 경고**(승차 위치 1밴드 0.60 m · 위험 지점 0.30 m 이격) /
    #   **선형 = 유도**(보도 → 승차 위치 1줄, 돌출선 = 보행 방향). ADA §705.2·§810.
    #
    # ── [문서 정정 · 2026-08-24 · REG_AUDIT 전달 3건 반영] ──────────────────────
    #  (1) **별표 번호 오표기 정정** (REG_AUDIT §2.7 N9/N11-C · §3 C-5).
    #      구 표기는 점자블록 근거를 「교통약자법 시행규칙」 **별표2** 로 적었다.
    #      2026-01-30 공포판 대조 결과: **별표1** = 「이동편의시설의 구조·재질 등에 관한
    #      세부기준」(= **점자블록 정본**) · **별표2** = 「보행안전시설물의 구조 시설기준」
    #      (= 볼라드). ⇒ 이 씬의 점자블록 근거는 전부 **별표1** 이고, 버스정류장은
    #      동 별표1 **버목 3)** (*보도폭이 넓으면 점형 + 선형, 좁으면 점형만*)이다.
    #      ※ 볼라드 계열은 근거가 또 다르다 — 구 별표2 제7호는 **삭제·이관**되어 현행은
    #        「보행안전 및 편의증진에 관한 법률 시행규칙」 **별표1 제10호**(수치 동일)다.
    #        이 씬의 볼라드 전면에는 점형블록이 없다(동 10호 **바** 미달 — 전국 실측
    #        볼라드 부적정 96.0 % 의 최빈 유형이라 **의도적 미수정**, REG_AUDIT §4 (1)).
    #      기하는 한 글자도 바뀌지 않는다 — **인용 문자열만**의 정정이다.
    #
    #  (2) **선형블록 세로폭 0.30 m 판독 기록** (REG_AUDIT §2.7 N9-3 "판정 보류(경미)").
    #      조항이 양방향으로 읽힌다(CUE_REGULATION_BASIS §2.4):
    #        · *"횡단보도·교통섬·지하도·육교·건물입구·**정류장** = **60 cm**"*
    #        · *"**연속적인 직선 보행을 유도**할 때는 **30 cm 로 할 수 있음**"* `[권장]`
    #      이 씬의 유도로는 보도 유효폭 → 승차 위치를 잇는 **직선 1구간 1.42 m** 이고
    #      분기·굴절·교차가 없다 ⇒ **30 cm 판독을 채택**한다. 위반이 아니라 **판독 선택**
    #      이므로 기하는 그대로 두고 근거만 남긴다(감사: 재렌더 불요).
    #      한편 **점형** 밴드 폭은 이 유예가 없다 — 지침 6.6.7 가의 *"마주치는 방향 60 cm"*
    #      가 표준이고 이 씬은 0.60 m 로 그 표준을 따른다.
    #
    #  (3) **N9(0.60) ↔ N11(0.30) 점형 세로폭 불일치 기록** (REG_AUDIT §2.7 N11-1).
    #      `sceneN11_ground_pattern` 은 **같은 "정면 접근"** 케이스에서 0.30 m(1유닛)를
    #      쓴다. 30~90 cm 범위 안이라 **위반은 아니지만 표준(60 cm) 미달**이고, 두 씬이
    #      코퍼스 안에서 갈린다. **N9 는 표준값 0.60 을 유지**한다.
    #      통일하려면 N11 밴드의 **기하**를 바꿔야 하므로(= 밴드 세로폭 변경) 이 문서
    #      정정의 범위 밖이다 ⇒ **기록만 하고 처분은 열어 둔다**(사용자 판단 항목).
    "cue_tactile":         "decorative",   # **승차 위치 점형 1밴드(L6)** + 선형 유도로 1줄
    "cue_nosing":          "decorative",   # 기본 OFF — 평탄 승강장에 계단코 없음(법4)
    "cue_material_break":  "decorative",   # **재질 재바인딩 전용** — 프림 집합 불변
    "cue_sign":            "decorative",   # 버스정류장 안내 표지 1매 (법정 제식)
    "cue_scene_dressing":  "decorative",   # 승차대 쉘터·벤치·노선안내판·관목·원경 상가
    "cue_shadow_caster":   "decorative",   # 가로수 + 가로등주 — 그림자 밴드
    "cue_manhole":         "decorative",   # 보도 맨홀 (flush)
    "cue_tree_grate":      "decorative",   # 수목보호격자 (flush)
    "cue_slab_joint":      "decorative",   # 보도 시공줄눈 (recess 3 mm)
    "cue_drainage":        "decorative",   # 빗물받이 (flush)
    "cue_bollard":         "decorative",   # 보도 진입 차량 억제 볼라드
    "cue_road_marking":    "decorative",   # 정차대 표시 + 차선 (FA_REALITY §2 6위 키 승격)
    # ── 토글 금지 목록 (팔 불변 지형). 어떤 cue_* 도 이 프림들을 참조하지 않는다 ──
    "_structural":         ["Ground/Walk", "Ground/Platform", "Ground/Setback",
                            "Ground/Furnish", "Ground/Frontage"],
}


# ===========================================================================
# [A] SCENE_CONFIG — **표준 장비 16키** (RENDER_PLAN_V3 §2.0 · CUE_COVERAGE §4-4 (1))
# ===========================================================================
SCENE_CONFIG = {
    # ── ② "위험" 축: 유일한 기하 토글. **낙차가 아니라 함정을 짓는다**(계획 §1.0) ──
    #   True  → 차도면이 −0.200 으로 내려가고 화강석 연석이 선다 (실측 정류장 상태)
    #   False → 차도면이 승강장과 같은 0.000 으로 올라온다 (고원식 정류장 = 반사실 팔)
    #   어느 쪽도 0.30 m 임계를 넘지 않으므로 **두 팔 다 GT 올-음성**이다.
    "hazard_platform_edge": True,
    # ── ③ 단서: 공통 6키 ────────────────────────────────────────────────────
    "cue_railing":         True,   # L4 보행자 방호울타리 — 목적은 횡단 금지(추락 방지 아님)
    "cue_tactile":         True,   # **L6 승강장 경계 점형블록** — 이 씬의 주 단서
    # 평탄 승강장에는 계단이 없다 ⇒ 나이징은 대상 기하가 없다. 법4 "비움이 기본값"에 따라
    #   기본 OFF 로 두되 코드 경로는 상시 보유한다(sceneN1·N5 선례 "Key reserved only").
    "cue_nosing":          False,
    "cue_material_break":  True,   # 승강장 = 화강석 판석 / 보도 = 인터로킹 블록
    "cue_sign":            True,   # 버스정류장 안내 표지 (법2 — 법정 제식만)
    "cue_scene_dressing":  True,   # **승차대 쉘터·벤치·노선안내판** = 정류장 정체성
    # ── v3 신설 3키 (FA_REALITY §2) ─────────────────────────────────────────
    "cue_shadow_caster":   True,   # 갭 4위 — 양성·음성 씬 동일 비율(§2.0 역지름길 경보)
    "cue_manhole":         True,   # 갭 1위 (25.0)
    "cue_tree_grate":      True,   # 갭 2위 (20.0)
    # ── FA_REALITY §2 승격 후보 4키 ────────────────────────────────────────
    "cue_slab_joint":      True,   # 갭 5위 — 보도 시공줄눈
    "cue_drainage":        True,   # 갭 3위 — 빗물받이
    "cue_bollard":         True,   # L2 — 보도 진입 차량 억제 볼라드
    "cue_road_marking":    True,   # **갭 6위 키 승격** — 정차대 표시 + 차선 (신규 기하 0)
    # ── 팔 제어 2키 ─────────────────────────────────────────────────────────
    "keep_dressing":       False,
    "placebo_remove":      False,
}


# ===========================================================================
# [B] PARAMS — 전 수치. 횡단면은 파일 상단 표와 **한 글자도 어긋나지 않는다**
# ===========================================================================
PARAMS = dict(
    terrain=dict(
        y_far=40.0, base_z=-1.60, walk_z=0.0,
        x0=-34.0, x1=44.0,
        # 보도 유효폭 3.40 m [규격 「도로의 구조·시설 기준에 관한 규칙」 §16 보도 유효폭
        #   최소 2.0 m · 간선도로 권장 3.0 m 이상]
        walk=dict(y_half=1.70),
        # 승강장 대기공간 — 보도와 같은 레벨. 쉘터·벤치가 서는 자리
        platform=dict(y0=-3.12, y1=-1.70),
        # 점형블록 띠 — 세로 0.60 m [규격 교통약자법 시행규칙 **별표1** · ADA §705 610 mm]
        tactile_band=dict(y0=-3.72, y1=-3.12),
        # 연석 배면 여유 0.30 m — 방호울타리·볼라드 자리 (점형블록 침범 금지: S37 오설치 민원)
        setback=dict(y0=-4.02, y1=-3.72),
        # 연석 화강석 B형 폭 0.18 m [규격 KS F 4006 도로경계석 B형 180×200]
        curb=dict(y0=-4.20, y1=-4.02, w=0.18),
        # 건물측 시설물대 1.80 m — 가로수·가로등·수목보호격자
        furnish=dict(y0=1.70, y1=4.10),
        frontage=dict(y0=4.10, y1=8.80),
    ),
    # ── ② "위험" 축 (hazard_platform_edge 전속) — 승강장 경계 단차 ───────────
    hazard=dict(
        y_curb=-4.20,             # 연석 차도측 면 = 표고차 선
        road_z=-0.200,            # **핵심 수치**: 차도면. |0.200| < 0.300 임계
        fill_z=0.0,               # hazard=False 반사실 노면(고원식 정류장)
        # [computed] 표고차 = 0.000 − (−0.200) = **0.200 m** · 임계 여유 0.100 m
        # [규격] 보도 연석 표준 높이 0.15~0.25 m · FA_REALITY §3 L6 실측 밴드와 동일
    ),
    # ── ③ 단서 파라미터 ─────────────────────────────────────────────────────
    # ── **[개정 R3 · D82 설치-규정 감사]** ────────────────────────────────────
    #   D82 ⓐ: *"단서 설치 = 실제 설치 기준 준거 원칙(**점형 = 경고 / 선형 = 유도**
    #   역할 구분, **위험 경계 전 점형 1밴드**, 근거 조항 씬 사양 명기)"* ·
    #   ⓒ **cue-extent 감사**(N-cue 밀도 대칭) · ⓓ 신규 씬 전수 설치-규정 감사.
    #
    #   R2 까지의 배치는 **두 가지를 위반**했다:
    #     ① 점형블록을 **승차 구간 전 길이 12.40 m** 로 깔았다 — 그것은 **철도 승강장**의
    #        제식이고, 한국 버스정류장의 법정 제식은 **승차 위치**에 점형블록 1밴드다
    #        (「교통약자의 이동편의증진법 시행규칙」 **별표1 버목 3)**). 실물보다 큰 소품이 되면
    #        D82 ⓒ 가 말한 *"오버사이즈 프롭"* 이 되어 함정의 그럴듯함이 깨진다.
    #     ② 유도로를 `sc.build_tactile`(**점형** 도트형)로 2줄 깔았다 — 유도는
    #        **선형블록**의 역할이고 점형으로 유도로를 까는 것은 S37 이 집계한
    #        **오설치** 유형 그 자체다(재시공 요구 325건).
    #
    #   수정 후 면적: 점형 1.08 m² + 선형 0.43 m² = **1.51 m²**.
    #   기존 위험 씬 실측(점형 면적): H3 1.08 · H7 1.28 · L1 4.08 · H1 8.72 · H2 7.20 m².
    #   ⇒ **N-cue 밀도가 위험 씬 밴드의 하단**에 들어간다(D82 ⓒ 밀도 대칭).
    tactile=dict(
        # (a) **점형블록(경고) 1밴드** — 승차 위치.
        #   [규격 「교통약자의 이동편의증진법 시행규칙」 **별표1 버목 3)** — 버스 승강장의 **승차
        #    위치**에 점형블록을 설치한다. 깊이 **0.60 m**(0.30 m 유닛 2매) ·
        #    위험 지점에서 **0.30 m 이격**. ADA §705.2 / PROWAG R305 의 610 mm 와 같은 밴드]
        #   연석 배면선 y = −4.02 에서 0.30 m 물러난 y = −3.72 에서 시작한다.
        warn=(2.70, -3.72, 4.50, -3.12),        # 1.80 × 0.60 m — 승차 위치 폭 6유닛
        # (b) **선형블록(유도) 1줄** — 보도 유효폭 → 승차 위치.
        #   [규격 동 **별표1** — 선형블록은 **유도** 목적이며 돌출선(4줄/유닛)은 **보행
        #    방향과 나란하다**. 점형블록으로 유도로를 까는 것은 오설치(S37)]
        #   세로폭 0.30 m 는 *"연속적인 직선 보행 유도 시 30 cm 로 할 수 있음"* 판독이다
        #   (정류장 일반값은 60 cm — CUE_CLASS 주석 (2) 의 양방향 판독 기록 참조).
        guide=(3.45, -3.12, 3.75, -1.70),       # 0.30 × 1.42 m (유도 폭 1유닛)
        proud=0.004,               # [계획 §2.0] 점형블록 융기 4 mm
        guide_proud=0.005,         # [규격] 선형블록 돌출 0.5 cm 대
        guide_bar_w=0.017, guide_bar_pitch=0.075,   # 유닛(0.30 m)당 4줄
    ),
    # 보행자 방호울타리 — **정류장 구간은 개방**(승하차 동선). 법4 기능 필수성.
    #   [규격 — **정정 2026-08-24 · REG_AUDIT §2.7 N9-4**] 구 표기 *"「도로안전시설 설치
    #    및 관리지침 — 보행자용 방호울타리편」 h **1.00~1.20 m**"* 는 **미확인 수치**였다.
    #    확인된 값은 두 갈래이고, 이 울타리에 맞는 쪽은 **아래**다:
    #      · 지침 2.4.1 나 — 보행자용 방호울타리 **110 cm 표준**(= 추락·차량 방호 계열)
    #      · 「보행안전 및 편의증진에 관한 법률 시행규칙」 **별표1 제3호 나** —
    #        **무단횡단 금지시설 90 cm 표준**
    #    이 씬의 울타리는 CUE_CLASS 가 명시하듯 목적이 **무단횡단 금지**(추락 방지가
    #    아니다 — 낙차 0.20 m 는 임계 미만이고 이 씬은 N-cue 함정이다)이므로
    #    **90 cm 계열**이 근거이고, as-built 1.00 m 는 그 위 = **규정 정합**이다.
    #    지주 간격 1.80 m 는 지침의 1.5~2.0 m 범위 안. **기하 변경 없음 — 인용만 정정.**
    #   **[개정 R1]** 동측 구간 시점 10.40 → **18.00** — 볼라드 열(x 10.8…16.8)과
    #   같은 y 를 쓰므로 x 로 분리한다. 실제 가로도 정류장 뒤에는 볼라드, 그 너머부터
    #   울타리가 이어지는 순서로 시공된다.
    fence=dict(y=-3.87, post_r=0.030, post_h=1.05, post_pitch=1.80,
               rail_r=0.020, top_z=1.00, mid_z=0.55,
               spans=[(-16.00, -2.20), (18.00, 34.00)]),
    # 승차대(쉘터) — [규격 「여객자동차 운수사업법 시행규칙」 버스정류장 승차대
    #   표준: 길이 4.0 m · 폭 1.5 m · 유효높이 2.30 m 이상]
    shelter=dict(x0=1.60, x1=5.60, y0=-3.06, y1=-1.76,
                 roof_z=2.60, roof_t=0.10, post_r=0.055,
                 back_t=0.06, bench=(3.60, -2.86, 0.0)),
    # 노선안내판 (쉘터 측면 게시) — 임의 문구 없음. 색면 패널 + 프레임만.
    routeboard=dict(x=5.52, y=-2.41, w=0.06, h=1.10, l=1.10, z=1.55),
    # 버스정류장 표지주 — 법정 제식 안내판 1매
    #   **[개정 R1]** (−1.20, −3.30) → **(0.60, −2.95)** · yaw 0 → **180**.
    #   R0 실측에서 표지가 **16프레임 중 4프레임**에만 잡혔다(카메라 뒤쪽 x = −1.20).
    #   또 y = −3.30 은 점형블록 띠(−3.72…−3.12) **안**이었다 — 표지주를 경고블록 위에
    #   세우는 것은 S37 이 집계한 오설치 민원 유형(침범 603건) 그 자체다.
    #   새 자리는 승강장(−3.12…−1.70) 안이고 카메라 전방이며, yaw 180 은 판면이
    #   **접근 보행자를 향하게** 한다(정류장 표지의 실제 설치 방향).
    sign=dict(x=0.60, y=-2.95, yaw=180.0, pole_h=2.60, w=0.52, h=0.52),
    # [규격 행정안전부 볼라드 설치기준: h 0.80~1.00 · φ0.10~0.20 · 간격 ~1.5 m · 반사띠]
    #   **[개정 R1]** 서측 진입부(x −16.5…−10.5) → **정류장 동측 보차도 경계**(x 10.8…17.3).
    #   사유는 R0 프로브 실측이다 `[260823_v3p5_n911probe_A · sceneN9 · 16프레임]`:
    #   서측 배치는 카메라(x = −d, d ≤ 12)의 **뒤쪽**이라 `cue_bollard` 픽셀이
    #   **16프레임 전부 0** 이었다 — 켜져 있으나 화면에 없는 단서는 §12-5 의 k 판정에서
    #   OFF 와 구별되지 않으므로 그 키는 사문(死文)이 된다. 동측 배치는 전 밴드에서
    #   화각 안이다(d = 2 → 방위각 16.8° · d = 12 → 9.6°, hFOV/2 = 31.1°).
    #   기능도 그대로다 — 보차도 경계선 위 차량 진입 억제이고, 정류장 승하차 구간
    #   (x −2.0…10.4)을 **비켜서** 선다.
    bollard=dict(y=-3.87, xs=(10.80, 12.30, 13.80, 15.30, 16.80),
                 r=0.075, h=0.90, band_z=0.68, band_t=0.09),
    # 정차대 노면표시 — [규격 「도로교통법 시행규칙」 별표6 노면표시. 황색 실선 정차금지
    #   지대 + 백색 차선]. **면적 최소화**(v5.1 §4 순백 대면적 금지) · 두께 3 mm.
    marking=dict(
        bay=(-2.40, -5.60, 10.80, -4.40),   # 정차대(버스전용 정차 구간) 테두리
        bay_w=0.15,
        lane=(-24.0, -8.80, 40.0, -8.65),   # 차선 1줄 (격자 |y| ≤ 8 **밖**)
        z_off=0.003,
    ),
    gkit=dict(
        # (a) 보도 본선 — 시공줄눈 + 맨홀 2 + 빗물받이 2 (**격자 안** · 전부 flush)
        walk_region=(-7.60, -1.66, 13.90, 1.66),
        walk_manholes=[(2.80, 0.90), (9.60, -1.10)],
        walk_gullies=[(0.60, -1.55), (11.40, 1.52)],
        # (b) 승강장 — 판석 줄눈만 (맨홀·빗물받이 없음)
        plat_region=(-1.90, -3.08, 12.00, -1.74),
        # (c) 수목보호격자 — 시설물대. 가로수와 같은 좌표(격자 안에 뿌리분 개구 없음)
        tree_grates=[(2.60, 3.00), (9.60, 3.00), (16.60, 3.00)],
    ),
    shadow=dict(
        # [FA_REALITY §2 4위] 그림자 밴드 캐스터. **양성 씬에도 동일 비율**(§2.0 경보).
        #   가로수는 전부 **시설물대**(|y| ≥ 1.70). 보도 유효폭 위에 수관 0
        #   (격자 안 최저점 회계 오염 방지 — 파일 상단 프림 위생 5).
        trees=[(2.60, 3.00), (9.60, 3.00), (16.60, 3.00)],
        tree_h=6.4,
        lamps=[(0.20, 3.72), (13.00, 3.72)],
        lamp_h=4.6, lamp_arm=1.05,
    ),
    dress=dict(
        # 상가 저층부 — 원경. 전부 |y| ≥ 8.80 이라 높이맵 격자 밖.
        # **[개정 R4 · D82 ⓒ 밀도 대칭]** 높이 7.2/8.4/9.0 → **4.8/5.4/6.0**.
        #   R3 확정 라운드의 cue-extent 감사 실측: 이 씬의 단서 화면비율 p50 **0.290**
        #   으로 위험 씬 밴드(H2 0.035 · H3 0.047 · L1 0.153 · H1 0.214)의 **상단을
        #   넘었고**, 클래스 분해에서 그 **75 %(453k/601k px)가 `dressing`**, 그중
        #   대부분이 원경 상가 매스였다. 즉 초과분의 원인은 **규정 시설물이 아니라
        #   배경 물량**이다. D82 ⓒ 가 막으려는 상태(단서 밀도가 라벨을 예측)는 원인이
        #   무엇이든 성립하므로 배경을 줄인다.
        #   **줄이는 방법은 "치우기"가 아니라 "층수 현실화"다** — D82 부가 지침
        #   *"규정 미적용 시점의 현실 환경 상실 금지"*. 보도에 면한 근린상가는 2~3층
        #   (4.8~6.0 m)이 표준이고, 7~9 m 는 오히려 과장이었다. 건물은 그대로 보도에
        #   면해 있고 수평선 폐합도 유지된다.
        shops=[("S0", -14.0, 6.0, 8.80, 15.0, 4.8),
               ("S1", 9.0, 30.0, 8.80, 16.0, 5.4)],
        # 도로 건너편 원경 — |y| ≤ −12 (격자 밖)
        across=[("A0", -6.0, 26.0, -22.0, -13.0, 6.0)],
        # 시설물대 관목 띠 (가로수 하부) — 격자 안이지만 |y| ∈ [2.95, 3.45] 로
        #   보도 유효폭·승강장 어디도 덮지 않는다.
        hedge=[(-4.0, 3.55, 14.0, 4.05)],
        shrub_h=0.55,
        benches=[(-5.20, -2.40, 270.0)],    # 승강장 서측 추가 벤치 1 (차도 향)
    ),

    # ── 재질 3단 (realism_v1_final §84) ─────────────────────────────────────
    material=dict(
        scale=dict(paving_interlock=1.20, granite_dark=1.70, concrete_floor=1.60,
                   asphalt=2.60, grass=1.4, tactile=0.3, stone_flag=1.5),
        # **[개정 R1]** (0.615,0.605,0.585) → (0.575,0.572,0.565). 텍스처 평균
        #   (0.553,0.554,0.550) × 구 tint = 유효 알베도 0.334 로 `paving` 클래스 상한
        #   0.34 에 붙어 있었다(L5 에서 과노출 위험). 새 값은 0.317 로 여유를 만든다.
        tactile_lin_color=(0.620, 0.520, 0.075),   # 선형블록 안전 황색 (캡 0.55 이하)
        walk_tint=(0.575, 0.572, 0.565),     # 보도 인터로킹 블록 (회색)
        walk_alt_tint=(0.585, 0.585, 0.578),  # cue_material_break OFF 대체 재질
        plat_tint=(0.560, 0.552, 0.540),     # 승강장 화강석 판석
        # **[개정 R1]** 냉색 보정 — `stone_flag` 텍스처 평균 (0.480,0.478,0.448)은
        #   난색이라 구 tint 로는 (0.281,0.276,0.253) = R/B 1.11 의 누런 판석이 됐다.
        #   OmniPBR 의 `diffuse_tint` 는 텍스처와 **곱**이므로(scene_common:1653) tint 를
        #   역수 비례로 잡아 (0.278,0.279,0.279) = 중성으로 되돌린다.
        front_tint=(0.580, 0.583, 0.622),    # 상가 전면 공지 판석 (중성 보정)
        furnish_tint=(0.545, 0.540, 0.528),  # 시설물대 판석
        curb_tint=(0.635, 0.628, 0.612),     # 화강석 연석
        road_color=(0.118, 0.118, 0.121),    # 아스팔트 (alb 0.12 — asphalt 클래스 밴드)
        road_rough=0.80,
        grass_tint=(0.40, 0.50, 0.25),
        # [look 층] 프림 이름이 클래스를 정한다. 울타리는 실제로 아연도 강관이다.
        fence_color=(0.545, 0.560, 0.575), fence_metal=0.72, fence_rough=0.42,
        #   **[개정 R2]** 도장 강관으로 낮춘다 — R1 룩체크에서 쉘터 기둥·마구리가
        #   프레임에서 가장 밝은 수직 대면적이었다(v5.1 §4 순백 대면적 취지).
        shelter_color=(0.300, 0.310, 0.322), shelter_metal=0.35, shelter_rough=0.48,
        roof_color=(0.295, 0.300, 0.305), roof_rough=0.55,
        glass_color=(0.44, 0.50, 0.52),
        board_color=(0.155, 0.230, 0.360),   # 노선안내판 바탕 (도시형 청색)
        nosing_color=(0.41, 0.39, 0.35), nosing_rough=0.70,
        band_color=(0.80, 0.52, 0.05),       # 볼라드 반사띠 (면적 小)
        bollard_color=(0.60, 0.61, 0.62), bollard_metallic=0.55, bollard_rough=0.38,
        pole_color=(0.235, 0.240, 0.255), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.76, 0.76, 0.74), lamp_rough=0.4,
        wood_color=(0.315, 0.215, 0.135), wood_rough=0.85,
        # **[개정 R1]** metallic 0.55 → **0.15** · rough 0.62 → **0.82**.
        #   R0/스모크 육안: 맨홀 뚜껑이 **밝은 회색 원반**으로 렌더됐다. 원인은 알베도가
        #   아니라(0.145 는 이미 어둡다) metallic 0.55 × rough 0.62 가 정오 천공을
        #   경면 반사한 것이다. FA_REALITY §1.3 C1 의 전제는 *"평탄면 위의 **어두운
        #   원반**"* 이므로 밝게 읽히면 이 단서는 FA 재료가 되지 못한다. 실제 주철
        #   뚜껑은 산화 피막으로 거의 비금속으로 보인다 — 물리적으로도 이 값이 맞다.
        #   **[개정 R2]** 알베도 0.145 → **0.072**. R1(metallic 0.55→0.15)만으로는
        #   부족했다 — `rev` 라운드 실측 `[260823_v3p5_n911rev_A · sceneN11 · 프림별
        #   휘도]`: 맨홀 뚜껑 **148.9** vs 포장 **123.7** 로 여전히 **더 밝았다**.
        #   원인은 알베도가 아니라 **grazing 처리의 비대칭**이다 — 포장은 `mdl="ground"`
        #   클래스(concrete/paving)라 `LOOK_CLASS[...]["grazing"]=0.30` 으로 스침각에서
        #   어두워지는데, 주철은 `mdl="omni"` 라 그 처리가 없어 램버시안 값을 유지한다.
        #   보행 눈높이(h 0.25–1.9)는 거의 전부 스침각이므로 실제 프레임에서는 두 값이
        #   역전된다. 실측 주철 알베도는 0.05–0.12 이므로 0.072 는 물리적으로도 옳다.
        iron_color=(0.072, 0.072, 0.078), iron_metallic=0.15, iron_rough=0.82,
        # 노면표시 — **순백 금지**(v5.1 §4). 실제 도색은 마모·오염으로 0.62~0.72.
        mark_white=(0.700, 0.700, 0.688), mark_yellow=(0.700, 0.545, 0.105),
        mark_rough=0.68,
        canopy_a=(0.031, 0.052, 0.019), canopy_b=(0.042, 0.066, 0.026),
        canopy_rough=1.0,
        shrub_tint=(0.40, 0.47, 0.24),
        backdrop_color=(0.240, 0.238, 0.232), backdrop_rough=0.74,
    ),

    # ── 조명 (L0–L7 카탈로그. 생산 3종 = L0·L5·L7) ─────────────────────────
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-96.0,
        noon_sun_enable=True, noon_sun_elev=54.2,
        noon_sun_intensity=2400.0, noon_sun_color=(1.0, 0.972, 0.940),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # 시설물대 가로수·가로등의 그림자가 **보행축을 가로질러** 보도에 떨어지도록.
    SUN_AZ_OFFSET=14.0,

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [B'] 팔 제어 2키 — 모듈 스코프에서 **한 번** 확정 (sceneC2:496-520 패턴)
# ===========================================================================
KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))
PLACEBO_REMOVE = bool(SCENE_CONFIG.get("placebo_remove", False))
if KEEP_DRESSING:
    if SCENE_CONFIG.get("hazard_platform_edge", True):
        raise SystemExit(
            "[FATAL sceneN9] keep_dressing=True 는 hazard_platform_edge=False 를 "
            "요구한다 — 이 팔은 반사실(고원식 정류장) 위에 단서를 보존하는 C팔이다.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL sceneN9] keep_dressing=True 와 cue_scene_dressing=False 는 "
            "모순이다 — 쉘터·벤치·노선안내판이 바로 이 팔이 보존하려는 대상이다.")
if PLACEBO_REMOVE:
    if not SCENE_CONFIG.get("hazard_platform_edge", True):
        raise SystemExit(
            "[FATAL sceneN9] placebo_remove=True 는 hazard_platform_edge=True 를 "
            "요구한다 — 플라시보 팔은 ON 상태의 외형 대조군(D35)이다.")
    if KEEP_DRESSING:
        raise SystemExit(
            "[FATAL sceneN9] placebo_remove 와 keep_dressing 은 서로 다른 팔(P·C)이며 "
            "동시에 설정될 수 없다.")
_ARM = ("C_hz0_cue1" if KEEP_DRESSING else
        "P_hz1_placebo" if PLACEBO_REMOVE else
        "hz%d_fen%d_tac%d_mat%d_dress%d" % (
            int(SCENE_CONFIG["hazard_platform_edge"]), int(SCENE_CONFIG["cue_railing"]),
            int(SCENE_CONFIG["cue_tactile"]), int(SCENE_CONFIG["cue_material_break"]),
            int(SCENE_CONFIG["cue_scene_dressing"])))
print(f"[sceneN9] arm={_ARM} keep_dressing={KEEP_DRESSING} "
      f"placebo_remove={PLACEBO_REMOVE}")


# ===========================================================================
# [C] 경로 상수 · 필요 텍스처 역할 · 데이텀 선언
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN9")

ASSET_ROLES = ["paving_interlock", "granite_dark", "concrete_floor", "asphalt",
               "stone_flag", "grass", "tactile", "sign_info", "hdri", "mdl"]

# 카메라 데이텀 스트립 — 밴드는 base(d ∈ LogU[1.2,12]) 뿐이므로 x = −d ∈ [−12.00, −1.20]
#   에 각 방향 0.05 m 여유.
DATUM_STRIP = dict(x0=-12.05, x1=-1.15, y0=-0.95, y1=0.95)
DATUM_TOL = 0.02

GATED_ZONES = [
    # (tag, key, x0, x1, y0, y1, dz)  — dz = 지면 위 최대 융기
    # 차도·연석·반사실 노면 — 전부 |y| ≤ −4.02 이므로 데이텀 스트립(|y| ≤ 0.95) 밖
    ("Road",         "hazard_platform_edge",       -34.00, 44.00, -40.00, -4.20, 0.00),
    ("Curb",         "hazard_platform_edge",       -34.00, 44.00,  -4.20, -4.02, 0.00),
    ("RoadFlush",    "hazard_platform_edge(off)",  -34.00, 44.00, -40.00, -4.02, 0.00),
    # 점형블록 — 승강장 경계. proud 4 mm. 스트립 밖.
    ("Tactile-Warn", "cue_tactile",                  2.70,  4.50,  -3.72, -3.12, 0.004),
    ("Tactile-Guide", "cue_tactile",                 3.45,  3.75,  -3.12, -1.70, 0.005),
    ("Fence-W",      "cue_railing",                -16.00, -2.20,  -3.91, -3.83, 1.06),
    ("Fence-E",      "cue_railing",                 18.00, 34.00,  -3.91, -3.83, 1.06),
    ("Nosing",       "cue_nosing",                  -0.10,  0.10,  -1.70,  1.70, 0.012),
    ("Sign",         "cue_sign",                     0.20,  1.00,  -3.25, -2.65, 2.62),
    ("Bollard",      "cue_bollard",                 10.72, 16.88,  -3.95, -3.79, 0.90),
    # ground_kit: 줄눈 recess 3 mm(융기 0) · 맨홀 7.7 mm · 빗물받이 flush.
    #   `surface=None` 로 잡초(proud 최대 0.107 m)를 **끈다** — 법1과 VG-datum 이 같은
    #   방향을 가리킨다.
    ("GKitWalk",     "cue_manhole/slab_joint/drainage",
                                                    -7.64, 13.94,  -1.70,  1.70, 0.008),
    ("GKitPlat",     "cue_slab_joint",              -1.94, 12.04,  -3.12, -1.70, 0.008),
    ("TreeGrate",    "cue_tree_grate",               1.88, 17.32,   2.28,  3.72, 0.004),
    # 가로수·가로등 **줄기**는 시설물대(y ∈ [1.70, 4.10]) — 스트립(|y| ≤ 0.95) 밖.
    #   수관은 보도 위로 뻗을 수 있으나 높이맵을 **올릴 뿐** 내리지 못하므로 최저점
    #   회계에 무해하다(프림 위생 5). 등기구 암은 보행축 쪽으로 1.05 m 뻗어 최근접
    #   |y| = 2.67 이고 스트립을 침범하지 않는다.
    # **수관 AABB 는 카메라 데이텀 스트립(x ∈ [−12.05, −1.15] · |y| ≤ 0.95)에 닿으면
    #   안 된다** — `AabbPrefilter.ground_z` 는 (x,y) 상공 60 m 에서 내리쏘는 레이의
    #   **최초 히트**이고 식생을 제외하지 않는다(`variation_kit.py:781-785`). 수관이
    #   스트립을 덮으면 그 컷의 `cam.ground_z` 가 수관 top 이 되어 카메라가 6 m 위로
    #   올라가고, `cue_shadow_caster` OFF 팔에서는 지면으로 돌아오므로 **팔마다 다른
    #   포즈**가 된다 = VG-datum·VG-10 동시 파괴. 그래서 가로수 x 를 스트립 동단
    #   밖으로 민다(보수적 수관 반경 3.2 m · 여유 0.55 m).
    ("Shadow-Tree",  "cue_shadow_caster",           -0.60, 19.80,  -0.20,  6.20, 6.60),
    ("Shadow-Lamp",  "cue_shadow_caster",           -0.10, 13.30,   2.60,  3.82, 4.80),
    # 노면표시 — 정차대 테두리는 차도(|y| ≤ −4.40) · 차선은 격자 밖
    ("Marking-Bay",  "cue_road_marking",            -2.40, 10.80,  -5.60, -4.40, 0.003),
    ("Marking-Lane", "cue_road_marking",           -24.00, 40.00,  -8.80, -8.65, 0.003),
    # 쉘터·벤치·노선안내판 — 승강장(|y| ≥ 1.76 반대편) · 스트립 밖
    ("Dress-Shelter", "cue_scene_dressing",          1.60,  5.60,  -3.06, -1.76, 2.70),
    ("Dress-Bench",  "cue_scene_dressing",          -6.20, -4.20,  -2.65, -2.15, 0.46),
    ("Dress-Hedge",  "cue_scene_dressing",          -4.00, 14.00,   3.55,  4.05, 0.60),
    ("Dress-Far",    "cue_scene_dressing",         -14.00, 30.00,   8.80, 16.00, 5.40),
    ("Dress-Across", "cue_scene_dressing",          -6.00, 26.00, -22.00, -13.00, 6.00),
]


# ===========================================================================
# [C'] PLACEMENT — `placement_lint.py` 의 기하 무관 선언 블록 (w3_execution_spec §10.4)
# ===========================================================================
PLACEMENT = dict(
    # `walk_edges` 는 **의도적으로 비운다** — 그리고 이것은 누락이 아니라 판정이다.
    #   LINT-5 의 근거문(PE-8)이 적은 계산형은 `setback_far_edge <= sidewalk_width − 1.5`
    #   인데, 구현(`placement_lint.py:860-874`)은 **선언된 모든 edge 중 가장 가까운 선**
    #   까지의 거리 `d` 를 재어 `d − occ/2 ≥ 1.5` 를 요구한다. 보도의 양 경계를 둘 다
    #   선언하면 항상 **가까운 쪽**이 잡히므로 규칙의 자기 계산형과 **부호가 뒤집힌다** —
    #   그 상태에서는 *"부재는 보도 경계에서 1.5 m 이상 안쪽에 있어야 한다"* 가 되는데,
    #   **버스정류장은 표지주·승차대·점형블록이 법정으로 승강장 가장자리에 서는 시설**
    #   이라 원리적으로 통과할 수 없다(표지 occ 1.80 ⇒ 경계에서 2.40 m 안쪽 요구 =
    #   연석에서 2.40 m 물러난 정류장 표지 = 실물에 없는 배치).
    #   통과시키려고 없는 데이텀을 지어내면 그 규칙은 검사가 아니라 허구가 된다
    #   (spec §1.8 "prepare vs enforce" · SCENE_H67_BUILD §5-5 · SCENE_TEXT_BUILD §8-5
    #   승계 — sceneH1·H2·L1 과 같은 판단). **미선언은 `nodata` WARN 으로 보고되지
    #   거짓 통과가 아니다.** 대신 실제 유효폭 규정은 이 씬의 CPU 자기검사가 직접
    #   강제한다 — 「보도 유효폭 3.40 m 위 수직 부재 0건」 (아래 `_geometry_selfcheck`).
    walk_edges=[],
    kerb_lines=[((-34.0, -4.20), (44.0, -4.20))],
    anchors={
        # 승강장 벤치는 **차도를 향한다**(대기 승객이 진입 버스를 본다) = 270°.
        "platform": dict(face_bearing_deg=270.0, props=["Dress/Bench_0"]),
        # `sc.build_sign` 의 `/Panel` 은 월드 좌표로 직접 작도되는 메시라 xformOp 가
        #   없다(scene_common.py:4572-4595). 실제 정면 방위는 `/Back` 이 갖는다.
        # **[개정 R1]** 표지 판면이 접근 보행자를 향한다 ⇒ 방위 180°.
        "busstop_sign": dict(face_bearing_deg=180.0, props=["Sign/Back"]),
        "walk_axis": dict(face_bearing_deg=0.0, props=["Sign/Panel"]),
    },
    # 가로수 열 — 1열 1수종(S-1) · 피치 **7.0 m**(조례 제7조1가 6~8 m 법정 밴드) ·
    #   방위 = 연석 방위 0°. `pts` 는 전 그루의 좌표여야 한다(LINT-2 는 인접 간격을
    #   그대로 피치로 읽는다).
    routes={
        "furnish_N": dict(pts=[(2.60, 3.00), (9.60, 3.00), (16.60, 3.00)],
                          species="zelkova", pitch_m=7.0),
    },
)


# ===========================================================================
# 격자·폴라 모형 — pxr 없이 CPU 로 돈다. **이 씬의 판정은 "전부 음성"이다.**
# ===========================================================================
SECTOR_NAMES = ("A", "B", "C", "D", "E")
SECTOR_EDGES = (31.1, 18.66, 6.22, -6.22, -18.66, -31.1)   # gridspec_v1
BAND_EDGES = (0.0, 2.0, 5.0, 8.0, 12.0)                    # gridspec_v1
GRID = dict(x0=-2.0, x1=14.0, y0=-8.0, y1=8.0)             # 높이맵 격자
HAZ_DEPTH = 0.30                                            # gridspec_v1 hazard_depth_m


def _profile_z(x):
    """보행축 종단면 z(x). 이 씬은 **전 구간 평탄**이다 (계단 0단 · 경사 0)."""
    return PARAMS["terrain"]["walk_z"]


def _road_z():
    """차도 노면 z — `hazard_platform_edge` 상태를 따른다.

    **왜 단서가 이 함수를 부르는가**: 노면표시는 노면 위에 있는 도색이지 공중에 뜬
    프림이 아니다. `cue_road_marking` 빌더를 `if cfg["hazard_*"]` **안에 넣는 것**은
    금지되지만(프림 위생 1), 지면 높이를 조회하는 것은 sceneL1 의 볼라드가
    `_profile_z(x)` 를 부르는 것과 같은 패턴이고 금지 대상이 아니다.
    """
    h = PARAMS["hazard"]
    return h["road_z"] if SCENE_CONFIG["hazard_platform_edge"] else h["fill_z"]


def _grid_min_z():
    """격자 안 **최저 상면 z** 의 해석적 값 — 파일 상단 「격자 안 최저점 회계」.

    반환 (z_min, 최저를 만든 요소). 이 값과 보행면(0.000)의 차가 `HAZ_DEPTH` 미만이면
    이 씬은 구성상 GT 올-음성이다.
    """
    T = PARAMS["terrain"]
    cands = [(_road_z(), "차도·정차대"), (T["walk_z"], "보도·승강장·시설물대")]
    if SCENE_CONFIG["cue_drainage"]:
        cands.append((T["walk_z"] - 0.008, "빗물받이 그레이팅(flush)"))
    if SCENE_CONFIG["cue_slab_joint"]:
        cands.append((T["walk_z"] - 0.003, "수축줄눈 recess"))
    return min(cands)


def _cell_of(x, y, eye, yaw_deg):
    """(x, y) 가 떨어지는 폴라 셀 = (band, sector) 또는 None. `labeler.polar_cells` 와
    같은 산술이다."""
    cy, sy = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    dx, dy = x - eye[0], y - eye[1]
    xc, yc = dx * cy + dy * sy, -dx * sy + dy * cy
    rng = math.hypot(xc, yc)
    if rng >= BAND_EDGES[-1]:
        return None
    az = math.degrees(math.atan2(yc, xc))
    if az > SECTOR_EDGES[0] or az < SECTOR_EDGES[-1]:
        return None
    s = 0
    while s < 5 and az < SECTOR_EDGES[s + 1]:
        s += 1
    if s >= 5:
        return None
    b = 0
    while b < 4 and rng >= BAND_EDGES[b + 1]:
        b += 1
    return b, s


def _trunc_norm(rng, mu, sd, lo, hi):
    for _ in range(64):
        v = rng.gauss(mu, sd)
        if lo <= v <= hi:
            return v
    return min(max(rng.gauss(mu, sd), lo), hi)


def _cue_visibility_mc(d_lo=1.2, d_hi=12.0, n=800, seed=29):
    """**주 단서(점형블록 띠)가 폴라 격자 안에 들어오는 포즈 비율** 의 MC 추정.

    N-cue 씬의 판정 하나가 *"단서가 화면에 실제로 있는가"* (§12-5 의 k 게이트)인데,
    렌더 전에 그 도달성을 기하로 미리 재 둔다. 렌더 후에는 **strict 세그 마스크의
    cue 픽셀 수**가 같은 질문에 실측으로 답한다 — 이 MC 는 그 실측의 사전 예측이다.

    반환: dict(band_frac — 점형블록 띠 표본이 격자 안에 있는 포즈 비율,
               cells — 프레임당 격자 안 점형블록 셀 수 평균)
    """
    t = PARAMS["tactile"]["warn"]
    pts = []
    x = max(GRID["x0"], t[0])
    while x <= min(GRID["x1"], t[2]) + 1e-9:
        y = t[1]
        while y <= t[3] + 1e-9:
            pts.append((x, y))
            y += 0.15
        x += 0.15
    rng = random.Random(seed)
    n_any, cells = 0, 0
    for _ in range(n):
        d = math.exp(rng.uniform(math.log(d_lo), math.log(d_hi)))
        y_c = _trunc_norm(rng, 0.0, 0.35, -0.90, 0.90)
        yaw = _trunc_norm(rng, 0.0, 8.0, -20.0, 20.0)
        eye = (-d, y_c)
        hit = set()
        for (px, py) in pts:
            c = _cell_of(px, py, eye, yaw)
            if c is not None:
                hit.add(c)
        if hit:
            n_any += 1
        cells += len(hit)
    return dict(band_frac=n_any / n, cells=cells / n, n_pts=len(pts))


def build_views():
    """카메라 프리셋: grid_views(gy=0, 보행축 +X) + 미장경 4컷."""
    views = sc.grid_views(0.0)
    # busstop_approach: 보행축 저시점 — 점형블록 띠와 쉘터가 한 프레임에
    views["busstop_approach"] = dict(eye=[-6.0, 0.20, 0.95], tgt=[6.0, -2.0, -0.15])
    # platform_edge: 승강장 경계 근접 — 점형블록·연석·차도 단차 0.20 m 의 스케일
    views["platform_edge"] = dict(eye=[0.60, -1.60, 1.55], tgt=[8.0, -4.4, -0.45])
    # shelter_face: 승차대 정면 — 쉘터·벤치·노선안내판이 "정류장"으로 읽히는가
    views["shelter_face"] = dict(eye=[3.60, 1.40, 1.70], tgt=[3.60, -3.6, 0.20])
    # street_over: 가로 전경 — 방호울타리 · 가로수 · 상가가 층을 이루는 사면 컷
    views["street_over"] = dict(eye=[-11.0, 5.6, 5.2], tgt=[6.0, -3.0, -0.4])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트 — N-cue 전용]
 1. shelter_face   — **정류장으로 읽히는가** (쉘터·벤치·노선안내판·표지주)
                     읽히지 않으면 이 씬은 함정으로 성립하지 않는다 (D58 ③)
 2. platform_edge  — 연석 단차가 **0.20 m 급**으로 보이는가 (철도 승강장처럼 보이면 실패)
 3. busstop_approach — 점형블록 띠가 보행 시점에서 **읽히는가** (§12-5 k 의 육안 판)
 4. street_over    — 방호울타리가 **횡단 금지용**으로 읽히는가 (추락 가드로 보이면 그것도
                     함정의 일부지만, 그 너머가 **차도**임이 같은 프레임에 있어야 한다)
 5. cue ON vs OFF  — 단서 토글 시 **지면 기하 불변**인가 (노면표시 제외 전부 flush)
 6. 접지·순백      — 순백(>0.8) 대면적 없음 · 모든 프림 접지 · Z파이팅 없음
 7. props 규율     — 볼라드 피치 1.50 · 가로수 피치 7.0 · 조형물 0 · 차량 0(법5)"""


def main():
    # [GT-89] SMOKE 게이트 — Isaac 부팅 **전** 조기 종료 (GPU·GUI 미사용).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1" \
            and os.environ.get("NEGOBS_SMOKE_ASSEMBLE", "0") != "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        if not _geometry_selfcheck():
            raise SystemExit("sceneN9 CPU 자기검사 실패")
        return
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/SceneN9")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    T = PARAMS["terrain"]
    HZ = PARAMS["hazard"]
    ROOT = "/World/SceneN9"

    def BOX(path, center, size, mtl=None, col=False, rotZ=0.0):
        return sc.add_box(stage, path, center, size, mtl, collider=col, rotZ=rotZ)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # [VG-void] 타일 이음매 여유 — 인접 슬래브가 정확히 같은 좌표에서 맞닿으면
    #   `AabbPrefilter.ground_z` 의 하향 레이가 두 상자의 면을 동시에 스치며 둘 다 놓친다
    #   (sceneH7 스모크 실측). 4 mm 겹침을 주면 겹친 구간에서 더 높은 상자가 이기므로
    #   경계가 4 mm 이동할 뿐이다(격자 피치 50 mm 의 1/12).
    SEAM = 0.004

    def RECT(path, x0, y0, x1, y1, z_top, base, mtl, col=True, seam=True):
        """축정렬 지면 상자. 회전 상자를 쓰지 않는 이유는 `AabbPrefilter.ground_z`
        (상방 레이 최초 히트)가 회전체의 월드 AABB 를 평면으로 읽기 때문이다."""
        if seam:
            x0, y0, x1, y1 = x0 - SEAM, y0 - SEAM, x1 + SEAM, y1 + SEAM
        return BOX(path, ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z_top + base) / 2.0),
                   (x1 - x0, y1 - y0, z_top - base), mtl, col=col)

    # -------------------------------------------------------------------
    # 재질 (3단 규약)
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["walk"] = PBR(f"{ROOT}/Looks/PavingInterlock",
                        sc.tex_path("paving_interlock", "diff"),
                        sc.tex_path("paving_interlock", "nor"),
                        sc.tex_path("paving_interlock", "rough"),
                        sca["paving_interlock"], tint=mp["walk_tint"])
        M["walk_alt"] = PBR(f"{ROOT}/Looks/ConcretePave",
                            sc.tex_path("concrete_floor", "diff"),
                            sc.tex_path("concrete_floor", "nor"),
                            sc.tex_path("concrete_floor", "rough"),
                            sca["concrete_floor"], tint=mp["walk_alt_tint"])
        M["plat"] = PBR(f"{ROOT}/Looks/GraniteFlag",
                        sc.tex_path("granite_dark", "diff"),
                        sc.tex_path("granite_dark", "nor"),
                        sc.tex_path("granite_dark", "rough"),
                        sca["granite_dark"], tint=mp["plat_tint"])
        M["front"] = PBR(f"{ROOT}/Looks/StoneFlagFront",
                         sc.tex_path("stone_flag", "diff"),
                         sc.tex_path("stone_flag", "nor"),
                         sc.tex_path("stone_flag", "rough"),
                         sca["stone_flag"], tint=mp["front_tint"])
        M["furnish"] = PBR(f"{ROOT}/Looks/GraniteFurnish",
                           sc.tex_path("granite_dark", "diff"),
                           sc.tex_path("granite_dark", "nor"),
                           sc.tex_path("granite_dark", "rough"),
                           sca["granite_dark"], tint=mp["furnish_tint"])
        M["curb"] = PBR(f"{ROOT}/Looks/GraniteCurb",
                        sc.tex_path("granite_dark", "diff"),
                        sc.tex_path("granite_dark", "nor"),
                        sc.tex_path("granite_dark", "rough"),
                        sca["granite_dark"], tint=mp["curb_tint"])
        M["road"] = PBR(f"{ROOT}/Looks/Asphalt",
                        sc.tex_path("asphalt", "diff"),
                        sc.tex_path("asphalt", "nor"),
                        sc.tex_path("asphalt", "rough"),
                        sca["asphalt"], tint=mp["road_color"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"),
                         sc.tex_path("grass", "rough"),
                         sca["grass"], tint=mp["grass_tint"])
        M["tactile"] = sc.tactile_pbr(stage, f"{ROOT}/Looks/Tactile",
                                      scale_m=sca["tactile"])
        # **선형블록 전용 재질** — 점형(도트) 노멀맵을 선형블록에 바르면 그것은
        #   재질 층에서 다시 점형이 된다(D82 ⓐ 역할 구분 위반). 돌출선은 **기하**로
        #   짓고 재질은 평면 안전 황색만 쓴다. `Looks/TactileLinear` 는 look 층에서
        #   `paint` 클래스(상수색·텍스처 치환 없음)로 분류된다 [실측].
        #   알베도 0.53 < `ground_kit.TACTILE_ALBEDO_CAP` 0.55.
        M["tactile_lin"] = PBR(f"{ROOT}/Looks/TactileLinear",
                               diffuse_color=mp["tactile_lin_color"],
                               roughness_const=0.70)
        # 금속·도색·사인 = OmniPBR
        M["fence"] = PBR(f"{ROOT}/Looks/FenceSteel",
                         diffuse_color=mp["fence_color"], metallic=mp["fence_metal"],
                         roughness_const=mp["fence_rough"])
        M["shelter"] = PBR(f"{ROOT}/Looks/ShelterSteel",
                           diffuse_color=mp["shelter_color"],
                           metallic=mp["shelter_metal"],
                           roughness_const=mp["shelter_rough"])
        M["roof"] = PBR(f"{ROOT}/Looks/ShelterRoof",
                        diffuse_color=mp["roof_color"],
                        roughness_const=mp["roof_rough"])
        M["board"] = PBR(f"{ROOT}/Looks/RouteBoard",
                         diffuse_color=mp["board_color"], roughness_const=0.40)
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing", diffuse_color=mp["nosing_color"],
                          roughness_const=mp["nosing_rough"])
        M["band"] = PBR(f"{ROOT}/Looks/GuardBand", diffuse_color=mp["band_color"],
                        roughness_const=0.35)
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["iron"] = PBR(f"{ROOT}/Looks/Iron", diffuse_color=mp["iron_color"],
                        metallic=mp["iron_metallic"],
                        roughness_const=mp["iron_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["mark_w"] = PBR(f"{ROOT}/Looks/MarkPaintW",
                          diffuse_color=mp["mark_white"],
                          roughness_const=mp["mark_rough"])
        M["mark_y"] = PBR(f"{ROOT}/Looks/MarkPaintY",
                          diffuse_color=mp["mark_yellow"],
                          roughness_const=mp["mark_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA", diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"])
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB", diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"])
        M["shrub"] = PBR(f"{ROOT}/Looks/Shrub", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
                         1.1, tint=mp["shrub_tint"])
        M["backdrop"] = PBR(f"{ROOT}/Looks/BgConcrete",
                            diffuse_color=mp["backdrop_color"],
                            roughness_const=mp["backdrop_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", sc.tex_path("sign_info", "diff"),
                        uv_mode=True)
        return M

    # -------------------------------------------------------------------
    # ① 경로 — 지형. **hazard_* 밖**. 4팔 전부에서 동일 프림·동일 좌표.
    # -------------------------------------------------------------------
    def build_terrain(M):
        """보도 · 승강장 · 연석 배면 · 시설물대 · 상가 전면 공지.

        전부 **z = 0.000 단일 레벨**이다 — 이 씬에는 보행면 표고차가 없다.
        `cam.ground_z` 가 이 프림들만으로 결정되므로 VG-datum 은 `datum_exact` 로
        통과하도록 **구성상** 되어 있다.
        """
        zw, bz, x0, x1 = T["walk_z"], T["base_z"], T["x0"], T["x1"]
        pl, tb, sb, fu, fr = (T["platform"], T["tactile_band"], T["setback"],
                              T["furnish"], T["frontage"])
        # (1) 보도 유효폭 — `cue_material_break` 의 유일한 대상 (재바인딩 전용)
        walk_mtl = M["walk"] if cfg["cue_material_break"] else M["walk_alt"]
        RECT(f"{ROOT}/Ground/Walk", x0, -T["walk"]["y_half"], x1,
             T["walk"]["y_half"], zw, bz, walk_mtl)
        print(f"[cue] material_break={cfg['cue_material_break']} → Walk = "
              f"{'인터로킹 블록(PavingInterlock)' if cfg['cue_material_break'] else '콘크리트 타설(ConcretePave)'}"
              " · **프림 집합 불변**(재질 재바인딩 전용) → 높이맵 비트 동일 보증")
        # (2) 승강장 대기공간 (화강석 판석) — 쉘터·벤치가 서는 자리
        RECT(f"{ROOT}/Ground/Platform", x0, pl["y0"], x1, pl["y1"], zw, bz,
             M["plat"])
        # (3) 점형블록 띠가 앉는 판석 바탕 (블록이 OFF 여도 지면은 있어야 한다)
        RECT(f"{ROOT}/Ground/EdgeBed", x0, tb["y0"], x1, tb["y1"], zw, bz,
             M["plat"])
        # (4) 연석 배면 여유 — 방호울타리·볼라드가 서는 0.30 m 띠
        RECT(f"{ROOT}/Ground/Setback", x0, sb["y0"], x1, sb["y1"], zw, bz,
             M["plat"])
        # (5) 건물측 시설물대 — 가로수·가로등·수목보호격자
        RECT(f"{ROOT}/Ground/Furnish", x0, fu["y0"], x1, fu["y1"], zw, bz,
             M["furnish"])
        # (6) 상가 전면 공지 — 격자 |y| ≤ 8 을 끝까지 덮는다 (VG-void)
        RECT(f"{ROOT}/Ground/Frontage", x0, fr["y0"], x1, T["y_far"], zw, bz,
             M["front"])
        print(f"[구조] 보도 유효폭 {2 * T['walk']['y_half']:.2f} m · 승강장 "
              f"{pl['y1'] - pl['y0']:.2f} m · 점형블록 띠 세로 "
              f"{tb['y1'] - tb['y0']:.2f} m · 연석 배면 {sb['y1'] - sb['y0']:.2f} m "
              f"· **전 구간 z = {zw:+.3f} (표고차 0)**")

    # -------------------------------------------------------------------
    # ② "위험" 축 — hazard_platform_edge 전속. 여기에는 **단서가 한 개도 없다**.
    # -------------------------------------------------------------------
    def build_platform_edge(M):
        """차도면을 연석 높이만큼 내리고 화강석 연석을 세운다.

        **이것은 낙차가 아니다.** 표고차 0.200 m 는 `gridspec_v1.hazard_depth_m = 0.30`
        미만이므로 라벨러 발자국(`z_off − z_on ≥ 0.30`)이 한 셀도 켜지지 않는다.
        FA_REALITY §3 L6 이 명시한 실측 밴드(연석 0.15–0.25 m)의 중앙값이다.
        """
        c, x0, x1 = T["curb"], T["x0"], T["x1"]
        sc.skin_exclude(f"{ROOT}/Road", f"{ROOT}/Curb")
        # 연석 — 상면이 승강장과 같은 0.000 (그래서 연석 위 프림이 팔 불변이다)
        RECT(f"{ROOT}/Curb/Stone", x0, c["y0"], x1, c["y1"], T["walk_z"],
             T["base_z"], M["curb"])
        # 차도·정차대 — 격자 |y| ≤ 8 을 끝까지 덮는다 (VG-void)
        RECT(f"{ROOT}/Road/Asphalt", x0, -T["y_far"], x1, c["y0"],
             HZ["road_z"], T["base_z"], M["road"])
        drop = T["walk_z"] - HZ["road_z"]
        print(f"[hazard-axis] 승강장 경계 단차 ON — 연석 상면 {T['walk_z']:+.3f} → "
              f"차도면 {HZ['road_z']:+.3f} · **표고차 {drop:.3f} m** "
              f"< 임계 {HAZ_DEPTH:.2f} m (여유 {HAZ_DEPTH - drop:.3f} m) "
              "⇒ 발자국 0셀 · GT 올-음성 [FA_REALITY §3 L6 연석 0.15–0.25 m]")

    def build_flush_road(M):
        """hazard_platform_edge=False 대조군 — **고원식(플랫폼형) 정류장**.

        차도면이 승강장과 같은 0.000 으로 올라온다. 이것이 라벨러의 반사실 보행
        가능면 `z_off` 이며, 실재하는 공법(고원식 정류장 · 보행자우선도로)이므로
        반사실 팔도 독립적으로 그럴듯하다.
        """
        RECT(f"{ROOT}/RoadFlush/Asphalt", T["x0"], -T["y_far"], T["x1"],
             T["curb"]["y1"], HZ["fill_z"], T["base_z"], M["road"])
        print(f"[hazard-axis] OFF — 반사실 노면 z_off = {HZ['fill_z']:+.3f} "
              f"(|y| ≥ {abs(T['curb']['y1']):.2f} · 고원식 정류장) "
              "⇒ z_off − z_on = 0.200 m, 여전히 임계 미만")

    # -------------------------------------------------------------------
    # ③ 단서 — **전부 hazard_* 밖의 자립 프림**.
    # -------------------------------------------------------------------
    def build_tactile(M):
        """**이 씬의 주 단서** — 승차 위치 **점형 1밴드** + **선형 유도로 1줄**.

        **[개정 R3 · D82 ⓐ]** 역할 구분을 기하로 강제한다:
          · **점형(경고)** = `sc.build_tactile`(도트형) · 승차 위치 1.80 × 0.60 m,
            연석 배면에서 **0.30 m 이격**. [**별표1 버목 3)** — 버스 승강장 승차 위치 / ADA §705.2]
          · **선형(유도)** = `_linear_tactile()` · 보도 → 승차 위치 0.30 × 1.42 m,
            **돌출선이 보행 방향(−y)과 나란하다**. [**별표1** — 선형블록 = 유도]
        점형으로 유도로를 까는 것은 S37 이 집계한 오설치 유형이므로 금지한다.
        """
        t = PARAMS["tactile"]
        wx0, wy0, wx1, wy1 = t["warn"]
        sc.build_tactile(stage, f"{ROOT}/Tactile/Warn", wx0, wx1, wy0, wy1,
                         M["tactile"], z=T["walk_z"], proud=t["proud"])
        gx0, gy0, gx1, gy1 = t["guide"]
        n_bar = _linear_tactile(M, f"{ROOT}/Tactile/Guide", gx0, gy0, gx1, gy1,
                                T["walk_z"], t)
        area_w = (wx1 - wx0) * (wy1 - wy0)
        area_g = (gx1 - gx0) * (gy1 - gy0)
        print(f"[cue] tactile ON — **점형(경고) 1밴드** {wx1 - wx0:.2f} × "
              f"{wy1 - wy0:.2f} m (승차 위치 · 연석 배면에서 "
              f"{abs(T['curb']['y1'] - wy1):.2f} m 이격) + **선형(유도) 1줄** "
              f"{gx1 - gx0:.2f} × {gy1 - gy0:.2f} m ({n_bar}줄 돌출선, 보행 방향) · "
              f"**총 {area_w + area_g:.2f} m²** "
              "[규격 교통약자법 시행규칙 **별표1** · ADA §705.2/§810 · D82 ⓐⓒ]")

    def _linear_tactile(M, path, x0, y0, x1, y1, z, t):
        """**선형블록(유도)** — 바탕판 + 평행 돌출선. 점형(도트)과 **기하가 다르다**.

        [규격 **별표1**] 선형블록의 돌출선은 유닛(0.30 m)당 **4줄**이고 **보행 방향과
        나란하다**. 이 씬의 유도 방향은 −y(보도 → 승차 위치)이므로 선은 y 축을 따른다.
        """
        w, bw, pitch = x1 - x0, t["guide_bar_w"], t["guide_bar_pitch"]
        BOX(f"{path}/Base", (0.5 * (x0 + x1), 0.5 * (y0 + y1), z + 0.001 - 0.01),
            (w, y1 - y0, 0.020), M["tactile_lin"])
        n = max(1, int(round(w / pitch)))
        for i in range(n):
            bx = x0 + w * (i + 0.5) / n
            BOX(f"{path}/Bar_{i}", (bx, 0.5 * (y0 + y1),
                                    z + t["guide_proud"] - 0.005),
                (bw, y1 - y0, 0.010), M["tactile_lin"])
        return n

    def build_fence(M):
        """보행자 방호울타리 (**FA_REALITY §3 L4**) — 정류장 구간은 개방.

        [규격 「도로안전시설 설치 및 관리지침 — 보행자용 방호울타리편」]
        목적을 **①추락 방지 ②횡단 금지 ③보행 안전** 으로 **병렬** 규정한다 —
        즉 같은 외형이 낙차와 무관하게 서는 제도적 근거가 있다. 이 씬에는 낙차가
        없고 울타리의 목적은 **무단횡단 금지** 하나다.
        """
        f = PARAMS["fence"]
        zw = T["walk_z"]
        n_post = 0
        for si, (sx0, sx1) in enumerate(f["spans"]):
            n = int(math.floor((sx1 - sx0) / f["post_pitch"])) + 1
            for i in range(n):
                x = sx0 + i * f["post_pitch"]
                # 지주는 **정렬해 세운다** — 실제 시공이 그러하고 J-3/J-5(07-30)가
                #   배치 지터를 폐지했다(LINT-10 정적 검사 대상).
                CYL(f"{ROOT}/Fence/Span{si}_Post_{i:02d}",
                    (x, f["y"], zw + f["post_h"] / 2.0), f["post_r"],
                    f["post_h"], M["fence"])
                n_post += 1
            for nm, z in (("Top", f["top_z"]), ("Mid", f["mid_z"])):
                CYL(f"{ROOT}/Fence/Span{si}_{nm}Rail",
                    (0.5 * (sx0 + sx1), f["y"], zw + z), f["rail_r"],
                    sx1 - sx0, M["fence"], rotY=90.0)
        gap = f["spans"][1][0] - f["spans"][0][1]
        print(f"[cue] railing(방호울타리) ON — L4 · 지주 {n_post}본(피치 "
              f"{f['post_pitch']} m) · 가드선 {f['top_z']:.2f} m · "
              f"**정류장 구간 {gap:.2f} m 개방**(승하차 동선) · y {f['y']:+.2f} "
              "[규격 도로안전시설 지침 — 목적 ①추락 ②횡단금지 ③보행안전 병렬]")

    def build_nosing(M):
        """평탄 승강장에는 계단이 없으므로 기본 OFF. 코드 경로만 보유한다(법4).

        켜면 보도 중앙 횡단 논슬립 띠 1줄이 서지만 **대상 계단이 없다** — 이 씬에서
        이 키를 켜는 것은 어블레이션 목적 외에는 의미가 없다.
        """
        ng = PARAMS["terrain"]
        BOX(f"{ROOT}/Nosing/Strip_0", (0.0, 0.0, T["walk_z"] + 0.006),
            (0.20, 2 * ng["walk"]["y_half"], 0.012), M["nosing"])
        print("[cue] nosing ON — **대상 계단 없음**(평탄 승강장). 어블레이션 전용 1줄")

    def build_sign(M):
        """버스정류장 안내 표지 1매 — 법2(임의 경고판 금지): 법정 제식 판만.

        **임의 경고 문구를 넣지 않는 것이 이 씬의 실험 조건이다** — "추락주의" 같은
        판을 하나라도 넣으면 그것이 곧 낙차 단서가 되어 함정의 무죄가 깨진다.
        """
        s = PARAMS["sign"]
        sc.build_sign(stage, f"{ROOT}/Sign", s["x"], s["y"], T["walk_z"],
                      s["yaw"], M["sign"], w=s["w"], h=s["h"],
                      pole_h=s["pole_h"], pole_mtl=M["pole"], back_mtl=M["iron"])
        print(f"[cue] sign ON — 버스정류장 안내 표지 1매 @({s['x']:+.2f},"
              f"{s['y']:+.2f}) · 지주 {s['pole_h']:.2f} m · 임의 경고문구 0 (법2)")

    def build_bollards(M):
        """보도 서측 진입부 차량 진입 억제 볼라드 열. 피치 1.50 m 법정치."""
        b = PARAMS["bollard"]
        for i, x in enumerate(b["xs"]):
            gz = _profile_z(x)
            # `placement_lint` 의 `props.bollard` 규약: `Bollard_NN` + `/Post` + `/Band`.
            CYL(f"{ROOT}/Bollard_{i:02d}/Post", (x, b["y"], gz + b["h"] / 2.0),
                b["r"], b["h"], M["bollard"])
            CYL(f"{ROOT}/Bollard_{i:02d}/Band", (x, b["y"], gz + b["band_z"]),
                b["r"] + 0.004, b["band_t"], M["band"])
        print(f"[cue] bollard ON — {len(b['xs'])}본 · h {b['h']} m · "
              f"φ{2 * b['r']:.2f} m · 피치 1.50 m · y {b['y']:+.2f} (연석 배면) "
              "· 반사띠 [규격 행정안전부 볼라드 설치기준]")

    def build_road_marking(M):
        """정차대 노면표시 + 차선 — **FA_REALITY §2 6위 `cue_road_marking` 키 승격**.

        갭 지도: *"씬별 on/off 는 되나 **키 아님**. 키 승격만 필요(신규 기하 0)"*.
        노면 위 도색이므로 z 는 `_road_z()` 를 따른다(위 함수 주석 참조).
        면적을 최소화하고 알베도를 0.70 으로 낮춘다 — v5.1 §4 순백 대면적 금지.
        """
        mk = PARAMS["marking"]
        rz = _road_z() + mk["z_off"]
        bx0, by0, bx1, by1 = mk["bay"]
        w = mk["bay_w"]
        # 정차대 테두리 — 황색 실선 3변 (차도 안쪽 변은 차선이 대신한다)
        for nm, a, b_, c_, d_ in (("N", bx0, by1 - w, bx1, by1),
                                  ("S", bx0, by0, bx1, by0 + w),
                                  ("W", bx0, by0, bx0 + w, by1)):
            BOX(f"{ROOT}/Marking/Bay{nm}",
                (0.5 * (a + c_), 0.5 * (b_ + d_), rz),
                (c_ - a, d_ - b_, 0.003), M["mark_y"])
        lx0, ly0, lx1, ly1 = mk["lane"]
        BOX(f"{ROOT}/Marking/Lane",
            (0.5 * (lx0 + lx1), 0.5 * (ly0 + ly1), rz),
            (lx1 - lx0, ly1 - ly0, 0.003), M["mark_w"])
        print(f"[cue] road_marking ON — 정차대 테두리 3변({bx1 - bx0:.2f} × "
              f"{by1 - by0:.2f} m, 폭 {w:.2f}) + 차선 1줄 · 노면 z "
              f"{_road_z():+.3f} · 알베도 0.70 (순백 대면적 금지 v5.1 §4) "
              "[FA_REALITY §2 6위 키 승격 · 신규 기하 0]")

    def build_ground_kit(M):
        """지면 문양 (`cue_manhole`·`cue_slab_joint`·`cue_drainage`) + `cue_tree_grate`.

        전부 **flush**(융기 ≤ 8 mm · 줄눈은 recess 3 mm)이므로 법7(기하 불변)을 지킨다.
        """
        g = PARAMS["gkit"]
        M2 = dict(M)
        M2.update(joint=M["curb"], crack=M["curb"], manhole=M["iron"],
                  gully=M["iron"], gutter=M["curb"], gutter_cover=M["iron"],
                  trench=M["iron"], trench_frame=M["iron"], marking=M["lamp"],
                  weed=M["grass"], wear=M["furnish"], stain_dirt=M["furnish"],
                  stain_water=M["furnish"], tree_grate=M["iron"], grate=M["iron"],
                  patch=M["walk_alt"], patch_cut=M["curb"])
        kit = gk.kit_from_scene_common(sc, stage)
        n_prims = 0

        # (a) 보도 본선 — 시공줄눈 + 맨홀 + 빗물받이 (**격자 안** · 전부 flush)
        infra = dict(manhole=len(g["walk_manholes"]) if cfg["cue_manhole"] else 0,
                     gully=len(g["walk_gullies"]) if cfg["cue_drainage"] else 0,
                     gutter_L=0)
        sites = dict()
        if cfg["cue_manhole"]:
            sites["manhole"] = [tuple(v) for v in g["walk_manholes"]]
        if cfg["cue_drainage"]:
            sites["gully"] = [tuple(v) for v in g["walk_gullies"]]
        gp = gk.plan_ground(
            "sidewalk_block", region=tuple(g["walk_region"]), z=T["walk_z"],
            gy=0.0, origin=(0.0, 0.0, 0.0),
            dists=(2, 5, 10), scene="sceneN9", tactile=(),
            # `surface=None` — 잡초/균열/오염 데칼 OFF. 1차 이유는 **법1**(손상·노후
            #   표현 금지: N-cue 씬은 "온전한 시설만"이 성립 조건이다), 2차 이유는
            #   잡초 프림(proud 최대 0.107 m)이 데이텀 스트립을 `datum_fail` 로 밀 수
            #   있다는 것이다.
            overrides=dict(infra=infra, surface=None), sites=sites, seed=71)
        if not cfg["cue_slab_joint"]:
            gp["ops"] = [o for o in gp["ops"] if o["name"] != "joints"]
            gp["elements"] = [e for e in gp["elements"] if e["kind"] != "joint"]
        res = gk.apply_ground(kit, f"{ROOT}/GKitWalk", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        n_prims += res["prims"]

        # (b) 승강장 판석 줄눈만 (맨홀·빗물받이 없음 — 승강장에는 두지 않는다)
        gp2 = gk.plan_ground(
            "sidewalk_block", region=tuple(g["plat_region"]), z=T["walk_z"],
            gy=0.0, origin=(0.0, 0.0, 0.0),
            dists=(2, 5, 10), scene="sceneN9", tactile=(),
            overrides=dict(infra=dict(manhole=0, gully=0, gutter_L=0),
                           surface=None), sites=dict(), seed=72)
        if not cfg["cue_slab_joint"]:
            gp2["ops"] = [o for o in gp2["ops"] if o["name"] != "joints"]
            gp2["elements"] = [e for e in gp2["elements"] if e["kind"] != "joint"]
        res2 = gk.apply_ground(kit, f"{ROOT}/GKitPlat", gp2, M2,
                               skin_exclude=sc.skin_exclude,
                               scatter=sc.scatter_debris)
        n_prims += res2["prims"]

        # (c) 수목보호격자 — 빌더가 없으므로 flush 격자를 직접 짓는다(갭 2위 = 전무)
        n_grate = 0
        if cfg["cue_tree_grate"]:
            for i, (gx, gy_) in enumerate(g["tree_grates"]):
                n_grate += _tree_grate(M, f"{ROOT}/TreeGrate_{i}", gx, gy_,
                                       T["walk_z"])
        print(f"[cue] ground pattern — manhole={cfg['cue_manhole']}"
              f"({len(g['walk_manholes'])}) tree_grate={cfg['cue_tree_grate']}"
              f"({n_grate} 프림) slab_joint={cfg['cue_slab_joint']} "
              f"drainage={cfg['cue_drainage']}({len(g['walk_gullies'])}) · "
              f"gkit 프림 {n_prims} · δmax "
              f"{max(res['gt_delta_max'], res2['gt_delta_max']):.4f} m (flush — 법7)")
        return n_prims + n_grate

    def _tree_grate(M, path, cx, cy, z, side=1.44, frame=0.09, bar=0.035,
                    n_bar=9, proud=0.004):
        """수목보호덮개 (flush) — 사각 프레임 + 평행 바 격자. 단차 4 mm.
        [FA_REALITY §2 2위] 33씬 **전무**였던 지면 문양. 리세스형(함몰)은 hazard 로
        분리하고 여기서는 **flush 한정**(법7)."""
        n, h = 0, 0.05
        for tag, cx_, cy_, sx, sy in (
                ("FN", cx, cy + (side - frame) / 2.0, side, frame),
                ("FS", cx, cy - (side - frame) / 2.0, side, frame),
                ("FE", cx + (side - frame) / 2.0, cy, frame, side - 2 * frame),
                ("FW", cx - (side - frame) / 2.0, cy, frame, side - 2 * frame)):
            BOX(f"{path}/{tag}", (cx_, cy_, z + proud - h / 2.0), (sx, sy, h),
                M["iron"])
            n += 1
        span = side - 2 * frame
        for i in range(n_bar):
            yy = cy - span / 2.0 + span * (i + 0.5) / n_bar
            BOX(f"{path}/Bar_{i}", (cx, yy, z + proud - h / 2.0),
                (span, bar, h), M["iron"])
            n += 1
        sc.add_disc(stage, f"{path}/Soil", (cx, cy, z - 0.02), 0.22, 0.06,
                    M["furnish"], seg=18)
        return n + 1

    def build_shadow_casters(M):
        """그림자 밴드 캐스터 — 시설물대 가로수 + 가로등주 (`cue_shadow_caster`).

        §2.0 부작용 경보: 이 토글을 **음성 씬에만** 넣으면 "그림자 = 안전"이라는
        역지름길이 생긴다. 본 계획은 양성 신규 씬(H1·H2·H3·L1)과 **같은 비율**로
        음성 씬에도 넣는다 — 이 씬이 그 음성측 표본이다.

        배치 규칙: **줄기는 시설물대 안, 수관은 보도 위로 뻗어도 좋다.** 높이맵은 수직
        레이의 최초 히트이므로 수관이 덮은 셀은 z 가 올라가는데, sceneL1 에서는 그것이
        낙차 발자국을 지웠지만 이 씬에는 지울 발자국이 없고 **상방 이동은 최저점
        회계(= z_max 의 최소값)를 오염시키지 않는다**. 보도 위로 뻗는 수관이 곧
        이 토글이 만들려는 **그림자 밴드**다.
        """
        s = PARAMS["shadow"]
        for i, (tx, ty) in enumerate(s["trees"]):
            sc.build_tree(stage, f"{ROOT}/Shadow/Tree_{i}", tx, ty,
                          _profile_z(tx), M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.13, trunk_h=s["tree_h"] * 0.55,
                          canopy_blobs=10, canopy_spread=0.98, species="zelkova")
        for i, (lx, ly) in enumerate(s["lamps"]):
            gz = _profile_z(lx)
            CYL(f"{ROOT}/Shadow/LampPole_{i}", (lx, ly, gz + s["lamp_h"] / 2.0),
                0.070, s["lamp_h"], M["pole"])
            arm_y = ly - s["lamp_arm"] / 2.0
            CYL(f"{ROOT}/Shadow/LampArm_{i}", (lx, arm_y, gz + s["lamp_h"]),
                0.05, s["lamp_arm"], M["pole"], rotX=90.0)
            BOX(f"{ROOT}/Shadow/LampHead_{i}",
                (lx, ly - s["lamp_arm"], gz + s["lamp_h"] - 0.09),
                (0.44, 0.20, 0.13), M["lamp"])
        print(f"[cue] shadow_caster ON — 시설물대 가로수 {len(s['trees'])}주 "
              f"(피치 7.0 m) + 가로등 {len(s['lamps'])}주 · **보도 유효폭 상부 수관 0**")

    def build_dressing(M):
        """③ 단서의 환경 성분 — **승차대 쉘터 · 벤치 · 노선안내판** + 관목 + 원경 상가.

        **이 함수가 이 씬의 정체성을 만든다.** D58 ③ 의 "화단 난간은 화단으로 읽혀야
        한다"의 이 씬 판본은 *"점형블록 띠가 **정류장** 경고블록으로 읽혀야 한다"* 이고,
        그것을 성립시키는 것은 쉘터·벤치·노선안내판이다. B·D팔에서 이것들이 사라지면
        같은 자리가 그냥 보도가 되는데, 그 대조가 바로 (C,D) 용량-반응의 내용이다.
        """
        d = PARAMS["dress"]
        sh = PARAMS["shelter"]
        zw = T["walk_z"]
        # (a) 승차대 쉘터 — 지붕 + 4주 + 배면 패널 + 벤치
        #   [규격 버스정류장 승차대 표준: 길이 4.0 m · 폭 1.5 m · 유효높이 2.30 m 이상]
        sc.build_canopy(stage, f"{ROOT}/Dress/Shelter", sh["x0"], sh["x1"],
                        sh["y0"], sh["y1"], sh["roof_z"], sh["post_r"],
                        M["roof"], M["shelter"], roof_t=sh["roof_t"], base_z=zw)
        # 배면 패널 (차도 반대편 = 보도측이 아니라 **승강장 배면**에 세운다)
        BOX(f"{ROOT}/Dress/Shelter/BackPanel",
            (0.5 * (sh["x0"] + sh["x1"]), sh["y0"] + sh["back_t"] / 2.0,
             zw + 1.30), (sh["x1"] - sh["x0"], sh["back_t"], 1.90), M["shelter"])
        bx, by, byaw = sh["bench"]
        sc.build_bench(stage, f"{ROOT}/Dress/ShelterBench_0", bx, by, zw,
                       M["wood"], length=2.20, yaw=byaw)
        # (b) 노선안내판 — 쉘터 동측 마구리. 임의 문구 없음(법2): 색면 + 프레임만.
        rb = PARAMS["routeboard"]
        BOX(f"{ROOT}/Dress/RouteBoard/Panel",
            (rb["x"], rb["y"], zw + rb["z"]), (rb["w"], rb["l"], rb["h"]),
            M["board"])
        BOX(f"{ROOT}/Dress/RouteBoard/Frame",
            (rb["x"] - 0.012, rb["y"], zw + rb["z"]),
            (0.024, rb["l"] + 0.06, rb["h"] + 0.06), M["shelter"])
        # (c) 승강장 서측 벤치
        for i, (bx2, by2, byaw2) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Dress/Bench_{i}", bx2, by2,
                           _profile_z(bx2), M["wood"], yaw=byaw2)
        # (d) 시설물대 관목 띠 (가로수 하부)
        for i, (x0, y0, x1, y1) in enumerate(d["hedge"]):
            sc.build_hedge(stage, f"{ROOT}/Dress/Hedge_{i}", x0, y0, x1, y1,
                           d["shrub_h"], mtl=M["shrub"], base_z=zw,
                           rounded=True, crown_max=30)
        # (e) 원경 상가·건너편 — **전부 높이맵 격자(|y| ≤ 8) 밖**이라 라벨 무관.
        if not PLACEBO_REMOVE:
            for tag, x0, x1, y0, y1, hgt in d["shops"] + d["across"]:
                BOX(f"{ROOT}/Dress/Far_{tag}",
                    ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zw + hgt / 2.0),
                    (x1 - x0, y1 - y0, hgt), M["backdrop"])
        else:
            print("[placebo] 원경 상가·건너편 물량군 제거 — "
                  "단서(쉘터·벤치·안내판)는 전부 유지(D35 P팔)")
        print(f"[cue] scene_dressing ON — **승차대 쉘터 "
              f"{sh['x1'] - sh['x0']:.1f}×{sh['y1'] - sh['y0']:.1f} m "
              f"(유효높이 {sh['roof_z']:.2f} m)** · 쉘터 벤치 1 · 노선안내판 1 · "
              f"승강장 벤치 {len(d['benches'])} · 관목 {len(d['hedge'])}띠 · 원경 "
              f"{0 if PLACEBO_REMOVE else len(d['shops']) + len(d['across'])}동")

    # -------------------------------------------------------------------
    # 자기검사 — 조립 직후, 렌더 전
    # -------------------------------------------------------------------
    def scene_selfcheck():
        from pxr import Usd, UsdGeom
        ok = True
        ds = DATUM_STRIP

        # (1) 선언 검사 — 3층(VG-datum) 분류
        cross = [z for z in GATED_ZONES
                 if not (z[3] <= ds["x0"] or z[2] >= ds["x1"]
                         or z[5] <= ds["y0"] or z[4] >= ds["y1"])]
        fail = [z for z in cross if z[6] > DATUM_TOL]
        tol = [z for z in cross if z[6] <= DATUM_TOL]
        if fail:
            ok = False
        print(f"[selfcheck] (1) 데이텀 스트립 × 토글구역 {len(GATED_ZONES)}건 → "
              f"datum_exact {len(GATED_ZONES) - len(cross)} · datum_tol "
              f"{[(t[0], t[6]) for t in tol]} · datum_fail {[f[0] for f in fail]}"
              + ("" if fail else " · OK"))

        # (2) 기계 재확인 — 이 팔에서 실제로 존재하는 토글 프림의 월드 AABB
        bbc = UsdGeom.BBoxCache(Usd.TimeCode.Default(),
                                [UsdGeom.Tokens.default_, UsdGeom.Tokens.render])
        gated_roots = ("/Road", "/Curb", "/RoadFlush", "/Tactile", "/Fence",
                       "/Nosing", "/Sign", "/Bollard", "/Marking", "/GKitWalk",
                       "/GKitPlat", "/TreeGrate", "/Shadow", "/Dress")
        hits, tol_hits, n_scan = [], [], 0
        for prim in stage.Traverse():
            p = str(prim.GetPath())
            if not p.startswith(ROOT) or not prim.IsA(UsdGeom.Gprim):
                continue
            tail = p[len(ROOT):]
            if not any(tail.startswith(g) for g in gated_roots):
                continue
            n_scan += 1
            try:
                b = bbc.ComputeWorldBound(prim).ComputeAlignedRange()
            except Exception:
                continue
            if b.IsEmpty():
                continue
            mn, mx = b.GetMin(), b.GetMax()
            if not (mx[0] > ds["x0"] and mn[0] < ds["x1"]
                    and mx[1] > ds["y0"] and mn[1] < ds["y1"]):
                continue
            x_ref = min(max(0.5 * (mn[0] + mx[0]), ds["x0"]), ds["x1"])
            dz = float(mx[2]) - _profile_z(x_ref)
            (tol_hits if dz <= DATUM_TOL else hits).append((p, round(dz, 4)))
        if hits:
            ok = False
        print(f"[selfcheck] (2) 토글 프림 {n_scan}개 전수 AABB → 스트립 교차 "
              f"{len(hits) + len(tol_hits)}건 (datum_tol {len(tol_hits)} · "
              f"datum_fail {len(hits)})"
              + (f" FAIL={hits[:6]}" if hits else " · OK"))

        # (3) VG-void — 격자 전역 횡단면 커버리지 (해석적)
        segs = [(-T["y_far"], T["curb"]["y0"]),          # 차도 (또는 반사실 노면)
                (T["curb"]["y0"], T["curb"]["y1"]),      # 연석
                (T["setback"]["y0"], T["setback"]["y1"]),
                (T["tactile_band"]["y0"], T["tactile_band"]["y1"]),
                (T["platform"]["y0"], T["platform"]["y1"]),
                (-T["walk"]["y_half"], T["walk"]["y_half"]),
                (T["furnish"]["y0"], T["furnish"]["y1"]),
                (T["frontage"]["y0"], T["y_far"])]
        cover_hi, gap = -T["y_far"], []
        for a, b in sorted(segs):
            if a > cover_hi + 1e-6:
                gap.append((cover_hi, a))
            cover_hi = max(cover_hi, b)
        if cover_hi < T["y_far"] - 1e-6:
            gap.append((cover_hi, T["y_far"]))
        if gap:
            ok = False
        print(f"[selfcheck] (3) VG-void 횡단면 커버리지 |y| ≤ {T['y_far']:.0f} → "
              f"공백 {len(gap)}구간" + (f" {gap}" if gap else " · 커버리지 1.0 · OK"))

        # (4) **격자 안 최저점** 전수 AABB — ④-a 함정의 기계 증명
        #     격자 x ∈ [−2,14] · |y| ≤ 8 에 걸치는 모든 Gprim 의 z_max 중 **지면류**의
        #     최저값이 보행면에서 얼마나 내려가는가. `HAZ_DEPTH` 미만이어야 한다.
        z_min, who = 1e9, None
        for prim in stage.Traverse():
            p = str(prim.GetPath())
            if not p.startswith(ROOT) or not prim.IsA(UsdGeom.Gprim):
                continue
            tail = p[len(ROOT):]
            # 지면류만 본다 — 공중 부재(울타리·쉘터·수관)는 최저점 회계 대상이 아니다.
            if not any(tail.startswith(g) for g in
                       ("/Ground", "/Road", "/RoadFlush", "/Curb", "/GKit",
                        "/Tactile", "/Marking", "/TreeGrate")):
                continue
            try:
                b = bbc.ComputeWorldBound(prim).ComputeAlignedRange()
            except Exception:
                continue
            if b.IsEmpty():
                continue
            mn, mx = b.GetMin(), b.GetMax()
            if not (mx[0] > GRID["x0"] and mn[0] < GRID["x1"]
                    and mx[1] > GRID["y0"] and mn[1] < GRID["y1"]):
                continue
            if float(mx[2]) < z_min:
                z_min, who = float(mx[2]), p
        depth = T["walk_z"] - z_min
        if depth >= HAZ_DEPTH:
            ok = False
        print(f"[selfcheck] (4) **격자 안 최저 상면** z = {z_min:+.4f} ({who}) → "
              f"보행면 대비 {depth:.4f} m {'<' if depth < HAZ_DEPTH else '≥'} "
              f"임계 {HAZ_DEPTH:.2f} m"
              + (f" · 여유 {HAZ_DEPTH - depth:.4f} m · OK ⇒ 발자국 구성상 0셀"
                 if depth < HAZ_DEPTH else " · **FAIL — ④-a 함정 아님**"))

        # (5) 단서 도달성 (§12-5 k 게이트의 사전 예측)
        v = _cue_visibility_mc(n=300, seed=31)
        print(f"[selfcheck] (5) 주 단서(점형블록 띠) 격자 도달성 MC 300포즈 — "
              f"포즈 비율 {v['band_frac']:.3f} · 프레임당 셀 {v['cells']:.2f}/20")

        print(f"[selfcheck] sceneN9 {'통과' if ok else '실패'}")
        return ok

    # -------------------------------------------------------------------
    # 조립
    # -------------------------------------------------------------------
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_terrain(M)                                   # ① 경로 (팔 불변)
    if cfg["hazard_platform_edge"]:                    # ② "위험" 축 — 분기 2줄
        build_platform_edge(M)
    else:
        build_flush_road(M)

    # ③ 단서 — **어느 것도 hazard 분기 안에 있지 않다** (프림 위생 1)
    if cfg["cue_tactile"]:
        build_tactile(M)
    if cfg["cue_railing"]:
        build_fence(M)
    if cfg["cue_nosing"]:
        build_nosing(M)
    if cfg["cue_sign"]:
        build_sign(M)
    if cfg["cue_bollard"]:
        build_bollards(M)
    if cfg["cue_road_marking"]:
        build_road_marking(M)
    if cfg["cue_manhole"] or cfg["cue_tree_grate"] or cfg["cue_slab_joint"] \
            or cfg["cue_drainage"]:
        build_ground_kit(M)
    if cfg["cue_shadow_caster"]:
        build_shadow_casters(M)
    if cfg["cue_scene_dressing"] or KEEP_DRESSING:
        # `KEEP_DRESSING` 은 hazard=False 팔에서 장식을 ON 변환 그대로 유지시킨다.
        #   이 씬의 장식은 전부 승강장·시설물대(z = 0.000)에 앵커되고 그 지면은
        #   **hazard 토글 밖**이므로 sceneC2 의 "하부 앵커 드레싱 소실 → ground_z
        #   이동" 사고가 구조적으로 불가능하다.
        build_dressing(M)

    if not scene_selfcheck():
        raise SystemExit("sceneN9 self-check 실패")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneN9 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["street_over"]
    look_from(_v0["eye"], _v0["tgt"])

    pt_spp = int(PARAMS["render"]["pt_total_spp"])

    def set_render_mode(mode):
        if mode == "PathTracing":
            settings.set("/rtx/pathtracing/spp", 1)
            settings.set("/rtx/pathtracing/totalSpp", pt_spp)
            settings.set("/rtx/pathtracing/optixDenoiser/enabled", True)
            settings.set("/rtx/pathtracing/maxBounces",
                         int(PARAMS["render"]["pt_max_bounces"]))
            settings.set("/rtx/rendermode", "PathTracing")
        else:
            settings.set("/rtx/rendermode", "RaytracedLighting")

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    if capture_mode:
        out_dir = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, build_views(), out_dir,
                            set_render_mode, look_from)
        simulation_app.close()
        return

    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    def on_key(event, *args):
        if event.type != carb.input.KeyboardEventType.KEY_PRESS:
            return True
        if event.input == K.P:
            cur = settings.get("/rtx/rendermode")
            if cur == "PathTracing":
                set_render_mode("RaytracedLighting")
                print("[렌더] RTX Real-Time (이동용)")
            else:
                set_render_mode("PathTracing")
                print(f"[렌더] PathTracing (totalSpp={pt_spp})")
        elif event.input == K.C:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN9_{ts}.png")
            capture(fp)
            print(f"[캡처] {fp}")
        elif event.input == K.LEFT_BRACKET:
            dome_user_rot[0] -= rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        elif event.input == K.RIGHT_BRACKET:
            dome_user_rot[0] += rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        return True

    keyboard_sub = input_iface.subscribe_to_keyboard_events(
        appwindow.get_keyboard(), on_key)

    print("=" * 64)
    print(BANNER)
    print("-" * 64)
    print("※ 키가 안 먹으면 Isaac Sim 창을 한 번 클릭해서 포커스를 줘!")
    print("=" * 64)

    while simulation_app.is_running():
        simulation_app.update()

    input_iface.unsubscribe_to_keyboard_events(
        appwindow.get_keyboard(), keyboard_sub)
    simulation_app.close()


# ===========================================================================
# CPU 자기검사 — pxr·GPU 없이 횡단면과 함정 회계를 재계산한다
# ===========================================================================
def _geometry_selfcheck():
    T, HZ = PARAMS["terrain"], PARAMS["hazard"]
    ok = True

    def chk(tag, cond, msg=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))

    print("=" * 70)
    print("sceneN9_busstop_tactile — CPU 자기검사 (pxr·GPU 불필요)")
    print("=" * 70)

    # ── ④-a 함정의 정의 — **가장 중요한 검사** ──────────────────────────────
    drop = T["walk_z"] - HZ["road_z"]
    chk("승강장 경계 표고차가 FA_REALITY §3 L6 밴드(0.15–0.25 m) 안",
        0.15 <= drop <= 0.25, f"{drop:.3f} m")
    chk("**표고차 < gridspec_v1 hazard_depth_m (④-a 함정 성립)**",
        drop < HAZ_DEPTH,
        f"{drop:.3f} < {HAZ_DEPTH:.2f} · 여유 {HAZ_DEPTH - drop:.3f} m "
        "⇒ 라벨러 발자국 `z_off − z_on ≥ 0.30` 이 한 셀도 켜지지 않는다")
    z_min, who = _grid_min_z()
    chk("**격자 안 최저 상면도 임계 미만** (해석적)",
        T["walk_z"] - z_min < HAZ_DEPTH,
        f"최저 {z_min:+.4f} ({who}) · 보행면 대비 {T['walk_z'] - z_min:.4f} m")
    chk("반사실 노면(고원식 정류장) = 승강장 레벨",
        abs(HZ["fill_z"] - T["walk_z"]) < 1e-9, f"{HZ['fill_z']:+.3f}")

    # ── D78 축방향 스텝 게이트 사각 — 이 씬에서는 발동하지 않는다 ────────────
    d_reach = -GRID["x0"] + math.sqrt(3.0) * abs(HZ["y_curb"])
    print(f"  [info] D78 축방향 사각 한계 d ≤ −x₀ + √3·|y_curb| = {d_reach:.2f} m "
          f"(base 밴드 상한 12.0 m). **발동하지 않는다** — 발자국이 스텝 게이트 "
          "이전에 이미 비어 있다(`cells_raw = 0`, 카메라 무관량).")

    # ── 횡단면 연속성 · void ────────────────────────────────────────────────
    segs = [(-T["y_far"], T["curb"]["y0"]),
            (T["curb"]["y0"], T["curb"]["y1"]),
            (T["setback"]["y0"], T["setback"]["y1"]),
            (T["tactile_band"]["y0"], T["tactile_band"]["y1"]),
            (T["platform"]["y0"], T["platform"]["y1"]),
            (-T["walk"]["y_half"], T["walk"]["y_half"]),
            (T["furnish"]["y0"], T["furnish"]["y1"]),
            (T["frontage"]["y0"], T["y_far"])]
    cover_hi, gap = -T["y_far"], []
    for a, b in sorted(segs):
        if a > cover_hi + 1e-6:
            gap.append((round(cover_hi, 3), round(a, 3)))
        cover_hi = max(cover_hi, b)
    chk("VG-void 횡단면 커버리지 (개방 바닥 0)", not gap and cover_hi >= T["y_far"],
        f"공백 {gap}" if gap else "커버리지 1.0")

    # ── 단서 배치 규율 ──────────────────────────────────────────────────────
    tb, c, sb = T["tactile_band"], T["curb"], T["setback"]
    tw = PARAMS["tactile"]["warn"]
    tg = PARAMS["tactile"]["guide"]
    chk("**점형(경고) 밴드는 정확히 1개** [D82 ⓐ 위험 경계 전 점형 1밴드]",
        isinstance(tw, tuple) and len(tw) == 4, "warn 1밴드 · guide 는 선형이라 별도")
    chk("점형 밴드 깊이 ≥ 0.60 m [별표1 버목 3) 승강장 · ADA §705.2 610 mm]",
        tw[3] - tw[1] >= 0.60 - 1e-9, f"{tw[3] - tw[1]:.2f} m")
    chk("점형 밴드가 연석 배면에서 **0.30 m 이격** [별표1 위험 지점 0.3 m 앞]",
        abs((tw[1] - c["y1"]) - 0.30) < 1e-6,
        f"이격 {tw[1] - c['y1']:.2f} m")
    chk("**선형(유도)은 점형과 다른 기하** — 바탕판 + 평행 돌출선 [D82 ⓐ 역할 구분]",
        PARAMS["tactile"]["guide_bar_w"] > 0
        and PARAMS["tactile"]["guide_bar_pitch"] > 0,
        f"유닛 0.30 m 당 {round(0.30 / PARAMS['tactile']['guide_bar_pitch'])}줄 · "
        f"돌출 {PARAMS['tactile']['guide_proud'] * 1000:.0f} mm")
    chk("선형 유도로가 보도 유효폭 ↔ 점형 밴드를 잇는다 (유도의 실제 역할)",
        abs(tg[1] - tw[3]) < 1e-6 and abs(tg[3] + T["walk"]["y_half"]) < 1e-6,
        f"유도로 y [{tg[1]:+.2f}, {tg[3]:+.2f}] · 점형 y1 {tw[3]:+.2f} · "
        f"보도 가장자리 {-T['walk']['y_half']:+.2f}")
    a_w = (tw[2] - tw[0]) * (tw[3] - tw[1])
    a_g = (tg[2] - tg[0]) * (tg[3] - tg[1])
    chk("**cue-extent — 점자블록 총면적이 위험 씬 밴드 안** [D82 ⓒ 밀도 대칭]",
        1.0 <= a_w + a_g <= 9.0,
        f"점형 {a_w:.2f} + 선형 {a_g:.2f} = **{a_w + a_g:.2f} m²** vs "
        "위험 씬 실측 H3 1.08 · H7 1.28 · L1 4.08 · H2 7.20 · H1 8.72 m²")
    f = PARAMS["fence"]
    chk("방호울타리가 점형블록 띠(및 그 판석 바탕)를 침범하지 않는다",
        f["y"] + f["post_r"] < tb["y0"] and f["y"] - f["post_r"] > c["y1"],
        f"울타리 y {f['y']:+.3f} ± {f['post_r']:.3f} ⊂ 연석배면 "
        f"[{sb['y0']:+.2f}, {sb['y1']:+.2f}]")
    chk("정류장 구간이 울타리로 막히지 않는다 (승하차 동선)",
        f["spans"][1][0] - f["spans"][0][1] >= 8.0,
        f"개방 {f['spans'][1][0] - f['spans'][0][1]:.2f} m ⊇ 승하차 구간 "
        f"(점형 {tw[0]:+.2f}…{tw[2]:+.2f} · 쉘터 "
        f"{PARAMS['shelter']['x0']:+.2f}…{PARAMS['shelter']['x1']:+.2f})")
    b = PARAMS["bollard"]
    pitches = [round(b["xs"][i + 1] - b["xs"][i], 4) for i in range(len(b["xs"]) - 1)]
    chk("볼라드 피치 1.50 m 법정치 [행안부 볼라드 설치기준]",
        all(abs(p - 1.50) < 1e-6 for p in pitches), f"{pitches}")
    chk("볼라드 h 0.80–1.00 · φ 0.10–0.20",
        0.80 <= b["h"] <= 1.00 and 0.10 <= 2 * b["r"] <= 0.20,
        f"h {b['h']} · φ {2 * b['r']:.2f}")
    chk("볼라드 열과 울타리 구간이 x 로 겹치지 않는다 (같은 y = 연석 배면)",
        all(not (a <= x <= c) for x in b["xs"] for a, c in f["spans"]),
        f"볼라드 x {b['xs'][0]:+.2f}…{b['xs'][-1]:+.2f} · 울타리 구간 {f['spans']}")
    chk("**볼라드가 정류장 승하차 구간을 비켜선다**",
        min(b["xs"]) > PARAMS["shelter"]["x1"] + 0.3,
        f"볼라드 서단 {min(b['xs']):+.2f} > 쉘터 동단 "
        f"{PARAMS['shelter']['x1']:+.2f} + 0.3")
    # 이 씬의 볼라드 열은 **보차도 경계와 나란한 종방향 열**이라 보행 동선을 가로막지
    #   않는다 ⇒ **「보행안전 및 편의증진에 관한 법률 시행규칙」 별표1 제10호 바**
    #   ("말뚝 앞 0.3 m 점형블록")는 **적용되지 않는다**.
    #   [정정 2026-08-24 · REG_AUDIT §2.7 N9/N11-C] 구 표기 "교통약자법 시행규칙 별표2
    #     제7호"는 **삭제·이관**된 조문이다 — 현행 근거는 위 보행안전법 별표1 제10호이고
    #     **수치는 전부 동일**(문구만 "전면 → 앞쪽")하다. 판정은 바뀌지 않는다.
    #   (횡단 배치는 sceneN11 이고 그 씬은 점형블록을 둔다.) D82 부가 지침
    #   *"규정 미적용 시점에 규정 시설물을 억지로 두지 말 것"* 의 이행이다.
    chk("볼라드 열이 보행 동선과 **나란하다** ⇒ 보행안전법 별표1 10호 바 점형블록 미적용",
        abs(b["y"] + 3.87) < 1e-9 and len(set(b["xs"])) == len(b["xs"]),
        f"열 방향 = x (보행축과 나란) · y {b['y']:+.2f} 고정")
    chk("**표지주가 점형블록 띠를 침범하지 않는다** (S37 오설치 유형 회피)",
        not (tb["y0"] <= PARAMS["sign"]["y"] <= tb["y1"]),
        f"표지 y {PARAMS['sign']['y']:+.2f} ∉ 점형블록 띠 "
        f"[{tb['y0']:+.2f}, {tb['y1']:+.2f}]")
    chk("**표지주·볼라드가 카메라 전방(x > −1.15)** — R0 의 '켜져 있으나 화면에 없는 단서' 수리",
        PARAMS["sign"]["x"] > DATUM_STRIP["x1"] and min(b["xs"]) > DATUM_STRIP["x1"],
        f"표지 x {PARAMS['sign']['x']:+.2f} · 볼라드 서단 {min(b['xs']):+.2f} > "
        f"데이텀 스트립 동단 {DATUM_STRIP['x1']:+.2f}")
    sh = PARAMS["shelter"]
    chk("쉘터가 승강장 안 (보도 유효폭·점형블록 침범 0)",
        sh["y0"] >= T["platform"]["y0"] - 1e-9
        and sh["y1"] <= T["platform"]["y1"] + 1e-9,
        f"쉘터 y [{sh['y0']:+.2f}, {sh['y1']:+.2f}] ⊂ 승강장 "
        f"[{T['platform']['y0']:+.2f}, {T['platform']['y1']:+.2f}]")
    chk("쉘터 유효높이 ≥ 2.30 m [승차대 표준]", sh["roof_z"] >= 2.30,
        f"{sh['roof_z']:.2f} m")
    tr = PARAMS["shadow"]["trees"]
    tpit = [round(tr[i + 1][0] - tr[i][0], 4) for i in range(len(tr) - 1)]
    chk("가로수 피치 6~8 m 법정 밴드 [조례 제7조1가]",
        all(6.0 <= p <= 8.0 for p in tpit), f"{tpit}")
    # **수관 overhang 은 허용한다** (파일 상단 프림 위생 5) — 상방 이동은 최저점 회계를
    #   오염시키지 않고, 보도 위로 뻗는 수관이 곧 `cue_shadow_caster` 의 그림자 밴드다.
    #   규율은 **줄기 위치**에만 건다.
    fu = T["furnish"]
    chk("가로수 줄기가 시설물대 안 (보도 유효폭·승강장 침범 0)",
        all(fu["y0"] + 0.5 <= ty <= fu["y1"] - 0.5 for _tx, ty in tr),
        f"가로수 y {[ty for _tx, ty in tr]} ⊂ 시설물대 "
        f"[{fu['y0']:+.2f}, {fu['y1']:+.2f}] (±0.5 여유)")
    # **보도 유효폭 규정을 씬이 직접 강제한다** (LINT-5 미선언의 대체 검사).
    #   [규격 「도로의 구조·시설 기준에 관한 규칙」 제16조 — 보도 유효폭 최소 2.0 m]
    yh = T["walk"]["y_half"]
    sg = PARAMS["sign"]
    occupants = ([("가로수", ty) for _tx, ty in tr]
                 + [("가로등", ly) for _lx, ly in PARAMS["shadow"]["lamps"]]
                 + [("볼라드", b["y"])] + [("방호울타리", f["y"])]
                 + [("표지주", sg["y"])] + [("쉘터", sh["y0"]), ("쉘터", sh["y1"])]
                 + [("벤치", by) for _bx, by, _yw in PARAMS["dress"]["benches"]]
                 + [("점형블록", tw[1]), ("점형블록", tw[3])]
                 + [("선형유도", tg[1])])
    intruders = [(nm, yy) for nm, yy in occupants if abs(yy) < yh]
    chk(f"**보도 유효폭 {2 * yh:.2f} m 위 수직 부재 0건** "
        "[「도로의 구조·시설 기준에 관한 규칙」 §16 — 최소 2.0 m]",
        not intruders, f"침범 {intruders}" if intruders
        else f"전 {len(occupants)}개 부재가 |y| ≥ {yh:.2f} 밖 (LINT-5 미선언의 대체 검사)")

    gt_side = 1.44
    chk("수목보호격자가 시설물대 안",
        all(fu["y0"] <= gy - gt_side / 2 and gy + gt_side / 2 <= fu["y1"]
            for _gx, gy in PARAMS["gkit"]["tree_grates"]),
        f"격자 반폭 {gt_side / 2:.2f} · 시설물대 폭 {fu['y1'] - fu['y0']:.2f} m")

    # ── 데이텀 ──────────────────────────────────────────────────────────────
    ds = DATUM_STRIP
    cross = [z for z in GATED_ZONES
             if not (z[3] <= ds["x0"] or z[2] >= ds["x1"]
                     or z[5] <= ds["y0"] or z[4] >= ds["y1"])]
    dfail = [(z[0], z[6]) for z in cross if z[6] > DATUM_TOL]
    dtol = [(z[0], z[6]) for z in cross if z[6] <= DATUM_TOL]
    chk("VG-datum 선언 검사 (datum_fail 0)", not dfail,
        f"datum_tol {dtol} · datum_fail {dfail}")

    # ── 단서 도달성 — §12-5 k 게이트의 사전 예측 ────────────────────────────
    v = _cue_visibility_mc(n=900, seed=29)
    print(f"  [info] 주 단서(점형블록 띠 {v['n_pts']}표본점) 격자 도달성 MC 900포즈 "
          f"— 포즈 비율 **{v['band_frac']:.3f}** · 프레임당 격자 셀 "
          f"{v['cells']:.2f}/20")
    chk("주 단서가 base 밴드 과반 포즈에서 폴라 격자 안에 있다",
        v["band_frac"] >= 0.50,
        f"{v['band_frac']:.3f} ≥ 0.50 (렌더 후 strict 세그 cue 픽셀 수가 실측한다)")

    # ── 표준 장비 ───────────────────────────────────────────────────────────
    chk("표준 장비 16키", len(SCENE_CONFIG) == 16, f"{len(SCENE_CONFIG)}키")
    declared = set(CUE_CLASS) - {"_structural"}
    cue_keys = {k for k in SCENE_CONFIG if k.startswith("cue_")}
    chk("CUE_CLASS 가 모든 cue_* 를 분류", declared == cue_keys,
        f"미분류 {sorted(cue_keys - declared)} · 초과 {sorted(declared - cue_keys)}")
    chk("hazard_* 키가 정확히 1개", len([k for k in SCENE_CONFIG
                                         if k.startswith("hazard_")]) == 1)

    print(f"\n  ⇒ sceneN9 CPU 자기검사 {'통과' if ok else '실패'}")
    print("=" * 70)
    return ok


if __name__ == "__main__":
    main()
