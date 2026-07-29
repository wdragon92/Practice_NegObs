# -*- coding: utf-8 -*-
"""
sceneC2_leaf_stairs.py — NegObs 인공씬 27호: 낙엽 매몰 석계단 (Isaac Sim 4.5)

유형    : C2 조건 변주 (기하 불변 · 환경 레이어로 cue 매몰)
사양서  : Docs/nanobanana_batch1_geometry_map.md §B sceneC2_leaf_stairs
          Docs/multi_scene_brief_v3.md §A 회귀 방지 체크리스트
공통    : scene_common.py · 골격 관례 scene16_canopy_shadow.py
룩 참조 : look_refs/c2_leaf_stairs.jpg (생성 이미지는 하부 시점 — **구현은
          프롬프트 의도대로 상부 접근로 시점·상단 3단 매몰**)

위험 본질: 공원 석계단 14단이 상부 접근로에서 +X로 하강한다. 두꺼운 낙엽층이
           **첫 3단을 완전히 매몰**해 계단 시작 에지(낙차 경계)가 소실되고,
           낙엽 마운드의 마루선(x≈-0.25, z≈+0.20)이 그 너머를 전부 가린다.
           4~6단은 중앙만 부분 매몰(점진 노출), 7단 이하만 온전히 노출된다.
           **하강이 계속된다는 유일한 단서 = 편측 난간 1선의 하강 사선.**
목표     : 상부 접근로 + 석계단(+양측 경계석) + 낙엽 2단 레이어(매몰 마운드 +
           근경 산포) + 난간 1선 + 측면 잔디 사면·가을 수목을 조립, 렌더 판정.
GT       : 계단 낙차 양성(기하 불변, drop 2.24 m). cue 매몰 극한 케이스.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneC2_leaf_stairs.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneC2_leaf_stairs.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneC2_leaf_stairs.py

좌표계: Z-up, m, 진행축 +X, 낙차 시작 모서리 = x=0 (계단 상단 = 접근로 어깨).

────────────────────────────────────────────────────────────────────────────
기하 핵심 (수치 검산 — 감독 재검산용)
  riser 0.16 · tread 0.34 · n 14  → run 4.76 · drop 2.24 (z_bot −2.24)
  단코선  z(x) = −(riser/tread)·x = −0.4706·x
  경계석  상면 = 단코선 + 0.12 (양측 y 1.28..1.62, 좌우 대칭)
  낙엽 마운드 3매 (build_slope = rotateY 경사 박스):
    A 접근로 카펫 : x −3.20..−0.10, 상면 +0.06 → +0.13 (역경사 = 에지 퇴적)
    B 매몰 램프   : x −0.25.. 1.02, 상면 +0.20 → −0.390 (기울기 0.4643 < 0.4706)
                    → 단1~3 상면(−0.16/−0.32/−0.48) 대비 상시 +0.086~0.090 피복
                    → **x=0 에서 낙엽면 +0.084 = 접근로(0)보다 높은 마루** ⇒
                      계단 시작 에지가 기하학적으로 시선에서 사라짐
    C 점이 램프   : x  1.02.. 2.38, 상면이 단코선보다 0.03~0.06 아래로 추종,
                    폭 y ±0.90(중앙만) → 단4~7 트레드 오목부 **중앙만** 메워
                    단코 모서리·양 끝 0.4m 는 노출(점진 노출), 단8 이하 완전 노출
  * 사양의 "_oriented_box 경사판"은 rotY(+X 하강 경사)를 요구하나 _oriented_box는
    rotZ/rotX 만 지원 → 동일 목적의 sc.build_slope(rotateY 경사 박스)로 구현.
    _oriented_box 는 **rotX(횡단 크라운)** 이 필요한 측면 낙엽 드리프트 2매에 사용.
────────────────────────────────────────────────────────────────────────────
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
# [A] SCENE_CONFIG — 표준 7키 + 씬 특색 1키(leaf_cover)
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 계단·사면을 z=0 평지로 (기하 토글)
    "cue_railing":        True,    # **편측 난간 1선** — 매몰 구간 유일 단서(정체성)
    "cue_tactile":        False,   # 공원 석계단엔 미관행(코드 경로만)
    "cue_material_break": True,    # 접근로 흙길 vs 석계단 재질 대비
    "cue_nosing":         False,   # 공원 마모석엔 논슬립 띠 미관행(코드 경로만)
    "cue_sign":           False,   # [선택] 미구현 — 키만 예약
    "cue_scene_dressing": True,    # 가을 수목·생울타리·원경 능선 일괄
    # ─ 특색 토글: False → 낙엽 마운드·산포 전부 제거 = 동일 기하 대응쌍 ─
    "leaf_cover":         True,
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- 석계단 14단 (riser 0.16 · tread 0.34 → run 4.76 · drop 2.24) ---
    stairs=dict(x0=0.0, riser=0.16, tread=0.34, nsteps=14,
                y0=-1.30, y1=1.30, z_top=0.0, base_z=-3.30),
    # --- 양측 경계석(석재 코핑) : 단코선 위 0.12, y 1.28..1.62 ---
    coping=dict(y_in=1.28, y_out=1.62, rise=0.12, ext=0.25, thick=0.55),
    # --- 상부 접근로 (흙길) : x −20 .. +0.02 (계단과 0.02 겹침 = 단1 라이저) ---
    upper=dict(x0=-20.0, x1=0.02, y_half=1.62, z_top=0.0, thick=0.60),
    # --- 하부 진입로 : 계단 밑으로 1.0 언더랩 + 상면 0.002 침하(동일평면 금지) ---
    # x_pad 46 : 원경 능선(RUN+24 / RUN+33, 두께 6~8)까지 지면이 이어져야
    #            능선 기부 부유·지면 끝 허공이 안 생긴다(브리프 §A-4)
    lower=dict(x_pad=46.0, under_lap=1.0, y_half=1.62, sink=0.002, thick=0.60),
    # --- 측면 잔디 사면 (계단 회랑 y ±1.58 비움, 상면 0.005 침하) ---
    slopes=dict(y_in=1.58, y_edge=40.0, thick=0.80, sink=0.005),
    # --- 지면 평판 (사면 바깥 상·하부) ---
    ground=dict(y_edge=40.0, thick=0.60),

    # --- 낙엽 ① 매몰 마운드 (build_slope 경사판 3매) ---
    #     dict(x0, z0, run, drop, y_half, thick) — 상면 = (x0,z0)→(x0+run, z0−drop)
    mound=[
        # A 접근로 카펫: 상면 +0.06 → +0.13 (역경사 drop<0 = 에지 퇴적).
        #   밑면 −0.09..−0.02 → 접근로(z=0)에 매입, 부유 없음.
        dict(name="A", x0=-3.20, z0=0.06, run=3.10, drop=-0.07,
             y_half=2.40, thick=0.15),
        # B 매몰 램프: 마루 x=−0.25(z=+0.20) → x=+1.02(z=−0.390) = **단3 후단**.
        #   기울기 0.4643 < 단코선 0.4706 → 단1~3 상면을 상시 +0.086~0.090 피복.
        #   종단(x=1.02)에서 밑면 −0.540 < 단3 상면 −0.48 → 판이 계단 솔리드에
        #   매입되어 끝난다 ⇒ 트레드별 내부 포켓(판 밑면과 트레드 사이 ~9cm)이
        #   **상류=마운드A / 하류=B 매입부 / 좌우=경계석(y1.28~1.62, B는 ±1.33)**
        #   로 완전 밀폐 — 광 누출·가시 슬릿 없음. 노출되는 것은 낙엽층 종단면
        #   (h≈0.115~0.15)뿐이며 이는 실제 낙엽 둑 에지 룩과 일치.
        dict(name="B", x0=-0.25, z0=0.20, run=1.27, drop=0.5897,
             y_half=1.33, thick=0.15),
        # C 점이 램프: 상면이 단코선(−0.4706x)보다 0.03~0.06 낮게 추종
        #   → 트레드 오목부만 메우고 **단코 모서리는 노출**(점진 노출 구간).
        #   끝(x=2.38)에서 단7 솔리드 내부로 잠겨 끝면 노출 없음.
        dict(name="C", x0=1.02, z0=-0.505, run=1.36, drop=0.675,
             y_half=0.90, thick=0.15),
    ],
    # --- 낙엽 ①' 측면 드리프트 (_oriented_box rotX = 횡단 크라운) ---
    drift=[dict(name="N", sgn=1.0), dict(name="S", sgn=-1.0)],
    #   상부 평탄부(x −3.40..−0.10, z=0)에만 배치 — 경사 구간에 걸치면 부유.
    #   rotX 부호는 **회랑쪽(안쪽) 모서리가 높아지도록** 코드에서 −sgn 적용:
    #   상면 z 0.012~0.108, 밑면 최대 −0.012 → 전 폭 지면 매입(부유 없음).
    drift_geo=dict(cx=-1.75, len_x=3.30, cy=1.95, len_y=1.10, center_z=0.0,
                   thick=0.12, rotx=5.0),
    # --- 낙엽 ② 근경 산포 (납작 타원체) — count 로 렌더 비용 조절 ---
    leaf_scatter=dict(count=900, seed=2702,
                      scale=(0.038, 0.028, 0.006), jitter=(0.75, 1.30),  # r1: 팬케이크화 → 축소
                      x0=-4.20, x_pad=3.00, y_wide=3.60, y_band=1.70,
                      band_frac=0.70, lift=0.006,
                      # 실물 USD 산포(룩v1) — 근경 밴드만. cover 는 목표 피복률.
                      cover=0.55, y_near=2.20, x_pad_near=1.50, max_count=900,
                      # ── [W2] G2 leaf globalisation (leaf_globalization_budget_v2 §6-a) ──
                      # The old near-band stopped at x −4.20, which leaves 69.0 %
                      # of the h0.3_d10 lower frame as bare dirt [measured]: the
                      # upstream rect must start BEHIND the farthest preset eye
                      # (x −10.0), hence −10.60. Non-overlapping 5-way split;
                      # inhomogeneity comes from splitting rects and varying
                      # `cover`, never from `edge_bias` (which silently
                      # under-covers — it drops interior samples after n is
                      # fixed and never compensates, §3-e-1).
                      # `max_count` is a truncation guard only, set at ~1.15n.
                      # Rect 1 widened to |y| 2.60 (was 2.20) so mound A (2.40)
                      # and drift (2.50) keep a 0.10 m margin — kills the
                      # texture fringe of §4.
                      g2=[
                          dict(tag="core",  x0=-4.20, x1=6.26, y0=-2.60, y1=2.60,
                               cover=0.55, max_count=1150),
                          dict(tag="up",    x0=-10.60, x1=-4.20, y0=-3.60, y1=3.60,
                               cover=0.32, max_count=470),
                          dict(tag="sideN", x0=-4.20, x1=6.26, y0=2.60, y1=3.60,
                               cover=0.32, max_count=110),
                          dict(tag="sideS", x0=-4.20, x1=6.26, y0=-3.60, y1=-2.60,
                               cover=0.32, max_count=110),
                          dict(tag="down",  x0=6.26, x1=7.76, y0=-3.60, y1=3.60,
                               cover=0.32, max_count=110),
                      ]),

    # --- cue ---
    rail=dict(y=1.45, x_start=-1.60, rail_h=0.90, post_r=0.022,
              rail_r=0.028, rail_mid_r=0.018, rail_mid_drop=0.42,
              spacing=1.20),
    nosing=dict(color=(0.80, 0.76, 0.62), width=0.05, proud=0.001),
    tactile=dict(ahead=0.35, depth=0.35, proud=0.004),

    # --- 드레싱 / 지평 폐쇄 ---
    trees=[dict(cx=-6.0, cy=5.5, where="upper"),
           dict(cx=-11.0, cy=-6.5, where="upper"),
           dict(cx=3.0, cy=7.5, where="lower"),
           dict(cx=8.0, cy=-6.0, where="lower"),
           dict(cx=14.0, cy=5.0, where="lower"),
           dict(cx=19.0, cy=-8.0, where="lower")],
    back_hedge=dict(cx=-15.0, sx=1.4, length=24.0, h=1.7),
    back_hedges=[dict(cy=-20.0), dict(cy=4.0), dict(cy=26.0)],
    far_hedge=dict(sx=1.4, length=26.0, h=1.8, x_pad=17.0),
    far_hedges=[dict(cy=-24.0), dict(cy=0.0), dict(cy=24.0)],
    # sy 76 (= y ±38) : 대지 y ±40 안쪽 — 능선 끝이 지면 밖으로 나가지 않게
    ridge=[dict(x_pad=24.0, h=5.0, sy=76.0, t=6.0),
           dict(x_pad=33.0, h=7.5, sy=76.0, t=8.0)],

    # ═══ [맥락 드레싱 v2 · 07-27] "여기가 공원이다"가 읽히는 소품 레이어 ═══
    #  감사 v4 통합계획 §휑함 대응. 계단·경계석·낙엽 레이어(마운드/드리프트/
    #  산포)·난간·조명은 일절 불변이며, 신규 프림은 상부 접근로 옆 잔디(x<0,
    #  z=0)와 하부 진입로 옆 잔디(x>RUN, z=Z_BOT) 평탄면 위에만 선다.
    #  where="upper" → 절대 x, "lower" → RUN + cx (기존 trees 관례 그대로).
    #
    #  [카메라 검산 — build_views() 8+4컷, FOV 수평 ±30°/수직 ±18° 가정]
    #   grid eye(-2/-5/-10, 0, h) +X (계단 방위 밴드 ±7.4° @d10) ·
    #   approach_walk eye(-4,0,1.55) az 0 · buried_edge eye(-1.7,0.2,0.35) az -1.9 ·
    #   rail_cue eye(-2.4,2.2,1.6) az -14.4(프레임 -44.4..15.6) ·
    #   beauty_side eye(-3.2,-7.5,3.3) az 51.1(프레임 21.1..81.1)
    #   원칙 ① 카메라 eye 반경 1.5 m 내 신규 솔리드 금지(특히 rail_cue 근접)
    #        ② 하부 소품은 전부 x>RUN → 계단보다 **멀어** 매몰부 가림 불가
    #        ③ 보행 회랑 |y|<1.62(접근로·진입로) 침범 금지
    # ───────────────────────────────────────────────────────────────────────
    # 등받이 벤치 2 — 상부는 휴게 포켓(grid d10 az 22.4° / beauty), 하부는
    #   approach_walk 중경(az -14.1°, 계단보다 원거리라 무가림).
    benches=[dict(cx=-5.0, cy=3.4, yaw=0.0, where="upper"),
             dict(cx=4.0, cy=-3.2, yaw=0.0, where="lower")],
    bench=dict(length=1.8, width=0.50, height=0.45, back_h=0.42),
    # 휴지통 2 (몸통 + 림)
    bins=[dict(cx=-5.6, cy=2.3, where="upper"),
          dict(cx=4.9, cy=-2.5, where="lower")],
    bin_spec=dict(r=0.26, h=0.85),
    # 공원등(볼라드형 저조도등) — 하부 진입로 양측 2쌍이 산책로 성격을 만든다.
    #   (RUN+2.8, ±2.1) / (RUN+6.8, ±2.1) 은 회랑(1.62) 바깥 잔디.
    parklamps=[dict(cx=-4.6, cy=2.1, where="upper"),
               dict(cx=-6.0, cy=-2.1, where="upper"),
               dict(cx=2.8, cy=2.1, where="lower"),
               dict(cx=2.8, cy=-2.1, where="lower"),
               dict(cx=6.8, cy=2.1, where="lower"),
               dict(cx=6.8, cy=-2.1, where="lower")],
    parklamp=dict(post_r=0.07, post_h=1.05, head_r=0.115, head_h=0.18,
                  cap_t=0.04),
    # 산책로 분기 암시 — 흙/자갈 패치(상면 proud 0.006, 두께 0.16 매입).
    #   상부: 벤치·휴지통·공원등을 얹는 휴게 포켓. 하부: +Y 로 갈라지는 지선.
    patches=[dict(x0=-6.4, x1=-2.6, y0=1.50, y1=4.50, where="upper"),
             dict(x0=5.0, x1=6.5, y0=1.40, y1=9.50, where="lower")],
    patch=dict(proud=0.006, thick=0.16),
    # 원경 파고라(기둥 4 + 지붕 슬래브 + 서까래 3) — 공원 시설물 실루엣.
    pergola=dict(x0=9.0, x1=12.4, y0=6.0, y1=9.5, post_r=0.09, post_h=2.40,
                 roof_t=0.14, eave=0.30, rafter_t=0.08, rafters=3,
                 where="lower"),
    # 소품 위 낙엽 소량 산포 — 별도 고정 시드(본 산포 seed 2702 와 분리).
    prop_leaves=dict(seed=2711, per_bench=10, pergola=22, per_prop=6,
                     scale=(0.038, 0.028, 0.006), jitter=(0.75, 1.25),
                     lift=0.008),

    material=dict(
        # [W2 · leaf_globalization_budget_v2 §6-b] leaf_ground 0.9 -> 2.2.
        # The texture plate cannot be deleted — `LeafMound_A/B/C` + `LeafDrift_N/S`
        # ARE the burial geometry that hides the drop, so removing them removes
        # the hazard. It is demoted to an UNDERLAYER instead: at 0.9 m the
        # printed leaves rendered at 39 % of their real size against the 3D
        # leaves now lying on top, and that size discontinuity is what read as
        # "linoleum". 2.2 m matches the source texture's own physical scale, so
        # the plate reads as ground tone under the scatter rather than as a
        # competing second leaf layer.
        scale=dict(stone_worn=1.1, dirt_park=1.0, grass=1.4, leaf_ground=2.2),
        stone_tint=(0.88, 0.92, 0.84),        # 석재 이끼 톤(약)
        grass_tint=(0.55, 0.62, 0.38),        # 표준 잔디 틴트 + 가을 건조
        leaf_tex_tint=(0.95, 0.72, 0.48),     # leaf_ground 텍스처 오텀 보정
        # 낙엽 산포 4색 (사양 고정값 — 중간톤 상수라 sRGB 암색 규칙 대상 아님)
        leaf_tints=((0.20, 0.09, 0.03), (0.26, 0.13, 0.04),   # r1: 감채
                    (0.16, 0.07, 0.025), (0.30, 0.19, 0.06)),
        leaf_rough=0.90,
        rail_color=(0.14, 0.14, 0.15), rail_metallic=0.8, rail_rough=0.45,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        # 가을 수관: 표준 수관(0.025,0.045,0.015)의 sRGB 암색 대역을 유지한 채
        # 색상만 오텀으로 회전(적갈/황갈). 밝기 총량은 표준과 동급.
        canopy_a=(0.055, 0.030, 0.010), canopy_b=(0.075, 0.048, 0.014),
        canopy_rough=1.0,
        ridge_color=(0.28, 0.26, 0.24),       # 원경 능선(중간 무채·약 갈색기)
        lamp_color=(0.86, 0.86, 0.80), lamp_rough=0.40,   # 공원등 헤드(주간)
    ),

    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        # [ctx2] 49.79 → 42.0 (조사 §1·§5): 낙엽 절정(10월 말~11월 중순)
        #   서울(37.5°N) 정오 태양고도는 35~42° 대역. 49.79°는 9월 말/3월
        #   정오값이라 "늦가을 낙엽"이라는 계절 세계관과 모순이었다.
        #   → 그림자 길이 cot(49.79°)=0.845·h → cot(42.0°)=1.111·h (+31%).
        noon_sun_enable=True, noon_sun_elev=42.0,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # ─── SUN_AZ_OFFSET 근거: 기본 171.5 계열 유지(브리프 §A-7).
    #     월드 태양 az ≈ 33.5+171.5 = 205 → 그림자 az 25(≈ +X 진행방향).
    #     ① 주 시점이 **상부(−X)** 이므로 scene07/09류 "정면 관람 시 라이저 흑
    #        실루엣" 함정에 해당하지 않는다(상부 시점은 라이저가 아니라 디딤면을
    #        본다).  ② 태양이 카메라 뒤(우측)에서 들어와 낙엽 마운드 경사면
    #        (법선이 −X로 25° 기울어짐)을 거의 정면광으로 때린다 → 마운드 상면의
    #        음영 그라디언트가 사라져 **매몰 에지 소실이 극대화**(특색 강화).
    #        ③ 하부 노출단은 난간·산포 낙엽의 캐스트 섀도로 판독 가능.
    #     [ ]키(15° step)로 GUI 스윕 후 감독 재판정. ───
    #  ─── [ctx2] 태양고도 42.0° 하향에 따른 **방위 검산** (SUN_AZ_OFFSET 불변) ───
    #    그림자 단위벡터 = (cos25°, sin25°) = (+0.906, +0.423), 길이 1.111·h.
    #    ① 매몰 구간(마운드 B, x −0.25..1.02 · |y| ≤ 1.33)에 **신규 그림자 0**:
    #       상류(−X)의 유일한 입체는 상부 수목(−6.0, +5.5)·(−11.0, −6.5) 뿐이고
    #       둘 다 그림자가 +Y 로 흘러 회랑(|y| < 1.62) 밖에서 끝난다
    #       (−11 수목: 팁 y = −6.5 + 1.55 = −4.95, 회랑까지 3.3 m 여유).
    #    ② 공원등(−6.0, −2.1, 전고 1.27)만 팁이 (−4.72, −1.50)로 회랑 안에
    #       0.12 m 들어온다 — 계단머리(x=0)에서 4.7 m 상류, 마운드 A(x≥−3.20)
    #       밖이라 특색·판정 무관(구 고도에서는 y=−1.65 로 간발의 차 밖이었다).
    #    ③ 계단 판독 강화: 라이저 0.16 의 그림자가 디딤면(0.34)의 36% → 47%
    #       를 덮어 **하부 노출단의 단 구분이 오히려 선명**해진다.
    #    ④ 명암 대비: 마운드 상면(경사 24.9°)/평탄면 휘도비 0.585 → 0.484.
    #       마운드가 상대적으로 17% 어두워지나, 매몰 특색의 근거는 **기하
    #       연속성**(단코선 0.4706 vs 마운드 0.4643)이지 등휘도가 아니므로
    #       판정 성립에 영향 없음. 가을 사광감(측광)은 오히려 강화.
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneC2")

ASSET_ROLES = ["stone_worn", "leaf_ground", "dirt_park", "grass",
               "hdri", "mdl"]


# ===========================================================================
# [D] 카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷
# ===========================================================================
def build_views(run, z_bot):
    views = sc.grid_views(0.0)                 # h{0.3,0.9,1.8}×d{2,5,10}, +X
    # approach_walk: 상부 접근로 보행 시점 — 낙엽 마루 너머 계단 시작 에지 소실
    views["approach_walk"] = dict(eye=[-4.0, 0.0, 1.55],
                                  tgt=[3.2, 0.0, -0.90])
    # buried_edge: 그레이징 저시점 — 매몰 구간이 완만한 낙엽 경사로 읽히는가
    views["buried_edge"] = dict(eye=[-1.70, 0.20, 0.35],
                                tgt=[4.20, 0.0, -1.10])
    # rail_cue: 난간측 사교 — 하강 사선(유일 단서)만으로 낙차 추정 가능한가
    views["rail_cue"] = dict(eye=[-2.40, 2.20, 1.60],
                             tgt=[4.60, 0.40, -1.60])
    # beauty_side: 사교 부감 — 매몰(1~3단)/점이(4~6단)/노출(7단~) 3구간 대비
    views["beauty_side"] = dict(eye=[-3.20, -7.50, 3.30],
                                tgt=[run * 0.7, 0.60, z_bot + 0.60])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach_walk      — 낙엽 마루 너머로 계단 시작 에지가 소실되는가(특색)
 2. h0.3·d2~5          — 그레이징에서 매몰부가 '완만한 낙엽 경사'로 읽히는가
 3. rail_cue           — 난간 1선 하강 사선이 유일 단서로 잔존하는가
 4. beauty_side        — 1~3단 완전매몰 / 4~6단 중앙피복 / 7단~ 노출 3구간 성립
 5. leaf_cover ON/OFF  — OFF 시 계단·난간 트랜스폼 완전 불변(대응쌍)
 6. 재질·접지          — 낙엽판 부유/틈, 경계석-사면 이음, Z파이팅 없는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import Usd, UsdGeom
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene27")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene27"

    st = PARAMS["stairs"]
    RISER, TREAD, NSTEP = st["riser"], st["tread"], st["nsteps"]
    RUN = TREAD * NSTEP                        # 4.76
    DROP = RISER * NSTEP                       # 2.24
    Z_BOT = st["z_top"] - DROP                 # −2.24
    SLOPE = RISER / TREAD                      # 0.4706 (단코선 기울기)

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return PBR(path, sc.tex_path(role, "diff"),
                       sc.tex_path(role, "nor"), sc.tex_path(role, "rough"),
                       scale, **kw)

        M = {}
        M["stone"] = tex("stone_worn", f"{ROOT}/Looks/Stone",
                         sca["stone_worn"], tint=mp["stone_tint"])
        # [v5.1 §4] 경계석 2매 인스턴스별 ±5% 틴트 지터 — 좌우가 완전히
        #   동일 재질이면 '복제' 인상이 남는다. 텍스처는 공유(석재 결 동일).
        for _tag in ("N", "S"):
            M[f"coping_{_tag}"] = tex(
                "stone_worn", f"{ROOT}/Looks/Coping{_tag}",
                sca["stone_worn"],
                tint=bc.jit_tint(mp["stone_tint"], 0.0,
                                 1.0 if _tag == "N" else -1.0,
                                 "copingC2", amp=0.05))
        M["dirt"] = tex("dirt_park", f"{ROOT}/Looks/Dirt", sca["dirt_park"])
        M["grass"] = tex("grass", f"{ROOT}/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["leafbed"] = tex("leaf_ground", f"{ROOT}/Looks/LeafBed",
                           sca["leaf_ground"], tint=mp["leaf_tex_tint"])
        for i, c in enumerate(mp["leaf_tints"]):
            M[f"leaf_{i}"] = PBR(f"{ROOT}/Looks/Leaf_{i}", diffuse_color=c,
                                 roughness_const=mp["leaf_rough"],
                                 metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
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
        M["ridge"] = PBR(f"{ROOT}/Looks/Ridge", diffuse_color=mp["ridge_color"],
                         roughness_const=0.95, specular_level=0.0)
        # ─ 맥락 드레싱 v2: 공원등 헤드(주간 비발광 확산체) ─
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        return M

    # -------------------------------------------------------------------
    # 지면 — 상부/하부/측면 사면을 **분할 배치** (계단 회랑을 덮지 않음)
    # -------------------------------------------------------------------
    def build_terrain(M):
        up = PARAMS["upper"]
        lo = PARAMS["lower"]
        sl = PARAMS["slopes"]
        gr = PARAMS["ground"]
        path_mtl = M["dirt"] if cfg["cue_material_break"] else M["stone"]

        # ① 상부 접근로(흙길) — x1=+0.02 로 계단과 겹쳐 단1 라이저 면을 담당
        BOX(f"{ROOT}/UpperPath",
            ((up["x0"] + up["x1"]) / 2.0, 0.0, up["z_top"] - up["thick"] / 2.0),
            (up["x1"] - up["x0"], 2.0 * up["y_half"], up["thick"]),
            path_mtl, col=True)
        # ② 상부 잔디 (회랑 바깥 남·북)
        for tag, ya, yb in (("N", up["y_half"], gr["y_edge"]),
                            ("S", -gr["y_edge"], -up["y_half"])):
            BOX(f"{ROOT}/UpperGrass_{tag}",
                ((up["x0"] + up["x1"]) / 2.0, (ya + yb) / 2.0,
                 up["z_top"] - gr["thick"] / 2.0),
                (up["x1"] - up["x0"], yb - ya, gr["thick"]), M["grass"],
                col=True)
        # ③ 측면 잔디 사면 (x 0..RUN, 상면 0.005 침하 → 상·하부 평판이 덮음)
        for tag, ya, yb in (("N", sl["y_in"], sl["y_edge"]),
                            ("S", -sl["y_edge"], -sl["y_in"])):
            sc.build_slope(stage, f"{ROOT}/SideSlope_{tag}", 0.0,
                           -sl["sink"], RUN, DROP, ya, yb, sl["thick"],
                           M["grass"], margin=0.0, collider=True)
        # ④ 하부 진입로 — 계단 밑으로 under_lap 언더랩(부유 방지) + 0.002 침하
        lx0 = RUN - lo["under_lap"]
        lx1 = RUN + lo["x_pad"]
        BOX(f"{ROOT}/LowerPath",
            ((lx0 + lx1) / 2.0, 0.0,
             Z_BOT - lo["sink"] - lo["thick"] / 2.0),
            (lx1 - lx0, 2.0 * lo["y_half"], lo["thick"]), path_mtl, col=True)
        # ⑤ 하부 잔디 (회랑 바깥) — 사면 끝을 0.02 덮어 이음 봉합
        for tag, ya, yb in (("N", lo["y_half"], gr["y_edge"]),
                            ("S", -gr["y_edge"], -lo["y_half"])):
            BOX(f"{ROOT}/LowerGrass_{tag}",
                ((RUN - 0.02 + lx1) / 2.0, (ya + yb) / 2.0,
                 Z_BOT - gr["thick"] / 2.0),
                (lx1 - RUN + 0.02, yb - ya, gr["thick"]), M["grass"], col=True)

    # -------------------------------------------------------------------
    # 석계단 + 양측 경계석
    # -------------------------------------------------------------------
    def build_stairs(M):
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            RISER, TREAD, NSTEP, st["base_z"], M["stone"],
            z_top=st["z_top"], collider=True)
        # 경계석: 단코선 + rise 를 상면으로 하는 경사 스트립(양측)
        cp = PARAMS["coping"]
        cx0 = -cp["ext"]
        crun = RUN + 2.0 * cp["ext"]
        cz0 = -SLOPE * cx0 + cp["rise"]        # x=cx0 에서의 상면 z
        cdrop = SLOPE * crun
        for tag, ya, yb in (("N", cp["y_in"], cp["y_out"]),
                            ("S", -cp["y_out"], -cp["y_in"])):
            sc.build_slope(stage, f"{ROOT}/Coping_{tag}", cx0, cz0, crun,
                           cdrop, ya, yb, cp["thick"], M[f"coping_{tag}"],
                           margin=0.0, collider=True)
        print(f"[기하] 계단 {NSTEP}단 run={RUN:.3f} drop={DROP:.3f} "
              f"z_bot={Z_BOT:.3f} 단코선기울기={SLOPE:.4f}")

    # -------------------------------------------------------------------
    # 낙엽 ① 매몰 마운드(경사판 3매) + 측면 드리프트(_oriented_box rotX)
    # -------------------------------------------------------------------
    def build_leaf_mound(M):
        for md in PARAMS["mound"]:
            sc.build_slope(stage, f"{ROOT}/LeafMound_{md['name']}",
                           md["x0"], md["z0"], md["run"], md["drop"],
                           -md["y_half"], md["y_half"], md["thick"],
                           M["leafbed"], margin=0.0, collider=False)
        dg = PARAMS["drift_geo"]
        for df in PARAMS["drift"]:
            sgn = df["sgn"]
            # rotX(∓5°): 횡단 크라운 — 회랑 바깥 낙엽 둑(안쪽이 높고 바깥이 얇음).
            # rotX(θ): 로컬 +Y → 월드 (cosθ, sinθ). 바깥(+y·−y 각 방향)이 내려가야
            # 하므로 부호는 −sgn.
            sc._oriented_box(
                stage, f"{ROOT}/LeafDrift_{df['name']}",
                (dg["cx"], sgn * dg["cy"], dg["center_z"]),
                (dg["len_x"], dg["len_y"], dg["thick"]), M["leafbed"],
                collider=False, rotx=-sgn * dg["rotx"])

    # -------------------------------------------------------------------
    # 낙엽 ② 근경 산포 — 납작 타원체 count개(고정 시드)
    #   표면 z 는 지형(접근로/계단/사면/하부) + 마운드 상면의 max 로 산출해
    #   부유·매몰 없이 안착시킨다.
    # -------------------------------------------------------------------
    def build_leaf_scatter(M):
        ls = PARAMS["leaf_scatter"]
        rng = random.Random(int(ls["seed"]))
        UsdGeom.Xform.Define(stage, f"{ROOT}/Leaves")
        mats = [M[f"leaf_{i}"] for i in range(len(mp["leaf_tints"]))]
        cp = PARAMS["coping"]
        y_stair = st["y1"]
        plates = [(m["x0"], m["x0"] + m["run"], m["y_half"], m["z0"],
                   m["drop"] / m["run"]) for m in PARAMS["mound"]]

        def terrain_z(x, y):
            if x <= 0.0:
                return 0.0
            if x >= RUN:
                return Z_BOT
            ay = abs(y)
            if ay <= y_stair:                  # 계단 회랑 → 단 상면
                i = min(int(x / TREAD) + 1, NSTEP)
                return -RISER * i
            if ay <= cp["y_out"]:              # 경계석 상면(단코선 + rise)
                return cp["rise"] - SLOPE * x
            # 측면 사면(선형) — build_slope 의 sink 만큼 낮음(부유 방지)
            return -DROP * (x / RUN) - PARAMS["slopes"]["sink"]

        def surface_z(x, y):
            z = terrain_z(x, y)
            if cfg["leaf_cover"]:
                for px0, px1, pyh, pz0, pslope in plates:
                    if px0 <= x <= px1 and abs(y) <= pyh:
                        z = max(z, pz0 - pslope * (x - px0))
            return z

        sx, sy, sz = ls["scale"]
        jlo, jhi = ls["jitter"]
        x_lo = ls["x0"]
        x_hi = RUN + ls["x_pad"]
        n = int(ls["count"])
        x_hi_near = RUN + ls.get("x_pad_near", 1.5)

        # [사실화 v1] 실제 낙엽 USD 산포.
        #   기존 납작 타원체 900개는 **총 피복이 0.96 m² 뿐**이라(실측),
        #   화면에 보이는 낙엽은 사실상 전부 leaf_ground 텍스처 무늬였다.
        #   = 사용자가 지적한 "장판". 피복률로 지정하고 실제 지오메트리를 깐다.
        # 게이트는 `sc.LOOK_GEO` — 산포는 프림 신설이라 기하다. 재질 A/B 양팔에서
        # 낙엽이 사라지면 §7.1 문턱표를 뽑은 렌더와 다른 씬이 된다(T1 §1.7.1 주).
        if sc.LOOK_GEO and sc.veg_available():
            # [W2 · G2] The 3D leaves go GLOBAL, not just to the near band.
            # Only the large clusters (fallcluster) are used: per-instance
            # coverage is 12~20x a single leaf, so the same prim budget covers
            # far more ground. Instancing keeps the unique vertex data flat —
            # the prototype is shared, only the instance table grows.
            # One scatter call per rect, seed = base + k, so re-runs are
            # deterministic and the rects stay independent.
            pool = [p for p in sc.VEG_DEBRIS if "fallcluster" in p[0]]
            gfn = lambda x, y: surface_z(x, y) + ls["lift"]
            got = 0
            for k, r in enumerate(ls["g2"]):
                got += sc.scatter_debris(
                    stage, f'{ROOT}/Leaves/{r["tag"]}',
                    r["x0"], r["y0"], r["x1"], r["y1"], 0.0,
                    cover=r["cover"], seed=int(ls["seed"]) + k, pool=pool,
                    ground_fn=gfn, edge_bias=0.0,
                    max_count=int(r["max_count"]), tilt_max=10.0)
            if got:
                # Budget doc predicted 1,689 with the pre-A3 coverage ledger
                # (mean_cov 0.0435). B-audit A3 lowered the two cluster rows,
                # so mean_cov is 0.04115 and the same target cover now needs
                # ~1,784 instances (~10.8 M logical tris, under the 12 M cap of
                # ground_kit §8.3). Count is printed, never assumed.
                print(f"[낙엽] 실물 USD 전역 산포(G2) {got}개 / "
                      f"{len(ls['g2'])} rect · seed={ls['seed']}+k")
                return
        for i in range(n):
            x = rng.uniform(x_lo, x_hi)
            if rng.random() < ls["band_frac"]:
                y = rng.uniform(-ls["y_band"], ls["y_band"])
            else:
                y = rng.uniform(-ls["y_wide"], ls["y_wide"])
            j = rng.uniform(jlo, jhi)
            a, b = sx * j, sy * j
            if rng.random() < 0.5:             # 장축 방향 변주(회전 대용)
                a, b = b, a
            z = surface_z(x, y) + ls["lift"]
            sc.add_sphere(stage, f"{ROOT}/Leaves/Leaf_{i}", (x, y, z),
                          (a, b, sz * j), mats[rng.randrange(len(mats))])
        print(f"[낙엽] 산포 {n}개 (seed={ls['seed']}) · 마운드 판 "
              f"{len(PARAMS['mound'])}매 + 드리프트 {len(PARAMS['drift'])}매")

    # -------------------------------------------------------------------
    # 단서 (cue)
    # -------------------------------------------------------------------
    def build_cues(M):
        cp = PARAMS["coping"]
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                RISER, TREAD, NSTEP, color=ns["color"], width=ns["width"],
                proud=ns["proud"], z_top=st["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["stone"], z=0.0,
                             proud=tc["proud"])
        if cfg["cue_railing"]:
            rl = PARAMS["rail"]

            def rail_ground(x):
                """포스트 착지면 = 경계석 상면(계단 구간) / 접근로 지면."""
                if x < -cp["ext"]:
                    return 0.0
                xx = min(max(x, 0.0), RUN)
                return cp["rise"] - SLOPE * xx

            sc.build_railing_line(
                stage, f"{ROOT}/Rail", rl["y"], rl["x_start"], st["x0"],
                RUN, DROP, rail_ground, M["rail"], rail_h=rl["rail_h"],
                post_r=rl["post_r"], spacing=rl["spacing"],
                rail_r=rl["rail_r"], rail_mid_r=rl["rail_mid_r"],
                rail_mid_drop=rl["rail_mid_drop"])

    # -------------------------------------------------------------------
    # 드레싱 + 지평 폐쇄
    # -------------------------------------------------------------------
    def build_dressing(M):
        for i, t in enumerate(PARAMS["trees"]):
            if t["where"] == "upper":
                gx, gz = t["cx"], 0.0
            else:
                gx, gz = RUN + t["cx"], Z_BOT
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", gx, t["cy"], gz,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        build_park_context(M)

    # -------------------------------------------------------------------
    # 맥락 드레싱 v2 — 벤치 · 휴지통 · 공원등 · 분기 산책로 패치 · 파고라
    #   + 소품 위 낙엽 소량 산포(고정 시드). 계단·낙엽 레이어·난간 불변.
    #   좌표 규약: where="upper" → 절대 x(지면 z=0),
    #              where="lower" → RUN + cx(지면 z=Z_BOT). 전부 평탄면.
    # -------------------------------------------------------------------
    def build_park_context(M):
        pl = PARAMS["prop_leaves"]
        rng = random.Random(int(pl["seed"]))
        lmats = [M[f"leaf_{i}"] for i in range(len(mp["leaf_tints"]))]
        sx0, sy0, sz0 = pl["scale"]
        jlo, jhi = pl["jitter"]
        counter = [0]

        # hazard_stairs=False 대조군은 전면 평지(z=0) → 하부 소품 부유 방지
        low_z = Z_BOT if cfg["hazard_stairs"] else 0.0

        def place(where, cx):
            """(gx, gz) — where 별 지면 좌표."""
            return (cx, 0.0) if where == "upper" else (RUN + cx, low_z)

        def leaves(cx, cy, z, rx, ry, n):
            """소품 상면·주변 낙엽 산포 n장(고정 시드 · 납작 타원체)."""
            for _ in range(int(n)):
                j = rng.uniform(jlo, jhi)
                a, b = sx0 * j, sy0 * j
                if rng.random() < 0.5:
                    a, b = b, a
                sc.add_sphere(
                    stage, f"{ROOT}/Leaves/Prop_{counter[0]}",
                    (cx + rng.uniform(-rx, rx), cy + rng.uniform(-ry, ry),
                     z + pl["lift"]),
                    (a, b, sz0 * j), lmats[rng.randrange(len(lmats))])
                counter[0] += 1

        # ① 산책로 분기 패치 (흙/자갈) — 소품 아래 먼저 깔아 접지 정합
        pa = PARAMS["patch"]
        for i, pd in enumerate(PARAMS["patches"]):
            gx0, gz = place(pd["where"], pd["x0"])
            gx1, _ = place(pd["where"], pd["x1"])
            z_hi = gz + pa["proud"]
            z_lo = z_hi - pa["thick"]
            BOX(f"{ROOT}/PathPatch_{i}",
                ((gx0 + gx1) / 2.0, (pd["y0"] + pd["y1"]) / 2.0,
                 (z_hi + z_lo) / 2.0),
                (gx1 - gx0, pd["y1"] - pd["y0"], z_hi - z_lo), M["dirt"])

        # ② 등받이 벤치 — 좌판·등받이 위 낙엽 소량
        bs = PARAMS["bench"]
        for i, bd in enumerate(PARAMS["benches"]):
            gx, gz = place(bd["where"], bd["cx"])
            # [v5.1 §3] 축평행·정위치 해소 (좌표 해시 결정적 지터).
            #   벤치는 이미 흙 패치(휴게 포켓)·수목 앵커 옆이라 지터만 건다.
            _dx, _dy = bc.jit_pos(bd["cx"], bd["cy"], "benchC2", amp=0.20)
            _yaw = bc.jit_yaw(bd["cx"], bd["cy"], "benchC2", lo=3.0, hi=8.0,
                              base=bd["yaw"])
            gx, bcy = gx + _dx, bd["cy"] + _dy
            pfx = f"{ROOT}/Bench_{i}"
            sc.build_bench(stage, pfx, gx, bcy, gz, M["wood"],
                           length=bs["length"], width=bs["width"],
                           height=bs["height"], yaw=_yaw)
            back_y = -(bs["width"] / 2.0 - 0.04)      # 로컬 좌표(회전 상속)
            BOX(f"{pfx}/Back", (0.0, back_y, bs["height"] + bs["back_h"] / 2.0),
                (bs["length"], 0.06, bs["back_h"]), M["wood"])
            leaves(gx, bcy, gz + bs["height"],
                   bs["length"] / 2.0 - 0.10, bs["width"] / 2.0 - 0.08,
                   pl["per_bench"])
            leaves(gx, bcy + 0.55, gz, 1.10, 0.35, pl["per_prop"])

        # ③ 휴지통
        bn = PARAMS["bin_spec"]
        for i, bd in enumerate(PARAMS["bins"]):
            gx, gz = place(bd["where"], bd["cx"])
            _dx, _dy = bc.jit_pos(bd["cx"], bd["cy"], "binC2", amp=0.18)
            gx, bcy = gx + _dx, bd["cy"] + _dy      # [v5.1 §3] 위치 지터
            sc.add_cylinder(stage, f"{ROOT}/Bin_{i}/Body",
                            (gx, bcy, gz + bn["h"] / 2.0),
                            bn["r"], bn["h"], M["rail"], collider=True)
            sc.add_cylinder(stage, f"{ROOT}/Bin_{i}/Rim",
                            (gx, bcy, gz + bn["h"] + 0.015),
                            bn["r"] * 1.12, 0.05, M["rail"])
            leaves(gx, bcy, gz, 0.55, 0.55, pl["per_prop"])

        # ④ 공원등(볼라드형) — 포스트 + 확산 헤드 + 캡
        pk = PARAMS["parklamp"]
        for i, ld in enumerate(PARAMS["parklamps"]):
            gx, gz = place(ld["where"], ld["cx"])
            # [v5.1 §3] ±0.18 m 지터. |y| 는 회랑(1.62) 밖을 유지해야 하므로
            #   지터 후에도 |cy| ≥ 1.92 임을 좌표로 보장(원 2.1 − 0.18).
            _dx, _dy = bc.jit_pos(ld["cx"], ld["cy"], "lampC2", amp=0.18)
            gx, lcy = gx + _dx, ld["cy"] + _dy
            pfx = f"{ROOT}/ParkLamp_{i}"
            sc.add_cylinder(stage, f"{pfx}/Post",
                            (gx, lcy, gz + pk["post_h"] / 2.0),
                            pk["post_r"], pk["post_h"], M["rail"],
                            collider=True)
            sc.add_cylinder(stage, f"{pfx}/Head",
                            (gx, lcy,
                             gz + pk["post_h"] + pk["head_h"] / 2.0 - 0.02),
                            pk["head_r"], pk["head_h"], M["lamp"])
            sc.add_cylinder(stage, f"{pfx}/Cap",
                            (gx, lcy,
                             gz + pk["post_h"] + pk["head_h"] + pk["cap_t"] / 2.0
                             - 0.03),
                            pk["head_r"] * 1.08, pk["cap_t"], M["rail"])

        # ⑤ 파고라 (기둥 4 + 지붕 슬래브 + 서까래) — 원경 공원 시설물
        pg = PARAMS["pergola"]
        gx0, gz = place(pg["where"], pg["x0"])
        gx1, _ = place(pg["where"], pg["x1"])
        cy = (pg["y0"] + pg["y1"]) / 2.0
        cx = (gx0 + gx1) / 2.0
        for tag, px, py in (("A", gx0, pg["y0"]), ("B", gx1, pg["y0"]),
                            ("C", gx0, pg["y1"]), ("D", gx1, pg["y1"])):
            sc.add_cylinder(stage, f"{ROOT}/Pergola/Post_{tag}",
                            (px, py, gz + pg["post_h"] / 2.0),
                            pg["post_r"], pg["post_h"], M["wood"],
                            collider=True)
        z_roof = gz + pg["post_h"]
        BOX(f"{ROOT}/Pergola/Roof",
            (cx, cy, z_roof + pg["roof_t"] / 2.0 - 0.02),
            (gx1 - gx0 + 2.0 * pg["eave"], pg["y1"] - pg["y0"]
             + 2.0 * pg["eave"], pg["roof_t"]), M["wood"])
        for r in range(int(pg["rafters"])):
            ry = pg["y0"] + (pg["y1"] - pg["y0"]) * (r + 1.0) \
                / (pg["rafters"] + 1.0)
            BOX(f"{ROOT}/Pergola/Rafter_{r}",
                (cx, ry, z_roof + pg["roof_t"] + pg["rafter_t"] / 2.0 - 0.03),
                (gx1 - gx0 + 2.0 * pg["eave"], pg["rafter_t"] * 1.6,
                 pg["rafter_t"]), M["wood"])
        leaves(cx, cy, z_roof + pg["roof_t"] - 0.02,
               (gx1 - gx0) / 2.0, (pg["y1"] - pg["y0"]) / 2.0, pl["pergola"])
        print(f"[드레싱] 공원 소품 {len(PARAMS['benches'])}벤치 · "
              f"{len(PARAMS['bins'])}휴지통 · {len(PARAMS['parklamps'])}공원등 · "
              f"파고라 1 · 패치 {len(PARAMS['patches'])} · "
              f"소품 낙엽 {counter[0]}장 (seed={pl['seed']})")

    def build_horizon(M):
        bh = PARAMS["back_hedge"]
        for i, h in enumerate(PARAMS["back_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/BackHedge_{i}",
                           bh["cx"] - bh["sx"] / 2.0,
                           h["cy"] - bh["length"] / 2.0,
                           bh["cx"] + bh["sx"] / 2.0,
                           h["cy"] + bh["length"] / 2.0,
                           bh["h"], base_z=0.0)
        fh = PARAMS["far_hedge"]
        fx = RUN + fh["x_pad"]
        for i, h in enumerate(PARAMS["far_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}",
                           fx - fh["sx"] / 2.0, h["cy"] - fh["length"] / 2.0,
                           fx + fh["sx"] / 2.0, h["cy"] + fh["length"] / 2.0,
                           fh["h"], base_z=Z_BOT)
        for i, r in enumerate(PARAMS["ridge"]):
            BOX(f"{ROOT}/Ridge_{i}",
                (RUN + r["x_pad"], 0.0, Z_BOT + r["h"] / 2.0),
                (r["t"], r["sy"], r["h"]), M["ridge"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 : 계단·사면을 z=0 평지로 통일."""
        up = PARAMS["upper"]
        lo = PARAMS["lower"]
        gr = PARAMS["ground"]
        x0, x1 = up["x0"], RUN + lo["x_pad"]
        BOX(f"{ROOT}/FlatFill", ((x0 + x1) / 2.0, 0.0, -gr["thick"] / 2.0),
            (x1 - x0, 2.0 * gr["y_edge"], gr["thick"]), M["grass"], col=True)
        BOX(f"{ROOT}/FlatPath", ((x0 + x1) / 2.0, 0.0, 0.002 - 0.30),
            (x1 - x0, 2.0 * up["y_half"], 0.60),
            M["dirt"] if cfg["cue_material_break"] else M["grass"], col=True)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    if cfg["hazard_stairs"]:
        build_terrain(M)
        build_stairs(M)
        if cfg["leaf_cover"]:
            build_leaf_mound(M)
        build_leaf_scatter(M)
        build_cues(M)
    else:
        build_flat_fill(M)
        if cfg["leaf_cover"]:
            build_leaf_scatter(M)

    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_horizon(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneC2 조립 완료 · 프림 {n}개 · 조기 종료")
        # ── [W2-C · B12] G2 인스턴싱 런타임 검증 ────────────────────────
        #   `leaf_globalization_budget_v2` 게이트 0. `SetInstanceable(True)` 는
        #   조용히 실패할 수 있고(참조 없는 프림 등) CPU 정적 검사로는
        #   프로토타입 공유 여부를 볼 방법이 없다 — pxr 런타임이 필요하다.
        #   1,784개가 프로토타입을 **공유하지 않으면** 고유 정점이 그대로
        #   1,784배로 늘어 §8.3 삼각형 예산이 무의미해진다.
        protos = stage.GetPrototypes()
        leaves, inst = [], 0
        for p in stage.Traverse():
            sp = str(p.GetPath())
            if "/Leaves/" in sp and sp.endswith("/Asset"):
                leaves.append(p)
                if p.IsInstance():
                    inst += 1
        print(f"[B12] 프로토타입 {len(protos)}개 "
              f"(≥1 필요) · 낙엽 Asset 프림 {len(leaves)}개 · "
              f"IsInstance True {inst}개 "
              f"({100.0 * inst / max(1, len(leaves)):.1f} %)")
        for pr in protos:
            print(f"       · 프로토타입 {pr.GetPath()} "
                  f"자손 {sum(1 for _ in Usd.PrimRange(pr))}")
        ok = (len(protos) >= 1 and leaves and inst == len(leaves))
        print(f"[B12] {'PASS' if ok else 'FAIL'} — "
              f"프로토타입 ≥1 ∧ 전 낙엽 인스턴스화")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views(RUN, Z_BOT)
    _v0 = views["approach_walk"]
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
        sc.capture_pipeline(simulation_app, views, out_dir,
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneC2_{ts}.png")
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
