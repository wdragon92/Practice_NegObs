# -*- coding: utf-8 -*-
"""
scene03_riverbank.py — NegObs 인공씬 3호: 하천 제방 하행계단 (Isaac Sim 4.5)

사양서 : Docs/multi_scene_brief_v2.md §C(scene03_riverbank) — 유일 사양
공통 라이브러리 : scene_common.py (§A) / 골격 관례 : scene01_campus_stairs.py

유형 (T5 하천 제방): **무난간 × 물면 앵커**.
  둑마루 평탄로에서 사면을 절개해 계단이 하강 → 낮은 시점에서 계단·사면이
  사면에 접혀 완전 소실. 낙차 증거는 오직 **수면(최저부) + 건너편 둔치 +
  눈높이 아래 수관**. **난간 없음이 이 유형의 정체성** (cue_railing 기본 False).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene03_riverbank.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene03_riverbank.py
      NEGOBS_CAPTURE_DIR  : 저장 폴더 (기본 look_check/scene03/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (기본 rt)
      NEGOBS_VIEWS        : 쉼표로 뷰 이름 필터 (기본 전부)

좌표계: Z-up, m, 진행축 +X, 낙차 시작 모서리 = x=0 (둑마루 어깨).

────────────────────────────────────────────────────────────────────────────
기하 정정 (감독 판정 반영):
  브리프 §C의 계단 16단은 낙차 16×0.16=2.56 으로 사면/둔치 낙차 3.2 와 불일치.
  → 감독 결정: **계단 20단으로 연장**. drop 20×0.16=3.2 (사면·둔치 정합),
    run 20×0.35=7.0 → 사면 run=7.0, 둔치 시작 x=7.0, 계단 base_z=-3.6 유지.
    트림 경사보 drop=3.2, cue_railing ground_fn·run·drop 도 20단 기준. 랜딩 없음.
  수변 재정렬: 둔치 x 7.0..18.0, 사석 띠 x0=17.0, 수면 x0=17.5(유효 수변 x≈18).
────────────────────────────────────────────────────────────────────────────
[v5.1 현실성 — 사행 하천 재구성]  사용자 피드백 "하천 굴곡 부자연(직선 수로)".

  ★ 좌표 규약 변경: 하천 평행 요소(둑마루·자갈도로·사면·둔치·산책로·사석·
    수면·건너편 둔치)의 PARAMS x 값은 이제 **월드 X 가 아니라 횡단면 좌표 s**
    (하천 중심선으로부터의 오프셋)다. 월드 X = s + dx(y).
      dx(y) = A1·(cos(2πy/L1) − 1) + A3·(y/40)³      [river_dx]
      A1=6.0 · L1=110 · A3=−2.0
    설계 구속:
      · dx(0)=0, dx′(0)=0  → 계단 회랑(y ±0.95)에서 중심선이 정확히 +Y 를
        향하고 오프셋 0 → **위험 기하(계단·트림·스퍼) 트랜스폼 완전 불변**.
      · 세그 19개(요구 10+ 충족, seg_dy 5.0, y −47.5..47.5).
      · |yaw|max 23.2° · 인접 세그 yaw 변화 ≤6.5° · 측방 dx 진폭 14.8 m.
    수로폭을 22.5 → 15.8 m 로 좁혀(far_bank s 40→34, water s1 40→36)
    사행 진폭/수로폭 = 0.94 ≈ 브리프 요구 "1~2배" 하한. 진폭을 더 키우면
    제방 접선각이 45° 를 넘어(우각호 수준) 95 m 시야 안에서 도리어 부자연.

  ★ 밴드 조립: 각 세그는 build_rot_group(피벗=세그 중심, yaw) 안에 축정렬
    build_slope 박스를 넣어 만든다(전단 배치 — 접힘·자기교차 원천 불가).
      · 세그 로컬 run = 폭/cos(yaw) → 상면의 **월드 X 투영이 정확히 폭**
        → 인접 밴드는 항상 (폭합/2)·(1/cos−cos) 만큼 **겹친다**(틈 0).
      · 세그 길이 = span/cos(yaw) + 0.8 겹침 → 종방향 이음 개구 0.
        (감사 v4 최다 결함 '수면-지면 접합 부유' 재발 차단)
      · 동일 z 코플래너 Z파이팅은 세그·서브밴드 인덱스별 1.5 mm 스태거로 회피.
────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import math
import json
import random
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG — scene01 6키 + cue_nosing(신규). 유형상 무의미한 단서는
#     기본 False (코드 경로는 존재). hazard_stairs 외 토글은 위험 기하 불변.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 계단+사면+둔치를 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        False,   # **이 유형의 정체성** — True면 계단 우측(y=+0.85) 파이프 레일 1선만
    "cue_tactile":        False,   # 제방엔 점자블록 미관행 — 코드 경로만 예약(이 씬 미사용)
    "cue_material_break": True,    # 둑마루 gravel vs 계단 concrete 대비. False→계단도 gravel
    "cue_sign":           False,   # [선택] 미구현 — config 키만 예약
    "cue_scene_dressing": True,    # 볼라드·벤치·관목·나무·흙길 일괄
    "cue_nosing":         False,   # [신규] True → 전 단 논슬립 단코 띠
}


# ===========================================================================
# [B] PARAMS — §C 치수 + 재질/조명/캡처. NEGOBS_PARAMS_OVERRIDE 머지.
#     light dict 는 scene01 noon 검증 상수 그대로. SUN_AZ_OFFSET=171.5.
# ===========================================================================
PARAMS = dict(
    # --- [v5.1] 사행 중심선 (모듈 함수 river_dx/river_yaw 가 참조) ---
    #   y0/y1 은 밴드 조립 범위(지형 y ±40 보다 7.5 넉넉히 — 세그 끝단이
    #   회전하며 안쪽으로 말려 들어와 원경에 하늘 구멍을 내는 것을 막는다).
    meander=dict(A1=6.0, L1=110.0, A3=-2.0, y_ref=40.0,
                 seg_dy=5.0, y0=-47.5, y1=47.5, over=0.8, z_stagger=0.0015),
    # --- 지형 ---
    # 둑마루: 기본 grass 대지 + Y방향 자갈 도로 밴드(하천 평행) + 계단 접속 스퍼
    # v4-A1/A2: 둑마루 y ±10 → ±40 (둔치와 정합), x0 −20 → −45.
    #   기존엔 x<−20 및 |y|>10 에 어떤 프림도 없어 주 보행축(둑길)이 허공으로
    #   절단되고, 사면 측방(x 0..7, |y| 10..40)에 깊이 3.2 노치가 개방돼 있었다.
    levee=dict(x0=-45.0, x1=0.0, y0=-40.0, y1=40.0, z_top=0.0, thick=0.5),
    levee_road=dict(x0=-4.0, x1=-1.0, proud=0.0015, embed=0.05),  # 자갈 도로(폭 3m, Y 전폭)
    levee_spur=dict(x0=-1.0, x1=0.0, y0=-1.2, y1=1.2),            # 계단 상단 접속 스퍼(gravel)

    # === [W2-D ground_kit] P13 levee_paved, natural-forced (spec §5.7) =====
    # The supervisor ruling of 07-29 put scene03's cycle track on hold ("03 은
    # 자연 유지, 자전거도로는 scene17 제방만 유효"), so the whole paved half of
    # profile P13 is inapplicable here. What is left is the levee crest as
    # built: grass + a 3 m gravel road band + the stair-head spur.
    #   -> `natural=True` is forced in `overrides`, which makes ground_kit
    #      itself raise on any urban infra (manhole / gully / gutter / marking),
    #      i.e. the §5.7 "도시 인프라 0건" rule is enforced by code, not by
    #      discipline. Interlock joints are switched off as well: there is no
    #      interlock paving on this crest, and the ledger's 200 mm unit cell
    #      would draw a grid onto grass and gravel.
    # z: elements sit on the **gravel band top** (levee_road proud, +1.5 mm).
    #   Using the grass top (0.0) instead would bury every element on the road,
    #   which is exactly the burial class the pilots found (spec §1.1).
    # patches = 답압 노출토 (spec §5.7 "8~12"), bound to the dirt material -
    # trampled bare soil at the gravel/grass margins, not asphalt repairs.
    # wear lane runs **along the river (+-Y)**, i.e. along the walking route on
    #   the crest, offset to x=-3.50 so it falls inside the d5 near window
    #   (x -4.44..-3.00). Length is capped at |y| <= 10 because the band is
    #   straight while the road follows the meander: |dx(10)| = 0.95 m and the
    #   road is 3 m wide, so the straight band is still inside the road at the
    #   ends; at |y| = 20 it would not be (|dx| = 3.52).
    # NO silt band. Spec §5.7 lists one, but the crest top (z=0) is 3.35 m
    #   above the water line (riprap bottom -3.35): silt deposition belongs to
    #   the 둔치 at z=-3.2, which is outside every h0.3 near window.
    gkit=dict(x0=-12.0, half_y=3.0, wear_x=-3.50, wear_y=10.0,
              break_y=3.0,
              patch=[(-1.10, 0.15), (-3.35, 0.55), (-2.15, -1.35),
                     (-5.10, 1.85), (-8.60, -0.80), (-9.35, 1.50),
                     (-4.30, -2.15), (-11.00, 0.40)]),
    slope=dict(x0=0.0, z0=0.0, run=7.0, drop=3.2, thick=0.4,   # 20단 정합: run 7.0
               y0=-40.0, y1=40.0),
    # 계단+측벽 테두리 회랑(사면 절개폭). [v5.1] band_gap = 사행 사면 밴드의
    #   내측 한계 — 회전 편차(±0.044)에도 트림(0.75~0.95) 밑으로 물리도록
    #   0.95 → 0.88 로 0.07 물려 넣는다. 계단 측면 0.75 는 침범 불가.
    corridor=dict(y0=-0.95, y1=0.95, band_gap=0.88),
    # --- 계단 : 20단 (drop 3.2 = 사면·둔치 정합, run 7.0) ---
    stairs=dict(x0=0.0, riser=0.16, tread=0.35, nsteps=20,     # run 7.0, drop 3.2
                y0=-0.75, y1=0.75, base_z=-3.6, z_top=0.0),
    # v4-A4: margin 0.3 → 0.0, z0 0.05 → 0.02. 종전엔 경사보가 x≈−0.13 까지
    #   앞으로 튀어나와 둑마루 상면 위 약 0.10 m 콘크리트 토막 2개가 생겼다.
    trim=dict(width=0.2, drop=3.2, z0=0.02, thick=0.4, margin=0.0),
    # --- 둔치(beach) : x 7.0..18.0, z=-3.2, dirt|grass 두 띠(경계 x=12) ---
    #     원경 하늘 구멍 제거 위해 y폭 ±40 확폭 (near 지형은 ±10 유지)
    beach=dict(x0=7.0, x1=18.0, y0=-40.0, y1=40.0, z_top=-3.2,
               thick=0.4, split_x=12.0),
    # v4-A3: 하부 트레일을 하천 평행(Y축)으로 재배치. 종전 x 7..18 × y ±1.2 는
    #   계단을 내려온 뒤 유일한 길이 물로 직진 종료하는 보행 논리 오류였다.
    beach_path=dict(x0=9.4, x1=12.4, y0=-40.0, y1=40.0, z_top=-3.18,
                    thick=0.12),
    # v4-D4 자전거도로 노면 표시 (한강 둔치 즉독)
    path_lines=dict(edge_x=(9.6, 12.2), w=0.12, z_top=-3.175, thick=0.02,
                    mid_x=10.9, dash_len=2.0, dash_step=8.0, dash_y0=-32.0,
                    dash_n=9),
    # --- 사석 띠(riprap) : 수면-둔치 사이 낮은 경사보 ---
    riprap=dict(x0=17.0, z0=-3.2, run=1.2, drop=0.15, thick=0.3,
                y0=-40.0, y1=40.0),
    # --- 수면 & 건너편 둔치 (유효 수변이 s≈18 에서 노출) ---
    # v4-B2: 균질 시안 판(수영장 오독) 완화 — 3밴드 roughness 변주
    # [v5.1] 수로폭 축소(far_bank s0 40→34, 수면 s1 40→36 — 34~36 은 건너편
    #   둔치 밑으로 물려 넣는 겹침분). 유효 수면 s 18.2..34 = 15.8 m.
    #   사행 진폭 14.8 / 수로폭 15.8 = 0.94 → 요구 "1~2배" 하한 충족.
    water=dict(x0=16.5, y0=-40.0, x1=36.0, y1=40.0, z=-3.35,
               bands=((16.5, 23.0, 0.06), (23.0, 29.0, 0.10),
                      (29.0, 36.0, 0.15))),
    far_bank=dict(x0=34.0, x1=70.0, y0=-40.0, y1=40.0, z_top=-3.2, thick=0.4),
    # v4-B3/D11: far_hedge 3장(grass 텍스처 60 m 띠)이 지평에 규칙 해칭 줄무늬를
    #   만들어 인쇄 배경막처럼 읽혔다 → 수목 라인 7본으로 교체.
    # [v5.1] 수변이 s34 로 당겨졌으므로 수목 라인도 s38 로. 등간격 10 m 나열은
    #   전역 규약 3(격자 금지) 위반이라 간격·오프셋을 불규칙화.
    far_trees=[dict(cx=38.0 + dxo, cy=cy) for dxo, cy in
               ((0.0, -31.0), (1.8, -22.5), (-1.2, -13.0), (2.4, -3.0),
                (-0.6, 7.5), (1.5, 16.0), (-1.8, 27.5), (0.9, 35.0))],

    # --- 소품 ---
    # 스퍼 양옆(차량 진입 방지) — [v5.1 전역 규약 2] 볼라드는 기능 시설물.
    #   계단 진입 전면이라는 배치 근거는 유지하되 높이 0.75 → 0.90(규정
    #   0.8~1.0m), 상단 백색 반사띠 추가. 장식 열주가 아니라 2본 게이트.
    # [v6 판정 ㉢] "levee_walk 근경에서 2본이 화면 높이 1/3 을 점유 — 계단 진입
    #   전면 게이트가 주 컷의 주인공". 후퇴 방향을 −X 로 잡으면 카메라(−6)에
    #   가까워져 오히려 커지므로, **시선축 밖(횡방향)으로 벌리고 도로-스퍼
    #   경계선(s −1.0)까지만 후퇴**시킨다. 스퍼 폭(y ±1.2) 모서리 바깥 1.0 m.
    #   levee_walk 기준 방위각 |az| 14.8° → 25.3° 로 이동(프레임 가장자리).
    bollards=[dict(cx=-1.2, cy=2.2), dict(cx=-1.2, cy=-2.2)],
    bollard=dict(h=0.90, r=0.075, band_z=0.74, band_h=0.10),
    # v4-D7: 벤치 1 → 4 (둑마루 2 + 둔치 2). (cx, cy, base_z, yaw)
    # [v5.1 전역 규약 3] 구 배치는 y=±6 대칭쌍 2조(격자)였다 → 앵커(파고라
    #   내부·나무 옆·산책로 가장자리) 기준 비대칭 배치 + yaw 비정수각.
    benches=[(-6.5, 4.4, 0.0, 5.0),        # 파고라(s −8..−5, y 3..6) 안
             (-6.4, -7.6, 0.0, 172.0),     # 둑마루 나무(−8,−7) 옆 1.75 m
             (12.9, -4.6, -3.2, 93.0),     # 둔치 산책로 가장자리(s12.4)에서 0.5
             (15.2, 6.4, -3.2, 187.0)],    # 둔치 나무(16,5) 옆 1.60 m
    # v4-B1 [치명급 룩]: 사면 관목이 축정렬 박스라 구배 0.457 × 반폭 0.6 →
    #   상류 0.37 매입 / 하류 0.17 공중부양. build_slope(경사 슬래브)로 전환하고
    #   군락당 3장 중첩(크기·높이 변주)으로 블록감도 해소.
    # [v5.1 재수정] 그 경사 슬래브 3장 중첩이 scene04 v5 판정에서 '잔디를 뚫고
    #   나온 각진 판떼기'로 확인된 형상이다(같은 구현). 여기도 **눌린 타원체
    #   3개 중첩**으로 교체 — 축정렬 회전체라 절단면이 없고, 구배는 배치 높이
    #   (slope_z)로만 반영. 접지 조건 rz·embed ≥ rx·구배(0.457):
    #     0.34×0.55=0.187 ≥ 0.40×0.457=0.183 ✓ (rx 를 0.40 이하로 제한)
    hedges=[dict(cx=1.5, cy=-4.0), dict(cx=3.0, cy=6.0),
            dict(cx=2.2, cy=8.0), dict(cx=4.0, cy=-7.0),
            dict(cx=1.8, cy=-11.5), dict(cx=3.4, cy=13.0)],
    hedge=dict(embed=0.55,
               blobs=((0.00, 0.00, 0.40, 0.62, 0.34),
                      (0.30, 0.52, 0.30, 0.46, 0.25),
                      (-0.26, -0.44, 0.33, 0.40, 0.29))),  # (dx,dy,rx,ry,rz)
    # 둔치 나무 2그루 (수관 상단 z≈-0.15, 둑마루 눈높이 1.5 아래 — 계열③ 앵커)
    trees=[dict(cx=10.0, cy=-4.0), dict(cx=16.0, cy=5.0)],
    # v4-D10: 나무 2 → 8 (둑마루 3 + 둔치 3 추가)
    trees_extra=[dict(cx=-8.0, cy=-7.0, gz=0.0), dict(cx=-8.0, cy=7.0, gz=0.0),
                 dict(cx=-14.0, cy=0.0, gz=0.0),
                 dict(cx=9.0, cy=-10.0, gz=-3.2), dict(cx=14.5, cy=-24.0, gz=-3.2),
                 dict(cx=9.0, cy=12.0, gz=-3.2)],

    # === v4-D 맥락 드레싱 (하천 제방으로 읽히게) ===
    # D1 [최우선] 원경 교량 — 한 컷에 '하천' 확정. 하천축이 Y이므로 교량은 X로 횡단.
    bridge=dict(x0=12.0, x1=46.0, y0=-22.5, y1=-13.5, deck_top=-0.2,
                deck_thick=0.8, parapet_h=0.9, parapet_w=0.3,
                pier_r=1.2, pier_x=(14.0, 22.0, 30.0, 38.0, 45.0),
                pier_z0=-3.7),
    # D2 건너편 도시 실루엣 (지평 폐쇄 + 하천폭 스케일 앵커). base_z=far_bank 상면
    # [v5.1] 수변 축소에 맞춰 s 55→48 로 당기고(둔치 폭 14 m 유지), 세 동을
    #   각자 rot_group 에 넣어 곡류 접선 + 배치 지터(yaw ±4°)를 준다.
    city=dict(
        A=dict(x0=48.0, x1=55.0, y0=-30.0, y1=-14.0, h=22.0, floors=7,
               axis="x", facade_x=48.0, face_dir=-1.0, base_z=-3.2, jyaw=3.5),
        B=dict(x0=48.0, x1=57.0, y0=-6.0, y1=8.0, h=16.0, floors=5,
               axis="x", facade_x=48.0, face_dir=-1.0, base_z=-3.2, jyaw=-4.0),
        C=dict(x0=48.0, x1=53.0, y0=16.0, y1=30.0, h=26.0, floors=8,
               axis="x", facade_x=48.0, face_dir=-1.0, base_z=-3.2, jyaw=2.5),
    ),
    # D5 갈대 밴드 (수변 전이) — [v5.1] 구 5분할 축정렬 박스 → 사행 밴드
    #   (수변선 곡률을 그대로 따라가야 '강가 갈대'로 읽힌다). segs 키 폐기.
    reeds=dict(x0=16.0, x1=17.0, h=0.9, base_z=-3.2),
    # D6 둑마루 자전거도로 중앙선 + 거리표지
    levee_line=dict(x=-2.5, w=0.12, y0=-40.0, y1=40.0, z_top=0.002,
                    thick=0.02),
    # [v5.1] 3본 6 m 등간격은 실제 하천 거리표지(수백 m 간격) 관행과 무관한
    #   장식 열이었다 → 2본으로 축소.
    # [v6 판정 ㉣ / v5.2 §6] 남은 2본도 "둔치 잔디 한복판에 홀로 선 이발소 기둥"
    #   으로 판정 → **전량 삭제**(기능 근거 약함 · 비움이 기본값). 빌더 코드
    #   경로는 유지(리스트를 채우면 그대로 복원).
    markers=[],                                        # (s, y, yaw_jit)
    marker=dict(post_r=0.04, post_h=1.2, plate=(0.06, 0.35, 0.25),
                plate_z=1.02),
    # D7 파고라 1
    pergola=dict(x0=-8.0, x1=-5.0, y0=3.0, y1=6.0, z_roof=2.4, post_r=0.09,
                 roof_t=0.14, jyaw=-3.0),
    # D8 둔치 운동장 라인 (둔치 정체성)
    # (교량 y −22.5..−13.5 · 벤치 y ±6 과 겹치지 않도록 +Y 원경에 배치)
    field=dict(x0=12.8, x1=15.8, y0=20.0, y1=32.0, w=0.10, z_top=-3.19,
               thick=0.02),
    # D9 수위표 (하천 시설 확정)
    gauge=dict(cx=17.4, cy=-3.0, r=0.09, z0=-3.35, z1=0.2,
               band_z=(-2.6, -1.6, -0.6), band_h=0.25),

    # --- 재질: texture_scale용 물리 크기[m/타일] + 상수 ---
    material=dict(
        scale=dict(gravel=0.6, grass=1.4, concrete_floor=0.8,   # grass 4.0: 이끼 뭉침 완화
                   dirt_park=1.0, rock_wall=1.5, wood_dark=1.0),
        grass_tint=(0.55, 0.68, 0.42),        # 타일 반복 완화 + 초록 틴트 (유지)
        hedge_tint=(0.48, 0.60, 0.34),        # v4-B1 사면 관목
        reed_tint=(0.78, 0.72, 0.40),         # v4-D5 갈대 (마른 억새 톤)
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,        # scene01 최종값 (나무 줄기·지지대)
        # v4-B4: (0.33,·,0.36)+metallic 0.4 는 정오 직사광에서 흰 PVC 파이프로
        #   날아갔다 → 어두운 아연도금 톤 + 금속성 축소.
        bollard_color=(0.16, 0.16, 0.17), bollard_metallic=0.15,
        bollard_rough=0.6,
        # v4-B(공통): 수관 알베도 상향 (검은 얼룩 → 잎 실루엣)
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030),
        canopy_rough=1.0,
        water_color=(0.05, 0.10, 0.11), water_rough=0.08,      # 거울 완화 (0.03→0.08)
        # [v5 판정 반영] v4-D1 교량 알베도 0.055 는 상판·파라펫·교각 전부를
        #   정보량 0의 검은 실루엣으로 만들었다(levee_walk 우측 검은 덩어리 +
        #   수면 검은 반사, across_river 는 '허공에 뜬 검은 판'). 감사 v4가
        #   지적한 '검은 상자' 결함이 더 큰 스케일로 재발한 사례.
        #   → 상판·교각을 실제 노출 콘크리트 톤(0.28)으로 상향,
        #     파라펫은 판정 권고대로 0.22 로 분리해 상판과 면 구분을 남긴다.
        concrete_dark=(0.28, 0.28, 0.275), concrete_dark_rough=0.8,   # v4-D1 교량 상판·교각
        concrete_parapet=(0.22, 0.22, 0.215),                         # 교량 파라펫(난간벽)
        city_color=(0.16, 0.16, 0.17), city_glass=(0.05, 0.07, 0.10),
        city_parapet=(0.22, 0.22, 0.21),      # v4-D2 원경 도시
        line_color=(0.55, 0.55, 0.52),        # v4-D4/D8 노면·운동장 백선
        gauge_band=(0.30, 0.045, 0.035),      # v4-D9 수위표 적색 밴드
        # [v5.1 전역 규약 2] 볼라드 상단 반사띠 (순백 금지 — 0.72 유광 회백)
        bollard_band=(0.72, 0.72, 0.70), bollard_band_rough=0.35,
        # [v5.1 전역 규약 4] 인스턴스 틴트 지터 진폭
        tint_jitter=0.05,
    ),

    # --- 조명: scene01 noon 검증 상수 그대로 ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    SUN_AZ_OFFSET=171.5,               # scene01 동일 기본 (수면 하늘 반사 확인용)

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


# 파라미터 오버라이드 (A/B 렌더 비교용 — scene01 패턴)
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
# [C] 경로 (텍스처·mdl·hdri 실체는 scene_common 이 관리)
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene03")

# 이 씬이 사용하는 텍스처 역할 (tactile 미사용)
ASSET_ROLES = ["gravel", "grass", "concrete_floor", "dirt_park",
               "rock_wall", "wood_dark", "hdri", "mdl"]


# ===========================================================================
# [C2] [v5.1] 사행 중심선 — 하천 평행 요소의 좌표 변환 기저
#   월드 X = s + river_dx(y),  밴드 세그 방위 = river_yaw(y)
#   dx(0)=0 · dx'(0)=0 이므로 계단 회랑(y ±0.95)에서는 항등 변환 → 위험 기하
#   (계단·트림·스퍼·회랑) 트랜스폼이 v5 와 비트 단위로 동일하다.
# ===========================================================================
def river_dx(y):
    """중심선의 X 오프셋 [m]."""
    mn = PARAMS["meander"]
    k1 = 2.0 * math.pi / mn["L1"]
    return (mn["A1"] * (math.cos(k1 * y) - 1.0)
            + mn["A3"] * (y / mn["y_ref"]) ** 3)


def river_ddx(y):
    """dx/dy — 중심선 접선 기울기."""
    mn = PARAMS["meander"]
    k1 = 2.0 * math.pi / mn["L1"]
    return (-mn["A1"] * k1 * math.sin(k1 * y)
            + 3.0 * mn["A3"] * y * y / mn["y_ref"] ** 3)


def river_yaw(y):
    """세그 방위각 [deg]. rotZ 로 걸면 세그 로컬 +Y 가 중심선 접선과 일치."""
    return -math.degrees(math.atan(river_ddx(y)))


def river_segments(y_gap=None):
    """밴드 세그 분할 → [(yc_ref, y_lo, y_hi, clip_lo, clip_hi), ...].

    ★ 전 밴드가 **동일한 y 분할(동일 현 프레임)** 을 쓴다. 밴드마다 분할이
      다르면 같은 y 에서 이웃 밴드의 현(chord)이 서로 다른 각도로 곡선을
      근사해 최대 수 cm 의 실틈이 생긴다(검증 스크립트로 2 cm 실측).
      회랑(y_gap)은 분할을 바꾸지 말고 **해당 세그를 길이방향으로 잘라내기만**
      한다 — 회전축(yc_ref)과 폭 방향 에지선이 그대로라 이웃 밴드와의 정합이
      유지된다. 잘린 끝에는 종방향 겹침(over)을 붙이지 않는다(회랑 침범 방지).
      seg_dy=5.0 · y ±47.5 → 세그 19개(그 중 y=0 세그가 회랑에서 2조각).
    """
    mn = PARAMS["meander"]
    y0, y1, dy = mn["y0"], mn["y1"], mn["seg_dy"]
    n = max(1, int(round((y1 - y0) / dy)))
    h = (y1 - y0) / n
    out = []
    for i in range(n):
        a = y0 + i * h
        b = a + h
        yc = (a + b) / 2.0
        if y_gap is None:
            out.append((yc, a, b, False, False))
            continue
        glo, ghi = y_gap
        if b <= glo or a >= ghi:
            out.append((yc, a, b, False, False))
        elif a < glo and b > ghi:
            out.append((yc, a, glo, False, True))
            out.append((yc, ghi, b, True, False))
        elif a < glo:
            out.append((yc, a, glo, False, True))
        elif b > ghi:
            out.append((yc, ghi, b, True, False))
    return out


def tint_jitter(color, seed, amp=None):
    """[v5.1 전역 규약 4] 인스턴스별 ±amp 색 지터(시드 결정적)."""
    if amp is None:
        amp = PARAMS["material"]["tint_jitter"]
    rnd = random.Random(1000003 * (int(seed) + 13))
    return tuple(round(max(0.005, c * (1.0 + rnd.uniform(-amp, amp))), 5)
                 for c in color)


# ===========================================================================
# [D] 카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷 (§C)
#     이 씬은 중앙 난간 없음 → 프리셋 축이 계단 중심 y=0 통과.
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)                 # h{0.3,0.9,1.8}×d{2,5,10}, +X pitch -10°
    # levee_walk: 둑마루에서 진행방향 — 계단이 사면에 접혀 소실, 물면만 걸림
    views["levee_walk"] = dict(eye=[-6.0, 0.0, 1.2], tgt=[4.0, 0.0, 0.3])
    # stair_down: 계단 위(어깨)에서 아래로 부감
    views["stair_down"] = dict(eye=[-0.6, 0.0, 1.6], tgt=[4.5, 0.0, -2.0])
    # beach_lookup: 둔치에서 역방향(-X) — 사면·계단 올려봄
    views["beach_lookup"] = dict(eye=[9.0, 2.0, -2.6], tgt=[0.5, 0.0, -0.8])
    # across_river: 수면 너머 건너편 둔치 조망
    views["across_river"] = dict(eye=[17.0, 0.0, -2.5], tgt=[42.0, 0.0, -2.9])

    # ===================================================================
    # [v6 판정 ㉠] **하천 종방향/사선 미장센 3컷 신설** — 기하 무수정, 카메라만.
    #   판정 사유: 구 4컷이 전부 하천에 직교(시선 azimuth ≈ 0°)해 화각에 들어오는
    #   하천 길이가 15~40 m 뿐 → 파장 110 m 사행이 그 구간에서 사실상 직선.
    #   아래 3컷은 시선을 **하천 축(+Y)** 으로 돌려 y 45~90 m 구간을 한 프레임에
    #   담는다. 그 구간의 중심선 측방 이동 = 14.8 m (dx(0)=0 → dx(±47.5)).
    #   좌표는 전부 river_dx() 로 사행 좌표계에서 계산 — 진폭을 바꿔도 자동 추종.
    #   (차폐 검산은 아래 river_view_selfcheck() — NEGOBS_SELFCHECK=1)
    # ===================================================================
    def W(s, y):                               # 횡단면 s → 월드 X
        return river_dx(y) + s

    # ① river_along [미장센·비판정] — 둑마루 자갈도로 위 **보행 시선**(h1.65)에서
    #    상류 종방향. 교량(y −22.5..−13.5) 북쪽에서 출발해 시야를 막지 않는다.
    #    눈높이가 수면보다 5 m 위일 뿐이라 사행의 화면 휨은 0.4 % 로 작다
    #    (아래 검산) — 판정용이 아니라 "둑길을 걷는 시점"의 현실성 컷이다.
    views["river_along"] = dict(eye=[W(-2.5, -10.0), -10.0, 1.65],
                                tgt=[W(14.0, 35.0), 35.0, -3.30])
    # ② meander_air [판정] — 부각 15.4° 부감. y −44..+20 의 굴곡 + 교량 횡단이
    #    한 프레임에. 수변선의 화면 휨 14.1 %(프레임 반폭 대비).
    views["meander_air"] = dict(eye=[W(10.2, -44.0), -44.0, 16.0],
                                tgt=[W(20.0, 25.0), 25.0, -3.35])
    # ③ bank_oblique [판정] — **건너편 둔치 상공**에서 상류를 보는 사선(부각 12.7°).
    #    ②와 반대편·다른 각이라 사행이 카메라 배치 우연이 아님을 교차 확인한다.
    #    수변선 휨 14.2 % · 차폐 21 %(전부 교량 상판, 연속 구간).
    views["bank_oblique"] = dict(eye=[W(40.0, -26.0), -26.0, 8.0],
                                 tgt=[W(20.0, 20.0), 20.0, -3.20])
    return views


def _cam_basis(eye, tgt):
    """월드 → 카메라 정규화 이미지좌표 변환기. up=+Z, 이미지 u(우)·v(상).
    반환: project(P) → (u, v, depth). u,v 는 tan 단위(= 화각 tan)."""
    ex, ey, ez = eye
    fx, fy, fz = tgt[0] - ex, tgt[1] - ey, tgt[2] - ez
    fl = math.sqrt(fx * fx + fy * fy + fz * fz)
    f = (fx / fl, fy / fl, fz / fl)
    # right = f × Z  (정규화). 시선이 수직에 가깝지 않다고 가정(부각 ≤ 60°).
    rx, ry, rz = f[1] * 1.0 - 0.0, 0.0 - f[0] * 1.0, 0.0
    rl = math.hypot(rx, ry)
    r = (rx / rl, ry / rl, 0.0)
    u_ = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2],
          r[0] * f[1] - r[1] * f[0])            # up = r × f

    def project(p):
        dx_, dy_, dz_ = p[0] - ex, p[1] - ey, p[2] - ez
        d = dx_ * f[0] + dy_ * f[1] + dz_ * f[2]
        if d <= 1e-6:
            return None
        return ((dx_ * r[0] + dy_ * r[1] + dz_ * r[2]) / d,
                (dx_ * u_[0] + dy_ * u_[1] + dz_ * u_[2]) / d, d)
    return project


def _seg_hits_box(eye, p, box):
    """선분 eye→p 가 AABB box=(x0,x1,y0,y1,z0,z1) 를 지나면 True (slab법).
    끝점 근방(t>0.995)은 대상 자신이므로 제외한다."""
    x0, x1, y0, y1, z0, z1 = box
    t0, t1 = 0.0, 0.995
    for a, b, lo, hi in ((eye[0], p[0], x0, x1), (eye[1], p[1], y0, y1),
                         (eye[2], p[2], z0, z1)):
        d = b - a
        if abs(d) < 1e-9:
            if a < lo or a > hi:
                return False
            continue
        ta, tb = (lo - a) / d, (hi - a) / d
        if ta > tb:
            ta, tb = tb, ta
        t0, t1 = max(t0, ta), min(t1, tb)
        if t0 > t1:
            return False
    return True


def river_view_selfcheck(verbose=True):
    """[v6 판정 ㉠] 신설 종방향 컷의 **사행 판독성 + 차폐** 좌표 검산.

    핵심 성질: **3차원의 직선은 어떤 투영에서도 직선으로 맺힌다.** 따라서
    수변선(s=18.2 유효 수변)을 화면에 투영했을 때 양 끝점을 잇는 현(chord)에서
    벗어나는 최대 편차 = "직선 수로였다면 0" 인 순수 사행 신호다. 이 값을
    **프레임 반폭(tan30° = 0.577) 대비 %** 로 환산해 판독성을 정량화한다.
    (구 4컷은 하천 직교라 프레임 안 수변선 자체가 15~40 m 뿐 → 편차 ≈ 0.)

    차폐: 카메라와 각 수변 표본을 잇는 선분이 근경 요소(교량+파라펫·둔치/둑마루
    수목·파고라·볼라드·수위표) AABB 를 관통하는지 slab 법으로 검사.
    반환: (ok, 진단 dict). 순수 수학 — Isaac 부팅 불필요.
    """
    views = build_views()
    s_edge = 18.2                              # 유효 수변(사석 하단)
    TU, TV = math.tan(math.radians(30.0)), math.tan(math.radians(18.0))

    # --- 근경 차폐체 AABB (회전 그룹은 외접 박스로 보수적 근사) ---
    bg = PARAMS["bridge"]
    bdx = river_dx((bg["y0"] + bg["y1"]) / 2.0)
    byw = (bg["x1"] - bg["x0"]) / 2.0 * abs(math.sin(math.radians(
        river_yaw((bg["y0"] + bg["y1"]) / 2.0))))
    boxes = [(bdx + bg["x0"], bdx + bg["x1"], bg["y0"] - byw, bg["y1"] + byw,
              bg["pier_z0"], bg["deck_top"] + bg["parapet_h"])]
    # 수목: 수관(구형 blob 군) + 줄기를 분리 — 통짜 박스로 잡으면 수관 아래
    #   빈 공간까지 차폐로 오판한다(build_tree: th = trunk_h·U(0.85,1.25)).
    trees = ([(t["cx"], t["cy"], PARAMS["beach"]["z_top"], 2.2)
              for t in PARAMS["trees"]]
             + [(t["cx"], t["cy"], t["gz"], 2.2)
                for t in PARAMS["trees_extra"]]
             + [(t["cx"], t["cy"], PARAMS["far_bank"]["z_top"], 3.0)
                for t in PARAMS["far_trees"]])
    for cx0, cy0, gz, th in trees:
        cx = river_dx(cy0) + cx0
        boxes.append((cx - 1.0, cx + 1.0, cy0 - 1.0, cy0 + 1.0,
                      gz + th * 0.85, gz + th * 1.25 + 1.1))     # 수관
        boxes.append((cx - 0.12, cx + 0.12, cy0 - 0.12, cy0 + 0.12,
                      gz, gz + th * 0.85))                       # 줄기
    pg = PARAMS["pergola"]
    pcy = (pg["y0"] + pg["y1"]) / 2.0
    pdx = river_dx(pcy)
    boxes.append((pdx + pg["x0"], pdx + pg["x1"], pg["y0"], pg["y1"], 0.0,
                  pg["z_roof"] + pg["roof_t"]))
    for b in PARAMS["bollards"]:
        bx = river_dx(b["cy"]) + b["cx"]
        boxes.append((bx - 0.09, bx + 0.09, b["cy"] - 0.09, b["cy"] + 0.09,
                      0.0, PARAMS["bollard"]["h"]))
    gg = PARAMS["gauge"]
    gx = river_dx(gg["cy"]) + gg["cx"]
    boxes.append((gx - 0.1, gx + 0.1, gg["cy"] - 0.1, gg["cy"] + 0.1,
                  gg["z0"], gg["z1"]))

    for key, bd in PARAMS["city"].items():
        ccy = (bd["y0"] + bd["y1"]) / 2.0
        cdx = river_dx(ccy)
        boxes.append((cdx + bd["x0"], cdx + bd["x1"], bd["y0"], bd["y1"],
                      bd["base_z"], bd["base_z"] + bd["h"]))

    # (컷 이름, 판정컷 여부) — 미장센 전용 컷에는 휨 하한을 적용하지 않는다.
    diag, ok = {}, True
    for name, judge in (("river_along", False), ("meander_air", True),
                        ("bank_oblique", True)):
        v = views[name]
        eye, tgt = v["eye"], v["tgt"]
        proj = _cam_basis(eye, tgt)
        pts = []
        for k in range(191):
            y = -47.5 + 95.0 * k / 190.0
            p = (river_dx(y) + s_edge, y, PARAMS["water"]["z"])
            q = proj(p)
            if q is None or abs(q[0]) > TU or abs(q[1]) > TV:
                continue
            pts.append((y, q[0], q[1], p))
        if len(pts) < 3:
            ok = False
            diag[name] = dict(n=0)
            continue
        # 화면 현(chord) 대비 최대 편차 → 프레임 반폭 %
        u0, v0, u1, v1 = pts[0][1], pts[0][2], pts[-1][1], pts[-1][2]
        cl = math.hypot(u1 - u0, v1 - v0)
        dev = 0.0
        for _, u, vv, _p in pts:
            dev = max(dev, abs((u1 - u0) * (vv - v0) - (v1 - v0) * (u - u0))
                      / cl if cl > 1e-9 else 0.0)
        occ = sum(1 for _, _, _, p in pts
                  if any(_seg_hits_box(eye, p, b) for b in boxes))
        span = pts[-1][0] - pts[0][0]
        pit = math.degrees(math.atan2(tgt[2] - eye[2],
                                      math.hypot(tgt[0] - eye[0],
                                                 tgt[1] - eye[1])))
        diag[name] = dict(pitch=round(pit, 1), y_span=round(span, 1),
                          bow_pct=round(100.0 * dev / TU, 2),
                          occluded=occ, n=len(pts), judge=judge)
        if judge and (span < 40.0 or dev / TU < 0.05
                      or occ > len(pts) * 0.35):
            ok = False
    if verbose:
        print("=" * 64)
        print("scene03 [v6] 종방향 컷 — 사행 판독성 + 차폐 검산")
        print("=" * 64)
        for k, d in diag.items():
            print(f"  {k:13s}{'[판정]' if d['judge'] else '[미장센]':7s}"
                  f" pitch{d.get('pitch', 0):+6.1f}°  "
                  f"프레임내 수변 y {d.get('y_span', 0):5.1f} m  "
                  f"직선대비 휨 {d.get('bow_pct', 0):5.2f}% 프레임반폭  "
                  f"차폐 {d.get('occluded', 0)}/{d.get('n', 0)}")
        print("  판정컷 기준: 종방향 ≥40 m · 휨 ≥5 % · 차폐 ≤35 %")
        print("  (3차원 직선은 어떤 투영에서도 직선 → 휨 > 0 자체가 사행 신호)")
        print(f"  → {'OK' if ok else 'FAIL'}")
        print("=" * 64)
    return ok, diag


# ===========================================================================
# [E] 메인 — 부팅 → 조립 → 조명 → 뷰 → 캡처/GUI
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. levee_walk       — h1.2 둑길에서 계단·사면 소실 + 수면·건너편 둔치만 남는가
 2. h0.3·d5~10       — 제방 어깨가 평지로 보이고 낙차 증거가 물면뿐인가
 3. stair_down       — 계단 16단이 명확히 보이는가 (부감)
 4. beach_lookup     — 둔치 나무 수관이 둑마루 눈높이 아래인가 (계열③ 앵커)
 5. across_river     — 수면 하늘 반사 + 건너편 둔치 재출현
 6. cue_railing OFF/ON — 위험 기하(계단·사면) 트랜스폼 동일한가
 7. [v6] meander_air / bank_oblique — 사행이 프레임 안에서 휘어 보이는가
                     (검산: NEGOBS_SELFCHECK=1 python scene03_riverbank.py)
 8. [v6] river_along — 둑길 보행 시점에서 하천 종방향 원근이 자연스러운가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # ── [v6] 좌표 검산만 수행하고 종료 (Isaac 부팅 불필요) ──
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        river_view_selfcheck()
        return

    # ── 0단계: 에셋 존재 검사 (부팅 전) ──
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    # ── 1단계: Isaac Sim 부팅 (SimulationApp 무조건 먼저) ──
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    from pxr import UsdGeom
    UsdGeom.Xform.Define(stage, "/World/Scene03")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene03"

    # -------------------------------------------------------------------
    # setup_materials — scene_common.make_pbr 로 전 재질 생성
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        M = {}
        M["gravel"] = tex("gravel", "/World/Looks/Gravel", sca["gravel"])
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["concrete"] = tex("concrete_floor", "/World/Looks/Concrete",
                            sca["concrete_floor"])
        M["dirt"] = tex("dirt_park", "/World/Looks/Dirt", sca["dirt_park"])
        M["rock"] = tex("rock_wall", "/World/Looks/Rock", sca["rock_wall"])
        M["wood_dark"] = tex("wood_dark", "/World/Looks/WoodDark",
                             sca["wood_dark"])
        # 상수 컬러 재질
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["bollard"] = sc.make_pbr(stage, "/World/Looks/Bollard",
                                   diffuse_color=mp["bollard_color"],
                                   metallic=mp["bollard_metallic"],
                                   roughness_const=mp["bollard_rough"])
        M["water"] = sc.make_pbr(stage, "/World/Looks/Water",
                                 diffuse_color=mp["water_color"],
                                 roughness_const=mp["water_rough"], metallic=0.0)
        # v4-B2: 수면 3밴드 (roughness 변주로 균질 시안 판 완화)
        for bi, (_, _, rgh) in enumerate(PARAMS["water"]["bands"]):
            M[f"water_{bi}"] = sc.make_pbr(
                stage, f"/World/Looks/Water_{bi}",
                diffuse_color=mp["water_color"],
                roughness_const=rgh, metallic=0.0)
        # [v5.1 전역 규약 2] 볼라드 상단 반사띠
        M["bollard_band"] = sc.make_pbr(
            stage, "/World/Looks/BollardBand",
            diffuse_color=mp["bollard_band"], metallic=0.2,
            roughness_const=mp["bollard_band_rough"])
        # v4 드레싱 전용 재질
        # [v5.1] 관목 3종 ±5 % 틴트 지터 (군락 내 개체차 — 재질 신설 대신
        #   기존 hedge_tint 를 diffuse_tint 로만 흔든다)
        M["hedge_v"] = [tex("grass", f"/World/Looks/Hedge{i}", 1.2,
                            tint=tint_jitter(mp["hedge_tint"], 30 + i))
                        for i in range(3)]
        M["hedge"] = M["hedge_v"][0]
        M["reed"] = tex("grass", "/World/Looks/Reed", 0.8,
                        tint=mp["reed_tint"])
        M["concrete_dark"] = sc.make_pbr(
            stage, "/World/Looks/ConcreteDark",
            diffuse_color=mp["concrete_dark"],
            roughness_const=mp["concrete_dark_rough"])
        # [v5 판정 반영] 파라펫 전용 톤 (상판 0.28 / 파라펫 0.22 대비)
        M["concrete_parapet"] = sc.make_pbr(
            stage, "/World/Looks/ConcreteParapet",
            diffuse_color=mp["concrete_parapet"],
            roughness_const=mp["concrete_dark_rough"])
        M["city"] = sc.make_pbr(stage, "/World/Looks/City",
                                diffuse_color=mp["city_color"],
                                roughness_const=0.8)
        M["city_glass"] = sc.make_pbr(stage, "/World/Looks/CityGlass",
                                      diffuse_color=mp["city_glass"],
                                      roughness_const=0.15)
        M["city_parapet"] = sc.make_pbr(stage, "/World/Looks/CityParapet",
                                        diffuse_color=mp["city_parapet"],
                                        roughness_const=0.7)
        M["line"] = sc.make_pbr(stage, "/World/Looks/Line",
                                diffuse_color=mp["line_color"],
                                roughness_const=0.75)
        M["gauge_band"] = sc.make_pbr(stage, "/World/Looks/GaugeBand",
                                      diffuse_color=mp["gauge_band"],
                                      roughness_const=0.6)
        # [v5.1] 수관 4종(기저 2색 × ±5 % 지터 2) — 나무마다 다른 쌍을 물린다.
        M["canopy"] = []
        for i, base in enumerate((mp["canopy_a"], mp["canopy_b"])):
            for j in range(2):
                M["canopy"].append(sc.make_pbr(
                    stage, f"/World/Looks/Canopy{i}{j}",
                    diffuse_color=tint_jitter(base, 10 * i + j),
                    roughness_const=mp["canopy_rough"], specular_level=0.0))
        M["canopy_a"], M["canopy_b"] = M["canopy"][0], M["canopy"][2]
        return M

    # -------------------------------------------------------------------
    # v4-B5: 성목·원경 나무에 신식재 지지대는 비현실 → 지지대를 사실상 제거.
    #   scene_common.build_tree 는 지지대 3본을 무조건 만들므로 치수를 0에
    #   근접시켜 무력화한다. (제안: build_tree 에 stakes=False 인자 추가 — 픽스로그)
    # -------------------------------------------------------------------
    def tree_no_stake(M, prefix, cx, cy, gz, trunk_h=2.2, slot=0):
        """[v5.1] 나무별 수관 재질 쌍 교체(수형·크기·기울기 변형은
        scene_common.build_tree v2 가 좌표 시드로 이미 수행)."""
        ca, cb = ((0, 2), (1, 3), (2, 1), (3, 0))[int(slot) % 4]
        sc.build_tree(stage, prefix, cx, cy, gz, M["wood"], M["canopy"][ca],
                      M["canopy"][cb], trunk_h=trunk_h,
                      stake_r=0.004, stake_h=0.02, stake_off=0.2)

    # -------------------------------------------------------------------
    # [v5.1] 사행 밴드 조립기 — 하천 평행 요소의 유일한 진입점
    # -------------------------------------------------------------------
    def river_band(prefix, s0, s1, z_top, thick, mtl, drop=0.0, y_gap=None,
                   max_w=4.0, z_bias=0.0, collider=True, mtl_fn=None):
        """횡단면 구간 [s0,s1] 을 사행 폴리라인 세그로 깐다.

        · 서브밴드 : 폭 max_w 이하로 분할. 인접 밴드 간 겹침 lip 은
          (폭합/2)·(1/cos yaw − cos yaw) 이므로 폭을 좁게 잡을수록 작아진다.
          높이/재질이 다른 경계(둑마루↔사면, 수면↔건너편 둔치)에서 max_w 를
          작게, 균질 배경면(둑마루 내부·건너편 둔치)에서 크게 준다.
        · 세그    : river_segments() 분할(전 밴드 공통). 각 세그는
          build_rot_group(피벗=(세그 상면 중심 x, yc_ref), yaw) 안의 축정렬
          build_slope 박스.
          - 로컬 run = 폭/cos(yaw)  → 상면의 월드 X 투영 = 폭 (밴드 간 정합)
          - 로컬 y 범위 = yc + (y_lo−yc)/cos, yc + (y_hi−yc)/cos (호길이 보정)
            + 잘리지 않은 끝마다 over/2 겹침
        · z 스태거: 코플래너 겹침의 Z파이팅을 막는 1.5 mm 계단(서브밴드·세그
          인덱스 홀짝). 재질 경계가 1.5 mm 어긋나는 것은 원경에서 불가시.
        mtl_fn(j) 지정 시 서브밴드별 재질(수면 3밴드 roughness 변주 등).
        반환: 생성 세그 수."""
        mn = PARAMS["meander"]
        over, stag = mn["over"], mn["z_stagger"]
        width = s1 - s0
        nsub = max(1, int(math.ceil(abs(width) / max_w)))
        segs = river_segments(y_gap)
        n = 0
        for j in range(nsub):
            a = s0 + width * j / nsub
            b = s0 + width * (j + 1) / nsub
            zt_j = z_top - drop * (a - s0) / width if width else z_top
            drop_j = drop / nsub
            for i, (yc, ylo, yhi, clip_lo, clip_hi) in enumerate(segs):
                yaw = river_yaw(yc)
                cw = math.cos(math.radians(yaw))
                run = (b - a) / cw
                sx = river_dx(yc) + (a + b) / 2.0
                zt = zt_j + z_bias - stag * ((i + j) % 2)
                y_lo = yc + (ylo - yc) / cw - (0.0 if clip_lo else over / 2.0)
                y_hi = yc + (yhi - yc) / cw + (0.0 if clip_hi else over / 2.0)
                grp = sc.build_rot_group(stage, f"{prefix}/S{j}_{i}",
                                         (sx, yc), yaw)
                sc.build_slope(stage, f"{grp}/B", sx - run / 2.0, zt, run,
                               drop_j, y_lo, y_hi, thick,
                               mtl_fn(j) if mtl_fn else mtl,
                               margin=0.0, collider=collider)
                n += 1
        return n

    def river_prop(path, s, y, yaw_extra=0.0):
        """[v5.1] 사행 좌표계에 놓이는 단품 소품용 회전 그룹.
        (s, y) → 월드 (s+dx(y), y) 로 옮기고 국부 접선 + 배치 지터로 회전."""
        return sc.build_rot_group(stage, path,
                                  (river_dx(y) + s, y),
                                  river_yaw(y) + yaw_extra)

    # -------------------------------------------------------------------
    # 사면 상면 z(x) — 관목 착지 높이 근사 (x0..x0+run 에서 z0→z0-drop 선형)
    # -------------------------------------------------------------------
    def slope_z(x):
        sl = PARAMS["slope"]
        t = max(0.0, min((x - sl["x0"]) / sl["run"], 1.0))
        return sl["z0"] - sl["drop"] * t

    # 계단 디딤면 높이(레일 포스트 착지용 ground_fn) — build_straight_stairs 정합
    def stair_ground(x):
        st = PARAMS["stairs"]
        x0, riser, tread, n = st["x0"], st["riser"], st["tread"], st["nsteps"]
        if x <= x0:
            return 0.0
        if x >= x0 + tread * n:
            return -riser * n
        idx = min(int((x - x0) / tread), n - 1)
        return -riser * (idx + 1)

    # -------------------------------------------------------------------
    # 지형·계단 빌더
    # -------------------------------------------------------------------
    def build_levee(M):
        """둑마루: 기본 grass 대지 + 하천 평행 자갈 도로 밴드(폭 3m) + 계단 상단
        접속 스퍼(gravel). 자갈 밴드는 상판에서 1.5mm 돌출·5cm 매입.
        [v5.1] 전 밴드가 사행 폴리라인을 추종한다. 어깨(s=0)에 접한 서브밴드는
        폭 2.5 m 로 잘라 사면과의 겹침 lip 을 최소화하고, 배후 대지는 폭 12 m."""
        lv = PARAMS["levee"]
        top = lv["z_top"]
        # [W2-0 · P-A] Crest slabs are what ground_kit decorates. river_band
        # builds them through `sc.build_slope`, which carries no displacement
        # skin today, so this is a forward guard (prefix match covers the
        # per-segment rot groups).
        sc.skin_exclude(f"{ROOT}/LeveeBack", f"{ROOT}/Levee",
                        f"{ROOT}/LeveeRoad", f"{ROOT}/LeveeSpur")
        river_band(f"{ROOT}/LeveeBack", lv["x0"], -8.0, top, lv["thick"],
                   M["grass"], max_w=12.0)
        # 어깨측은 폭 2.5 — 사면과의 겹침 lip = (2.5+3.5)/2·(1/cos−cos)
        #   = 0.46 m @yaw 23°(y≈±35) · 0.09 m @yaw 10°(y≈±10) · 0 @회랑.
        river_band(f"{ROOT}/Levee", -8.0, lv["x1"], top, lv["thick"],
                   M["grass"], max_w=2.5, z_bias=-0.0005)
        # 자갈 도로 밴드 (하천 평행) — 상판 1.5 mm 돌출 · 5 cm 매입
        lr = PARAMS["levee_road"]
        z_top = top + lr["proud"]
        river_band(f"{ROOT}/LeveeRoad", lr["x0"], lr["x1"], z_top,
                   lr["proud"] + lr["embed"], M["gravel"], max_w=3.5)
        # 계단 상단 접속 스퍼 (gravel, s -1..0, y -1.2..1.2)
        #   회랑 근방은 dx≈0 · yaw≈0 이므로 축정렬 그대로 둔다(위험 기하 정합).
        ls = PARAMS["levee_spur"]
        z_bot = top - lr["embed"]
        sc.add_box(stage, f"{ROOT}/LeveeSpur",
                   ((ls["x0"] + ls["x1"]) / 2.0, (ls["y0"] + ls["y1"]) / 2.0,
                    (z_top + z_bot) / 2.0),
                   (ls["x1"] - ls["x0"], ls["y1"] - ls["y0"], z_top - z_bot),
                   M["gravel"], collider=True)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P13 levee_paved forced natural (spec §5.7 row 03).
    #   Runs in both hazard arms: the hazard-off twin must carry the same
    #   ground elements for the GT-E4 comparison to mean anything.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        lv, lr = PARAMS["levee"], PARAMS["levee_road"]
        z = lv["z_top"] + lr["proud"]
        gp = gk.plan_ground(
            "levee_paved",
            region=(g["x0"], -g["half_y"], lv["x1"], g["half_y"]),
            z=z, gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("shoulder", float(lv["x1"]))],
            dists=(2, 5, 10), scene="scene03",
            tactile=(),                 # §12.4 — p=0.24 공원/둔치, 미설치
            overrides=dict(
                natural=True,           # code-enforced: no urban infra here
                infra=dict(manhole=0, gully=0, gutter_L=0, marking=()),
                pave=dict(module=(None, None), joint=None,
                          step_x=None, step_y=None),
                surface=(("patch", len(g["patch"])),
                         ("stain", ("dirt", "water"))),
                extras=(("wear_lane", dict(width=0.90)),)),
            sites=dict(patch=[tuple(v) for v in g["patch"]]),
            extras_args=dict(wear_lane=dict(
                centerline=((g["wear_x"], -g["wear_y"]),
                            (g["wear_x"], g["wear_y"])))),
            seed=3)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(patch=M["dirt"], patch_cut=M["dirt"], wear=M["dirt"],
                  stain_dirt=M["dirt"], stain_water=M["concrete_dark"],
                  edge_break=M["dirt"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        # 경계 파쇄 (spec §5.7 "경계 파쇄") — the seam that crosses the h0.3
        #   frames is the gravel road edge, and it runs **along Y**, which
        #   `_compose_ops` cannot express (its `lines` are constant-y).
        #   Direct call, same builder, same z. |y| <= 3.0 keeps the straight
        #   strip on the meandering seam: |dx(3.0)| = 0.088 m < the 0.10 m half
        #   width of the transition band.
        #   Only the **landward** seam (x=-4.0) is broken. The river-side seam
        #   at x=-1.0 is 1.0 m in front of the shoulder: drow = 5.65 rows @1080
        #   at d10 against a 16-row floor, i.e. exactly the band GT-E2 keeps
        #   clear, and for |y| <= 1.2 it is gravel-on-gravel (LeveeSpur) so
        #   there is no material boundary to break there anyway.
        by = g["break_y"]
        nb = 0
        for tag, sx in (("W", lr["x0"]),):
            nb += gk.build_edge_break(
                kit, f"{ROOT}/GKit/EdgeBreak_{tag}",
                ((sx, -by), (sx, by)), z, M["dirt"])["prim_count"]
        print(f"[ground_kit] scene03 P13(natural) · prims {res['prims']} "
              f"+ edge_break {nb} · delta_max {res['gt_delta_max']:.4f}")
        return res

    def build_slopes(M):
        """사면 grass — 계단 회랑을 비우고 사행 밴드로 양측 조립.
        [v5.1] 회랑을 품는 세그는 yc=0 (yaw(0)=0 · dx(0)=0) 이므로 **회전도
        오프셋도 0** — 회랑 경계가 정확히 직선 y=±0.88 로 떨어진다. 0.95 대신
        0.88 을 쓰는 이유는 트림(y 0.75..0.95) 밑으로 0.07 물려 이음선을 없애기
        위함이고, 계단 측면 0.75 는 침범하지 않는다(검증: 코너 최소 |y|=0.88)."""
        sl = PARAMS["slope"]
        g = PARAMS["corridor"]["band_gap"]
        river_band(f"{ROOT}/Slope", sl["x0"], sl["x0"] + sl["run"], sl["z0"],
                   sl["thick"], M["grass"], drop=sl["drop"],
                   y_gap=(-g, g), max_w=3.5)

    def build_stairs(M):
        """콘크리트 직선 20단. cue_material_break OFF면 계단도 gravel(둑마루 동재질)."""
        st = PARAMS["stairs"]
        stair_mtl = M["concrete"] if cfg["cue_material_break"] else M["gravel"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"],
            stair_mtl, z_top=st["z_top"], collider=True)

    def build_trims(M):
        """계단 양측 소단 테두리: 폭 0.2 콘크리트 경사보 2장(y -0.95..-0.75 /
        0.75..0.95). 상면이 계단 노징 라인(drop 2.56)보다 0.05 위 — 사면 잔디와
        계단 사이 마감."""
        st = PARAMS["stairs"]
        tr = PARAMS["trim"]
        # N측: y -0.95..-0.75, P측: y 0.75..0.95
        for tag, y0, y1 in (("N", -0.95, st["y0"]), ("P", st["y1"], 0.95)):
            sc.build_slope(stage, f"{ROOT}/Trim_{tag}", st["x0"], tr["z0"],
                           st["tread"] * st["nsteps"], tr["drop"], y0, y1,
                           tr["thick"], M["concrete"], margin=tr["margin"],
                           collider=True)

    def build_beach(M):
        """둔치 z=-3.2 평탄 — dirt_park / grass 두 띠(경계 s=12).
        [v5.1] 전부 사행 밴드. 재질 경계(dirt↔grass)는 겹침 lip 이 그대로
        경계선의 굴곡이 되므로 max_w 를 작게 잡아 lip 을 0.3 m 이하로 묶는다."""
        bc = PARAMS["beach"]
        river_band(f"{ROOT}/BeachDirt", bc["x0"], bc["split_x"], bc["z_top"],
                   bc["thick"], M["dirt"], max_w=2.5)
        river_band(f"{ROOT}/BeachGrass", bc["split_x"], bc["x1"], bc["z_top"],
                   bc["thick"], M["grass"], max_w=3.0, z_bias=-0.002)
        # v4-A3: 하부 트레일 — 하천 평행 산책로 s 9.4..12.4 (곡률 추종)
        bp = PARAMS["beach_path"]
        river_band(f"{ROOT}/BeachPath", bp["x0"], bp["x1"], bp["z_top"],
                   bp["thick"], M["dirt"], max_w=3.0)
        # 계단 하단(s 7.0..9.4)과 산책로를 잇는 접속 에이프런 (y ±1.6)
        #   회랑 근방(dx≈0)이라 축정렬 유지.
        sc.add_box(stage, f"{ROOT}/BeachSpur",
                   ((bc["x0"] + bp["x0"]) / 2.0, 0.0,
                    bp["z_top"] - bp["thick"] / 2.0),
                   (bp["x0"] - bc["x0"], 3.2, bp["thick"]),
                   M["dirt"], collider=True)
        # v4-D4: 자전거도로 노면 표시 (가장자리 백선 2 + 중앙 파선) — 곡률 추종
        pl = PARAMS["path_lines"]
        for i, ex in enumerate(pl["edge_x"]):
            river_band(f"{ROOT}/PathLine_{i}", ex - pl["w"] / 2.0,
                       ex + pl["w"] / 2.0, pl["z_top"], pl["thick"],
                       M["line"], max_w=pl["w"], collider=False)
        for k in range(pl["dash_n"]):
            yd = pl["dash_y0"] + pl["dash_step"] * k
            grp = river_prop(f"{ROOT}/PathDash_{k}", pl["mid_x"], yd)
            sc.add_box(stage, f"{grp}/Box",
                       (river_dx(yd) + pl["mid_x"], yd,
                        pl["z_top"] - pl["thick"] / 2.0),
                       (pl["w"], pl["dash_len"], pl["thick"]), M["line"])

    def build_riprap(M):
        """수면-둔치 사이 사석 띠: rock_wall 낮은 경사보 (drop 0.15).
        [v5.1] 사행 밴드. 상단(s17)은 둔치(−3.2) 밑, 하단(s18.2)은 수면(−3.35)
        아래로 내려가므로 양쪽 접합이 항상 겹친다 = 수변 부유 0."""
        rp = PARAMS["riprap"]
        river_band(f"{ROOT}/Riprap", rp["x0"], rp["x0"] + rp["run"], rp["z0"],
                   rp["thick"], M["rock"], drop=rp["drop"], max_w=1.4,
                   z_bias=-0.003)

    def build_river(M):
        """수면(roughness 0.08) + 건너편 둔치(grass) + 원경 생울타리·나무
        — '건너편 재출현' 앵커 · 스케일 앵커 · 지평 폐쇄."""
        wt = PARAMS["water"]
        # [v5.1] 수면 3밴드도 사행 폴리라인 — 수변선이 제방·둔치와 같은 곡률.
        #   두께 0.4(구 build_water 0.2)로 키워 사석·건너편 둔치 밑으로 확실히
        #   물린다. 밴드 간 1.5 mm 스태거로 코플래너 Z파이팅 회피.
        for bi, (bs0, bs1, _) in enumerate(wt["bands"]):
            river_band(f"{ROOT}/Water_{bi}", bs0, bs1, wt["z"], 0.4,
                       M[f"water_{bi}"], max_w=3.5, z_bias=-0.002 * bi,
                       collider=False)
        fb = PARAMS["far_bank"]
        river_band(f"{ROOT}/FarBank", fb["x0"], fb["x1"], fb["z_top"],
                   fb["thick"], M["grass"], max_w=12.0)
        # v4-B3/D11: 원경 생울타리 띠 → 수목 라인 8본 (타일 해칭 줄무늬 제거)
        for i, t in enumerate(PARAMS["far_trees"]):
            tree_no_stake(M, f"{ROOT}/FarTree_{i}",
                          river_dx(t["cy"]) + t["cx"], t["cy"],
                          fb["z_top"], trunk_h=3.0, slot=i)
        # v4-D1 [최우선]: 원경 교량 — 하천축(Y)을 X로 횡단. 상판 x 12..46 이
        #   둔치(−3.2)·수면(−3.35)·건너편 둔치(−3.2)를 모두 건너므로 '하천'이
        #   한 컷에 확정된다. 교각 5본은 각 지반에서 상판 밑면(−1.0)까지.
        # [v5.1] 교량은 하천을 **직교 횡단**해야 한다 → 상판 중심 y 의 국부
        #   접선각만큼 통째로 회전(river_prop)하고 s→월드 X 변환을 얹는다.
        #   상판 하부는 -1.0 이하, 교각은 -3.7 까지 내려가므로 지반이 곡류를
        #   따라 좌우로 밀려도 교각 하단은 항상 지형에 묻힌다.
        bg = PARAMS["bridge"]
        deck_cy = (bg["y0"] + bg["y1"]) / 2.0
        deck_ly = bg["y1"] - bg["y0"]
        bdx = river_dx(deck_cy)
        bgrp = river_prop(f"{ROOT}/Bridge", (bg["x0"] + bg["x1"]) / 2.0,
                          deck_cy)
        sc.add_box(stage, f"{bgrp}/Deck",
                   (bdx + (bg["x0"] + bg["x1"]) / 2.0, deck_cy,
                    bg["deck_top"] - bg["deck_thick"] / 2.0),
                   (bg["x1"] - bg["x0"], deck_ly, bg["deck_thick"]),
                   M["concrete_dark"], collider=True)
        for tag, yc in (("S", bg["y0"] + bg["parapet_w"] / 2.0),
                        ("N", bg["y1"] - bg["parapet_w"] / 2.0)):
            sc.add_box(stage, f"{bgrp}/Parapet_{tag}",
                       (bdx + (bg["x0"] + bg["x1"]) / 2.0, yc,
                        bg["deck_top"] + bg["parapet_h"] / 2.0),
                       (bg["x1"] - bg["x0"], bg["parapet_w"], bg["parapet_h"]),
                       M["concrete_parapet"])   # [v5 판정 반영] 0.22 톤 분리
        pier_top = bg["deck_top"] - bg["deck_thick"]
        for i, px in enumerate(bg["pier_x"]):
            ph = pier_top - bg["pier_z0"]
            sc.add_cylinder(stage, f"{bgrp}/Pier_{i}",
                            (bdx + px, deck_cy, bg["pier_z0"] + ph / 2.0),
                            bg["pier_r"], ph, M["concrete_dark"], collider=True)
        # v4-D2: 건너편 도시 실루엣 3동 (base_z = far_bank 상면 −3.2)
        # [v5.1] 곡류 접선 + 동별 yaw 지터(전역 규약 3 — 축정렬 3동 정렬 금지)
        for key, bd in PARAMS["city"].items():
            bcy = (bd["y0"] + bd["y1"]) / 2.0
            cdx = river_dx(bcy)
            cgrp = river_prop(f"{ROOT}/City_{key}", (bd["x0"] + bd["x1"]) / 2.0,
                              bcy, yaw_extra=bd.get("jyaw", 0.0))
            shifted = dict(bd)
            shifted["x0"] = bd["x0"] + cdx
            shifted["x1"] = bd["x1"] + cdx
            shifted["facade_x"] = bd["facade_x"] + cdx
            sc.build_building(stage, f"{cgrp}/B", shifted, M["city"],
                              M["city_glass"], M["city_parapet"])

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 계단·사면·둔치를 z=0 평지로 통일
        (둑마루~x18 gravel 평지). 낙차/위험 제거.
        주의: 수면·건너편 둔치는 원경 요소로 잔존 — 완전 평지 대조군은
        cue_scene_dressing=False 와 조합(수변까지 제거하려면 build_river 도 스킵)."""
        lv = PARAMS["levee"]
        bc = PARAMS["beach"]
        # [v5.1] 대조군도 같은 사행 밴드로 깔아야 둑마루와 이음이 맞는다.
        river_band(f"{ROOT}/FlatFill", 0.0, bc["x1"], lv["z_top"],
                   lv["thick"], M["gravel"], max_w=4.0)

    # -------------------------------------------------------------------
    # 소품 빌더 (cue_scene_dressing)
    # -------------------------------------------------------------------
    def build_dressing(M):
        # 둑마루 볼라드 2 (스퍼 양옆 — 계단 진입 전면 차량 저지).
        # [v5.1 전역 규약 2] h 0.90 · r 0.075 · 상단 백색 반사띠.
        bo = PARAMS["bollard"]
        for i, b in enumerate(PARAMS["bollards"]):
            bx = river_dx(b["cy"]) + b["cx"]
            sc.build_bollard(stage, f"{ROOT}/Bollard_{i}", bx, b["cy"], 0.0,
                             mtl=M["bollard"], radius=bo["r"],
                             height=bo["h"])
            sc.add_cylinder(stage, f"{ROOT}/BollardBand_{i}",
                            (bx, b["cy"], bo["band_z"] + bo["band_h"] / 2.0),
                            bo["r"] * 1.04, bo["band_h"], M["bollard_band"])
            sc.add_cylinder(stage, f"{ROOT}/BollardCap_{i}",
                            (bx, b["cy"], bo["h"] + 0.015),
                            bo["r"] * 1.15, 0.03, M["bollard"])
        # v4-D7: 벤치 4 (둑마루 2 + 둔치 2) — [v5.1] 앵커 옆 비대칭 배치,
        #   yaw 는 국부 접선 + 지정 각(비정수) 합.
        for i, (bx, by, bz_, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", river_dx(by) + bx, by,
                           bz_, M["wood_dark"], yaw=yaw + river_yaw(by))
        # v4-B1 / [v5.1 재수정]: 사면 관목 = 눌린 타원체 3개 중첩.
        #   경사 슬래브(v4)는 v5 판정에서 '각진 판떼기'로 확인된 형상이라 폐기.
        #   구배는 배치 높이(slope_z)로만 반영 — 축정렬 회전체라 절단면 없음.
        hb = PARAMS["hedge"]
        emb = hb["embed"]
        for i, h in enumerate(PARAMS["hedges"]):
            for j, (dx, dy, rx, ry, rz) in enumerate(hb["blobs"]):
                cx = h["cx"] + dx
                cy = h["cy"] + dy
                sc.add_sphere(stage, f"{ROOT}/Hedge_{i}_{j}",
                              (river_dx(cy) + cx, cy,
                               slope_z(cx) + rz * (1.0 - emb)),
                              (rx, ry, rz),
                              M["hedge_v"][(i + j) % len(M["hedge_v"])])
        # 둔치 나무 2 (수관 상단이 둑마루 눈높이 아래 — 앵커) + v4-D10 증식 6
        bz = PARAMS["beach"]["z_top"]
        for i, t in enumerate(PARAMS["trees"]):
            tree_no_stake(M, f"{ROOT}/Tree_{i}", river_dx(t["cy"]) + t["cx"],
                          t["cy"], bz, slot=i)
        for i, t in enumerate(PARAMS["trees_extra"]):
            tree_no_stake(M, f"{ROOT}/TreeX_{i}", river_dx(t["cy"]) + t["cx"],
                          t["cy"], t["gz"], slot=i + 2)
        # v4-D5: 갈대 밴드 (수변 전이) — [v5.1] 수변 곡률 추종 사행 밴드
        rd = PARAMS["reeds"]
        river_band(f"{ROOT}/Reed", rd["x0"], rd["x1"], rd["base_z"] + rd["h"],
                   rd["h"], M["reed"], max_w=1.0, collider=False)
        # v4-D6: 둑마루 자전거도로 중앙선 + 거리표지 2
        ll = PARAMS["levee_line"]
        river_band(f"{ROOT}/LeveeLine", ll["x"] - ll["w"] / 2.0,
                   ll["x"] + ll["w"] / 2.0, ll["z_top"], ll["thick"],
                   M["line"], max_w=ll["w"], collider=False)
        mk = PARAMS["marker"]
        for i, (ms, my, jy) in enumerate(PARAMS["markers"]):
            mx = river_dx(my) + ms
            grp = river_prop(f"{ROOT}/Marker_{i}", ms, my, yaw_extra=jy)
            sc.add_cylinder(stage, f"{grp}/Post",
                            (mx, my, mk["post_h"] / 2.0), mk["post_r"],
                            mk["post_h"], M["bollard"], collider=True)
            sc.add_box(stage, f"{grp}/Plate",
                       (mx, my, mk["plate_z"]), mk["plate"], M["line"])
        # v4-D7: 파고라 1 (휴게 = 사람이 오는 곳)
        pg = PARAMS["pergola"]
        pcy = (pg["y0"] + pg["y1"]) / 2.0
        pdx = river_dx(pcy)
        pgrp = river_prop(f"{ROOT}/Pergola", (pg["x0"] + pg["x1"]) / 2.0, pcy,
                          yaw_extra=pg["jyaw"])
        sc.build_canopy(stage, f"{pgrp}/C", pg["x0"] + pdx, pg["x1"] + pdx,
                        pg["y0"], pg["y1"], pg["z_roof"], pg["post_r"],
                        M["wood_dark"], M["wood_dark"], roof_t=pg["roof_t"],
                        base_z=0.0)
        # v4-D8: 둔치 운동장 라인 (사각 4선) — 강체 사각형이므로 통째로 회전
        fd = PARAMS["field"]
        fcy = (fd["y0"] + fd["y1"]) / 2.0
        fdx = river_dx(fcy)
        fgrp = river_prop(f"{ROOT}/Field", (fd["x0"] + fd["x1"]) / 2.0, fcy)
        for tag, cx, cy, sx, sy in (
                ("W", fd["x0"], fcy, fd["w"], fd["y1"] - fd["y0"]),
                ("E", fd["x1"], fcy, fd["w"], fd["y1"] - fd["y0"]),
                ("S", (fd["x0"] + fd["x1"]) / 2.0, fd["y0"],
                 fd["x1"] - fd["x0"], fd["w"]),
                ("N", (fd["x0"] + fd["x1"]) / 2.0, fd["y1"],
                 fd["x1"] - fd["x0"], fd["w"])):
            sc.add_box(stage, f"{fgrp}/Line_{tag}",
                       (cx + fdx, cy, fd["z_top"] - fd["thick"] / 2.0),
                       (sx, sy, fd["thick"]), M["line"])
        # v4-D9: 수위표 (백색 기둥 + 적색 밴드 3)
        gg = PARAMS["gauge"]
        gh = gg["z1"] - gg["z0"]
        gx = river_dx(gg["cy"]) + gg["cx"]
        sc.add_cylinder(stage, f"{ROOT}/Gauge/Post",
                        (gx, gg["cy"], gg["z0"] + gh / 2.0), gg["r"],
                        gh, M["line"], collider=True)
        for i, gz in enumerate(gg["band_z"]):
            sc.add_cylinder(stage, f"{ROOT}/Gauge/Band_{i}",
                            (gx, gg["cy"], gz), gg["r"] * 1.06,
                            gg["band_h"], M["gauge_band"])

    # -------------------------------------------------------------------
    # 단서 빌더 (cue_railing / cue_nosing / cue_tactile)
    # -------------------------------------------------------------------
    def build_cues(M):
        st = PARAMS["stairs"]
        run = st["tread"] * st["nsteps"]           # 20×0.35 = 7.0
        drop = st["riser"] * st["nsteps"]          # 20×0.16 = 3.2
        # cue_railing (정체성): True면 계단 우측 y=+0.85 파이프 레일 1선만
        if cfg["cue_railing"]:
            sc.build_railing_line(
                stage, f"{ROOT}/Rail", 0.85, -1.0, st["x0"], run, drop,
                stair_ground, M["rail"], rail_h=0.9)
        # cue_nosing (신규): 전 단 논슬립 단코 띠
        if cfg["cue_nosing"]:
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"], base_z=st["base_z"],
                z_top=st["z_top"])
        # cue_tactile (이 씬 미사용 — 코드 경로만): 둑마루 어깨 0.3m 앞 황색 띠
        if cfg["cue_tactile"]:
            sc.build_tactile(stage, f"{ROOT}/Tactile", st["x0"] - 0.3,
                             st["x0"], st["y0"], st["y1"],
                             sc.make_pbr(stage, f"{ROOT}/TactileMtl",
                                         sc.tex_path("gravel", "diff"),
                                         sc.tex_path("gravel", "nor"),
                                         sc.tex_path("gravel", "rough"), 0.3,
                                         tint=(1.6, 1.3, 0.2)), z=0.0)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_levee(M)
    if cfg["hazard_stairs"]:
        build_slopes(M)
        build_stairs(M)
        build_trims(M)
        build_beach(M)
        build_riprap(M)
    else:
        build_flat_fill(M)          # 대조군: z=0 평지 통일
    build_ground_kit(M)             # [W2-D] both arms — GT-E4 twin parity
    build_river(M)                  # 수면·건너편 둔치는 상시 (원경 증거)
    if cfg["cue_scene_dressing"] and cfg["hazard_stairs"]:
        build_dressing(M)
    build_cues(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── 카메라 + 렌더 모드 ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["levee_walk"]
    look_from(_v0["eye"], _v0["tgt"])              # 시작 카메라 = 미장센

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

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

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
    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]                           # [ / ] 키 사용자 오프셋

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene03_{ts}.png")
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
