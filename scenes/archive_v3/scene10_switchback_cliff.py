# -*- coding: utf-8 -*-
"""
scene10_switchback_cliff.py — NegObs 인공씬 10호: 산릉 갈지자 (Isaac Sim 4.5)

사양서 : Docs/briefs/multi_scene_brief_v3.md §A(회귀 체크리스트)·§D(scene10)·§B(빌더)
공통 라이브러리 : scene_common.py / 골격 관례 : scene03_riverbank.py

유형 (T13 갈지자): **방향 반전 + 투과 디딤판 아래 계곡**.
  45° 암반 사면(rock_face 계단식 적층) 위에 철제 개방라이저 플라이트 6개가
  참마다 180° 반전(갈지자)하며 하강. 라이저가 없어 디딤판 사이로 아래 계곡이
  투시된다. 낙차 증거는 **반전하는 플라이트 실루엣 + 투과 디딤판 너머 계곡 +
  원경 능선**. 파이프 난간 양측(산악 안전시설, cue_railing 기본 True).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene10_switchback_cliff.py

자동 캡처 : NEGOBS_CAPTURE=1 python scene10_switchback_cliff.py
조립 스모크: NEGOBS_SMOKE=1 python scene10_switchback_cliff.py

좌표계: Z-up, m. 플라이트는 로컬 +X 하강(관례). 짝수 플라이트는 rot_group 0°,
        홀수는 rot_group 180°(피벗=플라이트 상단) → 월드에서 방향 반전.

────────────────────────────────────────────────────────────────────────────
기하 핵심 (감독 보충 + 감사 v4 반영):
  · 철제 플라이트 6개×8단(open_riser, 폭 0.8, riser 0.16, tread 0.28,
    metal_rust). 플라이트 k = rot_group(180°*(k%2)) 안에 배치, 참(1.2×2.45)
    연결. 총 낙차 6×8×0.16 = 7.68 + 착지 계단 0.92 → 계곡 바닥 −8.6.
  · **갈지자 Y 오프셋**(감사 v4): 짝수 대역 y[−1.0,−0.2] / 홀수 y[+0.2,+1.0].
    두 방향이 나란히 놓이고 참은 반전 지점의 돌출 플랫폼 — 실제 switchback.
  · 진입: 벤치 암반(트레일 z=0) → 진입 데크(x −1.2..0) → 1단(−0.16).
  · 파이프 난간 양측 : build_railing_line 은 +X 하강 전용이므로 각 플라이트
    rot_group **내부**에서 호출(그룹이 방향 반전 처리).
  · 암반 사면 : rock_face 5단 적층(각 6×20×3, 뒤로 3 물러나며 3 상승 = 45°).
  · 배경 : 하부 계곡 바닥(어두운 숲 톤 + 나무 3) + 원경 능선 rock 박스.
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
# [A] SCENE_CONFIG — 표준 7키. 산악 안전 파이프 난간(cue_railing 기본 True).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 플라이트를 z=0 평판 데크로(낙차 제거)
    "cue_railing":        True,    # **양측 파이프 난간**(산악 안전) 기본 True
    "cue_tactile":        False,   # 미사용(코드 경로만)
    "cue_material_break": True,    # 철제 플라이트 vs 암반 재질 대비(상시 상이)
    "cue_sign":           False,   # [선택] 미구현 — 키만 예약
    "cue_scene_dressing": True,    # 계곡 나무 3
    "cue_nosing":         False,   # 미사용(코드 경로만)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # [감사 v4 A-10-2·3·5] y_off 신설 — 갈지자 두 플라이트를 **폭만큼 옆으로**
    #   나란히 놓는다(실제 switchback). 기존엔 두 플라이트가 y 오프셋 없이 동일
    #   대역(y±0.4)에 공선 배치돼 ①상단 4단이 직전 참 밑에 매몰(헤드룸 0.08 m)
    #   ②상·하 플라이트 헤드룸 0.80 m ③난간 상호 관통 이 동시에 발생했다.
    #   짝수(=+X 하강) 대역 y ∈ [−1.0, −0.2] / 홀수(rot180) 대역 y ∈ [+0.2, +1.0].
    #   → 두 대역은 겹치지 않으므로 x 겹침이 있어도 간섭 0, 상하 플라이트 간
    #     연직 여유 = 2×1.28 − 0.29(스트링거+디딤판) = 2.27 m.
    flights=dict(n=6, steps=8, riser=0.16, tread=0.28, half_w=0.4, y_off=0.6,
                 tread_t=0.04, gap=0.02, z_top=0.0),
    # 참 : x 1.2 × y −1.1..1.35 (두 대역을 모두 덮고 +Y 끝은 배킹 벽에 0.05 물림)
    landing=dict(size=1.2, thick=0.08, y0=-1.1, y1=1.35),
    # [A-10-1] 최상단 진입 데크 + 등산로 벤치(암반 노두) — 첫 단 앞에 발 디딜
    #   곳이 전혀 없어(벽 모서리에 매달린 사다리) 진입 자체가 불가했다.
    deck=dict(x0=-1.2, x1=0.0, thick=0.15),
    bench_rock=dict(x0=-18.0, x1=-1.2, y0=-1.8, y1=26.0, z0=0.0, z1=-9.0),
    # [A-10-4] 최하단 착지 계단 — 마지막 참(z −7.68)과 계곡 바닥(−8.6) 사이
    #   0.92 m 낙차(마지막 한 단 부재)를 6단(riser 0.15333)으로 잇는다.
    toe=dict(steps=6, tread=0.28),
    # 암반 사면 5단(rock_face) — 각 6(x)×20(y)×3(z), 뒤로 3 물러나며 3 상승.
    # 감독 r3 — cy 3.0→13.0: sy=20 이라 cy3 이면 y[-7,13] 로 플라이트(y±0.4)를
    # 덮어 카메라가 암반 내부에 들어감. cy13(y[3,23])으로 물려 −Y 개방측을
    # 완전히 비움 → 계단은 배킹 벽(+Y) 앞의 독립 구조(브래킷 고정 인상).
    #   [B-10-1] cy 13.0 → 15.0 (tier y0 = 5.0): 그리드 뷰(eye (−d,0,h), hFOV 60°)
    #     좌측 42%를 무늬 없는 암갈색 벽이 막던 문제. d=5 에서 tier 원단 모서리
    #     (x=1, y=5)의 축 이탈각 = atan(5/6) = 39.8° > 30°(반화각) → 프레임 밖.
    #     d=10 에서는 24.4° 로 좌측에만 걸려 '측면 절벽'으로 읽힌다.
    #     z0 2.0 → 1.5 로 tier_0 하면을 벤치 암반 상면(z=0)에 접지(부유 제거).
    #   [B-10-5] jitter — 정형 적층의 '회벽' 인상 완화(단별 x/z 요동)
    rock_tiers=dict(n=6, sx=6.0, sy=20.0, sz=3.0, x0=-2.0, z0=1.5,
                    recede=3.0, rise=3.0, cy=15.0,
                    jx=(0.0, -0.5, 0.4, -0.3, 0.6, -0.2),
                    jz=(0.0, 0.3, -0.4, 0.2, -0.3, 0.4)),
    # 암반 배킹 벽(+Y) — 플라이트가 벽에 붙게(부유 방지), 개방측 −Y 유지.
    #   [A-10-6] y0 0.4 → 1.3: 참(y≤1.35)과 0.05 만 물리게(기존 0.2 관통).
    #   y1 6.0 → 26.0: tier_0(y 5..25) 하부 지지(부유 방지).
    backing=dict(x0=-1.2, x1=3.6, y0=1.3, y1=26.0, z0=2.0, z1=-8.5),
    # 배킹 벽 앞면 돌출 암괴 4 — 매끈한 회벽 인상 제거 [B-10-5]
    boulders=[dict(cx=0.2, cy=1.1, cz=0.9, sx=1.2, sy=1.0, sz=2.0, rz=12.0),
              dict(cx=2.6, cy=1.15, cz=-0.4, sx=1.0, sy=0.9, sz=1.6, rz=-20.0),
              dict(cx=1.2, cy=1.2, cz=-3.2, sx=1.4, sy=1.0, sz=2.2, rz=8.0),
              dict(cx=3.0, cy=1.1, cz=-6.0, sx=1.1, sy=0.9, sz=1.8, rz=-14.0)],
    # 하부 계곡 바닥 — [B-10-2] 단색 무텍스처 판 → rock_face 텍스처 + 어두운 틴트.
    #   원경 능선까지 받도록 범위 확대(부유 방지).
    valley=dict(x0=-60.0, x1=90.0, y0=-95.0, y1=2.0, z_top=-8.6, thick=2.0),
    # 계곡 하천대 (폭 4) — "계곡" 확정
    stream=dict(x0=-45.0, x1=70.0, cy=-27.0, w=4.0, z=-8.55),
    # 원경 능선 : [B-10-4] 근접 판때기(cx18/6) → 중경·원경 3매로 재배치.
    #   기존 ridge[0]는 카메라에서 19 m 앞 h10 판이라 화면 우측 절반을 채웠다.
    ridge=[dict(cx=34.0, cy=-16.0, sx=10.0, sy=80.0, h=14.0, z0=-8.6,
                tone="mid"),
           dict(cx=62.0, cy=-12.0, sx=12.0, sy=120.0, h=26.0, z0=-8.6,
                tone="far"),
           dict(cx=0.0, cy=-44.0, sx=130.0, sy=10.0, h=16.0, z0=-8.6,
                tone="mid"),
           dict(cx=4.0, cy=-70.0, sx=170.0, sy=12.0, h=30.0, z0=-8.6,
                tone="far")],
    # 계곡 수목 12 + 관목 덩어리 8 (인스턴스 ~20, 스캐터 아님) [D-10-1]
    trees=[dict(cx=-6.0, cy=-6.0), dict(cx=8.0, cy=-10.0),
           dict(cx=-12.0, cy=-14.0), dict(cx=3.5, cy=-4.5),
           dict(cx=-19.0, cy=-8.0), dict(cx=14.0, cy=-16.0),
           dict(cx=-3.0, cy=-21.0), dict(cx=21.0, cy=-7.0),
           dict(cx=-25.0, cy=-19.0), dict(cx=9.0, cy=-31.0),
           dict(cx=-14.0, cy=-35.0), dict(cx=26.0, cy=-24.0)],
    shrubs=[dict(cx=-9.0, cy=-3.0, sx=1.5, sy=3.0, h=1.4),
            dict(cx=5.0, cy=-13.0, sx=3.0, sy=1.5, h=1.0),
            dict(cx=-17.0, cy=-25.0, sx=2.4, sy=2.0, h=1.8),
            dict(cx=17.0, cy=-4.0, sx=1.6, sy=2.8, h=1.2),
            dict(cx=-2.0, cy=-12.0, sx=2.8, sy=1.6, h=2.2),
            dict(cx=12.0, cy=-22.0, sx=2.0, sy=2.4, h=1.6),
            dict(cx=-22.0, cy=-11.0, sx=2.2, sy=1.8, h=1.3),
            dict(cx=30.0, cy=-15.0, sx=2.6, sy=2.2, h=2.0)],
    # 등산로 표식 1조 + 케른(돌무지) 2 [D-10-3·4]
    trailsign=dict(cx=-2.2, cy=-1.3, r=0.06, h=1.7,
                   plate=(0.5, 0.05, 0.16)),
    cairns=[dict(cx=-2.6, cy=-1.0, gz=0.0), dict(cx=2.6, cy=-1.35, gz=-8.6)],

    material=dict(
        # [B-10-5] rock_face 2.0 → 6.0 (6×20 m 박스에 2 m 타일은 너무 잘아
        #   요철감이 사라져 '베이지 스투코 외벽'으로 읽혔다)
        scale=dict(rock_face=6.0, metal_rust=1.0, valley_rock=8.0),
        # [B-10-3] 0.62/metallic 0.85 = 광택 스테인리스(실내 인테리어 파이프)
        #   → 아연도금·도장 산악 안전시설 톤
        rail_color=(0.20, 0.18, 0.16), rail_metallic=0.25, rail_rough=0.75,
        valley_tint=(0.35, 0.32, 0.28),        # 계곡 바닥 rock_face 틴트
        water_color=(0.05, 0.09, 0.10), water_rough=0.16,
        # [B-10-4] 능선 2단 톤 — 중경 숲 / 원경 대기(암색 규칙 0.02~0.06)
        ridge_mid=(0.042, 0.048, 0.040),
        ridge_far=(0.052, 0.056, 0.062),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
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
    # 감독 r3 — 플라이트 개방측(−Y)을 정면광으로 채우려면 태양이 −Y쪽. 월드
    # 태양 az≈33.5+offset → offset 240(az≈273.5≈−Y 방위)로 디딤판·난간·반전
    # 실루엣이 살게. (r2 의 30(az63.5)은 암반 뒤에서 와 계단이 암부였음.)
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene10")

ASSET_ROLES = ["rock_face", "metal_rust", "hdri", "mdl"]


# ===========================================================================
# 플라이트 배치 사전계산 — (k, x_top, z_top, rot, even, landing) 리스트
# ===========================================================================
def compute_flights():
    fl = PARAMS["flights"]
    run = fl["steps"] * fl["tread"]            # 2.24
    fdrop = fl["steps"] * fl["riser"]          # 1.28
    land = PARAMS["landing"]["size"]           # 1.2
    seq = []
    x_top = 0.0
    z_top = fl["z_top"]
    for k in range(fl["n"]):
        even = (k % 2 == 0)
        rot = 180.0 * (k % 2)
        z_bot = z_top - fdrop
        if even:                               # 월드 +X 하강
            x_bot = x_top + run
            lx0, lx1 = x_bot, x_bot + land     # 참은 진행 방향 앞쪽으로 돌출
        else:                                  # 월드 −X 하강(rot 180)
            x_bot = x_top - run
            lx0, lx1 = x_bot - land, x_bot
        seq.append(dict(k=k, x_top=x_top, z_top=z_top, rot=rot, even=even,
                        lx0=lx0, lx1=lx1, z_bot=z_bot))
        # [감사 v4 A-10-2] 다음 플라이트 상단 = **참의 먼 쪽 모서리가 아니라
        #   플라이트 하단(x_bot) 그 자리**. 기존처럼 참 끝(lx1/lx0)을 다음 상단으로
        #   잡으면 반전한 플라이트가 자기 참 바로 밑을 되돌아 지나 상단 4단이
        #   참 슬래브 아래 매몰됐다(헤드룸 0.08/0.24/0.40/0.56 m).
        #   이제 참(1.2 m)은 반전 지점의 돌출 플랫폼이고, 다음 플라이트는 그
        #   참의 안쪽 모서리에서 반대 방향(y 반대 대역)으로 내려간다.
        x_top = x_bot
        z_top = z_bot
    return seq, run, fdrop


# ===========================================================================
# [D] 카메라 프리셋
# ===========================================================================
def land_center(f):
    """플라이트 f 의 하단 참 중심 (x, y=0, z)."""
    return ((f["lx0"] + f["lx1"]) / 2.0, 0.0, f["z_bot"])


def flight_ends(f, run):
    """플라이트 f 의 월드 시작/끝 좌표. 짝수는 +X, 홀수(rot180)는 −X 하강."""
    start = (f["x_top"], 0.0, f["z_top"])
    if f["even"]:
        end = (f["x_top"] + run, 0.0, f["z_bot"])
    else:                                       # rot180 about (x_top,0)
        end = (f["x_top"] - run, 0.0, f["z_bot"])
    return start, end


def build_views(seq, z_bot_total, run):
    # grid_views 축(y=0, +X)은 플라이트 폭 중심(y±0.4)과 정합. 암반은 전부 +Y
    # (backing y≥0.4, tier cy=13→y≥3) → −Y 개방측·y=0 축은 암반 비관통.
    views = sc.grid_views(0.0)
    # switchback_down: 감독 r3 — 최상단 플라이트 시작 좌표 +(진행 반대방향 1.5, h1.6),
    #   tgt=3번째 참. 전부 seq 좌표에서 프로그램 산출(하드코딩 금지).
    #   (밴드 예외: 갈지자 전체 부감 establishing shot.)
    s0, _ = flight_ends(seq[0], run)            # 최상단 시작 (0,0,0)
    views["switchback_down"] = dict(
        eye=[s0[0] - 1.5, 0.0, s0[2] + 1.6],    # 진행(+X) 반대방향 1.5, h1.6
        tgt=list(land_center(seq[2])))          # 3번째 참
    # reversal: 감독 r3 — 참1 좌표에서 −Y 2.5m·h1.2, tgt=참1. 참1 위 플라이트0(+X)와
    #   아래 플라이트1(−X 반전)이 한 프레임에.
    l1 = land_center(seq[0])
    views["reversal"] = dict(eye=[l1[0], l1[1] - 2.5, l1[2] + 1.2],
                             tgt=list(l1))
    # through_treads: 낮은 시점(−Y 개방측)에서 투과 디딤판 너머 계곡 투시
    views["through_treads"] = dict(eye=[2.6, -2.2, -1.0],
                                   tgt=[1.4, 0.2, -6.5])
    # valley_below: 감독 r3 — 최하단 착지 좌표 −Y 4m·h1.0, tgt=위쪽 플라이트3 시작.
    lb = land_center(seq[-1])
    s3, _ = flight_ends(seq[3], run)
    views["valley_below"] = dict(eye=[lb[0], lb[1] - 4.0, lb[2] + 1.0],
                                 tgt=list(s3))
    return views


# ===========================================================================
# [E] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. switchback_down — 참마다 180° 방향 반전이 낙차 증거로 읽히나
 2. through_treads  — 라이저 부재로 디딤판 사이 계곡이 투시되나
 3. reversal        — 6 플라이트 반전 실루엣이 명확한가
 4. valley_below    — 하부 계곡 바닥(어두운 숲 톤)이 낙차 앵커인가
 5. 지평 폐쇄        — 중경/원경 능선 2층 + 계곡 숲이 허공을 막는가
 6. cue_railing OFF/ON — 위험 기하(플라이트·참) 트랜스폼 동일한가
 7. 진입/착지       — 트레일→데크→1단, 마지막 참→착지 계단→계곡 바닥
 8. h0.9_d5        — 좌측이 암반 벽으로 막히지 않는가 (tier cy 15)
 9. 맥락            — 등산로 표식·케른·숲·하천이 '산악 등산로'로 읽히나"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene10")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene10"

    seq, run, fdrop = compute_flights()
    z_bot_total = seq[-1]["z_bot"]             # -7.68

    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        M = {}
        M["rock"] = tex("rock_face", "/World/Looks/RockFace", sca["rock_face"])
        M["metal"] = tex("metal_rust", "/World/Looks/Metal", sca["metal_rust"])
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        # [B-10-2] 계곡 바닥: 단색 상수 → rock_face 텍스처(scale 8) + 어두운 틴트
        M["valley"] = tex("rock_face", "/World/Looks/Valley",
                          sca["valley_rock"], tint=mp["valley_tint"])
        M["water"] = sc.make_pbr(stage, "/World/Looks/Water",
                                 diffuse_color=mp["water_color"],
                                 roughness_const=mp["water_rough"],
                                 metallic=0.0)
        for tone in ("mid", "far"):
            M[f"ridge_{tone}"] = sc.make_pbr(
                stage, f"/World/Looks/Ridge_{tone}",
                diffuse_color=mp[f"ridge_{tone}"], roughness_const=0.95,
                specular_level=0.0)
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        return M

    # -------------------------------------------------------------------
    def build_rock(M):
        """암반 사면 6단(rock_face, 단별 지터) + 배킹 벽(+Y) + 돌출 암괴 4
        + [A-10-1] 등산로 벤치 암반(트레일) — 최상단 진입 지면."""
        rt = PARAMS["rock_tiers"]
        for i in range(rt["n"]):
            cx = rt["x0"] - rt["recede"] * i + rt["jx"][i % len(rt["jx"])]
            cz = rt["z0"] + rt["rise"] * i + rt["jz"][i % len(rt["jz"])]
            sc.add_box(stage, f"{ROOT}/Tier_{i}", (cx, rt["cy"], cz),
                       (rt["sx"], rt["sy"], rt["sz"]), M["rock"],
                       collider=True)
        bk = PARAMS["backing"]
        sc.add_box(stage, f"{ROOT}/Backing",
                   ((bk["x0"] + bk["x1"]) / 2.0, (bk["y0"] + bk["y1"]) / 2.0,
                    (bk["z0"] + bk["z1"]) / 2.0),
                   (bk["x1"] - bk["x0"], bk["y1"] - bk["y0"],
                    bk["z0"] - bk["z1"]), M["rock"], collider=True)
        # 등산로 벤치 암반 — 트레일(z=0) + 그 아래 계곡 벽. 그리드 뷰 eye
        #   (−d, 0, h) 가 이 위에 선다(d=2/5/10 모두 x0..x1 안).
        br = PARAMS["bench_rock"]
        sc.add_box(stage, f"{ROOT}/BenchRock",
                   ((br["x0"] + br["x1"]) / 2.0, (br["y0"] + br["y1"]) / 2.0,
                    (br["z0"] + br["z1"]) / 2.0),
                   (br["x1"] - br["x0"], br["y1"] - br["y0"],
                    br["z0"] - br["z1"]), M["rock"], collider=True)
        # 배킹 벽 앞면 돌출 암괴 4 (rotz 로 무작위감)
        for i, b in enumerate(PARAMS["boulders"]):
            grp = sc.build_rot_group(stage, f"{ROOT}/BoulderGrp_{i}",
                                     (b["cx"], b["cy"]), b["rz"])
            sc.add_box(stage, f"{grp}/Rock", (b["cx"], b["cy"], b["cz"]),
                       (b["sx"], b["sy"], b["sz"]), M["rock"], collider=True)

    def build_flights(M):
        """철제 플라이트 6개 — rot_group(180°*(k%2)) 안에 open_riser + 양측 난간.
        참(x 1.2 × y 2.45 metal 판)은 월드 좌표로 플라이트 하단에 연결하며 짝·홀
        두 폭 대역을 모두 덮는다. + 최상단 진입 데크 + 최하단 착지 계단."""
        fl = PARAMS["flights"]
        hw = fl["half_w"]
        yo = fl["y_off"]
        ld = PARAMS["landing"]
        lcy = (ld["y0"] + ld["y1"]) / 2.0
        lsy = ld["y1"] - ld["y0"]

        def _rails(grp, tag_x0, z_top, gy0, gy1, rrun, rdrop, rsteps, rriser,
                   rtread):
            """플라이트 양측 파이프 난간 (rot_group 내부, +X 하강 규약)."""
            def ground_fn(x, _xt=tag_x0, _zt=z_top):
                if x <= _xt:
                    return _zt
                i = min(int((x - _xt) / rtread) + 1, rsteps)
                return _zt - i * rriser

            for tag, y in (("N", gy0), ("P", gy1)):
                sc.build_railing_line(
                    stage, f"{grp}/Rail_{tag}", y, tag_x0, tag_x0, rrun,
                    rdrop, ground_fn, M["rail"], rail_h=0.9,
                    post_r=0.025, spacing=1.0, rail_r=0.03)

        for f in seq:
            k = f["k"]
            grp = sc.build_rot_group(stage, f"{ROOT}/FlightGrp_{k}",
                                     (f["x_top"], 0.0), f["rot"])
            # 로컬 +X 하강 open_riser. 폭 대역은 −Y 로 y_off 만큼 치우쳐 있고,
            # rot180(홀수)이 그것을 +Y 대역으로 미러링한다 → 두 방향이 나란히.
            sc.build_open_riser_stairs(
                stage, f"{grp}/Flight", f["x_top"], -yo - hw, -yo + hw,
                fl["riser"], fl["tread"], fl["steps"], f["z_top"],
                M["metal"], M["metal"],
                tread_t=fl["tread_t"], gap=fl["gap"])
            if cfg["cue_railing"]:
                _rails(grp, f["x_top"], f["z_top"], -yo - hw, -yo + hw,
                       run, fdrop, fl["steps"], fl["riser"], fl["tread"])
            # 참(월드 좌표) — 플라이트 하단 상면 z_bot 에 정합. 두 대역을 모두 덮음.
            sc.add_box(stage, f"{ROOT}/Landing_{k}",
                       ((f["lx0"] + f["lx1"]) / 2.0, lcy,
                        f["z_bot"] - ld["thick"] / 2.0),
                       (f["lx1"] - f["lx0"], lsy, ld["thick"]),
                       M["metal"], collider=True)

        # [A-10-1] 최상단 진입 데크 — 벤치 암반(x≤−1.2)과 첫 단(x=0)을 잇는다
        dk = PARAMS["deck"]
        sc.add_box(stage, f"{ROOT}/EntryDeck",
                   ((dk["x0"] + dk["x1"]) / 2.0, lcy, -dk["thick"] / 2.0),
                   (dk["x1"] - dk["x0"], lsy, dk["thick"]), M["metal"],
                   collider=True)
        # [A-10-4] 최하단 착지 계단 — 마지막 참 → 계곡 바닥(정확히 z_top 착지)
        toe = PARAMS["toe"]
        last = seq[-1]
        vz = PARAMS["valley"]["z_top"]
        t_riser = (last["z_bot"] - vz) / toe["steps"]
        # n 이 짝수면 마지막 플라이트는 홀수(−X 하강)이므로 착지 계단은 +X 방향,
        # 참의 +X 끝(lx1 = x_bot)에서 시작한다. (현 설정 n=6)
        t_x0 = last["lx1"]
        sc.build_open_riser_stairs(
            stage, f"{ROOT}/ToeFlight", t_x0, -yo - hw, -yo + hw, t_riser,
            toe["tread"], toe["steps"], last["z_bot"], M["metal"], M["metal"],
            tread_t=fl["tread_t"], gap=fl["gap"])
        if cfg["cue_railing"]:
            _rails(f"{ROOT}/ToeFlight", t_x0, last["z_bot"], -yo - hw,
                   -yo + hw, toe["steps"] * toe["tread"],
                   toe["steps"] * t_riser, toe["steps"], t_riser, toe["tread"])
        print(f"[기하] 착지 계단 {toe['steps']}단 riser={t_riser:.4f} "
              f"x {t_x0:.2f}→{t_x0 + toe['steps'] * toe['tread']:.2f} "
              f"z {last['z_bot']:.2f}→{vz:.2f}")

    def build_background(M):
        """하부 계곡 바닥(암반 텍스처) + 하천대 + 원경 능선 3층 — 지평 폐쇄."""
        vl = PARAMS["valley"]
        sc.add_box(stage, f"{ROOT}/Valley",
                   ((vl["x0"] + vl["x1"]) / 2.0, (vl["y0"] + vl["y1"]) / 2.0,
                    vl["z_top"] - vl["thick"] / 2.0),
                   (vl["x1"] - vl["x0"], vl["y1"] - vl["y0"], vl["thick"]),
                   M["valley"], collider=True)
        stm = PARAMS["stream"]
        sc.build_water(stage, f"{ROOT}/Stream", stm["x0"],
                       stm["cy"] - stm["w"] / 2.0, stm["x1"],
                       stm["cy"] + stm["w"] / 2.0, stm["z"], mtl=M["water"])
        for i, r in enumerate(PARAMS["ridge"]):
            sc.add_box(stage, f"{ROOT}/Ridge_{i}",
                       (r["cx"], r["cy"], r["z0"] + r["h"] / 2.0),
                       (r["sx"], r["sy"], r["h"]), M[f"ridge_{r['tone']}"],
                       collider=True)

    def build_dressing(M):
        """[감사 v4 D-10] 계곡 수목 12 + 관목 8 + 등산로 표식 + 케른 2.
        "건물 외벽에 붙은 녹슨 비상계단" 오판독(scene11 과 중복)을
        "산악 등산로 / 계곡 잔도"로 되돌린다."""
        gz = PARAMS["valley"]["z_top"]
        for i, t in enumerate(PARAMS["trees"]):
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", t["cx"], t["cy"], gz,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        for i, s in enumerate(PARAMS["shrubs"]):
            sc.build_hedge(stage, f"{ROOT}/Shrub_{i}",
                           s["cx"] - s["sx"] / 2.0, s["cy"] - s["sy"] / 2.0,
                           s["cx"] + s["sx"] / 2.0, s["cy"] + s["sy"] / 2.0,
                           s["h"], base_z=gz, tint=(0.045, 0.062, 0.035))
        # 등산로 표식(기둥 + 방향판 2) — 진입 데크 옆
        ts = PARAMS["trailsign"]
        sc.add_cylinder(stage, f"{ROOT}/TrailSign/Post",
                        (ts["cx"], ts["cy"], ts["h"] / 2.0), ts["r"],
                        ts["h"], M["metal"])
        for k, dz in enumerate((0.0, -0.26)):
            sc.add_box(stage, f"{ROOT}/TrailSign/Plate_{k}",
                       (ts["cx"] + ts["plate"][0] / 2.0 * (1 if k == 0 else -1),
                        ts["cy"], ts["h"] - 0.15 + dz),
                       ts["plate"], M["metal"])
        # 케른(돌무지) 2 — 구 4~5개 적층
        for i, c in enumerate(PARAMS["cairns"]):
            zz = c["gz"]
            for j, rr in enumerate((0.18, 0.15, 0.12, 0.09)):
                sc.add_sphere(stage, f"{ROOT}/Cairn_{i}/S{j}",
                              (c["cx"] + 0.02 * j, c["cy"] - 0.02 * j,
                               zz + rr * 0.7), (rr, rr, rr * 0.7), M["rock"])
                zz += rr * 1.3

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 : 플라이트를 z=0 평판 데크로(낙차 제거)."""
        ld = PARAMS["landing"]
        dk = PARAMS["deck"]
        x0, x1 = dk["x0"], PARAMS["flights"]["steps"] * \
            PARAMS["flights"]["tread"] + PARAMS["landing"]["size"]
        sc.add_box(stage, f"{ROOT}/FlatDeck",
                   ((x0 + x1) / 2.0, (ld["y0"] + ld["y1"]) / 2.0, -0.04),
                   (x1 - x0, ld["y1"] - ld["y0"], 0.08), M["metal"],
                   collider=True)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_rock(M)
    if cfg["hazard_stairs"]:
        build_flights(M)
        print(f"[기하] 갈지자 {PARAMS['flights']['n']}플라이트×"
              f"{PARAMS['flights']['steps']}단 총낙차 {-z_bot_total:.3f} "
              f"z_bot={z_bot_total:.3f}")
    else:
        build_flat_fill(M)
    build_background(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke:
        print("[SMOKE] 부팅+조립+조명 완료 — 렌더 없이 조기 종료")
        # 플라이트 k별 시작·끝 (x,y,z)
        for f in seq:
            s, e = flight_ends(f, run)
            print(f"[SMOKE] flight{f['k']} rot={int(f['rot'])} "
                  f"start=({s[0]:.2f},{s[1]:.2f},{s[2]:.2f}) "
                  f"end=({e[0]:.2f},{e[1]:.2f},{e[2]:.2f})")
        # rock tier k bbox + 참/플라이트 y 대역(−1.1..1.35) 간섭 검사
        rt = PARAMS["rock_tiers"]
        fy = max(abs(PARAMS["landing"]["y0"]), abs(PARAMS["landing"]["y1"]))
        overlap = False
        for i in range(rt["n"]):
            cx = rt["x0"] - rt["recede"] * i + rt["jx"][i % len(rt["jx"])]
            cz = rt["z0"] + rt["rise"] * i + rt["jz"][i % len(rt["jz"])]
            ylo, yhi = rt["cy"] - rt["sy"] / 2.0, rt["cy"] + rt["sy"] / 2.0
            hit = ylo < fy and yhi > -fy          # y 대역이 플라이트 폭과 겹치나
            overlap = overlap or hit
            print(f"[SMOKE] tier{i} bbox x[{cx-rt['sx']/2:.1f},"
                  f"{cx+rt['sx']/2:.1f}] y[{ylo:.1f},{yhi:.1f}] "
                  f"z[{cz-rt['sz']/2:.1f},{cz+rt['sz']/2:.1f}] "
                  f"{'⚠y겹침' if hit else 'y-clear'}")
        print(f"[SMOKE] 플라이트↔암반 y-간섭 = {overlap} (False 여야 함)")
        for vn in ("switchback_down", "reversal", "valley_below",
                   "through_treads"):
            v = build_views(seq, z_bot_total, run)[vn]
            print(f"[SMOKE] cam {vn:<15} eye={['%.2f' % e for e in v['eye']]} "
                  f"tgt={['%.2f' % t for t in v['tgt']]}")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views(seq, z_bot_total, run)
    _v0 = views["switchback_down"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene10_{ts}.png")
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
