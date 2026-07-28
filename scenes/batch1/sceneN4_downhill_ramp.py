# -*- coding: utf-8 -*-
"""
sceneN4_downhill_ramp.py — NegObs 인공씬 24호: 내리막 완경사로 (Isaac Sim 4.5)

유형    : N4 hard negative — 보행 가능 완경사(5%) · **GT = 전 픽셀 "낙차 없음"**
사양서  : Docs/nanobanana_batch1_geometry_map.md §A sceneN4_downhill_ramp
룩 레퍼 : look_refs/n4_ramp.jpg (콘크리트 옹벽 사이 폭 4 m 직선로)
공통    : scene_common.py (build_slope / add_box / 드레싱·조명 하네스)

위험 본질(반례): 노면이 시야에서 아래로 사라지고 좌우 옹벽이 수렴하는 구도는
           "노면 끝 = 낙차"라는 오검출을 유발한다. 그러나 실제 기하는 5%(1:20)
           완경사 — 주행·보행 모두 가능하고 낙차는 **어디에도 없다**.
           S1(노변 이탈) 갈래의 반례이자 T21(램프-계단 대비쌍)의 단독 버전.
목표     : 진입 평지(x<0) → 5% 경사 30 m(낙차 1.5) → 평탄 착지 → 원경 지면·수목·
           건물로 지평 폐쇄. 좌우 콘크리트 옹벽(노면 위 1.6 m)이 경사를 추종.

GT 규약  : 낙차 없음(전 픽셀 0). **대지도 노면과 함께 5%로 하강**시켜 옹벽 뒤편에
           단차가 생기지 않게 했다(옹벽은 옹벽이 아니라 경사면 위 자립 방호벽).
           → 프레임 어디에도 실제 수직 낙차가 존재하지 않는다. 미장센 컷도 회랑
           내부에서만 잡아 이 불변식을 깨지 않는다.

────────────────────────────────────────────────────────────────────────────
[v6 맥락 드레싱] 감사 v4 "휑함" 지적 반영 — "여기가 어디인지" 읽히게.
  ① 노면 재질 교정: concrete_floor 텍스처가 난색(황토)이라 r1 렌더에서 흙길로
     읽혔다 → road_tint (0.80,0.86,0.94) 를 걸어 중성 회색 콘크리트로 냉각.
     (텍스처 평균 R:G:B ≈ 1:0.89:0.74 → 완전 중성화 틴트는 (0.74,0.83,1.00).
      실물 콘크리트는 미세 난색이 자연스러워 70% 만 보정 = 잔류비 1:0.96:0.87)
     + 신축이음 횡줄눈(4 m 간격, 폭 0.06, proud 0.001) 으로 '포장 램프' 확정.
  ② 옹벽 상단 가드레일 1선(양측) — build_railing_line, 경사 추종 + 착지 평구간
     연장. 상부 여백(휑한 하늘/벽면)을 채우고 보행 통로임을 확정.
  ③ 가로등 3본 — **-Y(남) 측 잔디에만** 배치. 태양 방위상 그림자가 −Y 로만
     뻗어 노면에 신규 그림자가 **0** 이다(§검산). 암(arm)이 회랑 상공으로 뻗어
     '차도/보도 조명'의 도시 리듬을 준다.
  ④ 옹벽면 안내판 3매(남측 = 직사광 면) + 진입부 안내 사인 1본(한글 텍스처).
  ⑤ 진입 볼라드 2 → 4 (2열) — 보행 진입부 리듬.
  ⑥ 원경 저층 건물 2동(L1·L2) — 기존 원경 건물 F(h12) 앞에 h5.0/4.2 지붕을
     깔아 스카이라인 층위 형성. 회랑 시야각 안(|y| 작음)에 두어 옹벽에 가리지
     않는 x·y 로 검산 배치.
  ⑦ GT 불변: 신규 요소는 전부 지면 위 기립물 — 수직 낙차·개구·단차 신설 없음.
────────────────────────────────────────────────────────────────────────────

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneN4_downhill_ramp.py

자동 캡처 (headless):   NEGOBS_CAPTURE=1 python sceneN4_downhill_ramp.py
스모크 조기종료:        NEGOBS_SMOKE=1  python sceneN4_downhill_ramp.py

좌표계: Z-up, m, 진행축 +X, 경사 시작(크레스트) = x=0.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import batch1_common as bc


# ===========================================================================
# [A] SCENE_CONFIG — 표준 7키.
#     낙차가 없는 씬이므로 hazard_stairs 키는 **특색 요소(경사) 토글**로 재정의.
# ===========================================================================
SCENE_CONFIG = {
    # False → 경사 제거, 전 구간 z=0 평지(옹벽 높이 일정). 기하 토글 유일 예외.
    "hazard_stairs":      True,
    # 옹벽 자체가 방호 — True면 옹벽 상단에 '연속 파이프 1선'(포스트 없음) 추가.
    # [v6] 맥락 드레싱이 켜지면 정식 가드레일(포스트+상·중단 2선)이 같은 y·z 에
    #      이미 서므로 중복(동축 실린더 = Z-파이팅)을 피해 cue 레일은 생략한다.
    #      → cue_scene_dressing=False 인 순수 기하 컷에서만 cue 레일이 나온다.
    "cue_railing":        False,
    "cue_tactile":        False,  # 미관행 — 코드 경로만 예약
    "cue_material_break": True,   # True → 진입 평지 아스팔트 vs 경사 콘크리트
                                  # False → 전 구간 콘크리트(경사 시작 경계 소실)
    "cue_nosing":         False,  # [선택] 계단 없음 — 키만 예약
    "cue_sign":           False,  # [선택] 미구현 — 키만 예약
    "cue_scene_dressing": True,   # 볼라드·원경 수목/생울타리/건물 일괄
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- 경사: run 30 · drop 1.5 → 5.0%(1:20). 크레스트 x=0, 착지 x=30 ---
    ramp=dict(x0=0.0, run=30.0, drop=1.5, y0=-2.0, y1=2.0, thick=0.6),
    # --- 진입 평지(x<0) : 보행 연속성(교훈 9) 시작 구간 ---
    approach=dict(x0=-14.0, x1=0.02, z_top=0.0, thick=0.6),
    # --- 평탄 착지 + 하부 평야 (경사 끝 z=-1.5) ---
    landing=dict(x0=29.98, x1=60.0, z_top=-1.5, thick=0.6),
    # --- 옹벽(방호벽): 노면 위 wall_h, 두께 t, 내면 y=±y_in ---
    wall=dict(y_in=2.0, thick=0.35, wall_h=1.6, depth=3.2, x_end=45.0),
    # --- 대지: 회랑 밖 잔디. **노면과 동일하게 5% 하강**(옹벽 뒤 단차 0) ---
    ground=dict(half_y=60.0, x_w=-60.0, x_e=130.0, thick=1.0),
    # --- 원경(지평 폐쇄) ---
    far=dict(hedge_x=72.0, hedge_h=1.8, hedge_len=30.0,
             hedge_cys=(-30.0, 0.0, 30.0),
             tree_x=80.0, tree_cys=(-16.0, 0.0, 16.0),
             ridge=dict(x0=100.0, x1=118.0, y0=-60.0, y1=60.0, h=6.0)),
    buildings=dict(
        # 정면(+X) 비스타 차단 — 파사드 -X평면. 상면 z = -1.5+12 = 10.5
        # → 카메라(h0.9, x-5)에서 +5.8° (지평선 위) → 하늘 노출 차단 검증됨.
        F=dict(x0=90.0, x1=98.0, y0=-16.0, y1=16.0, h=12.0, floors=4,
               axis="x", facade_x=90.0, face_dir=-1.0, base_z=-1.5),
        # [v6-⑥] 저층 지붕 2동 — 착지부 너머 스카이라인 층위.
        #   옹벽(h1.6, x_end 45)이 만드는 가림 쐐기 때문에 |y| 가 크면 전부 가려
        #   진다: 시선이 y=±2.0 을 넘는 x 에서 옹벽 상단보다 높아야 보인다.
        #   L1(y 4..10, x 62..70): 시선이 y=2 를 x≈30.5 에서 통과 → 그 지점 옹벽
        #     상단 z=0.1, 시선 z=2.45 → 가림 없음(검산 OK).
        #   L2(y −12..−5, x 56..64): y=−2 통과 x≈21.8, 옹벽 상단 0.51,
        #     시선 z=1.82 → 가림 없음.
        #   둘 다 원경 하늘 폐쇄용 F(상단 10.5) 앞에 있어 하늘 틈을 만들지 않음.
        L1=dict(x0=62.0, x1=70.0, y0=4.0, y1=10.0, h=5.0, floors=2,
                axis="x", facade_x=62.0, face_dir=-1.0, base_z=-1.5),
        L2=dict(x0=56.0, x1=64.0, y0=-12.0, y1=-5.0, h=4.2, floors=1,
                axis="x", facade_x=56.0, face_dir=-1.0, base_z=-1.5),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),
    # --- 소품 ---
    # ── 볼라드 [v6-⑤ → v5.1 §2 · ctx2] 램프 진입부(x<0 평지) 2열 ──────────
    #   구(舊): y=±1.55 (간격 3.10 m) · h0.75 · 반사띠/점형블록 없음.
    #   신(新): 규격 h0.90·φ0.12 + 상단 백색 반사띠 + 전면(−X = 보행 접근측)
    #   0.3 m 점형블록. **간격 1.5 m 내외로 재배열**: y=±0.80
    #     · 볼라드↔볼라드 1.60 m  · 볼라드↔옹벽내면(y=±2.0) 1.20 m
    #     둘 다 "1.5 m 내외" 대역이고, 최대 개구 1.60 m < 승용차 폭(1.8 m)
    #     이므로 차량 진입 차단이라는 기능도 성립한다.
    #   ★ 특색 보존 검산(_dressing_report 실측, hFOV60/vFOV36):
    #     −0.9 열 |yaw| = 37.1°(h0.3_d2) / 34.6°(h0.9_d2) / 31.3°(h1.8_d2)
    #       → 전부 프레임 반각 30° 밖. h1.8_d2 는 수평 여유가 1.3° 로 얇지만
    #         el −36.4° 로 **수직 반각 18° 를 크게 벗어나** 이중으로 안전.
    #         h0.9_d2 는 실루엣 반각(0.06/1.43 = 2.4°)을 빼도 32.2° > 30°.
    #     −3.6 열은 d2 에서 |yaw| ≈ 150° = 카메라 후방.
    #     ramp_head(eye −1.0)에서도 |yaw| 79.5° 로 화면 밖.
    #     점형블록 소판은 더 바깥(|yaw| 43.9~52.0°) → 판정 요소 무간섭.
    #     d5·d10 에서만 프레임 안에 들어오며, 소실선(x ≥ 20) 레이캐스트 가림
    #     0건 · 프레임 내 최근접 1.67 m 로 검산 통과.
    #   ★ 중앙 1.6 m 는 완전히 비어 있어 보행축·판정 시선 무간섭.
    bollards=[dict(cx=-0.9, cy=-0.80), dict(cx=-0.9, cy=0.80),
              dict(cx=-3.6, cy=-0.80), dict(cx=-3.6, cy=0.80)],
    bollard=dict(r=0.06, h=0.90, front=(-1.0, 0.0)),

    # --- [v6-②] 옹벽 상단 가드레일 (양측, 노면 경사 추종) ---
    #   지면함수 = 옹벽 상단 z = road_z(x) + wall_h. 착지 평구간(x 30..44.9)은
    #   로컬 평행 연장(포스트 rhythm 2.75 유지, x=30 중복 포스트 회피).
    guard=dict(rail_h=0.95, post_r=0.022, rail_r=0.028, rail_mid_r=0.016,
               rail_mid_drop=0.42, spacing=2.75, x_land_end=44.9),
    # --- [v6-③] 가로등 3본 : -Y(남) 잔디 위. 그림자는 −Y 로만 → 노면 영향 0 ---
    streetlight=dict(pole_h=4.6, pole_r=0.07, arm_len=1.30, arm_r=0.04,
                     head=0.24, y=-2.90),
    streetlights=[4.0, 15.0, 26.0],
    # --- [v6-④] 옹벽 안내판(남측 내면 = 직사광 면). y=−2.0 에서 +Y로 proud ---
    wall_plates=[dict(x=9.0), dict(x=18.0), dict(x=27.0)],
    wall_plate=dict(w=0.55, h=0.38, t=0.03, z_off=1.05,
                    face_w=0.42, face_h=0.26, face_t=0.012),
    # --- [v6-④] 진입 안내 사인 1본 (한글 텍스처, -X 를 바라봄) ---
    #   yaw=180 이면 판 폭(w)이 **Y축**으로 펼쳐진다: y 1.13..1.91
    #   → 옹벽 내면(y=2.0)과 0.09 이격(관통 없음), 노면 안(|y|<2) 유지.
    #   x=−4.2: d2·d5·ramp_head·beauty 는 후방/화각 밖, d10 에서 yaw 14.7° 정면.
    entry_sign=dict(x=-4.2, y=1.52, yaw=180.0, pole_h=2.30, pole_r=0.045,
                    w=0.78, h=0.78),
    # --- [v6-①] 노면 신축이음 횡줄눈 (평판 proud 0.001, 경사 추종) ---
    joints=dict(x0=4.0, x1=44.0, step=4.0, w=0.06, proud=0.001),

    material=dict(
        scale=dict(concrete_floor=0.9, concrete_wall=1.2, grass=4.0),
        grass_tint=(0.55, 0.68, 0.42),
        wall_tint=(0.92, 0.92, 0.90),                 # 밝은 노출 콘크리트
        # [v6-①] 노면 냉각 틴트 — concrete_floor 난색(황토) 제거. 흙길 오독 해소.
        road_tint=(0.80, 0.86, 0.94),
        joint_color=(0.055, 0.055, 0.058),            # 줄눈 (sRGB 암색 규약 내)
        joint_rough=0.92,
        asphalt_color=(0.16, 0.16, 0.17), asphalt_rough=0.85,
        bollard_color=(0.33, 0.33, 0.36), bollard_metallic=0.4,
        bollard_rough=0.5,
        # ─ 볼라드 v5.1 부속: 상단 백색 반사띠(본당 0.08 m²) + 전면 점형블록 ─
        bollard_band_color=(0.88, 0.88, 0.86),
        tactile_color=(0.80, 0.66, 0.14), tactile_rough=0.70,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        parapet_color=(0.90, 0.90, 0.87), parapet_rough=0.6,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        brick_tint=(0.80, 0.80, 0.82),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # [v6] 드레싱 상수색
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        sign_color=(0.045, 0.085, 0.19), sign_rough=0.55,   # 안내판 남색 바탕
        sign_face=(0.58, 0.59, 0.56),                       # 판면(문자대)
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
    # ─── SUN_AZ_OFFSET: 171.5(기본) → **81.5**. 근거:
    #     태양 월드 az ≈ 33.5 + offset = 115° (그림자 az = az−180 = 295°).
    #     그림자 벡터 ≈ (cos295, sin295) = (+0.42, −0.91), 길이 =
    #     wall_h/tan(elev 49.79°) = 1.6/1.181 = 1.355 m
    #     → +Y 옹벽 그림자가 노면을 y=2.0 → y=0.77 까지, 폭 1.23 m 만 덮는다
    #        (노면 폭 4.0 의 31% — "좌우 옹벽 그림자가 노면을 완전히 덮지 않는
    #         방위" 요건 충족). 나머지 69%는 직달광 → 노면 질감·경사 음영 유지.
    #     [v6 신규 요소 그림자 검산] 그림자 변위(높이 h 당) = (+0.3577h, −0.7675h).
    #       · 가로등(y=−2.90, h≤4.60): 지주 그림자 y ≤ −2.90 → **노면(|y|≤2.0)
    #         밖**. 암 끝/헤드(y=−1.60, h=4.45~4.50)도 y = −1.60−3.42 = −5.02 →
    #         노면 밖.  ⇒ 신규 노면 그림자 면적 **0**(소실선 구간 무영향).
    #       · 진입 사인(y=+1.52, 판 상단 z 2.25): 그림자 y = 1.52−1.73 = −0.21,
    #         x −4.2 → −3.4. 그중 y 0.77..1.52 는 이미 옹벽 그림자대 → 순증가는
    #         **진입 평지(x<0)** 위 폭 0.98 의 가는 띠뿐 — 경사 구간 무영향.
    #       · 가드레일(파이프 r0.028, 옹벽 상단): 그림자 폭 ≈0.03 m 의 실선 1~2
    #         본이 기존 옹벽 그림자대(y 0.77..2.0) 안쪽에 겹쳐 떨어짐.
    #       · 옹벽 안내판(proud 0.03): 자기 벽면에만 투영, 노면 도달 없음.
    #     [ ]키(15° step)로 GUI에서 재스윕 가능. ───
    SUN_AZ_OFFSET=81.5,

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
# [C] 경로 상수 + 필요 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN4")

ASSET_ROLES = ["concrete_floor", "concrete_wall", "grass", "brick_red",
               "sign_info", "hdri", "mdl"]


# ===========================================================================
# [C1] 노면 종단 프로파일 — 드레싱 요소의 착지 z 를 노면/대지에 정합시킨다.
#      (대지도 동일 프로파일로 하강하므로 옹벽 밖 잔디 z 도 같은 함수)
# ===========================================================================
def road_z(x, drop):
    rp = PARAMS["ramp"]
    if x <= rp["x0"]:
        return 0.0
    if x >= rp["x0"] + rp["run"]:
        return -drop
    return -drop * (x - rp["x0"]) / rp["run"]


# ===========================================================================
# [C2] 기하 자기검증 리포트 (순수 수학 — SMOKE 조기종료에서 출력)
# ===========================================================================
def _geometry_report():
    rp = PARAMS["ramp"]
    ap = PARAMS["approach"]
    ld = PARAMS["landing"]
    wl = PARAMS["wall"]
    grade = rp["drop"] / rp["run"]
    ang = math.degrees(math.atan2(rp["drop"], rp["run"]))
    print("-" * 64)
    print("[기하] sceneN4 자기검증")
    print(f"  경사: run {rp['run']:.1f} · drop {rp['drop']:.2f} → "
          f"{grade * 100:.1f}% ({ang:.2f}°)  폭 {rp['y1'] - rp['y0']:.1f} m")
    print(f"  보행 연속성: 진입 [{ap['x0']:.1f},{ap['x1']:.2f}] z=0 → "
          f"경사 [0,{rp['run']:.1f}] z 0→{-rp['drop']:.2f} → "
          f"착지 [{ld['x0']:.2f},{ld['x1']:.1f}] z={ld['z_top']:.2f}")
    print(f"    이음 겹침: 진입/경사 {ap['x1'] - rp['x0']:+.3f} m, "
          f"경사/착지 {rp['x0'] + rp['run'] - ld['x0']:+.3f} m "
          f"(쐐기 틈 방지 ≥0.02 · 상면이 서로 교차 발산 → Z-파이팅 없음)")
    # 옹벽 상단(노면 추종) — 경사 세그먼트 근사 없이 build_slope 1개로 처리
    print(f"  옹벽: 내면 y=±{wl['y_in']:.2f} 두께 {wl['thick']:.2f} · "
          f"상단 = 노면 +{wl['wall_h']:.2f} 일정 (build_slope 1개 = 계단식 근사 불요)")
    print(f"    상단 z: x=0 {wl['wall_h']:+.2f} → x={rp['run']:.0f} "
          f"{wl['wall_h'] - rp['drop']:+.2f} · 하단 z {-wl['depth'] + wl['wall_h']:+.2f}"
          f" (노면 아래 {wl['depth'] - wl['wall_h']:.2f} m 매입 → 부유 없음)")
    # 시선 검산: 노면 소실선이 지평선 아래인가 + 지평 폐쇄
    print("  [시선 검산] 카메라 h=0.9 · 노면 소실선 = atan(-grade) = "
          f"{-math.degrees(math.atan(grade)):+.2f}° → 지평선(0°) 아래 OK")
    bd = PARAMS["buildings"]["F"]
    btop = bd["base_z"] + bd["h"]
    for ex in (-2.0, -5.0, -10.0):
        h = 0.9
        a_end = math.degrees(math.atan2(ld["z_top"] - h, ld["x1"] - ex))
        a_bld = math.degrees(math.atan2(btop - h, bd["x0"] - ex))
        print(f"    eye x={ex:6.1f}: 착지끝 {a_end:+.2f}° / 원경건물 상단 "
              f"{a_bld:+.2f}° → 하늘 노출 {'차단 OK' if a_bld > 0 else 'FAIL'}")
    print("  [GT] 전 픽셀 '낙차 없음' — 대지도 노면과 동일 5% 하강, "
          "옹벽 뒤 단차 0, 개구 없음")
    print("-" * 64)


def build_views():
    """카메라 프리셋: grid_views(gy=0.0) + 미장센 4컷(모두 회랑 내부)."""
    views = sc.grid_views(0.0)
    # ramp_head: 크레스트 직전 — 노면이 아래로 사라지는 오검출 구도(특색)
    views["ramp_head"] = dict(eye=[-1.0, 0.0, 0.9], tgt=[12.0, 0.0, -0.5])
    # wall_run: 경사 중간, 편측 옹벽 그림자가 노면 일부를 덮는 구도
    views["wall_run"] = dict(eye=[6.0, -1.2, 0.6], tgt=[26.0, 0.6, -1.2])
    # landing_lookback: 착지에서 되돌아봄 — 오르막으로 연속(보행 가능 증명)
    views["landing_lookback"] = dict(eye=[33.0, 0.0, 0.9], tgt=[16.0, 0.0, 0.1])
    # beauty_overview: 사선 부감(회랑 내부 상공) — 경사 전개 인상
    views["beauty_overview"] = dict(eye=[-6.0, -1.7, 3.0], tgt=[16.0, 0.4, -1.0])
    return views


# ===========================================================================
# [D2] 카메라 검산 (v6 맥락 드레싱) — 순수 수학. SMOKE 에서 출력.
#   Isaac 기본 카메라: focal 18.14756 / horiz aperture 20.955 → hFOV 60.0°,
#   1920×1080 → vFOV = 2·atan(tan30°·9/16) = 36.0°. 반각 30° / 18°.
#   판정: ① 전 뷰에서 신규 프림이 카메라와 근접 충돌(<0.6 m)하지 않는가
#         ② 프레임 안에 들어오는 경우 노면 소실선(중앙 저각)을 가리지 않는가
# ===========================================================================
HFOV_HALF = 30.0
VFOV_HALF = 18.0


def _cam_angles(view, p):
    """(yaw_rel°, elev_rel°, dist, in_frame) — 카메라 광축 기준 정확 변환."""
    ex, ey, ez = view["eye"]
    tx, ty, tz = view["tgt"]
    fx, fy, fz = tx - ex, ty - ey, tz - ez
    yaw = math.atan2(fy, fx)
    pitch = math.atan2(fz, math.hypot(fx, fy))
    dx, dy, dz = p[0] - ex, p[1] - ey, p[2] - ez
    u = dx * math.cos(yaw) + dy * math.sin(yaw)
    v = -dx * math.sin(yaw) + dy * math.cos(yaw)          # 카메라 좌측 +
    u2 = u * math.cos(pitch) + dz * math.sin(pitch)
    w2 = -u * math.sin(pitch) + dz * math.cos(pitch)
    yaw_r = math.degrees(math.atan2(v, u2))
    elev_r = math.degrees(math.atan2(w2, math.hypot(u2, v)))
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
    inf = (u2 > 0.0 and abs(yaw_r) <= HFOV_HALF and abs(elev_r) <= VFOV_HALF)
    return yaw_r, elev_r, dist, inf


def _road_hit(eye, p, drop, t_max=40.0, step=0.02):
    """eye→p 시선을 p 너머(t>1)로 연장해 노면 상면과 만나는 (x,y) 반환.
    노면 = |y| ≤ 2.0, x ∈ [approach.x0, landing.x1], z = road_z(x).
    만나지 않으면 None. (프림이 그 지점의 노면 픽셀을 가린다는 뜻)"""
    ap, ld = PARAMS["approach"], PARAMS["landing"]
    rp = PARAMS["ramp"]
    ex, ey, ez = eye
    dx, dy, dz = p[0] - ex, p[1] - ey, p[2] - ez
    t = 1.0
    prev = None
    while t <= t_max:
        x = ex + dx * t
        y = ey + dy * t
        z = ez + dz * t
        on = (abs(y) <= rp["y1"]) and (ap["x0"] <= x <= ld["x1"])
        cur = (z - road_z(x, drop)) if on else None
        if cur is not None and prev is not None and prev > 0.0 >= cur:
            return (x, y)
        prev = cur
        t += step
    return None


def streetlight_xs():
    """[v5.1 §3] 가로등 x 좌표 ±0.3 m 결정적 지터 — 11 m 등간격 인상 제거.
    y(=−2.90)는 **불변**: 그림자가 −Y 로만 뻗어 노면 기여 0 이라는 조명 검산
    전제와, 암(+Y 1.30)이 회랑 상공에 걸치는 기능 조건을 깨지 않기 위함."""
    return [x + bc.jit_scalar(x, PARAMS["streetlight"]["y"], "slN4",
                              -0.30, 0.30)
            for x in PARAMS["streetlights"]]


def wall_plate_xs():
    """[v5.1 §3] 옹벽 안내판 x ±0.25 m 지터 (9 m 등간격 완화)."""
    return [d["x"] + bc.jit_scalar(d["x"], 0.0, "wpN4", -0.25, 0.25)
            for d in PARAMS["wall_plates"]]


def _dressing_probes(drop):
    """검산 대상점: (이름, (x,y,z)). 신규 드레싱의 대표 극단점만."""
    P = []
    sl = PARAMS["streetlight"]
    for x in streetlight_xs():
        gz = road_z(x, drop)
        P.append((f"가로등x{x:.1f}·헤드", (x + 0.0, sl["y"] + sl["arm_len"],
                                        gz + sl["pole_h"] - 0.15)))
        P.append((f"가로등x{x:.1f}·기부", (x, sl["y"], gz + 0.3)))
    es = PARAMS["entry_sign"]
    P.append(("진입사인·판", (es["x"], es["y"],
                             es["pole_h"] - es["h"] / 2.0 - 0.05)))
    wp = PARAMS["wall_plate"]
    for x in wall_plate_xs():
        P.append((f"옹벽판x{x:.1f}", (x, -PARAMS["wall"]["y_in"] + 0.02,
                                      road_z(x, drop) + wp["z_off"])))
    bo = PARAMS["bollard"]
    for b in PARAMS["bollards"]:
        P.append((f"볼라드({b['cx']:+.1f},{b['cy']:+.1f})",
                  (b["cx"], b["cy"], bo["h"] / 2.0)))
        # 전면 점형블록 소판의 **가장 카메라쪽 모서리**(축방향 원단 × 측방 외단)
        fx, fy = bo["front"]
        P.append((f"점형블록({b['cx']:+.1f},{b['cy']:+.1f})",
                  (b["cx"] + fx * (bo["r"] + 0.30),
                   b["cy"] + fy * (bo["r"] + 0.30)
                   + (0.20 if fx != 0.0 else 0.0)
                   * (1.0 if b["cy"] >= 0.0 else -1.0), 0.004)))
    g = PARAMS["guard"]
    yg = PARAMS["wall"]["y_in"] + PARAMS["wall"]["thick"] / 2.0
    for sgn, tag in ((1.0, "N"), (-1.0, "S")):
        for x in (-14.0, -6.0, -2.0, 0.0, 15.0, 30.0, 40.0):
            P.append((f"가드레일{tag}x{x:g}",
                      (x, sgn * yg,
                       road_z(x, drop) + PARAMS["wall"]["wall_h"] + g["rail_h"])))
    for key in ("L1", "L2"):
        bd = PARAMS["buildings"][key]
        P.append((f"원경{key}·근각",
                  (bd["x0"], bd["y0"] if abs(bd["y0"]) < abs(bd["y1"])
                   else bd["y1"], -drop + bd["h"])))
    return P


def _dressing_report(drop):
    views = build_views()
    probes = _dressing_probes(drop)
    print("-" * 64)
    print("[검산] v6 맥락 드레싱 × 카메라 (hFOV 60° / vFOV 36°)")
    # ① 카메라 근접 충돌
    worst = None
    worst_in = None
    for vn, vw in views.items():
        for nm, p in probes:
            _, _, dist, inf = _cam_angles(vw, p)
            if worst is None or dist < worst[0]:
                worst = (dist, vn, nm)
            if inf and (worst_in is None or dist < worst_in[0]):
                worst_in = (dist, vn, nm)
    print(f"  ① 최근접(전체)   = {worst[0]:.2f} m ({worst[1]} ↔ {worst[2]}) "
          f"— 프레임 밖이면 시각 영향 없음")
    ok = worst_in[0] >= 1.0
    print(f"    최근접(프레임 내) = {worst_in[0]:.2f} m "
          f"({worst_in[1]} ↔ {worst_in[2]}) → "
          f"{'OK(근접 점유 없음)' if ok else 'FAIL(<1.0)'}")
    # ② 특색(노면 소실선) 가림 — **정확 판정**: 프레임 안 프림에 대해 eye→프림
    #    시선을 프림 너머로 연장해 노면(|y|≤2, x −14..60)에 닿는지 레이캐스트.
    #    닿는 지점 x_h 가 소실선 구간(x ≥ 20, 즉 경사 하부~착지 전이)이면 경고.
    #    (프림 대표점 기준 근사 — 실루엣 전체가 아니라 극단점 표본)
    warn = []
    for vn, vw in views.items():
        for nm, p in probes:
            yw, el, dist, inf = _cam_angles(vw, p)
            if not inf:
                continue
            hit = _road_hit(vw["eye"], p, drop)
            if hit is not None and hit[0] >= 20.0:
                warn.append((vn, nm, hit))
    if warn:
        for vn, nm, hit in warn:
            print(f"  ② [경고] {vn}: {nm} → 노면 (x={hit[0]:.1f}, "
                  f"y={hit[1]:+.2f}) 가림 — 소실선 구간(x≥20) 침범")
    else:
        print("  ② 소실선 구간(x≥20) 노면 가림 프림 없음 → OK "
              "(연장 시선 레이캐스트 판정)")
    # ③ 주요 미장센 뷰별 프레임 내 신규 프림 요약
    for vn in ("ramp_head", "wall_run", "beauty_overview",
               "landing_lookback", "preset_h0.9_d5"):
        vw = views.get(vn)
        if vw is None:
            continue
        names = [nm for nm, p in probes if _cam_angles(vw, p)[3]]
        print(f"  ③ {vn:18s} 프레임 내 {len(names):2d}종: "
              f"{', '.join(names[:6])}{' …' if len(names) > 6 else ''}")
    # ④ 기하 여유(관통·부유) 검산
    wl = PARAMS["wall"]
    es = PARAMS["entry_sign"]
    sl = PARAMS["streetlight"]
    g = PARAMS["guard"]
    sy1 = es["y"] + es["w"] / 2.0                   # yaw180 → 판 폭이 Y축
    print(f"  ④ 진입사인 판 y [{es['y'] - es['w'] / 2.0:+.2f}, {sy1:+.2f}] vs "
          f"옹벽 내면 {wl['y_in']:+.2f} → 여유 {wl['y_in'] - sy1:+.3f} m "
          f"{'OK' if sy1 < wl['y_in'] else 'FAIL(관통)'}")
    hy = sl["y"] + sl["arm_len"]
    print(f"    가로등 헤드 y {hy:+.2f} (노면 |y|≤{PARAMS['ramp']['y1']:.2f} 안) "
          f"· 지주 y {sl['y']:+.2f} (옹벽 외면 "
          f"{-(wl['y_in'] + wl['thick']):+.2f} 밖 = 잔디) → "
          f"{'OK' if abs(hy) < PARAMS['ramp']['y1'] and abs(sl['y']) > wl['y_in'] + wl['thick'] else 'FAIL'}")
    ygr = wl["y_in"] + wl["thick"] / 2.0
    print(f"    가드레일 y ±{ygr:.3f} = 옹벽 두께 중앙(±{wl['y_in']:.2f}.."
          f"±{wl['y_in'] + wl['thick']:.2f}) → 천단 착지 OK · 포스트 높이 "
          f"{g['rail_h']:.2f} m")
    print("-" * 64)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. ramp_head / h0.9   — 노면이 아래로 사라지는데 실제로는 5% 완경사인가(특색)
 2. wall_run           — 편측 옹벽 그림자가 노면을 '일부만' 덮는가(태양 az 115°)
 3. 지평 폐쇄          — 경사 끝 너머 하늘 틈 없이 착지·원경 지면/건물로 닫히는가
 4. landing_lookback   — 진입→경사→착지 노면이 끊김 없이 이어지는가(보행 연속성)
 5. GT 불변식          — 프레임 어디에도 수직 낙차/개구/옹벽 뒤 단차가 없는가
 6. 경사 ON vs OFF     — hazard_stairs False 시 전 구간 평지, 옹벽 높이 일정
 7. [v6] 노면 재질     — 콘크리트 회색으로 읽히는가(흙길 오독 해소) · 횡줄눈
 8. [v6] 맥락 판독     — 가드레일·가로등·안내판/사인·볼라드 2열·원경 저층지붕
                         으로 '지하차도 진입 보행 램프'가 읽히는가
 9. [v6] 신규 그림자   — 가로등 그림자가 노면에 전혀 안 떨어지는가(-Y 배치)"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene24")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene24"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # 경사 토글: OFF면 drop=0 (전 구간 평지) — 기하 트랜스폼만 바뀐다.
    DROP = PARAMS["ramp"]["drop"] if cfg["hazard_stairs"] else 0.0

    # -------------------------------------------------------------------
    # 재질
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        # [v6-①] road_tint 로 concrete_floor 의 난색(황토)을 중성 회색으로 냉각
        #        — r1 렌더에서 "흙길"로 읽히던 원인. 기하·스케일은 불변.
        M["road"] = PBR(
            f"{ROOT}/Looks/Road", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"],
            tint=mp["road_tint"])
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
            2.0, tint=mp["brick_tint"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        M["tactile"] = PBR(f"{ROOT}/Looks/Tactile",
                           diffuse_color=mp["tactile_color"],
                           roughness_const=mp["tactile_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
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
        # --- [v6] 드레싱 재질 ---
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=mp["sign_rough"])
        M["sign_face"] = PBR(f"{ROOT}/Looks/SignFace",
                             diffuse_color=mp["sign_face"],
                             roughness_const=mp["sign_rough"])
        # 한글 안내 사인 패널 — uv_mode(메시 st 1:1 정합, build_sign 전용)
        M["sign_panel"] = PBR(f"{ROOT}/Looks/SignPanel",
                              sc.tex_path("sign_info", "diff"), uv_mode=True,
                              roughness_const=0.45)
        M["joint"] = PBR(f"{ROOT}/Looks/Joint", diffuse_color=mp["joint_color"],
                         roughness_const=mp["joint_rough"], specular_level=0.0)
        return M

    # -------------------------------------------------------------------
    # 대지 — 회랑 밖 잔디. 노면과 동일 경사로 하강(옹벽 뒤 단차 0 = GT 불변식)
    #   상부 평지 / 경사면(남·북) / 하부 평야 3구간. 이음은 0.02 겹침 + 상면이
    #   서로 교차 발산하므로 동일평면 Z-파이팅이 생기지 않는다.
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        rp = PARAMS["ramp"]
        wl = PARAMS["wall"]
        y_out = wl["y_in"] + wl["thick"]              # 2.35
        th = g["thick"]
        run = rp["run"]
        # ① 상부 평지 (x_w .. 0.02) 전폭
        BOX(f"{ROOT}/Land_Upper",
            ((g["x_w"] + 0.02) / 2.0, 0.0, -th / 2.0),
            (0.02 - g["x_w"], 2.0 * g["half_y"], th), M["grass"], col=True)
        # ② 경사 대지 (0 .. run) — 회랑(±y_out) 밖 남·북 2매
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            ya = sgn * y_out
            yb = sgn * g["half_y"]
            sc.build_slope(stage, f"{ROOT}/Land_Slope_{tag}", rp["x0"], 0.0,
                           run, DROP, min(ya, yb), max(ya, yb), th, M["grass"],
                           margin=0.0, collider=True)
        # ③ 하부 평야 (run-0.02 .. x_e) 전폭
        BOX(f"{ROOT}/Land_Lower",
            ((run - 0.02 + g["x_e"]) / 2.0, 0.0, -DROP - th / 2.0),
            (g["x_e"] - run + 0.02, 2.0 * g["half_y"], th), M["grass"],
            col=True)

    # -------------------------------------------------------------------
    # 노면 — 진입 평지 + 5% 경사 + 평탄 착지 (연속 보행면)
    # -------------------------------------------------------------------
    def build_road(M):
        rp = PARAMS["ramp"]
        ap = PARAMS["approach"]
        ld = PARAMS["landing"]
        appr_mtl = M["asphalt"] if cfg["cue_material_break"] else M["road"]
        # 진입 평지
        BOX(f"{ROOT}/Road_Approach",
            ((ap["x0"] + ap["x1"]) / 2.0, 0.0, ap["z_top"] - ap["thick"] / 2.0),
            (ap["x1"] - ap["x0"], rp["y1"] - rp["y0"], ap["thick"]),
            appr_mtl, col=True)
        # 경사 본체
        sc.build_slope(stage, f"{ROOT}/Road_Slope", rp["x0"], 0.0, rp["run"],
                       DROP, rp["y0"], rp["y1"], rp["thick"], M["road"],
                       margin=0.0, collider=True)
        # 평탄 착지
        BOX(f"{ROOT}/Road_Landing",
            ((ld["x0"] + ld["x1"]) / 2.0, 0.0, -DROP - ld["thick"] / 2.0),
            (ld["x1"] - ld["x0"], rp["y1"] - rp["y0"], ld["thick"]),
            M["road"], col=True)

    # -------------------------------------------------------------------
    # 옹벽 — 상단이 노면을 그대로 추종(build_slope 1매). 진입·착지 구간은 평벽.
    #   세그먼트 계단식 근사를 쓰지 않으므로 쐐기 틈(교훈 4)이 원천 차단된다.
    # -------------------------------------------------------------------
    def build_walls(M):
        rp = PARAMS["ramp"]
        ap = PARAMS["approach"]
        wl = PARAMS["wall"]
        y_in, t = wl["y_in"], wl["thick"]
        hh, dep = wl["wall_h"], wl["depth"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            ya = sgn * y_in
            yb = sgn * (y_in + t)
            y0, y1 = min(ya, yb), max(ya, yb)
            yc = (y0 + y1) / 2.0
            # 진입 구간 평벽 (상단 z=hh) — 경사벽과 0.02 겹침
            BOX(f"{ROOT}/Wall_Appr_{tag}",
                ((ap["x0"] + ap["x1"]) / 2.0, yc, hh - dep / 2.0),
                (ap["x1"] - ap["x0"], t, dep), M["wall"], col=True)
            # 경사 구간 — 상면이 (0,hh)→(run, hh-DROP)
            sc.build_slope(stage, f"{ROOT}/Wall_Slope_{tag}", rp["x0"], hh,
                           rp["run"], DROP, y0, y1, dep, M["wall"],
                           margin=0.0, collider=True)
            # 착지 구간 평벽 (상단 z=hh-DROP)
            BOX(f"{ROOT}/Wall_Land_{tag}",
                ((rp["run"] - 0.02 + wl["x_end"]) / 2.0, yc,
                 hh - DROP - dep / 2.0),
                (wl["x_end"] - rp["run"] + 0.02, t, dep), M["wall"], col=True)

    # -------------------------------------------------------------------
    # cue — 옹벽 상단 파이프 레일(옵션)
    # -------------------------------------------------------------------
    def build_cues(M):
        if not cfg["cue_railing"]:
            return
        # [v6] 드레싱 가드레일(포스트+2선)과 동일 y·z 이므로 동축 중복 방지.
        if cfg["cue_scene_dressing"]:
            print("[cue] cue_railing 생략 — 드레싱 가드레일이 이미 동일 선상에 "
                  "있음(동축 실린더 Z-파이팅 회피)")
            return
        rp = PARAMS["ramp"]
        wl = PARAMS["wall"]
        yc = wl["y_in"] + wl["thick"] / 2.0
        n = 12
        seg = rp["run"] / n
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            for i in range(n):
                xa = rp["x0"] + i * seg
                zc = wl["wall_h"] - DROP * (i + 0.5) / n + 0.45
                CYL(f"{ROOT}/Rail_{tag}/Seg_{i}", (xa + seg / 2.0, sgn * yc, zc),
                    0.03, seg * 1.02, M["rail"], rotY=90.0)

    # -------------------------------------------------------------------
    # [v6-②] 옹벽 상단 가드레일 — 노면 경사 추종(진입 평지 + 5% 경사)
    #   build_railing_line 의 ground_fn = 옹벽 상단 z = road_z(x) + wall_h.
    #   착지 평구간(x 30..44.9)은 로컬 평행 연장(포스트 리듬 2.75 유지).
    #   포스트 하단이 옹벽 천단에 착지하므로 부유·매몰 없음.
    # -------------------------------------------------------------------
    def build_guard(M):
        rp = PARAMS["ramp"]
        wl = PARAMS["wall"]
        ap = PARAMS["approach"]
        g = PARAMS["guard"]
        yg = wl["y_in"] + wl["thick"] / 2.0            # 옹벽 두께 중앙
        top_of_wall = lambda x: road_z(x, DROP) + wl["wall_h"]   # noqa: E731
        z_land = wl["wall_h"] - DROP                   # 착지 구간 천단 z
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            y = sgn * yg
            sc.build_railing_line(
                stage, f"{ROOT}/Guard_{tag}", y, ap["x0"], rp["x0"],
                rp["run"], DROP, top_of_wall, M["rail"],
                rail_h=g["rail_h"], post_r=g["post_r"], spacing=g["spacing"],
                rail_r=g["rail_r"], rail_mid_r=g["rail_mid_r"],
                rail_mid_drop=g["rail_mid_drop"])
            # 착지 평구간 연장: 상·중단 레일 2본 + 포스트(2.75 리듬, x=30 중복 X)
            xa, xb = rp["x0"] + rp["run"], g["x_land_end"]
            if xb - xa > 0.1:
                for nm, r, zo in (("Top", g["rail_r"], 0.0),
                                  ("Mid", g["rail_mid_r"], g["rail_mid_drop"])):
                    CYL(f"{ROOT}/GuardLand_{tag}/Rail{nm}",
                        ((xa + xb) / 2.0, y, z_land + g["rail_h"] - zo),
                        r, xb - xa, M["rail"], rotY=90.0)
                xp = xa + g["spacing"]
                k = 0
                while xp <= xb - 0.2:
                    CYL(f"{ROOT}/GuardLand_{tag}/Post_{k}",
                        (xp, y, z_land + g["rail_h"] / 2.0),
                        g["post_r"], g["rail_h"], M["rail"])
                    xp += g["spacing"]
                    k += 1

    # -------------------------------------------------------------------
    # [v6-③] 가로등 3본 — **-Y 잔디에만**. 그림자가 −Y 로만 뻗어 노면 영향 0.
    #   지주는 옹벽(천단 = 노면+1.6) 뒤에 서고 암이 회랑 상공으로 뻗는다.
    # -------------------------------------------------------------------
    def build_streetlights(M):
        sl = PARAMS["streetlight"]
        for i, x in enumerate(streetlight_xs()):    # v5.1 §3 등간격 지터
            gz = road_z(x, DROP)                       # 잔디 = 노면 동일 프로파일
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (x, sl["y"], gz + sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["pole"], col=True)
            ay = sl["y"] + sl["arm_len"] / 2.0          # 암은 +Y(회랑쪽)로만
            CYL(f"{base}/Arm", (x, ay, gz + sl["pole_h"] - 0.10),
                sl["arm_r"], sl["arm_len"], M["pole"], rotX=90.0)
            BOX(f"{base}/Head",
                (x, sl["y"] + sl["arm_len"], gz + sl["pole_h"] - 0.15),
                (sl["head"], sl["head"], 0.12), M["lamp"])

    # -------------------------------------------------------------------
    # [v6-④] 옹벽 안내판 3매 — 남측(-Y) 내면 = 직사광 면이라 판독된다.
    #   내면 y=-y_in 에서 +Y 로 proud. 바탕판 + 판면 2박스(scene02 패턴).
    # -------------------------------------------------------------------
    def build_wall_plates(M):
        wl = PARAMS["wall"]
        wp = PARAMS["wall_plate"]
        y_face = -wl["y_in"]                           # 남측 옹벽 내면
        for i, x in enumerate(wall_plate_xs()):     # v5.1 §3 등간격 지터
            zc = road_z(x, DROP) + wp["z_off"]
            yb = y_face + wp["t"] / 2.0                # 바탕판 중심
            BOX(f"{ROOT}/WallPlate_{i}/Back", (x, yb, zc),
                (wp["w"], wp["t"], wp["h"]), M["sign"])
            BOX(f"{ROOT}/WallPlate_{i}/Face",
                (x, y_face + wp["t"] + wp["face_t"] / 2.0, zc),
                (wp["face_w"], wp["face_t"], wp["face_h"]), M["sign_face"])

    # -------------------------------------------------------------------
    # [v6-④] 진입 안내 사인 1본 — 한글 텍스처 패널(sign_info). -X 를 바라봄.
    #   GT 규약상 '낙차 경고'가 아닌 **안내(info)** 사인만 쓴다(오라벨 금지).
    # -------------------------------------------------------------------
    def build_entry_sign(M):
        es = PARAMS["entry_sign"]
        sc.build_sign(stage, f"{ROOT}/EntrySign", es["x"], es["y"], 0.0,
                      es["yaw"], M["sign_panel"], w=es["w"], h=es["h"],
                      pole_h=es["pole_h"], pole_r=es["pole_r"],
                      pole_mtl=M["pole"], back_mtl=M["sign"])

    # -------------------------------------------------------------------
    # [v6-①] 노면 신축이음 횡줄눈 — 경사면을 따라가는 얇은 암색 띠.
    #   상자 두께 0.02, 상면이 국소 노면 +0.001. 줄눈 폭 0.06 구간의 경사 편차는
    #   0.05·0.06 = 0.003 m < 반두께 0.01 → 관통·부유 없음(Z-파이팅 회피).
    # -------------------------------------------------------------------
    def build_joints(M):
        jt = PARAMS["joints"]
        rp = PARAMS["ramp"]
        n = 0
        x = jt["x0"]
        while x <= jt["x1"] + 1e-6:
            zc = road_z(x, DROP) + jt["proud"] - 0.01
            # 폭은 노면보다 0.04 좁게 — 노면 측면(y=±2.0, 옹벽 내면과 접함)에
            # 세 번째 동일평면을 만들지 않는다.
            BOX(f"{ROOT}/RoadJoint_{n}", (x, 0.0, zc),
                (jt["w"], rp["y1"] - rp["y0"] - 0.04, 0.02), M["joint"])
            x += jt["step"]
            n += 1

    # -------------------------------------------------------------------
    # 드레싱 — 볼라드 + 원경(생울타리·수목·능선·건물)로 지평 폐쇄
    # -------------------------------------------------------------------
    def build_dressing(M):
        # 볼라드 [v5.1 §2] — 램프 진입부 2열, 규격 h0.90·간격 1.5 m 내외,
        #   상단 백색 반사띠 + 전면(−X 접근측) 0.3 m 점형블록.
        bo = PARAMS["bollard"]
        for i, bd in enumerate(PARAMS["bollards"]):
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{i}", bd["cx"],
                                 bd["cy"], 0.0, None, M["bollard"],
                                 M["bollard_band"], M["tactile"],
                                 front_dir=bo["front"], radius=bo["r"],
                                 height=bo["h"])
        build_guard(M)
        build_streetlights(M)
        build_wall_plates(M)
        build_entry_sign(M)
        build_joints(M)
        fa = PARAMS["far"]
        for i, cy in enumerate(fa["hedge_cys"]):
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}",
                           fa["hedge_x"], cy - fa["hedge_len"] / 2.0,
                           fa["hedge_x"] + 1.2, cy + fa["hedge_len"] / 2.0,
                           fa["hedge_h"], base_z=-DROP)
        for i, cy in enumerate(fa["tree_cys"]):
            sc.build_tree(stage, f"{ROOT}/FarTree_{i}", fa["tree_x"], cy,
                          -DROP, M["wood"], M["canopy_a"], M["canopy_b"])
        rg = fa["ridge"]
        BOX(f"{ROOT}/FarRidge",
            ((rg["x0"] + rg["x1"]) / 2.0, (rg["y0"] + rg["y1"]) / 2.0,
             -DROP + rg["h"] / 2.0),
            (rg["x1"] - rg["x0"], rg["y1"] - rg["y0"], rg["h"]), M["grass"])
        for key, bd in PARAMS["buildings"].items():
            bd = dict(bd)
            bd["base_z"] = -DROP
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # ── 씬 조립 ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_ground(M)
    build_road(M)
    build_walls(M)
    build_cues(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        _geometry_report()
        if cfg["cue_scene_dressing"]:
            _dressing_report(DROP)
        print(f"[SMOKE] sceneN4 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN4_{ts}.png")
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
