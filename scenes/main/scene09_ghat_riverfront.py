# -*- coding: utf-8 -*-
"""
scene09_ghat_riverfront.py — NegObs 인공씬 9호: 호수공원 수변 계단
(Isaac Sim 4.5)

사양서 : Docs/briefs/multi_scene_brief_v5.md §R4 (구 v3 §D scene09 를 대체)
공통 라이브러리 : scene_common.py / 골격 관례 : scene03_riverbank.py

[v5 채택] 무대 재해석: 인도 '가트' → **호수공원 수변 관람 계단**.
  ** 기하 전면 불변 ** — 계단 36단·riser 테이블·참 2·제방·수면 z 전부 그대로.
  드레싱만 교체해 종교색을 제거한다:
    가트 파빌리온(차트리) 2 → 수변 정자 1(사모정: 기둥 4 + 모임지붕)
    계선주 8            → 데크 말뚝 8 (r 0.13→0.09, h 1.1→0.50)
    나룻배 2            → 오리배 1 (백색 박스 선체 + 머리 근사)
    (신규) 목재 산책 데크 접속 · 갈대 군락 · sign_info(호수공원 안내)
    (신규) 이끼 틴트 — 수면 바로 아래 2단(물때 밴드와 함께 수위 이력 표현)

[v6 판정 재수정] "의도 불명 미해소" — 재해석 요소가 **코드에만 있고 어떤 컷에도
  안 잡혔다**. 계단·수면 기하는 그대로 두고 판독 4축을 전부 손본다:
  ① 정자  : 콘크리트 상자 → **목조 사모정**. 기단(석)+누마루(목)+기둥 4(목)+
            창방 + 2단 처마선 + **4면 경사 모임지붕 메시(귀솟음)** + 절병통.
            위치도 x −5.4..−1.0 / y 6.2..10.6 로 이설(수변 쪽 25 m → 13~15 m).
  ② 오리배: 박스 선체 → **회전타원체 조합**(선체·가슴·꼬리·날개) + 곡면 머리·
            부리, 황색 틴트(백색 0.86 → 0.78/0.70/0.25). y 10.5 → 3.0 로 당겨
            across_river·from_river·park_vista 세 컷 화각 안으로.
  ③ 재질  : 계단·테라스 석재를 **사암(가트 핑크베이지) → plaza_light 화강암**
            으로 교체(+ 상부 테라스 잔디 밴드 2매 · 가로수 10주) = 공원 인상.
  ④ 카메라: **park_vista 신설** — 정자·데크·잔디·계단 상단·수위선·오리배를
            한 프레임에 담는 미장센 컷(뷰 주석에 방위/앙각 검산).
  부수: 수관·원경 실루엣 알베도 상향(대안 흑색 띠 완화).

유형 (초광폭 수변 계단): **초광폭 석재 계단 × 수면 수평 경계**.
  폭 10m 화강석 계단 36단(불균등 riser 테이블)이 수변으로 하강, 중간 참 2개.
  수면이 하부 6단을 침수 → **수면이 계단 중간을 수평으로 자르는 경계**가 유일한
  고정 낙차 앵커. 물때 틴트 밴드가 수위선을 강조. T5(하천)와 구분: 전면 석재·
  초광폭·참.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene09_ghat_riverfront.py

[v7 판정 재수정] judge_v7_rt_A §6 — 담당 2건.
  ① [최우선 버그] 정자 모임지붕 메시가 **알베도 지정과 정반대로 근백색**
     (176,179,186) — 같은 재질 절병통(107,116,128) 대비 1.6배.
     → `build_hip_roof` 의 **법선 미저작**이 원인(스무딩 법선이 21.8° 경사면과
       수직 처마밴드를 뭉개 '흰 천막'으로 셰이딩). faceVarying 면법선 저작 +
       orientation/doubleSided 명시. 검산 `roof_normal_selfcheck()`:
       기하상 램버트 상한비는 1.10배뿐 → 실측 1.6배는 법선 문제로 확정.
  ② 석재 톤 교체가 **순백 대면적**으로 착지(포장 223 · §4 위반).
     → `stone_tint` 0.90 → 0.64(권고 0.62~0.68). 물때·이끼 틴트는 **대비비를
       보존**하며 같은 비율로 하향(수위선 = 이 씬의 유일한 낙차 앵커).
  ③ (공통) §4 순백 대면적 자가검사 `albedo_selfcheck()` 신설.
  미조치(범위 밖): 판정 ㉢ `ghat_walk` 재조준 · ㉣ 대안 흑색 실루엣 상향.

[v8 판정 재수정 — Y1] judge_v8_rt §4 ① "지붕 셰이딩 픽셀 무변화(0 델타)".
  **v7 의 법선 가설은 기각되었다.** v7↔v8 지붕 픽셀 diff 0.0 % 가 그 증거이고,
  실제로는 **법선 저작 전부터 이미 평면(면법선) 셰이딩이 걸려 있었다** —
  v8 렌더에 능선이 각지게 서 있고 그늘면(-X)이 별도 계조로 갈라진다.
  ⇒ 재작성한 faceVarying 법선이 렌더러가 이미 쓰던 값과 동일 → 0 델타.

  **진짜 원인 = `M["pav_roof"]` 만 `specular_level` 미지정(OmniPBR 기본 0.5).**
  근거 3개(전부 기존 v8_rt PNG 실측 · 렌더 불요):
   ⓐ 바인딩·법선은 결백. v8 스모크 로그가 Roof/Finial 모두
     `/World/Looks/PavRoof` · normals 64 faceVarying 로 이미 찍혀 있다.
   ⓑ **확산만으로는 수치가 안 맞는다.** park_vista 에서 보이는 지붕면은
     +Y군(램버트 0.840)과 −X군(0.508) 둘뿐인데, 이 둘을 `resp = S·lam + K`
     로 적합하면 **K = −0.87**(음의 앰비언트) — 물리적으로 불가능.
     ⇒ 램버트로 설명 안 되는 **시선의존 항**이 반드시 있다.
   ⓒ 로브 밖 면(−X, N·H 0.39~0.48)과 수평 포장을 확산 앵커로 잡으면
     S 1.360 / K 0.749 → +Y면 확산 예측 응답 **1.892**(씬 `_ALBEDO_GAIN`
     1.77 과 일치) → 예측 sRGB (147,152,160). 실측은 (180,183,190).
     **초과분이 3채널 모두 +0.164 선형으로 동일** = 알베도 오차가 아니라
     **가산 반사항**. park_vista 시선의 하프벡터는 +Y면에서 N·H 0.78~0.79
     (38°) — roughness 0.72 의 넓은 GGX 로브 정중앙이다.
   ⓓ 절병통이 어두웠던 이유도 같다. 원기둥은 법선이 연속 스윕이라 로브에
     드는 것이 **가느다란 한 줄**뿐 — 실측도 밝은 열 157~163, 몸통 111.
     판정의 "같은 재질 1.6배"는 지붕의 **정반사 가산면**과 절병통의
     **확산 몸통**을 비교한 것이었다(로브 열끼리 비교하면 1.20배 = 기하 상한 내).
  조치 ①: `pav_roof` 에 `specular_level=0.0` — 한식 기와(무유약)는 무광이고,
    이 씬의 다른 무광 재질(reed/far/canopy_a/canopy_b)은 전부 이미 0.0 이다.
    `pav_roof` 만 빠져 있었다.
  조치 ②: `roof_tile_color` ×0.70 → (0.109,0.116,0.130). 실제 암회색 무유약
    기와 반사율 0.10~0.15 대역. ①만으로는 (147,152,160) = 여전히 밝은 회색.
  예측(위 S/K 모델): +Y 지붕면 (125,129,136) · −X 지붕면 (110,114,120) ·
    처마밴드 (103,106,111)/(81,83,88) → 처마밴드 < 지붕면 순서도 성립.
  ※ 판정 대안 폴백(_oriented_box 4장 재구성)은 **채택하지 않았다** — 메시가
    범인이 아니므로(평면 셰이딩·바인딩 정상) 박스로 바꿔도 같은 재질·같은
    방위면 정반사 가산분이 그대로 남고, 귀솟음만 잃는다.

자동 캡처 : NEGOBS_CAPTURE=1 python scene09_ghat_riverfront.py
조립 스모크: NEGOBS_SMOKE=1 python scene09_ghat_riverfront.py
자가검사   : NEGOBS_SELFCHECK=1 python scene09_ghat_riverfront.py  (부팅 없음)

좌표계: Z-up, m, 진행축 +X(강 쪽으로 하강). 계단 상단 = x=0(z=0).

────────────────────────────────────────────────────────────────────────────
기하 핵심 (감독 보충 반영):
  · riser 테이블 = [0.14,0.16,0.18,0.20,0.18,0.16] 반복(고정 리스트, 0.14~0.20),
    tread 0.34. 중간 참 2 = 12·24단째 tread 를 1.2 로(깊은 디딤=참).
  · 계단 상면 z 를 직접 누적 계산 → **수면 z = 하부에서 6단째 상면 +0.05**
    (하부 6단이 수면 아래가 되게). 브리프의 z≈-4.2 는 근사 힌트, 수식이 우선.
  · 침수부: 수면 위 1.5단 대역의 단은 **별도 물때 재질(석재 텍스처 + stain_tint)**
    로 교체 — 기하 불변(단별 add_box 재질만 분기).
────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. 가트 계단엔 난간 미관행(cue_railing 기본 False).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False → 계단·둔치를 z=0 평지로
    "cue_railing":        False,   # 수변 관람 계단 무난간(관행) — 코드 경로만 예약
    # [v5] 비관행(수변 데크) 씬 → cue_tactile 은 False 유지 (브리프 v5 공통 레이어)
    "cue_tactile":        False,   # 미사용(코드 경로만)
    "cue_material_break": True,    # 상부 테라스 vs 계단 재질 대비(둘 다 화강암,
                                   #   테라스는 tint 미적용). False→테라스도 stain 톤
    "cue_sign":           True,    # [v5 공통 레이어] sign_info(호수공원 안내) 1매
    "cue_scene_dressing": True,    # 정자·데크 말뚝·산책 데크·갈대·건너편 숲 일괄
    "cue_nosing":         False,   # 미사용(코드 경로만)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
# riser 불균등 테이블(0.14~0.20 반복) — 고정 리스트로 재현성 보장
_RISER_CYCLE = [0.14, 0.16, 0.18, 0.20, 0.18, 0.16]   # 합 1.02 / 6단
_RISER_MU = sum(_RISER_CYCLE) / len(_RISER_CYCLE)       # 0.17

PARAMS = dict(
    stairs=dict(x0=0.0, nsteps=36, tread=0.34, y0=-5.0, y1=5.0, z_top=0.0,
                base_pad=0.6,                  # base_z = 최하단 상면 - base_pad
                landing_steps=[11, 23],        # 12·24단째(0-based) = 중간 참
                landing_tread=1.2,             # 참 깊이
                submerge_from_bottom=6,         # 하부 6단 침수(수위 산정 기준)
                stain_band_steps=1.5),          # 수면 위 1.5단 대역 물때 틴트
    water_extra=0.05,                          # 수면 z = 6단째 상면 + 0.05
    # 상부 테라스(사암 평탄, z=0). [A-09-2] x0 −12 → −30: d10 그리드 뷰(eye x=−10)
    #   뒤가 곧 허공이던 것을 해소.
    terrace=dict(x0=-30.0, x1=0.0, y0=-40.0, y1=40.0, z_top=0.0, thick=0.5),
    # 좌우 제방 : [A-09-1] build_slope(선형 평면) → **계단과 동일 riser 테이블의
    #   계단식**으로 교체. 선형 사면 대 이산 단의 z 차가 y=±5 경계선을 따라
    #   최대 0.315 m(참 구간) 톱니 홈/턱을 만들었다(판정 임계 0.2 초과).
    #   같은 (xa, xb, tz, base_z)를 쓰므로 이음새 오차 = 0.
    embankment=dict(y_edge=40.0),
    # 수면 : 계단 침수선에서 강 건너까지(강폭 30m 근사)
    water=dict(x_far=44.0, y0=-40.0, y1=40.0),
    # 건너편 대안 둔치(사암) + 숲 라인
    #   [B-09-2] above_water 0.3 → 1.6 / hedge 2.0 → 3.6 / trees 3 → 8 + 건물 2:
    #   화면 상단 절반이 균일 청록('무한 수영장')이던 지평 폐쇄 실패를 해소.
    #   [v5 판정 반영] thick 0.6 → 2.4: 저면이 fb_z − thick = water_z + 1.6 − 0.6
    #   = −4.19 로 수면(−5.19) 위 1.0 m 부유 → 슬래브 밑으로 하늘이 새어 전 수면
    #   컷의 지평에 하드에지 백색 띠(RGB 183–197)가 생겼다. 2.4 면 저면이
    #   water_z − 0.8 로 확실히 잠기고, 상면 z(fb_z)는 불변이라 B-09-2 지평
    #   폐쇄 효과·헤지/수목/건물 base_z 도 그대로다.
    far_bank=dict(x0=44.0, x1=74.0, y0=-40.0, y1=40.0, above_water=1.6,
                  thick=2.4),
    far_hedge=dict(cx=52.0, sx=1.4, length=24.0, h=3.6),
    far_hedges=[dict(cy=-24.0), dict(cy=0.0), dict(cy=24.0)],
    far_trees=[dict(cx=56.0, cy=-28.0), dict(cx=57.5, cy=-20.0),
               dict(cx=55.5, cy=-11.0), dict(cx=57.0, cy=-3.0),
               dict(cx=55.5, cy=5.0), dict(cx=57.5, cy=13.0),
               dict(cx=56.0, cy=21.0), dict(cx=57.0, cy=29.0)],
    # 대안 건물 실루엣 2 (어두운 상수색) — 3단 깊이의 원경 층
    far_buildings=[dict(x0=66.0, x1=72.0, cy=14.0, sy=12.0, h=7.0),
                   dict(x0=66.0, x1=72.0, cy=-14.0, sy=12.0, h=7.0)],
    # [v5 채택] 계선주(mooring) → **수변 경계 말뚝**: 종교·나루터 색을 지우고
    #   수변 공원 계단머리 경계 말뚝으로 축소. r 0.13→0.09, h 1.1→0.50.
    #   [v6] |y| 8.5 쌍 삭제 — 신설 정자 처마(x −7.25..−1.15, y 5.35..11.45)
    #   아래로 들어가 자리가 겹친다. 남은 6본은 간격이 3.8/9.7/5.5 로 비등간격
    #   (§3 등간격 금지)이 되어 오히려 정합.
    mooring=[dict(cx=-1.2, cy=3.8), dict(cx=-1.2, cy=-3.8),
             dict(cx=-1.2, cy=13.5), dict(cx=-1.2, cy=-13.5),
             dict(cx=-1.2, cy=19.0), dict(cx=-1.2, cy=-19.0)],
    mooring_r=0.09, mooring_h=0.50,

    # --- 맥락 드레싱 (판독어 "호수공원 수변 계단") ---
    # [v6 재수정 ①] 수변 정자(사모정) — 구 "무채색 콘크리트 상자" 판정 해소.
    #   실물 비례 근거(한국 전통 목조 사모정 관행 치수):
    #     주칸(기둥 중심 간격) 4.4 m · 기둥 지름 0.26(주칸의 1/17)
    #     기둥 높이 2.30(주칸의 0.52) · 처마 내밀기 0.85(기둥 높이의 0.37)
    #     지붕 물매 = rise 1.15 / 처마 반폭 3.05 → 20.7°(전통 4~5치 물매 근사)
    #     귀솟음(추녀 들림) 0.16 · 절병통 r0.11 h0.42
    #   구 파라미터(z_roof/roof_t/cap_shrink/cap_t)는 평판 지붕 전용이라 폐기.
    #   위치 이설 : 구 (x −9.0..−5.8, y 6.4..9.6) 은 from_river/across_river 에서
    #     25~30 m 원경(화면 폭 6 %)이라 판독 불가였다. 계단 상단 쪽으로 당기고
    #     한 변을 3.2 → 4.4 m 로 키운다 → from_river 29.4 m 에서 화면 폭 20 %,
    #     across_river 33.2 m 에서 17 %, 신설 park_vista 14.9 m 에서 39 %.
    #   안전 : y0 6.6 > 계단 폭 5.0 (1.6 m 이격) · 기단 외밀기 포함 x1 = −1.54,
    #     **처마 끝**(가장 돌출)조차 x −1.15 / y 5.75 → 계단 상단 모서리(x=0)에서
    #     1.15 m · 계단 폭 경계에서 0.75 m, 접지물 0 → **위험 기하 불변**.
    #   그리드 프리셋 화각 검산(eye x −2/−5/−10 @ y=0, ±30°): 처마 최근접 모서리
    #     (−1.15, 5.75) 의 방위가 81.6° / 56.2° / **33.0°** = 전부 화각 밖 →
    #     **은닉 프리셋에 정자 미진입**(grazing 은닉 무영향).
    #     ghat_walk(−4,0) 도 63.6° 로 밖.
    pavilion=dict(x0=-6.4, x1=-2.0, y0=6.6, y1=11.0,
                  base_t=0.22, base_over=0.46,      # 석재 기단
                  floor_t=0.23, floor_over=0.30,    # 목재 누마루
                  post_r=0.13, post_h=2.30,         # 기둥 4
                  beam_t=0.20, beam_w=0.15,         # 창방(기둥머리 가로보)
                  eave_over=0.85, eave_t=0.10,      # 처마선 1단(서까래층)
                  fascia_inset=0.18, fascia_t=0.09,  # 처마선 2단(부연/기와 처마)
                  roof_rise=1.15, corner_lift=0.16,  # 4면 경사 + 귀솟음
                  finial_r=0.11, finial_h=0.42,
                  rail_h=0.44, rail_t=0.07, rail_post_r=0.035, rail_n=3),
    # 참(landing) 표식 석주 4 — 계단 폭(y±5) 밖. 초광폭 스케일·참 위치 판독용
    land_posts=dict(r=0.24, h=2.1, ys=(-5.6, 5.6)),
    # [v6 재수정 ③] 상부 테라스 잔디 밴드 2매 — "공원"의 근거를 프레임에 넣는다.
    #   계단 폭(y±5) 밖 · 테라스(x −30..0, y ±40) 안. 상면 0.03 돌출(보행 연속).
    #   판독 경로: park_vista 에서 좌·우 잔디면, from_river/across_river 에서는
    #   테라스 마루선 위로 **가로수 수관만** 솟아 녹지 스카이라인이 된다.
    lawns=[dict(x0=-24.0, x1=-0.8, y0=12.0, y1=30.0),
           dict(x0=-24.0, x1=-0.8, y0=-30.0, y1=-12.0)],
    lawn_proud=0.03,
    # 가로수 10주 — 잔디 밴드 위, 비정형 배치(§3 격자·등간격 금지).
    #   park_vista(eye −9.6, 22) 최근접 6.1 m 이며 전부 화각 ±30° 밖 →
    #   전경 침입 0. from_river(23.92,0)/across_river(27.96,0) 에서는
    #   방위 −18.9°~+25.7° 로 프레임 안(수관 앙각 11.4°, 반수직 ±18° 내).
    park_trees=[(-13.4, 17.2), (-19.8, 15.0), (-16.4, 24.6),
                (-22.6, 21.8), (-12.2, 27.4),
                (-13.0, -17.8), (-19.2, -15.6), (-16.8, -25.0),
                (-22.2, -22.4), (-12.6, -27.0)],
    # 벤치 4 (강 조망) — [§3] 앵커(정자·잔디 밴드 가장자리·데크) 옆 · yaw 지터
    #   0/1 : 정자 기단 북/남면(|y| 11.46)에서 1.14 m, 잔디 밴드 시작선(|y| 12) 위
    #   2/3 : 데크 서측(x0 −10.0)에서 1.0 m, 잔디 밴드 위
    benches=[(-4.6, 12.6, 86.5), (-4.6, -12.6, 274.0),
             (-11.0, 13.4, 93.5), (-11.0, -13.4, 265.5)],
    # [v6 재수정 ②] 오리배 1 — 박스 조합 → **회전타원체(구 스케일) 조합**.
    #   판정: "백색 무텍스처 박스 + 판때기 목" → 선체·가슴·꼬리·날개를 곡면으로,
    #   차양은 두꺼운 박스(h 0.45) → 얇은 판(0.05) + 지주 4로 교체.
    #   위치 (18.5, 10.5) → **(15.4, 3.0)** : 판정 "across_river 기준 방위 47.9°
    #     로 화각 밖 / ghat_walk 좌상단 반쯤 잘림" 해소. 재검산(화각 ±30°,
    #     선체 전장 3.07 m 의 양끝까지 포함):
    #       from_river(23.92,0)  −19.4° (9.03 m, −29.0..−9.8°)  전부 안
    #       across_river(27.96,0) −13.4° (12.91 m, −20.2..−6.6°) 전부 안
    #       park_vista(−10.2,22)  +20.6° (31.9 m, +17.9..+23.3°) 전부 안
    #   방위 rotz 62° : 두 수면 컷의 시선(−25.4° / 152.3°)과 각각 87°/90° →
    #     **양쪽에서 측면 실루엣**(오리 판독이 가장 쉬운 각).
    #   계단 간섭 : rotz 62° 회전 후 선체 최후단 x = 15.4 − (1.525·cos62 +
    #     0.69·sin62) = 14.08 → 최하단 단(x1 13.96)과 평면 0.12 m 이격.
    #     설령 평면이 겹쳐도 침수단 상면(−6.12) 대 선저(water_z − 0.24 = −5.43)
    #     로 **연직 0.69 m 이격** → 접촉 0. 계단·수면 기하 불변.
    boats=[dict(cx=15.4, cy=3.0, rotz=62.0)],
    boat=dict(hull=(1.30, 0.62, 0.36),      # 선체 반경(회전타원체 스케일)
              breast=(0.62, 0.52, 0.42), stern=(0.42, 0.34, 0.26),
              wing=(0.62, 0.14, 0.24), wing_dy=0.55,
              neck_r=0.115, neck_h=0.60, neck_lean=12.0,
              head=(0.24, 0.20, 0.20), beak=(0.30, 0.13, 0.09),
              canopy=(1.15, 1.10, 0.05), canopy_post_r=0.03,
              hull_float=0.12),             # 선체 중심이 수면 위로 뜨는 양
    # [v5 채택] 목재 산책 데크 — 상부 테라스 수변 산책로.
    #   [v6] x −4.0..−1.6 → **−10.0..−7.6** : 신설 정자(기단 x −6.86..−1.54)와
    #   자리를 맞바꾼다. 정자 기단과 0.74 m 이격, 계단 상단(x=0)에서 7.6 m
    #   이격 → 위험 기하 여유 오히려 증가.
    #   [v6] 판 이음선 간격 2.0 → 0.62 m : 판폭 2 m 는 '나무 바닥'으로 읽혔다.
    #   0.62 m 는 데크재 3~4장 묶음 폭 = 원경에서도 널결이 서는 최소 밀도.
    deck=dict(x0=-10.0, x1=-7.6, y0=-22.0, y1=22.0, top_z=0.06,
              seam_step=0.62, seam_w=0.035, seam_drop=0.010),
    # [v5 채택] 갈대 군락 — 수위선 부근 제방(계단 폭 y±5 **밖**)과 대안 둔치.
    #   (cx, cy, n, seed). x 12.2~13.6 = 수위선(water_x0≈11.92) 바로 아래 →
    #   갈대가 수면에서 솟은 그림. 위험 기하(계단 y±5)와 무간섭.
    reeds=[(12.2, -8.5, 9, 11), (12.9, -13.0, 11, 12), (12.2, -18.0, 9, 13),
           (13.6, -24.0, 12, 14),
           (12.2, 8.5, 9, 21), (12.9, 13.0, 11, 22), (12.2, 18.0, 9, 23),
           (13.6, 24.0, 12, 24),
           (45.6, -14.0, 10, 41), (45.6, 14.0, 10, 42)],
    reed=dict(r=0.022, h_lo=1.1, h_hi=1.9, spread=0.85, tilt=9.0),
    # [v5 공통 레이어] 한글 사인 — (태그, TEX 키, cx, cy, base_z, yaw, w, h)
    #   [v6] Info (−6.5, 5.5) → **(−7.0, −5.6)** : +Y 측은 정자(기단 y 5.74~)와
    #     데크(x −10.0..−7.6)가 채워 여지가 없다 → 대칭 위치인 남측으로 이설.
    #     데크 동단에서 0.6 m, 계단 폭(y±5) 밖 0.6 m.
    #   카메라 검산(화각 ±30°): 그리드 eye=(−2/−5/−10, 0) → 후방 / 후방 /
    #     −61.8°(밖), ghat_walk(−4,0) −118.2°(밖), waterline 은 +X 수면측 → 후방.
    #     from_river(23.92,0) +10.3°(31.4 m 원경) · park_vista −26.2°(27.8 m,
    #     프레임 좌하) = 안내판이 미장센 컷에 들어오되 시선 차폐 0.
    signs=[("Info", "sign_info", -7.0, -5.6, 0.0, 180.0, 1.0, 0.75)],

    material=dict(
        # [v6 재수정 ③] 석재 역할 sandstone → **plaza_light**(밝은 화강암 포장).
        #   인도 가트의 핑크베이지 사암이 "가트" 판독을 유지시킨 주범이었다.
        #   위험 기하·은닉 성질에는 영향 없음(전 단 + 테라스 + 제방이 동일 재질
        #   이라 균질성 그대로). scale 1.5 → 1.1 (화강암 판석 타일 크기).
        scale=dict(stone=1.1, grass=1.4, wood_dark=0.9, wood_fine=0.45),
        # [v7 판정 §6 ③] 석재 톤 교체가 **순백 대면적**으로 착지했다.
        #   `ghat_walk` 포장 RGB (223,222,221) · 프레임 65 % 점유,
        #   `from_river` 는 36단이 "백색 옹벽 한 장"으로 뭉쳐 단 분절 소멸.
        #   판정 권고 ㉡ 0.86 → 0.62~0.68 하향을 그대로 채택(0.64 계열).
        #   plaza_light diff 선형평균 0.469 × 0.64 = **알베도 0.300**
        #   (실제 회색 화강암 0.2~0.35 대역) → 예상 렌더 sRGB 0.75 ≈ 191.
        #   ** 기하·은닉 성질 불변 ** — 전 단·테라스·제방이 여전히 동일 재질.
        stone_tint=(0.64, 0.63, 0.60),         # 구 (0.90,0.89,0.86)
        # [v5 채택] 이끼 틴트 — 수면 바로 아래 2단(수위 변동 이력의 '젖은 구간').
        # [v7] stone_tint 하향(0.90→0.64)에 맞춰 **대비비를 보존**한다.
        #   구 moss/stone = 0.30/0.90 = 0.333 → 신 0.64×0.333 = 0.213.
        #   (절대값만 낮추면 수위선 단서가 같이 죽는다 — 이 씬의 유일한 낙차 앵커)
        moss_tint=(0.213, 0.284, 0.185),       # 구 (0.30,0.40,0.26)
        deck_tint=(0.95, 0.88, 0.78),          # 목재 산책 데크(회색 풍화 목)
        seam_color=(0.030, 0.026, 0.022),      # 데크 판 이음선(암색 규칙)
        # [v6 ①] 정자 목부재 — 기둥·창방·난간(적갈 소나무) / 누마루(밝은 마루널)
        pav_wood_tint=(0.68, 0.44, 0.28), pav_floor_tint=(0.78, 0.60, 0.42),
        # [v8 판정 §4 ①] 지붕 근백색의 실체는 **정반사 가산분**이었다(모듈
        #   독스트링 [v8 Y1] ⓑⓒ). `specular_level=0.0` 로 그 항을 끄면 확산만
        #   남아 (147,152,160) — 여전히 밝은 회색이라 알베도도 ×0.70 내린다.
        #   0.109~0.130 = 실측 암회색 무유약 기와 반사율 0.10~0.15 대역.
        #   색비(1 : 1.064 : 1.193)는 그대로 보존.
        roof_tile_color=(0.109, 0.116, 0.130), roof_tile_rough=0.72,  # 한식 기와
        roof_tile_specular=0.0,                # [v8 Y1] 원인 — 아래 주석 참조
        # [v6 ②] 오리배 — 백색(0.86) → 황색(§4 순백 상한 0.8 이하)
        duck_color=(0.78, 0.70, 0.25), duck_rough=0.45,
        duck_top_color=(0.52, 0.19, 0.17), duck_top_rough=0.55,  # 차양(적색)
        beak_color=(0.74, 0.42, 0.07), beak_rough=0.5,
        # [v6 부수] 0.055/0.065/0.030 → 상향. 갈대가 흑색 침엽으로 뭉쳤다.
        reed_color=(0.110, 0.125, 0.060), reed_rough=1.0,
        # [B-09-4] 0.55 → 0.42: 물때 밴드가 사암 텍스처 변화보다 약해 수위선이
        #   식별되지 않았다. (석재 교체 후에도 대비량은 동일하게 유지)
        # [v7] 동일 사유로 대비비 보존: 구 0.42/0.90 = 0.467 → 0.64×0.467 = 0.299
        stain_tint=(0.299, 0.299, 0.263),      # 구 (0.42,0.42,0.37)
        grass_tint=(0.55, 0.68, 0.42),
        # [B-09-3] rough 0.10 → 0.15 (균일 밝은 청록 클리핑 완화)
        water_color=(0.06, 0.11, 0.12), water_rough=0.15,
        # [B-09-1] 0.34 → 0.10: 정오 직달 2450 에서 계선주가 완전 백색(PVC 파이프)
        post_color=(0.10, 0.085, 0.07), post_rough=0.8,
        # [v6 부수] 판정 "대안 전체가 무텍스처 흑색 실루엣(p5 5.2/8.8)".
        #   원경 실루엣·수관 알베도를 실측 식생 반사율(6~12 %) 대역으로 올린다.
        far_color=(0.130, 0.125, 0.118),       # 원경 건물 실루엣
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.055, 0.085, 0.035), canopy_b=(0.075, 0.115, 0.045),
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
    # 감독 r1 — 표준 171.5(az205)는 +X향 라이저를 음영에 넣어 정면 사암 계단이
    # 흑색 실루엣이 됨. → offset 0.0(az33.5)로 +X향 라이저 정면광(사암이 삶).
    SUN_AZ_OFFSET=0.0,

    # [v8 Y1] park_vista 카메라 = **단일 출처**. build_views(조립기)와
    #   roof_specular_selfcheck(검산기)가 같은 좌표를 쓰게 한다
    #   (scene04 `verge_instances` 규약). roof_z = 지붕면 무게중심 z
    #   = z_fa 3.05 + fascia 0.09 + rise/3 0.383 ≒ 3.52.
    views_park_vista=dict(eye=[-10.2, 22.0, 3.8], tgt=[4.0, 0.0, -1.8],
                          roof_z=3.52),

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene09")

# [v6 재수정 ③] sandstone → plaza_light (밝은 화강암 포장)
ASSET_ROLES = ["plaza_light", "grass", "wood_dark", "sign_info", "hdri", "mdl"]


# ===========================================================================
# 계단 기하 사전계산 — (xa, xb, top_z) 리스트 + 수위·물때 밴드
# ===========================================================================
def compute_steps():
    st = PARAMS["stairs"]
    n = st["nsteps"]
    risers = [_RISER_CYCLE[i % len(_RISER_CYCLE)] for i in range(n)]
    treads = [st["tread"]] * n
    for li in st["landing_steps"]:
        treads[li] = st["landing_tread"]
    steps = []
    xa = float(st["x0"])
    z = float(st["z_top"])
    for i in range(n):
        z -= risers[i]                         # i단 상면(디딤면) z
        xb = xa + treads[i]
        steps.append((xa, xb, z))
        xa = xb
    z_bot = steps[-1][2]
    base_z = z_bot - st["base_pad"]
    # 수면 z = 하부에서 k단째 상면 + water_extra
    k = st["submerge_from_bottom"]
    idx6 = n - k                               # 하부 6단째의 인덱스(0-based)
    water_z = steps[idx6][2] + PARAMS["water_extra"]
    band_hi = water_z + st["stain_band_steps"] * _RISER_MU
    return steps, base_z, z_bot, water_z, band_hi


# ===========================================================================
# [C2] [v7 판정 §6 ②] 모임지붕 커스텀 메시 — 토폴로지 + 법선 (모듈 레벨)
# ---------------------------------------------------------------------------
# 증상: `park_vista` 지붕면 RGB (176,179,186) 인데 **같은 재질**(`M["pav_roof"]`,
#   알베도 0.155/0.165/0.185 = 한식 기와 암회색)을 쓴 절병통 원기둥은
#   (107,116,128). 동일 광원·동일 재질에서 1.6배 → 기와가 아니라 흰 천막.
# 원인: `UsdGeom.Mesh` 에 **normals 미저작**. 저작이 없으면 Hydra 가 인접면
#   평균(스무딩) 법선을 추정하는데, 이 지붕은 21.8° 경사면 8장과 **수직**
#   처마밴드 8장이 처마링 T[0..7] 을 공유한다. 두 그룹의 평균 법선은 처마
#   부근을 통째로 하늘 쪽으로 들어 올려, 각진 기와지붕이 **부풀린 천막/
#   파라솔**로 셰이딩된다(= 판정 표현 그대로). `sc.add_cylinder`/`add_box` 는
#   내장 프림이라 법선이 스키마로 확정되므로 이 문제가 없다 → 메시 경로 한정.
# 조치: 면 법선을 **faceVarying** 으로 명시 저작(평면 셰이딩 강제) +
#   orientation/doubleSided 명시. 와인딩·법선 방향은 렌더 없이 수치로 검산
#   (`roof_normal_selfcheck`) — 조립기와 검산기가 같은 좌표를 쓰도록
#   토폴로지 생성을 모듈 레벨로 분리한다(scene04 `verge_instances` 규약).
#
# ---------------------------------------------------------------------------
# [v8 판정 §4 ① — Y1] **위 v7 원인 진단은 오진이었다.** 아래를 정본으로 본다.
#   · v7↔v8 지붕 픽셀 diff **0.0 %**. 법선을 저작해도 렌더가 1비트도 안 변했다
#     = 렌더러는 **저작 전부터 이미 같은 면법선**을 쓰고 있었다(RTX 는
#     subdivisionScheme="none" 메시에서 면법선을 쓴다). 실제로 v8 PNG 에서
#     능선이 각지게 서 있고 −X 그늘면이 +Y 면과 별도 계조로 갈라져 있다.
#   · 따라서 이 블록의 법선 저작·검산은 **무해하지만 무효과**다. 유지하는
#     이유는 렌더러 기본값에 의존하지 않게 고정하는 방어 코드로서다.
#   · 진짜 원인은 재질의 **정반사(specular) 가산분** — 모듈 독스트링
#     [v8 판정 재수정 — Y1] ⓐ~ⓓ 참조. 아래 `roof_normal_selfcheck` 의
#     ④ 항이 v8 실측으로 갱신되어 그 분리 근거를 수치로 남긴다.
# ===========================================================================
def hip_roof_topology(cx, cy, sx, sy, z_bot, band, rise, lift):
    """모임지붕(사모지붕) 메시의 (points, faceVertexCounts, faceVertexIndices,
    z_top, z_apex). 좌표 정의는 build_hip_roof 독스트링 참조."""
    hx, hy = sx / 2.0, sy / 2.0
    ring = [(cx + hx, cy + hy, lift), (cx, cy + hy, 0.0),
            (cx - hx, cy + hy, lift), (cx - hx, cy, 0.0),
            (cx - hx, cy - hy, lift), (cx, cy - hy, 0.0),
            (cx + hx, cy - hy, lift), (cx + hx, cy, 0.0)]
    z_top = z_bot + band
    z_apex = z_top + rise
    pts = [(px, py, z_bot) for px, py, _ in ring]            # B 0..7
    pts += [(px, py, z_top + dz) for px, py, dz in ring]     # T 8..15
    pts.append((cx, cy, z_apex))                             # A 16
    counts, idx = [], []
    for i in range(8):                       # 지붕면 8삼각형
        counts.append(3)
        idx += [8 + i, 8 + (i + 1) % 8, 16]
    for i in range(8):                       # 처마 밴드 8쿼드
        counts.append(4)
        idx += [i, (i + 1) % 8, 8 + (i + 1) % 8, 8 + i]
    counts.append(8)                         # 밑면
    idx += [7, 6, 5, 4, 3, 2, 1, 0]
    return pts, counts, idx, z_top, z_apex


def _newell(poly):
    """다각형의 단위 법선(Newell 법) — 볼록/오목·비평면 모두 안정.
    USD 기본 orientation=rightHanded 와 동일한 부호 규약."""
    nx = ny = nz = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0, z0 = poly[i]
        x1, y1, z1 = poly[(i + 1) % n]
        nx += (y0 - y1) * (z0 + z1)
        ny += (z0 - z1) * (x0 + x1)
        nz += (x0 - x1) * (y0 + y1)
    L = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return (nx / L, ny / L, nz / L)


def hip_roof_face_normals(pts, counts, idx):
    """면 순서대로의 단위 면법선 리스트."""
    out, o = [], 0
    for c in counts:
        out.append(_newell([pts[i] for i in idx[o:o + c]]))
        o += c
    return out


def _sun_dir():
    """DistantLight 진행 방향 d(월드) — setup_lighting 의 op 순서 역산
    (기본 −Z → rotateX(90−elev) → rotateZ(rz)). 면이 받는 직달 램버트는
    max(0, −d·n)."""
    lp = PARAMS["light"]
    rz = math.radians(lp["noon_dome_rot"] + PARAMS["SUN_AZ_OFFSET"]
                      + lp["hdri_sun_rotz_offset"])
    rx = math.radians(90.0 - lp["noon_sun_elev"])
    return (-math.sin(rx) * math.sin(rz),
            math.sin(rx) * math.cos(rz),
            -math.cos(rx))


def roof_normal_selfcheck(verbose=True):
    """[v7 §6 ②] 지붕 메시 법선 검산 — **렌더 없이** 방향·램버트를 수치로 확인.

    ① 지붕면 8: 법선 z>0 이고 수평성분이 축에서 바깥을 향하는가(외향).
    ② 처마밴드 8: 법선이 수평(|nz|<1e-6)이고 외향인가.
    ③ 밑면 1: 법선이 (0,0,−1) 인가.
    ④ 절병통(원기둥) 대비: 같은 재질이 왜 다르게 보였는지의 정량 근거 —
       지붕면 평균 램버트 vs 원기둥 측면 최대 램버트 비. 이 비를 넘는
       밝기 차이는 재질/법선 문제이지 기하 문제가 아니다.
    반환 (ok, diag)."""
    p = PARAMS["pavilion"]
    cx = (p["x0"] + p["x1"]) / 2.0
    cy = (p["y0"] + p["y1"]) / 2.0
    sx, sy = p["x1"] - p["x0"], p["y1"] - p["y0"]
    z_ev = (p["base_t"] + p["floor_t"] + p["post_h"] + p["beam_t"]
            + p["eave_t"])
    fx = sx + 2 * p["eave_over"] - 2 * p["fascia_inset"]
    fy = sy + 2 * p["eave_over"] - 2 * p["fascia_inset"]
    pts, counts, idx, _z_top, z_apex = hip_roof_topology(
        cx, cy, fx, fy, z_ev, p["fascia_t"], p["roof_rise"], p["corner_lift"])
    nrm = hip_roof_face_normals(pts, counts, idx)
    d = _sun_dir()
    # 면별 무게중심 → 외향 판정
    cents, o = [], 0
    for c in counts:
        poly = [pts[i] for i in idx[o:o + c]]
        o += c
        cents.append((sum(q[0] for q in poly) / c,
                      sum(q[1] for q in poly) / c))
    bad = []
    for f, n in enumerate(nrm):
        gx, gy = cents[f][0] - cx, cents[f][1] - cy
        out = n[0] * gx + n[1] * gy
        if f < 8:                                   # 지붕면
            if not (n[2] > 0.0 and out > 0.0):
                bad.append(("roof", f, n))
        elif f < 16:                                # 처마 밴드
            if not (abs(n[2]) < 1e-6 and out > 0.0):
                bad.append(("band", f, n))
        else:                                       # 밑면
            if n[2] > -0.999999:
                bad.append(("bottom", f, n))
    lam_roof = [max(0.0, -(d[0] * n[0] + d[1] * n[1] + d[2] * n[2]))
                for n in nrm[:8]]
    lam_r = sum(lam_roof) / 8.0
    lam_cyl_side = math.hypot(d[0], d[1])           # 원기둥 측면 최대 램버트
    slope = math.degrees(math.atan2(p["roof_rise"], fx / 2.0))
    ok = not bad
    if verbose:
        print("=" * 68)
        print("scene09 [v7] 모임지붕 메시 법선 검산 (렌더 없음)")
        print("=" * 68)
        print(f"  면 구성            지붕 8삼각 + 처마밴드 8쿼드 + 밑면 1 "
              f"= {len(counts)}면 / 정점 {len(pts)}")
        print(f"  지붕 경사          {slope:.1f}° (rise {p['roof_rise']:.2f} / "
              f"반폭 {fx/2.0:.2f}) · 용마루 z {z_apex:.2f}")
        print(f"  ① 지붕면 법선      nz>0 & 외향 → "
              f"{'OK' if not any(b[0]=='roof' for b in bad) else 'FAIL'}"
              f"   (예: {nrm[0][0]:+.3f},{nrm[0][1]:+.3f},{nrm[0][2]:+.3f})")
        print(f"  ② 처마밴드 법선    수평 & 외향 → "
              f"{'OK' if not any(b[0]=='band' for b in bad) else 'FAIL'}"
              f"   (예: {nrm[8][0]:+.3f},{nrm[8][1]:+.3f},{nrm[8][2]:+.3f})")
        print(f"  ③ 밑면 법선        (0,0,−1) → "
              f"{'OK' if not any(b[0]=='bottom' for b in bad) else 'FAIL'}"
              f"   ({nrm[16][0]:+.3f},{nrm[16][1]:+.3f},{nrm[16][2]:+.3f})")
        print(f"  ④ 램버트(직달)     지붕면 평균 {lam_r:.3f} · "
              f"절병통 측면 최대 {lam_cyl_side:.3f} → 기하상 상한비 "
              f"{lam_r / max(lam_cyl_side, 1e-6):.2f}배")
        print(f"     ※ [v8 정정] v7 은 여기서 '초과분 = 스무딩 법선'으로 "
              f"결론냈으나 **오진**이었다.")
        print(f"       v7↔v8 지붕 픽셀 diff 0.0 % = 법선은 저작 전부터 이미 "
              f"면법선이었다. 실체는 ⑤.")
        if bad:
            for kind, f, n in bad:
                print(f"     [FAIL] {kind} face{f} n={n}")
        roof_specular_selfcheck(nrm, cx, cy, verbose=True)
        print("=" * 68)
    return ok, dict(n_faces=len(counts), lam_roof=lam_r,
                    lam_cyl=lam_cyl_side, bad=bad)


# ---------------------------------------------------------------------------
# [C2-b] [v8 판정 §4 ① — Y1] 지붕 정반사 진단 (렌더 없음)
#   v8_rt/rt_noon_park_vista.png 실측을 상수로 박아 두고, "확산만" 모델과
#   비교해 초과분이 남는지를 **부팅 없이** 재현한다. 다음 라운드에서 누가
#   다시 열어도 같은 수치를 보게 하는 것이 목적(교훈: 같은 1줄로 2라운드 소모).
# ---------------------------------------------------------------------------
# park_vista 실측(v7·v8 동일): +Y 지붕면 (180,183,190) · −X 지붕면 (130,134,144)
#                              포장(수평, 알베도 0.300) 193.5
_V8_MEAS = dict(roof_pY=(180.2, 183.1, 189.9), roof_mX=(130.0, 134.0, 144.0),
                pav=193.5, pav_albedo=0.300)


def _lin(s):
    """sRGB(0..255) → 선형."""
    u = max(0.0, min(1.0, s / 255.0))
    return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4


def roof_specular_selfcheck(nrm, cx, cy, verbose=True):
    """지붕 근백색이 **알베도가 아니라 정반사 가산분**임을 수치로 분리한다.

    ① park_vista 에서 보이는 지붕면은 +Y군(face0,1)·−X군(face2,3) 둘뿐.
    ② 이 둘만으로 `resp = S·lam + K` 를 풀면 K<0 (음의 앰비언트) = 불가능
       ⇒ 램버트로 설명 안 되는 **시선의존 항**이 존재.
    ③ 로브 밖 면(−X)과 수평 포장을 확산 앵커로 다시 풀면 S/K 가 양수로
       나오고, +Y면 확산 예측 응답이 `_ALBEDO_GAIN` 과 일치한다.
       실측 − 예측 = 3채널 동일한 **가산** 값 → 정반사.
    ④ GGX 하프벡터 N·H 로 +Y군만 로브 안임을 확인.
    반환 (ok, diag). ok = "정반사 항이 검출됐고 specular_level 이 0.0 인가".
    """
    v = PARAMS["views_park_vista"]
    d = _sun_dir()
    lam = [max(0.0, -(d[0] * n[0] + d[1] * n[1] + d[2] * n[2])) for n in nrm]
    lam_pY = (lam[0] + lam[1]) / 2.0
    lam_mX = (lam[2] + lam[3]) / 2.0
    lam_h = -d[2]
    alb = PARAMS["material"]["roof_tile_color"]
    m = _V8_MEAS
    # ② 지붕 2면만으로 적합 → K<0 이면 시선의존 항 존재
    r_pY = _lin(m["roof_pY"][0]) / 0.155      # v8 당시 알베도 R = 0.155
    r_mX = _lin(m["roof_mX"][0]) / 0.155
    S_bad = (r_pY - r_mX) / (lam_pY - lam_mX)
    K_bad = r_pY - S_bad * lam_pY
    # ③ 로브 밖 면 + 수평 포장 = 확산 앵커
    r_pav = _lin(m["pav"]) / m["pav_albedo"]
    S = (r_pav - r_mX) / (lam_h - lam_mX)
    K = r_pav - S * lam_h
    resp_pY = S * lam_pY + K
    excess = [_lin(c) - a * resp_pY for c, a in zip(m["roof_pY"],
                                                    (0.155, 0.165, 0.185))]
    # ④ 하프벡터
    eye = v["eye"]
    px, py, pz = cx, cy, v["roof_z"]
    vv = [eye[0] - px, eye[1] - py, eye[2] - pz]
    lv = [-d[0], -d[1], -d[2]]
    nh = []
    for arr in (vv, lv):
        L = math.sqrt(sum(q * q for q in arr)) or 1.0
        arr[:] = [q / L for q in arr]
    h = [vv[i] + lv[i] for i in range(3)]
    L = math.sqrt(sum(q * q for q in h)) or 1.0
    h = [q / L for q in h]
    for f in range(4):
        nh.append(sum(nrm[f][i] * h[i] for i in range(3)))
    spec_off = PARAMS["material"].get("roof_tile_specular", 0.0) == 0.0
    ok = (K_bad < 0.0) and spec_off
    if verbose:
        print(f"  ⑤ [v8] 정반사 분리   park_vista 가시면 = +Y군(lam "
              f"{lam_pY:.3f}) · −X군(lam {lam_mX:.3f})")
        print(f"     ⓑ 확산만 적합      S {S_bad:+.3f} / K {K_bad:+.3f} → "
              f"K<0 = 음의 앰비언트 ⇒ **시선의존 항 존재** "
              f"{'OK' if K_bad < 0 else 'FAIL'}")
        print(f"     ⓒ 로브 밖 재적합   S {S:+.3f} / K {K:+.3f} → +Y면 확산 "
              f"응답 {resp_pY:.3f} (GAIN {_ALBEDO_GAIN})")
        print(f"        실측−확산예측   {excess[0]:+.4f} / {excess[1]:+.4f} / "
              f"{excess[2]:+.4f} (선형) = 3채널 동일 **가산 반사항**")
        print(f"     ⓓ 하프벡터 N·H     +Y {nh[0]:+.3f},{nh[1]:+.3f} vs "
              f"−X {nh[2]:+.3f},{nh[3]:+.3f} → +Y군만 GGX 로브 안"
              f"(rough {PARAMS['material']['roof_tile_rough']})")
        print(f"     ⑥ 조치 반영        specular_level 0.0 "
              f"{'OK' if spec_off else 'FAIL'} · roof_tile_color "
              f"{alb[0]:.3f}/{alb[1]:.3f}/{alb[2]:.3f}")
        for tag, lm in (("+Y 지붕면", lam_pY), ("−X 지붕면", lam_mX),
                        ("+Y 처마밴드", lam[8]), ("−X 처마밴드", lam[10])):
            pr = [_srgb(a * (S * lm + K)) * 255.0 for a in alb]
            print(f"        예측 sRGB {tag:11s} "
                  f"({pr[0]:5.1f},{pr[1]:5.1f},{pr[2]:5.1f})")
    return ok, dict(S_bad=S_bad, K_bad=K_bad, S=S, K=K,
                    resp_pY=resp_pY, excess=excess, nh=nh)


# ===========================================================================
# [C3] [v7 판정 §11-6] §4 "순백(>0.8) 대면적 금지" 알베도 상한 자가검사
# ---------------------------------------------------------------------------
# 이번 라운드에 09 포장·18 광장·19 지붕에서 동시 발생 → 판정관이 "개별 지적
# 대신 알베도 상한 전역 검사 스크립트를 스모크에 추가할 것"을 권고.
# **렌더 없이** 재질 정의만으로 두 기준을 함께 본다(05/09/12 공통 규약):
#   (A) 알베도 상한 : 유효 알베도 max 채널 > CAP(0.80) → v5.1 §4 문자 위반.
#   (B) 렌더 예측   : **수평 대면적**(포장·데크·지붕 상면·잔디)에 한해
#       예상 렌더 sRGB = sRGB(알베도 × GAIN) > PRED_CAP(0.87 ≒ 222).
#       GAIN 1.77 = v7_rt 실측 역산: 이 씬 `ghat_walk` 포장 알베도
#       0.469×0.90 = 0.422 → 렌더 (223,222,221) = 선형 0.738.
#       (돔 1000 + 태양 2450 · elev 49.79 동일 리그를 쓰는 05/09/12 공통값)
#       수직면은 일사·천공 가시율이 달라 (B) 미적용.
#   유효 알베도 = 상수색 그대로 | diff 텍스처 선형평균 × 틴트.
#   ※ (A) 만으로는 이번 09 포장(알베도 0.422)을 못 잡고, (B) 만으로는 수직
#      순백 판(19 파라펫류)을 못 잡는다 — 두 기준이 함께 있어야 한다.
# ===========================================================================
_ALBEDO_GAIN = 1.77          # 정오 직달 순광 수평면, v7_rt 실측 역산
_ALBEDO_CAP = 0.80           # v5.1 §4 "순백(>0.8) 대면적 금지"
_ALBEDO_PRED_CAP = 0.87      # 판정관이 "순백 대면적"으로 지적한 실측(223/220) 직하
_TEXMEAN_CACHE = {}


def _tex_lin_mean(role):
    """diff 텍스처의 선형(sRGB 해제) 채널평균. PIL 없거나 파일 없으면 None."""
    if role in _TEXMEAN_CACHE:
        return _TEXMEAN_CACHE[role]
    val = None
    try:
        from PIL import Image
        im = Image.open(sc.tex_path(role, "diff")).convert("RGB")
        im.thumbnail((192, 192))
        a = np.asarray(im, dtype=np.float64) / 255.0
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        val = tuple(float(v) for v in lin.mean(axis=(0, 1)))
    except Exception:
        val = None
    _TEXMEAN_CACHE[role] = val
    return val


def _srgb(u):
    u = max(0.0, min(1.0, u))
    return 12.92 * u if u <= 0.0031308 else 1.055 * u ** (1 / 2.4) - 0.055


# (라벨, 텍스처 role|None, material 키, 대면적, 수평면)
_ALBEDO_TABLE = [
    ("계단·테라스·제방 석재", "plaza_light", "stone_tint",      True,  True),
    ("물때(수위선) 밴드",     "plaza_light", "stain_tint",      True,  True),
    ("상부 잔디 밴드",        "grass",       "grass_tint",      True,  True),
    ("산책 데크(목)",         "wood_dark",   "deck_tint",       True,  True),
    ("정자 기와지붕",         None,          "roof_tile_color", True,  True),
    ("정자 누마루(목)",       "wood_dark",   "pav_floor_tint",  False, True),
    ("오리배 선체",           None,          "duck_color",      False, False),
    ("원경 건물 실루엣",      None,          "far_color",       True,  False),
]


def albedo_selfcheck(verbose=True):
    """[v7 §4/§11-6] 순백 대면적 자가검사. (A) 알베도 > 0.80 또는
    (B) 수평 대면적의 예상 렌더 sRGB > 0.87 이면 위반. 대면적 FAIL /
    소면적 WARN. 반환 (ok, rows)."""
    mp = PARAMS["material"]
    rows, fails, warns = [], [], []
    for label, role, key, wide, horiz in _ALBEDO_TABLE:
        v = mp.get(key)
        if v is None:
            continue
        base = (1.0, 1.0, 1.0) if role is None else _tex_lin_mean(role)
        if base is None:
            rows.append((label, key, None, None, "SKIP(텍스처 없음)"))
            continue
        alb = max(b * t for b, t in zip(base, v))
        pred = _srgb(alb * _ALBEDO_GAIN) if horiz else None
        why = []
        if alb > _ALBEDO_CAP:
            why.append("A:알베도")
        if pred is not None and pred > _ALBEDO_PRED_CAP:
            why.append("B:렌더예측")
        if why:
            mark = "/".join(why)
            (fails if wide else warns).append(label)
            tag = (f"FAIL 대면적({mark})" if wide
                   else f"WARN 소면적({mark})")
        else:
            tag = "OK"
        rows.append((label, key, alb, pred, tag))
    ok = not fails
    if verbose:
        print("=" * 68)
        print("scene09 [v7 §4] 순백 대면적 알베도 상한 자가검사 "
              f"(CAP {_ALBEDO_CAP} · 수평 렌더예측 CAP {_ALBEDO_PRED_CAP} "
              f"· GAIN {_ALBEDO_GAIN})")
        print("=" * 68)
        for label, key, alb, pred, tag in rows:
            if alb is None:
                print(f"  {label:22s} {key:18s} {tag}")
                continue
            pr = f"{pred*255:5.1f}" if pred is not None else "  수직"
            print(f"  {label:22s} {key:18s} 알베도 {alb:.3f} · "
                  f"수평 예상 렌더 {pr}  {tag}")
        print(f"  ⇒ {'OK — 대면적 위반 0건' if ok else 'FAIL: ' + str(fails)}"
              f"{'  (WARN: ' + str(warns) + ')' if warns else ''}")
        print("=" * 68)
    return ok, rows


# ===========================================================================
# [D] 카메라 프리셋
# ===========================================================================
def build_views(run, z_bot, water_z, water_x0):
    views = sc.grid_views(0.0)
    # ghat_walk: 상부 테라스에서 강 쪽 — 수면이 계단 중간을 자르는 경계 확인
    views["ghat_walk"] = dict(eye=[-4.0, 0.0, 1.4], tgt=[8.0, 0.0, water_z + 0.8])
    # waterline: 수면 수평 경계에 눈높이 근접(특색 포인트)
    views["waterline"] = dict(eye=[water_x0 - 3.0, 4.0, water_z + 1.2],
                              tgt=[water_x0 + 2.0, 0.0, water_z])
    # from_river: 강 위 근거리에서 계단 정면 올려봄(초광폭·참·수위선)
    views["from_river"] = dict(eye=[water_x0 + 12.0, 0.0, water_z + 1.6],
                               tgt=[2.0, 0.0, -1.0])
    # across_river: 감독 r1 — 강 중앙 수면 위(h1.5)에서 가트 정면을 담게 재조준
    #   (기존엔 far_bank 만 봐 가트가 프레임 밖). 강폭 물면 반사 + 수위 경계 포함.
    river_mid = (water_x0 + PARAMS["water"]["x_far"]) / 2.0
    views["across_river"] = dict(eye=[river_mid, 0.0, water_z + 1.5],
                                 tgt=[2.0, 0.0, -1.0])
    # [v6 재수정 ④] park_vista — 판정이 요구한 **재해석 미장센 컷**.
    #   "정자 + 데크 + 수면 + 계단 상단을 한 프레임에" (판정 수정안 1).
    #   판정 예시안 eye(4,16,2)→tgt(−7,5,−0.5) 은 역산 결과 **수면이 프레임 밖**
    #   (수위선 x 11.92 가 방위 +80.8°)이라 채용하지 않고, 산책 데크 서측
    #   잔디 밴드 위(x −10.2, y 22)에서 남동을 부감하는 축으로 재설계했다.
    #   화각 ±30°(수평)·±18°(수직), 시선 방위 −57.2° / 피치 −12.1°
    #   → 프레임 방위 [−87.2, −27.2] · 앙각 [−30.1, +5.9]
    #   역산(요소 = 방위차 / 거리 / 앙각):
    #     수변 정자 (−4.2, 8.8)    −8.4°  14.50 m  절병통 끝 +3.6° (처마 ±11.9°)
    #     산책 데크 (x −8.8 축)    −24.9°~−28.8°  10~20 m       → 좌측 유도선
    #     잔디 밴드 N/S            프레임 좌·우 녹지면           → "공원" 근거
    #     계단 상단 모서리 (0, 5)  −1.9°  19.83 m  −10.9°        → 프레임 중앙
    #     수위선 (11.92, 0)        +12.3° 31.20 m  −16.1°        → 수면 경계
    #     오리배 (15.4, 3.0)       +20.6° 31.88 m  −13.1°        → 우측
    #     sign_info (−7.0, −5.6)   −26.2° 27.78 m                → 좌하
    #     대안 지평                                −7.0°         → 프레임 상부
    #   근접(<6 m) 침입 0 : 최근접 가로수 (−13.4, 17.2) 5.77 m 이나 방위차
    #   −66.5° 로 화각 밖. 벤치 0(−4.6, 12.6) 은 −2.1° / 10.94 m 중경(높이
    #   0.45 → 앙각 −17.0°)이라 정자(절병통 +3.6°)를 가리지 않는다.
    #   [의도] 정자 방위폭(−22.6°~+8.9°)이 계단 상단 모서리(−1.9°)를 품는다.
    #   가림이 아니라 **개방 정자 너머로 계단·수면을 보는 구도**다 — 시선 검산:
    #   (0,5) 로 가는 광선은 y 11.85 에서 z 1.53, y 5.75 에서 z 0.17 로 지나
    #   난간 상단(마루+0.44 → z 0.89)과 창방 밑(z 2.75) 사이 **빈 칸을 관통**하고,
    #   기둥 4(x −6.27/−2.13, y 6.73/10.87)와 최소 2.1 m 이격한다. 계단 상단
    #   모서리(앙각 −10.9°)는 정자 마루 끝단(−11.4°)보다 **위**라 프레임에 남는다.
    #   [v8 Y1] 좌표는 PARAMS["views_park_vista"] 단일 출처(검산기 공유).
    _pv = PARAMS["views_park_vista"]
    views["park_vista"] = dict(eye=list(_pv["eye"]), tgt=list(_pv["tgt"]))
    return views


# ===========================================================================
# [E] 메인
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. ghat_walk    — 수면이 계단 중간을 수평으로 자르는 경계가 낙차 앵커인가
                  (뷰 키는 판정 파일명 연속성 때문에 v4 이름 유지)
 2. waterline    — 물때 밴드(수면 위 1.5단) + 이끼(수면 아래 2단) 수위 이력
 3. from_river   — 초광폭 36단 + 중간 참 2개가 정면에서 읽히나
 4. h0.3·d5~10   — 상부 테라스가 평지로 보이고 낙차 증거가 수면뿐인가
 5. across_river — 대안 둔치(+1.6)+숲+건물 실루엣이 지평을 막는가
 6. cue_railing OFF/ON — 위험 기하(계단) 트랜스폼 동일한가
 7. 이음새       — y=±5 경계에 톱니 홈/턱이 없는가 (제방 계단식 정합)
 8. [v5] 맥락    — 정자·데크 말뚝·오리배·산책 데크·갈대·안내판이
                   '호수공원'으로 읽히나 (종교색 잔존 0)
 9. [v6] park_vista — 목조 사모정(4면 경사 지붕·귀솟음)·데크 널결·잔디 밴드·
                   황색 오리배가 **한 프레임**에서 동시에 판독되나
10. [v8] 지붕 셰이딩 — park_vista 에서 +Y 지붕면이 (125,129,136) 대역
                   (구 180,183,190 = 흰 천막)으로 내려오고 −X 그늘면
                   (110,114,120)·처마밴드(103/81)와 **밝기 순서**가 서는가.
                   원인은 법선이 아니라 `specular_level` 미지정이었다
11. [v7] 석재 톤   — ghat_walk 포장이 순백(223)에서 회색 화강암(≈192)으로
                   내려오고, from_river 36단의 **단 분절**이 되살아났는가.
                   물때(수위선)·이끼 밴드 대비는 그대로인가(대비비 보존)"""


def main():
    smoke = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # [v7] 부팅 없이 도는 순수 파이썬 자가검사 (지붕 법선 · §4 알베도 상한).
    #   NEGOBS_SELFCHECK=1 python scene09_ghat_riverfront.py
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        ok1, _ = roof_normal_selfcheck()
        ok2, _ = albedo_selfcheck()
        sys.exit(0 if (ok1 and ok2) else 1)

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode or smoke)

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
    UsdGeom.Xform.Define(stage, "/World/Scene09")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene09"

    steps, base_z, z_bot, water_z, band_hi = compute_steps()
    run = steps[-1][1]
    # 수면 침수선 x : 하부에서 6단째 시작 xa(대략 수위선)
    water_x0 = steps[PARAMS["stairs"]["nsteps"]
                     - PARAMS["stairs"]["submerge_from_bottom"]][0]

    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        M = {}
        # [v6 재수정 ③] 석재 = plaza_light(밝은 화강암). 구 sandstone 폐기.
        M["stone"] = tex("plaza_light", "/World/Looks/Stone", sca["stone"],
                         tint=mp["stone_tint"])
        # 물때(수위선) — 동일 텍스처에 어두운 tint (기하 불변, 재질만 분기)
        M["stain"] = tex("plaza_light", "/World/Looks/StoneStain",
                         sca["stone"], tint=mp["stain_tint"])
        # [v5 채택] 이끼 — 수면 바로 아래 2단. 기하 불변, 재질만 분기.
        M["moss"] = tex("plaza_light", "/World/Looks/StoneMoss",
                        sca["stone"], tint=mp["moss_tint"])
        M["deck"] = tex("wood_dark", "/World/Looks/Deck", sca["wood_dark"],
                        tint=mp["deck_tint"])
        M["seam"] = sc.make_pbr(stage, "/World/Looks/Seam",
                                diffuse_color=mp["seam_color"],
                                roughness_const=0.9)
        # [v6 ①] 정자 목부재 2종 + 기와 1종
        M["pav_wood"] = tex("wood_dark", "/World/Looks/PavWood",
                            sca["wood_fine"], tint=mp["pav_wood_tint"])
        M["pav_floor"] = tex("wood_dark", "/World/Looks/PavFloor",
                             sca["wood_fine"], tint=mp["pav_floor_tint"])
        # [v8 Y1] specular_level=0.0 — 지붕 근백색의 **원인**. 미지정 시
        #   OmniPBR 기본 0.5(F0 0.04)이고 roughness 0.72 의 넓은 GGX 로브가
        #   park_vista 시선에서 +Y 지붕면(N·H 0.78)에 태양+천공을 그대로 담아
        #   확산 위에 선형 +0.164 를 가산했다. 이 씬의 다른 무광 재질
        #   (reed/far/canopy_a/canopy_b)은 전부 0.0 인데 pav_roof 만 빠져 있었다.
        M["pav_roof"] = sc.make_pbr(stage, "/World/Looks/PavRoof",
                                    diffuse_color=mp["roof_tile_color"],
                                    roughness_const=mp["roof_tile_rough"],
                                    specular_level=mp["roof_tile_specular"])
        M["duck"] = sc.make_pbr(stage, "/World/Looks/Duck",
                                diffuse_color=mp["duck_color"],
                                roughness_const=mp["duck_rough"])
        M["duck_top"] = sc.make_pbr(stage, "/World/Looks/DuckTop",
                                    diffuse_color=mp["duck_top_color"],
                                    roughness_const=mp["duck_top_rough"])
        M["beak"] = sc.make_pbr(stage, "/World/Looks/Beak",
                                diffuse_color=mp["beak_color"],
                                roughness_const=mp["beak_rough"])
        M["reed"] = sc.make_pbr(stage, "/World/Looks/Reed",
                                diffuse_color=mp["reed_color"],
                                roughness_const=mp["reed_rough"],
                                specular_level=0.0)
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["water"] = sc.make_pbr(stage, "/World/Looks/Water",
                                 diffuse_color=mp["water_color"],
                                 roughness_const=mp["water_rough"],
                                 metallic=0.0)
        M["post"] = sc.make_pbr(stage, "/World/Looks/Post",
                                diffuse_color=mp["post_color"],
                                roughness_const=mp["post_rough"])
        M["far"] = sc.make_pbr(stage, "/World/Looks/Far",
                               diffuse_color=mp["far_color"],
                               roughness_const=0.95, specular_level=0.0)
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
        return M

    # -------------------------------------------------------------------
    # 초광폭 계단 — 단별 add_box, 물때 밴드는 재질만 분기(기하 불변)
    # -------------------------------------------------------------------
    st_p = PARAMS["stairs"]
    # [v5 채택] 이끼 단 = 수면 바로 아래 2단(= 침수 시작 단과 그 다음 단).
    _MOSS_IDX = (st_p["nsteps"] - st_p["submerge_from_bottom"],
                 st_p["nsteps"] - st_p["submerge_from_bottom"] + 1)

    def _step_mtl(M, tz, default, idx=None):
        """수면 위 1.5단 대역(수위선)이면 물때, 수면 아래 2단이면 이끼 재질.
        **기하 불변 — 재질만 분기**(단별 add_box 의 mtl 인자)."""
        if idx is not None and idx in _MOSS_IDX:
            return M["moss"]
        return M["stain"] if (water_z - 0.01) < tz <= band_hi else default

    def build_stairs(M):
        st = PARAMS["stairs"]
        cy = (st["y0"] + st["y1"]) / 2.0
        Ly = st["y1"] - st["y0"]
        default = M["stone"] if cfg["cue_material_break"] else M["stain"]
        n_stain = 0
        for i, (xa, xb, tz) in enumerate(steps):
            mtl = _step_mtl(M, tz, default, i)
            if mtl is M["stain"] and default is not M["stain"]:
                n_stain += 1
            cx = (xa + xb) / 2.0
            cz = (tz + base_z) / 2.0
            hz = tz - base_z
            sc.add_box(stage, f"{ROOT}/Step_{i}", (cx, cy, cz),
                       (xb - xa, Ly, hz), mtl, collider=True)
        print(f"[기하] 가트 {len(steps)}단 run={run:.3f} z_bot={z_bot:.3f} "
              f"water_z={water_z:.3f} 물때단={n_stain} 참={st['landing_steps']}")

    def build_terrace(M):
        """상부 사암 테라스 (z=0)."""
        tr = PARAMS["terrace"]
        sc.add_box(stage, f"{ROOT}/Terrace",
                   ((tr["x0"] + tr["x1"]) / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
                    tr["z_top"] - tr["thick"] / 2.0),
                   (tr["x1"] - tr["x0"], tr["y1"] - tr["y0"], tr["thick"]),
                   M["stone"], collider=True)

    def build_embankment(M):
        """[A-09-1] 좌우 제방 — 계단과 **동일 단 테이블**의 계단식 확장.
        단별 (xa, xb, tz, base_z)를 그대로 재사용하므로 y=±5 이음새의 z 차이가
        구조적으로 0 이다(기존 선형 사면은 최대 0.315 m 톱니). 결과적으로 폭 80 m
        의 초광폭 가트가 되어 유형 정체성(T12)도 강화된다."""
        st = PARAMS["stairs"]
        em = PARAMS["embankment"]
        default = M["stone"] if cfg["cue_material_break"] else M["stain"]
        for tag, y0, y1 in (("N", -em["y_edge"], st["y0"]),
                            ("P", st["y1"], em["y_edge"])):
            cyb = (y0 + y1) / 2.0
            Lyb = y1 - y0
            for i, (xa, xb, tz) in enumerate(steps):
                sc.add_box(stage, f"{ROOT}/Embank_{tag}_{i}",
                           ((xa + xb) / 2.0, cyb, (tz + base_z) / 2.0),
                           (xb - xa, Lyb, tz - base_z),
                           _step_mtl(M, tz, default, i), collider=True)

    def build_river(M):
        """수면(계단 침수) + 대안 둔치 + 원경 숲 라인 — 지평 폐쇄·수위 경계."""
        wt = PARAMS["water"]
        sc.build_water(stage, f"{ROOT}/Water", water_x0, wt["y0"], wt["x_far"],
                       wt["y1"], water_z, mtl=M["water"])
        fb = PARAMS["far_bank"]
        fb_z = water_z + fb["above_water"]
        sc.add_box(stage, f"{ROOT}/FarBank",
                   ((fb["x0"] + fb["x1"]) / 2.0, (fb["y0"] + fb["y1"]) / 2.0,
                    fb_z - fb["thick"] / 2.0),
                   (fb["x1"] - fb["x0"], fb["y1"] - fb["y0"], fb["thick"]),
                   M["grass"], collider=True)
        fh = PARAMS["far_hedge"]
        for i, h in enumerate(PARAMS["far_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}",
                           fh["cx"] - fh["sx"] / 2.0,
                           h["cy"] - fh["length"] / 2.0,
                           fh["cx"] + fh["sx"] / 2.0,
                           h["cy"] + fh["length"] / 2.0, fh["h"], base_z=fb_z)
        for i, t in enumerate(PARAMS["far_trees"]):
            sc.build_tree(stage, f"{ROOT}/FarTree_{i}", t["cx"], t["cy"], fb_z,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        # 대안 건물 실루엣 2 (원경 층) — 지평 3단 깊이 완성
        for i, b in enumerate(PARAMS["far_buildings"]):
            sc.add_box(stage, f"{ROOT}/FarBldg_{i}",
                       ((b["x0"] + b["x1"]) / 2.0, b["cy"],
                        fb_z + b["h"] / 2.0),
                       (b["x1"] - b["x0"], b["sy"], b["h"]), M["far"],
                       collider=True)

    def _step_top_at(x):
        """x 지점의 계단(=제방) 상면 z. 갈대 접지용. 범위 밖이면 끝값."""
        if x <= steps[0][0]:
            return PARAMS["stairs"]["z_top"]
        for xa, xb, tz in steps:
            if x < xb:
                return tz
        return steps[-1][2]

    def build_hip_roof(path, cx, cy, sx, sy, z_bot, band, rise, lift, mtl):
        """[v6 재수정 ①] **모임지붕(사모지붕) 솔리드 메시** — 4면 경사 + 귀솟음.
        반환 : (mesh, z_apex).

        박스 조합이 아니라 메시인 이유:
          · 축소 박스 적층 → 원경에서 '웨딩케이크 층단'.
          · `sc.build_slope` 회전 박스 4장의 **합집합**은 상면이 각 면의 max 가
            되어 ±X/±Y 축선을 따라 정점 높이가 그대로 남는다(피라미드가 아니라
            대각선 골). 즉 4면 경사는 합집합으로 만들 수 없다.
        → 8각 처마링 + 정점 1의 각뿔을 직접 정의한다.

        3링 구성(scene14 쐐기 슬릿 교훈 = "겹침 없는 접합 금지" 적용):
          B[0..7] 밑링  z_bot 평면 8각 (부연층 밑면)
          T[0..7] 처마링 모서리 = z_bot+band+lift · 변 중점 = z_bot+band
          A       정점   z_bot+band+rise
        모서리 4점만 lift 올려 **처마선이 모서리에서 들리는 귀솟음**(추녀 곡선
        근사)을 만들되, 밑링까지 이어진 **수직 밴드 8쿼드**가 그 아래를 솔리드로
        채우므로 들린 모서리 밑에 삼각 공동이 생기지 않는다.

        와인딩: 밑링을 위에서 볼 때 반시계로 잡았으므로
          · 옆면 삼각형 (T[i], T[i+1], A)      → 법선 바깥·위
          · 밴드 쿼드   (B[i], B[i+1], T[i+1], T[i]) → 법선 바깥
          · 밑면 8각형  역순(7..0)             → 법선 아래
        subdivisionScheme='none' 고정 — 기본값 catmullClark 이면 각뿔이 둥근
        덩어리로 뭉개진다.

        [v7 판정 §6 ② — 최우선 버그] **법선 미저작 수정.**
          증상: 지붕면 (176,179,186) vs 같은 재질 절병통 (107,116,128) = 1.6배.
          원인: normals 를 안 쓰면 Hydra 가 인접면 평균(스무딩) 법선을 추정한다.
            21.8° 경사면 8장과 **수직** 처마밴드 8장이 처마링 T[0..7] 을
            공유하므로 평균 법선이 처마 부근을 하늘 쪽으로 들어 올려,
            각진 기와지붕이 **부풀린 흰 천막/파라솔**로 셰이딩된다.
          조치: 면법선을 **faceVarying**(면-정점마다 그 면의 법선)으로 명시
            저작 → 평면 셰이딩 강제. orientation·doubleSided 도 명시해
            와인딩 해석이 뷰어/렌더러 기본값에 의존하지 않게 한다.
          검산: `roof_normal_selfcheck()`(모듈 레벨, 렌더 불요) — 지붕면 nz>0·
            외향, 밴드 수평·외향, 밑면 −Z 를 좌표로 확인. 토폴로지는
            `hip_roof_topology()` 단일 출처를 조립기·검산기가 공유한다."""
        from pxr import UsdGeom, Gf, Vt
        hx, hy = sx / 2.0, sy / 2.0
        raw_pts, counts, idx, _z_top, z_apex = hip_roof_topology(
            cx, cy, sx, sy, z_bot, band, rise, lift)
        pts = [Gf.Vec3f(*p) for p in raw_pts]
        face_n = hip_roof_face_normals(raw_pts, counts, idx)
        # faceVarying = 면-정점 1개당 1법선. 면 안에서는 전부 같은 값 → 평면 셰이딩.
        normals = []
        for f, c in enumerate(counts):
            normals += [Gf.Vec3f(*face_n[f])] * c
        mesh = UsdGeom.Mesh.Define(stage, path)
        mesh.CreatePointsAttr(pts)
        mesh.CreateFaceVertexCountsAttr(counts)
        mesh.CreateFaceVertexIndicesAttr(idx)
        mesh.CreateSubdivisionSchemeAttr("none")
        mesh.CreateNormalsAttr(Vt.Vec3fArray(normals))
        mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)
        mesh.CreateOrientationAttr(UsdGeom.Tokens.rightHanded)
        mesh.CreateDoubleSidedAttr(False)
        mesh.CreateExtentAttr([Gf.Vec3f(cx - hx, cy - hy, z_bot),
                               Gf.Vec3f(cx + hx, cy + hy, z_apex)])
        sc._bind_mtl(mesh.GetPrim(), mtl)
        return mesh, z_apex

    def build_pavilion(M):
        """[v6 재수정 ①] 수변 **목조 사모정** — 구 "평판 지붕 무채색 콘크리트
        상자"(v6 판정) 전면 교체. 층 구성(아래→위):
          ① 석재 기단   base_t 0.22, 외밀기 0.46 — 지면 습기 차단(관행)
          ② 목재 누마루 floor_t 0.23, 외밀기 0.30
          ③ 기둥 4      r 0.13 · h 2.30, 마루 상면에서 창방 밑까지
          ④ 창방        기둥머리를 잇는 사각 보 4 — '목구조'의 최소 신호
          ⑤ 처마선 1단  서까래층(기둥열 밖 0.85 내밀기, 6.10 × 6.10)
          ⑥ 처마선 2단 + 모임지붕 = build_hip_roof 단일 메시(5.74 × 5.74 밴드
             0.09 + 4면 경사 rise 1.15 + 귀솟음 0.16)
          ⑦ 절병통      정점 원기둥
          ⑧ 계자난간    N/E/S 3면(서측은 진입 개방) — 하방 + 상방 + 동자 3
        높이 누적 : 0.22 + 0.23 + 2.30 + 0.20 + 0.10 = 3.05(처마 2단 밑면),
        용마루 = 3.05 + 0.09 + 1.15 = 4.29, 절병통 끝 4.71.
        위치는 계단 폭(y±5) 밖 y 6.6..11.0, 기단 외밀기 포함 x1 = −1.54,
        처마 끝 x −1.15 → **위험 기하 불변**."""
        p = PARAMS["pavilion"]
        cx = (p["x0"] + p["x1"]) / 2.0
        cy = (p["y0"] + p["y1"]) / 2.0
        sx, sy = p["x1"] - p["x0"], p["y1"] - p["y0"]
        P = f"{ROOT}/Pavilion"
        # ① 석재 기단
        bo = p["base_over"]
        sc.add_box(stage, f"{P}/Base", (cx, cy, p["base_t"] / 2.0),
                   (sx + 2 * bo, sy + 2 * bo, p["base_t"]), M["stone"],
                   collider=True)
        # ② 목재 누마루
        fo = p["floor_over"]
        z_fl = p["base_t"] + p["floor_t"]                 # 마루 상면 0.45
        sc.add_box(stage, f"{P}/Floor",
                   (cx, cy, p["base_t"] + p["floor_t"] / 2.0),
                   (sx + 2 * fo, sy + 2 * fo, p["floor_t"]), M["pav_floor"],
                   collider=True)
        # ③ 기둥 4 (모서리에서 반경만큼 안쪽 = 주칸 4.4 유지)
        pr, ph = p["post_r"], p["post_h"]
        posts = ((p["x0"] + pr, p["y0"] + pr, "SW"),
                 (p["x0"] + pr, p["y1"] - pr, "NW"),
                 (p["x1"] - pr, p["y0"] + pr, "SE"),
                 (p["x1"] - pr, p["y1"] - pr, "NE"))
        for px, py, tag in posts:
            sc.add_cylinder(stage, f"{P}/Post_{tag}", (px, py, z_fl + ph / 2.0),
                            pr, ph, M["pav_wood"], collider=True)
        # ④ 창방 — 기둥머리 사각 보 4
        z_bm = z_fl + ph                                  # 2.75
        bt, bw = p["beam_t"], p["beam_w"]
        for tag, yy in (("N", p["y1"] - pr), ("S", p["y0"] + pr)):
            sc.add_box(stage, f"{P}/Beam_{tag}", (cx, yy, z_bm + bt / 2.0),
                       (sx, bw, bt), M["pav_wood"])
        for tag, xx in (("E", p["x1"] - pr), ("W", p["x0"] + pr)):
            sc.add_box(stage, f"{P}/Beam_{tag}", (xx, cy, z_bm + bt / 2.0),
                       (bw, sy, bt), M["pav_wood"])
        # ⑤ 처마선 2단 — 서까래층(목) + 부연/기와 처마층(기와)
        z_ev = z_bm + bt                                  # 2.95
        eo = p["eave_over"]
        ex, ey = sx + 2 * eo, sy + 2 * eo                 # 6.10 × 6.10
        sc.add_box(stage, f"{P}/Eave", (cx, cy, z_ev + p["eave_t"] / 2.0),
                   (ex, ey, p["eave_t"]), M["pav_wood"])
        # ⑥ 처마선 2단(부연 밴드) + 모임지붕 — 단일 메시(밴드가 귀솟음 밑을 채움)
        z_fa = z_ev + p["eave_t"]                         # 3.05
        fi = p["fascia_inset"]
        fx, fy = ex - 2 * fi, ey - 2 * fi                 # 5.74 × 5.74
        _, z_ap = build_hip_roof(f"{P}/Roof", cx, cy, fx, fy, z_fa,
                                 p["fascia_t"], p["roof_rise"],
                                 p["corner_lift"], M["pav_roof"])
        # ⑦ 절병통 — 용마루 z_ap = 4.29
        sc.add_cylinder(stage, f"{P}/Finial",
                        (cx, cy, z_ap + p["finial_h"] / 2.0),
                        p["finial_r"], p["finial_h"], M["pav_roof"])
        # ⑧ 계자난간 — N/E/S 3면(서측 진입 개방). 하방 + 상방 + 동자 rail_n
        rh, rt, rr = p["rail_h"], p["rail_t"], p["rail_post_r"]
        rails = (("N", cx, p["y1"] - pr, sx - 2 * pr, rt),
                 ("S", cx, p["y0"] + pr, sx - 2 * pr, rt),
                 ("E", p["x1"] - pr, cy, rt, sy - 2 * pr))
        for tag, rx, ry, lx, ly in rails:
            for lbl, zz, th in (("Low", z_fl + 0.06, 0.10),
                                ("Top", z_fl + rh, 0.08)):
                sc.add_box(stage, f"{P}/Rail{lbl}_{tag}", (rx, ry, zz),
                           (lx, ly, th), M["pav_wood"])
            span = max(lx, ly)
            for k in range(p["rail_n"]):
                t = (k + 1.0) / (p["rail_n"] + 1.0) - 0.5
                bx = rx + (span * t if lx > ly else 0.0)
                by = ry + (0.0 if lx > ly else span * t)
                sc.add_cylinder(stage, f"{P}/RailPost_{tag}{k}",
                                (bx, by, z_fl + rh / 2.0), rr, rh,
                                M["pav_wood"])

    def build_lawns(M):
        """[v6 재수정 ③] 상부 테라스 잔디 밴드 2매 + 가로수 10주.
        판정 "상부에 잔디·수목 밴드가 없어 '공원'의 근거가 프레임에 0" 대응.
        전부 계단 폭(y±5) 밖(|y| ≥ 12) · 테라스 상면 위 lawn_proud(0.03) 돌출
        → **위험 기하·grazing 은닉 무영향**(그리드 프리셋 화각 ±30° 밖:
        eye x=−10 기준 밴드 최근접점이 방위 86° 이상)."""
        pr = PARAMS["lawn_proud"]
        for i, lw in enumerate(PARAMS["lawns"]):
            sc.add_box(stage, f"{ROOT}/Lawn_{i}",
                       ((lw["x0"] + lw["x1"]) / 2.0,
                        (lw["y0"] + lw["y1"]) / 2.0, pr / 2.0),
                       (lw["x1"] - lw["x0"], lw["y1"] - lw["y0"], pr),
                       M["grass"], collider=True)
        for i, (tx, ty) in enumerate(PARAMS["park_trees"]):
            sc.build_tree(stage, f"{ROOT}/ParkTree_{i}", tx, ty, pr,
                          M["wood"], M["canopy_a"], M["canopy_b"])

    def build_deck(M):
        """[v5 채택] 목재 산책 데크 접속 — 호수공원 수변 산책로.
        [v6] x −9.2..−6.8 (계단 상단 에지 x=0 에서 6.8 m 이격 → 위험 기하
        무간섭), 상면 0.06(테라스 0.0 대비 6 cm — 보행 연속). 판 이음선 간격을
        2.0 → 0.62 m 로 조여 원경에서도 '널결 있는 데크'로 판독되게 한다."""
        d = PARAMS["deck"]
        cx = (d["x0"] + d["x1"]) / 2.0
        sc.add_box(stage, f"{ROOT}/Deck",
                   (cx, (d["y0"] + d["y1"]) / 2.0, d["top_z"] / 2.0),
                   (d["x1"] - d["x0"], d["y1"] - d["y0"], d["top_z"]),
                   M["deck"], collider=True)
        n = int(round((d["y1"] - d["y0"]) / d["seam_step"]))
        for k in range(1, n):
            y = d["y0"] + k * d["seam_step"]
            sc.add_box(stage, f"{ROOT}/DeckSeam_{k}",
                       (cx, y, d["top_z"] - d["seam_drop"] / 2.0),
                       (d["x1"] - d["x0"], d["seam_w"], d["seam_drop"]),
                       M["seam"])

    def build_reeds(M):
        """[v5 채택] 갈대 군락 — 수위선 부근(제방, 계단 폭 y±5 밖)과 대안 둔치.
        군락마다 seed 고정 RandomState 로 재현. 대(cylinder)에 소각 기울기."""
        rd = PARAMS["reed"]
        fb = PARAMS["far_bank"]
        fb_z = water_z + fb["above_water"]
        for ci, (cx, cy, n, seed) in enumerate(PARAMS["reeds"]):
            rs = np.random.RandomState(int(seed))
            gz = fb_z if cx >= fb["x0"] else _step_top_at(cx)
            for k in range(int(n)):
                dx = float(rs.uniform(-rd["spread"], rd["spread"]))
                dy = float(rs.uniform(-rd["spread"], rd["spread"]))
                hh = float(rs.uniform(rd["h_lo"], rd["h_hi"]))
                a = float(rs.uniform(0.0, 360.0))
                t = rd["tilt"]
                sc.add_cylinder(
                    stage, f"{ROOT}/Reed_{ci}_{k}",
                    (cx + dx, cy + dy, gz + hh / 2.0), rd["r"], hh, M["reed"],
                    rotY=t * math.cos(math.radians(a)),
                    rotX=t * math.sin(math.radians(a)))

    def build_signs():
        """[v5 공통 레이어] 한글 사인(sc.build_sign). 좌표 검산은 PARAMS 주석."""
        back = sc.make_pbr(stage, "/World/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"/World/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, back_mtl=back)

    def build_dressing(M):
        """[v5 채택 / v6 재수정] 호수공원 드레싱 — 수변 경계 말뚝 8 +
        **목조 사모정 1** + 참 석주 4 + 벤치 4 + **오리배 1(곡면)** +
        산책 데크 + **잔디 밴드 2 + 가로수 10** + 갈대 10군락.
        [v6 §6 비움] 화단 2 는 삭제 — 잔디 밴드 위 가로수가 그 역할을 대체한다.
        전부 계단 폭(y±5) 밖 또는 테라스 위 → 위험 기하 불변."""
        r = PARAMS["mooring_r"]
        h = PARAMS["mooring_h"]
        # [v5] 계선주 → 경계 말뚝(축소): 계단머리 수변 경계 표시
        #   [v6] 데크가 x −10.0..−7.6 로 이설돼 이 말뚝열(x −1.2)은 이제
        #   "계단머리 경계"만 뜻한다(프림 이름은 판정 파일 연속성 위해 유지).
        for i, m in enumerate(PARAMS["mooring"]):
            sc.add_cylinder(stage, f"{ROOT}/DeckPile_{i}",
                            (m["cx"], m["cy"], h / 2.0), r, h, M["post"],
                            collider=True)
            sc.add_cylinder(stage, f"{ROOT}/DeckPileCap_{i}",
                            (m["cx"], m["cy"], h + 0.04 / 2.0), r * 1.2, 0.04,
                            M["post"])
        build_pavilion(M)
        build_lawns(M)                       # [v6 ③] 잔디 밴드 + 가로수
        build_deck(M)
        build_reeds(M)
        # 참(landing) 표식 석주 4 — 참 x 중앙, 계단 폭 밖(y±5.6)
        lp = PARAMS["land_posts"]
        for li, si in enumerate(PARAMS["stairs"]["landing_steps"]):
            xa, xb, _ = steps[si]
            for yi, yy in enumerate(lp["ys"]):
                sc.add_cylinder(stage, f"{ROOT}/LandPost_{li}_{yi}",
                                ((xa + xb) / 2.0, yy,
                                 steps[si][2] + lp["h"] / 2.0),
                                lp["r"], lp["h"], M["stone"], collider=True)
        # 벤치 4 — [§3] 앵커(정자 · 잔디 밴드 가장자리 · 데크) 옆, yaw 지터 ±3~8°
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, 0.0, M["post"],
                           yaw=yaw)
        # [v6 재수정 ②] 오리배 1 — 박스 조합 → **회전타원체 조합**.
        #   판정: "400 % 크롭 결과 백색 무텍스처 박스 + 판때기 목 — '배'로
        #   읽히지 않는다". 곡면 6부재(선체·가슴·꼬리·날개 2)로 오리 실루엣을
        #   만들고, 차양은 두꺼운 박스(h 0.45) → 얇은 판(0.05)+지주 4 로 바꿔
        #   선체 곡률을 가리지 않게 한다. 알베도 백색 0.86 → 황색 0.78/0.70/0.25.
        #   흘수 : 선체 반경 0.36, 중심이 수면 위 0.12 → 수면 아래 0.24 /
        #   수면 위 0.48 (오리배 실측 흘수 비율 근사). rot_group 으로 방위.
        bt = PARAMS["boat"]
        hl, br, st_, wg = bt["hull"], bt["breast"], bt["stern"], bt["wing"]
        hd, bk, cp = bt["head"], bt["beak"], bt["canopy"]
        for i, b in enumerate(PARAMS["boats"]):
            grp = sc.build_rot_group(stage, f"{ROOT}/DuckBoat_{i}",
                                     (b["cx"], b["cy"]), b["rotz"])
            bx, by = b["cx"], b["cy"]
            hz = water_z + bt["hull_float"]               # 선체 중심 z
            SPH = sc.add_sphere
            SPH(stage, f"{grp}/Hull", (bx, by, hz), hl, M["duck"])
            SPH(stage, f"{grp}/Breast", (bx + hl[0] * 0.71, by, hz + 0.14),
                br, M["duck"])
            SPH(stage, f"{grp}/Stern", (bx - hl[0] * 0.85, by, hz + 0.18),
                st_, M["duck"])
            for tag, sgn in (("P", 1.0), ("S", -1.0)):
                SPH(stage, f"{grp}/Wing_{tag}",
                    (bx - 0.15, by + sgn * bt["wing_dy"], hz - 0.04), wg,
                    M["duck"])
            # 목 — 가슴 위에서 앞으로 neck_lean° 기운 원기둥.
            #   add_cylinder 는 **중심 기준 rotY** 이므로 목 끝(머리 자리)은
            #   중심에서 (neck_h/2)·(sinθ, 0, cosθ) 만큼 간다. 머리 중심은
            #   거기서 다시 head_rz·0.55 만큼 같은 축으로 더 나간 지점.
            nx = bx + hl[0] * 0.81
            nz = hz + 0.38 + bt["neck_h"] / 2.0
            sc.add_cylinder(stage, f"{grp}/Neck", (nx, by, nz),
                            bt["neck_r"], bt["neck_h"], M["duck"],
                            rotY=bt["neck_lean"])
            lean = math.radians(bt["neck_lean"])
            d_nh = bt["neck_h"] / 2.0 + hd[2] * 0.55       # 0.41
            hxc = nx + d_nh * math.sin(lean)
            hzc = nz + d_nh * math.cos(lean)
            SPH(stage, f"{grp}/Head", (hxc, by, hzc), hd, M["duck"])
            sc.add_box(stage, f"{grp}/Beak",
                       (hxc + hd[0] + bk[0] / 2.0, by, hzc - 0.04), bk,
                       M["beak"])
            # 차양 — 얇은 판 + 지주 4 (구: 높이 0.45 박스 = '백색 상자'의 주범)
            #   판 상면 = 수면 위 1.55 m(오리배 차양 실측 대역), 머리 정수리
            #   (수면 위 1.41)보다 약간 위 → 실루엣에서 머리를 가리지 않는다.
            cz = hz + 1.40                      # 차양 판 중심
            czb = hz + 0.10                     # 지주 밑동(선체에 매입)
            sc.add_box(stage, f"{grp}/Canopy", (bx - 0.30, by, cz), cp,
                       M["duck_top"])
            ph_c = cz - cp[2] / 2.0 - czb
            for tag, sx_, sy_ in (("SW", -1.0, -1.0), ("SE", 1.0, -1.0),
                                  ("NW", -1.0, 1.0), ("NE", 1.0, 1.0)):
                sc.add_cylinder(
                    stage, f"{grp}/CanopyPost_{tag}",
                    (bx - 0.30 + sx_ * (cp[0] / 2.0 - 0.06),
                     by + sy_ * (cp[1] / 2.0 - 0.06), czb + ph_c / 2.0),
                    bt["canopy_post_r"], ph_c, M["duck_top"])

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 : 계단·둔치를 z=0 평지로 통일(수면 유지)."""
        sc.add_box(stage, f"{ROOT}/FlatFill", (16.0, 0.0, -0.25),
                   (56.0, 80.0, 0.5), M["stone"], collider=True)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_terrace(M)
    if cfg["hazard_stairs"]:
        build_stairs(M)
        build_embankment(M)
    else:
        build_flat_fill(M)
    build_river(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if cfg.get("cue_sign"):
        build_signs()                       # [v5 공통 레이어]

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke:
        # [v7] 지붕 메시 법선 + §4 알베도 상한 자가검사 (렌더 없음)
        roof_normal_selfcheck()
        albedo_selfcheck()
        # 조립 직후 바인딩 검증 — 판정 §6 ② 후속("그래도 밝으면 바인딩 확인")
        rp = stage.GetPrimAtPath(f"{ROOT}/Pavilion/Roof")
        fp = stage.GetPrimAtPath(f"{ROOT}/Pavilion/Finial")
        from pxr import UsdShade, UsdGeom as _UG
        rb = UsdShade.MaterialBindingAPI(rp).GetDirectBinding() if rp else None
        fb = UsdShade.MaterialBindingAPI(fp).GetDirectBinding() if fp else None
        rmat = rb.GetMaterialPath() if rb else "(없음)"
        fmat = fb.GetMaterialPath() if fb else "(없음)"
        ni = _UG.Mesh(rp).GetNormalsInterpolation() if rp else "(없음)"
        nn = len(_UG.Mesh(rp).GetNormalsAttr().Get() or []) if rp else 0
        print("=" * 68)
        print("scene09 [v7] 지붕/절병통 재질 바인딩 · 법선 저작 확인")
        print(f"  Roof   바인딩 {rmat} · normals {nn}개 · "
              f"interpolation {ni}")
        print(f"  Finial 바인딩 {fmat}")
        print(f"  ⇒ 두 프림 동일 재질 "
              f"{'OK' if str(rmat) == str(fmat) else 'FAIL'} · "
              f"법선 저작 {'OK' if nn > 0 else 'FAIL'}")
        # [v8 Y1] MDL 파라미터 실측 — 판정 권고 ㉡("바인딩이 맞다면 경면 계열").
        #   바인딩·법선은 v7 라운드에 이미 OK 로 찍혔다. 다음 라운드가 다시
        #   같은 곳을 파지 않도록 **셰이더 입력값 자체**를 로그에 남긴다.
        try:
            shp = stage.GetPrimAtPath("/World/Looks/PavRoof/Shader")
            sh = UsdShade.Shader(shp)
            got = {}
            for nm in ("diffuse_color_constant", "reflection_roughness_constant",
                       "specular_level", "metallic_constant"):
                i = sh.GetInput(nm)
                got[nm] = i.Get() if i else "(미지정=MDL 기본값)"
            print("  PavRoof MDL 입력 실측:")
            for nm, val in got.items():
                print(f"    {nm:32s} {val}")
            sl = got["specular_level"]
            print(f"  ⇒ specular_level {'OK(0.0 명시)' if sl == 0.0 else 'FAIL'}"
                  f" — 미지정이면 OmniPBR 기본 0.5(F0 0.04)가 살아 "
                  f"roughness {mp['roof_tile_rough']} 광로브로 천공/태양을 가산한다")
        except Exception as e:
            print(f"  [WARN] MDL 입력 조회 실패: {e}")
        print("=" * 68)
        print("[SMOKE] 부팅+조립+조명 완료 — 렌더 없이 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views(run, z_bot, water_z, water_x0)
    _v0 = views["ghat_walk"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene09_{ts}.png")
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
