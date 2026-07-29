# -*- coding: utf-8 -*-
"""
sceneD2_floor_opening.py — NegObs 인공씬 29호: 공사장 바닥 개구부 (Isaac Sim 4.5)

유형    : D2 비계단 낙차 — 골조 공사 층 슬래브의 무방호 개구 (낙차 3.0 m)
사양서  : Docs/nanobanana_batch1_geometry_map.md §C sceneD2_floor_opening
룩 근거 : look_refs/d2_floor_opening.jpg
공통    : scene_common.py (검증된 API 헬퍼) · scene16_canopy_shadow.py (표준 템플릿)

위험 본질: 골조 공사 층(콘크리트 슬래브, 거푸집 자국 벽)의 한복판에 1.5×2.0 m
           무방호 개구가 뚫려 있고 그 아래는 지하층(z −3.0)이다. 개구 내부는
           역광·자기폐색으로 "검은 사각형"으로만 읽히며 — 계단처럼 단코가
           연속하는 단서가 전무해, RGB 맥락(철근 스터브·부스러기 링·거푸집
           벽면 원근)만이 낙차의 존재를 알린다.
주의     : sceneN2(신설 아스팔트 패치, GT 음성)와 **"검은 사각형" 최강 혼동쌍**.
           개구 치수 1.5×2.0 [고정] — 혼동쌍 성립 조건.
목표     : 슬래브(4박스 분할) + 지하실(바닥·거푸집 벽) + 철근 스터브 + 파쇄
           부스러기 산포 + 거푸집 벽 2면 / 남측 기둥 개구부(채광원)를 조립,
           렌더로 판정 (렌더 전용).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneD2_floor_opening.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneD2_floor_opening.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneD2_floor_opening.py

좌표계: Z-up, m, 진행축 +X, 낙차 시작 모서리 = x=0 (개구 서쪽 립).
"""

import os
import math
import json
import random
import datetime

import scene_common as sc
import batch1_common as bc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키. hazard_opening 대신 hazard_stairs 키를 유지
#     (라이브러리 공통 규약: 기하 토글 유일 예외).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False → 개구를 슬래브로 메워 z=0 평지 (대조군)
    "cue_railing":        False,  # 임시 개구부 안전난간 — 기본 OFF(**무방호가 특색**)
    "cue_tactile":        False,  # 해당 없음(공사장) — 키만 예약
    "cue_material_break": True,   # False → 지하층도 슬래브와 동일 재질(대비 소거)
    "cue_nosing":         False,  # 개구 둘레 황색 경고 도색 — 기본 OFF(무방호)
    "cue_sign":           False,  # [선택] 미구현 — 키만 예약
    "cue_scene_dressing": True,   # 거푸집 패널·잔토 더미·외부 흙무지·원경 능선
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # 골조 층 슬래브(=지상 레벨). 남·서는 외부 흙과 거의 flush(보행 연속),
    # 동·북은 거푸집 벽으로 폐쇄 → 지평선 차단.
    deck=dict(x_w=-9.0, x_e=8.45, y_s=-6.5, y_n=6.5, z_top=0.0, thick=0.25),

    # ★ 무방호 개구: 진행축 2.0 m × 폭 1.5 m. 서쪽 립이 낙차 시작 모서리 x=0.
    #   [고정] sceneN2(4×5 m 아스팔트 패치)와의 혼동쌍 성립 조건.
    opening=dict(x0=0.0, x1=2.0, y0=-0.75, y1=0.75),

    # 개구 하단에 매달린 거푸집 다운스탠드(그을린 암색) — 립 바로 아래를
    # 확실히 어둡게. 내면을 개구보다 0.01 바깥으로 물려 동일평면 회피.
    #   z_top −0.24 = 슬래브 하면(−0.25)에 0.01 물림 → 수평 동일평면 회피.
    skirt=dict(inset=0.01, thick=0.35, z_top=-0.24, z_bot=-0.55),

    # 지하층(개구 아래). 개구보다 넉넉히 넓어 통과광이 바닥에 착지 → 반사광이
    # 동쪽 벽(카메라가 개구 너머로 보는 면)을 비춘다 = "어둡되 0 아님".
    lower=dict(x0=-5.0, x1=7.0, y0=-4.5, y1=4.5,
               z_floor=-3.0, floor_t=0.5, wall_t=0.35, z_ceil=-0.20),

    # 거푸집 벽(동·북) — 층고 3.2, 지평선 폐쇄용.
    #   벽 외곽면을 데크 가장자리보다 **엄격히 안쪽**에 두고(동 8.30<8.45,
    #   북 6.45<6.50), 동·북 벽의 z 범위를 서로 다르게 해 코너 동일평면 제거.
    walls=dict(t=0.30, n_t=0.28, h=3.2, x_face=8.0, y_face=6.15,
               e_y0=-6.05, e_y1=6.45, n_x0=-8.65, n_x1=8.15,
               n_h_delta=0.06, n_base=-0.12, base=-0.09),

    # 남측 기둥 개구부(콜로네이드) — 기둥 사이로 외부 흙·하늘이 보이는 채광원
    colonnade=dict(y_c=-6.2, size=0.45, h=3.2,
                   xs=[-6.5, -3.5, -0.5, 2.5, 5.5]),

    # 철근 스터브: 직선 6본(수직) + 굽은 것 2본(_oriented_box 근사) + 갈고리 1
    rebar=dict(r=0.006, h=0.36, z_c=0.13,
               straight=[(-0.20, -0.55), (-0.20, 0.60), (0.70, -0.95),
                         (1.55, 0.96), (2.20, -0.30), (2.22, 0.62)],
               bent=[(0.05, -0.98, 32.0, 18.0), (2.32, 0.05, 27.0, -64.0)],
               bent_len=0.42, bent_t=0.013,
               # 갈고리: (-0.20,-0.55) 직선 스터브 상단을 관통하도록 배치(부유 금지)
               hook=dict(cx=-0.20, cy=-0.42, z=0.293, lx=0.30, t=0.013,
                         yaw=90.0)),

    # ═══ [W2 ground_kit] P15 slab_construction — 사양 §5.8 D2 행 ═══════════
    #  처방: 개구 표시 도색의 **마모 잔흔**(황색 잔존 20~30 %) · 먹줄(부분
    #  구간) · 콜드 조인트 · 백화 얼룩 · 발자국 8~15.
    #  근거: 산안규칙 §43 은 "개구부임을 표시" 를 요구하는데, 실물은 팻말이
    #  아니라 **노면 도색**이고 타설 후 통행으로 절반 이상 지워져 있다.
    #  ★ GT-V(§6.3): 개구(x 0…2 · y ±0.75) 위에는 **어떤 요소도 걸치지
    #    않는다**. region 원단을 개구 서립(x=0)에서 끊고 `voids` 로 개구를
    #    넘겨 `plan_ground` 가 전 요소 AABB × 개구 교차를 어서션하게 한다.
    #  ★ 개구 표시 도색은 **종방향 2본(y=±1.05) + 횡방향 1본(x=−3.00)** 의
    #    ㄷ 자다. 종방향 2본은 GT-E1′ 때문에 서립에서 0.15 m 물린다
    #    (도색 proud 0.003 × EDGE_K 40 = 0.12 m 필요 `[계산]`).
    #  ★ [2026-07-30, 킷 결함 F1 수정 후] W2-D 라운드는 횡방향 띠를 **보류**
    #    했었다 — `ground_kit._ik_marking` 이 요소 AABB 를 yaw 를 무시하고
    #    +X 로 깔아서 횡단 띠가 "개구를 가로지르는 요소"로 오판정돼 B8/B6 에
    #    걸렸기 때문이다. F1 이 고쳐진 지금 **그 두 게이트는 깨끗하다**
    #    `[실측 — 서립 앞 x=−0.225 배치를 재현하면 B6·B8 은 통과하고 B7 만
    #     남는다]`. 남은 것은 오판정이 아니라 진짜 규칙이다:
    #      GT-E2 — 립 바로 앞의 전폭 횡단 단선은 GRAZE 에서 립과 융합한다.
    #      x=−0.225 에서 Δ = 19.7/3.1/0.8 행@1080 (요구 32/32/16) `[실측]`.
    #      d10 E 대역(7~22 m)을 통과하려면 근단이 **립에서 2.60 m** 물러나야
    #      한다 `[계산]`.
    #    → 띠를 종방향 2본의 서단(x=−3.00)에 놓아 도색 구역을 **개구 쪽으로
    #      열린 ㄷ 자**로 닫는다. 립 쪽이 먼저 닳는 실물 마모 순서와 §5.8 의
    #      "황색 잔존 20~30 %" 처방에 그대로 맞고, 전 컷에서 합법이다
    #      (d2·d5 는 E 대역 밖, d10 은 Δ 21.0 ≥ 16 `[실측]`).
    #      립을 감싸는 배치를 원한다면 점자블록과 같은 **GT-E2-x 등재**
    #      (EXPECTED_FP) 가 필요하고 그건 GRAZE 판정자 소관이다 — 감독 안건.
    gkit=dict(
        region=(-9.0, -6.0, 0.0, 6.0),
        #  개구 표시 도색 잔흔 — (x0, y0, yaw, length). 서립에서 0.15 물림.
        #  3본째는 yaw 90° 횡단 띠: x=−3.00 중심, y −1.125…+1.125 (종방향
        #  2본의 폭 0.15 바깥선까지 덮어 모서리가 맞물린다).
        mark_lines=[(-3.00, -1.05, 0.0, 2.85), (-3.00, 1.05, 0.0, 2.85),
                    (-3.00, -1.125, 90.0, 2.25)],
        #  발자국 동선 — 개구를 향해 걸어온 흔적(개구 위는 지나지 않는다).
        foot_path=[(-7.0, -0.90), (-1.2, -0.30)],
        foot_n=12,
    ),

    # 파쇄 콘크리트 부스러기 산포 (seed 고정)
    debris=dict(seed=2907, count=46, perim_ratio=0.6,
                x0=-2.2, x1=4.2, y0=-2.6, y1=2.6,
                ring_lo=0.03, ring_hi=0.55,
                s_lo=0.030, s_hi=0.130, sink=0.35),

    # cue (기본 OFF — 무방호가 이 씬의 위험 본질)
    nosing=dict(width=0.15, proud=0.002, color=(0.85, 0.72, 0.10)),
    opening_rail=dict(rail_h=0.95, post_r=0.025, rail_r=0.022,
                      mid_h=0.48, offset=0.45),

    # 외부 지면(흙) — 슬래브와 0.05 단차뿐 → 보행 연속성 확보(교훈 9)
    #   overlap: 지면 4박스를 건물 풋프린트 안쪽으로 6 cm 밀어넣어 슬래브
    #   측면과의 수직 동일평면(전/후면 맞댐 → Z-파이팅)을 제거한다.
    ground=dict(z_top=-0.05, thick=1.0, half=60.0, overlap=0.06),
    dressing=dict(
        # 거푸집 패널 3매(북벽에 기대 세움)
        panels=[dict(cx=3.0), dict(cx=4.4), dict(cx=5.8)],
        panel=dict(w=1.15, t=0.055, h=2.35, y_c=6.10, tilt=12.0),
        # 잔토·자갈 더미 2
        piles=[dict(cx=6.1, cy=-4.6, sx=1.7, sy=1.15, sz=0.42),
               dict(cx=-6.8, cy=4.1, sx=1.2, sy=0.9, sz=0.30)],
        # 외부 흙무지 2 + 원경 능선(-Y 지평 폐쇄)
        #   v2(맥락 드레싱): r2 판정 "우측 마운드가 매끈한 조약돌로 이질적" →
        #   **낮고 넓게 + 로브 3분할**로 잔토 더미화. 최고점 ≈ gz−sink+sz.
        #   (예: −0.05−0.55+1.45 = 0.85 m 높이 × 18 m 폭 = 잔토 프로파일)
        mounds=[dict(cx=-16.0, cy=-26.0, sink=0.55,
                     lobes=[(0.0, 0.0, 9.0, 5.2, 1.45),
                            (7.5, 2.4, 5.6, 3.4, 1.05),
                            (-7.0, -1.8, 6.2, 3.6, 0.95)]),
                dict(cx=15.0, cy=-33.0, sink=0.60,
                     lobes=[(0.0, 0.0, 10.5, 5.8, 1.50),
                            (-8.0, 2.0, 6.0, 3.6, 1.10),
                            (8.5, -1.5, 5.4, 3.2, 0.95)])],
        ridge=dict(cy=-52.0, half_x=58.0, t=8.0, h=8.5),
    ),

    # ─── 맥락 드레싱 v2 (2026-07-27, 휑함 해소) ────────────────────────────
    #   목적: "여기가 골조 공사 현장"이 읽히게. 전 요소 cue_scene_dressing 소속.
    #   ★ 불변: 개구(1.5×2.0)·철근 스터브·부스러기 산포·슬래브 4분할·스커트·지하층.
    #   ★ 배치 원칙(검산은 build_site_dressing docstring):
    #     ① grid_views(gy=0) 카메라 → 개구 시선 반폭 |y| ≤ 0.75·(x+10)/10.
    #        신규 입체는 전부 그 웨지 **밖**(최소 이격 1.6 m 이상).
    #     ② 개구 자체는 **무방호 유지** — 안전 펜스는 개구에서 3.9 m 이상 이격,
    #        개구를 둘러싸지 않는 **직선 1열**(북측)로만 둔다.
    #     ③ 원경 크레인은 동벽(x 8.15, h 3.2) 남단을 스치는 방위에만 성립 —
    #        좌표 검산으로 시선 통과를 확인(주석 참조).
    site=dict(
        # 철근 다발(눕힘). 저프로파일(≤0.20 m)이라 어떤 시선도 가리지 않는다.
        rebar_bundles=[dict(tag="A", cx=-3.40, cy=3.90, yaw=4.0, L=5.0,
                            rows=3, per_row=4),
                       dict(tag="B", cx=3.20, cy=-3.40, yaw=-7.0, L=4.2,
                            rows=2, per_row=5)],
        bundle=dict(r=0.010, batten_w=0.16, batten_h=0.085, batten_d=0.45,
                    strap_t=0.012),
        # 시멘트 포대 팔레트
        bagpallets=[dict(tag="A", cx=-3.60, cy=-3.60, yaw=12.0, layers=4),
                    dict(tag="B", cx=4.60, cy=3.40, yaw=-8.0, layers=3)],
        bagpallet=dict(pw=1.20, pd=1.00, pt=0.14, bw=0.52, bd=0.34, bh=0.11,
                       seed=6203),
        # 이동식 안전 펜스 3매 (북측 1열 — **개구는 무방호 유지가 특색**)
        fences=[dict(cx=-1.00, cy=4.60), dict(cx=1.10, cy=4.60),
                dict(cx=3.20, cy=4.60)],
        fence=dict(w=2.00, h=1.90, post_r=0.024, rail_r=0.018, bar_r=0.008,
                   n_bar=7, foot_d=0.62, foot_w=0.10, foot_h=0.06),
        # 전선 릴 · 공구 상자
        reel=dict(cx=-5.40, cy=2.40, flange_r=0.46, flange_t=0.05,
                  coil_r=0.40, coil_w=0.42),
        toolboxes=[dict(cx=-4.85, cy=1.70, yaw=15.0, w=0.72, d=0.40, h=0.36),
                   dict(cx=-5.95, cy=3.15, yaw=-22.0, w=0.55, d=0.34, h=0.30)],
        # 기둥 안전 표어 박판(무텍스트 색면) — colonnade 인덱스 3(x 2.5)·4(x 5.5)
        placards=[dict(col=3, z=1.58), dict(col=4, z=1.66)],
        placard=dict(w=0.42, h=0.56, t=0.04, band_h=0.14, proud=0.010),
        # 원경 타워크레인 (가는 박스 조합, 거리 ≈110 m)
        #   cy=−40: 동벽 남단(y −6.05)·기둥(x 5.5, y −6.425..−5.975) 양쪽을
        #   여유 있게 비껴가는 방위(검산치는 build_site_dressing docstring).
        #   정점 15.4 m @ 거리 110 m → 앙각 7.5° < 프레임 상한 8.0°.
        crane=dict(cx=100.0, cy=-40.0, base_z=-1.20,
                   mast_w=1.15, mast_top=14.20,
                   apex_w=1.60, apex_top=15.40,
                   jib_len=28.0, jib_w=0.85, jib_h=1.15, jib_z0=13.40,
                   cjib_len=11.0, cjib_w=0.95, cjib_h=1.00, cjib_z0=13.50,
                   cw_w=1.60, cw_d=2.40, cw_h=1.80,
                   hook_dy=-14.0, hook_w=0.46, hook_h=0.85, hook_z0=6.60,
                   rope_w=0.07),
        # 원경 지면 패드 — 기존 ground(half 60) 밖으로 시선이 빠지지 않게 폐쇄.
        #   상면 −0.06 = 기존 지면(−0.05)보다 1 cm 아래 → 겹침부 코플래너 0.
        farpad=dict(x0=45.0, x1=420.0, y0=-260.0, y1=260.0,
                    z_top=-0.06, thick=1.0),
    ),

    material=dict(
        scale=dict(concrete_floor=1.2, concrete_wall=2.0,
                   dirt_park=3.0, gravel=0.9),
        slab_tint=(0.88, 0.86, 0.82),       # 시멘트 먼지 틴트(밝은 회백)
        lower_wall_tint=(0.58, 0.58, 0.57),  # 지하 거푸집 — 채도·명도 저하
        lower_floor_tint=(0.52, 0.51, 0.49),
        wall_tint=(0.92, 0.91, 0.89),        # 지상 거푸집 벽(밝음)
        # 개구 하단 그을린 거푸집 — sRGB 암색 대역 0.02~0.06 [교훈 1]
        skirt_color=(0.042, 0.042, 0.045), skirt_rough=0.95,
        rebar_color=(0.25, 0.12, 0.08), rebar_metallic=0.8, rebar_rough=0.6,
        debris_colors=[(0.30, 0.29, 0.27), (0.24, 0.23, 0.22),   # r1: 0.55는 백색 지각 → 감광
                       (0.18, 0.175, 0.17)],
        debris_rough=0.95,
        panel_color=(0.46, 0.38, 0.27), panel_rough=0.88,   # 합판 거푸집
        rail_color=(0.80, 0.60, 0.10), rail_metallic=0.6, rail_rough=0.5,
        # ── 맥락 드레싱 v2 ── (소품 중간톤 0.18~0.35 규약 준수. 암색 0.02~0.09
        #    대역은 개구 스커트·전선 코일처럼 '실제로 검은' 것에만.)
        bag_color=(0.52, 0.49, 0.43), bag_rough=0.92,       # 시멘트 포대(종이)
        fence_color=(0.50, 0.51, 0.53), fence_metallic=0.60,
        fence_rough=0.38,
        cable_color=(0.055, 0.055, 0.060), cable_rough=0.85,  # 전선 코일(암색)
        tool_color=(0.34, 0.12, 0.09), tool_metallic=0.20, tool_rough=0.55,
        placard_color=(0.68, 0.68, 0.65), placard_rough=0.60,
        placard_band=(0.09, 0.34, 0.18),                    # 안전 표어 색띠(녹)
        crane_color=(0.40, 0.38, 0.33), crane_metallic=0.25,
        crane_rough=0.70,
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
    # ─── SUN_AZ_OFFSET 근거 (씬별 재정의 — 브리프 v3 §A-7) ───
    #   태양 매핑 월드 az ≈ 33.5 + offset = 185.5  →  그림자 az = az−180 = 5.5°
    #   ① 그림자가 거의 정 +X (카메라 등 뒤 태양) → 슬래브 상면·철근 스터브·
    #      부스러기가 정면광으로 또렷하고, 개구는 상대적으로 더 검게 읽힌다.
    #   ② 개구(x 0..2)를 통과한 직달광은 3.0 m 낙하하는 동안 수평으로
    #      3.0/tan(49.79°) = 2.53 m 밀려 지하 바닥 x 2.53..4.53 에 착지.
    #      그 광반의 반사광이 지하 동쪽 벽(x=7.0)을 비추고, 그 벽면이 바로
    #      h0.9/d4~5 보행 시점에서 개구 너머로 보이는 영역(z −1.6..−0.8)이다.
    #      → **"어둡되 완전 0 아님"** 목표(사양서 §C)를 기하학적으로 보장.
    #   ③ +5.5°의 미세 요각으로 광반·그림자가 살짝 사선이 되어 평면적 인상 회피.
    #   [ ]키(dome_rotation_step 15°)로 GUI 추가 스윕 가능.
    SUN_AZ_OFFSET=152.0,

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


def fence_placements():
    """[v5.1 §3] 이동식 안전 펜스 3매 — 등간격 2.1 m·축평행을 해소.
    위치 ±0.18 m · yaw ±3~8° (좌표 해시 결정적). 실제 현장의 가설 펜스는
    딱 맞춰 늘어서 있지 않다. ★ 개구(무방호 유지)와의 이격 3.9 m 는
    지터폭(0.18)보다 압도적으로 커서 '개구 무방호' 특색 불변."""
    out = []
    for i, fd in enumerate(PARAMS["site"]["fences"]):
        dx, dy = bc.jit_pos(fd["cx"], fd["cy"], "fenceD2", amp=0.18)
        yaw = bc.jit_yaw(fd["cx"], fd["cy"], "fenceD2", lo=3.0, hi=8.0)
        out.append((i, fd["cx"] + dx, fd["cy"] + dy, yaw))
    return out


def formpanel_xs():
    """[v5.1 §3] 북벽에 기대 세운 거푸집 패널 3매의 x ±0.16 m 지터."""
    return [pd["cx"] + bc.jit_scalar(pd["cx"], 0.0, "panelD2", -0.16, 0.16)
            for pd in PARAMS["dressing"]["panels"]]


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
# [C] 경로 상수 + 필요 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneD2")

ASSET_ROLES = ["concrete_floor", "concrete_wall", "dirt_park", "gravel",
               "hdri", "mdl"]


def ground_plans():
    """[W2 ground_kit] 지면 계획 — 씬 조립부와 CPU 검산이 같은 함수를 쓴다."""
    g = PARAMS["gkit"]
    op = PARAMS["opening"]
    gp = gk.plan_ground(
        "slab_construction", region=tuple(g["region"]),
        z=float(PARAMS["deck"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("opening_lip", float(op["x0"]))],
        voids=((float(op["x0"]), float(op["y0"]),
                float(op["x1"]), float(op["y1"])),),
        dists=(2, 5, 10), scene="sceneD2",
        tactile=(),                     # §12.4 — 비대상(공사장)
        sites=dict(marking=[tuple(m) for m in g["mark_lines"]]),
        overrides=dict(infra=dict(marking=("line", "line", "line")),
                       extras=(("footprints",
                                dict(n=int(g["foot_n"]),
                                     path_pts=[tuple(p)
                                               for p in g["foot_path"]])),)),
        seed=29)
    return [("slab", gp)]


def build_views():
    """카메라 프리셋: grid_views(gy=0.0, 개구 정면 직교 접근) + 미장센 4컷.

    사양서 §C 카메라: '보행 접근각 4 m · h0.9' → grid_views d5/h0.9 및
    미장센 approach(d4·h0.9)가 모두 그 축에 정합한다.
    """
    views = sc.grid_views(0.0)
    # approach: 사양서 명시 시점 — 보행자가 4 m 앞에서 개구를 마주함
    views["approach"] = dict(eye=[-4.0, 0.0, 0.9], tgt=[1.2, 0.0, -0.35])
    # brink: 립 바로 앞에서 내려다봄 — 지하 바닥 광반·거푸집 벽 노출
    views["brink"] = dict(eye=[-1.0, 0.0, 1.60], tgt=[1.6, 0.15, -2.30])
    # graze: 저시점 — 개구가 얇은 검은 띠로 납작해지는 은닉 구도(위험 극대)
    views["graze"] = dict(eye=[-6.0, -0.25, 0.35], tgt=[2.5, 0.05, 0.02])
    # beauty_overview: 사선 부감 — 개구·철근·거푸집 벽 코너 일괄 판독
    views["beauty_overview"] = dict(eye=[-5.2, -5.0, 3.4], tgt=[1.2, 0.4, -0.9])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach/preset_h0.9_d5 — 1.5×2.0 개구가 '검은 사각형'으로 읽히는가(특색)
 2. brink                   — 개구 내부가 어둡되 **완전 0이 아닌가**(PT 8바운스로 판정)
 3. graze (h0.35)           — 저시점에서 개구가 납작해지며 은닉되는가
 4. 철근·부스러기           — 립 주변 스터브 6+2+1본·부스러기 링이 낙차 단서로 작동
 5. 보행 연속성             — 슬래브↔외부 흙 단차 0.05, 개구 우회 가능
 6. Z-파이팅/부유           — 스커트 내면 물림 0.01, 스터브 하단 매입, 거푸집 패널 접지"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

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
    UsdGeom.Xform.Define(stage, "/World/Scene29")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene29"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def OBOX(path, center, size, mtl=None, rotz=0.0, rotx=0.0):
        return sc._oriented_box(stage, path, center, size, mtl,
                                rotz=rotz, rotx=rotx)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def SPH(path, center, scale3, mtl=None):
        return sc.add_sphere(stage, path, center, scale3, mtl)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["slab"] = PBR(
            f"{ROOT}/Looks/Slab", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["slab_tint"])
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["wall_tint"])
        M["lower_wall"] = PBR(
            f"{ROOT}/Looks/LowerWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["lower_wall_tint"])
        M["lower_floor"] = PBR(
            f"{ROOT}/Looks/LowerFloor", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["lower_floor_tint"])
        M["dirt"] = PBR(
            f"{ROOT}/Looks/Dirt", sc.tex_path("dirt_park", "diff"),
            sc.tex_path("dirt_park", "nor"), sc.tex_path("dirt_park", "rough"),
            sca["dirt_park"])
        M["gravel"] = PBR(
            f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            sca["gravel"])
        M["skirt"] = PBR(f"{ROOT}/Looks/Skirt",
                         diffuse_color=mp["skirt_color"],
                         roughness_const=mp["skirt_rough"], metallic=0.0)
        M["rebar"] = PBR(f"{ROOT}/Looks/Rebar",
                         diffuse_color=mp["rebar_color"],
                         metallic=mp["rebar_metallic"],
                         roughness_const=mp["rebar_rough"])
        for i, c in enumerate(mp["debris_colors"]):
            M[f"debris{i}"] = PBR(f"{ROOT}/Looks/Debris_{i}",
                                  diffuse_color=c,
                                  roughness_const=mp["debris_rough"])
        M["panel"] = PBR(f"{ROOT}/Looks/Panel",
                         diffuse_color=mp["panel_color"],
                         roughness_const=mp["panel_rough"])
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing",
                          diffuse_color=PARAMS["nosing"]["color"],
                          roughness_const=0.75)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # ── 맥락 드레싱 v2 재질 ──
        M["bag"] = PBR(f"{ROOT}/Looks/Bag", diffuse_color=mp["bag_color"],
                       roughness_const=mp["bag_rough"])
        M["fence"] = PBR(f"{ROOT}/Looks/Fence", diffuse_color=mp["fence_color"],
                         metallic=mp["fence_metallic"],
                         roughness_const=mp["fence_rough"])
        M["cable"] = PBR(f"{ROOT}/Looks/Cable", diffuse_color=mp["cable_color"],
                         roughness_const=mp["cable_rough"])
        M["tool"] = PBR(f"{ROOT}/Looks/Tool", diffuse_color=mp["tool_color"],
                        metallic=mp["tool_metallic"],
                        roughness_const=mp["tool_rough"])
        M["placard"] = PBR(f"{ROOT}/Looks/Placard",
                           diffuse_color=mp["placard_color"],
                           roughness_const=mp["placard_rough"])
        M["placard_band"] = PBR(f"{ROOT}/Looks/PlacardBand",
                                diffuse_color=mp["placard_band"],
                                roughness_const=mp["placard_rough"])
        M["crane"] = PBR(f"{ROOT}/Looks/Crane", diffuse_color=mp["crane_color"],
                         metallic=mp["crane_metallic"],
                         roughness_const=mp["crane_rough"])
        return M

    # -------------------------------------------------------------------
    # 외부 지면(흙) — 건물 풋프린트를 비운 4박스 (지하 공동을 덮지 않음)
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        d = PARAMS["deck"]
        H = g["half"]
        th = g["thick"]
        cz = g["z_top"] - th / 2.0
        ov = g["overlap"]
        # 건물 풋프린트 안쪽으로 ov 만큼 물린 경계(지면 상면 −0.05 는 슬래브
        # 하면 −0.25 보다 위이므로, 물린 부분은 슬래브에 가려 보이지 않는다)
        xw, xe = d["x_w"] + ov, d["x_e"] - ov
        ys, yn = d["y_s"] + ov, d["y_n"] - ov
        BOX(f"{ROOT}/Ground_W", ((-H + xw) / 2.0, 0.0, cz),
            (xw + H, 2.0 * H, th), M["dirt"], col=True)
        BOX(f"{ROOT}/Ground_E", ((xe + H) / 2.0, 0.0, cz),
            (H - xe, 2.0 * H, th), M["dirt"], col=True)
        BOX(f"{ROOT}/Ground_S", ((xw + xe) / 2.0, (-H + ys) / 2.0, cz),
            (xe - xw, ys + H, th), M["dirt"], col=True)
        BOX(f"{ROOT}/Ground_N", ((xw + xe) / 2.0, (yn + H) / 2.0, cz),
            (xe - xw, H - yn, th), M["dirt"], col=True)

    # -------------------------------------------------------------------
    # 슬래브 — **개구 4박스 분할** (브리프 v3 §A-3 / 교훈 5)
    #   공동(개구) 위를 어떤 박스도 덮지 않는다.
    # -------------------------------------------------------------------
    def build_slab(M):
        d = PARAMS["deck"]
        op = PARAMS["opening"]
        th = d["thick"]
        # [W2-0 · P-A] 슬래브 4분할 전체가 ground_kit 의 장식 대상이다 →
        #   변위 스킨 OFF(**BOX 호출 전에** 등록). 콜드 조인트(음각 톤)·
        #   도색 잔흔(+3 mm)·발자국(+0.6 mm)이 전부 스킨 아래로 사라진다.
        sc.skin_exclude(f"{ROOT}/Slab_W", f"{ROOT}/Slab_E",
                        f"{ROOT}/Slab_S", f"{ROOT}/Slab_N",
                        f"{ROOT}/Slab_Fill")
        cz = d["z_top"] - th / 2.0
        xw, xe, ys, yn = d["x_w"], d["x_e"], d["y_s"], d["y_n"]
        ox0, ox1, oy0, oy1 = op["x0"], op["x1"], op["y0"], op["y1"]
        # ① 서: x_w..개구서립, 전폭
        BOX(f"{ROOT}/Slab_W", ((xw + ox0) / 2.0, (ys + yn) / 2.0, cz),
            (ox0 - xw, yn - ys, th), M["slab"], col=True)
        # ② 동: 개구동립..x_e, 전폭
        BOX(f"{ROOT}/Slab_E", ((ox1 + xe) / 2.0, (ys + yn) / 2.0, cz),
            (xe - ox1, yn - ys, th), M["slab"], col=True)
        # ③ 남: 개구 x구간, y_s..개구남립
        BOX(f"{ROOT}/Slab_S", ((ox0 + ox1) / 2.0, (ys + oy0) / 2.0, cz),
            (ox1 - ox0, oy0 - ys, th), M["slab"], col=True)
        # ④ 북: 개구 x구간, 개구북립..y_n
        BOX(f"{ROOT}/Slab_N", ((ox0 + ox1) / 2.0, (oy1 + yn) / 2.0, cz),
            (ox1 - ox0, yn - oy1, th), M["slab"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False 대조군: 개구를 슬래브로 메움(전 픽셀 낙차 없음)."""
        d = PARAMS["deck"]
        op = PARAMS["opening"]
        th = d["thick"]
        BOX(f"{ROOT}/Slab_Fill",
            ((op["x0"] + op["x1"]) / 2.0, (op["y0"] + op["y1"]) / 2.0,
             d["z_top"] - th / 2.0),
            (op["x1"] - op["x0"], op["y1"] - op["y0"], th), M["slab"], col=True)

    # -------------------------------------------------------------------
    # 개구 하단 거푸집 스커트 — 립 바로 아래 암부 확보(암색 상수 0.042)
    #   내면을 개구보다 inset(0.01) 만큼 **바깥으로** 물려 슬래브 개구
    #   리빌면과 동일평면이 되지 않게 한다 (Z-파이팅 금지, 브리프 §A-8).
    # -------------------------------------------------------------------
    def build_skirt(M):
        op = PARAMS["opening"]
        sk = PARAMS["skirt"]
        ins, t = sk["inset"], sk["thick"]
        z0, z1 = sk["z_bot"], sk["z_top"]
        cz, hz = (z0 + z1) / 2.0, z1 - z0
        xa, xb = op["x0"] - ins, op["x1"] + ins       # 스커트 내면
        ya, yb = op["y0"] - ins, op["y1"] + ins
        # 코너에서 W/E 와 S/N 이 서로 **엄격히 내부로** 겹치도록 e(0.02)를 준다
        # → 4박스 프레임의 코너 맞댐면(동일평면) 제거.
        e = 0.02
        BOX(f"{ROOT}/Skirt_W", (xa - t / 2.0, (ya + yb) / 2.0, cz),
            (t, yb - ya + 2.0 * e, hz), M["skirt"])
        BOX(f"{ROOT}/Skirt_E", (xb + t / 2.0, (ya + yb) / 2.0, cz),
            (t, yb - ya + 2.0 * e, hz), M["skirt"])
        # S/N 은 z 를 2 mm 안쪽으로 물려 코너 겹침부의 상·하면 동일평면 제거
        BOX(f"{ROOT}/Skirt_S", ((xa + xb) / 2.0, ya - t / 2.0, cz),
            (xb - xa + 2.0 * (t + e), t, hz - 0.004), M["skirt"])
        BOX(f"{ROOT}/Skirt_N", ((xa + xb) / 2.0, yb + t / 2.0, cz),
            (xb - xa + 2.0 * (t + e), t, hz - 0.004), M["skirt"])

    # -------------------------------------------------------------------
    # 지하층 — 바닥(z −3.0) + 거푸집 벽 4면. 천장은 슬래브(z −0.25)가 겸한다.
    #   벽 상단 −0.20 으로 슬래브 하면(−0.25)과 0.05 겹침 → 틈 없음.
    # -------------------------------------------------------------------
    def build_lower(M):
        lw = PARAMS["lower"]
        t = lw["wall_t"]
        x0, x1, y0, y1 = lw["x0"], lw["x1"], lw["y0"], lw["y1"]
        zf, ft = lw["z_floor"], lw["floor_t"]
        # 바닥판: 벽 외곽보다 0.05 더 크게 → 벽 외곽면과의 동일평면 회피
        BOX(f"{ROOT}/Lower_Floor",
            ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zf - ft / 2.0),
            (x1 - x0 + 2.0 * t + 0.10, y1 - y0 + 2.0 * t + 0.10, ft),
            M["lower_floor"], col=True)
        # 벽 하단을 바닥판 상면보다 0.10 낮춰 수평 동일평면(맞댐) 회피
        zwb = zf - 0.10
        czw = (zwb + lw["z_ceil"]) / 2.0
        hzw = lw["z_ceil"] - zwb
        # 코너: W/E 는 y 를, S/N 은 x 를 각각 벽 두께 + 0.02 만큼 넘겨 겹침
        # (4박스 프레임 코너 맞댐면 제거)
        e = 0.02
        BOX(f"{ROOT}/Lower_Wall_W", (x0 - t / 2.0, (y0 + y1) / 2.0, czw),
            (t, y1 - y0 + 2.0 * t, hzw), M["lower_wall"], col=True)
        BOX(f"{ROOT}/Lower_Wall_E", (x1 + t / 2.0, (y0 + y1) / 2.0, czw),
            (t, y1 - y0 + 2.0 * t, hzw), M["lower_wall"], col=True)
        ts = t - e                                   # S/N 두께(외곽면을 0.02 안쪽)
        # S/N 은 z 도 2 cm 안쪽으로 물려 코너 겹침부의 상·하면 동일평면 제거
        BOX(f"{ROOT}/Lower_Wall_S", ((x0 + x1) / 2.0, y0 - ts / 2.0, czw),
            (x1 - x0 + 2.0 * ts, ts, hzw - 0.04), M["lower_wall"], col=True)
        BOX(f"{ROOT}/Lower_Wall_N", ((x0 + x1) / 2.0, y1 + ts / 2.0, czw),
            (x1 - x0 + 2.0 * ts, ts, hzw - 0.04), M["lower_wall"], col=True)

    # -------------------------------------------------------------------
    # 지상 거푸집 벽 2면(동·북) + 남측 기둥 개구부(채광원)
    # -------------------------------------------------------------------
    def build_upper_walls(M):
        w = PARAMS["walls"]
        t, h = w["t"], w["h"]
        xf, yf = w["x_face"], w["y_face"]
        # 동벽 — 주 카메라 축(+X) 정면 지평 폐쇄 (브리프 §A-4)
        ey0, ey1 = w["e_y0"], w["e_y1"]
        BOX(f"{ROOT}/Wall_E", (xf + t / 2.0, (ey0 + ey1) / 2.0,
                               (w["base"] + h) / 2.0),
            (t, ey1 - ey0, h - w["base"]), M["wall"], col=True)
        # 북벽 — 동벽과 x 방향으로 겹치되 z 범위를 달리해 코너 동일평면 제거
        nx0, nx1 = w["n_x0"], w["n_x1"]
        hn, tn = h - w["n_h_delta"], w["n_t"]
        BOX(f"{ROOT}/Wall_N", ((nx0 + nx1) / 2.0, yf + tn / 2.0,
                               (w["n_base"] + hn) / 2.0),
            (nx1 - nx0, tn, hn - w["n_base"]), M["wall"], col=True)
        # 남측 기둥열 — 사이 간극으로 외부 흙·하늘 노출 = 실내 암부 방지 채광원
        co = PARAMS["colonnade"]
        s = co["size"]
        for i, cx in enumerate(co["xs"]):
            BOX(f"{ROOT}/Column_{i}", (cx, co["y_c"], (w["base"] + co["h"]) / 2.0),
                (s, s, co["h"] - w["base"]), M["wall"], col=True)

    # -------------------------------------------------------------------
    # 철근 스터브 — 직선 6 + 굽은 것 2(_oriented_box) + 갈고리 1
    # -------------------------------------------------------------------
    def build_rebar(M):
        rb = PARAMS["rebar"]
        for i, (cx, cy) in enumerate(rb["straight"]):
            CYL(f"{ROOT}/Rebar_{i}", (cx, cy, rb["z_c"]), rb["r"], rb["h"],
                M["rebar"])
        L, t = rb["bent_len"], rb["bent_t"]
        for i, (cx, cy, tilt, yaw) in enumerate(rb["bent"]):
            # 로컬 Z=철근 축. rotx로 기울이고 rotz로 방위를 준다.
            # 기운 뒤 수직 길이 = L*cos(tilt) → 하단이 슬래브에 매입되도록 중심 z.
            zc = L * math.cos(math.radians(tilt)) / 2.0 - 0.055
            OBOX(f"{ROOT}/RebarBent_{i}", (cx, cy, zc), (t, t, L),
                 M["rebar"], rotz=yaw, rotx=tilt)
        hk = rb["hook"]
        OBOX(f"{ROOT}/RebarHook", (hk["cx"], hk["cy"], hk["z"]),
             (hk["lx"], hk["t"], hk["t"]), M["rebar"], rotz=hk["yaw"])

    # -------------------------------------------------------------------
    # 파쇄 콘크리트 부스러기 — seed 고정 random (재현성). 개구 내부 배치 금지
    #   (공동 위 부유 방지). 60%는 립 둘레 링에 몰아 '부스러기 테'를 만든다.
    # -------------------------------------------------------------------
    def build_debris(M):
        db = PARAMS["debris"]
        op = PARAMS["opening"]
        rng = random.Random(db["seed"])
        mats = [M[f"debris{i}"] for i in range(len(mp["debris_colors"]))]
        n_mat = len(mats)
        placed = 0
        guard = 0
        while placed < db["count"] and guard < db["count"] * 20:
            guard += 1
            if rng.random() < db["perim_ratio"]:
                off = rng.uniform(db["ring_lo"], db["ring_hi"])
                side = rng.randrange(4)
                if side == 0:                      # 서립 바깥
                    px = op["x0"] - off
                    py = rng.uniform(op["y0"] - 0.5, op["y1"] + 0.5)
                elif side == 1:                    # 동립 바깥
                    px = op["x1"] + off
                    py = rng.uniform(op["y0"] - 0.5, op["y1"] + 0.5)
                elif side == 2:                    # 남립 바깥
                    px = rng.uniform(op["x0"] - 0.5, op["x1"] + 0.5)
                    py = op["y0"] - off
                else:                              # 북립 바깥
                    px = rng.uniform(op["x0"] - 0.5, op["x1"] + 0.5)
                    py = op["y1"] + off
            else:
                px = rng.uniform(db["x0"], db["x1"])
                py = rng.uniform(db["y0"], db["y1"])
            # 개구 내부(공동 위) 배치 금지 — 부유 파편 방지
            if (op["x0"] - 0.02 < px < op["x1"] + 0.02
                    and op["y0"] - 0.02 < py < op["y1"] + 0.02):
                continue
            s = rng.uniform(db["s_lo"], db["s_hi"])
            mtl = mats[placed % n_mat]
            sink = db["sink"]
            if placed % 3 == 2:
                # 납작 타원체: 반경 rz, 중심 z = rz*(1−2·sink) → 하단 매입
                rz = s * 0.38
                SPH(f"{ROOT}/Debris_{placed}",
                    (px, py, rz * (1.0 - 2.0 * sink)),
                    (s * 0.6, s * 0.5, rz), mtl)
            else:
                # 박스: 높이 hz, 중심 z = hz*(0.5−sink) → 하단 −hz·sink (매입)
                hz = s * rng.uniform(0.4, 0.8)
                OBOX(f"{ROOT}/Debris_{placed}",
                     (px, py, hz * (0.5 - sink)),
                     (s, s * rng.uniform(0.55, 1.0), hz),
                     mtl, rotz=rng.uniform(0.0, 90.0))
            placed += 1
        return placed

    # -------------------------------------------------------------------
    # cue — 경고 도색 / 임시 난간 (기본 OFF: 무방호가 이 씬의 위험 본질)
    # -------------------------------------------------------------------
    def build_cues(M):
        op = PARAMS["opening"]
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            w, pr = ns["width"], ns["proud"]
            t = 0.01
            cz = pr - t / 2.0
            xa, xb, ya, yb = op["x0"], op["x1"], op["y0"], op["y1"]
            BOX(f"{ROOT}/Nosing_W", (xa - w / 2.0, (ya + yb) / 2.0, cz),
                (w, yb - ya, t), M["nosing"])
            BOX(f"{ROOT}/Nosing_E", (xb + w / 2.0, (ya + yb) / 2.0, cz),
                (w, yb - ya, t), M["nosing"])
            BOX(f"{ROOT}/Nosing_S", ((xa + xb) / 2.0, ya - w / 2.0, cz),
                (xb - xa + 2.0 * w, w, t), M["nosing"])
            BOX(f"{ROOT}/Nosing_N", ((xa + xb) / 2.0, yb + w / 2.0, cz),
                (xb - xa + 2.0 * w, w, t), M["nosing"])
        if cfg["cue_railing"]:
            rr = PARAMS["opening_rail"]
            o = rr["offset"]
            xa, xb = op["x0"] - o, op["x1"] + o
            ya, yb = op["y0"] - o, op["y1"] + o
            corners = [(xa, ya), (xb, ya), (xb, yb), (xa, yb)]
            for i, (cx, cy) in enumerate(corners):
                CYL(f"{ROOT}/OpenRail_Post_{i}",
                    (cx, cy, rr["rail_h"] / 2.0 - 0.05),
                    rr["post_r"], rr["rail_h"] + 0.10, M["rail"])
            for i in range(4):
                ax, ay = corners[i]
                bx, by = corners[(i + 1) % 4]
                mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
                length = math.hypot(bx - ax, by - ay)
                horiz = abs(by - ay) < 1e-9
                for tag, zc in (("Top", rr["rail_h"]), ("Mid", rr["mid_h"])):
                    if horiz:
                        CYL(f"{ROOT}/OpenRail_{tag}_{i}", (mx, my, zc),
                            rr["rail_r"], length, M["rail"], rotY=90.0)
                    else:
                        CYL(f"{ROOT}/OpenRail_{tag}_{i}", (mx, my, zc),
                            rr["rail_r"], length, M["rail"], rotX=90.0)

    # -------------------------------------------------------------------
    # 드레싱 — 거푸집 패널·잔토 더미·외부 흙무지·원경 능선
    # -------------------------------------------------------------------
    def build_dressing(M):
        dr = PARAMS["dressing"]
        pn = dr["panel"]
        tilt = pn["tilt"]
        # 기운 패널: 수직 반높이 = (h/2)*cos(tilt) → 하단이 슬래브(z=0)에 접지.
        # y 중심을 북벽 안쪽(6.10)에 두어 상·하단 중 한쪽이 반드시 벽에 물린다.
        zc = pn["h"] * math.cos(math.radians(tilt)) / 2.0 - 0.03
        for i, px in enumerate(formpanel_xs()):      # v5.1 §3 등간격 지터
            OBOX(f"{ROOT}/FormPanel_{i}", (px, pn["y_c"], zc),
                 (pn["w"], pn["t"], pn["h"]), M["panel"], rotx=tilt)
        for i, pl in enumerate(dr["piles"]):
            # 하단이 슬래브 상면(0)보다 0.06 만 아래로 물리게 — 슬래브(두께 0.25)를
            # 관통해 지하 천장으로 튀어나오지 않도록 sz 대비 얕게 매입한다.
            SPH(f"{ROOT}/Pile_{i}", (pl["cx"], pl["cy"], pl["sz"] - 0.06),
                (pl["sx"], pl["sy"], pl["sz"]), M["gravel"])
        gz = PARAMS["ground"]["z_top"]
        # 외부 흙무지 — v2: 로브 3분할·저편평(sink 로 하단을 지면에 묻어
        #   '매끈한 조약돌' 실루엣을 깬다). 최고점 = gz − sink + sz.
        for i, mo in enumerate(dr["mounds"]):
            for j, (dx, dy, sx, sy, sz) in enumerate(mo["lobes"]):
                SPH(f"{ROOT}/Mound_{i}_{j}",
                    (mo["cx"] + dx, mo["cy"] + dy, gz - mo["sink"]),
                    (sx, sy, sz), M["dirt"])
        rg = dr["ridge"]
        BOX(f"{ROOT}/Ridge_S", (0.0, rg["cy"], gz + rg["h"] / 2.0 - 0.5),
            (2.0 * rg["half_x"], rg["t"], rg["h"]), M["dirt"])

    # -------------------------------------------------------------------
    # 맥락 드레싱 v2 — 자재 더미(철근 다발·시멘트 포대) · 이동식 안전 펜스 ·
    #                  전선 릴/공구 상자 · 기둥 표어 박판 · 원경 타워크레인
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # [W2] ground_kit — P15 slab_construction. 개구(GT-V)와 서립(GT-E1′)을
    #   모두 존중한다. 판정은 B8(개구 교차 0)·B6(에지 이격)가 한다.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        (_tag, gp), = ground_plans()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["skirt"], crack=M["skirt"],
                  marking=M["nosing"],           # 황색 개구 표시 도색
                  stain_efflorescence=M["panel"], stain_dirt=M["dirt"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] sceneD2 P15 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    def build_site_dressing(M):
        """골조 공사장 맥락 요소. **개구·철근 스터브·부스러기·슬래브 분할 불변.**

        ── 카메라 검산 (전 뷰, 좌표 계산 근거) ─────────────────────────────
        grid_views(gy=0) hfov 60°(half tan 0.577)·pitch −10°·16:9 → vfov 36°.
        [개구 시선 웨지] 카메라 (−d,0) → 개구(x 0..2, |y| ≤ 0.75) 를 잇는 시선은
          x=px 에서 |y| ≤ 0.75·(px+d)/(d+1)  (d=10 이 최대폭).
          신규 입체 최근접 = 공구 상자(−4.85, 1.70) → 웨지 상한 0.39 →
          **여유 1.31 m**. 나머지는 전부 3 m 이상. → 개구 가림 0.
        [미장센 4컷]
          approach(−4,0,0.9→1.2,0,−0.35): 신규 입체는 전부 카메라 뒤이거나
            시축에서 51°+ (hfov half 30°) → 프레임 밖.
          brink(−1,0,1.6→1.6,0.15,−2.3): 개구 직상 하향컷. 반경 3 m 내 신규 0.
          graze(−6,−0.25,0.35→2.5,0.05,0.02): 릴 77°·공구 59°·포대팔레트 56°
            → 전부 프레임 밖. **저시점 은닉 구도 불변**.
          beauty_overview(−5.2,−5,3.4→1.2,0.4,−0.9): 포대팔레트 A 가 시축 26°
            (프레임 좌하단)에 들어오나, 개구 근립을 향한 시선의 해당 지점 고도
            z=2.40 m ≫ 팔레트 총고 0.55 m → **가림 0**(전경 소품으로만 작용).
        [원경 타워크레인 — 동벽 남단 스치기]
          크레인 (100, −40), 마스트 상단 14.2 / 정점 15.4.
          · 시선각: eye(−10,0) 기준 방위 21.8° < hfov half 30° → 프레임 안.
          · 동벽(x 8.15, y −6.05..6.45, h 3.2) 통과 검산: 마스트 방위선이
            x=8.15 에서 y = −40·18.15/110 = −6.60 < −6.05 → **벽 남단 밖 통과**
            (여유 0.55 m).
          · 콜로네이드 기둥(x 2.5·5.5, y −6.425..−5.975) 검산:
            x=2.5 에서 y=−4.55, x=5.5 에서 y=−5.64 → 둘 다 기둥 북측 → 무가림.
          · 고도 검산: 정점 15.4 m·거리 ≈110 m → 앙각 7.5° < 프레임 상한
            (pitch −10 + vfov half 18 = +8.0°) → **정점까지 프레임 안**.
          · **가시 뷰 = grid h*_d10(가장 넓은 컷)**. d5/d2·graze 는 동벽
            (앙각 9.9°/12.7°)에 가려 보이지 않는다 — 의도된 결과(근접 컷은
            개구가 주인공이어야 하므로 원경 소품이 끼어들지 않는 편이 낫다).
        [원경 지면 패드] 기존 ground half 60 m 밖(크레인 위치 100 m)의 허공을
          폐쇄. 상면 −0.06 은 기존 지면 −0.05 아래라 겹침부 코플래너 0.
        """
        st = PARAMS["site"]
        cnt = dict(rebar=0, bag=0, fence=0, tool=0, placard=0, crane=0)

        # ── ⓪ 원경 지면 패드 ──
        fp = st["farpad"]
        BOX(f"{ROOT}/FarPad",
            ((fp["x0"] + fp["x1"]) / 2.0, (fp["y0"] + fp["y1"]) / 2.0,
             fp["z_top"] - fp["thick"] / 2.0),
            (fp["x1"] - fp["x0"], fp["y1"] - fp["y0"], fp["thick"]), M["dirt"])

        # ── ① 철근 다발(눕힘) — 받침목 2 + 봉 rows×per_row + 결속 밴드 2 ──
        bu = st["bundle"]
        for rb in st["rebar_bundles"]:
            tag, cx, cy, yaw, L = rb["tag"], rb["cx"], rb["cy"], rb["yaw"], rb["L"]
            a = math.radians(yaw)
            ca, sa = math.cos(a), math.sin(a)

            def put(dx, dy, _cx=cx, _cy=cy, _ca=ca, _sa=sa):
                return (_cx + dx * _ca - dy * _sa, _cy + dx * _sa + dy * _ca)

            for k, dx in enumerate((-L / 2.0 + 0.55, L / 2.0 - 0.55)):
                bx, by = put(dx, 0.0)
                OBOX(f"{ROOT}/Batten_{tag}_{k}",
                     (bx, by, bu["batten_h"] / 2.0 - 0.01),
                     (bu["batten_w"], bu["batten_d"], bu["batten_h"]),
                     M["panel"], rotz=yaw)
            r = bu["r"]
            for row in range(int(rb["rows"])):
                zc = bu["batten_h"] + r + row * (1.85 * r)
                off = (row % 2) * r          # 층마다 반 피치 엇물림(적층 안정감)
                for j in range(int(rb["per_row"])):
                    dy = (j - (rb["per_row"] - 1) / 2.0) * (2.2 * r) + off
                    px, py = put(0.0, dy)
                    # add_cylinder 는 rotz 를 못 받으므로 방위가 필요한 봉은
                    # _oriented_box 로(D20 굵기에서 원/각 단면 차는 비가시).
                    OBOX(f"{ROOT}/RebarBar_{tag}_{row}_{j}", (px, py, zc),
                         (L, 2.0 * r, 2.0 * r), M["rebar"], rotz=yaw)
                    cnt["rebar"] += 1
            # 결속 밴드 2 (봉 다발을 감싸는 얇은 띠)
            hz = bu["batten_h"] + 2.0 * r * int(rb["rows"]) + 0.02
            wy = rb["per_row"] * 2.2 * r + 0.05
            for k, dx in enumerate((-L / 4.0, L / 4.0)):
                bx, by = put(dx, 0.0)
                OBOX(f"{ROOT}/Strap_{tag}_{k}", (bx, by, hz / 2.0),
                     (bu["strap_t"], wy, hz), M["rail"], rotz=yaw)

        # ── ② 시멘트 포대 팔레트 ──
        bp = st["bagpallet"]
        brng = random.Random(bp["seed"])
        for pd_ in st["bagpallets"]:
            tag, cx, cy, yaw = pd_["tag"], pd_["cx"], pd_["cy"], pd_["yaw"]
            a = math.radians(yaw)
            ca, sa = math.cos(a), math.sin(a)

            def put2(dx, dy, _cx=cx, _cy=cy, _ca=ca, _sa=sa):
                return (_cx + dx * _ca - dy * _sa, _cy + dx * _sa + dy * _ca)

            OBOX(f"{ROOT}/BagPallet_{tag}", (cx, cy, bp["pt"] / 2.0 - 0.01),
                 (bp["pw"], bp["pd"], bp["pt"]), M["panel"], rotz=yaw)
            for lay in range(int(pd_["layers"])):
                for q in range(4):
                    dx = (0.5 - (q % 2)) * (bp["bw"] * 0.52)
                    dy = (0.5 - (q // 2)) * (bp["bd"] * 1.02)
                    if lay % 2:                      # 교호 적층
                        dx, dy = dy * 0.9, dx * 1.1
                    px, py = put2(dx, dy)
                    OBOX(f"{ROOT}/Bag_{tag}_{lay}_{q}",
                         (px, py, bp["pt"] + bp["bh"] * (lay + 0.5)),
                         (bp["bw"], bp["bd"], bp["bh"]), M["bag"],
                         rotz=yaw + (90.0 if lay % 2 else 0.0)
                         + brng.uniform(-4.0, 4.0))
                    cnt["bag"] += 1

        # ── ③ 이동식 안전 펜스 (북측 1열 — 개구에서 3.85 m 이상 이격) ──
        fc = st["fence"]
        for i, cx, cy, fyaw in fence_placements():   # v5.1 §3 위치·yaw 지터
            w, h = fc["w"], fc["h"]
            grp = sc.build_rot_group(stage, f"{ROOT}/Fence_{i}", (cx, cy),
                                     fyaw)
            for s, sx in enumerate((-w / 2.0, w / 2.0)):
                CYL(f"{grp}/P{s}", (cx + sx, cy, h / 2.0 - 0.01),
                    fc["post_r"], h, M["fence"])
                BOX(f"{grp}/F{s}",
                    (cx + sx, cy, fc["foot_h"] / 2.0 - 0.012),
                    (fc["foot_w"], fc["foot_d"], fc["foot_h"]), M["fence"])
            z_lo, z_hi = 0.22, h - 0.06
            for s, zc in enumerate((z_lo, z_hi)):
                CYL(f"{grp}/R{s}", (cx, cy, zc), fc["rail_r"], w,
                    M["fence"], rotY=90.0)
            nb = int(fc["n_bar"])
            for j in range(nb):
                bx = cx - w / 2.0 + w * (j + 1) / (nb + 1)
                CYL(f"{grp}/B{j}", (bx, cy, (z_lo + z_hi) / 2.0),
                    fc["bar_r"], z_hi - z_lo, M["fence"])
            cnt["fence"] += 1

        # ── ④ 전선 릴 · 공구 상자 ──
        rl = st["reel"]
        for s, sy in enumerate((-1.0, 1.0)):
            CYL(f"{ROOT}/Reel_F{s}",
                (rl["cx"], rl["cy"] + sy * (rl["coil_w"] + rl["flange_t"]) / 2.0,
                 rl["flange_r"]),
                rl["flange_r"], rl["flange_t"], M["panel"], rotX=90.0)
        CYL(f"{ROOT}/Reel_Coil", (rl["cx"], rl["cy"], rl["flange_r"]),
            rl["coil_r"], rl["coil_w"] + 0.01, M["cable"], rotX=90.0)
        for i, tb in enumerate(st["toolboxes"]):
            OBOX(f"{ROOT}/ToolBox_{i}",
                 (tb["cx"], tb["cy"], tb["h"] / 2.0 - 0.01),
                 (tb["w"], tb["d"], tb["h"]), M["tool"], rotz=tb["yaw"])
            cnt["tool"] += 1

        # ── ⑤ 기둥 안전 표어 박판 (무텍스트 색면) ──
        co = PARAMS["colonnade"]
        pc = st["placard"]
        y_face = co["y_c"] + co["size"] / 2.0        # 기둥 북면 (카메라 쪽)
        for i, pl in enumerate(st["placards"]):
            cxp = co["xs"][int(pl["col"])]
            BOX(f"{ROOT}/Placard_{i}", (cxp, y_face + 0.010, pl["z"]),
                (pc["w"], pc["t"], pc["h"]), M["placard"])
            BOX(f"{ROOT}/Placard_{i}_B", (cxp, y_face + 0.035,
                                          pl["z"] + pc["h"] / 2.0
                                          - pc["band_h"] / 2.0),
                (pc["w"], 0.030, pc["band_h"]), M["placard_band"])
            cnt["placard"] += 1

        # ── ⑥ 원경 타워크레인 (가는 박스 조합) ──
        cr = st["crane"]
        cx, cy = cr["cx"], cr["cy"]
        BOX(f"{ROOT}/Crane_Mast",
            (cx, cy, (cr["base_z"] + cr["mast_top"]) / 2.0),
            (cr["mast_w"], cr["mast_w"], cr["mast_top"] - cr["base_z"]),
            M["crane"])
        BOX(f"{ROOT}/Crane_Apex",
            (cx, cy, (cr["mast_top"] - 0.40 + cr["apex_top"]) / 2.0),
            (cr["apex_w"], cr["apex_w"],
             cr["apex_top"] - cr["mast_top"] + 0.40), M["crane"])
        jl = cr["jib_len"] + 0.6
        BOX(f"{ROOT}/Crane_Jib",
            (cx, cy + 0.30 - jl / 2.0, cr["jib_z0"] + cr["jib_h"] / 2.0),
            (cr["jib_w"], jl, cr["jib_h"]), M["crane"])
        cl = cr["cjib_len"] + 0.6
        BOX(f"{ROOT}/Crane_CJib",
            (cx, cy - 0.30 + cl / 2.0, cr["cjib_z0"] + cr["cjib_h"] / 2.0),
            (cr["cjib_w"], cl, cr["cjib_h"]), M["crane"])
        BOX(f"{ROOT}/Crane_CW",
            (cx, cy + cr["cjib_len"] - 1.40,
             cr["cjib_z0"] + 0.90 - cr["cw_h"] / 2.0),
            (cr["cw_w"], cr["cw_d"], cr["cw_h"]), M["crane"])
        hz0 = cr["hook_z0"]
        BOX(f"{ROOT}/Crane_Hook",
            (cx, cy + cr["hook_dy"], hz0 + cr["hook_h"] / 2.0),
            (cr["hook_w"], cr["hook_w"], cr["hook_h"]), M["crane"])
        BOX(f"{ROOT}/Crane_Rope",
            (cx, cy + cr["hook_dy"],
             (hz0 + cr["hook_h"] - 0.05 + cr["jib_z0"] + 0.05) / 2.0),
            (cr["rope_w"], cr["rope_w"],
             cr["jib_z0"] + 0.05 - (hz0 + cr["hook_h"] - 0.05)), M["crane"])
        cnt["crane"] = 7
        return cnt

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    if not cfg["cue_material_break"]:
        # 대비 소거 대조군: 지하층도 슬래브와 동일 재질
        M["lower_wall"] = M["slab"]
        M["lower_floor"] = M["slab"]

    build_ground(M)
    build_upper_walls(M)
    if cfg["hazard_stairs"]:
        build_slab(M)
        build_skirt(M)
        build_lower(M)
        build_rebar(M)
        n_debris = build_debris(M)
        build_cues(M)
    else:
        build_slab(M)
        build_flat_fill(M)
        n_debris = build_debris(M)
    site_cnt = None
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
        site_cnt = build_site_dressing(M)
    build_ground_kit(M)                  # [W2] 지면 요소 — 드레싱 뒤(산포 규약)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # 기하 자기검증 프린트 (렌더 전 수치 확인 — 감독 재검산용)
    op, lw = PARAMS["opening"], PARAMS["lower"]
    drop = PARAMS["deck"]["z_top"] - lw["z_floor"]
    beam = drop / math.tan(math.radians(PARAMS["light"]["noon_sun_elev"]))
    print(f"[기하] 개구 {op['x1'] - op['x0']:.2f}(진행축) × "
          f"{op['y1'] - op['y0']:.2f}(폭) m · 낙차 {drop:.2f} m · "
          f"부스러기 {n_debris}개")
    print(f"[조명] 개구 통과광 수평 이동 {beam:.2f} m → 지하 바닥 착지 "
          f"x {op['x0'] + beam:.2f}..{op['x1'] + beam:.2f} "
          f"(지하 동벽 x={lw['x1']:.1f} 까지 여유 "
          f"{lw['x1'] - (op['x1'] + beam):.2f} m)")

    if site_cnt is not None:
        # 맥락 드레싱 자기검산 — 개구 시선 웨지 여유 · 크레인 시선 통과
        st = PARAMS["site"]
        props = ([(f"철근{b['tag']}", b["cx"], b["cy"]) for b in st["rebar_bundles"]]
                 + [(f"포대{b['tag']}", b["cx"], b["cy"])
                    for b in st["bagpallets"]]
                 + [(f"펜스{i}", fx, fy)
                    for i, fx, fy, _fy in fence_placements()]
                 + [("릴", st["reel"]["cx"], st["reel"]["cy"])]
                 + [(f"공구{i}", t["cx"], t["cy"])
                    for i, t in enumerate(st["toolboxes"])])
        worst = None
        for nm, px, py in props:
            wedge = 0.75 * max(px + 10.0, 0.0) / 10.0     # d10 카메라 최대폭
            margin = abs(py) - wedge
            if worst is None or margin < worst[1]:
                worst = (nm, margin)
        cr = st["crane"]
        w = PARAMS["walls"]
        y_at_wall = cr["cy"] * (w["x_face"] + w["t"] / 2.0 - (-10.0)) \
            / (cr["cx"] + 10.0)
        elev = math.degrees(math.atan2(cr["apex_top"] - 0.9, cr["cx"] + 10.0))
        print(f"[드레싱] 철근봉 {site_cnt['rebar']} · 포대 {site_cnt['bag']} · "
              f"펜스 {site_cnt['fence']}매 · 공구 {site_cnt['tool']} · "
              f"표어 {site_cnt['placard']} · 크레인 {site_cnt['crane']}프림 "
              f"+ 원경 패드")
        print(f"[검산] 개구 시선 웨지 최소 여유 = {worst[0]} {worst[1]:.2f} m "
              f"(>0 이면 개구 가림 0)")
        print(f"[검산] 크레인 방위선이 동벽면(x={w['x_face']:.2f})을 지나는 y = "
              f"{y_at_wall:.2f} (동벽 남단 {w['e_y0']:.2f} 밖이어야 가시) · "
              f"정점 앙각 {elev:.1f}° (프레임 상한 8.0°)")

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneD2 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneD2_{ts}.png")
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
