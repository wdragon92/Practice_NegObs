# -*- coding: utf-8 -*-
"""
scene06_spiral_towerstone.py — NegObs 인공씬 6호: T9 성탑/전망대 나선 석계단 하강
(Isaac Sim 4.5)

사양서 : Docs/multi_scene_brief_v3.md §D scene06_spiral_towerstone (유일 사양)
공통 라이브러리 : scene_common.py (§A) — boot·make_pbr·build_helix_steps·build_arc_steps·조명·캡처
모티프 참조 : scene05_amphitheater.py (main 골격·원형 개구 4박스 분할·cue 토글)

유형 정체성: 곡률 자기폐색 — 나선 2~3단 아래가 완전히 은폐된다.
  상단 화강암 광장의 원형 개구에서 지하(탑 지하실)로 하강하는 32단 나선(2회전,
  낙차 5.76m). 낮은 시점에서 개구 너머 나선이 통째로 사라지는 grazing 은닉이
  판정 포인트.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene06_spiral_towerstone.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene06_spiral_towerstone.py
      NEGOBS_CAPTURE_DIR / NEGOBS_CAPTURE_MODE(rt|pt|both) / NEGOBS_VIEWS

스모크 모드 (감독 런타임 검증):
    NEGOBS_SMOKE=1 python scene06_spiral_towerstone.py
      → 씬 조립+조명까지 마친 뒤 "SMOKE_OK prims=<count>" 출력하고 즉시 종료.

좌표계: Z-up, m, 진행축 +X. 탑 중심 (2.5, 0). 광장 상면 z=0. 개구 근연 x=0.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — scene05 동일 7키. hazard_stairs 만 위험 기하 토글(나선 개구
#     ↔ 광장 평지). 나머지 cue 는 기하 불변.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # 나선 개구 기하 (False → 개구 없는 화강암 평지)
    "cue_railing":        True,    # 개구 둘레 부분 호 난간(−X 관람측). scene05 선택 구현
    "cue_tactile":        False,   # True → −X 접근 경고 점자띠(선택 구현)
    "cue_material_break": True,    # 개구 둘레 다크 화강암 연석 링(재질 경계)
    "cue_nosing":         False,   # True → 나선 단코 논슬립 아크 밴드(선택 구현)
    "cue_sign":           False,   # [예약] 미구현 — config 키만
    "cue_scene_dressing": True,    # 화단·건물·잔디 대지 일괄
}


# ===========================================================================
# [B] PARAMS — 치수표 + 재질/조명/캡처. NEGOBS_PARAMS_OVERRIDE 로 머지 가능.
# ===========================================================================
PARAMS = dict(
    tower=dict(cx=2.5, cy=0.0),
    # 상부 광장 (화강암 plaza_light) — 원형 개구는 링+4박스로 분할(체크리스트 §3)
    plaza=dict(x0=-20.0, x1=20.0, y0=-16.0, y1=16.0, z_top=0.0, thick=0.5),
    # 광장 링 슬래브: 개구 원(r_in 2.5)의 매끈한 원형 가장자리 + 코너 무공극
    #   top_z=-0.002 : 프레임 4박스(z=0)와 동일평면 Z파이팅 회피용 2mm 오프셋
    ring=dict(r_in=2.5, r_out=6.0, seg=48, top_z=-0.002, base_z=-0.5),
    # 나선 계단: build_helix_steps(z0=0, 32단, riser 0.18, step 22.5° → 2회전, 낙차 5.76)
    #   [감사 v4 A-06-2] a0 0.0 → 168.75: 0단(방위 168.75~191.25, 상면 −0.18)이
    #   −X 정면에 오도록 나선 전체를 축 회전. 출입 슬릿(170.5~189.5)이 "그 방위의
    #   최상단 단" 바로 위에 정렬되어 허공 슬릿(1.08/2.88 m 추락)이 소멸한다.
    #   단수·riser·반경·회전수 등 위험 기하 치수는 불변(축 회전만).
    spiral=dict(r_in=0.5, r_out=2.2, a0=168.75, step_deg=22.5, n=32,
                riser=0.18, z0=0.0, base_drop=0.5),
    # 탑 외벽 원통 셸 — [감사 v4 A-06-2] 3구간 슬릿 구조를 재편
    #   drum  : 지하 구간(base_z..drum_top) **360° 연속** — 지하 슬릿을 없애
    #           샤프트를 밀폐(광장 하부 공동 노출·허공 개구 동시 해소)
    #   walls : 지상 파라펫(drum_top..top_z) 3구간 → 사이 개구 3
    #           = 문 1(170.5~189.5, 계단 0단 위) + 창 2(115~125 / 235~245)
    #   sills : 창 2개의 하부를 sill_top 까지 막아 **통행 불가**(문만 출입)
    #   drum_top −0.012 : 링 상면(−0.002)과 **동일 평면 회피**(r 2.5..2.7 에서
    #     드럼과 링이 겹치므로 coplanar 면이면 Z파이팅). 1 cm 차는 판정 임계
    #     (0.2)의 1/20 이고 문 통행선은 랜딩(−0.002)이 덮으므로 보행 무영향.
    shell=dict(r_in=2.4, r_out=2.7, top_z=1.2, base_z=-6.0, deg_per_seg=5.0,
               drum_top=-0.012, sill_top=0.55,
               walls=[(125.0, 170.5), (189.5, 235.0), (245.0, 475.0)],
               sills=[(115.0, 125.0), (235.0, 245.0)],
               door=(170.5, 189.5)),
    # [감사 v4 A-06-1] 나선 상단 랜딩 — 광장 링 내경(2.5)/드럼 내경(2.4)과 첫
    #   디딤단 외경(2.2) 사이 환형 공극(0.30 m × 깊이 5.6)을 문 방위에서 메운다.
    #   상면 −0.002(링·드럼과 동일 평면) → 광장에서 0.178 m 만 내려서면 0단.
    #   문 밖(파라펫 뒤) 나머지 방위의 0.2 m 슬롯은 발광 스트립 코브라 접근 불가.
    #   r_out 2.52 : 링 내경(2.5)까지 덮어 문 통행선 전체를 −0.002 평면으로 통일.
    landing=dict(r_in=2.2, r_out=2.52, a0=168.75, a1=191.25, seg=6,
                 top_z=-0.002, base_z=-0.5),
    # 중심 석주 Cylinder r0.5 (z −6..1.2)
    column=dict(r=0.5, z_bot=-6.0, z_top=1.2),
    # 나선 하부 랜딩 + 어두운 지하실 바닥 — 샤프트 풋프린트(r≤2.4=셸 내경)로 축소.
    #   상면 z=−5.80(마지막 단 −5.76 과 Z파이팅 회피, §8), 두께 0.2 [A-06①]
    basement=dict(r=2.40, top_z=-5.80, thick=0.2),
    # 샤프트 벽 발광 스트립 2개(z −2.0/−4.0) — 나선 내부·지하 가독용 [A-06①]
    #   r 2.28..2.38(나선 r_out2.2 와 셸 내경2.4 사이 간극), 높이 0.25 얇은 호형 박스
    #   [감사 v4 B-06-2] intensity 3000 → 350: 3000 은 opening_over 에서 순백
    #   클리핑(형광 리본)이었다. 드럼 밀폐로 지하 자연광 유입이 개구·문으로
    #   한정되므로 감사 권고(150~300)보다 약간 높은 350 을 임시값으로 둔다.
    strips=dict(r_in=2.28, r_out=2.38, zs=[-2.0, -4.0], h=0.25, seg=24,
                a0=0.0, a1=360.0, color=(1.0, 0.95, 0.85), intensity=350.0),
    # 개구 둘레 다크 화강암 연석 (cue_material_break) — 광장 위 +0.06 proud 링
    curb=dict(r_in=2.7, r_out=3.05, seg=48, top_z=0.06, base_z=-0.1),
    # 개구 둘레 부분 호 난간 (cue_railing) — 문(방위 180) 양옆 2호.
    #   [감사 v4 A-06-3] 기존 120~240 단일 호는 출입구 정면을 가로막았다.
    #   165~195 를 비워 문 접근 축을 열고, 양옆 난간이 그 축을 유도한다.
    railing=dict(r=3.2, arcs=[(75.0, 165.0), (195.0, 285.0)], nposts=7,
                 rail_h=0.95),

    # 부지 바깥 잔디 대지 (지평 폐쇄 §4) — 광장 사각 둘레 4박스
    ground=dict(gx0=-120.0, gx1=120.0, gy0=-120.0, gy1=120.0, top_z=-0.02),
    buildings=dict(
        # C: +X 지평선 차단. 파사드 −X(광장 향).
        C=dict(x0=44.0, x1=52.0, y0=-14.0, y1=16.0, h=16.0, floors=5,
               axis="x", facade_x=44.0, face_dir=-1.0),
        # W: −X 지평선 차단. 파사드 +X(광장 향).
        W=dict(x0=-52.0, x1=-44.0, y0=-16.0, y1=14.0, h=13.0, floors=4,
               axis="x", facade_x=-44.0, face_dir=1.0),
        # [감사 v4 D-06-8] N/S 추가 → 4면 지평 폐쇄(기존 2면은 좌우가 뚫려 있었다)
        N=dict(x0=-18.0, x1=18.0, y0=46.0, y1=54.0, h=12.0, floors=4,
               axis="y", facade_y=46.0, face_dir=-1.0),
        S=dict(x0=-18.0, x1=18.0, y0=-54.0, y1=-46.0, h=12.0, floors=4,
               axis="y", facade_y=-46.0, face_dir=1.0),
    ),

    # --- [감사 v4 D-06] 맥락 드레싱 (전부 cue_scene_dressing 소속) ---
    # 폐허 탑신 링 : "석탑 유적" 판독의 핵심 오브젝트. 위험 기하(셸 r2.4..2.7,
    #   난간 r3.2)보다 바깥(r 4.35..4.85)이라 간섭 없음. 높이가 들쭉날쭉한 4구간
    #   + 사이 결손부. −X(방위 140~215)는 통째로 비워 그리드 뷰 시선 회랑 확보.
    ruin=dict(r_in=4.35, r_out=4.85, base_z=-0.06, deg_per_seg=6.0,
              arcs=[(5.0, 75.0, 3.4), (85.0, 140.0, 2.4),
                    (215.0, 285.0, 4.2), (295.0, 355.0, 3.0)]),
    # 화단 6 (기존 2 + 4) — 40×32 광장의 백색 여백 분할
    #   (0, ±12.5): 경계 헤지(y 14.6..15.4)와 화단 연석(±1.75)이 겹치지 않게
    planters=[(-10.0, -10.0), (-12.0, 9.0), (11.0, -10.0), (13.0, 9.0),
              (0.0, -12.5), (0.0, 12.5)],
    # 유적 안내판 1조 (판 + 지주 2)
    sign=dict(cx=-4.2, cy=1.6, z=1.15, w=1.0, h=0.7, t=0.06, post_r=0.03,
              post_h=1.15, color=(0.05, 0.045, 0.04)),
    # 관람 벤치 4 (탑 조망)
    benches=[(-6.5, -4.5, 0.0), (-6.5, 4.5, 0.0),
             (10.5, -4.5, 180.0), (10.5, 4.5, 180.0)],
    # 볼라드 유도열 2줄 × 5 — 문(방위 180, −X) 접근 축 형성
    bollards=dict(ys=(-1.8, 1.8), xs=(-12.0, -10.5, -9.0, -7.5, -6.0)),
    # 경계 헤지 2 (광장/잔디 직선 컷 완화)
    hedges=[dict(y0=14.6, y1=15.4), dict(y0=-15.4, y1=-14.6)],
    hedge_x=dict(x0=-18.0, x1=18.0, h=1.0),
    # 자갈 apron 2 (백색 포장 면적 축소)
    aprons=[dict(x0=12.0, x1=20.0), dict(x0=-20.0, x1=-12.0)],
    apron=dict(y0=-16.0, y1=16.0, top_z=-0.01, thick=0.04),

    # --- 재질: texture_scale 용 물리 크기[m/타일] + 틴트/상수 ---
    material=dict(
        scale=dict(plaza_light=0.75, granite_dark=1.0, stone_worn=1.2,
                   brick_red=2.0, grass=4.0, gravel=0.6),
        stone_tint=(0.92, 0.90, 0.86),            # 마모석 약한 웜/탈색 틴트
        basement_color=(0.06, 0.06, 0.07),        # 어두운 지하실 바닥
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        # [감사 v4 B-06-3] 0.80/metallic 0.9 는 정오 직달에서 순백 클리핑(PVC
        #   파이프 인상) → 어두운 도장 금속으로. 규칙 범위(0.10~0.35) 준수.
        rail_color=(0.32, 0.31, 0.29), rail_metallic=0.4, rail_rough=0.5,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        parapet_color=(0.90, 0.90, 0.87), parapet_rough=0.6,
        nosing_color=(0.85, 0.72, 0.10), nosing_rough=0.7,
    ),

    # --- 조명: scene01 light dict + SUN_AZ_OFFSET=171.5 (표준) ---
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


# 파라미터 / 토글 환경변수 오버라이드 (scene01 패턴 — 기본 실행엔 영향 없음)
_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")
_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [C] 경로 — stone_worn 은 scene_common.TEX 미등록(디스크엔 존재) → 직접 경로
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene06")

_STONE_WORN = {k: os.path.join(sc.S1_DIR, f"stone_worn_{s}.jpg")
               for k, s in (("diff", "diff"), ("nor", "nor_dx"),
                            ("rough", "rough"))}


def _check_stone_worn():
    """stone_worn 은 TEX 레지스트리 미등록 → check_assets 로 못 잡으므로 수동 검사."""
    missing = [p for p in _STONE_WORN.values() if not os.path.isfile(p)]
    if missing:
        print("=" * 64)
        print("[에러] stone_worn 텍스처 누락 (assets/scene01/):")
        for p in missing:
            print(f"  - {p}")
        print("=" * 64)
        sys.exit(1)


def _add_emission(stage, mtl_path, color, intensity):
    """OmniPBR 발광 활성화 — make_pbr 로 만든 재질의 Shader 에 발광 입력 세팅.
    입력명은 OmniPBR.mdl 확인: enable_emission(bool)/emissive_color(color3f)/
    emissive_intensity(float, 기본 40). intensity 는 실내 가독 위해 수천 단위 —
    렌더가 어둡/밝으면 여기(strips.intensity)를 조정한다."""
    from pxr import UsdShade, Sdf, Gf
    sh = UsdShade.Shader.Get(stage, mtl_path + "/Shader")
    sh.CreateInput("enable_emission", Sdf.ValueTypeNames.Bool).Set(True)
    sh.CreateInput("emissive_color",
                   Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    sh.CreateInput("emissive_intensity",
                   Sdf.ValueTypeNames.Float).Set(float(intensity))


# ===========================================================================
# [D] 카메라 프리셋 — grid_views(gy=0) + 미장센 4컷
# ===========================================================================
def build_views():
    """h·d 그리드 9장 + 미장센 4컷. 개구 근연이 x=0 이므로 그리드 기준 유지.
    개구 위·나선 1/2회전 지점·슬릿 역광·지하 부감(브리프 §D 미장센 지시)."""
    v = sc.grid_views(0.0)
    out = {k: dict(eye=list(val["eye"]), tgt=list(val["tgt"]))
           for k, val in v.items()}
    # opening_over: 개구 연석 바로 위(h1.6)에서 개구 안 첫 3~4단이 보이게 −25° 내려봄.
    #   [미장센 예외] 카메라 밴드(h/pitch) 제약의 의도적 예외 — 개구 내부 노출 목적.
    out["opening_over"]   = dict(eye=[-0.3, 0.0, 1.6], tgt=[3.6, 0.0, -0.2])
    out["spiral_mid"]     = dict(eye=[1.2, 1.6, -1.0], tgt=[2.5, 0.0, -3.6])
    # slit_backlight: [감사 v4 B-06-1] 기존 eye(7.6,3.0,−1.4)는 광장 슬래브 밑
    #   공동(Plaza_E 아래)에 매몰돼 프레임 90%가 셸 외벽 암부였다. 게다가 지하
    #   슬릿 역광은 원래 성립하지 않는다(광장 하부는 암부 공동).
    #   → **샤프트 내부**에서 지상 출입 슬릿(방위 180, −X)을 역광으로 올려본다.
    #     eye = 12단(상면 −2.34) 워크라인 위 눈높이 1.5 → 방위 90°·r1.6·z −0.84.
    #     시선 최근접 반경 1.355 m > 석주 r0.5 (비관통), 경로상 모든 단 상면보다
    #     위(최소 여유 0.13 m)로 지나 문까지 무차폐. (좌표 산술 검증)
    out["slit_backlight"] = dict(eye=[2.50, 1.60, -0.84],
                                 tgt=[-0.05, 0.0, 0.55])
    # basement_up: 샤프트 바닥 중심(z=−5.5)에서 나선을 올려봄 [A-06②]
    out["basement_up"]    = dict(eye=[4.0, 0.0, -5.3], tgt=[2.0, 0.5, -0.5])  # 핫픽스: 석주 밖 워크라인
    return out


# ===========================================================================
# [E] 배너 + 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. opening_over    — 개구 위에서 나선 2~3단만 보이고 나머지 자기폐색되는가
 2. h0.3·d5~10      — 개구 너머 나선(낙차 5.76m)이 통째로 grazing 소실
 3. spiral_mid      — 나선 1/2회전 지점: 곡률 자기폐색 육안 확인
 4. slit_backlight  — 샤프트 내부에서 출입 슬릿 역광, 셸 원통성·석주 실루엣
 5. cue             — material_break 연석 링 / railing(문 양옆 2호)
 6. 진입 연속성      — 광장(z0) → 랜딩 → 0단(−0.18) 이 한 걸음인가
 7. 맥락            — 폐허 탑신·안내판·벤치·볼라드가 "유적 광장"으로 읽히나"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"

    # 에셋 검사 (누락 시 목록 출력 후 종료)
    sc.check_assets(
        ["plaza_light", "granite_dark", "grass", "brick_red", "gravel",
         "hdri", "mdl"],
        hdri=PARAMS["light"]["hdri"])
    _check_stone_worn()

    # ── 부팅 (SimulationApp 먼저, 그 뒤 pxr/omni) ──
    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene06")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    T = PARAMS["tower"]
    cx, cy = T["cx"], T["cy"]

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        scl = mp["scale"]
        M = {}
        M["plaza"] = sc.make_pbr(
            stage, "/World/Looks/Plaza", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"])
        M["granite"] = sc.make_pbr(
            stage, "/World/Looks/Granite", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"), sc.tex_path("granite_dark", "rough"),
            scl["granite_dark"])
        # 마모석(stone_worn) — TEX 미등록이므로 직접 경로로 make_pbr
        M["stone"] = sc.make_pbr(
            stage, "/World/Looks/StoneWorn", _STONE_WORN["diff"],
            _STONE_WORN["nor"], _STONE_WORN["rough"],
            scl["stone_worn"], tint=mp["stone_tint"])
        M["basement"] = sc.make_pbr(
            stage, "/World/Looks/Basement",
            diffuse_color=mp["basement_color"], roughness_const=0.9,
            metallic=0.0)
        # 발광 스트립 재질(OmniPBR emission) [A-06①]
        st = PARAMS["strips"]
        M["glow"] = sc.make_pbr(stage, "/World/Looks/Glow",
                                diffuse_color=st["color"],
                                roughness_const=0.6, metallic=0.0)
        _add_emission(stage, "/World/Looks/Glow", st["color"], st["intensity"])
        M["brick"] = sc.make_pbr(
            stage, "/World/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            scl["brick_red"])
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            scl["grass"], tint=mp["grass_tint"])
        # 자갈 apron (드레싱) — 백색 포장 여백 축소용
        M["gravel"] = sc.make_pbr(
            stage, "/World/Looks/Gravel", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            scl["gravel"])
        M["glass"] = sc.make_pbr(stage, "/World/Looks/Glass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
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
        M["parapet"] = sc.make_pbr(stage, "/World/Looks/Parapet",
                                   diffuse_color=mp["parapet_color"],
                                   roughness_const=mp["parapet_rough"])
        return M

    # -------------------------------------------------------------------
    # 상부 광장 — 원형 개구 정합. 링 슬래브 + 링 내접사각 밖 4박스 (scene05 기법).
    # -------------------------------------------------------------------
    def build_plaza(M, hazard):
        p = PARAMS["plaza"]
        top, th = p["z_top"], p["thick"]
        if not hazard:
            # 평지 대조군: 개구 없는 단일 슬래브
            sc.add_box(stage, "/World/Scene06/PlazaFlat",
                       ((p["x0"] + p["x1"]) / 2.0, (p["y0"] + p["y1"]) / 2.0,
                        top - th / 2.0),
                       (p["x1"] - p["x0"], p["y1"] - p["y0"], th),
                       M["plaza"], collider=True)
            return
        rg = PARAMS["ring"]
        # 링 슬래브(아크): 개구 원(r_in)의 매끈한 가장자리 담당
        sc.build_arc_steps(stage, "/World/Scene06/PlazaRing", cx, cy,
                           rg["r_in"], rg["r_out"], 0.0, 360.0, rg["seg"],
                           rg["top_z"], rg["base_z"], M["plaza"])
        # 링 outer 원에 **내접**하는 사각(반변=r_out/√2)을 비워 코너 무공극.
        half = rg["r_out"] / math.sqrt(2.0)
        sx0, sx1 = cx - half, cx + half
        sy0, sy1 = cy - half, cy + half
        ov = 0.05

        def slab(tag, x0, x1, y0, y1):
            sc.add_box(stage, f"/World/Scene06/Plaza_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, top - th / 2.0),
                       (x1 - x0, y1 - y0, th), M["plaza"], collider=True)
        slab("W", p["x0"], sx0, p["y0"], p["y1"])
        slab("E", sx1, p["x1"], p["y0"], p["y1"])
        slab("N", sx0 - ov, sx1 + ov, sy1, p["y1"])
        slab("S", sx0 - ov, sx1 + ov, p["y0"], sy0)

    # -------------------------------------------------------------------
    # 탑 — 나선 계단 + 원통 셸(슬릿 3) + 중심 석주 + 지하실 바닥
    # -------------------------------------------------------------------
    def build_tower(M):
        s = PARAMS["spiral"]
        sc.build_helix_steps(stage, "/World/Scene06/Spiral", cx, cy,
                             s["r_in"], s["r_out"], s["a0"], s["step_deg"],
                             s["n"], s["riser"], s["z0"], M["stone"],
                             base_drop=s["base_drop"])
        # 상단 랜딩 [A-06-1] — 문 방위의 환형 공극(r 2.2..2.42)을 광장 높이로 메움
        ld = PARAMS["landing"]
        sc.build_arc_steps(stage, "/World/Scene06/Landing", cx, cy,
                           ld["r_in"], ld["r_out"], ld["a0"], ld["a1"],
                           ld["seg"], ld["top_z"], ld["base_z"], M["stone"])
        # 원통 셸 [A-06-2] — 지하 드럼(360° 연속) + 지상 파라펫 3구간 + 창 sill 2
        sh = PARAMS["shell"]
        dps = float(sh["deg_per_seg"])

        def nseg(a0, a1):
            """호 길이에 비례한 세그 수 (chord 는 r_out 기준 ×1.03 — 공통 규약)."""
            return max(2, int(round(abs(a1 - a0) / dps)))

        sc.build_arc_steps(stage, "/World/Scene06/ShellDrum", cx, cy,
                           sh["r_in"], sh["r_out"], 0.0, 360.0,
                           nseg(0.0, 360.0), sh["drum_top"], sh["base_z"],
                           M["stone"])
        for wi, (a0, a1) in enumerate(sh["walls"]):
            sc.build_arc_steps(stage, f"/World/Scene06/Shell_{wi}", cx, cy,
                               sh["r_in"], sh["r_out"], a0, a1, nseg(a0, a1),
                               sh["top_z"], sh["drum_top"], M["stone"])
        for si, (a0, a1) in enumerate(sh["sills"]):
            sc.build_arc_steps(stage, f"/World/Scene06/Sill_{si}", cx, cy,
                               sh["r_in"], sh["r_out"], a0, a1, nseg(a0, a1),
                               sh["sill_top"], sh["drum_top"], M["stone"])
        # 중심 석주
        col = PARAMS["column"]
        sc.add_cylinder(stage, "/World/Scene06/Column",
                        (cx, cy, (col["z_top"] + col["z_bot"]) / 2.0),
                        col["r"], col["z_top"] - col["z_bot"], M["stone"],
                        collider=True)
        # 지하실 바닥 (어두운) — 나선 하부 랜딩 겸용. 샤프트 풋프린트(r≤2.4).
        bm = PARAMS["basement"]
        sc.add_cylinder(stage, "/World/Scene06/Basement",
                        (cx, cy, bm["top_z"] - bm["thick"] / 2.0),
                        bm["r"], bm["thick"], M["basement"], collider=True)
        # 샤프트 벽 발광 스트립 2개(z −2.0/−4.0) — 얇은 호형 박스 [A-06①]
        st = PARAMS["strips"]
        for zi, z in enumerate(st["zs"]):
            sc.build_arc_steps(stage, f"/World/Scene06/Strip_{zi}", cx, cy,
                               st["r_in"], st["r_out"], st["a0"], st["a1"],
                               st["seg"], z + st["h"] / 2.0, z - st["h"] / 2.0,
                               M["glow"], collider=False)

    # -------------------------------------------------------------------
    # 부지 바깥 잔디 대지 — 광장 사각 둘레 4박스(지평 폐쇄). 개구/광장은 위에서 덮음.
    # -------------------------------------------------------------------
    def build_ground(M):
        p = PARAMS["plaza"]
        g = PARAMS["ground"]
        top = g["top_z"]
        th = 1.0
        cz = top - th / 2.0
        ov = 0.05

        def slab(tag, x0, x1, y0, y1):
            sc.add_box(stage, f"/World/Scene06/Ground_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                       (x1 - x0, y1 - y0, th), M["grass"])
        slab("W", g["gx0"], p["x0"], g["gy0"], g["gy1"])
        slab("E", p["x1"], g["gx1"], g["gy0"], g["gy1"])
        slab("N", p["x0"] - ov, p["x1"] + ov, p["y1"], g["gy1"])
        slab("S", p["x0"] - ov, p["x1"] + ov, g["gy0"], p["y0"])

    # -------------------------------------------------------------------
    # 드레싱 — 화단 2 + 원경 건물 2 (지평 폐쇄)
    # -------------------------------------------------------------------
    def build_dressing(M):
        """[감사 v4 C/D-06] 휑함 5/5 해소 — "석탑 유적 / 전망대 광장" 판독 부여.
        전부 광장 상면 위 요소이며 위험 기하(개구·나선·셸)는 불변."""
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for i, (px, py) in enumerate(PARAMS["planters"]):
            sc.build_planter(stage, f"/World/Scene06/Planter_{i}", px, py, 0.0,
                             M["granite"], M["grass"], tree_mtls=tree_mtls)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"/World/Scene06/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"])
        # (1) 폐허 탑신 링 — 판독의 핵심. 난간(r3.2) 바깥 r4.35..4.85.
        ru = PARAMS["ruin"]
        for i, (a0, a1, htop) in enumerate(ru["arcs"]):
            nsg = max(2, int(round((a1 - a0) / ru["deg_per_seg"])))
            sc.build_arc_steps(stage, f"/World/Scene06/Ruin_{i}", cx, cy,
                               ru["r_in"], ru["r_out"], a0, a1, nsg,
                               htop, ru["base_z"], M["stone"])
        # (2) 유적 안내판 1조
        sg = PARAMS["sign"]
        sign_mtl = sc.make_pbr(stage, "/World/Looks/SignPanel",
                               diffuse_color=sg["color"], roughness_const=0.8)
        sc.add_box(stage, "/World/Scene06/Sign/Panel",
                   (sg["cx"], sg["cy"], sg["z"]),
                   (sg["t"], sg["w"], sg["h"]), sign_mtl)
        for k, dy in enumerate((-0.45, 0.45)):
            sc.add_cylinder(stage, f"/World/Scene06/Sign/Post_{k}",
                            (sg["cx"], sg["cy"] + dy, sg["post_h"] / 2.0),
                            sg["post_r"], sg["post_h"], M["granite"])
        # (3) 관람 벤치 4
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"/World/Scene06/Bench_{i}", bx, by, 0.0,
                           M["wood"], yaw=yaw)
        # (4) 볼라드 유도열 2줄 × 5 — 문 접근 축
        bo = PARAMS["bollards"]
        for yi, by in enumerate(bo["ys"]):
            for xi, bx in enumerate(bo["xs"]):
                sc.build_bollard(stage, f"/World/Scene06/Bollard_{yi}_{xi}",
                                 bx, by, 0.0, M["rail"])
        # (5) 경계 헤지 2 — 광장/잔디 직선 컷 완화
        hx = PARAMS["hedge_x"]
        for i, h in enumerate(PARAMS["hedges"]):
            sc.build_hedge(stage, f"/World/Scene06/Hedge_{i}", hx["x0"],
                           h["y0"], hx["x1"], h["y1"], hx["h"], base_z=-0.02)
        # (6) 자갈 apron 2 — 백색 포장 면적 축소
        ap = PARAMS["apron"]
        for i, a in enumerate(PARAMS["aprons"]):
            sc.add_box(stage, f"/World/Scene06/Apron_{i}",
                       ((a["x0"] + a["x1"]) / 2.0,
                        (ap["y0"] + ap["y1"]) / 2.0,
                        ap["top_z"] - ap["thick"] / 2.0),
                       (a["x1"] - a["x0"], ap["y1"] - ap["y0"], ap["thick"]),
                       M["gravel"])

    # -------------------------------------------------------------------
    # 단서 토글 (기하 불변)
    # -------------------------------------------------------------------
    def build_cues(M):
        # cue_material_break: 개구 둘레 다크 화강암 연석 링
        if cfg.get("cue_material_break"):
            c = PARAMS["curb"]
            sc.build_arc_steps(stage, "/World/Scene06/Curb", cx, cy,
                               c["r_in"], c["r_out"], 0.0, 360.0, c["seg"],
                               c["top_z"], c["base_z"], M["granite"])
        # cue_railing: 개구 둘레 부분 호 난간 (−X 관람측) — scene05 선택 구현
        if cfg.get("cue_railing"):
            rl = PARAMS["railing"]
            for ai, (a0, a1) in enumerate(rl["arcs"]):
                for k in range(rl["nposts"]):
                    a = math.radians(a0 + (a1 - a0) * k / (rl["nposts"] - 1))
                    px = cx + rl["r"] * math.cos(a)
                    py = cy + rl["r"] * math.sin(a)
                    sc.add_cylinder(stage,
                                    f"/World/Scene06/Rail/Post_{ai}_{k}",
                                    (px, py, rl["rail_h"] / 2.0), 0.02,
                                    rl["rail_h"], M["rail"])
                sc.build_arc_steps(stage, f"/World/Scene06/Rail/Top_{ai}",
                                   cx, cy, rl["r"] - 0.03, rl["r"] + 0.03,
                                   a0, a1, 12, rl["rail_h"],
                                   rl["rail_h"] - 0.04, M["rail"],
                                   collider=False)
        # cue_tactile: −X 접근 경고 점자띠 (개구 밖 서측)
        if cfg.get("cue_tactile"):
            tac = sc.make_pbr(stage, "/World/Looks/Tactile",
                              diffuse_color=(0.85, 0.72, 0.10),
                              roughness_const=0.7)
            sc.build_tactile(stage, "/World/Scene06/Tactile",
                             cx - 4.2, cx - 3.8, cy - 2.0, cy + 2.0, tac, z=0.0)
        # cue_nosing: 나선 단코 논슬립 (상수색 얇은 아크 밴드 — 각 단 전연부)
        if cfg.get("cue_nosing"):
            s = PARAMS["spiral"]
            nos = sc.make_pbr(stage, "/World/Looks/Nosing",
                              diffuse_color=mp["nosing_color"],
                              roughness_const=mp["nosing_rough"])
            for i in range(s["n"]):
                a0 = s["a0"] + i * s["step_deg"]
                top = s["z0"] - (i + 1) * s["riser"]
                sc.build_arc_steps(stage, f"/World/Scene06/Nosing_{i}", cx, cy,
                                   s["r_out"] - 0.06, s["r_out"], a0,
                                   a0 + s["step_deg"], 1, top + 0.004,
                                   top - 0.02, nos, collider=False)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hazard = cfg["hazard_stairs"]
    build_plaza(M, hazard)
    if hazard:
        build_tower(M)
    build_ground(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_cues(M)
    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── 스모크 모드: 조립+조명까지 확인하고 즉시 종료 (캡처·GUI 진입 전) ──
    if smoke_mode:
        nprim = sum(1 for pr in stage.Traverse() if pr.IsA(UsdGeom.Gprim))
        print(f"SMOKE_OK prims={nprim}")
        simulation_app.close()
        return

    # ── 카메라 + 렌더 모드 ──
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
    _v0 = VIEWS["opening_over"]
    look_from(_v0["eye"], _v0["tgt"])

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    # ── 자동 캡처 모드 (headless) ──
    if capture_mode:
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
                            set_render_mode, look_from)
        simulation_app.close()
        return

    # ── GUI 룩 체크 모드 (기본) ──
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene06_{ts}.png")
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
