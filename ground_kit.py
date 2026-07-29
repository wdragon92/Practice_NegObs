# -*- coding: utf-8 -*-
"""ground_kit.py — 지면 요소 프로파일 오케스트레이터 (Isaac Sim 4.5 / USD)

작성 2026-07-29 · 대상: NegObs 33씬 (본편 21 + 배치1 12)
유일 사양: `Docs/briefs/ground_kit_spec_v1.md` **v1.1**

## 이 파일이 무엇인가 (그리고 무엇이 아닌가)

**아니다**: "새 요소 라이브러리". `infra_kit` 의 6빌더(측구·빗물받이·맨홀·램프연석·
노면표시·옹벽상세)는 이미 구현·검산 완료인데 33씬 중 `sceneN4` 1건만 쓴다
`[실측 — grep]`. 여기서 **재구현하지 않는다**. `import infra_kit as ik` 로 흡수한다.

**맞다**: "씬 유형 → 프로파일 → 배치 계획 → USD" 3계층 오케스트레이터 +
사양 §4.3 이 요구한 **신규 소빌더 15종**(전부 기하).

## 왜 필요한가 (측정된 사실 — 사양 §0)

1. 채워야 할 곳은 카메라 앞 **0.56~2.00 m 띠 하나**다 — h0.3 프레임 세로의
   **53.9 %** `[계산 — 사양 §2.2]`. 요소를 x ≥ 0(위험 기하 주변)에 두면 프레임
   상위 8 % 에만 걸린다. `sceneN2` 가 요소 9종을 갖고도 σ_LF 1.36 인 기전이다.
2. `_ground_skin`(룩 레이어)이 flush 지면 요소를 **묻는다**. 스킨 상면
   **+6.5 ~ +16.5 mm** `[실측 — scene_common.py:820-841]` 아래로 맨홀(proud
   2.0 mm)·점형블록(4.0 mm)이 통째로 사라진다. → **P-A: 대상 슬래브 스킨 OFF**
   (`scene_common.skin_exclude` 콜백 주입, 사양 §1.2).
3. ground_kit 산출물 자신이 2차 스킨을 뒤집어쓰는 사고는 경로 토큰 `"gkit"`
   (= `GKIT_PATH_TOKEN` 소문자)이 `_SKIN_DENY` 에 들어가 구조적으로 막힌다.

## 규약 (`infra_kit` 승계, 예외 없음 — 사양 §3.1)

- **Z-up · m · 진행축 +X**(씬별 진행축은 `axis` 인자로 회전).
- **`scene_common` 미 import.** 프리미티브는 `Kit` 주입. `import infra_kit` 는
  허용(역참조 없음). `Kit`·`det_seed`·`det_rng`·`_bay_joints`·
  `kit_from_scene_common`·`dry_kit` 는 **재수출**(재구현 금지).
- **RNG 100 % 결정적** — `hash()` 금지, `zlib.crc32 → random.Random` 만.
- **모든 프림은 `{prefix}` 아래**, `prefix` 는 `{ROOT}/GKit` 고정(§1.2 스킨 방어).
- 각 빌더 docstring 에 **`GT:` 줄** + 개당/미터당 프림 수.
- 치수는 **`GROUND_DIMENSIONS` 원장에만**. 원장에 없는 수치를 기본값으로 넣지 않는다.
- **알베도 하드클램프 ≤ 0.30**(점자블록만 0.55 — 법정 노란색·소면적). 초과는 `ValueError`.
- **금지 API**: `lid=False` 계열(무개구) · 볼라드 신규 배치 · 사람/차량 오브젝트 ·
  계절 특정 산포(04·07 갈변낙엽·C1 눈·C2 낙엽만 씬 정체성 예외).
- **점자블록은 `TACTILE_SITES` 등재 (씬, 지점)에만**. 프로파일 플래그로는 못 켠다.

## 3계층 공개 API

    계층1  GROUND_DIMENSIONS / GROUND_PROFILES / TACTILE_SITES / EXPECTED_FP
           GROUND_INVARIANTS / GT_DELTA / EDGE_K / GRAZE_ROW_SEP ...
    계층2  plan_ground(...) -> GroundPlan      (순수 계산, USD 미접촉)
           frame_budget(plan, ...) -> dict     (렌더 없이 B1~B12 판정)
    계층3  apply_ground(kit, prefix, plan, mtls, *, skin_exclude=None, scatter=None)

씬 통합은 2줄이다:

    gp = gk.plan_ground("alley_concrete", region=(-12.0, -0.9, 0.0, 0.9), z=0.0,
                        edges=[("stair_top", 0.0)], scene="scene15",
                        overrides=PARAMS.get("ground"))
    gk.apply_ground(gk.kit_from_scene_common(sc, stage), f"{ROOT}/GKit", gp, M,
                    skin_exclude=sc.skin_exclude, scatter=sc.scatter_debris)

**좌표의 진실 원천(§7.4)**: 아래 `SCENE_PLANS` 는 **자기검산 픽스처**이지
통합 코드의 좌표 원천이 아니다. 통합부는 씬 `PARAMS`/`build_views()` 에서 읽는다.

Isaac 없이 전 33씬 계획 검산: `python3 ground_kit.py`
"""

from __future__ import annotations

import math
import sys

import infra_kit as ik

# ── infra_kit 재수출 (사양 §3.1 "재구현 금지, 재수출") ─────────────────────
Kit = ik.Kit
det_seed = ik.det_seed
det_rng = ik.det_rng
_bay_joints = ik._bay_joints
kit_from_scene_common = ik.kit_from_scene_common
dry_kit = ik.dry_kit
TACTILE_YELLOW = ik.TACTILE_YELLOW

__all__ = [
    # 재수출
    "Kit", "kit_from_scene_common", "dry_kit", "det_seed", "det_rng",
    "TACTILE_YELLOW",
    # 계층 1
    "GROUND_DIMENSIONS", "GROUND_PROFILES", "TACTILE_SITES", "EXPECTED_FP",
    "GROUND_INVARIANTS", "SCENE_PLANS",
    "GROUND_PROUD_MIN", "GROUND_PROUD_FLOOR", "GT_DELTA", "EDGE_STANDOFF",
    "EDGE_K", "GRAZE_ROW_SEP", "GRAZE_ROW_SEP_WORK", "GRAZE_ROW_SEP_1080",
    "GRAZE_FOOTPRINT_WORK", "GRAZE_FOOTPRINT_1080", "GRAZE_WORK_H",
    "ROWS_1080_PER_WORK", "to_work_rows", "to_1080_rows", "graze_row_sep_1080",
    "GKIT_PATH_TOKEN", "ALBEDO_CAP",
    "TACTILE_ALBEDO_CAP", "CAM_F", "CAM_W", "CAM_H",
    # 계층 2·3
    "plan_ground", "frame_budget", "apply_ground",
    "region_from_params", "edges_from_params",
    # 신규 소빌더 15종
    "build_joint_grid", "build_slab_joints", "build_patch_field",
    "build_crack_lines", "build_trench_drain", "build_gutter_U",
    "build_groove_band", "build_membrane", "build_stain_field",
    "build_footprints", "build_wear_lane", "build_edge_litter",
    "build_edge_break", "build_deck_planks", "build_silt_band",
]


# ===========================================================================
# [0] 상수 — 전부 사양 §1.3·§6·§7 에서 온다. 여기 없는 수치를 기본값에 넣지 않는다.
# ===========================================================================
GROUND_PROUD_MIN = 0.0006      # z-fighting 회피 실효 하한 [실측 — N5 줄눈]
GROUND_PROUD_FLOOR = 0.018     # P-B 폴백 전용(평상시 미사용) [계산 — 16.5+1.5]
GT_DELTA = 0.020               # 전 요소 |Δz| 상한 [실측 — minor-step 0.10 의 1/5]
EDGE_STANDOFF = 0.80           # z_e=GT_DELTA 요소의 에지 전방 금지대 [m]
EDGE_K = 40.0                  # GT-E1′ 필요이격 = EDGE_K·z_e  [계산 — 1.20·10/0.3]
GKIT_PATH_TOKEN = "GKit"       # 전 프림이 이 경로 아래 (§1.2 스킨 방어)
ALBEDO_CAP = 0.30              # 규약 하드클램프
TACTILE_ALBEDO_CAP = 0.55      # 점자블록 예외(법정 노란색·소면적) — §12.5 ④

# 카메라 상수 (하드코드 — 사양 §2.1. 검증 3건: N5 줄눈 −6 px · N1 그림자 4/10 px
#              · scene18 지평선 행비)
CAM_W, CAM_H = 1920, 1080
CAM_HFOV_DEG = 60.0
CAM_F = (CAM_W / 2.0) / math.tan(math.radians(CAM_HFOV_DEG / 2.0))   # 1662.769
CAM_PITCH_DEG = -10.0
CAM_VFOV_DEG = 2.0 * math.degrees(math.atan((CAM_H / 2.0) / CAM_F))  # 35.98
NEAR_W1 = (0.564, 2.00)        # 근경 창 W1 — 프레임 세로 53.9 %
NEAR_W2 = (2.00, 3.00)         # 2순위 창 (+7.6 %p)
GRAZE_E_BAND = (0.7, 2.2)      # GRAZE v2 E 대역 = 지면거리 [0.7d, 2.2d]

# ═══ 행 단위 규약 (v1.2 — 540 vs 1080 혼용 해소, 레드팀 G-1) ═══════════════
#  **모든 행 수치는 접미사로 축을 명시한다. 접미사 없는 행 상수를 새로 만들지 말 것.**
#
#  · `_WORK`  = GRAZE 검사기 작업본 행 (`regression_check.GRAZE_LONG = 960`
#               → 1920×1080 이 960×540 으로 축소된다). GRAZE 상수
#               `GRAZE_HW 3 · GRAZE_SMOOTH 3 · GRAZE_SLACK 2` 는 **전부 이 축**이고,
#               GRAZE JSON 의 `gz_row`·대역 표기도 이 축이다.
#  · `_1080`  = `cam_row()` 가 돌려주는 원본 프레임 행. 사양 §2.1 Appendix B
#               (`row(2.0)=497.35`) 와 워크드 예제 C-1′ 도 이 축이다.
#
#  v1.1 의 결함: `GRAZE_ROW_SEP = 16` 은 **_WORK 축에서 유도**됐는데
#  (`(HW+SMOOTH+SLACK)×2 = 16`) `cam_row`(_1080) 결과와 직접 비교됐다
#  → 실제 집행 강도가 유도값의 **절반**(8 _WORK 행 = footprint 반경)이었다.
GRAZE_WORK_LONG = 960                                  # = regression_check.GRAZE_LONG
GRAZE_WORK_H = CAM_H * GRAZE_WORK_LONG // CAM_W        # 540
ROWS_1080_PER_WORK = CAM_H / float(GRAZE_WORK_H)       # 2.0
GRAZE_FOOTPRINT_WORK = 8       # 단차응답 반경 = HW 3 + SMOOTH 3 + SLACK 2  [@540]
GRAZE_ROW_SEP_WORK = 2 * GRAZE_FOOTPRINT_WORK          # 16 — 두 응답 완전분리 [@540]
GRAZE_FOOTPRINT_1080 = GRAZE_FOOTPRINT_WORK * ROWS_1080_PER_WORK   # 16.0
GRAZE_ROW_SEP_1080 = GRAZE_ROW_SEP_WORK * ROWS_1080_PER_WORK       # 32.0
# 하위호환 별칭 — 의미는 위 이름이 정본이다.
GRAZE_ROW_SEP = GRAZE_ROW_SEP_1080      # [@1080]
GRAZE_FOOTPRINT = GRAZE_FOOTPRINT_WORK  # [@540] (EXPECTED_FP 확장폭)


# ===========================================================================
# [1] 치수 원장 — `infra_kit.INFRA_DIMENSIONS` 와 동일 3튜플 형식
#     (값, "확인|추정", 출처). 값을 바꾸려면 **먼저 출처를 갱신**하라.
#     + (v1.1) "unit_cell" — T1 MDL 유닛 지터의 주기·원점 역방향 계약(§4.5)
# ===========================================================================
GROUND_DIMENSIONS = {
    # ── 포장 모듈 ────────────────────────────────────────────────────────
    "module_granite_slab":  (0.600, "확인", "KCS 34 6-5-1 / scene14 실측 600"),
    "module_sidewalk_block": (0.300, "확인", "보도블록 300 그리드 [ZZ_synthesis §9.3]"),
    "module_interlock_l":   (0.200, "확인", "인터로킹 200×100 [규격]"),
    "module_interlock_w":   (0.100, "확인", "동"),
    "module_deck_plank":    (0.145, "확인", "KCS 34 5-2-1 2.3.1 — 데크 판재 폭"),
    "deck_plank_gap":       (0.005, "추정", "업계 4~5 mm 이격 [추정]"),
    "deck_butt_len":        (1.25, "추정", "마구리 엇갈림 1.2~1.3 m 의 중앙 [추정]"),
    # ── 줄눈 (전부 음각. 값은 사양 §1.3 proud/recess 원장) ────────────────
    "joint_slab_w":         (0.007, "시방", "KCS 34 6-5-1 3.1.11 — 판석 줄눈 5~9 mm 중앙"),
    "joint_slab_recess":    (-0.0015, "시방", "동 3.1.14 — 음각 1~2 mm"),
    "joint_contraction_w":  (0.003, "시방", "KCS 34 6-3 3.3.3⑸ — 수축줄눈 폭 3 mm"),
    "joint_contraction_recess": (-0.003, "시방", "동 — 음각 3 mm"),
    "joint_expansion_w":    (0.025, "시방", "동 ⑷ — 신축줄눈 20~30 mm 중앙"),
    "joint_expansion_recess": (-0.0025, "시방", "동 — 음각 2.5 mm"),
    "joint_interlock_w":    (0.0035, "시방", "KCS 34 6-4-1 3.1.4 — 2~5 mm 중앙"),
    "joint_interlock_recess": (-0.002, "시방", "동 — 음각 2 mm"),
    "step_contraction_conc": (3.00, "시방", "콘크리트 포장 시공줄눈 3 m [통계 B 92 %]"),
    "step_contraction_plaza": (1.80, "계산", "판석 셀 0.600 의 3배 — §4.5 U2"),
    "step_expansion_plaza": (6.00, "시방", "광장 신축줄눈 6 m (셀 0.600 의 10배)"),
    # ★ U2 정합 정정: 시방 원문은 "20 m" 지만 판석 셀 0.600 의 정수배가 아니다
    #    (33.33배) → 이중 격자. 33배 = 19.80 m 로 내린다(규정은 "이하"이므로 만족).
    "step_expansion_ghat":  (19.80, "계산", "KCS 34 6-3 3.3.3⑻ 20 m 이하 "
                                            "+ 판석 셀 0.600 의 33배 (§4.5 U2)"),
    # ── 보수 패치·균열 ───────────────────────────────────────────────────
    "patch_area_mean":      (0.63, "통계", "건당 0.61~0.69 ㎡ 표본 중앙"),
    "patch_proud":          (0.002, "실측", "sceneN2 PARAMS 계승"),
    "patch_cutline_proud":  (0.0012, "실측", "동"),
    "crack_w":              (0.012, "통계", "사진표본 3~15 mm 중앙"),
    "crack_recess":         (-0.006, "통계", "동 음각 3~10 mm 중앙"),
    "crack_seg":            (0.60, "추정", "폴리라인 세그 길이 [추정]"),
    # ── 트렌치·측구 ──────────────────────────────────────────────────────
    "trench_w":             (0.30, "통계-산업", "진입부 우수차단 트렌치 표준 300"),
    "trench_frame_w":       (0.040, "추정", "틀 립 폭 [추정] — 측구 줄눈 8 mm 준용 아님"),
    "trench_seat":          (0.002, "실측", "infra_kit.build_gully(seat=0.002) 계승"),
    "gutter_U_w":           (0.25, "추정", "골목 덮개식 U형 측구 표본 관측 [추정]"),
    "gutter_U_cover_len":   (2.00, "추정", "덮개 1매 길이 [추정]"),
    # ── 오염·마모 ────────────────────────────────────────────────────────
    "stain_proud":          (0.0006, "추정", "z-fighting 회피 최소값 = GROUND_PROUD_MIN"),
    "stain_area_mean":      (0.35, "추정", "데칼 1매 평균 면적 [추정]"),
    "wear_lane_w":          (0.90, "통계", "등산로 답압 마모 띠 6/6 표본"),
    "wear_albedo_gain":     (0.85, "통계", "동 — 노면 대비 ×0.85"),
    "edge_litter_w":        (0.25, "통계", "가장자리 유기물 띠 폭"),
    "edge_break_w":         (0.20, "실측", "재질 경계 전이대 0.15~0.25 중앙 (scene04·10)"),
    "silt_band_w":          (0.60, "추정", "침수 실트·물때 띠 [추정]"),
    # ── 도막 방수 (P6) ───────────────────────────────────────────────────
    "membrane_seam_pitch":  (1.00, "시방", "우레탄 도막 롤 이음 0.9~1.1 m 중앙"),
    "membrane_albedo":      (0.19, "결재", "감독 M2 — 0.16~0.22 승인, 중앙값"),
    "membrane_proud":       (0.0006, "추정", "도막 두께(시각) [추정]"),
    # ── 논슬립 홈파기 (T1 1순위, ground_kit 폴백) ────────────────────────
    "groove_pitch":         (0.12, "법령", "주차장법 시행규칙 §6①5마 — 미끄럼방지 홈"),
    "groove_shade":         (0.72, "추정", "명도 ×0.72 [추정]"),
    # ── 잡초 (식생 — GT-E5 램프 대상) ────────────────────────────────────
    "weed_h_max":           (0.12, "추정", "밟히면 눕는 종. 상한 [추정]"),
    # ── 산포 노출 (GT-E5 램프 대상) ──────────────────────────────────────
    "scatter_expose_max":   (0.06, "통계", "등산로 6/6 — φ≤0.12 반매몰 노출 ≤0.06"),
    # ── 점자블록 (법정) ──────────────────────────────────────────────────
    "tactile_tile":         (0.300, "법령", "교통약자법 시행규칙 별표1 2호 차목"),
    "tactile_band_depth":   (0.600, "시방", "국도 실무요령 7.5 — 점형 60 cm 표준(2줄)"),
    "tactile_setback":      (0.300, "법령", "계단 첫 단 0.3 m 전 / 볼라드 전면 0.3 m"),
    "tactile_dot_h":        (0.006, "법령", "점형 돌기 6±1 mm"),
    "tactile_bar_h":        (0.005, "법령", "선형 돌기 5±1 mm"),

    # ── (v1.1) 역방향 계약 — T1 MDL 유닛 지터 원장 (§4.5) ────────────────
    #    profile -> (cell_m, (ox, oy), 출처). cell_m=None 이면 무모듈(지터 금지 — U4)
    "unit_cell": {
        "plaza_granite":      (0.600, (0.0, 0.0), "판석 모듈 600 [규격]"),
        "plaza_water":        (0.600, (0.0, 0.0), "판석 모듈 600 [규격] — 09 동일"),
        "sidewalk_block":     (0.300, (0.0, 0.0), "보도블록 300 그리드 [법령 ZZ §9.3]"),
        "street_asphalt":     (None, None, "무모듈 — 지터 비적용"),
        "alley_concrete":     (3.000, (0.0, 0.0), "시공줄눈 step_x 3.0 [시방]"),
        "roof_membrane":      (None, None, "도막 — 격자 없음(§5.6 줄눈 금지)"),
        "ramp_parking":       (None, None, "무모듈 — 홈파기는 T1 스트라이프"),
        "ramp_road":          (None, None, "무모듈 아스팔트"),
        "bridge_deck":        (None, None, "무모듈 — 지간 이음만"),
        "deck_timber":        (0.145, (0.0, 0.0), "판재 폭 0.145 [시방 KCS 34 5-2-1]"),
        "trail_soil":         (None, None, "무모듈 마사토"),
        "courtyard_dg":       (None, None, "무모듈 마사토"),
        "levee_paved":        (0.200, (0.0, 0.0), "인터로킹 200×100 [규격]"),
        "yard_industrial":    (None, None, "무모듈 — 야드 줄눈은 6.0×4.5 대역"),
        "slab_construction":  (None, None, "무모듈 타설 슬래브"),
        "platform_indoor":    (0.300, (0.0, 0.0), "실내 바닥타일 300 [추정]"),
        "verge_rural":        (None, None, "무모듈 — 복개 슬래브 줄눈만"),
        "deck_trail_hybrid":  (0.145, (0.0, 0.0), "진입 데크 판재 0.145 [시방]"),
        "tunnel_under":       (0.300, (0.0, 0.0), "보도블록 300 (P3 하위변종)"),
    },
}


def _dim(key):
    """원장에서 값만 꺼낸다. 없는 키는 즉시 예외 — 지어낸 수치 유입 차단."""
    if key not in GROUND_DIMENSIONS:
        raise KeyError(f"ground_kit: GROUND_DIMENSIONS 에 '{key}' 가 없다. "
                       "원장에 근거와 함께 먼저 등재하라.")
    return GROUND_DIMENSIONS[key][0]


# ===========================================================================
# [2] 카메라·프레임 기하 — 사양 §2.1 / 부록 B 와 1:1
# ===========================================================================
def cam_row(X, h=0.3):
    """지면거리 X [m] 에 있는 지면점의 화상 행 **[@1080]**.

    row(2.0)=497.35 · row(10)=297.98. GRAZE JSON 과 비교하려면 반드시
    `to_work_rows()` 로 축을 옮길 것 — 두 축은 정확히 2배 차이다.
    """
    X = max(float(X), 1e-6)
    return CAM_H / 2.0 + CAM_F * math.tan(math.atan(float(h) / X)
                                          - math.radians(-CAM_PITCH_DEG))


def cam_row_z(X, z, h=0.3):
    """지면보다 z 만큼 높은(낮은) 점의 행. 램프처럼 지면이 꺼지는 경우에 쓴다."""
    X = max(float(X), 1e-6)
    return CAM_H / 2.0 + CAM_F * math.tan(math.atan((float(h) - float(z)) / X)
                                          - math.radians(-CAM_PITCH_DEG))


def cam_halfwidth(X):
    """지면거리 X 에서 프레임에 드는 횡방향 반폭 [m]. 0.5774·X."""
    return float(X) * math.tan(math.radians(CAM_HFOV_DEG / 2.0))


def cam_wpx(w, X):
    """가로폭 w [m] 의 화면 폭 [px]."""
    return CAM_F * float(w) / max(float(X), 1e-6)


def cam_lpx(L, X, h=0.3):
    """진행축 길이 L [m] 의 세로 투영 [px]."""
    return CAM_F * float(L) * float(h) / max(float(X), 1e-6) ** 2


def drow(x_e, d, h=0.3):
    """에지(지면거리 d)와 그 전방 x_e [m, 음수] 요소의 행 이격 **[@1080]**."""
    return cam_row(d + float(x_e), h) - cam_row(d, h)


def to_work_rows(rows_1080):
    """`cam_row` 축(@1080) → GRAZE 검사기 작업본 축(@540). 나눗셈 2.0."""
    return float(rows_1080) / ROWS_1080_PER_WORK


def to_1080_rows(rows_work):
    """GRAZE 작업본 축(@540) → `cam_row` 축(@1080)."""
    return float(rows_work) * ROWS_1080_PER_WORK


def graze_row_sep_1080(d, h=0.3, band=None):
    """이 컷에서 **집행 가능한 최강** GT-E2 행 이격 하한 [@1080].

    유도 강도는 `GRAZE_ROW_SEP_WORK = 16` (@540 = 32 @1080, "두 단차응답 완전분리").
    그러나 E 대역 자체가 그보다 얕으면 **대역 안 어떤 위치로도 달성 불가**다
    `[계산]` — d10 의 E 대역은 지면거리 7~22 m = **24.80 행 @540** 뿐이고
    에지행(297.97 @1080)에서 대역 양끝까지가 각각 10.87 / 13.92 행 @540 이라
    16 행을 넘을 방법이 없다. 그런 컷에서 16 을 강제하면 "E 대역 안 횡단선 0본"
    이 되어 §5.1 P1 의 주기 줄눈 처방과 GT-E2 자신의 "≤ 1본" 문언이 동시에 죽는다.

    → **달성 가능하면 완전분리(16 @540), 불가능하면 footprint(8 @540)** 를 건다.
      footprint 미만은 두 응답이 실제로 융합해 에지를 감추므로 어느 컷에서도
      하드 실패로 남는다. 판정 강도는 v1.1(항상 8 @540) 보다 **엄격해지기만 한다**.
    """
    lo, hi = band or GRAZE_E_BAND
    r_e = cam_row(d, h)
    reach = max(abs(cam_row(lo * d, h) - r_e), abs(cam_row(hi * d, h) - r_e))
    return GRAZE_ROW_SEP_1080 if reach >= GRAZE_ROW_SEP_1080 \
        else GRAZE_FOOTPRINT_1080


# 진행축 → (전방 단위벡터, 좌법선 단위벡터)
_AXIS_FRAME = {
    "+x": ((1.0, 0.0), (0.0, 1.0)),
    "-x": ((-1.0, 0.0), (0.0, -1.0)),
    "+y": ((0.0, 1.0), (-1.0, 0.0)),
    "-y": ((0.0, -1.0), (1.0, 0.0)),
}


class _View:
    """씬 좌표 ↔ (전방 s, 횡 t) 변환. 그리드 원점이 다른 씬(§2.3) 대응."""

    def __init__(self, origin=(0.0, 0.0, 0.0), gy=0.0, axis="+x"):
        if axis not in _AXIS_FRAME:
            raise ValueError(f"ground_kit: axis 는 {list(_AXIS_FRAME)} 중 하나.")
        self.origin = (float(origin[0]), float(origin[1]),
                       float(origin[2]) if len(origin) > 2 else 0.0)
        self.gy = float(gy)
        self.axis = axis
        self.fwd, self.lat = _AXIS_FRAME[axis]

    def s_of(self, x, y):
        dx, dy = float(x) - self.origin[0], float(y) - self.origin[1]
        return dx * self.fwd[0] + dy * self.fwd[1]

    def t_of(self, x, y):
        dx, dy = float(x) - self.origin[0], float(y) - self.origin[1]
        return dx * self.lat[0] + dy * self.lat[1]

    def s_span(self, aabb):
        """AABB 의 전방 s 구간 (진행축이 ±x/±y 축평행이므로 4모서리 중 2개면 충분)."""
        xs = (aabb[0], aabb[3])
        ys = (aabb[1], aabb[4])
        vals = [self.s_of(x, y) for x in xs for y in ys]
        return min(vals), max(vals)

    def t_span(self, aabb):
        xs = (aabb[0], aabb[3])
        ys = (aabb[1], aabb[4])
        vals = [self.t_of(x, y) for x in xs for y in ys]
        return min(vals), max(vals)


# ===========================================================================
# [3] Elem — 계획의 원자. plan_ground 만으로 프림·GT·프레임 예산이 판정된다.
# ===========================================================================
def _elem(kind, path, aabb, proud=0.0, mtl_key=None, **meta):
    """`dict(kind, path, aabb, proud, mtl_key, meta)` — 사양 §3.3.

    meta 규약:
      line     : None | "cross"(전폭 횡단 단선) | "cross_periodic"(주기 격자)
                 | "long"(종단선)
      area     : True 면 면 요소(B1·B2 대상)
      decal    : True 면 오염 데칼(B5 대상)
      exc      : GT 예외 등록 종류 — None | "tactile" | "scatter" | "weed"
                 | "plank_gap"
      albedo   : 알베도(B9). None 이면 미신고 = 검사 제외
      surface_z: 요소가 얹히는 면의 z(램프처럼 지면이 꺼지는 경우)
      beyond   : True 면 에지 너머(램프 노면 등) — 가시 컷이 제한된다
    """
    return dict(kind=kind, path=path,
                aabb=tuple(float(v) for v in aabb),
                proud=float(proud), mtl_key=mtl_key, meta=dict(meta))


def _seed_key(path):
    """`{ROOT}/GKit/` 이후 부분만 시드 키로 쓴다.

    `plan_ground` 는 prefix 를 모르고(`"Crack"`), `apply_ground` 는 전체 경로
    (`"/World/Scene15/GKit/Crack"`)를 넘긴다. 경로를 그대로 시드에 넣으면 두
    단계가 **다른 난수열**을 뽑아 프림 수가 어긋난다(실제로 2 프림 어긋났다).
    """
    p = str(path)
    tok = "/" + GKIT_PATH_TOKEN + "/"
    i = p.find(tok)
    return p[i + len(tok):] if i >= 0 else p.lstrip("/")


def _box_aabb(cx, cy, cz, sx, sy, sz):
    return (cx - sx / 2.0, cy - sy / 2.0, cz - sz / 2.0,
            cx + sx / 2.0, cy + sy / 2.0, cz + sz / 2.0)


def _obb_aabb(cx, cy, cz, L, w, t, yaw_deg):
    """yaw 회전한 박스의 **정확한** 축정렬 AABB.

    정사각 근사(`max(L,w)`)를 쓰면 전방 s 구간이 부풀어 GT-E2 판정과 가시 컷
    판정이 통째로 틀어진다 — scene13 진입 트렌치가 d10 에서 "보인다"고 오판한
    실제 버그가 여기서 나왔다.
    """
    c = abs(math.cos(math.radians(yaw_deg)))
    sn = abs(math.sin(math.radians(yaw_deg)))
    hx = (L * c + w * sn) / 2.0
    hy = (L * sn + w * c) / 2.0
    return (cx - hx, cy - hy, cz - t / 2.0, cx + hx, cy + hy, cz + t / 2.0)


def _norm_region(region):
    x0, y0, x1, y1 = [float(v) for v in region]
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


# ===========================================================================
# [4] 신규 소빌더 15종 — 전부 **기하**. 재질은 T1 소관(사양 §4.4).
#
#     공통 규약: `(kit, path, ...)` 첫 두 인자 고정. 반환은
#     `dict(prim_count=int, elems=[Elem, ...])`. `kit` 에 `dry_kit()` 를 주면
#     USD 접촉 없이 같은 계산을 한다 — plan_ground 가 이 성질을 쓴다.
# ===========================================================================
def build_joint_grid(kit, path, region, z, mtl, step_x=3.0, step_y=None,
                     width=None, recess=None, jitter=0.0, seed=0,
                     origin_xy=(0.0, 0.0), skip_x=(), skip_y=(),
                     kind="contraction"):
    """**포장 분할·수축·신축 줄눈 격자** (음각 홈).

    `step_y=None` → 횡방향(진행축 직교) 줄눈만. 텍스처 줄눈은 음영이 없어
    h0.3 스침각에서 죽는다 `[실측 — 09·18 sd 13~14]` → 기하로 낸다.

    음각 구현: 상면을 `z + recess`(음수)에 두는 얇은 판. 슬래브 상면보다
    낮으므로 홈으로 읽힌다. **P-A(스킨 OFF)가 선행되지 않으면 묻힌다.**

    `origin_xy` 는 격자 원점 — **T1 MDL `unit_cell_origin` 과 같은 값이어야
    한다**(§4.5 U3). `skip_x/skip_y` 는 에지 금지대·개구로 드롭된 좌표.

    프림: 1/줄눈.  GT: 음각 ≤3 mm — **낙차 아님**.
    """
    x0, y0, x1, y1 = _norm_region(region)
    width = _dim("joint_%s_w" % kind) if width is None else float(width)
    recess = (_dim("joint_%s_recess" % kind) if recess is None
              else float(recess))
    if recess > 0:
        raise ValueError("ground_kit: 줄눈은 음각이다(recess ≤ 0). "
                         f"받은 값 {recess}")
    thick = 0.030                      # 판 두께(상면만 보인다)
    cz = float(z) + recess - thick / 2.0
    ox, oy = float(origin_xy[0]), float(origin_xy[1])
    rng = det_rng("gkit.joint", _seed_key(path), seed)
    n0 = kit.mark()
    elems = []

    def _ticks(a0, a1, step, o):
        if not step or step <= 0:
            return []
        i0 = int(math.ceil((a0 - o) / step - 1e-9))
        i1 = int(math.floor((a1 - o) / step + 1e-9))
        return [o + i * step for i in range(i0, i1 + 1)]

    skipx = set(round(float(v), 4) for v in skip_x)
    skipy = set(round(float(v), 4) for v in skip_y)
    for i, xx in enumerate(_ticks(x0, x1, step_x, ox)):
        if round(xx, 4) in skipx:
            continue
        jx = xx + (rng.random() - 0.5) * 2.0 * jitter
        p = f"{path}/JX_{i}"
        kit.B(p, ((jx), (y0 + y1) / 2.0, cz), (width, y1 - y0, thick), mtl)
        elems.append(_elem("joint", p,
                           _box_aabb(jx, (y0 + y1) / 2.0, cz,
                                     width, y1 - y0, thick),
                           proud=recess, mtl_key="joint",
                           line="cross_periodic", albedo=0.12))
    for i, yy in enumerate(_ticks(y0, y1, step_y, oy) if step_y else []):
        if round(yy, 4) in skipy:
            continue
        jy = yy + (rng.random() - 0.5) * 2.0 * jitter
        p = f"{path}/JY_{i}"
        kit.B(p, ((x0 + x1) / 2.0, jy, cz), (x1 - x0, width, thick), mtl)
        elems.append(_elem("joint", p,
                           _box_aabb((x0 + x1) / 2.0, jy, cz,
                                     x1 - x0, width, thick),
                           proud=recess, mtl_key="joint",
                           line="long", albedo=0.12))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_slab_joints(kit, path, region, z, mtl, step_x=None, step_y=None,
                      seed=0, origin_xy=(0.0, 0.0), skip_x=(), skip_y=()):
    """**판석 줄눈** — `build_joint_grid` 의 얇은 프리셋(폭 5~9 mm·음각 1~2 mm).

    프림: 1/줄눈.  GT: 음각 2 mm — 낙차 아님.
    """
    step_x = _dim("module_granite_slab") * 3 if step_x is None else step_x
    return build_joint_grid(kit, path, region, z, mtl,
                            step_x=step_x, step_y=step_y,
                            width=_dim("joint_slab_w"),
                            recess=_dim("joint_slab_recess"),
                            seed=seed, origin_xy=origin_xy,
                            skip_x=skip_x, skip_y=skip_y, kind="slab")


def build_patch_field(kit, path, region, z, mtls, n=2, area_mean=None,
                      ar=(0.7, 1.6), cutline=True, seed=0, sites=None,
                      cutline_n=1):
    """**보수 패치 + 컷라인.** 기본 0.7×0.9 m (건당 0.61~0.69 ㎡ `[통계]`).

    면적·위치는 기하(여기), 색차는 재질(T1) — 사양 §4.4.
    `sites` 를 주면 그 좌표에, 없으면 region 안 결정적 난수 배치.

    프림: 1/매 + 4/컷라인 매. `cutline_n` 매(기본 1 — **근경 1매만**)에만
    컷라인을 붙인다 — §8.2 프로파일 견적이 1 프림/매를 전제하기 때문이다.

    GT: +2 mm — 낙차 아님.
    """
    x0, y0, x1, y1 = _norm_region(region)
    area_mean = _dim("patch_area_mean") if area_mean is None else float(area_mean)
    pr = _dim("patch_proud")
    cpr = _dim("patch_cutline_proud")
    rng = det_rng("gkit.patch", _seed_key(path), seed)
    n0 = kit.mark()
    elems = []
    mtl = mtls.get("patch") if isinstance(mtls, dict) else mtls
    mtl_cut = (mtls.get("patch_cut", mtl) if isinstance(mtls, dict) else mtls)
    for i in range(int(n)):
        a = area_mean * (0.85 + 0.30 * rng.random())
        r = ar[0] + (ar[1] - ar[0]) * rng.random()
        w = math.sqrt(a * r)
        h = a / w
        if sites and i < len(sites):
            cx, cy = float(sites[i][0]), float(sites[i][1])
        else:
            cx = x0 + w / 2.0 + rng.random() * max(1e-6, (x1 - x0) - w)
            cy = y0 + h / 2.0 + rng.random() * max(1e-6, (y1 - y0) - h)
        p = f"{path}/Patch_{i}"
        kit.B(p, (cx, cy, z + pr - 0.015), (w, h, 0.030), mtl)
        elems.append(_elem("patch", p,
                           _box_aabb(cx, cy, z + pr - 0.015, w, h, 0.030),
                           proud=pr, mtl_key="patch", area=True, albedo=0.22))
        if cutline and i < int(cutline_n):
            for k, (dx, dy, sw, sh) in enumerate((
                    (-w / 2.0, 0.0, 0.02, h), (w / 2.0, 0.0, 0.02, h),
                    (0.0, -h / 2.0, w, 0.02), (0.0, h / 2.0, w, 0.02))):
                q = f"{path}/Patch_{i}_Cut{k}"
                kit.B(q, (cx + dx, cy + dy, z + cpr - 0.010),
                      (sw, sh, 0.020), mtl_cut)
                elems.append(_elem("patch_cut", q,
                                   _box_aabb(cx + dx, cy + dy, z + cpr - 0.010,
                                             sw, sh, 0.020),
                                   proud=cpr, mtl_key="patch_cut",
                                   albedo=0.14))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_crack_lines(kit, path, region, z, mtl, n=4, seg=None, branch_p=0.25,
                      width=None, seed=0):
    """**균열 폴리라인** (음각). 텍스처 균열은 반복 패턴이 근경에서 보인다
    `[실측 — N4]` → 개별 기하로 낸다.

    프림: **3~5/본**(분기 시 5). §4.3 표기는 "4~6/본" 이지만 §8.2 프로파일
    견적(P1 "2+12" = 균열 4본에 12 프림)은 3/본을 전제한다 — 예산표 쪽을 채택했다.
    GT: 음각 ≤10 mm — 낙차 아님.
    """
    x0, y0, x1, y1 = _norm_region(region)
    seg = _dim("crack_seg") if seg is None else float(seg)
    width = _dim("crack_w") if width is None else float(width)
    rec = _dim("crack_recess")
    rng = det_rng("gkit.crack", _seed_key(path), seed)
    n0 = kit.mark()
    elems = []
    span = seg * 3.0                      # 폴리라인이 영역을 벗어나지 않게 여유
    for i in range(int(n)):
        cx = x0 + span + rng.random() * max(1e-6, (x1 - x0) - 2 * span)
        cy = y0 + span + rng.random() * max(1e-6, (y1 - y0) - 2 * span)
        ang = rng.random() * math.pi
        nseg = 3 if rng.random() > branch_p else 5
        for k in range(nseg):
            ang += (rng.random() - 0.5) * 0.9
            sx = cx + math.cos(ang) * seg / 2.0
            sy = cy + math.sin(ang) * seg / 2.0
            p = f"{path}/Crack_{i}_{k}"
            kit.B(p, (sx, sy, z + rec - 0.010), (seg, width, 0.020), mtl,
                  rotz=math.degrees(ang))
            elems.append(_elem("crack", p,
                               _obb_aabb(sx, sy, z + rec - 0.010,
                                         seg, width, 0.020,
                                         math.degrees(ang)),
                               proud=rec, mtl_key="crack", albedo=0.08))
            cx = cx + math.cos(ang) * seg
            cy = cy + math.sin(ang) * seg
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_trench_drain(kit, path, x0, y0, x1, y1, z, mtl, mtl_frame=None,
                       width=None, slats=0, flush=True):
    """**선형 트렌치 그레이팅.** `sceneN5` 슬랫 로직의 일반화.

    구성: 틀(프레임) 1 + 커버 1 (+ 슬랫 n). 커버 상면은 틀 상면보다
    `seat=2 mm` 낮다 — 동일평면 z-fighting 회피이자 물리적으로도 맞다
    `[실측 — infra_kit.build_gully(seat=0.002)]`.

    프림: 2 (슬랫 모드 2+n).  GT: flush — **낙차 아님**(무개구 금지).
    """
    width = _dim("trench_w") if width is None else float(width)
    seat = _dim("trench_seat")
    fw = _dim("trench_frame_w")
    n0 = kit.mark()
    elems = []
    cx, cy = (float(x0) + float(x1)) / 2.0, (float(y0) + float(y1)) / 2.0
    L = math.hypot(float(x1) - float(x0), float(y1) - float(y0))
    yaw = math.degrees(math.atan2(float(y1) - float(y0), float(x1) - float(x0)))
    p = f"{path}/Frame"
    kit.B(p, (cx, cy, float(z) - 0.030), (L, width + 2 * fw, 0.060),
          mtl_frame or mtl, rotz=yaw)
    elems.append(_elem("trench", p,
                       _obb_aabb(cx, cy, float(z) - 0.030,
                                 L, width + 2 * fw, 0.060, yaw),
                       proud=0.0, mtl_key="trench_frame",
                       line="cross" if abs(math.sin(math.radians(yaw))) > 0.5
                       else "long", area=True, albedo=0.10))
    q = f"{path}/Cover"
    kit.B(q, (cx, cy, float(z) - seat - 0.020), (L, width, 0.040), mtl,
          rotz=yaw)
    elems.append(_elem("trench_cover", q,
                       _obb_aabb(cx, cy, float(z) - seat - 0.020,
                                 L, width, 0.040, yaw),
                       proud=-seat, mtl_key="trench", area=True, albedo=0.09))
    for i in range(int(slats)):
        s = -L / 2.0 + (i + 0.5) * (L / max(1, int(slats)))
        sx = cx + s * math.cos(math.radians(yaw))
        sy = cy + s * math.sin(math.radians(yaw))
        r = f"{path}/Slat_{i}"
        kit.B(r, (sx, sy, float(z) - 0.010), (0.012, width, 0.020), mtl,
              rotz=yaw)
        elems.append(_elem("trench_slat", r,
                           _obb_aabb(sx, sy, float(z) - 0.010,
                                     0.012, width, 0.020, yaw),
                           proud=0.0, mtl_key="trench", albedo=0.06))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_gutter_U(kit, path, x0, y0, x1, y1, z, mtl, mtl_cover=None,
                   width=None, cover=True, cover_len=None):
    """**덮개식 U형 측구** (골목·터널). 벽측을 따라 종주한다.

    L형 측구(`infra_kit.build_gutter_L`)는 차도 가장자리용이고, 골목·지하보도는
    **덮개식 U형**이 표본 관행이다 `[추정 — 표본 관측]`.

    프림: 1 + ceil(L/cover_len).  GT: flush — 낙차 아님.
    """
    width = _dim("gutter_U_w") if width is None else float(width)
    cover_len = (_dim("gutter_U_cover_len") if cover_len is None
                 else float(cover_len))
    n0 = kit.mark()
    elems = []
    L = math.hypot(float(x1) - float(x0), float(y1) - float(y0))
    yaw = math.degrees(math.atan2(float(y1) - float(y0), float(x1) - float(x0)))
    cx, cy = (float(x0) + float(x1)) / 2.0, (float(y0) + float(y1)) / 2.0
    p = f"{path}/Channel"
    kit.B(p, (cx, cy, float(z) - 0.120), (L, width, 0.240), mtl, rotz=yaw)
    elems.append(_elem("gutter_u", p,
                       _obb_aabb(cx, cy, float(z) - 0.120,
                                 L, width, 0.240, yaw),
                       proud=0.0, mtl_key="gutter", line="long",
                       area=True, albedo=0.16))
    if cover:
        n = max(1, int(math.ceil(L / cover_len)))
        for i in range(n):
            s = -L / 2.0 + (i + 0.5) * (L / n)
            sx = cx + s * math.cos(math.radians(yaw))
            sy = cy + s * math.sin(math.radians(yaw))
            q = f"{path}/Cover_{i}"
            kit.B(q, (sx, sy, float(z) - 0.024), (L / n - 0.01, width, 0.048),
                  mtl_cover or mtl, rotz=yaw)
            elems.append(_elem("gutter_cover", q,
                               _obb_aabb(sx, sy, float(z) - 0.024,
                                         L / n, width, 0.048, yaw),
                               proud=0.0, mtl_key="gutter_cover",
                               line="long", area=True, albedo=0.14))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_groove_band(kit, path, region, z, mtl=None, pitch=None, width=0.006,
                      shade=None, geom_fallback=False):
    """**논슬립 홈파기 명암 밴드** — 사양 §4.4 는 **T1(MDL 스트라이프) 1순위**.

    기하로 만들면 17 m 램프에 140 프림이다 `[계산]`. 기본은 **프림 0** —
    `materials_needed` 로 T1 에 스트라이프 요청만 남긴다.
    `geom_fallback=True` 는 T1 미배선 시 폴백(프림 폭증 주의).

    프림: **0**(재질 위임) / 폴백 시 1/홈.  GT: 무변.
    """
    x0, y0, x1, y1 = _norm_region(region)
    pitch = _dim("groove_pitch") if pitch is None else float(pitch)
    shade = _dim("groove_shade") if shade is None else float(shade)
    n0 = kit.mark()
    elems = []
    if not geom_fallback:
        return dict(prim_count=0, elems=[], material_req=[
            dict(kind="groove_stripe", region=(x0, y0, x1, y1),
                 pitch=pitch, shade=shade, owner="T1")])
    n = int((x1 - x0) / pitch)
    for i in range(n):
        xx = x0 + (i + 0.5) * pitch
        p = f"{path}/Groove_{i}"
        kit.B(p, (xx, (y0 + y1) / 2.0, float(z) - 0.0015 - 0.010),
              (width, y1 - y0, 0.020), mtl)
        elems.append(_elem("groove", p,
                           _box_aabb(xx, (y0 + y1) / 2.0,
                                     float(z) - 0.0115, width, y1 - y0, 0.020),
                           proud=-0.0015, mtl_key="groove",
                           line="cross_periodic", albedo=0.10))
    return dict(prim_count=kit.count_since(n0), elems=elems,
                material_req=[])


def build_membrane(kit, path, region, z, mtl, seam_pitch=None, wear_n=4,
                   seed=0, albedo=None):
    """**도막 방수 / 논슬립 도막 + 마모 박리.** scene19(옥상)·scene06(육교).

    알베도는 감독 결재 M2 로 **0.16~0.22** 확정 — 순백 위반 1위 씬의 처방이다.
    도막 마감에 **신축줄눈 격자는 금지**(실물에 없는 조합, §5.6).

    프림: 1(도막면) + 이음 + 박리.  GT: +0.6 mm — 낙차 아님.
    """
    x0, y0, x1, y1 = _norm_region(region)
    seam_pitch = (_dim("membrane_seam_pitch") if seam_pitch is None
                  else float(seam_pitch))
    pr = _dim("membrane_proud")
    albedo = _dim("membrane_albedo") if albedo is None else float(albedo)
    rng = det_rng("gkit.membrane", _seed_key(path), seed)
    n0 = kit.mark()
    elems = []
    p = f"{path}/Coat"
    kit.B(p, ((x0 + x1) / 2.0, (y0 + y1) / 2.0, float(z) + pr - 0.005),
          (x1 - x0, y1 - y0, 0.010), mtl)
    elems.append(_elem("membrane", p,
                       _box_aabb((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                                 float(z) + pr - 0.005,
                                 x1 - x0, y1 - y0, 0.010),
                       proud=pr, mtl_key="membrane", area=True, albedo=albedo))
    n = max(0, int((y1 - y0) / seam_pitch) - 1)
    for i in range(n):
        yy = y0 + (i + 1) * seam_pitch
        q = f"{path}/Seam_{i}"
        kit.B(q, ((x0 + x1) / 2.0, yy, float(z) + pr + 0.0004 - 0.004),
              (x1 - x0, 0.030, 0.008), mtl)
        elems.append(_elem("membrane_seam", q,
                           _box_aabb((x0 + x1) / 2.0, yy,
                                     float(z) + pr - 0.0036,
                                     x1 - x0, 0.030, 0.008),
                           proud=pr + 0.0004, mtl_key="membrane_seam",
                           line="long", albedo=albedo * 0.9))
    for i in range(int(wear_n)):
        cx = x0 + rng.random() * (x1 - x0)
        cy = y0 + rng.random() * (y1 - y0)
        w = 0.35 + rng.random() * 0.45
        r = f"{path}/Wear_{i}"
        kit.B(r, (cx, cy, float(z) + pr + 0.0002 - 0.004), (w, w * 0.8, 0.008),
              mtl)
        elems.append(_elem("membrane_wear", r,
                           _box_aabb(cx, cy, float(z) + pr - 0.0038,
                                     w, w * 0.8, 0.008),
                           proud=pr + 0.0002, mtl_key="membrane_wear",
                           area=True, albedo=min(ALBEDO_CAP, albedo * 1.35)))
    return dict(prim_count=kit.count_since(n0), elems=elems)


_STAIN_KINDS = ("tire", "oil", "water", "efflorescence", "gum", "dirt",
                "grime_band", "drip")


def build_stain_field(kit, path, region, z, mtl, kind="dirt", n=6, seed=0,
                      band_axis="long", albedo=None):
    """**오염 데칼** — 타이어·유류·물때·백화·껌·흙·기단 밴드·낙수.

    위치가 씬 논리에 종속(드레인 주변·통행선·기단)이라 MDL 절차 마스크로는
    제어 불가 → **얇은 판 프림**으로 낸다(사양 §4.4).
    `grime_band` 는 벽–바닥 접합 밴드로 **바닥면만** 담당한다(벽면은 T1 대기).

    프림: 1/개.  GT: +0.6 mm — 낙차 아님.
    """
    if kind not in _STAIN_KINDS:
        raise ValueError(f"ground_kit: stain kind 는 {_STAIN_KINDS} 중 하나.")
    x0, y0, x1, y1 = _norm_region(region)
    pr = _dim("stain_proud")
    am = _dim("stain_area_mean")
    albedo = 0.16 if albedo is None else float(albedo)
    rng = det_rng("gkit.stain", _seed_key(path), kind, seed)
    n0 = kit.mark()
    elems = []
    for i in range(int(n)):
        if kind == "grime_band":
            w, h = (x1 - x0), 0.15
            cx = (x0 + x1) / 2.0
            cy = (y0 if i % 2 == 0 else y1) + (0.075 if i % 2 == 0 else -0.075)
            line = "long" if band_axis == "long" else "cross"
        elif kind == "tire":
            w, h = 1.2 + rng.random() * 1.6, 0.22
            cx = x0 + w / 2.0 + rng.random() * max(1e-6, (x1 - x0) - w)
            cy = y0 + h / 2.0 + rng.random() * max(1e-6, (y1 - y0) - h)
            line = "long"
        else:
            a = am * (0.6 + 0.9 * rng.random())
            w = math.sqrt(a * (0.8 + 0.6 * rng.random()))
            h = a / w
            cx = x0 + w / 2.0 + rng.random() * max(1e-6, (x1 - x0) - w)
            cy = y0 + h / 2.0 + rng.random() * max(1e-6, (y1 - y0) - h)
            line = None
        p = f"{path}/{kind}_{i}"
        kit.B(p, (cx, cy, float(z) + pr - 0.004), (w, h, 0.008), mtl)
        elems.append(_elem("stain", p,
                           _box_aabb(cx, cy, float(z) + pr - 0.004, w, h, 0.008),
                           proud=pr, mtl_key="stain_%s" % kind,
                           decal=True, line=line, albedo=albedo,
                           stain_kind=kind))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_footprints(kit, path, path_pts, z, mtl, n=10, seed=0, stride=0.62):
    """**발자국·1륜차 자국** (D2 타설 슬래브). 흔적이지 객체가 아니다 —
    "사람·차량 배치 금지" 규약과 무관 `[사양 §11]`.

    프림: 1/개.  GT: +0.6 mm — 낙차 아님.
    """
    pr = _dim("stain_proud")
    rng = det_rng("gkit.foot", _seed_key(path), seed)
    n0 = kit.mark()
    elems = []
    pts = [(float(a), float(b)) for a, b in path_pts]
    if len(pts) < 2:
        raise ValueError("ground_kit: 발자국 경로는 점 2개 이상.")
    total = sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
                for i in range(len(pts) - 1))
    for i in range(int(n)):
        s = min(total, (i + 0.5) * stride)
        acc, px, py, ang = 0.0, pts[0][0], pts[0][1], 0.0
        for k in range(len(pts) - 1):
            seg = math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])
            if acc + seg >= s:
                u = (s - acc) / max(seg, 1e-6)
                px = pts[k][0] + u * (pts[k + 1][0] - pts[k][0])
                py = pts[k][1] + u * (pts[k + 1][1] - pts[k][1])
                ang = math.degrees(math.atan2(pts[k + 1][1] - pts[k][1],
                                              pts[k + 1][0] - pts[k][0]))
                break
            acc += seg
        off = 0.11 if i % 2 == 0 else -0.11
        ox = px - math.sin(math.radians(ang)) * off
        oy = py + math.cos(math.radians(ang)) * off
        p = f"{path}/Foot_{i}"
        kit.B(p, (ox, oy, float(z) + pr - 0.004), (0.27, 0.10, 0.008), mtl,
              rotz=ang + (rng.random() - 0.5) * 12.0)
        elems.append(_elem("footprint", p,
                           _obb_aabb(ox, oy, float(z) + pr - 0.004,
                                     0.27, 0.10, 0.008, ang),
                           proud=pr, mtl_key="stain_dirt", decal=True,
                           albedo=0.15))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_wear_lane(kit, path, centerline, z, mtl, width=None,
                    albedo_gain=None, split=1):
    """**답압 마모 띠** — 통행 동선의 알베도 저하대. `[통계]` 등산로 6/6.

    프림: 1~3.  GT: 무변(면 위 데칼).
    """
    width = _dim("wear_lane_w") if width is None else float(width)
    gain = _dim("wear_albedo_gain") if albedo_gain is None else float(albedo_gain)
    pr = _dim("stain_proud")
    n0 = kit.mark()
    elems = []
    (ax, ay), (bx, by) = centerline
    L = math.hypot(bx - ax, by - ay)
    yaw = math.degrees(math.atan2(by - ay, bx - ax))
    for i in range(max(1, int(split))):
        u0, u1 = i / split, (i + 1) / split
        cx = ax + (bx - ax) * (u0 + u1) / 2.0
        cy = ay + (by - ay) * (u0 + u1) / 2.0
        p = f"{path}/Wear_{i}"
        kit.B(p, (cx, cy, float(z) + pr - 0.004),
              (L / split, width, 0.008), mtl, rotz=yaw)
        elems.append(_elem("wear_lane", p,
                           _obb_aabb(cx, cy, float(z) + pr - 0.004,
                                     L / split, width, 0.008, yaw),
                           proud=pr, mtl_key="wear", line="long",
                           albedo=min(ALBEDO_CAP, 0.22 * gain)))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_edge_litter(kit, path, centerline, z, mtl, width=None):
    """**가장자리 유기물 띠** — 길 양연에 쓸려 쌓인 유기물(계절 중립).

    프림: 2.  GT: 무변.
    """
    width = _dim("edge_litter_w") if width is None else float(width)
    pr = _dim("stain_proud")
    n0 = kit.mark()
    elems = []
    (ax, ay), (bx, by) = centerline
    L = math.hypot(bx - ax, by - ay)
    yaw = math.degrees(math.atan2(by - ay, bx - ax))
    nx, ny = -math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
    for tag, sgn in (("L", -1.0), ("R", 1.0)):
        cx = (ax + bx) / 2.0 + nx * sgn * (width / 2.0)
        cy = (ay + by) / 2.0 + ny * sgn * (width / 2.0)
        p = f"{path}/Litter_{tag}"
        kit.B(p, (cx, cy, float(z) + pr - 0.004), (L, width, 0.008), mtl,
              rotz=yaw)
        elems.append(_elem("edge_litter", p,
                           _obb_aabb(cx, cy, float(z) + pr - 0.004,
                                     L, width, 0.008, yaw),
                           proud=pr, mtl_key="litter", line="long",
                           albedo=0.13))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_edge_break(kit, path, line, z, mtl, width=None, density=12.0,
                     seed=0, scatter_only=False):
    """**재질 경계 파쇄** — 직선 경계에 전이대를 얹어 "칼로 자른 경계"를 없앤다.

    scene04 "잔디 사각 이음매"의 진범은 타일링이 아니라 **3.0×6.0 m dirt 박스와
    grass 슬래브의 전이대 0 px 재질 경계**(ΔE76 18.9)다 `[실측 — B조 §3]`.
    scene10 은 흙길↔잔디 ΔE76 15.2 · 낙엽 데칼 윤곽 27.3 `[실측 — 사양 §13.3]`.

    구성: 전이대 띠 1 프림 + (산포는 `scatter_debris` 콜백에 위임 — `edge_bias`
    인자가 이미 있어 직결된다 `[실측 — scene_common.py:1805]`).

    프림: 1 + 산포(위임).  GT: 무변.
    """
    width = _dim("edge_break_w") if width is None else float(width)
    pr = _dim("stain_proud")
    n0 = kit.mark()
    elems = []
    (ax, ay), (bx, by) = line
    L = math.hypot(bx - ax, by - ay)
    yaw = math.degrees(math.atan2(by - ay, bx - ax))
    if not scatter_only:
        p = f"{path}/Trans"
        kit.B(p, ((ax + bx) / 2.0, (ay + by) / 2.0, float(z) + pr - 0.004),
              (L, width, 0.008), mtl, rotz=yaw)
        elems.append(_elem("edge_break", p,
                           _obb_aabb((ax + bx) / 2.0, (ay + by) / 2.0,
                                     float(z) + pr - 0.004,
                                     L, width, 0.008, yaw),
                           proud=pr, mtl_key="edge_break", line="long",
                           albedo=0.17))
    # 전이대 산포는 **프레임 유효 구간**만 의미가 있다 — 근경 창 밖으로 무한히
    # 늘리면 예산만 먹는다. 라인당 상한 35(= 사양 §8.2 P18 산포 250 배분).
    n_scat = min(35, int(round(L * float(density))))
    return dict(prim_count=kit.count_since(n0), elems=elems,
                scatter_req=[dict(line=line, width=width * 2.0,
                                  count=n_scat, edge_bias=width)])


def build_deck_planks(kit, path, x0, y0, x1, y1, z, mtl, plank_w=None,
                      gap=None, butt=None, seed=0, max_gaps=None):
    """**데크 판재 분할** — 슬래브는 씬이 이미 갖고 있으므로 **틈 스트립만** 낸다.

    판재 폭 0.145 · 틈 0.005 `[시방 KCS 34 5-2-1 2.3.1]`. 틈은 음각 20 mm
    (판재 두께 내부 — **상면 z 불변**이라 GT 낙차가 아니다).

    프림: 1/틈 (+마구리).  GT: 음각 20 mm — 낙차 아님.
    """
    plank_w = _dim("module_deck_plank") if plank_w is None else float(plank_w)
    gap = _dim("deck_plank_gap") if gap is None else float(gap)
    butt_len = _dim("deck_butt_len") if butt is None else float(butt)
    x0, y0, x1, y1 = _norm_region((x0, y0, x1, y1))
    n0 = kit.mark()
    elems = []
    pitch = plank_w + gap
    n = int((x1 - x0) / pitch)
    if max_gaps:
        n = min(n, int(max_gaps))
    for i in range(n):
        xx = x0 + (i + 1) * pitch
        if xx >= x1:
            break
        p = f"{path}/Gap_{i}"
        kit.B(p, (xx, (y0 + y1) / 2.0, float(z) - 0.020 - 0.010),
              (gap, y1 - y0, 0.020), mtl)
        elems.append(_elem("plank_gap", p,
                           _box_aabb(xx, (y0 + y1) / 2.0, float(z) - 0.030,
                                     gap, y1 - y0, 0.020),
                           proud=-0.020, mtl_key="deck_gap",
                           line="cross_periodic", exc="plank_gap",
                           deck=True, albedo=0.06))
    nb = max(0, int((y1 - y0) / butt_len) - 1)
    for i in range(nb):
        yy = y0 + (i + 1) * butt_len
        q = f"{path}/Butt_{i}"
        kit.B(q, ((x0 + x1) / 2.0, yy, float(z) - 0.030),
              (x1 - x0, gap, 0.020), mtl)
        elems.append(_elem("plank_butt", q,
                           _box_aabb((x0 + x1) / 2.0, yy, float(z) - 0.030,
                                     x1 - x0, gap, 0.020),
                           proud=-0.020, mtl_key="deck_gap", line="long",
                           exc="plank_gap", deck=True, albedo=0.06))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_silt_band(kit, path, region, waterline, z, mtl, width=None,
                    albedo_gain=0.80, n=2):
    """**침수 실트·물때·모래 밀림 띠** — 수변(03·09·12·18)의 수위 흔적.

    프림: 1~2.  GT: 무변.
    """
    x0, y0, x1, y1 = _norm_region(region)
    width = _dim("silt_band_w") if width is None else float(width)
    pr = _dim("stain_proud")
    n0 = kit.mark()
    elems = []
    for i in range(int(n)):
        yy = float(waterline) + (i + 0.5) * width
        p = f"{path}/Silt_{i}"
        kit.B(p, ((x0 + x1) / 2.0, yy, float(z) + pr - 0.004),
              (x1 - x0, width, 0.008), mtl)
        elems.append(_elem("silt_band", p,
                           _box_aabb((x0 + x1) / 2.0, yy, float(z) + pr - 0.004,
                                     x1 - x0, width, 0.008),
                           proud=pr, mtl_key="silt", line="long",
                           albedo=min(ALBEDO_CAP, 0.24 * albedo_gain)))
    return dict(prim_count=kit.count_since(n0), elems=elems)


# ── infra_kit 재사용 6종 어댑터 (재구현 아님 — 계획용 Elem 을 붙일 뿐) ──────
def _ik_manhole(kit, path, cx, cy, z, mtl, mtl_frame=None, d_frame=0.648):
    n0 = kit.mark()
    r = ik.build_manhole(kit, path, cx, cy, z, mtl, frame_mtl=mtl_frame,
                         d_frame=d_frame, lid=True, proud=None)
    pr = float(r.get("proud", 0.0))
    return dict(prim_count=kit.count_since(n0), elems=[
        _elem("manhole", path,
              _box_aabb(cx, cy, z - 0.055, d_frame, d_frame, 0.110),
              proud=abs(pr), mtl_key="manhole", area=True, albedo=0.10,
              screen_w=d_frame)], ik=r)


def _ik_gully(kit, path, cx, cy, z, mtl, yaw_deg=0.0):
    n0 = kit.mark()
    r = ik.build_gully(kit, path, cx, cy, z, mtl, yaw_deg=yaw_deg, lid=True)
    return dict(prim_count=kit.count_since(n0), elems=[
        _elem("gully", path, _box_aabb(cx, cy, z - 0.030, 0.50, 0.40, 0.060),
              proud=0.0, mtl_key="gully", area=True, albedo=0.09,
              screen_w=0.40)], ik=r)


def _ik_gutter_l(kit, path, x0, y0, x1, y1, z, mtl):
    n0 = kit.mark()
    r = ik.build_gutter_L(kit, path, x0, y0, x1, y1, z, mtl,
                          width=0.30, contraction=6.0, expansion=20.0)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    L = math.hypot(x1 - x0, y1 - y0)
    return dict(prim_count=kit.count_since(n0), elems=[
        _elem("gutter_l", path,
              _box_aabb(cx, cy, z - 0.10, max(L, 0.30), max(L, 0.30), 0.20),
              proud=0.0, mtl_key="gutter", line="long", area=True,
              albedo=0.20)], ik=r)


def _ik_marking(kit, path, kind, mtl, x0, y0, z, yaw_deg=0.0, **kw):
    n0 = kit.mark()
    r = ik.build_road_marking(kit, path, kind, mtl, x0, y0, z,
                              yaw_deg=yaw_deg, **kw)
    L = float(r.get("length", 3.0))
    w = float(r.get("width", 0.15))
    line = "cross" if 45.0 < (abs(yaw_deg) % 180.0) < 135.0 else "long"
    return dict(prim_count=kit.count_since(n0), elems=[
        _elem("marking", path,
              _box_aabb(x0 + L / 2.0, y0, z + 0.0015, L, max(w, 0.15), 0.003),
              proud=ik.INFRA_DIMENSIONS["marking_proud"][0],
              mtl_key="marking", line=line, albedo=ALBEDO_CAP)], ik=r)


def _ik_tactile(kit, path, kind, x0, y0, x1, y1, mtl, z=0.0, relief="normal",
                walk_axis="x", site=None):
    n0 = kit.mark()
    r = ik.build_tactile_pair(kit, path, kind, x0, y0, x1, y1, mtl, z=z,
                              relief=relief, walk_axis=walk_axis)
    h = float(r.get("nub_h", _dim("tactile_dot_h")))
    return dict(prim_count=kit.count_since(n0), elems=[
        _elem("tactile", path,
              (min(x0, x1), min(y0, y1), z - 0.060,
               max(x0, x1), max(y0, y1), z + h),
              proud=h, mtl_key="tactile", exc="tactile", line="cross",
              area=True, albedo=TACTILE_ALBEDO_CAP, site=site,
              screen_w=abs(x1 - x0))], ik=r)


def _ik_ramp_curb(kit, path, profile, y_neg, y_pos, mtl, height=0.12,
                  width=0.30):
    """**GT 변경 1건 — 감독 결재 M4 로 W2 집행**(라벨은 W4 GT 맵).

    v1 표기의 `offset` 인자는 **존재하지 않는다** `[실측 — infra_kit.py:778-781]`.
    벽에서 띄우려면 `width` 를 줄이고 `y_neg/y_pos` 를 직접 준다.
    """
    n0 = kit.mark()
    r = ik.build_ramp_curb(kit, path, profile, y_neg, y_pos, mtl,
                           height=height, width=width, sides="both")
    xs = [p[0] for p in profile] + [profile[-1][0] + profile[-1][2]]
    zs = [p[1] for p in profile] + [profile[-1][1] - profile[-1][3]]
    elems = []
    for tag, yc in (("N", y_neg + width / 2.0), ("P", y_pos - width / 2.0)):
        elems.append(_elem("ramp_curb", f"{path}/Curb_{tag}",
                           (min(xs), yc - width / 2.0, min(zs),
                            max(xs), yc + width / 2.0, max(zs) + height),
                           proud=height, mtl_key="curb", line="long",
                           beyond=True, gt_change=True, exc="gt_change",
                           albedo=0.24))
    return dict(prim_count=kit.count_since(n0), elems=elems, ik=r,
                gt_changes=[dict(scene=None, item="ramp_curb",
                                 drop=float(r.get("gt_drop", height)),
                                 label_owner="W4",
                                 note="사양 §6.4 M4 — 연석은 W2 에서 만들고 "
                                      "낙차 라벨은 W4 GT 맵에서 붙인다")])


# ===========================================================================
# [5] 프로파일 18종 — 사양 §4.1 / §5 매트릭스
#
#     스키마: doc · natural · pave · infra · surface · extras · scatter ·
#             tactile(None 고정) · albedo_cap · prim_cap
#     `natural=True` 에 도시 인프라를 넣으면 plan_ground 가 ValueError.
# ===========================================================================
_URBAN_INFRA_KEYS = ("manhole", "gully", "gutter_L", "gutter_U", "marking",
                     "trench")


def _P(doc, natural=False, pave=None, infra=None, surface=(), extras=(),
       scatter=None, albedo_cap=ALBEDO_CAP, prim_cap=60, inst_cap=250):
    return dict(doc=doc, natural=bool(natural), pave=pave or {},
                infra=infra or {}, surface=tuple(surface),
                extras=tuple(extras), scatter=scatter, tactile=None,
                albedo_cap=float(albedo_cap), prim_cap=int(prim_cap),
                inst_cap=int(inst_cap))


GROUND_PROFILES = {
    # ── P1 ────────────────────────────────────────────────────────────────
    "plaza_granite": _P(
        "화강석 판석 광장 [규격 KCS 34 6-5-1]",
        pave=dict(module=(0.600, 0.600), joint="slab",
                  step_x=_dim("step_contraction_plaza"),
                  step_y=_dim("step_expansion_plaza")),
        infra=dict(manhole=2, gully=2),
        surface=(("patch", 2), ("crack", 4), ("stain", ("dirt", "water")),
                 ("weed", 6)),
    ),
    # ── P2 ────────────────────────────────────────────────────────────────
    "plaza_water": _P(
        "수변 계단광장(가트) — 자연 씬. 도시 인프라 0건 [결재 M3]",
        natural=True,
        pave=dict(module=(0.600, 0.600), joint="slab",
                  step_x=_dim("step_expansion_ghat"), step_y=None),
        surface=(("patch", 2), ("crack", 4), ("stain", ("water",))),
        extras=(("silt_band", dict(n=2)), ("edge_break", dict(density=10.0)),),
    ),
    # ── P3 ────────────────────────────────────────────────────────────────
    "sidewalk_block": _P(
        "보도·블록포장 [법령 보도블록 300 그리드]",
        pave=dict(module=(0.300, 0.300), joint="interlock",
                  step_x=3.0, step_y=None),
        infra=dict(manhole=1, gully=2, gutter_L=1),
        surface=(("patch", 2), ("crack", 4), ("stain", ("dirt", "gum")),
                 ("weed", 8)),
    ),
    # ── P4 ────────────────────────────────────────────────────────────────
    "street_asphalt": _P(
        "차도 접점 아스팔트 [법령 별표6]",
        pave=dict(module=(None, None), joint=None, step_x=None, step_y=None),
        infra=dict(manhole=1, gully=3, gutter_L=1, marking=("line",)),
        surface=(("patch", 3), ("crack", 6), ("stain", ("tire", "oil")),
                 ("weed", 4)),
    ),
    # ── P5 ────────────────────────────────────────────────────────────────
    "alley_concrete": _P(
        "골목 콘크리트 타설 포장 [통계 B 92 %]",
        pave=dict(module=(3.000, None), joint="contraction",
                  step_x=_dim("step_contraction_conc"), step_y=None,
                  groove_w=0.010, recess=-0.003),   # §3.4 스키마 예·§5.4 15-1
        infra=dict(manhole=1, gutter_U=1, trench=1),
        surface=(("patch", 2), ("crack", 4),
                 ("stain", ("grime_band", "dirt")), ("weed", 8)),
    ),
    # ── P6 ────────────────────────────────────────────────────────────────
    "roof_membrane": _P(
        "옥상 우레탄 도막방수(녹색) [결재 M2 알베도 0.16~0.22]",
        pave=dict(module=(None, None), joint=None, step_x=None, step_y=None),
        infra=dict(gully=2),
        surface=(("patch", 3), ("stain", ("water", "drip"))),
        extras=(("membrane", dict(wear_n=4)),),
    ),
    # ── P7 ────────────────────────────────────────────────────────────────
    "ramp_parking": _P(
        "지하주차 진입 램프 [법령 주차장법 §6①5다·마]",
        pave=dict(module=(None, None), joint="contraction",
                  step_x=3.0, step_y=None),
        infra=dict(manhole=1, trench=2, marking=("line", "line")),
        surface=(("patch", 2), ("crack", 6), ("stain", ("tire",)),
                 ("weed", 5)),
        extras=(("groove_band", dict()), ("ramp_curb", dict(height=0.12)),),
    ),
    # ── P8 ────────────────────────────────────────────────────────────────
    "ramp_road": _P(
        "옹벽 회랑 하향 램프 [시방 오목부 빗물받이 필수]",
        pave=dict(module=(None, None), joint=None, step_x=None, step_y=None),
        infra=dict(gully=6, gutter_L=2, marking=("line", "line")),
        surface=(("patch", 2), ("crack", 6), ("stain", ("tire", "dirt")),
                 ("weed", 4)),
    ),
    # ── P9 ────────────────────────────────────────────────────────────────
    "bridge_deck": _P(
        "교량·육교 상판 [추정 보도육교 관행]",
        pave=dict(module=(None, None), joint="expansion",
                  step_x=9.0, step_y=None),
        infra=dict(gully=4),
        surface=(("crack", 4), ("stain", ("water", "drip"))),
        extras=(("wear_lane", dict(width=0.75)),),
    ),
    # ── P10 ───────────────────────────────────────────────────────────────
    "deck_timber": _P(
        "목재 데크 [시방 KCS 34 5-2-1 2.3.1]",
        natural=True,
        pave=dict(module=(0.145, None), joint="plank",
                  step_x=None, step_y=None),
        surface=(("stain", ("dirt", "water")),),
        extras=(("deck_planks", dict()), ("silt_band", dict(n=1)),),
        prim_cap=140,
    ),
    # ── P11 ───────────────────────────────────────────────────────────────
    "trail_soil": _P(
        "마사토 산길 [통계 등산로 6/6]",
        natural=True,
        pave=dict(module=(None, None), joint=None, step_x=None, step_y=None),
        surface=(("stain", ("dirt",)),),
        extras=(("wear_lane", dict()), ("edge_litter", dict()),
                ("edge_break", dict(density=12.0)),),
        scatter=dict(kind="gravel", cover=0.18, count=250, expose=0.06),
        inst_cap=400,
    ),
    # ── P12 ───────────────────────────────────────────────────────────────
    "courtyard_dg": _P(
        "마사토 마당 3대역 [시방 KCS 34 6-3-1 3.1.2 역해석]",
        natural=True,
        pave=dict(module=(None, None), joint=None, step_x=None, step_y=None),
        surface=(("stain", ("dirt",)),),
        extras=(("wear_lane", dict(width=1.2)), ("edge_litter", dict()),
                ("edge_break", dict(density=10.0)),),
        scatter=dict(kind="gravel", cover=0.14, count=330, expose=0.06),
        inst_cap=400,
    ),
    # ── P13 ───────────────────────────────────────────────────────────────
    "levee_paved": _P(
        "둔치 포장(인터로킹) [규격 200×100]",
        pave=dict(module=(0.200, 0.100), joint="interlock",
                  step_x=3.0, step_y=None),
        infra=dict(manhole=1, gully=2, gutter_L=1),
        surface=(("patch", 4), ("crack", 5), ("stain", ("dirt", "water")),
                 ("weed", 6)),
        extras=(("wear_lane", dict()),),
    ),
    # ── P14 ───────────────────────────────────────────────────────────────
    "yard_industrial": _P(
        "하역 야드 [법령 산안규칙·추정]",
        pave=dict(module=(None, None), joint="contraction",
                  step_x=6.0, step_y=4.5),
        infra=dict(trench=1, marking=("line", "line")),
        surface=(("stain", ("tire", "oil", "dirt")),),
    ),
    # ── P15 ───────────────────────────────────────────────────────────────
    "slab_construction": _P(
        "공사 슬래브 [법령 산안규칙 §43 — 개구부 노면 도색]",
        pave=dict(module=(None, None), joint="contraction",
                  step_x=4.0, step_y=None),
        infra=dict(marking=("line",)),
        surface=(("stain", ("efflorescence", "dirt")),),
        extras=(("footprints", dict(n=12)),),
    ),
    # ── P16 ───────────────────────────────────────────────────────────────
    "platform_indoor": _P(
        "실내 승강장 [실측 — D4 하단 L_mu 0.069, 조명 선행(M8)]",
        pave=dict(module=(0.300, 0.300), joint="interlock",
                  step_x=3.0, step_y=None),
        surface=(("stain", ("dirt",)),),
        extras=(("wear_lane", dict(width=1.2)),),
    ),
    # ── P17 ───────────────────────────────────────────────────────────────
    "verge_rural": _P(
        "농촌 개거변 복개 슬래브 [시방 KCS 34 6-3]",
        natural=True,
        pave=dict(module=(None, None), joint="contraction",
                  step_x=2.0, step_y=None),
        surface=(("patch", 3), ("crack", 5), ("stain", ("dirt",)),
                 ("weed", 4)),
    ),
    # ── P18 (v1.1 신설) ───────────────────────────────────────────────────
    "deck_trail_hybrid": _P(
        "데크 진입부 + 공원 흙길 [실측 — 사양 §13. P10 오배정 폐기]",
        natural=True,
        pave=dict(module=(0.145, None), joint="plank",
                  step_x=None, step_y=None),
        surface=(("stain", ("dirt",)),),
        extras=(("deck_planks", dict(max_gaps=9)),
                ("edge_break", dict(density=12.0)),
                ("wear_lane", dict()), ("edge_litter", dict()),),
        scatter=dict(kind="gravel", cover=0.12, count=180, expose=0.06),
    ),
    # ── P3 하위변종 ────────────────────────────────────────────────────────
    "tunnel_under": _P(
        "지하보도(P3 하위변종) [추정 지하보도 관행]",
        pave=dict(module=(0.300, 0.300), joint="interlock",
                  step_x=3.0, step_y=None),
        infra=dict(gutter_U=1, trench=1),
        surface=(("stain", ("grime_band", "efflorescence")),),
    ),
}


# ===========================================================================
# [6] 점자블록 등록부 — 사양 §12.4. **여기 없으면 설치 금지**(게이트 B11)
#     GT 열은 전부 A(z 불변) — flush + 돌기 6 mm 는 낙차가 아니다 `[법령]`.
# ===========================================================================
def _T(kind, site, p, trigger, defect=None, relief="normal", walk_axis="x",
       note=""):
    return dict(kind=kind, site=site, p=float(p), trigger=trigger,
                defect=defect, relief=relief, walk_axis=walk_axis, note=note)


TACTILE_SITES = {
    # 신설 6씬
    "scene02": {"stair_top": _T("dot", "계단 상단 0.3 m 전 전폭", 0.54,
                                "계단 첫 단", note="완전 적정(부적정 미적용)"),
                "stair_foot": _T("dot", "하부 랜딩 대칭 1줄", 0.54, "계단 마지막 단")},
    "scene11": {"stair_top": _T("dot", "승강부 4개소 상단", 0.54, "계단 첫 단",
                                defect="방향 어긋남 15°"),
                "stair_foot": _T("dot", "승강부 4개소 하단", 0.54, "계단 마지막 단",
                                 defect="방향 어긋남 15°")},
    "scene01": {"stair_top": _T("dot", "상단 x −0.90…−0.30 전폭", 0.51,
                                "계단 첫 단", defect="색 바램·오염 −40 %")},
    "scene08": {"opening_ring": _T("dot", "개구 둘레 띠", 0.51, "개구 둘레",
                                   defect="부분 결손 2~3매")},
    "scene16": {"entrance": _T("dot", "건물 주출입구 전면 0.6×전폭", 0.54,
                               "주출입구", defect="점유·방해(자리만 비움)",
                               note="★ 낙차와 무관 — cue+/label− 사분면")},
    "scene13": {"bollard": _T("dot", "볼라드 전면 0.3 m", 0.54, "볼라드 전면",
                              defect="부분 결손 2~3매"),
                "stair_head": _T("dot", "보도 계단 상단", 0.54, "계단 첫 단",
                                 defect="부분 결손 2~3매"),
                "stair_foot": _T("dot", "보도 계단 하단", 0.54, "계단 마지막 단")},
    # 유지 3씬
    "sceneD4": {"platform_edge": _T("dot", "연단 0.30 m 이격 2열", 0.90,
                                    "승강장 연단", note="완전 적정")},
    "sceneC4": {"stair_top": _T("dot", "계단머리 경고 점형", 0.51, "계단 첫 단",
                                defect="위치 오류 0.6~1.0 m")},
    "sceneC1": {"stair_top": _T("dot", "계단머리 경고 점형", 0.51, "계단 첫 단",
                                defect="색 바램·오염 −40 %",
                                note="적설 0.05 m 에 매몰되는 것이 씬 특색")},
    # 볼라드 전면 유지 4씬(전부 무낙차 = cue+/label−)
    "sceneN1": {"bollard": _T("dot", "볼라드 전면 연속 띠 0.60", 0.54, "볼라드 전면")},
    "sceneN2": {"bollard": _T("dot", "볼라드 전면 연속 띠 0.60", 0.54, "볼라드 전면")},
    "sceneN4": {"bollard": _T("dot", "볼라드 전면 연속 띠 0.60", 0.54, "볼라드 전면")},
    # ★ 사양 충돌 1건 — §12.5 ③ 은 N5 1개소에 relief="geom" 을 허용하지만,
    #   dot geom 은 0.6×3.0 m 띠에 **721 프림**(§4.2)이고 N5 의 볼라드 열 전면
    #   연속 띠는 7.0 m 라 **1,706 프림** = §8.1 절대 상한 200 의 8.5배다.
    #   → W2 는 relief="normal"(프림 1) 로 집행하고, 36점 돌기의 음영은
    #     §12.5 ③ 처방대로 `tactile_yellow_diff/nor` 텍스처 배선(T1)으로 낸다.
    #     `relief_wanted` 에 원 의도를 남겨 감독 판단을 받는다.
    "sceneN5": {"bollard": _T("dot", "볼라드 열 전면 연속 띠 0.60", 0.54,
                              "볼라드 전면", relief="normal",
                              note="§12.5 ③ 의 relief='geom' 의도는 프림 절대상한 "
                                   "200(§8.1)과 비양립 — 텍스처 배선으로 대체")},
}

# 미설치 사유 원장 — "왜 안 놓았는가"를 코드가 기억한다(B11 진단 메시지에 쓴다)
TACTILE_OFF_REASON = {
    "scene06": "홀드 — 나선 계단 '전폭' 정의 모호(감독 판단, M10 과 함께)",
    "scene17": "p=0.24 미달 (둔치 공원)",
    "scene05": "p=0.24 미달", "scene09": "p 미달 + 자연 씬 도시 인프라 금지",
    "scene10": "p=0.24 미달 (공원)", "scene12": "자연 씬 도시 인프라 금지",
    "sceneC2": "p=0.24 미달", "scene03": "자연 씬", "scene04": "자연 씬",
    "scene07": "자연 씬",
    "scene14": "정체성 충돌 — 은닉 착시(cue_tactile 토글 무결성)",
    "scene20": "정체성 충돌 — 은닉 착시", "scene21": "정체성 충돌 — 은닉 착시",
    "sceneN3": "정체성 충돌 — 은닉 착시",
    "scene15": "p≈0.05 — 노후 골목 표본 0/12",
    "scene18": "파형 비정형 — 300 그리드 부설 미관행",
    "scene19": "민간 옥상 — 편의증진법 대상시설 아님",
    "sceneD1": "비대상(산업 야드). 미설치 사유를 코드에 명시한 모범 사례",
    "sceneD2": "비대상(공사장)", "sceneD3": "비대상(농촌 도로변)",
}


# ===========================================================================
# [7] EXPECTED_FP — GT-E2-x 등재 예외의 오탐 사전등록 (사양 §12.3)
#
#     라운드 판정기는 이 행 구간의 GRAZE 응답을 **신규 오탐으로 세지 않는다**.
#     행은 하드코드하지 않고 **법정 기하에서 계산**한다 — 씬마다 계단 전폭·
#     원점이 달라도 같은 규칙이 재현되도록.
#     등록 범위 = [에지 행, **그 컷의 이격 하한에 미달한 가장 먼 경계선 행**].
#     d2 는 자력 통과(Δ 42.9 @1080 = 21.4 @540 ≥ 16 @540)라 등재 불요.
#
#     ★ (v1.2) **소비자 축 정합** — 레드팀 G-1 따름. 이 등록부의 소비자는
#       GRAZE JSON(`gz_row`, 대역)이고 그쪽은 **@540** 이다. 등록부는 두 축을
#       모두 내보낸다: `rows`(=@1080, 사양 §12.3 표기 유지) + `rows_work`(@540).
#       라운드 판정기는 `rows_work` 를 쓸 것. 한 축만 보고 매칭하면 영원히
#       한 행도 일치하지 않는다.
# ===========================================================================
def tactile_fp_rows(dists=(2, 5, 10), h=0.3, setback=None, depth=None):
    """법정 점자블록 띠(에지 전방 `setback`, 폭 `depth`)의 오탐 등록 행 구간.

    반환 `{d: (lo_1080, hi_1080)}` — **@1080**. @540 은 `_fp_work()` 로 변환.
    """
    setback = _dim("tactile_setback") if setback is None else float(setback)
    depth = _dim("tactile_band_depth") if depth is None else float(depth)
    out = {}
    for d in dists:
        sep = graze_row_sep_1080(d, h)
        r_edge = cam_row(d, h)
        r_near = cam_row(d - setback, h)
        r_far = cam_row(d - setback - depth, h)
        fails = [r for r in (r_near, r_far) if abs(r - r_edge) < sep]
        if not fails:
            continue
        lo = min([r_edge] + fails)
        hi = max([r_edge] + fails)
        out[d] = (int(math.floor(lo)), int(math.ceil(hi)))
    return out


def _fp_work(rows_1080):
    """등록 구간을 GRAZE 소비자 축(@540)으로 옮기고 footprint 만큼 넓힌다."""
    lo, hi = rows_1080
    return (int(math.floor(to_work_rows(lo))) - GRAZE_FOOTPRINT_WORK,
            int(math.ceil(to_work_rows(hi))) + GRAZE_FOOTPRINT_WORK)


# 낙차 에지를 동반하는 법정 트리거 — 이 지점만 GRAZE 오탐 사전등록이 필요하다
_FP_TRIGGERS = ("계단 첫 단", "계단 마지막 단", "승강장 연단", "개구 둘레")


def _build_expected_fp():
    fp = {}
    rows = tactile_fp_rows()
    for scene, sites in TACTILE_SITES.items():
        for site, spec in sites.items():
            if spec["trigger"] not in _FP_TRIGGERS:
                continue          # 볼라드 전면·주출입구는 낙차 에지가 없다
            for d, (r0, r1) in rows.items():
                fp[(scene, f"preset_h0.3_d{d}")] = dict(
                    rows=(r0, r1), scale=CAM_H,          # @1080 (사양 §12.3)
                    rows_work=_fp_work((r0, r1)),        # @540  (GRAZE 소비자)
                    scale_work=GRAZE_WORK_H,
                    src=f"tactile_{site}")
    return fp


EXPECTED_FP = _build_expected_fp()


# ===========================================================================
# [8] 씬 고유 불변식 등록부 — 게이트 B12 (사양 §7.3)
#     `plan_ground` 가 전 요소 AABB 에 대해 호출하고, 하나라도 False 면 ValueError.
#     씬이 자기 검사기를 갖고 있으면(예: sceneN1.dresscheck) **재구현하지 말고**
#     `plan_ground(..., invariants=[...])` 로 주입받는다.
# ===========================================================================
def _inv_n1_band(elem, ctx):
    """N1 밴드 보존 — 오클루더는 공중 슬래브 단 하나여야 한다.
    `xb + 0.84536·h < 0.0`(앞배치) 또는 `xa > 4.0`(뒤배치)."""
    xa, _, _, xb, _, z1 = elem["aabb"]
    h = max(0.0, z1 - ctx.get("z", 0.0))
    return (xb + 0.84536 * h < 0.0) or (xa > 4.0)


def _inv_n3_painting(elem, ctx):
    """N3 트롱프뢰유 그림면 x ∈ [0, 6.3] 위 **면 요소 금지**(줄눈 관통은 의도)."""
    if not elem["meta"].get("area"):
        return True
    xa, _, _, xb, _, _ = elem["aabb"]
    return xb <= 0.0 or xa >= 6.3


def _inv_hidden_illusion(elem, ctx):
    """14·20·21·N3 은닉 착시 무결성 — 상시 고대비 단서 금지."""
    m = elem["meta"]
    if elem["kind"] == "tactile":
        return False
    if m.get("line") == "cross" and (m.get("albedo") or 0.0) > 0.28:
        return False
    return True


def _inv_13_ramp_d2only(elem, ctx):
    """13 램프 크레스트 은닉 — 램프 위 요소는 d2 에서만 [F] 여야 한다."""
    if not elem["meta"].get("beyond"):
        return True
    return tuple(elem["meta"].get("vis_dists", ())) in ((), (2,), (2.0,))


def _inv_10_trail_cut(elem, ctx):
    """10 상부 트레일은 x = −1.5 에서 끊긴다(계단 공동 위 지면 평면 금지)."""
    xa, _, za, xb, _, zb = elem["aabb"]
    if xb <= -1.5:
        return True
    return zb > -6.0 and elem["meta"].get("deck", False)


def _inv_c1_snow(elem, ctx):
    """C1 적설 매몰이 씬 특색 — 신규 요소 proud ≤ 눈 두께 0.05."""
    return elem["proud"] <= 0.05 + 1e-9


GROUND_INVARIANTS = {
    "sceneN1": [_inv_n1_band],
    "sceneN3": [_inv_n3_painting, _inv_hidden_illusion],
    "scene14": [_inv_hidden_illusion],
    "scene20": [_inv_hidden_illusion],
    "scene21": [_inv_hidden_illusion],
    "scene13": [_inv_13_ramp_d2only],
    "scene10": [_inv_10_trail_cut],
    "sceneC1": [_inv_c1_snow],
}


# ===========================================================================
# [9] plan_ground — 프로파일 → 계획 (순수 계산, USD 미접촉)
# ===========================================================================
def _edge_list(edges):
    """edges 정규화 → [(name, s, opts)]."""
    out = []
    for e in edges or ():
        if isinstance(e, dict):
            out.append((e.get("name", "edge"), float(e["s"]), dict(e)))
        elif len(e) >= 3:
            out.append((str(e[0]), float(e[1]), dict(e[2])))
        else:
            out.append((str(e[0]), float(e[1]), {}))
    return out


def _nearest_edge_gap(view, elem, edges):
    """요소 전방 s 구간과 에지 사이의 최소 전방 이격 [m]. 없으면 None.
    요소가 에지를 넘거나 걸치면 0.0."""
    if not edges:
        return None
    sa, sb = view.s_span(elem["aabb"])
    best = None
    for _n, se, _o in edges:
        if sa >= se:                       # 에지 너머 요소 — GT-E1′ 대상 아님
            continue
        gap = max(0.0, se - sb)
        best = gap if best is None else min(best, gap)
    return best


def _vis_dists(view, elem, edges, dists, h):
    """에지 너머(램프 노면 등) 요소의 가시 컷 판정. 광선기울기 h/d > 노면구배."""
    sa, _sb = view.s_span(elem["aabb"])
    for _n, se, opts in edges:
        g = opts.get("beyond_grade")
        if g is None or sa < se - 1e-9:
            continue
        return tuple(d for d in dists if (h / float(d)) > float(g) + 1e-9)
    return tuple(dists)


def plan_ground(profile, region, *, z=0.0, z_fn=None, gy=0.0,
                origin=(0.0, 0.0, 0.0), axis="+x", edges=(), voids=(),
                dists=(2, 5, 10), heights=(0.3,), overrides=None, seed=0,
                scene=None, tactile=(), invariants=None, sites=None,
                extras_args=None, caps=None):
    """프로파일 + 영역 → **GroundPlan**. USD 를 만들지 않는다.

    이 함수만으로 프림 수·GT·프레임 예산이 전부 판정 가능해야 한다 —
    `python3 ground_kit.py` 가 33씬 계획을 USD 접촉 전에 검산하기 위함이다.

    위반 시 `ValueError`:
      · `natural=True` 프로파일에 도시 인프라 (§3.4)
      · GT δ 초과(예외 미등록 요소) · GT-E1′(B6) · GT-E2(B7) · GT-V(B8)
      · 알베도 상한(B9) · 프림/인스턴스 예산(B10)
      · `TACTILE_SITES` 미등재 점자블록(B11) · 씬 고유 불변식(B12)
    """
    if profile not in GROUND_PROFILES:
        raise ValueError(f"ground_kit: 미등록 프로파일 '{profile}'. "
                         f"등록: {sorted(GROUND_PROFILES)}")
    prof = dict(GROUND_PROFILES[profile])
    if overrides:
        for k, v in dict(overrides).items():
            if isinstance(v, dict) and isinstance(prof.get(k), dict):
                d = dict(prof[k]); d.update(v); prof[k] = d
            else:
                prof[k] = v

    # ── §3.4 규약 강제: 자연 씬 도시 인프라 금지 ────────────────────────
    if prof["natural"]:
        bad = [k for k in _URBAN_INFRA_KEYS if prof["infra"].get(k)]
        if bad:
            raise ValueError(
                f"ground_kit: natural=True 프로파일 '{profile}' 에 도시 인프라 "
                f"{bad} 를 넣을 수 없다. 자연 씬(03·04·07·09·12·D3·10) 규약 — "
                "코드가 강제한다(사양 §3.4·§5.7).")
    if prof.get("tactile") is not None:
        raise ValueError("ground_kit: 프로파일 tactile 은 None 고정. "
                         "점자블록은 TACTILE_SITES 로만 들어온다(§3.4).")

    view = _View(origin, gy, axis)
    ed = _edge_list(edges)
    reg = _norm_region(region)
    h0 = float(heights[0]) if heights else 0.3
    ctx = dict(profile=profile, region=reg, z=float(z), gy=float(gy),
               origin=tuple(origin), axis=axis, dists=tuple(dists),
               heights=tuple(heights), edges=ed,
               voids=[_norm_region(v) for v in (voids or ())],
               scene=scene, seed=int(seed), caps=dict(caps or {}))

    # ── 계획 = ops 목록. dry 실행으로 elems·프림 수를 얻는다 ─────────────
    ops = _compose_ops(profile, prof, ctx, tactile, sites or {},
                       extras_args or {})
    dk = dry_kit()
    elems, prims, mats, scat_reqs, gt_changes = [], 0, [], [], []
    for op in ops:
        r = op["fn"](dk, op["path"], *op.get("args", ()), **op.get("kw", {}))
        op["prim_count"] = r.get("prim_count", 0)
        prims += op["prim_count"]
        for e in r.get("elems", ()):
            e["meta"].setdefault("op", op["name"])
            elems.append(e)
        mats.extend(r.get("material_req", ()))
        for s in r.get("scatter_req", ()):
            scat_reqs.append(s)
        for g in r.get("gt_changes", ()):
            g = dict(g); g["scene"] = scene
            gt_changes.append(g)

    # 산포(프로파일 선언 + edge_break 요청) — `scatter_debris` 콜백 위임
    inst = 0
    sc_spec = prof.get("scatter")
    if sc_spec:
        inst += int(sc_spec.get("count", 0))
    inst += sum(int(s.get("count", 0)) for s in scat_reqs)

    # ── 가시 컷 · GT-E5 클램프 ─────────────────────────────────────────
    for e in elems:
        e["meta"]["vis_dists"] = _vis_dists(view, e, ed, dists, h0)
        e["meta"]["edge_gap"] = _nearest_edge_gap(view, e, ed)
        sa, _sb = view.s_span(e["aabb"])
        if any(o.get("beyond_grade") is not None and sa >= se - 1e-9
               for _n, se, o in ed):
            e["meta"]["beyond"] = True         # 램프 노면 위 = d2 전용 (§5.0 C-2)

    _clamp_gt_e5(elems, view, ed)

    plan = dict(profile=profile, scene=scene, elements=elems,
                materials_needed=mats, scatter_req=scat_reqs,
                prims=prims, instances=inst, ops=ops,
                gt=dict(delta=GT_DELTA), gt_changes=gt_changes, ctx=ctx,
                unit_cell=GROUND_DIMENSIONS["unit_cell"].get(profile))
    _assert_unit_cell(profile, prof)

    # ── 게이트 (B6~B12 하드) ───────────────────────────────────────────
    b = frame_budget(plan, h=h0, dists=dists)
    plan["budget"] = b
    hard = [k for k in ("B6", "B7", "B8", "B9", "B10", "B11", "B12")
            if not b["gates"][k]["pass"]]
    if hard:
        msgs = "\n  ".join(f"{k}: {b['gates'][k]['detail']}" for k in hard)
        raise ValueError(f"ground_kit: plan_ground 게이트 위반 "
                         f"[{profile}/{scene}]\n  {msgs}")

    # B12 — 씬 고유 불변식(등록부 + 씬 주입 콜백)
    invs = list(GROUND_INVARIANTS.get(scene or "", ()))
    invs += list(invariants or ())
    for fn in invs:
        for e in elems:
            if not fn(e, ctx):
                raise ValueError(
                    f"ground_kit: B12 씬 고유 불변식 위반 — {scene} / "
                    f"{getattr(fn, '__name__', fn)} / {e['path']}")
    plan["gt"]["delta_max"] = max([abs(e["proud"]) for e in elems] or [0.0])
    return plan


def _assert_unit_cell(profile, prof):
    """§4.5 U1~U4 — T1 유닛 지터 계약 정합. 위반은 ValueError."""
    uc = GROUND_DIMENSIONS["unit_cell"].get(profile)
    if uc is None:
        raise ValueError(f"ground_kit: unit_cell 원장에 '{profile}' 미등재 "
                         "(§4.5 역방향 계약 불이행).")
    cell, orig, _src = uc
    mod = prof["pave"].get("module", (None, None))
    mx = mod[0] if mod else None
    if cell is None:
        if mx:
            raise ValueError(f"U1 위반: '{profile}' 은 pave.module={mx} 를 "
                             "저작했는데 unit_cell=None 이다.")
        return
    if mx is not None and abs(float(mx) - float(cell)) > 1e-9:
        raise ValueError(f"U1 위반: '{profile}' pave.module={mx} ≠ "
                         f"unit_cell={cell} — 이중 격자가 생긴다.")
    for key in ("step_x", "step_y"):
        st = prof["pave"].get(key)
        if not st:
            continue
        k = float(st) / float(cell)
        if abs(k - round(k)) > 1e-6:
            raise ValueError(f"U2 위반: '{profile}' {key}={st} 는 "
                             f"unit_cell={cell} 의 정수배가 아니다(×{k:.3f}).")
    if orig is None:
        raise ValueError(f"U3 위반: '{profile}' unit_cell_origin 이 없다 — "
                         "주기만 넘기면 계약 불이행(MDL 기본 원점은 UV 원점).")


def _clamp_gt_e5(elems, view, edges):
    """GT-E5 램프 — 식생·산포는 에지에 가까울수록 낮아진다(금지가 아니라 클램프).

    `z_e ≤ min(요소종별 상한, |x_e| / EDGE_K)`. 클램프 후에도 종별 최소치를
    못 맞추면 드롭 표시(`meta["dropped"]=True`).
    """
    for e in elems:
        exc = e["meta"].get("exc")
        if exc not in ("weed", "scatter"):
            continue
        gap = e["meta"].get("edge_gap")
        if gap is None:
            continue
        zmax = gap / EDGE_K
        if e["proud"] > zmax + 1e-12:
            e["meta"]["clamped_from"] = e["proud"]
            e["proud"] = max(0.0, zmax)
            x0, y0, z0, x1, y1, _z1 = e["aabb"]
            e["aabb"] = (x0, y0, z0, x1, y1, z0 + e["proud"])
            if e["proud"] < 0.005:
                e["meta"]["dropped"] = True


# ===========================================================================
# [10] frame_budget — 렌더 없이 B1~B12 판정 (사양 §7.1)
# ===========================================================================
def _gate(ok, detail, hard=True):
    return dict(**{"pass": bool(ok)}, detail=detail, hard=bool(hard))


def frame_budget(plan, *, h=0.3, dists=None, gy=None, origin=None):
    """각 h0.3 컷의 요소 픽셀 점유·차폐·GT 규칙 위반을 렌더 없이 판정한다.

    B1~B5 는 **프레임 충전 목표**(WARN — 최종 판정은 렌더 후 σ_LF/sd),
    B6~B12 는 **하드 게이트**(위반 시 `plan_ground` 가 예외).
    """
    ctx = plan["ctx"]
    dists = tuple(dists or ctx["dists"])
    view = _View(origin or ctx["origin"], ctx["gy"] if gy is None else gy,
                 ctx["axis"])
    edges = ctx["edges"]
    elems = plan["elements"]
    prof = GROUND_PROFILES[plan["profile"]]

    per_cut = {}
    b1 = b3 = b4 = b5 = 0
    b2 = 0.0
    e1_viol, e2_viol, e2_lines = [], [], {}

    for d in dists:
        area_w1, area_wpx, cross_ok, long_ok, decal_n = 0, 0.0, 0, 0, 0
        e_lo, e_hi = GRAZE_E_BAND[0] * d, GRAZE_E_BAND[1] * d
        # 에지의 지면거리 = d + s_edge (표준 규약에서 에지 s=0 → 정확히 d).
        # 원점이 다른 씬도 `edges` 를 전방 s 로 주므로 같은 식이 성립한다.
        r_edge = {name: cam_row(d + se, h) for name, se, _o in edges}
        singular = []
        for e in elems:
            if e["meta"].get("dropped"):
                continue
            if d not in e["meta"].get("vis_dists", dists):
                continue
            sa, sb = view.s_span(e["aabb"])
            ta, tb = view.t_span(e["aabb"])
            Xa, Xb = d + sa, d + sb
            if Xb <= 0.05:
                continue
            Xm = max(0.05, (Xa + Xb) / 2.0)
            hw = cam_halfwidth(Xm)
            # 프레임 밖 판정은 **두 에지가 같은 쪽으로** 벗어난 경우만이다.
            # `min(|ta|,|tb|) > hw` 로 쓰면 화면을 가로지르는 전폭 요소(트렌치·
            # 점자블록 띠)가 통째로 탈락한다 — 실제로 scene13 d2 가 그랬다.
            if (ta - view.gy) > hw or (tb - view.gy) < -hw:
                continue
            m = e["meta"]
            in_w1 = (NEAR_W1[0] <= Xm <= NEAR_W1[1])
            if m.get("area"):
                w = float(m.get("screen_w") or min(abs(tb - ta), 2 * hw))
                if in_w1:
                    area_w1 += 1
                    area_wpx += cam_wpx(w, Xm)
            if m.get("decal") and Xm <= 3.0:
                decal_n += 1
            if m.get("line") in ("cross", "cross_periodic"):
                if cam_lpx(max(1e-3, abs(sb - sa)), Xm, h) >= 2.0:
                    cross_ok += 1
            if m.get("line") == "long":
                if cam_wpx(max(1e-3, abs(tb - ta)), 5.0) >= 2.0:
                    long_ok += 1
            # ── B6 GT-E1′ ────────────────────────────────────────────
            gap = m.get("edge_gap")
            z_e = e["proud"]
            if m.get("exc") == "plank_gap":
                z_e = 0.0            # 판재 틈 = 음각. §6.1 예외표 "필요 이격 0"
            if gap is not None and z_e > 0:
                need = EDGE_K * z_e
                if gap + 1e-9 < need and m.get("exc") != "tactile":
                    e1_viol.append((e["path"], round(gap, 3), round(need, 3)))
                elif m.get("exc") == "tactile" and gap + 1e-9 < need:
                    e1_viol.append((e["path"], round(gap, 3), round(need, 3)))
            # ── B7 GT-E2 (E 대역 안 전폭 횡단선) ──────────────────────
            if m.get("line") in ("cross", "cross_periodic") and r_edge:
                if m.get("exc") == "plank_gap":
                    continue         # 음각 판재 틈은 GT-E2 대상이 아니다(§6.1)
                if not (e_lo <= Xm <= e_hi):
                    continue
                surf = m.get("surface_z", 0.0)
                # 행은 전부 **@1080**(`cam_row` 축). 판정 하한도 같은 축으로
                # 맞춘 뒤 비교한다 — v1.1 은 @540 유도값을 @1080 과 직접 비교했다.
                rows = [cam_row_z(max(0.05, d + s), surf, h) for s in (sa, sb)]
                worst = None
                for _nm, se, _o in edges:
                    re_ = cam_row(d + se, h)
                    dd = min(abs(r - re_) for r in rows)
                    worst = dd if worst is None else min(worst, dd)
                sep = graze_row_sep_1080(d, h)
                if worst is not None and worst < sep:
                    if m.get("exc") == "tactile":
                        key = (ctx.get("scene"), f"preset_h{h}_d{d}")
                        if key not in EXPECTED_FP:
                            e2_viol.append((e["path"], d, round(worst, 2),
                                            "GT-E2-x 미등재"))
                    else:
                        e2_viol.append((
                            e["path"], d, round(worst, 2),
                            f"Δ {worst:.1f}@1080 = {to_work_rows(worst):.1f}@540 "
                            f"< {sep:.0f}@1080"))
                if m.get("line") == "cross":
                    singular.append(e["path"])
        e2_lines[d] = singular
        if len(singular) > 1:
            e2_viol.append((",".join(singular), d, len(singular),
                            "E 대역 전폭 횡단 단선 2본 이상"))
        per_cut[d] = dict(area_w1=area_w1, area_wpx=round(area_wpx, 1),
                          area_pct=round(100.0 * area_wpx / CAM_W, 2),
                          cross=cross_ok, long=long_ok, decal=decal_n,
                          singular=len(singular))
        b1 = max(b1, area_w1); b2 = max(b2, 100.0 * area_wpx / CAM_W)
        b3 = max(b3, cross_ok); b4 = max(b4, long_ok); b5 = max(b5, decal_n)

    # ── B8 GT-V : 요소 AABB × 개구 교차 0 ────────────────────────────
    v_hits = []
    for e in elems:
        if e["meta"].get("dropped"):
            continue
        x0, y0, _z0, x1, y1, _z1 = e["aabb"]
        for vx0, vy0, vx1, vy1 in ctx["voids"]:
            if x1 > vx0 and x0 < vx1 and y1 > vy0 and y0 < vy1:
                v_hits.append((e["path"], (vx0, vy0, vx1, vy1)))
    # ── B9 알베도 ────────────────────────────────────────────────────
    a_hits = []
    for e in elems:
        a = e["meta"].get("albedo")
        if a is None:
            continue
        cap = TACTILE_ALBEDO_CAP if e["meta"].get("exc") == "tactile" \
            else prof["albedo_cap"]
        if a > cap + 1e-9:
            a_hits.append((e["path"], a, cap))
    # ── B10 예산 ─────────────────────────────────────────────────────
    over = []
    if plan["prims"] > prof["prim_cap"]:
        over.append(f"기하 프림 {plan['prims']} > {prof['prim_cap']}")
    if plan["prims"] > 200:
        over.append(f"절대 상한 200 초과 ({plan['prims']})")
    if plan["instances"] > prof["inst_cap"]:
        over.append(f"산포 {plan['instances']} > {prof['inst_cap']}")
    # ── B11 점자블록 무단 배치 ────────────────────────────────────────
    t_hits = []
    for e in elems:
        if e["kind"] != "tactile":
            continue
        site = e["meta"].get("site")
        reg = TACTILE_SITES.get(ctx.get("scene") or "", {})
        if site not in reg:
            t_hits.append((e["path"], ctx.get("scene"), site,
                           TACTILE_OFF_REASON.get(ctx.get("scene") or "",
                                                  "미등재")))

    gates = {
        "B1": _gate(b1 >= 1, f"W1 면 요소 {b1} (≥1)", hard=False),
        "B2": _gate(b2 >= 20.0, f"면 요소 화면폭 {b2:.1f} % (≥20)", hard=False),
        "B3": _gate(b3 >= 1, f"횡단선 L_px≥2 {b3}본 (≥1)", hard=False),
        "B4": _gate(b4 >= 2, f"종단선 W_px≥2@5m {b4}본 (≥2)", hard=False),
        "B5": _gate(b5 >= 6, f"오염 데칼(X≤3) {b5} (≥6)", hard=False),
        "B6": _gate(not e1_viol, f"GT-E1′ 위반 {len(e1_viol)}: {e1_viol[:3]}"),
        "B7": _gate(not e2_viol, f"GT-E2 위반 {len(e2_viol)}: {e2_viol[:3]}"),
        "B8": _gate(not v_hits, f"GT-V 개구 교차 {len(v_hits)}: {v_hits[:3]}"),
        "B9": _gate(not a_hits, f"알베도 초과 {len(a_hits)}: {a_hits[:3]}"),
        "B10": _gate(not over, "; ".join(over) or
                     f"프림 {plan['prims']}/{prof['prim_cap']} · "
                     f"산포 {plan['instances']}/{prof['inst_cap']}"),
        "B11": _gate(not t_hits, f"점자블록 무단 {len(t_hits)}: {t_hits[:2]}"),
        "B12": _gate(True, "씬 고유 불변식 — plan_ground 가 콜백으로 검사"),
    }
    return dict(gates=gates, per_cut=per_cut,
                warn=[k for k, g in gates.items()
                      if not g["pass"] and not g["hard"]],
                fail=[k for k, g in gates.items() if not g["pass"] and g["hard"]])


# ===========================================================================
# [11] apply_ground — 계획 → USD (계층 3)
# ===========================================================================
def apply_ground(kit, prefix, plan, mtls, *, skin_exclude=None, scatter=None,
                 slabs=()):
    """계획을 실제 USD 프림으로 만든다.

    `skin_exclude`: `scene_common.skin_exclude` 콜백 **주입**(scene_common
      미의존 원칙 유지 — 사양 §1.2). ground_kit 이 장식하는 지면 슬래브 경로를
      `slabs` 로 받아 스킨 대상에서 **명시 제외**한다(P-A). 이것이 선행되지
      않으면 flush 요소(맨홀 2 mm·점형블록 4 mm)가 스킨(+6.5~16.5 mm)에 묻힌다.

    반환: `{"prims", "instances", "elements", "gt_delta_max", "gt_changes"}`
    """
    if GKIT_PATH_TOKEN not in str(prefix):
        raise ValueError(f"ground_kit: prefix 는 '{{ROOT}}/{GKIT_PATH_TOKEN}' "
                         f"이어야 한다(2차 스킨 방어, §1.2). 받은 값: {prefix}")
    # ── P-A: 대상 슬래브 스킨 OFF ─────────────────────────────────────
    if skin_exclude is not None and slabs:
        skin_exclude(*[str(s) for s in slabs])

    # ── GT δ 사전 검사 — **생성 전에** 던진다 ─────────────────────────
    gmax, gchange_max = 0.0, 0.0
    for e in plan["elements"]:
        if e["meta"].get("dropped"):
            continue
        exc = e["meta"].get("exc")
        z = abs(e["proud"])
        if exc is None and z > GT_DELTA + 1e-9:
            raise ValueError(f"ground_kit: GT δ 초과(예외 미등록) {e['path']} "
                             f"z={z:.4f} > {GT_DELTA}")
        if exc == "gt_change":
            # **승인된 GT 변경**만 δ 를 넘을 수 있다(현재 대상: scene13 램프 연석
            # h0.12, 감독 결재 M4). 반드시 `gt_changes` 원장에 실려 있어야 한다 —
            # 라벨 없는 낙차를 조용히 만드는 것을 구조적으로 막는다(§6.4).
            if not plan["gt_changes"]:
                raise ValueError(
                    f"ground_kit: GT 변경 요소 {e['path']} 가 gt_changes 원장에 "
                    "없다. 승인 없는 낙차 신설은 금지(§6.4).")
            gchange_max = max(gchange_max, z)
            continue
        gmax = max(gmax, z)

    # ── 알베도 하드클램프 (§3.1) ──────────────────────────────────────
    prof = GROUND_PROFILES[plan["profile"]]
    for e in plan["elements"]:
        a = e["meta"].get("albedo")
        cap = TACTILE_ALBEDO_CAP if e["meta"].get("exc") == "tactile" \
            else prof["albedo_cap"]
        if a is not None and a > cap + 1e-9:
            raise ValueError(f"ground_kit: 알베도 상한 초과 {e['path']} "
                             f"{a} > {cap} (순백 대면적 금지 규약).")

    n_prims = 0
    for op in plan["ops"]:
        kw = dict(op.get("kw", {}))
        # mtl_key → 실제 재질 객체로 치환
        for k in list(kw):
            if k in ("mtl", "mtl_frame", "mtl_cover") and isinstance(kw[k], str):
                kw[k] = mtls.get(kw[k])
            if k == "mtls" and isinstance(kw[k], dict):
                kw[k] = {kk: mtls.get(vv) if isinstance(vv, str) else vv
                         for kk, vv in kw[k].items()}
        args = tuple(mtls.get(a[1:]) if (isinstance(a, str) and
                                         a.startswith("@")) else a
                     for a in op.get("args", ()))
        # ── 미치환 재질 참조 가드 (파일럿 1회차 크래시 재발 방지) ────────
        #    치환 후에도 "@" 문자열이나 **값이 전부 문자열인 사전**이 남아
        #    있으면 그건 빌더가 그대로 `Bind()` 에 넘길 재질 키다 → 즉시 던진다.
        #    `dry_kit` 은 Bind 를 하지 않아 CPU 자기검산이 이 결함을 못 본다.
        def _unresolved(v):
            if isinstance(v, str) and v.startswith("@"):
                return True
            return (isinstance(v, dict) and len(v) > 0
                    and all(isinstance(x, str) for x in v.values()))
        bad = [f"arg[{i}]={v!r}" for i, v in enumerate(args) if _unresolved(v)]
        bad += [f"{k}={v!r}" for k, v in kw.items() if _unresolved(v)]
        if bad:
            raise ValueError(
                f"ground_kit: op '{op['name']}' 에 미치환 재질 참조가 남았다 "
                f"{bad} — 재질 사전은 kw `mtls=`, 단일 재질은 '@키' 또는 "
                f"kw `mtl*=` 로만 넘길 수 있다(apply_ground 치환 규칙).")
        m0 = kit.mark()
        op["fn"](kit, f"{prefix}/{op['path'].lstrip('/')}", *args, **kw)
        n_prims += kit.count_since(m0)

    # ── 산포 — `scene_common.scatter_debris` 콜백 위임 (신규 함수 금지) ──
    n_inst = 0
    if scatter is not None:
        stage = getattr(kit, "stage", None)
        for i, s in enumerate(plan["scatter_req"]):
            (ax, ay), (bx, by) = s["line"]
            w = float(s["width"]) / 2.0
            n = scatter(stage, f"{prefix}/Scatter_Edge_{i}",
                        min(ax, bx) - w, min(ay, by) - w,
                        max(ax, bx) + w, max(ay, by) + w,
                        plan["ctx"]["z"], cover=0.10,
                        seed=det_seed("gkit.scatter", prefix, i),
                        edge_bias=float(s.get("edge_bias", 0.0)),
                        max_count=int(s["count"]))
            n_inst += int(n or 0)
        sp = GROUND_PROFILES[plan["profile"]].get("scatter")
        if sp:
            x0, y0, x1, y1 = plan["ctx"]["region"]
            n = scatter(stage, f"{prefix}/Scatter_Field", x0, y0, x1, y1,
                        plan["ctx"]["z"], cover=float(sp.get("cover", 0.15)),
                        seed=det_seed("gkit.scatter.field", prefix),
                        max_count=int(sp.get("count", 0)))
            n_inst += int(n or 0)

    return dict(prims=n_prims, instances=n_inst,
                elements=plan["elements"], gt_delta_max=gmax,
                gt_change_max=gchange_max,
                gt_changes=plan["gt_changes"],
                materials_needed=plan["materials_needed"],
                unit_cell=plan["unit_cell"])


# ===========================================================================
# [12] 씬 통합 보조 — §7.4 "좌표의 진실 원천은 씬 PARAMS"
# ===========================================================================
def region_from_params(params, key, pad=0.0):
    """씬 `PARAMS[key]` 의 x0/x1/y0/y1 을 region 으로. 문서 좌표 하드코드 금지."""
    d = params[key]
    return (float(d["x0"]) - pad, float(d["y0"]) - pad,
            float(d["x1"]) + pad, float(d["y1"]) + pad)


def edges_from_params(params, specs):
    """`specs = [(name, key, field, opts?), ...]` → plan_ground(edges=...)."""
    out = []
    for sp in specs:
        name, key, field = sp[0], sp[1], sp[2]
        opts = sp[3] if len(sp) > 3 else {}
        out.append((name, float(params[key][field]), dict(opts)))
    return out


# ===========================================================================
# [13] ops 조립 — 프로파일 처방 → 빌더 호출 목록
# ===========================================================================
def _op(name, fn, path, args=(), kw=None):
    return dict(name=name, fn=fn, path=path, args=tuple(args), kw=dict(kw or {}))


def _edge_guard_ticks(ctx, step, origin_x):
    """에지 전방에서 GT-E2(Δ≥16행)를 못 맞추는 횡단 줄눈 좌표를 걸러낸다.

    사양 §5.4 15-1 "x=0 제외(에지 금지대)"의 일반화. 주기 격자라도 **에지에
    붙은 한 줄**은 에지 신호를 오염시킨다 — 그 줄만 드롭한다.
    """
    if not step or not ctx["edges"]:
        return []
    x0, _y0, x1, _y1 = ctx["region"]
    skip = []
    i0 = int(math.ceil((x0 - origin_x) / step - 1e-9))
    i1 = int(math.floor((x1 - origin_x) / step + 1e-9))
    for i in range(i0, i1 + 1):
        xx = origin_x + i * step
        bad = False
        for _n, se, _o in ctx["edges"]:
            for d in ctx["dists"]:
                h0 = ctx["heights"][0]
                if abs(drow(xx - se, d, h0)) < graze_row_sep_1080(d, h0) \
                        and (0.7 * d) <= (d + xx - se) <= (2.2 * d):
                    bad = True
        if bad:
            skip.append(xx)
    return skip


def _trim_region(ctx, region, standoff=EDGE_STANDOFF):
    """에지 전방 금지대(GT-E1′ 기본 이격)만큼 **배치 영역 자체를** 자른다.

    난수 배치 요소(패치·균열·오염·잡초)가 에지에 우연히 붙는 것을 사후 게이트로
    잡으면 계획이 통째로 깨진다. 사양 §2.2 처방 제1원칙("근경 창을 채운다")과도
    맞으므로 **영역 단계에서** 잘라 둔다. 음각 요소(줄눈)는 이 함수를 안 쓴다.
    """
    x0, y0, x1, y1 = _norm_region(region)
    if not ctx["edges"]:
        return (x0, y0, x1, y1)
    view = _View(ctx["origin"], ctx["gy"], ctx["axis"])
    fx, fy = view.fwd
    for _n, se, _o in ctx["edges"]:
        lim = se - float(standoff)          # 전방 s 상한
        if abs(fx) > 0.5:                   # 진행축 = ±X
            wx = view.origin[0] + lim * fx
            if fx > 0:
                x1 = min(x1, wx)
            else:
                x0 = max(x0, wx)
        else:                               # 진행축 = ±Y
            wy = view.origin[1] + lim * fy
            if fy > 0:
                y1 = min(y1, wy)
            else:
                y0 = max(y0, wy)
    if x1 - x0 < 0.30 or y1 - y0 < 0.30:
        raise ValueError(
            f"ground_kit: 에지 금지대 {standoff} m 를 빼면 배치 영역이 남지 않는다 "
            f"(region={region}). region 을 에지 전방으로 더 넓게 잡아라.")
    return (x0, y0, x1, y1)


def _compose_ops(profile, prof, ctx, tactile_sites, sites, extras_args):
    """프로파일 처방 → 빌더 호출 목록. 좌표는 region·edges 에서 유도한다."""
    x0, y0, x1, y1 = ctx["region"]
    # 표면 요소(양각)는 에지 금지대를 뺀 영역에만 놓는다. 줄눈(음각)은 전 영역.
    sx0, sy0, sx1, sy1 = _trim_region(ctx, ctx["region"])
    z = ctx["z"]
    seed = ctx["seed"]
    ops = []
    uc = GROUND_DIMENSIONS["unit_cell"].get(profile) or (None, (0.0, 0.0), "")
    ox, oy = (uc[1] or (0.0, 0.0))

    # ── 포장 줄눈 ─────────────────────────────────────────────────────
    pv = prof["pave"]
    jkind = pv.get("joint")
    if jkind in ("slab", "contraction", "expansion", "interlock"):
        skip = _edge_guard_ticks(ctx, pv.get("step_x"), ox)
        fn = build_slab_joints if jkind == "slab" else build_joint_grid
        kw = dict(step_x=pv.get("step_x"), step_y=pv.get("step_y"),
                  seed=seed, origin_xy=(ox, oy), skip_x=skip)
        if pv.get("groove_w"):
            kw["width"] = pv["groove_w"]
        if pv.get("recess"):
            kw["recess"] = pv["recess"]
        if jkind != "slab":
            kw["kind"] = jkind
        ops.append(_op("joints", fn, "Joints",
                       args=((x0, y0, x1, y1), z, "@joint"), kw=kw))

    # ── infra (자연 씬은 위에서 이미 차단됨) ────────────────────────────
    inf = prof["infra"]
    for i in range(int(inf.get("manhole", 0))):
        site = (sites.get("manhole") or [])[i:i + 1]
        cx, cy = site[0] if site else (x1 - 1.15 - 3.0 * i, y0 + 0.35)
        ops.append(_op(f"manhole{i}", _ik_manhole, f"Manhole_{i}",
                       args=(cx, cy, z, "@manhole")))
    for i in range(int(inf.get("gully", 0))):
        site = (sites.get("gully") or [])[i:i + 1]
        cx, cy = site[0] if site else (x0 + 2.0 + 22.0 * i, y0 + 0.30)
        ops.append(_op(f"gully{i}", _ik_gully, f"Gully_{i}",
                       args=(cx, cy, z, "@gully")))
    for i in range(int(inf.get("gutter_L", 0))):
        yy = y0 + 0.15 if i == 0 else y1 - 0.15
        ops.append(_op(f"gutterL{i}", _ik_gutter_l, f"GutterL_{i}",
                       args=(x0, yy, x1, yy, z, "@gutter")))
    for i in range(int(inf.get("gutter_U", 0))):
        yy = (sites.get("gutter_U") or [y0 + 0.15])[i]
        ops.append(_op(f"gutterU{i}", build_gutter_U, f"GutterU_{i}",
                       args=(x0, yy, x1, yy, z), kw=dict(mtl="gutter")))
    for i in range(int(inf.get("trench", 0))):
        st = (sites.get("trench") or [])[i:i + 1]
        if st:
            tx, ty0, ty1 = st[0]
        else:
            tx, ty0, ty1 = x0 + 1.0 + 4.0 * i, y0, y1
        ops.append(_op(f"trench{i}", build_trench_drain, f"Trench_{i}",
                       args=(tx, ty0, tx, ty1, z), kw=dict(mtl="trench")))
    for i, kind in enumerate(inf.get("marking", ())):
        st = (sites.get("marking") or [])[i:i + 1]
        st0 = st[0] if st else None
        mx, my, yaw = (st0[0], st0[1], st0[2]) if st0 else \
            (sx0 + 0.5, sy0 + 0.6 + 1.2 * i, 0.0)
        Lm = float(st0[3]) if (st0 and len(st0) > 3) \
            else max(1.0, min(6.0, sx1 - mx - 0.2))
        ops.append(_op(f"marking{i}", _ik_marking, f"Marking_{i}",
                       args=(kind, "@marking", mx, my, z),
                       kw=dict(yaw_deg=yaw, length=Lm)))

    # ── 표면 처방 ─────────────────────────────────────────────────────
    for item in prof["surface"]:
        what = item[0]
        if what == "patch":
            # ★ 재질 사전은 **반드시 kw `mtls=` 로** 넘긴다. 위치인자로 넘기면
            #   `apply_ground` 의 치환 규칙(@문자열 / kw mtl* / kw mtls)에
            #   걸리지 않아 빌더가 `"patch"` **문자열**을 그대로 Bind 에 넘긴다
            #   — dry_kit 은 Bind 를 안 하므로 CPU 자기검산이 못 잡는다
            #   `[실측 — sceneN5 파일럿 1회차 크래시]`.
            ops.append(_op("patch", build_patch_field, "Patch",
                           args=((sx0, sy0, sx1, sy1), z),
                           kw=dict(mtls=dict(patch="patch",
                                             patch_cut="patch_cut"),
                                   n=item[1], seed=seed,
                                   sites=sites.get("patch"))))
        elif what == "crack":
            ops.append(_op("crack", build_crack_lines, "Crack",
                           args=((sx0, sy0, sx1, sy1), z, "@crack"),
                           kw=dict(n=item[1], seed=seed)))
        elif what == "stain":
            for kind in item[1]:
                ops.append(_op(f"stain_{kind}", build_stain_field,
                               f"Stain_{kind}",
                               args=((sx0, sy0, sx1, sy1), z,
                                     f"@stain_{kind}"),
                               kw=dict(kind=kind,
                                       n=2 if kind == "grime_band" else 4,
                                       seed=seed)))
        elif what == "weed":
            ops.append(_op("weed", _build_weed_band, "Weed",
                           args=((sx0, sy0, sx1, sy1), z, "@weed"),
                           kw=dict(n=item[1], seed=seed,
                                   h_max=ctx["caps"].get("weed_h"))))

    # ── extras ────────────────────────────────────────────────────────
    for name, kw0 in prof["extras"]:
        kw = dict(kw0); kw.update(extras_args.get(name, {}))
        if name == "membrane":
            ops.append(_op("membrane", build_membrane, "Membrane",
                           args=((sx0, sy0, sx1, sy1), z, "@membrane"),
                           kw=dict(seed=seed, **kw)))
        elif name == "groove_band":
            reg = kw.pop("region", (max(x0, 0.0) + 3.6, y0, x1, y1))
            ops.append(_op("groove", build_groove_band, "Groove",
                           args=(reg, z), kw=kw))
        elif name == "ramp_curb":
            prof_segs = kw.pop("profile", None)
            if prof_segs:
                ops.append(_op("ramp_curb", _ik_ramp_curb, "RampCurb",
                               args=(prof_segs, kw.pop("y_neg", y0),
                                     kw.pop("y_pos", y1), "@curb"), kw=kw))
        elif name == "deck_planks":
            reg = kw.pop("region", (x0, y0, x1, y1))
            ops.append(_op("planks", build_deck_planks, "Planks",
                           args=(reg[0], reg[1], reg[2], reg[3], z, "@deck"),
                           kw=kw))
        elif name == "wear_lane":
            cl = kw.pop("centerline", ((sx0, (sy0 + sy1) / 2.0),
                                       (sx1, (sy0 + sy1) / 2.0)))
            ops.append(_op("wear", build_wear_lane, "Wear",
                           args=(cl, z, "@wear"), kw=kw))
        elif name == "edge_litter":
            cl = kw.pop("centerline", ((sx0, (sy0 + sy1) / 2.0),
                                       (sx1, (sy0 + sy1) / 2.0)))
            kw.pop("width", None)
            ops.append(_op("litter", build_edge_litter, "Litter",
                           args=(cl, z, "@litter"),
                           kw=dict(width=abs(y1 - y0))))
        elif name == "edge_break":
            for k, yy in enumerate(kw.pop("lines", [y0, y1])):
                ops.append(_op(f"edgebreak{k}", build_edge_break,
                               f"EdgeBreak_{k}",
                               args=(((sx0, yy), (sx1, yy)), z, "@edge_break"),
                               kw=dict(kw)))
        elif name == "silt_band":
            ops.append(_op("silt", build_silt_band, "Silt",
                           args=((sx0, sy0, sx1, sy1), kw.pop("waterline", sy0),
                                 z,
                                 "@silt"), kw=kw))
        elif name == "footprints":
            pts = kw.pop("path_pts", [(sx0, (sy0 + sy1) / 2.0),
                                      (sx1, (sy0 + sy1) / 2.0)])
            ops.append(_op("foot", build_footprints, "Foot",
                           args=(pts, z, "@stain_dirt"),
                           kw=dict(seed=seed, **kw)))

    # ── 점자블록 — TACTILE_SITES 등재 지점만 (B11) ─────────────────────
    for site in tactile_sites:
        scene = ctx.get("scene")
        reg = TACTILE_SITES.get(scene or "", {})
        if site not in reg:
            raise ValueError(
                f"ground_kit: B11 — 점자블록 무단 배치 ({scene}, {site}). "
                f"미설치 사유: {TACTILE_OFF_REASON.get(scene or '', '미등재')}. "
                "설치하려면 §12.3 4조건(법정 트리거·p≥0.50·정체성 비충돌·"
                "GT-E1′/E2)을 먼저 통과시키고 TACTILE_SITES 에 등재하라.")
        spec = reg[site]
        co = (sites.get("tactile") or {}).get(site)
        if co is None:
            se = ctx["edges"][0][1] if ctx["edges"] else 0.0
            sb = _dim("tactile_setback"); dp = _dim("tactile_band_depth")
            co = (se - sb - dp, y0, se - sb, y1)
        ops.append(_op(f"tactile_{site}", _ik_tactile, f"Tactile_{site}",
                       args=(spec["kind"], co[0], co[1], co[2], co[3],
                             "@tactile"),
                       kw=dict(z=z, relief=spec["relief"],
                               walk_axis=spec["walk_axis"], site=site)))
        ops[-1]["site"] = site
    return ops


def _build_weed_band(kit, path, region, z, mtl, n=6, seed=0, h_max=None):
    """**경계 잡초 밴드** — 줄눈선·측구 덮개 틈에 포기 단위로.

    식생이지 지면이 아니다. **GT-E5 램프 대상**(`exc="weed"`) — 에지에 가까울수록
    `_clamp_gt_e5` 가 높이를 깎는다. 계절 중립종 확보는 A조(식생) 이관.

    프림: 1/포기.  GT: 예외 등록(h ≤ 0.12, 램프 클램프).
    """
    x0, y0, x1, y1 = _norm_region(region)
    h_max = _dim("weed_h_max") if h_max is None else float(h_max)
    rng = det_rng("gkit.weed", _seed_key(path), seed)
    n0 = kit.mark()
    elems = []
    for i in range(int(n)):
        cx = x0 + 0.05 + rng.random() * max(1e-6, (x1 - x0) - 0.10)
        cy = (y0 if i % 2 == 0 else y1) + (0.05 if i % 2 == 0 else -0.05)
        hh = h_max * (0.5 + 0.5 * rng.random())
        p = f"{path}/Weed_{i}"
        kit.B(p, (cx, cy, float(z) + hh / 2.0), (0.10, 0.10, hh), mtl)
        elems.append(_elem("weed", p,
                           _box_aabb(cx, cy, float(z) + hh / 2.0,
                                     0.10, 0.10, hh),
                           proud=hh, mtl_key="weed", exc="weed", albedo=0.15))
    return dict(prim_count=kit.count_since(n0), elems=elems)


# ===========================================================================
# [14] SCENE_PLANS — **자기검산 픽스처** (통합 코드의 좌표 원천이 아니다, §7.4)
#
#     통합부는 씬 `PARAMS`/`build_views()` 에서 좌표를 읽는다. 아래 값은
#     §5 매트릭스·§2.3 원점표에서 옮긴 **검산용 근사**다.
# ===========================================================================
def _S(profile, region, **kw):
    d = dict(profile=profile, region=region, z=0.0, gy=0.0,
             origin=(0.0, 0.0, 0.0), axis="+x", edges=(), voids=(),
             dists=(2, 5, 10), tactile=(), sites={}, extras_args={}, caps={})
    d.update(kw)
    return d


_E0 = (("edge", 0.0),)                       # 표준 낙차 에지 = 진행축 원점

# scene13 램프 종단 프로파일 — 씬 `ramp_profile()` 과 동일 규약(검산 픽스처).
#   완화 3.6 m @8.5 % → 본선 @17 % → 완화 3.6 m @8.5 %, 총 낙차 4.4 m.
_R13_TRUN, _R13_TG, _R13_DROP, _R13_MG = 3.6, 0.085, 4.4, 0.17
_R13_TD = _R13_TRUN * _R13_TG
_R13_MD = _R13_DROP - 2.0 * _R13_TD
_RAMP13_PROFILE = [(0.0, 0.0, _R13_TRUN, _R13_TD),
                   (_R13_TRUN, -_R13_TD, _R13_MD / _R13_MG, _R13_MD),
                   (_R13_TRUN + _R13_MD / _R13_MG,
                    -(_R13_TD + _R13_MD), _R13_TRUN, _R13_TD)]

SCENE_PLANS = {
    # ── 본편 21 ───────────────────────────────────────────────────────
    "scene01": _S("plaza_granite", (-12.0, -5.5, -0.5, 5.5), gy=-2.75,
                  edges=_E0, tactile=("stair_top",),
                  sites=dict(manhole=[(-3.8, -2.4), (-8.0, 1.6)],
                             gully=[(-0.95, -5.10), (-0.95, 5.10)])),
    "scene02": _S("sidewalk_block", (-12.0, -4.0, -0.5, 4.0), edges=_E0,
                  tactile=("stair_top",),
                  sites=dict(manhole=[(-1.20, 0.35)],
                             gully=[(-0.95, -3.6), (-0.95, 3.6)])),
    "scene03": _S("levee_paved", (-12.0, -3.0, 6.0, 3.0), edges=_E0),
    "scene04": _S("trail_soil", (-12.0, -1.6, 2.0, 1.6), edges=_E0),
    "scene05": _S("plaza_granite", (-12.0, -5.0, -0.5, 5.0), edges=_E0,
                  sites=dict(manhole=[(-3.5, -1.0), (-8.5, 0.0)],
                             gully=[(-8.5, 0.4), (-6.0, -2.0)])),
    # 06 — 원점 (3.5, −13.0, 5.000), 진행 −Y. 데크 폭 x 2~5, 에지 y=−13.
    #  ※ 사양 §2.3 의 06 행 W1 표기(y −12.44…−11.0 등)는 §2.2 정의보다 +0.564 m
    #    어긋난다. 여기서는 §2.2 기하 정의(X∈[0.564,2.00])를 따른다.
    "scene06": _S("bridge_deck", (2.0, -13.0, 5.0, 0.0),
                  origin=(3.5, -13.0, 5.0), axis="-y", edges=_E0),
    "scene07": _S("courtyard_dg", (-12.0, -3.0, 4.0, 3.0), edges=_E0),
    "scene08": _S("sidewalk_block", (-12.0, -4.0, -0.5, 4.0), edges=_E0,
                  tactile=("opening_ring",),
                  sites=dict(manhole=[(-9.0, 1.5)],
                             gully=[(-9.5, -1.2), (-2.0, 2.0)],
                             tactile=dict(opening_ring=(-1.4, -3.0, -0.8, 3.0)))),
    "scene09": _S("plaza_water", (-12.0, -6.0, -0.5, 6.0), edges=_E0),
    "scene10": _S("deck_trail_hybrid", (-12.0, -0.85, -1.5, 0.85), edges=_E0,
                  extras_args=dict(deck_planks=dict(region=(-1.5, -1.4, 0.0, 1.4)),
                                   edge_break=dict(lines=[-0.85, 0.85]))),
    "scene11": _S("bridge_deck", (-12.0, -1.0, 0.0, 1.0),
                  origin=(15.0, 0.0, 5.5), edges=_E0,
                  tactile=("stair_top", "stair_foot")),
    "scene12": _S("deck_timber", (-12.0, -1.6, 0.0, 1.6), edges=_E0,
                  extras_args=dict(deck_planks=dict(max_gaps=60))),
    # 13 — 램프 크레스트 은닉(§5.0 C-2): 에지 너머 노면구배 0.085 → d2 만 [F].
    #      점자블록은 **보도부만**(램프 내부 = 주차장 내부 = 비대상, §12.4).
    "scene13": _S("ramp_parking", (-14.0, -3.3, 0.6, 3.3),
                  edges=(("ramp_crest", 0.0, dict(beyond_grade=0.085)),),
                  tactile=("bollard",),
                  extras_args=dict(
                      ramp_curb=dict(profile=_RAMP13_PROFILE, y_neg=-3.0,
                                     y_pos=3.0, height=0.12, width=0.30),
                      groove_band=dict(region=(3.6, -3.0, 20.4, 3.0))),
                  sites=dict(manhole=[(-3.90, 0.00)],
                             # 13-3 진입 트렌치(d2 전용) + 13-4 램프 하단
                             # 집수 트렌치(미장센 — 크레스트 너머라 h0.3 밖)
                             #  ★ (v1.2) 0.35 → 0.52. 프레임 반폭 0.19 라
                             #    근단이 크레스트 +0.16 m 에 있었고 d2 이격이
                             #    18.1 @1080 = 9.1 @540 — 유도 강도(16 @540)
                             #    미달이었다. 근단 +0.33 m → 34.7 @1080
                             #    = 17.4 @540 `[계산]`. 여전히 크레스트 너머라
                             #    C-2(d2 전용) 불변.
                             trench=[(0.52, -3.0, 3.0), (23.4, -3.0, 3.0)],
                             tactile=dict(bollard=(-2.90, 4.35, -1.40, 4.65)))),
    "scene14": _S("plaza_granite", (-12.0, -4.0, -0.5, 4.0), edges=_E0,
                  sites=dict(manhole=[(-8.7, 1.2), (-4.5, -1.5)],
                             gully=[(-0.95, -3.6), (-0.95, 3.6)])),
    "scene15": _S("alley_concrete", (-12.0, -0.9, 0.0, 0.9), edges=_E0,
                  # (v1.2) 픽스처를 씬 실좌표에 맞춘다 — 구 −1.15 는 M9-ⓑ
                  # 이설 전 값이었고 −4.00 은 d5 화면폭 56.1 % 였다(레드팀 G-2).
                  sites=dict(manhole=[(-2.40, -0.15)], gutter_U=[-0.75],
                             # 15-6 계단 발치 그레이팅 — 실제로는 꺾임
                             # rot_group 로컬 x=9.3·z=−4.25. 픽스처는 공칭 좌표.
                             trench=[(9.3, -0.9, 0.9)],
                             patch=[(-4.2, 0.10), (-7.6, -0.30)])),
    "scene16": _S("sidewalk_block", (-12.0, -2.5, 2.0, 2.5), edges=_E0,
                  tactile=("entrance",),
                  sites=dict(manhole=[(-3.9, -0.8)],
                             gully=[(-6.0, -2.2), (-1.5, 2.2)],
                             tactile=dict(entrance=(-6.0, -2.5, -5.4, 2.5)))),
    "scene17": _S("levee_paved", (-12.0, -4.0, 4.0, 4.0), edges=_E0,
                  sites=dict(manhole=[(-2.0, 1.2)],
                             gully=[(-3.0, -3.6), (-9.0, -3.6)])),
    "scene18": _S("plaza_granite", (-12.0, -5.0, -0.5, 5.0), edges=_E0,
                  sites=dict(manhole=[(-4.0, 1.0), (-9.0, -1.0)],
                             gully=[(-2.5, -4.6), (-8.0, 4.6)])),
    # 19 — 미러(x' = 2·5.8 − x)·진행 −X·dists (2, 3.5, 5). 에지 x=9.04.
    "scene19": _S("roof_membrane", (9.04, -4.0, 21.0, 4.0),
                  origin=(9.04, 0.0, 0.0), axis="-x", edges=_E0,
                  dists=(2, 3.5, 5),
                  sites=dict(gully=[(10.5, -0.6), (15.0, -2.5)])),
    "scene20": _S("plaza_granite", (-13.0, -4.0, -0.5, 4.0), edges=_E0,
                  sites=dict(manhole=[(-5.0, 1.4), (-10.0, -1.4)],
                             gully=[(-3.0, -3.6), (-8.0, 3.6)])),
    "scene21": _S("plaza_granite", (-12.0, -4.0, -0.5, 4.0), edges=_E0,
                  sites=dict(manhole=[(-4.0, 1.0), (-4.0, -1.0)],
                             gully=[(-2.0, -3.6), (-7.0, 3.6)])),
    # ── 배치1 12 ──────────────────────────────────────────────────────
    # C1 — §7.3 불변식: 신규 요소 proud ≤ 적설 0.05(매몰이 씬 특색).
    "sceneC1": _S("plaza_granite", (-11.0, -3.0, -0.5, 3.0), edges=_E0,
                  caps=dict(weed_h=0.045), tactile=("stair_top",),
                  sites=dict(manhole=[(-3.0, 1.0)],
                             gully=[(-5.0, -2.6), (-9.0, 2.6)])),
    "sceneC2": _S("sidewalk_block", (-10.6, -3.6, -0.3, 3.6), edges=_E0,
                  sites=dict(manhole=[(-4.0, 1.2)],
                             gully=[(-2.0, -3.2), (-8.0, 3.2)])),
    "sceneC4": _S("sidewalk_block", (-10.0, -3.0, -0.5, 3.0), edges=_E0,
                  tactile=("stair_top",),
                  sites=dict(manhole=[(-4.4, 1.0)],
                             gully=[(-2.0, -2.6), (-8.0, 2.6)],
                             tactile=dict(stair_top=(-1.60, -3.0, -1.00, 3.0)))),
    "sceneD1": _S("yard_industrial", (-12.0, -6.0, 0.0, 2.0), gy=-4.0,
                  edges=_E0,
                  sites=dict(trench=[(-6.0, -6.0, 2.0)],
                             marking=[(-10.0, -5.0, 0.0), (-10.0, -3.0, 0.0)])),
    "sceneD2": _S("slab_construction", (-12.0, -4.0, 0.0, 4.0), edges=_E0,
                  voids=((0.2, -1.6, 2.4, 1.6),),
                  sites=dict(marking=[(-4.0, -2.0, 0.0, 3.0)])),
    "sceneD3": _S("verge_rural", (-12.0, -3.0, 2.0, 3.0), edges=_E0),
    "sceneD4": _S("platform_indoor", (-12.0, -5.0, 0.0, -2.2), gy=-3.6,
                  edges=_E0, tactile=("platform_edge",),
                  sites=dict(tactile=dict(platform_edge=(-0.90, -5.0, -0.30, -2.2)))),
    "sceneN1": _S("plaza_granite", (-12.0, -4.0, -0.6, 4.0),
                  sites=dict(manhole=[(-1.0, 0.4)],
                             gully=[(-4.0, -3.6), (-9.0, 3.6)])),
    "sceneN2": _S("street_asphalt", (-12.0, -4.0, 2.0, 4.0),
                  sites=dict(manhole=[(-1.0, 0.5)],
                             gully=[(-3.0, -3.6), (-8.0, -3.6),
                                    (-11.0, 3.6)],
                             marking=[(-4.6, 5.6, 0.0)])),
    "sceneN3": _S("plaza_granite", (-12.0, -4.0, -1.6, 4.0),
                  sites=dict(manhole=[(-2.0, 1.0), (-6.0, -1.0)],
                             gully=[(-4.0, -3.6), (-9.0, 3.6)])),
    "sceneN4": _S("ramp_road", (-12.0, -1.85, 6.0, 1.85), edges=_E0,
                  sites=dict(gully=[(4.0, -1.7), (-2.0, -1.7), (-8.0, -1.7),
                                    (0.0, 1.7), (-5.0, 1.7), (-11.0, 1.7)],
                             marking=[(-11.0, -1.6, 0.0), (-11.0, 1.6, 0.0)])),
    "sceneN5": _S("sidewalk_block", (-12.0, -3.0, 2.0, 3.0),
                  tactile=("bollard",),
                  sites=dict(manhole=[(-1.15, 0.30)],
                             gully=[(-4.0, -2.6), (-9.0, -2.6)],
                             tactile=dict(bollard=(4.0, -5.7, 11.0, -5.1)))),
}


# ===========================================================================
# [15] 자기검산 — `python3 ground_kit.py` (Isaac·GPU 불요)
# ===========================================================================
def _selfcheck():
    ok = True
    fails = []

    def chk(name, cond, detail=""):
        nonlocal ok
        mark = "OK  " if cond else "FAIL"
        if not cond:
            ok = False
            fails.append(f"{name}: {detail}")
        print(f"  [{mark}] {name}" + (f"  ({detail})" if detail else ""))

    print("=" * 78)
    print("ground_kit — 계획·프림수·GT 자기검산 (Isaac 부팅 없음)")
    print(f"  카메라 f = {CAM_F:.3f} px · pitch {CAM_PITCH_DEG}° · "
          f"VFOV {CAM_VFOV_DEG:.2f}° · {CAM_W}×{CAM_H}")
    print("=" * 78)

    # ── ① 상수·기하 검산 (사양 부록 B 재현) ────────────────────────────
    print("\n[1] 상수·기하 (사양 부록 B 재현)")
    chk("f = 1662.77 px", abs(CAM_F - 1662.769) < 0.01, f"{CAM_F:.3f}")
    chk("VFOV = 35.98°", abs(CAM_VFOV_DEG - 35.98) < 0.02,
        f"{CAM_VFOV_DEG:.3f}")
    chk("row(2.0) = 497.35", abs(cam_row(2.0) - 497.35) < 0.05,
        f"{cam_row(2.0):.2f}")
    chk("row(10.0) = 297.98", abs(cam_row(10.0) - 297.98) < 0.05,
        f"{cam_row(10.0):.2f}")
    chk("EDGE_K = 40.0", abs(EDGE_K - 1.20 * 10 / 0.3) < 1e-9, f"{EDGE_K}")
    chk("GT_DELTA×EDGE_K = EDGE_STANDOFF",
        abs(GT_DELTA * EDGE_K - EDGE_STANDOFF) < 1e-9,
        f"{GT_DELTA * EDGE_K:.3f}")
    chk("drow(−0.95, 10) = 5.34 (v1 트렌치 → FAIL)",
        abs(drow(-0.95, 10) - 5.34) < 0.02, f"{drow(-0.95, 10):.2f}")
    chk("drow(−2.40, 10) = 16.05 (C-1′ 근단 → PASS)",
        abs(drow(-2.40, 10) - 16.05) < 0.02, f"{drow(-2.40, 10):.2f}")
    chk("drow(−0.30, 5) = 6.42 (법정 점자블록 → GT-E2-x 필요)",
        abs(drow(-0.30, 5) - 6.42) < 0.02, f"{drow(-0.30, 5):.2f}")
    # ── 행 단위 규약 (v1.2) — 두 축이 섞이지 않는지 코드가 지킨다 ──────
    chk("GRAZE 작업본 = 960×540 (regression_check.GRAZE_LONG)",
        (GRAZE_WORK_LONG, GRAZE_WORK_H) == (960, 540),
        f"{GRAZE_WORK_LONG}×{GRAZE_WORK_H}")
    chk("ROWS_1080_PER_WORK = 2.0", abs(ROWS_1080_PER_WORK - 2.0) < 1e-12,
        f"{ROWS_1080_PER_WORK}")
    chk("GRAZE_ROW_SEP_WORK = 16 = (HW3+SMOOTH3+SLACK2)×2 [@540]",
        GRAZE_ROW_SEP_WORK == 16, f"{GRAZE_ROW_SEP_WORK}")
    chk("GRAZE_ROW_SEP_1080 = 32.0 (유도 강도, v1.1 은 16 = 절반)",
        abs(GRAZE_ROW_SEP_1080 - 32.0) < 1e-12, f"{GRAZE_ROW_SEP_1080}")
    chk("축 왕복 무손실 to_work→to_1080",
        abs(to_1080_rows(to_work_rows(497.35)) - 497.35) < 1e-9)
    # 컷별 집행 하한 — d2/d5 는 완전분리 달성 가능, d10 은 대역이 얕아 불가
    chk("d2 집행하한 = 32 @1080 (완전분리 달성 가능)",
        abs(graze_row_sep_1080(2) - 32.0) < 1e-9, f"{graze_row_sep_1080(2)}")
    chk("d5 집행하한 = 32 @1080", abs(graze_row_sep_1080(5) - 32.0) < 1e-9,
        f"{graze_row_sep_1080(5)}")
    _d10_reach = max(abs(cam_row(7.0) - cam_row(10.0)),
                     abs(cam_row(22.0) - cam_row(10.0)))
    chk("d10 은 E대역(7~22 m)이 얕아 완전분리 불가 → footprint 16 @1080",
        abs(graze_row_sep_1080(10) - 16.0) < 1e-9 and _d10_reach < 32.0,
        f"대역내 최대도달 {_d10_reach:.2f}@1080 = "
        f"{to_work_rows(_d10_reach):.2f}@540 < 16@540")
    chk("15-2 맨홀 d2 화면폭 1,268 px (X = 2 − 1.15 = 0.85)",
        abs(cam_wpx(0.648, 0.85) - 1268) < 3.0,
        f"{cam_wpx(0.648, 0.85):.0f} px = 프레임 폭 "
        f"{100 * cam_wpx(0.648, 0.85) / CAM_W:.1f} %")

    # ── ② 프로파일 원장 (18종 + U1~U4) ────────────────────────────────
    print("\n[2] 프로파일 원장 · 유닛 셀 계약 (§4.1·§4.5)")
    chk("프로파일 18종 + 하위변종 1", len(GROUND_PROFILES) == 19,
        f"{len(GROUND_PROFILES)}")
    chk("P18 deck_trail_hybrid 존재", "deck_trail_hybrid" in GROUND_PROFILES)
    ucok = True
    for key, prof in GROUND_PROFILES.items():
        try:
            _assert_unit_cell(key, prof)
        except ValueError as ex:
            ucok = False
            print(f"        · {ex}")
    chk("U1~U4 유닛 셀 정합 (전 프로파일)", ucok)
    chk("자연 프로파일 도시 인프라 0건",
        all(not any(prof["infra"].get(k) for k in _URBAN_INFRA_KEYS)
            for prof in GROUND_PROFILES.values() if prof["natural"]))
    chk("프로파일 tactile 전부 None (§3.4)",
        all(p["tactile"] is None for p in GROUND_PROFILES.values()))

    # ── ③ 점자블록 등록부 ─────────────────────────────────────────────
    print("\n[3] 점자블록 등록부 (§12.4)")
    k_h = len([s for s in TACTILE_SITES
               if s not in ("sceneN1", "sceneN2", "sceneN4", "sceneN5")])
    k_n = len([s for s in TACTILE_SITES
               if s in ("sceneN1", "sceneN2", "sceneN4", "sceneN5")])
    chk("설치 낙차 씬 K_h = 9", k_h == 9, f"{k_h}")
    chk("볼라드 전면 무낙차 K_n = 4", k_n == 4, f"{k_n}")
    chk("P(점형|낙차) = K_h/28 = 0.321", abs(k_h / 28.0 - 0.321) < 0.005,
        f"{k_h / 28.0:.3f}")
    fp_rows = tactile_fp_rows()
    chk("d2 는 Δ≥16 자력 통과 → EXPECTED_FP 미등재", 2 not in fp_rows,
        f"등재 컷 {sorted(fp_rows)}")
    # ★ (v1.2) 사양 §12.3 의 d5 표본 (348, 356) 은 **행 축 결함의 산물**이었다.
    #   그 값은 "Δ<16 @1080" 로 걸러 근단(355.03)만 담은 것이고, 유도 강도
    #   (16 @540 = 32 @1080)에서는 원단(Δ 22.1 @1080 = 11.1 @540)도 융합 대역
    #   안이라 함께 담긴다 → (348, 371). d10 표본 (297, 304) 는 불변.
    #   **§12.3 d5 표본은 본 수정으로 대체된다** — 보고서에 명기.
    chk("scene02 d5 FP 행 = (348, 371)  [§12.3 (348,356) 대체 — 축 정정]",
        fp_rows.get(5) == (348, 371), f"{fp_rows.get(5)}")
    chk("scene02 d10 FP 행 = (297, 304)  [§12.3 표본 그대로]",
        fp_rows.get(10) == (297, 304), f"{fp_rows.get(10)}")
    chk("EXPECTED_FP 가 소비자 축(@540)을 함께 싣는다",
        all("rows_work" in v and v["scale_work"] == 540
            for v in EXPECTED_FP.values()),
        f"d5 @540 = {EXPECTED_FP[('scene02', 'preset_h0.3_d5')]['rows_work']}")
    chk("EXPECTED_FP 등재 = 낙차 트리거 씬 × {d5,d10}",
        len(EXPECTED_FP) == 2 * len([s for s, v in TACTILE_SITES.items()
                                     if any(x["trigger"] in _FP_TRIGGERS
                                            for x in v.values())]),
        f"{len(EXPECTED_FP)}")
    chk("relief='geom' 사용 0 (프림 절대상한 200 과 비양립 — 감독 안건)",
        sum(1 for v in TACTILE_SITES.values() for s in v.values()
            if s["relief"] == "geom") == 0)

    # ── ④ 규약 강제 (예외가 실제로 던져지는가) ────────────────────────
    print("\n[4] 규약 강제 — 예외 발생 검사")

    def raises(fn, tag):
        try:
            fn()
        except ValueError:
            return True
        except Exception as ex:                 # noqa: BLE001
            print(f"        · {tag}: 다른 예외 {type(ex).__name__}: {ex}")
            return False
        return False

    chk("자연 프로파일 + 도시 인프라 → ValueError",
        raises(lambda: plan_ground("trail_soil", (-10, -2, 0, 2),
                                   overrides=dict(infra=dict(manhole=1)),
                                   scene="scene04", edges=_E0), "natural"))
    chk("미등재 점자블록 → ValueError (B11)",
        raises(lambda: plan_ground("alley_concrete", (-12, -0.9, 0, 0.9),
                                   scene="scene15", edges=_E0,
                                   tactile=("stair_top",)), "B11"))
    chk("prefix 에 GKit 없음 → ValueError",
        raises(lambda: apply_ground(dry_kit(), "/World/X",
                                    plan_ground("sidewalk_block",
                                                (-10, -2, 0, 2),
                                                scene="scene16", edges=_E0),
                                    {}), "prefix"))
    chk("줄눈 양각 요청 → ValueError",
        raises(lambda: build_joint_grid(dry_kit(), "/T", (-4, -1, 0, 1), 0.0,
                                        None, recess=+0.003), "recess"))

    # ── ⑤ 전 33씬 dry 실행 ────────────────────────────────────────────
    print("\n[5] 전 33씬 계획 dry 실행 (USD 미접촉)")
    hdr = (f"{'씬':<9}{'프로파일':<20}{'프림':>5}{'산포':>6}"
           f"{'δmax':>8}{'B1':>4}{'B2':>7}{'B3':>4}{'B4':>4}{'B5':>4}"
           f"  {'하드게이트':<10}{'WARN'}")
    print("  " + hdr)
    print("  " + "-" * (len(hdr) + 8))
    n_ok, tot_prims, tot_inst, warn_rows = 0, 0, 0, []
    for scene in sorted(SCENE_PLANS):
        sp = SCENE_PLANS[scene]
        try:
            plan = plan_ground(sp["profile"], sp["region"], z=sp["z"],
                               gy=sp["gy"], origin=sp["origin"],
                               axis=sp["axis"], edges=sp["edges"],
                               voids=sp["voids"], dists=sp["dists"],
                               scene=scene, tactile=sp["tactile"],
                               sites=sp["sites"], caps=sp["caps"],
                               extras_args=sp["extras_args"], seed=7)
        except ValueError as ex:
            ok = False
            fails.append(f"{scene}: {ex}")
            print(f"  {scene:<9}{sp['profile']:<20}  *** ValueError ***")
            print(f"        {ex}")
            continue
        b = plan["budget"]
        g = b["gates"]
        hard = "PASS" if not b["fail"] else "FAIL:" + ",".join(b["fail"])
        pc = b["per_cut"]
        b1 = max(v["area_w1"] for v in pc.values())
        b2 = max(v["area_pct"] for v in pc.values())
        b3 = max(v["cross"] for v in pc.values())
        b4 = max(v["long"] for v in pc.values())
        b5 = max(v["decal"] for v in pc.values())
        print(f"  {scene:<9}{plan['profile']:<20}{plan['prims']:>5}"
              f"{plan['instances']:>6}{plan['gt']['delta_max']:>8.4f}"
              f"{b1:>4}{b2:>7.1f}{b3:>4}{b4:>4}{b5:>4}  {hard:<10}"
              f"{','.join(b['warn'])}")
        tot_prims += plan["prims"]; tot_inst += plan["instances"]
        if b["warn"]:
            warn_rows.append((scene, b["warn"]))
        if not b["fail"]:
            n_ok += 1
        # 요소 단위 하드 어서션
        for e in plan["elements"]:
            if e["meta"].get("dropped"):
                continue
            if e["meta"].get("exc") in (None,) \
                    and abs(e["proud"]) > GT_DELTA + 1e-9:
                ok = False
                fails.append(f"{scene} GT δ: {e['path']} {e['proud']}")
        # 개구 교차 0
        for e in plan["elements"]:
            x0, y0, _, x1, y1, _ = e["aabb"]
            for vx0, vy0, vx1, vy1 in plan["ctx"]["voids"]:
                if x1 > vx0 and x0 < vx1 and y1 > vy0 and y0 < vy1:
                    ok = False
                    fails.append(f"{scene} 개구 교차: {e['path']}")
    print("  " + "-" * (len(hdr) + 8))
    print(f"  합계: 씬 {len(SCENE_PLANS)} · 하드게이트 통과 {n_ok} · "
          f"기하 프림 {tot_prims} · 산포 인스턴스 {tot_inst}")
    chk("33씬 등재", len(SCENE_PLANS) == 33, f"{len(SCENE_PLANS)}")
    chk("전 씬 하드게이트(B6~B12) 통과", n_ok == len(SCENE_PLANS),
        f"{n_ok}/{len(SCENE_PLANS)}")
    chk("33씬 합계 기하 프림 ≤ 33×60", tot_prims <= 33 * 60,
        f"{tot_prims}")
    if warn_rows:
        print("\n  [WARN 상세] B1~B5 는 프레임 충전 목표(하드 아님) — "
              "최종 판정은 렌더 후 σ_LF/sd")
        for scene, w in warn_rows:
            print(f"    · {scene:<9} {','.join(w)}")

    # ── ⑥ 파일럿 3씬 상세 ─────────────────────────────────────────────
    print("\n[6] 파일럿 3씬 상세 (N5 · 15 · 13)")
    for scene in ("sceneN5", "scene15", "scene13"):
        sp = SCENE_PLANS[scene]
        plan = plan_ground(sp["profile"], sp["region"], z=sp["z"], gy=sp["gy"],
                           origin=sp["origin"], axis=sp["axis"],
                           edges=sp["edges"], voids=sp["voids"],
                           dists=sp["dists"], scene=scene,
                           tactile=sp["tactile"], sites=sp["sites"],
                           caps=sp["caps"], extras_args=sp["extras_args"],
                           seed=7)
        print(f"  {scene} [{plan['profile']}] 프림 {plan['prims']} · "
              f"요소 {len(plan['elements'])} · δmax {plan['gt']['delta_max']:.4f}"
              f" · unit_cell {plan['unit_cell']}")
        for d, v in sorted(plan["budget"]["per_cut"].items()):
            print(f"      d{d:<4} 면요소W1 {v['area_w1']} · 폭 {v['area_pct']:.1f} %"
                  f" · 횡단선 {v['cross']} · 종단선 {v['long']} · 데칼 {v['decal']}"
                  f" · 단선 {v['singular']}")
        if plan["gt_changes"]:
            for g in plan["gt_changes"]:
                print(f"      [GT 변경] {g['item']} drop={g['drop']:.3f} "
                      f"→ 라벨 {g['label_owner']}")

    # ── ⑦ apply_ground dry 왕복 ───────────────────────────────────────
    print("\n[7] apply_ground dry 왕복 (USD 헬퍼 = dry_kit)")
    sp = SCENE_PLANS["scene15"]
    plan = plan_ground(sp["profile"], sp["region"], scene="scene15",
                       edges=sp["edges"], sites=sp["sites"], seed=7)
    dk = dry_kit()
    res = apply_ground(dk, "/World/Scene15/GKit", plan, {},
                       skin_exclude=lambda *a: None,
                       slabs=("/World/Scene15/UpperAlley",))
    chk("apply 프림 = plan 프림", res["prims"] == plan["prims"],
        f"{res['prims']} vs {plan['prims']}")
    chk("전 프림이 GKit 아래",
        all(p.startswith("/World/Scene15/GKit") for p in dk.prims),
        f"{len(dk.prims)}")
    chk("gt_delta_max ≤ GT_DELTA (예외 제외)",
        res["gt_delta_max"] <= max(GT_DELTA, _dim("weed_h_max")) + 1e-9,
        f"{res['gt_delta_max']:.4f}")

    # ★ 전 33씬 apply 왕복 — 재질 치환 규칙 위반을 **CPU 에서** 잡는다.
    #   `dry_kit` 은 Bind 를 안 하므로, 미치환 재질 키는 apply_ground 의
    #   가드가 아니면 GPU 렌더에서야 `Bind(str)` 로 터진다
    #   `[실측 — sceneN5 파일럿 1회차]`.
    mtl_bad, prim_bad = [], []
    for scene in sorted(SCENE_PLANS):
        sp = SCENE_PLANS[scene]
        try:
            pl = plan_ground(sp["profile"], sp["region"], z=sp["z"],
                             gy=sp["gy"], origin=sp["origin"], axis=sp["axis"],
                             edges=sp["edges"], voids=sp["voids"],
                             dists=sp["dists"], scene=scene,
                             tactile=sp["tactile"], sites=sp["sites"],
                             caps=sp["caps"], extras_args=sp["extras_args"],
                             seed=7)
            d2 = dry_kit()
            r2 = apply_ground(d2, f"/World/{scene}/GKit", pl, {},
                              skin_exclude=lambda *a: None)
            if r2["prims"] != pl["prims"]:
                prim_bad.append(f"{scene} {r2['prims']}≠{pl['prims']}")
        except ValueError as ex:
            mtl_bad.append(f"{scene}: {ex}")
    chk("33씬 apply 왕복 — 미치환 재질 참조 0",
        not mtl_bad, mtl_bad[0][:110] if mtl_bad else "0건")
    chk("33씬 apply 프림 = plan 프림", not prim_bad,
        "; ".join(prim_bad[:3]) or "33/33")

    print("\n" + "=" * 78)
    if ok:
        print("ground_kit 자기검산 — 전 항목 통과")
    else:
        print(f"ground_kit 자기검산 — 실패 {len(fails)}건")
        for f in fails:
            print(f"  · {f}")
    print("=" * 78)
    return ok


if __name__ == "__main__":
    sys.exit(0 if _selfcheck() else 1)
