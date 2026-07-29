# -*- coding: utf-8 -*-
"""
sceneN5_flush_grating.py — NegObs 인공씬 25호: 평면 그레이팅·맨홀 (Isaac Sim 4.5)

유형    : N5 Hard Negative — flush 배수 그레이팅 + 주철 맨홀 (GT = 전 픽셀 낙차 없음)
사양서  : Docs/nanobanana_batch1_geometry_map.md §A sceneN5_flush_grating
룩참조  : look_refs/n5_grating.jpg
공통    : scene_common.py (검증된 API 헬퍼) · scene16_canopy_shadow.py (골격)
          scene11_grating_fireescape.py (그레이팅 슬랫 패턴·암색 금속 재질)

위험 본질(반례): **낙차는 어디에도 없다.** 콘크리트 보도를 사선으로 횡단하는 폭
           0.4m 장대 배수 그레이팅과 주철 맨홀 2개가 전부 노면과 flush다. 슬랫
           사이는 "뚫려 보이지만" 실제로는 z=−0.05의 암색 바닥판이 받치는 **얕은
           암부**이며 실개구는 없다(GT 낙차 0이므로 실제 구멍 금지).
           T19(scene11 그레이팅 비상계단, 개방·투과·양성)와 **같은 재질 계열의
           대조쌍** — "flush면 안전, 개방이면 낙차"를 재질이 아니라 기하로
           구분하도록 강제한다.
목표     : 평탄 콘크리트 보도(대형 슬래브 줄눈) + 사선 그레이팅 스트립(슬랫 714매)
           + 맨홀 2 + 옹벽·건물을 조립, 렌더로 판정 (렌더 전용). GT 낙차 = 전 0.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneN5_flush_grating.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneN5_flush_grating.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneN5_flush_grating.py
기하·드레싱 검산:       NEGOBS_GEOCHECK=1 python3 sceneN5_flush_grating.py (Isaac 불요)

좌표계: Z-up, m, 진행축 +X. 낙차 없음 — 그레이팅이 (3.0, 0.0)을 지나 yaw 62°로
        횡단(x≈0~6 구간에서 화면을 가로지름).
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
#     "씬 특색 요소(그레이팅·맨홀)" 토글. 해당 없는 cue 키는 False + 사유 주석.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_flush_grating": True,  # False → 그레이팅·맨홀 제거(민무늬 보도 대조군)
    "cue_railing":        False,  # 낙차 없음 → 방호 난간 비관행. 키만 예약
    "cue_tactile":        False,  # 그레이팅 주변 점자블록 비관행. 키만 예약
    "cue_material_break": True,   # 보도 슬래브 줄눈 격자. False → 무줄눈
    "cue_nosing":         False,  # 단이 없음 → 논슬립 띠 무의미. 키만 예약
    "cue_sign":           False,  # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,   # 옹벽·화단·볼라드·원경 건물(지평선 폐쇄) 일괄
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # ─ 그레이팅(사선 트렌치 드레인). rot_group(pivot, yaw)의 **로컬 좌표**로 기술:
    #   로컬에서 스트립은 y=0 축을 따라 +X로 뻗고, 그룹이 pivot 기준 yaw 회전한다.
    #   pivot 의 y 는 0 이어야 로컬 y=0 축이 곧 드레인 축이 된다 [고정].
    drain=dict(
        pivot=(3.0, 0.0), yaw=62.0, half_len=15.0,
        slot_half=0.200,      # 개구(슬롯) 반폭 — 프레임 안쪽 면
        pave_inner=0.205,     # 보도 평판 안쪽 면(프레임보다 5mm 뒤 → 동일평면 회피)
        rail_outer=0.260,     # 프레임 레일 바깥 면
        rail_top=0.002, rail_bot=-0.060,
        plate_half=0.250, plate_top=-0.050, plate_bot=-0.300,
        bar_t=0.012, bar_h=0.020, bar_top=0.001, bar_ylen=0.460,
        pitch=0.042,          # bar_t 0.012 + 슬롯 간격 0.030
        clip_half=0.320,      # 줄눈 절단 반폭(rail_outer 0.26 + 여유)
        pave_half=70.0, pave_thick=0.5,
    ),
    # ─ 맨홀(주철, flush). proud 3층: frame 0.0012 < lid 0.0020 < boss 0.0030
    manholes=[dict(name="A", cx=6.0, cy=2.2), dict(name="B", cx=9.5, cy=1.2)],
    manhole=dict(r_frame=0.42, r_lid=0.35, r_boss=0.09, h=0.03,
                 proud_frame=0.0012, proud_lid=0.0020, proud_boss=0.0030),
    # ─ 보도 슬래브 줄눈(최하층 proud 0.0006) — 드레인 회랑에서 잘라낸다
    joints=dict(spacing=3.0, width=0.03, proud=0.0006,
                x0=-9.0, x1=15.0, y0=-9.0, y1=9.0),

    # ═══ [W2 ground_kit] P-A 검증 씬 ══════════════════════════════════════
    #  ★ 이 씬은 사양 §1.4 의 **P-A(스킨 OFF) A/B 증명 대상**이다. 요소가 이미
    #    다 있는데 룩 ON 에서 매몰돼 있다 — 스킨만 끄면 결과가 즉시 보인다.
    #    합격선: 맨홀 ROI(px 500–1100 × 350–750) 암부 화소 0.02 % → **≥ 4.5 %**,
    #            |∇| p99 0.079 → **≥ 0.30**, approach 강황색 화소 **≥ 1,500 px**.
    #  ★ 신설 맨홀 1기 — **근경 창 W1**(d2 에서 지면거리 0.564~2.00 m). 사선 드레인
    #    축(pivot(3,0)·yaw 62°)에서 x 기준 4.3 m 이격이라 그레이팅 특색과 무간섭.
    ground=dict(
        region=(-12.0, -3.0, 2.0, 3.0),      # 보도 회랑(드레인 남측 대역)
        manhole_w1=(-1.15, 0.30),            # [F d2] 화면폭 f·0.648/0.85 = 1,268 px
        gullies=[(-4.0, -2.6), (-9.0, -2.6)],
        # 볼라드 열 전면 연속 띠 — §12.5 ② "소판 0.40×0.30 → 폭 0.60 연속 띠"
        #   면적 0.12 ㎡/본 × 5 → 4.2 ㎡ = 35배. relief="normal" 이라 프림 1.
        tactile_band=(4.0, -5.70, 11.0, -5.10),
    ),

    # ═══ 맥락 드레싱 — "차도 옆 도시 보도"를 렌더만으로 확정 ══════════════
    #  ★ GT 불변: 연석은 **평지 위 융기 스트립**(양측 지면 모두 z≈0) → 실낙차
    #    아님. 차도 슬래브도 포장(z=0) 위 proud 0.0010 의 flush 판이다.
    #    (보도 평판 Pave_S/N 이 ±70 m 를 덮으므로 차도는 그 위에 얹는다.)
    #  ★ 드레인 회랑 회피: 드레인 축은 pivot(3,0)·yaw 62° → y=−8.70 에서
    #    x=−1.63 (회랑 반폭 0.294 → x∈[−1.92,−1.33]). 차도·연석을 x0=0.0 에서
    #    시작시켜 1.33 m 이격한다. 차도의 −X 시단(x=0)은 전 뷰 프레임 밖임을
    #    geocheck() ③ 에서 검산.
    road=dict(x0=0.0, x1=51.0, y0=-22.0, y1=-8.70, z_top=0.0010, thick=0.40),
    #   연석: y_out = 차도측 면(차도 안으로 0.05 물림), y_in = 보도측 면
    curbs=[dict(name="N", y_out=-8.75, y_in=-8.40),      # 보도측 연석
           dict(name="F", y_out=-21.95, y_in=-22.30)],   # 건너편 연석
    curb=dict(x0=0.0, x1=51.0, h=0.16),
    #   차도 도색 (차도면 0.0010 위 1.6 mm) — 중앙 파선 + 양측 가장자리 실선
    road_dash=dict(y=-15.35, x0=0.0, x1=51.0, dash=3.0, gap=6.0,
                   width=0.12, proud=0.0026, thick=0.012),
    road_edges=[dict(name="N", y=-9.15), dict(name="F", y=-21.25)],
    road_edge=dict(x0=0.0, x1=51.0, width=0.12),
    #   가로수 열 — 보도 시설물대(연석 −8.40 과 볼라드열 −6.00 사이)
    street_trees=[dict(name="A", cx=2.0), dict(name="B", cx=8.0),
                  dict(name="C", cx=14.0), dict(name="D", cx=20.0)],
    street_tree=dict(cy=-7.30, pit=1.20, pit_proud=0.0020, pit_thick=0.02,
                     trunk_r=0.075, trunk_h=2.40),
    #   자전거 거치대(U형 후프 3) + 안내 사인 1본(입간판급)
    rack=dict(cx=12.5, cy0=4.60, step=0.80, count=3, span=0.70,
              bar_r=0.030, h=0.75),
    entry_sign=dict(x=12.0, y=-5.80, yaw=180.0, w=0.8, h=0.8,
                    pole_h=2.2, pole_r=0.045),
    #   옹벽 — 보도 배면(부지 경계)을 따라 X 로 종주. 카메라 최근접은
    #   manhole_pair eye(1.5, 5.0) 로 3.0 m 이격.
    #   ※ 사선 드레인이 y=8.0~8.45 를 x≈7.25~7.49 에서 통과하므로 그 자리에
    #     **개구(보행 통로)** 를 둔다 — 벽이 드레인 위에 서는 결함 방지.
    #     개구 범위는 _drain_axis() 로부터 자동 산출(gap_clear 여유).
    wall=dict(x0=-20.0, x1=34.0, y0=8.00, y1=8.45, h=1.10,
              cap_h=0.06, cap_over=0.04, gap_clear=0.55),
    planters=[dict(name="A", cx=-4.0, cy=-6.30, base_z=0.0, tree=False),
              dict(name="B", cx=16.0, cy=6.20, base_z=0.0, tree=True)],
    planter=dict(size=3.0, curb_h=0.45, curb_t=0.25, cap_over=0.05,
                 cap_h=0.05, grass_h=0.40),
    # ── 볼라드 [v5.1 §2 · ctx2] ───────────────────────────────────────────
    #   위치(보도 시설물대 y=−6.00, 연석 −8.40 과 보행대 사이)는 **유지**.
    #   구(舊) 간격 3.5 m · h0.75 · 반사띠/점형블록 없음
    #   → 신(新) 간격 1.40 m(=7.0/5, "1.5 m 내외") · h0.90 · φ0.12 ·
    #      상단 백색 반사띠 · 전면(보도측 +Y) 0.3 m 점형블록.
    #   ★ 특색(사선 그레이팅) 보존: 드레인 축은 y=−6.00 에서 x=−0.19 를
    #     지난다. 볼라드 열은 x 4.0~11.0 이라 최근접 4.19 m — 그레이팅
    #     본체·판정 시선과 무간섭(드레싱 검산 ②로 재확인).
    bollards=dict(y=-6.0, x0=4.0, x1=11.0, spacing=1.5, r=0.06, h=0.90,
                  front=(0.0, 1.0)),
    buildings=dict(
        # 원경 비스타 차단(+X 지평선): 파사드 -X평면. y0 은 차도를 비켜 −4.0.
        C=dict(x0=34.0, x1=44.0, y0=-4.0, y1=26.0, h=14.0, floors=4,
               axis="x", facade_x=34.0, face_dir=-1.0),
        # 차도 건너편 가로 벽면 — "여기는 차도 옆 보도"를 결정짓는 단서
        D=dict(x0=8.0, x1=44.0, y0=-34.0, y1=-24.0, h=12.0, floors=4,
               axis="y", facade_y=-24.0, face_dir=1.0),
        # 차도 소실점 폐쇄(+X) + 배후 스카이라인 고층
        E=dict(x0=52.0, x1=64.0, y0=-30.0, y1=-8.0, h=20.0, floors=6,
               axis="x", facade_x=52.0, face_dir=-1.0),
        T=dict(x0=48.0, x1=58.0, y0=2.0, y1=26.0, h=32.0, floors=9,
               axis="x", facade_x=48.0, face_dir=-1.0),
    ),
    window=dict(w=1.3, h=1.7, inset=0.15, col_step=3.0, margin=2.5),

    material=dict(
        scale=dict(plaza_light=1.1, concrete_wall=2.0, grass=4.0,
                   brick_red=2.0),
        # 보도: plaza_light 원본 평균 sRGB 0.714 + 약한 중성 틴트 → ~0.64
        pave_tint=(0.90, 0.89, 0.86),
        joint_color=(0.06, 0.06, 0.06), joint_rough=0.85,
        # 주철(그레이팅 슬랫·프레임·맨홀): sRGB 0.02~0.06 대역 [규약]
        iron_color=(0.045, 0.045, 0.048), iron_rough=0.55, iron_metallic=0.5,
        lid_color=(0.040, 0.040, 0.045), lid_rough=0.50, lid_metallic=0.6,
        frame_color=(0.050, 0.050, 0.052), frame_rough=0.65, frame_metallic=0.4,
        # 트렌치 바닥판: 얕은 암부 (개구가 아니라 "어두워 보이는 바닥")
        trough_color=(0.040, 0.040, 0.040), trough_rough=0.90,
        wall_tint=(0.90, 0.90, 0.88),
        grass_tint=(0.55, 0.68, 0.42),
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.88, 0.86, 0.82), parapet_rough=0.6,
        # ─ 맥락 드레싱 신규 ─
        asphalt_color=(0.16, 0.16, 0.17), asphalt_rough=0.90,  # 구 아스팔트 표준
        roadpaint_color=(0.60, 0.59, 0.56), roadpaint_rough=0.70,
        pit_color=(0.055, 0.052, 0.048), pit_rough=0.90,       # 수목보호판(암색)
        steel_color=(0.62, 0.64, 0.66), steel_metallic=0.85, steel_rough=0.35,
        # ─ 볼라드 v5.1: 스테인리스 몸통 + 상단 백색 반사띠(소면적) +
        #   전면 점형블록(황색) ─
        bollard_color=(0.78, 0.80, 0.83), bollard_metallic=0.85,
        bollard_rough=0.34,
        bollard_band_color=(0.88, 0.88, 0.86),
        tactile_color=(0.80, 0.66, 0.14), tactile_rough=0.70,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
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
    # ─── SUN_AZ_OFFSET = 171.5 (v3 §A-7 표준 유지 — 적극적 사유 있음).
    #     태양 매핑: 월드 태양 az ≈ 33.5 + 171.5 = 205° → 광선 진행 방위 25°.
    #     슬롯 침투 검산: 슬랫 상면(z=+0.001) → 바닥판(z=−0.050) 깊이 0.051 m.
    #       수평 이동 = 0.051·cot(49.79°) = 0.0431 m, 그 중 드레인 축(62°) 성분
    #       = 0.0431·|cos(25°−62°)| = 0.0344 m > 슬롯 간격 0.030 m
    #       ⇒ **직달광이 바닥판에 닿지 않는다** → 슬롯이 확실히 암부로 읽힌다
    #          (레퍼런스 n5의 검은 슬릿 재현). 동시에 보도면은 정면광으로 밝다.
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN5")

ASSET_ROLES = ["plaza_light", "concrete_wall", "grass", "brick_red",
               "sign_info", "hdri", "mdl"]


# ===========================================================================
# [D] 줄눈 절단 — 사선 드레인 회랑을 통과하는 줄눈 스트립은 두 토막으로
#     (드레인 위를 줄눈 박판이 가로지르면 슬롯 위에 막대가 뜬 것처럼 보인다)
# ===========================================================================
def _drain_axis():
    """(px, py, cosθ, sinθ, half_len, clip_half) — 월드 드레인 축 파라미터."""
    d = PARAMS["drain"]
    th = math.radians(float(d["yaw"]))
    return (float(d["pivot"][0]), float(d["pivot"][1]),
            math.cos(th), math.sin(th), float(d["half_len"]),
            float(d["clip_half"]))


def _cut_span(a0, a1, center, half, s_at, half_len):
    """[a0,a1] 에서 [center±half] 를 제거한 세그먼트 리스트.
    s_at: 절단 지점의 드레인 축 파라미터(=중심에서의 거리). |s_at|>half_len 이면
    그 자리에 드레인이 실재하지 않으므로 자르지 않는다."""
    if abs(s_at) > half_len or center + half <= a0 or center - half >= a1:
        return [(a0, a1)]
    segs = []
    if center - half > a0:
        segs.append((a0, center - half))
    if center + half < a1:
        segs.append((center + half, a1))
    return segs


def wall_segments():
    """옹벽을 드레인 통과부에서 두 토막으로 — [(xa,xb), (xa,xb)].
    벽 밴드 y∈[y0,y1] 과 드레인 축의 교점 x 범위 ± (회랑 반폭/|sinθ| + 여유).
    """
    px, py, ct, st_, hl, wc = _drain_axis()
    wl = PARAMS["wall"]
    d = PARAMS["drain"]
    xs = []
    for yy in (wl["y0"], wl["y1"]):
        t = (yy - py) / st_
        xs.append(px + t * ct)
    half = float(d["rail_outer"]) / abs(st_) + float(wl["gap_clear"])
    ga, gb = min(xs) - half, max(xs) + half
    return [(wl["x0"], ga), (gb, wl["x1"])]


def build_views():
    """카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷.
    ※ 그레이팅 양끝(월드 (10.04,13.24)/(−4.04,−13.24))이 프레임에 들어오면
      '중간에서 끊긴 드레인'으로 보인다 — 전 컷에서 화면 밖임을 검산했다
      (NEGOBS_GEOCHECK=1). 최소 여유는 preset_*_d10 의 수평 33.5°(한계 30°)."""
    views = sc.grid_views(0.0)
    # approach: 보도를 따라 그레이팅으로 보행 접근
    views["approach"] = dict(eye=[-6.0, 0.0, 1.6], tgt=[4.0, 0.0, 0.1])
    # grating_close: 근접·사선 — 슬롯 암부와 flush 여부 판독 [1순위]
    views["grating_close"] = dict(eye=[1.0, 3.2, 0.7], tgt=[4.2, 0.2, -0.2])
    # manhole_pair: 맨홀 2개 + 사선 드레인 (룩참조 n5 구도)
    views["manhole_pair"] = dict(eye=[1.5, 5.0, 1.3], tgt=[8.0, 0.5, -0.2])
    # beauty_oblique: +Y 사선 부감 — 전체 배치 인상
    views["beauty_oblique"] = dict(eye=[-4.0, 5.5, 2.6], tgt=[5.5, -0.5, -0.3])
    return views


def geocheck():
    """Isaac 없이: ①그레이팅 끝단 프레임인 ②줄눈 절단 ③슬롯 광학 검산."""
    px, py, ct, st, hl, wc = _drain_axis()
    d = PARAMS["drain"]
    ends = [(px + hl * ct, py + hl * st), (px - hl * ct, py - hl * st)]
    hfov, vfov = 60.0, 36.0
    print("=" * 68)
    print("sceneN5 기하 검산")
    print("  드레인 축: pivot(%.2f, %.2f) yaw %.1f° half_len %.1f"
          % (px, py, PARAMS["drain"]["yaw"], hl))
    print("  끝단 월드좌표: (%.2f, %.2f) / (%.2f, %.2f)"
          % (ends[0][0], ends[0][1], ends[1][0], ends[1][1]))
    nslat = int(2.0 * hl / d["pitch"])
    print("  슬랫 %d매 (pitch %.3f, bar %.3f, 슬롯 %.3f)"
          % (nslat, d["pitch"], d["bar_t"], d["pitch"] - d["bar_t"]))
    e = math.radians(float(PARAMS["light"]["noon_sun_elev"]))
    depth = d["bar_top"] - d["plate_top"]
    reach = depth / math.tan(e)
    ray_az = math.radians(33.5 + PARAMS["SUN_AZ_OFFSET"] - 180.0)
    axis_comp = reach * abs(math.cos(ray_az - math.radians(d["yaw"])))
    print("  슬롯 침투: 깊이 %.4f → 수평 %.4f → 축성분 %.4f  vs 슬롯 %.3f  → %s"
          % (depth, reach, axis_comp, d["pitch"] - d["bar_t"],
             "차폐(암부)" if axis_comp > d["pitch"] - d["bar_t"] else "관통(밝음!)"))
    worst = (None, 1e9)
    for name, v in sorted(build_views().items()):
        ex, ey, ez = v["eye"]
        vx, vy = v["tgt"][0] - ex, v["tgt"][1] - ey
        vyaw = math.degrees(math.atan2(vy, vx))
        m = 1e9
        for gx, gy in ends:
            dx, dy = gx - ex, gy - ey
            rel = (math.degrees(math.atan2(dy, dx)) - vyaw + 540.0) % 360.0 - 180.0
            m = min(m, abs(rel))
        flag = "IN!!" if m < hfov / 2.0 else "out"
        print("  %-20s 끝단 최소 수평이각 %6.1f°  (한계 %.0f°) %s"
              % (name, m, hfov / 2.0, flag))
        if m < worst[1]:
            worst = (name, m)
    print("  최소 여유 뷰: %s (%.1f°)" % worst)
    # 줄눈 절단
    j = PARAMS["joints"]
    n = int(round((j["y1"] - j["y0"]) / j["spacing"])) + 1
    print("  줄눈 절단 예시 (X평행, y=const):")
    for i in range(n):
        c = j["y0"] + i * j["spacing"]
        if abs(st) < 1e-6:
            continue
        t = (c - py) / st
        xc = px + t * ct
        segs = _cut_span(j["x0"], j["x1"], xc, wc / abs(st), t, hl)
        print("    y=%+6.1f  교차 x=%+7.2f (s=%+6.2f) → 세그 %d개 %s"
              % (c, xc, t, len(segs),
                 ["(%.2f..%.2f)" % s for s in segs]))
    dresscheck()
    print("=" * 68)


# ===========================================================================
# [D2] 맥락 드레싱 검산 — ①드레인 회랑 침범 ②특색 시선 차단 ③카메라 매몰
#      ④차도 −X 시단 프레임인
# ===========================================================================
def street_tree_xs():
    """[v5.1 §3] 가로수 x ±0.30 m 결정적 지터 — 6 m 등간격 인상 제거.
    y(시설물대 −7.30)는 연석(−8.40)·볼라드열(−6.00) 사이 폭이 좁아 불변."""
    return [td["cx"] + bc.jit_scalar(td["cx"], PARAMS["street_tree"]["cy"],
                                     "stN5", -0.30, 0.30)
            for td in PARAMS["street_trees"]]


def planter_placements():
    """[v5.1 §3] 화단 위치 ±0.15 m 지터."""
    out = []
    for p in PARAMS["planters"]:
        dx, dy = bc.jit_pos(p["cx"], p["cy"], "plN5", amp=0.15)
        out.append((p["name"], p["cx"] + dx, p["cy"] + dy, p))
    return out


def bollard_points():
    """[v5.1 §2] 보도 시설물대 볼라드 열 [(x, y), ...] (간격 1.4 m)."""
    bo = PARAMS["bollards"]
    return bc.bollard_line(bo["x0"], bo["y"], bo["x1"], bo["y"],
                           spacing=bo["spacing"])


def dressing_aabbs():
    """드레싱 **입체물**의 (name, xa, xb, ya, yb, z_top). flush 판(차도·도색·
    수목보호판)은 시선 차단과 무관하므로 제외한다."""
    out = []
    cb = PARAMS["curb"]
    for cd in PARAMS["curbs"]:
        out.append((f"Curb_{cd['name']}", cb["x0"], cb["x1"],
                    min(cd["y_out"], cd["y_in"]), max(cd["y_out"], cd["y_in"]),
                    cb["h"]))
    wl = PARAMS["wall"]
    for tag, (a, b) in zip(("W", "E"), wall_segments()):
        out.append((f"Wall_{tag}", a, b, wl["y0"] - wl["cap_over"],
                    wl["y1"] + wl["cap_over"], wl["h"] + wl["cap_h"]))
    st = PARAMS["street_tree"]
    top = st["trunk_h"] + 0.85 + 0.24                 # build_tree 수관 상계
    for td, tx in zip(PARAMS["street_trees"], street_tree_xs()):
        out.append((f"StreetTree_{td['name']}", tx - 0.77,
                    tx + 0.77, st["cy"] - 0.77, st["cy"] + 0.77, top))
    rk = PARAMS["rack"]
    out.append(("Rack", rk["cx"] - rk["span"] / 2.0 - rk["bar_r"],
                rk["cx"] + rk["span"] / 2.0 + rk["bar_r"],
                rk["cy0"] - rk["bar_r"],
                rk["cy0"] + (rk["count"] - 1) * rk["step"] + rk["bar_r"],
                rk["h"] + rk["bar_r"]))
    es = PARAMS["entry_sign"]
    out.append(("EntrySign", es["x"] - es["w"] / 2.0, es["x"] + es["w"] / 2.0,
                es["y"] - 0.10, es["y"] + 0.10, es["pole_h"]))
    pl = PARAMS["planter"]
    ph = pl["size"] / 2.0
    for name, px, py, p in planter_placements():
        zt = pl["curb_h"] + pl["cap_h"]
        if p.get("tree"):
            zt = pl["grass_h"] + 2.2 + 0.85 + 0.24
        out.append((f"Planter_{name}", px - ph, px + ph,
                    py - ph, py + ph, zt))
    bo = PARAMS["bollards"]
    for i, (bx, by) in enumerate(bollard_points()):
        out.extend(bc.bollard_v51_aabbs(f"Bollard_{i}", bx, by, 0.0,
                                        front_dir=bo["front"],
                                        radius=bo["r"], height=bo["h"]))
    for k, bd in PARAMS["buildings"].items():
        out.append((f"Building_{k}", bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                    bd["h"] + 0.5))
    return out


def _in_frame(eye, tgt, p, hfov=60.0, vfov=36.0):
    """점 p 가 (eye→tgt) 카메라 프레임 안인가 (Isaac 기본 h60/v36)."""
    fx, fy, fz = (tgt[0] - eye[0], tgt[1] - eye[1], tgt[2] - eye[2])
    fn = math.sqrt(fx * fx + fy * fy + fz * fz)
    fx, fy, fz = fx / fn, fy / fn, fz / fn
    rx, ry = fy, -fx                                  # f × Z (수평 우측)
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


def _seg_hits_box(p0, p1, bmin, bmax):
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


def dresscheck():
    px, py, ct, st_, hl, wc = _drain_axis()
    d = PARAMS["drain"]
    boxes = dressing_aabbs()
    views = build_views()
    print("-" * 68)
    print("sceneN5 맥락 드레싱 검산")
    # ① 드레인 회랑 침범 — 회랑 반폭 = rail_outer, 축 |t| ≤ half_len
    corr = float(d["rail_outer"])
    bad = 0
    for nm, xa, xb, ya, yb, zt in boxes:
        hit = False
        for cx_ in (xa, xb):
            for cy_ in (ya, yb):
                t = (cx_ - px) * ct + (cy_ - py) * st_       # 축방향
                q = -(cx_ - px) * st_ + (cy_ - py) * ct      # 축직각 거리
                if abs(t) <= hl and abs(q) <= corr:
                    hit = True
        # 상자가 회랑을 가로지르는 경우(모서리는 밖) — 축선 샘플로 보강
        for k in range(121):
            t = -hl + 2.0 * hl * k / 120.0
            ax, ay = px + t * ct, py + t * st_
            if xa <= ax <= xb and ya <= ay <= yb:
                hit = True
        if hit:
            print("  ① ★드레인 회랑 침범★ %s" % nm)
            bad += 1
    rd = PARAMS["road"]
    t_edge = (rd["y1"] - py) / st_
    x_edge = px + t_edge * ct
    print("  ① 회랑 침범 %d건 · 차도 북단(y=%.2f)에서 드레인 x=%.2f "
          "(회랑 x∈[%.2f,%.2f]) vs 차도 시단 x0=%.2f → 이격 %.2f m"
          % (bad, rd["y1"], x_edge, x_edge - corr / abs(st_),
             x_edge + corr / abs(st_), rd["x0"],
             rd["x0"] - (x_edge + corr / abs(st_))))
    # ② 특색(드레인 가시부 + 맨홀) 시선 차단
    #    드레인 가시부 = |t| ≤ 9.0 (t > 9.06 부터는 옹벽 뒤 — 의도된 은폐이자
    #    geocheck ①에서 이미 프레임 밖으로 확인된 구간).
    pts = []
    for k in range(73):
        t = -9.0 + 18.0 * k / 72.0
        pts.append((px + t * ct, py + t * st_, 0.0))
    for md in PARAMS["manholes"]:
        pts.append((md["cx"], md["cy"], 0.0))
        for a in range(8):
            r = math.radians(45.0 * a)
            pts.append((md["cx"] + 0.35 * math.cos(r),
                        md["cy"] + 0.35 * math.sin(r), 0.0))
    blk = 0
    for vn, v in sorted(views.items()):
        eye = tuple(float(c) for c in v["eye"])
        vis = [p for p in pts if _in_frame(eye, v["tgt"], p)]
        if not vis:
            continue
        for nm, xa, xb, ya, yb, zt in boxes:
            bmin = (xa + 0.01, ya + 0.01, 0.01)
            bmax = (xb - 0.01, yb - 0.01, zt - 0.01)
            if bmax[0] <= bmin[0] or bmax[1] <= bmin[1] or bmax[2] <= bmin[2]:
                continue
            n_hit = sum(1 for p in vis if _seg_hits_box(eye, p, bmin, bmax))
            if n_hit:
                print("  ② %-20s ★특색 시선 차단★ %s (%d/%d 프레임내 샘플)"
                      % (vn, nm, n_hit, len(vis)))
                blk += 1
    print("  ② 특색 시선 차단(프레임 내 샘플 한정): %s"
          % ("0건 합격" if blk == 0 else "%d건 검토" % blk))
    # ③ 카메라 매몰
    m, hit, worst = 0.35, 0, (None, 1e9)
    for vn, v in sorted(views.items()):
        ex_, ey_, ez_ = v["eye"]
        for nm, xa, xb, ya, yb, zt in boxes:
            if (xa - m <= ex_ <= xb + m and ya - m <= ey_ <= yb + m
                    and -m <= ez_ <= zt + m):
                print("  ③ %-20s ★매몰★ %s" % (vn, nm))
                hit += 1
            dd = max(xa - ex_, ex_ - xb, ya - ey_, ey_ - yb, 0.0)
            if dd < worst[1]:
                worst = ("%s vs %s" % (vn, nm), dd)
    print("  ③ 카메라 매몰: %s (최근접 수평 %s = %.2f m)"
          % ("0건 합격" if hit == 0 else "%d건 불합격" % hit,
             worst[0], worst[1]))
    # ④ 차도 −X 시단(x = road.x0) 프레임인 — 보이면 '도로가 허공에서 시작'
    hfov, vfov = 60.0, 36.0
    edge = [(rd["x0"], rd["y0"] + (rd["y1"] - rd["y0"]) * k / 20.0, 0.0)
            for k in range(21)]
    fin, worst4 = 0, (None, -1e9)
    for vn, v in sorted(views.items()):
        ex_, ey_, ez_ = v["eye"]
        vyaw = math.degrees(math.atan2(v["tgt"][1] - ey_, v["tgt"][0] - ex_))
        mrel = 1e9
        for qx, qy, _ in edge:
            rel = (math.degrees(math.atan2(qy - ey_, qx - ex_)) - vyaw
                   + 540.0) % 360.0 - 180.0
            mrel = min(mrel, abs(rel))
        if mrel < hfov / 2.0:
            print("  ④ %-20s ★차도 시단 프레임인★ (최소 이각 %.1f°)" % (vn, mrel))
            fin += 1
        if mrel > worst4[1] or worst4[0] is None:
            pass
        if worst4[0] is None or mrel < worst4[1]:
            worst4 = (vn, mrel)
    print("  ④ 차도 시단 프레임인: %s (최소 여유 %s = %.1f°, 한계 %.0f°)"
          % ("0건 합격" if fin == 0 else "%d건 불합격" % fin,
             worst4[0], worst4[1], hfov / 2.0))
    print("-" * 68)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]  ※ 이 씬은 GT = 전 픽셀 "낙차 없음" (hard negative)
 1. grating_close (PT)  — 슬롯이 검게 읽히되 **바닥판이 얕게 보이는가**
                           (뚫린 개구처럼 무한 암흑이면 과잉 — 얕은 암부가 목표)
 2. patch/manhole flush — 맨홀·프레임이 노면과 flush(단차·두께 그림자 부재)
 3. approach / h0.3_d2  — 저시점에서 그레이팅 암부가 "틈/낙차"로 혼동되는 강도
 4. 전 컷              — 그레이팅 끝단이 프레임에 들어오지 않는가(검산과 대조)
 5. 기하                — 줄눈이 드레인 위를 가로지르지 않는가, 슬랫 Z파이팅 없음
                           (줄눈0.0006<프레임0.0012<맨홀0.0020<보스0.0030,
                            차도판 0.0010 · 차도 도색 0.0026 는 별도 XY)
 6. 맥락(드레싱)        — 차도(아스팔트+연석+중앙 파선/가장자리 실선)·가로수 열·
                           자전거 거치대·안내 사인·배면 옹벽·차도 건너 가로벽으로
                           "여기는 차도 옆 도시 보도"가 읽히는가
 7. 신규 요소 무간섭    — 드레인·맨홀 시야(approach/grating_close/manhole_pair)를
                           가리지 않는가 (NEGOBS_GEOCHECK=1 의 ②③④ 와 대조)"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene25")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene25"

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
        M["pave"] = PBR(
            f"{ROOT}/Looks/Pave", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=mp["pave_tint"])
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"],
            tint=mp["wall_tint"])
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
        M["iron"] = PBR(f"{ROOT}/Looks/Iron", diffuse_color=mp["iron_color"],
                        metallic=mp["iron_metallic"],
                        roughness_const=mp["iron_rough"], specular_level=0.3)
        M["lid"] = PBR(f"{ROOT}/Looks/Lid", diffuse_color=mp["lid_color"],
                       metallic=mp["lid_metallic"],
                       roughness_const=mp["lid_rough"], specular_level=0.3)
        M["mframe"] = PBR(f"{ROOT}/Looks/MFrame",
                          diffuse_color=mp["frame_color"],
                          metallic=mp["frame_metallic"],
                          roughness_const=mp["frame_rough"])
        M["trough"] = PBR(f"{ROOT}/Looks/Trough",
                          diffuse_color=mp["trough_color"],
                          roughness_const=mp["trough_rough"], metallic=0.0)
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # ─ 맥락 드레싱 신규 ─
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["roadpaint"] = PBR(f"{ROOT}/Looks/RoadPaint",
                             diffuse_color=mp["roadpaint_color"],
                             roughness_const=mp["roadpaint_rough"], metallic=0.0)
        M["pit"] = PBR(f"{ROOT}/Looks/TreePit", diffuse_color=mp["pit_color"],
                       roughness_const=mp["pit_rough"], metallic=0.0)
        M["bollard_body"] = PBR(f"{ROOT}/Looks/BollardBody",
                                diffuse_color=mp["bollard_color"],
                                metallic=mp["bollard_metallic"],
                                roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        # [W2 §12.5 ③] 상수색 → **`tactile_yellow` 텍스처 배선**.
        #   현행 상수색은 법정 36점 돌기의 음영이 화면에 0 이라, 룩 OFF 에서도
        #   소판이 "저채도 얼룩"으로만 읽혔다. 텍스처는 이미 등록돼 있었는데
        #   쓰지 않고 있었다 `[실측 — scene_common.TEX["tactile"]]`.
        M["tactile"] = PBR(f"{ROOT}/Looks/Tactile",
                           sc.tex_path("tactile", "diff"),
                           sc.tex_path("tactile", "nor"),
                           None, 0.30,
                           roughness_const=mp["tactile_rough"])
        M["steel"] = PBR(f"{ROOT}/Looks/Steel", diffuse_color=mp["steel_color"],
                         metallic=mp["steel_metallic"],
                         roughness_const=mp["steel_rough"])
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
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=mp["sign_rough"])
        # 한글 안내 사인 패널 — uv_mode(메시 st 1:1 정합, build_sign 전용)
        M["sign_panel"] = PBR(f"{ROOT}/Looks/SignPanel",
                              sc.tex_path("sign_info", "diff"), uv_mode=True,
                              roughness_const=0.45)
        return M

    # -------------------------------------------------------------------
    # 보도 + 그레이팅 — 전부 rot_group(pivot, yaw) 로컬 좌표계에서 축정렬 조립
    #   개구는 만들지 않는다(GT 낙차 0). 보도 평판을 드레인 양측 2매로 나누고
    #   그 사이를 **암색 바닥판(z=−0.05)** 이 받친다 = 얕은 암부.
    #   동일평면 회피: 보도 안쪽면 ±0.205 는 프레임 안쪽면 ±0.200 보다 5mm 뒤,
    #   바닥판(±0.250)·프레임(±0.260)은 서로·보도와 솔리드 관입만 한다.
    # -------------------------------------------------------------------
    def build_pave_and_grating(M):
        d = PARAMS["drain"]
        px, py = float(d["pivot"][0]), float(d["pivot"][1])
        grp = sc.build_rot_group(stage, f"{ROOT}/Drain", (px, py),
                                 float(d["yaw"]))
        ph, pt = d["pave_half"], d["pave_thick"]
        x0, x1 = px - ph, px + ph
        inner = d["pave_inner"]
        # 보도 평판 2매 (드레인 남/북)
        for tag, ya, yb in (("S", -ph, -inner), ("N", inner, ph)):
            # [W2-0 · P-A] **BOX 호출 전에** 스킨 제외를 등록한다 — `add_box` 가
            #   그 자리에서 `_skin_wanted` 를 부르므로 사후 등록은 늦다.
            sc.skin_exclude(f"{grp}/Pave_{tag}")
            BOX(f"{grp}/Pave_{tag}",
                ((x0 + x1) / 2.0, (ya + yb) / 2.0, -pt / 2.0),
                (x1 - x0, yb - ya, pt), M["pave"], col=True)
        if not cfg["hazard_flush_grating"]:
            # 대조군: 드레인 없이 슬롯 폭까지 보도로 메움(민무늬 평지)
            sc.skin_exclude(f"{grp}/Pave_Fill")
            BOX(f"{grp}/Pave_Fill",
                ((x0 + x1) / 2.0, 0.0, -pt / 2.0 - 0.001),
                (x1 - x0, 2.0 * inner + 0.01, pt), M["pave"], col=True)
            return
        hl = d["half_len"]
        gx0, gx1 = px - hl, px + hl
        gxc = (gx0 + gx1) / 2.0
        # 트렌치 바닥판 (얕은 암부 — 실개구 아님)
        BOX(f"{grp}/TroughPlate",
            (gxc, 0.0, (d["plate_top"] + d["plate_bot"]) / 2.0),
            (gx1 - gx0, 2.0 * d["plate_half"], d["plate_top"] - d["plate_bot"]),
            M["trough"])
        # 프레임 레일 2줄 (상면 proud 0.002 — 보도 에지를 덮어 동일평면 제거)
        rw = d["rail_outer"] - d["slot_half"]
        for tag, sgn in (("S", -1.0), ("N", 1.0)):
            BOX(f"{grp}/Frame_{tag}",
                (gxc, sgn * (d["slot_half"] + rw / 2.0),
                 (d["rail_top"] + d["rail_bot"]) / 2.0),
                (gx1 - gx0, rw, d["rail_top"] - d["rail_bot"]), M["iron"])
        # 슬랫 열 (양끝은 프레임 레일 볼륨에 물림 — bar_ylen > 슬롯폭)
        n = int((gx1 - gx0) / d["pitch"])
        cz = d["bar_top"] - d["bar_h"] / 2.0
        for i in range(n):
            bx = gx0 + (i + 0.5) * d["pitch"]
            BOX(f"{grp}/Slat_{i}", (bx, 0.0, cz),
                (d["bar_t"], d["bar_ylen"], d["bar_h"]), M["iron"])
        print(f"[기하] 그레이팅 슬랫 {n}매 · 슬롯폭 "
              f"{d['pitch'] - d['bar_t']:.3f} m · 암부 깊이 "
              f"{d['bar_top'] - d['plate_top']:.3f} m")

    # -------------------------------------------------------------------
    # 줄눈 — 드레인 회랑에서 절단 (월드 축정렬)
    # -------------------------------------------------------------------
    def build_joints(M):
        j = PARAMS["joints"]
        px, py, ct, st, hl, wc = _drain_axis()
        active = cfg["hazard_flush_grating"]
        w, pr = j["width"], j["proud"]
        thk = pr + 0.006
        cz = pr - thk / 2.0
        n = int(round((j["y1"] - j["y0"]) / j["spacing"])) + 1
        for i in range(n):
            yy = j["y0"] + i * j["spacing"]
            if active and abs(st) > 1e-6:
                t = (yy - py) / st
                segs = _cut_span(j["x0"], j["x1"], px + t * ct,
                                 wc / abs(st), t, hl)
            else:
                segs = [(j["x0"], j["x1"])]
            for k, (a, b) in enumerate(segs):
                BOX(f"{ROOT}/JointX_{i}_{k}", ((a + b) / 2.0, yy, cz),
                    (b - a, w, thk), M["joint"])
        m = int(round((j["x1"] - j["x0"]) / j["spacing"])) + 1
        for i in range(m):
            xx = j["x0"] + i * j["spacing"]
            if active and abs(ct) > 1e-6:
                t = (xx - px) / ct
                segs = _cut_span(j["y0"], j["y1"], py + t * st,
                                 wc / abs(ct), t, hl)
            else:
                segs = [(j["y0"], j["y1"])]
            for k, (a, b) in enumerate(segs):
                BOX(f"{ROOT}/JointY_{i}_{k}", (xx, (a + b) / 2.0, cz),
                    (w, b - a, thk), M["joint"])

    # -------------------------------------------------------------------
    # 맨홀 — 동심 3단(프레임/뚜껑/중앙 보스), 전부 flush. 실개구 없음.
    # -------------------------------------------------------------------
    def build_manholes(M):
        mh = PARAMS["manhole"]
        for md in PARAMS["manholes"]:
            nm = md["name"]
            for tag, r, pr, mtl in (
                    ("Frame", mh["r_frame"], mh["proud_frame"], M["mframe"]),
                    ("Lid", mh["r_lid"], mh["proud_lid"], M["lid"]),
                    ("Boss", mh["r_boss"], mh["proud_boss"], M["lid"])):
                CYL(f"{ROOT}/Manhole_{nm}/{tag}",
                    (md["cx"], md["cy"], pr - mh["h"] / 2.0),
                    r, mh["h"], mtl)

    # -------------------------------------------------------------------
    # [W2] ground_kit — P3 sidewalk_block. 근경 창 맨홀 신설 + 볼라드 전면
    #   점자블록 띠(§12 등록 지점 "bollard"). 낙차 에지가 없는 씬이라
    #   GT-E1′/GT-E2 는 공허참이고, 판정은 프림 예산·알베도·B11 이 한다.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["ground"]
        gp = gk.plan_ground(
            "sidewalk_block", region=g["region"], z=0.0,
            gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=(),                     # hard negative — 낙차 에지 0
            dists=(2, 5, 10), scene="sceneN5",
            tactile=("bollard",),
            sites=dict(manhole=[tuple(g["manhole_w1"])],
                       gully=[tuple(p) for p in g["gullies"]],
                       tactile=dict(bollard=tuple(g["tactile_band"]))),
            seed=25)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(manhole=M["lid"], gully=M["iron"], gutter=M["mframe"],
                  joint=M["joint"], crack=M["joint"], patch=M["pave"],
                  patch_cut=M["joint"], weed=M["grass"], marking=M["roadpaint"],
                  stain_dirt=M["trough"], stain_gum=M["trough"],
                  trench=M["iron"], trench_frame=M["mframe"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] sceneN5 P3 · 프림 {res['prims']} · "
              f"산포 {res['instances']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # 차도 + 연석 — "이 평면은 보도다"를 확정짓는 최상위 맥락 단서.
    #   차도는 보도 평판(z=0) 위 proud 0.0010 의 flush 판, 연석은 그 사이의
    #   융기 스트립(z 0~0.16). **양측 지면이 모두 z≈0 이므로 실낙차 없음**
    #   = GT 불변(전 픽셀 "낙차 없음").
    # -------------------------------------------------------------------
    def build_roadway(M):
        rd = PARAMS["road"]
        sc.skin_exclude(f"{ROOT}/Roadway")     # [P-A] 차도 flush 도색 보존
        BOX(f"{ROOT}/Roadway",
            ((rd["x0"] + rd["x1"]) / 2.0, (rd["y0"] + rd["y1"]) / 2.0,
             rd["z_top"] - rd["thick"] / 2.0),
            (rd["x1"] - rd["x0"], rd["y1"] - rd["y0"], rd["thick"]),
            M["asphalt"], col=True)
        cb = PARAMS["curb"]
        for cd in PARAMS["curbs"]:
            BOX(f"{ROOT}/Curb_{cd['name']}",
                ((cb["x0"] + cb["x1"]) / 2.0,
                 (cd["y_out"] + cd["y_in"]) / 2.0, cb["h"] / 2.0),
                (cb["x1"] - cb["x0"], abs(cd["y_in"] - cd["y_out"]), cb["h"]),
                M["curb"], col=True)
        # 차도 도색 — 중앙 파선 + 양측 가장자리 실선
        dh = PARAMS["road_dash"]
        zc = rd["z_top"] + dh["proud"] - dh["thick"] / 2.0
        period = dh["dash"] + dh["gap"]
        n = int((dh["x1"] - dh["x0"]) / period) + 1
        for i in range(n):
            xa = dh["x0"] + i * period
            xb = min(xa + dh["dash"], dh["x1"])
            if xb - xa < 0.2:
                continue
            BOX(f"{ROOT}/RoadDash_{i}", ((xa + xb) / 2.0, dh["y"], zc),
                (xb - xa, dh["width"], dh["thick"]), M["roadpaint"])
        re = PARAMS["road_edge"]
        for ed in PARAMS["road_edges"]:
            BOX(f"{ROOT}/RoadEdge_{ed['name']}",
                ((re["x0"] + re["x1"]) / 2.0, ed["y"], zc),
                (re["x1"] - re["x0"], re["width"], dh["thick"]), M["roadpaint"])

    # -------------------------------------------------------------------
    # 드레싱 — 옹벽(보도 배면) + 가로수 열 + 자전거 거치대 + 안내 사인
    #          + 화단 + 볼라드 + 원경 건물(차도 건너 가로벽·스카이라인)
    #   ※ 신규 요소는 전부 그레이팅·맨홀 시야를 비켜 배치 — geocheck() ② 에서
    #     eye→특색(드레인 가시부·맨홀) 선분 vs AABB 관통을 전 뷰 검산한다.
    # -------------------------------------------------------------------
    def build_dressing(M):
        wl = PARAMS["wall"]
        cy = (wl["y0"] + wl["y1"]) / 2.0
        Ly = wl["y1"] - wl["y0"]
        for tag, (a, b) in zip(("W", "E"), wall_segments()):
            BOX(f"{ROOT}/Wall_{tag}", ((a + b) / 2.0, cy, wl["h"] / 2.0),
                (b - a, Ly, wl["h"]), M["wall"], col=True)
            BOX(f"{ROOT}/WallCap_{tag}",
                ((a + b) / 2.0, cy, wl["h"] + wl["cap_h"] / 2.0),
                (b - a, Ly + 2.0 * wl["cap_over"], wl["cap_h"]), M["curb"])
        pl = PARAMS["planter"]
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for pname, px, py, pdef in planter_placements():
            sc.build_planter(
                stage, f"{ROOT}/Planter_{pname}", px, py,
                pdef["base_z"], M["curb"], M["grass"],
                tree_mtls=(tree_mtls if pdef.get("tree") else None),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"],
                grass_h=pl["grass_h"])
        # 가로수 열 — 수목보호판(flush 암색 박판) + 가로수. 시설물대 y=−7.30
        st = PARAMS["street_tree"]
        for td, tx in zip(PARAMS["street_trees"], street_tree_xs()):
            base = f"{ROOT}/StreetTree_{td['name']}"
            BOX(f"{base}/Pit", (tx, st["cy"],
                                st["pit_proud"] - st["pit_thick"] / 2.0),
                (st["pit"], st["pit"], st["pit_thick"]), M["pit"])
            sc.build_tree(stage, base, tx, st["cy"], 0.0, M["wood"],
                          M["canopy_a"], M["canopy_b"],
                          trunk_r=st["trunk_r"], trunk_h=st["trunk_h"])
        # 자전거 거치대 — U형 후프 3기(수직 2 + 수평 1)
        rk = PARAMS["rack"]
        for i in range(int(rk["count"])):
            cy = rk["cy0"] + i * rk["step"]
            for sgn, tag in ((-1.0, "A"), (1.0, "B")):
                CYL(f"{ROOT}/Rack_{i}/Leg_{tag}",
                    (rk["cx"] + sgn * rk["span"] / 2.0, cy, rk["h"] / 2.0),
                    rk["bar_r"], rk["h"], M["steel"])
            CYL(f"{ROOT}/Rack_{i}/Bar", (rk["cx"], cy, rk["h"]),
                rk["bar_r"], rk["span"], M["steel"], rotY=90.0)
        # 안내 사인 1본 — -X 를 바라봄. GT 규약상 '낙차 경고' 아닌 안내(info).
        es = PARAMS["entry_sign"]
        sc.build_sign(stage, f"{ROOT}/EntrySign", es["x"], es["y"], 0.0,
                      es["yaw"], M["sign_panel"], w=es["w"], h=es["h"],
                      pole_h=es["pole_h"], pole_r=es["pole_r"],
                      pole_mtl=M["steel"], back_mtl=M["sign"])
        # 볼라드 [v5.1 §2] — 보도 시설물대, 간격 1.4 m, 반사띠 + 점형블록(+Y)
        bo = PARAMS["bollards"]
        for i, (bx, by) in enumerate(bollard_points()):
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{i}", bx, by, 0.0,
                                 None, M["bollard_body"], M["bollard_band"],
                                 M["tactile"], front_dir=bo["front"],
                                 radius=bo["r"], height=bo["h"])
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_pave_and_grating(M)
    if cfg["cue_material_break"]:
        build_joints(M)
    if cfg["hazard_flush_grating"]:
        build_manholes(M)
    if cfg["cue_scene_dressing"]:
        build_roadway(M)                 # 차도+연석 = "보도" 확정 단서
        build_dressing(M)
    build_ground_kit(M)                  # [W2] 지면 요소 — 드레싱 뒤에 놓는다
                                         #   (산포는 ground_kit 요소 생성 후 호출)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneN5 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN5_{ts}.png")
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
        geocheck()                     # Isaac 부팅 없이 기하만 검산
    else:
        main()
