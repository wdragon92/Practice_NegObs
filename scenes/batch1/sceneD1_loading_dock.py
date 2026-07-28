# -*- coding: utf-8 -*-
"""
sceneD1_loading_dock.py — NegObs 인공씬 33호: 하역장 ㄷ자 플랫폼 엣지 (Isaac Sim 4.5)

유형    : D1 비계단 낙차 — 물류 하역 플랫폼 연단 (낙차 1.2 m)
사양서  : Docs/nanobanana_batch1_geometry_map.md §D sceneD1_loading_dock
룩 근거 : look_refs/d1_loading_dock.jpg (v3, 온플랫폼 시점 — 주 구도)
          look_refs/d1_loading_dock_v2_overview.jpg (외부 부감 — 치수 참조)
공통    : scene_common.py (검증된 API 헬퍼) · scene16_canopy_shadow.py (표준 템플릿)

위험 본질: 플랫폼 위를 걷는 시점에서 **황·흑 사선 경고 도색 밴드가 시야를 횡단**
           하고, 그 너머 트럭 에이프런 바닥(z −1.2)은 그레이징 각에서 완전히
           은닉된다. 도색 밴드는 "여기서 끝"이 아니라 "바닥이 계속된다"는
           오독을 유발 — 낙차의 유일한 시각 단서가 **평면 도색**뿐인 케이스.
           ㄷ자 만입 베이(폭 6 × 깊이 4)가 엣지선을 90° 두 번 꺾어, 직선 연단
           가정(단일 소실선)을 무너뜨린다.
목표     : 플랫폼 슬래브(ㄷ자 베이 절개 — 3박스 분할) + 에이프런 + 베이 3면
           벽체 + 경고 도색 밴드 + 도크 범퍼 + 셔터 도어 벽·볼라드를 조립,
           렌더로 판정 (렌더 전용).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneD1_loading_dock.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneD1_loading_dock.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneD1_loading_dock.py

좌표계: Z-up, m, 진행축 +X, 낙차 시작 모서리 = x=0 (플랫폼 주 연단).
"""

import os
import math
import json
import random
import datetime

import scene_common as sc
import batch1_common as bc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 베이·연단을 메워 z=0 평지 (대조군)
    "cue_railing":        False,  # 베이 둘레 안전 난간 — 기본 OFF(무방호가 현실)
    "cue_tactile":        False,  # 해당 없음(산업 하역장) — 키만 예약
    "cue_material_break": True,   # False → 에이프런도 콘크리트(재질 대비 소거)
    "cue_nosing":         True,   # ★ 황·흑 45° 경고 도색 밴드 — 이 씬의 핵심 cue
    "cue_sign":           False,  # [선택] 미구현 — 키만 예약
    "cue_scene_dressing": True,   # 셔터 도어 벽·창고 벽·볼라드·단부 파라펫
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # 플랫폼 데크(상판). 상면 z=0, 두께 0.20. 주 연단 = x 0 (낙차 시작 모서리).
    deck=dict(x_w=-16.0, x_e=0.0, y_s=-14.0, y_n=14.0, z_top=0.0, thick=0.20),

    # ★ ㄷ자 만입 베이: 폭 6.0(y) × 깊이 4.0(x). +X 로 열려 트럭이 후진 진입.
    #   엣지선은 (0,−14)→(0,−3)→(−4,−3)→(−4,+3)→(0,+3)→(0,+14) 의 ㄷ자.
    bay=dict(x0=-4.0, x1=0.0, y0=-3.0, y1=3.0),

    # 플랫폼 매스(연단 벽체). 데크보다 setback 만큼 뒤로 물려 데크 립이
    # 3 cm 돌출 → ① 수직 동일평면 제거(Z-파이팅) ② 립 아래 그림자선 생성.
    mass=dict(z_bot=-1.35, z_top=-0.19, setback=0.03),

    # 트럭 에이프런(하부 야드). 상면 z −1.2 → 낙차 1.2 m [GT].
    apron=dict(z_top=-1.2, thick=0.6, half=40.0),

    # 경고 도색 밴드 (폭 0.35). 흑 베이스 띠(연속) + 황 45° 박판 교호.
    #   45° 회전 직사각형의 AABB 는 ((L+w)/√2)² → L = W·√2 − w 로 두면
    #   밴드 폭 W 에 정확히 내접 → **공동 위로 튀어나가는 부유 기하 0**.
    #   lip_inset: 흑 베이스 띠를 **낙차 쪽 모서리에서만** 3 mm 물려, 데크
    #   수직 절단면과의 동일평면(Z-파이팅)을 제거. 황 박판은 45° 면이라
    #   원 사각 그대로 두어도 데크 면과 평행하지 않아 안전하다.
    band=dict(width=0.35, pitch=0.38, stripe_w=0.15,
              base_proud=0.0015, base_t=0.010, lip_inset=0.003,
              stripe_proud=0.0035, stripe_t=0.006,
              seed=3301, drop_ratio=0.10, y_end=13.7),

    # 도크 범퍼 (흑 고무). 벽면 상단 부착, 간격 1.2 m.
    bumper=dict(w=0.30, proud=0.15, h=0.60, z_top=-0.30, spacing=1.2),

    # ── 볼라드 2본 (베이 코너 보호, 황색) [v5.1 §2 · ctx2] ────────────────
    #   위치 유지: 베이 코너는 트럭이 후진 진입하는 실제 충돌 우려 지점이라
    #   "차량 진입 우려 지점만" 규약에 정확히 부합한다(감독 판정).
    #   치수는 이미 규격 내(φ0.18 ∈ 0.10~0.20 · h0.95 ∈ 0.80~1.00) → 유지.
    #   추가: **상단 백색 반사띠**(야간 하역장 시인성 — 산업 관행에도 정합).
    #   ★ 점형블록은 **미설치**: 교통약자법 별표2는 보도(보행자 통행로) 규정이고
    #     여기는 차량 하역 야드다. 게다가 황색 소판이 데크 위 **경고 도색 밴드**
    #     (황흑 45°)와 색·위치가 겹쳐 판정 요소를 오염시킨다 → tactile=False.
    #   ★ 몸통은 황색 유지(v5.1 §2 "기능·관행 기반" — 산업 볼라드 표준색).
    bollards=[dict(cx=-0.75, cy=-3.9), dict(cx=-0.75, cy=3.9)],
    bollard=dict(radius=0.09, height=0.95, base_z=-0.04, tactile=False),

    # 플랫폼 단부 파라펫(±Y) — 연단 외 무방호 낙차를 없애 GT를 베이·주연단으로 한정
    parapet=dict(t=0.30, h=0.90, base_z=-0.05, outer_inset=0.02),

    # 배경: 셔터 도어 벽(+X 지평 폐쇄) + 창고 벽(-X, 플랫폼 배후)
    shutter=dict(x0=22.0, t=1.4, y_half=30.0, z_top=7.0,
                 door_w=3.6, door_h=4.2, door_embed=0.03, door_proud=0.10,
                 door_ys=[-12.0, -4.0, 4.0, 12.0],
                 rib_w=0.05, rib_proud=0.02, rib_step=0.30),
    #   x1 −15.6: 데크 서단(−16)보다 0.4 안쪽까지 물려 벽 전면과 데크/매스
    #   서측면의 동일평면(3면 맞댐 → Z-파이팅)을 제거한다.
    warehouse=dict(x1=-15.6, t=1.4, y_half=20.0, z_top=6.0),

    # ─── 맥락 드레싱 v2 (2026-07-27, 휑함 해소) ────────────────────────────
    #   목적: "여기가 물류창고 하역장"이 한눈에 읽히게. 전 요소 cue_scene_dressing
    #   소속. 낙차 기하(데크·베이·에이프런)·경고 도색·범퍼는 **일절 불변**.
    #   ★ 배치 원칙(카메라 검산은 build_yard_dressing docstring 참조):
    #     ① 데크 위 **엣지 접근 동선(x −10..0 × y −5..−3)** 에는 어떤 입체도 두지
    #        않는다(도색은 flush 이므로 허용 — 오히려 통로 판독을 돕는다).
    #     ② 판정 3컷(edge_graze / edge_walk / bay_corner)의 시야에 들어가는
    #        입체는 **엣지선 너머(x>0, 에이프런)** 이거나 **베이 북측(y>6.5)** 뿐.
    #     ③ 원경(컨테이너·창고동·조명탑)은 전부 x>6 → 데크 위 어떤 시선도
    #        가리지 못한다(에이프런 은닉 한계 x=8.2 밖이라 그레이징에서 보인다).
    yard=dict(
        # 목재 팔레트 스택 3곳. cx,cy=스택 중심, yaw=방위(도)
        stacks=[dict(tag="N1", cx=-2.55, cy=7.80, yaw=7.0, n_pallet=3, n_box=3),
                dict(tag="N2", cx=-5.60, cy=10.20, yaw=-14.0,
                     n_pallet=2, n_box=2),
                # S1: 그리드 d10 우측 하단에만 걸리는 **저스택**(총고 0.48)
                dict(tag="S1", cx=-3.60, cy=-7.40, yaw=21.0,
                     n_pallet=1, n_box=1)],
        pallet=dict(w=1.20, d=1.00, h=0.145, top_t=0.030, bot_t=0.022,
                    string_w=0.10, string_h=0.090),
        carton=dict(w=0.54, d=0.44, h=0.34, seed=5107),
        # 지게차 통행 도색(황색 마모) — 종주 아일 2쌍 + 횡단 아일 1쌍.
        #   dash/gap + seed 결락으로 마모 연출. 전부 flush(proud ≤ 0.0019).
        lane=dict(w=0.11, t=0.010, proud_main=0.0012, proud_cross=0.0019,
                  dash=1.30, gap=0.55, seed=4407, drop=0.13,
                  main_ys=(-4.60, -7.10), north_ys=(4.30, 6.50),
                  x0=-15.0, x1=-0.90,
                  cross_xs=(-11.0, -13.2), cy0=-7.10, cy1=6.50),
        # 도크 번호 표지 박판 (셔터 도어 옆, 무텍스트 색면)
        docksign=dict(w=0.70, h=0.90, z_c=2.85, off=0.62, t=0.05,
                      fw=0.40, fh=0.46),
        # 벽면 외등 박스 (주간이므로 발광 없음 — 형상·그림자만)
        lamp=dict(w=0.34, d=0.30, h=0.24, lens_t=0.035,
                  shutter_ys=(-9.0, 0.0, 9.0), shutter_z=5.30,
                  wh_ys=(-7.0, 5.0), wh_z=4.40),
        # 에이프런 위 컨테이너 (원경 실루엣 — 은닉 한계 x=8.2 밖)
        container=dict(L=12.19, W=2.44, H=2.59, gap=0.06),
        #   ★ 전 컨테이너의 **근단(min x) ≥ 8.91** — edge_graze 에이프런 은닉
        #     한계 8.23 m 밖(아래 C2 는 장축 x 방향이라 근단이 cx−L/2 임에 주의)
        containers=[dict(cx=12.60, cy=-16.0, yaw=90.0, tier=1, tone=0),
                    dict(cx=16.00, cy=13.5, yaw=90.0, tier=2, tone=1),
                    dict(cx=15.00, cy=-30.0, yaw=0.0, tier=1, tone=2)],
        # 야드 조명탑 (셔터 벽 z_top 7.0 위로 솟는 실루엣)
        masts=[dict(cx=7.40, cy=-21.0), dict(cx=8.20, cy=18.0)],
        mast=dict(r=0.10, h=8.0, head_w=0.90, head_d=0.45, head_h=0.20),
        # 원경 창고동 2동 — 셔터 벽(z 7.0) 너머로 상부만 보이는 실루엣
        sheds=[dict(x0=25.0, x1=38.0, y0=-33.0, y1=-8.0, z_top=10.6, tone=0),
               dict(x0=26.5, x1=39.5, y0=6.0, y1=31.0, z_top=9.4, tone=1)],
        shed=dict(z_bot=-1.60, band_h=0.50, band_proud=0.12,
                  vent_w=0.90, vent_h=0.70, vent_n=3),
    ),

    # 베이 둘레 난간 (cue_railing=True 일 때만)
    bay_rail=dict(rail_h=1.05, post_r=0.030, rail_r=0.025, mid_h=0.52,
                  offset=0.35, spacing=1.5),

    material=dict(
        scale=dict(concrete_floor=1.4, concrete_wall=2.2, wood_dark=0.55),
        deck_tint=(0.86, 0.85, 0.83),        # 빗자루 마감 콘크리트(밝은 회)
        wall_tint=(0.80, 0.79, 0.77),        # 연단 벽체(약간 어둡게)
        # 아스팔트 상수색 — scene11/17 규약과 동일
        asphalt_color=(0.16, 0.16, 0.17), asphalt_rough=0.90,
        # 경고 도색: 흑은 sRGB 암색 대역 0.02~0.06 [교훈 1]
        band_black=(0.045, 0.045, 0.047), band_black_rough=0.88,
        #   황 3단(신품→중간→마모) — 마모는 채도·명도 저하로 연출
        band_yellow=[(0.85, 0.72, 0.10), (0.70, 0.60, 0.14),
                     (0.52, 0.46, 0.20)],
        band_yellow_w=[0.45, 0.35, 0.20],
        band_yellow_rough=[0.75, 0.85, 0.92],
        # 흑 고무 범퍼
        rubber_color=(0.035, 0.035, 0.037), rubber_rough=0.90,
        bollard_color=(0.72, 0.60, 0.08), bollard_metallic=0.1,
        bollard_rough=0.65,
        # 상단 반사띠(백색, 본당 0.11 m² — 소면적이라 v5.1 §4 대면적 금지 무관)
        bollard_band_color=(0.88, 0.88, 0.86),
        shutter_color=(0.44, 0.45, 0.47), shutter_metallic=0.30,
        shutter_rough=0.48,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # ── 맥락 드레싱 v2 ── (소품 중간톤 0.18~0.35 규약 — 교훈 ②
        #    "회색 잔해 0.55는 백색 지각". 암색 대역 0.02~0.09 는 개구·고무만.)
        pallet_tint=(1.00, 0.94, 0.86),          # wood_dark(≈0.18) × → 목재 팔레트
        pallet_rough=0.90,
        carton_colors=[(0.32, 0.25, 0.16), (0.27, 0.21, 0.14),
                       (0.35, 0.29, 0.20)],
        carton_rough=0.93,
        sign_face=(0.72, 0.72, 0.69), sign_field=(0.055, 0.055, 0.060),
        sign_rough=0.60,
        lamp_body=(0.20, 0.21, 0.22), lamp_metallic=0.40, lamp_rough=0.50,
        lamp_lens=(0.56, 0.56, 0.53), lamp_lens_rough=0.22,
        container_colors=[(0.34, 0.15, 0.11), (0.13, 0.26, 0.32),
                          (0.30, 0.31, 0.29)],
        container_metallic=0.35, container_rough=0.62,
        container_door_mul=0.82,                 # 도어단 = 본체 × 0.82 (음영차)
        shed_colors=[(0.42, 0.43, 0.45), (0.38, 0.40, 0.42)],
        shed_band=(0.52, 0.53, 0.54),
        shed_metallic=0.25, shed_rough=0.55,
        galv_color=(0.46, 0.47, 0.48), galv_metallic=0.55, galv_rough=0.45,
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
    # ─── SUN_AZ_OFFSET 근거 (씬별 재정의 — 브리프 v3 §A-7) ───
    #   태양 매핑 월드 az ≈ 33.5 + offset = 205  →  그림자 az = az−180 = 25°
    #   (기본값 171.5 를 그대로 채택하되, 아래 근거로 이 씬에 최적임을 확인)
    #   ① 태양이 카메라 등 뒤(-X 측) → 플랫폼 데크가 정면광, **경고 도색 밴드의
    #      황·흑 대비가 최대**로 읽힌다(밴드가 이 씬의 유일한 cue).
    #   ② 그림자가 +X 로 25° 기울어 뻗음. 주 연단(x=0, 높이 1.2 m)이
    #      에이프런에 1.2/tan(49.79°) = 1.02 m 폭의 **암대(暗帶)** 를 드리워,
    #      밴드 너머 에이프런 근경이 어두워진다 → 은닉 효과 강화.
    #   ③ 베이 내부: 배면 벽(x=−4)이 +X 성분(0.92 m), 남측 벽(y=−3)이
    #      +Y 성분(0.43 m)으로 각각 그림자를 던져 **베이 바닥 하부가 L자로
    #      어두워진다** — 만입부가 '더 깊은 구멍'으로 읽히는 방위.
    #   [ ]키(dome_rotation_step 15°)로 GUI 추가 스윕 가능.
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneD1")

ASSET_ROLES = ["concrete_floor", "concrete_wall", "wood_dark", "hdri", "mdl"]

# grid_views 기준선: 베이(y ±3)를 피해 데크 위에 서는 y. −4.0 이면
#   · 카메라가 항상 Deck_S(y −14..−3) 위 → 허공 배치 없음
#   · d2 에서도 베이 코너(0,−3)가 시축에서 26.6° → hfov 60° 프레임 안
GRID_GY = -4.0


def build_views():
    """카메라 프리셋: grid_views(gy=−4.0, **엣지 직교 접근**) + 미장센 4컷.

    사양서 §D 카메라: 플랫폼 위 h0.9 종주 + 직교 접근 + 베이 코너 미장센.
    판정 포인트 = edge_graze 에서 에이프런 바닥이 경고 밴드 너머로 완전 은닉.
    """
    views = sc.grid_views(GRID_GY)
    # edge_approach: 보행자가 연단으로 직교 접근 (h0.9) — 밴드가 시야를 횡단
    views["edge_approach"] = dict(eye=[-4.0, -4.0, 0.9],
                                  tgt=[1.0, -3.4, -0.40])
    # edge_walk: 엣지 평행 종주 — 밴드가 소실점으로 수렴, ㄷ자 꺾임이 드러남
    views["edge_walk"] = dict(eye=[-1.25, -9.0, 0.9], tgt=[-0.75, 0.5, 0.30])
    # edge_graze: 저시점 그레이징 — 에이프런이 밴드 너머로 은닉(v3 레퍼런스 재현)
    #   eye z 0.35 · 엣지까지 2.4 m → 은닉 한계 x = 1.2·2.4/0.35 = 8.2 m
    views["edge_graze"] = dict(eye=[-2.4, -5.2, 0.35], tgt=[1.6, -3.0, 0.05])
    # bay_corner: 베이 코너 미장센 — 도색 90° 꺾임 + 범퍼 열 + 만입 깊이
    views["bay_corner"] = dict(eye=[-1.10, -5.0, 1.55], tgt=[-2.8, -0.6, -0.85])
    # beauty_overview: 사선 부감 — ㄷ자 전모
    views["beauty_overview"] = dict(eye=[-9.0, -9.5, 3.8], tgt=[-1.5, 0.0, -0.7])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. edge_graze (h0.35)  — **에이프런이 경고 밴드 너머로 완전 은닉**되는가(판정 1순위)
 2. edge_walk           — 밴드가 종주 소실선으로 수렴 + ㄷ자 90° 꺾임 판독
 3. bay_corner          — 도색 코너 연결·범퍼 열·만입 깊이 1.2 m 인지
 4. grid preset h0.9_d5 — 엣지 직교 접근에서 낙차 경계가 화면을 횡단
 5. 도색 밴드           — 황 박판이 밴드(0.35) 안에 내접, 공동 위 부유 없음
 6. 보행 연속성         — 데크가 베이를 우회 가능(y±3 바깥), 단부 파라펫으로 폐쇄
 7. Z-파이팅            — 데크 립 setback 0.03, 밴드 proud 0.0015/0.0035 층 분리"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene33")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene33"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def OBOX(path, center, size, mtl=None, rotz=0.0, rotx=0.0):
        return sc._oriented_box(stage, path, center, size, mtl,
                                rotz=rotz, rotx=rotx)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    def RECT(path, x0, y0, x1, y1, z_c, hz, mtl=None, col=False):
        """평면 사각(x0..x1, y0..y1) → 중심·크기 변환 박스."""
        return BOX(path, ((x0 + x1) / 2.0, (y0 + y1) / 2.0, z_c),
                   (x1 - x0, y1 - y0, hz), mtl, col=col)

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["deck"] = PBR(
            f"{ROOT}/Looks/Deck", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["deck_tint"])
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["wall_tint"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["band_black"] = PBR(f"{ROOT}/Looks/BandBlack",
                              diffuse_color=mp["band_black"],
                              roughness_const=mp["band_black_rough"])
        for i, c in enumerate(mp["band_yellow"]):
            M[f"band_y{i}"] = PBR(
                f"{ROOT}/Looks/BandYellow_{i}", diffuse_color=c,
                roughness_const=mp["band_yellow_rough"][i])
        M["rubber"] = PBR(f"{ROOT}/Looks/Rubber",
                          diffuse_color=mp["rubber_color"],
                          roughness_const=mp["rubber_rough"], metallic=0.0)
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        M["shutter"] = PBR(f"{ROOT}/Looks/Shutter",
                           diffuse_color=mp["shutter_color"],
                           metallic=mp["shutter_metallic"],
                           roughness_const=mp["shutter_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # ── 맥락 드레싱 v2 재질 ──
        M["pallet"] = PBR(
            f"{ROOT}/Looks/Pallet", sc.tex_path("wood_dark", "diff"),
            sc.tex_path("wood_dark", "nor"), sc.tex_path("wood_dark", "rough"),
            sca["wood_dark"], tint=mp["pallet_tint"])
        for i, c in enumerate(mp["carton_colors"]):
            M[f"carton{i}"] = PBR(f"{ROOT}/Looks/Carton_{i}",
                                  diffuse_color=c,
                                  roughness_const=mp["carton_rough"])
        M["sign_face"] = PBR(f"{ROOT}/Looks/SignFace",
                             diffuse_color=mp["sign_face"],
                             roughness_const=mp["sign_rough"])
        M["sign_field"] = PBR(f"{ROOT}/Looks/SignField",
                              diffuse_color=mp["sign_field"],
                              roughness_const=mp["sign_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_body"],
                        metallic=mp["lamp_metallic"],
                        roughness_const=mp["lamp_rough"])
        M["lens"] = PBR(f"{ROOT}/Looks/Lens", diffuse_color=mp["lamp_lens"],
                        roughness_const=mp["lamp_lens_rough"])
        k = mp["container_door_mul"]
        for i, c in enumerate(mp["container_colors"]):
            M[f"cont{i}"] = PBR(f"{ROOT}/Looks/Container_{i}",
                                diffuse_color=c,
                                metallic=mp["container_metallic"],
                                roughness_const=mp["container_rough"])
            M[f"cont{i}_d"] = PBR(
                f"{ROOT}/Looks/ContainerDoor_{i}",
                diffuse_color=tuple(v * k for v in c),
                metallic=mp["container_metallic"],
                roughness_const=mp["container_rough"])
        for i, c in enumerate(mp["shed_colors"]):
            M[f"shed{i}"] = PBR(f"{ROOT}/Looks/Shed_{i}", diffuse_color=c,
                                metallic=mp["shed_metallic"],
                                roughness_const=mp["shed_rough"])
        M["shed_band"] = PBR(f"{ROOT}/Looks/ShedBand",
                             diffuse_color=mp["shed_band"],
                             metallic=mp["shed_metallic"],
                             roughness_const=mp["shed_rough"])
        M["galv"] = PBR(f"{ROOT}/Looks/Galv", diffuse_color=mp["galv_color"],
                        metallic=mp["galv_metallic"],
                        roughness_const=mp["galv_rough"])
        return M

    # -------------------------------------------------------------------
    # 에이프런(하부 야드) — 4박스 분할.
    #   S/N 은 데크 밑으로 under(0.30) 만큼 들어가 립 아래 틈을 막고,
    #   중앙 스트립(Apron_C)과 베이 바닥(Apron_Bay)은 x=0 에서 **정확히 맞닿아**
    #   상면 겹침(동일평면 Z-파이팅) 없이 이어진다.
    # -------------------------------------------------------------------
    def build_apron(M, mtl):
        ap = PARAMS["apron"]
        by = PARAMS["bay"]
        ms = PARAMS["mass"]
        H, th = ap["half"], ap["thick"]
        cz = ap["z_top"] - th / 2.0
        sb = ms["setback"]
        # 베이 벽면(y ±(3+sb), x −4−sb)보다 0.05 더 파고들어 벽 안쪽에 매입
        ye = by["y1"] + sb + 0.05
        xb = by["x0"] - sb - 0.05
        RECT(f"{ROOT}/Apron_S", -H, -H, H, -ye, cz, th, mtl, col=True)
        RECT(f"{ROOT}/Apron_N", -H, ye, H, H, cz, th, mtl, col=True)
        RECT(f"{ROOT}/Apron_C", by["x1"], -ye, H, ye, cz, th, mtl, col=True)
        RECT(f"{ROOT}/Apron_Bay", xb, -ye, by["x1"], ye, cz, th, mtl, col=True)

    # -------------------------------------------------------------------
    # 플랫폼 — **ㄷ자 베이 절개: 데크 3박스 + 매스 3박스 분할** (교훈 5)
    #   베이 공동 위를 어떤 박스도 덮지 않는다.
    # -------------------------------------------------------------------
    def build_platform(M):
        d = PARAMS["deck"]
        by = PARAMS["bay"]
        ms = PARAMS["mass"]
        th = d["thick"]
        czd = d["z_top"] - th / 2.0
        sb = ms["setback"]
        czm = (ms["z_bot"] + ms["z_top"]) / 2.0
        hzm = ms["z_top"] - ms["z_bot"]
        # ── 데크 상판 3분할 ──
        RECT(f"{ROOT}/Deck_W", d["x_w"], d["y_s"], by["x0"], d["y_n"],
             czd, th, M["deck"], col=True)
        RECT(f"{ROOT}/Deck_S", by["x0"], d["y_s"], d["x_e"], by["y0"],
             czd, th, M["deck"], col=True)
        RECT(f"{ROOT}/Deck_N", by["x0"], by["y1"], d["x_e"], d["y_n"],
             czd, th, M["deck"], col=True)
        # ── 매스(연단 벽체) 3분할 — 노출면을 setback 만큼 물림 ──
        #    Mass_S/N 은 Mass_W 와 0.07 겹쳐 내부 맞댐면 제거
        RECT(f"{ROOT}/Mass_W", d["x_w"], d["y_s"] + sb, by["x0"] - sb,
             d["y_n"] - sb, czm, hzm, M["wall"], col=True)
        #    ±Y 외곽면은 Mass_W 보다 0.02 안쪽, z 범위도 0.005/0.01 안쪽 →
        #    코너 겹침부의 외벽면·상하면 동일평면 제거
        czs, hzs = czm + 0.0025, hzm - 0.015
        RECT(f"{ROOT}/Mass_S", by["x0"] - sb - 0.07, d["y_s"] + sb + 0.02,
             d["x_e"] - sb, by["y0"] - sb, czs, hzs, M["wall"], col=True)
        RECT(f"{ROOT}/Mass_N", by["x0"] - sb - 0.07, by["y1"] + sb,
             d["x_e"] - sb, d["y_n"] - sb - 0.02, czs, hzs, M["wall"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 베이·연단을 메워 전 영역 z=0 평지."""
        d = PARAMS["deck"]
        ap = PARAMS["apron"]
        H = ap["half"]
        RECT(f"{ROOT}/FlatDeck", d["x_w"], -H, H, H,
             d["z_top"] - 0.5, 1.0, M["deck"], col=True)

    # -------------------------------------------------------------------
    # 경고 도색 밴드 — 흑 베이스 띠 + 황 45° 박판 교호 (마모 = 틴트 3단 + 결락)
    #   ㄷ자 엣지선을 **서로 겹치지 않는 5개 사각 구간**으로 분해해
    #   코너에서 베이스 띠가 겹치는 동일평면(Z-파이팅)을 원천 제거한다.
    # -------------------------------------------------------------------
    def band_segments():
        by = PARAMS["bay"]
        bd = PARAMS["band"]
        W = bd["width"]
        ye = bd["y_end"]
        x0, x1, y0, y1 = by["x0"], by["x1"], by["y0"], by["y1"]
        # (이름, x0, y0, x1, y1, 장축, 낙차 쪽 모서리들)
        return [
            # 주 연단 남 구간 (베이 코너 도색과 겹치지 않게 y −3−W 에서 시작)
            ("MainS", x1 - W, -ye, x1, y0 - W, "y", ("x1",)),
            ("MainN", x1 - W, y1 + W, x1, ye, "y", ("x1",)),
            # 베이 남·북 벽 상단 (코너 정사각까지 포함해 x 방향으로 연장)
            #   동단(x1=0)도 주 연단 낙차면이므로 함께 물린다
            ("BayS", x0 - W, y0 - W, x1, y0, "x", ("y1", "x1")),
            ("BayN", x0 - W, y1, x1, y1 + W, "x", ("y0", "x1")),
            # 베이 배면 벽 상단 (남·북 구간과 y=±3 에서 맞닿음)
            ("BayBack", x0 - W, y0, x0, y1, "y", ("x1",)),
        ]

    def build_band(M):
        bd = PARAMS["band"]
        W, w = bd["width"], bd["stripe_w"]
        # 45° 회전 직사각형이 폭 W 밴드에 정확히 내접하는 장변 길이
        L = W * math.sqrt(2.0) - w
        cz_base = bd["base_proud"] - bd["base_t"] / 2.0
        cz_st = bd["stripe_proud"] - bd["stripe_t"] / 2.0
        rng = random.Random(bd["seed"])
        yell = [M[f"band_y{i}"] for i in range(len(mp["band_yellow"]))]
        wts = mp["band_yellow_w"]
        n_stripe = 0
        ins = bd["lip_inset"]
        for name, x0, y0, x1, y1, axis, dsides in band_segments():
            bx0, by0, bx1, by1 = x0, y0, x1, y1
            for dside in dsides:
                if dside == "x1":
                    bx1 -= ins
                elif dside == "x0":
                    bx0 += ins
                elif dside == "y1":
                    by1 -= ins
                else:
                    by0 += ins
            RECT(f"{ROOT}/Band_{name}_Base", bx0, by0, bx1, by1,
                 cz_base, bd["base_t"], M["band_black"])
            if axis == "y":
                a0, a1 = y0, y1
                cc = (x0 + x1) / 2.0
            else:
                a0, a1 = x0, x1
                cc = (y0 + y1) / 2.0
            n = max(int((a1 - a0) / bd["pitch"]), 1)
            for i in range(n):
                a = a0 + (i + 0.5) * (a1 - a0) / n
                if rng.random() < bd["drop_ratio"]:
                    continue                       # 도색 결락(마모)
                mtl = rng.choices(yell, weights=wts, k=1)[0]
                cx, cy = (cc, a) if axis == "y" else (a, cc)
                OBOX(f"{ROOT}/Band_{name}_S_{i}", (cx, cy, cz_st),
                     (L, w, bd["stripe_t"]), mtl, rotz=45.0)
                n_stripe += 1
        return n_stripe

    # -------------------------------------------------------------------
    # 도크 범퍼 — 흑 고무 박스, 벽면 상단 부착(간격 1.2 m). 데크 립보다
    #   앞으로 돌출해 연단 아래 그림자에 리듬을 만든다(레퍼런스 재현).
    # -------------------------------------------------------------------
    def build_bumpers(M):
        bp = PARAMS["bumper"]
        by = PARAMS["bay"]
        d = PARAMS["deck"]
        sb = PARAMS["mass"]["setback"]
        cz = bp["z_top"] - bp["h"] / 2.0
        idx = [0]

        def row(face_c, a0, a1, axis, sgn):
            """axis='y': 벽면이 x=face_c, 범퍼가 sgn·x 로 돌출 / 'x': 그 반대."""
            span = a1 - a0
            n = max(int(span / bp["spacing"]), 1)
            for i in range(n):
                a = a0 + (i + 0.5) * span / n
                # 벽면에 0.03 매입 + proud 만큼 돌출
                c_off = sgn * (bp["proud"] / 2.0 - 0.015)
                if axis == "y":
                    ctr = (face_c + c_off, a, cz)
                    size = (bp["proud"] + 0.03, bp["w"], bp["h"])
                else:
                    ctr = (a, face_c + c_off, cz)
                    size = (bp["w"], bp["proud"] + 0.03, bp["h"])
                BOX(f"{ROOT}/Bumper_{idx[0]}", ctr, size, M["rubber"])
                idx[0] += 1

        # 베이 배면 벽 (x = −4−sb, +X 로 돌출)
        row(by["x0"] - sb, by["y0"], by["y1"], "y", +1.0)
        # 베이 남·북 벽 (y = ∓(3+sb), 베이 안쪽으로 돌출)
        row(by["y0"] - sb, by["x0"], by["x1"], "x", +1.0)
        row(by["y1"] + sb, by["x0"], by["x1"], "x", -1.0)
        # 주 연단 (x = −sb, +X 로 돌출) — 베이 바깥 남·북 구간
        row(d["x_e"] - sb, d["y_s"] + 1.0, by["y0"] - 0.6, "y", +1.0)
        row(d["x_e"] - sb, by["y1"] + 0.6, d["y_n"] - 1.0, "y", +1.0)
        return idx[0]

    # -------------------------------------------------------------------
    # 단부 파라펫(±Y) — 플랫폼 단부의 무방호 낙차 제거 (GT를 ㄷ자 엣지로 한정)
    # -------------------------------------------------------------------
    def build_parapets(M):
        d = PARAMS["deck"]
        pp = PARAMS["parapet"]
        cz = (pp["base_z"] + pp["h"]) / 2.0
        hz = pp["h"] - pp["base_z"]
        # 연단 쪽 끝을 0.05, 외곽(±Y)면을 outer_inset 만큼 물려
        # 데크 절단면과의 동일평면 회피
        xe = d["x_e"] - 0.05
        oi = pp["outer_inset"]
        RECT(f"{ROOT}/Parapet_S", d["x_w"], d["y_s"] + oi, xe,
             d["y_s"] + pp["t"], cz, hz, M["wall"], col=True)
        RECT(f"{ROOT}/Parapet_N", d["x_w"], d["y_n"] - pp["t"], xe,
             d["y_n"] - oi, cz, hz, M["wall"], col=True)

    # -------------------------------------------------------------------
    # 배경 드레싱 — 셔터 도어 벽(+X 지평 폐쇄) · 창고 벽(-X) · 볼라드 2본
    # -------------------------------------------------------------------
    def build_dressing(M):
        sh = PARAMS["shutter"]
        ap = PARAMS["apron"]
        zb = ap["z_top"] - 0.3
        # +X 셔터 도어 벽 — 주 카메라 축 정면 지평 폐쇄 (브리프 §A-4)
        RECT(f"{ROOT}/ShutterWall", sh["x0"], -sh["y_half"],
             sh["x0"] + sh["t"], sh["y_half"],
             (zb + sh["z_top"]) / 2.0, sh["z_top"] - zb, M["wall"], col=True)
        dw, dh = sh["door_w"], sh["door_h"]
        dz0 = ap["z_top"] - 0.05          # 하단을 에이프런에 0.05 매입(동일평면 회피)
        for j, dy in enumerate(sh["door_ys"]):
            # 도어 패널: 벽면(x0)에 door_embed 매입 + door_proud 돌출
            px0 = sh["x0"] - sh["door_proud"]
            px1 = sh["x0"] + sh["door_embed"]
            RECT(f"{ROOT}/Door_{j}", px0, dy - dw / 2.0, px1, dy + dw / 2.0,
                 dz0 + dh / 2.0, dh, M["shutter"])
            # 세로 리브 (패널 앞면에 proud)
            nr = max(int(dw / sh["rib_step"]), 1)
            for k in range(nr):
                ry = dy - dw / 2.0 + (k + 0.5) * dw / nr
                RECT(f"{ROOT}/Door_{j}_Rib_{k}",
                     px0 - sh["rib_proud"], ry - sh["rib_w"] / 2.0,
                     px0 + 0.02, ry + sh["rib_w"] / 2.0,
                     dz0 + 0.03 + (dh - 0.09) / 2.0, dh - 0.09, M["shutter"])
        # -X 창고 벽 (플랫폼 배후) — 부지 폐쇄
        wh = PARAMS["warehouse"]
        RECT(f"{ROOT}/Warehouse", wh["x1"] - wh["t"], -wh["y_half"],
             wh["x1"], wh["y_half"],
             (zb + wh["z_top"]) / 2.0, wh["z_top"] - zb, M["wall"], col=True)
        # 황색 볼라드 2본 (베이 코너 보호) — v5.1 규격 + 상단 반사띠,
        #   점형블록은 산업 야드라 미설치(PARAMS 주석 참조).
        bo = PARAMS["bollard"]
        for i, bd in enumerate(PARAMS["bollards"]):
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{i}", bd["cx"],
                                 bd["cy"], bo["base_z"], None, M["bollard"],
                                 M["bollard_band"], None,
                                 radius=bo["radius"], height=bo["height"],
                                 tactile=bo["tactile"])

    # -------------------------------------------------------------------
    # 맥락 드레싱 v2 — 팔레트 스택 · 지게차 통행 도색 · 도크 번호 표지 ·
    #                  벽면 외등 · 에이프런 컨테이너 · 조명탑 · 원경 창고동
    # -------------------------------------------------------------------
    def build_yard_dressing(M):
        """물류창고 하역장 맥락 요소. **낙차 기하·도색 밴드·범퍼·에이프런 불변.**

        ── 카메라 검산 (전 뷰, 좌표 계산 근거) ─────────────────────────────
        시야: grid_views hfov 60°(half tan 0.577) · pitch −10° · 16:9 → vfov 36°.
        1) 데크 위 신규 입체는 팔레트 스택 3곳뿐.
           N1(−2.55, 7.80) / N2(−5.60, 10.20): **베이 북립(y=3) 너머**.
             · grid(gy=−4): 프레임 좌한 y ≤ −4+0.577·(x+10) → x=−2.55 에서 y ≤ 0.30
               → y 7.8/10.2 는 **프레임 밖**(가림 0).
             · edge_walk(eye −1.25,−9 → tgt −0.75,0.5): 축에서 9.6°(프레임 안)이나
               베이·주연단 도색(y ≤ 3.35)보다 **먼 쪽**이라 원리상 가림 불가.
             · bay_corner(eye −1.10,−5.0,1.55, 하향 27°): 수평 24.8°/수직 −4.3° →
               vfov 상한(−27+18=−9°) 위 → 프레임 밖.
           S1(−3.60, −7.40, 총고 0.48): 남측 스테이징.
             · grid d10(eye −10,−4): 프레임 우한 y ≥ −4−0.577·6.4 = −7.69 → 걸침.
               이 스택이 가리는 주연단 지점 = y −4+(10/6.4)(−3.4) = −9.31 ..
               프레임 우한 −9.77 사이의 **최우측 코너 0.46 m 구간뿐**(판정 대상인
               중앙부 밴드·베이 코너는 전혀 가리지 않음).
             · d5/d2·edge_approach·edge_graze: 축 밖 또는 카메라 뒤 → 무관.
             · beauty_overview(eye −9,−9.5,3.8): 시축에서 30.4° → 프레임 경계 밖.
        2) 통행 도색은 flush(proud ≤ 0.0019) — 은닉·가림에 영향 없음.
           엣지 접근 동선(x −10..0 × y −5..−3)에는 **입체 0**(도색만).
        3) 원경(컨테이너·조명탑·창고동)은 전부 x ≥ 7.4 = 낙차 너머.
           edge_graze(eye z 0.35, 엣지까지 2.4 m) 은닉 한계 x = 1.2·2.4/0.35
           = 8.23 m → 컨테이너 근단 min x = 8.91(C2) 로 **은닉 한계 밖**이라
           에이프런 근경 은닉을 깨지 않으면서 원경 맥락만 준다.
        4) 카메라 위치(전 뷰 eye) 최근접 신규 프림 = S1 스택(−3.60,−7.40) ↔
           beauty_overview eye(−9.0,−9.5,3.8): 수평 6.0 m·수직 3.3 m → 매몰 없음.
        """
        yd = PARAMS["yard"]
        sh = PARAMS["shutter"]
        ap = PARAMS["apron"]
        cnt = dict(pallet=0, carton=0, lane=0, sign=0, lamp=0,
                   container=0, mast=0, shed=0)

        # ── ① 목재 팔레트 스택 (박스 적층 근사) ──
        pl = yd["pallet"]
        ct = yd["carton"]
        ph = pl["bot_t"] + pl["string_h"] + pl["top_t"]      # 실높이(무공극)
        crng = random.Random(ct["seed"])
        ncar = len(mp["carton_colors"])
        for st in yd["stacks"]:
            cx, cy, yaw = st["cx"], st["cy"], st["yaw"]
            a = math.radians(yaw)
            ca, sa = math.cos(a), math.sin(a)

            def place(dx, dy, _cx=cx, _cy=cy, _ca=ca, _sa=sa):
                return (_cx + dx * _ca - dy * _sa, _cy + dx * _sa + dy * _ca)

            tag = st["tag"]
            for i in range(int(st["n_pallet"])):
                z0 = i * ph
                OBOX(f"{ROOT}/Pallet_{tag}_{i}_Bot",
                     (cx, cy, z0 + pl["bot_t"] / 2.0),
                     (pl["w"], pl["d"], pl["bot_t"]), M["pallet"], rotz=yaw)
                for j, dx in enumerate((-(pl["w"] - pl["string_w"]) / 2.0, 0.0,
                                        (pl["w"] - pl["string_w"]) / 2.0)):
                    sx, sy = place(dx, 0.0)
                    OBOX(f"{ROOT}/Pallet_{tag}_{i}_S{j}",
                         (sx, sy, z0 + pl["bot_t"] + pl["string_h"] / 2.0),
                         (pl["string_w"], pl["d"], pl["string_h"]),
                         M["pallet"], rotz=yaw)
                OBOX(f"{ROOT}/Pallet_{tag}_{i}_Top",
                     (cx, cy, z0 + ph - pl["top_t"] / 2.0),
                     (pl["w"], pl["d"], pl["top_t"]), M["pallet"], rotz=yaw)
                cnt["pallet"] += 1
            zc0 = int(st["n_pallet"]) * ph
            for b in range(int(st["n_box"])):
                bx, by = place(crng.uniform(-0.15, 0.15),
                               crng.uniform(-0.11, 0.11))
                OBOX(f"{ROOT}/Carton_{tag}_{b}",
                     (bx, by, zc0 + ct["h"] * (b + 0.5)),
                     (ct["w"], ct["d"], ct["h"]),
                     M[f"carton{crng.randrange(ncar)}"],
                     rotz=yaw + crng.uniform(-9.0, 9.0))
                cnt["carton"] += 1

        # ── ② 지게차 통행 도색 (황색 마모 파선) ──
        ln = yd["lane"]
        lrng = random.Random(ln["seed"])
        ymtl = [M["band_y1"], M["band_y2"]]
        cz_m = ln["proud_main"] - ln["t"] / 2.0
        cz_c = ln["proud_cross"] - ln["t"] / 2.0     # 교차부는 0.7 mm 위 → 코플래너 0

        def dashed(tag, a0, a1, fixed, axis, cz):
            step = ln["dash"] + ln["gap"]
            n = max(int((a1 - a0) / step), 1)
            k = 0
            for i in range(n):
                s = a0 + i * step
                e = min(s + ln["dash"], a1)
                if e - s < 0.30 or lrng.random() < ln["drop"]:
                    continue
                mtl = ymtl[lrng.randrange(len(ymtl))]
                if axis == "x":
                    RECT(f"{ROOT}/Lane_{tag}_{k}", s, fixed - ln["w"] / 2.0,
                         e, fixed + ln["w"] / 2.0, cz, ln["t"], mtl)
                else:
                    RECT(f"{ROOT}/Lane_{tag}_{k}", fixed - ln["w"] / 2.0, s,
                         fixed + ln["w"] / 2.0, e, cz, ln["t"], mtl)
                k += 1
            cnt["lane"] += k

        for i, ly in enumerate(ln["main_ys"]):
            dashed(f"MS{i}", ln["x0"], ln["x1"], ly, "x", cz_m)
        for i, ly in enumerate(ln["north_ys"]):
            dashed(f"MN{i}", ln["x0"], ln["x1"], ly, "x", cz_m)
        for i, lx in enumerate(ln["cross_xs"]):
            dashed(f"CX{i}", ln["cy0"], ln["cy1"], lx, "y", cz_c)

        # ── ③ 도크 번호 표지 박판 (셔터 도어 옆, 무텍스트 색면) ──
        ds = yd["docksign"]
        px1 = sh["x0"] + 0.01                     # 벽면(22.0)에 1 cm 물림
        px0 = px1 - ds["t"]
        for j, dy in enumerate(sh["door_ys"]):
            sy = dy - sh["door_w"] / 2.0 - ds["off"]
            RECT(f"{ROOT}/DockSign_{j}", px0, sy - ds["w"] / 2.0,
                 px1, sy + ds["w"] / 2.0, ds["z_c"], ds["h"], M["sign_face"])
            RECT(f"{ROOT}/DockSign_{j}_F", px0 - 0.012, sy - ds["fw"] / 2.0,
                 px0 + 0.010, sy + ds["fw"] / 2.0, ds["z_c"] - 0.03,
                 ds["fh"], M["sign_field"])
            cnt["sign"] += 1

        # ── ④ 벽면 외등 박스 (주간 — 발광 없음) ──
        lp = yd["lamp"]
        wh = PARAMS["warehouse"]
        for j, ly in enumerate(lp["shutter_ys"]):
            bx1 = sh["x0"] + 0.02
            bx0 = bx1 - lp["d"]
            RECT(f"{ROOT}/WallLamp_S{j}", bx0, ly - lp["w"] / 2.0,
                 bx1, ly + lp["w"] / 2.0, lp["shutter_z"], lp["h"], M["lamp"])
            RECT(f"{ROOT}/WallLamp_S{j}_L", bx0 - lp["lens_t"],
                 ly - lp["w"] / 2.0 + 0.05, bx0 + 0.01,
                 ly + lp["w"] / 2.0 - 0.05, lp["shutter_z"] - 0.03,
                 lp["h"] - 0.09, M["lens"])
            cnt["lamp"] += 1
        for j, ly in enumerate(lp["wh_ys"]):
            bx0 = wh["x1"] - 0.02
            bx1 = bx0 + lp["d"]
            RECT(f"{ROOT}/WallLamp_W{j}", bx0, ly - lp["w"] / 2.0,
                 bx1, ly + lp["w"] / 2.0, lp["wh_z"], lp["h"], M["lamp"])
            RECT(f"{ROOT}/WallLamp_W{j}_L", bx1 - 0.01,
                 ly - lp["w"] / 2.0 + 0.05, bx1 + lp["lens_t"],
                 ly + lp["w"] / 2.0 - 0.05, lp["wh_z"] - 0.03,
                 lp["h"] - 0.09, M["lens"])
            cnt["lamp"] += 1

        # ── ⑤ 에이프런 컨테이너 (원경 실루엣 — 은닉 한계 8.2 m 밖) ──
        cn = yd["container"]
        for j, cd in enumerate(yd["containers"]):
            a = math.radians(cd["yaw"])
            for t in range(int(cd["tier"])):
                zb = ap["z_top"] + t * (cn["H"] - cn["gap"])
                zc = zb + cn["H"] / 2.0
                OBOX(f"{ROOT}/Container_{j}_{t}", (cd["cx"], cd["cy"], zc),
                     (cn["L"], cn["W"], cn["H"]), M[f"cont{cd['tone']}"],
                     rotz=cd["yaw"])
                # 도어단: 본체보다 1 cm 돌출·1.5 cm 넓게·상하 3 cm 안쪽 → 코플래너 0
                ex = cd["cx"] + math.cos(a) * (cn["L"] / 2.0 - 0.05)
                ey = cd["cy"] + math.sin(a) * (cn["L"] / 2.0 - 0.05)
                OBOX(f"{ROOT}/Container_{j}_{t}_D", (ex, ey, zc),
                     (0.12, cn["W"] + 0.015, cn["H"] - 0.06),
                     M[f"cont{cd['tone']}_d"], rotz=cd["yaw"])
                cnt["container"] += 1

        # ── ⑥ 야드 조명탑 (셔터 벽 z 7.0 위로 솟는 실루엣) ──
        ms = yd["mast"]
        for j, md in enumerate(yd["masts"]):
            zb = ap["z_top"] - 0.10                # 에이프런에 0.10 매입
            CYL(f"{ROOT}/Mast_{j}", (md["cx"], md["cy"], zb + ms["h"] / 2.0),
                ms["r"], ms["h"], M["galv"])
            BOX(f"{ROOT}/Mast_{j}_Head",
                (md["cx"], md["cy"], zb + ms["h"] - ms["head_h"] / 2.0 + 0.03),
                (ms["head_w"], ms["head_d"], ms["head_h"]), M["lamp"])
            cnt["mast"] += 1

        # ── ⑦ 원경 창고동 (셔터 벽 너머 상부만 노출) ──
        shd = yd["shed"]
        for j, sd in enumerate(yd["sheds"]):
            z0 = shd["z_bot"]
            RECT(f"{ROOT}/Shed_{j}", sd["x0"], sd["y0"], sd["x1"], sd["y1"],
                 (z0 + sd["z_top"]) / 2.0, sd["z_top"] - z0,
                 M[f"shed{sd['tone']}"])
            p = shd["band_proud"]
            RECT(f"{ROOT}/Shed_{j}_Band", sd["x0"] - p, sd["y0"] - p,
                 sd["x1"] + p, sd["y1"] + p,
                 sd["z_top"] - shd["band_h"] / 2.0 + 0.20, shd["band_h"],
                 M["shed_band"])
            vx = (sd["x0"] + sd["x1"]) / 2.0
            nv = int(shd["vent_n"])
            for i in range(nv):
                vy = sd["y0"] + (sd["y1"] - sd["y0"]) * (i + 1) / (nv + 1)
                RECT(f"{ROOT}/Shed_{j}_V{i}",
                     vx - shd["vent_w"] / 2.0, vy - shd["vent_w"] / 2.0,
                     vx + shd["vent_w"] / 2.0, vy + shd["vent_w"] / 2.0,
                     sd["z_top"] + 0.15 + shd["vent_h"] / 2.0, shd["vent_h"],
                     M["shed_band"])
            cnt["shed"] += 1
        return cnt

    # -------------------------------------------------------------------
    # cue — 베이 둘레 안전 난간 (기본 OFF: 무방호가 이 씬의 위험 본질)
    # -------------------------------------------------------------------
    def build_railing(M):
        by = PARAMS["bay"]
        rr = PARAMS["bay_rail"]
        o = rr["offset"]
        # ㄷ자 난간선: (x1,y0−o) → (x0−o,y0−o) → (x0−o,y1+o) → (x1,y1+o)
        pts = [(by["x1"], by["y0"] - o), (by["x0"] - o, by["y0"] - o),
               (by["x0"] - o, by["y1"] + o), (by["x1"], by["y1"] + o)]
        nid = [0]
        for s in range(len(pts) - 1):
            ax, ay = pts[s]
            bx, by_ = pts[s + 1]
            length = math.hypot(bx - ax, by_ - ay)
            mx, my = (ax + bx) / 2.0, (ay + by_) / 2.0
            along_x = abs(by_ - ay) < 1e-9
            for tag, zc in (("Top", rr["rail_h"]), ("Mid", rr["mid_h"])):
                if along_x:
                    CYL(f"{ROOT}/BayRail_{tag}_{s}", (mx, my, zc),
                        rr["rail_r"], length, M["rail"], rotY=90.0)
                else:
                    CYL(f"{ROOT}/BayRail_{tag}_{s}", (mx, my, zc),
                        rr["rail_r"], length, M["rail"], rotX=90.0)
            npost = max(int(length / rr["spacing"]), 1)
            for i in range(npost + 1):
                t = i / float(npost)
                px, py = ax + (bx - ax) * t, ay + (by_ - ay) * t
                CYL(f"{ROOT}/BayRail_Post_{nid[0]}",
                    (px, py, rr["rail_h"] / 2.0 - 0.05),
                    rr["post_r"], rr["rail_h"] + 0.10, M["rail"])
                nid[0] += 1

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    # 재질 대비 토글: OFF 면 에이프런도 콘크리트(아스팔트/콘크리트 대비 소거)
    apron_mtl = M["asphalt"] if cfg["cue_material_break"] else M["deck"]

    n_stripe, n_bumper = 0, 0
    if cfg["hazard_stairs"]:
        build_apron(M, apron_mtl)
        build_platform(M)
        n_bumper = build_bumpers(M)
        if cfg["cue_nosing"]:
            n_stripe = build_band(M)
        if cfg["cue_railing"]:
            build_railing(M)
        build_parapets(M)
    else:
        build_flat_fill(M)
    yard_cnt = None
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
        yard_cnt = build_yard_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # 기하 자기검증 프린트 (감독 재검산용)
    by, bd, ap = PARAMS["bay"], PARAMS["band"], PARAMS["apron"]
    drop = PARAMS["deck"]["z_top"] - ap["z_top"]
    L = bd["width"] * math.sqrt(2.0) - bd["stripe_w"]
    aabb = (L + bd["stripe_w"]) / math.sqrt(2.0)
    shadow = drop / math.tan(math.radians(PARAMS["light"]["noon_sun_elev"]))
    print(f"[기하] ㄷ자 베이 폭 {by['y1'] - by['y0']:.2f}(y) × "
          f"깊이 {by['x1'] - by['x0']:.2f}(x) m · 낙차 {drop:.2f} m")
    print(f"[도색] 밴드 폭 {bd['width']:.3f} · 황 박판 {L:.3f}×"
          f"{bd['stripe_w']:.3f} @45° → AABB {aabb:.3f} m "
          f"(밴드 내접 오차 {abs(aabb - bd['width']):.2e}) · 박판 {n_stripe}개")
    print(f"[범퍼] {n_bumper}개 · [조명] 연단 그림자 폭 {shadow:.2f} m "
          f"(에이프런 근경 암대)")

    if yard_cnt is not None:
        # 맥락 드레싱 자기검산 — 데크 위 신규 입체의 카메라 간섭 수치 확인
        yd = PARAMS["yard"]
        gy = GRID_GY
        lines = []
        for st in yd["stacks"]:
            # grid d10(eye −10, gy) 기준: 프레임 반폭 0.577·Δx, 가림 도달 y@x=0
            dx = st["cx"] + 10.0
            half = 0.577 * dx
            inframe = abs(st["cy"] - gy) <= half
            y_at_edge = gy + (10.0 / dx) * (st["cy"] - gy) if dx > 1e-6 else 0.0
            lines.append(f"{st['tag']}({st['cx']:+.2f},{st['cy']:+.2f}) "
                         f"d10프레임={'IN' if inframe else 'OUT'} "
                         f"가림도달 y@x=0 {y_at_edge:+.2f}")
        graze_hide = 1.2 * 2.4 / 0.35
        cL, cW = yd["container"]["L"], yd["container"]["W"]
        cmin = min(c["cx"] - (cW if abs(c["yaw"] - 90.0) < 1e-6 else cL) / 2.0
                   for c in yd["containers"])
        print("[드레싱] 팔레트 " + str(yard_cnt["pallet"]) + "매·박스 "
              + str(yard_cnt["carton"]) + " · 통행도색 "
              + str(yard_cnt["lane"]) + "절 · 표지 " + str(yard_cnt["sign"])
              + " · 외등 " + str(yard_cnt["lamp"]) + " · 컨테이너 "
              + str(yard_cnt["container"]) + " · 조명탑 "
              + str(yard_cnt["mast"]) + " · 창고동 " + str(yard_cnt["shed"]))
        for s in lines:
            print(f"[검산] {s}")
        print(f"[검산] edge_graze 에이프런 은닉 한계 x={graze_hide:.2f} m < "
              f"컨테이너 근단 x={cmin:.2f} m → 은닉 특색 불변")

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneD1 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneD1_{ts}.png")
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
