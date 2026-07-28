# -*- coding: utf-8 -*-
"""
sceneC4_wet_stairs.py — NegObs 인공씬 28호: 비 온 직후 젖은 석재 계단 (Isaac Sim 4.5)

유형    : C4 조건 변주 — 광폭 화강암 계단 기하 + 젖음(재질) 레이어
사양서  : Docs/nanobanana_batch1_geometry_map.md §B sceneC4_wet_stairs
룩 참조 : look_refs/c4_wet_stairs.jpg
공통    : scene_common.py · scene16_canopy_shadow.py(표준 템플릿) ·
          scene01_campus_stairs.py(직선 계단 기준형)

위험 본질: 기하는 광폭 직선 14단(riser 0.15 · tread 0.35 · 폭 6.0)인데,
           비에 젖은 트레드 상면이 **거울처럼 흐린 하늘을 반사**한다.
           밝은 하늘 반사가 인접 단의 라이저 음영을 씻어내 단 에지가 서로
           **병합**되고, 수막이 고인 트레드는 아예 수평 거울면이 된다.
           GT는 기하 그대로 **낙차 양성(2.10m)** — C1(눈)과 함께 "재질 변주 축".
목표     : 상부 광장 → 광폭 계단 → 하부 광장의 보행 연속성을 유지한 채,
           젖음을 **재질 레이어(트레드 전용 저러프니스 박판)** 로 구현하고
           수막(build_water 박판)을 얹어 렌더로 판정 (렌더 전용).

특색 성립 조건 [중요]:
  **흐린 하늘 dome(overcast)** 이 이 씬의 성립 조건이다. 경면이 반사할 대상이
  밝고 균질한 하늘이어야 "단 에지 병합"이 성립한다. 청천 정오광이면 태양
  하이라이트가 점으로 찍히고 경질 그림자가 에지를 되살려 특색이 무너진다.
  → light 프로파일 = sc.OVERCAST_HDRI + lookfix=False + 무태양(sceneC1 공유).
  또한 경면 반사는 단일바운스 RT에서 과소평가되므로 **판정은 PT** 로 한다.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneC4_wet_stairs.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneC4_wet_stairs.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneC4_wet_stairs.py

좌표계: Z-up, m, 진행축 +X, 낙차 시작 모서리 = x=0.
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
# [A] SCENE_CONFIG — 표준 7키 + 특색 토글 1키(wet_surface).
#     hazard_stairs 만 기하 토글(False→전면 z=0 평지).
#     wet_surface 는 재질 토글(기하 불변)이며, 물리적으로 성립하지 않는
#     "마른 노면 위 수막"을 피하기 위해 수막 박판만 함께 제거된다.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 계단·사면·하부 광장을 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        True,   # 양측 치크밴드 위 스테인리스 난간 2선
    "cue_tactile":        True,   # 상단 경고 점자블록 (젖어도 잔존하는 유일 고대비 단서)
    "cue_material_break": True,   # False → 계단도 광장 포장재로 통일
    "cue_nosing":         False,  # 기본 off — 노징 도색은 '에지 병합' 특색을 무력화.
                                  #            대조 실험 시 True 로 켜서 사용.
    "cue_sign":           False,  # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,   # 잔디 사면·볼라드·원경 건물 일괄
    "wet_surface":        True,   # [특색] False → 건조 재질 + 수막 제거 = 대응쌍
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # 광폭 직선 14단 × riser 0.15 · tread 0.35 → 낙차 2.10m, run 4.90m, 폭 6.0
    stairs=dict(x0=0.0, riser=0.15, tread=0.35, nsteps=14,
                y0=-3.0, y1=3.0, z_top=0.0, base_z=-3.00),

    # 상부 광장(석재 포장). 두께 2.6 → 하부 광장 바닥보다 아래까지 솔리드.
    upper=dict(x0=-60.0, x1=0.0, y0=-60.0, y1=60.0, z_top=0.0, thick=2.60),
    # 하부 광장. x0 는 계단 끝(run)보다 0.05 뒤에서 시작하고 상면을 2mm 낮춰
    # 마지막 단 상면과의 동일평면(Z-파이팅)을 회피 — 겹침 5cm.
    lower=dict(x_back=0.05, x1=60.0, y0=-60.0, y1=60.0, z_gap=0.002,
               thick=0.70),

    # 계단 측면 석재 치크밴드(노출 스트링어). 상면 = 노징선 + proud.
    cheek=dict(y_in=2.94, y_out=3.60, proud=0.06, x_head=0.05, x_tail=0.10,
               thick=0.70),
    # 치크 바깥 잔디 사면 — 상부 광장 에지와 하부 광장을 잇는 제방.
    #   상면 평면 z = −(riser/tread)·x → 추가 낙차 에지 없음(GT 오염 없음),
    #   보행 연속성 유지(교훈 9). 램프 대비쌍(scene17)과 달리 주행로 아님.
    bank=dict(y_in=3.55, y_out=60.0, x_head=0.05, x_tail=0.20, thick=2.40),

    # ─── 젖음 레이어 [특색 파라미터] ─────────────────────────────────────
    #  film_*      트레드 상면 전용 박판(젖은 막). 이 박판만 저러프니스 재질을
    #              받아 "트레드는 경면 / 라이저·측면은 반건조" 대비를 만든다.
    #              proud 는 규약 0.001~0.004 내(0.003). x/y 로 3~5mm 내밀어
    #              단 솔리드 면과의 동일평면을 회피한다.
    #  wet_rough   경면 러프니스. 낮을수록 하늘 반사가 선명 → 에지 병합 강화.
    #              사양 0.06~0.12. 시작값 0.08. 스윕 0.06(거울)~0.12(무광젖음).
    #  damp_rough  라이저·측면 반건조 러프니스(사양 0.4).
    #  wet_tint / damp_tint : 젖으면 알베도가 어두워지는 물리 근사.
    #  water_films : 수막을 얹을 단 인덱스와 부분 폭(랜덤 금지 — 고정 테이블).
    # ────────────────────────────────────────────────────────────────────
    wet=dict(film_t=0.012, film_proud=0.003, film_over_x=0.003,
             film_over_y=0.005,
             wet_rough=0.14, wet_spec=0.9,   # r1: 0.08은 완전 거울면 → 경면 완화
             plaza_rough=0.12, plaza_spec=0.8,
             damp_rough=0.40,
             wet_tint=(0.55, 0.56, 0.60), plaza_tint=(0.56, 0.57, 0.61),
             damp_tint=(0.74, 0.75, 0.79),
             water_t=0.005, water_lift=0.006,
             # ─── [비 직후 패키지 v2 · 07-27] ────────────────────────────
             #  사용자 지적: "비가 온 상황이 덜 느껴진다 / 밝은 돌에 광만 난다".
             #  ① 패치워크: 트레드 젖음을 단일 재질 → 3단 tier 의 **트레드 내
             #     부분 폭 박판**으로 분해(트레드 단위 경계 제거).
             #  ② 다크닝: 마른 기준(damp_tint 0.74) 대비 강젖음 0.36 = 51% 감광
             #     (지시 30~40% 이상 확보), 중간 0.47, 반건조 패치 0.62.
             #     동시에 B 채널을 상대 상향(젖은 석재의 채도 상승 근사).
             #  ③ 러프니스는 tier 별 0.10 / 0.20 / 0.35 — 강젖음은 경면을 유지해
             #     "에지 병합" 특색(하늘 반사)이 무너지지 않게 한다.
             #  ④ 기하 불변: 박판 envelope(트레드 상면 proud 0.003 · 두께
             #     0.012)은 그대로. y 분할만 도입하고 인접 패치는 patch_overlap
             #     만큼 겹치며 proud 를 patch_step 씩 층지게 해 동일평면 회피.
             patch_tiers=[dict(name="Strong", rough=0.10, spec=0.95,
                               tint=(0.352, 0.362, 0.398)),
                          dict(name="Mid", rough=0.20, spec=0.85,
                               tint=(0.455, 0.468, 0.500)),
                          dict(name="Damp", rough=0.35, spec=0.60,
                               tint=(0.605, 0.615, 0.645))],
             patch_seed=2804, patch_min=3, patch_max=5, patch_bias=0.62,
             patch_overlap=0.006, patch_step=0.0004,
             # 웅덩이 다크닝 링(젖어 번진 둘레) — 수막보다 낮은 proud.
             ring_proud=0.0045, ring_grow_x=0.022, ring_grow_y=0.075,
             # tide mark(수위선) · 치크 러노프 · 라이저 흘러내림 스트릭
             #  ※ 치크밴드 외측면은 잔디 뱅크(y_in 3.55)에 6cm만 노출되므로
             #    긴 수위 밴드가 파묻힌다 → 노출분(0.10)만 밴드로 두고, 실제
             #    "비 온 티"는 **치크 상면 러노프 스트라이프**가 담당한다.
             tide_h=0.34, tide_h_cheek=0.10, tide_drop=0.005, tide_proud=0.012,
             runoff_w=0.24, runoff_in=0.02, runoff_proud=0.003, runoff_t=0.05,
             streak_seed=2811, streak_n=14, streak_w=0.11, streak_proud=0.003),
    # 수막: (단 인덱스 1~n, y0, y1) — 트레드 부분 폭에만 고임.
    #   v2: 사각 1매 → **불규칙 lobe 3~4매 겹침 + 다크닝 링**(고정 시드 산출).
    water_films=[dict(step=3, y0=-2.40, y1=0.30),
                 dict(step=6, y0=0.10, y1=2.55),
                 dict(step=9, y0=-2.60, y1=-0.20),
                 dict(step=12, y0=-1.20, y1=2.40)],
    # 광장 수막 2매 (하부 = 계단 발치 큰 시트 · 상부 = 접근로 얕은 시트)
    #   v2: 회전 lobe 3매 겹침으로 사각 윤곽 제거 + 다크닝 링.
    water_sheets=[dict(name="Lower", x0=0.15, x1=5.60, y0=-2.20, y1=2.60,
                       where="lower"),
                  dict(name="Upper", x0=-4.80, x1=-1.40, y0=-1.60, y1=1.90,
                       where="upper")],

    # 양측 난간 (치크밴드 위). 경사는 계단과 동일.
    rail=dict(y=3.27, x_start=-1.20, rail_h=0.90, post_r=0.022, rail_r=0.03,
              rail_mid_r=0.018, rail_mid_drop=0.45, spacing=1.50),

    tactile=dict(ahead=0.30, proud=0.004),
    nosing=dict(color=(0.85, 0.72, 0.10), width=0.05, proud=0.001,
                y_inset=0.02),

    # ── 볼라드 [v5.1 §2 · ctx2] 상부 광장 진입부 1열 ───────────────────────
    #   구(舊): (−2.6/−5.6, ±4.6) 2×2 장식 배열 · φ0.16·h0.80 · 반사띠/
    #   점형블록 없음 → 장식적 볼라드 열 금지(v5.1 §2)에 저촉.
    #   신(新): **광장 진입부(x=−6.0) 횡단 1열** · 규격 φ0.12·h0.90 ·
    #   간격 1.5 m · 상단 백색 반사띠 · 전면(−X 접근측) 0.3 m 점형블록.
    #   중앙 |y| < 2.8 (폭 5.6 m ≈ 계단 폭 6.4 m)은 **보행·소방 진입 개구**로
    #   비운다 — 광폭 대계단으로 향하는 주 동선이라 실제로도 막지 않는다.
    #   ★ 특색(젖은 계단) 보존 좌표 검산:
    #     · d10(eye −10) 기준 최내측 볼라드 실루엣 방위 34.4°, 점형블록 최내측
    #       모서리 33.4° — 둘 다 프레임 반각 30° 밖 → 계단 폐색 0.
    #     · approach(eye −7)·grazing_mirror(eye −2.4)·film_closeup(eye −0.8)
    #       에서는 각각 방위 70° 밖 / 카메라 후방 → 무간섭.
    #     · lower_lookback(eye +8.5)에서는 계단보다 **원거리**라 폐색 불가.
    #   ★ 점형블록은 젖음 틴트 미적용(감독 지시): 소판 x −6.06..−6.36 은
    #     상부 수막 시트(x −4.80..−1.40) 밖이라 물리적으로도 정합.
    bollard_rows=[dict(name="N", x=-6.0, y0=2.8, y1=5.8),
                  dict(name="S", x=-6.0, y0=-2.8, y1=-5.8)],
    bollard=dict(radius=0.06, height=0.90, spacing=1.5, front=(-1.0, 0.0)),
    buildings=dict(
        # +X 원경 비스타 차단(하부 광장 레벨 기단). 파사드 -X 평면.
        C=dict(x0=28.0, x1=34.0, y0=-16.0, y1=16.0, h=14.0, floors=4,
               axis="x", facade_x=28.0, face_dir=-1.0, level="lower"),
        # -X 원경(lower_lookback 용). 파사드 +X 평면, 상부 광장 레벨 기단.
        D=dict(x0=-48.0, x1=-42.0, y0=-16.0, y1=16.0, h=10.0, floors=3,
               axis="x", facade_x=-42.0, face_dir=1.0, level="upper"),
        # [맥락 v2] 파사드 폭 확장 — C 좌우 저층 익동 2동으로 관공서 가구(街區)
        #   느낌. C(y ±16)와 y 구간이 분리되어 중첩 없음. 전부 x≥30 원경.
        E=dict(x0=30.0, x1=36.0, y0=17.0, y1=40.0, h=11.0, floors=3,
               axis="x", facade_x=30.0, face_dir=-1.0, level="lower"),
        F=dict(x0=30.0, x1=36.0, y0=-40.0, y1=-17.0, h=12.0, floors=3,
               axis="x", facade_x=30.0, face_dir=-1.0, level="lower"),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),

    # ═══ [맥락 드레싱 v2 · 07-27] 관공서/문화시설 앞 대계단의 장소성 ═══
    #  감사 v4 통합계획 §휑함 대응. 계단 기하·젖음 레이어 파라미터 불변.
    #  신규 프림은 상부 광장(x<0, z=0)과 하부 광장(x>RUN, z=LOWER_TOP)의
    #  평탄면 위에만 서고, 잔디 뱅크(x -0.05..5.10, |y|>3.55)에는 얹지 않는다.
    #
    #  [카메라 검산 — build_views() 8+4컷, FOV 수평 ±30°/수직 ±18° 가정]
    #   grid eye(-2/-5/-10, 0, h) +X · approach eye(-7,0,1.65) az 0 ·
    #   grazing_mirror eye(-2.4,0,0.32) az 0(수직 -27.1..+8.9°) ·
    #   film_closeup eye(-0.8,-1.2,0.75) az 23.6(프레임 -6.4..53.6) ·
    #   lower_lookback eye(8.5,1.0,1.5) az 186.0(프레임 156..216)
    #   원칙 ① 카메라 eye 반경 1.5 m 내 신규 솔리드 금지
    #        ② **하부 광장 소품은 전부 x>5.5 → 계단(x 0..4.9)보다 멀어
    #           경면 병합 특색을 가릴 수 없다**(가림 불가 증명)
    #        ③ 수직 요소(가로등·게양대·주두)는 젖은 노면 반사에 걸리도록
    #           grazing_mirror/approach 프레임 안(az |·|<30°)에 배치
    # ───────────────────────────────────────────────────────────────────────
    # 대형 화분 쌍 2조 — 상부는 계단 어깨(lookback az 159.6°), 하부는 계단
    #   발치 좌우(grazing az ±25.5° · approach ±14.7°)에서 계단을 액자화.
    #   상부 화분(x -2.1..-0.3)은 기존 볼라드(x -2.68..-2.52)와 0.42 m 이격.
    planters=[dict(cx=-1.2, cy=4.6, size=1.8, base="upper"),
              dict(cx=-1.2, cy=-4.6, size=1.8, base="upper"),
              dict(cx=6.6, cy=4.3, size=2.0, base="lower"),
              dict(cx=6.6, cy=-4.3, size=2.0, base="lower")],
    planter=dict(curb_h=0.52, curb_t=0.22, cap_over=0.05, cap_h=0.06,
                 soil_h=0.44, shrub_r=0.42),
    # 가로등 4본 — 하부 광장 좌우 2쌍. 젖은 포장 경면에 수직 반사를 만든다.
    #   (9.2,±4.8) / (15.0,±4.8): 화분(x 5.6..7.6)·조형물(x 10.8..13.2)과 비중첩.
    #   lower_lookback 에서는 az 79.6°(프레임 밖) → 근접 가림 없음.
    plazalamps=[dict(cx=9.2, cy=4.8, base="lower"),
                dict(cx=9.2, cy=-4.8, base="lower"),
                dict(cx=15.0, cy=4.8, base="lower"),
                dict(cx=15.0, cy=-4.8, base="lower"),
                dict(cx=-3.5, cy=5.6, base="upper"),
                dict(cx=-3.5, cy=-5.6, base="upper")],
    plazalamp=dict(pole_r=0.075, pole_h=4.60, base_r=0.16, base_h=0.45,
                   head_r=0.24, head_h=0.30),
    # 국기게양대 3본 + 화강암 기단 — 상부 광장 +Y. lower_lookback 전용
    #   (프레임 +Y 한계: x=-8 에서 y≤8.35 → 5.8/7.0 in, 8.2 경계).
    #   정면 시점(approach/grazing/grid)에서는 전부 프레임 밖 = 특색 무간섭.
    flag=dict(cx=-8.0, cys=(5.8, 7.0, 8.2), pole_r=0.055, pole_h=8.0,
              finial_r=0.09, plinth_pad=0.75, plinth_h=0.35),
    # 조형물 기단 + 모놀리스 — 하부 광장 +Y. grazing_mirror az 20.9°,
    #   approach az 16.1° 로 **전체가 프레임 안**(원경 파사드 앞 실루엣).
    sculpture=dict(cx=12.0, cy=5.5, plinth=2.4, plinth_h=0.55,
                   mono_w=0.85, mono_h=3.20, base="lower"),
    # 원경 열주(콜로네이드) — 건물 C 파사드(x=28) 앞 0.2 m 이격.
    #   civic 파사드 폭 확장 지시의 "열주 힌트". 전부 x≥25.4 원경.
    colonnade=dict(x_c=26.6, y0=-9.6, y1=9.6, step=2.4, col_r=0.42,
                   col_h=6.60, sty_x0=25.4, sty_x1=27.8, sty_pad=1.9,
                   sty_h=0.50, beam_t=0.90, beam_pad=0.6, base="lower"),

    material=dict(
        scale=dict(granite_dark=1.2, stone_flag=0.9, grass=4.0,
                   brick_red=2.0, tactile=0.3),
        grass_tint=(0.42, 0.52, 0.34),      # 비 맞은 잔디 — 표준 톤보다 어둡게
        water_color=(0.03, 0.05, 0.06), water_rough=0.02, water_spec=1.0,
        dry_rough_hint=0.55,                # 건조 대응쌍(텍스처 러프니스 사용)
        rail_color=(0.78, 0.80, 0.83), rail_metallic=0.9, rail_rough=0.30,
        # 볼라드 v5.1 상단 반사띠(백색, 소면적). 몸통은 rail 재질 공유.
        bollard_band_color=(0.88, 0.88, 0.86),
        wall_tint=(0.86, 0.86, 0.88),
        glass_color=(0.05, 0.07, 0.10), glass_rough=0.12,
        parapet_color=(0.84, 0.85, 0.86), parapet_rough=0.7,
        # ─ 비 패키지 v2 / 맥락 v2 상수 (sRGB 암색 규약 0.02~0.09) ─
        tide_color=(0.062, 0.066, 0.078), tide_rough=0.22, tide_spec=0.9,
        shrub_color=(0.032, 0.050, 0.030),
    ),

    # ─── overcast 조명 프로파일 (sceneC1 과 동일) ────────────────────────
    #  · hdri=sc.OVERCAST_HDRI : 경면이 반사할 균질한 흐린 하늘.
    #  · lookfix=False         : lookfix는 "태양 캡 + 지평 리프트"용. 무태양
    #                            HDRI에는 무의미하므로 원본 사용.
    #  · noon_sun_enable=False : 보조 DistantLight 비가시 → 경질 그림자 제거.
    #                            (setup_lighting 이 intensity/color 키를 항상
    #                             읽으므로 키 자체는 남겨 둔다.)
    #  · dome_intensity        : 직달 2450 을 잃은 만큼 상향. 기존 noon 1000
    #                            기준 1500~2500 스윕 권장. 시작값 2000
    #                            (sceneC1 과 동일값으로 시작 — 화강암은 눈보다
    #                             어두우므로 어두우면 2400 쪽으로 올린다).
    #  · hdri_sun_rotz_offset  : 무태양이라 무의미 → 0.0.
    # ────────────────────────────────────────────────────────────────────
    light=dict(
        hdri=sc.OVERCAST_HDRI,
        # r1: 2000→1500 과노출 완화 / [비 패키지 v2] 1500→1150 소나기 직후
        #   어둑함. lookfix=False · 무태양 프로파일은 그대로(특색 성립 조건).
        dome_intensity=1150.0,
        noon_dome_rot=-110.0,
        lookfix=False,
        noon_sun_enable=False, noon_sun_elev=49.79,
        noon_sun_intensity=600.0, noon_sun_color=(1.0, 0.985, 0.97),
        hdri_sun_rotz_offset=0.0,
        dome_rotation_step=15.0,
    ),
    # ─── SUN_AZ_OFFSET: 무태양 프로파일이라 그림자 방위 의미가 없다. 돔 Z회전은
    #     흐린 하늘의 완만한 휘도 구배(=경면에 비치는 밝기 분포)만 바꾼다.
    #     하네스 일관성을 위해 브리프 v3 §A-7 기본값 171.5 유지, [ ]키로 스윕. ─
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneC4")

ASSET_ROLES = ["granite_dark", "stone_flag", "grass", "brick_red", "tactile",
               "hdri", "mdl"]


# --- 파생 치수 (여러 빌더가 공유) -------------------------------------------
def _dims():
    st = PARAMS["stairs"]
    run = st["tread"] * st["nsteps"]
    drop = st["riser"] * st["nsteps"]
    slope_k = st["riser"] / st["tread"]          # 노징선 기울기 (하강 +X)
    return run, drop, slope_k


def bollard_points():
    """[v5.1 §2] 광장 진입부 볼라드 중심 [(name, x, y), ...] (간격 1.5 m)."""
    out = []
    sp = PARAMS["bollard"]["spacing"]
    for row in PARAMS["bollard_rows"]:
        for i, (bx, by) in enumerate(bc.bollard_line(
                row["x"], row["y0"], row["x"], row["y1"], spacing=sp)):
            out.append((f"{row['name']}{i}", bx, by))
    return out


def civic_placements():
    """[v5.1 §3] 화분·광장 가로등 위치 지터 (좌우 완전대칭 해소)."""
    pls = []
    for i, pd in enumerate(PARAMS["planters"]):
        dx, dy = bc.jit_pos(pd["cx"], pd["cy"], "plC4", amp=0.15)
        pls.append((i, pd["cx"] + dx, pd["cy"] + dy, pd))
    lms = []
    for i, ld in enumerate(PARAMS["plazalamps"]):
        dx, dy = bc.jit_pos(ld["cx"], ld["cy"], "lmC4", amp=0.18)
        lms.append((i, ld["cx"] + dx, ld["cy"] + dy, ld))
    return pls, lms


def build_views():
    """카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷. 중앙 난간 없음."""
    views = sc.grid_views(0.0)
    # approach: 상부 광장 보행 시점 — 광폭 계단 전경
    views["approach"] = dict(eye=[-7.0, 0.0, 1.65], tgt=[2.5, 0.0, -1.00])
    # grazing_mirror: 낮은 시점 — 하늘 반사로 단 에지가 병합되는가(특색 1순위)
    views["grazing_mirror"] = dict(eye=[-2.4, 0.0, 0.32], tgt=[4.6, 0.0, -0.80])
    # film_closeup: 수막 트레드 근접 — 경면에 하늘·건물이 비치는가
    views["film_closeup"] = dict(eye=[-0.8, -1.2, 0.75], tgt=[2.4, 0.20, -1.10])
    # lower_lookback: 하부에서 되돌아봄 — 젖은 라이저 대비 확인
    views["lower_lookback"] = dict(eye=[8.5, 1.0, 1.50], tgt=[-1.0, 0.0, 0.20])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 하늘 방위
[체크리스트]
 1. approach / grid    — 광폭 14단·상하 광장·측면 치크밴드 식별
 2. grazing_mirror·PT  — 트레드 경면이 하늘을 반사해 단 에지가 병합되는가(특색)
 3. film_closeup·PT    — 수막 4곳이 수평 거울면으로 읽히는가 (RT는 과소평가)
 4. wet ON vs OFF      — 건조 대응쌍에서 단 에지가 되살아나는가·기하 불변인가
 5. 조명               — 무태양 저대비인가(경질 그림자 0), 경면 하이라이트 점 없는가
 6. 재질·Z파이팅       — 젖음 박판 가장자리·수막·광장 이음에 깜빡임 없는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene28")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    wt = PARAMS["wet"]
    ROOT = "/World/Scene28"

    RUN, DROP, SLOPE_K = _dims()
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
    #   젖음 재질은 러프니스 텍스처를 **주지 않는다**: OmniPBR 은
    #   reflection_roughness_texture_influence=1.0 이면 상수를 무시하므로,
    #   경면(0.08)을 강제하려면 diff+nor 만 쓰고 상수 러프니스를 걸어야 한다.
    #   (건조 대응쌍은 러프니스 텍스처를 그대로 사용 = 원래의 석재 룩)
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        wet = cfg["wet_surface"]
        M = {}
        gd = ("granite_dark", sca["granite_dark"])
        sf = ("stone_flag", sca["stone_flag"])

        def stone(name, role_scale, rough, spec, tint):
            role, s = role_scale
            if wet:
                return PBR(f"{ROOT}/Looks/{name}", sc.tex_path(role, "diff"),
                           sc.tex_path(role, "nor"), None, s,
                           tint=tint, roughness_const=rough,
                           specular_level=spec, metallic=0.0)
            return PBR(f"{ROOT}/Looks/{name}", sc.tex_path(role, "diff"),
                       sc.tex_path(role, "nor"), sc.tex_path(role, "rough"),
                       s, metallic=0.0)

        # 트레드 젖음 박판(경면) / 단 솔리드·라이저(반건조) / 광장 포장
        M["tread_wet"] = stone("TreadWet", gd, wt["wet_rough"],
                               wt["wet_spec"], wt["wet_tint"])
        # [비 패키지 v2] 젖음 3단 tier — 건조 대응쌍에서는 stone() 이 텍스처
        #   러프니스 경로로 떨어져 3종이 모두 동일한 마른 석재가 된다(기하·룩
        #   양쪽 모두 대응쌍 정합 유지).
        for ti, td in enumerate(wt["patch_tiers"]):
            M[f"tread_p{ti}"] = stone(f"TreadP{td['name']}", gd, td["rough"],
                                      td["spec"], td["tint"])
        M["stone_damp"] = stone("StoneDamp", gd, wt["damp_rough"], None,
                                wt["damp_tint"])
        M["plaza"] = stone("Plaza", sf, wt["plaza_rough"], wt["plaza_spec"],
                           wt["plaza_tint"])
        M["cheek"] = stone("Cheek", gd, wt["damp_rough"], None,
                           wt["damp_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"], tint=mp["wall_tint"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        M["water"] = PBR(f"{ROOT}/Looks/Water",
                         diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0,
                         specular_level=mp["water_spec"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # 볼라드 v5.1 상단 백색 반사띠 — 본당 0.08 m² 로 소면적(v5.1 §4 준수)
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # [비 패키지 v2] tide mark · 웅덩이 다크닝 링 · 라이저 흘러내림 공용
        #   암색 젖음 재질 (sRGB 암색 규약 0.02~0.09 준수, 경면기 유지)
        M["tide"] = PBR(f"{ROOT}/Looks/Tide", diffuse_color=mp["tide_color"],
                        roughness_const=mp["tide_rough"], metallic=0.0,
                        specular_level=mp["tide_spec"])
        # [맥락 v2] 화분 관목 — 젖은 잎(암색 + 약한 스펙큘러)
        M["shrub"] = PBR(f"{ROOT}/Looks/Shrub", diffuse_color=mp["shrub_color"],
                         roughness_const=0.65, specular_level=0.5)
        return M

    # -------------------------------------------------------------------
    # 지형 — 상부 광장 / 하부 광장 / 치크밴드 / 잔디 사면
    #   개구(피트)가 없는 제방형이므로 4박스 분할 대상 없음. 네 솔리드가 서로
    #   겹치며 타일링 → 공동 위를 덮는 평면도, 부유 에지도 없다.
    # -------------------------------------------------------------------
    def build_upper(M):
        up = PARAMS["upper"]
        BOX(f"{ROOT}/UpperPlaza",
            ((up["x0"] + up["x1"]) / 2.0, (up["y0"] + up["y1"]) / 2.0,
             up["z_top"] - up["thick"] / 2.0),
            (up["x1"] - up["x0"], up["y1"] - up["y0"], up["thick"]),
            M["plaza"], col=True)

    def build_lower(M):
        lo = PARAMS["lower"]
        x0 = RUN - lo["x_back"]
        BOX(f"{ROOT}/LowerPlaza",
            ((x0 + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             LOWER_TOP - lo["thick"] / 2.0),
            (lo["x1"] - x0, lo["y1"] - lo["y0"], lo["thick"]),
            M["plaza"], col=True)

    def build_cheeks(M):
        """계단 측면 석재 치크밴드 — 상면 = 노징선 + proud."""
        ck = PARAMS["cheek"]
        x0 = -ck["x_head"]
        z0 = SLOPE_K * ck["x_head"] + ck["proud"]
        run = RUN + ck["x_head"] + ck["x_tail"]
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            a, b = sgn * ck["y_in"], sgn * ck["y_out"]
            sc.build_slope(stage, f"{ROOT}/Cheek_{tag}", x0, z0, run,
                           run * SLOPE_K, min(a, b), max(a, b), ck["thick"],
                           M["cheek"], margin=0.0, collider=True)

    def build_banks(M):
        """치크 바깥 잔디 사면 — 상면 = 노징선(추가 낙차 에지 없음)."""
        bk = PARAMS["bank"]
        x0 = -bk["x_head"]
        z0 = SLOPE_K * bk["x_head"]
        run = RUN + bk["x_head"] + bk["x_tail"]
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            a, b = sgn * bk["y_in"], sgn * bk["y_out"]
            sc.build_slope(stage, f"{ROOT}/Bank_{tag}", x0, z0, run,
                           run * SLOPE_K, min(a, b), max(a, b), bk["thick"],
                           M["grass"], margin=0.0, collider=True)

    def build_stairs(stair_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 전면 z=0 평지."""
        up = PARAMS["upper"]
        lo = PARAMS["lower"]
        x0, x1 = up["x0"], lo["x1"]
        BOX(f"{ROOT}/FlatFill",
            ((x0 + x1) / 2.0, (up["y0"] + up["y1"]) / 2.0,
             up["z_top"] - up["thick"] / 2.0),
            (x1 - x0, up["y1"] - up["y0"], up["thick"]),
            M["plaza"], col=True)

    # -------------------------------------------------------------------
    # 젖음 레이어 [특색] — 트레드 전용 박판 + 수막
    #   박판은 단 솔리드 안으로 파묻히고(x/y 로 3~5mm 내밀어) 상면만 proud
    #   3mm 로 노출 → 동일평면 없음. 재질만 경면(러프니스 0.08)이다.
    # -------------------------------------------------------------------
    def build_tread_films(M):
        """[비 패키지 v2] 트레드 젖음 박판을 **트레드 내 부분 폭 패치 3~5매**로
        분해한다. 기하 envelope(상면 proud 0.003 · 두께 0.012 · x ±3mm 오버)는
        불변이고 y 절단선만 고정 시드로 흩뿌려 '트레드 단위 젖음' 인상을 지운다.
        인접 패치는 patch_overlap(6mm) 겹치고 proud 를 patch_step(0.4mm)씩
        층지게(j%3) 해 겹침 구간에 동일평면(Z-파이팅)이 생기지 않는다.
        건조 대응쌍(wet_surface=False)에서는 3 tier 재질이 모두 동일한 마른
        석재로 떨어져 **기하·룩 양쪽 모두 대응쌍 정합**이 유지된다."""
        st = PARAMS["stairs"]
        ox, oy = wt["film_over_x"], wt["film_over_y"]
        y_lo, y_hi = st["y0"] - oy, st["y1"] + oy
        span = y_hi - y_lo
        rng = random.Random(int(wt["patch_seed"]))
        bias = float(wt["patch_bias"])
        n_patch = 0
        for i in range(1, st["nsteps"] + 1):
            xa = st["x0"] + st["tread"] * (i - 1) - ox
            xb = xa + st["tread"] + 2.0 * ox
            ztop = st["z_top"] - st["riser"] * i
            k = rng.randint(int(wt["patch_min"]), int(wt["patch_max"]))
            cuts = sorted(y_lo + span * (j / k)
                          + rng.uniform(-0.34, 0.34) * span / k
                          for j in range(1, k))
            edges = [y_lo] + cuts + [y_hi]
            for j in range(k):
                r = rng.random()
                ti = 0 if r < bias * 0.55 else (1 if r < bias else 2)
                ya = edges[j] - (wt["patch_overlap"] if j > 0 else 0.0)
                yb = edges[j + 1] + (wt["patch_overlap"] if j < k - 1 else 0.0)
                z_hi = ztop + wt["film_proud"] + (j % 3) * wt["patch_step"]
                z_lo = ztop - wt["film_t"]
                BOX(f"{ROOT}/WetFilm/T{i}_P{j}",
                    ((xa + xb) / 2.0, (ya + yb) / 2.0, (z_hi + z_lo) / 2.0),
                    (xb - xa, yb - ya, z_hi - z_lo), M[f"tread_p{ti}"])
                n_patch += 1
        print(f"[젖음] 트레드 패치 {n_patch}매 · tier "
              f"{len(wt['patch_tiers'])}단 (seed={wt['patch_seed']})")

    def build_water(M):
        """수막 — [비 패키지 v2] 사각 1매 → **불규칙 lobe 겹침 + 다크닝 링**.
        고정 시드(patch_seed+1). z 층위 규약:
          트레드 필름 상면 0.0030~0.0038 < 다크닝 링 0.0045~0.0051
          < 수면 0.0060~0.0068  → 3층 모두 동일평면 없음.
        트레드 웅덩이 lobe 는 회전 없이 x 인셋·y 분할만으로 윤곽을 들쭉날쭉하게
        만든다(회전 시 노징 밖으로 삐져나옴). 광장 시트는 제약이 없으므로
        _oriented_box rotZ 로 3매를 비스듬히 겹쳐 사각 윤곽을 지운다."""
        st = PARAMS["stairs"]
        ox = wt["film_over_x"]
        rng = random.Random(int(wt["patch_seed"]) + 1)
        k = 0
        for f in PARAMS["water_films"]:
            i = int(f["step"])
            x_lo = st["x0"] + st["tread"] * (i - 1) - ox     # 필름 앞끝
            x_hi = x_lo + st["tread"] + 2.0 * ox             # 필름 뒷끝
            xa = st["x0"] + st["tread"] * (i - 1) + 0.010
            xb = xa + st["tread"] - 0.030
            ztop = st["z_top"] - st["riser"] * i
            y0, y1 = f["y0"], f["y1"]
            ly = y1 - y0
            cuts = sorted(y0 + ly * (j / 3.0) + rng.uniform(-0.16, 0.16) * ly / 3.0
                          for j in (1, 2))
            edges = [y0] + cuts + [y1]
            for j in range(3):
                lx0 = xa + rng.uniform(0.0, 0.055)
                lx1 = xb - rng.uniform(0.0, 0.045)
                ly0 = edges[j] - (0.05 if j > 0 else 0.0)
                ly1 = edges[j + 1] + (0.05 if j < 2 else 0.0)
                # ① 다크닝 링(젖어 번진 둘레) — 트레드 필름 폭 안으로 클램프
                rx0 = max(x_lo + 0.002, lx0 - wt["ring_grow_x"])
                rx1 = min(x_hi - 0.002, lx1 + wt["ring_grow_x"])
                rz = ztop + wt["ring_proud"] + j * 0.0003
                BOX(f"{ROOT}/Water/Ring_{k}",
                    ((rx0 + rx1) / 2.0, (ly0 + ly1) / 2.0, rz - 0.005),
                    (rx1 - rx0, (ly1 - ly0) + 2.0 * wt["ring_grow_y"], 0.010),
                    M["tide"])
                # ② 수면 lobe
                sc.build_water(stage, f"{ROOT}/Water/Tread_{k}", lx0, ly0,
                               lx1, ly1,
                               ztop + wt["water_lift"] + j * 0.0004,
                               thick=wt["water_t"], mtl=M["water"])
                k += 1
        # 광장 시트 — 회전 lobe 3매(+링). 계단 회랑(x≥0)을 침범하지 않도록
        #   상부 시트 lobe 최대 x = −0.97 (검산치) 로 유지된다.
        lobes = ((0.82, 0.70, -0.06, 0.10, 9.0),
                 (0.66, 0.92, 0.14, -0.08, -13.0),
                 (0.90, 0.52, 0.02, 0.16, 4.0))
        for sh in PARAMS["water_sheets"]:
            base = LOWER_TOP if sh["where"] == "lower" else 0.0
            xs = RUN if sh["where"] == "lower" else 0.0
            x0, x1 = sh["x0"] + xs, sh["x1"] + xs
            cx0 = (x0 + x1) / 2.0
            cy0 = (sh["y0"] + sh["y1"]) / 2.0
            Lx, Ly = x1 - x0, sh["y1"] - sh["y0"]
            for j, (fx, fy, dx, dy, rz_deg) in enumerate(lobes):
                cx = cx0 + dx * Lx
                cy = cy0 + dy * Ly
                sc._oriented_box(
                    stage, f"{ROOT}/Water/RingSheet_{sh['name']}_{j}",
                    (cx, cy, base + 0.002 + j * 0.0003 - 0.005),
                    (Lx * fx + 0.22, Ly * fy + 0.22, 0.010), M["tide"],
                    rotz=rz_deg)
                sc._oriented_box(
                    stage, f"{ROOT}/Water/Sheet_{sh['name']}_{j}",
                    (cx, cy, base + 0.006 + j * 0.0004 - 0.005),
                    (Lx * fx, Ly * fy, 0.010), M["water"], rotz=rz_deg)

    # -------------------------------------------------------------------
    # [비 패키지 v2] tide mark(수위선) + 라이저 흘러내림 스트릭
    #   젖음의 "증거"이므로 wet_surface 토글에 종속 — 건조 대응쌍에서는
    #   생성하지 않는다(기하 대응쌍 정합은 계단 본체·필름이 담당).
    # -------------------------------------------------------------------
    def build_rain_marks(M):
        st = PARAMS["stairs"]
        ck = PARAMS["cheek"]
        th = wt["tide_h"]
        x0 = -ck["x_head"]
        run = RUN + ck["x_head"] + ck["x_tail"]
        z_ck = SLOPE_K * ck["x_head"] + ck["proud"]      # x=x0 에서 치크 상면
        # ① 치크밴드 **상면 러노프 스트라이프** — 계단쪽 안쪽 모서리를 따라
        #    물이 흘러내린 암색 젖은 띠. proud 3mm(규약 내), 폭 0.24.
        #    치크 상면은 노징선 +0.06 이라 잔디 뱅크 위로 노출된 유일한 넓은
        #    경사면 → approach az 23.2° · grazing az 22.3° 로 프레임 안.
#    y 3.02..3.26 : 계단 측면(±3.00) 바깥 · 치크(2.94..3.60) 안쪽
#    → 노징 지점에서도 판이 치크 솔리드에 물려 부유 슬릿이 없다.
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            a = sgn * (ck["y_in"] + wt["runoff_in"])
            b = sgn * (ck["y_in"] + wt["runoff_in"] + wt["runoff_w"])
            sc.build_slope(stage, f"{ROOT}/Tide/Runoff_{tag}", x0,
                           z_ck + wt["runoff_proud"], run, run * SLOPE_K,
                           min(a, b), max(a, b), wt["runoff_t"], M["tide"],
                           margin=0.0, collider=False)
        # ② 치크밴드 외측면 tide — 잔디 뱅크 위로 노출된 0.10 만 밴드로.
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            a = sgn * (ck["y_out"] - 0.002)
            b = sgn * (ck["y_out"] + wt["tide_proud"])
            sc.build_slope(stage, f"{ROOT}/Tide/Cheek_{tag}", x0,
                           z_ck - wt["tide_drop"], run, run * SLOPE_K,
                           min(a, b), max(a, b), wt["tide_h_cheek"],
                           M["tide"], margin=0.0, collider=False)
        # ③ 원경 파사드 기부 tide — 건물 C 파사드(x=28) 하단 밴드
        bC = PARAMS["buildings"]["C"]
        BOX(f"{ROOT}/Tide/FacadeC",
            (bC["facade_x"] - 0.012, (bC["y0"] + bC["y1"]) / 2.0,
             LOWER_TOP + th / 2.0),
            (0.030, bC["y1"] - bC["y0"], th), M["tide"])
        # ④ 라이저 흘러내림 스트릭 — 라이저 수직면에서 3mm 돌출한 세로 띠.
        #    proud 를 k%3 로 층지게 해 같은 단에서 겹쳐도 동일평면 없음.
        rng = random.Random(int(wt["streak_seed"]))
        for k in range(int(wt["streak_n"])):
            i = rng.randint(2, st["nsteps"] - 1)
            y = rng.uniform(st["y0"] + 0.25, st["y1"] - 0.25)
            xa = st["x0"] + st["tread"] * (i - 1)
            zt = st["z_top"] - st["riser"] * i
            z_lo = zt + 0.005                    # 트레드 필름과 이격
            z_hi = zt + st["riser"] - 0.025      # 윗단 필름 밑면과 이격
            pr = wt["streak_proud"] + (k % 3) * 0.0005
            w = wt["streak_w"] * rng.uniform(0.55, 1.45)
            BOX(f"{ROOT}/Tide/Streak_{k}",
                (xa + (0.020 - pr) / 2.0, y, (z_lo + z_hi) / 2.0),
                (0.020 + pr, w, z_hi - z_lo), M["tide"])
        print(f"[비] 치크 러노프 2 · 치크 tide 2 · 파사드 tide 1 · "
              f"라이저 스트릭 {int(wt['streak_n'])}줄 "
              f"(seed={wt['streak_seed']})")

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
            ck = PARAMS["cheek"]

            def cheek_ground(x):
                """포스트 착지면: x<=0 은 상부 광장 상면, x>0 은 치크밴드 상면.
                (치크밴드는 계단 구간에만 있으므로 수평 연장부 포스트는 광장에
                 착지 — 그 결과 레일 상면은 치크밴드보다 proud 만큼 낮은
                 0.84m, 광장 기준으로는 규정 0.9m 가 된다.)"""
                if x <= 0.0:
                    return 0.0
                return ck["proud"] - SLOPE_K * min(x, RUN)

            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                sc.build_railing_line(
                    stage, f"{ROOT}/StairRail_{tag}", sgn * rl["y"],
                    rl["x_start"], st["x0"], RUN, DROP, cheek_ground,
                    M["rail"], rail_h=rl["rail_h"], post_r=rl["post_r"],
                    spacing=rl["spacing"], rail_r=rl["rail_r"],
                    rail_mid_r=rl["rail_mid_r"],
                    rail_mid_drop=rl["rail_mid_drop"])

    # -------------------------------------------------------------------
    # 드레싱 — 볼라드 4 + 원경 건물 2동(지평선 폐쇄 §A-4)
    # -------------------------------------------------------------------
    def build_dressing(M):
        # 볼라드 [v5.1 §2] — 광장 진입부 1열(중앙 5.6 m 개구), 반사띠 +
        #   전면(−X) 점형블록. 점형블록은 젖음 틴트 미적용(수막 시트 밖).
        bo = PARAMS["bollard"]
        for name, bx, by in bollard_points():
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{name}", bx, by, 0.0,
                                 None, M["rail"], M["bollard_band"],
                                 M["tactile"], front_dir=bo["front"],
                                 radius=bo["radius"], height=bo["height"])
        low_base = LOWER_TOP if cfg["hazard_stairs"] else 0.0
        for key, bd in PARAMS["buildings"].items():
            b = dict(bd)
            # level="lower"(하부 광장 기단) / "upper"(상부 광장 기단)
            b["base_z"] = low_base if bd.get("level", "upper") == "lower" \
                else 0.0
            sc.build_building(stage, f"{ROOT}/Building_{key}", b,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        build_civic(M)

    # -------------------------------------------------------------------
    # 맥락 드레싱 v2 — 관공서/문화시설 앞 대계단의 장소성
    #   화분 쌍 · 광장 가로등 · 국기게양대 · 조형물 · 원경 열주.
    #   전 요소가 평탄면(상부 광장 z=0 / 하부 광장 z=LOWER_TOP) 위에 서며,
    #   하부 소품은 전부 x>5.5 → 계단(x 0..4.9)보다 원거리 = 특색 무가림.
    #   수직 요소(가로등·게양대·주두)는 젖은 포장 경면 반사에 걸리도록
    #   grazing_mirror/approach 프레임 안에 배치했다.
    # -------------------------------------------------------------------
    def build_civic(M):
        wet = cfg["wet_surface"]
        low = LOWER_TOP if cfg["hazard_stairs"] else 0.0

        def base_of(kind):
            return low if kind == "lower" else 0.0

        def tide_band(path, cx, cy, sx, sy, z_base):
            """[비 패키지] 수직 구조물 기부 젖음 밴드(proud 12mm)."""
            if not wet:
                return
            h = wt["tide_h"] * 0.8
            BOX(path, (cx, cy, z_base + h / 2.0),
                (sx + 2.0 * wt["tide_proud"], sy + 2.0 * wt["tide_proud"], h),
                M["tide"])

        # ① 대형 화분 쌍 (경계석 + 캡 + 식재 + 관목 3구)
        pl = PARAMS["planter"]
        _pls, _lms = civic_placements()                # v5.1 §3 배치 지터
        for i, pcx, pcy, pd in _pls:
            bz = base_of(pd["base"])
            pfx = f"{ROOT}/Planter_{i}"
            sc.build_planter(stage, pfx, pcx, pcy, bz,
                             M["cheek"], M["shrub"], tree_mtls=None,
                             size=pd["size"], curb_h=pl["curb_h"],
                             curb_t=pl["curb_t"], cap_over=pl["cap_over"],
                             cap_h=pl["cap_h"], grass_h=pl["soil_h"])
            r = pl["shrub_r"] * (pd["size"] / 2.0)
            for j, (dx, dy, s) in enumerate(((0.0, 0.0, 1.0),
                                             (0.26, -0.20, 0.78),
                                             (-0.24, 0.22, 0.72))):
                sc.add_sphere(stage, f"{pfx}/Shrub_{j}",
                              (pcx + dx * pd["size"] * 0.5,
                               pcy + dy * pd["size"] * 0.5,
                               bz + pl["soil_h"] + r * s * 0.45),
                              (r * s, r * s, r * s * 0.72), M["shrub"])
            tide_band(f"{pfx}/Tide", pcx, pcy, pd["size"],
                      pd["size"], bz)

        # ② 광장 가로등 — 젖은 포장에 수직 반사를 만드는 핵심 요소
        lm = PARAMS["plazalamp"]
        for i, lcx, lcy, ld in _lms:
            bz = base_of(ld["base"])
            pfx = f"{ROOT}/PlazaLamp_{i}"
            CYL(f"{pfx}/Base", (lcx, lcy, bz + lm["base_h"] / 2.0),
                lm["base_r"], lm["base_h"], M["cheek"], col=True)
            CYL(f"{pfx}/Pole",
                (lcx, lcy, bz + lm["pole_h"] / 2.0 + 0.20),
                lm["pole_r"], lm["pole_h"], M["rail"], col=True)
            CYL(f"{pfx}/Head",
                (lcx, lcy,
                 bz + lm["pole_h"] + 0.20 + lm["head_h"] / 2.0 - 0.04),
                lm["head_r"], lm["head_h"], M["parapet"])
            tide_band(f"{pfx}/Tide", lcx, lcy, lm["base_r"] * 2.0,
                      lm["base_r"] * 2.0, bz)

        # ③ 국기게양대 3본 + 화강암 기단 (상부 광장 +Y · lookback 전용)
        fl = PARAMS["flag"]
        cy_mid = sum(fl["cys"]) / len(fl["cys"])
        py = (max(fl["cys"]) - min(fl["cys"])) + 2.0 * fl["plinth_pad"]
        BOX(f"{ROOT}/Flag/Plinth",
            (fl["cx"], cy_mid, fl["plinth_h"] / 2.0),
            (2.0 * fl["plinth_pad"], py, fl["plinth_h"]), M["cheek"], col=True)
        for i, fy in enumerate(fl["cys"]):
            CYL(f"{ROOT}/Flag/Pole_{i}",
                (fl["cx"], fy, fl["plinth_h"] + fl["pole_h"] / 2.0 - 0.10),
                fl["pole_r"], fl["pole_h"], M["rail"], col=True)
            sc.add_sphere(stage, f"{ROOT}/Flag/Finial_{i}",
                          (fl["cx"], fy,
                           fl["plinth_h"] + fl["pole_h"] - 0.10
                           + fl["finial_r"]),
                          (fl["finial_r"],) * 3, M["parapet"])
        tide_band(f"{ROOT}/Flag/Tide", fl["cx"], cy_mid,
                  2.0 * fl["plinth_pad"], py, 0.0)

        # ④ 조형물 기단 + 모놀리스 (하부 광장 +Y · grazing/approach 프레임 안)
        sp = PARAMS["sculpture"]
        bz = base_of(sp["base"])
        BOX(f"{ROOT}/Sculpture/Plinth",
            (sp["cx"], sp["cy"], bz + sp["plinth_h"] / 2.0),
            (sp["plinth"], sp["plinth"], sp["plinth_h"]), M["cheek"], col=True)
        BOX(f"{ROOT}/Sculpture/Mono",
            (sp["cx"], sp["cy"],
             bz + sp["plinth_h"] + sp["mono_h"] / 2.0 - 0.05),
            (sp["mono_w"], sp["mono_w"], sp["mono_h"]), M["plaza"], col=True)
        tide_band(f"{ROOT}/Sculpture/Tide", sp["cx"], sp["cy"], sp["plinth"],
                  sp["plinth"], bz)

        # ⑤ 원경 열주 — 기단(스타일로베이트) + 원주 열 + 엔타블러처
        co = PARAMS["colonnade"]
        bz = base_of(co["base"])
        sty_cx = (co["sty_x0"] + co["sty_x1"]) / 2.0
        sty_y0 = co["y0"] - co["sty_pad"]
        sty_y1 = co["y1"] + co["sty_pad"]
        BOX(f"{ROOT}/Colonnade/Stylobate",
            (sty_cx, (sty_y0 + sty_y1) / 2.0, bz + co["sty_h"] / 2.0),
            (co["sty_x1"] - co["sty_x0"], sty_y1 - sty_y0, co["sty_h"]),
            M["plaza"], col=True)
        n_col = int(round((co["y1"] - co["y0"]) / co["step"])) + 1
        z_col = bz + co["sty_h"]
        for i in range(n_col):
            cyc = co["y0"] + co["step"] * i
            CYL(f"{ROOT}/Colonnade/Col_{i}",
                (co["x_c"], cyc, z_col + co["col_h"] / 2.0 - 0.05),
                co["col_r"], co["col_h"], M["plaza"], col=True)
        BOX(f"{ROOT}/Colonnade/Beam",
            (co["x_c"], (co["y0"] + co["y1"]) / 2.0,
             z_col + co["col_h"] + co["beam_t"] / 2.0 - 0.10),
            (co["col_r"] * 3.4, (co["y1"] - co["y0"]) + 2.0 * co["beam_pad"],
             co["beam_t"]), M["parapet"])
        if wet:
            BOX(f"{ROOT}/Colonnade/Tide",
                (sty_cx, (sty_y0 + sty_y1) / 2.0, bz + co["sty_h"] * 0.55),
                (co["sty_x1"] - co["sty_x0"] + 2.0 * wt["tide_proud"],
                 sty_y1 - sty_y0 + 2.0 * wt["tide_proud"], co["sty_h"] * 0.9),
                M["tide"])
        print(f"[드레싱] 화분 {len(PARAMS['planters'])} · 가로등 "
              f"{len(PARAMS['plazalamps'])} · 게양대 {len(fl['cys'])} · "
              f"조형물 1 · 열주 {n_col}주 · 파사드 "
              f"{len(PARAMS['buildings'])}동")

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["stone_damp"] if cfg["cue_material_break"] else M["plaza"]

    if cfg["hazard_stairs"]:
        build_upper(M)
        build_lower(M)
        build_banks(M)
        build_cheeks(M)
        build_stairs(stair_mtl)
        build_tread_films(M)          # 기하는 항상 동일 — 재질만 젖음/건조
        build_cues(M)
        if cfg["wet_surface"]:
            build_water(M)
            build_rain_marks(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    print(f"[기하] run={RUN:.2f}m drop={DROP:.2f}m slope_k={SLOPE_K:.4f} "
          f"lower_top={LOWER_TOP:.3f} wet={cfg['wet_surface']} "
          f"rough={wt['wet_rough'] if cfg['wet_surface'] else 'tex'}")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneC4 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneC4_{ts}.png")
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
