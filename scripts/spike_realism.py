#!/usr/bin/env python3
"""Phase 1 "검증의 날" — 사실화 재료 실동작 스파이크 랩 (v2 split-face).

`Docs/briefs/realism_brief_v1.md` Phase 1 의 실험을 **부팅 1회**로 수행한다.

## v1 → v2 재설계 이유 (감독, 1차 렌더 후)
v1 은 실험마다 별개의 오브젝트를 다른 위치에 놓고 각각 다른 카메라로 찍었다.
결과적으로 ①프레임의 절반이 하늘이라 flat% 가 하늘로 오염되고 ②A/B 두 컷의
조명·시점·거리가 서로 달라 통제가 안 됐다. v2 는 두 가지를 바꾼다:

1. **split-face**: A/B 를 **하나의 연속된 면을 반으로 갈라** 배치한다. 이음매가
   화면 중앙에 오는 한 컷에 두 조건이 동시에 들어가므로 조명·시점·거리·재질
   스케일이 완전히 통제된다. 차이가 보이면 그건 재질 차이뿐이다.
2. **지면 충전 프레이밍**: 진단 뷰는 하늘이 0 이 되도록 잡는다. 그래야
   `scripts/imgstats.py` 의 flat%/slope 가 표면 미세구조만 반영한다.
   거리는 판정 1순위 시점(h0.3 로봇 뷰)과 근접 뷰(0.5~1.2 m) 양쪽을 잡는다.

## 실험
  E1 bevel   : `round_edges_radius` 0/1/2/5/10/20 mm            [ZZ §2 상충4 — 미검증]
  E2 ground  : `NegObsGround.mdl` vs OmniPBR **split-face**      [ZZ §1 결정적 발견]
  E3 detail  : `detail_normalmap_texture` split-face             [ZZ §2 — 로컬검증됨]
  E4 subdiv  : `catmullClark` + crease                           [ZZ §6 T0-2 — 미검증]
  E5 disp    : 정점 변위 그리드 0/5/10/20 mm                      [MDL displacement RTX 미지원]
  **E9 stack : 풀스택 예측 실험 (브리프 외 — 감독 추가)**
      P0 현행 프로덕션 레시피(평면 박스+OmniPBR) / P1 +NegObsGround /
      P2 +정점변위 메시 / P3 +디테일노멀(OmniPBR 계열)
      → Phase 2 게이트 통과 가능성을 **Phase 1 에서 미리 실측**한다.
      셋을 같은 크기·같은 뷰로 찍으므로 flat%/slope 를 직접 비교할 수 있다.
  E6/E7 budget : PT 수정설정 vs PT 512 vs RT90 vs RT32 s/컷 실측

실행 (반드시 cd 포함 스크립트로 — 백그라운드 셸 cwd 리셋 함정):
  bash run_p1_spike.sh --mode rt --only e1,e2,e3,e4,e5,e9
  bash run_p1_spike.sh --mode pt --only e9,e2 --bench
"""
import os
import sys
import math
import json
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

import numpy as np                                     # noqa: E402
import scene_common as sc                              # noqa: E402

ARGS = sys.argv[1:]


def _arg(name, default):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else default


ONLY = {s.strip().lower() for s in _arg("--only", "").split(",") if s.strip()}
MODE = _arg("--mode", "both")                          # rt | pt | both
BENCH = "--bench" in ARGS
OUT_ROOT = os.path.join(_ROOT, "look_check")
MDL_GROUND = os.path.join(sc.ASSETS_DIR, "NegObsGround.mdl")

# 본편 21씬과 문자 단위로 같은 조명 조건 (scene01 §5) — A/B 의 통제 변인
LIGHT = dict(
    hdri=sc.DEFAULT_HDRI, dome_intensity=1000.0, noon_dome_rot=-110.0,
    noon_sun_enable=True, noon_sun_elev=49.79,
    noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
    hdri_sun_rotz_offset=233.5,
)
SUN_AZ_OFFSET = 0.0
PT_MAX_BOUNCES = 8


def want(tag):
    return (not ONLY) or (tag in ONLY)


print("=" * 70)
print("Phase 1 스파이크 랩 v2 (split-face) — 부팅")
print("=" * 70)
sim_app = sc.boot(True)

import carb                                            # noqa: E402
import omni.usd                                        # noqa: E402
from pxr import UsdGeom, UsdShade, Sdf, Gf              # noqa: E402
from omni.kit.viewport.utility import (                 # noqa: E402
    get_active_viewport, capture_viewport_to_file)
from isaacsim.core.utils.viewports import set_camera_view  # noqa: E402

stage = omni.usd.get_context().get_stage()
settings = carb.settings.get_settings()
ROOT = "/World/Spike"
UsdGeom.Xform.Define(stage, ROOT)
UsdGeom.Xform.Define(stage, f"{ROOT}/Looks")

RESULTS = dict(experiments={}, timing={}, notes=[])


def note(msg):
    print(f"[노트] {msg}")
    RESULTS["notes"].append(msg)


# ===========================================================================
# 재질 팩토리
# ===========================================================================
def pbr(path, diff=None, nor=None, rough=None, scale_m=1.0,
        diffuse_color=None, roughness_const=None, bump=1.0,
        round_edges_radius=None, round_edges_roundness=1.0,
        round_edges_across=False,
        detail_nor=None, detail_bump=None, detail_scale_m=None):
    """OmniPBR — sc.make_pbr 과 동일 규약 + 베벨/디테일노멀 인자."""
    mtl = UsdShade.Material.Define(stage, path)
    sh = UsdShade.Shader.Define(stage, path + "/Shader")
    sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    sh.SetSourceAsset(Sdf.AssetPath(sc.OMNIPBR_PATH), "mdl")
    sh.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
    F, C3, A, B, F2 = (Sdf.ValueTypeNames.Float, Sdf.ValueTypeNames.Color3f,
                       Sdf.ValueTypeNames.Asset, Sdf.ValueTypeNames.Bool,
                       Sdf.ValueTypeNames.Float2)

    def tex(name, p, cs):
        i = sh.CreateInput(name, A)
        i.Set(p)
        try:
            i.GetAttr().SetColorSpace(cs)
        except Exception:
            pass

    if diff is not None:
        tex("diffuse_texture", diff, "auto")
        if nor is not None:
            tex("normalmap_texture", nor, "raw")
        if rough is not None and roughness_const is None:
            tex("reflectionroughness_texture", rough, "raw")
            sh.CreateInput("reflection_roughness_texture_influence", F).Set(1.0)
        sh.CreateInput("project_uvw", B).Set(True)
        sh.CreateInput("world_or_object", B).Set(True)
        s = 1.0 / float(scale_m)
        sh.CreateInput("texture_scale", F2).Set(Gf.Vec2f(s, s))
        sh.CreateInput("bump_factor", F).Set(float(bump))
    if diffuse_color is not None:
        sh.CreateInput("diffuse_color_constant", C3).Set(Gf.Vec3f(*diffuse_color))
    if roughness_const is not None:
        sh.CreateInput("reflection_roughness_constant", F).Set(float(roughness_const))
        sh.CreateInput("reflection_roughness_texture_influence", F).Set(0.0)
    sh.CreateInput("metallic_constant", F).Set(0.0)
    if round_edges_radius is not None:
        sh.CreateInput("round_edges_radius", F).Set(float(round_edges_radius))
        sh.CreateInput("round_edges_roundness", F).Set(float(round_edges_roundness))
        sh.CreateInput("round_edges_across_materials", B).Set(bool(round_edges_across))
    if detail_nor is not None:
        tex("detail_normalmap_texture", detail_nor, "raw")
        sh.CreateInput("detail_bump_factor", F).Set(
            float(0.3 if detail_bump is None else detail_bump))
        ds = 1.0 / float(detail_scale_m or 0.12)
        sh.CreateInput("detail_texture_scale", F2).Set(Gf.Vec2f(ds, ds))
    for out in ("surface", "displacement", "volume"):
        mtl.CreateOutput(f"mdl:{out}", Sdf.ValueTypeNames.Token).ConnectToSource(
            sh.ConnectableAPI(), "out")
    return mtl


def ground_mdl(path, diff, nor, rough, scale_m=1.0,
               macro_amp=0.12, macro_wl=14.0, patch_wl=4.0,
               desat_bright=0.35, rough_noise=0.25, rough_noise_wl=1.2,
               tri_dither=0.35, tri_dither_wl=0.15, tri_weight_exp=6.0,
               bump=1.0, rough_floor=0.0, rough_mult=1.0):
    """NegObsGround.mdl — 소프트 트라이플래너 + 반복파괴 (TerrainGen 사용례 이식).

    OmniPBR 의 project_uvw 는 트라이플래너가 아니라 **큐빅 투영**이라 경사면에서
    축 전환 이음매가 난다 [ZZ §10.5]. 이 MDL 이 그 대체재다.
    """
    mtl = UsdShade.Material.Define(stage, path)
    sh = UsdShade.Shader.Define(stage, path + "/Shader")
    sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    sh.SetSourceAsset(Sdf.AssetPath(MDL_GROUND), "mdl")
    sh.SetSourceAssetSubIdentifier("NegObsGround", "mdl")
    F, A, B, F2 = (Sdf.ValueTypeNames.Float, Sdf.ValueTypeNames.Asset,
                   Sdf.ValueTypeNames.Bool, Sdf.ValueTypeNames.Float2)

    def tex(name, p, cs):
        i = sh.CreateInput(name, A)
        i.Set(p)
        try:
            i.GetAttr().SetColorSpace(cs)
        except Exception:
            pass

    tex("diffuse_texture_a", diff, "auto")
    tex("normalmap_texture_a", nor, "raw")
    tex("roughness_texture_a", rough, "raw")
    s = 1.0 / float(scale_m)
    sh.CreateInput("texture_scale_a", F2).Set(Gf.Vec2f(s, s))
    for k, v in (("macro_amp_a", macro_amp), ("macro_wavelength_a", macro_wl),
                 ("patch_wavelength_a", patch_wl),
                 ("desat_bright_a", desat_bright),
                 ("rough_noise_a", rough_noise),
                 ("rough_noise_wavelength_a", rough_noise_wl),
                 ("rough_floor_a", rough_floor), ("rough_mult_a", rough_mult),
                 ("bump_factor_a", bump), ("tri_dither", tri_dither),
                 ("tri_dither_wavelength", tri_dither_wl),
                 ("tri_weight_exp", tri_weight_exp)):
        sh.CreateInput(k, F).Set(float(v))
    sh.CreateInput("use_blend", B).Set(False)
    for out in ("surface", "displacement", "volume"):
        mtl.CreateOutput(f"mdl:{out}", Sdf.ValueTypeNames.Token).ConnectToSource(
            sh.ConnectableAPI(), "out")
    return mtl


# ===========================================================================
# 메시 유틸
# ===========================================================================
def mesh_box(path, center, size, mtl=None, subdiv=None, crease_sharp=None):
    """8정점 박스 메시. crease_sharp 지정 시 12 모서리 전부에 crease."""
    m = UsdGeom.Mesh.Define(stage, path)
    hx, hy, hz = [s / 2.0 for s in size]
    pts = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
           (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    m.CreatePointsAttr([Gf.Vec3f(*p) for p in pts])
    m.CreateFaceVertexCountsAttr([4] * 6)
    m.CreateFaceVertexIndicesAttr([i for f in faces for i in f])
    m.CreateExtentAttr([Gf.Vec3f(-hx, -hy, -hz), Gf.Vec3f(hx, hy, hz)])
    if subdiv:
        m.CreateSubdivisionSchemeAttr(subdiv)
    if crease_sharp is not None:
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
                 (0, 4), (1, 5), (2, 6), (3, 7)]
        m.CreateCreaseIndicesAttr([i for e in edges for i in e])
        m.CreateCreaseLengthsAttr([2] * len(edges))
        m.CreateCreaseSharpnessesAttr([float(crease_sharp)] * len(edges))
    UsdGeom.Xformable(m).AddTranslateOp().Set(Gf.Vec3d(*center))
    if mtl is not None:
        UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mtl)
    return m


def _value_noise(XX, YY, x0, y0, x1, y1, wl, rng):
    """저해상도 격자 난수 → smoothstep 쌍선형 보간 (numpy 만으로 값노이즈)."""
    gx = max(2, int((x1 - x0) / wl) + 1)
    gy = max(2, int((y1 - y0) / wl) + 1)
    g = rng.random((gx + 1, gy + 1)) - 0.5
    fi = np.clip((XX - x0) / (x1 - x0) * gx, 0, gx - 1e-6)
    fj = np.clip((YY - y0) / (y1 - y0) * gy, 0, gy - 1e-6)
    i0, j0 = fi.astype(int), fj.astype(int)
    tx, ty = fi - i0, fj - j0
    sx, sy = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    return ((g[i0, j0] * (1 - sx) + g[i0 + 1, j0] * sx) * (1 - sy)
            + (g[i0, j0 + 1] * (1 - sx) + g[i0 + 1, j0 + 1] * sx) * sy)


def mesh_grid(path, x0, y0, x1, y1, nx, ny, z0, amp_m=0.0, mtl=None,
              seed=7, wavelengths=(0.45, 0.16, 0.06), smooth_normals=True):
    """정점 변위 지면 그리드. amp_m[m] 진폭의 3옥타브 값노이즈.

    MDL displacement 는 RTX 미지원 [ZZ §2 상충4] → 정점으로 우회한다.
    노이즈는 결정적(seed 고정) — 재렌더 재현성 유지.
    smooth_normals=True 면 정점 노멀을 유한차분으로 직접 계산해 넣는다
    (안 넣으면 Hydra 가 face normal 로 그려 저폴리 각짐이 나온다).
    """
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, nx + 1)
    ys = np.linspace(y0, y1, ny + 1)
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    ZZ = np.full_like(XX, float(z0))
    if amp_m > 0:
        for oi, wl in enumerate(wavelengths):
            ZZ += _value_noise(XX, YY, x0, y0, x1, y1, wl, rng) * amp_m * (0.6 ** oi)

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
    if smooth_normals and amp_m > 0:
        dx = (x1 - x0) / nx
        dy = (y1 - y0) / ny
        gzx, gzy = np.gradient(ZZ, dx, dy)
        nrm = np.stack([-gzx, -gzy, np.ones_like(ZZ)], axis=-1)
        nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
        m.CreateNormalsAttr([Gf.Vec3f(*nrm[i, j])
                             for i in range(nx + 1) for j in range(ny + 1)])
        m.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
    if mtl is not None:
        UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mtl)
    return m


# ===========================================================================
# 스테이지 조립
# ===========================================================================
print("[랩] 재질·기하 조립 중 ...")
TP = sc.tex_path
CONCRETE = (TP("concrete_floor", "diff"), TP("concrete_floor", "nor"),
            TP("concrete_floor", "rough"))
GRANITE = (TP("granite_dark", "diff"), TP("granite_dark", "nor"),
           TP("granite_dark", "rough"))
PAVING = (TP("paving_interlock", "diff"), TP("paving_interlock", "nor"),
          TP("paving_interlock", "rough"))

# 랩 바닥 — v1 은 60x60 이라 y=60·80 레인이 바닥 밖으로 나갔다. 240 으로 확대.
M_FLOOR = pbr(f"{ROOT}/Looks/Floor", *CONCRETE, scale_m=2.0)
sc.add_box(stage, f"{ROOT}/Floor", (0, 60, -0.06), (240, 240, 0.1), M_FLOOR)

LANES = {}


def lane(tag, y, views, **extra):
    LANES[tag] = dict(y=y, views=views, **extra)


# --- E1: 가짜 베벨 -----------------------------------------------------------
# 가시성 조건을 넓게 잡는다: ①거친 콘크리트(현장 재질) ②매끈한 화강암
# (roughness 0.22 — 하이라이트가 서는 조건) 두 열을 동시에 놓고,
# ③근접(0.5 m) ④로봇 시점 거리(2 m) 양쪽에서 본다. 어느 조건에서도 안 보이면
# 미지원으로 판정할 근거가 된다.
if want("e1"):
    y = 0.0
    radii_mm = [0.0, 1.0, 2.0, 5.0, 10.0, 20.0]
    for k, rmm in enumerate(radii_mm):
        x = -7.0 + k * 2.8
        m_c = pbr(f"{ROOT}/Looks/BevC_{k}", *CONCRETE, scale_m=1.0,
                  round_edges_radius=rmm / 1000.0)
        m_g = pbr(f"{ROOT}/Looks/BevG_{k}", *GRANITE, scale_m=1.0,
                  roughness_const=0.22, round_edges_radius=rmm / 1000.0)
        sc.add_box(stage, f"{ROOT}/E1_C_{k}", (x, y + 1.4, 0.45),
                   (1.6, 1.6, 0.9), m_c)
        sc.add_box(stage, f"{ROOT}/E1_G_{k}", (x, y - 1.4, 0.45),
                   (1.6, 1.6, 0.9), m_g)
    lane("e1", y, radii_mm=radii_mm, views={
        # 전열 조망 (전 반경 동시)
        "e1_row_concrete": dict(eye=[0.0, y + 7.5, 2.2], tgt=[0.0, y + 1.4, 0.7]),
        "e1_row_granite": dict(eye=[0.0, y - 7.5, 2.2], tgt=[0.0, y - 1.4, 0.7]),
        # 근접 0.6 m — 상단 모서리를 화면 중앙 수평선에 (0 mm vs 20 mm)
        "e1_near_0mm_gran": dict(eye=[-7.0, y - 2.9, 1.05], tgt=[-7.0, y - 2.2, 0.88]),
        "e1_near_20mm_gran": dict(eye=[7.0, y - 2.9, 1.05], tgt=[7.0, y - 2.2, 0.88]),
        "e1_near_5mm_conc": dict(eye=[1.4, y + 2.9, 1.05], tgt=[1.4, y + 2.2, 0.88]),
        # 로봇 시점 거리(2 m)·수직 모서리 — 실제 씬에서 보이는 조건
        "e1_robot_vedge_0": dict(eye=[-8.6, y - 3.4, 0.30], tgt=[-7.4, y - 2.0, 0.45]),
        "e1_robot_vedge_20": dict(eye=[5.4, y - 3.4, 0.30], tgt=[6.6, y - 2.0, 0.45]),
    })

# --- E2: NegObsGround.mdl vs OmniPBR — split-face ----------------------------
# 같은 평면/같은 경사면을 x=0 에서 반으로 갈라 좌 OmniPBR / 우 NegObsGround.
# 한 컷에 두 조건이 들어가므로 조명·시점·스케일이 완전히 통제된다.
if want("e2"):
    y = 30.0
    M_OMNI = pbr(f"{ROOT}/Looks/GndOmni", *CONCRETE, scale_m=1.0)
    M_MDL = ground_mdl(f"{ROOT}/Looks/GndMdl", *CONCRETE, scale_m=1.0)
    for side, m, xc in (("omni", M_OMNI, -3.0), ("mdl", M_MDL, 3.0)):
        # 평면 반쪽 (6 x 14)
        sc.add_box(stage, f"{ROOT}/E2_Flat_{side}", (xc, y, 0.01),
                   (6.0, 14.0, 0.02), m)
        # 경사면 반쪽 — 큐빅 투영 최악 조건(대각 방위 + 급경사)
        sc._oriented_box(stage, f"{ROOT}/E2_Ramp_{side}", (xc, y + 10.0, 1.10),
                         (6.0, 5.0, 0.25), m, rotz=0.0, rotx=38.0)
    lane("e2", y, views={
        # 이음매를 화면 중앙에 두고 지면 충전 (하늘 0)
        "e2_split_robot": dict(eye=[0.0, y - 6.2, 0.30], tgt=[0.0, y + 1.0, 0.02]),
        "e2_split_near": dict(eye=[0.0, y - 1.6, 0.55], tgt=[0.0, y + 0.6, 0.02]),
        "e2_split_top": dict(eye=[0.0, y - 3.0, 3.4], tgt=[0.0, y + 0.5, 0.02]),
        "e2_ramp_split": dict(eye=[0.0, y + 5.6, 1.35], tgt=[0.0, y + 9.6, 1.15]),
        "e2_ramp_grazing": dict(eye=[0.0, y + 6.4, 0.42], tgt=[0.0, y + 10.5, 1.30]),
    })

# --- E3: 디테일 노멀 — split-face -------------------------------------------
if want("e3"):
    y = 60.0
    M_OFF = pbr(f"{ROOT}/Looks/DetOff", *CONCRETE, scale_m=1.5)
    M_ON = pbr(f"{ROOT}/Looks/DetOn", *CONCRETE, scale_m=1.5,
               detail_nor=TP("concrete_wall", "nor"), detail_bump=0.5,
               detail_scale_m=0.08)
    for side, m, xc in (("off", M_OFF, -2.0), ("on", M_ON, 2.0)):
        sc.add_box(stage, f"{ROOT}/E3_Slab_{side}", (xc, y, 0.06),
                   (4.0, 10.0, 0.12), m)
    lane("e3", y, views={
        "e3_split_near": dict(eye=[0.0, y - 1.3, 0.42], tgt=[0.0, y + 0.5, 0.06]),
        "e3_split_robot": dict(eye=[0.0, y - 4.5, 0.30], tgt=[0.0, y + 1.5, 0.06]),
    })

# --- E4: subdiv catmullClark + crease ---------------------------------------
if want("e4"):
    y = 90.0
    M_S = pbr(f"{ROOT}/Looks/Subdiv", *GRANITE, scale_m=1.0, roughness_const=0.25)
    for k, (tag, sub, cr) in enumerate((("none", "none", None),
                                        ("cc", "catmullClark", None),
                                        ("cc_crease", "catmullClark", 4.0))):
        mesh_box(f"{ROOT}/E4_{tag}", (-2.4 + k * 2.4, y, 0.6),
                 (1.4, 1.4, 1.2), M_S, subdiv=sub, crease_sharp=cr)
    lane("e4", y, views={
        "e4_row": dict(eye=[0.0, y - 4.6, 1.5], tgt=[0.0, y, 0.6]),
        "e4_near_cc": dict(eye=[0.0, y - 1.9, 1.1], tgt=[0.0, y - 0.7, 0.85]),
    })

# --- E5: 정점 변위 그리드 -----------------------------------------------------
if want("e5"):
    y = 120.0
    M_G = ground_mdl(f"{ROOT}/Looks/DispGnd", *CONCRETE, scale_m=1.0)
    amps_mm = [0.0, 5.0, 10.0, 20.0]
    for k, amm in enumerate(amps_mm):
        x0 = -9.0 + k * 4.6
        mesh_grid(f"{ROOT}/E5_Grid_{k}", x0, y - 2.0, x0 + 4.2, y + 2.0,
                  nx=200, ny=190, z0=0.02, amp_m=amm / 1000.0, mtl=M_G,
                  seed=11 + k)
    lane("e5", y, amps_mm=amps_mm, views={
        "e5_row": dict(eye=[0.0, y - 6.5, 1.9], tgt=[0.0, y, 0.02]),
        # 스침각 — 미세 기복은 여기서만 읽힌다 (h0.3 로봇 뷰와 같은 조건)
        "e5_grazing_0mm": dict(eye=[-6.9, y - 3.0, 0.16], tgt=[-6.9, y + 2.0, 0.02]),
        "e5_grazing_10mm": dict(eye=[2.3, y - 3.0, 0.16], tgt=[2.3, y + 2.0, 0.02]),
        "e5_grazing_20mm": dict(eye=[6.9, y - 3.0, 0.16], tgt=[6.9, y + 2.0, 0.02]),
    })

# --- E9: 풀스택 예측 실험 (브리프 외 — 감독 추가) ------------------------------
# Phase 2 게이트("flat<8 / slope -2.0~-2.2")를 통과할 수 있는지를 지금 잰다.
# 네 패드를 같은 크기·같은 카메라 오프셋으로 찍어 수치를 직접 비교한다.
#   P0 현행 프로덕션 레시피  : 평면 박스 + OmniPBR(월드 큐빅)
#   P1 + NegObsGround        : 평면 박스 + 소프트 트라이플래너·반복파괴
#   P2 + 정점 변위           : 변위 메시(10 mm) + NegObsGround
#   P3 + 디테일 노멀         : 변위 메시(10 mm) + OmniPBR + detail normal
if want("e9"):
    y = 150.0
    PADS = []
    m0 = pbr(f"{ROOT}/Looks/S_P0", *PAVING, scale_m=1.2)
    m1 = ground_mdl(f"{ROOT}/Looks/S_P1", *PAVING, scale_m=1.2)
    m2 = ground_mdl(f"{ROOT}/Looks/S_P2", *PAVING, scale_m=1.2)
    m3 = pbr(f"{ROOT}/Looks/S_P3", *PAVING, scale_m=1.2,
             detail_nor=TP("concrete_wall", "nor"), detail_bump=0.5,
             detail_scale_m=0.08)
    SPEC = [("P0_omni_flat", m0, 0.0), ("P1_mdl_flat", m1, 0.0),
            ("P2_mdl_disp", m2, 10.0), ("P3_omni_disp_detail", m3, 10.0)]
    for k, (tag, m, amm) in enumerate(SPEC):
        xc = -13.5 + k * 9.0
        if amm <= 0:
            sc.add_box(stage, f"{ROOT}/E9_{tag}", (xc, y, 0.01), (8.0, 12.0, 0.02), m)
        else:
            mesh_grid(f"{ROOT}/E9_{tag}", xc - 4.0, y - 6.0, xc + 4.0, y + 6.0,
                      nx=380, ny=560, z0=0.02, amp_m=amm / 1000.0, mtl=m, seed=29 + k)
        PADS.append((tag, xc))
    v = {}
    for tag, xc in PADS:
        # 지면 충전 · h0.3 로봇 시점 (판정 1순위와 동일 조건)
        v[f"e9_{tag}_robot"] = dict(eye=[xc, y - 5.4, 0.30], tgt=[xc, y + 1.5, 0.02])
        # 지면 충전 · 근접 0.8 m
        v[f"e9_{tag}_near"] = dict(eye=[xc, y - 1.5, 0.60], tgt=[xc, y + 0.6, 0.02])
    lane("e9", y, pads=[t for t, _ in PADS], views=v)

# --- E10: texture_scale 의미 캘리브레이션 (감독 추가) ------------------------
# OmniPBR(큐빅)과 NegObsGround(트라이플래너)는 같은 texture_scale 값에서
# 타일 크기가 같지 않을 수 있다. 이 값을 틀리면 전 지면의 타일 스케일이
# 어긋나는 **전역 회귀**가 되므로 추정 금지 — 직접 잰다.
# 강한 주기성을 가진 인터로킹 보도블록을 같은 scale_m 으로 좌/우에 깔고
# **정사영에 가까운 하향 뷰**로 찍어 픽셀 주기를 비교한다.
if want("e10"):
    y = 180.0
    M_O = pbr(f"{ROOT}/Looks/CalOmni", *PAVING, scale_m=1.0)
    M_M = ground_mdl(f"{ROOT}/Looks/CalMdl", *PAVING, scale_m=1.0,
                     macro_amp=0.0, desat_bright=0.0, rough_noise=0.0,
                     tri_dither=0.0)
    for tag, m, xc in (("omni", M_O, -4.0), ("mdl", M_M, 4.0)):
        sc.add_box(stage, f"{ROOT}/E10_Pad_{tag}", (xc, y, 0.01),
                   (7.6, 7.6, 0.02), m)
    lane("e10", y, views={
        # 거의 수직 하향 — 원근 왜곡 최소화(주기 측정용)
        "e10_cal_omni": dict(eye=[-4.0, y - 0.01, 6.0], tgt=[-4.0, y, 0.02]),
        "e10_cal_mdl": dict(eye=[4.0, y - 0.01, 6.0], tgt=[4.0, y, 0.02]),
    })

print(f"[랩] 레인 {list(LANES)} 조립 완료")

sc.setup_lighting(stage, LIGHT, SUN_AZ_OFFSET)
for _ in range(90):
    sim_app.update()


# ===========================================================================
# 렌더 모드 · 캡처
# ===========================================================================
def set_pt(total_spp, spp=1, subframes=1):
    settings.set("/rtx/pathtracing/spp", int(spp))
    settings.set("/rtx/pathtracing/totalSpp", int(total_spp))
    settings.set("/rtx/pathtracing/optixDenoiser/enabled", True)
    settings.set("/rtx/pathtracing/maxBounces", PT_MAX_BOUNCES)
    settings.set("/app/renderer/rtSubframes", int(subframes))
    settings.set("/rtx/rendermode", "PathTracing")


def set_rt():
    settings.set("/app/renderer/rtSubframes", 1)
    settings.set("/rtx/rendermode", "RaytracedLighting")


def capture(view, fp, warm):
    set_camera_view(eye=[float(v) for v in view["eye"]],
                    target=[float(v) for v in view["tgt"]])
    t0 = time.time()
    for _ in range(warm):
        sim_app.update()
    capture_viewport_to_file(get_active_viewport(), file_path=fp)
    prev = -1
    for _ in range(60):
        sim_app.update()
        if os.path.isfile(fp):
            sz = os.path.getsize(fp)
            if sz > 0 and sz == prev:
                break
            prev = sz
    dt = time.time() - t0
    ok = os.path.isfile(fp) and os.path.getsize(fp) > 0
    print(f"[캡처] {os.path.basename(fp):<40} {dt:6.2f}s {'OK' if ok else 'FAIL'}")
    return dt, ok


PROFILES = []
if MODE in ("rt", "both"):
    PROFILES.append(("rt", set_rt, 90))
if MODE in ("pt", "both"):
    # ZZ §10.3: spp=1 이라 512spp 를 512프레임에 걸쳐 누적 중 → 8프레임 수렴 설정
    PROFILES.append(("ptfast", lambda: set_pt(64, spp=16, subframes=8), 8))

for tag, ln in LANES.items():
    out_dir = os.path.join(OUT_ROOT, f"spike_{tag}")
    os.makedirs(out_dir, exist_ok=True)
    for pname, setter, warm in PROFILES:
        setter()
        for _ in range(12):
            sim_app.update()
        for vname, v in ln["views"].items():
            fp = os.path.join(out_dir, f"{pname}_{vname}.png")
            dt, ok = capture(v, fp, warm)
            RESULTS["experiments"].setdefault(tag, []).append(
                dict(profile=pname, view=vname, file=fp, sec=round(dt, 2), ok=ok))

# ===========================================================================
# E6/E7 — 렌더 예산 실측
# ===========================================================================
if BENCH:
    ln = LANES.get("e9") or LANES.get("e2") or next(iter(LANES.values()), None)
    if ln is None:
        note("E6/E7: 벤치할 레인이 없다 — --only 에 e9 또는 e2 를 포함할 것")
    else:
        # 벤치 뷰는 **고분산 뷰**를 골라야 한다. 평면+하늘 같은 저분산 뷰는
        # 어떤 spp 로도 같은 이미지로 수렴해 "화질 동등"이 자명하게 참이 된다
        # (1차 벤치에서 pt512 와 ptfast 가 비트 단위로 동일하게 나온 원인).
        bvname = _arg("--benchview", "")
        bview = ln["views"].get(bvname) or next(iter(ln["views"].values()))
        print(f"[예산] 벤치 뷰 = {bvname or list(ln['views'])[0]}")
        out_dir = os.path.join(OUT_ROOT, "spike_budget")
        os.makedirs(out_dir, exist_ok=True)
        for bname, setter, warm in (
                ("pt512_legacy", lambda: set_pt(512, spp=1, subframes=1), 572),
                ("ptfast_16_64_8", lambda: set_pt(64, spp=16, subframes=8), 8),
                ("ptfast_16_128_8", lambda: set_pt(128, spp=16, subframes=8), 8),
                ("rt_warm90", set_rt, 90),
                ("rt_warm32", set_rt, 32)):
            setter()
            for _ in range(12):
                sim_app.update()
            secs = []
            for rep in range(2):                       # 2회 중 최소(캐시 편향 제거)
                fp = os.path.join(out_dir, f"{bname}_rep{rep}.png")
                dt, ok = capture(bview, fp, warm)
                secs.append(dt)
            RESULTS["timing"][bname] = dict(
                warmup=warm, sec_per_cut=round(min(secs), 2),
                reps=[round(s, 2) for s in secs])
            print(f"[예산] {bname:<18} {min(secs):6.2f} s/컷 (warmup={warm})")

rp = os.path.join(OUT_ROOT, "spike_results.json")
prev = {}
if os.path.isfile(rp):
    try:
        with open(rp) as f:
            prev = json.load(f)
    except Exception:
        pass
prev.setdefault("experiments", {}).update(RESULTS["experiments"])
prev.setdefault("timing", {}).update(RESULTS["timing"])
prev["notes"] = (prev.get("notes", []) + RESULTS["notes"])[-40:]
with open(rp, "w") as f:
    json.dump(prev, f, indent=2, ensure_ascii=False)
print(f"\n[결과] {rp}")
sim_app.close()
