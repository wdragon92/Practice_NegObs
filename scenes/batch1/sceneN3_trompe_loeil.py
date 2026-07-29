# -*- coding: utf-8 -*-
"""
sceneN3_trompe_loeil.py — NegObs 인공씬 23호: 바닥 그림 계단 (Isaac Sim 4.5)

유형    : N3 hard negative — 아나모픽 트롱프뢰유 · **GT = 전 픽셀 "낙차 없음"**
사양서  : Docs/nanobanana_batch1_geometry_map.md §A sceneN3_trompe_loeil
룩 레퍼 : look_refs/n3_trompe_loeil.jpg (보행자 몰 + 하강 계단 아나모픽 그림)
공통    : scene_common.py (add_box / 드레싱·조명 하네스) · scene14 착시 씬 선례

위험 본질(반례): 보행자 몰 한복판 포장면에 "하강 계단정"이 그려져 있다. 기하는
           전부 평면(두께 1 mm 페인트 박판) — 낙차는 **어디에도 없다**.
           T1 캠퍼스 계단(양성)과 최강 대조쌍.
판별 단서: ① 포장 줄눈이 그림 영역을 그대로 관통해 이어진다(실제 개구라면 끊긴다)
           ② 가짜 "암부"는 페인트라 roughness가 주변 포장과 같아 스펙큘러가 남는다
           ③ 실그림자 부재 — 반대로 **실제 가로등 기둥 그림자가 그림 위를 지나간다**
           ④ 설계 시점(1점)을 벗어나면 원근이 붕괴한다(off_axis 컷)

── 아나모픽 구성(핵심 수학) ─────────────────────────────────────────────
가상 객체 = **침하 계단정**: 근접 림 x=0(z=0) → 바닥 z=-Dp(길이 floor_len) →
n단이 +X로 상승 → 원격 림 z=0 (x=x_f). 설계 시점 E=(eye_x, 0, eye_h)에서
가상 표면의 각 점 P=(xv, yv, z)를 지면 z=0으로 투영:
      s(z) = eye_h / (eye_h - z)              (0 < s <= 1)
      Q_x  = eye_x + s * (xv - eye_x) ,  Q_y = s * yv
근접·원격 림은 z=0 → s=1 → 자기 자신으로 사상 ⇒ **그림 풋프린트 = 계단정 개구
[0, x_f] × [-W/2, W/2]** 가 정확히 채워진다(빈틈·중복 없음).
양 측벽(yv=±W/2)은 |Q_y| = s*W/2 밖 영역 = 사다리꼴 측벽 밴드로 투영된다.
밴드 순서(트레드/라이저/측벽)는 s와 xv가 함께 증가하므로 **단조** — 겹침 없음.
Q_x <= 0 으로 투영되는 밴드는 근접 림에 가려 보이지 않는 부분(그레이징 폐색)이므로
그리지 않는다: 낮은 시점(h 0.9)에서 계단정 하부가 안 보이는 물리를 그대로 반영.

기본값(eye (-2, 0.9) · n 13 · riser 0.15 · tread 0.30 · floor 2.4 · W 3.0):
      풋프린트 6.30 × 3.00 m (레퍼런스 ~3×6 m 정합) · 가시 단 10/13
      단당 원근 축소 계수 k ≈ 0.75~0.87 (사양서 k≈0.88 대역)
설계 시점은 grid_views preset_h0.9_d2 의 eye 와 동일 — 표준 프리셋에서 착시가
성립하고, d5/d10/h1.8 로 갈수록 붕괴한다(의도된 데이터 다양성).
사양 이탈: 사양서 설계 시점은 (x=-5, h=0.9) 였으나 **(x=-2, h=0.9)로 이동**했다.
근거 — 낮은 시점에서 계단정 하부는 근접 림에 가려(그레이징 폐색) 그릴 면이 없다.
같은 가상 계단으로 설계 시점만 바꿔 계산한 가시 단수·축소계수:
      eye_x  -2.0 → 10/13 단, k 0.750~0.867   ← 채택(사양 k≈0.88 정합)
      eye_x  -3.0 →  8/13 단, k 0.750~0.846
      eye_x  -5.0 →  6/13 단, k 0.483~0.818   (그림 내용 희박·k 이탈)
      eye_x -10.0 →  4/13 단, k 0.177~0.778
x=-5 를 유지하려면 riser/tread 를 비현실적으로 낮춰야(riser 5 cm급) 하므로,
"h0.9 표준 프리셋 중 하나"라는 성질은 지키면서 d2 로 옮기는 쪽을 택했다.
────────────────────────────────────────────────────────────────────────

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneN3_trompe_loeil.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneN3_trompe_loeil.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneN3_trompe_loeil.py
기하·드레싱 검산:       NEGOBS_GEOCHECK=1 python3 sceneN3_trompe_loeil.py (Isaac 불요)

좌표계: Z-up, m, 진행축 +X, 그림(가짜 낙차 에지) 시작 = x=0.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import batch1_common as bc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키.
#     낙차가 없는 씬이므로 hazard_stairs 키는 **특색 요소(그림) 토글**로 재정의.
# ===========================================================================
SCENE_CONFIG = {
    # False → 그림 제거, 순수 평지 몰(대조군). 기하 토글 유일 예외.
    "hazard_stairs":      True,
    "cue_railing":        False,  # 그림에는 난간이 없다 — 키만 예약
    "cue_tactile":        False,  # 미관행 — 키만 예약
    "cue_material_break": True,   # True → 그림 틴트가 포장과 뚜렷이 대비
                                  # False → 포장 톤에 근접(착시 약화 대조군)
    "cue_nosing":         True,   # 각 트레드 앞단 밝은 단코 선(그려진 단코)
    "cue_sign":           False,  # [선택] 미구현 — 키만 예약
    "cue_scene_dressing": True,   # 가로등(실그림자 단서)·화단·벤치·볼라드·건물
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- 가상 계단정(그림의 원본 객체) + 설계 시점 ---
    illusion=dict(eye_x=-2.0, eye_h=0.9,         # 설계 1시점 (= preset_h0.9_d2)
                  nsteps=13, riser=0.15, tread=0.30,
                  floor_len=2.4,                  # 첫 라이저 앞 바닥 길이
                  width=3.0,                      # 개구 폭(그림 풋프린트 폭)
                  x_rim=0.0),                     # 근접 림 = 그림 시작 x
    # --- 페인트 레이어 z 규약 (proud) ---
    #   페인트 0.001 < 블록 줄눈 0.0015 < 외곽선 0.002 < 포장 줄눈 0.003
    #   (전 층 0.5 mm 이상 이격 — 동일평면 Z-파이팅 없음)
    paint=dict(z=0.001, border_z=0.002, border_w=0.06,
               border=True, nosing_w=0.035),
    # --- 그림 내부 "석재 블록 줄눈" [v2 추가] : 레퍼런스의 블록 쌓기 재현 ---
    #   tread_frac : 디딤면·바닥의 블록 경계 (반폭 대비 비율, ±0 이 중앙)
    #   wall_frac  : 측벽 코스 줄눈 (내측 경계 0 → 외측 개구 경계 1 사이 비율)
    blocks=dict(enable=True, z=0.0015, w=0.020,
                tread_frac=(-0.42, 0.02, 0.46), wall_frac=(0.45,)),
    # --- 포장 ---
    plaza=dict(x0=-60.0, x1=100.0, y0=-60.0, y1=60.0, z_top=0.0, thick=0.6),
    band=dict(y=5.0, width=0.8, proud=0.002, embed=0.06),   # 화강암 경계 밴드
    joint=dict(x0=-12.0, x1=24.0, y0=-7.2, y1=7.2, step=1.2,
               width=0.028, proud=0.003, embed=0.06),        # 포장 줄눈 격자
    # --- 소품 ---
    #   가로등: 태양 az 205° → 그림자 az 25° = (+0.906,+0.423),
    #   길이 = 4.6/tan(49.79°) = 3.90 m → 그림자 끝 (4.13, -0.95) = 그림 내부.
    lamp=dict(cx=0.6, cy=-2.6, pole_r=0.07, pole_h=4.6,
              head=(0.55, 0.22, 0.14)),
    planters=[dict(name="A", cx=-4.5, cy=3.6), dict(name="B", cx=9.0, cy=-3.8),
              dict(name="C", cx=14.0, cy=3.4), dict(name="D", cx=18.5, cy=-3.6)],
    planter=dict(size=2.6, curb_h=0.42, curb_t=0.22, cap_over=0.05,
                 cap_h=0.05, grass_h=0.38),
    # 벤치 — 전부 화단(수목) 앵커 인접. A 는 ctx2 에서 허허벌판(-3.0,-3.4)
    #   → 화단 A 우측 0.3 m 로 이설. yaw/위치는 v5.1 §3 결정적 지터.
    benches=[dict(name="A", cx=-2.0, cy=3.5, yaw=0.0),      # 화단 A 옆 0.3 m
             dict(name="B", cx=6.5, cy=-3.6, yaw=0.0),      # 화단 B 옆 0.3 m
             dict(name="C", cx=10.5, cy=3.6, yaw=0.0),      # 화단 C 앞 1.3 m
             dict(name="D", cx=16.0, cy=3.5, yaw=0.0)],     # 화단 C 옆 0.2 m
    # ── 볼라드 [v5.1 §2 · ctx2] ───────────────────────────────────────────
    #   구(舊): (−6, ±1.4) 2본 h0.75 — 보행축(그림 중심선) 바로 옆이라
    #   설계 시점 시야에 걸릴 수 있고 규격·간격·반사띠·점형블록 전무.
    #   신(新): **몰 보행자전용거리 진입부**(x=−6) 횡단 1열. 규격 h0.90·φ0.12·
    #   간격 1.5 m. 중앙 4.8 m 는 **소방차 진입 통로**(건축법상 소방활동
    #   전용구역 최소폭 4 m)로 비워 둔다 — 실제 보행자전용거리 관행.
    #   ★ 그림 보존: 볼라드는 전부 |y| ≥ 2.4 · x = −6 → 그림 풋프린트
    #     (x 0..6.30 · |y| ≤ 1.50) 및 설계 시점(E=−2.0) **전방 시야 밖**.
    #     (설계 시점보다 −X 후방이라 design_eye 컷에는 원천적으로 안 나온다.)
    bollard_rows=[dict(name="N", x=-6.0, y0=2.4, y1=8.4),
                  dict(name="S", x=-6.0, y0=-2.4, y1=-8.4)],
    bollard=dict(r=0.06, h=0.90, spacing=1.5, front=(-1.0, 0.0)),
    # ── 몰 맥락 [v2 추가] : 상점 파사드 밴드 (차양 + 쇼윈도 + 사인 밴드) ──
    #   양측 상가(buildings L/R) 1층에 포디엄 벽을 덧대고 그 전면에 베이를 배열.
    #   포디엄(y 9.55~10.05, z 0~3.6)은 build_building 의 1층 창(y 9.98~10.01,
    #   z 0.60~2.40)을 **완전히 내포**하므로 동일평면 Z-파이팅이 발생하지 않는다.
    #   podium_embed 0.05 = 포디엄을 셸 안쪽으로 물려 **동일평면 접촉 제거**.
    #   podium_h 3.45 < 2층 창 하단 3.60 → 창과 상면 접촉도 없음.
    shop=dict(x0=-10.0, x1=30.0, bay=4.0, gap=0.55,
              podium_t=0.50, podium_h=3.45, podium_embed=0.05,
              glass_z0=0.45, glass_z1=2.50, glass_t=0.10, glass_proud=0.05,
              awn_z=2.66, awn_proj=1.30, awn_t=0.12,
              fascia_z0=2.78, fascia_z1=3.36, fascia_t=0.18, fascia_proud=0.10),
    shop_facades=[dict(name="L", y=10.0, dir=-1.0),
                  dict(name="R", y=-10.0, dir=1.0)],
    # 입간판(안내 사인 1본) — 몰 이용 안내. -X 를 바라봄(접근 카메라 정면).
    #   GT 규약: '낙차 경고'가 아닌 **안내(info)** 사인만 사용(오라벨 금지).
    entry_sign=dict(x=7.5, y=4.6, yaw=180.0, w=0.8, h=0.8,
                    pole_h=2.2, pole_r=0.045),
    buildings=dict(
        # 몰 양측 상가 파사드 + 정면(+X) 비스타 차단
        L=dict(x0=-14.0, x1=34.0, y0=10.0, y1=20.0, h=9.0, floors=3,
               axis="y", facade_y=10.0, face_dir=-1.0),
        R=dict(x0=-14.0, x1=34.0, y0=-20.0, y1=-10.0, h=9.0, floors=3,
               axis="y", facade_y=-10.0, face_dir=1.0),
        F=dict(x0=42.0, x1=52.0, y0=-18.0, y1=18.0, h=14.0, floors=4,
               axis="x", facade_x=42.0, face_dir=-1.0),
    ),
    window=dict(w=1.4, h=1.8, inset=0.15, col_step=3.0, margin=2.0),

    material=dict(
        scale=dict(stone_flag=1.2, band_dark=1.0, grass=1.4, plaza_light=1.80),
        grass_tint=(0.55, 0.68, 0.42),
        # ══ 페인트 틴트 [v2 팔레트 교정 · 2026-07-27] ════════════════════
        #   폐기 사유: v1 은 채도 0에 가까운 무채색 회색(0.40/0.385/0.355 계열)
        #     이라 렌더가 "회색 줄무늬 추상 패턴"으로 읽혔다(사용자 지적).
        #   교정 근거: look_refs/n3_trompe_loeil.jpg 판독 —
        #     ① 디딤면은 **따뜻한 베이지·황갈 석재**(분필 파스텔의 웜톤)
        #     ② 라이저·바닥 암부도 중성 회색이 아니라 **웜브라운 그늘**
        #     ③ 측벽은 석재 블록 쌓기(웜 중간톤 + 암색 줄눈)
        #     ④ 그림 외곽은 크림빛 분필 테두리
        #   sRGB 지각 규약: 암부는 0.02~0.09 대역 유지하되 **색상은 남긴다**
        #     (R:G:B ≈ 1.00:0.79:0.59 웜 비율 — 채도 있는 암부).
        #   roughness 는 전 페인트가 paint_rough(포장과 동일) — "재질 함정" 유지.
        paint_rough=0.55,
        tread_tint=(0.520, 0.450, 0.340),      # 웜 스톤 디딤면(황갈 베이지)
        riser_tint_a=(0.055, 0.043, 0.032),    # 웜브라운 암부 2톤(교대)
        riser_tint_b=(0.088, 0.070, 0.053),
        floor_tint=(0.040, 0.031, 0.023),      # 계단정 바닥(최심부·웜 암부)
        wall_tint=(0.240, 0.200, 0.150),       # 석재 블록 측벽(웜 중간톤)
        nosing_tint=(0.640, 0.565, 0.440),     # 그려진 단코(밝은 웜 스톤)
        border_tint=(0.760, 0.710, 0.600),     # 그림 외곽 크림 분필 라인
        block_tint=(0.130, 0.104, 0.078),      # 석재 블록 줄눈(웜 암색 박선)
        # 대비 약화(cue_material_break=False) 시 섞는 포장 기준톤 — 웜으로 동조
        flat_ref=(0.340, 0.315, 0.275),
        flat_mix=0.55,
        joint_color=(0.030, 0.030, 0.032), joint_rough=0.7,
        lamp_color=(0.42, 0.43, 0.45), lamp_metallic=0.6, lamp_rough=0.45,
        bollard_color=(0.33, 0.33, 0.36), bollard_metallic=0.4,
        bollard_rough=0.5,
        # ─ 볼라드 v5.1 부속: 상단 백색 반사띠(본당 0.08 m² — 대면적 아님) +
        #   전면 점형블록(황색). 몸통은 몰 관행대로 암회 유지.
        bollard_band_color=(0.88, 0.88, 0.86),
        tactile_color=(0.80, 0.66, 0.14), tactile_rough=0.70,
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        parapet_color=(0.90, 0.90, 0.87), parapet_rough=0.6,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        wall_face_tint=(0.86, 0.86, 0.85),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # ── 몰 맥락(상점 파사드) ──
        podium_tint=(0.90, 0.87, 0.82),
        shopglass_color=(0.055, 0.070, 0.085), shopglass_rough=0.10,
        awning_a=(0.34, 0.10, 0.09), awning_b=(0.10, 0.22, 0.17),
        awning_rough=0.85,
        fascia_a=(0.20, 0.17, 0.14), fascia_b=(0.14, 0.16, 0.21),
        fascia_rough=0.60,
        sign_color=(0.30, 0.30, 0.32), sign_rough=0.50,
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
    # ─── SUN_AZ_OFFSET: 기본 171.5 유지. 근거:
    #     태양 월드 az ≈ 33.5 + 171.5 = 205° → 실그림자 az = 25°(+X,+Y).
    #     그림의 "가짜 음영"은 라이저가 카메라를 향하는 면(즉 -X 향)이 어둡다는
    #     전제라, 실제 태양(205°=서남서)이 만드는 음영 방향과 **상충한다**.
    #     이 상충은 결함이 아니라 트롱프뢰유 판별 단서 — 그림은 자기 그림자를
    #     못 만들고, 반대로 실제 가로등/화단 그림자는 그림 위를 그대로 지나간다.
    #     [ ]키(15° step)로 GUI에서 재스윕 가능. ───
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
# [C] 경로 상수 + 필요 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN3")

ASSET_ROLES = ["stone_flag", "band_dark", "plaza_light", "grass", "brick_red",
               "sign_info", "hdri", "mdl"]


# ===========================================================================
# [C2] 아나모픽 투영 — 순수 수학 (stage 불필요, SMOKE 리포트와 공용)
# ===========================================================================
def project_bands(il):
    """가상 침하 계단정의 가시 표면을 지면(z=0)에 투영한 밴드 목록.

    il: PARAMS["illusion"] 딕셔너리.
    반환: [dict(kind, idx, xa, xb, ha, hb, sa, sb, depth_frac), ...]
      kind : "floor" | "riser" | "tread"   (근→원 순, xa < xb 단조)
      xa,xb: 지면 투영 x (근/원)           ha,hb: 그 지점의 반폭 |Qy| 경계
      sa,sb: 투영 계수 s                   depth_frac: 0(최심)~1(림) 깊이 비
    Q_x<=0 으로 접히는(근접 림에 가린) 밴드는 제외하고, 걸친 밴드는 x=0에서
    선형 보간해 자른다 — riser/tread 모두 Q 에 대해 s(따라서 반폭)가 선형이다.
    """
    ex, h = float(il["eye_x"]), float(il["eye_h"])
    n = int(il["nsteps"])
    r, t = float(il["riser"]), float(il["tread"])
    Lf, W = float(il["floor_len"]), float(il["width"])
    x_rim = float(il["x_rim"])
    Dp = n * r                                   # 계단정 깊이
    hw = W / 2.0

    def s_of(z):
        return h / (h - z)

    def qx(xv, z):
        return ex + s_of(z) * (xv - ex)

    raw = []
    # ① 바닥판 (z=-Dp, x_rim .. x_rim+Lf)
    raw.append(("floor", 0, x_rim, x_rim + Lf, -Dp, -Dp))
    # ② 단 i: 라이저(수직면) → 트레드(수평면)
    for i in range(1, n + 1):
        xi = x_rim + Lf + (i - 1) * t
        zb = -Dp + (i - 1) * r
        zt = -Dp + i * r
        raw.append(("riser", i, xi, xi, zb, zt))
        raw.append(("tread", i, xi, xi + t, zt, zt))

    bands = []
    for kind, idx, xva, xvb, za, zb in raw:
        sa, sb = s_of(za), s_of(zb)
        xa, xb = qx(xva, za), qx(xvb, zb)
        ha, hb = sa * hw, sb * hw
        if xb <= x_rim + 1e-9:                   # 전부 폐색 — 그리지 않음
            continue
        if xa < x_rim:                           # 걸친 밴드 → x_rim 에서 절단
            u = (x_rim - xa) / (xb - xa)
            ha = ha + (hb - ha) * u
            sa = sa + (sb - sa) * u
            xa = x_rim
        bands.append(dict(kind=kind, idx=idx, xa=xa, xb=xb, ha=ha, hb=hb,
                          sa=sa, sb=sb,
                          depth_frac=(sa + sb) / 2.0))
    return bands


def illusion_summary(il):
    """SMOKE·문서용 요약: 풋프린트·가시 단수·단당 축소계수 k."""
    b = project_bands(il)
    x_f = float(il["x_rim"]) + float(il["floor_len"]) \
        + int(il["nsteps"]) * float(il["tread"])
    steps = sorted({d["idx"] for d in b if d["kind"] in ("riser", "tread")})
    dep = []
    for i in steps:
        seg = [d for d in b if d["idx"] == i and d["kind"] in ("riser", "tread")]
        dep.append((i, max(d["xb"] for d in seg) - min(d["xa"] for d in seg)))
    ks = [dep[j][1] / dep[j + 1][1] for j in range(len(dep) - 1)
          if dep[j + 1][1] > 1e-9]
    return dict(bands=b, x_f=x_f, steps=steps, depths=dep,
                k_min=(min(ks) if ks else 0.0), k_max=(max(ks) if ks else 0.0))


# ===========================================================================
# [C3] 로컬 빌더 — 그림 계단(공용화 보류: 이 씬 전용)
# ===========================================================================
def _paint_quad(stage, path, corners_xy, z, mtl):
    """지면과 평행한 평면 사각형(사다리꼴) 1매. corners_xy 는 +Z 에서 볼 때
    반시계(CCW) 순서 — 법선 +Z. 인접 밴드는 변을 공유할 뿐 겹치지 않으므로
    동일평면 Z-파이팅이 발생하지 않는다."""
    from pxr import UsdGeom, UsdShade, Gf
    mesh = UsdGeom.Mesh.Define(stage, path)
    pts = [Gf.Vec3f(float(x), float(y), float(z)) for x, y in corners_xy]
    mesh.CreatePointsAttr(pts)
    mesh.CreateFaceVertexCountsAttr([len(pts)])
    mesh.CreateFaceVertexIndicesAttr(list(range(len(pts))))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mesh.CreateExtentAttr([Gf.Vec3f(min(xs), min(ys), float(z)),
                           Gf.Vec3f(max(xs), max(ys), float(z))])
    # TfToken 값은 문자열로 직접 지정(토큰 상수명 의존 제거).
    mesh.CreateSubdivisionSchemeAttr("none")     # 폴리곤 그대로(세분 금지)
    mesh.CreateDoubleSidedAttr(True)             # 후면 컬링 사고 방지
    mesh.CreateNormalsAttr([Gf.Vec3f(0.0, 0.0, 1.0)] * len(pts))
    mesh.SetNormalsInterpolation("vertex")
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mtl)
    return mesh


def _block_joints(stage, prefix, tag, xa, xb, ha, hb, hw, bk, mtl, inner):
    """그림 내부 "석재 블록 줄눈" 박선 (레퍼런스의 블록 쌓기 재현).

    inner=True 면 디딤면·바닥의 블록 경계(반폭 대비 tread_frac 위치의 종방향
    박선), 항상 측벽 코스 줄눈(내측→개구경계 사이 wall_frac 위치)도 함께 깐다.
    선은 밴드와 같은 사다리꼴 원근을 따르므로(반폭이 ha→hb 로 변함) 투영이
    깨지지 않는다. z 는 페인트(0.001)보다 0.5 mm 위 = Z-파이팅 없음.
    """
    z = float(bk["z"])
    w = float(bk["w"]) / 2.0
    n = 0
    if inner:
        for k, f in enumerate(bk["tread_frac"]):
            ya, yb = f * ha, f * hb
            _paint_quad(stage, f"{prefix}/BlkT_{tag}_{k}",
                        [(xa, ya - w), (xb, yb - w), (xb, yb + w), (xa, ya + w)],
                        z, mtl)
            n += 1
    for k, t in enumerate(bk["wall_frac"]):
        for sgn, sd in ((1.0, "N"), (-1.0, "S")):
            ya = sgn * (ha + t * (hw - ha))
            yb = sgn * (hb + t * (hw - hb))
            _paint_quad(stage, f"{prefix}/BlkW{sd}_{tag}_{k}",
                        [(xa, ya - w), (xb, yb - w), (xb, yb + w), (xa, ya + w)],
                        z, mtl)
            n += 1
    return n


def paint_fake_stairs(stage, prefix, il, pa, mtl_of, nosing=True,
                      blocks=None, block_mtl=None):
    """아나모픽 "하강 계단" 페인트 배열을 지면 z=pa["z"] 에 깐다.

    il      : PARAMS["illusion"],  pa: PARAMS["paint"]
    mtl_of  : (kind, idx, depth_frac) -> UsdShade.Material 콜백
              kind ∈ {"floor","riser","tread","wall","nosing","border"}
    nosing  : True 면 각 트레드 앞단을 폭 pa["nosing_w"] 만큼 잘라 단코 색으로.
    blocks  : PARAMS["blocks"] (enable 시 석재 블록 줄눈 박선 추가), block_mtl 필요.
    밴드 = 내측 사다리꼴(바닥/라이저/트레드) + 좌우 측벽 사다리꼴 3매.
    전체 합집합 = 개구 풋프린트 [x_rim, x_f] × [-W/2, W/2] 를 빈틈없이 덮는다.
    """
    z = float(pa["z"])
    hw = float(il["width"]) / 2.0
    bands = project_bands(il)
    n_prim = 0
    use_blk = bool(blocks and blocks.get("enable") and block_mtl is not None)
    for bi, b in enumerate(bands):
        segs = [(b["xa"], b["xb"], b["ha"], b["hb"], b["kind"])]
        if nosing and b["kind"] == "tread":
            w = min(float(pa["nosing_w"]), (b["xb"] - b["xa"]) * 0.5)
            if w > 1e-4:
                xm = b["xa"] + w
                u = (xm - b["xa"]) / max(b["xb"] - b["xa"], 1e-9)
                hm = b["ha"] + (b["hb"] - b["ha"]) * u
                segs = [(b["xa"], xm, b["ha"], hm, "nosing"),
                        (xm, b["xb"], hm, b["hb"], "tread")]
        for si, (xa, xb, ha, hb, kind) in enumerate(segs):
            tag = f"{bi:02d}_{si}"
            mtl = mtl_of(kind, b["idx"], b["depth_frac"])
            # 내측(계단면)
            _paint_quad(stage, f"{prefix}/Band_{tag}",
                        [(xa, -ha), (xb, -hb), (xb, hb), (xa, ha)], z, mtl)
            n_prim += 1
            # 좌우 측벽 사다리꼴 (내측 경계 ~ 개구 경계)
            wmtl = mtl_of("wall", b["idx"], b["depth_frac"])
            _paint_quad(stage, f"{prefix}/WallS_{tag}",
                        [(xa, -hw), (xb, -hw), (xb, -hb), (xa, -ha)], z, wmtl)
            _paint_quad(stage, f"{prefix}/WallN_{tag}",
                        [(xa, ha), (xb, hb), (xb, hw), (xa, hw)], z, wmtl)
            n_prim += 2
            if use_blk:
                n_prim += _block_joints(
                    stage, prefix, tag, xa, xb, ha, hb, hw, blocks, block_mtl,
                    inner=(kind in ("tread", "nosing", "floor")))
    return bands, n_prim


# ===========================================================================
# [C4] 기하 자기검증 리포트 (SMOKE 조기종료에서 출력)
# ===========================================================================
def _geometry_report():
    il = PARAMS["illusion"]
    s = illusion_summary(il)
    pa = PARAMS["paint"]
    Dp = il["nsteps"] * il["riser"]
    D = il["x_rim"] - il["eye_x"]
    i0 = min(s["steps"]) if s["steps"] else 0
    z_seen = -Dp + (i0 - 1) * il["riser"]        # 최심 가시면 = 지각 낙차
    print("-" * 68)
    print("[기하] sceneN3 아나모픽 자기검증")
    print(f"  설계 시점 E=({il['eye_x']:.2f}, 0, {il['eye_h']:.2f})  "
          f"근접 림 x={il['x_rim']:.2f} → D={D:.2f} m")
    print(f"  그레이징 폐색: 림 시선 기울기 h/D = {il['eye_h'] / D:.3f} vs "
          f"계단 상승 기울기 riser/tread = {il['riser'] / il['tread']:.3f} "
          f"→ 첫 가시 단 {i0} (하부 {i0 - 1}단+바닥은 림에 가림)")
    print(f"  지각 낙차(림에서 최심 가시면) = {-z_seen:.2f} m · "
          f"유효성 = 가시 단 {len(s['steps'])} ≥ 3 → "
          f"{'OK' if len(s['steps']) >= 3 else 'FAIL(그릴 면 부족 — floor_len/riser 재조정)'}")
    print(f"  가상 계단정: {il['nsteps']}단 riser {il['riser']:.2f} / "
          f"tread {il['tread']:.2f} · 깊이 {Dp:.2f} · 바닥 {il['floor_len']:.2f} "
          f"· 폭 {il['width']:.2f}")
    print(f"  그림 풋프린트: x [{il['x_rim']:.2f}, {s['x_f']:.2f}] "
          f"({s['x_f'] - il['x_rim']:.2f} m) × 폭 {il['width']:.2f} m "
          f"— 페인트 proud {pa['z']:.4f} m (≤0.001 규약)")
    print(f"  가시 단: {len(s['steps'])}/{il['nsteps']} "
          f"(단 {min(s['steps'])}~{max(s['steps'])}, 하부는 근접 림에 폐색)")
    print(f"  단당 원근 축소 계수 k = {s['k_min']:.3f} ~ {s['k_max']:.3f} "
          f"(사양 k≈0.88 대역)")
    print(f"  {'밴드':>10s} {'x_near':>8s} {'x_far':>8s} {'깊이':>7s} "
          f"{'반폭_n':>7s} {'반폭_f':>7s}")
    for b in s["bands"]:
        print(f"  {b['kind'] + str(b['idx']):>10s} {b['xa']:8.3f} {b['xb']:8.3f} "
              f"{b['xb'] - b['xa']:7.3f} {b['ha']:7.3f} {b['hb']:7.3f}")
    # 밴드 단조성 = 겹침 없음 검증
    xs = [(b["xa"], b["xb"]) for b in s["bands"]]
    mono = all(abs(xs[i][1] - xs[i + 1][0]) < 1e-9 for i in range(len(xs) - 1))
    print(f"  밴드 인접성(겹침·틈 0): {'OK' if mono else 'FAIL'} · "
          f"총 {len(s['bands'])} 밴드 × 3매(내측+측벽 2)")
    jt = PARAMS["joint"]
    print(f"  줄눈: 격자 {jt['step']:.2f} m · proud {jt['proud']:.3f} "
          f"(페인트 {pa['z']:.3f} 위 {jt['proud'] - pa['z']:.3f} m) → "
          "그림 영역 관통 OK")
    lp = PARAMS["lamp"]
    az = math.radians(25.0)
    L = lp["pole_h"] / math.tan(math.radians(PARAMS["light"]["noon_sun_elev"]))
    tx = lp["cx"] + L * math.cos(az)
    ty = lp["cy"] + L * math.sin(az)
    print(f"  실그림자 단서: 가로등({lp['cx']:.2f},{lp['cy']:.2f}) h{lp['pole_h']:.1f} "
          f"→ 그림자 길이 {L:.2f} m, 끝점 ({tx:.2f},{ty:.2f}) "
          f"{'= 그림 내부 OK' if (0 <= tx <= s['x_f'] and abs(ty) <= il['width'] / 2) else '(그림 밖 — 재배치 검토)'}")
    mp = PARAMS["material"]
    bk = PARAMS["blocks"]
    print("  팔레트 v2(웜 스톤): tread %s / riser %s·%s / floor %s / wall %s"
          % (mp["tread_tint"], mp["riser_tint_a"], mp["riser_tint_b"],
             mp["floor_tint"], mp["wall_tint"]))
    print("             nosing %s / border %s / block %s  "
          "(암부 0.02~0.09 · R:G:B 웜 비율 유지)"
          % (mp["nosing_tint"], mp["border_tint"], mp["block_tint"]))
    print("  석재 블록 줄눈: enable=%s · z %.4f(페인트 %.4f 위 %.4f) · 폭 %.3f · "
          "디딤면 %d선 / 측벽 %d선"
          % (bk["enable"], bk["z"], pa["z"], bk["z"] - pa["z"], bk["w"],
             len(bk["tread_frac"]), len(bk["wall_frac"])))
    print("  [GT] 전 픽셀 '낙차 없음' — 전 기하 평면, 개구/수직면 없음")
    print("-" * 68)


def build_views():
    """카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷."""
    views = sc.grid_views(0.0)
    il = PARAMS["illusion"]
    # design_eye: 아나모픽 설계 1시점 — 착시가 성립하는 유일 지점
    views["design_eye"] = dict(eye=[il["eye_x"], 0.0, il["eye_h"]],
                               tgt=[3.5, 0.0, 0.0])
    # off_axis: 측면 — 원근이 붕괴해 '납작한 그림'임이 드러남(판별 단서 ④)
    views["off_axis"] = dict(eye=[1.5, -6.5, 1.7], tgt=[3.2, 0.0, 0.0])
    # joint_cross: 저시점 근접 — 줄눈이 그림을 관통(단서 ①)·스펙큘러(단서 ②)
    views["joint_cross"] = dict(eye=[-0.7, 0.0, 0.35], tgt=[4.5, 0.0, 0.02])
    # beauty_overview: 사선 부감 — 몰 맥락 + 그림 전개
    views["beauty_overview"] = dict(eye=[-5.0, -5.5, 3.4], tgt=[3.5, 0.0, 0.0])
    return views


# ===========================================================================
# [C5] 드레싱 검산 (Isaac 불요) — NEGOBS_GEOCHECK=1 python3 sceneN3_trompe_loeil.py
#   ① 카메라 매몰 : 전 뷰 eye 가 신규 입체물 AABB(여유 0.35) 밖인가
#   ② 그림 폐색   : 신규 입체물이 카메라–그림 사이 방위구간을 침범하는가
# ===========================================================================
def placements():
    """[v5.1 §3] 결정적 지터 배치. 빌더·검산이 공유한다.
    반환 (benches[(name,x,y,yaw)], planters[(name,x,y)], bollards[(name,x,y)])."""
    bl = []
    for b in PARAMS["benches"]:
        dx, dy = bc.jit_pos(b["cx"], b["cy"], "benchN3", amp=0.18)
        yaw = bc.jit_yaw(b["cx"], b["cy"], "benchN3", lo=3.0, hi=8.0,
                         base=b["yaw"])
        bl.append((b["name"], b["cx"] + dx, b["cy"] + dy, yaw))
    pl = []
    for p in PARAMS["planters"]:
        dx, dy = bc.jit_pos(p["cx"], p["cy"], "plN3", amp=0.15)
        pl.append((p["name"], p["cx"] + dx, p["cy"] + dy))
    bo = []
    sp = PARAMS["bollard"]["spacing"]
    for row in PARAMS["bollard_rows"]:
        pts = bc.bollard_line(row["x"], row["y0"], row["x"], row["y1"],
                              spacing=sp)
        for i, (bx, by) in enumerate(pts):
            bo.append((f"{row['name']}{i}", bx, by))
    return bl, pl, bo


def dressing_aabbs():
    """맥락 드레싱 **입체물**의 (name, xa, xb, ya, yb, z_top). 페인트는 flush."""
    out = []
    _benches, _planters, _bollards = placements()
    sp = PARAMS["shop"]
    for fd in PARAMS["shop_facades"]:
        fy, dr = float(fd["y"]), float(fd["dir"])
        y_in = fy + dr * (sp["podium_t"] - sp["podium_embed"])   # 포디엄 전면
        y_aw = fy + dr * (sp["podium_t"] - sp["podium_embed"] + sp["awn_proj"])
        out.append((f"Shop_{fd['name']}", sp["x0"], sp["x1"],
                    min(fy, y_aw), max(fy, y_aw), sp["podium_h"]))
        out.append((f"ShopFace_{fd['name']}", sp["x0"], sp["x1"],
                    min(fy, y_in), max(fy, y_in), sp["podium_h"]))
    pl = PARAMS["planter"]
    ph = pl["size"] / 2.0
    top_tree = pl["grass_h"] + 2.2 + 0.85 + 0.24
    for name, px, py in _planters:
        out.append((f"Planter_{name}", px - ph, px + ph,
                    py - ph, py + ph, top_tree))
    # 벤치 1.8×0.4×h0.45 — yaw 지터 ≤8° 상계로 반폭 (0.92, 0.32)
    for name, bx, by, _yaw in _benches:
        out.append((f"Bench_{name}", bx - 0.92, bx + 0.92,
                    by - 0.32, by + 0.32, 0.45))
    bo = PARAMS["bollard"]
    for name, bx, by in _bollards:
        out.extend(bc.bollard_v51_aabbs(f"Bollard_{name}", bx, by, 0.0,
                                        front_dir=bo["front"],
                                        radius=bo["r"], height=bo["h"]))
    lp = PARAMS["lamp"]                     # 기둥/헤드 분리(과대 상계 방지)
    out.append(("LampPole", lp["cx"] - lp["pole_r"], lp["cx"] + lp["pole_r"],
                lp["cy"] - lp["pole_r"], lp["cy"] + lp["pole_r"],
                lp["pole_h"]))
    es = PARAMS["entry_sign"]
    out.append(("EntrySign", es["x"] - es["w"] / 2.0, es["x"] + es["w"] / 2.0,
                es["y"] - 0.1, es["y"] + 0.1, es["pole_h"]))
    for k, bd in PARAMS["buildings"].items():
        out.append((f"Building_{k}", bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                    bd["h"] + 0.5))
    return out


def dresscheck():
    """※ 기지 예외(허용): beauty_overview·off_axis 에서 **기존 가로등 기둥**
    (r 0.07, x 0.6 / y −2.6)이 그림 샘플의 3~5 % 를 스친다. 이 가로등은 판별
    단서 ③(실그림자가 그림 위를 지나감)의 광원 기하 자체라 이동 불가이며,
    14 cm 기둥이 6.30×3.00 m 그림을 가로지르는 얇은 선이므로 특색 판독을
    저해하지 않는다. **신규 맥락 드레싱은 전 뷰 0건**이어야 한다.
    """
    il = PARAMS["illusion"]
    s = illusion_summary(il)
    hw = il["width"] / 2.0
    pc = [(px, py) for px in (il["x_rim"], s["x_f"]) for py in (-hw, hw)]
    boxes = dressing_aabbs()
    views = build_views()
    print("-" * 68)
    print("sceneN3 드레싱 검산 (그림 풋프린트 x[%.2f, %.2f] × y±%.2f)"
          % (il["x_rim"], s["x_f"], hw))
    m, hit, worst = 0.35, 0, (None, 1e9)
    for vn, v in sorted(views.items()):
        ex_, ey_, ez_ = v["eye"]
        for nm, xa, xb, ya, yb, zt in boxes:
            if (xa - m <= ex_ <= xb + m and ya - m <= ey_ <= yb + m
                    and -m <= ez_ <= zt + m):
                print("  %-20s ★카메라 매몰★ %s" % (vn, nm))
                hit += 1
            d = max(xa - ex_, ex_ - xb, ya - ey_, ey_ - yb, 0.0)
            if d < worst[1]:
                worst = ("%s vs %s" % (vn, nm), d)
    print("  ① 카메라 매몰: %s (최근접 수평 %s = %.2f m)"
          % ("0건 합격" if hit == 0 else "%d건 불합격" % hit, worst[0], worst[1]))

    # ② 시선 차단 검사 — 그림 풋프린트를 13×7 격자로 샘플하고 eye→샘플점
    #    선분이 드레싱 AABB(0.01 축소)를 관통하는지 슬랩법으로 판정한다.
    def seg_hits_box(p0, p1, bmin, bmax):
        tmin, tmax = 0.0, 1.0
        for i in range(3):
            d = p1[i] - p0[i]
            if abs(d) < 1e-12:
                if p0[i] < bmin[i] or p0[i] > bmax[i]:
                    return False
                continue
            t1 = (bmin[i] - p0[i]) / d
            t2 = (bmax[i] - p0[i]) / d
            if t1 > t2:
                t1, t2 = t2, t1
            tmin, tmax = max(tmin, t1), min(tmax, t2)
            if tmin > tmax:
                return False
        return True

    def in_frame(eye, tgt, p, hfov=60.0, vfov=36.0):
        fx, fy, fz = (tgt[0] - eye[0], tgt[1] - eye[1], tgt[2] - eye[2])
        fn = math.sqrt(fx * fx + fy * fy + fz * fz)
        fx, fy, fz = fx / fn, fy / fn, fz / fn
        rx, ry = fy, -fx
        rn = math.hypot(rx, ry)
        if rn < 1e-9:
            return False
        rx, ry = rx / rn, ry / rn
        ux, uy, uz = ry * fz, -rx * fz, rx * fy - ry * fx
        dx, dy, dz = p[0] - eye[0], p[1] - eye[1], p[2] - eye[2]
        fw = dx * fx + dy * fy + dz * fz
        if fw <= 1e-6:
            return False
        ah = math.degrees(math.atan2(abs(dx * rx + dy * ry), fw))
        av = math.degrees(math.atan2(abs(dx * ux + dy * uy + dz * uz), fw))
        return ah < hfov / 2.0 and av < vfov / 2.0

    pts = [(il["x_rim"] + (s["x_f"] - il["x_rim"]) * i / 12.0,
            -hw + 2.0 * hw * j / 6.0, 0.0)
           for i in range(13) for j in range(7)]
    bad = 0
    for vn, v in sorted(views.items()):
        eye = tuple(float(c) for c in v["eye"])
        vis = [p for p in pts if in_frame(eye, v["tgt"], p)]
        if not vis:
            continue
        for nm, xa, xb, ya, yb, zt in boxes:
            bmin = (xa + 0.01, ya + 0.01, 0.01)
            bmax = (xb - 0.01, yb - 0.01, zt - 0.01)
            if bmax[0] <= bmin[0] or bmax[1] <= bmin[1] or bmax[2] <= bmin[2]:
                continue
            n_hit = sum(1 for p in vis if seg_hits_box(eye, p, bmin, bmax))
            if n_hit:
                print("  %-20s ★그림 시선 차단★ %s (%d/%d 프레임내 샘플)"
                      % (vn, nm, n_hit, len(vis)))
                bad += 1
    print("  ② 그림 시선 차단(프레임 내 샘플 한정): %s"
          % ("0건 합격" if bad == 0 else "%d건 검토" % bad))
    print("-" * 68)


def geocheck():
    _geometry_report()
    dresscheck()


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. design_eye / h0.9_d2 — 그림이 '하강 계단정'으로 읽히는가(착시 성립·특색)
 2. joint_cross          — 포장 줄눈이 그림을 끊김 없이 관통하는가(단서 ①)
 3. 암부 스펙큘러        — 라이저 암부에 포장과 같은 반사가 남는가(단서 ②)
 4. 실그림자             — 가로등 기둥 그림자가 그림 위를 지나가는가(단서 ③)
 5. off_axis             — 시점 이탈 시 원근이 붕괴하는가(단서 ④)
 6. GT 불변식            — 전 기하 평면·개구 없음·Z파이팅/부유 없는가
 7. 그림 ON vs OFF       — hazard_stairs False 시 순수 평지 몰
 8. 팔레트 v2 [1순위]    — 그림이 **웜 베이지·황갈 석재 분필화**로 읽히는가
                            (무채색 회색 줄무늬면 실패 — v1 폐기 사유).
                            석재 블록 줄눈이 트레드·측벽에 보이는가
 9. 몰 맥락             — 차양·쇼윈도·사인 밴드·벤치·화분·안내 사인으로
                            "보행자 몰"이 렌더만으로 읽히는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene23")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene23"

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
        M["plaza"] = PBR(
            f"{ROOT}/Looks/Plaza", sc.tex_path("stone_flag", "diff"),
            sc.tex_path("stone_flag", "nor"), sc.tex_path("stone_flag", "rough"),
            sca["stone_flag"])
        M["band"] = PBR(
            f"{ROOT}/Looks/Band", sc.tex_path("band_dark", "diff"),
            sc.tex_path("band_dark", "nor"), sc.tex_path("band_dark", "rough"),
            sca["band_dark"])
        M["light_stone"] = PBR(
            f"{ROOT}/Looks/LightStone", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"),
            sc.tex_path("plaza_light", "rough"), sca["plaza_light"],
            tint=(0.72, 0.72, 0.72))                     # [T1 T-1] x0.72
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            2.0, tint=mp["wall_face_tint"])
        M["joint"] = PBR(f"{ROOT}/Looks/Joint",
                         diffuse_color=mp["joint_color"],
                         roughness_const=mp["joint_rough"], metallic=0.0)
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        metallic=mp["lamp_metallic"],
                        roughness_const=mp["lamp_rough"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots actually shade.
        M["tactile"] = bc.tactile_mtl(stage, f"{ROOT}/Looks/Tactile")
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        # ─ 그림 내부 석재 블록 줄눈 ─
        M["block"] = PBR(f"{ROOT}/Looks/Block", diffuse_color=mp["block_tint"],
                         roughness_const=mp["paint_rough"], metallic=0.0)
        # ─ 몰 맥락(상점 파사드) ─
        M["podium"] = PBR(
            f"{ROOT}/Looks/Podium", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"),
            sc.tex_path("plaza_light", "rough"), 1.4, tint=mp["podium_tint"])
        M["shopglass"] = PBR(f"{ROOT}/Looks/ShopGlass",
                             diffuse_color=mp["shopglass_color"],
                             roughness_const=mp["shopglass_rough"], metallic=0.0)
        M["awning_a"] = PBR(f"{ROOT}/Looks/AwningA",
                            diffuse_color=mp["awning_a"],
                            roughness_const=mp["awning_rough"])
        M["awning_b"] = PBR(f"{ROOT}/Looks/AwningB",
                            diffuse_color=mp["awning_b"],
                            roughness_const=mp["awning_rough"])
        M["fascia_a"] = PBR(f"{ROOT}/Looks/FasciaA",
                            diffuse_color=mp["fascia_a"],
                            roughness_const=mp["fascia_rough"])
        M["fascia_b"] = PBR(f"{ROOT}/Looks/FasciaB",
                            diffuse_color=mp["fascia_b"],
                            roughness_const=mp["fascia_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=mp["sign_rough"])
        # 한글 안내 사인 패널 — uv_mode(메시 st 1:1 정합, build_sign 전용)
        M["sign_panel"] = PBR(f"{ROOT}/Looks/SignPanel",
                              sc.tex_path("sign_info", "diff"), uv_mode=True,
                              roughness_const=0.45)
        return M

    # -------------------------------------------------------------------
    # 페인트 재질 팩토리 — 깊이에 따라 톤을 낮춘 틴트를 캐시해 재사용.
    #   roughness 는 전 페인트가 paint_rough(포장과 동일) — "재질 함정".
    # -------------------------------------------------------------------
    def make_paint_mtl_of():
        cache = {}
        base = dict(floor=mp["floor_tint"], tread=mp["tread_tint"],
                    wall=mp["wall_tint"], nosing=mp["nosing_tint"],
                    border=mp["border_tint"],
                    riser_a=mp["riser_tint_a"], riser_b=mp["riser_tint_b"])
        plaza_ref = tuple(mp["flat_ref"])       # 포장 평균 톤(대비 약화용·웜)
        # 깊이 감쇠 하한: 라이저는 0.04~0.08 대역을 유지해야 하므로 얕게 감쇠
        lo = dict(floor=1.0, tread=0.55, wall=0.45, riser=0.80,
                  nosing=0.70, border=1.0)

        def mtl_of(kind, idx, depth_frac):
            key_kind = kind
            tint = base.get(kind)
            if kind == "riser":
                key_kind = "riser_a" if idx % 2 == 0 else "riser_b"
                tint = base[key_kind]
            f = lo.get("riser" if kind == "riser" else kind, 1.0)
            k = f + (1.0 - f) * max(0.0, min(1.0, float(depth_frac)))
            col = tuple(c * k for c in tint)
            if not cfg["cue_material_break"]:
                m = float(mp["flat_mix"])
                col = tuple(c * (1.0 - m) + p * m
                            for c, p in zip(col, plaza_ref))
            ck = tuple(round(c, 4) for c in col)
            if ck not in cache:
                path = f"{ROOT}/Looks/Paint/{key_kind}_{len(cache):02d}"
                cache[ck] = PBR(path, diffuse_color=ck,
                                roughness_const=mp["paint_rough"],
                                metallic=0.0)
            return cache[ck]

        return mtl_of, cache

    # -------------------------------------------------------------------
    # 포장 — 대형 판석 평판 + 화강암 경계 밴드 (개구 없음 → 분할 불요)
    # -------------------------------------------------------------------
    def build_plaza(M):
        pz = PARAMS["plaza"]
        cz = pz["z_top"] - pz["thick"] / 2.0
        BOX(f"{ROOT}/Plaza",
            ((pz["x0"] + pz["x1"]) / 2.0, (pz["y0"] + pz["y1"]) / 2.0, cz),
            (pz["x1"] - pz["x0"], pz["y1"] - pz["y0"], pz["thick"]),
            M["plaza"], col=True)
        bd = PARAMS["band"]
        z_top = pz["z_top"] + bd["proud"]
        z_bot = pz["z_top"] - bd["embed"]
        jt = PARAMS["joint"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Band_{tag}",
                ((jt["x0"] + jt["x1"]) / 2.0, sgn * bd["y"],
                 (z_top + z_bot) / 2.0),
                (jt["x1"] - jt["x0"], bd["width"], z_top - z_bot), M["band"])

    # -------------------------------------------------------------------
    # 포장 줄눈 — 격자. **그림 영역을 관통**해 이어진다(판별 단서 ①).
    #   페인트(z=0.001) 위 proud 0.003 → 2 mm 이격, Z-파이팅 없음.
    # -------------------------------------------------------------------
    def build_joints(M):
        jt = PARAMS["joint"]
        pz = PARAMS["plaza"]
        z_top = pz["z_top"] + jt["proud"]
        z_bot = pz["z_top"] - jt["embed"]
        zc, hz = (z_top + z_bot) / 2.0, z_top - z_bot
        Lx = jt["x1"] - jt["x0"]
        Ly = jt["y1"] - jt["y0"]
        n_x = int(round(Lx / jt["step"])) + 1
        n_y = int(round(Ly / jt["step"])) + 1
        for i in range(n_x):                     # 횡단 줄눈 (일정 x)
            x = jt["x0"] + i * jt["step"]
            BOX(f"{ROOT}/JointX_{i}", (x, (jt["y0"] + jt["y1"]) / 2.0, zc),
                (jt["width"], Ly, hz), M["joint"])
        for j in range(n_y):                     # 종단 줄눈 (일정 y)
            y = jt["y0"] + j * jt["step"]
            BOX(f"{ROOT}/JointY_{j}", ((jt["x0"] + jt["x1"]) / 2.0, y, zc),
                (Lx, jt["width"], hz), M["joint"])

    # -------------------------------------------------------------------
    # 그림 — 아나모픽 페인트 배열 + 외곽 라인
    # -------------------------------------------------------------------
    def build_painting(M):
        il = PARAMS["illusion"]
        pa = PARAMS["paint"]
        mtl_of, cache = make_paint_mtl_of()
        bands, n_prim = paint_fake_stairs(stage, f"{ROOT}/Paint", il, pa,
                                          mtl_of, nosing=cfg["cue_nosing"],
                                          blocks=PARAMS["blocks"],
                                          block_mtl=M["block"])
        s = illusion_summary(il)
        print(f"[그림] 밴드 {len(bands)} · 페인트 프림 {n_prim} · "
              f"재질 {len(cache)} · 풋프린트 x[{il['x_rim']:.2f},{s['x_f']:.2f}] "
              f"× {il['width']:.2f} m · 가시 단 {len(s['steps'])}/{il['nsteps']}")
        if not pa["border"]:
            return
        # 외곽 백색 라인 (그림 경계 — 레퍼런스의 분필 테두리)
        bmtl = mtl_of("border", 0, 1.0)
        hw = il["width"] / 2.0
        w = pa["border_w"]
        z = pa["border_z"]
        x0, x1 = il["x_rim"], s["x_f"]
        rects = [("W", x0 - w / 2.0, 0.0, w, 2 * hw + w),
                 ("E", x1 + w / 2.0, 0.0, w, 2 * hw + w),
                 ("S", (x0 + x1) / 2.0, -hw - w / 2.0, x1 - x0, w),
                 ("N", (x0 + x1) / 2.0, hw + w / 2.0, x1 - x0, w)]
        for tag, cx, cy, sx, sy in rects:
            _paint_quad(stage, f"{ROOT}/Paint/Border_{tag}",
                        [(cx - sx / 2.0, cy - sy / 2.0),
                         (cx + sx / 2.0, cy - sy / 2.0),
                         (cx + sx / 2.0, cy + sy / 2.0),
                         (cx - sx / 2.0, cy + sy / 2.0)], z, bmtl)

    # -------------------------------------------------------------------
    # 드레싱 — 가로등(실그림자 단서)·화단·벤치·볼라드·상가 건물
    # -------------------------------------------------------------------
    def build_dressing(M):
        lp = PARAMS["lamp"]
        CYL(f"{ROOT}/Lamp/Pole", (lp["cx"], lp["cy"], lp["pole_h"] / 2.0),
            lp["pole_r"], lp["pole_h"], M["lamp"], col=True)
        hd = lp["head"]
        BOX(f"{ROOT}/Lamp/Head",
            (lp["cx"] + hd[0] / 2.0 - lp["pole_r"], lp["cy"],
             lp["pole_h"] + hd[2] / 2.0), hd, M["lamp"])
        _benches, _planters, _bollards = placements()
        pl = PARAMS["planter"]
        for name, px, py in _planters:
            sc.build_planter(
                stage, f"{ROOT}/Planter_{name}", px, py,
                0.0, M["curb"], M["grass"],
                tree_mtls=(M["wood"], M["canopy_a"], M["canopy_b"]),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"],
                grass_h=pl["grass_h"])
        for name, bx, by, byaw in _benches:
            sc.build_bench(stage, f"{ROOT}/Bench_{name}", bx, by, 0.0,
                           M["wood"], yaw=byaw)
        # 볼라드 [v5.1 §2] — 몰 진입부 횡단 1열(중앙 4.8 m 소방 통로 개방)
        bo = PARAMS["bollard"]
        for name, bx, by in _bollards:
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{name}", bx, by, 0.0,
                                 None, M["bollard"], M["bollard_band"],
                                 M["tactile"], front_dir=bo["front"],
                                 radius=bo["r"], height=bo["h"])
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        build_shopfronts(M)
        es = PARAMS["entry_sign"]
        sc.build_sign(stage, f"{ROOT}/EntrySign", es["x"], es["y"], 0.0,
                      es["yaw"], M["sign_panel"], w=es["w"], h=es["h"],
                      pole_h=es["pole_h"], pole_r=es["pole_r"],
                      pole_mtl=M["lamp"], back_mtl=M["sign"])

    # -------------------------------------------------------------------
    # 상점 파사드 밴드 — "보행자 몰"을 렌더만으로 읽히게 하는 핵심 맥락.
    #   포디엄(1층 벽) + 베이별 쇼윈도·차양·사인 밴드. 전부 |y| ≥ 8.25 이므로
    #   그림(|y| ≤ 1.5) 폐색·카메라 매몰과 무관 [shopcheck() 검산].
    #   그림자: 태양 az 205 → 그림자 방위 25°(+X,+Y). L(y=+10) 차양 그림자는
    #   +Y 로, R(y=−10) 차양 그림자는 y −8.25 → −6.8 부근까지만 이동 →
    #   그림 영역(|y| ≤ 1.5)에 닿지 않는다.
    # -------------------------------------------------------------------
    def build_shopfronts(M):
        sp = PARAMS["shop"]
        nbay = max(1, int(round((sp["x1"] - sp["x0"]) / sp["bay"])))
        bw = sp["bay"] - sp["gap"]
        for fd in PARAMS["shop_facades"]:
            fy, dr = float(fd["y"]), float(fd["dir"])
            base = f"{ROOT}/Shop_{fd['name']}"
            # 포디엄(1층 벽) — 건물 1층 창을 완전히 내포(Z-파이팅 회피).
            #   셸 안쪽으로 podium_embed 만큼 물려 배면 동일평면도 제거한다.
            py = fy + dr * (sp["podium_t"] / 2.0 - sp["podium_embed"])
            BOX(f"{base}/Podium",
                ((sp["x0"] + sp["x1"]) / 2.0, py, sp["podium_h"] / 2.0),
                (sp["x1"] - sp["x0"], sp["podium_t"], sp["podium_h"]),
                M["podium"], col=True)
            face = fy + dr * (sp["podium_t"] - sp["podium_embed"])   # 전면 y
            for i in range(nbay):
                xc = sp["x0"] + (i + 0.5) * sp["bay"]
                BOX(f"{base}/Glass_{i}",
                    (xc, face + dr * (sp["glass_proud"] - sp["glass_t"] / 2.0),
                     (sp["glass_z0"] + sp["glass_z1"]) / 2.0),
                    (bw, sp["glass_t"], sp["glass_z1"] - sp["glass_z0"]),
                    M["shopglass"])
                BOX(f"{base}/Awning_{i}",
                    (xc, face + dr * sp["awn_proj"] / 2.0, sp["awn_z"]),
                    (bw, sp["awn_proj"], sp["awn_t"]),
                    M["awning_a"] if i % 2 == 0 else M["awning_b"])
                BOX(f"{base}/Fascia_{i}",
                    (xc, face + dr * (sp["fascia_proud"] - sp["fascia_t"] / 2.0),
                     (sp["fascia_z0"] + sp["fascia_z1"]) / 2.0),
                    (bw, sp["fascia_t"], sp["fascia_z1"] - sp["fascia_z0"]),
                    M["fascia_a"] if i % 2 == 0 else M["fascia_b"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_plaza(M)
    if cfg["hazard_stairs"]:
        build_painting(M)
    build_joints(M)                              # 그림 위를 관통 — 그림 뒤에 배치
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        _geometry_report()
        print(f"[SMOKE] sceneN3 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["design_eye"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN3_{ts}.png")
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
    if os.environ.get("NEGOBS_GEOCHECK", "0") == "1":
        geocheck()                     # Isaac 부팅 없이 아나모픽·드레싱 검산
    else:
        main()
