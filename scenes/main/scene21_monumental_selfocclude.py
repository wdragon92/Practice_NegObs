# -*- coding: utf-8 -*-
"""
scene21_monumental_selfocclude.py — NegObs 인공씬 21호: 관공서 대계단 (Isaac Sim 4.5)

유형    : T2 기념비적 진입 대계단 (다단 자기폐색)
사양서  : Docs/multi_scene_brief_v3.md §D scene21_monumental_selfocclude + 감독 보충
공통    : scene_common.py (build_railing_line/build_nosing) · scene02 골격

위험 본질: 상부 테라스(관공서 파사드 앞)에서 진행하면 18단 대계단의 하부 12단이
           상단 단코 뒤로 접혀 소실된다(다단 자기폐색). 난간 하강선과 상단 1~2 단코
           만 잔존해 낙차 2.7 m가 은닉. 설비(난간·단코·점자)는 완비돼 있으나
           grazing 시야에선 무력하다.
목표     : 상부 테라스(대리석)+기둥 4주 파사드 힌트 + 18단 + 양측 석재 파라펫 +
           중앙 스테인리스 난간 2선 + 하부 대광장 + 깃대 2를 조립.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene21_monumental_selfocclude.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene21_monumental_selfocclude.py
스모크(부팅 전 기하 자기검증·조기종료):
    NEGOBS_SMOKE=1 python scene21_monumental_selfocclude.py

좌표계: Z-up, m, 진행축 +X(테라스→하강), 낙차 시작 x=0. 파사드는 -X(상부 뒤).

대리석(테라스·계단·기둥·파사드): scene_common.TEX `marble_light` 역할(실재질).
하부 대광장은 브리프대로 `plaza_light`.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 7키. 설비 완비 유형 → cue_railing/nosing/tactile 기본 True.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 계단을 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        True,    # 중앙 스테인리스 난간 2선 (y ±1.3)
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)    # 상단 진입 경고 점자띠
    "cue_material_break": True,    # 계단 대리석 vs 하부 광장 plaza_light+밴드
    "cue_sign":           True,    # [v5 공통 레이어] sign_info(광장 안내) 1매
    "cue_scene_dressing": True,    # 기둥 파사드·깃대·원경 건물
    "cue_nosing":         True,    # [신규] 전 단 단코 띠
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- 대계단 18단 (riser 0.15 → 낙차 2.7, tread 0.32 run 5.76, 폭 8 y ±4) ---
    stairs=dict(x0=0.0, riser=0.15, tread=0.32, nsteps=18,
                y0=-4.0, y1=4.0, z_top=0.0, base_z=-3.2),
    # --- 지반 (감사v4 B1: 지반 프림 자체가 없어 테라스·파라펫·건물이 전부
    #     부유하고 테라스 측면이 무한낙하였다). 상면 -2.75 = 하부 대광장
    #     상면(-2.70) 바로 아래 → 광장 둘레 단차 0.05 m 로 보행 연속.
    ground=dict(cx=14.0, cy=0.0, size_x=110.0, size_y=90.0, z_top=-2.75,
                thick=1.2),
    # --- 양측 석재 파라펫 (경사 박스, 폭 0.5, 상면=계단선 +0.85) ---
    #     [감사v4 B2] y 대역을 계단 폭 **안쪽**(±3.5..±4.0)으로 이동 + 두께
    #     0.5 → 1.6. 종전엔 계단 폭(±4) 밖 허공에 경사 대들보가 떠 있었다.
    #     두께 1.6 → 밑면이 상단(x=0)에서 z=-0.60 로 디딤면(-0.15) 아래 0.45 m
    #     매입, 하단(x=5.76)에서 -3.30 으로 계단 저면(-3.2) 아래 → 전 구간 접지.
    #     유효 계단 폭 8 → 7 m. 낙차·단 치수(위험 기하)는 불변.
    #     [v5 판정 반영·중대] 파라펫 외면이 계단 외측면과 **정확히 동일 평면**
    #     (y=±4.0)이라 oblique 200 % 크롭에서 백색/석재가 단 피치로 교대하는
    #     빗살(코플래너 Z파이팅)이 파라펫 하단 전 구간에 발생했다. out_off 로
    #     외면만 2 cm 돌출(y ±4.02)시켜 깊이 순서를 확정한다. 안쪽 경계
    #     (y ±3.5)·상면(+0.85)·두께(1.6)는 불변이므로 접지·유효 계단폭 검산
    #     (B2)은 그대로 성립한다.
    parapet=dict(width=0.5, over=0.85, thick=1.6, out_off=0.02),
    # --- 중앙 스테인리스 난간 2선 (y ±1.3) ---
    railing=dict(ys=(-1.3, 1.3), rail_h=0.9),
    # --- 상부 테라스 (대리석) : thick 0.5 → 3.7 로 석조 기단화(저면 -3.7,
    #     지반 -2.75 아래로 0.95 m 매입). 상면 z=0(위험 기하) 불변. ---
    #     [v5 판정 반영] x0 −12.0 → −15.2 : 아래 파사드 서측 이설에 맞춘 기단 확장.
    #     상면 z=0 · x1=0(위험 기하 경계)는 불변.
    terrace=dict(x0=-15.2, x1=0.0, y0=-9.0, y1=9.0, z_top=0.0, thick=3.7),
    # --- 파사드 힌트: 기둥 4주(r0.4 h7) + 인방 보 + 후면 파사드 벽(창 다크) ---
    #     [v5 판정 반영·중대] d10 프리셋 열 전체가 주랑 그림자로 흑색 크러시
    #     (전경 평균 RGB (23,26,28)). 원인은 열주가 아니라 그 뒤의 **전폭 8.5 m
    #     파사드 벽**이다: 정오 태양(elev 49.79°, 그림자 방위 25°)에서 높이 h 의
    #     그림자는 +X 로 0.766·h 뻗으므로 벽(x −10.9, h 8.5) 그림자가
    #     x −10.9..−4.39 를 통째로 덮었고, d10 eye(x −10)·d5 eye(x −5) 의
    #     전경이 전부 그 안에 들어간다.
    #     · 프리셋 원점 이동은 불가 — 그리드는 eye_x = −d 로 낙차 모서리(x=0)
    #       까지의 거리를 정의하므로 +4 시프트 시 d2 eye 가 x=+2(계단 솔리드
    #       내부)로 들어간다. 그래서 **그림자원 자체를 물리고 태양 방위를 튼다**.
    #     · col_x −10.0 → −13.2 / wall_x −11.2 → −14.4 (서측 3.2 m 이설)
    #     · SUN_AZ_OFFSET 171.5 → 206.5 (그림자 방위 25° → 60°)
    #     → 벽 그림자 도달 x = −14.1 + 0.845·8.5·cos60° = −10.51,
    #       열주 −13.2 + 0.845·7·cos60° = −10.24 로 둘 다 d10 프레임 하단
    #       (h0.3 기준 x=−9.42, h0.9 기준 −8.27)보다 뒤 → 전경 크러시 소멸.
    facade=dict(col_r=0.4, col_h=7.0, col_x=-13.2, col_ys=(-6.0, -2.0, 2.0, 6.0),
                lintel_h=0.8, wall_x=-14.4, wall_t=0.6, wall_h=8.5,
                win_w=1.4, win_h=2.6, win_ys=(-6.0, -2.0, 2.0, 6.0)),
    # --- 하부 대광장 (plaza_light + band_dark) ---
    lower=dict(x1=34.0, y0=-16.0, y1=16.0, z_top=-2.7, thick=0.5),
    # --- 깃대 2 (가는 원기둥 h8) ---
    flagpole=dict(r=0.08, h=8.0, xs=(-2.0,), ys=(-7.0, 7.0)),
    # --- 원경 건물 3동 (지평 폐쇄). base_z=-2.75 = 지반 상면 (미지정이면
    #     셸이 z=-1.0 까지만 내려와 통째로 부유 — 감사v4 B3) ---
    buildings=dict(
        B=dict(x0=36.0, x1=42.0, y0=-14.0, y1=14.0, h=14.0, floors=6,
               axis="x", facade_x=36.0, face_dir=-1.0, base_z=-2.75),
        C=dict(x0=20.0, x1=44.0, y0=18.0, y1=24.0, h=11.0, floors=4,
               axis="y", facade_y=18.0, face_dir=-1.0, base_z=-2.75),
        D=dict(x0=44.0, x1=52.0, y0=-20.0, y1=20.0, h=18.0, floors=6,
               axis="x", facade_x=44.0, face_dir=-1.0, base_z=-2.75),
    ),
    # --- 맥락 드레싱 (cue_scene_dressing) : "기념공원·시청 앞 대계단" ---
    # [v5.1 현실성] 피드백: "위엄 — **중앙축 위 물체 제거**. 위엄은 대칭·비움에서
    #   나온다." 구 배치는 축선(y=0) 위에 ①기념 조형물(x 16, 샤프트 9 m)
    #   ②깃대 열의 중앙 2본(y ±1.8) ③볼라드 (7.5, 0.0) 이 겹겹이 서서
    #   프리셋(+X) 소실점을 통째로 막고 있었다. 셋 다 축선에서 치운다.
    #   ① 기념비 → 축선 밖 측면 (24.0, −12.0) 이설 + 샤프트 9.0 → 6.5 축소.
    #      (하부 광장 x1 34 · y ±16 안. 벤치(20,−12) 에서 4.00 m,
    #       가로등(18,−13) 에서 6.08 m, 깃대 열(19,−10.5) 에서 5.22 m 이격)
    monument=dict(x=24.0, y=-12.0, base=3.0, base_h=0.9, shaft=0.9,
                  shaft_h=6.5),
    #   ② 깃대 → 축선을 가로지르는 1열 6본(y −9..9) → **측면 대칭 2열**.
    #      y = ±10.5 · x = 10.0 / 14.5 / 19.0 (좌우 3본씩). 축선 y=0 완전 비움.
    flagpoles_lower=dict(r=0.08, h=9.0, ys=(-10.5, 10.5),
                         xs=(10.0, 14.5, 19.0)),
    #   ③ 볼라드 → 계단 발치 축선 횡단열(x 7.5, y −7..7, 간격 3.5, y=0 포함)
    #      폐기. §2 규정 배치로 **하부 광장 북측 진입부**(서비스 도로 접점)
    #      1열: y 14.5 · x 8.0..17.0 간격 1.5 (7본) + 보행자 접근면(남측)
    #      전면 0.3 m 점형블록. 그리드 eye(x −2/−5/−10, y 0) 기준 방위
    #      37~55° 로 화각(±30°) 밖, oblique(−4,−9) 에서도 28 m 원경.
    bollards_lower=dict(y=14.5, xs=(8.0, 9.5, 11.0, 12.5, 14.0, 15.5, 17.0),
                        block=dict(x0=7.7, x1=17.3, y0=14.2, y1=14.5)),
    #   ④ 테라스 볼라드 4본 — §2 근거(차량 진입 지점) 없는 장식 배치라 삭제.
    benches_lower=[(20.0, -12.0, 90.0), (20.0, 12.0, -90.0),
                   (26.0, -6.0, 180.0), (26.0, 6.0, 180.0),
                   (12.0, -13.0, 0.0), (12.0, 13.0, 0.0)],
    streetlights=[(6.6, -5.2), (6.6, 5.2), (18.0, -13.0), (18.0, 13.0)],
    streetlight=dict(pole_h=5.5, pole_r=0.09, arm_len=0.9, arm_r=0.05,
                     head=0.28),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),
    tactile=dict(ahead=0.4, proud=0.004),
    # [v5 공통 레이어] 한글 사인 — (태그, TEX 키, cx, cy, base_z, yaw, w, h)
    #   Info(−3.2, −5.4): 상부 테라스(x −15.2..0, y ±9, z 0) 위 광장 안내판.
    #     계단 상단 모서리(x=0, 폭 y ±4) 최근접점 (0, −4) 까지 3.49 m,
    #     테라스 남단(y=−9) 에서 3.60 m — 위험 기하 이격 ≥0.5 m 충족.
    #     깃대(x −2.0, y −7.0) 에서 1.98 m, 테라스 볼라드(−1.0, −6.0) 에서 2.27 m.
    #   카메라 검산(그리드 gy=0, eye x −2/−5/−10, 화각 ±30°):
    #     −2 → 후방 · −5 → −71.6° 밖 · −10 → −38.5° 밖
    #     crown_graze(−3,0) 후방 · railing_line(−2,1.3) 후방 ·
    #     oblique(−4,−9) 32.5° 밖 · facade_front(9,0) 23.9°(13.3 m 원경)
    #     → 자기폐색 판정 영역(계단 상단·난간선) 차폐 0.
    signs=[("Info", "sign_info", -3.2, -5.4, 0.0, 180.0, 1.0, 0.75)],

    material=dict(
        scale=dict(marble_light=1.2, plaza_light=1.80, granite_dark=1.0,
                   band_dark=0.5, brick_red=2.0, tactile=0.3, grass=1.4),
        grass_tint=(0.55, 0.68, 0.42),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        window_color=(0.05, 0.07, 0.10), window_rough=0.10,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        # [v5.1 §4] 파라펫 0.90 → 0.72 (순백 대면적 금지)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        pole_color=(0.80, 0.82, 0.85), pole_metallic=0.9, pole_rough=0.30,
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
    # [v5 판정 반영] 171.5 → 206.5. 그림자 수평 방위 = atan2(cosφ, −sinφ),
    #   φ = SUN_AZ_OFFSET + 123.5 (= noon_dome_rot −110 + hdri_sun_rotz_offset
    #   233.5). 구값 φ=295° → 그림자 방위 25°(거의 +X, 파사드 그림자가 테라스를
    #   전개), 신값 φ=330° → 60° 로 틀어 그림자 x 성분을 절반으로 줄인다.
    #   돔·DistantLight 가 같은 rot 로 함께 돌아 HDRI 태양 정합은 유지된다.
    #   −X 향 원경 건물(B·D) 조도는 cos 성분 0.585 → 0.323 으로 낮아지지만
    #   실루엣·접지 판독에는 영향이 없고, −Y 향 건물 C 와 남측 파라펫은 밝아진다.
    SUN_AZ_OFFSET=206.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene21")
ASSET_ROLES = ["marble_light", "plaza_light", "granite_dark", "band_dark",
               "brick_red", "tactile", "grass",
               "sign_info", "hdri", "mdl"]              # [v5] sign_info


# ===========================================================================
# [C2] 스모크 — 부팅 전 기하 자기검증 (조기종료)
# ===========================================================================
def _smoke_report():
    st = PARAMS["stairs"]
    print("=" * 64)
    print("scene21_monumental_selfocclude — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 64)
    n = st["nsteps"]
    drop = n * st["riser"]
    run = n * st["tread"]
    print(f"  대계단: {n}단 × riser {st['riser']} = 낙차 {drop:.2f} m, "
          f"run {run:.2f} m, 폭 {st['y1']-st['y0']:.1f}")
    # 자기폐색 근사: 상단 단코에서 시선 아래로 접히는 하부 단 수(개념 표기)
    print(f"  자기폐색 특색: 상부 테라스 grazing 시 하부 ~12단 소실, "
          f"상단 1~2 단코+난간 하강선 잔존")
    print(f"  파사드: 기둥 {len(PARAMS['facade']['col_ys'])}주 "
          f"(r{PARAMS['facade']['col_r']} h{PARAMS['facade']['col_h']}) + 인방 + 창 다크")
    print(f"  중앙 난간 2선 y={PARAMS['railing']['ys']}, "
          f"파라펫 폭 {PARAMS['parapet']['width']} 상면+{PARAMS['parapet']['over']}")
    print(f"  낙차 검증: {drop:.2f} ≥ 0.3 m → {'OK' if drop >= 0.3 else 'FAIL'}")
    # ── 지반·기단 z 위계 (감사v4 T1/T2/B2 수정 검산) ──
    gr = PARAMS["ground"]
    te = PARAMS["terrace"]
    lo = PARAMS["lower"]
    pa = PARAMS["parapet"]
    ang = math.atan2(drop, run)
    pz0 = st["z_top"] + pa["over"]                    # 파라펫 상면(x=0)
    pb0 = pz0 - pa["thick"] * math.cos(ang)           # 파라펫 밑면(x=0)
    pb1 = pb0 - drop                                  # 파라펫 밑면(x=run)
    print("  [z 위계]  지반 상면 %.2f / 하부광장 상면 %.2f / 테라스 저면 %.2f"
          % (gr["z_top"], lo["z_top"], te["z_top"] - te["thick"]))
    print("    테라스 기단 매입: %.2f m (저면이 지반 상면 아래) → %s"
          % (gr["z_top"] - (te["z_top"] - te["thick"]),
             "OK" if te["z_top"] - te["thick"] < gr["z_top"] else "FAIL"))
    print("    광장 둘레 단차: %.2f m (지반↔하부광장) → %s"
          % (lo["z_top"] - gr["z_top"],
             "OK" if abs(lo["z_top"] - gr["z_top"]) <= 0.2 else "FAIL"))
    print("    파라펫 y대역 [%.2f,%.2f] (외면 +%.2f 돌출 — 계단 측면 Z파이팅 회피)"
          " ⊂ 계단 폭 [%.1f,%.1f] → %s"
          % (st["y1"] - pa["width"], st["y1"] + pa.get("out_off", 0.0),
             pa.get("out_off", 0.0), st["y0"], st["y1"],
             "OK" if pa["width"] <= (st["y1"] - st["y0"]) / 2.0 else "FAIL"))
    print("    파라펫 밑면 x=0: %.2f (1단 디딤면 %.2f 아래) / x=run: %.2f "
          "(계단 저면 %.2f 아래) → %s"
          % (pb0, -st["riser"], pb1, st["base_z"],
             "OK" if (pb0 < -st["riser"] and pb1 < st["base_z"]) else "FAIL"))
    print("=" * 64)


# ===========================================================================
# [D] 카메라 프리셋 — 중앙 난간 2선 → gy=0 유지(대칭)
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)
    # crown_graze: 테라스에서 진행 — 하부 12단 자기폐색, 단코·난간만 잔존
    views["crown_graze"] = dict(eye=[-3.0, 0.0, 0.9], tgt=[7.0, 0.0, -0.4])
    # facade_front: 하부 광장에서 파사드·기둥 올려봄 (계단 실체 확인)
    views["facade_front"] = dict(eye=[9.0, 0.0, -2.0], tgt=[-9.0, 0.0, 3.0])
    # oblique: 사선 부감
    views["oblique"] = dict(eye=[-4.0, -9.0, 3.5], tgt=[5.0, 0.0, -2.0])
    # railing_line: 난간선 따라 하강 폭로
    views["railing_line"] = dict(eye=[-2.0, 1.3, 1.5], tgt=[6.0, 1.3, -1.5])
    return views


# ===========================================================================
# [E] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. crown_graze / h0.3 — 하부 12단 자기폐색, 상단 단코·난간 하강선만 잔존하는가
 2. facade_front       — 하부에서 기둥 4주·인방·창 다크(관공서 힌트) 식별
 3. railing_line       — 중앙 스테인리스 난간 2선 하강선
 4. oblique            — 18단·양측 파라펫 실체
 5. 재질/단서          — 대리석·단코·점자·밴드·Z파이팅·부유 없는가
 6. [v4] 지반·테라스 기단·파라펫 계단 위 안착·축선 조형물/깃대 열
 7. [v5] 공통 레이어 — 상단 점자띠 + sign_info(−3.2, −5.4) 판독"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene21")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene21"

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
        M["plaza"] = PBR(
            f"{ROOT}/Looks/Plaza", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["granite"] = PBR(
            f"{ROOT}/Looks/Granite", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"),
            sc.tex_path("granite_dark", "rough"), sca["granite_dark"])
        M["band"] = PBR(
            f"{ROOT}/Looks/Band", sc.tex_path("band_dark", "diff"),
            sc.tex_path("band_dark", "nor"), sc.tex_path("band_dark", "rough"),
            sca["band_dark"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        M["window"] = PBR(f"{ROOT}/Looks/Window",
                          diffuse_color=mp["window_color"],
                          roughness_const=mp["window_rough"], metallic=0.0)
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
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        return M

    # -------------------------------------------------------------------
    # 상부 테라스 + 하부 대광장
    # -------------------------------------------------------------------
    def build_plazas(M):
        # [감사v4 T1] 지반 — 이 1박스가 A3(테라스 측면 무한낙하)·A4(하부 광장
        # 자유단 아래 공동)·B1·B4를 동시에 해소한다. 상면 -2.75 (하부 광장
        # -2.70 보다 0.05 낮음 → 광장은 0.05 proud, 보행 단차 무시 가능).
        gr = PARAMS["ground"]
        BOX(f"{ROOT}/Ground",
            (gr["cx"], gr["cy"], gr["z_top"] - gr["thick"] / 2.0),
            (gr["size_x"], gr["size_y"], gr["thick"]), M["grass"], col=True)
        te = PARAMS["terrace"]
        BOX(f"{ROOT}/Terrace",
            ((te["x0"] + te["x1"]) / 2.0, (te["y0"] + te["y1"]) / 2.0,
             te["z_top"] - te["thick"] / 2.0),
            (te["x1"] - te["x0"], te["y1"] - te["y0"], te["thick"]),
            M["marble"], col=True)
        lo = PARAMS["lower"]
        st = PARAMS["stairs"]
        x0 = st["x0"] + st["nsteps"] * st["tread"]
        BOX(f"{ROOT}/LowerPlaza",
            ((x0 + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0),
            (lo["x1"] - x0, lo["y1"] - lo["y0"], lo["thick"]),
            M["plaza"] if cfg["cue_material_break"] else M["marble"], col=True)
        for k, xb in enumerate((x0 + 1.0, x0 + 2.0)):
            BOX(f"{ROOT}/LowerBand_{k}",
                (xb, (lo["y0"] + lo["y1"]) / 2.0, lo["z_top"] - 0.02),
                (0.4, lo["y1"] - lo["y0"], 0.06), M["band"])

    # -------------------------------------------------------------------
    # 대계단 18단 (대리석)
    # -------------------------------------------------------------------
    def build_stairs(M):
        st = PARAMS["stairs"]
        stair_mtl = M["marble"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)

    def build_flat_fill(M):
        st = PARAMS["stairs"]
        x1 = st["x0"] + st["nsteps"] * st["tread"]
        BOX(f"{ROOT}/FlatStairs",
            ((st["x0"] + x1) / 2.0, 0.0, st["z_top"] - 0.25),
            (x1 - st["x0"], st["y1"] - st["y0"], 0.5), M["marble"], col=True)

    # -------------------------------------------------------------------
    # 양측 석재 파라펫 (경사 박스, 상면=계단선 +0.85)
    # -------------------------------------------------------------------
    def build_parapets(M):
        st = PARAMS["stairs"]
        pa = PARAMS["parapet"]
        run = st["nsteps"] * st["tread"]
        drop = st["nsteps"] * st["riser"]
        z0 = st["z_top"] + pa["over"]
        # [감사v4 B2] 계단 폭 **안쪽** 0.5 m 대역에 얹는다(종전: 폭 밖 허공).
        # [v5 판정 반영] 외면만 out_off(2 cm) 바깥으로 — 계단 외측면(y=±4.0)과의
        #   동일 평면 Z파이팅(빗살 무늬) 해소. 내측 경계는 ±3.5 그대로.
        off = pa.get("out_off", 0.0)
        for tag, y0, y1 in (("N", st["y1"] - pa["width"], st["y1"] + off),
                            ("S", st["y0"] - off, st["y0"] + pa["width"])):
            sc.build_slope(stage, f"{ROOT}/Parapet_{tag}", st["x0"], z0,
                           run, drop, y0, y1, pa["thick"], M["parapet"],
                           collider=True)

    # -------------------------------------------------------------------
    # 파사드 힌트 — 기둥 4주 + 인방 보 + 후면 벽(창 다크)
    # -------------------------------------------------------------------
    def build_facade(M):
        fa = PARAMS["facade"]
        # 후면 파사드 벽
        BOX(f"{ROOT}/FacadeWall",
            (fa["wall_x"], 0.0, fa["wall_h"] / 2.0),
            (fa["wall_t"], PARAMS["terrace"]["y1"] - PARAMS["terrace"]["y0"],
             fa["wall_h"]), M["marble"], col=True)
        # 창 다크 (벽 앞면 살짝 돌출)
        gx = fa["wall_x"] + fa["wall_t"] / 2.0 + 0.02
        for j, y in enumerate(fa["win_ys"]):
            BOX(f"{ROOT}/FacadeWin_{j}", (gx, y, 4.0),
                (0.05, fa["win_w"], fa["win_h"]), M["window"])
        # 기둥 4주
        for j, y in enumerate(fa["col_ys"]):
            CYL(f"{ROOT}/Column_{j}", (fa["col_x"], y, fa["col_h"] / 2.0),
                fa["col_r"], fa["col_h"], M["marble"], col=True)
        # 인방 보 (기둥 상단 가로보)
        BOX(f"{ROOT}/Lintel",
            (fa["col_x"], 0.0, fa["col_h"] + fa["lintel_h"] / 2.0),
            (fa["col_r"] * 2.5,
             PARAMS["terrace"]["y1"] - PARAMS["terrace"]["y0"] - 2.0,
             fa["lintel_h"]), M["marble"], col=True)

    # -------------------------------------------------------------------
    # 드레싱 — 깃대 2 + 원경 건물 2동
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
        fp = PARAMS["flagpole"]
        x = fp["xs"][0]
        for j, y in enumerate(fp["ys"]):
            CYL(f"{ROOT}/Flagpole_{j}", (x, y, fp["h"] / 2.0),
                fp["r"], fp["h"], M["pole"], col=True)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        lz = PARAMS["lower"]["z_top"]                 # -2.70 (하부 광장 상면)
        # [v5.1] 기념 조형물 — 축선 밖 측면(24, −12). 축선(y=0)은 비운다.
        mo = PARAMS["monument"]
        BOX(f"{ROOT}/Monument_Base",
            (mo["x"], mo["y"], lz + mo["base_h"] / 2.0),
            (mo["base"], mo["base"], mo["base_h"]), M["marble"], col=True)
        BOX(f"{ROOT}/Monument_Shaft",
            (mo["x"], mo["y"], lz + mo["base_h"] + mo["shaft_h"] / 2.0),
            (mo["shaft"], mo["shaft"], mo["shaft_h"]), M["marble"], col=True)
        # [v5.1] 깃대 6본 — 축선 횡단 1열 → **측면 대칭 2열**(y ±10.5 × x 3본)
        fl = PARAMS["flagpoles_lower"]
        for j, y in enumerate(fl["ys"]):
            for i, x in enumerate(fl["xs"]):
                CYL(f"{ROOT}/FlagpoleLow_{j}_{i}", (x, y, lz + fl["h"] / 2.0),
                    fl["r"], fl["h"], M["pole"], col=True)
        # [v5.1 §2] 하부 광장 북측 진입부 규정 볼라드 1열 + 점형블록 0.3 m
        bl = PARAMS["bollards_lower"]
        for j, bx in enumerate(bl["xs"]):
            build_bollard_std(M, f"{ROOT}/BollardLow_{j}", bx, bl["y"], lz,
                              k=j)
        if cfg["cue_tactile"]:
            bk = bl["block"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Bollard",
                             bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                             M["tactile"], z=lz,
                             proud=PARAMS["tactile"]["proud"])
        # [v5.1] 테라스 볼라드 4본 삭제 (§2 근거 없는 장식 배치)
        for j, (bx, by, yaw) in enumerate(PARAMS["benches_lower"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{j}", bx, by, lz,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for j, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{j}"
            CYL(f"{base}/Pole", (lx, ly, lz + sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["pole"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (lx + sgn * sl["arm_len"] / 2.0, ly,
                     lz + sl["pole_h"] - 0.1),
                    sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (lx + sgn * sl["arm_len"], ly, lz + sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])

    def build_signs():
        """[v5 공통 레이어] 한글 사인(sc.build_sign). 좌표·카메라 검산은
        PARAMS['signs'] 주석. 위험 기하(대계단) 트랜스폼 불변."""
        back = PBR(f"{ROOT}/Looks/SignBack", diffuse_color=(0.16, 0.17, 0.18),
                   metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = PBR(f"{ROOT}/Looks/Sign{tag}",
                        diff=sc.tex_path(key, "diff"), uv_mode=True,
                        roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, back_mtl=back)

    # -------------------------------------------------------------------
    # 단서 (cue) — 중앙 난간 2선 / 단코 / 상단 점자띠 (기본 True)
    # -------------------------------------------------------------------
    def build_cues(M):
        st = PARAMS["stairs"]
        run = st["nsteps"] * st["tread"]
        drop = st["nsteps"] * st["riser"]

        def stair_ground(x):
            if x <= st["x0"]:
                return 0.0
            if x >= st["x0"] + run:
                return -drop
            idx = min(int((x - st["x0"]) / st["tread"]), st["nsteps"] - 1)
            return -st["riser"] * (idx + 1)

        if cfg["cue_railing"]:
            for k, y in enumerate(PARAMS["railing"]["ys"]):
                sc.build_railing_line(
                    stage, f"{ROOT}/Rail_{k}", y, st["x0"] - 0.5, st["x0"],
                    run, drop, stair_ground, M["rail"],
                    rail_h=PARAMS["railing"]["rail_h"])
        if cfg["cue_nosing"]:
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"], z_top=st["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["tactile"],
                             z=0.0, proud=tc["proud"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_plazas(M)
    if cfg["hazard_stairs"]:
        build_stairs(M)
        build_parapets(M)
        build_cues(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_facade(M)
        build_dressing(M)
    if cfg.get("cue_sign"):
        build_signs()               # [v5 공통 레이어]

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["oblique"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene21_{ts}.png")
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
