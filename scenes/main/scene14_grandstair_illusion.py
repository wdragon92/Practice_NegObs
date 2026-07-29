# -*- coding: utf-8 -*-
"""
scene14_grandstair_illusion.py — NegObs 인공씬 14호: 착시 기념계단 (Isaac Sim 4.5)

유형    : T14 포템킨형 착시 대계단 (40단, 참 3개, 폭 점증 tapered)
사양서  : Docs/multi_scene_brief_v3.md §D scene14_grandstair_illusion + 감독 보충
공통    : scene_common.py (build_straight_stairs width_pairs) · scene02 골격

위험 본질: 상부 전망 소광장에서 진행하면 40단 계단의 '참(landing)'만 눈에 들어와
           평탄한 테라스로 오독된다. 실제로는 낙차 6.0 m가 참 사이에 숨는다.
           폭이 상부 y±3 → 하부 y±5 로 벌어지는 원근 착시가 은닉을 강화.
목표     : 상부 소광장(화강암) + 40단(참 3개, width_pairs 연속) + 측면 경사
           파라펫 + 하부 대광장(분수 힌트) + 원경 건물 2동을 조립.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene14_grandstair_illusion.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene14_grandstair_illusion.py
스모크(부팅 전 기하 자기검증·조기종료):
    NEGOBS_SMOKE=1 python scene14_grandstair_illusion.py

좌표계: Z-up, m, 진행축 +X, 낙차 시작 모서리 = x=0. 총 낙차 6.0 m.

대리석: scene_common.TEX `marble_light` 역할(실재질).
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 7키. hazard_stairs 만 위험 기하 토글.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 계단/참을 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        False,   # 기념계단은 개방형 — True → 측면 파라펫 위 파이프 레일
    # [v5 공통 레이어] 도시 관행 씬(01/02/05/13/14/16/20/21) cue_tactile 기본 True.
    #   구 주석의 '미관행'은 v5 무대 명확화(시청/문화회관 앞 광장 대계단)로 무효 —
    #   관공서 대계단 진입부 점자블록은 국내 표준 관행이다. 실제 지오메트리 생성.
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)    # 상단 진입 경고 점자띠 (x −0.4..0, 계단 상부 폭)
    "cue_material_break": True,    # False → 상·하부 광장도 대리석으로 통일(경계 흡수)
    "cue_sign":           True,    # [v5 공통 레이어] sign_info(광장 안내) 1매
    "cue_scene_dressing": True,    # 가로등·파라펫 연석·분수 힌트·원경 건물
    "cue_nosing":         False,   # [신규] True → 전 단 단코 띠
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- 대계단: 40단, riser 0.15 (낙차 6.0), tread 0.34, 참 3개(깊이 2.4) ---
    stairs=dict(x0=0.0, riser=0.15, tread=0.34, nsteps=40, z_top=0.0,
                base_z=-6.7, seg_len=10, landing_depth=2.4,
                w_top=3.0, w_bot=5.0),            # 반폭: 상부 y±3 → 하부 y±5
    landings=(10, 20, 30),                        # 참 삽입 위치(단 뒤)
    # --- 상부 전망 소광장(대리석 계단머리, 화강암 대신 marble) ---
    upper=dict(x0=-9.0, x1=0.0, y0=-8.0, y1=8.0, z_top=0.0, thick=0.5),
    # --- 대형 상부 광장 (감독 D-14 r3①): 테라스 뒤 -X로 20m × y±20, plaza_light.
    #     계단이 상·하 두 레벨을 잇는 구조로 읽히게 (고립 제거). 테라스 구멍 3박스.
    upper_big=dict(x0=-29.0, x1=0.0, y0=-20.0, y1=20.0, z_top=0.0, thick=0.5),
    streetlight=dict(pole_h=5.0, pole_r=0.06, arm_len=1.0, arm_r=0.04,
                     head=0.25, xs=(-6.0, -14.0, -22.0), ys=(-6.0, 6.0)),
    # --- 하부 대광장 (plaza_lower + band_dark 밴드) + 분수 힌트 ---
    #     x1 40→75 : 원경 건물 발치까지 지면을 깔아 5 m 부유 해소 [B-14-1 치명]
    lower=dict(x1=75.0, y0=-20.0, y1=20.0, z_top=-6.0, thick=0.5),
    # --- 계단 좌우 경사 잔디 사면 (감독 D-14 r3②): 파라펫 바깥 y±5.2..±20 상→하 ---
    #     thick 0.5→3.0 : 얇은 판이 허공에 뜬 채 보이던 문제 해소(솔리드 사면 매시프)
    #     run_ext 3.2   : 하단 끝단면(경사 절단 쐐기)을 하부 광장 아래로 숨김
    side_slope=dict(y_out=20.0, thick=3.0, run_ext=3.2),
    fountain=dict(cx=30.0, cy=0.0, r_out=3.0, r_in=2.4, h=0.4,
                  nozzles=5, nozzle_r=0.06, nozzle_h=0.5),
    # --- 측면 파라펫 (폭 0.5) ---
    #     thick 0.4→1.6 : 계단식 어깨면(build_shoulder)에 전 구간 매입시켜 부유 제거
    #     [v5.1] cap_t : 상단 경사 헌치(사선 솔리드) 슬래브 두께 — build_parapets
    #       docstring 의 물림 검산(수직 환산 1.530 > 필요 0.43+0.03) 참조.
    parapet=dict(width=0.5, z0=0.35, thick=1.6, cap_t=1.4),
    # --- 계단 밖 어깨면(구 소핏 대체) — build_shoulder 참조 ---
    shoulder=dict(y_out=5.2, offset=0.03, lap=0.05),
    # --- 원경 건물 5동 (지평 폐쇄, 하부 광장 위 — base_z 로 접지) ---
    buildings=dict(
        B=dict(x0=42.0, x1=48.0, y0=-14.0, y1=14.0, h=12.0, floors=5,
               axis="x", facade_x=42.0, face_dir=-1.0, base_z=-6.0),
        C=dict(x0=30.0, x1=40.0, y0=13.0, y1=19.0, h=10.0, floors=4,
               axis="y", facade_y=13.0, face_dir=-1.0, base_z=-6.0),
        F=dict(x0=30.0, x1=40.0, y0=-19.0, y1=-13.0, h=9.0, floors=3,
               axis="y", facade_y=-13.0, face_dir=1.0, base_z=-6.0),
        D=dict(x0=56.0, x1=70.0, y0=-19.0, y1=-6.0, h=22.0, floors=7,
               axis="x", facade_x=56.0, face_dir=-1.0, base_z=-6.0),
        E=dict(x0=56.0, x1=70.0, y0=4.0, y1=19.0, h=18.0, floors=6,
               axis="x", facade_x=56.0, face_dir=-1.0, base_z=-6.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),
    # --- 맥락 드레싱 (기념광장 즉독) — 전부 기존 빌더 조합, cue_scene_dressing 소속 ---
    dressing=dict(
        # 하부 대광장(z −6.0)
        trees_low=((24.0, 7.0), (24.0, -7.0), (24.0, 13.0), (24.0, -13.0),
                   (33.0, 10.0), (33.0, -10.0)),
        planters_low=((25.5, 4.0), (25.5, -4.0), (34.5, 4.0), (34.5, -4.0)),
        benches_low=((22.5, 5.0), (22.5, -5.0), (22.5, 10.0), (22.5, -10.0),
                     (22.5, 15.0), (22.5, -15.0)),
        # [v5.1 §2] 볼라드 — 구: x 21.6 에 y −12..12 를 2.0 m 등간격 13본
        #   (①등간격 장식열 ②**y=0 본이 계단 축선 위**). 규정 배치로 교체:
        #   간격 1.5 m · 축선(y=0)을 비운 좌우 대칭 10본 = 계단 진입 전면
        #   차량 차단선(§2 허용 위치). 높이/지름/반사띠는 build_bollard_std 참조.
        #   점형블록은 이 씬에서 **의도적으로 생략** — 계단 발치(x 21.6)에
        #   토글되지 않는 황색 경고띠를 두면 '참만 보여 평탄해 보인다'는 본 씬의
        #   은닉 착시에 상시 단서가 섞인다(cue_tactile 토글 무결성 위반).
        bollard_x=21.6,
        bollard_ys=(-6.75, -5.25, -3.75, -2.25, -0.75,
                    0.75, 2.25, 3.75, 5.25, 6.75),
        # [v6 판정 §3-2] 깃대 4본 — 구 x 24.5 · y ±6/±10 은 **3라운드 연속**
        #   beauty_overview(eye 28,−14,4 → tgt 6,0,−2.5, 시선 방위 147.5°) 전경을
        #   침범했다. 역산: (24.5,−10) 은 카메라에서 수평 5.31 m · 방위차 −16.3°
        #   (화각 ±30° 한복판, 화면 우측), 깃대 상단 z 3.0 이 아이레벨 4.0 바로
        #   아래라 세로로 화면을 관통하고 흑색 깃발이 계단면을 가렸다.
        #   (24.5,−6) 도 8.73 m · −33.9° 로 프레임 경계.
        #   판정 대안 "eye 를 +Y 1.5 m" 는 **역효과** — eye y −14→−12.5 이면
        #   (24.5,−10) 방위차가 −16.3° → −5.9° 로 오히려 중앙에 온다. 따라서
        #   **깃대 이설**을 택한다: 분수(30, 0, r_out 3.0) 를 좌우로 끼는
        #   x 30.0 · y ±7 / ±12 — 기념광장 분수단 깃대열(실존 관행).
        #   카메라 검산(화각 ±30°, 반수직 ±18°):
        #     beauty_overview : −73.5° / −102.5° / −63.0° / −61.9°  = 전부 밖
        #     lower_lookup(eye 26,0 → tgt 8,0, 방위 180°) : ±119.7° / ±108.4° 밖
        #     side_reveal(방위 42.5°) : −13.9°(37.6 m) · −7.6°(40.2 m) 원경만,
        #                               −Y 2본은 −35.6° / −44.2° 밖
        #     terrace_read(방위 0°)   : ±11.6° / ±19.4°, 34.7~36 m 원경(앙각 3.5°)
        #     grid preset(eye x −2..−10) : ±12.3° 내외, 32.8 m 원경 — 착시 무영향
        #   이격 : 분수 림 4.0 m · 가로수(33,±10) 3.61 m · 화단(34.5,±4) 5.41 m
        flags=((30.0, 7.0), (30.0, -7.0), (30.0, 12.0), (30.0, -12.0)),
        # 상부 광장(z 0)
        trees_up=((-20.0, 14.0), (-20.0, -14.0), (-26.0, 14.0), (-26.0, -14.0)),
        benches_up=((-12.0, 5.0), (-12.0, -5.0), (-20.0, 5.0), (-20.0, -5.0)),
        # [v5.1] 축선 비움 — 구 (−15.0, 0.0) 은 상부 광장 중심축 위여서
        #   lower_lookup(eye 26,0,−5.2) 에서 샤프트 상단(z 9.8, 앙각 20.1°)이
        #   계단 마루선(앙각 11.3°) 위로 솟아 **축선 소실점을 막았다**.
        #   측면(y −6.5)으로 이설 — 생울타리 S(y −10.5..−9.0) 안쪽 1.0 m,
        #   벤치(−12,−5)/(−20,−5) 에서 3.35 m 이격.
        monument=(-15.0, -6.5),
        hedges=(("N", -29.0, 9.0, -9.0, 10.5), ("S", -29.0, -10.5, -9.0, -9.0),
                ("W", -29.0, -9.0, -27.5, 9.0)),
        curb_gap=2.5,                     # 상부 경계석 중앙 개구 반폭 [A-14-5]
    ),
    # [v5 공통 레이어] 점자블록 — 계단 상단 모서리(x=0) 앞 0.4 m, 상부 폭 y ±3.
    #   대리석 테라스(x −9..0, z 0) 위. 위험 기하(계단·참) 트랜스폼 불변.
    tactile=dict(ahead=0.4, proud=0.004),
    # [v5 공통 레이어] 한글 사인 — (태그, TEX 키, cx, cy, base_z, yaw, w, h)
    #   Info(−6.5, −4.2): 상부 대리석 테라스(x −9..0, y ±8) 위 광장 안내판.
    #     계단 상단 모서리 최근접점 (0, −3) 까지 6.61 m — 이격 ≥0.5 m 충족.
    #     상부 경계석(x −9.0..−8.5) 동측 2.0 m, 가로등(−6.0, −6.0) 에서 1.80 m.
    #   카메라 검산(그리드 gy=0, eye x −2/−5/−10, 화각 ±30°):
    #     −2/−5 → 후방, −10 → −50.2° (프레임 밖)
    #     terrace_read(−4,0) 후방 · side_reveal(−3,−11) 74.7° 밖
    #     lower_lookup(26,0) 7.4°(32.8 m 원경·계단 매시프 뒤) ·
    #     beauty_overview(28,−14) 16.6°(35.9 m 원경) → 근접 차폐 0
    signs=[("Info", "sign_info", -6.5, -4.2, 0.0, 180.0, 1.0, 0.75)],

    material=dict(
        scale=dict(marble_light=1.2, granite_dark=1.0, plaza_lower=0.7,
                   band_dark=0.5, brick_red=2.0, plaza_light=1.80, grass=1.4,
                   tactile=0.3),                      # [v5 공통 레이어]
        grass_tint=(0.55, 0.68, 0.42),
        # B-14-5: 전 화면 고명도 몰림 해소 — 파사드 0.56→0.30, 파라펫 0.90→0.62
        bldg_color=(0.30, 0.30, 0.33), bldg_rough=0.6,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.62, 0.62, 0.60), parapet_rough=0.6,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        water_color=(0.05, 0.10, 0.11), water_rough=0.06,
        wood_color=(0.20, 0.14, 0.09),
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
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
# [C] 경로 + 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene14")
ASSET_ROLES = ["marble_light", "granite_dark", "plaza_lower", "band_dark",
               "brick_red", "plaza_light", "grass",
               "tactile", "sign_info",                # [v5 공통 레이어]
               "hdri", "mdl"]


# ===========================================================================
# [C2] 폭 점증(width_pairs) — 전 단 i(1..n)의 반폭 선형 보간 (참 포함 연속)
# ===========================================================================
def _half_width(i, n, w_top, w_bot):
    """단 i(1-based)의 반폭. i=1→w_top, i=n→w_bot 선형."""
    if n <= 1:
        return w_top
    return w_top + (w_bot - w_top) * (i - 1) / (n - 1)


# ===========================================================================
# [C3] 스모크 — 부팅 전 기하 자기검증 (조기종료)
# ===========================================================================
def _smoke_report():
    st = PARAMS["stairs"]
    print("=" * 64)
    print("scene14_grandstair_illusion — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 64)
    n = st["nsteps"]
    drop = n * st["riser"]
    run = n * st["tread"]
    nland = len(PARAMS["landings"])
    total_x = run + nland * st["landing_depth"]
    print(f"  계단: {n}단 × riser {st['riser']} = 낙차 {drop:.2f} m")
    print(f"  run(디딤) {run:.2f} + 참 {nland}×{st['landing_depth']} "
          f"= 총 X {total_x:.2f} m")
    print(f"  폭 점증(반폭): 상부 {st['w_top']} → 하부 {st['w_bot']}")
    for i in (1, 10, 20, 30, 40):
        hw = _half_width(i, n, st["w_top"], st["w_bot"])
        print(f"    단 {i:2d}: 반폭 {hw:.3f}  (y ±{hw:.3f}, 전폭 {2*hw:.2f})")
    print(f"  낙차 검증: {drop:.2f} ≥ 0.3 m → {'OK' if drop >= 0.3 else 'FAIL'}")
    # ── 레벨 z 표 (감독 D-14 r3④) ──
    ub = PARAMS["upper_big"]
    lo = PARAMS["lower"]
    z_bot = lo["z_top"] - 0.3
    print("  [레벨 z 표]")
    rows = [
        ("상부 광장(대형) plaza_light", f"x[{ub['x0']},{ub['x1']}] y±{ub['y1']}",
         ub["z_top"]),
        ("상부 테라스(계단머리) marble", "x[-9,0] y±8", PARAMS["upper"]["z_top"]),
        ("계단 상단", "x=0", st["z_top"]),
        ("계단 하단(40단)", f"x={total_x:.2f}", st["z_top"] - drop),
        ("계단 밖 어깨면(단별)", "|y| hw..5.2", "디딤면 -0.03"),
        ("측면 경사 잔디 사면", "y±5.2..±20", "0.0→-6.0"),
        ("하부 대광장 plaza_lower", f"x[..{lo['x1']}] y±{lo['y1']}", lo["z_top"]),
        ("기단 매시프 바닥", "상부 풋프린트", z_bot),
    ]
    for name, ext, z in rows:
        zs = z if isinstance(z, str) else f"{z:+.2f}"
        print(f"    {name:28s} {ext:22s} top z={zs}")
    print("=" * 64)


# ===========================================================================
# [D] 카메라 프리셋
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)                    # preset_h0.9_d5 = 착시 확인 지점
    # terrace_read: 상부에서 참만 보여 평탄 테라스로 읽힘 (h0.9, 약한 부감)
    views["terrace_read"] = dict(eye=[-4.0, 0.0, 0.9], tgt=[6.0, 0.0, 0.1])
    # side_reveal: 측면 사선 — 실제 낙차 폭로
    views["side_reveal"] = dict(eye=[-3.0, -11.0, 3.5], tgt=[9.0, 0.0, -3.0])
    # lower_lookup: 하부 대광장에서 계단 올려봄
    views["lower_lookup"] = dict(eye=[26.0, 0.0, -5.2], tgt=[8.0, 0.0, -2.0])
    # beauty_overview: 하부 광장 모서리 부감 (감독 D-14③, d≈18/h4 — 미장센 밴드
    #   예외). 40단 전폭 + 참 3개 + 상부 테라스가 한 프레임에.
    views["beauty_overview"] = dict(eye=[28.0, -14.0, 4.0], tgt=[6.0, 0.0, -2.5])
    return views


# ===========================================================================
# [E] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. terrace_read / preset_h0.9_d5 — 참만 보여 평탄 테라스로 읽히는가 (은폐 착시)
 2. h0.3·d5~10                    — 낙차 6.0이 grazing 에서 완전 소실되는가
 3. side_reveal                   — 측면에서 40단·참 3개 실체 확인
 4. lower_lookup                  — 하부 대광장·분수 힌트·건물 지평
 5. 재질                          — 폭 점증 tapered 연속·Z파이팅·부유 없는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene14")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene14"

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
        M["marble"] = PBR(
            f"{ROOT}/Looks/Marble", sc.tex_path("marble_light", "diff"),
            sc.tex_path("marble_light", "nor"), sc.tex_path("marble_light", "rough"),
            sca["marble_light"])
        M["granite"] = PBR(
            f"{ROOT}/Looks/Granite", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"),
            sc.tex_path("granite_dark", "rough"), sca["granite_dark"])
        M["plaza_lower"] = PBR(
            f"{ROOT}/Looks/PlazaLower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"),
            sc.tex_path("plaza_lower", "rough"), sca["plaza_lower"])
        M["band"] = PBR(
            f"{ROOT}/Looks/Band", sc.tex_path("band_dark", "diff"),
            sc.tex_path("band_dark", "nor"), sc.tex_path("band_dark", "rough"),
            sca["band_dark"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["plaza_light"] = PBR(
            f"{ROOT}/Looks/PlazaLight", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["bldg"] = PBR(f"{ROOT}/Looks/Bldg", diffuse_color=mp["bldg_color"],
                        roughness_const=mp["bldg_rough"], metallic=0.0)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
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
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        # 드레싱 수목(어두운 상수색 0.02~0.06 규약)
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=0.85)
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=1.0, specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=1.0, specular_level=0.0)
        # [v5 공통 레이어] 점형 점자블록(황색) — diff+nor 만(rough 없음)
        M["tactile"] = PBR(f"{ROOT}/Looks/Tactile",
                           sc.tex_path("tactile", "diff"),
                           sc.tex_path("tactile", "nor"), None,
                           mp["scale"].get("tactile", 0.3))
        return M

    # -------------------------------------------------------------------
    # 대계단 — 40단을 참 3개로 4구간 분할. width_pairs 로 참 전후 연속 폭 점증.
    # -------------------------------------------------------------------
    def build_stairs(stair_mtl):
        st = PARAMS["stairs"]
        n = st["nsteps"]
        wt, wb = st["w_top"], st["w_bot"]
        landings = list(PARAMS["landings"])
        # 구간 경계(전역 단 인덱스): [0,10,20,30,40] → 4구간 각 10단
        bounds = [0] + landings + [n]
        x_cur = st["x0"]
        z_cur = st["z_top"]
        for si in range(len(bounds) - 1):
            i0, i1 = bounds[si], bounds[si + 1]     # 전역 단 [i0+1 .. i1]
            wp = []
            for gi in range(i0 + 1, i1 + 1):
                hw = _half_width(gi, n, wt, wb)
                wp.append((-hw, hw))
            sc.build_straight_stairs(
                stage, f"{ROOT}/Stairs_{si}", x_cur, -wt, wt,
                st["riser"], st["tread"], i1 - i0, st["base_z"], stair_mtl,
                z_top=z_cur, collider=True, width_pairs=wp)
            x_cur += (i1 - i0) * st["tread"]
            z_cur -= (i1 - i0) * st["riser"]
            # 참 삽입 (마지막 구간 뒤엔 없음)
            if si < len(bounds) - 2:
                hw = _half_width(i1, n, wt, wb)      # 참 폭 = 그 지점 단 폭
                xa, xb = x_cur, x_cur + st["landing_depth"]
                BOX(f"{ROOT}/Landing_{si}",
                    ((xa + xb) / 2.0, 0.0, (z_cur + st["base_z"]) / 2.0),
                    (xb - xa, 2 * hw, z_cur - st["base_z"]), stair_mtl, col=True)
                x_cur = xb

    def _profile():
        """계단 프로파일: 구간별 (kind, x_a, x_b, 대표 z, 전역 단 인덱스) 나열.
        kind='step' 이면 z 는 그 단의 디딤면, 'land' 면 참 상면. build_stairs 와
        동일한 누적식을 쓰므로 계단 본체와 정확히 같은 좌표를 재현한다."""
        st = PARAMS["stairs"]
        n = st["nsteps"]
        bounds = [0] + list(PARAMS["landings"]) + [n]
        rows = []
        x_cur, z_cur = st["x0"], st["z_top"]
        for si in range(len(bounds) - 1):
            i0, i1 = bounds[si], bounds[si + 1]
            for gi in range(i0 + 1, i1 + 1):
                xa = x_cur + (gi - i0 - 1) * st["tread"]
                z = z_cur - (gi - i0) * st["riser"]
                rows.append(("step", xa, xa + st["tread"], z, gi))
            x_cur += (i1 - i0) * st["tread"]
            z_cur -= (i1 - i0) * st["riser"]
            if si < len(bounds) - 2:
                rows.append(("land", x_cur, x_cur + st["landing_depth"],
                             z_cur, i1))
                x_cur += st["landing_depth"]
        return rows

    def build_shoulder(M):
        """계단 밖 **어깨면 매시프** — 구 `build_soffit`(단일 경사 슬래브) 대체.

        [감사 A-14-1/2/3 치명] 구 소핏 상면은 z = −0.3 − 0.2885x 인 **단일 평면**
        이었다. 1구간 계단선(z = −0.441x)과 x = 1.967 에서 교차 → x>1.967 부터
        소핏이 계단보다 높아져 1구간 마지막 4~5단이 매몰(+0.219 @x=3.4), 2구간도
        x>8.905 에서 1단 매몰. 반대로 참 끝(x=5.8/11.6/17.4)에서는 계단보다
        0.47/0.65/0.82 m 낮아 계단 폭 밖(|y| hw..5.2)에 전 길이 세로 도랑이 생겼다.
        (감사 D5 는 '구간별 4장 분할'을 권고했으나, 경사 슬래브는 rotateY 절단면
         때문에 구간 이음부에 측면이 열린 쐐기 공동이 남는다 → 아래 방식 채택.)

        신 구조: **단(段)별 축정렬 박스 2장**(±Y 측대)을 계단과 동일한 x 구간에
        깔고 상면을 그 단의 디딤면 −offset(0.03) 에 맞춘다. 참 구간도 동일.
          · 계단 모서리 → 어깨면 단차 = 전 구간 균일 0.03 m (구 0.13~0.82 m 도랑)
          · 계단 매몰 0 (어깨면이 계단보다 높아지는 지점이 원리적으로 없음)
          · 수직 박스만 쓰므로 절단 쐐기 공동이 발생하지 않음
          · 상부 테라스(z 0)에서 어깨면 1단(−0.18)으로의 첫 단차 0.18 < 0.2 기준
        계단·참(위험 기하) 트랜스폼은 **불변** — 착시(terrace_read)는 보존."""
        st = PARAMS["stairs"]
        sh = PARAMS["shoulder"]
        n, yb = st["nsteps"], sh["y_out"]
        off, lap = sh["offset"], sh["lap"]
        for k, (kind, xa, xb, z, gi) in enumerate(_profile()):
            hw = _half_width(gi, n, st["w_top"], st["w_bot"])
            y_in = max(hw - lap, 0.0)              # 계단 밑으로 lap 만큼 물림
            top = z - off
            for tag, y0, y1 in (("N", y_in, yb), ("S", -yb, -y_in)):
                BOX(f"{ROOT}/Shoulder_{kind}{k}_{tag}",
                    ((xa + xb) / 2.0, (y0 + y1) / 2.0,
                     (top + st["base_z"]) / 2.0),
                    (xb - xa, y1 - y0, top - st["base_z"]),
                    M["marble"], col=True)

    def build_side_slopes(M):
        """계단 좌우 경사 잔디 사면 (감독 D-14 r3②): 어깨면 바깥(y±5.2)에서 부지
        가장자리(y±20)까지, 상부 광장(z0)→하부 광장(-6.0) 경사. 계단 고립 제거.
        thick 3.0 솔리드 + run_ext 로 하단 절단면을 하부 광장 밑으로 숨긴다."""
        st = PARAMS["stairs"]
        ss = PARAMS["side_slope"]
        total_x = st["nsteps"] * st["tread"] \
            + len(PARAMS["landings"]) * st["landing_depth"]
        drop = st["nsteps"] * st["riser"]
        run = total_x + ss["run_ext"]
        drop_ext = drop * run / total_x           # 기울기 유지한 채 하단 연장
        yb = PARAMS["shoulder"]["y_out"]          # 5.2 (어깨면/파라펫 바깥)
        for tag, y0, y1 in (("N", yb, ss["y_out"]), ("S", -ss["y_out"], -yb)):
            sc.build_slope(stage, f"{ROOT}/SideSlope_{tag}", st["x0"], -0.05,
                           run, drop_ext, y0, y1, ss["thick"], M["grass"],
                           margin=0.0, collider=True)

    def build_flat_fill(stair_mtl):
        """hazard_stairs=False 대조군: 계단 풋프린트를 z=0 평지로 통일."""
        st = PARAMS["stairs"]
        x1 = st["x0"] + st["nsteps"] * st["tread"] \
            + len(PARAMS["landings"]) * st["landing_depth"]
        BOX(f"{ROOT}/FlatStairs",
            ((st["x0"] + x1) / 2.0, 0.0, st["z_top"] - 0.25),
            (x1 - st["x0"], 2 * st["w_bot"], 0.5), stair_mtl, col=True)

    # -------------------------------------------------------------------
    # 상부 전망 소광장 (화강암) + 하부 대광장 (plaza_lower + 밴드)
    # -------------------------------------------------------------------
    def build_plazas(M):
        up = PARAMS["upper"]
        ub = PARAMS["upper_big"]
        lo = PARAMS["lower"]
        z_bot = lo["z_top"] - 0.3                   # 기단 바닥 (하부 광장보다 살짝 아래)
        pl_bot = ub["z_top"] - ub["thick"]          # 상부 판 밑면 = 기단 상면 (-0.5)
        # ── 상부 레벨 전체 기단 매시프 (감독 D-14①②): 대형 상부 광장+테라스 풋프린트
        #    전체를 z_bot 까지 채우는 솔리드(marble 측벽) — 상부 레벨 부유 제거.
        BOX(f"{ROOT}/UpperPlinth",
            ((ub["x0"] + ub["x1"]) / 2.0, (ub["y0"] + ub["y1"]) / 2.0,
             (z_bot + pl_bot) / 2.0),
            (ub["x1"] - ub["x0"], ub["y1"] - ub["y0"], pl_bot - z_bot),
            M["marble"], col=True)
        # ── 대형 상부 광장 (plaza_light) — 테라스 구멍(x up.x0..0, y up.y0..y1)을
        #    비운 3박스 (테라스가 채움, 동일평면 겹침 없음).
        cz = ub["z_top"] - ub["thick"] / 2.0
        BOX(f"{ROOT}/UpperPlazaW",              # 서: x0..up.x0 전폭
            ((ub["x0"] + up["x0"]) / 2.0, (ub["y0"] + ub["y1"]) / 2.0, cz),
            (up["x0"] - ub["x0"], ub["y1"] - ub["y0"], ub["thick"]),
            M["plaza_light"], col=True)
        BOX(f"{ROOT}/UpperPlazaS",              # 남: up.x0..0, y0..up.y0
            ((up["x0"] + ub["x1"]) / 2.0, (ub["y0"] + up["y0"]) / 2.0, cz),
            (ub["x1"] - up["x0"], up["y0"] - ub["y0"], ub["thick"]),
            M["plaza_light"], col=True)
        BOX(f"{ROOT}/UpperPlazaN",              # 북: up.x0..0, up.y1..y1
            ((up["x0"] + ub["x1"]) / 2.0, (up["y1"] + ub["y1"]) / 2.0, cz),
            (ub["x1"] - up["x0"], ub["y1"] - up["y1"], ub["thick"]),
            M["plaza_light"], col=True)
        # ── 대리석 테라스(계단머리) — 구멍 채움
        BOX(f"{ROOT}/UpperPlaza",
            ((up["x0"] + up["x1"]) / 2.0, (up["y0"] + up["y1"]) / 2.0,
             up["z_top"] - up["thick"] / 2.0),
            (up["x1"] - up["x0"], up["y1"] - up["y0"], up["thick"]),
            M["marble"], col=True)
        # 하부 대광장
        st = PARAMS["stairs"]
        x0 = st["x0"] + st["nsteps"] * st["tread"] \
            + len(PARAMS["landings"]) * st["landing_depth"]
        BOX(f"{ROOT}/LowerPlaza",
            ((x0 + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0),
            (lo["x1"] - x0, lo["y1"] - lo["y0"], lo["thick"]),
            M["plaza_lower"], col=True)
        # 차콜 밴드 2줄 (계단 발치 대광장 경계 강조)
        for k, xb in enumerate((x0 + 1.0, x0 + 2.0)):
            BOX(f"{ROOT}/LowerBand_{k}",
                (xb, (lo["y0"] + lo["y1"]) / 2.0, lo["z_top"] - 0.02),
                (0.4, lo["y1"] - lo["y0"], 0.06), M["band"])

    # -------------------------------------------------------------------
    # 측면 경사 파라펫 (build_slope, 폭 0.5, 대리석) — 계단 양측
    # -------------------------------------------------------------------
    def _rake_segments():
        """[v5.1] 파라펫 상단 헌치의 **폴리라인** — 구간(사선) / 참(수평) 교대.
        반환: (kind, x_a, x_b, z_a, z_b). 사선의 끝 z 와 다음 참의 z 가 정확히
        같고, 참의 z 와 다음 사선의 시작 z 도 같으므로 **이음부 단차 0**.
        z 는 그 x 에서의 **노징선**(라이저 상단 앞모서리를 잇는 선)이다."""
        st = PARAMS["stairs"]
        n = st["nsteps"]
        bounds = [0] + list(PARAMS["landings"]) + [n]
        out = []
        x_cur, z_cur = st["x0"], st["z_top"]
        for si in range(len(bounds) - 1):
            nst = bounds[si + 1] - bounds[si]
            xa, za = x_cur, z_cur
            x_cur += nst * st["tread"]
            z_cur -= nst * st["riser"]
            out.append(("rake", xa, x_cur, za, z_cur))
            if si < len(bounds) - 2:
                xa = x_cur
                x_cur += st["landing_depth"]
                out.append(("land", xa, x_cur, z_cur, z_cur))
        return out

    def build_parapets(M):
        """측면 파라펫 — [v5.1 현실성] **계단식 난간벽 → 경사 상단 솔리드 헌치**.

        피드백: "계단 좋음. 양쪽 하얀 난간의 계단층(스텝 파라펫) 제거."
        구 구현은 어깨면 프로파일을 그대로 따라가 상면이 40단 + 참 3개의
        **계단 모양 실루엣**을 만들었다(대계단 양측에 흰 톱니 2줄). 실제
        기념계단의 측벽(헌치)은 단이 아니라 **구간별 직선 레이크 + 참에서만
        수평**인 폴리라인이다. 이를 두 층으로 재구성한다:

          ① 본체 — 단별 박스(구 구조 유지). 다만 상면을 어깨면과 **동일**
             (z − offset)하게 낮춰 실루엣에서 완전히 사라지게 한다.
             (어깨면 86박스는 유지 가능 — 어깨면 자체는 계단 밖 바닥이라
              상부 실루엣을 만들지 않는다.)
          ② 헌치 — 구간별 `sc.build_slope` 사선 슬래브 + 참 구간 수평 박스.
             상면 = 노징선 + rail_h(0.95). 이음부 z 연속 → **단차 0의 사선**.

        헌치가 본체 위에 항상 얹히는지(공극 0) 검산:
          · 사선 두께 cap_t=1.4 (수직 환산 1.4/cos(23.83°) = 1.530)
          · 노징선은 그 단의 디딤면보다 최대 riser(0.15) 위 → 헌치 밑면은
            최대 z_step + 0.15 + 0.95 − 1.530 = z_step − 0.430
          · 본체 상면 = z_step − offset = z_step − 0.03
          → 밑면이 본체 상면보다 항상 0.40 m 이상 **아래** → 전 구간 물림.
        유효 난간 높이(어깨면 대비) = 0.95 ~ 1.10 m — 방호 성능도 구보다 상승.
        계단·참(위험 기하) 트랜스폼은 불변.

        ── [v6 판정 §3-1] 이음부 쐐기 슬릿 봉합 ──────────────────────────
        v6 RT 가 `lower_lookup` 400 % 크롭에서 참 3곳(좌 x≈310/740/935, 우 대칭)
        마다 폭 3~6 px 의 어두운 삼각 슬릿을 관측했다. **원인은 판정이 추정한
        '확폭(3.0→5.0)에 따른 ±Y 조그'가 아니다** — 파라펫 밴드 y 는
        (w_bot+0.05, +width) 로 전 구간 상수라 Y 조그 자체가 없다.

        진짜 원인은 `sc.build_slope` 사선 슬래브의 **끝면이 사면에 수직**이라는
        것이다. 상면 길이 = hypot(run,drop) + margin 이므로 끝면은 상단 모서리가
        margin/2 만큼 내리막으로 튀어나오고, 두께 cap_t 를 따라 내려가면서
        **오르막으로 cap_t·sin(ang) 만큼 후퇴**한다. 즉 사선의 내리막 끝은
        높이 rail_h 에 가까운 삼각 쐐기로 얇아진다:
          ang = atan(0.15/0.34) = 23.830°, sin = 0.4042, cos = 0.9147
          끝면 하단 x = x_b + margin/2·cos − cap_t·sin
                      = x_b + 0.027 − 0.566 = x_b − 0.538
        참 헌치 박스는 x_b 부터 시작(수직 끝면)하므로 x ∈ [x_b−0.538, x_b] 구간의
        끝면 아래가 **비어 있다**(밑에는 본체 상면 ≈ z_step−0.03 뿐 → 최대 0.9 m
        높이의 삼각 공동). fixlog 의 "이음부 Δz = 0.0" 검산은 상면 z 만 본 것이라
        이 평면 방향 공백을 잡지 못했다.

        봉합(판정 수정안 ①) — 참 헌치 박스를 오르막으로 lap 만큼 연장한다:
          lap = cap_t·sin(ang) + 0.15 = 0.566 + 0.15 = 0.716 m  (> 0.538 필요분)
        연장부 상면은 참 높이(z_a + rail_h) 그대로이고, 같은 x 에서 사선 상면은
        z_a + rail_h + (x_a − x)·tan(ang) 로 **항상 더 높다** → 연장부는 사선
        슬래브 내부에 완전히 매몰되어 실루엣을 만들지 않는다. 매몰 조건도 성립:
          연장부 상면이 사선 밑면(상면 − 1.530)보다 위여야 하므로
          lap·tan(ang) = 0.716 × 0.4419 = 0.316 < 1.530  ✓
        연장부의 ±Y 면은 사선 슬래브의 ±Y 면과 정확히 동일 평면·동일 법선·동일
        재질이라 Z 파이팅이 있어도 음영 차가 0 이다.

        반대쪽(참 → 사선) 이음부는 사선의 오르막 끝이 참 박스 안으로
        cap_t·sin + margin/2·cos = 0.594 m 파고들므로 원래부터 공백이 없다.

        같은 결함이 폴리라인 양 끝에도 있어 함께 봉합한다:
          · 머리 끝(x=0, 상부 테라스) — v6 [잔여] "terrace_read 좌·우 하단 헌치
            끝단 백색 삼각 매스" 가 이 쐐기다. 엄지기둥(端柱) 박스로 대체.
          · 발치 끝(계단 최하단) — 수직 마구리 박스로 대체.
        둘 다 |y| ≥ 5.05 로 계단 폭(w_bot 5.0) 밖 → 위험 기하·착시 불변."""
        st = PARAMS["stairs"]
        pa = PARAMS["parapet"]
        sh = PARAMS["shoulder"]
        yb = st["w_bot"] + 0.05                     # 5.05 — 하부 최대폭 바로 바깥
        rail_h = pa["z0"] + 0.6                     # 0.95 m (노징선 위 유효 높이)
        bands = (("N", yb, yb + pa["width"]),
                 ("S", -yb - pa["width"], -yb))
        # [v6] 사선 슬래브 끝면(사면 수직) 후퇴량 + 여유 = 평면 오버랩 lap
        _ang = math.atan2(st["riser"], st["tread"])
        lap = pa["cap_t"] * math.sin(_ang) + 0.15   # 0.716 m
        # ① 본체 — 상면을 어깨면과 동일하게 (구: +rail_h → 계단 실루엣)
        for k, (kind, xa, xb, z, gi) in enumerate(_profile()):
            top = z - sh["offset"]
            for tag, y0, y1 in bands:
                BOX(f"{ROOT}/Parapet_{kind}{k}_{tag}",
                    ((xa + xb) / 2.0, (y0 + y1) / 2.0,
                     (top + st["base_z"]) / 2.0),
                    (xb - xa, y1 - y0, top - st["base_z"]),
                    M["parapet"], col=True)
        # ② 상단 헌치 — 사선(구간) + 수평(참), 이음부 단차 0 · 평면 오버랩 lap
        segs = _rake_segments()
        for j, (kind, xa, xb, za, zb) in enumerate(segs):
            for tag, y0, y1 in bands:
                if kind == "rake":
                    sc.build_slope(
                        stage, f"{ROOT}/ParapetHaunch_{j}_{tag}",
                        xa, za + rail_h, xb - xa, za - zb, y0, y1,
                        pa["cap_t"], M["parapet"], margin=0.06,
                        collider=True)
                else:
                    # [v6] 오르막으로 lap 연장 → 직전 사선 슬래브 끝면 아래의
                    #      삼각 공동을 채운다(연장부는 사선 내부에 매몰).
                    x_a2 = xa - lap
                    top = za + rail_h
                    BOX(f"{ROOT}/ParapetHaunch_{j}_{tag}",
                        ((x_a2 + xb) / 2.0, (y0 + y1) / 2.0,
                         (top + st["base_z"]) / 2.0),
                        (xb - x_a2, y1 - y0, top - st["base_z"]),
                        M["parapet"], col=True)
        # [v6] 폴리라인 양 끝 쐐기 봉합 — 머리 엄지기둥 + 발치 마구리
        x_head, z_head = segs[0][1], segs[0][3]          # (0.0, z_top)
        x_toe, z_toe = segs[-1][2], segs[-1][4]          # 최하단 노징 끝
        for tag, y0, y1 in bands:
            # 머리 엄지기둥 : 상부 테라스(z_top) 위 lap × width × rail_h 솔리드.
            #   상면이 사선 상단(z_head + rail_h)과 정확히 일치 → 연속 어깨.
            top_h = z_head + rail_h
            bot_h = st["z_top"] - 0.30                    # 테라스 슬래브에 매입
            BOX(f"{ROOT}/ParapetNewel_{tag}",
                ((x_head - lap / 2.0), (y0 + y1) / 2.0, (top_h + bot_h) / 2.0),
                (lap, y1 - y0, top_h - bot_h), M["parapet"], col=True)
            # 발치 마구리 : 최하단 사선 끝을 수직면으로 닫는다.
            top_t = z_toe + rail_h
            BOX(f"{ROOT}/ParapetEndCap_{tag}",
                ((x_toe - lap / 2.0), (y0 + y1) / 2.0,
                 (top_t + st["base_z"]) / 2.0),
                (lap, y1 - y0, top_t - st["base_z"]), M["parapet"], col=True)

    # -------------------------------------------------------------------
    # 드레싱 — 가로등 2 + 파라펫 연석(상부 광장 뒤) + 분수 힌트 + 원경 건물
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
        """맥락 드레싱 — 판독어 "기념광장". 전부 기존 빌더/프리미티브 조합.
        구 인벤토리는 40×40 하부 광장에 분수 1개뿐이어서 휑함 5/5 였다."""
        dr = PARAMS["dressing"]
        z_lo = PARAMS["lower"]["z_top"]                # -6.0 (하부 광장 상면)
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        # 가로등 3×2 (상부 광장) — xs 확장으로 광장 축선을 만든다
        sl = PARAMS["streetlight"]
        for jx, x in enumerate(sl["xs"]):
            for j, y in enumerate(sl["ys"]):
                base = f"{ROOT}/Streetlight_{jx}_{j}"
                CYL(f"{base}/Pole", (x, y, sl["pole_h"] / 2.0),
                    sl["pole_r"], sl["pole_h"], M["pole"], col=True)
                for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                    ax = x + sgn * sl["arm_len"] / 2.0
                    CYL(f"{base}/Arm_{tag}", (ax, y, sl["pole_h"] - 0.1),
                        sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                    hx = x + sgn * sl["arm_len"]
                    BOX(f"{base}/Head_{tag}", (hx, y, sl["pole_h"] - 0.15),
                        (sl["head"], sl["head"], 0.12), M["lamp"])
        # 상부 광장 뒤 파라펫 연석 — 중앙 개구 2*curb_gap 을 비운 2박스 [A-14-5]
        #   구 구조는 폭 0.5 × 높이 0.5 가 y −8..8 전폭을 막아 테라스 진입이
        #   0.5 m 턱 넘기였다.
        up = PARAMS["upper"]
        g = dr["curb_gap"]
        for tag, y0, y1 in (("S", up["y0"], -g), ("N", g, up["y1"])):
            BOX(f"{ROOT}/UpperCurb_{tag}",
                (up["x0"] + 0.25, (y0 + y1) / 2.0, 0.25),
                (0.5, y1 - y0, 0.5), M["parapet"], col=True)
        # 분수: 수반 2단 + 얕은 수면 + 노즐 (구 '간이 수영장' 완화) [B-14-4]
        fo = PARAMS["fountain"]
        CYL(f"{ROOT}/FountainRingO", (fo["cx"], fo["cy"], z_lo + fo["h"] / 2.0),
            fo["r_out"], fo["h"], M["parapet"], col=True)
        CYL(f"{ROOT}/FountainRingM",
            (fo["cx"], fo["cy"], z_lo + fo["h"] * 0.75),
            fo["r_in"] + 0.35, fo["h"] * 1.5, M["parapet"], col=True)
        CYL(f"{ROOT}/FountainWater",
            (fo["cx"], fo["cy"], z_lo + fo["h"] / 2.0 + 0.01),
            fo["r_in"], fo["h"] + 0.02, M["water"])
        for k in range(fo["nozzles"]):
            a = 2.0 * math.pi * k / fo["nozzles"]
            CYL(f"{ROOT}/FountainNozzle_{k}",
                (fo["cx"] + 1.4 * math.cos(a), fo["cy"] + 1.4 * math.sin(a),
                 z_lo + fo["h"] + fo["nozzle_h"] / 2.0),
                fo["nozzle_r"], fo["nozzle_h"], M["parapet"])
        # ── 하부 대광장: 가로수·화단·벤치·볼라드·깃대 ──
        for k, (cx, cy) in enumerate(dr["trees_low"]):
            sc.build_tree(stage, f"{ROOT}/TreeLow_{k}", cx, cy, z_lo, *tree_mtls)
        for k, (cx, cy) in enumerate(dr["planters_low"]):
            sc.build_planter(stage, f"{ROOT}/PlanterLow_{k}", cx, cy, z_lo,
                             M["parapet"], M["grass"], size=3.0)
        for k, (cx, cy) in enumerate(dr["benches_low"]):
            sc.build_bench(stage, f"{ROOT}/BenchLow_{k}", cx, cy, z_lo,
                           M["parapet"], yaw=90.0)
        for k, by in enumerate(dr["bollard_ys"]):      # [v5.1 §2] 규정 볼라드
            build_bollard_std(M, f"{ROOT}/BollardLow_{k}",
                              dr["bollard_x"], by, z_lo, k=k)
        for k, (cx, cy) in enumerate(dr["flags"]):
            CYL(f"{ROOT}/FlagPole_{k}", (cx, cy, z_lo + 4.5), 0.09, 9.0,
                M["rail"], col=True)
            BOX(f"{ROOT}/Flag_{k}", (cx + 0.02, cy + 0.6, z_lo + 8.2),
                (0.03, 1.2, 0.8), M["band"])
        # ── 상부 광장: 기념비 + 생울타리 테두리 + 가로수·벤치 ──
        mx, my = dr["monument"]
        BOX(f"{ROOT}/MonumentBase", (mx, my, 0.4), (3.0, 3.0, 0.8),
            M["marble"], col=True)
        BOX(f"{ROOT}/MonumentShaft", (mx, my, 3.8), (1.6, 1.6, 6.0),
            M["marble"], col=True)
        for tag, x0, y0, x1, y1 in dr["hedges"]:
            sc.build_hedge(stage, f"{ROOT}/Hedge_{tag}", x0, y0, x1, y1, 0.9)
        for k, (cx, cy) in enumerate(dr["trees_up"]):
            sc.build_tree(stage, f"{ROOT}/TreeUp_{k}", cx, cy, 0.0, *tree_mtls)
        for k, (cx, cy) in enumerate(dr["benches_up"]):
            sc.build_bench(stage, f"{ROOT}/BenchUp_{k}", cx, cy, 0.0,
                           M["parapet"], yaw=90.0)
        # 원경 건물 5동 (지평 폐쇄) — bd["base_z"]=-6.0 로 하부 광장에 접지 [B-14-1]
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["bldg"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # -------------------------------------------------------------------
    # 단서 (cue) — nosing / railing (기본 OFF)
    # -------------------------------------------------------------------
    def build_signs():
        """[v5 공통 레이어] 한글 사인(sc.build_sign). 좌표·카메라 검산은
        PARAMS['signs'] 주석. 위험 기하(계단·참) 트랜스폼 불변."""
        back = PBR(f"{ROOT}/Looks/SignBack", diffuse_color=(0.16, 0.17, 0.18),
                   metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = PBR(f"{ROOT}/Looks/Sign{tag}",
                        diff=sc.tex_path(key, "diff"), uv_mode=True,
                        roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, back_mtl=back)

    def build_cues(M):
        st = PARAMS["stairs"]
        # [v5 공통 레이어] 점자블록 — 예약만 돼 있던 경로를 실제 지오메트리로.
        #   상단 모서리(x=0) 앞 ahead(0.4) m, 계단 상부 폭(y ±w_top) 밴드.
        #   대리석 테라스 상면(z=0)에서 4 mm 돌출 — 계단 트랜스폼 불변.
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             -st["w_top"], st["w_top"], M["tactile"],
                             z=st["z_top"], proud=tc["proud"])
        if cfg["cue_nosing"]:
            # 참 무시한 근사 단코 띠 (연속 40단 기준 — 대표 표기)
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], -st["w_top"], st["w_top"],
                st["riser"], st["tread"], st["nsteps"], z_top=st["z_top"])
        if cfg["cue_railing"]:
            pa = PARAMS["parapet"]
            sh = PARAMS["shoulder"]
            run = st["nsteps"] * st["tread"] \
                + len(PARAMS["landings"]) * st["landing_depth"]
            drop = st["nsteps"] * st["riser"]
            segs = _rake_segments()
            rail_h = pa["z0"] + 0.6

            def para_ground(x):
                """[v5.1] 헌치 상면(= 노징선 + rail_h) — 레일 포스트 착지면.
                구 계단식 상면 대신 사선/수평 폴리라인을 그대로 보간한다."""
                for kind, xa, xb, za, zb in segs:
                    if x < xb:
                        t = 0.0 if xb <= xa else (max(x, xa) - xa) / (xb - xa)
                        return za + (zb - za) * t + rail_h
                return segs[-1][4] + rail_h

            for sgn in (1.0, -1.0):
                sc.build_railing_line(
                    stage, f"{ROOT}/Rail_{'N' if sgn > 0 else 'S'}",
                    sgn * (st["w_bot"] + 0.3), st["x0"] - 0.5, st["x0"],
                    run, drop, para_ground, M["rail"], rail_h=0.9)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["marble"]
    if not cfg["cue_material_break"]:
        # 재질 경계 제거: 광장도 대리석(코드 경로 — plazas 는 별도이므로 계단만 유지)
        stair_mtl = M["marble"]

    build_plazas(M)
    if cfg["hazard_stairs"]:
        build_shoulder(M)           # 계단 밖 어깨면 매시프 (구 소핏) — 계단보다 먼저
        build_side_slopes(M)        # 계단 좌우 경사 잔디 사면 (고립 제거)
        build_stairs(stair_mtl)
        build_parapets(M)
        build_cues(M)
    else:
        build_flat_fill(stair_mtl)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if cfg["cue_sign"]:
        build_signs()               # [v5 공통 레이어]

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene14_{ts}.png")
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
