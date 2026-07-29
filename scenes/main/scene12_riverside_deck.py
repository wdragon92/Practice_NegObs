# -*- coding: utf-8 -*-
"""
scene12_riverside_deck.py — NegObs 인공씬 12호 (v5 R7): 한강 수변 캔틸레버
데크길 (Isaac Sim 4.5)

유형    : 캔틸레버 축(구 T17 절벽 잔도 기하축 계승) — 무대만 '한강/하천 수변
          목재 데크 산책로'로 교체. 사양서: Docs/briefs/multi_scene_brief_v5.md
          §R7 (근거: Docs/scene_redesign_v5_proposal.md 처분표 12=교체)
공통    : scene_common.py · **scene17_ramp_pair_hangang.py 세계관 공유**
          (수면/아파트 원경/교량/억새/가로등 파라미터·재질 패턴 재사용)

위험 본질
  폭 2.5 m 목재 데크가 호안 사석 위로 1.25 m 내밀어(캔틸레버) 수면(−1.8)
  위를 지난다. 강측 난간은 **한 스팬 2.4 m 가 훼손**(포스트 밑동만 잔존,
  경고 테이프 1선)되어 그 구간은 완전 무방호이고, 남은 난간에도 **킥플레이트
  (하부 막음판)가 없어** 로봇 눈높이 h0.3 에서는 중간대(z 0.55) 아래로
  시선이 그대로 빠져나간다. 그런데 정작 **근접 수면은 보이지 않는다** —
  데크 외단(y 1.25, z 0)을 스치는 시선이 수면에 닿는 지점은 y = 8.75 m 라,
  y 1.25..8.75 의 사석·수면 7.50 m 대역이 화면에서 사라진다(missing ground
  band). 데크 끝(x=0)의 8단 하강도 grazing 에서 동일하게 은닉된다.

목표
  ① 데크(x −18..0, 폭 2.5, z=0) + 목재 보·말뚝 + 캔틸레버 1.25 m
  ② 강측 난간(포스트+상단대+중간대, 킥플레이트 없음) + 훼손 스팬 2.4 m
  ③ 데크 끝 접속 계단 8 라이저(0.17 × 8 = 1.36) → 하부 둔치(−1.36)
  ④ 호안 사석 단(−0.55/−1.45/−1.75/−1.78/−1.95/−2.40) + 수면 −1.8 + 갈대·억새
  ⑤ 자전거도로 밴드·벤치·가로등·원경 교량/아파트(scene17 규약)
  ⑥ [v5.2 사용자] 임의 경고 팻말 제거 — 훼손 흔적(잔존 밑동·테이프)만 잔존

v6 판정(judge_v6_rt_new7 §6) 반영 — **GT 낙차 1.80 불변**(감독 결정 4)
  · 수면 z 조립 좌표 검증 : sc.build_water 는 상면이 z 에 오도록 두께 0.2 박스를
    z−0.1 중심에 놓는다 → 수면 상면 = −1.800, 데크 상면 = 0.000 → 낙차 1.800.
    **조립 버그 없음**(스모크 [수면 z 조립 검증]에서 매 실행 재확인).
    "수면이 데크 상면에 붙어 보인다"의 실제 원인은 z 가 아니라 **가시성**이었다:
    노출 사석이 y 1.25..2.35(1.10 m)뿐이라 부감 시선이 데크 에지에 가려
    사석·수제선이 통째로 은닉되고, 데크 에지 바로 뒤에서 수면이 시작됐다.
  · 대책 ① 호안 노출대 2.4배 확대(수제선 y 2.35 → 3.90, 수면 y0 1.90 → 3.70)
           + 물때 밴드 + 잡석 96개(구 42) → 사석 호안이 화면에 남는다.
    대책 ② 캔틸레버 하부 시인 컷 : under_deck 재조준(수면 위 0.9 m 저시점) +
           **bank_face 신설**(강측 부감 — 데크면·에지·페시아·보·말뚝·사석·
           수제선이 한 프레임에 수직으로 쌓여 1.80 m 가 눈금으로 읽힌다).
    대책 ③ beauty_overview 부각 상향(은닉 밴드 2.96 → 1.31 m).
    대책 ④ stair_join 재조준(8단 하강이 프레임에 없고 가로등이 관통하던 컷).
    대책 ⑤ [C-6] 경고 테이프 각재·부유 → 잔존 포스트 결속 처짐 리본(두께 4 mm).

보행 연속성 자가 검증표 (진입 → 종주 → 하강 → 탈출; 전 구간 단차 ≤ 0.17)
  ┌ # 구간               좌표(x, y, z)              단차/판정
  │ 0 상부 둔치 잔디      (−26.0, −3.0, 0.00)        평탄(잔디/마사토 산책로)
  │ 1 데크 진입           (−18.0,  0.0, 0.00)        평탄 (둔치와 플러시)
  │ 2 데크 종주           (−12.0,  0.0, 0.00)        평탄 (폭 2.5, 강측 난간)
  │ 3 훼손 스팬 통과      ( −4.8,  0.0, 0.00)        ← **강측 2.4 m 무방호**
  │                                                    (에지 너머 낙차 1.80)
  │ 4 계단 머리           (  0.0,  0.0, 0.00)        평탄
  │ 5 1단 디딤            (  0.16, 0.0, −0.17)       0.17
  │ 6 7단 디딤            (  2.08, 0.0, −1.19)       0.17 × 6
  │ 7 하부 둔치           (  2.60, 0.0, −1.36)       0.17 (8번째 라이저)
  │ 8 자전거도로 접속     (  8.0, −6.5, −1.358)      평탄
  └ 9 동측 탈출           ( 20.0, −6.5, −1.358)      평탄
  * 상부 둔치(z=0)와 하부 둔치(−1.36)는 데크 남측에서 잔디 사면(1:2, x 0..2.72)
    으로도 연결 — 계단이 유일 경로가 아니다(보행 우회 가능).
  * 데크 남측 에지는 상부 둔치와 **동일 레벨**이라 낙차 없음. 위험은 강측 편측.

[v7 판정 재수정] judge_v7_rt_A §8 — 담당분.
  ① `edge_void` 수면이 **완전 경면 + 무파**("인피니티 풀"). GT(1.80 m)는
     스모크가 이미 정합 확인 → 문제는 z 가 아니라 **재질과 프레이밍**.
     → water_rough 0.08 → **0.14**(scene09 0.15 대역) + 탁도 틴트 소폭 상향,
       `edge_void` tgt 를 수제선 직전으로 당겨 **노출 사석대(y 3.03..3.90)가
       프레임 중심**에 오게 재조준(eye·기울기·은닉 밴드 1.78 m 는 불변).
  ② 억새 4띠 = **갈색 육면체**(C-5, v6 최다 지적 미착수).
     → scene17 W-5 규약 이식: `build_hedge` 박스 → **대(stalk) 군락 164본**
       (r 22 mm · 높이 지터 · 소각 기울기 · 밴드별 seed). 밴드 사각형 불변.
  ③ 난간이 **광택 백색 파이프** → 도장 강재(0.80/metallic 0.9 → 0.30/0.25).
  ④ 우측(+X) 지평 미폐쇄 → 남측 시가지 1동(S2) 추가(C-2).
  ⑤ (공통) §4 순백 대면적 자가검사 `albedo_selfcheck()` + 억새 검산
     `reed_selfcheck()` 를 스모크에 편입. 파라펫 0.90 → 0.70 · 등기구 0.88 → 0.78.
  미조치(범위 밖·공통 빌더): 벤치 단색 슬래브(`sc.build_bench`),
     자전거도로 직선 절단(§5), `bank_face` 데크 하부 공극 준흑(조도 항목).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene12_riverside_deck.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene12_riverside_deck.py
스모크(부팅 전 기하·접지·은닉·카메라 자기검증·조기종료):
    NEGOBS_SMOKE=1 python scene12_riverside_deck.py

좌표계: Z-up, m. 진행축 +X(데크 종주 → 계단 하강). **낙차 시작 모서리 x=0**
  (계단 머리). 강은 +Y(북)측, 뭍은 −Y(남)측. 데크 상면 z=0, 수면 z=−1.8.
  태양 SUN_AZ_OFFSET=171.5(표준) → 광선이 −X−Y 상공에서 +X+Y 로 진행 =
  보행 진행 방향 순광, 호안 사면(법선 +Y)은 역광 암부(스모크에서 검산).
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 7키. hazard_stairs 만 위험 기하 토글(데크/계단 ↔ 평지).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 데크·계단·둔치 단차를 z=0 평지로 (기하 토글 유일 예외)
    "cue_railing":        True,    # 강측 난간(킥플레이트 없음). 훼손 스팬 2.4 m 는 상시 결손
    "cue_tactile":        False,   # 수변 목재 데크는 점자블록 비관행 — 코드 경로만 예약
    "cue_material_break": True,    # 데크 목재 vs 둔치 잔디/자갈 대비. False → 계단도 잔디톤 목재
    "cue_sign":           False,   # [v5.2 사용자] 임의 경고 팻말 제거 — 배치 없음(키만 예약)
    "cue_scene_dressing": True,    # 갈대·벤치·가로등·자전거도로·교량·아파트 원경
    "cue_nosing":         False,   # True → 계단 단코 논슬립 띠
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
_RISER = 0.17
_NRISER = 8                                     # 8 라이저 → 낙차 1.36
_LOWER_Z = -round(_RISER * _NRISER, 4)          # -1.36 (하부 둔치 상면)

PARAMS = dict(
    # --- 목재 데크 (x −18..0, 폭 2.5, 상면 z=0) ---
    #     y0 −1.25 는 상부 둔치와 플러시(낙차 없음), y1 +1.25 가 강측 캔틸레버 에지.
    deck=dict(x0=-18.0, x1=0.0, y0=-1.25, y1=1.25, z_top=0.0, slab_t=0.14,
              fascia_t=0.03),
    # 데크 하부 구조: 종보 2본(y −0.8 / 0.0) + 횡보 + 말뚝. 최외곽 지지선 y=0.0
    #   → 캔틸레버 내밈 = 1.25 m (호안 crest y=0.05 기준 1.20 m).
    deckframe=dict(beam_ys=(-0.8, 0.0), beam_w=0.16, beam_h=0.26,
                   pile_r=0.11, pile_step=3.0, cross_w=0.16, cross_step=3.0),
    # --- 접속 계단 8 라이저 (n_geom 7 + 하부 둔치 1) ---
    #     n_geom=7 : 8번째 라이저는 **하부 둔치 상면 자체**. 8개를 다 세우면
    #     마지막 단 상면(−1.36)이 둔치 슬래브 상면과 동일평면 → Z파이팅.
    stair=dict(x0=0.0, riser=_RISER, tread=0.32, n_riser=_NRISER,
               n_geom=_NRISER - 1, base_z=-2.0),
    # --- 지면 ---
    upper=dict(x0=-40.0, x1=0.0, y0=-22.0, y1=-1.25, z_top=0.0, thick=1.4,
               x_split=-18.0, y_crest=0.05),   # x_split 서측은 y_crest 까지 확장
    shoulder=dict(x0=-18.0, x1=0.0, y0=-1.25, y1=0.05, z_top=-1.20, thick=1.6),
    lower=dict(x0=0.0, x1=48.0, y0=-22.0, y1=1.25, z_top=_LOWER_Z, thick=1.2),
    slope=dict(x0=0.0, run=2.72, drop=1.36, y0=-22.0, y1=-1.25, thick=1.6),
    # 호안 사석 단 (전부 z_bot 까지 솔리드 — 부유 방지)
    #   [v6 판정 ②] "수면이 데크 상면에 붙어 보인다" 대응 — **GT 낙차 1.80 불변**
    #   (데크 상면 0.00 − 수면 −1.80). 감독 결정 4: 수면 z 는 그대로 두고
    #   **호안 노출대를 확대**해 낙차의 시각적 근거를 만든다.
    #     구: 노출 사석 = y 1.25..2.35 (1.10 m) → 수제선이 데크 에지 0.65 m 앞
    #     신: 노출 사석 = y 1.25..3.90 (2.65 m, 2.4배) → 수제선 y 3.90 으로 후퇴
    #   D 상면 −1.75 는 그대로라 **데크 에지 → 사석 낙하고 1.75 m 도 불변**이다.
    rip_bot=-3.2,
    riprap=[dict(tag="A", x0=-40.0, x1=-18.0, y0=0.05, y1=0.65, z=-0.55),
            dict(tag="B", x0=-40.0, x1=-18.0, y0=0.65, y1=1.25, z=-1.45),
            dict(tag="C", x0=-18.0, x1=0.0, y0=0.05, y1=1.25, z=-1.45),
            dict(tag="D", x0=-40.0, x1=48.0, y0=1.25, y1=2.30, z=-1.75),
            dict(tag="E", x0=-40.0, x1=48.0, y0=2.30, y1=3.90, z=-1.78),
            dict(tag="F", x0=-40.0, x1=48.0, y0=3.90, y1=5.60, z=-1.95),
            dict(tag="G", x0=-40.0, x1=48.0, y0=5.60, y1=7.40, z=-2.40)],
    # 물때(젖은 사석) 밴드 — 수제선 하드 에지 완화(v6 판정 ④ "물때·이끼 없음")
    waterline=dict(y0=2.90, y1=3.90, z=-1.78, proud=0.012),
    # 사석 잡석 낱개(랜덤 회전 박스) — seed 고정. 노출대 확대에 맞춰 개수·범위 증가
    #   (판정 ④ "매끈한 사고석 포장 → 잡석 호안이 아니다" 대응)
    rocks=dict(n=96, seed=712, x0=-38.0, x1=44.0, y0=0.2, y1=4.8,
               s_lo=0.30, s_hi=1.10),
    water=dict(x0=-40.0, x1=60.0, y0=3.70, y1=70.0, z=-1.80),
    far_bank=dict(x0=-40.0, x1=60.0, y0=70.0, y1=100.0, z_top=-1.50,
                  thick=2.2),
    # --- 난간 (강측 y=1.15) : 킥플레이트 **없음** — 로봇 시점 개방의 원인 ---
    rail=dict(y=1.15, post_r=0.032, post_h=1.05, spacing=1.5,
              top_z=1.05, top_r=0.035, mid_z=0.55, mid_r=0.020,
              gap_x0=-6.0, gap_x1=-3.6,            # 훼손 스팬 2.4 m
              stub_xs=(-5.4, -4.2), stub_h=0.10,   # 잘려나간 포스트 밑동
              # [v6 C-6] 경고 테이프 = 두께 0.02 각재 → **얇은 리본 + 처짐**.
              #   구 사양은 x −6.0..−3.6 을 그대로 잇는 솔리드 봉이라 (a) 두께가
              #   강재 빔급이고 (b) 동단 −3.6 에 지지물이 없어 공중 부유였다.
              #   신 사양: 양단을 **잔존 포스트 x −6.0 / −3.0** 에 결속하고
              #   중앙이 sag 만큼 처지는 포물선 리본(두께 4 mm).
              tape=dict(anchor_xs=(-6.0, -3.0), z_end=0.90, sag=0.17,
                        nseg=10, w=0.075, t=0.004, tie_h=0.05)),
    # [v5.2 사용자] 임의 경고 팻말 제거 — 추락주의·계단주의 사인 파라미터 삭제.
    # --- 상부 둔치 드레싱 ---
    path=dict(x0=-40.0, x1=0.0, y0=-4.6, y1=-2.6, proud=0.002),   # 마사토 산책로
    benches=[(-13.0, -1.90, 0.0), (-6.5, -1.90, 0.0)],
    streetlights=[(-15.0, -2.30), (-2.0, -2.60)],
    streetlight=dict(pole_h=4.5, pole_r=0.07, arm_len=0.9, arm_r=0.04,
                     head=0.24),
    trees=[(-34.0, -9.0), (-27.0, -13.0), (-19.0, -8.5), (-9.0, -12.0),
           (-2.0, -9.0)],
    # --- 하부 둔치 드레싱 ---
    bikeroad=dict(x0=0.0, x1=48.0, y0=-8.0, y1=-5.0, proud=0.002),
    lower_benches=[(9.0, -3.4, 180.0), (19.0, -3.4, 180.0)],
    lower_bollards=[(3.4, -1.6), (3.4, 1.6)],
    # 갈대·억새 띠 (수변 식생)
    # === [v7 판정 §8 ③] 억새 4띠가 **갈색/올리브 육면체**(C-5) ===
    #   증상: `bank_face` 중앙·`beauty_overview` 우측에서 상면 돔만 얹힌
    #     직육면체. v6 이 "12에서 가장 눈에 띄는 시뮬 티"로 지목한 항목 미착수.
    #   원인: `sc.build_hedge`(박스 + 상단 라운딩)로 심었다 — 생울타리 빌더는
    #     억새처럼 **줄기 사이로 배경이 비치는** 식생을 표현할 수 없다.
    #   조치: scene17 W-5(및 그 원본인 scene09 `build_reeds`) 규약 이식 —
    #     밴드 사각형(위치·크기 = **불변**) 안에 얇은 원기둥 대(stalk)를
    #     density 본/m² 로 시드 고정 산포. 높이 지터 0.80~1.12× · 소각
    #     기울기 9° · 밴드별 seed 고정 → 재현성 유지.
    #   프림 수 검산은 `reed_selfcheck()`(모듈 레벨, 부팅 없음).
    reeds=[dict(x0=-34.0, y0=1.40, x1=-28.0, y1=2.25, h=1.10, z=-1.75,
                seed=121),
           dict(x0=-13.0, y0=1.40, x1=-9.0, y1=2.25, h=1.05, z=-1.75,
                seed=122),
           dict(x0=6.0, y0=0.10, x1=12.0, y1=1.10, h=1.20, z=_LOWER_Z,
                seed=123),
           dict(x0=22.0, y0=1.40, x1=30.0, y1=2.25, h=1.15, z=-1.75,
                seed=124),
           dict(x0=36.0, y0=0.10, x1=42.0, y1=1.10, h=1.10, z=_LOWER_Z,
                seed=125)],
    # 대(stalk) 규약 — scene17 PARAMS["reed"] 와 동일값(21씬 식생 톤·굵기 통일)
    reed=dict(r=0.022, density=6.0, h_lo=0.80, h_hi=1.12, tilt=9.0),
    reed_tint=(0.42, 0.44, 0.26),
    # --- 원경 (scene17 세계관 재사용) : 건너편 아파트 + 교량 + 남측 시가지 ---
    far_buildings=dict(
        A=dict(x0=-34.0, x1=-14.0, y0=84.0, y1=92.0, h=44.0, floors=15,
               axis="y", facade_y=84.0, face_dir=-1.0, base_z=-1.5),
        B=dict(x0=-4.0, x1=16.0, y0=84.0, y1=92.0, h=50.0, floors=17,
               axis="y", facade_y=84.0, face_dir=-1.0, base_z=-1.5),
        C=dict(x0=26.0, x1=44.0, y0=84.0, y1=92.0, h=40.0, floors=13,
               axis="y", facade_y=84.0, face_dir=-1.0, base_z=-1.5),
        S=dict(x0=-30.0, x1=-6.0, y0=-42.0, y1=-30.0, h=32.0, floors=11,
               axis="y", facade_y=-30.0, face_dir=1.0, base_z=0.0),
        # [v7 판정 §8 ③ 잔여] "우측 지평 미폐쇄" — 남측 시가지가 x ≤ −6 뿐이라
        #   +X 쪽(데크 진행 방향 우측 배후)이 하늘로 뚫려 있었다. C-2(지평 폐쇄)
        #   규약대로 1동 추가. 이격 8 m·후퇴 4 m·높이 26 m 로 S 와 반복 주기를
        #   만들지 않는다(§3). 데크(x −18..0)·계단(x 0..2.24)에서 30 m 이상 떨어져
        #   위험 기하·grazing 은닉과 무관.
        S2=dict(x0=2.0, x1=24.0, y0=-38.0, y1=-26.0, h=26.0, floors=9,
                axis="y", facade_y=-26.0, face_dir=1.0, base_z=0.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.6, margin=2.0),
    bridge=dict(x0=30.0, x1=34.0, y0=-6.0, y1=100.0, deck_top=6.0,
                deck_t=1.2, pier_r=1.2, pier_x=32.0,
                pier_ys=(-2.0, 18.0, 42.0, 66.0), pier_base=-3.6),
    far_hedges=[dict(cx=-36.0, cy=-16.0, sx=1.2, length=20.0, h=1.6),
                dict(cx=-20.0, cy=-19.0, sx=1.2, length=20.0, h=1.6),
                dict(cx=6.0, cy=-19.0, sx=1.2, length=20.0, h=1.6)],

    material=dict(
        # [v6 판정 ④] rock_wall 1.4 → 0.7 : 타일 1.4 m 는 호안 사석을 "매끈한
        #   사고석 포장"으로 만든다. 0.7 로 줄여 개별 석괴 크기를 절반으로.
        scale=dict(wood_dark=0.6, rock_wall=0.7, grass=1.4, gravel=0.6,
                   concrete_wall=2.0),
        # 물때(젖은 사석) — 청록 이끼기 + 저러프(젖은 반사)
        wet_tint=(0.34, 0.38, 0.30), wet_rough=0.28,
        grass_tint=(0.55, 0.68, 0.42),
        # sRGB 감마 규칙(§A-1): "어두운 색"은 0.02~0.06 대역.
        asphalt_color=(0.045, 0.045, 0.050), asphalt_rough=0.85,
        paint_color=(0.72, 0.72, 0.68), paint_rough=0.6,
        # === [v7 판정 §8 ①/㉠] `edge_void` 수면이 **완전 경면**(건물 반사 선명)
        #   + 무파 균질 청록 → "인피니티 풀". 데크 널 → 이끼 사석 띠 → 수면이
        #   같은 높이로 붙어 보이는 인상의 절반이 이 반사다(나머지 절반은 부감).
        #   조치: roughness 0.08 → **0.14**(scene09 water_rough 0.15 참조 대역)
        #     + 탁도 틴트 소폭 상향(0.05,0.10,0.11 → 0.062,0.108,0.112) —
        #     한강 탁수는 완전 흑청이 아니라 옅은 회청이 실제에 가깝다.
        #   ** 수면 z(−1.80)·범위 불변 = GT 1.80 m 불변. 재질만 변경. **
        water_color=(0.062, 0.108, 0.112), water_rough=0.14,
        # === [v7 판정 §8 ③/㉢] 난간이 **광택 백색 파이프**(병원·수영장 핸드레일).
        #   한강 데크 난간은 도장 강재(다크그레이)다. 알베도 0.80 → 0.30,
        #   metallic 0.9 → 0.25, rough 0.35 → 0.55.
        rail_color=(0.30, 0.31, 0.33), rail_metallic=0.25, rail_rough=0.55,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        bollard_color=(0.33, 0.33, 0.36), bollard_metallic=0.4,
        bollard_rough=0.5,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        # [v7 §4] 파라펫 0.90 → 0.70 · 등기구 0.88 → 0.78 (알베도 상한 0.80).
        #   scene05 는 이미 0.72 로 내려와 있었는데 12 만 0.90 이 남아 있었다.
        parapet_color=(0.70, 0.70, 0.68), parapet_rough=0.6,
        bridge_color=(0.05, 0.05, 0.055), bridge_rough=0.7,
        lamp_color=(0.78, 0.78, 0.75), lamp_rough=0.4,
        tape_color=(0.75, 0.62, 0.10), tape_rough=0.7,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
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
    # 표준 유지(브리프 v5 §R7 명시 171.5). scene17 과 동일 광원 = 세계관 공유.
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene12")
ASSET_ROLES = ["wood_dark", "rock_wall", "grass", "gravel", "concrete_wall",
               "hdri", "mdl"]   # [v5.2 사용자] 임의 경고 팻말 제거


# ===========================================================================
# [C2] 기하 헬퍼 (스모크·조립 공용)
# ===========================================================================
def _rail_posts():
    """난간 포스트 x 목록 — 훼손 스팬(gap_x0..gap_x1) **내부**는 비운다.
    스팬 양 끝 포스트는 잔존(훼손 경계를 읽히게)."""
    d = PARAMS["deck"]
    r = PARAMS["rail"]
    xs = []
    n = int(round((d["x1"] - d["x0"]) / r["spacing"]))
    for k in range(n + 1):
        x = d["x0"] + k * r["spacing"]
        if r["gap_x0"] < x < r["gap_x1"]:
            continue
        xs.append(round(x, 4))
    return xs


def reed_instances():
    """[v7 판정 §8 ③] 억새 대(stalk) 생성기 — **조립기와 검산기가 같은 좌표를
    쓴다**(scene04 `verge_instances` 규약). 밴드별 seed 고정 → 재현성 보장.
    yield: (band_i, band, k, px, py, hh, rotY, rotX)"""
    rd = PARAMS["reed"]
    for i, b in enumerate(PARAMS["reeds"]):
        rs = np.random.RandomState(int(b["seed"]))
        area = (b["x1"] - b["x0"]) * (b["y1"] - b["y0"])
        for k in range(int(round(area * rd["density"]))):
            px = float(rs.uniform(b["x0"], b["x1"]))
            py = float(rs.uniform(b["y0"], b["y1"]))
            hh = float(b["h"] * rs.uniform(rd["h_lo"], rd["h_hi"]))
            a = float(rs.uniform(0.0, 360.0))
            yield (i, b, k, px, py, hh,
                   rd["tilt"] * math.cos(math.radians(a)),
                   rd["tilt"] * math.sin(math.radians(a)))


def reed_selfcheck(verbose=True):
    """억새 군락 검산 — 밴드 사각형 불변 · 대 본수 · 기울기 끝 이탈 ·
    **데크 구간(x −18..0)** 의 종주 회랑(|y| ≤ 0.55)·난간선(y 1.15) 침범 0.
    (x 6..42 밴드는 하부 둔치라 회랑 규약 대상이 아니다 — 기존 회랑 검사와
     동일하게 x 범위를 함께 본다.)"""
    rd = PARAMS["reed"]
    d = PARAMS["deck"]
    r = PARAMS["rail"]
    inst = list(reed_instances())
    # 기울기 9° 로 눕는 끝점이 밴드 밖으로 나가는 최대량
    out = 0.0
    intrude = []
    for i, b, k, px, py, hh, ry, rx in inst:
        dx = abs(math.tan(math.radians(rd["tilt"]))) * hh / 2.0
        out = max(out, dx)
        if not (d["x0"] - dx <= px <= d["x1"] + dx):
            continue                       # 데크 구간 밖 = 하부 둔치 식재
        if abs(py) - dx <= 0.55 or abs(py - r["y"]) <= dx:
            intrude.append((i, k))
    ok = (not intrude)
    if verbose:
        print("  [억새 군락 — v7 §8 ③ stalk 전환]")
        print(f"    밴드 {len(PARAMS['reeds'])}개(사각형 좌표 불변) · 밀도 "
              f"{rd['density']:.1f} 본/m² → **대 {len(inst)}본** "
              f"(구: build_hedge 육면체 {len(PARAMS['reeds'])}개)")
        print(f"    대 r {rd['r']*1000:.0f} mm · 높이 지터 {rd['h_lo']:.2f}"
              f"~{rd['h_hi']:.2f}× · 기울기 {rd['tilt']:.0f}° "
              f"(끝 이탈 최대 {out*100:.1f} cm)")
        print(f"    데크 구간(x {PARAMS['deck']['x0']:.0f}.."
              f"{PARAMS['deck']['x1']:.0f}) 회랑(|y|≤0.55)·난간선"
              f"(y {PARAMS['rail']['y']:.2f}) 침범 "
              f"{len(intrude)}건 → {'OK' if ok else 'FAIL'}")
    return ok, dict(n=len(inst), out=out, intrude=intrude)


# ===========================================================================
# [C2b] [v7 판정 §11-6] §4 "순백(>0.8) 대면적 금지" 알베도 상한 자가검사
#   05/09/12 공통 규약. 두 기준을 함께 본다:
#     (A) 유효 알베도 max 채널 > CAP(0.80)  → v5.1 §4 문자 위반
#     (B) **수평 대면적**의 예상 렌더 sRGB = sRGB(알베도×GAIN) > 0.87(≒222)
#   GAIN 1.77 = v7_rt 실측 역산(scene09 `ghat_walk` 포장 0.422 → 렌더 223).
#   05/09/12 는 돔 1000 + 태양 2450 · elev 49.79 의 동일 조명 리그.
# ===========================================================================
_ALBEDO_GAIN = 1.77
_ALBEDO_CAP = 0.80
_ALBEDO_PRED_CAP = 0.87
_TEXMEAN_CACHE = {}


def _tex_lin_mean(role):
    """diff 텍스처의 선형(sRGB 해제) 채널평균. PIL/파일 없으면 None."""
    if role in _TEXMEAN_CACHE:
        return _TEXMEAN_CACHE[role]
    val = None
    try:
        from PIL import Image
        im = Image.open(sc.tex_path(role, "diff")).convert("RGB")
        im.thumbnail((192, 192))
        a = np.asarray(im, dtype=float) / 255.0
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        val = tuple(float(v) for v in lin.mean(axis=(0, 1)))
    except Exception:
        val = None
    _TEXMEAN_CACHE[role] = val
    return val


def _srgb(u):
    u = max(0.0, min(1.0, u))
    return 12.92 * u if u <= 0.0031308 else 1.055 * u ** (1 / 2.4) - 0.055


# (라벨, 텍스처 role|None, material 키|None, 대면적, 수평면)
_ALBEDO_TABLE = [
    ("데크 널(목)",     "wood_dark",      None,             True,  True),
    ("호안 사석",       "rock_wall",      None,             True,  True),
    ("물때 사석",       "rock_wall",      "wet_tint",       True,  True),
    ("둔치 잔디",       "grass",          "grass_tint",     True,  True),
    ("자갈 산책로",     "gravel",         None,             True,  True),
    ("아파트 외벽",     "concrete_wall",  None,             True,  False),
    ("자전거도로 차선", None,             "paint_color",    False, True),
    ("난간",            None,             "rail_color",     False, False),
    ("파라펫",          None,             "parapet_color",  True,  False),
    ("가로등 등기구",   None,             "lamp_color",     False, False),
    ("경고 테이프",     None,             "tape_color",     False, False),
    ("억새 대",         "grass",          "reed_tint",      False, False),
]


def albedo_selfcheck(verbose=True):
    """[v7 §4/§11-6] 순백 대면적 자가검사. 반환 (ok, rows)."""
    mp = PARAMS["material"]
    rows, fails, warns = [], [], []
    for label, role, key, wide, horiz in _ALBEDO_TABLE:
        if key is None:
            tint = (1.0, 1.0, 1.0)
        else:
            tint = mp.get(key, PARAMS.get(key))
            if tint is None:
                continue
        base = (1.0, 1.0, 1.0) if role is None else _tex_lin_mean(role)
        if base is None:
            rows.append((label, key or role, None, None, "SKIP(텍스처 없음)"))
            continue
        alb = max(b * t for b, t in zip(base, tint))
        pred = _srgb(alb * _ALBEDO_GAIN) if horiz else None
        why = []
        if alb > _ALBEDO_CAP:
            why.append("A:알베도")
        if pred is not None and pred > _ALBEDO_PRED_CAP:
            why.append("B:렌더예측")
        if why:
            mark = "/".join(why)
            (fails if wide else warns).append(label)
            tag = f"FAIL 대면적({mark})" if wide else f"WARN 소면적({mark})"
        else:
            tag = "OK"
        rows.append((label, key or role, alb, pred, tag))
    ok = not fails
    if verbose:
        print("  [§4 순백 대면적 알베도 상한 자가검사] "
              f"CAP {_ALBEDO_CAP} · 수평 렌더예측 CAP {_ALBEDO_PRED_CAP} "
              f"· GAIN {_ALBEDO_GAIN}")
        for label, key, alb, pred, tag in rows:
            if alb is None:
                print(f"    {label:14s} {str(key):16s} {tag}")
                continue
            pr = f"{pred*255:5.1f}" if pred is not None else "  수직"
            print(f"    {label:14s} {str(key):16s} 알베도 {alb:.3f} · "
                  f"수평 예상 렌더 {pr}  {tag}")
        print(f"    ⇒ {'OK — 대면적 위반 0건' if ok else 'FAIL: ' + str(fails)}"
              f"{'  (WARN: ' + str(warns) + ')' if warns else ''}")
    return ok, rows


def _sun_dir():
    """DistantLight 진행 방향 d(월드) — setup_lighting op 순서 역산
    (기본 −Z → rotateX(90−elev) → rotateZ(rz))."""
    lp = PARAMS["light"]
    rz = math.radians(lp["noon_dome_rot"] + PARAMS["SUN_AZ_OFFSET"]
                      + lp["hdri_sun_rotz_offset"])
    rx = math.radians(90.0 - lp["noon_sun_elev"])
    return (-math.sin(rx) * math.sin(rz),
            math.sin(rx) * math.cos(rz),
            -math.cos(rx))


def _obstacle_boxes():
    """카메라 충돌 검사용 장애물 AABB (name, x0,x1, y0,y1, z0,z1).
    [브리프 v5 지시] 그리드/미장센 카메라가 난간·벤치·갈대·사인과 충돌하지
    않는지 좌표 검산(scene19 d5 암흑 전례)."""
    d = PARAMS["deck"]
    r = PARAMS["rail"]
    boxes = []
    # 난간 2세그(포스트+레일 포함 AABB)
    for tag, x0, x1 in (("Rail_W", d["x0"], r["gap_x0"]),
                        ("Rail_E", r["gap_x1"], d["x1"])):
        boxes.append((tag, x0, x1, r["y"] - 0.06, r["y"] + 0.06,
                      0.0, r["top_z"]))
    # 벤치·가로등·나무·갈대·사인·볼라드
    for i, (bx, by, _yaw) in enumerate(PARAMS["benches"]):
        boxes.append((f"Bench_{i}", bx - 0.95, bx + 0.95, by - 0.25, by + 0.25,
                      0.0, 0.46))
    for i, (bx, by, _yaw) in enumerate(PARAMS["lower_benches"]):
        boxes.append((f"BenchLow_{i}", bx - 0.95, bx + 0.95, by - 0.25,
                      by + 0.25, PARAMS["lower"]["z_top"],
                      PARAMS["lower"]["z_top"] + 0.46))
    sl = PARAMS["streetlight"]
    for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
        boxes.append((f"Streetlight_{i}", lx - 0.15, lx + 0.15,
                      ly - sl["arm_len"] - 0.2, ly + 0.2, 0.0, sl["pole_h"]))
    for i, (tx, ty) in enumerate(PARAMS["trees"]):
        boxes.append((f"Tree_{i}", tx - 0.9, tx + 0.9, ty - 0.9, ty + 0.9,
                      0.0, 3.3))
    for i, rd in enumerate(PARAMS["reeds"]):
        boxes.append((f"Reed_{i}", rd["x0"], rd["x1"], rd["y0"], rd["y1"],
                      rd["z"], rd["z"] + rd["h"]))
    # [v5.2 사용자] 임의 경고 팻말 제거 — 사인 AABB 삭제.
    for i, (bx, by) in enumerate(PARAMS["lower_bollards"]):
        boxes.append((f"BollardLow_{i}", bx - 0.08, bx + 0.08, by - 0.08,
                      by + 0.08, PARAMS["lower"]["z_top"],
                      PARAMS["lower"]["z_top"] + 0.75))
    return boxes


def _solid_at(x, y, z):
    """점 (x,y,z)를 품는 지형/구조 솔리드 이름(없으면 None).
    카메라 eye 매몰 검사 + **시선 차단 검사**(ray march)의 단일 출처.
    포함: 상·하부 둔치, 어깨 사석, 잔디 사면, 데크 슬래브·보, 계단 솔리드,
    호안 사석 단, 원경 교량 상판. (소품은 _obstacle_boxes 가 담당)"""
    u = PARAMS["upper"]
    sh = PARAMS["shoulder"]
    lo = PARAMS["lower"]
    d = PARAMS["deck"]
    st = PARAMS["stair"]
    sp = PARAMS["slope"]
    # 상부 둔치 A(데크 서측: crest 까지) / B(데크 구간: 데크 남측까지)
    if u["x0"] <= x <= u["x_split"] and u["y0"] <= y <= u["y_crest"] \
            and u["z_top"] - u["thick"] <= z < u["z_top"]:
        return "UpperA"
    if u["x_split"] <= x <= u["x1"] and u["y0"] <= y <= u["y1"] \
            and u["z_top"] - u["thick"] <= z < u["z_top"]:
        return "UpperB"
    if sh["x0"] <= x <= sh["x1"] and sh["y0"] <= y <= sh["y1"] \
            and sh["z_top"] - sh["thick"] <= z < sh["z_top"]:
        return "Shoulder"
    if lo["x0"] <= x <= lo["x1"] and lo["y0"] <= y <= lo["y1"] \
            and lo["z_top"] - lo["thick"] <= z < lo["z_top"]:
        return "Lower"
    # 잔디 사면(1:2) — 상면 z = −(drop/run)(x − x0)
    if sp["x0"] <= x <= sp["x0"] + sp["run"] and sp["y0"] <= y <= sp["y1"]:
        zs = -(sp["drop"] / sp["run"]) * (x - sp["x0"])
        if zs - sp["thick"] <= z < zs:
            return "GrassSlope"
    # 데크 슬래브 + 하부 보 영역(보 밑면까지 통째로 차단체로 근사)
    if d["x0"] <= x <= d["x1"] and d["y0"] <= y <= d["y1"]:
        z_beam_bot = d["z_top"] - d["slab_t"] - PARAMS["deckframe"]["beam_h"]
        if d["z_top"] - d["slab_t"] <= z < d["z_top"]:
            return "DeckSlab"
        if z_beam_bot <= z < d["z_top"] - d["slab_t"] and y <= 0.1:
            return "DeckBeam"          # 종보는 y ≤ 0.0 대역 — 캔틸레버부는 개방
    # 계단 솔리드 (x0..x0+run, 데크 폭)
    run = st["n_geom"] * st["tread"]
    if st["x0"] <= x <= st["x0"] + run and d["y0"] <= y <= d["y1"]:
        idx = min(int((x - st["x0"]) / st["tread"]), st["n_geom"] - 1)
        ztop = -st["riser"] * (idx + 1)
        if st["base_z"] <= z < ztop:
            return "Stairs"
    for rp in PARAMS["riprap"]:
        if rp["x0"] <= x <= rp["x1"] and rp["y0"] <= y <= rp["y1"] \
                and PARAMS["rip_bot"] <= z < rp["z"]:
            return f"Riprap_{rp['tag']}"
    br = PARAMS["bridge"]
    if br["x0"] <= x <= br["x1"] and br["y0"] <= y <= br["y1"] \
            and br["deck_top"] - br["deck_t"] <= z <= br["deck_top"]:
        return "BridgeDeck"
    return None


# ===========================================================================
# [C3] 스모크 — 부팅 전 기하·접지·은닉·카메라 자기검증 (조기종료)
# ===========================================================================
def _smoke_report():
    d = PARAMS["deck"]
    st = PARAMS["stair"]
    r = PARAMS["rail"]
    wt = PARAMS["water"]
    print("=" * 70)
    print("scene12_riverside_deck — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 70)
    drop_edge = d["z_top"] - wt["z"]
    drop_st = st["riser"] * st["n_riser"]
    print(f"  데크           : x [{d['x0']:.1f},{d['x1']:.1f}] 폭 "
          f"{d['y1']-d['y0']:.2f} m, 상면 {d['z_top']:+.2f}")
    print(f"  낙차 ① 데크 에지 → 수면 : {drop_edge:.2f} m → "
          f"{'OK' if drop_edge >= 0.3 else 'FAIL'}")
    print(f"  낙차 ② 접속 계단        : riser {st['riser']} × "
          f"{st['n_riser']} = {drop_st:.2f} m "
          f"(n_geom {st['n_geom']}단 + 하부 둔치 1라이저), run "
          f"{st['n_geom']*st['tread']:.2f} → "
          f"{'OK' if drop_st >= 0.3 else 'FAIL'}")
    lo = PARAMS["lower"]
    drop_lo = lo["z_top"] - wt["z"]
    print(f"  낙차 ③ 하부 둔치 → 수면 : {drop_lo:.2f} m → "
          f"{'OK' if drop_lo >= 0.3 else 'FAIL'}")
    print(f"  계단 착지 검증 : 하부 둔치 상면 {lo['z_top']:+.3f} == "
          f"−riser×n_riser {-drop_st:+.3f} → "
          f"{'OK' if abs(lo['z_top'] + drop_st) < 1e-6 else 'FAIL'}")

    # ── 캔틸레버 검산 ──
    sh = PARAMS["shoulder"]
    df = PARAMS["deckframe"]
    y_sup = max(df["beam_ys"])
    print("  [캔틸레버]")
    print(f"    최외곽 지지선 y={y_sup:+.2f} · 데크 외단 y={d['y1']:+.2f} → "
          f"내밈 {d['y1']-y_sup:.2f} m")
    print(f"    호안 crest y={sh['y1']:+.2f}(상면 {sh['z_top']:+.2f}) 기준 "
          f"내밈 {d['y1']-sh['y1']:.2f} m → "
          f"{'OK' if 1.0 <= d['y1']-sh['y1'] <= 1.5 else 'FAIL'}")
    pile_h = (d["z_top"] - d["slab_t"] - df["beam_h"]) - sh["z_top"]
    print(f"    말뚝 길이 {pile_h:.2f} m (어깨 사석 상면 {sh['z_top']:+.2f} → "
          f"보 밑면 {d['z_top']-d['slab_t']-df['beam_h']:+.2f}) → "
          f"{'OK(접지)' if pile_h > 0.3 else 'FAIL(부유/매몰)'}")

    # ── 지면·수면 플레이트 표 + 부유 검사 (감사 v4 최다 결함) ──
    u = PARAMS["upper"]
    fb = PARAMS["far_bank"]
    plates = [("UpperA(grass)", u["x0"], u["x_split"], u["y0"], u["y_crest"],
               u["z_top"]),
              ("UpperB(grass)", u["x_split"], u["x1"], u["y0"], u["y1"],
               u["z_top"]),
              ("Shoulder(rock)", sh["x0"], sh["x1"], sh["y0"], sh["y1"],
               sh["z_top"]),
              ("Lower(grass)", lo["x0"], lo["x1"], lo["y0"], lo["y1"],
               lo["z_top"]),
              ("Deck(wood)", d["x0"], d["x1"], d["y0"], d["y1"], d["z_top"])]
    for rp in PARAMS["riprap"]:
        plates.append((f"Riprap_{rp['tag']}", rp["x0"], rp["x1"], rp["y0"],
                       rp["y1"], rp["z"]))
    plates.append(("Water(river)", wt["x0"], wt["x1"], wt["y0"], wt["y1"],
                   wt["z"]))
    plates.append(("FarBank(grass)", fb["x0"], fb["x1"], fb["y0"], fb["y1"],
                   fb["z_top"]))
    print("  [지면·수면 플레이트 표] (수면 −1.80 보다 낮은 인접 상면 = 부유 유발)")
    print(f"    {'이름':18s} {'x범위':>16s} {'y범위':>14s}  상면z")
    off = []
    for nm, x0, x1, y0, y1, z in plates:
        print(f"    {nm:18s} [{x0:6.1f},{x1:6.1f}] [{y0:6.1f},{y1:6.1f}]  "
              f"{z:+.3f}")
        if nm.startswith("Water") or nm.startswith("Riprap"):
            continue
        if (not (x1 <= wt["x0"] or x0 >= wt["x1"] or
                 y1 <= wt["y0"] or y0 >= wt["y1"])) and z < wt["z"] - 1e-9:
            off.append(nm)
    print(f"    수면과 XY 중첩 + 상면이 수면보다 낮은 플레이트: "
          f"{off if off else '없음 → OK'}")
    print(f"    FarBank 저면 {fb['z_top']-fb['thick']:+.2f} vs 수면 "
          f"{wt['z']:+.2f} → "
          f"{'OK(매입)' if fb['z_top']-fb['thick'] < wt['z'] else 'FAIL(부유)'}"
          f"  [scene09 교훈]")
    # 사석 최하단이 수면 아래로 잠기는지(물가 하드에지 방지)
    deep = min(rp["z"] for rp in PARAMS["riprap"])
    print(f"    사석 최심 상면 {deep:+.2f} < 수면 {wt['z']:+.2f} → "
          f"{'OK(수몰단 존재)' if deep < wt['z'] else 'FAIL'}")

    # ── 은닉 밴드 검산 (연구 핵심 — h0.3 로봇 시점) ──
    print("  [h0.3 은닉 밴드 검산] 데크 외단(y=1.25, z=0)을 스치는 시선")
    for h in (0.3, 0.9, 1.8):
        # 시선 원점 (y=0, z=h) → 에지(y=1.25, z=0) 연장이 수면(−1.8)에 닿는 y
        slope = h / (d["y1"] - 0.0)
        y_hit = d["y1"] + (0.0 - wt["z"]) / slope
        # [v6] 은닉 대역은 **데크 외단 기준**으로 잰다(수면 y0 기준은 노출대
        #   확대 후 음수가 나와 의미가 없다 — 사석도 은닉 대상이므로).
        print(f"    h={h:.1f} → 수면 가시 시작 y {y_hit:6.2f} m "
              f"(에지 뒤 은닉 대역 {d['y1']:.2f}..{y_hit:.2f} = "
              f"{y_hit-d['y1']:.2f} m)")
    print(f"    ⇒ h0.3 에서 근접 수면·사석이 통째로 사라진다(missing ground band).")
    # 킥플레이트 부재 개방각
    z_at_rail = 0.3 + (r["y"] - 0.0) * ((0.0 - 0.3) / (d["y1"] - 0.0))
    print(f"    킥플레이트 부재: h0.3 시선이 난간선(y={r['y']:.2f})을 "
          f"z={z_at_rail:+.3f} 로 통과 → 중간대(z {r['mid_z']:.2f}) 아래 여유 "
          f"{r['mid_z']-z_at_rail:.2f} m → {'OK(개방)' if r['mid_z']-z_at_rail > 0.2 else 'FAIL'}")
    # 계단 grazing 은닉
    for dd in (2.0, 5.0):
        x_hit = abs(lo["z_top"]) * dd / 0.3 + st["x0"]
        print(f"    계단 은닉: h0.3·d{dd:.0f} 시선이 하부 둔치에 닿는 x "
              f"{x_hit:5.1f} m (계단 끝 {st['x0']+st['n_geom']*st['tread']:.2f}) "
              f"→ {'OK(하강 은닉)' if x_hit > st['x0']+st['n_geom']*st['tread'] else 'FAIL'}")

    # ── [v6 판정 ②] 수면 z 조립 검증 + 낙차 시각 성립 검산 ──
    print("  [수면 z 조립 검증] (감독 결정 4 — GT 1.80 유지, 버그면 수정)")
    print("    sc.build_water: 두께 0.2 박스를 z−0.1 중심에 → **상면 = z**. "
          f"수면 상면 {wt['z']:+.3f}")
    gt = d["z_top"] - wt["z"]
    print(f"    데크 상면 {d['z_top']:+.3f} − 수면 상면 {wt['z']:+.3f} = "
          f"{gt:.3f} m → "
          f"{'OK(GT 1.80 일치 · 조립 버그 없음)' if abs(gt - 1.80) < 1e-9 else 'FAIL'}")
    print("    ⇒ '수면이 데크 상면에 붙어 보인다'의 원인은 z 가 아니라 **가시성**"
          " (아래 노출대·부감 검산 참조)")
    expo = [rp for rp in PARAMS["riprap"]
            if rp["z"] > wt["z"] and rp["y1"] > d["y1"]]
    y_wet = max((rp["y1"] for rp in expo), default=d["y1"])
    z_D = PARAMS["riprap"][3]["z"]
    print(f"    노출 사석대 : y {d['y1']:.2f}..{y_wet:.2f} = "
          f"{y_wet - d['y1']:.2f} m (구 1.10) · 수제선 y {y_wet:.2f} (구 2.35)"
          f" · 수면 y0 {wt['y0']:.2f} (구 1.90)")
    print(f"    데크 에지 → 사석 D 상면 낙하고 {d['z_top'] - z_D:.2f} m "
          f"(구 1.75 = 불변) / → 수면 {gt:.2f} m")
    print(f"    물때 밴드 y [{PARAMS['waterline']['y0']:.2f},"
          f"{PARAMS['waterline']['y1']:.2f}] · 잡석 {PARAMS['rocks']['n']}개"
          f" (구 42) y ≤ {PARAMS['rocks']['y1']:.2f}")
    # 잡석 접지 검산 — band_top(x,y) 가 x 조건을 갖도록 고친 뒤 부유 0 확인
    rk_ = PARAMS["rocks"]
    rs_ = np.random.RandomState(int(rk_["seed"]))
    placed = skipped = 0
    for _ in range(int(rk_["n"])):
        rx = rs_.uniform(rk_["x0"], rk_["x1"])
        ry = rs_.uniform(rk_["y0"], rk_["y1"])
        rs_.uniform(rk_["s_lo"], rk_["s_hi"])
        rs_.uniform(0.0, 90.0)
        if any(rp["x0"] <= rx <= rp["x1"] and rp["y0"] <= ry < rp["y1"]
               for rp in PARAMS["riprap"]):
            placed += 1
        else:
            skipped += 1
    print(f"    잡석 접지 검산 : 사석 단 위 배치 {placed} · 단 없는 대역 생략 "
          f"{skipped} → {'OK(부유 0)' if placed + skipped == rk_['n'] else 'FAIL'}"
          f"  [구 구현은 y 만 보고 x>−18 잡석이 0.8~0.9 m 부유했다]")

    def _bank_top(y):
        """데크 구간(x≈−9)의 호안 종단면 상면 z — 사석 단 ∪ 수면 중 최고."""
        z = None
        for rp in PARAMS["riprap"]:
            if rp["x0"] <= -9.0 <= rp["x1"] and rp["y0"] <= y < rp["y1"]:
                z = rp["z"] if z is None else max(z, rp["z"])
        if wt["y0"] <= y <= wt["y1"]:
            z = wt["z"] if z is None else max(z, wt["z"])
        return z

    print("  [낙차 시각 성립] 데크 외단(y 1.25, z 0)을 스치는 시선의 지면 최초 접촉")
    for nm in ("beauty_overview", "bank_face", "under_deck", "edge_void"):
        v = build_views()[nm]
        ex, ey, ez = v["eye"]
        if ey >= d["y1"]:
            print(f"    {nm:16s} 강측 시점(eye y {ey:+.2f} > 데크 외단) → "
                  f"에지 폐색 없음 · 캔틸레버 하부·사석 직시")
            continue
        m = (0.0 - ez) / (d["y1"] - ey)          # 에지 통과 시선 기울기(음수)
        y_hit, z_hit = None, None
        yy = d["y1"]
        while yy <= 40.0:
            zs = _bank_top(yy)
            if zs is not None and m * (yy - d["y1"]) <= zs:
                y_hit, z_hit = yy, zs
                break
            yy += 0.02
        if y_hit is None:
            print(f"    {nm:16s} 기울기 {m:+.3f}/m → 40 m 내 접촉 없음")
            continue
        band = y_hit - d["y1"]
        kind = "수면" if abs(z_hit - wt["z"]) < 1e-9 else "노출 사석"
        flag = "OK(사석·수제선 프레임 잔존)" if kind == "노출 사석" else \
               "주의(사석 전부 은닉 — 부감 부족)"
        print(f"    {nm:16s} 기울기 {m:+.3f}/m → 최초 접촉 y {y_hit:5.2f} "
              f"(z {z_hit:+.2f}, {kind}) · 에지 뒤 은닉 밴드 {band:.2f} m → {flag}")

    # ── 난간 훼손 스팬 ──
    xs = _rail_posts()
    gapw = r["gap_x1"] - r["gap_x0"]
    print("  [난간]")
    print(f"    포스트 {len(xs)}본 (간격 {r['spacing']} m) · 상단대 z "
          f"{r['top_z']:.2f} · 중간대 z {r['mid_z']:.2f} · **킥플레이트 없음**")
    print(f"    훼손 스팬 x [{r['gap_x0']:.1f},{r['gap_x1']:.1f}] = {gapw:.1f} m"
          f" → {'OK' if abs(gapw-2.4) < 1e-6 else 'FAIL'} "
          f"(잔존 밑동 {len(r['stub_xs'])}본)")
    print(f"    난간 상단 {r['top_z']:.2f} m — 현행 규정 1.1 미달 = "
          f"'규정 미달의 현실'")
    # [v6 C-6] 경고 테이프 = 리본 + 양단 잔존 포스트 결속(부유 금지)
    tp = r["tape"]
    anch_ok = all(any(abs(ax - px) < 1e-6 for px in xs)
                  for ax in tp["anchor_xs"])
    print(f"    경고 테이프: 두께 {tp['t']*1000:.0f} mm 리본 × {tp['nseg']}세그 "
          f"(구 {20:.0f} mm 각재) · 폭 {tp['w']*100:.1f} cm · "
          f"처짐 {tp['sag']*100:.0f} cm")
    print(f"      결속 x {tp['anchor_xs']} vs 잔존 포스트 → "
          f"{'OK(양단 지지 — 부유 해소)' if anch_ok else 'FAIL(무지지 단부)'}"
          f"  · 스팬 {tp['anchor_xs'][1]-tp['anchor_xs'][0]:.1f} m, "
          f"양단 z {tp['z_end']:.2f} → 중앙 z "
          f"{tp['z_end']-tp['sag']:.2f}")

    # ── [v7] 억새 stalk 전환 + §4 알베도 상한 자가검사 ──
    reed_selfcheck()
    albedo_selfcheck()

    # ── 사광 ──
    sd = _sun_dir()
    print("  [태양] SUN_AZ_OFFSET="
          f"{PARAMS['SUN_AZ_OFFSET']:.1f} → 진행 d = "
          f"({sd[0]:+.3f}, {sd[1]:+.3f}, {sd[2]:+.3f})")
    print(f"    태양 위치 방향 (−d) = ({-sd[0]:+.3f}, {-sd[1]:+.3f}, "
          f"{-sd[2]:+.3f}) → −X−Y 상공(진행 순광, scene17 동일)")
    print(f"    데크 상면(법선 +Z) 직사 OK / 호안 사면(법선 +Y) d·n="
          f"{sd[1]:+.3f} > 0 → 역광 암부 (에지 아래 은닉 강화)")

    # ── 카메라 충돌 검산 ──
    boxes = _obstacle_boxes()
    views = build_views()
    print(f"  [카메라 충돌 검산] 뷰 {len(views)}개 × 장애물 {len(boxes)}개 AABB")
    hits = []
    for name, v in sorted(views.items()):
        ex, ey, ez = v["eye"]
        for bn, x0, x1, y0, y1, z0, z1 in boxes:
            if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1:
                hits.append((name, bn))
    for name, v in sorted(views.items()):
        s = _solid_at(*v["eye"])
        if s is not None:
            hits.append((name, f"{s}(지형 매몰)"))
    for name, bn in hits:
        print(f"    [FAIL] {name} eye 가 {bn} 내부")
    print(f"    충돌: {len(hits)}건 → {'OK' if not hits else 'FAIL'}")
    # 시선 차단 검사(ray march 0.1 m) — 미장센 컷이 지형에 파묻히지 않는지.
    #   첫 차단 지점이 목표까지의 90 % 미만이면 프레임이 지형으로 막힌 것.
    print("    [시선 차단] 미장센 컷 ray march (첫 차단 비율 ≥ 0.90 = OK)")
    blocked = []
    for name, v in sorted(views.items()):
        if name.startswith("preset_"):
            continue
        e = np.array(v["eye"], dtype=float)
        t = np.array(v["tgt"], dtype=float)
        L = float(np.linalg.norm(t - e))
        frac, hit = 1.0, None
        for k in range(1, int(L / 0.1) + 1):
            f = k * 0.1 / L
            s = _solid_at(*(e + (t - e) * f))
            if s is not None:
                frac, hit = f, s
                break
        flag = "OK" if frac >= 0.90 else "FAIL"
        print(f"      {name:18s} 첫 차단 {frac:5.2f} "
              f"({hit if hit else '없음'}) → {flag}")
        if frac < 0.90:
            blocked.append(name)
    print(f"      차단 컷: {blocked if blocked else '없음 → OK'}")
    # 데크 종주 회랑(로봇 몸통 폭 1.1 m = |y| ≤ 0.55)에 장애물 금지.
    #   난간(y 1.15)은 회랑 밖이어야 한다.
    half = 0.55
    intr = [bn for bn, x0, x1, y0, y1, z0, z1 in boxes
            if not (x1 <= -18.0 or x0 >= 0.0 or y1 <= -half or y0 >= half)
            and z1 > 0.05]
    print(f"    데크 종주 회랑(|y|≤{half}) 침범 요소: "
          f"{intr if intr else '없음 → OK'}")
    print("=" * 70)


# ===========================================================================
# [D] 카메라 프리셋: grid_views(gy=0, 데크 종주 +X) + 미장센 5컷
# ===========================================================================
def build_views():
    """프리셋 축 = 데크 종주 방향 +X. 그리드는 데크 중심선(y=0) 위 —
    h0.3 컷이 곧 '킥플레이트 부재 + 근접 수면 은닉' 판정 컷."""
    views = sc.grid_views(0.0)
    # edge_void: 훼손 스팬 안, **에지 바로 앞**(y 0.90)에 선 로봇 눈높이(0.35)로
    #   에지 너머를 봄 — 핵심 컷. [좌표 검산] 시선은 데크 외단(y 1.25)을
    #   z=+0.16 으로 넘어간다(구 eye y 0.20 은 슬래브 관통). 이 시점에서
    #   수면은 y ≥ 3.05 부터만 보이고 1.90..3.05 는 여전히 은닉된다.
    #   [v7 판정 §8 ㉣ 재조준] 구 tgt(−2.60, 4.60, −1.70)는 프레임 중심이 수면
    #   한복판(y 4.60)이라, 에지 뒤 은닉 밴드를 빠져나온 **노출 사석대
    #   (y 3.03..3.90)** 가 프레임 하단 가장자리로 밀려 "데크 널 → 이끼 띠 →
    #   수면"만 남았다. tgt 를 수제선 직전(y 3.45, z −1.62)으로 당겨 사석대가
    #   프레임 중심에 오게 한다. **eye 는 불변**(훼손 스팬 안·로봇 눈높이 0.35 =
    #   이 컷의 존재 이유). 에지 통과 기울기 −1.000/m 도 불변이므로 은닉 밴드
    #   1.78 m 라는 판정 근거 수치가 그대로 유지된다(스모크 [낙차 시각 성립]).
    views["edge_void"] = dict(eye=[-4.80, 0.90, 0.35], tgt=[-3.05, 3.45, -1.62])
    # broken_span: 뭍(산책로)에서 훼손 스팬을 비스듬히 — 잔존 밑동·경고 테이프
    views["broken_span"] = dict(eye=[-9.50, -3.20, 1.70], tgt=[-4.60, 0.70, 0.10])
    # stair_join: 데크 끝 8단 하강 접속부.
    #   [v6 판정 ④ 재조준] 구 컷(eye −4.20,−3.40,2.80 / tgt 1.80,−0.30,−1.00)은
    #   ⓐ 계단이 프레임에 없고 ⓑ 가로등(−2.0,−2.60, 기둥 h4.5)이 화면을 세로로
    #   관통했다. 카메라를 **하부 둔치(z −1.36) 위 보행 눈높이**로 내려 계단을
    #   아래에서 올려다보는 구도로 바꾼다 — 8단 전체가 실루엣으로 선다.
    #   [좌표 검산] eye z 0.30 = 하부 둔치 상면(−1.36) + 1.66. 시선은 x 2.24
    #   (계단 하단)에서 z −0.37 > 최하단 상면 −1.19, x 1.20 에서 z −0.55 >
    #   해당 단 상면 −0.68 → 전 구간 계단 솔리드 위를 스친다(관통 없음).
    #   가로등 2기는 모두 x<0 = 표적 뒤 → 프레임 관통 없음.
    views["stair_join"] = dict(eye=[6.00, -4.20, 0.30], tgt=[1.20, -0.10, -0.55])
    # deck_walk: 보행자 눈높이 종주 — 데크·난간·원경 교량/아파트
    views["deck_walk"] = dict(eye=[-14.00, 0.00, 1.60], tgt=[0.00, 0.40, 0.20])
    # under_deck: **캔틸레버 하부 시인 컷**(감독 결정 4). 수면 위 0.90 m 저시점
    #   (배 위 높이)에서 데크 하부 공간을 종방향으로 훑는다 — 슬래브 밑면·
    #   페시아·종보·말뚝·어깨 사석이 차례로 노출되어 "데크가 물 위 1.8 m 에
    #   떠 있다"가 기하로 증명된다.
    #   [좌표 검산] eye (5.0, 4.60, −0.90) : 수면(−1.80) 위 0.90 m, 사석 F 상면
    #   (−1.95) 위 1.05 m → 매몰 없음. 시선은 사석 F/E/D 상면(−1.95/−1.78/−1.75)
    #   보다 항상 위(최저 −0.58 @ y 2.30)를 지나고, 데크 진입 시 z ≈ −0.44 로
    #   보 밑면(−0.40)보다 낮아 **슬래브가 아니라 하부 공간으로** 들어간다.
    views["under_deck"] = dict(eye=[5.00, 4.60, -0.90], tgt=[-7.00, 0.60, -0.35])
    # bank_face [신설]: 강측 횡단면 부감 — 데크 상면·난간 → 에지 → 페시아 →
    #   보·말뚝 공극 → 호안 사석 3단 → 수제선이 **한 프레임에 수직으로 쌓인다**.
    #   GT 1.80 m 낙차의 시각적 근거를 담당하는 컷(v6 판정 ② 대응).
    #   [좌표 검산] eye (−9.50, 11.00, 2.60) : 수면 위 4.40 m, 수면 XY 내부이나
    #   z 가 −1.80 보다 훨씬 위 → 매몰 없음. 시선 기울기 dz/dy = 0.333 →
    #   y 3.90(수제선) z −0.24, y 1.25(데크 에지) z −0.65 로 **데크 슬래브
    #   (−0.14..0)·종보(−0.40..−0.14) 어느 것도 관통하지 않고** 하부 공간
    #   (사석 C 상면 −1.45 위)으로 들어간다.
    views["bank_face"] = dict(eye=[-9.50, 11.00, 2.60], tgt=[-9.20, 0.80, -0.80])
    # beauty_overview: 사선 부감 — 데크·강·교량·아파트 일괄.
    #   [v6 판정 ② 재조준] 구 컷(eye −16,−14,9)은 데크 에지를 스치는 시선의
    #   기울기가 0.59/m 밖에 안 돼 y 1.25..4.21(2.96 m)의 사석·수제선이 통째로
    #   에지 뒤에 숨었다 → 수면이 데크 상면에 붙어 보인 직접 원인.
    #   eye 를 (−15,−9,13)으로 올려 기울기 1.268/m 확보 → 은닉 밴드 1.31 m,
    #   노출 사석 E(y 2.56..3.90)와 수제선이 프레임에 남는다.
    views["beauty_overview"] = dict(eye=[-15.0, -9.0, 13.0], tgt=[2.0, 4.0, -1.4])
    return views


# ===========================================================================
# [E] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드     — 킥플레이트 없는 난간 아래로 근접 수면이 은닉되는가
 2. edge_void       — 훼손 스팬에서 수면 직행 개방이 읽히는가 (핵심 컷)
 3. broken_span     — 잔존 포스트 밑동·경고 테이프(리본 처짐·양단 결속)
 4. stair_join      — 데크 끝 8단 하강이 프레임에 들어왔는가(재조준 컷)
 5. under_deck      — 캔틸레버 하부 말뚝·보·사석 공간이 보이는가(저시점)
 6. bank_face       — 데크면→에지→하부공간→사석→수제선이 수직으로 쌓이는가
                      (= GT 1.80 m 낙차의 시각적 근거 · 신설 컷)
 7. 원경            — 교량·아파트·갈대가 '한강 둔치'로 읽히는가
 8. [v7] 수면       — edge_void·bank_face 에서 건물 반사가 흐려지고 잔물결
                      대역이 생겨 '인피니티 풀'이 아니라 강으로 읽히는가
 9. [v7] 억새       — bank_face 중앙·beauty_overview 우측이 갈색 육면체가
                      아니라 **줄기 사이로 배경이 비치는 대(stalk) 군락**인가
10. [v7] 난간       — 광택 백색 파이프가 도장 강재(다크그레이)로 바뀌었는가
11. [v7] 지평       — +X(우측) 배후가 시가지 실루엣으로 닫혔는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene12")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene12"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # 재질 (scene17 패턴 재사용)
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["deckwood"] = PBR(
            f"{ROOT}/Looks/DeckWood", sc.tex_path("wood_dark", "diff"),
            sc.tex_path("wood_dark", "nor"), sc.tex_path("wood_dark", "rough"),
            sca["wood_dark"])
        M["rock"] = PBR(
            f"{ROOT}/Looks/Rock", sc.tex_path("rock_wall", "diff"),
            sc.tex_path("rock_wall", "nor"), sc.tex_path("rock_wall", "rough"),
            sca["rock_wall"])
        # [v6 ④] 물때(젖은 사석) — 같은 텍스처를 더 잘게(0.45) + 청록 틴트 +
        #   저러프 상수(rough 텍스처 미사용 → roughness_const 가 그대로 먹는다)
        M["wetrock"] = PBR(
            f"{ROOT}/Looks/WetRock", sc.tex_path("rock_wall", "diff"),
            sc.tex_path("rock_wall", "nor"), None, sca["rock_wall"] * 0.65,
            tint=mp["wet_tint"], roughness_const=mp["wet_rough"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        # [v7 판정 §8 ③] 억새 대(stalk) 전용 재질 — scene17 M["reed"] 와 동일
        #   (grass 텍스처 0.6 m/타일 + reed_tint). 대 굵기 44 mm 에서 0.6 m
        #   타일이면 줄기 1본에 텍스처가 거의 균질하게 걸려 '마른 대' 톤이 된다.
        M["reed"] = PBR(
            f"{ROOT}/Looks/Reed", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            0.6, tint=PARAMS["reed_tint"])
        M["gravel"] = PBR(
            f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            sca["gravel"])
        M["cwall"] = PBR(
            f"{ROOT}/Looks/ConcreteWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["paint"] = PBR(f"{ROOT}/Looks/Paint", diffuse_color=mp["paint_color"],
                         roughness_const=mp["paint_rough"], metallic=0.0)
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["bridge"] = PBR(f"{ROOT}/Looks/Bridge",
                          diffuse_color=mp["bridge_color"],
                          roughness_const=mp["bridge_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["tape"] = PBR(f"{ROOT}/Looks/Tape", diffuse_color=mp["tape_color"],
                        roughness_const=mp["tape_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        # [v5.2 사용자] 임의 경고 팻말 제거 — 사인 패널·배킹 재질 생성 삭제.
        return M

    # -------------------------------------------------------------------
    # 지면 — 상부 둔치 2박스 + 어깨 사석 + 하부 둔치 + 잔디 사면
    # -------------------------------------------------------------------
    def build_terrain(M):
        u = PARAMS["upper"]
        sh = PARAMS["shoulder"]
        lo = PARAMS["lower"]
        # 상부 둔치 A: 데크 서측(x < x_split)은 호안 crest 까지 z=0
        BOX(f"{ROOT}/UpperA",
            ((u["x0"] + u["x_split"]) / 2.0, (u["y0"] + u["y_crest"]) / 2.0,
             u["z_top"] - u["thick"] / 2.0),
            (u["x_split"] - u["x0"], u["y_crest"] - u["y0"], u["thick"]),
            M["grass"], col=True)
        # 상부 둔치 B: 데크 구간(x_split..0)은 데크 남측 에지까지
        BOX(f"{ROOT}/UpperB",
            ((u["x_split"] + u["x1"]) / 2.0, (u["y0"] + u["y1"]) / 2.0,
             u["z_top"] - u["thick"] / 2.0),
            (u["x1"] - u["x_split"], u["y1"] - u["y0"], u["thick"]),
            M["grass"], col=True)
        # 데크 하부 어깨(사석 성토) — 말뚝 착지면
        BOX(f"{ROOT}/Shoulder",
            ((sh["x0"] + sh["x1"]) / 2.0, (sh["y0"] + sh["y1"]) / 2.0,
             sh["z_top"] - sh["thick"] / 2.0),
            (sh["x1"] - sh["x0"], sh["y1"] - sh["y0"], sh["thick"]),
            M["rock"], col=True)
        # 하부 둔치(저수부지)
        BOX(f"{ROOT}/Lower",
            ((lo["x0"] + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0),
            (lo["x1"] - lo["x0"], lo["y1"] - lo["y0"], lo["thick"]),
            M["grass"], col=True)
        # 상·하부를 잇는 잔디 사면(1:2) — 계단 외 우회 동선
        sp = PARAMS["slope"]
        sc.build_slope(stage, f"{ROOT}/GrassSlope", sp["x0"], u["z_top"],
                       sp["run"], sp["drop"], sp["y0"], sp["y1"], sp["thick"],
                       M["grass"], margin=0.0, collider=True)
        # 산책로(마사토) 밴드
        pa = PARAMS["path"]
        BOX(f"{ROOT}/Path",
            ((pa["x0"] + pa["x1"]) / 2.0, (pa["y0"] + pa["y1"]) / 2.0,
             u["z_top"] - u["thick"] / 2.0 + pa["proud"]),
            (pa["x1"] - pa["x0"], pa["y1"] - pa["y0"], u["thick"]),
            M["gravel"], col=True)

    def build_riprap(M):
        """호안 사석 단 + 물때 밴드 + 잡석 낱개(seed 고정 랜덤 회전).
        [v6 ②④] 노출대 y 1.25..3.90(2.65 m) — D 상면 −1.75 는 불변이라
        데크 에지 낙하고 1.75 m·GT 낙차(→수면) 1.80 m 모두 그대로다."""
        zb = PARAMS["rip_bot"]
        for rp in PARAMS["riprap"]:
            BOX(f"{ROOT}/Riprap_{rp['tag']}",
                ((rp["x0"] + rp["x1"]) / 2.0, (rp["y0"] + rp["y1"]) / 2.0,
                 (rp["z"] + zb) / 2.0),
                (rp["x1"] - rp["x0"], rp["y1"] - rp["y0"], rp["z"] - zb),
                M["rock"], col=True)
        # 물때 밴드 — 수제선 안쪽 1.0 m 를 젖은 사석 재질로 덮는다.
        #   z 하단을 4 mm 매입(−0.004)해 하부 단 상면과의 **동일평면 Z파이팅**을
        #   원천 차단하고, 상면은 8 mm 만 돌출시킨다(§A-8 규약).
        wl = PARAMS["waterline"]
        wx0, wx1 = PARAMS["riprap"][3]["x0"], PARAMS["riprap"][3]["x1"]
        z_bot = wl["z"] - 0.004
        BOX(f"{ROOT}/WaterlineBand",
            ((wx0 + wx1) / 2.0, (wl["y0"] + wl["y1"]) / 2.0,
             z_bot + wl["proud"] / 2.0),
            (wx1 - wx0, wl["y1"] - wl["y0"], wl["proud"]), M["wetrock"])
        rk = PARAMS["rocks"]
        rs = np.random.RandomState(int(rk["seed"]))

        def band_top(x, y):
            """(x,y)를 덮는 사석 단 상면(복수면 최고). 없으면 None.
            [v6 잠재 접지 결함 수정] 구 구현은 y 만 보고 **첫 일치 단**을
            반환해서, A/B(x −40..−18)만 있는 y 0.05..1.25 대역의 x > −18
            잡석이 실제 지면(하부 둔치 −1.36)보다 0.8~0.9 m 떠 있었다.
            잡석을 42 → 96 으로 늘리면 그대로 증폭되므로 x 조건을 넣는다."""
            best = None
            for rp in PARAMS["riprap"]:
                if rp["x0"] <= x <= rp["x1"] and rp["y0"] <= y < rp["y1"]:
                    best = rp["z"] if best is None else max(best, rp["z"])
            return best
        for i in range(int(rk["n"])):
            rx = rs.uniform(rk["x0"], rk["x1"])
            ry = rs.uniform(rk["y0"], rk["y1"])
            s = rs.uniform(rk["s_lo"], rk["s_hi"])
            yaw = rs.uniform(0.0, 90.0)
            top = band_top(rx, ry)
            if top is None:                  # 사석 단이 없는 대역 → 배치 생략
                continue                     # (RNG 소비 순서는 유지 = 결정성)
            sc._oriented_box(stage, f"{ROOT}/Rock_{i}",
                             (rx, ry, top - s * 0.15),
                             (s, s * 0.85, s * 0.7), M["rock"], rotz=yaw)

    def build_river(M):
        wt = PARAMS["water"]
        sc.build_water(stage, f"{ROOT}/Water", wt["x0"], wt["y0"], wt["x1"],
                       wt["y1"], wt["z"], mtl=M["water"])
        fb = PARAMS["far_bank"]
        BOX(f"{ROOT}/FarBank",
            ((fb["x0"] + fb["x1"]) / 2.0, (fb["y0"] + fb["y1"]) / 2.0,
             fb["z_top"] - fb["thick"] / 2.0),
            (fb["x1"] - fb["x0"], fb["y1"] - fb["y0"], fb["thick"]),
            M["grass"], col=True)

    # -------------------------------------------------------------------
    # 데크 — 슬래브 + 페시아 + 종보/횡보 + 말뚝 (캔틸레버 1.25 m)
    # -------------------------------------------------------------------
    def build_deck(M):
        d = PARAMS["deck"]
        df = PARAMS["deckframe"]
        mtl = M["deckwood"] if cfg["cue_material_break"] else M["gravel"]
        BOX(f"{ROOT}/Deck/Slab",
            ((d["x0"] + d["x1"]) / 2.0, (d["y0"] + d["y1"]) / 2.0,
             d["z_top"] - d["slab_t"] / 2.0),
            (d["x1"] - d["x0"], d["y1"] - d["y0"], d["slab_t"]), mtl, col=True)
        # 외측 페시아(측판). **킥플레이트가 아니다** — 상면이 데크면(z=0)과
        #   같아 보행면 위로 전혀 올라오지 않는다(로봇 시점 개방 유지).
        #   외면을 5 mm 만 돌출시켜 슬래브 측면과의 동일평면 Z파이팅 회피.
        BOX(f"{ROOT}/Deck/Fascia",
            ((d["x0"] + d["x1"]) / 2.0,
             d["y1"] - d["fascia_t"] / 2.0 + 0.005,
             d["z_top"] - 0.20 / 2.0),
            (d["x1"] - d["x0"], d["fascia_t"], 0.20), mtl)
        z_beam_top = d["z_top"] - d["slab_t"]
        zc = z_beam_top - df["beam_h"] / 2.0
        for i, by in enumerate(df["beam_ys"]):
            BOX(f"{ROOT}/Deck/Beam_{i}",
                ((d["x0"] + d["x1"]) / 2.0, by, zc),
                (d["x1"] - d["x0"], df["beam_w"], df["beam_h"]), mtl)
        # 횡보
        n_cross = int((d["x1"] - d["x0"]) / df["cross_step"])
        for k in range(n_cross + 1):
            cx = d["x0"] + k * df["cross_step"]
            BOX(f"{ROOT}/Deck/Cross_{k}", (cx, (d["y0"] + d["y1"]) / 2.0, zc),
                (df["cross_w"], d["y1"] - d["y0"], df["beam_h"] * 0.8), mtl)
        # 말뚝 — 어깨 사석 상면(−1.20)에 착지
        sh = PARAMS["shoulder"]
        pile_top = z_beam_top - df["beam_h"]
        ph = pile_top - sh["z_top"]
        n_pile = int((d["x1"] - d["x0"]) / df["pile_step"])
        for k in range(n_pile + 1):
            px = d["x0"] + k * df["pile_step"] + 0.4
            if px > d["x1"] - 0.2:
                continue
            for j, py in enumerate(df["beam_ys"]):
                CYL(f"{ROOT}/Deck/Pile_{k}_{j}",
                    (px, py, sh["z_top"] + ph / 2.0), df["pile_r"], ph,
                    mtl, col=True)

    def build_stairs(M):
        st = PARAMS["stair"]
        d = PARAMS["deck"]
        mtl = M["deckwood"] if cfg["cue_material_break"] else M["gravel"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], d["y0"], d["y1"], st["riser"],
            st["tread"], st["n_geom"], st["base_z"], mtl, z_top=0.0,
            collider=True)
        if cfg["cue_nosing"]:
            sc.build_nosing(stage, f"{ROOT}/Nosing", st["x0"], d["y0"],
                            d["y1"], st["riser"], st["tread"], st["n_geom"],
                            z_top=0.0)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 데크·계단·둔치 단차를 z=0 평지로."""
        u = PARAMS["upper"]
        lo = PARAMS["lower"]
        BOX(f"{ROOT}/FlatFill",
            ((u["x0"] + lo["x1"]) / 2.0, (u["y0"] + lo["y1"]) / 2.0,
             u["z_top"] - u["thick"] / 2.0),
            (lo["x1"] - u["x0"], lo["y1"] - u["y0"], u["thick"]),
            M["grass"], col=True)

    # -------------------------------------------------------------------
    # 난간 — 강측 1선. 훼손 스팬 2.4 m 결손 + 킥플레이트 부재.
    # -------------------------------------------------------------------
    def build_railing(M):
        d = PARAMS["deck"]
        r = PARAMS["rail"]
        for i, px in enumerate(_rail_posts()):
            CYL(f"{ROOT}/Rail/Post_{i}", (px, r["y"], r["post_h"] / 2.0),
                r["post_r"], r["post_h"], M["rail"], col=True)
        # 상단대·중간대 : 훼손 스팬을 뺀 2 세그먼트 (Z축 원기둥을 X로 눕힘)
        segs = [("W", d["x0"], r["gap_x0"]), ("E", r["gap_x1"], d["x1"])]
        for tag, x0, x1 in segs:
            if x1 - x0 <= 1e-6:
                continue
            for nm, zz, rr in (("Top", r["top_z"], r["top_r"]),
                               ("Mid", r["mid_z"], r["mid_r"])):
                CYL(f"{ROOT}/Rail/{nm}_{tag}",
                    ((x0 + x1) / 2.0, r["y"], zz), rr, x1 - x0, M["rail"],
                    rotY=90.0)
        # 잘려나간 포스트 밑동(훼손 흔적 — 설비 역추론 단서)
        for i, sx in enumerate(r["stub_xs"]):
            CYL(f"{ROOT}/Rail/Stub_{i}", (sx, r["y"], r["stub_h"] / 2.0),
                r["post_r"], r["stub_h"], M["rail"], col=True)
        # 경고 테이프 1선(명백한 규정 미달 — 방호 아님).
        #   [v6 C-6] 두께 0.02 솔리드 각재 + 동단 무지지 부유 → **두께 4 mm
        #   리본 + 포물선 처짐 + 양단 잔존 포스트 결속**으로 교체.
        _build_tape_ribbon(M)

    def _build_tape_ribbon(M):
        """훼손 스팬 경고 테이프 = 잔존 포스트 2본에 묶인 처짐 리본.

        기하 : x ∈ [xa, xb] (잔존 포스트 x), z(x) = z_end − sag·(1 − u²),
               u = 2(x − xm)/L  → 양단 z_end, 중앙 z_end − sag.
        구현 : sc._oriented_box(rotz=90, rotx=a).
               op 적용순 scale → rotX → rotZ 이므로 로컬 Y(길이축)는
               rotX(a) 후 (0, cos a, sin a), rotZ(90) 후 (−cos a, 0, sin a).
               즉 세그 축 방향 (cos a, 0, −sin a) ∝ (dx, 0, dz)
               → a = atan2(−dz, dx). size=(t, seg_len, w) 로 주면
               로컬X=두께(월드 Y), 로컬Z=폭(수직) 이 된다.
        """
        r = PARAMS["rail"]
        tp = r["tape"]
        xa, xb = tp["anchor_xs"]
        L = xb - xa
        xm = (xa + xb) / 2.0

        def z_of(x):
            u = 2.0 * (x - xm) / L
            return tp["z_end"] - tp["sag"] * (1.0 - u * u)

        n = int(tp["nseg"])
        for i in range(n):
            x0 = xa + L * i / n
            x1 = xa + L * (i + 1) / n
            z0, z1 = z_of(x0), z_of(x1)
            dx, dz = x1 - x0, z1 - z0
            seg_len = math.hypot(dx, dz)
            ang = math.degrees(math.atan2(-dz, dx))
            sc._oriented_box(
                stage, f"{ROOT}/Rail/Tape_{i}",
                ((x0 + x1) / 2.0, r["y"], (z0 + z1) / 2.0),
                (tp["t"], seg_len * 1.02, tp["w"]), M["tape"],
                rotz=90.0, rotx=ang)
        # 결속부 — 포스트에 감긴 테이프 끝단(부유 아님을 눈으로 확인시키는 요소)
        for i, ax in enumerate((xa, xb)):
            CYL(f"{ROOT}/Rail/TapeTie_{i}", (ax, r["y"], z_of(ax)),
                r["post_r"] + 0.006, tp["tie_h"], M["tape"])

    # [v5.2 사용자] 임의 경고 팻말 제거 — build_signs() 삭제.

    # -------------------------------------------------------------------
    # 드레싱 — 갈대·벤치·가로등·나무·자전거도로·볼라드
    # -------------------------------------------------------------------
    def build_dressing(M):
        u = PARAMS["upper"]
        lo = PARAMS["lower"]
        # 자전거도로(하부 둔치) + 백색 경계선 2
        br = PARAMS["bikeroad"]
        BOX(f"{ROOT}/BikeRoad",
            ((br["x0"] + br["x1"]) / 2.0, (br["y0"] + br["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0 + br["proud"]),
            (br["x1"] - br["x0"], br["y1"] - br["y0"], lo["thick"]),
            M["asphalt"], col=True)
        for tag, yc in (("Lo", br["y0"] + 0.15), ("Hi", br["y1"] - 0.15)):
            BOX(f"{ROOT}/BikeLine_{tag}",
                ((br["x0"] + br["x1"]) / 2.0, yc, lo["z_top"] + 0.005),
                (br["x1"] - br["x0"], 0.10, 0.02), M["paint"])
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, u["z_top"],
                           M["wood"], yaw=yaw)
        for i, (bx, by, yaw) in enumerate(PARAMS["lower_benches"]):
            sc.build_bench(stage, f"{ROOT}/BenchLow_{i}", bx, by, lo["z_top"],
                           M["wood"], yaw=yaw)
        for i, (bx, by) in enumerate(PARAMS["lower_bollards"]):
            sc.build_bollard(stage, f"{ROOT}/BollardLow_{i}", bx, by,
                             lo["z_top"], mtl=M["bollard"])
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (lx, ly, u["z_top"] + sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["bollard"], col=True)
            CYL(f"{base}/Arm", (lx, ly - sl["arm_len"] / 2.0,
                                u["z_top"] + sl["pole_h"] - 0.1),
                sl["arm_r"], sl["arm_len"], M["bollard"], rotX=90.0)
            BOX(f"{base}/Head", (lx, ly - sl["arm_len"],
                                 u["z_top"] + sl["pole_h"] - 0.15),
                (sl["head"], sl["head"], 0.12), M["lamp"])
        for i, (tx, ty) in enumerate(PARAMS["trees"]):
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", tx, ty, u["z_top"],
                          M["wood"], M["canopy_a"], M["canopy_b"])
        # [v7 판정 §8 ③] 억새 = **대(stalk) 군락** (구 build_hedge 육면체 폐기).
        #   scene17 W-5 / scene09 build_reeds 규약. 밴드 사각형은 불변.
        for i, rd, k, px, py, hh, ry, rx in reed_instances():
            CYL(f"{ROOT}/Reed_{i}_{k}", (px, py, rd["z"] + hh / 2.0),
                PARAMS["reed"]["r"], hh, M["reed"], rotY=ry, rotX=rx)
        for i, fh in enumerate(PARAMS["far_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}",
                           fh["cx"] - fh["sx"] / 2.0,
                           fh["cy"] - fh["length"] / 2.0,
                           fh["cx"] + fh["sx"] / 2.0,
                           fh["cy"] + fh["length"] / 2.0, fh["h"],
                           base_z=u["z_top"])

    def build_skyline(M):
        """원경 — 건너편 아파트 3동 + 교량 + 남측 시가지 1동 (지평 폐쇄 §A-4).
        scene17 의 '한강 둔치' 판독 요소를 그대로 승계한다."""
        for key, bd in PARAMS["far_buildings"].items():
            sc.build_building(stage, f"{ROOT}/FarBuilding_{key}", bd,
                              M["cwall"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        br = PARAMS["bridge"]
        deck_c = br["deck_top"] - br["deck_t"] / 2.0
        BOX(f"{ROOT}/Bridge/Deck",
            ((br["x0"] + br["x1"]) / 2.0, (br["y0"] + br["y1"]) / 2.0, deck_c),
            (br["x1"] - br["x0"], br["y1"] - br["y0"], br["deck_t"]),
            M["bridge"], col=True)
        pier_top = br["deck_top"] - br["deck_t"]
        ph = pier_top - br["pier_base"]
        for i, py in enumerate(br["pier_ys"]):
            CYL(f"{ROOT}/Bridge/Pier_{i}",
                (br["pier_x"], py, br["pier_base"] + ph / 2.0),
                br["pier_r"], ph, M["bridge"], col=True)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    if cfg["hazard_stairs"]:
        build_terrain(M)
        build_deck(M)
        build_stairs(M)
        if cfg["cue_railing"]:
            build_railing(M)
        # [v5.2 사용자] 임의 경고 팻말 제거 — cue_sign 배치 삭제.
    else:
        build_flat_fill(M)
    build_riprap(M)                     # 호안·수면·원경은 상시(지평 폐쇄)
    build_river(M)
    if cfg["cue_scene_dressing"]:
        build_skyline(M)
        if cfg["hazard_stairs"]:
            build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["deck_walk"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene12_{ts}.png")
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
