# -*- coding: utf-8 -*-
"""
scene17_ramp_pair_hangang.py — NegObs 인공씬 17호 (v5.1 재구성):
한강 제방 단면 — 둑길 → 잔디 사면 → 둔치 → 강 (Isaac Sim 4.5)

유형    : T21 램프-계단 대비쌍 (같은 낙차 3.2 m — 계단 vs 주행 가능 경사)
사양서  : Docs/audit_v4/user_feedback_v5_1.md §씬별 지시 17행
공통    : scene_common.py (build_slope/build_straight_stairs/build_rot_group/
          build_water/build_building/build_tree/add_sphere) · scene16 구조 준거
          (v6: 억새는 build_hedge 박스 → 대 군락·블롭으로 교체하며 호출 폐기)

[v5.1] 재구성 사유 (사용자: "정체 불명 · 억지 지형")
  구 버전은 옹벽 개구에서 계단과 **지그재그 2절 램프(페어레인 + 분리 파라펫)**
  가 튀어나오는 정체 불명의 구조물이었다. 실제 한강 제방에는 그런 형태가 없다.
  실제 단면은 단순하다:
      제방 마루(보도+자전거도로 폭 6) → **잔디 사면(구배 1:2, 높이 3.2)**
      → 둔치(산책로+잔디+벤치) → 호안 사석 → 넓은 수면 → 건너편 아파트·교량
  그 사면을 (a) **직선으로 관통하는 콘크리트 계단**(폭 3, 무난간 관행)과
  (b) **사면을 비스듬히 가로지르는 사선 단일 램프**(폭 2.5, 경사 8%)가
  같은 낙차 3.2 m 를 서로 다른 경사로 내려간다 — 대비쌍 학습 의도는 그대로,
  지형만 실제 한강으로 갈아엎었다.
  폐기: 지그재그 2절 · 페어레인(레인 A/B) · 분리 파라펫 · 옹벽 개구 3구간.

위험 본질
  둑길(z=0)에서 로봇 눈높이 h0.3 로 +X 를 보면, 마루 어깨(x=0)를 스치는 시선이
  사면(평균 50%)보다 훨씬 완만해 **사면·계단·둔치가 전부 시야에서 사라지고**
  둔치 원측(x ≥ 21)만 지평으로 남는다 → 근측 잔디와 연속 평면으로 읽힌다.
  방호는 없다(한강 제방 계단은 무난간이 관행). 사선 램프의 강측 가장자리도
  높이 1.5 m 석축 위 연석(h0.15)뿐이다 — 규정 미달의 현실.

목표
  ① 제방 마루(보도 3 + 자전거도로 3) + 마루 연석
  ② 잔디 사면 7세그 폴리라인(어깨 라운딩 25.7% → 하부 60%, 평균 50% = 1:2),
     계단 폭(y ±1.5)만 비우는 2 Y밴드 구성 — 세그 간 margin 겹침으로 틈 금지
  ③ 계단 20단(riser 0.16 · tread 0.32 · 폭 3) 사면 직선 관통
  ④ 사선 램프: rot_group(yaw 80.7931°) 안에서 build_slope 1장 — 길이 40 m,
     경사 8%, 폭 2.5, 상류측 절토면(최대 0.30 m) · 강측 석축(최대 1.53 m)
  ⑤ 둔치(산책로 폭 3 + 잔디 + 벤치 + 억새) · 호안 사석 · 넓은 수면 ·
     건너편 아파트 4동 · 교량 (기존 PARAMS 재사용)

보행 연속성 자가 검증표 (두 경로 모두 둑길 z=0 → 둔치 z=−3.2)
  ┌ #  구간              좌표(x, y, z)              단차/판정
  │ A0 둑길 자전거도로   (−1.50,  −6.00,  0.000)    평탄
  │ A1 마루 어깨(연단)   ( 0.00,   0.00,  0.000)    ← **낙차 3.20 무난간**
  │ A2 계단 1단          ( 0.32,   0.00, −0.160)    0.160
  │ A3 계단 20단         ( 6.40,   0.00, −3.200)    0.160 × 19
  │ A4 둔치 잔디         ( 7.20,   0.00, −3.200)    평탄 (계단 하단 flush)
  │ A5 산책로            (13.00,   0.00, −3.200)    평탄
  ├ B0 둑길 마루         (−0.60,   4.10,  0.000)    평탄
  │ B1 램프 상류 시단    ( 0.59,   3.90,  0.000)    마루 끝 대비 문턱 0.152
  │                                                 ([v7] 구 apron 프림 제거 —
  │                                                  PARAMS["ramp"]["apron"] 참조)
  │ B2 램프 s=10         ( 3.43,  13.58, −0.800)    경사 8%
  │ B3 램프 s=25         ( 5.83,  28.38, −2.000)    경사 8%
  │ B4 램프 종점 s=40    ( 8.23,  43.19, −3.200)    경사 8% → 둔치 flush
  └ B5 산책로 합류       (13.00,  43.00, −3.200)    평탄
  * 두 경로의 낙차가 같다(3.20) — 대비쌍의 근거. 계단 50% vs 램프 8%.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene17_ramp_pair_hangang.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python scene17_ramp_pair_hangang.py
스모크(부팅 없음):      NEGOBS_SMOKE=1  python scene17_ramp_pair_hangang.py

좌표계: Z-up, m, 진행축 +X(둑길 → 사면 → 물). **낙차 시작 모서리 x=0.**
  둑길 z=0 · 둔치 z=−3.2 · 수면 z=−3.42 · 건너편 둔치 z=−3.1.
"""

import os
import sys
import math
import json
import datetime
import random as _random          # [v6] 억새 군락·건너편 블롭 시드 고정 지터

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hazard_stairs 만 위험 기하 토글.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 사면·계단·램프를 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        False,   # 한강 제방 계단은 **무난간이 관행**. True → 계단 우측 파이프 레일 1선
    "cue_tactile":        False,   # 비관행(하천 시설) — 코드 경로만 예약
    "cue_material_break": True,    # 둑길 잔디/아스팔트 vs 계단·램프 콘크리트 대비
    "cue_sign":           False,   # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,    # 산책로·벤치·억새·가로등·아파트·교량
    "cue_nosing":         False,   # True → 전 단 단코 띠
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
_SLOPE_RUN = 6.4          # 사면 수평 (구배 1:2 · 높이 3.2)
_SLOPE_H = 3.2            # 사면 높이 = GT 낙차 (계단·램프 공통)
_TERRACE_Z = -_SLOPE_H    # 둔치 상면 -3.2

PARAMS = dict(
    # --- 제방 마루(둑길) : 잔디 성토체 위 보도(폭 3) + 자전거도로(폭 3) ---
    levee=dict(x0=-24.0, x1=0.0, y0=-30.0, y1=48.0, z_top=0.0, thick=3.6),
    crown_walk=dict(x0=-6.0, x1=-3.0, proud=0.006, embed=0.06),   # 보도(인터로킹)
    crown_bike=dict(x0=-3.0, x1=0.0, proud=0.004, embed=0.06),    # 자전거도로(아스팔트)
    crown_line=dict(x=-1.5, w=0.10, seg=2.4, gap=2.0, z=0.010),   # 자전거도로 중앙 파선
    # 마루 끝 연석 — 계단 개구(y ±1.5)와 램프 진입 apron(y 2.6..4.4)은 비운다
    cope=dict(x0=-0.20, x1=0.05, h=0.05,
              y_segs=((-30.0, -1.5), (1.5, 2.6), (4.4, 48.0))),
    # --- 잔디 사면: 7세그 폴리라인 (어깨 라운딩 → 하부 직선, 평균 50%) ---
    #     검증 규약: 각 세그 종점이 계단 현(z = −0.5x) **위**여야 계단이
    #     사면에 파묻히지 않는다(스모크 자동 검산).
    slope=dict(segs=((0.7, 0.18), (0.8, 0.34), (0.9, 0.50), (1.0, 0.58),
                     (1.0, 0.60), (1.0, 0.50), (1.0, 0.50)),
               thick=3.0, margin=0.25, y0=-30.0, y1=48.0),
    # --- 계단 20단 : 사면 직선 관통 (폭 3, 콘크리트, 무난간) ---
    stairs=dict(x0=0.0, riser=0.16, tread=0.32, nsteps=20,
                y0=-1.5, y1=1.5, z_top=0.0, base_z=-4.6),
    # --- 사선 단일 램프 : 사면을 비스듬히 가로지른다 ---
    #     길이 40 m · 경사 8% · 폭 2.5. 진행방위 yaw = acos(6.4/40) = 80.7931°
    #     (수평 40 m 중 X 로 6.4 m 만 전진 → 사면 구배 50% 를 8% 로 늘여 탄다)
    #     오프셋 e : 노면 상류(uphill) 가장자리를 사면-현 접선에서 강측으로
    #     e_up 만큼 민 값. e_up=0.6 이면 상류 절토면 0.07~0.30 m(매몰 0) 확보.
    #     [v6 판정 ㉠] 성토 노출면 처리: 강측 절단면(최대 1.53 m)이 "사면에 얹은
    #       콘크리트 블록"으로 읽혔다(judge_v6_rt_mod6 §6 — 현 시점 최대 억지 요소).
    #       원인은 ㉠ 재질 불연속(석축 rock_wall vs 주변 잔디) + ㉡ 평평한 상면 +
    #       수직 절단면. 램프 노면·경사·폭·시종점(= 위험 기하 GT)은 **불변**으로 두고
    #       마감만 바꾼다: Fill 재질을 사면 잔디와 동재질로 + 강측에 계단식 잔디
    #       배터(batter) 3단을 덧대 수직면을 분절한다.
    #       batter: n 단 × 폭 w × 낙차 dz (사면 구배 1:1.19 ≈ 40° — 잔디 성토
    #       어깨 관행). 3단 = 폭 1.50 · 낙차 1.26 로 노면 밑 최대 노출
    #       (1.53 − deck_t 0.35 = 1.18 m)를 전부 덮는다.
    #     [v7 판정 ⑪-1 — 수정 미반영 원인 규명] W-5 는 `Fill` 을 잔디로 바꿨는데
    #       판정은 "갈색 매스가 v6와 동일"이었다. levee_walk 카메라로 프림을
    #       역투영한 결과 그 매스는 **`Fill` 도 `Deck` 도 아닌 `Ramp/Apron`**
    #       이었다. 원인은 rot_group 안에서의 **로컬/월드 축 혼동**:
    #         · apron 은 "로컬 −X = 램프 뒤 = 마루 안쪽"이라고 가정하고
    #           local x ∈ [−1.4, 0], y ∈ [0.9, 5.2], 두께 2.8 m 로 놓였다.
    #         · 그러나 rot_group yaw = 80.793° 라 로컬 −X 는 월드 −X 가 아니라
    #           거의 월드 −Y 다. 실제 월드 풋프린트는 네 꼭짓점
    #           (3.06,3.50) (2.84,2.12) (−1.41,2.81) (−1.18,4.19) —
    #           **월드 x 가 +3.06 까지 사면 위로 튀어나온다.**
    #         · 그 지점 사면 상면은 z −1.40 인데 apron 상면은 −0.015 →
    #           사면 위로 **1.39 m 솟은 두께 2.8 m 콘크리트 블록**이 되고,
    #           수직 절단면이 프레임을 지배했다(= 판정이 말한 갈색 매스).
    #       → apron 을 rot_group 밖 **월드 정렬 마루 참**으로 재작성한다
    #         (아래 build_ramp_apron). 여기 파라미터는 그 월드 사각형이다.
    #         두께도 2.8 → 노면 두께 0.35 로 줄여 블록성을 제거.
    #     [v7 판정 ⑪-1 ㉠] 배터가 "인공 계단 3단"으로 읽힌 건 단 높이 0.42 m 가
    #       17 m 거리에서 또렷했기 때문. **폭·낙차 총량(1.50 × 1.26)은 그대로 두고**
    #       9단으로 잘게 쪼개 단 높이 0.14 m(판정 권고 ≤0.15)로 낮춘다 = 연속 사면.
    ramp=dict(p0=(0.0, 4.0), length=40.0, width=2.5, e_up=0.60,
              deck_t=0.35, fill_t=2.0, fill_out=0.10,
              curb_w=0.15, curb_h=0.15,
              batter=dict(n=9, w=0.1667, dz=0.14, margin=0.30),
              apron=dict(build=False, x0=-1.60, x1=0.05, y0=0.60, y1=5.40,
                         t=0.35, drop=0.015)),
    # --- 둔치(고수부지) : 잔디 + 산책로(폭 3, 강 평행) ---
    terrace=dict(x0=6.4, x1=27.5, y0=-30.0, y1=48.0, z_top=_TERRACE_Z,
                 thick=1.0),
    promenade=dict(x0=11.5, x1=14.5, proud=0.004, line_w=0.10, line_in=0.18),
    # --- 호안 사석 + 수면 + 건너편 ---
    bank=dict(x0=27.5, run=2.0, drop=0.45, thick=1.2, margin=0.2),
    water=dict(x0=28.6, x1=72.0, y0=-42.0, y1=60.0, z=-3.42),
    far_bank=dict(x0=72.0, x1=100.0, y0=-42.0, y1=60.0, z_top=-3.1, thick=0.5),
    # [v6 판정 ㉡] 건너편 억새 띠 — build_hedge 직육면체 → 편평 타원체 열(블롭).
    #   spacing 간격으로 심고 크기·위치에 시드 지터(§3 등간격 금지).
    #   [v7 판정 ⑪-2] 구 구성은 **1열 · 등간격(spacing 1.55, y지터 ±0.3 뿐)**
    #     이라 76 m 원경에서 "동일 크기 카키 구슬 목걸이"로 읽혔다(§3 등간격 금지).
    #     → ① 밴드 폭 방향 3열 엇갈림(dx 로 전후 배치, 열마다 y 위상 어긋남)
    #        ② 간격을 spacing × U(0.55, 1.60) 으로 **랜덤 보행**(등간격 소멸)
    #        ③ 크기 0.60~1.45× · 높이 0.70~1.25× 지터(판정 권고 대역)
    #        ④ 뒷열을 크고 높게, 앞열을 작고 낮게 → 띠에 깊이가 생긴다.
    far_hedge=dict(cx=76.0, sx=1.2, length=26.0, h=1.7, spacing=1.55,
                   rad=0.80,
                   rows=((-1.15, 1.18, 0.00), (0.00, 1.00, 0.37),
                         (1.25, 0.82, 0.68))),
    far_hedges=[dict(cy=-26.0), dict(cy=3.0), dict(cy=32.0)],
    far_trees=[dict(cx=80.4, cy=-19.0), dict(cx=79.1, cy=7.0),
               dict(cx=80.9, cy=34.0)],
    # [v6 판정 ㉢] 건너편 아파트 — "4동 동일 형상·동일 간격 격자 정렬" 해소.
    #   구: x0 88.0 고정(H만 89.5) · 폭 20/20/18/16 · 이격 8/6/6 · 높이 42/48/38/44
    #       → 파사드가 한 평면에 늘어서고 실루엣이 반복 격자로 읽혔다(§3 위반 인상).
    #   신: ① 후퇴(x0) 85.5~90.5 로 3.0 m 편차 → 파사드 평면 해체(원근 깊이 생성)
    #       ② 폭 17/23/15/17, 이격 8/5/11 → 반복 주기 소멸
    #       ③ 높이 36/49/41/30.5 · 층수 12/16/14/10 (층고 2.93~3.06 m 실제 대역)
    #       ④ 틴트 4종 순환(shell / shell_c / shell_b / shell_d) — 인접 동 색 상이
    #   전부 원경 배경물이라 위험 기하·보행 연속성과 무관. far_bank x 72..100 내.
    far_buildings=dict(
        E=dict(x0=86.5, x1=94.5, y0=-38.0, y1=-21.0, h=36.0, floors=12,
               axis="x", facade_x=86.5, face_dir=-1.0, base_z=-3.1),
        F=dict(x0=89.0, x1=97.0, y0=-13.0, y1=10.0, h=49.0, floors=16,
               axis="x", facade_x=89.0, face_dir=-1.0, base_z=-3.1),
        G=dict(x0=85.5, x1=93.5, y0=15.0, y1=30.0, h=41.0, floors=14,
               axis="x", facade_x=85.5, face_dir=-1.0, base_z=-3.1),
        H=dict(x0=90.5, x1=98.5, y0=41.0, y1=58.0, h=30.5, floors=10,
               axis="x", facade_x=90.5, face_dir=-1.0, base_z=-3.1),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.6, margin=2.0),
    bridge=dict(x0=42.0, x1=46.0, y0=-42.0, y1=60.0, deck_top=6.0,
                deck_t=1.2, pier_r=1.2, pier_x=44.0,
                pier_ys=(-30.0, -10.0, 12.0, 34.0, 54.0), pier_base=-3.7),

    # --- 드레싱 (배치 비정형: 등간격 금지, 앵커 옆, yaw 지터) ---
    #     램프 풋프린트(사선 스트립)와 계단 폭은 피해서 배치한다.
    # [v6 판정 ㉡] 억새 띠 — build_hedge 직육면체(카키 박스 = 볏짚더미/컨테이너
    #   인상)를 **대(stalk) 군락**으로 교체. scene09 build_reeds 규약 이식
    #   (얇은 원기둥 r0.022 · 높이 지터 · 소각 기울기 · 씨앗 고정 재현).
    #   밴드 사각형은 그대로 두고 그 안에 density[본/m²] 로 흩뿌린다.
    reeds=[dict(x0=24.6, y0=-18.0, x1=26.4, y1=-6.5, h=1.35, seed=171),
           dict(x0=24.9, y0=5.0, x1=26.6, y1=15.8, h=1.25, seed=172),
           dict(x0=25.2, y0=26.0, x1=26.8, y1=33.4, h=1.40, seed=173),
           dict(x0=7.4, y0=-27.0, x1=8.9, y1=-20.2, h=1.10, seed=174)],
    reed=dict(r=0.022, density=6.0, h_lo=0.80, h_hi=1.12, tilt=9.0),
    reed_tint=(0.42, 0.44, 0.26),
    terrace_trees=[(17.6, -14.2), (19.8, 8.6), (16.9, 30.1), (21.4, 39.7),
                   (18.2, -23.5)],
    terrace_benches=[(16.2, -13.0, 96.0), (16.4, 9.8, -84.0),
                     (15.9, 29.2, 93.0), (10.6, -21.4, -86.0)],
    terrace_lights=[(15.1, -19.0), (15.1, 1.5), (15.1, 22.0), (15.1, 41.0)],
    crown_lights=[(-6.4, -12.0), (-6.4, 9.5), (-6.4, 31.0)],
    streetlight=dict(pole_h=4.6, pole_r=0.075, arm_len=1.0, arm_r=0.045,
                     head=0.25),
    crown_trees=[(-11.2, -8.4), (-14.6, 12.7), (-9.8, 33.2), (-17.1, -19.6)],
    km_sign=dict(x=14.9, y=-4.6, pole_r=0.05, pole_h=2.2,
                 panel=(0.06, 0.7, 0.42), panel_z=1.95),

    material=dict(
        scale=dict(concrete_floor=0.9, paving_interlock=1.2, grass=1.4,
                   rock_wall=1.6),
        grass_tint=(0.54, 0.66, 0.41),
        grass_tint_b=(0.49, 0.62, 0.38),          # 사면 잔디(틴트 지터 −5%)
        # [v7 판정 ⑪-1] `concrete_floor` diff 평균은 sRGB (115.7,102.2,77.0) =
        #   난색 갈토다. 구 틴트 (0.80,0.79,0.76) 은 채널비를 그대로 두어
        #   렌더 결과가 sRGB (98,87,69) — **갈색**. 램프 노면·연석·마루 연석·
        #   계단이 전부 이 재질이라 "갈색 매스" 인상의 절반은 색이었다.
        #   → 선형 채널 등화(scene06/11 W-1 규약과 동일): 최저 채널(B) 기준으로
        #   R·G 를 눌러 sRGB (80,79,78) ≈ 중성 회색 콘크리트로 만든다.
        conc_tint=(0.53, 0.66, 1.00),
        paving_tint=(0.84, 0.83, 0.81),
        rock_tint=(0.72, 0.71, 0.68),
        asphalt_color=(0.145, 0.145, 0.155), asphalt_rough=0.86,
        paint_color=(0.70, 0.70, 0.66), paint_rough=0.62,   # 순백 금지(<0.8)
        water_color=(0.05, 0.10, 0.11), water_rough=0.06,
        rail_color=(0.66, 0.68, 0.70), rail_metallic=0.7, rail_rough=0.4,
        wood_color=(0.28, 0.19, 0.12), wood_rough=0.85,
        post_color=(0.33, 0.33, 0.36), post_metallic=0.35, post_rough=0.5,
        glass_color=(0.055, 0.075, 0.10), glass_rough=0.08,
        parapet_color=(0.60, 0.60, 0.58), parapet_rough=0.62,
        shell_tint=(0.84, 0.82, 0.79), shell_tint_b=(0.78, 0.77, 0.76),
        # [v6 판정 ㉢] 아파트 동별 틴트 4종 순환용 추가 2종
        shell_tint_c=(0.80, 0.77, 0.71), shell_tint_d=(0.73, 0.74, 0.73),
        bridge_color=(0.045, 0.045, 0.050), bridge_rough=0.7,
        lamp_color=(0.78, 0.78, 0.74), lamp_rough=0.4,
        sign_color=(0.05, 0.09, 0.16), sign_rough=0.5,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
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
    SUN_AZ_OFFSET=171.5,

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
# [C] 경로 + 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene17")
ASSET_ROLES = ["concrete_floor", "paving_interlock", "grass", "rock_wall",
               "hdri", "mdl"]


# ===========================================================================
# [C2] 사면·램프 기하 — 전 함수 공용 단일 진실원
# ===========================================================================
def slope_nodes():
    """사면 폴리라인 절점 [(x, z), ...] (x=0,z=0 시작)."""
    x, z = 0.0, 0.0
    nodes = [(0.0, 0.0)]
    for run, drop in PARAMS["slope"]["segs"]:
        x += run
        z -= drop
        nodes.append((round(x, 6), round(z, 6)))
    return nodes


def slope_z(xq):
    """사면 표면 z(x). x<0 은 마루(0), x>사면끝은 둔치."""
    if xq <= 0.0:
        return 0.0
    x, z = 0.0, 0.0
    for run, drop in PARAMS["slope"]["segs"]:
        if xq <= x + run + 1e-12:
            return z - drop * (xq - x) / run
        x += run
        z -= drop
    return z


def ramp_geom():
    """사선 램프의 방위·단위벡터. 반환 dict:
      yaw   : rot_group 회전각(도). 로컬 +X → 진행방향 d, 로컬 +Y → −n(상류측)
      d     : 진행 단위벡터(평면), n : 강측(하류) 법선 단위벡터
      length/drop/grade, e_up/e_dn : 상·하류 가장자리 오프셋(강측 +)
    수식: 노면이 사면 현(구배 50%)을 8% 로 늘여 타려면 진행 1 m 당 X 전진이
      dx = grade/0.5 = 0.16 m 여야 한다 → cos(yaw) = 0.16."""
    rp = PARAMS["ramp"]
    L = float(rp["length"])
    drop = float(_SLOPE_H)
    cos_p = float(_SLOPE_RUN) / L                  # 0.16
    sin_p = math.sqrt(max(0.0, 1.0 - cos_p * cos_p))
    return dict(yaw=math.degrees(math.acos(cos_p)),
                d=(cos_p, sin_p), n=(sin_p, -cos_p),
                length=L, drop=drop, grade=drop / L,
                e_up=float(rp["e_up"]),
                e_dn=float(rp["e_up"]) + float(rp["width"]))


def ramp_point(s, e):
    """램프 경로 매개변수 (s: 진행거리, e: 강측 횡오프셋) → 월드 (x, y, z)."""
    g = ramp_geom()
    px, py = PARAMS["ramp"]["p0"]
    x = px + g["d"][0] * s + g["n"][0] * e
    y = py + g["d"][1] * s + g["n"][1] * e
    return (x, y, -g["grade"] * s)


# ===========================================================================
# [C3] 스모크 — 부팅 전 기하 자기검증 (조기종료)
# ===========================================================================
def _smoke_report():
    st = PARAMS["stairs"]
    rp = PARAMS["ramp"]
    sl = PARAMS["slope"]
    te = PARAMS["terrace"]
    wt = PARAMS["water"]
    g = ramp_geom()

    print("=" * 74)
    print("scene17_ramp_pair_hangang — SMOKE 기하 자기검증 (부팅 없음, v5.1)")
    print("=" * 74)

    # ── 사면 폴리라인 (구배 1:2) ──
    nodes = slope_nodes()
    print(f"  [잔디 사면 폴리라인]  {len(sl['segs'])}세그 · 두께 "
          f"{sl['thick']:.1f} · 세그 margin {sl['margin']:.2f}(겹침)")
    ok_chord = True
    for i, (run, drop) in enumerate(sl["segs"]):
        x0, z0 = nodes[i]
        x1, z1 = nodes[i + 1]
        above = z1 >= -0.5 * x1 - 1e-9
        ok_chord &= above
        print(f"    seg{i + 1}: x {x0:5.2f} → {x1:5.2f}  z {z0:+.3f} → "
              f"{z1:+.3f}  구배 {drop / run * 100:5.1f}%  "
              f"현(−0.5x) 대비 {'위 OK' if above else '아래 FAIL'}")
    tot_run = nodes[-1][0]
    tot_drop = -nodes[-1][1]
    print(f"    총 {tot_run:.2f} × {tot_drop:.2f} → 평균 구배 "
          f"{tot_drop / tot_run * 100:.1f}% (1:2 = 50%) → "
          f"{'OK' if abs(tot_drop / tot_run - 0.5) < 1e-6 else 'FAIL'}")
    print(f"    계단 매몰 방지(전 절점이 현 위): "
          f"{'OK' if ok_chord else 'FAIL'}")

    # ── 대비쌍 ──
    sdrop = st["nsteps"] * st["riser"]
    srun = st["nsteps"] * st["tread"]
    print("  [대비쌍: 같은 낙차 · 다른 경사]")
    print(f"    계단 {st['nsteps']}단 × riser {st['riser']} = 낙차 "
          f"{sdrop:.2f} · run {srun:.2f} → 경사 {sdrop / srun * 100:.0f}% "
          f"(폭 {st['y1'] - st['y0']:.1f}, 무난간 관행)")
    print(f"    램프 길이 {g['length']:.1f} · 낙차 {g['drop']:.2f} → 경사 "
          f"{g['grade'] * 100:.1f}% (폭 {rp['width']:.1f}, 사선 단일로)")
    print(f"    낙차 일치 {sdrop:.2f} ≈ {g['drop']:.2f} → "
          f"{'OK' if abs(sdrop - g['drop']) < 1e-6 else 'FAIL'} · "
          f"계단 run {srun:.2f} = 사면 수평 {tot_run:.2f} → "
          f"{'OK' if abs(srun - tot_run) < 1e-6 else 'FAIL'}")
    print(f"    낙차 검증: {sdrop:.2f} ≥ 0.3 m → "
          f"{'OK' if sdrop >= 0.3 else 'FAIL'}")

    # ── 램프 사선 배치 · 절토/성토 검산 ──
    p_end = ramp_point(g["length"], (g["e_up"] + g["e_dn"]) / 2.0)
    print("  [사선 램프 배치]")
    print(f"    yaw {g['yaw']:.4f}° (cos = {_SLOPE_RUN}/{g['length']:.0f} = "
          f"{g['d'][0]:.3f}) · 시점 {rp['p0']} · 종점 중심 "
          f"({p_end[0]:.2f}, {p_end[1]:.2f}, {p_end[2]:+.2f})")
    print(f"    상류 절토(+) / 매몰(−) · 강측 석축 높이:")
    worst_cut, worst_face = 9.9, 0.0
    for s in (0.0, 6.0, 12.0, 20.0, 28.0, 34.0, 40.0):
        deck = -g["grade"] * s
        xu = g["d"][0] * s + g["n"][0] * g["e_up"]
        xd = g["d"][0] * s + g["n"][0] * g["e_dn"]
        tu = slope_z(xu) if xu <= tot_run else te["z_top"]
        td = slope_z(xd) if xd <= tot_run else te["z_top"]
        cut = deck - tu
        face = deck - td
        worst_cut = min(worst_cut, cut)
        worst_face = max(worst_face, face)
        print(f"      s{s:5.1f}  노면 {deck:+.3f} · 상류edge x{xu:5.2f} "
              f"지반 {tu:+.3f} → 절토 {cut:+.3f} · 강측edge x{xd:5.2f} "
              f"지반 {td:+.3f} → 석축 {face:.3f}")
    print(f"    최소 절토 {worst_cut:+.3f} ≥ 0 (음수면 노면이 잔디에 매몰) → "
          f"{'OK' if worst_cut >= -1e-9 else 'FAIL'}")
    fill_bot = rp["deck_t"] + rp["fill_t"]
    print(f"    최대 석축 {worst_face:.3f} < 성토 두께 {fill_bot:.2f} "
          f"(노면 밑 {fill_bot:.2f} m 까지 솔리드) → "
          f"{'OK (부유 없음)' if worst_face < fill_bot else 'FAIL'}")

    # ── [v6 판정 ㉠] 강측 잔디 배터 검산 ──
    bt = rp["batter"]
    n_bt, w_bt, dz_bt = int(bt["n"]), float(bt["w"]), float(bt["dz"])
    e_toe = g["e_dn"] + rp["fill_out"] + w_bt * n_bt
    print(f"  [강측 잔디 배터] {n_bt}단 × 폭 {w_bt:.2f} × 낙차 {dz_bt:.2f} "
          f"= 폭 {w_bt * n_bt:.2f} · 낙차 {dz_bt * n_bt:.2f} "
          f"(구배 {dz_bt / w_bt * 100:.0f}% ≈ 1:{w_bt / dz_bt:.2f})")
    print(f"    덮어야 할 노면 밑 최대 노출 = 최대석축 {worst_face:.3f} − "
          f"노면두께 {rp['deck_t']:.2f} = {worst_face - rp['deck_t']:.3f} m → "
          f"{'OK (배터 낙차가 더 큼)' if dz_bt * n_bt >= worst_face - rp['deck_t'] else 'FAIL'}")
    worst_res, x_toe_max, y_toe_min = 0.0, -99.0, 99.0
    for s in (0.0, 6.0, 12.0, 20.0, 28.0, 34.0, 40.0):
        deck = -g["grade"] * s
        z_toe = deck - rp["deck_t"] - dz_bt * n_bt
        x_toe = g["d"][0] * s + g["n"][0] * e_toe
        y_toe = rp["p0"][1] + g["d"][1] * s + g["n"][1] * e_toe
        gz = slope_z(x_toe) if x_toe <= tot_run else te["z_top"]
        res = max(0.0, z_toe - gz)
        worst_res = max(worst_res, res)
        x_toe_max, y_toe_min = max(x_toe_max, x_toe), min(y_toe_min, y_toe)
        print(f"      s{s:5.1f}  배터 끝 (x{x_toe:5.2f}, y{y_toe:6.2f}) "
              f"상면 {z_toe:+.3f} · 지반 {gz:+.3f} → 잔여 잔디면 {res:.3f}")
    print(f"    잔여 최대 {worst_res:.3f} m (구 수직 절단면 {worst_face:.3f} m "
          f"대비 −{(1 - worst_res / worst_face) * 100:.0f}%) · 전 구간 잔디 재질")
    print(f"    배터 풋프린트: x ≤ {x_toe_max:.2f} < 산책로 x0 "
          f"{PARAMS['promenade']['x0']:.1f} → "
          f"{'OK' if x_toe_max < PARAMS['promenade']['x0'] else 'FAIL'} · "
          f"y ≥ {y_toe_min:.2f} > 계단 y1 {st['y1']:.1f} → "
          f"{'OK (계단 무간섭)' if y_toe_min > st['y1'] else 'FAIL'}")

    # ── [v7 판정 ⑪-1] 진입 apron 풋프린트 검산 (갈색 매스 재발 방지) ──
    #   구 apron 은 rot_group(yaw) 안에 있어 로컬 좌표를 월드로 착각한 결과
    #   월드 x +3.06 까지 사면 위로 나갔다. 그 재현 계산을 남겨 대조한다.
    cy_, sy_ = (math.cos(math.radians(g["yaw"])),
                math.sin(math.radians(g["yaw"])))
    px0, py0 = rp["p0"]

    def _rot_world(lx, ly):
        vx, vy = lx - px0, ly - py0
        return (px0 + vx * cy_ - vy * sy_, py0 + vx * sy_ + vy * cy_)

    old_pts = [_rot_world(lx, ly) for lx in (-1.4, 0.0)
               for ly in (rp["p0"][1] - g["e_dn"], rp["p0"][1] + 1.2)]
    old_xmax = max(p[0] for p in old_pts)
    ap = rp["apron"]
    print("  [진입 apron 풋프린트 — v7 판정 ⑪-1 갈색 매스]")
    print(f"    구(rot_group 내부, 두께 2.80): 월드 꼭짓점 "
          f"{[(round(a, 2), round(b, 2)) for a, b in old_pts]}")
    print(f"      → 월드 x 최대 {old_xmax:+.2f} (사면 상면 "
          f"{slope_z(old_xmax):+.2f}) = 사면 위 "
          f"{-ap['drop'] - slope_z(old_xmax):+.2f} m 돌출 → 갈색 블록의 정체")
    thresh = -g["grade"] * 0.0 - slope_z(g["n"][0] * g["e_up"])
    print(f"    신: 빌드 생략(build={ap['build']}) — 대체 필요 없음. 마루 끝"
          f"(x 0) ~ 램프 상류 시단(x {g['n'][0]*g['e_up']:.2f}) 사이 문턱 "
          f"{thresh:.3f} m < 계단 riser {st['riser']:.2f} → "
          f"{'OK (별도 프림 불요)' if thresh < st['riser'] else 'FAIL'}")
    print(f"      프레임 갈색 매스 잔존 가능 프림: "
          f"{'없음 → OK' if not ap['build'] else 'Apron 재빌드됨 → 확인 요'}")

    # ── [v6 판정 ㉢] 건너편 아파트 변주 검산 ──
    fb2 = PARAMS["far_buildings"]
    print("  [건너편 아파트 4동 — 격자/동일 인상 해소]")
    prev_y1 = None
    for key, bd in fb2.items():
        gap = "" if prev_y1 is None else f"이격 {bd['y0'] - prev_y1:5.1f}"
        print(f"    {key}: x0 {bd['x0']:5.1f} · 폭 {bd['y1'] - bd['y0']:5.1f} · "
              f"h {bd['h']:5.1f} ({bd['floors']:2d}층, 층고 "
              f"{bd['h'] / bd['floors']:.2f}) {gap}")
        prev_y1 = bd["y1"]
    xs = sorted(set(round(b["x0"], 2) for b in fb2.values()))
    gaps = [round(list(fb2.values())[i + 1]["y0"] - list(fb2.values())[i]["y1"], 1)
            for i in range(len(fb2) - 1)]
    fbk = PARAMS["far_bank"]
    inside = all(fbk["x0"] <= b["x0"] and b["x1"] <= fbk["x1"]
                 for b in fb2.values())
    print(f"    후퇴(x0) {len(xs)}종 {xs} · 이격 {gaps} (동일값 반복 없음: "
          f"{len(set(gaps)) == len(gaps)}) · far_bank "
          f"[{fbk['x0']:.0f},{fbk['x1']:.0f}] 내 {inside}")

    # ── [v6 판정 ㉡] 억새 군락 검산 ──
    rd = PARAMS["reed"]
    tot_stalk = sum(int(round((r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
                              * rd["density"])) for r in PARAMS["reeds"])
    fh = PARAMS["far_hedge"]
    import random as _rnd_chk
    n_far, gaps_far = 0, []
    for i in range(len(PARAMS["far_hedges"])):
        for ri, (dx, sk, phase) in enumerate(fh["rows"]):
            r_ = _rnd_chk.Random((i + 1) * 26417 ^ (ri + 1) * 6151)
            yy, prev = fh["spacing"] * phase, None
            while yy <= fh["length"]:
                r_.uniform(0.70, 1.25), r_.uniform(0.60, 1.45)
                r_.uniform(-0.30, 0.30), r_.uniform(0.8, 1.4)
                if prev is not None:
                    gaps_far.append(round(yy - prev, 2))
                prev = yy
                yy += fh["spacing"] * r_.uniform(0.55, 1.60)
                n_far += 1
    print(f"  [억새 군락] 근경 {len(PARAMS['reeds'])}밴드 · 밀도 "
          f"{rd['density']:.1f} 본/m² → 대 {tot_stalk}본 "
          f"(r {rd['r']:.3f} · h {rd['h_lo']:.2f}~{rd['h_hi']:.2f}× · "
          f"기울기 {rd['tilt']:.0f}°)")
    print(f"    [v7 판정 ⑪-2] 건너편 억새: {len(PARAMS['far_hedges'])}띠 × "
          f"{len(fh['rows'])}열(dx {[r[0] for r in fh['rows']]}) → 블롭 {n_far}개 · "
          f"간격 {min(gaps_far):.2f}~{max(gaps_far):.2f} m "
          f"(구: 1열 등간격 {fh['spacing']:.2f} 고정) → "
          f"{'OK (등간격 소멸)' if len(set(gaps_far)) > len(gaps_far) * 0.5 else 'FAIL'}")

    # ── z 위계 플레이트 표 ──
    lv = PARAMS["levee"]
    fb = PARAMS["far_bank"]
    plates = [
        ("Levee(grass)", lv["x0"], lv["x1"], lv["y0"], lv["y1"], lv["z_top"]),
        ("CrownWalk(paving)", PARAMS["crown_walk"]["x0"],
         PARAMS["crown_walk"]["x1"], lv["y0"], lv["y1"],
         lv["z_top"] + PARAMS["crown_walk"]["proud"]),
        ("CrownBike(asphalt)", PARAMS["crown_bike"]["x0"],
         PARAMS["crown_bike"]["x1"], lv["y0"], lv["y1"],
         lv["z_top"] + PARAMS["crown_bike"]["proud"]),
        ("Slope(grass)", 0.0, tot_run, sl["y0"], sl["y1"], -1.6),
        ("Terrace(grass)", te["x0"], te["x1"], te["y0"], te["y1"],
         te["z_top"]),
        ("Promenade(asphalt)", PARAMS["promenade"]["x0"],
         PARAMS["promenade"]["x1"], te["y0"], te["y1"],
         te["z_top"] + PARAMS["promenade"]["proud"]),
        ("Bank(rock)", PARAMS["bank"]["x0"],
         PARAMS["bank"]["x0"] + PARAMS["bank"]["run"], te["y0"], te["y1"],
         te["z_top"] - PARAMS["bank"]["drop"]),
        ("Water(river)", wt["x0"], wt["x1"], wt["y0"], wt["y1"], wt["z"]),
        ("FarBank(grass)", fb["x0"], fb["x1"], fb["y0"], fb["y1"],
         fb["z_top"]),
    ]
    print("  [지면·수면 플레이트 표] (물가 위계: 둔치 −3.20 > 수면 −3.42)")
    print(f"    {'이름':22s} {'x범위':>16s} {'y범위':>16s}  상면z")
    for nm, x0, x1, y0, y1, z in plates:
        print(f"    {nm:22s} [{x0:6.1f},{x1:6.1f}] [{y0:6.1f},{y1:6.1f}]  "
              f"{z:+.3f}")
    offenders = [nm for nm, x0, x1, y0, y1, z in plates
                 if nm not in ("Water(river)", "Bank(rock)")
                 and not (x1 <= wt["x0"] or x0 >= wt["x1"]) and z < wt["z"]]
    print(f"    수면({wt['z']:+.2f}) 와 x겹침 중 더 낮은 지면: "
          f"{offenders if offenders else '없음 → OK'}")
    print(f"    호안: 둔치 {te['z_top']:+.2f} → 사석 사면 "
          f"{te['z_top'] - PARAMS['bank']['drop']:+.2f} (수면 {wt['z']:+.2f} "
          f"아래로 잠김) → "
          f"{'OK' if te['z_top'] - PARAMS['bank']['drop'] < wt['z'] else 'FAIL'}")

    # ── grazing 은닉 검산 ──
    print("  [h0.3/h0.9 grazing 은닉 검산] 마루 어깨(x=0,z=0) 스치는 시선")
    for h in (0.3, 0.9):
        for d in (2.0, 5.0, 10.0):
            k = h / d                                   # 시선 하강 기울기
            x_hit = te["z_top"] / -k                    # 둔치(-3.2)에 닿는 x
            hid = x_hit > tot_run
            print(f"    h{h:.1f} d{d:4.1f} → 시선이 −3.20 에 닿는 x = "
                  f"{x_hit:6.1f} vs 사면 끝 {tot_run:.1f} → "
                  f"{'사면·계단 전부 은닉 OK' if hid else '사면 일부 노출'}")
    print("    ⇒ 은닉 컷에서는 둔치 원측만 지평으로 남아 근측 잔디와 "
          "연속 평면으로 읽힌다(negative obstacle 성립).")
    print("=" * 74)


# ===========================================================================
# [D] 카메라 프리셋
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)
    # pair_compare: 계단(y 0)과 사선 램프(y 4 → 43)를 한 화면에 — 대비쌍 핵심.
    #   [v5.1 재조준] 지그재그 폐기로 램프가 +Y 로 40 m 뻗는다 → 남서 고각
    #   부감으로 재조준. 검산(eye −20,−13,15): 계단 중심 오프축 14.6°,
    #   램프 s=20 13.8°, 램프 종점 21.1° (전부 hFOV 30° 이내), 부각은
    #   계단 32.0° · 종점 16.3° 로 카메라 피치 24.6° ±17.5° 안.
    views["pair_compare"] = dict(eye=[-20.0, -13.0, 15.0], tgt=[7.0, 13.0, -2.2])
    # levee_walk: 둑길 종주(+Y) — 사면·계단·둔치가 전부 소실되는 grazing
    views["levee_walk"] = dict(eye=[-1.5, -14.0, 1.50], tgt=[-1.3, 6.0, 0.90])
    # ramp_run: 사선 램프 종주 (노면 위 눈높이)
    views["ramp_run"] = dict(eye=[2.15, 5.68, 1.39], tgt=[5.35, 25.40, -1.50])
    # across_river: 둑길에서 계단·둔치·강·건너편 스카이라인 조망
    views["across_river"] = dict(eye=[-4.0, 0.5, 1.60], tgt=[22.0, 2.0, -2.60])
    # toe_lookup: 둔치에서 사면·계단을 올려봄 (계단 실체 확인 컷)
    views["toe_lookup"] = dict(eye=[14.0, -6.0, -1.60], tgt=[3.5, -0.3, -1.20])
    return views


# ===========================================================================
# [E] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. pair_compare  — 같은 낙차의 계단(50%) vs 사선 램프(8%)가 한 화면에 대비되는가
 2. levee_walk·h0.3 — 둑길 grazing 에서 사면·계단·둔치가 소실되는가(특색)
 3. ramp_run      — 사선 단일로가 사면을 비스듬히 가로지르는가(지그재그 폐기)
 4. toe_lookup    — 사면 잔디 곡률(어깨 라운딩)·계단 절개면이 자연스러운가
 5. across_river  — 산책로·억새·호안·수면·건너편 아파트/교량 지평
 6. 접합          — 마루/사면/둔치/호안/수면 경계에 부유·틈·Z파이팅 없는가
 7. [v6] 융화     — 램프 성토가 잔디 배터로 사면에 녹아드는가(갈색 블록 소멸),
                    억새가 박스가 아니라 대(stalk) 군락으로 보이는가,
                    건너편 아파트가 격자 반복이 아닌가
 8. [v7] 갈색 매스 — levee_walk 우중앙에 **평평한 상면 + 수직면 갈색 블록**이
                    완전히 사라졌는가(정체 = 구 Ramp/Apron, 빌드 제거).
                    남는 램프 노면·연석·계단이 갈색이 아니라 **중성 회색
                    콘크리트**인가(conc_tint 채널 등화).
 9. [v7] 배터·억새 — 강측 배터가 '계단 3단'이 아니라 연속 사면으로 읽히는가
                    (9단 × 0.14 m), 건너편 억새가 등간격 구슬열이 아니라
                    3열 엇갈림 군락으로 읽히는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        _smoke_report()
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode)

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
    UsdGeom.Xform.Define(stage, "/World/Scene17")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene17"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # 재질 (틴트 지터 변종 포함)
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["conc"] = PBR(
            f"{ROOT}/Looks/Concrete", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["conc_tint"])
        M["paving"] = PBR(
            f"{ROOT}/Looks/Paving", sc.tex_path("paving_interlock", "diff"),
            sc.tex_path("paving_interlock", "nor"),
            sc.tex_path("paving_interlock", "rough"),
            sca["paving_interlock"], tint=mp["paving_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["grass_b"] = PBR(
            f"{ROOT}/Looks/GrassB", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint_b"])
        M["rock"] = PBR(
            f"{ROOT}/Looks/Rock", sc.tex_path("rock_wall", "diff"),
            sc.tex_path("rock_wall", "nor"), sc.tex_path("rock_wall", "rough"),
            sca["rock_wall"], tint=mp["rock_tint"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"])
        M["paint"] = PBR(f"{ROOT}/Looks/Paint", diffuse_color=mp["paint_color"],
                         roughness_const=mp["paint_rough"])
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["shell"] = PBR(f"{ROOT}/Looks/Shell",
                         sc.tex_path("concrete_floor", "diff"),
                         sc.tex_path("concrete_floor", "nor"),
                         sc.tex_path("concrete_floor", "rough"),
                         sca["concrete_floor"], tint=mp["shell_tint"])
        M["shell_b"] = PBR(f"{ROOT}/Looks/ShellB",
                           sc.tex_path("concrete_floor", "diff"),
                           sc.tex_path("concrete_floor", "nor"),
                           sc.tex_path("concrete_floor", "rough"),
                           sca["concrete_floor"], tint=mp["shell_tint_b"])
        for tag in ("c", "d"):
            M[f"shell_{tag}"] = PBR(
                f"{ROOT}/Looks/Shell{tag.upper()}",
                sc.tex_path("concrete_floor", "diff"),
                sc.tex_path("concrete_floor", "nor"),
                sc.tex_path("concrete_floor", "rough"),
                sca["concrete_floor"], tint=mp[f"shell_tint_{tag}"])
        M["reed"] = PBR(f"{ROOT}/Looks/Reed", sc.tex_path("grass", "diff"),
                        sc.tex_path("grass", "nor"),
                        sc.tex_path("grass", "rough"),
                        0.6, tint=PARAMS["reed_tint"])
        M["bridge"] = PBR(f"{ROOT}/Looks/Bridge",
                          diffuse_color=mp["bridge_color"],
                          roughness_const=mp["bridge_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=mp["sign_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        return M

    # -------------------------------------------------------------------
    # 제방 마루(둑길) — 성토체 + 보도/자전거도로 밴드 + 마루 연석
    # -------------------------------------------------------------------
    def build_levee(M):
        lv = PARAMS["levee"]
        cy = (lv["y0"] + lv["y1"]) / 2.0
        Ly = lv["y1"] - lv["y0"]
        BOX(f"{ROOT}/Levee",
            ((lv["x0"] + lv["x1"]) / 2.0, cy, lv["z_top"] - lv["thick"] / 2.0),
            (lv["x1"] - lv["x0"], Ly, lv["thick"]), M["grass"], col=True)
        for key, mtl in (("crown_walk", M["paving"]),
                         ("crown_bike", M["asphalt"])):
            b = PARAMS[key]
            z_hi = lv["z_top"] + b["proud"]
            z_lo = lv["z_top"] - b["embed"]
            BOX(f"{ROOT}/{key.split('_')[1].capitalize()}Band",
                ((b["x0"] + b["x1"]) / 2.0, cy, (z_hi + z_lo) / 2.0),
                (b["x1"] - b["x0"], Ly, z_hi - z_lo), mtl, col=True)
        # 자전거도로 중앙 파선
        cl = PARAMS["crown_line"]
        step = cl["seg"] + cl["gap"]
        n = int(Ly / step)
        for i in range(n):
            yy = lv["y0"] + 1.0 + i * step + cl["seg"] / 2.0
            if yy > lv["y1"] - 1.0:
                break
            BOX(f"{ROOT}/CrownLine_{i}", (cl["x"], yy, cl["z"] - 0.01),
                (cl["w"], cl["seg"], 0.02), M["paint"])
        # 마루 끝 연석 — 계단 개구·램프 apron 구간은 비움
        cp = PARAMS["cope"]
        for i, (y0, y1) in enumerate(cp["y_segs"]):
            BOX(f"{ROOT}/Cope_{i}",
                ((cp["x0"] + cp["x1"]) / 2.0, (y0 + y1) / 2.0,
                 cp["h"] / 2.0 - 0.10),
                (cp["x1"] - cp["x0"], y1 - y0, cp["h"] + 0.20), M["conc"])

    # -------------------------------------------------------------------
    # 잔디 사면 — 7세그 × 2 Y밴드 (계단 폭만 비움). 세그는 margin 으로 겹친다.
    # -------------------------------------------------------------------
    def build_slope_faces(M):
        sl = PARAMS["slope"]
        st = PARAMS["stairs"]
        nodes = slope_nodes()
        bands = (("S", sl["y0"], st["y0"]), ("N", st["y1"], sl["y1"]))
        for i, (run, drop) in enumerate(sl["segs"]):
            x0, z0 = nodes[i]
            mg = 0.0 if i == 0 else sl["margin"]
            for tag, y0, y1 in bands:
                sc.build_slope(
                    stage, f"{ROOT}/Slope_{i}_{tag}", x0, z0, run, drop,
                    y0, y1, sl["thick"],
                    M["grass"] if i % 2 == 0 else M["grass_b"],
                    margin=mg, collider=True)

    # -------------------------------------------------------------------
    # 계단 20단 — 사면 직선 관통 (무난간)
    # -------------------------------------------------------------------
    def build_stairs(M, stair_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)

    # -------------------------------------------------------------------
    # 사선 램프 — rot_group(yaw) 안에서 build_slope 1장 + 성토(석축) + 연석
    #   로컬 규약: +X = 진행(하강), +Y = 상류측(= −n). 로컬 y = p0y − e.
    # -------------------------------------------------------------------
    def build_ramp(M, ramp_mtl):
        rp = PARAMS["ramp"]
        g = ramp_geom()
        px, py = rp["p0"]
        grp = sc.build_rot_group(stage, f"{ROOT}/Ramp", (px, py), g["yaw"])
        L, drop = g["length"], g["drop"]
        y_up = py - g["e_up"]                       # 상류측 가장자리(로컬 y 큼)
        y_dn = py - g["e_dn"]                       # 강측 가장자리
        # ① 성토 — 노면 밑면부터 아래로. 강측으로 fill_out 만큼 더 나온다.
        #   [v6 판정 ㉠] 재질 M["rock"](석축) → M["grass_b"](사면 잔디와 동재질).
        #   갈색 석축면이 초록 사면 위에서 이물(콘크리트 블록)로 읽히던 원인 제거.
        sc.build_slope(stage, f"{grp}/Fill", px, -rp["deck_t"], L, drop,
                       y_dn - rp["fill_out"], y_up, rp["fill_t"], M["grass_b"],
                       margin=0.0, collider=True)
        # ①-b [v6 판정 ㉠] 강측 잔디 배터 — 수직 절단면을 계단식 잔디 성토
        #   어깨로 분절한다. k 단째: 폭 w 만큼 강측으로 물러나며 dz 씩 내려간다.
        #   노면 밑 최대 노출 1.18 m 를 9단(낙차 1.26)이 덮는다.
        #   [v7 판정 ⑪-1 ㉠] 구 3단(단 높이 0.42)은 17 m 거리에서 **인공 계단**
        #   으로 읽혔다 → 폭·낙차 총량(1.50 × 1.26)은 유지한 채 9단으로 세분해
        #   단 높이 0.14(≤0.15 권고)로 낮췄다. 또 구 구성은 grass/grass_b 를
        #   교대해 **단 경계가 줄무늬**로 도드라졌으므로, 성토체(`Fill`)와
        #   **동일한 grass_b 단일 재질**로 통일해 지형 접힘으로만 읽히게 한다.
        #   margin 으로 상·하단을 조금 늘여 성토체와의 이음 틈을 막는다.
        bt = rp["batter"]
        for k in range(int(bt["n"])):
            y_hi = y_dn - rp["fill_out"] - bt["w"] * k
            sc.build_slope(stage, f"{grp}/Batter_{k}", px,
                           -rp["deck_t"] - bt["dz"] * (k + 1), L, drop,
                           y_hi - bt["w"], y_hi, rp["fill_t"],
                           M["grass_b"],
                           margin=bt["margin"], collider=True)
        # ② 노면(콘크리트 포장)
        sc.build_slope(stage, f"{grp}/Deck", px, 0.0, L, drop, y_dn, y_up,
                       rp["deck_t"], ramp_mtl, margin=0.0, collider=True)
        # ③ 강측 연석(h0.15) — 난간 없음(규정 미달의 현실)
        sc.build_slope(stage, f"{grp}/Curb", px, rp["curb_h"], L, drop,
                       y_dn, y_dn + rp["curb_w"], rp["curb_h"] + 0.35,
                       M["conc"], margin=0.0, collider=True)
        # ④ 진입 apron — [v7 판정 ⑪-1] **빌드 생략**(사유는 아래 주석).
        if PARAMS["ramp"]["apron"]["build"]:
            ap = PARAMS["ramp"]["apron"]
            BOX(f"{ROOT}/RampApron",
                ((ap["x0"] + ap["x1"]) / 2.0, (ap["y0"] + ap["y1"]) / 2.0,
                 -ap["drop"] - ap["t"] / 2.0),
                (ap["x1"] - ap["x0"], ap["y1"] - ap["y0"], ap["t"]),
                ramp_mtl, col=True)
        # ── [v7 판정 ⑪-1] 왜 없앴는가 ────────────────────────────────────
        #  구 apron 은 rot_group(yaw 80.793°) **안**에서 "로컬 −X = 마루 안쪽"
        #  이라고 가정한 박스였다. 로컬 −X 는 월드 −X 가 아니라 거의 월드 −Y 라
        #  실제로는 월드 x +3.06 까지 사면 위로 돌아나갔고, 그 지점 사면 상면
        #  −1.40 보다 1.39 m 솟은 **두께 2.8 m 콘크리트 블록**이 됐다.
        #  v6·v7 판정이 "램프 성토 갈색 매스"로 지목한 것이 바로 이 프림이다
        #  (W-5 가 고친 `Fill` 은 이미 잔디였고 프레임에서 잔디로 렌더된다).
        #  기능적으로도 불필요하다: 진입 참이 메워야 할 "마루 ↔ 램프 시점"
        #  단차는 마루 슬래브(levee x −24…0, 상면 0.000, 두께 3.6)와 자전거도로
        #  (x −3…0, 상면 +0.004)가 마루 끝까지 이미 채우고 있고, 남는 것은
        #  마루 끝(x 0) ~ 램프 상류 시단(x 0.59) 사이 **최대 0.152 m 문턱**
        #  (스모크 [사선 램프 배치] s0.0 절토 +0.152)뿐이다. 이는 계단 riser
        #  0.16 보다도 낮은 시공 이음이라 별도 프림이 필요 없다.
        #  PARAMS 는 v5.2 규약(scene05 스피커 선례)대로 **이력 보존용 잔존**.

    # -------------------------------------------------------------------
    # 둔치 + 산책로 + 호안 사석
    # -------------------------------------------------------------------
    def build_terrace(M):
        te = PARAMS["terrace"]
        pm = PARAMS["promenade"]
        cy = (te["y0"] + te["y1"]) / 2.0
        Ly = te["y1"] - te["y0"]
        BOX(f"{ROOT}/Terrace",
            ((te["x0"] + te["x1"]) / 2.0, cy, te["z_top"] - te["thick"] / 2.0),
            (te["x1"] - te["x0"], Ly, te["thick"]), M["grass"], col=True)
        # 산책로(강 평행 = Y 방향 밴드)
        z_hi = te["z_top"] + pm["proud"]
        BOX(f"{ROOT}/Promenade",
            ((pm["x0"] + pm["x1"]) / 2.0, cy, z_hi - 0.06),
            (pm["x1"] - pm["x0"], Ly, 0.12), M["asphalt"], col=True)
        for tag, xc in (("W", pm["x0"] + pm["line_in"]),
                        ("E", pm["x1"] - pm["line_in"])):
            BOX(f"{ROOT}/PromLine_{tag}", (xc, cy, z_hi + 0.004),
                (pm["line_w"], Ly, 0.02), M["paint"])
        # 호안 사석 사면 (둔치 → 수면 아래)
        bk = PARAMS["bank"]
        sc.build_slope(stage, f"{ROOT}/Bank", bk["x0"], te["z_top"], bk["run"],
                       bk["drop"], te["y0"], te["y1"], bk["thick"], M["rock"],
                       margin=bk["margin"], collider=True)

    # -------------------------------------------------------------------
    # 강 + 건너편 (넓은 수면 유지 — 사행 없음)
    # -------------------------------------------------------------------
    def build_river(M):
        wt = PARAMS["water"]
        sc.build_water(stage, f"{ROOT}/Water", wt["x0"], wt["y0"], wt["x1"],
                       wt["y1"], wt["z"], mtl=M["water"])
        fb = PARAMS["far_bank"]
        BOX(f"{ROOT}/FarBank",
            ((fb["x0"] + fb["x1"]) / 2.0, (fb["y0"] + fb["y1"]) / 2.0,
             fb["z_top"] - fb["thick"] / 2.0),
            (fb["x1"] - fb["x0"], fb["y1"] - fb["y0"], fb["thick"]),
            M["grass"], col=True)
        # [v6 판정 ㉡ · v7 판정 ⑪-2] 건너편 억새 띠 — 편평 타원체 군락.
        #   76 m 원경이라 대(stalk) 단위는 소실되므로 블롭으로 실루엣만 흐트린다.
        #   구 구현은 **1열 · 균등분할 y + ±0.3 지터**라 등간격이 남아
        #   "동일 크기 구슬 목걸이"로 읽혔다(§3 저촉 인상). 이번엔
        #     · rows = (dx, size_k, phase) 3열 — dx 로 전후, phase 로 열 간 위상차
        #     · y 를 **랜덤 보행**(spacing × U(0.55,1.60))으로 전진 → 등간격 소멸
        #     · 크기 0.60~1.45× · 높이 0.70~1.25× 지터
        #   접지: 중심 z = z_top + hh*0.42, rz = hh*0.60 → 하단이 지면 아래 0.18hh.
        fh = PARAMS["far_hedge"]
        for i, h in enumerate(PARAMS["far_hedges"]):
            y_lo = h["cy"] - fh["length"] / 2.0
            y_hi = h["cy"] + fh["length"] / 2.0
            for ri, (dx, sk, phase) in enumerate(fh["rows"]):
                rnd = _random.Random((i + 1) * 26417 ^ (ri + 1) * 6151)
                yy = y_lo + fh["spacing"] * phase
                k = 0
                while yy <= y_hi:
                    hh = fh["h"] * sk * rnd.uniform(0.70, 1.25)
                    rr = fh["rad"] * sk * rnd.uniform(0.60, 1.45)
                    sc.add_sphere(stage, f"{ROOT}/FarReed_{i}_{ri}_{k}",
                                  (fh["cx"] + dx + rnd.uniform(-0.30, 0.30),
                                   yy, fb["z_top"] + hh * 0.42),
                                  (fh["sx"] / 2.0 * sk * rnd.uniform(0.8, 1.4),
                                   rr, hh * 0.60),
                                  M["reed"])
                    yy += fh["spacing"] * rnd.uniform(0.55, 1.60)
                    k += 1
        for i, t in enumerate(PARAMS["far_trees"]):
            sc.build_tree(stage, f"{ROOT}/FarTree_{i}", t["cx"], t["cy"],
                          fb["z_top"], M["wood"], M["canopy_a"], M["canopy_b"])

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 마루~둔치를 z=0 잔디 평지로 통일."""
        lv = PARAMS["levee"]
        te = PARAMS["terrace"]
        BOX(f"{ROOT}/FlatFill",
            ((lv["x0"] + te["x1"]) / 2.0, (lv["y0"] + lv["y1"]) / 2.0,
             lv["z_top"] - lv["thick"] / 2.0),
            (te["x1"] - lv["x0"], lv["y1"] - lv["y0"], lv["thick"]),
            M["grass"], col=True)

    # -------------------------------------------------------------------
    # 원경 드레싱 — 건너편 아파트 스카이라인 + 교량 (한강 판독의 8할)
    # -------------------------------------------------------------------
    def build_skyline(M):
        # [v6 판정 ㉢] 2종 교대 → 4종 순환. 인접 동이 같은 톤으로 반복되지 않게.
        tones = (M["shell"], M["shell_c"], M["shell_b"], M["shell_d"])
        for i, (key, bd) in enumerate(PARAMS["far_buildings"].items()):
            sc.build_building(stage, f"{ROOT}/FarBuilding_{key}", bd,
                              tones[i % len(tones)],
                              M["glass"], M["parapet"],
                              window=PARAMS["window"])
        br = PARAMS["bridge"]
        BOX(f"{ROOT}/Bridge/Deck",
            ((br["x0"] + br["x1"]) / 2.0, (br["y0"] + br["y1"]) / 2.0,
             br["deck_top"] - br["deck_t"] / 2.0),
            (br["x1"] - br["x0"], br["y1"] - br["y0"], br["deck_t"]),
            M["bridge"], col=True)
        pier_top = br["deck_top"] - br["deck_t"]
        ph = pier_top - br["pier_base"]
        for i, py in enumerate(br["pier_ys"]):
            CYL(f"{ROOT}/Bridge/Pier_{i}",
                (br["pier_x"], py, br["pier_base"] + ph / 2.0),
                br["pier_r"], ph, M["bridge"], col=True)

    # -------------------------------------------------------------------
    # 근경 드레싱 — 억새·벤치·수목·가로등·이정표 (배치 비정형)
    # -------------------------------------------------------------------
    def build_dressing(M):
        tz = PARAMS["terrace"]["z_top"]
        # [v6 판정 ㉡] 억새 = 대(stalk) 군락. 밴드 사각형 안에 density 본/m² 로
        #   시드 고정 산포(scene09 build_reeds 규약). 높이·기울기 개체 지터.
        rd = PARAMS["reed"]
        for i, r in enumerate(PARAMS["reeds"]):
            rnd = _random.Random(int(r["seed"]))
            area = (r["x1"] - r["x0"]) * (r["y1"] - r["y0"])
            for k in range(int(round(area * rd["density"]))):
                hh = r["h"] * rnd.uniform(rd["h_lo"], rd["h_hi"])
                a = rnd.uniform(0.0, 360.0)
                CYL(f"{ROOT}/Reed_{i}_{k}",
                    (rnd.uniform(r["x0"], r["x1"]),
                     rnd.uniform(r["y0"], r["y1"]), tz + hh / 2.0),
                    rd["r"], hh, M["reed"],
                    rotY=rd["tilt"] * math.cos(math.radians(a)),
                    rotX=rd["tilt"] * math.sin(math.radians(a)))
        for i, (tx, ty) in enumerate(PARAMS["terrace_trees"]):
            sc.build_tree(stage, f"{ROOT}/TerraceTree_{i}", tx, ty, tz,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        for i, (tx, ty) in enumerate(PARAMS["crown_trees"]):
            sc.build_tree(stage, f"{ROOT}/CrownTree_{i}", tx, ty, 0.0,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        for i, (bx, by, yaw) in enumerate(PARAMS["terrace_benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, tz,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for tag, lights, base in (("T", PARAMS["terrace_lights"], tz),
                                  ("C", PARAMS["crown_lights"], 0.0)):
            for i, (lx, ly) in enumerate(lights):
                pre = f"{ROOT}/Light{tag}_{i}"
                CYL(f"{pre}/Pole", (lx, ly, base + sl["pole_h"] / 2.0),
                    sl["pole_r"], sl["pole_h"], M["post"], col=True)
                CYL(f"{pre}/Arm",
                    (lx + sl["arm_len"] / 2.0, ly,
                     base + sl["pole_h"] - 0.12),
                    sl["arm_r"], sl["arm_len"], M["post"], rotY=90.0)
                BOX(f"{pre}/Head",
                    (lx + sl["arm_len"], ly, base + sl["pole_h"] - 0.17),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        ks = PARAMS["km_sign"]
        CYL(f"{ROOT}/KmSign/Pole", (ks["x"], ks["y"], tz + ks["pole_h"] / 2.0),
            ks["pole_r"], ks["pole_h"], M["post"], col=True)
        BOX(f"{ROOT}/KmSign/Panel", (ks["x"], ks["y"], tz + ks["panel_z"]),
            ks["panel"], M["sign"])

    # -------------------------------------------------------------------
    # 단서 (cue) — railing / nosing (기본 OFF: 무난간 관행)
    # -------------------------------------------------------------------
    def build_cues(M):
        st = PARAMS["stairs"]
        run = st["nsteps"] * st["tread"]
        drop = st["nsteps"] * st["riser"]

        def stair_ground(x):
            if x <= st["x0"]:
                return 0.0
            if x >= st["x0"] + run:
                return -drop
            idx = min(int((x - st["x0"]) / st["tread"]), st["nsteps"] - 1)
            return -st["riser"] * (idx + 1)

        if cfg["cue_railing"]:
            sc.build_railing_line(
                stage, f"{ROOT}/Rail", st["y1"] - 0.15, -0.5, st["x0"],
                run, drop, stair_ground, M["rail"], rail_h=0.9)
        if cfg["cue_nosing"]:
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"], z_top=st["z_top"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hard_mtl = M["conc"] if cfg["cue_material_break"] else M["paving"]

    build_levee(M)
    if cfg["hazard_stairs"]:
        build_slope_faces(M)
        build_stairs(M, hard_mtl)
        build_ramp(M, hard_mtl)
        build_terrace(M)
        build_cues(M)
    else:
        build_flat_fill(M)
    build_river(M)                  # 강·건너편은 상시 (지평 폐쇄)
    if cfg["cue_scene_dressing"]:
        build_skyline(M)            # 아파트·교량은 대조군(평지)에서도 유지
        if cfg["hazard_stairs"]:
            build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["pair_compare"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene17_{ts}.png")
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
