# -*- coding: utf-8 -*-
"""
scene01_campus_stairs.py — NegObs 인공씬 1호: 캠퍼스 광장 하행계단 (Isaac Sim 4.5)

사양서 : Docs/scene01_design_brief.md (유일 사양)
쿡북   : negobs_look_check_v1.py (검증된 API 패턴 이식)

위험 본질: 상·하부가 같은 계열 화강암이라 낮은 시점에서 계단 단차가 소실.
목표     : 넓은 화강암 광장 + 광폭 저단차 4단 계단 + 하부 광장을 GUI로 띄우고
           렌더로 판정 (렌더 전용, 물리 콜라이더만 부착 — 시뮬 스텝 없음).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene01_campus_stairs.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene01_campus_stairs.py
      NEGOBS_CAPTURE_DIR  : 저장 폴더 (기본 look_check/scene01/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (기본 rt)
      NEGOBS_VIEWS        : 쉼표로 뷰 이름 필터 (기본 전부)

좌표계: Z-up, m, 진행축 +X, 계단 상단 모서리 = x=0.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

# [v5 공통 레이어] 한글 사인(build_sign)만 공통 라이브러리에서 가져온다.
#   scene_common 은 SimulationApp 부팅 **전** import 해도 안전(pxr/omni 지연 import).
#   scene01 의 나머지 빌더·재질 헬퍼는 기존 로컬 구현을 그대로 쓴다(회귀 방지).
import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG (브리프 §2) — hazard_stairs 외 토글은 기하를 바꾸지 않는다.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 계단+하부광장 전체를 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        True,   # 중앙 + 양측 스테인리스 핸드레일 (h 0.9, 계단 + 상단 1 m 연장)
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)   # 점형 점자블록 띠: 상단 모서리 0.3 m 앞, 계단 폭, 깊이 0.3 m
    "cue_material_break": True,   # False → 하부 광장을 상부와 동일 재질·톤으로
    "cue_sign":           True,   # [v5 공통 레이어] 한글 사인 1매 (시설 안내)
    "cue_scene_dressing": True,   # 화단·나무·건물·가로등·앰피시어터 일괄
}


# ===========================================================================
# [B] PARAMS — 브리프 §1 치수표 + 재질/조명/캡처. NEGOBS_PARAMS_OVERRIDE 머지.
# ===========================================================================
PARAMS = dict(
    # --- §1 좌표·레이아웃 ---
    # v4-A3: thick 0.5→0.7 (밑면 −0.70 < 잔디 상면 −0.63) — 노출 절단면 언더컷 제거
    upper_plaza=dict(x0=-16.0, x1=0.0, y0=-8.0, y1=8.0, z_top=0.0, thick=0.7),
    band=dict(width=0.45, spacing=2.7, proud=0.0015, embed=0.05),  # Y로 달리는 차콜 밴드(F5: 돌출 1.5mm)
    stairs=dict(x0=0.0, riser=0.15, tread=0.38, nsteps=4,          # 총 낙차 0.6 m
                y0=-5.5, y1=5.5, base_z=-0.7),
    lower_plaza=dict(x0=1.52, x1=14.0, y0=-8.0, y1=8.0, z_top=-0.6, thick=0.5),
    # v4-A4: x1 2.0→1.52 (하부광장 서단과 플러시) — 하부광장 한복판 자유단 토막 제거
    flank=dict(y_out=0.5, x0=-0.5, x1=1.52, z_top=0.0, z_bot=-1.1),  # 계단 측벽 로우월
    amphi=dict(x0=0.0, y0=6.0, y1=8.0, rise=0.3, depth=0.9, ntiers=3,
               base_z=-0.7),   # F1: 솔리드 바닥 z=-0.7 (하부광장 위 부유 제거)
    # v4-A1: 계단 남측 잔디 구덩이(x 0..1.52 × y −8..−6, 깊이 0.63) 메움.
    #   +Y측 앰피시어터(x 0..2.7, y 6..8)와 대칭되는 상부광장 연장 에이프런.
    south_apron=dict(x0=0.0, x1=1.52, y0=-8.0, y1=-6.0, z_top=0.0, base_z=-0.7),
    # v4-A2: 상부광장 서단(x=−16) 0.60 무방비 낙하 → 잔디 3단 완만 뱅크로 종결
    west_bank=dict(x0=-16.0, step=0.6, drops=(-0.16, -0.32, -0.48),
                   y0=-8.0, y1=8.0, base_z=-1.0),
    # 화단: A/B/D 상부 광장(z 0), C/E 하부 광장(z -0.6)
    planters=[dict(name="A", cx=-5.0, cy=-6.0, base_z=0.0),
              dict(name="B", cx=-9.0, cy=6.0, base_z=0.0),
              dict(name="C", cx=7.0, cy=-5.5, base_z=-0.6),
              dict(name="D", cx=-13.0, cy=2.0, base_z=0.0),    # v4-D10
              dict(name="E", cx=10.0, cy=4.0, base_z=-0.6)],   # v4-D10
    planter=dict(size=3.0, curb_h=0.45, curb_t=0.25, cap_over=0.05,
                 cap_h=0.05, grass_h=0.40),
    # v4-B3: 성목에 신식재 지지대는 모순 → stakes=False (코드 경로는 존치)
    tree=dict(trunk_r=0.06, trunk_h=2.2, stake_r=0.015, stake_h=1.5,
              stake_off=0.5, stakes=False),
    buildings=dict(
        # axis="y": 파사드가 y평면, 창문 x배열 (R/L). axis="x": 파사드 x평면, 창문 y배열 (C).
        R=dict(x0=-18.0, x1=12.0, y0=9.5, y1=14.0, h=14.0, floors=4,
               axis="y", facade_y=9.5, face_dir=-1.0, mat="brick_R"),
        L=dict(x0=-20.0, x1=4.0, y0=-15.0, y1=-10.5, h=10.0, floors=3,
               axis="y", facade_y=-10.5, face_dir=1.0, mat="brick_L"),
        # R2-4: 원경 비스타 차단 건물 C (+X 지평선). 파사드 -X 평면.
        C=dict(x0=24.0, x1=30.0, y0=-12.0, y1=12.0, h=12.0, floors=4,
               axis="x", facade_x=24.0, face_dir=-1.0, mat="brick_R"),
        # 룩 r3: lower_lookback(-X 방향) 지평선 차단 건물 D. 파사드 +X 평면.
        # r3b: 24m는 그림자면 벽이 화면을 압도 → 40m 밖 원경 실루엣으로 후퇴
        D=dict(x0=-42.0, x1=-36.0, y0=-12.0, y1=12.0, h=9.0, floors=3,
               axis="x", facade_x=-36.0, face_dir=1.0, mat="brick_L"),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),
    streetlight=dict(pole_h=6.0, pole_r=0.06,
                     arm_len=1.0, arm_r=0.04, head=0.25),
    # v4-D4: 가로등 1→4본 (6 m 리듬 = 도시 공간 신호). (x, y, base_z)
    streetlights=[(-6.0, 6.8, 0.0), (-12.0, 6.8, 0.0), (-1.2, 6.8, 0.0),
                  (8.0, 6.8, -0.6)],

    # === v4-D 맥락 드레싱 (cue_scene_dressing 소속, 위험 기하 불변) ===
    # D1 건물 R 출입 캐노피 (TerraceR y 8..9.5, top 0 위)
    entry_canopy=dict(x0=-8.0, x1=-4.0, y0=8.0, y1=9.4, z_roof=3.2,
                      post_r=0.08, roof_t=0.14, base_z=0.0),
    # D2 자전거 거치대 4기 (U형 후프 = 기둥 2 + 상단 바)
    # [v5.1] 광장 한복판(x −13.5..−12.7, y −6..−3) → **서측 동선 가장자리**로 이설.
    #   생울타리(x −16.0..−15.4) 동측 0.3 m, 상부 광장 서단 보행 여백에 붙인다.
    #   ys 간격도 등간격 1.0 → 0.95/1.05/0.90 비정형(§3 등간격 금지).
    bike_rack=dict(x_a=-15.1, x_b=-14.3, ys=(-6.85, -5.90, -4.85, -3.95),
                   r=0.05, h=0.75, base_z=0.0),
    # D3 벤치 6기 — (cx, cy, base_z, along, yaw). along="y" → 길이축 Y
    # [v5.1 현실성] 피드백 "벤치가 허허벌판" → **전부 화단(수목) 앵커 옆으로 재배치**
    #   (§3: 앵커 인접 · 격자/등간격 금지 · yaw ±3~8° 지터).
    #   화단 캡 외면(size 3.0 + cap_over 0.05 → ±1.55):
    #   A(−5,−6) B(−9,6) C(7,−5.5) D(−13,2) E(10,4). 이격은 캡 외면 기준,
    #   괄호 안은 yaw 지터로 코너가 파고드는 양(=half_len·sin|yaw|)을 뺀 여유.
    #     0 D-동측 (−11.05, 2.35, yaw −6.0) : 0.175 (−0.094 → 0.081)
    #     1 D-남측 (−13.40,−0.15, yaw +4.0) : 0.375 (−0.063 → 0.312)
    #     2 B-남측 ( −9.35, 4.05, yaw −5.0) : 0.175 (−0.078 → 0.097)
    #     3 A-북측 ( −4.65,−4.05, yaw +3.5) : 0.175 (−0.055 → 0.120)
    #     4 C-서측 (  5.00,−5.80, yaw −7.0) : 0.225 (−0.110 → 0.115)
    #     5 E-남측 ( 10.30, 2.05, yaw +5.0) : 0.175 (−0.078 → 0.097)
    #   카메라 검산(그리드 eye x −2/−5/−10 @ y −2.75, 화각 ±30°; 판정 기준은
    #   N-4 와 동일하게 "근거리(<1.2 m) ∧ 화각 안" 0건):
    #     0·1 : x < −10 → d10 후방, d5/d2 후방            (프레임 밖)
    #     2   : eye(−10) 에서 6.93 m / 방위 +84.6°         (화각 밖)
    #     3   : eye(−10) 5.62 m/−15.5°(원경) · eye(−5) 1.54 m/−76.9°(화각 밖)
    #     4·5 : 하부 광장 — lower_lookback(6,1.5) 에서 72.8°/139° 밖,
    #           amphi_view(5.5,2.5) 에서 132.6°/139° 밖
    #     beauty_overview(−9,−5.5,3) : 3 번이 4.53 m/16.6°(프레임 내, 원경) —
    #       차폐 기준(<1.2 m) 밖. edge_closeup 최근접 7.0 m.
    benches=[(-11.05, 2.35, 0.0, "y", -6.0), (-13.40, -0.15, 0.0, "x", 4.0),
             (-9.35, 4.05, 0.0, "x", -5.0), (-4.65, -4.05, 0.0, "x", 3.5),
             (5.00, -5.80, -0.6, "y", -7.0), (10.30, 2.05, -0.6, "x", 5.0)],
    bench=dict(length=1.8, width=0.45, height=0.45, seat_t=0.06),
    # D5 캠퍼스 게시판 2 (판 + 기둥 2) — (cx, cy, base_z, yaw)
    # [v5.1] 광장 한복판 대칭쌍(x −14, y ±2) → **동선 가장자리 2곳 비대칭**.
    #   0 (−7.2, 7.6, yaw 90) : 건물 R 출입 캐노피(x −8..−4) 앞 보행 동선 옆,
    #     광장 북단(y1 8.0) 에서 0.4 m — 판면이 −Y(광장 쪽)를 본다.
    #   1 (−14.6, −1.2, yaw 180): 서측 가장자리, 판면이 +X(광장 쪽)를 본다.
    #     생울타리 동측 0.8 m · 자전거 거치대(y −6.85..−3.95) 밖.
    #   카메라: 0 → 그리드 전 프리셋 76.9°+ 밖 / amphi_view 13.6 m 원경,
    #           1 → x < −10 전 프리셋 후방. 근접 차폐 0.
    boards=[(-7.2, 7.6, 0.0, 90.0), (-14.6, -1.2, 0.0, 180.0)],
    board=dict(thick=0.12, width=2.4, z0=1.0, z1=2.2, post_r=0.05),
    # [v5 공통 레이어] 한글 사인 — (태그, TEX 키, cx, cy, base_z, yaw, w, h)
    #   [v5.2 사용자] 임의 경고 팻말 제거 — Caution(계단주의) 삭제, 시설 안내만 잔존.
    #   Info(−7.5, −6.8): 화단 A(cx −5, size 3 → x −6.5..−3.5) 서측 1.0 m,
    #     벤치(−9.25, −5.0) 에서 2.50 m.
    #   카메라 검산(그리드 gy=−2.75, eye x −2/−5/−10, 화각 ±30°):
    #     Info    → 후방 / 후방 / −58.3°                    = 전 프리셋 밖
    #     beauty_overview(−9,−5.5) 축 33.1° 대비 Info 74° 밖 → 차폐 0.
    signs=[("Info", "sign_info", -7.5, -6.8, 0.0, 180.0, 1.0, 0.75)],
    # D6 쓰레기통 4
    bins=[(-13.0, -7.2, 0.0), (-4.0, 7.2, 0.0),
          (3.0, -7.2, -0.6), (9.0, 7.2, -0.6)],
    bin_spec=dict(r=0.28, h=0.9),
    # D7 하부광장 볼라드 열 — [v6 판정 §3] **전량 삭제**.
    #   구: x 13.2 · y −6..6 · step 2.4 · r 0.06 · h 0.75 · M["rail"](순백) 6본.
    #   v6 RT 판정이 §2/§3/§4 동시 위반으로 지목:
    #     §2 규격 — h 0.75 < 0.80 하한 / 반사띠 없음 / 간격 2.4 ≠ 1.5
    #     §2 위치 — 잔디–보도 경계(차량 진입 근거 0). 허용 지점(보도-차도 접점 ·
    #               램프/광장 진입부 · 계단 진입 전면) 어느 것도 아님
    #     §3 등간격 정렬 / §4 순백 대면적
    #   본 씬은 보행 전용 캠퍼스 광장이라 **차량 차단선 자체가 근거 없음** →
    #   규격 교체(택2)가 아니라 v5.1 §2 "장식적 볼라드 열 전면 제거" ·
    #   v5.2 §6 "비움이 기본값" 을 따라 삭제한다(판정 권장안 ①).
    #   하부 광장 동단 경계는 화단 E(10, 4)·가로등(8, 6.8)·건물 C(x 24) 가 잇는다.
    # D8 상부광장 서측 낮은 생울타리 (A2 뱅크와 함께 대지 종결)
    west_hedge=dict(x0=-16.0, x1=-15.4, y0=-8.0, y1=8.0, h=0.6, base_z=0.0),
    # D9 앰피 좌면 목재 스트립 (좌석으로 읽히게)
    amphi_seat=dict(y0=6.2, y1=7.8, width=0.4, inset=0.15, thick=0.05,
                    proud=0.012),
    railing=dict(post_r=0.02, post_h=0.9, spacing=1.2, rail_r=0.03,  # R2-5: 상단 레일 0.025→0.03
                 rail_mid_r=0.018, rail_mid_drop=0.45,               # R2-5: 중간 레일
                 ext=1.0, y_lines=(0.0, 5.45, -5.45)),
    tactile=dict(ahead=0.3, depth=0.3, proud=0.004),   # F4: 플러시 근접(4mm), 돌기는 노멀맵

    # --- §3 재질: texture_scale용 물리 크기[m/타일] + 틴트/상수 ---
    material=dict(
        scale=dict(plaza_light=0.75, band_dark=0.6, plaza_lower=0.7,
                   granite_dark=1.0, brick_red=2.0, grass=4.0, tactile=0.3),  # R2-3: grass 2→4
        lower_warm_tint=(1.06, 1.0, 0.94),        # 하부 광장 웜 틴트 (§3)
        building_L_tint=(0.95, 0.92, 0.88),       # 건물 L 약간 다른 톤
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,   # 유리창 (OmniGlass 금지)
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,  # 스테인리스
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,     # 줄기·지지대
        # R2-2: 수관 2종 교대 바인딩. 룩 r3: 여전히 밝아 어두운 올리브+무광으로
        # v4-B1: 0.025/0.045 대역은 정오 태양 아래서도 '검은 얼룩' → 상한(0.06)
        #   근처로 상향해 실루엣 확보. 제약 ②(0.02~0.06) 준수.
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030), canopy_rough=1.0,
        # v4-B2: granite_dark(경계석·밴드)가 검은 구멍으로 읽힘 → 디퓨즈 리프트
        granite_lift_tint=(1.25, 1.25, 1.22),
        hedge_tint=(0.50, 0.62, 0.36),                      # v4-D8 생울타리
        seat_wood=(0.055, 0.036, 0.022), seat_wood_rough=0.8,  # v4-D9 좌면 목재
        sign_color=(0.045, 0.085, 0.19), sign_face=(0.55, 0.56, 0.58),  # v4-D5 게시판
        # [v5.1 §4] 파라펫 0.90 → 0.72 (순백 대면적 금지)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,      # 램프 헤드(주간 비발광)
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
    ),

    # --- §5 조명: v1 noon 검증 상수 이식 (dawn 생략) ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # 태양 방위 사용자 오프셋 — 돔 Z회전에 가산. R2-6: 0→171.5 (월드 태양 방위
    # ≈205°: 프리셋 정면광, 계단 라이저(+X면) 음영으로 노징 대비 강화,
    # 건물 R 그림자는 +X+Y로 빠져 광장 밖).
    SUN_AZ_OFFSET=171.5,

    render=dict(pt_total_spp=512, pt_max_bounces=8),   # §6 PT 값 (v1과 동일)
)


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


# 파라미터 오버라이드 (A/B 렌더 비교용 — 기본 실행엔 영향 없음, v1 패턴)
#   NEGOBS_PARAMS_OVERRIDE='{"SUN_AZ_OFFSET":30}' python scene01_campus_stairs.py
_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

# F8: SCENE_CONFIG 환경변수 오버라이드 (토글 무결성 검증 파이프라인용)
#   NEGOBS_SCENE_CONFIG='{"cue_railing":false}' python scene01_campus_stairs.py
_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [C] 경로·에셋 (브리프 §3 canonical 파일명)
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_HERE, "assets")
S1_DIR = os.path.join(ASSETS_DIR, "scene01")
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene01")

OMNIPBR_PATH = os.path.expanduser(
    "~/miniconda3/envs/env_isaaclab/lib/python3.10/site-packages/"
    "omni/mdl/core/Base/OmniPBR.mdl")

# 역할별 텍스처 세트 (dir + 파일명). 잔디·HDRI는 assets/ 루트 재사용.
TEX = dict(
    plaza_light=dict(dir=S1_DIR, diff="plaza_light_diff.jpg",
                     nor="plaza_light_nor.jpg", rough="plaza_light_rough.jpg"),
    band_dark=dict(dir=S1_DIR, diff="band_dark_diff.jpg",
                   nor="band_dark_nor.jpg", rough="band_dark_rough.jpg"),
    plaza_lower=dict(dir=S1_DIR, diff="plaza_lower_diff.jpg",
                     nor="plaza_lower_nor.jpg", rough="plaza_lower_rough.jpg"),
    granite_dark=dict(dir=S1_DIR, diff="granite_dark_diff.jpg",
                      nor="granite_dark_nor_dx.jpg", rough="granite_dark_rough.jpg"),
    brick_red=dict(dir=S1_DIR, diff="brick_red_diff.jpg",
                   nor="brick_red_nor_dx.jpg", rough="brick_red_rough.jpg"),
    grass=dict(dir=ASSETS_DIR, diff="aerial_grass_rock_diff_4k.jpg",
               nor="aerial_grass_rock_nor_dx_4k.jpg",
               rough="aerial_grass_rock_rough_4k.jpg"),
    tactile=dict(dir=S1_DIR, diff="tactile_yellow_diff.png",
                 nor="tactile_yellow_nor.png"),   # rough 없음
    # [v5 공통 레이어] 한글 사인 패널 (assets/signs/gen_signs.py 생성, diff only)
    sign_info=dict(dir=os.path.join(ASSETS_DIR, "signs"),
                   diff="sign_info.png"),   # [v5.2 사용자] 임의 경고 팻말 제거
)


def _tex_path(role, kind):
    return os.path.join(TEX[role]["dir"], TEX[role][kind])


def _check_assets():
    """브리프 §3 에셋 존재 확인. 없으면 목록 출력 후 종료 (v1 패턴)."""
    missing = []
    for role, spec in TEX.items():
        for kind in ("diff", "nor", "rough"):
            if kind not in spec:
                continue
            p = os.path.join(spec["dir"], spec[kind])
            if not os.path.isfile(p):
                missing.append((role, kind, p))
    hdri = os.path.join(ASSETS_DIR, PARAMS["light"]["hdri"])
    if not os.path.isfile(hdri):
        missing.append(("light", "hdri", hdri))
    if not os.path.isfile(OMNIPBR_PATH):
        missing.append(("material", "mdl", OMNIPBR_PATH))
    if missing:
        print("=" * 64)
        print("[에러] 다음 에셋이 없습니다. assets/scene01/ 다운로드 후 재실행:")
        for role, kind, p in missing:
            print(f"  - [{role}/{kind}] {p}")
        print("=" * 64)
        sys.exit(1)


def _ensure_noon_lookfix(src_path):
    """noon HDRI 파생본(_lookfix.exr) 생성/캐시 — v1에서 그대로 이식.

    ① 태양 디스크(각반경 1.5°)를 서컴솔라 링(1.5~2.5°) p90 휘도로 캡:
       RTX 돔 샘플링의 태양 블러가 만드는 초연질 달걀형 캐스트 섀도 제거.
       제거된 직달 성분은 HDRI 태양 방향에 정합한 DistantLight(0.53°)가 대체.
    ② 지평 아래 -18°~0° 대역을 인접 하늘(elev 0.5~3.5°) 휘도로 리프트.
    실패 시(예: cv2 부재) 원본 경로를 그대로 반환 (경고만).
    """
    out_path = src_path[:-4] + "_lookfix.exr"
    try:
        if (os.path.isfile(out_path)
                and os.path.getmtime(out_path) >= os.path.getmtime(src_path)):
            return out_path
        os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
        import cv2
        rgb = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)[..., ::-1]
        rgb = rgb.astype(np.float64)
        h, w = rgb.shape[:2]
        lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1]
               + 0.0722 * rgb[..., 2])
        iy, ix = np.unravel_index(np.argmax(lum), lum.shape)
        vv = (np.arange(h) + 0.5) / h
        th = np.pi * vv
        ph = 2.0 * np.pi * (np.arange(w) + 0.5) / w
        st, ct = np.sin(th)[:, None], np.cos(th)[:, None]
        dx = st * np.cos(ph)[None, :]
        dy = st * np.sin(ph)[None, :]
        dz = np.broadcast_to(ct, (h, w))
        s = np.array([dx[iy, ix], dy[iy, ix], dz[iy, ix]])
        ang = np.degrees(np.arccos(
            np.clip(dx * s[0] + dy * s[1] + dz * s[2], -1.0, 1.0)))
        ring = (ang > 1.5) & (ang < 2.5)
        cap = np.percentile(lum[ring], 90)
        mask = (ang < 1.5) & (lum > cap)
        scl = np.ones_like(lum)
        scl[mask] = cap / lum[mask]
        out = rgb * scl[..., None]
        elev = 90.0 - 180.0 * vv
        ref = out[(elev > 0.5) & (elev < 3.5)].mean(axis=0)      # (w, 3)
        k = np.ones(129) / 129.0
        ref = np.stack(
            [np.convolve(np.r_[ref[-64:, c], ref[:, c], ref[:64, c]],
                         k, mode="same")[64:-64] for c in range(3)], axis=-1)
        t = np.clip((elev + 24.0) / 6.0, 0.0, 1.0) * (elev < 0.0)
        lift = np.maximum(out, ref[None, :, :])
        out += (lift - out) * t[:, None, None]
        cv2.imwrite(out_path, out[..., ::-1].astype(np.float32),
                    [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_HALF,
                     cv2.IMWRITE_EXR_COMPRESSION, cv2.IMWRITE_EXR_COMPRESSION_ZIP])
        print(f"[HDRI] noon lookfix 생성 (태양 캡 {int(mask.sum())}px, "
              f"cap L={cap:.2f}): {out_path}")
        return out_path
    except Exception as e:                       # pragma: no cover
        print(f"[HDRI][경고] lookfix 생성 실패({e}) — 원본 사용")
        return src_path


def build_views():
    """§6 카메라 프리셋: h·d 그리드 9장 + 미장센 4장."""
    views = {}
    # R2-1: 그리드 프리셋 y를 0→-2.75 (계단 좌반부 중심선)로 이동해 중앙 난간(y=0) 회피
    gy = -2.75
    for hh in (0.3, 0.9, 1.8):
        for dd in (2, 5, 10):
            eye = [-float(dd), gy, float(hh)]
            p = math.radians(-10.0)              # 피치 -10°, +X를 봄
            tgt = [eye[0] + 5.0 * math.cos(p), gy, eye[2] + 5.0 * math.sin(p)]
            views[f"preset_h{hh}_d{dd}"] = dict(eye=eye, tgt=tgt)
    # 룩 r3: 더 낮고 가깝게 — 계단 밴드가 실루엣으로 걸리고 건물 C가 배경을 채움
    views["beauty_overview"] = dict(eye=[-9.0, -5.5, 3.0], tgt=[2.5, 2.0, -1.3])
    views["lower_lookback"] = dict(eye=[6.0, 1.5, 1.0], tgt=[-2.0, 0.0, 0.4])
    views["edge_closeup"] = dict(eye=[-1.2, -1.0, 0.55], tgt=[0.8, 0.3, -0.45])
    # R2-7: 하부 광장에서 좌석단 정면·계단 측벽을 사선으로 (뒷벽 -Y면 회피)
    views["amphi_view"] = dict(eye=[5.5, 2.5, 0.75], tgt=[0.8, 7.2, -0.1])
    return views


# ===========================================================================
# [D] Isaac Sim 씬 조립 + 메인 루프 (__main__ 전용)
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. beauty_overview  — 새 캠퍼스 광장 인상 (포장 줄무늬·화단·건물·앰피 식별)
 2. h0.3·d5~10       — 계단 디딤면이 grazing 각에서 소실되는가
 3. h1.8·d2          — 계단이 명확히 보이는가
 4. cue ON vs OFF    — 계단·광장 기하 트랜스폼 동일한가
 5. 재질             — 타일 반복·늘어남·Z파이팅·앨리어싱 없는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    _check_assets()

    # ── 1단계: Isaac Sim 부팅 (SimulationApp이 무조건 먼저 — v9 검증 블록) ──
    from isaacsim import SimulationApp
    simulation_app = SimulationApp(
        {"headless": capture_mode, "width": 1920, "height": 1080})

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom, UsdShade, UsdLux, UsdPhysics, Sdf, Gf
    from omni.kit.viewport.utility import get_active_viewport, \
        capture_viewport_to_file
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    settings.set("/rtx/post/dlss/execMode", 2)     # DLSS Quality
    settings.set("/rtx/post/aa/op", 3)             # DLSS AA
    # 뷰포트 그리드·축 가이드가 렌더에 찍히지 않게 전부 끔 (캡처 위생, v1)
    settings.set("/app/viewport/grid/enabled", False)
    settings.set("/persistent/app/viewport/displayOptions", 0)
    settings.set("/app/viewport/show/grid", False)
    settings.set("/app/viewport/outline/enabled", False)

    stage = omni.usd.get_context().get_stage()

    # ── 스테이지 단위 (§1: Z-up, meter) ──
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    if abs(mpu - 1.0) > 1e-9:
        print(f"[경고] metersPerUnit={mpu} → 1.0(미터)으로 설정")
        UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

    UsdGeom.Xform.Define(stage, "/World")
    UsdGeom.Xform.Define(stage, "/World/Scene01")
    cfg = SCENE_CONFIG
    mp = PARAMS["material"]

    # -------------------------------------------------------------------
    # 지오메트리 헬퍼 (UsdGeom.Cube + Cylinder + Sphere, xformOp 통일)
    # 주의: UsdGeom.Cube는 size=2 기본(±1) → 스케일 = 원하는 치수/2
    # -------------------------------------------------------------------
    def bind_mtl(prim, mtl):
        if mtl is not None:
            UsdShade.MaterialBindingAPI.Apply(prim).Bind(mtl)

    def add_box(path, center, size, mtl=None, collider=False, rotZ=0.0):
        # [v5.1] rotZ 추가 — 배치 비정형(yaw 지터) 용. op 순서는 T → Rz → S
        #   (USD 표준 TRS: 스케일이 먼저 적용된 뒤 회전 → 비등방 박스도 전단 없음).
        cube = UsdGeom.Cube.Define(stage, path)
        cube.CreateSizeAttr(2.0)
        cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
        xf = UsdGeom.Xformable(cube)
        xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
        if abs(rotZ) > 1e-9:
            xf.AddRotateZOp().Set(float(rotZ))
        xf.AddScaleOp().Set(Gf.Vec3f(float(size[0]) / 2.0,
                                     float(size[1]) / 2.0,
                                     float(size[2]) / 2.0))
        prim = cube.GetPrim()
        bind_mtl(prim, mtl)
        if collider:
            UsdPhysics.CollisionAPI.Apply(prim)
        return cube

    def add_cylinder(path, center, radius, height, mtl=None,
                     rotY=0.0, rotX=0.0, collider=False):
        cyl = UsdGeom.Cylinder.Define(stage, path)
        cyl.CreateRadiusAttr(float(radius))
        cyl.CreateHeightAttr(float(height))
        cyl.CreateAxisAttr(UsdGeom.Tokens.z)
        xf = UsdGeom.Xformable(cyl)
        # 순서: translate → rotate (프림 원점에서 회전 후 이동)
        xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
        if abs(rotY) > 1e-9:
            xf.AddRotateYOp().Set(float(rotY))
        if abs(rotX) > 1e-9:
            xf.AddRotateXOp().Set(float(rotX))
        prim = cyl.GetPrim()
        bind_mtl(prim, mtl)
        if collider:
            UsdPhysics.CollisionAPI.Apply(prim)
        return cyl

    def add_sphere(path, center, scale3, mtl=None):
        sph = UsdGeom.Sphere.Define(stage, path)
        sph.CreateRadiusAttr(1.0)
        xf = UsdGeom.Xformable(sph)
        xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
        xf.AddScaleOp().Set(Gf.Vec3f(*[float(s) for s in scale3]))
        bind_mtl(sph.GetPrim(), mtl)
        return sph

    # -------------------------------------------------------------------
    # setup_materials — OmniPBR 헬퍼 make_pbr 하나로 전 재질 생성
    # -------------------------------------------------------------------
    def make_pbr(path, diff=None, nor=None, rough=None, scale_m=1.0,
                 tint=None, metallic=0.0, roughness_const=None,
                 diffuse_color=None, bump=1.0):
        """[사실화 v1] scene_common 으로 위임.

        scene01 은 이 라이브러리의 **첫 씬**이라 재질 팩토리를 자체 구현했고,
        이후 그 코드가 `scene_common.make_pbr` 로 추출됐다. 그런데 scene01 만
        로컬 사본을 계속 쓰는 바람에 **33씬 중 유일하게 공용 계층을 타지 않는
        씬**이 됐다. 사실화 룩 레이어(역할별 처방·MDL 교체·베벨·채도)가
        `scene_common.make_pbr` 에 들어가면서 scene01 에만 아무것도 적용되지
        않는 문제가 드러나 여기서 정리한다.

        위임 전후로 동작은 동일하다 — 로컬 사본은 `sc.make_pbr` 의 기능적
        부분집합이었고(specular_level·emission·uv_mode 없음), 호출부도 그
        인자만 쓴다. 검증: 룩 레이어 OFF 로 렌더해 기존 산출과 대조.
        """
        return sc.make_pbr(stage, path, diff=diff, nor=nor, rough=rough,
                           scale_m=scale_m, tint=tint, metallic=metallic,
                           roughness_const=roughness_const,
                           diffuse_color=diffuse_color, bump=bump)

    def setup_materials():
        sc = mp["scale"]
        M = {}
        M["plaza_light"] = make_pbr(
            "/World/Looks/PlazaLight", _tex_path("plaza_light", "diff"),
            _tex_path("plaza_light", "nor"), _tex_path("plaza_light", "rough"),
            sc["plaza_light"])
        # 룩 r3: PavingStones127은 결이 강해 밴드가 나무 데크처럼 읽힘 →
        # 경계석과 같은 어두운 화강암 타일(granite_dark)로 교체 (조인트 0.9m)
        # v4-B2: 밴드도 granite_dark 계열 — 리프트 틴트로 검은 줄무늬 완화
        M["band_dark"] = make_pbr(
            "/World/Looks/BandDark", _tex_path("granite_dark", "diff"),
            _tex_path("granite_dark", "nor"), _tex_path("granite_dark", "rough"),
            0.9, tint=mp["granite_lift_tint"])
        # 하부 광장: cue_material_break 에 따라 재질·틴트 결정 (기하 불변)
        if cfg["cue_material_break"]:
            M["lower"] = make_pbr(
                "/World/Looks/PlazaLower", _tex_path("plaza_lower", "diff"),
                _tex_path("plaza_lower", "nor"),
                _tex_path("plaza_lower", "rough"),
                sc["plaza_lower"], tint=mp["lower_warm_tint"])
        else:
            M["lower"] = make_pbr(
                "/World/Looks/PlazaLower", _tex_path("plaza_light", "diff"),
                _tex_path("plaza_light", "nor"),
                _tex_path("plaza_light", "rough"), sc["plaza_light"])
        M["granite_dark"] = make_pbr(
            "/World/Looks/GraniteDark", _tex_path("granite_dark", "diff"),
            _tex_path("granite_dark", "nor"),
            _tex_path("granite_dark", "rough"), sc["granite_dark"],
            tint=mp["granite_lift_tint"])                     # v4-B2
        M["brick_R"] = make_pbr(
            "/World/Looks/BrickR", _tex_path("brick_red", "diff"),
            _tex_path("brick_red", "nor"), _tex_path("brick_red", "rough"),
            sc["brick_red"])
        M["brick_L"] = make_pbr(
            "/World/Looks/BrickL", _tex_path("brick_red", "diff"),
            _tex_path("brick_red", "nor"), _tex_path("brick_red", "rough"),
            sc["brick_red"], tint=mp["building_L_tint"])
        M["grass"] = make_pbr(
            "/World/Looks/Grass", _tex_path("grass", "diff"),
            _tex_path("grass", "nor"), _tex_path("grass", "rough"),
            sc["grass"], tint=(0.55, 0.68, 0.42))   # R2-3: 타일 반복 완화 + 초록 틴트
        M["tactile"] = make_pbr(
            "/World/Looks/Tactile", _tex_path("tactile", "diff"),
            _tex_path("tactile", "nor"), None, sc["tactile"])
        # 상수 컬러 재질
        M["glass"] = make_pbr("/World/Looks/Glass", diffuse_color=mp["glass_color"],
                              roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = make_pbr("/World/Looks/Rail", diffuse_color=mp["rail_color"],
                             metallic=mp["rail_metallic"],
                             roughness_const=mp["rail_rough"])
        M["wood"] = make_pbr("/World/Looks/Wood", diffuse_color=mp["wood_color"],
                             roughness_const=mp["wood_rough"])
        M["canopy_a"] = make_pbr("/World/Looks/CanopyA",
                                 diffuse_color=mp["canopy_a"],
                                 roughness_const=mp["canopy_rough"])
        M["canopy_b"] = make_pbr("/World/Looks/CanopyB",
                                 diffuse_color=mp["canopy_b"],
                                 roughness_const=mp["canopy_rough"])
        M["parapet"] = make_pbr("/World/Looks/Parapet",
                                diffuse_color=mp["parapet_color"],
                                roughness_const=mp["parapet_rough"])
        M["lamp"] = make_pbr("/World/Looks/Lamp", diffuse_color=mp["lamp_color"],
                             roughness_const=mp["lamp_rough"])
        M["pole"] = make_pbr("/World/Looks/Pole", diffuse_color=mp["pole_color"],
                             metallic=mp["pole_metallic"],
                             roughness_const=mp["pole_rough"])
        # v4-D 드레싱 전용 재질
        M["hedge"] = make_pbr(
            "/World/Looks/Hedge", _tex_path("grass", "diff"),
            _tex_path("grass", "nor"), _tex_path("grass", "rough"),
            1.2, tint=mp["hedge_tint"])
        M["seat_wood"] = make_pbr("/World/Looks/SeatWood",
                                  diffuse_color=mp["seat_wood"],
                                  roughness_const=mp["seat_wood_rough"])
        # [v5.1 §4] 인스턴스 틴트 지터 ±5% — 벤치가 같은 재질 복제로 읽히지 않게.
        for _i, _f in enumerate((0.95, 1.0, 1.05)):
            M[f"seat_wood_{_i}"] = make_pbr(
                f"/World/Looks/SeatWood_{_i}",
                diffuse_color=tuple(c * _f for c in mp["seat_wood"]),
                roughness_const=mp["seat_wood_rough"] * (1.0 + 0.04 * (_i - 1)))
        M["sign"] = make_pbr("/World/Looks/Sign",
                             diffuse_color=mp["sign_color"],
                             roughness_const=0.5)
        M["sign_face"] = make_pbr("/World/Looks/SignFace",
                                  diffuse_color=mp["sign_face"],
                                  roughness_const=0.6)
        return M

    # -------------------------------------------------------------------
    # build_* 함수들 (브리프 §7)
    # -------------------------------------------------------------------
    def build_upper_plaza(M):
        up = PARAMS["upper_plaza"]
        b = PARAMS["band"]
        cx = (up["x0"] + up["x1"]) / 2.0
        cy = (up["y0"] + up["y1"]) / 2.0
        Lx = up["x1"] - up["x0"]
        Ly = up["y1"] - up["y0"]
        top = up["z_top"]
        th = up["thick"]
        add_box("/World/Scene01/UpperPlaza", (cx, cy, top - th / 2.0),
                (Lx, Ly, th), M["plaza_light"], collider=True)
        # 차콜 밴드: Y로 달리는 별도 박스(재질 분리), X방향 spacing 반복.
        # 상판에서 3mm 돌출·5cm 매입 → 상판 상면과 동일평면 없음(Z파이팅 방지).
        z_bot = top - b["embed"]
        z_top = top + b["proud"]
        cz = (z_top + z_bot) / 2.0
        hz = z_top - z_bot
        n = 0
        x = up["x0"] + b["spacing"]
        while x < up["x1"] - 1e-6:
            add_box(f"/World/Scene01/Band_{n}", (x, cy, cz),
                    (b["width"], Ly, hz), M["band_dark"])
            x += b["spacing"]
            n += 1

    def build_stairs(M):
        """하행 4단. 각 단은 상단면(tread)이 노출되는 솔리드 박스로 적층."""
        st = PARAMS["stairs"]
        tread, riser, ns = st["tread"], st["riser"], st["nsteps"]
        cy = (st["y0"] + st["y1"]) / 2.0
        Ly = st["y1"] - st["y0"]
        base = st["base_z"]
        for i in range(1, ns + 1):
            ztop = -riser * i                       # i번째 단 상단면 높이
            xa = st["x0"] + tread * (i - 1)
            xb = st["x0"] + tread * i
            cx = (xa + xb) / 2.0
            cz = (ztop + base) / 2.0
            hz = ztop - base
            add_box(f"/World/Scene01/Step_{i}", (cx, cy, cz),
                    (tread, Ly, hz), M["plaza_light"], collider=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 계단+하부광장 전체를 상부와 같은
        z=0 평지로 통일 → 낙차/위험을 완전히 제거한다 (브리프 편향 교정 해석)."""
        st = PARAMS["stairs"]
        lp = PARAMS["lower_plaza"]
        up = PARAMS["upper_plaza"]
        x0, x1 = st["x0"], lp["x1"]
        y0, y1 = up["y0"], up["y1"]
        th = up["thick"]
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        add_box("/World/Scene01/FlatFill", (cx, cy, up["z_top"] - th / 2.0),
                (x1 - x0, y1 - y0, th), M["plaza_light"], collider=True)

    def build_lower_plaza(M):
        lp = PARAMS["lower_plaza"]
        cx = (lp["x0"] + lp["x1"]) / 2.0
        cy = (lp["y0"] + lp["y1"]) / 2.0
        add_box("/World/Scene01/LowerPlaza",
                (cx, cy, lp["z_top"] - lp["thick"] / 2.0),
                (lp["x1"] - lp["x0"], lp["y1"] - lp["y0"], lp["thick"]),
                M["lower"], collider=True)

    def build_flank_walls(M):
        """계단 측벽 로우월: y ±5.5 바깥 0.5m, 상부면 z=0, 하부까지."""
        fl = PARAMS["flank"]
        st = PARAMS["stairs"]
        cx = (fl["x0"] + fl["x1"]) / 2.0
        Lx = fl["x1"] - fl["x0"]
        cz = (fl["z_top"] + fl["z_bot"]) / 2.0
        hz = fl["z_top"] - fl["z_bot"]
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            yc = sgn * (st["y1"] + fl["y_out"] / 2.0)   # 5.5→6.0 벽, 중심 5.75
            add_box(f"/World/Scene01/FlankWall_{tag}", (cx, yc, cz),
                    (Lx, fl["y_out"], hz), M["granite_dark"], collider=True)

    def build_amphitheater(M):
        """앰피시어터 좌면 3단 (사진1 우측 모티프). F1: 상단 z = +0.3−(i−1)*0.3
        (+0.3/0.0/−0.3)로 하강 — 최상단이 상부광장보다 0.3 높은 벤치로 읽히고
        마지막 티어(−0.3)에서 하부광장(−0.6)으로 떨어진다. 솔리드 바닥 z=−0.7."""
        am = PARAMS["amphi"]
        cy = (am["y0"] + am["y1"]) / 2.0
        Ly = am["y1"] - am["y0"]
        base = am["base_z"]
        for i in range(1, am["ntiers"] + 1):
            ztop = 0.3 - (i - 1) * am["rise"]
            xa = am["x0"] + am["depth"] * (i - 1)
            xb = am["x0"] + am["depth"] * i
            cx = (xa + xb) / 2.0
            add_box(f"/World/Scene01/AmphiTier_{i}",
                    (cx, cy, (ztop + base) / 2.0),
                    (am["depth"], Ly, ztop - base), M["plaza_light"],
                    collider=True)

    def build_tree(prefix, cx, cy, gz):
        """[사실화 v1] `scene_common.build_tree` 로 위임.

        scene01 은 이 라이브러리의 첫 씬이라 나무 빌더도 자체 사본을 갖고
        있었다(`make_pbr`·캡처 블록과 같은 패턴). 그 결과 **공용 계층 개선이
        scene01 만 비껴갔다** — 사실화 라운드에서 `sc.build_tree` 내부를 실제
        식생 USD 에셋으로 교체했는데 scene01 의 나무만 여전히 구(sphere) 블롭
        이었다.

        옛 주석은 "sc 로 갈아타면 v4-B3 로 차단한 지지대가 되살아난다"고 적혀
        있었으나, 공용 함수는 v6 판정에서 이미 `stakes=False` 가 기본값이 됐다.
        차단 사유가 사라졌으므로 위임한다.
        """
        tr = PARAMS["tree"]
        sc.build_tree(stage, prefix, cx, cy, gz,
                      M["wood"], M["canopy_a"], M["canopy_b"],
                      trunk_r=tr["trunk_r"], trunk_h=tr["trunk_h"],
                      stake_r=tr["stake_r"], stake_h=tr["stake_h"],
                      stake_off=tr["stake_off"],
                      stakes=bool(tr.get("stakes", False)))

    def build_planters(M):
        pl = PARAMS["planter"]
        S, h, t = pl["size"], pl["curb_h"], pl["curb_t"]
        over, cap_h, gh = pl["cap_over"], pl["cap_h"], pl["grass_h"]
        half = S / 2.0
        for spec in PARAMS["planters"]:
            cx, cy, bz = spec["cx"], spec["cy"], spec["base_z"]
            base = f"/World/Scene01/Planter_{spec['name']}"
            top = bz + h
            # 경계석 4벽 프레임 (짙은 화강암)
            walls = [
                ("S", cx, cy - half + t / 2.0, S, t),
                ("N", cx, cy + half - t / 2.0, S, t),
                ("W", cx - half + t / 2.0, cy, t, S - 2 * t),
                ("E", cx + half - t / 2.0, cy, t, S - 2 * t),
            ]
            for tag, wx, wy, sx, sy in walls:
                add_box(f"{base}/Curb_{tag}", (wx, wy, bz + h / 2.0),
                        (sx, sy, h), M["granite_dark"], collider=True)
                # 캡: 5cm 오버행 (짙은 화강암)
                add_box(f"{base}/Cap_{tag}", (wx, wy, top + cap_h / 2.0),
                        (sx + 2 * over if sx < sy else sx,
                         sy + 2 * over if sy <= sx else sy, cap_h),
                        M["granite_dark"])
            # 잔디 상면 (경계석 안쪽, 캡 아래)
            add_box(f"{base}/Grass", (cx, cy, bz + gh / 2.0),
                    (S - 2 * t, S - 2 * t, gh), M["grass"])
            build_tree(base, cx, cy, bz + gh)

    def build_buildings(M):
        wd = PARAMS["window"]
        for key, bd in PARAMS["buildings"].items():
            cx = (bd["x0"] + bd["x1"]) / 2.0
            cy = (bd["y0"] + bd["y1"]) / 2.0
            Lx = bd["x1"] - bd["x0"]
            Ly = bd["y1"] - bd["y0"]
            hh = bd["h"]
            base = f"/World/Scene01/Building_{key}"
            # F3: 셸을 z -1.0까지 연장(높이 hh+1.0, 중심 (hh-1)/2) — 하부광장
            # 쪽에서 기초가 부유하지 않게. 파라펫·창문 z는 불변.
            add_box(f"{base}/Shell", (cx, cy, (hh - 1.0) / 2.0),
                    (Lx, Ly, hh + 1.0), M[bd["mat"]], collider=True)
            # 창문 그리드: floors 층 × ncols 열. F2: 두께 0.03 다크글라스 패널을
            # 파사드에서 2cm 돌출·1cm 매입 (동일평면 Z파이팅 회피, 불리언 불필요).
            # R2-4: axis="y"는 파사드 y평면(창문 x배열), "x"는 x평면(창문 y배열).
            fstep = hh / bd["floors"]
            if bd.get("axis", "y") == "y":
                gy = bd["facade_y"] + bd["face_dir"] * 0.005
                usable = Lx - 2 * wd["margin"]
                ncols = max(1, int(usable / wd["col_step"]))
                for f in range(bd["floors"]):
                    zc = fstep * f + fstep * 0.5
                    for c in range(ncols):
                        xc = bd["x0"] + wd["margin"] + (c + 0.5) * (usable / ncols)
                        add_box(f"{base}/Win_{f}_{c}", (xc, gy, zc),
                                (wd["w"], 0.03, wd["h"]), M["glass"])
            else:
                gx = bd["facade_x"] + bd["face_dir"] * 0.005
                usable = Ly - 2 * wd["margin"]
                ncols = max(1, int(usable / wd["col_step"]))
                for f in range(bd["floors"]):
                    zc = fstep * f + fstep * 0.5
                    for c in range(ncols):
                        yc = bd["y0"] + wd["margin"] + (c + 0.5) * (usable / ncols)
                        add_box(f"{base}/Win_{f}_{c}", (gx, yc, zc),
                                (0.03, wd["w"], wd["h"]), M["glass"])
            # 상단 백색 파라펫 밴드 (약간 오버행)
            add_box(f"{base}/Parapet", (cx, cy, hh + 0.25),
                    (Lx + 0.2, Ly + 0.2, 0.5), M["parapet"])

    def build_streetlight(M):
        """v4-D4: PARAMS['streetlights'] 목록(x, y, base_z)으로 다본 배치."""
        sl = PARAMS["streetlight"]
        for k, (x, y, bz) in enumerate(PARAMS["streetlights"]):
            base = f"/World/Scene01/Streetlight_{k}"
            add_cylinder(f"{base}/Pole", (x, y, bz + sl["pole_h"] / 2.0),
                         sl["pole_r"], sl["pole_h"], M["pole"], collider=True)
            # 쌍암 + 램프 헤드 (±X 방향)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                ax = x + sgn * sl["arm_len"] / 2.0
                add_cylinder(f"{base}/Arm_{tag}",
                             (ax, y, bz + sl["pole_h"] - 0.1),
                             sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                hx = x + sgn * sl["arm_len"]
                add_box(f"{base}/Head_{tag}",
                        (hx, y, bz + sl["pole_h"] - 0.15),
                        (sl["head"], sl["head"], 0.12), M["lamp"])

    def build_south_apron(M):
        """v4-A1 [치명]: 계단 남측 잔디 함몰 구덩이 메움.

        기존 좌표 검증: 상부광장 x≤0 · 하부광장 x≥1.52 · 계단 y≥−5.5 ·
        FlankWall_N y −6.0..−5.5 · TerraceL y≤−8 → 사각 x 0..1.52 × y −8..−6
        을 덮는 프림이 전무했고 바닥은 GroundGrass(−0.63)뿐 → 깊이 0.63 구덩이.
        +Y측은 앰피시어터(x 0..2.7, y 6..8)가 같은 자리를 채우므로 좌우 비대칭.
        → 상부광장과 동일 상면(z=0)·동일 재질의 에이프런 1매로 대칭 복구.
           동측 절단면(x=1.52)은 하부광장(−0.6) 서면과 정확히 접함(플랭크월과 동일).
        """
        ap = PARAMS["south_apron"]
        add_box("/World/Scene01/SouthApron",
                ((ap["x0"] + ap["x1"]) / 2.0, (ap["y0"] + ap["y1"]) / 2.0,
                 (ap["z_top"] + ap["base_z"]) / 2.0),
                (ap["x1"] - ap["x0"], ap["y1"] - ap["y0"],
                 ap["z_top"] - ap["base_z"]),
                M["plaza_light"], collider=True)
        # 같은 사각의 +Y 대응(x 0..1.52, y 6..8)은 앰피시어터가 채우지만
        # 앰피는 cue_scene_dressing 소속 → 드레싱 OFF 시 동일 구덩이가 열린다.
        # 토글 무결성을 위해 그 경우에만 북측 에이프런을 깐다(앰피 상면과 중복 회피).
        if not cfg["cue_scene_dressing"]:
            add_box("/World/Scene01/NorthApron",
                    ((ap["x0"] + ap["x1"]) / 2.0, 7.0,
                     (ap["z_top"] + ap["base_z"]) / 2.0),
                    (ap["x1"] - ap["x0"], 2.0, ap["z_top"] - ap["base_z"]),
                    M["plaza_light"], collider=True)

    def build_west_bank(M):
        """v4-A2: 상부광장 서단(x=−16) 0.60 m 무방비 낙하를 잔디 3단으로 종결.
        단차 0.16 / 0.16 / 0.16 + 잔디까지 0.15 → 전부 0.2 m 이하(보행 가능)."""
        wb = PARAMS["west_bank"]
        for i, ztop in enumerate(wb["drops"]):
            x1 = wb["x0"] - wb["step"] * i
            x0 = x1 - wb["step"]
            add_box(f"/World/Scene01/WestBank_{i}",
                    ((x0 + x1) / 2.0, (wb["y0"] + wb["y1"]) / 2.0,
                     (ztop + wb["base_z"]) / 2.0),
                    (wb["step"], wb["y1"] - wb["y0"], ztop - wb["base_z"]),
                    M["grass"], collider=True)

    def build_surroundings(M):
        """F3: 부지 바깥 허공 방지 (cue_scene_dressing 무관, 상시 생성)."""
        # ① 대형 잔디 대지: 상면 z=−0.63 (하부광장 −0.6과 3cm 단차로 동일평면 회피)
        add_box("/World/Scene01/GroundGrass", (0.0, 0.0, -0.63 - 0.25),
                (120.0, 120.0, 0.5), M["grass"])
        # ② 건물 앞 테라스(보행 띠): 상면 z=0, 바닥 −1.1. 하부광장과 만나는
        #    y=8 / y=−8 면이 0.6m 옹벽으로 노출되는 것은 의도됨.
        add_box("/World/Scene01/TerraceR", (-2.0, 8.75, -0.55),
                (32.0, 1.5, 1.1), M["plaza_light"], collider=True)   # x −18..14, y 8..9.5
        add_box("/World/Scene01/TerraceL", (-3.0, -9.25, -0.55),
                (34.0, 2.5, 1.1), M["plaza_light"], collider=True)   # x −20..14, y −10.5..−8
        # ③ v4-A2: 서측 잔디 뱅크 (상시 — 상부광장은 토글과 무관하게 존재)
        build_west_bank(M)

    # -------------------------------------------------------------------
    # v4-D 맥락 드레싱 (cue_scene_dressing 소속) — "캠퍼스"로 읽히게
    # -------------------------------------------------------------------
    def build_bench_unit(M, prefix, cx, cy, bz, along="x", yaw=0.0, mtl=None):
        """좌판 + 다리 4. along='y'면 길이축을 Y로(포장 밴드와 평행).
        [v5.1] yaw(도) 지터 — 좌판·다리 전부 중심 (cx,cy) 둘레로 회전한다."""
        bs = PARAMS["bench"]
        L, W, H, st = bs["length"], bs["width"], bs["height"], bs["seat_t"]
        sx, sy = (L, W) if along == "x" else (W, L)
        mt = mtl if mtl is not None else M["seat_wood"]
        add_box(f"{prefix}/Seat", (cx, cy, bz + H - st / 2.0),
                (sx, sy, st), mt, collider=True, rotZ=yaw)
        lx = sx / 2.0 - 0.09
        ly = sy / 2.0 - 0.09
        legh = H - st
        ca, sa = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        for i, (ox, oy) in enumerate(((lx, ly), (lx, -ly), (-lx, ly),
                                      (-lx, -ly))):
            rx, ry = ox * ca - oy * sa, ox * sa + oy * ca
            add_box(f"{prefix}/Leg_{i}", (cx + rx, cy + ry, bz + legh / 2.0),
                    (0.07, 0.07, legh), mt, rotZ=yaw)

    def build_canopy_unit(M, prefix, x0, x1, y0, y1, z_roof, post_r, bz,
                          roof_t):
        """캐노피: 지붕판 1 + 모서리 기둥 4 (scene_common.build_canopy 동형)."""
        add_box(f"{prefix}/Roof", ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                                   z_roof + roof_t / 2.0),
                (x1 - x0, y1 - y0, roof_t), M["parapet"], collider=True)
        ph = z_roof - bz
        for i, (px, py) in enumerate(((x0 + post_r, y0 + post_r),
                                      (x0 + post_r, y1 - post_r),
                                      (x1 - post_r, y0 + post_r),
                                      (x1 - post_r, y1 - post_r))):
            add_cylinder(f"{prefix}/Post_{i}", (px, py, bz + ph / 2.0),
                         post_r, ph, M["pole"], collider=True)

    def build_dressing_props(M):
        """D1~D9: 캐노피·자전거 거치대·벤치·게시판·쓰레기통·생울타리·좌면.
        (D7 볼라드 열은 v6 판정으로 삭제 — PARAMS['...'] D7 주석 참조)"""
        R = "/World/Scene01"
        # D1 건물 R 출입 캐노피
        ec = PARAMS["entry_canopy"]
        build_canopy_unit(M, f"{R}/EntryCanopy", ec["x0"], ec["x1"], ec["y0"],
                          ec["y1"], ec["z_roof"], ec["post_r"], ec["base_z"],
                          ec["roof_t"])
        # D2 자전거 거치대 4기 (U형 후프)
        br = PARAMS["bike_rack"]
        for k, y in enumerate(br["ys"]):
            for tag, x in (("A", br["x_a"]), ("B", br["x_b"])):
                add_cylinder(f"{R}/BikeRack_{k}/Post{tag}",
                             (x, y, br["base_z"] + br["h"] / 2.0),
                             br["r"], br["h"], M["rail"], collider=True)
            add_cylinder(f"{R}/BikeRack_{k}/Bar",
                         ((br["x_a"] + br["x_b"]) / 2.0, y,
                          br["base_z"] + br["h"] - br["r"]),
                         br["r"], abs(br["x_b"] - br["x_a"]), M["rail"],
                         rotY=90.0)
        # D3 벤치 6기 — [v5.1] 화단 앵커 옆 + yaw 지터 + 인스턴스 틴트 지터(§4)
        for k, (cx, cy, bz, along, yaw) in enumerate(PARAMS["benches"]):
            build_bench_unit(M, f"{R}/Bench_{k}", cx, cy, bz, along, yaw=yaw,
                             mtl=M[f"seat_wood_{k % 3}"])
        # D5 게시판 2 (판 + 기둥 2 + 백색 게시면) — [v5.1] yaw 지원
        #   로컬축: 판 두께 = 법선 n(yaw), 판 폭 = 접선 t = n 을 +90° 돌린 방향.
        bo = PARAMS["board"]
        for k, (cx, cy, bz, yaw) in enumerate(PARAMS["boards"]):
            zc = (bo["z0"] + bo["z1"]) / 2.0
            hz = bo["z1"] - bo["z0"]
            ca, sa = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
            add_box(f"{R}/Board_{k}/Panel", (cx, cy, bz + zc),
                    (bo["thick"], bo["width"], hz), M["sign"], collider=True,
                    rotZ=yaw)
            fo = bo["thick"] / 2.0 + 0.006      # 게시면은 −법선 쪽(접근면)
            add_box(f"{R}/Board_{k}/Face", (cx - ca * fo, cy - sa * fo, bz + zc),
                    (0.012, bo["width"] - 0.24, hz - 0.16), M["sign_face"],
                    rotZ=yaw)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                d = sgn * (bo["width"] / 2.0 - 0.12)
                add_cylinder(f"{R}/Board_{k}/Post_{tag}",
                             (cx - sa * d, cy + ca * d, bz + bo["z1"] / 2.0),
                             bo["post_r"], bo["z1"], M["pole"], collider=True)
        # D6 쓰레기통 4
        bn = PARAMS["bin_spec"]
        for k, (cx, cy, bz) in enumerate(PARAMS["bins"]):
            add_cylinder(f"{R}/Bin_{k}/Body", (cx, cy, bz + bn["h"] / 2.0),
                         bn["r"], bn["h"], M["pole"], collider=True)
            add_cylinder(f"{R}/Bin_{k}/Rim", (cx, cy, bz + bn["h"] + 0.02),
                         bn["r"] * 1.1, 0.04, M["rail"])
        # D7 볼라드 열 — [v6 판정 §3] 삭제(PARAMS 주석의 §2/§3/§4 위반 근거 참조).
        # D8 상부광장 서측 낮은 생울타리 (뱅크 상단 은폐 + 대지 종결)
        wh = PARAMS["west_hedge"]
        add_box(f"{R}/WestHedge",
                ((wh["x0"] + wh["x1"]) / 2.0, (wh["y0"] + wh["y1"]) / 2.0,
                 wh["base_z"] + wh["h"] / 2.0),
                (wh["x1"] - wh["x0"], wh["y1"] - wh["y0"], wh["h"]),
                M["hedge"], collider=True)
        # D9 앰피 좌면 목재 스트립 3 (티어를 좌석으로 읽히게)
        am = PARAMS["amphi"]
        se = PARAMS["amphi_seat"]
        for i in range(1, am["ntiers"] + 1):
            ztop = 0.3 - (i - 1) * am["rise"]
            xb = am["x0"] + am["depth"] * i
            bx = xb - se["inset"] - se["width"] / 2.0
            z_hi = ztop + se["proud"]
            add_box(f"{R}/AmphiSeat_{i}",
                    (bx, (se["y0"] + se["y1"]) / 2.0, z_hi - se["thick"] / 2.0),
                    (se["width"], se["y1"] - se["y0"], se["thick"]),
                    M["seat_wood"])

    def build_signs():
        """[v5 공통 레이어] 한글 사인 — sc.build_sign(지주 + st-UV 패널 + 배킹).
        [v5.2 사용자] 임의 경고 팻말 제거 — 시설 안내(sign_info)만 배치.
        좌표·카메라 검산은 PARAMS['signs'] 주석 참조. 위험 기하 불변."""
        back = sc.make_pbr(stage, "/World/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"/World/Looks/Sign{tag}",
                                diff=_tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"/World/Scene01/Sign_{tag}", cx, cy, bz,
                          yaw, panel, w=w, h=h, back_mtl=back)

    def build_cues(M):
        # 점자블록: 상단 모서리 0.3m 앞, 계단 폭, 깊이 0.3m
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            st = PARAMS["stairs"]
            x1 = st["x0"] - 0.0
            x0 = st["x0"] - tc["ahead"]
            cx = (x0 + x1) / 2.0
            cy = (st["y0"] + st["y1"]) / 2.0
            Ly = st["y1"] - st["y0"]
            # F4: 상판(z=0)에서 4mm 돌출·1cm 매입 (거의 플러시, 돌기는 노멀맵)
            z_top = 0.0 + tc["proud"]
            z_bot = 0.0 - 0.01
            add_box("/World/Scene01/Tactile", (cx, cy, (z_top + z_bot) / 2.0),
                    (tc["ahead"], Ly, z_top - z_bot), M["tactile"])

        # 핸드레일: 중앙 y=0 + 양측 y=±5.45. 계단 경사 따라 기운 상단 레일 +
        # 상단 1m 수평 연장 + 포스트(지름 4cm, 간격 ~1.2m, 높이 0.9m).
        if cfg["cue_railing"]:
            rl = PARAMS["railing"]
            st = PARAMS["stairs"]
            tread, riser, nsteps = st["tread"], st["riser"], st["nsteps"]
            run_x1 = tread * nsteps                   # 1.52
            drop = riser * nsteps                     # 0.6
            rail_h = rl["post_h"]                     # 0.9
            ext = rl["ext"]
            ang = math.degrees(math.atan2(drop, run_x1))   # 경사각(수평 대비)
            L = math.hypot(run_x1, drop)
            for j, y in enumerate(rl["y_lines"]):
                base = f"/World/Scene01/Rail_{j}"
                # 상단 수평 연장 레일 (x -ext→0, z=rail_h) — Cylinder Z축을 X로
                add_cylinder(f"{base}/RailExt", (-ext / 2.0, y, rail_h),
                             rl["rail_r"], ext, M["rail"], rotY=90.0)
                # 경사 레일: (0, rail_h) → (run_x1, rail_h-drop). rotateY로 기울임.
                add_cylinder(f"{base}/RailSlope",
                             (run_x1 / 2.0, y, rail_h - drop / 2.0),
                             rl["rail_r"], L, M["rail"], rotY=90.0 + ang)
                # R2-5: 중간 레일 — 상단 레일과 같은 기하를 z만 mid_drop만큼 낮춰 복제.
                mid_z = rail_h - rl["rail_mid_drop"]
                add_cylinder(f"{base}/RailExtMid", (-ext / 2.0, y, mid_z),
                             rl["rail_mid_r"], ext, M["rail"], rotY=90.0)
                add_cylinder(f"{base}/RailSlopeMid",
                             (run_x1 / 2.0, y, mid_z - drop / 2.0),
                             rl["rail_mid_r"], L, M["rail"], rotY=90.0 + ang)
                # 포스트: F6 — 실제 단 상면에 착지. 하단=디딤면, 상단=경사 레일.
                xp = -ext
                p = 0
                while xp <= run_x1 + 1e-6:
                    if xp <= 0:
                        gz = 0.0                       # 상부 광장/연장 구간
                    else:
                        step_idx = min(int(xp / tread), nsteps - 1)
                        gz = -riser * (step_idx + 1)   # 해당 디딤면 높이
                    railz = rail_h - drop * max(0.0, min(xp / run_x1, 1.0))
                    ph = railz - gz                    # 가변 높이 (레일과 디딤면 사이)
                    add_cylinder(f"{base}/Post_{p}", (xp, y, gz + ph / 2.0),
                                 rl["post_r"], ph, M["rail"])
                    xp += rl["spacing"]
                    p += 1

    # -------------------------------------------------------------------
    # setup_lighting (§5: DomeLight + noon HDRI lookfix + 보조 태양)
    # -------------------------------------------------------------------
    def setup_lighting():
        lp = PARAMS["light"]
        dome = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
        dome.CreateIntensityAttr(float(lp["dome_intensity"]))
        dome.CreateTextureFormatAttr("latlong")
        tex_attr = dome.CreateTextureFileAttr()
        hdri = os.path.join(ASSETS_DIR, lp["hdri"])
        hdri = _ensure_noon_lookfix(hdri)          # 태양 캡 + 지평 헤이즈 리프트
        print(f"[하늘] noon: {os.path.basename(hdri)} "
              f"(exists={os.path.isfile(hdri)})")
        tex_attr.Set(hdri)
        # RTX 돔은 Z-up 스테이지에서 극축 +Z로 올바름(rotateX 불필요)
        rot_op = UsdGeom.Xformable(dome.GetPrim()).AddRotateZOp()
        rot_op.Set(0.0)

        # HDRI 태양 방향에 정합한 명시적 DistantLight(0.53°) — 경질 그림자 담당
        sun = UsdLux.DistantLight.Define(stage, "/World/NoonSun")
        sun.CreateAngleAttr(0.53)
        sun.CreateIntensityAttr(float(lp["noon_sun_intensity"]))
        sun.CreateColorAttr(Gf.Vec3f(*[float(c) for c in lp["noon_sun_color"]]))
        sxf = UsdGeom.Xformable(sun.GetPrim())
        sun_rz = sxf.AddRotateZOp()
        sun_rz.Set(0.0)
        sxf.AddRotateXOp().Set(90.0 - float(lp["noon_sun_elev"]))
        if not lp["noon_sun_enable"]:
            UsdGeom.Imageable(sun.GetPrim()).MakeInvisible()

        def apply_dome_rot(user_off):
            # 돔 회전 = noon_dome_rot + SUN_AZ_OFFSET(사용자) + [ ]키 오프셋
            rot = (float(lp["noon_dome_rot"]) + float(PARAMS["SUN_AZ_OFFSET"])
                   + float(user_off))
            rot_op.Set(rot)
            # 보조 태양은 돔과 함께 회전 (그림자 방위 일치)
            sun_rz.Set(rot + float(lp["hdri_sun_rotz_offset"]))

        apply_dome_rot(0.0)
        return apply_dome_rot

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_upper_plaza(M)
    if cfg["hazard_stairs"]:
        build_stairs(M)
        build_lower_plaza(M)
        build_flank_walls(M)        # F7: 계단 있을 때만 (측벽 상면 z=0)
        build_south_apron(M)        # v4-A1: 남측 구덩이 메움 (평지 대조군엔 불필요)
    else:
        build_flat_fill(M)          # 대조군: z=0 평지 통일
        # F7: 측벽 상면(z=0)이 FlatFill 상면(z=0)과 동일평면 → Z파이팅.
        #     평지 대조군에는 측벽이 무의미하므로 스킵.
    build_surroundings(M)           # F3: 부지 바깥 지면 (상시 생성)
    if cfg["cue_scene_dressing"]:
        build_amphitheater(M)
        build_planters(M)
        build_buildings(M)
        build_streetlight(M)
        build_dressing_props(M)     # v4-D: 캠퍼스 맥락단서 일괄
    build_cues(M)
    if cfg["cue_sign"]:
        build_signs()               # [v5 공통 레이어]
    apply_dome_rot = setup_lighting()

    # ── §6 카메라 + 렌더 모드 ──
    def look_from(eye, pitch_deg=None, target=None):
        if target is None:
            p = math.radians(pitch_deg)
            target = [eye[0] + 5.0 * math.cos(p), eye[1],
                      eye[2] + 5.0 * math.sin(p)]
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in target])

    _v0 = build_views()["beauty_overview"]
    look_from(_v0["eye"], target=_v0["tgt"])       # 시작 카메라 = 미장센

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

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    # ===================================================================
    # 자동 캡처 모드 (headless 검증 파이프라인 — noon 전용)
    # ===================================================================
    if capture_mode:
        # [사실화 v1] 자체 캡처 블록 → `scene_common.capture_pipeline` 위임.
        # 이 블록이 바로 capture_pipeline 의 원본이었고(여기서 추출됨), 이후
        # 나머지 32씬은 공용 함수를 쓰는데 scene01 만 사본을 유지해 갈라져 있었다.
        # 그 결과 PT 가속(NEGOBS_PT_FAST)·룩 레이어 계측 리포트 같은 공용 계층
        # 개선이 scene01 에만 적용되지 않았다.
        sc.capture_pipeline(
            simulation_app, build_views(),
            os.path.join(LOOKCHECK_DIR, "auto"),
            set_render_mode,
            lambda eye, tgt: look_from(eye, target=tgt))
        simulation_app.close()
        return

    # ===================================================================
    # GUI 룩 체크 모드 (기본)
    # ===================================================================
    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]                           # [ / ] 키 사용자 오프셋

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene01_{ts}.png")
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
