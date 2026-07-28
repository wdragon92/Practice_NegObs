# -*- coding: utf-8 -*-
"""
scene12_cliff_plankwalk.py — NegObs 인공씬 12호: 절벽 잔도 (Isaac Sim 4.5)

사양서 : Docs/multi_scene_brief_v3.md §A(회귀 체크리스트)·§D(scene12)·§B(빌더)
공통 라이브러리 : scene_common.py / 골격 관례 : scene03_riverbank.py

유형 (T17 절벽 잔도): **편측 무한낙차 — missing ground band 극단**.
  수직 암벽(rock_face)에 목판이 캔틸레버로 붙어 +X 하강. 벽 반대쪽(−Y)은
  완전 개방, 하부는 안개톤 대지 z=−30. 낙차 증거는 **판 자체의 계단 + 벽측
  쇠사슬 힌트 + 원경 맞은편 암벽**뿐. 지면이 한쪽에만 존재.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene12_cliff_plankwalk.py

자동 캡처 : NEGOBS_CAPTURE=1 python scene12_cliff_plankwalk.py
조립 스모크: NEGOBS_SMOKE=1 python scene12_cliff_plankwalk.py

좌표계: Z-up, m, 진행축 +X(벽면 따라 하강). 벽면 = y=0(벽 몸체 +Y),
        개방측 = −Y. 잔도 시작 = x=0(z=0 상부 판 랜딩).

────────────────────────────────────────────────────────────────────────────
기하 핵심 (감독 보충 반영):
  · 수직 암벽 : rock_face 대형 박스(두께 3=Y, 높이 z +6..−30) 3장 겹침
    (x 오프셋+미세 Y 돌출 = 요철).
  · 목판 20단(riser 0.16, 폭 0.35, weathered_planks=wood_dark)이 벽에서
    3cm 겹쳐 캔틸레버, −Y 로 개방.
  · 카메라 밴드(h0.3~2.0)는 **판 표면 기준** → grid_views eye z 를 판 기준
    z(plank_ref)로 시프트. 판 중심선 y 로 gy 이동.
  · 하부 안개톤 대지 z=−30 + 원경 맞은편 암벽(x≈+25) + 협곡 건너 원경 암벽
    (−Y 원거리) = 지평 폐쇄(허공 방지)하되 근경은 편측 무한낙차 유지.
────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. 잔도 안전용 쇠사슬(cue_railing 기본 True).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 판을 z=0 평판 보행로로(낙차 제거)
    "cue_railing":        True,    # **벽측 쇠사슬 힌트**(잔도 안전시설) 기본 True
    "cue_tactile":        False,   # 미사용(코드 경로만)
    "cue_material_break": True,    # 판(wood) vs 벽(rock) 재질 대비(상시 상이)
    "cue_sign":           False,   # [선택] 미구현 — 키만 예약
    "cue_scene_dressing": True,    # 암벽 요철·판 버팀목·앵커·리본·경고판 (감사 D)
    "cue_nosing":         False,   # 미사용(코드 경로만)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # 목판 계단 : 20단, riser 0.16, tread 0.30, 폭(Y) 0.35, 벽 3cm 겹침
    planks=dict(x0=0.0, nsteps=20, riser=0.16, tread=0.30, width=0.35,
                thick=0.06, wall_overlap=0.03, z_start=0.0),  # 감독 r1 —
                # 판 두께 0.05→0.06(렌더 가시성 확보). 벽 3cm 겹침 유지
    # 상부 판 랜딩(벽 부착 진입부)
    top_landing=dict(x0=-2.0, x1=0.0, thick=0.08),
    # 수직 암벽(rock_face) — 두께 3(Y), z +6..−30
    #  감사 A-12-3 — 패널1 y0 0.15→−0.02: 판 안쪽 끝(y=+0.03)과 0.05 겹침 확보.
    #    (기존 0.15 는 x 3..7 구간에서 0.12 m 슬롯 + 무지지 캔틸레버였다.)
    #  감사 A-12-1/2 — 진입(−X)·탈출(+X) 선반을 받칠 벽 패널을 양단으로 연장.
    wall=dict(z_top=6.0, z_bot=-30.0, thick=3.0),
    wall_panels=[dict(x0=-9.5, x1=-2.5, y0=0.02),    # 진입 선반 배후(신규)
                 dict(x0=-3.0, x1=3.0, y0=0.0),
                 dict(x0=2.0, x1=8.0, y0=-0.02),     # A-12-3 (구 0.15)
                 dict(x0=7.0, x1=12.0, y0=-0.04),    # 미세 −Y
                 dict(x0=11.0, x1=17.0, y0=0.02)],   # 탈출 선반 배후(신규)
    # 진입/탈출 암반 선반 (A-12-1/2) — 잔도 양끝을 절벽 지형에 접속
    entry_shelf=dict(cx=-5.0, cy=-0.50, cz=-0.75, sx=6.2, sy=1.60, sz=1.50),
    exit_shelf=dict(cx=7.55, cy=-0.45, cz=-3.95, sx=3.30, sy=1.30, sz=1.50),
    exit_trail=dict(x0=9.2, n=3, tread=0.30, z_top=-3.2,
                    ledge=dict(cx=11.8, cy=-0.35, cz=-3.95, sx=3.4, sy=1.10,
                               sz=1.50)),
    # 하부 안개톤 대지(z=−30, 대형) — 개방측(−Y)로 크게 (원경 능선 발치까지)
    abyss=dict(x0=-80.0, x1=120.0, y0=-200.0, y1=8.0, z_top=-30.0, thick=2.0),
    # 감사 B-12-1 — 원경 암벽 후퇴. 기존(far x24..32 / gorge y−52..−46)은 개방측·
    #   전방 시야를 전부 막아 하늘 0 %·심연 0~5 % → 씬 정체성(편측 무한낙차) 소멸.
    #   눈높이 아래 능선으로 물리면 프레임 상부에 하늘, 하부에 심연이 열린다.
    far_cliff=dict(x0=55.0, x1=75.0, y0=-60.0, y1=6.0, z0=-30.0, z1=-2.0),
    gorge_cliff=dict(x0=-60.0, x1=90.0, y0=-165.0, y1=-150.0, z0=-30.0,
                     z1=-4.0),
    # 협곡 안개층 1장(z=−18) — 심연 깊이감 (단일 프림).
    #   x −62.5..52.5 / y −132.5..−7.5 : far_cliff(x≥55)·gorge_cliff(y≤−150)와
    #   교차하지 않게 열린 협곡 안쪽으로만 깐다(하드에지 관통 방지).
    haze=dict(cx=-5.0, cy=-70.0, cz=-18.1, sx=115.0, sy=125.0, sz=0.2),
    # 벽측 쇠사슬 힌트(cue_railing) : 판 위 0.8, 가는 원기둥 선
    chain=dict(y=0.0, rail_h=0.8, rail_r=0.012, rail_mid_r=0.010,
               post_r=0.010, spacing=1.0),

    # --- 맥락 드레싱(cue_scene_dressing) ---
    #  relief: (cx, cz, 폭X, 높이Z, 돌출Y) — 전부 판 라인과 z 간섭 없게 검증
    #    (상방 배치는 판 상면 +1.4 이상, 하방 배치는 판 하면 −0.15 이하)
    dressing=dict(
        relief=((-1.0, 3.00, 1.40, 1.20, 0.35),
                (0.30, -1.35, 1.00, 1.20, 0.34),
                (1.20, 2.60, 1.30, 1.40, 0.30),
                (2.40, -2.35, 1.10, 1.00, 0.32),
                (3.60, 1.20, 1.60, 1.60, 0.40),
                (4.50, -3.70, 1.20, 1.20, 0.30),
                (5.40, 0.20, 1.10, 1.40, 0.28),
                (7.50, 0.50, 1.50, 1.80, 0.35),
                (9.50, 1.00, 1.30, 2.00, 0.30)),
        brace_xs=(0.45, 1.35, 2.25, 3.15, 4.05, 4.95, 5.85),
        brace_r=0.05, brace_len_drop=0.45, brace_reach=0.30,
        anchor_xs=(0.5, 1.5, 2.5, 3.5, 4.5, 5.5),
        ribbon_xs=(0.8, 1.8, 2.8, 3.8, 4.8, 5.8),
        sign=dict(cx=-1.0, cy=-0.10, post_h=1.30, w=0.55, h=0.40),
    ),

    material=dict(
        scale=dict(rock_face=2.0, rock_far=9.0, wood_dark=0.8),
        # 감독 r3 — 암벽/판이 어두운 적갈 덩어리로 뭉쳐 판독 불가 → 알베도 상향 틴트
        rock_tint=(1.25, 1.22, 1.18),
        # 감사 B-12-2 — 원경 암벽은 별도 재질(타일 9 m·대기원근 틴트)로 격자 노출 억제
        rock_far_tint=(0.92, 0.98, 1.10),
        wood_tint=(1.30, 1.25, 1.15),
        # 감사 B-12-3 — 0.35 는 선형값이라 정오광에서 하드에지 백색 판이 된다.
        abyss_color=(0.06, 0.07, 0.08),        # 안개톤 상수색(무한낙차 바닥)
        haze_color=(0.20, 0.22, 0.24),
        chain_color=(0.09, 0.09, 0.10), chain_metallic=0.7, chain_rough=0.5,
        ribbon_color=(0.30, 0.03, 0.03),
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
    # 감독 r3 — 벽면 법선이 −Y. 정면광을 벽면에 때리려면 태양이 −Y쪽에서 와야 함.
    # 월드 태양 az≈33.5+offset. offset 240(az≈273.5≈−Y 방위)로 벽면·판을 정면광.
    # (r2 의 30(az63.5)은 벽 뒤에서 와 전체가 그늘 덩어리였음.)
    SUN_AZ_OFFSET=240.0,

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
# [C] 경로 / 에셋 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene12")

ASSET_ROLES = ["rock_face", "wood_dark", "hdri", "mdl"]


# ===========================================================================
# 판 기하 — 판 중심선 y, 단별 상면 z(x) 콜백
# ===========================================================================
def plank_center_y():
    pk = PARAMS["planks"]
    y_in = pk["wall_overlap"]                   # 벽 안쪽(+Y) 끝
    y_out = pk["wall_overlap"] - pk["width"]    # 개방측(−Y) 끝
    return (y_in + y_out) / 2.0


def plank_surface_z(x):
    """단별 판 상면 z(x). x≤0(랜딩)=z_start, 이후 +X로 riser 하강."""
    pk = PARAMS["planks"]
    z0 = pk["z_start"]
    if x <= pk["x0"]:
        return z0
    i = min(int((x - pk["x0"]) / pk["tread"]), pk["nsteps"] - 1)
    return z0 - (i + 1) * pk["riser"]


def plank_pt(i):
    """판 i(0-based)의 중심 (x, 상면 z). 카메라·스모크가 기하 상수 없이 산출."""
    pk = PARAMS["planks"]
    cx = pk["x0"] + (i + 0.5) * pk["tread"]
    tz = pk["z_start"] - (i + 1) * pk["riser"]
    return cx, tz


def wall_face_y():
    """벽 패널들의 개방측(−Y) 최전면 y (판이 붙는 벽면)."""
    return min(p["y0"] for p in PARAMS["wall_panels"])


# ===========================================================================
# [D] 카메라 프리셋 — 밴드 h/d 는 판 표면(plank_ref) 기준으로 시프트
# ===========================================================================
def build_views():
    pk = PARAMS["planks"]
    cy = plank_center_y()
    plank_ref = pk["z_start"]                   # 카메라 x(<0=랜딩)에서 판 표면 z
    views = sc.grid_views(cy)                   # gy=판 중심선
    # 판 표면 기준으로 eye/tgt z 시프트(랜딩부 plank_ref=z_start)
    for v in views.values():
        v["eye"][2] += plank_ref
        v["tgt"][2] += plank_ref
    n = pk["nsteps"]
    x1, z1 = plank_pt(0)                        # 판 1 (1-based)
    xM, zM = plank_pt(9)                        # 판 10 (1-based) = 카메라 기준판
    xL, zL = plank_pt(n - 1)                    # 판 20 (1-based)
    wy = wall_face_y()
    # walk_down: 상부 랜딩에서 하강 잔도를 내려봄(편측 개방)
    views["walk_down"] = dict(eye=[-1.5, cy, plank_ref + 1.5],
                              tgt=[xL, cy, zL + 0.5])
    # edge_void: 감독 r3 — 판 10 위 h1.2 에서 판 라인 소실 방향(→ 판 20 너머 허공).
    #   기하 상수 산출: eye=(판10.x, cy, 판10.z+1.2), tgt=판 라인 하단 연장.
    views["edge_void"] = dict(eye=[xM, cy, zM + 1.2],
                              tgt=[xL, cy, zL - 0.6])
    # lookup_wall: 하부 판에서 벽·쇠사슬 올려봄
    views["lookup_wall"] = dict(eye=[xL - 1.0, cy, zL + 1.4],
                                tgt=[x1, 0.5, z1 + 0.6])
    # across_gorge: 감독 r3 — 벽면에서 −Y 로 8m 떨어진 허공, 판 라인 중간 높이에서
    #   잔도·암벽·판을 측면 프로파일로. 기하 상수 산출(벽면 y·판10 사용).
    views["across_gorge"] = dict(eye=[xM, wy - 8.0, zM + 0.6],
                                 tgt=[xM, wy, zM - 0.4])
    # entry_ledge / trail_end: 감사 A-12-1/2 로 신설한 암반 선반 접속 검수 +
    #   B-12-1(하늘·심연 회복) 확인용 개방측 컷.
    views["entry_ledge"] = dict(eye=[-9.5, cy - 5.0, plank_ref + 2.2],
                                tgt=[-1.0, cy, plank_ref - 0.3])
    views["trail_end"] = dict(eye=[3.2, cy - 6.0, zM - 0.6],
                              tgt=[8.5, cy, zL - 0.2])
    return views


# ===========================================================================
# [E] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. walk_down    — 편측(−Y) 완전 개방, 판 계단만 낙차 증거인가
 2. edge_void    — 개방측 하부 안개톤 대지(z=−30)로 무한낙차가 읽히나
 3. h0.3~2.0     — 밴드가 판 표면 기준으로 시프트되어 눈높이가 판 위인가
 4. lookup_wall  — 벽측 쇠사슬 힌트(cue_railing)가 판 위 0.8에 걸리나
 5. across_gorge — 원경 암벽이 후퇴해 하늘/심연이 프레임에 살아 있나 (B-12-1)
 6. entry_ledge / trail_end — 진입·탈출 암반 선반이 잔도 양끝에 접속되나
 7. 판↔벽    — 패널1 y0=−0.02 로 x 3..7 구간 슬롯(0.12 m)이 사라졌나
 8. cue_railing OFF/ON — 위험 기하(판·벽) 트랜스폼 동일한가"""


def main():
    smoke = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode or smoke)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view
    from pxr import UsdGeom

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene12")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene12"

    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        M = {}
        M["rock"] = tex("rock_face", "/World/Looks/RockFace", sca["rock_face"],
                        tint=mp["rock_tint"])
        # 원경 전용 암벽(타일 9 m + 대기원근 틴트) — B-12-2 격자 반복 억제
        M["rock_far"] = tex("rock_face", "/World/Looks/RockFar",
                            sca["rock_far"], tint=mp["rock_far_tint"])
        M["wood"] = tex("wood_dark", "/World/Looks/Planks", sca["wood_dark"],
                        tint=mp["wood_tint"])
        M["abyss"] = sc.make_pbr(stage, "/World/Looks/Abyss",
                                 diffuse_color=mp["abyss_color"],
                                 roughness_const=1.0, specular_level=0.0)
        M["haze"] = sc.make_pbr(stage, "/World/Looks/Haze",
                                diffuse_color=mp["haze_color"],
                                roughness_const=1.0, specular_level=0.0)
        M["chain"] = sc.make_pbr(stage, "/World/Looks/Chain",
                                 diffuse_color=mp["chain_color"],
                                 metallic=mp["chain_metallic"],
                                 roughness_const=mp["chain_rough"])
        M["ribbon"] = sc.make_pbr(stage, "/World/Looks/Ribbon",
                                  diffuse_color=mp["ribbon_color"],
                                  roughness_const=0.9)
        return M

    # -------------------------------------------------------------------
    def build_wall(M):
        """수직 암벽 5장(rock_face) — x 겹침 + 미세 Y 돌출(요철) + 양단 연장."""
        wl = PARAMS["wall"]
        h = wl["z_top"] - wl["z_bot"]
        cz = (wl["z_top"] + wl["z_bot"]) / 2.0
        for i, p in enumerate(PARAMS["wall_panels"]):
            cx = (p["x0"] + p["x1"]) / 2.0
            cy = p["y0"] + wl["thick"] / 2.0
            sc.add_box(stage, f"{ROOT}/Wall_{i}", (cx, cy, cz),
                       (p["x1"] - p["x0"], wl["thick"], h), M["rock"],
                       collider=True)

    def build_shelves(M):
        """진입/탈출 암반 선반 — 감사 A-12-1/2 (허공 시작·막장 종점 해소).
          상부 : 상면 z=0   → 랜딩(x −2..0, 상면 0) 의 −X 로 접속 (x −8.1..−1.9)
          하부 : 상면 z=−3.2 → 판20(x 5.7..6.0, 상면 −3.2) 의 +X 로 접속
                 + 목판 3장 암시 + 원경 쪽 암반 선반(트레일 지속)."""
        for tag, s in (("Entry", PARAMS["entry_shelf"]),
                       ("Exit", PARAMS["exit_shelf"])):
            sc.add_box(stage, f"{ROOT}/Shelf_{tag}",
                       (s["cx"], s["cy"], s["cz"]),
                       (s["sx"], s["sy"], s["sz"]), M["rock"], collider=True)
        et = PARAMS["exit_trail"]
        pk = PARAMS["planks"]
        cy = plank_center_y()
        Ly = pk["width"]
        for i in range(et["n"]):
            xa = et["x0"] + i * et["tread"]
            sc.add_box(stage, f"{ROOT}/TrailPlank_{i}",
                       (xa + et["tread"] / 2.0, cy,
                        et["z_top"] - pk["thick"] / 2.0),
                       (et["tread"], Ly, pk["thick"]), M["wood"],
                       collider=True)
        lg = et["ledge"]
        sc.add_box(stage, f"{ROOT}/Shelf_Ledge", (lg["cx"], lg["cy"], lg["cz"]),
                   (lg["sx"], lg["sy"], lg["sz"]), M["rock"], collider=True)

    def build_planks(M):
        """목판 캔틸레버 계단 20단 — 벽에서 3cm 겹쳐 −Y 로 개방."""
        pk = PARAMS["planks"]
        y_in = pk["wall_overlap"]               # +Y(벽 안)
        y_out = pk["wall_overlap"] - pk["width"]
        cy = (y_in + y_out) / 2.0
        Ly = y_in - y_out
        # 상부 랜딩(벽 부착)
        tl = PARAMS["top_landing"]
        sc.add_box(stage, f"{ROOT}/TopLanding",
                   ((tl["x0"] + tl["x1"]) / 2.0, cy,
                    pk["z_start"] - tl["thick"] / 2.0),
                   (tl["x1"] - tl["x0"], Ly, tl["thick"]), M["wood"],
                   collider=True)
        for i in range(pk["nsteps"]):
            xa = pk["x0"] + i * pk["tread"]
            xb = xa + pk["tread"]
            ztop = pk["z_start"] - (i + 1) * pk["riser"]
            sc.add_box(stage, f"{ROOT}/Plank_{i}",
                       ((xa + xb) / 2.0, cy, ztop - pk["thick"] / 2.0),
                       (pk["tread"], Ly, pk["thick"]), M["wood"],
                       collider=True)

    def build_abyss(M):
        """하부 안개톤 대지 z=−30 + 원경 맞은편/협곡 암벽 — 지평 폐쇄."""
        ab = PARAMS["abyss"]
        sc.add_box(stage, f"{ROOT}/Abyss",
                   ((ab["x0"] + ab["x1"]) / 2.0, (ab["y0"] + ab["y1"]) / 2.0,
                    ab["z_top"] - ab["thick"] / 2.0),
                   (ab["x1"] - ab["x0"], ab["y1"] - ab["y0"], ab["thick"]),
                   M["abyss"], collider=True)
        for tag, c in (("Far", PARAMS["far_cliff"]),
                       ("Gorge", PARAMS["gorge_cliff"])):
            cz = (c["z0"] + c["z1"]) / 2.0
            sc.add_box(stage, f"{ROOT}/Cliff_{tag}",
                       ((c["x0"] + c["x1"]) / 2.0, (c["y0"] + c["y1"]) / 2.0,
                        cz),
                       (c["x1"] - c["x0"], c["y1"] - c["y0"],
                        c["z1"] - c["z0"]), M["rock_far"], collider=True)
        hz = PARAMS["haze"]
        sc.add_box(stage, f"{ROOT}/Haze", (hz["cx"], hz["cy"], hz["cz"]),
                   (hz["sx"], hz["sy"], hz["sz"]), M["haze"])

    def build_cues(M):
        """벽측 쇠사슬 힌트(cue_railing) : 판 위 0.8, 가는 원기둥 선.
        build_railing_line(+X 하강 전용)에 ground_fn=판 표면 z 를 주어 포스트가
        판에 착지하게 함(허공 포스트 방지)."""
        if not cfg["cue_railing"]:
            return
        pk = PARAMS["planks"]
        ch = PARAMS["chain"]
        run = pk["nsteps"] * pk["tread"]
        drop = pk["nsteps"] * pk["riser"]
        sc.build_railing_line(
            stage, f"{ROOT}/Chain", ch["y"], pk["x0"], pk["x0"], run, drop,
            plank_surface_z, M["chain"], rail_h=ch["rail_h"],
            post_r=ch["post_r"], spacing=ch["spacing"], rail_r=ch["rail_r"],
            rail_mid_r=ch["rail_mid_r"], rail_mid_drop=0.35)

    def build_dressing(M):
        """맥락 드레싱(cue_scene_dressing) — 감사 C '휑함 5/5' 대응.
        암벽 요철(B-12-4) · 판 하부 버팀목(캔틸레버 근거) · 벽 앵커 · 기원 리본 ·
        목재 경고판. 전부 add_box/add_cylinder 조합, 위험 기하 트랜스폼 불변."""
        d = PARAMS["dressing"]
        pk = PARAMS["planks"]
        ch = PARAMS["chain"]
        # 1) 암벽 요철 — 벽면(y≈0)에서 −Y 로 돌출. z 는 판 라인과 간섭 없게 검증됨.
        for i, (rx, rz, sx, sz, prot) in enumerate(d["relief"]):
            sc.add_box(stage, f"{ROOT}/Relief_{i}",
                       (rx, (0.12 - prot) / 2.0, rz),
                       (sx, prot + 0.12, sz), M["rock"], collider=True)
        # 2) 판 하부 사선 버팀목 — 벽 하단 → 판 하면 외측 (rotX)
        for i, bx in enumerate(d["brace_xs"]):
            ztop = plank_surface_z(bx) - pk["thick"]
            y_w, y_o = 0.02, -d["brace_reach"] + 0.02
            z_hi, z_lo = ztop - 0.01, ztop - 0.01 - d["brace_len_drop"]
            dz = z_hi - z_lo
            ang = math.degrees(math.atan2(y_w - y_o, dz))
            L = math.hypot(y_w - y_o, dz)
            sc.add_cylinder(stage, f"{ROOT}/Brace_{i}",
                            (bx, (y_w + y_o) / 2.0, (z_lo + z_hi) / 2.0),
                            d["brace_r"], L, M["wood"], rotX=ang)
        # 3) 벽 앵커(쇠사슬 지점) — 벽면에서 −Y 로 돌출한 짧은 원기둥
        for i, ax in enumerate(d["anchor_xs"]):
            az = plank_surface_z(ax) + ch["rail_h"]
            sc.add_cylinder(stage, f"{ROOT}/Anchor_{i}", (ax, -0.06, az),
                            0.03, 0.22, M["chain"], rotX=90.0)
        # 4) 붉은 기원 리본 — 쇠사슬(직선 보간)에 매달림
        run = pk["nsteps"] * pk["tread"]
        drop = pk["nsteps"] * pk["riser"]
        for i, rx in enumerate(d["ribbon_xs"]):
            z_rail = ch["rail_h"] - drop * (rx - pk["x0"]) / run
            sc.add_box(stage, f"{ROOT}/Ribbon_{i}", (rx, -0.02, z_rail - 0.18),
                       (0.03, 0.05, 0.30), M["ribbon"])
        # 5) 목재 경고판(상부 랜딩)
        sg = d["sign"]
        sc.add_cylinder(stage, f"{ROOT}/SignPost",
                        (sg["cx"], sg["cy"], pk["z_start"] + sg["post_h"] / 2.0),
                        0.04, sg["post_h"], M["wood"])
        sc.add_box(stage, f"{ROOT}/SignBoard",
                   (sg["cx"], sg["cy"], pk["z_start"] + sg["post_h"] - 0.10),
                   (sg["w"], 0.05, sg["h"]), M["wood"])

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 : 판을 z=0 평판 보행로로(낙차 제거)."""
        pk = PARAMS["planks"]
        cy = plank_center_y()
        run = pk["nsteps"] * pk["tread"]
        sc.add_box(stage, f"{ROOT}/FlatWalk",
                   (pk["x0"] + run / 2.0, cy, pk["z_start"] - pk["thick"] / 2.0),
                   (run, pk["width"], pk["thick"]), M["wood"], collider=True)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_wall(M)
    build_shelves(M)                 # A-12-1/2 진입·탈출 접속 (경로 필수 = 상시)
    if cfg["hazard_stairs"]:
        build_planks(M)
        build_cues(M)
    else:
        build_flat_fill(M)
    build_abyss(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    z_bot = plank_surface_z(PARAMS["planks"]["x0"]
                            + PARAMS["planks"]["nsteps"]
                            * PARAMS["planks"]["tread"])
    print(f"[기하] 잔도 {PARAMS['planks']['nsteps']}단 낙차 {-z_bot:.3f} "
          f"z_bot={z_bot:.3f} (개방측 −Y, 바닥 z=-30)")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke:
        print("[SMOKE] 부팅+조립+조명 완료 — 렌더 없이 조기 종료")
        n = PARAMS["planks"]["nsteps"]
        for lbl, i in (("판1", 0), ("판10", 9), ("판20", n - 1)):
            px, pz = plank_pt(i)
            print(f"[SMOKE] {lbl}(i={i}) x={px:.3f} z={pz:.3f}")
        print(f"[SMOKE] 벽면 y(개방측 최전면) = {wall_face_y():.3f} "
              f"판 중심선 y = {plank_center_y():.3f}")
        for vn in ("across_gorge", "edge_void", "walk_down", "lookup_wall"):
            v = build_views()[vn]
            print(f"[SMOKE] cam {vn:<12} eye={['%.2f' % e for e in v['eye']]} "
                  f"tgt={['%.2f' % t for t in v['tgt']]}")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views()
    _v0 = views["walk_down"]
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

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    if capture_mode:
        out_dir_default = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, views, out_dir_default,
                            set_render_mode, look_from)
        simulation_app.close()
        return

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene12_{ts}.png")
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
