#!/usr/bin/env python3
"""렌더 라운드 회귀 자동 검사기 — 이미지 + manifest.json 만으로 동작.

`Docs/briefs/multi_scene_brief_v3.md` §A 회귀 방지 체크리스트 중
**렌더 산출물만으로 판정 가능한 항목**을 자동화한다. GPU·Isaac 불요.

동기 (프로젝트 교훈, `Docs/audit_v4/fixlog_W7.md` §0):
  "신설 기하가 프리셋 카메라를 삼키는 회귀가 4회 재발했다
   (scene19 d5 암흑 · scene17 성토 매몰 · scene05 화단 매몰 · scene19 skyline 접선 차폐).
   눈으로 한 차폐 검산은 차폐 주체 자체를 오진한다."
  "프레이밍 검산은 앵커 **개수**가 아니라 **픽셀 점유율**로 걸 것"
   (`Docs/audit_v4/judge_v8_rt.md` §376)

검사 6종
  [DARK]  암흑 프레임        — 평균 휘도·암부 비율 (카메라가 기하에 삼켜짐의 주 증상)
  [BLOWN] 과노출·255 클리핑
  [WHITE] 순백 대면적        — v5.1 §4 금지 규약 (절대치는 참고, 증가분이 판정)
  [OCCL]  카메라 차폐 회귀   — 이전 라운드 대비 **신규 암부**와 그 최대 연결 덩어리
  [FRAME] 프레임 점유율 급변 — 전역 톤 정규화 후 16×9 블록 점유율 이동
  [GRAZE] grazing 은닉 의심  — **낙차 에지 투영 대역**의 수평 결맞음 변화 (지표 v2)

사용법
  # 단일 씬 A/B
  python scripts/regression_check.py --before look_check/scene07/p2g2_off \
                                     --after  look_check/scene07/p2g2_on

  # 전 33씬 (라운드 이름은 쉼표 폴백 — 먼저 존재하는 것을 씀)
  python scripts/regression_check.py --scenes 'look_check/scene*' \
      --before-round final_pt_r2,final_pt,ctx2_pt,ctx2 --after-round v9_look \
      --json Docs/reports/regr_v9.json

  # 씬별로 라운드가 제각각이면 목록 파일 (씬경로 TAB 이전 TAB 이후, # 주석)
  python scripts/regression_check.py --list rounds.tsv

의존성: numpy + PIL 뿐 (scipy·opencv 금지 — 배포 환경 가정).
같은 계열 도구: `scripts/imgstats.py` (사실성 저수준 통계). 본 도구는 **회귀** 전용이다.

지표 버전
  GRAZE 만 v2 (2026-07-29 재캘리브레이션). 나머지 6종은 v1 그대로다.
  근거·전후 비교표: `Docs/reports/graze_recalibration_v1.md`
"""
import argparse
import glob
import json
import math
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from PIL import Image

# ===========================================================================
# 임계값 — 전부 여기 모아 둔다. 각 값의 근거를 주석으로 남긴다.
#
# 근거의 출처는 3가지다.
#   (a) 감독 판정문의 실측 대역 — `Docs/audit_v4/judge_v7_rt_A.md`,
#       `judge_v8_rt.md` 는 프리셋 9컷을 "mean / dark<25 / 255 클리핑" 으로
#       전수 측광했다. 본 도구는 **같은 정의**를 쓴다(호환).
#   (b) 대조군 실측 — 룩 레이어 A/B 페어 4쌍(scene07/sceneD3 p2g1·p2g2 off↔on,
#       총 56컷) + 소폭 수정 라운드(sceneD3 r2→r3) + 렌더 모드 교체
#       (scene07 v8_rt→v8_pt). **회귀가 없어야 정상인 페어들**의 잡음 상한.
#   (c) 실회귀 실측 — scene07 v6→v7, v7→v8 (판정문이 실제 차폐·암흑으로
#       지적한 컷들)의 값.
# 임계는 (b)의 상한과 (c)의 하한 사이에 둔다.
# ===========================================================================

# --- [DARK] 절대 암흑 -------------------------------------------------------
# judge_v7_rt_A §128: mean 26.3 · dark 81.3 % 를 "사실상 판정 불능" 으로 판정.
# judge_v8_rt §78 : 합격 그리드는 mean 127~185 · dark 1.8~10.4 %.
# judge_v8_rt §240: mean 49.4 · dark 53.4 % 를 "여전히 씬 최암부" 로 잔여 지적.
DARK_MEAN_FAIL = 30.0
DARK_MEAN_WARN = 55.0
DARK_PCT_FAIL = 70.0
DARK_PCT_WARN = 45.0
DARK_LEVEL = 25          # 암부 정의 — 감독 측광과 동일 (0~255 휘도 < 25)

# --- [BLOWN] 과노출 ---------------------------------------------------------
# 합격 33씬 최종 라운드 412컷 전수 실측(본 도구): mean p95 = 188, max = 238.3
# (scene14 h0.3_d10 — 실제로 정보가 죽은 백판 프레임). 255 클리핑은 max 0.35 %
# 로 사실상 전무하므로 클리핑 임계는 낮게 잡아도 과탐지가 없다.
BLOWN_MEAN_FAIL = 235.0
BLOWN_MEAN_WARN = 210.0
CLIP_PCT_FAIL = 1.0
CLIP_PCT_WARN = 0.2
CLIP_LEVEL = 254         # 채널 최대값이 254 이상 = 255 클리핑

# --- [WHITE] 순백 대면적 (v5.1 §4 "순백(>0.8) 대면적 금지") -----------------
# 픽셀값 > 0.8 은 **알베도 > 0.8 과 같지 않다**(정오광+ACES 톤매핑에서
# 알베도 0.5 콘크리트도 쉽게 넘는다). 합격 33씬 중 12씬이 절대치로 걸린다.
# → 절대치는 참고(WARN)로만 쓰고, **판정은 이전 라운드 대비 증가분**으로 한다.
WHITE_LEVEL = 204        # = 0.8 × 255, 채널 최소값 기준(= 무채색 순백)
WHITE_PCT_WARN = 60.0    # 하단 2/3 기준. 33씬 중앙값 0.97 %, p95 88.6 % (이봉분포)
WHITE_DELTA_FAIL = 25.0  # 증가 pp. 대조군 A/B 최대 증가 +2.4 pp
WHITE_DELTA_WARN = 10.0

# --- [OCCL] 카메라 차폐 회귀 ------------------------------------------------
# newdark = (이전 휘도 >= 60) & (신규 휘도 < 25) 인 픽셀 비율.
#   대조군 56컷 최대 0.67 % / 소폭 수정 0.26 % / 모드 교체 0.00 %
#   실회귀     : 8.2 · 14.0 · 14.5 · 17.3 · 23.0 · 26.5 · 39.3 · 47.7 %
OCCL_NEWDARK_FAIL = 8.0
OCCL_NEWDARK_WARN = 2.0
# 최대 **연결** 신규암부(대면적 판정). 대조군 최대 0.05 %, 실회귀 2.3~41.6 %.
OCCL_BLOB_FAIL = 5.0
OCCL_BLOB_WARN = 1.5
OCCL_BRIGHT_BEFORE = 60  # "원래 밝았다" 의 하한
NEAR_BAND = 0.60         # 프레임 하단 40 % = 근거리대(카메라를 삼키는 기하가 앉는 곳)

# --- [FRAME] 프레임 점유율 급변 --------------------------------------------
# 전역 톤(밝기·대비·하늘 교체·RT↔PT)을 백분위 매칭으로 제거한 뒤 16×9 블록
# 평균을 비교한다. 톤 정규화가 없으면 **의도한 룩 변경만으로 전 컷이 경보**가 된다
# (실측: scene07 v8_rt→v8_pt 는 정규화 전 변화픽셀 55 %, 정규화 후 블록이탈 0 %).
#   대조군 A/B  : blk_shift 0.0~25.0 % (최대는 scene07 side_slope — 룩 레이어가
#                 실제로 사면을 바꾼 컷이라 WARN 이 나는 게 맞다)
#   소폭 수정   : 0.0~4.2 %
#   모드 교체   : 0.0 %
#   실회귀      : 36.8 ~ 97.9 %
FRAME_SHIFT_FAIL = 40.0
FRAME_SHIFT_WARN = 20.0
FRAME_BLOCK_DELTA = 10.0   # 블록 평균이 이만큼(0~255) 어긋나면 "이동한 블록"
# 최대 블록 편차. 룩레이어 A/B 대조군 최대 32.7 / 실회귀 78.8~207.
# 배치1 ctx 라운드에서 46~64 대역이 무해하게 나오므로 WARN 을 55 로 둔다
# (대조군의 1.7배, 실회귀 하한 78.8 아래).
FRAME_MAXBLK_FAIL = 100.0
FRAME_MAXBLK_WARN = 55.0
BLOCKS_Y, BLOCKS_X = 9, 16

# --- [PHOTO] 휘도 분포 급변 (절대 mean/dark 의 변화량) ----------------------
#   대조군 |Δmean| <= 7.0 · Δdark <= +0.0 pp
#   모드 교체 |Δmean| <= 8.8
#   실회귀 Δmean -25.0 / Δdark +15.8, +11.8 pp
# 어두워지는 방향만 FAIL 로 본다(밝아지는 것은 회귀가 아니라 개선 방향이 대부분).
PHOTO_DMEAN_FAIL = -45.0
PHOTO_DMEAN_WARN = -20.0
PHOTO_DMEAN_UP_WARN = 25.0     # 밝아짐 — 급변이므로 알리되 FAIL 로 올리지 않는다
PHOTO_DDARK_FAIL = 25.0
PHOTO_DDARK_WARN = 12.0

# ===========================================================================
# --- [GRAZE] grazing 은닉 의심 — 지표 **v2** (2026-07-29 재캘리브레이션) -----
# ===========================================================================
# 전면 근거: `Docs/reports/graze_recalibration_v1.md`
#
# ■ v1 이 왜 틀렸나 (기하학적 오류, [기하])
#   v1 은 "지면대 = 프레임 하단 55 %" 의 **거시 구조 총량**을 쟀다. 그런데
#   지면점의 상 행은 카메라 기하로 결정된다 —
#       row(X) = H/2 · (1 − tan(−atan(h/X) − pitch) / tan(vFOV/2))
#   h0.3 · pitch −10° · vFOV 36° (1920×1080, hFOV 60°) 를 넣으면
#       X = 1 m → 0.68H · 2 m → 0.46H · 5 m → 0.32H · 10 m → 0.28H · ∞ → 0.23H
#   즉 **하단 55 %(row ≥ 0.45H)에 들어오는 지면은 X ≲ 2.05 m 뿐**이다.
#   그런데 프리셋 `preset_h{h}_d{d}` 의 낙차 에지는 정의상 카메라에서
#   수평거리 **정확히 d** 다(`scene_common.grid_views` + 씬별 기준점 시프트,
#   예: scene05 "립까지 거리 d 의미가 되게" §build_views). 따라서
#     · d5 · d10 의 에지는 v1 밴드 **바깥**(0.32H · 0.28H)에 있었고
#     · v1 이 실제로 잰 것은 **근경 클러터 지대**(X < 2 m)였다.
#   ground_kit 근경 충전은 바로 그 지대를 채운다 → 구조적 오탐 폭주가 예정.
#
# ■ 실측 뒷받침
#   · 오탐: sceneC2 `balust`→`leaf3d`(3D 낙엽 산포 = 근경 충전 그 자체)에서
#           v1 은 `h0.3_d5` GRAZE **FAIL**(vgrad ×1.46 · erow +0.50). 육안으로
#           에지 대역은 불변이고 변화는 전량 근경이다.
#   · 검출력: 낙차 노출을 물리 파라미터(노출 라이저 높이 · 면 대비)로 주입한
#           844컷 중 v1 검출 **7.2 %**. v2 는 70.5 %(라이저 ≤0.4 m 78.5 %).
#   · 판정 이력 정합: v6→v7·v7→v8 은 판정문이 "은닉(grazing) 회귀 0"
#           (`judge_v8_rt.md` §46, `judge_v7_rt_B.md`)으로 확정한 라운드인데
#           v1 은 92컷 중 FAIL 11 · WARN 7 을 냈다. v2 는 FAIL 1 · WARN 3.
#
# ■ v2 가 재는 것 — 에지 투영 대역의 **수평 결맞음 변화**
#   E 대역(에지) = 지면거리 [0.7·d, 2.2·d] 의 투영 행 ± FOV 오차 여유
#   G 대역(가드) = 라이저 0.5 m 가 드러났을 때 채울 행 (측정 제외)
#   N 대역(근경) = 그 아래 전부 = 클러터 대조군
#   신호 = (톤 정규화 후) 세로 단차장의 **열 평균**. 등방 클러터(낙엽·자갈·
#   소품)는 열 평균에서 상쇄되고, 화면을 가로지르는 선(= 낙차 에지)만 남는다.
#   판정치 spec = max|Δ|_E − max|Δ|_N  → "변화가 에지 대역에 **국소**한가".
#
# ■ v2.1 (2026-07-29) — **2차 판별기 2종 추가**. 대역·신호·임계는 v2 그대로다.
#   근거: `w2_gate_preflight.md` §3.4 (T3 잔여 WARN 2건 크롭 육안) +
#         `graze_recalibration_v1.md` §11-2 (방향별 게이트 분리).
#   T3 가 규명한 것: v2 의 잔여 발화 2건은 **은닉 회귀가 아니라 에지 양쪽 지면의
#   알베도 교체**였다. `Δcoh` 는 단차장의 **절대 변화량**이라 그 둘을 못 가른다.
#   부족한 것은 "그 변화가 은닉을 바꿨는가" 를 묻는 2차 판별이고, v2.1 이 그것이다.
#
#   (a) **에지 존속 게이트** — 낙차행 ±GRAZE_SLACK 에서 **before/after 각각의**
#       세로 단차 절대값을 같이 재고, **둘 다** GRAZE_STEP_MIN 이상이면 spec 초과라도
#       정숙(재질 변화)으로 내린다. 진짜 매몰이면 after 단차가 무너지므로(선이 없어짐)
#       검출력은 유지된다. T3 실측: scene13 115.9→67.8 · scene07 109.6→86.4 (원해상 단일행).
#   (b) **방향별 분리** — 노출 방향(선이 생김)은 v2 그대로 **변화의 열 일치율**로 게이트하고,
#       매몰 방향(선이 약해짐)은 **단차비** `step_after / step_before` 로 게이트한다.
#       물리적으로 매몰 = "있던 선이 사라짐" 이므로 이쪽이 정의에 맞다(§11-2).
#       사실화 라운드의 알베도 교체는 비 0.5~0.9 대에 몰리고 진짜 매몰은 0 에 가깝다
#       (T3 실측 0.585 · 0.788). 또 **이전 라운드에 선이 없었으면**(step_before 미달)
#       매몰이라는 말 자체가 성립하지 않으므로 정숙으로 내린다.
#   (c) `GRAZE_SLACK` 은 **2 유지**. T3 §3.4-3 의 "2→3" 안은 채택하지 않았다 —
#       (a) 가 scene07 을 이미 정숙시키므로 슬랙을 건드릴 이유가 없고, 슬랙 변경은
#       주입시험 전면 재산정을 요구한다(T3 스스로 단 조건).
GRAZE_VER = "v2.1"
GRAZE_HFOV = 60.0          # [코드] 1920×1080 뷰포트 수평 화각. 근거 다중:
#   `scenes/main/facade_kit.py` §231 "pitch −10° · vFOV 36°"
#   `scenes/main/scene19_fan_winder.py` `_cam_basis(hfov=60, aspect=16/9)`
#   `sceneC2/C1` "[카메라 검산] FOV 수평 ±30°/수직 ±18° 가정"
#   원출처는 `fixlog_W4.md` §155 · `fixlog_W5.md` §66 (v6 렌더 역산).
#   W5 는 반각 32.6°/19.8° 라는 다른 역산치도 남겼다 → 수직 스케일 오차
#   최대 11 % → 아래 GRAZE_FOV_TOL 로 흡수한다.
GRAZE_KN = 0.7             # E 대역 근단 = 0.7·d  (에지보다 앞 30 %)
GRAZE_KF = 2.2             # E 대역 원단 = 2.2·d  (에지 너머 배경 진입 직전)
GRAZE_FOV_TOL = 0.13       # 화각 불확실성 여유 (프레임 중심 기준 오프셋의 13 %)
GRAZE_GUARD_DZ = 0.5       # 가드 대역 = 라이저 0.5 m 노출분. 이만큼은 N 에서 뺀다
#   (안 빼면 큰 노출이 N 까지 번져 spec 이 스스로 상쇄된다 — 실측:
#    라이저 0.4 m 검출률 가드 없음 55 % → 가드 0.5 m 로 동일, 0.8 m 는 24 %.
#    0.8 m 급 노출은 어차피 PHOTO/OCCL 관할이라 가드를 더 키우지 않는다.)
# 판정 임계 — 대조군 157컷(모드교체·룩A/B·맥락ctx·사실화r2·P4근경) 실측
#   spec p50 0.0~1.3 · p90 0.2~9.8 · max 24.8.  임계 8/20 에서 대조군 WARN 1.
GRAZE_SPEC_WARN = 8.0
GRAZE_SPEC_FAIL = 20.0
GRAZE_AGREE_MIN = 0.70     # 변화의 **열 부호 일치율**. 0.5=난수(등방 클러터),
#   1.0=화면 전폭 선. 실측: 낙엽 산포 0.5~0.6 / 주입 낙차선 0.9~1.0
GRAZE_BAND_MU_MIN = 35.0   # E 대역 절대 휘도 하한. 이보다 어두우면 판정 유보
#   (scene06 나선 내부 mean 2.7 · sceneD4 터널 12.9 — 톤 정규화가 잡음을 증폭)
GRAZE_PHOTO_DMEAN = 20.0   # 프레임 측광이 이만큼 흔들리면 GRAZE 판정 유보
GRAZE_PHOTO_DDARK = 12.0   #   (= PHOTO WARN 임계. 조명 회귀를 먼저 고칠 것)
GRAZE_HW = 3               # 단차 정합 필터 반폭(행)
GRAZE_SMOOTH = 3           # 프로파일 이동평균(행)
GRAZE_SLACK = 2            # 행 오정합 허용 — 기존 에지가 1~2행 밀린 것은 변화 아님
GRAZE_EDGE_GUARD = 6       # 프레임 상·하단 절단 구간(필터가 잘리는 곳)
GRAZE_LONG = 960           # GRAZE 전용 작업 해상도 (d10 대역이 384 에선 13행뿐)
# --- v2.1 2차 판별 상수 ----------------------------------------------------
GRAZE_STEP_MIN = 25.0      # [v2.1a] "그 행에 선이 있다" 로 인정하는 세로 단차(계조).
#   측정 위치는 최대 변화행 ±GRAZE_SLACK, 측정 대상은 **열 평균 단차 프로파일**
#   (graze_delta 와 같은 평활을 거친 값). 임계 25 는 W2 지시값이며 T3 실측
#   (before 115.9/109.6 · after 67.8/86.4, 원해상 단일행)의 한참 아래라
#   "선이 존속한다" 를 넉넉히 인정한다. 진짜 매몰(선 소멸)은 after 가 0 근방이라 무영향.
GRAZE_BURY_RATIO = 0.50    # [v2.1b] 매몰 방향 발화 상한 = step_after / step_before.
#   T3 실측 0.585(scene13) · 0.788(scene07) = 알베도 교체 대역. 매몰은 0 근방.
#   0.5 는 두 군 사이이며 T3 §3.4-2 가 제시한 "0.5~0.9 대 vs 0" 분리선을 따른다.
# --- v2.1 검출력 보호 가드 2개 (T3 안에는 없던 **추가 조건**) -----------------
# T3 §3.4-1 은 "진짜 매몰이면 after 단차가 무너지므로 검출력은 유지된다" 고 적었으나
# 이는 **매몰 방향에 대해서만** 성립하는 논증이고, §6 주입시험(노출 방향)으로는
# 검증되지 않았다. 실제로 존속 게이트를 무조건 적용하면 주입 검출이
# **70.4 % → 46.8 %** 로 무너진다 `[실측 — w2_tools_v1.md §4.5]`. 원인은 §6 주입 모형이
# 낙차행 **아래**를 어둡게 하므로 낙차행 단차가 오히려 **줄고**, 그 모습이 알베도 교체와
# 구분되지 않기 때문이다. 아래 두 가드가 그 겹침을 걷어낸다(재현: 검출 65.8 % 유지).
GRAZE_PERSIST_ROWTOL = 4   # 최대 변화행이 낙차행에서 이만큼 이내여야 "그 선의 변화" 다.
#   T3 2건 실측 3.3 · 3.7 행(960 px 축소본). 이 밖의 변화는 E 대역의 **다른 지물**이므로
#   존속 게이트를 적용할 근거가 없다(scene17 74.7 · scene18 36.7 · scene19 30.3 → 발화 유지).
GRAZE_PERSIST_DOM = 3.5    # 존속 선이 변화량을 이만큼 압도해야 "알베도 교체" 로 읽는다.
#   step_after / dE — T3 실측 3.97(scene13) · 6.41(scene07). 새로 드러난 라이저는
#   변화량 자체가 선의 대비와 같은 급이라 이 비가 작다.

# --- 이월 결함 판정 ---------------------------------------------------------
# 절대 결함(DARK/BLOWN)이 이전 라운드에도 있었으면 회귀가 아니다. 이만큼
# 더 나빠졌을 때만 등급을 유지한다. 값은 대조군 A/B 잡음(|Δmean| <= 7.0,
# Δdark <= 0.0 pp)의 약 1.5배.
CARRY_DMEAN = 10.0
CARRY_DDARK = 10.0

# --- [UNCHANGED] 무변화 감지 -----------------------------------------------
# PT 표본 노이즈 상한. realism_phase1 §3.2 실측: PT legacy↔fast 의 평균차
# 0.6~0.7/255. 최대차는 노이즈 한 픽셀로도 튀므로(무변화 컷 실측 max 89 LSB)
# 최대치가 아니라 **평균차 + 유의차 픽셀 비율**로 본다.
#   무변화 실측 : 평균차 0.017~0.235 · 4 LSB 초과 0.000~0.012 %
#   룩레이어 변화: 평균차 15.3      · 4 LSB 초과 55.3 %
IDENTICAL_MEAN = 0.5     # 평균 절대차 (0~255)
IDENTICAL_FRAC = 0.1     # 4 LSB 초과 픽셀 비율 (%)

# --- 처리 해상도 ------------------------------------------------------------
SMALL_LONG = 384     # 구조 비교용 축소 (BOX = 면적 평균 → 평균값 보존)
BLOB_LONG = 192      # 연결성분용 (대면적만 보므로 더 성겨도 된다)

SEV = {"PASS": 0, "INFO": 1, "WARN": 2, "FAIL": 3}
SEV_NAME = ["PASS", "INFO", "WARN", "FAIL"]


# ===========================================================================
# [1] 기본 측정
# ===========================================================================
def _lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def _load(path, graze=False):
    """전해상도 RGB + 축소본 2종(+GRAZE 전용 1종)을 한 번에 만든다.

    GRAZE 축소본은 h0.3 컷에서만 만든다 — d10 의 에지 대역은 384 px 축소본에서
    13행뿐이라 통계가 서지 않는다(960 px 에선 34행).
    """
    im = Image.open(path).convert("RGB")
    w, h = im.size
    full = np.asarray(im).astype(np.float32)

    def rs(n):
        s = n / max(w, h)
        return np.asarray(im.resize((max(1, int(w * s)), max(1, int(h * s))),
                                    Image.BOX)).astype(np.float32)
    return full, rs(SMALL_LONG), rs(BLOB_LONG), (_lum(rs(GRAZE_LONG)) if graze
                                                 else None)


def photometry(full):
    """감독 판정문과 동일 정의의 절대 측광 (전해상도에서)."""
    g = _lum(full)
    h = g.shape[0]
    return dict(
        mean=float(g.mean()),
        dark=100.0 * float((g < DARK_LEVEL).mean()),
        dark_near=100.0 * float((g[int(h * NEAR_BAND):] < DARK_LEVEL).mean()),
        clip=100.0 * float((full.max(-1) >= CLIP_LEVEL).mean()),
        white=100.0 * float((full.min(-1)[h // 3:] > WHITE_LEVEL).mean()),
        w=int(g.shape[1]), h=int(h),
    )


def tone_match(src, ref):
    """src 를 ref 의 휘도 분포에 백분위 매칭 — 전역 톤 변화를 제거한다.

    이것이 이 도구의 핵심 전제다. 룩 레이어 라운드는 **전 씬의 밝기·채도·
    하늘이 동시에 바뀐다.** 정규화 없이 픽셀을 비교하면 의도한 변경이
    전부 경보가 되어 도구가 무용지물이 된다(실측: 정규화 전 변화픽셀 55 % →
    정규화 후 블록이탈 0 %, scene07 v8_rt→v8_pt).
    """
    qs = np.linspace(0.0, 100.0, 33)
    xs = np.percentile(src, qs)
    ys = np.percentile(ref, qs)
    xs = np.maximum.accumulate(xs) + np.arange(33) * 1e-6   # 단조 증가 보장
    return np.interp(src, xs, ys)


def block_means(l):
    h, w = l.shape
    return np.array([[l[y * h // BLOCKS_Y:(y + 1) * h // BLOCKS_Y,
                        x * w // BLOCKS_X:(x + 1) * w // BLOCKS_X].mean()
                      for x in range(BLOCKS_X)] for y in range(BLOCKS_Y)])


def largest_blob_pct(mask):
    """4-이웃 최대 연결성분의 화면 비율 (%). 스캔라인 union-find, 순수 파이썬."""
    if not mask.any():
        return 0.0
    H, W = mask.shape
    parent = [0]
    lab = np.zeros((H, W), np.int32)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    nxt = 1
    m = mask
    for y in range(H):
        row = m[y]
        if not row.any():
            continue
        prev_row = lab[y - 1] if y else None
        cur = lab[y]
        for x in np.flatnonzero(row):
            up = prev_row[x] if y else 0
            left = cur[x - 1] if x else 0
            if up and left:
                cur[x] = min(up, left)
                union(up, left)
            elif up or left:
                cur[x] = up or left
            else:
                parent.append(nxt)
                cur[x] = nxt
                nxt += 1
    flat = lab.ravel()
    nz = flat[flat > 0]
    if nz.size == 0:
        return 0.0
    roots = np.array([find(int(v)) for v in np.unique(nz)])
    remap = dict(zip(np.unique(nz).tolist(), roots.tolist()))
    counts = {}
    for v, c in zip(*np.unique(nz, return_counts=True)):
        r = remap[int(v)]
        counts[r] = counts.get(r, 0) + int(c)
    return 100.0 * max(counts.values()) / mask.size


# ---------------------------------------------------------------------------
# GRAZE v2 — 카메라 기하로 낙차 에지 대역을 특정하고 거기만 본다
# ---------------------------------------------------------------------------
def ground_row(X, h, pitch_deg, H, tanv):
    """지면점(수평거리 X, 눈보다 h 아래)의 상 행. 행은 아래로 증가.

    점의 앙각 = −atan(h/X), 광축 앙각 = pitch → 광축 위 오프셋 a = −atan(h/X) − pitch.
    """
    X = max(float(X), 1e-6)
    a = -math.atan2(h, X) - math.radians(pitch_deg)
    return H / 2.0 * (1.0 - math.tan(a) / tanv)


def graze_geom(view, eye, tgt):
    """(지면 위 눈높이 h, 낙차 에지까지 수평거리 d, pitch°, 종류) 또는 None.

    · `preset_h{h}_d{d}` — 이름이 곧 기하다. `grid_views` 규약상 eye 는
      (−d, gy, h) 이고 낙차 에지는 원점(x=0)이므로 **에지까지 거리 = d**,
      **지면 위 눈높이 = h**. 씬이 기준점을 옮겨도(scene05 −1.5, scene19 미러)
      "립까지 거리 d" 의미가 유지되도록 옮긴 것이라 이 해석이 맞다.
      manifest 의 eye z 는 **월드 절대 z** 라 여기 쓸 수 없다(도크스트링 §is_graze_view).
    · 그 밖의 `*graz*` 미장센 컷 — 저자 관례상 **tgt 가 위험 기하**다.
      그래서 지면 = tgt 의 z 평면, 에지 거리 = eye→tgt 수평거리로 푼다.
    """
    m = re.search(r"h([0-9.]+)_d([0-9.]+)", view)
    e = [float(v) for v in eye]
    t = [float(v) for v in tgt]
    horiz = math.hypot(t[0] - e[0], t[1] - e[1])
    if horiz < 1e-6:
        return None
    pitch = math.degrees(math.atan2(t[2] - e[2], horiz))
    if m:
        return dict(h=float(m.group(1)), d=float(m.group(2)), pitch=pitch,
                    kind="preset")
    h = e[2] - t[2]
    if h <= 0.02 or horiz < 0.3:
        return None                      # 수평·상향 시선 → 지면 대역이 안 잡힌다
    return dict(h=h, d=horiz, pitch=pitch, kind="aimed")


def graze_bands(g, H, W):
    """에지(E) · 가드 · 근경(N) 대역의 행 범위."""
    tanv = math.tan(math.radians(GRAZE_HFOV / 2.0)) * H / float(W)
    h, d, p = g["h"], g["d"], g["pitch"]
    y_hor = ground_row(1e9, h, p, H, tanv)         # 지평선
    y_haz = ground_row(d, h, p, H, tanv)           # 낙차 에지
    y_far = ground_row(d * GRAZE_KF, h, p, H, tanv)
    y_near = ground_row(d * GRAZE_KN, h, p, H, tanv)
    pad = GRAZE_FOV_TOL * max(abs(y_far - H / 2.0), abs(y_near - H / 2.0))
    e_top = max(y_hor + 1.0, y_far - pad, float(GRAZE_EDGE_GUARD))
    e_bot = min(H - GRAZE_EDGE_GUARD, max(e_top + 6.0, y_near + pad))
    n_top = min(H - GRAZE_EDGE_GUARD,
                max(e_bot, ground_row(d, h + GRAZE_GUARD_DZ, p, H, tanv)))
    n_bot = H - GRAZE_EDGE_GUARD
    if n_bot - n_top < 20:               # 가드가 근경을 다 먹었다(d2 + 깊은 낙차)
        n_top = max(min(n_top, H * 0.80), e_bot)
    return dict(e_top=e_top, e_bot=e_bot, n_top=n_top, n_bot=n_bot,
                y_haz=y_haz, y_hor=y_hor, tanv=tanv)


def step_field(l):
    """화소별 세로 단차 응답 = (아래 GRAZE_HW행 평균) − (위 GRAZE_HW행 평균)."""
    H = l.shape[0]
    c = np.cumsum(np.pad(l, ((1, 0), (0, 0))), axis=0)
    i = np.arange(H)
    a0, a1 = np.clip(i - GRAZE_HW, 0, H), i
    b0, b1 = np.clip(i + 1, 0, H), np.clip(i + 1 + GRAZE_HW, 0, H)
    up = (c[a1] - c[a0]) / np.maximum(1, a1 - a0)[:, None]
    dn = (c[b1] - c[b0]) / np.maximum(1, b1 - b0)[:, None]
    return dn - up


def graze_delta(Da, Db):
    """행별 (|결맞음 변화|, 변화의 열 부호 일치율).

    **열 평균이 핵심이다.** 낙엽·자갈·소품 같은 등방 클러터는 열마다 부호가
    달라 평균에서 상쇄되고, 화면을 가로지르는 선(낙차 에지·단코)만 살아남는다.
    행 슬랙은 "이미 있던 에지가 1~2행 밀린 것"을 변화로 세지 않기 위한 것이다.
    """
    k = np.ones(GRAZE_SMOOTH) / GRAZE_SMOOTH
    best_c = best_a = None
    for s in range(-GRAZE_SLACK, GRAZE_SLACK + 1):
        dD = Db - np.roll(Da, s, axis=0)
        c = np.convolve(dD.mean(1), k, mode="same")
        a = np.maximum((dD > 0).mean(1), (dD < 0).mean(1))
        if best_c is None:
            best_c, best_a = c, a
        else:
            take = np.abs(c) < np.abs(best_c)
            best_c = np.where(take, c, best_c)
            best_a = np.where(take, a, best_a)
    return np.abs(best_c), best_a


def _band_peak(mag, agr, top, bot):
    n = len(mag)
    a = max(GRAZE_EDGE_GUARD, min(n - 1 - GRAZE_EDGE_GUARD, int(round(top))))
    b = max(a + 1, min(n - GRAZE_EDGE_GUARD, int(round(bot))))
    k = a + int(np.argmax(mag[a:b]))
    return float(mag[k]), k, float(agr[k])


def graze_v2(la, lbn, view, vw):
    """la=이전, lbn=톤 정규화된 신규 (GRAZE_LONG 축소본 휘도). 없으면 None."""
    if not vw or "eye" not in vw or "tgt" not in vw:
        return None
    g = graze_geom(view, vw["eye"], vw["tgt"])
    if g is None:
        return None
    H, W = la.shape
    B = graze_bands(g, H, W)
    Da, Db = step_field(la), step_field(lbn)
    mag, agr = graze_delta(Da, Db)
    dE, rE, agE = _band_peak(mag, agr, B["e_top"], B["e_bot"])
    dN = (_band_peak(mag, agr, B["n_top"], B["n_bot"])[0]
          if B["n_bot"] - B["n_top"] > 4 else 0.0)
    a, b = int(B["e_top"]), int(B["e_bot"])
    ca = np.convolve(Da.mean(1), np.ones(GRAZE_SMOOTH) / GRAZE_SMOOTH, mode="same")
    cb = np.convolve(Db.mean(1), np.ones(GRAZE_SMOOTH) / GRAZE_SMOOTH, mode="same")
    # [v2.1] **낙차행 ±슬랙**에서 이전/신규 각각의 세로 단차 절대값과 그 비.
    # v2 는 `Δcoh`(단차장의 변화량)만 봤기 때문에 "선이 존속하는데 양쪽 알베도가
    # 바뀐 것"과 "선이 사라진 것"을 구분할 수단이 없었다 — 이 두 값이 그 자리를 메운다.
    # 측정 위치는 **최대 변화행 rE 가 아니라 낙차행 y_haz** 다(T3 §3.4-1 축자).
    # rE 로 재면 두꺼운 노출(라이저 0.4~0.8 m)에서 rE 가 밴드 **하단** 에지로 밀려
    # 낙차행과 무관한 지물의 단차를 읽고, 그 결과 진탐이 조용해진다
    # (실측: rE 기준이면 주입 검출 66.7 % → 55.9 %).
    y_h = int(round(min(max(B["y_haz"], B["e_top"]), B["e_bot"])))
    s0 = max(0, y_h - GRAZE_SLACK)
    s1 = min(len(ca), y_h + GRAZE_SLACK + 1)
    if s1 <= s0:
        s0, s1 = max(0, y_h), max(1, y_h + 1)
    step_b = float(np.abs(ca[s0:s1]).max())
    step_a = float(np.abs(cb[s0:s1]).max())
    ratio = step_a / step_b if step_b > 1e-6 else float("inf")
    return dict(spec=dE - dN, dE=dE, dN=dN, agree=agE, row=rE,
                step_b=step_b, step_a=step_a, ratio=ratio,
                row_off=abs(rE - y_h),
                dom=(step_a / dE if dE > 1e-6 else float("inf")),
                up=bool(abs(cb[rE]) > abs(ca[rE])),
                band_mu=min(float(la[a:b].mean()), float(lbn[a:b].mean())),
                d=g["d"], h=g["h"], kind=g["kind"],
                e_top=B["e_top"], e_bot=B["e_bot"], y_haz=B["y_haz"])


# ===========================================================================
# [2] 뷰 인덱싱 — manifest.json 우선, 없으면 파일명 규약
# ===========================================================================
def index_round(d, root):
    """라운드 폴더 → {view: dict(path, mode, ok)}.

    manifest.json 은 `scene_common.capture_pipeline` 이 쓴 구조를 가정한다
    (views/shots, shots[i] = file·mode·sky·view·ok). file 경로는 저장소
    루트 기준 상대경로로 기록되므로 root 를 붙여 푼다. manifest 가 없거나
    깨졌으면 파일명 `{mode}_{sky}_{view}.png` 규약으로 폴백한다.
    """
    out = {}
    cams = {}
    mf = os.path.join(d, "manifest.json")
    if os.path.isfile(mf):
        try:
            j = json.load(open(mf))
            # views[name] = dict(eye, tgt) — GRAZE v2 의 에지 대역 투영에 필수
            cams = {k: v for k, v in (j.get("views") or {}).items()
                    if isinstance(v, dict) and "eye" in v and "tgt" in v}
            for s in j.get("shots", []):
                f = s.get("file", "")
                p = f if os.path.isabs(f) else os.path.join(root, f)
                if not os.path.isfile(p):
                    p2 = os.path.join(d, os.path.basename(f))
                    p = p2 if os.path.isfile(p2) else p
                if os.path.isfile(p):
                    out[s["view"]] = dict(path=p, mode=s.get("mode", "?"),
                                          ok=bool(s.get("ok", True)),
                                          cam=cams.get(s["view"]))
        except Exception as e:                       # manifest 파손 → 폴백
            print(f"[경고] manifest 판독 실패 {mf}: {e}", file=sys.stderr)
    for p in sorted(glob.glob(os.path.join(d, "*.png"))):
        parts = os.path.basename(p)[:-4].split("_", 2)
        if len(parts) == 3 and parts[2] not in out:
            out[parts[2]] = dict(path=p, mode=parts[0], ok=True,
                                 cam=cams.get(parts[2]))
    return out


def is_graze_view(view):
    """grazing 판정 대상 뷰 = h0.3 프리셋(판정 1순위) + grazing 계열 미장센.

    manifest 의 eye z 는 **월드 절대 z** 라 지면이 하강하는 씬에서는 로봇
    눈높이의 지표가 되지 못한다(scene07 side_slope 의 eye z 는 −2.67).
    그래서 grid_views 가 만드는 이름 규약(`preset_h0.3_*`)으로 고른다.
    """
    v = view.lower()
    return ("h0.3" in v) or ("graz" in v)


# ===========================================================================
# [3] 컷 1개 판정
# ===========================================================================
def _add(iss, sev, code, msg):
    iss.append(dict(sev=sev, code=code, msg=msg))


def check_view(scene, view, before, after):
    """(scene, view) 1건 판정. before/after 는 index_round 의 값 dict."""
    r = dict(scene=scene, view=view, verdict="PASS", issues=[], metrics={})
    iss = r["issues"]

    if before is None:
        _add(iss, "INFO", "NEW-VIEW", "이전 라운드에 없던 뷰 — 비교 불가")
    if after is None:
        _add(iss, "FAIL", "MISSING", "신규 라운드에 이 뷰가 없다 — 렌더 누락")
        r["verdict"] = "FAIL"
        return r
    if not after.get("ok", True):
        # `Docs/reports/realism_baseline.md` §알려진 무해한 현상 — capture_pipeline
        # 의 파일 크기 안정화 폴링(40회)이 성급히 끝난 것으로, 파일 자체는 정상.
        # 그래서 INFO 로만 남긴다.
        _add(iss, "INFO", "CAPTURE",
             "manifest ok=false — 캡처 폴링 조기 종료(파일은 정상인 경우가 대부분)")

    gz_want = is_graze_view(view)
    fullB, smallB, blobB, grazB = _load(after["path"], gz_want)
    pb = photometry(fullB)
    r["metrics"].update({("after_" + k): v for k, v in pb.items()})

    # ---- 절대 검사 -------------------------------------------------------
    pa = None
    if before is not None:
        fullA, smallA, blobA, grazA = _load(before["path"], gz_want)
        pa = photometry(fullA)
        r["metrics"].update({("before_" + k): v for k, v in pa.items()})
        if before.get("mode", "?") != after.get("mode", "?"):
            _add(iss, "INFO", "MODE",
                 f"렌더 모드 상이 {before['mode']}→{after['mode']} — "
                 f"톤 정규화로 흡수하지만 절대 측광 비교는 주의")

    def grade(bad, warn, was_bad, worsened):
        """이 도구는 **회귀** 검사기다. 같은 결함이 이전 라운드에도 있었다면
        (= 이월) 등급을 낮춘다. 그러지 않으면 원래 어두운 씬(scene06 나선
        내부·scene13 지하·sceneD4 터널 등 합격 33씬 중 4씬)이 매 라운드
        같은 경보를 쏟아내 표를 못 읽게 된다. 다만 **더 나빠졌으면** 유지한다."""
        sev = "FAIL" if bad else ("WARN" if warn else None)
        if sev is None or not was_bad:
            return sev, "[신규]"
        if worsened:
            return ("WARN" if bad else "INFO"), "[이월 — 악화]"
        return "INFO", "[이월 — 변화 없음, 회귀 아님]"

    # [DARK]
    dark_bad = pb["mean"] < DARK_MEAN_FAIL or pb["dark"] > DARK_PCT_FAIL
    dark_warn = pb["mean"] < DARK_MEAN_WARN or pb["dark"] > DARK_PCT_WARN
    if dark_bad or dark_warn:
        was = pa is not None and (pa["mean"] < DARK_MEAN_WARN
                                  or pa["dark"] > DARK_PCT_WARN)
        wor = pa is not None and (pb["mean"] < pa["mean"] - CARRY_DMEAN
                                  or pb["dark"] > pa["dark"] + CARRY_DDARK)
        sev, tag = grade(dark_bad, dark_warn, was, wor)
        if sev:
            _add(iss, sev, "DARK",
                 f"암흑 mean {pb['mean']:.1f} · dark {pb['dark']:.1f} %  {tag}")

    # [BLOWN]
    blown_bad = pb["mean"] > BLOWN_MEAN_FAIL or pb["clip"] > CLIP_PCT_FAIL
    blown_warn = pb["mean"] > BLOWN_MEAN_WARN or pb["clip"] > CLIP_PCT_WARN
    if blown_bad or blown_warn:
        was = pa is not None and (pa["mean"] > BLOWN_MEAN_WARN
                                  or pa["clip"] > CLIP_PCT_WARN)
        wor = pa is not None and (pb["mean"] > pa["mean"] + CARRY_DMEAN
                                  or pb["clip"] > pa["clip"] + 0.2)
        sev, tag = grade(blown_bad, blown_warn, was, wor)
        if sev:
            _add(iss, sev, "BLOWN",
                 f"과노출 mean {pb['mean']:.1f} · 255클리핑 {pb['clip']:.2f} %  {tag}")

    # [WHITE] — 절대치는 참고, 증가분이 판정
    if pa is not None:
        dw = pb["white"] - pa["white"]
        r["metrics"]["d_white"] = dw
        if dw > WHITE_DELTA_FAIL:
            _add(iss, "FAIL", "WHITE",
                 f"순백(>0.8) 대면적 증가 {pa['white']:.1f}→{pb['white']:.1f} % "
                 f"(+{dw:.1f} pp) — v5.1 §4 금지 규약")
        elif dw > WHITE_DELTA_WARN:
            _add(iss, "WARN", "WHITE",
                 f"순백 면적 증가 {pa['white']:.1f}→{pb['white']:.1f} % (+{dw:.1f} pp)")
        elif pb["white"] > WHITE_PCT_WARN:
            _add(iss, "INFO", "WHITE",
                 f"순백 대면적 {pb['white']:.1f} % [이월 — 픽셀>0.8 은 알베도>0.8 이 "
                 f"아니다. 절대치는 참고값]")
    elif pb["white"] > WHITE_PCT_WARN:
        _add(iss, "WARN", "WHITE", f"순백 대면적 {pb['white']:.1f} %")

    # ---- 회귀 검사 (before 있을 때만) ------------------------------------
    if before is not None:
        la, lb = _lum(smallA), _lum(smallB)
        if la.shape != lb.shape:
            _add(iss, "WARN", "SIZE",
                 f"해상도 불일치 {pa['w']}×{pa['h']} → {pb['w']}×{pb['h']} — 구조 비교 생략")
        else:
            # PT 는 표본 노이즈로 ±1~2 LSB 가 항상 흔들린다. 그 이상 아무것도
            # 안 바뀌었다면 **재렌더·토글이 반영되지 않은 것**이다. 실제로
            # scene01 은 자체 캡처 블록을 쓰느라 공용 토글이 안 먹는 전례가 있다
            # (`Docs/reports/realism_phase1.md` §3.4).
            if fullA.shape == fullB.shape:
                d = np.abs(fullA - fullB)
                dmu = float(d.mean())
                dfr = 100.0 * float((d > 4).mean())
                r["metrics"].update(diff_mean=dmu, diff_frac=dfr)
                if dmu < IDENTICAL_MEAN and dfr < IDENTICAL_FRAC:
                    _add(iss, "WARN", "UNCHANGED",
                         f"이전 라운드와 사실상 동일(평균차 {dmu:.2f} LSB · "
                         f"4 LSB 초과 픽셀 {dfr:.3f} %) — 재렌더·룩 토글이 "
                         f"이 컷에 반영되지 않았을 가능성")

            # [PHOTO] 휘도 분포 급변
            dmean = pb["mean"] - pa["mean"]
            ddark = pb["dark"] - pa["dark"]
            r["metrics"].update(d_mean=dmean, d_dark=ddark)
            if dmean <= PHOTO_DMEAN_FAIL or ddark >= PHOTO_DDARK_FAIL:
                _add(iss, "FAIL", "PHOTO",
                     f"휘도 급락 mean {pa['mean']:.1f}→{pb['mean']:.1f} "
                     f"({dmean:+.1f}) · dark {ddark:+.1f} pp")
            elif dmean <= PHOTO_DMEAN_WARN or ddark >= PHOTO_DDARK_WARN:
                _add(iss, "WARN", "PHOTO",
                     f"휘도 하락 mean {dmean:+.1f} · dark {ddark:+.1f} pp")
            elif dmean >= PHOTO_DMEAN_UP_WARN:
                _add(iss, "WARN", "PHOTO",
                     f"휘도 급상승 mean {pa['mean']:.1f}→{pb['mean']:.1f} "
                     f"({dmean:+.1f}) — 밝아지는 방향(대개 개선). 의도 확인")

            # [OCCL] 신규 암부 = 카메라 차폐의 직접 증거
            nd = (la >= OCCL_BRIGHT_BEFORE) & (lb < DARK_LEVEL)
            nd_pct = 100.0 * float(nd.mean())
            H = nd.shape[0]
            nd_near = 100.0 * float(nd[int(H * NEAR_BAND):].mean())
            ga, gb = _lum(blobA), _lum(blobB)
            blob = largest_blob_pct((ga >= OCCL_BRIGHT_BEFORE) & (gb < DARK_LEVEL))
            r["metrics"].update(newdark=nd_pct, newdark_near=nd_near, newdark_blob=blob)
            if nd_pct > OCCL_NEWDARK_FAIL or blob > OCCL_BLOB_FAIL:
                _add(iss, "FAIL", "OCCL",
                     f"신규 암부 {nd_pct:.1f} % (근거리대 {nd_near:.1f} %) · "
                     f"최대 연결 덩어리 {blob:.1f} % — 신설 기하가 카메라를 삼켰을 가능성")
            elif nd_pct > OCCL_NEWDARK_WARN or blob > OCCL_BLOB_WARN:
                _add(iss, "WARN", "OCCL",
                     f"신규 암부 {nd_pct:.1f} % (근거리대 {nd_near:.1f} %) · "
                     f"덩어리 {blob:.1f} %")

            # [FRAME] 전역 톤 정규화 후 블록 점유율 이동
            lbn = tone_match(lb, la)
            bA, bB = block_means(la), block_means(lbn)
            dblk = np.abs(bA - bB)
            shift = 100.0 * float((dblk > FRAME_BLOCK_DELTA).mean())
            mx = float(dblk.max())
            r["metrics"].update(blk_shift=shift, blk_max=mx)
            if shift > FRAME_SHIFT_FAIL or mx > FRAME_MAXBLK_FAIL:
                _add(iss, "FAIL", "FRAME",
                     f"프레임 점유율 급변 — 이동 블록 {shift:.0f} % "
                     f"(최대 편차 {mx:.0f}/255). 톤 정규화 후 값이므로 "
                     f"밝기 변경이 아니라 **화면 구성**이 바뀐 것")
            elif shift > FRAME_SHIFT_WARN or mx > FRAME_MAXBLK_WARN:
                _add(iss, "WARN", "FRAME",
                     f"프레임 점유율 이동 {shift:.0f} % (최대 편차 {mx:.0f}/255)")

            # [GRAZE v2] 낙차 에지 투영 대역의 수평 결맞음 변화
            if gz_want:
                gz = None
                if grazA is not None and grazB is not None \
                        and grazA.shape == grazB.shape:
                    gz = graze_v2(grazA, tone_match(grazB, grazA), view,
                                  (after.get("cam") or (before or {}).get("cam")))
                if gz is None:
                    _add(iss, "INFO", "GRAZE",
                         f"[{GRAZE_VER}] 판정 유보 — manifest 에 이 뷰의 eye/tgt 가 "
                         f"없거나 시선이 지면을 안 물어 에지 대역을 못 세웠다")
                else:
                    r["metrics"].update(
                        gz_ver=GRAZE_VER, gz_spec=gz["spec"], gz_dE=gz["dE"],
                        gz_dN=gz["dN"], gz_agree=gz["agree"], gz_row=gz["row"],
                        gz_band=[round(gz["e_top"], 1), round(gz["e_bot"], 1)],
                        gz_haz_row=round(gz["y_haz"], 1), gz_d=gz["d"],
                        gz_band_mu=gz["band_mu"],
                        gz_step_b=round(gz["step_b"], 2),
                        gz_step_a=round(gz["step_a"], 2),
                        gz_step_ratio=(round(gz["ratio"], 3)
                                       if math.isfinite(gz["ratio"]) else None),
                        gz_step_off=gz["row_off"],
                        gz_step_dom=(round(gz["dom"], 2)
                                     if math.isfinite(gz["dom"]) else None))
                    band = (f"에지대역 y{gz['e_top']:.0f}~{gz['e_bot']:.0f}"
                            f"/{grazA.shape[0]} (낙차 {gz['d']:.1f} m 지점 y"
                            f"{gz['y_haz']:.0f})")
                    if gz["band_mu"] < GRAZE_BAND_MU_MIN:
                        _add(iss, "INFO", "GRAZE",
                             f"[{GRAZE_VER}] 판정 유보 — 에지 대역이 너무 어둡다"
                             f"(휘도 {gz['band_mu']:.0f} < {GRAZE_BAND_MU_MIN:.0f}). {band}")
                    elif (abs(dmean) > GRAZE_PHOTO_DMEAN
                          or abs(ddark) > GRAZE_PHOTO_DDARK):
                        _add(iss, "INFO", "GRAZE",
                             f"[{GRAZE_VER}] 판정 유보 — 프레임 측광이 흔들렸다"
                             f"(Δmean {dmean:+.1f} · Δdark {ddark:+.1f} pp). "
                             f"조명 회귀를 먼저 처리하고 재실행할 것. {band}")
                    elif (gz["spec"] > GRAZE_SPEC_WARN
                          and gz["agree"] >= GRAZE_AGREE_MIN):
                        # --- [v2.1] 2차 판별 ---------------------------------
                        # 1차(v2)를 통과한 발화에 "그 변화가 은닉을 바꿨는가" 를 묻는다.
                        # 조건은 T3 §3.4-1(존속) 과 §3.4-2·§11-2(방향별 단차비) 를
                        # **하나로 합친 형태**다 — T3 스스로 "2번을 이 형태로 구현하면
                        # 매몰 방향까지 함께 해결된다" 고 적었다.
                        sev = "FAIL" if gz["spec"] > GRAZE_SPEC_FAIL else "WARN"
                        step = (f"단차 {gz['step_b']:.1f}→{gz['step_a']:.1f}"
                                f"(비 {gz['ratio']:.2f})"
                                if math.isfinite(gz["ratio"])
                                else f"단차 {gz['step_b']:.1f}→{gz['step_a']:.1f}")
                        quiet = None
                        # 적용 요건 — 전부 만족해야 2차 판별을 시도한다.
                        #  · WARN 등급만(FAIL 은 절대 강등하지 않는다)
                        #  · 낙차행에 이전·신규 모두 유의한 선이 있다
                        #  · 최대 변화행이 그 선 위에 있다(다른 지물의 변화가 아니다)
                        #  · 존속 선이 변화량을 압도한다(새 라이저가 아니다)
                        eligible = (sev == "WARN"
                                    and gz["step_b"] >= GRAZE_STEP_MIN
                                    and gz["step_a"] >= GRAZE_STEP_MIN
                                    and gz["row_off"] <= GRAZE_PERSIST_ROWTOL
                                    and gz["dom"] >= GRAZE_PERSIST_DOM)
                        if eligible:
                            if gz["ratio"] > 1.0:
                                # 노출 방향 — 선이 오히려 굵어졌다. v2 그대로 발화시킨다.
                                pass
                            elif gz["ratio"] > GRAZE_BURY_RATIO:
                                quiet = ("에지 존속 — 낙차행의 선이 이전·신규 양쪽에 "
                                         f"유의하게 남아 있고({step}) 변화량을 "
                                         f"{gz['dom']:.1f}배 압도한다. 변화의 실체는 에지 "
                                         "양쪽 **지면 알베도**이지 은닉 상태가 아니다")
                        if quiet:
                            _add(iss, "INFO", "GRAZE",
                                 f"[{GRAZE_VER}] 정숙(2차 판별) — 국소도 "
                                 f"{gz['spec']:.1f} 은 임계 초과지만 {quiet}. {band}")
                        else:
                            # 방향 표기는 **낙차행 단차비**로 읽는다(v2 의 `up` 은
                            # 최대 변화행의 크기 비교라 낙차행과 어긋날 수 있다).
                            grew = (gz["ratio"] > 1.0 if math.isfinite(gz["ratio"])
                                    else gz["up"])
                            why = ("에지 대역에 화면을 가로지르는 선이 **생겼다/굵어졌다** → "
                                   "숨어 있어야 할 낙차가 드러났을 가능성" if grew
                                   else "낙차행의 선이 **무너졌다** → 낙차가 과도하게 "
                                        "은폐·매몰됐을 가능성")
                            _add(iss, sev, "GRAZE",
                                 f"[{GRAZE_VER}][의심] 은닉 — 국소도 {gz['spec']:.1f} "
                                 f"(에지 {gz['dE']:.1f} − 근경 {gz['dN']:.1f}) · "
                                 f"열 일치율 {gz['agree']:.2f} · {step} · "
                                 f"최대 변화 y{gz['row']}. "
                                 f"{why}. {band}. **그 대역만 잘라서 육안 확인**"
                                 f"(자동 확정 불가)")

    worst = max((SEV[i["sev"]] for i in iss), default=0)
    r["verdict"] = SEV_NAME[worst] if worst >= 2 else ("INFO" if worst else "PASS")
    return r


def _job(args):
    try:
        return check_view(*args)
    except Exception as e:                          # 한 컷 실패로 전체가 죽지 않게
        scene, view = args[0], args[1]
        return dict(scene=scene, view=view, verdict="FAIL", metrics={},
                    issues=[dict(sev="FAIL", code="ERROR", msg=f"검사 예외: {e}")])


# ===========================================================================
# [4] 씬 페어 수집
# ===========================================================================
def resolve_round(scene_dir, spec):
    """`final_pt_r2,final_pt,ctx2` 처럼 쉼표 폴백을 받아 존재하는 첫 폴더를 준다."""
    for name in [s.strip() for s in spec.split(",") if s.strip()]:
        d = name if os.path.isabs(name) else os.path.join(scene_dir, name)
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*.png")):
            return d
    return None


def collect_pairs(args, root):
    """[(scene명, before_dir, after_dir)] 을 만든다."""
    pairs = []
    if args.list:
        for ln in open(args.list, encoding="utf-8"):
            ln = ln.split("#")[0].strip()
            if not ln:
                continue
            f = [c.strip() for c in ln.replace("\t", " ").split() if c.strip()]
            if len(f) < 3:
                print(f"[경고] 목록 행 무시(3열 필요): {ln}", file=sys.stderr)
                continue
            sd = f[0] if os.path.isabs(f[0]) else os.path.join(root, f[0])
            b, a = resolve_round(sd, f[1]), resolve_round(sd, f[2])
            pairs.append((os.path.basename(sd.rstrip("/")), b, a))
    elif args.scenes:
        for sd in sorted(glob.glob(args.scenes)):
            if not os.path.isdir(sd):
                continue
            b = resolve_round(sd, args.before_round or "")
            a = resolve_round(sd, args.after_round or "")
            if a is None:
                continue                     # 신규 라운드가 아직 없는 씬은 건너뛴다
            pairs.append((os.path.basename(sd.rstrip("/")), b, a))
    else:
        a = args.after
        b = args.before
        name = os.path.basename(os.path.dirname(a.rstrip("/"))) or "scene"
        pairs.append((name, b, a))
    return pairs


# ===========================================================================
# [5] 출력
# ===========================================================================
MARK = {"PASS": "  ", "INFO": "· ", "WARN": "! ", "FAIL": "✗ "}


def print_scene(scene, b, a, rows):
    tag = f"{scene}  [{os.path.basename(b) if b else '(이전 없음)'} → " \
          f"{os.path.basename(a)}]"
    print(f"\n{'='*100}\n{tag}\n{'-'*100}")
    print(f"{'':2}{'view':<22}{'판정':<6}{'mean':>7}{'dark%':>7}{'신규암부':>9}"
          f"{'덩어리':>8}{'블록이동':>9}  사유")
    for r in rows:
        m = r["metrics"]
        def g(k, f="{:.1f}"):
            return f.format(m[k]) if k in m else "-"
        head = (f"{MARK[r['verdict']]}{r['view'][:22]:<22}{r['verdict']:<6}"
                f"{g('after_mean'):>7}{g('after_dark'):>7}{g('newdark'):>9}"
                f"{g('newdark_blob'):>8}{g('blk_shift','{:.0f}'):>9}")
        # FAIL/WARN 사유는 전부 보여 주고, INFO 는 개수만 (경보 피로 방지 —
        # 전부 나열하면 우선순위를 못 읽는다. 전문은 --json 에 남는다).
        loud = [i for i in r["issues"] if SEV[i["sev"]] >= SEV["WARN"]]
        quiet = [i for i in r["issues"] if SEV[i["sev"]] < SEV["WARN"]]
        if not loud:
            note = ("· " + ", ".join(i["code"] for i in quiet)) if quiet else "—"
            print(head + "  " + note)
            continue
        first = True
        for i in sorted(loud, key=lambda i: -SEV[i["sev"]]):
            print((head if first else " " * 70) + f"  [{i['code']}] {i['msg']}")
            first = False
        if quiet:
            print(" " * 70 + "  · " + ", ".join(i["code"] for i in quiet))


def print_summary(all_rows):
    order = {"FAIL": 0, "WARN": 1, "INFO": 2, "PASS": 3}
    bad = [r for r in all_rows if r["verdict"] in ("FAIL", "WARN")]
    n = len(all_rows)
    cnt = {k: sum(1 for r in all_rows if r["verdict"] == k) for k in SEV_NAME}
    print(f"\n{'='*100}\n총평 — {n} 컷 중 "
          f"FAIL {cnt['FAIL']} · WARN {cnt['WARN']} · INFO {cnt['INFO']} · "
          f"PASS {cnt['PASS']}\n{'='*100}")
    # 이월 결함 — 회귀는 아니지만 감독이 알아야 하는 절대 상태
    carry = {}
    for r in all_rows:
        for i in r["issues"]:
            if i["sev"] == "INFO" and i["code"] in ("DARK", "BLOWN", "WHITE"):
                carry.setdefault(i["code"], {}).setdefault(r["scene"], 0)
                carry[i["code"]][r["scene"]] += 1
    if carry:
        print("\n이월 결함 (이전 라운드에도 있던 절대 상태 — 회귀 아님, 참고):")
        for code, sc in sorted(carry.items()):
            tot = sum(sc.values())
            top = ", ".join(f"{s}×{n}" for s, n in
                            sorted(sc.items(), key=lambda kv: -kv[1])[:6])
            print(f"  {code:<6} {tot:>3} 컷 — {top}")

    if not bad:
        print("\n회귀 없음.")
        return
    print("\n우선순위 (FAIL → WARN, 씬순):")
    for r in sorted(bad, key=lambda r: (order[r["verdict"]], r["scene"], r["view"])):
        codes = ",".join(sorted({i["code"] for i in r["issues"]
                                 if i["sev"] in ("FAIL", "WARN")}))
        print(f"  {r['verdict']:<5} {r['scene']:<10} {r['view']:<24} {codes}")
    scenes = {}
    for r in all_rows:
        s = scenes.setdefault(r["scene"], {"FAIL": 0, "WARN": 0})
        if r["verdict"] in s:
            s[r["verdict"]] += 1
    worst = sorted(scenes.items(), key=lambda kv: (-kv[1]["FAIL"], -kv[1]["WARN"]))
    print("\n씬 우선순위:")
    for s, c in worst:
        if c["FAIL"] or c["WARN"]:
            print(f"  {s:<12} FAIL {c['FAIL']:>2} · WARN {c['WARN']:>2}")


# ===========================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="렌더 라운드 회귀 검사기 (이미지 + manifest.json 만 사용)")
    ap.add_argument("--before", help="이전 라운드 폴더 (단일 씬 모드)")
    ap.add_argument("--after", help="신규 라운드 폴더 (단일 씬 모드)")
    ap.add_argument("--scenes", help="씬 폴더 글롭 (예: 'look_check/scene*')")
    ap.add_argument("--before-round", help="씬 안의 이전 라운드 이름. 쉼표 폴백 가능")
    ap.add_argument("--after-round", help="씬 안의 신규 라운드 이름. 쉼표 폴백 가능")
    ap.add_argument("--list", help="씬별 라운드 목록 파일 (씬경로 이전 이후)")
    ap.add_argument("--json", help="기계 판독용 JSON 출력 경로")
    ap.add_argument("--only", help="뷰 이름 부분일치 필터 (쉼표)")
    ap.add_argument("--fail-only", action="store_true", help="FAIL/WARN 컷만 출력")
    ap.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("--root", default=os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))),
        help="저장소 루트 (manifest 의 상대경로 해석 기준)")
    a = ap.parse_args(argv)

    if not (a.list or a.scenes or (a.before and a.after)):
        ap.error("--before/--after, 또는 --scenes + --after-round, 또는 --list 중 하나가 필요합니다.")
    if a.scenes and not a.after_round:
        ap.error("--scenes 모드에는 --after-round 가 필요합니다.")

    root = a.root
    pairs = collect_pairs(a, root)
    if not pairs:
        print("[에러] 비교할 씬을 못 찾았습니다.")
        return 2
    only = [s.strip() for s in a.only.split(",")] if a.only else None

    jobs, meta = [], []
    for scene, bdir, adir in pairs:
        if adir is None or not os.path.isdir(adir):
            print(f"[경고] {scene}: 신규 라운드 폴더 없음 — 건너뜀", file=sys.stderr)
            continue
        A = index_round(adir, root)
        B = index_round(bdir, root) if bdir else {}
        if bdir is None:
            print(f"[경고] {scene}: 이전 라운드 폴더 없음 — 절대 검사만 수행",
                  file=sys.stderr)
        views = sorted(set(A) | set(B))
        if only:
            views = [v for v in views if any(o in v for o in only)]
        for v in views:
            jobs.append((scene, v, B.get(v), A.get(v)))
        meta.append((scene, bdir, adir, views))

    if not jobs:
        print("[에러] 비교할 컷이 없습니다.")
        return 2

    if a.jobs > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=a.jobs) as ex:
            results = list(ex.map(_job, jobs, chunksize=1))
    else:
        results = [_job(j) for j in jobs]

    by = {}
    for r in results:
        by.setdefault(r["scene"], {})[r["view"]] = r
    for scene, bdir, adir, views in meta:
        rows = [by[scene][v] for v in views if v in by.get(scene, {})]
        if a.fail_only:
            rows = [r for r in rows if r["verdict"] in ("FAIL", "WARN")]
            if not rows:
                continue
        print_scene(scene, bdir, adir, rows)
    print_summary(results)

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(dict(
                pairs=[dict(scene=s, before=b, after=c) for s, b, c, _ in meta],
                results=results), f, indent=2, ensure_ascii=False)
        print(f"\n[JSON] {a.json}")

    # 종료코드: FAIL 있으면 1 (배치 스크립트에서 게이트로 쓸 수 있게)
    return 1 if any(r["verdict"] == "FAIL" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
