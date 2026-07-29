# -*- coding: utf-8 -*-
"""
scene02_underpass.py — NegObs 인공씬 2호: 지하도/지하철 입구 (Isaac Sim 4.5)

유형    : T3 지하도 (설비 완비 × 하부 암부)
사양서  : Docs/multi_scene_brief_v2.md §C scene02_underpass (유일 사양)
공통    : scene_common.py (검증된 API 헬퍼) · scene01_campus_stairs.py (골격)

위험 본질: 지상 보도에 뚫린 하강 피트. 낮은 시점(h0.3 원거리)에서 피트가
           완전한 평지로 보이고 난간·점자블록만 떠 있는 그림 → 계단 20단
           낙차 3.2m가 grazing 각에서 은닉. 하부는 dome 차폐로 자연 암부.
목표     : 지상 보도(개구) + 옹벽 피트 + 20단 계단 + 하부 랜딩 + 터널 포탈을
           GUI로 띄우고 렌더로 판정 (렌더 전용, 물리 콜라이더만 — 시뮬 스텝 없음).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene02_underpass.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene02_underpass.py
      NEGOBS_CAPTURE_DIR  : 저장 폴더 (기본 look_check/scene02/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (기본 rt)
      NEGOBS_VIEWS        : 쉼표로 뷰 이름 필터 (기본 전부)

좌표계: Z-up, m, 진행축 +X, 낙차 시작 모서리 = x=0.

===========================================================================
⚠️ 아래는 **설계안이며 아직 코드에 반영되지 않았다**(2026-07-29).
   작성 중 세션이 사용량 한도로 중단됐다. 좌표 검산은 끝났으니 다음 세션이
   이 표대로 구현하면 된다. 구현 완료 시 이 경고 블록을 지울 것.
===========================================================================
기하 핵심 (수치 검산) — [v8 설계안] 법정 계단참 + 광폭 중간난간
===========================================================================
진단 근거 : Docs/reports/stair_compliance_v1.md §1 scene02 행 (P0-L1 · P0-R1)
계산 도구 : stair_kit.stair_landings() / mid_rail_lines() / build_stair_landing()
            — 이 파일은 계단참 좌표를 **직접 계산하지 않는다**(단일 진실원).

  L1 계단참 : 낙차 3.20 > 법정 3.00 (피난방화 §15①1) → 참 1개 의무.
      stair_landings(3.20, 0.160, 0.320) ⇒ m = floor(3.00/0.160) = 18,
      n_flights = ceil(20/18) = 2, 20 = 10 + 10 (앞쪽 우선 배분, 결정적).
      run 6.40 → **7.60** (+1.20 = 참 깊이, 법정 하한 1.20 정확히).
  R1 중간난간 : 폭 3.50 > 3.00 이고 면제조건이 **AND** 라 riser 0.160 > 0.150
      에서 이미 탈락 → 의무. mid_rail_lines(−1.75, 1.75, 0.160, 0.320)
      ⇒ n_bays = ceil(3.50/3.00) = 2 → **y = 0.000 1열**(각 베이 1.75).

[보행 연속성 z 사다리]  진입 → 하강 → 계단참 → 하강 → 탈출 (전 단차 ≤ 0.160)
  ┌ #  구간                x 구간         상면 z      단차/판정
  │ 0  지상 보도            ≤ 0.00        +0.000      평탄 (개구 전연 = 낙차 3.200)
  │ 1  flight0 1단      0.00 … 0.32       −0.160      0.160
  │ 2  flight0 5단      1.28 … 1.60       −0.800      0.160 × 4
  │ 3  flight0 10단     2.88 … 3.20       −1.600      0.160 × 5   ← flight0 끝
  │ 4  **계단참**       3.20 … 4.40       −1.600      0.000 (평탄 1.200)
  │ 5  flight1 1단      4.40 … 4.72       −1.760      0.160       ← 참 전연 에지
  │ 6  flight1 5단      5.68 … 6.00       −2.400      0.160 × 4
  │ 7  flight1 10단     7.28 … 7.60       −3.200      0.160 × 5
  │ 8  하부 랜딩        7.60 … 8.20       −3.200      0.000 (flush)
  └ 9  터널 바닥        8.20 … 12.20      −3.200      0.000 (flush)
  * 총 낙차 보존: 10×0.160 + 0 + 10×0.160 = 3.200 = 구 20×0.160.
  * 불연속 0: flight0.z_bot = 참.z = flight1.z_top = −1.600 (stair_kit 자기검사 (4)).
  * 하류 이동 +1.20 : 피트 x1 7.0→8.2 · 하부 랜딩 6.4→7.6 · 터널 x0 7.0→8.2 ·
    둘레난간 x1/x_rear · 잔디 개구 gx1 7.6→8.8 · 도로 8.0→9.2(연석·차선 동반) ·
    터널등 3본 · Exit 사인 7.8→9.0. (x ≤ 3.20 구간은 좌표 **완전 불변**)

[GT 변경] — 계단참은 z(x) 프로파일을 바꾸므로 낙차/뎁스 GT 캐시 재생성 필수
  · 낙차 에지 수 : 20 → **21** (계단코 20 + **계단참 전연 1**)
  · 새 에지      : x = 4.400, y ±1.75, 상면 z = −1.600.
                   이 에지에 걸리는 잔여 낙차 = 하류 flight1 합 = **1.600 m**
  · 새 평지 띠   : x 3.200…4.400 × y −1.75…1.75 = 1.20 × 3.50 = **4.20 m²**,
                   국지 낙차 **0** (참 상면. 라벨상 계단면이 아니라 평지)
  · 불변         : 개구 전연 x=0 의 총 낙차 3.200 · 단코 주기 0.320 · riser 0.160
                   (참 구간에서만 주기가 1회 끊긴다 — 단코 실루엣 단서는 보존)
  · 중간난간·손잡이는 z(x,y) 를 만들지 않으므로 **GT 불변**(자기폐색만 증가).

[카메라 차폐 검산]  (build_views 좌표를 그대로 대입)
  · 그리드 gy : 0.000 → **−0.875**(남측 베이 중심). 중간난간 y=0 이 프리셋 축을
    정면으로 가리는 것을 회피 — scene01 R2-1(중앙 난간 회피 gy=−2.75) 선례 동일.
    −0.875 는 |y| ≤ 1.75 개구 안이라 피트 정면 조망은 유지된다.
  · h0.3 은닉 보존 : 연단(x=0,z=0) 스치는 시선이 참 상면(−1.600)에 닿는 x
    = 1.600·d/0.3 = 5.33·d → d=2 에서 10.7 m > 참 하류단 4.40 → **참은 은닉**.
    (참이 −1.600 으로 얕아졌지만 grazing 시선은 여전히 도달하지 못한다.)
  · h1.8/d2 는 x=3.56 부터 참 상면이 보인다(0.9/… 판정 컷 — 의도된 노출).
  · 계단참 AABB(x 3.20…4.40 · y ±1.75 · z −3.50…−1.600) 안에 들어가는 eye 없음.
  · inside_looking_up : eye x 6.60 → **7.80**(+1.20, 하부 랜딩 위 0.50 m 유지),
    y 0.00 → −0.875 (중간난간 y=0 정면 차폐 회피). 시선은 x=4.40 에서 참 상면
    위 0.065 m 로 통과 → 참에 막히지 않는다.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import stair_kit as sk           # 법정 계단참·중간난간 (좌표 계산 단일 진실원)


# ===========================================================================
# [A] SCENE_CONFIG — scene01 6키 + cue_nosing(신규). 토글은 위험 기하 불변
#     (hazard_stairs 만 예외: False → 피트를 z=0 평지로 메움).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 피트/계단/옹벽/터널을 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        True,   # 계단 양측 벽부착 경사 레일 2선 + 피트 지상 둘레 3면 난간
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)   # 점형 점자블록: 상단 x=-0.3 경고띠 + 하부 랜딩
    "cue_material_break": True,   # False → 계단·랜딩도 보도블록재(plaza_lower)로 통일
    "cue_nosing":         True,   # [신규] 전 단 황색 논슬립 띠 (지하철 관행)
    "cue_sign":           True,   # [v5 공통 레이어] 한글 사인 1매 (터널 출구 표지)
    "cue_scene_dressing": True,   # 벽돌 건물·생울타리·가로등·원경 비스타 일괄
}


# ===========================================================================
# [B] PARAMS — 치수·재질·조명. NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG 머지.
# ===========================================================================
PARAMS = dict(
    # --- 지상 보도 (개구를 둘러싼 4박스 분할) ---
    walk=dict(x_w=-18.0, x_e=16.0, y_s=-8.0, y_n=8.0, z_top=0.0, thick=0.5),
    # 하강 피트 개구: 계단 폭 = 옹벽 내면 사이 3.5 (y ±1.75)
    pit=dict(x0=0.0, x1=7.0, y0=-1.75, y1=1.75),
    # 계단 20단 × riser 0.16 · tread 0.32 → 낙차 3.2m, run 6.4m. z_top=0
    stairs=dict(x0=0.0, riser=0.16, tread=0.32, nsteps=20,
                y0=-1.75, y1=1.75, z_top=0.0, base_z=-3.5),
    landing=dict(x0=6.4, x1=7.0, z_top=-3.2, base_z=-3.5),   # 하부 랜딩
    # 옹벽: 두께 0.3, 내면 ±1.75(계단 폭 접), 외면 ±2.05, 파라펫 상면 +0.15
    wall=dict(thick=0.3, y_in=1.75, parapet_top=0.15, base_z=-3.5),
    # 터널 포탈: x=7 개구 3.5(폭)×2.3(높이) — 랜딩(z-3.2) 위 z -3.2..-0.9,
    #   깊이 4m 내부 박스(x 7..11), 상부 인방(z -0.9..0.15) 잔존
    tunnel=dict(x0=7.0, depth=4.0, open_w=3.5, open_h=2.3,
                floor_z=-3.2, lintel_top=0.15),
    # 피트 지상 둘레 난간(3면): 남·북 x 0..7 y=±1.9, 후면 x=7.15
    perim_rail=dict(y=1.9, x0=0.0, x1=7.0, x_rear=7.15,
                    parapet_top=0.15, rail_h=0.9, post_r=0.03,
                    rail_r=0.03, rail_mid_r=0.018, mid_h=0.45, spacing=1.2),
    # 계단 양측 벽부착 경사 레일: y=±1.65 (내면 0.1 안쪽), x_start=-0.5
    stair_rail=dict(y=1.65, x_start=-0.5, rail_h=0.9, post_r=0.02,
                    rail_r=0.03, rail_mid_r=0.018, rail_mid_drop=0.45,
                    spacing=1.2),
    tactile=dict(ahead=0.3, depth=0.3, proud=0.004,   # 상단 경고띠 x=-0.3..0
                 land_depth=0.4),                      # 랜딩 점자 폭
    # v4-B1: width 0.05/proud 0.001 은 512spp 디노이즈에서 소실 → 20단이 램프로
    #   읽힘. 0.08 / 0.004 로 확대(단서 토글 소속 — 위험 기하 트랜스폼 불변).
    nosing=dict(color=(0.85, 0.72, 0.10), width=0.08, proud=0.004),

    # 주변 대지 / 드레싱
    # 잔디 대지 (보도 0보다 3cm 아래). 피트 풋프린트(gx/gy)를 비우는 4박스 분할
    #  — 잔디 슬래브(z=-0.03)가 계단 상단(-0.16..)보다 위라 개구를 덮는 것 방지.
    #  터널(x 7..11 지하)은 자체 천장이 있어 gx1(7.6) 밖 잔디는 유지 무해.
    ground=dict(size=140.0, z_top=-0.03,
                gx0=-0.5, gx1=7.6, gy0=-2.3, gy1=2.3),
    # v4-B2: 생울타리가 '검은 직육면체'로 읽힘 → 틴트 상향 + 4세그 높이 변주로
    #   블록감 해소. 도로(x 8..13) 앞에서 종료(x1 6.8), y −6→−7 (화단 회피).
    hedge=dict(x0=-16.0, x1=6.8, y=-7.0, half=0.3, h=1.0, nseg=4,
               h_var=(0.0, -0.15, 0.05, -0.10), y_var=(0.0, 0.08, -0.06, 0.05)),

    # === v4-D1 도로 (최우선 맥락단서: 지하도의 '존재 이유') ===
    #   터널(x 7..11, 천장 상면 −0.6)이 도로 밑을 지난다는 서사를 성립시킨다.
    #   보도 동편(기존 Walk_E x 7..16)을 도로 폭만큼 잘라 E1/E2 로 분할.
    road=dict(x0=8.0, x1=13.0, y0=-60.0, y1=60.0, top=-0.02, thick=0.5,
              walk_a=7.7, walk_b=13.3,                 # 연석 바깥면 = 보도 절단면
              curb_top=0.10, curb_base=-0.5,
              lane_x=10.5, lane_w=0.12, dash_len=3.0, dash_step=6.0,
              dash_y0=-36.0, dash_n=13),
    # === v4-D 그 밖의 맥락 드레싱 ===
    # D4 지하도 입구 사인 (기둥 2 + 판 1) — 한 컷에 '지하도' 확정
    # [v5.1 현실성] 피드백 "게시판(패널) 위치 부자연" → **진입부 측면**으로 이설.
    #   구: y −2.6..−0.6 (보행축 y=0 을 0.6 m 까지 침범) · z 2.0..2.6 (기둥 상단에
    #     매달린 문형 갠트리 인상 = 부유 패널).
    #   신: y +1.9..+3.7 (피트 난간선 y=+1.9 에 접한 **측면**, 개구 y ±1.75 밖
    #     0.15 m) · z 1.5..2.25 (기둥 h2.25 상단걸이 = 표준 지주식 안내판).
    #   카메라 검산(그리드 gy=0 · 화각 ±30°): eye(−2) 후방 · eye(−5) 60.3° 밖 ·
    #     eye(−10) 23.0°(7.2 m 원경) · approach(−6,0) 47.1° 밖 ·
    #     pit_edge(−0.5,0) 후방 · beauty_overview(−7,−5) 시선축 31.0° 대비
    #     65.2°(34.2° 이탈) 밖 · inside_looking_up 은 10.4 m 후경(파라펫 위) →
    #     근접(<1.2 m) ∧ 화각 안 조합 0건.
    sign=dict(x=-3.4, y0=1.9, y1=3.7, z0=1.5, z1=2.25, thick=0.08,
              post_r=0.05, post_h=2.25),
    # D5 계단 상단 캐노피 (지하철 출입구 실루엣)
    canopy=dict(x0=-1.8, x1=0.6, y0=-2.45, y1=2.45, z_roof=2.7, post_r=0.08,
                roof_t=0.14, base_z=0.0),
    # D6 노선도/안내 게시판 — [v5.1] **삭제**(개수 축소).
    #   피드백 "개수 축소 / 중복되면 게시판 쪽을 줄일 것" → 게시판을 없애고
    #   진입부 안내는 D4 지하도 입구 사인 1매로 정리한다.
    # [v5 공통 레이어] 한글 사인 — (태그, TEX 키, cx, cy, base_z, yaw, w, h, pole_h)
    #   [v5.2 사용자] 임의 경고 팻말 제거 — Caution(계단주의) 삭제, 출구 표지만 잔존.
    #   Exit(7.8, −1.4, z −3.2): 터널 **안**(x 7..11, 바닥 −3.2, 유효고 2.3).
    #     패널 상단 = −3.2+2.1−0.05 = −1.15 < 인방 하단 −0.9 → 천장 여유 0.25 m.
    #     터널 폭 y ±1.75 기준 남측 벽에서 0.35 m — 통행 중앙(y=0) 비움.
    #   카메라 검산(그리드 gy=0, eye x −2/−5/−10, 화각 ±30°):
    #     Exit    → 터널 개구 안(정면) — approach/pit_edge 의 판정 대상(암부 판독)
    #     inside_looking_up(6.6,0,−2.7) 은 −X 를 보므로 Exit 은 후방.
    signs=[("Exit", "sign_exit", 7.8, -1.4, -3.2, 180.0, 0.9, 0.45, 2.1)],
    # D7 볼라드 (보도 경계) — 사인·캐노피 기둥과 겹치지 않는 y만
    bollards=[(-1.0, -6.0), (-1.0, -4.3), (-1.0, 4.3), (-1.0, 6.0)],
    # D8 벤치 2 + 쓰레기통 2
    benches=[(-6.0, -4.0, 0.0), (-6.0, 4.0, 0.0)],
    bins=[(-2.0, -4.0), (-2.0, 4.0)],
    bin_spec=dict(r=0.28, h=0.9),
    # D11 화단 2 (생울타리 단독 대체)
    planters=[(-8.0, -5.0), (-13.0, 5.5)],
    # D10 터널 내부 형광등 3 (암부에 정보 부여 — 데이터 가치 확보)
    # [v5 판정 반영] intensity 1500 은 정오 태양(2450) + 돔(1000) 노출 기준에서
    #   화면 기여가 사실상 0 이라 RT 컷의 터널 개구가 전부 '순수 검정'이었다.
    #   (pit_edge / approach / beauty_overview 모두 암부 그라디언트 없음)
    #   본 씬의 판정 포인트가 '개구 암부에 계단 하부·점자가 읽히는가'이므로
    #   1500 → 45000(권고 3만~6만의 중앙값)으로 상향한다.
    #   광원 위치·개수·반경은 불변 — 기하/노출 프로파일에 영향 없음.
    tunnel_lights=dict(pos=[(8.0, 0.0, -1.05), (9.5, 0.0, -1.05),
                            (10.5, 0.0, -1.05)],
                       radius=0.12, intensity=45000.0,
                       color=(0.92, 0.95, 1.0)),
    buildings=dict(
        # 벽돌 건물 1동: y 9..13, x -14..10, h10. 파사드 -Y평면(보도쪽), 창문 x배열
        B=dict(x0=-14.0, x1=10.0, y0=9.0, y1=13.0, h=10.0, floors=4,
               axis="y", facade_y=9.0, face_dir=-1.0),
        # 원경 비스타: +X 건물 1동. 파사드 -X평면, 창문 y배열
        C=dict(x0=22.0, x1=28.0, y0=-10.0, y1=10.0, h=10.0, floors=4,
               axis="x", facade_x=22.0, face_dir=-1.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),
    streetlight=dict(pole_h=6.0, pole_r=0.06,
                     arm_len=1.0, arm_r=0.04, head=0.25),
    # v4-D9: 가로등 1→4본 (도시 리듬). (x, y, base_z)
    streetlights=[(-4.0, 6.5, 0.0), (-10.0, 6.5, 0.0), (2.0, 6.5, 0.0),
                  (14.5, 6.5, 0.0)],

    # --- 재질: texture_scale용 물리 크기[m/타일] + 틴트/상수 ---
    material=dict(
        scale=dict(plaza_lower=0.7, concrete_floor=1.0, concrete_wall=2.0,
                   grass=1.4, brick_red=2.0, granite_dark=1.0, tactile=0.3),
        grass_tint=(0.55, 0.68, 0.42),
        hedge_tint=(0.50, 0.64, 0.38),            # v4-B2 생울타리 (검은 판 해소)
        tunnel_tint=(0.32, 0.32, 0.34),           # 터널 짙은 콘크리트 틴트
        asphalt_color=(0.045, 0.045, 0.047), asphalt_rough=0.75,  # v4-D1 노면
        lane_color=(0.55, 0.55, 0.52),            # v4-D2 차선 표시
        sign_color=(0.045, 0.085, 0.19), sign_face=(0.55, 0.56, 0.58),
        seat_wood=(0.13, 0.085, 0.05), seat_wood_rough=0.8,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,   # 나무 줄기
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030),
        canopy_rough=1.0,                          # v4-B(공통): 수관 알베도 상향
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # [v5.1 §4] 파라펫 0.90 → 0.72 (순백 대면적 금지)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
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


# 파라미터 오버라이드 (A/B 렌더 비교용 — 기본 실행엔 영향 없음)
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
# [C] 경로 상수 + 필요 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene02")

# check_assets 에 전달할 사용 역할 (concrete_wall/floor·plaza_lower·grass·
# brick_red·granite_dark·tactile + HDRI + MDL)
ASSET_ROLES = ["plaza_lower", "concrete_floor", "concrete_wall", "grass",
               "brick_red", "granite_dark", "tactile",
               "sign_exit",     # [v5.2 사용자] 임의 경고 팻말 제거
               "hdri", "mdl"]


def build_views():
    """카메라 프리셋: grid_views(gy=0.0) 9장 + 미장센 4컷 (§C)."""
    views = sc.grid_views(0.0)               # 이 씬은 중앙 난간 없음 → gy=0
    # approach: 보도에서 피트로 접근
    views["approach"] = dict(eye=[-6.0, 0.0, 1.5], tgt=[3.0, 0.0, -0.6])
    # pit_edge: 모서리 위에서 아래로 -15° (dx5, dz-1.3 → -14.6°)
    views["pit_edge"] = dict(eye=[-0.5, 0.0, 1.7], tgt=[4.5, 0.0, 0.4])
    # inside_looking_up: 랜딩에서 지상 역광으로 올려봄
    views["inside_looking_up"] = dict(eye=[6.6, 0.0, -2.7], tgt=[-3.0, 0.0, 1.0])
    # beauty_overview: 사선 부감 인상
    views["beauty_overview"] = dict(eye=[-7.0, -5.0, 3.0], tgt=[3.0, 1.0, -1.2])
    return views


# ===========================================================================
# [D] Isaac Sim 씬 조립 + 메인 루프
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach / beauty  — 지하도 피트 인상 (개구·옹벽·계단·터널 포탈 식별)
 2. h0.3·d5~10         — 피트가 완전한 평지로 보이고 난간·점자만 뜨는가
 3. pit_edge / inside  — 피트 내부 깊이감·암부 그라디언트, 터널 포탈 암부
 4. cue ON vs OFF      — 피트·계단·옹벽 기하 트랜스폼 동일한가 (nosing/railing/tactile)
 5. 재질               — 타일 반복·늘어남·Z파이팅·부유 없는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    # ── 1단계: Isaac Sim 부팅 (SimulationApp이 무조건 먼저) ──
    simulation_app = sc.boot(capture_mode)

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
    UsdGeom.Xform.Define(stage, "/World/Scene02")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene02"

    # 얇은 지오메트리 래퍼 (stage 캡처)
    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        # scene_common.make_pbr 는 stage 가 첫 위치 인자 — 여기서 주입
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["sidewalk"] = PBR(
            f"{ROOT}/Looks/Sidewalk", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"])
        M["concrete_floor"] = PBR(
            f"{ROOT}/Looks/ConcreteFloor", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"])
        M["concrete_wall"] = PBR(
            f"{ROOT}/Looks/ConcreteWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"])
        # 터널 내부: concrete_wall 텍스처 + 짙은 틴트 (dome 차폐 암부 보강)
        M["tunnel"] = PBR(
            f"{ROOT}/Looks/Tunnel", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"],
            tint=mp["tunnel_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["granite_dark"] = PBR(
            f"{ROOT}/Looks/GraniteDark", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"),
            sc.tex_path("granite_dark", "rough"), sca["granite_dark"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        # 상수 컬러
        M["glass"] = PBR(f"{ROOT}/Looks/Glass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                                   diffuse_color=mp["parapet_color"],
                                   roughness_const=mp["parapet_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp",
                                diffuse_color=mp["lamp_color"],
                                roughness_const=mp["lamp_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole",
                                diffuse_color=mp["pole_color"],
                                metallic=mp["pole_metallic"],
                                roughness_const=mp["pole_rough"])
        # v4-D 드레싱 전용 재질
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"])
        M["lane"] = PBR(f"{ROOT}/Looks/Lane",
                        diffuse_color=mp["lane_color"], roughness_const=0.75)
        M["hedge"] = PBR(
            f"{ROOT}/Looks/Hedge", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            1.2, tint=mp["hedge_tint"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=0.5)
        M["sign_face"] = PBR(f"{ROOT}/Looks/SignFace",
                             diffuse_color=mp["sign_face"],
                             roughness_const=0.6)
        M["seat_wood"] = PBR(f"{ROOT}/Looks/SeatWood",
                             diffuse_color=mp["seat_wood"],
                             roughness_const=mp["seat_wood_rough"])
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
        return M

    # -------------------------------------------------------------------
    # 대지 (상시): 잔디 대지 z=-0.03 (보도 0보다 3cm 아래, 부지 밖 허공 방지)
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        cz = g["z_top"] - 0.25
        th = 0.5
        H = g["size"] / 2.0                       # ±70
        gx0, gx1 = g["gx0"], g["gx1"]             # 피트 풋프린트 x (-0.5..7.6)
        gy0, gy1 = g["gy0"], g["gy1"]             # 피트 풋프린트 y (-2.3..2.3)
        # 피트 풋프린트를 비우는 4박스 (보도 개구와 동일 기법)
        # 서: -H..gx0 전폭
        BOX(f"{ROOT}/Grass_W", ((-H + gx0) / 2.0, 0.0, cz),
            (gx0 + H, g["size"], th), M["grass"])
        # 동: gx1..H 전폭
        BOX(f"{ROOT}/Grass_E", ((gx1 + H) / 2.0, 0.0, cz),
            (H - gx1, g["size"], th), M["grass"])
        # 남: gx0..gx1, -H..gy0
        BOX(f"{ROOT}/Grass_S", ((gx0 + gx1) / 2.0, (-H + gy0) / 2.0, cz),
            (gx1 - gx0, gy0 + H, th), M["grass"])
        # 북: gx0..gx1, gy1..H
        BOX(f"{ROOT}/Grass_N", ((gx0 + gx1) / 2.0, (gy1 + H) / 2.0, cz),
            (gx1 - gx0, H - gy1, th), M["grass"])

    # -------------------------------------------------------------------
    # 지상 보도 — 개구(x 0..7, 옹벽 외면 ±2.05)를 둘러싼 4박스로 분할.
    #   서(x<0)·동(x>7)은 전폭 y; 남(y<-y_out)·북(y>y_out)은 개구 x구간만.
    #   보도 절단면이 옹벽 외면(±y_out)에 정확히 접함 → Z-파이팅 없음.
    # -------------------------------------------------------------------
    def build_sidewalk(M):
        w = PARAMS["walk"]
        p = PARAMS["pit"]
        wl = PARAMS["wall"]
        top, th = w["z_top"], w["thick"]
        cz = top - th / 2.0
        y_out = p["y1"] + wl["thick"]        # 옹벽 외면 = 2.05 (보도 절단 위치)
        # 서: x_w..pit.x0 전폭
        BOX(f"{ROOT}/Walk_W",
            ((w["x_w"] + p["x0"]) / 2.0, (w["y_s"] + w["y_n"]) / 2.0, cz),
            (p["x0"] - w["x_w"], w["y_n"] - w["y_s"], th),
            M["sidewalk"], col=True)
        # 동: pit.x1..x_e 전폭.  v4-D1: 도로가 들어가면 도로 폭(연석 바깥면
        #   walk_a..walk_b)만큼 잘라 두 조각으로. 드레싱 OFF면 종전대로 1매
        #   (어느 경우에도 보행면 구멍 없음 — 토글 무결성).
        rd = PARAMS["road"]
        if cfg["cue_scene_dressing"]:
            spans = [("E1", p["x1"], rd["walk_a"]),
                     ("E2", rd["walk_b"], w["x_e"])]
        else:
            spans = [("E", p["x1"], w["x_e"])]
        for tag, xa, xb in spans:
            BOX(f"{ROOT}/Walk_{tag}",
                ((xa + xb) / 2.0, (w["y_s"] + w["y_n"]) / 2.0, cz),
                (xb - xa, w["y_n"] - w["y_s"], th),
                M["sidewalk"], col=True)
        # 남: 개구 x구간, y_s..-y_out
        BOX(f"{ROOT}/Walk_S",
            ((p["x0"] + p["x1"]) / 2.0, (w["y_s"] - y_out) / 2.0, cz),
            (p["x1"] - p["x0"], (-y_out) - w["y_s"], th),
            M["sidewalk"], col=True)
        # 북: 개구 x구간, +y_out..y_n
        BOX(f"{ROOT}/Walk_N",
            ((p["x0"] + p["x1"]) / 2.0, (y_out + w["y_n"]) / 2.0, cz),
            (p["x1"] - p["x0"], w["y_n"] - y_out, th),
            M["sidewalk"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 개구를 메워 전체를 z=0 평지로 통일.
        v4-D1: 도로가 켜져 있으면 도로 폭만큼 비워 노면이 매몰되지 않게 한다."""
        w = PARAMS["walk"]
        rd = PARAMS["road"]
        if cfg["cue_scene_dressing"]:
            spans = [("A", w["x_w"], rd["walk_a"]),
                     ("B", rd["walk_b"], w["x_e"])]
        else:
            spans = [("", w["x_w"], w["x_e"])]
        for tag, xa, xb in spans:
            BOX(f"{ROOT}/FlatWalk{tag}",
                ((xa + xb) / 2.0, (w["y_s"] + w["y_n"]) / 2.0,
                 w["z_top"] - w["thick"] / 2.0),
                (xb - xa, w["y_n"] - w["y_s"], w["thick"]),
                M["sidewalk"], col=True)

    # -------------------------------------------------------------------
    # 계단 + 랜딩 (재질: cue_material_break)
    # -------------------------------------------------------------------
    def build_stairs(stair_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)
        la = PARAMS["landing"]
        st = PARAMS["stairs"]
        BOX(f"{ROOT}/Landing",
            ((la["x0"] + la["x1"]) / 2.0, (st["y0"] + st["y1"]) / 2.0,
             (la["z_top"] + la["base_z"]) / 2.0),
            (la["x1"] - la["x0"], st["y1"] - st["y0"],
             la["z_top"] - la["base_z"]),
            stair_mtl, col=True)

    # -------------------------------------------------------------------
    # 옹벽 — 양측(남·북) + 후면 인방. 내면 ±1.75 (계단 폭 접), 파라펫 +0.15.
    # -------------------------------------------------------------------
    def build_walls(M):
        p = PARAMS["pit"]
        wl = PARAMS["wall"]
        tn = PARAMS["tunnel"]
        y_out = wl["y_in"] + wl["thick"]          # 2.05
        y_ctr = (wl["y_in"] + y_out) / 2.0        # 1.9
        top = wl["parapet_top"]                   # 0.15
        bot = wl["base_z"]                        # -3.5
        cz = (top + bot) / 2.0
        hz = top - bot
        Lx = p["x1"] - p["x0"]
        # 양측 옹벽 (남 y=-1.9 / 북 y=+1.9), x 0..7
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Wall_{tag}",
                ((p["x0"] + p["x1"]) / 2.0, sgn * y_ctr, cz),
                (Lx, wl["thick"], hz), M["concrete_wall"], col=True)
        # 후면 옹벽: 터널 개구(z -3.2..-0.9) 위 인방만 잔존 (z -0.9..0.15)
        lintel_bot = tn["floor_z"] + tn["open_h"]  # -0.9
        lintel_top = tn["lintel_top"]              # 0.15
        BOX(f"{ROOT}/Wall_RearLintel",
            (tn["x0"] + wl["thick"] / 2.0, 0.0,
             (lintel_bot + lintel_top) / 2.0),
            (wl["thick"], 2.0 * y_out, lintel_top - lintel_bot),
            M["concrete_wall"], col=True)

    # -------------------------------------------------------------------
    # 터널 — 깊이 4m 내부 박스(바닥/천장/양벽/막다른 후벽), 짙은 틴트.
    # -------------------------------------------------------------------
    def build_tunnel(M):
        tn = PARAMS["tunnel"]
        wl = PARAMS["wall"]
        p = PARAMS["pit"]
        x0 = tn["x0"]
        x1 = tn["x0"] + tn["depth"]               # 11.0
        cx = (x0 + x1) / 2.0
        floor_z = tn["floor_z"]                    # -3.2
        ceil_z = floor_z + tn["open_h"]            # -0.9
        y_in = wl["y_in"]                          # 1.75
        y_out = y_in + wl["thick"]                 # 2.05
        Wy = 2.0 * y_in                            # 3.5 (개구 폭)
        thk = wl["thick"]                          # 0.3
        # 바닥 (상면 floor_z)
        BOX(f"{ROOT}/Tunnel/Floor", (cx, 0.0, floor_z - thk / 2.0),
            (tn["depth"], Wy, thk), M["tunnel"], col=True)
        # 천장 (하면 ceil_z). x0+thk 부터 시작 — 후면 인방(lintel, x0..x0+thk)의
        #   하면(z=ceil_z 하향)과 천장 하면이 겹쳐 Z-파이팅 나는 것 회피.
        ce_x0 = x0 + thk
        BOX(f"{ROOT}/Tunnel/Ceil",
            ((ce_x0 + x1) / 2.0, 0.0, ceil_z + thk / 2.0),
            (x1 - ce_x0, Wy, thk), M["tunnel"], col=True)
        # 양벽 (내면 ±y_in), z floor..ceil
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Tunnel/Wall_{tag}",
                (cx, sgn * (y_in + thk / 2.0), (floor_z + ceil_z) / 2.0),
                (tn["depth"], thk, ceil_z - floor_z), M["tunnel"], col=True)
        # 막다른 후벽 (x1)
        BOX(f"{ROOT}/Tunnel/Back",
            (x1 + thk / 2.0, 0.0, (floor_z + ceil_z) / 2.0),
            (thk, 2.0 * y_out, ceil_z - floor_z), M["tunnel"], col=True)

    # -------------------------------------------------------------------
    # [v5 공통 레이어] 한글 사인 (cue_sign)
    # -------------------------------------------------------------------
    def build_signs():
        """sc.build_sign 배치. [v5.2 사용자] 임의 경고 팻말 제거 — 출구 표지만.
        좌표·카메라 검산은 PARAMS['signs'] 주석. 위험 기하 불변."""
        back = sc.make_pbr(stage, f"{ROOT}/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h, ph in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"{ROOT}/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, pole_h=ph, back_mtl=back)

    # -------------------------------------------------------------------
    # 단서 (cue) — nosing / tactile / railing
    # -------------------------------------------------------------------
    def build_cues(M, stair_mtl):
        st = PARAMS["stairs"]

        # ── cue_nosing: 전 단 황색 논슬립 띠 ──
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"],
                color=ns["color"], width=ns["width"], proud=ns["proud"],
                z_top=st["z_top"])

        # ── cue_tactile: 상단 경고띠(x -0.3..0) + 하부 랜딩 ──
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            la = PARAMS["landing"]
            # 상단: 개구 앞 0.3m 경고띠 (개구 폭)
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["tactile"],
                             z=0.0, proud=tc["proud"])
            # 하부 랜딩: 포탈 진입 앞 경고띠
            sc.build_tactile(stage, f"{ROOT}/Tactile_Land",
                             la["x1"] - tc["land_depth"], la["x1"],
                             st["y0"], st["y1"], M["tactile"],
                             z=la["z_top"], proud=tc["proud"])

        # ── cue_railing: 계단 양측 벽부착 경사 레일 2선 + 피트 둘레 3면 난간 ──
        if cfg["cue_railing"]:
            sr = PARAMS["stair_rail"]

            # 계단식 지면 콜백 (x<0 → 0.0, 계단 구간 → 단 상면)
            def stair_ground(x):
                # x<=0(접근/x_top)은 지상 0.0 → build_railing_line 기준
                # ground_fn(x_top)+rail_h 가 0.9 로 정상. 첫 단(-0.16)은 x>0에서.
                if x <= 1e-9:
                    return 0.0
                return -st["riser"] * min(max(int(x / st["tread"]) + 1, 1),
                                          st["nsteps"])

            run = st["tread"] * st["nsteps"]          # 6.4
            drop = st["riser"] * st["nsteps"]         # 3.2
            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                sc.build_railing_line(
                    stage, f"{ROOT}/StairRail_{tag}", sgn * sr["y"],
                    sr["x_start"], st["x0"], run, drop, stair_ground,
                    M["rail"], rail_h=sr["rail_h"], post_r=sr["post_r"],
                    spacing=sr["spacing"], rail_r=sr["rail_r"],
                    rail_mid_r=sr["rail_mid_r"],
                    rail_mid_drop=sr["rail_mid_drop"])

            # 피트 지상 둘레 난간 3면 (파라펫 위 수평 레일 — add_cylinder 직접)
            pr = PARAMS["perim_rail"]
            base_z = pr["parapet_top"]                # 0.15
            top_z = base_z + pr["rail_h"]             # 1.05
            mid_z = base_z + pr["mid_h"]              # 0.60

            def hrail(prefix, along, const_c, a0, a1):
                """수평 난간 1면: 상단+중간 레일 + 포스트. along='x'|'y'."""
                mid_c = (a0 + a1) / 2.0
                length = a1 - a0
                if along == "x":
                    CYL(f"{prefix}/Top", (mid_c, const_c, top_z),
                        pr["rail_r"], length, M["rail"], rotY=90.0)
                    CYL(f"{prefix}/Mid", (mid_c, const_c, mid_z),
                        pr["rail_mid_r"], length, M["rail"], rotY=90.0)
                else:                                  # along Y (rotX=90)
                    CYL(f"{prefix}/Top", (const_c, mid_c, top_z),
                        pr["rail_r"], length, M["rail"], rotX=90.0)
                    CYL(f"{prefix}/Mid", (const_c, mid_c, mid_z),
                        pr["rail_mid_r"], length, M["rail"], rotX=90.0)
                # 포스트: 파라펫 상면(base_z)에서 상단 레일까지
                ph = top_z - base_z
                n = 0
                a = a0 + pr["spacing"] / 2.0
                while a <= a1 - pr["spacing"] / 2.0 + 1e-6:
                    if along == "x":
                        pxy = (a, const_c, base_z + ph / 2.0)
                    else:
                        pxy = (const_c, a, base_z + ph / 2.0)
                    CYL(f"{prefix}/Post_{n}", pxy, pr["post_r"], ph, M["rail"])
                    a += pr["spacing"]
                    n += 1

            # 남·북 가장자리 (x 0..7), 후면 (x=7.15, y -1.9..1.9)
            hrail(f"{ROOT}/PerimRail_S", "x", -pr["y"], pr["x0"], pr["x1"])
            hrail(f"{ROOT}/PerimRail_N", "x", pr["y"], pr["x0"], pr["x1"])
            hrail(f"{ROOT}/PerimRail_R", "y", pr["x_rear"], -pr["y"], pr["y"])

    # -------------------------------------------------------------------
    # 드레싱 — 벽돌 건물 1동 + 원경 비스타 + 생울타리 + 가로등
    # -------------------------------------------------------------------
    def build_road(M):
        """v4-D1/D2 [최우선]: 터널 위를 가로지르는 아스팔트 도로 + 연석 + 차선.

        좌표 근거 — 터널은 x 7..11 (천장 상면 −0.6), 후벽 x 11..11.3.
        노면 x 8..13 이 그 위를 덮으므로 '도로 밑을 지나는 지하도' 서사가 성립,
        막다른 후벽(x 11.3)이 문제되지 않는다. 노면 상면 −0.02 는 잔디 대지
        상면 −0.03 보다 1 cm 위 → 매몰 없음. 연석 상면 +0.10 (보도 0.0 대비 10 cm).
        """
        rd = PARAMS["road"]
        cy = (rd["y0"] + rd["y1"]) / 2.0
        Ly = rd["y1"] - rd["y0"]
        BOX(f"{ROOT}/Road/Surface",
            ((rd["x0"] + rd["x1"]) / 2.0, cy, rd["top"] - rd["thick"] / 2.0),
            (rd["x1"] - rd["x0"], Ly, rd["thick"]), M["asphalt"], col=True)
        # 연석 2줄 (보도 절단면 walk_a/walk_b ↔ 노면 사이)
        for tag, xa, xb in (("W", rd["walk_a"], rd["x0"]),
                            ("E", rd["x1"], rd["walk_b"])):
            BOX(f"{ROOT}/Road/Curb_{tag}",
                ((xa + xb) / 2.0, cy,
                 (rd["curb_top"] + rd["curb_base"]) / 2.0),
                (xb - xa, Ly, rd["curb_top"] - rd["curb_base"]),
                M["granite_dark"], col=True)
        # 중앙 파선 (노면에 8 mm 돌출)
        for k in range(rd["dash_n"]):
            yd = rd["dash_y0"] + rd["dash_step"] * k
            BOX(f"{ROOT}/Road/Dash_{k}",
                (rd["lane_x"], yd, rd["top"] - 0.002),
                (rd["lane_w"], rd["dash_len"], 0.02), M["lane"])

    def build_dressing(M):
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        # v4-D1: 도로 (지하도의 존재 이유)
        build_road(M)
        # 생울타리 — v4-B2: 4세그 높이·y 변주로 '검은 직육면체' 해소
        h = PARAMS["hedge"]
        seg_w = (h["x1"] - h["x0"]) / float(h["nseg"])
        for i in range(h["nseg"]):
            xa = h["x0"] + seg_w * i
            yc = h["y"] + h["y_var"][i % len(h["y_var"])]
            hh = h["h"] + h["h_var"][i % len(h["h_var"])]
            sc.build_hedge(stage, f"{ROOT}/Hedge_{i}", xa, yc - h["half"],
                           xa + seg_w + 0.05, yc + h["half"], hh,
                           mtl=M["hedge"], base_z=0.0)
        # v4-D5 계단 상단 캐노피 (지하철 출입구 실루엣)
        cp = PARAMS["canopy"]
        sc.build_canopy(stage, f"{ROOT}/EntryCanopy", cp["x0"], cp["x1"],
                        cp["y0"], cp["y1"], cp["z_roof"], cp["post_r"],
                        M["parapet"], M["pole"], roof_t=cp["roof_t"],
                        base_z=cp["base_z"])
        # v4-D4 지하도 입구 사인 (판 + 백색 픽토그램면 + 기둥 2)
        sg = PARAMS["sign"]
        zc = (sg["z0"] + sg["z1"]) / 2.0
        BOX(f"{ROOT}/Sign/Panel", (sg["x"], (sg["y0"] + sg["y1"]) / 2.0, zc),
            (sg["thick"], sg["y1"] - sg["y0"], sg["z1"] - sg["z0"]), M["sign"])
        BOX(f"{ROOT}/Sign/Face",
            (sg["x"] - sg["thick"] / 2.0 - 0.006,
             (sg["y0"] + sg["y1"]) / 2.0, zc),
            (0.012, (sg["y1"] - sg["y0"]) - 0.5,
             (sg["z1"] - sg["z0"]) - 0.22), M["sign_face"])
        for tag, py in (("A", sg["y0"] + 0.1), ("B", sg["y1"] - 0.1)):
            CYL(f"{ROOT}/Sign/Post_{tag}", (sg["x"], py, sg["post_h"] / 2.0),
                sg["post_r"], sg["post_h"], M["pole"], col=True)
        # v4-D6 노선도/안내 게시판 — [v5.1] 삭제(기능·위치 중복,
        #   PARAMS["board"] 항목 자체를 제거했다). 진입부 안내는 D4 사인 1매.
        # v4-D7 볼라드
        for k, (bx, by) in enumerate(PARAMS["bollards"]):
            sc.build_bollard(stage, f"{ROOT}/Bollard_{k}", bx, by, 0.0,
                             mtl=M["rail"])
        # v4-D8 벤치 2 + 쓰레기통 2
        for k, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{k}", bx, by, 0.0,
                           M["seat_wood"], yaw=yaw)
        bn = PARAMS["bin_spec"]
        for k, (bx, by) in enumerate(PARAMS["bins"]):
            CYL(f"{ROOT}/Bin_{k}/Body", (bx, by, bn["h"] / 2.0),
                bn["r"], bn["h"], M["pole"], col=True)
            CYL(f"{ROOT}/Bin_{k}/Rim", (bx, by, bn["h"] + 0.02),
                bn["r"] * 1.1, 0.04, M["rail"])
        # v4-D11 화단 2 (나무 포함)
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for k, (px, py) in enumerate(PARAMS["planters"]):
            sc.build_planter(stage, f"{ROOT}/Planter_{k}", px, py, 0.0,
                             M["granite_dark"], M["grass"],
                             tree_mtls=tree_mtls)
        # v4-D9 가로등 (1→4본)
        sl = PARAMS["streetlight"]
        for k, (x, y, bz) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{k}"
            CYL(f"{base}/Pole", (x, y, bz + sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["pole"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                ax = x + sgn * sl["arm_len"] / 2.0
                CYL(f"{base}/Arm_{tag}", (ax, y, bz + sl["pole_h"] - 0.1),
                    sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                hx = x + sgn * sl["arm_len"]
                BOX(f"{base}/Head_{tag}", (hx, y, bz + sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        # v4-D10 터널 내부 형광등 3 (하부 암부에 정보 부여)
        if cfg["hazard_stairs"]:
            from pxr import UsdLux, Gf
            tl = PARAMS["tunnel_lights"]
            for k, (lx, ly, lz) in enumerate(tl["pos"]):
                lt = UsdLux.SphereLight.Define(stage, f"{ROOT}/TunnelLight_{k}")
                lt.CreateRadiusAttr(float(tl["radius"]))
                lt.CreateIntensityAttr(float(tl["intensity"]))
                lt.CreateColorAttr(Gf.Vec3f(*[float(c) for c in tl["color"]]))
                UsdGeom.Xformable(lt.GetPrim()).AddTranslateOp().Set(
                    Gf.Vec3d(float(lx), float(ly), float(lz)))

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["concrete_floor"] if cfg["cue_material_break"] else M["sidewalk"]

    build_ground(M)
    if cfg["hazard_stairs"]:
        build_sidewalk(M)
        build_stairs(stair_mtl)
        build_walls(M)
        build_tunnel(M)
        build_cues(M, stair_mtl)
    else:
        build_flat_fill(M)          # 대조군: z=0 평지 통일 (단서는 위 피트 없음)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if cfg.get("cue_sign") and cfg["hazard_stairs"]:
        build_signs()               # [v5 공통 레이어] (Exit 은 터널 안 → 피트 필요)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── 카메라 + 렌더 모드 ──
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

    # ===================================================================
    # 자동 캡처 모드 (headless 검증 파이프라인 — noon 전용)
    # ===================================================================
    if capture_mode:
        out_dir = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, build_views(), out_dir,
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene02_{ts}.png")
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
