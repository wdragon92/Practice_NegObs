# -*- coding: utf-8 -*-
"""
sceneN5_flush_grating.py - NegObs synthetic scene 25: flush grating and manholes (Isaac Sim 4.5)

Type     : N5 Hard Negative - flush drainage grating + cast iron manholes (GT = no drop on any pixel)
Spec     : Docs/nanobanana_batch1_geometry_map.md §A sceneN5_flush_grating
Look ref : look_refs/n5_grating.jpg
Shared   : scene_common.py (verified API helpers) · scene16_canopy_shadow.py (skeleton)
           scene11_grating_fireescape.py (grating bar pattern · dark metal material)

Hazard (counter-example): **there is no drop anywhere.** A 0.4 m wide long drainage grating
           crossing the concrete walkway diagonally and 2 cast iron manholes are all flush with the
           surface. Between the bars it "looks open", but in reality it is a **recessed dark sump**
           carried by a near-black floor plate at z=−0.25 plus sump side walls under the frame
           rails ([GT-126] — the old z=−0.05 "shallow dark zone" rested on a broken shading proof,
           see the SUN_AZ_OFFSET note), with no real opening (GT drop is 0, so an actual hole is forbidden).
           It is the **contrast pair in the same material family** as T19 (scene11 grating fire
           escape - open, see-through, positive) - forcing "flush is safe, open is a drop" to be
           told apart by geometry rather than by material.
Goal     : assemble a flat concrete walkway (large slab joints) + the oblique grating strip (714 bars)
           + 2 manholes + retaining wall and buildings, and adjudicate by render (render only). GT drop = 0 throughout.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneN5_flush_grating.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python sceneN5_flush_grating.py
Smoke early exit:         NEGOBS_SMOKE=1  python sceneN5_flush_grating.py
Geometry·dressing check:  NEGOBS_GEOCHECK=1 python3 sceneN5_flush_grating.py (no Isaac needed)

Coordinates: Z-up, m, travel axis +X. No drop - the grating passes (3.0, 0.0) and crosses at yaw 62 deg
        (cutting across the screen over the x~0~6 stretch).
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import batch1_common as bc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. This is a hard negative scene, so hazard_* toggles are not a drop but
#     "the scene's characteristic elements (grating, manholes)". Cue keys that do not apply are False + a reason comment.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_flush_grating": True,  # False -> removes the grating and manholes (plain walkway control)
    "cue_railing":        False,  # no drop -> a guard railing is not practice. Key reserved only
    "cue_tactile":        False,  # tactile paving around a grating is not practice. Key reserved only
    "cue_material_break": True,   # walkway slab joint grid. False -> no joints
    "cue_nosing":         False,  # no step -> anti-slip strips are meaningless. Key reserved only
    "cue_sign":           False,  # [optional] not implemented - config key reserved only
    "cue_scene_dressing": True,   # retaining wall · planters · bollards · distant buildings (horizon closure) together
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # ─ Grating (oblique trench drain). Described in the **local coordinates** of rot_group(pivot, yaw):
    #   locally the strip runs along the y=0 axis toward +X, and the group yaw-rotates about the pivot.
    #   The pivot's y must be 0 for the local y=0 axis to be the drain axis [fixed].
    drain=dict(
        pivot=(3.0, 0.0), yaw=62.0, half_len=15.0,
        slot_half=0.200,      # opening (slot) half-width - inner face of the frame
        pave_inner=0.205,     # inner face of the walkway plate (5 mm behind the frame -> avoids coplanarity)
        rail_outer=0.260,     # outer face of the frame rail
        rail_top=0.002, rail_bot=-0.060,
        # ═══ [GT-126] plate_top −0.05 → −0.25 — 섬프 함몰 ═══
        #  구 −0.05 는 "직사광 불도달 → 확실한 암부" 검산에 기대고 있었는데 그 검산이
        #  틀려 있었다(SUN_AZ_OFFSET 주석의 정오표 참조): 바 층 20 mm 만 축방향을
        #  가리므로 직사광이 39 % 듀티로 바닥판에 닿아, 슬롯 사이가 sRGB ~0.29 회백
        #  줄무늬로 렌더됐다(= 감사 HIGH "얹은 격자" 판독의 본체). 실물 트렌치 드레인
        #  채널 깊이 20~30 cm 로 내리면 판정 저시점(그리드 최대 부앙 ~35°)에서 바닥이
        #  시야 밖으로 나가고(가시 한계 = atan(0.20/0.406) ≈ 26° 를 넘는 몇 컷만
        #  원측 바닥 슬리버), 나머지 시선은 섬프 측벽 암면에서 끝난다.
        #  보행면 z=0·그레이팅 상면 bar_top·바 패턴은 전부 불변 — 지면 아래만 판다.
        #  구값 `[repro]`: plate_top=-0.050
        plate_half=0.250, plate_top=-0.250, plate_bot=-0.300,
        # [GT-126] 섬프 측벽 파생 치수: 내측면 = slot_half + sump_inset(동일면 회피,
        #   pave_inner 의 5 mm 후퇴와 같은 관례) · 외측면 = plate_half + sump_inset ·
        #   상단 = rail_bot + sump_bite(레일 몸통에 10 mm 물림 — 광 누설 이음 0) ·
        #   하단 = plate_top − sump_bite(바닥판에 10 mm 물림).
        sump_inset=0.003, sump_bite=0.010,
        bar_t=0.012, bar_h=0.020, bar_top=0.001, bar_ylen=0.460,
        pitch=0.042,          # bar_t 0.012 + slot gap 0.030
        clip_half=0.320,      # joint cut half-width (rail_outer 0.26 + margin)
        pave_half=70.0, pave_thick=0.5,
    ),
    # ─ Manholes (cast iron, flush). 3 proud tiers: frame 0.0012 < lid 0.0020 < boss 0.0030
    manholes=[dict(name="A", cx=6.0, cy=2.2), dict(name="B", cx=9.5, cy=1.2)],
    manhole=dict(r_frame=0.42, r_lid=0.35, r_boss=0.09, h=0.03,
                 proud_frame=0.0012, proud_lid=0.0020, proud_boss=0.0030),
    # ─ Walkway slab joints (lowest tier, proud 0.0006) - cut away inside the drain corridor
    joints=dict(spacing=3.0, width=0.03, proud=0.0006,
                x0=-9.0, x1=15.0, y0=-9.0, y1=9.0),

    # ═══ [W2 ground_kit] P-A verification scene ══════════════════════════════
    #  * This scene is the **A/B proof case for P-A (skin OFF)** in spec §1.4. The elements are all
    #    already there but buried with the look ON - turning off just the skin makes the result visible at once.
    #    Pass line: manhole ROI (px 500–1100 x 350–750) dark pixels 0.02 % -> **>= 4.5 %**,
    #            |∇| p99 0.079 -> **>= 0.30**, approach strong-yellow pixels **>= 1,500 px**.
    #  * One new manhole - **near-field window W1** (ground distance 0.564-2.00 m at d2). It is 4.3 m
    #    clear in x from the oblique drain axis (pivot(3,0) · yaw 62 deg), so it does not interfere with the grating feature.
    ground=dict(
        region=(-12.0, -3.0, 2.0, 3.0),      # walkway corridor (band south of the drain)
        manhole_w1=(-1.15, 0.30),            # [F d2] screen width f·0.648/0.85 = 1,268 px
        gullies=[(-4.0, -2.6), (-9.0, -2.6)],
        # Continuous band in front of the bollard row - §12.5 (2) "small 0.40x0.30 plates -> a continuous 0.60-wide band"
        #   area 0.12 m2 per post x 5 -> 4.2 m2 = 35x. relief="normal", so 1 prim.
        tactile_band=(4.0, -5.70, 11.0, -5.10),
    ),

    # ═══ Context dressing - fixing "urban sidewalk beside a roadway" by render alone ══════════════
    #  * GT unchanged: the kerb is a **raised strip on flat ground** (ground on both sides at z~0) -> not a
    #    real drop. The roadway slab too is a flush plate proud 0.0010 above the paving (z=0).
    #    (The walkway plates Pave_S/N cover +-70 m, so the roadway is laid on top of them.)
    #  * Drain corridor avoidance: the drain axis is pivot(3,0) · yaw 62 deg -> at y=-8.70 it is at
    #    x=-1.63 (corridor half-width 0.294 -> x∈[-1.92,-1.33]). Roadway and kerbs start at x0=0.0,
    #    giving 1.33 m clearance. That the roadway's -X start (x=0) is out of frame in every view is
    #    checked in geocheck() (3).
    road=dict(x0=0.0, x1=51.0, y0=-22.0, y1=-8.70, z_top=0.0010, thick=0.40),
    #   Kerb: y_out = roadway-side face (biting 0.05 into the roadway), y_in = walkway-side face
    curbs=[dict(name="N", y_out=-8.75, y_in=-8.40),      # walkway-side kerb
           dict(name="F", y_out=-21.95, y_in=-22.30)],   # far-side kerb
    curb=dict(x0=0.0, x1=51.0, h=0.16),
    #   Roadway markings (1.6 mm above the roadway surface 0.0010) - centre dashed line + solid edge lines both sides
    road_dash=dict(y=-15.35, x0=0.0, x1=51.0, dash=3.0, gap=6.0,
                   width=0.12, proud=0.0026, thick=0.012),
    road_edges=[dict(name="N", y=-9.15), dict(name="F", y=-21.25)],
    road_edge=dict(x0=0.0, x1=51.0, width=0.12),
    #   Street tree row - in the walkway furnishing zone (between the kerb -8.40 and the bollard row -6.00)
    street_trees=[dict(name="A", cx=2.0), dict(name="B", cx=8.0),
                  dict(name="C", cx=14.0), dict(name="D", cx=20.0)],
    street_tree=dict(cy=-7.30, pit=1.20, pit_proud=0.0020, pit_thick=0.02,
                     trunk_r=0.075, trunk_h=2.40),
    #   Bicycle rack (3 U-hoops) + 1 info sign (freestanding-board class)
    rack=dict(cx=12.5, cy0=4.60, step=0.80, count=3, span=0.70,
              bar_r=0.030, h=0.75),
    entry_sign=dict(x=12.0, y=-5.80, yaw=180.0, w=0.8, h=0.8,
                    pole_h=2.2, pole_r=0.045),
    #   Retaining wall - runs along X at the back of the walkway (site boundary). The nearest camera is
    #   manhole_pair eye(1.5, 5.0), 3.0 m clear.
    #   NB the oblique drain crosses y=8.0-8.45 at x~7.25-7.49, so an **opening (walk-through)**
    #     is placed there - preventing the defect of a wall standing on the drain.
    #     The opening extent is derived automatically from _drain_axis() (gap_clear margin).
    wall=dict(x0=-20.0, x1=34.0, y0=8.00, y1=8.45, h=1.10,
              cap_h=0.06, cap_over=0.04, gap_clear=0.55),
    planters=[dict(name="A", cx=-4.0, cy=-6.30, base_z=0.0, tree=False),
              dict(name="B", cx=16.0, cy=6.20, base_z=0.0, tree=True)],
    planter=dict(size=3.0, curb_h=0.45, curb_t=0.25, cap_over=0.05,
                 cap_h=0.05, grass_h=0.40),
    # ── Bollards [v5.1 §2 · ctx2] ───────────────────────────────────────────
    #   The position (walkway furnishing zone y=-6.00, between the kerb -8.40 and the walking zone) is **kept**.
    #   Old: spacing 3.5 m · h0.75 · no reflective band or dot tactile paving
    #   -> new: spacing 1.40 m (=7.0/5, "about 1.5 m") · h0.90 · dia 0.12 ·
    #      white reflective band at the top · 0.3 m of dot tactile paving in front (walkway side, +Y).
    #   * Feature preserved (the oblique grating): the drain axis passes x=-0.19 at y=-6.00.
    #     The bollard row spans x 4.0-11.0, so the nearest approach is 4.19 m - no interference
    #     with the grating body or the adjudication sight lines (re-confirmed by dressing check (2)).
    bollards=dict(y=-6.0, x0=4.0, x1=11.0, spacing=1.5, r=0.06, h=0.90,
                  front=(0.0, 1.0)),
    buildings=dict(
        # Distant vista blocker (+X horizon): facade on the -X plane. y0 is -4.0, clearing the roadway.
        C=dict(x0=34.0, x1=44.0, y0=-4.0, y1=26.0, h=14.0, floors=4,
               axis="x", facade_x=34.0, face_dir=-1.0),
        # Street wall across the roadway - the cue that settles "this is a sidewalk beside a roadway"
        D=dict(x0=8.0, x1=44.0, y0=-34.0, y1=-24.0, h=12.0, floors=4,
               axis="y", facade_y=-24.0, face_dir=1.0),
        # Closes the roadway vanishing point (+X) + high-rise skyline behind
        E=dict(x0=52.0, x1=64.0, y0=-30.0, y1=-8.0, h=20.0, floors=6,
               axis="x", facade_x=52.0, face_dir=-1.0),
        T=dict(x0=48.0, x1=58.0, y0=2.0, y1=26.0, h=32.0, floors=9,
               axis="x", facade_x=48.0, face_dir=-1.0),
    ),
    window=dict(w=1.3, h=1.7, inset=0.15, col_step=3.0, margin=2.5),

    material=dict(
        scale=dict(plaza_light=1.1, concrete_wall=2.0, grass=1.4,
                   brick_red=2.0),
        # ═══ [GT-126] 광장 판석 순백 대면적 — 실효 알베도 좌표계로 재보정 ═══
        #  실효 알베도 = 텍스처 선형 평균 × 틴트 (Rec.709 luma·IEC 61966-2-1, GT-121 관례).
        #  plaza_light_diff 선형 평균 (0.4686, 0.4620, 0.4449) → luma **0.4622**
        #  `[measured — 이번 세션, _texture_mean 동일 산법 64px]`. 구틴트 luma 0.8877
        #  과의 곱 = **실효 0.4114** — paving 클래스 천장 `alb_max` 0.34 를 21 % 초과.
        #  렌더 실증: p50 0.863 · >0.85 픽셀 68.4 % `[measured — 260806_w3_allview5
        #  pt_noon_manhole_pair ROI x200-1700,y600-1000]` = v5.1 §4 순백 대면적 위반.
        #  구주석 "source mean sRGB 0.714 → ~0.64" 는 sRGB **부호화값** 산술이라
        #  실효(선형) 좌표가 아니었다 — 적힌 값과 도달 값이 달랐다.
        #  분류 확인: `Looks/Pave` 는 규칙 토큰 "pav" → paving(ground MDL)으로 정상
        #  라우팅되므로 밴드 통치는 받는다. 다만 천장 고정(0.34 되-스케일)에 맡기지
        #  않고 화강석 판석 실측 대역 0.25~0.34 의 중앙 **0.30** 을 저작값으로 착지:
        #  틴트 = 구틴트 × (0.30/0.4114) = ×0.7293, 색상비 1 : 0.989 : 0.956 불변
        #  (단일 스칼라 — 색상 보존). 검산: (0.3074, 0.2998, 0.2790) → luma 0.2999
        #  `[computed]`. 룩 OFF 팔에도 같은 값이 흘러 두 팔이 정합한다.
        #  구값 `[repro]`: (0.90, 0.89, 0.86) → 실효 0.4114
        pave_tint=(0.656, 0.649, 0.627),
        joint_color=(0.06, 0.06, 0.06), joint_rough=0.85,
        # Cast iron (grating bars, frame, manholes): sRGB 0.02-0.06 band [convention]
        iron_color=(0.045, 0.045, 0.048), iron_rough=0.55, iron_metallic=0.5,
        lid_color=(0.040, 0.040, 0.045), lid_rough=0.50, lid_metallic=0.6,
        frame_color=(0.050, 0.050, 0.052), frame_rough=0.65, frame_metallic=0.4,
        # Trench sump (floor plate + side walls): a recessed dark zone, not an opening.
        # ═══ [GT-126] 0.040 → 0.013 — 섬프 근흑화 ═══
        #  깊이만으로는 39 % 듀티 직사광 줄무늬가 남는다(SUN_AZ_OFFSET 정오표).
        #  실물 배수 채널 바닥은 슬러지·습윤 퇴적으로 알베도 0.01~0.02 대역이다.
        #  0.013 이면 직사광 아래서도 표시선형 0.7085 × (0.013/0.4114) = 0.0224 →
        #  sRGB **0.164** `[computed — 판정 라운드 판석 p50 0.863 기준 등가 산법]`,
        #  그늘부(바운스만)는 ~0.05 — 구 렌더의 슬롯 p90 0.287 을 절반 이하로 끊고
        #  "배수구 암부" 판독이 재질로도 성립한다. `Looks/Trough` 는 규칙 토큰
        #  "trough" → concrete 승격이라 결은 유지되고 알베도만 보존-하향된다.
        #  구값 `[repro]`: (0.040, 0.040, 0.040)
        trough_color=(0.013, 0.013, 0.013), trough_rough=0.90,
        wall_tint=(0.90, 0.90, 0.88),
        grass_tint=(0.55, 0.68, 0.42),
        # [GT-126 · med 동승] 같은 백색 띠 소견의 나머지 절반 — 옹벽 캡(WallCap)이 이
        #  상수를 쓴다. luma 0.7478 > curb 천장 0.34. 대역 상단 0.32 로(연석은 판정
        #  문맥 단서라 회색 계열 중 최명값 유지), × 0.4287, 색상비 불변.
        #  구값 `[repro]`: (0.75, 0.75, 0.72)
        curb_color=(0.322, 0.322, 0.309), curb_rough=0.6,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        # [GT-126 · med] 파라펫/플린스 백색 띠 p50 0.938 `[measured — manhole_pair ROI
        #  x60-300,y240-262]`. 상수색 = 그 자체가 실효 알베도: luma 0.8614 는 concrete
        #  천장 0.34 의 2.5 배(옥외 노출 콘크리트 실측 0.20~0.30). × 0.3483 으로 대역
        #  중앙 0.30 착지, 색상비 1 : 0.977 : 0.932 불변. 룩 ON 팔은 HEAD 밴드가 이미
        #  0.34 로 되-스케일하므로 이 행은 사실상 룩 OFF 팔 정합 + 천장 고정 해제.
        #  구값 `[repro]`: (0.88, 0.86, 0.82) → luma 0.8614
        parapet_color=(0.306, 0.300, 0.286), parapet_rough=0.6,
        # ─ new for the context dressing ─
        asphalt_color=(0.16, 0.16, 0.17), asphalt_rough=0.90,  # standard aged asphalt
        roadpaint_color=(0.60, 0.59, 0.56), roadpaint_rough=0.70,
        pit_color=(0.055, 0.052, 0.048), pit_rough=0.90,       # tree grate (dark)
        steel_color=(0.62, 0.64, 0.66), steel_metallic=0.85, steel_rough=0.35,
        # ─ Bollard v5.1: stainless body + white reflective band at the top (small area) +
        #   dot tactile paving in front (yellow) ─
        bollard_color=(0.78, 0.80, 0.83), bollard_metallic=0.85,
        bollard_rough=0.34,
        bollard_band_color=(0.88, 0.88, 0.86),
        tactile_color=(0.80, 0.66, 0.14), tactile_rough=0.70,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        sign_color=(0.30, 0.30, 0.32), sign_rough=0.50,
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
    # ─── SUN_AZ_OFFSET = 171.5 (keeps the v3 §A-7 standard - there is a positive reason).
    #     Sun mapping: world sun az ~ 33.5 + 171.5 = 205 deg -> ray travel bearing 25 deg.
    # ═══ [GT-126] 슬롯 차폐 검산 정오표 — 구판 "직사광 불도달" 증명은 틀렸다 ═══
    #  구판은 바 상면(+0.001)→바닥판(−0.050) 전깊이 0.051 을 벽처럼 취급했다:
    #    0.051·cot(49.79°)·|cos(25°−62°)| = 0.0344 > 슬롯 0.030 → "불도달".
    #  그러나 축방향을 가리는 것은 **바 층 두께 bar_h 0.020 뿐**이고 그 아래 0.031 은
    #  자유 낙하 구간이다. 바 층 통과 축이동 = 0.020·0.8457·0.7986 = **0.0135 m
    #  < 슬롯 0.030 m** → 직사광이 바 층을 통과해 바닥에 닿는다. 피치당 개방 듀티
    #  = (0.030−0.0135)/0.042 = **39 %** `[computed]` — "규칙적 회백 사각면"의 정체.
    #  실측 정합: 판석 p50 0.863(sRGB) → 표시선형 0.7085. 동일 조명이므로 직사광
    #  트로프 상면 = 0.040/0.4114 × 0.7085 = 표시선형 0.0689 → sRGB **0.290**
    #  ≒ 감사 슬롯 ROI p90 **0.287** `[measured — 260806_w3_allview5
    #  pt_noon_grating_close x250-450,y565-595]`. 슬롯 사이로 보인 것은 Pave 가
    #  아니라 **직사광을 받은 트로프 상면**(concrete 승격 결이 그대로 노출)이다.
    #  처방: 암부를 거짓 차폐 증명이 아니라 **깊이 + 알베도**에 싣는다 —
    #  plate_top −0.25(채널 20~30 cm 실물 대역) + 근흑 섬프 0.013 + 레일 하단 아래
    #  섬프 측벽 2면. 잔존 직사광 줄무늬는 sRGB ~0.16, 그늘부 ~0.05 로 착지.
    #  geocheck() 의 침투 검산도 같은 산법으로 교체했다(정직한 "관통" 출력).
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
# [C] path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN5")

ASSET_ROLES = ["plaza_light", "concrete_wall", "grass", "brick_red",
               "sign_info", "hdri", "mdl"]


# ===========================================================================
# [D] Joint cutting - a joint strip crossing the oblique drain corridor is split in two
#     (a joint plate spanning the drain would look like a bar floating over the slots)
# ===========================================================================
def _drain_axis():
    """(px, py, cosθ, sinθ, half_len, clip_half) - world drain axis parameters."""
    d = PARAMS["drain"]
    th = math.radians(float(d["yaw"]))
    return (float(d["pivot"][0]), float(d["pivot"][1]),
            math.cos(th), math.sin(th), float(d["half_len"]),
            float(d["clip_half"]))


def _cut_span(a0, a1, center, half, s_at, half_len):
    """The list of segments left after removing [center+-half] from [a0,a1].
    s_at: the drain axis parameter at the cut point (= distance from the centre). If |s_at|>half_len
    the drain does not actually exist there, so no cut is made."""
    if abs(s_at) > half_len or center + half <= a0 or center - half >= a1:
        return [(a0, a1)]
    segs = []
    if center - half > a0:
        segs.append((a0, center - half))
    if center + half < a1:
        segs.append((center + half, a1))
    return segs


def wall_segments():
    """Splits the retaining wall in two where the drain passes through - [(xa,xb), (xa,xb)].
    The x range where the wall band y∈[y0,y1] meets the drain axis, +- (corridor half-width/|sinθ| + margin).
    """
    px, py, ct, st_, hl, wc = _drain_axis()
    wl = PARAMS["wall"]
    d = PARAMS["drain"]
    xs = []
    for yy in (wl["y0"], wl["y1"]):
        t = (yy - py) / st_
        xs.append(px + t * ct)
    half = float(d["rail_outer"]) / abs(st_) + float(wl["gap_clear"])
    ga, gb = min(xs) - half, max(xs) + half
    return [(wl["x0"], ga), (gb, wl["x1"])]


def build_views():
    """Camera presets: grid_views(gy=0.0) + 4 mise-en-scene cuts.
    NB if the two ends of the grating (world (10.04,13.24)/(−4.04,−13.24)) enter the frame
      it reads as 'a drain cut off midway' - every cut was checked to keep them off screen
      (NEGOBS_GEOCHECK=1). The tightest margin is the horizontal 33.5 deg of preset_*_d10 (limit 30 deg)."""
    views = sc.grid_views(0.0)
    # approach: walking toward the grating along the walkway
    views["approach"] = dict(eye=[-6.0, 0.0, 1.6], tgt=[4.0, 0.0, 0.1])
    # grating_close: close and oblique - reads the slot dark zone and whether it is flush [priority 1]
    views["grating_close"] = dict(eye=[1.0, 3.2, 0.7], tgt=[4.2, 0.2, -0.2])
    # manhole_pair: the 2 manholes + the oblique drain (framing of look reference n5)
    views["manhole_pair"] = dict(eye=[1.5, 5.0, 1.3], tgt=[8.0, 0.5, -0.2])
    # beauty_oblique: oblique high angle from +Y - overall layout impression
    views["beauty_oblique"] = dict(eye=[-4.0, 5.5, 2.6], tgt=[5.5, -0.5, -0.3])
    return views


def geocheck():
    """Without Isaac: (1) grating ends in frame (2) joint cutting (3) slot optics check."""
    px, py, ct, st, hl, wc = _drain_axis()
    d = PARAMS["drain"]
    ends = [(px + hl * ct, py + hl * st), (px - hl * ct, py - hl * st)]
    hfov, vfov = 60.0, 36.0
    print("=" * 68)
    print("sceneN5 기하 검산")
    print("  드레인 축: pivot(%.2f, %.2f) yaw %.1f° half_len %.1f"
          % (px, py, PARAMS["drain"]["yaw"], hl))
    print("  끝단 월드좌표: (%.2f, %.2f) / (%.2f, %.2f)"
          % (ends[0][0], ends[0][1], ends[1][0], ends[1][1]))
    nslat = int(2.0 * hl / d["pitch"])
    print("  슬랫 %d매 (pitch %.3f, bar %.3f, 슬롯 %.3f)"
          % (nslat, d["pitch"], d["bar_t"], d["pitch"] - d["bar_t"]))
    # [GT-126] 정오표 반영: 축방향 차폐는 바 층(bar_h)만 담당한다 — 구판은 전깊이를
    #   벽처럼 계산해 "차폐(암부)"를 오출력했다. 지금 검산은 (a) 바 층 통과 축이동
    #   vs 슬롯, (b) 개방 듀티, (c) 섬프 깊이·측벽 시야 한계각을 함께 찍는다.
    e = math.radians(float(PARAMS["light"]["noon_sun_elev"]))
    ray_az = math.radians(33.5 + PARAMS["SUN_AZ_OFFSET"] - 180.0)
    ax_f = abs(math.cos(ray_az - math.radians(d["yaw"]))) / math.tan(e)
    gap = d["pitch"] - d["bar_t"]
    adv_bar = d["bar_h"] * ax_f              # 바 층 안에서의 축이동
    duty = max(0.0, gap - adv_bar) / d["pitch"]
    depth = d["bar_top"] - d["plate_top"]
    sump_w = 2.0 * (d["slot_half"] + d["sump_inset"])
    wall_top = d["rail_bot"] + d["sump_bite"]
    see_lim = math.degrees(math.atan2(-(d["plate_top"] - wall_top), sump_w))
    print("  슬롯 직사광: 바층 축이동 %.4f vs 슬롯 %.3f → %s · 개방 듀티 %.0f%%"
          % (adv_bar, gap,
             "차폐" if adv_bar > gap else "관통(줄무늬 — 근흑 섬프가 받는다)",
             100.0 * duty))
    print("  섬프: 깊이 %.3f m (plate_top %.3f) · 폭 %.3f · 바닥 가시 한계 부앙 %.1f°"
          % (depth, d["plate_top"], sump_w, see_lim))
    worst = (None, 1e9)
    for name, v in sorted(build_views().items()):
        ex, ey, ez = v["eye"]
        vx, vy = v["tgt"][0] - ex, v["tgt"][1] - ey
        vyaw = math.degrees(math.atan2(vy, vx))
        m = 1e9
        for gx, gy in ends:
            dx, dy = gx - ex, gy - ey
            rel = (math.degrees(math.atan2(dy, dx)) - vyaw + 540.0) % 360.0 - 180.0
            m = min(m, abs(rel))
        flag = "IN!!" if m < hfov / 2.0 else "out"
        print("  %-20s 끝단 최소 수평이각 %6.1f°  (한계 %.0f°) %s"
              % (name, m, hfov / 2.0, flag))
        if m < worst[1]:
            worst = (name, m)
    print("  최소 여유 뷰: %s (%.1f°)" % worst)
    # joint cutting
    j = PARAMS["joints"]
    n = int(round((j["y1"] - j["y0"]) / j["spacing"])) + 1
    print("  줄눈 절단 예시 (X평행, y=const):")
    for i in range(n):
        c = j["y0"] + i * j["spacing"]
        if abs(st) < 1e-6:
            continue
        t = (c - py) / st
        xc = px + t * ct
        segs = _cut_span(j["x0"], j["x1"], xc, wc / abs(st), t, hl)
        print("    y=%+6.1f  교차 x=%+7.2f (s=%+6.2f) → 세그 %d개 %s"
              % (c, xc, t, len(segs),
                 ["(%.2f..%.2f)" % s for s in segs]))
    dresscheck()
    print("=" * 68)


# ===========================================================================
# [D2] Context dressing checks - (1) drain corridor intrusion (2) feature sight-line blocking (3) camera burial
#      (4) roadway -X start end in frame
# ===========================================================================
def street_tree_xs():
    """[v5.1 §3] deterministic x +-0.30 m jitter on the street trees - removes the even 6 m spacing look.
    y (furnishing zone −7.30) is unchanged: the band between the kerb (−8.40) and the bollard row (−6.00) is narrow."""
    return [td["cx"] + bc.jit_scalar(td["cx"], PARAMS["street_tree"]["cy"],
                                     "stN5", -0.30, 0.30)
            for td in PARAMS["street_trees"]]


def planter_placements():
    """[v5.1 §3] planter position +-0.15 m jitter."""
    out = []
    for p in PARAMS["planters"]:
        dx, dy = bc.jit_pos(p["cx"], p["cy"], "plN5", amp=0.15)
        out.append((p["name"], p["cx"] + dx, p["cy"] + dy, p))
    return out


def bollard_points():
    """[v5.1 §2] bollard row in the walkway furnishing zone [(x, y), ...] (spacing 1.4 m)."""
    bo = PARAMS["bollards"]
    return bc.bollard_line(bo["x0"], bo["y"], bo["x1"], bo["y"],
                           spacing=bo["spacing"])


def dressing_aabbs():
    """(name, xa, xb, ya, yb, z_top) of the **solid** dressing objects. Flush plates (roadway, markings,
    tree grates) have nothing to do with blocking a sight line, so they are excluded."""
    out = []
    cb = PARAMS["curb"]
    for cd in PARAMS["curbs"]:
        out.append((f"Curb_{cd['name']}", cb["x0"], cb["x1"],
                    min(cd["y_out"], cd["y_in"]), max(cd["y_out"], cd["y_in"]),
                    cb["h"]))
    wl = PARAMS["wall"]
    for tag, (a, b) in zip(("W", "E"), wall_segments()):
        out.append((f"Wall_{tag}", a, b, wl["y0"] - wl["cap_over"],
                    wl["y1"] + wl["cap_over"], wl["h"] + wl["cap_h"]))
    st = PARAMS["street_tree"]
    top = st["trunk_h"] + 0.85 + 0.24                 # build_tree crown upper bound
    for td, tx in zip(PARAMS["street_trees"], street_tree_xs()):
        out.append((f"StreetTree_{td['name']}", tx - 0.77,
                    tx + 0.77, st["cy"] - 0.77, st["cy"] + 0.77, top))
    rk = PARAMS["rack"]
    out.append(("Rack", rk["cx"] - rk["span"] / 2.0 - rk["bar_r"],
                rk["cx"] + rk["span"] / 2.0 + rk["bar_r"],
                rk["cy0"] - rk["bar_r"],
                rk["cy0"] + (rk["count"] - 1) * rk["step"] + rk["bar_r"],
                rk["h"] + rk["bar_r"]))
    es = PARAMS["entry_sign"]
    out.append(("EntrySign", es["x"] - es["w"] / 2.0, es["x"] + es["w"] / 2.0,
                es["y"] - 0.10, es["y"] + 0.10, es["pole_h"]))
    pl = PARAMS["planter"]
    ph = pl["size"] / 2.0
    for name, px, py, p in planter_placements():
        zt = pl["curb_h"] + pl["cap_h"]
        if p.get("tree"):
            zt = pl["grass_h"] + 2.2 + 0.85 + 0.24
        out.append((f"Planter_{name}", px - ph, px + ph,
                    py - ph, py + ph, zt))
    bo = PARAMS["bollards"]
    for i, (bx, by) in enumerate(bollard_points()):
        out.extend(bc.bollard_v51_aabbs(f"Bollard_{i}", bx, by, 0.0,
                                        front_dir=bo["front"],
                                        radius=bo["r"], height=bo["h"]))
    for k, bd in PARAMS["buildings"].items():
        out.append((f"Building_{k}", bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                    bd["h"] + 0.5))
    return out


def _in_frame(eye, tgt, p, hfov=60.0, vfov=36.0):
    """Is point p inside the (eye->tgt) camera frame (Isaac default h60/v36)?"""
    fx, fy, fz = (tgt[0] - eye[0], tgt[1] - eye[1], tgt[2] - eye[2])
    fn = math.sqrt(fx * fx + fy * fy + fz * fz)
    fx, fy, fz = fx / fn, fy / fn, fz / fn
    rx, ry = fy, -fx                                  # f x Z (horizontal right)
    rn = math.hypot(rx, ry)
    if rn < 1e-9:
        return False
    rx, ry = rx / rn, ry / rn
    ux, uy, uz = ry * fz, -rx * fz, rx * fy - ry * fx
    dx, dy, dz = p[0] - eye[0], p[1] - eye[1], p[2] - eye[2]
    fw = dx * fx + dy * fy + dz * fz
    if fw <= 1e-6:
        return False
    ah = math.degrees(math.atan2(abs(dx * rx + dy * ry), fw))
    av = math.degrees(math.atan2(abs(dx * ux + dy * uy + dz * uz), fw))
    return ah < hfov / 2.0 and av < vfov / 2.0


def _seg_hits_box(p0, p1, bmin, bmax):
    tmin, tmax = 0.0, 1.0
    for i in range(3):
        d = p1[i] - p0[i]
        if abs(d) < 1e-12:
            if p0[i] < bmin[i] or p0[i] > bmax[i]:
                return False
            continue
        t1 = (bmin[i] - p0[i]) / d
        t2 = (bmax[i] - p0[i]) / d
        if t1 > t2:
            t1, t2 = t2, t1
        tmin, tmax = max(tmin, t1), min(tmax, t2)
        if tmin > tmax:
            return False
    return True


def dresscheck():
    px, py, ct, st_, hl, wc = _drain_axis()
    d = PARAMS["drain"]
    boxes = dressing_aabbs()
    views = build_views()
    print("-" * 68)
    print("sceneN5 맥락 드레싱 검산")
    # (1) Drain corridor intrusion - corridor half-width = rail_outer, axis |t| <= half_len
    corr = float(d["rail_outer"])
    bad = 0
    for nm, xa, xb, ya, yb, zt in boxes:
        hit = False
        for cx_ in (xa, xb):
            for cy_ in (ya, yb):
                t = (cx_ - px) * ct + (cy_ - py) * st_       # along the axis
                q = -(cx_ - px) * st_ + (cy_ - py) * ct      # distance normal to the axis
                if abs(t) <= hl and abs(q) <= corr:
                    hit = True
        # Box straddling the corridor (corners outside) - reinforced with samples along the axis
        for k in range(121):
            t = -hl + 2.0 * hl * k / 120.0
            ax, ay = px + t * ct, py + t * st_
            if xa <= ax <= xb and ya <= ay <= yb:
                hit = True
        if hit:
            print("  ① ★드레인 회랑 침범★ %s" % nm)
            bad += 1
    rd = PARAMS["road"]
    t_edge = (rd["y1"] - py) / st_
    x_edge = px + t_edge * ct
    print("  ① 회랑 침범 %d건 · 차도 북단(y=%.2f)에서 드레인 x=%.2f "
          "(회랑 x∈[%.2f,%.2f]) vs 차도 시단 x0=%.2f → 이격 %.2f m"
          % (bad, rd["y1"], x_edge, x_edge - corr / abs(st_),
             x_edge + corr / abs(st_), rd["x0"],
             rd["x0"] - (x_edge + corr / abs(st_))))
    # (2) Sight-line blocking of the features (visible drain + manholes)
    #    Visible drain = |t| <= 9.0 (beyond t > 9.06 it is behind the retaining wall - intended concealment,
    #    and a stretch already confirmed out of frame by geocheck (1)).
    pts = []
    for k in range(73):
        t = -9.0 + 18.0 * k / 72.0
        pts.append((px + t * ct, py + t * st_, 0.0))
    for md in PARAMS["manholes"]:
        pts.append((md["cx"], md["cy"], 0.0))
        for a in range(8):
            r = math.radians(45.0 * a)
            pts.append((md["cx"] + 0.35 * math.cos(r),
                        md["cy"] + 0.35 * math.sin(r), 0.0))
    blk = 0
    for vn, v in sorted(views.items()):
        eye = tuple(float(c) for c in v["eye"])
        vis = [p for p in pts if _in_frame(eye, v["tgt"], p)]
        if not vis:
            continue
        for nm, xa, xb, ya, yb, zt in boxes:
            bmin = (xa + 0.01, ya + 0.01, 0.01)
            bmax = (xb - 0.01, yb - 0.01, zt - 0.01)
            if bmax[0] <= bmin[0] or bmax[1] <= bmin[1] or bmax[2] <= bmin[2]:
                continue
            n_hit = sum(1 for p in vis if _seg_hits_box(eye, p, bmin, bmax))
            if n_hit:
                print("  ② %-20s ★특색 시선 차단★ %s (%d/%d 프레임내 샘플)"
                      % (vn, nm, n_hit, len(vis)))
                blk += 1
    print("  ② 특색 시선 차단(프레임 내 샘플 한정): %s"
          % ("0건 합격" if blk == 0 else "%d건 검토" % blk))
    # (3) Camera burial
    m, hit, worst = 0.35, 0, (None, 1e9)
    for vn, v in sorted(views.items()):
        ex_, ey_, ez_ = v["eye"]
        for nm, xa, xb, ya, yb, zt in boxes:
            if (xa - m <= ex_ <= xb + m and ya - m <= ey_ <= yb + m
                    and -m <= ez_ <= zt + m):
                print("  ③ %-20s ★매몰★ %s" % (vn, nm))
                hit += 1
            dd = max(xa - ex_, ex_ - xb, ya - ey_, ey_ - yb, 0.0)
            if dd < worst[1]:
                worst = ("%s vs %s" % (vn, nm), dd)
    print("  ③ 카메라 매몰: %s (최근접 수평 %s = %.2f m)"
          % ("0건 합격" if hit == 0 else "%d건 불합격" % hit,
             worst[0], worst[1]))
    # (4) Roadway -X start end (x = road.x0) in frame - if visible, 'the road starts in mid-air'
    hfov, vfov = 60.0, 36.0
    edge = [(rd["x0"], rd["y0"] + (rd["y1"] - rd["y0"]) * k / 20.0, 0.0)
            for k in range(21)]
    fin, worst4 = 0, (None, -1e9)
    for vn, v in sorted(views.items()):
        ex_, ey_, ez_ = v["eye"]
        vyaw = math.degrees(math.atan2(v["tgt"][1] - ey_, v["tgt"][0] - ex_))
        mrel = 1e9
        for qx, qy, _ in edge:
            rel = (math.degrees(math.atan2(qy - ey_, qx - ex_)) - vyaw
                   + 540.0) % 360.0 - 180.0
            mrel = min(mrel, abs(rel))
        if mrel < hfov / 2.0:
            print("  ④ %-20s ★차도 시단 프레임인★ (최소 이각 %.1f°)" % (vn, mrel))
            fin += 1
        if mrel > worst4[1] or worst4[0] is None:
            pass
        if worst4[0] is None or mrel < worst4[1]:
            worst4 = (vn, mrel)
    print("  ④ 차도 시단 프레임인: %s (최소 여유 %s = %.1f°, 한계 %.0f°)"
          % ("0건 합격" if fin == 0 else "%d건 불합격" % fin,
             worst4[0], worst4[1], hfov / 2.0))
    print("-" * 68)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]  ※ 이 씬은 GT = 전 픽셀 "낙차 없음" (hard negative)
 1. grating_close (PT)  — 슬롯이 **배수구 암부**로 읽히는가 [GT-126]
                           (슬롯 사이 회백 콘크리트 면 = 결함. 직사광 줄무늬는
                            근흑 섬프 위 sRGB ~0.16 이하의 희미한 변조만 허용)
 2. patch/manhole flush — 맨홀·프레임이 노면과 flush(단차·두께 그림자 부재)
 3. approach / h0.3_d2  — 저시점에서 그레이팅 암부가 "틈/낙차"로 혼동되는 강도
 4. 전 컷              — 그레이팅 끝단이 프레임에 들어오지 않는가(검산과 대조)
 5. 기하                — 줄눈이 드레인 위를 가로지르지 않는가, 슬랫 Z파이팅 없음
                           (줄눈0.0006<프레임0.0012<맨홀0.0020<보스0.0030,
                            차도판 0.0010 · 차도 도색 0.0026 는 별도 XY)
 6. 맥락(드레싱)        — 차도(아스팔트+연석+중앙 파선/가장자리 실선)·가로수 열·
                           자전거 거치대·안내 사인·배면 옹벽·차도 건너 가로벽으로
                           "여기는 차도 옆 도시 보도"가 읽히는가
 7. 신규 요소 무간섭    — 드레인·맨홀 시야(approach/grating_close/manhole_pair)를
                           가리지 않는가 (NEGOBS_GEOCHECK=1 의 ②③④ 와 대조)"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return
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
    UsdGeom.Xform.Define(stage, "/World/Scene25")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene25"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def DISC(path, center, r, h, mtl=None, seg=32, col=False):
        """[W2 fix batch F5] n-gon prism - the manhole silhouette. An analytic
        `UsdGeom.Cylinder` is tessellated by Hydra at its own low default, which is
        what renders these covers as an octagon / 12-gon at d2 (defect D4)."""
        return sc.add_disc(stage, path, center, r, h, mtl, seg=seg, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["pave"] = PBR(
            f"{ROOT}/Looks/Pave", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=mp["pave_tint"])
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"],
            tint=mp["wall_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["joint"] = PBR(f"{ROOT}/Looks/Joint",
                         diffuse_color=mp["joint_color"],
                         roughness_const=mp["joint_rough"], metallic=0.0)
        # [W2 fix batch F1] Ground-class decal materials for the kit.
        #   Binding kit crack / stain / wear elements to the scene's joint-sealant
        #   (`paint` class), steel (`metal`) or kerb constants is what rendered them
        #   as flat texture-less ribbons and mats: those classes are excluded from
        #   `_CONST_MDL_CLASSES` **by design** (a constant colour is physically right
        #   for paint and metal), so a *ground* prim bound to one gets no texture at
        #   all. `GKitCrack` / `GKitStain` classify as concrete, so they are promoted
        #   to a real ground texture with the intended albedo preserved.
        M["gk_crack"] = PBR(f"{ROOT}/Looks/GKitCrack",
                            diffuse_color=(0.055, 0.055, 0.056),
                            roughness_const=0.92)
        M["gk_stain"] = PBR(f"{ROOT}/Looks/GKitStain",
                            diffuse_color=(0.20, 0.20, 0.195),
                            roughness_const=0.86)
        # [GT-126] The kit's dirt/gum stains used to share M["trough"] (0.040). The
        #   sump re-materialisation (0.013 near-black) must not ride along onto plaza
        #   surface stains, so they keep the old value under a dedicated constant.
        M["gk_stain_dark"] = PBR(f"{ROOT}/Looks/GKitStainDark",
                                 diffuse_color=(0.040, 0.040, 0.040),
                                 roughness_const=0.90)
        M["iron"] = PBR(f"{ROOT}/Looks/Iron", diffuse_color=mp["iron_color"],
                        metallic=mp["iron_metallic"],
                        roughness_const=mp["iron_rough"], specular_level=0.3)
        M["lid"] = PBR(f"{ROOT}/Looks/Lid", diffuse_color=mp["lid_color"],
                       metallic=mp["lid_metallic"],
                       roughness_const=mp["lid_rough"], specular_level=0.3)
        M["mframe"] = PBR(f"{ROOT}/Looks/MFrame",
                          diffuse_color=mp["frame_color"],
                          metallic=mp["frame_metallic"],
                          roughness_const=mp["frame_rough"])
        M["trough"] = PBR(f"{ROOT}/Looks/Trough",
                          diffuse_color=mp["trough_color"],
                          roughness_const=mp["trough_rough"], metallic=0.0)
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # ─ new for the context dressing ─
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["roadpaint"] = PBR(f"{ROOT}/Looks/RoadPaint",
                             diffuse_color=mp["roadpaint_color"],
                             roughness_const=mp["roadpaint_rough"], metallic=0.0)
        M["pit"] = PBR(f"{ROOT}/Looks/TreePit", diffuse_color=mp["pit_color"],
                       roughness_const=mp["pit_rough"], metallic=0.0)
        M["bollard_body"] = PBR(f"{ROOT}/Looks/BollardBody",
                                diffuse_color=mp["bollard_color"],
                                metallic=mp["bollard_metallic"],
                                roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        # [W2 §12.5 (3)] constant colour -> **wire up the `tactile_yellow` texture**.
        #   With the current constant colour the shading of the statutory 36 dots is 0 on screen, so even with
        #   the look OFF the small plates read only as a "low-saturation smudge". The texture was already
        #   registered but unused `[measured - scene_common.TEX["tactile"]]`.
        # [W2-C merge] supervisor approved: this version (MAIN, render-verified) is adopted and the
        #   duplicate `bc.tactile_mtl` from w2-surgeon is dropped. The two are functionally equivalent (same
        #   tactile_yellow diff/nor · same 0.30 m tile), and only this one was verified by an actual render
        #   `[measured - w2_pilot_ground_v1.md §2, strong-yellow 118 -> 12,149 px]`.
        M["tactile"] = PBR(f"{ROOT}/Looks/Tactile",
                           sc.tex_path("tactile", "diff"),
                           sc.tex_path("tactile", "nor"),
                           None, 0.30,
                           roughness_const=mp["tactile_rough"])
        M["steel"] = PBR(f"{ROOT}/Looks/Steel", diffuse_color=mp["steel_color"],
                         metallic=mp["steel_metallic"],
                         roughness_const=mp["steel_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=mp["sign_rough"])
        # Korean-text info sign panel - uv_mode (1:1 match to the mesh st, build_sign only)
        M["sign_panel"] = PBR(f"{ROOT}/Looks/SignPanel",
                              sc.tex_path("sign_info", "diff"), uv_mode=True,
                              roughness_const=0.45)
        return M

    # -------------------------------------------------------------------
    # Walkway + grating - all assembled axis-aligned in the rot_group(pivot, yaw) local frame
    #   No opening is made (GT drop 0). The walkway plate is split into 2 on either side of the drain
    #   and a **dark floor plate (z=-0.05)** carries the gap between them = a shallow dark zone.
    #   Coplanarity avoidance: the walkway inner faces +-0.205 sit 5 mm behind the frame inner faces +-0.200,
    #   and the floor plate (+-0.250) and frame (+-0.260) only interpenetrate each other and the walkway as solids.
    # -------------------------------------------------------------------
    def build_pave_and_grating(M):
        d = PARAMS["drain"]
        px, py = float(d["pivot"][0]), float(d["pivot"][1])
        grp = sc.build_rot_group(stage, f"{ROOT}/Drain", (px, py),
                                 float(d["yaw"]))
        ph, pt = d["pave_half"], d["pave_thick"]
        x0, x1 = px - ph, px + ph
        inner = d["pave_inner"]
        # 2 walkway plates (south / north of the drain)
        for tag, ya, yb in (("S", -ph, -inner), ("N", inner, ph)):
            # [W2-0 · P-A] register the skin exclusion **before the BOX call** - `add_box` calls
            #   `_skin_wanted` right then and there, so registering afterwards is too late.
            sc.skin_exclude(f"{grp}/Pave_{tag}")
            BOX(f"{grp}/Pave_{tag}",
                ((x0 + x1) / 2.0, (ya + yb) / 2.0, -pt / 2.0),
                (x1 - x0, yb - ya, pt), M["pave"], col=True)
        if not cfg["hazard_flush_grating"]:
            # Control: no drain, the walkway fills across the slot width as well (plain flat ground)
            sc.skin_exclude(f"{grp}/Pave_Fill")
            BOX(f"{grp}/Pave_Fill",
                ((x0 + x1) / 2.0, 0.0, -pt / 2.0 - 0.001),
                (x1 - x0, 2.0 * inner + 0.01, pt), M["pave"], col=True)
            return
        hl = d["half_len"]
        gx0, gx1 = px - hl, px + hl
        gxc = (gx0 + gx1) / 2.0
        # Trench floor plate (recessed dark sump floor - not a real opening) [GT-126]
        BOX(f"{grp}/TroughPlate",
            (gxc, 0.0, (d["plate_top"] + d["plate_bot"]) / 2.0),
            (gx1 - gx0, 2.0 * d["plate_half"], d["plate_top"] - d["plate_bot"]),
            M["trough"])
        # [GT-126] Sump side walls - below the frame rails the slot used to open onto
        #   nothing, so oblique sightlines escaped past rail_bot and low-angle views saw
        #   the sunlit floor at -0.05. Now every slot sightline that misses the floor
        #   terminates on these near-black faces. Tops bite 10 mm into the rail bodies
        #   and bottoms 10 mm into the floor plate (solid interpenetration only - the
        #   coplanarity idiom of this assembly), so there is no light-leak seam. The
        #   inner faces sit 3 mm behind the frame inner faces (same convention as the
        #   5 mm pave setback). Walking surface z, grating top z and the bar pattern
        #   are untouched - the change is entirely below z = rail_bot + sump_bite.
        wy0 = d["slot_half"] + d["sump_inset"]
        wy1 = d["plate_half"] + d["sump_inset"]
        wz1 = d["rail_bot"] + d["sump_bite"]
        wz0 = d["plate_top"] - d["sump_bite"]
        for tag, sgn in (("S", -1.0), ("N", 1.0)):
            BOX(f"{grp}/SumpWall_{tag}",
                (gxc, sgn * (wy0 + wy1) / 2.0, (wz0 + wz1) / 2.0),
                (gx1 - gx0, wy1 - wy0, wz1 - wz0), M["trough"])
        # 2 frame rails (top face proud 0.002 - covers the walkway edge to remove coplanarity)
        rw = d["rail_outer"] - d["slot_half"]
        for tag, sgn in (("S", -1.0), ("N", 1.0)):
            BOX(f"{grp}/Frame_{tag}",
                (gxc, sgn * (d["slot_half"] + rw / 2.0),
                 (d["rail_top"] + d["rail_bot"]) / 2.0),
                (gx1 - gx0, rw, d["rail_top"] - d["rail_bot"]), M["iron"])
        # Bar row (both ends bite into the frame rail volume - bar_ylen > slot width)
        n = int((gx1 - gx0) / d["pitch"])
        cz = d["bar_top"] - d["bar_h"] / 2.0
        for i in range(n):
            bx = gx0 + (i + 0.5) * d["pitch"]
            BOX(f"{grp}/Slat_{i}", (bx, 0.0, cz),
                (d["bar_t"], d["bar_ylen"], d["bar_h"]), M["iron"])
        print(f"[기하] 그레이팅 슬랫 {n}매 · 슬롯폭 "
              f"{d['pitch'] - d['bar_t']:.3f} m · 암부 깊이 "
              f"{d['bar_top'] - d['plate_top']:.3f} m")

    # -------------------------------------------------------------------
    # Joints - cut away inside the drain corridor (world axis-aligned)
    # -------------------------------------------------------------------
    def build_joints(M):
        j = PARAMS["joints"]
        px, py, ct, st, hl, wc = _drain_axis()
        active = cfg["hazard_flush_grating"]
        w, pr = j["width"], j["proud"]
        thk = pr + 0.006
        cz = pr - thk / 2.0
        n = int(round((j["y1"] - j["y0"]) / j["spacing"])) + 1
        for i in range(n):
            yy = j["y0"] + i * j["spacing"]
            if active and abs(st) > 1e-6:
                t = (yy - py) / st
                segs = _cut_span(j["x0"], j["x1"], px + t * ct,
                                 wc / abs(st), t, hl)
            else:
                segs = [(j["x0"], j["x1"])]
            for k, (a, b) in enumerate(segs):
                BOX(f"{ROOT}/JointX_{i}_{k}", ((a + b) / 2.0, yy, cz),
                    (b - a, w, thk), M["joint"])
        m = int(round((j["x1"] - j["x0"]) / j["spacing"])) + 1
        for i in range(m):
            xx = j["x0"] + i * j["spacing"]
            if active and abs(ct) > 1e-6:
                t = (xx - px) / ct
                segs = _cut_span(j["y0"], j["y1"], py + t * st,
                                 wc / abs(ct), t, hl)
            else:
                segs = [(j["y0"], j["y1"])]
            for k, (a, b) in enumerate(segs):
                BOX(f"{ROOT}/JointY_{i}_{k}", (xx, (a + b) / 2.0, cz),
                    (w, b - a, thk), M["joint"])

    # -------------------------------------------------------------------
    # Manholes - 3 concentric tiers (frame / lid / centre boss), all flush. No real opening.
    # -------------------------------------------------------------------
    def build_manholes(M):
        mh = PARAMS["manhole"]
        for md in PARAMS["manholes"]:
            nm = md["name"]
            for tag, r, pr, mtl in (
                    ("Frame", mh["r_frame"], mh["proud_frame"], M["mframe"]),
                    ("Lid", mh["r_lid"], mh["proud_lid"], M["lid"]),
                    ("Boss", mh["r_boss"], mh["proud_boss"], M["lid"])):
                DISC(f"{ROOT}/Manhole_{nm}/{tag}",
                    (md["cx"], md["cy"], pr - mh["h"] / 2.0),
                    r, mh["h"], mtl)

    # -------------------------------------------------------------------
    # [W2] ground_kit - P3 sidewalk_block. A new near-field-window manhole + a tactile paving band
    #   in front of the bollards (§12 registered site "bollard"). This scene has no drop edge, so
    #   GT-E1′/GT-E2 are vacuously true and adjudication falls to prim budget, albedo and B11.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["ground"]
        gp = gk.plan_ground(
            "sidewalk_block", region=g["region"], z=0.0,
            gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=(),                     # hard negative - 0 drop edges
            dists=(2, 5, 10), scene="sceneN5",
            tactile=("bollard",),
            sites=dict(manhole=[tuple(g["manhole_w1"])],
                       gully=[tuple(p) for p in g["gullies"]],
                       tactile=dict(bollard=tuple(g["tactile_band"]))),
            seed=25)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(manhole=M["lid"], gully=M["iron"], gutter=M["mframe"],
                  joint=M["joint"], crack=M["gk_crack"], patch=M["pave"],
                  patch_cut=M["gk_crack"], weed=M["grass"], marking=M["roadpaint"],
                  stain_dirt=M["gk_stain_dark"], stain_gum=M["gk_stain_dark"],
                  trench=M["iron"], trench_frame=M["mframe"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] sceneN5 P3 · 프림 {res['prims']} · "
              f"산포 {res['instances']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # Roadway + kerbs - the top-level context cue that settles "this plane is a sidewalk".
    #   The roadway is a flush plate proud 0.0010 above the walkway plate (z=0); the kerb is the
    #   raised strip between them (z 0-0.16). **Ground on both sides is at z~0, so there is no real drop**
    #   = GT unchanged ("no drop" on every pixel).
    # -------------------------------------------------------------------
    def build_roadway(M):
        rd = PARAMS["road"]
        sc.skin_exclude(f"{ROOT}/Roadway")     # [P-A] preserves the flush roadway markings
        BOX(f"{ROOT}/Roadway",
            ((rd["x0"] + rd["x1"]) / 2.0, (rd["y0"] + rd["y1"]) / 2.0,
             rd["z_top"] - rd["thick"] / 2.0),
            (rd["x1"] - rd["x0"], rd["y1"] - rd["y0"], rd["thick"]),
            M["asphalt"], col=True)
        cb = PARAMS["curb"]
        for cd in PARAMS["curbs"]:
            BOX(f"{ROOT}/Curb_{cd['name']}",
                ((cb["x0"] + cb["x1"]) / 2.0,
                 (cd["y_out"] + cd["y_in"]) / 2.0, cb["h"] / 2.0),
                (cb["x1"] - cb["x0"], abs(cd["y_in"] - cd["y_out"]), cb["h"]),
                M["curb"], col=True)
        # Roadway markings - centre dashed line + solid edge lines both sides
        dh = PARAMS["road_dash"]
        zc = rd["z_top"] + dh["proud"] - dh["thick"] / 2.0
        period = dh["dash"] + dh["gap"]
        n = int((dh["x1"] - dh["x0"]) / period) + 1
        for i in range(n):
            xa = dh["x0"] + i * period
            xb = min(xa + dh["dash"], dh["x1"])
            if xb - xa < 0.2:
                continue
            BOX(f"{ROOT}/RoadDash_{i}", ((xa + xb) / 2.0, dh["y"], zc),
                (xb - xa, dh["width"], dh["thick"]), M["roadpaint"])
        re = PARAMS["road_edge"]
        for ed in PARAMS["road_edges"]:
            BOX(f"{ROOT}/RoadEdge_{ed['name']}",
                ((re["x0"] + re["x1"]) / 2.0, ed["y"], zc),
                (re["x1"] - re["x0"], re["width"], dh["thick"]), M["roadpaint"])

    # -------------------------------------------------------------------
    # Dressing - retaining wall (back of the walkway) + street tree row + bicycle rack + info sign
    #          + planters + bollards + distant buildings (street wall across the roadway, skyline)
    #   NB every new element is placed clear of the view to the grating and manholes - geocheck() (2)
    #     checks eye->feature (visible drain, manholes) segments against AABB penetration in every view.
    # -------------------------------------------------------------------
    def build_dressing(M):
        wl = PARAMS["wall"]
        cy = (wl["y0"] + wl["y1"]) / 2.0
        Ly = wl["y1"] - wl["y0"]
        for tag, (a, b) in zip(("W", "E"), wall_segments()):
            BOX(f"{ROOT}/Wall_{tag}", ((a + b) / 2.0, cy, wl["h"] / 2.0),
                (b - a, Ly, wl["h"]), M["wall"], col=True)
            BOX(f"{ROOT}/WallCap_{tag}",
                ((a + b) / 2.0, cy, wl["h"] + wl["cap_h"] / 2.0),
                (b - a, Ly + 2.0 * wl["cap_over"], wl["cap_h"]), M["curb"])
        pl = PARAMS["planter"]
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for pname, px, py, pdef in planter_placements():
            sc.build_planter(
                stage, f"{ROOT}/Planter_{pname}", px, py,
                pdef["base_z"], M["curb"], M["grass"],
                tree_mtls=(tree_mtls if pdef.get("tree") else None),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"],
                grass_h=pl["grass_h"])
        # Street tree row - tree grates (flush dark plates) + street trees. Furnishing zone y=-7.30
        st = PARAMS["street_tree"]
        for td, tx in zip(PARAMS["street_trees"], street_tree_xs()):
            base = f"{ROOT}/StreetTree_{td['name']}"
            BOX(f"{base}/Pit", (tx, st["cy"],
                                st["pit_proud"] - st["pit_thick"] / 2.0),
                (st["pit"], st["pit"], st["pit_thick"]), M["pit"])
            sc.build_tree(stage, base, tx, st["cy"], 0.0, M["wood"],
                          M["canopy_a"], M["canopy_b"],
                          trunk_r=st["trunk_r"], trunk_h=st["trunk_h"])
        # Bicycle rack - 3 U-hoops (2 vertical + 1 horizontal)
        rk = PARAMS["rack"]
        for i in range(int(rk["count"])):
            cy = rk["cy0"] + i * rk["step"]
            for sgn, tag in ((-1.0, "A"), (1.0, "B")):
                CYL(f"{ROOT}/Rack_{i}/Leg_{tag}",
                    (rk["cx"] + sgn * rk["span"] / 2.0, cy, rk["h"] / 2.0),
                    rk["bar_r"], rk["h"], M["steel"])
            CYL(f"{ROOT}/Rack_{i}/Bar", (rk["cx"], cy, rk["h"]),
                rk["bar_r"], rk["span"], M["steel"], rotY=90.0)
        # 1 info sign - facing -X. Under the GT convention this is information (info), not a 'drop warning'.
        es = PARAMS["entry_sign"]
        sc.build_sign(stage, f"{ROOT}/EntrySign", es["x"], es["y"], 0.0,
                      es["yaw"], M["sign_panel"], w=es["w"], h=es["h"],
                      pole_h=es["pole_h"], pole_r=es["pole_r"],
                      pole_mtl=M["steel"], back_mtl=M["sign"])
        # Bollards [v5.1 §2] - walkway furnishing zone, spacing 1.4 m, reflective band + dot tactile paving (+Y)
        bo = PARAMS["bollards"]
        for i, (bx, by) in enumerate(bollard_points()):
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{i}", bx, by, 0.0,
                                 None, M["bollard_body"], M["bollard_band"],
                                 M["tactile"], front_dir=bo["front"],
                                 radius=bo["r"], height=bo["h"])
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_pave_and_grating(M)
    if cfg["cue_material_break"]:
        build_joints(M)
    if cfg["hazard_flush_grating"]:
        build_manholes(M)
    if cfg["cue_scene_dressing"]:
        build_roadway(M)                 # roadway+kerb = the cue that settles "sidewalk"
        build_dressing(M)
    build_ground_kit(M)                  # [W2] ground elements - placed after the dressing
                                         #   (the scatter is called after the ground_kit elements are created)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneN5 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["beauty_oblique"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN5_{ts}.png")
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
    if os.environ.get("NEGOBS_GEOCHECK", "0") == "1":
        geocheck()                     # geometry check only, without booting Isaac
    else:
        main()
