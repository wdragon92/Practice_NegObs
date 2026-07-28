# -*- coding: utf-8 -*-
"""
scene07_temple_stone_path.py — NegObs 인공씬 7호(v5 R2): 산사 자연석 듬성 계단

유형   : R2 (v5 재설계) — 자연석 **이산 배석**(듬성듬성 박힌 큰 판석)
사양서 : Docs/briefs/multi_scene_brief_v5.md §R2 + Docs/scene_redesign_v5_proposal.md
공통   : scene_common.py (무수정) / 골격 관례 : scenes/main/scene04_parktrail.py
계승   : scenes/archive_v3/scene07_wornstone_temple.py (worn_stone·산사 드레싱 어휘)

────────────────────────────────────────────────────────────────────────────
[위험 본질]
  한국 산사 진입 산길. 규격 계단이 아니라 **큰 자연석이 듬성듬성 박혀** 계단
  구실을 한다. 위험은 '이색 지형'이 아니라 **규정 미달의 현실** 세 겹이다.

  ① 디딤 리듬 파괴 — 돌 간 간격(0.05~0.30 m)·답차(0.04~0.31 m)가 불균일해
     "n번째 단코 = n×riser" 라는 계단 사전지식이 성립하지 않는다. 로봇 시점
     (h0.3)에서 다음 디딤면 높이를 외삽할 수 없다.
  ② 측방 사면 낙차 1.8 m **무방호** — 회랑(y ±1.7) 남측 어깨 너머는 석축
     옹벽이 곧장 1.8 m 떨어진다. 난간·연석·점자 어느 것도 없다(산사 비관행).
     grazing 시 하부 테라스의 낙엽면이 회랑면과 **연속된 한 장의 지면**으로
     읽혀 경계가 소실 — 이 씬의 GT 양성 핵심.
  ③ 낙엽 부분 가림 — leaf_ground 밴드가 돌 에지를 물고 덮어 단코 절단선을
     지운다(계열② 부분 가림).

  GT 원칙: 배석 경로(회랑) 외 남측 사면 낙차 = 양성. 배석 자체의 답차도
  0.3 m 근접(최대 0.31)까지 커져 '작은 낙차'의 경계 사례를 겸한다.

[보행 연속성 자가 검증표]  — 진입 → 하강 → 탈출 (좌표는 y=0 워크라인 기준)
  ┌ 구간 ───────────────┬ 좌표(x, z) ─────────────┬ 단차/근거 ──────────────┐
  │ 경내 마당(진입)      │ x −24..0,  z 0.000       │ 평탄(마사토)            │
  │ 일주문 통과          │ x −5.6,    z 0.000       │ 기둥 y ±1.35 (개구 2.7) │
  │ 마당 어깨 → 1석      │ x 0 → 0.24, 0.000→−0.02x │ 단차 = 표 [1] 참조      │
  │ 배석 24석 하강       │ x 0.06..12.05            │ 답차 min/max = 표 [2]   │
  │ 마지막 석 → 진입마당 │ x 12.05→12.2, →−4.200    │ 단차 = 표 [3] 참조      │
  │ 하부 진입로(탈출)    │ x 12.2..90, z −4.200     │ 평탄(낙엽 흙길)         │
  └──────────────────────┴──────────────────────────┴─────────────────────────┘
  · 전 배석은 워크라인 |y| ≤ 0.22 를 반드시 덮도록 cy 지터를 폭에 종속시킨다
    (|cy| ≤ w/2 − 0.22) → "발 디딜 돌이 없는 구간" 0 (SMOKE 가 전수 검사).
  · 실제 수치·판정은 `NEGOBS_SMOKE=1` 표 [1][2][3]에서 출력된다.

[기하 핵심]
  · 배석은 scene_common.build_worn_stone_stairs 를 쓰지 않는다(그 빌더는 단을
    가로 블록으로 쪼갠 '연속 석단'이라 듬성 배석이 안 나온다). 씬 로컬에서
    **돌별 개별 박스**를 seed 고정 random 으로 생성한다:
      폭 w U(0.50,1.10) · 깊이 U(0.28,0.40) · 간격 U(0.05,0.30) ·
      두께 = proud + U(0.10,0.18) (0.12~0.26) · 상면 proud U(0.02,0.08) ·
      yaw rz U(−4,4)° · 상면 요철 rx U(−2.5,2.5)°  → sc._oriented_box
    돌 사이 지면은 leaf_ground 재질 사면(회랑 슬래브)이 채운다.
  · 배석 상면 z = P(cx) + proud,  P(x) = −(4.2/12.2)·x  (사면 19.0°)
    → 매입 깊이 = 두께 − proud ∈ [0.10, 0.18] m (부유 0, 최소 매입 0.10).
  · 총 낙차 4.2 m / 총 run 12.2 m / 24석.

[v6 판정 재수정 — judge_v6_rt_new7.md §2 + 감독 결정 2항]
  ① **태양 재선정**(감독 승인). 구 `SUN_AZ_OFFSET=0.0`(월드 az 33.5 = 태양이
     +X·+Y 하늘)은 주 카메라 축(+X 관람)에서 **완전 역광**이라 원경 능선(−X향
     면)·남측 석축(−Y향 면)이 lambert 0 → 화면 상반 40~60 % 순흑이었다.
     → `SUN_AZ_OFFSET=191.5` (월드 az = 33.5+191.5 = **225**, 그림자 az 45).
       면별 직사광 lambert = dot(N, L) (태양 고도 49.79° → 수평성분 0.6456):
         −X향(원경 능선·일주문 정면·배석 라이저) 0.707×0.6456 = **0.456**
         −Y향(남측 무방호 석축·하부 테라스 절개면)          = **0.456**
         상면(마당·회랑·배석 상면)      sin49.79            = **0.763**
       즉 그리드(+X)·`side_slope`·`grazing_edge` 전 컷이 순광. 그림자는 +X·+Y
       (화면 안쪽·북측)로 떨어져 전경을 덮지 않는다.
     · (v6 주석 오류 — v7 에서 정정) "처마 그림자는 x ≈ 0.69 에 떨어져 배석
       1~2석만 스친다"는 **처마 끝선 1점만** 투영한 결과였다. 지붕은 면이므로
       그림자는 x −3.17…+0.57 의 **띠**이고, 그 띠가 근경 마당을 덮었다.
       → 아래 [v7] 절. 캐스터 발자국은 SMOKE 가 AABB 전 모서리로 재계산한다.
     · `gate_frame`(되돌아봄)만 일주문 +X면이 음영측 — az 180~270 구간에서는
       구조적으로 회피 불가(배경 순흑 해소가 상위 우선). 대신 초석·2단 처마·
       기단 명도로 실루엣 판독을 보강했다.
  ② **자연석이 '벽돌 판석'으로 렌더됨** → 원인은 두 겹.
     (a) 재질 `stone_worn` = **조적 줄눈 텍스처**(정형 벽돌 + 몰탈 줄눈),
     (b) `make_pbr` 는 **월드 스페이스 투영**이라 전 배석이 하나의 줄눈 격자를
         공유 → 돌 경계를 가로질러 줄눈이 연속 = 콘크리트 보도판.
     → 재질을 `rock_face`(무줄눈 자연암 diff/nor)로 교체하고, **돌별 재질 풀**
       (scale·tint·texture_rotate·texture_translate 지터 8종)을 만들어 인접
       돌의 결·색·요철이 어긋나게 했다. bump 1.5 로 요철 강화.
     → 실루엣: 돌마다 **캔트 노브**(주석보다 1~3 cm 낮고 rz·rx 가 다른 부속
       덩어리) 1개를 얹어 직사각 윤곽을 깬다. x 방향 돌출은 검산으로 억제.
  ③ **배경 지평 폐쇄** — 능선 알베도가 sRGB 암색 하한(0.030)이라 순광이어도
     검은 벽이 된다. 원경 대기원근(aerial perspective)을 알베도에 구워
     near 0.052 / mid 0.088 / far 0.142(청기 증가)로 올리고, 근경 능선을
     **3분절 엇물림**(y 오프셋·높이 지터)한 뒤 마루에 숲 밴드(build_hedge
     라운드 크라운)를 얹어 직선 능선·검은 벽을 동시에 해소했다.
  ④ 낙엽 밴드가 **축정렬 수평판**이라 19° 회랑 위에서 상류단 매몰 / 하류단
     0.17 m 부유 → `gate_frame` 의 "검은 사각 구멍 2개소"의 정체. 사면 추종
     (`build_slope`) + 패치당 3매 회전 중첩으로 부유·직사각 데칼을 동시 해소.

[v7 판정 재수정 — judge_v7_rt_A.md §5 "그림자가 근경 마당으로 이동"]
  진단: v6 는 **면별 lambert** 만 보고 방위를 골랐다. 면은 전부 순광이 됐지만
    **캐스트 그림자**는 사라진 게 아니라 위(배경)에서 아래(근경)로 자리를
    옮겼을 뿐이다. 유일한 대형 캐스터인 일주문(부연 폭 5.14 m · 처마 z 2.81)의
    z=0 투영이 az 225 에서 x −3.17…+0.57 · y ≥ −0.89 → 그리드 **하반 지면대**
    (h0.3_d2 = x −1.44…−0.30, 반폭 ±0.33)를 통째로 덮었다(하반 mean 27.5).
    태양 회전만으로는 그림자 길이(2.38 m)를 줄일 수 없으므로 세 축을 같이 쓴다.
  ① **태양 az 225 → 240**(offset 191.5 → 206.5) : 그림자 az 45 → 60 으로 눕혀
     그림자를 +Y 로 더 밀어낸다. 부수 효과로 **−Y향(남측 무방호 석축 = grazing
     판정면) lambert 0.456 → 0.559 상승**. 대가는 −X향(원경 능선) 0.456 → 0.323.
  ② **일주문 cx −3.0 → −5.6**(석등·안내판 동반 −2.6) : 그림자 x 대역을
     −6.26…−2.25 로 후퇴시켜 h0.3_d2 하반 지면대를 완전히 비운다.
  ③ **박공 내밈 roof_y 2.35 → 1.90**(부연 2.57 → 2.12) : 그림자 남단을
     y −0.89 → **−0.06** 으로 북상 → 워크라인 남측 절반과 프레임 남측(우측)이
     직사광. (부연 폭 > 그림자 이동량이라 az 로는 원리상 전량 회피 불가.)
  ④ **원경 능선 알베도 ×1.42** : ①의 대가를 상쇄해 **렌더 휘도(알베도 ×
     lambert)를 v7 수준으로 보존**한다 — 이 보정이 없으면 "배경 순흑 해소"가
     되돌아간다. + 중·원경 능선을 2분절 엇물림(높이 15.0/18.4 · 25.0/29.2)해
     단일 박스의 **수평 직선 마루("무대 배경막")** 를 꺾었다.
  검산: SMOKE `[v6 태양]`(면별 lambert + 알베도×lambert 곱 대조) ·
        `[v7 그림자]`(캐스터별 z=0 투영 발자국) ·
        `[v7 하반 지면대]`(프리셋 9개 × 프레임 아래절반 지면 구간 대조).
────────────────────────────────────────────────────────────────────────────

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene07_temple_stone_path.py

자동 캡처 : NEGOBS_CAPTURE=1 python scene07_temple_stone_path.py
스모크    : NEGOBS_SMOKE=1 python3 scene07_temple_stone_path.py  (부팅 없음)

좌표계: Z-up, m, 진행축 +X 하강(관례). 낙차 시작 모서리 = x=0(마당 어깨).
        그리드 축(y=0)은 경내 → 일주문 → 배석 하강 → 하부 진입로.
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hazard_stairs 만 위험 기하 토글.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 배석·사면·남측 낙차를 z=0 평지로
    "cue_railing":        False,   # 산사 배석엔 난간 미관행(무방호) — 코드 경로만
    "cue_tactile":        False,   # 비관행(v5 브리프 §공통) — 코드 경로만
    "cue_material_break": True,    # 마당 마사토 vs 배석 마모석 대비
    "cue_sign":           True,    # [v5 공통 레이어] sign_info(사찰 안내) 진입부
    "cue_scene_dressing": True,    # 일주문·석등·석축담·소나무·법당 실루엣
    "cue_nosing":         False,   # 자연석 단코엔 논슬립 띠 미관행 — 코드 경로만
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
STAIR_RUN = 12.2                   # 배석 구간 수평 길이
STAIR_DROP = 4.2                   # 배석 구간 총 낙차 (사면 19.0°)
SIDE_DROP = 1.8                    # 남측(−Y) 무방호 측방 낙차

PARAMS = dict(
    # --- 배석(이산 자연석) 생성 파라미터 : seed 고정 random ---
    stones=dict(n=24, seed=707, x_start=0.06, x_end=12.05,
                w=(0.50, 1.10), depth=(0.28, 0.40), gap=(0.05, 0.30),
                proud=(0.02, 0.08), embed=(0.10, 0.18),
                rz=4.0, rx=2.5, foot_half=0.22),
    # --- [v6] 돌별 재질 풀 : 월드투영 공유로 생기는 '연속 줄눈' 파괴 ---
    #     rock_face(무줄눈 자연암) 기반 · scale/tint/rotate/translate 지터.
    stone_mtl=dict(n=8, seed=7071, scale=(0.55, 1.35), bump=1.5,
                   tint_dry=(0.88, 0.86, 0.82), tint_moss=(0.74, 0.84, 0.70),
                   moss_every=3, jitter=0.06),
    # --- [v6] 캔트 노브 : 직사각 실루엣 파괴(주석 상면보다 낮아 GT 불변) ---
    #     x 반폭 = (dx·cosθ + dy·sinθ)/2 ≤ 돌 깊이/2 + 0.02 를 SMOKE 가 검산.
    #     drop 하한 0.050 = rx 최대 기울기가 만드는 코너 상승(0.043) 초과분 확보
    #     → 노브 최고점이 주석 상면을 절대 넘지 않는다(보행면 GT 불변).
    knob=dict(seed=7072, fx=0.62, fy=0.50, rz=(10.0, 20.0), rx=(3.0, 9.0),
              drop=(0.050, 0.080), off_y=0.33, thick=0.16),
    # --- 회랑(배석 사이 지면) : leaf_ground 사면 ---
    corridor=dict(y0=-1.7, y1=1.7, thick=0.60),
    # --- 축정렬 지면 플레이트 표 (name, x0, x1, y0, y1, z_top, thick, mtl) ---
    #     v5 회귀 체크리스트 ③ : 공동을 덮는 평면 없음 — 남측 낙차는 y=−1.7
    #     경계에서 플레이트가 **갈라져** 있다(연속 판이 걸쳐 있지 않음).
    plates=[
        ("Courtyard",     -24.0,   0.0,  -1.7,  44.0,   0.0, 0.50, "gravel"),
        ("CourtyardBody", -24.0,   0.0,  -1.7,  44.0,  -0.5, 2.20, "rock"),
        ("BackField",     -46.0, -24.0,  -1.7,  44.0,   0.0, 2.40, "grass"),
        ("SouthTerraceA", -46.0,   0.0, -34.0,  -1.7,  -1.8, 1.20, "leaf"),
        ("SouthTerraceC",  12.2,  90.0, -34.0,  -1.7,  -6.0, 1.20, "leaf"),
        ("Approach",       12.2,  90.0,  -1.7,   2.15, -4.2, 1.00, "leaf"),
        ("NorthWallFlat",  12.2,  90.0,   2.15,  2.6,  -1.25, 3.20, "rock"),
        ("NorthBankFlat",  12.2,  90.0,   2.6,  44.0,  -2.0, 1.20, "grass"),
        ("ScarpFlatBot",   12.2,  90.0,  -1.80, -1.66, -4.2, 2.00, "rock"),
    ],
    # --- 사면 플레이트(build_slope) : (name, z0, drop, y0, y1, thick, mtl) ---
    #     전부 x0=0, run=STAIR_RUN. margin=0.0(플레이트 경계 정확 일치).
    slopes=[
        ("PathCorridor",  0.00, STAIR_DROP, -1.70,  1.70, 0.60, "leaf"),
        ("SouthTerraceB", -1.80, STAIR_DROP, -34.0, -1.70, 1.20, "leaf"),
        ("SouthScarp",    0.00, STAIR_DROP, -1.80, -1.66, 2.00, "rock"),
        ("NorthWall",     0.75, 2.00,        1.70,  2.15, 3.20, "rock"),
        ("NorthBank",     0.00, 2.00,        2.15, 44.00, 1.20, "grass"),
    ],
    # --- 낙엽 밴드(돌 에지 부분 가림) : 회랑 위 얇은 판 (cx, cy, sx, sy) ---
    #     [v6] 축정렬 수평판 → **사면 추종 슬래브**(19°) + 패치당 3매 회전 중첩.
    #     구 방식은 상류단 매몰·하류단 0.17 m 부유(= gate_frame 검은 사각 구멍).
    leaf_drifts=[(1.30, 0.55, 1.30, 0.95), (3.05, -0.60, 1.10, 1.00),
                 (5.40, 0.35, 1.40, 1.10), (7.20, -0.75, 1.00, 0.85),
                 (9.10, 0.50, 1.25, 1.00), (10.90, -0.40, 1.15, 0.90)],
    leaf_band=dict(thick=0.05, proud=0.012, seed=7073, subs=3,
                   sub_scale=(0.55, 0.92), sub_off=0.42, sub_rz=26.0),
    # [v6] 마당(마사토) 낙엽 퇴적 3 — '대면적 고반사 베이지 평면'(판정 ⑤) 완화.
    #      마당은 평탄이 관행이므로 곡률 대신 재질 변주로 단조로움을 깬다.
    #      전부 y ≥ −1.55 (남측 경계 −1.7 밖으로 나가지 않음 = 부유 0).
    yard_drifts=[(-2.6, 2.2, 2.4, 1.8), (-7.6, -0.72, 2.1, 1.6),
                 (-13.2, 1.7, 2.6, 2.0)],
    yard_leaf=dict(seed=7074, subs=2, scale=(0.6, 0.9), off=0.38, rz=30.0),

    # --- 일주문(기둥 2 + 맞배지붕) : 마당 어깨 뒤, 그리드 축 개구 2.7 m ---
    #   [v7 판정 §5 ②] 근경 마당 그림자의 **유일한 대형 캐스터**가 이 문이다.
    #     구 cx −3.0 · roof_y 2.35(부연 2.57) · az 225 → 그림자 x −3.17…+0.57 ·
    #     y ≥ −0.89 로 h0.3_d2 의 하반 지면대(x −1.44…−0.30, y ±0.98)를 통째로
    #     덮었다(측광 하반 mean 27.5). 태양 회전만으로는 x 방향 그림자 길이
    #     (부연 2.81 m × cot49.79 = 2.38 m)를 못 줄이므로 **문을 서쪽으로 2.6 m
    #     후퇴**시키고 박공 내밈을 1.00 → 0.55 m 로 줄여 그림자 남단을 y≈0 까지
    #     북상시킨다(SMOKE [v7 그림자] 표가 프리셋별 하반 지면대와 대조).
    gate=dict(cx=-5.6, half_y=1.35, post_r=0.24, post_h=3.05,
              beam_t=0.30, beam_over=0.45,
              roof_half_run=1.55, roof_drop=0.62, roof_t=0.22,
              roof_y=1.90, ridge_z=4.00),
    # --- 석등 2 (일주문 앞) ---
    #   [v6] 구 형상(각기둥 + 사각 갓 + 원통)은 **벽돌 굴뚝**으로 읽혔다.
    #   원인 ① 재질이 조적 텍스처(stone_worn) ② 화강암 석등의 표준 부재 결여.
    #   → 지대석·하대석·간주석(원형)·상대석·화사석(4주 + 암부 화창)·옥개석 2단·
    #      보주 구성으로 교체하고 재질을 무줄눈 화강암 톤으로 바꿨다.
    #   [v7] 일주문과 함께 −2.6 m 이동(문 앞 1.3 m 상대위치 유지).
    lanterns=[dict(cx=-6.9, cy=2.45), dict(cx=-6.9, cy=-1.15)],
    lantern=dict(plinth_w=0.86, plinth_h=0.14, lower_r=0.30, lower_h=0.20,
                 shaft_r=0.13, shaft_h=0.62, upper_r=0.26, upper_h=0.16,
                 fire_w=0.46, fire_h=0.42, pillar=0.075,
                 cap_w=0.94, cap_h=0.11, cap2_w=0.66, cap2_h=0.09,
                 jewel_r=0.085),
    # --- 법당 실루엣(상부) : 기단 + 기둥열 + 맞배지붕 ---
    #   기둥 상단(0.9+2.4=3.30) < 최외곽 기둥(±4.1) 위 지붕 하면(3.72) — 관통 0
    hall=dict(cx=-18.0, cy=3.5, sx=9.0, sy=5.6, base_h=0.9,
              post_r=0.20, post_h=2.4, n_posts=5,
              roof_half_run=5.6, roof_drop=1.6, roof_t=0.30, roof_y=4.2,
              ridge_z=5.20),
    # --- 소나무(build_tree) : 사면·마당·테라스 (name, cx, cy, zone, trunk_h) ---
    pines=[("N0", 2.5, 4.6, "north", 3.0), ("N1", 7.4, 6.2, "north", 3.4),
           ("N2", 11.6, 4.2, "north", 2.8), ("N3", -6.0, 6.5, "flat", 3.2),
           ("S0", 4.2, -4.4, "south", 2.6), ("S1", 9.0, -6.0, "south", 3.0),
           ("S2", -8.0, -5.2, "south", 2.8), ("S3", 15.0, -4.0, "south", 3.1)],
    tree=dict(trunk_r=0.11),
    # --- 관목 군락(눌린 타원체 중첩 — scene04 v5 규약) ---
    # [v6] 북측 관목 y 3.0~3.6 → 4.4~5.0 : 돌담(y 1.70~2.15, 배면 0.75 m 낮음)
    #      바로 뒤라 회랑 시점에서 '담 위에 얹힌 부유'로 읽혔다.
    shrubs=[(1.8, 4.5, "north"), (6.0, 4.9, "north"), (10.4, 4.6, "north"),
            (2.0, -2.9, "south"), (7.6, -3.4, "south"), (12.0, -3.0, "south"),
            (-9.0, 3.0, "flat"), (-14.0, -3.4, "south")],
    shrub=dict(embed=0.25,
               blobs=((0.00, 0.00, 0.78, 0.62, 0.36),
                      (0.55, 0.42, 0.52, 0.44, 0.26),
                      (-0.46, -0.38, 0.58, 0.40, 0.30))),
    # --- 사찰 안내판(sign_info) : 진입부(일주문 앞), 접근 시점을 향함(yaw 180) ---
    #   [v7] 일주문과 함께 −2.6 m 이동(문 뒤 0.65 m 상대위치 유지).
    sign=dict(cx=-4.95, cy=-1.15, yaw=180.0, w=0.78, h=0.62, pole_h=1.95),

    # --- 원경 능선 (지평 폐쇄, 주 카메라 축 정면 +X) ---
    #   [v6] 구 near 능선은 sy 130 단일 박스 → **직선 능선 + 검은 벽**.
    #   근경 능선을 3분절(x 41.0~46.5 엇물림 · 높이 7.6/10.4/8.6)하고 각 마루에
    #   숲 밴드(ridge_crest)를 얹어 능선선을 요철화한다. y 합집합 −74..+79 로
    #   그리드 FOV(±30 m @ 50 m)를 여유 있게 덮는다.
    ridge=[dict(cx=42.5, cy=-46.0, sx=7.0, sy=56.0, h=7.6, z0=-6.0,
                tone="near"),
           dict(cx=46.5, cy=6.0, sx=8.0, sy=52.0, h=10.4, z0=-6.0,
                tone="near"),
           dict(cx=41.0, cy=52.0, sx=6.5, sy=54.0, h=8.6, z0=-6.0,
                tone="near"),
           # [v7 판정 §5 ②] 중·원경이 각각 sy 170/210 **단일 박스**라 마루가
           #   완전한 수평 직선 = "무대 배경막 + 수평 이음선". 근경과 같은
           #   방식으로 2분절 엇물림(높이차 3~4 m)해 스카이라인을 꺾는다.
           #   y 합집합은 그리드 FOV(±48 m @ 84 m)를 덮도록 유지.
           dict(cx=62.0, cy=-52.0, sx=11.0, sy=104.0, h=15.0, z0=-6.0,
                tone="mid"),
           dict(cx=66.0, cy=48.0, sx=10.0, sy=112.0, h=18.4, z0=-6.0,
                tone="mid"),
           dict(cx=84.0, cy=-58.0, sx=14.0, sy=132.0, h=25.0, z0=-6.0,
                tone="far"),
           dict(cx=88.0, cy=56.0, sx=13.0, sy=140.0, h=29.2, z0=-6.0,
                tone="far")],
    # 능선 마루 숲 밴드 : (능선 인덱스, 높이) — build_hedge 라운드 크라운으로
    # 원경 수목을 개체 대신 **실루엣 밴드**로 처리(C-4 롤리팝 회피).
    ridge_crest=[(0, 3.4, "near"), (1, 4.2, "near"), (2, 3.8, "near"),
                 (3, 5.0, "far"), (4, 4.2, "far")],
    # 개체 수목은 근경 능선 마루에만 소수(가장자리 실루엣 변주용)
    ridge_trees=[dict(ri=0, cy=-30.0), dict(ri=1, cy=-6.0),
                 dict(ri=1, cy=14.0), dict(ri=2, cy=38.0)],
    # 뒤(−X) 숲 라인 : 배경 생울타리 3 + 나무 3. base 는 그 y 대역의 지면.
    back_hedge=dict(cx=-34.0, sx=1.4, length=20.0, h=2.0),
    back_hedges=[dict(cy=8.5, base=0.0), dict(cy=29.0, base=0.0),
                 dict(cy=-16.0, base=-1.8)],
    back_trees=[dict(cx=-38.0, cy=-12.0, gz=-1.8, trunk_h=3.4),
                dict(cx=-38.0, cy=6.0, gz=0.0, trunk_h=3.8),
                dict(cx=-38.0, cy=24.0, gz=0.0, trunk_h=3.2)],
    # 원경 숲 밴드 (name, x0, x1, y0, y1, h, base_z) — 남측 테라스 / 북측 사면
    far_hedges=[("S0", -40.0, 0.0, -30.0, -27.0, 2.4, -1.80),
                ("S1", 12.2, 80.0, -30.0, -27.0, 2.4, -6.00),
                ("N0", -40.0, 0.0, 40.0, 43.0, 2.6, 0.00),
                ("N1", 12.2, 80.0, 40.0, 43.0, 2.6, -2.00)],

    # --- 재질 ---
    material=dict(
        # [v6] rock_face = 배석용 무줄눈 자연암 / granite = 석등·초석(화강암)
        scale=dict(rock_wall=3.5, rock_face=0.95,
                   granite=3.2, leaf_ground=2.0, gravel=0.35, grass=4.0),
        stone_moss_tint=(0.86, 0.95, 0.82),   # (구 배석 이끼 톤 — v6 미사용)
        leaf_tint=(0.95, 0.90, 0.82),
        gravel_tint=(0.84, 0.81, 0.76),       # [v6] 마당 고반사 베이지 완화
        granite_tint=(1.0, 1.0, 1.0),
        grass_tint=(0.55, 0.68, 0.42),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        roof_color=(0.045, 0.030, 0.018),     # 어두운 목조 기와(sRGB 암색 규칙)
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        shrub=(0.030, 0.047, 0.021), shrub_rough=1.0,
        # [v6] 원경 대기원근을 알베도에 반영(구값 0.030~0.052 = 순광에서도 검은 벽).
        #   거리에 따라 명도↑·청기↑ — 능선 3단이 층으로 분리돼 읽힌다.
        # [v7] 태양 az 225 → 240 으로 −X향 lambert 가 0.456 → 0.323(×0.708)
        #   낮아진다. **렌더 휘도(= 알베도 × lambert)를 v7 수준으로 보존**하기
        #   위해 능선·마루 알베도를 일괄 ×1.42(=0.456/0.323) 한다(순백 상한
        #   0.72 이하 유지). 이 보정이 없으면 "배경 순흑 해소"가 되돌아간다
        #   — SMOKE [v6 태양] 블록이 알베도×lambert 곱을 v6 값과 대조한다.
        ridge_near=(0.074, 0.088, 0.064),
        ridge_mid=(0.125, 0.139, 0.131),
        ridge_far=(0.202, 0.222, 0.250),
        crest_near=(0.060, 0.078, 0.051),     # 능선 마루 숲 밴드(근경)
        crest_far=(0.102, 0.122, 0.111),
        sign_back=(0.055, 0.050, 0.045),
        rail_color=(0.20, 0.18, 0.16), rail_metallic=0.25, rail_rough=0.75,
    ),

    # --- 조명: scene01 noon 검증 상수 ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # 씬별 태양. 월드 태양 az ≈ 33.5+offset(태양이 있는 방위), 그림자는 az−180.
    # [v6 판정 §2 ⑥ + 감독 결정 2항 — 재선정 승인]
    #   구 0.0(az 33.5) = 태양이 +X·+Y 하늘 → +X 관람 축에서 완전 역광.
    #     원경 능선(−X향) lambert −0.538 → 0, 남측 석축(−Y향) −0.553 → 0 = 순흑.
    #   구 191.5(az 225) = 태양이 −X·−Y 하늘. 면 lambert 는 살렸으나 **일주문
    #     그림자가 근경 마당(그리드 하반 지면대)에 그대로 떨어졌다**(v7 §5 ②).
    #   신 206.5(az 240, 그림자 az 60) = 그림자를 +Y 로 더 눕혀 워크라인 남측을
    #     비운다. −X향 0.323 / −Y향 0.559 / 상면 0.763.
    #     · −Y향(남측 무방호 석축 = grazing 판정면)은 0.456 → 0.559 로 **상승**.
    #     · −X향(원경 능선)은 0.456 → 0.323 로 하락 → 능선 알베도 ×1.35 보정.
    #     상세 검산은 SMOKE [v7 그림자]·[v7 태양] 표.
    SUN_AZ_OFFSET=206.5,

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
# [C] 경로 / 에셋 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene07")

ASSET_ROLES = ["rock_wall", "rock_face", "granite_dark",
               "leaf_ground", "gravel", "grass", "sign_info", "hdri", "mdl"]


# ===========================================================================
# [D] 지형 수학 (부팅 불필요 — SMOKE 에서 그대로 재사용)
# ===========================================================================
def path_z(x):
    """회랑(배석 사면) 상면 z. x 0..run → 0..−drop, 밖은 클램프."""
    t = max(0.0, min(x / STAIR_RUN, 1.0))
    return -STAIR_DROP * t


def bank_z(x):
    """북측(+Y) 절토 사면 상면 z (완만 9.3° — 산복 절개면)."""
    t = max(0.0, min(x / STAIR_RUN, 1.0))
    return -2.0 * t


def ground_z(x, y):
    """드레싱 접지용 지면 z. 회랑/마당/진입로 · 북측 사면 · 남측 테라스."""
    if y >= 2.15:
        return bank_z(x)
    if y <= -1.7:
        return path_z(x) - SIDE_DROP
    return path_z(x)


def _zone_z(x, y, zone):
    """zone 태그로 접지면 선택: north/south/flat(마당 z=0)."""
    if zone == "north":
        return bank_z(x)
    if zone == "south":
        return path_z(x) - SIDE_DROP
    if zone == "flat":
        return 0.0
    return ground_z(x, y)


# ===========================================================================
# [E] 자연석 이산 배석 레이아웃 — seed 고정 random (재현 보장)
# ===========================================================================
def stone_layout():
    """돌별 개별 박스 사양 리스트를 반환(부팅 없이 계산 가능).

    각 원소: dict(i, xa, xb, cx, w, cy, thick, proud, top, rz, rx, gap_next)
      xa/xb = 돌의 −X/+X 끝, cx = 중심, w = Y 폭, cy = Y 중심 오프셋,
      top   = 상면 z (= path_z(cx) + proud), thick = 두께(매입 포함).
    간격·깊이는 원시 샘플을 x_end−x_start 에 정확히 맞춰 등비 스케일한다
    (총 run 을 고정해 하부 진입로 접속 좌표가 흔들리지 않게).
    """
    sp = PARAMS["stones"]
    rng = random.Random(int(sp["seed"]))
    n = int(sp["n"])
    raw = []
    for _ in range(n):
        raw.append((rng.uniform(*sp["depth"]), rng.uniform(*sp["gap"]),
                    rng.uniform(*sp["w"]), rng.uniform(*sp["proud"]),
                    rng.uniform(*sp["embed"]),
                    rng.uniform(-sp["rz"], sp["rz"]),
                    rng.uniform(-sp["rx"], sp["rx"]),
                    rng.random()))
    span = float(sp["x_end"]) - float(sp["x_start"])
    total = sum(d + g for d, g, *_ in raw)
    k = span / total                    # 등비 스케일(간격·깊이 동시)
    out = []
    x = float(sp["x_start"])
    fh = float(sp["foot_half"])
    for i, (d, g, w, pr, em, rz, rx, u) in enumerate(raw):
        dep = d * k
        gap = g * k
        xa, xb = x, x + dep
        cx = (xa + xb) / 2.0
        cy_max = max(0.0, w / 2.0 - fh)   # 워크라인 |y|≤fh 를 반드시 덮게
        cy = (u * 2.0 - 1.0) * min(cy_max, 0.35)
        out.append(dict(i=i, xa=xa, xb=xb, cx=cx, w=w, cy=cy,
                        proud=pr, thick=pr + em, top=path_z(cx) + pr,
                        rz=rz, rx=rx, gap_next=gap))
        x = xb + gap
    return out


STONES = stone_layout()


def knob_layout():
    """[v6] 돌별 캔트 노브 사양(부팅 없이 계산 — SMOKE 가 포함관계를 검산).

    각 원소: dict(i, cx, cy, dx, dy, thick, top, rz, rx, half_x, over_x)
      · top   = 주석 상면 − drop  → **보행면(GT)은 주석 상면 그대로 불변**.
      · half_x= 회전 후 X 반폭 = (dx·|cos| + dy·|sin|)/2.
      · over_x= half_x − 돌 깊이/2 (양수면 돌 밖으로 X 돌출 — 0.02 m 이하로 억제).
      · cy 는 한쪽으로 off_y·w 만큼 밀어 Y 실루엣이 주석 윤곽을 벗어나게 한다.
    """
    kp = PARAMS["knob"]
    rng = random.Random(int(kp["seed"]))
    out = []
    for s in STONES:
        dep = s["xb"] - s["xa"]
        dx = dep * float(kp["fx"])
        dy = s["w"] * float(kp["fy"])
        rz = rng.uniform(*kp["rz"]) * (1.0 if rng.random() < 0.5 else -1.0)
        rx = rng.uniform(*kp["rx"]) * (1.0 if rng.random() < 0.5 else -1.0)
        drop = rng.uniform(*kp["drop"])
        sgn = 1.0 if rng.random() < 0.5 else -1.0
        a = math.radians(abs(rz))
        half_x = (dx * math.cos(a) + dy * math.sin(a)) / 2.0
        out.append(dict(i=s["i"], cx=s["cx"], cy=s["cy"] + sgn * kp["off_y"]
                        * s["w"], dx=dx, dy=dy, thick=float(kp["thick"]),
                        top=s["top"] - drop, rz=rz, rx=rx,
                        half_x=half_x, over_x=half_x - dep / 2.0))
    return out


KNOBS = knob_layout()


def leaf_patches():
    """[v6] 낙엽 밴드 → 사면 추종 패치. (name, x0, z0, run, drop, y0, y1, rz).

    구현: 패치당 subs 매를 서로 다른 크기·오프셋으로 겹쳐 경계를 불규칙화(C-7).
    build_slope 는 회전 축이 Y 뿐이라 rz(yaw)는 쓸 수 없어, 대신 **폭·중심 지터**
    로 직사각 경계를 깬다. 상면 z 는 회랑 사면 P(x)+proud 에 정확히 얹힌다.
    """
    lb = PARAMS["leaf_band"]
    rng = random.Random(int(lb["seed"]))
    tan = STAIR_DROP / STAIR_RUN
    out = []
    for n, (cx, cy, sx, sy) in enumerate(PARAMS["leaf_drifts"]):
        for j in range(int(lb["subs"])):
            f = rng.uniform(*lb["sub_scale"]) if j else 1.0
            ox = (rng.uniform(-1.0, 1.0) * lb["sub_off"] * sx) if j else 0.0
            oy = (rng.uniform(-1.0, 1.0) * lb["sub_off"] * sy) if j else 0.0
            w = sx * f
            d = sy * f * rng.uniform(0.85, 1.15)
            x0 = min(max(cx + ox - w / 2.0, 0.04), STAIR_RUN - 0.05 - w)
            ycl = min(max(cy + oy, -1.66 + d / 2.0), 1.66 - d / 2.0)
            out.append((f"{n}_{j}", x0, path_z(x0) + lb["proud"], w, w * tan,
                        ycl - d / 2.0, ycl + d / 2.0))
    return out


LEAF_PATCHES = leaf_patches()


def stone_metrics():
    """배석 검증 지표 — (답차 리스트, 간격 리스트, 진입/탈출 단차)."""
    tops = [s["top"] for s in STONES]
    rises = [tops[i] - tops[i + 1] for i in range(len(tops) - 1)]
    gaps = [s["gap_next"] for s in STONES[:-1]]
    enter = 0.0 - tops[0]                        # 마당(z=0) → 1석 상면
    exit_ = tops[-1] - (-STAIR_DROP)             # 마지막 석 → 진입로(−4.2)
    return rises, gaps, enter, exit_


# ===========================================================================
# [F] 카메라 프리셋: grid_views(gy=0.0) + 미장센 5컷
#     전 좌표를 path_z()에서 산출 — 하드코딩 금지(사면 정합 보장).
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)          # h{0.3,0.9,1.8} × d{2,5,10}, +X

    # temple_walk : 마당 눈높이에서 진행방향 — 배석이 사면·낙엽에 녹아 낙차 소실
    #   [v7] 일주문이 −5.6 으로 후퇴 → eye 를 문 3.0 m 앞으로 물려 문이
    #   프레임 안에서 길을 감싸는 구도(구 −6.0 은 문 바로 아래가 된다).
    views["temple_walk"] = dict(eye=[-8.6, 0.0, 1.30],
                                tgt=[4.0, 0.0, path_z(4.0) + 0.30])
    # stone_rhythm : 배석 클로즈 — 간격·답차 불균일(디딤 리듬 파괴)
    views["stone_rhythm"] = dict(eye=[1.0, -1.05, path_z(1.0) + 0.60],
                                 tgt=[5.4, 0.10, path_z(5.4) + 0.05])
    # gate_frame : 배석 중턱에서 되돌아봄 — 일주문·석등·법당 실루엣 프레이밍
    #   [v7] tgt 를 이동한 일주문(cx −5.6)에 재정렬. 문 +X면 음영은 태양
    #   az 180~270 구간의 구조적 귀결 — 감독 결정(컷 미러) 대기 항목.
    views["gate_frame"] = dict(eye=[7.0, 0.0, path_z(7.0) + 1.50],
                               tgt=[PARAMS["gate"]["cx"], 0.0, 1.60])
    # side_slope : 남측 하부 테라스에서 무방호 1.8 m 낙차 단면
    views["side_slope"] = dict(
        eye=[6.0, -5.2, path_z(6.0) - SIDE_DROP + 1.20],
        tgt=[6.6, -1.5, path_z(6.6) - 0.35])
    # grazing_edge : 회랑 남측 어깨 로봇 시점 — 하부 테라스가 회랑과 이어져 보임
    #   시선 피치(−17.4°) < 사면각(19.0°) → 하부 테라스면이 지평 근처로 압축
    views["grazing_edge"] = dict(eye=[2.0, 1.10, path_z(2.0) + 0.30],
                                 tgt=[12.0, -1.50, path_z(12.0) + 0.60])
    return views


# ===========================================================================
# [G] SMOKE — 부팅 없는 기하 자기검증
# ===========================================================================
def lantern_height():
    """석등 총고(지대석 하면 → 보주 상단)."""
    ln = PARAMS["lantern"]
    return (ln["plinth_h"] + ln["lower_h"] + ln["shaft_h"] + ln["upper_h"]
            + ln["fire_h"] + ln["cap_h"] + ln["cap2_h"] + 2 * ln["jewel_r"])


def _grid_obstacles():
    """그리드 카메라(−d, 0, h) 충돌 검산용 AABB 목록 [(name,x0,x1,y0,y1,z0,z1)]."""
    g = PARAMS["gate"]
    hl = PARAMS["hall"]
    sg = PARAMS["sign"]
    ln = PARAMS["lantern"]
    obs = []
    for tag, sgn in (("P", 1.0), ("N", -1.0)):
        cy = sgn * g["half_y"]
        pr = g["post_r"] * 1.55            # [v6] 초석 반경 포함
        obs.append((f"GatePost_{tag}", g["cx"] - pr, g["cx"] + pr,
                    cy - pr, cy + pr, 0.0, g["post_h"]))
    # [v6] 부연(2단 처마) 포함 — 처마 최하단 z 는 ridge−0.45−drop'−0.11
    obs.append(("GateRoof", g["cx"] - g["roof_half_run"] - 0.35,
                g["cx"] + g["roof_half_run"] + 0.35,
                -(g["roof_y"] + 0.22), g["roof_y"] + 0.22,
                g["ridge_z"] - 0.45 - g["roof_drop"] * 1.20 - 0.11,
                g["ridge_z"]))
    obs.append(("Hall", hl["cx"] - hl["sx"] / 2.0, hl["cx"] + hl["sx"] / 2.0,
                hl["cy"] - hl["roof_y"], hl["cy"] + hl["roof_y"],
                0.0, hl["ridge_z"]))
    obs.append(("SignPost", sg["cx"] - 0.06, sg["cx"] + 0.06,
                sg["cy"] - sg["w"] / 2.0, sg["cy"] + sg["w"] / 2.0,
                0.0, sg["pole_h"]))
    for i, p in enumerate(PARAMS["lanterns"]):
        r = ln["cap_w"] / 2.0
        obs.append((f"Lantern_{i}", p["cx"] - r, p["cx"] + r,
                    p["cy"] - r, p["cy"] + r, 0.0, lantern_height()))
    for name, cx, cy, zone, th in PARAMS["pines"]:
        gz = _zone_z(cx, cy, zone)
        obs.append((f"Pine_{name}", cx - 0.9, cx + 0.9, cy - 0.9, cy + 0.9,
                    gz, gz + th + 1.4))
    return obs


def _smoke_report():
    P = PARAMS
    print("=" * 72)
    print("scene07_temple_stone_path (v5 R2) — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 72)
    slope_deg = math.degrees(math.atan2(STAIR_DROP, STAIR_RUN))
    print(f"  사면: run {STAIR_RUN:.2f} m / drop {STAIR_DROP:.2f} m "
          f"= {slope_deg:.1f}°  · 배석 {len(STONES)}석 (seed "
          f"{P['stones']['seed']})")
    print(f"  낙차 검증: 주낙차 {STAIR_DROP:.2f} ≥ 0.3 → "
          f"{'OK' if STAIR_DROP >= 0.3 else 'FAIL'} · "
          f"측방 {SIDE_DROP:.2f} ≥ 0.3 → "
          f"{'OK' if SIDE_DROP >= 0.3 else 'FAIL'}")

    # ── 표 [1][2][3] 배석 ──
    rises, gaps, enter, exit_ = stone_metrics()
    print("\n  [표] 자연석 이산 배석 (i, xa..xb, 폭 w, cy, 두께, 상면 z, "
          "답차→다음, 간격)")
    print(f"    {'i':>2} {'xa':>6} {'xb':>6} {'w':>5} {'cy':>6} {'thk':>5} "
          f"{'top z':>7} {'답차':>6} {'간격':>6} {'매입':>5} 워크라인")
    ok_walk = True
    for s in STONES:
        i = s["i"]
        rise = rises[i] if i < len(rises) else float("nan")
        y0, y1 = s["cy"] - s["w"] / 2.0, s["cy"] + s["w"] / 2.0
        fh = P["stones"]["foot_half"]
        covers = (y0 <= -fh + 1e-9) and (y1 >= fh - 1e-9)
        ok_walk = ok_walk and covers
        print(f"    {i:2d} {s['xa']:6.2f} {s['xb']:6.2f} {s['w']:5.2f} "
              f"{s['cy']:+6.2f} {s['thick']:5.2f} {s['top']:7.3f} "
              f"{rise:6.3f} {s['gap_next']:6.3f} "
              f"{s['thick'] - s['proud']:5.2f} {'OK' if covers else 'MISS'}")
    print(f"    [1] 진입 단차(마당 z0 → 1석 상면) = {enter:+.3f} m")
    print(f"    [2] 답차 min {min(rises):.3f} / max {max(rises):.3f} / "
          f"평균 {sum(rises)/len(rises):.3f} m  "
          f"(리듬 파괴 폭 {max(rises)-min(rises):.3f})")
    print(f"        간격 min {min(gaps):.3f} / max {max(gaps):.3f} m "
          f"(목표대 0.05~0.35 → "
          f"{'OK' if min(gaps) >= 0.045 and max(gaps) <= 0.355 else 'CHECK'})")
    print(f"    [3] 탈출 단차(마지막 석 → 진입로 z{-STAIR_DROP:.1f}) "
          f"= {exit_:+.3f} m")
    print(f"    보행 연속성: 전 배석이 워크라인 |y| ≤ "
          f"{P['stones']['foot_half']} 를 덮는가 → "
          f"{'OK' if ok_walk else 'FAIL'}")
    max_step = max(abs(enter), abs(exit_), max(abs(r) for r in rises))
    print(f"    최대 단일 답차 {max_step:.3f} m "
          f"({'보행 가능(<0.35)' if max_step < 0.35 else '과대 — 재조정 필요'})")
    emin = min(s["thick"] - s["proud"] for s in STONES)
    print(f"    최소 매입 깊이 {emin:.3f} m (>0 = 부유 없음 → "
          f"{'OK' if emin > 0.0 else 'FAIL'})")

    # ── [v6] 캔트 노브 : GT 불변 + X 돌출 억제 검산 ──
    over = max(k["over_x"] for k in KNOBS)
    # 노브 최고점 = top + (dy/2)·sin|rx| (rotX 가 Y 에지를 들어올림)
    ktop = [k["top"] + (k["dy"] / 2.0) * math.sin(math.radians(abs(k["rx"])))
            for k in KNOBS]
    marg = min(s["top"] - t for s, t in zip(STONES, ktop))
    kemb = max(k["top"] - k["thick"] - path_z(k["cx"]) for k in KNOBS)
    print(f"\n  [v6 노브] {len(KNOBS)}개 · 노브 최고점이 주석 상면보다 낮은 "
          f"여유 min {marg:+.4f} m (>0 = 보행면 GT 불변 → "
          f"{'OK' if marg > 0.0 else 'FAIL'})")
    print(f"    X 최대 돌출 {over:+.4f} m (≤0.02 → "
          f"{'OK' if over <= 0.02 else 'CHECK'}) · 노브 하면−회랑면 최대 "
          f"{kemb:+.3f} m (<0 = 전량 매입 → "
          f"{'OK' if kemb < 0.0 else 'CHECK'})")

    # ── [v6] 낙엽 패치 : 사면 정합·회랑 내 포함 검산 ──
    lb = P["leaf_band"]
    ferr = max(abs((z0) - (path_z(x0) + lb["proud"]))
               for _n, x0, z0, _r, _d, _y0, _y1 in LEAF_PATCHES)
    yout = max(max(abs(y0), abs(y1))
               for _n, _x, _z, _r, _d, y0, y1 in LEAF_PATCHES)
    xout = max(x0 + run for _n, x0, _z, run, _d, _y0, _y1 in LEAF_PATCHES)
    print(f"\n  [v6 낙엽] 패치 {len(LEAF_PATCHES)}매(밴드 "
          f"{len(P['leaf_drifts'])}×{lb['subs']}) · 사면 상면 정합 오차 "
          f"{ferr:.4f} m ({'OK' if ferr < 1e-6 else 'FAIL'})")
    print(f"    최대 |y| {yout:.3f} (<1.70 = 남측 공동 위 부유 없음 → "
          f"{'OK' if yout < 1.70 else 'FAIL'}) · 최대 x끝 {xout:.2f} "
          f"(≤{STAIR_RUN:.2f} → {'OK' if xout <= STAIR_RUN + 1e-9 else 'CHECK'})")

    # ── [v6] 태양 방위 → 면별 직사광 lambert 검산 ──
    az = 33.5 + float(P["SUN_AZ_OFFSET"])
    el = math.radians(float(P["light"]["noon_sun_elev"]))
    lx = math.cos(math.radians(az)) * math.cos(el)
    ly = math.sin(math.radians(az)) * math.cos(el)
    lz = math.sin(el)
    print(f"\n  [v6 태양] offset {P['SUN_AZ_OFFSET']:.1f} → 월드 az {az:.1f}° "
          f"(그림자 az {az - 180:.1f}°) · 고도 {math.degrees(el):.2f}°")
    for nm, N in (("−X향(원경 능선·문 정면)", (-1, 0, 0)),
                  ("−Y향(남측 무방호 석축)", (0, -1, 0)),
                  ("상면(마당·회랑·배석)", (0, 0, 1)),
                  ("+X향(gate_frame 문 배면)", (1, 0, 0))):
        d = N[0] * lx + N[1] * ly + N[2] * lz
        print(f"    {nm:<24} lambert {d:+.3f} "
              f"{'순광' if d > 0.15 else ('터미네이터' if d > 0 else '음영')}")
    lam_x = -lx                                   # −X향 lambert(원경 능선)
    for nm, key, old_a, old_l in (("근경 능선", "ridge_near", 0.052, 0.456),
                                  ("중경 능선", "ridge_mid", 0.088, 0.456),
                                  ("원경 능선", "ridge_far", 0.142, 0.456),
                                  ("마루 숲(근)", "crest_near", 0.042, 0.456)):
        a_new = P["material"][key][0]
        print(f"    {nm:<12} 알베도 {old_a:.3f}→{a_new:.3f} · 휘도곱 "
              f"{old_a*old_l:.4f} → {a_new*lam_x:.4f} "
              f"({'보존 OK' if a_new*lam_x >= old_a*old_l else 'CHECK(어두워짐)'}"
              f") · 순백 상한 0.72 "
              f"{'OK' if a_new <= 0.72 else 'FAIL'}")

    # ── [v7] 캐스트 그림자 발자국 × 그리드 하반 지면대 ──
    #   교훈(judge_v7 말미): "그림자는 사라지지 않고 이동한다". 면별 lambert 표는
    #   **캐스트 그림자가 어디로 가는지**를 말해주지 않는다 — W2 가 놓친 칸이
    #   '그리드 근경 지면'이었다. 여기서 두 표를 한 화면에서 대조한다.
    #   · 그림자 투영 : P → P − L·(P.z/L.z),  수평 이동 = −(cos az, sin az)·z·cot(el)
    #   · 하반 지면대 : 수직 반화각 18.0°(초점 18.147 / 수직 애퍼처 11.787),
    #     pitch −10° → 프레임 하단 −28° · 중앙 −10° 시선이 마당(z=0)에 닿는 x 구간
    cot = math.cos(el) / math.sin(el)
    sdx = -math.cos(math.radians(az)) * cot
    sdy = -math.sin(math.radians(az)) * cot
    g = P["gate"]
    ln_h = lantern_height()
    casters = [
        ("일주문 주지붕", g["cx"] - g["roof_half_run"],
         g["cx"] + g["roof_half_run"], -g["roof_y"], g["roof_y"],
         g["ridge_z"] - g["roof_drop"], g["ridge_z"]),
        ("일주문 부연", g["cx"] - g["roof_half_run"] - 0.30,
         g["cx"] + g["roof_half_run"] + 0.30, -(g["roof_y"] + 0.22),
         g["roof_y"] + 0.22,
         g["ridge_z"] - 0.45 - g["roof_drop"] * (g["roof_half_run"] + 0.30)
         / g["roof_half_run"], g["ridge_z"] - 0.45),
        ("일주문 기둥", g["cx"] - 0.24, g["cx"] + 0.24, -g["half_y"] - 0.24,
         g["half_y"] + 0.24, 0.0, g["post_h"]),
        ("석등(남)", P["lanterns"][1]["cx"] - 0.47,
         P["lanterns"][1]["cx"] + 0.47, P["lanterns"][1]["cy"] - 0.47,
         P["lanterns"][1]["cy"] + 0.47, 0.0, ln_h),
        ("안내판", P["sign"]["cx"] - 0.06, P["sign"]["cx"] + 0.06,
         P["sign"]["cy"] - P["sign"]["w"] / 2.0,
         P["sign"]["cy"] + P["sign"]["w"] / 2.0, 0.0, P["sign"]["pole_h"]),
        ("법당", P["hall"]["cx"] - P["hall"]["sx"] / 2.0,
         P["hall"]["cx"] + P["hall"]["sx"] / 2.0,
         P["hall"]["cy"] - P["hall"]["roof_y"],
         P["hall"]["cy"] + P["hall"]["roof_y"], 0.0, P["hall"]["ridge_z"]),
    ]
    print("\n  [v7 그림자] 캐스터 → 마당(z=0) 투영 발자국 · 워크라인 |y|≤0.22")
    shade = []                       # (이름, x0, x1, y_south) — 마당 위 그림자
    for nm, x0, x1, y0, y1, zlo, zhi in casters:
        xs = [x + sdx * z for x in (x0, x1) for z in (zlo, zhi)]
        ys = [y + sdy * z for y in (y0, y1) for z in (zlo, zhi)]
        sx0, sx1, sy0, sy1 = min(xs), max(xs), min(ys), max(ys)
        cross = (sy0 <= 0.22 and sy1 >= -0.22)
        shade.append((nm, sx0, sx1, sy0))
        print(f"    {nm:<12} x[{sx0:+6.2f},{sx1:+6.2f}] y[{sy0:+6.2f},"
              f"{sy1:+6.2f}]  워크라인 {'가로지름' if cross else '비껴감'}")
    big = [s for s in shade if (s[2] - s[1]) * 1.0 >= 2.0]     # 대형 캐스터만
    print("  [v7 하반 지면대] 프리셋별 프레임 아래절반이 찍는 마당 구간 "
          "(x_하단…x_중앙) vs 대형 그림자")
    for h in (0.3, 0.9, 1.8):
        for d in (2, 5, 10):
            xe = -float(d)
            xn = xe + h / math.tan(math.radians(28.0))
            xm = xe + h / math.tan(math.radians(10.0))
            half_w = (xn - xe) * math.tan(math.radians(30.0))   # 근단 반폭
            ov = []
            for nm, sx0, sx1, sy0 in big:
                if sx1 > xn and sx0 < xm and sy0 < half_w:
                    ov.append(nm if sy0 <= -half_w else f"{nm}(북측만)")
            state = "직사광" if not ov else ("부분(" + ",".join(ov) + ")")
            print(f"    h{h}_d{d:<3} 지면대 x[{xn:+6.2f},{xm:+6.2f}] "
                  f"반폭 ±{half_w:.2f} → {state}")
    print("    ※ x_중앙 > 0 인 프리셋은 하반이 배석·회랑(사면)이라 마당 투영이"
          " 아니라 SMOKE 사면 표로 판정한다.")

    # ── 지면 플레이트 표 + 남측 낙차 검증 ──
    print("\n  [표] 축정렬 지면 플레이트 (상면 z / 두께)")
    print(f"    {'이름':16s} {'x범위':>16s} {'y범위':>16s} {'상면z':>7s} 두께")
    for nm, x0, x1, y0, y1, zt, th, _m in P["plates"]:
        print(f"    {nm:16s} [{x0:7.1f},{x1:7.1f}] [{y0:7.2f},{y1:7.2f}] "
              f"{zt:7.2f} {th:5.2f}")
    print("  [표] 사면 플레이트 (x0=0, run=%.2f)" % STAIR_RUN)
    for nm, z0, drop, y0, y1, th, _m in P["slopes"]:
        print(f"    {nm:16s} z0 {z0:+6.2f} → {z0 - drop:+6.2f}  "
              f"y[{y0:7.2f},{y1:7.2f}] 두께 {th:.2f}")
    for x in (0.0, 3.0, 6.0, 9.0, 12.2):
        print(f"    x={x:5.1f}: 회랑 {path_z(x):+6.3f} / 남측테라스 "
              f"{path_z(x) - SIDE_DROP:+6.3f} (낙차 {SIDE_DROP:.2f}) / "
              f"북측사면 {bank_z(x):+6.3f} / 담 상단 {bank_z(x) + 0.75:+6.3f}")
    print("    남측 낙차는 y=−1.7 에서 플레이트가 갈라짐 → 공동 위 연속 평면 "
          "없음 (체크리스트 ③ OK)")

    # ── 그리드 카메라 vs 기하 충돌 검산 ──
    print("\n  [검산] 그리드 카메라(−d, 0, h) vs 기하 AABB")
    obs = _grid_obstacles()
    hit_any = False
    for d in (2, 5, 10):
        for h in (0.3, 0.9, 1.8):
            ex, ey, ez = -float(d), 0.0, float(h)
            hits = [nm for nm, x0, x1, y0, y1, z0, z1 in obs
                    if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1]
            if hits:
                hit_any = True
                print(f"    d{d} h{h}: ⚠ {hits}")
    print(f"    충돌 = {hit_any} (False 여야 함)  · 카메라 접지면 z=0 "
          "(Courtyard x −24..0, y −1.7..44) 내부 OK")

    # ── 미장센 카메라 좌표 ──
    print("\n  [카메라] 미장센")
    v = build_views()
    for vn in ("temple_walk", "stone_rhythm", "gate_frame", "side_slope",
               "grazing_edge"):
        vv = v[vn]
        print(f"    {vn:<14} eye={['%.2f' % e for e in vv['eye']]} "
              f"tgt={['%.2f' % t for t in vv['tgt']]}")
    print("=" * 72)


# ===========================================================================
# [H] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드      — 배석 너머 사면이 평지로 접히고 남측 낙차가 소실되나
 2. stone_rhythm     — 돌 간 간격·답차 불균일(디딤 리듬 파괴)이 읽히나
 3. grazing_edge     — 회랑면과 하부 테라스가 한 장 지면으로 이어져 보이나
 4. side_slope       — 무방호 1.8 m 석축 낙차 단면이 명확한가
 5. gate_frame       — 일주문·석등·석축담·법당이 '산사'로 판독되나
 6. 낙엽 밴드        — 돌 에지를 물고 덮어 단코 절단선을 지우나
 7. 접지             — 배석 매입(≥0.10)·석등·기둥에 부유·틈이 없나
 8. 지평 폐쇄        — 근경 능선 3분절 + 마루 숲 밴드가 검은 벽 없이 닫히나
10. [v6] 배석 재질   — 인접 돌의 결·색이 어긋나 '연속 줄눈 판석'이 사라졌나
11. [v6] 낙엽 밴드   — 사면에 밀착(하류단 부유·검은 사각 구멍 소멸)했나
12. [v6] 석등        — 굴뚝이 아니라 화사석·옥개석 갖춘 석등으로 읽히나
 9. cue 토글         — railing/tactile/nosing ON/OFF 시 위험 기하 불변인가"""


def main():
    smoke = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    if smoke:
        _smoke_report()
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view
    from pxr import UsdGeom

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene07")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene07"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl, rotY=rotY,
                               collider=col)

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        def tex_xform(mtl, translate=None, rotate=None):
            """[v6] 월드투영 UV 오프셋·회전. `scene_common` 무수정 원칙에 따라
            make_pbr 가 만든 OmniPBR 셰이더에 씬 로컬로 입력만 추가한다
            (OmniPBR.mdl 의 texture_translate/texture_rotate — project_uvw=True
            일 때 유효). 인접 배석의 결이 어긋나 '연속 줄눈'이 사라진다."""
            from pxr import UsdShade, Sdf, Gf
            sh = UsdShade.Shader(
                stage.GetPrimAtPath(mtl.GetPath().AppendChild("Shader")))
            if translate is not None:
                sh.CreateInput("texture_translate",
                               Sdf.ValueTypeNames.Float2).Set(
                    Gf.Vec2f(float(translate[0]), float(translate[1])))
            if rotate is not None:
                sh.CreateInput("texture_rotate",
                               Sdf.ValueTypeNames.Float).Set(float(rotate))
            return mtl

        M = {}
        # [v6] 구 M["stone"](stone_worn = 조적 줄눈)은 **폐기** — 배석은 아래
        #      rock_face 재질 풀에서 뽑는다(판정 §2 ⑤ '벽돌 줄눈 판석' 원인).
        # [v6] 석등·초석 = 무줄눈 화강암 톤(구 stone_cap = 조적 텍스처 → 굴뚝)
        M["stone_cap"] = tex("granite_dark", "/World/Looks/StoneCap",
                             sca["granite"], tint=mp["granite_tint"])
        M["rock"] = tex("rock_wall", "/World/Looks/Rock", sca["rock_wall"])
        M["leaf"] = tex("leaf_ground", "/World/Looks/Leaf",
                        sca["leaf_ground"], tint=mp["leaf_tint"])
        M["gravel"] = tex("gravel", "/World/Looks/Gravel", sca["gravel"],
                          tint=mp["gravel_tint"])
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["roof"] = sc.make_pbr(stage, "/World/Looks/Roof",
                                diffuse_color=mp["roof_color"],
                                roughness_const=0.9, specular_level=0.0)
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["shrub"] = sc.make_pbr(stage, "/World/Looks/Shrub",
                                 diffuse_color=mp["shrub"],
                                 roughness_const=mp["shrub_rough"],
                                 specular_level=0.0)
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        for tone in ("near", "mid", "far"):
            M[f"ridge_{tone}"] = sc.make_pbr(
                stage, f"/World/Looks/Ridge_{tone}",
                diffuse_color=mp[f"ridge_{tone}"], roughness_const=0.95,
                specular_level=0.0)
        for tone in ("near", "far"):
            M[f"crest_{tone}"] = sc.make_pbr(
                stage, f"/World/Looks/Crest_{tone}",
                diffuse_color=mp[f"crest_{tone}"], roughness_const=1.0,
                specular_level=0.0)
        # [v6] 배석 재질 풀 — rock_face(무줄눈) × scale/tint/rotate/translate 지터
        smp = PARAMS["stone_mtl"]
        rng = random.Random(int(smp["seed"]))
        jt = float(smp["jitter"])
        M["stone_pool"] = []
        for k in range(int(smp["n"])):
            base = (smp["tint_moss"] if (k % int(smp["moss_every"]) == 0)
                    else smp["tint_dry"])
            tint = tuple(max(0.0, c * (1.0 + rng.uniform(-jt, jt)))
                         for c in base)
            m = tex("rock_face", f"/World/Looks/StoneNat_{k}",
                    rng.uniform(*smp["scale"]), tint=tint,
                    bump=float(smp["bump"]))
            tex_xform(m, translate=(rng.uniform(-4.0, 4.0),
                                    rng.uniform(-4.0, 4.0)),
                      rotate=rng.uniform(0.0, 360.0))
            M["stone_pool"].append(m)
        # [v5 공통 레이어] 한글 사인 패널 — uv_mode=True (메시 st 1:1 정합)
        M["sign_info"] = sc.make_pbr(
            stage, "/World/Looks/SignInfo",
            sc.tex_path("sign_info", "diff"), None, None, 1.0,
            roughness_const=0.55, uv_mode=True)
        M["sign_back"] = sc.make_pbr(stage, "/World/Looks/SignBack",
                                     diffuse_color=mp["sign_back"],
                                     roughness_const=0.7)
        # 마당 재질 토글 (cue_material_break=False → 배석도 마사토 톤)
        #   [v6] 배석은 재질 풀에서 뽑는다. 토글 OFF 면 전부 마사토 단일 재질.
        if not cfg["cue_material_break"]:
            M["stone_pool"] = [M["gravel"]]
        return M

    # -------------------------------------------------------------------
    # 지형 : 축정렬 플레이트 표 + 사면 플레이트 표
    # -------------------------------------------------------------------
    def build_terrain(M):
        for nm, x0, x1, y0, y1, zt, th, mk in PARAMS["plates"]:
            BOX(f"{ROOT}/Plate_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zt - th / 2.0),
                (x1 - x0, y1 - y0, th), M[mk], col=True)
        for nm, z0, drop, y0, y1, th, mk in PARAMS["slopes"]:
            sc.build_slope(stage, f"{ROOT}/Slope_{nm}", 0.0, z0, STAIR_RUN,
                           drop, y0, y1, th, M[mk], margin=0.0, collider=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 : 배석·사면·남측 낙차를 z=0 평지로."""
        BOX(f"{ROOT}/FlatFill", (22.0, 5.0, -0.5), (136.0, 78.0, 1.0),
            M["gravel"], col=True)

    # -------------------------------------------------------------------
    # 자연석 이산 배석 (씬 로컬 — build_worn_stone_stairs 미사용)
    # -------------------------------------------------------------------
    def build_stones(M):
        pool = M["stone_pool"]
        for s in STONES:
            cz = s["top"] - s["thick"] / 2.0
            # 돌별 재질(월드투영 UV 가 서로 어긋난 풀) — 인접 줄눈 연속 파괴
            sc._oriented_box(stage, f"{ROOT}/Stone_{s['i']}",
                             (s["cx"], s["cy"], cz),
                             (s["xb"] - s["xa"], s["w"], s["thick"]),
                             pool[s["i"] % len(pool)], collider=True,
                             rotz=s["rz"], rotx=s["rx"])
        # 캔트 노브 : 주석보다 낮은 부속 덩어리(직사각 실루엣 파괴, GT 불변)
        for k in KNOBS:
            sc._oriented_box(stage, f"{ROOT}/StoneKnob_{k['i']}",
                             (k["cx"], k["cy"], k["top"] - k["thick"] / 2.0),
                             (k["dx"], k["dy"], k["thick"]),
                             pool[(k["i"] + 3) % len(pool)], collider=False,
                             rotz=k["rz"], rotx=k["rx"])
        # 낙엽 밴드 : 돌 에지 부분 가림 — **사면 추종**(19°) 패치 중첩(스캐터 금지)
        lb = PARAMS["leaf_band"]
        for nm, x0, z0, run, drop, y0, y1 in LEAF_PATCHES:
            sc.build_slope(stage, f"{ROOT}/LeafDrift_{nm}", x0, z0, run, drop,
                           y0, y1, lb["thick"], M["leaf"], margin=0.0,
                           collider=False)
        # 마당 낙엽 퇴적 : 평탄면이라 회전 박스 중첩(경계 불규칙화)
        yl = PARAMS["yard_leaf"]
        rng = random.Random(int(yl["seed"]))
        for n, (cx, cy, sx, sy) in enumerate(PARAMS["yard_drifts"]):
            for j in range(int(yl["subs"])):
                f = 1.0 if j == 0 else rng.uniform(*yl["scale"])
                ox = 0.0 if j == 0 else rng.uniform(-1.0, 1.0) * yl["off"] * sx
                oy = 0.0 if j == 0 else rng.uniform(-1.0, 1.0) * yl["off"] * sy
                sc._oriented_box(
                    stage, f"{ROOT}/YardLeaf_{n}_{j}",
                    (cx + ox, cy + oy,
                     lb["proud"] - lb["thick"] / 2.0 - j * 0.002),
                    (sx * f, sy * f * rng.uniform(0.85, 1.15), lb["thick"]),
                    M["leaf"], collider=False,
                    rotz=rng.uniform(-yl["rz"], yl["rz"]))

    # -------------------------------------------------------------------
    # 맞배지붕 : build_slope 2매(용마루에서 ±X 로 각각 하강)
    # -------------------------------------------------------------------
    def gable_roof(prefix, x_ridge, z_ridge, half_run, drop, y0, y1, thick,
                   mtl):
        """용마루(x_ridge, z_ridge)에서 ±X 양쪽으로 각각 drop 만큼 **하강**.
        build_slope 는 +X 하강 전용이므로 −X 반쪽은 시작점을 처마
        (x_ridge−half_run, z_ridge−drop)로 두고 drop=−drop(상승)으로 준다."""
        sc.build_slope(stage, f"{prefix}/RoofP", x_ridge, z_ridge, half_run,
                       drop, y0, y1, thick, mtl, margin=0.10, collider=False)
        sc.build_slope(stage, f"{prefix}/RoofN", x_ridge - half_run,
                       z_ridge - drop, half_run, -drop, y0, y1, thick, mtl,
                       margin=0.10, collider=False)

    # -------------------------------------------------------------------
    # 드레싱 : 일주문 · 석등 2 · 법당 실루엣 · 소나무 · 관목
    # -------------------------------------------------------------------
    def build_gate(M):
        g = PARAMS["gate"]
        for tag, sgn in (("P", 1.0), ("N", -1.0)):
            CYL(f"{ROOT}/Gate/Post_{tag}",
                (g["cx"], sgn * g["half_y"], g["post_h"] / 2.0),
                g["post_r"], g["post_h"], M["wood"], col=True)
            # [v6] 초석(주춧돌) — 목주가 지면에 바로 꽂힌 '베이지 박스' 인상 완화
            CYL(f"{ROOT}/Gate/Plinth_{tag}",
                (g["cx"], sgn * g["half_y"], 0.15),
                g["post_r"] * 1.55, 0.30, M["stone_cap"], col=True)
        # 창방(가로 인방)
        BOX(f"{ROOT}/Gate/Beam",
            (g["cx"], 0.0, g["post_h"] + g["beam_t"] / 2.0),
            (g["post_r"] * 2.2, 2 * (g["half_y"] + g["beam_over"]),
             g["beam_t"]), M["wood"])
        gable_roof(f"{ROOT}/Gate", g["cx"], g["ridge_z"], g["roof_half_run"],
                   g["roof_drop"], -g["roof_y"], g["roof_y"], g["roof_t"],
                   M["roof"])
        # [v6] 부연(2단 처마) — 주 지붕 아래 0.34 m, 0.30 m 더 내밀어 처마 그림자
        #      2단을 만든다(한국 사찰 문의 겹처마 판독 단서). 관통 없음:
        #      하단 처마 상면(ridge−0.34)이 주 지붕 하면(ridge−roof_t)보다 낮다.
        gable_roof(f"{ROOT}/GateEave", g["cx"], g["ridge_z"] - 0.45,
                   g["roof_half_run"] + 0.30,
                   g["roof_drop"] * (g["roof_half_run"] + 0.30)
                   / g["roof_half_run"],
                   -(g["roof_y"] + 0.22), g["roof_y"] + 0.22, 0.11,
                   M["wood"])

    def build_lanterns(M):
        """석등 2기 — 지대석·하대석·간주석·상대석·화사석·옥개석 2단·보주.
        [v6] 구 형상(사각 몸통 + 사각 갓)은 조적 텍스처와 겹쳐 '벽돌 굴뚝'으로
        읽혔다. 부재 구성을 표준 석등 프로파일로 바꾸고 화사석에 암부 화창을
        내어 실루엣만으로 판독되게 한다. 총고 = lantern_height()."""
        ln = PARAMS["lantern"]
        pw, ph = ln["plinth_w"], ln["plinth_h"]
        for i, p in enumerate(PARAMS["lanterns"]):
            gz = ground_z(p["cx"], p["cy"])
            pre = f"{ROOT}/Lantern_{i}"
            BOX(f"{pre}/Plinth", (p["cx"], p["cy"], gz + ph / 2.0),
                (pw, pw, ph), M["stone_cap"], col=True)           # 지대석
            z = gz + ph
            CYL(f"{pre}/Lower", (p["cx"], p["cy"], z + ln["lower_h"] / 2.0),
                ln["lower_r"], ln["lower_h"], M["stone_cap"])      # 하대석
            z += ln["lower_h"]
            CYL(f"{pre}/Shaft", (p["cx"], p["cy"], z + ln["shaft_h"] / 2.0),
                ln["shaft_r"], ln["shaft_h"], M["stone_cap"])      # 간주석
            z += ln["shaft_h"]
            CYL(f"{pre}/Upper", (p["cx"], p["cy"], z + ln["upper_h"] / 2.0),
                ln["upper_r"], ln["upper_h"], M["stone_cap"])      # 상대석
            z += ln["upper_h"]
            # 화사석 : 모서리 기둥 4 + 내부 암부(화창) — 관통 없음(기둥이 외곽)
            fo = (ln["fire_w"] - ln["pillar"]) / 2.0
            for j, (sx, sy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
                BOX(f"{pre}/Fire_{j}",
                    (p["cx"] + sx * fo, p["cy"] + sy * fo,
                     z + ln["fire_h"] / 2.0),
                    (ln["pillar"], ln["pillar"], ln["fire_h"]), M["stone_cap"])
            BOX(f"{pre}/FireCore",
                (p["cx"], p["cy"], z + ln["fire_h"] / 2.0),
                (ln["fire_w"] - 2 * ln["pillar"] - 0.02,
                 ln["fire_w"] - 2 * ln["pillar"] - 0.02,
                 ln["fire_h"] * 0.92), M["roof"])
            z += ln["fire_h"]
            BOX(f"{pre}/Cap", (p["cx"], p["cy"], z + ln["cap_h"] / 2.0),
                (ln["cap_w"], ln["cap_w"], ln["cap_h"]), M["stone_cap"])
            z += ln["cap_h"]
            BOX(f"{pre}/Cap2", (p["cx"], p["cy"], z + ln["cap2_h"] / 2.0),
                (ln["cap2_w"], ln["cap2_w"], ln["cap2_h"]), M["stone_cap"])
            z += ln["cap2_h"]
            sc.add_sphere(stage, f"{pre}/Jewel",
                          (p["cx"], p["cy"], z + ln["jewel_r"]),
                          (ln["jewel_r"],) * 3, M["stone_cap"])    # 보주

    def build_hall(M):
        """상부 법당 실루엣 : 기단(석축) + 기둥열 + 맞배지붕."""
        hl = PARAMS["hall"]
        BOX(f"{ROOT}/Hall/Base", (hl["cx"], hl["cy"], hl["base_h"] / 2.0),
            (hl["sx"] + 1.2, hl["sy"] + 1.2, hl["base_h"]), M["rock"],
            col=True)
        n = int(hl["n_posts"])
        for j in range(n):
            t = (j / float(n - 1)) - 0.5
            px = hl["cx"] + t * (hl["sx"] - 0.8)
            for tag, sgn in (("P", 1.0), ("N", -1.0)):
                CYL(f"{ROOT}/Hall/Post_{j}_{tag}",
                    (px, hl["cy"] + sgn * (hl["sy"] / 2.0 - 0.4),
                     hl["base_h"] + hl["post_h"] / 2.0),
                    hl["post_r"], hl["post_h"], M["wood"])
        # 몸체(벽) — 기둥열 안쪽 어두운 판
        BOX(f"{ROOT}/Hall/Body",
            (hl["cx"], hl["cy"], hl["base_h"] + hl["post_h"] / 2.0),
            (hl["sx"] - 1.0, hl["sy"] - 1.2, hl["post_h"]), M["wood"])
        gable_roof(f"{ROOT}/Hall", hl["cx"], hl["ridge_z"],
                   hl["roof_half_run"], hl["roof_drop"],
                   hl["cy"] - hl["roof_y"], hl["cy"] + hl["roof_y"],
                   hl["roof_t"], M["roof"])

    def build_nature(M):
        tr = PARAMS["tree"]
        for name, cx, cy, zone, th in PARAMS["pines"]:
            gz = _zone_z(cx, cy, zone)
            sc.build_tree(stage, f"{ROOT}/Pine_{name}", cx, cy, gz,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=tr["trunk_r"], trunk_h=th,
                          stake_r=0.004, stake_h=0.02, stake_off=0.2)
        # 관목 = 눌린 타원체 3개 중첩 (scene04 v5 규약 — 각진 판떼기 금지)
        #   [v6] 사면(zone north/south 는 X 방향 경사)에 얹을 때 블롭 중심 z 로
        #   접지하면 **하류측이 rx·tan19° 만큼 뜬다** → 하류단(x+rx) 지면을 기준
        #   으로 낮춰 부유를 구조적으로 제거한다.
        sh = PARAMS["shrub"]
        emb = sh["embed"]
        for n, (cx, cy, zone) in enumerate(PARAMS["shrubs"]):
            for j, (dx, dy, rx, ry, rz) in enumerate(sh["blobs"]):
                bx, by = cx + dx, cy + dy
                gz = min(_zone_z(bx - rx, by, zone), _zone_z(bx, by, zone),
                         _zone_z(bx + rx, by, zone))
                sc.add_sphere(stage, f"{ROOT}/Shrub_{n}_{j}",
                              (bx, by, gz + rz * (1.0 - emb)),
                              (rx, ry, rz), M["shrub"])

    def build_horizon(M):
        """지평 폐쇄 : 앞 능선(근경 3분절 + 중·원경) + 마루 숲 밴드 + 뒤 숲 라인.
        [v6] 근경 능선을 엇물린 3매로 쪼개고 각 마루에 라운드 크라운 숲 밴드를
        얹어 '직선 능선 + 검은 벽'을 해소한다(알베도는 material 참조)."""
        rg = PARAMS["ridge"]
        for i, r in enumerate(rg):
            BOX(f"{ROOT}/Ridge_{i}", (r["cx"], r["cy"], r["z0"] + r["h"] / 2.0),
                (r["sx"], r["sy"], r["h"]), M[f"ridge_{r['tone']}"], col=True)
        for n, (ri, hh, tone) in enumerate(PARAMS["ridge_crest"]):
            r = rg[ri]
            top = r["z0"] + r["h"]
            sc.build_hedge(stage, f"{ROOT}/RidgeCrest_{n}",
                           r["cx"] - r["sx"] * 0.62, r["cy"] - r["sy"] / 2.0,
                           r["cx"] + r["sx"] * 0.62, r["cy"] + r["sy"] / 2.0,
                           hh, mtl=M[f"crest_{tone}"], base_z=top - 0.4)
        for i, t in enumerate(PARAMS["ridge_trees"]):
            r = rg[t["ri"]]
            sc.build_tree(stage, f"{ROOT}/RidgeTree_{i}", r["cx"], t["cy"],
                          r["z0"] + r["h"] - 0.4,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.16, trunk_h=4.2, stake_r=0.004,
                          stake_h=0.02, stake_off=0.2)
        bh = PARAMS["back_hedge"]
        for i, h in enumerate(PARAMS["back_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/BackHedge_{i}",
                           bh["cx"] - bh["sx"] / 2.0,
                           h["cy"] - bh["length"] / 2.0,
                           bh["cx"] + bh["sx"] / 2.0,
                           h["cy"] + bh["length"] / 2.0, bh["h"],
                           base_z=h["base"])
        for i, t in enumerate(PARAMS["back_trees"]):
            sc.build_tree(stage, f"{ROOT}/BackTree_{i}", t["cx"], t["cy"],
                          t["gz"], M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_h=t["trunk_h"], stake_r=0.004, stake_h=0.02,
                          stake_off=0.2)
        for nm, x0, x1, y0, y1, hh, bz in PARAMS["far_hedges"]:
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{nm}", x0, y0, x1, y1, hh,
                           base_z=bz)

    def build_sign(M):
        """[v5 공통 레이어] 사찰 안내판 — 진입부(일주문 앞), 접근 시점 대향."""
        sg = PARAMS["sign"]
        sc.build_sign(stage, f"{ROOT}/SignInfo", sg["cx"], sg["cy"], 0.0,
                      sg["yaw"], M["sign_info"], w=sg["w"], h=sg["h"],
                      pole_h=sg["pole_h"], pole_mtl=M["wood"],
                      back_mtl=M["sign_back"])

    def build_cues(M):
        """비관행 설비 단서(코드 경로만 — 기본 전부 False)."""
        if cfg["cue_railing"]:
            def gfn(x):
                return path_z(x)
            sc.build_railing_line(stage, f"{ROOT}/Rail", -1.55, 0.0, 0.0,
                                  STAIR_RUN, STAIR_DROP, gfn, M["rail"],
                                  rail_h=0.9, post_r=0.035, spacing=1.4,
                                  rail_r=0.035)
        if cfg["cue_tactile"]:
            tac = sc.make_pbr(stage, "/World/Looks/Tactile",
                              diffuse_color=(0.85, 0.72, 0.10),
                              roughness_const=0.7)
            sc.build_tactile(stage, f"{ROOT}/Tactile", -0.62, -0.02,
                             -1.6, 1.6, tac, z=0.0)
        if cfg["cue_nosing"]:
            for s in STONES:
                BOX(f"{ROOT}/Nose_{s['i']}",
                    (s["xb"] - 0.03, s["cy"], s["top"] + 0.002),
                    (0.06, s["w"] * 0.9, 0.012), M["stone_cap"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    if cfg["hazard_stairs"]:
        build_terrain(M)
        build_stones(M)
        build_cues(M)
    else:
        build_flat_fill(M)
    build_horizon(M)
    if cfg["cue_scene_dressing"] and cfg["hazard_stairs"]:
        build_gate(M)
        build_lanterns(M)
        build_hall(M)
        build_nature(M)
    if cfg["cue_sign"] and cfg["hazard_stairs"]:
        build_sign(M)

    rises, gaps, enter, exit_ = stone_metrics()
    print(f"[기하] 배석 {len(STONES)}석 run={STAIR_RUN:.2f} drop="
          f"{STAIR_DROP:.2f} · 답차 {min(rises):.3f}~{max(rises):.3f} · "
          f"간격 {min(gaps):.3f}~{max(gaps):.3f} · 측방 낙차 {SIDE_DROP:.2f}")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── 카메라 + 렌더 모드 ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views()
    _v0 = views["temple_walk"]
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

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    if capture_mode:
        out_dir_default = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, views, out_dir_default,
                            set_render_mode, look_from)
        simulation_app.close()
        return

    # ── GUI 룩 체크 ──
    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene07_{ts}.png")
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
