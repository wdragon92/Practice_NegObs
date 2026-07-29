# -*- coding: utf-8 -*-
"""
scene15_alley_labyrinth.py — NegObs 인공씬 15호: 감천/알파마형 골목 계단 (Isaac Sim 4.5)

유형    : T15 골목 미로 (벽 압축 원근 × 좁은 시야 낙차 은닉)
사양서  : Docs/multi_scene_brief_v3.md §D scene15_alley_labyrinth
공통    : scene_common.py (검증된 API 헬퍼) · scene02_underpass.py (도시계 골격)

위험 본질: 폭 1.2m 콘크리트 계단이 좌우 파스텔 주택 사이로 하강. 벽이 계단에
           0.3m까지 바짝 붙어 시야를 압축하고, 중간 꺾임(rot_group 25°) 뒤로
           하부 골목이 소실 — 좁은 프레임에서 낙차 총 4.25m가 은닉된다.
목표     : 25단(12단 뒤 25° 꺾임 + 참 1.5m) + 좌우 파스텔 주택 12동(창·문 인셋,
           지붕 오버행) + 하부 골목(막다른 벽 금지)을 조립, 렌더 판정.

[v5.1 현실성] 사용자 총평 "조형물 빼라 — 더 부자연해졌다".
  옥상 물탱크·위성접시(+브래킷)·계량기함·빨래줄/빨래·전주·전선을 **전량 제거**,
  생활 흔적은 화분 5 + 실외기 2 + 걸레받이 띠만 남긴다. 골목 바닥·계단·주택
  본체 기하는 불변(트랜스폼 0 변경). 파스텔 팔레트는 순백 대면적 금지 규약에
  맞춰 최대 채널 ≤0.80 으로 낮추고, 파사드·지붕은 인스턴스별 ±5 % 틴트 지터.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene15_alley_labyrinth.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python scene15_alley_labyrinth.py
스모크 조기종료:        NEGOBS_SMOKE=1  python scene15_alley_labyrinth.py

좌표계: Z-up, m, 진행축 +X(첫 플라이트), 낙차 시작 모서리 = x=0.
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hazard_stairs 만 기하 토글(False→평탄 골목).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 계단·꺾임 제거, 상부 골목이 z=0로 평탄 연장
    "cue_railing":        True,   # 계단 한쪽(우측) 단순 파이프 손잡이
    "cue_tactile":        False,  # 노후 골목 — 점자블록 비관행(키 예약)
    "cue_material_break": True,   # False → 계단을 골목 바닥재로 통일
    "cue_nosing":         False,  # 도색 단코 비관행(키 예약)
    "cue_sign":           False,  # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,   # 좌우 주택·전선줄·하부 골목 소실 일괄
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # 첫 플라이트 12단 (x0=0, z 0→-2.04), 폭 1.2
    flight1=dict(x0=0.0, riser=0.17, tread=0.30, nsteps=12,
                 y0=-0.6, y1=0.6, z_top=0.0, base_z=-6.0),
    # 참 1.5m (x 3.6..5.1, z=-2.04)
    landing=dict(x0=3.6, x1=5.1, z_top=-2.04, base_z=-6.0),
    # 둘째 플라이트 13단, rot_group(pivot (5.1,0), 25°)로 꺾임 (x0=5.1, z -2.04→-4.25)
    flight2=dict(x0=5.1, riser=0.17, tread=0.30, nsteps=13,
                 y0=-0.6, y1=0.6, z_top=-2.04, base_z=-6.0),
    bend=dict(pivot=(5.1, 0.0), deg=25.0),
    # 하부 골목: 둘째 플라이트 끝(x≈9.0, z≈-4.25)에서 +X로 이어져 소실 (rot_group 내)
    lower_alley=dict(x0=9.0, x1=20.0, y0=-0.9, y1=0.9, z_top=-4.25, base_z=-6.0),
    rail=dict(y_side=0.55, rail_h=0.92, post_r=0.02, rail_r=0.026,
              rail_mid_r=0.02, rail_mid_drop=0.46, spacing=1.1),

    # 상부 골목 평탄 (x -12..0, z=0)
    upper_alley=dict(x0=-12.0, x1=0.0, y0=-0.9, y1=0.9, z_top=0.0, base_z=-6.0),

    # ═══ [W2 ground_kit] P5 alley_concrete — 요소 0 → 전면 충전 (사양 §5.4) ═══
    #  표본 대비 격차 최대 씬. 8요소를 한 번에 통과시킨다:
    #   15-1 횡 시공줄눈 step 3.0·폭 0.010·음각 3 mm  (x=0 은 에지 금지대로 드롭)
    #   15-2 맨홀 φ0.648  ★ **감독 결재 M9-ⓑ — d5 창으로 이설**
    #        (구안 x=−1.15 는 d2 에서 화면폭 1,268 px = 프레임 66.0 % 로 근경 창을
    #         한 요소가 독점했다 `[계산 — W_px=f·0.648/0.85]`. d5 창 x=−4.0 이면
    #         화면폭 280 px = 14.6 % 로 정상. d2 창의 B1 은 15-4 패치 1매가 채운다.)
    #   15-3 벽측 U형 측구(덮개) y=−0.75 · 15-4 보수 패치 2매
    #   15-5 벽–바닥 오염 밴드 · 15-6 계단 발치 그레이팅(꺾임 그룹 로컬)
    #   15-7 균열 3~5본 · 15-8 잡초 6~10 포기(GT-E5 램프로 에지 근방 자동 클램프)
    #  금지: 무지 흙바닥(표본 0/12) · 낙엽 · **점자블록**(§12 — p≈0.05 미설치)
    ground=dict(
        region=(-12.0, -0.9, 0.0, 0.9),
        #  15-2 맨홀 — M9-ⓑ 이설(구 −1.15) 의 **2차 정정**.
        #  ★ [W2 사전점검] −4.00 은 d5 시점에서 지면거리 X=1.00 m 라 화면폭
        #    f·0.648/1.00 = **1,078 px = 56.1 %** 였다 `[계산 — 레드팀 G-2]`.
        #    M9 의 취지는 "근경 독점 해소"인데 66 %(구) → 56 %(신) 는 해소가
        #    아니다. 게다가 **W1(지면거리 0.564~2.00 m) 안에서는 원리적으로
        #    ≤25 % 가 불가능**하다 — W1 원단 X=2.00 에서도 539 px = 28.1 % 다.
        #    → 2순위 창 **W2(2.00~3.00 m)** 로 내보낸다. x=−2.40 ⇒ d5 에서
        #    X=2.60 m · **414 px = 21.6 %** `[계산]`. d2 에서는 눈 뒤(X=−0.40)라
        #    비가시 → d2 창은 설계대로 패치 #1(x=−1.20)이 계속 담당한다.
        #    d10 에서는 X=7.60 · 142 px = 7.4 %.
        #  간섭 검사 `[계산]`: 반경 0.324 → x[−2.724,−2.076]·y[−0.474,0.174].
        #    줄눈 JX_3(x=−3.00) 밖 · 패치#1(x −1.557…−0.843) 밖 ·
        #    U측구(y −0.875…−0.625) 밖 · 그라임 밴드(|y|≥0.75) 밖 → Z파이팅 0.
        manhole_d5=(-2.40, -0.15),
        #  첫 매가 d2 창(W1 = x −1.436…0)의 B1·B2 를 담당한다. x=−1.20 이면
        #  화면폭 1,663 px(86.6 %) — 구 맨홀 안(1,268 px)과 달리 **평면 톤 변화**라
        #  근경 독점의 시각적 부담이 훨씬 작다.
        patch_sites=[(-1.20, 0.10), (-7.60, -0.30)],
        gutter_y=-0.75,
        grating_local=(9.30, -0.90, 0.90),         # 꺾임 rot_group 로컬
        grating_z=-4.25,
    ),
    # 상부 골목 옹벽 (A-15-3 치명): 구 구조는 x −12..−0.5 좌우가 주택·옹벽 없이
    #   계곡(−4.35)까지 4.35 m 절벽인 폭 1.8 m 외줄 노두였다. 골목 양옆을
    #   상면 z=1.2 옹벽으로 막고 그 뒤에 주택 4동을 앉힌다.
    retwall=dict(x0=-12.0, x1=0.0, y_in=0.9, y_out=1.4, z_top=1.2),
    # 참↔꺾임 −Y 쐐기 봉합 (A-15-4): 참 앞모서리(직선 x=5.1)와 25° 회전된
    #   flight2 첫 단 서측 모서리((4.846,0.544)→(5.354,−0.544)) 사이 최대 0.254 m
    #   삼각 개구. 첫 단 상면(−2.21)보다 5 mm 낮은 상면으로 메운다.
    wedge=dict(x0=5.05, x1=5.42, y0=-0.66, y1=0.05, z_top=-2.215, base_z=-6.0),
    # 계곡(하부) 지면 슬래브 — 언덕 사면 채움(공동 방지)
    valley=dict(size=90.0, z_top=-4.35),

    # 좌우 주택 12동 (파스텔 5색 순환). base_z는 하강 계단을 따라 계단식.
    #  face_dir: 골목 향하는 파사드 방향(+1=+Y면, -1=-Y면).
    #  grp=True : **꺾임 rot_group(피벗 (5.1,0), +25°) 안의 로컬 좌표**.
    #    [A-15-1/2 치명 대응] 구 House[2]/[3](월드 축정렬)은 25° 회전된 flight2·
    #    하부 골목을 전폭 폐색했다. 감사안(cy 3.6/5.0)으로 밀어내면 골목이 벌거
    #    벗으므로, 대신 두 동을 **회전 그룹 안으로 옮겨** 꺾인 골목을 로컬 y=±0.58
    #    (flight2) / ±0.88(하부 골목)에서 나란히 끼고 서게 했다 → 폐색 0,
    #    골목 회랑 정체성 유지, 중심선 이격 = 골목 반폭 그대로.
    #  life=True : [v5.1] 실외기 1대만 부착(계량기·물탱크·위성접시 폐기).
    #    골목에서 실제로 보이는 두 동(북측 첫 플라이트 옆 · 꺾임부 북측)에만 준다.
    #    걸레받이 띠는 도장 흔적이라 전 동 유지(소품 아님).
    houses=[
        # 상부 골목(옹벽 뒤, z=0 레벨)
        dict(cx=-2.6, cy=2.58, base_z=0.0, w=3.2, d=2.4, h=3.0, tint=4, face=-1),
        dict(cx=-2.6, cy=-2.58, base_z=0.0, w=3.2, d=2.4, h=2.6, tint=1, face=1),
        dict(cx=-6.6, cy=2.58, base_z=0.0, w=3.4, d=2.4, h=2.7, tint=3, face=-1),
        dict(cx=-6.6, cy=-2.58, base_z=0.0, w=3.4, d=2.4, h=3.2, tint=0, face=1),
        # 첫 플라이트·참 (월드 축정렬). 파사드 y=±0.58/±0.55 → 계단 측면(±0.6)에
        #   0.02~0.05 물려 구 0.10 m 크레바스(A-15-6) 소거.
        dict(cx=1.40, cy=1.78, base_z=-0.2, w=2.8, d=2.4, h=4.2, tint=0, face=-1,
             life=True),
        dict(cx=3.95, cy=1.78, base_z=-1.9, w=2.3, d=2.4, h=3.6, tint=1, face=-1),
        # 남측(y−) 동은 골목 일조 확보 위해 2.5~3m 저층(감독 r1 C-15③, 감천 실제)
        dict(cx=1.40, cy=-1.78, base_z=-0.2, w=2.8, d=2.4, h=2.8, tint=2, face=1),
        # 남측 참 옆 동은 x1=5.45 까지 늘려 꺾임 바깥 모서리(House[10] 서단
        #   월드 X=5.390)와의 0.29 m 틈을 닫는다. flight2 −Y 에지(X=5.45 에서
        #   Y=−0.499)보다 파사드(−0.58)가 바깥이라 회랑 침범 없음.
        dict(cx=4.125, cy=-1.78, base_z=-1.9, w=2.65, d=2.4, h=3.0, tint=3,
             face=1),
        # 꺾임 그룹 로컬 (flight2 local x 5.1..9.0 / 하부 골목 9.0..20)
        dict(cx=7.075, cy=1.88, base_z=-3.6, w=3.85, d=2.6, h=4.6, tint=2,
             face=-1, grp=True, life=True),
        dict(cx=11.05, cy=2.18, base_z=-4.25, w=4.1, d=2.6, h=3.8, tint=3,
             face=-1, grp=True),
        dict(cx=7.075, cy=-1.88, base_z=-3.6, w=3.85, d=2.6, h=2.7, tint=4,
             face=1, grp=True),
        dict(cx=11.05, cy=-2.18, base_z=-4.25, w=4.1, d=2.6, h=2.9, tint=0,
             face=1, grp=True),
    ],
    # 건너편 언덕 배경(원경 지평 폐쇄, 계곡 너머 사면 — 막다른 벽 아님)
    backdrop=[
        dict(cx=24.0, cy=8.0, base_z=-1.5, w=4.5, d=4.0, h=5.0, tint=1, face=-1),
        dict(cx=28.0, cy=2.0, base_z=-0.5, w=4.5, d=4.0, h=4.5, tint=3, face=-1),
        dict(cx=26.0, cy=-6.0, base_z=-2.5, w=4.5, d=4.0, h=5.5, tint=0, face=1),
        dict(cx=31.0, cy=-1.0, base_z=0.5, w=5.0, d=4.5, h=4.8, tint=4, face=1),
    ],
    # [v5 판정 반영] roof_over 0.25 → 0.14 : 25° 꺾임부에서 월드 축정렬 주택
    #   (House 5/7)과 회전군 주택(House 8/10)의 처마가 서로 다른 z(1.88·1.28·
    #   1.18·−0.72)로 교차하며 회랑 상공에 '뜬 흰 판' 조각을 만들었다. 오버행을
    #   줄여 교차 슬리버를 없앤다(주택 본체 트랜스폼 불변).
    house=dict(win_w=0.7, win_h=1.0, door_w=0.9, door_h=1.9, inset=0.06,
               roof_over=0.14, roof_t=0.18),
    # [v5.1 현실성 · 제거] 전주 2본 + 전선 2본 폐기.
    #   근거: poleA(2.0, −0.48, r0.11)·poleB(10.5, 0.72)는 각각 계단 회랑
    #   (y ±0.6)·하부 골목(y ±0.9) **안쪽**에 박혀 보행로를 관통하고 있었다.
    #   실제 골목 전주는 옹벽·담장 선에 서지 노면 한가운데 서지 않는다.
    #   "어색하면 제거" 지시에 따라 전주·전선 일괄 삭제(옮겨 세우면 파사드·
    #   지붕 오버행과 다시 교차하므로 존치 이득이 없다).
    # 생활 흔적 — 화분(pot) 5개로 축소: (x, y, z, grp).
    #   y=±0.40(계단 반폭 0.6, 화분 r 0.20 → 파사드 0.58 에 닿지 않음).
    #   등간격 6쌍 나열은 '진열'로 읽혀 한쪽씩 비대칭으로 남긴다.
    pots=[(0.9, 0.40, -0.68, False), (2.1, -0.40, -1.36, False),
          (4.2, 0.40, -2.04, False), (6.4, 0.40, -2.89, True),
          (10.5, -0.68, -4.25, True)],
    pot=dict(r=0.20, h=0.34, leaf_r=0.19),   # [v5 판정 반영] leaf_r 0.26 → 0.19
    # [v5.1 현실성 · 제거] 빨래줄 3본 + 빨래 9장 폐기 — 골목 상공을 가로지르는
    #   부유 판떼기로 읽혔고, 좁은 회랑 판독(낙차 은닉)에 기여가 없었다.

    material=dict(
        # [v5 판정 반영] retwall=3.5 신설 — 옹벽은 노면(concrete_floor, scale 1.0)
        #   과도 주택 회벽(plaster, scale 2.0)과도 다른 스케일로 분리한다.
        scale=dict(plaza_lower=0.7, concrete_floor=1.0, plaster=2.0,
                   retwall=3.5),
        # 파스텔 5색 (브리프 §D scene15).
        # [v5.1 현실성] 전역 규약 "순백(>0.8) 대면적 금지" — 파사드는 이 씬에서
        #   가장 넓은 면이라 0.90~0.95 채널이 정오광에서 흰 판으로 날아갔다.
        #   색상(hue)은 유지한 채 최대 채널 ≤0.80 으로 일괄 감광(×0.86 근사).
        pastel=[(0.78, 0.65, 0.60), (0.65, 0.73, 0.78), (0.80, 0.76, 0.60),
                (0.69, 0.77, 0.65), (0.77, 0.69, 0.77)],
        # [v5.1] 인스턴스별 틴트 지터 진폭(±5 %) — 파사드·지붕 공통
        tint_jitter=0.05,
        roof_tints=[(0.55, 0.31, 0.22), (0.42, 0.42, 0.44)],  # 주황·회색
        # B-15-1 [치명]: 0.60 순백은 정오광에서 클리핑되어 디딤/챌면 경계가
        #   완전 소실됐다(낙차 라벨의 시각 근거 상실). 0.20 중성 콘크리트로.
        stair_color=(0.20, 0.20, 0.19), stair_rough=0.82,
        # [v5 판정 반영·치명] 옹벽 2열이 M["alley"](노면 concrete_floor)를 그대로
        #   써서 h0.3/h0.9 전 프리셋이 '좌우 갈색 판 + 같은 재질 바닥'의 무맥락
        #   회랑이 됐다. 옹벽 전용 = plaster 텍스처 + 회청 석축 틴트(0.28 대역,
        #   판정 권장 0.10~0.35) + scale 3.5. 파스텔 파사드(0.75~0.95)와도,
        #   노면과도 명도·색상·텍스처 스케일이 모두 분리된다.
        retwall_tint=(0.30, 0.29, 0.27), retwall_rough=0.88,
        # [v5 판정 반영] 화분 잎이 M["roof"][1](0.45,0.45,0.47 회색)이라 정오광에
        #   백색 블롭으로 렌더됐다 → 전용 진녹 상수색 + 반경 축소.
        foliage_color=(0.13, 0.22, 0.11), foliage_rough=0.80,
        window_color=(0.05, 0.06, 0.08), window_rough=0.2,    # 다크 유리
        frame_color=(0.72, 0.70, 0.66), frame_rough=0.65,     # 창·문 프레임
        skirt_color=(0.10, 0.10, 0.12), skirt_rough=0.8,      # 파사드 걸레받이
        rail_color=(0.30, 0.30, 0.32), rail_metallic=0.5, rail_rough=0.5,
        pot_color=(0.35, 0.12, 0.10), pot_rough=0.7,          # 토분(구 tank_color)
        gear_color=(0.045, 0.05, 0.045), gear_rough=0.7,      # 실외기
        valley_tint=(0.85, 0.85, 0.82),
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
    # 감독 r1 C-15①: 171.5→153.0. 태양 매핑 월드 az ≈ 33.5+offset = 186.5,
    #   그림자 az = az−180 = 6.5 → 광선이 골목 축(+X)에 근평행하게 낮게 들어와
    #   계단 바닥을 핥는다(통짜 암부 해소). 좁은 골목 일조 확보.
    SUN_AZ_OFFSET=153.0,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene15")

ASSET_ROLES = ["plaster", "plaza_lower", "concrete_floor", "hdri", "mdl"]


def tint_jitter(color, seed, amp=None, cap=0.80):
    """[v5.1 전역 규약 4] 인스턴스별 ±amp 틴트 지터.

    같은 파스텔 5색을 12동이 그대로 돌려쓰면 '복붙 블록'으로 읽힌다. 재질을
    새로 설계하는 대신 기존 색을 인스턴스 시드로 ±5 % 흔든다(결정적 — 같은
    슬롯은 재실행해도 동일). cap 으로 순백(>0.8) 대면적을 원천 차단한다."""
    if amp is None:
        amp = PARAMS["material"]["tint_jitter"]
    rnd = random.Random(1000003 * (int(seed) + 7))
    return tuple(round(min(cap, max(0.02, c * (1.0 + rnd.uniform(-amp, amp)))), 4)
                 for c in color)


def build_views():
    """카메라 프리셋: grid_views(gy=0, 첫 플라이트 축) + 미장센 4컷."""
    views = sc.grid_views(0.0)               # 첫 플라이트 축 = +X, y=0
    # top_compress: 상부 골목에서 계단 하강을 내려다봄(벽 압축)
    views["top_compress"] = dict(eye=[-3.0, 0.0, 1.6], tgt=[5.0, 0.0, -1.6])
    # bend_landing: 참에서 25° 꺾임 너머 소실을 봄
    views["bend_landing"] = dict(eye=[3.4, 0.0, -0.4], tgt=[9.0, 1.5, -3.6])
    # narrow_up: 하부에서 좁은 골목 역광으로 올려봄. v2 재선정 [B-15-5] —
    #   구 eye (7.5,0.4,−3.8)은 꺾임 로컬 (7.44,−0.65) = 남측 주택 솔리드 **안쪽**
    #   이라 프레임 95 %가 흑색이었다. 꺾인 골목 중심(로컬 (7.4,0) = 월드
    #   (7.185,0.972), 그 지점 계단 상면 −3.40) 위 1.5 m 로 이동하고, 시선을
    #   꺾임 안쪽(참·flight1)으로 되돌린다. 시선이 통과하는 월드 y ≤ 0.49 로
    #   북측 주택 전면(y 0.55)에 닿지 않는다.
    views["narrow_up"] = dict(eye=[7.185, 0.972, -1.90], tgt=[3.0, -0.2, 0.2])
    # beauty_overview: v4 재선정 [v5 판정 반영·치명]. v3(eye (0,−1.2,10),
    #   피치 −49°)는 폐색 검산은 CLEAR 였지만 실제 프레임의 70 %가 주택 지붕·
    #   옥상 물탱크 부감이고 골목은 폭 5 % 슬릿 — '달동네 골목'이 아니라 추상
    #   색면이 됐다. v4 는 **회랑 축 위 부감**으로 바꿔 회랑·계단 하강·양측
    #   파스텔 파사드가 한 프레임에 들어오게 한다.
    #     eye (−5.5, −0.2, 4.6) / tgt (4.6, 0.35, −2.04)  → 피치 −33.3°
    #   피치를 판정 권고(−25~−30)보다 약간 세운 이유: flight1 경사각이
    #   atan(0.17/0.30)=29.5° 라 부각이 그보다 커야 디딤면이 분해된다.
    #   폐색 검산 — 시선 P(x) : y(x) = −0.2 + 0.05446(x+5.5),
    #                          z(x) = 4.6 − 0.65743(x+5.5)
    #     · eye : 상부 골목 회랑 상공(|y|<0.9), 옹벽 1.2·생울타리 1.7 위 ✓
    #     · House[3](x −8.3..−4.9, y ≤ −1.38) / House[1](x −4.2..−1.0) :
    #       해당 구간 시선 y = −0.352..−0.129 → y 대역 밖 ✓
    #     · 옹벽 2열(|y| 0.9..1.4, 상면 1.2 · 생울타리 1.7) : 전 구간
    #       |시선 y| ≤ 0.377 → 애초에 벽 y 대역에 들어가지 않는다 ✓
    #     · House[2]/[0](북측 y ≥ 1.38) : 같은 구간 시선 y < 0 ✓
    #     · House[4](x 0..2.8, y ≥ 0.58) : x=2.8 에서 y=0.252 → 0.33 m 여유 ✓
    #     · House[5](x 2.8..5.1, y ≥ 0.58) : x=5.1 에서 y=0.377 → 0.20 m 여유 ✓
    #     · House[6]/[7](남측 y ≤ −0.58) : 시선 y ≥ −0.20 ✓
    #     · (전주 A 는 [v5.1] 에서 제거 — 회랑 내 장애물 0)
    #     · 지면 : 계단 상면(x=2.8 −1.70 / x=3.6 −2.04) 대비 시선 z
    #       (−0.857 / −1.383)이 0.66~0.84 m 위 → x=4.615 에서 참(−2.04) 착지 ✓
    #       (부각 33.3° > flight1 경사 29.5° 이므로 12단이 전부 분해된다)
    views["beauty_overview"] = dict(eye=[-5.5, -0.2, 4.6],
                                    tgt=[4.6, 0.35, -2.04])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. top_compress / beauty — 좌우 주택·계단·25° 꺾임·하부 소실 식별
 2. h0.3·d5~10            — 좁은 시야에서 낙차 4.25m가 벽 압축에 은닉되는가
 3. bend_landing          — 참 뒤 꺾임 너머로 하부 골목이 소실(막다른 벽 없음)
 4. cue ON vs OFF         — railing/material_break 토글 시 기하 트랜스폼 불변
 5. 재질                  — 파스텔 회벽·지붕 오버행·전선줄·Z파이팅·부유 없는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene15")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene15"

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
        M = {}
        M["stair"] = PBR(f"{ROOT}/Looks/Stair",
                         diffuse_color=mp["stair_color"],
                         roughness_const=mp["stair_rough"], metallic=0.0)
        M["alley"] = PBR(
            f"{ROOT}/Looks/Alley", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"])
        # [v5 판정 반영] 옹벽 전용 재질 — 노면(alley)·파스텔 파사드 양쪽과 분리
        M["retwall"] = PBR(
            f"{ROOT}/Looks/RetWall", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["retwall"], tint=mp["retwall_tint"],
            roughness_const=mp["retwall_rough"])
        # [v5 판정 반영] 화분 잎 전용 진녹 재질 (구: M["roof"][1] 회색 → 백색 블롭)
        M["foliage"] = PBR(f"{ROOT}/Looks/Foliage",
                           diffuse_color=mp["foliage_color"],
                           roughness_const=mp["foliage_rough"])
        M["valley"] = PBR(
            f"{ROOT}/Looks/Valley", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"),
            sc.tex_path("plaza_lower", "rough"), sca["plaza_lower"],
            tint=mp["valley_tint"])
        # 파스텔 회벽 — [v5.1] 5색 공유 → **주택 인스턴스별** ±5 % 틴트 지터.
        #   신규 재질 파라미터는 없다(기존 pastel 5색 · roof 2색이 그대로 기저).
        #   슬롯 = houses 인덱스, 이어서 backdrop 인덱스.
        specs = list(PARAMS["houses"]) + list(PARAMS["backdrop"])
        M["plaster_i"], M["roof_i"] = [], []
        for i, hs in enumerate(specs):
            base = mp["pastel"][hs["tint"] % len(mp["pastel"])]
            M["plaster_i"].append(PBR(
                f"{ROOT}/Looks/Plaster_{i}", sc.tex_path("plaster", "diff"),
                sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
                sca["plaster"], tint=tint_jitter(base, i)))
            rbase = mp["roof_tints"][hs["tint"] % len(mp["roof_tints"])]
            M["roof_i"].append(PBR(
                f"{ROOT}/Looks/Roof_{i}",
                diffuse_color=tint_jitter(rbase, 100 + i, cap=0.70),
                roughness_const=0.7))
        M["window"] = PBR(f"{ROOT}/Looks/Window",
                          diffuse_color=mp["window_color"],
                          roughness_const=mp["window_rough"], metallic=0.0)
        M["frame"] = PBR(f"{ROOT}/Looks/Frame",
                         diffuse_color=mp["frame_color"],
                         roughness_const=mp["frame_rough"])
        M["skirt"] = PBR(f"{ROOT}/Looks/Skirt",
                         diffuse_color=mp["skirt_color"],
                         roughness_const=mp["skirt_rough"])
        # [v5.1] 화분 토분 3종 — 같은 기저색의 ±5 % 지터(진열 인상 완화)
        M["pot"] = [PBR(f"{ROOT}/Looks/Pot_{i}",
                        diffuse_color=tint_jitter(mp["pot_color"], 200 + i,
                                                  cap=0.55),
                        roughness_const=mp["pot_rough"]) for i in range(3)]
        M["gear"] = PBR(f"{ROOT}/Looks/Gear", diffuse_color=mp["gear_color"],
                        roughness_const=mp["gear_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail",
                        diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        return M

    # -------------------------------------------------------------------
    # 지면 — 계곡 슬래브(사면 채움) + 상부 골목 평탄
    # -------------------------------------------------------------------
    def build_ground(M):
        v = PARAMS["valley"]
        H = v["size"] / 2.0
        th = 1.0
        BOX(f"{ROOT}/Valley", (5.0, 0.0, v["z_top"] - th / 2.0),
            (v["size"], v["size"], th), M["valley"], col=True)
        ua = PARAMS["upper_alley"]
        # 상부 골목: 솔리드 메사(계곡까지 채움) 상면 z=0
        cx = (ua["x0"] + ua["x1"]) / 2.0
        cy = (ua["y0"] + ua["y1"]) / 2.0
        top, bot = ua["z_top"], v["z_top"]
        # [W2-0 · P-A] 상부 골목 상면이 ground_kit 의 장식 대상이다 → 변위 스킨
        #   OFF. 안 끄면 음각 줄눈(−3 mm)·맨홀(±10 mm)이 스킨(+6.5~16.5 mm)에
        #   통째로 묻힌다 `[실측 — 사양 §1.1]`.
        sc.skin_exclude(f"{ROOT}/UpperAlley")
        BOX(f"{ROOT}/UpperAlley", (cx, cy, (top + bot) / 2.0),
            (ua["x1"] - ua["x0"], ua["y1"] - ua["y0"], top - bot),
            M["alley"], col=True)
        # 상부 골목 옹벽 2열 (A-15-3 치명): 폭 1.8 m 외줄 노두 → 좌우 마감.
        #   상면 z=1.2, 저면은 계곡(−4.35)까지 솔리드 → 4.35 m 절벽 소거.
        rw = PARAMS["retwall"]
        for tag, y0, y1 in (("N", rw["y_in"], rw["y_out"]),
                            ("S", -rw["y_out"], -rw["y_in"])):
            BOX(f"{ROOT}/RetWall_{tag}",
                ((rw["x0"] + rw["x1"]) / 2.0, (y0 + y1) / 2.0,
                 (rw["z_top"] + v["z_top"]) / 2.0),
                (rw["x1"] - rw["x0"], y1 - y0, rw["z_top"] - v["z_top"]),
                M["retwall"], col=True)   # [v5 판정 반영] M["alley"] → 옹벽 전용
            # 옹벽 위 생울타리 (골목 판독 보조)
            sc.build_hedge(stage, f"{ROOT}/RetHedge_{tag}",
                           rw["x0"], y0 + 0.05, rw["x0"] + 8.0, y1 - 0.05,
                           0.5, base_z=rw["z_top"])

    # -------------------------------------------------------------------
    # [W2] ground_kit — P5 alley_concrete. 상부 골목(x −12…0) 전면 충전.
    #   낙차 에지 = 첫 플라이트 시단 x=0. 줄눈 x=0 은 `_edge_guard_ticks` 가
    #   자동 드롭한다(GT-E2 Δ≥16행). 계단 발치 그레이팅(15-6)만 꺾임 그룹
    #   로컬 좌표라 별도 호출로 붙인다.
    # -------------------------------------------------------------------
    def build_ground_kit(M, grp):
        g = PARAMS["ground"]
        gp = gk.plan_ground(
            "alley_concrete", region=tuple(g["region"]), z=0.0, gy=0.0,
            origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(PARAMS["flight1"]["x0"]))],
            dists=(2, 5, 10), scene="scene15",
            tactile=(),                       # §12 — p≈0.05, 표본 0/12 → 미설치
            sites=dict(manhole=[tuple(g["manhole_d5"])],
                       gutter_U=[float(g["gutter_y"])],
                       trench=[],             # 15-6 은 꺾임 그룹에서 따로
                       patch=[tuple(v) for v in g["patch_sites"]]),
            overrides=dict(infra=dict(manhole=1, gutter_U=1, trench=0)),
            seed=15)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["stair"], crack=M["stair"], patch=M["alley"],
                  patch_cut=M["stair"], manhole=M["rail"], gutter=M["stair"],
                  gutter_cover=M["stair"], weed=M["foliage"],
                  stain_grime_band=M["skirt"], stain_dirt=M["skirt"],
                  trench=M["rail"], trench_frame=M["rail"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        # 15-6 계단 발치 선형 그레이팅 — 꺾임 rot_group **로컬** 좌표.
        #   하부 골목 상면 z=−4.25 라 상부 골목 계획과 좌표계가 다르다.
        gx, gy0, gy1 = g["grating_local"]
        gk.build_trench_drain(kit, f"{grp}/GKit_Grating", gx, gy0, gx, gy1,
                              float(g["grating_z"]), M["rail"],
                              mtl_frame=M["rail"], width=0.20)
        print(f"[ground_kit] scene15 P5 · 프림 {res['prims']} + 그레이팅 2 · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # 계단 — 첫 플라이트 + 참 + 둘째 플라이트(25° 꺾임) + 하부 골목
    # -------------------------------------------------------------------
    def build_stairs(M, grp):
        stair_mtl = M["stair"] if cfg["cue_material_break"] else M["alley"]
        f1 = PARAMS["flight1"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Flight1", f1["x0"], f1["y0"], f1["y1"],
            f1["riser"], f1["tread"], f1["nsteps"], f1["base_z"], stair_mtl,
            z_top=f1["z_top"], collider=True)
        # 참
        la = PARAMS["landing"]
        BOX(f"{ROOT}/Landing",
            ((la["x0"] + la["x1"]) / 2.0, 0.0,
             (la["z_top"] + la["base_z"]) / 2.0),
            (la["x1"] - la["x0"], f1["y1"] - f1["y0"],
             la["z_top"] - la["base_z"]), stair_mtl, col=True)

        # 참↔꺾임 −Y 쐐기 봉합 (A-15-4). 첫 단 상면(−2.21)보다 5 mm 낮게 놓아
        #   동일평면 Z파이팅을 피하고, 참 아래(x<5.1)에서는 참 솔리드에 묻힌다.
        we = PARAMS["wedge"]
        BOX(f"{ROOT}/BendWedge",
            ((we["x0"] + we["x1"]) / 2.0, (we["y0"] + we["y1"]) / 2.0,
             (we["z_top"] + we["base_z"]) / 2.0),
            (we["x1"] - we["x0"], we["y1"] - we["y0"],
             we["z_top"] - we["base_z"]), stair_mtl, col=True)

        # 둘째 플라이트 + 하부 골목: rot_group 25° 꺾임 (grp 은 상위에서 1회 생성)
        f2 = PARAMS["flight2"]
        sc.build_straight_stairs(
            stage, f"{grp}/Flight2", f2["x0"], f2["y0"], f2["y1"],
            f2["riser"], f2["tread"], f2["nsteps"], f2["base_z"], stair_mtl,
            z_top=f2["z_top"], collider=True)
        # 하부 골목(꺾임 그룹 내 — 경계 정합, +X로 소실)
        lo = PARAMS["lower_alley"]
        BOX(f"{grp}/LowerAlley",
            ((lo["x0"] + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             (lo["z_top"] + lo["base_z"]) / 2.0),
            (lo["x1"] - lo["x0"], lo["y1"] - lo["y0"],
             lo["z_top"] - lo["base_z"]), M["alley"], col=True)

        # 손잡이 — A-15-5: 구 구조는 첫 플라이트(+Y 한쪽)만 있고 참·꺾임·둘째
        #   플라이트(2.21 m 하강)가 무난간이었다. 참 구간과 flight2(그룹 로컬)
        #   까지 연장한다.
        if cfg["cue_railing"]:
            rl = PARAMS["rail"]
            run = f1["tread"] * f1["nsteps"]
            drop = f1["riser"] * f1["nsteps"]

            def f1_ground(x):
                if x <= 1e-9:
                    return f1["z_top"]
                i = min(max(int(x / f1["tread"]) + 1, 1), f1["nsteps"])
                return f1["z_top"] - f1["riser"] * i

            sc.build_railing_line(
                stage, f"{ROOT}/Rail1", rl["y_side"], -0.3, f1["x0"],
                run, drop, f1_ground, M["rail"], rail_h=rl["rail_h"],
                post_r=rl["post_r"], spacing=rl["spacing"], rail_r=rl["rail_r"],
                rail_mid_r=rl["rail_mid_r"], rail_mid_drop=rl["rail_mid_drop"])
            # 참(평탄, drop 0)
            sc.build_railing_line(
                stage, f"{ROOT}/RailLanding", rl["y_side"], la["x0"], la["x0"],
                la["x1"] - la["x0"], 0.0, lambda x: la["z_top"], M["rail"],
                rail_h=rl["rail_h"], post_r=rl["post_r"],
                spacing=rl["spacing"], rail_r=rl["rail_r"],
                rail_mid_r=rl["rail_mid_r"], rail_mid_drop=rl["rail_mid_drop"])
            # 둘째 플라이트 (회전 그룹 로컬 — 꺾임과 함께 돈다)
            run2 = f2["tread"] * f2["nsteps"]
            drop2 = f2["riser"] * f2["nsteps"]

            def f2_ground(x):
                t = x - f2["x0"]
                if t <= 1e-9:
                    return f2["z_top"]
                i = min(max(int(t / f2["tread"]) + 1, 1), f2["nsteps"])
                return f2["z_top"] - f2["riser"] * i

            sc.build_railing_line(
                stage, f"{grp}/Rail2", rl["y_side"], f2["x0"], f2["x0"],
                run2, drop2, f2_ground, M["rail"], rail_h=rl["rail_h"],
                post_r=rl["post_r"], spacing=rl["spacing"], rail_r=rl["rail_r"],
                rail_mid_r=rl["rail_mid_r"], rail_mid_drop=rl["rail_mid_drop"])

    def build_flat_control(M):
        """hazard_stairs=False: 상부 골목이 z=0로 평탄 연장(계단 소거)."""
        f1 = PARAMS["flight1"]
        v = PARAMS["valley"]
        x0, x1 = 0.0, 12.0
        BOX(f"{ROOT}/FlatAlley",
            ((x0 + x1) / 2.0, 0.0, (0.0 + v["z_top"]) / 2.0),
            (x1 - x0, f1["y1"] - f1["y0"], 0.0 - v["z_top"]),
            M["alley"], col=True)

    # -------------------------------------------------------------------
    # 주택 (파스텔 회벽 박스 + 창·문 인셋 + 지붕 오버행)
    # -------------------------------------------------------------------
    def _opening(prefix, tag, cx, yf, face, z, ow, oh, M):
        """창·문 1개 = 다크 패널 + 프레임 4변.

        [B-15-2 수정] 구 코드는 `gy = cy + face*(d/2−0.005)` (벽면 안쪽 5 mm)에
        `ny = 0.02*face` 를 **더해서**(`wy = gy + ny`) 두께 0.04 패널 중심이 벽면
        바깥 0.015 m 로 나갔다 → 벽에서 3.5 cm 뜬 검은 판 + 측면 두께가 렌더에
        보였다. 셸이 솔리드라 진짜 인셋은 불가하므로, 패널 **외면**이 벽면 +5 mm
        가 되도록 부호를 바로잡고(사실상 면일치), 3 cm 돌출 프레임 4변을 둘러
        '인셋 창'으로 읽히게 한다."""
        t_p, t_f, fw = 0.04, 0.05, 0.06
        py = yf + face * (0.005 - t_p / 2.0)       # 패널 외면 = 벽면 +5 mm
        BOX(f"{prefix}/{tag}_Panel", (cx, py, z), (ow, t_p, oh), M["window"])
        fy = yf + face * (0.03 - t_f / 2.0)        # 프레임 외면 = 벽면 +3 cm
        for nm, ox, oz, sx, sz in (
                ("T", 0.0, oh / 2 + fw / 2, ow + 2 * fw, fw),
                ("B", 0.0, -oh / 2 - fw / 2, ow + 2 * fw, fw),
                ("L", -ow / 2 - fw / 2, 0.0, fw, oh),
                ("R", ow / 2 + fw / 2, 0.0, fw, oh)):
            BOX(f"{prefix}/{tag}_F{nm}", (cx + ox, fy, z + oz),
                (sx, t_f, sz), M["frame"])

    def build_house(prefix, hs, M, slot, life=False):
        h = PARAMS["house"]
        cx, cy = hs["cx"], hs["cy"]
        w, d, ht = hs["w"], hs["d"], hs["h"]
        base = hs["base_z"]
        face = hs["face"]
        v = PARAMS["valley"]
        shell_mtl = M["plaster_i"][slot]     # [v5.1] 인스턴스별 틴트 지터
        top = base + ht
        bot = v["z_top"]                          # 계곡까지 솔리드(부유·공동 방지)
        BOX(f"{prefix}/Shell", (cx, cy, (top + bot) / 2.0),
            (w, d, top - bot), shell_mtl, col=True)
        # 파사드(골목쪽) 벽면 평면: face=-1 → -Y면(y=cy-d/2), face=+1 → +Y면
        yf = cy + face * (d / 2.0)
        z_win = base + ht * 0.55
        for c, off in enumerate((-w * 0.28, w * 0.28)):
            _opening(prefix, f"Win_{c}", cx + off, yf, face, z_win,
                     h["win_w"], h["win_h"], M)
        _opening(prefix, "Door", cx, yf, face, base + h["door_h"] / 2.0,
                 h["door_w"], h["door_h"], M)
        # 지붕 슬래브 (오버행)
        BOX(f"{prefix}/Roof", (cx, cy, top + h["roof_t"] / 2.0),
            (w + 2 * h["roof_over"], d + 2 * h["roof_over"], h["roof_t"]),
            M["roof_i"][slot], col=True)
        # 걸레받이 띠 (파사드 하부 다크 밴드) — 도장 흔적이라 전 동 유지.
        #   [v5.1 전역 규약 4] '기단 오염 밴드' 역할도 겸한다(순백 대면적 차단).
        BOX(f"{prefix}/Skirt", (cx, yf + face * 0.015, base + 0.425),
            (w, 0.03, 0.85), M["skirt"])
        if not life:
            return
        # ── [v5.1] 생활 흔적은 실외기 1대만 ──
        #   구 사양(계량기함·위성접시+브래킷·옥상 물탱크)은 12동 전부에 같은
        #   위치·같은 크기로 복제돼 '소품 카탈로그'로 읽혔다(사용자 총평).
        #   벽부 실외기는 파사드에 밀착한 유일한 기능 설비라 이것만 남긴다.
        BOX(f"{prefix}/AC", (cx - w * 0.30, yf + face * 0.16,
                             base + ht * 0.78), (0.70, 0.32, 0.55), M["gear"])

    def build_dressing(M, grp):
        # 주택 12동. grp=True 인 동은 꺾임 회전 그룹 하위(로컬 좌표)에 놓여
        #   25° 회전된 골목을 그대로 끼고 선다 [A-15-1/2 치명 해소].
        #   [v5.1] life 는 씬 파라미터가 지정한 2동만 (구: 12동 전부).
        n_house = len(PARAMS["houses"])
        for i, hs in enumerate(PARAMS["houses"]):
            root = grp if hs.get("grp") else ROOT
            build_house(f"{root}/House_{i}", hs, M, i,
                        life=bool(hs.get("life")))
        # 건너편 언덕 배경 클러스터(원경 지평 폐쇄 — 막다른 벽 아님, 계곡 너머
        #   맞은편 사면에 계단식으로 얹힌 감천형 주택군). 꺾여 소실하는 골목의
        #   소실점 뒤를 지평선에서 막아준다(체크리스트 §A-4).
        for i, bh in enumerate(PARAMS["backdrop"]):
            build_house(f"{ROOT}/Backdrop_{i}", bh, M, n_house + i)
        # [v5.1] 전주·전선·빨래줄 제거 (PARAMS 주석의 근거 참조).
        # 화분 5 (골목 가장자리, 계단 레벨별) — 항아리 + 잎 덩어리 2프림
        po = PARAMS["pot"]
        for i, (px, py, pz, in_grp) in enumerate(PARAMS["pots"]):
            root = grp if in_grp else ROOT
            CYL(f"{root}/Pot_{i}", (px, py, pz + po["h"] / 2.0),
                po["r"], po["h"], M["pot"][i % len(M["pot"])], col=True)
            sc.add_sphere(stage, f"{root}/PotLeaf_{i}",
                          (px, py, pz + po["h"] + po["leaf_r"] * 0.6),
                          (po["leaf_r"], po["leaf_r"], po["leaf_r"] * 0.8),
                          M["foliage"])   # [v5 판정 반영] 회색 → 진녹

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    # 꺾임 회전 그룹은 계단·주택·드레싱이 공유하므로 조립 최상위에서 1회 생성
    #   (hazard_stairs=False 대조군에서도 그룹 하위 드레싱이 올바로 회전한다).
    _bd = PARAMS["bend"]
    GRP = sc.build_rot_group(stage, f"{ROOT}/Bend", _bd["pivot"], _bd["deg"])
    build_ground(M)
    if cfg["hazard_stairs"]:
        build_stairs(M, GRP)
    else:
        build_flat_control(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M, GRP)
    build_ground_kit(M, GRP)             # [W2] 지면 요소 — 드레싱 뒤(산포 순서 규약)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] scene15 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["beauty_overview"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene15_{ts}.png")
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
