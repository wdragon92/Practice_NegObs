# -*- coding: utf-8 -*-
"""
sceneN11_ground_pattern.py — NegObs 신규 씬 N11: **지면 문양 삼중주**
                             (④-a 함정 표본 · Isaac Sim 4.5)

계열    : **N-cue (단서 有 · 위험 無)** · 생활권 = **보도**
사다리  : **FA_REALITY §3 L10** — *"지면 문양 삼중주 — 평탄 보도에 맨홀 + flush 수목격자 +
          신축이음이 한 화면에. 셋 다 **단차 0** 인데 셋 다 '어두운 폐영역/평행 밴드'라는
          **낙차의 저역 신호 문법**을 갖는다. **인공 부재 없이 지면 문양만으로** 만든 N-cue"*
          난이도 **★★★★☆ (★4)**
정본    : `experiments/v3_0823/RENDER_PLAN_V3.md` §2.0(공통 표준) · §2.4 표
          `sceneN11_ground_pattern` · §2.6(CUE_CLASS) · §3.1–3.2(test-ext 사양)
분리    : **test-ext** — v2·v3 **양 모델 모두 미학습**. 훈련·검증에 절대 넣지 않는다(§3.1).
          **4팔 전부 제작 의무**(DZ §4.2 `:243`) — A·B·C·D 완비.
밴드    : base · base2 (둘 다 기본 `CAM_DIST` 지지집합 · 시드만 다른 2차 draw)
          씬당 팔당 48컷 · 4팔 합 192

════════════════════════════════════════════════════════════════════════════
**이 씬이 존재하는 이유** — 갭 지도 1·2·5위를 한 씬에 착지시킨다

계획 §2.4: *"맨홀은 **빌더가 이미 있고 에셋만 없다**(갭 25.0, 1위), 수목보호격자는
전무(20.0, 2위), 줄눈/신축이음은 빌더 존재·키 미승격(15.0, 5위). N11 은 이 셋을 한 씬에
착지시키는 **최대 ROI 작업**"*.

지름길 모델의 오답(계획 §2.4): *"원반·격자·직선을 각각 개구부/그레이팅/계단코로 오독 →
**한 프레임에 서로 다른 세 종류 FA** 가 동시 발생(가족 분해에 최적)"*.

  | 문양 | FA 가족 (FA_REALITY §1.3) | 이 씬의 프림 |
  |---|---|---|
  | **어두운 원반** | C1 맨홀 뚜껑 — 포트홀 검출기의 대표 오탐원 | `GKitPlaza/…/Manhole_*` × 3 |
  | **어두운 정사각 격자** | C3 수목보호 격자(flush) | `TreeGrate_*` × 3 |
  | **규칙적 직선** | C4 수축줄눈·신축이음 (6 m / 12 m 리듬) | `GKitPlaza/…/joint*` + `Joint/Exp_*` |
  | (보너스) **어두운 평행선 밴드** | C2 트렌치 커버 | `GKitPlaza/…/Trench` |
  | (보너스) **수직 백색 밴드** | C6 노면표시 | `Marking/*` |

D58 ③ 이 이 씬에 거는 요구 — *"함정의 무죄가 눈으로 읽혀야 한다"* — 의 이 씬 판본은
**"보행자전용도로(차없는 거리)로 읽혀야 한다"** 이다. 상가 전면 공지·가로수·벤치·
진입 볼라드·법정 규제표지가 있어야 이 지면 문양들이 *"평탄한 도심 보행로의 일상 설비"*
로 읽히고, 그것이 없으면 그냥 "구멍처럼 생긴 것들이 널린 바닥"이 되어 함정으로 성립하지
않는다. FA_REALITY §4 P6 이 요구한 프레이밍(*"인공 **부재**를 프레임에서 배제하고 지면
문양만"*)은 **보행로 위**에 대한 요구이고, 맥락(가로수·상가)까지 지우라는 뜻이 아니다 —
그래서 이 씬은 보행로 유효폭 8.40 m 안에는 **수직 부재를 한 개도 세우지 않는다**.

════════════════════════════════════════════════════════════════════════════
**팔 사상 (계획 §1.0 — 팔의 이름은 레시피, 판정은 사실)**

`hazard_planting_bed` 는 **연속 식재대의 토양면 높이**를 토글한다:

  · True  → 토양면 z = **−0.150** (관수·통기를 위해 포장면보다 낮춘 표준 식재대)
  · False → 같은 자리가 화강석 판석으로 flush 채워진다(반사실 보행 가능면 z_off = 0.000)

표고차 **0.150 m** 는 `gridspec_v1.hazard_depth_m = 0.30` 미만이므로 라벨러 발자국
(`z_off − z_on ≥ 0.30`)이 **한 셀도 켜지지 않는다**(`cells_raw = 0`).

  | 렌더 레시피 팔 | `hazard_planting_bed` | `cue_*` | **사실 판정** |
  |---|---|---|---|
  | A | True  | 전부 ON  | **C (단서 有·위험 無)** |
  | B | True  | 전부 OFF | **D (단서 無·위험 無)** |
  | C | False | ON 유지(`keep_dressing`) | **C** |
  | D | False | 전부 OFF | **D** |

⇒ **네 팔 전부 GT 올-음성.** 계기판 ③(용량-반응)의 대조는 **단서 축 (C,D)** 다.

**왜 식재대인가 (FA_REALITY §2 9위 동시 착지)**: 갭 지도 9위가
*"**얕은 함몰(깊이 0.05–0.25 m) 무위험 씬**을 깊은 낙차와 페어로 — D팔 최상급 재료"* 를
요구한다. 이 씬의 식재대가 정확히 그 표본이고, **격자 안에 실측 가능한 0.150 m 함몰이
있는데 GT 가 전부 음성**이라는 상태가 ④-a 함정의 가장 강한 형태다.
`hazard_*` 토글이 완전히 공허하면(A ≡ C 바이트 동일) "재 봤더니 임계 미만"이라는
**기계 증거 자체가 생기지 않는다** — 그래서 일부러 잴 것을 둔다.

**식재 여백 규칙**: 높이맵은 수직 레이의 최초 히트이므로 관목이 덮은 셀은 z 가 관목
상면이 되어 함몰을 **가린다**. 관목을 식재대 폭 전체에 깔면 위 증거가 사라지므로,
식재대 양 가장자리에 **맨흙 여백 0.30 m 씩**을 남긴다(실제 식재대도 경계석 안쪽
0.2–0.4 m 는 비어 있다). 그 여백이 라벨러가 0.150 m 를 실측하는 창이다.

════════════════════════════════════════════════════════════════════════════
씬 조립 공식 (4요소 — 브리프 §2.0)
  ① 경로   **보행자전용도로**(차없는 거리) 유효폭 **8.40 m** · 콘크리트 타설 포장 z 0.000
  ② 위험   **없다.** 유일한 표고차는 **식재대 −0.150 m** 이고 임계 0.30 m 미만이다.
  ③ 단서   **맨홀 3 · flush 수목보호격자 3 · 수축줄눈 + 신축이음 · 트렌치 커버 ·
           빗물받이 · 노면표시** (지면 문양 6종) + 진입 볼라드 · 점형블록 ·
           규제표지 · 가로수 그림자 · 벤치 · 관목 식재대
  ④ 은닉   **없다.** 은닉할 낙차가 없다. 가림체 프림 0개.

────────────────────────────────────────────────────────────────────────────
좌표계 · 횡단면 (walk axis = +X, Z-up, m. 카메라는 x = −d, |y| ≤ 0.90 에서 +X 를 본다)

   y
  +40.0 ┌──────────────────────────────────────────────────────┐
        │  북측 상가 건물동 (원경 · 높이맵 격자 |y| ≤ 8 **밖**) │  Dress/Shop
  +8.60 ├──────────────────────────────────────────────────────┤
        │  북측 상가 전면 공지 (화강석 판석)     z = 0.000      │  Ground/FrontN
  +6.00 ├──────────────────────────────────────────────────────┤
  +5.88 │  식재대 경계석 (화강석) 상면 z = 0.000 · 폭 0.12      │  Ground/BedKerbN
        │  **② 연속 식재대** 토양면 z = **−0.150** (관목 + 여백)│  Bed  ← 유일한 표고차
  +4.32 │  ← 맨흙 여백 0.30 · 관목 0.96 · 맨흙 여백 0.30 →     │
  +4.20 ├──────────────────────────────────────────────────────┤  Ground/BedKerbS
        │                                                       │
   0.00 │  ① 보행자전용도로 유효폭 8.40 (콘크리트 타설)         │  Ground/Mall
        │     **맨홀 3 · 수축줄눈 · 신축이음 · 트렌치 · 노면표시**│      z = 0.000
        │     **수직 부재 0개** (FA_REALITY §4 P6 프레이밍)     │
  −4.20 ├──────────────────────────────────────────────────────┤
        │  남측 시설물대 1.80 — **flush 수목보호격자 3 + 가로수**│  Ground/Furnish
  −6.00 ├──────────────────────────────────────────────────────┤
        │  남측 상가 전면 공지 (화강석 판석)     z = 0.000      │  Ground/FrontS
  −8.60 ├──────────────────────────────────────────────────────┤
        │  남측 상가 건물동 (원경 · 격자 밖)                    │  Dress/Shop
  −40.0 └──────────────────────────────────────────────────────┘

  종단(보행축): **전 구간 z = 0.000 · 계단 0단 · 경사 0**.

  **표고차 = 0.000 − (−0.150) = 0.150 m < 0.300 m (gridspec_v1 hazard_depth_m)**
  ⇒ 발자국 `cells_raw = 0` · `polar_gt` 올-제로 · tier `none_in_fov` (전 팔·전 프레임)

────────────────────────────────────────────────────────────────────────────
**격자 안 최저점 회계** — 이 씬이 인쇄해야 하는 수치

  | 요소 | 최저 z | 보행면 대비 | 임계 0.30 대비 |
  |---|---|---|---|
  | 식재대 토양면 (hazard ON · 맨흙 여백) | −0.150 | **0.150 m** | −0.150 (여유) |
  | 트렌치 커버 (flush · seat 2 mm) | −0.002 | 0.002 m | — |
  | 빗물받이 그레이팅 (flush) | −0.008 | 0.008 m | — |
  | 수축줄눈 recess | −0.003 | 0.003 m | — |
  | 그 밖 전부 | 0.000 | 0 | — |

⇒ **격자 안 어디에도 0.30 m 이상의 하강이 없다.** 이것이 ④-a 함정의 정의다.
   그리고 **맨홀·수목격자·신축이음은 셋 다 단차 0** 이다 — 이 씬의 주 단서 세 개는
   *"낙차처럼 보이지만 기하학적으로 완전히 평평하다"* 는 상태 그 자체다.

────────────────────────────────────────────────────────────────────────────
**D78 측방 사각과의 관계** (SCENE_TEXT_BUILD §12-9.3)

식재대 경계선(y = +4.20 / +6.00)은 보행축과 나란한 축방향 선이고, 라벨러 `step_gate` 의
8이웃 양자화 한계는 `d ≤ −x₀ + √3·y_lip = 2 + √3 × 4.32 = 9.48 m` 다.
**그러나 그 사각은 이 씬에서 발동하지 않는다** — 발자국이 스텝 게이트 **이전에** 이미
비어 있기 때문이다(`cells_raw` 는 카메라 무관량이고 0 이다). 게이트 배터리는
`cells_kept` 이 아니라 **`cells_raw`** 를 판정 근거로 인쇄한다.

────────────────────────────────────────────────────────────────────────────
프림 위생 · 데이텀 (CUE_COVERAGE §4-4 (2)(3)(4))

1. 단서 빌더가 `if cfg["hazard_*"]` 안에 있는 것은 **0개**. 조립부 hazard 분기는 2줄뿐이다.
2. **식재대 경계석 상면 = 보행면 = 반사실 채움면 = 0.000** 이므로 경계석은 **팔 불변
   지형**(`Ground/BedKerb*`)으로 짓는다. hazard 토글은 **경계석 안쪽 토양면만** 움직인다.
3. 카메라 데이텀 스트립 `x ∈ [−12.05, −1.15] · |y| ≤ 0.95` 안에서 상면을 움직이는 토글
   프림은 줄눈(recess 3 mm)·신축이음(proud 2 mm)·맨홀(≤ 10 mm)·트렌치/빗물받이(flush)
   ·노면표시(3 mm) 뿐 — 전부 `datum_tol`(≤ 0.02 m).
   **가로수 수관은 |y| ≤ −4.2 쪽에만 있고 스트립(|y| ≤ 0.95)에 닿지 않는다** —
   `AabbPrefilter.ground_z` 는 상공 60 m 하향 레이의 최초 히트이고 식생을 제외하지 않으므로
   (`variation_kit.py:781-785`), 수관이 스트립을 덮으면 `cam.ground_z` 가 수관 top 이 되어
   **팔마다 카메라가 다른 높이에 놓인다**(VG-datum·VG-10 동시 파괴).
4. **void 커버리지 1.0** — 상가 전면 공지·시설물대·보행로·경계석·식재대가
   x ∈ [−2, 14] × y ∈ [−8, 8] 을 빈틈없이 덮는다. 개방 바닥 0.
5. **보행로 유효폭 위에 수직 부재 0개** — 볼라드·표지·벤치는 전부 x ≤ −8 진입부이거나
   시설물대다. 이것이 L10 의 성립 조건(*"인공 부재 없이 지면 문양만으로"*)이다.

표준법: 법1 온전 상태만(포장 균열·잡초·패치 데칼 전부 OFF — N-cue 는 "온전한 시설만"이
성립 조건이다) · 법2 법정 제식 표지 1매 · 법4 기능 필수성(볼라드·점형블록·배수는 법정) ·
법5 차량·계절소품 0 · 법6 신규 재질 역할 0 · 법7 `cue_*` 최대 융기 10 mm · 법8 근거 태그.

실행
    unset PYTHONPATH VIRTUAL_ENV; conda activate env_isaaclab; export PYTHONNOUSERSITE=1
    python scenes/main/sceneN11_ground_pattern.py                 # GUI 룩체크
    NEGOBS_SMOKE=1 python scenes/main/sceneN11_ground_pattern.py  # CPU 조립 스모크
데이터 렌더 진입점:
    python experiments/v3_0823/code/h67_probe.py --scene sceneN11 --run <stamp> ...
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk


# [계획 §2.0] 생활권 = 보도. 계절은 **초가을** — 같은 생활권의 sceneN9(초여름)·
#   sceneH3(늦봄)과 톤을 분리한다(§3.2 "부지·드레싱을 겹치지 않게").
SEASON = "early_autumn"


# ===========================================================================
# [A0] CUE_CLASS — 렌더 **전** 사전 분류 (RENDER_PLAN_V3 §2.6 / ACCOUNTING §2-6)
# ===========================================================================
CUE_CLASS = {
    "cue_railing":         "decorative",   # 기본 OFF — 보행자전용도로에 방호울타리 없음
    # [D82 ⓐ 근거 조항] 「**보행안전 및 편의증진에 관한 법률** 시행규칙」
    #   **별표1 제10호 바** — 자동차 진입억제용 말뚝 **앞 0.3 m** 에 점형블록.
    #   **점형 = 경고 1밴드**이고 이 씬에는 유도가 필요한 분기·대기 지점이 없어
    #   **선형블록은 두지 않는다**.
    #
    # ── [문서 정정 · 2026-08-24 · REG_AUDIT 전달 3건 반영] ──────────────────────
    #  (1) **별표 번호 오표기 정정** (REG_AUDIT §2.7 N9/N11-C · §3 C-5).
    #      구 표기는 「교통약자의 이동편의증진법 시행규칙」 **별표2 제7호**였다. 그 조문은
    #      **삭제되어 이관**됐고 현행 근거는 위 보행안전법 시행규칙 **별표1 제10호**다
    #      (**수치는 전부 동일**, 문구만 "전면 → 앞쪽"). 별표 번호는 이렇게 갈린다:
    #        · 교통약자법 시행규칙 **별표1** = 「이동편의시설의 구조·재질 등에 관한
    #          세부기준」 = **점자블록 정본**
    #        · 동 **별표2** = 「보행안전시설물의 구조 시설기준」(볼라드) — **삭제·이관**
    #        · 보행안전법 시행규칙 **별표1 제10호** = **볼라드 현행 정본**(같은 호 **바**가
    #          "말뚝 앞 0.3 m 점형블록")
    #      ⇒ 이 씬은 **볼라드 전면 점형**이므로 근거는 보행안전법 별표1 제10호 바이고,
    #      점형블록의 **치수·재질·색상** 근거는 교통약자법 시행규칙 **별표1**(§2.5 KS 급
    #      치수)이다. **기하 변경 없음 — 인용 문자열만 정정.**
    #
    #  (2) **점형 세로폭 0.30 m — N9(0.60)과 갈리는 지점** (REG_AUDIT §2.7 N11-1).
    #      이 밴드는 보행자가 **정면으로 마주치는** 접근선 위에 놓인다. 지침 6.6.7 가는
    #      *"위험물과 **마주치는 방향**에는 **60 cm**, 동선과 **평행한 측방**에는 30 cm"*
    #      로 갈라 쓰므로, 이 케이스의 **표준값은 60 cm**다. 현재 0.30 m 는 허용 범위
    #      (30~90 cm) 안이라 **위반은 아니지만 표준 미달**이고, 형제 씬
    #      `sceneN9_busstop_tactile` 이 같은 정면 케이스에서 **0.60 m** 를 쓰므로
    #      **코퍼스 안에서 두 씬이 갈린다**.
    #      **처분: 기록만.** 통일하려면 밴드 세로폭이라는 **기하**를 바꿔야 하고
    #      (0.30 → 0.60 ⇒ 점형 면적 2.52 → 5.04 m², D82 ⓒ 밀도 대칭 재계산 필요),
    #      그것은 문서 정정의 범위 밖이다 ⇒ **사용자 판단 항목으로 열어 둔다**.
    #      감사 판정은 "재렌더 불요"이므로 현 상태로 본렌더에 들어가도 된다.
    #
    #  (3) 선형블록 세로폭 판독 건(REG_AUDIT §2.7 N9-3)은 **이 씬과 무관**하다 —
    #      여기에는 선형블록이 0개다(위 "선형블록은 두지 않는다"). N9 쪽에 기록했다.
    "cue_tactile":         "decorative",   # 진입 볼라드 전면 점형 1밴드 (0.30 m 이격)
    "cue_nosing":          "decorative",   # 기본 OFF — 평탄 보행로에 계단코 없음(법4)
    "cue_material_break":  "decorative",   # **재질 재바인딩 전용** — 프림 집합 불변
    "cue_sign":            "decorative",   # 보행자전용도로 규제표지 1매 (법정 제식)
    "cue_scene_dressing":  "decorative",   # 벤치·관목 식재·원경 상가
    "cue_shadow_caster":   "decorative",   # 시설물대 가로수 + 가로등주
    "cue_manhole":         "decorative",   # **삼중주 ① 어두운 원반** (갭 1위)
    "cue_tree_grate":      "decorative",   # **삼중주 ② 어두운 정사각 격자** (갭 2위)
    "cue_slab_joint":      "decorative",   # **삼중주 ③ 규칙적 직선** (갭 5위)
    "cue_drainage":        "decorative",   # 트렌치 커버 + 빗물받이 (갭 3위 · C2 평행선)
    "cue_bollard":         "decorative",   # 진입부 차량 진입 억제 볼라드
    "cue_road_marking":    "decorative",   # 구간 시·종점 횡단 밴드 (갭 6위 · C6)
    # ── 토글 금지 목록 (팔 불변 지형) ────────────────────────────────────────
    "_structural":         ["Ground/Mall", "Ground/Furnish", "Ground/FrontN",
                            "Ground/FrontS", "Ground/BedKerbN", "Ground/BedKerbS"],
}


# ===========================================================================
# [A] SCENE_CONFIG — **표준 장비 16키** (RENDER_PLAN_V3 §2.0 · CUE_COVERAGE §4-4 (1))
# ===========================================================================
SCENE_CONFIG = {
    # ── ② "위험" 축: 유일한 기하 토글. **낙차가 아니라 함정을 짓는다**(계획 §1.0) ──
    #   True  → 식재대 토양면 −0.150 (표준 식재대: 관수·통기를 위해 포장면 아래로)
    #   False → 같은 자리를 화강석 판석으로 flush 채움 (반사실 보행 가능면 0.000)
    #   FA_REALITY §2 9위 "얕은 함몰(0.05–0.25 m) 무위험 씬" 을 동시에 착지시킨다.
    "hazard_planting_bed": True,
    # ── ③ 단서: 공통 6키 ────────────────────────────────────────────────────
    # 보행자전용도로에는 차량방호·보행자방호 울타리를 두지 않는다(차량이 없다).
    #   법4 "비움이 기본값" → 기본 OFF, 코드 경로는 상시 보유(어블레이션용).
    "cue_railing":         False,
    "cue_tactile":         True,   # 진입 볼라드 전면 점형블록 [보행안전법 시행규칙 별표1 10호 바]
    "cue_nosing":          False,  # 평탄 — 대상 계단 없음(법4). Key reserved only.
    "cue_material_break":  True,   # 보행로 = 콘크리트 타설 / 공지·시설물대 = 화강석 판석
    "cue_sign":            True,   # 보행자전용도로 규제표지 (법2 — 법정 제식만)
    "cue_scene_dressing":  True,   # 벤치·관목 식재·원경 상가
    # ── v3 신설 3키 (FA_REALITY §2) — **이 씬의 주 단서 2개가 여기 있다** ─────
    "cue_shadow_caster":   True,   # 갭 4위 — 양성·음성 동일 비율(§2.0 역지름길 경보)
    "cue_manhole":         True,   # **갭 1위 (25.0) — 삼중주 ①**
    "cue_tree_grate":      True,   # **갭 2위 (20.0) — 삼중주 ②**
    # ── FA_REALITY §2 승격 후보 4키 ────────────────────────────────────────
    "cue_slab_joint":      True,   # **갭 5위 (15.0) — 삼중주 ③ 수축줄눈 + 신축이음**
    "cue_drainage":        True,   # 갭 3위 — 트렌치 커버 + 빗물받이 (C2 평행선 밴드)
    "cue_bollard":         True,   # L2 — 보행자전용도로 진입부 차량 억제
    "cue_road_marking":    True,   # 갭 6위 키 승격 — 구간 시·종점 횡단 밴드 (C6)
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
        # 보행자전용도로 유효폭 8.40 m [규격 「보행안전 및 편의증진에 관한 법률」
        #   보행자전용길 유효폭 최소 2.0 m · 상업지구 차없는 거리 실측 6~12 m 밴드]
        mall=dict(y_half=4.20),
        # 남측 시설물대 1.80 m — 수목보호격자 + 가로수
        furnish=dict(y0=-6.00, y1=-4.20),
        front_s=dict(y0=-8.60, y1=-6.00),
        front_n=dict(y0=6.00, y1=8.60),
        # 식재대 경계석 (팔 불변 · 상면 = 보행면)
        bed_kerb=dict(w=0.12, y0=4.20, y1=6.00),
    ),
    # ── ② "위험" 축 (hazard_planting_bed 전속) — 연속 식재대 ─────────────────
    hazard=dict(
        y0=4.32, y1=5.88,          # 경계석 안쪽 토양 구간 (폭 1.56 m)
        soil_z=-0.150,             # **핵심 수치**: 토양면. |0.150| < 0.300 임계
        soil_bot=-0.62,            # 토양층 하부 (VG-void — 실제 바닥 프림)
        fill_z=0.0,                # hazard=False 반사실 판석 채움면
        x0=-13.00, x1=34.00,       # 식재대 종단 구간
        # [computed] 표고차 = 0.000 − (−0.150) = **0.150 m** · 임계 여유 0.150 m
        # [규격] 표준 식재대 토양면은 포장면보다 0.05~0.15 m 낮게 조성한다
        #        (관수·통기 · 토양 유실 방지). FA_REALITY §2 9위 "얕은 함몰" 밴드와 동일.
    ),
    # ── ③ 단서 파라미터 ─────────────────────────────────────────────────────
    # (a) 삼중주 ③-b **신축이음** — 12 m 리듬. 실링재 밴드 폭 0.025 · proud 2 mm.
    #     [규격 콘크리트 포장 신축이음 12~20 m · 수축줄눈 3~6 m — FA_REALITY §1.3 C4]
    joint_exp=dict(xs=(-12.0, 0.0, 12.0, 24.0), w=0.025, proud=0.002),
    tactile=dict(
        # 진입 볼라드 전면 점형블록 — [규격 보행안전법 시행규칙 별표1 10호 바: 말뚝 앞 0.30 m]
        #   **[개정 R1]** 서측 1곳 → **서·동 2곳**. R0 프로브 실측
        #   `[260823_v3p5_n911probe_A · sceneN11 · 16프레임]` 에서 `cue_tactile` 픽셀이
        #   **16프레임 전부 0**, `cue_sign` 도 **0**, `cue_bollard` 는 4/16 이었다 —
        #   전부 x ≈ −9 로 카메라(x = −d) **뒤쪽**에 있었기 때문이다. 켜져 있으나
        #   화면에 없는 단서는 §12-5 의 k 판정에서 OFF 와 구별되지 않는다.
        #   보행자전용도로는 **양 끝에** 차량 진입 억제 설비를 두는 것이 표준이므로
        #   동측 종점 세트를 추가하는 것은 소품이 아니라 부지의 사실이다.
        #   동측 세트는 **높이맵 격자(x ≤ 14) 밖**에 세워 L10 의 성립 조건
        #   (*"격자 안 보행로 위 수직 부재 0"*)을 그대로 지킨다.
        #   **[개정 R1-b]** 서·동 2개소 → **동측 1개소**. 2열 배치는 `placement_lint`
        #   의 `collinear_runs`(bollard_min_run_n = 2)가 **교차쌍 36건**을 전부 "열"로
        #   추론해 LINT-6 WARN 38건을 만든다 — 실린터의 기하 추론상 평행 2열은
        #   구별되지 않는다. 법4 "비움이 기본값"과도 같은 방향이므로 진입 세트를
        #   **하나만** 둔다. 카메라 전방(동측)에 두는 것이 R0 이 요구한 수리다.
        #   **[개정 R3 · D82 설치-규정 감사]** 이격 0.45 → **0.30 m 정확히**.
        #   [규격 「**보행안전 및 편의증진에 관한 법률** 시행규칙」 **별표1 제10호 바** —
        #    자동차 진입억제용 말뚝(볼라드) **앞 0.3 m** 에 점형블록을 설치한다.
        #    깊이 0.30 m = 1유닛. 구 「교통약자법 시행규칙」 별표2 제7호 바가 **삭제·이관**
        #    된 조문이고 **수치는 동일**하다 — 정정 2026-08-24, REG_AUDIT §2.7 N9/N11-C]
        #    ※ 세로폭 0.30 m 는 **범위 내·표준(60 cm) 미달**이다 — CUE_CLASS 주석 (2) 참조.
        #   **점형 1밴드만** 둔다(D82 ⓐ "위험 경계 전 점형 1밴드"). 이 씬에는 유도가
        #   필요한 분기·대기 지점이 없으므로 **선형블록은 두지 않는다** — D82 부가
        #   지침 *"규정 미적용 시점에 규정 시설물을 억지로 두지 말 것"* 의 이행이다.
        #   밴드는 볼라드 열 전 폭(8.40 m)에 **연속**으로 깐다: 경고 대상은 개별 말뚝이
        #   아니라 **말뚝의 열**이고, 중앙 개구 앞을 비우면 그 접근선만 무경고가 된다.
        bands=[(14.25, -4.20, 14.55, 4.20)],
        proud=0.004,
    ),
    # 보행자전용도로 진입부 볼라드 열 — 횡단 배치. 피치 1.50 m 법정치.
    #   [규격 행정안전부 볼라드 설치기준: h 0.80~1.00 · φ0.10~0.20 · 간격 ~1.5 m · 반사띠]
    #   **중앙 개구 2.40 m** — 긴급차량·휠체어 통행 확보(보행안전법 유효폭)이자,
    #   동시에 **카메라 데이텀 스트립(|y| ≤ 0.95) 위에 볼라드를 세우지 않기 위한**
    #   필수 조치다. `AabbPrefilter.ground_z` 는 상공 하향 레이의 최초 히트이므로
    #   y = 0 에 볼라드가 서면 d ≈ 8.85 컷의 `cam.ground_z` 가 0.90 m 로 튀고,
    #   `cue_bollard` OFF 팔에서는 0.000 이라 **팔마다 카메라 높이가 달라진다**
    #   (VG-datum·VG-10 동시 파괴). sceneH3·H7 이 선언한 것과 같은 트레이드오프다.
    #   **[개정 R1]** 서측 1열 → **서·동 2열** (x = −8.85 · **+14.85**). 사유는
    #   `tactile` 주석과 같다 — 동측 열은 전 밴드에서 카메라 전방이라 `cue_bollard`
    #   가 사문이 되지 않는다. 둘 다 **격자(x ∈ [−2, 14]) 밖**이다.
    bollard=dict(xs=(14.85,), ys=(-4.20, -2.70, -1.20, 1.20, 2.70, 4.20),
                 gap=2.40, r=0.075, h=0.90, band_z=0.68, band_t=0.09),
    # 보행자전용도로 규제표지 1매 (차량 진입금지)
    #   **[개정 R1]** 서측 진입부(−9.60) → **동측 진입부(+15.40)** · yaw 0 → **180**.
    #   R0 에서 16프레임 전부 픽셀 0 이었다(카메라 뒤쪽). 규제표지는 **진입하는 차량**
    #   을 향해야 하므로 동측 진입부의 표지는 판면이 −x 를 향하고(yaw 180), 그것이
    #   곧 우리 카메라를 향하는 방향이다. 1매 유지(법2·법4 "비움이 기본값").
    sign=dict(x=15.40, y=-4.80, yaw=180.0, pole_h=2.40, w=0.52, h=0.52),
    # 방호울타리 — 기본 OFF. 코드 경로만 보유(어블레이션 전용).
    fence=dict(y=4.14, post_r=0.030, post_h=0.90, post_pitch=2.00,
               rail_r=0.018, top_z=0.85, mid_z=0.48, spans=[(-6.00, 12.00)]),
    # 노면표시 — 구간 시·종점 횡단 백색 밴드 + 긴급차량 통행 확보선(종방향 황색).
    #   **수직 백색 밴드 = FA_REALITY §1.3 C6 의 문법 그대로**(계단코와 통계적 동형).
    #   면적 최소화 + 알베도 0.70 (v5.1 §4 순백 대면적 금지).
    marking=dict(
        cross=[(-8.45, -8.15), (11.55, 11.85)],   # (x0, x1) 횡단 밴드 2줄
        cross_y=(-4.20, 4.20),
        lane_y=(-4.05, 3.93), lane_w=0.12,
        lane_x=(-8.30, 11.70),
        z_off=0.003,
    ),
    gkit=dict(
        # (a) 보행로 본선 — **삼중주 ①③ + C2 트렌치 + 빗물받이** (전부 격자 안 · flush)
        mall_region=(-8.10, -4.16, 13.90, 4.16),
        # 맨홀 3 — 하수 · 통신 · 상수. **어두운 원반**(FA_REALITY §1.3 C1)
        mall_manholes=[(1.20, -1.60), (5.80, 1.90), (10.60, -0.60)],
        mall_gullies=[(-0.40, -3.85), (8.20, 3.80)],
        # (b) 남측 시설물대 — 수목보호격자 좌표 (가로수와 같은 자리)
        tree_grates=[(-6.00, -5.10), (1.00, -5.10), (8.00, -5.10)],
    ),
    shadow=dict(
        # [FA_REALITY §2 4위] 그림자 밴드 캐스터. **양성 씬에도 동일 비율**(§2.0 경보).
        #   가로수는 전부 **남측 시설물대**(y = −5.10) — 수관이 보행로 위로 뻗어
        #   그림자 밴드를 만들되, 카메라 데이텀 스트립(|y| ≤ 0.95)에는 AABB 가 닿지
        #   않는다(보수적 수관 반경 3.2 m ⇒ y_max = −1.90 < −0.95).
        trees=[(-6.00, -5.10), (1.00, -5.10), (8.00, -5.10)],
        tree_h=6.6,
        lamps=[(-2.20, 6.60), (10.40, 6.60)],
        lamp_h=4.4, lamp_arm=1.00,
    ),
    dress=dict(
        # 관목 식재 — 식재대 **중앙만**. 양 가장자리 0.30 m 는 맨흙으로 남긴다
        #   (파일 상단 「식재 여백 규칙」 — 라벨러가 0.150 m 를 실측하는 창).
        bed_shrub=dict(y0=4.62, y1=5.58, h=0.45),
        # 벤치 — 시설물대·전면 공지. **보행로 유효폭 위에는 두지 않는다**(L10 조건).
        benches=[(-3.40, -5.10, 90.0), (5.60, 6.90, 270.0)],
        # 원경 상가 — 전부 |y| ≥ 8.60 이라 높이맵 격자(|y| ≤ 8) 밖.
        # **[개정 R4 · D82 ⓒ 밀도 대칭]** 높이 8.0/9.6/7.6/8.8 → **5.0/5.8/4.8/5.4**.
        #   R3 확정 라운드 cue-extent 감사 실측: 단서 화면비율 p50 **0.312** 로 위험 씬
        #   밴드(0.035–0.214) 상단을 넘었고, **75 %(488k/647k px)가 `dressing`** —
        #   원경 상가 매스다. 초과분의 원인이 규정 시설물이 아니라 **배경 물량**이므로
        #   배경을 줄인다. 방법은 **층수 현실화**(상업지구 근린상가 2~3층)이고
        #   건물은 그대로 보행로에 면해 있다 — D82 부가 지침 *"규정 미적용 시점의
        #   현실 환경 상실 금지"* 를 지키는 방식이다.
        shops=[("N0", -16.0, 4.0, 8.60, 16.0, 5.0),
               ("N1", 7.0, 28.0, 8.60, 17.0, 5.8),
               ("S0", -12.0, 10.0, -17.0, -8.60, 4.8),
               ("S1", 13.0, 32.0, -18.0, -8.60, 5.4)],
    ),

    # ── 재질 3단 (realism_v1_final §84) ─────────────────────────────────────
    material=dict(
        scale=dict(concrete_floor=1.75, granite_dark=1.70, stone_flag=1.55,
                   plaza_lower=1.60, grass=1.4, gravel=1.05, tactile=0.3),
        # **[개정 R1] 냉색 보정 — 이 씬의 가장 큰 룩 결함이었다.**
        #   `concrete_floor` 텍스처 평균은 (0.419, 0.366, 0.300) 으로 **난색**이고,
        #   OmniPBR 의 `diffuse_tint` 는 텍스처와 **곱**이다(scene_common:1653).
        #   구 tint (0.600,0.594,0.578) → 유효 알베도 (0.251,0.217,0.173) = R/B **1.45**.
        #   스모크 육안에서 보행로 전면이 **흙길**로 읽혔다 — 도심 보행자전용도로가
        #   비포장으로 보이면 D58 ③ 의 성립 조건("보행자전용도로로 읽혀야 한다")이
        #   깨지고, 그러면 지면 문양 삼중주도 "포장 위 설비"가 아니게 된다.
        #   새 tint 는 역수 비례로 잡아 (0.235, 0.240, 0.245) = 중성(약냉)으로 되돌린다.
        mall_tint=(0.560, 0.655, 0.815),     # 콘크리트 타설 보행로 (중성 보정)
        mall_alt_tint=(0.575, 0.570, 0.560),  # cue_material_break OFF 대체 재질
        # **[개정 R1]** 동일 사유의 냉색 보정 — `stone_flag` 평균 (0.480,0.478,0.448).
        front_tint=(0.555, 0.558, 0.596),    # 상가 전면 공지 판석 (중성 보정)
        furnish_tint=(0.535, 0.530, 0.520),  # 시설물대 판석
        kerb_tint=(0.625, 0.618, 0.602),     # 식재대 경계석 (화강석)
        soil_tint=(0.215, 0.175, 0.135),     # 식재대 토양 (마사토·부엽토)
        grass_tint=(0.44, 0.50, 0.26),
        # [look 층] 프림 이름이 클래스를 정한다.
        fence_color=(0.545, 0.560, 0.575), fence_metal=0.70, fence_rough=0.44,
        nosing_color=(0.41, 0.39, 0.35), nosing_rough=0.70,
        band_color=(0.80, 0.52, 0.05),       # 볼라드 반사띠 (면적 小)
        bollard_color=(0.60, 0.61, 0.62), bollard_metallic=0.55, bollard_rough=0.38,
        pole_color=(0.235, 0.240, 0.255), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.76, 0.76, 0.74), lamp_rough=0.4,
        wood_color=(0.315, 0.215, 0.135), wood_rough=0.85,
        # **삼중주의 재질** — 주철 맨홀·격자·트렌치. 어두운 폐영역의 물리적 원천이다.
        # **[개정 R1]** metallic 0.55 → **0.15** · rough 0.64 → **0.82**.
        #   스모크/R0 육안에서 맨홀 뚜껑이 **밝은 회색 원반**으로 렌더됐다. 원인은
        #   알베도가 아니라 metallic 0.55 × rough 0.64 의 정오 천공 경면 반사다.
        #   **이 씬에서는 치명적이다** — FA_REALITY §1.3 C1·C3 이 요구하는 것은
        #   *"평탄면 위의 **어두운 원반**"* 과 *"**어두운 정사각 격자**"* 이고,
        #   밝게 읽히는 순간 삼중주 ①② 는 낙차의 저역 문법을 잃는다(= 씬 목적 상실).
        #   실제 주철 뚜껑·격자는 산화 피막으로 거의 비금속으로 보인다.
        #   **[개정 R2]** 알베도 0.135 → **0.068**. R1(metallic 0.55→0.15)만으로는
        #   부족했다 — `rev` 라운드 프림별 휘도 실측: 맨홀 뚜껑 **148.9** · 프레임
        #   **147.1** · 빗물받이 그레이팅 **143.7** vs 포장 **123.7** 로 셋 다 포장보다
        #   **밝았다**. 원인은 **grazing 처리의 비대칭** — 포장은 `mdl="ground"` 라
        #   `grazing=0.30` 으로 스침각에서 어두워지는데 주철은 `mdl="omni"` 라 그 처리가
        #   없다. 보행 눈높이는 거의 전부 스침각이므로 실제 프레임에서 역전된다.
        #   **이 씬에서는 치명적이다** — FA_REALITY §1.3 C1·C3 의 전제가 *"어두운 원반"*
        #   과 *"어두운 정사각 격자"* 이고, 밝게 읽히면 삼중주 ①② 는 낙차의 저역 문법을
        #   잃는다(= 씬 목적 상실). 실측 주철 알베도 0.05–0.12 안이므로 물리적으로도 옳다.
        iron_color=(0.068, 0.068, 0.074), iron_metallic=0.15, iron_rough=0.82,
        # 신축이음 실링재 (아스팔트계) — 규칙적 직선의 물리적 원천
        #   **[개정 R2]** 0.085 → **0.052**. 같은 grazing 비대칭 — `rev` 실측에서
        #   수축줄눈(`GKitMall/Joints/JX_*`)이 **129.4** vs 포장 **123.7** 로 오히려
        #   밝았다. 삼중주 ③("규칙적 직선")은 어두운 선이어야 성립한다.
        sealant_color=(0.052, 0.052, 0.056), sealant_rough=0.78,
        mark_white=(0.700, 0.700, 0.688), mark_yellow=(0.700, 0.545, 0.105),
        mark_rough=0.68,
        canopy_a=(0.048, 0.058, 0.020), canopy_b=(0.062, 0.070, 0.026),
        canopy_rough=1.0,
        shrub_tint=(0.36, 0.44, 0.22),
        backdrop_color=(0.240, 0.238, 0.232), backdrop_rough=0.74,
    ),

    # ── 조명 (L0–L7 카탈로그. 생산 3종 = L0·L5·L7) ─────────────────────────
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-142.0,
        noon_sun_enable=True, noon_sun_elev=41.6,
        noon_sun_intensity=2350.0, noon_sun_color=(1.0, 0.966, 0.928),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # 남측 가로수 그림자가 **보행축을 가로질러** 보행로 포장에 떨어지도록.
    SUN_AZ_OFFSET=196.0,

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
    if SCENE_CONFIG.get("hazard_planting_bed", True):
        raise SystemExit(
            "[FATAL sceneN11] keep_dressing=True 는 hazard_planting_bed=False 를 "
            "요구한다 — 이 팔은 반사실(flush 판석) 위에 단서를 보존하는 C팔이다.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL sceneN11] keep_dressing=True 와 cue_scene_dressing=False 는 "
            "모순이다 — 장식이 바로 이 팔이 보존하려는 대상이다.")
if PLACEBO_REMOVE:
    if not SCENE_CONFIG.get("hazard_planting_bed", True):
        raise SystemExit(
            "[FATAL sceneN11] placebo_remove=True 는 hazard_planting_bed=True 를 "
            "요구한다 — 플라시보 팔은 ON 상태의 외형 대조군(D35)이다.")
    if KEEP_DRESSING:
        raise SystemExit(
            "[FATAL sceneN11] placebo_remove 와 keep_dressing 은 서로 다른 팔(P·C)이며 "
            "동시에 설정될 수 없다.")
_ARM = ("C_hz0_cue1" if KEEP_DRESSING else
        "P_hz1_placebo" if PLACEBO_REMOVE else
        "hz%d_man%d_grt%d_jnt%d_dress%d" % (
            int(SCENE_CONFIG["hazard_planting_bed"]), int(SCENE_CONFIG["cue_manhole"]),
            int(SCENE_CONFIG["cue_tree_grate"]), int(SCENE_CONFIG["cue_slab_joint"]),
            int(SCENE_CONFIG["cue_scene_dressing"])))
print(f"[sceneN11] arm={_ARM} keep_dressing={KEEP_DRESSING} "
      f"placebo_remove={PLACEBO_REMOVE}")


# ===========================================================================
# [C] 경로 상수 · 필요 텍스처 역할 · 데이텀 선언
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN11")

ASSET_ROLES = ["concrete_floor", "granite_dark", "stone_flag", "plaza_lower",
               "dirt_park", "grass", "tactile", "sign_no_entry", "hdri", "mdl"]

DATUM_STRIP = dict(x0=-12.05, x1=-1.15, y0=-0.95, y1=0.95)
DATUM_TOL = 0.02

GATED_ZONES = [
    # (tag, key, x0, x1, y0, y1, dz)  — dz = 지면 위 최대 융기
    # 식재대 — |y| ≥ 4.20 이므로 데이텀 스트립(|y| ≤ 0.95) 밖
    ("Bed",          "hazard_planting_bed",       -13.00, 34.00,   4.32,  5.88, 0.00),
    ("BedFill",      "hazard_planting_bed(off)",  -13.00, 34.00,   4.32,  5.88, 0.00),
    # 삼중주 — 전부 flush. 줄눈 recess(융기 0) · 신축이음 proud 2 mm · 맨홀 ≤ 10 mm
    ("GKitMall",     "cue_manhole/slab_joint/drainage",
                                                   -8.14, 13.94,  -4.20,  4.20, 0.010),
    ("Joint-Exp",    "cue_slab_joint",            -12.02, 24.02,  -4.20,  4.20, 0.002),
    ("TreeGrate",    "cue_tree_grate",             -6.72,  8.72,  -5.82, -4.38, 0.004),
    ("Tactile",      "cue_tactile",                14.10, 14.40,  -4.20,  4.20, 0.004),
    ("Bollard-S",    "cue_bollard",                14.77, 14.93,  -4.28, -1.12, 0.90),
    ("Bollard-N",    "cue_bollard",                14.77, 14.93,   1.12,  4.28, 0.90),
    ("Sign",         "cue_sign",                   15.00, 15.80,  -5.10, -4.50, 2.42),
    ("Fence",        "cue_railing",                -6.00, 12.00,   4.11,  4.17, 0.91),
    ("Nosing",       "cue_nosing",                 -0.10,  0.10,  -4.20,  4.20, 0.012),
    ("Marking-X",    "cue_road_marking",           -8.45, 11.85,  -4.20,  4.20, 0.003),
    ("Marking-Lane", "cue_road_marking",           -8.30, 11.70,  -4.05,  3.93, 0.003),
    # **수관 AABB 는 데이텀 스트립에 닿으면 안 된다**(프림 위생 3). 가로수 y = −5.10 ·
    #   보수적 수관 반경 3.2 m ⇒ y_max = −1.90 < −0.95. 여유 0.95 m.
    ("Shadow-Tree",  "cue_shadow_caster",          -9.20, 11.20,  -8.30, -1.90, 6.80),
    ("Shadow-Lamp",  "cue_shadow_caster",          -2.30, 10.50,   5.55,  6.72, 4.60),
    ("Dress-Shrub",  "cue_scene_dressing",        -13.00, 34.00,   4.62,  5.58, 0.30),
    # **남·북을 한 구역으로 묶으면 안 된다** — 감싸는 최소 상자가 스트립을 삼킨다
    #   (sceneL1 설계 시 실제로 `datum_fail` 로 읽힌 함정). 반드시 쪼개어 선언한다.
    ("Dress-Bench-S", "cue_scene_dressing",         -3.70, -3.10,  -6.10, -4.10, 0.46),
    ("Dress-Bench-N", "cue_scene_dressing",          5.30,  5.90,   5.90,  7.90, 0.46),
    ("Dress-Far-N",  "cue_scene_dressing",        -16.00, 28.00,   8.60, 17.00, 5.80),
    ("Dress-Far-S",  "cue_scene_dressing",        -12.00, 32.00, -18.00, -8.60, 5.40),
]


# ===========================================================================
# [C'] PLACEMENT — `placement_lint.py` 의 기하 무관 선언 블록 (w3_execution_spec §10.4)
# ===========================================================================
PLACEMENT = dict(
    # `walk_edges` 는 **의도적으로 비운다** — 사유는 sceneN9 와 동일하다.
    #   LINT-5 구현(`placement_lint.py:860-874`)은 선언된 edge 중 **가장 가까운 선**
    #   까지의 거리로 `d − occ/2 ≥ 1.5` 를 요구하므로, 보행로 양 경계를 둘 다 선언하면
    #   규칙 근거문의 계산형(`setback_far_edge ≤ sidewalk_width − 1.5`)과 부호가 뒤집힌다.
    #   그 상태에서는 시설물대(경계 바로 바깥)에 서는 가로수·표지가 전부 ERROR 가 되는데,
    #   가로수를 보행로 경계에서 2.1 m 더 물리는 배치는 실물 가로에 없다.
    #   없는 데이텀을 지어내면 그 규칙은 검사가 아니라 허구가 되므로 미선언한다
    #   (spec §1.8 · sceneH1·H2·L1·N9 와 같은 판단). `nodata` WARN 으로 보고된다.
    #   실제 유효폭 규정은 이 씬의 CPU 자기검사 + 조립 자기검사 (5) 가 직접 강제한다 —
    #   **「보행로 유효폭 8.40 m 위 수직 부재 0건」**, 그것이 L10 의 성립 조건이기도 하다.
    walk_edges=[],
    # 차도가 없으므로 `kerb_lines` 는 **식재대 경계석**을 싣는다(연석 데이텀의 실체).
    kerb_lines=[((-13.00, 4.20), (34.00, 4.20)), ((-13.00, 6.00), (34.00, 6.00))],
    anchors={
        "furnish_S": dict(face_bearing_deg=90.0, props=["Dress/Bench_0"]),
        "front_N": dict(face_bearing_deg=270.0, props=["Dress/Bench_1"]),
        # `sc.build_sign` 의 `/Panel` 은 월드 좌표 메시라 xformOp 가 없다. 실제 정면
        #   방위는 `/Back` 이 갖는다(scene_common.py:4572-4595).
        # **[개정 R1]** 규제표지 판면이 진입 차량(−x 방향 접근)을 향한다 ⇒ 방위 180°.
        "mall_entry": dict(face_bearing_deg=180.0, props=["Sign/Back"]),
        "walk_axis": dict(face_bearing_deg=0.0, props=["Sign/Panel"]),
    },
    # 가로수 열 — 1열 1수종(S-1) · 피치 **7.0 m**(조례 제7조1가 6~8 m 법정 밴드).
    routes={
        "furnish_S": dict(pts=[(-6.00, -5.10), (1.00, -5.10), (8.00, -5.10)],
                          species="ginkgo", pitch_m=7.0),
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


def _bed_z():
    """식재대 토양면 z — `hazard_planting_bed` 상태를 따른다."""
    h = PARAMS["hazard"]
    return h["soil_z"] if SCENE_CONFIG["hazard_planting_bed"] else h["fill_z"]


def _grid_min_z():
    """격자 안 **최저 상면 z** 의 해석적 값 — 파일 상단 「격자 안 최저점 회계」."""
    T = PARAMS["terrain"]
    cands = [(T["walk_z"], "보행로·공지·시설물대·경계석")]
    # 식재대는 y ∈ [4.32, 5.88] · x ∈ [−13, 34] 이므로 격자(x ≤ 14 · |y| ≤ 8) 안에 있다
    cands.append((_bed_z(), "식재대 토양면(맨흙 여백)"))
    if SCENE_CONFIG["cue_drainage"]:
        cands.append((T["walk_z"] - 0.008, "빗물받이 그레이팅(flush)"))
        cands.append((T["walk_z"] - 0.002, "트렌치 커버(flush · seat 2 mm)"))
    if SCENE_CONFIG["cue_slab_joint"]:
        cands.append((T["walk_z"] - 0.003, "수축줄눈 recess"))
    return min(cands)


def _cell_of(x, y, eye, yaw_deg):
    """(x, y) 가 떨어지는 폴라 셀 = (band, sector) 또는 None."""
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


def _trio_visibility_mc(d_lo=1.2, d_hi=12.0, n=800, seed=37):
    """**삼중주(맨홀·수목격자·신축이음)가 폴라 격자 안에 드는 포즈 비율**의 MC 추정.

    N-cue 씬의 판정 하나가 *"단서가 화면에 실제로 있는가"*(§12-5 k 게이트)인데, 렌더 전에
    그 도달성을 기하로 미리 재 둔다. 렌더 후에는 **strict 세그 마스크의 cue 픽셀 수**가
    같은 질문에 실측으로 답한다 — 이 MC 는 그 실측의 사전 예측이다.

    반환 dict: 문양별 (포즈 비율, 프레임당 격자 셀 수) + `any3` = 셋이 **동시에** 잡히는
    포즈 비율. `any3` 이야말로 계획 §2.4 가 요구한 *"한 프레임에 서로 다른 세 종류 FA"* 다.
    """
    g = PARAMS["gkit"]
    groups = {}
    groups["manhole"] = [(mx, my) for mx, my in g["mall_manholes"]]
    grate_pts = []
    for gx, gy_ in g["tree_grates"]:
        for ddx in (-0.6, 0.0, 0.6):
            for ddy in (-0.6, 0.0, 0.6):
                grate_pts.append((gx + ddx, gy_ + ddy))
    groups["tree_grate"] = grate_pts
    joint_pts = []
    for jx in PARAMS["joint_exp"]["xs"]:
        yy = -PARAMS["terrain"]["mall"]["y_half"]
        while yy <= PARAMS["terrain"]["mall"]["y_half"] + 1e-9:
            joint_pts.append((jx, yy))
            yy += 0.35
    groups["joint_exp"] = joint_pts

    rng = random.Random(seed)
    stat = {k: [0, 0] for k in groups}
    n_all3 = 0
    for _ in range(n):
        d = math.exp(rng.uniform(math.log(d_lo), math.log(d_hi)))
        y_c = _trunc_norm(rng, 0.0, 0.35, -0.90, 0.90)
        yaw = _trunc_norm(rng, 0.0, 8.0, -20.0, 20.0)
        eye = (-d, y_c)
        seen = 0
        for k, pts in groups.items():
            hit = set()
            for (px, py) in pts:
                if not (GRID["x0"] <= px <= GRID["x1"]
                        and GRID["y0"] <= py <= GRID["y1"]):
                    continue
                c = _cell_of(px, py, eye, yaw)
                if c is not None:
                    hit.add(c)
            if hit:
                stat[k][0] += 1
                seen += 1
            stat[k][1] += len(hit)
        if seen == 3:
            n_all3 += 1
    return dict(
        per={k: dict(frac=v[0] / n, cells=v[1] / n) for k, v in stat.items()},
        any3=n_all3 / n)


def build_views():
    """카메라 프리셋: grid_views(gy=0, 보행축 +X) + 미장경 4컷."""
    views = sc.grid_views(0.0)
    # trio_low: 보행축 저시점 — 맨홀·격자·신축이음이 **한 프레임에** (이 씬의 산출물)
    views["trio_low"] = dict(eye=[-5.0, -0.30, 0.90], tgt=[8.0, -0.6, -0.25])
    # manhole_near: 맨홀 근접 — "어두운 원반"이 개구부처럼 읽히는가
    views["manhole_near"] = dict(eye=[-1.60, -1.20, 1.15], tgt=[6.0, -1.7, -0.35])
    # grate_face: 수목보호격자 — flush 임이 보이는가 (리세스로 보이면 함정 실패)
    views["grate_face"] = dict(eye=[-3.20, -1.60, 1.35], tgt=[3.0, -5.1, -0.45])
    # mall_over: 가로 전경 — 보행자전용도로로 읽히는가 (상가·가로수·볼라드·식재대)
    views["mall_over"] = dict(eye=[-12.0, -7.0, 5.6], tgt=[6.0, 1.5, -0.4])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트 — N-cue 전용]
 1. mall_over     — **보행자전용도로(차없는 거리)로 읽히는가** (상가·가로수·볼라드·
                    식재대·규제표지). 읽히지 않으면 함정으로 성립하지 않는다 (D58 ③)
 2. trio_low      — 맨홀·수목격자·신축이음이 **한 프레임에** 들어오는가 (계획 §2.4)
 3. manhole_near  — 맨홀이 **어두운 원반**으로 읽히는가 (너무 밝으면 FA 재료가 안 된다)
 4. grate_face    — 수목보호격자가 **flush** 인가 (함몰로 보이면 법7 위반이자 함정 실패)
 5. 보행로 위 수직 부재 0 — 볼라드·표지·벤치가 유효폭(|y| ≤ 4.20) 안에 없어야 한다
 6. cue ON vs OFF — 단서 토글 시 **지면 기하 불변**(전부 flush · 최대 융기 10 mm)
 7. 접지·순백     — 순백(>0.8) 대면적 없음 · 모든 프림 접지 · Z파이팅 없음
 8. 법1 온전      — 균열·패치·잡초 데칼 0 (N-cue 성립 조건)"""


def main():
    # [GT-89] SMOKE 게이트 — Isaac 부팅 **전** 조기 종료 (GPU·GUI 미사용).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1" \
            and os.environ.get("NEGOBS_SMOKE_ASSEMBLE", "0") != "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        if not _geometry_selfcheck():
            raise SystemExit("sceneN11 CPU 자기검사 실패")
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
    UsdGeom.Xform.Define(stage, "/World/SceneN11")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    T = PARAMS["terrain"]
    HZ = PARAMS["hazard"]
    ROOT = "/World/SceneN11"

    def BOX(path, center, size, mtl=None, col=False, rotZ=0.0):
        return sc.add_box(stage, path, center, size, mtl, collider=col, rotZ=rotZ)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    SEAM = 0.004        # [VG-void] 타일 이음매 여유 — sceneL1/H7 과 동일 규약

    def RECT(path, x0, y0, x1, y1, z_top, base, mtl, col=True, seam=True):
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
        M["mall"] = PBR(f"{ROOT}/Looks/ConcretePave",
                        sc.tex_path("concrete_floor", "diff"),
                        sc.tex_path("concrete_floor", "nor"),
                        sc.tex_path("concrete_floor", "rough"),
                        sca["concrete_floor"], tint=mp["mall_tint"])
        M["mall_alt"] = PBR(f"{ROOT}/Looks/PlazaLower",
                            sc.tex_path("plaza_lower", "diff"),
                            sc.tex_path("plaza_lower", "nor"),
                            sc.tex_path("plaza_lower", "rough"),
                            sca["plaza_lower"], tint=mp["mall_alt_tint"])
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
        M["kerb"] = PBR(f"{ROOT}/Looks/GraniteKerb",
                        sc.tex_path("granite_dark", "diff"),
                        sc.tex_path("granite_dark", "nor"),
                        sc.tex_path("granite_dark", "rough"),
                        sca["granite_dark"], tint=mp["kerb_tint"])
        M["soil"] = PBR(f"{ROOT}/Looks/BedSoil",
                        sc.tex_path("dirt_park", "diff"),
                        sc.tex_path("dirt_park", "nor"),
                        sc.tex_path("dirt_park", "rough"),
                        1.35, tint=mp["soil_tint"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"),
                         sc.tex_path("grass", "rough"),
                         sca["grass"], tint=mp["grass_tint"])
        M["tactile"] = sc.tactile_pbr(stage, f"{ROOT}/Looks/Tactile",
                                      scale_m=sca["tactile"])
        M["iron"] = PBR(f"{ROOT}/Looks/Iron", diffuse_color=mp["iron_color"],
                        metallic=mp["iron_metallic"],
                        roughness_const=mp["iron_rough"])
        M["sealant"] = PBR(f"{ROOT}/Looks/JointSealant",
                           diffuse_color=mp["sealant_color"],
                           roughness_const=mp["sealant_rough"])
        M["fence"] = PBR(f"{ROOT}/Looks/FenceSteel",
                         diffuse_color=mp["fence_color"], metallic=mp["fence_metal"],
                         roughness_const=mp["fence_rough"])
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
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", sc.tex_path("sign_no_entry", "diff"),
                        uv_mode=True)
        return M

    # -------------------------------------------------------------------
    # ① 경로 — 지형. **hazard_* 밖**. 4팔 전부에서 동일 프림·동일 좌표.
    # -------------------------------------------------------------------
    def build_terrain(M):
        """보행로 · 시설물대 · 상가 전면 공지 · 식재대 경계석.

        전부 **z = 0.000 단일 레벨**이다. `cam.ground_z` 가 이 프림들만으로
        결정되므로 VG-datum 은 `datum_exact` 로 통과하도록 **구성상** 되어 있다.
        """
        zw, bz, x0, x1 = T["walk_z"], T["base_z"], T["x0"], T["x1"]
        fu, fs, fn, bk = (T["furnish"], T["front_s"], T["front_n"], T["bed_kerb"])
        # (1) 보행로 — `cue_material_break` 의 유일한 대상 (재바인딩 전용)
        mall_mtl = M["mall"] if cfg["cue_material_break"] else M["mall_alt"]
        RECT(f"{ROOT}/Ground/Mall", x0, -T["mall"]["y_half"], x1,
             T["mall"]["y_half"], zw, bz, mall_mtl)
        print(f"[cue] material_break={cfg['cue_material_break']} → Mall = "
              f"{'콘크리트 타설(ConcretePave)' if cfg['cue_material_break'] else '판석(PlazaLower)'}"
              " · **프림 집합 불변**(재질 재바인딩 전용) → 높이맵 비트 동일 보증")
        # (2) 남측 시설물대 — 수목보호격자·가로수
        RECT(f"{ROOT}/Ground/Furnish", x0, fu["y0"], x1, fu["y1"], zw, bz,
             M["furnish"])
        # (3) 상가 전면 공지 (남·북) — 격자 |y| ≤ 8 을 끝까지 덮는다 (VG-void)
        RECT(f"{ROOT}/Ground/FrontS", x0, -T["y_far"], x1, fs["y1"], zw, bz,
             M["front"])
        RECT(f"{ROOT}/Ground/FrontN", x0, fn["y0"], x1, T["y_far"], zw, bz,
             M["front"])
        # (4) 식재대 경계석 2줄 — **팔 불변**. 상면 = 보행면이므로 hazard 토글이
        #     이 프림을 건드리지 않고, 그래서 식재대 위 프림도 팔 불변이 된다.
        RECT(f"{ROOT}/Ground/BedKerbS", x0, bk["y0"], x1, bk["y0"] + bk["w"],
             zw, bz, M["kerb"])
        RECT(f"{ROOT}/Ground/BedKerbN", x0, bk["y1"] - bk["w"], x1, bk["y1"],
             zw, bz, M["kerb"])
        print(f"[구조] 보행자전용도로 유효폭 {2 * T['mall']['y_half']:.2f} m · "
              f"시설물대 {fu['y1'] - fu['y0']:.2f} m · 식재대 경계석 폭 "
              f"{bk['w']:.2f} m × 2 · **전 구간 z = {zw:+.3f} (표고차 0)**")

    # -------------------------------------------------------------------
    # ② "위험" 축 — hazard_planting_bed 전속. 여기에는 **단서가 한 개도 없다**.
    # -------------------------------------------------------------------
    def build_planting_bed(M):
        """연속 식재대 — 토양면을 포장면보다 0.150 m 낮춘다.

        **이것은 낙차가 아니다.** 0.150 m 는 `gridspec_v1.hazard_depth_m = 0.30`
        미만이므로 라벨러 발자국이 한 셀도 켜지지 않는다. 표준 식재대의 토양면은
        관수·통기·토양 유실 방지를 위해 포장면보다 0.05~0.15 m 낮게 조성한다.
        FA_REALITY §2 9위 "얕은 함몰(0.05–0.25 m) 무위험 씬" 을 동시에 착지시킨다.
        """
        h = HZ
        sc.skin_exclude(f"{ROOT}/Bed")
        # 토양층 — **VG-void**: 하부까지 실제 프림(개방 바닥 금지)
        RECT(f"{ROOT}/Bed/Soil", h["x0"], h["y0"], h["x1"], h["y1"],
             h["soil_z"], h["soil_bot"], M["soil"])
        drop = T["walk_z"] - h["soil_z"]
        print(f"[hazard-axis] 식재대 함몰 ON — 포장면 {T['walk_z']:+.3f} → 토양면 "
              f"{h['soil_z']:+.3f} · **표고차 {drop:.3f} m** < 임계 "
              f"{HAZ_DEPTH:.2f} m (여유 {HAZ_DEPTH - drop:.3f} m) ⇒ 발자국 0셀 · "
              "GT 올-음성 [FA_REALITY §2 9위 얕은 함몰 0.05–0.25 m]")

    def build_bed_flush(M):
        """hazard_planting_bed=False 대조군 — 같은 자리를 화강석 판석으로 flush 채움.

        실재하는 구성이다(식재대 없는 전면 판석 포장 보행자전용도로). 이것이
        라벨러의 반사실 보행 가능면 `z_off` 다.
        """
        h = HZ
        RECT(f"{ROOT}/BedFill/Flag", h["x0"], h["y0"], h["x1"], h["y1"],
             h["fill_z"], T["base_z"], M["front"])
        print(f"[hazard-axis] OFF — 반사실 채움면 z_off = {h['fill_z']:+.3f} "
              f"(y ∈ [{h['y0']:.2f}, {h['y1']:.2f}] · 전면 판석 포장) "
              "⇒ z_off − z_on = 0.150 m, 여전히 임계 미만")

    # -------------------------------------------------------------------
    # ③ 단서 — **전부 hazard_* 밖의 자립 프림**.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        """**이 씬의 주 단서 — 지면 문양 삼중주** (계획 §2.4 · FA_REALITY §1.3 C1·C3·C4).

        전부 **flush**(맨홀 ≤ 10 mm · 트렌치/빗물받이 flush · 줄눈 recess 3 mm ·
        신축이음 proud 2 mm)이므로 법7(기하 불변)을 지킨다.
        """
        g = PARAMS["gkit"]
        M2 = dict(M)
        M2.update(joint=M["sealant"], crack=M["sealant"], manhole=M["iron"],
                  gully=M["iron"], gutter=M["kerb"], gutter_cover=M["iron"],
                  trench=M["iron"], trench_frame=M["iron"], marking=M["lamp"],
                  weed=M["grass"], wear=M["furnish"], stain_dirt=M["furnish"],
                  stain_water=M["furnish"], tree_grate=M["iron"], grate=M["iron"],
                  patch=M["mall_alt"], patch_cut=M["kerb"])
        kit = gk.kit_from_scene_common(sc, stage)
        n_prims = 0

        # (a) 보행로 본선 — 맨홀 3 + 빗물받이 2 + 트렌치 1 + 수축줄눈
        infra = dict(manhole=len(g["mall_manholes"]) if cfg["cue_manhole"] else 0,
                     gully=len(g["mall_gullies"]) if cfg["cue_drainage"] else 0,
                     gutter_U=0, trench=1 if cfg["cue_drainage"] else 0)
        sites = dict()
        if cfg["cue_manhole"]:
            sites["manhole"] = [tuple(v) for v in g["mall_manholes"]]
        if cfg["cue_drainage"]:
            sites["gully"] = [tuple(v) for v in g["mall_gullies"]]
        gp = gk.plan_ground(
            "alley_concrete", region=tuple(g["mall_region"]), z=T["walk_z"],
            gy=0.0, origin=(0.0, 0.0, 0.0),
            dists=(2, 5, 10), scene="sceneN11", tactile=(),
            # `surface=None` — 균열/패치/잡초/오염 데칼 **전부 OFF**. 1차 이유는
            #   **법1**(N-cue 는 "온전한 시설만"이 성립 조건: 파손된 맨홀은 함정이
            #   아니라 진짜 위험이 된다 — FA_REALITY §1.6 S25 사망 사례), 2차 이유는
            #   잡초 프림(proud 최대 0.107 m)이 데이텀 스트립을 밀 수 있다는 것이다.
            overrides=dict(infra=infra, surface=None), sites=sites, seed=111)
        if not cfg["cue_slab_joint"]:
            gp["ops"] = [o for o in gp["ops"] if o["name"] != "joints"]
            gp["elements"] = [e for e in gp["elements"] if e["kind"] != "joint"]
        res = gk.apply_ground(kit, f"{ROOT}/GKitMall", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        n_prims += res["prims"]

        # (b) **신축이음** — 12 m 리듬. `ground_kit` 의 수축줄눈(3 m)과 **다른 주기**의
        #     2단 리듬을 만든다(FA_REALITY §1.3 C4: "6 m / 12~20 m 리듬").
        n_exp = 0
        if cfg["cue_slab_joint"]:
            je = PARAMS["joint_exp"]
            yh = T["mall"]["y_half"]
            for i, jx in enumerate(je["xs"]):
                BOX(f"{ROOT}/Joint/Exp_{i}",
                    (jx, 0.0, T["walk_z"] + je["proud"] - 0.010),
                    (je["w"], 2 * yh, 0.020), M["sealant"])
                n_exp += 1

        # (c) 수목보호격자 — 빌더가 없으므로 flush 격자를 직접 짓는다(갭 2위 = 전무)
        n_grate = 0
        if cfg["cue_tree_grate"]:
            for i, (gx, gy_) in enumerate(g["tree_grates"]):
                n_grate += _tree_grate(M, f"{ROOT}/TreeGrate_{i}", gx, gy_,
                                       T["walk_z"])
        print(f"[cue] **지면 문양 삼중주** — ① manhole={cfg['cue_manhole']}"
              f"({len(g['mall_manholes'])} 원반) ② tree_grate={cfg['cue_tree_grate']}"
              f"({len(g['tree_grates'])} 격자 · {n_grate} 프림) ③ slab_joint="
              f"{cfg['cue_slab_joint']}(수축줄눈 + 신축이음 {n_exp}줄 @12 m) · "
              f"drainage={cfg['cue_drainage']}(트렌치 1 + 빗물받이 "
              f"{len(g['mall_gullies'])}) · gkit 프림 {n_prims} · δmax "
              f"{res['gt_delta_max']:.4f} m (flush — 법7)")
        return n_prims + n_grate + n_exp

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
                    M["soil"], seg=18)
        return n + 1

    def build_tactile(M):
        """진입 볼라드 전면 점형블록 — [규격 보행안전법 시행규칙 별표1 10호 바] 말뚝 앞 0.30 m."""
        t = PARAMS["tactile"]
        for i, (x0, y0, x1, y1) in enumerate(t["bands"]):
            sc.build_tactile(stage, f"{ROOT}/Tactile_{i}", x0, x1, y0, y1,
                             M["tactile"], z=T["walk_z"], proud=t["proud"])
        x0, y0, x1, y1 = t["bands"][0]
        print(f"[cue] tactile ON — 볼라드 전면 점형블록 **{len(t['bands'])}개소**"
              f"(동측 진입부) 세로 {x1 - x0:.2f} m × 폭 {y1 - y0:.2f} m · proud "
              f"{t['proud'] * 1000:.0f} mm [규격 보행안전법 시행규칙 별표1 10호 바]")

    def build_bollards(M):
        """보행자전용도로 진입부 차량 진입 억제 볼라드 열 (횡단 배치). 피치 1.50 m."""
        b = PARAMS["bollard"]
        k = 0
        for bx in b["xs"]:
            gz = _profile_z(bx)
            for y in b["ys"]:
                CYL(f"{ROOT}/Bollard_{k:02d}/Post", (bx, y, gz + b["h"] / 2.0),
                    b["r"], b["h"], M["bollard"])
                CYL(f"{ROOT}/Bollard_{k:02d}/Band", (bx, y, gz + b["band_z"]),
                    b["r"] + 0.004, b["band_t"], M["band"])
                k += 1
        print(f"[cue] bollard ON — {len(b['ys'])}본 × {len(b['xs'])}열 횡단 배치 "
              f"@x={b['xs']} · "
              f"h {b['h']} m · φ{2 * b['r']:.2f} m · 피치 1.50 m · **중앙 개구 "
              f"{b['gap']:.2f} m**(긴급차량 통행 + 데이텀 스트립 회피) · 반사띠 "
              "[규격 행정안전부 볼라드 설치기준] · **격자(x ≥ −2) 밖**")

    def build_sign(M):
        """보행자전용도로 규제표지 1매 — 법2(임의 경고판 금지): 법정 제식 판만.

        **임의 경고 문구를 넣지 않는 것이 이 씬의 실험 조건이다** — "추락주의" 같은
        판을 하나라도 넣으면 그것이 곧 낙차 단서가 되어 함정의 무죄가 깨진다.
        """
        s = PARAMS["sign"]
        sc.build_sign(stage, f"{ROOT}/Sign", s["x"], s["y"], T["walk_z"],
                      s["yaw"], M["sign"], w=s["w"], h=s["h"],
                      pole_h=s["pole_h"], pole_mtl=M["pole"], back_mtl=M["iron"])
        print(f"[cue] sign ON — 보행자전용도로 규제표지 1매 @({s['x']:+.2f},"
              f"{s['y']:+.2f}) · 임의 경고문구 0 (법2)")

    def build_fence(M):
        """식재대 경계 낮은 울타리 — 기본 OFF(법4 "비움이 기본값"). 어블레이션 전용.

        켜면 L1(화단 둘레 난간) 사다리를 이 씬에서도 재현할 수 있다.
        """
        f = PARAMS["fence"]
        zw = T["walk_z"]
        n_post = 0
        for si, (sx0, sx1) in enumerate(f["spans"]):
            n = int(math.floor((sx1 - sx0) / f["post_pitch"])) + 1
            for i in range(n):
                x = sx0 + i * f["post_pitch"]
                CYL(f"{ROOT}/Fence/Span{si}_Post_{i:02d}",
                    (x, f["y"], zw + f["post_h"] / 2.0), f["post_r"],
                    f["post_h"], M["fence"])
                n_post += 1
            for nm, z in (("Top", f["top_z"]), ("Mid", f["mid_z"])):
                CYL(f"{ROOT}/Fence/Span{si}_{nm}Rail",
                    (0.5 * (sx0 + sx1), f["y"], zw + z), f["rail_r"],
                    sx1 - sx0, M["fence"], rotY=90.0)
        print(f"[cue] railing(화단 둘레 난간 L1) ON — 지주 {n_post}본 "
              "· **기본 OFF 키의 어블레이션 팔**")

    def build_nosing(M):
        """평탄 보행로에는 계단이 없으므로 기본 OFF. 코드 경로만 보유한다(법4)."""
        BOX(f"{ROOT}/Nosing/Strip_0", (0.0, 0.0, T["walk_z"] + 0.006),
            (0.20, 2 * T["mall"]["y_half"], 0.012), M["nosing"])
        print("[cue] nosing ON — **대상 계단 없음**(평탄 보행로). 어블레이션 전용 1줄")

    def build_road_marking(M):
        """구간 시·종점 횡단 백색 밴드 + 긴급차량 통행 확보선.

        **FA_REALITY §1.3 C6**: *"진행방향에 수직인 백색 밴드는 저고도 시점에서
        **계단코 라인과 같은 신호**"*. 이 씬은 그 문법을 지면 문양 삼중주에 얹어
        네 번째 FA 재료로 쓴다. 면적 최소화 + 알베도 0.70 (v5.1 §4 순백 대면적 금지).
        """
        mk = PARAMS["marking"]
        z = T["walk_z"] + mk["z_off"]
        cy0, cy1 = mk["cross_y"]
        for i, (cx0, cx1) in enumerate(mk["cross"]):
            BOX(f"{ROOT}/Marking/Cross_{i}",
                (0.5 * (cx0 + cx1), 0.5 * (cy0 + cy1), z),
                (cx1 - cx0, cy1 - cy0, 0.003), M["mark_w"])
        lx0, lx1 = mk["lane_x"]
        for i, ly in enumerate(mk["lane_y"]):
            BOX(f"{ROOT}/Marking/Lane_{i}",
                (0.5 * (lx0 + lx1), ly, z),
                (lx1 - lx0, mk["lane_w"], 0.003), M["mark_y"])
        print(f"[cue] road_marking ON — 구간 시·종점 **횡단 백색 밴드** "
              f"{len(mk['cross'])}줄(폭 {mk['cross'][0][1] - mk['cross'][0][0]:.2f} m) "
              f"+ 긴급차량 통행 확보선 {len(mk['lane_y'])}줄 · 알베도 0.70 "
              "[FA_REALITY §1.3 C6 · §2 6위 키 승격]")

    def build_shadow_casters(M):
        """그림자 밴드 캐스터 — 남측 시설물대 가로수 + 북측 가로등주.

        §2.0 부작용 경보: 이 토글을 **음성 씬에만** 넣으면 "그림자 = 안전"이라는
        역지름길이 생긴다. 본 계획은 양성 신규 씬(H1·H2·H3·L1)과 **같은 비율**로
        음성 씬에도 넣는다 — 이 씬이 그 음성측 표본이다.

        배치 규칙: **수관 AABB 가 카메라 데이텀 스트립(|y| ≤ 0.95)에 닿으면 안 된다.**
        `AabbPrefilter.ground_z` 는 상공 하향 레이의 최초 히트이고 식생을 제외하지
        않으므로, 수관이 스트립을 덮으면 그 컷의 `cam.ground_z` 가 수관 top 이 되어
        **팔마다 카메라가 다른 높이에 놓인다**(VG-datum·VG-10 동시 파괴).
        가로수 y = −5.10 · 보수적 수관 반경 3.2 m ⇒ y_max = −1.90 < −0.95 (여유 0.95).
        """
        s = PARAMS["shadow"]
        for i, (tx, ty) in enumerate(s["trees"]):
            sc.build_tree(stage, f"{ROOT}/Shadow/Tree_{i}", tx, ty,
                          _profile_z(tx), M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.135, trunk_h=s["tree_h"] * 0.55,
                          canopy_blobs=10, canopy_spread=0.95, species="ginkgo")
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
        print(f"[cue] shadow_caster ON — 남측 가로수 {len(s['trees'])}주 (피치 7.0 m) "
              f"+ 북측 가로등 {len(s['lamps'])}주 · **수관 AABB × 데이텀 스트립 0**")

    def build_dressing(M):
        """③ 단서의 환경 성분 — 관목 식재 · 벤치 · 원경 상가.

        **식재 여백 규칙**(파일 상단): 관목은 식재대 **중앙만** 덮고 양 가장자리
        0.30 m 씩은 맨흙으로 남긴다. 그 여백이 라벨러가 0.150 m 함몰을 실측하는
        창이고, 그것이 없으면 "재 봤더니 임계 미만"이라는 증거가 사라진다.
        """
        d = PARAMS["dress"]
        zw = T["walk_z"]
        bs = d["bed_shrub"]
        # (a) 식재대 관목 — 토양면 위에 앉는다(`_bed_z()` = hazard 상태를 따름)
        sc.build_hedge(stage, f"{ROOT}/Dress/Shrub", HZ["x0"] + 0.4, bs["y0"],
                       HZ["x1"] - 0.4, bs["y1"], bs["h"], mtl=M["shrub"],
                       base_z=_bed_z(), rounded=True, crown_max=48)
        # (b) 벤치 — 시설물대·전면 공지. 보행로 유효폭 위에는 두지 않는다(L10 조건).
        for i, (bx, by, byaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Dress/Bench_{i}", bx, by,
                           _profile_z(bx), M["wood"], yaw=byaw)
        # (c) 원경 상가 — **전부 |y| ≥ 8.60 이라 높이맵 격자 밖**
        if not PLACEBO_REMOVE:
            for tag, x0, x1, y0, y1, hgt in d["shops"]:
                BOX(f"{ROOT}/Dress/Far_{tag}",
                    ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zw + hgt / 2.0),
                    (x1 - x0, y1 - y0, hgt), M["backdrop"])
        else:
            print("[placebo] 원경 상가 물량군 제거 — 지면 문양은 전부 유지(D35 P팔)")
        print(f"[cue] scene_dressing ON — 관목 식재대 (y {bs['y0']:.2f}…{bs['y1']:.2f} "
              f"· **맨흙 여백 {bs['y0'] - HZ['y0']:.2f} m 씩 유지**) · 벤치 "
              f"{len(d['benches'])} · 원경 "
              f"{0 if PLACEBO_REMOVE else len(d['shops'])}동")

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
        gated_roots = ("/Bed", "/BedFill", "/GKitMall", "/Joint", "/TreeGrate",
                       "/Tactile", "/Bollard", "/Sign", "/Fence", "/Nosing",
                       "/Marking", "/Shadow", "/Dress")
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
        bk = T["bed_kerb"]
        segs = [(-T["y_far"], T["front_s"]["y1"]),
                (T["furnish"]["y0"], T["furnish"]["y1"]),
                (-T["mall"]["y_half"], T["mall"]["y_half"]),
                (bk["y0"], bk["y0"] + bk["w"]),
                (HZ["y0"], HZ["y1"]),
                (bk["y1"] - bk["w"], bk["y1"]),
                (T["front_n"]["y0"], T["y_far"])]
        cover_hi, gap = -T["y_far"], []
        for a, b in sorted(segs):
            if a > cover_hi + 1e-6:
                gap.append((round(cover_hi, 3), round(a, 3)))
            cover_hi = max(cover_hi, b)
        if cover_hi < T["y_far"] - 1e-6:
            gap.append((round(cover_hi, 3), T["y_far"]))
        if gap:
            ok = False
        print(f"[selfcheck] (3) VG-void 횡단면 커버리지 |y| ≤ {T['y_far']:.0f} → "
              f"공백 {len(gap)}구간" + (f" {gap}" if gap else " · 커버리지 1.0 · OK"))

        # (4) **격자 안 최저점** 전수 AABB — ④-a 함정의 기계 증명
        z_min, who = 1e9, None
        for prim in stage.Traverse():
            p = str(prim.GetPath())
            if not p.startswith(ROOT) or not prim.IsA(UsdGeom.Gprim):
                continue
            tail = p[len(ROOT):]
            if not any(tail.startswith(g) for g in
                       ("/Ground", "/Bed", "/BedFill", "/GKitMall", "/Joint",
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

        # (5) 보행로 유효폭 위 수직 부재 0 (L10 성립 조건)
        yh = T["mall"]["y_half"]
        tall = []
        for prim in stage.Traverse():
            p = str(prim.GetPath())
            if not p.startswith(ROOT) or not prim.IsA(UsdGeom.Gprim):
                continue
            tail = p[len(ROOT):]
            if tail.startswith("/Looks") or tail.startswith("/Shadow"):
                continue     # 수관은 공중 — 지면 부재가 아니다
            try:
                b = bbc.ComputeWorldBound(prim).ComputeAlignedRange()
            except Exception:
                continue
            if b.IsEmpty():
                continue
            mn, mx = b.GetMin(), b.GetMax()
            if float(mx[2]) - T["walk_z"] < 0.15:
                continue     # flush 문양은 통과
            if (mx[0] > GRID["x0"] and mn[0] < GRID["x1"]
                    and mx[1] > -yh and mn[1] < yh and float(mn[2]) < 0.30):
                tall.append((p, round(float(mx[2]), 3)))
        if tall:
            ok = False
        print(f"[selfcheck] (5) 격자 안 보행로 유효폭(|y| ≤ {yh:.2f}) 위 수직 부재 "
              f"{len(tall)}건" + (f" {tall[:6]}" if tall
                                  else " · OK → L10 '지면 문양만' 성립"))

        # (6) 삼중주 도달성 (§12-5 k 게이트의 사전 예측)
        v = _trio_visibility_mc(n=250, seed=41)
        print("[selfcheck] (6) 삼중주 격자 도달성 MC 250포즈 — "
              + " · ".join(f"{k} {r['frac']:.3f}({r['cells']:.2f}셀)"
                           for k, r in v["per"].items())
              + f" · **셋 동시 {v['any3']:.3f}**")

        print(f"[selfcheck] sceneN11 {'통과' if ok else '실패'}")
        return ok

    # -------------------------------------------------------------------
    # 조립
    # -------------------------------------------------------------------
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_terrain(M)                                   # ① 경로 (팔 불변)
    if cfg["hazard_planting_bed"]:                     # ② "위험" 축 — 분기 2줄
        build_planting_bed(M)
    else:
        build_bed_flush(M)

    # ③ 단서 — **어느 것도 hazard 분기 안에 있지 않다** (프림 위생 1)
    if cfg["cue_manhole"] or cfg["cue_tree_grate"] or cfg["cue_slab_joint"] \
            or cfg["cue_drainage"]:
        build_ground_kit(M)
    if cfg["cue_tactile"]:
        build_tactile(M)
    if cfg["cue_bollard"]:
        build_bollards(M)
    if cfg["cue_sign"]:
        build_sign(M)
    if cfg["cue_railing"]:
        build_fence(M)
    if cfg["cue_nosing"]:
        build_nosing(M)
    if cfg["cue_road_marking"]:
        build_road_marking(M)
    if cfg["cue_shadow_caster"]:
        build_shadow_casters(M)
    if cfg["cue_scene_dressing"] or KEEP_DRESSING:
        # `KEEP_DRESSING` 은 hazard=False 팔에서 장식을 ON 변환 그대로 유지시킨다.
        #   관목만이 hazard 면(토양면)에 앉는데 `_bed_z()` 가 그 상태를 따르므로
        #   반사실 팔에서는 판석 위에 앉는다 — 프림 집합은 불변이다.
        build_dressing(M)

    if not scene_selfcheck():
        raise SystemExit("sceneN11 self-check 실패")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneN11 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["mall_over"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN11_{ts}.png")
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
    print("sceneN11_ground_pattern — CPU 자기검사 (pxr·GPU 불필요)")
    print("=" * 70)

    # ── ④-a 함정의 정의 — **가장 중요한 검사** ──────────────────────────────
    drop = T["walk_z"] - HZ["soil_z"]
    chk("식재대 함몰이 FA_REALITY §2 9위 밴드(0.05–0.25 m) 안",
        0.05 <= drop <= 0.25, f"{drop:.3f} m")
    chk("**함몰 < gridspec_v1 hazard_depth_m (④-a 함정 성립)**",
        drop < HAZ_DEPTH,
        f"{drop:.3f} < {HAZ_DEPTH:.2f} · 여유 {HAZ_DEPTH - drop:.3f} m "
        "⇒ 라벨러 발자국 `z_off − z_on ≥ 0.30` 이 한 셀도 켜지지 않는다")
    z_min, who = _grid_min_z()
    chk("**격자 안 최저 상면도 임계 미만** (해석적)",
        T["walk_z"] - z_min < HAZ_DEPTH,
        f"최저 {z_min:+.4f} ({who}) · 보행면 대비 {T['walk_z'] - z_min:.4f} m")
    chk("반사실 채움면 = 보행면", abs(HZ["fill_z"] - T["walk_z"]) < 1e-9,
        f"{HZ['fill_z']:+.3f}")
    chk("삼중주 세 문양이 **전부 단차 0 계열** (맨홀 ≤ 10 mm · 격자 4 mm · 이음 2 mm)",
        PARAMS["joint_exp"]["proud"] <= 0.010,
        f"신축이음 proud {PARAMS['joint_exp']['proud'] * 1000:.0f} mm · "
        "수목격자 4 mm · 맨홀 0.6–10 mm — 셋 다 법7(기하 불변) 안")
    chk("토양층 하부가 실제 프림 (VG-void 개방 바닥 금지)",
        HZ["soil_bot"] < HZ["soil_z"] - 0.20,
        f"토양 하부 {HZ['soil_bot']:+.2f} < 토양면 {HZ['soil_z']:+.2f}")

    # ── 식재 여백 규칙 — 함몰을 실측할 수 있는 창이 남아 있는가 ──────────────
    bs = PARAMS["dress"]["bed_shrub"]
    m_lo, m_hi = bs["y0"] - HZ["y0"], HZ["y1"] - bs["y1"]
    chk("**식재대 맨흙 여백 ≥ 0.25 m 씩** (라벨러가 0.150 m 를 실측하는 창)",
        m_lo >= 0.25 and m_hi >= 0.25,
        f"남 {m_lo:.2f} m · 북 {m_hi:.2f} m · 여백 셀 폭 "
        f"{m_lo / 0.05:.0f}·{m_hi / 0.05:.0f} (높이맵 피치 0.05 m)")

    # ── D78 축방향 스텝 게이트 사각 — 이 씬에서는 발동하지 않는다 ────────────
    d_reach = -GRID["x0"] + math.sqrt(3.0) * HZ["y0"]
    print(f"  [info] D78 축방향 사각 한계 d ≤ −x₀ + √3·y_bed = {d_reach:.2f} m "
          f"(base 밴드 상한 12.0 m). **발동하지 않는다** — 발자국이 스텝 게이트 "
          "이전에 이미 비어 있다(`cells_raw = 0`, 카메라 무관량).")

    # ── 횡단면 연속성 · void ────────────────────────────────────────────────
    bk = T["bed_kerb"]
    segs = [(-T["y_far"], T["front_s"]["y1"]),
            (T["furnish"]["y0"], T["furnish"]["y1"]),
            (-T["mall"]["y_half"], T["mall"]["y_half"]),
            (bk["y0"], bk["y0"] + bk["w"]),
            (HZ["y0"], HZ["y1"]),
            (bk["y1"] - bk["w"], bk["y1"]),
            (T["front_n"]["y0"], T["y_far"])]
    cover_hi, gap = -T["y_far"], []
    for a, b in sorted(segs):
        if a > cover_hi + 1e-6:
            gap.append((round(cover_hi, 3), round(a, 3)))
        cover_hi = max(cover_hi, b)
    chk("VG-void 횡단면 커버리지 (개방 바닥 0)", not gap and cover_hi >= T["y_far"],
        f"공백 {gap}" if gap else "커버리지 1.0")

    # ── L10 성립 조건 — 보행로 위 수직 부재 0 ───────────────────────────────
    yh = T["mall"]["y_half"]
    b = PARAMS["bollard"]
    s = PARAMS["sign"]
    chk("**볼라드 2열이 전부 격자(x ∈ [−2, 14]) 밖** — 보행로 위 수직 부재 0 (L10 조건)",
        all(bx < GRID["x0"] or bx > GRID["x1"] for bx in b["xs"]),
        f"볼라드 x {b['xs']} · 격자 [{GRID['x0']:+.2f}, {GRID['x1']:+.2f}]")
    chk("**동측 진입부 세트가 카메라 전방** — R0 의 '켜져 있으나 화면에 없는 단서' 수리",
        max(b["xs"]) > 0 and PARAMS["sign"]["x"] > 0
        and max(bd[2] for bd in PARAMS["tactile"]["bands"]) > 0,
        f"볼라드 동열 x {max(b['xs']):+.2f} · 표지 x {PARAMS['sign']['x']:+.2f} · "
        f"점형블록 동측 x {max(bd[2] for bd in PARAMS['tactile']['bands']):+.2f}")
    chk("규제표지가 보행로 유효폭 밖", abs(s["y"]) > yh,
        f"표지 y {s['y']:+.2f} · 유효폭 반폭 {yh:.2f}")
    for i, (bx, by, _yaw) in enumerate(PARAMS["dress"]["benches"]):
        chk(f"벤치 {i} 가 보행로 유효폭 밖", abs(by) > yh,
            f"y {by:+.2f} · 반폭 {yh:.2f}")

    # ── 단서 배치 규율 ──────────────────────────────────────────────────────
    pitches = [round(b["ys"][i + 1] - b["ys"][i], 4) for i in range(len(b["ys"]) - 1)]
    chk("볼라드 피치 1.50 m 법정치 (중앙 개구 1건 제외) [행안부 볼라드 설치기준]",
        sorted(pitches) == sorted([1.50] * (len(pitches) - 1) + [b["gap"]]),
        f"{pitches} · 중앙 개구 {b['gap']:.2f} m 는 선언된 예외")
    chk("**볼라드가 카메라 데이텀 스트립 밖** (VG-datum·VG-10 보호)",
        all(abs(y) - b["r"] > DATUM_STRIP["y1"] for y in b["ys"]),
        f"최근접 |y| {min(abs(y) for y in b['ys']):.2f} − r {b['r']:.3f} > "
        f"스트립 반폭 {DATUM_STRIP['y1']:.2f}")
    chk("볼라드 h 0.80–1.00 · φ 0.10–0.20",
        0.80 <= b["h"] <= 1.00 and 0.10 <= 2 * b["r"] <= 0.20,
        f"h {b['h']} · φ {2 * b['r']:.2f}")
    tb = PARAMS["tactile"]["bands"]
    chk("**점형(경고) 밴드는 정확히 1개** [D82 ⓐ 위험 경계 전 점형 1밴드]",
        len(tb) == 1, f"{len(tb)}밴드")
    chk("점형 밴드 깊이 0.30 m = 1유닛 [교통약자법 별표1 §2.5 KS 급 · 표준 60 cm 미달 — 기록]",
        abs(tb[0][2] - tb[0][0] - 0.30) < 1e-6, f"{tb[0][2] - tb[0][0]:.2f} m")
    chk("점형 밴드가 볼라드 열 앞 **0.30 m** [보행안전법 시행규칙 별표1 10호 바]",
        abs((min(b["xs"]) - tb[0][2]) - 0.30) < 1e-6,
        f"이격 {min(b['xs']) - tb[0][2]:.2f} m · 블록 동단 {tb[0][2]:+.2f} · "
        f"볼라드 x {min(b['xs']):+.2f}")
    chk("**선형(유도) 블록 0개** [D82 부가 — 규정 미적용 시점에 규정 시설물 강요 금지]",
        "guide" not in PARAMS["tactile"],
        "이 씬에는 유도가 필요한 분기·대기 지점이 없다")
    a_t = (tb[0][2] - tb[0][0]) * (tb[0][3] - tb[0][1])
    chk("**cue-extent — 점자블록 총면적이 위험 씬 밴드 안** [D82 ⓒ 밀도 대칭]",
        1.0 <= a_t <= 9.0,
        f"점형 **{a_t:.2f} m²** vs 위험 씬 실측 H3 1.08 · H7 1.28 · L1 4.08 · "
        "H2 7.20 · H1 8.72 m² (sceneN9 는 1.51)")
    tr = PARAMS["shadow"]["trees"]
    tpit = [round(tr[i + 1][0] - tr[i][0], 4) for i in range(len(tr) - 1)]
    chk("가로수 피치 6~8 m 법정 밴드 [조례 제7조1가]",
        all(6.0 <= p <= 8.0 for p in tpit), f"{tpit}")
    # **수관 AABB × 데이텀 스트립 = 0** — VG-datum·VG-10 을 동시에 지키는 규율
    CANOPY_R = 3.2
    chk("**수관 AABB 가 카메라 데이텀 스트립에 닿지 않는다** (보수적 반경 3.2 m)",
        all(ty + CANOPY_R < DATUM_STRIP["y0"] for _tx, ty in tr),
        f"수관 y_max {max(ty for _tx, ty in tr) + CANOPY_R:+.2f} < 스트립 남단 "
        f"{DATUM_STRIP['y0']:+.2f} (여유 "
        f"{DATUM_STRIP['y0'] - (max(ty for _tx, ty in tr) + CANOPY_R):.2f} m)")
    gt_side = 1.44
    fu = T["furnish"]
    chk("수목보호격자가 시설물대 안",
        all(fu["y0"] <= gy - gt_side / 2 and gy + gt_side / 2 <= fu["y1"]
            for _gx, gy in PARAMS["gkit"]["tree_grates"]),
        f"격자 반폭 {gt_side / 2:.2f} · 시설물대 폭 {fu['y1'] - fu['y0']:.2f} m")
    je = PARAMS["joint_exp"]
    jp = [round(je["xs"][i + 1] - je["xs"][i], 4) for i in range(len(je["xs"]) - 1)]
    chk("신축이음 12 m 리듬 [FA_REALITY §1.3 C4 · 12~20 m]",
        all(12.0 <= p <= 20.0 for p in jp), f"{jp}")
    chk("신축이음이 격자 안에 **2줄 이상** (한 프레임 삼중주의 ③ 공급)",
        len([x for x in je["xs"] if GRID["x0"] <= x <= GRID["x1"]]) >= 2,
        f"격자 안 신축이음 x = {[x for x in je['xs'] if GRID['x0'] <= x <= GRID['x1']]}")
    mh = PARAMS["gkit"]["mall_manholes"]
    chk("맨홀 3개가 전부 격자 안 (삼중주 ① 공급)",
        all(GRID["x0"] <= mx <= GRID["x1"] and GRID["y0"] <= my <= GRID["y1"]
            for mx, my in mh), f"{mh}")

    # ── 데이텀 ──────────────────────────────────────────────────────────────
    ds = DATUM_STRIP
    cross = [z for z in GATED_ZONES
             if not (z[3] <= ds["x0"] or z[2] >= ds["x1"]
                     or z[5] <= ds["y0"] or z[4] >= ds["y1"])]
    dfail = [(z[0], z[6]) for z in cross if z[6] > DATUM_TOL]
    dtol = [(z[0], z[6]) for z in cross if z[6] <= DATUM_TOL]
    chk("VG-datum 선언 검사 (datum_fail 0)", not dfail,
        f"datum_tol {dtol} · datum_fail {dfail}")

    # ── 삼중주 도달성 — §12-5 k 게이트의 사전 예측 ──────────────────────────
    v = _trio_visibility_mc(n=900, seed=37)
    print("  [info] 삼중주 격자 도달성 MC 900포즈 — "
          + " · ".join(f"{k} 포즈 {r['frac']:.3f} / 프레임당 {r['cells']:.2f}셀"
                       for k, r in v["per"].items()))
    print(f"         **셋이 동시에 잡히는 포즈 {v['any3']:.3f}** "
          "(계획 §2.4 '한 프레임에 서로 다른 세 종류 FA')")
    chk("삼중주 각각이 base 밴드 과반 포즈에서 격자 안에 있다",
        all(r["frac"] >= 0.50 for r in v["per"].values()),
        " · ".join(f"{k} {r['frac']:.3f}" for k, r in v["per"].items()))
    chk("셋이 **동시에** 잡히는 포즈가 1/3 이상",
        v["any3"] >= 0.33, f"{v['any3']:.3f} ≥ 0.33")

    # ── 표준 장비 ───────────────────────────────────────────────────────────
    chk("표준 장비 16키", len(SCENE_CONFIG) == 16, f"{len(SCENE_CONFIG)}키")
    declared = set(CUE_CLASS) - {"_structural"}
    cue_keys = {k for k in SCENE_CONFIG if k.startswith("cue_")}
    chk("CUE_CLASS 가 모든 cue_* 를 분류", declared == cue_keys,
        f"미분류 {sorted(cue_keys - declared)} · 초과 {sorted(declared - cue_keys)}")
    chk("hazard_* 키가 정확히 1개", len([k for k in SCENE_CONFIG
                                         if k.startswith("hazard_")]) == 1)

    print(f"\n  ⇒ sceneN11 CPU 자기검사 {'통과' if ok else '실패'}")
    print("=" * 70)
    return ok


if __name__ == "__main__":
    main()
