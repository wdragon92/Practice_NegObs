# -*- coding: utf-8 -*-
"""
scene19_fan_winder.py — NegObs 인공씬 19호: T7 부채꼴 코너 계단(winder)
(Isaac Sim 4.5)

사양서 : Docs/multi_scene_brief_v3.md §D scene19_fan_winder (유일 사양)
공통 라이브러리 : scene_common.py (§A) — boot·make_pbr·build_arc_steps·조명·캡처
모티프 참조 : scene05_amphitheater.py (main 골격·아크 단 티어·cue 토글)

유형 정체성: 단코가 방사선 — 직선 소실점 부재.
  건물 모서리를 1/4회전(90°) 감아 도는 12단 부채꼴 계단(r_in1.2/r_out4.0,
  각 단 7.5° 섹터, 낙차 1.8m). 상부 접근 방향(+X)에서 방사형 단코가 소실점
  규칙을 깬다.

[접근성 v2] (2026-07-27, look_refs/scene19 시안 참고): 구버전은 파라펫이 12
  sector 전부를 막고 외호↔보도 쐐기·L벽 옆 포켓이 낙차로 뚫려 있어 보행 진입
  불가였다. 수정: 파라펫 sector 2..9 만 존치(입·출구 개방) + 게이트 기둥,
  코너 슬래브(쐐기 바닥=하부 광장 연장), 상부 문턱 슬리버, 에지 가드 옹벽,
  L벽을 라디얼 에지에 플러시(포켓 봉합). PARAMS["access"] 참조.

[옥상 v3] (2026-07-27, 사용자 지시 "진입로 확폭 + 옥상 장면맥락"):
  ① 진입 확폭 — 입구 sector 0..2 를 카이트 랜딩(동일 상면 −0.15)으로 병합,
    파라펫 sector 3..9 → 입구 개방 호 22.5°(외호 1.53m, 구 1.05m). 잔여 9단이
    riser (1.8−0.15)/9 를 등분해 총낙차 1.8 불변. _step_top 참조.
  ② 옥상 재프레이밍 — 상부 보도(z0)=저층 윙 옥상 테라스, L벽=옥탑 코어,
    하부 보도(−1.95)=아래층 테라스. 지반 −2.31→−6.0(도로 레벨), 보도 슬래브가
    건물 몸체로 연장. 옥상 파라펫(외곽 에지 방호=설비 역추론 단서), 실외기·
    환기구·배관·옥탑 문(설비 단서), 주변 저층 건물 지붕(눈높이 이하 스케일
    앵커, base_z 지원 build_building). PARAMS["roof"]·build_rooftop 참조.

[옥상 v4] (2026-07-27, judge_v6_rt_light8 §scene19 재수정 — 재조준 2컷 2연속 실패):
  실패 원인은 두 컷 모두 **차폐 검산을 좌표로 하지 않은 것**이었다. 그래서
  scene08_sunken_plaza 의 `_obstacle_boxes`/`_solid_at` 시선 검사를 이식·간이화한
  [C] 절(_solid_at·_frame_scan·_geom_report)을 신설하고, NEGOBS_SMOKE=1 이면
  **부팅 전에 전 프리셋을 좌표로 검산**한다(프레임 성긴 레이마칭 → 점유율).
  ① roof_skyline — E동 지붕이 옥상 파라펫(U_N 상단 1.1)에 접선 차폐되던 문제.
    사람 눈높이(2.0 m) 상한을 지키기 위해 카메라를 올리는 대신 **원경 E동을
    북측으로 이동**(구 x−28..−14·y8..22 → x6..20·y16..42, 높이 4.5 불변).
    하부 테라스 파라펫(상단 −0.75) 이 시선에 끼지 않는 정북 방위가 되어
    E동 지붕(−1.5, 캡 −1.0)이 눈높이보다 3.0 m 아래로 열린다.
  ② radial_nosing — 구 eye(5.2,0.7)는 L벽·에지가드 안쪽이라 백색 매스를 피할
    수 없었다. 판정 권고대로 **winder_mid 근방(카이트 랜딩 위)** 으로 옮기고
    tgt 를 뉴얼 하단으로 낮춰 12단 전부를 부감. 백색 매스 점유 0 %.
  ③ (감독 추가 지시) lower_lookup — 구 eye 는 파라펫 링을 정면으로 보는 자리라
    시선축이 0.60 m 앞에서 `Parapet_9` 에 막히고 백색 매스가 54 %였다.
    **하강 마지막 단(sector 10) 위**로 내려서서 팬을 거슬러 올려다보는 자리로
    교체 — 라이저 면 47 %, 백색 0 %. radial_nosing(부감=디딤면)과 짝을 이룬다.
  ④ (감독 추가 지시) roof_context — 옥상 화단을 서측 끝(6.0,−6.8)으로 물리고
    부각을 완만화해 수관 정상이 프레임 안(sy +0.86)에 들어오게 했다.
  ※ 미수정(구조적): winder 회랑 전역이 L벽(top 3.5) 그림자 안이다. 조명 조정은
    이번 지시 범위 밖 — PT 판정은 "회랑 컷은 하늘광만 받는다"를 전제로 볼 것.

실행 / 캡처 / 스모크 : scene05·scene06 와 동일한 env 규약.
    NEGOBS_CAPTURE=1 / NEGOBS_SMOKE=1 / NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG

좌표계: Z-up, m. winder 중심(건물 모서리 newel) (0, 0). 첫 단 방향 +X.
  프리셋 축 = 상부 접근 방향(+X에서 −X로 하강을 내려다봄): grid_views 를 x=6
  기준으로 미러 → 상부 보도에서 winder 를 내려다보는 축 [브리프 §D '프리셋 축'].
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
# [A] SCENE_CONFIG — 7키. hazard_stairs=winder 하강 기하 토글(↔ 평탄 코너).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # 부채꼴 winder (False → z=0 평탄 코너 광장)
    "cue_railing":        True,    # 외측 파라펫 상단 핸드레일(공공 코너 계단 관례)
    "cue_tactile":        False,   # True → 상부 접근 경고 점자띠
    "cue_material_break": True,    # 상부 보도(plaza_light) vs 하부 보도(plaza_lower)
    "cue_nosing":         False,   # True → 방사형 단코 논슬립 아크 밴드
    "cue_sign":           False,   # [예약]
    "cue_scene_dressing": True,    # 화단·건물·잔디
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    center=dict(cx=0.0, cy=0.0),
    # 부채꼴 12단: 단 i=build_arc_steps(r_in1.2/r_out4.0, i*7.5°..+7.5°, seg3,
    #   top_z=−0.15*(i+1), base −2.3) → 총 90° 회전, 낙차 1.8
    # [옥상 v3] kite_n: 입구 sector 0..kite_n-1 을 단일 카이트 랜딩(top −riser)으로
    #   병합. 잔여 (n−kite_n) 단이 (n·riser − riser) 낙차를 등분 → 총낙차 불변 1.8.
    winder=dict(r_in=1.2, r_out=4.0, n=12, sector_deg=7.5, a0=0.0,
                riser=0.15, base_z=-2.3, seg=3, kite_n=3),
    # 내측 코너 newel: Cylinder r1.1 (z −2.3..0.5)
    newel=dict(r=1.1, z_bot=-2.3, z_top=0.5),
    # 건물 모서리 L벽: winder 라디얼 에지(y=0 / x=0)와 플러시 — 측면 낙차 포켓 봉합
    #   [접근성 v2] south x1 1→4·y1 −0.2→0, west x1 −0.2→0·y1 1→4
    walls=dict(z_bot=-6.0, z_top=3.5,   # [옥상 v3] 지반 −6.0까지 연장(옥탑 코어 몸체)
               south=dict(x0=-8.0, x1=4.0, y0=-1.0, y1=0.0),
               west=dict(x0=-1.0, x1=0.0, y0=-8.0, y1=4.0)),
    # 외측 낮은 파라펫: 단별 호 링(r 3.82..4.05), 각 단 상면 +1.0 (호 링)
    parapet=dict(r_in=3.82, r_out=4.05, h=1.0),
    # [접근성 v2] 입·출구 개방 (look_refs 시안 반영): 파라펫은 sector 2..9 만.
    #   corner   = 코너 슬래브(외호↔보도 직선 에지 쐐기 바닥, 하부 광장 연장 −1.95)
    #   threshold= 상부 문턱 슬리버(보도 x=4 ↔ 입구 sector 외호 틈 최대 0.14, z0)
    #   guard    = 상부 보도 에지 옹벽(쐐기 위 1.95 낙차 방호, 상단 +1.0)
    # [옥상 v3] 입구 확폭: 개방 sector 0..2(카이트 랜딩) → 파라펫 3..9.
    #   threshold x0 3.86→3.70(외호가 22.5°에서 x=3.70 까지 물러남 — 슬리버 틈 방지,
    #   내측 밴드는 카이트 상면 −0.15 위 z0 플레이트로 물림 = 유효 답면 x≤3.70),
    #   y1 1.05→1.53(=4·sin22.5°). guard 도 x0 3.7·y0 1.53 연동(정션 슬롯 봉합).
    access=dict(parapet_first=3, parapet_last=9,
                corner=dict(x0=-1.0, y0=-1.0, x1=4.0, y1=4.0),
                threshold=dict(x0=3.70, y0=0.0, y1=1.53),
                guard=dict(x0=3.7, x1=4.0, y0=1.53, y1=4.0, h_top=1.0),
                post_r=0.05, post_h=1.15),
    # 상·하부 보도 (재질 경계 cue) — 솔리드 슬래브(지반 −2.31 까지)
    upper=dict(x0=4.0, x1=17.0, y0=-9.0, y1=4.0, top_z=0.0),
    lower=dict(x0=-9.0, x1=4.0, y0=4.0, y1=17.0, top_z=-1.95),
    # 지반(잔디) 바닥 — [옥상 v3] 도로 레벨 −6.0 (상부 보도 z0 = 지상 6m 옥상)
    ground=dict(x0=-60.0, x1=60.0, y0=-60.0, y1=60.0, top_z=-6.0),

    # ═══ [W2-D ground_kit] P6 roof_membrane — 사양 §5.6 scene19 행 ══════════
    #  19-1 우레탄 도막방수(녹색) + 롤 이음 pitch 0.9~1.1 m, 알베도 **0.16~0.22**
    #       (감독 결재 M2; 특수조 0.10~0.16 과 C4 소품조 0.20~0.35 의 교집합이
    #        공집합이라 사양이 노후 도막 중간대로 판정) — 키트 원장 기본값 0.19.
    #  19-2 파라펫 치켜올림 + 두겁  -> build_rooftop (위 `roof.turnup_h/coping_w`)
    #  19-3 루프 드레인 2개소 (10.5, -0.6) [F 전 컷] · (6.0, -7.5)
    #  19-4 도막 보수 덧칠 패치 4매 · 드레인 방사 물때 · 파라펫 하부 흘림
    #  --   **줄눈 격자 금지** — P6 has `joint=None`, so the kit cannot emit one.
    #  ★ Tactile **OFF** (§12.4): private rooftop, not a facility covered by the
    #    accessibility act. The scene keeps a `cue_tactile` path for ablation
    #    only; nothing is installed by default.
    #  ★ Frame origin: `build_views` mirrors `grid_views` about xref 5.8, so the
    #    preset grid origin is world x = 2*5.8 = **11.6** and the progression is
    #    **-X**. `plan_ground(origin=...)` wants that grid origin (the frame
    #    model puts the eye at s = -d), **not** the drop edge. The drop edge is
    #    the roof deck's west lip `upper.x0` = 4.0, i.e. s = 11.6 - 4.0 = **7.6**.
    #    dists are (2, 3.5, 5) to match `build_views` (d10 would be off-roof).
    gkit=dict(
        grid_origin_x=11.6,                    # = 2 * xref(5.8), build_views
        region_inset=0.25,                     # = roof.pp_t (inside parapets)
        drains=[(10.50, -0.60), (6.00, -7.50)],
        patches=[(12.30, -0.60), (14.30, -0.25), (9.20, -3.40), (6.80, 1.90)],
        seam_pitch=1.00,
        wear_n=5,
    ),
    # 지평 폐쇄 건물 (base_z=지반) — C 고층 + [옥상 v3] D/E 저층(지붕이 눈높이
    #   이하 −2.5/−1.5 = 옥상 스케일 앵커)
    # [옥상 v4] E 재배치: 구 x−28..−14·y8..22(북서)는 시선이 **하부 테라스
    #   파라펫 L_W/L_N(상단 −0.75)** 을 스쳐 지붕(캡 상단 −1.0)이 그 실루엣
    #   아래로 잠겼다(2라운드 연속 미시인). 정북 대지(x6..20·y16..42)로 옮기면
    #   상부 옥상(x4..17·y−9..4)·하부 테라스(x−9..4·y4..17) 어느 쪽 파라펫과도
    #   교차하지 않는 시선이 열린다. 높이 4.5(지붕 −1.5) 불변 → 눈높이 2.0 대비
    #   3.0 m 아래 = 스케일 앵커 유지. 파사드를 남면(우리 쪽)으로 돌림.
    #   *위험 기하(winder·파라펫)는 불변, 원경 건물만 이동.*
    buildings=dict(
        C=dict(x0=44.0, x1=54.0, y0=-16.0, y1=16.0, h=15.0, floors=5,
               axis="x", facade_x=44.0, face_dir=-1.0, base_z=-6.0),
        D=dict(x0=-30.0, x1=-16.0, y0=-20.0, y1=-6.0, h=3.5, floors=1,
               axis="x", facade_x=-16.0, face_dir=1.0, base_z=-6.0),
        E=dict(x0=6.0, x1=20.0, y0=16.0, y1=42.0, h=4.5, floors=1,
               axis="y", facade_y=16.0, face_dir=-1.0, base_z=-6.0),
    ),
    # [옥상 v3] 옥상 파라펫(외곽 방호)·설비 소품·옥탑 문 — build_rooftop
    roof=dict(pp_t=0.25, pp_h=1.2, pp_h_inner=1.1,
              # [W2-D §5.6 19-2] 치켜올림 0.30 m · 두겁 0.45~0.55 의 중앙 0.50
              turnup_h=0.30, coping_w=0.50,
              hvac=[dict(cx=13.0, cy=-7.0), dict(cx=14.4, cy=-7.0)],
              hvac_size=(0.9, 0.35, 0.8),
              vent=dict(cx=8.0, cy=-5.5, r=0.15, h=0.8),
              pipe=dict(x0=5.0, x1=16.0, y=-8.55, r=0.06),
              door=dict(w=0.9, h=2.1),   # 위치=L벽 south 동단면(x=4) 중앙
              # [옥상 v4] 옥상 화단 위치를 PARAMS 로 승격(조립·차폐 검산 단일
              #   출처). 구 (11,−6)은 roof_context eye 에서 5.9 m 앞이라 수관
              #   정상이 프레임 상단 밖 sy=1.95 로 잘렸다(v6 판정 추가관측①).
              #   서측 끝으로 물려 시거리 10.8 m 확보 → sy 0.83 로 프레임 안.
              #   배관(y −8.61..−8.49)과 0.19 m, U_W 파라펫(x4.25)과 0.25 m 이격.
              #   canopy_*: scene_common.build_tree 가 좌표해시 RNG 로 만드는
              #   수형의 실측 상한(줄기 2.42 + 수관) — 차폐 AABB·프레임 검산용.
              planter=dict(cx=6.0, cy=-6.8, size=3.0,
                           canopy_top=3.90, canopy_r=1.35)),

    material=dict(
        scale=dict(plaza_light=1.80, plaza_lower=0.8, granite_dark=1.0,
                   concrete_wall=2.0, brick_red=2.0, grass=1.4),
        lower_warm_tint=(1.06, 1.0, 0.94),
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # [W2-D · 사양 §5.6 19-2] The near-white parapet constant is retired.
        #   scene19 is the #1 near-white offender of the whole set and this
        #   single constant is bound to every parapet, guard and gate post in
        #   the scene. Weathered concrete coping measures 0.35~0.45; 0.40 is
        #   the middle and is unambiguously not near-white.
        parapet_color=(0.40, 0.40, 0.385), parapet_rough=0.66,
        # 19-2 코팅 치켜올림: 파라펫 내면 하부 0.30 m 를 바닥 도막과 동색으로.
        #   값은 감독 결재 M2 대역 0.16~0.22 의 중앙 (= ground_kit
        #   GROUND_DIMENSIONS["membrane_albedo"] 0.19) 을 녹색으로 준 것.
        coating_color=(0.115, 0.150, 0.120), coating_rough=0.72,
        nosing_color=(0.85, 0.72, 0.10), nosing_rough=0.7,
        hvac_color=(0.60, 0.61, 0.62), hvac_rough=0.5,      # [옥상 v3] 실외기
        # r5 판정: 암색 문이 암색 화강암벽에 매몰 → 도장 강판 회청색으로 대비 확보
        door_color=(0.28, 0.30, 0.33), door_rough=0.6,      # [옥상 v3] 옥탑 철문
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


_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene19")


# ===========================================================================
# [C] 기하 자기검증 — 점 포함(_solid_at) + 시선 레이마칭
#   [v6 판정 §scene19] 재조준 2컷이 **2라운드 연속 차폐**로 실패했다. 원인은
#   차폐를 눈으로만 가정한 것. scene08_sunken_plaza 의 `_obstacle_boxes`/
#   `_solid_at` 시선 검사를 이식·간이화해 렌더 전에 좌표로 검산한다.
#   좌표의 단일 출처는 PARAMS — 조립부와 같은 값을 읽는다(정의 이중화 금지).
#   근사: winder 단·파라펫 호는 build_arc_steps 의 세그 박스 대신 **환형 섹터**
#   로 판정(세그 현 1.03배 여유만큼 실제보다 약간 작다 = 보수적 판정 아님이
#   아니라 '차폐 과소평가' 쪽이므로, 통과 판정에는 여유 마진을 둔다).
# ===========================================================================
def _step_top(i):
    """[옥상 v3] sector 0..kite_n-1 = 카이트 랜딩(동일 상면 −riser).
    잔여 (n−kite_n)단이 (총낙차−riser)를 등분 → 총낙차 n·riser 불변."""
    w = PARAMS["winder"]
    kn = int(w.get("kite_n", 0))
    if kn <= 0 or i < kn:
        if kn <= 0:
            return -w["riser"] * (i + 1)
        return -w["riser"]
    rem = (w["riser"] * w["n"] - w["riser"]) / (w["n"] - kn)
    return -w["riser"] - rem * (i - kn + 1)


_BOXES_CACHE = [None]


def _solid_boxes():
    """장애물 AABB 목록 (name, x0,x1, y0,y1, z0,z1) — 조립부와 동일 좌표.
    호(winder 단·파라펫)·원기둥(newel)은 _solid_at 에서 극좌표로 별도 판정."""
    if _BOXES_CACHE[0] is not None:
        return _BOXES_CACHE[0]
    up, lo, gr = PARAMS["upper"], PARAMS["lower"], PARAMS["ground"]
    ac, wl, rf = PARAMS["access"], PARAMS["walls"], PARAMS["roof"]
    base = gr["top_z"]
    t, h, hi = rf["pp_t"], rf["pp_h"], rf["pp_h_inner"]
    th, gd, co = ac["threshold"], ac["guard"], ac["corner"]
    B = [
        ("Ground", gr["x0"], gr["x1"], gr["y0"], gr["y1"], base - 1.0, base),
        ("Walk_upper", up["x0"], up["x1"], up["y0"], up["y1"], base,
         up["top_z"]),
        ("Walk_lower", lo["x0"], lo["x1"], lo["y0"], lo["y1"], base,
         lo["top_z"]),
        ("CornerSlab", co["x0"], co["x1"], co["y0"], co["y1"], base,
         lo["top_z"]),
        ("Threshold", th["x0"], up["x0"], th["y0"], th["y1"], lo["top_z"],
         up["top_z"]),
        ("EdgeGuard", gd["x0"], gd["x1"], gd["y0"], gd["y1"], lo["top_z"],
         gd["h_top"]),
    ]
    for tag in ("south", "west"):
        b = wl[tag]
        B.append((f"Wall_{tag}", b["x0"], b["x1"], b["y0"], b["y1"],
                  wl["z_bot"], wl["z_top"]))
    # 옥상 파라펫 7변 (build_rooftop 의 pp() 와 동일 z: base−0.05 .. base+hh)
    for tag, x0, x1, y0, y1, bz, hh in (
            ("U_E", up["x1"] - t, up["x1"], up["y0"], up["y1"], up["top_z"], h),
            ("U_S", up["x0"], up["x1"] - t, up["y0"], up["y0"] + t,
             up["top_z"], h),
            ("U_W", up["x0"], up["x0"] + t, up["y0"] + t, -1.0, up["top_z"], h),
            ("U_N", up["x0"], up["x1"], up["y1"] - t, up["y1"], up["top_z"],
             hi),
            ("L_W", lo["x0"], lo["x0"] + t, lo["y0"], lo["y1"], lo["top_z"], h),
            ("L_N", lo["x0"] + t, lo["x1"], lo["y1"] - t, lo["y1"],
             lo["top_z"], h),
            ("L_E", lo["x1"] - t, lo["x1"], lo["y0"], lo["y1"] - t,
             lo["top_z"], h)):
        B.append((f"RoofPP_{tag}", x0, x1, y0, y1, bz - 0.05, bz + hh))
    # 설비·옥탑 문·화단(수관 포함 근사)
    hs = rf["hvac_size"]
    for i, u in enumerate(rf["hvac"]):
        B.append((f"Hvac_{i}", u["cx"] - hs[0] / 2 - 0.05,
                  u["cx"] + hs[0] / 2 + 0.05, u["cy"] - hs[1] / 2 - 0.05,
                  u["cy"] + hs[1] / 2 + 0.05, up["top_z"],
                  up["top_z"] + 0.1 + hs[2]))
    v = rf["vent"]
    B.append(("Vent", v["cx"] - v["r"], v["cx"] + v["r"] * 2.2,
              v["cy"] - v["r"], v["cy"] + v["r"], up["top_z"],
              up["top_z"] + v["h"] + v["r"]))
    p = rf["pipe"]
    B.append(("PipeRun", p["x0"], p["x1"], p["y"] - p["r"], p["y"] + p["r"],
              up["top_z"] + 0.02, up["top_z"] + 0.02 + 2 * p["r"]))
    d, ws = rf["door"], wl["south"]
    B.append(("CoreDoor", ws["x1"], ws["x1"] + 0.04,
              (ws["y0"] + ws["y1"]) / 2 - d["w"] / 2,
              (ws["y0"] + ws["y1"]) / 2 + d["w"] / 2, up["top_z"],
              up["top_z"] + d["h"]))
    pl = rf["planter"]
    ph = max(pl["size"] / 2.0, pl["canopy_r"])                  # 수관 포함
    B.append(("Planter_A", pl["cx"] - ph, pl["cx"] + ph, pl["cy"] - ph,
              pl["cy"] + ph, 0.0, pl["canopy_top"]))
    for k, bd in PARAMS["buildings"].items():
        bz = float(bd.get("base_z", 0.0))
        B.append((f"Bldg{k}", bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                  bz - 1.0, bz + bd["h"]))
        B.append((f"Bldg{k}_roof", bd["x0"] - 0.1, bd["x1"] + 0.1,
                  bd["y0"] - 0.1, bd["y1"] + 0.1, bz + bd["h"],
                  bz + bd["h"] + 0.5))
    _BOXES_CACHE[0] = B
    return B


def _solid_at(x, y, z):
    """점 (x,y,z)를 품는 솔리드 이름(없으면 None).
    카메라 eye 매몰 + 시선 차단(ray march) 검사의 단일 출처."""
    for nm, x0, x1, y0, y1, z0, z1 in _solid_boxes():
        if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
            return nm
    cx, cy = PARAMS["center"]["cx"], PARAMS["center"]["cy"]
    w, ac, pp = PARAMS["winder"], PARAMS["access"], PARAMS["parapet"]
    nw = PARAMS["newel"]
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy)
    if r <= nw["r"] and nw["z_bot"] <= z <= nw["z_top"]:
        return "Newel"
    a = math.degrees(math.atan2(dy, dx)) % 360.0
    span = w["n"] * w["sector_deg"]
    if w["a0"] <= a <= w["a0"] + span:
        i = min(int((a - w["a0"]) / w["sector_deg"]), w["n"] - 1)
        top = _step_top(i)
        if w["r_in"] <= r <= w["r_out"] and w["base_z"] <= z <= top:
            return f"Step_{i}"
        # 파라펫 호 링 + 상단 핸드레일(+0.06) 을 한 밴드로
        if ac["parapet_first"] <= i <= ac["parapet_last"] \
                and pp["r_in"] <= r <= pp["r_out"] \
                and top - 0.1 <= z <= top + pp["h"] + 0.06:
            return f"Parapet_{i}"
    return None


def _ray_hit(eye, dirv, step=0.1, tmax=80.0):
    """eye 에서 dirv(단위) 로 step 간격 행진 — (거리, 솔리드명|None)."""
    for k in range(1, int(tmax / step) + 1):
        t = k * step
        s = _solid_at(eye[0] + dirv[0] * t, eye[1] + dirv[1] * t,
                      eye[2] + dirv[2] * t)
        if s is not None:
            return t, s
    return tmax, None


def _cam_basis(eye, tgt, hfov=60.0, aspect=16.0 / 9.0):
    """(eye, forward, right, up, tan(hfov/2), tan(vfov/2)) — 1920×1080 = 60°."""
    e = np.array(eye, dtype=float)
    f = np.array(tgt, dtype=float) - e
    f /= np.linalg.norm(f)
    rt = np.cross(f, np.array([0.0, 0.0, 1.0]))
    rt /= np.linalg.norm(rt)
    th = math.tan(math.radians(hfov / 2.0))
    return e, f, rt, np.cross(rt, f), th, th / aspect


def _screen_uv(eye, tgt, p):
    """월드 점 p 의 화면 정규좌표 (sx, sy, 프레임 안 여부). |s|≤1 = 프레임 안."""
    e, f, rt, uu, th, tv = _cam_basis(eye, tgt)
    v = np.array(p, dtype=float) - e
    d = float(v @ f)
    if d <= 1e-6:
        return None, None, False
    sx, sy = float(v @ rt) / d / th, float(v @ uu) / d / tv
    return sx, sy, (abs(sx) <= 1.0 and abs(sy) <= 1.0)


def _frame_scan(eye, tgt, nx=21, ny=12, step=0.12, tmax=80.0, face=False):
    """뷰포트(1920×1080 = 수평화각 60°)를 nx×ny 광선으로 성기게 스캔.
    반환: {솔리드명: 화면 점유율 %} — 무접촉은 '<SKY>'.
    face=True 면 winder 단을 `Step_i:tread` / `Step_i:riser` 로 분리(적중점 z가
    그 단 상면과 같으면 디딤면, 아니면 라이저 면) — 상행 시선 컷 판독용.
    *v6 판정 '차폐 검산 실패는 재발한다'에 대한 규약: 재조준 후 반드시 이 함수로
     파라펫 전 부재를 포함한 광선 투사를 돌린다.*"""
    e, f, rt, uu, th, tv = _cam_basis(eye, tgt)
    cnt = {}
    for iy in range(ny):
        sy = (1.0 - (iy + 0.5) * 2.0 / ny) * tv
        for ix in range(nx):
            sx = ((ix + 0.5) * 2.0 / nx - 1.0) * th
            d = f + sx * rt + sy * uu
            d /= np.linalg.norm(d)
            t, s = _ray_hit(e, d, step, tmax)
            k = s if s is not None else "<SKY>"
            if face and k.startswith("Step_"):
                zh = e[2] + d[2] * t
                k += ":tread" if abs(zh - _step_top(int(k.split("_")[1]))) \
                    <= step else ":riser"
            cnt[k] = cnt.get(k, 0) + 1
    tot = float(nx * ny)
    return {k: 100.0 * v / tot for k, v in cnt.items()}


def _pct(scan, *prefixes):
    return sum(v for k, v in scan.items() if k.startswith(prefixes))


def _geom_report():
    """부팅 전 기하·카메라 자기검증 (NEGOBS_SMOKE=1)."""
    views = build_views()
    up = PARAMS["upper"]
    bE = PARAMS["buildings"]["E"]
    e_roof = bE["base_z"] + bE["h"]
    print("=" * 70)
    print("scene19_fan_winder — SMOKE 기하 자기검증 (부팅 전)")
    print("=" * 70)
    print(f"  총낙차 {abs(_step_top(PARAMS['winder']['n'] - 1)):.2f} m "
          f"(카이트 {PARAMS['winder']['kite_n']}섹터 + 잔여 "
          f"{PARAMS['winder']['n'] - PARAMS['winder']['kite_n']}단) — 불변 검사")
    print(f"  E동 지붕 z {e_roof:+.2f} (캡 {e_roof + 0.5:+.2f}) vs 옥상 눈높이 "
          f"{up['top_z'] + 2.0:+.2f} → "
          f"{'OK (눈높이 이하)' if e_roof + 0.5 < up['top_z'] + 2.0 else 'FAIL'}")

    hits = [(n, _solid_at(*v["eye"])) for n, v in sorted(views.items())]
    hits = [(n, s) for n, s in hits if s is not None]
    for n, s in hits:
        print(f"    [FAIL] {n} eye 가 {s} 내부(매몰)")
    print(f"  [eye 매몰] {len(hits)}건 → {'OK' if not hits else 'FAIL'}")

    print("  [프레임 레이마칭] 21×12 광선 · 60° 수평화각")
    v = views["roof_skyline"]
    sc_sky = _frame_scan(v["eye"], v["tgt"])
    pe = _pct(sc_sky, "BldgE")
    print(f"    roof_skyline  eye{tuple(v['eye'])} → tgt{tuple(v['tgt'])}")
    for k in sorted(sc_sky, key=lambda k: -sc_sky[k])[:6]:
        print(f"      {k:16s} {sc_sky[k]:5.1f}%")
    print(f"      E동 점유 {pe:.1f}% (≥8 = 스케일 앵커 성립) → "
          f"{'OK' if pe >= 8.0 else 'FAIL'}")

    def _stair_cut(name, min_step, min_tier, max_white):
        v = views[name]
        sc_ = _frame_scan(v["eye"], v["tgt"], tmax=20.0, step=0.03, face=True)
        steps_ = _pct(sc_, "Step_")
        riser = sum(val for k, val in sc_.items() if k.endswith(":riser"))
        tiers = sorted({int(k.split("_")[1].split(":")[0])
                        for k, val in sc_.items()
                        if k.startswith("Step_") and val >= 0.4})
        white_ = _pct(sc_, "Parapet_", "RoofPP", "EdgeGuard", "Threshold")
        print(f"    {name:13s} eye{tuple(v['eye'])} → tgt{tuple(v['tgt'])}")
        print(f"      단 점유 {steps_:.1f}%(라이저 {riser:.1f} / 디딤 "
              f"{steps_ - riser:.1f}) · 시인 단 {len(tiers)}/"
              f"{PARAMS['winder']['n']} {tiers} · 뉴얼 "
              f"{sc_.get('Newel', 0.0):.1f}% · 백색 매스 {white_:.1f}%")
        ok = (steps_ >= min_step and len(tiers) >= min_tier
              and white_ <= max_white)
        print(f"      → {'OK' if ok else 'FAIL'} (기준 단≥{min_step:.0f}% · "
              f"시인≥{min_tier}단 · 백색≤{max_white:.0f}%)")

    # radial_nosing = 하강 부감(디딤면 위주) / lower_lookup = 상행 앙각(라이저)
    _stair_cut("radial_nosing", 60.0, 8, 5.0)
    _stair_cut("lower_lookup", 60.0, 6, 5.0)

    v = views["roof_context"]
    rf = PARAMS["roof"]
    pl, hv = rf["planter"], rf["hvac"]
    probes = [("수관 정상", (pl["cx"], pl["cy"], pl["canopy_top"]))]
    for i, u in enumerate(hv):
        probes.append((f"실외기{i}", (u["cx"], u["cy"], 0.5 + 0.4 * i)))
    probes += [("환기구", (rf["vent"]["cx"], rf["vent"]["cy"], 0.8)),
               ("배관", (10.0, rf["pipe"]["y"], 0.14)),
               ("남 파라펫 상단", (10.0, PARAMS["upper"]["y0"] + 0.12,
                                   rf["pp_h"]))]
    print(f"    roof_context  eye{tuple(v['eye'])} → tgt{tuple(v['tgt'])}")
    bad = []
    for nm, p in probes:
        sx, sy, ok = _screen_uv(v["eye"], v["tgt"], p)
        print(f"      {nm:14s} sx {sx:+.2f} sy {sy:+.2f} → "
              f"{'프레임 안' if ok else '프레임 밖'}")
        if not ok:
            bad.append(nm)
    print(f"      → {'OK' if not bad else 'FAIL ' + str(bad)} "
          f"(수관 잘림 0 · 설비 클러스터 전원 프레임 안)")

    print("  [미장센 시선축 첫 접촉]")
    for n in ("upper_approach", "winder_mid", "lower_lookup", "entry_gate",
              "roof_context", "radial_nosing", "roof_skyline"):
        v = views[n]
        e = np.array(v["eye"], float)
        d = np.array(v["tgt"], float) - e
        L = float(np.linalg.norm(d))
        t, s = _ray_hit(e, d / L, 0.05, L * 3.0)
        print(f"    {n:16s} t={t:5.2f} ({L:5.2f} 까지 tgt) → "
              f"{s if s else '무접촉(지평/하늘)'}")
    print("=" * 70)


# ===========================================================================
# [D] 카메라 프리셋 — grid_views 를 x=6 미러(상부 접근축) + 미장센 4컷
# ===========================================================================
def build_views():
    """프리셋 축 = 상부 접근 방향. grid_views(+X 응시)를 x=6 기준 미러하여
    상부 보도(+X, z=0)에서 winder 하강을 −X 방향으로 내려다보는 축으로 전환."""
    # [옥상 v3] xref 6.0→5.8: 미러 후 d5 eye x=17.0 이 동측 옥상 파라펫(16.75~17,
    #   h1.2) 내부에 들어가 h0.3/0.9_d5 프레임 전면 암흑 → 16.6 으로 안쪽 이동.
    #   d10(21.6)은 옥상 밖 호버 컷 = "옥상을 밖에서 본" 맥락 컷으로 유지.
    xref = 5.8
    # [v5 판정 반영] d10(미러 후 x21.6)은 옥상 밖 허공 — 보행자가 설 수 없는
    #   시점이라 그리드 1/3이 무효였다. 옥상 위 물리 가능 거리 (2, 3.5, 5)로 교체.
    v = sc.grid_views(0.0, dists=(2, 3.5, 5))
    out = {}
    for k, val in v.items():
        e, t = list(val["eye"]), list(val["tgt"])
        e[0] = 2.0 * xref - e[0]                # 미러 → 카메라 +X측, −X 응시
        t[0] = 2.0 * xref - t[0]
        out[k] = dict(eye=e, tgt=t)
    out["upper_approach"] = dict(eye=[9.0, -1.0, 1.0], tgt=[1.0, 2.0, -1.2])
    # [v5 판정 반영] winder_mid·lower_lookup 구도는 파라펫 외측이라 부채꼴 단이
    #   전부 가려졌다(15컷 중 단 시인 0). 계단 회랑 **내부** 시점으로 재조준:
    #   보행선 r≈2.6, 입구(각 11°)→출구(각 79°).
    #   winder_mid: 카이트 랜딩 위(입구 어깨)에서 팬 하강을 내려다봄
    out["winder_mid"]     = dict(eye=[3.4, 0.9, 1.3],  tgt=[1.1, 2.4, -1.3])
    # [옥상 v4 / v6 판정 추가관측] lower_lookup 재조준. 구 eye(0.9,4.4,−0.35)는
    #   하부 보도에 서서 파라펫 링을 **정면으로** 보는 자리였다 — 시선축이
    #   0.60 m 앞에서 `Parapet_9` 에 차단되고 백색 파라펫이 프레임 54.1 %
    #   (v6 판정 "좌 절반→55 %" 와 일치). 애초에 "코너 슬래브"는 각 45° 부근
    #   에만 폭이 있고 그 구간이 곧 파라펫 존치 구간(22.5~75°)이라 구조적으로
    #   불가능한 자리였다. → **하강 마지막 단(sector 10) 위**로 내려서서 팬을
    #   거슬러 올려다보는 자리로 교체(파라펫 링은 시선 뒤로 빠진다).
    #   eye 극좌표 r 3.40 / 각 80.0°(sector 10, 상면 −1.617) 위 안구고 1.60 m.
    #   [_frame_scan 검산] 단 88.8 %(**라이저 41.8 / 디딤 47.0** — 상행 시선이라
    #   라이저 면이 교대로 드러난다) · 시인 단 8(sector 2~9) · 백색 매스 0.0 % ·
    #   뉴얼 11.2 %(방사 수렴 기준) · 암색 L벽 0.1 %.
    out["lower_lookup"]   = dict(eye=[0.59, 3.35, -0.02], tgt=[1.55, 1.55, -0.9])
    # [옥상 v4 / v6 판정②] 구 eye(5.2,0.7,1.5)는 L벽·에지가드 안쪽이라 어떤
    #   tgt 로도 백색 매스를 피할 수 없었다(부채꼴 단 0단). 판정 권고대로
    #   **성공한 winder_mid 근방 = 카이트 랜딩 위**로 옮기고 tgt 를 뉴얼 하단
    #   으로 낮춘다. eye 는 카이트 상면(−0.15) 위 안구고 1.60 m, 극좌표
    #   r 3.15 / 각 17.6°(sector 2 = 카이트) → tgt r 1.73 / 각 56.8°(sector 7),
    #   부각 57°. [_frame_scan 검산] 단 84.9 % · 12/12 단 전부 시인(단별
    #   1.8~13.4 %) · 뉴얼 5.7 %(방사 수렴 기준점) · 파라펫/레일/가드/문턱/
    #   게이트기둥 0.0 % · 암색 L벽 8.3 %(winder_mid 22.5 % 대비 1/3).
    out["radial_nosing"]  = dict(eye=[3.0, 0.95, 1.45], tgt=[0.95, 1.45, -1.85])
    out["entry_gate"]     = dict(eye=[6.5, 0.5, 1.2], tgt=[1.8, 1.8, -1.2])  # 접근성 v2 진입 동선
    # [옥상 v3] roof_context: 설비 클러스터(실외기·환기구·배관)+파라펫 수평 컷
    # [옥상 v4 / v6 판정 추가관측①] 수관 잘림 해소. 구 tgt z 0.2(부각 10.7°)에
    #   구 화단 (11,−6)(시거리 5.9 m) 조합은 수관 정상이 sy=1.95 = 프레임 상단
    #   밖 2배 지점. 화단을 서측 끝(6.0,−6.8)으로 물려 시거리 10.8 m 로 늘리고
    #   부각을 4.4°로 완만화(tgt z 0.2→1.15, eye z 1.8→1.9 = 사람 눈높이 유지).
    #   [검산 sy(=화면 세로 정규좌표, |sy|≤1 이 프레임 안)]
    #   수관 정상 +0.86 · 실외기0 −0.67 · 실외기1 −0.67 · 환기구 −0.14 ·
    #   배관 −0.41 · 남측 파라펫 상단 ±0.00 → **전부 프레임 안**
    #   (수관은 roof.planter.canopy_top 3.90 = 실측 3.81 의 보수 상한 기준).
    #   [_frame_scan] 하늘 30.1 / 옥상 데크 20.9 / 화단·수목 19.0(구 44.2 →
    #   과점유도 완화) / 남·서 파라펫 13.9 / 실외기 11.0 / 환기구 0.5 %.
    out["roof_context"]   = dict(eye=[16.6, -4.2, 1.9], tgt=[9.0, -8.0, 1.15])
    # [옥상 v4 / v6 판정①] roof_skyline 3차 재조준. v5·v6 의 북서 방위는 눈으로
    #   만 검산해 두 번 다 실패했다 — 실제 차폐 주체는 winder 호 링이 아니라
    #   ⓐ 코앞의 U_N 옥상 파라펫(top 1.1)과 ⓑ 하부 테라스 파라펫 L_W/L_N
    #   (top −0.75)이었고, E동 캡(−1.0)이 ⓑ 실루엣 아래로 잠겨 지붕이 2 %만
    #   노출됐다(_frame_scan 으로 v6 프레임 재현·확인).
    #   해법: 눈높이는 사람 기준 2.0 m 를 지키고 **E동을 정북으로 이동**(PARAMS
    #   buildings 참조) — 상부 옥상 북연(y3.75)에서 정북을 보면 하부 테라스
    #   (x≤4)와 그 파라펫이 시선에 전혀 걸리지 않는다.
    #   [검산] eye(10.0,2.0,2.0): U_N 안쪽 면까지 1.76 m → 시선 하강 한계
    #   atan(0.9/1.76)=27.1°. E동 근단(y16, 캡 −1.0) 부각 12.0° · 원단(y42)
    #   4.3° → 지붕면 밴드 7.7°(수직화각 36°의 21 %)가 한계 안쪽(여유 15.1°).
    #   L_N(y16.75..17, x≤4)은 시선이 y17 에서 x11.7 → 미교차.
    #   [_frame_scan] 하늘 44.6 % · E동 38.9 %(지붕 상면 12.3 %) · 지반(6 m
    #   아래 골목) 7.7 % · U_N 파라펫 전경 6.7 % · 암색 벽 0 %.
    out["roof_skyline"]   = dict(eye=[10.0, 2.0, 2.0], tgt=[13.0, 29.0, -2.0])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. upper_approach — 상부 보도에서 방사형 단코, 직선 소실점 부재
 2. h0.3·d5~10     — 코너 winder 낙차(1.8m) 인지
 3. winder_mid     — 1/4회전 하강의 부채꼴 단 형태
 4. radial_nosing  — 방사선 단코가 세그(3) 각짐 없이 읽히는가(하강 부감=디딤면)
 4b. lower_lookup  — [옥상 v4] 마지막 단에서 팬을 거슬러 올려다본 **라이저 면**
                     (4번과 짝: 부감=디딤 84 % / 앙각=라이저 47 %)
 5. cue            — 상/하부 보도 재질경계 / 외측 파라펫·핸드레일
 6. entry_gate     — [접근성 v2] 문턱→카이트 랜딩 연속(입구 폭 1.53)·게이트
                     기둥·에지 가드, 하부는 출구 sector→코너 슬래브→하부 보도 연속
 7. roof_context   — [옥상 v3] 실외기·환기구·배관·옥상 파라펫 + 옥상 화단·수목
                     [옥상 v4] 수관 정상이 프레임 안에 온전히 들어오는가
                     (스케일 앵커 역할은 8번 roof_skyline 이 전담 — 이 컷의
                      시선은 U_W 파라펫(상단 1.2)에 막혀 원경 D동이 안 보인다)
 8. roof_skyline   — [옥상 v4] 북측 파라펫 너머 E동 지붕이 **눈높이 아래**로
                     열리는가(스케일 앵커) + 6 m 아래 지반이 함께 읽히는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"

    if smoke_mode:
        # [옥상 v4] 부팅 전 좌표 검산 — 차폐 실패 재발 방지 규약(v6 판정 §교훈).
        _geom_report()

    sc.check_assets(
        ["plaza_light", "plaza_lower", "granite_dark",
         "brick_red", "grass", "hdri", "mdl"],
        hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene19")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    C = PARAMS["center"]
    cx, cy = C["cx"], C["cy"]

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        scl = mp["scale"]
        M = {}
        M["upper"] = sc.make_pbr(
            stage, "/World/Looks/Upper", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["lower"] = sc.make_pbr(
            stage, "/World/Looks/Lower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            scl["plaza_lower"], tint=mp["lower_warm_tint"])
        # 단 재질 = 밝은 plaza_light (벽 granite_dark 와 대비) [A-19①]
        M["step"] = sc.make_pbr(
            stage, "/World/Looks/Step", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        # 건물 모서리 L벽·newel = 어두운 화강암(granite_dark) — 단과 대비
        M["granite"] = sc.make_pbr(
            stage, "/World/Looks/Granite", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"), sc.tex_path("granite_dark", "rough"),
            scl["granite_dark"])
        M["brick"] = sc.make_pbr(
            stage, "/World/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            scl["brick_red"])
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            scl["grass"], tint=mp["grass_tint"])
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
        M["hvac"] = sc.make_pbr(stage, "/World/Looks/Hvac",
                                diffuse_color=mp["hvac_color"], metallic=0.3,
                                roughness_const=mp["hvac_rough"])
        M["door"] = sc.make_pbr(stage, "/World/Looks/Door",
                                diffuse_color=mp["door_color"], metallic=0.4,
                                roughness_const=mp["door_rough"])
        # [W2-D · §5.6] 우레탄 도막방수(녹색) — 바닥 도막 + 파라펫 치켜올림 동색.
        #   `[시방]` 나라장터 R25BK00911379 "표면 색상은 녹색".
        M["coating"] = sc.make_pbr(stage, "/World/Looks/Coating",
                                   diffuse_color=mp["coating_color"],
                                   roughness_const=mp["coating_rough"])
        M["gk_iron"] = sc.make_pbr(stage, "/World/Looks/GKitIron",
                                   diffuse_color=(0.09, 0.09, 0.095),
                                   metallic=0.55, roughness_const=0.55)
        M["gk_stain"] = sc.make_pbr(stage, "/World/Looks/GKitStain",
                                    diffuse_color=(0.17, 0.19, 0.16),
                                    roughness_const=0.88)
        return M

    # -------------------------------------------------------------------
    # 지반 바닥(잔디) — 전면 슬래브(낙차보다 아래 = 바닥). 4박스 타일링.
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        top, th = g["top_z"], 1.0
        cz = top - th / 2.0
        xm = (g["x0"] + g["x1"]) / 2.0
        ym = (g["y0"] + g["y1"]) / 2.0
        for tag, (x0, x1, y0, y1) in (
                ("SW", (g["x0"], xm, g["y0"], ym)),
                ("SE", (xm, g["x1"], g["y0"], ym)),
                ("NW", (g["x0"], xm, ym, g["y1"])),
                ("NE", (xm, g["x1"], ym, g["y1"]))):
            sc.add_box(stage, f"/World/Scene19/Ground_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                       (x1 - x0, y1 - y0, th), M["grass"])

    # -------------------------------------------------------------------
    # 상·하부 보도(재질 경계) — 솔리드 슬래브(지반 −2.31 까지). 계단 밖(r≥4).
    # -------------------------------------------------------------------
    def build_walkways(M, hazard):
        base = PARAMS["ground"]["top_z"]
        for name, mtl in (("upper", M["upper"]), ("lower", M["lower"])):
            w = PARAMS[name]
            top = w["top_z"] if hazard else 0.0    # 평탄 대조군은 전부 z=0
            # [W2-0 · P-A] The upper roof deck is the ground_kit stage.
            sc.skin_exclude(f"/World/Scene19/Walk_{name}")
            sc.add_box(stage, f"/World/Scene19/Walk_{name}",
                       ((w["x0"] + w["x1"]) / 2.0, (w["y0"] + w["y1"]) / 2.0,
                        (top + base) / 2.0),
                       (w["x1"] - w["x0"], w["y1"] - w["y0"], top - base),
                       mtl, collider=True)
        # [접근성 v2] 코너 슬래브: winder 외호(r4)와 보도 직선 에지(x=4/y=4)
        #   사이 쐐기(최대 폭 1.66)를 채우는 바닥. hazard=하부 광장 연장(−1.95),
        #   평탄 대조군=z0. 벽 내부와 겹치는 x/y<0 밴드는 벽 볼륨에 매립(비가시).
        co = PARAMS["access"]["corner"]
        top = PARAMS["lower"]["top_z"] if hazard else 0.0
        sc.add_box(stage, "/World/Scene19/CornerSlab",
                   ((co["x0"] + co["x1"]) / 2.0, (co["y0"] + co["y1"]) / 2.0,
                    (top + base) / 2.0),
                   (co["x1"] - co["x0"], co["y1"] - co["y0"], top - base),
                   M["lower"], collider=True)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P6 roof_membrane (사양 §5.6 scene19 행)
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        up = PARAMS["upper"]
        ins = float(g["region_inset"])
        ox = float(g["grid_origin_x"])
        s_edge = ox - float(up["x0"])          # axis "-x": s = origin_x - x
        gp = gk.plan_ground(
            "roof_membrane",
            region=(up["x0"] + ins, up["y0"] + ins,
                    up["x1"] - ins, up["y1"] - ins),
            z=float(up["top_z"]), gy=0.0, origin=(ox, 0.0, 0.0), axis="-x",
            edges=[("roof_edge", s_edge)], dists=(2, 3.5, 5),
            scene="scene19", tactile=(),
            overrides=dict(infra=dict(gully=2),
                           surface=(("patch", 4),
                                    ("stain", ("water", "drip", "dirt")))),
            extras_args=dict(membrane=dict(seam_pitch=float(g["seam_pitch"]),
                                           wear_n=int(g["wear_n"]))),
            sites=dict(gully=[tuple(v) for v in g["drains"]],
                       patch=[tuple(v) for v in g["patches"]]),
            seed=19)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(membrane=M["coating"], membrane_seam=M["gk_stain"],
                  membrane_wear=M["coating"], patch=M["coating"],
                  patch_cut=M["gk_stain"], gully=M["gk_iron"],
                  manhole=M["gk_iron"], trench=M["gk_iron"],
                  trench_frame=M["gk_iron"], joint=M["gk_stain"],
                  crack=M["gk_stain"], weed=M["grass"], wear=M["gk_stain"],
                  stain_water=M["gk_stain"], stain_drip=M["gk_stain"],
                  stain_dirt=M["gk_stain"])
        res = gk.apply_ground(kit, "/World/Scene19/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene19 P6 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # winder 12단 + newel + 건물 L벽 + 외측 파라펫
    # -------------------------------------------------------------------
    # [옥상 v4] _step_top 은 [C] 절의 모듈 스코프 정의를 그대로 쓴다
    #   (조립 ↔ 차폐 검산이 같은 단 상면을 읽도록 단일 출처화).

    def build_winder(M):
        w = PARAMS["winder"]
        for i in range(w["n"]):
            a0 = w["a0"] + i * w["sector_deg"]
            sc.build_arc_steps(stage, f"/World/Scene19/Step_{i}", cx, cy,
                               w["r_in"], w["r_out"], a0, a0 + w["sector_deg"],
                               w["seg"], _step_top(i), w["base_z"], M["step"])
        # 내측 코너 newel
        nw = PARAMS["newel"]
        sc.add_cylinder(stage, "/World/Scene19/Newel",
                        (cx, cy, (nw["z_top"] + nw["z_bot"]) / 2.0),
                        nw["r"], nw["z_top"] - nw["z_bot"], M["granite"],
                        collider=True)
        # 건물 모서리 L벽 2면
        wl = PARAMS["walls"]
        zc = (wl["z_top"] + wl["z_bot"]) / 2.0
        hz = wl["z_top"] - wl["z_bot"]
        for tag in ("south", "west"):
            b = wl[tag]
            sc.add_box(stage, f"/World/Scene19/Wall_{tag}",
                       ((b["x0"] + b["x1"]) / 2.0, (b["y0"] + b["y1"]) / 2.0, zc),
                       (b["x1"] - b["x0"], b["y1"] - b["y0"], hz), M["granite"],
                       collider=True)
        # 외측 낮은 파라펫: 입구(sector 0..1)·출구(10..11)는 개방[접근성 v2],
        #   중간 sector 만 호 링(각 단 상면 +h)
        pp = PARAMS["parapet"]
        ac = PARAMS["access"]
        for i in range(ac["parapet_first"], ac["parapet_last"] + 1):
            a0 = w["a0"] + i * w["sector_deg"]
            top = _step_top(i)
            sc.build_arc_steps(stage, f"/World/Scene19/Parapet_{i}", cx, cy,
                               pp["r_in"], pp["r_out"], a0, a0 + w["sector_deg"],
                               1, top + pp["h"], top - 0.1, M["parapet"],
                               collider=True)
        # 파라펫 양끝 게이트 기둥 (개방부 시작 표시, look_refs 시안) — 금속.
        #   기둥 밑단은 개방측(더 낮은) 단 상면 기준 −0.05 매립 → 부유 방지
        r_mid = (pp["r_in"] + pp["r_out"]) / 2.0
        for tag, top, ang in (
                ("entry", _step_top(ac["parapet_first"]),
                 w["a0"] + ac["parapet_first"] * w["sector_deg"]),
                ("exit", _step_top(ac["parapet_last"] + 1),
                 w["a0"] + (ac["parapet_last"] + 1) * w["sector_deg"])):
            a = math.radians(ang)
            sc.add_cylinder(stage, f"/World/Scene19/GatePost_{tag}",
                            (cx + r_mid * math.cos(a), cy + r_mid * math.sin(a),
                             top - 0.05 + ac["post_h"] / 2.0),
                            ac["post_r"], ac["post_h"], M["rail"])

    # -------------------------------------------------------------------
    # [접근성 v2] 상부 문턱 + 에지 가드 — 보행 연속성 (look_refs 시안)
    # -------------------------------------------------------------------
    def build_access(M):
        ac = PARAMS["access"]
        up = PARAMS["upper"]
        low_z = PARAMS["lower"]["top_z"]
        # 문턱 슬리버: 보도(z0)와 입구 sector 외호 사이 틈을 보도 포장재로 채움.
        #   내호측(r<4)으로 물린 밴드는 입구 단(step0/1) 외곽에 매립 → 유효 답면
        #   경계가 x=3.86 으로 일관
        th = ac["threshold"]
        sc.add_box(stage, "/World/Scene19/Threshold",
                   ((th["x0"] + up["x0"]) / 2.0, (th["y0"] + th["y1"]) / 2.0,
                    (up["top_z"] + low_z) / 2.0),
                   (up["x0"] - th["x0"], th["y1"] - th["y0"],
                    up["top_z"] - low_z), M["upper"], collider=True)
        # 에지 가드 옹벽: 문턱 북측 보도 에지(코너 슬래브까지 1.95 낙차) 방호.
        #   코너 슬래브 상면(−1.95)에서 보도 위 +1.0 까지
        gd = ac["guard"]
        sc.add_box(stage, "/World/Scene19/EdgeGuard",
                   ((gd["x0"] + gd["x1"]) / 2.0, (gd["y0"] + gd["y1"]) / 2.0,
                    (low_z + gd["h_top"]) / 2.0),
                   (gd["x1"] - gd["x0"], gd["y1"] - gd["y0"],
                    gd["h_top"] - low_z), M["parapet"], collider=True)

    # -------------------------------------------------------------------
    # [옥상 v3] 옥상 파라펫(외곽 방호) + 설비 소품 + 옥탑 문
    #   — 장면 맥락단서(설비 역추론·스케일 앵커). 위험 기하(winder) 불변.
    # -------------------------------------------------------------------
    def build_rooftop(M):
        rf = PARAMS["roof"]
        up, lo = PARAMS["upper"], PARAMS["lower"]
        t, h, hi = rf["pp_t"], rf["pp_h"], rf["pp_h_inner"]

        cw = rf["coping_w"]
        tu = rf["turnup_h"]

        def pp(tag, x0, x1, y0, y1, base, hh, ref=None):
            sc.add_box(stage, f"/World/Scene19/RoofPP_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                        base - 0.05 + (hh + 0.05) / 2.0),
                       (x1 - x0, y1 - y0, hh + 0.05), M["parapet"],
                       collider=True)
            ref = ref or up                    # deck this parapet belongs to
            # [W2-D · 사양 §5.6 19-2] **치켜올림 + 두겁**.
            #   ① turn-up: the waterproofing coat wraps the parapet's inner
            #      face for `turnup_h` (0.30 m) — it is the same green as the
            #      deck, not concrete. `[시방]` "내벽 및 상부까지 전체를 감아 도포".
            #   ② coping: a cap `coping_w` (0.45~0.55) wide **centred** on the
            #      parapet, so it overhangs 0.125 m each side with a drip edge
            #      instead of cantilevering over the deck. Both are 12 mm
            #      plates — no GT change, no camera occlusion (the roof_context
            #      eye sits at z 1.9, above the 1.15~1.20 parapet crown).
            #   Orientation is derived from the box: the long axis is the run,
            #   the short axis is the thickness, and "inner" is the side that
            #   faces the centre of the deck this parapet belongs to (`ref`) —
            #   passing `ref` matters for the lower terrace ring, whose
            #   east parapet has the deck on its **-X** side, the opposite of
            #   the upper deck's.
            sx, sy = x1 - x0, y1 - y0
            cxm, cym = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            top = base - 0.05 + (hh + 0.05)
            if sx <= sy:                       # runs along Y, thickness in X
                inner = 1.0 if cxm < (ref["x0"] + ref["x1"]) / 2.0 else -1.0
                sc.add_box(stage, f"/World/Scene19/RoofTurn_{tag}",
                           (cxm + inner * (sx / 2.0 + 0.006), cym,
                            base + tu / 2.0), (0.012, sy, tu), M["coating"])
                sc.add_box(stage, f"/World/Scene19/RoofCope_{tag}",
                           (cxm, cym, top + 0.006),
                           (cw, sy, 0.012), M["parapet"])
            else:                              # runs along X, thickness in Y
                inner = 1.0 if cym < (ref["y0"] + ref["y1"]) / 2.0 else -1.0
                sc.add_box(stage, f"/World/Scene19/RoofTurn_{tag}",
                           (cxm, cym + inner * (sy / 2.0 + 0.006),
                            base + tu / 2.0), (sx, 0.012, tu), M["coating"])
                sc.add_box(stage, f"/World/Scene19/RoofCope_{tag}",
                           (cxm, cym, top + 0.006),
                           (sx, cw, 0.012), M["parapet"])

        # 상부 옥상(z0) 외곽: 동(x1)·남(y0)·서(x0, 남단..L벽 y0)·북(하부 테라스 경계)
        pp("U_E", up["x1"] - t, up["x1"], up["y0"], up["y1"], up["top_z"], h)
        pp("U_S", up["x0"], up["x1"] - t, up["y0"], up["y0"] + t, up["top_z"], h)
        pp("U_W", up["x0"], up["x0"] + t, up["y0"] + t, -1.0, up["top_z"], h)
        pp("U_N", up["x0"], up["x1"], up["y1"] - t, up["y1"], up["top_z"], hi)
        # 하부 테라스(−1.95) 외곽: 서(x0)·북(y1)·동(x1, 상부 몸체 밖 y>4)
        pp("L_W", lo["x0"], lo["x0"] + t, lo["y0"], lo["y1"], lo["top_z"], h, lo)
        pp("L_N", lo["x0"] + t, lo["x1"], lo["y1"] - t, lo["y1"], lo["top_z"], h, lo)
        pp("L_E", lo["x1"] - t, lo["x1"], lo["y0"], lo["y1"] - t, lo["top_z"], h, lo)

        # 실외기(기단 0.1 + 본체) + 거위목 환기구 + 배관 런 — 상부 옥상
        hs = rf["hvac_size"]
        for i, u in enumerate(rf["hvac"]):
            sc.add_box(stage, f"/World/Scene19/HvacBase_{i}",
                       (u["cx"], u["cy"], up["top_z"] + 0.05),
                       (hs[0] + 0.1, hs[1] + 0.1, 0.1), M["granite"])
            sc.add_box(stage, f"/World/Scene19/Hvac_{i}",
                       (u["cx"], u["cy"], up["top_z"] + 0.1 + hs[2] / 2.0),
                       hs, M["hvac"])
        v = rf["vent"]
        sc.add_cylinder(stage, "/World/Scene19/Vent",
                        (v["cx"], v["cy"], up["top_z"] + v["h"] / 2.0),
                        v["r"], v["h"], M["hvac"])
        sc.add_cylinder(stage, "/World/Scene19/VentCap",
                        (v["cx"] + v["r"] * 1.2, v["cy"],
                         up["top_z"] + v["h"] + v["r"] * 0.4),
                        v["r"] * 0.9, v["r"] * 2.6, M["hvac"], rotY=90.0)
        p = rf["pipe"]
        sc.add_cylinder(stage, "/World/Scene19/PipeRun",
                        ((p["x0"] + p["x1"]) / 2.0, p["y"],
                         up["top_z"] + p["r"] + 0.02),
                        p["r"], p["x1"] - p["x0"], M["hvac"], rotY=90.0)
        # 옥탑 철문 — L벽 south 동단면(x=4, 폭 1m)의 상부 테라스 레벨.
        #   진입 문턱 바로 옆이라 "옥탑 코어에서 나와 코너 계단으로" 동선이 읽힘.
        d = rf["door"]
        ws = PARAMS["walls"]["south"]
        sc.add_box(stage, "/World/Scene19/CoreDoor",
                   (ws["x1"] + 0.02, (ws["y0"] + ws["y1"]) / 2.0,
                    up["top_z"] + d["h"] / 2.0),
                   (0.04, d["w"], d["h"]), M["door"])

    # -------------------------------------------------------------------
    # 드레싱 — 화단 + 원경 건물 + [옥상 v3] 옥상 맥락 요소
    # -------------------------------------------------------------------
    def build_dressing(M):
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        pl = PARAMS["roof"]["planter"]     # [옥상 v4] 위치는 PARAMS 단일 출처
        sc.build_planter(stage, "/World/Scene19/Planter_A",
                         pl["cx"], pl["cy"], 0.0,
                         M["granite"], M["grass"], tree_mtls=tree_mtls,
                         size=pl["size"])
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"/World/Scene19/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"])
        build_rooftop(M)

    # -------------------------------------------------------------------
    # 단서 토글 (기하 불변)
    # -------------------------------------------------------------------
    def build_cues(M):
        w = PARAMS["winder"]
        pp = PARAMS["parapet"]
        # cue_railing: 파라펫 상단 핸드레일(단별 호 캡) — 파라펫 존치 구간만
        if cfg.get("cue_railing"):
            ac = PARAMS["access"]
            for i in range(ac["parapet_first"], ac["parapet_last"] + 1):
                a0 = w["a0"] + i * w["sector_deg"]
                top = _step_top(i) + pp["h"]
                sc.build_arc_steps(stage, f"/World/Scene19/Rail_{i}", cx, cy,
                                   pp["r_out"] - 0.06, pp["r_out"], a0,
                                   a0 + w["sector_deg"], 1, top + 0.06,
                                   top - 0.06, M["rail"], collider=False)
        # cue_tactile: 상부 접근 경고 점자띠(첫 단 앞)
        if cfg.get("cue_tactile"):
            # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
            tac = sc.tactile_pbr(stage, "/World/Looks/Tactile")
            sc.build_tactile(stage, "/World/Scene19/Tactile",
                             4.1, 4.5, -1.0, 1.0, tac, z=0.0)
        # cue_nosing: 방사형 단코 논슬립 아크 밴드
        if cfg.get("cue_nosing"):
            nos = sc.make_pbr(stage, "/World/Looks/Nosing",
                              diffuse_color=mp["nosing_color"],
                              roughness_const=mp["nosing_rough"])
            for i in range(w["n"]):
                a0 = w["a0"] + i * w["sector_deg"]
                top = _step_top(i)
                sc.build_arc_steps(stage, f"/World/Scene19/Nosing_{i}", cx, cy,
                                   w["r_out"] - 0.06, w["r_out"], a0,
                                   a0 + w["sector_deg"], 1, top + 0.004,
                                   top - 0.02, nos, collider=False)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hazard = cfg["hazard_stairs"]
    build_ground(M)
    build_walkways(M, hazard)
    if hazard:
        build_winder(M)
        build_access(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if hazard:
        build_cues(M)
    build_ground_kit(M)             # [W2-D] 지면 요소 — 드레싱 뒤(산포 순서 규약)
    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        nprim = sum(1 for pr in stage.Traverse() if pr.IsA(UsdGeom.Gprim))
        print(f"SMOKE_OK prims={nprim}")
        simulation_app.close()
        return

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
    _v0 = VIEWS["upper_approach"]
    look_from(_v0["eye"], _v0["tgt"])

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    if capture_mode:
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
                            set_render_mode, look_from)
        simulation_app.close()
        return

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene19_{ts}.png")
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
