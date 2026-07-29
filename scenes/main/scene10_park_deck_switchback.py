# -*- coding: utf-8 -*-
"""
scene10_park_deck_switchback.py — NegObs 인공씬 10호(v5 R5): 공원 경사면 데크 갈지자

유형   : R5 (v5 재설계) — 목재 데크 지그재그 계단(open riser 투과 단서 계승)
사양서 : Docs/briefs/multi_scene_brief_v5.md §R5 + Docs/scene_redesign_v5_proposal.md
공통   : scene_common.py (무수정) / 골격 관례 : scenes/main/scene04_parktrail.py
계승   : scenes/archive_v3/scene10_switchback_cliff.py
         (rot_group 180° 반전 + **갈지자 병렬 Y 대역** 규약 · open_riser 빌더)

────────────────────────────────────────────────────────────────────────────
[위험 본질]
  근린공원 둘레길 경사면의 목재 데크 갈지자 계단. 위험은 **규정 미달의 현실**.

  ① 참 난간 1개소 파손 — 첫 참(z −1.65, x 4.4 외측 에지)의 가로대 2본이
     탈락하고 포스트만 남았다. 그 아래 지면은 z −6.62 → **4.97 m 개방 낙차**.
     포스트만 남은 난간은 로봇 시점에서 '난간 있음'으로 오검출되기 쉽다
     (설비 역추론 단서의 함정 사례).
  ② 라이저 부재(open riser) — 목재 디딤판 사이로 아래 플라이트·지면이 투시.
     디딤면-라이저 명암 쌍이 없어 단코 절단선이 성립하지 않는다.
  ③ 낙엽 퇴적 — 상단 2단(디딤판 1·2)의 에지를 leaf_ground 밴드가 물고 덮어
     첫 단코를 지운다. 상부 접근 로봇 시점(h0.3)에서 '평탄한 데크 진입'으로
     읽히는 것이 이 씬의 GT 양성 핵심.
  ④ 트레일 남측(−Y) 30° 잔디 사면 무방호 — 둘레길 어깨(y −1.6) 밖은 30°로
     떨어져 4 m 이내 2.3 m 하강. 난간·연석 없음(공원 흙길 비관행).

[보행 연속성 자가 검증표]  — 진입 → 하강 → 탈출 (SMOKE 가 전수 재계산)
  ┌ 구간 ──────────────────┬ 좌표(x, y대역, z) ────────────┬ 단차 ─────────┐
  │ 상부 둘레길(진입)       │ x −40..−1.5, y −1.6..1.45, 0.0 │ 평탄          │
  │ 진입 데크(옹벽 머리)    │ x −1.5..0,  y ±1.40,   −0.005  │ 0.005         │
  │ 플라이트0 (+X, −Y대역)  │ x 0→3.0,   z 0→−1.65 (10단)    │ riser 0.165   │
  │ 참0 (반전)              │ x 3.0..4.4, y ±1.40,   −1.65   │ 0 (플러시)    │
  │ 플라이트1 (−X, +Y대역)  │ x 3.0→0.0, z −1.65→−3.30       │ riser 0.165   │
  │ 참1                     │ x −1.4..0,  y ±1.40,   −3.30   │ 0             │
  │ 플라이트2 (+X, −Y대역)  │ x 0→3.0,   z −3.30→−4.95       │ riser 0.165   │
  │ 참2                     │ x 3.0..4.4, y ±1.40,   −4.95   │ 0             │
  │ 플라이트3 (−X, +Y대역)  │ x 3.0→0.0, z −4.95→−6.60       │ riser 0.165   │
  │ 참3                     │ x −1.4..0,  y ±1.40,   −6.60   │ 0             │
  │ 하부 산책로(탈출)       │ 지면 z −6.62 (참3 2 cm 아래)   │ 0.02          │
  └─────────────────────────┴────────────────────────────────┴───────────────┘
  · 참에서의 방향 전환 동선: (x_bot, y −0.70) → (참 중앙, y 0) → (x_bot, y +0.70)
    — 두 폭 대역이 참 안(y ±1.40)에 모두 들어오므로 끊김 없음.
  · 상·하 플라이트 연직 여유 = 2×1.65 − 0.29(스트링거+디딤판) = 3.01 m.
  · 짝수 대역 y[−1.39,−0.01] / 홀수 대역 y[+0.01,+1.39] — 겹침 0(간극 0.02).

[기하 핵심]
  · 플라이트 4 × 10단, riser 0.165 / tread 0.30 / 폭 1.38, 총 낙차 6.60.
  · 순수 갈지자는 수평 진행이 없다(평면 x −1.4..4.4). 따라서 계단 구간의 지면은
    사실상 연직이어야 하며, 이를 **공원 절토 석축 옹벽**(x=−1.5 머리 옹벽 +
    y=1.45 측면 옹벽)으로 실체화했다. 브리프의 "경사 30°"는 그 **주변 사면**
    (북측 +Y 30° 잔디 사면 / 남측 −Y 30° 잔디 사면)이 그대로 충족한다.
  · 공동(계단 통로) 위를 덮는 지면 평면 없음 — 상부 트레일 플레이트는 x=−1.5
    에서 끊기고, 그 앞(x −1.5..4.4)은 하부 산책로(z −6.62)만 존재.

[v6 판정 재수정 — judge_v6_rt_new7.md §4 + 감독 결정 3항]
  ① **태양 재선정**(감독 승인 — 개방측 순광). 구 `SUN_AZ_OFFSET=171.5`
     (월드 az 205 = 태양이 −X·−Y 하늘)은 **머리 옹벽(x=−1.5, 상단 z 0)** 이
     갈지자 통로를 통째로 그림자에 넣었다: 깊이 d 인 점의 그림자 경계는
     x < −1.5 + 0.766·d 이므로 d 6.6 m 지점까지 x 3.56 이 암부 = 통로 전체.
     `from_below`·`through_treads` 2컷 사망의 직접 원인.
     → `SUN_AZ_OFFSET=216.5` (월드 az = 33.5+216.5 = **250**, 그림자 az 70).
       이 씬에서 뚫린 방향은 **−Y(남측 하부 공원)** 과 +X 뿐이므로 태양을 −Y
       쪽으로 크게 돌려 통로에 직사광을 넣는다. 태양 광선 역추적 검산:
         (x 1.7, y −0.7, z −4.24) → z=0 도달점 (0.47, −4.07) : x=−1.5 평면을
         가로지르지 않음 → 머리 옹벽·남측 사면 미차폐 = **직사광 도달**.
       면별 lambert (고도 49.79 → 수평성분 0.6456):
         −Y향(데크 스트링거·참 코·북측 옹벽면 = 4개 미장센 컷의 피사체) 0.607
         −X향(그리드 축 정면·원경 능선)                                0.221
         상면(트레일·참·디딤판·잔디)                                   0.763
       그리드(+X 관람)의 −X향이 0.221 로 낮아지지만 그리드 화면은 대부분
       **상면**(0.763)이라 판독 손실이 없다. 반대로 −Y향이 0.273→0.607 로 2.2배.
     · 최하부(참3, x −1.4..0, z −6.60)는 머리 옹벽 바로 밑이라 어떤 서쪽 태양
       에서도 그늘 — 6.6 m 절토 바닥의 물리적 사실로 남긴다(핵심 단서 컷 4개는
       모두 직사광 구간).
  ② **"성곽 옹벽" 인상 해소** (판정 ⑤ '재질·스케일 교체가 공원 판독의 핵심')
     (a) `rock_wall` UV 3.0 m → **0.9 m** : 석괴 0.6 m급 성곽 조적 → 0.18 m급
         **발파석 사석쌓기**(공원 절토면 관행).
     (b) 인공 옹벽과 **자연 절개면을 재질로 분리** : 머리 옹벽·북측 옹벽만
         조적(`rock_wall`), 남측 사면 몸체(x=−1.5 에서 하부 공원으로 떨어지는
         절개면)는 `rock_face`(무줄눈 자연암) — 종전엔 이 면까지 조적이라
         `from_below` 좌반부가 통째로 성벽이었다.
     (c) **동측 옹벽 2단화**(x 5.2..44) : 6.62 m 단일 벽 → 하단 3.32 m + **소단
         1.0 m(식재)** + 상단 3.30 m. 도시공원 절토 옹벽의 표준 단면이며,
         데크 구간(x −1.5..5.2)은 단일 벽 그대로라 **위험 기하 불변**.
     (d) 옹벽 상단 **갓돌(코핑) 밴드** — 벽두께보다 0.08 m 내민 콘크리트 띠.
  ③ **난간이 가설 사다리틀/교수대** (판정 ⑤) → 상·중 가로대만 있던 난간에
     **세로 살**(0.30 m 간격)을 넣었다. 공원 데크 난간의 표준이며, 세로살이
     들어가면 인접 플라이트의 사선 레일이 '브레이스'로 오독되지 않는다.
  ④ **낙엽·흙길 사각 데칼**(C-7)·**confetti 채도**(판정 ⑤) → 흙길 UV 3.0→1.1,
     낙엽 1.8→1.05, 틴트 중성화, 지면 낙엽 패치를 3매 회전 중첩으로 경계 파괴.
  ⑤ 관목이 사면 위에서 뜨는 문제 → 블롭 접지 z 를 **하류측 지면**으로 낮춤.
  ⑥ 원경 롤리팝(C-4) → 원경 수목 줄기 반경·높이 지터 + 원경 능선 마루에
     숲 실루엣 밴드(build_hedge 라운드 크라운).

[v7 판정 재수정 — judge_v7_rt_A.md §7 "미장센 4컷이 공원으로 안 읽힌다"]
  판정문 결론: **"남은 것은 코드가 아니라 카메라"** — 재질 수정(사석 축소·
  자연암 분리·2단 옹벽·세로살)은 충분하나 4컷 전부가 데크 클로즈업이라
  공원 신호(잔디·관목·수목·이용자 시설)가 한 컷에도 안 들어왔다. 반면
  그리드 컷은 공원으로 읽힌다 = 기하가 아니라 프레이밍 문제.
  ① **`from_below` 개방측(−Y) 미러**(㉡ 직접 지시) : 구 시선 129.6° 는 피사면의
     절반이 +X향(머리 옹벽·절개면 = lambert −0.342)이라 mean 36.4·dark 66.3 %
     였다. eye (8.0,−7.5)→**(5.2,−10.8)**, 시선 105.4°(법선 285.4° =
     **lambert +0.527**), 피치 +6.6°. 프레임 하단 시선이 **하부 공원 흙길**에
     착지하고 관목 3·북측 잔디사면 3·이정표·벤치 = **공원 앵커 8개**가 화각 안.
  ② **`reversal` 후퇴·상승 재조준**(㉠) : eye (3.7,−3.2,−0.30)→**(6.6,−6.6,1.20)**,
     피치 −24° → **−16°**. 프레임 상단(+2.0° 앙각)이 옹벽 갓돌 너머 **북측 30°
     잔디 사면**을 담아 화면의 약 1/4 이 녹지가 된다(참0·플라이트0/1 유지).
  ③ **`broken_rail` 남측 회전** : 시선 135°(lambert +0.273, 파손/정상 난간이
     같은 어두운 대역) → 112°(**+0.480**). 하단 시선이 참0 아래 수직 공간을
     지나 z −4.46 에 착지 → 낙차 깊이가 프레임에 남는다.
  ④ **이정표 재축소**(㉢) : 방향판 0.72×0.11 → **0.58×0.09**, 높이 1.72/1.98 →
     **1.80/2.06**, 기둥 r 0.065 → 0.080 · 전고 2.26 → 기둥 노출 79 %.
  ⑤ 하부 공원 관목 1군락 추가(0.5,−5.5) — `from_below` 좌측 프레이밍용(§6
     "판독에 필요한 최소" 통과: 이 컷의 공원 판독이 재수정 사유 그 자체).
  검산: SMOKE `[v7 미장센]` — 컷별 시선/법선/**lambert**, 프레임 하단 시선의
        지면 착지점, 화각(수평 ±30°·수직 ±18°) 안의 공원 앵커 열거.
  미조치: `through_treads`(투과 클로즈업, v7 "개선 확정") 는 성격상 앵커 0 —
        lambert +0.620 로 조도만 확인하고 구도 유지.
────────────────────────────────────────────────────────────────────────────

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene10_park_deck_switchback.py

자동 캡처 : NEGOBS_CAPTURE=1 python scene10_park_deck_switchback.py
스모크    : NEGOBS_SMOKE=1 python3 scene10_park_deck_switchback.py  (부팅 없음)

좌표계: Z-up, m. 플라이트는 로컬 +X 하강(관례). 홀수 플라이트는 rot_group 180°
        (피벗 = 플라이트 상단) → 월드에서 −X 방향. 그리드 축 = 상부 접근(+X).
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
    "hazard_stairs":      True,    # False → 플라이트를 z=0 평판 데크로(낙차 제거)
    "cue_railing":        True,    # 공원 데크 = 난간 관행. **단 참0 외측 1개소 파손**
    "cue_tactile":        False,   # 공원 흙길 비관행(v5 브리프 §공통) — 코드 경로만
    "cue_material_break": True,    # 목재 데크 vs 잔디/낙엽 지면 대비
    "cue_sign":           False,   # [v5.2 사용자] 임의 경고 팻말 제거 — 배치 없음(키만 예약)
    "cue_scene_dressing": True,    # 수목·관목·이정표·벤치·쉼터 정자
    "cue_nosing":         False,   # 목재 데크 단코 띠는 비관행 — 코드 경로만
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- 갈지자 플라이트 (archive_v3/scene10 병렬 Y 대역 규약 계승) ---
    #   half_w 0.69 → 폭 1.38 ≈ 브리프 1.4. y_off 0.70 → 두 대역 간극 0.02.
    flights=dict(n=4, steps=10, riser=0.165, tread=0.30, half_w=0.69,
                 y_off=0.70, tread_t=0.05, gap=0.02, z_top=0.0),
    # 참 1.4(X) × 2.8(Y) — 두 폭 대역을 모두 덮는다
    landing=dict(size=1.4, thick=0.12, y0=-1.40, y1=1.40),
    # 진입 데크 : 옹벽 머리(x −1.5)에서 첫 단(x 0)까지 — 상부 트레일과 접속
    entry=dict(x0=-1.5, x1=0.0, top=-0.005, thick=0.10),
    # 데크 기둥 : 참 네 모서리(참 x 끝에서 0.15 안쪽) × y ±half_y.
    #   실제 (x, z 구간)은 post_segments() 가 참 스택에서 산출한다.
    post=dict(r=0.075, half_y=1.25, inset=0.15),
    # 난간 : 상부 가로대 h1.05 / 중간 h0.55, 포스트 간격 1.05
    #   [v6] baluster = 세로 살(공원 데크 난간 표준). 가로대만 있으면 '가설
    #   사다리틀'로 읽힌다(판정 §4 ⑤). 파손 개소(참0 외측)는 세로살도 탈락.
    rail=dict(h=1.05, mid=0.55, post_r=0.05, post_h=1.10, bar_t=0.06,
              spacing=1.05, broken_landing=0,   # 참0 외측 = 파손 개소
              bal_r=0.022, bal_step=0.30, bal_top=1.02),

    # --- 지면 축정렬 플레이트 (name, x0, x1, y0, y1, z_top, thick, mtl) ---
    #   v5 회귀 체크리스트 ③ : 상부 트레일은 x=−1.5 에서 **끊긴다**
    #   (계단 공동 위를 덮지 않음). 그 앞은 하부 산책로(−6.60)만.
    #   [Z-파이팅 회피] 하부 산책로 지면 상면은 −6.62 로, 데크 최하단(−6.60)
    #   보다 2 cm 낮다 → 참3·플라이트3 마지막 디딤판이 지면과 동일평면이 되지
    #   않는다(교훈 8). 보행 단차 0.02 m 는 연속성 표에서 검증.
    #   [v6 ②(c)] BankCut(북측 옹벽)은 데크 구간 x −40..5.2 만 6.62 m 단일 벽으로
    #   남기고, 동측 x 5.2..44 는 **하단벽 + 소단(1.0 m) + 상단벽** 2단으로 나눈다.
    #   소단 상면 z −3.30, 상단벽은 y 2.45..2.60 으로 물러서 그림자선이 생긴다.
    plates=[
        ("UpperTrail",   -40.0,  -1.5,  -1.60,  1.45,  0.00, 0.45, "grass"),
        ("UpperBody",    -40.0,  -1.5,  -1.60,  1.45, -0.45, 6.95, "rock"),
        ("TrailPath",    -40.0,  -1.6,  -0.85,  0.85,  0.002, 0.06, "dirt"),
        ("BankCut",      -40.0,   5.20,  1.45,  2.60,  0.00, 7.40, "rock"),
        ("EastTierLow",    5.20, 44.0,   1.45,  2.45, -3.30, 4.30, "rock"),
        ("EastTierUp",     5.20, 44.0,   2.45,  2.60,  0.00, 3.50, "rock"),
        ("LowerParkMain", -1.5,  44.0, -13.00,  1.45, -6.62, 1.50, "grass"),
        ("LowerParkFar", -40.0,  44.0, -60.00, -13.00, -6.62, 1.50, "grass"),
        ("LowerPath",     -1.5,  44.0,  -4.40, -2.60, -6.618, 0.06, "dirt"),
        ("FarHill",      -40.0,  44.0,  15.00, 40.00,  7.16, 9.00, "grass"),
        # 계곡 건너 원경 능선 (+X 지평 폐쇄)
        ("FarRidge",      44.0,  78.0, -60.00, 40.00,  3.50, 12.00, "grass"),
    ],
    # --- Y 방향 사면(_ybank, rotX 슬래브) : (name, x0,x1, y_hi,z_hi, y_lo,z_lo,
    #     thick, mtl). +Y 가 높고 −Y 로 하강.
    ybanks=[
        # 북측 공원 사면 (경사 30.0°) — 옹벽 상단(y2.60,z0) → 능선(y15,z7.16)
        ("NorthBank", -40.0, 44.0, 15.00, 7.16, 2.60, 0.00, 9.00, "grass"),
        # 남측 무방호 사면 (경사 30.1°) — 트레일 어깨(y−1.6,z0) → 하부(y−13)
        ("SouthBankCap", -40.0, -1.5, -1.60, 0.00, -13.00, -6.62, 0.50,
         "grass"),
        # [v6 ②(b)] 몸체 재질 rock(조적) → rockface(무줄눈 자연암).
        #   이 슬래브의 +X 끝면(x=−1.5, y −1.6..−13)이 하부 공원으로 떨어지는
        #   **자연 절개면**이며 `from_below` 좌반부를 채운다. 조적이면 성벽.
        ("SouthBankBody", -40.0, -1.5, -1.60, -0.50, -13.00, -7.12, 7.50,
         "rockface"),
    ],
    # --- [v6] 옹벽 갓돌(코핑) 밴드 : (name, x0, x1, y0, y1, z_top, thick) ---
    #     벽면보다 0.08 m 내밀어 상단에 그림자선을 만든다(토목 시설물 판독).
    #   (머리 옹벽 상단은 진입 데크가 덮으므로 갓돌 없음 — 관통 회피)
    copings=[("BankW", -40.0, 5.20, 1.41, 2.60, 0.02, 0.18),
             ("BankE", 5.20, 44.0, 2.37, 2.60, 0.02, 0.18),
             ("Tier", 5.20, 44.0, 1.37, 2.45, -3.28, 0.16)],
    # --- [v6] 소단 식재 밴드 : (x0, x1) — 소단 상면(z −3.30) 위 관목 띠 ---
    berm_hedges=[(5.6, 15.5), (19.0, 29.0), (33.0, 43.4)],
    berm=dict(y0=1.62, y1=2.34, h=0.85, base_z=-3.30),

    # --- 낙엽 밴드 : 상단 2단 에지 가림(플라이트0 디딤판 1·2) + 지면 퇴적 ---
    leaf=dict(thick=0.02, proud=0.012, over=0.045),
    # [v6 C-7] 지면 낙엽 패치 : 1매 사각 데칼 → 회전·크기 지터 3매 중첩
    leaf_patch=dict(seed=1007, subs=3, scale=(0.55, 0.90), off=0.42, rz=32.0),
    leaf_ground_patches=[(-3.2, -0.9, 1.6, 1.1, "trail"),
                         (-5.6, 0.7, 1.4, 1.0, "trail"),
                         (1.4, -3.4, 2.2, 1.6, "lower"),
                         (5.0, -1.9, 2.0, 1.5, "lower")],

    # --- 드레싱 ---
    # 수목 10 (cx, cy, zone, trunk_h) — zone: north/south/lower/trail
    trees=[(-6.0, 5.5, "north", 3.6), (0.5, 8.0, "north", 4.0),
           (7.0, 6.0, "north", 3.4), (13.0, 9.5, "north", 3.8),
           (-14.0, 4.5, "north", 3.2), (-20.0, 7.5, "north", 3.6),
           (-9.0, -7.5, "south", 3.0), (-17.0, -10.0, "south", 3.4),
           (9.0, -9.0, "lower", 3.2), (16.0, -5.0, "lower", 3.6),
           (2.0, -11.5, "lower", 3.0), (21.0, -12.0, "lower", 3.4)],
    tree=dict(trunk_r=0.10),
    # 관목 군락 (눌린 타원체 중첩 — scene04 v5 규약)
    #   [v6] 남측 절개면(x=−1.5) 상단 모서리에 군락 4를 추가해 직선 절단선을
    #        가린다(from_below 좌반부 '성벽' 인상 완화).
    shrubs=[(-4.0, 3.3, "north"), (3.5, 4.0, "north"), (10.0, 3.6, "north"),
            (-12.0, 3.4, "north"), (-6.5, -4.2, "south"),
            (-14.0, -6.0, "south"), (6.0, -4.6, "lower"),
            (12.0, -2.6, "lower"),
            (-2.3, -2.7, "south"), (-2.6, -5.4, "south"),
            (-2.2, -8.2, "south"), (-2.9, -10.8, "south"),
            # [v7 판정 §7 ㉠] from_below 프레임 좌측(yaw −26°)에 공원 관목을
            #   하나 더 세워 데크를 식생으로 감싼다. 시선 회랑(카메라→데크)은
            #   x 3.5 대역이라 침범 없음 — SMOKE [v7 미장센]이 검산.
            (0.5, -5.5, "lower")],
    shrub=dict(embed=0.25,
               blobs=((0.00, 0.00, 0.75, 0.60, 0.35),
                      (0.54, 0.41, 0.51, 0.43, 0.26),
                      (-0.45, -0.37, 0.56, 0.39, 0.29))),
    # 목재 이정표 (기둥 + 방향판 2 + 기둥 캡)
    #   [v6] 구 사양(0.90×0.16 판 2매 @1.55/1.80)은 원거리에서 **피크닉 테이블**
    #   로 읽혔다 → 판을 얇고 짧게(0.72×0.11), 높이를 벌리고(1.72/1.98) 상단에
    #   캡을 씌워 '기둥형 이정표' 실루엣을 만든다.
    #   [v7 판정 §7 ③] 0.72×0.11 두 판이 여전히 "상판 넓고 낮은 피크닉 테이블"
    #   로 읽혔다 → 판을 **0.58×0.09** 로 더 줄이고, 두 판을 2.06/1.80 으로
    #   올려 **기둥 노출을 1.80 m(전고의 79 %)** 로 키운다. 기둥은 0.065→0.080
    #   으로 굵혀 원거리에서 '기둥형' 실루엣이 먼저 읽히게 한다.
    signpost=dict(cx=-3.6, cy=1.00, post_r=0.080, post_h=2.26,
                  arm=(0.58, 0.05, 0.09), arm_off=0.34,
                  arms=((2.06, 15.0), (1.80, 195.0)),
                  cap=(0.20, 0.20, 0.07)),
    # 벤치 1 (상부 트레일)
    bench=dict(cx=-6.5, cy=0.90, yaw=180.0),
    # 쉼터 정자 (하부 산책로). [v7] from_below 가 (5.2,−10.8)→(2.4,−0.6) 로
    #   미러됐어도 정자(중심 11.5,−6.0)는 yaw 68° 로 화각 밖 — 시선 무간섭 유지.
    pergola=dict(x0=10.0, x1=13.0, y0=-7.5, y1=-4.5, z_roof=-4.20, post_r=0.10,
                 roof_t=0.16),
    # [v5.2 사용자] 임의 경고 팻말 제거 — 계단주의 표지(PARAMS['sign']) 삭제.
    # 원경 폐쇄 : 하부 공원 너머 숲 밴드 + 상부 능선 수목
    far_hedges=[dict(x0=-40.0, x1=6.0, y0=-40.0, y1=-37.0, h=4.0),
                dict(x0=6.0, x1=44.0, y0=-40.0, y1=-37.0, h=4.0),
                dict(x0=40.0, x1=43.0, y0=-33.0, y1=1.40, h=4.0)],
    # [v6 C-4] 원경 능선(FarRidge 상면 z 3.50) 마루 숲 실루엣 밴드 —
    #   개체 롤리팝 대신 라운드 크라운 띠로 지평을 닫는다.
    #   + 북측 언덕(FarHill 상면 7.16)의 **직선 지평**(판정 ① '무대 배경막')도
    #     마루 밴드로 요철화한다.
    ridge_crest=[dict(x0=46.0, x1=54.0, y0=-58.0, y1=-8.0, h=5.0, base=3.10),
                 dict(x0=49.0, x1=57.0, y0=-10.0, y1=38.0, h=6.0, base=3.10),
                 dict(x0=-40.0, x1=6.0, y0=13.6, y1=17.4, h=5.2, base=6.76),
                 dict(x0=6.0, x1=44.0, y0=13.6, y1=17.4, h=4.6, base=6.76)],
    # (cx, cy, zone) — north = 북측 사면, far = 원경 능선(z 3.5), low = 하부
    hill_trees=[dict(cx=-22.0, cy=20.0, zone="north"),
                dict(cx=-8.0, cy=24.0, zone="north"),
                dict(cx=6.0, cy=19.0, zone="north"),
                dict(cx=20.0, cy=25.0, zone="north"),
                dict(cx=32.0, cy=20.0, zone="north"),
                dict(cx=50.0, cy=-14.0, zone="far"),
                dict(cx=58.0, cy=2.0, zone="far"),
                dict(cx=52.0, cy=16.0, zone="far"),
                dict(cx=62.0, cy=-28.0, zone="far"),
                dict(cx=-14.0, cy=-38.5, zone="low"),
                dict(cx=10.0, cy=-38.5, zone="low"),
                dict(cx=28.0, cy=-38.5, zone="low")],

    # --- 재질 ---
    material=dict(
        # [v6] rock_wall 3.0→0.9(성곽 조적 → 발파석 사석) · dirt 3.0→1.1
        #      (confetti 채도) · leaf 1.8→1.05 · rock_face(자연 절개면) 추가
        #      grass 4.0→2.6(사면 '퀼팅 무늬 반복' 완화)
        scale=dict(wood_dark=1.0, rock_wall=0.9, rock_face=2.2, grass=1.4,
                   leaf_ground=1.05, dirt_park=1.1, concrete_wall=2.4),
        deck_tint=(1.00, 0.96, 0.90),          # 데크 목판(약간 바랜 톤)
        stringer_tint=(0.72, 0.70, 0.66),      # 스트링거·기둥(어둡게)
        grass_tint=(0.55, 0.68, 0.42),
        leaf_tint=(0.88, 0.85, 0.80),
        dirt_tint=(0.78, 0.76, 0.72),          # [v6] 채도·명도 하향(색종이 방지)
        rock_tint=(0.82, 0.82, 0.80),          # [v6] 사석 회색화(유럽 성벽 톤 제거)
        rockface_tint=(0.80, 0.80, 0.78),
        coping_tint=(0.78, 0.77, 0.74),
        shrub=(0.030, 0.047, 0.021), shrub_rough=1.0,
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030),
        canopy_rough=1.0,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
    ),   # [v5.2 사용자] 임의 경고 팻말 제거 — sign_back 색상 상수 삭제

    # --- 조명: scene01 noon 검증 상수 + v5 §R5 지정 태양 ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # [v6 판정 §4 ④ + 감독 결정 3항 — 재선정 승인(개방측 순광)]
    #   구 171.5(az 205) → 머리 옹벽이 갈지자 통로 전체를 그림자에 넣음.
    #   신 216.5 = 월드 az 250(태양이 −X·−Y 하늘, 그림자 az 70).
    #   개방측(−Y 하부 공원)에서 직사광이 통로로 들어온다. 검산은 독스트링 ①.
    SUN_AZ_OFFSET=216.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene10")

ASSET_ROLES = ["wood_dark", "rock_wall", "rock_face", "concrete_wall",
               "grass", "leaf_ground", "dirt_park",
               "hdri", "mdl"]     # [v5.2 사용자] 임의 경고 팻말 제거

DECK_BOT = -6.60                   # 데크 최하단(참3 상면 = 플라이트3 끝)
GROUND_Z = -6.62                   # 하부 산책로 지면 상면(데크보다 2 cm 아래)
TRAIL_Z = 0.0                      # 상부 둘레길
HEAD_X = -1.5                      # 옹벽 머리 = 상부 플레이트 끝
FAR_RIDGE_Z = 3.50                 # 원경 능선 상면
NORTH_TAN = math.tan(math.radians(30.0))
SOUTH_SLOPE = 6.62 / 11.40         # 남측 사면 기울기(= tan 30.14°)


# ===========================================================================
# [D] 플라이트 배치 사전계산 (부팅 불필요)
# ===========================================================================
def compute_flights():
    fl = PARAMS["flights"]
    run = fl["steps"] * fl["tread"]             # 3.00
    fdrop = fl["steps"] * fl["riser"]           # 1.65
    land = PARAMS["landing"]["size"]            # 1.40
    seq = []
    x_top, z_top = 0.0, float(fl["z_top"])
    for k in range(fl["n"]):
        even = (k % 2 == 0)
        rot = 180.0 * (k % 2)
        z_bot = z_top - fdrop
        if even:
            x_bot = x_top + run
            lx0, lx1 = x_bot, x_bot + land      # 참은 진행 방향 앞으로 돌출
        else:
            x_bot = x_top - run
            lx0, lx1 = x_bot - land, x_bot
        seq.append(dict(k=k, x_top=x_top, z_top=z_top, x_bot=x_bot,
                        z_bot=z_bot, rot=rot, even=even, lx0=lx0, lx1=lx1))
        # 다음 플라이트 상단 = 참의 먼 모서리가 아니라 **플라이트 하단 그 자리**
        # (archive_v3/scene10 감사 A-10-2 — 참 밑 매몰 방지)
        x_top, z_top = x_bot, z_bot
    return seq, run, fdrop


SEQ, FLIGHT_RUN, FLIGHT_DROP = compute_flights()
TOTAL_DROP = -SEQ[-1]["z_bot"]                  # 6.60


def band(even):
    """플라이트 폭 대역(월드 y). 짝수 = −Y 대역, 홀수 = +Y 대역."""
    fl = PARAMS["flights"]
    lo, hi = -fl["y_off"] - fl["half_w"], -fl["y_off"] + fl["half_w"]
    return (lo, hi) if even else (-hi, -lo)


# ===========================================================================
# [E] 지형 수학
# ===========================================================================
def north_z(y):
    """북측(+Y) 30° 잔디 사면 상면 z (옹벽 상단 y2.60 = 0)."""
    if y <= 2.60:
        return 0.0
    return min(7.16, (y - 2.60) * NORTH_TAN)


def south_z(y):
    """남측(−Y) 30° 무방호 사면 상면 z (트레일 어깨 y−1.60 = 0)."""
    if y >= -1.60:
        return 0.0
    return max(GROUND_Z, (y + 1.60) * SOUTH_SLOPE)


def ground_z(x, y):
    """드레싱 접지용 지면 z."""
    if y >= 2.60:
        return north_z(y)
    if y >= 1.45:
        return 0.0                     # 측면 옹벽 상단
    if y >= -1.60:
        return TRAIL_Z if x <= HEAD_X else GROUND_Z
    if x <= HEAD_X:
        return south_z(y)
    return GROUND_Z


def _zone_z(x, y, zone):
    if zone == "north":
        return north_z(y)
    if zone == "south":
        return south_z(y)
    if zone in ("lower", "low"):
        return GROUND_Z
    if zone == "trail":
        return TRAIL_Z
    if zone == "far":
        return FAR_RIDGE_Z
    return ground_z(x, y)


# ===========================================================================
# [F] 데크 기둥 배치 (기둥 하단이 반드시 지면/하부 참에 닿게)
# ===========================================================================
def post_segments():
    """(name, cx, cy, z_lo, z_hi) 리스트 — z_hi 는 지지 대상 슬래브 밑면."""
    ld = PARAMS["landing"]
    ent = PARAMS["entry"]
    hy = PARAMS["post"]["half_y"]
    ins = PARAMS["post"]["inset"]
    t = ld["thick"]
    segs = []
    # 참별 지지 : 참 슬래브 밑면(z_bot − thick)까지, 하단은 지면 또는 아래 참 상면
    for f in SEQ:
        cols = [f["lx0"] + ins, f["lx1"] - ins]
        for ci, cx in enumerate(cols):
            for tag, sgn in (("P", 1.0), ("N", -1.0)):
                z_hi = f["z_bot"] - t
                # 아래에 같은 x 대역의 참이 또 있으면 그 상면에서 시작
                below = [g["z_bot"] for g in SEQ
                         if g["k"] > f["k"] and abs(g["lx0"] - f["lx0"]) < 1e-6]
                z_lo = max(below) if below else GROUND_Z
                if z_hi - z_lo > 0.05:
                    segs.append((f"L{f['k']}_C{ci}_{tag}", cx, sgn * hy,
                                 z_lo, z_hi))
    # 진입 데크 +X 끝 기둥 (아래 참1 상면 −3.30 에서 기립)
    z_hi = ent["top"] - ent["thick"]
    z_lo = SEQ[1]["z_bot"]
    for tag, sgn in (("P", 1.0), ("N", -1.0)):
        segs.append((f"Entry_{tag}", ent["x1"] - ins, sgn * hy, z_lo, z_hi))
    return segs


# ===========================================================================
# [G] 카메라 프리셋: grid_views(gy=0.0) + 미장센 5컷
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)          # h{0.3,0.9,1.8} × d{2,5,10}, +X

    l0 = SEQ[0]                          # 참0 (z −1.65, x 3.0..4.4)
    lc = ((l0["lx0"] + l0["lx1"]) / 2.0, 0.0, l0["z_bot"])
    # reversal : 참0 을 남측(개방측)에서 — 위(+X 하강)·아래(−X 반전) 동시.
    #   [v7 판정 §7 ①·㉠] 구 컷(eye 3.70,−3.20,−0.30 / pitch −24°)은 프레임이
    #   조적 옹벽 + 갈색 목구조로만 채워져 "근린공원"이 읽히지 않았다.
    #   → **뒤로 3.6 m 물리고 1.5 m 올려 피치를 −16° 로 세운다**: 프레임 상단
    #   (+2.0° 앙각)이 옹벽 갓돌 너머 **북측 30° 잔디 사면·관목 군락**을 담고,
    #   하단(−34°)에 참0·플라이트0/1 이 그대로 남는다(SMOKE [v7 미장센] 검산).
    views["reversal"] = dict(eye=[6.60, -6.60, 1.20],
                             tgt=[2.90, -0.35, -0.88])
    # through_treads : 개방 라이저 투과 — 디딤판 사이로 아래 플라이트·지면
    views["through_treads"] = dict(eye=[1.5, -2.8, -1.10],
                                   tgt=[1.7, 0.30, -4.20])
    # broken_rail : 참0 외측(x 4.4) 가로대 탈락 구간 클로즈 + 4.95 m 낙차
    #   [v7 판정 §7 ②] 구 시선 135° 는 피사면 법선 315° → lambert +0.273 으로
    #   파손·정상 난간이 같은 어두운 밝기 대역에 놓였다. 남측(개방측)으로
    #   0.7 m 돌려 시선 111.9°(법선 291.9°) → **+0.480**. 프레임 하단(−38.5°)
    #   시선은 참0 아래 수직 공간을 지나 옹벽면 z −4.46 에 착지 → 4.95 m
    #   낙차의 **깊이 자체가 프레임에 남는다**(SMOKE 하단 시선 착지).
    views["broken_rail"] = dict(eye=[5.60, -3.40, -0.30],
                                tgt=[4.35, -0.30, -1.55])
    # leaf_edge : 상단 2단 낙엽 가림 — 진입 로봇 시점 근접
    views["leaf_edge"] = dict(eye=[-1.05, -1.55, 0.55],
                              tgt=[0.80, -0.70, -0.38])
    # from_below : 하부 공원에서 갈지자 전경(참·기둥·낙차 앵커)
    #   [v7 판정 §7 ②·㉡] 구 컷(eye 8.0,−7.5 → tgt 1.8,0)은 시선 방위 129.6° 라
    #   **피사면의 절반이 +X향 절개면·머리 옹벽**(lambert −0.342 = 음영측)이었다
    #   → mean 36.4 · dark 66.3 %. 태양 az 250 에서 순광인 면은 −Y향(0.607)
    #   이므로 **개방측(−Y)으로 미러**해 데크를 정남에서 올려다본다.
    #   시선 105.4° · 피사면 법선 285.4° → lambert +0.526.
    #   피치 +6.6° 는 "하부 공원 잔디·흙길·관목이 하반에, 데크 스택이 상반에"
    #   들어오는 값(전자는 7.5~10.6 m 대역, 후자는 앙각 +18.7°).
    views["from_below"] = dict(eye=[5.20, -10.80, GROUND_Z + 1.55],
                               tgt=[2.40, -0.60, -3.85])
    return views


# ===========================================================================
# [H] SMOKE — 부팅 없는 기하 자기검증
# ===========================================================================
def _grid_obstacles():
    """그리드 카메라(−d, 0, h) 충돌 검산용 AABB [(name,x0,x1,y0,y1,z0,z1)]."""
    sp = PARAMS["signpost"]
    bn = PARAMS["bench"]
    # [v5.2 사용자] 임의 경고 팻말 제거 — Sign AABB 삭제(이정표·벤치만)
    obs = [("SignPost", sp["cx"] - sp["arm"][0], sp["cx"] + sp["arm"][0],
            sp["cy"] - 0.4, sp["cy"] + 0.4, 0.0, sp["post_h"]),
           ("Bench", bn["cx"] - 0.95, bn["cx"] + 0.95, bn["cy"] - 0.25,
            bn["cy"] + 0.25, 0.0, 0.50)]
    for cx, cy, zone, th in PARAMS["trees"]:
        gz = _zone_z(cx, cy, zone)
        obs.append((f"Tree_{len(obs)}", cx - 0.9, cx + 0.9, cy - 0.9, cy + 0.9,
                    gz, gz + th + 1.4))
    for cx, cy, zone in PARAMS["shrubs"]:
        gz = _zone_z(cx, cy, zone)
        obs.append((f"Shrub_{len(obs)}", cx - 1.3, cx + 1.3, cy - 1.1,
                    cy + 1.1, gz, gz + 0.65))
    return obs


def _smoke_report():
    P = PARAMS
    fl = P["flights"]
    ld = P["landing"]
    ent = P["entry"]
    print("=" * 74)
    print("scene10_park_deck_switchback (v5 R5) — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 74)
    print(f"  플라이트 {fl['n']} × {fl['steps']}단 · riser {fl['riser']} / "
          f"tread {fl['tread']} · 폭 {2*fl['half_w']:.2f} m")
    print(f"  총 낙차 {TOTAL_DROP:.2f} m (≥0.3 → "
          f"{'OK' if TOTAL_DROP >= 0.3 else 'FAIL'}) · "
          f"플라이트 경사 {math.degrees(math.atan2(fl['riser'], fl['tread'])):.1f}°"
          f" · 평면 x [{SEQ[1]['lx0']:.2f}, {SEQ[0]['lx1']:.2f}]")

    # ── 플라이트·참 표 ──
    print("\n  [표] 플라이트/참 (월드 좌표)")
    print(f"    {'k':>2} {'rot':>4} {'대역 y':>16} {'x_top→x_bot':>14} "
          f"{'z_top→z_bot':>16} {'참 x범위':>14} 참 z")
    for f in SEQ:
        lo, hi = band(f["even"])
        print(f"    {f['k']:2d} {int(f['rot']):4d} [{lo:+6.2f},{hi:+6.2f}] "
              f"{f['x_top']:6.2f}→{f['x_bot']:6.2f} "
              f"{f['z_top']:+7.3f}→{f['z_bot']:+7.3f} "
              f"[{f['lx0']:6.2f},{f['lx1']:6.2f}] {f['z_bot']:+7.3f}")
    lo_e, hi_e = band(True)
    lo_o, hi_o = band(False)
    print(f"    대역 간극 = {lo_o - hi_e:.3f} m (>0 = 두 방향 간섭 0 → "
          f"{'OK' if lo_o > hi_e else 'FAIL'})")
    print(f"    참 y범위 [{ld['y0']:+.2f},{ld['y1']:+.2f}] 이 두 대역을 모두 "
          f"덮는가 → {'OK' if ld['y0'] <= lo_e and ld['y1'] >= hi_o else 'FAIL'}")
    head = 2 * FLIGHT_DROP - 0.29
    print(f"    상·하 플라이트 연직 여유 = 2×{FLIGHT_DROP:.2f} − 0.29 = "
          f"{head:.2f} m ({'OK' if head > 2.0 else 'CHECK'})")

    # ── 보행 연속성 전수 검사 ──
    print("\n  [표] 보행 연속성 (구간 → 다음 구간, n단 분할 단차)")
    links = [("상부 트레일", TRAIL_Z, "진입 데크", ent["top"], 1)]
    prev_n, prev_z = "진입 데크", ent["top"]
    for f in SEQ:
        z1 = f["z_top"] - fl["riser"]
        links.append((prev_n, prev_z, f"플라이트{f['k']} 1단", z1, 1))
        links.append((f"플라이트{f['k']} 1단", z1,
                      f"플라이트{f['k']} {fl['steps']}단", f["z_bot"],
                      fl["steps"] - 1))
        links.append((f"플라이트{f['k']} {fl['steps']}단", f["z_bot"],
                      f"참{f['k']}", f["z_bot"], 1))
        prev_n, prev_z = f"참{f['k']}", f["z_bot"]
    links.append((prev_n, prev_z, "하부 산책로", GROUND_Z, 1))
    worst = 0.0
    for n0, z0, n1, z1, ns in links:
        d = (z0 - z1) / float(ns)
        worst = max(worst, abs(d))
        flag = "OK" if abs(d) <= fl["riser"] + 1e-6 else "CHECK"
        print(f"    {n0:<15} {z0:+7.3f} → {n1:<15} {z1:+7.3f} "
              f"×{ns:2d}단  단차 {d:+6.3f}  {flag}")
    print(f"    최대 단일 단차 {worst:.3f} m (riser {fl['riser']} 이하 = "
          f"{'OK' if worst <= fl['riser'] + 1e-6 else 'CHECK'})")
    gap = SEQ[-1]["z_bot"] - GROUND_Z
    print(f"    참3 상면 {SEQ[-1]['z_bot']:+.3f} vs 하부 지면 {GROUND_Z:+.3f} "
          f"→ 프라우드 {gap:+.3f} m "
          f"({'OK (동일평면 아님·보행 무해)' if 0.0 < gap <= 0.05 else 'CHECK'})")

    # ── 지면 플레이트 / 사면 표 ──
    print("\n  [표] 축정렬 지면 플레이트")
    print(f"    {'이름':15s} {'x범위':>16s} {'y범위':>16s} {'상면z':>7s} 두께")
    for nm, x0, x1, y0, y1, zt, th, _m in P["plates"]:
        print(f"    {nm:15s} [{x0:7.1f},{x1:7.1f}] [{y0:7.2f},{y1:7.2f}] "
              f"{zt:7.3f} {th:5.2f}")
    print("  [표] Y 방향 사면(_ybank, rotX)")
    for nm, x0, x1, yh, zh, yl, zl, th, _m in P["ybanks"]:
        ang = math.degrees(math.atan2(zh - zl, yh - yl))
        print(f"    {nm:15s} y {yh:+6.2f}(z{zh:+6.2f}) → {yl:+6.2f}"
              f"(z{zl:+6.2f})  {ang:5.1f}° 두께 {th:.2f}")
    print("    상부 트레일 플레이트는 x=%.1f 에서 끊김 → 계단 공동(x %.1f..%.1f) "
          "위 연속 평면 없음 (체크리스트 ③ OK)"
          % (HEAD_X, SEQ[1]["lx0"], SEQ[0]["lx1"]))
    for y in (4.0, 2.0, 0.0, -3.0, -8.0, -14.0):
        print(f"    ground_z(x=−5, y={y:+6.1f}) = {ground_z(-5.0, y):+6.3f} · "
              f"(x=+2, y={y:+6.1f}) = {ground_z(2.0, y):+6.3f}")
    print(f"    남측 무방호: 트레일 어깨(y−1.60) 기준 y−5.6 에서 "
          f"{-south_z(-5.6):.2f} m 하강 (브리프 2~3 m 대역)")

    # ── 데크 기둥 접지 표 ──
    print("\n  [표] 데크 기둥 접지 (하단 z / 상단 z / 길이)")
    for nm, cx, cy, z_lo, z_hi in post_segments():
        base = "지면" if abs(z_lo - GROUND_Z) < 1e-6 else "하부 참"
        print(f"    {nm:<12} ({cx:6.2f},{cy:+5.2f}) {z_lo:+7.3f} → "
              f"{z_hi:+7.3f}  L={z_hi - z_lo:5.3f}  하단={base}")

    # ── 파손 난간 ──
    br = P["rail"]["broken_landing"]
    f = SEQ[br]
    print(f"\n  [파손 난간] 참{br} 외측 에지 x={f['lx1'] if f['even'] else f['lx0']:.2f}"
          f" z={f['z_bot']:+.2f} — 가로대 2본 탈락 · 포스트 잔존")
    print(f"    개방 낙차 = {f['z_bot'] - GROUND_Z:.2f} m "
          f"(≥0.3 → {'OK' if f['z_bot'] - GROUND_Z >= 0.3 else 'FAIL'})")

    # ── [v6] 태양 재선정 검산 : 면별 lambert + 통로 직사광 도달 ──
    az = 33.5 + float(P["SUN_AZ_OFFSET"])
    el = math.radians(float(P["light"]["noon_sun_elev"]))
    ux, uy = math.cos(math.radians(az)), math.sin(math.radians(az))
    lx, ly, lz = ux * math.cos(el), uy * math.cos(el), math.sin(el)
    hv = math.cos(el) / math.sin(el)          # 1 m 상승당 수평 이동
    print(f"\n  [v6 태양] offset {P['SUN_AZ_OFFSET']:.1f} → 월드 az {az:.1f}° "
          f"(그림자 az {az - 180:.1f}°) · 고도 {math.degrees(el):.2f}°")
    for nm, N in (("−Y향(데크 측면·북측 옹벽면)", (0, -1, 0)),
                  ("−X향(그리드 정면·원경 능선)", (-1, 0, 0)),
                  ("상면(트레일·참·디딤판)", (0, 0, 1)),
                  ("+X향(머리 옹벽 노출면)", (1, 0, 0))):
        d = N[0] * lx + N[1] * ly + N[2] * lz
        print(f"    {nm:<26} lambert {d:+.3f} "
              f"{'순광' if d > 0.15 else ('터미네이터' if d > 0 else '음영')}")
    print("    [광선 역추적] 통로 대표점 → 태양 방향으로 z=0 까지 상승했을 때의 "
          "평면 위치 (x<−1.5 이면 머리 옹벽/남측 사면에 차폐)")
    for nm, px, py, pz in (("플라이트0 중단", 1.5, -0.7, -0.83),
                           ("참0 상면", 3.70, -0.70, -1.65),
                           ("플라이트2 중단", 1.7, -0.7, -4.24),
                           ("참2 상면", 3.70, -0.70, -4.95),
                           ("참3 상면(최하부)", -0.70, 0.70, -6.60)):
        rise = -pz
        ex, ey = px + ux * hv * rise, py + uy * hv * rise   # 태양 쪽으로 역추적
        ok = ex >= HEAD_X            # 보수적 판정(x=−1.5 평면을 넘으면 차폐 의심)
        print(f"    {nm:<16} ({px:+.2f},{py:+.2f},{pz:+.2f}) → "
              f"({ex:+.2f},{ey:+.2f}, 0.00)  "
              f"{'직사광 도달' if ok else '옹벽 그늘(설계상 허용)'}")

    # ── [v6] 옹벽 2단화 정합 검산 ──
    tiers = {nm: (x0, x1, y0, y1, zt, th)
             for nm, x0, x1, y0, y1, zt, th, _m in P["plates"]
             if nm in ("BankCut", "EastTierLow", "EastTierUp")}
    bc, tl, tu = tiers["BankCut"], tiers["EastTierLow"], tiers["EastTierUp"]
    print(f"\n  [v6 옹벽] 단일벽 x ≤ {bc[1]:.2f}(데크 구간 — 위험 기하 불변) / "
          f"동측 2단 x ≥ {tl[0]:.2f}")
    print(f"    하단벽 상면(소단) z {tl[4]:+.2f} · 노출고 "
          f"{tl[4] - GROUND_Z:.2f} m · 상단벽 노출고 {0.0 - tl[4]:.2f} m "
          f"(구 단일 {0.0 - GROUND_Z:.2f} m → "
          f"{'OK' if max(tl[4] - GROUND_Z, -tl[4]) < 4.0 else 'CHECK'})")
    print(f"    소단 폭 {tu[2] - tl[2]:.2f} m · 접합 연속(하단벽 상면 y "
          f"{tl[2]:.2f}~{tl[3]:.2f}, 상단벽 저면 z {tu[4] - tu[5]:+.2f} ≤ "
          f"{tl[4]:+.2f} → "
          f"{'OK' if tu[4] - tu[5] <= tl[4] + 1e-9 else 'FAIL'})")
    bm = P["berm"]
    print(f"    소단 식재 {len(P['berm_hedges'])}띠 y[{bm['y0']:.2f},"
          f"{bm['y1']:.2f}] ⊂ 소단 y[{tl[2]:.2f},{tl[3]:.2f}] → "
          f"{'OK' if bm['y0'] >= tl[2] and bm['y1'] <= tl[3] else 'FAIL'}")

    # ── 그리드 카메라 충돌 검산 ──
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
    print(f"    충돌 = {hit_any} (False 여야 함) · 카메라 접지면 z=0 "
          f"(UpperTrail x −40..{HEAD_X}, y −1.60..1.45) 내부 OK")

    print("\n  [카메라] 미장센")
    v = build_views()
    for vn in ("reversal", "through_treads", "broken_rail", "leaf_edge",
               "from_below"):
        vv = v[vn]
        print(f"    {vn:<15} eye={['%.2f' % e for e in vv['eye']]} "
              f"tgt={['%.2f' % t for t in vv['tgt']]}")

    # ── [v7] 미장센 프레이밍 : 공원 앵커가 프레임에 들어오는가 + 컷별 순광 ──
    #   판정 §7 ① "미장센 4컷 어디에도 공원 신호(잔디·관목·수목·이용자 시설)가
    #   들어오지 않는다 — 문제는 기하가 아니라 프레이밍". 재조준을 **좌표로
    #   검증**하기 위해 화각(수평 반각 30° · 수직 반각 18°) 안에 들어오는 공원
    #   앵커를 열거하고, 동시에 컷별 피사면 lambert 를 붙인다(judge v7 교훈:
    #   "재조준은 프레임 점유율로 검산되지만 조도는 검산되지 않는다").
    anchors = []
    for cx, cy, zone in P["shrubs"]:
        if zone in ("lower", "south"):
            anchors.append((f"관목({cx:+.1f},{cy:+.1f})", cx, cy,
                            _zone_z(cx, cy, zone) + 0.55))
    for cx, cy, zone, th in P["trees"]:
        anchors.append((f"수목({cx:+.1f},{cy:+.1f})", cx, cy,
                        _zone_z(cx, cy, zone) + th + 0.7))
    pg = P["pergola"]
    anchors.append(("쉼터 정자", (pg["x0"] + pg["x1"]) / 2.0,
                    (pg["y0"] + pg["y1"]) / 2.0, pg["z_roof"]))
    for yy in (4.0, 7.0, 11.0):
        anchors.append((f"북측 잔디사면 y{yy:.0f}", 3.0, yy, north_z(yy)))
    bm = P["berm"]
    for x0b, x1b in P["berm_hedges"][:1]:
        anchors.append(("소단 식재띠", (x0b + x1b) / 2.0,
                        (bm["y0"] + bm["y1"]) / 2.0,
                        bm["base_z"] + bm["h"] / 2.0))
    sp, bn = P["signpost"], P["bench"]
    anchors.append(("이정표", sp["cx"], sp["cy"], sp["post_h"] / 2.0))
    anchors.append(("벤치", bn["cx"], bn["cy"], 0.25))

    azd = 33.5 + float(P["SUN_AZ_OFFSET"])
    el2 = math.radians(float(P["light"]["noon_sun_elev"]))
    print("\n  [v7 미장센] 컷별 피사면 lambert + 프레임 내 공원 앵커")
    for vn in ("reversal", "through_treads", "broken_rail", "leaf_edge",
               "from_below"):
        ex, ey, ez = v[vn]["eye"]
        tx, ty, tz = v[vn]["tgt"]
        fx, fy = tx - ex, ty - ey
        dh = math.hypot(fx, fy)
        ux, uy = fx / dh, fy / dh
        rx, ry = uy, -ux
        gaze = math.degrees(math.atan2(fy, fx)) % 360.0
        nrm = (gaze + 180.0) % 360.0
        lam = math.cos(math.radians(nrm - azd)) * math.cos(el2)
        pit = math.degrees(math.atan2(tz - ez, dh))
        seen = []
        for nm, ax, ay, az_ in anchors:
            vx, vy, vz = ax - ex, ay - ey, az_ - ez
            dep = vx * ux + vy * uy
            if dep <= 0.5:
                continue
            yaw = math.degrees(math.atan2(vx * rx + vy * ry, dep))
            elv = math.degrees(math.atan2(vz, math.hypot(vx, vy)))
            if abs(yaw) <= 30.0 and abs(elv - pit) <= 18.0:
                seen.append(f"{nm}[yaw{yaw:+.0f}°]")
        # 프레임 하단 중앙 시선이 닿는 지면 (하반 = 잔디/흙길인가)
        pr = math.radians(pit - 18.0)
        hit = None
        for i in range(1, 401):
            s = i * 0.25
            px, py = ex + ux * s * math.cos(pr), ey + uy * s * math.cos(pr)
            pz = ez + s * math.sin(pr)
            if pz <= ground_z(px, py):
                zone = ("하부공원 흙길" if (px > HEAD_X and -4.4 <= py <= -2.6)
                        else ("하부공원 잔디" if (px > HEAD_X and py < 1.45)
                              else "상부/사면"))
                hit = f"({px:+.1f},{py:+.1f}) {zone}"
                break
        print(f"    {vn:<15} 시선 {gaze:5.1f}° · 법선 {nrm:5.1f}° · lambert "
              f"{lam:+.3f} {'순광' if lam > 0.15 else '역광/터미네이터'} · "
              f"피치 {pit:+5.1f}°")
        print(f"      하단 시선 착지 : {hit if hit else '지면 미교차(하늘)'}")
        # 판정 §7 ①은 "**전** 미장센 컷에 공원 신호가 없다"는 지적이었다.
        #   재조준 대상(from_below·reversal)은 앵커를 반드시 물어야 하고,
        #   클로즈업 컷(through_treads·broken_rail)은 면제 — 대신 lambert 와
        #   하단 착지로 조도·낙차를 검산한다.
        need = vn in ("from_below", "reversal")
        verdict = ("OK" if seen else "FAIL ← 판정 §7 ① 재발") if need \
            else ("OK" if seen else "면제(클로즈업 — lambert·하단 착지로 판정)")
        print(f"      공원 앵커 {len(seen)}개 [{verdict}] : "
              f"{', '.join(seen) if seen else '-'}")
    print("=" * 74)


# ===========================================================================
# [I] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드      — 낙엽 덮인 상단 2단이 '평탄한 데크 진입'으로 읽히나
 2. through_treads   — 라이저 부재로 디딤판 사이 아래 플라이트·지면이 투시되나
 3. reversal         — 참0에서 두 방향 플라이트(±X, 병렬 Y 대역)가 한 프레임에
 4. broken_rail      — 가로대 탈락·포스트 잔존 + 4.97 m 개방 낙차가 명확한가
 5. leaf_edge        — 낙엽 밴드가 단코를 물고 덮어 절단선을 지우나
 6. from_below       — 데크 기둥 접지·참 스택이 낙차 앵커로 읽히나
 7. 남측 사면        — 트레일 어깨 밖 30° 무방호 하강이 grazing 시 소실되나
 8. 지평 폐쇄        — 북측 언덕·원경 능선 마루 숲 밴드가 직선 지평을 깨는가
 9. cue 토글         — railing/tactile/nosing ON/OFF 시 위험 기하 불변인가
10. [v6] 태양        — from_below·through_treads 에 직사광이 들어왔나(암부 사망 해소)
11. [v6] 옹벽        — 사석 스케일 + 동측 2단(소단 식재)로 '공원 절토면'이 되나
12. [v6] 난간        — 세로살이 들어가 '가설 사다리틀'이 아니라 데크 난간인가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene10")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene10"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl, rotY=rotY,
                               collider=col)

    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        M = {}
        M["deck"] = tex("wood_dark", "/World/Looks/Deck", sca["wood_dark"],
                        tint=mp["deck_tint"])
        M["stringer"] = tex("wood_dark", "/World/Looks/Stringer",
                            sca["wood_dark"] * 1.6, tint=mp["stringer_tint"])
        # [v6] 인공 옹벽(조적, 사석 스케일) / 자연 절개면(무줄눈) / 갓돌(콘크리트)
        M["rock"] = tex("rock_wall", "/World/Looks/Rock", sca["rock_wall"],
                        tint=mp["rock_tint"])
        M["rockface"] = tex("rock_face", "/World/Looks/RockFace",
                            sca["rock_face"], tint=mp["rockface_tint"])
        M["coping"] = tex("concrete_wall", "/World/Looks/Coping",
                          sca["concrete_wall"], tint=mp["coping_tint"])
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["leaf"] = tex("leaf_ground", "/World/Looks/Leaf",
                        sca["leaf_ground"], tint=mp["leaf_tint"])
        M["dirt"] = tex("dirt_park", "/World/Looks/Dirt", sca["dirt_park"],
                        tint=mp["dirt_tint"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["shrub"] = sc.make_pbr(stage, "/World/Looks/Shrub",
                                 diffuse_color=mp["shrub"],
                                 roughness_const=mp["shrub_rough"],
                                 specular_level=0.0)
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        # [v5.2 사용자] 임의 경고 팻말 제거 — 사인 패널·배킹 재질 생성 삭제.
        M["tread"] = M["deck"] if cfg["cue_material_break"] else M["stringer"]
        return M

    # -------------------------------------------------------------------
    # 지형 : 축정렬 플레이트 + Y 방향 사면(rotX 슬래브)
    # -------------------------------------------------------------------
    def ybank(path, x0, x1, y_hi, z_hi, y_lo, z_lo, thick, mtl):
        """+Y(높음) → −Y(낮음) 로 기우는 사면 슬래브. build_slope 의 Y 대응물.
        rotX(θ): 로컬 +Y → (0, cosθ, sinθ) 이므로 θ>0 이면 −Y 로 하강.
        로컬 −Z(두께 방향) → 월드 (0, sinθ, −cosθ)."""
        dy, dz = (y_hi - y_lo), (z_hi - z_lo)
        ang = math.atan2(dz, dy)
        L = math.hypot(dy, dz)
        cy = (y_hi + y_lo) / 2.0 + (thick / 2.0) * math.sin(ang)
        cz = (z_hi + z_lo) / 2.0 - (thick / 2.0) * math.cos(ang)
        return sc._oriented_box(stage, path, ((x0 + x1) / 2.0, cy, cz),
                                (x1 - x0, L, thick), mtl, collider=True,
                                rotx=math.degrees(ang))

    def build_terrain(M):
        for nm, x0, x1, y0, y1, zt, th, mk in PARAMS["plates"]:
            BOX(f"{ROOT}/Plate_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zt - th / 2.0),
                (x1 - x0, y1 - y0, th), M[mk], col=True)
        for nm, x0, x1, yh, zh, yl, zl, th, mk in PARAMS["ybanks"]:
            ybank(f"{ROOT}/Bank_{nm}", x0, x1, yh, zh, yl, zl, th, M[mk])
        # [v6] 옹벽 갓돌(코핑) — 벽면보다 내밀어 상단 그림자선을 만든다
        for nm, x0, x1, y0, y1, zt, th in PARAMS["copings"]:
            BOX(f"{ROOT}/Coping_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zt - th / 2.0),
                (x1 - x0, y1 - y0, th), M["coping"], col=True)
        # [v6] 동측 2단 옹벽 소단(z −3.30) 식재 밴드 — '성곽' 인상 해소
        bm = PARAMS["berm"]
        for i, (x0, x1) in enumerate(PARAMS["berm_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/BermHedge_{i}", x0, bm["y0"],
                           x1, bm["y1"], bm["h"], base_z=bm["base_z"])

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 : 계단 구간을 z=0 평판 데크로."""
        ld = PARAMS["landing"]
        x0, x1 = SEQ[1]["lx0"], SEQ[0]["lx1"]
        BOX(f"{ROOT}/FlatDeck",
            ((x0 + x1) / 2.0, (ld["y0"] + ld["y1"]) / 2.0, -0.06),
            (x1 - x0, ld["y1"] - ld["y0"], 0.12), M["deck"], col=True)

    # -------------------------------------------------------------------
    # 갈지자 데크 계단
    # -------------------------------------------------------------------
    def deck_rail(prefix, x0, x1, y0, y1, z_top, broken=False):
        """축정렬 난간 1선(포스트 + 상·중 가로대 + **세로 살**).
        broken=True → 가로대·세로살 탈락, 포스트만 잔존(참0 파손 개소).
        위험 기하는 불변."""
        r = PARAMS["rail"]
        horiz = abs(x1 - x0) >= abs(y1 - y0)
        L = math.hypot(x1 - x0, y1 - y0)
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        if not broken:
            for tag, hh, rr in (("Top", r["h"], r["bar_t"]),
                                ("Mid", r["mid"], r["bar_t"] * 0.7)):
                size = ((L, rr, rr) if horiz else (rr, L, rr))
                BOX(f"{prefix}/Bar{tag}", (cx, cy, z_top + hh), size,
                    M["rail"])
            # [v6] 세로 살 : 공원 데크 난간 표준. 상부 가로대 하면까지.
            nb = max(1, int(round(L / r["bal_step"])) - 1)
            for i in range(nb):
                t = (i + 1) / float(nb + 1)
                bx = x0 + (x1 - x0) * t
                by = y0 + (y1 - y0) * t
                CYL(f"{prefix}/Bal_{i}", (bx, by, z_top + r["bal_top"] / 2.0),
                    r["bal_r"], r["bal_top"], M["rail"])
        n = max(2, int(round(L / r["spacing"])) + 1)
        for i in range(n):
            t = i / float(n - 1)
            px = x0 + (x1 - x0) * t
            py = y0 + (y1 - y0) * t
            CYL(f"{prefix}/Post_{i}", (px, py, z_top + r["post_h"] / 2.0),
                r["post_r"], r["post_h"], M["rail"])

    def build_deck(M):
        fl = PARAMS["flights"]
        ld = PARAMS["landing"]
        ent = PARAMS["entry"]
        r = PARAMS["rail"]
        lcy = (ld["y0"] + ld["y1"]) / 2.0
        lsy = ld["y1"] - ld["y0"]

        def _flight_rails(grp, f, gy0, gy1):
            """플라이트 양측 난간 — rot_group **내부**(로컬 +X 하강 규약).
            대역 에지에서 0.04 안쪽으로 물려 세운다: 중앙(짝·홀 대역 경계)에서
            두 플라이트의 내측 포스트(r 0.05)가 y=−0.05 / +0.05 로 접할 뿐
            상호 관통하지 않는다."""
            def gfn(x, _xt=f["x_top"], _zt=f["z_top"]):
                if x <= _xt:
                    return _zt
                i = min(int((x - _xt) / fl["tread"]) + 1, fl["steps"])
                return _zt - i * fl["riser"]

            for tag, y in (("N", gy0 + 0.04), ("P", gy1 - 0.04)):
                sc.build_railing_line(
                    stage, f"{grp}/Rail_{tag}", y, f["x_top"], f["x_top"],
                    FLIGHT_RUN, FLIGHT_DROP, gfn, M["rail"], rail_h=r["h"],
                    post_r=r["post_r"], spacing=r["spacing"],
                    rail_r=r["bar_t"] / 2.0,
                    # 이 씬은 **아래에 자체 세로살 루프**가 있다. 공통 간살을
                    # 켜면 실린더가 이중 생성되어 관통한다(레드팀 적발: 48쌍).
                    baluster_r=0.0)
                # [v6] 경사 난간 세로 살 : 디딤면 → 상부 가로대. 세로살이 없으면
                #      경사 레일 2본이 이웃 프레임 뒤로 겹쳐 '사선 브레이스'로
                #      오독된다(판정 §4 ⑤ 가설 사다리틀).
                top0 = f["z_top"] + r["h"]
                nb = max(1, int(round(FLIGHT_RUN / r["bal_step"])) - 1)
                for i in range(nb):
                    bx = f["x_top"] + FLIGHT_RUN * (i + 1) / float(nb + 1)
                    zr = top0 - FLIGHT_DROP * (bx - f["x_top"]) / FLIGHT_RUN
                    zg = gfn(bx)
                    hh = zr - zg - r["bar_t"] / 2.0
                    if hh > 0.05:
                        CYL(f"{grp}/Bal_{tag}_{i}", (bx, y, zg + hh / 2.0),
                            r["bal_r"], hh, M["rail"])

        # 진입 데크 (옹벽 머리 → 첫 단)
        BOX(f"{ROOT}/EntryDeck",
            ((ent["x0"] + ent["x1"]) / 2.0, lcy, ent["top"] - ent["thick"] / 2.0),
            (ent["x1"] - ent["x0"], lsy, ent["thick"]), M["deck"], col=True)

        for f in SEQ:
            k = f["k"]
            lo, hi = band(True)              # 로컬 대역(짝수 기준) — rot180 이 미러
            grp = sc.build_rot_group(stage, f"{ROOT}/FlightGrp_{k}",
                                     (f["x_top"], 0.0), f["rot"])
            sc.build_open_riser_stairs(
                stage, f"{grp}/Flight", f["x_top"], lo, hi, fl["riser"],
                fl["tread"], fl["steps"], f["z_top"], M["tread"],
                M["stringer"], tread_t=fl["tread_t"], gap=fl["gap"])
            if cfg["cue_railing"]:
                _flight_rails(grp, f, lo, hi)
            # 참 (월드 좌표) — 두 대역을 모두 덮는 슬래브
            BOX(f"{ROOT}/Landing_{k}",
                ((f["lx0"] + f["lx1"]) / 2.0, lcy,
                 f["z_bot"] - ld["thick"] / 2.0),
                (f["lx1"] - f["lx0"], lsy, ld["thick"]), M["deck"], col=True)

        # 데크 기둥 (전부 지면 또는 하부 참에 접지)
        pp = PARAMS["post"]
        for nm, cx, cy, z_lo, z_hi in post_segments():
            h = z_hi - z_lo
            CYL(f"{ROOT}/Post_{nm}", (cx, cy, z_lo + h / 2.0), pp["r"], h,
                M["stringer"], col=True)

        # 참 난간 : 외측 에지 + 양 측면. 참0 외측만 **파손**(가로대 탈락).
        if cfg["cue_railing"]:
            for f in SEQ:
                k = f["k"]
                z = f["z_bot"]
                x_out = f["lx1"] if f["even"] else f["lx0"]
                broken = (k == int(r["broken_landing"]))
                deck_rail(f"{ROOT}/LandRail_{k}_Out", x_out, x_out, ld["y0"],
                          ld["y1"], z, broken=broken)
                for tag, yy in (("N", ld["y0"]), ("P", ld["y1"])):
                    deck_rail(f"{ROOT}/LandRail_{k}_{tag}", f["lx0"], f["lx1"],
                              yy, yy, z)
            # 진입 데크 측면 난간 2
            for tag, yy in (("N", ld["y0"]), ("P", ld["y1"])):
                deck_rail(f"{ROOT}/EntryRail_{tag}", ent["x0"], ent["x1"],
                          yy, yy, ent["top"])

        # 낙엽 밴드 : 플라이트0 상단 2단 에지 가림
        lf = PARAMS["leaf"]
        f0 = SEQ[0]
        blo, bhi = band(True)
        for i in (1, 2):
            xa = f0["x_top"] + (i - 1) * fl["tread"]
            xb = f0["x_top"] + i * fl["tread"]
            zt = f0["z_top"] - i * fl["riser"] + lf["proud"]
            cx = (xa + 0.06 + xb + lf["over"]) / 2.0
            sx = (xb + lf["over"]) - (xa + 0.06)
            BOX(f"{ROOT}/LeafTread_{i}", (cx, (blo + bhi) / 2.0,
                                          zt - lf["thick"] / 2.0),
                (sx, bhi - blo, lf["thick"]), M["leaf"])
        # 지면 낙엽 퇴적 4 — [v6 C-7] 사각 데칼 → 회전 3매 중첩으로 경계 파괴
        lp = PARAMS["leaf_patch"]
        rng = random.Random(int(lp["seed"]))
        for n, (cx, cy, sx, sy, zone) in enumerate(
                PARAMS["leaf_ground_patches"]):
            zt = _zone_z(cx, cy, zone) + lf["proud"]
            for j in range(int(lp["subs"])):
                f = 1.0 if j == 0 else rng.uniform(*lp["scale"])
                ox = 0.0 if j == 0 else rng.uniform(-1.0, 1.0) * lp["off"] * sx
                oy = 0.0 if j == 0 else rng.uniform(-1.0, 1.0) * lp["off"] * sy
                sc._oriented_box(
                    stage, f"{ROOT}/LeafGround_{n}_{j}",
                    (cx + ox, cy + oy, zt - lf["thick"] / 2.0 - j * 0.002),
                    (sx * f, sy * f * rng.uniform(0.85, 1.15), lf["thick"]),
                    M["leaf"], collider=False,
                    rotz=rng.uniform(-lp["rz"], lp["rz"]))

    # -------------------------------------------------------------------
    # 드레싱
    # -------------------------------------------------------------------
    def build_nature(M):
        tr = PARAMS["tree"]
        for n, (cx, cy, zone, th) in enumerate(PARAMS["trees"]):
            gz = _zone_z(cx, cy, zone)
            sc.build_tree(stage, f"{ROOT}/Tree_{n}", cx, cy, gz, M["wood"],
                          M["canopy_a"], M["canopy_b"], trunk_r=tr["trunk_r"],
                          trunk_h=th, stake_r=0.004, stake_h=0.02,
                          stake_off=0.2)
        # [v6] 30° 사면 위 블롭은 중심 z 접지 시 하류측이 ry·tan30 (≈0.35 m) 뜬다
        #      → 블롭 footprint 의 **최저 지면**을 기준으로 접지(부유 구조적 제거).
        sh = PARAMS["shrub"]
        emb = sh["embed"]
        for n, (cx, cy, zone) in enumerate(PARAMS["shrubs"]):
            for j, (dx, dy, rx, ry, rz) in enumerate(sh["blobs"]):
                bx, by = cx + dx, cy + dy
                gz = min(_zone_z(bx, by - ry, zone), _zone_z(bx, by, zone),
                         _zone_z(bx, by + ry, zone))
                sc.add_sphere(stage, f"{ROOT}/Shrub_{n}_{j}",
                              (bx, by, gz + rz * (1.0 - emb)),
                              (rx, ry, rz), M["shrub"])

    def build_props(M):
        # 목재 이정표 (기둥 + 방향판 2 + 캡)
        sp = PARAMS["signpost"]
        CYL(f"{ROOT}/SignPost/Post",
            (sp["cx"], sp["cy"], sp["post_h"] / 2.0), sp["post_r"],
            sp["post_h"], M["wood"], col=True)
        BOX(f"{ROOT}/SignPost/Cap",
            (sp["cx"], sp["cy"], sp["post_h"] + sp["cap"][2] / 2.0),
            sp["cap"], M["wood"])
        for k, (az, yaw) in enumerate(sp["arms"]):
            grp = sc.build_rot_group(stage, f"{ROOT}/SignPost/Arm_{k}",
                                     (sp["cx"], sp["cy"]), yaw)
            BOX(f"{grp}/Box", (sp["cx"] + sp["arm_off"], sp["cy"], az),
                sp["arm"], M["wood"])
        # 벤치 1
        bn = PARAMS["bench"]
        sc.build_bench(stage, f"{ROOT}/Bench", bn["cx"], bn["cy"], 0.0,
                       M["deck"], yaw=bn["yaw"])
        # 쉼터 정자 (하부 산책로)
        pg = PARAMS["pergola"]
        sc.build_canopy(stage, f"{ROOT}/Pergola", pg["x0"], pg["x1"], pg["y0"],
                        pg["y1"], pg["z_roof"], pg["post_r"], M["deck"],
                        M["stringer"], roof_t=pg["roof_t"], base_z=GROUND_Z)

    def build_horizon(M):
        for i, h in enumerate(PARAMS["far_hedges"]):
            base = ground_z((h["x0"] + h["x1"]) / 2.0,
                            (h["y0"] + h["y1"]) / 2.0)
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}", h["x0"], h["y0"],
                           h["x1"], h["y1"], h["h"], base_z=base)
        # [v6 C-4] 원경 능선 마루 숲 밴드 — 개체 롤리팝 대신 실루엣 띠로 폐쇄
        for i, h in enumerate(PARAMS["ridge_crest"]):
            sc.build_hedge(stage, f"{ROOT}/RidgeCrest_{i}", h["x0"], h["y0"],
                           h["x1"], h["y1"], h["h"], base_z=h["base"])
        # [v6 C-4] 원경 개체는 줄기 반경·높이를 키워 '가는 막대 + 구' 회피
        for i, t in enumerate(PARAMS["hill_trees"]):
            gz = _zone_z(t["cx"], t["cy"], t["zone"])
            sc.build_tree(stage, f"{ROOT}/HillTree_{i}", t["cx"], t["cy"], gz,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.17, trunk_h=4.6 + 0.35 * (i % 4),
                          stake_r=0.004, stake_h=0.02, stake_off=0.2)

    # [v5.2 사용자] 임의 경고 팻말 제거 — build_sign() 삭제.

    def build_cues(M):
        """비관행 설비 단서(코드 경로만)."""
        if cfg["cue_tactile"]:
            tac = sc.make_pbr(stage, "/World/Looks/Tactile",
                              diffuse_color=(0.85, 0.72, 0.10),
                              roughness_const=0.7)
            sc.build_tactile(stage, f"{ROOT}/Tactile", -2.10, -1.50,
                             PARAMS["landing"]["y0"], PARAMS["landing"]["y1"],
                             tac, z=0.0)
        if cfg["cue_nosing"]:
            fl = PARAMS["flights"]
            for f in SEQ:
                grp = sc.build_rot_group(stage, f"{ROOT}/NoseGrp_{f['k']}",
                                         (f["x_top"], 0.0), f["rot"])
                lo, hi = band(True)
                sc.build_nosing(stage, f"{grp}/Nose", f["x_top"], lo, hi,
                                fl["riser"], fl["tread"], fl["steps"],
                                base_z=f["z_bot"], z_top=f["z_top"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    M["rail"] = M["stringer"]          # 목재 난간 (데크와 동일 목재)
    build_terrain(M)
    if cfg["hazard_stairs"]:
        build_deck(M)
        build_cues(M)
    else:
        build_flat_fill(M)
    build_horizon(M)
    if cfg["cue_scene_dressing"]:
        build_nature(M)
        build_props(M)
    # [v5.2 사용자] 임의 경고 팻말 제거 — cue_sign 배치 삭제.

    print(f"[기하] 갈지자 {PARAMS['flights']['n']}플라이트 × "
          f"{PARAMS['flights']['steps']}단 총낙차 {TOTAL_DROP:.2f} "
          f"(z {SEQ[0]['z_top']:+.2f} → {SEQ[-1]['z_bot']:+.2f}) · "
          f"참0 외측 난간 파손 개방낙차 "
          f"{SEQ[0]['z_bot'] - GROUND_Z:.2f} m")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── 카메라 + 렌더 모드 ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views()
    _v0 = views["reversal"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene10_{ts}.png")
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
