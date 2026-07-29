# -*- coding: utf-8 -*-
"""ground_kit.py - ground element profile orchestrator (Isaac Sim 4.5 / USD)

Written 2026-07-29, target: the 33 NegObs scenes (21 main + 12 batch 1)
Sole specification: `Docs/briefs/ground_kit_spec_v1.md` **v1.1**

## What this file is (and is not)

**Not**: "a new element library". The 6 builders of `infra_kit` (gutter, gully,
manhole, ramp curb, road marking, retaining wall detail) are already implemented and
checked, yet only 1 of the 33 scenes (`sceneN4`) uses them `[measured - grep]`. They are
**not reimplemented** here; they are absorbed via `import infra_kit as ik`.

**Yes**: a 3-layer "scene type -> profile -> placement plan -> USD" orchestrator plus
the **15 new small builders** required by spec §4.3 (all geometry).

## Why it is needed (measured facts - spec §0)

1. What must be filled is **a single band 0.56-2.00 m in front of the camera** -
   **53.9 %** of the h0.3 frame height `[computed - spec §2.2]`. Elements placed at
   x >= 0 (around the hazard geometry) fall in the top 8 % of the frame only. That is
   the mechanism by which `sceneN2` scored sigma_LF 1.36 despite having 9 element types.
2. `_ground_skin` (the look layer) **buries** flush ground elements. Manholes
   (proud 2.0 mm) and dot blocks (4.0 mm) disappear entirely under a skin top of
   **+6.5 to +16.5 mm** `[measured - scene_common.py:820-841]`. -> **P-A: skin OFF for
   the target slabs** (inject the `scene_common.skin_exclude` callback, spec §1.2).
3. The failure mode where ground_kit output takes on a second skin is structurally
   prevented: the path token `"gkit"` (= `GKIT_PATH_TOKEN` lowercased) is in `_SKIN_DENY`.

## Conventions (inherited from `infra_kit`, no exceptions - spec §3.1)

- **Z-up, metres, travel axis +X** (per-scene travel axis is rotated via the `axis` arg).
- **`scene_common` is not imported.** Primitives are injected via `Kit`.
  `import infra_kit` is allowed (no back-reference). `Kit`, `det_seed`, `det_rng`,
  `_bay_joints`, `kit_from_scene_common` and `dry_kit` are **re-exported**
  (reimplementation forbidden).
- **RNG 100 % deterministic** - `hash()` banned, only `zlib.crc32 -> random.Random`.
- **Every prim lives under `{prefix}`**, and `prefix` is fixed to `{ROOT}/GKit`
  (§1.2 skin defence).
- Every builder docstring carries a **`GT:` line** plus prims per unit / per metre.
- Dimensions live **only in the `GROUND_DIMENSIONS` ledger**. A number absent from the
  ledger is never used as a default.
- **Albedo hard clamp <= 0.30** (tactile paving only 0.55 - statutory yellow, small
  area). Exceeding it raises `ValueError`.
- **Forbidden APIs**: the `lid=False` family (uncovered), new bollard placement,
  person/vehicle objects, season-specific scatter (04/07 browned leaves, C1 snow and
  C2 leaves are the only scene-identity exceptions).
- **Tactile paving only at (scene, site) pairs registered in `TACTILE_SITES`.** A
  profile flag cannot enable it.

## The 3-layer public API

    layer 1  GROUND_DIMENSIONS / GROUND_PROFILES / TACTILE_SITES / EXPECTED_FP
             GROUND_INVARIANTS / GT_DELTA / EDGE_K / GRAZE_ROW_SEP ...
    layer 2  plan_ground(...) -> GroundPlan      (pure computation, no USD contact)
             frame_budget(plan, ...) -> dict     (B1-B12 decided without rendering)
    layer 3  apply_ground(kit, prefix, plan, mtls, *, skin_exclude=None, scatter=None)

Scene integration is two lines:

    gp = gk.plan_ground("alley_concrete", region=(-12.0, -0.9, 0.0, 0.9), z=0.0,
                        edges=[("stair_top", 0.0)], scene="scene15",
                        overrides=PARAMS.get("ground"))
    gk.apply_ground(gk.kit_from_scene_common(sc, stage), f"{ROOT}/GKit", gp, M,
                    skin_exclude=sc.skin_exclude, scatter=sc.scatter_debris)

**Source of truth for coordinates (§7.4)**: `SCENE_PLANS` below is a **self-check
fixture**, not the coordinate source for integration code. Integration reads from the
scene `PARAMS` / `build_views()`.

Check all 33 scene plans without Isaac: `python3 ground_kit.py`
"""

from __future__ import annotations

import inspect
import math
import os
import sys

import infra_kit as ik

# -- infra_kit re-export (spec §3.1 "no reimplementation, re-export") ------
Kit = ik.Kit
det_seed = ik.det_seed
det_rng = ik.det_rng
_bay_joints = ik._bay_joints
kit_from_scene_common = ik.kit_from_scene_common
dry_kit = ik.dry_kit
TACTILE_YELLOW = ik.TACTILE_YELLOW

__all__ = [
    # Re-export
    "Kit", "kit_from_scene_common", "dry_kit", "det_seed", "det_rng",
    "TACTILE_YELLOW",
    # Layer 1
    "GROUND_DIMENSIONS", "GROUND_PROFILES", "TACTILE_SITES", "EXPECTED_FP",
    "GROUND_INVARIANTS", "SCENE_PLANS", "SCATTER_POOLS", "DECAL_Z_ORDER",
    "GROUND_PROUD_MIN", "GROUND_PROUD_FLOOR", "GT_DELTA", "EDGE_STANDOFF",
    "EDGE_K", "GRAZE_ROW_SEP", "GRAZE_ROW_SEP_WORK", "GRAZE_ROW_SEP_1080",
    "GRAZE_FOOTPRINT_WORK", "GRAZE_FOOTPRINT_1080", "GRAZE_WORK_H",
    "ROWS_1080_PER_WORK", "to_work_rows", "to_1080_rows", "graze_row_sep_1080",
    "GKIT_PATH_TOKEN", "ALBEDO_CAP",
    "TACTILE_ALBEDO_CAP", "CAM_F", "CAM_W", "CAM_H",
    # Layers 2 and 3
    "plan_ground", "frame_budget", "apply_ground",
    "region_from_params", "edges_from_params",
    # The 15 new small builders
    "build_joint_grid", "build_slab_joints", "build_patch_field",
    "build_crack_lines", "build_trench_drain", "build_gutter_U",
    "build_groove_band", "build_membrane", "build_stain_field",
    "build_footprints", "build_wear_lane", "build_edge_litter",
    "build_edge_break", "build_deck_planks", "build_silt_band",
]


# ===========================================================================
# [0] Constants - all from spec §1.3/§6/§7. No number absent from here goes into a default.
# ===========================================================================
GROUND_PROUD_MIN = 0.0006      # Effective lower bound for avoiding z-fighting [measured - N5 joints]
GROUND_PROUD_FLOOR = 0.018     # P-B fallback only (normally unused) [computed - 16.5+1.5]
GT_DELTA = 0.020               # Upper bound on |dz| for every element [measured - 1/5 of the 0.10 minor step]
EDGE_STANDOFF = 0.80           # Forbidden zone in front of an edge for elements with z_e=GT_DELTA [m]
EDGE_K = 40.0                  # GT-E1' required clearance = EDGE_K * z_e  [computed - 1.20*10/0.3]
GKIT_PATH_TOKEN = "GKit"       # Every prim lives under this path (§1.2 skin defence)
ALBEDO_CAP = 0.30              # Convention hard clamp
TACTILE_ALBEDO_CAP = 0.55      # Tactile paving exception (statutory yellow, small area) - §12.5 (4)

# -- (v1.3, defect R3) Decal z ladder -------------------------------------
#    Every soiling/wear/transition builder used to top out at exactly
#    `z + stain_proud`, so wherever two of them overlap in XY the shared top plane is
#    **coincident** and the renderer has no depth ordering left - classic z-fighting
#    shimmer. Measured overlaps existed in the shipped plans (scene07 `Stain_dirt/dirt_1`
#    y -0.19..0.31 and `Stain_water/water_1` y 0.01..0.75 both inside the wear lane
#    y +-0.60) `[measured - w2d_edit_g2 §5 R3]`.
#    -> Each decal **family** gets a fixed rank and is lifted by `rank * DECAL_Z_EPS`;
#    inside `build_stain_field`, which is one builder emitting eight different materials,
#    each `kind` gets a further `DECAL_Z_SUB` (a stain-vs-stain overlap is the commonest
#    one there is - dirt over water, gum over dirt).
#    The order is bottom-up by what physically lies under what: the ground transition band
#    and the waterline film are surface tone, the trodden lane sits on them, footprints
#    press into that, and discrete soiling is the last thing to land.
#    Budget: 5 x 0.2 mm + 7 x 0.1 mm = **1.7 mm span**, inside the 2 mm ceiling and under
#    a tenth of `GT_DELTA`. It is real relief, not an epsilon trick, so it is reported in
#    `proud` - GT-E1' then needs `EDGE_K * 0.0023 = 0.092 m` of edge clearance at worst,
#    against a measured minimum decal edge gap of 0.60 m `[measured]`.
#    The smallest step in the ladder is the 0.1 mm between two stain kinds; that is the
#    one the GPU round should confirm on the scene07/scene10 d2/d5 crops (redteam rider 3).
DECAL_Z_EPS = 0.0002           # Step between decal families
DECAL_Z_SUB = 0.0001           # Step between kinds inside one family (stains)
DECAL_Z_ORDER = {
    "edge_break":  0,          # material-boundary transition band (lowest - it *is* the ground)
    "silt_band":   1,          # waterline film / silt drift
    "edge_litter": 2,          # organic matter swept to the path edge
    "wear_lane":   3,          # trodden band along the walking line
    "footprint":   4,          # trace pressed into the trodden band
    "stain":       5,          # discrete soiling decals, + DECAL_Z_SUB per kind
}


def decal_proud(family, sub=0):
    """Relief [m] a decal family (and, for stains, `kind`) stands proud of the paving.

    `z + decal_proud(...)` is the rendered top - the R3 ladder that keeps two overlapping
    decals off a shared plane.
    """
    if family not in DECAL_Z_ORDER:
        raise KeyError(f"ground_kit: DECAL_Z_ORDER 에 '{family}' 가 없다. "
                       "데칼 계열을 새로 만들면 사다리 순서를 먼저 등재하라.")
    return (_dim("stain_proud") + DECAL_Z_ORDER[family] * DECAL_Z_EPS
            + int(sub) * DECAL_Z_SUB)


# -- [W2-C, C2] Diagnostic switch - with `NEGOBS_GKIT=0`, **not a single** element is built.
#    Purpose: shoot ground-kit ON/OFF A/B in the same session at the same HEAD, turning
#    OCCL (camera burial) into an **attributable** metric. The FRAME/PHOTO/OCCL verdicts
#    of the pilot round were held back for exactly this lack of attribution [w2_pilot_ground_v1.md §5].
#    P-A (`skin_exclude`) runs **identically in both arms** - if the displacement skin
#    (+-6.5 to 16.5 mm) also differed between arms, the A/B would not measure the effect
#    of the kit prims. ON by default. Production renders and self-checks leave it alone.
GKIT_ON = os.environ.get("NEGOBS_GKIT", "1") != "0"

# Camera constants (hard-coded - spec §2.1. Three validations: N5 joints -6 px, N1 shadow
#              4/10 px, scene18 horizon row ratio)
CAM_W, CAM_H = 1920, 1080
CAM_HFOV_DEG = 60.0
CAM_F = (CAM_W / 2.0) / math.tan(math.radians(CAM_HFOV_DEG / 2.0))   # 1662.769
CAM_PITCH_DEG = -10.0
CAM_VFOV_DEG = 2.0 * math.degrees(math.atan((CAM_H / 2.0) / CAM_F))  # 35.98
NEAR_W1 = (0.564, 2.00)        # Near window W1 - 53.9 % of the frame height
NEAR_W2 = (2.00, 3.00)         # Secondary window (+7.6 %p)
GRAZE_E_BAND = (0.7, 2.2)      # GRAZE v2 E band = ground distance [0.7d, 2.2d]

# === Row unit convention (v1.2 - resolves the 540 vs 1080 mix, red team G-1) ========
#  **Every row figure states its axis in a suffix. Do not create a new row constant without one.**
#
#  - `_WORK`  = the GRAZE checker working-copy rows (`regression_check.GRAZE_LONG = 960`
#               shrinks 1920x1080 to 960x540). The GRAZE constants
#               `GRAZE_HW 3, GRAZE_SMOOTH 3, GRAZE_SLACK 2` are **all on this axis**, as are
#               the `gz_row` and band figures in the GRAZE JSON.
#  - `_1080`  = the original frame rows returned by `cam_row()`. Spec §2.1 Appendix B
#               (`row(2.0)=497.35`) and the worked example C-1' are on this axis too.
#
#  The defect in v1.1: `GRAZE_ROW_SEP = 16` was **derived on the _WORK axis**
#  (`(HW+SMOOTH+SLACK)*2 = 16`) yet compared directly against `cam_row` (_1080) results
#  -> the enforced strength was in fact **half** the derived value (8 _WORK rows = the footprint radius).
GRAZE_WORK_LONG = 960                                  # = regression_check.GRAZE_LONG
GRAZE_WORK_H = CAM_H * GRAZE_WORK_LONG // CAM_W        # 540
ROWS_1080_PER_WORK = CAM_H / float(GRAZE_WORK_H)       # 2.0
GRAZE_FOOTPRINT_WORK = 8       # Step response radius = HW 3 + SMOOTH 3 + SLACK 2  [@540]
GRAZE_ROW_SEP_WORK = 2 * GRAZE_FOOTPRINT_WORK          # 16 - full separation of two responses [@540]
GRAZE_FOOTPRINT_1080 = GRAZE_FOOTPRINT_WORK * ROWS_1080_PER_WORK   # 16.0
GRAZE_ROW_SEP_1080 = GRAZE_ROW_SEP_WORK * ROWS_1080_PER_WORK       # 32.0
# Backward-compatible aliases - the names above are canonical.
GRAZE_ROW_SEP = GRAZE_ROW_SEP_1080      # [@1080]
GRAZE_FOOTPRINT = GRAZE_FOOTPRINT_WORK  # [@540] (EXPECTED_FP widening)


# ===========================================================================
# [1] Dimension ledger - same 3-tuple format as `infra_kit.INFRA_DIMENSIONS`
#     (value, "verified|estimate", source). To change a value, **update the source first**.
#     + (v1.1) "unit_cell" - the reverse contract for T1 MDL unit jitter period/origin (§4.5)
# ===========================================================================
GROUND_DIMENSIONS = {
    # -- Paving module ---------------------------------------------------
    "module_granite_slab":  (0.600, "확인", "KCS 34 6-5-1 / scene14 실측 600"),
    "module_sidewalk_block": (0.300, "확인", "보도블록 300 그리드 [ZZ_synthesis §9.3]"),
    "module_interlock_l":   (0.200, "확인", "인터로킹 200×100 [규격]"),
    "module_interlock_w":   (0.100, "확인", "동"),
    "module_deck_plank":    (0.145, "확인", "KCS 34 5-2-1 2.3.1 — 데크 판재 폭"),
    "deck_plank_gap":       (0.005, "추정", "업계 4~5 mm 이격 [추정]"),
    "deck_butt_len":        (1.25, "추정", "마구리 엇갈림 1.2~1.3 m 의 중앙 [추정]"),
    # -- Joints (all recessed. Values from the spec §1.3 proud/recess ledger) --
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
    # * U2 consistency fix: the specification text says "20 m", which is not an integer
    #    multiple of the 0.600 slab cell (33.33x) -> a double grid. Lowered to 33x = 19.80 m
    "step_expansion_ghat":  (19.80, "계산", "KCS 34 6-3 3.3.3⑻ 20 m 이하 "
                                            "+ 판석 셀 0.600 의 33배 (§4.5 U2)"),
    # -- Repair patches and cracks ---------------------------------------
    "patch_area_mean":      (0.63, "통계", "건당 0.61~0.69 ㎡ 표본 중앙"),
    "patch_proud":          (0.002, "실측", "sceneN2 PARAMS 계승"),
    "patch_cutline_proud":  (0.0012, "실측", "동"),
    "crack_w":              (0.012, "통계", "사진표본 3~15 mm 중앙"),
    "crack_recess":         (-0.006, "통계", "동 음각 3~10 mm 중앙"),
    "crack_seg":            (0.60, "추정", "폴리라인 세그 길이 [추정]"),
    # -- Trenches and gutters --------------------------------------------
    "trench_w":             (0.30, "통계-산업", "진입부 우수차단 트렌치 표준 300"),
    "trench_frame_w":       (0.040, "추정", "틀 립 폭 [추정] — 측구 줄눈 8 mm 준용 아님"),
    "trench_seat":          (0.002, "실측", "infra_kit.build_gully(seat=0.002) 계승"),
    "gutter_U_w":           (0.25, "추정", "골목 덮개식 U형 측구 표본 관측 [추정]"),
    "gutter_U_cover_len":   (2.00, "추정", "덮개 1매 길이 [추정]"),
    # -- Soiling and wear ------------------------------------------------
    "stain_proud":          (0.0006, "추정", "z-fighting 회피 최소값 = GROUND_PROUD_MIN"),
    "stain_area_mean":      (0.35, "추정", "데칼 1매 평균 면적 [추정]"),
    "wear_lane_w":          (0.90, "통계", "등산로 답압 마모 띠 6/6 표본"),
    "wear_albedo_gain":     (0.85, "통계", "동 — 노면 대비 ×0.85"),
    "edge_litter_w":        (0.25, "통계", "가장자리 유기물 띠 폭"),
    "edge_break_w":         (0.20, "실측", "재질 경계 전이대 0.15~0.25 중앙 (scene04·10)"),
    "silt_band_w":          (0.60, "추정", "침수 실트·물때 띠 [추정]"),
    # -- Membrane waterproofing (P6) -------------------------------------
    "membrane_seam_pitch":  (1.00, "시방", "우레탄 도막 롤 이음 0.9~1.1 m 중앙"),
    "membrane_albedo":      (0.19, "결재", "감독 M2 — 0.16~0.22 승인, 중앙값"),
    "membrane_proud":       (0.0006, "추정", "도막 두께(시각) [추정]"),
    # -- Anti-slip grooving (T1 first choice, ground_kit fallback) --------
    "groove_pitch":         (0.12, "법령", "주차장법 시행규칙 §6①5마 — 미끄럼방지 홈"),
    "groove_shade":         (0.72, "추정", "명도 ×0.72 [추정]"),
    # -- Weeds (vegetation - subject to the GT-E5 ramp) ------------------
    "weed_h_max":           (0.12, "추정", "밟히면 눕는 종. 상한 [추정]"),
    # -- Scatter exposure (subject to the GT-E5 ramp) --------------------
    "scatter_expose_max":   (0.06, "통계", "등산로 6/6 — φ≤0.12 반매몰 노출 ≤0.06"),
    # -- Tactile paving (statutory) --------------------------------------
    "tactile_tile":         (0.300, "법령", "교통약자법 시행규칙 별표1 2호 차목"),
    "tactile_band_depth":   (0.600, "시방", "국도 실무요령 7.5 — 점형 60 cm 표준(2줄)"),
    "tactile_setback":      (0.300, "법령", "계단 첫 단 0.3 m 전 / 볼라드 전면 0.3 m"),
    "tactile_dot_h":        (0.006, "법령", "점형 돌기 6±1 mm"),
    "tactile_bar_h":        (0.005, "법령", "선형 돌기 5±1 mm"),

    # -- (v1.1) Reverse contract - T1 MDL unit jitter ledger (§4.5) ------
    #    profile -> (cell_m, (ox, oy), source). cell_m=None means no module (jitter banned - U4)
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
    """Fetch only the value from the ledger. A missing key raises immediately - this blocks invented numbers."""
    if key not in GROUND_DIMENSIONS:
        raise KeyError(f"ground_kit: GROUND_DIMENSIONS 에 '{key}' 가 없다. "
                       "원장에 근거와 함께 먼저 등재하라.")
    return GROUND_DIMENSIONS[key][0]


# ===========================================================================
# [1b] Scatter pools - `profile["scatter"]["kind"]` -> asset pool  (v1.3, defect D-5)
#
#   Until v1.2 `apply_ground` called the scatter callback with **no `pool`**, so every
#   profile fell through to the callback default (`scene_common.VEG_DEBRIS` = 5 fallen-leaf
#   assets). A "gravel" prescription - P11 scene04, P12 scene07, P18 scene10 - therefore
#   rendered as **autumn leaves**, which is a seasonal-asset leak in every scene whose
#   identity is not already leaves `[measured - w2d_edit_g1 §5 D-5]`.
#
#   Rows are `(path relative to the vegetation asset root, effective XY cover [m2],
#   triangles)` - the same 3-tuple contract `scene_common.scatter_debris` reads, where the
#   cover feeds the count formula `n = A*(-ln(1-cover)) / mean_cov`. The kit stores only
#   **relative paths**, so §1.2 (no scene_common dependency) still holds.
#
#   Cover was measured, not estimated: every triangle of each `.usda` was projected onto
#   XY and rasterised at 2048 px on the long side (the method
#   `props_audit_w1/B_groundcover_debris.md` §6 used for VEG_DEBRIS)
#   `[measured 2026-07-30 - scratchpad measure_rocks.py]`. `zmax` (top of the rock above
#   its own origin, which is the rock **centre**) is carried so `apply_ground` can seat the
#   pool at the profile's `expose` budget instead of letting half a rock stand proud.
SCATTER_POOLS = {
    # W2-A4 procured set (audit B C3: `Rocks/rock_small_02~07,11~14`, 10 assets).
    #   rock_small_01/08/09/10/15 are the W1 five; 01 carries a root rotateXYZ, so its
    #   silhouette is not measurable in point space and it is left out of the pool.
    "gravel": [
        # path                          cover_m2  tris   (zmax 0.086/0.077/... - see below)
        ("Rocks/rock_small_02.usda",    0.0338,   460),
        ("Rocks/rock_small_03.usda",    0.0301,   432),
        ("Rocks/rock_small_04.usda",    0.0331,   378),
        ("Rocks/rock_small_05.usda",    0.0221,   480),
        ("Rocks/rock_small_06.usda",    0.0240,   392),
        ("Rocks/rock_small_07.usda",    0.0119,   496),
        ("Rocks/rock_small_11.usda",    0.0289,   436),
        ("Rocks/rock_small_12.usda",    0.0310,   400),
        ("Rocks/rock_small_13.usda",    0.0227,   398),
        ("Rocks/rock_small_14.usda",    0.0330,   428),
    ],
    "leaf": None,          # -> the callback's own default pool (VEG_DEBRIS). sceneC2 only.
}
SCATTER_POOLS["rock"] = SCATTER_POOLS["gravel"]

#   Mean top-of-rock above the asset origin over the gravel pool [m] `[measured]`. The
#   origin is the rock centre, so dropping one straight onto the ground leaves ~72 mm
#   standing proud - above the `scatter_expose_max` 0.06 m the trail statistics give. The
#   sink that `apply_ground` passes is `mean_zmax - expose`, i.e. the pool is half-buried
#   exactly as `[통계] 등산로 6/6 — φ≤0.12 반매몰` describes.
#   Residual worth an eyes-on: one `sink` has to serve every draw, and the callback's own
#   `scale_jitter` is (0.75, 1.25), so per-instance exposure spreads **0.023-0.095 m**
#   around the 0.060 target and the pool's native width (0.16-0.24 m) is wider than the
#   phi <= 0.12 the statistic describes - these are rubble, not pea gravel `[measured]`.
SCATTER_POOL_ZMAX = {"gravel": 0.0721, "rock": 0.0721}


# ===========================================================================
# [2] Camera and frame geometry - 1:1 with spec §2.1 / appendix B
# ===========================================================================
def cam_row(X, h=0.3):
    """Image row of a ground point at ground distance X [m] **[@1080]**.

    row(2.0)=497.35, row(10)=297.98. To compare against the GRAZE JSON you must move
    axes with `to_work_rows()` - the two axes differ by exactly a factor of 2.
    """
    X = max(float(X), 1e-6)
    return CAM_H / 2.0 + CAM_F * math.tan(math.atan(float(h) / X)
                                          - math.radians(-CAM_PITCH_DEG))


def cam_row_z(X, z, h=0.3):
    """Row of a point z above (below) the ground. Used where the ground drops away, e.g. a ramp."""
    X = max(float(X), 1e-6)
    return CAM_H / 2.0 + CAM_F * math.tan(math.atan((float(h) - float(z)) / X)
                                          - math.radians(-CAM_PITCH_DEG))


def surface_top_z(z):
    """**Actual rendered top z** of a recessed element.

    This is where a structural defect revealed by the first pilot round is fixed.

    The v1.1 recess implementation was "a thin plate whose top sits at `z + recess`
    (negative)". That assumed *paving is a thin surface*, whereas real scene paving is a
    **solid box** (scene15 UpperAlley = z -6.0...0.0, N5 Pave = 60 mm thick). A plate
    whose top is below the slab top is **completely trapped inside the slab and produces
    zero pixels**
    `[measured - scene15 w2_pilot round 1: joint at x=-9 (ground distance 1.00 m, d10)
     |delta|max 9.5 = no change; |delta| 0 inside the predicted manhole rectangle;
     d5 sigma_LF 0.76 -> 0.80]`.
    This is a separate cause from the skin (P-A) - turning the skin off leaves the slab
    just as solid.

    In this pipeline, with no subtraction (CSG), the only way to express a recess as
    **depth** is to build the slab split around the groove, and that is work on the scale
    of the §6.3 GT-V 4-box split. W2 follows spec §4.4 ("area and position are geometry,
    **colour difference is material**") and expresses the recess **as tone**: the top is
    raised by the z-fighting lower bound (`GROUND_PROUD_MIN`, 0.6 mm) and a dark material
    is used. The scenes already build their own joints that way
    (`sceneN5 PARAMS.joints.proud = +0.0006`) and those joints **are visible** in renders.

    The nominal recess value stays in the element ledger as `recess_nominal`, so the GT
    and specification basis is not lost.
    """
    return float(z) + GROUND_PROUD_MIN


def cam_halfwidth(X):
    """Half-width [m] entering the frame laterally at ground distance X. 0.5774*X."""
    return float(X) * math.tan(math.radians(CAM_HFOV_DEG / 2.0))


def cam_wpx(w, X):
    """Screen width [px] of a horizontal width w [m]."""
    return CAM_F * float(w) / max(float(X), 1e-6)


def cam_lpx(L, X, h=0.3):
    """Vertical projection [px] of a length L [m] along the travel axis."""
    return CAM_F * float(L) * float(h) / max(float(X), 1e-6) ** 2


def drow(x_e, d, h=0.3):
    """Row separation **[@1080]** between an edge (ground distance d) and an element x_e [m, negative] in front of it."""
    return cam_row(d + float(x_e), h) - cam_row(d, h)


def to_work_rows(rows_1080):
    """`cam_row` axis (@1080) -> GRAZE checker working-copy axis (@540). Division by 2.0."""
    return float(rows_1080) / ROWS_1080_PER_WORK


def to_1080_rows(rows_work):
    """GRAZE working-copy axis (@540) -> `cam_row` axis (@1080)."""
    return float(rows_work) * ROWS_1080_PER_WORK


def graze_row_sep_1080(d, h=0.3, band=None):
    """The **strongest enforceable** GT-E2 row separation lower bound for this shot [@1080].

    The derived strength is `GRAZE_ROW_SEP_WORK = 16` (@540 = 32 @1080, "full separation
    of two step responses"). But if the E band itself is shallower than that, it is
    **unachievable at any position within the band** `[computed]` - the d10 E band is
    ground distance 7-22 m = only **24.80 rows @540**, and from the edge row (297.97
    @1080) to each end of the band is 10.87 / 13.92 rows @540, so 16 rows cannot be
    reached. Forcing 16 on such a shot yields "zero transverse lines inside the E band",
    killing both the periodic-joint prescription of §5.1 P1 and GT-E2's own "<= 1 line"
    wording at once.

    -> **Enforce full separation (16 @540) where achievable, otherwise the footprint
      (8 @540).** Below the footprint the two responses genuinely merge and hide the
      edge, so that remains a hard failure on any shot. The verdict strength only
      **becomes stricter** than v1.1 (which always used 8 @540).
    """
    lo, hi = band or GRAZE_E_BAND
    r_e = cam_row(d, h)
    reach = max(abs(cam_row(lo * d, h) - r_e), abs(cam_row(hi * d, h) - r_e))
    return GRAZE_ROW_SEP_1080 if reach >= GRAZE_ROW_SEP_1080 \
        else GRAZE_FOOTPRINT_1080


# Travel axis -> (forward unit vector, left normal unit vector)
_AXIS_FRAME = {
    "+x": ((1.0, 0.0), (0.0, 1.0)),
    "-x": ((-1.0, 0.0), (0.0, -1.0)),
    "+y": ((0.0, 1.0), (-1.0, 0.0)),
    "-y": ((0.0, -1.0), (1.0, 0.0)),
}


class _View:
    """Scene coordinates <-> (forward s, lateral t). Handles scenes whose grid origin differs (§2.3)."""

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
        """Forward s interval of an AABB (the travel axis is +-x/+-y parallel, so 2 of the 4 corners suffice)."""
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
# [3] Elem - the atom of a plan. plan_ground alone decides prims, GT and frame budget.
# ===========================================================================
def _elem(kind, path, aabb, proud=0.0, mtl_key=None, **meta):
    """`dict(kind, path, aabb, proud, mtl_key, meta)` - spec §3.3.

    meta convention:
      line     : None | "cross" (single full-width transverse line)
                 | "cross_periodic" (periodic grid) | "long" (longitudinal line)
      area     : True for an area element (subject to B1/B2)
      decal    : True for a soiling decal (subject to B5)
      exc      : kind of GT exception registration - None | "tactile" | "scatter"
                 | "weed" | "plank_gap"
      albedo   : albedo (B9). None means undeclared = excluded from the check
      surface_z: z of the surface the element rests on (where the ground drops, e.g. a ramp)
      beyond   : True for beyond-the-edge elements (ramp surface etc.) - visible shots are limited
    """
    return dict(kind=kind, path=path,
                aabb=tuple(float(v) for v in aabb),
                proud=float(proud), mtl_key=mtl_key, meta=dict(meta))


def _seed_key(path):
    """Use only the part after `{ROOT}/GKit/` as the seed key.

    `plan_ground` does not know the prefix (`"Crack"`) while `apply_ground` passes the
    full path (`"/World/Scene15/GKit/Crack"`). Seeding on the raw path makes the two
    stages draw **different random sequences** and the prim counts diverge (they actually
    diverged by 2 prims).
    """
    p = str(path)
    tok = "/" + GKIT_PATH_TOKEN + "/"
    i = p.find(tok)
    return p[i + len(tok):] if i >= 0 else p.lstrip("/")


def _box_aabb(cx, cy, cz, sx, sy, sz):
    return (cx - sx / 2.0, cy - sy / 2.0, cz - sz / 2.0,
            cx + sx / 2.0, cy + sy / 2.0, cz + sz / 2.0)


def _obb_aabb(cx, cy, cz, L, w, t, yaw_deg):
    """The **exact** axis-aligned AABB of a yaw-rotated box.

    A square approximation (`max(L,w)`) inflates the forward s interval and throws off
    both the GT-E2 verdict and the visible-shot verdict - a real bug where the scene13
    entry trench was wrongly judged "visible" at d10 came from exactly this.
    """
    c = abs(math.cos(math.radians(yaw_deg)))
    sn = abs(math.sin(math.radians(yaw_deg)))
    hx = (L * c + w * sn) / 2.0
    hy = (L * sn + w * c) / 2.0
    return (cx - hx, cy - hy, cz - t / 2.0, cx + hx, cy + hy, cz + t / 2.0)


def _norm_region(region):
    x0, y0, x1, y1 = [float(v) for v in region]
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def _grid_ticks(a0, a1, step, o):
    """Periodic grid coordinates `o + i*step` inside `[a0, a1]`.

    **One** generator for both the builder that lays the joints and the edge guard that
    decides which of them to skip - if the two computed their ticks separately, a change
    to one would silently stop the `skip_x`/`skip_y` coordinates from matching (the skip
    lists are matched on the rounded coordinate, not on an index).
    """
    if not step or float(step) <= 0:
        return []
    step, o = float(step), float(o)
    i0 = int(math.ceil((float(a0) - o) / step - 1e-9))
    i1 = int(math.floor((float(a1) - o) / step + 1e-9))
    return [o + i * step for i in range(i0, i1 + 1)]


# ===========================================================================
# [4] The 15 new small builders - all **geometry**. Materials belong to T1 (spec §4.4).
#
#     Shared convention: the first two arguments are fixed as `(kit, path, ...)`. The return
#     is `dict(prim_count=int, elems=[Elem, ...])`. Passing `dry_kit()` as `kit` performs the
#     same computation without touching USD - plan_ground relies on this property.
# ===========================================================================
def build_joint_grid(kit, path, region, z, mtl, step_x=3.0, step_y=None,
                     width=None, recess=None, jitter=0.0, seed=0,
                     origin_xy=(0.0, 0.0), skip_x=(), skip_y=(),
                     kind="contraction"):
    """**Paving division / contraction / expansion joint grid** (recessed grooves).

    `step_y=None` -> transverse joints only (perpendicular to the travel axis). Texture
    joints have no shading and die at the h0.3 grazing angle `[measured - 09/18 sd 13-14]`
    -> they are made as geometry.

    Recess implementation **(v1.2 correction)**: the top is `surface_top_z(z)` = slab top
    +0.6 mm, and the recess reads as a **dark material (tone)**. v1.1 put the top at
    `z + recess` (negative), but because the paving slab is a solid box the plate was
    trapped entirely inside it and produced **zero rendered pixels** - see the
    `surface_top_z` docstring for the basis and measurements.
    The nominal recess value stays in the ledger as `recess_nominal`.
    **P-A (skin OFF) is still a precondition** (the skin is +6.5 to 16.5 mm).

    `origin_xy` is the grid origin - **it must equal the T1 MDL `unit_cell_origin`**
    (§4.5 U3). `skip_x/skip_y` are coordinates dropped by edge forbidden zones or openings.

    Prims: 1 per joint.  GT: recess <= 3 mm - **not a drop**.
    """
    x0, y0, x1, y1 = _norm_region(region)
    width = _dim("joint_%s_w" % kind) if width is None else float(width)
    recess = (_dim("joint_%s_recess" % kind) if recess is None
              else float(recess))
    if recess > 0:
        raise ValueError("ground_kit: 줄눈은 음각이다(recess ≤ 0). "
                         f"받은 값 {recess}")
    thick = 0.030                      # Plate thickness (only the top is visible)
    cz = surface_top_z(z) - thick / 2.0        # (v1.2) Prevents burial in the solid slab
    ox, oy = float(origin_xy[0]), float(origin_xy[1])
    rng = det_rng("gkit.joint", _seed_key(path), seed)
    n0 = kit.mark()
    elems = []

    skipx = set(round(float(v), 4) for v in skip_x)
    skipy = set(round(float(v), 4) for v in skip_y)
    for i, xx in enumerate(_grid_ticks(x0, x1, step_x, ox)):
        if round(xx, 4) in skipx:
            continue
        jx = xx + (rng.random() - 0.5) * 2.0 * jitter
        p = f"{path}/JX_{i}"
        kit.B(p, ((jx), (y0 + y1) / 2.0, cz), (width, y1 - y0, thick), mtl)
        elems.append(_elem("joint", p,
                           _box_aabb(jx, (y0 + y1) / 2.0, cz,
                                     width, y1 - y0, thick),
                           proud=GROUND_PROUD_MIN, mtl_key="joint",
                           recess_nominal=recess,
                           line="cross_periodic", albedo=0.12))
    for i, yy in enumerate(_grid_ticks(y0, y1, step_y, oy) if step_y else []):
        if round(yy, 4) in skipy:
            continue
        jy = yy + (rng.random() - 0.5) * 2.0 * jitter
        p = f"{path}/JY_{i}"
        kit.B(p, ((x0 + x1) / 2.0, jy, cz), (x1 - x0, width, thick), mtl)
        elems.append(_elem("joint", p,
                           _box_aabb((x0 + x1) / 2.0, jy, cz,
                                     x1 - x0, width, thick),
                           proud=GROUND_PROUD_MIN, mtl_key="joint",
                           recess_nominal=recess,
                           line="long", albedo=0.12))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_slab_joints(kit, path, region, z, mtl, step_x=None, step_y=None,
                      seed=0, origin_xy=(0.0, 0.0), skip_x=(), skip_y=()):
    """**Flagstone joints** - the thin preset of `build_joint_grid` (5-9 mm wide, 1-2 mm recess).

    Prims: 1 per joint.  GT: recess 2 mm - not a drop.
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
    """**Repair patch + cut line.** Default 0.7x0.9 m (0.61-0.69 m2 per patch `[statistic]`).

    Area and position are geometry (here), colour difference is material (T1) - spec §4.4.
    With `sites` the patches go at those coordinates; otherwise they are placed by
    deterministic random draw inside the region.

    Prims: 1 per patch + 4 per patch with a cut line. Only `cutline_n` patches
    (default 1 - **the near one only**) get a cut line, because the §8.2 profile estimate
    assumes 1 prim per patch.

    GT: +2 mm - not a drop.
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
    """**Crack polyline** (recessed). Texture cracks show their repeating pattern up close
    `[measured - N4]` -> they are made as individual geometry.

    Prims: **3-5 per crack** (5 when branching). §4.3 states "4-6 per crack" but the §8.2
    profile estimate (P1 "2+12" = 12 prims for 4 cracks) assumes 3 per crack - the budget
    table was adopted.
    GT: recess <= 10 mm - not a drop.
    """
    x0, y0, x1, y1 = _norm_region(region)
    seg = _dim("crack_seg") if seg is None else float(seg)
    width = _dim("crack_w") if width is None else float(width)
    rec = _dim("crack_recess")
    rng = det_rng("gkit.crack", _seed_key(path), seed)
    n0 = kit.mark()
    elems = []
    span = seg * 3.0                      # Margin so the polyline does not leave the region
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
            czc = surface_top_z(z) - 0.010      # (v1.2) Prevents burial in the solid slab
            kit.B(p, (sx, sy, czc), (seg, width, 0.020), mtl,
                  rotz=math.degrees(ang))
            elems.append(_elem("crack", p,
                               _obb_aabb(sx, sy, czc,
                                         seg, width, 0.020,
                                         math.degrees(ang)),
                               proud=GROUND_PROUD_MIN, mtl_key="crack",
                               recess_nominal=rec, albedo=0.08))
            cx = cx + math.cos(ang) * seg
            cy = cy + math.sin(ang) * seg
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_trench_drain(kit, path, x0, y0, x1, y1, z, mtl, mtl_frame=None,
                       width=None, slats=0, flush=True):
    """**Linear trench grating.** A generalisation of the `sceneN5` slat logic.

    Composition: 1 frame + 1 cover (+ n slats). The cover top sits `seat=2 mm` below the
    frame top - avoiding coplanar z-fighting, and physically correct too
    `[measured - infra_kit.build_gully(seat=0.002)]`.

    Prims: 2 (2+n in slat mode).  GT: flush - **not a drop** (uncovered mode banned).
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
    """**Covered U-type gutter** (alleys, tunnels). Runs longitudinally along the wall side.

    The L-type gutter (`infra_kit.build_gutter_L`) is for carriageway edges; in alleys and
    underpasses the **covered U type** is the observed practice `[estimate - sample
    observation]`.

    Prims: 1 + ceil(L/cover_len).  GT: flush - not a drop.
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
    """**Anti-slip grooving light/dark bands** - spec §4.4 makes **T1 (MDL stripes) the
    first choice**.

    Built as geometry, a 17 m ramp costs 140 prims `[computed]`. The default is
    **0 prims** - only a stripe request is left for T1 via `materials_needed`.
    `geom_fallback=True` is the fallback when T1 is not wired (beware the prim explosion).

    Prims: **0** (delegated to material) / 1 per groove in fallback.  GT: unchanged.
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
    """**Membrane waterproofing / anti-slip coating + wear peeling.** scene19 (rooftop),
    scene06 (footbridge).

    The albedo was fixed at **0.16-0.22** by supervisor approval M2 - the prescription for
    the worst pure-white offender. **An expansion joint grid is forbidden** on a coated
    finish (a combination that does not exist in reality, §5.6).

    Prims: 1 (coated surface) + joints + peeling.  GT: +0.6 mm - not a drop.
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
    """**Soiling decals** - tyre, oil, water stain, efflorescence, gum, soil, plinth band,
    dripping.

    Their positions depend on scene logic (around drains, along traffic lines, at the
    plinth) and cannot be controlled by an MDL procedural mask -> they are made as
    **thin plate prims** (spec §4.4).
    `grime_band` is the wall-to-floor junction band and covers **the floor side only**
    (the wall side waits for T1).

    Prims: 1 each.  GT: +1.6 to +2.3 mm - not a drop (R3 ladder rank 5 + kind).
    """
    if kind not in _STAIN_KINDS:
        raise ValueError(f"ground_kit: stain kind 는 {_STAIN_KINDS} 중 하나.")
    x0, y0, x1, y1 = _norm_region(region)
    # R3 - decal z ladder. The per-kind sub-step is what keeps `Stain_dirt` off
    # `Stain_water`'s plane where they overlap, which is the commonest coplanar pair in
    # the shipped plans (9 of 18) `[measured]`.
    pr = decal_proud("stain", _STAIN_KINDS.index(kind))
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
    """**Footprints and single-wheel tracks** (D2 poured slab). These are traces, not
    objects - unrelated to the "no person/vehicle placement" convention `[spec §11]`.

    Prims: 1 each.  GT: +1.4 mm - not a drop (R3 ladder rank 4).
    """
    pr = decal_proud("footprint")      # R3 - decal z ladder
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
    """**Trampling wear band** - a lowered-albedo strip along the walking line.
    `[statistic]` 6/6 on hiking trails.

    Prims: 1-3.  GT: unchanged (a decal on the surface, R3 ladder rank 3).
    """
    width = _dim("wear_lane_w") if width is None else float(width)
    gain = _dim("wear_albedo_gain") if albedo_gain is None else float(albedo_gain)
    pr = decal_proud("wear_lane")      # R3 - decal z ladder
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
    """**Edge organic-matter band** - organic matter swept up along both edges of a path
    (season neutral).

    Prims: 2.  GT: unchanged (R3 ladder rank 2).
    """
    width = _dim("edge_litter_w") if width is None else float(width)
    pr = decal_proud("edge_litter")    # R3 - decal z ladder
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
    """**Material boundary break-up** - a transition band over a straight boundary removes
    the "cut with a knife" look.

    The real culprit behind the "square grass seam" in scene04 was not tiling but the
    **0 px transition between the 3.0x6.0 m dirt box and the grass slab** (deltaE76 18.9)
    `[measured - team B §3]`.
    scene10 has dirt path <-> grass deltaE76 15.2 and a leaf decal outline of 27.3
    `[measured - spec §13.3]`.

    Composition: 1 prim for the transition band + (scatter is delegated to the
    `scatter_debris` callback - the `edge_bias` argument already exists and connects
    directly `[measured - scene_common.py:1805]`).

    Prims: 1 + scatter (delegated).  GT: unchanged (R3 ladder rank 0 - the floor).
    """
    width = _dim("edge_break_w") if width is None else float(width)
    pr = decal_proud("edge_break")     # R3 - decal z ladder
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
    # Transition-band scatter only means anything **inside the effective frame** - extending it
    # infinitely beyond the near window just eats budget. Cap of 35 per line (= the spec §8.2 P18 scatter allocation of 250).
    n_scat = min(35, int(round(L * float(density))))
    return dict(prim_count=kit.count_since(n0), elems=elems,
                scatter_req=[dict(line=line, width=width * 2.0,
                                  count=n_scat, edge_bias=width)])


def build_deck_planks(kit, path, x0, y0, x1, y1, z, mtl, plank_w=None,
                      gap=None, butt=None, seed=0, max_gaps=None):
    """**Deck plank division** - the scene already owns the slab, so **only the gap strips**
    are built.

    Plank width 0.145, gap 0.005 `[specification KCS 34 5-2-1 2.3.1]`. The gap is a 20 mm
    recess (inside the plank thickness - **the walking surface z is unchanged**, so it is
    not a GT drop).

    Recess implementation **(v1.3 correction, defect R1)**: the top is `surface_top_z(z)`
    = deck top +0.6 mm and the recess reads as a **dark material (tone)** - identical to
    what `cb40ae8` did for joints and manholes. v1.2 put the strip top at `z - 0.020`,
    i.e. **below** the deck surface; scene decks are solid boxes (scene12's slab spans
    z -0.14..0), so every strip was sealed inside the slab and rendered **zero pixels** -
    120 of scene12's 129 prims and 10 of scene10's 17 `[measured - w2d_edit_g2 §5 R1]`.
    Both scenes worked around it by lifting the whole plan z; that lift is removed now
    that the builder is correct, and the resulting USD is **bit-identical** to the
    worked-around geometry (`surface_top_z(z)+0.020` fed to the old formula and `z` fed to
    the new one both put the strip centre at `z - 0.0094`) `[calc]`.
    The nominal recess stays in the ledger as `recess_nominal`, exactly as joints do, so
    the GT and specification basis is not lost and B6/B7 keep treating it as a recess.

    Prims: 1 per gap (+ end grain).  GT: recess 20 mm - not a drop.
    """
    plank_w = _dim("module_deck_plank") if plank_w is None else float(plank_w)
    gap = _dim("deck_plank_gap") if gap is None else float(gap)
    butt_len = _dim("deck_butt_len") if butt is None else float(butt)
    x0, y0, x1, y1 = _norm_region((x0, y0, x1, y1))
    thick = 0.020                      # Strip thickness (only the top is visible)
    cz = surface_top_z(z) - thick / 2.0        # (v1.3) Prevents burial in the solid slab
    recess = -thick                    # Nominal groove depth, kept for GT (§6.1)
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
        kit.B(p, (xx, (y0 + y1) / 2.0, cz), (gap, y1 - y0, thick), mtl)
        elems.append(_elem("plank_gap", p,
                           _box_aabb(xx, (y0 + y1) / 2.0, cz,
                                     gap, y1 - y0, thick),
                           proud=GROUND_PROUD_MIN, mtl_key="deck_gap",
                           recess_nominal=recess,
                           line="cross_periodic", exc="plank_gap",
                           deck=True, albedo=0.06))
    nb = max(0, int((y1 - y0) / butt_len) - 1)
    for i in range(nb):
        yy = y0 + (i + 1) * butt_len
        q = f"{path}/Butt_{i}"
        kit.B(q, ((x0 + x1) / 2.0, yy, cz), (x1 - x0, gap, thick), mtl)
        elems.append(_elem("plank_butt", q,
                           _box_aabb((x0 + x1) / 2.0, yy, cz,
                                     x1 - x0, gap, thick),
                           proud=GROUND_PROUD_MIN, mtl_key="deck_gap",
                           recess_nominal=recess, line="long",
                           exc="plank_gap", deck=True, albedo=0.06))
    return dict(prim_count=kit.count_since(n0), elems=elems)


def build_silt_band(kit, path, region, waterline, z, mtl, width=None,
                    albedo_gain=0.80, n=2):
    """**Flood silt / water stain / sand drift band** - waterline traces at waterfronts
    (03/09/12/18).

    Prims: 1-2.  GT: unchanged (R3 ladder rank 1).
    """
    x0, y0, x1, y1 = _norm_region(region)
    width = _dim("silt_band_w") if width is None else float(width)
    pr = decal_proud("silt_band")      # R3 - decal z ladder
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


# -- Adapters for the 6 reused infra_kit builders (not reimplementation - they only attach planning Elems) --
def _ik_manhole(kit, path, cx, cy, z, mtl, mtl_frame=None, d_frame=0.648):
    """Adapter for `infra_kit.build_manhole`. **Folds the flush offset to be non-negative.**

    (v1.2) With `proud=None`, `build_manhole` draws the KS D 4040 "level with the road
    surface, +-10 mm" as a deterministic `U(-10, +10) mm`. A negative draw puts the cover
    top below the paving top, and because the paving is a **solid slab** the cover and
    frame are trapped entirely inside it, producing **zero rendered pixels**
    `[measured - scene15 (-2.40,-0.15) drew -1.73 mm -> |delta| = 0 over the manhole area
     in every shot d2/d5/d10/overview. scene13 (-3.90,0.00) drew -9.07 mm, same state]`.
    Across all 33 scenes **about half** the draws were in this state.

    With no subtraction geometry a "sunken cover" cannot be expressed as depth, so the
    deviation is **folded** (`|raw|`) into a **proud deviation** of 0.6-10 mm. In reality
    frames often sit slightly above the road after resurfacing or settlement, and the
    original intent (that a deviation exists at all, since "all exactly the same height
    reads as CG") is fully preserved.
    """
    n0 = kit.mark()
    raw = ik.det_rng("manhole", path, cx, cy).uniform(-0.010, 0.010)
    pr_use = GROUND_PROUD_MIN + abs(raw)
    r = ik.build_manhole(kit, path, cx, cy, z, mtl, frame_mtl=mtl_frame,
                         d_frame=d_frame, lid=True, proud=pr_use)
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


def _marking_local_box(r, kw):
    """Local-frame extent of a `build_road_marking` result: `(lx0, ly0, lx1, ly1)`.

    `infra_kit` lays every marking with **+X = length, +Y = width** and then rotates the
    whole thing about `(x0, y0)` by `yaw_deg`, so the exact world AABB is this box rotated
    (see `_marking_aabb`). One entry per `kind` the builder supports.
    """
    kind = r.get("kind")
    lw = float(kw.get("line_w", 0.15))
    if kind == "parking":
        total = float(r["n_stall"]) * float(r["stall"][0])
        return (-lw / 2.0, -lw / 2.0, total + lw / 2.0,
                float(r["stall"][1]) + lw / 2.0)
    if kind == "crosswalk":
        return (0.0, 0.0, float(kw.get("band_w", 4.00)),
                float(r.get("walk_len", 8.00)))
    # "line" - a single stripe of `length` along +X, `line_w` wide, centred on y = 0.
    L = float(r.get("length", 3.0))
    w = max(float(r.get("width", 0.15)), 0.15)
    return (0.0, -w / 2.0, L, w / 2.0)


def _marking_aabb(x0, y0, z, yaw_deg, local, t=0.003):
    """Exact world AABB of a local-frame box rotated by `yaw_deg` about `(x0, y0)`.

    (v1.3, defect F1) v1.2 built this as `_box_aabb(x0 + L/2, y0, ..., L, w, ...)` - it
    laid the length along **+X regardless of `yaw_deg`** while the *same* function
    classified the line as `cross`/`long` **using** the yaw. Any transverse marking was
    therefore judged as if it ran along +X: sceneD2's opening-perimeter west leg tripped
    B8 (void intersection) and B6 (edge standoff) on geometry that is clear of both, and
    the leg had to be deferred `[measured - w2d_edit_gb §5 F1]`. scene13/N4/D1's yaw-0
    lane lines never showed it, which is why it survived.
    """
    a = math.radians(float(yaw_deg))
    ca, sa = math.cos(a), math.sin(a)
    lx0, ly0, lx1, ly1 = local
    xs, ys = [], []
    for lx, ly in ((lx0, ly0), (lx1, ly0), (lx1, ly1), (lx0, ly1)):
        xs.append(float(x0) + lx * ca - ly * sa)
        ys.append(float(y0) + lx * sa + ly * ca)
    return (min(xs), min(ys), float(z), max(xs), max(ys), float(z) + float(t))


def _ik_marking(kit, path, kind, mtl, x0, y0, z, yaw_deg=0.0, **kw):
    n0 = kit.mark()
    r = ik.build_road_marking(kit, path, kind, mtl, x0, y0, z,
                              yaw_deg=yaw_deg, **kw)
    line = "cross" if 45.0 < (abs(yaw_deg) % 180.0) < 135.0 else "long"
    return dict(prim_count=kit.count_since(n0), elems=[
        _elem("marking", path,
              _marking_aabb(x0, y0, z, yaw_deg, _marking_local_box(r, kw)),
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
    """**One GT change - executed in W2 under supervisor approval M4** (labels come with the
    W4 GT map).

    The `offset` argument in the v1 notation **does not exist**
    `[measured - infra_kit.py:778-781]`. To stand the curb off the wall, reduce `width`
    and set `y_neg/y_pos` directly.
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
# [5] The 18 profiles - spec §4.1 / §5 matrix
#
#     Schema: doc, natural, pave, infra, surface, extras, scatter,
#             tactile (fixed None), albedo_cap, prim_cap
#     Putting urban infrastructure into a `natural=True` profile makes plan_ground raise ValueError.
# ===========================================================================
_URBAN_INFRA_KEYS = ("manhole", "gully", "gutter_L", "gutter_U", "marking",
                     "trench")

# What `overrides[key] = None` clears a profile key **to** (§F2 explicit-clear semantic).
# Keys absent from the table clear to `None`.
_OVERRIDE_EMPTY = {"pave": dict, "infra": dict, "surface": tuple,
                   "extras": tuple, "scatter": lambda: None}


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
                  groove_w=0.010, recess=-0.003),   # §3.4 schema example, §5.4 15-1
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
    # -- P18 (new in v1.1) -----------------------------------------------
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
    # -- P3 sub-variants -------------------------------------------------
    "tunnel_under": _P(
        "지하보도(P3 하위변종) [추정 지하보도 관행]",
        pave=dict(module=(0.300, 0.300), joint="interlock",
                  step_x=3.0, step_y=None),
        infra=dict(gutter_U=1, trench=1),
        surface=(("stain", ("grime_band", "efflorescence")),),
    ),
}


# ===========================================================================
# [6] Tactile paving register - spec §12.4. **Not listed here means installation is banned** (gate B11)
#     The GT column is A (z unchanged) throughout - flush plus 6 mm dots is not a drop `[statute]`.
# ===========================================================================
def _T(kind, site, p, trigger, defect=None, relief="normal", walk_axis="x",
       note=""):
    return dict(kind=kind, site=site, p=float(p), trigger=trigger,
                defect=defect, relief=relief, walk_axis=walk_axis, note=note)


TACTILE_SITES = {
    # 6 newly added scenes
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
    # 3 retained scenes
    "sceneD4": {"platform_edge": _T("dot", "연단 0.30 m 이격 2열", 0.90,
                                    "승강장 연단", note="완전 적정")},
    "sceneC4": {"stair_top": _T("dot", "계단머리 경고 점형", 0.51, "계단 첫 단",
                                defect="위치 오류 0.6~1.0 m")},
    "sceneC1": {"stair_top": _T("dot", "계단머리 경고 점형", 0.51, "계단 첫 단",
                                defect="색 바램·오염 −40 %",
                                note="적설 0.05 m 에 매몰되는 것이 씬 특색")},
    # 4 scenes retained in front of bollards (all drop-free = cue+/label-)
    "sceneN1": {"bollard": _T("dot", "볼라드 전면 연속 띠 0.60", 0.54, "볼라드 전면")},
    "sceneN2": {"bollard": _T("dot", "볼라드 전면 연속 띠 0.60", 0.54, "볼라드 전면")},
    "sceneN4": {"bollard": _T("dot", "볼라드 전면 연속 띠 0.60", 0.54, "볼라드 전면")},
    # * One spec conflict - §12.5 (3) allows relief="geom" at one N5 site, but
    #   dot geom costs **721 prims** for a 0.6x3.0 m strip (§4.2), and the continuous strip
    #   in front of the N5 bollard row is 7.0 m -> **1,706 prims** = 8.5x the §8.1 absolute cap of 200.
    #   -> W2 executes with relief="normal" (1 prim) and produces the shading of the 36 dots
    #     via the `tactile_yellow_diff/nor` texture wiring (T1) as §12.5 (3) prescribes.
    #     The original intent is left in `relief_wanted` for the supervisor to judge.
    "sceneN5": {"bollard": _T("dot", "볼라드 열 전면 연속 띠 0.60", 0.54,
                              "볼라드 전면", relief="normal",
                              note="§12.5 ③ 의 relief='geom' 의도는 프림 절대상한 "
                                   "200(§8.1)과 비양립 — 텍스처 배선으로 대체")},
}

# Ledger of non-installation reasons - the code remembers "why it was not placed" (used in the B11 diagnostic message)
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
# [7] EXPECTED_FP - pre-registration of false positives for GT-E2-x registered exceptions (spec §12.3)
#
#     The round judge does **not count** GRAZE responses in these row ranges as new false positives.
#     Rows are not hard-coded but **computed from the statutory geometry** - so the same rule
#     reproduces even when stair width and origin differ per scene.
#     Registered range = [edge row, **the farthest boundary row that fell short of that shot's separation bound**].
#     d2 passes on its own (delta 42.9 @1080 = 21.4 @540 >= 16 @540) and needs no registration.
#
#     * (v1.2) **Consumer axis alignment** - per red team G-1. The consumer of this register is
#       the GRAZE JSON (`gz_row`, bands) and that is on **@540**. The register exports both axes:
#       `rows` (=@1080, keeping the spec §12.3 notation) + `rows_work` (@540).
#       The round judge must use `rows_work`. Matching on one axis alone would
#       never align a single row.
# ===========================================================================
def tactile_fp_rows(dists=(2, 5, 10), h=0.3, setback=None, depth=None):
    """False-positive registration row range of a statutory tactile strip (`setback` in front of
    the edge, `depth` wide).

    Returns `{d: (lo_1080, hi_1080)}` - **@1080**. Convert to @540 with `_fp_work()`.
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
    """Move the registered range onto the GRAZE consumer axis (@540) and widen it by the footprint."""
    lo, hi = rows_1080
    return (int(math.floor(to_work_rows(lo))) - GRAZE_FOOTPRINT_WORK,
            int(math.ceil(to_work_rows(hi))) + GRAZE_FOOTPRINT_WORK)


# Statutory triggers accompanied by a drop edge - only these sites need GRAZE false-positive pre-registration
_FP_TRIGGERS = ("계단 첫 단", "계단 마지막 단", "승강장 연단", "개구 둘레")


def _build_expected_fp():
    fp = {}
    rows = tactile_fp_rows()
    for scene, sites in TACTILE_SITES.items():
        for site, spec in sites.items():
            if spec["trigger"] not in _FP_TRIGGERS:
                continue          # Bollard frontages and main entrances have no drop edge
            for d, (r0, r1) in rows.items():
                fp[(scene, f"preset_h0.3_d{d}")] = dict(
                    rows=(r0, r1), scale=CAM_H,          # @1080 (spec §12.3)
                    rows_work=_fp_work((r0, r1)),        # @540  (GRAZE consumer)
                    scale_work=GRAZE_WORK_H,
                    src=f"tactile_{site}")
    return fp


EXPECTED_FP = _build_expected_fp()


# ===========================================================================
# [8] Scene-specific invariant register - gate B12 (spec §7.3)
#     `plan_ground` calls these over every element AABB; a single False raises ValueError.
#     If a scene has its own checker (e.g. sceneN1.dresscheck), **do not reimplement it** -
#     inject it via `plan_ground(..., invariants=[...])`.
# ===========================================================================
def _inv_n1_band(elem, ctx):
    """N1 band preservation - the only occluder may be the single airborne slab.
    `xb + 0.84536*h < 0.0` (front placement) or `xa > 4.0` (rear placement)."""
    xa, _, _, xb, _, z1 = elem["aabb"]
    h = max(0.0, z1 - ctx.get("z", 0.0))
    return (xb + 0.84536 * h < 0.0) or (xa > 4.0)


def _inv_n3_painting(elem, ctx):
    """N3 trompe-l'oeil: **no area elements** over the painted surface x in [0, 6.3] (joints crossing it are intended)."""
    if not elem["meta"].get("area"):
        return True
    xa, _, _, xb, _, _ = elem["aabb"]
    return xb <= 0.0 or xa >= 6.3


def _inv_hidden_illusion(elem, ctx):
    """14/20/21/N3 concealed-illusion integrity - no permanently high-contrast cue."""
    m = elem["meta"]
    if elem["kind"] == "tactile":
        return False
    if m.get("line") == "cross" and (m.get("albedo") or 0.0) > 0.28:
        return False
    return True


def _inv_13_ramp_d2only(elem, ctx):
    """13 ramp crest concealment - elements on the ramp must be [F] at d2 only."""
    if not elem["meta"].get("beyond"):
        return True
    return tuple(elem["meta"].get("vis_dists", ())) in ((), (2,), (2.0,))


def _inv_10_trail_cut(elem, ctx):
    """10 upper trail stops at x = -1.5 (no ground plane over the stair void)."""
    xa, _, za, xb, _, zb = elem["aabb"]
    if xb <= -1.5:
        return True
    return zb > -6.0 and elem["meta"].get("deck", False)


def _inv_c1_snow(elem, ctx):
    """C1 snow burial is the scene identity - new elements must have proud <= the snow thickness 0.05."""
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
# [9] plan_ground - profile -> plan (pure computation, no USD contact)
# ===========================================================================
def _edge_list(edges):
    """Normalise edges -> [(name, s, opts)]."""
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
    """Minimum forward clearance [m] between an element's forward s interval and an edge.
    None if there is none. 0.0 if the element crosses or touches the edge."""
    if not edges:
        return None
    sa, sb = view.s_span(elem["aabb"])
    best = None
    for _n, se, _o in edges:
        if sa >= se:                       # Beyond-the-edge element - not subject to GT-E1'
            continue
        gap = max(0.0, se - sb)
        best = gap if best is None else min(best, gap)
    return best


def _vis_dists(view, elem, edges, dists, h):
    """Visible-shot decision for beyond-the-edge elements (ramp surface etc.). Ray slope h/d > surface gradient."""
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
    """Profile + region -> **GroundPlan**. Creates no USD.

    This function alone must be able to decide prim count, GT and frame budget - so that
    `python3 ground_kit.py` can check all 33 scene plans before touching USD.

    Raises `ValueError` on:
      - urban infrastructure in a `natural=True` profile (§3.4)
      - GT delta exceeded (unregistered exception element), GT-E1' (B6), GT-E2 (B7), GT-V (B8)
      - albedo cap (B9), prim/instance budget (B10)
      - tactile paving not registered in `TACTILE_SITES` (B11), scene-specific invariants (B12)
    """
    if profile not in GROUND_PROFILES:
        raise ValueError(f"ground_kit: 미등록 프로파일 '{profile}'. "
                         f"등록: {sorted(GROUND_PROFILES)}")
    prof = dict(GROUND_PROFILES[profile])
    if overrides:
        for k, v in dict(overrides).items():
            if v is None:
                # (v1.3, defect F2) **Explicit clear.** `infra=None` drops every key the
                # profile declared. Before this there was no way to say "clear": a dict
                # override is *merged*, so `infra=dict()` silently kept the whole urban
                # infra set - sceneC2 asked for `infra=dict()` and still got 1 manhole +
                # 2 gullies + 1 L-gutter, 12 prims, on a row whose spec says "urban
                # infrastructure 0" `[measured - w2d_edit_gb §5 F2]`.
                prof[k] = _OVERRIDE_EMPTY.get(k, lambda: None)()
            elif isinstance(v, dict) and isinstance(prof.get(k), dict):
                if not v:
                    # An empty merge is a no-op, and it is a no-op that *looks* like a
                    # clear. Refusing it is the whole point of F2 - staying silent is how
                    # the defect shipped.
                    raise ValueError(
                        f"ground_kit: overrides['{k}'] = {{}} 는 아무 것도 하지 "
                        f"않는다(사전 오버라이드는 **병합**이다). 프로파일 값을 "
                        f"비우려면 `{k}=None`, 일부만 끄려면 0/() 를 명시하라 "
                        "(예: infra=dict(manhole=0, gully=0, gutter_L=0)).")
                d = dict(prof[k]); d.update(v); prof[k] = d
            else:
                prof[k] = v

    # -- Enforce the §3.4 convention: no urban infrastructure in natural scenes --
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

    # -- A plan is a list of ops. A dry run yields the elems and prim count --
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

    # Scatter (profile declaration + edge_break request) - delegated to the `scatter_debris` callback
    inst = 0
    sc_spec = prof.get("scatter")
    if sc_spec:
        inst += int(sc_spec.get("count", 0))
    inst += sum(int(s.get("count", 0)) for s in scat_reqs)

    # -- Visible shots, GT-E5 clamp -------------------------------------
    for e in elems:
        e["meta"]["vis_dists"] = _vis_dists(view, e, ed, dists, h0)
        e["meta"]["edge_gap"] = _nearest_edge_gap(view, e, ed)
        sa, _sb = view.s_span(e["aabb"])
        if any(o.get("beyond_grade") is not None and sa >= se - 1e-9
               for _n, se, o in ed):
            e["meta"]["beyond"] = True         # On the ramp surface = d2 only (§5.0 C-2)

    _clamp_gt_e5(elems, view, ed)

    plan = dict(profile=profile, scene=scene, elements=elems,
                materials_needed=mats, scatter_req=scat_reqs,
                prims=prims, instances=inst, ops=ops,
                # (v1.3, part of D-5) The **effective** scatter prescription, i.e. after
                # `overrides`. `apply_ground` used to re-read `GROUND_PROFILES[...]`
                # directly, so a scene that overrode the scatter got the plan's count in
                # the B10 budget and the *profile's* count in the USD - scene10 planned
                # 120 and applied with max_count 180 `[measured]`.
                scatter=(dict(sc_spec) if sc_spec else None),
                gt=dict(delta=GT_DELTA), gt_changes=gt_changes, ctx=ctx,
                unit_cell=GROUND_DIMENSIONS["unit_cell"].get(profile))
    _assert_unit_cell(profile, prof)

    # -- Gates (B6-B12, hard) -------------------------------------------
    b = frame_budget(plan, h=h0, dists=dists)
    plan["budget"] = b
    hard = [k for k in ("B6", "B7", "B8", "B9", "B10", "B11", "B12")
            if not b["gates"][k]["pass"]]
    if hard:
        msgs = "\n  ".join(f"{k}: {b['gates'][k]['detail']}" for k in hard)
        raise ValueError(f"ground_kit: plan_ground 게이트 위반 "
                         f"[{profile}/{scene}]\n  {msgs}")

    # B12 - scene-specific invariants (register + scene-injected callbacks)
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
    """§4.5 U1-U4 - T1 unit jitter contract consistency. A violation raises ValueError."""
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
    """GT-E5 ramp - vegetation and scatter get lower the closer they are to the edge (a clamp,
    not a ban).

    `z_e <= min(per-kind cap, |x_e| / EDGE_K)`. If the per-kind minimum still cannot be met
    after clamping, the element is marked dropped (`meta["dropped"]=True`).
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
# [10] frame_budget - decide B1-B12 without rendering (spec §7.1)
# ===========================================================================
def _gate(ok, detail, hard=True):
    return dict(**{"pass": bool(ok)}, detail=detail, hard=bool(hard))


def frame_budget(plan, *, h=0.3, dists=None, gy=None, origin=None):
    """Decide element pixel occupancy, occlusion and GT rule violations for each h0.3 shot
    without rendering.

    B1-B5 are **frame-fill targets** (WARN - the final verdict comes from sigma_LF/sd after
    rendering); B6-B12 are **hard gates** (a violation makes `plan_ground` raise).
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
        # Ground distance of an edge = d + s_edge (with the standard convention edge s=0 -> exactly d).
        # Scenes with a different origin also pass `edges` as forward s, so the same formula holds.
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
            # An out-of-frame verdict requires **both edges off the same side**.
            # Writing it as `min(|ta|,|tb|) > hw` drops full-width elements crossing the screen
            # (trenches, tactile strips) entirely - which is exactly what happened to scene13 d2.
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
                z_e = 0.0            # Plank gap = recess. §6.1 exception table, "required clearance 0"
            if m.get("recess_nominal") is not None:
                # (v1.2) Nominally recessed element - the +0.6 mm of the rendered z is a
                # z-fighting epsilon, not real relief. GT-E1' must judge on real
                # relief, so the nominal value (<=0) is used.
                z_e = min(0.0, float(m["recess_nominal"]))
            if gap is not None and z_e > 0:
                need = EDGE_K * z_e
                if gap + 1e-9 < need and m.get("exc") != "tactile":
                    e1_viol.append((e["path"], round(gap, 3), round(need, 3)))
                elif m.get("exc") == "tactile" and gap + 1e-9 < need:
                    e1_viol.append((e["path"], round(gap, 3), round(need, 3)))
            # -- B7 GT-E2 (full-width transverse lines inside the E band) --------
            if m.get("line") in ("cross", "cross_periodic") and r_edge:
                if m.get("exc") == "plank_gap":
                    continue         # Recessed plank gaps are not subject to GT-E2 (§6.1)
                if not (e_lo <= Xm <= e_hi):
                    continue
                surf = m.get("surface_z", 0.0)
                # All rows are **@1080** (the `cam_row` axis). The verdict bound is converted
                # to the same axis before comparing - v1.1 compared an @540 derivation directly against @1080.
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

    # -- B8 GT-V: element AABB x opening intersection = 0 ----------------
    v_hits = []
    for e in elems:
        if e["meta"].get("dropped"):
            continue
        x0, y0, _z0, x1, y1, _z1 = e["aabb"]
        for vx0, vy0, vx1, vy1 in ctx["voids"]:
            if x1 > vx0 and x0 < vx1 and y1 > vy0 and y0 < vy1:
                v_hits.append((e["path"], (vx0, vy0, vx1, vy1)))
    # -- B9 Albedo -------------------------------------------------------
    a_hits = []
    for e in elems:
        a = e["meta"].get("albedo")
        if a is None:
            continue
        cap = TACTILE_ALBEDO_CAP if e["meta"].get("exc") == "tactile" \
            else prof["albedo_cap"]
        if a > cap + 1e-9:
            a_hits.append((e["path"], a, cap))
    # -- B10 Budget ------------------------------------------------------
    over = []
    if plan["prims"] > prof["prim_cap"]:
        over.append(f"기하 프림 {plan['prims']} > {prof['prim_cap']}")
    if plan["prims"] > 200:
        over.append(f"절대 상한 200 초과 ({plan['prims']})")
    if plan["instances"] > prof["inst_cap"]:
        over.append(f"산포 {plan['instances']} > {prof['inst_cap']}")
    # -- B11 Unauthorised tactile paving ---------------------------------
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
# [11] apply_ground - plan -> USD (layer 3)
# ===========================================================================
_MISSING = object()


def _scatter_pool_kw(scatter_fn, spec):
    """Extra kwargs that pin the scatter callback to the profile's asset pool (D-5).

    Returns `{}` when the prescription names no kind, when the kind maps to the callback's
    own default (`leaf`), or when the injected callback predates the `pool=` contract -
    the kit must degrade to v1.2 behaviour rather than crash a render on a signature
    mismatch.
    """
    kind = (spec or {}).get("kind")
    pool = SCATTER_POOLS.get(kind) if kind else None
    if not pool:
        if kind and kind not in SCATTER_POOLS:
            raise ValueError(
                f"ground_kit: 산포 kind '{kind}' 가 SCATTER_POOLS 에 없다. "
                f"등재: {sorted(SCATTER_POOLS)} — 계절 자산 유출을 막으려면 "
                "풀을 먼저 등재하라(D-5).")
        return {}
    try:
        params = inspect.signature(scatter_fn).parameters
    except (TypeError, ValueError):             # builtins / C callables
        return {}

    def takes(name):
        return (name in params
                or any(p.kind is inspect.Parameter.VAR_KEYWORD
                       for p in params.values()))

    if not takes("pool"):
        print("[ground_kit][경고] 산포 콜백이 pool= 을 받지 않는다 — "
              f"kind '{kind}' 처방이 콜백 기본 풀로 떨어진다(D-5).")
        return {}
    kw = dict(pool=list(pool))
    expose = (spec or {}).get("expose")
    zmax = SCATTER_POOL_ZMAX.get(kind)
    if expose is not None and zmax is not None and takes("sink"):
        # The asset origin is the rock centre, so `sink = zmax - expose` leaves exactly
        # the prescribed exposure standing proud (`scatter_expose_max` 0.06 m).
        kw["sink"] = round(float(zmax) - float(expose), 6)
    return kw


def apply_ground(kit, prefix, plan, mtls, *, skin_exclude=None, scatter=None,
                 slabs=()):
    """Turn a plan into real USD prims.

    `skin_exclude`: **inject** the `scene_common.skin_exclude` callback (keeping the
      no-scene_common-dependency principle - spec §1.2). It takes the ground slab paths
      that ground_kit decorates as `slabs` and **explicitly excludes** them from skinning
      (P-A). Without this, flush elements (manhole 2 mm, dot block 4 mm) are buried by the
      skin (+6.5 to 16.5 mm).

    Returns: `{"prims", "instances", "elements", "gt_delta_max", "gt_changes"}`
    """
    if GKIT_PATH_TOKEN not in str(prefix):
        raise ValueError(f"ground_kit: prefix 는 '{{ROOT}}/{GKIT_PATH_TOKEN}' "
                         f"이어야 한다(2차 스킨 방어, §1.2). 받은 값: {prefix}")
    # -- P-A: skin OFF for the target slabs ------------------------------
    #    **Placed before GKIT_ON** - the skin state must be identical in the OFF arm too,
    #    so that the A/B measures only "the effect of the kit prims" (§C2).
    if skin_exclude is not None and slabs:
        skin_exclude(*[str(s) for s in slabs])

    # -- [W2-C, C2] Diagnostic OFF arm ----------------------------------
    if not GKIT_ON:
        print("[ground_kit] ** NEGOBS_GKIT=0 — 요소 0개 (C2 A/B OFF 팔) ** "
              f"계획상 {len(plan['elements'])}요소 / {len(plan['ops'])}op 생략")
        # The key set must be **identical** to the normal return - scene integration reads
        # res[...] directly, so a missing key kills the OFF arm alone with KeyError (this happened).
        return dict(prims=0, instances=0, elements=[], gt_delta_max=0.0,
                    gt_change_max=0.0, gt_changes=[], materials_needed=[],
                    unit_cell=plan["unit_cell"], gkit_off=True)

    # -- GT delta pre-check - raised **before** creation -----------------
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
            # Only an **approved GT change** may exceed delta (current target: the scene13 ramp curb
            # h0.12, supervisor approval M4). It must be listed in the `gt_changes` ledger -
            # this structurally prevents silently creating an unlabelled drop (§6.4).
            if not plan["gt_changes"]:
                raise ValueError(
                    f"ground_kit: GT 변경 요소 {e['path']} 가 gt_changes 원장에 "
                    "없다. 승인 없는 낙차 신설은 금지(§6.4).")
            gchange_max = max(gchange_max, z)
            continue
        gmax = max(gmax, z)

    # -- Albedo hard clamp (§3.1) ---------------------------------------
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
        raw_kw, raw_args = dict(op.get("kw", {})), tuple(op.get("args", ()))
        kw, handled = dict(raw_kw), set()
        # mtl_key -> substituted with the real material object
        for k in list(kw):
            if k in ("mtl", "mtl_frame", "mtl_cover") and isinstance(kw[k], str):
                kw[k] = mtls.get(kw[k]); handled.add(k)
            if k == "mtls" and isinstance(kw[k], dict):
                kw[k] = {kk: mtls.get(vv) if isinstance(vv, str) else vv
                         for kk, vv in kw[k].items()}
                handled.add(k)
        args = tuple(mtls.get(a[1:]) if (isinstance(a, str) and
                                         a.startswith("@")) else a
                     for a in raw_args)
        # -- Guard against unsubstituted material references (prevents a repeat of the pilot round-1 crash) --
        #    It inspects the **op definition (before substitution)** - sniffing the substituted
        #    result by type gives false positives in tests where the `mtls` values are strings.
        #    A positional material dict is not covered by the substitution rules at all and is
        #    therefore always a defect, and an unhandled `mtl*` string kw is a defect too. `dry_kit`
        #    does not Bind, so this is the only way a CPU self-check can see the defect before rendering.
        bad = [f"arg[{i}]={v!r}" for i, v in enumerate(raw_args)
               if isinstance(v, dict) and len(v) > 0
               and all(isinstance(x, str) for x in v.values())]
        bad += [f"{k}={v!r}" for k, v in raw_kw.items()
                if k not in handled
                and ((isinstance(v, str) and v.startswith("@"))
                     or (k.startswith("mtl") and isinstance(v, (str, dict))))]
        if bad:
            raise ValueError(
                f"ground_kit: op '{op['name']}' 에 미치환 재질 참조가 남았다 "
                f"{bad} — 재질 사전은 kw `mtls=`, 단일 재질은 '@키' 또는 "
                f"kw `mtl*=` 로만 넘길 수 있다(apply_ground 치환 규칙).")
        m0 = kit.mark()
        op["fn"](kit, f"{prefix}/{op['path'].lstrip('/')}", *args, **kw)
        n_prims += kit.count_since(m0)

    # -- Scatter - delegated to the `scene_common.scatter_debris` callback (no new function) --
    n_inst = 0
    if scatter is not None:
        stage = getattr(kit, "stage", None)
        # (v1.3, defect D-5) Resolve the profile's **scatter kind** to an asset pool.
        #   Until v1.2 the callback was called with no `pool`, so every profile - gravel
        #   included - fell through to `VEG_DEBRIS`, i.e. autumn leaves, and scenes 07/10
        #   (P12/P18) shipped a seasonal-asset violation. `sink` seats the pool at the
        #   profile's own `expose` budget instead of leaving half a rock proud.
        sp = plan.get("scatter", _MISSING)
        if sp is _MISSING:                      # Plan built before v1.3
            sp = GROUND_PROFILES[plan["profile"]].get("scatter")
        pool_kw = _scatter_pool_kw(scatter, sp)
        for i, s in enumerate(plan["scatter_req"]):
            (ax, ay), (bx, by) = s["line"]
            w = float(s["width"]) / 2.0
            n = scatter(stage, f"{prefix}/Scatter_Edge_{i}",
                        min(ax, bx) - w, min(ay, by) - w,
                        max(ax, bx) + w, max(ay, by) + w,
                        plan["ctx"]["z"], cover=0.10,
                        seed=det_seed("gkit.scatter", prefix, i),
                        edge_bias=float(s.get("edge_bias", 0.0)),
                        max_count=int(s["count"]), **pool_kw)
            n_inst += int(n or 0)
        if sp:
            x0, y0, x1, y1 = plan["ctx"]["region"]
            n = scatter(stage, f"{prefix}/Scatter_Field", x0, y0, x1, y1,
                        plan["ctx"]["z"], cover=float(sp.get("cover", 0.15)),
                        seed=det_seed("gkit.scatter.field", prefix),
                        max_count=int(sp.get("count", 0)), **pool_kw)
            n_inst += int(n or 0)

    return dict(prims=n_prims, instances=n_inst,
                elements=plan["elements"], gt_delta_max=gmax,
                gt_change_max=gchange_max,
                gt_changes=plan["gt_changes"],
                materials_needed=plan["materials_needed"],
                unit_cell=plan["unit_cell"])


# ===========================================================================
# [12] Scene integration helpers - §7.4 "the source of truth for coordinates is the scene PARAMS"
# ===========================================================================
def region_from_params(params, key, pad=0.0):
    """Turn x0/x1/y0/y1 of the scene `PARAMS[key]` into a region. No hard-coded document coordinates."""
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
# [13] ops assembly - profile prescription -> builder call list
# ===========================================================================
def _op(name, fn, path, args=(), kw=None):
    return dict(name=name, fn=fn, path=path, args=tuple(args), kw=dict(kw or {}))


def _tick_guarded(ctx, s_tick, half_w=0.0):
    """Would a transverse line at forward s = `s_tick` fail GT-E2 on any shot?

    The arithmetic is **the same one `frame_budget` B7 runs**: an element counts only if
    its ground distance sits inside the GRAZE E band `[0.7d, 2.2d]`, and it fails if its
    row is closer to the edge row than `graze_row_sep_1080(d)`. `half_w` is half the joint
    width, so the two rims are tested exactly as B7 tests `sa`/`sb`.
    """
    h0 = ctx["heights"][0]
    for _n, se, _o in ctx["edges"]:
        for d in ctx["dists"]:
            Xm = d + s_tick
            if not ((GRAZE_E_BAND[0] * d) <= Xm <= (GRAZE_E_BAND[1] * d)):
                continue
            r_edge = cam_row(d + se, h0)
            worst = min(abs(cam_row(max(0.05, d + s_tick + o), h0) - r_edge)
                        for o in (-half_w, +half_w))
            if worst < graze_row_sep_1080(d, h0):
                return True
    return False


def _edge_guard_ticks(ctx, step_x, step_y, origin_xy, width=0.0):
    """Filter out the transverse joint coordinates in front of an edge that cannot meet
    GT-E2. Returns `(skip_x, skip_y)` in **world** coordinates.

    A generalisation of spec §5.4 15-1 "exclude x=0 (edge forbidden zone)". Even in a
    periodic grid, **the one line stuck to the edge** contaminates the edge signal - only
    that line is dropped.

    **(v1.3 correction, defect D-1/R4)** v1.2 had two frame bugs in three lines:

    1. it fed the **world x** of each tick straight into `drow()`, which expects a
       **forward-s offset**. On any scene whose grid origin is not the world origin the
       comparison was meaningless - scene05 (origin -1.5) dropped the tick at x=-1.8 for
       the wrong reason (it read drow 11.16 where the truth is 1.57) and **kept** x=-3.6
       (read 28.54, true 13.51 < 16), which then raised B7 on `Joints/JX_5`; scene11
       (origin x=15) dropped the joint 15 m *behind* the drop edge, leaving 2 joints where
       the profile intends 3 `[measured - w2d_edit_g1 §5 D-1 / g2 §5 R4]`.
    2. it always guarded the **X** family regardless of the travel axis, so on a -y scene
       (06) the guard was applied to the joints that run *parallel* to travel and the
       transverse family was never examined at all.

    Both are fixed by converting each tick to forward s through the plan's own
    `_View(origin, gy, axis)` and guarding the family perpendicular to the travel axis.
    Because the test is now B7's own arithmetic, the guard can no longer drop a tick that
    B7 would have passed (a content loss) nor keep one B7 will reject (a hard raise).
    """
    if not ctx["edges"]:
        return [], []
    view = _View(ctx["origin"], ctx["gy"], ctx["axis"])
    x0, y0, x1, y1 = ctx["region"]
    ox, oy = float(origin_xy[0]), float(origin_xy[1])
    hw = abs(float(width)) / 2.0
    if abs(view.fwd[0]) > 0.5:              # Travel axis = +-X -> the X ticks cross it
        ym = (y0 + y1) / 2.0
        return [xx for xx in _grid_ticks(x0, x1, step_x, ox)
                if _tick_guarded(ctx, view.s_of(xx, ym), hw)], []
    xm = (x0 + x1) / 2.0                    # Travel axis = +-Y -> the Y ticks cross it
    return [], [yy for yy in _grid_ticks(y0, y1, step_y, oy)
                if _tick_guarded(ctx, view.s_of(xm, yy), hw)]


def _trim_region(ctx, region, standoff=EDGE_STANDOFF):
    """Cut **the placement region itself** by the edge forbidden zone (the GT-E1' default
    clearance).

    Catching randomly placed elements (patches, cracks, soiling, weeds) that happen to land
    on an edge with a post-hoc gate breaks the whole plan. It also matches the first
    principle of the spec §2.2 prescription ("fill the near window"), so the cut is made
    **at the region stage**. Recessed elements (joints) do not use this function.
    """
    x0, y0, x1, y1 = _norm_region(region)
    if not ctx["edges"]:
        return (x0, y0, x1, y1)
    view = _View(ctx["origin"], ctx["gy"], ctx["axis"])
    fx, fy = view.fwd
    for _n, se, _o in ctx["edges"]:
        lim = se - float(standoff)          # Forward s upper bound
        if abs(fx) > 0.5:                   # Travel axis = +-X
            wx = view.origin[0] + lim * fx
            if fx > 0:
                x1 = min(x1, wx)
            else:
                x0 = max(x0, wx)
        else:                               # Travel axis = +-Y
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
    """Profile prescription -> builder call list. Coordinates are derived from region and edges."""
    x0, y0, x1, y1 = ctx["region"]
    # Surface (proud) elements go only in the region minus the edge forbidden zone. Joints (recessed) use the whole region.
    sx0, sy0, sx1, sy1 = _trim_region(ctx, ctx["region"])
    z = ctx["z"]
    seed = ctx["seed"]
    ops = []
    uc = GROUND_DIMENSIONS["unit_cell"].get(profile) or (None, (0.0, 0.0), "")
    ox, oy = (uc[1] or (0.0, 0.0))

    # -- Paving joints ---------------------------------------------------
    pv = prof["pave"]
    jkind = pv.get("joint")
    if jkind in ("slab", "contraction", "expansion", "interlock"):
        # The guard needs the same groove width the builder will use, so the two rims of
        # the joint are tested exactly as `frame_budget` B7 tests them (D-1).
        jw = float(pv.get("groove_w") or _dim("joint_%s_w" % jkind))
        skip_x, skip_y = _edge_guard_ticks(ctx, pv.get("step_x"),
                                           pv.get("step_y"), (ox, oy), width=jw)
        fn = build_slab_joints if jkind == "slab" else build_joint_grid
        kw = dict(step_x=pv.get("step_x"), step_y=pv.get("step_y"),
                  seed=seed, origin_xy=(ox, oy),
                  skip_x=skip_x, skip_y=skip_y)
        if pv.get("groove_w"):
            kw["width"] = pv["groove_w"]
        if pv.get("recess"):
            kw["recess"] = pv["recess"]
        if jkind != "slab":
            kw["kind"] = jkind
        ops.append(_op("joints", fn, "Joints",
                       args=((x0, y0, x1, y1), z, "@joint"), kw=kw))

    # -- infra (natural scenes are already blocked above) -----------------
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

    # -- Surface prescriptions -------------------------------------------
    for item in prof["surface"]:
        what = item[0]
        if what == "patch":
            # * The material dict **must** be passed as the kw `mtls=`. Passed positionally it
            #   does not match the `apply_ground` substitution rules (@string / kw mtl* / kw mtls)
            #   and the builder hands the **string** `"patch"` straight to Bind
            #   - dry_kit does not Bind, so the CPU self-check cannot catch it
            #   `[measured - sceneN5 pilot round 1 crash]`.
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

    # -- Tactile paving - only at sites registered in TACTILE_SITES (B11) --
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
    """**Boundary weed band** - clump by clump in joint lines and gutter cover gaps.

    This is vegetation, not ground. **Subject to the GT-E5 ramp** (`exc="weed"`) - the
    closer to the edge, the more `_clamp_gt_e5` cuts the height. Securing season-neutral
    species is handed to team A (vegetation).

    Prims: 1 per clump.  GT: registered exception (h <= 0.12, ramp clamp).
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
# [14] SCENE_PLANS - **a self-check fixture** (not the coordinate source for integration code, §7.4)
#
#     Integration reads coordinates from the scene `PARAMS` / `build_views()`. The values below
#     are **check-only approximations** transcribed from the §5 matrix and the §2.3 origin table.
# ===========================================================================
def _S(profile, region, **kw):
    d = dict(profile=profile, region=region, z=0.0, gy=0.0,
             origin=(0.0, 0.0, 0.0), axis="+x", edges=(), voids=(),
             dists=(2, 5, 10), tactile=(), sites={}, extras_args={}, caps={},
             overrides=None)
    d.update(kw)
    return d


def _fixture_plan(scene, seed=7, **over):
    """`SCENE_PLANS[scene]` -> `plan_ground(...)`. One call site so a new fixture field
    cannot be wired into some of the self-check passes and not the others (`overrides` was
    exactly that risk when D-6 was fixed)."""
    sp = SCENE_PLANS[scene]
    kw = dict(z=sp["z"], gy=sp["gy"], origin=sp["origin"], axis=sp["axis"],
              edges=sp["edges"], voids=sp["voids"], dists=sp["dists"],
              scene=scene, tactile=sp["tactile"], sites=sp["sites"],
              caps=sp["caps"], extras_args=sp["extras_args"],
              overrides=sp["overrides"], seed=seed)
    kw.update(over)
    return plan_ground(sp["profile"], sp["region"], **kw)


_E0 = (("edge", 0.0),)                       # Standard drop edge = travel axis origin

# scene13 ramp longitudinal profile - same convention as the scene `ramp_profile()` (check fixture).
#   transition 3.6 m @8.5 % -> main @17 % -> transition 3.6 m @8.5 %, total drop 4.4 m.
_R13_TRUN, _R13_TG, _R13_DROP, _R13_MG = 3.6, 0.085, 4.4, 0.17
_R13_TD = _R13_TRUN * _R13_TG
_R13_MD = _R13_DROP - 2.0 * _R13_TD
_RAMP13_PROFILE = [(0.0, 0.0, _R13_TRUN, _R13_TD),
                   (_R13_TRUN, -_R13_TD, _R13_MD / _R13_MG, _R13_MD),
                   (_R13_TRUN + _R13_MD / _R13_MG,
                    -(_R13_TD + _R13_MD), _R13_TRUN, _R13_TD)]

SCENE_PLANS = {
    # -- Main 21 --------------------------------------------------------
    "scene01": _S("plaza_granite", (-12.0, -5.5, -0.5, 5.5), gy=-2.75,
                  edges=_E0, tactile=("stair_top",),
                  sites=dict(manhole=[(-3.8, -2.4), (-8.0, 1.6)],
                             gully=[(-0.95, -5.10), (-0.95, 5.10)])),
    "scene02": _S("sidewalk_block", (-12.0, -4.0, -0.5, 4.0), edges=_E0,
                  tactile=("stair_top",),
                  sites=dict(manhole=[(-1.20, 0.35)],
                             gully=[(-0.95, -3.6), (-0.95, 3.6)])),
    # 03 - (v1.3, defect D-6) The fixture used to run plain `levee_paved`, so the CPU
    #   self-check green-lit **manhole + 2 gullies + an L-gutter on a natural scene** - a
    #   §5.7 violation the gate structurally cannot see, because `natural` is a *profile*
    #   flag and the fixture never set it. The real scene forces `natural=True` and zeroes
    #   the infra; the fixture now mirrors that (via the F2 explicit clear), so a
    #   regression that puts urban infra back on 03 fails `python3 ground_kit.py`.
    "scene03": _S("levee_paved", (-12.0, -3.0, 6.0, 3.0), edges=_E0,
                  overrides=dict(natural=True, infra=None)),
    "scene04": _S("trail_soil", (-12.0, -1.6, 2.0, 1.6), edges=_E0),
    # 05 - (v1.4, fixture drift) The fixture used origin (0,0,0) while the scene runs the
    #   grid at the bowl lip (-1.5, 0, 0), because `build_views()` subtracts 1.5 from every
    #   preset eye/tgt. That is why the fixture never exercised D-1 for scene05 at all
    #   (`_edge_guard_ticks` only mixes frames on an origin-shifted scene). Now mirrors the
    #   wired call: origin -1.5, region out to the lip, and the §5.1 coordinates re-derived
    #   in the scene (the spec manhole -3.5 sits exactly on the d2 eye).
    "scene05": _S("plaza_granite", (-13.5, -5.0, -1.5, 5.0), edges=(("bowl_lip", 0.0),),
                  origin=(-1.5, 0.0, 0.0),
                  overrides=dict(infra=dict(manhole=1, gully=2)),
                  sites=dict(manhole=[(-3.90, -0.40)],
                             gully=[(-10.00, 0.00), (-6.00, -3.00)],
                             patch=[(-2.60, -0.45), (-3.35, 1.20)])),
    # 06 - origin (3.5, -13.0, 5.000), travel -Y. Deck width x 2-5, edge y=-13.
    #  Note: the 06 row W1 notation in spec §2.3 (y -12.44...-11.0 etc.) is off by +0.564 m
    #    from the §2.2 definition. The §2.2 geometric definition (X in [0.564,2.00]) is used here.
    "scene06": _S("bridge_deck", (2.0, -13.0, 5.0, 0.0),
                  origin=(3.5, -13.0, 5.0), axis="-y", edges=_E0),
    "scene07": _S("courtyard_dg", (-12.0, -3.0, 4.0, 3.0), edges=_E0),
    # 08 - (v1.4, fixture drift) The fixture declared a **kit-emitted** `opening_ring`
    #   tactile band; the scene keeps that ring on its own `build_tactile_ring()` path and
    #   passes `tactile=()`. A fixture that gates an element the kit never builds proves
    #   nothing, so it is removed. The scene also runs a **second** plan (the pit floor at
    #   z=-4.498, region (2,-3,10,3), gully x1, everything else cleared) which the fixture
    #   does not model - one fixture entry per scene is the structure's limit, and the
    #   recorder harness (`w2d_kitfix_v1.md` Sec.1) is what covers the second plan.
    "scene08": _S("sidewalk_block", (-12.0, -4.0, -0.95, 4.0),
                  edges=(("pit_near_edge", 0.0),),
                  voids=((0.0, -4.5, 12.0, 4.5),),
                  overrides=dict(pave=dict(step_y=3.0),
                                 surface=(("patch", 3), ("crack", 4),
                                          ("stain", ("dirt", "gum")), ("weed", 8))),
                  sites=dict(manhole=[(-2.40, 1.60)],
                             gully=[(-1.75, -3.40), (-1.75, 3.40)],
                             patch=[(-1.25, 0.20), (-3.60, -0.30), (-8.60, 0.40)])),
    "scene09": _S("plaza_water", (-12.0, -6.0, -0.5, 6.0), edges=_E0),
    "scene10": _S("deck_trail_hybrid", (-12.0, -0.85, -1.5, 0.85), edges=_E0,
                  extras_args=dict(deck_planks=dict(region=(-1.5, -1.4, 0.0, 1.4)),
                                   edge_break=dict(lines=[-0.85, 0.85]))),
    "scene11": _S("bridge_deck", (-12.0, -1.0, 0.0, 1.0),
                  origin=(15.0, 0.0, 5.5), edges=_E0,
                  tactile=("stair_top", "stair_foot")),
    "scene12": _S("deck_timber", (-12.0, -1.6, 0.0, 1.6), edges=_E0,
                  extras_args=dict(deck_planks=dict(max_gaps=60))),
    # 13 - ramp crest concealment (§5.0 C-2): beyond-edge surface gradient 0.085 -> [F] at d2 only.
    #      Tactile paving is **on the sidewalk part only** (inside the ramp = inside the car park = out of scope, §12.4).
    "scene13": _S("ramp_parking", (-14.0, -3.3, 0.6, 3.3),
                  edges=(("ramp_crest", 0.0, dict(beyond_grade=0.085)),),
                  tactile=("bollard",),
                  extras_args=dict(
                      ramp_curb=dict(profile=_RAMP13_PROFILE, y_neg=-3.0,
                                     y_pos=3.0, height=0.12, width=0.30),
                      groove_band=dict(region=(3.6, -3.0, 20.4, 3.0))),
                  sites=dict(manhole=[(-3.90, 0.00)],
                             # 13-3 entry trench (d2 only) + 13-4 ramp foot
                             # Collection trench (mise en scene - beyond the crest, so outside h0.3)
                             #  * (v1.2) 0.35 -> 0.52. With a frame half-width of 0.19 the
                             #    near end sat at crest +0.16 m and the d2 separation was
                             #    18.1 @1080 = 9.1 @540 - short of the derived strength
                             #    (16 @540). Near end +0.33 m -> 34.7 @1080
                             #    = 17.4 @540 `[computed]`. Still beyond the crest, so
                             #    C-2 (d2 only) is unchanged.
                             trench=[(0.52, -3.0, 3.0), (23.4, -3.0, 3.0)],
                             tactile=dict(bollard=(-2.90, 4.35, -1.40, 4.65)))),
    "scene14": _S("plaza_granite", (-12.0, -4.0, -0.5, 4.0), edges=_E0,
                  sites=dict(manhole=[(-8.7, 1.2), (-4.5, -1.5)],
                             gully=[(-0.95, -3.6), (-0.95, 3.6)])),
    "scene15": _S("alley_concrete", (-12.0, -0.9, 0.0, 0.9), edges=_E0,
                  # (v1.2) Fixture aligned to the real scene coordinates - the old -1.15 predated the M9-(b)
                  # relocation and -4.00 gave 56.1 % of the d5 screen width (red team G-2).
                  sites=dict(manhole=[(-2.40, -0.15)], gutter_U=[-0.75],
                             # 15-6 grating at the stair foot - actually bent
                             # rot_group local x=9.3, z=-4.25. The fixture uses nominal coordinates.
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
    # 19 - mirrored (x' = 2*5.8 - x), travel -X, dists (2, 3.5, 5).
    #   (v1.4, fixture drift) The fixture used to claim grid origin 9.04 with the edge at
    #   s=0, i.e. it gated a **phantom lip 5 m short of the real one**. `build_views()`
    #   mirrors `sc.grid_views` about xref 5.8, so the grid origin is 2*5.8 = 11.6 and the
    #   roof's west lip (x=4.0) is at forward s = 11.6 - 4.0 = 7.6. Now mirrors the wired
    #   call, incl. the inset region and the membrane extras.
    "scene19": _S("roof_membrane", (4.25, -8.75, 16.75, 3.75),
                  origin=(11.6, 0.0, 0.0), axis="-x",
                  edges=(("roof_edge", 7.6),), dists=(2, 3.5, 5),
                  overrides=dict(infra=dict(gully=2),
                                 surface=(("patch", 4),
                                          ("stain", ("water", "drip", "dirt")))),
                  extras_args=dict(membrane=dict(seam_pitch=1.0, wear_n=5)),
                  sites=dict(gully=[(10.5, -0.6), (6.0, -7.5)],
                             patch=[(12.3, -0.6), (14.3, -0.25),
                                    (9.2, -3.4), (6.8, 1.9)])),
    "scene20": _S("plaza_granite", (-13.0, -4.0, -0.5, 4.0), edges=_E0,
                  sites=dict(manhole=[(-5.0, 1.4), (-10.0, -1.4)],
                             gully=[(-3.0, -3.6), (-8.0, 3.6)])),
    "scene21": _S("plaza_granite", (-12.0, -4.0, -0.5, 4.0), edges=_E0,
                  sites=dict(manhole=[(-4.0, 1.0), (-4.0, -1.0)],
                             gully=[(-2.0, -3.6), (-7.0, 3.6)])),
    # -- Batch 1, 12 -----------------------------------------------------
    # C1 - §7.3 invariant: new elements must have proud <= the 0.05 snow cover (burial is the scene identity).
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
    # N1 - (v1.4, fixture drift) The fixture still carried the **defective spec manhole**
    #   (-1.0, 0.4): at d2 that is X=1.0 m = 1,077 px = 56.1 % of frame width, which the
    #   scene itself had already moved to the W2 window per pilot ruling M9-(b). It also
    #   missed the `pave=dict(joint=None)` clear (the scene owns its two-tier joint grid -
    #   defect D6 class) and the bollard tactile band. Now mirrors the wired call.
    "sceneN1": _S("plaza_granite", (-12.0, -4.0, -0.6, 4.0),
                  tactile=("bollard",),
                  overrides=dict(pave=dict(joint=None)),
                  sites=dict(manhole=[(-2.40, 0.40), (-6.60, -1.50)],
                             gully=[(-3.80, 0.40), (-9.00, 2.60)],
                             patch=[(-1.20, 0.10), (-8.80, -0.20)],
                             tactile=dict(bollard=(10.85, -7.96, 17.15, -7.36)))),
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
# [15] Self-check - `python3 ground_kit.py` (no Isaac, no GPU)
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

    # -- (1) Constant and geometry check (reproduces spec appendix B) ----
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
    # -- Row unit convention (v1.2) - the code enforces that the two axes never mix --
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
    # Per-shot enforcement bound - d2/d5 can reach full separation, d10 cannot because its band is shallow
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

    # -- (2) Profile ledger (18 profiles + U1-U4) ------------------------
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
    # (v1.3, R3) The decal ladder must stay a tone separator, never relief.
    _lad = [decal_proud(f, i if f == "stain" else 0)
            for f in DECAL_Z_ORDER
            for i in range(len(_STAIN_KINDS) if f == "stain" else 1)]
    chk("R3 데칼 사다리 폭 ≤ 2 mm · 최대 양각 ≤ GT_DELTA/8",
        (max(_lad) - min(_lad)) <= 0.0020 + 1e-12
        and max(_lad) <= GT_DELTA / 8.0,
        f"폭 {(max(_lad) - min(_lad)) * 1000:.1f} mm · 최대 {max(_lad) * 1000:.1f} mm")
    # (v1.3, D-5) Every scatter kind a profile prescribes must have a pool, or the
    # prescription silently renders as the callback default (= fallen leaves).
    _kinds = {p["scatter"]["kind"] for p in GROUND_PROFILES.values()
              if p.get("scatter") and p["scatter"].get("kind")}
    chk("산포 kind 전부 SCATTER_POOLS 등재 (계절 자산 유출 방지)",
        _kinds <= set(SCATTER_POOLS),
        f"{sorted(_kinds)} ⊆ {sorted(SCATTER_POOLS)}")

    # -- (3) Tactile paving register -------------------------------------
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
    # * (v1.2) The d5 sample (348, 356) in spec §12.3 was **an artefact of the row axis defect**.
    #   That value filtered on "delta < 16 @1080" and kept only the near end (355.03); at the
    #   derived strength (16 @540 = 32 @1080) the far end (delta 22.1 @1080 = 11.1 @540) is inside
    #   the merge band too and is included -> (348, 371). The d10 sample (297, 304) is unchanged.
    #   **The §12.3 d5 sample is superseded by this correction** - to be stated in the report.
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

    # -- (4) Convention enforcement (do the exceptions actually raise?) --
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
    # (v1.3, F2) A dict override is a **merge**, so an empty dict is a no-op that reads
    # like a clear - that is how sceneC2 shipped a manhole on a "urban infra 0" row.
    chk("빈 사전 오버라이드 → ValueError (F2 무언의 무동작 차단)",
        raises(lambda: plan_ground("sidewalk_block", (-10, -2, 0, 2),
                                   scene="scene16", edges=_E0,
                                   overrides=dict(infra=dict())), "F2-empty"))
    _p_clear = plan_ground("sidewalk_block", (-10, -2, 0, 2), scene="scene16",
                           edges=_E0, overrides=dict(infra=None))
    _p_zero = plan_ground("sidewalk_block", (-10, -2, 0, 2), scene="scene16",
                          edges=_E0,
                          overrides=dict(infra=dict(manhole=0, gully=0,
                                                    gutter_L=0)))
    chk("infra=None 명시 소거 = 명시 0 패턴 (F2 하위호환)",
        _p_clear["prims"] == _p_zero["prims"]
        and not ({e["kind"] for e in _p_clear["elements"]}
                 & {"manhole", "gully", "gutter_l"}),
        f"소거 {_p_clear['prims']} 프림 = 명시0 {_p_zero['prims']} 프림")
    # (v1.3, D-5) An unregistered scatter kind must not fall back to the leaf pool.
    chk("미등재 산포 kind → ValueError (D-5)",
        raises(lambda: apply_ground(
            dry_kit(), "/World/T/GKit",
            plan_ground("trail_soil", (-10, -2, 0, 2), scene="scene04",
                        edges=_E0,
                        overrides=dict(scatter=dict(kind="snow", cover=0.1,
                                                    count=10))),
            {}, scatter=lambda *a, **k: 0), "D-5-kind"))

    # -- (5) Dry run of all 33 scenes ------------------------------------
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
            plan = _fixture_plan(scene)
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
        # Per-element hard assertions
        for e in plan["elements"]:
            if e["meta"].get("dropped"):
                continue
            if e["meta"].get("exc") in (None,) \
                    and abs(e["proud"]) > GT_DELTA + 1e-9:
                ok = False
                fails.append(f"{scene} GT δ: {e['path']} {e['proud']}")
        # Zero opening intersections
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

    # -- (6) Pilot 3-scene detail ----------------------------------------
    print("\n[6] 파일럿 3씬 상세 (N5 · 15 · 13)")
    for scene in ("sceneN5", "scene15", "scene13"):
        plan = _fixture_plan(scene)
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

    # -- (7) apply_ground dry round trip ---------------------------------
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

    # * apply round trip over all 33 scenes - catches material substitution rule violations **on CPU**.
    #   `dry_kit` does not Bind, so without the apply_ground guard an unsubstituted material key
    #   would only blow up as `Bind(str)` during a GPU render
    #   `[measured - sceneN5 pilot round 1]`.
    mtl_bad, prim_bad = [], []
    for scene in sorted(SCENE_PLANS):
        try:
            pl = _fixture_plan(scene)
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

    # * (v1.2) Solid-slab burial guard - an element whose top is below the paving top
    #   produces zero rendered pixels (there is no subtraction geometry). The only allowed exception is a genuine geometric gap.
    _BURY_OK = {"deck_gap", "trench", "gutter", "groove"}
    buried = []
    for scene in sorted(SCENE_PLANS):
        try:
            pl = _fixture_plan(scene)
        except ValueError:
            continue
        for e in pl["elements"]:
            if e["proud"] < 0 and (e.get("mtl_key") or e["kind"]) \
                    not in _BURY_OK and e["meta"].get("exc") != "plank_gap":
                buried.append(f"{scene}/{e['path']} proud {e['proud']:+.4f}")
    chk("음각 요소 매몰 0 (상면 < 포장 상면인 비예외 요소)",
        not buried, "; ".join(buried[:3]) or "0건")

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
