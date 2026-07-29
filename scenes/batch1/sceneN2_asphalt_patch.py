# -*- coding: utf-8 -*-
"""
sceneN2_asphalt_patch.py — NegObs 인공씬 32호: 검은 아스팔트 패치 (Isaac Sim 4.5)

유형    : N2 Hard Negative — 평지 노면의 신설 아스팔트 패치 (GT = 전 픽셀 낙차 없음)
사양서  : Docs/nanobanana_batch1_geometry_map.md §D sceneN2_asphalt_patch
룩참조  : look_refs/n2_asphalt_patch.jpg (v2 재생성분)
공통    : scene_common.py (검증된 API 헬퍼) · scene16_canopy_shadow.py (골격)

위험 본질(반례): **낙차는 어디에도 없다.** 회색 풍화 노면 한복판에 크리스프 컷라인의
           직사각 신설 아스팔트 패치가 완전 flush로 깔려 있다. 신설 아스팔트는
           알베도 0.030 — 주변 콘크리트(0.42)의 1/14, 기존 아스팔트(0.16)의 1/5로
           **"뚫린 구멍"처럼 읽히는 것**이 이 씬의 특색이다. sceneD2(공사장
           1.5×2.0m 무방호 개구, 낙차 3.0m 양성)와 **검은 사각형 최강 혼동쌍**을
           이루도록, 동일 치수(1.5×2.0m)의 소형 패치를 카메라 전방 x 2.6~4.6m에
           같은 접근 구도(4m·h0.9)로 배치했다.
목표     : 평탄 콘크리트 에이프런 + 신설 패치 2매(대형 4×5 / 소형 1.5×2.0) +
           원경 구 아스팔트 차도·자갈 버지·건물을 조립, 렌더로 판정 (렌더 전용).
           GT 낙차 맵 = 전 픽셀 0.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneN2_asphalt_patch.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneN2_asphalt_patch.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneN2_asphalt_patch.py
도색·드레싱 검산:       NEGOBS_GEOCHECK=1 python3 sceneN2_asphalt_patch.py (Isaac 불요)

좌표계: Z-up, m, 진행축 +X. 낙차 없음 — 특색(소형 패치)이 x=2.6~4.6 구간.
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import batch1_common as bc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hard negative 씬이므로 hazard_* 는 낙차가 아니라
#     "씬 특색 요소(아스팔트 패치)" 토글. 해당 없는 cue 키는 False + 사유 주석.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_asphalt_patch": True,  # False → 패치·컷라인 제거(균일 노면 대조군)
    "cue_railing":        False,  # 낙차 없음 → 방호 난간 비관행. 키만 예약
    "cue_tactile":        False,  # 차량 동선 노면 → 점자블록 비관행. 키만 예약
    "cue_material_break": True,   # 컷라인 밝은 스트립 + 노면 줄눈. False → 경계
                                  #   강조 없는 더 어려운 반례(패치만 덩그러니)
    "cue_nosing":         False,  # 단이 없음 → 논슬립 띠 무의미. 키만 예약
    "cue_sign":           False,  # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,   # 차선 파선·볼라드·생울타리·원경 건물 일괄
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # ─ 노면 3대(전부 평탄, 개구 전무). 인접 평판은 z를 2mm씩 낮춰 동일평면 금지.
    apron=dict(x0=-70.0, x1=16.05, y0=-70.0, y1=70.0, z_top=0.0, thick=0.5),
    road=dict(x0=16.0, x1=30.05, y0=-70.0, y1=70.0, z_top=-0.002, thick=0.5),
    verge=dict(x0=30.0, x1=70.0, y0=-70.0, y1=70.0, z_top=-0.004, thick=0.5),

    # ─ 신설 아스팔트 패치 (완전 flush: proud 0.002 ≤ 0.002 규약)
    #   small : 맵 §D 대형과 별개 — sceneD2 개구 1.5×2.0m 와 동일 치수·구도
    #   main  : 맵 §D 판독치 4(Y)×5(X) m. -Y로 비켜 배치(소형과 시각적 병합 방지)
    patches=[
        dict(name="small", x0=2.6, x1=4.6, y0=-0.75, y1=0.75),   # 2.0 × 1.5
        dict(name="main",  x0=7.0, x1=12.0, y0=-4.8, y1=-0.8),   # 5.0 × 4.0
    ],
    patch=dict(proud=0.0020, thick=0.05,
               cut_w=0.08, cut_proud=0.0012, cut_thick=0.02),
    # ─ 노면 줄눈(콘크리트 슬래브 경계) — 최하층 proud
    joints=dict(spacing=4.0, width=0.03, proud=0.0006,
                x0=-20.0, x1=16.0, y0=-20.0, y1=20.0),
    # ─ 원경 차도 차선 파선 (도로가 Y방향 주행 → 파선도 Y로 나열)
    lane=dict(x=23.0, y0=-30.0, y1=30.0, dash=3.0, gap=6.0,
              width=0.12, proud=0.002, thick=0.01),
    # ─ 차도 가장자리 실선 2줄(파선과 함께 "2차로 도로" 확정). 파선과 동일 층.
    edge_lines=[dict(name="W", x=17.0), dict(name="E", x=29.2)],
    edge_line=dict(y0=-30.0, y1=30.0, width=0.15),

    # ═══ 노면 도색 문양 (cue_scene_dressing) — "주차장 → 차도" 용도 확정 ═══
    #  ★ 재포장 리얼리즘 [사용자 지시]: 구획선은 패치(+컷라인 폭 clear)와 겹치는
    #    구간이 **삭제**된다 → 선이 패치 아래로 사라졌다가 반대편에서 이어진다.
    #    paint_line_segments() 가 PARAMS["patches"] 로부터 자동 절단.
    #  ★ z 층서: 줄눈 0.0006 < 도색 0.0010 < 컷라인 0.0012 < 패치 0.0020
    #            < 맨홀 프레임 0.0026 < 뚜껑 0.0032 < 보스 0.0038 (동일평면 없음)
    marking=dict(proud=0.0010, thick=0.012, clear=0.030,
                 tile=0.90, gap_prob=0.10, seed=20260727),
    #   근열/원열 주차 구획선(진행축 X를 따라 뻗음). 소형 패치가 y=0 선을,
    #   대형 패치가 원열 y=−2.5 선을 끊는다.
    stall=dict(ys=(-5.0, -2.5, 0.0, 2.5, 5.0), width=0.12,
               near=(0.4, 5.6), far=(9.0, 13.6)),
    #   구획 끝선(폐단부) — 각 열의 +X 끝을 가로지르는 선
    stall_heads=[dict(name="N", x=5.6), dict(name="F", x=13.6)],
    stall_head=dict(y0=-5.0, y1=5.0, width=0.12),
    #   정지선(주차장 → 차도 진출부) + 통로 진행 화살표 1개(+Y 일방통행)
    stopline=dict(x=15.2, y0=-6.0, y1=6.0, width=0.45),
    arrow=dict(cx=7.3, cy=3.2, yaw=90.0, shaft_len=2.0, shaft_w=0.22,
               head_len=0.85, head_w=0.20, head_ang=32.0),
    #   소형 맨홀 1기(통로부, flush)
    manhole=dict(cx=6.3, cy=1.4, r_frame=0.36, r_lid=0.30, r_boss=0.08,
                 h=0.03, proud_frame=0.0026, proud_lid=0.0032,
                 proud_boss=0.0038),

    # ═══ 맥락 드레싱 — 연석·보도 경계 / 가로등 / 가로수 / 원경 스카이라인 ═══
    #  ★ GT 불변: 연석은 **평지 위에 솟은 z≥0 융기 스트립**(양측 지면 모두 z≈0)
    #    → 실낙차 아님. 보도 슬래브도 proud 0.003 의 flush 판.
    #  ★ 카메라 회랑: 전 뷰 eye 는 (x −6..−1.4, y 0) — 신규 입체물은 |y| ≥ 9.5
    #    또는 x ≥ 14.5 에만 둔다(매몰·폐색 원천 배제).
    curb=dict(x0=-30.0, x1=15.0, y=9.50, t=0.35, h=0.14),   # ±y 대칭 2본
    walk=dict(x0=-30.0, x1=15.0, y_in=9.85, y_out=14.0, z_top=0.0030),
    streetlights=[dict(name="A", cx=0.0, cy=11.6), dict(name="B", cx=-8.0, cy=11.6),
                  dict(name="C", cx=12.0, cy=-12.2)],
    streetlight=dict(pole_h=5.2, pole_r=0.075, arm_len=0.9, arm_r=0.04, head=0.26),
    planters=[dict(name="A", cx=4.0, cy=12.0), dict(name="B", cx=-4.0, cy=-12.0)],
    planter=dict(size=2.4, curb_h=0.42, curb_t=0.22, cap_over=0.05,
                 cap_h=0.05, grass_h=0.36),
    # ── 볼라드 [v5.1 §2 · ctx2] ───────────────────────────────────────────
    #   구(舊): y=8.5(=차도 한복판, 연석 y9.5 안쪽 1 m) · 간격 4.0 · h0.75 ·
    #   반사띠/점형블록 없음 → 위치·규격 모두 비현실.
    #   신(新): **보도-차도 접점 유지**하되 연석(y 9.50..9.85) **바깥쪽 보도 위**
    #   y=10.30 (연석 전면에서 0.45 m 이격 = 관행)으로 이설. 간격 1.5 m.
    #   점형블록은 **보도측(+Y)** 으로 flush (보행 유도 방향).
    #   base_z = walk.z_top(0.0030) — 보도판 위에 세운다.
    #   ★ 카메라 회랑 |y| ≥ 9.5 규약을 이제서야 충족(구 y=8.5는 위반이었다).
    bollards=dict(y=10.30, x0=2.0, x1=14.0, spacing=1.5, r=0.06, h=0.90,
                  front=(0.0, 1.0)),
    hedge=dict(x0=31.0, x1=32.2, y0=-26.0, y1=26.0, h=0.9),
    buildings=dict(
        # 원경 비스타 차단(+X 지평선): 파사드 -X평면
        C=dict(x0=40.0, x1=50.0, y0=-26.0, y1=26.0, h=11.0, floors=3,
               axis="x", facade_x=40.0, face_dir=-1.0, base_z=-0.004),
        # ─ 스카이라인(실루엣 단차): C 뒤 고층 + 측면 중층 ─
        T=dict(x0=52.0, x1=64.0, y0=-18.0, y1=12.0, h=30.0, floors=9,
               axis="x", facade_x=52.0, face_dir=-1.0, base_z=-0.004),
        E=dict(x0=42.0, x1=52.0, y0=28.0, y1=44.0, h=20.0, floors=6,
               axis="x", facade_x=42.0, face_dir=-1.0, base_z=-0.004),
        # ─ 보도 너머 가로 벽면(양측) : 파사드 y평면. x1=14.5 (차도 침범 금지) ─
        L=dict(x0=-24.0, x1=14.5, y0=15.0, y1=25.0, h=12.0, floors=4,
               axis="y", facade_y=15.0, face_dir=-1.0),
        R=dict(x0=-24.0, x1=14.5, y0=-25.0, y1=-15.0, h=12.0, floors=4,
               axis="y", facade_y=-15.0, face_dir=1.0),
    ),
    window=dict(w=1.4, h=1.7, inset=0.15, col_step=3.2, margin=2.5),

    material=dict(
        scale=dict(plaza_lower=0.9, plaza_light=1.0, gravel=0.6, grass=1.4,
                   brick_red=2.0),
        # ─ 노면: plaza_lower 원본 평균 sRGB 0.49(중성 회) + 풍화 틴트 → ~0.42
        apron_tint=(0.86, 0.86, 0.84),
        # ─ 신설 아스팔트: sRGB 지각 규약(0.02~0.06 대역)의 최암부.
        #   기존 asphalt 상수색 0.16(scene11/17) 대비 1/5 → "구멍처럼 보임"이 특색
        patch_color=(0.030, 0.030, 0.033), patch_rough=0.92,
        cut_color=(0.34, 0.33, 0.31), cut_rough=0.85,      # 컷라인 밝은 회색 립
        joint_color=(0.06, 0.06, 0.06), joint_rough=0.85,
        asphalt_color=(0.16, 0.16, 0.17), asphalt_rough=0.90,  # 구 아스팔트(표준)
        lane_color=(0.55, 0.55, 0.53), lane_rough=0.70,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.88, 0.86, 0.82), parapet_rough=0.6,
        hedge_tint=(0.35, 0.45, 0.28),
        # ─ 노면 도색: 마모 3톤(신설→퇴색). 콘크리트 노면(~0.42)보다 밝아야
        #   "백색 도색"으로 읽힌다. 퇴색톤은 노면과 거의 같아 결락처럼 보인다.
        paint_tints=((0.68, 0.67, 0.64), (0.56, 0.55, 0.53), (0.45, 0.45, 0.43)),
        paint_rough=0.72,
        # ─ 맨홀(주철) : sRGB 0.02~0.06 암색 규약
        iron_color=(0.048, 0.048, 0.050), iron_rough=0.60, iron_metallic=0.4,
        lid_color=(0.040, 0.040, 0.045), lid_rough=0.50, lid_metallic=0.6,
        # ─ 맥락 드레싱
        walk_tint=(0.90, 0.89, 0.86),
        curb_color=(0.72, 0.72, 0.69), curb_rough=0.6,
        post_color=(0.55, 0.55, 0.58), post_metallic=0.5, post_rough=0.5,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,
        grass_tint=(0.55, 0.68, 0.42),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # ─ 볼라드 v5.1: 스테인리스 몸통 + 상단 백색 반사띠(소면적) +
        #   전면 점형블록(황색). 반사띠는 본당 0.08 m² 라 "순백 대면적" 아님.
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
    # ─── SUN_AZ_OFFSET = 171.5 (v3 §A-7 표준 유지).
    #     태양 매핑: 월드 태양 az ≈ 33.5 + 171.5 = 205° → 카메라(+X 주시) 뒤 좌측.
    #     그림자 방위 az_s = 205 − 180 = 25° → 그림자가 +X(약간 +Y)로, 즉 물체
    #     뒤편(카메라 반대쪽)으로 떨어진다.
    #     ⇒ **정면광**이라 프레임 안으로 들어오는 긴 캐스트 섀도가 없다. 이 씬의
    #        판정 대상은 "재질 암부(패치)"이므로, 그림자 암부와 섞이면 반례
    #        해석이 오염된다 — 표준 방위를 그대로 쓰는 적극적 사유. (sceneN1이
    #        146.5로 그림자를 특색화한 것과 정반대 목적.)
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN2")

ASSET_ROLES = ["plaza_lower", "plaza_light", "gravel", "grass", "brick_red",
               "hdri", "mdl"]


# ===========================================================================
# [C2] 노면 도색 절단 — "재포장으로 구획선이 패치 아래로 사라진다"
#      (stage 불필요 · 순수 기하 → markcheck() 와 공용)
# ===========================================================================
def paint_line_segments(axis, fixed, a0, a1):
    """직선 도색 [a0,a1] 에서 패치(+컷라인 폭 + clear 여유) 구간을 제거.

    axis="x": 선이 X를 따라 뻗고 `fixed` 는 그 선의 y 좌표.
    axis="y": 선이 Y를 따라 뻗고 `fixed` 는 x 좌표.
    반환: [(a, b), ...] (길이 0.05 m 미만 조각은 버림).
    패치 밑은 신설 아스팔트로 덮여 도색이 존재하지 않으므로, 선은 패치 한쪽에서
    끊기고 반대편에서 다시 나타난다 = 재포장 리얼리즘(사용자 지시).
    동시에 도색(proud 0.0010)과 컷라인(0.0012)의 XY 겹침도 원천 제거된다.
    """
    m = float(PARAMS["patch"]["cut_w"]) + float(PARAMS["marking"]["clear"])
    segs = [(float(a0), float(a1))]
    for pd in PARAMS["patches"]:
        if axis == "x":
            if not (pd["y0"] - m <= fixed <= pd["y1"] + m):
                continue
            ca, cb = pd["x0"] - m, pd["x1"] + m
        else:
            if not (pd["x0"] - m <= fixed <= pd["x1"] + m):
                continue
            ca, cb = pd["y0"] - m, pd["y1"] + m
        nxt = []
        for a, b in segs:
            if cb <= a or ca >= b:
                nxt.append((a, b))
                continue
            if ca > a:
                nxt.append((a, ca))
            if cb < b:
                nxt.append((cb, b))
        segs = nxt
    return [(a, b) for a, b in segs if b - a > 0.05]


def build_views():
    """카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷."""
    views = sc.grid_views(0.0)
    # approach: 에이프런에서 패치로 보행 접근 (두 패치가 함께 읽히는 인상)
    views["approach"] = dict(eye=[-6.0, 0.0, 1.6], tgt=[5.0, 0.0, 0.1])
    # patch_confusion: **sceneD2(개구부)와 동일 구도** — 소형 패치 근단
    #   x=2.6 에서 4m 후퇴·h0.9. 두 씬 캡처를 나란히 놓고 혼동쌍 판정.
    views["patch_confusion"] = dict(eye=[-1.4, 0.0, 0.9], tgt=[4.6, 0.0, 0.05])
    # patch_grazing: 저시점 grazing — flush 여부(두께 그림자 부재) 검증
    views["patch_grazing"] = dict(eye=[-3.0, 0.0, 0.35], tgt=[6.0, 0.0, 0.1])
    # beauty_oblique: 사선 부감 — 패치가 평면임을 드러내는 대조 컷
    views["beauty_oblique"] = dict(eye=[-5.0, -4.5, 2.4], tgt=[6.0, -1.0, -0.2])
    return views


# ===========================================================================
# [C3b] 배치 비정형 (v5.1 §3) — 결정적 지터. 빌더·검산이 같은 함수를 쓴다.
#   제외 대상(기능 반복열이라 정렬이 현실): 주차 구획선·차선 파선·줄눈·정지선.
# ===========================================================================
def streetlight_placements():
    """[(name, x, y, yaw), ...] — 가로등 위치 ±0.2 m · 암 방위 ±3~8° 지터."""
    out = []
    for s in PARAMS["streetlights"]:
        dx, dy = bc.jit_pos(s["cx"], s["cy"], "slN2", amp=0.20)
        yaw = bc.jit_yaw(s["cx"], s["cy"], "slN2", lo=3.0, hi=8.0)
        out.append((s["name"], s["cx"] + dx, s["cy"] + dy, yaw))
    return out


def planter_placements():
    """[(name, x, y), ...] — 가로수 화단 위치 ±0.15 m 지터(축평행 유지: 연석)."""
    out = []
    for p in PARAMS["planters"]:
        dx, dy = bc.jit_pos(p["cx"], p["cy"], "plN2", amp=0.15)
        out.append((p["name"], p["cx"] + dx, p["cy"] + dy))
    return out


def bollard_points():
    """[v5.1 §2] 보도-차도 접점 볼라드 열 중심 [(x, y), ...] (간격 1.5 m)."""
    bo = PARAMS["bollards"]
    return bc.bollard_line(bo["x0"], bo["y"], bo["x1"], bo["y"],
                           spacing=bo["spacing"])


# ===========================================================================
# [C4] 검산 (Isaac 불요) — NEGOBS_GEOCHECK=1 python3 sceneN2_asphalt_patch.py
#   ① 도색 절단표: 구획선이 패치에서 끊기고 반대편에서 이어지는가
#   ② 카메라 매몰: 전 뷰 eye 가 신규 입체물 AABB(여유 0.35) 밖인가
#   ③ 특색 폐색: 신규 입체물이 카메라–패치 사이 시야뿔(±30°)에 없는가
# ===========================================================================
def dressing_aabbs():
    """신규/기존 **입체** 드레싱의 (name, xa, xb, ya, yb, z_top). 도색·맨홀 등
    flush 요소는 폐색·매몰과 무관하므로 제외한다."""
    out = []
    cb, wk = PARAMS["curb"], PARAMS["walk"]
    for sgn, tag in ((1.0, "N"), (-1.0, "S")):
        y0 = sgn * cb["y"]
        y1 = sgn * (cb["y"] + cb["t"])
        out.append((f"Curb_{tag}", cb["x0"], cb["x1"], min(y0, y1),
                    max(y0, y1), cb["h"]))
        w0, w1 = sgn * wk["y_in"], sgn * wk["y_out"]
        out.append((f"Walk_{tag}", wk["x0"], wk["x1"], min(w0, w1),
                    max(w0, w1), wk["z_top"]))
    sl = PARAMS["streetlight"]
    ex = sl["arm_len"] + sl["head"] / 2.0
    ey = ex * math.sin(math.radians(8.0)) + sl["head"] / 2.0   # yaw 지터 상계
    for name, sx, sy, _yaw in streetlight_placements():
        out.append((f"Streetlight_{name}", sx - ex, sx + ex,
                    sy - ey, sy + ey, sl["pole_h"]))
    pl = PARAMS["planter"]
    ph = pl["size"] / 2.0
    top_tree = PARAMS["walk"]["z_top"] + pl["grass_h"] + 2.2 + 0.85 + 0.24
    for name, px, py in planter_placements():
        out.append((f"Planter_{name}", px - ph, px + ph,
                    py - ph, py + ph, top_tree))
    bo = PARAMS["bollards"]
    for i, (bx, by) in enumerate(bollard_points()):
        out.extend(bc.bollard_v51_aabbs(
            f"Bollard_{i}", bx, by, PARAMS["walk"]["z_top"],
            front_dir=bo["front"], radius=bo["r"], height=bo["h"]))
    hg = PARAMS["hedge"]
    out.append(("Hedge", hg["x0"], hg["x1"], hg["y0"], hg["y1"], hg["h"]))
    for k, bd in PARAMS["buildings"].items():
        out.append((f"Building_{k}", bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                    bd["h"] + 0.5))
    return out


def geocheck():
    print("=" * 72)
    print("sceneN2 검산 ① 노면 도색 절단 (패치가 구획선을 끊는가)")
    m = float(PARAMS["patch"]["cut_w"]) + float(PARAMS["marking"]["clear"])
    print("  절단 여유 m = cut_w %.3f + clear %.3f = %.3f"
          % (PARAMS["patch"]["cut_w"], PARAMS["marking"]["clear"], m))
    for pd in PARAMS["patches"]:
        print("  패치 %-6s x[%.2f, %.2f] y[%.2f, %.2f]"
              % (pd["name"], pd["x0"], pd["x1"], pd["y0"], pd["y1"]))
    st = PARAMS["stall"]
    n_cut = 0
    for ri, (rx0, rx1) in (("근열", st["near"]), ("원열", st["far"])):
        for yy in st["ys"]:
            segs = paint_line_segments("x", yy, rx0, rx1)
            cut = len(segs) != 1 or abs(segs[0][0] - rx0) > 1e-9 \
                or abs(segs[0][1] - rx1) > 1e-9
            n_cut += 1 if cut else 0
            print("  %s y=%+5.2f  x[%.2f,%.2f] → %s%s"
                  % (ri, yy, rx0, rx1,
                     " ".join("(%.2f..%.2f)" % s for s in segs),
                     "   ★패치가 절단★" if cut else ""))
    print("  절단된 구획선 %d개 (근열 y=0.00 / 원열 y=−2.50 이 기대값)" % n_cut)
    print("  z 층서: 줄눈 %.4f < 도색 %.4f < 컷라인 %.4f < 패치 %.4f "
          "< 맨홀 %.4f/%.4f/%.4f"
          % (PARAMS["joints"]["proud"], PARAMS["marking"]["proud"],
             PARAMS["patch"]["cut_proud"], PARAMS["patch"]["proud"],
             PARAMS["manhole"]["proud_frame"], PARAMS["manhole"]["proud_lid"],
             PARAMS["manhole"]["proud_boss"]))
    boxes = dressing_aabbs()
    views = build_views()
    print("sceneN2 검산 ② 카메라 매몰 (여유 0.35 m)")
    mm, hit, worst = 0.35, 0, (None, 1e9)
    for vn, v in sorted(views.items()):
        ex_, ey_, ez_ = v["eye"]
        for nm, xa, xb, ya, yb, zt in boxes:
            if (xa - mm <= ex_ <= xb + mm and ya - mm <= ey_ <= yb + mm
                    and -mm <= ez_ <= zt + mm):
                print("  %-20s ★매몰★ %s" % (vn, nm))
                hit += 1
            d = max(xa - ex_, ex_ - xb, ya - ey_, ey_ - yb, 0.0)
            if d < worst[1]:
                worst = ("%s vs %s" % (vn, nm), d)
    print("  최근접(수평) %s = %.2f m → %s"
          % (worst[0], worst[1], "합격" if hit == 0 else "불합격"))
    print("sceneN2 검산 ③ 특색(패치) 폐색 — 방위구간 중첩 × 패치보다 근접")
    #   폐색 성립 조건 = ①물체의 수평 방위구간이 패치의 방위구간과 겹치고
    #   ②물체가 패치보다 앞에 있을 것. (지면 위 물체이므로 방위가 안 겹치면
    #    화면상 좌우로 비켜나 패치를 가릴 수 없다.)
    def _bearing_span(ex_, ey_, vyaw, corners):
        rels = []
        for cx_, cy_ in corners:
            rels.append((math.degrees(math.atan2(cy_ - ey_, cx_ - ex_))
                         - vyaw + 540.0) % 360.0 - 180.0)
        lo, hi = min(rels), max(rels)
        if hi - lo > 180.0:                 # 카메라를 감싸는 판(보도·연석 등)
            return -180.0, 180.0
        return lo, hi

    bad = 0
    for vn, v in sorted(views.items()):
        ex_, ey_ = v["eye"][0], v["eye"][1]
        vyaw = math.degrees(math.atan2(v["tgt"][1] - ey_, v["tgt"][0] - ex_))
        pc = [(px, py) for pd in PARAMS["patches"]
              for px in (pd["x0"], pd["x1"]) for py in (pd["y0"], pd["y1"])]
        plo, phi = _bearing_span(ex_, ey_, vyaw, pc)
        d_far = max(math.hypot(px - ex_, py - ey_) for px, py in pc)
        for nm, xa, xb, ya, yb, zt in boxes:
            if zt < 0.05:                   # flush 판(보도 슬래브)은 폐색 불가
                continue
            cor = [(cx_, cy_) for cx_ in (xa, xb) for cy_ in (ya, yb)]
            olo, ohi = _bearing_span(ex_, ey_, vyaw, cor)
            d_min = min(math.hypot(cx_ - ex_, cy_ - ey_) for cx_, cy_ in cor)
            if ohi < plo or olo > phi:      # 방위 비중첩 → 좌우로 비켜남
                continue
            if d_min < d_far:
                print("  %-20s ★폐색 위험★ %s (방위 %.1f..%.1f vs 패치 %.1f..%.1f,"
                      " 거리 %.1f < %.1f)"
                      % (vn, nm, olo, ohi, plo, phi, d_min, d_far))
                bad += 1
    print("  판정 ③: %s" % ("전 뷰 무폐색 (합격)" if bad == 0
                            else "%d건 (검토 필요)" % bad))
    print("=" * 72)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]  ※ 이 씬은 GT = 전 픽셀 "낙차 없음" (hard negative)
 1. patch_confusion (PT) — 소형 패치(1.5×2.0)가 sceneD2 개구부처럼 "구멍"으로
                            읽히는가 = 혼동쌍 성립 여부 [1순위]
 2. approach / h0.9_d5   — 대형 패치 컷라인이 크리스프한가, 입자 톤이 신설인가
 3. patch_grazing        — 완전 flush(proud 0.002): 패치 두께 그림자·단차 부재
 4. 톤 서열              — 콘크리트(~0.42) ≫ 구 아스팔트(0.16) ≫ 패치(0.030)
 5. 기하                 — 줄눈(0.0006)<도색(0.0010)<컷라인(0.0012)<패치(0.0020)
                            <맨홀(0.0026/32/38) 5층 Z분리, 평판 겹침 없음
 6. 노면 문양            — 주차 구획선이 **패치 아래로 사라졌다 반대편에서
                            이어지는가**(근열 y=0 / 원열 y=−2.5). 마모 3톤·
                            10% 결락이 도색으로 읽히는가
 7. 맥락(드레싱)         — 연석·보도·가로등·가로수·정지선·차도 실선/파선으로
                            "주차장 → 차도"가 읽히는가 (NEGOBS_GEOCHECK=1 대조)"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene32")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene32"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    def SLAB(path, p, mtl, col=True):
        """z_top 상면·thick 두께의 축정렬 노면 평판."""
        return BOX(path,
                   ((p["x0"] + p["x1"]) / 2.0, (p["y0"] + p["y1"]) / 2.0,
                    p["z_top"] - p["thick"] / 2.0),
                   (p["x1"] - p["x0"], p["y1"] - p["y0"], p["thick"]),
                   mtl, col=col)

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["apron"] = PBR(
            f"{ROOT}/Looks/Apron", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"], tint=mp["apron_tint"])
        M["gravel"] = PBR(
            f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            sca["gravel"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["patch"] = PBR(f"{ROOT}/Looks/Patch",
                         diffuse_color=mp["patch_color"],
                         roughness_const=mp["patch_rough"], metallic=0.0)
        M["cut"] = PBR(f"{ROOT}/Looks/CutLine",
                       diffuse_color=mp["cut_color"],
                       roughness_const=mp["cut_rough"], metallic=0.0)
        M["joint"] = PBR(f"{ROOT}/Looks/Joint",
                         diffuse_color=mp["joint_color"],
                         roughness_const=mp["joint_rough"], metallic=0.0)
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["lane"] = PBR(f"{ROOT}/Looks/Lane", diffuse_color=mp["lane_color"],
                        roughness_const=mp["lane_rough"], metallic=0.0)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # ─ 노면 도색 3톤(마모) ─
        M["paint"] = []
        for i, t in enumerate(mp["paint_tints"]):
            M["paint"].append(PBR(f"{ROOT}/Looks/Paint_{i}", diffuse_color=t,
                                  roughness_const=mp["paint_rough"],
                                  metallic=0.0))
        M["iron"] = PBR(f"{ROOT}/Looks/Iron", diffuse_color=mp["iron_color"],
                        metallic=mp["iron_metallic"],
                        roughness_const=mp["iron_rough"], specular_level=0.3)
        M["lid"] = PBR(f"{ROOT}/Looks/Lid", diffuse_color=mp["lid_color"],
                       metallic=mp["lid_metallic"],
                       roughness_const=mp["lid_rough"], specular_level=0.3)
        # ─ 맥락 드레싱 ─
        M["walk"] = PBR(
            f"{ROOT}/Looks/Walk", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=mp["walk_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
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
        # ─ 볼라드 v5.1 (몸통 / 반사띠 / 전면 점형블록) ─
        M["bollard_body"] = PBR(f"{ROOT}/Looks/BollardBody",
                                diffuse_color=mp["bollard_color"],
                                metallic=mp["bollard_metallic"],
                                roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots actually shade.
        M["tactile"] = bc.tactile_mtl(stage, f"{ROOT}/Looks/Tactile")
        return M

    # -------------------------------------------------------------------
    # 노면 — 에이프런 / 구 아스팔트 차도 / 자갈 버지 (전부 평탄, 개구 전무)
    #   인접 평판은 X로 0.05 겹치되 z_top 을 2mm씩 낮춰 동일평면·틈 동시 회피.
    # -------------------------------------------------------------------
    def build_ground(M):
        SLAB(f"{ROOT}/Apron", PARAMS["apron"], M["apron"])
        SLAB(f"{ROOT}/Road", PARAMS["road"], M["asphalt"])
        SLAB(f"{ROOT}/Verge", PARAMS["verge"], M["gravel"])

    def build_joints(M):
        """에이프런 슬래브 줄눈 — 최하층(proud 0.0006). 패치 아래로 들어가면
        패치 박판(두께 0.05) 볼륨에 완전히 포함되어 자연히 은폐된다."""
        j = PARAMS["joints"]
        w, pr = j["width"], j["proud"]
        thk = pr + 0.006
        cz = PARAMS["apron"]["z_top"] + pr - thk / 2.0
        Lx = j["x1"] - j["x0"]
        Ly = j["y1"] - j["y0"]
        n = int(round(Ly / j["spacing"])) + 1
        for i in range(n):
            yy = j["y0"] + i * j["spacing"]
            BOX(f"{ROOT}/JointX_{i}", ((j["x0"] + j["x1"]) / 2.0, yy, cz),
                (Lx, w, thk), M["joint"])
        m = int(round(Lx / j["spacing"])) + 1
        for i in range(m):
            xx = j["x0"] + i * j["spacing"]
            BOX(f"{ROOT}/JointY_{i}", (xx, (j["y0"] + j["y1"]) / 2.0, cz),
                (w, Ly, thk), M["joint"])

    # -------------------------------------------------------------------
    # 신설 아스팔트 패치 + 컷라인 (특색 — GT는 여전히 "낙차 없음")
    # -------------------------------------------------------------------
    def build_patches(M):
        pc = PARAMS["patch"]
        for pd in PARAMS["patches"]:
            nm = pd["name"]
            x0, x1, y0, y1 = pd["x0"], pd["x1"], pd["y0"], pd["y1"]
            z_hi = PARAMS["apron"]["z_top"] + pc["proud"]
            BOX(f"{ROOT}/Patch_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, z_hi - pc["thick"] / 2.0),
                (x1 - x0, y1 - y0, pc["thick"]), M["patch"])
            if not cfg["cue_material_break"]:
                continue
            # 컷라인: 패치 둘레 밖으로 cut_w 만큼 (패치와 XY 겹침 없음 + z도 분리)
            w = pc["cut_w"]
            zc = PARAMS["apron"]["z_top"] + pc["cut_proud"] - pc["cut_thick"] / 2.0
            strips = (
                ("S", (x0 + x1) / 2.0, y0 - w / 2.0, x1 - x0 + 2.0 * w, w),
                ("N", (x0 + x1) / 2.0, y1 + w / 2.0, x1 - x0 + 2.0 * w, w),
                ("W", x0 - w / 2.0, (y0 + y1) / 2.0, w, y1 - y0),
                ("E", x1 + w / 2.0, (y0 + y1) / 2.0, w, y1 - y0),
            )
            for tag, cx, cy, sx, sy in strips:
                BOX(f"{ROOT}/CutLine_{nm}_{tag}", (cx, cy, zc),
                    (sx, sy, pc["cut_thick"]), M["cut"])

    # -------------------------------------------------------------------
    # 노면 도색 문양 — 주차 구획선(마모·결락) + 정지선 + 통로 화살표 + 맨홀
    #   ★ 구획선은 paint_line_segments() 로 패치 구간이 잘려 나간다:
    #     "선이 패치 아래로 사라졌다가 반대편에서 이어짐"(재포장 리얼리즘).
    #   ★ 마모 표현: 0.9 m 타일 분할 → 3톤 랜덤 틴트 + 10% 결락(seed 고정).
    #     세그먼트의 첫/끝 타일은 결락시키지 않아 선의 시작·끝은 항상 읽힌다.
    # -------------------------------------------------------------------
    def build_markings(M):
        mk = PARAMS["marking"]
        rng = random.Random(int(mk["seed"]))
        z_top = PARAMS["apron"]["z_top"] + mk["proud"]
        zc = z_top - mk["thick"] / 2.0
        n_tile = [0]

        def paint_run(tag, axis, fixed, a0, a1, width, wear=True):
            """[a0,a1] 을 패치로 절단한 뒤 타일 분할해 도색 박판을 깐다."""
            for si, (a, b) in enumerate(paint_line_segments(axis, fixed, a0, a1)):
                nt = max(1, int(round((b - a) / mk["tile"])))
                for i in range(nt):
                    ta = a + (b - a) * i / nt
                    tb = a + (b - a) * (i + 1) / nt
                    if wear and 0 < i < nt - 1 and rng.random() < mk["gap_prob"]:
                        continue                    # 결락(마모로 지워진 구간)
                    mtl = M["paint"][rng.randrange(len(M["paint"]))] if wear \
                        else M["paint"][0]
                    if axis == "x":
                        c, s = ((ta + tb) / 2.0, fixed), (tb - ta, width)
                    else:
                        c, s = (fixed, (ta + tb) / 2.0), (width, tb - ta)
                    BOX(f"{ROOT}/Mark/{tag}_{si}_{i}", (c[0], c[1], zc),
                        (s[0], s[1], mk["thick"]), mtl)
                    n_tile[0] += 1

        st = PARAMS["stall"]
        for ri, (rx0, rx1) in (("N", st["near"]), ("F", st["far"])):
            for yi, yy in enumerate(st["ys"]):
                paint_run(f"Stall{ri}_{yi}", "x", yy, rx0, rx1, st["width"])
        sh = PARAMS["stall_head"]
        for hd in PARAMS["stall_heads"]:
            paint_run(f"StallHead_{hd['name']}", "y", hd["x"], sh["y0"],
                      sh["y1"], sh["width"])
        sl = PARAMS["stopline"]
        paint_run("StopLine", "y", sl["x"], sl["y0"], sl["y1"], sl["width"],
                  wear=False)
        # 차도 가장자리 실선(원경·연속 — 타일 분할 불요)
        el = PARAMS["edge_line"]
        zr = PARAMS["road"]["z_top"] + PARAMS["lane"]["proud"] \
            - PARAMS["lane"]["thick"] / 2.0
        for ed in PARAMS["edge_lines"]:
            BOX(f"{ROOT}/Mark/Edge_{ed['name']}",
                (ed["x"], (el["y0"] + el["y1"]) / 2.0, zr),
                (el["width"], el["y1"] - el["y0"], PARAMS["lane"]["thick"]),
                M["lane"])
        # 통로 진행 화살표(+Y 일방통행) — 축(1) + 화살머리 사선 2 (총 3 프림)
        ar = PARAMS["arrow"]
        a = math.radians(float(ar["yaw"]))
        ux, uy = math.cos(a), math.sin(a)             # 화살 진행 방향
        BOX(f"{ROOT}/Mark/Arrow/Shaft",
            (ar["cx"], ar["cy"], zc),
            (ar["shaft_w"] if abs(ux) < 0.5 else ar["shaft_len"],
             ar["shaft_len"] if abs(ux) < 0.5 else ar["shaft_w"],
             mk["thick"]), M["paint"][0])
        tip = (ar["cx"] + ux * ar["shaft_len"] * 0.5,
               ar["cy"] + uy * ar["shaft_len"] * 0.5)
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            ang = ar["yaw"] + 180.0 - sgn * ar["head_ang"]
            ra = math.radians(ang)
            cxh = tip[0] + math.cos(ra) * ar["head_len"] / 2.0
            cyh = tip[1] + math.sin(ra) * ar["head_len"] / 2.0
            sc._oriented_box(stage, f"{ROOT}/Mark/Arrow/Head_{tag}",
                             (cxh, cyh, zc),
                             (ar["head_len"], ar["head_w"], mk["thick"]),
                             M["paint"][0], rotz=ang)
        # 소형 맨홀 1기(주철, flush). 3층 proud 는 도색·패치보다 위 [층서 참조]
        mh = PARAMS["manhole"]
        for tag, r, pr, mtl in (("Frame", mh["r_frame"], mh["proud_frame"], M["iron"]),
                                ("Lid", mh["r_lid"], mh["proud_lid"], M["lid"]),
                                ("Boss", mh["r_boss"], mh["proud_boss"], M["lid"])):
            CYL(f"{ROOT}/Manhole/{tag}",
                (mh["cx"], mh["cy"],
                 PARAMS["apron"]["z_top"] + pr - mh["h"] / 2.0),
                r, mh["h"], mtl)
        print(f"[도색] 구획·정지선 타일 {n_tile[0]}매 · 화살표 3 · 맨홀 3 · "
              f"차도 실선 {len(PARAMS['edge_lines'])}")

    # -------------------------------------------------------------------
    # 드레싱 — 차선 파선 + 연석·보도 + 가로등·가로수 + 볼라드 + 생울타리
    #          + 원경 건물(스카이라인 + 보도 너머 가로 벽면)
    # -------------------------------------------------------------------
    def build_dressing(M):
        ln = PARAMS["lane"]
        period = ln["dash"] + ln["gap"]
        n = int((ln["y1"] - ln["y0"]) / period) + 1
        zc = PARAMS["road"]["z_top"] + ln["proud"] - ln["thick"] / 2.0
        for i in range(n):
            ya = ln["y0"] + i * period
            yb = min(ya + ln["dash"], ln["y1"])
            if yb - ya < 0.2:
                continue
            BOX(f"{ROOT}/LaneDash_{i}", (ln["x"], (ya + yb) / 2.0, zc),
                (ln["width"], yb - ya, ln["thick"]), M["lane"])
        # 연석 + 보도 (±Y 대칭). 연석은 평지 위 융기 스트립 — 양측 지면 모두
        # z≈0 이므로 **낙차 아님**(GT 불변). 보도판은 proud 0.003 flush.
        cb, wk = PARAMS["curb"], PARAMS["walk"]
        for sgn, tag in ((1.0, "N"), (-1.0, "S")):
            BOX(f"{ROOT}/Curb_{tag}",
                ((cb["x0"] + cb["x1"]) / 2.0,
                 sgn * (cb["y"] + cb["t"] / 2.0), cb["h"] / 2.0),
                (cb["x1"] - cb["x0"], cb["t"], cb["h"]), M["curb"], col=True)
            BOX(f"{ROOT}/Walk_{tag}",
                ((wk["x0"] + wk["x1"]) / 2.0,
                 sgn * (wk["y_in"] + wk["y_out"]) / 2.0,
                 wk["z_top"] - 0.20),
                (wk["x1"] - wk["x0"], wk["y_out"] - wk["y_in"], 0.4),
                M["walk"], col=True)
        sl = PARAMS["streetlight"]
        for name, sx, sy, syaw in streetlight_placements():
            # v5.1 §3: 암 방위를 축평행에서 살짝 틀어 복제 인상 제거
            base = sc.build_rot_group(stage, f"{ROOT}/Streetlight_{name}",
                                      (sx, sy), syaw)
            CYL(f"{base}/Pole", (sx, sy, sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["post"], col=True)
            for sg, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (sx + sg * sl["arm_len"] / 2.0, sy,
                     sl["pole_h"] - 0.10), sl["arm_r"], sl["arm_len"],
                    M["post"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (sx + sg * sl["arm_len"], sy, sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        pl = PARAMS["planter"]
        for name, px, py in planter_placements():
            sc.build_planter(
                stage, f"{ROOT}/Planter_{name}", px, py,
                PARAMS["walk"]["z_top"], M["curb"], M["grass"],
                tree_mtls=(M["wood"], M["canopy_a"], M["canopy_b"]),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"],
                grass_h=pl["grass_h"])
        # 볼라드 [v5.1 §2] — 보도-차도 접점, 연석 바깥 0.45 m, 간격 1.5 m,
        #   상단 백색 반사띠 + 전면(보도측 +Y) 0.3 m 점형블록.
        bo = PARAMS["bollards"]
        for i, (bx, by) in enumerate(bollard_points()):
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{i}", bx, by,
                                 PARAMS["walk"]["z_top"], None,
                                 M["bollard_body"], M["bollard_band"],
                                 M["tactile"], front_dir=bo["front"],
                                 radius=bo["r"], height=bo["h"])
        hg = PARAMS["hedge"]
        sc.build_hedge(stage, f"{ROOT}/Hedge", hg["x0"], hg["y0"], hg["x1"],
                       hg["y1"], hg["h"], base_z=PARAMS["verge"]["z_top"],
                       tint=mp["hedge_tint"])
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_ground(M)
    if cfg["cue_material_break"]:
        build_joints(M)
    if cfg["hazard_asphalt_patch"]:
        build_patches(M)
    if cfg["cue_scene_dressing"]:
        build_markings(M)                # 노면 도색(패치가 구획선을 끊는다)
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneN2 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN2_{ts}.png")
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
        geocheck()                     # Isaac 부팅 없이 도색·드레싱만 검산
    else:
        main()
