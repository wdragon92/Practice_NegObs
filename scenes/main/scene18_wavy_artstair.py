# -*- coding: utf-8 -*-
"""
scene18_wavy_artstair.py — NegObs 인공씬 18호: 동네 벽화(색칠) 계단
(Isaac Sim 4.5)

사양서 : Docs/briefs/multi_scene_brief_v5.md §재해석(scene18) — v3 §D 를 대체
공통 라이브러리 : scene_common.py (§A) — boot·make_pbr·add_box·조명·캡처
모티프 참조 : scene05_amphitheater.py (main 골격·cue 토글·드레싱)

[v5 채택] 무대 재해석: '예술 물결 계단' → **문화마을 색칠 계단**.
  기하는 표준 계단에 가깝게 되돌리고(phase 0.4→0.25, amp 0.35→0.245 = 30 %
  축소) 색 변주(위장 효과)만 남긴다. 5색 유지. 낙차 2.56 m(16×0.16) 불변.
  파생 기하(치크월·상부 보도 물결 에지 세그)는 amp/phase 를 함수로 참조하므로
  **자동 추종** — `_wave_selfcheck()` 가 좌표로 검증한다(NEGOBS_SMOKE=1).

유형 정체성: 고대비 색이 오히려 낙차 인지를 교란(위장 대비군).
  16단, 단코가 완만한 사인파(진폭 0.245, 파장 4m)를 이루도록 각 단을 y 세그
  24개 박스로 근사. 라이저 면은 고채색 5색 교대(상수색). 디딤면 밝은 콘크리트.
  cue_nosing 기본 False — 색채가 단코 위치를 흐려 위험 인지를 방해.

[v6 판정 — 재수정] "바다 수평선이 전 13컷에서 미시인 / 벽화가 색블록(레고) /
  사면부 슬리버 파손 / 치크월 톱니 파라펫". 조치:
    ㉠ 해안 재구성 — 지반 동단 x1 50→34(=해안선), 수면 top −4.40→−3.35,
       마을을 계단 조망축(|y|<13) 밖 남·북 군락으로. → 전 +X 컷에서 수평선 노출
       (검산 `_sea_selfcheck`, 화폭 개방 54~100 %). oblique_down 재조준 +
       sea_beauty 컷 신설.
    ㉡ 벽화 — 원색 5색 → 저채도 7색 × 마모 3종, 색 경계를 **사선 연속 띠**로.
    ㉢ 슬리버 — 상부 세그 최소폭 0.052→0.203 m, nseg 24→40(측면 노치 0.128→0.077).
    ㉣ 치크월 — 계단식 톱니 폐기 → 노징선 평행 사선 헌치(scene14 방식).
  물결 계단 곡면·낙차 2.56 m(위험 기하 GT)는 전부 불변.

실행 / 캡처 / 스모크 : scene05·scene06 와 동일한 env 규약.
    NEGOBS_CAPTURE=1 / NEGOBS_SMOKE=1 / NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG
    NEGOBS_SELFCHECK=1 : Isaac 부팅 없이 좌표 검산만(물결 + 수평선)

좌표계: Z-up, m, 진행축 +X. 상단(첫 단 뒤) 모서리 x≈0, 디딤면 +X로 하강.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 7키. hazard_stairs=물결 계단 기하 토글(↔ 평탄 광장).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # 물결 계단 (False → z=0 평탄 소광장)
    "cue_railing":        False,   # 예술 계단 정체성: 개방 — 난간 전무
    "cue_tactile":        False,   # True → 상단 경고 점자띠
    "cue_material_break": True,    # 상부(plaza_light) vs 하부(plaza_lower) 보도
    "cue_nosing":         False,   # 정체성: 색채 위장 — 단코 논슬립 기본 없음
    "cue_sign":           False,   # [예약]
    "cue_scene_dressing": True,    # 벤치·가로등·화단·건물
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # 물결 계단: 16단, riser0.16, tread0.34, y 세그 8(−4..4). 전연 x 오프셋
    #   = amp*sin(2π*y_j/wavelength + i*phase) (단마다 위상 이동 → 물결이 흘러내림)
    #   nseg 24 — 사인 각짐·세로 이음선 완화(핫픽스)(인접 세그 오프셋 연속) [A-18②]
    # [v5 채택] 물결 완화 → **동네 벽화(색칠) 계단**. 기하를 표준 계단에 가깝게
    #   되돌리고 색 변주(위장 효과)만 남긴다. 5색 유지.
    #     phase 0.4 → 0.25 · amp 0.35 → 0.245 (30 % 축소)
    #   1단 최소 노출 디딤 = tread − 2·amp·|sin(phase/2)|
    #     구: 0.34 − 2(0.35)sin(0.20) = 0.34 − 0.1391 = **0.201**
    #     신: 0.34 − 2(0.245)sin(0.125) = 0.34 − 0.0611 = **0.279** (최대 0.401)
    #   riser 0.16 × 16단 = 낙차 2.56 m **불변**(위험 기하 GT 유지).
    # [v6 판정 ㉢] nseg 24 → 40. 세그 j 와 j+1 의 전연 x 차이(= 물결의 세그 간
    #   계단화)가 최대 amp·k·Wb = 0.245·(2π/4)·(8/nseg) 이고, 이 폭만큼 이웃
    #   세그의 **측면(y법선)** 이 노출돼 정오광에서 자기그림자 삼각 노치가 된다
    #   (= oblique_down 의 "종이 슬리버 수십 개"). 24 → 40 이면 0.128 → 0.077 m.
    #   물결 곡면 _front_x(i,y) 자체는 불변이므로 **위험 기하 GT 불변**(세밀화).
    stair=dict(n=16, riser=0.16, tread=0.34, nseg=40, y0=-4.0, y1=4.0,
               amp=0.245, wavelength=4.0, phase=0.25, base_z=-3.0),
    # 라이저 고채색 = 두께 0.05 솔리드 박스, 전면 5mm 매입(계단 솔리드와 겹침 →
    #   상단 개구 봉합, '여물통' 방지), 높이 riser+0.005(상단 윗단 디딤면 아래 1mm) [A-18①]
    riser_panel=dict(thick=0.05, proud=0.005, embed=0.045, top_gap=0.001,
                     over=0.005),
    # 상·하부 보도 (재질 경계) — 솔리드 슬래브(지반 −3.01 까지)
    #   x0=−15.0 : 서측 상가 2동(D/E) 파사드까지 테라스를 연장해 3 m 절벽 제거 [D-18①]
    #   follow_wave=True : 동측 에지를 물결 계단 상단 back 모서리 _front_x(−1,y) 에
    #     맞춰 nseg 세그먼트로 분할. 구 직선 에지(x=0.5)는 파저에서 1~2단을 매몰시켜
    #     첫 단차가 0.16/0.32/0.48 m 로 요동했다(감사 A-18 A1, 치명).
    #   x0=−15.2 : 건물 파사드(x=−15.0)에 0.2 m 물려 동일평면 Z파이팅 회피
    #   [v6 판정 ㉢] seg_min_w : 물결 추종 세그의 **최소 x 폭 하한**. 구 코드는
    #     x_cut = −amp−0.05 라 파저 세그가 0.052 m × 3.01 m 높이의 **종잇장
    #     슬래브**가 됐다(oblique_down 우측 파손의 실체). 0.05 → 0.20 으로
    #     올려 하한 0.202 m 확보(판정 권고 0.15 이상). 동측 에지(계단 접합면)는
    #     불변이므로 첫 단차 0.16 균일도 그대로다.
    upper=dict(x0=-15.2, x1=0.5, y0=-9.0, y1=9.0, top_z=0.0, follow_wave=True,
               seg_min_w=0.20),
    # x0=5.05 : 마지막 단 전연 최소 5.09(= 5.44−0.35)보다 0.04 안쪽 → 0.11 m 슬롯 소거
    # top_z=−2.57 : 마지막 단 상면(−2.56)과 1 cm 이격(동일평면 Z파이팅 회피 + 립 축소)
    lower=dict(x0=5.05, x1=16.0, y0=-9.0, y1=9.0, top_z=-2.57),
    # 계단 폭 밖(|y| 4..9) 도랑 봉합 스커트 — 상부 보도 에지(x=0.5)~하부 보도 사이 [A5]
    skirt=dict(x0=0.5, y_in=4.0, y_out=9.0),
    # [v6 판정 ㉠] 지반 동단이 **해안선**이다. 구 x1=50 + 수면 top −4.40 조합은
    #   지반 절단면 1.39 m 를 마을로 가려야 했고, 그 마을이 수평선을 통째로
    #   막았다(전 13컷 수평선 0). → 지반을 x1=34 에서 끊고 수면을 그 밑(31)부터
    #   깔아 **절단면 0.34 m = 낮은 호안**으로 만든다. 가릴 것이 없으므로
    #   마을을 시선축에서 치울 수 있다.
    #   y 폭은 ±50 → ±90 (측방 시선에서 지반 끝이 프레임에 들어오지 않게).
    ground=dict(x0=-60.0, x1=34.0, y0=-90.0, y1=90.0, top_z=-3.01),
    # 해안 산책로(호안 상면 마감) — 잔디가 바다에 바로 닿는 인상 제거
    quay=dict(x0=29.5, x1=34.0, y0=-90.0, y1=90.0, top_z=-3.005),
    # 드레싱
    benches=[(-4.0, -6.0, 0.0, 0.0), (-4.0, 6.0, 0.0, 0.0),
             (8.0, -5.0, -2.57, 90.0), (8.0, 5.0, -2.57, 90.0),
             (12.0, -5.0, -2.57, 90.0), (12.0, 5.0, -2.57, 90.0)],
    # 가로등 4열(계단 양옆 라인) + 기존 상부 1주 [D-18②]
    streetlights=[dict(x=-6.0, y=-7.5, base_z=0.0, pole_h=6.0),
                  dict(x=-1.0, y=-5.0, base_z=0.0, pole_h=5.0),
                  dict(x=-1.0, y=5.0, base_z=0.0, pole_h=5.0),
                  dict(x=6.5, y=-5.0, base_z=-2.57, pole_h=5.0),
                  dict(x=6.5, y=5.0, base_z=-2.57, pole_h=5.0)],
    streetlight=dict(pole_r=0.06, arm_len=1.0, arm_r=0.04, head=0.25),
    planters=[("A", -7.0, 7.0, 0.0), ("B", 10.0, 7.0, -2.57),
              ("C", 10.0, -7.0, -2.57)],
    # 볼라드 — [v5.1 §2] **전면 제거**.
    #   피드백: "볼라드 안 어울림". §2 상 볼라드는 차량 진입 우려 지점
    #   (보도-차도 접점 / 광장·램프 진입부 / 계단 진입 전면)에만 두는 기능
    #   시설물인데, 본 씬은 차도가 없는 언덕 골목 벽화계단이라 근거가 없다.
    #   구 8본(상부 x −1.2 · 하부 x 6.4)은 순수 장식열이었으므로 삭제한다.
    # 계단 측단 마감(치크월) [v5 판정 반영] — 물결 세그먼트 24개의 끝면이
    #   |y|=4.0 에서 그대로 노출돼 스커트(−2.57) 위 2.57 m 측면이 격자·공동처럼
    #   읽혔고(=oblique_down 우측), 동시에 계단→스커트 2.57 m 측면 낙차가
    #   무방호였다. 단마다 그 단의 전·후연 x 를 그대로 쓰는 계단식 연석을
    #   |y| 4.0..4.3 에 세운다. **계단(위험 기하) 트랜스폼 불변** — 계단 폭 밖에만
    #   덧대는 마감이라 grazing 은닉(계단 노출 0)에도 영향이 없다(높이가 인접
    #   디딤면 +0.14 이므로 h0.3 시선에서 낙차 실루엣을 만들지 않는다).
    # [v6 판정 ㉣] 구 치크월은 단마다 상면이 z_top+0.14 인 **계단식 톱니 파라펫**
    #   — 사용자가 scene14 에서 폐기시킨 형상과 동일 계열이 18 에 잔존했다.
    #   → 단별 박스는 상면을 디딤면과 **면일치(curb=0)** 시켜 톱니를 없애고,
    #     그 위에 노징선 평행 **사선 헌치**(build_slope 1장/측) 를 덮는다.
    #     헌치 상면 z(x) = rise − (riser/tread)·x  (= 노징선 + rise).
    #     두께 0.45 → 헌치 밑면은 상면에서 0.497 아래(=0.45/cos25.2°) 이므로
    #     단별 박스 상면(−0.16(i+1))보다 항상 0.08 m 이상 낮게 물린다 → 공중
    #     부양·틈 0. 계단(위험 기하)은 |y|<4.0, 헌치는 4.0..4.3 — 불침범.
    cheek=dict(w=0.30, curb=0.0, base_z=-2.72,
               rise=0.14, haunch_x0=-0.10, haunch_over=0.15, thick=0.45),
    # 상부 보도 |y| 4.2..9 에지 파라펫 (스커트 낙차 방호) [D-18④]
    parapet=dict(x0=0.2, x1=0.5, y_in=4.2, y_out=9.0, h=1.05),
    # 하부 광장 바닥 밴드 2줄 (광장 스케일 지시) [D-18⑥]
    # [v6 판정 / v5.2 §6] 알베도 0.045 짙은 회색 띠 2줄이 "정체불명 직선 띠"로
    #   판정됨(oblique_down). 기능 근거 없는 스케일 장식이므로 **삭제**
    #   (빌더 경로는 유지 — 리스트를 채우면 복원).
    bands=[],
    buildings=dict(
        # 계단 너머(서쪽) 저층 상가 2동 — color_front·lower_lookback 프레임 상반부가
        #   100 % 하늘이던 문제 해소. base_z 로 지반(−3.01) 접지 [B1/D-18①]
        # [v6 판정 ㉤] h 12/15 · 4~5층은 "언덕 위 저층 주택" 서사와 정면 충돌하는
        #   **암적색 벽돌 아파트**로 읽혔다 → 2층 상가(h 5.0/6.2)로 하향.
        #   낮춘 만큼 배후 언덕 성토단(상면 1.4/4.6/8.2)과 그 위 주택 실루엣이
        #   드러나 프레임 상반부는 계속 채워진다(하늘 100 % 재발 없음):
        #   lower_lookback 기준 앙각 — 상가 8.2° < 언덕1 11.3° < 언덕2 13.9°
        #   < 언덕3 15.3° 로 층층이 올라간다.
        D=dict(x0=-24.0, x1=-15.0, y0=-14.0, y1=-1.0, h=5.0, floors=2,
               axis="x", facade_x=-15.0, face_dir=1.0, base_z=-3.01),
        E=dict(x0=-24.0, x1=-15.0, y0=1.0, y1=14.0, h=6.2, floors=2,
               axis="x", facade_x=-15.0, face_dir=1.0, base_z=-3.01),
        # [v5.1] 구 C(x 44..54, h 15)는 +X 지평선을 통째로 막는 고층 벽이었다.
        #   바닷가 언덕 정체성 확정에 따라 **삭제** — 계단 아래쪽(+X) 지평은
        #   아래 seaside["town"] 저층 지붕 스카이라인 + 바다 수평선이 닫는다.
    ),

    # === [v5.1 현실성] 정체성 확정: **바닷가 언덕 벽화계단** ===
    #   피드백: "바닷가 벽화계단 느낌 — 포지션 확정 필요."
    #   계단은 언덕(−X, 높음)에서 바다 쪽(+X, 낮음)으로 내려간다. 따라서
    #     · 계단 **아래쪽(+X)** = 해안선 → 바다 수평선(조망축)
    #     · 계단 **양옆(±Y)**   = 저층 마을 (조망축을 비켜 앉는다)
    #     · 계단 **위쪽(−X)**   = 언덕 주택 실루엣(계단식 성토 위)
    # [v6 판정 ㉠ — 구조 재편] 구 배치는 "수면을 지반 밑(−4.40)에 깔고 그 절단면
    #   1.39 m 를 마을로 가린다"였는데, 그 마을이 **수평선까지 통째로 가렸다**
    #   (전 13컷 수평선 0 = 정체성 미달). 원인은 저시점(h0.35~1.8)에서 수평선
    #   앙각이 −0.4~−5° 인데 마을 지붕 앙각이 +2~+7° 라 구조적으로 이길 수 없다는
    #   것. → **가릴 절단면을 없앤다**: 지반을 x1=34 에서 끊고(해안선) 수면을
    #   바로 그 밑 −3.35 에 깔면 절단면이 0.34 m 로 줄어 호안으로 읽힌다.
    #   마을은 계단 조망축(|y| < 13)에서 물러나 남·북 군락으로 간다.
    #   검산은 _sea_selfcheck() 가 컷별로 수행(화폭 ±30° 를 5° 간격 레이캐스트).
    seaside=dict(
        # 수면: 헤이즈 톤(저채도·중명도) + 낮은 러프니스 — 원경 수평선 인상
        # [v6 판정 ㉠] top_z −4.40 → **−3.35**(지반 −3.01 바로 아래 0.34 m).
        #   x0 46 → 31 (지반 동단 34 보다 3 m 안쪽 = 지반 두께 1.0 안에 물려
        #   접합 개구 0). 이제 저시점(h0.35)에서도 수면 띠가 지붕 위가 아니라
        #   **지반 너머 아래**로 드러난다 — 마을이 가릴 이유 자체가 사라진다.
        water=dict(x0=31.0, x1=530.0, y0=-560.0, y1=560.0,
                   top_z=-3.35, thick=1.2),
        water_color=(0.175, 0.205, 0.225), water_rough=0.22,
        # 저층 지붕 스카이라인 (x0, x1, y0, y1, h, floors) — 지붕 캡은 아래 roof
        #   등간격/격자 금지(§3): x·y·높이·폭을 전부 비정형으로 흩는다.
        # [v6 판정 ㉠] 구 배치는 계단 하강 축(|y| ≲ 13)을 **정면으로 가로막는
        #   2열 벽**이었다(x 21..42.5 × y −34..38). 실제 바닷가 계단마을은
        #   계단축이 곧 조망축이고 집은 그 **양옆**에 앉는다 → 중앙 회랑
        #   |y| < 13 을 비우고 남·북 군락으로 재편(x 17..32.5, 지반 안쪽).
        #   높이도 3.0~5.6 (1~2층)으로 낮춘다.
        town=[(18.0, 23.5, -40.0, -32.5, 3.4, 1), (21.0, 26.5, -31.0, -24.0, 5.0, 2),
              (17.5, 22.5, -22.5, -15.5, 3.0, 1),
              (26.5, 32.0, -37.0, -29.5, 4.6, 2), (28.0, 32.5, -28.0, -20.0, 3.2, 1),
              (25.5, 31.0, -18.5, -13.5, 5.4, 2),
              (18.5, 24.0, 13.0, 20.0, 3.6, 1), (21.5, 27.0, 21.5, 29.0, 5.2, 2),
              (17.0, 22.0, 30.5, 37.0, 3.0, 1), (20.0, 25.5, 38.5, 45.0, 4.4, 1),
              (26.0, 31.5, 14.5, 22.0, 4.8, 2), (28.5, 32.5, 23.5, 31.0, 3.2, 1),
              (25.0, 30.5, 32.5, 40.0, 5.6, 2)],
        roof=dict(over=0.35, t=0.28),      # 지붕 캡(처마 0.35 돌출) — 마을 실루엣
        roof_color=(0.115, 0.085, 0.070), roof_rough=0.75,
        # 언덕 성토 3단 (x0, x1, top_z) — y 전폭. 계단 위쪽(−X)이 솟는다.
        terraces=[(-33.0, -26.0, 1.4), (-40.0, -33.0, 4.6), (-50.0, -40.0, 8.2)],
        terrace_y=(-46.0, 46.0),
        # 언덕 주택 (x0, x1, y0, y1, base_z, h) — 성토 상면에 접지, 비정형 배치
        houses=[(-31.5, -27.0, -41.0, -35.5, 1.4, 3.8),
                (-32.0, -27.5, -33.0, -27.0, 1.4, 4.4),
                (-31.0, -26.5, -24.5, -18.5, 1.4, 3.5),
                (-32.5, -27.0, 17.5, 23.5, 1.4, 4.1),
                (-31.5, -26.5, 25.5, 32.0, 1.4, 3.6),
                (-32.0, -27.5, 34.0, 40.5, 1.4, 4.6),
                (-38.5, -34.0, -38.0, -31.5, 4.6, 4.0),
                (-39.0, -33.5, -29.0, -22.0, 4.6, 3.4),
                (-38.0, -33.5, -13.0, -6.0, 4.6, 4.5),
                (-39.0, -34.5, 6.5, 13.0, 4.6, 3.9),
                (-38.5, -34.0, 21.0, 27.5, 4.6, 4.3),
                (-39.5, -34.0, 30.0, 37.0, 4.6, 3.6),
                (-47.0, -41.5, -34.0, -27.0, 8.2, 3.7),
                (-46.5, -41.0, -18.0, -11.0, 8.2, 4.2),
                (-47.5, -42.0, 2.0, 9.0, 8.2, 3.5),
                (-46.0, -41.0, 15.0, 22.0, 8.2, 4.4),
                (-47.0, -41.5, 28.0, 35.0, 8.2, 3.8)],
        house_color=(0.30, 0.29, 0.27), house_rough=0.75,
        # [v6] 판정 ⑤ "무텍스처 백색 박스의 복제". 벽·지붕 변종을 3 → 5 로 늘리고
        #   명도뿐 아니라 **색조**(따뜻/차가움)도 흔든다 — 항구 마을의 페인트 벽.
        house_var=((0.90, 0.89, 0.87), (1.00, 0.98, 0.94), (1.10, 1.04, 0.96),
                   (0.94, 0.99, 1.06), (1.16, 1.10, 1.00)),
        roof_var=((0.85, 0.88, 0.95), (1.00, 0.96, 0.92), (1.12, 1.00, 0.90),
                  (0.92, 0.90, 1.00), (1.05, 1.08, 1.10)),
    ),

    material=dict(
        scale=dict(concrete_floor=1.2, plaza_light=0.75, plaza_lower=0.8,
                   brick_red=2.0, grass=4.0),
        tread_tint=(1.15, 1.15, 1.12),            # 밝은 콘크리트 디딤면
        lower_warm_tint=(1.06, 1.0, 0.94),
        # 라이저 색 — [v6 판정 ㉡] 구 5색은 원색 솔리드(최대/최소 채널비 7~9)라
        #   단마다 통째로 색이 바뀌는 **레고 블록 적층**으로 읽혔다. 판정 권고
        #   "횡방향 연속 띠 + 낮은 채도(벽화 인상)" 를 이렇게 구현한다:
        #     ㉮ 팔레트 7색으로 늘리되 채널비를 2.2 이하로 낮춘 **벽화 중간톤**
        #        (테라코타·머스터드·세이지·청록·청·자주회·크림). 최대 채널 0.52
        #        → §4 "순백(>0.8) 대면적 금지" 여유.
        #     ㉯ 색 인덱스를 단 i 가 아니라 **i + (y 정규화)·mural_skew** 로 잡아
        #        색 경계가 계단을 **사선으로 가로지르는 연속 띠**가 되게 한다.
        #        (= 색 경계와 단코 경계가 어긋남 → 이 씬의 정체성인 '색 위장'은
        #          오히려 강화된다. skew 2.5 = 폭 8 m 에서 2.5단 만큼 밀림)
        #     ㉰ 세그별 마모 틴트 3종(±10 %)으로 같은 띠 안에서도 명도가 흔들려
        #        솔리드 판 인상과 세로 이음선이 함께 완화된다.
        riser_colors=[(0.42, 0.24, 0.19), (0.50, 0.40, 0.20),
                      (0.30, 0.38, 0.27), (0.20, 0.34, 0.36),
                      (0.22, 0.30, 0.42), (0.36, 0.28, 0.34),
                      (0.52, 0.49, 0.42)],
        mural_skew=2.5,
        mural_wear=(0.88, 1.0, 1.09),
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # [v5.1 §4] 파라펫 0.90 → 0.72 (순백 대면적 금지)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        nosing_color=(0.85, 0.72, 0.10), nosing_rough=0.7,
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


_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene18")


# ===========================================================================
# [C] 물결 전연 오프셋 (순수 수학 — pxr 불필요)
# ===========================================================================
def _seg_centers():
    s = PARAMS["stair"]
    Wb = (s["y1"] - s["y0"]) / s["nseg"]
    return [s["y0"] + (j + 0.5) * Wb for j in range(s["nseg"])], Wb


def _front_x(i, y):
    """단 i(전연) x. i=−1 은 상단 back 모서리. 위상 i*phase 로 물결 흘러내림."""
    s = PARAMS["stair"]
    k = 2.0 * math.pi / s["wavelength"]
    return (i + 1) * s["tread"] + s["amp"] * math.sin(k * y + i * s["phase"])


# ===========================================================================
# [C2] [v5 채택] 물결 완화 자기검증 — 치크월·상부 에지 세그가 자동 추종하는지
#      **좌표로** 확인 (Isaac 부팅 불필요, 순수 수학).
# ===========================================================================
def _wave_selfcheck(verbose=True):
    """amp/phase 변경이 파생 기하에 자동 반영되는지 좌표 검산.

    ① 치크월(|y| 4.0..4.3): 단 i 의 x 구간을 _front_x(i−1/i, y1) 로 잡는다.
       물결 위상 동일성 — k = 2π/wavelength = 2π/4 이므로
         y=+4 : sin(k·4  + iφ) = sin( 2π + iφ) = sin(iφ)
         y=−4 : sin(k·(−4)+ iφ) = sin(−2π + iφ) = sin(iφ)
       **양측 위상이 항상 같다** → phase/amp 값과 무관하게 성립(파장 4 m 가
       계단 폭 8 m 를 정확히 2주기로 나누기 때문). 아래에서 수치로 재확인한다.
    ② 상부 보도 세그(follow_wave): x_cut = −amp − 0.05, 세그 동측 에지
       x1_j = _front_x(−1, yc_j) = amp·sin(k·yc_j − φ) ∈ [−amp, amp]
       → 전 세그에서 x1_j − x_cut ≥ 0.05 (음폭 슬래브 없음).
    ③ 상부 보도 |y|>4 직선 에지 x=0.5 > max back 모서리(amp).
    ④ 하부 보도 x0=5.05 < 마지막 단 전연 최소값(= 16·tread − amp).
    반환: (ok, 진단 dict)
    """
    s = PARAMS["stair"]
    up, lo = PARAMS["upper"], PARAMS["lower"]
    ck = PARAMS["cheek"]
    yc, Wb = _seg_centers()
    # ① 치크월 좌우 위상 동일성
    dmax = max(abs(_front_x(i, s["y1"]) - _front_x(i, s["y0"]))
               for i in range(-1, s["n"]))
    # ② 세그 폭
    x_cut = -s["amp"] - up.get("seg_min_w", 0.05)
    wmin = min(_front_x(-1, y) + 0.002 - x_cut for y in yc)
    # ③ 직선 에지 여유
    back_max = max(_front_x(-1, y) for y in yc)
    m3 = up["x1"] - back_max
    # ④ 하부 보도 겹침
    front_min = min(_front_x(s["n"] - 1, y) for y in yc)
    m4 = front_min - lo["x0"]
    # ⑤ 노출 디딤 폭(최소/최대) — 위험 인지 난이도 지표
    tr = [_front_x(i, y) - _front_x(i - 1, y)
          for i in range(s["n"]) for y in yc]
    # ⑥ [v6] 세그 측면 노치 — 이웃 세그의 전연 x 차이(= 노출되는 측면 폭).
    #    자기그림자 삼각 노치("종이 슬리버")의 실제 원인 치수.
    notch = max(abs(_front_x(i, yc[j + 1]) - _front_x(i, yc[j]))
                for i in range(s["n"]) for j in range(s["nseg"] - 1))
    # ⑦ [v6] 치크 헌치 — 상면이 인접 디딤면 위, 밑면이 몸통 상면 아래인가.
    kk = s["riser"] / s["tread"]
    def hz(x):                                    # 헌치 상면 z(x)
        return ck["rise"] - kk * x

    hb = ck["thick"] / math.cos(math.atan(kk))    # 상면→밑면 수직 거리
    h_over, h_under = 1e9, 1e9
    for i in range(s["n"]):
        xa, xb = _front_x(i - 1, s["y1"]), _front_x(i, s["y1"])
        top_i = -s["riser"] * (i + 1) + ck["curb"]
        for x in (xa, xb):
            h_over = min(h_over, hz(x) - top_i)        # 헌치 상면 − 몸통 상면
            h_under = min(h_under, top_i - (hz(x) - hb))  # 몸통 상면 − 헌치 밑면
    ok = (dmax < 1e-9) and (wmin > 0.0) and (m3 > 0.0) and (m4 > 0.0) \
        and (min(tr) > 0.0) and (notch < 0.09) and (h_over > 0.0) \
        and (h_under > 0.0)
    diag = dict(cheek_lr_dx=dmax, seg_w_min=wmin, upper_edge_margin=m3,
                lower_overlap=m4, tread_min=min(tr), tread_max=max(tr),
                notch=notch, haunch_over=h_over, haunch_under=h_under,
                drop=s["n"] * s["riser"])
    if verbose:
        print("=" * 64)
        print("scene18 [v5] 물결 완화 자기검증 (amp=%.3f phase=%.3f)"
              % (s["amp"], s["phase"]))
        print("=" * 64)
        print(f"  ① 치크월 좌우 위상차  max|x(+4)−x(−4)| = {dmax:.3e}  "
              f"→ {'동일(자동 추종 OK)' if dmax < 1e-9 else 'FAIL'}")
        print(f"     치크월 x 구간(단 0) = "
              f"[{_front_x(-1, s['y1']):+.4f}, {_front_x(0, s['y1']):+.4f}] "
              f"@ |y| {s['y1']:.1f}..{s['y1'] + ck['w']:.1f}")
        print(f"  ② 상부 세그 최소 폭   {wmin:.4f} m (x_cut={x_cut:+.3f})  "
              f"→ {'OK' if wmin > 0 else 'FAIL'}")
        print(f"  ③ 직선 에지 여유      {m3:.4f} m (x1={up['x1']}, "
              f"back_max={back_max:+.4f}) → {'OK' if m3 > 0 else 'FAIL'}")
        print(f"  ④ 하부 보도 겹침      {m4:.4f} m (x0={lo['x0']}, "
              f"front_min={front_min:.4f}) → {'OK' if m4 > 0 else 'FAIL'}")
        print(f"  ⑤ 노출 디딤 폭        {min(tr):.4f} ~ {max(tr):.4f} m "
              f"(구 0.201~0.479)")
        print(f"  ⑥ 세그 측면 노치 최대 {notch:.4f} m (nseg={s['nseg']}, "
              f"구 nseg24 = 0.1276) → {'OK' if notch < 0.09 else 'FAIL'}")
        print(f"  ⑦ 치크 헌치           상면−몸통 {h_over:+.4f} · "
              f"몸통−밑면 {h_under:+.4f} → "
              f"{'OK(틈·부유 0)' if h_over > 0 and h_under > 0 else 'FAIL'}")
        print(f"  낙차(GT) {s['n'] * s['riser']:.2f} m — 불변")
        print("=" * 64)
    return ok, diag


# ===========================================================================
# [C3] [v6 판정 ㉠] **바다 수평선 시인성 검산** — 순수 수학(Isaac 부팅 불필요).
#   v6 판정: "바다 수평선이 전 13컷 중 어디에서도 보이지 않는다. VC 픽스로그의
#   차폐 검산은 지반 절단면만 봤고 **수평선 가시성 검산은 없었다**."
#   → 그 검산을 코드로 고정한다. 컷마다 시선축 수직면에서:
#     · 수면 밴드 앙각 [a_near, a_far]
#         a_far  = 수면 원단(x1) 앙각 ≈ 수평선
#         a_near = 지반 동단(해안선) 위를 스쳐 지나간 시선이 수면에 닿는 점
#     · 차폐 앙각 blk = 시선축 평면상 장애물(마을·언덕·상가·화단) 상면 최대 앙각
#     · 프레임 = 세로 반화각 18°(vFOV 36°, 16:9·기본 초점거리 기준) 안인가
#   판정: blk < a_far (수평선 노출) · a_far ≤ pitch+18° · a_near ≥ pitch−18°
# ===========================================================================
def _sea_selfcheck(verbose=True, cuts=("wave_raking", "oblique_down",
                                       "sea_beauty", "preset_h0.3_d5",
                                       "preset_h1.8_d10")):
    sea = PARAMS["seaside"]
    w, g = sea["water"], PARAMS["ground"]
    rf_h = 0.5                                   # build_building 파라펫 높이
    # (x0, x1, y0, y1, top_z) 장애물 — +X 시선을 막을 수 있는 것만
    obs = [(x0, x1, y0, y1, g["top_z"] + h + rf_h)
           for (x0, x1, y0, y1, h, _f) in sea["town"]]
    for name, bd in PARAMS["buildings"].items():
        obs.append((bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                    bd["base_z"] + bd["h"] + rf_h))
    for px, py, bz in [(p[1], p[2], p[3]) for p in PARAMS["planters"]]:
        obs.append((px - 1.5, px + 1.5, py - 1.5, py + 1.5, bz + 3.2))
    views = build_views()
    diag, ok = {}, True
    for name in cuts:
        v = views[name]
        ex, ey, ez = v["eye"]
        tx, ty, tz = v["tgt"]
        dxh, dyh = tx - ex, ty - ey
        dh = math.hypot(dxh, dyh)
        ux, uy = dxh / dh, dyh / dh              # 시선축 수평 단위벡터
        pitch = math.degrees(math.atan2(tz - ez, dh))
        if ux <= 1e-6:                           # 바다(+X) 를 등진 컷은 대상 외
            diag[name] = dict(skip=True)
            continue
        d_edge = (g["x1"] - ex) / ux             # 해안선까지 수평거리
        slope = (g["top_z"] - ez) / d_edge
        d_near = (w["top_z"] - ez) / slope       # 시선이 수면에 닿는 거리
        d_far = (w["x1"] - ex) / ux
        a_near = math.degrees(math.atan2(w["top_z"] - ez, d_near))
        a_far = math.degrees(math.atan2(w["top_z"] - ez, d_far))
        # 차폐는 시선축 1개가 아니라 **수평 화각 전폭(±30°)** 을 5° 간격으로
        #   훑는다(축만 보면 마을이 프레임 절반을 막아도 통과해버린다).
        base_az = math.degrees(math.atan2(uy, ux))
        blk, who, n_vis, n_ray = -90.0, "", 0, 0
        for m_ in range(-6, 7):
            aa = math.radians(base_az + 5.0 * m_)
            vx, vy = math.cos(aa), math.sin(aa)
            if vx <= 1e-6:
                continue
            n_ray += 1
            de = (g["x1"] - ex) / vx
            af = math.degrees(math.atan2(w["top_z"] - ez,
                                         (w["x1"] - ex) / vx))
            b_, w_ = -90.0, ""
            for x0, x1, y0, y1, top in obs:
                t0, t1 = 0.0, 1e9
                for a, u, lo, hi in ((ex, vx, x0, x1), (ey, vy, y0, y1)):
                    if abs(u) < 1e-9:
                        if a < lo or a > hi:
                            t0, t1 = 1.0, 0.0
                            break
                        continue
                    ta, tb = (lo - a) / u, (hi - a) / u
                    t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
                if t0 > t1 or t1 <= 0.0 or t0 > de:
                    continue
                ang = math.degrees(math.atan2(top - ez, max(t0, 0.5)))
                if ang > b_:
                    b_, w_ = ang, f"{x0:.0f}~{x1:.0f}"
            if b_ < af:
                n_vis += 1
            if b_ > blk:
                blk, who = b_, w_
        vis = n_vis >= max(1, int(0.5 * n_ray))     # 화각 절반 이상에서 노출
        in_frame = (a_far <= pitch + 18.0) and (a_near >= pitch - 18.0)
        diag[name] = dict(pitch=round(pitch, 1), a_near=round(a_near, 2),
                          a_far=round(a_far, 2), blk=round(blk, 2),
                          blk_who=who, vis=vis, in_frame=in_frame,
                          open_pct=round(100.0 * n_vis / max(n_ray, 1)),
                          band=round(min(a_far, pitch + 18.0)
                                     - max(a_near, pitch - 18.0), 2))
        if not (vis and in_frame and diag[name]["band"] > 0.5):
            ok = False
    if verbose:
        print("=" * 64)
        print("scene18 [v6] 바다 수평선 시인성 검산 (세로 반화각 18° 가정)")
        print("=" * 64)
        for k, d in diag.items():
            if d.get("skip"):
                print(f"  {k:16s} — 바다 반대편 시선(대상 외)")
                continue
            print(f"  {k:16s} pitch{d['pitch']:+6.1f}°  수면 앙각 "
                  f"{d['a_near']:+6.2f}..{d['a_far']:+6.2f}°  "
                  f"최대차폐 {d['blk']:+6.2f}°  화폭 개방 {d['open_pct']:3d}%  "
                  f"수면띠 {d['band']:5.2f}°  "
                  f"{'OK' if d['vis'] and d['in_frame'] else 'FAIL'}")
        print(f"  → {'OK (요구 3컷 이상에서 수평선 시인)' if ok else 'FAIL'}")
        print("=" * 64)
    return ok, diag


# ===========================================================================
# [D] 카메라 프리셋 — grid_views(gy=0) + 미장센 4컷
# ===========================================================================
def build_views():
    """그리드 9장(상단 back 모서리 x≈0 기준) + 미장센 4컷(브리프 §D 특색)."""
    v = sc.grid_views(0.0)
    out = {k: dict(eye=list(val["eye"]), tgt=list(val["tgt"]))
           for k, val in v.items()}
    out["wave_raking"]    = dict(eye=[-3.0, 0.0, 0.35], tgt=[5.0, 0.0, -1.3])
    # color_front: 하부 광장에서 계단 정면(h1.2 above 하부보도 −2.58, d≈6) [A-18③]
    out["color_front"]    = dict(eye=[11.7, 0.0, -1.38], tgt=[2.7, 0.0, -1.1])
    # [v6 판정 ㉠] oblique_down 재조준 — 구 (eye −4,4.5,2.6 → tgt 3.5,0,−1.5)는
    #   부각 25.7° 라 수평선 밴드가 프레임 위(중심 +20~25°)로 완전히 벗어났다.
    #   부각을 14.6° 로 낮추고 시점을 0.4 m 올려, **물결 계단(하좌) + 바다
    #   수평선(상부)** 이 한 프레임에 들어오게 한다(검산 _sea_selfcheck).
    out["oblique_down"]   = dict(eye=[-4.5, 5.0, 3.0],  tgt=[7.5, 0.0, -0.4])
    out["lower_lookback"] = dict(eye=[8.5, 0.0, -1.9],  tgt=[2.0, 0.0, -1.4])
    # [v6 판정 ㉠ 신설] sea_beauty — 언덕 쪽 3/4 부감(beauty 컷).
    #   계단 하강축 너머로 해안선·수평선이 프레임 중앙~상단에 걸린다.
    out["sea_beauty"]     = dict(eye=[-12.0, -9.0, 5.5], tgt=[26.0, 4.0, -1.5])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. wave_raking    — h0.3 그레이징에서 색 교대가 낙차를 위장하는가
 2. color_front    — 라이저 5색 교대(고채색)가 단코를 흐리는가
 3. oblique_down   — 완만해진 단코가 세그(24) 각짐 없이 흐르는가
                     + 치크월(|y|4.0..4.3)이 물결을 그대로 따라가는가 [v5]
 4. cue_nosing OFF — 색채 위장 정체성(기본 논슬립 없음)
 5. material_break — 상부(밝음)/하부(웜) 보도 재질 경계
 6. [v5] 노출 디딤 0.279~0.401 m — '표준 계단에 색만 칠한' 인상인가
 7. [v6] sea_beauty / oblique_down / wave_raking — **바다 수평선**이 보이는가
        (검산: NEGOBS_SELFCHECK=1 python scene18_wavy_artstair.py)
 8. [v6] 벽화 사선 띠가 '레고 적층'이 아니라 칠한 그림으로 읽히는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"

    if smoke_mode:
        _wave_selfcheck()          # [v5] 부팅 전 좌표 검산 (그 뒤 프림 수 검증)
        _sea_selfcheck()           # [v6] 수평선 시인성 검산

    # 좌표 검산만 수행하고 종료 (Isaac 부팅 불필요)
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        a, _ = _wave_selfcheck()
        b, _ = _sea_selfcheck()
        print(f"SELFCHECK {'OK' if (a and b) else 'FAIL'}")
        return

    sc.check_assets(
        ["concrete_floor", "plaza_light", "plaza_lower", "grass", "brick_red",
         "hdri", "mdl"],
        hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene18")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        scl = mp["scale"]
        M = {}
        M["tread"] = sc.make_pbr(
            stage, "/World/Looks/Tread", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), scl["concrete_floor"],
            tint=mp["tread_tint"])
        M["upper"] = sc.make_pbr(
            stage, "/World/Looks/Upper", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"])
        M["lower"] = sc.make_pbr(
            stage, "/World/Looks/Lower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            scl["plaza_lower"], tint=mp["lower_warm_tint"])
        # [v6] 벽화 팔레트 7색 × 마모 3종 = 21 재질 (M["riser"][색][마모])
        M["riser"] = [[sc.make_pbr(
            stage, f"/World/Looks/Riser_{c}_{w}",
            diffuse_color=tuple(min(v * f, 1.0) for v in col),
            roughness_const=0.55, metallic=0.0)
            for w, f in enumerate(mp["mural_wear"])]
            for c, col in enumerate(mp["riser_colors"])]
        M["brick"] = sc.make_pbr(
            stage, "/World/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            scl["brick_red"])
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            scl["grass"], tint=mp["grass_tint"])
        M["glass"] = sc.make_pbr(stage, "/World/Looks/Glass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"], metallic=0.0)
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["parapet"] = sc.make_pbr(stage, "/World/Looks/Parapet",
                                   diffuse_color=mp["parapet_color"],
                                   roughness_const=mp["parapet_rough"])
        M["lamp"] = sc.make_pbr(stage, "/World/Looks/Lamp",
                                diffuse_color=mp["lamp_color"],
                                roughness_const=mp["lamp_rough"])
        M["pole"] = sc.make_pbr(stage, "/World/Looks/Pole",
                                diffuse_color=mp["pole_color"],
                                metallic=mp["pole_metallic"],
                                roughness_const=mp["pole_rough"])
        # [v5.1] 바닷가 언덕 정체성 — 수면·지붕·주택 벽. 인스턴스 틴트 지터(§4)는
        #   지붕·벽 각각 3종으로 준다(마을이 단일 색 복제로 보이지 않게).
        sea = PARAMS["seaside"]
        M["sea"] = sc.make_pbr(stage, "/World/Looks/Sea",
                               diffuse_color=sea["water_color"],
                               roughness_const=sea["water_rough"],
                               metallic=0.0)
        M["nvar"] = len(sea["house_var"])
        for i in range(M["nvar"]):
            M[f"roof_{i}"] = sc.make_pbr(
                stage, f"/World/Looks/Roof_{i}",
                diffuse_color=tuple(min(c * f, 1.0) for c, f
                                    in zip(sea["roof_color"],
                                           sea["roof_var"][i])),
                roughness_const=sea["roof_rough"])
            M[f"house_{i}"] = sc.make_pbr(
                stage, f"/World/Looks/House_{i}",
                diffuse_color=tuple(min(c * f, 1.0) for c, f
                                    in zip(sea["house_color"],
                                           sea["house_var"][i])),
                roughness_const=sea["house_rough"])
        return M

    # -------------------------------------------------------------------
    # 지반 바닥(잔디) — 전면 슬래브(낙차보다 아래 = 바닥). 4박스 타일링.
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        top, th = g["top_z"], 1.0
        cz = top - th / 2.0
        xm = (g["x0"] + g["x1"]) / 2.0
        ym = (g["y0"] + g["y1"]) / 2.0
        for tag, (x0, x1, y0, y1) in (
                ("SW", (g["x0"], xm, g["y0"], ym)),
                ("SE", (xm, g["x1"], g["y0"], ym)),
                ("NW", (g["x0"], xm, ym, g["y1"])),
                ("NE", (xm, g["x1"], ym, g["y1"]))):
            sc.add_box(stage, f"/World/Scene18/Ground_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                       (x1 - x0, y1 - y0, th), M["grass"])

    # -------------------------------------------------------------------
    # 상·하부 보도(재질 경계) — 솔리드 슬래브.
    # -------------------------------------------------------------------
    def _slab(path, x0, x1, y0, y1, top, mtl):
        """상면 top, 밑면 지반(−3.01) 까지 채우는 솔리드 슬래브 1장."""
        base = PARAMS["ground"]["top_z"]
        sc.add_box(stage, path,
                   ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (top + base) / 2.0),
                   (x1 - x0, y1 - y0, top - base), mtl, collider=True)

    def build_walkways(M, hazard):
        """상·하부 보도. hazard=True 면 상부 보도 **동측 에지를 물결에 맞춰
        세그먼트화**한다(감사 A-18 A1 치명).

        구 구조: 상부 슬래브가 x ≤ 0.5 를 z 0..−3.01 로 꽉 채워, 전연이 x=0.5
        미만인 파저(波底) 구간의 1~2단이 통째로 매몰 → 첫 단차가 폭 방향으로
        0.16 / 0.32 / 0.48 m 로 요동(폭 8 m 중 2.70 m 가 0.48 m 낙차 = 점프).
        신 구조: 계단 폭(|y|<4) 안에서 세그 j 의 동측 에지를
            x1_j = _front_x(-1, yc[j]) = 0.35·sin(k·yc[j] − 0.4)  ∈ [−0.35, +0.35]
        로 지정 → 계단 최상단 back 모서리와 정확히 맞물려 **첫 단차 전 폭 0.16 m
        균일**. 계단(위험 기하) 트랜스폼은 불변, 보도만 손댄다.
        하부: x0 5.2→5.05(마지막 단 전연 최소 5.09 대비 0.04 안쪽) → A3 슬롯 소거.
        스커트: |y| 4..9 의 x 0.5..5.05 잔디 도랑을 하부 레벨로 메움(A5)."""
        s = PARAMS["stair"]
        up, lo = PARAMS["upper"], PARAMS["lower"]
        top_u = up["top_z"] if hazard else 0.0
        top_l = lo["top_z"] if hazard else 0.0
        if hazard and up.get("follow_wave", False):
            yc, Wb = _seg_centers()
            # [v6 판정 ㉢] 세그 최소폭 하한 = upper["seg_min_w"] (0.052 → 0.202)
            x_cut = -s["amp"] - up.get("seg_min_w", 0.05)
            # ① 본체(전폭) x0..x_cut
            _slab("/World/Scene18/Walk_upper_W", up["x0"], x_cut,
                  up["y0"], up["y1"], top_u, M["upper"])
            # ② 계단 폭 밖(|y| 4..9) — 구 직선 에지 x1(=0.5) 유지
            for tag, y0, y1 in (("S", up["y0"], s["y0"]),
                                ("N", s["y1"], up["y1"])):
                _slab(f"/World/Scene18/Walk_upper_{tag}", x_cut, up["x1"],
                      y0, y1, top_u, M["upper"])
            # ③ 계단 폭 안 — 세그별 물결 에지 (2 mm 겹침으로 헤어라인 방지)
            for j in range(s["nseg"]):
                x1j = _front_x(-1, yc[j]) + 0.002
                sy0 = s["y0"] + j * Wb - 0.001
                sy1 = s["y0"] + (j + 1) * Wb + 0.001
                _slab(f"/World/Scene18/Walk_upper_Seg_{j}", x_cut, x1j,
                      sy0, sy1, top_u, M["upper"])
        else:
            _slab("/World/Scene18/Walk_upper", up["x0"], up["x1"],
                  up["y0"], up["y1"], top_u, M["upper"])
        # --- 하부 보도 ---
        _slab("/World/Scene18/Walk_lower", lo["x0"], lo["x1"],
              lo["y0"], lo["y1"], top_l, M["lower"])
        if hazard:
            # 계단 폭 밖 도랑 봉합 스커트 2장 (위험 기하 불변)
            sk = PARAMS["skirt"]
            for tag, y0, y1 in (("S", -sk["y_out"], -sk["y_in"]),
                                ("N", sk["y_in"], sk["y_out"])):
                _slab(f"/World/Scene18/Walk_skirt_{tag}", sk["x0"], lo["x0"],
                      y0, y1, top_l, M["lower"])
        else:
            # 대조군(평탄): 계단 자리 공백을 z=0 으로 메움
            _slab("/World/Scene18/Walk_flat", up["x1"], lo["x0"],
                  lo["y0"], lo["y1"], 0.0, M["lower"])

    # -------------------------------------------------------------------
    # 물결 계단 — 단 i × 세그 j 박스 + 라이저 고채색 판
    # -------------------------------------------------------------------
    def build_stair(M):
        s = PARAMS["stair"]
        rp = PARAMS["riser_panel"]
        base_z = s["base_z"]
        yc, Wb = _seg_centers()
        ncol = len(M["riser"])
        skew = mp["mural_skew"]
        span_y = s["y1"] - s["y0"]
        for i in range(s["n"]):
            z_top = -s["riser"] * (i + 1)
            for j in range(s["nseg"]):
                y = yc[j]
                # [v6] 사선 연속 띠: 색 경계가 단코와 어긋나 계단을 가로지른다.
                col_mtl = M["riser"][int(math.floor(
                    i + (y - s["y0"]) / span_y * skew)) % ncol][
                        (i * 7 + j * 13) % len(mp["mural_wear"])]
                x_back = _front_x(i - 1, y)
                x_front = _front_x(i, y)
                cxs = (x_back + x_front) / 2.0
                sy0 = s["y0"] + j * Wb - 0.001    # 1mm 겹침
                sy1 = s["y0"] + (j + 1) * Wb + 0.001
                # 디딤(솔리드 박스, 상면=디딤면)
                sc.add_box(stage, f"/World/Scene18/Step_{i}_{j}",
                           (cxs, (sy0 + sy1) / 2.0, (z_top + base_z) / 2.0),
                           (x_front - x_back, sy1 - sy0, z_top - base_z),
                           M["tread"], collider=True)
                # 라이저 고채색 솔리드(전면 5mm 매입 — 계단 솔리드와 겹쳐 상단 봉합).
                #   앞면 = x_front+over(proud), 뒷면 = x_front−embed(계단 속 겹침).
                #   높이 = riser+over, 상단 = z_top−top_gap(윗단 디딤면 아래 1mm).
                r_cx = x_front - rp["thick"] / 2.0 + rp["over"]
                r_h = s["riser"] + rp["over"]
                r_top = z_top - rp["top_gap"]
                sc.add_box(stage, f"/World/Scene18/Riser_{i}_{j}",
                           (r_cx, (sy0 + sy1) / 2.0, r_top - r_h / 2.0),
                           (rp["thick"], sy1 - sy0, r_h), col_mtl)
            # [v5 판정 반영] 측단 치크월 — 단 i 의 전·후연 x 를 그대로 쓰는
            #   연석 몸통 2장(|y| 4.0..4.3). y=±4 에서 물결 위상은
            #   sin(k·(±4)+i·φ) = sin(±2π+i·φ) = sin(i·φ) 로 **양측이 동일**하므로
            #   한 쌍의 x 구간으로 좌우를 같이 만든다.
            # [v6 판정 ㉣] 몸통 상면을 디딤면과 면일치(curb=0)시켜 계단식 톱니를
            #   제거한다. 가시 상면은 아래 build_cheek_haunch 의 사선 헌치.
            ck = PARAMS["cheek"]
            xb_e = _front_x(i - 1, s["y1"])
            xf_e = _front_x(i, s["y1"])
            c_top = z_top + ck["curb"]
            for tag, cy0, cy1 in (("S", s["y0"] - ck["w"], s["y0"]),
                                  ("N", s["y1"], s["y1"] + ck["w"])):
                sc.add_box(stage, f"/World/Scene18/Cheek_{tag}_{i}",
                           ((xb_e + xf_e) / 2.0, (cy0 + cy1) / 2.0,
                            (c_top + ck["base_z"]) / 2.0),
                           (xf_e - xb_e, cy1 - cy0, c_top - ck["base_z"]),
                           M["upper"], collider=True)

    def build_cheek_haunch(M):
        """[v6 판정 ㉣] 치크월 사선 헌치 — 노징선 평행 상면 1장/측(scene14 방식).

        상면 z(x) = rise − (riser/tread)·x. 단별 박스 상면(−riser·(i+1))보다
        항상 0.025~0.415 m 위, 헌치 밑면(상면−thick/cos)보다는 0.08 m 이상 위 →
        **틈·부유 0**. 계단 폭(|y|<4.0) 은 건드리지 않는다."""
        s, ck = PARAMS["stair"], PARAMS["cheek"]
        k = s["riser"] / s["tread"]
        x0h = ck["haunch_x0"]
        z0h = ck["rise"] - k * x0h
        runh = s["n"] * s["tread"] - x0h + ck["haunch_over"]
        for tag, y0, y1 in (("S", s["y0"] - ck["w"], s["y0"]),
                            ("N", s["y1"], s["y1"] + ck["w"])):
            sc.build_slope(stage, f"/World/Scene18/CheekHaunch_{tag}",
                           x0h, z0h, runh, k * runh, y0, y1, ck["thick"],
                           M["upper"], margin=0.0, collider=True)

    # -------------------------------------------------------------------
    # 드레싱 — 벤치·가로등·화단·건물
    # -------------------------------------------------------------------
    def build_streetlight(M, idx, sl_i):
        sl = PARAMS["streetlight"]
        x, y, bz, ph = sl_i["x"], sl_i["y"], sl_i["base_z"], sl_i["pole_h"]
        base = f"/World/Scene18/Streetlight_{idx}"
        sc.add_cylinder(stage, f"{base}/Pole", (x, y, bz + ph / 2.0),
                        sl["pole_r"], ph, M["pole"], collider=True)
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            ax = x + sgn * sl["arm_len"] / 2.0
            sc.add_cylinder(stage, f"{base}/Arm_{tag}",
                            (ax, y, bz + ph - 0.1),
                            sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
            hx = x + sgn * sl["arm_len"]
            sc.add_box(stage, f"{base}/Head_{tag}", (hx, y, bz + ph - 0.15),
                       (sl["head"], sl["head"], 0.12), M["lamp"])

    def build_seaside(M):
        """[v5.1 현실성] **바닷가 언덕 벽화계단** 정체성 확정 레이어.

        구성 (좌표 근거는 PARAMS["seaside"] 주석):
          ① 바다 — 해안선(지반 동단 x=34) 밑 x 31 부터 500 m 뻗는 수면 평판,
             상면 −3.35(지반 상면보다 0.34 m 아래) + 헤이즈 톤 저채도 재질.
             [v6] 저시점에서도 수평선이 지붕 위가 아니라 **지반 너머**로 뜬다.
          ② 호안 산책로 — x 29.5..34 폭 4.5 m(잔디가 바다에 직접 닿지 않게).
          ③ 저층 마을 13동 — 계단 조망축(|y| < 13)을 **비우고** 남·북 군락
             (x 17..32.5, h 3.0~5.6)으로. 프레임 좌우를 채워 원경을 닫는다.
          ④ 언덕 — 계단 **위쪽(−X)** 성토 3단(상면 1.4 / 4.6 / 8.2) +
             그 위 주택 17동. 상가 D/E(x −24..−15, h 5.0/6.2)를 넘겨다본다.
        위험 기하(물결 계단·치크월·보도)와 좌표가 겹치는 요소는 없다
        (최근접 town x0 = 17.0 → 하부 보도 동단 x1 = 16.0 에서 1.0 m,
         y 는 ±13 밖이라 평면상 이격은 13 m 이상).
        """
        sea = PARAMS["seaside"]
        w = sea["water"]
        sc.add_box(stage, "/World/Scene18/Sea",
                   ((w["x0"] + w["x1"]) / 2.0, (w["y0"] + w["y1"]) / 2.0,
                    w["top_z"] - w["thick"] / 2.0),
                   (w["x1"] - w["x0"], w["y1"] - w["y0"], w["thick"]),
                   M["sea"])
        gz = PARAMS["ground"]["top_z"]
        # [v6] 호안 산책로 — 잔디가 바다에 직접 닿는 인상 제거(폭 4.5 m).
        #   상면은 지반보다 5 mm 만 높다(코플래너 Z파이팅 회피).
        q = PARAMS["quay"]
        sc.add_box(stage, "/World/Scene18/Quay",
                   ((q["x0"] + q["x1"]) / 2.0, (q["y0"] + q["y1"]) / 2.0,
                    (q["top_z"] + gz - 0.4) / 2.0),
                   (q["x1"] - q["x0"], q["y1"] - q["y0"],
                    q["top_z"] - (gz - 0.4)), M["lower"])
        rf = sea["roof"]
        for i, (x0, x1, y0, y1, h, fl) in enumerate(sea["town"]):
            sc.build_building(
                stage, f"/World/Scene18/Town_{i}",
                dict(x0=x0, x1=x1, y0=y0, y1=y1, h=h, floors=fl,
                     axis="x", facade_x=x0, face_dir=-1.0, base_z=gz),
                M[f"house_{i % M['nvar']}"], M["glass"],
                M[f"roof_{(i * 3) % M['nvar']}"])
            sc.add_box(stage, f"/World/Scene18/TownRoof_{i}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                        gz + h + rf["t"] / 2.0),
                       (x1 - x0 + 2 * rf["over"], y1 - y0 + 2 * rf["over"],
                        rf["t"]), M[f"roof_{(i * 3) % M['nvar']}"])
        ty0, ty1 = sea["terrace_y"]
        for i, (x0, x1, top) in enumerate(sea["terraces"]):
            sc.add_box(stage, f"/World/Scene18/HillTerrace_{i}",
                       ((x0 + x1) / 2.0, (ty0 + ty1) / 2.0,
                        (top + gz - 1.0) / 2.0),
                       (x1 - x0, ty1 - ty0, top - (gz - 1.0)), M["grass"])
        for i, (x0, x1, y0, y1, bz, h) in enumerate(sea["houses"]):
            sc.add_box(stage, f"/World/Scene18/Hill_{i}/Body",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, bz + h / 2.0),
                       (x1 - x0, y1 - y0, h),
                       M[f"house_{(i * 2 + 1) % M['nvar']}"])
            sc.add_box(stage, f"/World/Scene18/Hill_{i}/Roof",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                        bz + h + rf["t"] / 2.0),
                       (x1 - x0 + 2 * rf["over"], y1 - y0 + 2 * rf["over"],
                        rf["t"]), M[f"roof_{(i + 2) % M['nvar']}"])

    def build_dressing(M):
        """맥락 드레싱 — 판독어 "바닷가 언덕 벽화계단이 있는 항구 마을".
        기존 빌더(build_bench/planter/building) 조합 + build_seaside."""
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for j, (cx, cy, bz, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"/World/Scene18/Bench_{j}", cx, cy, bz,
                           M["wood"], yaw=yaw)
        for i, sl_i in enumerate(PARAMS["streetlights"]):
            build_streetlight(M, i, sl_i)
        for name, px, py, bz in PARAMS["planters"]:
            sc.build_planter(stage, f"/World/Scene18/Planter_{name}", px, py, bz,
                             M["parapet"], M["grass"], tree_mtls=tree_mtls)
        # [v5.1] 볼라드 8본 삭제 (§2 근거 없음 — PARAMS["bollards"] 항목 제거)
        build_seaside(M)
        # 상부 보도 |y| 4.2..9 에지 파라펫 — 스커트(−2.57)로의 2.57 m 낙차 방호
        pa = PARAMS["parapet"]
        for tag, y0, y1 in (("S", -pa["y_out"], -pa["y_in"]),
                            ("N", pa["y_in"], pa["y_out"])):
            sc.add_box(stage, f"/World/Scene18/Parapet_{tag}",
                       ((pa["x0"] + pa["x1"]) / 2.0, (y0 + y1) / 2.0,
                        pa["h"] / 2.0),
                       (pa["x1"] - pa["x0"], y1 - y0, pa["h"]),
                       M["parapet"], collider=True)
        # 하부 광장 바닥 밴드 2줄 (광장 스케일 지시 — 어두운 상수색 0.045)
        band = sc.make_pbr(stage, "/World/Looks/Band",
                           diffuse_color=(0.045, 0.045, 0.05),
                           roughness_const=0.8)
        lo = PARAMS["lower"]
        for k, bx in enumerate(PARAMS["bands"]):
            sc.add_box(stage, f"/World/Scene18/Band_{k}",
                       (bx, (lo["y0"] + lo["y1"]) / 2.0, lo["top_z"] - 0.01),
                       (0.45, lo["y1"] - lo["y0"], 0.04), band)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"/World/Scene18/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"])

    # -------------------------------------------------------------------
    # 단서 토글 (기하 불변)
    # -------------------------------------------------------------------
    def build_cues(M):
        s = PARAMS["stair"]
        yc, Wb = _seg_centers()
        # cue_tactile: 상단 접근 경고 점자띠
        if cfg.get("cue_tactile"):
            tac = sc.make_pbr(stage, "/World/Looks/Tactile",
                              diffuse_color=(0.85, 0.72, 0.10),
                              roughness_const=0.7)
            sc.build_tactile(stage, "/World/Scene18/Tactile",
                             -0.6, -0.2, s["y0"], s["y1"], tac, z=0.0)
        # cue_nosing: 물결 단코 논슬립(각 세그 전연 상수색 띠) — 기본 False
        if cfg.get("cue_nosing"):
            nos = sc.make_pbr(stage, "/World/Looks/Nosing",
                              diffuse_color=mp["nosing_color"],
                              roughness_const=mp["nosing_rough"])
            for i in range(s["n"]):
                z_top = -s["riser"] * (i + 1)
                for j in range(s["nseg"]):
                    y = yc[j]
                    xf = _front_x(i, y)
                    sy0 = s["y0"] + j * Wb - 0.001
                    sy1 = s["y0"] + (j + 1) * Wb + 0.001
                    sc.add_box(stage, f"/World/Scene18/Nosing_{i}_{j}",
                               (xf - 0.03, (sy0 + sy1) / 2.0, z_top + 0.004),
                               (0.06, sy1 - sy0, 0.01), nos)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hazard = cfg["hazard_stairs"]
    build_ground(M)
    build_walkways(M, hazard)
    if hazard:
        build_stair(M)
        build_cheek_haunch(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if hazard:
        build_cues(M)
    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        nprim = sum(1 for pr in stage.Traverse() if pr.IsA(UsdGeom.Gprim))
        print(f"SMOKE_OK prims={nprim}")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

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

    VIEWS = build_views()
    _v0 = VIEWS["wave_raking"]
    look_from(_v0["eye"], _v0["tgt"])

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    if capture_mode:
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
                            set_render_mode, look_from)
        simulation_app.close()
        return

    from omni.kit.viewport.utility import get_active_viewport, \
        capture_viewport_to_file

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene18_{ts}.png")
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
