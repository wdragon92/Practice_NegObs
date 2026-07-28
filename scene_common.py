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

import numpy as np


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
    grass=dict(dir=ASSETS_DIR, diff="aerial_grass_rock_diff_4k.jpg",
               nor="aerial_grass_rock_nor_dx_4k.jpg",
               rough="aerial_grass_rock_rough_4k.jpg"),
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
    return cube


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
             emission_color=None, emission_intensity=None, uv_mode=False):
    """OmniPBR 재질. diff 지정 시 월드 스페이스 투영 텍스처, 아니면 상수 컬러.
    specular_level 지정 시 sh.CreateInput("specular_level", Float).
    emission_color+emission_intensity 지정 시 발광(enable_emission) — 실내
    씬(D4 등) 발광 패널용. RT 단일바운스 기여 미미, 판정은 PT 8바운스(교훈 7).
    uv_mode=True: 월드 투영 대신 메시 st(UV 0..1)로 샘플 — 사인 패널처럼
    텍스처가 면에 1:1 정합해야 하는 경우(build_sign 의 _sign_quad 전용).
    """
    from pxr import UsdShade, Sdf, Gf
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
                       mtl, rail_h=0.9, post_r=0.02, spacing=1.2, rail_r=0.03,
                       rail_mid_r=0.018, rail_mid_drop=0.45):
    """레일 1선(scene01 build_cues 일반화). 상단 레일 + 중간 레일 + 포스트.
      y        : 레일 Y 위치
      x_start  : 수평 연장 시작 x  (x_start..x_top 구간은 수평)
      x_top    : 경사 시작 x       (여기서부터 +X로 drop 하강)
      run,drop : 경사 구간 수평길이·낙차
      ground_fn: x→지면z 콜백 (포스트 하단 착지 높이). 단면(계단)이면 계단식.
    반환: 생성 프림 리스트."""
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

    # 포스트: 실제 지면(ground_fn)에 착지, 상단=레일선.
    xp = x_start
    p = 0
    x_end = x_top + run
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
def build_tactile(stage, path, x0, x1, y0, y1, mtl, z=0.0, proud=0.004):
    """점형 점자블록 띠(황색). x0..x1 × y0..y1 사각 밴드. 상면 z에서 proud 돌출,
    돌기는 노멀맵으로 표현(거의 플러시). 반환: Cube 프림."""
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    z_top = z + proud
    z_bot = z - 0.01
    return add_box(stage, path, (cx, cy, (z_top + z_bot) / 2.0),
                   (abs(x1 - x0), abs(y1 - y0), z_top - z_bot), mtl)


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
    반환: None(프림은 prefix 하위에 생성)."""
    import random as _random
    rnd = _random.Random((int(round(cx * 100)) * 73856093)
                         ^ (int(round(cy * 100)) * 19349663))
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
    if tree_mtls is not None:
        build_tree(stage, prefix, cx, cy, base_z + gh, *tree_mtls)


def build_building(stage, prefix, bd, shell_mtl, glass_mtl, parapet_mtl,
                   window=None):
    """건물 1동. bd 딕셔너리(x0,x1,y0,y1,h,floors,axis,facade_*,face_dir).
    axis="y"→파사드 y평면(창문 x배열), "x"→x평면(창문 y배열). scene01 이식.
    bd["base_z"](선택, 기본 0.0): 건물 기단 월드 z — 지반이 z=0이 아닌 씬에서
    부유 방지(h·창문·파라펫 z는 base_z 기준 상대).
    반환: 생성 프림 리스트."""
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
    # 셸을 base_z−1.0까지 연장(기초 부유 방지). 파라펫·창문 z는 불변.
    prims.append(add_box(stage, f"{prefix}/Shell",
                         (cx, cy, base + (hh - 1.0) / 2.0),
                         (Lx, Ly, hh + 1.0), shell_mtl, collider=True))
    fstep = hh / bd["floors"]
    if bd.get("axis", "y") == "y":
        gy = bd["facade_y"] + bd["face_dir"] * 0.005
        usable = Lx - 2 * wd["margin"]
        ncols = max(1, int(usable / wd["col_step"]))
        for f in range(bd["floors"]):
            zc = base + fstep * f + fstep * 0.5
            for c in range(ncols):
                xc = bd["x0"] + wd["margin"] + (c + 0.5) * (usable / ncols)
                prims.append(add_box(stage, f"{prefix}/Win_{f}_{c}",
                                     (xc, gy, zc), (wd["w"], 0.03, wd["h"]),
                                     glass_mtl))
    else:
        gx = bd["facade_x"] + bd["face_dir"] * 0.005
        usable = Ly - 2 * wd["margin"]
        ncols = max(1, int(usable / wd["col_step"]))
        for f in range(bd["floors"]):
            zc = base + fstep * f + fstep * 0.5
            for c in range(ncols):
                yc = bd["y0"] + wd["margin"] + (c + 0.5) * (usable / ncols)
                prims.append(add_box(stage, f"{prefix}/Win_{f}_{c}",
                                     (gx, yc, zc), (0.03, wd["w"], wd["h"]),
                                     glass_mtl))
    prims.append(add_box(stage, f"{prefix}/Parapet", (cx, cy, base + hh + 0.25),
                         (Lx + 0.2, Ly + 0.2, 0.5), parapet_mtl))
    return prims


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
        rgb = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)[..., ::-1]
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
        ring = (ang > 1.5) & (ang < 2.5)
        cap = np.percentile(lum[ring], 90)
        mask = (ang < 1.5) & (lum > cap)
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
