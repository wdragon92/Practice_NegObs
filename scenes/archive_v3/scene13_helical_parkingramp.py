# -*- coding: utf-8 -*-
"""
scene13_helical_parkingramp.py — NegObs 인공씬 13호: T10 주차장 나선 램프
(Isaac Sim 4.5)

사양서 : Docs/multi_scene_brief_v3.md §D scene13_helical_parkingramp (유일 사양)
공통 라이브러리 : scene_common.py (§A) — boot·make_pbr·build_helix_ramp·build_helix_steps·조명·캡처
모티프 참조 : scene05_amphitheater.py (main 골격·원형 개구 4박스 분할)

유형 정체성: "경사(주행 가능) vs 계단(불가)" 혼동쌍 병치.
  매끈한 나선 램프(r_in6/r_out9.5, 1.25회전, 낙차 3.2)와 내측 병설 나선 계단
  (r_in4.8/r_out6, 낙차 3.2)이 같은 코어를 공유. 모델이 경사도와 낙차를 분리
  학습해야 하는 대비쌍.

실행 / 캡처 / 스모크 : scene05·scene06 와 동일한 env 규약.
    NEGOBS_CAPTURE=1 / NEGOBS_SMOKE=1 / NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG

좌표계: Z-up, m. 램프·계단·코어 동심 중심 (0, 0). 램프 상면(진입) z=0, 하부 z=−3.2.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 7키. hazard_stairs=나선 램프+계단 기하 토글(↔ 평지 원반).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # 나선 램프+계단 (False → z=0 평지 원반)
    "cue_railing":        True,    # 램프 외측 파이프 난간(주차 램프 안전시설)
    # [v5 공통 레이어] 도시 관행 씬(01/02/05/13/14/16/20/21) cue_tactile 기본 True
    "cue_tactile":        True,    # 계단 상단 참(a −24..0) 경고 점자띠
    "cue_material_break": True,    # 연석(다크) + 중앙 도색선(백색) 재질 경계
    "cue_nosing":         False,   # True → 계단 단코 논슬립 아크 밴드
    "cue_sign":           True,    # [v5 공통 레이어] sign_no_entry(보행 금지) 1매
    "cue_scene_dressing": True,    # 지상 진입 광장·건물·잔디
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    center=dict(cx=0.0, cy=0.0),
    # 나선 램프: r_in6/r_out9.5, a0 0..450°(1.25회전), 낙차 0→−3.2, 두께 0.35
    #   seg 60. bands 4 — 감사 B-13-5 대응:
    #   build_helix_ramp 의 세그 현길이는 **r_mid** 기준(L_c=2·r_mid·sin(dθ/2)·1.02)
    #   이라 외경에서 (r_out−1.02·r_mid)·dθ 만큼 방사형 쐐기 틈이 생긴다.
    #   현 파라미터 = (9.5−7.905)·0.1309 ≈ 0.21 m 슬릿 ×60. 밴드를 4개로 쪼개면
    #   각 밴드의 r_out−1.02·r_mid 가 줄어 슬릿이 ≈0.04 m 로 축소된다.
    #   (근본 수정은 scene_common 에 r_out 기준 chord 옵션 추가 — 픽스로그 보고)
    ramp=dict(r_in=6.0, r_out=9.5, a0=0.0, a1=450.0, seg=60, bands=4,
              z0=0.0, z1=-3.2, thick=0.35),
    # 차량 진입 개구 [감사 A-13-1/2]: 외측 연석·난간을 a=cue_a0 에서 시작시켜
    #   a 0..22° 구간(램프 상면 0..−0.156, 광장 −0.002 대비 단차 ≤0.16 m)을
    #   광장에서 반경방향으로 진입 가능한 '입구'로 남긴다. 별도 에이프런 슬래브를
    #   a<0 에 깔지 않는 이유: a 312..360 램프(2회전째, z −2.22..−2.56) 바로 위가
    #   되어 유효고 1.9 m 로 떨어진다(차량 통과 불가).
    entry=dict(cue_a0=22.0,
               # 램프 상단 종단벽(a −4..0, r 6..9.58) — a=0 끝면 아래 2.56 m 낙차 방호
               endwall=dict(a0=-4.0, a1=0.0, seg=2, r_in=6.0, r_out=9.58,
                            top_z=0.95, base_z=-0.35),
               # 보행 브리지(광장 r9.6 → 계단참). 하부 램프(a≈336, z −2.39) 대비
               #   유효고 = 2.39−0.25 ≈ 2.14 m
               bridge=dict(a0=-24.0, a1=-10.0, seg=4, r_in=4.45, r_out=9.60,
                           top_z=0.0, base_z=-0.25, parapet_h=1.05),
               # 계단 상단 참(r 4.45..6.0, a −24..0) — 계단 1단(top −0.16)에 접속
               landing=dict(a0=-24.0, a1=0.0, seg=5, r_in=4.45, r_out=6.0,
                            top_z=0.0, base_z=-0.40)),
    # 지하 조명·기둥 — 지하층 칠흑 해소 [A-13①ㆍ감사 B-13-3]
    #   구 사양(스트립 4개 y=−6/−2/2/6, len 16)은 ① 코어(r4.5)를 관통하고
    #   ② 나선 천장(램프 하면)이 방위각마다 달라 허공에 뜨는 문제가 있었다.
    #   → 램프 하면 아래에 실제로 들어가는 4개 위치로 재배치 + 면광원 병설.
    #   각 스트립은 r 6.3..9.5(램프 바로 아래) 안에서 그 방위의 램프 하면
    #   (z(a)−thick) 보다 낮게 z 를 잡았다 — 좌표 산술은 픽스로그 참조.
    #   [v5 판정 반영] 지하 흑색 미해소(RT·구 PT 공통 84~99 % 가 휘도 20 미만)
    #   → 램프 하부 조도를 전담하는 이 광원군이 절대량 부족. 개수 4 → 9,
    #   light_intensity 9000 → 300000 으로 보강한다. 신설 5기는 기존 4기와 같은
    #   환형(r 7.0~7.9, 램프 하면 아래)에 방위 118/134/148/182/206° 로 배치해
    #   basement 뷰(eye (0,6.8,−2.45) → tgt (−7.5,0,−1.0)) 가 훑는
    #   x −9..0 · y −4..8 대역(주차구획선 4·차량 3·방화문)을 균일하게 덮는다.
    #   z 는 각 방위의 램프 하면 = −3.2·θ/450 − 0.35 보다 0.11~0.13 m 낮게 잡아
    #   (세그 7.5° 의 z 요동 0.053 포함) 슬래브 관통이 없다.
    garage=dict(strips=[dict(cx=-7.6, cy=2.20, sx=3.2, sy=0.22, z=-1.62),
                        dict(cx=-5.8, cy=5.60, sx=3.6, sy=0.22, z=-1.45),
                        dict(cx=-2.0, cy=7.70, sx=0.22, sy=3.0, z=-1.19),
                        dict(cx=-8.0, cy=-0.90, sx=0.22, sy=3.4, z=-1.83),
                        # --- [v5 판정 반영] 신설 5기 (r 7.9, 1.4×1.4 판) ---
                        dict(cx=-3.71, cy=6.97, sx=1.4, sy=1.4, z=-1.33),
                        # z −1.56 : 기존 스트립 1(z −1.45, y 5.49..5.71)과
                        #   xy 가 겹치므로 0.11 m 내려 판 간 관통·근접 코플래너를
                        #   피한다(램프 하면 −1.350 대비 여유 0.18).
                        dict(cx=-5.44, cy=5.73, sx=1.4, sy=1.4, z=-1.56),
                        dict(cx=-6.70, cy=4.19, sx=1.4, sy=1.4, z=-1.54),
                        dict(cx=-7.00, cy=-0.30, sx=1.4, sy=1.4, z=-1.82),
                        dict(cx=-7.10, cy=-3.46, sx=1.4, sy=1.4, z=-1.96)],
                strip_t=0.06,
                color=(0.95, 0.97, 1.0), intensity=2500.0,
                # OmniPBR emissive 는 PT 에서 메시 광원으로 등록되지 않는다(감사
                #   B-13-3). 동일 위치에 RectLight 를 병설해 실조명을 준다.
                arealight=True, light_intensity=300000.0,
                # 기둥은 방위별 램프 하면까지 정확히 뻗는다(구 사양은 −0.42 고정
                #   이라 나선 천장 아래 허공에 떠 있었다).
                col_r=0.3, col_rad=7.75, col_az=[55.0, 100.0, 145.0, 190.0],
                col_z0=-3.25),
    # 내측 병설 나선 계단: r_in4.45(코어 r4.5 와 0.05 겹침 → 환형 슬롯 폐쇄)
    #   step_deg 12→6 [감사 A-13-5]: 현 = 2·5.225·sin3° = 0.547 m.
    #   구 12° 는 1.13 m/단(한 단당 2보)로 계단 판독 자체가 무너졌다.
    #   riser 0.16 × 20단 = 낙차 3.2 (불변), 호 120°.
    stair=dict(r_in=4.45, r_out=6.0, a0=0.0, step_deg=6.0, n=20,
               riser=0.16, z0=0.0, base_drop=0.5),
    # 중앙 코어 Cylinder r4.5 (z −3.7..0.3) + 계단실 헤드하우스 [감사 B-13-4]
    core=dict(r=4.5, z_bot=-3.7, z_top=0.3),
    headhouse=dict(s=3.4, h=2.60, roof_t=0.25, door_w=1.10, door_h=2.10),
    # 램프 연석(내/외측) — helix_ramp 로 램프 슬로프를 따라 상면 +0.1
    #   thick 0.22→0.18 [감사 A-13-8]: 계단 1단 상면(−0.16)과 3 mm 간섭 해소
    curb=dict(inner=(5.92, 6.02), outer=(9.48, 9.58), z_off=0.10, thick=0.18),
    # 중앙 도색선: 폭 0.12, 램프 상면 +0.006, 두께 0.05 [감사 B-13-6]
    #   두껍게 깔아 밴드 이음(≈5 mm 단차)을 덮고 '떠 있는 백색 각재' 인상 제거.
    centerline=dict(r_in=7.69, r_out=7.81, z_off=0.006, thick=0.05),
    # 지하층 바닥 슬래브: 상면 z=−3.25 (램프 하단 −3.2 와 동일평면 Z파이팅 회피, §8)
    basement=dict(r=9.7, top_z=-3.25, thick=0.4),
    # 지하 외주벽 — 슬래브 림 바깥이 허공이던 문제(지평 미폐쇄) 폐쇄
    garage_wall=dict(r_in=9.70, r_out=10.00, seg=48, top_z=-0.28, base_z=-3.35),
    # 지상 진입 광장(아스팔트 톤 plaza_lower) — 램프 원형 개구는 링+4박스 분할
    #   감사 B-13-2 — ±45 는 프레임 안에서 지면이 끊겼다 → ±110
    plaza=dict(x0=-110.0, x1=110.0, y0=-110.0, y1=110.0, z_top=0.0, thick=0.5),
    ring=dict(r_in=9.5, r_out=14.0, seg=56, top_z=-0.002, base_z=-0.5),
    # 지평 폐쇄 건물 4동 [감사 B-13-1/D-4] — 전부 광장(±110) 안에 착지
    buildings=dict(
        C=dict(x0=46.0, x1=58.0, y0=-18.0, y1=18.0, h=15.0, floors=5,
               axis="x", facade_x=46.0, face_dir=-1.0),
        W=dict(x0=-72.0, x1=-56.0, y0=-36.0, y1=36.0, h=20.0, floors=6,
               axis="x", facade_x=-56.0, face_dir=1.0),
        N=dict(x0=-30.0, x1=10.0, y0=42.0, y1=58.0, h=18.0, floors=6,
               axis="y", facade_y=42.0, face_dir=-1.0),
        S=dict(x0=-30.0, x1=10.0, y0=-58.0, y1=-42.0, h=17.0, floors=5,
               axis="y", facade_y=-42.0, face_dir=1.0),
    ),
    # --- 주차장 즉독 드레싱 (cue_scene_dressing) [감사 C '주차장 신호 0개'] ---
    lot=dict(
        canopy=dict(x0=10.5, x1=16.0, y0=-3.0, y1=4.0, z_roof=3.30,
                    post_r=0.18),
        gate=dict(bar_x=12.3, bar_y0=-0.10, bar_y1=2.90, bar_z=1.05,
                  bar_r=0.05, ped_x=12.3, ped_y=-0.25, ped_r=0.12,
                  ped_h=1.10),
        booth=dict(cx=12.6, cy=-2.20, sx=1.70, sy=1.70, h=2.50),
        hbar=dict(x=10.3, y=0.50, span=6.0, z=2.35, post_r=0.06, post_h=2.50),
        sign=dict(cx=16.5, cy=3.0, pole_r=0.07, pole_h=3.20, w=1.10, h=1.10),
        # 지하 주차구획선 (cx, cy, 길이X) — 전부 r 4.85..9.6 안, 램프 하면 아래
        bays=((-6.9, 0.10, 3.9), (-6.9, 2.85, 3.9),
              (-6.2, 5.10, 3.6), (-5.0, 6.95, 3.0)),
        # 주차 차량 대용 박스 (cx, cy, 색인) — 유효고 1.7~2.0 m 구간에만 배치
        cars=((-6.8, 1.90, 0), (-5.6, 4.20, 1), (-4.6, 6.00, 2)),
        #   차 전고 = 0.30(휠) + 0.70(바디) + 0.50(캐빈) = 1.50 → 상면 z=−1.75.
        #   3 대 배치점의 최저 램프 하면은 −1.582 → 여유 0.17 m 이상 확보.
        car=dict(sx=3.80, sy=1.75, lift=0.30, body_h=0.70, cabin_h=0.50,
                 cabin_sx=2.00, cabin_sy=1.62, wheel_r=0.30, wheel_t=0.20),
        car_colors=((0.030, 0.032, 0.035), (0.090, 0.092, 0.098),
                    (0.045, 0.028, 0.026)),
        # 코어 지하 방화문 — 코어(r 4.5) 표면에 부착, 문턱 = 지하 슬래브
        firedoors=((4.47, 0.0), (-4.47, 0.0)),
        firedoor=dict(sx=0.08, sy=1.10, h=2.10),
        # 코어 상면(z=0.3) 진입 2단 — 계단참(z=0)에서 헤드하우스 문으로
        core_steps=((5.35, -1.55, 0.15), (4.75, -1.35, 0.30)),
        # 볼라드 열 = 램프 개구의 보행 경계 표시.
        #   r 12.6 : 프리셋 카메라 반경(11.5/14.5/19.5)과 겹치지 않는 값.
        #   방위    : 차량 개구(a 0..22)·보행 브리지(a 336..350)·프리셋 시선축
        #             (az 180)을 비운다.
        bollard_r=12.6, bollard_az=(40.0, 75.0, 110.0, 145.0,
                                    215.0, 250.0, 285.0, 320.0),
        trees=((-16.0, 13.0), (-16.0, -13.0), (-22.0, 13.0), (-22.0, -13.0),
               (-28.0, 13.0), (-28.0, -13.0)),
        planters=((-18.0, 8.0), (-18.0, -8.0)),
        benches=((-12.0, 6.0), (-12.0, -6.0), (-12.0, 10.0), (-12.0, -10.0)),
    ),
    # [v5 공통 레이어] 한글 사인 — (태그, TEX 키, cx, cy, base_z, yaw, w, h)
    #   NoEntry: 차량 진입 개구(a 0..22°) 바로 옆 **보행 금지** 표지.
    #     극좌표 r=10.6, a=24° → (9.68, 4.31). 램프 외경 r 9.5 에서 **1.10 m
    #     이격**(위험 기하 ≥0.5 m 충족), 지상 광장(z=0) 위.
    #     주차 캐노피(x 10.5..16, y −3..4) 밖, 높이제한바 포스트(10.3, 3.5,
    #     r 0.06) 에서 0.86 m, 볼라드열(r 12.6, az 40°→(9.65, 8.10)) 에서 3.79 m.
    #   카메라 검산(화각 ±30°):
    #     top_entry(14.5,−1.2) 축 160.1° vs 131.2° → 28.9° (프레임 가장자리)
    #     stair_entry(12.4,−5.2) 축 150.6° vs 106.0° → 44.6° 밖
    #     ramp_descent(0,12.5) 축 −71.6° vs −40.2° → 31.4° 밖
    #     그리드(eye x −11.5/−14.5/−19.5, y 0) → 11.5°/9.4°/7.5°, 거리 21.6 m↑
    #       (원경 주변부, 램프 실루엣 뒤 — 시선 차폐 없음)
    signs=[("NoEntry", "sign_no_entry", 9.68, 4.31, 0.0, 24.0, 0.75, 0.75)],

    material=dict(
        scale=dict(concrete_floor=1.5, concrete_wall=2.0, plaza_lower=0.9,
                   granite_dark=1.0, brick_red=2.0, grass=4.0),
        # 감사 B-13-7 / D-6 — 0.82 는 '기념광장 판석'. 아스팔트 진입로 톤으로.
        asphalt_tint=(0.42, 0.42, 0.44),          # plaza_lower 아스팔트 톤
        concrete_tint=(0.62, 0.62, 0.63),         # 램프 콘크리트 한 단계 어둡게
        core_tint=(0.58, 0.58, 0.59),
        line_color=(0.55, 0.55, 0.52),            # 마모 도색(감마 중간톤)
        basement_color=(0.055, 0.055, 0.060),     # 어두운 콘크리트
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.55, 0.57, 0.60), rail_metallic=0.9, rail_rough=0.35,
        parapet_color=(0.62, 0.62, 0.60), parapet_rough=0.6,
        steel_color=(0.05, 0.055, 0.055), steel_metallic=0.5, steel_rough=0.5,
        booth_color=(0.16, 0.17, 0.18), booth_rough=0.6,
        signface_color=(0.025, 0.055, 0.16),      # 주차 안내판(청색)
        wood_color=(0.075, 0.055, 0.038),
        leaf_a=(0.085, 0.150, 0.055), leaf_b=(0.055, 0.110, 0.045),
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


_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene13")


def _add_emission(stage, mtl_path, color, intensity):
    """OmniPBR 발광 활성화 — Shader 에 enable_emission/emissive_color/
    emissive_intensity 입력 세팅(입력명 OmniPBR.mdl 확인). intensity 는 실내 가독용
    수천 단위 — 지하가 어둡/밝으면 garage.intensity 를 조정한다."""
    from pxr import UsdShade, Sdf, Gf
    sh = UsdShade.Shader.Get(stage, mtl_path + "/Shader")
    sh.CreateInput("enable_emission", Sdf.ValueTypeNames.Bool).Set(True)
    sh.CreateInput("emissive_color",
                   Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    sh.CreateInput("emissive_intensity",
                   Sdf.ValueTypeNames.Float).Set(float(intensity))


# ===========================================================================
# [D] 카메라 프리셋 — grid_views(gy=0, 외경 시프트) + 미장센 4컷
# ===========================================================================
def build_views():
    """그리드 기준을 외경(r_out=9.5)만큼 −X 시프트 → d=구조물까지 거리."""
    R = PARAMS["ramp"]["r_out"]
    v = sc.grid_views(0.0)
    out = {}
    for k, val in v.items():
        e, t = list(val["eye"]), list(val["tgt"])
        e[0] -= R
        t[0] -= R
        out[k] = dict(eye=e, tgt=t)
    out["ramp_vs_stair"] = dict(eye=[-2.0, -11.5, 2.4], tgt=[0.0, -2.5, -1.2])
    # top_entry: 캐노피 아래 차량 진입선상. 차단기(x12.3, y −0.1..2.9, z≈1.05)와
    #   높이제한바(x10.3, z 2.2..2.5) 사이를 시선이 통과하도록 재조준.
    out["top_entry"]     = dict(eye=[14.5, -1.2, 1.7],  tgt=[4.0, 2.6, -0.8])
    out["ramp_descent"]  = dict(eye=[0.0, 12.5, 1.5],   tgt=[3.0, 3.5, -2.2])
    out["basement"]      = dict(eye=[0.0, 6.8, -2.45],  tgt=[-7.5, 0.0, -1.0])  # 핫픽스: 채광측 조망
    # stair_entry: 광장 → 보행 브리지(a −24..−10) → 계단 상단 참(a −24..0) 접속 검수
    # [v5 판정 반영] 구 eye (12.4,−3.8,1.7) 은 시선축상 캐노피 기둥(10.5,−3.0,
    #   r 0.18)이 거리 2.06 m·측방 편차 0.06 m 에 놓여 화면 가로 15 % 를 검은
    #   원통이 점유했다. eye y −3.8 → −5.2 로 이설하면 같은 기둥의 측방 편차가
    #   0.98 m(반경 0.18 대비 여유 0.80 m)로 벌어진다. 재검산: 요금부스
    #   (x 11.75..13.45, y −3.05..−1.35) 는 시선이 x=11.75 를 지날 때 y=−4.83 로
    #   남측 통과, 차단기 붐(x 12.3, y −0.1..2.9)·높이제한바(x 10.3, y −2.5..3.5)
    #   ·게이트 받침(12.3,−0.25)·볼라드열(r 12.6) 모두 시선축 밖. tgt 불변.
    out["stair_entry"]   = dict(eye=[12.4, -5.2, 1.7],  tgt=[4.6, -0.8, -0.6])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. ramp_vs_stair  — 매끈한 램프 vs 계단이 같은 코어에서 병치(혼동쌍)
 2. h0.3·d5~10     — 램프 상면과 지면 경계의 낙차(3.2m) 인지 (개방 유지가 정답)
 3. top_entry      — 캐노피·차단기·요금부스·높이제한바로 '주차장'이 읽히나
 4. stair_entry    — 광장→보행 브리지→계단 상단 참 연속 (A-13-3)
 5. ramp_descent   — 나선 램프 방사 슬릿(밴드 4분할 후 ≈4cm)·중앙선 정합
 6. basement       — 램프 하부(−3.2) 착지 · 형광등 실광원 · 구획선/차량
 7. cue            — 연석(다크)+중앙 도색선 / 외측 난간(a 22°~) · 내측 난간
 8. [v5] 공통 레이어 — 계단 상단 참 점자띠 + sign_no_entry(진입구 옆) 판독"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"

    sc.check_assets(
        ["concrete_floor", "concrete_wall", "plaza_lower", "granite_dark",
         "brick_red", "grass", "sign_no_entry", "hdri", "mdl"],
        hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene13")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    C = PARAMS["center"]
    cx, cy = C["cx"], C["cy"]

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        scl = mp["scale"]
        M = {}
        M["concrete"] = sc.make_pbr(
            stage, "/World/Looks/Concrete", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), scl["concrete_floor"],
            tint=mp["concrete_tint"])
        M["core"] = sc.make_pbr(
            stage, "/World/Looks/Core", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), scl["concrete_wall"],
            tint=mp["core_tint"])
        M["asphalt"] = sc.make_pbr(
            stage, "/World/Looks/Asphalt", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            scl["plaza_lower"], tint=mp["asphalt_tint"])
        M["curb"] = sc.make_pbr(
            stage, "/World/Looks/Curb", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"), sc.tex_path("granite_dark", "rough"),
            scl["granite_dark"])
        M["line"] = sc.make_pbr(stage, "/World/Looks/Line",
                                diffuse_color=mp["line_color"],
                                roughness_const=0.6, metallic=0.0)
        M["basement"] = sc.make_pbr(stage, "/World/Looks/Basement",
                                    diffuse_color=mp["basement_color"],
                                    roughness_const=0.9, metallic=0.0)
        # 지하 형광등 발광 재질 [A-13①]
        ga = PARAMS["garage"]
        M["glow"] = sc.make_pbr(stage, "/World/Looks/Glow",
                                diffuse_color=ga["color"],
                                roughness_const=0.6, metallic=0.0)
        _add_emission(stage, "/World/Looks/Glow", ga["color"], ga["intensity"])
        M["brick"] = sc.make_pbr(
            stage, "/World/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            scl["brick_red"])
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            scl["grass"], tint=mp["grass_tint"])
        M["glass"] = sc.make_pbr(stage, "/World/Looks/Glass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        M["parapet"] = sc.make_pbr(stage, "/World/Looks/Parapet",
                                   diffuse_color=mp["parapet_color"],
                                   roughness_const=mp["parapet_rough"])
        M["steel"] = sc.make_pbr(stage, "/World/Looks/Steel",
                                 diffuse_color=mp["steel_color"],
                                 metallic=mp["steel_metallic"],
                                 roughness_const=mp["steel_rough"])
        M["booth"] = sc.make_pbr(stage, "/World/Looks/Booth",
                                 diffuse_color=mp["booth_color"],
                                 roughness_const=mp["booth_rough"])
        M["signface"] = sc.make_pbr(stage, "/World/Looks/SignFace",
                                    diffuse_color=mp["signface_color"],
                                    roughness_const=0.6)
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=0.85)
        M["leaf_a"] = sc.make_pbr(stage, "/World/Looks/LeafA",
                                  diffuse_color=mp["leaf_a"],
                                  roughness_const=0.9)
        M["leaf_b"] = sc.make_pbr(stage, "/World/Looks/LeafB",
                                  diffuse_color=mp["leaf_b"],
                                  roughness_const=0.9)
        for ci, col in enumerate(PARAMS["lot"]["car_colors"]):
            M[f"car{ci}"] = sc.make_pbr(stage, f"/World/Looks/Car{ci}",
                                        diffuse_color=col, metallic=0.7,
                                        roughness_const=0.35)
        return M

    # -------------------------------------------------------------------
    # 램프 헬릭스 상면 z(a) — 진입 개구·브리지 유효고·기둥 높이 산출 공용
    # -------------------------------------------------------------------
    def ramp_z(a_deg):
        r = PARAMS["ramp"]
        t = (a_deg - r["a0"]) / (r["a1"] - r["a0"])
        return r["z0"] + (r["z1"] - r["z0"]) * t

    # -------------------------------------------------------------------
    # 램프 + 계단 + 코어 + 지하 슬래브
    # -------------------------------------------------------------------
    def build_structure(M):
        r = PARAMS["ramp"]
        # 램프 슬래브 — 반경방향 bands 개로 분할(감사 B-13-5 방사 슬릿 축소).
        #   각 밴드의 상면 중앙 z 는 동일하므로 이음부 단차는 ≈5 mm(중앙선이 덮음).
        nb = int(r.get("bands", 1))
        dr = (r["r_out"] - r["r_in"]) / nb
        for b in range(nb):
            sc.build_helix_ramp(stage, f"/World/Scene13/Ramp_b{b}", cx, cy,
                                r["r_in"] + dr * b, r["r_in"] + dr * (b + 1),
                                r["a0"], r["a1"], r["seg"],
                                r["z0"], r["z1"], r["thick"], M["concrete"])
        s = PARAMS["stair"]
        sc.build_helix_steps(stage, "/World/Scene13/Stair", cx, cy,
                            s["r_in"], s["r_out"], s["a0"], s["step_deg"],
                            s["n"], s["riser"], s["z0"], M["concrete"],
                            base_drop=s["base_drop"])
        co = PARAMS["core"]
        sc.add_cylinder(stage, "/World/Scene13/Core",
                        (cx, cy, (co["z_top"] + co["z_bot"]) / 2.0),
                        co["r"], co["z_top"] - co["z_bot"], M["core"],
                        collider=True)
        bm = PARAMS["basement"]
        sc.add_cylinder(stage, "/World/Scene13/Basement",
                        (cx, cy, bm["top_z"] - bm["thick"] / 2.0),
                        bm["r"], bm["thick"], M["basement"], collider=True)
        # 지하 외주벽 — 슬래브 림 바깥 허공 폐쇄
        gw = PARAMS["garage_wall"]
        sc.build_arc_steps(stage, "/World/Scene13/GarageWall", cx, cy,
                           gw["r_in"], gw["r_out"], 0.0, 360.0, gw["seg"],
                           gw["top_z"], gw["base_z"], M["basement"])
        build_entry(M)
        # 지하 천장 발광 스트립 + 실면광원 + 콘크리트 기둥 [A-13①·B-13-3]
        ga = PARAMS["garage"]
        for si, st in enumerate(ga["strips"]):
            sc.add_box(stage, f"/World/Scene13/CeilStrip_{si}",
                       (cx + st["cx"], cy + st["cy"], st["z"]),
                       (st["sx"], st["sy"], ga["strip_t"]), M["glow"])
            if ga.get("arealight"):
                _add_rectlight(stage, f"/World/Scene13/GarageLight_{si}",
                               (cx + st["cx"], cy + st["cy"],
                                st["z"] - ga["strip_t"] / 2.0 - 0.01),
                               st["sx"], st["sy"], ga["color"],
                               ga["light_intensity"])
        for ci, az in enumerate(ga["col_az"]):
            rad = math.radians(az)
            px = cx + ga["col_rad"] * math.cos(rad)
            py = cy + ga["col_rad"] * math.sin(rad)
            z1 = ramp_z(az) - r["thick"]        # 그 방위의 램프 하면까지
            sc.add_cylinder(stage, f"/World/Scene13/Column_{ci}",
                            (px, py, (ga["col_z0"] + z1) / 2.0),
                            ga["col_r"], z1 - ga["col_z0"],
                            M["core"], collider=True)

    # -------------------------------------------------------------------
    # 진입부 [감사 A-13-1/2/3] — 램프 종단벽 · 보행 브리지 · 계단 상단 참
    # -------------------------------------------------------------------
    def build_entry(M):
        en = PARAMS["entry"]
        # ① 램프 상단 종단벽: a=0 끝면 아래는 2회전째 램프(−2.56)까지 허공
        ew = en["endwall"]
        sc.build_arc_steps(stage, "/World/Scene13/RampEndWall", cx, cy,
                           ew["r_in"], ew["r_out"], ew["a0"], ew["a1"],
                           ew["seg"], ew["top_z"], ew["base_z"], M["curb"])
        # ② 보행 브리지: 광장(r 9.6) → 계단참. 하부 램프 대비 유효고 ≈2.14 m
        br = en["bridge"]
        sc.build_arc_steps(stage, "/World/Scene13/PedBridge", cx, cy,
                           br["r_in"], br["r_out"], br["a0"], br["a1"],
                           br["seg"], br["top_z"], br["base_z"], M["concrete"])
        # 브리지 양측 방사 파라펫 — build_arc_steps(seg=1, 미소 각폭)로 방사 박스
        for tag, a in (("A", br["a0"]), ("B", br["a1"])):
            sc.build_arc_steps(stage, f"/World/Scene13/PedBridgeRail{tag}",
                               cx, cy, br["r_in"], br["r_out"],
                               a - 0.3, a + 0.3, 1, br["top_z"] +
                               br["parapet_h"], br["top_z"], M["curb"])
        # ③ 계단 상단 참(a −24..0) — 계단 1단(top −0.16)에 riser 0.16 으로 접속
        la = en["landing"]
        sc.build_arc_steps(stage, "/World/Scene13/StairLanding", cx, cy,
                           la["r_in"], la["r_out"], la["a0"], la["a1"],
                           la["seg"], la["top_z"], la["base_z"], M["concrete"])

    # -------------------------------------------------------------------
    def _add_rectlight(stage_, path, center, w, h, color, intensity):
        """천장 형광등 실광원(RectLight, 기본 −Z 방향). 감사 B-13-3 —
        OmniPBR emissive 만으로는 PT 에서 조명 기여가 없다."""
        from pxr import UsdGeom, UsdLux, Gf
        lt = UsdLux.RectLight.Define(stage_, path)
        lt.CreateWidthAttr(float(w))
        lt.CreateHeightAttr(float(h))
        lt.CreateColorAttr(Gf.Vec3f(*color))
        lt.CreateIntensityAttr(float(intensity))
        UsdGeom.Xformable(lt).AddTranslateOp().Set(
            Gf.Vec3d(*[float(c) for c in center]))
        return lt

    # -------------------------------------------------------------------
    # 지상 진입 광장(아스팔트) — 램프 원형 개구를 링+4박스로 분할(§3)
    # -------------------------------------------------------------------
    def build_plaza(M, hazard):
        p = PARAMS["plaza"]
        top, th = p["z_top"], p["thick"]
        if not hazard:
            sc.add_box(stage, "/World/Scene13/PlazaFlat",
                       ((p["x0"] + p["x1"]) / 2.0, (p["y0"] + p["y1"]) / 2.0,
                        top - th / 2.0),
                       (p["x1"] - p["x0"], p["y1"] - p["y0"], th),
                       M["asphalt"], collider=True)
            return
        rg = PARAMS["ring"]
        sc.build_arc_steps(stage, "/World/Scene13/PlazaRing", cx, cy,
                           rg["r_in"], rg["r_out"], 0.0, 360.0, rg["seg"],
                           rg["top_z"], rg["base_z"], M["asphalt"])
        half = rg["r_out"] / math.sqrt(2.0)
        sx0, sx1 = cx - half, cx + half
        sy0, sy1 = cy - half, cy + half
        ov = 0.05

        def slab(tag, x0, x1, y0, y1):
            sc.add_box(stage, f"/World/Scene13/Plaza_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, top - th / 2.0),
                       (x1 - x0, y1 - y0, th), M["asphalt"], collider=True)
        slab("W", p["x0"], sx0, p["y0"], p["y1"])
        slab("E", sx1, p["x1"], p["y0"], p["y1"])
        slab("N", sx0 - ov, sx1 + ov, sy1, p["y1"])
        slab("S", sx0 - ov, sx1 + ov, p["y0"], sy0)

    # -------------------------------------------------------------------
    # 드레싱 — 원경 건물 1 (지평 폐쇄)
    # -------------------------------------------------------------------
    def build_dressing(M):
        # 지평 폐쇄 건물 4동 — 광장(±110) 안이므로 base_z 기본 0.0 그대로 착지
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"/World/Scene13/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"])
        L = PARAMS["lot"]
        R = "/World/Scene13"
        bm_top = PARAMS["basement"]["top_z"]
        # --- 진입 캐노피 · 차단기 · 요금부스 · 높이제한바 · 안내표지 ---
        cp = L["canopy"]
        sc.build_canopy(stage, f"{R}/Canopy", cp["x0"], cp["x1"], cp["y0"],
                        cp["y1"], cp["z_roof"], cp["post_r"], M["concrete"],
                        M["steel"])
        gt = L["gate"]
        sc.add_cylinder(stage, f"{R}/GateBoom",
                        (gt["bar_x"], (gt["bar_y0"] + gt["bar_y1"]) / 2.0,
                         gt["bar_z"]), gt["bar_r"],
                        gt["bar_y1"] - gt["bar_y0"], M["steel"], rotX=90.0)
        sc.add_cylinder(stage, f"{R}/GatePedestal",
                        (gt["ped_x"], gt["ped_y"], gt["ped_h"] / 2.0),
                        gt["ped_r"], gt["ped_h"], M["steel"], collider=True)
        bo = L["booth"]
        sc.add_box(stage, f"{R}/TollBooth", (bo["cx"], bo["cy"], bo["h"] / 2.0),
                   (bo["sx"], bo["sy"], bo["h"]), M["booth"], collider=True)
        sc.add_box(stage, f"{R}/TollBoothWin",
                   (bo["cx"], bo["cy"] + bo["sy"] / 2.0 - 0.02, 1.60),
                   (bo["sx"] * 0.7, 0.06, 0.90), M["glass"])
        hb = L["hbar"]
        sc.add_box(stage, f"{R}/HeightBar", (hb["x"], hb["y"], hb["z"]),
                   (0.10, hb["span"], 0.30), M["steel"])
        for i, sgn in enumerate((-1.0, 1.0)):
            sc.add_cylinder(stage, f"{R}/HeightPost_{i}",
                            (hb["x"], hb["y"] + sgn * (hb["span"] / 2.0 + 0.05),
                             hb["post_h"] / 2.0), hb["post_r"], hb["post_h"],
                            M["steel"], collider=True)
        sg = L["sign"]
        sc.add_cylinder(stage, f"{R}/LotSignPole",
                        (sg["cx"], sg["cy"], sg["pole_h"] / 2.0),
                        sg["pole_r"], sg["pole_h"], M["steel"], collider=True)
        sc.add_box(stage, f"{R}/LotSignFace",
                   (sg["cx"], sg["cy"], sg["pole_h"] + sg["h"] / 2.0 - 0.1),
                   (0.08, sg["w"], sg["h"]), M["signface"])
        # --- 코어 = 계단실: 헤드하우스 + 문 + 진입 2단 + 지하 방화문 ---
        hh = PARAMS["headhouse"]
        co = PARAMS["core"]
        sc.add_box(stage, f"{R}/HeadHouse",
                   (cx, cy, co["z_top"] + hh["h"] / 2.0),
                   (hh["s"], hh["s"], hh["h"]), M["core"], collider=True)
        sc.add_box(stage, f"{R}/HeadHouseRoof",
                   (cx, cy, co["z_top"] + hh["h"] + hh["roof_t"] / 2.0),
                   (hh["s"] + 0.30, hh["s"] + 0.30, hh["roof_t"]), M["curb"])
        sc.add_box(stage, f"{R}/HeadHouseDoor",
                   (cx + hh["s"] / 2.0 - 0.02, cy,
                    co["z_top"] + hh["door_h"] / 2.0),
                   (0.08, hh["door_w"], hh["door_h"]), M["steel"])
        for i, (sx_, sy_, top) in enumerate(L["core_steps"]):
            sc.add_box(stage, f"{R}/CoreStep_{i}", (sx_, sy_, top / 2.0),
                       (0.90, 0.90, top), M["concrete"], collider=True)
        fd = L["firedoor"]
        for i, (dx, dy) in enumerate(L["firedoors"]):
            sc.add_box(stage, f"{R}/FireDoor_{i}",
                       (dx, dy, bm_top + fd["h"] / 2.0),
                       (fd["sx"], fd["sy"], fd["h"]), M["steel"])
        # --- 지하 주차구획선 + 차량 대용 박스 ---
        for i, (bx, by, blen) in enumerate(L["bays"]):
            sc.add_box(stage, f"{R}/BayLine_{i}", (bx, by, bm_top + 0.01),
                       (blen, 0.12, 0.02), M["line"])
        ca = L["car"]
        for i, (px, py, ci) in enumerate(L["cars"]):
            mtl = M[f"car{ci}"]
            z0 = bm_top + ca["lift"]
            sc.add_box(stage, f"{R}/Car_{i}/Body",
                       (px, py, z0 + ca["body_h"] / 2.0),
                       (ca["sx"], ca["sy"], ca["body_h"]), mtl)
            sc.add_box(stage, f"{R}/Car_{i}/Cabin",
                       (px, py, z0 + ca["body_h"] + ca["cabin_h"] / 2.0),
                       (ca["cabin_sx"], ca["cabin_sy"], ca["cabin_h"]), mtl)
            for wi, (wx, wy) in enumerate(
                    ((ca["sx"] / 2.0 - 0.75, ca["sy"] / 2.0),
                     (ca["sx"] / 2.0 - 0.75, -ca["sy"] / 2.0),
                     (-ca["sx"] / 2.0 + 0.75, ca["sy"] / 2.0),
                     (-ca["sx"] / 2.0 + 0.75, -ca["sy"] / 2.0))):
                sc.add_cylinder(stage, f"{R}/Car_{i}/Wheel_{wi}",
                                (px + wx, py + wy, bm_top + ca["wheel_r"]),
                                ca["wheel_r"], ca["wheel_t"], M["basement"],
                                rotX=90.0)
        # --- 지상 광장 맥락: 볼라드 열(개구 경계) · 나무 · 화단 · 벤치 ---
        for i, az in enumerate(L["bollard_az"]):
            rad = math.radians(az)
            sc.build_bollard(stage, f"{R}/Bollard_{i}",
                             cx + L["bollard_r"] * math.cos(rad),
                             cy + L["bollard_r"] * math.sin(rad), 0.0)
        for i, (tx, ty) in enumerate(L["trees"]):
            sc.build_tree(stage, f"{R}/Tree_{i}", tx, ty, 0.0, M["wood"],
                          M["leaf_a"], M["leaf_b"])
        for i, (px, py) in enumerate(L["planters"]):
            sc.build_planter(stage, f"{R}/Planter_{i}", px, py, 0.0,
                             M["curb"], M["grass"], size=3.0)
        for i, (bx, by) in enumerate(L["benches"]):
            sc.build_bench(stage, f"{R}/Bench_{i}", bx, by, 0.0, M["wood"],
                           yaw=90.0)

    # -------------------------------------------------------------------
    # [v5 공통 레이어] 한글 사인 (cue_sign)
    # -------------------------------------------------------------------
    def build_signs():
        """sc.build_sign 배치. 차량 램프 진입구 옆 보행 금지 표지 = 낙차 인접
        설비 역추론 단서(계열①). 좌표·카메라 검산은 PARAMS['signs'] 주석."""
        back = sc.make_pbr(stage, "/World/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"/World/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"/World/Scene13/Sign_{tag}", cx, cy, bz,
                          yaw, panel, w=w, h=h, back_mtl=back)

    # -------------------------------------------------------------------
    # 단서 토글 (기하 불변) — 연석·중앙선(재질경계) / 외측 난간
    # -------------------------------------------------------------------
    def build_cues(M):
        r = PARAMS["ramp"]
        a_cue = PARAMS["entry"]["cue_a0"]        # 진입 개구 [A-13-1/2]
        seg_cue = max(4, int(round(r["seg"] * (r["a1"] - a_cue)
                                   / (r["a1"] - r["a0"]))))
        if cfg.get("cue_material_break"):
            cu = PARAMS["curb"]
            # 내측 연석은 전 구간(a0..a1) — 보행 계단측 경계.
            ri, ro = cu["inner"]
            sc.build_helix_ramp(
                stage, "/World/Scene13/CurbInner", cx, cy, ri, ro,
                r["a0"], r["a1"], r["seg"], r["z0"] + cu["z_off"],
                r["z1"] + cu["z_off"], cu["thick"], M["curb"], collider=False)
            # 외측 연석은 a_cue 부터 — a 0..22° 를 차량 진입 개구로 남긴다.
            ri, ro = cu["outer"]
            sc.build_helix_ramp(
                stage, "/World/Scene13/CurbOuter", cx, cy, ri, ro,
                a_cue, r["a1"], seg_cue, ramp_z(a_cue) + cu["z_off"],
                r["z1"] + cu["z_off"], cu["thick"], M["curb"], collider=False)
            cl = PARAMS["centerline"]
            sc.build_helix_ramp(
                stage, "/World/Scene13/CenterLine", cx, cy, cl["r_in"],
                cl["r_out"], r["a0"], r["a1"], r["seg"], r["z0"] + cl["z_off"],
                r["z1"] + cl["z_off"], cl["thick"], M["line"], collider=False)
        if cfg.get("cue_railing"):
            def _pipe_rail(tag, rad, a0, a1, nseg, npost):
                sc.build_helix_ramp(
                    stage, f"/World/Scene13/Rail{tag}", cx, cy, rad - 0.03,
                    rad + 0.03, a0, a1, nseg, ramp_z(a0) + 1.0,
                    ramp_z(a1) + 1.0, 0.05, M["rail"], collider=False)
                for k in range(npost + 1):
                    a = a0 + (a1 - a0) * k / npost
                    px = cx + rad * math.cos(math.radians(a))
                    py = cy + rad * math.sin(math.radians(a))
                    sc.add_cylinder(stage,
                                    f"/World/Scene13/Rail{tag}/Post_{k}",
                                    (px, py, ramp_z(a) + 0.5), 0.03, 1.0,
                                    M["rail"])
            # 외측: 진입 개구(a<a_cue) 를 비우고 시작
            _pipe_rail("Outer", r["r_out"], a_cue, r["a1"], seg_cue, 23)
            # 내측 [감사 A-13-4]: a=240° 에서 계단 최하단까지 1.49 m, 이후
            #   지하 슬래브까지 최대 1.54 m 낙차가 연석 0.10 만으로 무방호였다.
            _pipe_rail("Inner", r["r_in"] + 0.05, r["a0"], r["a1"],
                       r["seg"], 25)
        if cfg.get("cue_tactile"):
            tac = sc.make_pbr(stage, "/World/Looks/Tactile",
                              diffuse_color=(0.85, 0.72, 0.10),
                              roughness_const=0.7)
            # 계단 상단 참(a −24..0, r 4.45..6.0) 위 경고띠로 재배치
            sc.build_tactile(stage, "/World/Scene13/Tactile",
                             cx + 4.7, cx + 5.6, cy - 1.9, cy - 0.8, tac, z=0.0)
        if cfg.get("cue_nosing"):
            s = PARAMS["stair"]
            nos = sc.make_pbr(stage, "/World/Looks/Nosing",
                              diffuse_color=(0.85, 0.72, 0.10),
                              roughness_const=0.7)
            for i in range(s["n"]):
                a0 = s["a0"] + i * s["step_deg"]
                top = s["z0"] - (i + 1) * s["riser"]
                sc.build_arc_steps(stage, f"/World/Scene13/Nosing_{i}", cx, cy,
                                   s["r_out"] - 0.06, s["r_out"], a0,
                                   a0 + s["step_deg"], 1, top + 0.004,
                                   top - 0.02, nos, collider=False)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hazard = cfg["hazard_stairs"]
    build_plaza(M, hazard)
    if hazard:
        build_structure(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if hazard:
        build_cues(M)          # 나선 기하가 없으면 연석·난간도 없다(부유 방지)
    if cfg.get("cue_sign"):
        build_signs()          # [v5 공통 레이어]
    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        nprim = sum(1 for pr in stage.Traverse() if pr.IsA(UsdGeom.Gprim))
        print(f"SMOKE_OK prims={nprim}")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

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

    VIEWS = build_views()
    _v0 = VIEWS["ramp_vs_stair"]
    look_from(_v0["eye"], _v0["tgt"])

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    if capture_mode:
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
                            set_render_mode, look_from)
        simulation_app.close()
        return

    from omni.kit.viewport.utility import get_active_viewport, \
        capture_viewport_to_file

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]

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
