# -*- coding: utf-8 -*-
"""
sceneD4_subway_platform.py — NegObs 인공씬 31호: D4 지하철 승강장 연단
(Isaac Sim 4.5) — **라이브러리 최초의 완전 실내 씬**

유형    : D4 비계단 낙차 (승강장 연단 → 궤도부, 낙차 1.15 m)
사양서  : Docs/nanobanana_batch1_geometry_map.md §C sceneD4_subway_platform
룩 레퍼: look_refs/d4_subway_platform.jpg
공통    : scene_common.py (검증 API) · scene16_canopy_shadow.py (표준 골격)
          · scene02_underpass.py (반실내 콘크리트) · scene06_spiral_towerstone.py
            (실내 암부 교훈의 진원지 — 아래 [조명 규약] 참조)

위험 본질: 승강장 보행면(z=0)이 궤도 골 위에서 아무 방호 없이 끊긴다. 연단
           수직면 1.15 m 아래는 암색 발라스트라 **낮은 시점(grazing)에서 궤도
           골이 통째로 은닉**되고, 승강장이 건너편까지 이어진 하나의 바닥처럼
           읽힌다. 유일한 단서는 연단 0.3 m 안쪽 황색 점자블록 2열 + 연단선.
GT       : 궤도 영역(y −2.0..+2.0) 낙차 1.15 m 양성. 승강장 상면 전역 = 낙차 없음.
           근거 = 승강장 추락(시나리오 조사 v1, 국내 통계).

──────────────────────────────────────────────────────────────────────────
[조명 규약 — 이 씬의 최대 난제. 반드시 읽을 것]
  이 씬은 **창·개구가 하나도 없는 완전 밀폐 셸**이다(승강장 슬래브+발라스트 바닥,
  측벽 2, 천장, 단부 벽 2, 터널 보어까지 back cap 으로 봉함). 따라서 DomeLight/
  HDRI 기여는 **구조적으로 0**이며, 씬의 광원은 천장 발광 패널 30장이 전부다.

  ★ **RT(RaytracedLighting) 단일바운스에서는 발광 기여가 거의 잡히지 않는다.**
    RT 렌더는 형상·배치 확인용으로만 쓰고, **밝기·암부 판정은 반드시
    PathTracing 8바운스(PARAMS["render"]["pt_max_bounces"]=8)** 로 한다.
    (scene06 교훈 7 — 실내 암부는 PT 로만 판정)

  ★ 밝기 튜닝은 PARAMS["panel"]["intensity"] 단일 노브. 시작값 1500.
    감독 스윕 권장(파일 수정 불필요):
      NEGOBS_PARAMS_OVERRIDE='{"panel":{"intensity":400}}'  python sceneD4_...py
      ... 400 / 800 / 1500 / 3000 을 PT 로 비교.
    scene06 감사 B-06-2 는 "실내 가독이면 150~300 이면 충분"이라 했으나 그것은
    **정오 태양이 노출을 지배하던 반옥외 씬**의 값이다. 본 씬은 직달·천공광이
    전무해 같은 표시 밝기를 얻으려면 한 자릿수 더 큰 값이 필요하다고 보고
    1500 에서 출발한다(패널 자체가 조명기구이므로 약한 백색 클리핑은 허용).

  ★ 궤도부 상대 암부(설계 근거): 패널 열은 승강장 상부(y=±5.0)에만 두고 궤도
    상공(|y|<2)에는 **한 장도 두지 않는다**. 승강장 보행면 바로 위 패널까지
    거리 3.35 m, 궤도면까지 최근접 거리 6.7 m·입사각 48° →
    직달 조도비 ≈ (0.669²/45.3)/(1/11.2) ≈ 0.26. 여기에 알베도가
    발라스트 0.05 vs 콘크리트 0.35 로 7배 차 → 궤도부 표시 휘도는 승강장의
    수 % 수준. 그러나 **0 은 아니다**: 백색 타일 벽·천장의 간접 바운스가
    궤도 골로 유입되므로 PT 에서 침목·레일 두부가 겨우 읽혀야 정상이다.
    (완전 흑이면 intensity 를 올리는 게 아니라 벽 알베도/바운스를 의심할 것)
──────────────────────────────────────────────────────────────────────────

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneD4_subway_platform.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt python sceneD4_...py
      ※ 실내 발광 단독 조명은 PT 수렴이 느리다. 노이즈가 남으면
        NEGOBS_WARMUP=900 (+ pt_total_spp 768) 로 올릴 것.
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneD4_subway_platform.py

좌표계: Z-up, m. **승강장 종주축 = +X**(카메라 진행축), 승강장 보행면 z=0.
        낙차 시작 모서리 = 연단선 **y=−2.0**(근측) / **y=+2.0**(건너편, 대칭).
        x=0 은 역 중앙 기준점(종주축이므로 x 원점에 위험 기하가 걸리지 않음).
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc
import batch1_common as bc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hazard_track 대신 관례상 hazard_stairs 키 유지
#     (기하 토글 유일 예외: False → 궤도 골을 z=0 으로 메워 평지화).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 궤도 골 매립(전면 z=0 평지, 낙차 0)
    "cue_railing":        True,   # 승강장 끝(터널측) 차단 난간 — 연단에는 무방호[고정]
    "cue_tactile":        True,   # 황색 점자블록 2열 × 양 승강장 (연단 0.3m 이격)
    "cue_material_break": True,   # 연단 수직면 암색 오염 파세이드(밝은 코핑 6cm 잔존)
    "cue_nosing":         True,   # 연단 황색 경계선 (보행면, proud 0.002)
    "cue_sign":           False,  # [예약] 미구현 — config 키만
    "cue_scene_dressing": True,   # 벤치·벽 도어·걸레받이/코니스 띠 일괄
}


# ===========================================================================
# [B] PARAMS — 치수표. NEGOBS_PARAMS_OVERRIDE 로 머지 가능.
# ===========================================================================
PARAMS = dict(
    seed=31,                                  # 침목 지터 고정 시드 (재현성)

    # ── 홀 셸 ──────────────────────────────────────────────────────────
    #  x: 승강장 종주 62 m (−16..46), 그 너머 터널 보어 46..56
    #  y: 근측 승강장 −8..−2 / 궤도 골 −2..+2 / 건너편 승강장 +2..+8
    hall=dict(x0=-16.0, x1=46.0,
              plat_out=8.0,                   # 승강장 바깥 끝 (벽 앞면)
              edge=2.0,                       # 연단선 |y| (낙차 시작 모서리)
              z_walk=0.0,                     # 승강장 보행면
              z_base=-1.60,                   # 슬래브 하단(비가시)
              wall_in=7.98, wall_out=8.40,    # 측벽 (0.02 는 슬래브 물림)
              wall_top=3.70,
              ceil_z0=3.40, ceil_z1=3.72,
              end_t=0.42),                    # 단부 벽 두께

    # ── 궤도부 ────────────────────────────────────────────────────────
    #  발라스트 상면 z=−1.15 → **GT 낙차 1.15 m 의 기준면**
    track=dict(x0=-16.0, x1=55.5,
               half_w=2.05,                   # 슬래브에 0.05 물림(코플래너 회피)
               # ballast_bot 은 슬래브 하단(−1.60)보다 2 cm 더 내림 —
               # 셸 최하면(비가시)이지만 코플래너 자체를 남기지 않는다(§8).
               ballast_top=-1.15, ballast_bot=-1.62,
               gauge=1.435,                   # 표준궤 — 레일 중심 y=±0.7175
               sleeper_step=0.65, sleeper_len=2.60,
               sleeper_w=0.24, sleeper_h=0.16, sleeper_top=-1.06,
               jitter_x=0.03, jitter_y=0.03, jitter_z=0.012,
               rail_w=0.070, rail_h=0.15,     # 레일 몸통 (침목 상면에서 기립)
               head_w=0.075, head_z0=-0.925, head_z1=-0.900),

    # ── 터널 포탈 · 보어 (원경 폐쇄 + 암부 소실점) ──────────────────────
    portal=dict(half_w=2.40, top_z=1.58),     # 단부 벽 개구
    bore=dict(x0=46.30, x1=56.00, half_in=2.38, half_out=2.82,
              z0=-1.92, z1=1.92, cap_t=0.40),

    # ── 천장 발광 패널 (이 씬의 유일 광원) ──────────────────────────────
    #   승강장 중앙 상부 2열(y=±5.0), 간격 4.0 m, 열당 15장 = 총 30장
    panel=dict(rows=(-5.0, 5.0), x0=-14.0, step=4.0, n=15,
               size_x=1.60, size_y=0.55, z0=3.32, z1=3.41,
               color=(0.90, 0.90, 0.86), rough=0.35,
               emis=(1.0, 1.0, 0.95), intensity=12000.0),  # r1: 1500은 승강장 암흑 → 8배 상향

    # ── cue ──────────────────────────────────────────────────────────
    #  점자블록: 연단에서 0.30 이격 → 1열 |y| 2.30..2.60, 2열 2.62..2.92
    tactile=dict(offset=0.30, width=0.30, gap=0.02, proud=0.004),
    #  연단 황색 경계선: 연단선 안쪽 0.02..0.14
    nosing=dict(color=(0.85, 0.72, 0.10), inset=0.02, width=0.12, proud=0.002),
    #  연단 수직면 오염 파세이드 (상단 6 cm 는 밝은 코핑으로 잔존)
    facade=dict(y_in=2.06, y_out=1.99, z0=-1.25, z1=-0.06),
    #  승강장 끝 차단 난간 (터널측) — 연단에는 난간 없음이 위험 본질[고정]
    endrail=dict(x=45.40, rail_r=0.030, post_r=0.040,
                 top_h=1.05, mid_h=0.55, nposts=5),
    #  보행면 줄눈 (횡방향, 3 m 간격)
    joint=dict(step=3.0, width=0.03, proud=0.001),

    # ── 드레싱 ────────────────────────────────────────────────────────
    bench=dict(ys=(-7.40, 7.40), xs_near=(-2.0, 10.0, 22.0, 34.0),
               xs_far=(4.0, 16.0, 28.0),
               length=1.80, width=0.40, height=0.45),
    door=dict(xs=(-8.0, 6.0, 20.0, 34.0), w=1.00, t=0.05, h=2.10),
    trim=dict(skirt_z0=-0.005, skirt_z1=0.22,
              cornice_z0=3.08, cornice_z1=3.41, proud=0.02),

    # ── 사이니지 맥락 v2 (2026-07-27, 휑함 해소 — **소폭**) ────────────────
    #   ★ 불변: 연단(|y|=2.0)·궤도·발라스트·점자블록·연단 경계선·천장 발광 패널
    #     ·조명 파라미터. 신규 요소는 전부 **측벽면(|y| ≥ 7.958)** 또는
    #     **천장 걸이(z ≥ 2.44)** 에만 둔다 → 보행면·연단·궤도 기하 0 변경.
    #   ★ 조도 균형: 광고 라이트박스 발광은 천장 패널(12000)의 1/5 = 2400 으로
    #     상한(1/4=3000) 이내. 총 2장(면적 2.86 m²)뿐이라 승강장/궤도 조도비에
    #     주는 영향은 패널 30장 대비 수 % 미만(궤도 상대 암부 특색 유지).
    signage=dict(
        # 노선 색 밴드 — 양 측벽 종주. 도어(h 2.10)·역명판(≤2.05)·라이트박스
        # (≤2.15) 위, 코니스(3.08) 아래 대역에 둔다.
        band=dict(z0=2.30, z1=2.55, proud=0.022, embed=0.005),
        # 역명판(무텍스트 색면 박판) — 근측벽 x{-4,10,30} / 대측벽 x{2,26}
        #   도어 x{-8,6,20,34}·라이트박스 x{16,12} 와 x 구간이 겹치지 않는다.
        nameplates=[dict(x=-4.0, sgn=-1.0), dict(x=10.0, sgn=-1.0),
                    dict(x=30.0, sgn=-1.0), dict(x=2.0, sgn=1.0),
                    dict(x=26.0, sgn=1.0)],
        nameplate=dict(w=1.60, h=0.50, z_c=1.80, proud=0.030, embed=0.005,
                       bar_h=0.14, bar_w=1.10, bar_proud=0.012),
        # 광고 라이트박스 2 (약한 발광)
        lightboxes=[dict(x=16.0, sgn=-1.0), dict(x=12.0, sgn=1.0)],
        #   face_proud > frame_proud 여야 발광면이 프레임 슬래브에 묻히지 않는다
        #   (프레임은 솔리드 박스 — 면적이 w+2·frame 이라 테두리로 읽힌다).
        lightbox=dict(w=2.20, h=1.30, z_c=1.50, frame=0.09,
                      face_proud=0.095, frame_proud=0.075, embed=0.005,
                      emis=(1.0, 0.96, 0.88), intensity=2400.0),
        # 천장 걸이 역명 사인 4 — 연단 안쪽 |y|=2.6, 최고 카메라(z 1.85) 위
        #   0.59 m 여유. 판 하단 2.44 / 상단 3.05, 걸이봉 → 천장 3.40.
        hangers=[dict(x=0.0, sgn=-1.0), dict(x=24.0, sgn=-1.0),
                 dict(x=12.0, sgn=1.0), dict(x=36.0, sgn=1.0)],
        hanger=dict(y=2.60, w=2.20, t=0.07, z0=2.44, z1=3.05,
                    rod_r=0.022, rod_dx=0.80, ceil_z=3.42,
                    bar_h=0.16, bar_w=1.50, bar_proud=0.010),
    ),

    material=dict(
        scale=dict(concrete_floor=1.5, concrete_wall=2.0, plaster=1.2,
                   gravel=0.5, wood_dark=0.5, tactile=0.3),
        # ─ sRGB 감마 규약(§A-1): "어두운 색"은 0.02~0.06 대역.
        #   텍스처 틴트는 곱셈이므로 (원본 알베도 × 틴트) 가 그 대역에 들도록.
        ballast_tint=(0.155, 0.150, 0.145),   # gravel(≈0.35) × → ≈0.052 [암화]
        sleeper_tint=(0.30, 0.28, 0.26),      # wood_dark(≈0.18) × → ≈0.052
        facade_tint=(0.14, 0.14, 0.15),       # concrete_wall(≈0.45) × → ≈0.063
        wall_tint=(0.90, 0.90, 0.88),         # 백색 타일 벽 (밝음 — 간접광 담당)
        rail_color=(0.045, 0.042, 0.038), rail_metallic=0.55, rail_rough=0.75,
        head_color=(0.42, 0.42, 0.44), head_metallic=0.85, head_rough=0.14,
        ceil_color=(0.20, 0.20, 0.21), ceil_rough=0.85,
        trim_color=(0.055, 0.055, 0.060), trim_rough=0.70,
        tunnel_color=(0.022, 0.022, 0.026), tunnel_rough=0.95,
        joint_color=(0.045, 0.045, 0.048), joint_rough=0.90,
        door_color=(0.28, 0.30, 0.32), door_metallic=0.35, door_rough=0.45,
        bench_color=(0.22, 0.23, 0.25), bench_metallic=0.25, bench_rough=0.50,
        fence_color=(0.45, 0.46, 0.48), fence_metallic=0.70, fence_rough=0.35,
        # ── 사이니지 v2 ── (실내 저조도라 중간~고채도로. 암색 대역은 미사용)
        line_band=(0.72, 0.30, 0.06), line_band_rough=0.55,   # 노선 색(주황)
        sign_field=(0.06, 0.10, 0.24), sign_rough=0.50,       # 역명판 감청 색면
        sign_bar=(0.78, 0.78, 0.76),                          # 백색 색면 바
        lbox_frame=(0.12, 0.12, 0.13), lbox_frame_rough=0.45,
        lbox_face=(0.85, 0.82, 0.75), lbox_face_rough=0.30,
    ),

    # ── 조명 ──────────────────────────────────────────────────────────
    #  완전 실내: 돔·태양 모두 사실상 무효화. hdri 는 check_assets 통과 및
    #  setup_lighting 계약 유지를 위해 기본값 그대로 둔다(밀폐 셸이라 기여 0).
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        lookfix=False,          # 실내 — 태양 캡/지평 리프트 무의미(cv2 비용 절약)
        dome_intensity=8.0,     # 사실상 차단. 셸이 밀폐라 실제 기여는 0
        noon_dome_rot=0.0,
        noon_sun_enable=False,  # 실내 — 직달 태양 없음(프림은 invisible 처리)
        noon_sun_elev=49.79,
        noon_sun_intensity=0.0, noon_sun_color=(1.0, 1.0, 1.0),
        hdri_sun_rotz_offset=0.0,
        dome_rotation_step=15.0,
    ),
    # ─── SUN_AZ_OFFSET: 규약 기본 171.5 에서 **0.0 으로 이탈**.
    #     사유 = 완전 밀폐 실내라 태양 방위가 화면에 아무 영향을 주지 않으며,
    #     노출 판정을 흐리는 잔여 변수를 제거하기 위함. [ ]키 스윕도 무의미. ───
    SUN_AZ_OFFSET=0.0,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneD4")

# 발라스트는 신규 에셋 없이 기존 gravel + 암화 틴트 재사용(감독 결정, 맵 §공통-1).
ASSET_ROLES = ["concrete_floor", "concrete_wall", "plaster", "gravel",
               "wood_dark", "tactile", "hdri", "mdl"]


def build_views():
    """카메라 프리셋: grid_views(gy=−3.6, 근측 승강장 위 종주) + 미장센 4컷.

    gy=−3.6 은 연단(y=−2.0)에서 1.6 m 안쪽 = 점자블록 바로 뒤 보행 동선.
    +X 를 보므로 연단·궤도 골은 **화면 좌측**, 측벽은 우측에 온다."""
    views = sc.grid_views(-3.6)
    # edge_graze: 연단 바로 옆·저시점 종주 — 궤도 골이 통째로 은닉되는 핵심 컷
    views["edge_graze"] = dict(eye=[-6.0, -2.55, 0.32], tgt=[9.0, -2.25, 0.02])
    # edge_approach: 연단 **직교 접근**(보행자가 승강장 안쪽에서 연단으로)
    views["edge_approach"] = dict(eye=[8.0, -6.60, 1.60], tgt=[8.6, -1.20, -0.85])
    # track_reveal: 궤도 골·레일·건너편 승강장이 함께 읽히는 판독 컷
    views["track_reveal"] = dict(eye=[-3.0, -4.80, 1.85], tgt=[9.0, -0.60, -0.95])
    # tunnel_vista: 종주 소실점 + 터널 포탈 암부 (실내 스케일 인상)
    views["tunnel_vista"] = dict(eye=[6.0, -3.40, 1.70], tgt=[44.0, -1.40, 0.10])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 돔 방위(실내=무의미)
[체크리스트]  ※ 밝기·암부 판정은 반드시 P(PathTracing, 8바운스)로!
 1. track_reveal   — 승강장/궤도 골/건너편 승강장 3층 구성이 읽히는가
 2. edge_graze     — 저시점에서 궤도 골이 은닉되어 "하나의 바닥"으로 읽히는가(특색)
 3. edge_approach  — 연단 직교 접근에서 1.15 m 수직면·발라스트가 드러나는가
 4. 조도 대비      — 궤도부가 승강장보다 확연히 어둡되 **완전 흑은 아닌가**
                     (침목·레일 두부가 겨우 읽혀야 정상. 아니면 panel.intensity 스윕)
 5. 패널           — 천장 패널 30장이 승강장 상부에만·궤도 상공엔 없는가
 6. cue ON vs OFF  — tactile/nosing/material_break 토글 시 위험 기하 트랜스폼 불변
 7. Z-파이팅       — 연단 파세이드·줄눈·점자블록·레일 두부 경계에 깜빡임 없는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene31")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    HA = PARAMS["hall"]
    TR = PARAMS["track"]
    ROOT = "/World/Scene31"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    def SPAN(path, x0, x1, y0, y1, z0, z1, mtl=None, col=False):
        """AABB(x0..x1, y0..y1, z0..z1) 박스 — 셸 조립용 가독 래퍼."""
        return BOX(path, ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0),
                   (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), mtl, col=col)

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["platform"] = PBR(
            f"{ROOT}/Looks/Platform", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"])
        # 연단 수직면: 콘크리트 벽 텍스처 + 강한 암화 틴트(분진·제륜자 오염)
        M["facade"] = PBR(
            f"{ROOT}/Looks/Facade", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"],
            tint=mp["facade_tint"])
        # 발라스트: 신규 에셋 없이 gravel + 암화 틴트 (감독 결정)
        M["ballast"] = PBR(
            f"{ROOT}/Looks/Ballast", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            sca["gravel"], tint=mp["ballast_tint"])
        M["sleeper"] = PBR(
            f"{ROOT}/Looks/Sleeper", sc.tex_path("wood_dark", "diff"),
            sc.tex_path("wood_dark", "nor"), sc.tex_path("wood_dark", "rough"),
            sca["wood_dark"], tint=mp["sleeper_tint"])
        # 백색 타일 측벽 — 실내 간접광의 주 반사체이므로 밝게 유지
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["plaster"], tint=mp["wall_tint"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        # ── 상수색 ──
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["head"] = PBR(f"{ROOT}/Looks/RailHead",
                        diffuse_color=mp["head_color"],
                        metallic=mp["head_metallic"],
                        roughness_const=mp["head_rough"])
        M["ceiling"] = PBR(f"{ROOT}/Looks/Ceiling",
                           diffuse_color=mp["ceil_color"],
                           roughness_const=mp["ceil_rough"])
        M["trim"] = PBR(f"{ROOT}/Looks/Trim", diffuse_color=mp["trim_color"],
                        roughness_const=mp["trim_rough"])
        M["tunnel"] = PBR(f"{ROOT}/Looks/Tunnel",
                          diffuse_color=mp["tunnel_color"],
                          roughness_const=mp["tunnel_rough"])
        M["joint"] = PBR(f"{ROOT}/Looks/Joint", diffuse_color=mp["joint_color"],
                         roughness_const=mp["joint_rough"])
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing",
                          diffuse_color=PARAMS["nosing"]["color"],
                          roughness_const=0.70)
        M["door"] = PBR(f"{ROOT}/Looks/Door", diffuse_color=mp["door_color"],
                        metallic=mp["door_metallic"],
                        roughness_const=mp["door_rough"])
        M["bench"] = PBR(f"{ROOT}/Looks/Bench", diffuse_color=mp["bench_color"],
                         metallic=mp["bench_metallic"],
                         roughness_const=mp["bench_rough"])
        M["fence"] = PBR(f"{ROOT}/Looks/Fence", diffuse_color=mp["fence_color"],
                         metallic=mp["fence_metallic"],
                         roughness_const=mp["fence_rough"])
        # ── 사이니지 v2 재질 ──
        M["line_band"] = PBR(f"{ROOT}/Looks/LineBand",
                             diffuse_color=mp["line_band"],
                             roughness_const=mp["line_band_rough"])
        M["sign_field"] = PBR(f"{ROOT}/Looks/SignField",
                              diffuse_color=mp["sign_field"],
                              roughness_const=mp["sign_rough"])
        M["sign_bar"] = PBR(f"{ROOT}/Looks/SignBar",
                            diffuse_color=mp["sign_bar"],
                            roughness_const=mp["sign_rough"])
        M["lbox_frame"] = PBR(f"{ROOT}/Looks/LboxFrame",
                              diffuse_color=mp["lbox_frame"],
                              roughness_const=mp["lbox_frame_rough"])
        lb = PARAMS["signage"]["lightbox"]
        M["lbox_face"] = PBR(f"{ROOT}/Looks/LboxFace",
                             diffuse_color=mp["lbox_face"],
                             roughness_const=mp["lbox_face_rough"],
                             metallic=0.0,
                             emission_color=lb["emis"],
                             emission_intensity=lb["intensity"])
        # 천장 발광 패널 — make_pbr 의 emission 인자 사용(scene_common 07-27 추가)
        pn = PARAMS["panel"]
        M["panel"] = PBR(f"{ROOT}/Looks/Panel", diffuse_color=pn["color"],
                         roughness_const=pn["rough"], metallic=0.0,
                         emission_color=pn["emis"],
                         emission_intensity=pn["intensity"])
        return M

    # -------------------------------------------------------------------
    # 승강장 슬래브 2면 — **궤도 골(|y|<2.0)을 덮지 않는다** (교훈 5 준수).
    #   근측/건너편을 완전히 분리된 2박스로 만들어 개구 분할 규약을 구조적으로
    #   만족시킨다(사각 개구 4박스 분할의 종주형 축약: 종방향은 단부 벽이 폐쇄).
    # -------------------------------------------------------------------
    def build_platforms(M):
        for i, sgn in enumerate((-1.0, 1.0)):
            y_a = sgn * HA["edge"]
            y_b = sgn * HA["plat_out"]
            SPAN(f"{ROOT}/Platform_{i}", HA["x0"], HA["x1"],
                 min(y_a, y_b), max(y_a, y_b),
                 HA["z_base"], HA["z_walk"], M["platform"], col=True)

    def build_joints(M):
        """보행면 횡방향 줄눈 — 대형 슬래브 판 경계(스케일 단서)."""
        jt = PARAMS["joint"]
        w = jt["width"]
        n = int((HA["x1"] - HA["x0"]) / jt["step"]) + 1
        k = 0
        for i in range(n):
            x = HA["x0"] + jt["step"] * (i + 0.5)
            if x >= HA["x1"] - 0.1:
                break
            for j, sgn in enumerate((-1.0, 1.0)):
                y_a = sgn * HA["edge"]
                y_b = sgn * HA["plat_out"]
                SPAN(f"{ROOT}/Joint_{k}", x - w / 2.0, x + w / 2.0,
                     min(y_a, y_b), max(y_a, y_b),
                     HA["z_walk"] - 0.01, HA["z_walk"] + jt["proud"],
                     M["joint"])
                k += 1

    def build_facade(M):
        """연단 수직면 오염 파세이드 (cue_material_break).
        z1=−0.06 → 상단 6 cm 는 슬래브 본체(밝은 콘크리트) 코핑으로 잔존.
        y 범위는 슬래브 안쪽으로 0.06 물려 코플래너 Z-파이팅을 회피하고
        궤도 쪽으로 0.01 만 돌출시킨다."""
        fa = PARAMS["facade"]
        for i, sgn in enumerate((-1.0, 1.0)):
            y_a = sgn * fa["y_in"]
            y_b = sgn * fa["y_out"]
            SPAN(f"{ROOT}/Facade_{i}", HA["x0"], HA["x1"],
                 min(y_a, y_b), max(y_a, y_b), fa["z0"], fa["z1"], M["facade"])

    # -------------------------------------------------------------------
    # 궤도부 — 발라스트 평판 + 침목 + 레일 2본
    # -------------------------------------------------------------------
    def build_track(M):
        hw = TR["half_w"]
        SPAN(f"{ROOT}/Ballast", TR["x0"], TR["x1"], -hw, hw,
             TR["ballast_bot"], TR["ballast_top"], M["ballast"], col=True)

        rs = np.random.RandomState(int(PARAMS["seed"]))     # 고정 시드
        step = TR["sleeper_step"]
        n = int((TR["x1"] - TR["x0"] - 0.4) / step) + 1
        sz = (TR["sleeper_w"], TR["sleeper_len"], TR["sleeper_h"])
        zc = TR["sleeper_top"] - TR["sleeper_h"] / 2.0
        for i in range(n):
            x = TR["x0"] + 0.2 + step * i + rs.uniform(-TR["jitter_x"],
                                                       TR["jitter_x"])
            y = rs.uniform(-TR["jitter_y"], TR["jitter_y"])
            z = zc + rs.uniform(-TR["jitter_z"], TR["jitter_z"])
            BOX(f"{ROOT}/Sleeper_{i}", (x, y, z), sz, M["sleeper"])

        # 레일 2본: 몸통(암색 강재) + 두부(연마면, metallic 0.85)
        rz0 = TR["sleeper_top"]
        rz1 = rz0 + TR["rail_h"]
        for i, sgn in enumerate((-1.0, 1.0)):
            yc = sgn * TR["gauge"] / 2.0
            SPAN(f"{ROOT}/Rail_{i}/Body", TR["x0"], TR["x1"],
                 yc - TR["rail_w"] / 2.0, yc + TR["rail_w"] / 2.0,
                 rz0, rz1, M["rail"])
            # 두부는 몸통 상단에 0.015 물리고 0.01 돌출 (코플래너 회피)
            SPAN(f"{ROOT}/Rail_{i}/Head", TR["x0"], TR["x1"],
                 yc - TR["head_w"] / 2.0, yc + TR["head_w"] / 2.0,
                 TR["head_z0"], TR["head_z1"], M["head"])

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 궤도 골을 z=0 까지 메워 전면 평지화.
        (연단 파세이드·궤도 일체 미생성 — 낙차 0)"""
        SPAN(f"{ROOT}/FlatFill", HA["x0"], HA["x1"],
             -TR["half_w"], TR["half_w"], HA["z_base"], HA["z_walk"],
             M["platform"], col=True)

    # -------------------------------------------------------------------
    # 셸 — 측벽 2 · 천장 · 단부 벽 2(+터널 포탈) · 터널 보어
    #   완전 밀폐가 목적: 어느 면에도 돔 유입 경로를 남기지 않는다.
    # -------------------------------------------------------------------
    def build_shell(M):
        # 측벽 (백색 타일). 안쪽 면 |y|=7.98 — 슬래브(±8.0)에 0.02 물림.
        for i, sgn in enumerate((-1.0, 1.0)):
            y_a = sgn * HA["wall_in"]
            y_b = sgn * HA["wall_out"]
            SPAN(f"{ROOT}/SideWall_{i}", HA["x0"] - HA["end_t"],
                 HA["x1"] + HA["end_t"], min(y_a, y_b), max(y_a, y_b),
                 HA["z_base"], HA["wall_top"], M["wall"], col=True)
        # 천장 슬래브 (벽 상단을 0.30 물고 덮음)
        SPAN(f"{ROOT}/Ceiling", HA["x0"] - HA["end_t"], HA["x1"] + HA["end_t"],
             -HA["wall_out"], HA["wall_out"], HA["ceil_z0"], HA["ceil_z1"],
             M["ceiling"])
        # 단부 벽 W (승강장 시작단) — 전면 폐쇄
        SPAN(f"{ROOT}/EndWall_W", HA["x0"] - HA["end_t"], HA["x0"] + 0.02,
             -HA["wall_out"], HA["wall_out"], HA["z_base"], HA["ceil_z1"],
             M["wall"], col=True)
        # 단부 벽 E (터널측) — 궤도 개구(포탈)를 남기고 3분할
        po = PARAMS["portal"]
        ex0, ex1 = HA["x1"] - 0.02, HA["x1"] + HA["end_t"]
        SPAN(f"{ROOT}/EndWall_E_0", ex0, ex1, -HA["wall_out"], -po["half_w"],
             HA["z_base"], HA["ceil_z1"], M["wall"], col=True)
        SPAN(f"{ROOT}/EndWall_E_1", ex0, ex1, po["half_w"], HA["wall_out"],
             HA["z_base"], HA["ceil_z1"], M["wall"], col=True)
        SPAN(f"{ROOT}/EndWall_E_2", ex0, ex1,
             -po["half_w"] - 0.02, po["half_w"] + 0.02,
             po["top_z"], HA["ceil_z1"], M["wall"], col=True)

        # 터널 보어 — 5면(측벽2·천장·바닥·back cap) 암색 박스로 봉함.
        #   "터널 입구 암부"가 목표값이므로 재질은 0.022 대의 극암색 상수.
        bo = PARAMS["bore"]
        for i, sgn in enumerate((-1.0, 1.0)):
            y_a = sgn * bo["half_in"]
            y_b = sgn * bo["half_out"]
            SPAN(f"{ROOT}/Bore_Side_{i}", bo["x0"], bo["x1"],
                 min(y_a, y_b), max(y_a, y_b), bo["z0"], bo["z1"], M["tunnel"])
        SPAN(f"{ROOT}/Bore_Roof", bo["x0"], bo["x1"],
             -bo["half_out"], bo["half_out"], po["top_z"], bo["z1"],
             M["tunnel"])
        SPAN(f"{ROOT}/Bore_Floor", bo["x0"], bo["x1"],
             -bo["half_out"], bo["half_out"], bo["z0"], HA["z_base"] + 0.02,
             M["tunnel"])
        SPAN(f"{ROOT}/Bore_Cap", bo["x1"] - bo["cap_t"], bo["x1"],
             -bo["half_out"], bo["half_out"], bo["z0"], bo["z1"], M["tunnel"])

    # -------------------------------------------------------------------
    # 천장 발광 패널 — 승강장 상부 2열만. 궤도 상공은 의도적 미배치.
    # -------------------------------------------------------------------
    def build_panels(M):
        pn = PARAMS["panel"]
        k = 0
        for r, yc in enumerate(pn["rows"]):
            for i in range(int(pn["n"])):
                x = pn["x0"] + pn["step"] * i
                SPAN(f"{ROOT}/Panel_{k}",
                     x - pn["size_x"] / 2.0, x + pn["size_x"] / 2.0,
                     yc - pn["size_y"] / 2.0, yc + pn["size_y"] / 2.0,
                     pn["z0"], pn["z1"], M["panel"])
                k += 1
        print(f"[조명] 천장 발광 패널 {k}장 "
              f"(열 {len(pn['rows'])} × {pn['n']}, 간격 {pn['step']} m, "
              f"emissive_intensity={pn['intensity']}) — 궤도 상공 미배치")

    # -------------------------------------------------------------------
    # cue — 점자블록 / 연단 경계선 / 승강장 끝 차단 난간
    # -------------------------------------------------------------------
    def build_cues(M):
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            a0 = HA["edge"] + tc["offset"]              # 2.30
            a1 = a0 + tc["width"]                       # 2.60
            b0 = a1 + tc["gap"]                         # 2.62
            b1 = b0 + tc["width"]                       # 2.92
            k = 0
            for sgn in (-1.0, 1.0):
                for (p, q) in ((a0, a1), (b0, b1)):
                    y0, y1 = sorted((sgn * p, sgn * q))
                    sc.build_tactile(stage, f"{ROOT}/Tactile_{k}",
                                     HA["x0"], HA["x1"], y0, y1, M["tactile"],
                                     z=HA["z_walk"], proud=tc["proud"])
                    k += 1
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            for i, sgn in enumerate((-1.0, 1.0)):
                p = HA["edge"] + ns["inset"]
                q = p + ns["width"]
                y0, y1 = sorted((sgn * p, sgn * q))
                SPAN(f"{ROOT}/Nosing_{i}", HA["x0"], HA["x1"], y0, y1,
                     HA["z_walk"] - 0.01, HA["z_walk"] + ns["proud"],
                     M["nosing"])
        if cfg["cue_railing"]:
            # 승강장 끝(터널측) 차단 난간. **연단에는 난간 없음**이 위험 본질.
            er = PARAMS["endrail"]
            k = 0
            for sgn in (-1.0, 1.0):
                ya = sgn * HA["edge"]
                yb = sgn * HA["plat_out"]
                y0, y1 = sorted((ya, yb))
                length = y1 - y0
                yc = (y0 + y1) / 2.0
                for tag, hz, rr in (("Top", er["top_h"], er["rail_r"]),
                                    ("Mid", er["mid_h"], er["rail_r"] * 0.6)):
                    CYL(f"{ROOT}/EndRail_{k}/{tag}", (er["x"], yc, hz),
                        rr, length, M["fence"], rotX=90.0)
                ph = er["top_h"]
                for j in range(int(er["nposts"])):
                    t = (j + 0.5) / float(er["nposts"])
                    CYL(f"{ROOT}/EndRail_{k}/Post_{j}",
                        (er["x"], y0 + t * length, ph / 2.0),
                        er["post_r"], ph, M["fence"])
                k += 1

    # -------------------------------------------------------------------
    # 드레싱 — 벤치 · 벽 도어 · 걸레받이/코니스 띠 (맥락 판독 보강)
    # -------------------------------------------------------------------
    def build_dressing(M):
        bn = PARAMS["bench"]
        k = 0
        # [v5.1 §3] 12 m 등간격·완전 축평행 해소. 고정식 승강장 의자이므로
        #   각도는 시공 오차 대역(3~5°)·위치는 ±0.12 m 로 **작게** 준다
        #   (산업 정렬 관행 제외 대상인 천장 패널·침목·점자블록은 불변).
        #   |y| = 7.40 ± 0.12 → 연단(|y| 2.0)·측벽(7.958)과 여유 유지.
        for ys, xs in ((bn["ys"][0], bn["xs_near"]), (bn["ys"][1], bn["xs_far"])):
            for x in xs:
                dx, dy = bc.jit_pos(x, ys, "benchD4", amp=0.12)
                yaw = bc.jit_yaw(x, ys, "benchD4", lo=3.0, hi=5.0)
                sc.build_bench(stage, f"{ROOT}/Bench_{k}", x + dx, ys + dy,
                               HA["z_walk"], M["bench"], length=bn["length"],
                               width=bn["width"], height=bn["height"], yaw=yaw)
                k += 1
        tm = PARAMS["trim"]
        dr = PARAMS["door"]
        k = 0
        for sgn in (-1.0, 1.0):
            wi = sgn * HA["wall_in"]
            wo = sgn * (HA["wall_in"] - tm["proud"])    # 벽면에서 실내측 돌출
            y0, y1 = sorted((wi, wo))
            SPAN(f"{ROOT}/Skirt_{k}", HA["x0"], HA["x1"], y0, y1,
                 tm["skirt_z0"], tm["skirt_z1"], M["trim"])
            SPAN(f"{ROOT}/Cornice_{k}", HA["x0"], HA["x1"], y0, y1,
                 tm["cornice_z0"], tm["cornice_z1"], M["trim"])
            k += 1
        k = 0
        for sgn in (-1.0, 1.0):
            wi = sgn * HA["wall_in"]
            wo = sgn * (HA["wall_in"] - dr["t"])
            y0, y1 = sorted((wi, wo))
            for x in dr["xs"]:
                SPAN(f"{ROOT}/Door_{k}", x - dr["w"] / 2.0, x + dr["w"] / 2.0,
                     y0, y1, HA["z_walk"], HA["z_walk"] + dr["h"], M["door"])
                k += 1

    # -------------------------------------------------------------------
    # 사이니지 맥락 v2 — 노선 색 밴드 · 역명판 · 광고 라이트박스 · 천장 걸이 사인
    # -------------------------------------------------------------------
    def build_signage(M):
        """승강장 사이니지. **연단·궤도·점자블록·발광 패널·조명 일절 불변.**

        ── 카메라 검산 (PT 판정 씬이므로 좌표 검산으로 대체) ────────────────
        전 뷰 eye: grid(gy −3.6) (−2/−5/−10, −3.6, 0.3~1.8) ·
          edge_graze(−6, −2.55, 0.32) · edge_approach(8, −6.60, 1.60) ·
          track_reveal(−3, −4.80, 1.85) · tunnel_vista(6, −3.40, 1.70).
        1) 벽면 요소(밴드·역명판·라이트박스): 최대 돌출 y = ±(7.98−0.095)
           = ±7.885. 카메라 최대 |y| = 6.60(edge_approach) → **1.29 m 여유**,
           매몰·간섭 0. 보행면(z 0)·연단(|y|=2.0)과는 5.9 m 이격.
        2) 천장 걸이 사인: |y| = 2.60(연단 안쪽 0.6 m, 점자블록 2.30~2.92 직상),
           판 하단 z 2.44. 카메라 최고 z = 1.85(track_reveal) →
           **수직 여유 0.59 m**, 최근접 카메라 edge_graze(y −2.55, z 0.32)
           와는 x 6 m 이상 이격 → 매몰 0.
           · 시야 검산: edge_graze 에서 x=0 사인은 앙각 19.5° > vfov half 18°
             → 프레임 위로 벗어나고, x=24 사인은 4.0° → 프레임 안(원경).
             어느 쪽도 **연단선·궤도 골 시선(하향)** 을 가리지 않는다.
           · track_reveal 에서 x=0 사인은 시축 위 23° → 프레임 밖,
             x=24 사인은 13.8° → 프레임 안(상부). 궤도 시선은 하향이라 무간섭.
        3) x 구간 충돌 검산: 도어 x{−8,6,20,34}(±0.50) / 역명판 x{−4,10,30}
           근측·{2,26} 대측(±0.80) / 라이트박스 x{16}근측·{12}대측(±1.10)
           → 동일 벽면에서 서로 겹치는 구간 없음. 벤치(근 −2,10,22,34 /
           대 4,16,28)는 y=±7.40 이라 벽면 요소(|y| ≥ 7.905)와 z·y 모두 이격.
        4) 노선 색 밴드 z 2.30~2.55 — 도어 상단 2.10 / 역명판 상단 2.05 /
           라이트박스 상단 2.15 위, 코니스 하단 3.08 아래 → 코플래너 0.
        """
        sg = PARAMS["signage"]
        wi = HA["wall_in"]
        cnt = dict(band=0, plate=0, lbox=0, hanger=0)

        def wall_slab(path, x0, x1, sgn, z0, z1, proud, mtl, embed=0.005):
            """측벽 내면 부착 박판. sgn=−1 근측 / +1 대측.
            뒷면은 벽체 안으로 embed 만큼 물려 벽면과의 코플래너를 제거한다."""
            y_a = sgn * (wi + embed)
            y_b = sgn * (wi - proud)
            SPAN(path, x0, x1, min(y_a, y_b), max(y_a, y_b), z0, z1, mtl)

        # ── ① 노선 색 밴드 (양 측벽 종주) ──
        bd = sg["band"]
        for i, sgn in enumerate((-1.0, 1.0)):
            wall_slab(f"{ROOT}/LineBand_{i}", HA["x0"], HA["x1"], sgn,
                      bd["z0"], bd["z1"], bd["proud"], M["line_band"],
                      bd["embed"])
            cnt["band"] += 1

        # ── ② 역명판 (무텍스트 색면 박판) ──
        np_ = sg["nameplate"]
        for i, pl in enumerate(sg["nameplates"]):
            x, sgn = pl["x"], pl["sgn"]
            wall_slab(f"{ROOT}/NamePlate_{i}", x - np_["w"] / 2.0,
                      x + np_["w"] / 2.0, sgn,
                      np_["z_c"] - np_["h"] / 2.0, np_["z_c"] + np_["h"] / 2.0,
                      np_["proud"], M["sign_field"], np_["embed"])
            # 백색 색면 바 — 판 앞면에서 다시 bar_proud 만큼 돌출(코플래너 0)
            y_a = sgn * (wi - np_["proud"] + 0.008)
            y_b = sgn * (wi - np_["proud"] - np_["bar_proud"])
            SPAN(f"{ROOT}/NamePlate_{i}_Bar", x - np_["bar_w"] / 2.0,
                 x + np_["bar_w"] / 2.0, min(y_a, y_b), max(y_a, y_b),
                 np_["z_c"] - np_["bar_h"] / 2.0,
                 np_["z_c"] + np_["bar_h"] / 2.0, M["sign_bar"])
            cnt["plate"] += 1

        # ── ③ 광고 라이트박스 (약발광 — 패널의 1/5) ──
        lb = sg["lightbox"]
        for i, bx in enumerate(sg["lightboxes"]):
            x, sgn = bx["x"], bx["sgn"]
            fw, fh = lb["w"] + 2.0 * lb["frame"], lb["h"] + 2.0 * lb["frame"]
            wall_slab(f"{ROOT}/LightBox_{i}_Frame", x - fw / 2.0, x + fw / 2.0,
                      sgn, lb["z_c"] - fh / 2.0, lb["z_c"] + fh / 2.0,
                      lb["frame_proud"], M["lbox_frame"], lb["embed"])
            # 발광면: 뒷면은 프레임 슬래브 안에 0.010 물리고 앞면은 프레임보다
            #   0.020 돌출 → 코플래너 0 + 프레임이 폭 0.09 테두리로 남는다.
            y_a = sgn * (wi - lb["face_proud"])
            y_b = sgn * (wi - lb["face_proud"] + 0.030)
            SPAN(f"{ROOT}/LightBox_{i}_Face", x - lb["w"] / 2.0,
                 x + lb["w"] / 2.0, min(y_a, y_b), max(y_a, y_b),
                 lb["z_c"] - lb["h"] / 2.0, lb["z_c"] + lb["h"] / 2.0,
                 M["lbox_face"])
            cnt["lbox"] += 1

        # ── ④ 천장 걸이 역명 사인 ──
        hg = sg["hanger"]
        for i, hd in enumerate(sg["hangers"]):
            x, sgn = hd["x"], hd["sgn"]
            yc = sgn * hg["y"]
            SPAN(f"{ROOT}/HangSign_{i}", x - hg["w"] / 2.0, x + hg["w"] / 2.0,
                 yc - hg["t"] / 2.0, yc + hg["t"] / 2.0, hg["z0"], hg["z1"],
                 M["sign_field"])
            # 양면 색면 바 (승강장 양방향에서 읽히게 2매)
            for s, sy in enumerate((-1.0, 1.0)):
                y_a = yc + sy * hg["t"] / 2.0 - sy * 0.008
                y_b = yc + sy * (hg["t"] / 2.0 + hg["bar_proud"])
                SPAN(f"{ROOT}/HangSign_{i}_Bar{s}", x - hg["bar_w"] / 2.0,
                     x + hg["bar_w"] / 2.0, min(y_a, y_b), max(y_a, y_b),
                     (hg["z0"] + hg["z1"]) / 2.0 - hg["bar_h"] / 2.0,
                     (hg["z0"] + hg["z1"]) / 2.0 + hg["bar_h"] / 2.0,
                     M["sign_bar"])
            for s, sx in enumerate((-hg["rod_dx"], hg["rod_dx"])):
                CYL(f"{ROOT}/HangSign_{i}_Rod{s}",
                    (x + sx, yc, (hg["z1"] - 0.03 + hg["ceil_z"]) / 2.0),
                    hg["rod_r"], hg["ceil_z"] - hg["z1"] + 0.03, M["fence"])
            cnt["hanger"] += 1
        return cnt

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ... (완전 실내 · 발광 패널 단독 조명)")
    M = setup_materials()

    build_platforms(M)
    build_joints(M)
    build_shell(M)
    if cfg["hazard_stairs"]:
        build_track(M)
        if cfg["cue_material_break"]:
            build_facade(M)
    else:
        build_flat_fill(M)
    build_panels(M)
    build_cues(M)
    sign_cnt = None
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
        sign_cnt = build_signage(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])
    print("[조명] 완전 밀폐 실내 — dome/sun 기여 0. "
          "밝기·암부 판정은 PathTracing(P키, 8바운스)로만 할 것.")

    if sign_cnt is not None:
        # 사이니지 자기검산 (PT 씬 — RT 로 확인 불가한 요소는 좌표로 검산)
        sg = PARAMS["signage"]
        lb, hg = sg["lightbox"], sg["hanger"]
        eyes = [(-2.0, -3.6, 1.8), (-5.0, -3.6, 1.8), (-10.0, -3.6, 1.8),
                (-6.0, -2.55, 0.32), (8.0, -6.60, 1.60),
                (-3.0, -4.80, 1.85), (6.0, -3.40, 1.70)]
        y_wall_face = HA["wall_in"] - max(lb["frame_proud"], lb["face_proud"],
                                          sg["nameplate"]["proud"],
                                          sg["band"]["proud"])
        wall_margin = y_wall_face - max(abs(e[1]) for e in eyes)
        z_margin = hg["z0"] - max(e[2] for e in eyes)
        ratio = lb["intensity"] / PARAMS["panel"]["intensity"]
        print(f"[사이니지] 노선밴드 {sign_cnt['band']} · 역명판 "
              f"{sign_cnt['plate']} · 라이트박스 {sign_cnt['lbox']} · "
              f"천장 걸이 {sign_cnt['hanger']}")
        print(f"[검산] 벽면 요소 최전면 |y|={y_wall_face:.3f} vs 카메라 최대 "
              f"|y|={max(abs(e[1]) for e in eyes):.2f} → 여유 "
              f"{wall_margin:.2f} m · 걸이 사인 하단 z={hg['z0']:.2f} vs "
              f"카메라 최고 z={max(e[2] for e in eyes):.2f} → 여유 "
              f"{z_margin:.2f} m")
        print(f"[검산] 라이트박스 발광비 {ratio:.2f} × 패널(상한 0.25) · "
              f"연단(|y|=2.0)·궤도·점자블록·패널 좌표 불변")

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneD4 조립 완료 · SMOKE_OK prims={n} · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["track_reveal"]
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
                print("[렌더] RTX Real-Time (이동용 — 실내 발광 미반영)")
            else:
                set_render_mode("PathTracing")
                print(f"[렌더] PathTracing (totalSpp={pt_spp}, "
                      f"maxBounces={PARAMS['render']['pt_max_bounces']}) "
                      f"← 판정은 이 모드로")
        elif event.input == K.C:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fp = os.path.join(LOOKCHECK_DIR, f"sceneD4_{ts}.png")
            capture(fp)
            print(f"[캡처] {fp}")
        elif event.input == K.LEFT_BRACKET:
            dome_user_rot[0] -= rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[돔 방위] 오프셋 {dome_user_rot[0]:+.0f}° (실내라 영향 없음)")
        elif event.input == K.RIGHT_BRACKET:
            dome_user_rot[0] += rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[돔 방위] 오프셋 {dome_user_rot[0]:+.0f}° (실내라 영향 없음)")
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
