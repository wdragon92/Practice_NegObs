# -*- coding: utf-8 -*-
"""
sceneD3_drainage_channel.py — NegObs 인공씬 30호: 도시 콘크리트 측구
                              (Isaac Sim 4.5)

유형    : D3 비계단 낙차 (클래스 확장 — 도로변 종주형 개거)
사양서  : Docs/nanobanana_batch1_geometry_map.md §C sceneD3_drainage_channel
          Docs/multi_scene_brief_v3.md §A 회귀 방지 체크리스트
공통    : scene_common.py · 골격 관례 scene16_canopy_shadow.py
          아스팔트 상수색 패턴 scene17_ramp_pair_hangang.py
룩 참조 : look_refs/d3_drainage_channel.jpg

위험 본질: 교외 아스팔트 차도 옆에 **무방호 건식 콘크리트 측구**(상폭 1.0 ·
           깊이 0.8 · 하폭 0.5 사다리꼴)가 **카메라 진행축(+X)과 평행하게 종주**
           한다. 보행자는 복개(슬래브 덮개) 구간 위를 걷다가 x=0 에서 개거를
           만난다. 종주 시점의 그레이징에서 개구는 폭 1.0 m 의 가는 띠로 축소
           되고, 버지측 마른 잔디가 에지를 오버행으로 덮어 **낙차 경계가 소실**
           된다. 도로측 콘크리트 립은 노면과 flush 라 단차 단서도 없다.
목표     : 차도(중앙 파선·가장자리 실선) + 측구(경사 내벽 2매·바닥판·립·풀
           오버행·바닥 낙엽) + 원거리 박스 컬버트 + 울타리·주택·수목을 조립.
GT       : **측구 영역 낙차 0.8 m 양성** (그 외 전 픽셀 낙차 없음).
           근거 = 도로이탈 ditch/culvert 사망(시나리오 조사 v1 최강 근거).
           룩체크 v1 자연 도랑(S2)의 **도시 대응쌍**.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneD3_drainage_channel.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneD3_drainage_channel.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneD3_drainage_channel.py

좌표계: Z-up, m, 진행축 +X.
  ※ 규약 보정: 이 씬의 낙차 경계는 +X 와 **평행한 종주선**(y=±0.50)이라
    "낙차 시작 모서리 = x=0" 을 종주축에 그대로 적용할 수 없다. 대신
    **복개 슬래브가 x=0 에서 끝나고 개거가 시작**하도록 배치해 (x<0 = 보행
    가능 복개 / x≥0 = 개구) 규약의 의미(전방 x=0 에서 낙차 개시)를 보존한다.
    측구 중심선 y=0 → grid_views(gy=0.0) 가 그대로 종주 시점이 된다.

────────────────────────────────────────────────────────────────────────────
기하 핵심 — 사다리꼴 단면 경사 내벽 (_oriented_box rotX) 유도
  단면: 상폭 2·0.50, 하폭 2·0.25, 깊이 0.80 → 내벽 수평후퇴 0.25
        벽 기울기(연직 대비) = atan2(0.25, 0.80) = 17.354°  (사양 ~17° 부합)
  _oriented_box 의 rotX(θ) 는 로컬축을 다음으로 사상(row-vector 규약):
        로컬 +Y → 월드 (y,z) = ( cosθ,  sinθ)      … 판 두께 방향(법선)
        로컬 +Z → 월드 (y,z) = (−sinθ,  cosθ)      … 판 길이 방향(사면 방향)
  +Y측 벽: 내면이 위 (0.50, 0) → 아래 (0.25, −0.80) 이어야 하므로
        사면 상향 단위벡터 u = (+sinφ, +cosφ), φ=17.354°.
        로컬 +Z = u 를 만족하려면 −sinθ = +sinφ ⇒ **θ = −φ**(부호 주의:
        +φ 를 쓰면 상·하폭이 뒤집힌 역사다리꼴이 된다 — 수치 검산으로 확인).
        이때 로컬 +Y = (cosφ, −sinφ) = 바깥 법선 n (채널 반대쪽·아래) ✓
        내면 중점 (0.375, −0.40) 기준
          center = mid + (t/2)·n − (ext/2)·u − (0, edge_sink)
        길이 L = hypot(0.25,0.80)·1.10 = 0.9220 (연장분 ext 는 **하단으로만**)
        검산: 상단 내면 (0.5000, −0.0040) / z=−0.80 에서 내면 y=0.2513 /
              하단 외면 y=0.3109 < 인버트 반폭 0.60(밀폐) /
              상단 외면 y=0.5859 > 버지 시작 0.50(상면 스트립 은폐)
  −Y측 벽: θ=+17.354°, center_y 부호 반전(대칭). center_z 는 동일.
  개구 상단 모서리는 edge_sink=0.004 만큼 침하 → 버지/립 상면(z=0/+0.002)과
  **동일평면 회피**(Z-파이팅 금지 규약).

────────────────────────────────────────────────────────────────────────────
[v6 맥락 드레싱] 감사 v4 "휑함" 지적 반영 — 교외 주택가 도로임이 읽히게.
  **측구 기하(개구 y −0.50..+0.50 · 오버행 · 복개 슬래브 · 립 · 컬버트)는
    한 줄도 건드리지 않았다.** 신규 요소는 전부 버지 바깥(y ≥ 4.2) 또는
    차도 건너편(y ≤ −8.05) 또는 원경(x ≥ 52) 에만 놓았다.
  ① 전신주 4본(x 13·33·53·73, y=+4.20) + 전선 3선(스팬별 2세그 새그 근사).
     y=+4.2 는 개구 에지(y=0.5) 에서 3.7 m 이격 — 종주 뷰에서 항상 개구선
     **왼쪽 바깥**에 서고, 시선 연장 레이캐스트로 개구 가림 0 을 검산(§검산).
     그림자는 태양 방위상 **+Y(펜스쪽)로만** 뻗어 측구에 닿지 않는다.
  ② 주택 진입로(driveway) 콘크리트 패치 1곳 — **차도 건너편**(y −13.65..−8.05,
     x 12.5..16.5), 주택 A 파사드로 이어짐. 측구(y ≥ −0.65)와 7.4 m 이격.
  ③ 우편함 1 + 수거함(쓰레기통) 1 — 진입로 좌우 갓길(y ≈ −8.6).
  ④ 원경 보강: 주택 C(건너편 x 56..68) · 주택 E(펜스 너머 x 52..62) ·
     수목 3본 · **수림대(treeline) 5세그(x 74..76.4)** — r5 렌더에서 지평을
     막던 '거대 백색 벽'(능선)을 수림대로 분절하고, 능선에 대기원근
     (가까울수록 짙게: 0.135 → 0.175 → 0.215) 색을 부여.
  ⑤ GT 불변: 신규 요소는 전부 지면 위 기립·박판 — 개구·낙차 신설 없음.
────────────────────────────────────────────────────────────────────────────

개구 분할 규약(교훈 5 — 주변 지면이 공동을 덮는 버그 3회 재발 이력):
  지면 평판을 y 로 4분할하여 개구대(y −0.50..+0.50, x≥0)를 **어느 평판도
  덮지 않는다**: [원측 갓길 | 차도 | 립] · 개구 · [버지 | 뒷마당]
  x<0 은 복개 슬래브가 의도적으로 덮는다(= 보행 연속성의 원천, 낙차 개시점).
────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import batch1_common as bc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키 + 씬 특색 1키(grass_overhang)
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # 씬 낙차 기하 = **측구 개거**.
                                   # False → 개구를 메워 z=0 평지 (기하 토글)
    "cue_railing":        False,   # **무방호가 정체성** — True면 버지측 파이프
                                   # 난간 1선(코드 경로 구현됨)
    "cue_tactile":        False,   # 도로변 측구엔 미관행(코드 경로만)
    "cue_material_break": True,    # 콘크리트 립·측구 vs 아스팔트 노면 대비
                                   # False → 립도 아스팔트 재질(단서 제거)
    "cue_nosing":         False,   # 계단 전용 — 미사용(키만 예약)
    "cue_sign":           False,   # [선택] 미구현 — 키만 예약
    "cue_scene_dressing": True,    # 울타리·주택·수목·원경 일괄
    # ─ 특색 토글: False → 풀 오버행 제거 = 에지 완전 노출 대응쌍 ─
    "grass_overhang":     True,
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- 측구 단면/연장 ---
    ch=dict(x_open=0.0, x_end=38.0, x_back=-22.0,
            top_half=0.50, bot_half=0.25, depth=0.80,
            wall_t=0.18, wall_ext=1.10, edge_sink=0.004,
            invert_half=0.60, invert_t=0.25),
    # --- 복개(덮개) 슬래브 : x −22..0, 상면 +0.004 (보행면·낙차 개시 에지) ---
    cover=dict(y0=-0.65, y1=0.66, top=0.004, thick=0.20,
               joint_step=2.5, joint_w=0.04, joint_proud=0.001),
    # --- 도로측 콘크리트 립 (노면과 flush, 폭 0.15) ---
    lip=dict(y0=-0.65, y1=-0.50, top=0.002, x0=-0.30, base_z=-1.60),
    # --- 아스팔트 차도 ---
    # x1 96 : 원경 능선(x 77..94)까지 지면이 이어져야 지면 끝 허공이 안 생긴다
    road=dict(y0=-8.20, y1=-0.65, x0=-22.0, x1=96.0, top=0.0, thick=1.60),
    dash=dict(y=-4.40, w=0.15, length=3.0, period=8.0, proud=0.002),
    edge_line=dict(y=-0.95, w=0.10, proud=0.002),
    # --- 버지(마른 잔디) / 뒷마당 / 원측 갓길 ---
    verge=dict(y0=0.50, y1=6.40, top=0.0, thick=1.60),
    # 대지 횡폭 y −42..+20 (브리프 §A-4: 부지 가장자리 허공 금지)
    yard=dict(y0=6.40, y1=20.0, top=0.0, thick=1.60),
    farside=dict(y0=-42.0, y1=-8.20, top=0.0, thick=1.60),
    # 컬버트 이후 개거선 매립 구간(x>헤드월) — 개구대를 여기서만 덮는다.
    #   lid = 암색 후퇴부(CulvertDark) 위를 지나는 **얇은 뚜껑**(두께 0.05):
    #   두껍게 하면 암색 박스와 볼륨이 겹쳐 개구 정면에서 동일평면 Z-파이팅.
    #   main = 그 이후 정상 두께. 뚜껑 아래 공동은 헤드월·립·버지·main 으로 밀폐.
    beyond=dict(y0=-0.65, y1=0.50, top=0.0, thick=1.60,
                lid_x0=38.40, lid_x1=44.20, lid_t=0.05),

    # --- 풀 오버행 : build_hedge 저고 스트립을 개구 에지에 걸쳐 배치 ---
    overhang=dict(count=12, seed=3001, x0=0.4, x_span=36.0,
                  len_lo=2.9, len_hi=3.1, over_lo=0.0, over_hi=0.05,
                  out_lo=0.32, out_hi=0.55, h_lo=0.05, h_hi=0.08),  # r2: 개구 돌출 거의 0, 연속 저고 잔디 립으로
    # --- 측구 바닥 낙엽 (판 + 산포) ---
    bed_leaf=dict(patches=6, seed=3002, y_half=0.22, thick=0.05,
                  sink=0.025, len_lo=0.9, len_hi=2.4, x0=1.0, x_span=34.0,
                  scatter=160, scale=(0.06, 0.045, 0.008),
                  jitter=(0.75, 1.30), lift=0.006),

    # --- 박스 컬버트 (원거리 지평 앵커 + 암색 후퇴) ---
    culvert=dict(x0=38.0, x1=38.6, y_half=0.72, z_top=0.08, z_bot=-1.05,
                 op_half=0.45, op_top=-0.10, sill_top=-0.79,
                 dark_x1=44.0, dark_half=0.48, dark_top=-0.06),

    # --- cue (기본 OFF — 무방호가 정체성) ---
    rail=dict(y=0.72, x0=0.0, x1=38.0, rail_h=0.90, post_r=0.024,
              rail_r=0.030, rail_mid_r=0.018, rail_mid_drop=0.42,
              spacing=1.60),
    tactile=dict(depth=0.30, proud=0.004),

    # --- 드레싱 / 지평 폐쇄 ---
    fence=dict(y=6.40, t=0.12, h=1.75, x0=-22.0, x1=96.0,
               cap_h=0.08, cap_over=0.04),
    trees=[dict(cx=-6.0, cy=9.0), dict(cx=5.0, cy=8.4),
           dict(cx=16.0, cy=10.0), dict(cx=28.0, cy=8.6),
           dict(cx=44.0, cy=9.4), dict(cx=58.0, cy=8.2),
           dict(cx=22.0, cy=-11.0), dict(cx=52.0, cy=-12.5)],
    houses=dict(
        A=dict(x0=8.0, x1=20.0, y0=-19.0, y1=-13.5, h=4.2, floors=1,
               axis="y", facade_y=-13.5, face_dir=1.0),
        B=dict(x0=32.0, x1=44.0, y0=-19.0, y1=-13.5, h=4.2, floors=1,
               axis="y", facade_y=-13.5, face_dir=1.0),
        # [v6-④] 원경 주택 열 보강. C = 건너편 3번째 집(주택가 리듬),
        #        E = 펜스 너머 뒷집(버지쪽 원경 — 펜스 상단 1.83 위로 노출).
        C=dict(x0=56.0, x1=68.0, y0=-19.0, y1=-13.5, h=4.2, floors=1,
               axis="y", facade_y=-13.5, face_dir=1.0),
        E=dict(x0=52.0, x1=62.0, y0=13.6, y1=19.5, h=4.0, floors=1,
               axis="y", facade_y=13.6, face_dir=-1.0),
    ),
    window=dict(w=1.2, h=1.3, inset=0.15, col_step=3.0, margin=2.0),
    back_hedge=dict(cy=12.6, sy=1.4, length=26.0),
    back_hedges=[dict(cx=-8.0), dict(cx=18.0), dict(cx=44.0), dict(cx=68.0)],
    # 원경 비스타 차단(+X 지평선): 능선 박스 2단. cy/sy 는 대지 y −42..+20 안쪽.
    # [v6-④] 대기원근 색 부여 — r5 렌더의 '백색 벽' 해소(가까울수록 짙게).
    ridge=[dict(cx=80.0, cy=-8.0, h=6.0, sy=56.0, t=6.0,
                color=(0.155, 0.175, 0.150)),
           dict(cx=90.0, cy=-8.0, h=9.0, sy=56.0, t=8.0,
                color=(0.205, 0.220, 0.235))],
    # [v6-④] 수림대 — 능선(x≥77) 앞 x 74..76.4. 높이 변주로 상면 동일평면 회피.
    #   y 는 대지(−42..+20) 안쪽으로만. base_z −0.05(지면 상면 동일평면 회피).
    treeline=dict(x0=74.0, x1=76.4, span=13.0, base_z=-0.05,
                  cys=(-30.0, -18.0, -6.0, 6.0, 13.2),
                  hs=(3.4, 2.9, 3.8, 3.1, 3.5),
                  tint=(0.150, 0.205, 0.120)),

    # ─── [v6] 맥락 드레싱 (측구 기하 불변 — 전부 y≥4.2 / y≤−8.05 / x≥52) ───
    # ① 전신주 + 전선. y=+4.20 은 개구 에지(0.50)에서 3.70 m, 펜스(6.40)에서
    #    2.20 m — 버지 한가운데. 스팬 20 m, 새그 0.35(중점 2세그 근사).
    poles=[13.0, 33.0, 53.0, 73.0],
    pole=dict(y=4.20, r=0.115, h=8.50, arm_len=1.80, arm_t=0.10, arm_h=0.09,
              wire_r=0.016, wire_z=7.620, wire_dy=(-0.75, 0.0, 0.75),
              sag=0.35, stub_x=-12.0, stub_z=7.30),
    # ② 주택 진입로 — 차도 건너편. y1 −8.05 는 노면(y0 −8.20) 위로 0.15 겹쳐
    #    동일평면 회피(상면 +0.002 proud), y0 −13.65 는 주택 A 셸 밑으로 0.15 매입.
    driveway=dict(x0=12.5, x1=16.5, y0=-13.65, y1=-8.05, top=0.002,
                  thick=0.20),
    # ③ 우편함 · 수거함 (진입로 좌우 갓길)
    mailbox=dict(cx=17.4, cy=-8.55, post_r=0.05, post_h=1.05,
                 w=0.34, d=0.24, h=0.26),
    binbox=dict(cx=11.4, cy=-8.60, w=0.58, d=0.72, h=1.02, lid_t=0.06),
    # ④ 원경 수목 3본 추가 (yard/farside 지면 위)
    trees_v6=[dict(cx=66.0, cy=15.5), dict(cx=34.0, cy=16.5),
              dict(cx=64.0, cy=-22.0)],

    material=dict(
        scale=dict(concrete_wall=1.6, concrete_floor=1.2, grass=1.4,
                   leaf_ground=0.8, wood_dark=1.0, brick_red=2.0),
        asphalt_color=(0.16, 0.16, 0.17), asphalt_rough=0.85,  # scene17 상수
        paint_color=(0.72, 0.72, 0.68), paint_rough=0.60,
        wall_tint=(0.55, 0.53, 0.50),        # 측구 내벽 풍화 암화(텍스처 배율)
        lip_tint=(0.82, 0.81, 0.78),         # 립·복개 슬래브(밝은 콘크리트)
        dry_grass_tint=(0.62, 0.58, 0.34),   # 마른 잔디 버지
        leaf_tex_tint=(0.95, 0.72, 0.48),
        leaf_tints=((0.30, 0.14, 0.05), (0.38, 0.20, 0.06),
                    (0.25, 0.10, 0.04), (0.42, 0.28, 0.10)),
        leaf_rough=0.90,
        # 컬버트 내부 암색 상수 — sRGB 감마 규칙(암색은 0.02~0.06 대역)
        dark_color=(0.030, 0.030, 0.032), dark_rough=0.95,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.86, 0.85, 0.82), parapet_rough=0.60,
        ridge_color=(0.26, 0.28, 0.26),          # (폴백 — 능선별 color 우선)
        # --- [v6] 드레싱 상수색 ---
        pole_color=(0.30, 0.27, 0.23), pole_rough=0.88,   # 풍화 목재 전신주
        wire_color=(0.045, 0.045, 0.048), wire_rough=0.60,
        mailbox_color=(0.38, 0.40, 0.42), mailbox_metallic=0.25,
        mailbox_rough=0.45,
        bin_color=(0.055, 0.075, 0.050), bin_rough=0.70,  # 진녹 수거함(암색 규약)
        bin_lid_color=(0.42, 0.38, 0.06), bin_lid_rough=0.65,
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
    # ─── SUN_AZ_OFFSET 근거(씬별 재정의): 월드 태양 az ≈ 33.5+201.5 = **235°**
    #     → 그림자 az = 55° (측구 종주축 +X 와 **55° 사각** — 사양 "종주축과
    #       사각" 충족. 90°(직교)면 한쪽 벽 전면 직사/전면 음영으로 단조,
    #       0/180°(축방향)면 양 벽이 동등해 부분 음영이 성립하지 않음).
    #     정량 검산(elev 49.79 → 깊이 1 m 당 수평 그림자 0.8455 m):
    #       도로측 상단 모서리(y=−0.50)의 그림자는 깊이 0.80 m 에서
    #       y = −0.50 + 0.8455·sin55°·0.80 = **+0.054**
    #       ⇒ 도로측 내벽 = 전면 음영 / 바닥 y<0.054 음영·y>0.054 직사 /
    #          버지측 내벽 = 직사.  개구 내부가 단일 흑색이 아니라 **부분 음영**
    #          으로 읽혀 그레이징 은닉(특색)이 성립한다.
    #     또한 태양이 카메라(+X 주시) 뒤쪽에 있어 노면·버지는 정면광.
    #     [v6 신규 요소 그림자 검산] 그림자 변위(높이 h 당) = (+0.485h, +0.6925h)
    #       — **+Y 방향(펜스쪽)** 이므로 y > 0.5 에 놓인 신규 요소의 그림자는
    #       측구에서 더 멀어진다. 전신주(y=4.20, h=8.50)의 최대 변위도
    #       y = 4.20 + 5.89 = +10.09 (펜스 6.40 너머 뒷마당) → **개구 도달 0**.
    #       차도 건너편 소품(우편함·수거함 y≈−8.6, h≤1.05)은 Δy ≤ +0.73 →
    #       y ≤ −7.87 로 갓길·노면 가장자리에 머문다(개구까지 7.2 m 남음).
    #       진입로는 평면 패치라 그림자 없음. ⇒ 측구 부분 음영 프로파일 불변. ───
    SUN_AZ_OFFSET=201.5,

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
# [C] 경로 상수 + 필요 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneD3")

ASSET_ROLES = ["concrete_wall", "concrete_floor", "grass", "leaf_ground",
               "wood_dark", "brick_red", "hdri", "mdl"]


# ===========================================================================
# [D] 카메라 프리셋: grid_views(gy=0.0 = 측구 중심선) + 미장센 4컷
#     gy 를 측구 중심선에 두어 그리드 프리셋 전부가 **종주 시점**이 된다.
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)                 # h{0.3,0.9,1.8}×d{2,5,10}, +X
    # verge_walk: 버지를 따라 걷다 측구로 사교 접근 — 오버행이 에지를 덮는가
    views["verge_walk"] = dict(eye=[-6.0, 1.70, 1.60], tgt=[6.0, 0.35, -0.20])
    # grazing_low: 종주 그레이징 저시점 — 개구가 가는 띠로 축소되는 극한
    views["grazing_low"] = dict(eye=[-4.0, 0.12, 0.35], tgt=[9.0, 0.05, -0.05])
    # oblique_cross: 차도쪽에서 30° 사교 접근(미장센 사교 컷)
    views["oblique_cross"] = dict(eye=[-3.0, -5.20, 1.50],
                                  tgt=[6.0, 0.55, -0.35])
    # channel_reveal: 근접 부감 — 사다리꼴 단면·부분 음영·바닥 낙엽 확인
    views["channel_reveal"] = dict(eye=[1.20, 2.60, 1.90],
                                   tgt=[10.0, 0.00, -0.60])
    # culvert_far: 원거리 컬버트 입구(암색 후퇴) 확인
    views["culvert_far"] = dict(eye=[30.0, 1.10, 1.55], tgt=[40.0, 0.0, -0.40])
    return views


# ===========================================================================
# [D2] 카메라 검산 (v6 맥락 드레싱) — 순수 수학, SMOKE 에서 출력.
#   Isaac 기본 카메라(focal 18.14756 / aperture 20.955) → hFOV 60°,
#   1920×1080 → vFOV 36°. 반각 30°/18°.
#   ① 카메라-신규프림 근접 충돌  ② **측구 시야 가림 = 0** (연장 시선 레이캐스트)
# ===========================================================================
HFOV_HALF = 30.0
VFOV_HALF = 18.0


def _cam_angles(view, p):
    """(yaw_rel°, elev_rel°, dist, in_frame) — 카메라 광축 기준 정확 변환."""
    ex, ey, ez = view["eye"]
    tx, ty, tz = view["tgt"]
    fx, fy, fz = tx - ex, ty - ey, tz - ez
    yaw = math.atan2(fy, fx)
    pitch = math.atan2(fz, math.hypot(fx, fy))
    dx, dy, dz = p[0] - ex, p[1] - ey, p[2] - ez
    u = dx * math.cos(yaw) + dy * math.sin(yaw)
    v = -dx * math.sin(yaw) + dy * math.cos(yaw)
    u2 = u * math.cos(pitch) + dz * math.sin(pitch)
    w2 = -u * math.sin(pitch) + dz * math.cos(pitch)
    yaw_r = math.degrees(math.atan2(v, u2))
    elev_r = math.degrees(math.atan2(w2, math.hypot(u2, v)))
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
    inf = (u2 > 0.0 and abs(yaw_r) <= HFOV_HALF and abs(elev_r) <= VFOV_HALF)
    return yaw_r, elev_r, dist, inf


def _channel_hit(eye, p, t_max=60.0, step=0.02):
    """eye→p 시선을 p **너머**로 연장해 측구 시야대(복개·립·개구·오버행 포함:
    |y| ≤ 0.66, x ∈ [x_back, x_end], z ≥ −depth) 를 통과하는지 판정.
    통과하면 (x, y) 반환 = 그 프림이 측구 픽셀을 가린다는 뜻. 아니면 None."""
    ex, ey, ez = eye
    dx, dy, dz = p[0] - ex, p[1] - ey, p[2] - ez
    ch = PARAMS["ch"]
    t = 1.0
    while t <= t_max:
        x = ex + dx * t
        y = ey + dy * t
        z = ez + dz * t
        if (abs(y) <= 0.66 and ch["x_back"] <= x <= ch["x_end"]
                and -ch["depth"] <= z <= 0.30):
            return (x, y)
        t += step
    return None


def pole_xs():
    """[v5.1 §3] 전신주 x ±0.5 m 결정적 지터. 배전 전주는 지형·부지 사정으로
    정확히 20 m 등간격이 되지 않는다 — 스팬 새그는 build_utility_line 이
    실제 스팬 중점에서 계산하므로 지터 후에도 정합한다.
    y(+4.20, 버지 중앙)는 불변 — 개구 이격 3.70 m 불변식 보존."""
    return [x + bc.jit_scalar(x, PARAMS["pole"]["y"], "poleD3", -0.5, 0.5)
            for x in PARAMS["poles"]]


def back_hedge_xs():
    """[v5.1 §3] 배경 생울타리 4구간 cx ±1.0 m 지터 (26 m 등간격 완화)."""
    return [h["cx"] + bc.jit_scalar(h["cx"], 0.0, "bhD3", -1.0, 1.0)
            for h in PARAMS["back_hedges"]]


def _dressing_probes():
    """검산 대상점: (이름, (x,y,z)) — v6 신규 드레싱의 대표 극단점."""
    P = []
    pl = PARAMS["pole"]
    for x in pole_xs():
        P.append((f"전신주x{x:.1f}·상단", (x, pl["y"], pl["h"])))
        P.append((f"전신주x{x:.1f}·중단", (x, pl["y"], pl["h"] * 0.5)))
        P.append((f"전신주x{x:.1f}·기부", (x, pl["y"], 0.3)))
        P.append((f"완목x{x:.1f}·단부",
                  (x, pl["y"] + pl["arm_len"] / 2.0, pl["wire_z"])))
    dw = PARAMS["driveway"]
    for tag, (x, y) in (("근각", (dw["x0"], dw["y1"])),
                        ("원각", (dw["x1"], dw["y0"]))):
        P.append((f"진입로·{tag}", (x, y, dw["top"])))
    mb = PARAMS["mailbox"]
    P.append(("우편함", (mb["cx"], mb["cy"], mb["post_h"] + mb["h"] / 2.0)))
    bn = PARAMS["binbox"]
    P.append(("수거함", (bn["cx"], bn["cy"], bn["h"] / 2.0)))
    for key in ("C", "E"):
        hs = PARAMS["houses"][key]
        P.append((f"주택{key}·근각", (hs["x0"], hs["facade_y"], hs["h"])))
    tl = PARAMS["treeline"]
    for i, (cy, h) in enumerate(zip(tl["cys"], tl["hs"])):
        P.append((f"수림대_{i}", (tl["x0"], cy, tl["base_z"] + h)))
    for t in PARAMS["trees_v6"]:
        P.append((f"수목({t['cx']:g},{t['cy']:g})", (t["cx"], t["cy"], 2.8)))
    return P


def _dressing_report():
    views = build_views()
    probes = _dressing_probes()
    print("-" * 64)
    print("[검산] v6 맥락 드레싱 × 카메라 (hFOV 60° / vFOV 36°)")
    worst = worst_in = None
    for vn, vw in views.items():
        for nm, p in probes:
            _, _, dist, inf = _cam_angles(vw, p)
            if worst is None or dist < worst[0]:
                worst = (dist, vn, nm)
            if inf and (worst_in is None or dist < worst_in[0]):
                worst_in = (dist, vn, nm)
    print(f"  ① 최근접(전체)     = {worst[0]:.2f} m ({worst[1]} ↔ {worst[2]})")
    print(f"    최근접(프레임 내) = {worst_in[0]:.2f} m "
          f"({worst_in[1]} ↔ {worst_in[2]}) → "
          f"{'OK' if worst_in[0] >= 1.0 else 'FAIL(<1.0)'}")
    warn = []
    for vn, vw in views.items():
        for nm, p in probes:
            if not _cam_angles(vw, p)[3]:
                continue
            hit = _channel_hit(vw["eye"], p)
            if hit is not None:
                warn.append((vn, nm, hit))
    if warn:
        for vn, nm, hit in warn:
            print(f"  ② [FAIL] {vn}: {nm} → 측구 시야대 (x={hit[0]:.1f}, "
                  f"y={hit[1]:+.2f}) 가림")
    else:
        print("  ② 측구 시야대(|y|≤0.66, x −22..38) 가림 프림 **0** → OK "
              "(연장 시선 레이캐스트, 전 뷰 × 전 프림)")
    for vn in ("verge_walk", "grazing_low", "oblique_cross", "channel_reveal",
               "culvert_far", "preset_h0.9_d5"):
        vw = views.get(vn)
        if vw is None:
            continue
        names = [nm for nm, p in probes if _cam_angles(vw, p)[3]]
        print(f"  ③ {vn:15s} 프레임 내 {len(names):2d}종: "
              f"{', '.join(names[:5])}{' …' if len(names) > 5 else ''}")
    # ④ 측구 불변식 · 지면 경계 여유
    ch = PARAMS["ch"]
    pl = PARAMS["pole"]
    dw = PARAMS["driveway"]
    mb, bn = PARAMS["mailbox"], PARAMS["binbox"]
    rd, vg, yd, fs = (PARAMS["road"], PARAMS["verge"], PARAMS["yard"],
                      PARAMS["farside"])
    print(f"  ④ 개구 에지 y=±{ch['top_half']:.2f} · 오버행/립 대역 |y|≤0.66")
    print(f"    전신주 y {pl['y']:+.2f} (버지 {vg['y0']:+.2f}..{vg['y1']:+.2f} 안, "
          f"개구에서 {pl['y'] - ch['top_half']:.2f} m) → "
          f"{'OK' if vg['y0'] < pl['y'] < vg['y1'] else 'FAIL'}")
    print(f"    진입로 y [{dw['y0']:+.2f},{dw['y1']:+.2f}] : 노면 y0 "
          f"{rd['y0']:+.2f} 위로 {rd['y0'] - dw['y1']:+.3f} 겹침(동일평면 회피) · "
          f"개구까지 {abs(dw['y1']) - 0.66:.2f} m → "
          f"{'OK' if dw['y1'] < -0.66 else 'FAIL'}")
    print(f"    우편함 y {mb['cy'] + mb['w'] / 2.0:+.2f} / 수거함 y "
          f"{bn['cy'] + bn['d'] / 2.0:+.2f} (둘 다 갓길 y<{rd['y0']:+.2f}) → "
          f"{'OK' if mb['cy'] + mb['w'] / 2 < rd['y0'] and bn['cy'] + bn['d'] / 2 < rd['y0'] else 'FAIL'}")
    tl = PARAMS["treeline"]
    ty0 = min(tl["cys"]) - tl["span"] / 2.0
    ty1 = max(tl["cys"]) + tl["span"] / 2.0
    print(f"    수림대 y [{ty0:+.1f},{ty1:+.1f}] vs 대지 [{fs['y0']:+.1f},"
          f"{yd['y1']:+.1f}] → {'OK(부유 없음)' if ty0 >= fs['y0'] and ty1 <= yd['y1'] else 'FAIL'}"
          f" · 높이 {tl['hs']} (상면 동일평면 없음)")
    hE = PARAMS["houses"]["E"]
    print(f"    주택E y [{hE['y0']:+.1f},{hE['y1']:+.1f}] + 파라펫 0.1 vs 뒷마당 "
          f"{yd['y1']:+.1f} → {'OK' if hE['y1'] + 0.1 <= yd['y1'] else 'FAIL'}")
    print("-" * 64)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3·h0.9 종주      — 측구 개구가 가는 띠로 축소·소실되는가(그레이징 은닉)
 2. verge_walk          — 마른 잔디 오버행이 근측 에지를 덮는가(특색)
 3. channel_reveal      — 사다리꼴 단면(1.0/0.8/0.5)·부분 음영·바닥 낙엽
 4. 립·노면             — 콘크리트 립이 노면과 flush(단차 단서 부재)인가
 5. 개구 분할           — 지면 평판이 개구를 덮지 않는가 / x<0 복개만 덮는가
 6. culvert_far         — 컬버트 입구가 암색 후퇴로 읽히는가(완전 흑 금지)
 7. grass_overhang OFF  — 측구 기하 트랜스폼 완전 불변(대응쌍)
 8. [v6] 맥락 판독      — 전신주·전선/진입로/우편함·수거함/원경 주택열·수림대로
                          '교외 주택가 도로변'이 읽히는가
 9. [v6] 측구 시야      — 신규 요소가 전 뷰에서 개구·오버행을 전혀 안 가리는가
10. [v6] 지평           — 능선이 백색 벽이 아니라 수림대+대기원근 층위로 읽히는가"""


def main():
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
    UsdGeom.Xform.Define(stage, "/World/Scene30")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene30"

    ch = PARAMS["ch"]
    # 벽 기울기(연직 대비) — 사다리꼴 단면에서 유도
    TILT = math.degrees(math.atan2(ch["top_half"] - ch["bot_half"],
                                   ch["depth"]))
    SLOPE_LEN = math.hypot(ch["top_half"] - ch["bot_half"], ch["depth"])

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return PBR(path, sc.tex_path(role, "diff"),
                       sc.tex_path(role, "nor"), sc.tex_path(role, "rough"),
                       scale, **kw)

        M = {}
        M["chwall"] = tex("concrete_wall", f"{ROOT}/Looks/ChWall",
                          sca["concrete_wall"], tint=mp["wall_tint"])
        M["conc"] = tex("concrete_floor", f"{ROOT}/Looks/Conc",
                        sca["concrete_floor"], tint=mp["lip_tint"])
        M["grass"] = tex("grass", f"{ROOT}/Looks/Grass", sca["grass"],
                         tint=mp["dry_grass_tint"])
        M["leafbed"] = tex("leaf_ground", f"{ROOT}/Looks/LeafBed",
                           sca["leaf_ground"], tint=mp["leaf_tex_tint"])
        M["wood"] = tex("wood_dark", f"{ROOT}/Looks/WoodTex", sca["wood_dark"])
        M["brick"] = tex("brick_red", f"{ROOT}/Looks/Brick", sca["brick_red"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["paint"] = PBR(f"{ROOT}/Looks/Paint", diffuse_color=mp["paint_color"],
                         roughness_const=mp["paint_rough"], metallic=0.0)
        M["dark"] = PBR(f"{ROOT}/Looks/Dark", diffuse_color=mp["dark_color"],
                        roughness_const=mp["dark_rough"], metallic=0.0,
                        specular_level=0.0)
        for i, c in enumerate(mp["leaf_tints"]):
            M[f"leaf_{i}"] = PBR(f"{ROOT}/Looks/Leaf_{i}", diffuse_color=c,
                                 roughness_const=mp["leaf_rough"],
                                 metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["woodc"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                         roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # [v6-④] 능선은 대기원근 색을 개별 부여(폴백 = ridge_color)
        for i, r in enumerate(PARAMS["ridge"]):
            M[f"ridge_{i}"] = PBR(
                f"{ROOT}/Looks/Ridge_{i}",
                diffuse_color=r.get("color", mp["ridge_color"]),
                roughness_const=0.95, specular_level=0.0)
        # --- [v6] 드레싱 재질 ---
        tl = PARAMS["treeline"]
        M["treeline"] = tex("grass", f"{ROOT}/Looks/Treeline", sca["grass"],
                            tint=tl["tint"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        roughness_const=mp["pole_rough"], metallic=0.0)
        M["wire"] = PBR(f"{ROOT}/Looks/Wire", diffuse_color=mp["wire_color"],
                        roughness_const=mp["wire_rough"], metallic=0.0)
        M["mailbox"] = PBR(f"{ROOT}/Looks/Mailbox",
                           diffuse_color=mp["mailbox_color"],
                           metallic=mp["mailbox_metallic"],
                           roughness_const=mp["mailbox_rough"])
        M["bin"] = PBR(f"{ROOT}/Looks/Bin", diffuse_color=mp["bin_color"],
                       roughness_const=mp["bin_rough"], metallic=0.0)
        M["bin_lid"] = PBR(f"{ROOT}/Looks/BinLid",
                           diffuse_color=mp["bin_lid_color"],
                           roughness_const=mp["bin_lid_rough"], metallic=0.0)
        return M

    # -------------------------------------------------------------------
    # 두 점 사이 원기둥(전선) — scene15 관례. Z축 실린더를 yaw/pitch 로 정렬.
    # -------------------------------------------------------------------
    def _wire(path, a, b, r, mtl):
        from pxr import UsdGeom, UsdShade, Gf
        ax, ay, az = a
        bx, by, bz = b
        dx, dy, dz = bx - ax, by - ay, bz - az
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        cyl = UsdGeom.Cylinder.Define(stage, path)
        cyl.CreateRadiusAttr(float(r))
        cyl.CreateHeightAttr(float(L))
        cyl.CreateAxisAttr(UsdGeom.Tokens.z)
        xf = UsdGeom.Xformable(cyl)
        xf.AddTranslateOp().Set(Gf.Vec3d((ax + bx) / 2.0, (ay + by) / 2.0,
                                         (az + bz) / 2.0))
        xf.AddRotateZOp().Set(float(math.degrees(math.atan2(dy, dx))))
        xf.AddRotateYOp().Set(
            float(math.degrees(math.atan2(math.hypot(dx, dy), dz))))
        if mtl is not None:
            UsdShade.MaterialBindingAPI.Apply(cyl.GetPrim()).Bind(mtl)
        return cyl

    # -------------------------------------------------------------------
    # 지면 — **개구대(y ±0.50, x≥0)를 덮지 않도록 y 로 분할** (교훈 5)
    #   [원측 갓길 | 차도 | 립] · 개구 · [버지 | 뒷마당]
    # -------------------------------------------------------------------
    def build_ground(M):
        rd = PARAMS["road"]
        lp = PARAMS["lip"]
        vg = PARAMS["verge"]
        yd = PARAMS["yard"]
        fs = PARAMS["farside"]
        by = PARAMS["beyond"]
        cv = PARAMS["culvert"]
        x0, x1 = rd["x0"], rd["x1"]

        def plate(name, y0, y1, top, thick, mtl, xa=None, xb=None):
            xa = x0 if xa is None else xa
            xb = x1 if xb is None else xb
            BOX(f"{ROOT}/{name}", ((xa + xb) / 2.0, (y0 + y1) / 2.0,
                                   top - thick / 2.0),
                (xb - xa, y1 - y0, thick), mtl, col=True)

        # 차도(아스팔트) + 원측 갓길 + 버지 + 뒷마당
        plate("Road", rd["y0"], rd["y1"], rd["top"], rd["thick"], M["asphalt"])
        plate("FarSide", fs["y0"], fs["y1"], fs["top"], fs["thick"], M["grass"])
        plate("Verge", vg["y0"], vg["y1"], vg["top"], vg["thick"], M["grass"])
        plate("Yard", yd["y0"], yd["y1"], yd["top"], yd["thick"], M["grass"])
        # 도로측 립 (노면과 flush, proud 0.002) — x는 개거 구간 + 복개 밑 0.30
        lip_mtl = M["conc"] if cfg["cue_material_break"] else M["asphalt"]
        plate("Lip", lp["y0"], lp["y1"], lp["top"], lp["top"] - lp["base_z"],
              lip_mtl, xa=lp["x0"], xb=cv["x1"])
        # 컬버트 이후 매립 구간 — 개구대를 덮는 유일한 +X측 평판(뚜껑 + 본체).
        # hazard_stairs=False(평지 대조군)에서는 FlatFill 이 개구선을 통째로
        # 메우므로 여기서 만들면 상면 동일평면(Z-파이팅) → 위험 기하일 때만.
        if cfg["hazard_stairs"]:
            plate("BeyondLid", by["y0"], by["y1"], by["top"], by["lid_t"],
                  M["grass"], xa=by["lid_x0"], xb=by["lid_x1"])
            plate("BeyondMain", by["y0"], by["y1"], by["top"], by["thick"],
                  M["grass"], xa=by["lid_x1"], xb=x1)

    def build_cover(M):
        """복개 슬래브 (x −22..0) — 보행 연속성의 원천이자 낙차 개시 에지."""
        cvr = PARAMS["cover"]
        BOX(f"{ROOT}/CoverSlab",
            ((ch["x_back"] + ch["x_open"]) / 2.0,
             (cvr["y0"] + cvr["y1"]) / 2.0, cvr["top"] - cvr["thick"] / 2.0),
            (ch["x_open"] - ch["x_back"], cvr["y1"] - cvr["y0"],
             cvr["thick"]), M["conc"], col=True)
        # 슬래브 줄눈 (암색 대신 동일 재질 음각 대용 — 얇은 띠, proud 0.001)
        n = 0
        x = ch["x_back"] + cvr["joint_step"]
        while x < ch["x_open"] - 1e-6:
            BOX(f"{ROOT}/CoverJoint_{n}",
                (x, (cvr["y0"] + cvr["y1"]) / 2.0,
                 cvr["top"] + cvr["joint_proud"] - 0.01),
                (cvr["joint_w"], cvr["y1"] - cvr["y0"], 0.02), M["dark"])
            x += cvr["joint_step"]
            n += 1

    # -------------------------------------------------------------------
    # 측구 — 경사 내벽 2매(_oriented_box rotX) + 바닥판
    # -------------------------------------------------------------------
    def build_channel(M):
        ph = math.radians(TILT)               # φ (연직 대비 벽 기울기)
        t = ch["wall_t"]
        mid_y = (ch["top_half"] + ch["bot_half"]) / 2.0     # 0.375
        uy, uz = math.sin(ph), math.cos(ph)   # u: 사면 상향 단위벡터
        ny, nz = math.cos(ph), -math.sin(ph)  # n: 바깥 법선(로컬 +Y, θ=−φ)
        ext = SLOPE_LEN * (ch["wall_ext"] - 1.0)   # 연장분(하단으로만)
        cy = mid_y + (t / 2.0) * ny - 0.5 * ext * uy
        cz = -ch["depth"] / 2.0 + (t / 2.0) * nz - 0.5 * ext * uz
        cz -= ch["edge_sink"]                 # 상단 모서리 침하(동일평면 회피)
        xa, xb = ch["x_back"], ch["x_end"] + 0.30      # 헤드월 안으로 0.30 매입
        cx = (xa + xb) / 2.0
        for tag, sgn in (("N", 1.0), ("S", -1.0)):
            sc._oriented_box(
                stage, f"{ROOT}/ChWall_{tag}",
                (cx, sgn * cy, cz),
                (xb - xa, t, SLOPE_LEN * ch["wall_ext"]), M["chwall"],
                collider=True, rotx=-sgn * TILT)
        # 바닥판(인버트) — 벽 하단을 받아 밀폐. 노출 폭은 벽 사이 2·bot_half.
        BOX(f"{ROOT}/ChInvert",
            (cx, 0.0, -ch["depth"] - ch["invert_t"] / 2.0),
            (xb - xa, 2.0 * ch["invert_half"], ch["invert_t"]),
            M["chwall"], col=True)
        # 복개 구간 후단 마감(원경 광 누출 차단)
        BOX(f"{ROOT}/ChBackCap",
            (ch["x_back"] - 0.15, 0.0, -ch["depth"] / 2.0),
            (0.30, 2.0 * ch["invert_half"], ch["depth"] + 0.4), M["dark"])
        print(f"[기하] 측구 상폭 {2 * ch['top_half']:.2f} 하폭 "
              f"{2 * ch['bot_half']:.2f} 깊이 {ch['depth']:.2f} · "
              f"내벽 기울기 {TILT:.3f}° · 사면장 {SLOPE_LEN:.4f} m")

    def build_road_paint(M):
        """백색 중앙 파선 + 노측 실선 (paint 박스, proud 0.002)."""
        rd = PARAMS["road"]
        ds = PARAMS["dash"]
        n = 0
        x = rd["x0"] + 1.0
        while x + ds["length"] <= rd["x1"]:
            BOX(f"{ROOT}/Dash_{n}",
                (x + ds["length"] / 2.0, ds["y"], ds["proud"] - 0.01),
                (ds["length"], ds["w"], 0.02), M["paint"])
            x += ds["period"]
            n += 1
        el = PARAMS["edge_line"]
        BOX(f"{ROOT}/EdgeLine",
            ((rd["x0"] + rd["x1"]) / 2.0, el["y"], el["proud"] - 0.01),
            (rd["x1"] - rd["x0"], el["w"], 0.02), M["paint"])

    # -------------------------------------------------------------------
    # 풀 오버행 — build_hedge 저고 스트립이 개구 에지(y=+0.50)를 걸침
    # -------------------------------------------------------------------
    def build_overhang(M):
        ov = PARAMS["overhang"]
        rng = random.Random(int(ov["seed"]))
        step = ov["x_span"] / float(ov["count"])
        for i in range(int(ov["count"])):
            xa = ov["x0"] + i * step   # r4: 지터 제거 — 간극 없는 연속 잔디 립(끊긴 판재감 해소)
            xb = xa + rng.uniform(ov["len_lo"], ov["len_hi"])
            y_in = ch["top_half"] - rng.uniform(ov["over_lo"], ov["over_hi"])
            y_out = ch["top_half"] + rng.uniform(ov["out_lo"], ov["out_hi"])
            h = rng.uniform(ov["h_lo"], ov["h_hi"])
            sc.build_hedge(stage, f"{ROOT}/Overhang_{i}", xa, y_in, xb, y_out,
                           h, mtl=M["grass"], base_z=-0.04)  # r1: 버지면 매입(부유 해소)

    # -------------------------------------------------------------------
    # 측구 바닥 낙엽 — 패치 판 + 산포 타원체(고정 시드)
    # -------------------------------------------------------------------
    def build_bed_leaf(M):
        bl = PARAMS["bed_leaf"]
        rng = random.Random(int(bl["seed"]))
        z_top = -ch["depth"] + bl["sink"]      # 바닥판 상면 위 2.5cm
        step = bl["x_span"] / float(bl["patches"])
        for i in range(int(bl["patches"])):
            xa = bl["x0"] + i * step + rng.uniform(0.0, step * 0.5)
            xb = xa + rng.uniform(bl["len_lo"], bl["len_hi"])
            BOX(f"{ROOT}/BedLeaf_{i}",
                ((xa + xb) / 2.0, rng.uniform(-0.05, 0.05),
                 z_top - bl["thick"] / 2.0),
                (xb - xa, 2.0 * bl["y_half"], bl["thick"]), M["leafbed"])
        UsdGeom.Xform.Define(stage, f"{ROOT}/BedLeaves")
        mats = [M[f"leaf_{i}"] for i in range(len(mp["leaf_tints"]))]
        sx, sy, sz = bl["scale"]
        jlo, jhi = bl["jitter"]
        for i in range(int(bl["scatter"])):
            x = rng.uniform(ch["x_open"] + 0.3, ch["x_end"] - 0.5)
            y = rng.uniform(-ch["bot_half"] + 0.03, ch["bot_half"] - 0.03)
            j = rng.uniform(jlo, jhi)
            a, b = sx * j, sy * j
            if rng.random() < 0.5:
                a, b = b, a
            sc.add_sphere(stage, f"{ROOT}/BedLeaves/Leaf_{i}",
                          (x, y, -ch["depth"] + bl["lift"]), (a, b, sz * j),
                          mats[rng.randrange(len(mats))])

    # -------------------------------------------------------------------
    # 박스 컬버트 입구 — 개구 4분할(교훈 5) + 암색 후퇴
    # -------------------------------------------------------------------
    def build_culvert(M):
        cv = PARAMS["culvert"]
        cx = (cv["x0"] + cv["x1"]) / 2.0
        lx = cv["x1"] - cv["x0"]
        # ① 좌 ② 우 (개구 y ±op_half 바깥, 전 높이)
        for tag, ya, yb in (("N", cv["op_half"], cv["y_half"]),
                            ("S", -cv["y_half"], -cv["op_half"])):
            BOX(f"{ROOT}/Culvert_{tag}",
                (cx, (ya + yb) / 2.0, (cv["z_top"] + cv["z_bot"]) / 2.0),
                (lx, yb - ya, cv["z_top"] - cv["z_bot"]), M["conc"], col=True)
        # ③ 상인방 (개구 상단 ~ 헤드월 천단)
        BOX(f"{ROOT}/Culvert_Top",
            (cx, 0.0, (cv["op_top"] + cv["z_top"]) / 2.0),
            (lx, 2.0 * cv["op_half"], cv["z_top"] - cv["op_top"]),
            M["conc"], col=True)
        # ④ 하부 문턱 (인버트보다 1cm 융기 → 동일평면 회피 + 입구 단차 연출)
        BOX(f"{ROOT}/Culvert_Sill",
            (cx, 0.0, (cv["z_bot"] + cv["sill_top"]) / 2.0),
            (lx, 2.0 * cv["op_half"], cv["sill_top"] - cv["z_bot"]),
            M["conc"], col=True)
        # 암색 후퇴부 (개구 뒤 어둠) — 완전 흑 금지: 상수 0.030 + 개구 통과광
        BOX(f"{ROOT}/CulvertDark",
            ((cv["x1"] + cv["dark_x1"]) / 2.0, 0.0,
             (cv["z_bot"] + cv["dark_top"]) / 2.0),
            (cv["dark_x1"] - cv["x1"], 2.0 * cv["dark_half"],
             cv["dark_top"] - cv["z_bot"]), M["dark"])

    # -------------------------------------------------------------------
    # 단서 (cue) — 기본 OFF
    # -------------------------------------------------------------------
    def build_cues(M):
        if cfg["cue_railing"]:
            rl = PARAMS["rail"]
            sc.build_railing_line(
                stage, f"{ROOT}/Rail", rl["y"], rl["x0"], rl["x0"],
                rl["x1"] - rl["x0"], 0.0, lambda x: 0.0, M["rail"],
                rail_h=rl["rail_h"], post_r=rl["post_r"],
                spacing=rl["spacing"], rail_r=rl["rail_r"],
                rail_mid_r=rl["rail_mid_r"],
                rail_mid_drop=rl["rail_mid_drop"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{ROOT}/Tactile",
                             ch["x_open"] - tc["depth"], ch["x_open"],
                             -ch["top_half"], ch["top_half"], M["conc"],
                             z=PARAMS["cover"]["top"], proud=tc["proud"])

    # -------------------------------------------------------------------
    # 드레싱 + 지평 폐쇄
    # -------------------------------------------------------------------
    def build_dressing(M):
        fc = PARAMS["fence"]
        BOX(f"{ROOT}/Fence",
            ((fc["x0"] + fc["x1"]) / 2.0, fc["y"], fc["h"] / 2.0),
            (fc["x1"] - fc["x0"], fc["t"], fc["h"]), M["wood"], col=True)
        BOX(f"{ROOT}/FenceCap",
            ((fc["x0"] + fc["x1"]) / 2.0, fc["y"], fc["h"] + fc["cap_h"] / 2.0),
            (fc["x1"] - fc["x0"], fc["t"] + 2 * fc["cap_over"], fc["cap_h"]),
            M["wood"])
        for i, t in enumerate(PARAMS["trees"] + PARAMS["trees_v6"]):
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", t["cx"], t["cy"], 0.0,
                          M["woodc"], M["canopy_a"], M["canopy_b"])
        for key, bd in PARAMS["houses"].items():
            sc.build_building(stage, f"{ROOT}/House_{key}", bd, M["brick"],
                              M["glass"], M["parapet"],
                              window=PARAMS["window"])
        build_utility_line(M)
        build_driveway(M)
        build_kerb_props(M)

    # -------------------------------------------------------------------
    # [v6-①] 전신주 4본 + 전선 3선 — 버지 y=+4.20 (개구 에지에서 3.70 m).
    #   그림자는 +Y(펜스쪽)로만 뻗어 측구 부분 음영 프로파일에 영향 없음.
    #   스팬은 중점 새그(2세그 절선)로 근사 — 곡선 프림 없이 처짐 실루엣 확보.
    # -------------------------------------------------------------------
    def build_utility_line(M):
        pl = PARAMS["pole"]
        xs = pole_xs()                          # v5.1 §3 등간격 지터
        for i, x in enumerate(xs):
            base = f"{ROOT}/Pole_{i}"
            CYL(f"{base}/Shaft", (x, pl["y"], pl["h"] / 2.0),
                pl["r"], pl["h"], M["pole"], col=True)
            # 완목(crossarm) — 상면이 전선 하단(wire_z − wire_r)에 접함
            arm_top = pl["wire_z"] - pl["wire_r"]
            BOX(f"{base}/Arm", (x, pl["y"], arm_top - pl["arm_h"] / 2.0),
                (pl["arm_t"], pl["arm_len"], pl["arm_h"]), M["pole"])
        # 전선: 스팬(pole→pole) + 진행 반대편 스텁(전 카메라 후방에서 종단)
        spans = [(pl["stub_x"], xs[0], pl["stub_z"], pl["wire_z"])]
        spans += [(xs[k], xs[k + 1], pl["wire_z"], pl["wire_z"])
                  for k in range(len(xs) - 1)]
        for s, (xa, xb, za, zb) in enumerate(spans):
            xm = (xa + xb) / 2.0
            zm = (za + zb) / 2.0 - pl["sag"]
            for w, dy in enumerate(pl["wire_dy"]):
                y = pl["y"] + dy
                _wire(f"{ROOT}/Wire_{s}_{w}a", (xa, y, za), (xm, y, zm),
                      pl["wire_r"], M["wire"])
                _wire(f"{ROOT}/Wire_{s}_{w}b", (xm, y, zm), (xb, y, zb),
                      pl["wire_r"], M["wire"])

    # -------------------------------------------------------------------
    # [v6-②] 주택 진입로 — **차도 건너편**(측구와 7.4 m 이격). 노면 위 0.15 겹침
    #   + 상면 proud 0.002 → 동일평면 Z-파이팅 회피. 주택 A 셸 밑 0.15 매입.
    # -------------------------------------------------------------------
    def build_driveway(M):
        dw = PARAMS["driveway"]
        BOX(f"{ROOT}/Driveway",
            ((dw["x0"] + dw["x1"]) / 2.0, (dw["y0"] + dw["y1"]) / 2.0,
             dw["top"] - dw["thick"] / 2.0),
            (dw["x1"] - dw["x0"], dw["y1"] - dw["y0"], dw["thick"]),
            M["conc"], col=True)

    # -------------------------------------------------------------------
    # [v6-③] 우편함 · 수거함 — 진입로 좌우 갓길(y ≈ −8.6, 차도 건너편).
    # -------------------------------------------------------------------
    def build_kerb_props(M):
        mb = PARAMS["mailbox"]
        CYL(f"{ROOT}/Mailbox/Post", (mb["cx"], mb["cy"], mb["post_h"] / 2.0),
            mb["post_r"], mb["post_h"], M["mailbox"], col=True)
        BOX(f"{ROOT}/Mailbox/Box",
            (mb["cx"], mb["cy"], mb["post_h"] + mb["h"] / 2.0),
            (mb["d"], mb["w"], mb["h"]), M["mailbox"])
        bn = PARAMS["binbox"]
        BOX(f"{ROOT}/Bin/Body", (bn["cx"], bn["cy"], bn["h"] / 2.0),
            (bn["w"], bn["d"], bn["h"]), M["bin"], col=True)
        BOX(f"{ROOT}/Bin/Lid", (bn["cx"], bn["cy"], bn["h"] + bn["lid_t"] / 2.0),
            (bn["w"] + 0.02, bn["d"] + 0.02, bn["lid_t"]), M["bin_lid"])

    def build_horizon(M):
        bh = PARAMS["back_hedge"]
        # [v5.1 §3·§4] 등간격 26 m → ±1.0 m 지터 + 구간별 ±5% 틴트 지터.
        #   (동일 재질 4연속 = '복제 벽' 인상. 실제 생울타리는 수종·관리
        #    상태 차로 구간마다 녹색이 갈린다.)
        for i, hx in enumerate(back_hedge_xs()):
            sc.build_hedge(stage, f"{ROOT}/BackHedge_{i}",
                           hx - bh["length"] / 2.0,
                           bh["cy"] - bh["sy"] / 2.0,
                           hx + bh["length"] / 2.0,
                           bh["cy"] + bh["sy"] / 2.0, 1.9, base_z=0.0,
                           tint=bc.jit_tint((0.35, 0.45, 0.28), hx, 0.0,
                                            "bhTintD3", amp=0.05))
        for i, r in enumerate(PARAMS["ridge"]):
            BOX(f"{ROOT}/Ridge_{i}", (r["cx"], r["cy"], r["h"] / 2.0),
                (r["t"], r["sy"], r["h"]), M[f"ridge_{i}"], col=True)
        # [v6-④] 수림대 — 능선 앞 절단선을 수관 실루엣으로 분절(백색 벽 해소).
        tl = PARAMS["treeline"]
        for i, (cy, h) in enumerate(zip(tl["cys"], tl["hs"])):
            sc.build_hedge(stage, f"{ROOT}/TreeLine_{i}",
                           tl["x0"], cy - tl["span"] / 2.0,
                           tl["x1"], cy + tl["span"] / 2.0, h,
                           mtl=M["treeline"], base_z=tl["base_z"])

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 : 개구를 메워 전 구간 z=0 평지."""
        by = PARAMS["beyond"]
        rd = PARAMS["road"]
        BOX(f"{ROOT}/FlatFill",
            ((rd["x0"] + rd["x1"]) / 2.0, (by["y0"] + by["y1"]) / 2.0,
             by["top"] - by["thick"] / 2.0),
            (rd["x1"] - rd["x0"], by["y1"] - by["y0"], by["thick"]),
            M["grass"], col=True)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_ground(M)
    build_road_paint(M)
    if cfg["hazard_stairs"]:
        build_cover(M)
        build_channel(M)
        build_bed_leaf(M)
        if cfg["grass_overhang"]:
            build_overhang(M)
        build_culvert(M)
        build_cues(M)
    else:
        build_flat_fill(M)

    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_horizon(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        if cfg["cue_scene_dressing"]:
            _dressing_report()
        print(f"[SMOKE] sceneD3 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views()
    _v0 = views["verge_walk"]
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
        sc.capture_pipeline(simulation_app, views, out_dir,
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneD3_{ts}.png")
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


if __name__ == "__main__":
    main()
