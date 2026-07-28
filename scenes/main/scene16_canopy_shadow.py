# -*- coding: utf-8 -*-
"""
scene16_canopy_shadow.py — NegObs 인공씬 16호: 캐노피 그림자 계단 (Isaac Sim 4.5)

유형    : T20 캐노피 계단 (T3의 반전 — 상부 그림자 밴드가 위험 신호)
사양서  : Docs/multi_scene_brief_v3.md §D scene16_canopy_shadow
공통    : scene_common.py (검증된 API 헬퍼) · scene02_underpass.py (도시계 골격)

위험 본질: 밝은 보도 한복판에 하강 계단(14단)이 있고, 그 위를 솔리드 캐노피가
           덮는다. 정오광에서 계단 전체가 캐노피 그림자에 잠겨 어두운 밴드로
           읽히고 — T3(하부 암부)의 반전으로, 위에 뜬 **상부 그림자 밴드**가
           낙차의 위험 신호가 된다. cue_nosing 황색 띠가 암부 속 저대비로 잔존.
목표     : 밝은 보도(plaza_lower) + 하강 계단(plaza_light) + 캐노피(솔리드 지붕
           +기둥 4) + 하부 통로 + 화단·건물을 조립, 렌더로 판정 (렌더 전용).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene16_canopy_shadow.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python scene16_canopy_shadow.py
스모크 조기종료:        NEGOBS_SMOKE=1  python scene16_canopy_shadow.py

좌표계: Z-up, m, 진행축 +X, 낙차 시작 모서리 = x=0.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hazard_stairs 만 기하 토글(False→피트 평지 메움).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 피트/계단/통로를 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        True,   # 계단 양측 경사 레일 + 피트 지상 둘레 난간
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)   # 점형 점자블록: 상단 경고띠 + 하부 통로
    "cue_material_break": True,   # False → 계단·통로도 보도재(plaza_lower)로 통일
    "cue_nosing":         True,   # 전 단 황색 논슬립 띠 (암부 속 저대비 — 특색)
    "cue_sign":           True,   # [v5 공통 레이어] sign_exit(지하보도 출구) 1매
    "cue_scene_dressing": True,   # 화단·건물·원경 비스타 일괄
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    walk=dict(x_w=-12.0, x_e=22.0, y_s=-8.0, y_n=8.0, z_top=0.0, thick=0.5),
    # 하강 피트(트렌치): 계단 폭 3 (y ±1.5), 벽 외면 ±1.8
    pit=dict(x0=0.0, x1=4.48, y0=-1.5, y1=1.5),
    # 계단 14단 × riser 0.15 · tread 0.32 → 낙차 2.1m, run 4.48m
    stairs=dict(x0=0.0, riser=0.15, tread=0.32, nsteps=14,
                y0=-1.5, y1=1.5, z_top=0.0, base_z=-2.6),
    # 하부 통로 (plaza_lower), +X로 이어져 동측 출구 계단으로 올라온다.
    passage=dict(x0=4.48, x1=14.0, z_top=-2.1, base_z=-2.6),
    # [감사v4 A1] 동측 출구 계단 — 종전엔 x=14 에 전폭 막음벽(Wall_E)이 있어
    #   2.1 m 내려가 9.5 m 걷고 탈출구가 없는 막다른 골목이었다.
    #   rot_group 180°(pivot x=(14+18.48)/2) 안에 하강 계단을 지어 상승
    #   계단으로 매핑: 로컬 x=14(z=0) → 월드 x=18.48, 로컬 x=18.48(z=-2.1) →
    #   월드 x=14.0 (통로 상면과 flush). 이로써 씬이 "지하보도"로 완결된다.
    east_stairs=dict(x0=14.0, riser=0.15, tread=0.32, nsteps=14,
                     y0=-1.5, y1=1.5, z_top=0.0, base_z=-2.6),
    east_rail=dict(y=1.4, x_start=13.5),
    # 벽·트렌치 동단 = 동측 계단 상단 (14.0 + 14*0.32 = 18.48)
    wall=dict(thick=0.3, y_in=1.5, parapet_top=0.15, base_z=-2.6, x1=18.48),

    # 캐노피: 계단 전체(x 0..4.48) + 상단 1m(x -1) 덮음. 지붕 z=2.6, 기둥 4.
    canopy=dict(x0=-1.0, x1=4.6, y0=-2.0, y1=2.0, z_roof=2.6, post_r=0.13,
                roof_t=0.14, base_z=-0.05),

    # cue
    # [감사v4 B1] perim_rail y 1.9 → 1.65. y=1.9 는 파라펫(y 1.5..1.8) 밖이라
    #   포스트 하단(z=0.15)과 보도(z=0) 사이 15 cm 공극이 생겼다. y=1.65 는
    #   파라펫 벽 중심선 → 포스트가 파라펫 상면(0.15)에 정확히 얹힌다.
    #   x1 4.48 → 18.48 : 트렌치 전 구간(동측 출구 계단 포함) 방호.
    perim_rail=dict(y=1.65, x0=0.0, x1=18.48, x_rear=None,
                    parapet_top=0.15, rail_h=0.9, post_r=0.03,
                    rail_r=0.03, rail_mid_r=0.018, mid_h=0.45, spacing=1.2),
    stair_rail=dict(y=1.4, x_start=-0.5, rail_h=0.9, post_r=0.02,
                    rail_r=0.03, rail_mid_r=0.018, rail_mid_drop=0.45,
                    spacing=1.2),
    tactile=dict(ahead=0.3, depth=0.3, proud=0.004, land_depth=0.4),
    nosing=dict(color=(0.85, 0.72, 0.10), width=0.05, proud=0.001),

    # 주변 대지 / 드레싱
    #   gx1 14.5 → 19.0 : 동측 출구 계단(x 14..18.48) 풋프린트도 잔디에서 비운다.
    ground=dict(size=140.0, z_top=-0.03, gx0=-0.5, gx1=19.0, gy0=-1.85, gy1=1.85),
    planters=[dict(name="A", cx=-4.0, cy=4.0, base_z=0.0),
              dict(name="B", cx=8.0, cy=-4.5, base_z=0.0),
              dict(name="C", cx=12.0, cy=5.0, base_z=0.0),
              dict(name="D", cx=2.0, cy=6.5, base_z=0.0)],
    planter=dict(size=3.0, curb_h=0.45, curb_t=0.25, cap_over=0.05,
                 cap_h=0.05, grass_h=0.40),
    buildings=dict(
        # 원경 비스타 차단(+X 지평선): 파사드 -X평면
        C=dict(x0=26.0, x1=32.0, y0=-12.0, y1=12.0, h=12.0, floors=4,
               axis="x", facade_x=26.0, face_dir=-1.0),
        # -X 지평선도 폐쇄 (종전엔 한쪽만 막혀 반대편이 텅 빈 지평선)
        D=dict(x0=-30.0, x1=-24.0, y0=-14.0, y1=14.0, h=15.0, floors=5,
               axis="x", facade_x=-24.0, face_dir=1.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),

    # --- 맥락 드레싱 (cue_scene_dressing) : "지하보도 입구가 있는 도심 광장" ---
    # 출입구 사인 게이트 (문형 표지) — 개구 상단을 가로지른다
    # [v5.1 현실성·치명] 피드백 "청색 사인 패널이 공중에 떠 있다 — 왜 위에?"
    #   원인: 구 Gate/Beam 은 (x −1.2, **y 0**, z 2.55) 에 크기 (2.4, 0.15, 0.45)
    #   인 박스였다. 즉 **X 방향으로 2.4 m 누운 판**이 개구 한복판 상공에 놓여
    #   있었고, 기둥은 y ±2.0 이라 판과 기둥이 물리적으로 닿지 않는다 →
    #   구조적 지지가 없는 부유 청색 패널.
    #   해결: 보(beam)를 **기둥을 잇는 진짜 인방**으로 바꾼다. Y 로 4.12 m
    #   (= 2·(y_half + post/2), 두 기둥 바깥면까지) 뻗고 두께는 X 0.22,
    #   상면(z 2.60)을 기둥 머리와 플러시로 맞춘다 → 문형(portal) 폐합.
    #   이 인방 자체가 개구 상단 부착형 표지 밴드(gate 재질=감청)가 되므로
    #   별도 부유 패널은 두지 않는다. 한글 안내는 N-4 의 sign_exit(측면 지주식,
    #   −1.6, 2.6) 1매로 통합 — 사인 중복 없음.
    gate=dict(x=-1.2, y_half=2.0, post=0.12, post_h=2.6,
              beam_t=0.22, beam_h=0.40, beam_top=2.60),
    # [v5.1 §2] 볼라드 규정화 — 구: 트렌치 양옆 y ±3.2 에 x 2.5 m 간격 6본
    #   (개구를 따라 늘어선 **장식열**. 차량 진입 지점과 무관, 간격 규정 위반).
    #   신: 동측 출구 계단 상단(x 18.48) 밖 **보도 진입부 1열**(x 20.5)에
    #   간격 1.5 m·중앙 1.5 m 개구(휠체어 통과)로 6본. 점형블록은 보행자
    #   접근면(서측) 전면 0.3 m(x 20.2..20.5).
    #   카메라: 전 프리셋(eye x ≤ −0.5, +X 응시)에서 21~30 m 원경 —
    #   근접 차폐 0, 판정 대상(계단·캐노피 암부, x 0..4.6)과 무관.
    bollards=dict(x=20.5, ys=(-3.75, -2.25, -0.75, 0.75, 2.25, 3.75),
                  block=dict(x0=20.2, x1=20.5, y0=-4.05, y1=4.05)),
    benches=[(-5.0, 5.5, 180.0), (-5.0, -5.5, 0.0), (9.0, 5.0, 180.0)],
    streetlights=[(-3.0, 6.5), (9.0, -6.5)],
    streetlight=dict(pole_h=5.0, pole_r=0.07, arm_len=0.9, arm_r=0.04,
                     head=0.24),
    hedges=[(-12.0, 6.5, -9.0, 7.3), (14.0, -7.3, 18.0, -6.5)],
    # 보도 포장 밴드 2줄 (광장 스케일 지시)
    walk_bands=dict(ys=(-6.0, 6.0), width=0.45, z=0.007),
    # [v5 공통 레이어] 한글 사인 — (태그, TEX 키, cx, cy, base_z, yaw, w, h)
    #   Exit(−1.6, 2.6): 지하보도 진입부 출구 표지. 트렌치 개구(y ±1.5)에서
    #     1.10 m, 옹벽 외면(y ±1.8)에서 0.80 m — 위험 기하 이격 ≥0.5 m 충족.
    #     사인 게이트 기둥(x −1.2, y ±2.0, r 0.12) 에서 0.57 m, 볼라드
    #     (−1.0, 3.2) 에서 0.92 m, 캐노피(x −1.0..4.6) 서측 밖.
    #   카메라 검산(그리드 gy=0, eye x −2/−5/−10, 화각 ±30°):
    #     −2 → 81.3° 밖(거리 2.63 m 측방) · −5 → 37.4° 밖 · −10 → 17.2°(8.81 m)
    #     approach(−7,0) 25.7°(프레임 가장자리) · shadow_band(−5,0) 37.4° 밖 ·
    #     under_canopy(−0.5,0) 후방 · beauty_overview(−7,−5) 23.6° 가장자리
    #     → 계단·암부 판정 대상(화면 중앙)을 가리지 않는다.
    signs=[("Exit", "sign_exit", -1.6, 2.6, 0.0, 180.0, 0.9, 0.45)],

    material=dict(
        scale=dict(plaza_lower=0.7, plaza_light=0.75, grass=4.0,
                   brick_red=2.0, tactile=0.3),
        grass_tint=(0.55, 0.68, 0.42),
        roof_color=(0.72, 0.72, 0.74), roof_rough=0.55,     # 밝은 회색 지붕
        post_color=(0.55, 0.55, 0.58), post_metallic=0.5, post_rough=0.5,
        wall_tint=(0.85, 0.85, 0.86),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # [v5.1 §4] 파라펫 0.90 → 0.72 (순백 대면적 금지)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # 드레싱용 어두운 상수색 (알베도 0.02~0.06 규약)
        band_color=(0.05, 0.05, 0.055), band_rough=0.7,
        gate_color=(0.03, 0.05, 0.09), gate_rough=0.45,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
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
    # ─── SUN_AZ_OFFSET: 이 씬의 특색(캐노피 그림자가 계단을 덮음)을 좌우하는
    #     핵심 파라미터. 감독 r1 C-16: 171.5→146.5. 태양 매핑 월드 az ≈
    #     33.5+offset = 180 → 그림자 az = az−180 = 0 → 지붕(z=2.6, 정오 고도
    #     elev≈49.79°) 그림자가 +X(계단 하강 방향)로 밀려 피트 개구·계단 전체를
    #     덮는다. 그림자-계단 정합은 감독이 렌더로 재판정.
    #     [ ]키(dome_rotation_step 15°)로 GUI에서 추가 스윕 가능. ───
    SUN_AZ_OFFSET=146.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene16")

ASSET_ROLES = ["plaza_lower", "plaza_light", "grass", "tactile",
               "brick_red", "sign_exit", "hdri", "mdl"]   # [v5] sign_exit


def build_views():
    """카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷."""
    views = sc.grid_views(0.0)
    # approach: 밝은 보도에서 계단·캐노피로 접근 (상부 그림자 밴드 인상)
    views["approach"] = dict(eye=[-7.0, 0.0, 1.6], tgt=[3.0, 0.0, -0.6])
    # shadow_band: 낮은 시점 — 밝은 보도 위 계단만 어두운 밴드
    views["shadow_band"] = dict(eye=[-5.0, 0.0, 0.35], tgt=[4.0, 0.0, -0.4])
    # under_canopy: 계단 위에서 캐노피 아래 암부·하부 통로 내려봄
    views["under_canopy"] = dict(eye=[-0.5, 0.0, 1.7], tgt=[4.5, 0.0, -1.6])
    # beauty_overview: 사선 부감 인상
    views["beauty_overview"] = dict(eye=[-7.0, -5.0, 3.2], tgt=[3.0, 1.0, -1.0])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach / beauty  — 밝은 보도·하강 계단·캐노피(지붕+기둥4) 식별
 2. shadow_band·h0.3   — 계단 전체가 캐노피 그림자로 어두운 밴드가 되는가(특색)
 3. under_canopy       — 암부 속 황색 노징이 저대비로 잔존하는가
 4. cue ON vs OFF      — nosing/railing/tactile 토글 시 기하 트랜스폼 불변
 5. 재질·태양방위      — [ ]키로 그림자가 계단을 덮는 방위 확인·Z파이팅 없는가
 6. [v4] 동측 출구 계단(x14→18.48 상승)·둘레난간 파라펫 접지·사인 게이트
 7. [v5] 공통 레이어 — 점자띠(상단·하부) + sign_exit(진입부 y +2.6) 판독"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene16")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene16"

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
        M["walk"] = PBR(
            f"{ROOT}/Looks/Walk", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"])
        M["stair"] = PBR(
            f"{ROOT}/Looks/Stair", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"])
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"], tint=mp["wall_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        M["roof"] = PBR(f"{ROOT}/Looks/Roof", diffuse_color=mp["roof_color"],
                        roughness_const=mp["roof_rough"], metallic=0.0)
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # [v5.1 §2/§4] 규정 볼라드용 재질 — 본체 3종(틴트 지터 ±5%) + 반사띠.
        #   반사띠는 소면적이므로 고휘도 허용(순백 대면적 금지 규약과 무관).
        for _i, _f in enumerate((0.95, 1.0, 1.05)):
            M[f"bollard_{_i}"] = PBR(
                f"{ROOT}/Looks/Bollard_{_i}",
                diffuse_color=tuple(min(c * _f, 1.0) for c in mp["rail_color"]),
                metallic=mp["rail_metallic"],
                roughness_const=mp["rail_rough"] * (1.0 + 0.05 * (_i - 1)))
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=(0.86, 0.86, 0.84),
                                roughness_const=0.35)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"])
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"])
        M["band"] = PBR(f"{ROOT}/Looks/Band", diffuse_color=mp["band_color"],
                        roughness_const=mp["band_rough"])
        M["gate"] = PBR(f"{ROOT}/Looks/Gate", diffuse_color=mp["gate_color"],
                        roughness_const=mp["gate_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        return M

    # -------------------------------------------------------------------
    # 대지 — 잔디 base(피트 풋프린트 4박스 제거) : 공동을 덮지 않음
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        cz = g["z_top"] - 0.25
        th = 0.5
        H = g["size"] / 2.0
        gx0, gx1 = g["gx0"], g["gx1"]
        gy0, gy1 = g["gy0"], g["gy1"]
        BOX(f"{ROOT}/Grass_W", ((-H + gx0) / 2.0, 0.0, cz),
            (gx0 + H, g["size"], th), M["grass"])
        BOX(f"{ROOT}/Grass_E", ((gx1 + H) / 2.0, 0.0, cz),
            (H - gx1, g["size"], th), M["grass"])
        BOX(f"{ROOT}/Grass_S", ((gx0 + gx1) / 2.0, (-H + gy0) / 2.0, cz),
            (gx1 - gx0, gy0 + H, th), M["grass"])
        BOX(f"{ROOT}/Grass_N", ((gx0 + gx1) / 2.0, (gy1 + H) / 2.0, cz),
            (gx1 - gx0, H - gy1, th), M["grass"])

    # -------------------------------------------------------------------
    # 지상 보도 — 트렌치(x 0..14, 벽 외면 ±1.8) 둘레: 서 + 남·북 플랭크
    # -------------------------------------------------------------------
    def build_walk(M):
        w = PARAMS["walk"]
        p = PARAMS["pit"]
        wl = PARAMS["wall"]
        top, th = w["z_top"], w["thick"]
        cz = top - th / 2.0
        y_out = p["y1"] + wl["thick"]            # 1.8
        x_tr1 = wl["x1"]                          # 트렌치 동쪽 끝 18.48
        # 서: x_w..0 전폭
        BOX(f"{ROOT}/Walk_W",
            ((w["x_w"] + p["x0"]) / 2.0, (w["y_s"] + w["y_n"]) / 2.0, cz),
            (p["x0"] - w["x_w"], w["y_n"] - w["y_s"], th), M["walk"], col=True)
        # 남: 트렌치 x구간, y_s..-y_out
        BOX(f"{ROOT}/Walk_S",
            ((p["x0"] + x_tr1) / 2.0, (w["y_s"] - y_out) / 2.0, cz),
            (x_tr1 - p["x0"], (-y_out) - w["y_s"], th), M["walk"], col=True)
        # 북: 트렌치 x구간, +y_out..y_n
        BOX(f"{ROOT}/Walk_N",
            ((p["x0"] + x_tr1) / 2.0, (y_out + w["y_n"]) / 2.0, cz),
            (x_tr1 - p["x0"], w["y_n"] - y_out, th), M["walk"], col=True)
        # 동: 트렌치 끝(x18.48 = 동측 계단 상단)..x_e 전폭
        BOX(f"{ROOT}/Walk_E",
            ((x_tr1 + w["x_e"]) / 2.0, (w["y_s"] + w["y_n"]) / 2.0, cz),
            (w["x_e"] - x_tr1, w["y_n"] - w["y_s"], th), M["walk"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 트렌치를 메워 전체 z=0 평지."""
        w = PARAMS["walk"]
        BOX(f"{ROOT}/FlatWalk",
            ((w["x_w"] + w["x_e"]) / 2.0, (w["y_s"] + w["y_n"]) / 2.0,
             w["z_top"] - w["thick"] / 2.0),
            (w["x_e"] - w["x_w"], w["y_n"] - w["y_s"], w["thick"]),
            M["walk"], col=True)

    # -------------------------------------------------------------------
    # 벽 + 계단 + 하부 통로
    # -------------------------------------------------------------------
    def build_walls(M):
        p = PARAMS["pit"]
        wl = PARAMS["wall"]
        y_out = wl["y_in"] + wl["thick"]          # 1.8
        y_ctr = (wl["y_in"] + y_out) / 2.0
        top = wl["parapet_top"]
        bot = wl["base_z"]
        cz = (top + bot) / 2.0
        hz = top - bot
        Lx = wl["x1"] - p["x0"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Wall_{tag}",
                ((p["x0"] + wl["x1"]) / 2.0, sgn * y_ctr, cz),
                (Lx, wl["thick"], hz), M["wall"], col=True)
        # (감사v4 A1) 동쪽 막음벽 Wall_E 삭제 — 대신 동측 출구 계단이 선다.

    def build_stairs(stair_mtl, passage_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)
        # 하부 통로
        pa = PARAMS["passage"]
        st = PARAMS["stairs"]
        BOX(f"{ROOT}/Passage",
            ((pa["x0"] + pa["x1"]) / 2.0, 0.0,
             (pa["z_top"] + pa["base_z"]) / 2.0),
            (pa["x1"] - pa["x0"], st["y1"] - st["y0"],
             pa["z_top"] - pa["base_z"]), passage_mtl, col=True)

    def build_east_exit(M, stair_mtl):
        """동측 출구 계단(상승) — rot_group 180°로 하강 계단을 미러링.
        로컬 x0(z=0)=14.0 → 월드 18.48(보도 상면), 로컬 끝(z=-2.1) → 월드
        14.0(통로 상면)과 flush. 노징·점자·난간도 같은 그룹 안에서 미러."""
        es = PARAMS["east_stairs"]
        run = es["tread"] * es["nsteps"]
        px = es["x0"] + run / 2.0                      # 16.24
        grp = sc.build_rot_group(stage, f"{ROOT}/EastExit", (px, 0.0), 180.0)
        sc.build_straight_stairs(
            stage, f"{grp}/Stairs", es["x0"], es["y0"], es["y1"],
            es["riser"], es["tread"], es["nsteps"], es["base_z"], stair_mtl,
            z_top=es["z_top"], collider=True)
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{grp}/Nosing", es["x0"], es["y0"], es["y1"],
                es["riser"], es["tread"], es["nsteps"], color=ns["color"],
                width=ns["width"], proud=ns["proud"], z_top=es["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{grp}/Tactile_East",
                             es["x0"] - tc["ahead"], es["x0"],
                             es["y0"], es["y1"], M["tactile"], z=0.0,
                             proud=tc["proud"])
        if cfg["cue_railing"]:
            er = PARAMS["east_rail"]
            sr = PARAMS["stair_rail"]

            def east_ground(x):
                if x <= es["x0"] + 1e-9:
                    return 0.0
                i = int((x - es["x0"]) / es["tread"]) + 1
                return -es["riser"] * min(max(i, 1), es["nsteps"])

            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                sc.build_railing_line(
                    stage, f"{grp}/EastRail_{tag}", sgn * er["y"],
                    er["x_start"], es["x0"], run,
                    es["riser"] * es["nsteps"], east_ground, M["rail"],
                    rail_h=sr["rail_h"], post_r=sr["post_r"],
                    spacing=sr["spacing"], rail_r=sr["rail_r"],
                    rail_mid_r=sr["rail_mid_r"],
                    rail_mid_drop=sr["rail_mid_drop"])

    # -------------------------------------------------------------------
    # 캐노피 (솔리드 지붕 + 기둥 4) — 계단 전체 + 상단 1m 덮음
    # -------------------------------------------------------------------
    def build_canopy(M):
        cp = PARAMS["canopy"]
        sc.build_canopy(stage, f"{ROOT}/Canopy", cp["x0"], cp["x1"],
                        cp["y0"], cp["y1"], cp["z_roof"], cp["post_r"],
                        M["roof"], M["post"], roof_t=cp["roof_t"],
                        base_z=cp["base_z"])

    # -------------------------------------------------------------------
    # 단서 (cue) — nosing / tactile / railing
    # -------------------------------------------------------------------
    def build_signs():
        """[v5 공통 레이어] 한글 사인(sc.build_sign). 지하보도 진입부 출구 표지 =
        낙차 인접 설비 역추론 단서(계열①). 좌표 검산은 PARAMS['signs'] 주석."""
        back = sc.make_pbr(stage, f"{ROOT}/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"{ROOT}/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, back_mtl=back)

    def build_cues(M, stair_mtl):
        st = PARAMS["stairs"]
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"],
                color=ns["color"], width=ns["width"], proud=ns["proud"],
                z_top=st["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            pa = PARAMS["passage"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["tactile"], z=0.0,
                             proud=tc["proud"])
            sc.build_tactile(stage, f"{ROOT}/Tactile_Land",
                             pa["x0"], pa["x0"] + tc["land_depth"],
                             st["y0"], st["y1"], M["tactile"],
                             z=pa["z_top"], proud=tc["proud"])
        if cfg["cue_railing"]:
            sr = PARAMS["stair_rail"]

            def stair_ground(x):
                if x <= 1e-9:
                    return 0.0
                return -st["riser"] * min(max(int(x / st["tread"]) + 1, 1),
                                          st["nsteps"])

            run = st["tread"] * st["nsteps"]
            drop = st["riser"] * st["nsteps"]
            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                sc.build_railing_line(
                    stage, f"{ROOT}/StairRail_{tag}", sgn * sr["y"],
                    sr["x_start"], st["x0"], run, drop, stair_ground,
                    M["rail"], rail_h=sr["rail_h"], post_r=sr["post_r"],
                    spacing=sr["spacing"], rail_r=sr["rail_r"],
                    rail_mid_r=sr["rail_mid_r"],
                    rail_mid_drop=sr["rail_mid_drop"])
            # 피트 지상 둘레 난간(남·북 가장자리, 계단 폭 구간)
            pr = PARAMS["perim_rail"]
            base_z = pr["parapet_top"]
            top_z = base_z + pr["rail_h"]
            mid_z = base_z + pr["mid_h"]

            def hrail(prefix, const_c, a0, a1):
                mid_c = (a0 + a1) / 2.0
                length = a1 - a0
                CYL(f"{prefix}/Top", (mid_c, const_c, top_z),
                    pr["rail_r"], length, M["rail"], rotY=90.0)
                CYL(f"{prefix}/Mid", (mid_c, const_c, mid_z),
                    pr["rail_mid_r"], length, M["rail"], rotY=90.0)
                ph = top_z - base_z
                n = 0
                a = a0 + pr["spacing"] / 2.0
                while a <= a1 - pr["spacing"] / 2.0 + 1e-6:
                    CYL(f"{prefix}/Post_{n}", (a, const_c, base_z + ph / 2.0),
                        pr["post_r"], ph, M["rail"])
                    a += pr["spacing"]
                    n += 1

            hrail(f"{ROOT}/PerimRail_S", -pr["y"], pr["x0"], pr["x1"])
            hrail(f"{ROOT}/PerimRail_N", pr["y"], pr["x0"], pr["x1"])

    # -------------------------------------------------------------------
    # 드레싱 — 화단 2 + 원경 건물
    # -------------------------------------------------------------------
    def build_bollard_std(M, prefix, cx, cy, bz, k=0):
        """[v5.1 §2] 규정 볼라드 1본 — 높이 0.90 m · 지름 0.15 m(r 0.075) +
        상단 백색 반사띠(폭 0.09). 근거: 교통약자의 이동편의 증진법 시행규칙
        별표2(높이 0.8~1.0 · 지름 0.1~0.2 · 간격 1.5 m 내외 · 밝은 반사띠).
        구 sc.build_bollard 기본값(r 0.06 · h 0.75)은 규정 하한 미달이라
        여기서 치수를 명시한다(scene_common 미수정). 본체 재질은 인스턴스별
        틴트 지터(bollard_0..2)로 '동일 복제' 인상을 뺀다."""
        h, r = 0.90, 0.075
        sc.build_bollard(stage, f"{prefix}/Post", cx, cy, bz,
                         mtl=M[f"bollard_{k % 3}"], radius=r, height=h)
        sc.add_cylinder(stage, f"{prefix}/Band", (cx, cy, bz + h - 0.14),
                        r * 1.05, 0.09, M["bollard_band"])

    def build_dressing(M):
        pl = PARAMS["planter"]
        for pdef in PARAMS["planters"]:
            sc.build_planter(
                stage, f"{ROOT}/Planter_{pdef['name']}", pdef["cx"], pdef["cy"],
                pdef["base_z"], M["curb"], M["grass"],
                tree_mtls=(M["wood"], M["canopy_a"], M["canopy_b"]),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"], grass_h=pl["grass_h"])
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        # 출입구 사인 게이트 — 개구 상단을 가로지르는 문형 표지("지하보도 입구")
        # [v5.1] 보를 기둥 사이를 실제로 잇는 인방으로 교체(부유 패널 제거).
        ga = PARAMS["gate"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Gate/Post_{tag}",
                (ga["x"], sgn * ga["y_half"], ga["post_h"] / 2.0),
                (ga["post"], ga["post"], ga["post_h"]), M["gate"], col=True)
        span = 2.0 * (ga["y_half"] + ga["post"] / 2.0)     # 4.12 (기둥 바깥면)
        BOX(f"{ROOT}/Gate/Beam",
            (ga["x"], 0.0, ga["beam_top"] - ga["beam_h"] / 2.0),
            (ga["beam_t"], span, ga["beam_h"]), M["gate"], col=True)
        # [v5.1 §2] 규정 볼라드 1열 (동측 보도 진입부) + 점형블록 0.3 m
        bl = PARAMS["bollards"]
        for i, by in enumerate(bl["ys"]):
            build_bollard_std(M, f"{ROOT}/Bollard_{i}", bl["x"], by, 0.0, k=i)
        # 점형블록은 '점자블록' 단서 계열이므로 cue_tactile 토글에 묶는다
        #   (OFF 컷에 토글 밖 황색 경고띠가 남지 않게 — 토글 무결성 유지).
        if cfg["cue_tactile"]:
            bk = bl["block"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Bollard",
                             bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                             M["tactile"], z=0.0,
                             proud=PARAMS["tactile"]["proud"])
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, 0.0,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (lx, ly, sl["pole_h"] / 2.0), sl["pole_r"],
                sl["pole_h"], M["post"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (lx + sgn * sl["arm_len"] / 2.0, ly, sl["pole_h"] - 0.1),
                    sl["arm_r"], sl["arm_len"], M["post"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (lx + sgn * sl["arm_len"], ly, sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        for i, (hx0, hy0, hx1, hy1) in enumerate(PARAMS["hedges"]):
            sc.build_hedge(stage, f"{ROOT}/Hedge_{i}", hx0, hy0, hx1, hy1,
                           0.8, base_z=0.0)
        # 보도 포장 밴드 2줄 (광장 스케일 지시) — 트렌치 밖 y=±6
        w = PARAMS["walk"]
        wb = PARAMS["walk_bands"]
        for i, by in enumerate(wb["ys"]):
            BOX(f"{ROOT}/WalkBand_{i}",
                ((w["x_w"] + w["x_e"]) / 2.0, by, wb["z"] - 0.01),
                (w["x_e"] - w["x_w"], wb["width"], 0.02), M["band"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["stair"] if cfg["cue_material_break"] else M["walk"]
    # 통로 재질: 밝은 보도재(plaza_lower)로 하부 톤 유지
    passage_mtl = M["walk"]

    build_ground(M)
    if cfg["hazard_stairs"]:
        build_walk(M)
        build_walls(M)
        build_stairs(stair_mtl, passage_mtl)
        build_east_exit(M, stair_mtl)
        build_canopy(M)
        build_cues(M, stair_mtl)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if cfg.get("cue_sign"):
        build_signs()               # [v5 공통 레이어]

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] scene16 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene16_{ts}.png")
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
