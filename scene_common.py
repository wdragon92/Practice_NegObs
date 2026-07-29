# -*- coding: utf-8 -*-
"""
scene_common.py — NegObs 인공씬 공통 라이브러리 (Isaac Sim 4.5)

scene01_campus_stairs.py의 검증된 블록을 함수화·일반화한 것.
브리프: Docs/multi_scene_brief_v2.md §A(API)·§B(신규 텍스처)·§C(사용 씬).

임포트 안전 규칙 (중요):
  이 모듈은 SimulationApp 부팅 **전에** import 되어도 안전해야 한다.
  → pxr / isaacsim / carb / omni 는 모듈 최상단에서 import 하지 않는다.
    (전부 함수 내부 지연 import.)  최상단은 numpy/os/math/json 만.

좌표계 관례(전 씬 공통): Z-up, m, 진행축 +X, 낙차 시작 모서리 x=0.
"""

import os
import math
import json
import zlib

import numpy as np

import facade_kit as fk        # 파사드 저층부 키트(scene_common 을 import 하지 않음)
import stair_kit as sk        # 계단 법규 키트(동일 — 프리미티브 주입식)


# ===========================================================================
# [0] 경로·에셋 상수
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_HERE, "assets")
S1_DIR = os.path.join(ASSETS_DIR, "scene01")     # 텍스처 세트는 scene01/ 로 통합

OMNIPBR_PATH = os.path.expanduser(
    "~/miniconda3/envs/env_isaaclab/lib/python3.10/site-packages/"
    "omni/mdl/core/Base/OmniPBR.mdl")

# 기본 noon HDRI (씬은 light_params["hdri"]로 개별 지정 가능)
DEFAULT_HDRI = "qwantani_noon_puresky_4k.exr"


# ===========================================================================
# [1] TEX 레지스트리 — scene01 기존 세트 + §B 신규 7역할 (canonical 파일명)
#     nor 접미사: ambientCG 세트는 _nor, PolyHaven 세트는 _nor_dx.
# ===========================================================================
TEX = dict(
    # --- scene01 기존 역할 ---
    plaza_light=dict(dir=S1_DIR, diff="plaza_light_diff.jpg",
                     nor="plaza_light_nor.jpg", rough="plaza_light_rough.jpg"),
    band_dark=dict(dir=S1_DIR, diff="band_dark_diff.jpg",
                   nor="band_dark_nor.jpg", rough="band_dark_rough.jpg"),
    plaza_lower=dict(dir=S1_DIR, diff="plaza_lower_diff.jpg",
                     nor="plaza_lower_nor.jpg", rough="plaza_lower_rough.jpg"),
    granite_dark=dict(dir=S1_DIR, diff="granite_dark_diff.jpg",
                      nor="granite_dark_nor_dx.jpg",
                      rough="granite_dark_rough.jpg"),
    brick_red=dict(dir=S1_DIR, diff="brick_red_diff.jpg",
                   nor="brick_red_nor_dx.jpg", rough="brick_red_rough.jpg"),
    # [W2 · B감사 A1] `aerial_grass_rock`(PolyHaven 항공 초지, 실측 타일 15 m)에서
    # ambientCG **Grass001**(실측 타일 **1.40 m**, CC0, 태그 lawn/park/short/dense)로 교체.
    #   · 픽셀 밀도 273 px/m → **2,926 px/m (×10.7)** — 들잔디 잎 나비 4~7 mm 가
    #     12~20 px 로 **실제 해상**된다 [실측 — assets/veg_manifest_w2.json textures]
    #   · 색상 초록 98.25 % · 선형 알베도 0.0932 · 순백 0 % → 계절 규약 통과
    #   · **`scale_m` 은 반드시 1.4**(타일 실치수). 전 씬 `scale=dict(grass=…)` 동시 교정.
    #   대안(씬 간 변주용) = `grass_lawn_b` (ambientCG Grass004, 동일 1.40 m).
    grass=dict(dir=ASSETS_DIR, diff="grass_lawn_diff.jpg",
               nor="grass_lawn_nor.jpg",
               rough="grass_lawn_rough.jpg"),
    tactile=dict(dir=S1_DIR, diff="tactile_yellow_diff.png",
                 nor="tactile_yellow_nor.png"),        # rough 없음
    # --- §B 신규 7역할 ---
    concrete_wall=dict(dir=S1_DIR, diff="concrete_wall_diff.jpg",
                       nor="concrete_wall_nor_dx.jpg",
                       rough="concrete_wall_rough.jpg"),   # 지하도 옹벽·터널
    concrete_floor=dict(dir=S1_DIR, diff="concrete_floor_diff.jpg",
                        nor="concrete_floor_nor_dx.jpg",
                        rough="concrete_floor_rough.jpg"),  # 지하도 계단·바닥
    wood_dark=dict(dir=S1_DIR, diff="wood_dark_diff.jpg",
                   nor="wood_dark_nor_dx.jpg",
                   rough="wood_dark_rough.jpg"),            # 침목(목재)
    dirt_park=dict(dir=S1_DIR, diff="dirt_park_diff.jpg",
                   nor="dirt_park_nor_dx.jpg",
                   rough="dirt_park_rough.jpg"),            # 공원 흙길
    gravel=dict(dir=S1_DIR, diff="gravel_diff.jpg",
                nor="gravel_nor_dx.jpg",
                rough="gravel_rough.jpg"),                  # 마사토·자갈
    stone_flag=dict(dir=S1_DIR, diff="stone_flag_diff.jpg",
                    nor="stone_flag_nor_dx.jpg",
                    rough="stone_flag_rough.jpg"),          # 자연석 판석
    rock_wall=dict(dir=S1_DIR, diff="rock_wall_diff.jpg",
                   nor="rock_wall_nor_dx.jpg",
                   rough="rock_wall_rough.jpg"),            # 석축/사석
    # --- §C v3 신규 6역할 (에셋 에이전트 다운로드 완료, canonical 슬러그) ---
    metal_rust=dict(dir=S1_DIR, diff="metal_rust_diff.jpg",
                    nor="metal_rust_nor_dx.jpg",
                    rough="metal_rust_rough.jpg"),          # 녹슨 철(비상계단·잔도)
    plaster=dict(dir=S1_DIR, diff="plaster_diff.jpg",
                 nor="plaster_nor_dx.jpg",
                 rough="plaster_rough.jpg"),                # 회벽(골목 주택)
    marble_light=dict(dir=S1_DIR, diff="marble_light_diff.jpg",
                      nor="marble_light_nor_dx.jpg",
                      rough="marble_light_rough.jpg"),      # 대리석/밝은 기념석
    sandstone=dict(dir=S1_DIR, diff="sandstone_diff.jpg",
                   nor="sandstone_nor_dx.jpg",
                   rough="sandstone_rough.jpg"),            # 사암(스텝웰·가트)
    stone_worn=dict(dir=S1_DIR, diff="stone_worn_diff.jpg",
                    nor="stone_worn_nor_dx.jpg",
                    rough="stone_worn_rough.jpg"),          # 사원 마모석
    rock_face=dict(dir=S1_DIR, diff="rock_face_diff.jpg",
                   nor="rock_face_nor_dx.jpg",
                   rough="rock_face_rough.jpg"),            # 절벽 암반
    # --- 배치1 나노바나나(scene22~33) 신규 1역할 ---
    # [사실화 v1] 아스팔트 — sceneD3 진단에서 죽은 픽셀의 89.8% 가 상수색
    # 아스팔트 차도였다. PolyHaven asphalt_02(3.0 m 타일, CC0).
    asphalt=dict(dir=S1_DIR, diff="asphalt_diff.jpg",
                 nor="asphalt_nor_dx.jpg", rough="asphalt_rough.jpg"),
    # 눈 — sceneC1 최대 면적 재질(88.5%). PolyHaven snow_01(2.0 m 타일, CC0)
    snow=dict(dir=S1_DIR, diff="snow_diff.jpg",
              nor="snow_nor_dx.jpg", rough="snow_rough.jpg"),
    leaf_ground=dict(dir=S1_DIR, diff="leaf_ground_diff.jpg",
                     nor="leaf_ground_nor_dx.jpg",
                     rough="leaf_ground_rough.jpg"),        # 낙엽 지면(C2)
)

# 배치1 overcast HDRI (C1 눈·C4 젖은 석재 공유) — light_params["hdri"]로 지정,
# lookfix=False 권장(무태양이라 태양 캡 무의미, 원본 사용).
# [v5 공통 레이어] 인터로킹 보도블록 + 한글 사인 텍스처(assets/signs/gen_signs.py 생성)
# [v6 판정 C-1] 구 소스는 이끼 낀 유럽식 사고석이라 한국 보도가 아니었다 →
#   ambientCG CC0 **PavingStones015**(2K-JPG, Color/NormalDX/Roughness)로 교체.
#   정형 인터로킹 블록 바스켓위브·회색 콘크리트·모래 줄눈.
#   타일당 반복 12(정사각 유닛 170 px/2048) → 블록(=2유닛) 장변이 씬 scale_m
#   1.0/1.2/1.5 에서 각각 0.17/0.20/0.25 m (실물 보도블록 200×100 대역).
#   구 사고석은 같은 scale_m 에서 석괴가 0.4 m급이라 화면을 지배했다.
#   파일명·경로 불변 → 씬 파일 수정 불필요(C-1 의 "UV 스케일 축소"를 텍스처
#   자체의 반복수로 달성).
TEX["paving_interlock"] = dict(dir=ASSETS_DIR, diff="paving_interlock_diff.jpg",
                               nor="paving_interlock_nor.jpg",
                               rough="paving_interlock_rough.jpg")
SIGNS_DIR = os.path.join(ASSETS_DIR, "signs")
for _s in ("warn_fall", "caution_step", "exit", "info", "no_entry"):
    TEX[f"sign_{_s}"] = dict(dir=SIGNS_DIR, diff=f"sign_{_s}.png")

OVERCAST_HDRI = "kloofendal_overcast_4k.exr"

# ---------------------------------------------------------------------------
# [사실화 P1] PT 수정 설정 — `NEGOBS_PT_FAST=1` 로 활성화
#   근거: ZZ_synthesis §10.3 (D팀) + 감독 스파이크 실측(2026-07-28)
#   현행은 spp=1 · totalSpp=512 라 512프레임에 걸쳐 누적한다. spp 를 올리고
#   rtSubframes 로 한 update 안에서 여러 서브프레임을 돌리면 8프레임에 수렴.
#   실측(스파이크 랩, 2뷰): 4.89~5.14 → 0.08~0.31 s/컷. 두 설정의 출력 PNG 는
#   **바이트 단위 동일**(PSNR 무한대) — 무손실 가속이다.
#   RT 대비로도 빠르다(RT warmup 90 = 0.79~1.03 s/컷).
# ---------------------------------------------------------------------------
PT_FAST = dict(spp=16, total_spp=64, subframes=8, warmup=8)


def tex_path(role, kind):
    """역할·종류(diff/nor/rough)의 절대 경로."""
    return os.path.join(TEX[role]["dir"], TEX[role][kind])


# ===========================================================================
# [1b] 사실화 v1 룩 레이어 — `NEGOBS_LOOK_MTL` / `NEGOBS_LOOK_GEO` 2단 플래그
#      (상위 호환 스위치 `NEGOBS_LOOK_V1=1` 은 둘 다 ON. 기본 전부 OFF)
#
# 지시서 `Docs/briefs/realism_brief_v1.md` + 개정 이력 rev.1.
# **씬 파일은 한 줄도 고치지 않는다**(불변 3종). 대신 `make_pbr` 에 이미 들어오는
# 프림 경로(`{ROOT}/Looks/Paving` 등)에서 역할을 읽어 룩 사양을 주입한다.
#
# 왜 경로 이름인가: 33씬 전 재질이 `make_pbr` 단일 경유이고, `Looks/` 하위 이름이
# 의미 있게 붙어 있다(Wood 20 · Grass 20 · Rail 17 · Parapet 15 · Glass 15 …).
# 씬 무수정으로 역할별 처방을 거는 유일한 통로다.
#
# 3단 재질 정책 [Phase1 §6.5 — H 보고서와 감독 실측이 독립 수렴]:
#   지면·사면 계열       → NegObsGround.mdl (소프트 트라이플래너. 경사면 필수)
#   구조물·식생·사인     → OmniPBR (uv_mode·opacity·detail normal 필요)
#   발광·유리            → OmniPBR (MDL 에 emission 입력 없음)
# NegObsGround 전역 승격은 불가로 확정: UV 파이프라인·opacity 부재 + 텍스처 페치 72회.
# ===========================================================================
# --- 2단 플래그(T1 §1.7.2) — 재질 A/B 대조군 오염(치명 C3) 구조적 차단 ------
# `NEGOBS_LOOK_V1` 단일 플래그는 재질뿐 아니라 **기하도** 바꾼다. 그 상태로
# "V1=0 vs 1" 을 재질 A/B 로 쓰면 기하 변화가 섞여 재질 효과를 분리할 수 없다
# (재발 2회 기록 — `redteam_verification_v1.md` R3).
#   LOOK_MTL : 셰이더 입력·`UsdShade.Material` 정의만 바꾼다(프림 불변).
#   LOOK_GEO : 프림 집합·타입·xform·points·extent 를 바꾼다.
# 재질 A/B 대조군은 `LOOK_MTL=0, LOOK_GEO=1` 이다(규칙 R-2).
# **아래 3줄이 `LOOK_V1` 토큰의 유일한 잔존 허용 지점**이다(규칙 R-5 —
# `scripts/geom_invariance_check.py --assert-no-residual-lookv1` 가 검사한다).
LOOK_V1 = os.environ.get("NEGOBS_LOOK_V1", "") == "1"          # 상위(종전 호환)
LOOK_MTL = os.environ.get("NEGOBS_LOOK_MTL", "1" if LOOK_V1 else "0") == "1"
LOOK_GEO = os.environ.get("NEGOBS_LOOK_GEO", "1" if LOOK_V1 else "0") == "1"
MDL_GROUND = os.path.join(ASSETS_DIR, "NegObsGround.mdl")

# 디테일 노멀(근접 텍셀 뭉개짐 완화) 공용 소스 — 미세 그레인용 범용 맵.
_DETAIL_NOR = os.path.join(S1_DIR, "concrete_wall_nor_dx.jpg")

# OmniPBR(큐빅 투영) ↔ NegObsGround(트라이플래너) 의 texture_scale 의미 차이 보정.
# 틀리면 **전 지면의 타일 스케일이 어긋나는 전역 회귀**가 되므로 추정 금지 —
# 전용 캘리브레이션 렌더(스파이크 랩 E10: 인터로킹 보도블록을 같은 scale_m 으로
# 좌/우에 깔고 수직 하향 뷰에서 자기상관 픽셀 주기 비교)로 실측했다.
#
#   1차 측정(MDL v1.4.0): OmniPBR 23.163/23.164 px vs MDL 26.454/32.764 px
#     → 비율이 축마다 다르고(이방성) 육안으로 **패턴이 45° 돌아가 있었다**.
#       원인은 스케일이 아니라 MDL 의 기저 선택 버그였다(아래 참조).
#   2차 측정(MDL v1.5.0, 버그 수정 후): 23.163/23.164 vs 23.154/23.177
#     → **비율 1.0001. 보정 불요.**
#
# 즉 "스케일이 다르다"는 1차 관찰은 **오진**이었고, 진짜 원인은 수평면에서
# 45° 보조 기저가 50:50 으로 섞여 들어가던 축퇴였다(MDL v1.5.0 에서 수정).
_GROUND_SCALE_FIX = 1.0        # E10 2차 실측 확정 (비율 1.0001)

# --- 클래스별 룩 사양 -------------------------------------------------------
# bevel[m] : round_edges_radius. Phase1 §2.1 실측 — 화면상 폭 ≈ 24·(r/d)·57.3 px.
#            브리프 원안(콘크리트 3mm)은 로봇 시점 2~10 m 에서 서브픽셀이라
#            비용만 들고 보이지 않는다.
#   **국내 규격 조사 반영** (`Docs/surveys/.../I_ks_dimension_verification.md`):
#     · 현장타설 콘크리트 모서리 **20~30 mm** — KCS 21 50 05:2023 3.3(10) 원문.
#       우리 콘크리트는 옹벽·계단 챌면·제방 = 대부분 현장타설이므로 **0.020**.
#       (감독 잠정 10 mm 는 1/2~1/3 과소였다. 프리캐스트라면 10 mm 가 맞다.)
#     · 연석 수직형 **R=10** — 국토부 예규 제321호 보도 설치 지침 그림 2.17
#     · 금속 **2 mm** — KS B 0403 모떼기 수열 2열 정규값 (잠정값 유지 확인)
#     · 계단 노징 — **국내 규정 없음**(법정문서 4건 전수 확인). 값은 IBC
#       1.6~14.3 mm 상단을 쓰되 **출처가 국내가 아님을 명시**한다.
#     · 일반 석재 — **근거 없음**. 보수적으로 낮게 둔다.
# sat      : 채도 계수(MDL 전용). 전역 하향은 금지 — scene01 은 이미 0.146 으로
#            하한 미달이다. 과채도는 석재·초목·흙 계열의 국소 현상.
# mdl      : "ground" = NegObsGround / "omni" = OmniPBR
# patch    : NegObsGround 패치 회전 강도. 모듈형 포장 0(패턴 파손 방지), 자연 1.
# 웨더링(MDL v1.6.0) 역할별 값 — 키가 없으면 전부 0(무영향).
#   **치명 주의**: 기단 오염 밴드는 **월드 Z 절대 기준**이다. 지면 프림은 z≈0 이라
#   grime 을 켜면 밴드 안에 통째로 들어가 **지면 전체가 균일 암화**된다(전역 회귀).
#   → 지면 계열(paving/asphalt/soil/gravel)은 grime/splash 를 **반드시 0** 으로.
#   밴드는 지면 위에 **서 있는 수직 구조물**(옹벽·기단·파라펫·연석·계단 챌면)에만.
# [치명 C4 수정] **월드 z 기반 웨더링(grime·splash)을 전면 비활성**한다.
#   `grime_z0` 기본값이 0.0 이고 scene_common 이 이를 한 번도 설정하지 않아,
#   m_grime = 1 - smoothstep(0, h, z) 가 **z ≤ 0 인 모든 면**에 균일하게 걸렸다.
#   클래스로만 막으려 했으나 concrete 가 215종 중 46종을 흡수하며
#   `Slab`·`LowerFloor`·`Lower`·`Trough` 같은 **수평 지면**까지 포함해 방어가 뚫렸다.
#
#   단순한 룩 버그가 아니다 — sceneD3 측구(깊이 0.80·인버트 −1.05)처럼 **낙차가
#   깊을수록 어두워지는 결정론적 알베도 규칙**이 되어, GT 낙차와 상관된
#   **합성 지름길**을 만든다. 이 프로젝트가 가장 경계하는 실패 모드다.
#
#   재활성 조건: 프림별 발치 z 를 `grime_z0` 로 넘길 통로가 생긴 뒤.
#   노멀 기반 항목(streak = 수직면 흘러내림, dust = 상향면 먼지)은 z 와 무관하므로 유지.
_W_STRUCT = dict(grime=0.0, splash=0.0, streak=0.12, wrough=0.15)
_W_STONE = dict(grime=0.0, splash=0.0, streak=0.08, wrough=0.12)
_W_EDGE = dict(grime=0.0, splash=0.0, wrough=0.10)

LOOK_CLASS = {
    #                    bevel   sat   mdl        patch  detail
    # 보도블록 개별 모따기는 **국내 공개 규정에 수치가 없다**(KS F 4419 본문 유료,
    # 이를 인용하는 공개 문서 전수에서 모따기 조항 0건 — 조사 결론 "추정 금지").
    # 게다가 round_edges 는 개별 블록이 아니라 **슬래브 프림 경계**에 걸린다.
    # 개별 블록 모따기는 텍스처 노멀맵이 이미 담당하므로, 여기 값은 슬래브 경계용
    # 이며 연석(10 mm)보다 낮게 둔다. [근거 없음 — 보수적 선택]
    "paving":   dict(bevel=0.006, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     tex="paving_interlock", bump=1.4,
                     tex_alts=("stone_flag", "paving_interlock", "plaster")),
    "concrete": dict(bevel=0.020, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     weather=_W_STRUCT, tex="concrete_floor", bump=1.6,
                     tex_alts=("concrete_floor", "concrete_wall", "plaster")),
                     # concrete_wall(c@1/16 0.0345) → concrete_floor(0.129, x3.7).
                     # 진단: 승격 텍스처의 국소대비가 낮으면 승격해도 결이 안 산다.
                     # 현장타설 20~30 mm (KCS 21 50 05). bump 1.6 = 진단 P3
                     # (음영부는 밝기가 아니라 노멀 대비로만 결이 산다)
    "brick":    dict(bevel=0.006, sat=0.88, mdl="ground", patch=0.0, detail=True,
                     tex="brick_red", bump=1.4, tex_alts=("brick_red", "plaster"),
                     weather=dict(grime=0.0, splash=0.0, streak=0.10,
                                  wrough=0.15)),
    "stone":    dict(bevel=0.004, sat=0.66, mdl="ground", patch=1.0, detail=True,
                     weather=_W_STONE, tex="stone_flag", bump=1.5,
                     tex_alts=("stone_flag", "marble_light")),
                     # 베벨 [근거 없음] 보수적 하향
    "soil":     dict(bevel=0.000, sat=0.74, mdl="ground", patch=1.0, detail=True,
                     tex="dirt_park", bump=1.4,
                     tex_alts=("dirt_park", "gravel")),
    "gravel":   dict(bevel=0.000, sat=0.78, mdl="ground", patch=1.0, detail=True,
                     tex="gravel", bump=1.4),
    # tex: 상수색 재질을 이 TEX 역할의 텍스처로 승격한다(의도 알베도는 보존).
    # spec/bump: 진단 P1/P3 — 노면이 과하게 밝은 원인이 그레이징 광택이라
    # specular_level 을 명시하고, 음영부 대비는 노멀 강도로 살린다.
    "asphalt":  dict(bevel=0.006, sat=0.90, mdl="ground", patch=1.0, detail=True,
                     tex="asphalt", spec=0.20, bump=1.4),
    # 노징 12 mm 는 **IBC 1.6~14.3 mm 상단**이다. 국내 규정은 존재하지 않음(전수 확인).
    "nosing":   dict(bevel=0.012, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     weather=dict(grime=0.0, splash=0.0, wrough=0.10)),
    "curb":     dict(bevel=0.010, sat=1.00, mdl="ground", patch=0.0, detail=True,
                     weather=_W_EDGE),   # 연석 수직형 R=10 (예규 321호 그림2.17)
    "metal":    dict(bevel=0.002, sat=1.00, mdl="omni",   detail=True),
    # 목재는 라이브러리에 어두운 wood_dark(선형휘도 0.061) 하나뿐이라 밝은
    # 목재는 배율이 커진다. 목재 결은 방향성이 강해 증폭해도 잡음이 덜 튀므로
    # 이 클래스만 상한을 높인다.
    "wood":     dict(bevel=0.004, sat=0.88, mdl="omni",   detail=True,
                     tex="wood_dark", bump=1.3, max_gain=7.0),
    # [W2 · B감사 A2] `tex_alts` 에서 **`leaf_ground` 제거** — 치명 계절 규약 위반 차단.
    #   승격 채택 조건은 `max(ratio) ≤ max_gain` **그리고** `spread = max/min ≤ 4.0` 인데,
    #   구 `grass`(aerial_grass_rock)는 청 채널이 비어 있어(적/청 7.03) 초록 수관
    #   상수색에서 spread 4.22 로 탈락하고, 대신 `leaf_ground`(적/청 4.09 → spread 2.86)가
    #   채택됐다. 전 33씬 시뮬레이션 결과 **`leaf_ground` 승격 50건 / 24씬** — 즉 24개 씬의
    #   나무 수관에 **가을 낙엽 픽셀**이 칠해지고 있었다(원본 2.3 m 낙엽이 52 % 크기로)
    #   [실측 — `B_groundcover_debris.md` §8].
    #   A1(Grass001 교체)만으로도 spread 가 내려가 grass 가 채택되지만, `leaf_ground` 가
    #   목록에 남는 한 **어두운 상수색에서는 여전히 그쪽으로 떨어진다.** A2 가 그 경로를
    #   물리적으로 없앤다 — 둘 다 한다.
    #   `tex_scale` 1.2 → **1.4**: 승격 경로도 Grass001 실측 타일을 따라야 한다.
    #   `detail=False` 는 유지(잎은 실물 USD 담당 — §2.1).
    "veg":      dict(bevel=0.000, sat=0.76, mdl="omni",   detail=False,
                     tex="grass", bump=1.2, max_gain=7.0, tex_scale=1.4,
                     tex_alts=("grass",)),
    "water":    dict(bevel=0.000, sat=1.00, mdl="omni",   detail=False),
    "glass":    dict(bevel=0.000, sat=1.00, mdl="omni",   detail=False),
    "paint":    dict(bevel=0.000, sat=1.00, mdl="omni",   detail=False),
    "sign":     dict(bevel=0.000, sat=1.00, mdl="omni",   detail=False),
    # 미상 역할 — 보수적으로. MDL 교체·채도 변경·디테일 노멀 전부 없음.
    # 분류기가 215종 중 208종을 잡으므로 여기 떨어지는 건 진짜 미상이고,
    # 그런 재질에 콘크리트 그레인 노멀을 씌우는 건 개선이 아니라 훼손이다.
    # 눈: 반사율이 높아 베벨·채도 조정 대상이 아니다. 텍스처만 얹는다.
    # **주의(조사 경고)**: 현 의도색 0.72~0.78 은 표시 sRGB 221~229 로 톤매핑
    # 상단에서 클리핑돼 텍스처를 붙여도 국소표준편차가 다시 0 이 된다.
    # 승격 전에 의도 알베도를 0.55~0.62 로 낮춰야 실효가 있다(TODO: 조달 후 적용).
    "snow":     dict(bevel=0.000, sat=1.00, mdl="ground", patch=1.0, detail=True,
                     tex="snow", bump=1.3),
    "misc":     dict(bevel=0.003, sat=1.00, mdl="omni",   detail=False),
}

# --- `Looks/<이름>` → 클래스 -------------------------------------------------
# 실측된 이름 빈도 상위부터. 미등재 이름은 "misc"(보수적 기본)로 떨어진다.
LOOK_ROLE = {
    # 포장·광장
    "Paving": "paving", "PlazaLight": "paving", "PlazaLower": "paving",
    "Plaza": "paving", "Deck": "wood", "Tile": "paving",
    # 콘크리트 구조물
    "Concrete": "concrete", "ConcreteWall": "concrete", "Wall": "concrete",
    "Shell": "concrete", "ShellB": "concrete", "Parapet": "concrete",
    "Stage": "concrete", "Upper": "concrete", "Lower": "concrete",
    "Stair": "concrete", "Riser": "concrete", "Slab": "concrete",
    "Fascia": "concrete", "Pier": "concrete", "Abutment": "concrete",
    # 석재
    "Granite": "stone", "GraniteDark": "stone", "Marble": "stone",
    "Rock": "stone", "Stone": "stone", "Sandstone": "stone",
    "RockWall": "stone", "Flag": "stone",
    # 벽돌·회벽
    "Brick": "brick", "Plaster": "brick",
    # 지면 자연물
    "Soil": "soil", "Dirt": "soil", "Gravel": "gravel", "Sand": "soil",
    "Asphalt": "asphalt",
    # 낙차 에지 — 브리프 §2.1 승인값(노징 12 mm)
    "Nosing": "nosing", "Curb": "curb", "Edge": "nosing",
    # 금속
    "Rail": "metal", "Steel": "metal", "Pole": "metal", "Post": "metal",
    "Lamp": "metal", "Bollard": "metal", "BollardBand": "paint",
    "Grate": "metal", "Grating": "metal", "Gear": "metal", "Roof": "metal",
    # 목재
    "Wood": "wood", "WoodDark": "wood", "SeatWood": "wood", "Bench": "wood",
    # 식생
    "Grass": "veg", "GrassB": "veg", "CanopyA": "veg", "CanopyB": "veg",
    "Leaf": "veg", "LeafA": "veg", "LeafB": "veg", "Hedge": "veg",
    "Shrub": "veg", "Reed": "veg", "Moss": "veg",
    # 물
    "Water": "water",
    # 도색·표지 — 상수색이 물리적으로 옳다(텍스처화 금지 대상)
    "Paint": "paint", "LineWhite": "paint", "LineYellow": "paint",
    "Band": "paint", "Tactile": "paint",
    # 유리·사인·발광
    "Glass": "glass", "Window": "glass", "Panel": "sign",
    # 분류기 잔여 7종 중 명확한 것만 명시(나머지 Bag/Emit/Rubber/Snow 는
    # 의도적으로 misc = 최소 처방 — 알 수 없는 재질에 콘크리트 그레인을
    # 씌우는 것이 더 나쁘다)
    "Line": "paint", "CutLine": "paint", "Pot_": "concrete",
    "Snow": "snow", "Panel": "metal", "Iron": "metal",
    # 오분류 정정(진단 2차): Roof 는 산사 목조 기와라 금속이 아니고,
    # Ridge/Crest 는 자연 능선이라 콘크리트가 아니다.
    "Roof": "wood", "Roof_": "wood", "Ridge": "soil", "Ridge_": "soil",
    "Crest_": "soil", "Crest": "soil",
    "Sign": "sign", "SignFace": "sign", "SignBack": "sign",
}


# 룩 레이어 적용 계측 — 무엇이 실제로 걸렸는지 눈으로 확인하기 위한 카운터.
# (게이트 1차에서 "룩 레이어를 켰는데 수치가 안 움직인다"를 진단한 도구다.
#  원인은 상수색 재질을 통째로 건너뛰고 있었던 것 — 그게 flat% 의 주범인데.)
LOOK_STATS = dict(ground=0, omni_tex=0, const=0, bevel=0, detail=0, skin=0,
                  skipped=0, roles={})


def look_report():
    """룩 레이어 적용 요약 한 줄. capture_pipeline 시작 시 출력.

    2단 플래그 도입 후 **양팔 각인**이 규칙 R-2 의 검증 수단이다 — 라운드
    로그에 MTL/GEO 상태가 남아야 대조군을 사후에 확인할 수 있다."""
    if not (LOOK_MTL or LOOK_GEO):
        return "[룩v1] OFF (MTL=0 GEO=0)"
    r = LOOK_STATS
    top = sorted(r["roles"].items(), key=lambda kv: -kv[1])[:8]
    return (f"[룩v1] MTL={int(LOOK_MTL)} GEO={int(LOOK_GEO)} | "
            f"재질 ground={r['ground']} omni_tex={r['omni_tex']} "
            f"const={r['const']} skip={r['skipped']} | 베벨={r['bevel']} "
            f"디테일={r['detail']} 스킨={r['skin']} "
            f"승격={r.get('promoted', 0)} 상수MDL={r.get('const_mdl', 0)} "
            f"웨더={r.get('weather', 0)} 나무={r.get('veg_asset', 0)} "
            f"간살={r.get('baluster', 0)} 관목={r.get('shrub', 0)} "
            f"손잡이={r.get('handrail', 0)} "
            f"산포={r.get('debris', 0)} | 역할 "
            + ", ".join(f"{k}:{v}" for k, v in top))


# --- 키워드 규칙 분류기 --------------------------------------------------
# 저장소 전수 실측 결과 `Looks/` 이름이 **약 200종**이고 대부분이 1~2회만 쓰이는
# 롱테일이다(WetRock, StoneMoss, CityParapet, LboxFrame …). 정확 일치 표만으로는
# 게이트 1차에서 재질의 절반 이상이 "misc" 로 떨어졌다(scene07 33개 중 21개).
# → **부분문자열 규칙**을 순서대로 적용해 롱테일을 흡수한다.
#   규칙은 위에서부터 검사하므로 **더 구체적인 것을 먼저** 둔다
#   (예: "roadpaint" 는 paint, 그냥 "road" 는 asphalt).
_LOOK_RULES = [
    # 발광·투명 — 룩 레이어에서 제외해야 하는 것부터
    ("glass", ("glass", "window", "lens", "shopglass", "cityglass")),
    # "panel" 단독은 사인이 아니다 — 실체는 난간 패널·쉘터 지붕이었다
    # (scene11 6.0% · scene06 5.4%). 사인은 sign/placard 계열로 한정한다.
    ("sign", ("sign", "placard", "plaque", "lbox", "mailbox")),
    # 도색·표지 — 상수색이 물리적으로 옳다(텍스처화 금지 대상)
    # joint/cutline = 줄눈 실런트. 종전에는 asphalt 로 분류돼 **줄눈에 아스팔트
    # 결이 얹히고** 있었다. 도색 계열이 옳다.
    ("paint", ("paint", "linewhite", "lineyellow", "roadpaint", "tactile",
               "warn", "tape", "band", "stripe", "gauge", "joint", "cutline",
               "lane")),   # **"lane" 은 여기(도로 표시)** — asphalt 보다 먼저 잡는다
    # 식생
    ("veg", ("grass", "leaf", "canopy", "hedge", "shrub", "foliage", "reed",
             "tuft", "tree", "moss", "treeline", "treepit", "verge")),
    # 눈 — 33씬 통틀어 **단일 재질 최대 면적**(sceneC1 88.5%)인데 misc 에 갇혀
    # 상수색 MDL 도 텍스처 승격도 못 받고 있었다.
    ("snow", ("snow", "frost")),
    # 물
    ("water", ("water", "sea", "tide", "wet")),
    # 금속
    ("metal", ("rail", "steel", "iron", "metal", "pole", "post", "lamp",
               "bollard", "gate", "fence", "grate", "grating", "galv",
               "rebar", "wire", "cable", "hvac", "crane", "gear", "shutter",
               "mullion", "frame", "bin", "lid", "duck", "tool", "beak")),
    # 목재
    ("wood", ("wood", "deck", "bench", "seat", "sleeper", "pallet",
              "stringer", "carton", "door")),
    # 낙차 에지 — 승인된 노징 12 mm / 연석 12 mm
    ("nosing", ("nosing", "tread", "step")),
    # **"verge" 제거** — scene04 의 Verge* 는 잔디 갓길(식생)인데 연석 처방을
    # 받고 있었다(면적 13.4%). 영어 verge 는 갓길·풀밭 가장자리이지 연석이 아니다.
    ("curb", ("curb", "coping", "cope", "kerb")),
    # 석재
    ("stone", ("stone", "granite", "marble", "rock", "flag", "cobble",
               "polish", "lightstone")),
    # 벽돌·회벽
    ("brick", ("brick", "plaster")),
    # 흙·자갈
    ("soil", ("soil", "dirt", "earth", "mud", "leafbed")),
    ("gravel", ("gravel", "ballast", "debris", "rubble")),
    # 아스팔트·차도
    # "lane"·"joint" 는 paint 로 이동(차선 파선·줄눈 실런트).
    # 종전에는 차선이 asphalt 로 분류돼 **아스팔트 텍스처 승격 대상**이 됐다 —
    # v5.1 §4 상수색 불가침 정면 위반이다(도색은 균일해야 단서로 기능한다).
    ("asphalt", ("asphalt", "road", "patch")),
    # 포장
    ("paving", ("pav", "plaza", "walk", "sidewalk", "tile", "block",
                "apron", "alley", "podium", "platform")),
    # 콘크리트 구조물 — 가장 넓은 그물이므로 마지막
    ("concrete", ("concrete", "conc", "wall", "parapet", "shell", "slab",
                  "stair", "riser", "skirt", "fascia", "ceiling", "facade",
                  "bldg", "city", "house", "shed", "tunnel", "bridge",
                  "pier", "abutment", "crest", "ridge", "trough", "valley",
                  "container", "stage", "upper", "lower", "roof", "canopy",
                  "awning", "trim", "grime", "dark", "skyline", "far")),
]



# --- 채도 자기교정 ------------------------------------------------------
# 역할별 계수만으로는 부족하다. Phase0 에서 이미 확인했듯 scene01 은 sat_mu 가
# 0.146 으로 **이미 목표 하한(0.15) 미달**인데, 역할 계수는 씬 상태를 모르므로
# 그대로 걸면 더 탈색된다(실측: 0.146 → 0.134). 과채도는 석재·흙·초목 계열의
# **국소 현상**이지 전역이 아니다.
# → 재질 **자신의 채도**를 보고 과채도일 때만 낮춘다. 자기교정이라 씬 정보가
#   필요 없고, 이미 저채도인 재질은 건드리지 않는다.
# [중대 M5] 종전 0.30 은 **텍스처 채도 분포보다 위**라 stone(0.66)·asphalt(0.90)·
# paving 계수가 사실상 한 번도 발동하지 않았다. 게다가 렌더 공간 sat_mu 임계를
# 텍스처 공간에 그대로 옮겨 쓴 단위 불일치였다.
# 실사 n=54 의 sat_mu 는 0.232±0.071 이고 텍스처 자체 채도는 그보다 낮게 나온다.
# → knee 를 텍스처 공간 기준으로 낮춘다.
_SAT_KNEE = 0.18
_TEXSAT_CACHE = {}


def _rgb_sat(rgb):
    mx, mn = max(rgb), min(rgb)
    return 0.0 if mx <= 1e-6 else (mx - mn) / mx


def _texture_sat(path):
    """텍스처 평균 채도. PIL 로 축소 로드해 계산하고 캐시한다(씬당 수 개)."""
    if path in _TEXSAT_CACHE:
        return _TEXSAT_CACHE[path]
    v = None
    try:
        from PIL import Image
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((64, 64))
            a = np.asarray(im).astype(np.float64) / 255.0
        a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        mx = a.max(-1)
        mn = a.min(-1)
        v = float(np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0).mean())
    except Exception as e:
        print(f"[룩v1][경고] 텍스처 채도 계산 실패 {os.path.basename(path)}: {e}")
        v = None
    _TEXSAT_CACHE[path] = v
    return v


def _effective_sat(spec, diff, base_color):
    """역할 계수를 **과채도일 때만** 적용한 실효 채도 계수.

    반환 1.0 = 원본 유지. 재질 채도를 모르면 보수적으로 1.0(무영향).
    """
    coef = float(spec.get("sat", 1.0))
    if coef >= 0.999:
        return 1.0
    cur = (_rgb_sat(base_color) if base_color is not None
           else (_texture_sat(diff) if diff else None))
    if cur is None or cur <= _SAT_KNEE:
        return 1.0                          # 이미 저채도 → 손대지 않는다
    # knee 를 넘은 만큼만 비례 적용 (급격한 계단 방지)
    t = min(1.0, (cur - _SAT_KNEE) / 0.20)
    return 1.0 + (coef - 1.0) * t


# 승격 배율 상한. 넘으면 승격을 포기한다(색 왜곡 < 결 획득).
# 밝기 분기가 배율을 1 근처로 낮추므로 실제로 걸리는 경우는 드물다.
_PROMOTE_MAX_GAIN = 4.0
_TEXMEAN_CACHE = {}


def _texture_mean(path):
    """텍스처 평균 RGB (0~1). PIL 축소 로드 + 캐시."""
    if path in _TEXMEAN_CACHE:
        return _TEXMEAN_CACHE[path]
    v = None
    try:
        from PIL import Image
        with Image.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((64, 64))
            a = np.asarray(im).astype(np.float64) / 255.0
        # [치명 · 색공간] MDL 은 diffuse 를 colorSpace="auto" 로 읽어 **선형으로
        # 디코딩**한 뒤 base_color 를 곱한다. 그런데 종전에는 여기서 JPEG 를
        # **sRGB 인코딩 값 그대로** 평균내 base_color = 의도색 / sRGB평균 을 냈다.
        # 두 공간을 섞은 셈이라 승격 재질이 **2.06~3.64배 어두워졌다**.
        # scene07 이 9.51 → 10.00 으로 역행한 직접 원인이다.
        # → sRGB → 선형 변환 후 평균낸다 (IEC 61966-2-1).
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        v = tuple(float(x) for x in lin.reshape(-1, 3).mean(0))
    except Exception as e:
        print(f"[룩v1][경고] 텍스처 평균 계산 실패 {os.path.basename(path)}: {e}")
        v = None
    _TEXMEAN_CACHE[path] = v
    return v


def _promote_const_to_texture(spec, diffuse_color):
    """[사실화 v1] 상수색 재질을 역할 텍스처로 승격.

    왜 필요한가 — sceneD3 정밀 진단 결과 죽은 픽셀의 **89.8% 가 상수색
    아스팔트 차도 한 장**이었고, 그 표면의 국소표준편차 중앙값은 임계의
    **1/4000** 이었다. 결정적 대조군: 같은 z=0 평면·같은 광원·같은 거리의 잔디
    버지는 dead **0.0%** 이며, 유일한 차이가 디퓨즈 텍스처의 유무였다.

    상수색 MDL 모드(파장 14 m 명도 변조)로는 못 고친다 — `flat_gnd` 는 5×5 픽셀
    창의 "결"을 보는데 macro 변조는 주파수 대역이 아예 다르다.

    **의도 알베도 보존**: 씬 작성자가 고른 색을 그대로 살리기 위해, 텍스처를
    바인딩하되 `base_color = 의도색 / 텍스처평균` 으로 곱해 평균 알베도를
    유지한다. 즉 "색은 그대로, 결만 얻는다".

    반환: (diff, nor, rough, base_color) — 승격 불가 시 (None, None, None, 원색)
    """
    cands = [r for r in (spec.get("tex_alts") or (spec.get("tex"),))
             if r and r in TEX]
    if not cands or diffuse_color is None:
        return None, None, None, diffuse_color
    try:
        # [밝기 분기] **1순위(의미) 우선, 예산 초과 시에만 대안**.
        #   휘도만으로 고르면 낙엽에 잔디 텍스처가 붙는 등 재질 의미가 깨진다.
        #   종전에는 역할당 텍스처가 하나라, 밝은 파라펫(0.9)에 어두운
        #   concrete_floor(선형휘도 0.115)를 씌우면 배율이 7.8배가 되어
        #   클램프(2.5)에 포화 → **의도 대비 2.5~4.8배 어둡고 색까지 편향**됐다.
        #   ("색은 그대로, 결만 얻는다"는 주석이 사실과 반대였다.)
        #   가까운 텍스처를 고르면 배율이 1 근처로 내려가 클램프가 안 걸린다.
        gain_max = float(spec.get("max_gain", _PROMOTE_MAX_GAIN))
        # 후보 순서 = 의미 우선순위. tex 를 맨 앞에 놓는다.
        prim = spec.get("tex")
        order = ([prim] if prim in cands else []) + [r for r in cands if r != prim]
        role = None
        for r in order:
            pth = tex_path(r, "diff")
            if not os.path.isfile(pth):
                continue
            tm = _texture_mean(pth)
            if tm is None or min(tm) < 1e-4:
                continue
            ratio = [float(c) / m for c, m in zip(diffuse_color, tm)]
            # 채널 배율 편차가 크면 색 변동이 특정 채널로 쏠린다(잡음 증폭).
            spread = max(ratio) / max(min(ratio), 1e-6)
            if max(ratio) <= gain_max and spread <= 4.0:
                role = r
                break
        if role is None:
            return None, None, None, diffuse_color
        diff = tex_path(role, "diff")
        nor = tex_path(role, "nor") if "nor" in TEX[role] else None
        rough = tex_path(role, "rough") if "rough" in TEX[role] else None
        if nor and not os.path.isfile(nor):
            nor = None
        if rough and not os.path.isfile(rough):
            rough = None
        tm = _texture_mean(diff)
        if tm is None or min(tm) < 1e-4:
            return None, None, None, diffuse_color
        # 의도 알베도 / 텍스처 평균(선형). 배율이 과하면 텍스처 잡음까지 증폭되고
        # 하이라이트가 클리핑되므로, **클램프에 걸릴 정도면 승격을 포기**하고
        # 상수색 MDL 로 되돌린다. 색을 틀리게 만드느니 결을 포기하는 편이 낫다.
        bc = tuple(max(0.05, r) for r in ratio)
        return diff, nor, rough, bc
    except Exception as e:
        print(f"[룩v1][경고] 텍스처 승격 실패({role}): {e}")
        return None, None, None, diffuse_color


def _look_spec(path):
    """프림 경로에서 룩 사양을 얻는다. `.../Looks/Paving` → paving 사양.

    ① 정확 일치 표(LOOK_ROLE) → ② 접미 변형 제거 후 재시도
    → ③ 키워드 부분문자열 규칙 → ④ "misc"(보수적 기본).
    미상은 최소 처방만 받으므로 회귀 위험이 없다.
    반환: (클래스명, 사양 dict)
    """
    name = str(path).rstrip("/").split("/")[-1]
    cls = LOOK_ROLE.get(name)
    if cls is None:
        base = name.rstrip("0123456789_")
        cls = LOOK_ROLE.get(base)
    if cls is None:
        low = name.lower()
        for c, keys in _LOOK_RULES:
            if any(k in low for k in keys):
                cls = c
                break
    if cls is None:
        cls = "misc"
    return cls, LOOK_CLASS[cls]


def check_assets(roles, hdri=None):
    """지정 역할의 텍스처 존재만 검사. 누락 시 목록 출력 후 sys.exit(1).

    roles: 텍스처 역할 이름 리스트. 특수 pseudo-role:
        "hdri" → noon HDRI(기본 DEFAULT_HDRI, hdri 인자로 지정 가능),
        "mdl"  → OmniPBR.mdl.
    """
    import sys
    missing = []
    for role in roles:
        if role == "hdri":
            p = os.path.join(ASSETS_DIR, hdri or DEFAULT_HDRI)
            if not os.path.isfile(p):
                missing.append((role, "exr", p))
            continue
        if role == "mdl":
            if not os.path.isfile(OMNIPBR_PATH):
                missing.append((role, "mdl", OMNIPBR_PATH))
            continue
        spec = TEX.get(role)
        if spec is None:
            missing.append((role, "?", f"<알 수 없는 역할 '{role}'>"))
            continue
        for kind in ("diff", "nor", "rough"):
            if kind not in spec:
                continue
            p = os.path.join(spec["dir"], spec[kind])
            if not os.path.isfile(p):
                missing.append((role, kind, p))
    if missing:
        print("=" * 64)
        print("[에러] 다음 에셋이 없습니다. assets/scene01/ 다운로드 후 재실행:")
        for role, kind, p in missing:
            print(f"  - [{role}/{kind}] {p}")
        print("=" * 64)
        sys.exit(1)


# ===========================================================================
# [2] boot — SimulationApp + carb 설정 + 스테이지 단위 (scene01 그대로)
# ===========================================================================
def boot(headless):
    """Isaac Sim 부팅. SimulationApp을 무조건 먼저 생성한 뒤 나머지 import.
    carb 캡처 위생 설정 + 스테이지 단위(Z-up, meter)를 적용하고 sim_app 반환.
    stage는 씬에서 omni.usd.get_context().get_stage()로 다시 얻으면 된다.
    """
    from isaacsim import SimulationApp
    sim_app = SimulationApp(
        {"headless": bool(headless), "width": 1920, "height": 1080})

    import carb
    import omni.usd
    from pxr import UsdGeom

    settings = carb.settings.get_settings()
    settings.set("/rtx/post/dlss/execMode", 2)     # DLSS Quality
    settings.set("/rtx/post/aa/op", 3)             # DLSS AA
    # [사실화 P1] PT 가속 — /rtx/pathtracing/spp 기본값이 1이라 totalSpp 를
    # 프레임 수만큼 누적하고 있었다(512spp = 512프레임). subframes 를 올리면
    # 한 update 안에서 여러 샘플을 돌린다. 감독 실측: 4.89 → 0.08 s/컷(61배),
    # 결과 이미지는 픽셀 단위 동일. 씬 파일은 이 키를 건드리지 않으므로
    # 여기서 켜면 전 씬에 적용된다. 기본 OFF(회귀 방지) — env 로 명시 활성화.
    if os.environ.get("NEGOBS_PT_FAST", "") == "1":
        settings.set("/app/renderer/rtSubframes", PT_FAST["subframes"])
        print(f"[렌더] PT 가속 ON — {PT_FAST}")
    # 뷰포트 그리드·축 가이드가 렌더에 찍히지 않게 (캡처 위생)
    settings.set("/app/viewport/grid/enabled", False)
    settings.set("/persistent/app/viewport/displayOptions", 0)
    settings.set("/app/viewport/show/grid", False)
    settings.set("/app/viewport/outline/enabled", False)

    stage = omni.usd.get_context().get_stage()
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    if abs(mpu - 1.0) > 1e-9:
        print(f"[경고] metersPerUnit={mpu} → 1.0(미터)으로 설정")
        UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.Xform.Define(stage, "/World")
    return sim_app


# ===========================================================================
# [3] 지오메트리 헬퍼 (stage 인자화) — UsdGeom.Cube/Cylinder/Sphere
#     주의: UsdGeom.Cube는 size=2 기본(±1) → 스케일 = 원하는 치수/2
# ===========================================================================
def _bind_mtl(prim, mtl):
    if mtl is not None:
        from pxr import UsdShade
        UsdShade.MaterialBindingAPI.Apply(prim).Bind(mtl)


def add_box(stage, path, center, size, mtl=None, collider=False):
    from pxr import UsdGeom, UsdPhysics, Gf
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(2.0)
    cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
    xf = UsdGeom.Xformable(cube)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
    xf.AddScaleOp().Set(Gf.Vec3f(float(size[0]) / 2.0,
                                 float(size[1]) / 2.0,
                                 float(size[2]) / 2.0))
    prim = cube.GetPrim()
    _bind_mtl(prim, mtl)
    if collider:
        UsdPhysics.CollisionAPI.Apply(prim)
    # [사실화 v1] 대면적 수평 지면 슬래브에 미세 기복 스킨을 덮는다.
    # Phase1 E9 에서 **정점 변위가 최대 시각 기여**였다(MDL 교체보다 큼).
    # 슬래브 자체는 건드리지 않으므로 낙차 에지 실루엣은 그대로다(승용 조건②).
    if LOOK_GEO and _skin_wanted(path, size, mtl):    # 메시 신설 = 기하
        try:
            # 시드는 **반드시 결정적**이어야 한다. Python 내장 hash() 는
            # PYTHONHASHSEED 로 프로세스마다 무작위화되므로 매 렌더마다 지형
            # 기복이 달라진다(이 프로젝트는 RNG 100% 결정적이 원칙). crc32 사용.
            if _ground_skin(stage, f"{path}_Skin", center, size, mtl,
                            seed=zlib.crc32(str(path).encode()) % 100000
                            ) is not None:
                LOOK_STATS["skin"] += 1
        except Exception as e:                 # 스킨 실패가 씬을 죽이면 안 된다
            print(f"[룩v1][경고] 지면 스킨 생성 실패 {path}: {e}")
    return cube


def _skin_wanted(path, size, mtl):
    """변위 스킨 대상 판정 — 대면적·수평·지면 계열만.

    승용 조건②("낙차 에지 실루엣은 변위로 흔들리지 않게 보존")에 따라 계단·연석·
    노징·데크 등 낙차 기하는 경로 토큰으로 전면 제외한다. 판정이 애매하면 **제외**가
    기본값이다 — 변위는 개선 항목이지 필수가 아니므로 위험을 지지 않는다.
    """
    if mtl is None:
        return False
    sx, sy, sz = [float(v) for v in size]
    if sx < 4.0 or sy < 4.0:                   # 대면적만 (소품·연석 제외)
        return False
    if sz > 0.8 or sz >= min(sx, sy) * 0.5:    # 수평 슬래브만 (벽·기둥 제외)
        return False
    low = str(path).lower()
    if any(t in low for t in _SKIN_DENY):
        return False
    # 역할은 **바인딩된 재질 경로**(`.../Looks/Paving`)로 판정한다.
    # 지오메트리 경로(`.../Ground`)에는 역할 이름이 없다.
    try:
        mpath = str(mtl.GetPath())
    except Exception:
        return False
    if any(t in mpath.lower() for t in _SKIN_DENY):
        return False
    cls, _spec = _look_spec(mpath)
    return cls in _SKIN_CLASSES


def _ground_skin(stage, path, center, size, mtl, amp_m=0.010,
                 spacing=0.12, taper=0.60, max_n=170, seed=17):
    """[사실화 v1] 지면 슬래브 위에 얹는 **미세 기복 스킨** 메시.

    왜 스킨인가 — 슬래브 자체(Cube)를 변위 메시로 갈아치우면 측면 4면이 사라지고
    **낙차 에지의 실루엣이 흔들린다**(승용 조건②: "낙차 에지는 변위로 흔들리지
    않게 보존"). 그래서 원래 Cube 는 **그대로 두고**, 상면보다 아주 살짝 위에
    변위 스킨을 덮는다. 결과적으로
      · 슬래브의 외곽 실루엣·낙차 에지 = 원래 Cube 가 그대로 결정 (변경 0)
      · 상면 안쪽만 기복 → h0.3 스침각에서 지면이 평면으로 안 읽힘
    이 방식은 GT 낙차 기하도 건드리지 않는다.

    추가 안전장치 2개:
      ① 스킨을 슬래브 경계에서 `edge` 만큼 **안쪽으로 들여** 깐다 → 슬래브 rim 은
         원본 그대로 보이고, 스킨 자신의 rim 은 시야에서 죽는다.
      ② 변위 진폭에 **경계 테이퍼**를 곱해 스킨 가장자리에서 0 으로 수렴 →
         들여깐 경계에서도 단차가 생기지 않는다.

    Phase1 E5 실측: 노멀을 저작하지 않으면 Hydra 가 면법선으로 그려 각져 보인다
    → 유한차분으로 정점 노멀을 직접 계산해 넣는다. `subdivisionScheme="none"` 도
    명시 저작(미저작 시 USD 기본값 catmullClark — Phase1 §2.6 지뢰).
    """
    from pxr import UsdGeom, UsdShade, Gf
    cx, cy, cz = [float(v) for v in center]
    sx, sy, sz = [float(v) for v in size]
    edge = 0.05
    hx, hy = sx / 2.0 - edge, sy / 2.0 - edge
    if hx <= 0.5 or hy <= 0.5:
        return None
    nx = max(4, min(int(2 * hx / spacing), max_n))
    ny = max(4, min(int(2 * hy / spacing), max_n))
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy - hy, cy + hy
    # [중대 M3] 부상 1.5 mm 인데 변위 진폭이 ±9.8 mm 라 스킨의 25~29% 가 슬래브
    # 상면 **아래로 침투**해 원 Cube 평면이 드러나고 교차 컨투어가 생겼다.
    # 부상량을 진폭보다 크게 잡아 스킨이 항상 위에 있게 한다.
    ztop = cz + sz / 2.0 + max(0.0015, amp_m * 1.15)

    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, nx + 1)
    ys = np.linspace(y0, y1, ny + 1)
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    ZZ = np.full_like(XX, ztop)
    # [중대 M4] 최고주파 옥타브(0.07 m)가 메시 간격(0.12~0.24 m)보다 촘촘해
    # **항상 앨리어싱**됐다(나이퀴스트 위반) → 노멀에 고주파 잡음. 간격의 2.5배
    # 이상인 파장만 쓴다.
    _wl_min = spacing * 2.5
    for oi, wl in enumerate(w for w in (0.55, 0.19, 0.07) if w >= _wl_min):
        gx = max(2, int((x1 - x0) / wl) + 1)
        gy = max(2, int((y1 - y0) / wl) + 1)
        g = rng.random((gx + 1, gy + 1)) - 0.5
        fi = np.clip((XX - x0) / (x1 - x0) * gx, 0, gx - 1e-6)
        fj = np.clip((YY - y0) / (y1 - y0) * gy, 0, gy - 1e-6)
        i0, j0 = fi.astype(int), fj.astype(int)
        tx, ty = fi - i0, fj - j0
        sxs, sys_ = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        v = ((g[i0, j0] * (1 - sxs) + g[i0 + 1, j0] * sxs) * (1 - sys_)
             + (g[i0, j0 + 1] * (1 - sxs) + g[i0 + 1, j0 + 1] * sxs) * sys_)
        ZZ += v * amp_m * (0.6 ** oi)
    # 경계 테이퍼 — 스킨 가장자리에서 변위 0
    tx_ = np.clip((np.minimum(XX - x0, x1 - XX)) / max(taper, 1e-6), 0, 1)
    ty_ = np.clip((np.minimum(YY - y0, y1 - YY)) / max(taper, 1e-6), 0, 1)
    t = (tx_ * tx_ * (3 - 2 * tx_)) * (ty_ * ty_ * (3 - 2 * ty_))
    ZZ = ztop + (ZZ - ztop) * t

    pts = [Gf.Vec3f(float(XX[i, j]), float(YY[i, j]), float(ZZ[i, j]))
           for i in range(nx + 1) for j in range(ny + 1)]
    idx, cnt = [], []
    for i in range(nx):
        for j in range(ny):
            a = i * (ny + 1) + j
            idx += [a, a + 1, a + ny + 2, a + ny + 1]
            cnt.append(4)
    m = UsdGeom.Mesh.Define(stage, path)
    m.CreatePointsAttr(pts)
    m.CreateFaceVertexCountsAttr(cnt)
    m.CreateFaceVertexIndicesAttr(idx)
    m.CreateSubdivisionSchemeAttr("none")
    m.CreateExtentAttr([Gf.Vec3f(x0, y0, float(ZZ.min())),
                        Gf.Vec3f(x1, y1, float(ZZ.max()))])
    gzx, gzy = np.gradient(ZZ, (x1 - x0) / nx, (y1 - y0) / ny)
    nrm = np.stack([-gzx, -gzy, np.ones_like(ZZ)], axis=-1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    m.CreateNormalsAttr([Gf.Vec3f(*nrm[i, j])
                         for i in range(nx + 1) for j in range(ny + 1)])
    m.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
    if mtl is not None:
        UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mtl)
    return m


# 상수색 재질을 NegObsGround(base_color 모드)로 태울 클래스.
# 제외: paint(차선·반사띠·점자블록) · sign · glass · water · misc
#   → 이들은 **상수색이 물리적으로 옳다**(v5.1 §4). 텍스처·노이즈를 얹으면
#     오히려 규약 위반이고, 특히 도색 표지는 균일해야 단서로 기능한다.
# [중대 M1 + 정책 정합] 보고서 §2.2 의 3단 재질 정책은 "식생·금속·목재 = OmniPBR"
# 인데 코드는 이 집합에 셋 다 넣어 상수색이면 MDL 로 보내고 있었다(59종 불일치).
# 특히 **금속은 MDL 에 metallic 입력이 아예 없어 금속성이 소실**된다.
# 정책대로 지면·구조물 계열만 남긴다.
# metal 만 제외하면 된다 — MDL 이 metalness=0 축약형이라 **금속성만** 소실된다.
# 식생·목재는 금속성이 없으므로 MDL 로 보내도 무방하고, scene07 진단에서
# 상수색 식생 2.26%p·상수색 목재 1.61%p 가 죽은 픽셀 상위였다.
_CONST_MDL_CLASSES = {"paving", "concrete", "brick", "stone", "soil",
                      "gravel", "asphalt", "nosing", "curb", "snow",
                      "veg", "wood"}

# 변위 스킨을 붙일 역할 클래스 (지면 계열만). 계단·연석·노징은 제외 —
# 낙차 에지 기하이므로 승용 조건②에 따라 손대지 않는다.
_SKIN_CLASSES = {"paving", "concrete", "asphalt", "soil", "gravel", "stone"}
# 경로에 이 토큰이 있으면 지면이어도 변위 금지 (낙차 기하·보행 안전 관련)
_SKIN_DENY = ("stair", "step", "tread", "riser", "nosing", "curb", "ramp",
              "landing", "deck", "platform", "edge", "lip", "sill")


def add_cylinder(stage, path, center, radius, height, mtl=None,
                 rotY=0.0, rotX=0.0, collider=False):
    from pxr import UsdGeom, UsdPhysics, Gf
    cyl = UsdGeom.Cylinder.Define(stage, path)
    cyl.CreateRadiusAttr(float(radius))
    cyl.CreateHeightAttr(float(height))
    cyl.CreateAxisAttr(UsdGeom.Tokens.z)
    xf = UsdGeom.Xformable(cyl)
    # 순서: translate → rotate (프림 원점에서 회전 후 이동)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
    if abs(rotY) > 1e-9:
        xf.AddRotateYOp().Set(float(rotY))
    if abs(rotX) > 1e-9:
        xf.AddRotateXOp().Set(float(rotX))
    prim = cyl.GetPrim()
    _bind_mtl(prim, mtl)
    if collider:
        UsdPhysics.CollisionAPI.Apply(prim)
    return cyl


def add_sphere(stage, path, center, scale3, mtl=None):
    from pxr import UsdGeom, Gf
    sph = UsdGeom.Sphere.Define(stage, path)
    sph.CreateRadiusAttr(1.0)
    xf = UsdGeom.Xformable(sph)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
    xf.AddScaleOp().Set(Gf.Vec3f(*[float(s) for s in scale3]))
    _bind_mtl(sph.GetPrim(), mtl)
    return sph


def _oriented_box(stage, path, center, size, mtl=None, collider=False,
                  rotz=0.0, rotx=0.0):
    """회전 가능한 솔리드 Cube. op 리스트 = translate→rotZ→rotX→scale.
    USD row-vector 규약상 리스트 역순으로 점에 적용된다: scale → rotX → rotZ →
    translate. 즉 rotX 는 (아직 방위로 안 돌린) 로컬 프레임에서 먼저 걸리고,
    이어 rotZ 가 그 로컬 프레임 전체를 방위각으로 회전시킨다.
      build_arc_steps 관례: 로컬 X=반경방향, Y=접선(현), Z=높이.
      → rotZ 이전의 로컬 X 는 방위 0의 반경축이며, rotZ 후 실제 반경방향이 된다.
        따라서 '접선방향 경사'(현을 따라 오르내림)는 **로컬 X축(rotX) 회전**이다.
        (접선=로컬Y 이므로 접선을 기울이는 축은 그에 수직인 로컬X = 반경축.)"""
    from pxr import UsdGeom, UsdPhysics, Gf
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(2.0)
    cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
    xf = UsdGeom.Xformable(cube)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(c) for c in center]))
    if abs(rotz) > 1e-12:
        xf.AddRotateZOp().Set(float(rotz))
    if abs(rotx) > 1e-12:
        xf.AddRotateXOp().Set(float(rotx))
    xf.AddScaleOp().Set(Gf.Vec3f(float(size[0]) / 2.0,
                                 float(size[1]) / 2.0,
                                 float(size[2]) / 2.0))
    prim = cube.GetPrim()
    _bind_mtl(prim, mtl)
    if collider:
        UsdPhysics.CollisionAPI.Apply(prim)
    return cube


# ===========================================================================
# [4] make_pbr — OmniPBR 월드투영 팩토리 (scene01 그대로 + specular_level)
# ===========================================================================
def make_pbr(stage, path, diff=None, nor=None, rough=None, scale_m=1.0,
             tint=None, metallic=0.0, roughness_const=None,
             diffuse_color=None, bump=1.0, specular_level=None,
             emission_color=None, emission_intensity=None, uv_mode=False,
             unit_cell=None):
    """OmniPBR 재질. diff 지정 시 월드 스페이스 투영 텍스처, 아니면 상수 컬러.
    specular_level 지정 시 sh.CreateInput("specular_level", Float).
    emission_color+emission_intensity 지정 시 발광(enable_emission) — 실내
    씬(D4 등) 발광 패널용. RT 단일바운스 기여 미미, 판정은 PT 8바운스(교훈 7).
    uv_mode=True: 월드 투영 대신 메시 st(UV 0..1)로 샘플 — 사인 패널처럼
    텍스처가 면에 1:1 정합해야 하는 경우(build_sign 의 _sign_quad 전용).

    [사실화 v1] `NEGOBS_LOOK_MTL=1` 이면 프림 경로에서 역할을 읽어 룩 사양을
    주입한다(§1b). 플래그가 꺼져 있으면 아래 코드 경로는 **전혀 타지 않으며**
    종전 동작과 바이트 단위로 동일하다. 이 함수는 재질만 만들므로 **전부
    `LOOK_MTL` 소속**이다(규칙 R-1 — 프림 집합을 바꾸지 않는다).
    """
    from pxr import UsdShade, Sdf, Gf

    _look_omni = None
    if LOOK_MTL and not uv_mode and emission_color is None:
        cls, spec = _look_spec(path)
        LOOK_STATS["roles"][cls] = LOOK_STATS["roles"].get(cls, 0) + 1
        if diff is not None and spec["mdl"] == "ground":
            LOOK_STATS["ground"] += 1
            return _make_ground_pbr(stage, path, diff, nor, rough, scale_m,
                                    spec, tint=tint,
                                    roughness_const=roughness_const,
                                    specular_level=specular_level, bump=bump,
                                    unit_cell=unit_cell)
        # [사실화 v1] **상수색 재질도 MDL 로 태운다.**
        # 33씬 make_pbr 호출의 절반 이상이 diffuse_color 상수색인데, 상수색은
        # 정의상 완전 평탄이라 flat% 의 최대 발생원이다. 텍스처를 새로 조달하지
        # 않고도 MDL 의 월드 macro 변조·roughness 노이즈·웨더링을 상수색 위에
        # 얹으면 "평탄한 단색"이 아니게 된다(MDL v1.7.0 `base_color`).
        # 단 **상수색이 물리적으로 옳은 역할은 제외**한다 — 차선 도색·반사띠·
        # 점자블록·사인·유리·수면. v5.1 §4 가 이들을 상수색으로 못박았다.
        if (diff is None and diffuse_color is not None
                and cls in _CONST_MDL_CLASSES):
            # 먼저 역할 텍스처로 **승격**을 시도한다(의도 알베도 보존).
            # 승격되면 patch 혼합·tri_dither·macro·desat 까지 전부 켜지므로
            # 상수색 모드보다 훨씬 강력하다.
            pd, pn, pr, pbc = _promote_const_to_texture(spec, diffuse_color)
            if pd is not None:
                LOOK_STATS["promoted"] = LOOK_STATS.get("promoted", 0) + 1
                return _make_ground_pbr(
                    stage, path, pd, pn, pr,
                    scale_m if scale_m != 1.0 else spec.get("tex_scale", 1.2),
                    spec, tint=tint, roughness_const=None,
                    specular_level=(specular_level if specular_level is not None
                                    else spec.get("spec")),
                    bump=spec.get("bump", 1.0), base_color=pbc,
                    unit_cell=unit_cell)
            LOOK_STATS["const_mdl"] = LOOK_STATS.get("const_mdl", 0) + 1
            return _make_ground_pbr(stage, path, None, None, None, scale_m,
                                    spec, tint=tint,
                                    roughness_const=roughness_const,
                                    specular_level=specular_level, bump=bump,
                                    base_color=diffuse_color,
                                    unit_cell=unit_cell)
        # 텍스처 재질 → 베벨 + 디테일 노멀.
        # **상수색 재질도 베벨은 받는다** — 게이트 1차에서 상수색을 통째로
        # 건너뛰고 있었고, 상수색이야말로 flat% 의 주범이다. 텍스처화는 별도
        # 항목(브리프 2-7, 전수 감사 대기)이지만 베벨은 텍스처가 필요 없다.
        LOOK_STATS["omni_tex" if diff is not None else "const"] += 1
        _look_omni = spec
    elif LOOK_MTL:
        LOOK_STATS["skipped"] += 1

    mtl = UsdShade.Material.Define(stage, path)
    sh = UsdShade.Shader.Define(stage, path + "/Shader")
    sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    sh.SetSourceAsset(Sdf.AssetPath(OMNIPBR_PATH), "mdl")
    sh.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
    F = Sdf.ValueTypeNames.Float
    C3 = Sdf.ValueTypeNames.Color3f
    A = Sdf.ValueTypeNames.Asset
    B = Sdf.ValueTypeNames.Bool
    F2 = Sdf.ValueTypeNames.Float2

    def _tex(name, path_, cs):
        i = sh.CreateInput(name, A)
        i.Set(path_)
        try:                                   # normalmap 은 raw 필수
            i.GetAttr().SetColorSpace(cs)
        except Exception:
            pass

    if diff is not None:
        _tex("diffuse_texture", diff, "auto")
        if nor is not None:
            _tex("normalmap_texture", nor, "raw")
        if rough is not None:
            _tex("reflectionroughness_texture", rough, "raw")
            sh.CreateInput("reflection_roughness_texture_influence",
                           F).Set(1.0)
        if uv_mode:
            # [v5] 메시 st 샘플 — 텍스처가 면 UV 0..1에 1:1 정합(사인 패널)
            sh.CreateInput("project_uvw", B).Set(False)
        else:
            # 월드 스페이스 투영 (축정렬 박스 → 늘어남 없음). world_or_object=True 가
            # 월드 스페이스. False(오브젝트 스페이스)면 스케일된 Cube에서 텍스처가
            # 스케일에 끌려 늘어난다.
            sh.CreateInput("project_uvw", B).Set(True)
            sh.CreateInput("world_or_object", B).Set(True)
            s = 1.0 / float(scale_m)           # texture_scale = 1/타일크기[m]
            sh.CreateInput("texture_scale", F2).Set(Gf.Vec2f(s, s))
        sh.CreateInput("bump_factor", F).Set(float(bump))
    if diffuse_color is not None:
        sh.CreateInput("diffuse_color_constant",
                       C3).Set(Gf.Vec3f(*diffuse_color))
    if tint is not None:
        sh.CreateInput("diffuse_tint", C3).Set(Gf.Vec3f(*tint))
    sh.CreateInput("metallic_constant", F).Set(float(metallic))
    if roughness_const is not None:
        sh.CreateInput("reflection_roughness_constant",
                       F).Set(float(roughness_const))
    if specular_level is not None:
        sh.CreateInput("specular_level", F).Set(float(specular_level))
    if emission_color is not None and emission_intensity is not None:
        sh.CreateInput("enable_emission", B).Set(True)
        sh.CreateInput("emissive_color", C3).Set(Gf.Vec3f(*emission_color))
        sh.CreateInput("emissive_intensity", F).Set(float(emission_intensity))
    if _look_omni is not None:
        # 가짜 베벨 — Kit 106.1+ 정식 구현, RT·PT 양쪽 동작 확인(Phase1 E1).
        if _look_omni["bevel"] > 0.0:
            LOOK_STATS["bevel"] += 1
            sh.CreateInput("round_edges_radius", F).Set(
                float(_look_omni["bevel"]))
            sh.CreateInput("round_edges_roundness", F).Set(1.0)
            sh.CreateInput("round_edges_across_materials", B).Set(False)
        # 디테일 노멀 — 근접 텍셀 뭉개짐 완화(Phase1 E3)
        if (_look_omni.get("detail") and diff is not None
                and os.path.isfile(_DETAIL_NOR)):
            LOOK_STATS["detail"] += 1
            _tex("detail_normalmap_texture", _DETAIL_NOR, "raw")
            sh.CreateInput("detail_bump_factor", F).Set(0.45)
            ds = 1.0 / 0.08                    # 8 cm 주기 미세 그레인
            sh.CreateInput("detail_texture_scale", F2).Set(Gf.Vec2f(ds, ds))

    for out in ("surface", "displacement", "volume"):
        mtl.CreateOutput(f"mdl:{out}",
                         Sdf.ValueTypeNames.Token).ConnectToSource(
            sh.ConnectableAPI(), "out")
    return mtl


# Unit-cell jitter defaults (T1 §1.8-3). sigma 0.10 / accent 7 % are the spec
# values; they only take effect once ground_kit supplies a cell period.
UNIT_CELL_DEFAULTS = dict(sigma=0.10, accent=0.07)


def _wire_unit_cell(sh, F, F2, unit_cell):
    """Pass the ground_kit unit-cell ledger through to the MDL. Default = OFF.

    Contract: `ground_kit_spec_v1.md` §4.5 (U1~U4) / `t1_material_layer_spec_v1.md`
    §1.8-3. The MDL quantises the dominant-plane coordinate into cells and gives
    each cell one log-normal albedo scalar (zero texture fetches) — that scalar
    is the principal component of sigma_LF for every paving profile.

    `unit_cell` is `None` (default) or `(cell_m, (ox, oy))`, optionally
    `(cell_m, (ox, oy), sigma, accent)`. Nothing is authored when it is None or
    when cell_m <= 0, so the shader is byte-identical to before — the wiring
    exists but the value injection waits on the ground_kit ledger (spec §8.1 P2).

    U3 is why the ORIGIN is mandatory and not optional: the MDL's default grid
    origin is the UV origin, not the scene origin, so a matching period with a
    mismatched phase produces a half-cell offset seam under the engraved joints.
    U4 (`unit_cell = None` profile + jitter on) is a T1-side FAIL, raised here:
    unmodular paving (asphalt, membrane) has no cell to jitter.
    """
    if unit_cell is None:
        return False
    try:
        cell = float(unit_cell[0])
        origin = unit_cell[1]
        sigma = float(unit_cell[2]) if len(unit_cell) > 2 else \
            UNIT_CELL_DEFAULTS["sigma"]
        accent = float(unit_cell[3]) if len(unit_cell) > 3 else \
            UNIT_CELL_DEFAULTS["accent"]
    except (TypeError, IndexError, ValueError) as e:
        raise ValueError(f"unit_cell 형식 오류 {unit_cell!r}: {e}")
    if cell <= 0.0:                       # U4 — explicitly "no module" profile
        if sigma > 0.0:
            raise ValueError(
                "unit_cell 주기가 0 이하인데 지터가 켜져 있다(계약 U4 위반) — "
                "무모듈 포장(아스팔트·도막)에 셀 지터는 물리적으로 틀렸다")
        return False
    if origin is None:                    # U3 — period without phase is not a contract
        raise ValueError(
            "unit_cell_origin 미제공(계약 U3 위반) — MDL 기본 원점은 UV 원점이지 "
            "씬 원점이 아니라서, 주기가 맞아도 위상이 어긋나면 반 칸 이음매가 생긴다")
    ox, oy = float(origin[0]), float(origin[1])
    sh.CreateInput("unit_cell_m", F2).Set(_vec2(cell, cell))
    sh.CreateInput("unit_cell_origin", F2).Set(_vec2(ox, oy))
    sh.CreateInput("unit_albedo_sigma", F).Set(sigma)
    sh.CreateInput("unit_accent_frac", F).Set(accent)
    LOOK_STATS["unit_cell"] = LOOK_STATS.get("unit_cell", 0) + 1
    return True


def _vec2(a, b):
    from pxr import Gf
    return Gf.Vec2f(float(a), float(b))


def _make_ground_pbr(stage, path, diff, nor, rough, scale_m, spec,
                     tint=None, roughness_const=None, specular_level=None,
                     bump=1.0, base_color=None, metallic=0.0,
                     unit_cell=None):
    """[사실화 v1] NegObsGround.mdl 재질 — 지면·사면 계열 전용.

    OmniPBR 의 `project_uvw` 는 트라이플래너가 아니라 **큐빅 투영**이라 경사면에서
    텍스처가 낙하 방향으로 뭉개져 늘어난다(Phase1 E2 에서 38° 경사면 split-face 로
    확인). 이 MDL 은 노멀 가중 소프트 트라이플래너 + 45° 보조 기저로 그 결함이
    없다. 우리 씬은 계단 챌면·램프·제방으로 가득해 **낙차가 있는 바로 그 지점**에
    결함이 집중돼 있었다.

    주의 — `texture_scale` 의미가 OmniPBR 과 다르다(트라이플래너 ↔ 큐빅).
    같은 scale_m 을 줘도 타일 크기가 달라지므로 `_GROUND_SCALE_FIX` 로 보정한다.
    """
    from pxr import UsdShade, Sdf, Gf
    mtl = UsdShade.Material.Define(stage, path)
    sh = UsdShade.Shader.Define(stage, path + "/Shader")
    sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    sh.SetSourceAsset(Sdf.AssetPath(MDL_GROUND), "mdl")
    sh.SetSourceAssetSubIdentifier("NegObsGround", "mdl")
    F = Sdf.ValueTypeNames.Float
    C3 = Sdf.ValueTypeNames.Color3f
    A = Sdf.ValueTypeNames.Asset
    B = Sdf.ValueTypeNames.Bool
    F2 = Sdf.ValueTypeNames.Float2

    def _tex(name, p, cs):
        i = sh.CreateInput(name, A)
        i.Set(p)
        try:
            i.GetAttr().SetColorSpace(cs)
        except Exception:
            pass

    # diff=None 이면 텍스처를 바인딩하지 않는다 → MDL 이 흰색을 반환하고
    # base_color 곱셈으로 상수색이 복원된다(v1.7.0 상수색 모드).
    if diff is not None:
        _tex("diffuse_texture_a", diff, "auto")
    if nor is not None:
        _tex("normalmap_texture_a", nor, "raw")
    if rough is not None:
        _tex("roughness_texture_a", rough, "raw")
    # [치명 C1 수정] MDL 에는 diffuse_tint 입력이 없어 종전에는 씬이 준 tint 를
    # **경고만 찍고 통째로 버렸다**. 실측 77 호출 / 30 씬이 영향받았고,
    # sceneD4 Facade 는 tint (0.14,0.14,0.15) 가 사라져 알베도가 **7.1배**로
    # 렌더되고 있었다. OmniPBR 의 diffuse_tint 는 albedo 곱셈이므로
    # base_color 에 접어 넣으면 **수학적으로 동일**하다.
    _bc = list(base_color) if base_color is not None else [1.0, 1.0, 1.0]
    if tint is not None:
        _bc = [c * t for c, t in zip(_bc, tint)]
    if base_color is not None or tint is not None:
        sh.CreateInput("base_color", C3).Set(Gf.Vec3f(*_bc))
    s = _GROUND_SCALE_FIX / float(scale_m)
    sh.CreateInput("texture_scale_a", F2).Set(Gf.Vec2f(s, s))
    sh.CreateInput("bump_factor_a", F).Set(
        float(spec.get("bump", bump)))
    sh.CreateInput("use_blend", B).Set(False)
    # 반복 파괴 — 모듈형 포장은 patch 0(패턴 파손 방지), 자연 지면은 1
    sh.CreateInput("patch_mix_a", F).Set(float(spec.get("patch", 1.0)))
    sh.CreateInput("patch_wavelength_a", F).Set(4.0)
    # 상수색 모드는 텍스처 고주파가 없어 macro 를 강하게 주면 얼룩으로 보인다.
    sh.CreateInput("macro_amp_a", F).Set(0.07 if diff is None else 0.12)
    sh.CreateInput("macro_wavelength_a", F).Set(14.0)
    sh.CreateInput("desat_bright_a", F).Set(0.0 if diff is None else 0.30)
    sh.CreateInput("saturation_a", F).Set(
        _effective_sat(spec, diff, base_color))
    sh.CreateInput("rough_noise_a", F).Set(0.22)
    sh.CreateInput("rough_noise_wavelength_a", F).Set(1.2)
    # 상수색 모드는 텍스처가 없어 축 전환 스트리크가 발생하지 않는다 →
    # 디더링 노이즈 6회가 순수 낭비다. 0 으로 꺼서 비용을 줄인다.
    sh.CreateInput("tri_dither", F).Set(0.0 if diff is None else 0.35)
    sh.CreateInput("tri_dither_wavelength", F).Set(0.15)
    sh.CreateInput("tri_weight_exp", F).Set(6.0)
    if roughness_const is not None:            # 상수 roughness 요구 → floor 로 이식
        # **함정**: 이 경로는 rough_mult_a=0 이라 roughness 맵을 통째로 무시한다.
        # 텍스처 승격 시에는 roughness_const 를 넘기지 않는 이유다(진단 P1).
        sh.CreateInput("rough_mult_a", F).Set(0.0)
        sh.CreateInput("rough_floor_a", F).Set(float(roughness_const))
    if specular_level is not None:
        sh.CreateInput("specular_level_a", F).Set(float(specular_level))
    # 웨더링 (MDL v1.6.0). spec 에 weather 키가 없으면 전부 0 = 무영향.
    w = spec.get("weather") or {}
    if w:
        for key, val in (("grime_strength", w.get("grime", 0.0)),
                         ("grime_desat", w.get("grime_desat", 0.0)),
                         ("grime_height", w.get("grime_h", 0.35)),
                         ("splash_strength", w.get("splash", 0.0)),
                         ("streak_strength", w.get("streak", 0.0)),
                         ("dust_strength", w.get("dust", 0.0)),
                         ("dust_desat", w.get("dust_desat", 0.0)),
                         ("weather_rough", w.get("wrough", 0.0))):
            sh.CreateInput(key, F).Set(float(val))
        LOOK_STATS["weather"] = LOOK_STATS.get("weather", 0) + 1
    # [중대 M1] NegObsGround 는 metalness=0 경로만 이식된 축약형이라 metallic
    # 입력이 없다. 상수색 금속(난간·볼라드·셔터·펜스 — 금속 37종·113 호출)이
    # 이 경로로 오면 **금속성이 소실**된다. → 금속은 MDL 로 보내지 않는다.
    if spec.get("bevel", 0.0) > 0.0:
        sh.CreateInput("round_edges_radius", F).Set(float(spec["bevel"]))
        sh.CreateInput("round_edges_roundness", F).Set(1.0)
        sh.CreateInput("round_edges_across_materials", B).Set(False)
    _wire_unit_cell(sh, F, F2, unit_cell)
    # tint 는 위에서 base_color 에 접어 넣었다(아래 참조).
    for out in ("surface", "displacement", "volume"):
        mtl.CreateOutput(f"mdl:{out}",
                         Sdf.ValueTypeNames.Token).ConnectToSource(
            sh.ConnectableAPI(), "out")
    return mtl


# ===========================================================================
# [5] 계단·기하 빌더
# ===========================================================================
def _stair_steps(x0, riser, tread, n, z_top, riser_list, tread_list):
    """단별 (xa, xb, ztop) 리스트. 상면 z_top에서 +X로 하강.
    riser_list/tread_list 지정 시 불규칙 단 (없으면 균일 riser/tread × n).
    반환 단 수 = 두 리스트 중 존재하는 것의 길이(없으면 n)."""
    risers = list(riser_list) if riser_list else [riser] * n
    treads = list(tread_list) if tread_list else [tread] * n
    m = max(len(risers), len(treads))
    if len(risers) < m:
        risers += [risers[-1]] * (m - len(risers))
    if len(treads) < m:
        treads += [treads[-1]] * (m - len(treads))
    steps = []
    xa = float(x0)
    z = float(z_top)
    for i in range(m):
        z = z - float(risers[i])           # i번째 단 상면(디딤면) 높이
        xb = xa + float(treads[i])
        steps.append((xa, xb, z))
        xa = xb
    return steps


def build_straight_stairs(stage, prefix, x0, y0, y1, riser, tread, n, base_z,
                          mtl, riser_list=None, tread_list=None, z_top=0.0,
                          collider=True, width_pairs=None):
    """직선 계단(솔리드 적층). 각 단은 디딤면(tread)이 노출되는 박스.
    riser_list/tread_list로 불규칙 단 지원(scene04). z_top=상단 시작 지면.
    width_pairs: 단별 (y0_i,y1_i) 리스트(폭 점증 tapered 지원). None이면 전 단
      공통 (y0,y1). 길이가 단 수보다 짧으면 마지막 값을 반복(안전 확장).
      *기존 호출은 width_pairs 미지정 → 완전 무영향.*
    반환: 생성 Cube 프림 리스트."""
    prims = []
    steps = _stair_steps(x0, riser, tread, n, z_top, riser_list, tread_list)
    wp = list(width_pairs) if width_pairs else None
    for i, (xa, xb, ztop) in enumerate(steps, 1):
        if wp is not None:
            wy0, wy1 = wp[min(i - 1, len(wp) - 1)]
        else:
            wy0, wy1 = y0, y1
        cy = (wy0 + wy1) / 2.0
        Ly = wy1 - wy0
        cx = (xa + xb) / 2.0
        cz = (ztop + base_z) / 2.0
        hz = ztop - base_z
        prims.append(add_box(stage, f"{prefix}/Step_{i}", (cx, cy, cz),
                             (xb - xa, Ly, hz), mtl, collider=collider))
    return prims


def build_arc_steps(stage, prefix, cx, cy, r_in, r_out, a0_deg, a1_deg, seg,
                    top_z, base_z, mtl, collider=True):
    """호(a0..a1)를 seg개 사다리꼴(근사) 박스로 티어 1개분 생성.
    각 세그 = rotZ(세그 중앙각) + translate 한 Cube. 반경 두께 = r_out-r_in,
    현길이 = 2*r_mid*sin(dθ/2)*1.02 (세그 간 쐐기 틈 방지 겹침 여유).
    반환: 생성 Cube 프림 리스트."""
    from pxr import UsdGeom, UsdPhysics, Gf
    r_mid = (r_in + r_out) / 2.0
    radial = r_out - r_in
    height = top_z - base_z
    cz = (top_z + base_z) / 2.0
    dth = math.radians((a1_deg - a0_deg) / float(seg))
    chord = 2.0 * r_out * math.sin(dth / 2.0) * 1.03   # 외경 기준 커버(룩 r1: r_mid 기준은 외측 쐐기 틈)
    prims = []
    for k in range(seg):
        a_mid = math.radians(a0_deg) + (k + 0.5) * dth
        px = cx + r_mid * math.cos(a_mid)
        py = cy + r_mid * math.sin(a_mid)
        cube = UsdGeom.Cube.Define(stage, f"{prefix}/Seg_{k}")
        cube.CreateSizeAttr(2.0)
        cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
        xf = UsdGeom.Xformable(cube)
        # translate → rotZ → scale. 로컬 X=반경방향, Y=접선(현), Z=높이.
        xf.AddTranslateOp().Set(Gf.Vec3d(float(px), float(py), float(cz)))
        xf.AddRotateZOp().Set(math.degrees(a_mid))
        xf.AddScaleOp().Set(Gf.Vec3f(float(radial) / 2.0,
                                     float(chord) / 2.0,
                                     float(height) / 2.0))
        prim = cube.GetPrim()
        _bind_mtl(prim, mtl)
        if collider:
            UsdPhysics.CollisionAPI.Apply(prim)
        prims.append(cube)
    return prims


def build_nosing(stage, prefix, x0, y0, y1, riser, tread, n, base_z=0.0,
                 mtl=None, color=(0.85, 0.72, 0.10), width=0.05, proud=0.001,
                 riser_list=None, tread_list=None, z_top=0.0):
    """단코 논슬립 띠. 각 단 상면(디딤면) 전연부(+X 끝 모서리)에 상수색 박스 띠.
    mtl=None이면 color로 상수색 재질 내부 생성. width=띠 폭(X), proud=돌출.
    build_straight_stairs와 동일한 단 정의(x0,y0,y1,riser,tread,n 또는 리스트).
    반환: 생성 프림 리스트."""
    if mtl is None:
        mtl = make_pbr(stage, prefix + "/NosingMtl",
                       diffuse_color=color, roughness_const=0.7, metallic=0.0)
    cy = (y0 + y1) / 2.0
    Ly = y1 - y0
    thk = proud + 0.005                     # 얇은 띠 (일부 매입 + proud 돌출)
    prims = []
    steps = _stair_steps(x0, riser, tread, n, z_top, riser_list, tread_list)
    for i, (xa, xb, ztop) in enumerate(steps, 1):
        # 전연부(xb) 안쪽으로 width 만큼. 상면 위 proud 돌출.
        bx = xb - width / 2.0
        z_hi = ztop + proud
        cz = z_hi - thk / 2.0
        prims.append(add_box(stage, f"{prefix}/Nose_{i}", (bx, cy, cz),
                             (width, Ly, thk), mtl))
    return prims


def build_railing_line(stage, prefix, y, x_start, x_top, run, drop, ground_fn,
                       mtl, rail_h=None, post_r=0.02, spacing=None, rail_r=0.03,
                       rail_mid_r=0.018, rail_mid_drop=0.45,
                       baluster_r=0.009, baluster_gap=0.098, handrail=True):
    """레일 1선(scene01 build_cues 일반화). 상단 레일 + 중간 레일 + 포스트.
      y        : 레일 Y 위치
      x_start  : 수평 연장 시작 x  (x_start..x_top 구간은 수평)
      x_top    : 경사 시작 x       (여기서부터 +X로 drop 하강)
      run,drop : 경사 구간 수평길이·낙차
      ground_fn: x→지면z 콜백 (포스트 하단 착지 높이). 단면(계단)이면 계단식.
    반환: 생성 프림 리스트."""
    # 기본값은 **LOOK_GEO 에서만** 법정값으로 바뀐다(포스트 개수 = 기하).
    # 종전에 기본값 자체를 1.1/2.0 으로 바꿨더니, 이 두 값을 명시하지 않는
    # 호출부(scene03/14/17/21)에서 **룩 레이어를 꺼도 포스트 개수가 바뀌었다**.
    # 포스트 루프는 게이트 밖이라 대조군 기하가 오염된다 —
    # bc87292 에서 스스로 "치명 C3" 로 명명하고 고쳤던 것과 동일 유형의 재발.
    if rail_h is None:
        rail_h = 1.1 if LOOK_GEO else 0.9      # 도로안전시설 지침 2.5
    if spacing is None:
        spacing = 2.0 if LOOK_GEO else 1.2
    ground_ref = float(ground_fn(x_top))       # 경사 상단 지면
    top0 = ground_ref + rail_h                 # x_top 에서의 레일 상면 z
    L = math.hypot(run, drop)
    ang = math.degrees(math.atan2(drop, run))  # 경사각(수평 대비)
    prims = []

    def _seg(tag, r, z_off):
        # 수평 연장 (x_start..x_top, z=top0-z_off) — Cylinder Z축을 X로
        if x_top - x_start > 1e-6:
            prims.append(add_cylinder(
                stage, f"{prefix}/{tag}Ext",
                ((x_start + x_top) / 2.0, y, top0 - z_off),
                r, x_top - x_start, mtl, rotY=90.0))
        # 경사 (x_top..x_top+run), z: top0 → top0-drop
        prims.append(add_cylinder(
            stage, f"{prefix}/{tag}Slope",
            (x_top + run / 2.0, y, top0 - z_off - drop / 2.0),
            r, L, mtl, rotY=90.0 + ang))

    _seg("RailTop", rail_r, 0.0)
    _seg("RailMid", rail_mid_r, rail_mid_drop)
    x_end = x_top + run

    # 세로 간살 — 「도로안전시설 지침」난간 표준. 안목(살 사이 빈틈) 100mm 이하가
    # 법정 요건이라 실제 한국 난간은 예외 없이 촘촘하다. 경사 구간에서도 살은
    # **연직**(레일만 기울고 살은 서 있음)이라 실루엣이 확연히 다르다.
    # LOOK_GEO 게이트 안 — A/B 대조군 보존.
    if LOOK_GEO and baluster_r > 0:
        pitch = 2.0 * baluster_r + baluster_gap
        xb = x_start + pitch * 0.5
        b = 0
        while xb <= x_end - pitch * 0.25:
            t = max(0.0, min((xb - x_top) / run, 1.0)) if run > 1e-9 else 0.0
            ztop = top0 - drop * t - rail_r          # 상단 레일 밑면
            gz = float(ground_fn(xb))
            # 간살은 **지면 가까이까지** 내려와야 한다. 종전엔 중간 레일에서
            # 멈춰 난간 높이의 43% 만 채웠고, 하부 0.45~0.60m 구간의 실제
            # 빈틈이 인용한 법정 안목 100mm 를 11~28배로 위반했다.
            # (법정 요건을 근거로 넣은 기하가 그 요건을 어기고 있었다.)
            zbot = max(gz + 0.04, top0 - drop * t - rail_h + 0.04)
            h = ztop - zbot
            if h > 0.05:
                prims.append(add_cylinder(
                    stage, f"{prefix}/Bal_{b}", (xb, y, zbot + h / 2.0),
                    baluster_r, h, mtl))
            xb += pitch
            b += 1
        LOOK_STATS["baluster"] = LOOK_STATS.get("baluster", 0) + b

    # 포스트: 실제 지면(ground_fn)에 착지, 상단=레일선.
    xp = x_start
    p = 0
    while xp <= x_end + 1e-6:
        gz = float(ground_fn(xp))
        t = max(0.0, min((xp - x_top) / run, 1.0)) if run > 1e-9 else 0.0
        railz = top0 - drop * t
        ph = railz - gz
        if ph > 1e-3:
            prims.append(add_cylinder(
                stage, f"{prefix}/Post_{p}", (xp, y, gz + ph / 2.0),
                post_r, ph, mtl))
        xp += spacing
        p += 1

    # ── 손잡이(handrail) ───────────────────────────────────────────────
    # 피난·방화구조 규칙 §15④. **33씬 전부 미구현**이었다.
    # φ32~38 · 높이 850 · **끝단 수평 연장 ≥300** — 이 끝단 갈고리가
    # 한국 계단 실루엣의 특징인데 우리는 레일이 그냥 뚝 끊겨 있었다.
    # GT 무영향: 계단면 위 수직/수평 부재라 z(x,y) 를 바꾸지 않는다.
    if LOOK_GEO and handrail and run > 0.3:
        try:
            prims += sk.build_handrail(
                stage, f"{prefix}/Handrail", y, x_top, run, drop, mtl,
                add_cylinder, z_top=ground_ref, ground_fn=ground_fn,
                strict=False)
            LOOK_STATS["handrail"] = LOOK_STATS.get("handrail", 0) + 1
        except Exception as e:
            print(f"[룩v1][경고] 손잡이 실패 {prefix}: {e}")
    return prims


def build_water(stage, path, x0, y0, x1, y1, z, thick=0.2, mtl=None):
    """수면 슬래브. 상수색 (0.05,0.10,0.11), roughness 0.03, metallic 0.
    상면이 z에 오도록 얇은 박스. 반환: Cube 프림."""
    if mtl is None:
        mtl = make_pbr(stage, path + "_mtl",
                       diffuse_color=(0.05, 0.10, 0.11),
                       roughness_const=0.03, metallic=0.0)
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    return add_box(stage, path, (cx, cy, z - thick / 2.0),
                   (abs(x1 - x0), abs(y1 - y0), thick), mtl)


def build_slope(stage, path, x0, z0, run, drop, y0, y1, thick, mtl,
                margin=0.3, collider=True):
    """rotateY 회전 박스 사면. 상면이 (x0,z0)→(x0+run, z0−drop) 평면이 되도록
    중심·각도 계산. 각도=atan2(drop,run), 길이=hypot(run,drop)+양끝 여유(margin).
    반환: Cube 프림."""
    from pxr import UsdGeom, UsdPhysics, Gf
    ang = math.atan2(drop, run)                # +면 +X로 하강
    length = math.hypot(run, drop) + margin
    # 상면 중점 (x0,z0)→(x0+run,z0-drop) 의 중앙
    sx = x0 + run / 2.0
    sz = z0 - drop / 2.0
    # 로컬 -Z(두께 방향)의 월드 매핑: rotateY(+ang) → (-sin, 0, -cos)
    cx = sx - (thick / 2.0) * math.sin(ang)
    cz = sz - (thick / 2.0) * math.cos(ang)
    cy = (y0 + y1) / 2.0
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(2.0)
    cube.CreateExtentAttr([Gf.Vec3f(-1, -1, -1), Gf.Vec3f(1, 1, 1)])
    xf = UsdGeom.Xformable(cube)
    xf.AddTranslateOp().Set(Gf.Vec3d(float(cx), float(cy), float(cz)))
    xf.AddRotateYOp().Set(math.degrees(ang))   # +X 끝이 아래로
    xf.AddScaleOp().Set(Gf.Vec3f(float(length) / 2.0,
                                 float(abs(y1 - y0)) / 2.0,
                                 float(thick) / 2.0))
    prim = cube.GetPrim()
    _bind_mtl(prim, mtl)
    if collider:
        UsdPhysics.CollisionAPI.Apply(prim)
    return cube


# ===========================================================================
# [5c] 신규 계단 빌더 v3 (나선·마모석·회전그룹·개방라이저·캐노피)
#      수학 정의: Docs/stair_typology_survey_v2.md §3 / brief v3 §B
# ===========================================================================
def build_helix_steps(stage, prefix, cx, cy, r_in, r_out, a0_deg, step_deg, n,
                      riser, z0, mtl, ccw=True, collider=True, base_drop=0.5):
    """나선/헬리컬 석계단(T9/winder 공용). 단 i(0-based):
      중심각 a_i = a0_deg + (i+0.5)*step_deg*dir  (dir=+1 ccw, −1 cw)
      환형 섹터 박스: 반경폭 = r_out−r_in, 현길이 = 2*r_mid*sin(rad(step_deg)/2)*1.02
        (세그 간 쐐기 틈 방지 겹침 1.02 — build_arc_steps 재사용)
      상면 z = z0 − (i+1)*riser  (하강), 바닥 = 상면 − base_drop (솔리드).
    각 섹터는 translate→rotZ(a_i)→scale 로 배치(로컬 X=반경, Y=접선, Z=높이).
    반환: 생성 Cube 프림 리스트."""
    r_mid = (r_in + r_out) / 2.0
    radial = r_out - r_in
    half_rad = math.radians(step_deg) / 2.0
    chord = 2.0 * r_out * math.sin(half_rad) * 1.03    # 외경 기준 커버(룩 r1 수정)
    direction = 1.0 if ccw else -1.0
    prims = []
    for i in range(n):
        a_deg = a0_deg + (i + 0.5) * step_deg * direction
        rad = math.radians(a_deg)
        px = cx + r_mid * math.cos(rad)
        py = cy + r_mid * math.sin(rad)
        top = z0 - (i + 1) * riser
        cz = top - base_drop / 2.0
        prims.append(_oriented_box(
            stage, f"{prefix}/Step_{i}", (px, py, cz),
            (radial, chord, base_drop), mtl, collider=collider, rotz=a_deg))
    return prims


def build_helix_ramp(stage, prefix, cx, cy, r_in, r_out, a0_deg, a1_deg, seg,
                     z0, z1, thick, mtl, collider=True):
    """매끈한 나선 램프(T10 주차램프). 호 [a0,a1]를 seg개 현 세그로 근사.
      세그 j(0-based): 중심각 a_j = a0 + (j+0.5)*dth_deg
      z 선형보간: 세그 상면 중앙 z = z0 + (j+0.5)*dz_seg, dz_seg=(z1−z0)/seg
      세그 현길이 L_c = 2*r_mid*sin(dth/2)
      **로컬 접선축 경사**: 세그를 rotZ(a_j)로 방위 배치한 뒤, 현(=접선=로컬 Y)을
        따라 dz_seg 만큼 오르내리게 기울인다. 접선을 기울이는 회전축은 그에 수직인
        로컬 X(=반경축) → **rotX**(rotY 아님). 기울기각 = atan2(dz_seg, L_c).
        유도: rotX(θ): z' = y·sinθ + z·cosθ ⇒ ∂z'/∂y = sinθ. +Y(진행=현 앞쪽)에서
        높이변화율 dz_seg/L_c 를 만들려면 sinθ = dz_seg/L_c ⇒ θ=atan2(dz_seg,L_c).
        dz_seg<0(하강)이면 θ<0 → +Y 끝이 내려간다(옳음).
      op 순서 translate→rotZ→rotX→scale(=_oriented_box): 점 적용은 역순
        scale→rotX(로컬,방위 전)→rotZ(방위)→translate 이므로 접선경사가 정확히
        각 세그의 반경축을 중심으로 걸린다.
    반환: (프림 리스트, 세그 기울기각[deg] — 균일 세그이므로 단일 값 리스트)."""
    r_mid = (r_in + r_out) / 2.0
    radial = r_out - r_in
    dth_deg = (a1_deg - a0_deg) / float(seg)
    dth = math.radians(dth_deg)
    L_c = 2.0 * r_mid * math.sin(dth / 2.0)
    dz_seg = (z1 - z0) / float(seg)
    tilt_deg = math.degrees(math.atan2(dz_seg, L_c))
    # [감사 v4 I-3] 세그 폭은 r_out 기준 현길이 ×1.03 — r_mid 기준(×1.02)은 외경부
    #   에서 세그 간 관통 슬릿(scene13에서 0.21 m 실측). build_arc_steps 와 동일
    #   규약(교훈 4). 경사(tilt)는 진행 경로 기준이므로 r_mid 현길이 L_c 유지.
    seg_len = 2.0 * r_out * math.sin(dth / 2.0) * 1.03
    prims = []
    for j in range(seg):
        a_deg = a0_deg + (j + 0.5) * dth_deg
        rad = math.radians(a_deg)
        px = cx + r_mid * math.cos(rad)
        py = cy + r_mid * math.sin(rad)
        z_top = z0 + (j + 0.5) * dz_seg          # 세그 상면 중앙 높이
        cz = z_top - thick / 2.0
        prims.append(_oriented_box(
            stage, f"{prefix}/Seg_{j}", (px, py, cz),
            (radial, seg_len, thick), mtl, collider=collider,
            rotz=a_deg, rotx=tilt_deg))
    return prims, [tilt_deg]


def build_worn_stone_stairs(stage, prefix, x0, y0, y1, n, riser_mu, tread_mu,
                            blocks, seed, mtl, base_z, z_top=0.0, jr=0.03,
                            jt=0.10, jz=0.02, jyaw=3.0):
    """마모 부정형 석단(T16). numpy RandomState(seed) 고정 → 재현.
      단 i(0-based): riser_i = riser_mu + U(−jr,+jr), 상면 z 누적 하강,
        x 는 tread_mu 로 누적(xa_i..xb_i).
      각 단을 blocks개 가로 블록(공칭 폭 Wb=(y1−y0)/blocks, 이웃과 1mm 겹침)으로
        분할, 블록별 지터:
          상면 z += U(−jz,+jz),  앞/뒤 x 각 += U(−jt/2,+jt/2)(→ 단코 비직선),
          yaw = U(−jyaw,+jyaw)°(rotZ).  바닥은 솔리드로 base_z 까지.
    반환: (프림 리스트, 단별 평균 상면 z 리스트, 총 run[= n*tread_mu])."""
    rng = np.random.RandomState(int(seed))
    Wb = (y1 - y0) / float(blocks)
    prims = []
    mean_tops = []
    xa = float(x0)
    z_prev = float(z_top)
    for i in range(n):
        riser_i = riser_mu + float(rng.uniform(-jr, jr))
        top_i = z_prev - riser_i
        xb = xa + tread_mu
        block_tops = []
        for j in range(blocks):
            by0 = y0 + j * Wb - 0.0005            # 1mm 겹침(양측 0.5mm)
            by1 = y0 + (j + 1) * Wb + 0.0005
            bz = top_i + float(rng.uniform(-jz, jz))
            bxa = xa + float(rng.uniform(-jt / 2.0, jt / 2.0))
            bxb = xb + float(rng.uniform(-jt / 2.0, jt / 2.0))
            yaw = float(rng.uniform(-jyaw, jyaw))
            cx = (bxa + bxb) / 2.0
            cy = (by0 + by1) / 2.0
            cz = (bz + base_z) / 2.0
            prims.append(_oriented_box(
                stage, f"{prefix}/S{i}_B{j}", (cx, cy, cz),
                (bxb - bxa, by1 - by0, bz - base_z), mtl,
                collider=True, rotz=yaw))
            block_tops.append(bz)
        mean_tops.append(sum(block_tops) / len(block_tops))
        xa = xb
        z_prev = top_i
    run = n * tread_mu
    return prims, mean_tops, run


def build_rot_group(stage, path, pivot_xy, rot_deg):
    """피벗 회전 Xform 그룹. 하위 경로에 기존 빌더를 배치하면 그 전체가
    pivot_xy(월드 XY) 기준 rot_deg(도, +Z) 회전된다.
      xformOps = [translate(+pivot), rotateZ, translate(−pivot)]  (op suffix로
      두 translate 이름 충돌 회피). USD row-vector 규약상 점 적용은 리스트 역순:
      (−pivot)→rotZ→(+pivot) = '피벗을 원점으로 → 회전 → 되돌림' = 정확한 피벗회전.
    반환: Xform path(str) — 이후 f"{path}/..." 하위에 계단·드레싱 배치."""
    from pxr import UsdGeom, Gf
    xform = UsdGeom.Xform.Define(stage, path)
    xf = UsdGeom.Xformable(xform)
    px, py = float(pivot_xy[0]), float(pivot_xy[1])
    xf.AddTranslateOp(opSuffix="pivot").Set(Gf.Vec3d(px, py, 0.0))
    xf.AddRotateZOp().Set(float(rot_deg))
    xf.AddTranslateOp(opSuffix="unpivot").Set(Gf.Vec3d(-px, -py, 0.0))
    return path


def build_open_riser_stairs(stage, prefix, x0, y0, y1, riser, tread, n, z_top,
                            mtl_tread, mtl_stringer, tread_t=0.04, gap=0.025,
                            slits=0):
    """개방 라이저 계단(T11/T19 비상·그레이팅). 라이저 없음 — 아래 투시.
      스트링거 2본: 단면 0.06(Y폭)×0.25(두께) 경사 박스(build_slope 재사용),
        위치 y0+0.03 / y1−0.03, 상단 (x0,z_top)에서 run=n*tread·drop=n*riser 하강.
      디딤판: 각 단 상면(z=z_top−i*riser)에 두께 tread_t 판, 전후 gap 만큼 안쪽.
      slits>0: 판을 (slits+1)개 세로(y) 조각으로 분할, 조각 사이 0.02 틈(그레이팅).
    반환: 생성 프림 리스트."""
    run = n * tread
    drop = n * riser
    prims = []
    # 스트링거 2본 (경사 박스 — build_slope: y0,y1=Y폭 0.06, thick=0.25 깊이)
    for tag, yc in (("L", y0 + 0.03), ("R", y1 - 0.03)):
        prims.append(build_slope(
            stage, f"{prefix}/Stringer_{tag}", x0, z_top, run, drop,
            yc - 0.03, yc + 0.03, 0.25, mtl_stringer, margin=0.0,
            collider=True))
    Ly = y1 - y0
    for i in range(1, n + 1):
        xa = x0 + (i - 1) * tread
        xb = x0 + i * tread
        px = (xa + xb) / 2.0
        plen = (xb - xa) - 2.0 * gap             # 전후 gap 안쪽
        ztop = z_top - i * riser
        cz = ztop - tread_t / 2.0
        if slits > 0:
            nseg = slits + 1
            strip_w = (Ly - slits * 0.02) / nseg
            for s in range(nseg):
                sy0 = y0 + s * (strip_w + 0.02)
                syc = sy0 + strip_w / 2.0
                prims.append(add_box(
                    stage, f"{prefix}/Tread_{i}_{s}", (px, syc, cz),
                    (plen, strip_w, tread_t), mtl_tread, collider=True))
        else:
            prims.append(add_box(
                stage, f"{prefix}/Tread_{i}", (px, (y0 + y1) / 2.0, cz),
                (plen, Ly, tread_t), mtl_tread, collider=True))
    return prims


def build_canopy(stage, prefix, x0, x1, y0, y1, z_roof, post_r, mtl_roof,
                 mtl_post, roof_t=0.12, base_z=0.0):
    """캐노피(T20): 지붕판 1 + 모서리 기둥 4. 지붕은 z_roof(밑면)에서 roof_t 두께.
    기둥은 base_z(기본 지면 0)에서 z_roof 까지, 네 모서리(반경만큼 안쪽).
    반환: 생성 프림 리스트."""
    prims = []
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    prims.append(add_box(stage, f"{prefix}/Roof", (cx, cy, z_roof + roof_t / 2.0),
                         (x1 - x0, y1 - y0, roof_t), mtl_roof, collider=True))
    ph = z_roof - base_z
    corners = ((x0 + post_r, y0 + post_r, "SW"), (x0 + post_r, y1 - post_r, "NW"),
               (x1 - post_r, y0 + post_r, "SE"), (x1 - post_r, y1 - post_r, "NE"))
    for pxp, pyp, tag in corners:
        prims.append(add_cylinder(
            stage, f"{prefix}/Post_{tag}", (pxp, pyp, base_z + ph / 2.0),
            post_r, ph, mtl_post, collider=True))
    return prims


# ===========================================================================
# [5b] 씬 드레싱 빌더 (scene01 이식 — M 딕셔너리 대신 mtl 인자화)
# ===========================================================================
TACTILE_TILE_M = 0.30        # one statutory pad = 0.30 x 0.30 m (36 dots, 6x6)
TACTILE_RGB = (0.85, 0.72, 0.10)     # fallback constant only — see below


def tactile_pbr(stage, path, scale_m=None, roughness=0.70):
    """Canonical tactile-paving material — `tactile_yellow` texture, not flat colour.

    ground_kit §12.5-3 traced "batch1 tactile pads render at 0.003 % of frame"
    partly to this: the pads were authored as a CONSTANT colour, so the 36
    statutory dots produce no shading whatsoever. `TEX["tactile"]` has held
    `tactile_yellow_diff/nor` all along and simply was never bound at 8 of the
    call sites. The role key and the file names stay `tactile` /
    `tactile_yellow_*` — ground_kit and the vegetation agent address them by
    that exact name.
      texture [measured — assets/veg_manifest_w2.json]: 1024 px, 36 dots (6x6),
      pitch 50.0 mm, linear albedo 0.4841 (below the 0.55 clamp of §12.5-4).
    Falls back to the constant colour when the texture is absent, because
    `assets/scene01/*` is git-ignored and a missing binding renders black —
    strictly worse than the flat yellow it replaces.
    """
    sm = float(TACTILE_TILE_M if scale_m is None else scale_m)
    diff = os.path.join(TEX["tactile"]["dir"], TEX["tactile"]["diff"])
    nor = os.path.join(TEX["tactile"]["dir"], TEX["tactile"]["nor"])
    if os.path.isfile(diff):
        return make_pbr(stage, path, diff,
                        nor if os.path.isfile(nor) else None, None, sm,
                        metallic=0.0, roughness_const=roughness)
    print("[점자블록][경고] tactile_yellow 텍스처 부재 — 상수색 폴백(돌기 음영 0). "
          "assets/scene01/download_scene01_assets.py 실행 필요")
    return make_pbr(stage, path, diffuse_color=TACTILE_RGB,
                    metallic=0.0, roughness_const=roughness)


def build_tactile(stage, path, x0, x1, y0, y1, mtl, z=0.0, proud=0.004):
    """점형 점자블록 띠(황색). x0..x1 × y0..y1 사각 밴드. 상면 z에서 proud 돌출,
    돌기는 노멀맵으로 표현(거의 플러시). 반환: Cube 프림."""
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    z_top = z + proud
    z_bot = z - 0.01
    return add_box(stage, path, (cx, cy, (z_top + z_bot) / 2.0),
                   (abs(x1 - x0), abs(y1 - y0), z_top - z_bot), mtl)


# ===========================================================================
# [5b] 실제 식생 에셋 (NVIDIA S3, `assets/vegetation/`)
#
# **왜 필요한가**: 종전 `build_tree` 는 실린더 줄기 + 구(sphere) 블롭 수관이라
# 아무리 텍스처를 입혀도 "솜사탕"으로 읽혔다. 사실화 조사가 지목한
# "표현 원자가 Cube/Cylinder/Sphere 3종뿐" 의 가장 눈에 띄는 사례다.
# 재질 계층만 손대는 것으로는 이 문제를 못 고친다 — **기하를 바꿔야 한다.**
#
# 함정 (조달 조사 실측):
#   · 에셋 `metersPerUnit = 0.01`(cm). USD reference 는 **단위 변환을 하지 않는다**
#     → 스케일 안 걸면 벚나무가 464 m 로 들어온다.
#   · 참조가 상대 경로라 S3 디렉터리 구조(`Trees/`·`Shrub/`)를 그대로 유지해야 한다.
#   · 이 4종은 잎이 **실제 모델링 지오메트리**이고 알파 채널이 없다 →
#     `enable_opacity` 를 켜면 오히려 망가진다(ZZ §10.2 적용 범위 정정).
# ===========================================================================
VEG_DIR = os.path.join(ASSETS_DIR, "vegetation")

# (상대경로, **지상 노출 높이**[m], 가중치) — 서울 가로수 통계 반영. `[W2 재편]`
#
# **`Japanese_Cherry` 삭제(가중치 재분배가 아니라 삭제)** — A 감사 P0-1.
#   ① 계절 규약: 잎 텍스처 **초록 화소 0.0 %**(만개 벚꽃 픽셀). 수종명이 아니라
#      픽셀로 판정한 결과다 [실측 — `A_trees_shrubs.md` §9].
#   ② 빈도: 서울 가로수 벚나무는 4위권 ≈7 % 인데 가중치가 **62.5 %** 였다 —
#      서울 실태 대비 약 9배, 전국(18.6 %) 기준으로도 3.4배 과대 [통계 — 동 §5].
#
# 새 조합의 근거: 서울 2019(306,313주) 1·2위는 **은행 35.8 % · 양버즘 20.9 %** 인데
# 둘 다 조달 불가다(은행 = S3 부재 확정 / 양버즘 = 잎 텍스처가 갈색 낙엽이라
# 초록화 파생본 선행 필요). ⇒ **근연 대용종으로 활엽 우세 구성을 만든다**:
#   Elm_Sapling(느릅나무과 = 느티나무 대용) · Shumard_Oak(참나무류 = 대왕참나무 대용)
#   = 활엽 63.6 %, 침엽·상록 36.4 %. 현행 소나무류 37.5 % → **18.2 %** 로 하향.
#   `[추정 — 가중치 배분]` 통계는 수종별 비율까지만 주고 대용종 매핑 비율은 주지 않는다.
#
# **높이는 `zmax`(지상 노출)를 쓴다 — 바운딩 전체 높이가 아니다.**
#   `add_vegetation` 은 `s = target_h / native_h` 로 스케일하는데 `zmin < 0` 인 에셋에
#   전체 높이를 넣으면 지상 노출이 그만큼 짧아진다(White_Pine 이 −15 % 로 겪던 결함,
#   A §6-c). 신규 3종은 처음부터 `zmax` 로 넣어 같은 결함을 반복하지 않는다.
VEG_TREES = [
    # 상대경로                       native_h  w   비고
    ("Trees/Elm_Sapling.usd",         3.0867, 4),  # 느릅나무 묘목 — 느티/이팝 대용, 근경 3 m
    ("Trees/Shumard_Oak.usd",        10.8989, 3),  # 참나무류 — 대왕참나무 대용, 중·원경
    ("Trees/Chinese_Juniper.usd",     2.5164, 2),  # 향나무 — 사찰·관공서·학교 조경 최다
    ("Trees/White_Pine.usd",          2.35,   1),  # 소나무류(소형) — zmin −0.351 미보정 [기지 결함 A §6-c]
    ("Trees/Yellow_Pine.usd",        26.99,   1),  # 소나무류(대형) — 원경·배후림용
]
# [실측 — `assets/veg_manifest_w2.json`(2026-07-29, usd-core 26.8 · UV 픽셀 판정)]
#   Elm_Sapling     zmax 3.0867 · 113,268 tri · 잎 beech_leaf 초록 99.2 % · PASS
#   Shumard_Oak     zmax 10.8989 · 99,509 tri · oakleaves 1~4 초록/올리브 100 % · PASS
#   Chinese_Juniper zmax 2.5164 · 27,098 tri · pine_needles 초록 80.2 %+황록 19.8 % · PASS
VEG_SHRUB = [("Shrub/Boxwood.usd", 0.74, 1)]  # 회양목


def veg_pool():
    """실제로 디스크에 있는 수종만 남긴 가중 풀.

    `Japanese_Cherry` 삭제로 1행이 바뀌었으므로 "첫 행 존재"로 가용성을 판정하면
    조달 상태에 따라 **30개 씬의 식생이 통째로 사라진다.** 존재하는 것만 쓴다.
    """
    return [t for t in VEG_TREES
            if os.path.isfile(os.path.join(VEG_DIR, t[0]))]


def veg_available():
    """식생 에셋이 실제로 있는지. 없으면 절차 블롭으로 폴백한다."""
    return bool(veg_pool())


def _deactivate_seasonal(stage, asset_path, usd_rel):
    """Turn off season-specific sub-prims of a referenced vegetation asset.

    The season convention is judged on leaf/flower TEXTURE PIXELS, not on the
    species name. `Rhododendron` is a full-bloom scan (76.7 % of the basecolor
    is magenta), so the shrub itself is season-neutral only once `/Root/Flowers`
    is deactivated. Deactivation removes the prim from composition, so the
    flower geometry is never drawn and costs nothing.
    Silent no-op when the asset has no registered seasonal prims.
    """
    names = SEASONAL_SUBPRIMS.get(usd_rel)
    if not names:
        return 0
    off = 0
    for nm in names:
        try:
            p = stage.GetPrimAtPath(f"{asset_path}/{nm}")
            if p and p.IsValid():
                p.SetActive(False)
                off += 1
        except Exception as e:                 # never let this kill the scene
            print(f"[룩v1][경고] 계절 프림 비활성 실패 {asset_path}/{nm}: {e}")
    if off:
        LOOK_STATS["seasonal_off"] = LOOK_STATS.get("seasonal_off", 0) + off
    return off


def add_vegetation(stage, prim_path, usd_rel, pos_m, yaw_deg=0.0,
                   target_h=None, native_h=None, tilt_deg=(0.0, 0.0),
                   scale_mul=1.0):
    """식생 USD 를 reference 로 붙인다. cm→m 단위 변환 자동.

    target_h 지정 시 그 높이가 되도록 스케일한다 — 씬이 `trunk_h` 로 의도한
    수고(樹高)를 유지해야 그림자·차폐 구성이 안 깨진다.
    """
    from pxr import Usd, UsdGeom, Gf
    asset = os.path.join(VEG_DIR, usd_rel)
    if not os.path.isfile(asset):
        return None
    unit = 0.01                                # 에셋 metersPerUnit (실측)
    try:
        src = Usd.Stage.Open(asset)
        unit = (UsdGeom.GetStageMetersPerUnit(src)
                / UsdGeom.GetStageMetersPerUnit(stage))
    except Exception:
        pass
    # 참조는 **자식**에 붙인다. Debris 계열 USD 는 루트에 자체 xformOp
    # (translate/rotateXYZ/scale)를 갖고 있어서, 참조를 붙인 프림에 다시
    # AddTranslateOp 하면 "already exists in xformOpOrder" 로 죽는다.
    # (Trees 계열은 루트 op 이 없어 우연히 통과했을 뿐이다.)
    xf = UsdGeom.Xform.Define(stage, prim_path)
    UsdGeom.Xform.Define(stage, prim_path + "/Asset") \
        .GetPrim().GetReferences().AddReference(asset)
    xf.AddTranslateOp().Set(Gf.Vec3d(*[float(v) for v in pos_m]))
    xf.AddRotateZOp().Set(float(yaw_deg))      # 순서 중요: T → R → S
    # 경사면 추종·개체 기울기. 낙엽·잡석은 이게 없으면 비탈에서 공중에 뜬 채
    # 수평으로 눕는다 — 산포물에는 yaw 만으로 부족하다.
    tx, ty = (float(tilt_deg[0]), float(tilt_deg[1])) if tilt_deg else (0.0, 0.0)
    if abs(tx) > 1e-6:
        xf.AddRotateXOp().Set(tx)
    if abs(ty) > 1e-6:
        xf.AddRotateYOp().Set(ty)
    s = unit * ((float(target_h) / float(native_h))
                if (target_h and native_h) else 1.0) * float(scale_mul)
    xf.AddScaleOp().Set(Gf.Vec3f(s, s, s))
    return xf



# --- 3D 산포물 (낙엽·자갈·잔해·바위) ---------------------------------------
# **왜 필요한가**: 낙엽·자갈·잔해를 평면에 텍스처로 깔면 "장판 깐 것"으로 읽힌다.
# 사용자 지적: *"낙엽도 장판 깐 것처럼 만드는거에서 탈피시켜주고"*
# 아스팔트·콘크리트는 평면이 옳지만, **입체물을 평면으로 때운 것**은 3D 여야 한다.
# S3 `Assets/Vegetation/` 에 Debris 26 · Leaves 16 · Rocks 75 종이 있다.
# (상대경로, 1개가 덮는 유효 면적[m²], 삼각형 수)
#   유효면적은 추정이 아니라 **삼각형을 XY 로 투영해 래스터화한 실측**이다.
#   sceneC2 의 기존 낙엽은 두께 6mm 납작 타원체 900개였는데 총 피복이
#   **0.96 m² 뿐**이라, 화면에 보이는 낙엽은 사실상 전부 텍스처 무늬였다.
#   → "장판" 의 정확한 원인. 피복을 개수가 아니라 면적으로 다뤄야 하는 이유.
#   [정정 2026-07-29 · 레드팀 R8 → W1 재판정] `oakfall2` 는 (0.0030/520) →
#   (0.0038/582) 로 1차 정정했으나, W1 지피 감사가 usd-core 독립 재래스터화로
#   피복을 **0.0054 m²** 로 확정했다(래스터라이저 해석 검증·N 불변·실루엣 육안,
#   `Docs/surveys/props_audit_w1/B_groundcover_debris.md` §6, redteam_w1_assets 승소 판정).
#   **렌더 영향 0** — 유일한 호출부 `sceneC2_leaf_stairs.py:563` 이 `fallcluster` 만
#   필터해 넘기므로 이 행은 산포 개수식 `n = A·(−ln(1−cover))/mean_cov` 에 안 들어간다.
#   ⚠ 낱장 maplefall1(실측 0.0081)·oakfall1(0.0048)·클러스터 2행(0.0584/0.0239)도
#   계통 편차가 확인됐다 — sceneC2 개수식에 걸리는 fallcluster 행은 **렌더 영향이
#   있으므로** W2 낙엽 전역화(G2)에서 렌더 게이트와 함께 일괄 교체한다(B 감사 A3).
# [W2 · B감사 A3 — **5행 전면 교체**] 유효피복을 B조 독립 재래스터화 값으로 통일한다.
#   구값의 출처(`asset_audit_v1.md`)는 계산 코드가 저장소에 없어 원인 규명이 불가하고,
#   B조 값은 ① 래스터라이저 해석 검증(단위정사각 1.0000 / 원 0.7840 vs 이론 0.7854)
#   ② N=256~2048 결과 불변 ③ 실루엣 PNG 육안 확인을 거쳤다 [실측 — B §6·§12 A3].
#   삼각형 수는 5행 전부 이미 일치했다(정정 대상 아님).
#   변화폭: 낱장 3종이 **40~60 % 과소평가**(maplefall1 +59 % · oakfall1 +60 %),
#   클러스터 2종은 소폭 과대(−7.0 % · −1.2 %).
#   ⇒ `scatter_debris` 의 `mean_cov` 가 바뀌므로 **산포 개수가 바뀐다**(재질 A/B 밖의
#     before/after 항목 — 양팔에 동일하게 걸린다).
VEG_DEBRIS = [
    ("Debris/fallcluster1.usd", 0.0584, 9175),
    ("Debris/fallcluster2.usd", 0.0239, 2980),
    ("Debris/maplefall1.usd",   0.0081,  631),
    ("Debris/oakfall1.usd",     0.0048,  496),
    ("Debris/oakfall2.usd",     0.0054,  582),
]

# (상대경로, 대표 폭[m], **원점에서 바닥까지 깊이[m]**)
#   Rocks 는 원점이 바위 *중심* 이라 지면 z 에 그대로 놓으면 절반이 묻힌다.
#   z_min 만큼 띄워야 앉고, 일부러 묻을 때는 그만큼 덜 띄운다.
# (상대경로, 네이티브 폭[m], 원점→바닥 깊이[m], 삼각형 수, **네이티브 높이[m]**)
#   한국 조경 실사종. Privet(쥐똥나무)=생울타리 표준종, Rhododendron(철쭉)·
#   Juniper(향나무류)=화단 관목.
#   **삼각형이 비싸다**(5.5만~40만/주) — 근경에만 쓰고 원경은 블롭을 유지한다.
#
# [W2 · A감사 6-b] **5번째 필드(네이티브 높이) 신설.** `place_shrubs` 가 높이 스케일을
#   **폭 기준**으로 계산하고 있었는데, 실측 종횡비(높이/폭)가 **0.607~1.973 로 3.2배**
#   흩어져 있어 `target_h=0.85` 요청 시 실제 수고가 **−39 %~+97 %** 로 어긋났다
#   (Boxwood 0.62 m 와 Juniper 1.68 m 가 같은 화단에 선다) [실측 — A §6-b].
#   같은 함수 docstring 이 "관목 높이는 스케일 앵커라 랜덤화는 ±8 %" 라고 못박아 놓고
#   결정론적으로 그 12배 오차를 넣고 있었다 — **단서 축을 지우는 결함**이다.
VEG_SHRUBS = [
    # 상대경로                    폭     zmin    삼각형   높이[실측 A §6-b]
    ("Shrub/Privet.usd",        1.704, 0.067, 147000, 1.114),
    ("Shrub/Boxwood.usd",       1.009, 0.019, 178000, 0.741),
    ("Shrub/Juniper.usd",       0.455, 0.013, 200000, 0.898),
    ("Shrub/Rhododendron.usd",  2.547, 0.416,  55000, 2.013),
    ("Shrub/Burning_Bush.usd",  2.642, 0.193, 141000, 1.604),
    ("Shrub/Forsythia.usd",     3.539, 0.007, 404000, 2.317),
]
# 다듬은 생울타리는 실제로 상자 형태가 맞다(전정). 블롭이 틀린 것은
# **화단의 다듬지 않은 관목**이다 — 거기를 실물로 바꾼다.
SHRUB_HEDGE = ["Shrub/Privet.usd", "Shrub/Boxwood.usd"]
# [W2 · A감사 P0-2] `Forsythia`(개나리)·`Burning_Bush`(화살나무) **제거**.
#   계절 규약은 수종명이 아니라 잎 텍스처 픽셀로 판정한다 [실측 — B §9]:
#     · `forsythiaflower_basecolor.png` — 개화 전용 텍스처(초록 0.0 %). 개화기 3~4월.
#     · `burningbush_leaf_basecolor.png` — **적색 30.2 %**(가을 단풍). C2 에는 맞아도
#       여름·상시 씬에는 금지 대상이라 전역 풀에서 뺀다.
#   `Rhododendron`(철쭉)은 **꽃 프림 비활성화를 전제로만** 잔류한다 —
#   `rhododendron_basecolor.png` 픽셀의 **76.7 % 가 마젠타**(만개 스캔)라 그대로 두면
#   봄 개화가 전 씬에 박힌다. `place_shrubs` 가 `/Asset/Flowers` 를 끈다(아래).
SHRUB_ORNAMENT = ["Shrub/Rhododendron.usd", "Shrub/Juniper.usd"]

# 계절 특정 프림 — 참조 직후 `SetActive(False)` 로 끈다. 에셋 루트(`/Root`)가
# 참조 대상 프림으로 매핑되므로 `/Root/Flowers` 는 `{prim}/Asset/Flowers` 가 된다.
# [실측 — `strings assets/vegetation/Shrub/Rhododendron.usd` = Branches·Flowers·Leaves]
SEASONAL_SUBPRIMS = {
    "Shrub/Rhododendron.usd": ("Flowers",),
}

VEG_ROCKS = [
    ("Rocks/rock_small_01.usda", 0.314, 0.128),
    ("Rocks/rock_small_08.usda", 0.196, 0.072),
    ("Rocks/rock_small_09.usda", 0.164, 0.061),
    ("Rocks/rock_small_10.usda", 0.128, 0.044),
    ("Rocks/rock_small_15.usda", 0.238, 0.031),
]


def scatter_debris(stage, prefix, x0, y0, x1, y1, z, cover=0.35,
                   pool=None, seed=1234, scale_jitter=(0.75, 1.25),
                   edge_bias=0.0, max_count=400, ground_fn=None,
                   tilt_max=8.0, sink=0.0):
    """[사실화 v1] 영역에 3D 산포물을 뿌린다 — 낙엽·잔해·자갈·바위.

    cover: **목표 지면 피복률 0~1** (개수가 아니다). 무작위 산포는 겹치므로
      필요 개수는 n = A·(−ln(1−cover)) / (개당 유효면적) 으로 역산한다
      (겹침을 무시하고 면적을 그냥 나누면 실제 피복이 목표보다 낮게 나온다).
      개당 유효면적은 VEG_DEBRIS 에 실측해 넣어 두었다.
    edge_bias: >0 이면 가장자리·구석으로 몰아준다[m]. 실제 낙엽은 바람에
      쓸려 구석에 쌓이고 통행 동선은 비는데, 균일 산포는 그 반대라 오히려
      부자연스럽다. 0 이면 균일.
    ground_fn: (x,y)→z 콜백. 주면 각 개체를 지면에 앉히고 국소 기울기를
      따라 눕힌다 — 없으면 비탈에서 공중에 뜬 채 수평으로 눕는다.
    sink: 지면 아래로 내릴 깊이[m]. 바위 반매입용.
    seed 는 **반드시 결정적**이어야 한다 — 이 프로젝트는 RNG 100% 결정적이 원칙.

    반환: 배치한 개수.
    """
    pool = pool or VEG_DEBRIS
    avail = [p for p in pool
             if os.path.isfile(os.path.join(VEG_DIR, p[0]))]
    if not avail:
        return 0
    rng = np.random.default_rng(int(seed) & 0x7FFFFFFF)
    w, h = abs(x1 - x0), abs(y1 - y0)
    area = w * h
    cover = max(0.0, min(0.97, float(cover)))
    mean_cov = sum(float(p[1]) for p in avail) / len(avail)
    if area <= 0 or mean_cov <= 0 or cover <= 0:
        return 0
    n = int(round(area * (-math.log(1.0 - cover)) / mean_cov))
    if n > max_count:
        print(f"[룩v1] 산포 상한: {prefix} 목표피복 {cover:.2f} → {n}개 필요, "
              f"{max_count}개로 자름(실제 피복 "
              f"{1.0 - math.exp(-max_count * mean_cov / area):.2f})")
        n = max_count
    if n <= 0:
        return 0
    xa, ya = min(x0, x1), min(y0, y1)
    placed = 0
    for i in range(n):
        px = xa + rng.random() * w
        py = ya + rng.random() * h
        if edge_bias > 1e-6:
            dx = min(px - xa, xa + w - px)
            dy = min(py - ya, ya + h - py)
            if min(dx, dy) > edge_bias and rng.random() > 0.35:
                continue                    # 안쪽은 65% 확률로 건너뛴다
        rel, _cov = avail[int(rng.integers(len(avail)))][:2]
        pz = float(z)
        tilt = (0.0, 0.0)
        if ground_fn is not None:
            try:
                # d 는 **디딤면(0.24~0.34m)보다 작아야** 한다. 종전 0.15 는
                # 반폭이 tread 의 절반에 육박해, 수평 디딤면 위 낙엽 89.5% 가
                # 인접 단의 z 를 물고 평균 28° 기울어 6.6cm 뜨거나 파묻혔다.
                d = 0.04
                pz = float(ground_fn(px, py))
                # 국소 기울기 → 개체를 비탈에 눕힌다
                gx = (float(ground_fn(px + d, py)) - float(ground_fn(px - d, py))) / (2 * d)
                gy = (float(ground_fn(px, py + d)) - float(ground_fn(px, py - d))) / (2 * d)
                # 불연속면(계단코·연석)에서 기울기가 폭발하므로 클램프한다.
                _cl = lambda a: max(-15.0, min(15.0, math.degrees(math.atan(a))))
                tilt = (_cl(gy), -_cl(gx))
            except Exception:
                pass
        j = float(rng.uniform(-tilt_max, tilt_max))
        tilt = (tilt[0] + j, tilt[1] + float(rng.uniform(-tilt_max, tilt_max)))
        try:
            if add_vegetation(stage, f"{prefix}/Deb_{i}", rel,
                              (px, py, pz - float(sink)),
                              yaw_deg=float(rng.uniform(0, 360)),
                              tilt_deg=tilt,
                              scale_mul=float(rng.uniform(*scale_jitter))) is not None:
                # 산포물은 개수가 많아 인스턴싱이 필수 — 프로토타입 공유.
                try:
                    stage.GetPrimAtPath(f"{prefix}/Deb_{i}/Asset").SetInstanceable(True)
                except Exception:
                    pass
                placed += 1
        except Exception as e:
            print(f"[룩v1][경고] 산포물 배치 실패 {prefix}/Deb_{i}: {e}")
            break
    if placed:
        LOOK_STATS["debris"] = LOOK_STATS.get("debris", 0) + placed
    return placed


def build_tree(stage, prefix, cx, cy, gz, wood_mtl, canopy_a_mtl, canopy_b_mtl,
               trunk_r=0.09, trunk_h=2.2, stake_r=0.015, stake_h=1.5,
               stake_off=0.5, stakes=False, canopy_blobs=10,
               canopy_spread=1.0):
    """[v5.1 현실성] 줄기(2단 테이퍼+미세 기울기) + 수관(불규칙 타원 블롭,
    나무별 결정적 변형) + 지지대 3본(기본 OFF). 좌표 해시 시드 → 같은 씬
    재실행 시 동일, 나무마다 수형·크기·기울기가 달라 '막대사탕 복제' 인상 제거.

    [v6 판정 C-4] 원경에서 '가는 줄기 + 구형 수관'(롤리팝)으로 뭉치는 문제 →
    위성 블롭 7 → `canopy_blobs`(기본 10), 산포 반경·연직 분포 상향으로
    실루엣을 깨뜨린다. `canopy_spread` 로 씬별 미세조정(1.0 = 기본).
    [mod6 §1(c)] `trunk_r` 기본 0.06 → 0.09(지름 18 cm) — 과세 줄기 보정.
    (명시 지정 호출은 영향 없음.)
    [사실화 v1] `NEGOBS_LOOK_GEO=1` 이고 식생 에셋이 있으면 **실제 나무 USD**로
    교체된다(프림 집합이 바뀌므로 기하 소속). 시그니처가 같아 30개 씬이
    수정 없이 그대로 바뀐다. 에셋이 없으면 아래 절차 블롭으로 폴백한다(회귀 0).

    반환: None(프림은 prefix 하위에 생성)."""
    import random as _random
    rnd = _random.Random((int(round(cx * 100)) * 73856093)
                         ^ (int(round(cy * 100)) * 19349663))

    if LOOK_GEO and veg_available():
        # 수종은 좌표 해시로 결정 — 같은 씬 재실행 시 동일하고, 나무마다 다르다.
        pool = [t for t in veg_pool() for _ in range(t[2])]
        rel, native, _ = pool[rnd.randrange(len(pool))]
        # **수고는 단서다.** 단서 4계열 ③(스케일 앵커)이 "수관 꼭대기 절대높이"를
        # 쓰므로, 이걸 큰 폭으로 랜덤화하면 정작 학습해야 할 축을 지운다.
        # 종전 uniform(1.45,1.85) 는 근거 없는 매직넘버였다(레드팀 지적 — 수용).
        # → 고정 비율 1.60(줄기높이 대비 전체 수고)에 ±8% 개체차만 준다.
        target = float(trunk_h) * 1.60 * rnd.uniform(0.92, 1.08)
        try:
            # **자식 경로에 붙인다.** prefix 자신에 붙이면 `build_planter` 처럼
            # 같은 prefix 아래에 이미 만들어 둔 형제 프림(Curb/Cap/Grass)에
            # 스케일(약 0.0078)이 함께 걸려 **화단이 0.8% 크기로 수축**한다.
            # 12개 씬이 이 경로를 탄다(레드팀 적발 — 감독 버그).
            vx = add_vegetation(stage, f"{prefix}/Veg", rel, (cx, cy, gz),
                                yaw_deg=rnd.uniform(0, 360),
                                target_h=target, native_h=native)
            if vx is not None:
                # 같은 에셋을 여러 번 참조하므로 인스턴싱으로 메모리·시간 절약.
                # (33씬 합계 약 30 M 삼각형 추가 — 레드팀 추산)
                # 인스턴싱은 **참조가 붙은 프림**에 걸어야 한다. USD 는
                # "a prim must use at least one composition arc in order to be
                # eligible for instancing" 이므로, 참조를 /Asset 자식으로 내린
                # 뒤에도 부모에 걸어 두면 **조용히 무동작**이다.
                # (직전 커밋의 인스턴싱 조치가 다음 커밋에서 이렇게 무력화됐고,
                #  육안으로는 원리적으로 확인할 수 없는 종류의 회귀다.)
                try:
                    stage.GetPrimAtPath(f"{prefix}/Veg/Asset") \
                        .SetInstanceable(True)
                except Exception:
                    pass
                LOOK_STATS["veg_asset"] = LOOK_STATS.get("veg_asset", 0) + 1
                return
        except Exception as e:
            print(f"[룩v1][경고] 식생 에셋 배치 실패 {prefix}: {e} — 블롭 폴백")
    th = trunk_h * rnd.uniform(0.85, 1.25)
    lean_a = rnd.uniform(0.0, 2 * math.pi)
    lean = rnd.uniform(0.0, 4.0)               # 기울기(도)
    lx, ly = math.cos(lean_a), math.sin(lean_a)
    # 줄기 2단(테이퍼): 하단 r → 상단 0.7r, 상단은 기울기 방향으로 오프셋
    off = th * math.sin(math.radians(lean))
    # [v6 판정] 부호 수정: 상단 오프셋(+lx)과 정합하는 회전은 rotY=+lean*lx,
    #   rotX=-lean*ly (구 부호는 어긋남 가산 → 줄기 두 동강 렌더)
    add_cylinder(stage, f"{prefix}/Trunk", (cx, cy, gz + th * 0.35),
                 trunk_r, th * 0.7, wood_mtl,
                 rotX=-lean * ly, rotY=lean * lx)
    add_cylinder(stage, f"{prefix}/TrunkUp",
                 (cx + lx * off * 0.5, cy + ly * off * 0.5, gz + th * 0.78),
                 trunk_r * 0.7, th * 0.55, wood_mtl,
                 rotX=-lean * ly, rotY=lean * lx)
    # 수관: 중심 대형 1 + 위성 블롭 canopy_blobs (반경·위치·납작률 랜덤, 2색 랜덤)
    cs = rnd.uniform(0.85, 1.25)               # 수관 전체 스케일
    sp = float(canopy_spread)
    ccx, ccy = cx + lx * off, cy + ly * off
    czb = gz + th
    # 중심 블롭도 축비를 지터(구형 실루엣 회피)
    add_sphere(stage, f"{prefix}/Canopy_0",
               (ccx, ccy, czb + 0.35 * cs),
               (0.74 * cs * sp * rnd.uniform(0.92, 1.08),
                0.74 * cs * sp * rnd.uniform(0.92, 1.08),
                0.58 * cs * rnd.uniform(0.92, 1.10)),
               canopy_a_mtl if rnd.random() < 0.5 else canopy_b_mtl)
    for i in range(int(canopy_blobs)):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0.18, 0.68) * cs * sp   # 산포 반경 상향(구 0.15~0.55)
        dz = rnd.uniform(-0.05, 0.95) * cs      # 연직 분포 확대(구 0.05~0.85)
        r = rnd.uniform(0.30, 0.58) * cs * sp   # 블롭 반경 상향(구 0.30~0.55)
        mtl = canopy_a_mtl if rnd.random() < 0.5 else canopy_b_mtl
        add_sphere(stage, f"{prefix}/Canopy_{i + 1}",
                   (ccx + d * math.cos(a), ccy + d * math.sin(a), czb + dz),
                   (r, r * rnd.uniform(0.80, 1.0), r * rnd.uniform(0.65, 0.85)),
                   mtl)
    # 지지대 3본 — [v6 판정] 기본 OFF("삼각대 버섯" 인상): stakes=True 시에만
    if not stakes:
        return
    tilt = 15.0
    for i, a in enumerate((90.0, 210.0, 330.0)):
        rad = math.radians(a)
        bx = cx + stake_off * math.cos(rad)
        by = cy + stake_off * math.sin(rad)
        add_cylinder(stage, f"{prefix}/Stake_{i}",
                     (bx, by, gz + stake_h / 2.0), stake_r, stake_h, wood_mtl,
                     rotY=-tilt * math.cos(rad), rotX=tilt * math.sin(rad))


def build_planter(stage, prefix, cx, cy, base_z, curb_mtl, grass_mtl,
                  tree_mtls=None, size=3.0, curb_h=0.45, curb_t=0.25,
                  cap_over=0.05, cap_h=0.05, grass_h=0.40):
    """화단: 경계석 4벽 + 캡(오버행) + 잔디 상면 (+옵션 나무).
    tree_mtls=(wood, canopy_a, canopy_b) 지정 시 중앙에 나무. scene01 이식."""
    S, h, t = size, curb_h, curb_t
    over, gh = cap_over, grass_h
    half = S / 2.0
    top = base_z + h
    walls = [
        ("S", cx, cy - half + t / 2.0, S, t),
        ("N", cx, cy + half - t / 2.0, S, t),
        ("W", cx - half + t / 2.0, cy, t, S - 2 * t),
        ("E", cx + half - t / 2.0, cy, t, S - 2 * t),
    ]
    for tag, wx, wy, sx, sy in walls:
        add_box(stage, f"{prefix}/Curb_{tag}", (wx, wy, base_z + h / 2.0),
                (sx, sy, h), curb_mtl, collider=True)
        add_box(stage, f"{prefix}/Cap_{tag}", (wx, wy, top + cap_h / 2.0),
                (sx + 2 * over if sx < sy else sx,
                 sy + 2 * over if sy <= sx else sy, cap_h), curb_mtl)
    add_box(stage, f"{prefix}/Grass", (cx, cy, base_z + gh / 2.0),
            (S - 2 * t, S - 2 * t, gh), grass_mtl)
    # 화단 관목 — 다듬지 않은 화단 관목이야말로 "솜사탕"의 본체다.
    # (다듬은 생울타리가 상자 형태인 건 전정 결과라 오히려 맞다.)
    # 나무가 있으면 중앙을 비우고 모서리 쪽에 앉힌다.
    if LOOK_GEO and veg_available():
        inner = S / 2.0 - t - 0.25
        if inner > 0.35:
            r = inner * 0.62
            pts = [(cx + r, cy + r, base_z + gh), (cx - r, cy - r, base_z + gh)]
            if tree_mtls is None:
                pts.append((cx, cy, base_z + gh))
            place_shrubs(stage, f"{prefix}/Shrub", pts,
                         target_h=min(0.85, max(0.45, inner * 0.9)),
                         pool=SHRUB_ORNAMENT,
                         seed=zlib.crc32(f"{cx:.2f}_{cy:.2f}".encode()))
    if tree_mtls is not None:
        build_tree(stage, prefix, cx, cy, base_z + gh, *tree_mtls)


_FIRE_MTL_CACHE = {}


def _fire_decal_mtl(stage, prefix):
    """소방관 진입창 표식 재질 — **씬당 1개만** 만든다.
    동마다 만들면 82개 건물 × 재질이 되어 재질 테이블이 터진다.
    적색은 v5.1 §4 상수색 불가침 대상이라 텍스처 승격에서 제외되도록
    이름을 `Looks/FkFireSignRed` 로 준다(역할 분류기 sign 규칙에 걸린다).
    """
    root = prefix.split("/Looks")[0].rsplit("/", 2)[0] if "/Looks" in prefix \
        else "/".join(prefix.split("/")[:3])
    key = (id(stage), root)
    m = _FIRE_MTL_CACHE.get(key)
    if m is None:
        m = make_pbr(stage, f"{root}/Looks/FkFireSignRed",
                     diffuse_color=(0.55, 0.045, 0.035),
                     roughness_const=0.55)
        _FIRE_MTL_CACHE[key] = m
    return m


def build_building(stage, prefix, bd, shell_mtl, glass_mtl, parapet_mtl,
                   window=None):
    """건물 1동. bd 딕셔너리(x0,x1,y0,y1,h,floors,axis,facade_*,face_dir).
    axis="y"→파사드 y평면(창문 x배열), "x"→x평면(창문 y배열). scene01 이식.
    bd["base_z"](선택, 기본 0.0): 건물 기단 월드 z — 지반이 z=0이 아닌 씬에서
    부유 방지(h·창문·파라펫 z는 base_z 기준 상대).
    반환: 생성 프림 리스트.

    [사실화 v1 · 구성 감사] 종전 구성은 **박스 + 유리 쿼드 + 파라펫**이 전부라
    24개 씬에서 화면 상단 30~50%를 "파사드 빌보드"가 차지했다. 감사 지적:
      · 출입구 0 · 창틀 0 · 옥탑 0 · 선홈통 0
      · **33씬 통틀어 사람이 드나드는 문이 사실상 0개** →
        "무대는 있는데 아무도 살지 않는다"의 직접 원인
    LOOK_GEO 에서 아래 3단 구성을 얹는다(전부 기능 필수물이라 v5.2 §6 통과):
      ① 저층부 — 출입문(h2.1, 스케일 앵커 겸함)·기단 마감
      ② 기준층 — 창대(sill)·층간 띠
      ③ 옥탑 — 계단실 박스·난간(원경 실루엣을 직선 뚜껑에서 해방)
    선홈통(세로 홈통)은 파사드 수직 분절을 만들어 빌보드 인상을 깬다.
    """
    if window is None:
        window = dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0)
    wd = window
    base = float(bd.get("base_z", 0.0))
    cx = (bd["x0"] + bd["x1"]) / 2.0
    cy = (bd["y0"] + bd["y1"]) / 2.0
    Lx = bd["x1"] - bd["x0"]
    Ly = bd["y1"] - bd["y0"]
    hh = bd["h"]
    prims = []
    prims.append(add_box(stage, f"{prefix}/Shell",
                         (cx, cy, base + (hh - 1.0) / 2.0),
                         (Lx, Ly, hh + 1.0), shell_mtl, collider=True))
    fstep = hh / bd["floors"]
    ins = float(wd.get("inset", 0.0)) if LOOK_GEO else 0.0
    band_t = min(max(ins, 0.0), 0.15)
    band_h = 0.12
    # ── [T1-10] 창 리세스 — `window["inset"]` 이 정의만 되고 읽히지 않던 버그 ──
    # 종전: 유리 슬래브(두께 WIN_T=0.03)의 중심을 파사드면 +5 mm 에 두어
    #   **외면이 벽면보다 20 mm 바깥**에 있었다 = 벽에 유리판을 덧댄 모양.
    #   실제 창은 벽면보다 뒤로 물러나 있고 그 리빌이 그림자선을 만든다.
    # 그러나 **셸은 솔리드 박스**다 — 파사드면(facade_x/y)은 셸의 한 면이고
    #   그 안쪽은 전부 채워져 있다(씬 101개 동 AST 전수 확인, 예외 0).
    #   따라서 유리를 inset(=0.15) 만큼 그대로 밀어 넣으면 셸 내부에 묻혀
    #   **23개 씬의 창이 전부 사라진다**. 개구(리빌) 기하 없이 표현 가능한
    #   리세스의 상한은 "외면을 벽면까지 당기는 것"이고, 동일평면 Z-파이팅을
    #   피하려면 WIN_EPS 는 남겨야 한다(씬01 주석의 현행 관례:
    #   *"두께 0.03 패널을 파사드에서 2 cm 돌출·1 cm 매입 — 동일평면 Z파이팅
    #   회피, 불리언 불필요"*).
    # → 여기서는 **돌출 20 mm → 5 mm** 까지만 물린다. 잔여분(0.135)은 파사드
    #   개구가 필요하므로 `building_kit` 스팬드럴 분해(T2) 몫이다.
    # LOOK_GEO=0 이면 ins=0 → recess=0 → 창 좌표는 종전과 **완전 동일**하다.
    WIN_T = 0.03                                 # 유리 슬래브 두께(현행 값)
    WIN_EPS = 0.005                              # 벽면 동일평면 회피 여유
    recess = max(0.0, min(ins, 0.005 + WIN_T / 2.0 - WIN_EPS))
    axis_y = bd.get("axis", "y") == "y"
    fdir = bd["face_dir"]
    if axis_y:
        gy = bd["facade_y"] + fdir * 0.005
        gy_win = (gy - fdir * recess) if recess > 1e-9 else gy
        usable = Lx - 2 * wd["margin"]
    else:
        gx = bd["facade_x"] + fdir * 0.005
        gx_win = (gx - fdir * recess) if recess > 1e-9 else gx
        usable = Ly - 2 * wd["margin"]
    ncols = max(1, int(usable / wd["col_step"]))

    # ── 창 상한 ────────────────────────────────────────────────────────
    # 측정: 33씬에 창 프림이 **4,173개인데 그 대부분이 프레임 밖**이다.
    # 판정 1순위 시점(h0.3·pitch −10°·vFOV 36°)에서 프레임 상단은 지평 위
    # +8.0° 뿐이라, 거리 d 에서 보이는 최고 높이는 0.3 + 0.14·d 다.
    #   d=20m → 3.1m · d=34m → 5.1m · d=90m → 12.9m
    # 즉 34m 짜리 아파트 파사드도 **지상 5.1m = 1.7개 층만** 화면에 들어온다.
    # 프림의 19%를 안 보이는 곳에 쓰면서, 화면을 채우는 지상 0~5m 구간에는
    # 셸 박스 한 면 말고 아무것도 없었다.
    # → 안 보이는 층의 창을 만들지 않고, 그 예산을 저층부에 재투자한다.
    nrows = bd["floors"]
    # **창·SillBand 프림 개수**가 바뀌므로 기하다(T1 §1.7.1 #21 — v1 열거 누락 2곳 중 하나).
    if LOOK_GEO:
        try:
            nrows = fk.window_rows_visible(
                float(bd.get("lod_dist",
                             abs(bd["facade_y"] if axis_y else bd["facade_x"]))),
                fstep, bd["floors"], base_z=base,
                near_dist=20.0, min_rows=2)
        except Exception as e:
            print(f"[룩v1][경고] 창 상한 계산 실패 {prefix}: {e}")
            nrows = bd["floors"]

    for f in range(nrows):
        zc = base + fstep * f + fstep * 0.5
        if band_t > 1e-4:
            zb = zc - wd["h"] / 2.0 - band_h / 2.0
            if axis_y:
                prims.append(add_box(
                    stage, f"{prefix}/SillBand_{f}",
                    (cx, gy + fdir * band_t / 2.0, zb),
                    (Lx - 0.4, band_t, band_h), parapet_mtl))
            else:
                prims.append(add_box(
                    stage, f"{prefix}/SillBand_{f}",
                    (gx + fdir * band_t / 2.0, cy, zb),
                    (band_t, Ly - 0.4, band_h), parapet_mtl))
        for c in range(ncols):
            if axis_y:
                xc = bd["x0"] + wd["margin"] + (c + 0.5) * (usable / ncols)
                prims.append(add_box(stage, f"{prefix}/Win_{f}_{c}",
                                     (xc, gy_win, zc), (wd["w"], WIN_T, wd["h"]),
                                     glass_mtl))
            else:
                yc = bd["y0"] + wd["margin"] + (c + 0.5) * (usable / ncols)
                prims.append(add_box(stage, f"{prefix}/Win_{f}_{c}",
                                     (gx_win, yc, zc), (WIN_T, wd["w"], wd["h"]),
                                     glass_mtl))

    # 파라펫: 건축법 시행령 §40 은 옥상 난간을 **1.2 m 이상**으로 규정한다.
    # 종전 0.5 는 규정 미달이었고, 원경 실루엣도 그만큼 납작했다.
    par_h = 1.20 if LOOK_GEO else 0.5
    prims.append(add_box(stage, f"{prefix}/Parapet",
                         (cx, cy, base + hh + par_h / 2.0),
                         (Lx + 0.2, Ly + 0.2, par_h), parapet_mtl))

    # 이 아래가 전부 게이트 안이다 — 기단 석재 띠·에어컨 실외기·저층부 파사드 킷
    # 전체가 기하 신설이므로 `LOOK_GEO` 다(T1 §1.7.1 #23 — v1 열거 누락 2곳 중 하나.
    # 이 한 줄을 놓치면 A/B **양팔에서** 건물 저층부가 통째로 사라진다).
    if not LOOK_GEO:
        return prims

    # ── ⓪ 기단 석재 띠 ────────────────────────────────────────────────
    # **동당 프림 1개**인데 h0.3 프레임 하단을 직격한다 — 최대 ROI.
    # 한국 건물 저층부는 예외 없이 화강석·타일 기단으로 마감돼 있다.
    try:
        fac = fk.facade_from_bd(bd)
        K = fk.Kit(add_box, add_cylinder)
        prims += fk.build_plinth(K, stage, prefix, bd["x0"], bd["x1"],
                                 bd["y0"], bd["y1"], base, parapet_mtl,
                                 height=1.10)
        # 에어컨 실외기 — 조사가 꼽은 **한국 식별 최대 단서**이고
        # 설치 높이 1.5~2.6m = 로봇 시점 정면이다.
        prims += fk.build_aircon_units(K, stage, prefix, fac,
                                       parapet_mtl, parapet_mtl,
                                       mode="eaves", count=4,
                                       seed=zlib.crc32(prefix.encode()))
        # 소방관 진입창 붉은 역삼각형 — 2~11층 법정 의무라 실제로 100% 있고
        # **얇은 쿼드라 사실상 프림 비용이 없다**. 가장 값싼 한국 신호.
        lv = fk.floor_levels(bd["floors"], fstep, base_z=base)
        prims += fk.build_fire_access_marks(stage, prefix, fac, lv,
                                            _fire_decal_mtl(stage, prefix),
                                            max_floors=nrows)
    except Exception as e:
        print(f"[룩v1][경고] 파사드 저층부 실패 {prefix}: {e}")

    # ── ① 저층부: 출입문 ──────────────────────────────────────────────
    # 문 높이 2.1 m 는 **스케일 앵커**를 겸한다. 사람·차량이 0건인 라이브러리에서
    # 절대 크기를 읽을 단서가 거의 없다는 것이 구성 감사의 핵심 지적이었다.
    DW, DH = 1.8, 2.1
    if axis_y:
        prims.append(add_box(stage, f"{prefix}/Door",
                             (cx, gy + fdir * 0.02, base + DH / 2.0),
                             (DW, 0.06, DH), glass_mtl))
        prims.append(add_box(stage, f"{prefix}/DoorHead",
                             (cx, gy + fdir * 0.10, base + DH + 0.12),
                             (DW + 0.5, 0.22, 0.24), parapet_mtl))
    else:
        prims.append(add_box(stage, f"{prefix}/Door",
                             (gx + fdir * 0.02, cy, base + DH / 2.0),
                             (0.06, DW, DH), glass_mtl))
        prims.append(add_box(stage, f"{prefix}/DoorHead",
                             (gx + fdir * 0.10, cy, base + DH + 0.12),
                             (0.22, DW + 0.5, 0.24), parapet_mtl))

    # ── ② 선홈통(세로 홈통) — 파사드 수직 분절 ─────────────────────────
    # 빌보드 인상을 깨는 가장 싼 수단. 한국 건물에 예외 없이 있다.
    span = Lx if axis_y else Ly
    ndp = max(2, int(span / 12.0) + 1)
    for i in range(ndp):
        t = (i + 0.5) / ndp
        if axis_y:
            px = bd["x0"] + t * Lx
            prims.append(add_cylinder(stage, f"{prefix}/Downpipe_{i}",
                                      (px, gy + fdir * 0.09, base + hh / 2.0),
                                      0.055, hh, parapet_mtl))
        else:
            py = bd["y0"] + t * Ly
            prims.append(add_cylinder(stage, f"{prefix}/Downpipe_{i}",
                                      (gx + fdir * 0.09, py, base + hh / 2.0),
                                      0.055, hh, parapet_mtl))

    # ── ③ 옥탑 — 계단실 + 물탱크대 ────────────────────────────────────
    # 원경 실루엣이 "흰 뚜껑 얹은 상자"에서 벗어난다. 한국 건물 옥상의 기본 구성.
    ph_w = min(4.2, Lx * 0.34)
    ph_d = min(3.4, Ly * 0.34)
    if ph_w > 1.2 and ph_d > 1.2:
        ph_h = 2.6
        ox = cx - Lx * 0.18
        oy = cy + Ly * 0.12
        prims.append(add_box(stage, f"{prefix}/Penthouse",
                             (ox, oy, base + hh + 0.5 + ph_h / 2.0),
                             (ph_w, ph_d, ph_h), shell_mtl))
        prims.append(add_box(stage, f"{prefix}/PenthouseCap",
                             (ox, oy, base + hh + 0.5 + ph_h + 0.09),
                             (ph_w + 0.24, ph_d + 0.24, 0.18), parapet_mtl))
    return prims


def place_shrubs(stage, prefix, pts, target_h, pool=None, seed=1234,
                 overlap=0.0, tag="Sh"):
    """[사실화 v1] 지정 좌표들에 실물 관목 USD 를 세운다.

    pts: [(x, y, z_ground), ...]
    target_h: 목표 수고[m]. **랜덤화 폭은 ±8% 로 묶는다** — 관목 높이는
      스케일 앵커라서 크게 흔들면 단서가 지워진다(수고 매직넘버 사고 재발 방지).
    overlap: >0 이면 인접 개체가 겹치도록 폭 기준 배치를 호출부가 계산했다고 보고
      크기만 키운다. 생울타리용.
    반환: 배치 개수.
    """
    if not (LOOK_GEO and veg_available()):
        return 0
    names = pool or SHRUB_ORNAMENT
    avail = [s for s in VEG_SHRUBS
             if s[0] in names and os.path.isfile(os.path.join(VEG_DIR, s[0]))]
    if not avail:
        return 0
    import random as _random
    rnd = _random.Random(int(seed) & 0x7FFFFFFF)
    placed = 0
    for i, (px, py, pz) in enumerate(pts):
        rel, nat_w, zmin, _tri, nat_h = avail[rnd.randrange(len(avail))]
        # [W2 · A감사 6-b 교정] **높이 스케일은 네이티브 '높이' 기준**이다.
        # 종전은 폭 기준이었고("관목은 대체로 폭≈높이" [추정]), 실측 종횡비가
        # 0.607~1.973 로 흩어져 있어 요청 수고 대비 −39 %~+97 % 오차가 났다.
        # `overlap` 은 **폭 방향 겹침**을 만들려는 인자이므로 높이 기준으로 옮긴
        # 뒤에도 같은 배율로 걸어 종전 생울타리 밀도를 보존한다.
        s = (float(target_h) * (1.0 + overlap) / max(nat_h, 1e-6)
             * rnd.uniform(0.92, 1.08))
        try:
            # zmin 은 네이티브 치수라 같은 배율로 늘려야 바닥이 지면에 붙는다.
            # 이걸 빼먹으면 Rhododendron(zmin −0.416)은 41cm 가 땅에 묻힌다.
            xf = add_vegetation(stage, f"{prefix}/{tag}_{i}", rel,
                                (px, py, float(pz) + zmin * s),
                                yaw_deg=rnd.uniform(0, 360),
                                scale_mul=s)
            if xf is not None:
                # Seasonal sub-prims off BEFORE instancing. Order matters:
                # once SetInstanceable(True) is applied the descendants live in
                # a shared prototype and per-instance edits are ignored.
                _deactivate_seasonal(stage, f"{prefix}/{tag}_{i}/Asset", rel)
                try:
                    stage.GetPrimAtPath(f"{prefix}/{tag}_{i}/Asset").SetInstanceable(True)
                except Exception:
                    pass
                placed += 1
        except Exception as e:
            print(f"[룩v1][경고] 관목 배치 실패 {prefix}/{tag}_{i}: {e}")
            break
    if placed:
        LOOK_STATS["shrub"] = LOOK_STATS.get("shrub", 0) + placed
    return placed


def build_hedge(stage, prefix, x0, y0, x1, y1, h, mtl=None, base_z=0.0,
                scale_m=1.2, tint=(0.35, 0.45, 0.28), rounded=True,
                crown_max=48, bulge=1.03):
    """생울타리·억새 띠. mtl=None이면 grass 텍스처 진녹 틴트(0.35,0.45,0.28),
    scale 1.2로 내부 생성.

    [v6 판정 C-5] 단일 육면체는 '건초 더미/흙벽돌 상자'로 렌더된다(12 억새,
    13 생울타리). rounded=True(기본)면 본체 박스를 h*0.72로 낮추고 그 상단에
    눌린 타원체(crown blob) 열을 겹쳐 상단을 라운딩·요철화한다.
      - 본체 박스 경로 `prefix/Box`(콜라이더 유지) — 기존 참조·시그니처 호환.
      - crown 은 좌표 해시 시드라 재실행 시 동일, 띠마다 요철이 다르다.
      - 덩이 크기 ≈ 수관 높이. 띠가 넓으면(억새 밴드 등) 단변 방향 2~3 열로
        엇갈려 배치(`Crown_{열}_{i}`)해 가로 소시지 인상을 피한다.
      - 상면 z ≈ base_z+h (블롭별 ±6 % 요철), 측면 돌출은 장변 ≤5 cm ·
        단변 ≤ 0.1×열폭 — 벽 상단·개구 에지 배치에서도 부유 오독 없음.
    rounded=False 또는 h·길이가 미소하면 구 동작(단일 박스) 그대로.
    반환: Cube 프림(본체) — 기존과 동일."""
    import random as _random
    if mtl is None:
        mtl = make_pbr(stage, prefix + "/HedgeMtl", tex_path("grass", "diff"),
                       tex_path("grass", "nor"), tex_path("grass", "rough"),
                       scale_m, tint=tint)
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    sx, sy = abs(x1 - x0), abs(y1 - y0)
    L, W = max(sx, sy), min(sx, sy)          # 장변·단변
    if (not rounded) or h <= 0.06 or L <= 0.05 or W <= 1e-6:
        return add_box(stage, prefix + "/Box", (cx, cy, base_z + h / 2.0),
                       (sx, sy, h), mtl, collider=True)

    body_h = h * 0.72                        # 본체(상단 라운딩분 0.28h 를 블롭이 담당)
    box = add_box(stage, prefix + "/Box", (cx, cy, base_z + body_h / 2.0),
                  (sx, sy, body_h), mtl, collider=True)
    rnd = _random.Random((int(round(cx * 100)) * 73856093)
                         ^ (int(round(cy * 100)) * 19349663)
                         ^ (int(round(L * 100)) * 83492791))
    # 덩이 크기 ≈ 수관 높이(폭이 좁으면 폭) — 띠가 길면 개수로, 넓으면 열로 채운다
    pitch0 = max(0.30, min(W, h * 1.2)) * 0.9
    n = max(2, min(crown_max, int(round(L / max(pitch0, 1e-3)))))
    pitch = L / n
    rows = max(1, min(3, int(round(W / max(pitch, 1e-3)))))
    row_w = W / rows
    along_x = sx >= sy
    t0 = (cx - L / 2.0) if along_x else (cy - L / 2.0)
    u0 = (cy - W / 2.0) if along_x else (cx - W / 2.0)   # 단변 방향 원점
    for j in range(rows):
        for i in range(n):
            rz = h * rnd.uniform(0.26, 0.34)      # 정점 ≈ base_z + h (±6 %)
            rl = pitch * rnd.uniform(0.56, 0.70)  # 장변 반경(이웃과 겹치도록)
            rw = (row_w / 2.0) * bulge * rnd.uniform(0.94, 1.06)
            # 장변 끝단 돌출 ≤ 5 cm 로 클램프(벽 상단·에지 배치에서 부유 오독 방지)
            t = min(max(t0 + (i + 0.5) * pitch + (0.5 * pitch if j % 2 else 0.0),
                        t0 + rl - 0.05), t0 + L - rl + 0.05)
            u = u0 + (j + 0.5) * row_w + rnd.uniform(-0.05, 0.05) * row_w
            bx, by = (t, u) if along_x else (u, t)
            add_sphere(stage, f"{prefix}/Crown_{j}_{i}",
                       (bx, by, base_z + body_h),
                       (rl if along_x else rw, rw if along_x else rl, rz), mtl)
    return box


def build_bench(stage, prefix, cx, cy, base_z, mtl, length=1.8, width=0.4,
                height=0.45, yaw=0.0):
    """등받이 없는 벤치(좌판 + 다리 4). 기본 1.8×0.4×h0.45, weathered_planks.
    yaw(도)로 배치 회전. 자식은 부모 Xform 로컬 좌표. 반환: 루트 Xform 프림."""
    from pxr import UsdGeom, Gf
    root = UsdGeom.Xform.Define(stage, prefix)
    xf = UsdGeom.Xformable(root)
    xf.AddTranslateOp().Set(Gf.Vec3d(float(cx), float(cy), float(base_z)))
    if abs(yaw) > 1e-9:
        xf.AddRotateZOp().Set(float(yaw))
    seat_t = 0.06
    add_box(stage, prefix + "/Seat", (0.0, 0.0, height - seat_t / 2.0),
            (length, width, seat_t), mtl, collider=True)
    lx = length / 2.0 - 0.08
    ly = width / 2.0 - 0.06
    legh = height - seat_t
    for sx, sy, tag in ((lx, ly, "PP"), (lx, -ly, "PN"),
                        (-lx, ly, "NP"), (-lx, -ly, "NN")):
        add_box(stage, prefix + f"/Leg_{tag}", (sx, sy, legh / 2.0),
                (0.06, 0.06, legh), mtl)
    return root


def build_bollard(stage, path, cx, cy, base_z, mtl=None, radius=0.06,
                  height=0.75):
    """볼라드 r0.06 h0.75 스테인리스. mtl=None이면 내부 생성. 반환: Cylinder 프림."""
    if mtl is None:
        mtl = make_pbr(stage, path + "/Mtl", diffuse_color=(0.80, 0.82, 0.85),
                       metallic=0.9, roughness_const=0.35)
    return add_cylinder(stage, path, (cx, cy, base_z + height / 2.0),
                        radius, height, mtl, collider=True)


# ===========================================================================
# [6] 조명 — noon HDRI lookfix + DomeLight + 보조 태양 (scene01 그대로)
# ===========================================================================
def build_sign(stage, prefix, cx, cy, base_z, yaw_deg, panel_mtl,
               w=0.8, h=0.8, panel_z=None, pole_h=2.2, pole_r=0.04,
               pole_mtl=None, back_mtl=None):
    """[v5 공통 레이어] 한글 사인: 지주 1본 + st-UV 쿼드 패널(+박판 배킹).
      panel_mtl 은 make_pbr(tex_path("sign_*","diff"), uv_mode=True) 로 생성할 것.
      yaw_deg: 패널 법선 방위(0 = +X 를 바라봄). panel_z: 패널 중심 z
      (기본 = base_z + pole_h − h/2 − 0.05, 지주 상단걸이).
    반환: 생성 프림 리스트."""
    from pxr import UsdGeom, Gf, Sdf
    prims = []
    if panel_z is None:
        panel_z = base_z + pole_h - h / 2.0 - 0.05
    # 지주
    prims.append(add_cylinder(stage, f"{prefix}/Pole",
                              (cx, cy, base_z + pole_h / 2.0),
                              pole_r, pole_h,
                              pole_mtl if pole_mtl is not None else back_mtl))
    # 패널 쿼드 (월드 좌표 직접 — 접선 t = 법선의 좌측)
    a = math.radians(yaw_deg)
    nx, ny = math.cos(a), math.sin(a)
    tx, ty = -ny, nx
    off = pole_r + 0.015                       # 지주 전면으로 살짝 돌출
    cxp, cyp = cx + nx * off, cy + ny * off
    pts = [Gf.Vec3f(cxp - tx * w / 2, cyp - ty * w / 2, panel_z - h / 2),
           Gf.Vec3f(cxp + tx * w / 2, cyp + ty * w / 2, panel_z - h / 2),
           Gf.Vec3f(cxp + tx * w / 2, cyp + ty * w / 2, panel_z + h / 2),
           Gf.Vec3f(cxp - tx * w / 2, cyp - ty * w / 2, panel_z + h / 2)]
    mesh = UsdGeom.Mesh.Define(stage, f"{prefix}/Panel")
    mesh.CreatePointsAttr(pts)
    mesh.CreateFaceVertexCountsAttr([4])
    mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    # [사실화 P1] subdivisionScheme 미저작 = USD 기본값 catmullClark. 쿼드의
    # Catmull-Clark 극한면은 모서리 정점을 중심으로 당기므로 패널이 축소되고
    # st(0..1) 정합이 깨진다. 현재는 refinementLevel 기본 0 이라 잠복 상태지만
    # 그 설정이 바뀌는 순간 전 사인이 어긋난다. 명시 저작으로 못박는다.
    # (scene09·sceneN3 는 이미 같은 이유로 "none" 을 저작해 두었다.)
    mesh.CreateSubdivisionSchemeAttr("none")
    mesh.CreateDoubleSidedAttr(True)
    pv = UsdGeom.PrimvarsAPI(mesh.GetPrim()).CreatePrimvar(
        "st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
    pv.Set([Gf.Vec2f(0, 0), Gf.Vec2f(1, 0), Gf.Vec2f(1, 1), Gf.Vec2f(0, 1)])
    if panel_mtl is not None:
        _bind_mtl(mesh.GetPrim(), panel_mtl)
    prims.append(mesh.GetPrim())
    # 배킹 박판 (뒷면 미러 텍스트 가림) — 패널과 동일 yaw 회전 박스
    if back_mtl is not None:
        prims.append(_oriented_box(stage, f"{prefix}/Back",
                                   (cxp - nx * 0.013, cyp - ny * 0.013,
                                    panel_z),
                                   (0.022, w + 0.01, h + 0.01),
                                   back_mtl, rotz=yaw_deg))
    return prims


def ensure_noon_lookfix(src_path):
    """noon HDRI 파생본(_lookfix.exr) 생성/캐시 — scene01에서 그대로 이관.

    ① 태양 디스크(각반경 1.5°)를 서컴솔라 링(1.5~2.5°) p90 휘도로 캡:
       RTX 돔 샘플링의 태양 블러가 만드는 초연질 캐스트 섀도 제거. 제거된
       직달 성분은 HDRI 태양 방향에 정합한 DistantLight(0.53°)가 대체.
    ② 지평 아래 -18°~0° 대역을 인접 하늘(elev 0.5~3.5°) 휘도로 리프트.
    실패 시(예: cv2 부재) 원본 경로를 그대로 반환 (경고만)."""
    out_path = src_path[:-4] + "_lookfix.exr"
    try:
        if (os.path.isfile(out_path)
                and os.path.getmtime(out_path) >= os.path.getmtime(src_path)):
            return out_path
        os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
        import cv2
        # [사실화 v1 · 버그 수정] **4채널(RGBA) EXR 처리 오류.**
        # 종전 `[..., ::-1]` 은 BGRA 를 뒤집어 [A,R,G,B] 를 만든다 → 알파가 R
        # 자리에 들어가고 이후 지평 리프트에서 브로드캐스트 예외 → except 가
        # 삼키고 **원본 경로를 반환**한다. 그러면 태양 캡이 적용되지 않은 채
        # DistantLight 가 추가되어 **이중 태양**이 된다(조용한 실패라 더 위험).
        # 기존 qwantani 는 3채널이라 잠복했고, overcast 는 lookfix=False 라
        # 우회돼 있었다. PolyHaven puresky 계열은 대부분 RGBA 다.
        rgb = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)[..., :3][..., ::-1]
        rgb = rgb.astype(np.float64)
        h, w = rgb.shape[:2]
        lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1]
               + 0.0722 * rgb[..., 2])
        iy, ix = np.unravel_index(np.argmax(lum), lum.shape)
        vv = (np.arange(h) + 0.5) / h
        th = np.pi * vv
        ph = 2.0 * np.pi * (np.arange(w) + 0.5) / w
        st, ct = np.sin(th)[:, None], np.cos(th)[:, None]
        dx = st * np.cos(ph)[None, :]
        dy = st * np.sin(ph)[None, :]
        dz = np.broadcast_to(ct, (h, w))
        s = np.array([dx[iy, ix], dy[iy, ix], dz[iy, ix]])
        ang = np.degrees(np.arccos(
            np.clip(dx * s[0] + dy * s[1] + dz * s[2], -1.0, 1.0)))
        # 태양 캡 각반경. 실제 태양 각반경은 0.27° 인데 1.5° 를 통째로 클램프하면
        # **구름 하늘에서 "잘린 원반"** 이 보인다(지름 3° 균일 밴드 + 테두리).
        # 구름 HDRI 는 0.6° 권장(제거 직달에너지 보존 98.3~99.3% — 조사 실측이라
        # DistantLight 재튜닝 없이 전환 가능). 기본값은 **1.5 유지** — 기존 33씬
        # 조명이 미세하게라도 바뀌면 이번 라운드의 A/B 통제가 깨진다.
        cap_deg = float(os.environ.get("NEGOBS_SUN_CAP_DEG", "1.5"))
        ring = (ang > cap_deg) & (ang < cap_deg + 1.0)
        cap = np.percentile(lum[ring], 90)
        mask = (ang < cap_deg) & (lum > cap)
        scl = np.ones_like(lum)
        scl[mask] = cap / lum[mask]
        out = rgb * scl[..., None]
        elev = 90.0 - 180.0 * vv
        ref = out[(elev > 0.5) & (elev < 3.5)].mean(axis=0)      # (w, 3)
        k = np.ones(129) / 129.0
        ref = np.stack(
            [np.convolve(np.r_[ref[-64:, c], ref[:, c], ref[:64, c]],
                         k, mode="same")[64:-64] for c in range(3)], axis=-1)
        t = np.clip((elev + 24.0) / 6.0, 0.0, 1.0) * (elev < 0.0)
        lift = np.maximum(out, ref[None, :, :])
        out += (lift - out) * t[:, None, None]
        cv2.imwrite(out_path, out[..., ::-1].astype(np.float32),
                    [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_HALF,
                     cv2.IMWRITE_EXR_COMPRESSION, cv2.IMWRITE_EXR_COMPRESSION_ZIP])
        print(f"[HDRI] noon lookfix 생성 (태양 캡 {int(mask.sum())}px, "
              f"cap L={cap:.2f}): {out_path}")
        return out_path
    except Exception as e:                       # pragma: no cover
        print(f"[HDRI][경고] lookfix 생성 실패({e}) — 원본 사용")
        return src_path


def setup_lighting(stage, light_params, sun_az_offset):
    """DomeLight(noon HDRI lookfix) + HDRI 태양 방향 정합 DistantLight.
    light_params: hdri, dome_intensity, noon_dome_rot, noon_sun_enable,
      noon_sun_elev, noon_sun_intensity, noon_sun_color, hdri_sun_rotz_offset.
    반환: apply_dome_rot(user_off) 콜백 (돔+보조태양 Z회전 갱신)."""
    from pxr import UsdGeom, UsdLux, Gf
    lp = light_params
    dome = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
    dome.CreateIntensityAttr(float(lp["dome_intensity"]))
    dome.CreateTextureFormatAttr("latlong")
    tex_attr = dome.CreateTextureFileAttr()
    hdri = os.path.join(ASSETS_DIR, lp.get("hdri", DEFAULT_HDRI))
    if lp.get("lookfix", True):
        hdri = ensure_noon_lookfix(hdri)       # 태양 캡 + 지평 헤이즈 리프트
    else:
        print("[하늘] lookfix 스킵(overcast 등 무태양 프로파일) — 원본 사용")
    print(f"[하늘] noon: {os.path.basename(hdri)} "
          f"(exists={os.path.isfile(hdri)})")
    tex_attr.Set(hdri)
    # RTX 돔은 Z-up 스테이지에서 극축 +Z로 올바름 (rotateX 불필요)
    rot_op = UsdGeom.Xformable(dome.GetPrim()).AddRotateZOp()
    rot_op.Set(0.0)

    # HDRI 태양 방향에 정합한 명시적 DistantLight(0.53°) — 경질 그림자 담당
    sun = UsdLux.DistantLight.Define(stage, "/World/NoonSun")
    sun.CreateAngleAttr(0.53)
    sun.CreateIntensityAttr(float(lp["noon_sun_intensity"]))
    sun.CreateColorAttr(Gf.Vec3f(*[float(c) for c in lp["noon_sun_color"]]))
    sxf = UsdGeom.Xformable(sun.GetPrim())
    sun_rz = sxf.AddRotateZOp()
    sun_rz.Set(0.0)
    sxf.AddRotateXOp().Set(90.0 - float(lp["noon_sun_elev"]))
    if not lp.get("noon_sun_enable", True):
        UsdGeom.Imageable(sun.GetPrim()).MakeInvisible()

    def apply_dome_rot(user_off):
        # 돔 회전 = noon_dome_rot + sun_az_offset(씬) + [ ]키 오프셋
        rot = (float(lp["noon_dome_rot"]) + float(sun_az_offset)
               + float(user_off))
        rot_op.Set(rot)
        sun_rz.Set(rot + float(lp["hdri_sun_rotz_offset"]))

    apply_dome_rot(0.0)
    return apply_dome_rot


# ===========================================================================
# [7] 카메라 프리셋
# ===========================================================================
def grid_views(gy, heights=(0.3, 0.9, 1.8), dists=(2, 5, 10), pitch=-10):
    """h×d 그리드 프리셋 (scene01 build_views 그리드부). +X를 pitch°로 봄.
    반환: {"preset_h{h}_d{d}": dict(eye, tgt)}. 미장센 컷은 씬별로 추가."""
    views = {}
    p = math.radians(pitch)
    for hh in heights:
        for dd in dists:
            eye = [-float(dd), float(gy), float(hh)]
            tgt = [eye[0] + 5.0 * math.cos(p), float(gy),
                   eye[2] + 5.0 * math.sin(p)]
            views[f"preset_h{hh}_d{dd}"] = dict(eye=eye, tgt=tgt)
    return views


# ===========================================================================
# [8] 헤드리스 캡처 파이프라인 (scene01 캡처 블록 일반화)
# ===========================================================================
def capture_pipeline(sim_app, views, out_dir_default, set_render_mode_fn,
                     look_from_fn):
    """NEGOBS_* env 기반 헤드리스 캡처.
      NEGOBS_CAPTURE_DIR : 저장 폴더 (기본 out_dir_default)
      NEGOBS_CAPTURE_MODE: rt | pt | both (기본 rt)
      NEGOBS_VIEWS       : 쉼표 뷰 이름 필터 (기본 전부)
      NEGOBS_WARMUP      : 워밍업 update 횟수 오버라이드
    set_render_mode_fn(mode): "PathTracing"/"RaytracedLighting" 설정 콜백.
    look_from_fn(eye, tgt)  : 카메라 배치 콜백 (eye, target 위치인자)."""
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    out_dir = os.environ.get("NEGOBS_CAPTURE_DIR", out_dir_default)
    os.makedirs(out_dir, exist_ok=True)
    mode_sel = os.environ.get("NEGOBS_CAPTURE_MODE", "rt")
    modes = ["rt", "pt"] if mode_sel == "both" else [mode_sel]

    VIEWS = dict(views)
    view_f = os.environ.get("NEGOBS_VIEWS", "")
    if view_f:
        keep = {v.strip() for v in view_f.split(",") if v.strip()}
        VIEWS = {k: v for k, v in VIEWS.items() if k in keep}

    def _capture(fp):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=fp)

    manifest = []
    print(look_report())
    print(f"[캡처] 모드={modes} 뷰={list(VIEWS)}")
    for _ in range(30):                        # 초기 로딩 워밍업
        sim_app.update()

    pt_fast = os.environ.get("NEGOBS_PT_FAST", "") == "1"

    for mode in modes:
        set_render_mode_fn("PathTracing" if mode == "pt"
                           else "RaytracedLighting")
        warm_default = 572 if mode == "pt" else 90
        if pt_fast and mode == "pt":
            # 씬의 set_render_mode 가 spp=1/totalSpp=512 를 되돌려 놓으므로
            # **그 뒤에** 덮어써야 한다 (호출 순서가 핵심).
            import carb
            st = carb.settings.get_settings()
            # 씬별 상향 노브 — 간접광만으로 사는 어두운 씬(D4 등)은 64 로 부족할
            # 수 있다. `NEGOBS_PT_TOTAL_SPP=256` 처럼 씬 단위로 올린다.
            tot = int(os.environ.get("NEGOBS_PT_TOTAL_SPP",
                                     PT_FAST["total_spp"]))
            st.set("/rtx/pathtracing/spp", PT_FAST["spp"])
            st.set("/rtx/pathtracing/totalSpp", tot)
            st.set("/app/renderer/rtSubframes", PT_FAST["subframes"])
            warm_default = max(PT_FAST["warmup"],
                               -(-tot // (PT_FAST["spp"] * PT_FAST["subframes"])))
            print(f"[렌더] PT 가속 적용 (totalSpp {tot}, warmup {warm_default})")
        warm = int(os.environ.get("NEGOBS_WARMUP", str(warm_default)))
        for vname, v in VIEWS.items():
            look_from_fn(v["eye"], v["tgt"])
            for _ in range(warm):              # 워밍업 없으면 검은 이미지
                sim_app.update()
            fp = os.path.join(out_dir, f"{mode}_noon_{vname}.png")
            _capture(fp)
            # 캡처는 비동기 → 파일 크기가 안정될 때까지 대기
            ok, prev_sz = False, -1
            for _ in range(40):
                sim_app.update()
                if os.path.isfile(fp):
                    sz = os.path.getsize(fp)
                    if sz > 0 and sz == prev_sz:
                        ok = True
                        break
                    prev_sz = sz
            manifest.append(dict(file=fp, mode=mode, sky="noon",
                                 view=vname, ok=ok))
            print(f"[캡처] {os.path.basename(fp)} {'OK' if ok else 'FAIL'}")

    # manifest 병합 (조각 실행 간 — 같은 file 항목은 갱신)
    mf_path = os.path.join(out_dir, "manifest.json")
    prev = dict(views={}, shots=[])
    if os.path.isfile(mf_path):
        try:
            with open(mf_path) as f:
                prev = json.load(f)
        except Exception:
            pass
    shots = {s["file"]: s for s in prev.get("shots", [])}
    for s in manifest:
        shots[s["file"]] = s
    prev.get("views", {}).update({k: v for k, v in VIEWS.items()})
    with open(mf_path, "w") as f:
        json.dump(dict(views=prev.get("views", VIEWS),
                       shots=list(shots.values())),
                  f, indent=2, ensure_ascii=False)


# ===========================================================================
# [9] 순수 수학 자기검증 (pxr 불필요 — 빌더 배치 수학만 재현·검산)
#     실행: python3 scene_common.py
# ===========================================================================
def _geometry_selfcheck():
    print("=" * 68)
    print("scene_common v3 신규 빌더 — 순수 수학 자기검증")
    print("=" * 68)

    # (1) build_helix_steps: 32단 × 22.5° = 2회전, 낙차 합
    n, step_deg, riser, z0 = 32, 22.5, 0.18, 0.0
    total_sweep = n * step_deg
    total_drop = n * riser
    top_last = z0 - n * riser
    print("[1] helix_steps  n=%d step=%.1f°" % (n, step_deg))
    print("    총 회전각 = %.1f° = %.3f 회전" % (total_sweep, total_sweep / 360.0))
    print("    낙차 합 = %d*%.2f = %.2f m  (마지막 단 상면 z=%.2f)"
          % (n, riser, total_drop, top_last))
    r_in, r_out = 0.5, 2.2
    r_mid = (r_in + r_out) / 2.0
    chord = 2.0 * r_out * math.sin(math.radians(step_deg) / 2.0) * 1.03  # 외경 기준 커버(룩 r1 수정)
    r_w = r_in + (2.0 / 3.0) * (r_out - r_in)     # walkline 반경(서베이 §3-1)
    print("    r_mid=%.3f 현길이=%.4f m  walkline r_w=%.3f (tread깊이 %.4f m)"
          % (r_mid, chord, r_w, r_w * math.radians(step_deg)))

    # (2) build_helix_ramp: 세그 기울기각
    ri, ro = 6.0, 9.5
    a0, a1, seg = 0.0, 450.0, 36               # 1.25회전
    z0r, z1r = 0.0, -3.2
    rm = (ri + ro) / 2.0
    dth = math.radians((a1 - a0) / seg)
    L_c = 2.0 * rm * math.sin(dth / 2.0)
    dz_seg = (z1r - z0r) / seg
    tilt = math.degrees(math.atan2(dz_seg, L_c))
    print("[2] helix_ramp  r_in=%.1f r_out=%.1f sweep=%.0f° seg=%d 낙차=%.1f"
          % (ri, ro, a1 - a0, seg, z1r - z0r))
    print("    r_mid=%.3f  세그 현길이 L_c=%.4f m  dz/세그=%.4f m"
          % (rm, L_c, dz_seg))
    print("    세그 접선경사각(rotX) = atan2(%.4f, %.4f) = %.4f°  (음수=하강)"
          % (dz_seg, L_c, tilt))
    print("    검산: 전체 경사 sin = 낙차/호길이 = %.4f (세그 sinθ=%.4f 근사일치)"
          % ((z1r - z0r) / (rm * math.radians(a1 - a0)),
             math.sin(math.radians(tilt))))

    # (3) build_worn_stone_stairs: run 합 + 지터 재현(고정 시드)
    n, riser_mu, tread_mu, blocks, seed, jr = 18, 0.17, 0.38, 5, 77, 0.03
    rng = np.random.RandomState(seed)
    risers = [riser_mu + rng.uniform(-jr, jr) for _ in range(n)]
    run = n * tread_mu
    drop = sum(risers)
    print("[3] worn_stone  n=%d tread_mu=%.2f seed=%d" % (n, tread_mu, seed))
    print("    총 run = %d*%.2f = %.2f m" % (n, tread_mu, run))
    print("    지터 낙차 합(seed 재현) = %.4f m  (평균 riser=%.4f)"
          % (drop, drop / n))
    print("    처음 3단 riser = %s" % ["%.4f" % r for r in risers[:3]])

    # (4) width_pairs 선형 보간 예시(tapered_grand W_i)
    n, w_top, w_bot = 40, 6.0, 10.0
    cyc = 0.0
    def _wp(i):
        w = w_top + (w_bot - w_top) * i / (n - 1)
        return (cyc - w / 2.0, cyc + w / 2.0)
    print("[4] width_pairs 보간(tapered)  n=%d W_top=%.1f→W_bot=%.1f" %
          (n, w_top, w_bot))
    for i in (0, 10, 20, 39):
        y0i, y1i = _wp(i)
        print("    i=%2d  폭=%.3f m  (y0=%.3f, y1=%.3f)"
              % (i, y1i - y0i, y0i, y1i))
    print("=" * 68)


if __name__ == "__main__":
    _geometry_selfcheck()
