# -*- coding: utf-8 -*-
"""
scene20_diagonal_oblique.py — NegObs 인공씬 20호: 대각 사교 계단 (Isaac Sim 4.5)

유형    : T8 대각 사교 (정렬 가정 붕괴)
사양서  : Docs/multi_scene_brief_v3.md §D scene20_diagonal_oblique
공통    : scene_common.py (검증된 API 헬퍼) · scene01/scene02 (도시계 골격)

위험 본질: 광장 보행축(+X)에 대해 30° 틀어진 직선 계단. 정면 프리셋(축=보행축
           +X, 고정)에서 낙차 경계가 화면을 사선으로 가로지른다 — 계단이 보행
           방향과 정렬돼 있으리란 가정이 붕괴. 지평 폐쇄 건물은 축 정렬 그대로라
           대비가 강조된다.
목표     : 상부 광장(plaza_light+밴드, scene01 모티프 축소) + 30° rot_group 계단
           14단(폭 5) + 사선 연장 쐐기(광장-계단 flush 접합) + 하부 광장
           (plaza_lower 웜) + 잔디 채움(공동 없음) + 축정렬 건물 3·축정렬
           소품(볼라드 열·화단·벤치·가로등)을 조립, 렌더로 판정 (렌더 전용).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene20_diagonal_oblique.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python scene20_diagonal_oblique.py
스모크 조기종료:        NEGOBS_SMOKE=1  python scene20_diagonal_oblique.py

좌표계: Z-up, m, 보행축 +X(프리셋 고정), 낙차 시작 모서리 = 회전 전 x=0.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hazard_stairs 만 기하 토글(False→평지 통일).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 계단/하부광장 제거, 전체 z=0 평지
    "cue_railing":        True,   # 계단 양측 경사 레일 (rot_group 내 — 사선 따라)
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)   # 상단 경고띠 (rot_group 내 — 사선 따라)
    "cue_material_break": True,   # False → 계단·하부를 상부재(plaza_light)로 통일
    "cue_nosing":         False,  # (키 예약)
    "cue_sign":           False,  # [v5.2 사용자] 임의 경고 팻말 제거 — 배치 없음(키만 예약)
    "cue_scene_dressing": True,   # 밴드·축정렬 건물·잔디 일괄
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # 상부 광장(메사): plaza_light, x -14..-4.5, y -8..8. 상면 z=0, 계곡까지 솔리드.
    #   [감사v4 A2] x1 0.0 → -4.5. 축정렬 광장 에지가 계단 상단선(로컬 x=0 =
    #   월드 x=-0.5774·y 사선)보다 동쪽으로 넘어가면 북측(y>0) 윗단이 광장
    #   솔리드에 매몰돼 첫 단차가 최대 0.75 m까지 커진다. x1=-4.5 는
    #     ① |y|≤8 전 구간에서 광장 에지가 사선 서쪽에 머무는 한계값
    #        (사선 x = -0.5774·8 = -4.619 ≤ -4.5 는 y=8 에서만 0.12 m 초과 —
    #         그 지점은 계단 폭(로컬 |y|≤2.5) 밖 순수 절벽이라 보행 무관),
    #     ② 아래 wedge(로컬 |y|≤9)가 남는 영역을 빈틈없이 덮는 한계값
    #        (메사점은 lx≤0 ⇒ y ≤ -1.732x ⇒ ly = -0.5x+0.866y ≤ -2x ≤ 9)
    #   을 동시에 만족한다.
    upper=dict(x0=-14.0, x1=-4.5, y0=-8.0, y1=8.0, z_top=0.0, base_z=-2.2),
    # 상부 광장 사선 연장 쐐기 (rot_group 내부 — 동측 면 = 계단 상단선)
    wedge=dict(x0=-8.0, x1=0.0, y_half=9.0, z_top=0.0, base_z=-2.2),
    # 밴드는 축정렬 광장 위에만(x1 -0.6 → -5.0). 사선 에지와의 대비는 유지.
    band=dict(width=0.45, spacing=2.0, proud=0.0015, x0=-13.0, x1=-5.0,
              y_half=8.0),
    # 계단 14단 × riser 0.15 · tread 0.34 → 낙차 2.1m, run 4.76m. 폭 5 (y ±2.5).
    stairs=dict(x0=0.0, riser=0.15, tread=0.34, nsteps=14,
                y0=-2.5, y1=2.5, z_top=0.0, base_z=-2.6),
    # rot_group: pivot (0,0), 30° — 계단·하부광장을 함께 회전(경계 정합)
    rot=dict(pivot=(0.0, 0.0), deg=30.0),
    # 하부 광장(웜) — rot_group 내, 계단 끝(local x=4.76, z=-2.1)에서 이어짐
    lower=dict(x0=4.76, x1=18.0, y0=-2.5, y1=2.5, z_top=-2.1, thick=0.15),
    # 하부 잔디 base — 계곡 채움(공동 없음). rot 계단/광장 아래 전면 솔리드.
    valley=dict(size=100.0, z_top=-2.15, thick=1.0),

    stair_rail=dict(y=2.4, x_start=-0.4, rail_h=0.9, post_r=0.02,
                    rail_r=0.03, rail_mid_r=0.018, rail_mid_drop=0.45,
                    spacing=1.3),
    tactile=dict(ahead=0.3, depth=0.3, proud=0.004),

    # 축정렬 지평 폐쇄 건물 3 (회전 안 함 — 정렬 대비 강조)
    #   base_z=-2.15 : 계곡 잔디 상면. 미지정(0.0)이면 셸이 z=-1.0 까지만 내려와
    #   1.15 m 부유했다(감사v4 B3).
    buildings=dict(
        C=dict(x0=26.0, x1=32.0, y0=-14.0, y1=14.0, h=13.0, floors=4,
               axis="x", facade_x=26.0, face_dir=-1.0, base_z=-2.15),
        D=dict(x0=-6.0, x1=20.0, y0=16.0, y1=22.0, h=11.0, floors=4,
               axis="y", facade_y=16.0, face_dir=-1.0, base_z=-2.15),
        E=dict(x0=-40.0, x1=-32.0, y0=-16.0, y1=16.0, h=16.0, floors=5,
               axis="x", facade_x=-32.0, face_dir=1.0, base_z=-2.15),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.6, margin=2.0),

    # --- 맥락 드레싱 (cue_scene_dressing) : "관공서·대학 앞 도시 광장" ---
    #     축정렬 소품(밴드·건물·화단 열) vs 30° 사선 에지 대비가 이 씬의 주제다.
    #     상부 소품은 전부 메사(축정렬 광장 ∪ 쐐기) 위 — 좌표 검산 fixlog_I5 참조.
    # [v5.1 §2] 볼라드 규정화 — 구: x −1.2 에 y −7..1 을 2.0 m 등간격 5본 +
    #   산발 3본 = 총 8본. **사선 낙차 에지(로컬 x=0) 바로 앞을 따라 늘어선
    #   장식열**이라 §2(차량 진입 지점 한정)에 근거가 없고, 등간격 규약(§3)에도
    #   어긋난다. 지시 "사선 에지 자체를 따라 줄 세우지 말 것" 그대로 폐기.
    #   신: 실제 차량 접근 지점 2곳에만 **1열**씩(간격 1.5 m, 중앙 1.5 m 개구),
    #   각 열 보행자 접근면에 전면 0.3 m 점형블록.
    #     ① 메사 진입 램프 상단 (x −13.6, 램프 x −18..−14 폭 y ±2)
    #        → 그리드 eye(x −2/−5/−10)·미장센 전 프리셋의 **후방**(x < −10)
    #     ② 하부 광장 사선 복도 입구 (rot 로컬 lx 17.0, 광장 x1 18.0)
    #        → 월드 (14.72, 8.50). 그리드 eye 기준 방위 19~27°·거리 18.7~26 m
    #          원경, 판정 대상(사선 낙차 경계 x −4.6..0)과 무간섭.
    bollards=dict(x=-13.6, ys=(-2.25, -0.75, 0.75, 2.25),
                  block=dict(x0=-13.6, x1=-13.3, y0=-2.55, y1=2.55)),
    planters=[(-10.0, 5.5), (-10.0, -5.5), (-6.5, 6.2)],
    planter=dict(size=3.0),
    benches=[(-7.5, 6.6, 180.0), (-7.5, -6.6, 0.0),
             (-11.5, 3.0, 90.0), (-11.5, -3.0, -90.0)],
    streetlights=[(-7.0, 6.8), (-9.0, -6.8), (-12.5, 4.0)],
    streetlight=dict(pole_h=5.5, pole_r=0.07, arm_len=1.0, arm_r=0.04,
                     head=0.25),
    hedges=[(-14.0, 7.4, -9.0, 8.0), (-14.0, -8.0, -9.0, -7.4)],
    # 메사 진입 램프(서측) — "이 광장은 어떻게 올라가는가" (감사v4 A5)
    access_ramp=dict(x0=-18.0, x1=-14.0, y0=-2.0, y1=2.0, thick=2.6),
    # [v5.2 사용자] 임의 경고 팻말 제거 — 계단주의 사인(PARAMS['signs']) 삭제.
    # 하부 광장 소품 (rot_group 로컬 좌표, base_z=-2.1)
    # [v5.1 §2] 구: 계단 발치(lx 5.6/9.0)에 좌우 2쌍 = 사선 복도를 따라 세운
    #   장식 배치. → 복도 **입구**(lx 17.0) 1열로 이설 + 점형블록 전면 0.3 m.
    lower_bollards=dict(x=17.0, ys=(-2.25, -0.75, 0.75, 2.25),
                        block=dict(x0=16.7, x1=17.0, y0=-2.55, y1=2.55)),
    lower_benches=[(12.0, -1.85, 0.0), (12.0, 1.85, 0.0)],

    material=dict(
        scale=dict(plaza_light=0.75, band_dark=0.6, plaza_lower=0.7,
                   grass=4.0, brick_red=2.0, tactile=0.3),
        lower_warm_tint=(1.06, 1.0, 0.94),
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # [v5.1 §4] 파라펫 0.90 → 0.72 (순백 대면적 금지)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        # 드레싱용 (어두운 상수색 알베도 규약)
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
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
    SUN_AZ_OFFSET=171.5,   # 표준. 프리셋 정면광 유지(scene01 계승). 사선 낙차 경계에
                           # 그림자가 얹혀 사교성을 강조(렌더에서 미세조정 가능).

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene20")

ASSET_ROLES = ["plaza_light", "band_dark", "plaza_lower", "grass",
               "brick_red", "tactile",
               "hdri", "mdl"]      # [v5.2 사용자] 임의 경고 팻말 제거


def build_views():
    """카메라 프리셋: grid_views(gy=0, 보행축 +X [고정]) + 미장센 4컷."""
    views = sc.grid_views(0.0)               # 프리셋 축 = 보행축 +X (사양 §D 고정)
    # oblique_overview: 사선 낙차 경계가 화면을 가로지름
    views["oblique_overview"] = dict(eye=[-8.0, -4.0, 3.2], tgt=[3.0, 1.0, -1.0])
    # walk_axis_front: 보행축 정면 — 경계가 사선으로 프레임을 자름
    views["walk_axis_front"] = dict(eye=[-6.0, 0.0, 1.6], tgt=[4.0, 0.0, -0.8])
    # along_diagonal: 계단 사선 축을 따라 내려봄(정렬 붕괴 확인)
    views["along_diagonal"] = dict(eye=[-3.0, -3.0, 1.5], tgt=[5.0, 1.6, -1.6])
    # low_grazing: 낮은 시점 — 사선 경계 위 낙차 은닉
    views["low_grazing"] = dict(eye=[-6.0, 0.0, 0.35], tgt=[4.0, 0.5, -0.3])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. oblique_overview / walk_axis_front — 30° 사교 계단·사선 낙차 경계 식별
 2. h0.3·d5~10                         — 사선 경계 위로 낙차 2.1m가 은닉되는가
 3. 정렬 대비                          — 건물은 축정렬, 계단만 30° 틀어진 대비
 4. cue ON vs OFF                      — railing/tactile(사선 따라) 토글 시 기하 불변
 5. 재질/공동                          — 하부 잔디 채움·경계 정합·Z파이팅 없는가
 6. [v4] 사선 쐐기 접합(첫 단차 전 폭 0.15)·축정렬 볼라드 열·건물 접지
 7. [v5] 공통 레이어 — 사선 점자띠 판독"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene20")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene20"

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
        M["upper"] = PBR(
            f"{ROOT}/Looks/Upper", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"])
        M["band"] = PBR(
            f"{ROOT}/Looks/Band", sc.tex_path("band_dark", "diff"),
            sc.tex_path("band_dark", "nor"), sc.tex_path("band_dark", "rough"),
            sca["band_dark"])
        M["lower"] = PBR(
            f"{ROOT}/Looks/Lower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"], tint=mp["lower_warm_tint"])
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
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        return M

    # -------------------------------------------------------------------
    # 지면 — 계곡 잔디(전면 솔리드, 공동 없음) + 상부 메사
    # -------------------------------------------------------------------
    def build_ground(M):
        v = PARAMS["valley"]
        H = v["size"] / 2.0
        BOX(f"{ROOT}/Valley", (6.0, 0.0, v["z_top"] - v["thick"] / 2.0),
            (v["size"], v["size"], v["thick"]), M["grass"], col=True)

    def build_upper(M):
        u = PARAMS["upper"]
        cx = (u["x0"] + u["x1"]) / 2.0
        cy = (u["y0"] + u["y1"]) / 2.0
        top, bot = u["z_top"], u["base_z"]
        BOX(f"{ROOT}/UpperPlaza", (cx, cy, (top + bot) / 2.0),
            (u["x1"] - u["x0"], u["y1"] - u["y0"], top - bot),
            M["upper"], col=True)
        # 밴드(Y로 달리는 차콜 스트라이프, scene01 모티프 축소)
        if cfg["cue_scene_dressing"]:
            bd = PARAMS["band"]
            x = bd["x0"]
            i = 0
            while x <= bd["x1"] + 1e-6:
                BOX(f"{ROOT}/Band_{i}", (x, 0.0, top + bd["proud"] - 0.003),
                    (bd["width"], 2.0 * bd["y_half"], 0.02), M["band"])
                x += bd["spacing"]
                i += 1

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 상부+계단+하부를 z=0 평지로 통일."""
        u = PARAMS["upper"]
        v = PARAMS["valley"]
        x0, x1 = u["x0"], 20.0
        y0, y1 = -8.0, 8.0
        BOX(f"{ROOT}/FlatPlaza", ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
            (0.0 + v["z_top"]) / 2.0), (x1 - x0, y1 - y0, 0.0 - v["z_top"]),
            M["upper"], col=True)

    # -------------------------------------------------------------------
    # 계단 + 하부 광장 (rot_group 30° — 경계 정합) + 사선 cue
    # -------------------------------------------------------------------
    def build_diagonal(M):
        # 계단 톤은 상부 plaza_light 계열로 통일(하부 웜과 대비는 lower가 담당).
        stair_mtl = M["upper"]
        r = PARAMS["rot"]
        grp = sc.build_rot_group(stage, f"{ROOT}/Diag", r["pivot"], r["deg"])
        # [감사v4 S1] 상부 광장 사선 연장 쐐기 — 회전군 내부이므로 동측 면이
        # 계단 상단 모서리(로컬 x=0)와 정확히 일치하는 30° 사선 에지가 된다.
        # 축정렬 광장(x ≤ -4.5)과 겹쳐 하나의 연속 상면(z=0)을 이루므로
        #   · A1 남측 쐐기 트렌치(수평 틈 최대 1.25 m, 낙차 2.15 m) 소멸,
        #   · A2 북측 상단 매몰(첫 단차 최대 0.75 m) 소멸 → 첫 단차 전 폭 0.15 m,
        #   · B1 점자띠(로컬 x -0.3..0)·B2 남측 난간 시작부(로컬 x -0.4) 접지,
        #   · 낙차 경계가 원점 1점이 아니라 30° 직선 전체가 되어 씬 특색은 강화.
        # 겹침부는 두 박스 모두 상면 0 / 저면 -2.2 이고 재질·월드투영 텍스처가
        # 동일하므로 Z파이팅이 발생해도 화면상 차이가 없다.
        wg = PARAMS["wedge"]
        BOX(f"{grp}/UpperWedge",
            ((wg["x0"] + wg["x1"]) / 2.0, 0.0,
             (wg["z_top"] + wg["base_z"]) / 2.0),
            (wg["x1"] - wg["x0"], 2.0 * wg["y_half"],
             wg["z_top"] - wg["base_z"]), M["upper"], col=True)
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{grp}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)
        # 하부 광장(웜) — 잔디 위 얇은 판(proud). 같은 30° 그룹 → 경계 정합.
        lo = PARAMS["lower"]
        lower_mtl = M["lower"] if cfg["cue_material_break"] else M["upper"]
        BOX(f"{grp}/LowerPlaza",
            ((lo["x0"] + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0),
            (lo["x1"] - lo["x0"], lo["y1"] - lo["y0"], lo["thick"]),
            lower_mtl, col=True)

        # 사선 cue (rot_group 내부 — 낙차 사선을 따라 회전)
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{grp}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["tactile"], z=0.0,
                             proud=tc["proud"])
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
                    stage, f"{grp}/StairRail_{tag}", sgn * sr["y"],
                    sr["x_start"], st["x0"], run, drop, stair_ground,
                    M["rail"], rail_h=sr["rail_h"], post_r=sr["post_r"],
                    spacing=sr["spacing"], rail_r=sr["rail_r"],
                    rail_mid_r=sr["rail_mid_r"],
                    rail_mid_drop=sr["rail_mid_drop"])

        # 하부 광장 소품 (회전군 로컬 — 사선 복도를 따라 정렬)
        if cfg["cue_scene_dressing"]:
            lz = lo["z_top"]
            # [v5.1 §2] 복도 입구 규정 볼라드 1열 + 점형블록 (rot 로컬 좌표)
            lb = PARAMS["lower_bollards"]
            for i, ly in enumerate(lb["ys"]):
                build_bollard_std(M, f"{grp}/LowBollard_{i}", lb["x"], ly, lz,
                                  k=i)
            if cfg["cue_tactile"]:
                bk = lb["block"]
                sc.build_tactile(stage, f"{grp}/Tactile_LowBollard",
                                 bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                                 M["tactile"], z=lz,
                                 proud=PARAMS["tactile"]["proud"])
            for i, (lx, ly, yaw) in enumerate(PARAMS["lower_benches"]):
                sc.build_bench(stage, f"{grp}/LowBench_{i}", lx, ly, lz,
                               M["wood"], yaw=yaw)

    # -------------------------------------------------------------------
    # 드레싱 — 축정렬 건물 3 + 축정렬 소품(볼라드 열·화단·벤치·가로등·
    #          생울타리) + 메사 진입 램프
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
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        # [v5.1 §2] 메사 진입 램프 상단 규정 볼라드 1열 + 점형블록
        bl = PARAMS["bollards"]
        for i, by in enumerate(bl["ys"]):
            build_bollard_std(M, f"{ROOT}/Bollard_{i}", bl["x"], by, 0.0, k=i)
        if cfg["cue_tactile"]:
            bk = bl["block"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Bollard",
                             bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                             M["tactile"], z=0.0,
                             proud=PARAMS["tactile"]["proud"])
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for i, (px, py) in enumerate(PARAMS["planters"]):
            sc.build_planter(stage, f"{ROOT}/Planter_{i}", px, py, 0.0,
                             M["curb"], M["grass"], tree_mtls=tree_mtls,
                             size=PARAMS["planter"]["size"])
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, 0.0,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (lx, ly, sl["pole_h"] / 2.0), sl["pole_r"],
                sl["pole_h"], M["pole"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (lx + sgn * sl["arm_len"] / 2.0, ly, sl["pole_h"] - 0.1),
                    sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (lx + sgn * sl["arm_len"], ly, sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        for i, (hx0, hy0, hx1, hy1) in enumerate(PARAMS["hedges"]):
            sc.build_hedge(stage, f"{ROOT}/Hedge_{i}", hx0, hy0, hx1, hy1,
                           0.9, base_z=0.0)
        # 메사 진입 램프 (서측, 잔디 -2.15 → 광장 0). drop 음수 = +X로 상승.
        # margin=0 이라 상단 모서리가 광장 서면(x=-14, z=0)과 정확히 flush.
        ar = PARAMS["access_ramp"]
        vz = PARAMS["valley"]["z_top"]
        sc.build_slope(stage, f"{ROOT}/AccessRamp", ar["x0"], vz,
                       ar["x1"] - ar["x0"], vz - PARAMS["upper"]["z_top"],
                       ar["y0"], ar["y1"], ar["thick"], M["upper"],
                       margin=0.0, collider=True)

    # [v5.2 사용자] 임의 경고 팻말 제거 — build_signs() 삭제.

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_ground(M)
    if cfg["hazard_stairs"]:
        build_upper(M)
        build_diagonal(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    # [v5.2 사용자] 임의 경고 팻말 제거 — cue_sign 배치 삭제.

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] scene20 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["oblique_overview"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene20_{ts}.png")
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
