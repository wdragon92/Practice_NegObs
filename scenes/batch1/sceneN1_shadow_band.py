# -*- coding: utf-8 -*-
"""
sceneN1_shadow_band.py — NegObs 인공씬 22호: 건물 그림자 띠 (Isaac Sim 4.5)

유형    : N1 Hard Negative — 평지 광장을 횡단하는 암 밴드 (GT = 전 픽셀 낙차 없음)
사양서  : Docs/nanobanana_batch1_geometry_map.md §A sceneN1_shadow_band
룩참조  : look_refs/n1_shadow.jpg
공통    : scene_common.py (검증된 API 헬퍼) · scene16_canopy_shadow.py (골격)

위험 본질(반례): **낙차는 어디에도 없다.** 완전 평탄한 대형 콘크리트 타일 광장을
           공중 슬래브(스카이브리지형)의 그림자가 폭 4m 띠로 횡단하고, 그 양쪽은
           모두 밝다. 양 에지가 선명한 암 밴드는 T3(하부 암부)·T20(캐노피 암부)의
           양성 단서와 **화소 수준에서 구별 불가**에 가깝다 — 모델이 "어두운 띠 =
           낙차"라는 지름길을 학습했는지 검사하는 첫 반례. 밴드 안에서도 포장
           텍스처·줄눈이 연속으로 읽혀야 한다(완전 흑이면 반례로서 무의미).
목표     : 평탄 광장(줄눈 격자 3m) + 프레임 밖 공중 슬래브 1매 + 드레싱을 조립,
           렌더로 판정 (렌더 전용). GT 낙차 맵 = 전 픽셀 0.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneN1_shadow_band.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneN1_shadow_band.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneN1_shadow_band.py
슬래브 프레임인 검산:   NEGOBS_GEOCHECK=1 python3 sceneN1_shadow_band.py  (Isaac 불요)

좌표계: Z-up, m, 진행축 +X. 낙차 없음 — 특색(그림자 밴드)이 x=0..4 구간.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import batch1_common as bc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hard negative 씬이므로 hazard_* 는 낙차가 아니라
#     "씬 특색 요소(오클루더 슬래브)" 토글. 해당 없는 cue 키는 False + 사유 주석.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_shadow_band": True,   # False → 공중 슬래브 제거(밴드 없는 균일광 대조군)
    "cue_railing":        False,  # 낙차 없음 → 난간 비관행. 키만 예약
    "cue_tactile":        False,  # 낙차 없음 → 경고 점자블록 비관행. 키만 예약
    "cue_material_break": True,   # 포장 줄눈 격자(타일 경계 스트립). False → 무줄눈
    "cue_nosing":         False,  # 단이 없음 → 논슬립 띠 무의미. 키만 예약
    "cue_sign":           False,  # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,   # 화단·벤치·볼라드·원경 건물(지평선 폐쇄) 일괄
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # 평탄 광장 1매 (개구 없음 → 4박스 분할 불요). 상면 z=0.
    plaza=dict(size=140.0, z_top=0.0, thick=0.5),

    # 목표 그림자 밴드 (지면 X구간). 슬래브 위치는 여기서 역산 — _slab_x() 참조.
    band=dict(x0=0.0, x1=4.0),
    # 오클루더: 프레임 밖 공중 슬래브(스카이브리지형). H=고도(밑면), half_y=반길이.
    slab=dict(H=12.0, thick=0.8, half_y=30.0),

    # ═══ 줄눈 — [W2 §5.1 N1] 단일 3 m 격자 → **2단화** ════════════════════
    #  구(舊): spacing 3.0 단일 격자. 실물 화강석 판석 광장은 **신축줄눈(폭
    #    20~30 mm)** 과 **시공줄눈(폭 3 mm 급)** 이 서로 다른 주기로 겹친다.
    #  신(新): 신축 `exp_spacing` 6.0 m + 시공 `con_spacing` 1.8 m 의 2단.
    #    ★ 1.8 m 는 **판석 셀 0.600 의 3배**다 — 사양 §4.5 U2(줄눈 주기는
    #      유닛 셀의 정수배)에 걸린다. v1 표기 "1.5~2 m" 는 2.5배라 T1 MDL
    #      유닛 지터와 **이중 격자**를 만든다 `[사양 §4.5 U2·§5.1]`.
    #    ★ 두 주기가 겹치는 눈금(18 m 주기)에서는 시공줄눈을 드롭한다 —
    #      동일 위치 2프림 = Z-파이팅.
    #  ★ ground_kit 은 이 씬에서 **줄눈을 만들지 않는다**(`pave.joint=None`
    #    오버라이드). 킷 줄눈(1.8/6.0)과 씬 격자가 같은 면에 겹치면
    #    파일럿 결함 D6(sceneN5 이중 줄눈 격자)이 재발한다 `[W2-B §7 D-list]`.
    joints=dict(exp_spacing=6.0, exp_width=0.045, con_spacing=1.8,
                con_width=0.022, proud=0.001,
                x0=-21.0, x1=30.0, y0=-21.0, y1=21.0),

    # ═══ [W2 ground_kit] P1 plaza_granite — 사양 §5.1 N1 행 ════════════════
    #  씬 고유 처방: ① 줄눈 2단화(위 `joints` 에서 씬이 직접 집행)
    #                ② 맨홀 1기 — **밴드 보존 불변식 통과 필수**(§7.3)
    #  ★ 밴드 보존(§7.3 B12, `ground_kit._inv_n1_band`): 이 씬의 오클루더는
    #    공중 슬래브 **단 하나**여야 한다. 태양 그림자는 순수 +X, 길이
    #    0.84536·h 이므로 신규 요소는
    #      (앞배치) `xb + 0.84536·h < band.x0`  또는  (뒤배치) `xa > band.x1`
    #    를 만족해야 한다. region 원단을 `band.x0 − 0.60` 으로 잘라 두면
    #    잡초(클램프 후 h ≤ 0.12)까지 포함해 앞배치 조건이 자동 성립한다
    #    `[계산 — −0.60 + 0.84536×0.12 = −0.499 < 0]`.
    #  ★ 점자블록: §12.4 "N1 볼라드 전면 유지 + 형태 교정(§12.5 ②)" —
    #    소판 0.40×0.30(본당 0.12 ㎡)은 approach 뷰에서 212 px/본이라
    #    판독 불가였다. 볼라드 열 전면 **연속 띠 0.60 m** 로 바꾼다
    #    (`relief="normal"` 이라 프림 1). 볼라드 열은 x 11…17 = **뒤배치**
    #    (xa = 11 > 4.0) 라 밴드 불변식을 통과한다.
    ground=dict(
        region_pad_x=0.60,                  # 밴드 앞 여유 (위 계산)
        region_x0=-12.0, region_y=4.0,
        #  맨홀 — 사양 §5.1 표기는 (−1.0, +0.4) 이지만 **파일럿 결재
        #  M9-ⓑ 2차 정정**(scene15)이 세운 기준 "면 요소 1개가 근경 창을
        #  독점하지 않는다(화면폭 ≤ 25 %)"를 그대로 적용해 이설한다:
        #    x=−1.0 → d2 에서 지면거리 1.0 m · 화면폭 f·0.648/1.0 = **1,078 px
        #    = 56.1 %** `[계산]`. W1(0.564~2.00 m) 안에서는 원단 X=2.00 에서도
        #    28.1 % 라 ≤25 % 가 **원리적으로 불가**하다.
        #    → 2순위 창 W2(2.00~3.00 m) 로: x=−2.40 ⇒ d5 X=2.60 m ·
        #      414 px = **21.6 %**, d10 X=7.60 m · 7.4 % `[계산]`.
        #      d2 는 눈 뒤(X=−0.40)라 비가시 → d2 창은 패치 #1 이 담당한다.
        #  2기 — 사양 §5.1 "맨홀 1~2기(1기는 반드시 W1)". W1 은 패치가 맡고
        #  맨홀은 W2 창에 둔다(위 화면폭 계산). 2기째는 d10 의 W2 창
        #  (X=3.4 m · 317 px = 16.5 %)에 두어 원경 컷의 면 요소를 채운다.
        manholes=[(-2.40, 0.40), (-6.60, -1.50)],
        #  패치 #1 = d2 근경 창(W1 = x −1.436…0.0) 담당. 평면 톤 변화라
        #  원판(맨홀)과 달리 근경 독점의 시각적 부담이 작다 `[파일럿 #2]`.
        #  패치 2매 = d2·d10 근경 창(W1) 담당. d5 W1 은 빗물받이가 맡는다.
        #    d2  W1 = x −1.436…0.0   → (−1.20, +0.10)
        #    d10 W1 = x −9.436…−8.0  → (−8.80, −0.20)
        #  프레임 반폭이 X=0.8 m 에서 0.46 m 뿐이라 **|y| ≤ 0.4** 여야 화면에
        #  든다 `[계산 — 반폭 0.5774·X]`.
        patches=[(-1.20, 0.10), (-8.80, -0.20)],
        #  빗물받이 — 1기는 d5 W1(x −4.436…−3.0)에, 1기는 광장 가장자리에.
        gullies=[(-3.80, 0.40), (-9.00, 2.60)],
        tactile_depth=0.60,                 # 국도 실무요령 7.5 — 점형 60 cm 표준
        tactile_setback=0.30,               # 법정 볼라드 전면 0.3 m
    ),

    # ═══ 드레싱 (cue_scene_dressing) — "도심 광장" 맥락 ═══════════════════
    #  ★ 밴드 보존 불변식 [이 씬의 특색 = 오클루더가 공중 슬래브 단 하나]
    #    태양 월드 az = 180.0 · elev 49.79 → 그림자는 **순수 +X**(y 이동 0),
    #    길이 = 0.84536·h. 따라서 월드 AABB x∈[xa,xb]·상단높이 h 인 요소는
    #       (앞배치)  xb + 0.84536·h < band.x0 (=0.0)      … 그림자가 밴드 앞에서 끝
    #       (뒤배치)  xa > band.x1 (=4.0)                   … 그림자가 밴드 뒤로만
    #    둘 중 하나를 만족해야 밴드에 신규 그림자가 닿지 않는다.
    #    전 요소를 dresscheck()(NEGOBS_GEOCHECK=1)로 자동 검산한다.
    #  ★ 보행 회랑 보존: grid_views 카메라 eye = (−10/−5/−2, 0, h). 신규 프림은
    #    |y| ≥ 5.0 또는 x ≥ 6.0 만 쓴다 → 카메라 매몰·밴드 폐색 원천 배제.
    #
    # 화단 — 광장 코너 4곳. tree=False 는 밴드 앞(-X)측(수관 그림자 여유 확보용).
    planters=[dict(name="A", cx=-6.0, cy=-9.0, base_z=0.0, tree=False),
              dict(name="B", cx=12.0, cy=10.0, base_z=0.0, tree=True),
              dict(name="C", cx=17.0, cy=-13.0, base_z=0.0, tree=True),
              dict(name="D", cx=9.0, cy=15.0, base_z=0.0, tree=True)],
    planter=dict(size=3.0, curb_h=0.45, curb_t=0.25, cap_over=0.05,
                 cap_h=0.05, grass_h=0.40),
    # 벤치 — 전부 앵커(화단·생울타리) 인접. yaw/위치는 v5.1 §3 결정적 지터
    #   (bc.jit_yaw/jit_pos, 좌표 해시 시드)로 축평행·등간격 인상을 없앤다.
    benches=[dict(name="A", cx=-6.0, cy=-6.6, yaw=0.0),     # 화단 A 앞 0.9 m
             dict(name="B", cx=12.0, cy=7.6, yaw=0.0),      # 화단 B 앞 0.9 m
             dict(name="C", cx=8.0, cy=-7.4, yaw=0.0),      # 가로등 B 옆 0.6 m
             dict(name="D", cx=17.0, cy=-10.6, yaw=0.0),    # 화단 C 앞 0.9 m
             dict(name="E", cx=-9.0, cy=10.3, yaw=0.0)],    # 생울타리 A 앞 1.2 m
    bench_jitter=dict(yaw_lo=3.0, yaw_hi=8.0, pos_amp=0.22),
    # ── 볼라드 [v5.1 §2 · ctx2 재배치] ────────────────────────────────────
    #   구(舊): 광장 가장자리 y=±9 장식 2열 12본(간격 4 m·규격 h0.75·반사띠/
    #   점형블록 없음) → **전면 제거**. 장식적 볼라드 열 금지(v5.1 §2).
    #   신(新): 차량 진입 우려 지점 = 광장 남측 **상가 앞 보도 ↔ 광장 접점의
    #   진입 목** 1열만. 규격 h0.90·φ0.12·간격 1.5 m·상단 백색 반사띠·
    #   전면(보도측 −Y) 0.3 m 점형블록 소판.
    #   ★ 밴드 보존: xa = 11.0−0.062 = 10.94 > band.x1(4.0) → **뒤배치**로
    #     그림자가 밴드에 닿을 수 없다(그림자는 순수 +X 방향).
    #   ★ 프레임인: approach(eye −8) 기준 x=11 은 19 m 전방, 수평 반폭 11.0 m
    #     > |y|=7 → 열 전체가 화면 안. band_grazing(eye −3, z0.35)에서도
    #     14 m 전방·반폭 8.1 m → 보인다. 밴드(x 0..4)보다 **뒤**라 폐색 없음.
    bollard_entry=dict(y=-7.0, x0=11.0, x1=17.0, spacing=1.5,
                       front=(0.0, -1.0)),   # 점형블록 = 보도(−Y)측
    bollard=dict(r=0.06, h=0.90),
    # 가로등 — 폴 5.2 m(그림자 4.40 m). A만 밴드 앞: 헤드 최대 x −6.6 → −2.20 < 0.
    streetlights=[dict(name="A", cx=-7.5, cy=7.5), dict(name="B", cx=8.0, cy=-8.0),
                  dict(name="C", cx=15.0, cy=8.5), dict(name="D", cx=21.0, cy=-9.0)],
    streetlight=dict(pole_h=5.2, pole_r=0.075, arm_len=0.9, arm_r=0.04, head=0.26),
    # 광장 수경(반사지) — build_planter 재사용(잔디 슬래브 자리에 수면 재질)
    pool=dict(cx=19.0, cy=6.0, size=4.4, curb_h=0.45, curb_t=0.28,
              cap_over=0.06, cap_h=0.06, water_h=0.30),
    # 생울타리 — 광장 외곽 경계 지시
    hedges=[dict(name="A", x0=-14.0, y0=11.5, x1=-4.0, y1=12.3, h=0.85),
            dict(name="B", x0=14.0, y0=-16.3, x1=24.0, y1=-15.5, h=0.85)],
    buildings=dict(
        # 원경 비스타 차단(+X 지평선): 파사드 -X평면
        C=dict(x0=34.0, x1=44.0, y0=-22.0, y1=22.0, h=16.0, floors=5,
               axis="x", facade_x=34.0, face_dir=-1.0),
        # ─ 스카이라인(실루엣 단차) : C 뒤 고층 1 + 좌우 중층 2 ─
        T=dict(x0=54.0, x1=66.0, y0=-14.0, y1=10.0, h=38.0, floors=10,
               axis="x", facade_x=54.0, face_dir=-1.0),
        E=dict(x0=40.0, x1=50.0, y0=24.0, y1=42.0, h=24.0, floors=7,
               axis="x", facade_x=40.0, face_dir=-1.0),
        W=dict(x0=38.0, x1=48.0, y0=-44.0, y1=-24.0, h=21.0, floors=6,
               axis="x", facade_x=38.0, face_dir=-1.0),
        # ─ 광장 양측 저층 상가(가로 벽면) : 파사드 y평면. x0=6.0 > band.x1 ─
        L=dict(x0=6.0, x1=30.0, y0=18.0, y1=30.0, h=10.0, floors=3,
               axis="y", facade_y=18.0, face_dir=-1.0),
        R=dict(x0=6.0, x1=30.0, y0=-30.0, y1=-18.0, h=10.0, floors=3,
               axis="y", facade_y=-18.0, face_dir=1.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.8, margin=2.5),

    material=dict(
        scale=dict(plaza_light=1.1, grass=1.4, brick_red=2.0),
        # ─ sRGB 지각 규약: plaza_light 원본 평균 sRGB 0.714(중성 백회) →
        #   웜 틴트로 0.65 전후. 레퍼런스(n1)의 밝은 웜 콘크리트 광장 대응. ─
        plaza_tint=(0.92, 0.88, 0.82),
        joint_color=(0.05, 0.05, 0.05), joint_rough=0.85,   # 암색 줄눈(0.02~0.06대)
        slab_color=(0.55, 0.55, 0.56), slab_rough=0.75,     # 슬래브(프레임 밖·무관)
        grass_tint=(0.55, 0.68, 0.42),
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.90, 0.90, 0.87), parapet_rough=0.6,
        # ─ 드레싱 신규 ─ (수관 암색은 sRGB 0.02~0.06 규약 대역)
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        post_color=(0.55, 0.55, 0.58), post_metallic=0.5, post_rough=0.5,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,
        water_color=(0.05, 0.10, 0.11), water_rough=0.05,
        hedge_tint=(0.35, 0.45, 0.28),
        # ─ 볼라드 v5.1 ─ 반사띠는 밝은 백색이되 총면적 0.08 m²/본(소면적)이라
        #   "순백 대면적 금지"(v5.1 §4)에 저촉하지 않는다.
        bollard_color=(0.78, 0.80, 0.83), bollard_metallic=0.85,
        bollard_rough=0.34,
        bollard_band_color=(0.88, 0.88, 0.86),
        tactile_color=(0.80, 0.66, 0.14), tactile_rough=0.70,
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
    # ─── SUN_AZ_OFFSET = 146.5 [이 씬의 특색을 결정하는 핵심 파라미터]
    #     태양 매핑(scene16 확정 규약): 월드 태양 az ≈ 33.5 + offset = 180.0
    #       → 그림자 방위 az_s = 태양az − 180 = 0.0 = **정확히 +X**.
    #     ⇒ 그림자 이동이 +X 순수 성분이므로, Y로 긴 슬래브의 그림자 밴드는
    #        에지가 x=const 인 직선 2개 = **카메라 시축(+X)과 직교**. (요구사항)
    #     ⇒ 태양은 −X(카메라 뒤)에 있어 정면광 — 레퍼런스 n1처럼 광장이 밝고
    #        밴드만 어둡다(역광 실루엣 아님).
    #     [ ]키(dome_rotation_step 15°)로 GUI 스윕 시 밴드가 X로 평행이동하며
    #     동시에 사선으로 기울어진다 — 판정 시 오프셋 0(기본) 유지할 것.
    SUN_AZ_OFFSET=146.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN1")

ASSET_ROLES = ["plaza_light", "grass", "brick_red", "hdri", "mdl"]


# ===========================================================================
# [D] 오클루더 슬래브 위치 역산 (밴드 사양 → 슬래브 X구간)
# ===========================================================================
def _slab_x():
    """목표 밴드[x0,x1] · 고도 H · 두께 t 로부터 슬래브 X구간을 역산.

    유도 (태양 고도 e=49.79°, 그림자 방위 +X 순수 — SUN_AZ_OFFSET 주석 참조):
      지면 z=0 위의 점 p=(x,z)는 그림자로 x + z·cot(e) 로 투영된다.
      슬래브(솔리드 박스) x∈[sx0,sx1], z∈[H,H+t] 의 그림자(umbra) 구간은
        시작 = min(x + z·cot) = sx0 + H·cot      (밑면 −X 모서리)
        끝   = max(x + z·cot) = sx1 + (H+t)·cot  (상면 +X 모서리)
      ⇒ 밴드 폭 = (sx1−sx0) + t·cot  ⇒ W_s = 밴드폭 − t·cot
        *맵 §A의 W_s ≈ 밴드폭·sin(e) 식은 광선에 수직한 판 가정 — 수평 슬래브는
         그림자가 순수 평행이동이라 위 식이 정확하다(감독 검산 요청 사항).*
      기본값(H=12, t=0.8, 밴드 0..4): cot=0.84536 → W_s=3.3237,
        슬래브 x=[-10.1444, -6.8207], 밴드 x=[0.0000, 4.0000] (검산 일치).
      반그림자(태양 각지름 0.53°): 광로 H/sin(e)=15.71m → 지면 X방향 폭 0.190m
        — 레퍼런스급 선명 에지(완전 하드는 아님, PT에서 판정).
    반환: (sx0, sx1, cot_e)
    """
    e = math.radians(float(PARAMS["light"]["noon_sun_elev"]))
    cot = 1.0 / math.tan(e)
    b, s = PARAMS["band"], PARAMS["slab"]
    sx0 = float(b["x0"]) - float(s["H"]) * cot
    sx1 = sx0 + (float(b["x1"]) - float(b["x0"])) - float(s["thick"]) * cot
    return sx0, sx1, cot


def build_views():
    """카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷."""
    views = sc.grid_views(0.0)
    # approach: 밝은 광장에서 밴드로 보행 접근 (밴드가 낙차처럼 읽히는지)
    views["approach"] = dict(eye=[-8.0, 0.0, 1.6], tgt=[4.0, 0.0, 0.2])
    # band_grazing: 저시점 grazing — 밴드가 지평 압축되어 "단"처럼 보이는 극단
    views["band_grazing"] = dict(eye=[-3.0, 0.0, 0.35], tgt=[7.0, 0.0, 0.15])
    # band_edge_close: 밴드 진입 직전 근접 — 에지 선명도·밴드 내부 텍스처 판독
    views["band_edge_close"] = dict(eye=[-1.2, 0.0, 1.1], tgt=[3.0, 0.0, -0.4])
    # beauty_oblique: 사선 부감 — 밴드가 평면임을 드러내는 대조 컷
    views["beauty_oblique"] = dict(eye=[-7.0, -6.0, 2.6], tgt=[3.0, 1.0, -0.2])
    return views


# ===========================================================================
# [D1b] 배치 비정형 (v5.1 §3) — 결정적 지터 배치 산출.
#       빌더와 검산이 **동일 함수**를 호출하므로 AABB 가 항상 실제와 일치한다.
# ===========================================================================
def bench_placements():
    """[(name, x, y, yaw), ...] — 벤치 5기의 지터 후 최종 배치."""
    j = PARAMS["bench_jitter"]
    out = []
    for b in PARAMS["benches"]:
        dx, dy = bc.jit_pos(b["cx"], b["cy"], "benchN1", amp=j["pos_amp"])
        yaw = bc.jit_yaw(b["cx"], b["cy"], "benchN1",
                         lo=j["yaw_lo"], hi=j["yaw_hi"], base=b["yaw"])
        out.append((b["name"], b["cx"] + dx, b["cy"] + dy, yaw))
    return out


def streetlight_placements():
    """[(name, x, y, yaw), ...] — 가로등 4기의 지터 후 배치(암 방위 비정렬)."""
    out = []
    for s in PARAMS["streetlights"]:
        dx, dy = bc.jit_pos(s["cx"], s["cy"], "slN1", amp=0.20)
        yaw = bc.jit_yaw(s["cx"], s["cy"], "slN1", lo=3.0, hi=8.0)
        out.append((s["name"], s["cx"] + dx, s["cy"] + dy, yaw))
    return out


def bollard_entry_points():
    """[v5.1 §2] 진입부 1열 볼라드 중심 좌표 [(x, y), ...] (간격 1.5 m 균등)."""
    e = PARAMS["bollard_entry"]
    return bc.bollard_line(e["x0"], e["y"], e["x1"], e["y"],
                           spacing=e["spacing"])


def tactile_band_rect():
    """[W2 §12.5 ②] 볼라드 열 전면 **연속 점형 띠** 사각형 (x0, y0, x1, y1).

    법정 위치는 "볼라드 전면 0.3 m"(교통약자법 시행규칙 별표1 2호 차목),
    세로폭은 국도 실무요령 7.5 의 점형 표준 60 cm. `front_dir` 이 −Y 이므로
    띠는 볼라드 몸통 앞면에서 −Y 로 setback 만큼 떨어져 depth 만큼 뻗는다.
    좌표는 **PARAMS 에서 유도**한다(문서 좌표 하드코드 금지 — 사양 §7.4).
    """
    e, bo, g = PARAMS["bollard_entry"], PARAMS["bollard"], PARAMS["ground"]
    fx, fy = e["front"]
    sb, dp = float(g["tactile_setback"]), float(g["tactile_depth"])
    if abs(fy) > abs(fx):                       # 전면이 ±Y (이 씬: −Y)
        y_face = e["y"] + fy * bo["r"]
        ya, yb = y_face + fy * sb, y_face + fy * (sb + dp)
        return (e["x0"] - 0.15, min(ya, yb), e["x1"] + 0.15, max(ya, yb))
    x_face = e["x0"] + fx * bo["r"]
    xa, xb = x_face + fx * sb, x_face + fx * (sb + dp)
    return (min(xa, xb), e["y"] - 0.15, max(xa, xb), e["y"] + 0.15)


def ground_plans():
    """[W2 ground_kit] 지면 계획 — 씬 조립부와 CPU 검산이 **같은 함수**를 쓴다.

    반환 `[(tag, GroundPlan), ...]`. `plan_ground` 는 USD 를 만들지 않으므로
    Isaac 없이 게이트(B6~B12)를 그대로 돌릴 수 있다 `[사양 §3.3]`.
    """
    g = PARAMS["ground"]
    b = PARAMS["band"]
    x1 = float(b["x0"]) - float(g["region_pad_x"])
    gp = gk.plan_ground(
        "plaza_granite",
        region=(float(g["region_x0"]), -float(g["region_y"]),
                x1, float(g["region_y"])),
        z=float(PARAMS["plaza"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=(),                       # hard negative — 낙차 에지 0
        dists=(2, 5, 10), scene="sceneN1",
        # ★ `cue_tactile` 이 아니라 `cue_scene_dressing` 에 건다 — 이 씬의
        #   `cue_tactile` 은 "계단 경고 점자블록"용 예약 키(낙차가 없어 상시
        #   False)이고, 볼라드 전면 점형블록은 **볼라드와 한 몸**이라
        #   드레싱 토글을 따라야 한다 `[사양 §12.4 — N1 볼라드 전면 유지]`.
        tactile=("bollard",) if SCENE_CONFIG["cue_scene_dressing"] else (),
        sites=dict(manhole=[tuple(p) for p in g["manholes"]],
                   gully=[tuple(p) for p in g["gullies"]],
                   patch=[tuple(p) for p in g["patches"]],
                   tactile=dict(bollard=tactile_band_rect())),
        # 줄눈은 씬 `build_joints()` 가 2단으로 집행한다(위 PARAMS 주석 · D6)
        overrides=dict(pave=dict(joint=None)),
        seed=22)
    return [("plaza", gp)]


# ===========================================================================
# [D2] 맥락 드레싱 AABB 목록 (보수적 상계) — 밴드 그림자·카메라 매몰 검산 전용.
#      build_dressing() 이 실제로 만드는 프림의 **외접 상자**를 PARAMS 에서
#      재계산한다(빌더 내부 치수는 scene_common 주석 기준으로 상계를 잡음).
# ===========================================================================
def dressing_aabbs():
    """[(name, xa, xb, ya, yb, z_top), ...] 반환. z_top = 그림자 투영에 쓰는 최고점."""
    out = []
    pl = PARAMS["planter"]
    half = pl["size"] / 2.0
    top_curb = pl["curb_h"] + pl["cap_h"]
    # build_tree 상계: 잔디면(grass_h) + trunk_h 2.2 + 최고 blob(dz .85 + r .30*0.8)
    top_tree = pl["grass_h"] + 2.2 + 0.85 + 0.24
    for p in PARAMS["planters"]:
        t = top_tree if p.get("tree") else top_curb
        out.append((f"Planter_{p['name']}", p["cx"] - half, p["cx"] + half,
                    p["cy"] - half, p["cy"] + half, t))
    # 벤치 1.8(x)×0.4(y)×h0.45 — yaw 지터(≤8°) 상계로 반폭을 확장
    #   회전 후 반폭 ≤ (0.9·cos8 + 0.2·sin8, 0.9·sin8 + 0.2·cos8) = (0.92, 0.32)
    for name, bx, by, _yaw in bench_placements():
        out.append((f"Bench_{name}", bx - 0.92, bx + 0.92,
                    by - 0.32, by + 0.32, 0.45))
    # 볼라드 v5.1 (몸통+반사띠 / 점형블록 소판) — 진입부 1열
    bo = PARAMS["bollard"]
    e = PARAMS["bollard_entry"]
    for i, (bx, by) in enumerate(bollard_entry_points()):
        out.extend(bc.bollard_v51_aabbs(f"Bollard_{i}", bx, by, 0.0,
                                        front_dir=e["front"],
                                        radius=bo["r"], height=bo["h"]))
    sl = PARAMS["streetlight"]
    # 암 ±X + 헤드 반폭. yaw 지터(≤8°) 상계 → x 반폭 ex, y 반폭 ex·sin8+head/2
    for name, sx, sy, _yaw in streetlight_placements():
        ex = sl["arm_len"] + sl["head"] / 2.0
        ey = ex * math.sin(math.radians(8.0)) + sl["head"] / 2.0
        out.append((f"Streetlight_{name}", sx - ex, sx + ex,
                    sy - ey, sy + ey, sl["pole_h"]))
    po = PARAMS["pool"]
    ph = po["size"] / 2.0
    out.append(("Pool", po["cx"] - ph, po["cx"] + ph, po["cy"] - ph,
                po["cy"] + ph, po["curb_h"] + po["cap_h"]))
    for h in PARAMS["hedges"]:
        out.append((f"Hedge_{h['name']}", h["x0"], h["x1"], h["y0"], h["y1"],
                    h["h"]))
    for k, bd in PARAMS["buildings"].items():
        out.append((f"Building_{k}", bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                    bd["h"] + 0.5))                  # +파라펫
    return out


def dresscheck():
    """드레싱 검산 2종.
      ① 밴드 그림자 침입: 태양 az=180 → 그림자는 순수 +X, 길이 0.84536·z.
         요소가 밴드[x0,x1]에 그림자를 드리우지 않을 조건 =
           xb + cot·z_top < band.x0   (앞배치)   또는   xa > band.x1 (뒤배치)
      ② 카메라 매몰: 전 뷰 eye 가 어떤 AABB(여유 0.35 m 팽창) 안에도 없을 것.
    """
    cot = 1.0 / math.tan(math.radians(float(PARAMS["light"]["noon_sun_elev"])))
    b0, b1 = float(PARAMS["band"]["x0"]), float(PARAMS["band"]["x1"])
    boxes = dressing_aabbs()
    print("-" * 68)
    print("sceneN1 드레싱 검산 ① 밴드 그림자 침입 (밴드 x=[%.1f, %.1f], cot=%.5f)"
          % (b0, b1, cot))
    bad = 0
    for name, xa, xb, ya, yb, zt in boxes:
        sh_end = xb + cot * zt                       # 그림자 최원단(+X)
        if xa > b1:
            verdict = "뒤배치 OK (xa %.2f > %.1f)" % (xa, b1)
        elif sh_end < b0:
            verdict = "앞배치 OK (그림자 끝 %.2f < %.1f, 여유 %.2f m)" % (
                sh_end, b0, b0 - sh_end)
        else:
            verdict = "★밴드 침입★ (그림자 %.2f..%.2f)" % (xa, sh_end)
            bad += 1
        print("  %-16s x[%7.2f,%7.2f] z_top %5.2f → %s"
              % (name, xa, xb, zt, verdict))
    print("  판정 ①: %s" % ("전 요소 밴드 무침입 (합격)" if bad == 0
                            else "%d개 침입 (불합격)" % bad))
    print("sceneN1 드레싱 검산 ② 카메라 매몰 (여유 0.35 m)")
    m = 0.35
    hit = 0
    worst = (None, 1e9)
    for vname, v in sorted(build_views().items()):
        ex, ey, ez = v["eye"]
        for name, xa, xb, ya, yb, zt in boxes:
            if (xa - m <= ex <= xb + m and ya - m <= ey <= yb + m
                    and -m <= ez <= zt + m):
                print("  %-20s ★매몰★ %s" % (vname, name))
                hit += 1
            d = max(xa - ex, ex - xb, ya - ey, ey - yb, 0.0)
            if d < worst[1]:
                worst = ("%s vs %s" % (vname, name), d)
    print("  최근접(수평 거리) %s = %.2f m" % worst)
    print("  판정 ②: %s" % ("전 뷰 클리어 (합격)" if hit == 0
                            else "%d건 매몰 (불합격)" % hit))
    print("-" * 68)


# ─── 슬래브 프레임인 검산 (요구사항: 전 프리셋·미장센 컷에서 슬래브 불가시) ───
#  Isaac 기본 퍼스펙 카메라 = 초점 18.147mm / 수평 어퍼처 20.955mm, 16:9
#    → 수평 FOV 60.0°, 수직 FOV 35.98°. 검사는 안전마진 포함 h70°/v46°로 수행.
#  결과 (기본 PARAMS, NEGOBS_GEOCHECK=1 재현):
#    · preset_h*_d2 / d5, approach, band_grazing, band_edge_close
#        → 슬래브(x≤−6.82)가 **전부 카메라 후방** → 원천적 불가시
#    · preset_h0.3/0.9/1.8_d10 (eye x=−10, 슬래브 바로 아래)
#        → 전방 잔여부의 최소 수직각 84.8°/84.0°/82.7° ≫ 프레임 상단 23°
#    · beauty_oblique (eye −7,−6,2.6)
#        → 최소 수평각 58.3° ≫ 프레임 측단 35°  (수직 최소 37.3°도 초과)
#    ⇒ 전 컷 OUT. 밴드만 보이고 오클루더는 화면 밖 = N1 사양 충족.
#  ─ 맥락 드레싱 검산(dresscheck) 결과 요약 [ctx2 재검산, 07-27] ─
#    ① 밴드 그림자 침입 0건 — 앞배치 요소는 Planter_A(여유 4.08 m)·Bench_A
#       (4.85)·Bench_E(7.63)·Hedge_A(3.28)·Streetlight_A(2.13) 5개뿐이고,
#       나머지(볼라드 진입열 5본 + 점형블록 포함)는 전부 xa > 4.0 뒤배치.
#       ★ 볼라드 h0.75→0.90 상향분은 전량 뒤배치라 불변식에 무영향.
#    ② 카메라 매몰 0건 — 최근접 수평 0.23 m(beauty_oblique eye vs Bench_A).
#       eye z 2.60 · 프레임 하단광선 접지 4.3 m 전방 ⇒ 근접분은 화면 밖.
def geocheck():
    """슬래브 AABB를 뷰 프러스텀에 투영해 프레임인 여부 검산 (Isaac 불요)."""
    sx0, sx1, cot = _slab_x()
    s = PARAMS["slab"]
    z0, z1, hy = float(s["H"]), float(s["H"]) + float(s["thick"]), float(s["half_y"])
    hfov, vfov = 70.0, 46.0                      # 실 60/36 + 안전마진
    print("=" * 68)
    print("sceneN1 오클루더 슬래브 프레임인 검산")
    print("  cot(elev)=%.5f  슬래브 x=[%.4f, %.4f] (폭 %.4f) z=[%.2f, %.2f] "
          "y=±%.1f" % (cot, sx0, sx1, sx1 - sx0, z0, z1, hy))
    print("  → umbra 밴드 x=[%.4f, %.4f] (폭 %.4f)"
          % (sx0 + z0 * cot, sx1 + z1 * cot,
             (sx1 + z1 * cot) - (sx0 + z0 * cot)))
    print("  검사 FOV h%.0f°/v%.0f° (실제 h60/v36 + 마진)" % (hfov, vfov))
    pts = []
    for i in range(9):
        px = sx0 + (sx1 - sx0) * i / 8.0
        for j in range(201):
            py = -hy + 2.0 * hy * j / 200.0
            for pz in (z0, (z0 + z1) / 2.0, z1):
                pts.append((px, py, pz))
    bad = 0
    for name, v in sorted(build_views().items()):
        ex, ey, ez = v["eye"]
        fx, fy, fz = (v["tgt"][0] - ex, v["tgt"][1] - ey, v["tgt"][2] - ez)
        fn = math.sqrt(fx * fx + fy * fy + fz * fz)
        fx, fy, fz = fx / fn, fy / fn, fz / fn
        rx, ry, rz = fy * 1.0 - fz * 0.0, fz * 0.0 - fx * 1.0, 0.0   # f × Z
        rn = math.hypot(rx, ry)
        rx, ry = rx / rn, ry / rn
        ux = ry * fz - rz * fy
        uy = rz * fx - rx * fz
        uz = rx * fy - ry * fx
        n_front = 0
        min_h = 180.0
        min_v = 180.0
        inside = 0
        for px, py, pz in pts:
            dx, dy, dz = px - ex, py - ey, pz - ez
            fw = dx * fx + dy * fy + dz * fz
            if fw <= 1e-6:
                continue
            n_front += 1
            ah = math.degrees(math.atan2(abs(dx * rx + dy * ry), fw))
            av = math.degrees(math.atan2(abs(dx * ux + dy * uy + dz * uz), fw))
            min_h = min(min_h, ah)
            min_v = min(min_v, av)
            if ah < hfov / 2.0 and av < vfov / 2.0:
                inside += 1
        if n_front == 0:
            print("  %-20s OUT — 슬래브 전부 카메라 후방" % name)
        elif inside:
            bad += 1
            print("  %-20s ★FRAME-IN★ (샘플 %d개)" % (name, inside))
        else:
            print("  %-20s OUT — 최소 수평각 %.1f° / 수직각 %.1f°"
                  % (name, min_h, min_v))
    print("  판정: %s" % ("전 컷 OUT (합격)" if bad == 0 else "%d컷 프레임인 (불합격)" % bad))
    dresscheck()
    print("=" * 68)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]  ※ 이 씬은 GT = 전 픽셀 "낙차 없음" (hard negative)
 1. approach / h0.9_d5   — 폭 4m 암 밴드가 광장을 횡단, 양쪽 모두 밝은가
 2. band_edge_close (PT) — 밴드 **내부에 포장 텍스처·줄눈이 연속 판독**되는가
                            (완전 흑이면 실패 — 반례로서 무의미)
 3. band_grazing         — 저시점에서 밴드 에지가 "단"처럼 읽히는 혼동 강도
 4. 전 컷               — 오클루더 슬래브가 화면에 **절대 보이지 않는가**
                            (NEGOBS_GEOCHECK=1 검산과 대조)
 5. 기하                 — 밴드 에지가 x=const 직선(시축 직교)·평면 Z파이팅 없음
 6. 맥락(드레싱)         — 가로등·벤치·볼라드열·상가 가로벽·원경 스카이라인으로
                            "도심 광장"이 읽히는가. **밴드(x 0~4) 위·주변에는
                            신규 그림자가 하나도 없어야** 한다(dresscheck ① 대조)"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene22")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene22"

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
            f"{ROOT}/Looks/Plaza", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=mp["plaza_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["joint"] = PBR(f"{ROOT}/Looks/Joint",
                         diffuse_color=mp["joint_color"],
                         roughness_const=mp["joint_rough"], metallic=0.0)
        M["slab"] = PBR(f"{ROOT}/Looks/Slab", diffuse_color=mp["slab_color"],
                        roughness_const=mp["slab_rough"], metallic=0.0)
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # ─ 맥락 드레싱 신규 ─
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        # ─ 볼라드 v5.1 (몸통 스테인리스 / 상단 반사띠 / 전면 점형블록) ─
        M["bollard_body"] = PBR(f"{ROOT}/Looks/BollardBody",
                                diffuse_color=mp["bollard_color"],
                                metallic=mp["bollard_metallic"],
                                roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
        M["tactile"] = bc.tactile_mtl(stage, f"{ROOT}/Looks/Tactile")
        return M

    # -------------------------------------------------------------------
    # 광장 — 완전 평탄 단일 슬래브 (공동·개구 전무: GT 낙차 0)
    # -------------------------------------------------------------------
    def build_plaza(M):
        p = PARAMS["plaza"]
        # [W2-0 · P-A] 광장 상면이 ground_kit 의 장식 대상이다 → 변위 스킨 OFF.
        #   `add_box` 가 그 자리에서 `_skin_wanted` 를 부르므로 **BOX 호출 전에**
        #   등록해야 한다. 안 끄면 맨홀(±10 mm)·데칼(0.6 mm)이 스킨
        #   (+6.5~16.5 mm) 아래로 통째로 묻힌다 `[실측 — 사양 §1.1]`.
        sc.skin_exclude(f"{ROOT}/Plaza")
        BOX(f"{ROOT}/Plaza",
            (0.0, 0.0, p["z_top"] - p["thick"] / 2.0),
            (p["size"], p["size"], p["thick"]), M["plaza"], col=True)

    def build_joints(M):
        """[W2 §5.1 N1] **2단 줄눈** — 신축 6.0 m + 시공 1.8 m.

        암색 박판 proud 0.001 (밴드 내부 판독의 기준 단서)은 불변. 바뀐 것은
        주기 하나가 아니라 **두 주기의 층위**다 — 실물 판석 광장이 그렇고,
        1.8 m 는 판석 셀 0.600 의 정수배라 T1 유닛 지터와 위상이 맞는다
        `[사양 §4.5 U2]`. 두 주기가 겹치는 눈금에서는 시공줄눈을 드롭한다.
        """
        j = PARAMS["joints"]
        p = PARAMS["plaza"]
        pr = j["proud"]
        thk = pr + 0.006                        # 일부 매입 + proud 돌출
        cz = p["z_top"] + pr - thk / 2.0
        Lx = j["x1"] - j["x0"]
        Ly = j["y1"] - j["y0"]

        def ticks(a0, a1, step):
            n = int(math.floor((a1 - a0) / step + 1e-9)) + 1
            return [a0 + i * step for i in range(n)]

        exp_x = ticks(j["x0"], j["x1"], j["exp_spacing"])
        exp_y = ticks(j["y0"], j["y1"], j["exp_spacing"])
        exp_xs = set(round(v, 4) for v in exp_x)
        exp_ys = set(round(v, 4) for v in exp_y)
        n = 0
        # X축 방향 줄눈(=y=const 선) : 카메라 시축과 평행
        for yy in exp_y:
            BOX(f"{ROOT}/JointX_{n}", ((j["x0"] + j["x1"]) / 2.0, yy, cz),
                (Lx, j["exp_width"], thk), M["joint"])
            n += 1
        for yy in ticks(j["y0"], j["y1"], j["con_spacing"]):
            if round(yy, 4) in exp_ys:          # 동일 위치 2프림 = Z-파이팅
                continue
            BOX(f"{ROOT}/JointX_{n}", ((j["x0"] + j["x1"]) / 2.0, yy, cz),
                (Lx, j["con_width"], thk), M["joint"])
            n += 1
        # Y축 방향 줄눈(=x=const 선) : 밴드 에지와 평행 — 혼동 강화 요소
        m = 0
        for xx in exp_x:
            BOX(f"{ROOT}/JointY_{m}", (xx, (j["y0"] + j["y1"]) / 2.0, cz),
                (j["exp_width"], Ly, thk), M["joint"])
            m += 1
        for xx in ticks(j["x0"], j["x1"], j["con_spacing"]):
            if round(xx, 4) in exp_xs:
                continue
            BOX(f"{ROOT}/JointY_{m}", (xx, (j["y0"] + j["y1"]) / 2.0, cz),
                (j["con_width"], Ly, thk), M["joint"])
            m += 1
        print(f"[줄눈] 2단화 — 신축 {j['exp_spacing']} m · 시공 "
              f"{j['con_spacing']} m · X {n}본 · Y {m}본")

    # -------------------------------------------------------------------
    # [W2] ground_kit — P1 plaza_granite. 낙차 에지가 없는 hard negative 라
    #   GT-E1′/GT-E2 는 공허참이고, 판정은 **B12 밴드 보존 불변식**(§7.3)과
    #   프림 예산·알베도가 한다. 줄눈은 씬이 직접 집행한다(D6 회피).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        (_tag, gp), = ground_plans()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["joint"], crack=M["joint"], patch=M["plaza"],
                  patch_cut=M["curb"], manhole=M["post"], gully=M["post"],
                  gutter=M["curb"], weed=M["grass"], tactile=M["tactile"],
                  stain_dirt=M["joint"], stain_water=M["joint"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] sceneN1 P1 · 프림 {res['prims']} · 산포 "
              f"{res['instances']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # 오클루더 — 프레임 밖 공중 슬래브 (스카이브리지형). 위치는 _slab_x() 역산.
    # -------------------------------------------------------------------
    def build_occluder(M):
        s = PARAMS["slab"]
        sx0, sx1, cot = _slab_x()
        hy = s["half_y"]
        BOX(f"{ROOT}/SkyBridgeSlab",
            ((sx0 + sx1) / 2.0, 0.0, s["H"] + s["thick"] / 2.0),
            (sx1 - sx0, 2.0 * hy, s["thick"]), M["slab"])
        print("[기하] 슬래브 x=[%.4f, %.4f] z=[%.2f, %.2f] → 밴드 x=[%.4f, %.4f]"
              % (sx0, sx1, s["H"], s["H"] + s["thick"],
                 sx0 + s["H"] * cot, sx1 + (s["H"] + s["thick"]) * cot))

    # -------------------------------------------------------------------
    # 드레싱 — "여기가 어디인지"를 렌더만으로 읽히게 하는 도심 광장 맥락:
    #   화단 4(코너 식재) + 벤치 5 + 볼라드 진입 1열(v5.1 규격) + 가로등 4 + 수경 1 +
    #   생울타리 2 + 건물 6동(원경 스카이라인 + 광장 양측 상가 가로벽).
    #   전 요소는 dresscheck() 로 ①밴드 그림자 무침입 ②카메라 무매몰 검산.
    # -------------------------------------------------------------------
    def build_dressing(M):
        pl = PARAMS["planter"]
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for pdef in PARAMS["planters"]:
            # tree=False(밴드 앞 -X측): 수관 그림자 여유를 넉넉히 남긴다.
            sc.build_planter(
                stage, f"{ROOT}/Planter_{pdef['name']}", pdef["cx"], pdef["cy"],
                pdef["base_z"], M["curb"], M["grass"],
                tree_mtls=(tree_mtls if pdef.get("tree") else None),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"],
                grass_h=pl["grass_h"])
        # 벤치 — 앵커(화단·생울타리) 인접 + yaw/위치 결정적 지터 (v5.1 §3)
        for name, bx, by, byaw in bench_placements():
            sc.build_bench(stage, f"{ROOT}/Bench_{name}", bx, by, 0.0,
                           M["wood"], yaw=byaw)
        # 볼라드 [v5.1 §2] — 광장 남측 보도 접점 진입부 1열(간격 1.5 m).
        #   장식 2열(y=±9, 12본)은 제거. 점형블록은 보도측(−Y)에 flush.
        bo = PARAMS["bollard"]
        e = PARAMS["bollard_entry"]
        for i, (bx, by) in enumerate(bollard_entry_points()):
            # [W2 §12.5 ②] 본당 소판(0.40×0.30)은 **ground_kit 의 연속 띠
            #   0.60 m 로 대체**한다 — 소판은 approach 뷰에서 212 px/본,
            #   5본 합계도 프레임의 0.05 % 미만이라 판독이 불가능했다
            #   `[실측 — 사양 §12.5 ②]`. 여기서 끄지 않으면 띠와 소판이
            #   맞닿아 점형 대역이 0.9 m 로 늘어난다(법정 0.60 초과).
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{i}", bx, by, 0.0,
                                 None, M["bollard_body"], M["bollard_band"],
                                 M["tactile"], front_dir=e["front"],
                                 radius=bo["r"], height=bo["h"],
                                 tactile=False)
        sl = PARAMS["streetlight"]
        for name, sx, sy, syaw in streetlight_placements():
            # 암 방위를 축평행에서 살짝 틀어 '복제 배치' 인상 제거 (v5.1 §3)
            base = sc.build_rot_group(stage, f"{ROOT}/Streetlight_{name}",
                                      (sx, sy), syaw)
            CYL(f"{base}/Pole", (sx, sy, sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["post"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (sx + sgn * sl["arm_len"] / 2.0, sy,
                     sl["pole_h"] - 0.10), sl["arm_r"], sl["arm_len"],
                    M["post"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (sx + sgn * sl["arm_len"], sy,
                     sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        # 수경(반사지) — build_planter 의 "잔디 슬래브"를 수면 재질로 대체.
        #   수면 상단 z = water_h(0.30) < 경계석 0.45 → 전 기하 z ≥ 0 (GT 불변)
        po = PARAMS["pool"]
        sc.build_planter(stage, f"{ROOT}/Pool", po["cx"], po["cy"], 0.0,
                         M["curb"], M["water"], tree_mtls=None,
                         size=po["size"], curb_h=po["curb_h"],
                         curb_t=po["curb_t"], cap_over=po["cap_over"],
                         cap_h=po["cap_h"], grass_h=po["water_h"])
        for hg in PARAMS["hedges"]:
            sc.build_hedge(stage, f"{ROOT}/Hedge_{hg['name']}", hg["x0"],
                           hg["y0"], hg["x1"], hg["y1"], hg["h"], base_z=0.0,
                           tint=mp["hedge_tint"])
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_plaza(M)
    if cfg["cue_material_break"]:
        build_joints(M)
    if cfg["hazard_shadow_band"]:
        build_occluder(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)                  # [W2] 지면 요소 — 드레싱 뒤(산포 순서 규약)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneN1 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["beauty_oblique"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN1_{ts}.png")
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
        geocheck()                     # Isaac 부팅 없이 슬래브 프레임인만 검산
    else:
        main()
