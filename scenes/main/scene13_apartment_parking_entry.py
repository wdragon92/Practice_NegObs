# -*- coding: utf-8 -*-
"""
scene13_apartment_parking_entry.py — NegObs 인공씬 13호 (v5.1 R8):
아파트 단지 지하주차장 진입부 (Isaac Sim 4.5)

유형    : T10 계열 재정의 — 나선 주차램프(구 scene13, archive_v3)를 폐기하고
          **직선 지하주차장 진입 램프 + 병설 보행계단**으로 교체.
사양서  : Docs/audit_v4/user_feedback_v5_1.md §씬별 지시 13행(R8),
          Docs/briefs/multi_scene_brief_v5.md(파일 구조·공통 레이어)
공통    : scene_common.py (build_slope/build_straight_stairs/build_rot_group/
          build_canopy/build_planter/build_tree/build_building/build_sign/
          build_tactile/build_bollard) · scene16(최신 파일 구조) 준거

[v5.1] 교체 사유 (사용자 총평: "너무 시뮬레이션 티가 난다 — 현실성 기반")
  구 scene13 은 지상에 홀로 선 나선 주차램프였다. 실제로 그런 구조물이 단독으로
  서 있는 단지는 없다. 한국 아파트 단지에서 "차량이 지면 아래로 사라지는 곳"은
  거의 예외 없이 **지하주차장 직선 진입 램프**다 → 범용성(어느 단지에나 있음)과
  현실성(치수·설비가 법규로 고정)을 동시에 얻는다.

위험 본질
  단지 보도(z=0)를 걷다 보면 폭 6 m 의 램프 개구가 지면을 절개하고 있다.
  램프는 완화구간 8.5% → 본선 17% → 완화 8.5% 로 3.96 m 내려가는데,
  **로봇 눈높이(h0.3)에서는 이 하강이 원리적으로 소실된다**: 근측 연단(x=0)
  에서 거리 d 로 물러난 시선이 노면을 스치는 각도(atan(0.3/d))가 램프 초기
  경사각(4.86°)보다 작아지는 d ≥ 3.5 m 부터, 램프 노면은 화면에서 지면과
  같은 밝기·같은 재질의 평면으로 압축된다. 게다가 x ≥ 24 m 구간은 상부
  슬래브(지상 조경)로 덮여 **개구 너머 지반(z=0)이 근측 보도와 연속**으로
  읽힌다 → 전형적 negative obstacle.
  방호는 "규정 미달의 현실": 램프 개구 둘레 난간은 남측 x 10.5~13.5 구간이
  철거되어 있고(3 m), 병설 계단 샤프트(깊이 3.96)는 무난간 코핑만 남는다.

목표
  ① 램프 트렌치 개구(x 0..24, y ±3.3)와 계단 샤프트 개구(x 5..11.2,
     y 3.3..6.9)를 **덮지 않는** 지반 6박스 분할
  ② 직선 램프 3세그(완화-본선-완화) + 측벽·코핑 + 상부 캐노피 + 차단기 +
     높이제한바 + 요금 안내판
  ③ 병설 보행계단 24단(riser 0.165, 폭 1.4, 되돌음 2련 + 중간참) → 지하 복도
     → 지하 1층 주차장(약발광 조명 — PT 전제)
  ④ 규정 볼라드(h0.9·r0.08·간격 1.5·상단 반사띠) + 전면 0.3 m 점형블록 —
     **보도-램프 접점(횡단 지점)에만**
  ⑤ 단지 드레싱: 인터로킹 보도·조경 화단·수목(build_tree v2)·생울타리·
     아파트 3동(base_z·창 인셋)

보행 연속성 자가 검증표 (지상 → 계단 → 지하 → 램프 → 지상; 단차 ≤ 0.165)
  ┌ #  구간               좌표(x, y, z)              단차/판정
  │ 0  단지 북측 보도      (13.0,  8.20,  0.000)      평탄(인터로킹)
  │ 1  계단 지선 보도      (12.4,  5.50,  0.000)      평탄
  │ 2  점형블록 경고띠     (11.65, 4.25,  0.004)      0.004 (cue_tactile)
  │ 3  계단 머리(개구 연단)(11.20, 4.25,  0.000)      ← **낙차 3.96 무난간**
  │ 4  1단 디딤            (11.05, 4.25, -0.165)      0.165
  │ 5  12단 디딤           ( 7.75, 4.25, -1.980)      0.165 × 11
  │ 6  중간참(180° 반전)   ( 6.40, 5.10, -1.980)      평탄 (x 5.25..7.6)
  │ 7  13단 디딤           ( 7.75, 5.95, -2.145)      0.165
  │ 8  24단 디딤           (11.05, 5.95, -3.960)      0.165 × 11
  │ 9  지하 복도           (12.00, 5.95, -3.960)      평탄 (유효고 2.76)
  │10  주차장 진입         (24.50, 5.95, -3.960)      평탄
  │11  램프 하단 합류      (26.89, 0.00, -3.960)      평탄
  │12  램프 본선 상행      (23.29, 0.00, -3.654)      경사 8.5%
  │13  램프 완화 상단      ( 3.60, 0.00, -0.306)      경사 17%
  └14  지상 차로 복귀      ( 0.00, 0.00,  0.000)      경사 8.5% → 평탄
  * 계단 낙차(24 × 0.165 = 3.96) = 램프 낙차 → 두 경로가 같은 지하 1층 바닥
    (-3.96)에 착지한다(스모크에서 자동 검산).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene13_apartment_parking_entry.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python scene13_apartment_parking_entry.py
스모크(부팅 없음):      NEGOBS_SMOKE=1  python scene13_apartment_parking_entry.py

좌표계: Z-up, m, 진행축 +X(단지 보도 → 램프 하강). **낙차 시작 모서리 x=0.**
  지상 z=0, 지하 1층 바닥 z=-3.96, 상부 슬래브 밑면 z=-1.2.
  태양: SUN_AZ_OFFSET=171.5 (전 씬 기본 — 캐노피 그림자가 개구 상단에 걸린다).
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hazard_stairs 만 기하 토글(개구 → 평지 메움).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 램프·계단·지하를 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        True,   # 램프 개구 둘레 난간(남측 3 m 철거 결손 상시) + 샤프트 둘레
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)   # [v5 공통] 도시 관행 — 볼라드 전면·계단 상하부 점형블록
    "cue_material_break": True,   # 보도 인터로킹 vs 램프·계단 콘크리트. False → 전부 보도재
    "cue_sign":           True,   # [v5.2 사용자] 임의 경고 팻말 제거 — 요금 안내판(sign_info)만
    "cue_scene_dressing": True,   # 화단·수목·생울타리·벤치·가로등·아파트 3동
    "cue_nosing":         False,  # True → 계단 단코 논슬립 띠(지하 계단은 관행상 약함)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
_RISER = 0.165
_NSTEP = 24                        # 12단 × 2련 (되돌음)
_DROP = round(_RISER * _NSTEP, 4)  # 3.96 = 지하 1층 바닥
_FLOOR_Z = -_DROP

PARAMS = dict(
    # --- 램프 (직선, 폭 6) : 완화 3.6@8.5% → 본선 @17% → 완화 3.6@8.5% ---
    #     주차장법 시행규칙 별표: 직선 경사로 종단경사 17% 이하, 2차로 폭 6 m 이상,
    #     경사로 상·하단 완화구간(경사 1/2 · 길이 3.6 m) — 전부 실측 관행값.
    ramp=dict(y0=-3.0, y1=3.0, drop=_DROP, thick=0.6,
              trans_run=3.6, trans_grade=0.085, main_grade=0.17,
              seg_margin=0.10),
    # --- 트렌치 측벽(옹벽) + 상단 코핑 ---
    wall=dict(thick=0.3, z_bot=-4.4, z_top=0.0,
              cope_over=0.06, cope_h=0.12),
    # --- 지하 구조체: 상부 슬래브 밑면 = 지반 플레이트 저면(-1.2) ---
    #     포털(지상 개구 동단) x=24.0 → 그 지점 램프 노면 -3.714 → 유효고 2.514
    #     (표기 높이제한 2.3 < 실제 — 현실의 여유 관행)
    portal=dict(x=24.0, head_clear=2.3),
    garage=dict(x0=24.0, x1=38.0, y0=-9.3, y1=9.3, floor_z=_FLOOR_Z,
                floor_thick=0.8, wall_t=0.3, ceil_z=-1.2),
    # --- 병설 보행계단(되돌음 2련) : 샤프트 x 5.0..11.2, y 3.3..6.9 ---
    stair=dict(riser=_RISER, tread=0.30, n_flight=12, width=1.4,
               x_head=11.2, x_turn=7.6, land_x0=5.25,
               y_a0=3.55, y_a1=4.95,          # 1련(하행 -X)
               y_b0=5.25, y_b1=6.65,          # 2련(하행 +X)
               mid_z=-1.98, base_z=-4.4),
    shaft=dict(x0=5.0, x1=11.2, y0=3.3, y1=6.9, wall_t=0.25),
    # --- 지하 복도(계단 → 주차장) ---
    corridor=dict(x0=11.2, x1=24.0, y0=5.25, y1=6.65, wall_t=0.25,
                  floor_z=_FLOOR_Z, floor_thick=0.6, ceil_z=-1.2),
    # --- 지반(단지 지상) : 개구 2곳을 비운 6박스 ---
    ground=dict(x0=-34.0, x1=46.0, y0=-26.0, y1=26.0, z_top=0.0, thick=1.2),
    # --- 포장 오버레이 (지반 위 proud) ---
    drive=dict(x0=-14.0, x1=0.0, flare_x0=-6.0, flare_y=4.2, proud=0.004),
    walk_cross=dict(x0=-3.2, x1=-1.2, y_far=16.0, proud=0.007),   # 램프 횡단 보도
    walk_north=dict(y0=7.2, y1=9.2, x0=-14.0, x1=30.0, proud=0.007),
    walk_spur=dict(x0=11.4, x1=13.4, y0=3.3, y1=7.2, proud=0.007),
    walk_south=dict(y0=-9.4, y1=-7.4, x0=-14.0, x1=30.0, proud=0.007),
    # --- 규정 볼라드 (교통약자법 시행규칙 별표2 준거) ---
    #     h0.9 · r0.08 · 간격 1.5 · 상단 반사띠 · 전면 0.3 m 점형블록.
    #     배치는 **차량 진입 우려 지점만** = 보도가 차로를 횡단하는 접점 2곳.
    bollard=dict(h=0.9, r=0.08, gap=1.5, band_h=0.09, band_z=0.74,
                 band_r=0.086),
    bollard_rows=[dict(y=4.35, xs=(-2.9, -1.4), tac_y0=4.35, tac_y1=4.65),
                  dict(y=-4.35, xs=(-2.9, -1.4), tac_y0=-4.65, tac_y1=-4.35)],
    # --- 캐노피(진입부 상옥) + 높이제한바 + 차단기 ---
    canopy=dict(x0=-1.6, x1=4.2, y0=-3.75, y1=3.75, z_roof=2.85,
                roof_t=0.35, post_r=0.16, base_z=0.0,
                # [v6 C-3] 처마(페시아) 띠 : 슬래브 외주를 감싸고 소핏 아래로
                #   drop 만큼 내려와 "판때기"가 아니라 두께 있는 상옥으로 읽힌다.
                fas_ov=0.09, fas_in=0.02, fas_drop=0.07, fas_top_in=0.02,
                # 하면 조명 3개소 (지하 진입부 관행 — PT 8바운스 전제 약발광)
                soffit_xs=(0.0, 1.4, 2.8), soffit=(0.90, 0.22, 0.06),
                soffit_drop=0.01),
    height_bar=dict(x=-1.5, z=2.30, r=0.09, y0=-3.2, y1=3.2, nseg=8,
                    hanger_t=0.05),
    gate=dict(x=2.2, y=3.15, box=(0.34, 0.30, 1.00), base_z=0.12,
              arm_r=0.05, arm_z=0.97, arm_y0=-2.6, arm_y1=3.0, nseg=7),
    # --- 사인 (cue_sign) ---
    sign_info=dict(cx=-1.1, cy=4.75, yaw=170.0, w=0.9, h=0.7, pole_h=2.2),
    # [v5.2 사용자] 임의 경고 팻말 제거 — 계단주의 사인(sign_step) 삭제.
    # --- 난간 (cue_railing) : 개구 둘레 코핑 **위**에 착지(base_z = 코핑 상면).
    #     남측은 x 10.5~13.5 가 철거되어 있다(규정 미달의 현실).
    #     c 값은 코핑 중심선 = 옹벽 중심선(트렌치 ±3.15 / 샤프트 북 6.775 · 서 5.125)
    rail=dict(h=0.95, post_r=0.03, rail_r=0.028, mid_r=0.018, mid_h=0.46,
              spacing=1.45, base_z=0.12),
    rail_runs=[dict(axis="x", c=-3.15, a0=0.0,  a1=10.5),
               dict(axis="x", c=-3.15, a0=13.5, a1=24.0),   # ← 10.5~13.5 결손
               dict(axis="x", c=3.15,  a0=3.2,  a1=5.0),    # 차단기 함체 동측부터
               dict(axis="x", c=3.15,  a0=11.2, a1=24.0),
               dict(axis="x", c=6.775, a0=5.0,  a1=11.2),
               dict(axis="y", c=5.125, a0=3.3,  a1=6.9)],
    # --- 점자블록 (cue_tactile) ---
    tactile=dict(depth=0.30, proud=0.004,
                 head_x0=11.5, head_x1=11.8,        # 계단 머리 경고띠
                 foot_x0=11.25, foot_x1=11.55),     # 지하 착지 경고띠
    # --- 드레싱 (배치 비정형: 등간격·격자 금지, yaw 지터) ---
    planters=[dict(cx=-8.6, cy=6.4, size=3.4, tree=True),
              dict(cx=-12.9, cy=-5.2, size=2.8, tree=True),
              dict(cx=16.8, cy=10.9, size=3.8, tree=True),
              dict(cx=4.3, cy=-8.9, size=3.0, tree=True),
              dict(cx=27.4, cy=-6.1, size=3.2, tree=False)],
    planter=dict(curb_h=0.42, curb_t=0.22, cap_over=0.05, cap_h=0.05,
                 grass_h=0.38),
    trees=[(-19.4, 8.9), (-16.1, -9.7), (9.2, 12.4), (21.7, 6.8),
           (-5.8, -12.3), (30.6, 12.1), (18.4, -11.6), (-24.7, 3.4)],
    hedges=[(-22.0, 6.9, -14.6, 7.5), (14.2, -7.6, 21.3, -7.0),
            (2.4, 12.2, 9.6, 12.8)],
    benches=[(-9.4, 8.3, 174.0), (17.3, 12.6, -6.0), (-13.6, -7.1, 3.0)],
    streetlights=[(-7.2, 6.95), (12.6, 7.05), (26.9, -7.2)],
    streetlight=dict(pole_h=5.2, pole_r=0.075, arm_len=1.0, arm_r=0.045,
                     head=0.26),
    # 아파트 3동 — 파사드 인셋 창(build_building). base_z=0 (지상 기단)
    buildings=dict(
        A101=dict(x0=34.0, x1=46.0, y0=-15.0, y1=7.4, h=45.0, floors=15,
                  axis="x", facade_x=34.0, face_dir=-1.0, base_z=0.0),
        A102=dict(x0=30.5, x1=42.0, y0=13.6, y1=25.0, h=39.0, floors=13,
                  axis="x", facade_x=30.5, face_dir=-1.0, base_z=0.0),
        A103=dict(x0=-46.0, x1=-34.0, y0=-20.0, y1=11.5, h=42.0, floors=14,
                  axis="x", facade_x=-34.0, face_dir=1.0, base_z=0.0),
    ),
    window=dict(w=1.3, h=1.5, inset=0.15, col_step=2.7, margin=2.2),
    # 지하 주차장 내부 (약발광 — PT 전제)
    garage_cols=[(27.5, -5.6), (27.5, 2.4), (32.4, -5.6), (32.4, 2.4),
                 (35.8, 6.2)],
    garage_col=dict(size=0.55),
    garage_lights=[(26.0, 0.0), (30.5, 4.4), (34.5, -3.2), (30.0, -7.4)],
    corridor_lights=[(14.0, 5.95), (18.5, 5.95), (22.5, 5.95)],
    garage_lamp=dict(size=(1.2, 0.24, 0.06), z=-1.28),
    park_lines=[(26.6, -8.4), (29.3, -8.4), (32.0, -8.4), (34.7, -8.4)],
    park_line=dict(w=0.12, len=5.0, z_off=0.006),

    material=dict(
        scale=dict(paving_interlock=1.2, concrete_floor=1.0,
                   concrete_wall=1.4, grass=1.4, tactile=0.3, plaster=2.4),
        grass_tint=(0.52, 0.63, 0.40),
        grass_tint_b=(0.47, 0.60, 0.37),        # 화단 잔디(±5% 틴트 지터)
        paving_tint=(0.86, 0.85, 0.83),
        conc_tint=(0.80, 0.79, 0.77),
        wall_tint=(0.74, 0.73, 0.71),
        wall_tint_b=(0.70, 0.70, 0.69),
        # [v6 판정 ⑤] 아스팔트 = 무텍스처 짙은 남청색 판(화면 40~60 % 점유) →
        #   **골재 텍스처(gravel diff/nor/rough) + 중성 회흑 틴트**.
        #   gravel diff 평균 ≈0.45 × tint 0.21 ≈ 0.095 (sRGB 규약대 상단),
        #   청기 제거를 위해 B 를 R 보다 낮춘다(구 색은 B > R = 남청 원인).
        asphalt_color=(0.135, 0.135, 0.145), asphalt_rough=0.88,  # (미사용 보존)
        asphalt_tint=(0.215, 0.210, 0.198), asphalt_scale=0.35,
        # 타이어 폴리시 밴드 — 윤적부 마모로 골재가 눌려 어둡고 매끈해진 띠
        polish_color=(0.048, 0.047, 0.044), polish_rough=0.46,
        paint_color=(0.70, 0.70, 0.66), paint_rough=0.62,   # 순백 금지(<0.8)
        rail_color=(0.66, 0.68, 0.70), rail_metallic=0.7, rail_rough=0.42,
        bollard_color=(0.30, 0.31, 0.33), bollard_metallic=0.4,
        bollard_rough=0.5,
        band_color=(0.72, 0.72, 0.70), band_rough=0.35,     # 반사띠(순백 미만)
        cope_color=(0.62, 0.62, 0.60), cope_rough=0.65,
        wood_color=(0.28, 0.19, 0.12), wood_rough=0.85,
        glass_color=(0.055, 0.075, 0.10), glass_rough=0.08,
        parapet_color=(0.60, 0.60, 0.58), parapet_rough=0.62,
        shell_tint=(0.86, 0.84, 0.80), shell_tint_b=(0.80, 0.79, 0.78),
        # [v6 C-3] 캐노피 슬래브 = 6×5 m 무텍스처 백판(스티로폼 카포트) →
        #   콘크리트 텍스처 + 처마(페시아) 띠 + 하면 조명.
        roof_color=(0.42, 0.42, 0.44), roof_rough=0.60,   # (미사용 보존)
        roof_tint=(0.78, 0.77, 0.75), roof_scale=1.6,
        fascia_tint=(0.60, 0.60, 0.58), fascia_scale=0.8,
        post_color=(0.36, 0.36, 0.38), post_metallic=0.35, post_rough=0.5,
        lamp_color=(0.78, 0.78, 0.74), lamp_rough=0.4,
        # 어두운 상수색 (sRGB 알베도 0.02~0.06 규약)
        dark_color=(0.035, 0.035, 0.040), dark_rough=0.7,
        warn_y=(0.72, 0.58, 0.06), warn_r=(0.52, 0.10, 0.09),
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # 지하 약발광 (PT 8바운스 전제 — RT 기여 미미)
        emit_color=(0.85, 0.87, 0.80), emit_intensity=340.0,
        sign_back_color=(0.05, 0.05, 0.055), sign_back_rough=0.5,
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
# [C] 경로 상수 + 필요 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene13")

ASSET_ROLES = ["paving_interlock", "concrete_floor", "concrete_wall",
               "grass", "tactile", "plaster",
               "gravel",                     # [v6 ⑤] 아스팔트 골재 텍스처
               "sign_info", "hdri", "mdl"]   # [v5.2 사용자] 임의 경고 팻말 제거


# ===========================================================================
# [C2] 램프 종단 프로파일 — 완화 / 본선 / 완화 (전 함수 공용 단일 진실원)
# ===========================================================================
def ramp_profile():
    """반환: (segs, total_run)
      segs = [(x0, z0, run, drop), ...]  — build_slope 인자와 동일 규약
      (z0 = 세그 상단 노면 z, drop 만큼 +X 로 하강)"""
    rp = PARAMS["ramp"]
    t_run = float(rp["trans_run"])
    t_drop = t_run * float(rp["trans_grade"])
    main_drop = float(rp["drop"]) - 2.0 * t_drop
    main_run = main_drop / float(rp["main_grade"])
    segs = [(0.0, 0.0, t_run, t_drop),
            (t_run, -t_drop, main_run, main_drop),
            (t_run + main_run, -(t_drop + main_drop), t_run, t_drop)]
    return segs, 2.0 * t_run + main_run


def ramp_z(x):
    """램프 노면 z(x). 개구 밖(x<0)은 0, 하단 이후는 바닥."""
    segs, total = ramp_profile()
    if x <= 0.0:
        return 0.0
    if x >= total:
        return -float(PARAMS["ramp"]["drop"])
    for x0, z0, run, drop in segs:
        if x <= x0 + run + 1e-9:
            return z0 - drop * (x - x0) / run
    return -float(PARAMS["ramp"]["drop"])


# ===========================================================================
# [C3] 스모크 — 부팅 전 기하 자기검증 (조기종료)
# ===========================================================================
def _smoke_report():
    rp = PARAMS["ramp"]
    st = PARAMS["stair"]
    sh = PARAMS["shaft"]
    gr = PARAMS["ground"]
    ga = PARAMS["garage"]
    co = PARAMS["corridor"]
    po = PARAMS["portal"]
    segs, total_run = ramp_profile()

    print("=" * 72)
    print("scene13_apartment_parking_entry — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 72)

    # ── 램프 종단 ──
    print("  [램프 종단 프로파일]  폭 "
          f"{rp['y1'] - rp['y0']:.1f} m (2차로 규정 6 m 이상)")
    for i, (x0, z0, run, drop) in enumerate(segs, 1):
        print(f"    seg{i}: x {x0:6.3f} → {x0 + run:6.3f}  z {z0:+.3f} → "
              f"{z0 - drop:+.3f}  경사 {drop / run * 100:5.2f}%")
    tot_drop = sum(s[3] for s in segs)
    print(f"    총 run {total_run:.3f} m · 총 낙차 {tot_drop:.3f} m · "
          f"최대 경사 {max(s[3] / s[2] for s in segs) * 100:.1f}% ≤ 17% → "
          f"{'OK' if max(s[3] / s[2] for s in segs) <= 0.1701 else 'FAIL'}")
    print(f"    낙차 검증: {tot_drop:.3f} ≥ 0.3 m → "
          f"{'OK' if tot_drop >= 0.3 else 'FAIL'}")

    # ── 대비쌍: 계단 낙차 = 램프 낙차 ──
    sdrop = st["riser"] * st["n_flight"] * 2
    print("  [계단 ↔ 램프 낙차 정합]")
    print(f"    계단 {st['n_flight'] * 2}단 × riser {st['riser']} = "
          f"{sdrop:.3f} · 램프 {tot_drop:.3f} → "
          f"{'OK' if abs(sdrop - tot_drop) < 1e-6 else 'FAIL'} "
          f"(두 경로가 같은 지하 1층 바닥에 착지)")
    run_f = st["n_flight"] * st["tread"]
    print(f"    1련 run {run_f:.2f} m · 되돌음 참 x "
          f"[{st['land_x0']:.2f},{st['x_turn']:.2f}] "
          f"= {st['x_turn'] - st['land_x0']:.2f} m ≥ 1.2 → "
          f"{'OK' if st['x_turn'] - st['land_x0'] >= 1.2 else 'FAIL'}")
    print(f"    1련 상단 x {st['x_head']:.2f} → 하단 x "
          f"{st['x_head'] - run_f:.2f} (= 참 동단 {st['x_turn']:.2f}) → "
          f"{'OK' if abs(st['x_head'] - run_f - st['x_turn']) < 1e-6 else 'FAIL'}")

    # ── 유효고(높이제한) ──
    z_portal = ramp_z(po["x"])
    clear = ga["ceil_z"] - z_portal
    print("  [지하 진입 유효고]")
    print(f"    포털 x={po['x']:.1f} 노면 z {z_portal:+.3f} · 슬래브 밑면 "
          f"{ga['ceil_z']:+.2f} → 유효고 {clear:.3f} m "
          f"(표기 높이제한 {po['head_clear']:.1f}) → "
          f"{'OK' if clear >= po['head_clear'] else 'FAIL'}")
    print(f"    지하 복도 유효고 {ga['ceil_z'] - co['floor_z']:.2f} m ≥ 2.1 → "
          f"{'OK' if ga['ceil_z'] - co['floor_z'] >= 2.1 else 'FAIL'}")

    # ── 지반 플레이트 표: 개구를 덮는 평면이 없는지 ──
    x_p = po["x"]
    plates = [
        ("Ground_W(grass)", gr["x0"], 0.0, gr["y0"], gr["y1"]),
        ("Ground_S(grass)", 0.0, x_p, gr["y0"], -3.3),
        ("Ground_N1(grass)", 0.0, sh["x0"], 3.3, gr["y1"]),
        ("Ground_N2(grass)", sh["x1"], x_p, 3.3, gr["y1"]),
        ("Ground_N3(grass)", sh["x0"], sh["x1"], sh["y1"], gr["y1"]),
        ("Ground_E(grass)", x_p, gr["x1"], gr["y0"], gr["y1"]),
    ]
    opens = [("램프 트렌치", 0.0, x_p, -3.3, 3.3),
             ("계단 샤프트", sh["x0"], sh["x1"], sh["y0"], sh["y1"])]
    print("  [지반 플레이트 표] (개구 2곳을 비운 6박스 · 상면 z=0 · 두께 "
          f"{gr['thick']:.1f})")
    print(f"    {'이름':20s} {'x범위':>16s} {'y범위':>16s}")
    bad = []
    for nm, x0, x1, y0, y1 in plates:
        print(f"    {nm:20s} [{x0:6.1f},{x1:6.1f}] [{y0:6.1f},{y1:6.1f}]")
        for onm, ox0, ox1, oy0, oy1 in opens:
            if not (x1 <= ox0 + 1e-9 or x0 >= ox1 - 1e-9 or
                    y1 <= oy0 + 1e-9 or y0 >= oy1 - 1e-9):
                bad.append(f"{nm}∩{onm}")
    print(f"    개구 위를 덮는 플레이트: {bad if bad else '없음 → OK'}")

    # ── h0.3 grazing 은닉 검산 (연구 핵심) ──
    print("  [h0.3/h0.9 grazing 은닉 검산] 연단(x=0,z=0) 스치는 시선 vs 노면")
    ang_ramp = math.degrees(math.atan(rp["trans_grade"]))
    for h in (0.3, 0.9):
        for d in (2.0, 5.0, 10.0):
            ang_eye = math.degrees(math.atan(h / d))
            hid = ang_eye <= ang_ramp
            print(f"    h{h:.1f} d{d:4.1f} → 시선 부각 {ang_eye:5.2f}° vs "
                  f"램프 초기 경사 {ang_ramp:.2f}° → "
                  f"{'은닉(노면 평면 압축)' if hid else '노면 일부 노출'}")
    print(f"    ⇒ 개구 너머 지반(x ≥ {x_p:.0f}, z=0)은 상부 슬래브 위 조경이라"
          f" 근측 보도와 **연속 평면**으로 읽힌다(negative obstacle 성립).")

    # ── 규정 볼라드 검산 ──
    bo = PARAMS["bollard"]
    print("  [규정 볼라드] (교통약자법 시행규칙 별표2)")
    for i, row in enumerate(PARAMS["bollard_rows"]):
        xs = row["xs"]
        gaps = [round(abs(xs[k + 1] - xs[k]), 2) for k in range(len(xs) - 1)]
        print(f"    row{i}: y={row['y']:+.2f} · {len(xs)}본 · 간격 {gaps} "
              f"· 점형블록 y [{row['tac_y0']:+.2f},{row['tac_y1']:+.2f}] "
              f"(깊이 {abs(row['tac_y1'] - row['tac_y0']):.2f})")
    print(f"    h {bo['h']:.2f}(0.8~1.0) · 지름 {2 * bo['r']:.2f}(0.1~0.2) · "
          f"간격 {bo['gap']:.1f} 내외 · 상단 반사띠 z {bo['band_z']:.2f} → "
          f"{'OK' if 0.8 <= bo['h'] <= 1.0 and 0.1 <= 2 * bo['r'] <= 0.2 else 'FAIL'}")

    # ── 난간 결손(규정 미달의 현실) ──
    runs = [r for r in PARAMS["rail_runs"] if r["axis"] == "x"
            and abs(r["c"] + 3.15) < 1e-6]
    if len(runs) >= 2:
        gap = runs[1]["a0"] - runs[0]["a1"]
        print("  [난간 결손]")
        print(f"    남측 개구 난간: x [0,{runs[0]['a1']:.1f}] + "
              f"[{runs[1]['a0']:.1f},{runs[1]['a1']:.1f}] → 결손 {gap:.1f} m "
              f"(x {runs[0]['a1']:.1f}~{runs[1]['a0']:.1f}) — 그 지점 낙차 "
              f"{-ramp_z((runs[0]['a1'] + runs[1]['a0']) / 2.0):.2f} m 무방호")
    # ── [v6 판정 ⑤ / C-3] 재질 수정 검산 (기하·GT 불변 확인) ──
    mp_ = PARAMS["material"]
    dr_ = PARAMS["drive"]
    cp_ = PARAMS["canopy"]
    print("  [v6 재질 수정 검산] — 아스팔트·캐노피 (치수 불변)")
    print(f"    아스팔트 : gravel diff/nor/rough · scale "
          f"{mp_['asphalt_scale']:.2f} m · 틴트 {mp_['asphalt_tint']} → "
          f"청기 {'제거 OK' if mp_['asphalt_tint'][2] < mp_['asphalt_tint'][0] else 'FAIL(B>R)'}"
          f" (구 상수색 {mp_['asphalt_color']} = B>R 남청)")
    print(f"    폴리시 밴드 : 중심선 ±0.85 · 폭 0.55 · x "
          f"[{dr_['x0']:.1f},{dr_['x1']:.1f}] · 상면 돌출 4 mm "
          f"(저면 매입 → Z파이팅 없음)")
    print(f"    캐노피 : 지붕 콘크리트 텍스처(scale {mp_['roof_scale']:.1f}) + "
          f"처마 띠(돌출 {cp_['fas_ov']*100:.0f} cm, 소핏 아래 "
          f"{cp_['fas_drop']*100:.0f} cm) + 하면 조명 {len(cp_['soffit_xs'])}개소")
    print(f"      슬래브 {cp_['x1']-cp_['x0']:.1f}×{cp_['y1']-cp_['y0']:.1f} m · "
          f"밑면 z {cp_['z_roof']:.2f} · 두께 {cp_['roof_t']:.2f} → 치수 불변 · "
          f"높이제한바 z {PARAMS['height_bar']['z']:.2f} 간섭 없음")
    print("=" * 72)


# ===========================================================================
# [D] 카메라 프리셋
# ===========================================================================
def build_views():
    """grid_views(gy=0.0 — 차로 중심축) + 미장센 6컷."""
    views = sc.grid_views(0.0)
    # entry_approach: 차량 시점 진입 (캐노피·높이제한바·차단기·개구)
    views["entry_approach"] = dict(eye=[-12.0, 0.0, 1.55], tgt=[2.0, 0.0, -0.5])
    # ramp_graze: 보행 눈높이 grazing — 램프 하강이 평면으로 압축되는가
    views["ramp_graze"] = dict(eye=[-6.0, 0.0, 0.90], tgt=[8.0, 0.0, -0.55])
    # bollard_walk: 북측 보도에서 남하 — 규정 볼라드 열 + 점형블록 + 접점
    views["bollard_walk"] = dict(eye=[-2.2, 11.0, 1.50], tgt=[-2.2, 1.5, 0.15])
    # stair_head: 계단 머리에서 되돌음 2련·중간참 내려봄
    views["stair_head"] = dict(eye=[13.6, 4.30, 1.60], tgt=[6.6, 4.90, -2.20])
    # portal_look: 램프 중턱에서 지하 포털(약발광 주차장) 조망
    views["portal_look"] = dict(eye=[13.0, 0.0, -0.95], tgt=[27.0, 0.5, -3.20])
    # beauty_overview: 단지 사선 부감 (램프·계단·동·조경 일괄)
    views["beauty_overview"] = dict(eye=[-17.0, -15.0, 12.0],
                                    tgt=[9.0, 3.0, -1.2])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. entry_approach   — 캐노피·높이제한바·차단기·요금 안내판이 진입부로 읽히는가
 2. ramp_graze·h0.3  — 램프 하강이 평면으로 압축되고 개구 너머가 연속되는가(특색)
 3. bollard_walk     — 볼라드 h0.9·간격1.5·반사띠 + 전면 0.3 m 점형블록(규정)
 4. stair_head       — 되돌음 2련·중간참·무난간 코핑(규정 미달의 현실)
 5. portal_look      — 포털 유효고·지하 약발광(PT 필수, RT 는 새까맣게 나옴)
 6. beauty_overview  — 아파트 3동·조경 화단·수목 v2 배치가 비정형인가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene13")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene13"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # 재질 — 인스턴스 변주용 틴트 지터 변종(±5%) 포함
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["paving"] = PBR(
            f"{ROOT}/Looks/Paving", sc.tex_path("paving_interlock", "diff"),
            sc.tex_path("paving_interlock", "nor"),
            sc.tex_path("paving_interlock", "rough"),
            sca["paving_interlock"], tint=mp["paving_tint"])
        M["conc"] = PBR(
            f"{ROOT}/Looks/Concrete", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["conc_tint"])
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["wall_tint"])
        M["wall_b"] = PBR(
            f"{ROOT}/Looks/WallB", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["wall_tint_b"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["grass_b"] = PBR(
            f"{ROOT}/Looks/GrassB", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint_b"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        M["shell"] = PBR(
            f"{ROOT}/Looks/Shell", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["plaster"], tint=mp["shell_tint"])
        M["shell_b"] = PBR(
            f"{ROOT}/Looks/ShellB", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["plaster"], tint=mp["shell_tint_b"])
        # [v6 ⑤] 아스팔트 : 상수색 → 골재 텍스처 + 중성 회흑 틴트.
        #   scale 0.35 m = 골재 패치가 화면에 촘촘히 남는 크기(구 상수색은
        #   h0.3 컷 40~60 %를 정보 0 영역으로 만들었다).
        M["asphalt"] = PBR(
            f"{ROOT}/Looks/Asphalt", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            mp["asphalt_scale"], tint=mp["asphalt_tint"])
        M["polish"] = PBR(f"{ROOT}/Looks/Polish",
                          diffuse_color=mp["polish_color"],
                          roughness_const=mp["polish_rough"])
        M["paint"] = PBR(f"{ROOT}/Looks/Paint", diffuse_color=mp["paint_color"],
                         roughness_const=mp["paint_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["band"] = PBR(f"{ROOT}/Looks/Band", diffuse_color=mp["band_color"],
                        roughness_const=mp["band_rough"])
        M["cope"] = PBR(f"{ROOT}/Looks/Cope", diffuse_color=mp["cope_color"],
                        roughness_const=mp["cope_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # [v6 C-3] 캐노피 지붕·처마 : 상수색 백판 → 콘크리트 텍스처 + 틴트
        M["roof"] = PBR(
            f"{ROOT}/Looks/Roof", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), mp["roof_scale"],
            tint=mp["roof_tint"])
        M["fascia"] = PBR(
            f"{ROOT}/Looks/Fascia", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), mp["fascia_scale"],
            tint=mp["fascia_tint"])
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["dark"] = PBR(f"{ROOT}/Looks/Dark", diffuse_color=mp["dark_color"],
                        roughness_const=mp["dark_rough"])
        M["warn_y"] = PBR(f"{ROOT}/Looks/WarnY", diffuse_color=mp["warn_y"],
                          roughness_const=0.6)
        M["warn_r"] = PBR(f"{ROOT}/Looks/WarnR", diffuse_color=mp["warn_r"],
                          roughness_const=0.6)
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["emit"] = PBR(f"{ROOT}/Looks/Emit", diffuse_color=mp["lamp_color"],
                        roughness_const=0.4,
                        emission_color=mp["emit_color"],
                        emission_intensity=mp["emit_intensity"])
        M["sign_back"] = PBR(f"{ROOT}/Looks/SignBack",
                             diffuse_color=mp["sign_back_color"],
                             roughness_const=mp["sign_back_rough"])
        for key in ("info",):        # [v5.2 사용자] 임의 경고 팻말 제거
            M[f"sign_{key}"] = PBR(
                f"{ROOT}/Looks/Sign_{key}",
                diff=sc.tex_path(f"sign_{key}", "diff"), uv_mode=True,
                roughness_const=0.45)
        return M

    # -------------------------------------------------------------------
    # 지반 — 개구 2곳(램프 트렌치 · 계단 샤프트)을 비운 6박스
    # -------------------------------------------------------------------
    def build_ground(M):
        gr = PARAMS["ground"]
        sh = PARAMS["shaft"]
        x_p = PARAMS["portal"]["x"]
        cz = gr["z_top"] - gr["thick"] / 2.0
        segs = [("W", gr["x0"], 0.0, gr["y0"], gr["y1"]),
                ("S", 0.0, x_p, gr["y0"], -3.3),
                ("N1", 0.0, sh["x0"], 3.3, gr["y1"]),
                ("N2", sh["x1"], x_p, 3.3, gr["y1"]),
                ("N3", sh["x0"], sh["x1"], sh["y1"], gr["y1"]),
                ("E", x_p, gr["x1"], gr["y0"], gr["y1"])]
        for tag, x0, x1, y0, y1 in segs:
            BOX(f"{ROOT}/Ground_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                (x1 - x0, y1 - y0, gr["thick"]), M["grass"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 개구 2곳을 z=0 평지로 메움."""
        gr = PARAMS["ground"]
        sh = PARAMS["shaft"]
        x_p = PARAMS["portal"]["x"]
        cz = gr["z_top"] - gr["thick"] / 2.0
        BOX(f"{ROOT}/FlatFill_Ramp", (x_p / 2.0, 0.0, cz),
            (x_p, 6.6, gr["thick"]), M["paving"], col=True)
        BOX(f"{ROOT}/FlatFill_Shaft",
            ((sh["x0"] + sh["x1"]) / 2.0, (sh["y0"] + sh["y1"]) / 2.0, cz),
            (sh["x1"] - sh["x0"], sh["y1"] - sh["y0"], gr["thick"]),
            M["paving"], col=True)

    # -------------------------------------------------------------------
    # 지상 포장 오버레이 — 차로(아스팔트) + 보도(인터로킹) 밴드
    #   보도는 차로 확폭부(y ±4.2) 밖에서 끊긴다(횡단부는 차로 포장 = 실제 관행)
    # -------------------------------------------------------------------
    def build_paving(M):
        dr = PARAMS["drive"]
        z = PARAMS["ground"]["z_top"]
        # 차로: 직선부 + 진입 확폭(나팔형)
        BOX(f"{ROOT}/Drive_Main",
            ((dr["x0"] + dr["flare_x0"]) / 2.0, 0.0, z + dr["proud"] - 0.05),
            (dr["flare_x0"] - dr["x0"], 6.6, 0.1), M["asphalt"], col=True)
        BOX(f"{ROOT}/Drive_Flare",
            ((dr["flare_x0"] + dr["x1"]) / 2.0, 0.0, z + dr["proud"] - 0.05),
            (dr["x1"] - dr["flare_x0"], 2 * dr["flare_y"], 0.1),
            M["asphalt"], col=True)
        # [v6 ⑤] 타이어 폴리시 밴드 — 윤적부(중심선 ±0.85, 폭 0.55) 2열.
        #   저면을 노면 아래로 묻고 상면만 4 mm 돌출 → 동일평면 Z파이팅 회피.
        for tag, yc in (("L", -0.85), ("R", 0.85)):
            BOX(f"{ROOT}/DrivePolish_{tag}",
                ((dr["x0"] + dr["x1"]) / 2.0, yc,
                 z + dr["proud"] - 0.006),
                (dr["x1"] - dr["x0"], 0.55, 0.02), M["polish"])
        # 차로 중앙 유도선(파선 5절)
        for i in range(5):
            bx = dr["x0"] + 0.9 + i * 2.6
            BOX(f"{ROOT}/DriveLine_{i}", (bx, 0.0, z + 0.008),
                (1.5, 0.12, 0.02), M["paint"])
        walks = []
        wc = PARAMS["walk_cross"]
        wn = PARAMS["walk_north"]
        ws_ = PARAMS["walk_south"]
        # 횡단 보도는 종주 보도(walk_north/south)와 **겹치지 않게** 4토막
        #   (동일 상면 z 의 두 판이 겹치면 Z파이팅 — 감사 v4 교훈)
        walks.append(("CrossN1", wc["x0"], wc["x1"], dr["flare_y"], wn["y0"],
                      wc["proud"]))
        walks.append(("CrossN2", wc["x0"], wc["x1"], wn["y1"], wc["y_far"],
                      wc["proud"]))
        walks.append(("CrossS1", wc["x0"], wc["x1"], ws_["y1"], -dr["flare_y"],
                      wc["proud"]))
        walks.append(("CrossS2", wc["x0"], wc["x1"], -wc["y_far"], ws_["y0"],
                      wc["proud"]))
        for key in ("walk_north", "walk_south"):
            w = PARAMS[key]
            walks.append((key[5:].capitalize(), w["x0"], w["x1"], w["y0"],
                          w["y1"], w["proud"]))
        ws = PARAMS["walk_spur"]
        walks.append(("Spur", ws["x0"], ws["x1"], ws["y0"], ws["y1"],
                      ws["proud"]))
        for tag, x0, x1, y0, y1, pr in walks:
            BOX(f"{ROOT}/Walk_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, z + pr - 0.06),
                (x1 - x0, y1 - y0, 0.12), M["paving"], col=True)

    # -------------------------------------------------------------------
    # 램프 — 3세그(완화·본선·완화) + 측벽·코핑
    # -------------------------------------------------------------------
    def build_ramp(M, ramp_mtl):
        rp = PARAMS["ramp"]
        segs, total_run = ramp_profile()
        for i, (x0, z0, run, drop) in enumerate(segs, 1):
            # 첫 세그는 차로와 정확히 flush 해야 하므로 margin=0
            mg = 0.0 if i == 1 else rp["seg_margin"]
            sc.build_slope(stage, f"{ROOT}/Ramp_Seg{i}", x0, z0, run, drop,
                           rp["y0"], rp["y1"], rp["thick"], ramp_mtl,
                           margin=mg, collider=True)

    def build_trench_walls(M):
        wl = PARAMS["wall"]
        rp = PARAMS["ramp"]
        x_p = PARAMS["portal"]["x"]
        y_in, t = rp["y1"], wl["thick"]
        y_ctr = y_in + t / 2.0
        cz = (wl["z_top"] + wl["z_bot"]) / 2.0
        hz = wl["z_top"] - wl["z_bot"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/TrenchWall_{tag}", (x_p / 2.0, sgn * y_ctr, cz),
                (x_p, t, hz), M["wall"], col=True)
            BOX(f"{ROOT}/TrenchCope_{tag}",
                (x_p / 2.0, sgn * y_ctr, wl["z_top"] + wl["cope_h"] / 2.0),
                (x_p, t + 2 * wl["cope_over"], wl["cope_h"]), M["cope"],
                col=True)

    # -------------------------------------------------------------------
    # 계단 샤프트 — 되돌음 2련 + 중간참 + 벽체
    # -------------------------------------------------------------------
    def build_stair(M, stair_mtl):
        st = PARAMS["stair"]
        sh = PARAMS["shaft"]
        # 1련: 하행 -X. 로컬(+X 하행)로 지어 rot_group 180° 로 반전.
        px = (st["x_turn"] + st["x_head"]) / 2.0
        py = (st["y_a0"] + st["y_a1"]) / 2.0
        grp = sc.build_rot_group(stage, f"{ROOT}/StairA", (px, py), 180.0)
        sc.build_straight_stairs(
            stage, f"{grp}/Steps", st["x_turn"], st["y_a0"], st["y_a1"],
            st["riser"], st["tread"], st["n_flight"], st["base_z"], stair_mtl,
            z_top=0.0, collider=True)
        if cfg["cue_nosing"]:
            sc.build_nosing(
                stage, f"{grp}/Nosing", st["x_turn"], st["y_a0"], st["y_a1"],
                st["riser"], st["tread"], st["n_flight"], z_top=0.0)
        # 중간참
        BOX(f"{ROOT}/StairLanding",
            ((st["land_x0"] + st["x_turn"]) / 2.0,
             (st["y_a0"] + st["y_b1"]) / 2.0,
             (st["mid_z"] + st["base_z"]) / 2.0),
            (st["x_turn"] - st["land_x0"], st["y_b1"] - st["y_a0"],
             st["mid_z"] - st["base_z"]), stair_mtl, col=True)
        # 2련: 하행 +X (참 → 지하 복도)
        sc.build_straight_stairs(
            stage, f"{ROOT}/StairB", st["x_turn"], st["y_b0"], st["y_b1"],
            st["riser"], st["tread"], st["n_flight"], st["base_z"], stair_mtl,
            z_top=st["mid_z"], collider=True)
        if cfg["cue_nosing"]:
            sc.build_nosing(
                stage, f"{ROOT}/StairB_Nosing", st["x_turn"], st["y_b0"],
                st["y_b1"], st["riser"], st["tread"], st["n_flight"],
                z_top=st["mid_z"])
        # 샤프트 벽: 서(x0..x0+t) · 북(y1-t..y1) · 2련 사이 중간벽
        t = sh["wall_t"]
        wz = (0.0 + st["base_z"]) / 2.0
        wh = 0.0 - st["base_z"]
        BOX(f"{ROOT}/ShaftWall_W",
            (sh["x0"] + t / 2.0, (sh["y0"] + sh["y1"]) / 2.0, wz),
            (t, sh["y1"] - sh["y0"], wh), M["wall_b"], col=True)
        BOX(f"{ROOT}/ShaftWall_N",
            ((sh["x0"] + sh["x1"]) / 2.0, sh["y1"] - t / 2.0, wz),
            (sh["x1"] - sh["x0"], t, wh), M["wall_b"], col=True)
        BOX(f"{ROOT}/ShaftWall_Mid",
            ((st["x_turn"] + st["x_head"]) / 2.0,
             (st["y_a1"] + st["y_b0"]) / 2.0, wz),
            (st["x_head"] - st["x_turn"], st["y_b0"] - st["y_a1"], wh),
            M["wall_b"], col=True)
        # 샤프트 상단 코핑(무난간 관행 — 규정 미달의 현실)
        wl = PARAMS["wall"]
        BOX(f"{ROOT}/ShaftCope_W",
            (sh["x0"] + t / 2.0, (sh["y0"] + sh["y1"]) / 2.0,
             wl["cope_h"] / 2.0),
            (t + 2 * wl["cope_over"], sh["y1"] - sh["y0"], wl["cope_h"]),
            M["cope"])
        BOX(f"{ROOT}/ShaftCope_N",
            ((sh["x0"] + sh["x1"]) / 2.0, sh["y1"] - t / 2.0,
             wl["cope_h"] / 2.0),
            (sh["x1"] - sh["x0"], t + 2 * wl["cope_over"], wl["cope_h"]),
            M["cope"])

    # -------------------------------------------------------------------
    # 지하 — 복도 + 주차장(바닥·벽·기둥·구획선·약발광 조명)
    # -------------------------------------------------------------------
    def build_underground(M):
        co = PARAMS["corridor"]
        ga = PARAMS["garage"]
        t = co["wall_t"]
        # 복도 바닥
        BOX(f"{ROOT}/Corridor_Floor",
            ((co["x0"] + co["x1"]) / 2.0, (co["y0"] + co["y1"]) / 2.0,
             co["floor_z"] - co["floor_thick"] / 2.0),
            (co["x1"] - co["x0"], (co["y1"] - co["y0"]) + 2 * t,
             co["floor_thick"]), M["conc"], col=True)
        # 복도 벽 2 (천장 = 지반 플레이트 저면)
        wz = (co["floor_z"] + co["ceil_z"]) / 2.0
        wh = co["ceil_z"] - co["floor_z"]
        for sgn, tag, yc in ((-1.0, "S", co["y0"] - t / 2.0),
                             (1.0, "N", co["y1"] + t / 2.0)):
            BOX(f"{ROOT}/Corridor_Wall_{tag}",
                ((co["x0"] + co["x1"]) / 2.0, yc, wz),
                (co["x1"] - co["x0"], t, wh), M["wall_b"], col=True)
        # 주차장 바닥
        BOX(f"{ROOT}/Garage_Floor",
            ((ga["x0"] + ga["x1"]) / 2.0, (ga["y0"] + ga["y1"]) / 2.0,
             ga["floor_z"] - ga["floor_thick"] / 2.0),
            (ga["x1"] - ga["x0"], ga["y1"] - ga["y0"], ga["floor_thick"]),
            M["conc"], col=True)
        # 주차장 벽 (남·북·동) + 서측 마구리 3토막
        #   서측은 x=x0 면에서 **램프 개구(y ±3)와 복도 개구만 비우고** 막는다.
        #   비우지 않으면 지하 공동이 흙 속으로 뚫려 PT 에서 검은 구멍이 된다.
        gz = (ga["floor_z"] + ga["ceil_z"]) / 2.0
        gh = ga["ceil_z"] - ga["floor_z"]
        gt = ga["wall_t"]
        rp = PARAMS["ramp"]
        for tag, yc in (("S", ga["y0"] + gt / 2.0), ("N", ga["y1"] - gt / 2.0)):
            BOX(f"{ROOT}/Garage_Wall_{tag}",
                ((ga["x0"] + ga["x1"]) / 2.0, yc, gz),
                (ga["x1"] - ga["x0"], gt, gh), M["wall_b"], col=True)
        BOX(f"{ROOT}/Garage_Wall_E",
            (ga["x1"] - gt / 2.0, (ga["y0"] + ga["y1"]) / 2.0, gz),
            (gt, ga["y1"] - ga["y0"], gh), M["wall_b"], col=True)
        for tag, y0, y1 in (("a", ga["y0"], rp["y0"]),
                            ("b", rp["y1"], co["y0"]),
                            ("c", co["y1"], ga["y1"])):
            if y1 - y0 <= 1e-6:
                continue
            BOX(f"{ROOT}/Garage_Wall_W{tag}",
                (ga["x0"] + gt / 2.0, (y0 + y1) / 2.0, gz),
                (gt, y1 - y0, gh), M["wall_b"], col=True)
        # 기둥
        cs = PARAMS["garage_col"]["size"]
        for i, (cx, cy) in enumerate(PARAMS["garage_cols"]):
            BOX(f"{ROOT}/Garage_Col_{i}", (cx, cy, gz), (cs, cs, gh),
                M["wall"], col=True)
        # 주차구획 도색선
        pl = PARAMS["park_line"]
        for i, (lx, ly) in enumerate(PARAMS["park_lines"]):
            BOX(f"{ROOT}/ParkLine_{i}",
                (lx, ly + pl["len"] / 2.0, ga["floor_z"] + pl["z_off"]),
                (pl["w"], pl["len"], 0.02), M["paint"])
        # 약발광 천장 조명 (PT 8바운스 전제)
        gl = PARAMS["garage_lamp"]
        for i, (lx, ly) in enumerate(PARAMS["garage_lights"]):
            BOX(f"{ROOT}/GarageLamp_{i}", (lx, ly, gl["z"]), gl["size"],
                M["emit"])
        for i, (lx, ly) in enumerate(PARAMS["corridor_lights"]):
            BOX(f"{ROOT}/CorridorLamp_{i}", (lx, ly, gl["z"]),
                (gl["size"][0] * 0.7, gl["size"][1], gl["size"][2]),
                M["emit"])

    # -------------------------------------------------------------------
    # 진입부 설비 — 캐노피 + 높이제한바 + 차단기
    # -------------------------------------------------------------------
    def build_entry_gear(M):
        cp = PARAMS["canopy"]
        sc.build_canopy(stage, f"{ROOT}/Canopy", cp["x0"], cp["x1"],
                        cp["y0"], cp["y1"], cp["z_roof"], cp["post_r"],
                        M["roof"], M["post"], roof_t=cp["roof_t"],
                        base_z=cp["base_z"])
        # [v6 C-3] 처마(페시아) 4변 — 슬래브 외주를 감싸고 소핏 아래로 fas_drop
        #   내려온다. 상단은 지붕 상면보다 fas_top_in 낮춰(동일평면 회피) 리빌을
        #   남기고, 내측으로 fas_in 파고들어 슬래브와 교차시킨다.
        ov, fin = cp["fas_ov"], cp["fas_in"]
        fz0 = cp["z_roof"] - cp["fas_drop"]
        fz1 = cp["z_roof"] + cp["roof_t"] - cp["fas_top_in"]
        fcz, fch = (fz0 + fz1) / 2.0, fz1 - fz0
        for tag, x0, x1, y0, y1 in (
                ("S", cp["x0"] - ov, cp["x1"] + ov,
                 cp["y0"] - ov, cp["y0"] + fin),
                ("N", cp["x0"] - ov, cp["x1"] + ov,
                 cp["y1"] - fin, cp["y1"] + ov),
                ("W", cp["x0"] - ov, cp["x0"] + fin,
                 cp["y0"] + fin, cp["y1"] - fin),
                ("E", cp["x1"] - fin, cp["x1"] + ov,
                 cp["y0"] + fin, cp["y1"] - fin)):
            BOX(f"{ROOT}/Canopy/Fascia_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, fcz),
                (x1 - x0, y1 - y0, fch), M["fascia"])
        # 하면(소핏) 조명 3개소 — 슬래브 밑면에 매입, soffit_drop 만 돌출
        sw, sd, sh = cp["soffit"]
        for i, sx in enumerate(cp["soffit_xs"]):
            BOX(f"{ROOT}/Canopy/Soffit_{i}",
                (sx, 0.0, cp["z_roof"] - cp["soffit_drop"] + sh / 2.0),
                (sw, sd, sh), M["emit"])
        # 높이제한바 — 캐노피 전면 보에 매달린다(황·흑 교대 8절)
        hb = PARAMS["height_bar"]
        seg_len = (hb["y1"] - hb["y0"]) / hb["nseg"]
        for i in range(hb["nseg"]):
            yc = hb["y0"] + (i + 0.5) * seg_len
            CYL(f"{ROOT}/HeightBar/Seg_{i}", (hb["x"], yc, hb["z"]),
                hb["r"], seg_len * 1.02,
                M["warn_y"] if i % 2 == 0 else M["dark"], rotX=90.0)
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/HeightBar/Hanger_{tag}",
                (hb["x"], sgn * (hb["y1"] - 0.25),
                 (hb["z"] + cp["z_roof"]) / 2.0),
                (hb["hanger_t"], hb["hanger_t"], cp["z_roof"] - hb["z"]),
                M["post"])
        # 차단기 — 옹벽 코핑 위 함체 + 하강 상태 차단봉(적·백 교대 7절)
        gt = PARAMS["gate"]
        BOX(f"{ROOT}/Gate/Box",
            (gt["x"], gt["y"], gt["base_z"] + gt["box"][2] / 2.0),
            gt["box"], M["post"], col=True)
        aseg = (gt["arm_y1"] - gt["arm_y0"]) / gt["nseg"]
        for i in range(gt["nseg"]):
            yc = gt["arm_y1"] - (i + 0.5) * aseg
            CYL(f"{ROOT}/Gate/Arm_{i}", (gt["x"], yc, gt["arm_z"]),
                gt["arm_r"], aseg * 1.02,
                M["warn_r"] if i % 2 == 0 else M["band"], rotX=90.0)

    # -------------------------------------------------------------------
    # 단서 (cue) — 볼라드·점형블록 / 난간 / 사인
    # -------------------------------------------------------------------
    def build_bollards(M):
        """[v5.1 규정 볼라드] 높이 0.9 · 지름 0.16 · 간격 1.5 · 상단 반사띠 +
        전면 0.3 m 점형블록. 배치는 보도가 차로를 횡단하는 접점 2곳뿐."""
        bo = PARAMS["bollard"]
        wc = PARAMS["walk_cross"]
        for r, row in enumerate(PARAMS["bollard_rows"]):
            for i, bx in enumerate(row["xs"]):
                sc.build_bollard(stage, f"{ROOT}/Bollard_{r}_{i}", bx,
                                 row["y"], 0.0, mtl=M["bollard"],
                                 radius=bo["r"], height=bo["h"])
                CYL(f"{ROOT}/BollardBand_{r}_{i}", (bx, row["y"],
                                                    bo["band_z"]),
                    bo["band_r"], bo["band_h"], M["band"])
            if cfg["cue_tactile"]:
                sc.build_tactile(stage, f"{ROOT}/Tactile_Bollard_{r}",
                                 wc["x0"], wc["x1"], row["tac_y0"],
                                 row["tac_y1"], M["tactile"], z=0.0,
                                 proud=PARAMS["tactile"]["proud"])

    def build_railings(M):
        ra = PARAMS["rail"]
        top_z = ra["base_z"] + ra["h"]
        mid_z = ra["base_z"] + ra["mid_h"]

        def line(prefix, axis, c, a0, a1):
            mid_a = (a0 + a1) / 2.0
            L = a1 - a0
            rotY, rotX = (90.0, 0.0) if axis == "x" else (0.0, 90.0)
            for tag, r, z in (("Top", ra["rail_r"], top_z),
                              ("Mid", ra["mid_r"], mid_z)):
                ctr = (mid_a, c, z) if axis == "x" else (c, mid_a, z)
                CYL(f"{prefix}/{tag}", ctr, r, L, M["rail"],
                    rotY=rotY, rotX=rotX)
            n = 0
            a = a0 + 0.25
            while a <= a1 - 0.2 + 1e-6:
                ctr = ((a, c, ra["base_z"] + ra["h"] / 2.0) if axis == "x"
                       else (c, a, ra["base_z"] + ra["h"] / 2.0))
                CYL(f"{prefix}/Post_{n}", ctr, ra["post_r"], ra["h"],
                    M["rail"], col=True)
                a += ra["spacing"]
                n += 1

        for i, rr in enumerate(PARAMS["rail_runs"]):
            line(f"{ROOT}/Rail_{i}", rr["axis"], rr["c"], rr["a0"], rr["a1"])

    def build_tactiles(M):
        tc = PARAMS["tactile"]
        st = PARAMS["stair"]
        # 계단 머리 경고띠(지상) + 계단 하부 착지 경고띠(지하)
        sc.build_tactile(stage, f"{ROOT}/Tactile_StairHead",
                         tc["head_x0"], tc["head_x1"], st["y_a0"], st["y_a1"],
                         M["tactile"], z=0.0, proud=tc["proud"])
        sc.build_tactile(stage, f"{ROOT}/Tactile_StairFoot",
                         tc["foot_x0"], tc["foot_x1"], st["y_b0"], st["y_b1"],
                         M["tactile"], z=-PARAMS["ramp"]["drop"],
                         proud=tc["proud"])

    def build_signs(M):
        """[v5.2 사용자] 임의 경고 팻말 제거 — 요금 안내판(지주식) 1매만."""
        for key, prm in (("info", PARAMS["sign_info"]),):
            sc.build_sign(stage, f"{ROOT}/Sign_{key}", prm["cx"], prm["cy"],
                          0.0, prm["yaw"], panel_mtl=M[f"sign_{key}"],
                          w=prm["w"], h=prm["h"], pole_h=prm["pole_h"],
                          pole_mtl=M["post"], back_mtl=M["sign_back"])

    # -------------------------------------------------------------------
    # 드레싱 — 화단·수목·생울타리·벤치·가로등·아파트 3동
    # -------------------------------------------------------------------
    def build_dressing(M):
        pl = PARAMS["planter"]
        for i, p in enumerate(PARAMS["planters"]):
            sc.build_planter(
                stage, f"{ROOT}/Planter_{i}", p["cx"], p["cy"], 0.0,
                M["cope"] if i % 2 else M["wall_b"],
                M["grass_b"] if i % 2 else M["grass"],
                tree_mtls=((M["wood"], M["canopy_a"], M["canopy_b"])
                           if p["tree"] else None),
                size=p["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"],
                grass_h=pl["grass_h"])
        for i, (tx, ty) in enumerate(PARAMS["trees"]):
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", tx, ty, 0.0,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        for i, (hx0, hy0, hx1, hy1) in enumerate(PARAMS["hedges"]):
            sc.build_hedge(stage, f"{ROOT}/Hedge_{i}", hx0, hy0, hx1, hy1,
                           0.85, base_z=0.0)
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, 0.0,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (lx, ly, sl["pole_h"] / 2.0), sl["pole_r"],
                sl["pole_h"], M["post"], col=True)
            CYL(f"{base}/Arm", (lx - sl["arm_len"] / 2.0, ly,
                                sl["pole_h"] - 0.12),
                sl["arm_r"], sl["arm_len"], M["post"], rotY=90.0)
            BOX(f"{base}/Head", (lx - sl["arm_len"], ly, sl["pole_h"] - 0.17),
                (sl["head"], sl["head"], 0.12), M["lamp"])
        for i, (key, bd) in enumerate(PARAMS["buildings"].items()):
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["shell"] if i % 2 == 0 else M["shell_b"],
                              M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    ramp_mtl = M["conc"] if cfg["cue_material_break"] else M["paving"]
    stair_mtl = M["conc"] if cfg["cue_material_break"] else M["paving"]

    build_ground(M)
    build_paving(M)
    if cfg["hazard_stairs"]:
        build_ramp(M, ramp_mtl)
        build_trench_walls(M)
        build_stair(M, stair_mtl)
        build_underground(M)
        build_entry_gear(M)
        build_bollards(M)
        if cfg["cue_railing"]:
            build_railings(M)
        if cfg["cue_tactile"]:
            build_tactiles(M)
        if cfg["cue_sign"]:
            build_signs(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene13_{ts}.png")
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
