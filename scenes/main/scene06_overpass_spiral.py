# -*- coding: utf-8 -*-
"""
scene06_overpass_spiral.py — NegObs 인공씬 6호: 보행육교 나선 진입 계단
(Isaac Sim 4.5) · v5 신규(구 scene06_spiral_towerstone → scenes/archive_v3/)

유형    : R1 도심 보행육교 원형 나선 진입부 (곡률 자기폐색 축 계승)
사양서  : Docs/briefs/multi_scene_brief_v5.md §R1 + 공통 레이어 절
공통    : scene_common.py (build_helix_steps / build_arc_steps / build_helix_ramp /
          build_rot_group / build_straight_stairs / build_tactile)
세계관  : scene11_footbridge_stairs.py 와 육교 규약 공유
          (차도 아스팔트 0.045 · 연석 0.15 · 보도 paving_interlock · 가로등)

────────────────────────────────────────────────────────────────────────────
위험 본질 (= 규정 미달의 현실)
  왕복 4차로 교차부를 건너는 보행육교(데크 z=+5.0)의 원형 나선 진입부.
  나선 외측 파이프 난간이 **상부 90° 구간(방위 180~270°)에서 탈락**해 포스트만
  잔존한다. 그 구간의 개방 에지(r=3.3)는 지상까지 3.46~4.81 m(평균 4.14 m)
  낙차이며 방호가 전무하다. 난간은 나머지 210° 구간엔 멀쩡히 남아 있어
  "설비 완비"로 오독되기 쉽다.
  둘째 축 — 지상 grazing(로봇 h0.3)에서 나선은 중앙 기둥·계단 리본이 겹친
  **원통 실루엣**으로 읽혀 나선 하강(내부 5 m 보이드 + 진입 통로)이 은닉된다.
  셋째 — 나선 내측 r 0.5~1.5 환형 보이드(깊이 5 m)는 내측 난간이 있으나
  킥플레이트가 없어 로봇 시점에서 열려 있다.

GT 낙차 불변 원칙: cue_railing 토글은 난간 프림만 켜고 끈다. 나선·랜딩·데크·
  기둥의 트랜스폼과 riser/반경/방위는 어떤 토글에서도 변하지 않는다.

────────────────────────────────────────────────────────────────────────────
보행 연속성 자가 검증표 (진입 → 상행 → 데크 → 하행 → 탈출)

  #  구간                         좌표(월드, m)                     단차
  ─  ───────────────────────────  ────────────────────────────────  ──────
  1  남측 보도 접근               (x −30…0.2, y −13.0, z −0.005)    —
  2  나선 하부 진입 통로          방위 120~180° 지상(계단 없음)      0.000
     (나선 중심 C = (3.5, −13.0), 랜딩 아래 필로티 공간)
  3  하단 단 25 승단              방위 108.46~120°, 상면 z=+0.008   0.013
  4  나선 상행 26단(디딤 25단차)  riser 0.192 × 25 = 4.800          0.192/단
     (단 i 중심각 = 180 + (i+0.5)·11.53846°, 상면 = 5.0 −(i+1)·0.192)
  5  최상단 단 0 → 원형 랜딩      단 0 상면 4.808 → 랜딩 4.998      0.190
     (랜딩 = 북반원 환형 참 r 0.48…3.30, 방위 0~180°)
  6  랜딩 → 육교 데크             랜딩 4.998 → 데크 5.000           0.002
  7  데크 종주                    x 2.0…5.0, y −13.0…13.0, z 5.0    —
     (차도 y −8…8 위 유효고 = 4.65 −(−0.15) = 4.80 m)
  8  북측 계단 A 13단             y 13.0…16.9, z 5.0 → 2.504        0.192/단
  9  북측 중간참                  y 16.9…18.3, z 2.504              0.000
 10  북측 계단 B 13단             y 18.3…22.2, z 2.504 → 0.008      0.192/단
 11  북측 보도 탈출               (x 2…5, y 22.2…30, z −0.005)      0.013

  총 상승 = 총 하강 = 4.992 m. 최대 단차 0.192(정상 riser), 접속부 ≤0.013 m.

────────────────────────────────────────────────────────────────────────────
개구 4박스 규약: 이 씬에는 지면을 관통하는 공동(피트)이 없다 — 나선·데크는
  전부 지상 구조물이므로 보도/차도 슬래브는 연속 박스로 깔아도 §A-3 위배가
  아니다(공동 위를 지면이 덮는 상황 자체가 발생하지 않음).

────────────────────────────────────────────────────────────────────────────
카메라 축 주석 [v6 판정 재수정 · 감독 승인 — scene11 선례]
  v6 RT 판정: 그리드 9컷이 전부 **지상 보도**(eye y=−13, z 0.3~1.8)라 로봇
  정면에 낙차가 없었다(오히려 상승 계단). grid_views 는 "낙차 경계를 프레임
  정면에 두는" 규약이므로, 그리드를 **데크 종주축**으로 이설한다.
    원점 = 데크 남단 = 나선 개구(well) 연단 (3.5, −13.0, z 5.000)
    진행 = −Y(북 → 남, 데크 중심선 x=3.5) · eye = (3.5, −13+d, 5.0+h)
  이 축에서 로봇 정면 프로파일(x=3.5, y 감소)은
    y −13.0…−13.5 기둥머리 상면 z 5.000(데크와 **동일면 — 연속 오독의 근거**)
    y −13.5…−14.5 환형 보이드(내측 r 0.5…1.5) → 지면 −0.005 = **낙차 5.005 m**
    y −14.44     내측 난간(상면 4.456 — 데크면보다 0.54 m 아래)
    y −14.5…−16.3 나선 디딤(방위 270° 부근, 상면 ≈3.46) = 데크 대비 1.54 m 아래
    y −16.36     외측 난간 — **방위 270°가 훼손 구간(180~270) 경계**
    y < −16.3    지면 −0.005 = 낙차 5.005 m
  즉 훼손 난간 구간(180~270°)이 프레임 정면~우측에 들어오고, GT 낙차가
  h0.3/h0.9/h1.8 전 컷에 존재한다. 지상 접근(구 그리드 축)은 미장센
  `ground_graze` / `ground_approach` 로 보존한다.

카메라·태양 정합 [v7 판정 재수정 — judge_v7_rt_A.md §4]
  v6 는 **그리드 축만 옮기고 태양은 그대로 뒀다.** 그 결과 새 시선(−Y)의
  피사면(법선 +Y)이 태양 az 205 에서 lambert −0.273 = 완전 역광이 되어
  `h1.8_d2`(mean 26.3·dark 81.3 %)·`h0.9_d2`·`h1.8_d5` 3컷이 판독 불능,
  `deck_entry` 상반 70 % 암부로 떨어졌다. v7 은 셋을 함께 고친다.
  ① **태양 az 205 → 145**(offset 171.5 → 111.5) : 그리드 피사면 +0.370,
     전 미장센 컷 lambert +0.264~+0.545 = 순광(SMOKE [v7 태양] 컷별 표).
     규약 — **|시선축 피사면 법선 − 태양 az| ≤ 60°**(여기서는 55°).
  ② **d2 피치 하향** : 연단 부각(h0.9 24.2° / h1.8 42.0°)이 프레임 하단
     (pitch −10° → 28°)을 넘어 근경 지면이 통째로 프레임 밖이었다 →
     h0.9_d2 −20° · h1.8_d2 −28°. h0.3_d2 는 −10° 유지(지평선 유지 = 은닉 축).
  ③ **`spiral_up` 피치 +11 → +19°**(tgt z 2.15 → 2.75) : 프레임 상단을
     랜딩 소핏으로 막아 "원경 벽돌 파사드 60 %"를 줄인다.
  ④ **`overview` 시점 (−16,−28,14) → (−20,−16,15)** : ①로 죽는 피사면
     (법선 228°, +0.074)을 법선 207°(+0.303)로 돌린다. 나선·데크·차도·
     북측 계단의 프레임 내 포함은 yaw/부각으로 검산.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene06_overpass_spiral.py

자동 캡처 (headless):  NEGOBS_CAPTURE=1 python scene06_overpass_spiral.py
스모크(부팅 전 조기종료): NEGOBS_SMOKE=1 python scene06_overpass_spiral.py

좌표계: Z-up, m. 보행축 +X(지상 접근) · 차도축 +X · 데크축 +Y.
  나선 중심 C=(3.5, −13.0), 데크 중심선 x=3.5, 차도 중심 y=0, 보도 상면 −0.005.
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
# [A] SCENE_CONFIG — 표준 7키. hazard_stairs 만 기하 토글.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 나선·랜딩·데크·계단 제거(평탄 보도 대조군)
    "cue_railing":        True,   # 나선 난간(상부 90° 탈락 변주) + 데크 난간
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)   # 도시 관행 씬 — 승강부 점자띠 기본 ON(브리프 v5)
    "cue_material_break": True,   # 연석(화강암)·차선 도색·데크 단부 밴드
    "cue_nosing":         False,  # 나선 단코 논슬립 밴드(옵션)
    "cue_sign":           False,  # [v5.2 사용자] 임의 경고 팻말 제거 — 배치 없음(키만 예약)
    "cue_scene_dressing": True,   # 차도·가로등·가로수·정류장 폴·원경 건물
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- 나선 계단 (브리프 R1 치수 그대로) ---
    #   sweep 300° / 26단 → step_deg = 11.538462°, riser 0.192 → 낙차 4.992
    #   a0=180° : 데크 남단 모서리(= 나선 중심을 지나는 y=−13 선)가 방위 180°
    #     반경선과 정확히 일치하도록 잡은 값. 단 0[180,191.54]는 랜딩(북반원
    #     0~180)과 경계에서 접하고, 마지막 단 25[108.46,120]는 랜딩 **아래**
    #     지상에 놓여 방위 120~180°가 통째로 진입 통로로 비워진다.
    spiral=dict(cx=3.5, cy=-13.0, r_in=1.5, r_out=3.3, a0=180.0, sweep=300.0,
                n=26, riser=0.192, z0=5.0, base_drop=0.5),
    # [v6 판정 ⑤] 나선 외주 톱니(sawtooth) · 계단형 소핏 대책 — **GT 불변**.
    #   fascia : 외주 연속 페시아 링(헬리컬 밴드). 상면선 t(a)=_spiral_z_at(a)
    #     +riser*0.30 → 디딤면 대비 +0.154(단 시작) … −0.038(단 끝) 이므로
    #     디딤을 덮지 않으면서 현(chord) 계단 실루엣을 지운다. seg 0.5/deg.
    #   soffit : 하부 헬리컬 슬래브 1매(RC 나선 슬래브). 디딤 박스 저면
    #     (디딤−0.5)보다 아래로 0.2 m 더 내려가 적층 블록 저면을 가린다.
    fascia=dict(r_in=3.22, r_out=3.33, thick=0.78, z_off=0.30,
                seg_per_deg=0.5),
    soffit=dict(r_in=1.46, r_out=3.32, thick=0.34, drop=0.42,
                seg_per_deg=0.5),
    # 중앙 기둥 r0.5 (브리프). r_in 1.5 와의 사이 1.0 m 환형 보이드는 내측
    #   난간으로 방호되지만 킥플레이트가 없어 로봇 시점에선 열려 있다(부가 위험).
    column=dict(r=0.5, z_bot=-0.30, z_top=5.00),
    # 나선 상단 원형 랜딩(= 데크 남단 확폭부). 북반원만 — 남반원은 계단.
    #   r_in 0.48 : 기둥(r0.5) 안으로 2 cm 물려 코플래너 회피.
    #   top_z 4.998 : 데크 상면 5.000 과 2 mm 오프셋(§8 Z-파이팅 회피).
    landing=dict(r_in=0.48, r_out=3.30, a0=0.0, a1=180.0, seg=24,
                 top_z=4.998, base_z=4.498),
    # --- 육교 데크 (폭 3, y축 종주) ---
    #   [v6 판정 ①] 구 구성은 양측 무분절 판재 1매 → **폐합 박스거더**로 읽혔다.
    #   실물 육교는 지주 2~3 m 분절 + 방음판/개방 살대 교대. 아래 rail_bay 로
    #   베이 분절하고 홀수 베이는 **개방(세로 살)** 으로 비워 상판 너머가 비치게
    #   한다(그리드가 데크 종주축이 되었으므로 판정·학습 양쪽에 필수).
    deck=dict(x0=2.0, x1=5.0, y0=-13.0, y1=13.0, z_top=5.0, thick=0.35,
              parapet_h=1.25, parapet_t=0.08, panel_h=0.95),

    # === [W2-D ground_kit] P9 bridge_deck (spec §5.3 row "06 데크") ========
    # The h0.3 grid of this scene runs **along the deck**: origin = deck south
    # end = spiral well rim (3.5, -13.0, 5.000), travel -Y (spec §2.3 lists 06
    # explicitly). So the plan is given origin=(3.5,-13,5), axis="-y" and the
    # drop edge at s=0; the deck itself is the decorated surface, z = 5.000.
    #  * expansion joints at y = -9 / 0 / +9 (spec §5.3), driven by step_y=9.0.
    #    step_x is switched off: on this axis a constant-x line is longitudinal,
    #    not a bridge joint. NOTE - ground_kit tags constant-y lines "long" and
    #    constant-x lines "cross" regardless of `axis`, so on a -Y scene the
    #    line class is inverted and B7 does not see these joints. They are safe
    #    anyway (measured: the y=-9 joint is 33 rows @1080 from the edge row at
    #    d10, floor 16), but the mis-tagging is reported as a kit defect.
    #  * 4 scuppers at the deck edges, 0.35 m in from the parapet face.
    #  * the 논슬립 도막 밴드 (spec §5.3, width 2.0) is carried by `wear_lane`
    #    with an explicit centre line: `build_membrane` is a P6 builder whose
    #    region is the whole trimmed plan area, so it cannot express a 2.0 m
    #    band on a 3.0 m deck. Its albedo target 0.14~0.22 is a T1 material
    #    matter in any case (spec §4.4).
    #  * NO tactile: spec §12.4 puts scene06 on **hold** (the "full width" of a
    #    helical flight is undefined; supervisor call, filed with M10), so it is
    #    absent from TACTILE_SITES and ground_kit would raise B11 on it.
    gkit=dict(joint_step=9.0, wear=((3.5, -12.2), (3.5, -0.5)), wear_w=2.0,
              gully=[(2.35, -11.0), (4.65, -11.0), (2.35, -4.0), (4.65, -4.0)]),
    rail_bay=dict(post_t=0.10, post_h=1.28, n_bay=13, joint=0.05,
                  kick_h=0.12, cap_h=0.06, cap_over=0.03,
                  baluster_r=0.018, n_baluster=5),
    #   데크 지지 기둥 — 연석(y ±8.0…8.6) 바깥 보도에 착지. y ±9.0 은
    #   나선 외주(C.y −13 + r 3.3 = −9.7)에서 0.7 m 떨어져 간섭 없다.
    deck_posts=dict(x=3.5, ys=(-9.0, 9.0), r=0.35, z_bot=-0.30),
    # --- 북측 진입 계단 (rot_group 90° — 로컬 +X 하강을 월드 +Y 하강으로) ---
    #   회전: (x,y) → (16.5 − y, 9.5 + x)  [pivot (3.5,13.0), +90°]
    #   로컬 y 11.5…14.5 → 월드 x 2.0…5.0 (데크 폭 일치)
    #   로컬 x 3.5…12.7 → 월드 y 13.0…22.2
    north=dict(pivot=(3.5, 13.0), rot=90.0, x0=3.5, y0=11.5, y1=14.5,
               riser=0.192, tread=0.30, n=13, z_top=5.0, base_z=-0.30,
               land_len=1.4, cheek_t=0.22, cheek_h=0.95,
               cap_h=0.08, cap_over=0.03),
    # --- 차도 (왕복 4차로, x축) ---
    road=dict(x0=-70.0, x1=70.0, y0=-8.0, y1=8.0, z_top=-0.15, thick=0.60),
    #   차선 도색: 중앙 황색 복선 + 편도 차로 구분 백색 파선
    lane=dict(center_ys=(-0.20, 0.20), dash_ys=(-4.10, 4.10), w=0.15,
              z=-0.142, t=0.02, seg=3.0, gap=5.0, x0=-68.0, x1=68.0),
    # --- 보도(인터로킹) + 연석 ---
    #   [v6 판정 C-2] 구 폭 22 m 보도는 "개방감"이 아니라 **공터**였다(하늘과
    #   직접 맞닿는 직선 지평). 실제 4차로 가로의 보도 유효폭은 3~6 m이나
    #   나선 외주(y −16.3)를 담아야 하므로 남측 11 m / 북측 11 m 로 줄이고,
    #   그 바깥을 식재대(verge) + 가로수 열 + 원경 수목 띠로 **경계**한다.
    walk=dict(x0=-70.0, x1=70.0, ys0=-19.0, ys1=-8.0, yn0=8.0, yn1=19.0,
              z_top=-0.005, thick=0.50),
    curb=dict(w=0.60, z_top=0.0, thick=0.40),
    # --- 식재대(보도 바깥 경계) : 화강암 경계석 + 지피 상면 ---
    verge=dict(w=2.40, curb_t=0.20, curb_top=0.14, soil_top=0.10,
               x0=-70.0, x1=70.0),
    # --- 대지(지평 폐쇄용 잔디 판) ---
    #   z_top −0.16 : 차도 상면(−0.15)보다 1 cm 낮게 잡아 잔디 판이 아스팔트
    #   위로 비어져 나오지 않게 한다(보도 −0.005 대비 0.155 아래). 판 자체는
    #   ±150 까지 뻗어 §A-4 지평 폐쇄를 담당한다.
    ground=dict(x0=-150.0, x1=150.0, y0=-150.0, y1=150.0, z_top=-0.16,
                thick=1.40),
    # --- 나선 난간 (cue_railing) ---
    #   outer_r 3.36 : 외경(3.3) 바깥 6 cm. broken=(180,270) 구간은 **가로대만**
    #     제거하고 포스트는 남긴다(브리프 R1 "포스트 잔존").
    #   inner_r 1.44 : 내경(1.5) 안쪽 6 cm. 전 구간 정상.
    railing=dict(outer_r=3.36, inner_r=1.44, rail_h=1.05, mid_drop=0.50,
                 broken=(180.0, 270.0), pipe_r=0.032, post_r=0.030,
                 post_step_deg=20.0, seg_per_deg=0.25),
    # --- 점자블록 (cue_tactile) ---
    #   하부: 나선 방위 180° 진입 통로 앞(보도) / 상부: 데크 남단 승강부
    tactile=dict(low=(-0.45, 0.20, -13.95, -12.05), low_z=0.0,
                 high=(2.0, 5.0, -11.30, -10.90), high_z=5.0, proud=0.004),
    # [v5.2 사용자] 임의 경고 팻말 제거 — 계단주의 사인(PARAMS['sign']) 삭제.
    # --- 드레싱 ---
    dress=dict(
        # 가로등 (보도, 연석 안쪽 1 m). 그리드 시선축 y=−13 에서 3.4 m 이격.
        lamps=((-30.0, -9.60), (-10.0, -9.60), (18.0, -9.60), (38.0, -9.60),
               (-30.0, 9.60), (-10.0, 9.60), (18.0, 9.60), (38.0, 9.60)),
        lamp=dict(pole_h=6.0, pole_r=0.10, arm_len=1.1, arm_r=0.055, head=0.32),
        # 가로수 열 — [v6 판정 C-2] 식재대(y ∓20.2) 위 1열. 간격 7 m ±지터로
        #   보도–잔디 경계를 **선(線)** 으로 만든다(개방감 = 경계의 존재).
        #   나선 외주(y −16.3)·데크 하부는 비운다.
        trees=((-38.2, -20.2), (-31.0, -20.2), (-24.4, -20.2), (-17.6, -20.2),
               (-10.4, -20.2), (-3.6, -20.2), (10.2, -20.2),
               (17.0, -20.2), (24.2, -20.2), (31.4, -20.2), (38.0, -20.2),
               (-31.2, 20.2), (-24.0, 20.2), (-17.4, 20.2), (-10.2, 20.2),
               (3.6, 20.2), (10.4, 20.2), (17.2, 20.2), (24.0, 20.2),
               (31.0, 20.2)),
        # [v5.1 §3] 벤치는 앵커(가로수) 옆 — 평원 한복판 무앵커 금지.
        benches=((-24.4, -18.4, -6.0), (17.0, -18.4, 5.0), (-17.4, 18.4, 175.0)),
        # 볼라드 열 — 나선 진입 통로 바깥 경계(보도/차도 분리)
        bollards=((-6.0, -9.30), (-3.0, -9.30), (0.0, -9.30),
                  (9.0, -9.30), (12.0, -9.30), (15.0, -9.30)),
        # 버스 승차대 폴(정류장 표지) — 육교 세계관 공유 소품
        bus_pole=(24.0, -9.20, 3.2),
    ),
    # [v6 판정 C-2/C-4] 원경 폐쇄 — ① 건물 블록을 가로 가까이 끌어오고
    #   ② 그 앞에 **수목 실루엣 띠**(원경 LOD)를 깔아 잔디판이 하늘과 직접
    #   맞닿지 않게 한다. 띠는 개체 나무가 아니라 능선형 블록 열이므로
    #   "롤리팝 도열"이 생기지 않는다.
    #   높이 4.4~4.8(지터 ±1.2) — 데크 시점(z 5.3~6.8)에서 **눈높이 언저리**에
    #   걸리도록 잡아 지평선을 덮되 원경 건물 스카이라인은 남긴다.
    treeband=dict(rows=((-33.0, -29.0, 4.8), (29.0, 33.0, 4.4)),
                  x0=-74.0, x1=74.0, seg=7.0, jitter=1.2),
    buildings=dict(
        E=dict(x0=78.0, x1=94.0, y0=-42.0, y1=42.0, h=24.0, floors=8,
               axis="x", facade_x=78.0, face_dir=-1.0, base_z=-0.16),
        W=dict(x0=-94.0, x1=-78.0, y0=-42.0, y1=42.0, h=21.0, floors=7,
               axis="x", facade_x=-78.0, face_dir=1.0, base_z=-0.16),
        N=dict(x0=-44.0, x1=8.0, y0=34.0, y1=48.0, h=18.0, floors=6,
               axis="y", facade_y=34.0, face_dir=-1.0, base_z=-0.16),
        N2=dict(x0=14.0, x1=52.0, y0=37.0, y1=49.0, h=13.5, floors=4,
                axis="y", facade_y=37.0, face_dir=-1.0, base_z=-0.16),
        S=dict(x0=-40.0, x1=6.0, y0=-50.0, y1=-36.0, h=20.0, floors=6,
               axis="y", facade_y=-36.0, face_dir=1.0, base_z=-0.16),
        S2=dict(x0=12.0, x1=54.0, y0=-46.0, y1=-34.0, h=14.5, floors=5,
                axis="y", facade_y=-34.0, face_dir=1.0, base_z=-0.16),
    ),
    #   [v6 판정 ⑤] 창 데칼이 전 동 동일 격자로 반복돼 타일링 티가 났다 →
    #   동별 창 규격·열 간격을 달리해 리듬을 분리한다(키 = buildings 키).
    window=dict(w=1.3, h=1.7, inset=0.15, col_step=2.8, margin=2.5),
    window_by=dict(
        E=dict(w=1.5, h=1.6, inset=0.15, col_step=3.2, margin=3.0),
        W=dict(w=1.2, h=1.8, inset=0.15, col_step=2.6, margin=2.0),
        N=dict(w=1.4, h=1.5, inset=0.15, col_step=3.0, margin=2.8),
        N2=dict(w=1.1, h=1.9, inset=0.15, col_step=2.3, margin=1.8),
        S=dict(w=1.3, h=1.7, inset=0.15, col_step=2.8, margin=2.5),
        S2=dict(w=1.6, h=1.4, inset=0.15, col_step=3.4, margin=3.2),
    ),

    # --- 재질 (sRGB 감마: 어두운 상수색은 0.02~0.06 대역 — §A-1) ---
    material=dict(
        # [v6 판정 ⑤] 나선·기둥이 "갈색 목리(파티클보드)"로 읽힌 원인 =
        #   concrete_floor diff 평균 RGB (107,93,77) = 난색 갈토. 텍스처 교체
        #   없이 고치려면 ① 줄눈·타이홀이 있는 concrete_wall(141,133,111)로
        #   역할을 바꾸고 ② 틴트로 채널을 등화(等化)해 **중성 회색**을 만든다.
        #   tint (0.72,0.77,0.92) → 평균 (101,102,102) ≈ 알베도 0.40(§4 순백 금지·
        #   콘크리트 현실값). 페시아/파라펫은 조금 밝게(0.435) 잡아 층을 나눈다.
        scale=dict(paving_interlock=1.0, concrete_wall=2.0,
                   granite_dark=1.0, brick_red=2.0, grass=1.4, tactile=0.3),
        asphalt_color=(0.045, 0.045, 0.050), asphalt_rough=0.92,
        concrete_tint=(0.72, 0.77, 0.92),
        deck_tint=(0.76, 0.81, 0.97),
        parapet_tint=(0.78, 0.83, 0.99),
        soil_tint=(0.42, 0.44, 0.34),
        line_white=(0.55, 0.55, 0.52), line_yellow=(0.52, 0.40, 0.06),
        # 육교 난간 = 청록 도장 철재(한국 관행) — 훼손 대비를 위해 채도 유지
        rail_color=(0.045, 0.105, 0.115), rail_rough=0.55, rail_metallic=0.35,
        steel_color=(0.055, 0.058, 0.060), steel_rough=0.50,
        steel_metallic=0.45,
        # [v6 판정 C-3] 구 panel_rough 0.18 = 준경면 → 하늘을 통째로 반사해
        #   대면적 "순백 판"으로 렌더됐다(데크 파라펫·랜딩 파라펫). 도장 강판
        #   실물 광택으로 낮춘다(0.48).
        panel_color=(0.075, 0.095, 0.105), panel_rough=0.48,
        # 오염 밴드(기단 암화) — 파라펫·치크 하부 0.25 m 대역
        grime_color=(0.085, 0.085, 0.080), grime_rough=0.85,
        pole_color=(0.30, 0.31, 0.32), pole_metallic=0.75, pole_rough=0.35,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        # (구 상수색 파라펫 — v6 C-3 으로 텍스처 재질로 교체. 이력 보존용)
        parapet_color=(0.58, 0.58, 0.56), parapet_rough=0.60,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        leaf_a=(0.025, 0.045, 0.015), leaf_b=(0.035, 0.060, 0.020),
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
    # [v7 판정 §4 ③ — 그리드 시선축 ↔ 태양 방위 정합]
    #   구 171.5(월드 az 205, 태양이 −X·−Y 하늘)는 그리드가 **지상 접근(+X)**
    #   이던 시절의 값이다. v6 에서 그리드를 데크 종주(−Y 시선)로 이설하면서
    #   카메라를 향하는 면(법선 +Y)의 lambert 가 **−0.273 = 완전 역광**이 됐다
    #   (h1.8_d2 mean 26.3 · dark 81.3 %).
    #   신 111.5 = 월드 az **145**(태양이 −X·+Y 하늘 = 그리드 카메라 뒤 좌측).
    #     그리드 피사면(+Y향) +0.370 · deck_entry(102°향) +0.473 ·
    #     spiral_up(−X향) +0.529 · ground_approach +0.545 · broken_rail +0.340 ·
    #     ground_graze +0.264 — **전 컷 순광**(SMOKE [v7 태양] 이 컷별로 출력).
    #   규약화: 그리드 시선축의 피사면 법선(= 시선 +180°)과 태양 az 의 차이를
    #     ±60° 안으로 유지한다. 여기서는 |90 − 145| = 55°.
    #   그림자 방위 = az − 180 = −35° → 그림자가 +X·−Y(시선 진행방향 = 화면
    #     안쪽)로 떨어져 근경 데크면을 덮지 않는다.
    SUN_AZ_OFFSET=111.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene06")
ASSET_ROLES = ["paving_interlock", "concrete_wall", "granite_dark",
               "brick_red", "grass", "tactile",   # [v5.2 사용자] 임의 경고 팻말 제거
               "hdri", "mdl"]


def _step_deg():
    sp = PARAMS["spiral"]
    return sp["sweep"] / float(sp["n"])


def _spiral_top_z(i):
    """단 i(0-based) 디딤면 z."""
    sp = PARAMS["spiral"]
    return sp["z0"] - (i + 1) * sp["riser"]


def _spiral_mid_deg(i):
    """단 i 중심 방위(도, ccw)."""
    return PARAMS["spiral"]["a0"] + (i + 0.5) * _step_deg()


def _spiral_z_at(a_deg):
    """방위 a 에서 디딤면 연속 근사 z (난간 상면 산출 공용)."""
    sp = PARAMS["spiral"]
    t = (a_deg - sp["a0"]) / _step_deg()
    return sp["z0"] - sp["riser"] * (t + 0.5)


def _fascia_span():
    """페시아·소핏 링의 방위 구간 = 나선 전 구간 [a0, a0+sweep]."""
    sp = PARAMS["spiral"]
    return (sp["a0"], sp["a0"] + sp["sweep"])


def _fascia_z(a_deg):
    """페시아 상면선 t(a) = 디딤 연속선 + riser·z_off.
    단 i 구간 안에서 t(a) − 디딤면 ∈ [−riser·(0.5−z_off), +riser·(0.5+z_off)]
    → z_off 0.30 이면 +0.154(단 시작) … −0.038(단 끝). 디딤을 덮지 않고
    현(chord) 톱니만 지운다(교훈: GT 디딤 z 는 불변)."""
    sp = PARAMS["spiral"]
    return _spiral_z_at(a_deg) + sp["riser"] * PARAMS["fascia"]["z_off"]


# ===========================================================================
# [C1b] 카메라 검산 기반 — AABB 장애물 + 솔리드 조회(레이마칭 단일 출처)
#   [v6 판정 지시] 그리드 축 이설·미장센 재조준의 근거를 좌표로 검산한다.
#   scene08 `_obstacle_boxes` / `_solid_at` 규약을 그대로 따른다.
# ===========================================================================
def _north_local(x, y):
    """월드 → 북측 계단 rot_group(+90° @ pivot) 로컬 좌표 역변환.
    정변환 (lx,ly) → (px−(ly−py), py+(lx−px)) 의 역: lx = px+(wy−py),
    ly = py−(wx−px)."""
    px, py = PARAMS["north"]["pivot"]
    return (px + (y - py), py - (x - px))


def _north_top(lx):
    """북측 계단 로컬 x 에서의 상면 z(계단식). 범위 밖이면 None."""
    no = PARAMS["north"]
    runA = no["n"] * no["tread"]
    z_mid = no["z_top"] - no["n"] * no["riser"]
    a0, a1 = no["x0"], no["x0"] + runA
    m1 = a1 + no["land_len"]
    b1 = m1 + runA
    if lx < a0 or lx > b1:
        return None
    if lx <= a1:
        i = min(no["n"], int((lx - a0) / no["tread"]) + 1)
        return no["z_top"] - i * no["riser"]
    if lx <= m1:
        return z_mid
    i = min(no["n"], int((lx - m1) / no["tread"]) + 1)
    return z_mid - i * no["riser"]


def _spiral_top_at(r, az_raw):
    """반경 r·방위 az(0~360)에서 나선 디딤 상면 z. 계단 밖이면 None."""
    sp = PARAMS["spiral"]
    if not (sp["r_in"] <= r <= sp["r_out"]):
        return None
    sd = _step_deg()
    for a in (az_raw, az_raw + 360.0):
        t = (a - sp["a0"]) / sd
        if -1e-9 <= t < sp["n"]:
            return _spiral_top_z(int(t))
    return None


def _in_sweep(az_raw):
    """방위가 나선 전개 구간 [a0, a0+sweep] 에 드는지 → 연속 파라미터 a 반환."""
    sp = PARAMS["spiral"]
    for a in (az_raw, az_raw + 360.0):
        if sp["a0"] - 1e-9 <= a <= sp["a0"] + sp["sweep"] + 1e-9:
            return a
    return None


def _solid_at(x, y, z):
    """점 (x,y,z)를 품는 지형·구조 솔리드 이름(없으면 None).
    카메라 eye 매몰 + 시선 차단(ray march) 검사의 단일 출처."""
    sp = PARAMS["spiral"]
    dk = PARAMS["deck"]
    la = PARAMS["landing"]
    wk = PARAMS["walk"]
    rd = PARAMS["road"]
    g = PARAMS["ground"]
    fa, so = PARAMS["fascia"], PARAMS["soffit"]
    # ── 지반·차도·보도·연석·식재대 ──
    if g["x0"] <= x <= g["x1"] and g["y0"] <= y <= g["y1"] \
            and g["z_top"] - g["thick"] <= z <= g["z_top"]:
        return "Ground"
    if rd["x0"] <= x <= rd["x1"] and rd["y0"] <= y <= rd["y1"] \
            and rd["z_top"] - rd["thick"] <= z <= rd["z_top"]:
        return "Road"
    for tag, ya, yb in (("Walk_S", wk["ys0"], wk["ys1"]),
                        ("Walk_N", wk["yn0"], wk["yn1"])):
        if wk["x0"] <= x <= wk["x1"] and ya <= y <= yb \
                and wk["z_top"] - wk["thick"] <= z <= wk["z_top"]:
            return tag
    vg = PARAMS["verge"]
    for tag, ya, yb in (("Verge_S", wk["ys0"] - vg["w"], wk["ys0"]),
                        ("Verge_N", wk["yn1"], wk["yn1"] + vg["w"])):
        if vg["x0"] <= x <= vg["x1"] and ya <= y <= yb \
                and -0.30 <= z <= vg["curb_top"]:
            return tag
    # ── 나선·기둥·랜딩 ──
    r = math.hypot(x - sp["cx"], y - sp["cy"])
    az = math.degrees(math.atan2(y - sp["cy"], x - sp["cx"])) % 360.0
    co = PARAMS["column"]
    if r <= co["r"] and co["z_bot"] <= z <= co["z_top"]:
        return "Column"
    if la["r_in"] <= r <= la["r_out"] and la["a0"] <= az <= la["a1"] \
            and la["base_z"] <= z <= la["top_z"]:
        return "Landing"
    top = _spiral_top_at(r, az)
    if top is not None and top - sp["base_drop"] <= z <= top:
        return "SpiralStep"
    a_c = _in_sweep(az)
    if a_c is not None:
        tz = _fascia_z(a_c)
        if fa["r_in"] <= r <= fa["r_out"] and tz - fa["thick"] <= z <= tz:
            return "SpiralFascia"
        sz = tz - so["drop"]
        if so["r_in"] <= r <= so["r_out"] and sz - so["thick"] <= z <= sz:
            return "SpiralSoffit"
    # ── 데크·지지 기둥·데크 난간 ──
    if dk["x0"] <= x <= dk["x1"] and dk["y0"] <= y <= dk["y1"] \
            and dk["z_top"] - dk["thick"] <= z <= dk["z_top"]:
        return "Deck"
    dp = PARAMS["deck_posts"]
    for i, py in enumerate(dp["ys"]):
        if math.hypot(x - dp["x"], y - py) <= dp["r"] \
                and dp["z_bot"] <= z <= dk["z_top"] - dk["thick"]:
            return f"DeckPost_{i}"
    rb = PARAMS["rail_bay"]
    for i, xe in enumerate((dk["x0"], dk["x1"])):
        if abs(x - xe) <= max(dk["parapet_t"], rb["post_t"]) / 2.0 \
                and dk["y0"] <= y <= dk["y1"] \
                and dk["z_top"] <= z <= dk["z_top"] + rb["post_h"]:
            return f"DeckRail_{i}"
    # ── 북측 계단(회전군) ──
    no = PARAMS["north"]
    lx, ly = _north_local(x, y)
    if no["y0"] <= ly <= no["y1"]:
        nt = _north_top(lx)
        if nt is not None and no["base_z"] <= z <= nt:
            return "NorthStair"
    # ── 원경 수목 띠 · 건물 ──
    tb = PARAMS["treeband"]
    for ri, (ya, yb, hh) in enumerate(tb["rows"]):
        if tb["x0"] <= x <= tb["x1"] and ya - 1.0 <= y <= yb + 1.0 \
                and g["z_top"] <= z <= g["z_top"] + hh + tb["jitter"]:
            return f"TreeBand_{ri}"
    for key, bd in PARAMS["buildings"].items():
        if bd["x0"] <= x <= bd["x1"] and bd["y0"] <= y <= bd["y1"] \
                and bd.get("base_z", 0.0) - 1.0 <= z \
                <= bd.get("base_z", 0.0) + bd["h"]:
            return f"Building_{key}"
    return None


def _obstacle_boxes():
    """카메라 충돌 검사용 드레싱·난간 AABB (name, x0,x1, y0,y1, z0,z1).
    지형·구조 솔리드는 `_solid_at` 이 담당하므로 여기엔 얇은 프림만 넣는다."""
    d = PARAMS["dress"]
    gz = PARAMS["walk"]["z_top"]
    boxes = []
    lp = d["lamp"]
    for i, (lx, ly) in enumerate(d["lamps"]):
        boxes.append((f"Lamp_{i}", lx - 0.6, lx + 0.6, ly - 1.3, ly + 1.3,
                      gz, gz + lp["pole_h"]))
    for i, (tx, ty) in enumerate(d["trees"]):
        boxes.append((f"Tree_{i}", tx - 1.1, tx + 1.1, ty - 1.1, ty + 1.1,
                      gz, gz + 4.2))
    for i, (bx, by, _yaw) in enumerate(d["benches"]):
        boxes.append((f"Bench_{i}", bx - 1.0, bx + 1.0, by - 0.4, by + 0.4,
                      gz, gz + 0.5))
    for i, (bx, by) in enumerate(d["bollards"]):
        boxes.append((f"Bollard_{i}", bx - 0.1, bx + 0.1, by - 0.1, by + 0.1,
                      gz, gz + 0.75))
    bx, by, bh = d["bus_pole"]
    boxes.append(("BusPole", bx - 0.1, bx + 0.1, by - 0.3, by + 0.3, gz,
                  gz + bh))
    dk = PARAMS["deck"]
    rb = PARAMS["rail_bay"]
    for i, xe in enumerate((dk["x0"], dk["x1"])):
        boxes.append((f"DeckRail_{i}", xe - 0.09, xe + 0.09, dk["y0"], dk["y1"],
                      dk["z_top"], dk["z_top"] + rb["post_h"]))
    # 나선 난간(파이프 r0.03·포스트 r0.03)은 두께가 카메라 반경보다 얇아
    #   AABB 충돌 검사 대상에서 제외한다(링 형상이라 사각 AABB 는 거짓양성).
    return boxes


# ===========================================================================
# [C2] 스모크 — 부팅 전 기하 자기검증 (조기종료)
# ===========================================================================
def _smoke_report():
    sp = PARAMS["spiral"]
    dk = PARAMS["deck"]
    la = PARAMS["landing"]
    no = PARAMS["north"]
    rl = PARAMS["railing"]
    sd = _step_deg()
    drop = sp["n"] * sp["riser"]
    print("=" * 68)
    print("scene06_overpass_spiral — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 68)
    print(f"  나선: r_in {sp['r_in']} / r_out {sp['r_out']} / sweep {sp['sweep']}° "
          f"/ {sp['n']}단 · step {sd:.6f}°")
    print(f"    riser {sp['riser']} × {sp['n']} = 낙차 {drop:.3f} m  "
          f"(z0 {sp['z0']:.3f} → 단{sp['n']-1} 상면 {_spiral_top_z(sp['n']-1):+.3f})")
    r_w = sp["r_in"] + (2.0 / 3.0) * (sp["r_out"] - sp["r_in"])
    tread_w = r_w * math.radians(sd)
    chord = 2.0 * sp["r_out"] * math.sin(math.radians(sd) / 2.0) * 1.03
    arc_out = sp["r_out"] * math.radians(sd)
    print(f"    walkline r_w {r_w:.3f} → tread {tread_w:.4f} m, 2R+T = "
          f"{2*sp['riser']+tread_w:.3f}")
    print(f"    세그 현길이(외경×1.03) {chord:.4f} ≥ 외경 호 {arc_out:.4f} → "
          f"{'OK' if chord >= arc_out else 'FAIL'} (교훈 4 쐐기 틈)")
    print(f"    단 0  방위 [{sp['a0']:.2f}, {sp['a0']+sd:.2f}]  상면 "
          f"{_spiral_top_z(0):+.3f}")
    print(f"    단 {sp['n']-1} 방위 [{(sp['a0']+(sp['n']-1)*sd) % 360:.2f}, "
          f"{(sp['a0']+sp['n']*sd) % 360:.2f}]  상면 "
          f"{_spiral_top_z(sp['n']-1):+.3f}")
    # ── 진입 통로: 계단이 점유하지 않는 방위 대역 ──
    free0 = (sp["a0"] + sp["sweep"]) % 360.0          # 120°
    free1 = sp["a0"] % 360.0                          # 180°
    print(f"  [진입 통로] 지상 무단(無段) 방위 [{free0:.2f}, {free1:.2f}] "
          f"= {free1-free0:.1f}° — 랜딩(z {la['top_z']:.3f}) 아래 필로티")
    print(f"    통로 유효고 = 랜딩 저면 {la['base_z']:.3f} − 지면 "
          f"{PARAMS['walk']['z_top']:+.3f} = "
          f"{la['base_z']-PARAMS['walk']['z_top']:.3f} m → "
          f"{'OK' if la['base_z']-PARAMS['walk']['z_top'] > 2.1 else 'FAIL'}")
    # ── 보행 연속성 표 ──
    print("  [보행 연속성 검증표]")
    rows = [
        ("남측 보도 → 진입 통로", PARAMS["walk"]["z_top"], PARAMS["walk"]["z_top"]),
        ("진입 통로 → 하단 단", PARAMS["walk"]["z_top"], _spiral_top_z(sp["n"]-1)),
        # 단 25 상면 → 단 0 상면 사이의 단차 수는 (n−1). 나머지 1 riser 분은
        #   "단 0 → 랜딩"(0.190) 이 담당한다 — 지면→랜딩 총 상승 5.003 m.
        ("나선 상행(디딤 25단차)", _spiral_top_z(sp["n"]-1), _spiral_top_z(0)),
        ("단 0 → 원형 랜딩", _spiral_top_z(0), la["top_z"]),
        ("랜딩 → 데크", la["top_z"], dk["z_top"]),
        ("데크 → 북측 계단 A", dk["z_top"], dk["z_top"] - no["n"]*no["riser"]),
        ("북측 중간참", dk["z_top"] - no["n"]*no["riser"],
         dk["z_top"] - no["n"]*no["riser"]),
        ("북측 계단 B", dk["z_top"] - no["n"]*no["riser"],
         dk["z_top"] - 2*no["n"]*no["riser"]),
        ("북측 보도 탈출", dk["z_top"] - 2*no["n"]*no["riser"],
         PARAMS["walk"]["z_top"]),
    ]
    bad = 0
    for nm, z0, z1 in rows:
        d = abs(z1 - z0)
        # 계단 구간은 단수로 나눈 riser 가 판정 대상
        if "상행" in nm or "계단" in nm:
            ok = abs(d - ((sp["n"]-1)*sp["riser"] if "상행" in nm
                          else no["n"]*no["riser"])) < 1e-6
        else:
            ok = d <= 0.20
        bad += 0 if ok else 1
        print(f"    {nm:22s} z {z0:+.3f} → {z1:+.3f}  Δ{d:+.3f}  "
              f"{'OK' if ok else 'FAIL'}")
    print(f"    연속성 판정: {'OK' if bad == 0 else f'FAIL({bad})'}")
    # ── 위험(난간 탈락 구간) ──
    b0, b1 = rl["broken"]
    z_b0, z_b1 = _spiral_z_at(b0), _spiral_z_at(b1)
    gz = PARAMS["walk"]["z_top"]
    print(f"  [위험] 외측 난간 탈락 방위 [{b0:.0f}, {b1:.0f}] (상부 {b1-b0:.0f}°)")
    print(f"    개방 에지 z {z_b0:+.3f} … {z_b1:+.3f} → 지면 {gz:+.3f} 낙차 "
          f"{z_b0-gz:.3f} … {z_b1-gz:.3f} (평균 {(z_b0+z_b1)/2-gz:.3f} m)")
    print(f"    낙차 ≥ 0.3 m → {'OK' if (z_b1-gz) >= 0.3 else 'FAIL'}  "
          f"· 포스트는 잔존(가로대만 결손)")
    print(f"    내측 보이드: r {PARAMS['column']['r']:.2f}…{sp['r_in']:.2f} "
          f"(폭 {sp['r_in']-PARAMS['column']['r']:.2f}), 깊이 최대 "
          f"{_spiral_top_z(0)-gz:.3f} m — 내측 난간 有/킥플레이트 無")
    # ── 데크 유효고 · 기둥 간섭 ──
    deck_bot = dk["z_top"] - dk["thick"]
    print(f"  [데크] 상면 {dk['z_top']:.2f} 저면 {deck_bot:.2f} · 차도 상면 "
          f"{PARAMS['road']['z_top']:+.2f} → 유효고 "
          f"{deck_bot-PARAMS['road']['z_top']:.2f} m "
          f"{'OK' if deck_bot-PARAMS['road']['z_top'] >= 4.5 else 'FAIL'}")
    dp = PARAMS["deck_posts"]
    for py in dp["ys"]:
        dist = math.hypot(dp["x"] - sp["cx"], py - sp["cy"])
        clr = dist - sp["r_out"] - dp["r"]
        print(f"    지지 기둥 y={py:+.1f} → 나선 중심 거리 {dist:.3f}, "
              f"외주 여유 {clr:+.3f} {'OK' if clr > 0 else 'FAIL'}")
    # ── rot_group 90° 좌표 검산 (북측 계단) ──
    px, py = no["pivot"]

    def _rot90(x, y):
        return (px - (y - py), py + (x - px))
    runA = no["n"] * no["tread"]
    locs = [("계단A 상단", no["x0"], no["y0"]), ("계단A 하단", no["x0"]+runA, no["y1"]),
            ("중간참 끝", no["x0"]+runA+no["land_len"], no["y0"]),
            ("계단B 하단", no["x0"]+2*runA+no["land_len"], no["y1"])]
    print("  [북측 rot_group 90° 검산]  (x,y) → (16.5−y, 9.5+x)")
    for nm, lx, ly in locs:
        wx, wy = _rot90(lx, ly)
        print(f"    {nm:10s} 로컬({lx:6.2f},{ly:6.2f}) → 월드({wx:6.2f},{wy:6.2f})")
    # 치크 파라펫 매입 검산(경사 박스 — 계단선과 평행)
    angn = math.atan2(no["n"]*no["riser"], runA)
    ct = 1.5 * math.cos(angn)
    pb_top = no["z_top"] + no["cheek_h"] - ct
    pb_bot = pb_top - no["n"]*no["riser"]
    print(f"    치크 파라펫: 경사 {math.degrees(angn):.2f}° · thick 1.5 → "
          f"밑면 {pb_top:+.3f}(1단 디딤 {no['z_top']-no['riser']:+.3f} 아래 "
          f"{'OK' if pb_top < no['z_top']-no['riser'] else 'FAIL'}) … "
          f"{pb_bot:+.3f}(참 {no['z_top']-no['n']*no['riser']:+.3f} 아래 "
          f"{'OK' if pb_bot < no['z_top']-no['n']*no['riser'] else 'FAIL'})")
    print(f"    치크 y대역 [{no['y0']:.2f},{no['y0']+no['cheek_t']:.2f}] / "
          f"[{no['y1']-no['cheek_t']:.2f},{no['y1']:.2f}] ⊂ 계단 폭 "
          f"[{no['y0']:.2f},{no['y1']:.2f}] → "
          f"{'OK' if 2*no['cheek_t'] < (no['y1']-no['y0']) else 'FAIL'}")
    wx0, _ = _rot90(no["x0"], no["y1"])
    wx1, _ = _rot90(no["x0"], no["y0"])
    print(f"    계단 폭 월드 x [{min(wx0,wx1):.2f}, {max(wx0,wx1):.2f}] ⊂ 데크 "
          f"[{dk['x0']:.2f}, {dk['x1']:.2f}] → "
          f"{'OK' if abs(min(wx0,wx1)-dk['x0'])<1e-6 and abs(max(wx0,wx1)-dk['x1'])<1e-6 else 'FAIL'}")
    # ── 그리드 카메라 vs 신설 기하 좌표 검산 [v6 재수정: 데크 종주축] ──
    gx, gy, gz = _grid_shift()
    print(f"  [그리드] 원점 = 데크 남단 = 나선 개구 연단 "
          f"(x {gx:.2f}, y {gy:.2f}, z {gz:.3f}) · 진행 −Y")
    dk = PARAMS["deck"]
    for d in (2, 5, 10):
        ey = gy + d
        on_deck = dk["y0"] <= ey <= dk["y1"] and dk["x0"] <= gx <= dk["x1"]
        print(f"    d={d:2d}  eye ({gx:+.2f}, {ey:+.2f}, "
              f"{gz+0.3:.2f}~{gz+1.8:.2f}) · 데크 위 "
              f"{'OK' if on_deck else 'FAIL'}")
    print(f"    시선 회랑(데크 x {dk['x0']:.1f}…{dk['x1']:.1f} / 나선 r≤4.2) "
          f"드레싱 침입: {_corridor_hits()} 개 → "
          f"{'OK' if _corridor_hits() == 0 else 'FAIL'}")

    # ── 정면 프로파일(그리드 축 x=3.5, y 감소) — 낙차 GT 가 프레임에 있는가 ──
    print("  [정면 프로파일] 그리드 축 x=3.50 · y −13.0 → −18.0 (0.25 m 간격)")
    gzw = PARAMS["walk"]["z_top"]
    prof = []
    yy = gy
    while yy >= gy - 5.0:
        top = None
        zz = 6.0
        while zz > -0.60:                      # 위에서 아래로 첫 솔리드 상면
            if _solid_at(gx, yy, zz) is not None:
                top = zz
                break
            zz -= 0.01
        prof.append((yy, top))
        yy -= 0.25
    for yy, top in prof:
        if top is None:
            print(f"    y {yy:+6.2f}  상면 없음(개방) → 지면 {gzw:+.3f} "
                  f"낙차 {gz-gzw:.3f} m")
        else:
            print(f"    y {yy:+6.2f}  상면 {top:+.3f}  (데크면 대비 "
                  f"{top-gz:+.3f})")
    dmax = max((gz - (t if t is not None else gzw)) for _, t in prof)
    print(f"    프로파일 최대 낙차 {dmax:.3f} m ≥ 0.3 → "
          f"{'OK(낙차 GT 프레임 내)' if dmax >= 0.3 else 'FAIL'}")

    # ── h0.3 은닉 검산 (연근 연단 스침 시선) ──
    print("  [h0.3 은닉 검산] 데크 연단(y=−13.0, z 5.000) 스치는 시선")
    for d in (2.0, 5.0, 10.0):
        drop = gz - gzw
        y_hit = gy - drop * d / 0.3
        print(f"    d={d:4.1f} m → 지면 재출현 y {y_hit:8.1f} "
              f"(연단에서 {abs(y_hit-gy):.1f} m 밖) · 그 사이 "
              f"{'전 구간 은닉 OK' if abs(y_hit-gy) > 16.3 else 'FAIL'}")
    print("    ⇒ 나선 개구·디딤·지면이 전부 시선 아래로 숨고 기둥머리 상면"
          "(5.000, 데크 동일면)만 남는다 = negative obstacle 성립")

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
    print("      ※ preset_* 그리드는 pitch −10°(d2 의 h0.9/h1.8 은 v7 에서")
    print("        −20/−28°)로 **바닥을 겨냥**하는 규약이라 tgt 가 데크면")
    print("        아래에 놓인다 — 차단 검사 대상이 아니다.")
    blocked = []
    for name, v in sorted(views.items()):
        if name.startswith("preset_"):
            continue
        e = np.array(v["eye"], dtype=float)
        tg = np.array(v["tgt"], dtype=float)
        Ln = float(np.linalg.norm(tg - e))
        frac, hit = 1.0, None
        for k in range(1, int(Ln / 0.1) + 1):
            f = k * 0.1 / Ln
            s = _solid_at(*(e + (tg - e) * f))
            if s is not None:
                frac, hit = f, s
                break
        ok = frac >= 0.90
        print(f"      {name:18s} 첫 차단 {frac:5.2f} "
              f"({hit if hit else '없음'}) → {'OK' if ok else 'FAIL'}")
        if not ok:
            blocked.append(name)
    print(f"      차단 컷: {blocked if blocked else '없음 → OK'}")

    # ── [v7] 시선축 ↔ 태양 방위 정합 (컷별 lambert) ──
    #   교훈(judge_v7): 축을 옮기면 태양도 같이 옮겨야 한다. 면별 표만으로는
    #   "어느 컷이 역광인가"를 못 잡는다 → **컷별 피사면 법선**으로 뽑는다.
    azd = 33.5 + float(PARAMS["SUN_AZ_OFFSET"])
    el = math.radians(float(PARAMS["light"]["noon_sun_elev"]))
    lx = math.cos(math.radians(azd)) * math.cos(el)
    ly = math.sin(math.radians(azd)) * math.cos(el)
    lz = math.sin(el)
    print(f"  [v7 태양] offset {PARAMS['SUN_AZ_OFFSET']:.1f} → 월드 az "
          f"{azd:.1f}° (그림자 az {azd - 180:.1f}°) · 고도 "
          f"{math.degrees(el):.2f}°")
    for nm, N in (("+Y향(그리드 피사면)", (0, 1, 0)),
                  ("−X향(spiral_up 피사면)", (-1, 0, 0)),
                  ("−Y향(데크 남단 페시아)", (0, -1, 0)),
                  ("+X향", (1, 0, 0)),
                  ("상면(데크·디딤·지면)", (0, 0, 1))):
        d = N[0] * lx + N[1] * ly + N[2] * lz
        print(f"    {nm:<24} lambert {d:+.3f} "
              f"{'순광' if d > 0.15 else ('터미네이터' if d > 0 else '음영')}")
    print("    [컷별] 시선 방위 → 피사면 법선(시선+180°) 의 직사광 lambert")
    worst = None
    for name, vv in sorted(views.items()):
        e, t = vv["eye"], vv["tgt"]
        gaze = math.degrees(math.atan2(t[1] - e[1], t[0] - e[0])) % 360.0
        nrm = (gaze + 180.0) % 360.0
        lam = math.cos(math.radians(nrm - azd)) * math.cos(el)
        if name.startswith("preset_") and name != "preset_h0.3_d2":
            continue                      # 그리드 9컷은 축이 동일 — 대표 1컷
        tag = "그리드 대표" if name.startswith("preset_") else ""
        worst = lam if worst is None else min(worst, lam)
        print(f"      {name:<16} 시선 {gaze:6.1f}° · 법선 {nrm:6.1f}° · "
              f"lambert {lam:+.3f} {'순광' if lam > 0.15 else '역광/터미네이터'}"
              f" {tag}")
    print(f"      최저 컷 lambert {worst:+.3f} (>0.15 = 전 컷 순광 → "
          f"{'OK' if worst > 0.15 else 'CHECK'})")
    dk = PARAMS["deck"]
    rb = PARAMS["rail_bay"]
    sdx = -math.cos(math.radians(azd)) * math.cos(el) / math.sin(el)
    sdy = -math.sin(math.radians(azd)) * math.cos(el) / math.sin(el)
    x_sh = dk["x0"] + sdx * rb["post_h"]
    print(f"    [근경 데크 그림자] 서측 난간(x {dk['x0']:.1f}, h "
          f"{rb['post_h']:.2f}) 그림자 → x {x_sh:+.2f} (데크 폭 "
          f"{dk['x0']:.1f}…{dk['x1']:.1f} 중 "
          f"{max(0.0, x_sh - dk['x0']) / (dk['x1'] - dk['x0']) * 100:.0f} % "
          f"점유) · y 이동 {sdy * rb['post_h']:+.2f}(시선 진행방향)")

    # ── [v7] d2 프리셋 프레이밍 : 낙차 GT 가 프레임 안에 있는가 ──
    #   수직 반화각 18.0°(초점 18.147 / 수직 애퍼처 11.787). 부각 dep 인 대상은
    #   |−pitch − dep| ≤ 18 일 때 프레임 안.
    print("  [v7 프레이밍] d2 프리셋 (연단 2.0 m 앞) — 피치 하향 근거")
    gzw = PARAMS["walk"]["z_top"]
    for h, pit in ((0.3, -10.0), (0.9, -20.0), (1.8, -28.0)):
        row = []
        for nm, ahead, dz, need in (("연단", 2.0, h, True),
                                    ("디딤(방위270°)", 5.0, h + 1.540, True),
                                    ("보이드 저면", 3.5, h + gz - gzw, False)):
            dep = math.degrees(math.atan2(dz, ahead))
            ok = abs(-pit - dep) <= 18.0
            mark = ("OK" if ok else "밖") if need else ("밖=은닉" if not ok
                                                       else "노출")
            row.append(f"{nm} {dep:5.1f}°[{mark}]")
        print(f"    h{h}_d2 pitch {pit:+.0f}° (프레임 {-pit - 18:.1f}…"
              f"{-pit + 18:.1f}° 부각) : " + " · ".join(row))
    print("    ※ 보이드 저면(5.0 m 아래)이 프레임 밖인 것은 결함이 아니라 이 씬의")
    print("      GT 그 자체 — 연단·디딤만 보이고 바닥은 안 보이는 것이 은닉이다.")
    print("    ※ h0.3 은 연단 부각 8.5° 로 −10° 유지 — 피치를 내리면 지평선이")
    print("      프레임 밖이 되어 grazing 연속 평면 오독(GT 양성 축)이 깨진다.")
    print("=" * 68)


def _grid_shift():
    """[v6 재수정 · 감독 승인] 그리드 원점 = **데크 남단 = 나선 개구 연단**
    (3.5, −13.0, 5.000). 구 원점(나선 외주 서단, 지상)은 로봇 정면에 낙차가
    없어 h0.3 은닉 판정 자체가 불가능했다 — scene11 선례와 동일 논거."""
    dk = PARAMS["deck"]
    return ((dk["x0"] + dk["x1"]) / 2.0, dk["y0"], dk["z_top"])


def _to_world(p, org):
    """grid_views 로컬(+X 진행, 원점 0) → 월드(−Y 진행, 원점 org) 매핑.
    회전 R = rotZ(−90°): (lx, ly) → (ly, −lx). 로컬 eye(−d, 0, h) 는
    월드 (gx, gy+d, gz+h) 가 되어 원점 북쪽 d 지점·데크면 위 h 에 선다."""
    gx, gy, gz = org
    lx, ly, lz = p
    return [gx + ly, gy - lx, gz + lz]


def _corridor_hits():
    """[v6 재수정] 시선 회랑 = ① 데크 종주 회랑(x 2…5, y −13…13, 그리드 축)
    ② 나선 개구 전면(중심에서 r ≤ 4.2 — h0.3 근경 프레임).
    드레싱(가로수·가로등·볼라드·벤치·정류장 폴)이 여기 들어오면 낙차 판독을
    가린다 → 0 이어야 한다."""
    d = PARAMS["dress"]
    sp = PARAMS["spiral"]
    dk = PARAMS["deck"]
    pts = list(d["trees"]) + [(x, y) for x, y in d["lamps"]] \
        + [(x, y) for x, y in d["bollards"]] \
        + [(b[0], b[1]) for b in d["benches"]] + [d["bus_pole"][:2]]
    n = 0
    for x, y in pts:
        if dk["x0"] <= x <= dk["x1"] and dk["y0"] <= y <= dk["y1"]:
            n += 1
        elif math.hypot(x - sp["cx"], y - sp["cy"]) <= 4.2:
            n += 1
    return n


# ===========================================================================
# [D] 카메라 프리셋 — grid_views(지상 접근, +X) + 미장센 5컷
# ===========================================================================
def build_views():
    """[v6 재수정] 그리드를 **데크 종주축(−Y)** 으로 이설(감독 승인).
    원점 = 데크 남단 (3.5, −13.0, 5.000) = 나선 개구(well) 연단.
    eye = (3.5, −13+d, 5.0+h) · 시선 −Y · pitch −10°.
    로봇 h0.3 에서 기둥머리 상면(5.000, 데크와 동일면)과 원측 지면이 하나의
    연속 평면으로 읽혀 환형 보이드(낙차 5.005 m)와 나선 하강이 은닉되는지가
    판정 1순위. 지상 접근은 ground_approach / ground_graze 로 보존."""
    org = _grid_shift()
    # [v7 판정 §4 ③ ㉡] d2 프리셋 피치 하향 — **근경 지면이 프레임 밖** 문제.
    #   수직 반화각 18.0° · pitch −10° → 프레임 하단 −28°. 연단까지 2 m 인
    #   d2 에서 연단 부각은 h0.9 → 24.2° · h1.8 → **42.0°** 이므로 h1.8 은
    #   데크면·연단·개구가 통째로 프레임 아래로 빠지고 배경 암부만 남았다.
    #   → d2 만 pitch 를 내려 **연단과 환형 보이드를 프레임에 넣는다**:
    #        h0.9_d2 −20°(하단 38.0° > 24.2°) · h1.8_d2 −28°(하단 46.0° > 42.0°)
    #   h0.3_d2 는 −10° 유지 — 연단 부각이 8.5° 뿐이고, 피치를 내리면 지평선이
    #   프레임 밖으로 나가 **grazing 연속 평면 오독**(이 씬의 GT 양성 축)이
    #   깨진다. d5/d10 은 전 높이 −10° 유지(부각 ≤ 24°).
    v = sc.grid_views(0.0, dists=(5, 10))
    v.update(sc.grid_views(0.0, heights=(0.3,), dists=(2,)))
    v.update(sc.grid_views(0.0, heights=(0.9,), dists=(2,), pitch=-20))
    v.update(sc.grid_views(0.0, heights=(1.8,), dists=(2,), pitch=-28))
    out = {}
    for k, val in v.items():
        out[k] = dict(eye=_to_world(val["eye"], org),
                      tgt=_to_world(val["tgt"], org))
    # spiral_up: 나선 내부 상행 시점. [v6 판정 C-8] 구 컷(eye 동측 x6.13 →
    #   서향)은 **음영측 외벽 + 데크 소핏 암부**로 프레임 90 %가 죽었다.
    #   순광 축 = **시선을 +X 로 두는 것**. 나선 최하단(진입 통로측, 방위
    #   135°, r 2.55)에 서서 상행 방향(방위 45°, r 2.55)을 보면 시선 방위 0°,
    #   피사면 법선 180° → 태양 az 145 와 35° 차 = lambert +0.529 순광
    #   (v6 의 az 205 에서도 +0.585 였고, v7 재선정 후에도 순광 유지).
    #   [v7 판정 §4 ③] "프레임의 60 %가 원경 벽돌 파사드" → eye 는 그대로 두고
    #   (기둥 1.8 m 이격·통로 유효고 검산이 걸린 값) **tgt 만 올려** 피치를
    #   +11.0° → +18.8° 로 세운다. 시선 끝(x 5.30, r 2.55, 방위 45°)이 랜딩
    #   저면(4.498) 아래 z 2.75 이므로 프레임 상단이 **랜딩 소핏**으로 막히고,
    #   하단·중단에 방위 0~300° 구간 디딤 리본(z 1.9~2.9)이 들어온다.
    out["spiral_up"] = dict(eye=[1.70, -11.20, 1.45], tgt=[5.30, -11.20, 2.75])
    # deck_entry: 데크에서 나선 하강 진입(보행자 시점 h1.6).
    out["deck_entry"] = dict(eye=[3.50, -9.50, 6.60], tgt=[4.60, -14.60, 4.30])
    # broken_rail: 난간 탈락 구간(방위 225°, r3.3, z 4.155) 클로즈.
    #   eye 는 남서 — 피사면 법선 203.2°, 태양 az 145 와 58° 차 → lambert
    #   +0.340 (v6 az 205 의 +0.645 보다 낮지만 순광 유지, SMOKE 컷별 표).
    out["broken_rail"] = dict(eye=[-1.42, -16.44, 5.60],
                              tgt=[1.17, -15.33, 4.16])
    # ground_approach: 구 그리드 축(지상 보도 접근, 서 → 동) 보존 컷 h0.9.
    #   tgt 는 중앙 기둥(r0.5) 안으로 들어가지 않게 진입 통로 상공을 겨눈다.
    out["ground_approach"] = dict(eye=[-6.30, -13.00, 0.90],
                                  tgt=[2.30, -13.40, 1.60])
    # ground_graze: 사선 지상 grazing — 원통 실루엣 은닉 보강 컷.
    out["ground_graze"] = dict(eye=[-5.00, -17.50, 0.35],
                               tgt=[3.20, -12.60, 0.90])
    # overview: 육교 전경 부감(차도·데크·나선·북측 계단 동시).
    #   [v7] 태양 az 205 → 145 로 옮기면 구 시점(남서 −16,−28)의 피사면
    #   (법선 228°)이 lambert +0.074 = 터미네이터로 죽는다. 시점을 서측으로
    #   당겨(−20,−16) 피사면 법선을 207° 로 돌리면 +0.303 순광이 된다.
    #   프레이밍 검산(수평 반화각 30°·수직 18°): 나선 중심 yaw +19.8°·부각
    #   24.1°(피치 −24.4° 대비 +0.3°) · 북측 계단 yaw −27.9°·부각 17.0°
    #   → 나선·데크·차도·북측 계단이 모두 프레임 안(SMOKE [v7 프레이밍]).
    out["overview"] = dict(eye=[-20.00, -16.00, 15.00], tgt=[3.50, -4.00, 3.00])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드(데크 종주) — 기둥머리 상면(5.000)과 원측 지면이 하나의 평면으로
                            읽혀 환형 보이드(5.005 m)·나선 하강이 은닉되나
 2. broken_rail    — 상부 90°(방위 180~270) 가로대 결손 + 포스트 잔존 판독
 3. spiral_up      — 나선 내부 상행(피치 +19°): 랜딩 소핏이 상단을 막았나
 3b. d2 프리셋      — h0.9/h1.8 은 pitch −20/−28° : 연단·디딤이 프레임 안인가
 3c. 태양 az 145    — 그리드 피사면(+Y향)·deck_entry 상반의 암부가 걷혔나
 4. deck_entry     — 데크 → 원형 랜딩 → 단 0 접속(단차 0.002/0.190) 연속성
 5. ground_approach/graze — 지상 접근에서 진입 통로·내측 보이드가 읽히나
 6. overview       — 차도·연석·차선·데크 유효고 4.80 m·북측 계단 접지
 7. 데크 난간      — 지주 분절 + 개방 베이 교대(투시)로 회랑 암부가 걷혔나
 8. 경계·지평      — 식재대·가로수 열·원경 수목 띠로 지평이 폐쇄됐나"""


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
    ROOT = "/World/Scene06"
    UsdGeom.Xform.Define(stage, ROOT)

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    sp = PARAMS["spiral"]
    CX, CY = sp["cx"], sp["cy"]

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *a, **kw):
        return sc.make_pbr(stage, path, *a, **kw)

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
        M["concrete"] = PBR(f"{ROOT}/Looks/Concrete",
                            sc.tex_path("concrete_wall", "diff"),
                            sc.tex_path("concrete_wall", "nor"),
                            sc.tex_path("concrete_wall", "rough"),
                            s["concrete_wall"], tint=mp["concrete_tint"])
        M["deck"] = PBR(f"{ROOT}/Looks/DeckConcrete",
                        sc.tex_path("concrete_wall", "diff"),
                        sc.tex_path("concrete_wall", "nor"),
                        sc.tex_path("concrete_wall", "rough"),
                        s["concrete_wall"] * 1.6, tint=mp["deck_tint"])
        # 페시아·파라펫·치크 — 거푸집 줄눈이 크게 보이도록 스케일 분리(3.2 m)
        M["fascia"] = PBR(f"{ROOT}/Looks/Fascia",
                          sc.tex_path("concrete_wall", "diff"),
                          sc.tex_path("concrete_wall", "nor"),
                          sc.tex_path("concrete_wall", "rough"),
                          s["concrete_wall"] * 1.6, tint=mp["parapet_tint"])
        M["grime"] = PBR(f"{ROOT}/Looks/Grime",
                         diffuse_color=mp["grime_color"],
                         roughness_const=mp["grime_rough"])
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
        # [v6 판정 C-3] 구 파라펫 = 무텍스처 단색 판(스티로폼 인상) →
        #   콘크리트 diff/nor/rough + 중성 틴트(알베도 0.435). 코핑·오염 밴드는
        #   build_north / build_cues 에서 별도 프림으로 부여.
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           sc.tex_path("concrete_wall", "diff"),
                           sc.tex_path("concrete_wall", "nor"),
                           sc.tex_path("concrete_wall", "rough"),
                           s["concrete_wall"], tint=mp["parapet_tint"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["leaf_a"] = PBR(f"{ROOT}/Looks/LeafA", diffuse_color=mp["leaf_a"],
                          roughness_const=1.0, specular_level=0.0)
        M["leaf_b"] = PBR(f"{ROOT}/Looks/LeafB", diffuse_color=mp["leaf_b"],
                          roughness_const=1.0, specular_level=0.0)
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing",
                          diffuse_color=mp["nosing_color"],
                          roughness_const=0.7)
        # [v5.2 사용자] 임의 경고 팻말 제거 — 사인 패널 재질 생성 삭제.
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
        for i, (ya, yb) in enumerate(((wk["ys0"], wk["ys1"]),
                                      (wk["yn0"], wk["yn1"]))):
            BOX(f"{ROOT}/Walk_{i}",
                ((wk["x0"]+wk["x1"])/2.0, (ya+yb)/2.0,
                 wk["z_top"] - wk["thick"]/2.0),
                (wk["x1"]-wk["x0"], yb-ya, wk["thick"]), M["paving"], col=True)
        # 연석: 보도 가장자리 밴드(차도 대비 0.15 노출)
        cb = PARAMS["curb"]
        for i, ye in enumerate((rd["y0"], rd["y1"])):
            yc = ye - cb["w"]/2.0 if i == 0 else ye + cb["w"]/2.0
            BOX(f"{ROOT}/Curb_{i}",
                ((wk["x0"]+wk["x1"])/2.0, yc, cb["z_top"] - cb["thick"]/2.0),
                (wk["x1"]-wk["x0"], cb["w"], cb["thick"]), M["curb"], col=True)
        # [v6 판정 C-2] 식재대 — 보도 바깥 경계 1열(경계석 + 지피).
        #   보도판이 잔디와 하드 에지로 만나 "공터"가 되는 것을 막는 근경 경계물.
        vg = PARAMS["verge"]
        vx0, vx1 = vg["x0"], vg["x1"]
        for i, (ya, yb) in enumerate(((wk["ys0"] - vg["w"], wk["ys0"]),
                                      (wk["yn1"], wk["yn1"] + vg["w"]))):
            # 경계석(보도측·잔디측 2줄)
            for j, yc in enumerate((ya + vg["curb_t"]/2.0,
                                    yb - vg["curb_t"]/2.0)):
                BOX(f"{ROOT}/VergeCurb_{i}_{j}",
                    ((vx0+vx1)/2.0, yc, vg["curb_top"] - 0.22),
                    (vx1-vx0, vg["curb_t"], 0.44), M["curb"], col=True)
            BOX(f"{ROOT}/VergeSoil_{i}",
                ((vx0+vx1)/2.0, (ya+yb)/2.0, vg["soil_top"] - 0.20),
                (vx1-vx0, (yb-ya) - 2*vg["curb_t"], 0.40), M["soil"], col=True)

    def build_lanes(M):
        ln = PARAMS["lane"]
        for i, y in enumerate(ln["center_ys"]):
            BOX(f"{ROOT}/CenterLine_{i}",
                ((ln["x0"]+ln["x1"])/2.0, y, ln["z"]),
                (ln["x1"]-ln["x0"], ln["w"], ln["t"]), M["line_y"])
        period = ln["seg"] + ln["gap"]
        ndash = int((ln["x1"] - ln["x0"]) / period)
        for j, y in enumerate(ln["dash_ys"]):
            for k in range(ndash):
                xc = ln["x0"] + k*period + ln["seg"]/2.0
                BOX(f"{ROOT}/Dash_{j}_{k}", (xc, y, ln["z"]),
                    (ln["seg"], ln["w"], ln["t"]), M["line_w"])

    # -------------------------------------------------------------------
    # 나선 계단 + 중앙 기둥 + 원형 랜딩
    # -------------------------------------------------------------------
    def build_spiral(M):
        sc.build_helix_steps(stage, f"{ROOT}/Spiral", CX, CY, sp["r_in"],
                             sp["r_out"], sp["a0"], _step_deg(), sp["n"],
                             sp["riser"], sp["z0"], M["concrete"],
                             ccw=True, collider=True,
                             base_drop=sp["base_drop"])
        # [v6 판정 ⑤] 외주 연속 페시아 링 + 하부 헬리컬 슬래브(RC 나선 소핏).
        #   디딤(GT)은 건드리지 않고 **실루엣만** 매끈하게 만든다.
        a_lo, a_hi = _fascia_span()
        fa = PARAMS["fascia"]
        sc.build_helix_ramp(stage, f"{ROOT}/SpiralFascia", CX, CY,
                            fa["r_in"], fa["r_out"], a_lo, a_hi,
                            max(8, int(round((a_hi-a_lo) * fa["seg_per_deg"]))),
                            _fascia_z(a_lo), _fascia_z(a_hi), fa["thick"],
                            M["fascia"], collider=False)
        so = PARAMS["soffit"]
        sc.build_helix_ramp(stage, f"{ROOT}/SpiralSoffit", CX, CY,
                            so["r_in"], so["r_out"], a_lo, a_hi,
                            max(8, int(round((a_hi-a_lo) * so["seg_per_deg"]))),
                            _fascia_z(a_lo) - so["drop"],
                            _fascia_z(a_hi) - so["drop"], so["thick"],
                            M["concrete"], collider=False)
        co = PARAMS["column"]
        CYL(f"{ROOT}/Column", (CX, CY, (co["z_top"]+co["z_bot"])/2.0),
            co["r"], co["z_top"]-co["z_bot"], M["concrete"], col=True)
        la = PARAMS["landing"]
        # 북반원 환형 참 — 단 0(방위 180~) 과 경계에서 접한다. build_arc_steps
        #   세그는 외경 현 ×1.03 이라 마지막 세그가 180°를 0.11° 넘지만
        #   z 대역(4.498~4.998) 이 단 0(4.308~4.808) 과 겹치는 폭이 0.11°에
        #   불과해 판독·보행에 영향이 없다(감독 확인용 기록).
        sc.build_arc_steps(stage, f"{ROOT}/Landing", CX, CY, la["r_in"],
                           la["r_out"], la["a0"], la["a1"], la["seg"],
                           la["top_z"], la["base_z"], M["deck"])

    # -------------------------------------------------------------------
    # 육교 데크 + 지지 기둥
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P9 bridge_deck. Deck top (z=5.000), travel -Y.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        dk = PARAMS["deck"]
        gp = gk.plan_ground(
            "bridge_deck",
            region=(dk["x0"], dk["y0"], dk["x1"], dk["y1"]),
            z=dk["z_top"], gy=0.0,
            origin=(3.5, dk["y0"], dk["z_top"]), axis="-y",
            edges=[("well_edge", 0.0)],
            dists=(2, 5, 10), scene="scene06",
            tactile=(),                 # §12.4 — 홀드(감독 판단, M10)
            overrides=dict(pave=dict(module=(None, None), joint="expansion",
                                     step_x=None, step_y=g["joint_step"]),
                           infra=dict(gully=len(g["gully"]))),
            sites=dict(gully=[tuple(v) for v in g["gully"]]),
            extras_args=dict(wear_lane=dict(centerline=tuple(g["wear"]),
                                            width=g["wear_w"])),
            seed=6)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["curb"], crack=M["curb"], gully=M["steel"],
                  wear=M["curb"], stain_water=M["curb"], stain_drip=M["curb"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris,
                              slabs=(f"{ROOT}/Deck",))
        print(f"[ground_kit] scene06 P9 · prims {res['prims']} · "
              f"delta_max {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    def build_deck(M):
        dk = PARAMS["deck"]
        # [W2-0 · P-A] Registered before the slab exists, because `_skin_wanted`
        # is evaluated inside `sc.add_box`. (The deck is 3.0 m wide, i.e. under
        # the 4.0 m skin threshold today, so this is a forward guard.)
        sc.skin_exclude(f"{ROOT}/Deck")
        BOX(f"{ROOT}/Deck",
            ((dk["x0"]+dk["x1"])/2.0, (dk["y0"]+dk["y1"])/2.0,
             dk["z_top"] - dk["thick"]/2.0),
            (dk["x1"]-dk["x0"], dk["y1"]-dk["y0"], dk["thick"]),
            M["deck"], col=True)
        dp = PARAMS["deck_posts"]
        for i, py in enumerate(dp["ys"]):
            z1 = dk["z_top"] - dk["thick"]
            CYL(f"{ROOT}/DeckPost_{i}", (dp["x"], py, (dp["z_bot"]+z1)/2.0),
                dp["r"], z1-dp["z_bot"], M["concrete"], col=True)
            # 기둥머리 캡보
            BOX(f"{ROOT}/DeckCap_{i}", (dp["x"], py, z1 - 0.18),
                (dk["x1"]-dk["x0"]+0.4, 0.9, 0.36), M["concrete"])

    # -------------------------------------------------------------------
    # 북측 진입 계단 (rot_group 90°)  — 로컬 +X 하강 → 월드 +Y 하강
    # -------------------------------------------------------------------
    def build_north(M):
        no = PARAMS["north"]
        RG = sc.build_rot_group(stage, f"{ROOT}/NorthGroup",
                                no["pivot"], no["rot"])
        runA = no["n"] * no["tread"]
        z_mid = no["z_top"] - no["n"]*no["riser"]
        # 상단 플라이트
        sc.build_straight_stairs(stage, f"{RG}/FlightA", no["x0"], no["y0"],
                                 no["y1"], no["riser"], no["tread"], no["n"],
                                 no["base_z"], M["concrete"],
                                 z_top=no["z_top"], collider=True)
        # 중간참
        lx0 = no["x0"] + runA
        lx1 = lx0 + no["land_len"]
        BOX(f"{RG}/MidLanding",
            ((lx0+lx1)/2.0, (no["y0"]+no["y1"])/2.0,
             (z_mid + no["base_z"])/2.0),
            (lx1-lx0, no["y1"]-no["y0"], z_mid-no["base_z"]),
            M["concrete"], col=True)
        # 하단 플라이트
        sc.build_straight_stairs(stage, f"{RG}/FlightB", lx1, no["y0"],
                                 no["y1"], no["riser"], no["tread"], no["n"],
                                 no["base_z"], M["concrete"],
                                 z_top=z_mid, collider=True)
        # 치크 파라펫 — 계단선과 평행한 경사 박스(scene21 파라펫 규약).
        #   단일 수평 박스는 상부 단을 묻고 하부에선 떠 버리므로 build_slope 를
        #   쓴다. 경사각 = atan2(2.496, 3.9) = 32.62°, cos = 0.8422.
        #   thick 1.5 → 밑면이 계단선 아래 1.5·cos = 1.263 m 로 전 구간 매입
        #   (상단 x0 에서 밑면 4.687 < 1단 디딤면 4.808, 하단에서 2.191 <
        #   참 상면 2.504 · 계단 저면 −0.30 위이나 계단 솔리드 안이라 무공극).
        #   폭 cheek_t 는 계단 폭 **안쪽** 대역 — 폭 밖 허공 배치 금지(감사 B2).
        drop_f = no["n"] * no["riser"]
        cap_h, cap_ov = no["cap_h"], no["cap_over"]
        for fi, (fx0, fz0) in enumerate(((no["x0"], no["z_top"]),
                                         (lx1, z_mid))):
            for i, (ya, yb) in enumerate(
                    ((no["y0"], no["y0"] + no["cheek_t"]),
                     (no["y1"] - no["cheek_t"], no["y1"]))):
                sc.build_slope(stage, f"{RG}/Cheek_{fi}_{i}", fx0,
                               fz0 + no["cheek_h"], runA, drop_f, ya, yb,
                               1.5, M["parapet"], margin=0.0, collider=True)
                # [v6 판정 ①] 코핑(갓돌) — 무장식 백색 덩어리가 "흰 이빨"로
                #   읽히던 원인. 오버행 3 cm 캡을 얹어 파라펫 관행 실루엣으로.
                sc.build_slope(stage, f"{RG}/CheekCap_{fi}_{i}", fx0,
                               fz0 + no["cheek_h"] + cap_h, runA, drop_f,
                               ya - cap_ov, yb + cap_ov, cap_h * 1.6,
                               M["curb"], margin=0.0, collider=False)
        # 중간참 구간 치크(수평 구간 0.95 m 파라펫) + 코핑
        for i, (ya, yb) in enumerate(
                ((no["y0"], no["y0"] + no["cheek_t"]),
                 (no["y1"] - no["cheek_t"], no["y1"]))):
            BOX(f"{RG}/CheekMid_{i}",
                ((lx0+lx1)/2.0, (ya+yb)/2.0, z_mid + no["cheek_h"]/2.0),
                (lx1-lx0, yb-ya, no["cheek_h"]), M["parapet"])
            BOX(f"{RG}/CheekMidCap_{i}",
                ((lx0+lx1)/2.0, (ya+yb)/2.0,
                 z_mid + no["cheek_h"] + cap_h/2.0),
                (lx1-lx0, yb-ya + 2*cap_ov, cap_h), M["curb"])
        # [v5.1 §4 / v6 C-3] 기단 오염 밴드 — 계단 솔리드 측면 하단 0.30 m
        for i, ye in enumerate((no["y0"], no["y1"])):
            sgn = 1.0 if i == 0 else -1.0
            BOX(f"{RG}/StairGrime_{i}",
                (no["x0"] + (2*runA + no["land_len"])/2.0,
                 ye + sgn*0.012, PARAMS["walk"]["z_top"] + 0.15),
                (2*runA + no["land_len"], 0.024, 0.30), M["grime"])
        return RG

    # -------------------------------------------------------------------
    # 드레싱
    # -------------------------------------------------------------------
    def build_dressing(M):
        d = PARAMS["dress"]
        lp = d["lamp"]
        gz = PARAMS["walk"]["z_top"]
        for i, (lx, ly) in enumerate(d["lamps"]):
            base = f"{ROOT}/Lamp_{i}"
            CYL(f"{base}/Pole", (lx, ly, gz + lp["pole_h"]/2.0), lp["pole_r"],
                lp["pole_h"], M["pole"], col=True)
            sgn = 1.0 if ly < 0 else -1.0
            CYL(f"{base}/Arm", (lx, ly + sgn*lp["arm_len"]/2.0,
                                gz + lp["pole_h"] - 0.12),
                lp["arm_r"], lp["arm_len"], M["pole"], rotX=90.0)
            BOX(f"{base}/Head", (lx, ly + sgn*lp["arm_len"],
                                 gz + lp["pole_h"] - 0.18),
                (lp["head"], lp["head"]*1.5, 0.14), M["lamp"])
        # 가로수는 전부 식재대(verge) 위 — 지반이 보도(−0.005)가 아니라
        #   지피 상면(0.10)이므로 근원부가 묻히지 않게 그 높이로 심는다.
        tz = PARAMS["verge"]["soil_top"]
        for i, (tx, ty) in enumerate(d["trees"]):
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", tx, ty, tz, M["wood"],
                          M["leaf_a"], M["leaf_b"])
        for i, (bx, by, yaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, gz, M["wood"],
                           yaw=yaw)
        for i, (bx, by) in enumerate(d["bollards"]):
            sc.build_bollard(stage, f"{ROOT}/Bollard_{i}", bx, by, gz,
                             mtl=M["pole"])
        bx, by, bh = d["bus_pole"]
        CYL(f"{ROOT}/BusPole", (bx, by, gz + bh/2.0), 0.055, bh, M["pole"],
            col=True)
        BOX(f"{ROOT}/BusSign", (bx, by, gz + bh - 0.30),
            (0.06, 0.55, 0.55), M["panel"])
        build_treeband(M)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd, M["brick"],
                              M["glass"], M["parapet"],
                              window=PARAMS["window_by"].get(
                                  key, PARAMS["window"]))

    def build_treeband(M):
        """[v6 판정 C-2/C-4] 원경 수목 실루엣 띠 — 개체 나무(롤리팝) 도열 대신
        높이 지터를 준 능선형 블록 열. 잔디판이 하늘과 직접 만나는 직선 지평을
        지우는 것이 목적이며, 그리드 시선축(데크 종주 −Y)의 원측 배경이 된다.
        결정적 지터(좌표 해시) — 재실행 시 동일."""
        tb = PARAMS["treeband"]
        import random as _random
        for r, (ya, yb, hh) in enumerate(tb["rows"]):
            n = max(2, int(round((tb["x1"] - tb["x0"]) / tb["seg"])))
            for k in range(n):
                xa = tb["x0"] + k * (tb["x1"] - tb["x0"]) / n
                xb = tb["x0"] + (k + 1) * (tb["x1"] - tb["x0"]) / n
                rnd = _random.Random((r * 7717) ^ (k * 3413))
                h = hh + rnd.uniform(-tb["jitter"], tb["jitter"])
                dy = rnd.uniform(-0.8, 0.8)
                BOX(f"{ROOT}/TreeBand_{r}_{k}",
                    ((xa+xb)/2.0, (ya+yb)/2.0 + dy,
                     PARAMS["ground"]["z_top"] + h/2.0),
                    (xb - xa + 0.6, (yb - ya) * rnd.uniform(0.8, 1.25), h),
                    M["leaf_a"] if (k + r) % 2 == 0 else M["leaf_b"])
                # 수관 상부 블롭 1개 — 직육면체 능선을 깨는 최소 요소
                sc.add_sphere(stage, f"{ROOT}/TreeBlob_{r}_{k}",
                              ((xa+xb)/2.0 + rnd.uniform(-1.5, 1.5),
                               (ya+yb)/2.0 + dy,
                               PARAMS["ground"]["z_top"] + h),
                              (rnd.uniform(1.8, 3.0), rnd.uniform(1.4, 2.2),
                               rnd.uniform(1.0, 1.8)),
                              M["leaf_b"] if (k + r) % 2 == 0 else M["leaf_a"])

    # -------------------------------------------------------------------
    # 단서 (cue) — 난간(훼손 변주) · 점자 · 단코
    # -------------------------------------------------------------------
    def _pipe_arc(tag, rad, a0, a1, z_off, pipe_r, M):
        """나선 디딤선을 따르는 파이프 가로대 1선(helix_ramp 로 근사)."""
        rl = PARAMS["railing"]
        nseg = max(4, int(round((a1 - a0) * rl["seg_per_deg"])))
        sc.build_helix_ramp(stage, f"{ROOT}/Rail{tag}", CX, CY,
                            rad - pipe_r, rad + pipe_r, a0, a1, nseg,
                            _spiral_z_at(a0) + z_off,
                            _spiral_z_at(a1) + z_off,
                            pipe_r*2.0, M["rail"], collider=False)

    def _posts(tag, rad, a0, a1, M):
        rl = PARAMS["railing"]
        npost = max(2, int(round((a1 - a0) / rl["post_step_deg"])))
        for k in range(npost + 1):
            a = a0 + (a1 - a0) * k / float(npost)
            zt = _spiral_z_at(a)
            px = CX + rad * math.cos(math.radians(a))
            py = CY + rad * math.sin(math.radians(a))
            CYL(f"{ROOT}/RailPost{tag}_{k}",
                (px, py, zt + rl["rail_h"]/2.0), rl["post_r"],
                rl["rail_h"] + 0.10, M["rail"])

    def build_deck_rail(M):
        """[v6 판정 ①] 데크 방음 난간 — 지주 분절 + 방음판/개방 베이 교대.
        구 구성(양측 무분절 판재 1매 + 상단 파이프)은 폐합 박스거더로 읽혔고,
        그리드가 데크 종주축으로 옮겨온 지금은 **회랑 양벽이 순흑 그림자면**이
        되어 판정·학습 데이터 모두를 죽인다(scene11 동일 결함).
        짝수 베이 = 방음판(+코핑 캡), 홀수 베이 = 개방(킥 밴드 + 세로 살 5본).
        GT 무관(난간 프림) — cue_railing 토글 하위."""
        dk = PARAMS["deck"]
        rb = PARAMS["rail_bay"]
        y0, y1 = dk["y0"], dk["y1"]
        nb = int(rb["n_bay"])
        L = (y1 - y0) / float(nb)
        zt = dk["z_top"]
        for i, xe in enumerate((dk["x0"], dk["x1"])):
            for k in range(nb + 1):                      # 지주
                BOX(f"{ROOT}/DeckRailPost_{i}_{k}",
                    (xe, y0 + k*L, zt + rb["post_h"]/2.0),
                    (rb["post_t"], rb["post_t"], rb["post_h"]), M["steel"])
            for k in range(nb):
                ya = y0 + k*L + rb["post_t"]/2.0 + rb["joint"]
                yb = y0 + (k+1)*L - rb["post_t"]/2.0 - rb["joint"]
                yc, Ly = (ya + yb)/2.0, yb - ya
                if k % 2 == 0:                           # 방음판 베이
                    BOX(f"{ROOT}/DeckPanel_{i}_{k}",
                        (xe, yc, zt + dk["panel_h"]/2.0),
                        (dk["parapet_t"], Ly, dk["panel_h"]), M["panel"])
                    BOX(f"{ROOT}/DeckPanelCap_{i}_{k}",
                        (xe, yc, zt + dk["panel_h"] + rb["cap_h"]/2.0),
                        (dk["parapet_t"] + 2*rb["cap_over"], Ly, rb["cap_h"]),
                        M["rail"])
                else:                                    # 개방 베이(투시)
                    BOX(f"{ROOT}/DeckKick_{i}_{k}",
                        (xe, yc, zt + rb["kick_h"]/2.0),
                        (dk["parapet_t"], Ly, rb["kick_h"]), M["panel"])
                    nbal = int(rb["n_baluster"])
                    bz0 = zt + rb["kick_h"]
                    bz1 = zt + dk["parapet_h"] - 0.05
                    for b in range(nbal):
                        yb_ = ya + (b + 0.5) * Ly / float(nbal)
                        CYL(f"{ROOT}/DeckBal_{i}_{k}_{b}",
                            (xe, yb_, (bz0 + bz1)/2.0), rb["baluster_r"],
                            bz1 - bz0, M["rail"])
            CYL(f"{ROOT}/DeckRail_{i}", (xe, (y0+y1)/2.0,
                                         zt + dk["parapet_h"]),
                0.035, y1 - y0, M["rail"], rotX=90.0)

    def build_cues(M):
        rl = PARAMS["railing"]
        a0, a1 = sp["a0"], sp["a0"] + sp["sweep"]
        b0, b1 = rl["broken"]
        if cfg["cue_railing"]:
            # 외측: 포스트는 전 구간 잔존, 가로대는 훼손 구간(b0..b1) 결손
            _posts("Outer", rl["outer_r"], a0, a1, M)
            _pipe_arc("OuterTop", rl["outer_r"], b1, a1, rl["rail_h"],
                      rl["pipe_r"], M)
            _pipe_arc("OuterMid", rl["outer_r"], b1, a1,
                      rl["rail_h"] - rl["mid_drop"], rl["pipe_r"]*0.7, M)
            # 내측: 전 구간 정상(킥플레이트는 없음 — 로봇 시점 개방)
            _posts("Inner", rl["inner_r"], a0, a1, M)
            _pipe_arc("InnerTop", rl["inner_r"], a0, a1, rl["rail_h"],
                      rl["pipe_r"], M)
            _pipe_arc("InnerMid", rl["inner_r"], a0, a1,
                      rl["rail_h"] - rl["mid_drop"], rl["pipe_r"]*0.7, M)
            # 데크 방음 난간(양측) — [v6 판정 ①] 지주 분절 + 개방 베이 교대
            build_deck_rail(M)
            la = PARAMS["landing"]
            for i, (pa0, pa1) in enumerate(((0.0, 62.0), (118.0, 180.0))):
                sc.build_arc_steps(stage, f"{ROOT}/LandingParapet_{i}", CX, CY,
                                   la["r_out"] - 0.09, la["r_out"], pa0, pa1,
                                   max(4, int((pa1-pa0)/6.0)),
                                   la["top_z"] + PARAMS["deck"]["panel_h"],
                                   la["top_z"] - 0.10, M["panel"],
                                   collider=False)
                # 코핑(갓돌) — 순백 무텍스처 판 인상 제거(C-3)
                sc.build_arc_steps(stage, f"{ROOT}/LandingCoping_{i}", CX, CY,
                                   la["r_out"] - 0.12, la["r_out"] + 0.03,
                                   pa0, pa1, max(4, int((pa1-pa0)/6.0)),
                                   la["top_z"] + PARAMS["deck"]["panel_h"]
                                   + 0.07,
                                   la["top_z"] + PARAMS["deck"]["panel_h"],
                                   M["curb"], collider=False)
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            lx0, lx1, ly0, ly1 = tc["low"]
            sc.build_tactile(stage, f"{ROOT}/TactileLow", lx0, lx1, ly0, ly1,
                             M["tactile"], z=tc["low_z"], proud=tc["proud"])
            hx0, hx1, hy0, hy1 = tc["high"]
            sc.build_tactile(stage, f"{ROOT}/TactileHigh", hx0, hx1, hy0, hy1,
                             M["tactile"], z=tc["high_z"], proud=tc["proud"])
        # [v5.2 사용자] 임의 경고 팻말 제거 — cue_sign 배치 삭제.
        if cfg["cue_nosing"]:
            sd = _step_deg()
            for i in range(sp["n"]):
                aa = sp["a0"] + i * sd
                top = _spiral_top_z(i)
                sc.build_arc_steps(stage, f"{ROOT}/Nosing_{i}", CX, CY,
                                   sp["r_out"] - 0.07, sp["r_out"], aa,
                                   aa + sd, 1, top + 0.004, top - 0.02,
                                   M["nosing"], collider=False)

    def build_flat_control(M):
        """hazard_stairs=False — 육교 구조 일체를 제거한 평탄 보도 대조군."""
        wk = PARAMS["walk"]
        BOX(f"{ROOT}/FlatFill", (CX, CY, wk["z_top"] - 0.25),
            (2*sp["r_out"] + 1.0, 2*sp["r_out"] + 1.0, 0.5), M["paving"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_site(M)
    if cfg["cue_material_break"]:
        build_lanes(M)
    if cfg["hazard_stairs"]:
        build_spiral(M)
        build_deck(M)
        build_ground_kit(M)    # [W2-D] deck ground elements (deck must exist)
        build_north(M)
        build_cues(M)          # 기하가 없으면 난간도 없다(부유 방지)
    else:
        build_flat_control(M)
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene06_{ts}.png")
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
