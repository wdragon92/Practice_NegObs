# -*- coding: utf-8 -*-
"""
scene08_stepwell_lattice.py — NegObs 인공씬 8호: 스텝웰(계단우물) (Isaac Sim 4.5)

유형    : T11 스텝웰 미니어처 (사각 우물 12×12, 깊이 3.6·3층)
사양서  : Docs/briefs/multi_scene_brief_v3.md §D scene08_stepwell_lattice + 감독 보충
공통    : scene_common.py (검증 API 헬퍼) · scene02_underpass.py (개구 4박스 골격)

위험 본질: 상부 사암 테라스에 뚫린 12×12 사각 낙차(깊이 3.6). 격자 반복(대각
           미니 플라이트 지그재그)이 낙차 경계를 흡수해, 낮은 시점에서 우물이
           평탄한 문양 바닥으로 읽힘. 마주보는 두 벽(y±)의 다이아몬드 리듬이
           깊이 단서를 교란한다.
목표     : 상부 테라스(우물 개구 4박스 분할 + 파라펫 연석 링) + 4벽 우물 + 대각
           미니 플라이트(rot_group ±45°) + **계단식 층 링(역피라미드 단면)** +
           중앙 수면. (감사 v4: 수직 적층 선반 → 후퇴형 솔리드 링으로 교체)

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene08_stepwell_lattice.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene08_stepwell_lattice.py
스모크(부팅 전 기하 자기검증·조기종료):
    NEGOBS_SMOKE=1 python scene08_stepwell_lattice.py

좌표계: Z-up, m, 진행축 +X. 우물 개구 x 0..12, y -6..6 (중심 6,0). 테라스 z=0.

사암: scene_common.TEX `sandstone` 역할(실재질). 우물 내벽은 sandstone + 짙은
  틴트로 음영 흡수 톤을 준다(텍스처는 동일, 틴트만 상이).
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 7키. hazard_stairs 만 위험 기하 토글(우물↔평지).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 우물/플라이트/수면을 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        False,   # 스텝웰 원형: 난간 미관행. True → 개구 둘레 3면 파이프 난간
    "cue_tactile":        False,   # 사원 스텝웰엔 점자블록 미관행 — 코드 경로만 예약
    "cue_material_break": True,    # False → 플라이트도 테라스와 동일 사암(경계 흡수 강화)
    "cue_sign":           False,   # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,    # 파라펫 연석 링 + 원경 사암 회랑(지평 폐쇄)
    "cue_nosing":         False,   # [신규] True → 미니 플라이트 단코 띠
}


# ===========================================================================
# [B] PARAMS — 치수·재질·조명. NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG 머지.
# ===========================================================================
PARAMS = dict(
    # --- 우물 개구 12×12, 깊이 3.6(3층 × 1.2) ---
    well=dict(x0=0.0, x1=12.0, y0=-6.0, y1=6.0, z_top=0.0, depth=3.6,
              wall_t=0.4, floor_z=-3.6),
    # [감사 v4 A-08-2] setback 신설 — 층 선반을 같은 y 대역에 수직 적층하던 구조를
    #   **계단식 역피라미드 단면**(층마다 sb 만큼 안쪽으로 후퇴)으로 교체.
    #   ① V 하단 꼭짓점(벽에서 1.66 m)이 그 층 링(폭 1.9) 위에 착지(여유 0.24)
    #   ② 위층 선반 밑에 아래층 선반이 깔려 클리어런스 0.9 m 였던 문제 해소
    #   ③ 단면이 실제 스텝웰(계단우물)이 되어 "빈 수영장" 오판독 제거
    layers=dict(n=3, dz=1.2, setback=1.9),        # 층당 1.2 (5단 × 0.24)
    # 수면: 최하층 링 안쪽 자유 영역(x 3.8..8.2 · y ±2.2)에 0.1 인셋
    water=dict(x0=3.9, y0=-2.1, x1=8.1, y1=2.1, z=-3.4),
    # 대각 미니 플라이트: 5단 × riser 0.24 (drop 1.2 = 1층), tread 0.30, 폭 0.9
    #   reach = run/√2 (45° 회전 시 벽 따라 좌우 도달거리), base_drop=얇은 일관 두께
    # [감사 v4] base_drop 0.5→1.45: build_straight_stairs 는 밑면 고정(base_z)
    #   솔리드라 base_drop < 플라이트 낙차 1.2 면 3~5단째 박스 높이가 음수
    #   (상면 −0.72/−0.96/−1.2 < 밑면 −0.5) → "화살촉 덩어리" 렌더 결함의 원인.
    #   낙차 1.2 + 여유 0.25 로 솔리드 석조 플라이트화.
    #   xc: 층별 V 중심 x. 층 L 의 플라이트는 링 L−1 안쪽 모서리에서 출발해
    #     링 L 에 착지하므로, x 대역(xc±1.66)이 그 링의 x 범위 안이어야 한다.
    #     L0 ∈[1.66,10.34] / L1 ∈[3.56,8.44] / L2 ∈[5.46,6.54] → (3.0, 8.0, 6.0)
    flight=dict(nsteps=5, riser=0.24, tread=0.30, width=0.9,
                wall_overlap=0.05, base_drop=1.45, xc=(3.0, 8.0, 6.0)),
    # (링은 상면~바닥 솔리드이므로 thick 은 미사용 — 호환용 잔존 키)
    gallery=dict(thick=0.3),
    # [감사 v4 B-08-1] 장식 셰브런(맹계단) — 실제 V 는 층당 1조만 가능(2조를 같은
    #   x에 겹치면 아래 플라이트가 위 플라이트 밑에 매몰)하므로, 나머지 벽면에는
    #   라이저 면 부조로 다이아몬드 리듬을 복원한다. proud 0.18 = 통행 불가.
    chevrons=[dict(L=0, xc=6.5), dict(L=0, xc=9.8), dict(L=1, xc=4.0)],
    chevron=dict(proud=0.18),
    # --- 상부 사암 테라스 (개구를 4박스로 비움) ---
    terrace=dict(x_w=-12.0, x_e=24.0, y_s=-18.0, y_n=18.0, z_top=0.0,
                 thick=0.5),
    # 파라펫 연석 링(개구 테두리). [A-08-3] gap_pad: L0 플라이트 진입부에서
    #   연석을 끊어 "0.2 턱 넘고 곧바로 0.24 하강"하는 이중 단차를 제거한다.
    curb=dict(over=0.35, h=0.25, top=0.2, gap_pad=0.10),
    # --- 원경 사암 회랑(지평 폐쇄): 외곽 벽 h1.2→2.4 + 동측 기둥열 10 ---
    perim=dict(h=2.4, thick=0.5),
    perim_cols=dict(n=10, r=0.25, y0=-16.0, y1=16.0, inset=1.2),
    # --- [감사 v4 D-08] 스텝웰 맥락 드레싱 ---
    # 차트리(파빌리온) 4 — 개구 네 모서리 밖. 이것 하나로 "수영장"이 "사원 수조"로.
    chatri=[dict(x0=-1.8, x1=0.0, y0=-7.8, y1=-6.0),
            dict(x0=-1.8, x1=0.0, y0=6.0, y1=7.8),
            dict(x0=12.0, x1=13.8, y0=-7.8, y1=-6.0),
            dict(x0=12.0, x1=13.8, y0=6.0, y1=7.8)],
    chatri_p=dict(z_roof=2.6, post_r=0.13, roof_t=0.22),
    # 개구 둘레 사암 기둥열 (남·북 6 + 동·서 2) — 위험 기하에서 1.0 m 바깥
    col_ring=dict(r=0.17, h=1.8,
                  xs=(1.0, 3.2, 5.4, 7.6, 9.8, 12.0), y=7.0,
                  ys=(-3.0, 3.0), xw=-2.0, xe=14.0),
    # 테라스 화단 4
    planters=[(-6.0, -11.0), (-6.0, 11.0), (18.0, -11.0), (18.0, 11.0)],
    # 진입 축 벽 2 (서측) — 36×36 테라스 여백을 '우물로 향하는 통로'로 구조화
    axis_wall=dict(x0=-11.0, x1=-1.2, cy=3.4, t=0.4, h=0.9),
    # 수위 물때 밴드 — 우물 최하 벽면 z −3.35..−3.05
    stain=dict(z_hi=-3.05, z_lo=-3.35, proud=0.02,
               tint=(0.42, 0.44, 0.38)),

    # --- 재질: texture_scale용 물리 크기[m/타일] + 틴트/상수 ---
    material=dict(
        scale=dict(sandstone=1.0, grass=4.0),
        sandstone_dark_tint=(0.78, 0.72, 0.66),   # 우물 내벽(음영 흡수) 짙은 사암
        # [B-08-2] rough 0.06 → 0.14: 정오 돔이 균일 밝은 청록으로 클리핑되어
        #   "수영장 물"로 읽혔다. 거칠기를 올려 하늘 반사를 흐트러뜨린다.
        water_color=(0.05, 0.10, 0.11), water_rough=0.14,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
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
    # 표준 171.5 → 60.0 (감독 D-08①). 우물은 좁고 깊어 정오 표준광에선 내부 절반이
    #   완전 암흑 → 사광(az≈94)으로 한쪽 뱅크·내벽에 grazing 광을 넣는다. 반대편
    #   암부는 스텝웰의 미덕(명암 대비)이므로 허용. 태양고도(elev)는 정오 유지.
    SUN_AZ_OFFSET=60.0,

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
# [C] 경로 + 필요 텍스처 역할 (사암=stone_flag 대체, grass=원경·헤지)
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene08")
ASSET_ROLES = ["sandstone", "grass", "hdri", "mdl"]


# ===========================================================================
# [C2] 스모크 — 부팅/에셋 전 순수 기하 자기검증 (조기종료)
# ===========================================================================
def _smoke_report():
    w = PARAMS["well"]
    ly = PARAMS["layers"]
    fl = PARAMS["flight"]
    print("=" * 64)
    print("scene08_stepwell_lattice — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 64)
    depth = ly["n"] * ly["dz"]
    fdrop = fl["nsteps"] * fl["riser"]
    frun = fl["nsteps"] * fl["tread"]
    print(f"  우물 개구       : {w['x1']-w['x0']:.1f} × {w['y1']-w['y0']:.1f} m")
    print(f"  깊이(3층×{ly['dz']}): {depth:.2f} m  (floor_z={w['floor_z']})")
    print(f"  미니 플라이트   : {fl['nsteps']}단 × riser{fl['riser']} "
          f"= drop {fdrop:.2f} m (=1층 {ly['dz']}), run {frun:.2f} m, 폭 {fl['width']}")
    print(f"  수면 z          : {PARAMS['water']['z']}  (floor 위 "
          f"{PARAMS['water']['z']-w['floor_z']:.2f} m)")
    print(f"  플라이트 조수   : y±벽 × (V 1조 × {ly['n']}층) = {ly['n']}조/벽")
    print(f"  낙차 검증       : depth {depth:.2f} ≥ 0.3 m  → {'OK' if depth>=0.3 else 'FAIL'}")
    # [A-08-2] 층 링 후퇴 + V 착지 정합 검산
    sb = ly["setback"]
    reach = frun / math.sqrt(2.0)
    w0 = (fl["width"] - fl["wall_overlap"]) / math.sqrt(2.0)
    ok = True
    for L in range(ly["n"]):
        y_wall = w["y1"] - sb * L
        deep = y_wall - (reach + w0)               # V 최심 모서리 y
        edge = w["y1"] - sb * (L + 1)              # 그 층 링 안쪽 모서리
        floor_lv = (L == ly["n"] - 1)              # 최하층은 바닥 착지
        good = floor_lv or (deep - edge) >= 0.0
        ok = ok and good
        print(f"  L{L} 착지: 출발벽 y={y_wall:.2f} V최심 y={deep:.3f} "
              f"착지면={'바닥' if floor_lv else f'링 안쪽 {edge:.2f}'} "
              f"여유={0.0 if floor_lv else deep-edge:+.3f} "
              f"{'OK' if good else 'FAIL'}")
    print(f"  V 착지 정합     : {'OK' if ok else 'FAIL'}")
    print("=" * 64)


# ===========================================================================
# [D] 카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)                    # 중앙 대칭 → gy=0
    # corner_downview: 상부 모서리 부감 -12° (dx9,dz-2 → -12.5°)
    views["corner_downview"] = dict(eye=[-3.0, -9.0, 3.2], tgt=[6.0, -1.0, -1.5])
    # bank_front: 남 뱅크(y=-6 플라이트 벽) 정면 — 우물 내부 북측에서 -Y로 조망.
    #   r2 PT 판정: 북뱅크는 사광 az≈94에도 평균 5.9 암부 → 주석 대비책대로 플립.
    views["bank_front"] = dict(eye=[6.0, 1.5, 0.0], tgt=[6.0, -5.5, -1.8])
    # water_close: 중앙 수면 근접
    views["water_close"] = dict(eye=[3.0, 0.0, -2.4], tgt=[8.0, 0.0, -3.3])
    # beauty_overview: 사선 부감
    views["beauty_overview"] = dict(eye=[-7.0, -8.0, 4.0], tgt=[7.0, 0.0, -1.5])
    return views


# ===========================================================================
# [E] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. corner_downview / beauty — 스텝웰 인상 (개구·4벽·대각 플라이트·수면 식별)
 2. h0.3·d5~10              — 우물이 평탄한 문양 바닥으로 읽히는가 (낙차 흡수)
 3. bank_front              — y±벽 다이아몬드/V 리듬이 읽히는가(실 V + 셰브런)
 4. water_close             — 중앙 수면 + 계단식 링 3단 깊이감
 5. 재질                    — 사암 타일 반복·Z파이팅·부유 없는가 (개구 4박스)
 6. 진입                    — 연석이 끊긴 개구에서 단차 0.24 하나로 진입되는가
 7. 맥락                    — 차트리·기둥열·회랑이 '사원 수조'로 읽히는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # ── SMOKE: 부팅/에셋 검사 전 조기종료 (Isaac Sim 불필요) ──
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
    UsdGeom.Xform.Define(stage, "/World/Scene08")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene08"

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
        M["sandstone"] = PBR(
            f"{ROOT}/Looks/Sandstone", sc.tex_path("sandstone", "diff"),
            sc.tex_path("sandstone", "nor"), sc.tex_path("sandstone", "rough"),
            sca["sandstone"])
        M["sandstone_dark"] = PBR(
            f"{ROOT}/Looks/SandstoneDark", sc.tex_path("sandstone", "diff"),
            sc.tex_path("sandstone", "nor"), sc.tex_path("sandstone", "rough"),
            sca["sandstone"], tint=mp["sandstone_dark_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=(0.55, 0.68, 0.42))
        M["water"] = PBR(f"{ROOT}/Looks/Water",
                         diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        return M

    # -------------------------------------------------------------------
    # 상부 사암 테라스 — 개구(우물)를 4박스로 비움 (§A-3 공동 4박스)
    # -------------------------------------------------------------------
    def build_terrace(M):
        t = PARAMS["terrace"]
        w = PARAMS["well"]
        cz = t["z_top"] - t["thick"] / 2.0
        # 서: x_w..0 전폭
        BOX(f"{ROOT}/Terr_W",
            ((t["x_w"] + w["x0"]) / 2.0, (t["y_s"] + t["y_n"]) / 2.0, cz),
            (w["x0"] - t["x_w"], t["y_n"] - t["y_s"], t["thick"]),
            M["sandstone"], col=True)
        # 동: 12..x_e 전폭
        BOX(f"{ROOT}/Terr_E",
            ((w["x1"] + t["x_e"]) / 2.0, (t["y_s"] + t["y_n"]) / 2.0, cz),
            (t["x_e"] - w["x1"], t["y_n"] - t["y_s"], t["thick"]),
            M["sandstone"], col=True)
        # 남: 개구 x구간, y_s..-6
        BOX(f"{ROOT}/Terr_S",
            ((w["x0"] + w["x1"]) / 2.0, (t["y_s"] + w["y0"]) / 2.0, cz),
            (w["x1"] - w["x0"], w["y0"] - t["y_s"], t["thick"]),
            M["sandstone"], col=True)
        # 북: 개구 x구간, 6..y_n
        BOX(f"{ROOT}/Terr_N",
            ((w["x0"] + w["x1"]) / 2.0, (w["y1"] + t["y_n"]) / 2.0, cz),
            (w["x1"] - w["x0"], t["y_n"] - w["y1"], t["thick"]),
            M["sandstone"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 개구를 메워 전체 z=0 평지."""
        t = PARAMS["terrace"]
        BOX(f"{ROOT}/FlatTerr",
            ((t["x_w"] + t["x_e"]) / 2.0, (t["y_s"] + t["y_n"]) / 2.0,
             t["z_top"] - t["thick"] / 2.0),
            (t["x_e"] - t["x_w"], t["y_n"] - t["y_s"], t["thick"]),
            M["sandstone"], col=True)

    # -------------------------------------------------------------------
    # 파라펫 연석 링 — 개구 테두리 4박스 (top +0.2, 바깥으로 over 돌출)
    # -------------------------------------------------------------------
    def _entry_gaps():
        """[A-08-3] L0 플라이트 두 팔이 벽선(y=±6)에서 차지하는 x 대역 ±pad.
        좌팔(−45°)의 상단 단은 x ∈ [sx−w0, sx+e], 우팔(−135°)은 [sx−e, sx+w0].
          w0 = (width−ov)/√2 = 0.601,  e = (tread+ov)/√2 = 0.2475
        반환: [(gx0, gx1), ...] — 연석 링에서 비울 구간."""
        fl = PARAMS["flight"]
        pad = PARAMS["curb"]["gap_pad"]
        rt2 = math.sqrt(2.0)
        reach = fl["nsteps"] * fl["tread"] / rt2
        w0 = (fl["width"] - fl["wall_overlap"]) / rt2
        e = (fl["tread"] + fl["wall_overlap"]) / rt2
        xc0 = fl["xc"][0]
        return [(xc0 - reach - w0 - pad, xc0 - reach + e + pad),
                (xc0 + reach - e - pad, xc0 + reach + w0 + pad)]

    def build_curb(M):
        w = PARAMS["well"]
        cu = PARAMS["curb"]
        top = cu["top"]
        cz = top - cu["h"] / 2.0
        ov = cu["over"]
        # 남/북 연석 (x 방향, 개구 y경계 바깥) — 진입 개구 2곳에서 끊어 3분할
        edges = [w["x0"] - ov]
        for gx0, gx1 in _entry_gaps():
            edges += [gx0, gx1]
        edges.append(w["x1"] + ov)
        segs = [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]
        for tag, yc in (("S", w["y0"]), ("N", w["y1"])):
            for si, (sx0, sx1) in enumerate(segs):
                BOX(f"{ROOT}/Curb_{tag}_{si}",
                    ((sx0 + sx1) / 2.0, yc, cz),
                    (sx1 - sx0, ov, cu["h"]), M["sandstone"])
        # 서/동 연석 (y 방향)
        for tag, xc in (("W", w["x0"]), ("E", w["x1"])):
            BOX(f"{ROOT}/Curb_{tag}",
                (xc, (w["y0"] + w["y1"]) / 2.0, cz),
                (ov, w["y1"] - w["y0"], cu["h"]), M["sandstone"])

    # -------------------------------------------------------------------
    # 우물 4벽 + 바닥 — 개구를 둘러싼 셸 (사암 짙은 톤)
    # -------------------------------------------------------------------
    def build_well_shell(M):
        w = PARAMS["well"]
        t = w["wall_t"]
        # [A-08-3] 벽 상단 0.2 → 0.0(테라스 플러시). 기존엔 벽 상단(+0.2)과 연석
        #   (+0.2)이 개구 전 둘레에 폭 0.575 의 턱을 만들어, 진입 시 0.2 를 올라간
        #   뒤 곧바로 0.24 를 내려가는 이중 단차가 생겼다. 이제 연석만 +0.2 이며
        #   그 연석은 진입 개구에서 끊긴다 → 진입은 0.24 단 하나.
        z0, z1 = w["floor_z"], w["z_top"]
        cz = (z0 + z1) / 2.0
        hz = z1 - z0
        # 남 (y -6.4..-6), 북 (6..6.4)
        for tag, yc in (("S", w["y0"] - t / 2.0), ("N", w["y1"] + t / 2.0)):
            BOX(f"{ROOT}/WellWall_{tag}",
                ((w["x0"] + w["x1"]) / 2.0, yc, cz),
                (w["x1"] - w["x0"] + 2 * t, t, hz), M["sandstone_dark"], col=True)
        # 서 (x -0.4..0), 동 (12..12.4)
        for tag, xc in (("W", w["x0"] - t / 2.0), ("E", w["x1"] + t / 2.0)):
            BOX(f"{ROOT}/WellWall_{tag}",
                (xc, (w["y0"] + w["y1"]) / 2.0, cz),
                (t, w["y1"] - w["y0"], hz), M["sandstone_dark"], col=True)
        # 바닥 슬래브 (상면 floor_z)
        BOX(f"{ROOT}/WellFloor",
            ((w["x0"] + w["x1"]) / 2.0, (w["y0"] + w["y1"]) / 2.0,
             w["floor_z"] - 0.15),
            (w["x1"] - w["x0"] + 2 * t, w["y1"] - w["y0"] + 2 * t, 0.3),
            M["sandstone_dark"], col=True)

    # -------------------------------------------------------------------
    # 대각 미니 플라이트 (rot_group ±45°) — y±벽 V쌍 × 3층 = 6조/벽
    #   + 층간 갤러리 선반 (y±벽·x±벽)
    #
    # V쌍 기하(감독 D-08② 재계산): 각 층 중심 xc 에서 좌·우 팔이 상단 벽선의
    #   양 어깨(xc∓reach)에서 시작해 하단 중앙 (xc, y_wall∓reach) 로 수렴 → 깔끔한
    #   V(하단 꼭짓점). reach=run/√2 (45° 회전 시 수평 도달거리). 폭 밴드는 pit측
    #   으로 밀어 벽면과 wall_overlap(0.05)만 겹침(돌출 두께 base_drop 일관).
    #   xc 는 층마다 3m 균일 간격(3,6,9) → 인접 V 겹침 없음, 대칭.
    # -------------------------------------------------------------------
    def build_lattice(M, flight_mtl):
        w = PARAMS["well"]
        ly = PARAMS["layers"]
        fl = PARAMS["flight"]
        sb = ly["setback"]
        frun = fl["nsteps"] * fl["tread"]          # 1.5
        reach = frun / math.sqrt(2.0)              # ≈1.061
        ov = fl["wall_overlap"]

        def mini_flight(name, start_x, angle, y_wall, z_top):
            """대각 미니 플라이트 1팔. 폭 밴드는 **회전 후 pit 쪽으로** 놓는다.
            로컬 +Y 는 회전 후 월드 (−sin a, cos a) 로 간다. 벽이 +y 쪽(y_wall>0)
            이면 로컬 +Y 의 월드 y 성분 cos(a) 가 양수일 때 로컬 +Y 가 벽 쪽이다.
              벽 쪽 → 밴드 dy ∈ [−(width−ov), +ov]
              pit 쪽 → 밴드 dy ∈ [−ov, +(width−ov)]
            [감사 v4 추가결함] 기존 코드는 두 팔에 같은 밴드를 써서 우팔(−135°)의
            폭이 pit 이 아니라 **벽 바깥(y 6.60)** 으로 뻗었다 → V 가 비대칭이고
            우팔 꼭짓점이 좌팔보다 0.57 m 얕게 끝났다. 아래 판정으로 대칭 복원."""
            toward_wall = (math.cos(math.radians(angle))
                           * (1.0 if y_wall > 0 else -1.0)) > 0.0
            if toward_wall:
                dy0, dy1 = -(fl["width"] - ov), ov
            else:
                dy0, dy1 = -ov, fl["width"] - ov
            grp = sc.build_rot_group(stage, f"{ROOT}/Flight_{name}",
                                     (start_x, y_wall), angle)
            sc.build_straight_stairs(
                stage, f"{grp}/Steps", start_x, y_wall + dy0, y_wall + dy1,
                fl["riser"], fl["tread"], fl["nsteps"],
                z_top - fl["base_drop"], flight_mtl, z_top=z_top, collider=True)

        # (1) 층 링(테라스형 뱅크) — 층마다 sb 만큼 안쪽으로 후퇴한 사각 링 4박스.
        #     최하층(L=n−1) 착지면은 우물 바닥이므로 링은 n−1 개.
        #     각 링은 **상면에서 바닥(floor_z)까지 솔리드**. 얇은 선반(0.3)으로
        #     두면 아래가 비어 '떠 있는 발코니'가 되고, 라이저 면이 0.3 밖에 안 돼
        #     셰브런 부조·물때 밴드가 붙을 벽면이 생기지 않는다.
        for L in range(ly["n"] - 1):
            zb = w["z_top"] - ly["dz"] * (L + 1)
            hz = zb - w["floor_z"]
            cz = zb - hz / 2.0
            ox0, ox1 = w["x0"] + sb * L, w["x1"] - sb * L
            oy0, oy1 = w["y0"] + sb * L, w["y1"] - sb * L
            ix0, ix1 = w["x0"] + sb * (L + 1), w["x1"] - sb * (L + 1)
            iy0, iy1 = w["y0"] + sb * (L + 1), w["y1"] - sb * (L + 1)
            for tag, bx0, bx1, by0, by1 in (
                    ("N", ox0, ox1, iy1, oy1), ("S", ox0, ox1, oy0, iy0),
                    ("W", ox0, ix0, iy0, iy1), ("E", ix1, ox1, iy0, iy1)):
                BOX(f"{ROOT}/Ring_{L}_{tag}",
                    ((bx0 + bx1) / 2.0, (by0 + by1) / 2.0, cz),
                    (bx1 - bx0, by1 - by0, hz), M["sandstone"], col=True)

        # (2) V 쌍 — y± 벽, 층별. 층 L 은 링 L−1 안쪽 모서리(=y_wall)에서 출발해
        #     링 L(최하층은 바닥)에 착지. 꼭짓점 최심 y = y_wall − 1.66 이고
        #     링 L 의 안쪽 모서리는 y_wall − 1.90 → 여유 0.24 m (착지 성립).
        for wsign, wtag in ((1.0, "N"), (-1.0, "S")):
            for L in range(ly["n"]):
                y_wall = (w["y1"] - sb * L) * wsign
                z_top = w["z_top"] - ly["dz"] * L
                xc = fl["xc"][L]
                mini_flight(f"{wtag}_L{L}_a", xc - reach, -45.0 * wsign,
                            y_wall, z_top)
                mini_flight(f"{wtag}_L{L}_b", xc + reach, -135.0 * wsign,
                            y_wall, z_top)

        # (3) 장식 셰브런(맹계단) — 각 층 라이저 면에 proud 부조로 다이아몬드 리듬
        ch = PARAMS["chevron"]
        for ci, c in enumerate(PARAMS["chevrons"]):
            L, xcv = c["L"], c["xc"]
            z_top = w["z_top"] - ly["dz"] * L
            for wsign, wtag in ((1.0, "N"), (-1.0, "S")):
                y_face = (w["y1"] - sb * L) * wsign
                yc = y_face - wsign * ch["proud"] / 2.0
                for s in (-1, 1):
                    for j in range(fl["nsteps"]):
                        bx = xcv + s * (j + 0.5) * fl["tread"]
                        bz = z_top - (j + 1) * fl["riser"]
                        BOX(f"{ROOT}/Chevron_{ci}{wtag}_{'m' if s < 0 else 'p'}"
                            f"_{j}", (bx, yc, bz - fl["riser"] / 2.0),
                            (fl["tread"], ch["proud"], fl["riser"]),
                            M["sandstone_dark"])

    # -------------------------------------------------------------------
    # 중앙 수면
    # -------------------------------------------------------------------
    def build_water(M):
        wt = PARAMS["water"]
        sc.build_water(stage, f"{ROOT}/Water", wt["x0"], wt["y0"], wt["x1"],
                       wt["y1"], wt["z"], mtl=M["water"])

    # -------------------------------------------------------------------
    # 원경 사암 회랑 (지평 폐쇄) — 테라스 외곽 파라펫 벽 링 4박스
    # -------------------------------------------------------------------
    def build_dressing(M):
        """[감사 v4 C/D-08] 휑함 5/5 해소 — "스텝웰 / 사원 수조" 판독 부여.
        전부 테라스(z=0) 위 요소이며 우물 기하는 불변."""
        t = PARAMS["terrace"]
        pe = PARAMS["perim"]
        cz = t["z_top"] + pe["h"] / 2.0
        # 외곽 벽 링 (h 2.4 = 회랑 높이) — 서·동 (y 방향 벽)
        for tag, xc in (("W", t["x_w"]), ("E", t["x_e"])):
            BOX(f"{ROOT}/Perim_{tag}", (xc, 0.0, cz),
                (pe["thick"], t["y_n"] - t["y_s"], pe["h"]),
                M["sandstone"], col=True)
        # 남·북 (x 방향 벽)
        for tag, yc in (("S", t["y_s"]), ("N", t["y_n"])):
            BOX(f"{ROOT}/Perim_{tag}",
                ((t["x_w"] + t["x_e"]) / 2.0, yc, cz),
                (t["x_e"] - t["x_w"], pe["thick"], pe["h"]),
                M["sandstone"], col=True)
        # 동측 벽 앞 기둥열 10 — 원경이 '판때기'가 아니라 '회랑'으로 읽히게
        pc = PARAMS["perim_cols"]
        for i in range(pc["n"]):
            yy = pc["y0"] + (pc["y1"] - pc["y0"]) * i / (pc["n"] - 1)
            CYL(f"{ROOT}/PerimCol_{i}",
                (t["x_e"] - pc["inset"], yy, pe["h"] / 2.0),
                pc["r"], pe["h"], M["sandstone"], col=True)
        # 차트리(파빌리온) 4 — 개구 네 모서리 밖
        cp = PARAMS["chatri_p"]
        for i, c in enumerate(PARAMS["chatri"]):
            sc.build_canopy(stage, f"{ROOT}/Chatri_{i}", c["x0"], c["x1"],
                            c["y0"], c["y1"], cp["z_roof"], cp["post_r"],
                            M["sandstone"], M["sandstone"],
                            roof_t=cp["roof_t"])
        # 개구 둘레 사암 기둥열 (남·북 6 + 동·서 2)
        cr = PARAMS["col_ring"]
        for i, xx in enumerate(cr["xs"]):
            for tag, yy in (("N", cr["y"]), ("S", -cr["y"])):
                CYL(f"{ROOT}/WellCol_{tag}_{i}", (xx, yy, cr["h"] / 2.0),
                    cr["r"], cr["h"], M["sandstone"], col=True)
        for i, yy in enumerate(cr["ys"]):
            for tag, xx in (("W", cr["xw"]), ("E", cr["xe"])):
                CYL(f"{ROOT}/WellColX_{tag}_{i}", (xx, yy, cr["h"] / 2.0),
                    cr["r"], cr["h"], M["sandstone"], col=True)
        # 테라스 화단 4
        for i, (px, py) in enumerate(PARAMS["planters"]):
            sc.build_planter(stage, f"{ROOT}/Planter_{i}", px, py, 0.0,
                             M["sandstone"], M["grass"], size=3.5)
        # 진입 축 벽 2 (서측)
        aw = PARAMS["axis_wall"]
        for tag, yy in (("N", aw["cy"]), ("S", -aw["cy"])):
            BOX(f"{ROOT}/AxisWall_{tag}",
                ((aw["x0"] + aw["x1"]) / 2.0, yy, aw["h"] / 2.0),
                (aw["x1"] - aw["x0"], aw["t"], aw["h"]), M["sandstone"],
                col=True)

    def build_stain(M):
        """[B-08-3] 수위 물때 밴드 — 최하층 링 안쪽 4면에 얇은 띠(재질만 상이).
        수면 폴리곤이 잘려 보이던 것을 '수위선'이라는 재질 신호로 보완한다."""
        w = PARAMS["well"]
        ly = PARAMS["layers"]
        st = PARAMS["stain"]
        sb = ly["setback"]
        n_in = ly["n"] - 1                          # 최하 링의 안쪽 인셋 배수
        ix0, ix1 = w["x0"] + sb * n_in, w["x1"] - sb * n_in
        iy0, iy1 = w["y0"] + sb * n_in, w["y1"] - sb * n_in
        h = st["z_hi"] - st["z_lo"]
        cz = (st["z_hi"] + st["z_lo"]) / 2.0
        p = st["proud"]
        mtl = PBR(f"{ROOT}/Looks/Stain", sc.tex_path("sandstone", "diff"),
                  sc.tex_path("sandstone", "nor"),
                  sc.tex_path("sandstone", "rough"),
                  mp["scale"]["sandstone"], tint=st["tint"])
        for tag, bx, by, sx, sy in (
                ("W", ix0 + p / 2.0, (iy0 + iy1) / 2.0, p, iy1 - iy0),
                ("E", ix1 - p / 2.0, (iy0 + iy1) / 2.0, p, iy1 - iy0),
                ("S", (ix0 + ix1) / 2.0, iy0 + p / 2.0, ix1 - ix0, p),
                ("N", (ix0 + ix1) / 2.0, iy1 - p / 2.0, ix1 - ix0, p)):
            BOX(f"{ROOT}/Stain_{tag}", (bx, by, cz), (sx, sy, h), mtl)

    # -------------------------------------------------------------------
    # 단서 (cue) — nosing / railing (스텝웰 원형은 기본 OFF)
    # -------------------------------------------------------------------
    def build_cues(M, flight_mtl):
        w = PARAMS["well"]
        # cue_railing: 개구 지상 둘레 3면 파이프 난간 (연석 위 수평 레일)
        if cfg["cue_railing"]:
            top = PARAMS["curb"]["top"]
            rail_h = 0.9
            rz = top + rail_h
            for tag, yc in (("S", w["y0"]), ("N", w["y1"])):
                CYL(f"{ROOT}/PerimRail_{tag}",
                    ((w["x0"] + w["x1"]) / 2.0, yc, rz), 0.03,
                    w["x1"] - w["x0"], M["rail"], rotY=90.0)
            CYL(f"{ROOT}/PerimRail_E",
                (w["x1"], (w["y0"] + w["y1"]) / 2.0, rz), 0.03,
                w["y1"] - w["y0"], M["rail"], rotX=90.0)
        # cue_nosing: 대각 미니 플라이트 단코 띠 (rot_group 재현 생략 — 대표 벽만)
        # (기하 흡수 유형 특성상 기본 OFF; 코드 경로만 유지)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    flight_mtl = M["sandstone_dark"] if cfg["cue_material_break"] else M["sandstone"]

    if cfg["hazard_stairs"]:
        build_terrace(M)
        build_curb(M)
        build_well_shell(M)
        build_lattice(M, flight_mtl)
        build_water(M)
        build_stain(M)
        build_cues(M, flight_mtl)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── 카메라 + 렌더 모드 ──
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene08_{ts}.png")
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
