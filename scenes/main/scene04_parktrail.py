# -*- coding: utf-8 -*-
"""
scene04_parktrail.py — NegObs 인공씬 4호: 공원 침목 계단 (T4, Isaac Sim 4.5)

사양서 : Docs/multi_scene_brief_v2.md §C `scene04_parktrail` (유일 사양)
공통 라이브러리 : scene_common.py (검증된 API — scene01 이식·일반화)

위험 본질(T4): 완경사 공원 사면을 내려가는 **불규칙 단높이 침목 계단**.
  침목(목재) 라이저 + 마사토(자갈) 디딤면이 주변 흙·낙엽과 융합해 단코
  절단선이 모호해진다. 하부 나무 수관이 상부 눈높이에 걸리는 것이 앵커 단서.

[v5.1 현실성] 사용자 피드백 "길 굴곡 + 계단 옆 경사 부자연".
  (1) 길 사행 강화 — 중심선 폴리라인을 12~13절점으로 늘리고 세그당 yaw 진폭
      ±20~32° (구 ±8~12°), 세그 폭 ±10 % 미세 변동으로 '자로 그은 띠' 인상 제거.
  (2) **풀숲 사이 침목계단** — 계단 양측 노출 흙사면(구 dirt 밴드 |y| 1.15~3.0)을
      1.7 로 좁히고, 그 위를 초지 융기 밴드(눌린 타원체 열) + 관목 2열로 덮어
      절개 사면을 은폐한다. 계단·침목·말뚝(위험 기하) 트랜스폼은 불변.

[v6 판정 — 재수정] (2)의 초지 밴드가 **"이끼 낀 바위밭"** 으로 렌더됐다(덩치 큰
  타원체 × grass 텍스처 uv 1.6). → 상수색 tuft 3종 · 크기 1/2 · 개수 3배 · 배치
  불규칙(간격 지터/결측/축 교환)으로 재작업. 검산: `NEGOBS_SELFCHECK=1 python
  scene04_parktrail.py` (계단 침범 · 접지 · 흙띠 피복률). 위험 기하 불변.

정합 정정(감독 브리프 §C 대비):
  riser 테이블 합 = 1.45, tread 테이블 합 = 5.55.
  → 사면 drop = 1.45 (브리프 본문 0.9/−1.5 근사 아님), 하부 평탄 z = −1.45로 통일.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene04_parktrail.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene04_parktrail.py
      NEGOBS_CAPTURE_DIR  : 저장 폴더 (기본 look_check/scene04/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (기본 rt)
      NEGOBS_VIEWS        : 쉼표로 뷰 이름 필터 (기본 전부)

좌표계: Z-up, m, 진행축 +X, 계단 상단 모서리 = x=0.
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG — scene01 동일 6키 + cue_nosing 신규.
#     hazard_stairs 외 토글은 위험 기하를 바꾸지 않는다(불변).
#     T4 정체성상 설비 단서(난간·점자·논슬립)는 기본 False (코드 경로는 존재).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 사면+계단+하부를 z=0 평지로(기하 토글 유일 예외)
    "cue_railing":        False,   # True → 통나무 손스침 1선(y=+1.0, wood_dark 원기둥 r0.05 + 나무 포스트)
    "cue_tactile":        False,   # True → 상단 모서리 점자블록 띠(공원엔 이례적 — 코드 경로만)
    "cue_material_break": True,    # True → 디딤면 gravel(마사토), False → dirt_park(주변 흙과 융합·모호 강화)
    "cue_sign":           False,   # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,    # 나무·관목(hedge)·벤치 일괄 (길·잔디 지형은 상시)
    "cue_nosing":         False,   # 신규 키. True → 전 단 논슬립 띠(공원 침목 계단엔 이례적)
}


# ===========================================================================
# [B] 불규칙 단 테이블 (브리프 §C) — 합이 곧 사면 run/drop.
# ===========================================================================
RISERS = [0.16, 0.14, 0.18, 0.15, 0.19, 0.14, 0.17, 0.15, 0.17]   # 합 = 1.45
TREADS = [0.55, 0.70, 0.50, 0.80, 0.60, 0.55, 0.75, 0.50, 0.60]   # 합 = 5.55
STAIR_RUN = sum(TREADS)     # 5.55
STAIR_DROP = sum(RISERS)    # 1.45


# ===========================================================================
# [C] PARAMS — 치수·재질·조명·캡처. light dict = scene01 이식 + SUN_AZ_OFFSET.
# ===========================================================================
PARAMS = dict(
    # --- 지형 (Z-up, +X 하강). 기본 지면 = grass, 부지 y±25 확폭 ---
    upper=dict(x0=-35.0, x1=0.0, y0=-25.0, y1=25.0, z_top=0.0, thick=0.5),
    lower=dict(x0=STAIR_RUN, x1=35.0, y0=-25.0, y1=25.0, z_top=-STAIR_DROP,
               thick=0.5),
    # 사면(x 0..run): grass 기본 + 계단 회랑 주변 y±dirt_y만 dirt 사면.
    #   회랑측 트림 스트립(y ±corridor_y..±trim_out)은 노징 라인 +trim_over 봉합.
    # [v5.1] dirt_y 3.0 → 1.7 : 계단 양측 노출 흙사면을 0.55 m 어깨로 축소.
    #   나머지(1.7~25)는 grass, 그 위를 verge(초지 융기 밴드+관목)가 덮는다.
    slope=dict(x0=0.0, z0=0.0, run=STAIR_RUN, drop=STAIR_DROP, thick=0.35,
               corridor_y=0.9, trim_out=1.15, trim_over=0.02,
               dirt_y=1.7, flank_y=25.0),
    # 계단 전후 3m dirt 접속부 (grass 지면 위 흙 트레일 랜딩)
    connect=dict(length=3.0, half_y=3.0),

    # === [W2-D ground_kit] P11 trail_soil (spec §5.7 row 04) ===============
    # Natural profile: ground_kit raises on any urban infra by itself.
    # Element split follows the two constraints that actually bind here:
    #  * scatter (exposed gravel, exposure <= 0.06 m) obeys the GT-E5 ramp,
    #    |x_e| >= 40 * 0.06 = 2.40 m. The scatter field is driven by the plan
    #    **region**, so the region stops at x=-2.40; the d5/d10 near windows
    #    (x -4.44..-3.00 and -9.44..-8.00) sit fully inside it, and the d2
    #    window is filled by the strip elements below instead.
    #  * wear lane + edge litter are decals (+0.6 mm -> GT-E1' needs 0.024 m),
    #    so they may run right up to the stair head. They are given an explicit
    #    centreline on the ConnectU landing, which is the one straight piece of
    #    trail in frame; the PathU polyline meanders out of the h0.3 frame
    #    (at x=-9 its centre is y=-2.46 while the frame half width is 1.16).
    #  * `build_edge_break` targets the real culprit named by spec §5.7 /
    #    appendix A6: the 3.0 x 6.0 m ConnectU dirt box against the grass slab,
    #    transition width 0 px, dE76 18.9. Its three seams are x=-3.0 (across
    #    the frame) and y=+-3.0 (along it); the composer can only emit
    #    constant-y lines, so the seams are built by direct calls.
    #  * region y -3.0..+1.0 is not symmetric on purpose: it is the trail
    #    corridor. The PathU centre line runs y -2.46 (x=-9.3) to -1.36
    #    (x=-3.5), and the h0.3 frame half width is 1.16 m at X=2.0, so this
    #    band covers both the trail and the frame centre without spending
    #    scatter budget on lawn the camera never sees.
    gkit=dict(x0=-12.0, y0=-3.0, y1=1.0, scatter_x1=-2.40,
              wear=((-3.0, 0.0), (-0.6, 0.0)), wear_w=0.90),
    # 침목 계단: 폭 y −0.9..0.9, base_z=−1.8. 디딤면 gravel(마사토).
    stairs=dict(x0=0.0, y0=-0.9, y1=0.9, base_z=-1.8, z_top=0.0,
                sleeper_thick=0.15, sleeper_over=0.02,
                stake_r=0.025, stake_h=0.35, stake_y=0.8),

    # 길: 폭 1.8 dirt_park 밝은 틴트, 1mm 돌출.
    # v4-A1: 축정렬 3세그 + cy 0.8 계단 이동은 곡선이 아니라 직각 계단(Tetris)
    #   윤곽을 만들었다 → 중심선 폴리라인 + rotZ 회전 세그(build_rot_group)로
    #   완만한 사행 6세그로 교체. v4-A2: 양끝을 배경 울타리 개구까지 연장해
    #   '무에서 생기고 무로 사라지는' 접근/탈출로 절단을 해소.
    # [v5.1 현실성] 구 폴리라인은 y 가 단조 드리프트(상부 −4.6→0, 하부 0→1.9)라
    #   세그 yaw 가 8~12° 로만 변해 '완만히 휜 직선'이었다. 사인 사행(파장 21~23 m,
    #   진폭 1.5 m) + 절점 지터(±0.18)로 재생성 — 세그 yaw ±20~32°, 인접 세그
    #   yaw 변화 최대 21°(상부)/27°(하부). 절점 수 7→13(상부)·7→11(하부).
    #   양끝 절점은 유지: 상부 시점은 배경 울타리 개구(y −6.5..−2.5) 안,
    #   하부 종점은 개구(y −1.5..3.5) 안, 계단 접속점 (0,0)/(5.55,0) 고정.
    #   width_jit: 세그별 폭 ±10 % (다짐 폭이 일정한 인공 띠 인상 제거).
    path=dict(width=1.8, thick=0.06, proud=0.001, overlap=0.7, width_jit=0.10,
              tint=(1.10, 1.05, 0.95),
              upper=[(-33.0, -4.90), (-29.6, -5.51), (-26.7, -5.19),
                     (-23.8, -4.23), (-20.9, -2.39), (-18.0, -1.17),
                     (-15.1, -1.01), (-12.2, -1.49), (-9.3, -2.46),
                     (-6.4, -2.43), (-3.5, -1.36), (-1.2, -0.18), (0.0, 0.0)],
              lower=[(5.55, 0.0), (8.4, -1.07), (11.3, -0.72), (14.2, 0.16),
                     (17.1, 1.50), (20.0, 2.41), (22.9, 2.27), (25.8, 1.58),
                     (28.7, 0.57), (31.6, 0.02), (33.5, -0.15)]),

    # 원경 폐쇄: 배경 생울타리 띠 + 나무 라인 (확폭 부지 허공 차단).
    #   gz: 'lower'→하부 평탄, 'slope'→사면 보간, 숫자→절대. (x0,y0,x1,y1).
    # v4-A4: 울타리를 대지 끝(x ±35 / y ±25)에 근접시켜(±34 / ±24.2) 울타리 위로
    #   잔디가 더 보이던 것을 최소화 + h 1.2→1.5.
    # v4-A3: 사면 구간(x 0..5.55)에 뚫려 있던 5.55 m 구멍을 사면 보간 밴드로 봉합.
    # v4-A2: 길이 통과하는 개구(상부 y −6.5..−2.5 / 하부 y −1.5..3.5)를 남긴다.
    bg_hedge=dict(h=1.5),
    bg_hedges=[
        dict(x0=-34.0, y0=-24.2, x1=-32.8, y1=-6.5, gz=0.0),    # 상부 뒤 (남)
        dict(x0=-34.0, y0=-2.5, x1=-32.8, y1=24.2, gz=0.0),     # 상부 뒤 (북)
        dict(x0=32.8, y0=-24.2, x1=34.0, y1=-1.5, gz="lower"),  # 하부 끝 (남)
        dict(x0=32.8, y0=3.5, x1=34.0, y1=24.2, gz="lower"),    # 하부 끝 (북)
        dict(x0=-34.0, y0=23.0, x1=0.0, y1=24.2, gz=0.0),       # 상부 +Y
        dict(x0=-34.0, y0=-24.2, x1=0.0, y1=-23.0, gz=0.0),     # 상부 -Y
        dict(x0=5.55, y0=23.0, x1=34.0, y1=24.2, gz="lower"),   # 하부 +Y
        dict(x0=5.55, y0=-24.2, x1=34.0, y1=-23.0, gz="lower"), # 하부 -Y
    ],
    # v4-A3: 사면 구간 봉합 밴드 (구배 보정 — build_slope 방식)
    bg_slope_hedges=[dict(y0=23.0, y1=24.2), dict(y0=-24.2, y1=-23.0)],
    bg_trees=[dict(cx=-31.0, cy=-10.0, gz=0.0, trunk_h=2.4),
              dict(cx=-31.0, cy=9.0, gz=0.0, trunk_h=2.2),
              dict(cx=31.0, cy=-8.0, gz="lower", trunk_h=2.4),
              dict(cx=31.0, cy=6.0, gz="lower", trunk_h=2.2),
              dict(cx=31.0, cy=15.0, gz="lower", trunk_h=2.3)],

    # 자연물: 나무 5 (상부1·사면옆1·하부3). 하부 나무는 수관 상단이 z≈0.5~1.2에
    #   오도록 trunk_h 축소. gz='slope'는 사면 보간, 'lower'는 하부 평탄.
    trees=[dict(name="U0", cx=-6.0, cy=-4.0, gz=0.0, trunk_h=2.2),
           dict(name="S0", cx=2.5, cy=3.5, gz="slope", trunk_h=2.0),
           dict(name="L0", cx=9.0, cy=-3.0, gz="lower", trunk_h=1.3),
           dict(name="L1", cx=12.0, cy=4.0, gz="lower", trunk_h=1.4),
           dict(name="L2", cx=15.0, cy=-5.0, gz="lower", trunk_h=1.2)],
    tree=dict(trunk_r=0.06, stake_r=0.015, stake_h=1.2, stake_off=0.5),
    # v4-D9: 나무 10 → 18 (상부 3 + 하부 5 증식)
    trees_extra=[dict(cx=-12.0, cy=-8.0, gz=0.0, trunk_h=2.3),
                 dict(cx=-18.0, cy=6.0, gz=0.0, trunk_h=2.5),
                 dict(cx=-24.0, cy=-3.0, gz=0.0, trunk_h=2.2),
                 dict(cx=20.0, cy=-6.0, gz="lower", trunk_h=1.5),
                 dict(cx=24.0, cy=5.0, gz="lower", trunk_h=1.7),
                 dict(cx=28.0, cy=-12.0, gz="lower", trunk_h=2.0),
                 dict(cx=18.0, cy=9.0, gz="lower", trunk_h=1.6),
                 dict(cx=22.0, cy=0.0, gz="lower", trunk_h=1.4)],

    # 관목 hedge 6개소: (cx, cy, gz 표기).
    # v4-B1: gz="slope" 관목은 축정렬 박스라 구배 0.261 × 반폭 0.6 →
    #   상류 0.157 매입 / 하류 0.157 부유(높이 0.6의 26%) → build_slope 전환.
    # v4-B2: 모서리 각진 단일 박스가 '잔디 위 상자'로 읽힘 → 군락당 3장 중첩.
    # [v5 판정 반영 / 재수정] 위 v4-B1+B2 조합이 역효과였다. build_slope 는
    #   상면만 구배에 맞춘 얇은 판을 만들고, 그 판 3장이 서로 다른 각도로
    #   어긋나면서 '잔디를 뚫고 나온 각진 판떼기 더미'로 렌더됐다
    #   (step_detail 우측 / canopy_anchor 우하 / trail_approach 좌우).
    #   → 형상을 **눌린 타원체(add_sphere) 3개 중첩 = 수관 blob** 으로 교체.
    #     · 경사 보정은 형상이 아니라 '배치 높이'에만 건다(_resolve_gz).
    #       축정렬 회전체이므로 어느 각도에서도 각진 절단면이 생기지 않는다.
    #     · 접지: 구 중심을 지면 z + rz*(1−embed) 에 두어 하단을 rz*embed
    #       (=25 %) 만큼 지면에 매입 → 부유·하드 에지 그림자 소멸.
    #     · blobs = (dx, dy, rx, ry, rz) [반경, m]. 최대 높이 ≈ 1.75*rz.
    hedges=[dict(cx=-10.0, cy=3.0, gz=0.0), dict(cx=-4.0, cy=5.5, gz=0.0),
            dict(cx=1.5, cy=4.5, gz="slope"),
            dict(cx=7.0, cy=-4.5, gz="lower"), dict(cx=13.0, cy=-2.0, gz="lower"),
            dict(cx=16.0, cy=3.0, gz="lower")],
    hedge=dict(embed=0.25,
               blobs=((0.00, 0.00, 0.72, 0.60, 0.34),
                      (0.52, 0.40, 0.50, 0.42, 0.25),
                      (-0.44, -0.36, 0.55, 0.38, 0.29))),  # (dx,dy,rx,ry,rz)

    # === [v5.1] 풀숲 사이 침목계단 — 계단 양측 초지 융기 밴드 + 관목 ===
    # 구 v4-D8 `slope_understory`(build_slope 경사 판 4장)는 v5 판정이 관목에서
    #   지적한 '각진 판떼기' 형상과 같은 계열이라 폐기하고, 계단 양측을 감싸는
    #   **눌린 타원체 열**로 전면 교체한다.
    #   · rowA(초지 융기 밴드) : 흙 어깨(|y| 1.15~1.7)와 트림 이음선을 덮는다.
    #   · rowB/rowC(관목)     : 그 바깥에서 사면을 잡목림으로 닫는다.
    #
    # [v6 판정 — 재수정] rowA 가 **"이끼 낀 바위밭 / 일본식 석정원"** 으로 렌더됐다.
    #   원인 = (덩치 1.4×1.24×0.84 m 매끈 타원체) × (grass 텍스처 uv 1.6 m/타일).
    #   1.6 m 주기 노멀맵이 1.4 m 덩어리 위에 얹히면 잎이 아니라 **암괴 요철**이
    #   되고, 크기까지 사람 무릎 높이를 넘으니 바위로 읽힌다. 판정 권고대로
    #   **텍스처 폐기(상수 초록) + 크기 축소 + 개수 증가 + 배치 불규칙화**.
    #     ㉠ 재질  : grass 텍스처 → tuft 상수색 3종(밝은 초록·마른 초록 변주,
    #                shrub 대비 2.2배 밝음 → '풀' vs '관목' 층 구분).
    #     ㉡ 치수  : rx 0.70 → 0.30/0.42/0.46, rz 0.42 → 0.17/0.24/0.26
    #                (최고 높이 0.74 → 0.54 m = 무릎 아래 → 초지 인상).
    #                판정 권고 rx 0.35~0.45 준수(전열은 더 작게).
    #     ㉢ 개수  : 1행(step 0.85, 편측 9) → **3행**(step 0.26/0.40/0.50).
    #                총 38 → 121 개. 작아진 만큼 촘촘히 깔아 은폐는 강화된다.
    #     ㉣ 불규칙: 등간격 구슬줄 인상을 없애려 세로 간격 자체를 ±35 % 흔들고
    #                (jit_step) 12 % 를 건너뛰어(skip) 군락과 빈틈을 만든다.
    #                축정렬 타원체가 전부 같은 방향으로 눕는 것도 막으려
    #                절반은 rx/ry 를 교환(swap)한다.
    #   · 코리도 침범 검산 — tuft 행은 rx/ry 교환(swap)을 쓰므로 y 반경을
    #     max(rx,ry) 로 잡아야 안전측이다(최악값 = 지터 최대 조합):
    #       rowA0 내측단 = 1.42 − 0.22·0.7 − 0.30·1.18 = 0.912 > 반폭 0.90 ✓
    #       rowA1 내측단 = 1.92 − 0.154 − 0.42·1.18   = 1.270 ✓
    #       rowA2 내측단 = 2.45 − 0.154 − 0.46·1.18   = 1.753 ✓
    #     (시드 결정적이므로 **실측 최솟값 0.942** — verge_selfcheck ①)
    #   · 은폐: 흙띠 외곽선(|y|=1.30)의 x 방향 피복률 **91.7 %**(구 rowA 는
    #     덩치가 커 seam 을 넘겨 덮었지만 그 자체가 바위밭이었다). 나머지 8 %
    #     빈틈은 의도 — 풀 뭉치 사이로 흙이 조금 보이는 것이 초지의 정상이다.
    #   · 접지 조건 rz·embed ≥ rx·구배(0.261) — 스케일 지터에 불변(양변 s 비례).
    #     tuft 행은 교환 시 x 반경이 작아지므로 미교환(원본 rx)이 최악값:
    #       rowA0 0.17×0.5=0.085 ≥ 0.30×0.261=0.078 ✓
    #       rowA1 0.24×0.5=0.120 ≥ 0.42×0.261=0.110 ✓
    #       rowA2 0.26×0.5=0.130 ≥ 0.46×0.261=0.120 ✓
    #       rowB  0.32×0.5=0.160 ≥ 0.60×0.261=0.157 ✓ (shrub — 교환 안 함)
    #       rowC  0.30×0.5=0.150 ≥ 0.55×0.261=0.144 ✓
    #   rows: (cy, rx, ry, rz, step, x0, x1, mtl)  — mtl "tuft"|"shrub"
    verge=dict(embed=0.50, jit_pos=0.22, jit_scale=0.18, jit_step=0.35,
               skip=0.12, swap=0.5,
               rows=((1.42, 0.30, 0.30, 0.17, 0.26, -0.80, 6.40, "tuft"),
                     (1.92, 0.42, 0.36, 0.24, 0.40, -0.75, 6.35, "tuft"),
                     (2.45, 0.46, 0.40, 0.26, 0.50, -0.60, 6.25, "tuft"),
                     (3.05, 0.60, 0.66, 0.32, 1.10, -0.50, 6.20, "shrub"),
                     (3.85, 0.55, 0.62, 0.30, 1.75, -0.20, 6.00, "shrub"))),

    # 벤치 5 (v4-D4: 1 → 5). (cx, cy, gz, yaw)
    # [v5.1 전역 규약 3] 격자·정렬 배치 금지 → 전부 앵커(나무 그늘·관목 군락·
    #   길 가장자리) 옆으로 이동하고 yaw 를 ±3~8° 지터한 비정수각으로.
    #   · (11.7, 2.55) 나무 L1(12,4) 수관 아래 — 좌판 축 y방향(yaw 96)이라
    #     좌판 끝(11.7, 3.45)이 줄기(12,4)에서 0.62 m 이격(관통 없음).
    #   · (−8.7, 3.3) 관목 군락(−10,3) 옆 1.44 m · (10.1,−3.05) 나무 L0(9,−3)
    #     옆 1.10 m · (17.2, 3.1) 관목(16,3) 옆 1.20 m · (−13.0,−2.55) 길 가장자리
    #     (중심선 1.18 → 노면 가장자리에서 0.19 m).
    #   전부 길 반폭 0.99 밖 — 벤치가 노면을 밟는 배치 0.
    benches=[(11.7, 2.55, "lower", 96.0), (-8.7, 3.3, 0.0, 94.0),
             (-13.0, -2.55, 0.0, 4.5), (10.1, -3.05, "lower", 93.0),
             (17.2, 3.1, "lower", 87.0)],
    # v4-D1 [최우선] 목재 이정표 — 한 컷에 '공원 산책로' 확정
    # [v5.1] (−3.5, 2.2)는 재사행된 길(그 x 에서 중심 y≈−1.36)에서 3.5 m 떨어진
    #   허허벌판이었다 → 길 바깥 곡선(가장자리 −1.80)에서 0.15 m 옆으로 이동.
    signpost=dict(cx=-2.3, cy=-1.95, post_r=0.07, post_h=2.0,
                  arm=(0.9, 0.06, 0.16), arm_off=0.45,
                  arms=((1.75, 22.0), (1.5, 203.0))),   # (z, yaw)
    # v4-D2 안내 지도 게시판
    # [v5.1] 구 (−6.0,−2.6)은 재사행된 길 띠(중심 −2.43, 가장자리 −3.33) **안쪽**
    #   이라 노면 한복판에 선다 → 길 바깥 0.35 m 로 이동(나무 U0(−6,−4)와 2.5 m).
    board=dict(cx=-8.5, cy=-4.15, thick=0.10, width=1.4, z0=1.0, z1=1.9,
               post_r=0.05),
    # v4-D5 쓰레기통 3 — [v5.1] 재사행된 길 가장자리(0.2~0.5 m)로 재배치
    bins=[(-3.2, -2.85, 0.0), (7.4, -1.9, "lower"), (14.3, 1.5, "lower")],
    bin_spec=dict(r=0.26, h=0.85),
    # v4-D6 파고라/쉼터
    pergola=dict(x0=10.0, x1=13.0, y0=4.5, y1=7.5, z_roof=2.5, post_r=0.09,
                 roof_t=0.14),
    # v4-D11 낙엽 무더기 4 (계절감·바닥 다양성)
    # [v5.1] 재사행된 길 위/가장자리(중심선에서 ≤0.3 m)로 재배치 — 낙엽은
    #   다져진 노면에 쌓여야 '사람이 다니는 길'로 읽힌다.
    leaf_piles=[(-9.0, -2.50, 0.0), (-2.0, -0.75, 0.0), (8.0, -0.95, "lower"),
                (15.0, 0.60, "lower")],
    leaf=dict(sx=1.6, sy=1.2, h=0.05, proud=0.002),

    # cue_railing True 시 통나무 손스침 1선 (y=+1.0).
    log_rail=dict(y=1.0, rail_r=0.05, post_r=0.05, rail_h=0.9, spacing=1.2),

    # --- 재질: texture_scale용 물리 크기[m/타일] ---
    material=dict(
        # S4-4: dirt_park scale 2.0→3.0 (낙엽 입자 축소), 채도 낮춤 tint.
        scale=dict(dirt_park=3.0, gravel=0.5, grass=1.4, wood_dark=1.0),
        dirt_tint=(0.92, 0.88, 0.80),           # 낙엽 과채도 완화 (기본 흙 지면)
        grass_tint=(0.55, 0.68, 0.42),          # 타일 반복 완화 + 초록 틴트
        hedge_tint=(0.46, 0.58, 0.32),          # v4-B2 생울타리 밴드(배경·하층식생)
        # [v5 판정 반영] 관목 blob 전용 상수 재질. 판정 (c)"틴트를 잔디와 더
        #   분리" 요구 + 기존 수관 알베도 규약(0.025~0.06 계열 · rough 1.0 ·
        #   specular 0) 유지. canopy_a/b 보다 한 단계 어둡고 채도를 낮춰
        #   '나무 수관'과 '지면 관목'이 구분되게 한다.
        shrub=(0.030, 0.047, 0.021), shrub_rough=1.0,
        # [v6 판정] verge 초지 밴드 전용 상수색 3종 — grass 텍스처(uv 1.6)가
        #   타원체 위에서 '이끼 낀 바위'가 되던 문제의 직접 원인 제거.
        #   shrub(0.030,0.047,0.021) 대비 2.2배 밝고 채도는 낮춰 **잔디 층 > 관목
        #   층** 의 명도 서열을 만든다(잔디 텍스처 실효 알베도 ≈ 0.11/0.14/0.08
        #   보다는 어두워야 뭉치로 읽힌다). 3종 = 진초록·연초록·마른풀.
        tuft=((0.070, 0.105, 0.042), (0.082, 0.112, 0.050),
              (0.078, 0.096, 0.038)), tuft_rough=1.0,
        # [v5.1 전역 규약 4] 인스턴스 틴트 지터 ±5 % — 재질 신설을 최소화하려
        #   기저색은 그대로 두고 변종 개수만 3(shrub)·2(canopy)로 늘린다.
        tint_jitter=0.05,
        # S4-3: 나무 색 scene01 최종값 통일
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,   # 나무 줄기·지지대
        # v4-B(공통): 수관 알베도 상향 (구형 blob 실루엣만 남던 문제 완화)
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030),
        canopy_rough=1.0,
        tactile_color=(0.85, 0.72, 0.10),       # cue_tactile 상수 황색
        sign_face=(0.55, 0.56, 0.58),           # v4-D2 게시판 지도면
    ),

    # --- 조명: scene01 light dict 그대로 + SUN_AZ_OFFSET=171.5 ---
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


# 파라미터 오버라이드 (A/B 렌더 비교용 — 기본 실행엔 영향 없음, scene01 패턴)
_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

# SCENE_CONFIG 환경변수 오버라이드 (토글 무결성 검증 파이프라인용)
_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [D] 경로
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene04")

# 씬이 사용하는 텍스처 역할만 검사.
ASSET_ROLES = ["dirt_park", "gravel", "grass", "wood_dark", "hdri", "mdl"]


def slope_z(x):
    """사면 상면 z 보간 (x 0..run → 0..−drop, 밖은 클램프)."""
    sl = PARAMS["slope"]
    t = max(0.0, min(x / sl["run"], 1.0))
    return sl["z0"] - sl["drop"] * t


def _resolve_gz(spec_gz, cx):
    """gz 지정 해석: 'slope'→사면 보간, 'lower'→하부 평탄, 숫자→그대로."""
    if spec_gz == "slope":
        return slope_z(cx)
    if spec_gz == "lower":
        return PARAMS["lower"]["z_top"]
    return float(spec_gz)


def tint_jitter(color, seed, amp=None):
    """[v5.1 전역 규약 4] 인스턴스별 ±amp 색 지터(결정적).

    같은 상수색을 수십 인스턴스가 공유하면 '복제 배치'로 읽힌다. 기저색을
    바꾸지 않고 시드로 ±5 % 만 흔든다."""
    if amp is None:
        amp = PARAMS["material"]["tint_jitter"]
    rnd = random.Random(1000003 * (int(seed) + 11))
    return tuple(round(max(0.005, c * (1.0 + rnd.uniform(-amp, amp))), 5)
                 for c in color)


# ===========================================================================
# [D2] [v6] verge 개체 생성기 — **조립기와 검산기가 같은 좌표를 쓰도록** 분리.
#   (구조상 build_verge 안에 있던 루프. 시드 결정적이므로 Isaac 없이도 실측
#    최소 |y| / 접지 여유를 계산할 수 있다 → verge_selfcheck)
#   yield: (px, py, cz, ax, ay, az, kind, k, row)  — cz/a* 는 최종 월드값
# ===========================================================================
def verge_instances():
    vg = PARAMS["verge"]
    emb, jp, js = vg["embed"], vg["jit_pos"], vg["jit_scale"]
    jstep, skip, swap = vg["jit_step"], vg["skip"], vg["swap"]
    for r, (cy0, rx, ry, rz, step, x0, x1, kind) in enumerate(vg["rows"]):
        for sgn in (1.0, -1.0):
            k, x = 0, x0
            while x <= x1 + 1e-6:
                rnd = random.Random(int((r * 97 + k * 7919
                                         + (0 if sgn > 0 else 3571))))
                x_next = x + step * (1.0 + rnd.uniform(-jstep, jstep))
                k += 1
                # [v6] 12 % 결측 — 등간격 구슬줄이 아니라 군락/빈틈이 생긴다.
                if rnd.random() < skip:
                    x = x_next
                    continue
                px = x + rnd.uniform(-jp, jp)
                py = sgn * (cy0 + rnd.uniform(-jp, jp) * 0.7)
                s = 1.0 + rnd.uniform(-js, js)
                # [v6] 축정렬 타원체가 전부 같은 방향으로 눕지 않도록 절반은
                #   rx/ry 교환(add_sphere 에 회전 인자가 없다). **tuft 행 한정** —
                #   shrub 행은 ry>rx 라 교환하면 x 반경이 커져 접지 부등식
                #   (rz·embed ≥ rx·구배)이 깨진다(rowB 0.160 < 0.172).
                ax, ay = ((ry, rx) if (kind == "tuft" and rnd.random() < swap)
                          else (rx, ry))
                yield (px, py, slope_z(px) + rz * s * (1.0 - emb),
                       ax * s, ay * s, rz * s, kind, k, r)
                x = x_next


def verge_selfcheck(verbose=True):
    """[v6] verge 재작업 좌표 검산 — 계단 침범 0 · 부유 0 · 은폐 연속성.

    ① 침범: 개체의 y 내측단 |py| − ay 가 계단 반폭 0.90 보다 큰가(실측 최솟값).
    ② 부유: 사면 구배 위 타원체 하단이 지면 아래로 물리는가.
       하단 최고점(상류측 접선) z = cz − az, 그 x 에서 지면 = slope_z(px);
       구배 보정은 rx·|dz/dx| 만큼 상류가 뜨므로 여유 = az·embed − ax·0.261.
    ③ 은폐: 노출 흙띠(|y| 0.90~1.70)를 x 방향으로 몇 % 구간에서 덮는가
       (0.1 m 격자로 x −0.75..6.35 를 훑어 어느 개체의 XY 타원 안에 드는지).
    반환: (ok, diag)
    """
    sl = PARAMS["slope"]
    grade = sl["drop"] / sl["run"]
    inst = list(verge_instances())
    half = PARAMS["stairs"]["y1"]                       # 0.90
    min_gap = min(abs(p[1]) - p[4] for p in inst)
    min_ground = min(p[5] * PARAMS["verge"]["embed"] - p[3] * grade
                     for p in inst)
    # ③ 흙띠 피복률 (편측, y=1.30 대표선)
    xs = [(-0.75 + 0.1 * i) for i in range(72)]
    cov = 0
    for xq in xs:
        hit = False
        for px, py, _cz, ax, ay, _az, _k, _i, _r in inst:
            if py <= 0.0:
                continue
            if ((xq - px) / ax) ** 2 + ((1.30 - py) / ay) ** 2 <= 1.0:
                hit = True
                break
        cov += 1 if hit else 0
    ok = (min_gap > half) and (min_ground >= 0.0) and (cov / len(xs) > 0.90)
    if verbose:
        n_t = sum(1 for p in inst if p[6] == "tuft")
        print("=" * 64)
        print("scene04 [v6] verge(초지 밴드) 재작업 검산")
        print("=" * 64)
        print(f"  개체 수            {len(inst)} (tuft {n_t} / shrub "
              f"{len(inst) - n_t})   구 38개")
        print(f"  ① 계단 침범 여유   min(|y|−ry) = {min_gap:.3f} m "
              f"> 반폭 {half:.2f} → {'OK' if min_gap > half else 'FAIL'}")
        print(f"  ② 접지 여유        min(rz·emb − rx·구배) = {min_ground:+.4f} "
              f"→ {'OK' if min_ground >= 0 else 'FAIL'}")
        print(f"  ③ 흙띠(y=1.30) 피복 {100.0 * cov / len(xs):.1f} % "
              f"→ {'OK' if cov / len(xs) > 0.90 else 'FAIL'}")
        print(f"  최대 높이          "
              f"{max(p[2] - slope_z(p[0]) + p[5] for p in inst):.2f} m "
              f"(구 0.74 m)")
        print("=" * 64)
    return ok, dict(n=len(inst), min_gap=min_gap, min_ground=min_ground,
                    cover=cov / len(xs))


# ===========================================================================
# [E] 카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷.
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)
    # trail_approach: 상부 길 위 h0.9에서 계단 방향(+X)
    views["trail_approach"] = dict(eye=[-6.0, 0.0, 0.9], tgt=[0.8, 0.0, -0.35])
    # step_detail: 계단이 더 잘 담기게 (S4-6, 약간 측사 + 하강)
    views["step_detail"] = dict(eye=[-2.0, 0.6, 0.75], tgt=[1.8, 0.0, -0.55])
    # below_lookup: 하부에서 역방향(−X)으로 계단 올려봄
    views["below_lookup"] = dict(eye=[8.5, 0.0, 0.95], tgt=[2.0, 0.0, -0.55])
    # canopy_anchor: 상부 h1.6에서 하부 나무 수관이 눈높이에 걸리는 구도
    views["canopy_anchor"] = dict(eye=[-2.0, -1.0, 1.6], tgt=[12.0, -1.0, 0.85])
    return views


# ===========================================================================
# [F] 씬 조립 + 메인 (__main__ 전용)
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. trail_approach   — 상부 길에서 계단이 사면에 접혀 단차가 모호해지는가
 2. step_detail      — 침목(목재) 라이저 vs 마사토 디딤면 대비, 단코 절단선
 3. below_lookup     — 하부에서 불규칙 단높이 9단이 읽히는가
 4. canopy_anchor    — 하부 나무 수관이 상부 눈높이에 걸리는 앵커 구도
 5. cue 토글         — railing/tactile/nosing ON/OFF 시 위험 기하 불변인가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # ── [v6] 좌표 검산만 수행하고 종료 (Isaac 부팅 불필요) ──
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        verge_selfcheck()
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    # ── Isaac Sim 부팅 (SimulationApp 무조건 먼저 — scene_common.boot) ──
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene04")
    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene04"

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def make_mtls():
        S = mp["scale"]
        M = {}
        M["dirt"] = sc.make_pbr(
            stage, "/World/Looks/Dirt", sc.tex_path("dirt_park", "diff"),
            sc.tex_path("dirt_park", "nor"), sc.tex_path("dirt_park", "rough"),
            S["dirt_park"], tint=mp["dirt_tint"])
        M["dirt_path"] = sc.make_pbr(
            stage, "/World/Looks/DirtPath", sc.tex_path("dirt_park", "diff"),
            sc.tex_path("dirt_park", "nor"), sc.tex_path("dirt_park", "rough"),
            S["dirt_park"], tint=PARAMS["path"]["tint"])
        M["gravel"] = sc.make_pbr(
            stage, "/World/Looks/Gravel", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            S["gravel"])
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            S["grass"], tint=mp["grass_tint"])
        M["wood_dark"] = sc.make_pbr(
            stage, "/World/Looks/WoodDark", sc.tex_path("wood_dark", "diff"),
            sc.tex_path("wood_dark", "nor"), sc.tex_path("wood_dark", "rough"),
            S["wood_dark"])
        # 상수 컬러 재질 (나무 줄기·수관·점자)
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        # [v5.1] 수관 4종(기저 2색 × ±5 % 지터 2) — 나무별로 다른 쌍을 물려
        #   같은 두 색이 전 수목에 반복되는 인상을 없앤다.
        M["canopy"] = []
        for i, base in enumerate((mp["canopy_a"], mp["canopy_b"])):
            for j in range(2):
                M["canopy"].append(sc.make_pbr(
                    stage, f"/World/Looks/Canopy{i}{j}",
                    diffuse_color=tint_jitter(base, 10 * i + j),
                    roughness_const=mp["canopy_rough"], specular_level=0.0))
        M["canopy_a"], M["canopy_b"] = M["canopy"][0], M["canopy"][2]
        # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
        M["tactile"] = sc.tactile_pbr(stage, "/World/Looks/Tactile")
        M["hedge"] = sc.make_pbr(
            stage, "/World/Looks/Hedge", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            1.2, tint=mp["hedge_tint"])
        # [v5 판정 반영] 관목 blob 전용 (수관 규약: rough 1.0 · specular 0)
        # [v5.1] 3종 ±5 % 지터 (군락 내 개체차)
        M["shrub_v"] = [sc.make_pbr(stage, f"/World/Looks/Shrub{i}",
                                    diffuse_color=tint_jitter(mp["shrub"],
                                                              40 + i),
                                    roughness_const=mp["shrub_rough"],
                                    specular_level=0.0) for i in range(3)]
        M["shrub"] = M["shrub_v"][0]
        # [v6 판정] verge 초지 밴드 — 구 "grass 텍스처(uv 1.6) + hedge 틴트"는
        #   확대 노멀맵 탓에 바위로 렌더됐다 → **상수색 3종**(수관 규약과 동일:
        #   rough 1.0 · specular 0)으로 교체. 개체별 ±5 % 틴트 지터는 유지.
        M["verge"] = [sc.make_pbr(
            stage, f"/World/Looks/Verge{i}",
            diffuse_color=tint_jitter(c, 60 + i),
            roughness_const=mp["tuft_rough"], specular_level=0.0)
            for i, c in enumerate(mp["tuft"])]
        M["sign_face"] = sc.make_pbr(stage, "/World/Looks/SignFace",
                                     diffuse_color=mp["sign_face"],
                                     roughness_const=0.6)
        # 디딤면: cue_material_break — True=gravel(마사토), False=주변 흙과 융합
        M["tread"] = M["gravel"] if cfg["cue_material_break"] else M["dirt"]
        return M

    # -------------------------------------------------------------------
    # 지형
    # -------------------------------------------------------------------
    def _flat(prefix, d, mtl):
        sc.add_box(stage, prefix,
                   ((d["x0"] + d["x1"]) / 2.0, (d["y0"] + d["y1"]) / 2.0,
                    d["z_top"] - d["thick"] / 2.0),
                   (d["x1"] - d["x0"], d["y1"] - d["y0"], d["thick"]),
                   mtl, collider=True)

    def build_ground(M):
        """상부 평탄 (항상). 기본 지면 = grass (S4-1)."""
        # [W2-0 · P-A] Slabs ground_kit decorates — keep the displacement skin
        # off them so the +0.6..2 mm decals are not buried (spec §1.2).
        sc.skin_exclude(f"{ROOT}/UpperFlat", f"{ROOT}/ConnectU")
        _flat(f"{ROOT}/UpperFlat", PARAMS["upper"], M["grass"])

    def build_slope_zone(M):
        """하부 평탄 + 사면 (hazard on). 사면 = grass 기본 + 회랑측 dirt 밴드
        + 트림 스트립. 계단 회랑(y ±corridor_y) 자체는 비움(계단이 채움)."""
        _flat(f"{ROOT}/LowerFlat", PARAMS["lower"], M["grass"])
        sl = PARAMS["slope"]
        run, drop, thk = sl["run"], sl["drop"], sl["thick"]
        cy, to, dy, fy = (sl["corridor_y"], sl["trim_out"], sl["dirt_y"],
                          sl["flank_y"])
        tov = sl["trim_over"]
        for tag, sgn in (("P", 1.0), ("N", -1.0)):
            gy0, gy1 = sorted((sgn * dy, sgn * fy))     # grass 플랭크(바깥)
            sc.build_slope(stage, f"{ROOT}/SlopeGrass_{tag}", sl["x0"], sl["z0"],
                           run, drop, gy0, gy1, thk, M["grass"], collider=False)
            dy0, dy1 = sorted((sgn * to, sgn * dy))     # dirt 밴드(회랑측)
            sc.build_slope(stage, f"{ROOT}/SlopeDirt_{tag}", sl["x0"], sl["z0"],
                           run, drop, dy0, dy1, thk, M["dirt"], collider=True)
            ty0, ty1 = sorted((sgn * cy, sgn * to))     # S4-5 트림 봉합 스트립
            sc.build_slope(stage, f"{ROOT}/SlopeTrim_{tag}", sl["x0"],
                           sl["z0"] + tov, run, drop, ty0, ty1, thk, M["dirt"],
                           collider=False)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 사면·계단·하부를 z=0 평지(grass)로 통일.
        상부 평탄(x ≤0)은 build_ground가 이미 깖 → x 0..lower.x1만 채운다."""
        lo = PARAMS["lower"]
        x0, x1 = PARAMS["slope"]["x0"], lo["x1"]
        y0, y1 = lo["y0"], lo["y1"]
        th = PARAMS["upper"]["thick"]
        sc.add_box(stage, f"{ROOT}/FlatFill",
                   ((x0 + x1) / 2.0, (y0 + y1) / 2.0, 0.0 - th / 2.0),
                   (x1 - x0, y1 - y0, th), M["grass"], collider=True)

    def tree_no_stake(M, prefix, cx, cy, gz, trunk_h, slot=0):
        """v4-B3: 자연 산책로에 신식재 지지대 3본은 가장 어색한 요소 →
        지지대 치수를 0에 근접시켜 무력화. (제안: scene_common.build_tree 에
        stakes=False 인자 추가 — 픽스로그 참조)
        [v5.1] 나무마다 수관 재질 쌍을 바꿔 색 반복을 끊는다(수형·크기 변형은
        scene_common.build_tree v2 가 좌표 시드로 이미 수행)."""
        ca, cb = ((0, 2), (1, 3), (2, 1), (3, 0))[int(slot) % 4]
        sc.build_tree(stage, prefix, cx, cy, gz, M["wood"], M["canopy"][ca],
                      M["canopy"][cb], trunk_r=PARAMS["tree"]["trunk_r"],
                      trunk_h=trunk_h, stake_r=0.004, stake_h=0.02,
                      stake_off=0.2)

    def build_background(M):
        """원경 폐쇄 (S4-2, 상시): 배경 생울타리 밴드 + 나무 라인."""
        hh = PARAMS["bg_hedge"]["h"]
        for n, b in enumerate(PARAMS["bg_hedges"]):
            gz = _resolve_gz(b["gz"], (b["x0"] + b["x1"]) / 2.0)
            sc.build_hedge(stage, f"{ROOT}/BgHedge_{n}", b["x0"], b["y0"],
                           b["x1"], b["y1"], hh, mtl=M["hedge"], base_z=gz)
        # v4-A3: 사면 구간(x 0..5.55) 봉합 — 구배를 따라 기운 밴드
        sl = PARAMS["slope"]
        for n, b in enumerate(PARAMS["bg_slope_hedges"]):
            sc.build_slope(stage, f"{ROOT}/BgSlopeHedge_{n}", sl["x0"],
                           sl["z0"] + hh, sl["run"], sl["drop"],
                           b["y0"], b["y1"], hh, M["hedge"], margin=0.0,
                           collider=True)
        # 프림명에 좌표 사용 금지 — 음수 '-'는 USD 식별자 불허 (감독 핫픽스)
        for bi, b in enumerate(PARAMS["bg_trees"]):
            gz = _resolve_gz(b["gz"], b["cx"])
            tree_no_stake(M, f"{ROOT}/BgTree_{bi}", b["cx"], b["cy"], gz,
                          b["trunk_h"], slot=bi)

    # -------------------------------------------------------------------
    # 침목 계단 (불규칙 단) + 침목 라이저 + 고정말뚝
    # -------------------------------------------------------------------
    def build_sleeper_stairs(M):
        st = PARAMS["stairs"]
        # 솔리드 계단 (디딤면 = 마사토/흙). z_top=0에서 +X로 하강, 불규칙 단.
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            riser=0.0, tread=0.0, n=0, base_z=st["base_z"], mtl=M["tread"],
            riser_list=RISERS, tread_list=TREADS, z_top=st["z_top"],
            collider=True)
        # 각 단 전연부(xb) 침목 + 고정말뚝. _stair_steps로 단 좌표 재사용.
        steps = sc._stair_steps(st["x0"], 0.0, 0.0, 0, st["z_top"],
                                RISERS, TREADS)
        cy = (st["y0"] + st["y1"]) / 2.0
        Ly = st["y1"] - st["y0"]
        thk = st["sleeper_thick"]
        over = st["sleeper_over"]
        for i, (xa, xb, ztop) in enumerate(steps):
            riser_i = RISERS[i] if i < len(RISERS) else RISERS[-1]
            h = riser_i + over                       # 침목 높이
            z_hi = ztop + over                       # 상면 = 단 상면 + 0.02
            cz = z_hi - h / 2.0
            bx = xb - thk / 2.0                      # 전연부 안쪽 두께 0.15
            sc.add_box(stage, f"{ROOT}/Sleeper_{i}", (bx, cy, cz),
                       (thk, Ly, h), M["wood_dark"], collider=True)
            # 고정말뚝 2본/단 (침목 전면 양단 y ±0.8)
            scz = z_hi - st["stake_h"] / 2.0
            for sgn, ptag in ((1.0, "P"), (-1.0, "N")):
                sc.add_cylinder(
                    stage, f"{ROOT}/Stake_{i}_{ptag}",
                    (xb, sgn * st["stake_y"], scz),
                    st["stake_r"], st["stake_h"], M["wood_dark"])

    # -------------------------------------------------------------------
    # 길 (흙길 띠) — 세그 박스 3개로 완만히 꺾임, 1mm 돌출
    # -------------------------------------------------------------------
    def build_paths(M):
        """v4-A1: 중심선 폴리라인의 각 구간을 rotZ 회전 박스로 깐다.
        세그 중심 = 두 절점의 중점, 길이 = 절점 간 거리 + overlap(이음 겹침),
        yaw = atan2(dy, dx). build_rot_group(피벗=세그 중심)에 박스를 넣으면
        그 박스가 피벗 기준으로 회전 → 계단형 어긋남 없이 연속 사행."""
        pa = PARAMS["path"]
        w, th, proud, ov = pa["width"], pa["thick"], pa["proud"], pa["overlap"]
        wj = pa["width_jit"]

        def _seg(prefix, pts, surf_z, seed):
            z_hi = surf_z + proud
            cz = z_hi - th / 2.0
            rnd = random.Random(seed)
            for n in range(len(pts) - 1):
                (xa, ya), (xb, yb) = pts[n], pts[n + 1]
                cx, cy = (xa + xb) / 2.0, (ya + yb) / 2.0
                L = math.hypot(xb - xa, yb - ya) + ov
                yaw = math.degrees(math.atan2(yb - ya, xb - xa))
                # [v5.1] 세그 폭 ±10 % — 다짐 폭이 균일한 인공 띠 인상 제거.
                #   꺾임 절점에서 인접 세그 폭이 달라도 overlap 0.7 이 이음을
                #   덮으므로 개구가 생기지 않는다(폭 차 ≤0.36 m ≪ 겹침 길이).
                ws = w * (1.0 + rnd.uniform(-wj, wj))
                grp = sc.build_rot_group(stage, f"{prefix}_{n}", (cx, cy), yaw)
                sc.add_box(stage, f"{grp}/Box", (cx, cy, cz), (L, ws, th),
                           M["dirt_path"], collider=True)

        _seg(f"{ROOT}/PathU", pa["upper"], PARAMS["upper"]["z_top"], 20260727)
        _seg(f"{ROOT}/PathL", pa["lower"], PARAMS["lower"]["z_top"], 51)

        # 계단 전후 3m dirt 접속부 (grass 지면 위 흙 트레일 랜딩)
        cn = PARAMS["connect"]
        L, hy = cn["length"], cn["half_y"]
        x_bot = PARAMS["stairs"]["x0"] + STAIR_RUN         # 5.55
        for tag, cx, surf_z in (
                ("U", PARAMS["stairs"]["x0"] - L / 2.0, PARAMS["upper"]["z_top"]),
                ("L", x_bot + L / 2.0, PARAMS["lower"]["z_top"])):
            cz = (surf_z + proud) - th / 2.0
            sc.add_box(stage, f"{ROOT}/Connect{tag}", (cx, 0.0, cz),
                       (L, 2 * hy, th), M["dirt_path"], collider=True)

    # -------------------------------------------------------------------
    # 자연물 (나무·관목·벤치)
    # -------------------------------------------------------------------
    def build_verge(M):
        """[v5.1] 풀숲 사이 침목계단 — 계단 양측 초지 융기 밴드 + 관목 2열.

        각 개체는 눌린 타원체(add_sphere). 사면 구배는 형상이 아니라 **배치
        높이**로만 반영(slope_z) — v5 판정이 폐기한 '경사 슬래브 판떼기'를
        되풀이하지 않기 위함. 접지는 중심을 gz + rz(1−embed) 에 두어 하단을
        rz·embed 만큼 매입한다(PARAMS.verge 주석의 부유 방지 부등식 참조).
        위치·크기 지터는 좌표 시드 결정적 — 재실행 시 동일.
        [v6] 좌표 생성은 verge_instances() 로 분리(검산기와 동일 좌표 보장)."""
        n = 0
        for px, py, cz, ax, ay, az, kind, k, r in verge_instances():
            mtl = (M["verge"][(k + r) % len(M["verge"])] if kind == "tuft"
                   else M["shrub_v"][(k + r) % len(M["shrub_v"])])
            sc.add_sphere(stage, f"{ROOT}/Verge_{n}", (px, py, cz),
                          (ax, ay, az), mtl)
            n += 1
        return n

    def build_nature(M):
        for ti, spec in enumerate(PARAMS["trees"]):
            gz = _resolve_gz(spec["gz"], spec["cx"])
            tree_no_stake(M, f"{ROOT}/Tree_{spec['name']}", spec["cx"],
                          spec["cy"], gz, spec["trunk_h"], slot=ti + 1)
        for n, spec in enumerate(PARAMS["trees_extra"]):        # v4-D9
            gz = _resolve_gz(spec["gz"], spec["cx"])
            tree_no_stake(M, f"{ROOT}/TreeX_{n}", spec["cx"], spec["cy"], gz,
                          spec["trunk_h"], slot=n + 2)
        # [v5 판정 반영 / 재수정] 관목 군락 = 눌린 타원체 3개 중첩(수관 blob).
        #   v4 의 '경사 슬래브 + 박스 3장 중첩'은 각진 판떼기로 렌더돼 폐기.
        #   사면 여부와 무관하게 축정렬 회전체를 쓰고, 구배는 각 blob 의
        #   중심 x 에서 지면 z 를 뽑는 것(_resolve_gz)으로만 반영한다.
        #   → 사면/평탄 분기 자체가 사라져 경사 전단(shear) 아티팩트가 원천 소멸.
        hb = PARAMS["hedge"]
        emb = hb["embed"]
        for n, spec in enumerate(PARAMS["hedges"]):
            for j, (dx, dy, rx, ry, rz) in enumerate(hb["blobs"]):
                cx, cy = spec["cx"] + dx, spec["cy"] + dy
                gz = _resolve_gz(spec["gz"], cx)       # 배치 높이에만 구배 반영
                sc.add_sphere(stage, f"{ROOT}/Hedge_{n}_{j}",
                              (cx, cy, gz + rz * (1.0 - emb)),
                              (rx, ry, rz),
                              M["shrub_v"][(n + j) % len(M["shrub_v"])])
        # [v5.1] v4-D8 사면 하층식생 밴드(build_slope 경사 판 4장) 폐기 →
        #   build_verge 의 관목 2·3열이 같은 영역을 타원체로 대체한다.
        # v4-D4: 벤치 5
        for n, (bx, by, gz_spec, yaw) in enumerate(PARAMS["benches"]):
            gz = _resolve_gz(gz_spec, bx)
            sc.build_bench(stage, f"{ROOT}/Bench_{n}", bx, by, gz,
                           M["wood_dark"], yaw=yaw)

    def build_park_props(M):
        """v4-D1/D2/D5/D6/D11 — '공원 산책로'로 읽히게 하는 인공물."""
        # D1 목재 이정표 (기둥 + 방향판 2, 서로 다른 방위)
        sp = PARAMS["signpost"]
        gz = _resolve_gz(0.0, sp["cx"])
        sc.add_cylinder(stage, f"{ROOT}/SignPost/Post",
                        (sp["cx"], sp["cy"], gz + sp["post_h"] / 2.0),
                        sp["post_r"], sp["post_h"], M["wood_dark"],
                        collider=True)
        for k, (az, yaw) in enumerate(sp["arms"]):
            grp = sc.build_rot_group(stage, f"{ROOT}/SignPost/Arm_{k}",
                                     (sp["cx"], sp["cy"]), yaw)
            sc.add_box(stage, f"{grp}/Box",
                       (sp["cx"] + sp["arm_off"], sp["cy"], gz + az),
                       sp["arm"], M["wood_dark"])
        # D2 안내 지도 게시판
        bo = PARAMS["board"]
        bz = _resolve_gz(0.0, bo["cx"])
        zc = (bo["z0"] + bo["z1"]) / 2.0
        sc.add_box(stage, f"{ROOT}/Board/Panel", (bo["cx"], bo["cy"], bz + zc),
                   (bo["thick"], bo["width"], bo["z1"] - bo["z0"]),
                   M["wood_dark"])
        sc.add_box(stage, f"{ROOT}/Board/Face",
                   (bo["cx"] - bo["thick"] / 2.0 - 0.006, bo["cy"], bz + zc),
                   (0.012, bo["width"] - 0.18, (bo["z1"] - bo["z0"]) - 0.14),
                   M["sign_face"])
        for tag, sgn in (("A", -1.0), ("B", 1.0)):
            sc.add_cylinder(stage, f"{ROOT}/Board/Post_{tag}",
                            (bo["cx"], bo["cy"] + sgn * (bo["width"] / 2.0
                                                         - 0.12),
                             bz + bo["z1"] / 2.0),
                            bo["post_r"], bo["z1"], M["wood_dark"],
                            collider=True)
        # D5 쓰레기통 3
        bn = PARAMS["bin_spec"]
        for n, (bx, by, gz_spec) in enumerate(PARAMS["bins"]):
            bzz = _resolve_gz(gz_spec, bx)
            sc.add_cylinder(stage, f"{ROOT}/Bin_{n}/Body",
                            (bx, by, bzz + bn["h"] / 2.0), bn["r"], bn["h"],
                            M["wood_dark"], collider=True)
            sc.add_cylinder(stage, f"{ROOT}/Bin_{n}/Rim",
                            (bx, by, bzz + bn["h"] + 0.02), bn["r"] * 1.1,
                            0.04, M["wood_dark"])
        # D6 파고라/쉼터
        pg = PARAMS["pergola"]
        sc.build_canopy(stage, f"{ROOT}/Pergola", pg["x0"], pg["x1"],
                        pg["y0"], pg["y1"], pg["z_roof"], pg["post_r"],
                        M["wood_dark"], M["wood_dark"], roof_t=pg["roof_t"],
                        base_z=PARAMS["lower"]["z_top"])
        # D11 낙엽 무더기 4
        lf = PARAMS["leaf"]
        for n, (lx, ly, gz_spec) in enumerate(PARAMS["leaf_piles"]):
            lz = _resolve_gz(gz_spec, lx) + lf["proud"]
            sc.add_box(stage, f"{ROOT}/LeafPile_{n}",
                       (lx, ly, lz - lf["h"] / 2.0),
                       (lf["sx"], lf["sy"], lf["h"]), M["dirt"])

    # -------------------------------------------------------------------
    # cue — 통나무 손스침(railing) · 점자(tactile) · 논슬립(nosing)
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P11 trail_soil (spec §5.7 row 04).
    #   Runs in both hazard arms (GT-E4 twin parity).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        st = PARAMS["stairs"]
        z = PARAMS["upper"]["z_top"] + PARAMS["path"]["proud"]
        gp = gk.plan_ground(
            "trail_soil",
            region=(g["x0"], g["y0"], g["scatter_x1"], g["y1"]),
            z=z, gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(st["x0"]))],
            dists=(2, 5, 10), scene="scene04",
            tactile=(),                 # §12.4 — 자연 씬, 미설치
            extras_args=dict(
                wear_lane=dict(centerline=tuple(g["wear"]),
                               width=g["wear_w"]),
                edge_litter=dict(centerline=tuple(g["wear"])),
                # seams are built below (they are not constant-y lines)
                edge_break=dict(lines=[])),
            seed=4)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(wear=M["dirt"], litter=M["dirt_path"], edge_break=M["dirt"],
                  stain_dirt=M["dirt"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        # ConnectU seam breaking — the dE76 18.9 boundary of the 3.0 x 6.0 m
        #   dirt landing against the grass slab (spec §5.7 / appendix A6).
        cn = PARAMS["connect"]
        x_w, hy = st["x0"] - cn["length"], cn["half_y"]
        seams = (("W", ((x_w, -hy), (x_w, hy))),
                 ("S", ((x_w, -hy), (st["x0"] - 0.05, -hy))),
                 ("N", ((x_w, hy), (st["x0"] - 0.05, hy))))
        nb = 0
        for tag, line in seams:
            nb += gk.build_edge_break(kit, f"{ROOT}/GKit/EdgeBreak_{tag}",
                                      line, z, M["dirt"])["prim_count"]
        print(f"[ground_kit] scene04 P11 · prims {res['prims']} "
              f"+ edge_break {nb} · scatter {res['instances']} · "
              f"delta_max {res['gt_delta_max']:.4f}")
        return res

    def build_cues(M):
        st = PARAMS["stairs"]
        # 통나무 손스침 1선 (y=+1.0): 사면 프로파일 따라 기운 원기둥 + 나무 포스트
        if cfg["cue_railing"]:
            lr = PARAMS["log_rail"]
            y = lr["y"]
            x0, x1 = st["x0"], st["x0"] + STAIR_RUN
            z0 = slope_z(x0) + lr["rail_h"]          # 상단 레일 z
            z1 = slope_z(x1) + lr["rail_h"]          # 하단 레일 z
            L = math.hypot(x1 - x0, z0 - z1)
            ang = math.degrees(math.atan2(z0 - z1, x1 - x0))
            sc.add_cylinder(stage, f"{ROOT}/LogRail/Rail",
                            ((x0 + x1) / 2.0, y, (z0 + z1) / 2.0),
                            lr["rail_r"], L, M["wood_dark"], rotY=90.0 + ang)
            xp = x0 + lr["spacing"] / 2.0
            p = 0
            while xp <= x1 + 1e-6:
                gz = slope_z(xp)
                ph = lr["rail_h"]
                sc.add_cylinder(stage, f"{ROOT}/LogRail/Post_{p}",
                                (xp, y, gz + ph / 2.0),
                                lr["post_r"], ph, M["wood_dark"])
                xp += lr["spacing"]
                p += 1

        # 점자블록 띠: 상단 모서리 0.3m 앞 (공원엔 이례적 — 코드 경로만)
        if cfg["cue_tactile"]:
            sc.build_tactile(stage, f"{ROOT}/Tactile", st["x0"] - 0.3, st["x0"],
                             st["y0"], st["y1"], M["tactile"],
                             z=PARAMS["upper"]["z_top"])

        # 논슬립 단코 띠: 전 단 전연부 (신규 cue_nosing)
        if cfg["cue_nosing"]:
            sc.build_nosing(stage, f"{ROOT}/Nosing", st["x0"], st["y0"],
                            st["y1"], 0.0, 0.0, 0, base_z=st["base_z"],
                            riser_list=RISERS, tread_list=TREADS,
                            z_top=st["z_top"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = make_mtls()
    build_ground(M)                 # 상부 평탄 (grass, 항상)
    if cfg["hazard_stairs"]:
        build_slope_zone(M)         # 하부 평탄 + 사면(grass+dirt 밴드+트림)
        build_sleeper_stairs(M)
    else:
        build_flat_fill(M)          # 대조군: z=0 평지 통일 (grass)
    build_paths(M)                  # 길 띠 + 계단 전후 dirt 접속부
    build_ground_kit(M)             # [W2-D] both arms — GT-E4 twin parity
    build_background(M)             # 원경 폐쇄 (배경 울타리·나무, 상시)
    if cfg["cue_scene_dressing"]:
        build_nature(M)
        build_park_props(M)         # v4-D: 공원 맥락단서 일괄
        if cfg["hazard_stairs"]:
            # [v5.1] 계단 양측 풀숲 — 사면이 존재할 때만(평지 대조군엔 무의미)
            print(f"[씬] verge 초지·관목 {build_verge(M)}개")
    build_cues(M)
    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── 카메라 + 렌더 모드 ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["trail_approach"]
    look_from(_v0["eye"], _v0["tgt"])               # 시작 카메라 = 미장센

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

    # ===================================================================
    # 자동 캡처 모드 (headless 검증 파이프라인 — scene_common.capture_pipeline)
    # ===================================================================
    if capture_mode:
        out_dir_default = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, build_views(), out_dir_default,
                            set_render_mode, look_from)
        simulation_app.close()
        return

    # ===================================================================
    # GUI 룩 체크 모드 (기본)
    # ===================================================================
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]                            # [ / ] 키 사용자 오프셋

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene04_{ts}.png")
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
