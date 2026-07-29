# -*- coding: utf-8 -*-
"""
scene05_amphitheater.py — NegObs 인공씬 5호: 근린공원 야외공연장
(Isaac Sim 4.5)

사양서 : Docs/briefs/multi_scene_brief_v5.md §재해석(scene05) — v2 §C 를 대체
공통 라이브러리 : scene_common.py (§A) — boot·make_pbr·build_arc_steps·조명·캡처
모티프 참조 : scene01_campus_stairs.py (main 골격·차콜 밴드·화단·건물)

[v5 채택] 무대 재해석: 전주 원형 sunken 보울 → **반원(200° = 180°+여유 20°)
  야외공연장**. 티어·좌석·립 호를 θ 80..280° 로 절단하고, 절단 단면은 측벽
  (cut_wall, 파라펫 상면 z=+1.0)으로 마감한다. 무대 배후벽(shell) 뒤 동측
  (θ 9..79 / 281..349)은 **잔디 마당**(top −0.06)이 되어 광장 링(−0.002)과
  평지로 접속한다 — 근린공원 야외공연장 전형. 기존 아크 진입 계단(θ ±9°)·
  스테이지·목재 좌석은 그대로 유지, riser/tread/z 는 전부 불변.

유형 정체성: 대단차(−1.2m) × 곡률(반원 보울) × 관행 최소 설비.
  낮은 시점(h0.3)에서 보울이 통째로 소실되는 grazing 은닉이 판정 포인트.
  [v5 공통 레이어] cue_tactile 기본 True(도시 관행 씬) + sign_info 1매.

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene05_amphitheater.py

[v7 판정 재수정] judge_v7_rt_B §4 — 잔여 3건 전부 담당.
  ① 신설 배후 관목이 **"이끼 낀 바위 등간격 열"**(scene04 v6 verge 와 동일
     실패 모드 = 덩이 크기 × 확대 텍스처). → 상수색 tuft 3종 + **작은 로브
     스택**(개체 ≤0.46 m, 군락 상단 1.28 m 유지) + 2열·지터·결측.
     검산 `backdrop_selfcheck()`.
  ② 승강 계단 아크의 **예각 쐐기**. 원인은 build_arc_steps 현길이(r_out 기준)
     가 r_in 까지 내려오는 데서 오는 초승달 틈(15.3 mm)과 호끝 슬리버(42 mm).
     → seg 3→12(틈 1.05 mm · 돌출 10.6 mm) + **마구리(치크) 2장/조**.
     검산 `podium_step_selfcheck()`. 반경·각도·상면 z 불변 = 기하 GT 불변.
  ③ **림 스카이라인 백색 포스트 등간격 열**의 실체 = 서측 볼라드 10본
     (간격 2.67 m · 폭 24 m 장식 열). → 진입축 게이트 **4본 · 규정 1.5 m**,
     재질 도장 강재. v5.1 §2/§3 동시 해소.
  ④ (공통) §4 순백 대면적 자가검사 `albedo_selfcheck()` 신설 — 광장 포장은
     전 씬 공통 항목이라 WAIVED(감독 전역 결정 대기)로 명시 기록.

자가검사 (부팅 없음, 렌더 없음):
    NEGOBS_SMOKE=1 python scene05_amphitheater.py

자동 캡처 모드 (headless 검증용):
    NEGOBS_CAPTURE=1 python scene05_amphitheater.py
      NEGOBS_CAPTURE_DIR  : 저장 폴더 (기본 look_check/scene05/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (기본 rt)
      NEGOBS_VIEWS        : 쉼표로 뷰 이름 필터 (기본 전부)

좌표계: Z-up, m, 진행축 +X. 보울 중심 (6, 0). 광장 상면 z=0.
"""

import os
import sys
import math
import json
import random
import datetime

import numpy as np

import scene_common as sc


# ===========================================================================
# [A] SCENE_CONFIG — scene01 동일 6키 + cue_nosing(신규).
#     hazard_stairs 만 위험 기하 토글(보울 ↔ 평지). 나머지는 기하 불변.
#     ** cue_railing·cue_tactile 기본 False = 설비 전무 유형 정체성 **
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # 선큰 보울 기하 (False → z=0 평지로 통일)
    "cue_railing":        False,   # True → 립 부분 호 난간(선택 구현)
    # [v5 공통 레이어] 도시 관행 씬(01/02/05/13/14/16/20/21) cue_tactile 기본 True
    "cue_tactile":        False,  # [v5.2 사용자] 점자블록 현실에선 드묾 — 기본 OFF(소거 실험용 경로 유지)    # −X 접근 경고 점자띠 (립 밖 x −2.3..−1.9)
    "cue_material_break": True,    # 립 연석 링(다크) + 티어(밝은 화강암) vs 스테이지(회청)
    "cue_nosing":         False,   # [신규 예약] True → 곡선 단코 논슬립 아크 밴드(선택 구현)
    "cue_sign":           False,  # [v5.2] 팻말 제거    # [v5 공통 레이어] 한글 사인 (sc.build_sign)
    "cue_scene_dressing": True,    # 화단·생울타리·벤치·가로등·건물 일괄
}


# ===========================================================================
# [B] PARAMS — 치수표 + 재질/조명/캡처. NEGOBS_PARAMS_OVERRIDE 로 머지 가능.
# ===========================================================================
PARAMS = dict(
    # --- 상부 광장 (x −18..18, y −14..14, z=0) ---
    plaza=dict(x0=-18.0, x1=18.0, y0=-14.0, y1=14.0, z_top=0.0, thick=0.5),
    # 차콜 밴드: Y 방향으로 달리는 granite_dark 띠, X 간격 3.2, 1.5mm 돌출
    band=dict(width=0.45, spacing=3.2, proud=0.0015, embed=0.05),

    # --- 선큰 보울 (중심 (6,0), [v5 채택] 반원 200°) ---
    #   3티어 × riser 0.40 · tread 0.85(좌석 규격) — build_arc_steps 3회 호출.
    #   [v5 채택] a0=80..a1=280 (200° = 180°+여유 20°). 서측(θ=180) 관람석 반원 +
    #     동측(무대 배후벽 뒤)은 잔디 마당. seg 32(360°) → 18(200°) 으로 조정해
    #     세그 각폭 11.25° → 11.11° 유지(현길이·쐐기 여유 규약 동일).
    #   위험 기하 불변: r_in/r_out/top_z/base_z/riser(0.40)·tread(0.85) 전부 동일.
    bowl=dict(
        cx=6.0, cy=0.0, base_z=-1.6, seg=18, a0=80.0, a1=280.0, open_r=7.5,
        tiers=[dict(r_in=6.65, r_out=7.5,  top_z=-0.40),   # 티어1 (상연)
               dict(r_in=5.8,  r_out=6.65, top_z=-0.80),   # 티어2
               dict(r_in=5.0,  r_out=5.8,  top_z=-1.20)],  # 티어3 (스테이지 접연)
    ),
    # 광장 링 슬래브: 원형 개구를 박스로 못 뚫으므로 보울 둘레는 아크 링으로 근사.
    #   top_z=-0.002 : 프레임 박스(z=0)와의 동일평면 Z파이팅 회피용 1~2mm 오프셋.
    ring=dict(r_in=7.5, r_out=12.0, seg=48, top_z=-0.002, base_z=-0.5),
    # === v4-A1 [치명] 스테이지-티어3 관통 공극 수정 ===
    #   기존: UsdGeom.Cylinder(r=5.0) 단독. Cylinder 는 뷰포트 refinement 에 따라
    #   저폴리 다각형으로 테셀레이션돼 면 중앙 반경이 5.0·cos(π/n) 로 안쪽으로
    #   들어가고, 티어3 내면은 세그 끝에서 5.0/cos(5.625°)=5.0242 로 바깥으로
    #   물러난다 → 겹치는 지점에서 폭 최대 0.25 m 의 관통 공극(실제 낙차).
    #   해결: '내부 원반(4.9) + 32세그 아크 림(4.2..5.22)' 2중 구조.
    #     · 림 외경 최소 반경 5.22 > 티어3 내면 최대 5.0242 → 겹침 0.196 보장
    #       (테셀레이션 무관하게 공극 0).
    #     · 림이 32세그이므로 스테이지 외곽 실루엣의 '다각형' 인상(B-2)도 해소.
    #     · z 캐스케이드 −1.200(티어3) > −1.203(림) > −1.207(원반) 으로
    #       동일평면 Z파이팅 회피(단차는 3~4 mm — 시각적으로 불가시).
    stage=dict(radius=4.9, top_z=-1.207, height=0.4,
               rim=dict(r_in=4.2, r_out=5.22, seg=32, top_z=-1.203,
                        base_z=-1.6)),
    # === [v5.1 현실성] 원형 무대 단(podium) — "무대부가 더 솟아야 한다" ===
    #   구: 보울 바닥(−1.207) 전체가 무대 → 관람석 최하단(티어3 상면 −1.20)과
    #     사실상 동일 레벨이라 '무대'로 읽히지 않고 바닥 원반으로만 보였다.
    #   신: 보울과 **동심**인 원형 단을 0.70 m 솟게 한다(상면 −0.507).
    #     · 티어3 착석면(−1.20) 대비 유효 무대고 0.693 m → 실제 야외무대의
    #       표준 무대고(0.6~0.9 m) 대역. 피드백 지시 h 0.6~0.9 충족.
    #     · 반경 3.0 → 단 둘레에 폭 1.9 m 의 에이프런(−1.203)이 남아 진입
    #       아크 계단(r 4.99 착지)에서 무대 앞까지 평지 접속이 유지된다.
    #       **진입 계단·티어(위험 기하)는 트랜스폼 불변.**
    #     · 무대 라인(원호)을 배후벽 shell(r 4.75..5.25, θ 9..80/280..351,
    #       N-4 에서 호벽으로 확장 완료)과 동심으로 맞춰 '직선 슬라브' 잔재는
    #       현재 코드에 남아 있지 않음을 확인했다(build_bowl/build_halfbowl_finish
    #       전부 build_arc_steps 기반, 직사각 슬라브는 광장·지반 전용).
    #   보행 연속성(에이프런 → 무대): −1.203 → −1.032 → −0.857 → −0.682 →
    #     −0.507. 단차 0.171 / 0.175 ×3 — 0.2 m 초과 없음.
    # [v5.2 사용자] 단 높이 0.70 → 0.35 — "가볍게 폴짝 올라갈 수 있을 정도".
    #   상면 −1.203+0.35 = −0.853, 승강 계단은 1중간단(0.175×2)으로 축소.
    # === [v7 판정 §4 잔여2] 승강 계단 아크의 **예각 쐐기 / 나이프 에지** ===
    #   증상(judge_v6 §4 ③ → v7 미해소): `rim_view`·`side_arc` 400 % 크롭에서
    #     호 안쪽 반경이 급격히 좁아져 나이프 에지 삼각 조각이 보인다.
    #   원인 2개(build_arc_steps 규약을 좌표로 추적):
    #     ⓐ 세그 박스의 현길이는 **r_out 기준**(2·r_out·sin(dθ/2)·1.03)인데
    #        같은 박스가 r_in 까지 내려온다. seg=3(dθ 10°)에서 r_in=3.0 의
    #        모서리 반경은 √(3.0²+(현/2)²) = 3.0153 → 무대 단 원기둥(r 3.0)과
    #        **최대 15 mm 의 초승달 틈**이 세그마다 생긴다(400 % 에서 검은 쐐기).
    #     ⓑ 호 양끝 세그의 마구리면이 반경선이 아니라 a_mid 기준으로 5° 기울어
    #        나온다 → 계단 끝에 **얇은 삼각 슬리버**가 돌출한다.
    #   조치(판정 권고 ㉡ "각도범위 축소 또는 안쪽 반경 필렛/마구리"):
    #     ㉠ seg 3 → **12**(dθ 2.5°). ⓐ 틈 15 mm → **0.9 mm**, ⓑ 돌출 0.042 →
    #        0.011 m. 곡률만 세밀해질 뿐 반경 사다리·tops 는 불변 = **기하 GT 불변**.
    #     ㉡ 양단에 **마구리(치크) 1장씩** 신설 — 반경 3.0..3.75 · 상면 = 무대 단
    #        상면(−0.853) · 두께 3.2°(≈0.19 m). 실제 계단 치크월과 같은 마감이라
    #        끝단이 '뾰족한 조각'이 아니라 **각진 마구리**로 읽힌다.
    #        (에이프런 −1.203 대비 0.35 m = 무대 단과 동일 낙차 → 신규 위험 0)
    #   승강 계단·무대 단은 위험 기하(티어·진입 아크 계단)가 아니며 반경·각도
    #   범위·상면 z 는 전부 그대로다.
    podium=dict(r=3.0, top_z=-0.853, base_z=-1.607,
                steps=dict(radii=(3.75, 3.375, 3.0),
                           tops=(-1.028, -0.853),
                           seg=12, base_z=-1.6,
                           arcs=((130.0, 160.0), (200.0, 230.0)),
                           cheek_deg=3.2, cheek_overlap=0.2)),
    # === v4-A2/A3 [치명] 진입 계단 재설계 ===
    #   기존: 직교 플라이트(x_top 13.5, tread 0.35). 단 경계 x 와 티어 경계
    #   x(=6+r) 가 전혀 정렬되지 않아 실제 보행 프로파일의 디딤폭이
    #   0.35/0.35/0.15/0.20/0.35/0.30/**0.05**/0.35 로 붕괴, 폭 5 cm 디딤면 +
    #   0.40 m 단발 낙차(점프 구간)가 생겼다. 또 원호 에지 × 직사각 플라이트라
    #   좌우에 최대 0.09 m 초승달 쐐기가 남았다.
    #   해결: 계단을 **티어와 동심인 아크 계단**으로 교체. 반경 사다리를
    #   티어 경계(7.5 / 6.65 / 5.8 / 5.0)를 정확히 포함하도록 0.425 간격으로
    #   6등분 → 전 구간 riser 0.20 · tread(반경) 0.425 균일, 쐐기 0.
    #     프로파일: 링(−0.002) → −0.197 → −0.397(=티어1+3mm) → −0.597
    #               → −0.797(=티어2+3mm) → −0.997 → −1.197(=티어3+3mm) → 스테이지
    # === [v5 판정 반영] 진입 아크 계단 라이저의 백색 사각 패치 제거 ===
    #   증상: preset_h1.8_d2 (860,460–1010,560) 에서 석재 텍스처 라이저 위에
    #     텍스처 없는 순백 직사각형이 좌우 대칭 1쌍씩, **한 단 걸러** 반복.
    #   원인(추적): 흰 패치가 나타나는 단은 Step_1/3/5 뿐이고, 이 세 단의
    #     내경(r_in)이 각각 6.65 / 5.8 / 5.0 으로 **티어1/2/3 의 내경과 정확히
    #     동일**하다. 즉 계단 라이저면(진입 seg 4, dθ=4.5°)과 티어 내면
    #     (seg 32, dθ=11.25°)이 같은 반경의 동일평면이면서 세그 분할만 달라
    #     두 평면이 스치듯 교차한다 → 교차 근방에서 깊이 정밀도 이내로 붙어
    #     Z-다툼. 위로 올라온 쪽이 티어 재질(plaza_light = 밝은 무늬 없는 화강암)
    #     이라 '텍스처 없는 순백 사각형'으로 보인 것. 좌우 1쌍인 이유는
    #     두 평면이 θ = ±(진입 seg 중앙과 티어 seg 중앙의 중점)에서 교차하기 때문.
    #     (세그 간 겹침은 chord×1.03 로 이미 확보돼 있어 '틈'이 원인이 아니다.)
    #   해결: 진입 계단 반경 사다리 전체를 **10 mm 안쪽으로 이동**(r-캐스케이드).
    #     기존 z-캐스케이드(−1.200 > −1.203 > −1.207)와 같은 취지의 반경판.
    #     · 진입 라이저면이 그리는 반경 범위 = r .. r/cos(2.25°) = r + 5.1 mm
    #       → 6.640..6.6451 < 티어 내면 최소 6.650. 전 구간 4.9 mm 이상 이격.
    #       (티어2 5.5 mm · 티어3 6.1 mm 이격 — 동일평면 소멸)
    #     · 진입 단이 티어보다 10 mm 앞(안쪽)에 서므로 티어면이 확실히 가려진다.
    #   위험 기하 불변 확인: tops(라이저 높이 0.20 × 6단 · 총 낙차 1.2 m)와
    #     a0/a1/seg/base_z 전부 불변. 디딤폭도 최상단만 0.425→0.435, 나머지
    #     0.425/0.375 그대로 — 보행 프로파일 동일.
    entry=dict(a0=-9.0, a1=9.0, seg=4, base_z=-1.6,
               radii=(7.5, 7.065, 6.64, 6.215, 5.79, 5.365, 4.99),
               tops=(-0.197, -0.397, -0.597, -0.797, -0.997, -1.197)),
    # v4-D5: 관람석 통로 계단 2 (극장 문법) — 진입 계단과 동일 반경 사다리
    aisles=[dict(a0=100.0, a1=112.0, seg=3), dict(a0=248.0, a1=260.0, seg=3)],
    # 립 연석 링 (cue_material_break): 개구 밖 다크 화강암 링.
    #   [v5 채택] 티어와 동일하게 200° 로 절단 (seg 48→27, 각폭 7.5°→7.41°).
    lip=dict(r_in=7.5, r_out=7.8, seg=27, a0=80.0, a1=280.0,
             top_z=0.003, base_z=-0.1),
    # === [v5 채택] 반원화 마감 3종 ===
    #  ① cut_wall — 절단 단면 측벽(파라펫). θ 79..82 / 278..281 에 반경방향 벽.
    #     r 5.0..7.85 로 티어 3단 절단면(z −0.40/−0.80/−1.20)과 립(7.8)까지 덮고,
    #     상면 z=+1.00 → 잔디 마당(−0.06) 기준 1.06 m 방호벽 = 새 에지 낙차 방호.
    #     (마당에서 티어3 상면까지 최대 낙차 1.14 m 를 이 벽이 전 구간 차단)
    #  ② backyard — 무대 배후벽 뒤 잔디 마당. θ 11..79 / 281..349, r 5.25..7.5.
    #     상면 −0.06(광장 링 −0.002 대비 0.058 m 단차 = 평지 접속), 저면 −1.6
    #     (제거된 티어 볼륨을 그대로 채워 하부 공동 0). 내측 경계 r=5.25 는
    #     shell(무대 배후벽, r 4.75..5.25)이 전 각도 구간에서 받친다.
    #  ③ entry_cheek — 진입 아크 계단(θ ±9°) 양 옆 치크월. θ 9..11 / 349..351,
    #     r 4.99..7.5, 상면 −0.06(마당과 플러시) → 마당–계단 사이 단면 폐합.
    cut_wall=dict(r_in=5.0, r_out=7.85, seg=1, top_z=1.00, base_z=-1.6,
                  arcs=((79.0, 82.0), (278.0, 281.0))),
    backyard=dict(r_in=5.25, r_out=7.5, seg=8, top_z=-0.06, base_z=-1.6,
                  arcs=((11.0, 79.0), (281.0, 349.0))),
    entry_cheek=dict(r_in=4.99, r_out=7.5, seg=1, top_z=-0.06, base_z=-1.6,
                     arcs=((9.0, 11.0), (349.0, 351.0))),
    # [v5 공통 레이어] 한글 사인 — (태그, TEX 키, cx, cy, base_z, yaw, w, h)
    #   Info(-4.2, 3.6): 게이트(x −3.6, y ±2.6) 옆 −X 접근축. 보울 중심(6,0)에서
    #     10.82 m → 립(r 7.5) 밖 3.32 m (≥0.5 m 이격 충족).
    #   카메라 검산: 그리드 eye=(−3.5/−6.5/−11.5, 0) → 각각 후방 / 57.4° / 26.3°,
    #     plaza_approach 63.4°, rim_view 후방, side_arc 36.9°, stage_lookup 19.5°
    #     (10.8 m 원경) — 어느 프리셋도 시선 근접 차폐 없음.
    signs=[],  # [v5.2 사용자] 안내 팻말 제거 — 개방감

    # --- 드레싱 ---
    planters=[("A", -10.0, -9.0), ("B", -12.0, 8.0)],
    # v4-D8: 립 둘레 가로수 열 — r=9.6 원주 45° 간격(진입축 0°·게이트 180° 제외)
    # [v5 판정 반영] 270° 화단은 중심이 (6, −9.6) 이라 side_arc 카메라
    #   eye(6, −10, 1.2) 와 0.4 m — 카메라가 화단 박스(2.2각) 안에 들어가고
    #   줄기가 화면 전폭을 가려 컷 자체가 무효였다(rt_noon_side_arc 확인).
    #   → 270° → 285°. 중심 (8.484, −9.273) 으로 카메라 밖으로 빠지고,
    #     시선축(+Y)에서 화단 최근접 모서리가 37°(수평 화각 ±30° 밖)에 놓여
    #     프레임에 들어오지 않는다. 벤치 원주(r=9.0, 250°)와도 간섭 없음.
    #   (다른 5본은 side_arc 시선에서 측방 이격이 충분해 그대로 둔다.)
    ring_planters=[45.0, 90.0, 135.0, 225.0, 285.0, 315.0],
    ring_planter=dict(r=9.6, size=2.2, base_z=-0.002),
    # v4-B4/A4: 어긋난 생울타리 3장(y 12.0/12.4/12.0) 제거 → 광장 둘레
    #   생울타리로 재편. 0.51 m 무방비 낙하 은폐 + 대지 종결 + 어긋남 소멸.
    #   개구: −X 접근(서측 전체), 남측 x −3..3, 북측 x −8..−4(건물 출입).
    hedges=[(-18.0, 13.4, -8.0, 14.0), (-4.0, 13.4, 18.0, 14.0),
            (17.4, -13.4, 18.0, 13.4),
            (-18.0, -14.0, -3.0, -13.4), (3.0, -14.0, 18.0, -13.4)],
    hedge_h=0.6,
    # v4-A4: 광장 둘레 0.51 낙하를 잔디 뱅크(−0.26)로 2단 분할.
    berms=[("W", -19.2, -18.0, -15.2, 15.2), ("E", 18.0, 19.2, -15.2, 15.2),
           ("S", -18.0, 18.0, -15.2, -14.0)],
    berm=dict(top_z=-0.26, base_z=-0.9),
    # 북측은 뱅크 대신 건물 앞 포장 에이프런 (건물 접지 개선)
    apron=dict(x0=-18.0, x1=18.0, y0=14.0, y1=15.5, top_z=-0.26, base_z=-0.9),
    entry_canopy=dict(x0=-8.0, x1=-4.0, y0=14.2, y1=15.5, z_roof=3.2,
                      post_r=0.10, roof_t=0.14, base_z=-0.26),
    # v4-A4: 서측(개방 접근면) 볼라드 열
    # === [v7 판정 §4 잔여3] "림 스카이라인 백색 포스트 등간격 열 7본" ===
    #   실체 추적: cue_railing 은 False 이므로 난간 포스트가 아니라 **서측 볼라드
    #     열**이다. 구 (x −17.2, y −12..12, n 10)은 간격 2.67 m 로 광장 서변
    #     24 m 를 통째로 두르는 **장식 열**이라 v5.1 §2("차량 진입 우려 지점만,
    #     간격 1.5 m 내외, 장식적 볼라드 열 전면 제거")와 §3(등간격 금지) 동시
    #     저촉. `stage_lookup`(eye 6,0 → −X)에서 지평선에 7본이 도열해 보였다.
    #   조치: **진입축(y=0) 게이트 4본 · 규정 간격 1.5 m** 로 축소(y ±0.75, ±2.25).
    #     scene01 이 백색 볼라드 6본을 전량 소거해 PT 진출한 선례와 같은 방향이되,
    #     이 씬은 −X 가 실제 광장 보행 진입부라 기능 근거가 있으므로 존치한다.
    #     재질도 백색 스테인리스(M["rail"]) → **도장 강재 다크그레이**(M["bollard"])
    #     로 바꿔 "백색 포스트" 신호 자체를 없앤다(§4).
    bollards=dict(x=-17.2, spacing=1.5, n=4, base_z=0.0),
    # v4-B5/D9: 벤치 2 → 6. 보울 중심 (6,0) 기준 r=9.0 원주에 접선 배치.
    bench_ring=dict(r=9.0, base_z=-0.002,
                    angles=(110.0, 135.0, 160.0, 200.0, 225.0, 250.0)),
    # v4-D4: 좌석 목재 스트립 (티어를 좌석으로 읽히게 + 단 대비 확보).
    #   진입(±9°)·통로(100~112 / 248~260) 구간은 비운다.
    #   [v5 채택] 반원 절단(80..280)에 맞춰 재단: 80.5~99.5 / 112.5~247.5 /
    #   260.5~279.5 (통로 100~112 · 248~260 은 그대로 비움).
    seat=dict(width=0.45, inset=0.10, proud=0.012, drop=0.06,
              arcs=((80.5, 99.5, 3), (112.5, 247.5, 12), (260.5, 279.5, 3))),
    # v4-D1 [최우선] 무대 배후벽(스테이지 셸) — 진입 아크(±9°)를 비운 2조각
    #   [v5 채택] 14..76 / 284..346 → 9..80 / 280..351 로 확장.
    #     · 하단 9/351 = 진입 계단 폭과 정확히 일치 → 문틀(jamb) 완성.
    #     · 상단 80/280 = 티어 절단면(cut_wall)과 접합 → 마당 내측 경계 전 구간
    #       방호(마당 −0.06 → 스테이지 −1.207 의 1.15 m 낙차를 벽이 차단).
    # === [v6 판정 ㉠] 배후 아크벽 인하 1.40 → 0.70 (개방감 / v5.2 §6) ===
    #   증상(judge_v6_rt_mod6 §4): plaza_approach·preset_h0.9_d5 에서 배후 아크벽이
    #     "프레임 폭 100% 를 막는 무장식 콘크리트 옹벽(저수조/벙커)"으로 읽힘.
    #   조치: 상단 z +1.40 → +0.70.
    #     · 무대(−1.207) 기준 벽면 2.61 → 1.91 m (회색 면적 −27%, 실제 야외무대
    #       배후벽 스케일). 마당(−0.06) 기준 0.76 m = 앉음벽/난간벽 높이.
    #     · 실루엣 상단 1.40 → 1.04(관목 완충대 상단) 로 −0.36 m — 그 위로 하늘·녹지.
    #   호 길이(9..80 / 280..351)는 **불변**: 이 벽이 마당(−0.06) 내측 경계 전
    #     구간에서 무대(−1.207)로의 1.15 m 낙차를 받치는 옹벽이라, 호를 줄이면
    #     방호 없는 낙차 에지가 생긴다. 대신 낮춘 만큼을 아래 backdrop_shrub
    #     (관목 완충대)로 대체한다.
    shell=dict(r_in=4.75, r_out=5.25, top_z=0.70, base_z=-1.6, seg=12,
               arcs=((9.0, 80.0), (280.0, 351.0))),
    # === [v6 판정 ㉠] 배후 관목 완충대 — 아크벽 인하분 대체 + "무대 뒤 녹지" ===
    #   마당(top −0.06) 위, 아크벽 바로 뒤 r 5.25..6.05(폭 0.80) 밴드에 관목을
    #   호를 따라 spacing 0.62 m 로 심는다(편평 타원체, 좌표 시드 지터 → §3
    #   등간격·격자 인상 회피). 상단 ≈ +1.12 = 마당 기준 1.18 m.
    #   낙차 방호(마당 −0.06 → 무대 −1.207, 1.15 m): 아크벽 0.76 m + 폭 0.80 m·
    #     h1.18 관목 완충대 = 접근 억제. (규정 난간 1.1 m 를 벽 단독으로 만족하던
    #     구 상태보다 방호는 약해지나, v5.2 §6 개방감 우선 + 공원 관행(낮은
    #     옹벽 + 식재대) 조합. 감독 판단으로 top_z 만 되돌리면 원복 가능.)
    #   호 범위는 마당(11..79 / 281..349) 안쪽으로 1° 여유.
    # === [v7 판정 §4 잔여1] 신설 관목이 **"이끼 낀 바위 등간격 열"** 로 렌더 ===
    #   증상(judge_v7_rt_B §4): `plaza_approach` 벽 상단 밴드 400 % 크롭에서
    #     편평 타원체(rad 0.42 · h 1.10)에 확대 grass 텍스처(M["hedge"], uv 1.2)가
    #     물려 **황록 이끼 바위 덩어리**로 읽히고, spacing 0.62 등간격 도열이
    #     "벽 위에 얹은 돌"을 만든다. scene04 v6 verge 와 **동일 실패 모드**.
    #   원인(판정 §15-2 일반화): **덩이 크기 × 확대 텍스처**. 둘 다 줄여야 한다.
    #   조치 = scene04 W-4 해법 이식 + 이 씬 고유 제약(실루엣 높이) 보정:
    #     ㉠ 재질 : grass 텍스처 폐기 → **상수색 tuft 3종**(±5 % 틴트 지터,
    #               rough 1.0 · specular 0). 텍스처가 없으면 '암괴 요철' 신호 0.
    #     ㉡ 크기 : 개체(로브) rz ≤ 0.25 = **0.5 m 이하**(판정 권고 ①).
    #               단, 이 씬은 관목 상단이 아크벽(+0.70) 위로 나와야 "벽 위 녹지"
    #               라는 v6 달성분이 유지되므로 **높이를 잃으면 안 된다** →
    #               큰 타원체 1개가 아니라 **작은 로브 3~4개를 세로로 겹쳐 쌓아**
    #               군락 상단 1.22 m 를 만든다(수관이 여러 덩이로 갈라진 관목).
    #     ㉢ 배치 : 1열 등간격 → **3열**(r 5.62/5.98/6.32) · 열별 step 다름 +
    #               간격 지터 ±35 % + 결측 12 % + 로브별 위치/크기 지터
    #               → 등간격 도열 인상 소멸(§3).
    #   행 정의 rows: (r, step, rx, rz, h_top, n_lobe)
    #     · 2열(전열 1.02 / 후열 1.24) — 벽 위 실루엣이 한 덩이가 아니라 층진
    #       녹지 밴드가 된다. 아크벽(+0.70)보다 낮은 지피층은 어느 컷에서도
    #       보이지 않으므로(카메라가 전부 −X 광장측) 프림만 늘어 배제했다.
    #     · 반경 검산: 최내측 5.85 − 0.075 − 0.36·1.15 = 5.36 ≥ 아크벽 5.25 ✓
    #                  최외측 6.25 + 0.075 + 0.40·1.15 = 6.79 ≤ 마당 7.5 ✓
    #     · 로브 겹침: 인접 로브 z 간격 ≤ 1.35·min(rz) 로 잡아 **분리 부유 0**
    #       (검산 ⑦ 이 지터 최악 조합의 실측 최대비를 낸다).
    #     · taper: 위 로브일수록 반경 ×(1−0.14t) → 수관 테이퍼(원기둥 인상 회피).
    backdrop_shrub=dict(base_z=-0.06, embed=0.5, taper=0.14,
                        jit_step=0.35, skip=0.12, jit_pos=0.075,
                        jit_scale=0.15, jit_h=0.12,
                        rows=((5.85, 0.44, 0.36, 0.19, 1.02, 6),
                              (6.25, 0.52, 0.40, 0.20, 1.24, 7)),
                        arcs=((12.0, 78.0), (282.0, 348.0))),
    # v4-D2 조명 타워 2 / D3 스피커 스택 2
    towers=[(10.5, -6.5), (10.5, 6.5)],
    tower=dict(pole_r=0.10, pole_h=5.5, head=(0.35, 0.35, 0.25),
               head_z=(3.5, 4.3, 5.1), base_z=-0.002),
    speakers=[(7.8, -3.2), (7.8, 3.2)],
    speaker=dict(size=(0.6, 0.5, 0.9), n=2, base_z=-1.207),
    # v4-D7 입구 게이트 + 사인
    gate=dict(x=-3.6, y=2.6, post_r=0.10, post_h=3.0, base_z=-0.002,
              lintel_z0=2.6, lintel_z1=3.0, lintel_t=0.15, lintel_y=2.75),
    streetlight=dict(pole_h=6.0, pole_r=0.06,
                     arm_len=1.0, arm_r=0.04, head=0.25),
    # v4-D10: 가로등 1 → 5. (x, y, base_z)
    streetlights=[(-8.0, 10.0, 0.0), (-14.0, 10.0, 0.0), (-14.0, -10.0, 0.0),
                  (2.0, 12.0, 0.0), (14.0, -11.0, 0.0)],
    buildings=dict(
        # R: scene01 R 배치를 y 15.5..20 으로 이동, x −18..12. 파사드 −Y(광장 향).
        R=dict(x0=-18.0, x1=12.0, y0=15.5, y1=20.0, h=14.0, floors=4,
               axis="y", facade_y=15.5, face_dir=-1.0),
        # C: 원경 비스타 차단(+X 지평선). 파사드 −X(광장 향).
        # [v6 판정 ㉠ 보조] h 12.0(4층) → 7.2(2층). 배후 아크벽을 낮춰도 그 위가
        #   전부 이 건물 벽돌면이면 "하늘이 보이게" 라는 판정 목표가 달성되지
        #   않는다(plaza_approach 검산: 파라펫 상단 12.5 m·거리 30 m → 앙각
        #   21.2° > 프레임 상단 17.7° = 화면 위쪽 전부 벽돌).
        #   7.2 로 낮추면 상단 7.7 m → 앙각 12.8° 로 프레임 상단까지 4.9°
        #   (≈130 px) 의 하늘 띠가 열린다. 근린공원 연접 저층 근생 스케일이라
        #   비스타 차단 기능(원경 지평선 폐쇄)은 그대로 유지된다.
        C=dict(x0=24.0, x1=30.0, y0=-12.0, y1=12.0, h=7.2, floors=2,
               axis="x", facade_x=24.0, face_dir=-1.0),
    ),

    # --- 재질: texture_scale 용 물리 크기[m/타일] + 틴트/상수 ---
    material=dict(
        scale=dict(plaza_light=1.80, band_dark=0.9, plaza_lower=0.7,
                   granite_dark=1.0, brick_red=2.0, grass=1.4, tactile=0.3),
        lower_warm_tint=(1.06, 1.0, 0.94),        # 스테이지 웜 틴트
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        # v4-B(공통): 수관 알베도 상향 (검은 얼룩 → 잎 실루엣)
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030),
        canopy_rough=1.0,
        hedge_tint=(0.50, 0.62, 0.36),                   # v4 둘레 생울타리
        # [v7 판정 §4 잔여1] 배후 관목 = 상수색 tuft 3종 (scene04 W-4 이식).
        #   grass 텍스처(uv 1.2)를 물리면 확대 노멀맵이 곧바로 '이끼 낀 바위'가
        #   된다 → 텍스처를 아예 쓰지 않는다. 값은 scene04 verge 와 동일 계열
        #   (밝은 초록 / 마른 초록 변주)로 21씬 식생 톤 통일.
        tuft=((0.070, 0.105, 0.042), (0.082, 0.112, 0.050),
              (0.078, 0.096, 0.038)), tuft_rough=1.0,
        # [v7 판정 §4 잔여3] 볼라드 = 도장 강재(백색 스테인리스 폐기)
        bollard_color=(0.33, 0.33, 0.36), bollard_metallic=0.4,
        bollard_rough=0.5,
        seat_wood=(0.055, 0.036, 0.022), seat_wood_rough=0.8,  # v4-D4 좌면
        gear_color=(0.055, 0.055, 0.058), gear_rough=0.6,  # v4-D2/D3 조명·스피커
        # [v5.1 §4] 파라펫 0.90 → 0.72 (순백 대면적 금지)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        # [v7 §4] 0.88 → 0.78: 등기구 판면이 알베도 상한(0.80)을 넘었다(소면적
        #   WARN 이었으나 자가검사가 잡은 항목은 남기지 않는다).
        lamp_color=(0.78, 0.78, 0.75), lamp_rough=0.4,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        nosing_color=(0.85, 0.72, 0.10), nosing_rough=0.7,
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


# ===========================================================================
# [C2] [v7 판정 §4 잔여1] 배후 관목 로브 생성기 — **조립기와 검산기가 같은
#   좌표를 쓴다**(scene04 `verge_instances` 규약). 시드 결정적이므로 Isaac
#   없이도 침범·부유·실루엣 높이를 실측할 수 있다.
#   yield: (px, py, pz, ax, ay, az, row, k, lobe)
# ===========================================================================
def backdrop_instances():
    sh = PARAMS["backdrop_shrub"]
    b = PARAMS["bowl"]
    emb = sh["embed"]
    for r_i, (rr0, step, rx0, rz0, h_top, nlobe) in enumerate(sh["rows"]):
        for a_i, (a0, a1) in enumerate(sh["arcs"]):
            k, s = 0, 0.0
            span = math.radians(a1 - a0) * rr0            # 호 길이[m]
            while s <= span + 1e-6:
                rnd = random.Random(int(r_i * 9176 + a_i * 3571 + k * 7919))
                s_next = s + step * (1.0 + rnd.uniform(-sh["jit_step"],
                                                       sh["jit_step"]))
                k += 1
                if rnd.random() < sh["skip"]:             # 결측 → 군락/빈틈
                    s = s_next
                    continue
                a = math.radians(a0) + s / rr0
                sc_ = 1.0 + rnd.uniform(-sh["jit_scale"], sh["jit_scale"])
                hh = h_top * (1.0 + rnd.uniform(-sh["jit_h"], sh["jit_h"]))
                rx, rz = rx0 * sc_, rz0 * sc_
                z_lo = sh["base_z"] + rz * (1.0 - emb)     # 최하 로브 중심
                z_hi = sh["base_z"] + hh - rz              # 최상 로브 중심
                for j in range(nlobe):
                    t = j / float(nlobe - 1) if nlobe > 1 else 0.0
                    rr = rr0 + rnd.uniform(-sh["jit_pos"], sh["jit_pos"])
                    da = rnd.uniform(-sh["jit_pos"], sh["jit_pos"]) / rr0
                    # 위로 갈수록 로브가 작아진다(수관 테이퍼)
                    f = 1.0 - sh["taper"] * t
                    yield (b["cx"] + rr * math.cos(a + da),
                           b["cy"] + rr * math.sin(a + da),
                           z_lo + (z_hi - z_lo) * t,
                           rx * f, rx * f * rnd.uniform(0.85, 1.15), rz * f,
                           r_i, k, j)
                s = s_next


def backdrop_selfcheck(verbose=True):
    """[v7] 배후 관목 재작업 검산 — 아크벽 침범 0 · 부유 0 · 실루엣 높이 유지.

    ① 반경 침범 : 최내측 로브가 아크벽 외경(shell.r_out 5.25) 안으로 들어가는가.
    ② 마당 이탈 : 최외측 로브가 마당 외경(backyard.r_out 7.5)을 넘는가.
    ③ 부유     : 최하 로브 하단(z − az)이 마당 상면(base_z) 아래로 물리는가.
    ④ 실루엣   : 군락 최상단이 아크벽 상면(shell.top_z 0.70)보다 위인가
                 (= v6 달성분 "벽 위로 녹지·하늘" 유지 조건).
    ⑤ 개체 크기: 최대 로브 높이(2·az)가 판정 권고 0.5 m 이하인가.
    ⑥ 카메라   : 전 프리셋 eye 가 로브 타원체 안에 들어가지 않는가.
    ⑦ 로브 연속: 같은 군락의 인접 로브 z 간격 ≤ 1.35·min(az) 인가
                 (넘으면 스택이 끊겨 '공중에 뜬 구슬'이 된다).
    """
    b = PARAMS["bowl"]
    sh = PARAMS["backdrop_shrub"]
    inst = list(backdrop_instances())
    # ⑦ 군락별 로브 스택 연속성
    stacks = {}
    for p in inst:
        stacks.setdefault((p[6], p[7]), []).append(p)
    gap_ratio = 0.0
    for key, lb in stacks.items():
        lb = sorted(lb, key=lambda q: q[2])
        for q0, q1 in zip(lb, lb[1:]):
            gap_ratio = max(gap_ratio,
                            (q1[2] - q0[2]) / min(q0[5], q1[5]))
    r_of = [math.hypot(p[0] - b["cx"], p[1] - b["cy"]) for p in inst]
    r_min = min(r - p[3] for r, p in zip(r_of, inst))
    r_max = max(r + p[3] for r, p in zip(r_of, inst))
    z_bot = min(p[2] - p[5] for p in inst)
    z_top = max(p[2] + p[5] for p in inst)
    lobe_h = max(2.0 * p[5] for p in inst)
    wall_out = PARAMS["shell"]["r_out"]
    wall_top = PARAMS["shell"]["top_z"]
    yard_out = PARAMS["backyard"]["r_out"]
    hits = []
    for name, v in build_views().items():
        ex, ey, ez = v["eye"]
        for px, py, pz, ax, ay, az, *_ in inst:
            if (((ex - px) / ax) ** 2 + ((ey - py) / ay) ** 2
                    + ((ez - pz) / az) ** 2) <= 1.0:
                hits.append(name)
                break
    ok = (r_min >= wall_out - 1e-6 and r_max <= yard_out
          and z_bot <= sh["base_z"] and z_top > wall_top
          and lobe_h <= 0.50 and not hits and gap_ratio <= 1.35)
    if verbose:
        n_pos = len(stacks)
        print("=" * 68)
        print("scene05 [v7] 배후 관목(tuft 로브 군락) 재작업 검산")
        print("=" * 68)
        print(f"  로브 수            {len(inst)} (군락 {n_pos}, "
              f"{len(sh['rows'])}열) — 구 편평 타원체 1열 {'':s}")
        print(f"  ① 최내측 반경      {r_min:.3f} ≥ 아크벽 외경 {wall_out:.2f} → "
              f"{'OK' if r_min >= wall_out - 1e-6 else 'FAIL'}")
        print(f"  ② 최외측 반경      {r_max:.3f} ≤ 마당 외경 {yard_out:.2f} → "
              f"{'OK' if r_max <= yard_out else 'FAIL'}")
        print(f"  ③ 접지            최하단 z {z_bot:+.3f} ≤ 마당 상면 "
              f"{sh['base_z']:+.2f} → {'OK(부유 0)' if z_bot <= sh['base_z'] else 'FAIL'}")
        print(f"  ④ 실루엣 상단      {z_top:+.3f} > 아크벽 상면 {wall_top:+.2f} → "
              f"{'OK(벽 위 녹지 유지)' if z_top > wall_top else 'FAIL'}")
        print(f"  ⑤ 최대 로브 높이   {lobe_h:.3f} m ≤ 0.50 (판정 권고 ①) → "
              f"{'OK' if lobe_h <= 0.50 else 'FAIL'}")
        print(f"  ⑥ 카메라 매몰      {hits if hits else '없음 → OK'}")
        print(f"  ⑦ 로브 연속        최대 간격/rz = {gap_ratio:.3f} ≤ 1.35 → "
              f"{'OK(스택 끊김 0)' if gap_ratio <= 1.35 else 'FAIL'}")
        print("=" * 68)
    return ok, dict(n=len(inst), r_min=r_min, r_max=r_max, z_top=z_top,
                    lobe_h=lobe_h, hits=hits, gap=gap_ratio)


def podium_step_selfcheck(verbose=True):
    """[v7 판정 §4 잔여2] 승강 계단 예각 쐐기 검산 — build_arc_steps 의
    현길이 규약(2·r_out·sin(dθ/2)·1.03)을 그대로 써서 **세그 박스 모서리가
    안쪽 원기둥 밖으로 얼마나 나가는지**(=초승달 틈)와 **호 끝 돌출**을 잰다."""
    po = PARAMS["podium"]
    ps = po["steps"]
    rows = []
    for i, _ztop in enumerate(ps["tops"]):
        r_in, r_out = ps["radii"][i + 1], ps["radii"][i]
        for a0, a1 in ps["arcs"]:
            dth = math.radians((a1 - a0) / float(ps["seg"]))
            half = r_out * math.sin(dth / 2.0) * 1.03
            gap = math.hypot(r_in, half) - r_in        # 안쪽 초승달 틈
            # 끝 세그 마구리면이 호 끝을 넘어가는 각(도) → r_in 에서의 호 길이
            over_a = math.degrees(math.atan2(half, r_in)) - (a1 - a0) / (
                2.0 * ps["seg"])
            over = max(0.0, math.radians(over_a) * r_in)
            rows.append((i, a0, a1, r_in, r_out, gap, over))
            break                                      # 두 호는 대칭 — 1회면 족함
    gap_max = max(r[5] for r in rows)
    over_max = max(r[6] for r in rows)
    ok = gap_max <= 0.002 and over_max <= 0.020
    if verbose:
        print("=" * 68)
        print("scene05 [v7] 승강 계단 아크 예각(쐐기) 검산")
        print("=" * 68)
        print(f"  seg {ps['seg']} (구 3) · 호 {ps['arcs']}")
        for i, a0, a1, r_in, r_out, gap, over in rows:
            print(f"  단{i}  r {r_in:.3f}..{r_out:.3f}  안쪽 초승달 틈 "
                  f"{gap*1000:6.2f} mm · 호끝 돌출 {over*1000:6.2f} mm")
        print(f"  ⇒ 최대 틈 {gap_max*1000:.2f} mm (구 seg3 = 15.3 mm) · "
              f"최대 돌출 {over_max*1000:.2f} mm (구 42 mm) → "
              f"{'OK' if ok else 'FAIL'}")
        print(f"  마구리(치크) {ps['cheek_deg']:.1f}° × 2/조 · 반경 "
              f"{ps['radii'][-1]:.2f}..{ps['radii'][0]:.2f} · 상면 "
              f"{po['top_z']:+.3f}(무대 단과 동일) → 끝단 슬리버 은폐")
        print("=" * 68)
    return ok, dict(gap=gap_max, over=over_max)


# ===========================================================================
# [C3] [v7 판정 §11-6] §4 "순백(>0.8) 대면적 금지" 알베도 상한 자가검사
#   (scene05/09/12 공통 규약 — 이번 라운드 도입분)
#
#   판정 §11-6: "순백 대면적이 3씬(09 포장·18 광장·19 지붕/옥상)에서 동시
#   발생. 개별 지적 대신 **알베도 상한 전역 검사 스크립트**를 스모크에 추가할 것."
#
#   두 기준을 함께 본다 — 하나만으로는 실제 실패를 못 잡는다.
#     (A) 알베도 상한  : 유효 알베도 max 채널 > CAP(0.80) → v5.1 §4 문자 위반.
#     (B) 렌더 예측    : **수평 대면적**(포장·데크·지붕 상면·잔디)에 한해
#         예상 렌더 sRGB = sRGB(알베도 × GAIN) > PRED_CAP(0.87 ≒ 222) → 위반.
#         GAIN 1.77 은 v7_rt 실측 역산 — scene09 `ghat_walk` 포장 알베도
#         0.469×0.90 = 0.422 → 렌더 (223,222,221) = 선형 0.738.
#         05/09/12 는 돔 1000 + 태양 2450 · elev 49.79 의 **동일 조명 리그**라
#         한 값을 공유할 수 있다. 수직면은 일사·천공 가시율이 달라 (B) 미적용.
#     PRED_CAP 0.87 은 판정관이 "순백 대면적"으로 지적한 실측(09 223 · 18 220)
#     바로 아래로 잡았다 — 같은 렌더가 다시 나오면 스모크에서 걸린다.
#   유효 알베도 = 상수색 그대로 | diff 텍스처 선형평균 × 틴트.
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
        import numpy as _np
        from PIL import Image
        im = Image.open(sc.tex_path(role, "diff")).convert("RGB")
        im.thumbnail((192, 192))
        a = _np.asarray(im, dtype=float) / 255.0
        lin = _np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        val = tuple(float(v) for v in lin.mean(axis=(0, 1)))
    except Exception:
        val = None
    _TEXMEAN_CACHE[role] = val
    return val


def _srgb(u):
    u = max(0.0, min(1.0, u))
    return 12.92 * u if u <= 0.0031308 else 1.055 * u ** (1 / 2.4) - 0.055


# (라벨, 텍스처 role|None, material 키|None, 대면적, 수평면, 유예 사유|None)
_ALBEDO_TABLE = [
    ("광장·티어 포장",   "plaza_light", None,               True,  True,
     "v7 판정 [경] '§4 경계선' — 01/05/14/18/19 가 무틴트 plaza_light 를 "
     "공유하는 전 씬 공통 항목이라 씬 단독 하향 시 21씬 톤 정합이 깨진다. "
     "판정 §11-6 이 요구한 것도 '전역' 규약이므로 감독 결정 대기."),
    ("진입 계단 판석",   "plaza_lower", "lower_warm_tint",  True,  True,  None),
    ("잔디",             "grass",       "grass_tint",       True,  True,  None),
    ("둘레 생울타리",    "grass",       "hedge_tint",       False, False, None),
    ("파라펫(측벽 상단)", None,         "parapet_color",    True,  False, None),
    ("가로등 등기구",    None,          "lamp_color",       False, False, None),
    ("볼라드",           None,          "bollard_color",    False, False, None),
    ("배후 관목 tuft",   None,          "tuft",             True,  False, None),
]


def albedo_selfcheck(verbose=True):
    """[v7 §4/§11-6] 순백 대면적 자가검사. (A) 알베도 > 0.80 또는
    (B) 수평 대면적의 예상 렌더 sRGB > 0.87 이면 위반. 대면적은 FAIL,
    소면적은 WARN, 유예 사유가 있으면 WAIVED. 반환 (ok, rows)."""
    mp = PARAMS["material"]
    rows, fails, warns, waived = [], [], [], []
    for label, role, key, wide, horiz, waiver in _ALBEDO_TABLE:
        if key == "tuft":                      # 상수색 리스트
            v = max(max(c) for c in mp["tuft"])
            base, tint = (1.0, 1.0, 1.0), (v, v, v)
        else:
            tint = mp.get(key) if key else (1.0, 1.0, 1.0)
            if tint is None:
                continue
            base = (1.0, 1.0, 1.0) if role is None else _tex_lin_mean(role)
            if base is None:
                rows.append((label, key or role, None, None,
                             "SKIP(텍스처 없음)"))
                continue
        alb = max(b * t for b, t in zip(base, tint))
        pred = _srgb(alb * _ALBEDO_GAIN) if horiz else None
        why = []
        if alb > _ALBEDO_CAP:
            why.append("A:알베도")
        if horiz and pred is not None and pred > _ALBEDO_PRED_CAP:
            why.append("B:렌더예측")
        if why:
            mark = "/".join(why)
            if waiver:
                waived.append(label)
                tag = f"WAIVED({mark})"
            elif wide:
                fails.append(label)
                tag = f"FAIL 대면적({mark})"
            else:
                warns.append(label)
                tag = f"WARN 소면적({mark})"
        else:
            tag = "OK"
        rows.append((label, key or role, alb, pred, tag))
    ok = not fails
    if verbose:
        print("=" * 68)
        print("scene05 [v7 §4] 순백 대면적 알베도 상한 자가검사 "
              f"(CAP {_ALBEDO_CAP} · 수평 렌더예측 CAP {_ALBEDO_PRED_CAP} "
              f"· GAIN {_ALBEDO_GAIN})")
        print("=" * 68)
        for label, key, alb, pred, tag in rows:
            if alb is None:
                print(f"  {label:16s} {str(key):18s} {tag}")
                continue
            pr = f"{pred*255:5.1f}" if pred is not None else "  수직"
            print(f"  {label:16s} {str(key):18s} 알베도 {alb:.3f} · "
                  f"수평 예상 렌더 {pr}  {tag}")
        for label, role, key, wide, horiz, waiver in _ALBEDO_TABLE:
            if waiver and label in waived:
                print(f"  · WAIVED [{label}] {waiver}")
        print(f"  ⇒ {'OK — 미유예 대면적 위반 0건' if ok else 'FAIL: ' + str(fails)}"
              f"{'  (WARN: ' + str(warns) + ')' if warns else ''}")
        print("=" * 68)
    return ok, rows


# 파라미터 / 토글 환경변수 오버라이드 (scene01 패턴 — 기본 실행엔 영향 없음)
_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")
_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [C] 경로
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene05")


# ===========================================================================
# [D] 카메라 프리셋 — grid_views(gy=0) + 미장센 4컷
# ===========================================================================
def build_views():
    """h·d 그리드 9장 + 미장센 4컷.
    그리드 d 프리셋 기준점 시프트: 보울 립이 x=−1.5(중심6−개구7.5)이므로
    eye x = −1.5 − d 로 옮겨 "립까지 거리 d" 의미가 되게 한다."""
    v = sc.grid_views(0.0)
    out = {}
    for k, val in v.items():
        e = list(val["eye"])
        t = list(val["tgt"])
        e[0] -= 1.5            # 립(x=−1.5)까지의 거리로 재기준
        t[0] -= 1.5
        out[k] = dict(eye=e, tgt=t)
    # 미장센
    out["plaza_approach"] = dict(eye=[-6.0, 0.0, 0.9],  tgt=[2.0, 0.0, 0.6])
    out["rim_view"]       = dict(eye=[-0.5, 0.0, 1.6],  tgt=[6.0, 0.0, -1.0])
    # [v5.1] 무대 단(상면 −0.507)이 생기면서 eye z −0.3 은 단 위 0.207 m 가 돼
    #   시점이 무대 바닥에 파묻힌다 → 무대 상면 기준 눈높이 0.9 m 로 재설정.
    #   (미장센 컷 — 위험 기하·그리드 프리셋과 무관)
    out["stage_lookup"]   = dict(eye=[6.0, 0.0, 0.40], tgt=[-1.0, 0.0, -0.3])
    out["side_arc"]       = dict(eye=[6.0, -10.0, 1.2], tgt=[6.0, -2.0, 0.5])
    return out


# ===========================================================================
# [E] 씬 조립 + 메인 (__main__ 전용)
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. plaza_approach   — h0.9 광장 시점에서 반원 보울이 grazing 소실되는가
 2. h0.3·d5~10       — 1.2m 보울이 통째로 사라지는 평지 그림
 3. rim_view         — 림에서 스테이지 부감(−15°), 3티어 좌석 형태
 4. side_arc         — 곡선 단코가 세그(18) 각짐 없이 읽히는가
 5. [v5] 반원 절단   — 측벽(θ80/280)·배후 잔디 마당·진입 치크월 마감 확인
 6. [v5] 공통 레이어 — 점자띠(−X 접근) + sign_info(게이트 옆) 판독
 7. [v6] 개방감      — 배후 아크벽(0.70) 위로 관목 띠·하늘이 보이는가,
                       무대 위 회색 모놀리스(스피커)가 사라졌는가
 8. [v7] 배후 관목   — plaza_approach 400 % 에서 '이끼 낀 바위'가 아니라
                       **여러 덩이로 갈라진 관목 군락**으로 읽히는가.
                       등간격 도열이 사라지고 빈틈/군락이 생겼는가
 9. [v7] 승강 계단   — rim_view·side_arc 400 % 에서 호 끝의 나이프 에지가
                       **각진 마구리**로 바뀌었는가, 무대 단과의 초승달 틈 0
10. [v7] 서측 볼라드 — stage_lookup 지평선의 백색 포스트 열이 사라지고
                       진입축 4본(도장 강재)만 남았는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # [v7] 부팅 없이 도는 순수 파이썬 자가검사 — 배후 관목 · 승강 아크 예각 ·
    #   §4 알베도 상한.  NEGOBS_SMOKE=1 (또는 NEGOBS_SELFCHECK=1) python scene05_...
    if (os.environ.get("NEGOBS_SMOKE", "0") == "1"
            or os.environ.get("NEGOBS_SELFCHECK", "0") == "1"):
        ok = all([backdrop_selfcheck()[0], podium_step_selfcheck()[0],
                  albedo_selfcheck()[0]])
        print(f"[SMOKE] scene05 자가검사 {'전항 OK' if ok else 'FAIL 있음'} "
              f"— 부팅 없이 조기 종료")
        sys.exit(0 if ok else 1)

    # 에셋 검사 (누락 시 목록 출력 후 종료)
    sc.check_assets(
        ["plaza_light", "plaza_lower", "granite_dark", "grass", "brick_red",
         "tactile", "sign_info", "hdri", "mdl"],   # [v5] sign_info 추가
        hdri=PARAMS["light"]["hdri"])

    # ── 부팅 (SimulationApp 먼저, 그 뒤 pxr/omni) ──
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene05")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        scl = mp["scale"]
        M = {}
        M["plaza_light"] = sc.make_pbr(
            stage, "/World/Looks/PlazaLight", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        # 차콜 밴드 = 짙은 화강암 (scene01 모티프)
        M["band"] = sc.make_pbr(
            stage, "/World/Looks/Band", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"), sc.tex_path("granite_dark", "rough"),
            scl["band_dark"])
        M["granite_dark"] = sc.make_pbr(
            stage, "/World/Looks/GraniteDark", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"), sc.tex_path("granite_dark", "rough"),
            scl["granite_dark"])
        # 스테이지: cue_material_break 에 따라 회청 판석(웜) vs 밝은 화강암 (기하 불변)
        if cfg["cue_material_break"]:
            M["stage"] = sc.make_pbr(
                stage, "/World/Looks/Stage", sc.tex_path("plaza_lower", "diff"),
                sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
                scl["plaza_lower"], tint=mp["lower_warm_tint"])
        else:
            M["stage"] = sc.make_pbr(
                stage, "/World/Looks/Stage", sc.tex_path("plaza_light", "diff"),
                sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
                scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        # 진입 계단(통행용) — 좌석 티어와 대비되게 회청 판석
        M["plaza_lower"] = sc.make_pbr(
            stage, "/World/Looks/PlazaLower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            scl["plaza_lower"], tint=mp["lower_warm_tint"])
        M["brick"] = sc.make_pbr(
            stage, "/World/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            scl["brick_red"])
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            scl["grass"], tint=mp["grass_tint"])
        M["tactile"] = sc.make_pbr(
            stage, "/World/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, scl["tactile"])
        # 상수 컬러 재질
        M["glass"] = sc.make_pbr(stage, "/World/Looks/Glass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
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
        # v4 드레싱 전용 재질
        M["hedge"] = sc.make_pbr(
            stage, "/World/Looks/Hedge", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            1.2, tint=mp["hedge_tint"])
        M["seat_wood"] = sc.make_pbr(stage, "/World/Looks/SeatWood",
                                     diffuse_color=mp["seat_wood"],
                                     roughness_const=mp["seat_wood_rough"])
        M["gear"] = sc.make_pbr(stage, "/World/Looks/Gear",
                                diffuse_color=mp["gear_color"],
                                roughness_const=mp["gear_rough"])
        # [v7 판정 §4 잔여1] 배후 관목 = **상수색 tuft 3종**(텍스처 없음).
        #   확대 텍스처가 곧 '이끼 낀 바위'의 절반이므로 아예 물리지 않는다.
        M["tuft"] = [sc.make_pbr(
            stage, f"/World/Looks/Tuft{i}",
            diffuse_color=tuple(c * (1.0 + 0.05 * (i - 1)) for c in col),
            roughness_const=mp["tuft_rough"], specular_level=0.0)
            for i, col in enumerate(mp["tuft"])]
        # [v7 판정 §4 잔여3] 볼라드 = 도장 강재(구: 백색 스테인리스 M["rail"])
        M["bollard"] = sc.make_pbr(stage, "/World/Looks/Bollard",
                                   diffuse_color=mp["bollard_color"],
                                   metallic=mp["bollard_metallic"],
                                   roughness_const=mp["bollard_rough"])
        return M

    # -------------------------------------------------------------------
    # 상부 광장 — 보울 개구(원형) 정합. 링 슬래브 + 링 내접사각 밖 4박스.
    # -------------------------------------------------------------------
    def build_plaza(M, hazard):
        p = PARAMS["plaza"]
        top, th = p["z_top"], p["thick"]
        if not hazard:
            # 평지 대조군: 전체 단일 슬래브(보울 구멍 없음)
            cx = (p["x0"] + p["x1"]) / 2.0
            cy = (p["y0"] + p["y1"]) / 2.0
            sc.add_box(stage, "/World/Scene05/PlazaFlat",
                       (cx, cy, top - th / 2.0),
                       (p["x1"] - p["x0"], p["y1"] - p["y0"], th),
                       M["plaza_light"], collider=True)
            return
        b = PARAMS["bowl"]
        rg = PARAMS["ring"]
        # 링 슬래브(아크): 보울 개구 원(r=7.5)의 매끈한 원형 가장자리 담당
        sc.build_arc_steps(stage, "/World/Scene05/PlazaRing", b["cx"], b["cy"],
                           rg["r_in"], rg["r_out"], 0.0, 360.0, rg["seg"],
                           rg["top_z"], rg["base_z"], M["plaza_light"])
        # 링 외곽 사각 밖을 4박스로. 링 outer 원에 **내접**하는 사각(반변=r_out/√2)
        # 을 비워 두면 사각 전 영역이 r≤r_out → 링이 코너까지 덮어 코너 공극 0.
        # (문언의 '외접 사각'은 코너 4곳에 원-밖 공극을 남겨 링-사각 이음이 뚫림.)
        half = rg["r_out"] / math.sqrt(2.0)     # ≈ 8.485
        sx0, sx1 = b["cx"] - half, b["cx"] + half
        sy0, sy1 = b["cy"] - half, b["cy"] + half
        ov = 0.05                               # 1mm↑ 겹침(동일 재질 → 티 안 남)

        def slab(tag, x0, x1, y0, y1):
            sc.add_box(stage, f"/World/Scene05/Plaza_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, top - th / 2.0),
                       (x1 - x0, y1 - y0, th), M["plaza_light"], collider=True)
        slab("W", p["x0"], sx0, p["y0"], p["y1"])
        slab("E", sx1, p["x1"], p["y0"], p["y1"])
        slab("N", sx0 - ov, sx1 + ov, sy1, p["y1"])
        slab("S", sx0 - ov, sx1 + ov, p["y0"], sy0)

    # -------------------------------------------------------------------
    # 차콜 밴드 — Y 방향, 간격 3.2. 보울 개구에 걸리는 밴드는 y를 두 조각으로 분할.
    # -------------------------------------------------------------------
    def build_bands(M, hazard):
        p = PARAMS["plaza"]
        bd = PARAMS["band"]
        b = PARAMS["bowl"]
        top = p["z_top"]
        z_bot = top - bd["embed"]
        z_top = top + bd["proud"]
        cz = (z_top + z_bot) / 2.0
        hz = z_top - z_bot
        r = b["open_r"]
        n = 0
        x = p["x0"] + bd["spacing"]
        while x < p["x1"] - 1e-6:
            dx = x - b["cx"]
            if hazard and abs(dx) < r:
                # 보울 개구 X구간 → 북/남 두 조각으로 클립 (개구 밖 +0.2 여유)
                halfc = math.sqrt(r * r - dx * dx) + 0.2
                sc.add_box(stage, f"/World/Scene05/Band_{n}_N",
                           (x, (halfc + p["y1"]) / 2.0, cz),
                           (bd["width"], p["y1"] - halfc, hz), M["band"])
                sc.add_box(stage, f"/World/Scene05/Band_{n}_S",
                           (x, (p["y0"] - halfc) / 2.0, cz),
                           (bd["width"], (-halfc) - p["y0"], hz), M["band"])
            else:
                cy = (p["y0"] + p["y1"]) / 2.0
                sc.add_box(stage, f"/World/Scene05/Band_{n}", (x, cy, cz),
                           (bd["width"], p["y1"] - p["y0"], hz), M["band"])
            x += bd["spacing"]
            n += 1

    # -------------------------------------------------------------------
    # 선큰 보울 — 3티어(아크 × 3회) + 스테이지 원반 + 진입 계단
    # -------------------------------------------------------------------
    def build_bowl(M):
        b = PARAMS["bowl"]
        stg = PARAMS["stage"]
        # [v5 채택] 티어 호 = b["a0"]..b["a1"] (200°). 반경·z 는 불변.
        for i, t in enumerate(b["tiers"], 1):
            sc.build_arc_steps(stage, f"/World/Scene05/Tier_{i}", b["cx"], b["cy"],
                               t["r_in"], t["r_out"], b["a0"], b["a1"],
                               b["seg"], t["top_z"], b["base_z"],
                               M["plaza_light"])
        # v4-A1: 스테이지 = 내부 원반(r 4.9) + 32세그 아크 림(4.2..5.22).
        #   림 외경 최소 반경 5.22 > 티어3 내면 최대 5.0242 → 관통 공극 0.
        rim = stg["rim"]
        sc.add_cylinder(stage, "/World/Scene05/Stage/Disc",
                        (b["cx"], b["cy"], stg["top_z"] - stg["height"] / 2.0),
                        stg["radius"], stg["height"], M["stage"], collider=True)
        sc.build_arc_steps(stage, "/World/Scene05/Stage/Rim", b["cx"], b["cy"],
                           rim["r_in"], rim["r_out"], 0.0, 360.0, rim["seg"],
                           rim["top_z"], rim["base_z"], M["stage"])
        # [v5.1] 원형 무대 단 + 승강 계단 2조 — 좌표 근거는 PARAMS["podium"] 주석
        po = PARAMS["podium"]
        sc.add_cylinder(stage, "/World/Scene05/Stage/Podium",
                        (b["cx"], b["cy"],
                         (po["top_z"] + po["base_z"]) / 2.0),
                        po["r"], po["top_z"] - po["base_z"], M["stage"],
                        collider=True)
        ps = po["steps"]
        for j, (a0, a1) in enumerate(ps["arcs"]):
            for i, ztop in enumerate(ps["tops"]):
                sc.build_arc_steps(
                    stage, f"/World/Scene05/Stage/PodiumStep_{j}_{i}",
                    b["cx"], b["cy"], ps["radii"][i + 1], ps["radii"][i],
                    a0, a1, ps["seg"], ztop, ps["base_z"], M["stage"])
            # [v7 판정 §4 잔여2] 마구리(치크) — 호 양단의 나이프 에지 은폐.
            #   반경 전폭(3.0..3.75)을 덮는 두께 cheek_deg 의 짧은 아크 1장씩.
            #   상면 = 무대 단 상면(−0.853) → 에이프런 대비 0.35 m(단과 동일
            #   낙차, 신규 위험 0). overlap 만큼 계단 쪽으로 물려 틈을 없앤다.
            cd, ov = ps["cheek_deg"], ps["cheek_overlap"]
            for tag, ca0, ca1 in (("A", a0 - cd + ov, a0 + ov),
                                  ("B", a1 - ov, a1 + cd - ov)):
                sc.build_arc_steps(
                    stage, f"/World/Scene05/Stage/PodiumCheek_{j}{tag}",
                    b["cx"], b["cy"], ps["radii"][-1], ps["radii"][0],
                    ca0, ca1, 1, po["top_z"], ps["base_z"], M["stage"])

    def build_flight(M, prefix, a0, a1, seg):
        """v4-A2/A3: 티어와 동심인 아크 계단 1조. 반경 사다리가 티어 경계를
        정확히 포함하므로 디딤폭 붕괴·쐐기 단차가 원리적으로 발생하지 않는다."""
        e = PARAMS["entry"]
        b = PARAMS["bowl"]
        for i, ztop in enumerate(e["tops"]):
            sc.build_arc_steps(stage, f"{prefix}/Step_{i}", b["cx"], b["cy"],
                               e["radii"][i + 1], e["radii"][i], a0, a1, seg,
                               ztop, e["base_z"], M["plaza_lower"])

    def build_entry(M):
        """진입 계단(+X 방사, a −9..+9°) + v4-D5 관람석 통로 계단 2조."""
        e = PARAMS["entry"]
        build_flight(M, "/World/Scene05/Entry", e["a0"], e["a1"], e["seg"])
        for k, a in enumerate(PARAMS["aisles"]):
            build_flight(M, f"/World/Scene05/Aisle_{k}", a["a0"], a["a1"],
                         a["seg"])

    def build_seat_strips(M):
        """v4-D4: 각 티어 상연에 목재 좌면 밴드 — 티어가 '좌석'으로 읽히고
        단 대비(riser 0.40 · tread 0.85 의 밋밋한 흰 곡면 벽)가 확보된다.
        진입(±9°)·통로(100~112 / 248~260) 구간은 아크를 끊어 비운다."""
        b = PARAMS["bowl"]
        se = PARAMS["seat"]
        for i, t in enumerate(b["tiers"], 1):
            r1 = t["r_out"] - se["inset"]
            r0 = r1 - se["width"]
            z_hi = t["top_z"] + se["proud"]
            for j, (a0, a1, seg) in enumerate(se["arcs"]):
                sc.build_arc_steps(stage, f"/World/Scene05/Seat_{i}_{j}",
                                   b["cx"], b["cy"], r0, r1, a0, a1, seg,
                                   z_hi, z_hi - se["drop"], M["seat_wood"],
                                   collider=False)

    def build_lip(M):
        """립 연석 링 (cue_material_break): 개구 밖 다크 화강암 재질 경계 단서."""
        l = PARAMS["lip"]
        b = PARAMS["bowl"]
        sc.build_arc_steps(stage, "/World/Scene05/LipCurb", b["cx"], b["cy"],
                           l["r_in"], l["r_out"], l["a0"], l["a1"], l["seg"],
                           l["top_z"], l["base_z"], M["granite_dark"])

    def build_halfbowl_finish(M):
        """[v5 채택] 반원화 마감 — 절단 측벽 + 배후 잔디 마당 + 진입 치크월.

        보행 연속성 자가 검증(광장 → 마당 → 무대):
          광장/링 z −0.002 (r>7.5)
            → 마당 z −0.06        단차 0.058  (평지 접속)
            → 진입 계단 1단 −0.197 단차 0.137  (치크월 상면과 플러시 시작)
            → −0.397 / −0.597 / −0.797 / −0.997 / −1.197  각 riser 0.200
            → 스테이지 −1.207      단차 0.010
          역방향(무대 → 마당)도 동일 프로파일. 0.2 m 초과 단차 없음.
        새 에지 낙차 방호:
          · 티어 절단면(θ 80/280) → cut_wall 상면 +1.00 (마당 대비 1.06 m)
          · 마당 내측(r 5.25) → shell(θ 9..80 / 280..351) 전 구간 차단
            [v6] 상면 +1.4 → +0.70 + 배후 관목 완충대(backdrop_shrub) 병용
          · 진입 계단 측면(θ ±9) → entry_cheek(θ 9..11 / 349..351) 상면 −0.06
        """
        b = PARAMS["bowl"]
        for key, mtl in (("backyard", M["grass"]),
                         ("entry_cheek", M["plaza_light"]),
                         ("cut_wall", M["granite_dark"])):
            p = PARAMS[key]
            for j, (a0, a1) in enumerate(p["arcs"]):
                sc.build_arc_steps(stage, f"/World/Scene05/{key}_{j}",
                                   b["cx"], b["cy"], p["r_in"], p["r_out"],
                                   a0, a1, p["seg"], p["top_z"], p["base_z"],
                                   mtl)

    # -------------------------------------------------------------------
    # 부지 바깥 잔디 대지 — 보울 개구를 비우는 4박스 분할(r1 수정).
    #   단일 대지는 상면(-0.5)이 선큰 보울 내부를 관통해 티어2·3·스테이지를
    #   매장시킴 → 개구(중심(6,0) r7.5)의 외접 사각+0.2 여유를 홀로 비운다.
    #   홀 코너~원 사이는 광장 링(r7.5..12, base -0.5)이 위에서 덮어 무공극.
    #   잔디 상면 -0.51 : 링 base(-0.5)와의 동일평면 Z파이팅 1cm 하강 회피.
    # -------------------------------------------------------------------
    def build_ground(M):
        top = -0.51
        th = 1.0
        cz = top - th / 2.0
        # 홀 사각: 보울 r=7.5 원의 외접 사각 + 0.2 여유 (중심 (6,0))
        hx0, hx1 = -1.7, 13.7
        hy0, hy1 = -7.7, 7.7
        gx0, gx1 = -117.0, 123.0     # 대지 전역 (중심 x=3, 폭 240)
        gy0, gy1 = -120.0, 120.0
        ov = 0.05                    # 조각 이음 겹침(동일 재질 → 티 안 남)

        def slab(tag, x0, x1, y0, y1):
            sc.add_box(stage, f"/World/Scene05/Ground_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                       (x1 - x0, y1 - y0, th), M["grass"])
        slab("W", gx0, hx0, gy0, gy1)
        slab("E", hx1, gx1, gy0, gy1)
        slab("N", hx0 - ov, hx1 + ov, hy1, gy1)
        slab("S", hx0 - ov, hx1 + ov, gy0, hy0)

    # -------------------------------------------------------------------
    # 드레싱 — 화단·생울타리·벤치·가로등·건물
    # -------------------------------------------------------------------
    def build_streetlight(M):
        """v4-D10: PARAMS['streetlights'] 목록(x, y, base_z)으로 다본 배치."""
        sl = PARAMS["streetlight"]
        for k, (x, y, bz) in enumerate(PARAMS["streetlights"]):
            base = f"/World/Scene05/Streetlight_{k}"
            sc.add_cylinder(stage, f"{base}/Pole",
                            (x, y, bz + sl["pole_h"] / 2.0),
                            sl["pole_r"], sl["pole_h"], M["pole"],
                            collider=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                ax = x + sgn * sl["arm_len"] / 2.0
                sc.add_cylinder(stage, f"{base}/Arm_{tag}",
                                (ax, y, bz + sl["pole_h"] - 0.1),
                                sl["arm_r"], sl["arm_len"], M["pole"],
                                rotY=90.0)
                hx = x + sgn * sl["arm_len"]
                sc.add_box(stage, f"{base}/Head_{tag}",
                           (hx, y, bz + sl["pole_h"] - 0.15),
                           (sl["head"], sl["head"], 0.12), M["lamp"])

    def build_surround(M):
        """v4-A4: 광장 전 둘레 0.51 m 무방비 낙하 종결.
        잔디 뱅크(상면 −0.26)로 0.51 → 0.26 + 0.25 두 단으로 분할하고,
        북측은 건물 앞 포장 에이프런으로 대체해 건물 접지(B-6)도 개선한다."""
        bm = PARAMS["berm"]
        for tag, x0, x1, y0, y1 in PARAMS["berms"]:
            sc.add_box(stage, f"/World/Scene05/Berm_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                        (bm["top_z"] + bm["base_z"]) / 2.0),
                       (x1 - x0, y1 - y0, bm["top_z"] - bm["base_z"]),
                       M["grass"], collider=True)
        ap = PARAMS["apron"]
        sc.add_box(stage, "/World/Scene05/ApronN",
                   ((ap["x0"] + ap["x1"]) / 2.0, (ap["y0"] + ap["y1"]) / 2.0,
                    (ap["top_z"] + ap["base_z"]) / 2.0),
                   (ap["x1"] - ap["x0"], ap["y1"] - ap["y0"],
                    ap["top_z"] - ap["base_z"]),
                   M["plaza_light"], collider=True)

    def planter_no_stake(M, prefix, cx, cy, base_z, size=None):
        """[v5 판정 반영] 화단 + 지지대 없는 성목.

        v4-B3 '나무 삼각 지지대 제거' 공통 수정이 scene01/03/04 에만 반영되고
        scene05 만 누락돼(stage_lookup·side_arc·preset_h0.3_d10 에 지지대 노출)
        다른 4씬과 일관성이 깨졌다. scene05 는 나무를 sc.build_planter 가
        내부에서 심는데 이 함수는 stake 인자를 전달하지 않으므로,
        화단만 먼저 세우고(tree_mtls=None) 나무는 직접 sc.build_tree 로 심어
        지지대 치수를 0에 근접시켜 무력화한다(scene03/04 와 동일 규약).
        (제안: scene_common.build_tree/build_planter 에 stakes=False 인자 추가)
        """
        kw = {} if size is None else dict(size=size)
        sc.build_planter(stage, prefix, cx, cy, base_z,
                         M["granite_dark"], M["grass"], tree_mtls=None, **kw)
        # build_planter 기본 grass_h=0.40 상면에 식재 (내부 호출과 동일 높이)
        sc.build_tree(stage, prefix, cx, cy, base_z + 0.40,
                      M["wood"], M["canopy_a"], M["canopy_b"],
                      stake_r=0.004, stake_h=0.02, stake_off=0.2)

    def build_backdrop_shrubs(M):
        """[v6 판정 ㉠] 배후 관목 완충대 — 낮춘 아크벽(+0.70) 뒤 마당에 심는
        관목 밴드. 목적 ① 마당→무대 1.15 m 낙차 접근 억제(벽 인하분 대체),
        ② 무대 뒤가 '콘크리트 옹벽'이 아니라 **녹지**로 읽히게(개방감).

        [v7 판정 §4 잔여1] 구 구현(편평 타원체 rad 0.42·h 1.10 1열 + grass
        텍스처 uv 1.2 · spacing 0.62 등간격)이 **"이끼 낀 바위 등간격 열"** 로
        렌더됐다(scene04 v6 verge 와 동일 실패 모드). scene04 W-4 해법 이식:
          · 상수색 tuft 3종(텍스처 폐기) — '암괴 요철' 신호가 원천 제거된다.
          · 큰 타원체 1개 → **작은 로브 3~4개의 세로 스택**. 개체(로브) 높이는
            0.5 m 이하(판정 권고 ①)이면서 군락 상단은 1.22 m 를 유지해
            "아크벽(+0.70) 위로 녹지" 라는 v6 달성분이 그대로 남는다.
          · 3열 × 열별 step + 간격 지터 ±35 % + 결측 12 % + 로브별 위치/크기
            지터 → 등간격 도열 소멸(§3).
        좌표는 모듈 레벨 `backdrop_instances()` 단일 출처(검산기와 공유).
        """
        # [v8 핫픽스] (r,k,j) 3중 키가 130건 중복(지터·결측 후 k 재사용) →
        #   같은 프림 경로에 add_sphere 2회 = AddTranslateOp 충돌로 조립 크래시.
        #   전역 순번(idx) 명명으로 교체. v2 씬이라 SMOKE 부재 — RT에서 발견됨.
        n = 0
        for idx, (px, py, pz, ax, ay, az, r_i, k, j) in \
                enumerate(backdrop_instances()):
            sc.add_sphere(stage,
                          f"/World/Scene05/BackdropShrub_{idx}",
                          (px, py, pz), (ax, ay, az),
                          M["tuft"][(r_i + k + j) % len(M["tuft"])])
            n += 1
        return n

    def build_dressing(M):
        b = PARAMS["bowl"]
        # 화단 2 (림 주변)
        for name, cx, cy in PARAMS["planters"]:
            planter_no_stake(M, f"/World/Scene05/Planter_{name}", cx, cy, 0.0)
        # v4-D8 립 둘레 가로수 열 (r=9.6 원주, 45° 간격)
        rp = PARAMS["ring_planter"]
        for k, adeg in enumerate(PARAMS["ring_planters"]):
            a = math.radians(adeg)
            planter_no_stake(M, f"/World/Scene05/RingPlanter_{k}",
                             b["cx"] + rp["r"] * math.cos(a),
                             b["cy"] + rp["r"] * math.sin(a), rp["base_z"],
                             size=rp["size"])
        # v4-B4/A4 광장 둘레 생울타리 (어긋난 3장 → 둘레 5조각, 개구 3곳)
        for j, (x0, y0, x1, y1) in enumerate(PARAMS["hedges"]):
            sc.build_hedge(stage, f"/World/Scene05/Hedge_{j}", x0, y0, x1, y1,
                           PARAMS["hedge_h"], mtl=M["hedge"])
        # [v7 판정 §4 잔여3] 서측 볼라드 — 장식 열 10본(간격 2.67 m, 폭 24 m)
        #   → **진입축 게이트 4본**(규정 간격 1.5 m, 폭 4.5 m) · 도장 강재.
        #   v5.1 §2 "차량 진입 우려 지점만 · 간격 1.5 m 내외 · 장식 열 제거".
        bl = PARAMS["bollards"]
        y0 = -bl["spacing"] * (bl["n"] - 1) / 2.0
        for k in range(bl["n"]):
            sc.build_bollard(stage, f"/World/Scene05/Bollard_{k}", bl["x"],
                             y0 + bl["spacing"] * k, bl["base_z"],
                             mtl=M["bollard"])
        # [v5.2 사용자] 벤치 링 제거 — "개방감 악화, 깔끔하게 제거"
        #   (bench_ring PARAMS 는 이력 보존용으로 잔존, 빌드는 생략)
        # v4-D1 [최우선] 무대 배후벽(스테이지 셸) 2조각 — 보울이 있을 때만
        #   [v6 판정 ㉠] 상면 1.40 → 0.70 (PARAMS 주석). 낮춘 방호는 관목 완충대로.
        sh = PARAMS["shell"]
        if cfg["hazard_stairs"]:
            for j, (a0, a1) in enumerate(sh["arcs"]):
                sc.build_arc_steps(stage, f"/World/Scene05/StageShell_{j}",
                                   b["cx"], b["cy"], sh["r_in"], sh["r_out"],
                                   a0, a1, sh["seg"], sh["top_z"],
                                   sh["base_z"], M["granite_dark"])
            build_backdrop_shrubs(M)
        # v4-D2 조명 타워 2 (기둥 + 헤드 3)
        tw = PARAMS["tower"]
        for k, (tx, ty) in enumerate(PARAMS["towers"]):
            sc.add_cylinder(stage, f"/World/Scene05/Tower_{k}/Pole",
                            (tx, ty, tw["base_z"] + tw["pole_h"] / 2.0),
                            tw["pole_r"], tw["pole_h"], M["pole"],
                            collider=True)
            for hi, hz in enumerate(tw["head_z"]):
                sc.add_box(stage, f"/World/Scene05/Tower_{k}/Head_{hi}",
                           (tx, ty, tw["base_z"] + hz), tw["head"], M["gear"])
        # [v6 판정 ㉡] v4-D3 스피커 스택 2 제거 — "무대 위 정체불명 회색 모놀리스".
        #   그릴·거치대·기울기 없는 무텍스처 회색 판 2기가 무대 좌우에 서서
        #   v5.2 §6 "이게 없으면 장면 판독이 안 되는가" 를 통과하지 못한다.
        #   근린공원 야외무대에 상설 스피커는 관행도 아니다(행사 시 반입).
        #   → 빌드 생략. PARAMS["speakers"]/["speaker"] 는 이력 보존용으로 잔존
        #     (벤치 링 제거와 동일 규약).
        # v4-D7 입구 게이트 + 사인 (−X 접근축)
        gt = PARAMS["gate"]
        for tag, sgn in (("P", 1.0), ("N", -1.0)):
            sc.add_cylinder(stage, f"/World/Scene05/Gate/Post_{tag}",
                            (gt["x"], sgn * gt["y"],
                             gt["base_z"] + gt["post_h"] / 2.0),
                            gt["post_r"], gt["post_h"], M["granite_dark"],
                            collider=True)
        sc.add_box(stage, "/World/Scene05/Gate/Lintel",
                   (gt["x"], 0.0,
                    gt["base_z"] + (gt["lintel_z0"] + gt["lintel_z1"]) / 2.0),
                   (gt["lintel_t"], 2.0 * gt["lintel_y"],
                    gt["lintel_z1"] - gt["lintel_z0"]), M["granite_dark"])
        # v4-B6 건물 R 출입 캐노피 (에이프런 위)
        ec = PARAMS["entry_canopy"]
        sc.build_canopy(stage, "/World/Scene05/EntryCanopy", ec["x0"],
                        ec["x1"], ec["y0"], ec["y1"], ec["z_roof"],
                        ec["post_r"], M["parapet"], M["pole"],
                        roof_t=ec["roof_t"], base_z=ec["base_z"])
        # 가로등 5
        build_streetlight(M)
        # 원경 건물 2동 (R/C)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"/World/Scene05/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"])

    # -------------------------------------------------------------------
    # 단서 토글 (기본 전부 False — 설비 전무 정체성). 선택 구현.
    # -------------------------------------------------------------------
    def build_cues(M):
        b = PARAMS["bowl"]
        # cue_railing: 립 둘레 부분 호 난간 — 포스트 체인 + 얇은 아크 상단 레일.
        if cfg.get("cue_railing"):
            r_post = 7.9
            a0, a1 = 120.0, 240.0            # −X 관람측 부분 호
            nposts = 9
            rail_h = 0.9
            for k in range(nposts):
                a = math.radians(a0 + (a1 - a0) * k / (nposts - 1))
                px = b["cx"] + r_post * math.cos(a)
                py = b["cy"] + r_post * math.sin(a)
                sc.add_cylinder(stage, f"/World/Scene05/Rail/Post_{k}",
                                (px, py, rail_h / 2.0), 0.02, rail_h, M["rail"])
            # 상단 레일: 얇은 아크 박스 링(세그 원기둥 체인 대용 — rotZ 미노출 회피)
            sc.build_arc_steps(stage, "/World/Scene05/Rail/Top", b["cx"], b["cy"],
                               r_post - 0.03, r_post + 0.03, a0, a1, 12,
                               rail_h, rail_h - 0.04, M["rail"], collider=False)
        # cue_tactile: −X 접근 경고 점자띠 (립 밖)
        if cfg.get("cue_tactile"):
            sc.build_tactile(stage, "/World/Scene05/Tactile",
                             -2.3, -1.9, -2.0, 2.0, M["tactile"], z=0.0)
        # cue_nosing: 각 티어 상연에 곡선 단코 논슬립 아크 밴드
        if cfg.get("cue_nosing"):
            nos = sc.make_pbr(stage, "/World/Looks/Nosing",
                              diffuse_color=mp["nosing_color"],
                              roughness_const=mp["nosing_rough"])
            for i, t in enumerate(b["tiers"], 1):
                sc.build_arc_steps(stage, f"/World/Scene05/Nosing_{i}",
                                   b["cx"], b["cy"], t["r_out"] - 0.06, t["r_out"],
                                   b["a0"], b["a1"], b["seg"],  # [v5] 반원 추종
                                   t["top_z"] + 0.003,
                                   t["top_z"] - 0.02, nos, collider=False)

    # -------------------------------------------------------------------
    # [v5 공통 레이어] 한글 사인 (cue_sign)
    # -------------------------------------------------------------------
    def build_signs():
        """PARAMS['signs'] 목록을 sc.build_sign 으로 배치.
        경고/안내판은 낙차 인접 시설 단서(계열①) — 좌표 검산은 PARAMS 주석."""
        back = sc.make_pbr(stage, "/World/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"/World/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"/World/Scene05/Sign_{tag}", cx, cy, bz,
                          yaw, panel, w=w, h=h, back_mtl=back)

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hazard = cfg["hazard_stairs"]
    build_plaza(M, hazard)
    build_bands(M, hazard)
    if hazard:
        build_bowl(M)
        build_entry(M)
        build_halfbowl_finish(M)        # [v5 채택] 반원 절단 마감·배후 마당
        if cfg["cue_material_break"]:
            build_lip(M)
    build_ground(M)
    build_surround(M)               # v4-A4: 광장 둘레 종결 (상시 — 보행 안전)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
        if hazard:
            build_seat_strips(M)    # v4-D4: 티어가 있을 때만
    build_cues(M)
    if cfg.get("cue_sign"):
        build_signs()               # [v5 공통 레이어]
    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── 카메라 + 렌더 모드 ──
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
    _v0 = VIEWS["plaza_approach"]
    look_from(_v0["eye"], _v0["tgt"])              # 시작 카메라 = 미장센

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    # ── 자동 캡처 모드 (headless) ──
    if capture_mode:
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
                            set_render_mode, look_from)
        simulation_app.close()
        return

    # ── GUI 룩 체크 모드 (기본) ──
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene05_{ts}.png")
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
