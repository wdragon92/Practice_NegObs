# -*- coding: utf-8 -*-
"""
sceneC1_snow_stairs.py — NegObs 인공씬 26호: 눈 덮인 계단 (Isaac Sim 4.5)

유형    : C1 조건 변주 — 기존 직선 계단 기하 + 적설 환경 레이어 (배치1 핵심 씬)
사양서  : Docs/nanobanana_batch1_geometry_map.md §B sceneC1_snow_stairs
룩 참조 : look_refs/c1_snow_stairs.jpg
공통    : scene_common.py · scene16_canopy_shadow.py(표준 템플릿) ·
          scene01_campus_stairs.py(직선 계단 기준형)

위험 본질: 기하는 평범한 직선 12단(riser 0.17 · tread 0.30 · 폭 2.5)인데,
           5cm 적설이 트레드를 이어붙여 **모호한 백색 경사면**으로 만든다.
           단 에지는 노징 오버행(눈 처마)이 만든 둥근 융기선으로만 암시되고,
           고알베도·저대비 흐린 광 아래에서 그 융기선마저 뭉갠다.
           GT는 기하 그대로 **낙차 양성(2.04m)** — cue가 매몰된 극한 케이스.
목표     : 상부 테라스 → 계단 → 하부 평지의 보행 연속성을 유지한 채(교훈 9),
           눈 레이어(트레드별 눈 박스 + 접근로 평판 + 난간 상단 스트립)를
           올려 렌더로 판정 (렌더 전용).

특색 성립 조건 [중요]:
  **저대비 흐린 광(overcast)** 이 이 씬의 특색 성립 조건이다. 청천 정오광이면
  경질 그림자가 단 에지를 또렷하게 재생성해 "은닉" 자체가 무너진다. 그래서
  light 프로파일은 sc.OVERCAST_HDRI + lookfix=False + 무태양(DistantLight
  비가시)이고, 직달광 손실분은 dome_intensity 상향으로 보상한다.

은닉도 조절 [감독 스윕용]:
  PARAMS["snow"]의 thickness / nose_over / riser_cover 3개가 단 에지 가시성을
  지배한다. 기본값은 기하맵 사양치(0.05 / 0.06 / 0.50)이며, 레퍼런스보다 더
  매몰시키려면 (0.09 / 0.12 / 0.85) 방향으로 올린다. 세부는 PARAMS 주석 참조.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneC1_snow_stairs.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneC1_snow_stairs.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneC1_snow_stairs.py

좌표계: Z-up, m, 진행축 +X, 낙차 시작 모서리 = x=0.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import batch1_common as bc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키 + 특색 토글 1키(snow_cover).
#     hazard_stairs 만 기하 토글(False→전면 z=0 평지).
#     snow_cover 는 이 씬의 특색 토글 — 사양상 "False → 눈 제거"이므로
#     눈 레이어 프림이 사라지고 뱅크 표면이 적설 두께만큼 내려간다
#     (계단 코어 기하 = GT 는 불변).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 계단·뱅크·하부평지를 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        True,   # 편측(+Y) 파이프 난간 + 상단 눈 스트립
    "cue_tactile":        True,   # 상단 경고 점자블록 — 적설 아래 완전 매몰(특색)
    "cue_material_break": True,   # False → 계단도 접근로와 동일 콘크리트 톤
    "cue_nosing":         True,   # 황색 논슬립 띠 — 눈 아래 매몰, 대응쌍에서만 노출
    "cue_sign":           False,  # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,   # 제설 눈더미·기둥·원경 건물 일괄
    "snow_cover":         True,   # [특색] False → 눈 레이어 제거 = 대응쌍(맨 계단)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # 직선 12단 × riser 0.17 · tread 0.30 → 낙차 2.04m, run 3.60m, 폭 2.5
    stairs=dict(x0=0.0, riser=0.17, tread=0.30, nsteps=12,
                y0=-1.25, y1=1.25, z_top=0.0, base_z=-2.90),

    # 상부 테라스(제방 상단). 두께 2.6 → 하부 평지 바닥보다 아래까지 솔리드.
    terrace=dict(x0=-60.0, x1=0.0, y0=-60.0, y1=60.0, z_top=0.0, thick=2.60),
    # 하부 평지. x0 는 계단 끝(run)보다 0.05 뒤에서 시작하고 상면을 2mm 낮춰
    # 마지막 단 상면과의 동일평면(Z-파이팅)을 회피 — 겹침 5cm.
    lower=dict(x_back=0.05, x1=60.0, y0=-60.0, y1=60.0, z_gap=0.002,
               thick=0.70),

    # 계단 양측 눈 뱅크(제방 사면). 상면 평면 z = lift − (riser/tread)·x
    #   = "노징선"(단 앞모서리를 잇는 선)에 적설 두께만큼 얹힌 면.
    #   → 상부 테라스 눈면(z=+t)과 하부 평지 눈면(z=−2.04+t)을 정확히 잇는다:
    #     추가 낙차 에지 없음 = GT 오염 없음, 보행 연속성 유지(교훈 9).
    #   y_in 은 계단 측면(±1.25)보다 0.02 안쪽 → 솔리드 겹침(동일평면 회피).
    bank=dict(y_in_over=0.02, y_out=60.0, x_head=0.02, x_tail=0.20, thick=2.20),
    # 계단 측면 노출 콘크리트 스트링어(레퍼런스의 유일한 비적설 요소).
    # 상면 = 뱅크면 + proud(0.02) → 눈밭 속 가느다란 암색 에지선으로 잔존.
    stringer=dict(y_in=1.20, y_out=1.45, proud=0.02, x_head=0.05, x_tail=0.10,
                  thick=0.60),

    # ─── 눈 레이어 [특색 파라미터] ───────────────────────────────────────
    #  thickness   적설 두께. ↑ 하면 트레드 상면이 두껍게 융기해 단 높이 대비
    #              에지 대비가 낮아진다. 기하맵 사양 0.05. 스윕 0.05→0.09.
    #  nose_over   노징 전방 오버행(눈 처마). ↑ 하면 다음 단 위를 덮어 단코가
    #              둥글게 말리며 소실. 기하맵 사양 0.06. 스윕 0.06→0.12.
    #  riser_cover 라이저 상반부 덮음 비율(0.5=상반부). ↑ 하면 라이저 수직면의
    #              암부 띠가 줄어 프로파일이 램프에 근접. 스윕 0.50→0.85.
    #  lip_recess  처마 핀을 슬래브 앞끝보다 안쪽으로 후퇴시키는 비율(라운딩감).
    #  side_over   눈이 계단 측면으로 흘러넘치는 폭(동일평면 회피 겸용).
    #  embed_*     아래 솔리드에 파묻는 깊이(Z-파이팅 방지, 시각 영향 없음).
    # ────────────────────────────────────────────────────────────────────
    snow=dict(thickness=0.05, nose_over=0.06, riser_cover=0.50,
              lip_recess=0.15, side_over=0.010,
              embed_step=0.010, embed_plate=0.020,
              rail_strip_w=0.08, rail_strip_t=0.05, rail_strip_lift=0.04),

    # 편측 난간 (레퍼런스 우측). 뱅크면 위에 서고, 경사는 계단과 동일.
    rail=dict(y=1.60, x_start=-1.20, rail_h=0.90, post_r=0.022, rail_r=0.03,
              rail_mid_r=0.018, rail_mid_drop=0.45, spacing=1.20),

    tactile=dict(ahead=0.30, proud=0.004),
    # 노징 y를 계단 폭보다 0.02 안쪽으로 → 눈 슬래브 내부에 완전 봉입.
    nosing=dict(color=(0.85, 0.72, 0.10), width=0.05, proud=0.001,
                y_inset=0.02),

    # 드레싱 — 제설 눈더미(찌그러진 구 3개/더미) · 표지기둥 · 원경 건물
    piles=[dict(cx=-4.2, cy=3.6, s=1.0), dict(cx=-6.5, cy=-3.2, s=0.8),
           dict(cx=-2.6, cy=-5.4, s=0.9)],
    pile=dict(blobs=((0.00, 0.00, 1.30, 0.55), (0.75, 0.25, 1.05, 0.40),
                     (-0.60, -0.20, 0.95, 0.38))),
    pole=dict(cx=-3.4, cy=2.9, r=0.05, h=2.60, cap_t=0.06),
    buildings=dict(
        # +X 원경 비스타 차단(하부 평지 레벨에 기단). 파사드 -X 평면.
        C=dict(x0=26.0, x1=32.0, y0=-14.0, y1=14.0, h=12.0, floors=4,
               axis="x", facade_x=26.0, face_dir=-1.0),
        # -X 원경(lower_lookback 용). 파사드 +X 평면, 테라스 레벨 기단.
        D=dict(x0=-46.0, x1=-40.0, y0=-14.0, y1=14.0, h=9.0, floors=3,
               axis="x", facade_x=-40.0, face_dir=1.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),

    # ═══ [맥락 드레싱 v2 · 07-27] "여기가 어디인지" 읽히는 겨울 주거지/캠퍼스 ═══
    #  감사 v4 통합계획 §휑함 대응. 계단 코어·눈 레이어·조명 파라미터는 일절
    #  건드리지 않고, 상부 테라스(x<0, 상면 z=LIFT)와 하부 평지(x>RUN, 상면
    #  z=LOWER_TOP+LIFT) 위에만 신규 프림을 얹는다.
    #  전 요소에 **눈 캡(백색 박판 0.03~0.05)** 을 씌워 적설 정합을 유지한다.
    #
    #  [카메라 검산 — build_views() 8+4컷 전수, FOV 수평 ±30°/수직 ±18° 가정]
    #   grid  eye(-2/-5/-10, 0, h) +X · approach eye(-6,0,1.65) ·
    #   grazing_top eye(-2.2,0,0.35) · rail_side eye(-3.0,3.2,1.5) az -29.1° ·
    #   lower_lookback eye(7.0,0.6,1.5) az 184.3°
    #   → 아래 각 항목 주석에 (카메라, 방위각, 계단 가림 여부) 기재.
    #   공통 원칙 ① 카메라 eye 반경 1.5 m 내 신규 솔리드 금지
    #            ② 계단 방위각 밴드(각 시점별로 계산) 밖에 배치 = 특색 무가림
    #            ③ 보행 회랑(|y|<1.6, 접근로 x<0 / 하부 x>RUN) 침범 금지
    # ───────────────────────────────────────────────────────────────────────
    # 눈 쌓인 벤치 2 — A(-1.0,-2.35)는 approach 우측 프레임 가장자리
    #   (az -19.2..-32.9°, 계단 밴드 ±11.8° 밖) & lower_lookback 중경.
    #   B(-6.9,3.9)는 lower_lookback 좌측. 제설더미 0번(x -5.75..-2.40)과
    #   0.22 m 이격(자가감사 통과).
    benches=[dict(cx=-1.0, cy=-2.35, yaw=0.0, base="upper"),
             dict(cx=-6.9, cy=3.9, yaw=0.0, base="upper")],
    bench=dict(length=1.8, width=0.50, height=0.45, back_h=0.42, cap_t=0.04),
    # 가로등 2본 — 연질 직달(elev 28°, 광 진행 (-0.879,+0.477,-0.469);
    #   dome_rot -110+171.5=61.5° · rotX 62° 로부터 산출)에 긴 그림자.
    #   A(-0.9,-3.10): h4.0 → 그림자 끝 (-7.5,+0.5). **전 구간 x<0 테라스에만
    #   떨어져 계단 트레드 불간섭** = 은닉 조건 무변경, 근경 눈면 릴리프만 증가.
    #   카메라: approach 헤드 az -23.3°(계단 ±11.8° 밖) · grid d5 헤드
    #   az -28.2°(계단 ±14° 밖) · grid d10 헤드 az -13.6°(계단 ±7.1° 밖) ·
    #   rail_side az -71°(프레임 -59..+1° 밖) · lookback az 203.9°(계단 뒤편).
    lamps=[dict(cx=-0.9, cy=-3.10, arm=0.9, base="upper"),
           dict(cx=-8.4, cy=3.6, arm=-0.9, base="upper")],
    lamp=dict(pole_r=0.06, pole_h=4.0, arm_r=0.035, head_l=0.34, head_w=0.22,
              head_h=0.14, cap_t=0.04),
    # 표지판 기둥 1 — lower_lookback 전용(az 201.4°). 전 정면 시점 프레임 밖.
    signpost=dict(cx=-3.2, cy=-3.4, pole_r=0.045, pole_h=2.15,
                  panel_w=0.70, panel_h=0.50, panel_t=0.06, panel_z=1.72,
                  cap_t=0.035),
    # 눈 쌓인 생울타리 라인 — 대지 경계 정의(휑함 1순위 해소).
    #   상부 2줄(|y|=5.2, x -22..-4.5) : 제설더미 2번(x -3.8..-1.4) 회피 절단.
    #   하부 2줄(|y|=7.0, x 6.5..12.5) + 직교 2줄(x 12.0..12.7) = 원경 정원 경계.
    #   전부 보행 회랑(|y|<1.6) 밖 · 계단보다 멀어 가림 불가.
    hedges=[dict(x0=-22.0, x1=-4.5, y0=4.85, y1=5.55, h=0.75, base="upper"),
            dict(x0=-22.0, x1=-4.5, y0=-5.55, y1=-4.85, h=0.75, base="upper"),
            dict(x0=6.5, x1=12.5, y0=6.65, y1=7.35, h=0.80, base="lower"),
            dict(x0=6.5, x1=12.5, y0=-7.35, y1=-6.65, h=0.80, base="lower"),
            dict(x0=11.4, x1=12.1, y0=7.00, y1=15.5, h=0.80, base="lower"),
            dict(x0=11.4, x1=12.1, y0=-15.5, y1=-7.00, h=0.80, base="lower")],
    hedge_cap=dict(over=0.05, t=0.05),
    # 원경 저층 주택 4동(눈 캡 지붕 + 굴뚝) — 지평 폐쇄 + 주거지 판독.
    #   하부 3동은 approach/grazing_top 중원경 프레임을 채우고(건물 C 앞),
    #   상부 1동은 lower_lookback 좌측(az 161.4°)에서 건물 D와 함께 배경 형성.
    #   상호·생울타리·기존 건물과 전부 비중첩(좌표 검산 완료).
    houses=[dict(x0=13.0, x1=19.0, y0=9.0, y1=15.0, h=5.0, base="lower",
                 face=-1.0),
            dict(x0=15.0, x1=20.0, y0=-18.0, y1=-11.0, h=4.5, base="lower",
                 face=-1.0),
            dict(x0=20.0, x1=25.0, y0=4.5, y1=10.5, h=6.0, base="lower",
                 face=-1.0),
            dict(x0=-18.0, x1=-12.0, y0=7.0, y1=13.0, h=5.0, base="upper",
                 face=1.0)],
    house=dict(eave=0.35, roof_t=0.16, cap_t=0.06, cap_inset=0.06,
               chimney_s=0.50, chimney_h=1.10, win_w=1.0, win_h=1.4,
               win_rows=2, win_cols=3, foot=0.60),

    material=dict(
        scale=dict(concrete_floor=1.0, dirt_park=2.0, brick_red=2.0,
                   tactile=0.3),
        # 눈: 고알베도라 sRGB 암색 규약(0.02~0.06) 대상 아님.
        snow_color=(0.72, 0.74, 0.78), snow_rough=0.95, snow_spec=0.1,
        stair_tint=(0.92, 0.92, 0.95),      # cue_material_break 용 미세 색차
        dirt_tint=(0.72, 0.68, 0.62),       # 눈 제거 시 뱅크(마사토)
        rail_color=(0.72, 0.74, 0.78), rail_metallic=0.8, rail_rough=0.45,
        wall_tint=(0.88, 0.88, 0.90),
        glass_color=(0.05, 0.07, 0.10), glass_rough=0.12,
        parapet_color=(0.86, 0.87, 0.88), parapet_rough=0.7,
        # ─ 맥락 드레싱 v2 상수 (sRGB 암색 규약 0.02~0.09 준수) ─
        wood_color=(0.055, 0.036, 0.022), wood_rough=0.85,   # 벤치 목재
        roof_color=(0.045, 0.042, 0.048), roof_rough=0.75,   # 주택 지붕 슬래브
        hedge_color=(0.030, 0.048, 0.028), hedge_rough=1.0,  # 상록 생울타리
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,      # 램프 헤드(주간)
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.50,
        sign_color=(0.045, 0.085, 0.19),                     # 표지판 패널(청)
    ),

    # ─── overcast 조명 프로파일 (sceneC4 와 동일) ────────────────────────
    #  · hdri=sc.OVERCAST_HDRI : 청천 대신 흐린 하늘 → 태양 디스크 없음.
    #  · lookfix=False         : lookfix는 "태양 캡 + 지평 리프트"용. 무태양
    #                            HDRI에는 무의미(최대휘도 픽셀이 태양이 아님)
    #                            하므로 원본 사용.
    #  · noon_sun_enable=False : 보조 DistantLight 비가시 → 경질 그림자 제거.
    #                            (setup_lighting 이 intensity/color 키를 항상
    #                             읽으므로 키 자체는 남겨 둔다.)
    #  · dome_intensity        : 직달 2450 을 잃은 만큼 상향. 기존 noon 1000
    #                            기준 1500~2500 스윕 권장. 시작값 2000.
    #                            눈(알베도 0.85)이라 과노출 시 1600 쪽으로,
    #                            하이라이트가 죽으면 2400 쪽으로.
    #  · hdri_sun_rotz_offset  : 무태양이라 무의미 → 0.0.
    # ────────────────────────────────────────────────────────────────────
    light=dict(
        hdri=sc.OVERCAST_HDRI,
        dome_intensity=800.0,    # r2에도 포화 → 추가 감광. 무태양 돔 단독은 RT가 평면광 — 판정은 PT
        noon_dome_rot=-110.0,
        lookfix=False,
        noon_sun_enable=True, noon_sun_elev=28.0,   # r3: 완전 무방향광은 융기선 음영 불성립(화이트아웃) → 저강도 연질 직달로 릴리프 복원
        noon_sun_intensity=420.0, noon_sun_color=(1.0, 0.985, 0.97),
        hdri_sun_rotz_offset=0.0,
        dome_rotation_step=15.0,
    ),
    # ─── SUN_AZ_OFFSET: 무태양 프로파일이라 그림자 방위 의미가 없다. 돔 Z회전은
    #     흐린 하늘의 완만한 휘도 구배·원경 반영 방향만 바꾼다. 하네스 일관성을
    #     위해 브리프 v3 §A-7 기본값 171.5 유지, [ ]키로 스윕 가능. ───
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneC1")

ASSET_ROLES = ["concrete_floor", "dirt_park", "brick_red", "tactile",
               "hdri", "mdl"]


# --- 파생 치수 (여러 빌더가 공유) -------------------------------------------
def _dims():
    st = PARAMS["stairs"]
    run = st["tread"] * st["nsteps"]
    drop = st["riser"] * st["nsteps"]
    slope_k = st["riser"] / st["tread"]          # 노징선 기울기 (하강 +X)
    lift = PARAMS["snow"]["thickness"] if SCENE_CONFIG["snow_cover"] else 0.0
    return run, drop, slope_k, lift


def build_views():
    """카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷."""
    views = sc.grid_views(0.0)
    # approach: 상부 테라스 보행 시점 — 백색 경사면 인상
    views["approach"] = dict(eye=[-6.0, 0.0, 1.65], tgt=[2.0, 0.0, -0.90])
    # grazing_top: 낮은 시점 — 단 에지가 융기선으로만 남는가(특색 1순위)
    views["grazing_top"] = dict(eye=[-2.2, 0.0, 0.35], tgt=[3.6, 0.0, -0.70])
    # rail_side: 난간·스트링어 쪽 사선 — 유일한 잔존 단서 확인
    views["rail_side"] = dict(eye=[-3.0, 3.2, 1.50], tgt=[2.2, 0.30, -1.20])
    # lower_lookback: 하부에서 되돌아봄 — 단 에지가 가장 잘 보이는 대조 시점
    views["lower_lookback"] = dict(eye=[7.0, 0.60, 1.50], tgt=[-1.0, 0.0, 0.20])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach / grid    — 상부 테라스·계단·하부 평지가 하나의 백색면으로 읽히는가
 2. grazing_top·h0.3   — 단 에지가 둥근 융기선으로만 암시되는가(특색 1순위)
 3. rail_side          — 난간·콘크리트 스트링어가 유일 단서로 잔존하는가
 4. snow_cover ON/OFF  — 눈 제거 시 계단 코어 기하(단 위치·낙차) 불변인가
 5. 조명               — 무태양 저대비인가(경질 그림자 0), 눈 과노출/흑화 없는가
 6. 재질·Z파이팅       — 눈/콘크리트 경계, 처마 핀, 평판 이음에 깜빡임 없는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene26")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene26"

    RUN, DROP, SLOPE_K, LIFT = _dims()
    LOWER_TOP = PARAMS["stairs"]["z_top"] - DROP - PARAMS["lower"]["z_gap"]

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
        M["concrete"] = PBR(
            f"{ROOT}/Looks/Concrete", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"])
        M["stair"] = PBR(
            f"{ROOT}/Looks/Stair", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"],
            tint=mp["stair_tint"])
        M["dirt"] = PBR(
            f"{ROOT}/Looks/Dirt", sc.tex_path("dirt_park", "diff"),
            sc.tex_path("dirt_park", "nor"), sc.tex_path("dirt_park", "rough"),
            sca["dirt_park"], tint=mp["dirt_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"], tint=mp["wall_tint"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        # 눈: 상수 고알베도 + 초거친 + 낮은 스펙큘러 (기하맵 사양)
        M["snow"] = PBR(f"{ROOT}/Looks/Snow",
                        diffuse_color=mp["snow_color"],
                        roughness_const=mp["snow_rough"], metallic=0.0,
                        specular_level=mp["snow_spec"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # ─ 맥락 드레싱 v2 재질 (상수색만 — 신규 텍스처 의존 없음) ─
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["roof"] = PBR(f"{ROOT}/Looks/Roof", diffuse_color=mp["roof_color"],
                        roughness_const=mp["roof_rough"])
        # [v5.1 §4] 원경 주택 4동은 같은 지붕/벽 재질을 공유해 '복제 블록'
        #   인상을 준다 → 동별 ±5% 결정적 틴트 지터.
        #   · 지붕은 diffuse_color(알베도 0.045) → cap 무관.
        #   · 벽은 brick 텍스처의 tint 배율만 흔든다(텍스처 자체는 공유).
        for _i, _hd in enumerate(PARAMS["houses"]):
            _kx, _ky = _hd["x0"], _hd["y0"]
            M[f"roof_{_i}"] = PBR(
                f"{ROOT}/Looks/Roof_{_i}",
                diffuse_color=bc.jit_tint(mp["roof_color"], _kx, _ky,
                                          "roofC1", amp=0.05),
                roughness_const=mp["roof_rough"])
            M[f"brick_{_i}"] = PBR(
                f"{ROOT}/Looks/Brick_{_i}", sc.tex_path("brick_red", "diff"),
                sc.tex_path("brick_red", "nor"),
                sc.tex_path("brick_red", "rough"), sca["brick_red"],
                tint=bc.jit_tint(mp["wall_tint"], _kx, _ky, "wallC1",
                                 amp=0.05))
        M["hedge"] = PBR(f"{ROOT}/Looks/Hedge", diffuse_color=mp["hedge_color"],
                         roughness_const=mp["hedge_rough"], specular_level=0.0)
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=0.5)
        return M

    # -------------------------------------------------------------------
    # 지형 — 상부 테라스 / 하부 평지 / 양측 눈 뱅크 / 콘크리트 스트링어
    #   개구(피트)가 없는 제방형이므로 4박스 분할 대상 없음. 대신 세 솔리드가
    #   서로 겹치며 타일링 → 공동 위를 덮는 평면도, 부유 에지도 없다.
    # -------------------------------------------------------------------
    def build_terrace(M):
        tr = PARAMS["terrace"]
        BOX(f"{ROOT}/Terrace",
            ((tr["x0"] + tr["x1"]) / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
             tr["z_top"] - tr["thick"] / 2.0),
            (tr["x1"] - tr["x0"], tr["y1"] - tr["y0"], tr["thick"]),
            M["concrete"], col=True)

    def build_lower(M):
        lo = PARAMS["lower"]
        x0 = RUN - lo["x_back"]
        BOX(f"{ROOT}/LowerPlain",
            ((x0 + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             LOWER_TOP - lo["thick"] / 2.0),
            (lo["x1"] - x0, lo["y1"] - lo["y0"], lo["thick"]),
            M["concrete"], col=True)

    def build_banks(M):
        """양측 사면. 상면 z = LIFT − SLOPE_K·x (노징선 + 적설 두께)."""
        bk = PARAMS["bank"]
        st = PARAMS["stairs"]
        mtl = M["snow"] if cfg["snow_cover"] else M["dirt"]
        x0 = st["x0"] - bk["x_head"]
        z0 = LIFT + SLOPE_K * bk["x_head"]
        run = RUN + bk["x_head"] + bk["x_tail"]
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            y_in = sgn * (st["y1"] - bk["y_in_over"])   # 계단 솔리드에 2cm 물림
            y_out = sgn * bk["y_out"]
            sc.build_slope(stage, f"{ROOT}/Bank_{tag}", x0, z0, run,
                           run * SLOPE_K, min(y_in, y_out), max(y_in, y_out),
                           bk["thick"], mtl, margin=0.0, collider=True)

    def build_stringers(M):
        """계단 측면 노출 스트링어 — 상면 = 뱅크면 + proud."""
        sg = PARAMS["stringer"]
        st = PARAMS["stairs"]
        x0 = st["x0"] - sg["x_head"]
        z0 = LIFT + SLOPE_K * sg["x_head"] + sg["proud"]
        run = RUN + sg["x_head"] + sg["x_tail"]
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            a = sgn * sg["y_in"]
            b = sgn * sg["y_out"]
            sc.build_slope(stage, f"{ROOT}/Stringer_{tag}", x0, z0, run,
                           run * SLOPE_K, min(a, b), max(a, b), sg["thick"],
                           M["concrete"], margin=0.0, collider=True)

    def build_stairs(stair_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 전면 z=0 평지(+ 눈 평판)."""
        tr = PARAMS["terrace"]
        lo = PARAMS["lower"]
        x0, x1 = tr["x0"], lo["x1"]
        BOX(f"{ROOT}/FlatFill",
            ((x0 + x1) / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
             tr["z_top"] - tr["thick"] / 2.0),
            (x1 - x0, tr["y1"] - tr["y0"], tr["thick"]),
            M["concrete"], col=True)
        if cfg["snow_cover"]:
            sn = PARAMS["snow"]
            z_hi = tr["z_top"] + sn["thickness"]
            z_lo = tr["z_top"] - sn["embed_plate"]
            BOX(f"{ROOT}/Snow/FlatPlate",
                ((x0 + x1) / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
                 (z_hi + z_lo) / 2.0),
                (x1 - x0, tr["y1"] - tr["y0"], z_hi - z_lo), M["snow"])

    # -------------------------------------------------------------------
    # 눈 레이어 [특색] — 트레드별 눈 박스(+처마 핀) · 접근로 평판 · 난간 스트립
    #   * 처마 핀은 슬래브 앞끝보다 lip_recess 만큼 후퇴하고 위로 5mm 파고들어
    #     "둥근 노징" 프로파일을 근사한다(동일평면 없음).
    #   * 상부 평판은 x0+nose_over 까지만 내밀어 첫 라이저를 덮는 처마가 되며,
    #     그 아래 낙차 공간을 막지 않는다(회귀방지 §A-3 취지 준수).
    # -------------------------------------------------------------------
    def build_snow(M):
        sn = PARAMS["snow"]
        st = PARAMS["stairs"]
        tr = PARAMS["terrace"]
        lo = PARAMS["lower"]
        t = sn["thickness"]
        over = sn["nose_over"]
        so = sn["side_over"]
        sy0, sy1 = st["y0"] - so, st["y1"] + so
        scy = (sy0 + sy1) / 2.0
        sLy = sy1 - sy0
        fLy = sLy - 0.010                    # 처마 핀 폭(슬래브보다 좁게)

        def _slab(tag, xa, xb, ztop, lip):
            z_hi = ztop + t
            z_lo = ztop - sn["embed_step"]
            # 뒤끝을 1cm 앞 솔리드(이전 단 / 상부 테라스)에 파묻어 x=xa 동일평면 회피
            xa_s = xa - 0.010
            xb_s = xb + (over if lip else 0.0)
            BOX(f"{ROOT}/Snow/Slab_{tag}",
                ((xa_s + xb_s) / 2.0, scy, (z_hi + z_lo) / 2.0),
                (xb_s - xa_s, sLy, z_hi - z_lo), M["snow"])
            if lip:
                # 12mm 물림 — 다음 슬래브 뒤끝(10mm)과 다른 평면이어야 은닉도를
                # 올린 스윕(riser_cover↑)에서도 동일평면이 생기지 않는다.
                fx0 = xb - 0.012
                fx1 = xb + over * (1.0 - sn["lip_recess"])
                fz_hi = ztop + 0.005                   # 슬래브 내부로 봉입
                fz_lo = ztop - st["riser"] * sn["riser_cover"]
                BOX(f"{ROOT}/Snow/Lip_{tag}",
                    ((fx0 + fx1) / 2.0, scy, (fz_hi + fz_lo) / 2.0),
                    (fx1 - fx0, fLy, fz_hi - fz_lo), M["snow"])

        # ① 상부 접근로 평판 + 계단 상단 모서리 처마.
        #    대지 경계에서 0.1 인셋 — 테라스 박스 측면과의 동일평면 회피용
        #    (인셋 에지는 60m 밖이라 화면에 들어오지 않는다).
        ins = 0.10
        z_hi = tr["z_top"] + t
        z_lo = tr["z_top"] - sn["embed_plate"]
        px0 = tr["x0"] + ins
        px1 = st["x0"] + over
        BOX(f"{ROOT}/Snow/PlateTop",
            ((px0 + px1) / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
             (z_hi + z_lo) / 2.0),
            (px1 - px0, (tr["y1"] - tr["y0"]) - 2.0 * ins, z_hi - z_lo),
            M["snow"])
        lz_hi = st["z_top"] + 0.005
        lz_lo = st["z_top"] - st["riser"] * sn["riser_cover"]
        lx0 = st["x0"] - 0.012                  # Slab_1 뒤끝(10mm)과 다른 평면
        lx1 = st["x0"] + over * (1.0 - sn["lip_recess"])
        BOX(f"{ROOT}/Snow/LipTop",
            ((lx0 + lx1) / 2.0, scy, (lz_hi + lz_lo) / 2.0),
            (lx1 - lx0, fLy, lz_hi - lz_lo), M["snow"])

        # ② 트레드별 눈 박스 (마지막 단은 하부 평지와 이어지므로 처마 없음)
        for i in range(1, st["nsteps"] + 1):
            xa = st["x0"] + st["tread"] * (i - 1)
            xb = xa + st["tread"]
            ztop = st["z_top"] - st["riser"] * i
            _slab(str(i), xa, xb, ztop, lip=(i < st["nsteps"]))

        # ③ 하부 접근로 평판 (마지막 단 슬래브와 5cm 겹침 · 상면 2mm 낮음)
        bx0 = RUN - lo["x_back"]
        bx1 = lo["x1"] - ins
        z_hi = LOWER_TOP + t
        z_lo = LOWER_TOP - sn["embed_plate"]
        BOX(f"{ROOT}/Snow/PlateBot",
            ((bx0 + bx1) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             (z_hi + z_lo) / 2.0),
            (bx1 - bx0, (lo["y1"] - lo["y0"]) - 2.0 * ins, z_hi - z_lo),
            M["snow"])

    def build_rail_snow(M):
        """난간 상단 눈 스트립 — 수평 연장부(박스) + 경사부(build_slope 박판)."""
        sn = PARAMS["snow"]
        rl = PARAMS["rail"]
        top0 = LIFT + rl["rail_h"]                     # x=0 에서의 레일 중심 z
        z_top = top0 + rl["rail_r"] + sn["rail_strip_lift"]
        w = sn["rail_strip_w"]
        th = sn["rail_strip_t"]
        # 수평부: x_start..x0+0.03 (경사부와 3cm 겹침, 상면 2mm 낮춤 → 동일평면 X)
        hx1 = PARAMS["stairs"]["x0"] + 0.03
        BOX(f"{ROOT}/Snow/RailStripFlat",
            ((rl["x_start"] + hx1) / 2.0, rl["y"], z_top - 0.002 - th / 2.0),
            (hx1 - rl["x_start"], w, th), M["snow"])
        sc.build_slope(stage, f"{ROOT}/Snow/RailStripSlope", 0.0, z_top,
                       RUN, DROP, rl["y"] - w / 2.0, rl["y"] + w / 2.0,
                       th, M["snow"], margin=0.0, collider=False)

    # -------------------------------------------------------------------
    # 단서 (cue) — nosing / tactile / railing
    # -------------------------------------------------------------------
    def build_cues(M):
        st = PARAMS["stairs"]
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"],
                st["y0"] + ns["y_inset"], st["y1"] - ns["y_inset"],
                st["riser"], st["tread"], st["nsteps"],
                color=ns["color"], width=ns["width"], proud=ns["proud"],
                z_top=st["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["tactile"],
                             z=st["z_top"], proud=tc["proud"])
        if cfg["cue_railing"]:
            rl = PARAMS["rail"]

            def bank_ground(x):
                """뱅크 상면(난간 포스트 착지면)."""
                if x <= 0.0:
                    return LIFT
                return LIFT - SLOPE_K * min(x, RUN)

            sc.build_railing_line(
                stage, f"{ROOT}/StairRail_P", rl["y"], rl["x_start"],
                st["x0"], RUN, DROP, bank_ground, M["rail"],
                rail_h=rl["rail_h"], post_r=rl["post_r"],
                spacing=rl["spacing"], rail_r=rl["rail_r"],
                rail_mid_r=rl["rail_mid_r"],
                rail_mid_drop=rl["rail_mid_drop"])
            if cfg["snow_cover"]:
                build_rail_snow(M)

    # -------------------------------------------------------------------
    # 드레싱 — 제설 눈더미 · 표지기둥 · 원경 건물 2동(지평선 폐쇄 §A-4)
    # -------------------------------------------------------------------
    def build_dressing(M):
        pile_mtl = M["snow"] if cfg["snow_cover"] else M["dirt"]
        # 드레싱은 전부 상부 테라스(x<0) 위 — 뱅크 사면 위 부유 방지.
        base_top = LIFT
        for i, pd in enumerate(PARAMS["piles"]):
            s = pd["s"]
            for j, (dx, dy, rxy, rz) in enumerate(PARAMS["pile"]["blobs"]):
                sc.add_sphere(stage, f"{ROOT}/Pile_{i}_{j}",
                              (pd["cx"] + dx * s, pd["cy"] + dy * s,
                               base_top + rz * s * 0.35),
                              (rxy * s, rxy * s * 0.8, rz * s * 0.55),
                              pile_mtl)
        po = PARAMS["pole"]
        CYL(f"{ROOT}/Pole", (po["cx"], po["cy"], base_top + po["h"] / 2.0),
            po["r"], po["h"], M["rail"], col=True)
        if cfg["snow_cover"]:
            BOX(f"{ROOT}/Snow/PoleCap",
                (po["cx"], po["cy"], base_top + po["h"] + po["cap_t"] / 2.0
                 - 0.01),
                (po["r"] * 2.4, po["r"] * 2.4, po["cap_t"]), M["snow"])
        # 원경 건물 — C(+X)는 하부 평지, D(-X)는 테라스 레벨에 기단
        low_base = LOWER_TOP if cfg["hazard_stairs"] else 0.0
        for key, bd in PARAMS["buildings"].items():
            b = dict(bd)
            b["base_z"] = low_base if key == "C" else 0.0
            sc.build_building(stage, f"{ROOT}/Building_{key}", b,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        build_context(M)

    # -------------------------------------------------------------------
    # 맥락 드레싱 v2 — 벤치 · 가로등 · 표지판 · 생울타리 · 저층 주택
    #   전 요소가 "겨울 주거지/캠퍼스 뒷계단" 정황을 만든다. 계단·눈 레이어·
    #   조명 파라미터는 불변이며, 신규 프림은 전부 평탄면(테라스 z=LIFT /
    #   하부 평지 z=LOWER_TOP+LIFT) 위에만 선다(뱅크 사면 위 부유 없음).
    #   눈 캡은 snow_cover 토글에 종속 → 대응쌍(맨 계단)에서도 기하 정합.
    # -------------------------------------------------------------------
    def build_context(M):
        low_top = (LOWER_TOP if cfg["hazard_stairs"] else 0.0) + LIFT

        def base_of(kind):
            return LIFT if kind == "upper" else low_top

        def cap(path, center, size):
            """눈 캡 박판 — snow_cover ON 일 때만 생성(대응쌍 정합)."""
            if cfg["snow_cover"]:
                BOX(path, center, size, M["snow"])

        # ① 벤치 (좌판 + 다리 4 + 등받이) — 좌판·등받이 상단에 눈 캡
        bs = PARAMS["bench"]
        for i, bd in enumerate(PARAMS["benches"]):
            bz = base_of(bd["base"])
            pfx = f"{ROOT}/Bench_{i}"
            # [v5.1 §3] 축평행·정위치 해소. 벤치 0 은 제설더미·계단 어깨,
            #   벤치 1 은 제설더미 0번 앵커 옆이라 지터폭을 0.18 로 제한해
            #   기존 이격(0.22 m)을 잠식하지 않는다.
            _dx, _dy = bc.jit_pos(bd["cx"], bd["cy"], "benchC1", amp=0.18)
            _yaw = bc.jit_yaw(bd["cx"], bd["cy"], "benchC1", lo=3.0, hi=8.0,
                              base=bd["yaw"])
            sc.build_bench(stage, pfx, bd["cx"] + _dx, bd["cy"] + _dy, bz,
                           M["wood"], length=bs["length"], width=bs["width"],
                           height=bs["height"], yaw=_yaw)
            # 이하 자식 프림은 build_bench 루트 Xform 로컬 좌표(회전 상속)
            back_y = -(bs["width"] / 2.0 - 0.04)
            BOX(f"{pfx}/Back", (0.0, back_y, bs["height"] + bs["back_h"] / 2.0),
                (bs["length"], 0.06, bs["back_h"]), M["wood"])
            cap(f"{pfx}/SnowSeat",
                (0.0, 0.0, bs["height"] + bs["cap_t"] / 2.0 - 0.012),
                (bs["length"] + 0.05, bs["width"] + 0.05, bs["cap_t"]))
            cap(f"{pfx}/SnowBack",
                (0.0, back_y,
                 bs["height"] + bs["back_h"] + bs["cap_t"] / 2.0 - 0.012),
                (bs["length"] + 0.04, 0.11, bs["cap_t"]))

        # ② 가로등 (폴 + 편측 암 + 헤드) — 폴 상단·헤드에 눈 캡
        lm = PARAMS["lamp"]
        for i, ld in enumerate(PARAMS["lamps"]):
            bz = base_of(ld["base"])
            pfx = f"{ROOT}/Lamp_{i}"
            # [v5.1 §3] 위치 ±0.15 m 지터. 그림자는 여전히 x<0 테라스에만
            #   떨어지므로(그림자 방향 (−0.879,+0.477), 길이 8.5 m) 계단
            #   트레드 은닉 조건은 불변.
            _dx, _dy = bc.jit_pos(ld["cx"], ld["cy"], "lampC1", amp=0.15)
            cx, cy, arm = ld["cx"] + _dx, ld["cy"] + _dy, ld["arm"]
            CYL(f"{pfx}/Pole", (cx, cy, bz + lm["pole_h"] / 2.0),
                lm["pole_r"], lm["pole_h"], M["pole"], col=True)
            # 암은 +Y/−Y 로 뻗는 수평 실린더 → rotX 90° (축 Z→Y)
            CYL(f"{pfx}/Arm", (cx, cy + arm / 2.0, bz + lm["pole_h"] - 0.10),
                lm["arm_r"], abs(arm), M["pole"], rotX=90.0)
            hy = cy + arm
            BOX(f"{pfx}/Head", (cx, hy, bz + lm["pole_h"] - 0.18),
                (lm["head_w"], lm["head_l"], lm["head_h"]), M["lamp"])
            cap(f"{pfx}/SnowHead",
                (cx, hy, bz + lm["pole_h"] - 0.18 + lm["head_h"] / 2.0
                 + lm["cap_t"] / 2.0 - 0.010),
                (lm["head_w"] + 0.04, lm["head_l"] + 0.04, lm["cap_t"]))
            cap(f"{pfx}/SnowTop",
                (cx, cy, bz + lm["pole_h"] + lm["cap_t"] / 2.0 - 0.010),
                (lm["pole_r"] * 2.6, lm["pole_r"] * 2.6, lm["cap_t"]))

        # ③ 표지판 기둥 (안내 사인) — 패널 상단에 눈 캡
        sp = PARAMS["signpost"]
        bz = base_of("upper")
        CYL(f"{ROOT}/SignPost/Pole", (sp["cx"], sp["cy"],
                                      bz + sp["pole_h"] / 2.0),
            sp["pole_r"], sp["pole_h"], M["pole"], col=True)
        BOX(f"{ROOT}/SignPost/Panel", (sp["cx"], sp["cy"], bz + sp["panel_z"]),
            (sp["panel_t"], sp["panel_w"], sp["panel_h"]), M["sign"])
        cap(f"{ROOT}/SignPost/SnowPanel",
            (sp["cx"], sp["cy"],
             bz + sp["panel_z"] + sp["panel_h"] / 2.0 + sp["cap_t"] / 2.0
             - 0.008),
            (sp["panel_t"] + 0.05, sp["panel_w"] + 0.05, sp["cap_t"]))

        # ④ 생울타리 라인 — 상단 눈 캡(오버행)으로 겨울 정합
        hc = PARAMS["hedge_cap"]
        for i, hd in enumerate(PARAMS["hedges"]):
            bz = base_of(hd["base"])
            cx = (hd["x0"] + hd["x1"]) / 2.0
            cy = (hd["y0"] + hd["y1"]) / 2.0
            sx = hd["x1"] - hd["x0"]
            sy = hd["y1"] - hd["y0"]
            BOX(f"{ROOT}/Hedge_{i}", (cx, cy, bz + hd["h"] / 2.0),
                (sx, sy, hd["h"]), M["hedge"], col=True)
            cap(f"{ROOT}/Hedge_{i}_Snow",
                (cx, cy, bz + hd["h"] + hc["t"] / 2.0 - 0.015),
                (sx + 2.0 * hc["over"], sy + 2.0 * hc["over"], hc["t"]))

        # ⑤ 원경 저층 주택 — 벽체 + 처마 지붕 슬래브 + 눈 캡 + 굴뚝 + 창
        hs = PARAMS["house"]
        for i, hd in enumerate(PARAMS["houses"]):
            bz = base_of(hd["base"])
            pfx = f"{ROOT}/House_{i}"
            cx = (hd["x0"] + hd["x1"]) / 2.0
            cy = (hd["y0"] + hd["y1"]) / 2.0
            sx = hd["x1"] - hd["x0"]
            sy = hd["y1"] - hd["y0"]
            h = hd["h"]
            # 벽체: 기단을 foot 만큼 아래로 연장 → 지면 부유 방지
            BOX(f"{pfx}/Shell", (cx, cy, bz + (h - hs["foot"]) / 2.0),
                (sx, sy, h + hs["foot"]), M[f"brick_{i}"], col=True)
            # 처마 지붕 슬래브(오버행) — 상면 z = bz+h+roof_t
            BOX(f"{pfx}/Roof", (cx, cy, bz + h + hs["roof_t"] / 2.0),
                (sx + 2.0 * hs["eave"], sy + 2.0 * hs["eave"], hs["roof_t"]),
                M[f"roof_{i}"])
            cap(f"{pfx}/SnowRoof",
                (cx, cy, bz + h + hs["roof_t"] + hs["cap_t"] / 2.0 - 0.02),
                (sx + 2.0 * (hs["eave"] - hs["cap_inset"]),
                 sy + 2.0 * (hs["eave"] - hs["cap_inset"]), hs["cap_t"]))
            # 굴뚝(지붕 한쪽) + 눈 캡
            ch = hs["chimney_s"]
            chx = cx + sx * 0.28 * hd["face"]
            chy = cy + sy * 0.22
            BOX(f"{pfx}/Chimney",
                (chx, chy, bz + h + hs["roof_t"] + hs["chimney_h"] / 2.0
                 - 0.10),
                (ch, ch, hs["chimney_h"] + 0.20), M[f"brick_{i}"])
            cap(f"{pfx}/SnowChimney",
                (chx, chy,
                 bz + h + hs["roof_t"] + hs["chimney_h"] + hs["cap_t"] / 2.0
                 - 0.02),
                (ch + 0.06, ch + 0.06, hs["cap_t"]))
            # 창 — 카메라를 향한 면(face=-1 → -X 파사드, +1 → +X 파사드)
            # 창판(두께 0.04)을 벽면에 1cm 물려 동일평면 회피
            gx = (hd["x0"] if hd["face"] < 0 else hd["x1"]) \
                + hd["face"] * 0.01
            for r in range(hs["win_rows"]):
                zc = bz + h * (0.30 + 0.36 * r)
                for c in range(hs["win_cols"]):
                    yc = hd["y0"] + sy * (c + 0.5) / hs["win_cols"]
                    BOX(f"{pfx}/Win_{r}_{c}", (gx, yc, zc),
                        (0.04, hs["win_w"], hs["win_h"]), M["glass"])
        print(f"[드레싱] 벤치 {len(PARAMS['benches'])} · 가로등 "
              f"{len(PARAMS['lamps'])} · 표지판 1 · 생울타리 "
              f"{len(PARAMS['hedges'])} · 저층 주택 {len(PARAMS['houses'])} "
              f"(눈 캡 {'ON' if cfg['snow_cover'] else 'OFF'})")

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["stair"] if cfg["cue_material_break"] else M["concrete"]

    if cfg["hazard_stairs"]:
        build_terrace(M)
        build_lower(M)
        build_banks(M)
        build_stringers(M)
        build_stairs(stair_mtl)
        build_cues(M)
        if cfg["snow_cover"]:
            build_snow(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    print(f"[기하] run={RUN:.2f}m drop={DROP:.2f}m slope_k={SLOPE_K:.4f} "
          f"lower_top={LOWER_TOP:.3f} snow_lift={LIFT:.3f}")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneC1 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["approach"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneC1_{ts}.png")
            capture(fp)
            print(f"[캡처] {fp}")
        elif event.input == K.LEFT_BRACKET:
            dome_user_rot[0] -= rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[하늘 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        elif event.input == K.RIGHT_BRACKET:
            dome_user_rot[0] += rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[하늘 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
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
