# -*- coding: utf-8 -*-
"""
scene11_grating_fireescape.py — NegObs 인공씬 11호: 건물 외벽 비상계단 (Isaac Sim 4.5)

유형    : T19 그레이팅 비상계단 (개방 라이저 × 격자 그림자)
사양서  : Docs/briefs/multi_scene_brief_v3.md §D scene11_grating_fireescape
공통    : scene_common.py (검증된 API 헬퍼) · scene02_underpass.py (도시계 골격)

위험 본질: 벽돌 건물 측벽에 매달린 2플라이트 스위치백 비상계단. 라이저(수직판)가
           없어 디딤판 틈으로 아래가 그대로 투시되고, 정오광에서 그레이팅 슬릿이
           바닥에 스트라이프 그림자를 드리운다. 낙차 총 3.2m (플라이트당 1.6).
목표     : 벽돌 측벽 + 개방 라이저 2플라이트(상부 rot_group 180° 반전) + 중간 참
           + 파이프 난간 + 아스팔트 골목을 조립, 렌더로 판정 (렌더 전용).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene11_grating_fireescape.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python scene11_grating_fireescape.py
스모크 조기종료:        NEGOBS_SMOKE=1  python scene11_grating_fireescape.py

좌표계: Z-up, m, 진행축 +X, 낙차 시작 모서리 = x=0.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hazard_stairs 만 기하 토글(False→비상계단 제거).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 비상계단 전체 제거(평탄 골목 대조군)
    "cue_railing":        True,   # 양 플라이트 파이프 난간(rot_group 내 상부 포함)
    "cue_tactile":        False,  # 비상계단엔 점자블록 관행 없음(키만 예약)
    "cue_material_break": True,   # False → 디딤판을 골목 아스팔트 톤으로 통일
    "cue_nosing":         False,  # 개방 그레이팅 — 황색 논슬립 띠 비관행(키 예약)
    "cue_sign":           False,  # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,   # 건너편 건물·원경 차단·골목 소품 일괄
}


# ===========================================================================
# [B] PARAMS — 치수·재질·조명. NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG 머지.
# ===========================================================================
PARAMS = dict(
    # --- 비상계단 스위치백 ---
    #  플라이트당 10단 × riser 0.16 = 낙차 1.6, tread 0.28 → run 2.8. 폭 0.8.
    #  하부 플라이트: x0=0(z 1.6→0), +X 하강, y -0.4..0.4.
    #  상부 플라이트: 동일 빌더를 rot_group(pivot (1.4,0.475), 180°)로 반전 배치
    #    → 월드에서 x 2.8(z3.2, 지붕참)→x 0(z1.6, 중간참)로 하강,
    #      y 0.55..1.35 (측방 오프셋 · 벽면 y=1.35 에 밀착 → 감사 A-11-6 해소).
    flight=dict(riser=0.16, tread=0.28, nsteps=10, width=0.8,
                y0=-0.4, y1=0.4, z_mid=1.6, z_top=3.2, tread_t=0.04,
                gap=0.025, slits=3),
    # 감사 A-11-6/B-11-3 — 피벗 y 0.4→0.475: 상부 플라이트 외연이 벽면(1.35)에 접함
    rot_pivot=(1.4, 0.475), rot_deg=180.0,
    # 중간 참(z=1.6). 감사 A-11-1 — x1 을 0.4→0.0 으로 후퇴시켜 하부 플라이트
    #   단1(x 0..0.28, top 1.44)을 완전 노출(참 1.6 → 단1 1.44 = 정상 riser 0.16).
    #   깊이는 스위치백 반전용으로 x0 −0.7→−1.3(1.3 m) 확보.
    landing=dict(x0=-1.3, x1=0.0, y0=-0.4, y1=1.37, z_top=1.6, plate_t=0.05,
                 brace_r=0.035, brace_drop=1.0),
    # 지붕 진입 소참. 감사 A-11-2 — x0 을 2.4→2.8 로 후퇴(상부 플라이트 단1은
    #   월드 x 2.52..2.80/top 3.04 → 완전 노출). 깊이 1.6 m, 비상구 문 설치면.
    roof_pad=dict(x0=2.8, x1=4.4, y0=0.55, y1=1.37, z_top=3.2, plate_t=0.05,
                  brace_r=0.035, brace_drop=1.0),
    # 파이프 난간 (양 플라이트 개방측 1선 + 참 모서리)
    #   y_inset: 스트링거 중심선(y0+0.03)에 포스트를 매입 → 접선 부유 방지(B-11-3)
    rail=dict(rail_h=0.95, post_r=0.02, rail_r=0.028, rail_mid_r=0.02,
              rail_mid_drop=0.48, spacing=0.9, y_inset=0.03),
    # 지붕참 뒤 비상구(강철문 + 문틀 + EXIT 사인) — 감사 A-11-3 종점 막장 해소
    exit_door=dict(cx=3.6, w=1.05, h=2.10, leaf_t=0.05, frame_w=0.09,
                   frame_t=0.08, sign_w=0.60, sign_h=0.22, sign_z=5.52),

    # --- 건물 측벽(brick, x-z 긴 벽): 비상계단이 매달린 모체 ---
    #  파사드 -Y평면(y=1.35), 창문 x배열. 측벽이 골목 한쪽 벽.
    #  감사 D-11-1 — x0 −4→−24 로 접근 회랑 연장(d=10 밴드에서도 골목 성립).
    host=dict(x0=-24.0, x1=8.0, y0=1.35, y1=21.0, h=12.0, floors=4,
              axis="y", facade_y=1.35, face_dir=-1.0),
    # 골목 건너편 건물(-Y), 파사드 +Y평면
    across=dict(x0=-24.0, x1=8.0, y0=-20.0, y1=-3.0, h=11.0, floors=4,
                axis="y", facade_y=-3.0, face_dir=1.0),
    # 원경 차단(+X 지평선): 골목 가로지르는 건물
    endcap=dict(x0=12.0, x1=18.0, y0=-20.0, y1=21.0, h=13.0, floors=5,
                axis="x", facade_x=12.0, face_dir=-1.0),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.6, margin=2.0),

    # 골목 소품
    trashcan=dict(cx=4.2, cy=-1.6, r=0.32, h=0.95),
    bollard=dict(cx=5.4, cy=-2.2, r=0.07, h=0.75),
    # 맥락 드레싱(cue_scene_dressing) — 도시 골목 즉독용 저비용 소품
    props=dict(
        gutter=(-4.0, -0.72, 32.0, 0.25),        # 중앙 배수 측구 (cx,cy,길이,폭)
        manholes=((3.0, -1.25), (-3.4, -1.45)),
        hvac_host=((-1.2, 2.6), (-1.2, 5.6), (5.4, 2.6),
                   (5.4, 5.6), (7.0, 2.6), (7.0, 5.6)),   # (x, z) 벽면 실외기
        hvac_across=((0.6, 2.2), (4.8, 4.9)),
        downpipe_x=(-2.6, 7.4),
        dustbin=(6.5, -2.0),
        pallet=(-1.6, -2.4),
        cartons=((-0.9, -2.55, 0.0), (-0.4, -2.62, 0.0),
                 (0.1, -2.50, 0.0), (-0.65, -2.58, 0.46)),
        bollard_xs=(4.4, 5.4, 6.4, 7.4),
        bollard_y=-2.2,
    ),

    # 주변 대지 / 지면
    #  감사 A-11-8 — z_top −0.02→0.0: 하부 플라이트 최하단 디딤(top 0.0)과 동일면
    ground=dict(size=120.0, z_top=0.0),          # 아스팔트 골목 (평탄, 공동 없음)

    # --- 재질 ---
    #  감사 공통① — make_pbr diffuse_color 는 선형값. 어두운 상수색은 0.02~0.06.
    material=dict(
        scale=dict(brick_red=2.0, metal_rust=1.2, grass=4.0),
        asphalt_color=(0.045, 0.045, 0.05), asphalt_rough=0.9,   # B-11-1
        gutter_color=(0.028, 0.028, 0.032), gutter_rough=0.95,
        tread_alt_color=(0.055, 0.055, 0.06), tread_alt_rough=0.85,  # break OFF
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.06, 0.05, 0.045), rail_rough=0.65,             # B-11-4
        rail_metallic=0.4,
        parapet_color=(0.62, 0.60, 0.57), parapet_rough=0.6,
        trash_color=(0.05, 0.09, 0.06), trash_rough=0.55, trash_metallic=0.5,
        steel_color=(0.05, 0.055, 0.055), steel_rough=0.5,
        steel_metallic=0.5,
        sign_color=(0.03, 0.22, 0.09), sign_emit=(0.10, 0.85, 0.30),
        sign_emit_intensity=60.0,
        hvac_color=(0.085, 0.085, 0.09), hvac_metallic=0.4,
        wood_color=(0.075, 0.055, 0.038), carton_color=(0.115, 0.085, 0.055),
        grass_tint=(0.55, 0.68, 0.42),
    ),

    # --- 조명: scene01/02 표준 + SUN_AZ_OFFSET 171.5 ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    SUN_AZ_OFFSET=171.5,   # 표준. 정오 고도광에서 디딤판 슬릿이 골목 바닥에
                           # 스트라이프 그림자를 만드는 것이 특색(렌더에서 미세조정 가능).

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene11")

ASSET_ROLES = ["brick_red", "metal_rust", "grass", "hdri", "mdl"]


def build_views():
    """카메라 프리셋: grid_views(gy=0.4, 계단 중심축) + 미장센 4컷."""
    views = sc.grid_views(0.4)               # 스위치백 중심 y≈0.4
    # approach: 골목에서 비상계단 정면 접근
    views["alley_approach"] = dict(eye=[-6.0, -0.2, 1.6], tgt=[3.0, 0.4, 1.4])
    # under_treads: 계단 아래에서 개방 라이저 투시(틈으로 하늘/위 보임)
    views["under_treads"] = dict(eye=[2.6, -1.2, 0.5], tgt=[1.0, 0.4, 2.2])
    # slit_shadow: 낮은 시점으로 바닥 슬릿 그림자 스트라이프 포착
    views["slit_shadow"] = dict(eye=[-1.0, -2.0, 0.35], tgt=[2.5, 0.2, 0.1])
    # beauty_overview: 골목 건너(-Y)에서 비상계단 전체 지그재그가 벽면에 걸리는
    #   구도 (감독 r1 C-11 재조준). h4는 grid 높이밴드(0.3/0.9/1.8) 예외 — 부감
    #   인상용 의도적 상향.
    views["beauty_overview"] = dict(eye=[-8.0, -1.5, 3.5], tgt=[3.0, 0.4, 2.0])  # 핫픽스: 작동 뷰(alley_approach) 파생
    # exit_landing: 지붕참(z=3.2)·비상구 강철문·상부 난간 종점 확인 (A-11-2/3 검수)
    views["exit_landing"] = dict(eye=[6.6, -2.6, 4.2], tgt=[3.4, 1.0, 3.9])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. alley_approach / beauty — 2플라이트 스위치백·중간 참·지붕 진입 식별
 2. under_treads            — 라이저 부재: 디딤판 틈으로 위/아래 투시되는가
 3. slit_shadow / h0.3      — 그레이팅 슬릿(단당 3)이 바닥에 스트라이프 그림자
 4. exit_landing            — 지붕참↔강철문 접속·참 난간·벽 브래킷(지주 없음)
 5. cue ON vs OFF           — railing/material_break 토글 시 기하 트랜스폼 불변
 6. 재질                    — 벽돌 반복·녹철 톤·Z파이팅·부유 없는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene11")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene11"

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
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["metal_rust"] = PBR(
            f"{ROOT}/Looks/MetalRust", sc.tex_path("metal_rust", "diff"),
            sc.tex_path("metal_rust", "nor"), sc.tex_path("metal_rust", "rough"),
            sca["metal_rust"], metallic=0.6, specular_level=0.3)
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["tread_alt"] = PBR(f"{ROOT}/Looks/TreadAlt",
                             diffuse_color=mp["tread_alt_color"],
                             roughness_const=mp["tread_alt_rough"], metallic=0.0)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass",
                         diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail",
                        diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["trash"] = PBR(f"{ROOT}/Looks/Trash",
                         diffuse_color=mp["trash_color"],
                         metallic=mp["trash_metallic"],
                         roughness_const=mp["trash_rough"])
        M["gutter"] = PBR(f"{ROOT}/Looks/Gutter",
                          diffuse_color=mp["gutter_color"],
                          roughness_const=mp["gutter_rough"], metallic=0.0)
        M["steel"] = PBR(f"{ROOT}/Looks/Steel",
                         diffuse_color=mp["steel_color"],
                         metallic=mp["steel_metallic"],
                         roughness_const=mp["steel_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/ExitSign",
                        diffuse_color=mp["sign_color"], roughness_const=0.5,
                        emission_color=mp["sign_emit"],
                        emission_intensity=mp["sign_emit_intensity"])
        M["hvac"] = PBR(f"{ROOT}/Looks/Hvac",
                        diffuse_color=mp["hvac_color"],
                        metallic=mp["hvac_metallic"], roughness_const=0.55)
        M["wood"] = PBR(f"{ROOT}/Looks/Wood",
                        diffuse_color=mp["wood_color"], roughness_const=0.85)
        M["carton"] = PBR(f"{ROOT}/Looks/Carton",
                          diffuse_color=mp["carton_color"],
                          roughness_const=0.9)
        return M

    # -------------------------------------------------------------------
    # 지면 — 평탄 아스팔트 골목 (공동 없음: 비상계단은 지면 위 상부구조)
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        H = g["size"] / 2.0
        th = 0.5
        BOX(f"{ROOT}/Alley", (0.0, 0.0, g["z_top"] - th / 2.0),
            (g["size"], g["size"], th), M["asphalt"], col=True)

    # -------------------------------------------------------------------
    # 비상계단 — 2플라이트(상부 rot_group 180° 반전) + 참 2개
    # -------------------------------------------------------------------
    def build_fireescape(M):
        fl = PARAMS["flight"]
        tread_mtl = M["metal_rust"] if cfg["cue_material_break"] else M["tread_alt"]
        rp = PARAMS["rail"]

        # 하부 플라이트 (z 1.6 → 0, +X 하강)
        sc.build_open_riser_stairs(
            stage, f"{ROOT}/LowerFlight", 0.0, fl["y0"], fl["y1"],
            fl["riser"], fl["tread"], fl["nsteps"], fl["z_mid"],
            tread_mtl, M["metal_rust"], tread_t=fl["tread_t"],
            gap=fl["gap"], slits=fl["slits"])

        # 상부 플라이트 (rot_group 180° 반전 → 월드 z 3.2→1.6, 측방 오프셋)
        grp = sc.build_rot_group(stage, f"{ROOT}/UpperFlight",
                                 PARAMS["rot_pivot"], PARAMS["rot_deg"])
        sc.build_open_riser_stairs(
            stage, f"{grp}/Stairs", 0.0, fl["y0"], fl["y1"],
            fl["riser"], fl["tread"], fl["nsteps"], fl["z_top"],
            tread_mtl, M["metal_rust"], tread_t=fl["tread_t"],
            gap=fl["gap"], slits=fl["slits"])

        # 중간 참(x≈0, z=1.6): 금속 판 + 지지 기둥 4
        la = PARAMS["landing"]
        _metal_platform(M, f"{ROOT}/MidLanding", la)
        # 지붕 진입 소참(상부 플라이트 최상단)
        rpad = PARAMS["roof_pad"]
        _metal_platform(M, f"{ROOT}/RoofPad", rpad)

        # 파이프 난간
        if cfg["cue_railing"]:
            run = fl["tread"] * fl["nsteps"]
            drop = fl["riser"] * fl["nsteps"]
            la = PARAMS["landing"]
            rpad = PARAMS["roof_pad"]
            pvx, pvy = PARAMS["rot_pivot"]

            def flight_ground(z0):
                """플라이트 상단 z0 기준 단면 콜백(포스트 착지용).
                감사 잔여버그 — 기존 코드는 상·하부 모두 z_mid(1.6) 기준을 써서
                상부 난간이 계단면보다 1.6 m 아래에 매몰돼 있었다."""
                def f(x):
                    if x <= 1e-9:
                        return z0
                    i = min(max(int(x / fl["tread"]) + 1, 1), fl["nsteps"])
                    return z0 - fl["riser"] * i
                return f

            def _line(prefix, y, x_start, ground_fn):
                sc.build_railing_line(
                    stage, prefix, y, x_start, 0.0, run, drop, ground_fn,
                    M["rail"], rail_h=rp["rail_h"], post_r=rp["post_r"],
                    spacing=rp["spacing"], rail_r=rp["rail_r"],
                    rail_mid_r=rp["rail_mid_r"],
                    rail_mid_drop=rp["rail_mid_drop"])

            # 하부 플라이트 개방측(−Y) — 포스트를 스트링거 중심선에 매입(B-11-3),
            #   수평 연장은 중간 참 −X 끝까지(A-11-5 참 −Y 모서리 겸용)
            _line(f"{ROOT}/RailLower", fl["y0"] + rp["y_inset"],
                  la["x0"] + 0.03, flight_ground(fl["z_mid"]))
            # 상부 플라이트: rot_group 내부(계단과 함께 180° 반전).
            #   로컬 +Y 스트링거 = 월드 y 0.58 = 개방측 (A-11-4 벽쪽 난간 교정)
            x_start_local = 2.0 * pvx - (rpad["x1"] - 0.03)
            _line(f"{grp}/Rail", fl["y1"] - rp["y_inset"], x_start_local,
                  flight_ground(fl["z_top"]))
            # 참 −X 모서리 · 지붕참 +X 모서리 (A-11-5)
            y_up_world = 2.0 * pvy - (fl["y1"] - rp["y_inset"])   # = 0.58
            _edge_rail(M, f"{ROOT}/RailMidLandingW",
                       la["x0"] + 0.03, fl["y0"] + rp["y_inset"],
                       la["x0"] + 0.03, la["y1"] - 0.05, la["z_top"])
            _edge_rail(M, f"{ROOT}/RailRoofPadE",
                       rpad["x1"] - 0.03, y_up_world,
                       rpad["x1"] - 0.03, rpad["y1"] - 0.05, rpad["z_top"])

    def _edge_rail(M, prefix, x0, y0, x1, y1, z_base):
        """평탄 모서리 난간 1선(상·중 레일 + 포스트). 축정렬 세그먼트 전용.
        build_railing_line 은 +X 진행 전용이라 Y 방향 모서리를 못 만든다."""
        rp = PARAMS["rail"]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        if L < 1e-6:
            return
        mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        ry, rx = (90.0, 0.0) if abs(dy) < 1e-6 else (0.0, 90.0)
        for tag, r, off in (("RailTop", rp["rail_r"], 0.0),
                            ("RailMid", rp["rail_mid_r"], rp["rail_mid_drop"])):
            CYL(f"{prefix}/{tag}", (mx, my, z_base + rp["rail_h"] - off),
                r, L, M["rail"], rotY=ry, rotX=rx)
        n = max(1, int(round(L / rp["spacing"])))
        for k in range(n + 1):
            t = k / float(n)
            CYL(f"{prefix}/Post_{k}",
                (x0 + dx * t, y0 + dy * t, z_base + rp["rail_h"] / 2.0),
                rp["post_r"], rp["rail_h"], M["rail"])

    def _metal_platform(M, prefix, p):
        """금속 판 참 + 벽 브래킷 2본(캔틸레버).
        감사 B-11-5 — 실제 비상계단 참은 지면 기둥이 아니라 벽 브래킷에 매달린다.
        기존 4본 지주(z 0→1.55 / 0→3.15)는 '야외 테이블' 실루엣을 만들었다."""
        cx = (p["x0"] + p["x1"]) / 2.0
        cy = (p["y0"] + p["y1"]) / 2.0
        Lx = p["x1"] - p["x0"]
        Ly = p["y1"] - p["y0"]
        z_top = p["z_top"]
        t = p["plate_t"]
        BOX(f"{prefix}/Plate", (cx, cy, z_top - t / 2.0),
            (Lx, Ly, t), M["metal_rust"], col=True)
        wy = PARAMS["host"]["y0"] - 0.02        # 벽면(1.35) 안쪽 2cm 물림
        oy = p["y0"] + 0.15                     # 판 외측 근처 부착점
        z_hi = z_top - t - 0.01                 # 판 하면
        z_lo = z_hi - p["brace_drop"]           # 벽 부착점
        dz = z_hi - z_lo
        # add_cylinder 는 rotX(θ) 로 축 ẑ→(0,−sinθ,cosθ). 방향 (dy,dz) 를 맞추려면
        #   sinθ = −dy/L, cosθ = dz/L  ⇒ θ = atan2(wy−oy, dz)
        ang = math.degrees(math.atan2(wy - oy, dz))
        L = math.hypot(wy - oy, dz)
        for tag, bx in (("W", p["x0"] + 0.25), ("E", p["x1"] - 0.25)):
            CYL(f"{prefix}/Brace_{tag}",
                (bx, (wy + oy) / 2.0, (z_lo + z_hi) / 2.0),
                p["brace_r"], L, M["metal_rust"], rotX=ang)
            BOX(f"{prefix}/Bracket_{tag}", (bx, wy - 0.03, z_lo),
                (0.16, 0.10, 0.28), M["metal_rust"])

    # -------------------------------------------------------------------
    # 드레싱 — 모체 건물(측벽) + 건너편 + 원경 차단 + 골목 소품
    # -------------------------------------------------------------------
    def build_dressing(M):
        for key in ("host", "across", "endcap"):
            sc.build_building(stage, f"{ROOT}/Bldg_{key}", PARAMS[key],
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        gz = PARAMS["ground"]["z_top"]
        pr = PARAMS["props"]
        # --- 비상구(A-11-3 종점 막장 해소): 지붕참 뒤 host 벽면의 강철문 ---
        ed = PARAMS["exit_door"]
        rpad = PARAMS["roof_pad"]
        wy = PARAMS["host"]["y0"]                     # 벽면 y=1.35
        dz0 = rpad["z_top"]                           # 문턱 = 지붕참 상면
        ly = wy - ed["leaf_t"] / 2.0                  # 문짝 중심 y(벽면에 플러시)
        BOX(f"{ROOT}/ExitDoor/Leaf", (ed["cx"], ly, dz0 + ed["h"] / 2.0),
            (ed["w"], ed["leaf_t"], ed["h"]), M["steel"])
        fw, ft = ed["frame_w"], ed["frame_t"]
        fy = wy - ft / 2.0
        # 문틀 4변 (개구 4박스 분할 관례)
        BOX(f"{ROOT}/ExitDoor/FrameL",
            (ed["cx"] - ed["w"] / 2.0 - fw / 2.0, fy, dz0 + ed["h"] / 2.0),
            (fw, ft, ed["h"] + 2 * fw), M["steel"])
        BOX(f"{ROOT}/ExitDoor/FrameR",
            (ed["cx"] + ed["w"] / 2.0 + fw / 2.0, fy, dz0 + ed["h"] / 2.0),
            (fw, ft, ed["h"] + 2 * fw), M["steel"])
        BOX(f"{ROOT}/ExitDoor/FrameT",
            (ed["cx"], fy, dz0 + ed["h"] + fw / 2.0),
            (ed["w"], ft, fw), M["steel"])
        BOX(f"{ROOT}/ExitDoor/FrameB", (ed["cx"], fy, dz0 - fw / 2.0),
            (ed["w"], ft, fw), M["steel"])
        # EXIT 사인 (녹색 발광 상수색)
        BOX(f"{ROOT}/ExitSign", (ed["cx"], wy - 0.03, ed["sign_z"]),
            (ed["sign_w"], 0.06, ed["sign_h"]), M["sign"])
        # --- 골목 바닥: 배수 측구 + 맨홀 ---
        gx, gy_, gL, gW = pr["gutter"]
        BOX(f"{ROOT}/Gutter", (gx, gy_, gz - 0.03), (gL, gW, 0.06), M["gutter"])
        for i, (mx, my) in enumerate(pr["manholes"]):
            CYL(f"{ROOT}/Manhole_{i}", (mx, my, gz - 0.008), 0.32, 0.03,
                M["metal_rust"])
        # --- 벽면 설비: 실외기 · 수직 배수관 (도시 골목 즉독) ---
        for i, (hx, hz) in enumerate(pr["hvac_host"]):
            BOX(f"{ROOT}/Hvac_H{i}", (hx, wy - 0.24, hz),
                (0.85, 0.35, 0.60), M["hvac"])
            BOX(f"{ROOT}/HvacShelf_H{i}", (hx, wy - 0.24, hz - 0.33),
                (0.95, 0.42, 0.05), M["metal_rust"])
        ay = PARAMS["across"]["facade_y"]
        for i, (hx, hz) in enumerate(pr["hvac_across"]):
            BOX(f"{ROOT}/Hvac_A{i}", (hx, ay + 0.24, hz),
                (0.85, 0.35, 0.60), M["hvac"])
        for i, dx in enumerate(pr["downpipe_x"]):
            CYL(f"{ROOT}/DownPipe_{i}", (dx, wy - 0.08, gz + 6.0), 0.07, 12.0,
                M["metal_rust"])
            for k in range(4):
                CYL(f"{ROOT}/PipeBracket_{i}_{k}",
                    (dx, wy - 0.04, gz + 1.6 + 2.8 * k), 0.03, 0.10,
                    M["metal_rust"], rotX=90.0)
        # --- 골목 소품: 더스트빈 · 팔레트 적층 · 종이상자 · 볼라드 열 ---
        bx, by = pr["dustbin"]
        BOX(f"{ROOT}/DustBin", (bx, by, gz + 0.60), (1.8, 1.05, 1.20),
            M["trash"], col=True)
        BOX(f"{ROOT}/DustBinLid", (bx, by, gz + 1.24), (1.86, 1.10, 0.08),
            M["metal_rust"])
        px, py = pr["pallet"]
        for k in range(4):
            BOX(f"{ROOT}/Pallet_{k}", (px, py, gz + 0.07 + 0.16 * k),
                (1.2, 1.0, 0.14), M["wood"])
        for i, (cx_, cy_, cz_) in enumerate(pr["cartons"]):
            BOX(f"{ROOT}/Carton_{i}", (cx_, cy_, gz + cz_ + 0.225),
                (0.45, 0.45, 0.45), M["carton"])
        # 쓰레기통(원기둥)
        tc = PARAMS["trashcan"]
        CYL(f"{ROOT}/TrashCan", (tc["cx"], tc["cy"], gz + tc["h"] / 2.0),
            tc["r"], tc["h"], M["trash"], col=True)
        bo = PARAMS["bollard"]
        for i, bxx in enumerate(pr["bollard_xs"]):
            sc.build_bollard(stage, f"{ROOT}/Bollard_{i}", bxx,
                             pr["bollard_y"], gz,
                             radius=bo["r"], height=bo["h"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_ground(M)
    if cfg["hazard_stairs"]:
        build_fireescape(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── 스모크 조기종료: 조립·조명까지만 검증하고 종료 ──
    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] scene11 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene11_{ts}.png")
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
