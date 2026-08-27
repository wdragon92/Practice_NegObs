# -*- coding: utf-8 -*-
"""
scene07_wornstone_temple.py — NegObs 인공씬 7호: 사찰 진입 마모 석단 (Isaac Sim 4.5)

사양서 : Docs/briefs/multi_scene_brief_v3.md §A(회귀 체크리스트)·§D(scene07)·§B(빌더)
공통 라이브러리 : scene_common.py / 골격 관례 : scene03_riverbank.py

유형 (T16 마모 석단): **비직선 단코 × 소실점 규칙 붕괴**.
  마모·부정형 석단(numpy 고정 시드 지터)이 상부 사찰 마당에서 하부 진입로로
  하강. 단코가 직선이 아니라 소실점 규칙이 무너지고, 낮은 시점에서 낙차 경계가
  석축 사면·이끼 톤에 녹아든다. 낙차 증거는 **부정형 단코 + 측면 노후 석축 사면
  + 하부 노송(눈높이 아래 수관)**.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene07_wornstone_temple.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene07_wornstone_temple.py
조립 스모크(조기 종료 — 렌더 없이 부팅+조립만 검증):
    NEGOBS_SMOKE=1 python scene07_wornstone_temple.py

좌표계: Z-up, m, 진행축 +X. 낙차 시작 모서리 = x=0 (마당 어깨, 계단 상단).
        계단은 +X 하강(관례) → x=0 상부 마당(z=0), x=run 하부 진입로.

────────────────────────────────────────────────────────────────────────────
기하 핵심 (감독 보충 반영):
  build_worn_stone_stairs 는 (프림, 단별 평균 상면 z 리스트, run) 3튜플 반환.
  → 반환된 mean_tops[-1](최하단 평균 상면 z)로 **하부 진입로 z·측면 석축 사면
    drop**을 정합(부유·틈 방지). courtyard 는 z_top=0(계단 상단 지면)에 정합.
  이끼 톤: stone_worn 재질에 tint (0.85,0.95,0.8).
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
# [A] SCENE_CONFIG — 표준 7키. 이 유형은 무난간 석단(cue_railing 기본 False).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 계단·석축·마당을 z=0 평지로 (기하 토글)
    "cue_railing":        False,   # 사찰 석단엔 난간 미관행 — 코드 경로만 예약
    "cue_tactile":        False,   # 미사용(코드 경로만)
    "cue_material_break": True,    # 마당 gravel vs 계단 stone_worn 대비
    "cue_sign":           False,   # [선택] 미구현 — 키만 예약
    "cue_scene_dressing": True,    # 노송·담장·이끼 톤 일괄
    "cue_nosing":         False,   # 마모석 단코엔 논슬립 띠 미관행(코드 경로만)
}


# ===========================================================================
# [B] PARAMS — §D 치수 + 재질/조명/캡처. NEGOBS_PARAMS_OVERRIDE 머지.
# ===========================================================================
PARAMS = dict(
    # --- 마모 석단 : 18단, riser_mu 0.17, tread_mu 0.38, blocks 5, seed 77 ---
    stairs=dict(x0=0.0, y0=-1.6, y1=1.6, nsteps=18, riser_mu=0.17,
                tread_mu=0.38, blocks=5, seed=77, base_z=-3.9, z_top=0.0,
                jr=0.03, jt=0.05, jz=0.02, jyaw=3.0),   # jt 0.10→0.05:
                # 감독 r1 — 전후 지터 과대로 단코 블록이 사면 위 '이빨'처럼
                # 흩어져 보임 → 축소(단코 비직선성은 jz/jyaw 로 유지)
    # --- 상부 사찰 마당 : 마사토(gravel) 평탄, z=0. [A-07-3] y±40→±55 확장 ---
    courtyard=dict(x0=-14.0, x1=0.0, y0=-55.0, y1=55.0, z_top=0.0, thick=0.5),
    # 낮은 담장 2 (마당 좌우, rock_wall 몸체 + stone_worn 캡)
    #   [D-07-5] cy ±7 → ±8: 법당 지붕(y±6.2) 바깥에 두어 '닫힌 경내'가 되게.
    walls=[dict(cy=8.0), dict(cy=-8.0)],
    wall=dict(x0=-14.0, x1=-0.4, t=0.5, h=0.7, cap_over=0.06, cap_h=0.08),
    # 마당 뒤(−X) 가로 담장 1본 — 경내 폐합
    back_wall=dict(cx=-14.0, t=0.5, len_y=16.5, h=0.7),
    # --- 하부 진입로 : dirt_park, z=mean_tops[-1](런타임 정합) ---
    #   [A-07-1] x_len 16(→x22.84 끝) 은 능선 앞면 x29.84 와 7.0 m 지면 공백을
    #   남겨 하강 후 '세계의 끝'이 나왔다. x0=0(계단 하부까지 연장)·x1=30.84 로
    #   재정의하고, 그 너머는 lowfield 가 받는다.
    approach=dict(x0=0.0, x1=30.84, y0=-55.0, y1=55.0, thick=1.0),
    # 하부 들판(진입로 끝 ~ 능선 기저) — 지면 공백 완전 제거
    lowfield=dict(x0=30.84, x1=95.0, y0=-70.0, y1=70.0, thick=1.0),
    # 마당 뒤 들판 — [A-07-3] 마당이 x=−14 에서 절벽으로 끝나던 것 해소
    backfield=dict(x0=-46.0, x1=-14.0, y0=-55.0, y1=55.0, z_top=0.0, thick=0.8),
    # --- 좌우 노후 석축 사면 : rock_wall 경사 박스(계단 회랑 y±1.6 비움) ---
    corridor=dict(y0=-1.6, y1=1.6),        # 계단 폭 = 회랑(석축이 비우는 대역)
    masonry=dict(thick=0.5, y_edge=55.0,   # z0=0..drop(런타임), run=stair run
                 seam=0.05),               # 감독 r1 — 사면 패널이 계단 측면을
                 # 0.05 겹쳐 마모석 단코 지터가 만든 틈(검은 세로 슬릿) 봉합
    # [A-07-4] 마당 어깨 축대 난간석 — 사면(24°) 우회 하강 차단.
    #   계단 회랑(y±1.6) 만 열고 나머지 어깨 전 구간을 h0.9 석축 난간으로 막는다.
    #   → "계단이 유일한 하강로" 성립. 동시에 계단 상단으로 사람을 유도(A-07-5).
    edge_wall=dict(x0=-0.3, x1=0.3, h=0.9, cap_h=0.09, cap_over=0.05),
    # --- 지평 폐쇄 ---
    # 상부 뒤 숲 라인 : 생울타리 3 + 나무 3 (x≈-12, 마당 위)
    # [D-07] cx −12 → −17: 마당 뒤 담장(x=−14) **밖**(backfield 위)으로 물림.
    #   기존 −12 는 법당 지붕 기둥(x −12.24)과 관통했다.
    back_hedge=dict(cx=-17.0, sx=1.2, length=22.0, h=1.8),
    back_hedges=[dict(cy=-22.0), dict(cy=0.0), dict(cy=22.0)],
    back_trees=[dict(cx=-19.5, cy=-14.0), dict(cx=-19.5, cy=0.0),
                dict(cx=-19.5, cy=14.0)],
    # 하부 앞 능선 : [B-07-1] 단색 판때기 2매 → **3단 깊이**(근/중/원경) 로 분리.
    #   tone 키가 재질을 고르고, 근경 능선 위에는 나무를 심어 실루엣에 굴곡을 준다.
    ridge=[dict(cx=30.0, h=7.0, sy=110.0, t=6.0, z_off=0.0, tone="near"),
           dict(cx=42.0, h=12.0, sy=130.0, t=8.0, z_off=0.0, tone="mid"),
           dict(cx=58.0, h=20.0, sy=160.0, t=10.0, z_off=0.0, tone="far")],
    # 근경 능선 상면 수목(실루엣 굴곡) — x 는 run+cx 기준 상대
    ridge_trees=[dict(cx=28.0, cy=-26.0), dict(cx=31.5, cy=-14.0),
                 dict(cx=29.0, cy=-2.0), dict(cx=32.0, cy=9.0),
                 dict(cx=28.5, cy=20.0), dict(cx=31.0, cy=31.0)],
    # --- 노송 : 하부 5(수관 앵커, 계열③) + 마당 1 ---
    pines=[dict(cx=4.5, cy=6.0, where="approach"),
           dict(cx=3.0, cy=-6.0, where="approach"),
           dict(cx=9.5, cy=7.5, where="approach"),
           dict(cx=10.5, cy=-7.5, where="approach"),
           dict(cx=16.0, cy=5.0, where="approach"),
           dict(cx=-4.0, cy=6.0, where="courtyard")],

    # --- [감사 v4 D-07] 사원 건축 요소 (판독어 "산사 경내") ---
    # 일주문(산문) : 계단 상단 어깨 바로 뒤. 계단(x≥0)과 x 겹침 없음.
    gate=dict(x0=-2.2, x1=-0.6, y0=-2.8, y1=2.8, z_roof=3.4, post_r=0.22,
              roof_t=0.35),
    # 법당 1동 : 몸체 + 오버행 지붕(캐노피)
    hall=dict(cx=-9.5, cy=0.0, sx=5.0, sy=11.0, h=3.2,
              roof=dict(x0=-12.4, x1=-6.6, y0=-6.2, y1=6.2, z_roof=3.2,
                        post_r=0.16, roof_t=0.45)),
    # 석등 2 (계단 상단 앞마당)
    lanterns=[dict(cx=-3.2, cy=3.6), dict(cx=-3.2, cy=-3.6)],
    lantern=dict(base_r=0.20, base_h=0.85, body=0.52, cap_w=0.78, cap_h=0.14),
    # 당간지주 2 (계단 상단 양측 석주) — 계단 폭(y±1.6) 밖
    #   cy ±2.5 → ±3.6: 일주문 기둥(y ±2.58, r0.22)과 관통하지 않도록 바깥으로
    flagpoles=[dict(cx=-0.9, cy=3.6), dict(cx=-0.9, cy=-3.6)],
    flagpole=dict(t=0.36, h=2.4),

    # --- 재질 ---
    material=dict(
        # [B-07-2] rock_wall 1.5 → 4.0: 폭 55 m 석축에 1.5 m 타일은 '조약돌
        #   포장/기와'로 읽혔다. 노후 석축 블록 스케일 정상화.
        scale=dict(stone_worn=1.2, gravel=0.6, dirt_park=1.0, rock_wall=4.0,
                   grass=4.0),
        stone_moss_tint=(0.85, 0.95, 0.8),    # 이끼 톤 (녹색기)
        grass_tint=(0.55, 0.68, 0.42),        # 체크리스트 표준
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        roof_color=(0.045, 0.030, 0.018),     # 어두운 목조 지붕(암색 규칙)
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # [B-07-1] 능선 3단 톤 — 근경 짙은 숲 → 원경 대기 톤. 전부 암색 규칙 내.
        ridge_near=(0.030, 0.038, 0.024),
        ridge_mid=(0.040, 0.046, 0.038),
        ridge_far=(0.052, 0.056, 0.060),
    ),

    # --- 조명: scene01 noon 검증 상수 그대로 ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # 감독 r1 — 월드 태양 az≈33.5+offset, 그림자는 az−180. 표준 171.5(az205)는
    # +X향 라이저를 음영에 넣어 정면 관람 씬에서 계단이 흑색 실루엣이 됨.
    # → offset 0.0(az33.5)로 +X향 라이저 정면광.
    SUN_AZ_OFFSET=0.0,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene07")

ASSET_ROLES = ["stone_worn", "gravel", "dirt_park", "rock_wall", "grass",
               "hdri", "mdl"]


# ===========================================================================
# [D] 카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷 (§D)
# ===========================================================================
def build_views(run, z_bot):
    views = sc.grid_views(0.0)                 # h{0.3,0.9,1.8}×d{2,5,10}, +X
    # temple_walk: 마당에서 진행방향 — 단코가 석축·이끼에 녹아 낙차 소실
    views["temple_walk"] = dict(eye=[-5.0, 0.0, 1.3], tgt=[5.0, 0.0, 0.4])
    # stair_down: 계단 상단 어깨에서 아래로 부감(부정형 단코 확인)
    views["stair_down"] = dict(eye=[-0.6, 0.0, 1.7],
                               tgt=[run * 0.6, 0.0, z_bot + 0.5])
    # approach_lookup: 하부 진입로에서 역방향 — 석축·노송 앵커 올려봄
    views["approach_lookup"] = dict(eye=[run + 4.0, 2.5, z_bot + 1.4],
                                    tgt=[1.0, 0.0, -0.6])
    # side_masonry: 측면에서 노후 석축 사면 사교 조망
    views["side_masonry"] = dict(eye=[run * 0.5, 9.0, z_bot + 2.2],
                                 tgt=[run * 0.5, 0.0, z_bot + 0.5])
    return views


# ===========================================================================
# [E] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. temple_walk     — 마당 눈높이에서 단코가 석축·이끼에 녹아 낙차 소실되나
 2. h0.3·d5~10      — 마당 어깨가 평지로 보이고 단코가 비직선(소실점 붕괴)인가
 3. stair_down      — 18단 부정형 마모석단이 부감으로 명확한가
 4. approach_lookup — 하부 노송 수관이 마당 눈높이 아래인가 (계열③ 앵커)
 5. side_masonry    — 좌우 노후 석축 사면이 계단과 정합(부유·틈 없음)한가
 6. 지평 폐쇄        — 앞(능선 3단)·뒤(숲 라인)이 허공을 막는가
 7. cue_railing OFF/ON — 위험 기하(석단·석축) 트랜스폼 동일한가
 8. 보행 연속성      — 진입로 끝(x30.84) 너머 들판이 이어지는가(공백 0)
 9. 우회 차단        — 마당 어깨 축대 난간석으로 계단만 하강로인가
10. 맥락            — 일주문·법당·석등·당간지주가 '산사 경내'로 읽히나"""


def main():
    smoke = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # ── 0단계: 에셋 존재 검사 ──
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    # ── 1단계: Isaac Sim 부팅 (스모크도 조립 검증 위해 headless 부팅) ──
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
    UsdGeom.Xform.Define(stage, "/World/Scene07")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene07"

    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        M = {}
        # 마모석 — 이끼 톤 tint
        M["stone"] = tex("stone_worn", "/World/Looks/Stone",
                         sca["stone_worn"], tint=mp["stone_moss_tint"])
        # 담장 캡용(이끼 없는 마모석)
        M["stone_cap"] = tex("stone_worn", "/World/Looks/StoneCap",
                             sca["stone_worn"])
        M["gravel"] = tex("gravel", "/World/Looks/Gravel", sca["gravel"])
        M["dirt"] = tex("dirt_park", "/World/Looks/Dirt", sca["dirt_park"])
        M["rock"] = tex("rock_wall", "/World/Looks/Rock", sca["rock_wall"])
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        for tone in ("near", "mid", "far"):
            M[f"ridge_{tone}"] = sc.make_pbr(
                stage, f"/World/Looks/Ridge_{tone}",
                diffuse_color=mp[f"ridge_{tone}"], roughness_const=0.95,
                specular_level=0.0)
        M["roof"] = sc.make_pbr(stage, "/World/Looks/Roof",
                                diffuse_color=mp["roof_color"],
                                roughness_const=0.9, specular_level=0.0)
        return M

    # -------------------------------------------------------------------
    # 마모 석단 — 반환 mean_tops / run 을 하부·석축 정합에 사용
    # -------------------------------------------------------------------
    def build_stairs(M):
        st = PARAMS["stairs"]
        stair_mtl = M["stone"] if cfg["cue_material_break"] else M["gravel"]
        prims, mean_tops, run = sc.build_worn_stone_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["nsteps"], st["riser_mu"], st["tread_mu"], st["blocks"],
            st["seed"], stair_mtl, st["base_z"], z_top=st["z_top"],
            jr=st["jr"], jt=st["jt"], jz=st["jz"], jyaw=st["jyaw"])
        z_bot = mean_tops[-1]                  # 최하단 평균 상면 z
        print(f"[기하] 마모석단 {len(mean_tops)}단 run={run:.3f} "
              f"z_top=0 z_bot={z_bot:.3f} (드롭 {-z_bot:.3f})")
        return run, z_bot

    def build_courtyard(M):
        """상부 사찰 마당 : 마사토(gravel) 평탄 + 담장 3(좌우+뒤) + 뒤 들판."""
        cy = PARAMS["courtyard"]
        cyc = (cy["y0"] + cy["y1"]) / 2.0
        sc.add_box(stage, f"{ROOT}/Courtyard",
                   ((cy["x0"] + cy["x1"]) / 2.0, cyc,
                    cy["z_top"] - cy["thick"] / 2.0),
                   (cy["x1"] - cy["x0"], cy["y1"] - cy["y0"], cy["thick"]),
                   M["gravel"], collider=True)
        # [A-07-3] 마당 뒤 들판 — 마당이 x=−14 에서 절벽으로 끝나지 않게
        bf = PARAMS["backfield"]
        sc.add_box(stage, f"{ROOT}/BackField",
                   ((bf["x0"] + bf["x1"]) / 2.0,
                    (bf["y0"] + bf["y1"]) / 2.0,
                    bf["z_top"] - bf["thick"] / 2.0),
                   (bf["x1"] - bf["x0"], bf["y1"] - bf["y0"], bf["thick"]),
                   M["grass"], collider=True)
        # 담장 2 (몸체 rock_wall + 상면 stone_worn 캡, 1mm 오프셋)
        wl = PARAMS["wall"]
        for i, w in enumerate(PARAMS["walls"]):
            cxw = (wl["x0"] + wl["x1"]) / 2.0
            lenx = wl["x1"] - wl["x0"]
            sc.add_box(stage, f"{ROOT}/Wall_{i}",
                       (cxw, w["cy"], wl["h"] / 2.0),
                       (lenx, wl["t"], wl["h"]), M["rock"], collider=True)
            sc.add_box(stage, f"{ROOT}/WallCap_{i}",
                       (cxw, w["cy"], wl["h"] + wl["cap_h"] / 2.0),
                       (lenx + 2 * wl["cap_over"], wl["t"] + 2 * wl["cap_over"],
                        wl["cap_h"]), M["stone_cap"], collider=True)
        # 뒤 가로 담장 1본 (경내 폐합)
        bw = PARAMS["back_wall"]
        sc.add_box(stage, f"{ROOT}/BackWall", (bw["cx"], 0.0, bw["h"] / 2.0),
                   (bw["t"], bw["len_y"], bw["h"]), M["rock"], collider=True)
        sc.add_box(stage, f"{ROOT}/BackWallCap",
                   (bw["cx"], 0.0, bw["h"] + wl["cap_h"] / 2.0),
                   (bw["t"] + 2 * wl["cap_over"],
                    bw["len_y"] + 2 * wl["cap_over"], wl["cap_h"]),
                   M["stone_cap"], collider=True)

    def build_approach(M, run, z_bot):
        """하부 진입로(dirt) + 그 너머 들판(grass) — [A-07-1] 지면 공백 제거."""
        ap = PARAMS["approach"]
        cyc = (ap["y0"] + ap["y1"]) / 2.0
        sc.add_box(stage, f"{ROOT}/Approach",
                   ((ap["x0"] + ap["x1"]) / 2.0, cyc,
                    z_bot - ap["thick"] / 2.0),
                   (ap["x1"] - ap["x0"], ap["y1"] - ap["y0"], ap["thick"]),
                   M["dirt"], collider=True)
        lf = PARAMS["lowfield"]
        sc.add_box(stage, f"{ROOT}/LowField",
                   ((lf["x0"] + lf["x1"]) / 2.0,
                    (lf["y0"] + lf["y1"]) / 2.0, z_bot - lf["thick"] / 2.0),
                   (lf["x1"] - lf["x0"], lf["y1"] - lf["y0"], lf["thick"]),
                   M["grass"], collider=True)

    def build_masonry(M, run, z_bot):
        """좌우 노후 석축 사면 : rock_wall 경사 박스. 계단 회랑(y±1.6) 비움.
        z0=0(마당)→ z_bot(진입로) 로 하강 = 계단 낙차와 정합."""
        co = PARAMS["corridor"]
        ms = PARAMS["masonry"]
        drop = -z_bot                          # 0 → z_bot
        seam = ms["seam"]                      # 계단 측면으로 0.05 겹침(틈 봉합)
        # 회랑 y±1.6 은 계단이 채움 → 사면은 그 경계에서 seam 만큼만 겹치고 개방
        for tag, y0, y1 in (("N", -ms["y_edge"], co["y0"] + seam),
                            ("P", co["y1"] - seam, ms["y_edge"])):
            sc.build_slope(stage, f"{ROOT}/Masonry_{tag}", 0.0, 0.0, run,
                           drop, y0, y1, ms["thick"], M["rock"],
                           collider=True)
        # [A-07-4] 마당 어깨 축대 난간석 — 계단 회랑(y±1.6)만 열고 나머지 어깨를
        #   h0.9 로 막아 사면(24°) 우회 하강을 차단한다. 계단·사면 트랜스폼 불변.
        ew = PARAMS["edge_wall"]
        wl = PARAMS["wall"]
        cxw = (ew["x0"] + ew["x1"]) / 2.0
        lenx = ew["x1"] - ew["x0"]
        for tag, y0, y1 in (("N", -ms["y_edge"], co["y0"]),
                            ("P", co["y1"], ms["y_edge"])):
            cyw = (y0 + y1) / 2.0
            leny = y1 - y0
            sc.add_box(stage, f"{ROOT}/EdgeWall_{tag}",
                       (cxw, cyw, ew["h"] / 2.0), (lenx, leny, ew["h"]),
                       M["rock"], collider=True)
            sc.add_box(stage, f"{ROOT}/EdgeWallCap_{tag}",
                       (cxw, cyw, ew["h"] + ew["cap_h"] / 2.0),
                       (lenx + 2 * ew["cap_over"], leny, ew["cap_h"]),
                       M["stone_cap"], collider=True)

    def build_horizon(M, run, z_bot):
        """지평 폐쇄 : 뒤 숲 라인(생울타리+나무) + 앞 능선 실루엣 rock 박스."""
        bh = PARAMS["back_hedge"]
        for i, h in enumerate(PARAMS["back_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/BackHedge_{i}",
                           bh["cx"] - bh["sx"] / 2.0,
                           h["cy"] - bh["length"] / 2.0,
                           bh["cx"] + bh["sx"] / 2.0,
                           h["cy"] + bh["length"] / 2.0,
                           bh["h"], base_z=0.0)
        for i, t in enumerate(PARAMS["back_trees"]):
            sc.build_tree(stage, f"{ROOT}/BackTree_{i}", t["cx"], t["cy"],
                          0.0, M["wood"], M["canopy_a"], M["canopy_b"])
        # 앞 능선 : 진입로 너머 rock 박스 3단 (근/중/원경 = 3단 깊이감)
        for i, r in enumerate(PARAMS["ridge"]):
            cxr = run + r["cx"]
            sc.add_box(stage, f"{ROOT}/Ridge_{i}",
                       (cxr, 0.0, z_bot + r["z_off"] + r["h"] / 2.0),
                       (r["t"], r["sy"], r["h"]), M[f"ridge_{r['tone']}"],
                       collider=True)
        # 근경 능선 상면 수목 — 판때기 실루엣에 굴곡 부여 [B-07-1]
        rz = z_bot + PARAMS["ridge"][0]["h"]
        for i, t in enumerate(PARAMS["ridge_trees"]):
            sc.build_tree(stage, f"{ROOT}/RidgeTree_{i}", run + t["cx"],
                          t["cy"], rz, M["wood"], M["canopy_a"], M["canopy_b"])

    def build_dressing(M, run, z_bot):
        """노송 6(하부 5 = 눈높이 아래 수관 앵커 + 마당 1) + 사원 건축 요소.
        [감사 v4 D-07] '산사 경내' 판독 부여 — 위험 기하(석단·석축) 불변."""
        for i, p in enumerate(PARAMS["pines"]):
            if p["where"] == "approach":
                gx = run + p["cx"]
                gz = z_bot
            else:
                gx = p["cx"]
                gz = 0.0
            sc.build_tree(stage, f"{ROOT}/Pine_{i}", gx, p["cy"], gz,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        # (1) 일주문(산문) — 계단 상단이 "문을 지나 내려가는 곳"이 된다
        g = PARAMS["gate"]
        sc.build_canopy(stage, f"{ROOT}/Gate", g["x0"], g["x1"], g["y0"],
                        g["y1"], g["z_roof"], g["post_r"], M["roof"],
                        M["wood"], roof_t=g["roof_t"])
        # (2) 법당 1동(몸체 + 오버행 지붕) — 마당이 '경내'가 된다
        hl = PARAMS["hall"]
        sc.add_box(stage, f"{ROOT}/Hall/Body",
                   (hl["cx"], hl["cy"], hl["h"] / 2.0),
                   (hl["sx"], hl["sy"], hl["h"]), M["rock"], collider=True)
        rf = hl["roof"]
        sc.build_canopy(stage, f"{ROOT}/Hall/Roof", rf["x0"], rf["x1"],
                        rf["y0"], rf["y1"], rf["z_roof"], rf["post_r"],
                        M["roof"], M["wood"], roof_t=rf["roof_t"])
        # (3) 석등 2
        ln = PARAMS["lantern"]
        for i, p in enumerate(PARAMS["lanterns"]):
            sc.add_cylinder(stage, f"{ROOT}/Lantern_{i}/Base",
                            (p["cx"], p["cy"], ln["base_h"] / 2.0),
                            ln["base_r"], ln["base_h"], M["stone_cap"])
            sc.add_box(stage, f"{ROOT}/Lantern_{i}/Body",
                       (p["cx"], p["cy"], ln["base_h"] + ln["body"] / 2.0),
                       (ln["body"], ln["body"], ln["body"]), M["stone_cap"])
            sc.add_box(stage, f"{ROOT}/Lantern_{i}/Cap",
                       (p["cx"], p["cy"],
                        ln["base_h"] + ln["body"] + ln["cap_h"] / 2.0),
                       (ln["cap_w"], ln["cap_w"], ln["cap_h"]), M["stone_cap"])
        # (4) 당간지주 2 (계단 상단 양측 석주)
        fp = PARAMS["flagpole"]
        for i, p in enumerate(PARAMS["flagpoles"]):
            sc.add_box(stage, f"{ROOT}/Flagpole_{i}",
                       (p["cx"], p["cy"], fp["h"] / 2.0),
                       (fp["t"], fp["t"], fp["h"]), M["stone_cap"],
                       collider=True)

    def build_cues(M, run, z_bot):
        st = PARAMS["stairs"]
        if cfg["cue_railing"]:
            # 무난간 유형 — True면 우측 y=+1.7 파이프 레일 1선(균일 근사)
            def ground_fn(x):
                t = max(0.0, min(x / run, 1.0)) if run > 1e-9 else 0.0
                return -(-z_bot) * t           # 0 → z_bot 선형 근사
            sc.build_railing_line(stage, f"{ROOT}/Rail", st["y1"] + 0.1, 0.0,
                                  0.0, run, -z_bot, ground_fn, M["rail"],
                                  rail_h=0.9)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 : 계단·석축·진입로를 z=0 평지로 통일."""
        ap = PARAMS["approach"]
        x0, x1 = PARAMS["backfield"]["x0"], ap["x1"]
        cy = PARAMS["courtyard"]
        sc.add_box(stage, f"{ROOT}/FlatFill",
                   ((x0 + x1) / 2.0, 0.0, -0.25),
                   (x1 - x0, cy["y1"] - cy["y0"], 0.5), M["gravel"],
                   collider=True)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    if cfg["hazard_stairs"]:
        run, z_bot = build_stairs(M)
        build_courtyard(M)
        build_approach(M, run, z_bot)
        build_masonry(M, run, z_bot)
        build_cues(M, run, z_bot)
    else:
        run, z_bot = PARAMS["stairs"]["nsteps"] * PARAMS["stairs"]["tread_mu"], \
            -PARAMS["stairs"]["nsteps"] * PARAMS["stairs"]["riser_mu"]
        build_flat_fill(M)
    build_horizon(M, run, z_bot)
    if cfg["cue_scene_dressing"] and cfg["hazard_stairs"]:
        build_dressing(M, run, z_bot)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── 스모크(조립만) 조기 종료 ──
    if smoke:
        print("[SMOKE] 부팅+조립+조명 완료 — 렌더 없이 조기 종료")
        simulation_app.close()
        return

    # ── 카메라 + 렌더 모드 ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views(run, z_bot)
    _v0 = views["temple_walk"]
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

    # ── GUI 룩 체크 ──
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene07_{ts}.png")
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
