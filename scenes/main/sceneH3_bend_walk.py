# -*- coding: utf-8 -*-
"""
sceneH3_bend_walk.py — NegObs 신규 씬 H3: 석축 골목 보도의 굴절부 + 둔치 진입 계단 (Isaac Sim 4.5)

계열    : **복도 굴절형 자기가림 (paired-H)** · 생활권 = **보도**
정본    : `experiments/v3_0823/RENDER_PLAN_V3.md` §2.0(공통 표준) · §2.1 표 `sceneH3_bend_walk`
          · §2.6(CUE_CLASS 사전 분류) · §3.1–3.2(test-ext 사양 · paired-H 회계)
분리    : **test-ext** — v2·v3 **양 모델 모두 미학습**. 훈련·검증에 절대 넣지 않는다(§3.1).
          **4팔 전부 제작 의무**(DZ §4.2 `:243`) — A·B·C·D 완비.
밴드    : base · **H**  (씬당 팔당 48컷 · 4팔 합 192)
승계    : `scene_common.py` · `ground_kit.py`(P5 alley_concrete) · `props_kit`
          선행 빌더 런 2건의 확정 교훈을 **설계 입력**으로 받았다 —
          ⓐ SCENE_H67_BUILD §3.2 굴절형은 **평면 문제 하나**로 닫힌다(H7 실측 strict-H 0.875)
          ⓑ SCENE_TEXT_BUILD §6 「법칙 2」 낙차 종단면에 접하는 구조물의 상면은 반사실
             채움면보다 **높아야** 한다(H2 의 기단 사고) — 이 씬의 WallE·Flank 가 그 대상이다
          ⓒ SCENE_TEXT_BUILD §9 VG 게이트는 **발자국 안 / 격자 안 / 포즈 단위**로 센다

────────────────────────────────────────────────────────────────────────────
**부지 분리 선언 (§2.1 각주 · §12-9 무대 순도)**

계획 §2.1 은 *"H1–H4 는 test-ext, H5 는 train, H6·H7 은 val 이며 **부지·드레싱·재질을
공유하지 않는다**"* 를 명령한다. 같은 **복도 굴절형** 계열의 val 공급원
`sceneH7_bend_walk2` 와의 분리는 다음 9개 축에서 **구성상** 확보된다:

| 축 | sceneH7 (val) | **sceneH3 (test-ext)** |
|---|---|---|
| 부지 | 성토 절토부 콘크리트 옹벽 회랑 → **지하보도** | **구릉 주거지 석축 골목** → **하천 둔치 진입 계단** |
| 굴절 방향 | 남향(−y) 직각 | **북향(+y) 직각** — 평면 문제의 부호가 반대다 |
| 유효폭 | 3.40 m | **2.80 m** (골목 보도) |
| 가림체 재질 | 콘크리트 옹벽(`concrete_wall`) | **자연석 석축**(`rock_wall`) |
| 반대편 벽 | 콘크리트 옹벽 | **붉은 벽돌 담장**(`brick_red`) — 비대칭 |
| 포장 | 인터로킹 200×100(`paving_interlock`) | **콘크리트 타설 + 수축줄눈**(`concrete_floor`) |
| 계단참 재질전이 | 화강석 판석(`plaza_light`) | **판석 포장**(`stone_flag`) |
| 계단 | 12단 × R 0.17 · T 0.32 = 2.04 m | **10단 × R 0.18 · T 0.30 = 1.80 m** |
| 종단 단차 | 2단 × 0.17 | **3단 × 0.15** |
| 표지 | 지하보도 유도(`sign_underpass`) | **하천 둔치 안내**(`sign_info`) |
| 16번째 키 | `cue_level_handrail` (L7) | **`cue_convex_mirror`** (L12) — §4 참조 |
| 계절 톤 | 여름 | **늦봄** (잔디 0.40/0.53/0.26) |

────────────────────────────────────────────────────────────────────────────
씬 조립 공식 (4요소 — 브리프 §2.0)
  ① 경로   석축·담장 사이 골목 보도(유효폭 2.80 m) → 종단 3단 단차 → **굴절부 계단참**
  ② 위험   굴절 너머 **하행 계단 10단 × 0.18 = 1.80 m** → 하천 둔치 통로
  ③ 단서   벽면 계단 손잡이 · 점형블록 · 계단코 나이징 · 바닥 재질전이 · 둔치 안내표지 ·
           **굴절부 볼록거울** · 석축 위 가로수 그림자 · 맨홀 · 줄눈 · 측구 · 볼라드
  ④ 은닉   **BendWall** — 북측 석축이 (−0.85, +1.40)에서 직각으로 꺾여 계단실 서측벽이 된다.
           그 **수직 모서리**가 낙차 전체를 그림자 안에 넣는다. 굴절을 돌기 전에는 계단이 없다.

*"주변 환경은 장식이 아니라 단서 ③ 그 자체다"* — 계단만 덩그러니 만들면 이 씬은 실패다.

────────────────────────────────────────────────────────────────────────────
좌표계 · 평면 (walk axis = +X, Z-up, m. 카메라는 x = −d, |y| ≤ 0.90 에서 +X 를 본다)

                      y
        +9.60 ┌──────────────┬──────────────┬────────┐
              │              │  **하행      │        │
              │  BendWall    │   계단**     │ WallE  │  BankE z=+1.95
        +5.60 │   /Flank     │  10단×0.18   │ (top   │
              │  (top +2.55) ├──────────────┤ +2.55) │
        +2.60 │              │  계단참      │        │
        +2.12 ├──────────────┤  Landing     │        │
        +1.40 │ BendWall/Along (top +2.55)  │        │
              │······ 보도 유효폭 2.80 ·····│ z=0.00 │
         0.00 │            z = 0.00         │        │
        −1.40 ├─────────────────────────────┴────────┤
        −2.12 └──────── WallS (붉은 벽돌 담장, top +2.55) ┘  BankS z=+1.95
              x: −24.0        −1.57  −0.85       +2.05  +2.77   +14.6

  종단(보도 축): x ≤ −8.60 → z=+0.45 · x −8.60…−7.70 → 3단(라이즈 0.15) · x ≥ −7.70 → z=0.00
  낙차 = 0.00 − (−1.80) = **1.800 m** (10단 × 라이즈 0.18 · 트레드 0.30 · 폭 2.90 m)

────────────────────────────────────────────────────────────────────────────
H 수율 설계 — 굴절 은닉의 **닫힌 판정식** (§3.2)

석축 두 몸체(Along: y ∈ [+1.40,+2.12]·x ≤ −0.85 / Flank: x ∈ [−1.57,−0.85]·y ≥ +1.40)는
(−0.85, +1.40) 에서 만나는 L자 솔리드다. 눈 E = (−d, y_c) 에서 낙차점 T = (tx, ty) 로 가는
선분은 **두 경계선(y = +1.40 · x = −0.85)을 반드시 순서대로 지난다.**

      t_y = (y_c − 1.40) / (y_c − ty)      ← 선분이 y = +1.40 에 닿는 매개변수
      t_x = (−0.85 + d) / (tx + d)         ← 선분이 x = −0.85 에 닿는 매개변수

      **은닉 ⇔ t_y ≤ t_x**   (y 경계를 먼저 지나면 그때 x < −0.85 이므로 Along 솔리드 안이다)

최악 T = 발자국 중 **tx 최대 · ty 최소**(= 벽면에 가장 가까운 점) = (**+2.05, +2.90**)
   (계단 2단째 상면 −0.36 이 hazard_depth 0.30 을 처음 넘는다 ⇒ n_free = ⌈0.30/0.18⌉ − 1 = 1)

    y_c      은닉 성립 최소 d          비고
   −0.90        5.30                  낙차 반대쪽 오프셋 = 가장 안 가려짐
    0.00        3.56                  중앙
   +0.90        1.82                  낙차쪽 오프셋 = 더 잘 가려짐

**H7 과 부호가 반대다** — H7 은 남향 굴절이라 y_c = −0.90 이 가장 잘 가려졌다. 같은 계열
안에서 두 씬이 서로 **거울상 실패 모드**를 갖는다는 것이 §2.1 의 "다른 부지" 요구의 실질이다.

수직 방향은 **항상** 막힌다: 최대 눈높이 = z_up 0.45 + h_max 1.90 = **2.35 m** < 석축 마루 2.55 m.
따라서 이 씬의 H 판정은 **평면 문제 하나**로 닫힌다.

수율은 `_yield_mc()` 가 **실제 샘플러**(d LogU · h U · y trunc-N(0,0.35,±0.90) ·
yaw trunc-N(0,8,±20))로 몬테카를로 적분하고 폴라 격자 포함(±31.1°·반경 12 m)까지 함께 본다.
CPU 자기검사가 그 수치를 매 실행 인쇄하므로 평면을 만지면 즉시 드러난다.

**모서리 소속 게이트(VG-06) 적합성**: H 프레임에서 가시 지면(보도·계단참)의 북측 종단선은
**BendWall 모서리에서 뻗어 나온 그림자 경계선**이며, 그 선에 접한 픽셀은 ID 마스크에서
`…/BendWall/…` 이다. 낙차 림(계단 상단)과 계단 내부는 전부 그 선 너머에 있어 **0 px** 기여한다.
`BendWall` 은 **`hazard_*` 밖**에서 지어지므로 B팔에서도 불변이다(브리프 명시 요구).

**SCENE_TEXT_BUILD §6 「법칙 2」 준수**: 낙차의 종단 평면에 접하는 구조물(Flank·WallE)의
상면(+2.55)은 반사실 채움면(0.00)보다 **2.55 m 높다**. H2 에서 셀을 발자국으로 뒤집었던
"채움면보다 낮은 기단"이 이 씬에는 **구성상 존재할 수 없다**(자기검사 (6) 하드 체크).

────────────────────────────────────────────────────────────────────────────
프림 위생 · 데이텀 (CUE_COVERAGE §4-4 (2)(3)(4))

1. 단서 빌더가 `if cfg["hazard_*"]` 안에 있는 것은 **0개**. 조립부의 hazard 분기는 2줄뿐이다.
2. 낙차를 지지하는 구조물(석축 3매·담장 1매·성토 3매·계단참)은 **전부 hazard 밖**이다.
   hazard 토글이 움직이는 것은 **계단 10단 + 하부 슬래브**뿐이고 그 반대편이 `FlatFill/Slot` 이다.
3. `cue_railing`(벽면 계단 손잡이)은 A팔에서 계단 경사를, C·D팔에서 수평(z=0.90)을 따른다 —
   **양팔 모두에 존재**하므로 VG-03(단서 마스크 불변)이 성립한다. 평지 통로에 수평 손잡이가
   서는 것은 편의증진법 시행령 별표2 가 **의무화**하는 실제 구성이다.
   `cue_nosing` 도 같은 이유로 **보도 종단 3단 단차**(팔 불변 지형)에 먼저 놓인다.
4. 카메라 데이텀 스트립 `x ∈ [−12.05, −1.15] · |y| ≤ 0.95` 안에 토글 프림 **datum_fail 0건**.
5. **void 커버리지 1.0** — 슬롯은 계단 10단 + 하부 슬래브가, 그 밖은 보도·석축·담장·성토가
   x ∈ [−2, 14] × y ∈ [−8, 8] 을 빈틈없이 덮는다. 개방 바닥 0.

표준법: 법1 온전 상태만 · 법2 법정 제식 표지(둔치 안내) 1매 · 법4 손잡이·볼록거울·측구·볼라드는
기능 필수 · 법5 차량·계절소품 0 · 법6 신규 재질 역할 0 · 법7 `cue_*` 최대 융기 12 mm ·
법8 수치 주석에 근거 태그.

실행
    unset PYTHONPATH VIRTUAL_ENV; conda activate env_isaaclab; export PYTHONNOUSERSITE=1
    python scenes/main/sceneH3_bend_walk.py                 # GUI 룩체크
    NEGOBS_SMOKE=1 python scenes/main/sceneH3_bend_walk.py  # CPU 조립 스모크(부팅 전 종료)
데이터 렌더 진입점 (신설 씬은 AZ 원장 등재 전까지 이 경로가 유일 — CUE_COVERAGE §4-4 (6)):
    python experiments/v3_0823/code/h67_probe.py --scene sceneH3 --run <stamp> ...
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk
import infra_kit as ik


# [계획 §2.0] 생활권 = 보도. 계절은 **늦봄** — val 공급원 sceneH7(여름)과 톤을 분리한다.
SEASON = "late_spring"


# ===========================================================================
# [A0] CUE_CLASS — 렌더 **전** 사전 분류 (RENDER_PLAN_V3 §2.6 / ACCOUNTING §2-6)
# ===========================================================================
#   렌더 후 VG-01/VG-02 가 이 선언을 **기계 반증**한다. 선언과 실측이 어긋나면 그 씬은
#   **씬 결함**으로 반려하며, 결과를 보고 이 표를 고치지 않는다.
CUE_CLASS = {
    "cue_railing":          "decorative",  # 벽면 계단 손잡이 — 낙차는 계단 솔리드가 정의한다
    "cue_convex_mirror":    "decorative",  # **FA_REALITY L12 ★5** — 굴절부 볼록거울 (§4)
    "cue_tactile":          "decorative",  # 계단 상단 점형블록 (계단참 위, proud 4 mm)
    "cue_nosing":           "decorative",  # 나이징 12 mm — 종단 3단 + 계단 10단
    "cue_material_break":   "decorative",  # **재질 재바인딩 전용** — 프림 집합 불변
    "cue_sign":             "decorative",  # 하천 둔치 안내표지 1매 (WallE 벽면)
    "cue_scene_dressing":   "decorative",  # 담장 너머 관목·벤치·원경 주택동
    "cue_shadow_caster":    "decorative",  # 석축 위 가로수 열 — 그림자 밴드 캐스터
    "cue_manhole":          "decorative",  # 골목 맨홀 (flush)
    "cue_tree_grate":       "decorative",  # 수목보호격자 (flush) — 이 부지는 기본 OFF(법4)
    "cue_slab_joint":       "decorative",  # 콘크리트 수축줄눈 (flush)
    "cue_drainage":         "decorative",  # 횡배수 트렌치(복개) + 빗물받이 (flush)
    "cue_bollard":          "decorative",  # 골목 진입 볼라드 2본
    # ── 토글 금지 목록 (구조물). 어떤 cue_* 도 이 프림들을 참조하지 않는다 ────────────
    "_structural":          ["BendWall", "WallS", "WallE", "Bank",
                             "Walk/Landing", "Walk/Step"],
}


# ===========================================================================
# [A] SCENE_CONFIG — **표준 장비 16키** (RENDER_PLAN_V3 §2.0 · CUE_COVERAGE §4-4 (1))
# ===========================================================================
#   구성: 공통 cue 6 + v3 신설 3 + FA_REALITY §2/§3 승격 후보 4
#   (`cue_slab_joint` 갭 5위 · `cue_drainage` 갭 3위 · `cue_bollard` L2 ·
#    `cue_convex_mirror` L12) + hazard 1 + 팔 제어 2 = **16**. **사문 0.**
SCENE_CONFIG = {
    # ── ② 위험: 유일한 기하 토글 ────────────────────────────────────────────
    #   False → 계단 10단 + 하부 슬래브가 사라지고 계단참 레벨(z 0.00)의 평탄 지면이
    #   슬롯 x ∈ [−0.85, 2.05] · y ∈ [2.60, 9.60] 을 채운다(반사실 보행 가능면).
    "hazard_stairs":       True,
    # ── ③ 단서: 공통 6키 ────────────────────────────────────────────────────
    "cue_railing":         True,   # 벽면 계단 손잡이 2줄 (A팔 경사 / C팔 수평)
    "cue_tactile":         True,   # 계단 상단 점형블록 (교통약자법 시행규칙 별표2)
    "cue_nosing":          True,   # 논슬립 나이징 — 종단 3단 + 계단 10단
    "cue_material_break":  True,   # 계단참 = 판석 포장 / 보도 = 콘크리트 타설
    "cue_sign":            True,   # 하천 둔치 안내표지 (법2 — 법정 제식만)
    "cue_scene_dressing":  True,   # 담장 너머 관목·벤치·원경 주택동
    # ── v3 신설 3키 (FA_REALITY §2) ─────────────────────────────────────────
    #   `cue_shadow_caster` 는 **양성 씬인 이 씬에도** 배치한다(§2.0 역지름길 경보).
    "cue_shadow_caster":   True,
    "cue_manhole":         True,   # 갭 1위 (25.0)
    # 갭 2위. 유효폭 2.80 m 석축 골목에는 가로수를 심지 않는 것이 실제 구성이므로
    #   기본 OFF(법4 "비움이 기본값"). 코드 경로·좌표는 상시 보유하며, 성토 상단
    #   이면도로에 격자를 놓는 어블레이션 팔을 위해 살아 있다.
    "cue_tree_grate":      False,
    # ── FA_REALITY §2/§3 승격 후보 4키 ─────────────────────────────────────
    "cue_slab_joint":      True,   # 갭 5위 — 콘크리트 수축줄눈
    "cue_drainage":        True,   # 갭 3위 — 횡배수 트렌치(복개) + 빗물받이
    "cue_bollard":         True,   # L2 — 골목 진입 볼라드
    "cue_convex_mirror":   True,   # L12 — **굴절부 볼록거울**. §4 가 이 키를 설명한다
    # ── 팔 제어 2키 ─────────────────────────────────────────────────────────
    "keep_dressing":       False,
    "placebo_remove":      False,
}


# ===========================================================================
# [B] PARAMS — 전 수치. 평면도는 파일 상단 표와 **한 글자도 어긋나지 않는다**
# ===========================================================================
PARAMS = dict(
    # ── 보도 회랑 (전부 hazard_* 밖. 4팔 공통) ──────────────────────────────
    walk=dict(
        # [개정 R1] 유효폭 2.80 → **3.60 m**. 사유는 광량이다 — 폭 2.80 m 회랑에 마루
        #   2.55 m 벽 두 매를 세우면 태양 고도 49.79° 에서 그림자 길이가 2.15 m 라
        #   **어느 방위에서도 바닥의 77 % 가 그늘**이고, 1차 스모크가 `dark(<16) 73.1 %`
        #   를 실측했다(정보량이 0 인 프레임 = sceneH1 R3 와 같은 실패 모드).
        #   3.60 m + 마루 2.45 m 면 같은 계산이 **바닥의 59 % 를 볕**으로 만든다.
        y_half=1.80,                       # 유효폭 3.60 m [규격 보도 유효폭 ≥ 2.0 m]
        x0=-24.0, bend_x=-0.85,            # 굴절 모서리 x
        # [개정 R1] z_up 0.45 → 0.30 : 최대 눈높이 0.30 + 1.90 = 2.20 < 마루 2.45 로
        #   수직 폐합을 유지하면서 벽을 0.10 m 낮춘다.
        z_low=0.00, z_up=0.30,
        # [규격] 라이즈 0.10 · 트레드 0.30 — 완경사 3단. H7 의 2단 × 0.17 과 단수·치수가
        #   모두 다르다.
        step=dict(x0=-8.60, riser=0.10, tread=0.30, n=3),
        landing=dict(x0=-0.85, x1=2.05, y0=-2.52, y1=3.20, z=0.00),
    ),
    # ── 석축 3매 + 벽돌 담장 1매 · 성토 3매 (구조물. hazard_* 밖 — 브리프 명시 요구) ──
    wall=dict(
        # [개정 R2] **벽 마루를 비대칭으로 나눈다.** `top` 2.45 는 은닉체(북측 석축·
        #   Flank·WallE) 전용이고, 남측 **벽돌 담장**은 `top_s` 1.95 다.
        #   사유는 다시 광량이다 — R1 후에도 H 밴드 16컷의 `dark(<16)` 중앙값이 **45 %**
        #   였다(최악 77.6 %). 범인은 남측 담장이 만드는 그림자다: 마루 2.45 m · 태양 고도
        #   49.79° · 광선 방위 45° ⇒ 바닥 그림자 경계가 y = −0.34 라 3.60 m 폭 중 1.46 m
        #   가 늘 그늘이고, 낮은 시점(h 0.25~1.0)에서는 그 근거리 그늘이 화면의 대부분을
        #   차지한다. 담장을 1.95 m 로 낮추면 경계가 y = −0.64 로 물러나 볕이 68 % 로 는다.
        #   **은닉 판정에는 영향이 0 이다** — 평면 은닉은 북측 `BendWall` 의 L자 모서리
        #   하나로 닫히고 남측 담장은 그 식에 등장하지 않는다(`_hidden` 참조).
        #   그리고 석축 옹벽 2.45 m + 주택 담장 1.95 m 는 실제 구릉 주거지의 표준 조합이다.
        t=0.72, top=2.45, top_s=1.95, bot=-2.70, cap_t=0.10,
        along=dict(x0=-24.0, x1=-0.85, y0=1.80, y1=2.52),
        flank=dict(x0=-1.57, x1=-0.85, y0=1.80, y1=9.60),
        south=dict(x0=-24.0, x1=2.77, y0=-2.52, y1=-1.80),
        east=dict(x0=2.05, x1=2.77, y0=-2.52, y1=9.60),
    ),
    # 성토 상면 — 북측·동측 +1.95(석축 마루 2.45 보다 0.50 m 낮다) · [개정 R2] 남측은
    #   담장 마루 1.95 보다 낮아야 하므로 **+1.55**. 골목 남측이 한 단 낮은 비탈 주거지다.
    bank=dict(z=1.95, z_s=1.55, base=-2.90,
              south=(-24.0, -9.60, 14.60, -2.52),
              north=(-24.0, 2.52, -1.57, 9.60),
              east=(2.77, -9.60, 14.60, 9.60)),
    # ── ② 위험 (hazard_stairs 전속) ────────────────────────────────────────
    hazard=dict(
        # [개정 R1] `y_head` 2.60 → **3.20**. 회랑이 넓어지면 은닉 경계면(y_face)이
        #   1.40 → 1.80 으로 밀려 평면 은닉이 약해진다(y_c = −0.90 에서 최소 d 가
        #   5.30 → 7.97 로 올라 H 밴드 하한 6 을 넘어선다). 계단 머리를 0.60 m 북쪽으로
        #   물리면 최악점 ty 가 2.90 → 3.50 이 되어 최소 d 가 **5.46** 으로 돌아온다 —
        #   즉 넓힘의 대가를 계단참 깊이로 갚는다. 계단참 5.72 × 2.90 m 는 골목 계단의
        #   실제 계단참 치수대 안이다.
        stair=dict(x0=-0.85, x1=2.05, y_head=3.20, riser=0.18, tread=0.30,
                   n=10, base_z=-2.90),
        lower=dict(x0=-0.85, x1=2.05, y1=9.60, z=-1.80, base_z=-2.90),
        fill=dict(x0=-0.85, x1=2.05, y0=3.20, y1=9.60, z=0.00, base_z=-2.90),
        # [computed] 낙차 = 0.00 − (−1.80) = 1.800 m · 계단 10단 × 0.18
        #   발자국 근단(z_on ≤ −0.30) = 2단째 상면 −0.36 → y = 2.60 + 1·0.30 = 2.90 이
        #   가림 판정의 최악점이다(벽면에 가장 가까운 발자국 셀의 남쪽 경계).
    ),
    # ── ③ 단서 ─────────────────────────────────────────────────────────────
    handrail=dict(z_over=0.90, r=0.023, clear=0.055, bracket=0.055, seg=2),
    # [규격] 손잡이 높이 0.85~0.90 m · 벽 이격 50 mm (편의증진법 시행규칙 별표1)
    tactile=dict(y0=2.30, y1=2.90, x0=-0.75, x1=1.95, proud=0.004),
    # [규격·개정 R4 · D82ⓐ] 점형블록 세로 0.40 → **0.60 m**(0.30 m 유닛 2매) ·
    #   계단 상단(y_head = 3.20)에서 **0.30 m 이격**.
    #   근거 ① 이격 — 「교통약자의 이동편의 증진법 시행규칙」 **별표1**(이동편의시설의
    #     구조·재질 등에 관한 세부기준) "위험장소 **0.3 m 전면**" · 블록 규격 0.3×0.3 m ·
    #     점형 = **경고**(돌출점 36개) / 선형 = **유도**(돌출선 4줄) 역할 구분.
    #   근거 ② 세로폭 — 「도로안전시설 설치 및 관리지침 : 장애인 안전시설」 6.5.2 2)
    #     (= 국도건설공사 설계실무요령 7.5 가 전재): 점형블록 세로폭 **30~90 cm 범위,
    #     60 cm 표준**(0.30 m 유닛 2매). 같은 지침 6.6.7 가 가 더 구체적이다 —
    #     *"보행 동선에서 **위험물과 마주치게 되는 방향에는 60 cm 폭**으로 점형블록을
    #     설치하고, 보행 동선과 **평행한 방향으로는 30 cm 폭**"*. 이 밴드는 접근 동선을
    #     **정면으로 가로지르므로 60 cm** 가 표준값이다.
    #     구 0.40 m 는 300 mm 모듈의 정수배가 아니라 **시공 불가 치수**였다 — 그것이
    #     이 항목의 실제 결함이다. [웹 검증 2026-08-24]
    #   근거 ③ 밴드 수 — 위험 경계 **1곳당 점형 1밴드**(D82 ⓐ). 이 씬은 1밴드다.
    #   [면적] 0.60 × 2.70 = 1.62 m² (구 1.08). 계단참 y0 = −2.52 라 여유 있게 앉는다.
    nosing=dict(width=0.055, proud=0.012),
    # 안내표지는 **WallE 벽면**(막다른 벽)에 붙는다 — 굴절 전 카메라가 정면으로 보는 면이다.
    #   x 2.03 은 데이텀 스트립 동단(−1.15) **밖**이라 VG-datum 과 무관하다.
    sign=dict(x=2.03, y=-0.60, z=1.66, w=0.62, h=0.46),
    # **굴절부 볼록거울** (FA_REALITY L12) — 굴절 **바깥쪽** 벽(담장)에 달아 두 접근 방향이
    #   서로를 본다. 설치 근거는 **시거(視距) 부족**이지 낙차가 아니라는 것이 이 단서의
    #   요점이다(§4).
    # [정정 R4 · D82ⓐ] 구 주석의 "**법정** 안전시설(도로교통법 시행규칙 §8 도로반사경)"은
    #   두 군데가 틀렸다:
    #     ① **법정 의무가 아니다** — 저장소 조사는 *"캐노피·차단기·높이제한바·**볼록거울**은
    #        매우 보편적이나 **법정 의무가 아니다**"* 로 판정했다
    #        [`Docs/surveys/cue_arrangement_survey.md` §1.3 `[추정 — 관행]`].
    #     ② 근거 문서는 도로교통법이 아니라 **「도로안전시설 설치 및 관리지침 — 도로반사경편」**
    #        이다 [`Docs/surveys/cue_expansion_survey_v1.md` `cue_convex_mirror` 행 `[확인]`].
    #   ⇒ **관행 설치**라는 사실이 이 단서를 오히려 더 좋게 만든다: 법정 의무가 아니므로
    #     낙차와의 상관이 제도적으로도 끊겨 있다. [CUE_REGULATION_BASIS §7]
    mirror=dict(x=0.95, y=-1.38, z=2.10, r=0.34, depth=0.10, arm=0.20),
    #   유효폭 2.80 m 골목 입구의 오토바이 진입 억제 2본. 중앙 개구 2.28 m 는
    #   ⓐ 휠체어 유효폭과 ⓑ 카메라 데이텀 스트립(|y| ≤ 0.95) 회피를 동시에 만족시키는
    #   최소 개구이며, 그 대가로 LINT-6 의 피치 1.50 ± 0.10 은 **경고 1건**을 남긴다
    #   (추론 런에 대한 advisory — 하드 규칙이 아니다). 사전 선언된 초과분이다.
    #   위치 지터 없음 — J-3/J-5(07-30) 배치 지터 폐지 · LINT-10 정적 검사 대상.
    bollard=dict(x=-10.50, ys=(-1.20, 1.20), r=0.072, h=0.85,
                 band_z=0.63, band_t=0.09),
    gkit=dict(
        region=(-21.0, -1.76, -1.00, 1.76),
        manholes=[(-5.80, 1.02), (-12.40, -1.02)],
        gullies=[(-3.20, -1.14)],
        # 횡배수 트렌치 1개. x = −5.20 은 `plan_ground` 하드 게이트 B7(GT-E2, 낙차 모서리
        #   근방 대리선 금지)을 통과하는 위치다 — 굴절 모서리(−0.85)에서 4.35 m 로
        #   H7 의 실측 통과 사례(모서리 −1.00 에서 4.00 m)보다 여유가 크다 [측정].
        #   프레임 상면은 포장과 **동일 z**(proud 0.000)이므로 데이텀은 `datum_exact` 유지.
        trench=(-5.20, -1.70, 1.70),
        tree_grates=[(-4.10, -4.20), (-11.10, -4.20)],   # 성토 상단 (기본 OFF)
    ),
    shadow=dict(
        # 석축 반대편(**남측** 담장 위 성토 z=+1.95) 가로수 열 — 마루 위로 수관만 보이고
        #   그 **그림자가 보도 바닥을 가로지른다**. 낙차 방향(북측)이 아니라 남측에 세워,
        #   그림자가 낙차를 가리는 일이 없게 한다(VG-06 모서리 소유가 석축에 남아야 한다).
        #   H7 과 정확히 거울상이다(H7 은 낙차가 남측이라 가로수를 북측에 세웠다).
        #   가로수 열 `bank_S` — 피치 7.0 m (조례 제7조1가 6~8 m) · 1수종(elm) ·
        #   보도 축과 나란한 방위 0° (LINT-3: route bearing = kerb bearing).
        trees=[(-4.10, -4.20), (-11.10, -4.20), (-18.10, -4.20)],
        tree_h=7.2,
        lamps=[(-7.20, -3.05), (-15.40, -3.05)],
        lamp_h=4.4,
    ),
    dress=dict(
        hedge=[(-21.0, 2.60, -3.20, 5.40), (-21.0, -8.10, -3.20, -5.20)],
        shrub_h=0.78,
        # 벤치 2기. 계단참 벤치는 x = +0.90 으로 데이텀 스트립(x ≤ −1.15) **밖**이고,
        #   회랑 벤치는 x = −14.20 으로 스트립 서단(−12.05) **밖**이다 ⇒ 교차 0.
        #   (H7 은 y 로 피했고 이 씬은 x 로 피한다 — 유효폭이 0.60 m 좁기 때문이다.)
        benches=[(0.90, -1.55, 0.0), (-14.20, 1.55, 180.0)],
        bench_w=0.36,
        backdrop=[("B0", 17.0, 28.0, -24.0, -8.0, 12.0),
                  ("B1", 19.0, 31.0, 6.0, 22.0, 16.0)],
    ),

    # ── 재질 3단 (realism_v1_final §84) ─────────────────────────────────────
    #   지면·구조물 = NegObsGround.mdl 경로(텍스처 3매) / 식생·목재 = MDL 상수색 /
    #   금속·도색·사인·유리 = OmniPBR
    material=dict(
        scale=dict(concrete_floor=1.70, stone_flag=1.30, rock_wall=1.60,
                   brick_red=2.00, granite_dark=1.80, grass=1.4, gravel=1.2,
                   tactile=0.3),
        walk_tint=(0.62, 0.615, 0.60),      # 콘크리트 타설 골목 포장
        landing_tint=(0.68, 0.665, 0.64),   # 판석 계단참
        # [개정 R1] 0.44 → 0.50. 그늘진 석축이 1차 스모크에서 사실상 0 으로 렌더됐다
        #   (p50 5/255). look 층 stone 클래스가 alb_max 0.34 로 캡하므로 올려도 상한을
        #   넘지 않는다.
        # [개정 R4 · SCENE_TEXT_BUILD §12-10 (2) R7 레버 발동] 0.54 → **0.62**.
        #   **[실측 후기 — 이 레버는 §12-10 이 가정한 것보다 훨씬 약하다]**
        #   rev_A → reg_A 프림별 화면 평균: `BendWall` 55.93 → 59.91 (+7.1 %) ·
        #   `WallS` 10.84 → 12.13 (+11.9 %) · `Walk` 51.80 → 51.92 (미변경 ✔).
        #   그런데 **프레임 지표는 mean 44.78 → 46.05 (+2.8 %) · dark 58.5 → 58.3 %** 뿐이다.
        #   이유: `dark` 를 지배하는 것은 벽돌 담장이 **12/255** 라는 사실이고, 그것은
        #   알베도가 낮아서가 아니라 폭 3.60 m 회랑에서 **그 면이 빛을 거의 못 받기**
        #   때문이다. 알베도 스케일링은 빛이 안 드는 면을 밝히지 못한다.
        #   ⇒ 잔여 어두움은 **재질로 해결되지 않는다**. 남은 수단은 조명·시점이고 둘 다
        #     코퍼스 규약(L0–L7 고정)에 걸린다 → **R7 사용자 판단 항목으로 재상신**
        #     (REG_AUDIT §7.1). 레버는 발동한 채로 둔다 — 작은 실이익이 있고 `_alb_band`
        #     클램프(stone alb_max 0.34)가 이미 구속하므로 규약을 깨지 않는다.
        #   H 밴드 잔여 어두움(rev_A 16컷 mean 중앙값 **44.8**·dark 중앙값 58.5 %)은
        #   기하 개정 상한 2회를 소진한 뒤에도 남았고, 원인은 마루 1.95~2.45 m 벽 사이
        #   폭 3.60 m 회랑을 눈높이 0.25~1.0 m 에서 보는 계열 고유 조건이다. 기하가 아니라
        #   **재질 한 줄**로 올린다 — look 층 stone alb_max 0.34 캡 아래라 알베도 규약은
        #   깨지지 않는다(순백 대면적 금지와도 무관: 캡 후 0.34 ≪ 0.8).
        rock_tint=(0.62, 0.605, 0.58),      # 자연석 석축 (alb_max 0.34 이하로 look 층이 캡)
        # [개정 R2] 0.50 → 0.60. 그늘진 벽돌 담장이 H 밴드에서 사실상 0 으로 렌더됐다.
        # [개정 R4] 0.60 → **0.70** (동일 R7 레버). 색상비 고정(0.783 · 0.683)으로 곱해
        #   붉은 벽돌의 색조를 유지한 채 명도만 올린다.
        brick_tint=(0.70, 0.548, 0.478),    # 붉은 벽돌 담장
        cap_tint=(0.56, 0.555, 0.54),       # 석축 갓돌(콘크리트)
        stair_tint=(0.57, 0.565, 0.55),     # 화강석 계단
        lower_tint=(0.52, 0.515, 0.50),     # 둔치 통로
        grass_tint=(0.40, 0.53, 0.26),      # 늦봄 (H7 여름 0.42/0.55/0.30 과 다름)
        rail_color=(0.69, 0.70, 0.72), rail_metallic=0.75, rail_rough=0.36,
        nosing_color=(0.41, 0.39, 0.35), nosing_rough=0.70,
        band_color=(0.80, 0.52, 0.05),
        bollard_color=(0.63, 0.63, 0.62), bollard_rough=0.45,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.78, 0.78, 0.75), lamp_rough=0.4,
        # 볼록거울 — 유리면은 금속 반사이되 **순백 대면적 금지**(v5.1 §4)에 걸리지 않도록
        #   알베도를 0.55 대로 두고 면적을 φ0.68 m 로 제한한다.
        mirror_color=(0.55, 0.57, 0.58), mirror_metallic=0.85, mirror_rough=0.10,
        mirror_rim=(0.83, 0.35, 0.06), mirror_rim_rough=0.42,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.030, 0.052, 0.019), canopy_b=(0.040, 0.066, 0.025),
        canopy_rough=1.0,
        backdrop_color=(0.42, 0.415, 0.405), backdrop_rough=0.76,
        iron_color=(0.14, 0.14, 0.15), iron_metallic=0.55, iron_rough=0.62,
    ),

    # ── 조명 (L0–L7 카탈로그. 생산 3종 = L0·L5·L7) ─────────────────────────
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # [개정 R1] 16.0 → **192.0**. `LightingControl` 은 태양 방위를
    #   `sun_rz = noon_dome_rot(−110) + SUN_AZ_OFFSET + hdri_sun_rotz_offset(233.5)`
    #   로 만들고, 광선 진행 방향은 `(−sin θ, +cos θ)·cos(elev)` 다 `[scene_common:4731-4737]`.
    #   16.0 → θ = 139.5° → 광선이 (−x, −y) 로 진행 ⇒ 태양이 **북동쪽**에 서서
    #   ⓐ 은닉체인 북측 석축과 막다른 WallE 를 통째로 그늘에 넣고
    #   ⓑ 남측 가로수 그림자를 보도 **반대쪽**으로 던진다 — 둘 다 설계 의도의 정반대다.
    #   192.0 → θ = 315.5° → 광선이 (+x, +y) 로 진행 ⇒ 태양이 **남서쪽**에 서서
    #   석축·WallE 가 볕을 받고 남측 가로수 그림자가 보도를 가로지른다 `[computed]`.
    SUN_AZ_OFFSET=192.0,

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
    if SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneH3] keep_dressing=True 는 hazard_stairs=False 를 요구한다 — "
            "위험이 켜져 있으면 보존할 것이 없고 그 팔은 A팔의 라벨 없는 복제가 된다.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL sceneH3] keep_dressing=True 와 cue_scene_dressing=False 는 모순이다 — "
            "장식이 바로 이 팔이 보존하려는 대상이다.")
if PLACEBO_REMOVE:
    if not SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneH3] placebo_remove=True 는 hazard_stairs=True 를 요구한다 — "
            "플라시보 팔은 위험 ON 상태의 외형 대조군(D35)이다.")
    if KEEP_DRESSING:
        raise SystemExit(
            "[FATAL sceneH3] placebo_remove 와 keep_dressing 은 서로 다른 팔(P·C)이며 "
            "동시에 설정될 수 없다.")
_ARM = ("C_hz0_cue1" if KEEP_DRESSING else
        "P_hz1_placebo" if PLACEBO_REMOVE else
        "hz%d_rail%d_tac%d_mat%d_dress%d" % (
            int(SCENE_CONFIG["hazard_stairs"]), int(SCENE_CONFIG["cue_railing"]),
            int(SCENE_CONFIG["cue_tactile"]), int(SCENE_CONFIG["cue_material_break"]),
            int(SCENE_CONFIG["cue_scene_dressing"])))
print(f"[sceneH3] arm={_ARM} keep_dressing={KEEP_DRESSING} "
      f"placebo_remove={PLACEBO_REMOVE}")


# ===========================================================================
# [C] 경로 상수 · 필요 텍스처 역할 · 데이텀 선언
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneH3")

ASSET_ROLES = ["concrete_floor", "stone_flag", "rock_wall", "brick_red",
               "granite_dark", "grass", "gravel", "tactile", "sign_info",
               "hdri", "mdl"]

# 카메라 데이텀 스트립 — `variation_kit.sample_camera` 가 뽑는 (d, y) 의 지지집합.
#   d ∈ LogU[1.2, 12] ⇒ x = −d ∈ [−12.00, −1.20] · y ∈ trunc-N(0, 0.35) 잘림 ±0.90.
#   각 방향으로 0.05 m 여유를 더해 [−12.05, −1.15] × [−0.95, 0.95].
DATUM_STRIP = dict(x0=-12.05, x1=-1.15, y0=-0.95, y1=0.95)
DATUM_TOL = 0.02

GATED_ZONES = [
    # (tag, key, x0, x1, y0, y1, dz)  — dz = 지면 위 최대 융기
    ("Stair",        "hazard_stairs",      -0.85,   2.05,   3.20,  6.21, 0.00),
    ("Lower",        "hazard_stairs",      -0.85,   2.05,   6.19,  9.60, 0.00),
    ("FlatFill",     "hazard_stairs(off)", -0.85,   2.05,   3.20,  9.60, 0.00),
    ("Handrail-W",   "cue_railing",        -0.86,  -0.69,   3.20,  6.70, 1.30),
    ("Handrail-E",   "cue_railing",         1.89,   2.06,   3.20,  6.70, 1.30),
    ("Tactile",      "cue_tactile",        -0.75,   1.95,   2.30,  2.90, 0.004),
    # 나이징: 보도 종단 3단(x −8.60…−7.70, 전 폭) + 계단 10단(슬롯 안).
    ("Nosing-Walk",  "cue_nosing",         -8.61,  -7.69,  -1.80,  1.80, 0.012),
    ("Nosing-Stair", "cue_nosing",         -0.85,   2.05,   3.20,  6.20, 0.012),
    ("Sign",         "cue_sign",            1.96,   2.06,  -0.92, -0.28, 2.00),
    # 볼록거울: 담장 벽면(y −1.40) · x = +0.95 → 데이텀 스트립(x ≤ −1.15) **밖**.
    ("Mirror",       "cue_convex_mirror",   0.59,   1.31,  -1.42, -0.98, 2.45),
    ("Bollard-S",    "cue_bollard",       -10.60, -10.40,  -1.28, -1.12, 0.85),
    ("Bollard-N",    "cue_bollard",       -10.60, -10.40,   1.12,  1.28, 0.85),
    ("GKitWalk",     "cue_manhole/slab_joint/drainage",
                                          -21.00,  -1.00,  -1.76,  1.76, 0.008),
    ("TreeGrate",    "cue_tree_grate",    -11.90,  -3.30,  -4.95, -3.45, 0.004),
    ("Shadow",       "cue_shadow_caster", -20.00,  -3.00, -10.00, -2.80, 7.20),
    ("Dress-N",      "cue_scene_dressing", -24.00,  33.00,   2.52, 31.00, 22.0),
    ("Dress-S",      "cue_scene_dressing", -24.00,  33.00, -31.00, -2.52, 22.0),
    # 벤치는 **한 구역으로 묶으면 안 된다** — 두 벤치를 감싸는 최소 상자는 스트립을
    #   통째로 삼켜 `datum_fail` 로 읽힌다(설계 시 CPU 자기검사가 실제로 그렇게 읽었다).
    #   계단참 벤치는 스트립 **동단(−1.15) 밖**, 회랑 벤치는 **서단(−12.05) 밖**이며
    #   그 사실은 각각을 따로 선언해야만 기계가 볼 수 있다.
    ("Dress-BenchLand", "cue_scene_dressing", -0.05,  1.85,  -1.75, -1.35, 0.45),
    ("Dress-BenchCorr", "cue_scene_dressing", -15.15, -13.25,  1.35,  1.75, 0.45),
    ("Dress-Far",    "cue_scene_dressing",  17.00,  33.00, -31.00, 31.00, 22.0),
]


# ===========================================================================
# 은닉 판정 · 수율 모형 — pxr 없이 CPU 로 돈다
# ===========================================================================
def _walk_z(x):
    """보도 축 종단면 z(x). 굴절 이후(x ≥ bend_x)는 계단참 레벨."""
    w = PARAMS["walk"]
    st = w["step"]
    if x <= st["x0"]:
        return w["z_up"]
    if x >= st["x0"] + st["n"] * st["tread"]:
        return w["z_low"]
    i = min(st["n"] - 1, max(0, int((x - st["x0"]) / st["tread"])))
    return w["z_up"] - (i + 1) * st["riser"]


def _footprint_corner():
    """가림 판정의 **최악점** (tx, ty) = 발자국 중 tx 최대 · ty **최소**.

    발자국 = `z_off − z_on ≥ 0.3`. z_off = 0(반사실 평탄), 계단 i단 상면 = −(i+1)·riser.
    ≥ 0.30 을 처음 만족하는 것은 i = 1 (상면 −0.36) 이고, 그 단의 **남쪽 경계**(벽면에
    가장 가까운 쪽)가 y = y_head + n_free·tread 다. 여기서 n_free = ⌈0.30/riser⌉ − 1 = 1.

    H7 은 −y 로 내려가므로 "ty 최대"가 최악점이었다. 이 씬은 +y 로 내려가므로 **부호가
    반대**이고, 그 부호 뒤집힘이 두 씬의 실패 모드를 거울상으로 만든다.
    """
    hz = PARAMS["hazard"]["stair"]
    n_free = max(0, math.ceil(0.30 / hz["riser"]) - 1)
    ty = hz["y_head"] + n_free * hz["tread"]
    return hz["x1"], ty


def _hidden(d, y_c, tx, ty):
    """BendWall L자 솔리드가 (tx, ty) 를 가리는가 — 파일 상단의 닫힌 판정식."""
    w = PARAMS["walk"]
    y_face = PARAMS["wall"]["along"]["y0"]        # +1.40 (회랑쪽 안쪽 면)
    x_corner = w["bend_x"]                        # −0.85
    if ty <= y_face or tx <= x_corner:
        return True                               # 발자국이 아니거나 벽 안쪽
    # 선분 E=(−d, y_c) → T=(tx, ty) 의 매개변수 t ∈ [0,1].
    #   y = y_face 도달:  t_y = (y_c − y_face) / (y_c − ty)
    #   x = x_corner 도달: t_x = (x_corner + d) / (tx + d)
    t_y = (y_c - y_face) / (y_c - ty)
    t_x = (x_corner + d) / (tx + d)
    return t_y <= t_x


def _in_grid(d, y_c, yaw_deg):
    """폴라 격자(±31.1° · 반경 12 m) 안에 발자국 셀이 하나라도 있는가 = `any_pos`."""
    hz = PARAMS["hazard"]
    st, lo = hz["stair"], hz["lower"]
    _, ty0 = _footprint_corner()
    y_foot = st["y_head"] + st["n"] * st["tread"]
    cells = []
    nx = 9
    for i in range(nx):
        tx = st["x0"] + (st["x1"] - st["x0"]) * i / (nx - 1.0)
        yy = ty0
        while yy <= min(lo["y1"], 8.0):
            cells.append((tx, yy))
            yy += 0.5
        cells.append((tx, y_foot))
    ex, ey = -d, y_c
    cy, sy = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    for tx, ty in cells:
        dx, dy = tx - ex, ty - ey
        if math.hypot(dx, dy) >= 12.0:
            continue
        xc, yc2 = dx * cy + dy * sy, -dx * sy + dy * cy
        if abs(math.degrees(math.atan2(yc2, xc))) <= 31.1:
            return True
    return False


def _trunc_norm(rng, mu, sd, lo, hi):
    for _ in range(64):
        v = rng.gauss(mu, sd)
        if lo <= v <= hi:
            return v
    return min(max(rng.gauss(mu, sd), lo), hi)


def _yield_mc(d_lo, d_hi, h_lo, h_hi, n=20000, seed=7):
    """실제 샘플러로 strict-H 성립 비율을 몬테카를로 적분한다.

    반환 (p_H, p_none_in_fov, p_visible). 세 값의 합은 1 이며, 의미는
      p_H              — 발자국이 격자 안 + 전부 가려짐  → strict-H
      p_none_in_fov    — 발자국이 격자 밖               → tier `none_in_fov`
      p_visible        — 격자 안이지만 일부 보임        → V/E/H_weak
    (수직 방향은 석축 마루 2.55 m > 최대 눈높이 2.35 m 이므로 항상 막힌다 — 아래 검산)
    """
    rng = random.Random(seed)
    tx, ty = _footprint_corner()
    nh, nn, nv = 0, 0, 0
    for _ in range(n):
        d = math.exp(rng.uniform(math.log(d_lo), math.log(d_hi)))
        _h = rng.uniform(h_lo, h_hi)                      # 수직은 구속하지 않는다
        y_c = _trunc_norm(rng, 0.0, 0.35, -0.90, 0.90)
        yaw = _trunc_norm(rng, 0.0, 8.0, -20.0, 20.0)
        if not _in_grid(d, y_c, yaw):
            nn += 1
        elif _hidden(d, y_c, tx, ty):
            nh += 1
        else:
            nv += 1
    return nh / n, nn / n, nv / n


# ===========================================================================
# [C''] PLACEMENT — `placement_lint.py` 의 기하 무관 선언 블록 (w3_execution_spec §10.4)
# ===========================================================================
#   프림을 하나도 만들지 않는 순수 선언. 기존 33씬이 0개 선언해 죽어 있던 LINT-1/3/5/9 를
#   신규 씬에서 되살린다.
PLACEMENT = dict(
    # 보행 가능 폭 = 석축 안쪽 면과 담장 안쪽 면 (유효폭 2.80 m)
    walk_edges=[((-21.00, -1.80), (-1.20, -1.80)),
                ((-21.00, 1.80), (-1.20, 1.80))],
    # 골목에는 차도가 없다 — 남측 담장 밑선을 연석선으로 선언한다(가로수 이격 기준).
    kerb_lines=[((-21.00, -1.80), (-1.20, -1.80))],
    anchors={
        "corridor": dict(face_bearing_deg=0.0, props=["Bench_0"]),
        "corridor_back": dict(face_bearing_deg=180.0, props=["Bench_1"]),
        "wall_sign": dict(face_bearing_deg=180.0, props=["Sign.*"]),
    },
    # `pts` 는 **전 그루의 좌표**여야 한다 — LINT-2 는 선언된 폴리라인의 인접 간격을
    #   그대로 피치로 읽는다(양 끝점만 적으면 14 m 로 측정된다).
    routes={
        "bank_S": dict(pts=[(-18.10, -4.20), (-11.10, -4.20), (-4.10, -4.20)],
                       species="elm", pitch_m=7.0),
    },
)


def build_views():
    """카메라 프리셋: grid_views(gy=0, 보행축 +X) + 미장센 4컷."""
    views = sc.grid_views(0.0)
    # bend_low: 보행축 저시점 — **이 씬의 연구 변수**(굴절 모서리가 계단을 삼키는가)
    views["bend_low"] = dict(eye=[-7.0, -0.05, 0.62], tgt=[2.0, 0.5, -0.1])
    # corridor_over: 회랑 전체 — 석축·담장 두 줄과 굴절부의 관계
    views["corridor_over"] = dict(eye=[-11.0, 0.2, 2.10], tgt=[1.4, 0.9, -0.3])
    # stair_reveal: 굴절을 돌아선 시점 — 낙차가 다시 나타나는 지점(H → V 전이)
    views["stair_reveal"] = dict(eye=[-0.1, 1.20, 1.55], tgt=[1.2, 6.2, -1.7])
    # corner_face: BendWall 수직 모서리를 정면으로 — 모서리 소속 게이트의 육안 대응
    views["corner_face"] = dict(eye=[-4.6, -1.30, 1.45], tgt=[-0.6, 2.7, -0.4])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. bend_low (h0.62·d7.0)  — 굴절부 석축 모서리가 하행 계단을 통째로 삼키는가
 2. stair_reveal           — 굴절을 돌면 계단이 나타나는가 (H → V 전이)
 3. corner_face            — 가시 지면 종단선이 **석축 모서리**에서 뻗는가 (VG-06)
 4. corridor_over          — 석축·벽돌담·가로수 그림자 밴드가 골목을 읽히게 하는가
 5. cue ON vs OFF          — 손잡이·점형블록·나이징·볼록거울 토글 시 기하 불변인가
 6. 접지·순백              — 순백(>0.8) 대면적 없음 · 접지 · Z파이팅 없음
 7. props 규율             — 볼라드 중앙 유효폭 개방 · 조형물 0 · 볼록거울 φ0.68"""


def main():
    # [GT-89] SMOKE 게이트 — Isaac 부팅 **전** 조기 종료 (GPU·GUI 미사용).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1" \
            and os.environ.get("NEGOBS_SMOKE_ASSEMBLE", "0") != "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        if not _geometry_selfcheck():
            raise SystemExit("sceneH3 CPU 자기검사 실패")
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
    UsdGeom.Xform.Define(stage, "/World/SceneH3")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    W = PARAMS["walk"]
    WL = PARAMS["wall"]
    BK = PARAMS["bank"]
    HZ = PARAMS["hazard"]
    ROOT = "/World/SceneH3"

    def BOX(path, center, size, mtl=None, col=False, rotZ=0.0):
        return sc.add_box(stage, path, center, size, mtl, collider=col, rotZ=rotZ)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # [VG-void] 타일 이음매 여유 — 인접 슬래브가 **정확히 같은 좌표**에서 맞닿으면
    #   `AabbPrefilter.ground_z` 의 하향 레이가 두 상자의 면을 동시에 스치며 둘 다 놓친다
    #   (sceneH7 스모크에서 계단 이음매 3줄이 정확히 그렇게 찍혀 커버리지 0.9981 [측정]).
    #   4 mm 겹침을 주면 겹친 구간에서 더 높은 상자가 이기므로 경계가 4 mm 이동할 뿐이다
    #   (높이맵 격자 피치 50 mm 의 1/12).
    SEAM = 0.004

    def RECT(path, x0, y0, x1, y1, z_top, base, mtl, col=True, seam=True):
        """축정렬 지면 상자. 회전 상자를 쓰지 않는 이유는 `AabbPrefilter.ground_z`
        (상방 레이 최초 히트)가 회전체의 월드 AABB 를 평면으로 읽기 때문이다 —
        그러면 카메라 배치(`cam.ground_z`)와 높이맵이 동시에 틀린다."""
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
        # 지면·구조물 — 텍스처 3매 (ground 계열)
        M["walk"] = PBR(f"{ROOT}/Looks/ConcretePave",
                        sc.tex_path("concrete_floor", "diff"),
                        sc.tex_path("concrete_floor", "nor"),
                        sc.tex_path("concrete_floor", "rough"),
                        sca["concrete_floor"], tint=mp["walk_tint"])
        M["landing"] = PBR(f"{ROOT}/Looks/StoneFlag",
                           sc.tex_path("stone_flag", "diff"),
                           sc.tex_path("stone_flag", "nor"),
                           sc.tex_path("stone_flag", "rough"),
                           sca["stone_flag"], tint=mp["landing_tint"])
        # [look 층] 재질 프림 이름이 클래스를 정한다 — SCENE_H67_BUILD R3 / SCENE_TEXT_BUILD R1
        #   이 두 번 잡은 함정이다(`RailStone`·`GranitePost` 가 metal 로 분류됐다).
        #   `MasonryStone` 은 stone 클래스(alb_max 0.34)로 떨어진다.
        M["rock"] = PBR(f"{ROOT}/Looks/MasonryStone",
                        sc.tex_path("rock_wall", "diff"),
                        sc.tex_path("rock_wall", "nor"),
                        sc.tex_path("rock_wall", "rough"),
                        sca["rock_wall"], tint=mp["rock_tint"])
        M["brick"] = PBR(f"{ROOT}/Looks/BrickWall",
                         sc.tex_path("brick_red", "diff"),
                         sc.tex_path("brick_red", "nor"),
                         sc.tex_path("brick_red", "rough"),
                         sca["brick_red"], tint=mp["brick_tint"])
        M["cap"] = PBR(f"{ROOT}/Looks/ConcreteCap",
                       sc.tex_path("concrete_floor", "diff"),
                       sc.tex_path("concrete_floor", "nor"),
                       sc.tex_path("concrete_floor", "rough"),
                       sca["concrete_floor"], tint=mp["cap_tint"])
        M["stair"] = PBR(f"{ROOT}/Looks/GraniteStep",
                         sc.tex_path("granite_dark", "diff"),
                         sc.tex_path("granite_dark", "nor"),
                         sc.tex_path("granite_dark", "rough"),
                         sca["granite_dark"], tint=mp["stair_tint"])
        M["lower"] = PBR(f"{ROOT}/Looks/LowerWalk",
                         sc.tex_path("concrete_floor", "diff"),
                         sc.tex_path("concrete_floor", "nor"),
                         sc.tex_path("concrete_floor", "rough"),
                         sca["concrete_floor"], tint=mp["lower_tint"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"),
                         sc.tex_path("grass", "rough"),
                         sca["grass"], tint=mp["grass_tint"])
        M["gravel"] = PBR(f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
                          sc.tex_path("gravel", "nor"),
                          sc.tex_path("gravel", "rough"), sca["gravel"])
        M["tactile"] = sc.tactile_pbr(stage, f"{ROOT}/Looks/Tactile",
                                      scale_m=sca["tactile"])
        # 금속·도색·유리 = OmniPBR
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing", diffuse_color=mp["nosing_color"],
                          roughness_const=mp["nosing_rough"])
        M["band"] = PBR(f"{ROOT}/Looks/GuardBand", diffuse_color=mp["band_color"],
                        roughness_const=0.35)
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           roughness_const=mp["bollard_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["mirror"] = PBR(f"{ROOT}/Looks/MirrorGlass",
                          diffuse_color=mp["mirror_color"],
                          metallic=mp["mirror_metallic"],
                          roughness_const=mp["mirror_rough"])
        M["mirror_rim"] = PBR(f"{ROOT}/Looks/MirrorRim",
                              diffuse_color=mp["mirror_rim"],
                              roughness_const=mp["mirror_rim_rough"])
        M["iron"] = PBR(f"{ROOT}/Looks/Iron", diffuse_color=mp["iron_color"],
                        metallic=mp["iron_metallic"],
                        roughness_const=mp["iron_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA", diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"])
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB", diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"])
        # `Backdrop` 은 look 층에서 misc(무처방 상수색) → `BgConcrete` 로 두면 concrete
        #   클래스가 되어 알베도 상한 0.34 와 텍스처 승격을 받는다 (H6 R4 교훈).
        M["backdrop"] = PBR(f"{ROOT}/Looks/BgConcrete",
                            diffuse_color=mp["backdrop_color"],
                            roughness_const=mp["backdrop_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", sc.tex_path("sign_info", "diff"),
                        uv_mode=True)
        return M

    # -------------------------------------------------------------------
    # ① 경로 + ④ 은닉 — 보도·석축·담장·성토. **전부 hazard_* 밖** (4팔 공통 프림)
    # -------------------------------------------------------------------
    def build_walls(M):
        """석축 3매 + 벽돌 담장 1매 + 갓돌. `BendWall` 두 몸체가 굴절 모서리를 만든다.

        브리프 명시 요구: *"옹벽은 `hazard_*` 밖에 지어 B팔에서도 불변"*.
        `Along` 의 동단 면(x = −0.85)과 `Flank` 의 남단 면(y = +1.40)이 만나는
        **수직 모서리**가 이 씬의 은닉체이자 VG-06 의 모서리 소유자다.
        """
        sc.skin_exclude(f"{ROOT}/BendWall", f"{ROOT}/WallS", f"{ROOT}/WallE")
        for tag, spec, root, mtl, wtop in (
                ("Along", WL["along"], "BendWall", M["rock"], WL["top"]),
                ("Flank", WL["flank"], "BendWall", M["rock"], WL["top"]),
                # [개정 R2] 남측 담장만 마루가 낮다(`top_s`) — 은닉식에 등장하지 않는 벽이다.
                ("Body", WL["south"], "WallS", M["brick"], WL["top_s"]),
                ("Body", WL["east"], "WallE", M["rock"], WL["top"])):
            x0, x1 = spec["x0"], spec["x1"]
            y0, y1 = spec["y0"], spec["y1"]
            top = wtop - WL["cap_t"]
            RECT(f"{ROOT}/{root}/{tag}", x0, y0, x1, y1, top, WL["bot"], mtl)
            # 갓돌 — 양면 20 mm 오버세일(그림자선을 만들어 코핑으로 읽히게)
            RECT(f"{ROOT}/{root}/{tag}Cap", x0 - 0.02, y0 - 0.02, x1 + 0.02,
                 y1 + 0.02, wtop, top, M["cap"])
        print(f"[구조] 석축 3매(마루 {WL['top']:.2f} m) + 벽돌 담장 1매"
              f"(마루 {WL['top_s']:.2f} m) · 굴절 모서리 "
              f"({W['bend_x']:+.2f}, {WL['along']['y0']:+.2f}) · **hazard_* 밖**")

    def build_banks(M):
        """석축·담장이 지지하는 배면 지반(주택지). 상면 +1.95 — 마루보다 0.60 m 낮다."""
        for tag, (x0, y0, x1, y1) in (("S", BK["south"]), ("N", BK["north"]),
                                      ("E", BK["east"])):
            RECT(f"{ROOT}/Bank/{tag}", x0, y0, x1, y1,
                 BK["z_s"] if tag == "S" else BK["z"], BK["base"], M["grass"])

    def build_walk(M):
        """골목 보도 바닥 + 종단 3단 단차 + 굴절부 계단참.

        `cue_material_break` 는 **계단참 슬래브의 재질 재바인딩 전용**이다 —
        프림 집합이 불변이므로 높이맵 비트 동일이 구성상 보증된다.
        """
        st = W["step"]
        ybot, ytop = WL["south"]["y0"], WL["along"]["y1"]   # 벽 몸체까지 덮는다
        RECT(f"{ROOT}/Walk/Upper", W["x0"], ybot, st["x0"], ytop,
             W["z_up"], BK["base"], M["walk"])
        for i in range(st["n"]):
            x0 = st["x0"] + i * st["tread"]
            RECT(f"{ROOT}/Walk/Step_{i}", x0, ybot, x0 + st["tread"], ytop,
                 W["z_up"] - (i + 1) * st["riser"], BK["base"], M["walk"])
        RECT(f"{ROOT}/Walk/Lower", st["x0"] + st["n"] * st["tread"], ybot,
             W["bend_x"], ytop, W["z_low"], BK["base"], M["walk"])
        ld = W["landing"]
        land_mtl = M["landing"] if cfg["cue_material_break"] else M["walk"]
        RECT(f"{ROOT}/Walk/Landing", ld["x0"], ld["y0"], ld["x1"], ld["y1"],
             ld["z"], BK["base"], land_mtl)
        print(f"[cue] material_break={cfg['cue_material_break']} → Landing = "
              f"{'판석 포장(StoneFlag)' if cfg['cue_material_break'] else '콘크리트 타설(ConcretePave)'}"
              " · **프림 집합 불변**(재바인딩 전용) → 높이맵 비트 동일 보증")
        print(f"[구조] 보도 유효폭 {2 * W['y_half']:.2f} m · 종단 {st['n']}단"
              f"(라이즈 {st['riser']}) · 계단참 {ld['x1'] - ld['x0']:.2f} × "
              f"{ld['y1'] - ld['y0']:.2f} m")

    # -------------------------------------------------------------------
    # ② 위험 — hazard_stairs 전속. 여기에는 **단서가 한 개도 없다**(프림 위생 1).
    # -------------------------------------------------------------------
    def build_hazard(M):
        st, lo = HZ["stair"], HZ["lower"]
        sc.skin_exclude(f"{ROOT}/Stair", f"{ROOT}/Lower")
        for i in range(st["n"]):
            y0 = st["y_head"] + i * st["tread"]
            y1 = y0 + st["tread"]
            RECT(f"{ROOT}/Stair/Step_{i:02d}", st["x0"], y0, st["x1"], y1,
                 -(i + 1) * st["riser"], st["base_z"], M["stair"])
        y_foot = st["y_head"] + st["n"] * st["tread"]
        RECT(f"{ROOT}/Lower/Floor", lo["x0"], y_foot, lo["x1"], lo["y1"],
             lo["z"], lo["base_z"], M["lower"])
        print(f"[hazard] 낙차 = {0.0 - lo['z']:.3f} m · 계단 {st['n']}단 × "
              f"라이즈 {st['riser']} · 트레드 {st['tread']} · 둔치 통로 z={lo['z']:+.2f} "
              f"(y {y_foot:+.2f} … {lo['y1']:+.2f})")

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 — 계단참 레벨의 평탄 지면이 슬롯을 채운다.

        이것이 라벨러의 반사실 보행 가능면 z_off 다(footprint v2 = z_off − z_on ≥ 0.3).
        """
        f = HZ["fill"]
        RECT(f"{ROOT}/FlatFill/Slot", f["x0"], f["y0"], f["x1"], f["y1"],
             f["z"], f["base_z"], M["walk"])
        print(f"[hazard] OFF — 반사실 보행 가능면 z_off = {f['z']:+.3f} "
              f"(슬롯 x {f['x0']:+.2f}…{f['x1']:+.2f} · y {f['y0']:+.2f}…{f['y1']:+.2f})")

    # -------------------------------------------------------------------
    # ③ 단서 — **전부 hazard_* 밖의 자립 프림**
    # -------------------------------------------------------------------
    def _stair_rail_z(y):
        """계단 손잡이의 높이 — 노즈 라인 위 `z_over`. 계단이 없으면 수평(C·D팔)."""
        st = HZ["stair"]
        if not cfg["hazard_stairs"]:
            return W["landing"]["z"] + PARAMS["handrail"]["z_over"]
        t = (y - st["y_head"]) / st["tread"]
        t = min(max(t, 0.0), float(st["n"]))
        return -t * st["riser"] + PARAMS["handrail"]["z_over"]

    def build_handrail(M):
        """벽면 계단 손잡이 2줄 (`cue_railing`).

        **hazard 분기 밖에서 호출된다.** A팔에서는 계단 경사를, C·D팔에서는 수평
        (z = 0.90) 을 따른다 — 평지 통로에 수평 손잡이가 서는 것은 편의증진법
        시행령 별표2 가 **의무화**하는 실제 구성이므로 대체물이 아니라 같은 부재의
        같은 용도다. 그래서 이 단서는 **양팔에 모두 존재**하고 VG-03(단서 마스크
        불변)이 성립한다.
        """
        hr = PARAMS["handrail"]
        st = HZ["stair"]
        y_end = st["y_head"] + st["n"] * st["tread"] + 0.40
        n_seg = max(1, int(math.ceil((y_end - st["y_head"])
                                     / (hr["seg"] * st["tread"]))))
        for side, x_face, sgn in (("W", st["x0"], +1.0), ("E", st["x1"], -1.0)):
            x_rail = x_face + sgn * (hr["clear"] + hr["r"])
            for s in range(n_seg):
                ya = st["y_head"] + s * hr["seg"] * st["tread"]
                yb = min(y_end, ya + hr["seg"] * st["tread"])
                za, zb = _stair_rail_z(ya), _stair_rail_z(yb)
                CYL(f"{ROOT}/Handrail{side}/Seg_{s:02d}",
                    (x_rail, 0.5 * (ya + yb), 0.5 * (za + zb)), hr["r"],
                    abs(yb - ya) + 0.02, M["rail"],
                    rotX=90.0 + math.degrees(math.atan2(zb - za, yb - ya)))
                BOX(f"{ROOT}/Handrail{side}/Brk_{s:02d}",
                    (x_face + sgn * hr["bracket"] / 2.0, 0.5 * (ya + yb),
                     0.5 * (za + zb)), (hr["bracket"], 0.05, 0.05), M["rail"])
        print(f"[cue] railing ON — 벽면 계단 손잡이 2줄 × {n_seg}구간 · "
              f"노즈선 위 {hr['z_over']:.2f} m · 벽 이격 {hr['clear'] * 1000:.0f} mm "
              f"[규격 편의증진법 시행규칙 별표1] · "
              f"{'계단 경사' if cfg['hazard_stairs'] else '수평(평지 복도)'} 추종")

    def build_convex_mirror(M):
        """**굴절부 볼록거울** (`cue_convex_mirror`, FA_REALITY L12 ★5).

        왜 **양성 씬**에 심는가 — `cue_shadow_caster` 부작용 경보(계획 §2.0)와 같은
        논리다. 볼록거울은 「도로안전시설 설치 및 관리지침 — 도로반사경편」이 **시거 불량
        구간**을 위해 다루는 시설(법정 의무는 아니고 관행)이고 **낙차와는 아무 상관이
        없다**(FA_REALITY L12 ★5: "볼록거울 = 시거 부족").
        그것을 음성 씬(N12)에만 두면 "볼록거울 = 안전"이라는 **역지름길**이 생긴다.
        이 씬은 **낙차가 있는 굴절부**에 같은 부재를 세워 base rate 독립을 씬 내부에서
        강제한다 — 굴절부에 거울이 서는 이유는 낙차가 아니라 **시거**이기 때문이다.

        위치는 굴절 **바깥쪽** 벽(남측 담장)이다 — 안쪽(석축) 면에 달면 굴절을 돌기 전에는
        보이지 않아 시설의 목적을 잃는다. 실제 시공도 바깥쪽 벽이다.
        """
        mr = PARAMS["mirror"]
        # 브래킷 (담장 면 → 거울 뒤판)
        BOX(f"{ROOT}/Mirror/Arm", (mr["x"], mr["y"] + mr["arm"] / 2.0, mr["z"]),
            (0.06, mr["arm"], 0.06), M["pole"])
        # 거울 뒤판(주황 테) + 반사면 — 법선은 +y(회랑 쪽). `add_disc` 는 회전을 받지
        #   않으므로(Z축 고정 프리즘) `add_cylinder(rotX=90)` 로 축을 y 로 눕힌다.
        CYL(f"{ROOT}/Mirror/Rim",
            (mr["x"], mr["y"] + mr["arm"] + mr["depth"] / 2.0, mr["z"]),
            mr["r"] + 0.035, mr["depth"], M["mirror_rim"], rotX=90.0)
        CYL(f"{ROOT}/Mirror/Face",
            (mr["x"], mr["y"] + mr["arm"] + mr["depth"] * 0.92, mr["z"]),
            mr["r"], 0.022, M["mirror"], rotX=90.0)
        print(f"[cue] convex_mirror ON — 굴절부 도로반사경 φ{2 * mr['r']:.2f} m "
              f"@담장면 ({mr['x']:+.2f},{mr['y']:+.2f},{mr['z']:.2f}) "
              "[근거 도로안전시설 지침 도로반사경편 · **법정 의무 아님(관행)** · "
              "FA_REALITY L12 — **낙차 무관 단서**]")

    def build_tactile(M):
        t = PARAMS["tactile"]
        sc.build_tactile(stage, f"{ROOT}/Tactile", t["x0"], t["x1"],
                         t["y0"], t["y1"], M["tactile"],
                         z=W["landing"]["z"], proud=t["proud"])
        print(f"[cue] tactile ON — **경고 1밴드** 세로 {t['y1'] - t['y0']:.2f} m "
              f"(0.30 m 유닛 {round((t['y1'] - t['y0']) / 0.30)}매) · 계단 상단에서 "
              f"{abs(HZ['stair']['y_head'] - t['y1']):.2f} m 이격 "
              "[규격 교통약자법 시행규칙 별표1 · 국도 실무요령 7.5]")

    def build_nosing(M):
        """논슬립 나이징 — **보도 종단 3단(팔 불변 지형)** + 계단 10단.

        `hazard_stairs` 분기 밖에서 호출되며, 종단 3단 위의 띠는 4팔 전부에 존재한다.
        계단 위의 띠만 위험 기하에 종속되고, 그 사실을 아래 인쇄가 매 팔마다 남긴다.
        """
        ng = PARAMS["nosing"]
        st = W["step"]
        yh = W["y_half"]
        n_walk = 0
        for i in range(st["n"]):
            x1 = st["x0"] + (i + 1) * st["tread"]
            z = W["z_up"] - (i + 1) * st["riser"]
            BOX(f"{ROOT}/NosingWalk/Strip_{i}",
                (x1 - ng["width"] / 2.0, 0.0, z + ng["proud"] / 2.0),
                (ng["width"], 2 * yh, ng["proud"]), M["nosing"])
            n_walk += 1
        n_st = 0
        if cfg["hazard_stairs"]:
            hs = HZ["stair"]
            for i in range(hs["n"]):
                y0 = hs["y_head"] + i * hs["tread"]
                y1 = y0 + hs["tread"]
                BOX(f"{ROOT}/NosingStair/Strip_{i:02d}",
                    (0.5 * (hs["x0"] + hs["x1"]), y1 - ng["width"] / 2.0,
                     -(i + 1) * hs["riser"] + ng["proud"] / 2.0),
                    (hs["x1"] - hs["x0"], ng["width"], ng["proud"]), M["nosing"])
                n_st += 1
        print(f"[cue] nosing ON — 보도 종단 {n_walk}단(팔 불변) + 계단 {n_st}단 · "
              f"proud {ng['proud'] * 1000:.0f} mm [계획 realism_v1_final §84]")

    def build_sign(M):
        """하천 둔치 안내표지 — WallE 벽면(막다른 벽)에 붙는 법정 제식 판(법2)."""
        s = PARAMS["sign"]
        BOX(f"{ROOT}/Sign/Back", (s["x"] + 0.03, s["y"], s["z"]),
            (0.05, s["w"] + 0.04, s["h"] + 0.04), M["iron"])
        BOX(f"{ROOT}/Sign/Panel", (s["x"] + 0.002, s["y"], s["z"]),
            (0.02, s["w"], s["h"]), M["sign"])
        print(f"[cue] sign ON — 하천 둔치 안내표지 1매 @WallE ({s['x']:+.2f},"
              f"{s['y']:+.2f},{s['z']:.2f}) · 임의 문구 0 (법2)")

    def build_bollards(M):
        """골목 진입 볼라드 — 중앙 유효폭을 비운다(휠체어 통행 + VG-datum 동시 충족)."""
        b = PARAMS["bollard"]
        for i, y0 in enumerate(b["ys"]):
            x, y = b["x"], y0
            gz = _walk_z(x)
            # `placement_lint` 의 `props.bollard` 규약: `Bollard_NN` + `/Post` + `/Band`.
            CYL(f"{ROOT}/Bollard_{i:02d}/Post", (x, y, gz + b["h"] / 2.0), b["r"],
                b["h"], M["bollard"])
            CYL(f"{ROOT}/Bollard_{i:02d}/Band", (x, y, gz + b["band_z"]),
                b["r"] + 0.004, b["band_t"], M["band"])
        print(f"[cue] bollard ON — {len(b['ys'])}본 · h {b['h']} m · "
              f"φ{2 * b['r']:.2f} m · 중앙 개구 {abs(b['ys'][1] - b['ys'][0]):.2f} m "
              "[규격 user_feedback_v5_1 §2]")

    def build_ground_kit(M):
        """지면 문양 (`cue_manhole`·`cue_slab_joint`·`cue_drainage`) + `cue_tree_grate`.

        전부 flush(≤ 8 mm)이므로 법7(기하 불변)을 지킨다. 맨홀·빗물받이는 |y| ≥ 1.02 에
        배치해 카메라 데이텀 스트립(|y| ≤ 0.95)과의 교차를 `datum_tol` 안에 가둔다.
        """
        g = PARAMS["gkit"]
        M2 = dict(M)
        M2.update(joint=M["cap"], crack=M["cap"], manhole=M["iron"],
                  gully=M["iron"], gutter=M["cap"], gutter_cover=M["iron"],
                  trench=M["iron"], trench_frame=M["iron"], marking=M["lamp"],
                  weed=M["grass"], wear=M["gravel"], stain_dirt=M["gravel"],
                  stain_water=M["gravel"], patch=M["walk"], patch_cut=M["cap"])
        kit = gk.kit_from_scene_common(sc, stage)
        infra = dict(manhole=len(g["manholes"]) if cfg["cue_manhole"] else 0,
                     gully=len(g["gullies"]) if cfg["cue_drainage"] else 0,
                     gutter_L=0,
                     trench=1 if cfg["cue_drainage"] else 0)
        sites = {}
        if cfg["cue_manhole"]:
            sites["manhole"] = [tuple(v) for v in g["manholes"]]
        if cfg["cue_drainage"]:
            sites["gully"] = [tuple(v) for v in g["gullies"]]
            sites["trench"] = [tuple(g["trench"])]
        gp = gk.plan_ground(
            "alley_concrete", region=tuple(g["region"]), z=W["z_low"], gy=0.0,
            origin=(0.0, 0.0, 0.0), edges=[("bend_corner", W["bend_x"])],
            dists=(2, 5, 10), scene="sceneH3", tactile=(),
            # `surface=None` — 잡초/균열/오염 데칼 OFF. 1차 이유는 법1(손상·노후 금지),
            #   2차 이유는 잡초 프림(proud 최대 0.107 m)이 데이텀 스트립을
            #   `datum_fail` 로 밀 수 있다는 것이다.
            overrides=dict(infra=infra, surface=None), sites=sites, seed=83)
        if not cfg["cue_slab_joint"]:
            gp["ops"] = [o for o in gp["ops"] if o["name"] != "joints"]
            gp["elements"] = [e for e in gp["elements"] if e["kind"] != "joint"]
        res = gk.apply_ground(kit, f"{ROOT}/GKitWalk", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        n_grate = 0
        if cfg["cue_tree_grate"]:
            for i, (gx, gy_) in enumerate(g["tree_grates"]):
                n_grate += _tree_grate(M, f"{ROOT}/TreeGrate_{i}", gx, gy_, BK["z"])
        print(f"[cue] ground pattern — manhole={cfg['cue_manhole']}"
              f"({len(g['manholes'])}) slab_joint={cfg['cue_slab_joint']} "
              f"drainage={cfg['cue_drainage']} tree_grate={cfg['cue_tree_grate']}"
              f"({n_grate} 프림) · gkit 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} m (flush — 법7)")

    def _tree_grate(M, path, cx, cy, z, side=1.44, frame=0.09, bar=0.035,
                    n_bar=9, proud=0.004):
        """수목보호덮개 (flush) — 프레임 + 평행 바. [FA_REALITY §2 2위 · 33씬 전무]"""
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
                    M["gravel"], seg=18)
        return n + 1

    def build_shadow_casters(M):
        """그림자 밴드 캐스터 — 담장 위 성토 상단 가로수 열 + 가로등 (`cue_shadow_caster`).

        **양성 씬에도 동일 비율로**(RENDER_PLAN_V3 §2.0 경보). 전부 **남측**(y ≤ −2.40)에
        세운다 — 북측(낙차쪽)에 세우면 수관 그림자가 계단 쪽을 덮어 VG-06 의 모서리 소유가
        석축에서 수목으로 넘어간다. H7 과 정확히 거울상이다.
        """
        s = PARAMS["shadow"]
        bz = BK["z_s"]                      # [개정 R2] 캐스터는 전부 **남측** 성토 위다
        for i, (tx, ty) in enumerate(s["trees"]):
            sc.build_tree(stage, f"{ROOT}/Shadow/Tree_{i}", tx, ty, bz,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.15, trunk_h=s["tree_h"] * 0.52,
                          canopy_blobs=10, canopy_spread=1.12, species="elm")
        for i, (lx, ly) in enumerate(s["lamps"]):
            CYL(f"{ROOT}/Shadow/LampPole_{i}", (lx, ly, bz + s["lamp_h"] / 2.0),
                0.072, s["lamp_h"], M["pole"])
            BOX(f"{ROOT}/Shadow/LampHead_{i}",
                (lx, ly + 0.55, bz + s["lamp_h"] - 0.08),
                (0.44, 0.20, 0.13), M["lamp"])
            CYL(f"{ROOT}/Shadow/LampArm_{i}",
                (lx, ly + 0.28, bz + s["lamp_h"]), 0.05, 0.62, M["pole"],
                rotX=90.0)
        print(f"[cue] shadow_caster ON — 가로수 {len(s['trees'])}주 + "
              f"가로등 {len(s['lamps'])}주 (전부 남측 성토 상단) · "
              "북측 시선 통로 청소됨")

    def build_dressing(M):
        """③ 단서의 환경 성분 — 성토 상단 관목 띠 · 벤치 · 원경 주택동."""
        d = PARAMS["dress"]
        for i, (x0, y0, x1, y1) in enumerate(d["hedge"]):
            # 0 = 북측 성토(+1.95) · 1 = 남측 성토(+1.55, 개정 R2)
            sc.place_hedge_row(stage, f"{ROOT}/Dress/Hedge_{i}", x0, y0, x1, y1,
                               d["shrub_h"], seed=1830 + i,
                               base_z=BK["z"] if i == 0 else BK["z_s"],
                               fallback_mtl=M["grass"])
        for i, (bx, by, byaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Dress/Bench_{i}", bx, by, _walk_z(bx),
                           M["wood"], yaw=byaw, width=d["bench_w"])
        if not PLACEBO_REMOVE:
            for tag, x0, x1, y0, y1, hgt in d["backdrop"]:
                BOX(f"{ROOT}/Dress/Backdrop_{tag}",
                    ((x0 + x1) / 2.0, (y0 + y1) / 2.0, BK["z"] + hgt / 2.0),
                    (x1 - x0, y1 - y0, hgt), M["backdrop"])
        else:
            print("[placebo] 원경 주택동 물량군 제거 — 위험·단서는 전부 유지(D35 P팔)")
        print(f"[cue] scene_dressing ON — 관목 {len(d['hedge'])}띠 · "
              f"벤치 {len(d['benches'])} · 원경 "
              f"{0 if PLACEBO_REMOVE else len(d['backdrop'])}동")

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
        gated_roots = ("/Stair", "/Lower", "/FlatFill", "/Handrail", "/Mirror",
                       "/Tactile", "/NosingWalk", "/NosingStair", "/Sign",
                       "/Bollard", "/GKitWalk", "/TreeGrate", "/Shadow", "/Dress")
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
            dz = float(mx[2]) - _walk_z(x_ref)
            (tol_hits if dz <= DATUM_TOL else hits).append((p, round(dz, 4)))
        if hits:
            ok = False
        print(f"[selfcheck] (2) 토글 프림 {n_scan}개 전수 AABB → 스트립 교차 "
              f"{len(hits) + len(tol_hits)}건 (datum_tol {len(tol_hits)} · "
              f"datum_fail {len(hits)})"
              + (f" FAIL={hits[:6]}" if hits else " · OK"))

        # (3) VG-void — 슬롯 전역 커버리지
        st, lo = HZ["stair"], HZ["lower"]
        if cfg["hazard_stairs"]:
            y_hi = st["y_head"] + st["n"] * st["tread"]
            gap = abs(lo["z"] - (-(st["n"]) * st["riser"]))
            covered = (y_hi >= 5.59 - 1e-6) and gap < 1e-6 and lo["y1"] >= 9.5
        else:
            covered = (HZ["fill"]["y0"] <= st["y_head"] + 1e-9
                       and HZ["fill"]["y1"] >= 9.5)
        if not covered:
            ok = False
        print(f"[selfcheck] (3) VG-void 슬롯 커버리지 x[{st['x0']:+.2f},"
              f"{st['x1']:+.2f}] y[{st['y_head']:+.2f}, +9.60] → "
              + ("빈틈 0 · 커버리지 1.0 · OK" if covered else "빈틈 발견"))

        # (4) 단서 프림 × 낙차 발자국 교차 — 벽면 손잡이의 선언 초과분만 허용
        _, ty0 = _footprint_corner()
        cue_roots = ("/Handrail", "/Mirror", "/Tactile", "/NosingWalk",
                     "/Sign", "/Bollard", "/GKitWalk", "/TreeGrate", "/Shadow",
                     "/Dress")
        over = []
        for prim in stage.Traverse():
            p = str(prim.GetPath())
            if not p.startswith(ROOT) or not prim.IsA(UsdGeom.Gprim):
                continue
            tail = p[len(ROOT):]
            if not any(tail.startswith(g) for g in cue_roots):
                continue
            try:
                b = bbc.ComputeWorldBound(prim).ComputeAlignedRange()
            except Exception:
                continue
            if b.IsEmpty():
                continue
            mn, mx = b.GetMin(), b.GetMax()
            if (mx[0] > st["x0"] and mn[0] < st["x1"]
                    and mn[1] < 8.0 and mx[1] > ty0):
                over.append((p, round(float(mn[1]), 3), round(float(mx[1]), 3)))
        # 벽면 손잡이는 벽에서 55 mm 이격이 규격이므로 슬롯 위로 최대 0.078 m 나온다.
        #   양측 합쳐 0.16 m / 슬롯 폭 2.90 m = **5.4 %**. 사전 선언된 초과분이다.
        wide = [o for o in over if not o[0].split("/")[-2].startswith("Handrail")]
        if wide:
            ok = False
        print(f"[selfcheck] (4) 단서 × 발자국 교차 {len(over)}건 "
              f"(벽면 손잡이 선언 초과 {len(over) - len(wide)} · 미선언 {len(wide)})"
              + (f" {wide[:4]}" if wide else " · OK"))

        # (5) 은닉 기하 · 수율
        tx, ty = _footprint_corner()
        print(f"[selfcheck] (5) 은닉 최악점 T = ({tx:+.2f}, {ty:+.2f}) · "
              f"굴절 모서리 ({W['bend_x']:+.2f}, {WL['along']['y0']:+.2f}) · "
              f"석축 마루 {WL['top']:.2f} m > 최대 눈높이 "
              f"{W['z_up'] + 1.90:.2f} m → 수직은 항상 폐합")
        for y_c in (-0.90, 0.0, 0.90):
            d_min, dd = None, 1.20
            while dd <= 12.0:
                if _hidden(dd, y_c, tx, ty):
                    d_min = dd
                    break
                dd += 0.01
            print(f"              y_c={y_c:+.2f} → 은닉 성립 최소 d = "
                  + (f"{d_min:.2f}" if d_min else "없음"))

        # (6) **SCENE_TEXT_BUILD §6 법칙 2** — 낙차 종단 평면에 접하는 구조물의 상면이
        #     반사실 채움면보다 높은가. H2 는 이 부등식을 깨서 기단 서측면이 `int_px`
        #     로 계상됐고 strict-H 가 0/8 이었다. 이 씬은 하드 체크로 건다.
        fill_z = HZ["fill"]["z"]
        adj = [("BendWall/Flank", WL["top"]), ("WallE", WL["top"]),
               ("Bank/N", BK["z"]), ("Bank/E", BK["z"])]
        bad = [(t, v) for t, v in adj if v <= fill_z]
        if bad:
            ok = False
        print(f"[selfcheck] (6) 법칙 2 — 낙차 인접 구조물 상면 > 채움면 {fill_z:+.2f} : "
              + " · ".join(f"{t} {v:+.2f}" for t, v in adj)
              + (f" **위반 {bad}**" if bad else " · OK"))

        print(f"[selfcheck] sceneH3 {'통과' if ok else '실패'}")
        return ok

    # -------------------------------------------------------------------
    # 조립
    # -------------------------------------------------------------------
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_banks(M)                       # 구조물 (팔 불변)
    build_walls(M)                       # ④ 은닉체 BendWall — hazard 밖
    build_walk(M)                        # ① 경로

    if cfg["hazard_stairs"]:             # ② 위험 — 조립부의 hazard 분기는 이 2줄뿐
        build_hazard(M)
    else:
        build_flat_fill(M)

    # ③ 단서 — **어느 것도 hazard 분기 안에 있지 않다** (프림 위생 1 · s14 파라펫 교훈)
    if cfg["cue_railing"]:
        build_handrail(M)
    if cfg["cue_convex_mirror"]:
        build_convex_mirror(M)
    if cfg["cue_tactile"]:
        build_tactile(M)
    if cfg["cue_nosing"]:
        build_nosing(M)
    if cfg["cue_sign"]:
        build_sign(M)
    if cfg["cue_bollard"]:
        build_bollards(M)
    if cfg["cue_manhole"] or cfg["cue_slab_joint"] or cfg["cue_drainage"] \
            or cfg["cue_tree_grate"]:
        build_ground_kit(M)
    if cfg["cue_shadow_caster"]:
        build_shadow_casters(M)
    if cfg["cue_scene_dressing"] or KEEP_DRESSING:
        # KEEP_DRESSING: 이 씬의 장식은 전부 성토 상단(z = +1.95)과 보도(z ≥ 0)에
        #   앵커되므로 위험 제거가 장식을 끌고 내려가지 않는다 — sceneC2 의
        #   "하부 앵커 드레싱 소실 → ground_z 이동" 사고가 구조적으로 불가능하다.
        build_dressing(M)

    if not scene_selfcheck():
        raise SystemExit("sceneH3 self-check 실패")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneH3 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["corridor_over"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneH3_{ts}.png")
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
# CPU 자기검사 — pxr·GPU 없이 평면 은닉과 수율을 재계산한다
# ===========================================================================
def _geometry_selfcheck():
    W, WL, HZ, BK = (PARAMS["walk"], PARAMS["wall"], PARAMS["hazard"],
                     PARAMS["bank"])
    ok = True

    def chk(tag, cond, msg=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))

    print("=" * 70)
    print("sceneH3_bend_walk — CPU 자기검사 (pxr·GPU 불필요)")
    print("=" * 70)

    st = HZ["stair"]
    drop = 0.0 - HZ["lower"]["z"]
    chk("낙차 = 계단 10단 × 라이즈",
        abs(drop - st["n"] * st["riser"]) < 1e-9, f"{drop:.3f} m")
    chk("라이즈·트레드가 실내외 계단 규격 안",
        0.15 <= st["riser"] <= 0.18 and 0.28 <= st["tread"] <= 0.35,
        f"R {st['riser']} · T {st['tread']}")
    chk("반사실 채움면 = 계단참 레벨",
        abs(HZ["fill"]["z"] - W["landing"]["z"]) < 1e-9, f"{HZ['fill']['z']}")
    chk("계단참이 굴절 모서리에서 시작",
        abs(W["landing"]["x0"] - W["bend_x"]) < 1e-9, f"{W['landing']['x0']}")

    # 수직 폐합: 최대 눈높이 < **석축**(은닉체) 마루. 남측 담장은 은닉에 무관하다.
    eye_max = W["z_up"] + 1.90
    chk("수직 폐합 (눈높이 < 석축 마루)", eye_max < WL["top"],
        f"눈 {eye_max:.2f} m < 석축 마루 {WL['top']:.2f} m "
        f"(남측 담장 {WL['top_s']:.2f} m 는 은닉식에 등장하지 않는다)")
    chk("남측 성토가 담장 마루 아래", BK["z_s"] < WL["top_s"],
        f"성토 {BK['z_s']:.2f} < 담장 {WL['top_s']:.2f}")

    # SCENE_TEXT_BUILD §6 법칙 2
    chk("법칙 2 — 낙차 인접 구조물 상면 > 반사실 채움면",
        min(WL["top"], BK["z"]) > HZ["fill"]["z"],
        f"min(석축 {WL['top']:.2f}, 성토 {BK['z']:.2f}) > 채움 {HZ['fill']['z']:.2f}"
        f" · 남측 담장 {WL['top_s']:.2f}/성토 {BK['z_s']:.2f} 는 낙차 비인접")

    tx, ty = _footprint_corner()
    print(f"  [info] 은닉 최악점 T = ({tx:+.2f}, {ty:+.2f}) · 굴절 모서리 "
          f"({W['bend_x']:+.2f}, {WL['along']['y0']:+.2f})")
    for y_c in (-0.90, -0.45, 0.0, 0.45, 0.90):
        d_min, dd = None, 1.20
        while dd <= 12.0:
            if _hidden(dd, y_c, tx, ty):
                d_min = dd
                break
            dd += 0.01
        print(f"         y_c={y_c:+.2f} → 은닉 성립 최소 d = "
              + (f"{d_min:.2f}" if d_min else "없음"))

    p_h_b, p_n_b, p_v_b = _yield_mc(1.2, 12.0, 0.25, 1.90, n=20000, seed=81)
    p_h_h, p_n_h, p_v_h = _yield_mc(6.0, 12.0, 0.25, 1.00, n=20000, seed=82)
    exp_h = 24 * p_h_b + 24 * p_h_h
    print(f"  [info] base 밴드 — H {p_h_b:.3f} · none_in_fov {p_n_b:.3f} · "
          f"가시 {p_v_b:.3f}  (계획 §3.2 가정 base 0.20)")
    print(f"  [info] H 밴드   — H {p_h_h:.3f} · none_in_fov {p_n_h:.3f} · "
          f"가시 {p_v_h:.3f}  (계획 §3.2 가정 **H 0.50** — test-ext)")
    print(f"  [info] A팔 48컷(base 24 + H 24) 기대 strict-H {exp_h:.1f} "
          "(계획 §3.2 하한 paired-H ≥ 12)")
    chk("H 밴드 설계 수율 ≥ 계획 가정 0.50 (test-ext)", p_h_h >= 0.50,
        f"{p_h_h:.3f}")
    chk("A팔 48컷 기대 strict-H ≥ 12 (§3.2 하한)", exp_h >= 12.0, f"{exp_h:.1f}")
    # **퇴화 방지 게이트의 분모** — H7 은 이 검사를 `p_visible ≥ 0.10` 로 무조건 비율에
    #   걸었다. 그 분모에는 `none_in_fov`(발자국이 폴라 격자 **밖**)가 섞여 있는데, 그
    #   프레임은 H 도 V 도 아니고 *"위험이 화각에 들어왔는가"* 라는 **다른 질문**의 답이다.
    #   이 씬은 계단 머리를 북쪽으로 물린 결과 base 밴드의 48 % 가 격자 밖이라 무조건
    #   비율이 0.099 로 떨어진다 — 그러나 **격자 안 프레임만 보면 19.2 % 가 가시**다.
    #   퇴화("전 프레임 H")가 묻는 것은 후자이므로 조건부 비율을 판정층으로 쓰고,
    #   무조건 비율도 같이 인쇄해 둘을 혼동하지 않게 한다.
    #   (SCENE_TEXT_BUILD §9 가 확정한 결함 4건과 같은 구조 — *게이트를 어느 모집단에서
    #    세는가*. 이 정정도 계획 §6.1 문면 갱신 대상으로 §10 에 올린다.)
    in_grid_b = p_h_b + p_v_b
    cond_v = (p_v_b / in_grid_b) if in_grid_b > 0 else 0.0
    print(f"  [info] base 밴드 격자 안 {in_grid_b:.3f} · 그중 가시 **{cond_v:.3f}** "
          f"(무조건 가시 {p_v_b:.3f})")
    chk("퇴화 아님 (격자 안 base 프레임의 10 % 이상이 가시)", cond_v >= 0.10,
        f"조건부 가시 {cond_v:.3f} ≥ 0.10 (무조건 {p_v_b:.3f} · "
        f"none_in_fov {p_n_b:.3f} 은 H 도 V 도 아니다)")

    ds = DATUM_STRIP
    cross = [z for z in GATED_ZONES
             if not (z[3] <= ds["x0"] or z[2] >= ds["x1"]
                     or z[5] <= ds["y0"] or z[4] >= ds["y1"])]
    dfail = [(z[0], z[6]) for z in cross if z[6] > DATUM_TOL]
    dtol = [(z[0], z[6]) for z in cross if z[6] <= DATUM_TOL]
    chk("VG-datum 선언 검사 (datum_fail 0)", not dfail,
        f"datum_tol {dtol} · datum_fail {dfail}")

    chk("표준 장비 16키", len(SCENE_CONFIG) == 16, f"{len(SCENE_CONFIG)}키")
    declared = set(CUE_CLASS) - {"_structural"}
    cue_keys = {k for k in SCENE_CONFIG if k.startswith("cue_")}
    chk("CUE_CLASS 가 모든 cue_* 를 분류", declared == cue_keys,
        f"미분류 {sorted(cue_keys - declared)} · 초과 {sorted(declared - cue_keys)}")

    print(f"\n  ⇒ sceneH3 CPU 자기검사 {'통과' if ok else '실패'}")
    print("=" * 70)
    return ok


if __name__ == "__main__":
    main()
