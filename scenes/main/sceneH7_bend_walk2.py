# -*- coding: utf-8 -*-
"""
sceneH7_bend_walk2.py — NegObs 신규 씬 H7: 옹벽 사이 보도의 굴절부 + 하행 계단 (Isaac Sim 4.5)

계열    : **복도 굴절형 자기가림 (paired-H)** · 생활권 = **보도**
정본    : `experiments/v3_0823/RENDER_PLAN_V3.md` §2.0(공통 표준) · §2.1 표 `sceneH7_bend_walk2`
          (H3 변형 · 다른 부지) · §2.6(CUE_CLASS 사전 분류) · §3.5(val strict-H ≥ 30 회계)
분리    : **val** — H6(둔덕형)과 **계열이 다른** 2차 공급원. DZ §4.2 가 고치려는 병이 정확히
          "H 통계가 씬 2개(사실상 scene14 하나)에 갇힌 것"이므로 계열을 나눠 담는다.
밴드    : base · **H**  (씬당 A팔 48컷)
승계    : `scene_common.py` · `ground_kit.py`(P3 sidewalk_block) · `infra_kit`

────────────────────────────────────────────────────────────────────────────
씬 조립 공식 (4요소 — 브리프 §2.0)
  ① 경로   옹벽 사이 보도(유효폭 3.40 m) → 종단 2단 단차 → **굴절부 계단참**
  ② 위험   굴절 너머 **하행 계단 12단 × 0.17 = 2.04 m** → 하부 통로
  ③ 단서   벽면 계단 손잡이 · 평지 복도 손잡이 · 점형블록 · 계단코 나이징 · 바닥 재질전이 ·
           지하보도 안내표지 · 옹벽 상단 가로수/그림자 · 맨홀 · 줄눈 · 측구 · 볼라드
  ④ 은닉   **BendWall** — 남측 옹벽이 (−1.00, −1.70)에서 직각으로 꺾여 계단실 서측벽이 된다.
           그 **수직 모서리**가 낙차 전체를 그림자 안에 넣는다. 굴절을 돌기 전에는 계단이 없다.

────────────────────────────────────────────────────────────────────────────
좌표계 · 평면 (walk axis = +X, Z-up, m. 카메라는 x = −d, |y| ≤ 0.90 에서 +X 를 본다)

                    y
        +2.34 ┌──────────────────────────────────────┬────────┐  BankN  z=+1.90
        +1.70 │              WallN  (top +2.45)      │        │
              │                                      │ WallE  │
         0.00 │········  보도 유효폭 3.40  ··········│ (top   │  BankE z=+1.90
              │           z = 0.00                   │ +2.45) │
        −1.70 │                          ┌───────────┤        │
        −2.34 └──── BendWall/Along ──────┤ 계단참    │        │
                    (top +2.45)          │ Landing   │        │
                              x = −1.00 →│  z=0.00   │        │
                   BankS z=+1.90         │           │        │
        −3.05 ─────────────────  Flank  ─┼───────────┤        │  ← 계단 상단 (rim)
                                 (top    │ **하행    │        │
                                 +2.45)  │  계단**   │        │
        −6.89 ───────────────────────────┤ 12단×0.17 │        │
                                         │ 하부통로  │        │
        −9.60 ───────────────────────────┴─ z=−2.04 ─┴────────┘
              x: −22.0            −1.64 −1.00      +2.40  +3.04   +14.6

  종단(보도 축): x ≤ −9.10 → z=+0.34 · x −9.10…−8.46 → 2단(라이즈 0.17) · x ≥ −8.46 → z=0.00
  낙차 = 0.00 − (−2.04) = **2.040 m** (12단 × 라이즈 0.17 · 트레드 0.32 · 유효폭 3.40 m)

────────────────────────────────────────────────────────────────────────────
H 수율 설계 — 굴절 은닉의 **닫힌 판정식** (§3.5)

옹벽 두 몸체(Along: y ∈ [−2.34,−1.70]·x ≤ −1.00 / Flank: x ∈ [−1.64,−1.00]·y ≤ −1.70)는
(−1.00, −1.70) 에서 만나는 L자 솔리드다. 눈 E = (−d, y_c) 에서 낙차점 T = (tx, ty) 로 가는
선분은 **두 경계선(y = −1.70 · x = −1.00)을 반드시 순서대로 지난다.**

      t_y = (y_c + 1.70) / (y_c − ty)      ← 선분이 y = −1.70 에 닿는 매개변수
      t_x = (d − 1.00)  / (d + tx)         ← 선분이 x = −1.00 에 닿는 매개변수

      **은닉 ⇔ t_y ≤ t_x**   (y 경계를 먼저 지나면 그때 x < −1.00 이므로 Along 솔리드 안이다)

최악 T = 발자국 중 **tx 최대 · ty 최대**인 점 = (**+2.40, −3.37**)
   (계단 2단째 상면 −0.34 가 hazard_depth 0.30 을 처음 넘는 지점 = 발자국 근단)

    y_c      은닉 성립 최소 d          비고
   −0.90        2.63                  남측 오프셋 = 더 잘 가려짐
    0.00        4.46                  중앙
   +0.50        5.48
   +0.90        6.29                  북측 최대 오프셋 = 가장 안 가려짐

수직 방향은 **항상** 막힌다: 눈 높이 ≤ 0.34 + 1.90 = 2.24 m < 옹벽 마루 2.45 m.
따라서 이 씬의 H 판정은 **평면 문제 하나**로 닫힌다 — 둔덕형(H6)이 종단면 문제 하나로
닫히는 것과 정확히 대칭이고, 그래서 두 씬은 서로 다른 실패 모드를 갖는다.

수율은 `_yield_mc()` 가 **실제 샘플러**(d LogU[·] · h U[·] · y trunc-N(0,0.35,±0.90) ·
yaw trunc-N(0,8,±20))로 몬테카를로 적분한다. 폴라 격자 포함(±31.1°·반경 12 m)까지 함께 본다.
CPU 스모크가 그 수치를 인쇄하므로 종단면·평면을 만지면 즉시 드러난다.

**[측정 · 260823_v3p5_h67probe_A, H 밴드 8컷 · L0]**
    strict-H **7/8 = 0.875** (Wilson 95 % CI [0.53, 0.98]) — 계획 §3.5 가정 0.60 의 **1.46 배**
    나머지 1컷 = `none_in_fov` (`int_px 0 · edge_projected 0`) — 발자국이 폴라 섹터 밖으로
    나간 프레임이고, MC 모형이 예측한 `none_in_fov 0.053` 과 표본오차 안에서 일치한다.
    **가시(V/E) 0컷** — 이 밴드에서 굴절 은닉은 예외 없이 성립했다.
    부수 실측: VG-datum `datum_exact 8/8` (max |Δground_z| = 0.000000 m) · VG-10 포즈 불일치 0 ·
    VG-08 세그 8/8 (`fetch=t0`) · VG-void 커버리지 **1.0000** (양팔) ·
    발자국 `cells_raw 6221` · `max_diff 2.623 m`.
    ※ `max_diff` 가 낙차 2.04 m 보다 큰 이유는 **벽면 손잡이**다 — A팔에서 계단 경사를
      따라 내려가고 C팔에서 수평(z 0.90)이므로 손잡이가 덮는 폭 0.083 m × 2줄 구간에서
      `z_off − z_on` 이 2.6 m 로 읽힌다. 그 셀들은 어차피 발자국 안(슬롯)이므로 **발자국
      면적은 늘지 않고**, 영향은 `cell_mean_drop` 통계에만 남는다 — 사전 선언된 초과분이다.

**모서리 소속 게이트(VG-06) 적합성**: H 프레임에서 가시 지면(보도·계단참)의 남측 종단선은
**BendWall 모서리에서 뻗어 나온 그림자 경계선**이며, 그 선에 접한 픽셀은 ID 마스크에서
`…/BendWall/…` 이다. 낙차 림(계단 상단)과 계단 내부는 전부 그 선 너머에 있어 **0 px** 기여한다.
`BendWall` 은 **`hazard_*` 밖**에서 지어지므로 B팔에서도 불변이다(브리프 명시 요구).

────────────────────────────────────────────────────────────────────────────
프림 위생 · 데이텀 (CUE_COVERAGE §4-4 (2)(3)(4))

1. 단서 빌더가 `if cfg["hazard_*"]` 안에 있는 것은 **0개**. 조립부의 hazard 분기는 2줄뿐이다.
2. 낙차를 지지하는 구조물(옹벽 4매·성토 3매·계단참)은 **전부 hazard 밖**이다. hazard 토글이
   움직이는 것은 **계단 12단 + 하부 슬래브**뿐이고, 그 반대편이 `FlatFill/Slot` 이다.
3. `cue_railing`(벽면 계단 손잡이)은 A팔에서 계단 경사를, C팔에서 수평(z=0.90)을 따른다 —
   **양팔 모두에 존재**하므로 VG-03(단서 마스크 불변)이 성립한다. 평지 복도에 수평 손잡이가
   서는 것은 편의증진법 시행령 별표2가 **의무화**하는 실제 구성이지 대체물이 아니다.
   `cue_nosing` 도 같은 이유로 **보도 종단 2단 단차**(팔 불변 지형)에 먼저 놓인다.
4. 카메라 데이텀 스트립 `x ∈ [−12.05, −1.15] · |y| ≤ 0.95` 안에 토글 프림 **datum_fail 0건**.
5. **void 커버리지 1.0** — 슬롯은 계단 12단 + 하부 슬래브가, 그 밖은 보도·옹벽·성토가
   x ∈ [−2, 14] × y ∈ [−8, 8] 을 빈틈없이 덮는다. 개방 바닥 0.

표준법: 법1 온전 상태만 · 법2 법정 제식 표지(지하보도 유도) 1매 · 법4 손잡이·측구·볼라드는
기능 필수 · 법5 차량·계절소품 0 · 법6 신규 재질 역할 0 · 법7 `cue_*` 최대 융기 12 mm ·
법8 수치 주석에 근거 태그.

실행
    unset PYTHONPATH VIRTUAL_ENV; conda activate env_isaaclab; export PYTHONNOUSERSITE=1
    python scenes/main/sceneH7_bend_walk2.py                 # GUI 룩체크
    NEGOBS_SMOKE=1 python scenes/main/sceneH7_bend_walk2.py  # CPU 조립 스모크(부팅 전 종료)
데이터 렌더 진입점 (신설 씬은 AZ 원장 등재 전까지 이 경로가 유일 — CUE_COVERAGE §4-4 (6)):
    python scripts/run_data_render.py --scene-proc <this file> sceneH7 <out_dir> L0 8 <seed>
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


# [계획 §2.0] 생활권 = 보도. 옹벽 사이 절토부 보도이므로 계절 표현은 성토 상단 식재에만 있다.
SEASON = "summer"


# ===========================================================================
# [A0] CUE_CLASS — 렌더 **전** 사전 분류 (RENDER_PLAN_V3 §2.6 / ACCOUNTING §2-6)
# ===========================================================================
#   렌더 후 VG-01/VG-02 가 이 선언을 기계 반증한다. 어긋나면 **씬 결함**으로 반려하며
#   결과를 보고 이 표를 고치지 않는다.
CUE_CLASS = {
    "cue_railing":          "decorative",  # 벽면 계단 손잡이 — 낙차는 계단 솔리드가 정의한다
    "cue_level_handrail":   "decorative",  # 평지 복도 손잡이 (편의증진법 별표2) — 낙차 무관
    "cue_tactile":          "decorative",  # 계단 상단 점형블록 (계단참 위, proud 4 mm)
    "cue_nosing":           "decorative",  # 나이징 12 mm — 종단 2단 + 계단 12단
    "cue_material_break":   "decorative",  # **재질 재바인딩 전용** — 프림 집합 불변
    "cue_sign":             "decorative",  # 지하보도 유도표지 1매 (WallE 벽면)
    "cue_scene_dressing":   "decorative",  # 성토 상단 관목·가로등·원경 건물
    "cue_shadow_caster":    "decorative",  # 옹벽 상단 가로수 열 — 그림자 밴드 캐스터
    "cue_manhole":          "decorative",  # 보도 맨홀 (flush)
    "cue_tree_grate":       "decorative",  # 수목보호격자 (flush) — 이 부지는 기본 OFF(법4)
    "cue_slab_joint":       "decorative",  # 보도 줄눈·신축이음 (flush)
    "cue_drainage":         "decorative",  # 옹벽 측구 flush 트렌치
    "cue_bollard":          "decorative",  # 보도 진입 볼라드
    # ── 토글 금지 목록 (구조물). 어떤 cue_* 도 이 프림들을 참조하지 않는다 ────────────
    "_structural":          ["BendWall", "WallN", "WallE", "Bank",
                             "Walk/Landing", "Walk/Step"],
}


# ===========================================================================
# [A] SCENE_CONFIG — **표준 장비 16키** (RENDER_PLAN_V3 §2.0 · CUE_COVERAGE §4-4 (1))
# ===========================================================================
#   구성: 공통 cue 6 + v3 신설 3 + FA_REALITY §2/§3 승격 후보 4
#   (`cue_slab_joint` 갭 5위 · `cue_drainage` 갭 3위 · `cue_bollard` L2 ·
#    `cue_level_handrail` L7) + hazard 1 + 팔 제어 2 = **16**. **사문 0.**
SCENE_CONFIG = {
    # ── ② 위험: 유일한 기하 토글 ────────────────────────────────────────────
    #   False → 계단 12단 + 하부 슬래브가 사라지고 계단참 레벨(z 0.00)의 평탄 지면이
    #   슬롯 x ∈ [−1.00, 2.40] · y ∈ [−9.60, −3.05] 를 채운다(반사실 보행 가능면).
    "hazard_stairs":       True,
    # ── ③ 단서: 공통 6키 ────────────────────────────────────────────────────
    "cue_railing":         True,   # 벽면 계단 손잡이 2줄 (A팔 경사 / C팔 수평)
    "cue_tactile":         True,   # 계단 상단 점형블록 (교통약자법 시행규칙)
    "cue_nosing":          True,   # 논슬립 나이징 — 종단 2단 + 계단 12단
    "cue_material_break":  True,   # 계단참 = 화강석 판석 / 보도 = 인터로킹
    "cue_sign":            True,   # 지하보도 유도표지 (법2 — 법정 제식만)
    "cue_scene_dressing":  True,   # 성토 상단 관목·가로등·원경 건물
    # ── v3 신설 3키 (FA_REALITY §2) ─────────────────────────────────────────
    #   `cue_shadow_caster` 는 **양성 씬인 이 씬에도** 배치한다(§2.0 역지름길 경보).
    "cue_shadow_caster":   True,
    "cue_manhole":         True,   # 갭 1위 (25.0)
    # 갭 2위. 유효폭 3.40 m 옹벽 절토 보도에는 가로수를 심지 않는 것이 실제 구성이므로
    #   기본 OFF(법4 "비움이 기본값"). 코드 경로·좌표는 상시 보유하며, 성토 상단
    #   보행로에 격자를 놓는 어블레이션 팔을 위해 살아 있다.
    "cue_tree_grate":      False,
    # ── FA_REALITY §2/§3 승격 후보 4키 ─────────────────────────────────────
    "cue_slab_joint":      True,   # 갭 5위
    "cue_drainage":        True,   # 갭 3위 — 옹벽 측구(flush)
    "cue_bollard":         True,   # L2 — 보도 진입 볼라드
    "cue_level_handrail":  True,   # L7 — 평지 복도 손잡이. **낙차 없는 구간**에 선다
    # ── 팔 제어 2키 ─────────────────────────────────────────────────────────
    "keep_dressing":       False,
    "placebo_remove":      False,
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # ── 보도 회랑 (전부 hazard_* 밖. 4팔 공통) ──────────────────────────────
    walk=dict(
        y_half=1.70,                       # 유효폭 3.40 m [규격 보도 유효폭 ≥ 2.0 m]
        x0=-22.0, bend_x=-1.00,            # 굴절 모서리 x
        z_low=0.00, z_up=0.34,
        step=dict(x0=-9.10, riser=0.17, tread=0.32, n=2),
        landing=dict(x0=-1.00, x1=2.40, y0=-3.05, y1=2.34, z=0.00),
    ),
    # ── 옹벽 4매 · 성토 3매 (구조물. hazard_* 밖 — 브리프 명시 요구) ────────
    wall=dict(
        t=0.64, top=2.45, bot=-2.60, cap_t=0.12,
        along=dict(x0=-22.0, x1=-1.00, y0=-2.34, y1=-1.70),
        flank=dict(x0=-1.64, x1=-1.00, y0=-9.60, y1=-1.70),
        north=dict(x0=-22.0, x1=3.04, y0=1.70, y1=2.34),
        east=dict(x0=2.40, x1=3.04, y0=-9.60, y1=2.34),
    ),
    bank=dict(z=1.90, base=-2.80,
              south=(-22.0, -9.60, -1.64, -2.34),
              north=(-22.0, 2.34, 14.60, 9.60),
              east=(3.04, -9.60, 14.60, 9.60)),
    # ── ② 위험 (hazard_stairs 전속) ────────────────────────────────────────
    hazard=dict(
        stair=dict(x0=-1.00, x1=2.40, y_head=-3.05, riser=0.17, tread=0.32,
                   n=12, base_z=-2.90),
        lower=dict(x0=-1.00, x1=2.40, y0=-9.60, z=-2.04, base_z=-2.90),
        fill=dict(x0=-1.00, x1=2.40, y0=-9.60, y1=-3.05, z=0.00, base_z=-2.90),
        # [computed] 낙차 = 0.00 − (−2.04) = 2.040 m · 계단 12단 × 0.17
        #   발자국 근단(z_on ≤ −0.30) = 2단째 상면 −0.34 → y = −3.05 − 2·0.32 = −3.69,
        #   그 셀의 **북쪽 경계** y = −3.37 이 가림 판정의 최악점이다.
    ),
    # ── ③ 단서 ─────────────────────────────────────────────────────────────
    handrail=dict(z_over=0.90, r=0.023, clear=0.06, bracket=0.055,
                  post_pitch=1.28, seg=2),
    # [규격] 손잡이 높이 0.85~0.90 m · 벽 이격 50 mm (편의증진법 시행규칙 별표1)
    level_rail=dict(x0=-19.5, x1=-1.20, z=0.88, r=0.021, clear=0.055,
                    bracket_pitch=1.60),
    tactile=dict(y0=-2.75, y1=-2.15, x0=-0.90, x1=2.30, proud=0.004),
    # [규격·개정 R4 · D82ⓐ] 점형블록 세로 0.40 → **0.60 m**(0.30 m 유닛 2매) ·
    #   계단 상단(y_head = −3.05)에서 **0.30 m 이격**.
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
    #   [면적] 0.60 × 3.20 = 1.92 m² (구 1.28). 계단참 y1 = 2.34 라 여유 있게 앉는다.
    nosing=dict(width=0.055, proud=0.012),
    sign=dict(x=2.36, y=0.55, z=1.72, w=0.68, h=0.50),
    #   유효폭 3.40 m 회랑 입구의 오토바이 진입 억제 2본. 중앙 개구 2.24 m 는
    #   ⓐ 휠체어 유효폭과 ⓑ 카메라 데이텀 스트립(|y| ≤ 0.90) 회피를 동시에 만족시키는
    #   최소 개구이며, 그 대가로 LINT-6 의 피치 1.50 ± 0.10 은 **경고 1건**을 남긴다
    #   (추론 런에 대한 advisory — 하드 규칙이 아니다). 사전 선언된 초과분이다.
    #   위치 지터 없음 — J-3/J-5(07-30) 배치 지터 폐지 · LINT-10 정적 검사 대상.
    bollard=dict(x=-11.00, ys=(-1.12, 1.12), r=0.075, h=0.88,
                 band_z=0.66, band_t=0.09),
    gkit=dict(
        region=(-19.5, -1.66, -1.10, 1.66),
        manholes=[(-6.35, 1.28), (-13.10, -1.32)],
        gullies=[(-3.20, -1.42)],
        # 횡배수 트렌치 1개. x = −5.00 은 `plan_ground` 하드 게이트 B7(GT-E2, 낙차
        #   모서리 근방 대리선 금지)을 통과하는 가장 가까운 위치다 [측정 — 이 파일의
        #   설계 시 −1.10/−3.00 은 B7 위반, −5.00 통과]. 프레임 상면은 포장과 **동일 z**
        #   (proud 0.000)이므로 카메라 데이텀은 `datum_exact` 를 유지한다.
        trench=(-5.00, -1.60, 1.60),
        tree_grates=[(-3.90, 4.10), (-10.90, 4.10)],   # 성토 상단 가로수 (기본 OFF)
    ),
    shadow=dict(
        # 옹벽 상단(성토 z=+1.90) 가로수 열 — 마루 위로 수관만 보이고 그 **그림자가
        #   보도 바닥을 가로지른다**. 낙차 방향(남측)이 아니라 북측에 세워, 그림자가
        #   낙차를 가리는 일이 없게 한다(VG-06 모서리 소유가 옹벽에 남아야 한다).
        #   가로수 열 `bank_N` — 피치 7.0 m (조례 제7조1가 6~8 m) · 1수종(ash) ·
        #   보도 축과 나란한 방위 0° (LINT-3: route bearing = kerb bearing).
        trees=[(-3.90, 4.10), (-10.90, 4.10), (-17.90, 4.10)],
        tree_h=7.4,
        lamps=[(-6.50, 3.05), (-14.80, 3.05)],
        lamp_h=4.4,
    ),
    dress=dict(
        hedge=[(-20.0, -6.30, -2.60, -3.20), (-20.0, 5.20, -2.60, 8.10)],
        shrub_h=0.80,
        # 벤치는 남측 옹벽에 붙여 놓는다 — y −1.40 (몸체 y −1.60…−1.20) 이면
        #   카메라 데이텀 스트립(|y| ≤ 0.95)을 **완전히 비운다**. y −1.05 는 스트립을
        #   0.10 m 침범해 `datum_fail` 이었다(설계 시 스모크 (2) 전수 AABB 실측).
        benches=[(-7.40, -1.40, 0.0)],
        backdrop=[("B0", 18.0, 30.0, -22.0, -6.0, 21.0),
                  ("B1", 20.0, 33.0, 4.0, 20.0, 26.0)],
    ),

    # ── 재질 3단 (realism_v1_final §84) ─────────────────────────────────────
    material=dict(
        scale=dict(paving_interlock=1.0, plaza_light=1.80, granite_dark=1.80,
                   concrete_wall=2.0, concrete_floor=1.8, grass=1.4,
                   gravel=1.2, tactile=0.3, brick_red=2.0),
        # [D85 채택 · REG_AUDIT §6.1 (2)] **보행면 틴트 신설**. 이 씬의 `M["paving"]`
        #   (= `Walk/Upper` · `Walk/Step_*` · `Walk/Lower` · `FlatFill/Slot`)은 6씬 중
        #   **유일하게 보행면 재질에 `tint=` 가 없었다** — 재질 3단 규약의 표준 이탈이다
        #   (H1 `walk_tint` 0.66 · H3 0.62 · H6 `walk_tint` 0.72(화강석) · L1 0.64 ·
        #   H2 `plaza_tint` 0.74). 그 결과 순백 `frac(min>0.8)` **중앙값 0.0703 으로 6씬
        #   최고**였고 그 **93 %가 `Walk/Lower`(62.1 %) + `Walk/Upper`(31.1 %)** 였다
        #   [260823_v3p5_h67reg_A 8컷 실측].
        #   ※ `alb_max 0.34` 클램프만으로는 못 막는다 — 정오 직사광 + 톤매핑을 거치면
        #     화면에서 날아간다. 순백은 알베도 층이 아니라 **픽셀 층**에서 잰다.
        #   값은 형제 씬 sceneH3(`walk_tint` 0.62, 0.615, 0.60)과 **같은 자리**로 잡았다 —
        #   둘 다 콘크리트/인터로킹 보도 회랑이고, 감사 권고도 "0.62 대"였다.
        paving_tint=(0.62, 0.615, 0.60),    # 인터로킹 보도블록 (알베도 0.30 대)
        landing_tint=(0.72, 0.71, 0.68),
        wall_color=(0.315, 0.315, 0.30), wall_rough=0.62,   # alb_max 0.34 이하
        cap_tint=(0.64, 0.63, 0.60),
        stair_tint=(0.60, 0.60, 0.58),
        grass_tint=(0.42, 0.55, 0.30),
        rail_color=(0.70, 0.71, 0.73), rail_metallic=0.75, rail_rough=0.34,
        nosing_color=(0.42, 0.40, 0.36), nosing_rough=0.70,
        band_color=(0.80, 0.52, 0.05),
        bollard_color=(0.66, 0.66, 0.64), bollard_rough=0.45,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.78, 0.78, 0.75), lamp_rough=0.4,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.028, 0.050, 0.018), canopy_b=(0.038, 0.064, 0.024),
        canopy_rough=1.0,
        backdrop_color=(0.44, 0.44, 0.43), backdrop_rough=0.75,
        iron_color=(0.14, 0.14, 0.15), iron_metallic=0.55, iron_rough=0.62,
    ),

    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # 북측 성토 상단 가로수 열의 그림자가 **보도를 가로질러** 남측 옹벽 밑둥까지 닿도록.
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
# [B'] 팔 제어 2키 — 모듈 스코프에서 한 번 확정 (sceneC2:496-520 패턴)
# ===========================================================================
KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))
PLACEBO_REMOVE = bool(SCENE_CONFIG.get("placebo_remove", False))
if KEEP_DRESSING:
    if SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneH7] keep_dressing=True 는 hazard_stairs=False 를 요구한다 — "
            "위험이 켜져 있으면 보존할 것이 없고 그 팔은 A팔의 라벨 없는 복제가 된다.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL sceneH7] keep_dressing=True 와 cue_scene_dressing=False 는 모순이다.")
if PLACEBO_REMOVE:
    if not SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneH7] placebo_remove=True 는 hazard_stairs=True 를 요구한다.")
    if KEEP_DRESSING:
        raise SystemExit(
            "[FATAL sceneH7] placebo_remove 와 keep_dressing 은 서로 다른 팔(P·C)이다.")
_ARM = ("C_hz0_cue1" if KEEP_DRESSING else
        "P_hz1_placebo" if PLACEBO_REMOVE else
        "hz%d_rail%d_tac%d_mat%d_dress%d" % (
            int(SCENE_CONFIG["hazard_stairs"]), int(SCENE_CONFIG["cue_railing"]),
            int(SCENE_CONFIG["cue_tactile"]), int(SCENE_CONFIG["cue_material_break"]),
            int(SCENE_CONFIG["cue_scene_dressing"])))
print(f"[sceneH7] arm={_ARM} keep_dressing={KEEP_DRESSING} "
      f"placebo_remove={PLACEBO_REMOVE}")


# ===========================================================================
# [C] 경로 상수 · 필요 텍스처 역할 · 데이텀 선언
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneH7")

ASSET_ROLES = ["paving_interlock", "plaza_light", "granite_dark",
               "concrete_wall", "concrete_floor", "grass", "gravel",
               "brick_red", "tactile", "sign_underpass",
               "hdri", "mdl"]

DATUM_STRIP = dict(x0=-12.05, x1=-1.15, y0=-0.95, y1=0.95)
DATUM_TOL = 0.02

GATED_ZONES = [
    # (tag, key, x0, x1, y0, y1, dz)  — dz = 지면 위 최대 융기
    ("Stair",        "hazard_stairs",      -1.00,   2.40,  -6.90, -3.05, 0.00),
    ("Lower",        "hazard_stairs",      -1.00,   2.40,  -9.60, -6.89, 0.00),
    ("FlatFill",     "hazard_stairs(off)", -1.00,   2.40,  -9.60, -3.05, 0.00),
    ("Handrail-W",   "cue_railing",        -1.04,  -0.90,  -7.30, -3.05, 1.30),
    ("Handrail-E",   "cue_railing",         2.36,   2.50,  -7.30, -3.05, 1.30),
    # 평지 복도 손잡이: WallN 벽면(y ≈ +1.62)에 붙는다. 데이텀 |y| ≤ 0.95 밖.
    ("LevelRail",    "cue_level_handrail", -19.50, -1.20,   1.55,  1.72, 0.95),
    ("Tactile",      "cue_tactile",        -0.90,   2.30,  -2.75, -2.15, 0.004),
    # 나이징: 보도 종단 2단(x −9.10…−8.46, 전 폭) + 계단 12단(슬롯 안).
    ("Nosing-Walk",  "cue_nosing",         -9.11,  -8.45,  -1.70,  1.70, 0.012),
    ("Nosing-Stair", "cue_nosing",         -1.00,   2.40,  -6.90, -3.05, 0.012),
    ("Sign",         "cue_sign",            2.28,   2.44,   0.21,  0.89, 2.00),
    ("Bollard-S",    "cue_bollard",       -11.15, -10.85,  -1.25, -1.00, 0.88),
    ("Bollard-N",    "cue_bollard",       -11.15, -10.85,   1.00,  1.25, 0.88),
    ("GKitWalk",     "cue_manhole/slab_joint/drainage",
                                          -19.50,  -1.10,  -1.66,  1.66, 0.008),
    ("TreeGrate",    "cue_tree_grate",    -11.70,  -3.10,   3.35,  4.85, 0.004),
    ("Shadow",       "cue_shadow_caster", -19.00,  -2.00,   2.40, 10.00, 7.40),
    ("Dress-N",      "cue_scene_dressing", -22.00,  33.00,   2.40, 31.00, 26.0),
    ("Dress-S",      "cue_scene_dressing", -22.00,  33.00, -31.00, -1.20, 26.0),
    ("Dress-Far",    "cue_scene_dressing",  17.00,  33.00, -31.00, 31.00, 26.0),
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
    """가림 판정의 **최악점** (tx, ty) = 발자국 중 tx 최대 · ty 최대.

    발자국 = `z_off − z_on ≥ 0.3`. z_off = 0(반사실 평탄), 계단 i단 상면 = −(i+1)·riser.
    ≥ 0.30 을 처음 만족하는 것은 i = 1 (상면 −0.34) 이고, 그 단의 **북쪽 경계**가
    y = y_head − n_free·tread 다. 여기서 n_free = ceil(0.30 / riser) − 1 = 1.
    """
    hz = PARAMS["hazard"]["stair"]
    n_free = max(0, math.ceil(0.30 / hz["riser"]) - 1)
    ty = hz["y_head"] - n_free * hz["tread"]
    return hz["x1"], ty


def _hidden(d, y_c, tx, ty):
    """BendWall L자 솔리드가 (tx, ty) 를 가리는가 — 파일 상단의 닫힌 판정식."""
    w = PARAMS["walk"]
    y_face = PARAMS["wall"]["along"]["y1"]        # −1.70
    x_corner = w["bend_x"]                        # −1.00
    if ty >= y_face or tx <= x_corner:
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
    y_foot = st["y_head"] - st["n"] * st["tread"]
    cells = []
    nx = 9
    for i in range(nx):
        tx = st["x0"] + (st["x1"] - st["x0"]) * i / (nx - 1.0)
        yy = ty0
        while yy >= max(lo["y0"], -8.0):
            cells.append((tx, yy))
            yy -= 0.5
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
    (수직 방향은 옹벽 마루 2.45 m > 최대 눈높이 2.24 m 이므로 항상 막힌다 — 아래 검산)
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
    # 보행 가능 폭 = 옹벽 두 안쪽 면 (유효폭 3.40 m)
    walk_edges=[((-19.50, -1.70), (-1.20, -1.70)),
                ((-19.50, 1.70), (-1.20, 1.70))],
    # 회랑에는 차도가 없다 — 북측 옹벽 밑선을 연석선으로 선언한다(가로수 이격 기준).
    kerb_lines=[((-19.50, 1.70), (-1.20, 1.70))],
    anchors={
        "corridor": dict(face_bearing_deg=0.0, props=["Bench_.*"]),
        "wall_sign": dict(face_bearing_deg=180.0, props=["Sign.*"]),
    },
    # `pts` 는 **전 그루의 좌표**여야 한다 — LINT-2 는 선언된 폴리라인의 인접 간격을
    #   그대로 피치로 읽는다(양 끝점만 적으면 14 m 로 측정된다).
    routes={
        "bank_N": dict(pts=[(-17.90, 4.10), (-10.90, 4.10), (-3.90, 4.10)],
                       species="ash", pitch_m=7.0),
    },
)


def build_views():
    """카메라 프리셋: grid_views(gy=0, 보행축 +X) + 미장센 4컷."""
    views = sc.grid_views(0.0)
    # bend_low: 보행축 저시점 — **이 씬의 연구 변수**(굴절 모서리가 계단을 삼키는가)
    views["bend_low"] = dict(eye=[-7.0, 0.05, 0.62], tgt=[2.4, -0.5, -0.1])
    # corridor_over: 회랑 전체 — 옹벽 두 줄과 굴절부의 관계
    views["corridor_over"] = dict(eye=[-11.0, -0.2, 2.05], tgt=[1.6, -0.9, -0.3])
    # stair_reveal: 굴절을 돌아선 시점 — 낙차가 다시 나타나는 지점(H → V 전이)
    views["stair_reveal"] = dict(eye=[-0.2, -1.10, 1.55], tgt=[1.6, -6.2, -1.9])
    # corner_face: BendWall 수직 모서리를 정면으로 — 모서리 소속 게이트의 육안 대응
    views["corner_face"] = dict(eye=[-4.6, 1.05, 1.45], tgt=[-0.6, -2.6, -0.4])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. bend_low (h0.62·d7.0)  — 굴절부 옹벽 모서리가 하행 계단을 통째로 삼키는가
 2. stair_reveal           — 굴절을 돌면 계단이 나타나는가 (H → V 전이)
 3. corner_face            — 가시 지면 종단선이 **옹벽 모서리**에서 뻗는가 (VG-06)
 4. corridor_over          — 옹벽 2매·성토·가로수 그림자 밴드가 회랑을 읽히게 하는가
 5. cue ON vs OFF          — 손잡이·점형블록·나이징 토글 시 기하 불변인가
 6. 접지·순백              — 순백(>0.8) 대면적 없음 · 접지 · Z파이팅 없음
 7. props 규율             — 볼라드 중앙 유효폭 개방 · 조형물 0"""


def main():
    if os.environ.get("NEGOBS_SMOKE", "0") == "1" \
            and os.environ.get("NEGOBS_SMOKE_ASSEMBLE", "0") != "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        _geometry_selfcheck()
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
    UsdGeom.Xform.Define(stage, "/World/SceneH7")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    W = PARAMS["walk"]
    WL = PARAMS["wall"]
    BK = PARAMS["bank"]
    HZ = PARAMS["hazard"]
    ROOT = "/World/SceneH7"

    def BOX(path, center, size, mtl=None, col=False, rotZ=0.0):
        return sc.add_box(stage, path, center, size, mtl, collider=col, rotZ=rotZ)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # [VG-void] 타일 이음매 여유 — 인접 슬래브가 **정확히 같은 좌표**에서 맞닿으면
    #   `AabbPrefilter.ground_z` 의 하향 레이가 두 상자의 면을 동시에 스치며 둘 다 놓친다.
    #   설계 시 이 씬의 첫 스모크에서 계단 이음매 y = −3.05 / −4.65 / −6.25 세 줄이
    #   정확히 그렇게 찍혀 커버리지가 0.9981 로 내려갔다 [측정]. 4 mm 겹침을 주면
    #   겹친 구간에서 더 높은 상자가 이기므로 경계가 4 mm 이동할 뿐이다(격자 피치 50 mm).
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
        M["paving"] = PBR(f"{ROOT}/Looks/Paving",
                          sc.tex_path("paving_interlock", "diff"),
                          sc.tex_path("paving_interlock", "nor"),
                          sc.tex_path("paving_interlock", "rough"),
                          sca["paving_interlock"], tint=mp["paving_tint"])
        M["granite"] = PBR(f"{ROOT}/Looks/Granite",
                           sc.tex_path("plaza_light", "diff"),
                           sc.tex_path("plaza_light", "nor"),
                           sc.tex_path("plaza_light", "rough"),
                           sca["plaza_light"], tint=mp["landing_tint"])
        M["cap"] = PBR(f"{ROOT}/Looks/GraniteDark",
                       sc.tex_path("granite_dark", "diff"),
                       sc.tex_path("granite_dark", "nor"),
                       sc.tex_path("granite_dark", "rough"),
                       sca["granite_dark"], tint=mp["cap_tint"])
        M["wall"] = PBR(f"{ROOT}/Looks/ConcreteWall",
                        sc.tex_path("concrete_wall", "diff"),
                        sc.tex_path("concrete_wall", "nor"),
                        sc.tex_path("concrete_wall", "rough"),
                        sca["concrete_wall"], tint=mp["wall_color"])
        M["stair"] = PBR(f"{ROOT}/Looks/StairSlab",
                         sc.tex_path("concrete_floor", "diff"),
                         sc.tex_path("concrete_floor", "nor"),
                         sc.tex_path("concrete_floor", "rough"),
                         sca["concrete_floor"], tint=mp["stair_tint"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"),
                         sc.tex_path("grass", "rough"),
                         sca["grass"], tint=mp["grass_tint"])
        M["gravel"] = PBR(f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
                          sc.tex_path("gravel", "nor"),
                          sc.tex_path("gravel", "rough"), sca["gravel"])
        M["brick"] = PBR(f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
                         sc.tex_path("brick_red", "nor"),
                         sc.tex_path("brick_red", "rough"), sca["brick_red"])
        M["tactile"] = sc.tactile_pbr(stage, f"{ROOT}/Looks/Tactile",
                                      scale_m=sca["tactile"])
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
        M["iron"] = PBR(f"{ROOT}/Looks/Iron", diffuse_color=mp["iron_color"],
                        metallic=mp["iron_metallic"],
                        roughness_const=mp["iron_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA", diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"])
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB", diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"])
        # `Backdrop` 은 look 층 misc → `BgConcrete` 로 concrete 클래스에 얹는다.
        M["backdrop"] = PBR(f"{ROOT}/Looks/BgConcrete",
                            diffuse_color=mp["backdrop_color"],
                            roughness_const=mp["backdrop_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", sc.tex_path("sign_underpass", "diff"),
                        uv_mode=True)
        return M

    # -------------------------------------------------------------------
    # ① 경로 + ④ 은닉 — 보도·옹벽·성토. **전부 hazard_* 밖** (4팔 공통 프림)
    # -------------------------------------------------------------------
    def build_walls(M):
        """옹벽 4매 + 갓돌. `BendWall` 두 몸체가 굴절 모서리를 만든다.

        브리프 명시 요구: *"옹벽은 `hazard_*` 밖에 지어 B팔에서도 불변"*.
        `Along` 의 동단 면(x = −1.00)과 `Flank` 의 북단 면(y = −1.70)이 만나는
        **수직 모서리**가 이 씬의 은닉체이자 VG-06 의 모서리 소유자다.
        """
        sc.skin_exclude(f"{ROOT}/BendWall", f"{ROOT}/WallN", f"{ROOT}/WallE")
        for tag, spec, root in (("Along", WL["along"], "BendWall"),
                                ("Flank", WL["flank"], "BendWall"),
                                ("Body", WL["north"], "WallN"),
                                ("Body", WL["east"], "WallE")):
            x0, x1 = spec["x0"], spec["x1"]
            y0, y1 = spec["y0"], spec["y1"]
            top = WL["top"] - WL["cap_t"]
            RECT(f"{ROOT}/{root}/{tag}", x0, y0, x1, y1, top, WL["bot"], M["wall"])
            # 갓돌 — 양면 20 mm 오버세일(그림자선을 만들어 코핑으로 읽히게)
            RECT(f"{ROOT}/{root}/{tag}Cap", x0 - 0.02, y0 - 0.02, x1 + 0.02,
                 y1 + 0.02, WL["top"], top, M["cap"])
        print(f"[구조] 옹벽 4매 — 마루 {WL['top']:.2f} m · 굴절 모서리 "
              f"({W['bend_x']:+.2f}, {WL['along']['y1']:+.2f}) · **hazard_* 밖**")

    def build_banks(M):
        """옹벽이 지지하는 성토(절토 배면 지반). 상면 +1.90 — 옹벽 마루보다 0.55 m 낮다."""
        for tag, (x0, y0, x1, y1) in (("S", BK["south"]), ("N", BK["north"]),
                                      ("E", BK["east"])):
            RECT(f"{ROOT}/Bank/{tag}", x0, y0, x1, y1, BK["z"], BK["base"],
                 M["grass"])

    def build_walk(M):
        """보도 회랑 바닥 + 종단 2단 단차 + 굴절부 계단참.

        `cue_material_break` 는 **계단참 슬래브의 재질 재바인딩 전용**이다 —
        프림 집합이 불변이므로 높이맵 비트 동일이 구성상 보증된다.
        """
        st = W["step"]
        yh = WL["along"]["y1"]                      # −1.70 (옹벽 안쪽 면)
        ybot, ytop = WL["along"]["y0"], WL["north"]["y1"]    # 옹벽 몸체까지 덮는다
        RECT(f"{ROOT}/Walk/Upper", W["x0"], ybot, st["x0"], ytop,
             W["z_up"], BK["base"], M["paving"])
        for i in range(st["n"]):
            x0 = st["x0"] + i * st["tread"]
            RECT(f"{ROOT}/Walk/Step_{i}", x0, ybot, x0 + st["tread"], ytop,
                 W["z_up"] - (i + 1) * st["riser"], BK["base"], M["paving"])
        RECT(f"{ROOT}/Walk/Lower", st["x0"] + st["n"] * st["tread"], ybot,
             W["bend_x"], ytop, W["z_low"], BK["base"], M["paving"])
        ld = W["landing"]
        land_mtl = M["granite"] if cfg["cue_material_break"] else M["paving"]
        RECT(f"{ROOT}/Walk/Landing", ld["x0"], ld["y0"], ld["x1"], ld["y1"],
             ld["z"], BK["base"], land_mtl)
        print(f"[cue] material_break={cfg['cue_material_break']} → Landing = "
              f"{'화강석 판석(Granite)' if cfg['cue_material_break'] else '인터로킹(Paving)'}"
              " · **프림 집합 불변**(재바인딩 전용) → 높이맵 비트 동일 보증")
        print(f"[구조] 보도 유효폭 {2 * yh * -1:.2f} m · 종단 2단(라이즈 {st['riser']}) "
              f"· 계단참 {ld['x1'] - ld['x0']:.2f} × {ld['y1'] - ld['y0']:.2f} m")

    # -------------------------------------------------------------------
    # ② 위험 — hazard_stairs 전속. 여기에는 단서가 한 개도 없다.
    # -------------------------------------------------------------------
    def build_hazard(M):
        st, lo = HZ["stair"], HZ["lower"]
        sc.skin_exclude(f"{ROOT}/Stair", f"{ROOT}/Lower")
        for i in range(st["n"]):
            y1 = st["y_head"] - i * st["tread"]
            y0 = y1 - st["tread"]
            RECT(f"{ROOT}/Stair/Step_{i:02d}", st["x0"], y0, st["x1"], y1,
                 -(i + 1) * st["riser"], st["base_z"], M["stair"])
        y_foot = st["y_head"] - st["n"] * st["tread"]
        RECT(f"{ROOT}/Lower/Floor", lo["x0"], lo["y0"], lo["x1"], y_foot,
             lo["z"], lo["base_z"], M["stair"])
        print(f"[hazard] 낙차 = {0.0 - lo['z']:.3f} m · 계단 {st['n']}단 × "
              f"라이즈 {st['riser']} · 트레드 {st['tread']} · 하부 통로 z={lo['z']:+.2f} "
              f"(y {lo['y0']:+.2f} … {y_foot:+.2f})")

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 — 계단참 레벨의 평탄 지면이 슬롯을 채운다.

        이것이 라벨러의 반사실 보행 가능면 z_off 다(footprint v2 = z_off − z_on ≥ 0.3).
        """
        f = HZ["fill"]
        RECT(f"{ROOT}/FlatFill/Slot", f["x0"], f["y0"], f["x1"], f["y1"],
             f["z"], f["base_z"], M["paving"])
        print(f"[hazard] OFF — 반사실 보행 가능면 z_off = {f['z']:+.3f} "
              f"(슬롯 x {f['x0']:+.2f}…{f['x1']:+.2f} · y {f['y0']:+.2f}…{f['y1']:+.2f})")

    # -------------------------------------------------------------------
    # ③ 단서 — 전부 hazard_* 밖의 자립 프림
    # -------------------------------------------------------------------
    def _stair_rail_z(y):
        """계단 손잡이의 높이 — 노즈 라인 위 `z_over`. 계단이 없으면 수평(C·D팔)."""
        st = HZ["stair"]
        if not cfg["hazard_stairs"]:
            return W["landing"]["z"] + PARAMS["handrail"]["z_over"]
        t = (st["y_head"] - y) / st["tread"]
        t = min(max(t, 0.0), float(st["n"]))
        return -t * st["riser"] + PARAMS["handrail"]["z_over"]

    def build_handrail(M):
        """벽면 계단 손잡이 2줄 (`cue_railing`).

        **hazard 분기 밖에서 호출된다.** A팔에서는 계단 경사를, C·D팔에서는 수평
        (z = 0.90) 을 따른다 — 평지 통로에 수평 손잡이가 서는 것은 편의증진법
        시행령 별표2가 **의무화**하는 실제 구성이므로 대체물이 아니라 같은 부재의
        같은 용도다. 그래서 이 단서는 **양팔에 모두 존재**하고 VG-03(단서 마스크
        불변)이 성립한다.
        """
        hr = PARAMS["handrail"]
        st = HZ["stair"]
        y_end = st["y_head"] - st["n"] * st["tread"] - 0.40
        n_seg = max(1, int(math.ceil((st["y_head"] - y_end) / (hr["seg"] * st["tread"]))))
        for side, x_face, sgn in (("W", st["x0"], +1.0), ("E", st["x1"], -1.0)):
            x_rail = x_face + sgn * (hr["clear"] + hr["r"])
            for s in range(n_seg):
                ya = st["y_head"] - s * hr["seg"] * st["tread"]
                yb = max(y_end, ya - hr["seg"] * st["tread"])
                za, zb = _stair_rail_z(ya), _stair_rail_z(yb)
                CYL(f"{ROOT}/Handrail{side}/Seg_{s:02d}",
                    (x_rail, 0.5 * (ya + yb), 0.5 * (za + zb)), hr["r"],
                    abs(ya - yb) + 0.02, M["rail"],
                    rotX=90.0 + math.degrees(math.atan2(zb - za, ya - yb)))
                BOX(f"{ROOT}/Handrail{side}/Brk_{s:02d}",
                    (x_face + sgn * hr["bracket"] / 2.0, 0.5 * (ya + yb),
                     0.5 * (za + zb)), (hr["bracket"], 0.05, 0.05), M["rail"])
        print(f"[cue] railing ON — 벽면 계단 손잡이 2줄 × {n_seg}구간 · "
              f"노즈선 위 {hr['z_over']:.2f} m · 벽 이격 {hr['clear'] * 1000:.0f} mm "
              f"[규격 편의증진법 시행규칙 별표1] · "
              f"{'계단 경사' if cfg['hazard_stairs'] else '수평(평지 복도)'} 추종")

    def build_level_handrail(M):
        """평지 복도 손잡이 (`cue_level_handrail`, FA_REALITY L7 ★3).

        **낙차가 전혀 없는 구간**에 선다. 편의증진법 시행령 별표2 가 평지 복도 손잡이를
        의무화하므로 "손잡이 = 계단 = 낙차"라는 지름길의 정면 반례다. 이 씬은 양성
        씬이므로, 같은 부재가 낙차 있는 구간(계단)과 없는 구간(회랑)에 **동시에**
        존재한다 — base rate 독립을 한 씬 안에서 강제한다.
        """
        lr = PARAMS["level_rail"]
        y_face = WL["north"]["y0"]                 # +1.70 (북측 옹벽 안쪽 면)
        y_rail = y_face - (lr["clear"] + lr["r"])
        CYL(f"{ROOT}/LevelRail/Tube",
            (0.5 * (lr["x0"] + lr["x1"]), y_rail, lr["z"]), lr["r"],
            lr["x1"] - lr["x0"], M["rail"], rotY=90.0)
        n = int((lr["x1"] - lr["x0"]) / lr["bracket_pitch"]) + 1
        for i in range(n):
            x = lr["x0"] + i * lr["bracket_pitch"]
            if x > lr["x1"]:
                break
            BOX(f"{ROOT}/LevelRail/Brk_{i:02d}",
                (x, y_face - lr["bracket_pitch"] * 0.0 - lr["clear"] / 2.0,
                 lr["z"]), (0.05, lr["clear"], 0.05), M["rail"])
        print(f"[cue] level_handrail ON — 평지 복도 손잡이 {lr['x1'] - lr['x0']:.1f} m "
              f"· h {lr['z']:.2f} m · 브래킷 {n}개 [FA_REALITY L7 · 편의증진법 별표2]")

    def build_tactile(M):
        t = PARAMS["tactile"]
        sc.build_tactile(stage, f"{ROOT}/Tactile", t["x0"], t["x1"],
                         t["y0"], t["y1"], M["tactile"],
                         z=W["landing"]["z"], proud=t["proud"])
        print(f"[cue] tactile ON — **경고 1밴드** 세로 {t['y1'] - t['y0']:.2f} m "
              f"(0.30 m 유닛 {round((t['y1'] - t['y0']) / 0.30)}매) · 계단 상단에서 "
              f"{abs(HZ['stair']['y_head'] - t['y0']):.2f} m 이격 "
              "[규격 교통약자법 시행규칙 별표1 · 국도 실무요령 7.5]")

    def build_nosing(M):
        """논슬립 나이징 — **보도 종단 2단(팔 불변 지형)** + 계단 12단.

        `hazard_stairs` 분기 밖에서 호출되며, 종단 2단 위의 띠는 4팔 전부에 존재한다.
        계단 위의 띠만 위험 기하에 종속되고, 그 사실을 아래 인쇄가 매 팔마다 남긴다.
        """
        ng = PARAMS["nosing"]
        st = W["step"]
        yh = WL["along"]["y1"]
        n_walk = 0
        for i in range(st["n"]):
            x1 = st["x0"] + (i + 1) * st["tread"]
            z = W["z_up"] - (i + 1) * st["riser"]
            BOX(f"{ROOT}/NosingWalk/Strip_{i}",
                (x1 - ng["width"] / 2.0, 0.0, z + ng["proud"] / 2.0),
                (ng["width"], 2 * abs(yh), ng["proud"]), M["nosing"])
            n_walk += 1
        n_st = 0
        if cfg["hazard_stairs"]:
            hs = HZ["stair"]
            for i in range(hs["n"]):
                y1 = hs["y_head"] - i * hs["tread"]
                y0 = y1 - hs["tread"]
                BOX(f"{ROOT}/NosingStair/Strip_{i:02d}",
                    (0.5 * (hs["x0"] + hs["x1"]), y0 + ng["width"] / 2.0,
                     -(i + 1) * hs["riser"] + ng["proud"] / 2.0),
                    (hs["x1"] - hs["x0"], ng["width"], ng["proud"]), M["nosing"])
                n_st += 1
        print(f"[cue] nosing ON — 보도 종단 {n_walk}단(팔 불변) + 계단 {n_st}단 · "
              f"proud {ng['proud'] * 1000:.0f} mm [계획 realism_v1_final §84]")

    def build_sign(M):
        """지하보도 유도표지 — WallE 벽면에 붙는 법정 제식 판(법2)."""
        s = PARAMS["sign"]
        BOX(f"{ROOT}/Sign/Back", (s["x"] - 0.03, s["y"], s["z"]),
            (0.05, s["w"] + 0.04, s["h"] + 0.04), M["iron"])
        BOX(f"{ROOT}/Sign/Panel", (s["x"] - 0.062, s["y"], s["z"]),
            (0.02, s["w"], s["h"]), M["sign"])
        print(f"[cue] sign ON — 지하보도 유도표지 1매 @WallE ({s['x']:+.2f},"
              f"{s['y']:+.2f},{s['z']:.2f}) · 임의 문구 0 (법2)")

    def build_bollards(M):
        """보도 진입 볼라드 — 중앙 유효폭을 비운다(휠체어 통행 + VG-datum 동시 충족)."""
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
              f"φ{2 * b['r']:.2f} m · 중앙 유효폭 {2 * 1.30:.1f} m 개방 "
              "[규격 user_feedback_v5_1 §2]")

    def build_ground_kit(M):
        """지면 문양 (`cue_manhole`·`cue_slab_joint`·`cue_drainage`) + `cue_tree_grate`.

        전부 flush(≤ 8 mm)이므로 법7(기하 불변)을 지킨다. 맨홀·측구는 |y| ≥ 1.28 에
        배치해 카메라 데이텀 스트립(|y| ≤ 0.95)을 비운다.
        """
        g = PARAMS["gkit"]
        M2 = dict(M)
        M2.update(joint=M["cap"], crack=M["cap"], manhole=M["iron"],
                  gully=M["iron"], gutter=M["cap"], gutter_cover=M["iron"],
                  trench=M["iron"], trench_frame=M["iron"], marking=M["lamp"],
                  weed=M["grass"], wear=M["gravel"], stain_dirt=M["gravel"],
                  stain_water=M["gravel"], patch=M["paving"], patch_cut=M["cap"])
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
            "sidewalk_block", region=tuple(g["region"]), z=W["z_low"], gy=0.0,
            origin=(0.0, 0.0, 0.0), edges=[("bend_corner", W["bend_x"])],
            dists=(2, 5, 10), scene="sceneH7", tactile=(),
            # `surface=None` — 잡초/균열/오염 데칼 OFF. 1차 이유는 법1(손상·노후 금지),
            #   2차 이유는 잡초 프림(proud 최대 0.107 m)이 데이텀 스트립을
            #   `datum_fail` 로 밀 수 있다는 것이다.
            overrides=dict(infra=infra, surface=None), sites=sites, seed=77)
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
        """그림자 밴드 캐스터 — 성토 상단 가로수 열 + 가로등 (`cue_shadow_caster`).

        **양성 씬에도 동일 비율로**(RENDER_PLAN_V3 §2.0 경보). 전부 **북측**(y ≥ +3.0)에
        세운다 — 남측에 세우면 수관 그림자가 낙차 쪽을 덮어 VG-06 의 모서리 소유가
        옹벽에서 수목으로 넘어간다.
        """
        s = PARAMS["shadow"]
        for i, (tx, ty) in enumerate(s["trees"]):
            sc.build_tree(stage, f"{ROOT}/Shadow/Tree_{i}", tx, ty, BK["z"],
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.15, trunk_h=s["tree_h"] * 0.52,
                          canopy_blobs=10, canopy_spread=1.15, species="ash")
        for i, (lx, ly) in enumerate(s["lamps"]):
            CYL(f"{ROOT}/Shadow/LampPole_{i}", (lx, ly, BK["z"] + s["lamp_h"] / 2.0),
                0.072, s["lamp_h"], M["pole"])
            BOX(f"{ROOT}/Shadow/LampHead_{i}",
                (lx, ly - 0.55, BK["z"] + s["lamp_h"] - 0.08),
                (0.44, 0.20, 0.13), M["lamp"])
            CYL(f"{ROOT}/Shadow/LampArm_{i}",
                (lx, ly - 0.28, BK["z"] + s["lamp_h"]), 0.05, 0.62, M["pole"],
                rotX=90.0)
        print(f"[cue] shadow_caster ON — 가로수 {len(s['trees'])}주 + "
              f"가로등 {len(s['lamps'])}주 (전부 북측 성토 상단) · "
              "남측 시선 통로 청소됨")

    def build_dressing(M):
        """③ 단서의 환경 성분 — 성토 상단 관목 띠 · 벤치 · 원경 건물."""
        d = PARAMS["dress"]
        for i, (x0, y0, x1, y1) in enumerate(d["hedge"]):
            sc.place_hedge_row(stage, f"{ROOT}/Dress/Hedge_{i}", x0, y0, x1, y1,
                               d["shrub_h"], seed=1770 + i, base_z=BK["z"],
                               fallback_mtl=M["grass"])
        for i, (bx, by, byaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Dress/Bench_{i}", bx, by, _walk_z(bx),
                           M["wood"], yaw=byaw)
        if not PLACEBO_REMOVE:
            for tag, x0, x1, y0, y1, hgt in d["backdrop"]:
                BOX(f"{ROOT}/Dress/Backdrop_{tag}",
                    ((x0 + x1) / 2.0, (y0 + y1) / 2.0, BK["z"] + hgt / 2.0),
                    (x1 - x0, y1 - y0, hgt), M["backdrop"])
        else:
            print("[placebo] 원경 건물 물량군 제거 — 위험·단서는 전부 유지(D35 P팔)")
        print(f"[cue] scene_dressing ON — 관목 {len(d['hedge'])}띠 · "
              f"벤치 {len(d['benches'])} · 원경 "
              f"{0 if PLACEBO_REMOVE else len(d['backdrop'])}동")

    # -------------------------------------------------------------------
    # 자기검사
    # -------------------------------------------------------------------
    def scene_selfcheck():
        from pxr import Usd, UsdGeom
        ok = True
        ds = DATUM_STRIP

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

        bbc = UsdGeom.BBoxCache(Usd.TimeCode.Default(),
                                [UsdGeom.Tokens.default_, UsdGeom.Tokens.render])
        gated_roots = ("/Stair", "/Lower", "/FlatFill", "/Handrail", "/LevelRail",
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
            y_lo = st["y_head"] - st["n"] * st["tread"]
            gap = abs((lo["z"] - -(st["n"]) * st["riser"]))
            covered = (y_lo <= -6.88 + 1e-6) and gap < 1e-6
        else:
            covered = (HZ["fill"]["y1"] >= st["y_head"] - 1e-9
                       and HZ["fill"]["y0"] <= -9.5)
        if not covered:
            ok = False
        print(f"[selfcheck] (3) VG-void 슬롯 커버리지 x[{st['x0']:+.2f},"
              f"{st['x1']:+.2f}] y[−9.60, {st['y_head']:+.2f}] → "
              + ("빈틈 0 · 커버리지 1.0 · OK" if covered else "빈틈 발견"))

        # (4) 단서 프림 × 낙차 발자국 교차 — 벽면 손잡이의 선언 초과분만 허용
        _, ty0 = _footprint_corner()
        cue_roots = ("/Handrail", "/LevelRail", "/Tactile", "/NosingWalk",
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
                    and mx[1] > -8.0 and mn[1] < ty0):
                over.append((p, round(float(mn[0]), 3), round(float(mx[0]), 3)))
        # 벽면 손잡이는 벽에서 50 mm 이격이 규격이므로 슬롯 위로 최대 0.083 m 나온다.
        #   양측 합쳐 0.17 m / 슬롯 폭 3.40 m = **5.0 %**. 사전 선언된 초과분이다.
        wide = [o for o in over if not o[0].split("/")[-2].startswith("Handrail")]
        if wide:
            ok = False
        print(f"[selfcheck] (4) 단서 × 발자국 교차 {len(over)}건 "
              f"(벽면 손잡이 선언 초과 {len(over) - len(wide)} · 미선언 {len(wide)})"
              + (f" {wide[:4]}" if wide else " · OK"))

        # (5) 은닉 기하 · 수율
        tx, ty = _footprint_corner()
        print(f"[selfcheck] (5) 은닉 최악점 T = ({tx:+.2f}, {ty:+.2f}) · "
              f"굴절 모서리 ({W['bend_x']:+.2f}, {WL['along']['y1']:+.2f}) · "
              f"옹벽 마루 {WL['top']:.2f} m > 최대 눈높이 "
              f"{W['z_up'] + 1.90:.2f} m → 수직은 항상 폐합")
        for y_c in (-0.90, 0.0, 0.90):
            d_min = None
            dd = 1.2
            while dd <= 12.0:
                if _hidden(dd, y_c, tx, ty):
                    d_min = dd
                    break
                dd += 0.01
            print(f"              y_c={y_c:+.2f} → 은닉 성립 최소 d = "
                  + (f"{d_min:.2f}" if d_min else "없음"))
        print(f"[selfcheck] sceneH7 {'통과' if ok else '실패'}")
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

    # ③ 단서 — 어느 것도 hazard 분기 안에 있지 않다
    if cfg["cue_railing"]:
        build_handrail(M)
    if cfg["cue_level_handrail"]:
        build_level_handrail(M)
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
        # KEEP_DRESSING: 이 씬의 장식은 전부 성토 상단(z = +1.90)과 보도(z ≥ 0)에
        #   앵커되므로 위험 제거가 장식을 끌고 내려가지 않는다 — sceneC2 의
        #   "하부 앵커 드레싱 소실 → ground_z 이동" 사고가 구조적으로 불가능하다.
        build_dressing(M)

    if not scene_selfcheck():
        raise SystemExit("sceneH7 self-check 실패")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneH7 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneH7_{ts}.png")
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
    W, WL, HZ = PARAMS["walk"], PARAMS["wall"], PARAMS["hazard"]
    ok = True

    def chk(tag, cond, msg=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))

    print("=" * 70)
    print("sceneH7_bend_walk2 — CPU 자기검사 (pxr·GPU 불필요)")
    print("=" * 70)

    st = HZ["stair"]
    drop = 0.0 - HZ["lower"]["z"]
    chk("낙차 = 계단 12단 × 라이즈",
        abs(drop - st["n"] * st["riser"]) < 1e-9, f"{drop:.3f} m")
    chk("라이즈·트레드가 실내외 계단 규격 안",
        0.15 <= st["riser"] <= 0.18 and 0.28 <= st["tread"] <= 0.35,
        f"R {st['riser']} · T {st['tread']}")
    chk("반사실 채움면 = 계단참 레벨",
        abs(HZ["fill"]["z"] - W["landing"]["z"]) < 1e-9, f"{HZ['fill']['z']}")

    # 수직 폐합: 최대 눈높이 < 옹벽 마루
    eye_max = W["z_up"] + 1.90
    chk("수직 폐합 (눈높이 < 옹벽 마루)", eye_max < WL["top"],
        f"눈 {eye_max:.2f} m < 마루 {WL['top']:.2f} m")

    tx, ty = _footprint_corner()
    print(f"  [info] 은닉 최악점 T = ({tx:+.2f}, {ty:+.2f}) · 굴절 모서리 "
          f"({W['bend_x']:+.2f}, {WL['along']['y1']:+.2f})")
    for y_c in (-0.90, -0.45, 0.0, 0.45, 0.90):
        d_min, dd = None, 1.20
        while dd <= 12.0:
            if _hidden(dd, y_c, tx, ty):
                d_min = dd
                break
            dd += 0.01
        print(f"         y_c={y_c:+.2f} → 은닉 성립 최소 d = "
              + (f"{d_min:.2f}" if d_min else "없음"))

    print("  [info] 실측 (260823_v3p5_h67probe_A · H 밴드 8컷) strict-H 7/8 = 0.875 "
          "· 나머지 1컷 none_in_fov · 가시 0")
    p_h_b, p_n_b, p_v_b = _yield_mc(1.2, 12.0, 0.25, 1.90, n=20000, seed=71)
    p_h_h, p_n_h, p_v_h = _yield_mc(6.0, 12.0, 0.25, 1.00, n=20000, seed=72)
    exp_h = 24 * p_h_b + 24 * p_h_h
    print(f"  [info] base 밴드 — H {p_h_b:.3f} · none_in_fov {p_n_b:.3f} · "
          f"가시 {p_v_b:.3f}  (계획 가정 H 0.20)")
    print(f"  [info] H 밴드   — H {p_h_h:.3f} · none_in_fov {p_n_h:.3f} · "
          f"가시 {p_v_h:.3f}  (계획 가정 H 0.60)")
    print(f"  [info] A팔 48컷(base 24 + H 24) 기대 strict-H {exp_h:.1f} "
          "(계획 §3.5 기대 19.2)")
    chk("설계 수율이 계획 기대치 이상", exp_h >= 19.2, f"{exp_h:.1f} vs 19.2")
    chk("퇴화 아님 (근거리에 가시 프레임이 남는다)", p_v_b >= 0.10,
        f"base 가시 비율 {p_v_b:.3f} ≥ 0.10")

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

    print(f"\n  ⇒ sceneH7 CPU 자기검사 {'통과' if ok else '실패'}")
    print("=" * 70)
    return ok


if __name__ == "__main__":
    main()
