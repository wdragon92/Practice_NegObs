# -*- coding: utf-8 -*-
"""
scene11_footbridge_stairs.py — NegObs 인공씬 11호: 보도육교(과선교) 철제 계단
(Isaac Sim 4.5) · v5 신규(구 scene11_grating_fireescape → scenes/archive_v3/)

유형    : R6 왕복 6차로 위 보도육교 철제 계단 (개방 라이저·그레이팅 투과 축 계승)
사양서  : Docs/briefs/multi_scene_brief_v5.md §R6 + 공통 레이어 절
공통    : scene_common.py (build_open_riser_stairs / build_rot_group /
          build_railing_line / build_canopy / build_sign / build_tactile)
세계관  : scene06_overpass_spiral.py 와 육교 규약 공유
          (차도 아스팔트 0.045 · 연석 0.15 · 보도 paving_interlock · 가로등)

────────────────────────────────────────────────────────────────────────────
위험 본질 (= 규정 미달의 현실)
  왕복 6차로를 건너는 보도육교. 상판(z=+5.5)에서 동측 철제 계단 2련(22단×2,
  중간참)이 보도로 내려간다. 디딤판은 그레이팅(슬릿 3) — 라이저가 없어
  **아래가 그대로 투시**되고 정오광에서 슬릿 그림자가 노면에 스트라이프를
  깔아 단코 경계를 지운다.
  주 결함 — **동측 중간참(z=2.75)의 외측 난간 하부에 킥플레이트가 없다.**
  로봇 눈높이(h0.3)에서는 난간 가로대가 시야 위로 지나가고 하부 0~0.35 m 대역이
  통째로 열려 있어, 참 밖 2.755 m 낙차가 "바닥이 이어진 것"으로 읽힌다.
  서측 중간참은 같은 기하에 킥플레이트가 **있어** 규정 준수 대조군이 된다
  (동일 기하 × 설비 유무 = 단서 학습용 대비쌍).
  셋째 — 상판·계단 상부의 측면은 차도면(−0.15)까지 5.65 m 낙차이며, 방음
  패널이 시야를 막아 낙차의 깊이 단서(바닥 텍스처)가 소거된다.

GT 낙차 불변 원칙: cue_* 토글은 난간·패널·킥플레이트·점자·사인 프림만 켜고
  끈다. 상판·참·계단(riser 0.125 / tread 0.32 / 22단×2)의 트랜스폼은 불변.

────────────────────────────────────────────────────────────────────────────
보행 연속성 자가 검증표 (서측 보도 → 상행 → 상판 → 하행 → 동측 보도)

  #  구간                     좌표(월드, m)                          단차
  ─  ───────────────────────  ─────────────────────────────────────  ──────
  1  서측 보도 접근           (x −45…−30.88, y ±0.9, z −0.005)       —
  2  서측 계단 B 22단 상행    x −30.88…−23.84, z 0.000 → 2.750       0.125/단
  3  서측 중간참              x −23.84…−22.04, z 2.750 (킥플레이트 有) 0.000
  4  서측 계단 A 22단 상행    x −22.04…−15.00, z 2.750 → 5.500       0.125/단
  5  서측 상부 참             x −15.00…−13.20, z 5.500               0.000
  6  상판 종주                x −13.20…13.20, y −1.2…1.2, z 5.500    —
     (차도 x −10.5…10.5 위 유효고 = 5.10 −(−0.15) = 5.25 m)
  7  동측 상부 참             x 13.20…15.00, z 5.500                 0.000
  8  동측 계단 A 22단 하행    x 15.00…22.04, z 5.500 → 2.750         0.125/단
  9  동측 중간참              x 22.04…23.84, z 2.750 (킥플레이트 無)  0.000
 10  동측 계단 B 22단 하행    x 23.84…30.88, z 2.750 → 0.000         0.125/단
 11  동측 보도 탈출           (x 30.88…45, y ±0.9, z −0.005)         0.005

  총 상승 = 총 하강 = 5.500 m (= 44 × 0.125). 접속부 단차 ≤ 0.005 m.
  경사 = atan(0.125/0.32) = 21.34° — 완경사 육교 계단(2R+T = 0.570).

────────────────────────────────────────────────────────────────────────────
개구 4박스 규약: 지면을 관통하는 공동이 없다(상판·계단 전부 지상 구조물).
  보도/차도 슬래브는 연속 박스로 깔아도 §A-3 위배가 아니다.

카메라 축 주석: 브리프 R6 은 "보도 접근 그리드"를 지시했으나, grid_views 는
  **낙차 경계를 프레임 정면에 두는** 규약(eye_x = 원점 −d)이라 지상 접근으로
  잡으면 로봇 정면이 상승 계단이 되어 낙차 GT 가 프레임에서 사라진다.
  → 그리드는 **상판 종주축(+X, 원점 = 동측 계단 낙차 시작 x=15.0, z 5.5)** 으로
  잡고, 브리프가 요구한 보도 접근은 미장센 `sidewalk_approach` 로 제공한다.
  (판정 1순위 = 로봇 h0.3 에서 위험 은닉이 성립하는가 — 브리프 v5 공통 레이어 4)

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene11_footbridge_stairs.py

자동 캡처 (headless):  NEGOBS_CAPTURE=1 python scene11_footbridge_stairs.py
스모크(부팅 전 조기종료): NEGOBS_SMOKE=1 python scene11_footbridge_stairs.py

좌표계: Z-up, m. 보행축·상판축 +X · 차도축 +Y(왕복 6차로) · 보도 상면 −0.005.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 상판·계단 제거(평탄 보도 대조군)
    "cue_railing":        True,   # 계단·참 파이프 난간 + 상판 방음 패널
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)   # 도시 관행 씬 — 승강부 점자띠 기본 ON(브리프 v5)
    "cue_material_break": True,   # 연석·차선 도색·계단 하부 노면 밴드
    "cue_nosing":         True,   # 그레이팅 단코 황색 논슬립 띠(육교 관행)
    "cue_sign":           True,   # 한글 사인 sign_info(육교 안내) — 공통 레이어
    "cue_scene_dressing": True,   # 차도·버스 쉘터·가로등·가로수·원경 건물
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- 철제 계단 2련 (브리프 R6: 폭 1.8, 22단×2, 중간참, 그레이팅) ---
    #   riser 0.125 = 5.5 / 44 (상판고를 44단으로 균등 분할 → 접속 단차 0).
    #   tread 0.32 → 련당 run 7.04, 경사 21.34°, 2R+T = 0.570.
    #   slits 3 : 디딤판을 4조각으로 쪼개 0.02 m 틈 3개 — 하부 투시·격자 그림자.
    stair=dict(riser=0.125, tread=0.32, n=22, y0=-0.90, y1=0.90,
               tread_t=0.045, gap=0.025, slits=3),
    # --- 동측(주 위험측) 계단 배치 ---
    #   상부 참 → 계단 A → 중간참 → 계단 B → 보도
    #   참(상부·중간)은 상판과 같은 두께(deck.thick 0.40)의 강상판 박스로 만든다.
    #   kickplate=False 가 이 씬의 주 결함(브리프 R6).
    east=dict(pad_x0=13.20, pad_x1=15.00, a_x0=15.00,
              mid_len=1.80, z_top=5.50, pad_y0=-1.20, pad_y1=1.20,
              kick_h=0.14, kickplate=False),
    # --- 서측(규정 준수 대조군) — rot_group 180° 로 좌우 반전 ---
    #   pivot (−7.5, 0) · 180° : 로컬 (x,y) → 월드 (−15 − x, −y).
    #   로컬 x 0 → 월드 −15.00(상부 참 서단), 로컬 x 15.88 → 월드 −30.88(하단).
    west=dict(pivot=(-7.5, 0.0), rot=180.0, kickplate=True),
    # --- 육교 상판 (폭 2.4, x축 종주) ---
    deck=dict(x0=-13.20, x1=13.20, y0=-1.20, y1=1.20, z_top=5.50, thick=0.40,
              panel_h=1.80, panel_t=0.07, rail_z=1.95, rail_r=0.035),
    #   [v6 판정 ⑤] 구 방음 난간 = **무분절 대형 판재 1매**(길이 26.4 m).
    #   지주·조인트·상단 캡·투시 구간이 전무해 상판이 콘크리트 벙커 복도로
    #   읽혔고, 그림자면이 그리드 컷의 30~45 %를 순흑으로 만들었다(④).
    #   → 지주 2.2 m 분절 + **방음판/개방 베이 교대**. make_pbr 에 투명도
    #   입력이 없으므로(“투명 폴리카보네이트”를 그대로 만들 수 없다) 투시
    #   구간은 **세로 살 개방 베이**로 구현한다 — 투광·투시 목적은 동일하고
    #   국내 육교의 실제 관행(부분 방음판)에도 부합한다.
    #   post_h 1.98 = 상단 가로대 중심 rail_z 1.95 + 파이프 반경 0.035 → 지주가
    #   가로대를 **받치는** 높이(구 구성처럼 레일이 떠 보이지 않게).
    rail_bay=dict(post_t=0.10, post_h=1.98, n_bay=12, joint=0.05,
                  kick_h=0.16, cap_h=0.07, cap_over=0.03,
                  baluster_r=0.018, n_baluster=6),
    #   지지 기둥 — 연석(x ±10.5…11.1) 바깥 보도에 착지. 상판 저면까지.
    deck_posts=dict(xs=(-11.80, 11.80), y=0.0, r=0.40, z_bot=-0.30,
                    cap_sx=1.0, cap_sy=2.8, cap_h=0.36),
    # --- 차도 (왕복 6차로, y축) ---
    road=dict(x0=-10.50, x1=10.50, y0=-60.0, y1=60.0, z_top=-0.15, thick=0.60),
    #   차선: 중앙 황색 복선 + 편도 3차로 구분 백색 파선 2세트 (= "차선 3" 계열)
    lane=dict(center_xs=(-0.20, 0.20), dash_xs=(-7.10, -3.60, 3.60, 7.10),
              w=0.15, z=-0.142, t=0.02, seg=3.0, gap=5.0, y0=-58.0, y1=58.0),
    # --- 보도(인터로킹) + 연석 ---
    #   [v6 판정 C-2] 구 폭 34.5 m 보도는 개방감이 아니라 **공터**였고 잔디판이
    #   하늘과 직선으로 맞닿았다. 보도를 29.5 m(계단 하단 30.88 + 사인 31.6 +
    #   벤치 36 을 담는 최소치)로 줄이고 바깥을 식재대 + 가로수 열 + 원경 수목
    #   띠로 경계한다.
    walk=dict(y0=-60.0, y1=60.0, xw0=-40.0, xw1=-10.50, xe0=10.50, xe1=40.0,
              z_top=-0.005, thick=0.50),
    curb=dict(w=0.60, z_top=0.0, thick=0.40),
    # --- 식재대(보도 바깥 경계) : 화강암 경계석 + 지피 상면 ---
    verge=dict(w=2.40, curb_t=0.20, curb_top=0.14, soil_top=0.10,
               y0=-60.0, y1=60.0),
    # --- 대지 (지평 폐쇄) : 차도 상면(−0.15)보다 1 cm 낮게 ---
    ground=dict(x0=-150.0, x1=150.0, y0=-150.0, y1=150.0, z_top=-0.16,
                thick=1.40),
    # --- 난간 (cue_railing) ---
    #   rail_h 1.10 (육교 기준). 킥플레이트는 참에만 — 동측은 결손(위험).
    rail=dict(rail_h=1.10, post_r=0.026, rail_r=0.032, rail_mid_r=0.022,
              rail_mid_drop=0.52, spacing=1.00, y_inset=0.03),
    # --- 점자블록 (cue_tactile) : 승강부 4개소 ---
    tactile=dict(pad_len=0.40, low_len=0.40, proud=0.004),
    # --- 한글 사인 (cue_sign) : sign_info(육교 안내) 768×512 → w:h = 3:2 ---
    #   동측 계단 하단 진입부 + 서측 하단. 그리드 시선축(y=0)과 2.6 m 이격.
    #   [v6 판정 ④ — 원인 규명 완료] `sidewalk_approach`(eye 38,−5,0.9 →
    #   tgt 26,−0.4,3.2) 프레임 정중앙의 "정체불명 순흑 사각 패널"은 **부유
    #   결함이 아니라 이 사인의 뒷면**이다. 구 yaw 180° 는 패널 법선을 −X 로
    #   두므로, 동측 보도(+X)에서 계단으로 접근하는 시점에는 배킹판만 보인다.
    #   배킹 재질이 M["steel"](0.055,0.058,0.060)이라 순흑 사각형이 됐다.
    #   → ① 동측 사인 yaw 0(=+X 향, 접근자를 마주봄) / 서측 yaw 180 으로 반전
    #      ② 배킹을 알루미늄 회색(M["signback"], 0.44)으로 교체
    #      ③ 시선축(y=0)에서 2.6 m 이격은 유지(회랑 청소 규약).
    sign=dict(w=0.90, h=0.60, pole_h=2.40,
              spots=((31.60, -2.60, 0.0), (-31.60, 2.60, 180.0))),
    # --- 드레싱 ---
    dress=dict(
        # 버스 승차대 쉘터 1 (동측 보도) — 그리드 시선축 밖(y −9.6…−5.6)
        #   [v6 판정 ⑤] 구 구성은 지붕판 + 기둥 4 뿐이라 "카포트"로 읽혔다.
        #   실물 최소 구성 = 배면 유리벽 + **측벽 2** + 벤치 + **노선도 패널**.
        shelter=dict(x0=17.0, x1=23.0, y0=-9.60, y1=-5.60, z_roof=2.55,
                     post_r=0.08, bench_y=-8.6, side_t=0.05, side_h=2.20,
                     side_inset=0.9, route_w=0.90, route_h=1.10),
        bus_pole=(24.6, -7.60, 3.20),
        lamps=((16.0, -12.0), (16.0, 12.0), (-16.0, -12.0), (-16.0, 12.0)),
        # 가로수 열 — [v6 판정 C-2] 식재대(x ±41.2) 위 1열, 간격 7.5 m ±지터.
        #   보도–잔디 경계를 선으로 만든다. 계단 회랑(y −2.4…2.4)은 비운다.
        lamp=dict(pole_h=6.0, pole_r=0.10, arm_len=1.1, arm_r=0.055, head=0.32),
        trees=((41.2, -34.0), (41.2, -26.6), (41.2, -19.2), (41.2, -11.6),
               (41.2, 11.8), (41.2, 19.4), (41.2, 26.8), (41.2, 34.2),
               (-41.2, -34.2), (-41.2, -26.8), (-41.2, -19.4), (-41.2, -11.8),
               (-41.2, 11.6), (-41.2, 19.2), (-41.2, 26.6), (-41.2, 34.0),
               (14.0, -20.0), (14.0, 20.0), (26.0, -20.0), (26.0, 20.0),
               (-14.0, -20.0), (-14.0, 20.0), (-26.0, -20.0), (-26.0, 20.0)),
        # [v5.1 §3] 벤치는 가로수 앵커 옆(등간격 금지 · yaw 지터)
        benches=((38.6, -19.2, 86.0), (-38.6, 19.2, -94.0)),
        bollards=((12.6, -4.0), (12.6, 4.0), (-12.6, -4.0), (-12.6, 4.0)),
        # 계단 하부 노면 밴드(cue_material_break) — 그레이팅 그림자 대조면
        band=dict(x0=15.0, x1=31.5, y0=-1.40, y1=1.40, z=0.004, t=0.03),
    ),
    # [v6 판정 C-2/C-4] 원경 폐쇄 — 수목 실루엣 띠(원경 LOD, 능선형 블록 열)를
    #   보도 바깥에 깔아 잔디판이 하늘과 직접 만나지 않게 한다. 개체 나무 도열이
    #   아니므로 "롤리팝 반복"이 생기지 않는다. rows = (x0, x1, h).
    #   [v7 판정 ⑥-2] 구 구성(세그 7.5 m × 폭 4 m × 높이 4.4~4.8 의 **속 찬 박스**
    #   1개 + 그 위 작은 블롭 1개)은 상면이 평평한 연속 판이라 `midlanding`·
    #   `deck_walk` 배경에서 **도색 방음벽(초록 슬래브)** 으로 읽혔다.
    #   → ① 박스는 하부 임관(林床)만 담당하게 h·base_frac(0.36)로 낮추고
    #      ② 상단은 세그당 blobs(3)개의 겹치는 수관 블롭이 만든다(높이 0.72~1.16×
    #         지터 → 스카이라인 톱니) ③ 세그를 5.0 m 로 잘게 쪼개고 x 지터 ±1.7 로
    #         전후 깊이를 준다 ④ 틴트는 근경 잎(진초록)이 아니라 **대기원근 반영
    #         저채도 회록 3종**(leaf_far_*) 을 순환시켜 단색 판 인상을 지운다.
    treeband=dict(rows=((44.5, 48.5, 4.8), (-48.5, -44.5, 4.4)),
                  y0=-58.0, y1=58.0, seg=5.0, jitter=1.2,
                  base_frac=0.36, blobs=3, x_jit=1.2),
    buildings=dict(
        E=dict(x0=50.0, x1=64.0, y0=-52.0, y1=52.0, h=26.0, floors=8,
               axis="x", facade_x=50.0, face_dir=-1.0, base_z=-0.16),
        W=dict(x0=-64.0, x1=-50.0, y0=-52.0, y1=52.0, h=23.0, floors=7,
               axis="x", facade_x=-50.0, face_dir=1.0, base_z=-0.16),
        NE=dict(x0=16.0, x1=42.0, y0=34.0, y1=48.0, h=19.0, floors=6,
                axis="y", facade_y=34.0, face_dir=-1.0, base_z=-0.16),
        NW=dict(x0=-42.0, x1=-18.0, y0=38.0, y1=50.0, h=14.0, floors=5,
                axis="y", facade_y=38.0, face_dir=-1.0, base_z=-0.16),
        SW=dict(x0=-42.0, x1=-16.0, y0=-48.0, y1=-34.0, h=21.0, floors=7,
                axis="y", facade_y=-34.0, face_dir=1.0, base_z=-0.16),
        SE=dict(x0=18.0, x1=42.0, y0=-50.0, y1=-38.0, h=15.5, floors=5,
                axis="y", facade_y=-38.0, face_dir=1.0, base_z=-0.16),
    ),
    #   [v6 판정 ⑤] 창 데칼이 **정확한 격자로 반복**돼(deck_walk 배경) 타일링
    #   티가 가장 심한 컷이 됐다 → 동별 창 규격·열 간격을 분리해 리듬을 깬다.
    window=dict(w=1.3, h=1.7, inset=0.15, col_step=2.8, margin=2.5),
    window_by=dict(
        E=dict(w=1.5, h=1.55, inset=0.15, col_step=3.3, margin=3.4),
        W=dict(w=1.15, h=1.85, inset=0.15, col_step=2.5, margin=2.0),
        NE=dict(w=1.35, h=1.5, inset=0.15, col_step=3.0, margin=2.6),
        NW=dict(w=1.6, h=1.35, inset=0.15, col_step=3.5, margin=3.0),
        SW=dict(w=1.2, h=1.8, inset=0.15, col_step=2.4, margin=1.9),
        SE=dict(w=1.45, h=1.6, inset=0.15, col_step=3.1, margin=2.8),
    ),

    # --- 재질 (sRGB 감마: 어두운 상수색은 0.02~0.06 대역 — §A-1) ---
    material=dict(
        # [v7 판정 ⑥-1 — 원인 규명] W-1 의 `metal_rust` UV 1.0 → 0.25 축소는
        #   **실제로 반영됐다**(make_pbr 6번째 위치인자 scale_m 로 전달 →
        #   texture_scale = 1/scale_m = 4.0; OmniPBR "Texture Tiling" 이므로
        #   값이 클수록 반복↑ = 무늬 축소. `역작동` 아님. v6↔v7 midlanding
        #   렌더의 수평 자기상관 반폭도 20 px → 10 px 로 실측 축소됐다).
        #   그런데 판정이 반복된 이유는 **스케일이 아니라 대비·색상**이었다:
        #     · metal_rust_diff 휘도 p5 29 / p95 130(sRGB) = 선형 18:1 대비.
        #       타일을 줄여도 얼룩의 명암비는 그대로다(실측 std 33.2 → 34.7).
        #     · 채널 등화 틴트 (0.61,0.80,1.00) 은 **평균만** 중성화한다.
        #       화소 단위로는 어두운 녹 화소를 적갈(R 31.7 : B 11.0), 밝은
        #       소지 화소를 청백(R 80.5 : B 127.0)으로 **더 갈라놓아**
        #       "백·갈 고대비 얼룩"을 오히려 강화했다.
        #   → 조치: ① 타일 0.25 → 0.55 m (1 m² 당 3.3 타일 = 판정 목표 "얼룩
        #      3~5개/m²" 대역) ② OmniPBR albedo_add/brightness 로 알베도
        #      레인지를 선형 0.045~0.090(2.0:1)으로 압축 ③ albedo_desaturation
        #      으로 녹/소지 색분리 제거 ④ 틴트는 중성 냉회색만 담당.
        #      법선·거칠기 텍스처는 그대로 두어 "무텍스처 스티로폼 판"(§4)은 회피.
        #   [v6] concrete_floor(107,93,77 난색 갈토)를 쓰던 상판·교각이 "녹슨 철"로
        #   읽혔다(under_grating) → 줄눈·타이홀이 있는 concrete_wall + 등화 틴트
        #   (0.72,0.77,0.92) = 평균 102 ≈ 알베도 0.40 의 중성 콘크리트로 교체.
        scale=dict(paving_interlock=1.0, metal_rust=0.55, concrete_wall=2.0,
                   granite_dark=1.0, brick_red=2.0, grass=4.0, tactile=0.3),
        asphalt_color=(0.045, 0.045, 0.050), asphalt_rough=0.92,
        metal_tint=(0.90, 0.94, 1.00),          # 도장 강재 톤(중성 냉회색)
        # [v7 판정 ⑥-1] OmniPBR 알베도 보정 — 텍스처 룩업에
        #   diffuse = tex*brightness + add 를 걸어 대비를 압축하고(선형
        #   p5 0.0116/p95 0.216 → 0.045/0.090), desaturation 으로 색분리를 지운다.
        #   결과 예상: 선형 중앙값 0.051 ≈ sRGB 63 = 도장 강재 다크그레이.
        metal_albedo=dict(brightness=0.220, add=0.0425, desaturation=0.55),
        concrete_tint=(0.72, 0.77, 0.92),
        parapet_tint=(0.78, 0.83, 0.99),
        soil_tint=(0.42, 0.44, 0.34),
        line_white=(0.55, 0.55, 0.52), line_yellow=(0.52, 0.40, 0.06),
        band_color=(0.070, 0.070, 0.075), band_rough=0.88,
        rail_color=(0.050, 0.098, 0.108), rail_rough=0.55, rail_metallic=0.35,
        steel_color=(0.055, 0.058, 0.060), steel_rough=0.50,
        steel_metallic=0.45,
        # [v6 판정 C-3 계열] panel_rough 0.18 = 준경면 → 하늘 반사로 대면적
        #   백판처럼 보인다. 도장 강판 실물 광택(0.48)으로 낮춘다.
        panel_color=(0.075, 0.095, 0.105), panel_rough=0.48,
        pole_color=(0.30, 0.31, 0.32), pole_metallic=0.75, pole_rough=0.35,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.58, 0.58, 0.56), parapet_rough=0.60,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        leaf_a=(0.025, 0.045, 0.015), leaf_b=(0.035, 0.060, 0.020),
        # [v7 판정 ⑥-2] 원경(44~48 m) 수목 띠 전용 — 대기원근으로 채도·대비가
        #   떨어진 회록 3종. 근경 leaf_a/b(진초록)를 그대로 쓰면 원경이
        #   "도색 판"으로 굳는다. sRGB 로 (76,89,70)/(66,79,61)/(86,96,79).
        leaf_far_a=(0.075, 0.100, 0.062),
        leaf_far_b=(0.055, 0.078, 0.048),
        leaf_far_c=(0.095, 0.118, 0.082),
        grass_tint=(0.55, 0.68, 0.42),
        nosing_color=(0.85, 0.72, 0.10),
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
    # 브리프 R6 지정값. 그림자 방위 φ = 171.5 −110 +233.5 = 295° →
    #   수평 그림자 방위 ≈ 25°(거의 +X = 상판 종주축). 그레이팅 슬릿 그림자가
    #   계단 진행방향으로 길게 늘어나 노면 스트라이프(투과 단서)가 최대가 된다.
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
# [C] 경로 + 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene11")
ASSET_ROLES = ["paving_interlock", "metal_rust", "concrete_wall",
               "granite_dark", "brick_red", "grass", "tactile", "sign_info",
               "hdri", "mdl"]


def _flight_run():
    st = PARAMS["stair"]
    return st["n"] * st["tread"]


def _flight_drop():
    st = PARAMS["stair"]
    return st["n"] * st["riser"]


def _east_x():
    """동측 x 마디: (상부참 시작, A상단, A하단=중간참 시작, 중간참 끝, B하단)."""
    e = PARAMS["east"]
    run = _flight_run()
    a1 = e["a_x0"] + run                       # 22.04
    m1 = a1 + e["mid_len"]                     # 23.84
    b1 = m1 + run                              # 30.88
    return (e["pad_x0"], e["a_x0"], a1, m1, b1)


# ===========================================================================
# [C1b] 카메라 검산 기반 — AABB 장애물 + 솔리드 조회(레이마칭 단일 출처)
#   [v6 판정 지시] 재조준(`under_grating`)·사인 방위 수정의 근거를 좌표로
#   검산한다. scene08 `_obstacle_boxes` / `_solid_at` 규약을 따른다.
#   동·서 계단은 rot_group 180° 로 **x=0 대칭**이므로 ax=|x| 로 공통 처리.
# ===========================================================================
def _stair_top(ax):
    """|x| 에서의 계단·참 상면 z (계단 대역 밖이면 None). 폭 판정은 호출측."""
    e = PARAMS["east"]
    st = PARAMS["stair"]
    run = _flight_run()
    a0 = e["a_x0"]
    a1 = a0 + run
    m1 = a1 + e["mid_len"]
    b1 = m1 + run
    z_mid = e["z_top"] - _flight_drop()
    if e["pad_x0"] <= ax <= a0:
        return e["z_top"]
    if a0 < ax <= a1:
        i = min(st["n"], int((ax - a0) / st["tread"]) + 1)
        return e["z_top"] - i * st["riser"]
    if a1 < ax <= m1:
        return z_mid
    if m1 < ax <= b1:
        i = min(st["n"], int((ax - m1) / st["tread"]) + 1)
        return z_mid - i * st["riser"]
    return None


def _solid_at(x, y, z):
    """점 (x,y,z)를 품는 지형·구조 솔리드 이름(없으면 None).
    카메라 eye 매몰 + 시선 차단(ray march) 검사의 단일 출처.
    그레이팅 디딤판은 두께 tread_t 의 얇은 슬래브로 모델링한다(슬릿은
    무시 — 차단 판정을 보수적으로 잡기 위함)."""
    g = PARAMS["ground"]
    rd = PARAMS["road"]
    wk = PARAMS["walk"]
    dk = PARAMS["deck"]
    e = PARAMS["east"]
    st = PARAMS["stair"]
    if g["x0"] <= x <= g["x1"] and g["y0"] <= y <= g["y1"] \
            and g["z_top"] - g["thick"] <= z <= g["z_top"]:
        return "Ground"
    if rd["x0"] <= x <= rd["x1"] and rd["y0"] <= y <= rd["y1"] \
            and rd["z_top"] - rd["thick"] <= z <= rd["z_top"]:
        return "Road"
    for tag, xa, xb in (("Walk_W", wk["xw0"], wk["xw1"]),
                        ("Walk_E", wk["xe0"], wk["xe1"])):
        if xa <= x <= xb and wk["y0"] <= y <= wk["y1"] \
                and wk["z_top"] - wk["thick"] <= z <= wk["z_top"]:
            return tag
    vg = PARAMS["verge"]
    for tag, xa, xb in (("Verge_W", wk["xw0"] - vg["w"], wk["xw0"]),
                        ("Verge_E", wk["xe1"], wk["xe1"] + vg["w"])):
        if xa <= x <= xb and vg["y0"] <= y <= vg["y1"] \
                and -0.30 <= z <= vg["curb_top"]:
            return tag
    # ── 상판·지지 기둥·상판 난간 ──
    if dk["x0"] <= x <= dk["x1"] and dk["y0"] <= y <= dk["y1"] \
            and dk["z_top"] - dk["thick"] <= z <= dk["z_top"]:
        return "Deck"
    dp = PARAMS["deck_posts"]
    for i, px in enumerate(dp["xs"]):
        if math.hypot(x - px, y - dp["y"]) <= dp["r"] \
                and dp["z_bot"] <= z <= dk["z_top"] - dk["thick"]:
            return f"DeckPost_{i}"
    rb = PARAMS["rail_bay"]
    for i, ye in enumerate((dk["y0"], dk["y1"])):
        if abs(y - ye) <= max(dk["panel_t"], rb["post_t"]) / 2.0 \
                and dk["x0"] <= x <= dk["x1"] \
                and dk["z_top"] <= z <= dk["z_top"] + rb["post_h"]:
            return f"DeckRail_{i}"
    # ── 계단 2조(동·서 대칭) ──
    ax = abs(x)
    top = _stair_top(ax)
    if top is not None:
        run = _flight_run()
        a0, a1 = e["a_x0"], e["a_x0"] + run
        m1 = a1 + e["mid_len"]
        on_pad = (e["pad_x0"] <= ax <= a0) or (a1 < ax <= m1)
        half = (e["pad_y1"] if on_pad else st["y1"])
        if abs(y) <= half:
            if on_pad:
                if top - PARAMS["deck"]["thick"] <= z <= top:
                    return "StairPad"
            elif top - st["tread_t"] <= z <= top:
                return "StairTread"
    # ── 버스 쉘터(지붕판) ──
    sh = PARAMS["dress"]["shelter"]
    if sh["x0"] <= x <= sh["x1"] and sh["y0"] <= y <= sh["y1"] \
            and sh["z_roof"] <= z <= sh["z_roof"] + 0.10:
        return "ShelterRoof"
    # ── 원경 수목 띠 · 건물 ──
    tb = PARAMS["treeband"]
    #   [v7 판정 ⑥-2] 2층 구성(낮은 덤불 박스 + 수관 블롭)으로 바뀌면서
    #   실루엣 상단이 h·1.04·1.16 까지 올라가고 x 확산도 ±3.1 로 커졌다.
    #   차단 판정은 **보수적(= 실제보다 크게)** 이어야 하므로 봉투를 넓힌다.
    for ri, (xa_, xb_, hh) in enumerate(tb["rows"]):
        if xa_ - 3.2 <= x <= xb_ + 3.2 and tb["y0"] <= y <= tb["y1"] \
                and g["z_top"] <= z <= g["z_top"] \
                + (hh + tb["jitter"]) * 1.21:
            return f"TreeBand_{ri}"
    for key, bd in PARAMS["buildings"].items():
        if bd["x0"] <= x <= bd["x1"] and bd["y0"] <= y <= bd["y1"] \
                and bd.get("base_z", 0.0) - 1.0 <= z \
                <= bd.get("base_z", 0.0) + bd["h"]:
            return f"Building_{key}"
    return None


def _obstacle_boxes():
    """카메라 충돌 검사용 드레싱·난간 AABB (name, x0,x1, y0,y1, z0,z1).
    지형·구조 솔리드는 `_solid_at` 담당 — 여기엔 얇은 프림만."""
    d = PARAMS["dress"]
    gz = PARAMS["walk"]["z_top"]
    boxes = []
    lp = d["lamp"]
    for i, (lx, ly) in enumerate(d["lamps"]):
        boxes.append((f"Lamp_{i}", lx - 1.3, lx + 1.3, ly - 0.6, ly + 0.6,
                      gz, gz + lp["pole_h"]))
    for i, (tx, ty) in enumerate(d["trees"]):
        boxes.append((f"Tree_{i}", tx - 1.1, tx + 1.1, ty - 1.1, ty + 1.1,
                      gz, gz + 4.2))
    for i, (bx, by, _yaw) in enumerate(d["benches"]):
        boxes.append((f"Bench_{i}", bx - 0.4, bx + 0.4, by - 1.0, by + 1.0,
                      gz, gz + 0.5))
    for i, (bx, by) in enumerate(d["bollards"]):
        boxes.append((f"Bollard_{i}", bx - 0.1, bx + 0.1, by - 0.1, by + 0.1,
                      gz, gz + 0.75))
    bx, by, bh = d["bus_pole"]
    boxes.append(("BusPole", bx - 0.3, bx + 0.3, by - 0.3, by + 0.3, gz,
                  gz + bh))
    sh = d["shelter"]
    boxes.append(("Shelter", sh["x0"], sh["x1"], sh["y0"], sh["y1"], gz,
                  sh["z_roof"] + 0.10))
    for i, (sx, sy, _yaw) in enumerate(PARAMS["sign"]["spots"]):
        boxes.append((f"Sign_{i}", sx - 0.5, sx + 0.5, sy - 0.5, sy + 0.5,
                      gz, gz + PARAMS["sign"]["pole_h"]))
    return boxes


# ===========================================================================
# [C2] 스모크 — 부팅 전 기하 자기검증 (조기종료)
# ===========================================================================
def _smoke_report():
    st = PARAMS["stair"]
    e = PARAMS["east"]
    dk = PARAMS["deck"]
    wk = PARAMS["walk"]
    run, drop = _flight_run(), _flight_drop()
    pad0, a0, a1, m1, b1 = _east_x()
    gz = wk["z_top"]
    print("=" * 68)
    print("scene11_footbridge_stairs — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 68)
    print(f"  계단: 폭 {st['y1']-st['y0']:.2f} · {st['n']}단 × 2련 · "
          f"riser {st['riser']} · tread {st['tread']} · 그레이팅 슬릿 {st['slits']}")
    print(f"    련당 run {run:.2f} / drop {drop:.3f} · 경사 "
          f"{math.degrees(math.atan2(st['riser'], st['tread'])):.2f}° · "
          f"2R+T = {2*st['riser']+st['tread']:.3f}")
    tot = 2 * drop
    print(f"    총 낙차 {tot:.3f} = 상판고 {e['z_top']:.2f} → "
          f"{'OK' if abs(tot-e['z_top']) < 1e-9 else 'FAIL'} (접속 단차 0)")
    print(f"    낙차 ≥ 0.3 m → {'OK' if tot >= 0.3 else 'FAIL'}")
    print(f"  [동측 x 마디] 상부참 {pad0:.2f}…{a0:.2f} · A {a0:.2f}…{a1:.2f} "
          f"· 중간참 {a1:.2f}…{m1:.2f} · B {m1:.2f}…{b1:.2f}")
    # ── 보행 연속성 표 ──
    z_mid = e["z_top"] - drop
    rows = [
        ("서측 보도 → 계단 B", gz, 0.0, "join"),
        ("서측 계단 B(22단)", 0.0, z_mid, "flight"),
        ("서측 중간참", z_mid, z_mid, "flat"),
        ("서측 계단 A(22단)", z_mid, e["z_top"], "flight"),
        ("서측 상부 참 → 상판", e["z_top"], dk["z_top"], "flat"),
        ("상판 → 동측 상부 참", dk["z_top"], e["z_top"], "flat"),
        ("동측 계단 A(22단)", e["z_top"], z_mid, "flight"),
        ("동측 중간참", z_mid, z_mid, "flat"),
        ("동측 계단 B(22단)", z_mid, 0.0, "flight"),
        ("동측 계단 → 보도", 0.0, gz, "join"),
    ]
    print("  [보행 연속성 검증표]")
    bad = 0
    for nm, z0, z1, kind in rows:
        d = abs(z1 - z0)
        if kind == "flight":
            ok = abs(d - drop) < 1e-9
        elif kind == "flat":
            ok = d < 1e-9
        else:
            ok = d <= 0.02
        bad += 0 if ok else 1
        print(f"    {nm:22s} z {z0:+.3f} → {z1:+.3f}  Δ{d:+.3f}  "
              f"{'OK' if ok else 'FAIL'}")
    print(f"    연속성 판정: {'OK' if bad == 0 else f'FAIL({bad})'}")
    # ── 위험: 중간참 킥플레이트 결손 ──
    print(f"  [위험①] 동측 중간참 킥플레이트 {'有' if e['kickplate'] else '無'} "
          f"— 참 상면 {z_mid:.3f} → 보도 {gz:+.3f} 낙차 {z_mid-gz:.3f} m")
    print(f"    로봇 h0.3 시야 하단이 난간 하부 개방대(0…"
          f"{PARAMS['rail']['rail_h']-PARAMS['rail']['rail_mid_drop']:.2f} m)를 "
          f"통과 → 낙차 은닉 성립 {'OK' if not e['kickplate'] else 'FAIL(대조군)'}")
    print(f"    서측 중간참 킥플레이트 "
          f"{'有' if PARAMS['west']['kickplate'] else '無'} (동일 기하 대조군)")
    print(f"  [위험②] 상판·계단 상부 측면 → 차도면 "
          f"{PARAMS['road']['z_top']:+.2f} 낙차 "
          f"{dk['z_top']-PARAMS['road']['z_top']:.3f} m (방음 패널이 바닥 단서 차단)")
    print(f"  [위험③] 그레이팅 투과: 디딤판 {st['slits']}슬릿 × 0.02 m + 전후 "
          f"gap {st['gap']} → 라이저 부재로 하부 직시")
    # ── 상판 유효고 · 기둥 ──
    deck_bot = dk["z_top"] - dk["thick"]
    print(f"  [상판] 상면 {dk['z_top']:.2f} 저면 {deck_bot:.2f} · 차도 "
          f"{PARAMS['road']['z_top']:+.2f} → 유효고 "
          f"{deck_bot-PARAMS['road']['z_top']:.2f} m "
          f"{'OK' if deck_bot-PARAMS['road']['z_top'] >= 4.5 else 'FAIL'}")
    dp = PARAMS["deck_posts"]
    for i, px in enumerate(dp["xs"]):
        on_walk = (wk["xw0"] <= px <= wk["xw1"]) or (wk["xe0"] <= px <= wk["xe1"])
        print(f"    지지 기둥 x={px:+.2f} · 보도 위 {'OK' if on_walk else 'FAIL'} "
              f"· 연석(±{PARAMS['road']['x1']:.2f}) 바깥 "
              f"{'OK' if abs(px) > PARAMS['road']['x1'] else 'FAIL'}")
    # ── rot_group 180° 좌표 검산 (서측) ──
    w = PARAMS["west"]
    px, py = w["pivot"]

    def _rot180(x, y):
        return (2*px - x, 2*py - y)
    locs = [("상부참 서단", 0.0, 0.0), ("A 하단", run, 0.0),
            ("중간참 끝", run + e["mid_len"], 0.0),
            ("B 하단", 2*run + e["mid_len"], 0.0)]
    print("  [서측 rot_group 180° 검산]  (x,y) → (−15 − x, −y)")
    for nm, lx, ly in locs:
        wx, wy = _rot180(lx, ly)
        print(f"    {nm:10s} 로컬 x {lx:6.2f} → 월드 x {wx:7.2f}")
    wxb, _ = _rot180(2*run + e["mid_len"], 0.0)
    print(f"    서측 하단 x {wxb:.2f} ⊂ 서측 보도 [{wk['xw0']:.1f}, "
          f"{wk['xw1']:.1f}] → {'OK' if wk['xw0'] <= wxb <= wk['xw1'] else 'FAIL'}")
    # ── 그리드 카메라 vs 신설 기하 좌표 검산 ──
    gx, gy, gzc = _grid_shift()
    print(f"  [그리드] 원점 = 동측 낙차 시작 (x {gx:.2f}, y {gy:.2f}, z {gzc:.2f})")
    for d in (2, 5, 10):
        ex = gx - d
        on_deck = dk["x0"] <= ex <= e["pad_x1"]
        in_w = dk["y0"] < gy < dk["y1"]
        print(f"    d={d:2d}  eye ({ex:+.2f}, {gy:+.2f}, {gzc+0.3:.2f}~"
              f"{gzc+1.8:.2f}) · 상판/참 위 {'OK' if on_deck else 'FAIL'} "
              f"· 폭 안 {'OK' if in_w else 'FAIL'}")
    print(f"    지지 기둥(x ±11.80, z ≤ {deck_bot:.2f})은 상판 **아래** — "
          f"eye z ≥ {gzc+0.3:.2f} 시선 폐색 없음 OK")
    print(f"    시선 회랑(y −1.2…1.2, x {dk['x0']:.1f}…{b1:.1f}) 드레싱 침입: "
          f"{_corridor_hits()} 개 → {'OK' if _corridor_hits() == 0 else 'FAIL'}")

    # ── 정면 프로파일(그리드 축 y=0, x 증가) — 낙차 GT 가 프레임에 있는가 ──
    print("  [정면 프로파일] 그리드 축 y=0.00 · x 15.0 → 20.0 (0.25 m 간격)")
    prof = []
    xx = gx
    while xx <= gx + 5.0:
        topz = None
        zz = 6.5
        while zz > -0.60:
            if _solid_at(xx, gy, zz) is not None:
                topz = zz
                break
            zz -= 0.01
        prof.append((xx, topz))
        xx += 0.25
    for xx, topz in prof:
        print(f"    x {xx:+6.2f}  상면 "
              f"{'개방(지면)' if topz is None else f'{topz:+.3f}'}  "
              f"(상판면 대비 "
              f"{(gz if topz is None else topz) - gzc:+.3f})")
    dmax = max(gzc - (t if t is not None else gz) for _, t in prof)
    print(f"    프로파일 최대 낙차 {dmax:.3f} m ≥ 0.3 → "
          f"{'OK(낙차 GT 프레임 내)' if dmax >= 0.3 else 'FAIL'}")

    # ── h0.3 은닉 검산 (상판 연단 스침 시선) ──
    print("  [h0.3 은닉 검산] 상판 연단(x=15.0, z 5.500) 스치는 시선")
    for dd in (2.0, 5.0, 10.0):
        x_hit = gx + (gzc - gz) * dd / 0.3
        print(f"    d={dd:4.1f} m → 보도 재출현 x {x_hit:7.1f} vs 계단 하단 "
              f"{b1:.2f} → 계단 전 구간 은닉 "
              f"{'OK' if x_hit > b1 else 'FAIL'}")

    # ── 카메라 충돌·시선 차단 검산 (scene08 규약) ──
    boxes = _obstacle_boxes()
    views = build_views()
    print(f"  [카메라 충돌 검산] 뷰 {len(views)}개 × AABB {len(boxes)}개")
    hits = []
    for name, v in sorted(views.items()):
        ex, ey, ez = v["eye"]
        for bn, x0, x1, y0, y1, z0, z1 in boxes:
            if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1:
                hits.append((name, bn))
        s = _solid_at(ex, ey, ez)
        if s is not None:
            hits.append((name, f"{s}(지형 매몰)"))
    for name, bn in hits:
        print(f"    [FAIL] {name} eye 가 {bn} 내부")
    print(f"    충돌: {len(hits)}건 → {'OK' if not hits else 'FAIL'}")
    print("    [시선 차단] 미장센 컷 ray march 0.1 m (첫 차단 비율 ≥ 0.90 = OK)")
    print("      ※ preset_* 그리드는 pitch −10° 로 바닥을 겨냥하는 규약 — 제외")
    blocked = []
    for name, v in sorted(views.items()):
        if name.startswith("preset_"):
            continue
        eA = np.array(v["eye"], dtype=float)
        tg = np.array(v["tgt"], dtype=float)
        Ln = float(np.linalg.norm(tg - eA))
        frac, hit = 1.0, None
        for k in range(1, int(Ln / 0.1) + 1):
            f = k * 0.1 / Ln
            s = _solid_at(*(eA + (tg - eA) * f))
            if s is not None:
                frac, hit = f, s
                break
        ok = frac >= 0.90
        print(f"      {name:18s} 첫 차단 {frac:5.2f} "
              f"({hit if hit else '없음'}) → {'OK' if ok else 'FAIL'}")
        if not ok:
            blocked.append(name)
    print(f"      차단 컷: {blocked if blocked else '없음 → OK'}")

    # ── under_grating 역광 축 검산 (v6 판정 ④ 재조준 근거) ──
    ug = build_views()["under_grating"]
    ve = np.array(ug["tgt"], dtype=float) - np.array(ug["eye"], dtype=float)
    ve /= np.linalg.norm(ve)
    # 돔 회전 φ = SUN_AZ_OFFSET + noon_dome_rot + hdri_sun_rotz_offset,
    #   수평 그림자 방위 = atan2(cosφ, −sinφ), 태양 방위 = 그림자 + 180°
    phi = (PARAMS["SUN_AZ_OFFSET"] - 110.0 + 233.5) % 360.0
    shadow_az = math.degrees(math.atan2(math.cos(math.radians(phi)),
                                        -math.sin(math.radians(phi)))) % 360.0
    sun_az = (shadow_az + 180.0) % 360.0
    cam_az = math.degrees(math.atan2(ve[1], ve[0])) % 360.0
    cam_el = math.degrees(math.asin(max(-1.0, min(1.0, ve[2]))))
    daz = abs((cam_az - sun_az + 180.0) % 360.0 - 180.0)
    print(f"  [under_grating 역광 축] 그림자 방위 {shadow_az:.1f}° → 태양 방위 "
          f"{sun_az:.1f}°/고도 {PARAMS['light']['noon_sun_elev']:.1f}°")
    print(f"    카메라 시선 방위 {cam_az:.1f}° · 고도 {cam_el:+.1f}° → 태양과 "
          f"방위차 {daz:.1f}° → {'OK(역광 = 슬릿 투광 최대)' if daz <= 45.0 else 'FAIL(순광/측광)'}")

    # ── [v7 판정 ⑥-3] under_grating 프레임 점유 검산 ──
    #   v6→v7 재조준이 실패한 이유가 "역광은 맞는데 하늘이 프레임을 먹는다"
    #   였으므로, 축 검산만으로는 부족하다. `_solid_at` 를 단일 출처로
    #   프레임을 성기게(32×18) 레이캐스트해 하늘 비율·주 피사체를 직접 잰다.
    #   화각은 v6 렌더 역산치(hFOV 반각 32.6° / vFOV 반각 19.8°, 16:9).
    def _frame_occupancy(eye, tgt, nx=32, ny=18, far=70.0):
        e = np.array(eye, dtype=float)
        fwd = np.array(tgt, dtype=float) - e
        fwd /= np.linalg.norm(fwd)
        rgt = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
        rgt /= np.linalg.norm(rgt)
        upv = np.cross(rgt, fwd)
        th, tv = math.tan(math.radians(32.6)), math.tan(math.radians(19.8))
        sky, cnt = 0, {}
        for j in range(ny):
            sv = (1.0 - 2.0 * (j + 0.5) / ny) * tv
            for i in range(nx):
                su = (2.0 * (i + 0.5) / nx - 1.0) * th
                d = fwd + rgt * su + upv * sv
                d /= np.linalg.norm(d)
                t, what = 0.05, None
                while t < far:
                    what = _solid_at(*(e + d * t))
                    if what is not None:
                        break
                    t += 0.05 if t < 10.0 else 0.30
                if what is None:
                    sky += 1
                else:
                    cnt[what] = cnt.get(what, 0) + 1
        return sky / float(nx * ny), cnt

    sky_f, subj = _frame_occupancy(ug["eye"], ug["tgt"])
    top = sorted(subj.items(), key=lambda kv: -kv[1])[:3]
    print(f"    프레임 점유(레이캐스트 32×18) 하늘 {sky_f*100:.1f} % → "
          f"{'OK(≤30 % — 슬릿 투광 판독 가능)' if sky_f <= 0.30 else 'FAIL(하늘 과다)'}")
    print(f"    주 피사체 {[(n, c) for n, c in top]}  "
          f"(구 컷 eye(22.0,0,0.60)→tgt(16.0,0,4.20) 은 하늘 64.7 %)")
    print("=" * 68)


def _grid_shift():
    """그리드 원점 = 동측 계단의 낙차 시작 모서리(상부 참 동단, 상판 레벨)."""
    e = PARAMS["east"]
    return (e["a_x0"], 0.0, e["z_top"])


def _corridor_hits():
    """그리드 시선 회랑(y −1.2…1.2, x −13.2…30.88) 안의 드레싱 프림 수."""
    d = PARAMS["dress"]
    _, _, _, _, b1 = _east_x()
    pts = list(d["trees"]) + list(d["lamps"]) + list(d["bollards"]) \
        + [(b[0], b[1]) for b in d["benches"]] + [d["bus_pole"][:2]]
    sh = d["shelter"]
    pts += [((sh["x0"]+sh["x1"])/2.0, (sh["y0"]+sh["y1"])/2.0)]
    pts += [(s[0], s[1]) for s in PARAMS["sign"]["spots"]]
    n = 0
    for x, y in pts:
        if PARAMS["deck"]["x0"] <= x <= b1 and -1.2 <= y <= 1.2:
            n += 1
    return n


# ===========================================================================
# [D] 카메라 프리셋 — grid_views(상판 종주 +X) + 미장센 5컷
# ===========================================================================
def build_views():
    """그리드 원점을 (동측 낙차 시작 x=15.0, 상판 z=5.5)로 시프트.
    로봇 h0.3(= z 5.8)에서 그레이팅 투과·단코 소실·중간참 개방이 성립하는지가
    판정 1순위. 지상 보도 접근은 sidewalk_approach 컷으로 별도 제공."""
    gx, gy, gz = _grid_shift()
    v = sc.grid_views(gy)
    out = {}
    for k, val in v.items():
        e, t = list(val["eye"]), list(val["tgt"])
        e[0] += gx
        e[2] += gz
        t[0] += gx
        t[2] += gz
        out[k] = dict(eye=e, tgt=t)
    _, _, a1, m1, b1 = _east_x()
    z_mid = PARAMS["east"]["z_top"] - _flight_drop()
    # under_grating: [v7 판정 ⑥-3 재조준 — 재실패 원인 규명]
    #   v6→v7 에서 축(y=0 슬릿 정중앙·−X 상행·역광)은 옳게 잡았으나
    #   **eye z 0.60 · 고도 +31°** 가 문제였다. 눈이 낮고 조준각이 얕으면
    #   소핏은 전부 시선 **위쪽**에 걸린다(같은 눈에서 소핏의 앙각은 원단
    #   x=15 에서 34°, 근단 x=22 에서 90°). 즉 프레임 중심이 계단 꼭대기
    #   **너머 하늘**을 겨눈 셈이라 하늘이 64.7 %(_solid_at 레이캐스트 실측)
    #   를 먹었다. 태양(방위 205°·고도 49.8°)도 차폐 없이 프레임 상단에
    #   걸려 플레어까지 났다.
    #   → 눈을 계단 A 소핏 바로 밑(x 21.70, 헤드룸 0.83 m)으로 올리고
    #      조준 고도를 **+50°** 로 세운다. tgt 는 그 시선이 처음 만나는
    #      **디딤판 저면 위의 점**(x 20.79, z 3.08 — 아래 스모크가 검산)으로
    #      두어, 시선 차단 검사(첫 차단 ≥0.90)도 그대로 통과한다.
    #   실측(동일 레이캐스트): 하늘 18.5 % · 프레임 피사체 100 % StairTread ·
    #      태양은 디딤판에 **차폐**(직사 디스크 없음 = 슬릿 투광만 남음).
    out["under_grating"] = dict(eye=[21.70, 0.00, 2.00],
                                tgt=[20.79, 0.00, 3.08])
    # deck_walk: 상판 종주 보행자 시점(h1.6) — 방음 패널 사이 회랑
    out["deck_walk"] = dict(eye=[-9.00, 0.00, 7.10], tgt=[8.00, 0.00, 6.30])
    # midlanding: 동측 중간참 로봇 시점(h0.3) — 킥플레이트 결손 개방대 정면
    out["midlanding"] = dict(eye=[a1 + 0.30, 0.00, z_mid + 0.30],
                             tgt=[m1 + 1.60, -1.90, z_mid - 0.35])
    # sidewalk_approach: 브리프 R6 "보도 접근" — 동측 보도에서 계단 하단으로
    out["sidewalk_approach"] = dict(eye=[38.00, -5.00, 0.90],
                                    tgt=[26.00, -0.40, 3.20])
    # overview: 육교 전경 부감(차도 6차로·상판·양측 계단 동시)
    out["overview"] = dict(eye=[44.00, -34.00, 17.00], tgt=[2.00, 0.00, 4.00])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드      — 그레이팅 투과·단코 소실로 하강 시작(x=15.0)이 은닉되나
                       (방음판 그림자면 순흑 대역이 개방 베이로 걷혔는지 함께)
 2. midlanding       — 동측 중간참 난간 하부 개방대(킥플레이트 無) 2.755 m 낙차
 3. under_grating    — 역광 재조준: 라이저 부재 하부 투시 + 슬릿 투광 스트라이프
 4. deck_walk        — 지주 분절 + 개방 베이 교대 회랑 · 상판 유효고 5.25 m
 5. sidewalk_approach— 안내 사인이 **접근자를 마주보는지**(구 흑색 배면 패널
                       오독 제거) · 보도/연석/식재대로 '육교' 즉독
 6. overview         — 왕복 6차로·차선·양측 계단 접지·서측 킥플레이트 有 대조
 7. cue              — 점자띠 4개소·단코 황색 띠·연석/차선 재질 경계
 8. 경계·지평        — 식재대·가로수 열·원경 수목 띠로 양측 지평이 폐쇄됐나
 9. [v7] 강재 얼룩   — midlanding 참 상면·계단 스트링거가 **백·갈 고대비 얼룩**
                       이 아니라 도장 강판(중성 다크그레이 + 미세 발청)인가
                       (albedo add/brightness/desaturation 로 레인지 압축)
10. [v7] 수목 띠     — 배경 수목 띠가 **평평한 초록 슬래브 벽**이 아니라
                       상단이 톱니인 저채도 회록 수관 군락으로 읽히는가"""


# ===========================================================================
# [E] 메인
# ===========================================================================
def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        _smoke_report()
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
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
    ROOT = "/World/Scene11"
    UsdGeom.Xform.Define(stage, ROOT)

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    st = PARAMS["stair"]
    E = PARAMS["east"]
    RUN, DROP = _flight_run(), _flight_drop()
    Z_MID = E["z_top"] - DROP

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *a, **kw):
        return sc.make_pbr(stage, path, *a, **kw)

    def PBR_ALBEDO(path, *a, albedo=None, **kw):
        """[v7 판정 ⑥-1] make_pbr + OmniPBR 알베도 레인지 보정 입력.

        `scene_common.make_pbr` 는 albedo_add/brightness/desaturation 을
        노출하지 않는다(그리고 scene_common 은 21씬 공용이라 무수정 원칙).
        → 여기서는 make_pbr 이 만든 셰이더 프림에 **입력만 추가**한다.
        OmniPBR.mdl 의 정의(파일 62·68·74행)상 셋 다 float 이고,
        base::file_texture(color_offset=add, color_scale=brightness) →
        lerp(tint, mono, desaturation) 순으로 적용된다. 즉
            diffuse = lerp(tex*brightness + add,  mono(...),  desaturation)
        이라 **텍스처의 명암 레인지 자체를 압축**할 수 있다(틴트는 곱셈이라
        레인지를 못 줄인다 — v6/v7 재판정의 원인).
        """
        mtl = sc.make_pbr(stage, path, *a, **kw)
        if albedo:
            from pxr import UsdShade, Sdf
            sh = UsdShade.Shader.Get(stage, path + "/Shader")
            for key in ("brightness", "add", "desaturation"):
                if key in albedo:
                    sh.CreateInput(f"albedo_{key}",
                                   Sdf.ValueTypeNames.Float).Set(
                        float(albedo[key]))
        return mtl

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        s = mp["scale"]
        M = {}
        M["paving"] = PBR(f"{ROOT}/Looks/Paving",
                          sc.tex_path("paving_interlock", "diff"),
                          sc.tex_path("paving_interlock", "nor"),
                          sc.tex_path("paving_interlock", "rough"),
                          s["paving_interlock"])
        # 철제 계단·참 — [v7 판정 ⑥-1] metal_rust 를 **relief(법선·거칠기)** 로만
        #   쓰고, 알베도는 add/brightness 로 레인지를 압축 + desaturation 으로
        #   녹/소지 색분리 제거 → "도장 강판 + 국부 발청" 인상.
        M["metal"] = PBR_ALBEDO(f"{ROOT}/Looks/Metal",
                                sc.tex_path("metal_rust", "diff"),
                                sc.tex_path("metal_rust", "nor"),
                                sc.tex_path("metal_rust", "rough"),
                                s["metal_rust"], tint=mp["metal_tint"],
                                albedo=mp["metal_albedo"])
        M["concrete"] = PBR(f"{ROOT}/Looks/Concrete",
                            sc.tex_path("concrete_wall", "diff"),
                            sc.tex_path("concrete_wall", "nor"),
                            sc.tex_path("concrete_wall", "rough"),
                            s["concrete_wall"], tint=mp["concrete_tint"])
        M["soil"] = PBR(f"{ROOT}/Looks/Soil", sc.tex_path("grass", "diff"),
                        sc.tex_path("grass", "nor"),
                        sc.tex_path("grass", "rough"), 1.2,
                        tint=mp["soil_tint"])
        M["curb"] = PBR(f"{ROOT}/Looks/Curb",
                        sc.tex_path("granite_dark", "diff"),
                        sc.tex_path("granite_dark", "nor"),
                        sc.tex_path("granite_dark", "rough"), s["granite_dark"])
        M["brick"] = PBR(f"{ROOT}/Looks/Brick",
                         sc.tex_path("brick_red", "diff"),
                         sc.tex_path("brick_red", "nor"),
                         sc.tex_path("brick_red", "rough"), s["brick_red"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"),
                         sc.tex_path("grass", "rough"), s["grass"],
                         tint=mp["grass_tint"])
        M["tactile"] = PBR(f"{ROOT}/Looks/Tactile",
                           sc.tex_path("tactile", "diff"),
                           sc.tex_path("tactile", "nor"), None, s["tactile"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"])
        M["band"] = PBR(f"{ROOT}/Looks/Band", diffuse_color=mp["band_color"],
                        roughness_const=mp["band_rough"])
        M["line_w"] = PBR(f"{ROOT}/Looks/LineWhite",
                          diffuse_color=mp["line_white"], roughness_const=0.7)
        M["line_y"] = PBR(f"{ROOT}/Looks/LineYellow",
                          diffuse_color=mp["line_yellow"], roughness_const=0.7)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["steel"] = PBR(f"{ROOT}/Looks/Steel", diffuse_color=mp["steel_color"],
                         metallic=mp["steel_metallic"],
                         roughness_const=mp["steel_rough"])
        M["panel"] = PBR(f"{ROOT}/Looks/Panel", diffuse_color=mp["panel_color"],
                         roughness_const=mp["panel_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"])
        # [v6 C-3 계열] 무텍스처 단색 판(스티로폼 인상) 회피 — 콘크리트 텍스처.
        #   사인 배킹에도 재사용해 "순흑 부유 패널" 오독을 막는다.
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           sc.tex_path("concrete_wall", "diff"),
                           sc.tex_path("concrete_wall", "nor"),
                           sc.tex_path("concrete_wall", "rough"),
                           s["concrete_wall"], tint=mp["parapet_tint"])
        M["signback"] = PBR(f"{ROOT}/Looks/SignBack",
                            diffuse_color=(0.44, 0.45, 0.46),
                            metallic=0.25, roughness_const=0.55)
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["leaf_a"] = PBR(f"{ROOT}/Looks/LeafA", diffuse_color=mp["leaf_a"],
                          roughness_const=1.0, specular_level=0.0)
        M["leaf_b"] = PBR(f"{ROOT}/Looks/LeafB", diffuse_color=mp["leaf_b"],
                          roughness_const=1.0, specular_level=0.0)
        # [v7 판정 ⑥-2] 원경 수목 띠 전용 저채도 회록 3종(대기원근)
        for tag in ("a", "b", "c"):
            M[f"leaf_far_{tag}"] = PBR(
                f"{ROOT}/Looks/LeafFar{tag.upper()}",
                diffuse_color=mp[f"leaf_far_{tag}"],
                roughness_const=1.0, specular_level=0.0)
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing",
                          diffuse_color=mp["nosing_color"],
                          roughness_const=0.7)
        # [v5 공통 레이어] 한글 사인 패널 — sign_info(육교 안내), uv_mode 1:1
        M["sign"] = PBR(f"{ROOT}/Looks/SignPanel",
                        diff=sc.tex_path("sign_info", "diff"),
                        uv_mode=True, roughness_const=0.6)
        return M

    # -------------------------------------------------------------------
    # 지반 · 차도 · 보도 · 연석 · 차선
    # -------------------------------------------------------------------
    def build_site(M):
        g = PARAMS["ground"]
        BOX(f"{ROOT}/Ground",
            ((g["x0"]+g["x1"])/2.0, (g["y0"]+g["y1"])/2.0,
             g["z_top"] - g["thick"]/2.0),
            (g["x1"]-g["x0"], g["y1"]-g["y0"], g["thick"]), M["grass"], col=True)
        rd = PARAMS["road"]
        BOX(f"{ROOT}/Road",
            ((rd["x0"]+rd["x1"])/2.0, (rd["y0"]+rd["y1"])/2.0,
             rd["z_top"] - rd["thick"]/2.0),
            (rd["x1"]-rd["x0"], rd["y1"]-rd["y0"], rd["thick"]),
            M["asphalt"], col=True)
        wk = PARAMS["walk"]
        for i, (xa, xb) in enumerate(((wk["xw0"], wk["xw1"]),
                                      (wk["xe0"], wk["xe1"]))):
            BOX(f"{ROOT}/Walk_{i}",
                ((xa+xb)/2.0, (wk["y0"]+wk["y1"])/2.0,
                 wk["z_top"] - wk["thick"]/2.0),
                (xb-xa, wk["y1"]-wk["y0"], wk["thick"]), M["paving"], col=True)
        cb = PARAMS["curb"]
        for i, xe in enumerate((rd["x0"], rd["x1"])):
            xc = xe - cb["w"]/2.0 if i == 0 else xe + cb["w"]/2.0
            BOX(f"{ROOT}/Curb_{i}",
                (xc, (wk["y0"]+wk["y1"])/2.0, cb["z_top"] - cb["thick"]/2.0),
                (cb["w"], wk["y1"]-wk["y0"], cb["thick"]), M["curb"], col=True)
        # [v6 판정 C-2] 식재대 — 보도 바깥 경계 1열(경계석 2줄 + 지피).
        vg = PARAMS["verge"]
        vy0, vy1 = vg["y0"], vg["y1"]
        for i, (xa, xb) in enumerate(((wk["xw0"] - vg["w"], wk["xw0"]),
                                      (wk["xe1"], wk["xe1"] + vg["w"]))):
            for j, xc in enumerate((xa + vg["curb_t"]/2.0,
                                    xb - vg["curb_t"]/2.0)):
                BOX(f"{ROOT}/VergeCurb_{i}_{j}",
                    (xc, (vy0+vy1)/2.0, vg["curb_top"] - 0.22),
                    (vg["curb_t"], vy1-vy0, 0.44), M["curb"], col=True)
            BOX(f"{ROOT}/VergeSoil_{i}",
                ((xa+xb)/2.0, (vy0+vy1)/2.0, vg["soil_top"] - 0.20),
                ((xb-xa) - 2*vg["curb_t"], vy1-vy0, 0.40), M["soil"], col=True)

    def build_lanes(M):
        ln = PARAMS["lane"]
        for i, x in enumerate(ln["center_xs"]):
            BOX(f"{ROOT}/CenterLine_{i}", (x, (ln["y0"]+ln["y1"])/2.0, ln["z"]),
                (ln["w"], ln["y1"]-ln["y0"], ln["t"]), M["line_y"])
        period = ln["seg"] + ln["gap"]
        ndash = int((ln["y1"] - ln["y0"]) / period)
        for j, x in enumerate(ln["dash_xs"]):
            for k in range(ndash):
                yc = ln["y0"] + k*period + ln["seg"]/2.0
                BOX(f"{ROOT}/Dash_{j}_{k}", (x, yc, ln["z"]),
                    (ln["w"], ln["seg"], ln["t"]), M["line_w"])
        # 계단 하부 노면 밴드 — 그레이팅 슬릿 그림자를 받는 대조면
        # 계단 하부 노면 밴드 2매(동/서 대칭) — 그레이팅 슬릿 그림자 대조면
        bd = PARAMS["dress"]["band"]
        xc = (bd["x0"] + bd["x1"]) / 2.0
        for i, sgn in enumerate((1.0, -1.0)):
            BOX(f"{ROOT}/GratingBand_{i}", (sgn * xc, 0.0, bd["z"]),
                (bd["x1"]-bd["x0"], bd["y1"]-bd["y0"], bd["t"]), M["band"])

    # -------------------------------------------------------------------
    # 상판 + 지지 기둥
    # -------------------------------------------------------------------
    def build_deck(M):
        dk = PARAMS["deck"]
        BOX(f"{ROOT}/Deck",
            ((dk["x0"]+dk["x1"])/2.0, (dk["y0"]+dk["y1"])/2.0,
             dk["z_top"] - dk["thick"]/2.0),
            (dk["x1"]-dk["x0"], dk["y1"]-dk["y0"], dk["thick"]),
            M["concrete"], col=True)
        dp = PARAMS["deck_posts"]
        z1 = dk["z_top"] - dk["thick"]
        for i, px in enumerate(dp["xs"]):
            CYL(f"{ROOT}/DeckPost_{i}", (px, dp["y"], (dp["z_bot"]+z1)/2.0),
                dp["r"], z1-dp["z_bot"], M["concrete"], col=True)
            BOX(f"{ROOT}/DeckCap_{i}",
                (px, dp["y"], z1 - dp["cap_h"]/2.0),
                (dp["cap_sx"], dp["cap_sy"], dp["cap_h"]), M["concrete"])

    # -------------------------------------------------------------------
    # 계단 1조 (상부 참 → A → 중간참 → B). prefix 아래 로컬/월드 공용.
    #   x0_pad : 상부 참 서단, 이후 전부 +X 하강. kick=킥플레이트 유무.
    # -------------------------------------------------------------------
    def build_stair_set(M, prefix, x0_pad, x1_pad, kick, tag):
        a0 = x1_pad
        a1 = a0 + RUN
        m1 = a1 + E["mid_len"]
        b1 = m1 + RUN
        py0, py1 = E["pad_y0"], E["pad_y1"]
        dk_t = PARAMS["deck"]["thick"]
        # 상부 참 (상판과 같은 두께의 강상판)
        BOX(f"{prefix}/PadTop",
            ((x0_pad+x1_pad)/2.0, (py0+py1)/2.0, E["z_top"] - dk_t/2.0),
            (x1_pad-x0_pad, py1-py0, dk_t), M["metal"], col=True)
        # 계단 A (그레이팅 개방 라이저)
        sc.build_open_riser_stairs(
            stage, f"{prefix}/FlightA", a0, st["y0"], st["y1"], st["riser"],
            st["tread"], st["n"], E["z_top"], M["metal"], M["metal"],
            tread_t=st["tread_t"], gap=st["gap"], slits=st["slits"])
        # 중간참 (강상판 + 지지 기둥 4)
        BOX(f"{prefix}/MidLanding",
            ((a1+m1)/2.0, (py0+py1)/2.0, Z_MID - dk_t/2.0),
            (m1-a1, py1-py0, dk_t), M["metal"], col=True)
        for i, (lx, ly) in enumerate(((a1+0.30, py0+0.30), (a1+0.30, py1-0.30),
                                      (m1-0.30, py0+0.30), (m1-0.30, py1-0.30))):
            zt = Z_MID - dk_t
            CYL(f"{prefix}/MidPost_{i}", (lx, ly, (-0.30+zt)/2.0), 0.11,
                zt+0.30, M["metal"], col=True)
        # 계단 B
        sc.build_open_riser_stairs(
            stage, f"{prefix}/FlightB", m1, st["y0"], st["y1"], st["riser"],
            st["tread"], st["n"], Z_MID, M["metal"], M["metal"],
            tread_t=st["tread_t"], gap=st["gap"], slits=st["slits"])
        # 단코 논슬립 띠
        if cfg["cue_nosing"]:
            for j, (bx, ztop) in enumerate(((a0, E["z_top"]), (m1, Z_MID))):
                sc.build_nosing(stage, f"{prefix}/Nosing_{j}", bx, st["y0"],
                                st["y1"], st["riser"], st["tread"], st["n"],
                                mtl=M["nosing"], width=0.06, proud=0.003,
                                z_top=ztop)
        # 난간 + 킥플레이트
        if cfg["cue_railing"]:
            ra = PARAMS["rail"]

            def _gnd(bx, ztop):
                def f(x):
                    if x <= bx:
                        return ztop
                    if x >= bx + RUN:
                        return ztop - DROP
                    i = min(int((x - bx) / st["tread"]), st["n"] - 1)
                    return ztop - st["riser"] * (i + 1)
                return f
            for k, y in enumerate((st["y0"] + ra["y_inset"],
                                   st["y1"] - ra["y_inset"])):
                sc.build_railing_line(
                    stage, f"{prefix}/RailA_{k}", y, x0_pad, a0, RUN, DROP,
                    _gnd(a0, E["z_top"]), M["rail"], rail_h=ra["rail_h"],
                    post_r=ra["post_r"], spacing=ra["spacing"],
                    rail_r=ra["rail_r"], rail_mid_r=ra["rail_mid_r"],
                    rail_mid_drop=ra["rail_mid_drop"])
                sc.build_railing_line(
                    stage, f"{prefix}/RailB_{k}", y, a1, m1, RUN, DROP,
                    _gnd(m1, Z_MID), M["rail"], rail_h=ra["rail_h"],
                    post_r=ra["post_r"], spacing=ra["spacing"],
                    rail_r=ra["rail_r"], rail_mid_r=ra["rail_mid_r"],
                    rail_mid_drop=ra["rail_mid_drop"])
            # 킥플레이트(발끝막이판) — 중간참 양측. 동측은 **결손**이 위험 본질.
            if kick:
                for k, ye in enumerate((py0, py1)):
                    BOX(f"{prefix}/Kick_{k}",
                        ((a1+m1)/2.0, ye, Z_MID + E["kick_h"]/2.0),
                        (m1-a1, 0.05, E["kick_h"]), M["rail"])
        # 승강부 점자띠
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{prefix}/TactileTop_{tag}",
                             a0 - tc["pad_len"], a0, st["y0"], st["y1"],
                             M["tactile"], z=E["z_top"], proud=tc["proud"])
            sc.build_tactile(stage, f"{prefix}/TactileLow_{tag}",
                             b1, b1 + tc["low_len"], st["y0"], st["y1"],
                             M["tactile"], z=0.0, proud=tc["proud"])
        return b1

    def build_east(M):
        return build_stair_set(M, f"{ROOT}/East", E["pad_x0"], E["pad_x1"],
                               E["kickplate"], 0)

    def build_west(M):
        """rot_group 180° — 로컬 (x,y) → 월드 (−15 − x, −y). 로컬 상부 참은
        x −1.8…0 (= 월드 −13.2…−15.0), 이후 로컬 +X 하강이 월드 −X 하강이 된다.
        기하·설비는 동측과 동일하되 **킥플레이트만 有**(규정 준수 대조군)."""
        w = PARAMS["west"]
        RG = sc.build_rot_group(stage, f"{ROOT}/WestGroup", w["pivot"], w["rot"])
        pad_len = E["pad_x1"] - E["pad_x0"]
        return build_stair_set(M, RG, -pad_len, 0.0, w["kickplate"], 1)

    # -------------------------------------------------------------------
    # 상판 방음 패널 + 종주 난간 (cue_railing)
    # -------------------------------------------------------------------
    def build_deck_rails(M):
        """[v6 판정 ⑤] 방음 난간 — 지주 분절 + 방음판/개방 베이 교대.
        구 구성(무분절 판재 1매)은 벙커 복도 + 그림자면 순흑(프레임 30~45 %)의
        직접 원인이었다. 짝수 베이 = 방음판(+상단 캡), 홀수 베이 = 개방(하부
        킥 밴드 + 세로 살 6본)으로 투광·투시를 만든다. GT 무관(난간 프림)."""
        dk = PARAMS["deck"]
        rb = PARAMS["rail_bay"]
        x0, x1 = dk["x0"], dk["x1"]
        nb = int(rb["n_bay"])
        L = (x1 - x0) / float(nb)
        zt = dk["z_top"]
        for i, ye in enumerate((dk["y0"], dk["y1"])):
            for k in range(nb + 1):                      # 지주
                BOX(f"{ROOT}/DeckRailPost_{i}_{k}",
                    (x0 + k*L, ye, zt + rb["post_h"]/2.0),
                    (rb["post_t"], rb["post_t"], rb["post_h"]), M["steel"])
            for k in range(nb):
                xa = x0 + k*L + rb["post_t"]/2.0 + rb["joint"]
                xb = x0 + (k+1)*L - rb["post_t"]/2.0 - rb["joint"]
                xc, Lx = (xa + xb)/2.0, xb - xa
                if k % 2 == 0:                           # 방음판 베이
                    BOX(f"{ROOT}/DeckPanel_{i}_{k}",
                        (xc, ye, zt + dk["panel_h"]/2.0),
                        (Lx, dk["panel_t"], dk["panel_h"]), M["panel"])
                    BOX(f"{ROOT}/DeckPanelCap_{i}_{k}",
                        (xc, ye, zt + dk["panel_h"] + rb["cap_h"]/2.0),
                        (Lx, dk["panel_t"] + 2*rb["cap_over"], rb["cap_h"]),
                        M["rail"])
                else:                                    # 개방 베이(투시·투광)
                    BOX(f"{ROOT}/DeckKick_{i}_{k}",
                        (xc, ye, zt + rb["kick_h"]/2.0),
                        (Lx, dk["panel_t"], rb["kick_h"]), M["panel"])
                    nbal = int(rb["n_baluster"])
                    bz0 = zt + rb["kick_h"]
                    bz1 = zt + dk["rail_z"] - 0.06
                    for b in range(nbal):
                        xb_ = xa + (b + 0.5) * Lx / float(nbal)
                        CYL(f"{ROOT}/DeckBal_{i}_{k}_{b}",
                            (xb_, ye, (bz0 + bz1)/2.0), rb["baluster_r"],
                            bz1 - bz0, M["rail"])
            CYL(f"{ROOT}/DeckRail_{i}",
                ((dk["x0"]+dk["x1"])/2.0, ye, dk["z_top"] + dk["rail_z"]),
                dk["rail_r"], dk["x1"]-dk["x0"], M["rail"], rotY=90.0)

    # -------------------------------------------------------------------
    # 사인 (cue_sign) — 육교 안내 sign_info
    # -------------------------------------------------------------------
    def build_signs(M):
        sg = PARAMS["sign"]
        for i, (sx, sy, yaw) in enumerate(sg["spots"]):
            sc.build_sign(stage, f"{ROOT}/Sign_{i}", sx, sy,
                          PARAMS["walk"]["z_top"], yaw, M["sign"],
                          w=sg["w"], h=sg["h"], pole_h=sg["pole_h"],
                          pole_mtl=M["pole"], back_mtl=M["signback"])

    # -------------------------------------------------------------------
    # 드레싱
    # -------------------------------------------------------------------
    def build_dressing(M):
        d = PARAMS["dress"]
        gz = PARAMS["walk"]["z_top"]
        sh = d["shelter"]
        sc.build_canopy(stage, f"{ROOT}/Shelter", sh["x0"], sh["x1"], sh["y0"],
                        sh["y1"], sh["z_roof"], sh["post_r"], M["panel"],
                        M["pole"], roof_t=0.10, base_z=gz)
        BOX(f"{ROOT}/ShelterBack",
            ((sh["x0"]+sh["x1"])/2.0, sh["y0"] + 0.10, gz + 1.10),
            (sh["x1"]-sh["x0"], 0.06, 2.20), M["glass"])
        # [v6 판정 ⑤] 측벽 2 + 노선도 패널 — "다리 4개 카포트" 오독 제거.
        for i, xe in enumerate((sh["x0"] + sh["side_inset"]/2.0,
                                sh["x1"] - sh["side_inset"]/2.0)):
            BOX(f"{ROOT}/ShelterSide_{i}",
                (xe, (sh["y0"]+sh["y1"])/2.0 - 0.35,
                 gz + sh["side_h"]/2.0),
                (sh["side_t"], (sh["y1"]-sh["y0"]) - 1.4, sh["side_h"]),
                M["glass"])
        BOX(f"{ROOT}/ShelterRoute",
            (sh["x0"] + 1.35, sh["y0"] + 0.20, gz + 1.55),
            (sh["route_w"], 0.05, sh["route_h"]), M["panel"])
        sc.build_bench(stage, f"{ROOT}/ShelterBench",
                       (sh["x0"]+sh["x1"])/2.0, sh["bench_y"], gz, M["wood"],
                       yaw=0.0)
        bx, by, bh = d["bus_pole"]
        CYL(f"{ROOT}/BusPole", (bx, by, gz + bh/2.0), 0.055, bh, M["pole"],
            col=True)
        BOX(f"{ROOT}/BusSign", (bx, by, gz + bh - 0.30), (0.06, 0.55, 0.55),
            M["panel"])
        lp = d["lamp"]
        for i, (lx, ly) in enumerate(d["lamps"]):
            base = f"{ROOT}/Lamp_{i}"
            CYL(f"{base}/Pole", (lx, ly, gz + lp["pole_h"]/2.0), lp["pole_r"],
                lp["pole_h"], M["pole"], col=True)
            sgn = 1.0 if lx < 0 else -1.0
            CYL(f"{base}/Arm", (lx + sgn*lp["arm_len"]/2.0, ly,
                                gz + lp["pole_h"] - 0.12),
                lp["arm_r"], lp["arm_len"], M["pole"], rotY=90.0)
            BOX(f"{base}/Head", (lx + sgn*lp["arm_len"], ly,
                                 gz + lp["pole_h"] - 0.18),
                (lp["head"]*1.5, lp["head"], 0.14), M["lamp"])
        # 식재대 위 가로수는 지피 상면(0.10)에, 보도 위 가로수는 보도면에.
        vsoil = PARAMS["verge"]["soil_top"]
        vx = PARAMS["walk"]["xe1"] + 0.001
        for i, (tx, ty) in enumerate(d["trees"]):
            tz = vsoil if abs(tx) >= vx else gz
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", tx, ty, tz, M["wood"],
                          M["leaf_a"], M["leaf_b"])
        for i, (bx2, by2, yaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx2, by2, gz, M["wood"],
                           yaw=yaw)
        for i, (bx2, by2) in enumerate(d["bollards"]):
            sc.build_bollard(stage, f"{ROOT}/Bollard_{i}", bx2, by2, gz,
                             mtl=M["pole"])
        build_treeband(M)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd, M["brick"],
                              M["glass"], M["parapet"],
                              window=PARAMS["window_by"].get(
                                  key, PARAMS["window"]))

    def build_treeband(M):
        """[v6 판정 C-2/C-4 · v7 판정 ⑥-2] 원경 수목 실루엣 띠.

        v6 구성(세그당 속 찬 박스 1 + 작은 블롭 1)은 **상단이 평평한 연속 판**
        이라 "도색 방음벽(초록 슬래브)"으로 읽혔다. 구조를 2층으로 바꾼다.
          · 하부 박스 = 임관 아래 덤불층. 높이 h·base_frac(0.36) 로 낮춰
            **실루엣을 만들지 않는다**(스카이라인 담당에서 제외).
          · 상부 수관 = 세그당 blobs 개의 겹치는 편구 블롭. 개체 높이를
            0.72~1.16× 지터로 흩어 **상단선이 톱니**가 되게 하고, x 를
            ±x_jit 흔들어 전후 깊이를 만든다.
          · 재질은 대기원근 저채도 회록 3종을 좌표 해시로 순환(단색 판 방지).
        접지 보증: 블롭 중심 z = gz + hj·0.62, rz = hj·0.42 →
          하단 = gz + hj·0.20 ≤ gz + h·0.36 = 박스 상면(hj ≤ 1.16 h 이므로
          0.20·1.16 h = 0.232 h < 0.36 h). 즉 **부유 블롭 0**.
        결정적 지터(인덱스 해시) — 재현성 유지."""
        tb = PARAMS["treeband"]
        import random as _random
        gz = PARAMS["ground"]["z_top"]
        far = (M["leaf_far_a"], M["leaf_far_b"], M["leaf_far_c"])
        nb = int(tb.get("blobs", 3))
        bf = float(tb.get("base_frac", 0.36))
        xj = float(tb.get("x_jit", 1.7))
        for r, (xa_, xb_, hh) in enumerate(tb["rows"]):
            n = max(2, int(round((tb["y1"] - tb["y0"]) / tb["seg"])))
            xc0 = (xa_ + xb_) / 2.0
            for k in range(n):
                ya = tb["y0"] + k * (tb["y1"] - tb["y0"]) / n
                yb = tb["y0"] + (k + 1) * (tb["y1"] - tb["y0"]) / n
                rnd = _random.Random((r * 7717) ^ (k * 3413))
                h = hh + rnd.uniform(-tb["jitter"], tb["jitter"])
                dx = rnd.uniform(-0.8, 0.8)
                BOX(f"{ROOT}/TreeBand_{r}_{k}",
                    (xc0 + dx, (ya+yb)/2.0, gz + h*bf/2.0),
                    ((xb_ - xa_) * rnd.uniform(0.8, 1.25), yb - ya + 0.6,
                     h * bf),
                    far[(k + r) % 3])
                # 수관 반경은 **띠 폭 기준**(높이 기준이 아니라) — 높이 지터가
                #   커도 x 방향으로 번져 식재대·가로수 열(x ±41.2)을 침범하지
                #   않게 한다. x 최대 확산 = x_jit 1.2 + rx 1.9 = 3.1 m.
                rw = (xb_ - xa_) * 0.5
                for j in range(nb):
                    hj = h * rnd.uniform(0.72, 1.16)
                    rx = rw * rnd.uniform(0.55, 0.95)
                    sc.add_sphere(
                        stage, f"{ROOT}/TreeBlob_{r}_{k}_{j}",
                        (xc0 + rnd.uniform(-xj, xj),
                         ya + (j + 0.5) * (yb - ya) / nb
                         + rnd.uniform(-0.7, 0.7),
                         gz + hj * 0.62),
                        (rx, rx * rnd.uniform(0.90, 1.60), hj * 0.42),
                        far[(k + r + j + 1) % 3])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_site(M)
    if cfg["cue_material_break"]:
        build_lanes(M)
    if cfg["hazard_stairs"]:
        build_deck(M)
        build_east(M)
        build_west(M)
        if cfg["cue_railing"]:
            build_deck_rails(M)
    if cfg["cue_sign"]:
        build_signs(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    VIEWS = build_views()
    _v0 = VIEWS["overview"]
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
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene11_{ts}.png")
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
