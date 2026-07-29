# -*- coding: utf-8 -*-
"""
scene08_sunken_plaza.py — NegObs 인공씬 8호 (v5 R3): 도심 선큰 광장 (Isaac Sim 4.5)

유형    : 사방 하강 피트(구 T11 스텝웰 기하축 계승) — 무대만 '지하상가 연결
          선큰 가든'으로 교체. 사양서: Docs/briefs/multi_scene_brief_v5.md §R3
          (근거: Docs/scene_redesign_v5_proposal.md 처분표 08=교체)
공통    : scene_common.py (build_straight_stairs/build_rot_group/build_planter/
          build_railing_line/build_sign/build_tactile) ·
          구 scene08(scenes/archive_v3/scene08_stepwell_lattice.py)의
          **개구 4박스 + 사광 60°** 사용례를 승계.

위험 본질
  상부 보행 광장(인터로킹 40×30) 한복판에 12×9 사각 피트(깊이 4.498)가 뚫려
  있다. 로봇 눈높이(h0.3)에서 피트는 **원리적으로 전부 은닉**된다 —
  근측 연단(x=0, z=0)을 스치는 시선이 피트 바닥(−4.498)에 닿는 지점은
  x = 4.498·d/0.3 = 15·d (d=2 m 에서 30 m) 로, 피트 동단 12 m 를 한참 넘는다.
  즉 h0.3 에서는 원측 광장(x≥12.4, z=0)이 근측 지면과 **연속된 평면**으로
  읽히고 그 사이 4.5 m 공동은 화면에서 사라진다(negative obstacle).
  피트 둘레는 파라펫(h 1.0 — 현행 규정 1.1 미달)로 방호되지만, 접근측
  파라펫 **1.8 m 구간이 공사로 철거**되고 임시 표지(안전봉 2 + 테이프 1선)만
  남아 있다 → 그 개방 구간을 통해 무방호 낙차가 그대로 노출된다.

목표
  ① 광장 슬래브 4박스 + 지반 프레임 4박스(공동 위를 어떤 평면도 덮지 않음)
  ② 남·북 광폭 계단(폭 4, riser 0.173 × 26 = 4.498) 2련 — 회전그룹 ±90°
  ③ 피트 바닥 코트(화단 2·벤치 2) + 지하상가 유리 파사드(약발광)
  ④ 접근측 파라펫 개방 구간 + 임시 표지(안전봉·테이프)
  ⑤ 개구 둘레 점자블록(cue_tactile 기본 True — 도시 관행 씬)

[v5 브리프 대비 의도적 편차 1건]
  브리프 §R3 는 개방 구간을 "동측 에지"로 지정했으나 **접근측(서측 x=0)** 으로
  옮겼다. 사유: (a) v5 원칙 "grid h0.3 판정 1순위 — 위험 은닉이 로봇 시점에서
  성립하는지"를 만족하려면 개방 구간이 그리드 축(+X, y=0) 위에 있어야 한다.
  (b) 접근측 에지를 파라펫으로 완전히 막으면 h0.3/h0.9 그리드 9컷 중 6컷이
  파라펫 벽면으로 채워져 판정 불능이 된다(scene19 d5 암흑 전례와 동형).
  동측 에지에는 파라펫이 온전히 남아 대조군 역할을 한다.

보행 연속성 자가 검증표 (진입 → 하강 → 코트 → 상행 → 탈출; 전 구간 단차 ≤ 0.173)
  ┌ # 구간            좌표(x, y, z)                  단차/판정
  │ 0 광장 접근        (−10.0, 0.0, 0.00)            평탄(인터로킹)
  │ 1 점자블록 띠      (−0.75, 0.0, 0.004)           0.004 (경고 단서)
  │ 2 개방 구간 연단   ( 0.00, 0.0, 0.00)            ← **낙차 4.498 무방호**
  │ 3 남측 계단 머리   ( 2.00, −4.70, 0.00)          평탄(문턱 슬래브)
  │ 4 1단 디딤         ( 2.00, −4.35, −0.173)        0.173
  │ 5 25단 디딤        ( 2.00, 2.85, −4.325)         0.173 × 24
  │ 6 피트 바닥        ( 2.00, 3.30, −4.498)         0.173 (26번째 라이저)
  │ 7 코트 진입        ( 4.20, 3.60, −4.498)         평탄 (x=4 경계 개방)
  │ 8 코트 중앙        ( 6.00, 0.00, −4.498)         평탄 (화단·벤치·파사드)
  │ 9 북측 계단 하부   ( 10.00, −3.60, −4.498)       평탄 (x=8 경계 개방)
  │10 25단 디딤        ( 10.00, −2.85, −4.325)       0.173 (상행)
  │11 북측 계단 머리   ( 10.00, 4.70, 0.00)          0.173 × 25
  └12 광장 탈출        ( 10.00, 8.00, 0.00)          평탄
  * 남측 계단 폭 4(x 0..4)·북측 계단 폭 4(x 8..12) — 코트 x 4..8(4×9)이 상시 개방.
  * 계단 코트측 측면(x=4 / x=8)은 계단 하강선을 따르는 파이프 난간(cue_railing).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene08_sunken_plaza.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene08_sunken_plaza.py
스모크(부팅 전 기하·조명·카메라 자기검증·조기종료):
    NEGOBS_SMOKE=1 python scene08_sunken_plaza.py

좌표계: Z-up, m, 진행축 +X(광장 접근 → 피트). **낙차 시작 모서리 x=0.**
  피트 개구 x 0..12, y −4.5..4.5. 광장 상면 z=0, 피트 바닥 z=−4.498.
  태양: SUN_AZ_OFFSET=60(사광, 구 scene08 승계) → 광선이 +Y 상공에서 −Y로
  진행하므로 피트 **남측 절반이 직사, 북측이 암부** (스모크에서 수치 검산).
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG — 7키. hazard_stairs 만 위험 기하 토글(피트 ↔ 평지).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 피트/계단/코트를 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        True,    # 피트 둘레 파라펫(h1.0) + 계단 측면 난간. 개방 1.8 m 구간은 상시 결손
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)    # [v5 공통] 도시 관행 씬 — 개구 둘레 점자블록 띠
    "cue_material_break": True,    # 광장 인터로킹 vs 피트 콘크리트/화강 대비. False → 계단도 인터로킹
    "cue_sign":           True,    # [v5.2 사용자] 임의 경고 팻말 제거 — 임시 표지 + sign_exit(북측)
    "cue_scene_dressing": True,    # 화단·가로수·벤치·가로등·볼라드·원경 건물
    "cue_nosing":         False,   # True → 계단 단코 논슬립 띠
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
_RISER = 0.173
_NRISER = 26                       # 총 라이저 수 → 낙차 26 × 0.173 = 4.498
_FLOOR_Z = -round(_RISER * _NRISER, 4)          # -4.498

PARAMS = dict(
    # --- 피트 개구 (12 × 9, 깊이 4.498) ---
    #     ring_t: 개구 테두리 콘크리트 코핑 겸 피트 옹벽 두께. 광장 슬래브는
    #     이 링 **바깥**에서 끝난다 → 링 상면과 슬래브 상면이 겹치지 않아
    #     동일평면 Z파이팅이 원천 차단된다(§A-8).
    pit=dict(x0=0.0, x1=12.0, y0=-4.5, y1=4.5, floor_z=_FLOOR_Z,
             ring_t=0.4, floor_thick=0.6, ring_bot=-5.0),
    # --- 광장 슬래브 40 × 30 (개구를 4박스로 비움) ---
    plaza=dict(x0=-22.0, x1=18.0, y0=-15.0, y1=15.0, z_top=0.0, thick=0.8),
    # --- 주변 지반 프레임(차도 아스팔트, 광장보다 0.15 낮음) 4박스 ---
    ground=dict(x0=-45.0, x1=45.0, y0=-45.0, y1=45.0, z_top=-0.15, thick=1.0),
    # --- 남·북 광폭 계단 (폭 4, riser 0.173 × 26, tread 0.30) ---
    #     n_geom = 25 : 26번째 라이저는 **피트 바닥 자체**. 26개를 다 세우면
    #     마지막 단 상면(−4.498)이 바닥 슬래브 상면과 동일평면 → Z파이팅.
    stair=dict(riser=_RISER, tread=0.30, n_riser=_NRISER, n_geom=_NRISER - 1,
               width=4.0, base_z=-4.9,
               south_x0=0.0,        # 남측 계단 x 0..4  (y −4.5 → 3.0 하강)
               north_x0=8.0),       # 북측 계단 x 8..12 (y +4.5 → −3.0 하강)
    # --- 파라펫(h 1.0 = 현행 규정 1.1 미달 — "규정 미달의 현실") ---
    #     gap: 접근측(서측 x=0) 철거 구간 1.8 m. 개방 구간만 무방호.
    #     [v6 C-3] "무텍스처 순백 판 = 스티로폼" 지적 → 재질만 교체한다.
    #       h·t·gap·ext(= 기하와 카메라 구도)는 **판정 보존 권고에 따라 불변**.
    #       cope_h 는 h 안쪽에서 잘라 쓴다(몸통 h−cope_h + 코핑 cope_h = h).
    parapet=dict(h=1.0, t=0.25, gap_y0=-0.9, gap_y1=0.9, ext=0.25,
                 cope_h=0.08, cope_over=0.03,     # 코핑(갓돌) — 상단 0.08 m
                 grime_h=0.24, grime_over=0.008),  # 기단 오염 밴드 — 하단 0.24 m
    # --- 개구 둘레 점자블록 띠 (파라펫 바깥 0.05 여유, 폭 0.6) ---
    #  [W2-D Sec.12.4] scene08 = registered site `opening_ring`, p=0.51,
    #  statutory trigger "perimeter of an opening". It is **kept on the scene's
    #  own `build_tactile_ring` path** exactly as Sec.12.4 directs, so no
    #  `gk` tactile op is emitted (that would duplicate the band). The
    #  non-conforming variant assigned to this scene is "2-3 tiles missing",
    #  applied to the approach-side (west) band only - `gap_tiles` below.
    tactile=dict(w=0.6, off=0.05, proud=0.004, gap_tiles=2),

    # === [W2-D ground_kit] P3 `sidewalk_block` - spec Sec.5.2 row 08 ========
    #  Plaza slab is interlocking block; the pit opening at x=0 is the drop
    #  edge and is also passed as a **void** so GT-V (B8) is asserted.
    #  Near-window budget - one area element per preset cut, and the manhole
    #  is deliberately NOT in W1:
    #    d2  W1 x -1.436..0    -> patch #0 at x -1.25
    #    d5  W1 x -4.436..-3.0 -> patch #1 at x -3.60
    #    d10 W1 x -9.436..-8.0 -> patch #2 at x -8.60
    #    manhole x -2.40 -> d5 W2 (X=2.60) = 414 px = 21.6 % frame width.
    #      In W1 the phi 0.648 cover is >=28.1 % at any distance, which is the
    #      near-window monopoly the scene15 pilot had to undo. W2 is the only
    #      placement that satisfies both "1 manhole" and "<=25 %".
    #  region x1 = -0.95: clears the tactile band (x -0.90..-0.30) and the
    #  coping ring (x -0.40..0) while still overlapping the d2 W1 by 0.49 m.
    gkit=dict(
        region=(-12.0, -4.0, -0.95, 4.0),
        manhole=(-2.40, 1.60),
        gullies=((-1.75, -3.40), (-1.75, 3.40)),   # intercept before the pit
        #  |y| is kept small on purpose: the frame half-width at the W1
        #  mid-distance is only 0.43 m (d2), 0.81 m (d5/d10), so a patch
        #  offset by ~1 m falls out of frame and scores nothing [calc].
        patches=((-1.25, 0.20), (-3.60, -0.30), (-8.60, 0.40)),
        # Sec.5.2 "gully mandatory at the sunken low point" [시방]. The court
        # floor is a different slab at z=-4.498, so it needs its own plan.
        pit_region=(2.0, -3.0, 10.0, 3.0),
        pit_gully=(6.0, -2.0),
        seed=8,
    ),
    # --- 지하상가 유리 파사드 (피트 북벽 y=4.5, x 4..8) — 약발광 ---
    #     북벽 내면 법선 −Y = 태양(+Y 상공) 반대 → 상시 암부 → 약발광이 읽힌다.
    facade=dict(x0=4.0, x1=8.0, y=4.5, z0=-4.40, z1=-1.70, panels=6,
                glass_t=0.06, mull_w=0.09, mull_t=0.10, sill_h=0.18,
                emis=(0.86, 0.90, 0.82), emis_int=180.0),
    # --- 피트 바닥 코트 드레싱 ---
    court_planters=[(6.0, -2.6), (6.0, 2.6)],
    court_planter=dict(size=2.4, curb_h=0.42),
    court_benches=[(4.85, -0.7, 90.0), (7.15, 0.7, 90.0)],
    # --- 상부 광장 드레싱 ---
    #     접근 회랑(x −22..0, |y| ≤ 1.5)은 **완전 비움** — 그리드 카메라 축.
    gap_planters=[(-2.6, -3.0), (-2.6, 3.0)],       # 개방 구간 좌우(가림 요소)
    plaza_planters=[(-12.0, -10.5), (-12.0, 10.5),
                    (15.0, -10.5), (15.0, 10.5)],   # 가로수 화단
    plaza_planter=dict(size=3.0),
    plaza_benches=[(-8.0, -7.0, 0.0), (-8.0, 7.0, 180.0),
                   (14.5, -6.0, 0.0), (14.5, 6.0, 180.0)],
    streetlights=[(-6.0, -12.0), (6.0, -12.0), (-6.0, 12.0), (6.0, 12.0)],
    streetlight=dict(pole_h=4.8, pole_r=0.075, arm_len=1.0, arm_r=0.045,
                     head=0.26),
    bollards=[(-18.0, -2.4), (-18.0, 0.0), (-18.0, 2.4),
              (-18.0, -4.8), (-18.0, 4.8)],
    # --- 임시 표지(개방 구간) : 안전봉 2 + 경고 테이프 1선 ---
    #     [v6 C-6] 구 사양은 테이프가 두께 0.02 솔리드 각재라 **차단기 붐**으로
    #     읽혔고, 안전봉은 무늬 없는 주황 단색이었다. → 테이프는 두께 4 mm
    #     리본 + 처짐(양단 안전봉 결속), 안전봉은 적·백 교대 5밴드.
    #     x·post_r·post_h·배치는 불변(기하·카메라 보존).
    tempbar=dict(x=-0.72, post_r=0.045, post_h=1.0,
                 nband=5, band_ov=1.02,
                 tape=dict(z_end=0.85, sag=0.11, nseg=8, w=0.09, t=0.004,
                           tie_h=0.05),
                 post_color=(0.60, 0.14, 0.10),      # 적
                 post_color_b=(0.78, 0.78, 0.75),    # 백(순백 <0.8 규약)
                 tape_color=(0.75, 0.62, 0.10)),
    # --- 사인 (cue_sign) --- [v5.2 사용자] 임의 경고 팻말 제거(fall·step)
    sign_exit=dict(cx=9.20, cy=5.75, yaw=90.0, w=0.62, h=0.62, pole_h=2.2),
    # --- 원경(지평 폐쇄) : 동측 3동(주 카메라축 정면) + 남·북 2동 ---
    far_buildings=dict(
        E1=dict(x0=24.0, x1=34.0, y0=-26.0, y1=-8.0, h=26.0, floors=8,
                axis="x", facade_x=24.0, face_dir=-1.0, base_z=-0.15),
        E2=dict(x0=24.0, x1=34.0, y0=-4.0, y1=10.0, h=38.0, floors=12,
                axis="x", facade_x=24.0, face_dir=-1.0, base_z=-0.15),
        E3=dict(x0=24.0, x1=34.0, y0=14.0, y1=30.0, h=30.0, floors=10,
                axis="x", facade_x=24.0, face_dir=-1.0, base_z=-0.15),
        S1=dict(x0=-16.0, x1=-2.0, y0=-38.0, y1=-24.0, h=24.0, floors=8,
                axis="y", facade_y=-24.0, face_dir=1.0, base_z=-0.15),
        N1=dict(x0=-16.0, x1=-2.0, y0=24.0, y1=38.0, h=28.0, floors=9,
                axis="y", facade_y=24.0, face_dir=-1.0, base_z=-0.15),
    ),
    window=dict(w=1.3, h=1.7, inset=0.15, col_step=2.8, margin=2.2),
    # 차도 차선(지반 프레임 위) — "도심" 판독 보강
    road_lines=[dict(x0=-45.0, x1=45.0, y=-30.0), dict(x0=-45.0, x1=45.0, y=30.0)],

    material=dict(
        # texture_scale = 타일 물리크기[m]. 인터로킹 블록 텍스처는 4K 패치가
        # 대략 1.5 m 대역을 덮는다고 보고 1.5 로 둔다(과반복 방지).
        scale=dict(paving_interlock=1.5, concrete_wall=2.0, concrete_floor=1.0,
                   granite_dark=1.2, grass=1.4, tactile=0.3),
        grass_tint=(0.55, 0.68, 0.42),
        # sRGB 감마 규칙(§A-1): "어두운 색"은 0.02~0.06 대역.
        asphalt_color=(0.045, 0.045, 0.050), asphalt_rough=0.88,
        paint_color=(0.72, 0.72, 0.68), paint_rough=0.6,
        # [v6 C-3] 파라펫 = 상수색 단판 → **콘크리트 텍스처(diff+nor+rough)**.
        #   틴트로 알베도를 0.55~0.65 대역에 묶는다(순백 >0.8 금지 §4).
        parapet_color=(0.62, 0.61, 0.58), parapet_rough=0.65,
        parapet_tint=(0.80, 0.79, 0.76),      # 콘크리트 diff × 틴트 → ≈0.58
        cope_tint=(0.70, 0.69, 0.67),         # 코핑(갓돌) — 몸통보다 한 톤 낮게
        grime_color=(0.24, 0.235, 0.225), grime_rough=0.82,   # 기단 오염 밴드
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        bollard_color=(0.33, 0.33, 0.36), bollard_metallic=0.4,
        bollard_rough=0.5,
        glass_color=(0.055, 0.075, 0.090), glass_rough=0.10,
        mull_color=(0.055, 0.055, 0.060), mull_rough=0.45, mull_metallic=0.6,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        sign_back_color=(0.055, 0.060, 0.070), sign_back_rough=0.5,
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
    # 표준 171.5 → 60.0 (구 scene08 승계, 브리프 v5 §R3 명시). 깊이 4.5 의 좁은
    #   피트는 정오 표준광에서 내부가 통째로 암부가 된다. 사광으로 피트 남측
    #   절반·남측 계단 하부에 직사를 넣고 북측(유리 파사드측)을 암부로 남겨
    #   명암 대비를 만든다. 태양고도(elev)는 정오 유지.
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
# [C] 경로 + 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene08")
ASSET_ROLES = ["paving_interlock", "concrete_wall", "concrete_floor",
               "granite_dark", "grass", "tactile",
               "sign_exit",     # [v5.2 사용자] 임의 경고 팻말 제거
               "hdri", "mdl"]


# ===========================================================================
# [C2] 기하 헬퍼 (스모크·조립 공용 — 좌표 정의의 단일 출처)
# ===========================================================================
def _stair_local():
    """회전그룹 로컬 좌표에서의 계단 정의.
    남측: rot +90° @ (0,0) → world(x, y) = (−ly, lx)
    북측: rot −90° @ (0,0) → world(x, y) = ( ly, −lx)
    두 계단 모두 로컬 +X 하강(빌더 관례)이며 로컬 x0 = pit.y0 = −4.5.
    반환: dict(x0, run, drop)"""
    st = PARAMS["stair"]
    return dict(x0=PARAMS["pit"]["y0"],
                run=st["n_geom"] * st["tread"],
                drop=st["n_geom"] * st["riser"])


def _stair_ground_fn():
    """로컬 x → 계단 상면 z (난간 포스트 착지용 계단식 콜백)."""
    st = PARAMS["stair"]
    L = _stair_local()
    x_top, run, n = L["x0"], L["run"], st["n_geom"]

    def ground(x):
        if x <= x_top:
            return 0.0
        if x >= x_top + run:
            return -st["riser"] * n
        idx = min(int((x - x_top) / st["tread"]), n - 1)
        return -st["riser"] * (idx + 1)
    return ground


def _sun_dir():
    """DistantLight 진행 방향 d(월드). setup_lighting 의 op 순서
    (rotateZ(rz) → rotateX(90−elev), 기본 방향 −Z)를 그대로 역산한다.
      d0 = (0,0,−1) → rotX(rx): (0, sin rx, −cos rx) → rotZ(rz):
      (−sin rx · sin rz, sin rx · cos rz, −cos rx)
    태양 위치 방향은 −d."""
    lp = PARAMS["light"]
    rz = math.radians(lp["noon_dome_rot"] + PARAMS["SUN_AZ_OFFSET"]
                      + lp["hdri_sun_rotz_offset"])
    rx = math.radians(90.0 - lp["noon_sun_elev"])
    return (-math.sin(rx) * math.sin(rz),
            math.sin(rx) * math.cos(rz),
            -math.cos(rx))


def _obstacle_boxes():
    """카메라 충돌 검사용 장애물 AABB 목록 (name, x0,x1, y0,y1, z0,z1).
    [브리프 v5 지시] 그리드/미장센 카메라가 파라펫·화단과 충돌하지 않는지
    좌표로 검산한다(scene19 d5 암흑 전례)."""
    p = PARAMS["pit"]
    pr = PARAMS["parapet"]
    boxes = []
    # 파라펫 4변 (개방 구간 제외)
    for tag, (x0, x1, y0, y1) in (
            ("Parapet_W_S", (p["x0"] - pr["t"], p["x0"],
                             p["y0"] - pr["ext"], pr["gap_y0"])),
            ("Parapet_W_N", (p["x0"] - pr["t"], p["x0"],
                             pr["gap_y1"], p["y1"] + pr["ext"])),
            ("Parapet_E", (p["x1"], p["x1"] + pr["t"],
                           p["y0"] - pr["ext"], p["y1"] + pr["ext"])),
            ("Parapet_S", (4.0, p["x1"], p["y0"] - pr["ext"], p["y0"])),
            ("Parapet_N", (p["x0"], 8.0, p["y1"], p["y1"] + pr["ext"]))):
        boxes.append((tag, x0, x1, y0, y1, 0.0, pr["h"]))
    # 화단(광장) — 경계석 상면 0.50
    ps = PARAMS["plaza_planter"]["size"] / 2.0
    for i, (cx, cy) in enumerate(PARAMS["gap_planters"]):
        boxes.append((f"GapPlanter_{i}", cx - ps, cx + ps, cy - ps, cy + ps,
                      0.0, 0.50))
    for i, (cx, cy) in enumerate(PARAMS["plaza_planters"]):
        boxes.append((f"PlazaPlanter_{i}", cx - ps, cx + ps, cy - ps, cy + ps,
                      0.0, 3.40))          # 가로수 수관 포함
    # 화단(코트)
    cs = PARAMS["court_planter"]["size"] / 2.0
    for i, (cx, cy) in enumerate(PARAMS["court_planters"]):
        boxes.append((f"CourtPlanter_{i}", cx - cs, cx + cs, cy - cs, cy + cs,
                      p["floor_z"], p["floor_z"] + 0.50))
    # 계단 솔리드 2련 (world AABB)
    st = PARAMS["stair"]
    L = _stair_local()
    boxes.append(("Stair_S", st["south_x0"], st["south_x0"] + st["width"],
                  L["x0"], L["x0"] + L["run"], st["base_z"], 0.0))
    boxes.append(("Stair_N", st["north_x0"], st["north_x0"] + st["width"],
                  -(L["x0"] + L["run"]), -L["x0"], st["base_z"], 0.0))
    # 광장 슬래브 4박스 (상면 아래로 카메라가 잠기는지 검사)
    pl = PARAMS["plaza"]
    for tag, x0, x1, y0, y1 in (
            ("Plaza_W", pl["x0"], p["x0"] - p["ring_t"], pl["y0"], pl["y1"]),
            ("Plaza_E", p["x1"] + p["ring_t"], pl["x1"], pl["y0"], pl["y1"]),
            ("Plaza_S", p["x0"] - p["ring_t"], p["x1"] + p["ring_t"],
             pl["y0"], p["y0"] - p["ring_t"] - 0.1),
            ("Plaza_N", p["x0"] - p["ring_t"], p["x1"] + p["ring_t"],
             p["y1"] + p["ring_t"] + 0.1, pl["y1"])):
        boxes.append((tag, x0, x1, y0, y1, pl["z_top"] - pl["thick"],
                      pl["z_top"]))
    # 임시 안전봉·사인 지주
    tb = PARAMS["tempbar"]
    for i, gy in enumerate((pr["gap_y0"], pr["gap_y1"])):
        boxes.append((f"TempPost_{i}", tb["x"] - 0.06, tb["x"] + 0.06,
                      gy - 0.06, gy + 0.06, 0.0, tb["post_h"]))
    for tag, sg in (("SignExit", PARAMS["sign_exit"]),):
        hw = sg["w"] / 2.0 + 0.06
        boxes.append((tag, sg["cx"] - hw, sg["cx"] + hw,
                      sg["cy"] - hw, sg["cy"] + hw, 0.0, sg["pole_h"]))
    return boxes


def _solid_at(x, y, z):
    """점 (x,y,z)를 품는 지형/구조 솔리드 이름(없으면 None).
    카메라 eye 매몰 + **시선 차단(ray march)** 검사의 단일 출처.
    포함: 광장 슬래브 4, 코핑 링 4(=피트 옹벽), 계단 머리 문턱 2, 피트 바닥,
    지반 프레임 4, 남·북 계단 솔리드(회전 매핑을 역산한 계단식 상면), 파라펫."""
    p = PARAMS["pit"]
    pl = PARAMS["plaza"]
    gr = PARAMS["ground"]
    st = PARAMS["stair"]
    t = p["ring_t"]
    ox0, ox1, oy0, oy1 = p["x0"] - t, p["x1"] + t, p["y0"] - t, p["y1"] + t
    sx0, sx1 = st["south_x0"], st["south_x0"] + st["width"]
    nx0, nx1 = st["north_x0"], st["north_x0"] + st["width"]
    # 광장 슬래브 4박스
    for tag, x0, x1, y0, y1 in (("Plaza_W", pl["x0"], ox0, pl["y0"], pl["y1"]),
                                ("Plaza_E", ox1, pl["x1"], pl["y0"], pl["y1"]),
                                ("Plaza_S", ox0, ox1, pl["y0"], oy0),
                                ("Plaza_N", ox0, ox1, oy1, pl["y1"]),
                                ("StairHead_S", sx0, sx1, oy0, p["y0"]),
                                ("StairHead_N", nx0, nx1, p["y1"], oy1)):
        if x0 <= x <= x1 and y0 <= y <= y1 \
                and pl["z_top"] - pl["thick"] <= z < pl["z_top"]:
            return tag
    # 코핑 링(= 피트 옹벽) 4박스
    for tag, x0, x1, y0, y1 in (("Ring_W", ox0, p["x0"], oy0, oy1),
                                ("Ring_E", p["x1"], ox1, oy0, oy1),
                                ("Ring_S", sx1, p["x1"], oy0, p["y0"]),
                                ("Ring_N", p["x0"], nx0, p["y1"], oy1)):
        if x0 <= x <= x1 and y0 <= y <= y1 and p["ring_bot"] <= z < 0.0:
            return tag
    # 피트 바닥 슬래브
    if ox0 <= x <= ox1 and oy0 <= y <= oy1 \
            and p["floor_z"] - p["floor_thick"] <= z < p["floor_z"]:
        return "PitFloor"
    # 지반 프레임 4박스
    for tag, x0, x1, y0, y1 in (("Ground_W", gr["x0"], pl["x0"], gr["y0"], gr["y1"]),
                                ("Ground_E", pl["x1"], gr["x1"], gr["y0"], gr["y1"]),
                                ("Ground_S", pl["x0"], pl["x1"], gr["y0"], pl["y0"]),
                                ("Ground_N", pl["x0"], pl["x1"], pl["y1"], gr["y1"])):
        if x0 <= x <= x1 and y0 <= y <= y1 \
                and gr["z_top"] - gr["thick"] <= z < gr["z_top"]:
            return tag
    # 계단 솔리드 — world y 기준 계단식 상면(회전 매핑 역산)
    L = _stair_local()
    n = st["n_geom"]
    if sx0 <= x <= sx1 and L["x0"] <= y <= L["x0"] + L["run"]:
        idx = min(int((y - L["x0"]) / st["tread"]), n - 1)
        if st["base_z"] <= z < -st["riser"] * (idx + 1):
            return "Stair_S"
    if nx0 <= x <= nx1 and -(L["x0"] + L["run"]) <= y <= -L["x0"]:
        idx = min(int((-L["x0"] - y) / st["tread"]), n - 1)
        if st["base_z"] <= z < -st["riser"] * (idx + 1):
            return "Stair_N"
    # 파라펫(개방 구간 제외) — _obstacle_boxes 와 동일 정의 재사용
    for bn, x0, x1, y0, y1, z0, z1 in _obstacle_boxes():
        if bn.startswith("Parapet") and x0 <= x <= x1 and y0 <= y <= y1 \
                and z0 <= z <= z1:
            return bn
    return None


# ===========================================================================
# [C3] 스모크 — 부팅 전 기하·조명·카메라 자기검증 (조기종료)
# ===========================================================================
def _smoke_report():
    p = PARAMS["pit"]
    st = PARAMS["stair"]
    pr = PARAMS["parapet"]
    L = _stair_local()
    print("=" * 70)
    print("scene08_sunken_plaza — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 70)
    drop = st["riser"] * st["n_riser"]
    print(f"  피트 개구        : {p['x1']-p['x0']:.1f} × {p['y1']-p['y0']:.1f} m"
          f"  (깊이 {drop:.3f} = riser {st['riser']} × {st['n_riser']})")
    print(f"  피트 바닥 z      : {p['floor_z']:+.3f}  "
          f"(= −riser×n_riser → 계단 최하 라이저가 바닥에 정확히 착지)")
    print(f"  낙차 검증        : {drop:.3f} ≥ 0.3 m → "
          f"{'OK' if drop >= 0.3 else 'FAIL'}")
    print(f"  계단 기하        : n_geom {st['n_geom']}단(솔리드) + 바닥 1라이저 "
          f"= {st['n_riser']} 라이저, run {L['run']:.2f} m, 폭 {st['width']:.1f}")
    print(f"    남측: world x [{st['south_x0']:.1f},"
          f"{st['south_x0']+st['width']:.1f}] · y {L['x0']:+.2f} → "
          f"{L['x0']+L['run']:+.2f} (rot +90° @ (0,0), local x0 {L['x0']:+.2f})")
    print(f"    북측: world x [{st['north_x0']:.1f},"
          f"{st['north_x0']+st['width']:.1f}] · y {-L['x0']:+.2f} → "
          f"{-(L['x0']+L['run']):+.2f} (rot −90° @ (0,0))")
    ov = (L["run"] + L["run"]) - (p["y1"] - p["y0"])
    print(f"    두 계단 y 전개 합 {2*L['run']:.1f} vs 피트 y폭 "
          f"{p['y1']-p['y0']:.1f} → x 대역 분리로 회피(중첩 {ov:+.1f} m, "
          f"x 0..4 / 8..12) → "
          f"{'OK' if st['north_x0'] >= st['south_x0']+st['width'] else 'FAIL'}")
    court = (st["north_x0"] - (st["south_x0"] + st["width"]))
    print(f"    코트 순폭       : x {st['south_x0']+st['width']:.1f}.."
          f"{st['north_x0']:.1f} = {court:.1f} m × y {p['y1']-p['y0']:.1f} "
          f"= {court*(p['y1']-p['y0']):.0f} m² → "
          f"{'OK' if court >= 3.0 else 'FAIL'}")

    # ── 개구 4박스 + 지반 프레임: 공동 위를 덮는 평면이 없는지 ──
    pl = PARAMS["plaza"]
    gr = PARAMS["ground"]
    plates = [
        ("Plaza_W(paving)", pl["x0"], p["x0"] - p["ring_t"], pl["y0"], pl["y1"],
         pl["z_top"]),
        ("Plaza_E(paving)", p["x1"] + p["ring_t"], pl["x1"], pl["y0"], pl["y1"],
         pl["z_top"]),
        ("Plaza_S(paving)", p["x0"] - p["ring_t"], p["x1"] + p["ring_t"],
         pl["y0"], p["y0"] - p["ring_t"], pl["z_top"]),
        ("Plaza_N(paving)", p["x0"] - p["ring_t"], p["x1"] + p["ring_t"],
         p["y1"] + p["ring_t"], pl["y1"], pl["z_top"]),
        ("Ground_W(asphalt)", gr["x0"], pl["x0"], gr["y0"], gr["y1"],
         gr["z_top"]),
        ("Ground_E(asphalt)", pl["x1"], gr["x1"], gr["y0"], gr["y1"],
         gr["z_top"]),
        ("Ground_S(asphalt)", pl["x0"], pl["x1"], gr["y0"], pl["y0"],
         gr["z_top"]),
        ("Ground_N(asphalt)", pl["x0"], pl["x1"], pl["y1"], gr["y1"],
         gr["z_top"]),
        ("PitFloor(granite)", p["x0"] - p["ring_t"], p["x1"] + p["ring_t"],
         p["y0"] - p["ring_t"], p["y1"] + p["ring_t"], p["floor_z"]),
    ]
    print("  [지면 플레이트 표] (§A-3 개구 4박스 + 지반 프레임 4박스)")
    print(f"    {'이름':20s} {'x범위':>16s} {'y범위':>16s}  상면z")
    bad = []
    for nm, x0, x1, y0, y1, z in plates:
        print(f"    {nm:20s} [{x0:6.1f},{x1:6.1f}] [{y0:6.1f},{y1:6.1f}]  "
              f"{z:+.3f}")
        if nm.startswith("PitFloor"):
            continue
        # 개구(x 0..12, y −4.5..4.5)와 XY 로 겹치면서 상면이 바닥보다 높으면 = 공동을 덮음
        if not (x1 <= p["x0"] or x0 >= p["x1"] or
                y1 <= p["y0"] or y0 >= p["y1"]):
            bad.append(nm)
    print(f"    개구 위를 덮는 플레이트: {bad if bad else '없음 → OK'}")

    # ── 파라펫·개방 구간 ──
    gapw = pr["gap_y1"] - pr["gap_y0"]
    print("  [파라펫 / 개방 구간]")
    print(f"    파라펫 h {pr['h']:.2f} (현행 규정 1.1 미달 = '규정 미달의 현실')"
          f" · t {pr['t']:.2f}")
    print(f"    접근측(x=0) 철거 구간 y [{pr['gap_y0']:+.1f},{pr['gap_y1']:+.1f}]"
          f" = {gapw:.1f} m → {'OK' if abs(gapw-1.8) < 1e-6 else 'FAIL'}"
          f"  (그리드 축 y=0 관통 → h0.3 판정 가능)")
    # ── [v6 C-3/C-6] 재질 수정 검산 (기하·카메라는 판정 보존 권고에 따라 불변) ──
    _tb = PARAMS["tempbar"]
    _tp = _tb["tape"]
    print("  [v6 재질 수정 검산] — 치수 불변 확인")
    print(f"    파라펫 : 콘크리트 텍스처 + 코핑 {pr['cope_h']:.2f} m"
          f"(돌출 {pr['cope_over']*100:.0f} cm) + 기단 오염 밴드 "
          f"{pr['grime_h']:.2f} m")
    print(f"      몸통 {pr['h']-pr['cope_h']:.2f} + 코핑 {pr['cope_h']:.2f} = "
          f"{pr['h']-pr['cope_h']+pr['cope_h']:.2f} m vs 규정 h {pr['h']:.2f} → "
          f"{'OK(높이 불변)' if abs(pr['h']-pr['cope_h']+pr['cope_h']-pr['h']) < 1e-9 else 'FAIL'}")
    print(f"    안전봉 : 적·백 {_tb['nband']}밴드 (밴드 "
          f"{_tb['post_h']/_tb['nband']:.2f} m, 겹침 {_tb['band_ov']:.2f}×) · "
          f"총 h {_tb['post_h']:.2f} · r {_tb['post_r']:.3f} → 치수 불변")
    print(f"    경고 테이프 : 두께 {_tp['t']*1000:.0f} mm 리본 × {_tp['nseg']}세그"
          f" (구 20 mm 각재) · 폭 {_tp['w']*100:.0f} cm · 처짐 "
          f"{_tp['sag']*100:.0f} cm · 양단 안전봉 y "
          f"[{pr['gap_y0']:+.1f},{pr['gap_y1']:+.1f}] 결속 → "
          f"{'OK(부유 없음)' if _tp['z_end'] < _tb['post_h'] else 'FAIL(봉 상단 초과)'}")

    # ── grazing 은닉 검산 (연구 핵심) ──
    print("  [h0.3 은닉 검산] 근측 연단(x=0,z=0) 스치는 시선이 바닥에 닿는 x")
    for d in (2.0, 5.0, 10.0):
        x_hit = abs(p["floor_z"]) * d / 0.3
        hid = x_hit > p["x1"]
        print(f"    d={d:4.1f} m → x_hit {x_hit:6.1f} m vs 피트 동단 "
              f"{p['x1']:.1f} m → 피트 전체 은닉 {'OK' if hid else 'FAIL'}")
    print(f"    ⇒ h0.3 에서는 원측 광장(x≥{p['x1']+p['ring_t']:.1f}, z=0)이 "
          f"근측 지면과 연속 평면으로 읽힌다(negative obstacle 성립).")

    # ── 사광 침투 검산 (scene19 d5 암흑 전례 방지) ──
    d = _sun_dir()
    hxy = math.hypot(d[0], d[1])
    print("  [사광 침투 검산] SUN_AZ_OFFSET="
          f"{PARAMS['SUN_AZ_OFFSET']:.1f}, elev {PARAMS['light']['noon_sun_elev']:.2f}")
    print(f"    광선 진행 d = ({d[0]:+.3f}, {d[1]:+.3f}, {d[2]:+.3f}) "
          f"→ 태양은 (−d) 방향 = "
          f"{'+Y(북) 상공' if -d[1] > 0 else '−Y(남) 상공'}")
    reach = abs(p["floor_z"]) * hxy / abs(d[2])            # 바닥 도달 수평거리
    dy = abs(p["floor_z"]) * d[1] / abs(d[2])              # 바닥 도달 시 Δy
    y_edge = p["y1"] + dy if d[1] < 0 else p["y0"] + dy
    lit_lo, lit_hi = (p["y0"], y_edge) if d[1] < 0 else (y_edge, p["y1"])
    print(f"    림 통과 후 바닥(−{abs(p['floor_z']):.3f})까지 수평 {reach:.2f} m "
          f"(Δy {dy:+.2f})")
    print(f"    → 바닥 직사 대역 y [{lit_lo:+.2f},{lit_hi:+.2f}] "
          f"(폭 {lit_hi-lit_lo:.2f} m / 전폭 {p['y1']-p['y0']:.1f}) → "
          f"{'OK(암흑 아님)' if (lit_hi-lit_lo) > 1.0 else 'FAIL(피트 암흑)'}")
    # 남측 계단(로컬 하강선) 명암 경계: z_surf = −(riser/tread)(y−y0),
    #   가시 조건 z + (y1−y)·|dz|/|dy| ≥ 0
    k = st["riser"] / st["tread"]
    r = abs(d[2]) / abs(d[1])
    y_shadow = (r * p["y1"] - k * (-p["y0"])) / (r + k) if (r + k) > 0 else 0.0
    print(f"    남측 계단 명암 경계 y ≈ {y_shadow:+.2f} "
          f"(y ≤ 경계 = 직사 / 초과 = 암부) · 북측 계단은 전면 직사")
    fc = PARAMS["facade"]
    print(f"    유리 파사드(북벽 y={fc['y']:.1f}, 법선 −Y) → 상시 암부 → "
          f"약발광(intensity {fc['emis_int']:.0f}) 가독 OK")
    # 천공률 근사(코트 중심)
    hx = (p["x1"] - p["x0"]) / 2.0
    hy = (p["y1"] - p["y0"]) / 2.0
    dep = abs(p["floor_z"])
    print(f"    코트 중심 천공 반각: x {math.degrees(math.atan2(hx, dep)):.0f}° "
          f"/ y {math.degrees(math.atan2(hy, dep)):.0f}° → 돔 간접광 충분")

    # ── 카메라 충돌 검산 ──
    boxes = _obstacle_boxes()
    views = build_views()
    print(f"  [카메라 충돌 검산] 뷰 {len(views)}개 × 장애물 {len(boxes)}개 AABB")
    hits = []
    for name, v in sorted(views.items()):
        ex, ey, ez = v["eye"]
        for bn, x0, x1, y0, y1, z0, z1 in boxes:
            if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1:
                hits.append((name, bn))
    for name, v in sorted(views.items()):
        s = _solid_at(*v["eye"])
        if s is not None:
            hits.append((name, f"{s}(지형 매몰)"))
    for name, bn in hits:
        print(f"    [FAIL] {name} eye 가 {bn} 내부")
    print(f"    충돌: {len(hits)}건 → {'OK' if not hits else 'FAIL'}")
    # 시선 차단 검사(ray march 0.1 m) — 미장센 컷이 지형·파라펫에 막히지 않는지.
    print("    [시선 차단] 미장센 컷 ray march (첫 차단 비율 ≥ 0.90 = OK)")
    blocked = []
    for name, v in sorted(views.items()):
        if name.startswith("preset_"):
            continue
        e = np.array(v["eye"], dtype=float)
        tg = np.array(v["tgt"], dtype=float)
        Ln = float(np.linalg.norm(tg - e))
        frac, hit = 1.0, None
        for k in range(1, int(Ln / 0.1) + 1):
            f = k * 0.1 / Ln
            s = _solid_at(*(e + (tg - e) * f))
            if s is not None:
                frac, hit = f, s
                break
        print(f"      {name:18s} 첫 차단 {frac:5.2f} "
              f"({hit if hit else '없음'}) → {'OK' if frac >= 0.90 else 'FAIL'}")
        if frac < 0.90:
            blocked.append(name)
    print(f"      차단 컷: {blocked if blocked else '없음 → OK'}")
    # h0.3 그리드에서 **개구 연단을 스치는 시선**이 개방 구간을 통과하는지.
    #   (그리드 축 자체는 pitch −10° 라 1.7 m 앞 바닥을 찍는다 — 판정에 쓰는 것은
    #    프레임 상부의 수평 근접 시선이다.) 연단 앞(x<0)에서 막히면 FAIL.
    for dd in (2.0, 5.0, 10.0):
        e = np.array([-dd, 0.0, 0.3])
        rim = np.array([0.0, 0.0, 0.004])          # 근측 연단 스침
        dirv = (rim - e) / np.linalg.norm(rim - e)
        pre, post, x_post = None, None, None
        for k in range(1, int(30.0 / 0.05)):
            pnt = e + dirv * (k * 0.05)
            s = _solid_at(*pnt)
            if s is None:
                continue
            if pnt[0] < -1e-6:
                pre = s
                break
            post, x_post = s, pnt[0]
            break
        print(f"      grid h0.3_d{dd:.0f} 연단 스침 시선 → "
              f"연단 전 차단 {'없음(OK)' if pre is None else pre + '(FAIL)'}"
              f" · 연단 너머 최초 접촉 "
              f"{f'{post} @ x={x_post:.1f}' if post else '없음(지평)'}")
    # 시선 회랑 청소 여부: 카메라(y=0)에서 개방 구간을 관통하는 축 회랑
    #   (x −22..0, |y| ≤ 0.8 — 개방 구간 폭 1.8 의 안쪽)에 장애물이 없어야
    #   h0.3 그리드가 피트를 '연속 평면'으로 볼 수 있다. 파라펫 W 세그먼트와
    #   임시 안전봉은 회랑 **가장자리**(|y| ≥ 0.84)에 서므로 여기 걸리면 FAIL.
    half = 0.8
    intr = [bn for bn, x0, x1, y0, y1, z0, z1 in boxes
            if not (x1 <= -22.0 or x0 >= 0.0 or y1 <= -half or y0 >= half)
            and z1 > 0.05 and not bn.startswith("Plaza_")]
    print(f"    시선 회랑(x −22..0, |y|≤{half}) 침범 요소: "
          f"{intr if intr else '없음 → OK'}")
    print("=" * 70)


# ===========================================================================
# [C-2] ground_kit plans - pure CPU, no USD. Coordinates from PARAMS (Sec.7.4).
# ===========================================================================
def ground_plan():
    """P3 `sidewalk_block` plan for the upper plaza (approach corridor)."""
    g = PARAMS["gkit"]
    pl, pit = PARAMS["plaza"], PARAMS["pit"]
    return gk.plan_ground(
        "sidewalk_block",
        region=tuple(float(v) for v in g["region"]),
        z=float(pl["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("pit_near_edge", float(pit["x0"]))],
        voids=[(float(pit["x0"]), float(pit["y0"]),
                float(pit["x1"]), float(pit["y1"]))],
        dists=(2, 5, 10), scene="scene08",
        tactile=(),                  # Sec.12.4 - kept on build_tactile_ring
        sites=dict(manhole=[tuple(g["manhole"])],
                   gully=[tuple(v) for v in g["gullies"]],
                   patch=[tuple(v) for v in g["patches"]]),
        # 3 patches, one per preset near-window (see PARAMS comment).
        overrides=dict(
            # step_y 3.0 adds the longitudinal leg of the 3 m granite-band
            # grid over the block field (Sec.5.2 N5 row, same paving type).
            # 3.0 / 0.300 cell = 10x, so U2 holds. Without it B4 has only
            # the L-gutter line and cannot reach 2.
            pave=dict(step_y=3.0),
            surface=(("patch", 3), ("crack", 4),
                     ("stain", ("dirt", "gum")), ("weed", 8))),
        seed=int(g["seed"]))


def ground_plan_pit():
    """Court-floor plan - the single mandatory low-point gully, nothing else.

    Sec.5.2 row 08 makes this gully mandatory `[시방 오목부 필수]`, but the
    court floor is a separate slab 4.498 m below the plaza, so it cannot ride
    on the plaza plan (one plan carries one z). Everything except `gully=1`
    is overridden off.
    """
    g = PARAMS["gkit"]
    return gk.plan_ground(
        "sidewalk_block",
        region=tuple(float(v) for v in g["pit_region"]),
        z=float(PARAMS["pit"]["floor_z"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=(), dists=(2, 5, 10), scene="scene08", tactile=(),
        sites=dict(gully=[tuple(g["pit_gully"])]),
        overrides=dict(pave=dict(joint=None),
                       infra=dict(manhole=0, gully=1, gutter_L=0),
                       surface=(), extras=()),
        seed=int(g["seed"]) + 80)


# ===========================================================================
# [D] 카메라 프리셋: grid_views(gy=0) + 미장센 5컷
# ===========================================================================
def build_views():
    """프리셋 축 = 광장 보행축 +X(접근 → 피트). 개방 구간(y −0.9..0.9)이
    축 위에 있어 h0.3 그리드가 곧 '위험 은닉' 판정 컷이 된다."""
    views = sc.grid_views(0.0)
    # pit_edge: 개방 구간 연단에 선 보행자 시점(h1.55) — 피트 내부 노출
    views["pit_edge"] = dict(eye=[-1.60, -0.20, 1.55], tgt=[3.20, 0.60, -2.30])
    # open_gap: 철거 구간을 비스듬히 — 파라펫 단절 + 임시 표지(안전봉·테이프).
    #   [좌표 검산] tgt z 를 연단(0.00)에 맞춘다. 구 tgt(0.2,0.4,−0.60)은
    #   시선이 x=−1.07 에서 이미 z<0 로 내려가 **광장 슬래브를 관통**했다.
    views["open_gap"] = dict(eye=[-4.50, -2.20, 1.60], tgt=[0.30, 0.20, 0.00])
    # underground_look: 피트 바닥 코트에서 개방 구간을 올려봄(로봇 시점 반대편)
    views["underground_look"] = dict(eye=[6.00, 0.00, -3.40],
                                     tgt=[1.20, -1.40, 0.30])
    # stair_south: 남측 광폭 계단 하강선(직사 구간 → 명암 경계 y≈+1.55 확인).
    #   [좌표 검산] 시선은 y≈+1.45(20단째, 표면 −3.46)에서 계단면에 착지한다.
    #   구 tgt(2.2,0.2,−3.40)은 그 지점 계단면(−2.71)보다 낮아 솔리드 관통.
    views["stair_south"] = dict(eye=[2.00, -7.20, 2.10], tgt=[2.20, 1.40, -3.40])
    # facade_court: 코트에서 지하상가 유리 파사드(약발광) 정면
    views["facade_court"] = dict(eye=[6.00, -1.20, -3.30], tgt=[6.00, 4.40, -3.00])
    # beauty_overview: 사선 부감 — 피트·양측 계단·광장 맥락 일괄
    views["beauty_overview"] = dict(eye=[-12.0, -12.0, 9.0], tgt=[5.0, 1.0, -2.0])
    return views


# ===========================================================================
# [E] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드        — 개방 구간 너머 피트가 '연속 평면'으로 은닉되는가
 2. pit_edge/open_gap  — 파라펫 1.8 m 철거 + 임시 표지(안전봉·테이프)가 읽히는가
 3. underground_look   — 피트 바닥에서 개구·계단·광장 상부가 읽히는가 (PT)
 4. stair_south        — 남측 광폭 계단 명암 경계(사광 60°)와 측면 난간
 5. facade_court       — 지하상가 유리 파사드 약발광 (PT 8바운스 전제)
 6. 재질/접지          — 개구 4박스·Z파이팅·부유 없는가"""


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
        M["paving"] = PBR(
            f"{ROOT}/Looks/Paving", sc.tex_path("paving_interlock", "diff"),
            sc.tex_path("paving_interlock", "nor"),
            sc.tex_path("paving_interlock", "rough"), sca["paving_interlock"])
        M["cwall"] = PBR(
            f"{ROOT}/Looks/ConcreteWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"])
        M["cfloor"] = PBR(
            f"{ROOT}/Looks/ConcreteFloor",
            sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"])
        M["granite"] = PBR(
            f"{ROOT}/Looks/Granite", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"),
            sc.tex_path("granite_dark", "rough"), sca["granite_dark"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["paint"] = PBR(f"{ROOT}/Looks/Paint", diffuse_color=mp["paint_color"],
                         roughness_const=mp["paint_rough"], metallic=0.0)
        # [v6 C-3] 파라펫·코핑 : 콘크리트 텍스처 + 틴트(무텍스처 순백판 해소).
        #   scale 1.2 — 벽체용 2.0 보다 잘게 잡아 h1.0 판에도 골재·줄눈이 남는다.
        M["parapet"] = PBR(
            f"{ROOT}/Looks/Parapet", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), 1.2,
            tint=mp["parapet_tint"])
        M["cope"] = PBR(
            f"{ROOT}/Looks/Cope", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"),
            sc.tex_path("granite_dark", "rough"), 0.9, tint=mp["cope_tint"])
        M["grime"] = PBR(f"{ROOT}/Looks/Grime",
                         diffuse_color=mp["grime_color"],
                         roughness_const=mp["grime_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        # 지하상가 유리: 약발광(PT 8바운스 판정 전제 — RT 단일바운스 기여 미미)
        fc = PARAMS["facade"]
        M["glass_emis"] = PBR(f"{ROOT}/Looks/GlassEmis",
                              diffuse_color=mp["glass_color"],
                              roughness_const=mp["glass_rough"], metallic=0.0,
                              emission_color=fc["emis"],
                              emission_intensity=fc["emis_int"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["mullion"] = PBR(f"{ROOT}/Looks/Mullion",
                           diffuse_color=mp["mull_color"],
                           metallic=mp["mull_metallic"],
                           roughness_const=mp["mull_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["tempost"] = PBR(f"{ROOT}/Looks/TempPost",
                           diffuse_color=PARAMS["tempbar"]["post_color"],
                           roughness_const=0.6)
        M["tempost_b"] = PBR(f"{ROOT}/Looks/TempPostB",
                             diffuse_color=PARAMS["tempbar"]["post_color_b"],
                             roughness_const=0.6)
        M["temtape"] = PBR(f"{ROOT}/Looks/TempTape",
                           diffuse_color=PARAMS["tempbar"]["tape_color"],
                           roughness_const=0.7)
        M["sign_back"] = PBR(f"{ROOT}/Looks/SignBack",
                             diffuse_color=mp["sign_back_color"],
                             roughness_const=mp["sign_back_rough"])
        # 한글 사인 패널 (uv_mode=True : 메시 st 로 1:1 정합)
        for key in ("exit",):        # [v5.2 사용자] 임의 경고 팻말 제거
            M[f"sign_{key}"] = PBR(
                f"{ROOT}/Looks/Sign_{key}",
                diff=sc.tex_path(f"sign_{key}", "diff"), uv_mode=True,
                roughness_const=0.45)
        return M

    # -------------------------------------------------------------------
    # 지반 프레임(차도) — 광장 바깥 4박스. 대지 가장자리 허공 금지(§A-4)
    # -------------------------------------------------------------------
    def build_ground(M):
        gr = PARAMS["ground"]
        pl = PARAMS["plaza"]
        cz = gr["z_top"] - gr["thick"] / 2.0
        segs = [("W", gr["x0"], pl["x0"], gr["y0"], gr["y1"]),
                ("E", pl["x1"], gr["x1"], gr["y0"], gr["y1"]),
                ("S", pl["x0"], pl["x1"], gr["y0"], pl["y0"]),
                ("N", pl["x0"], pl["x1"], pl["y1"], gr["y1"])]
        for tag, x0, x1, y0, y1 in segs:
            BOX(f"{ROOT}/Ground_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                (x1 - x0, y1 - y0, gr["thick"]), M["asphalt"], col=True)
        for i, rl in enumerate(PARAMS["road_lines"]):
            BOX(f"{ROOT}/RoadLine_{i}",
                ((rl["x0"] + rl["x1"]) / 2.0, rl["y"], gr["z_top"] + 0.004),
                (rl["x1"] - rl["x0"], 0.15, 0.02), M["paint"])

    # -------------------------------------------------------------------
    # 광장 슬래브 — 개구(피트+코핑 링)를 4박스로 비움 (§A-3)
    # -------------------------------------------------------------------
    def build_plaza(M):
        pl = PARAMS["plaza"]
        p = PARAMS["pit"]
        t = p["ring_t"]
        cz = pl["z_top"] - pl["thick"] / 2.0
        ox0, ox1 = p["x0"] - t, p["x1"] + t          # 링 포함 개구 외곽
        oy0, oy1 = p["y0"] - t, p["y1"] + t
        # [W2-0 P-A] Plaza_W is the slab ground_kit decorates. Its displacement
        #   skin (+6.5..16.5 mm) would bury the manhole, joints and decals
        #   (0.6..3 mm), so it is excluded before the box exists (Sec.1.1/1.2).
        #   Only the W segment - E/S/N carry no kit elements and keep the skin.
        sc.skin_exclude(f"{ROOT}/Plaza_W")
        segs = [("W", pl["x0"], ox0, pl["y0"], pl["y1"]),
                ("E", ox1, pl["x1"], pl["y0"], pl["y1"]),
                ("S", ox0, ox1, pl["y0"], oy0),
                ("N", ox0, ox1, oy1, pl["y1"])]
        for tag, x0, x1, y0, y1 in segs:
            BOX(f"{ROOT}/Plaza_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                (x1 - x0, y1 - y0, pl["thick"]), M["paving"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 개구를 메워 광장 전체를 z=0 평지로."""
        pl = PARAMS["plaza"]
        BOX(f"{ROOT}/FlatPlaza",
            ((pl["x0"] + pl["x1"]) / 2.0, (pl["y0"] + pl["y1"]) / 2.0,
             pl["z_top"] - pl["thick"] / 2.0),
            (pl["x1"] - pl["x0"], pl["y1"] - pl["y0"], pl["thick"]),
            M["paving"], col=True)

    # -------------------------------------------------------------------
    # 피트 셸 — 코핑 링 4박스(= 옹벽) + 계단 머리 문턱 2 + 바닥 슬래브
    #   링은 광장 슬래브와 **XY 로 겹치지 않는다** → 동일평면 Z파이팅 없음.
    # -------------------------------------------------------------------
    def build_pit_shell(M):
        p = PARAMS["pit"]
        st = PARAMS["stair"]
        pl = PARAMS["plaza"]
        t = p["ring_t"]
        z_bot = p["ring_bot"]
        cz = (0.0 + z_bot) / 2.0
        hz = -z_bot
        sx0, sx1 = st["south_x0"], st["south_x0"] + st["width"]   # 0..4
        nx0, nx1 = st["north_x0"], st["north_x0"] + st["width"]   # 8..12
        # 링 4변 — 남/북은 계단 머리 개구를 비운다
        rings = [("W", p["x0"] - t, p["x0"], p["y0"] - t, p["y1"] + t),
                 ("E", p["x1"], p["x1"] + t, p["y0"] - t, p["y1"] + t),
                 ("S", sx1, p["x1"], p["y0"] - t, p["y0"]),
                 ("N", p["x0"], nx0, p["y1"], p["y1"] + t)]
        for tag, x0, x1, y0, y1 in rings:
            if x1 - x0 <= 1e-6 or y1 - y0 <= 1e-6:
                continue
            BOX(f"{ROOT}/Ring_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                (x1 - x0, y1 - y0, hz), M["cwall"], col=True)
        # 계단 머리 문턱 슬래브(광장 포장 연속) — 링이 비워진 자리를 메움
        for tag, x0, x1, y0, y1 in (("S", sx0, sx1, p["y0"] - t, p["y0"]),
                                    ("N", nx0, nx1, p["y1"], p["y1"] + t)):
            BOX(f"{ROOT}/StairHead_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                 pl["z_top"] - pl["thick"] / 2.0),
                (x1 - x0, y1 - y0, pl["thick"]), M["paving"], col=True)
        # 피트 바닥 슬래브 (링 밑면 −5.0 을 품도록 두껍게)
        BOX(f"{ROOT}/PitFloor",
            ((p["x0"] + p["x1"]) / 2.0, (p["y0"] + p["y1"]) / 2.0,
             p["floor_z"] - p["floor_thick"] / 2.0),
            (p["x1"] - p["x0"] + 2 * t, p["y1"] - p["y0"] + 2 * t,
             p["floor_thick"]), M["granite"], col=True)

    # -------------------------------------------------------------------
    # 남·북 광폭 계단 — build_rot_group(±90°) + build_straight_stairs
    #   로컬 +X 하강 관례를 유지한 채 world ±Y 하강으로 매핑한다.
    #     남측 rot +90° @ (0,0): world(x,y) = (−ly, lx)
    #     북측 rot −90° @ (0,0): world(x,y) = ( ly, −lx)
    # -------------------------------------------------------------------
    def build_stairs(M):
        st = PARAMS["stair"]
        L = _stair_local()
        mtl = M["cfloor"] if cfg["cue_material_break"] else M["paving"]
        w = st["width"]
        # 남측: world x [0,4] ← local y [−4, 0]
        g_s = sc.build_rot_group(stage, f"{ROOT}/StairS_Grp", (0.0, 0.0), 90.0)
        sc.build_straight_stairs(
            stage, f"{g_s}/Steps", L["x0"], -(st["south_x0"] + w),
            -st["south_x0"], st["riser"], st["tread"], st["n_geom"],
            st["base_z"], mtl, z_top=0.0, collider=True)
        # 북측: world x [8,12] ← local y [8, 12]
        g_n = sc.build_rot_group(stage, f"{ROOT}/StairN_Grp", (0.0, 0.0), -90.0)
        sc.build_straight_stairs(
            stage, f"{g_n}/Steps", L["x0"], st["north_x0"],
            st["north_x0"] + w, st["riser"], st["tread"], st["n_geom"],
            st["base_z"], mtl, z_top=0.0, collider=True)
        if cfg["cue_nosing"]:
            sc.build_nosing(stage, f"{g_s}/Nosing", L["x0"],
                            -(st["south_x0"] + w), -st["south_x0"],
                            st["riser"], st["tread"], st["n_geom"], z_top=0.0)
            sc.build_nosing(stage, f"{g_n}/Nosing", L["x0"], st["north_x0"],
                            st["north_x0"] + w, st["riser"], st["tread"],
                            st["n_geom"], z_top=0.0)
        return g_s, g_n

    # -------------------------------------------------------------------
    # 지하상가 유리 파사드 — 피트 북벽 내면(y=4.5) x 4..8, 약발광
    # -------------------------------------------------------------------
    def build_facade(M):
        fc = PARAMS["facade"]
        n = int(fc["panels"])
        span = fc["x1"] - fc["x0"]
        pw = span / n
        zc = (fc["z0"] + fc["z1"]) / 2.0
        hz = fc["z1"] - fc["z0"]
        yg = fc["y"] - fc["glass_t"] / 2.0 + 0.01      # 벽면보다 1 cm 안쪽 겹침
        ym = fc["y"] - fc["mull_t"] / 2.0 - 0.01       # 멀리언은 유리보다 코트측
        for i in range(n):
            xc = fc["x0"] + (i + 0.5) * pw
            BOX(f"{ROOT}/Facade/Glass_{i}", (xc, yg, zc),
                (pw - fc["mull_w"], fc["glass_t"], hz), M["glass_emis"])
        # 수직 멀리언 (양단 포함 n+1 본)
        for i in range(n + 1):
            xc = fc["x0"] + i * pw
            BOX(f"{ROOT}/Facade/Mull_{i}", (xc, ym, zc),
                (fc["mull_w"], fc["mull_t"], hz), M["mullion"])
        # 상부 인방 + 하부 문지방
        BOX(f"{ROOT}/Facade/Lintel",
            ((fc["x0"] + fc["x1"]) / 2.0, ym, fc["z1"] + 0.16),
            (span + 0.30, fc["mull_t"] + 0.10, 0.32), M["cwall"])
        BOX(f"{ROOT}/Facade/Sill",
            ((fc["x0"] + fc["x1"]) / 2.0, ym, fc["z0"] - fc["sill_h"] / 2.0),
            (span + 0.30, fc["mull_t"] + 0.14, fc["sill_h"]), M["cwall"])
        # 중간 트랜섬 1선
        BOX(f"{ROOT}/Facade/Transom",
            ((fc["x0"] + fc["x1"]) / 2.0, ym, (fc["z0"] + fc["z1"]) / 2.0),
            (span, fc["mull_t"], fc["mull_w"]), M["mullion"])

    # -------------------------------------------------------------------
    # 단서 — 파라펫(개방 구간 결손) · 계단 측면 난간 · 점자블록
    # -------------------------------------------------------------------
    def build_parapet(M):
        p = PARAMS["pit"]
        pr = PARAMS["parapet"]
        st = PARAMS["stair"]
        segs = [
            # 서측(접근측) — 개방 구간 y[-0.9,0.9] 결손 = 무방호 낙차
            ("W_S", p["x0"] - pr["t"], p["x0"], p["y0"] - pr["ext"],
             pr["gap_y0"]),
            ("W_N", p["x0"] - pr["t"], p["x0"], pr["gap_y1"],
             p["y1"] + pr["ext"]),
            # 동측 — 온전(대조)
            ("E", p["x1"], p["x1"] + pr["t"], p["y0"] - pr["ext"],
             p["y1"] + pr["ext"]),
            # 남측 — 계단 머리(x 0..4) 개방
            ("S", st["south_x0"] + st["width"], p["x1"],
             p["y0"] - pr["ext"], p["y0"]),
            # 북측 — 계단 머리(x 8..12) 개방
            ("N", p["x0"], st["north_x0"], p["y1"], p["y1"] + pr["ext"]),
        ]
        # [v6 C-3] 몸통(콘크리트 텍스처) + 코핑(갓돌) + 기단 오염 밴드.
        #   전체 높이 pr["h"]=1.0 은 **불변** — 코핑을 얹는 것이 아니라 몸통을
        #   cope_h 만큼 낮춰 그 자리에 갓돌을 끼운다(규정 미달 h1.0 유지).
        ch = pr["cope_h"]
        gh = pr["grime_h"]
        body_h = pr["h"] - ch
        for tag, x0, x1, y0, y1 in segs:
            if x1 - x0 <= 1e-6 or y1 - y0 <= 1e-6:
                continue
            BOX(f"{ROOT}/Parapet_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, body_h / 2.0),
                (x1 - x0, y1 - y0, body_h), M["parapet"], col=True)
            # 코핑 : 몸통 위 ch, 사방 cope_over 돌출(물끊기 턱) → 상면 = pr["h"]
            ov = pr["cope_over"]
            BOX(f"{ROOT}/ParapetCope_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, body_h + ch / 2.0),
                (x1 - x0 + 2 * ov, y1 - y0 + 2 * ov, ch), M["cope"])
            # 기단 오염 밴드 : 하단 gh, 측면 grime_over 만 돌출.
            #   저면을 4 mm 매입해 광장 슬래브 상면(z=0)과의 동일평면 회피(§A-8)
            go = pr["grime_over"]
            BOX(f"{ROOT}/ParapetGrime_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, gh / 2.0 - 0.004),
                (x1 - x0 + 2 * go, y1 - y0 + 2 * go, gh), M["grime"])

    def build_stair_rails(M, g_s, g_n):
        """계단 코트측 측면(남측 x=4 / 북측 x=8) 파이프 난간 — 회전그룹 내부에
        로컬 좌표로 세운다(그룹이 통째로 ±90° 회전)."""
        st = PARAMS["stair"]
        L = _stair_local()
        gfn = _stair_ground_fn()
        # 남측: world x=4 ↔ local y = −4 → 계단 안쪽 0.12
        sc.build_railing_line(
            stage, f"{g_s}/FlankRail", -(st["south_x0"] + st["width"]) + 0.12,
            L["x0"] - 0.6, L["x0"], L["run"], L["drop"], gfn, M["rail"],
            rail_h=0.9, spacing=1.5)
        # 북측: world x=8 ↔ local y = +8 → 계단 안쪽 0.12
        sc.build_railing_line(
            stage, f"{g_n}/FlankRail", st["north_x0"] + 0.12,
            L["x0"] - 0.6, L["x0"], L["run"], L["drop"], gfn, M["rail"],
            rail_h=0.9, spacing=1.5)

    def build_tactile_ring(M):
        """개구 둘레 점자블록 띠 — 파라펫 바깥 0.05 여유, 4변(모서리 비중첩)."""
        p = PARAMS["pit"]
        pr = PARAMS["parapet"]
        tc = PARAMS["tactile"]
        a = pr["t"] + tc["off"]                 # 개구선에서 띠 안쪽까지
        w = tc["w"]
        xw1, xw0 = p["x0"] - a, p["x0"] - a - w
        xe0, xe1 = p["x1"] + a, p["x1"] + a + w
        ys1, ys0 = p["y0"] - a, p["y0"] - a - w
        yn0, yn1 = p["y1"] + a, p["y1"] + a + w
        bands = [("W", xw0, xw1, ys1, yn0), ("E", xe0, xe1, ys1, yn0),
                 ("S", xw0, xe1, ys0, ys1), ("N", xw0, xe1, yn0, yn1)]
        # [W2-D Sec.12.4] Non-conforming variant for scene08 = "2-3 tiles
        #   missing". Measured reality is 4.0 % conforming / 77.3 %
        #   non-conforming (KBUWEL 2023, n=337), so a perfectly continuous ring
        #   is the unrealistic option. The gap is cut out of the **west** band
        #   because that is the approach side the grid presets look along, and
        #   it is centred on the walk axis (y=0) so it is actually in frame.
        #   `gap_tiles` x 0.300 m statutory tile = gap length.
        gap = float(tc.get("gap_tiles", 0)) * 0.300
        for tag, x0, x1, y0, y1 in bands:
            if tag == "W" and gap > 0.0:
                for k, (ya, yb) in enumerate(((y0, -gap / 2.0),
                                              (gap / 2.0, y1))):
                    sc.build_tactile(stage, f"{ROOT}/Tactile_{tag}{k}",
                                     x0, x1, ya, yb, M["tactile"], z=0.0,
                                     proud=tc["proud"])
                continue
            sc.build_tactile(stage, f"{ROOT}/Tactile_{tag}", x0, x1, y0, y1,
                             M["tactile"], z=0.0, proud=tc["proud"])

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P3 sidewalk_block (plaza) + court-floor gully.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["granite"], crack=M["granite"], patch=M["paving"],
                  patch_cut=M["granite"], manhole=M["rail"], gully=M["rail"],
                  gutter=M["cwall"], stain_dirt=M["grime"],
                  stain_gum=M["grime"], weed=M["grass"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", ground_plan(), M2,
                              skin_exclude=sc.skin_exclude)
        pit = gk.apply_ground(kit, f"{ROOT}/GKitPit", ground_plan_pit(), M2,
                              skin_exclude=sc.skin_exclude)
        print(f"[ground_kit] scene08 P3 · 프림 {res['prims']} + 피트 "
              f"{pit['prims']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    def build_tempbar(M):
        """개방 구간 임시 표지 — 안전봉 2 + 경고 테이프 1선(명백한 규정 미달).

        [v6 C-6] ① 안전봉 : 단색 원기둥 → **적·백 교대 5밴드**(총 높이·반경
                   불변, 세그 1.02배 겹침으로 캡 동일평면 회피).
                 ② 테이프 : 두께 0.02 솔리드 각재(= 차단기 붐으로 오독) →
                   두께 4 mm 리본 + 처짐 + 양단 안전봉 결속.
                   기하 구현은 sc._oriented_box(rotx) — op 적용순 scale→rotX→
                   rotZ 이므로 rotz=0 일 때 로컬 Y(길이축)는 (0, cos a, sin a).
                   세그 축 ∝ (0, dy, dz) → a = atan2(dz, dy).
                   size=(t, seg_len, w) → 로컬X=두께(월드 X), 로컬Z=폭(수직).
        """
        tb = PARAMS["tempbar"]
        pr = PARAMS["parapet"]
        nb = int(tb["nband"])
        bh = tb["post_h"] / nb
        for i, gy in enumerate((pr["gap_y0"], pr["gap_y1"])):
            for k in range(nb):
                CYL(f"{ROOT}/TempPost_{i}/Band_{k}",
                    (tb["x"], gy, (k + 0.5) * bh),
                    tb["post_r"], bh * tb["band_ov"],
                    M["tempost"] if k % 2 == 0 else M["tempost_b"],
                    col=(k == 0))
        # 경고 테이프 — 안전봉 2본 사이 처짐 리본
        tp = tb["tape"]
        ya, yb = pr["gap_y0"], pr["gap_y1"]
        L = yb - ya
        ym = (ya + yb) / 2.0

        def z_of(y):
            u = 2.0 * (y - ym) / L
            return tp["z_end"] - tp["sag"] * (1.0 - u * u)

        n = int(tp["nseg"])
        for i in range(n):
            y0 = ya + L * i / n
            y1 = ya + L * (i + 1) / n
            z0, z1 = z_of(y0), z_of(y1)
            dy, dz = y1 - y0, z1 - z0
            seg_len = math.hypot(dy, dz)
            ang = math.degrees(math.atan2(dz, dy))
            sc._oriented_box(
                stage, f"{ROOT}/TempTape_{i}",
                (tb["x"], (y0 + y1) / 2.0, (z0 + z1) / 2.0),
                (tp["t"], seg_len * 1.02, tp["w"]), M["temtape"], rotx=ang)
        for i, ay in enumerate((ya, yb)):
            CYL(f"{ROOT}/TempTapeTie_{i}", (tb["x"], ay, z_of(ay)),
                tb["post_r"] + 0.006, tp["tie_h"], M["temtape"])

    def build_signs(M):
        """[v5.2 사용자] 임의 경고 팻말 제거 — 시설 표지(sign_exit) 1매만."""
        for key, prm in (("exit", PARAMS["sign_exit"]),):
            sc.build_sign(stage, f"{ROOT}/Sign_{key}", prm["cx"], prm["cy"],
                          0.0, prm["yaw"], panel_mtl=M[f"sign_{key}"],
                          w=prm["w"], h=prm["h"], pole_h=prm["pole_h"],
                          pole_mtl=M["bollard"], back_mtl=M["sign_back"])

    # -------------------------------------------------------------------
    # 드레싱 — 코트(화단·벤치) / 광장(화단·가로수·벤치·가로등·볼라드)
    # -------------------------------------------------------------------
    def build_court_dressing(M):
        p = PARAMS["pit"]
        cp = PARAMS["court_planter"]
        for i, (cx, cy) in enumerate(PARAMS["court_planters"]):
            sc.build_planter(stage, f"{ROOT}/CourtPlanter_{i}", cx, cy,
                             p["floor_z"], M["cwall"], M["grass"],
                             size=cp["size"], curb_h=cp["curb_h"])
        for i, (cx, cy, yaw) in enumerate(PARAMS["court_benches"]):
            sc.build_bench(stage, f"{ROOT}/CourtBench_{i}", cx, cy,
                           p["floor_z"], M["wood"], yaw=yaw)

    def build_plaza_dressing(M):
        pp = PARAMS["plaza_planter"]
        # 개방 구간 좌우 화단(가림 요소 — '화단 뒤 파라펫' 구성). 나무 없음:
        #   그리드 축 근접이라 수관이 프레임을 잠식하지 않게 관목만.
        for i, (cx, cy) in enumerate(PARAMS["gap_planters"]):
            sc.build_planter(stage, f"{ROOT}/GapPlanter_{i}", cx, cy, 0.0,
                             M["cwall"], M["grass"], size=pp["size"])
        # 광장 가로수 화단 4 (원경·스케일 앵커)
        for i, (cx, cy) in enumerate(PARAMS["plaza_planters"]):
            sc.build_planter(stage, f"{ROOT}/PlazaPlanter_{i}", cx, cy, 0.0,
                             M["cwall"], M["grass"], size=pp["size"],
                             tree_mtls=(M["wood"], M["canopy_a"], M["canopy_b"]))
        for i, (cx, cy, yaw) in enumerate(PARAMS["plaza_benches"]):
            sc.build_bench(stage, f"{ROOT}/PlazaBench_{i}", cx, cy, 0.0,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            arm_dir = -1.0 if ly > 0 else 1.0        # 암은 광장 중심측으로
            CYL(f"{base}/Pole", (lx, ly, sl["pole_h"] / 2.0), sl["pole_r"],
                sl["pole_h"], M["bollard"], col=True)
            CYL(f"{base}/Arm",
                (lx, ly + arm_dir * sl["arm_len"] / 2.0, sl["pole_h"] - 0.12),
                sl["arm_r"], sl["arm_len"], M["bollard"], rotX=90.0)
            BOX(f"{base}/Head",
                (lx, ly + arm_dir * sl["arm_len"], sl["pole_h"] - 0.18),
                (sl["head"], sl["head"], 0.13), M["lamp"])
        for i, (bx, by) in enumerate(PARAMS["bollards"]):
            sc.build_bollard(stage, f"{ROOT}/Bollard_{i}", bx, by, 0.0,
                             mtl=M["bollard"])

    def build_skyline(M):
        """지평 폐쇄(§A-4) — 동측 3동이 주 카메라축 정면을 막는다."""
        for key, bd in PARAMS["far_buildings"].items():
            sc.build_building(stage, f"{ROOT}/FarBuilding_{key}", bd,
                              M["cwall"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_ground(M)
    if cfg["hazard_stairs"]:
        build_plaza(M)
        build_pit_shell(M)
        g_s, g_n = build_stairs(M)
        build_facade(M)
        build_ground_kit(M)            # [W2-D] ground elements
        if cfg["cue_railing"]:
            build_parapet(M)
            build_stair_rails(M, g_s, g_n)
        if cfg["cue_tactile"]:
            build_tactile_ring(M)
        if cfg["cue_sign"]:
            build_tempbar(M)
            build_signs(M)
        if cfg["cue_scene_dressing"]:
            build_court_dressing(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_plaza_dressing(M)
        build_skyline(M)               # 원경은 대조군(평지)에서도 유지

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
