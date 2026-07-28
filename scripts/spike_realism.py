#!/usr/bin/env python3
"""Phase 1 "검증의 날" — 사실화 재료 실동작 스파이크 랩.

`Docs/briefs/realism_brief_v1.md` Phase 1 의 실험 1~7 을 **부팅 1회**로 전부
수행한다(씬마다 부팅하면 부팅 시간이 실험 시간을 넘는다). 실험별 A/B 이미지는
`look_check/spike_<이름>/` 에 저장되고, 타이밍 실측은 JSON 으로 남는다.

실험:
  E1 bevel     : OmniPBR `round_edges_radius` 0/2/5/10 mm 스윕      [ZZ §2 상충4 — 미검증]
  E2 ground    : `NegObsGround.mdl` vs OmniPBR 동일 텍스처 A/B      [ZZ §1 결정적 발견]
  E3 detail    : `detail_normalmap_texture` + `detail_bump_factor`  [ZZ §2 — 로컬검증됨]
  E4 subdiv    : `subdivisionScheme=catmullClark` + crease           [ZZ §6 T0-2 — 미검증]
  E5 displace  : 정점 변위 그리드 메시 5/10/20 mm                    [MDL displacement 는 RTX 미지원]
  E6/E7 budget : PT 수정설정(spp16/totalSpp64/subframes8) vs PT 512 vs RT90 vs RT32 s/컷 실측

실행 (반드시 cd 포함 스크립트로 — 백그라운드 셸 cwd 리셋 함정):
  python scripts/spike_realism.py                 # 전부
  python scripts/spike_realism.py --only e1,e2    # 일부
  python scripts/spike_realism.py --mode rt       # 빠른 확인(기본 both)
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

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------
ARGS = sys.argv[1:]


def _arg(name, default):
    if name in ARGS:
        return ARGS[ARGS.index(name) + 1]
    return default


ONLY = {s.strip().lower() for s in _arg("--only", "").split(",") if s.strip()}
MODE = _arg("--mode", "both")                          # rt | pt | both
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


# ---------------------------------------------------------------------------
# 부팅 (SimulationApp 이 먼저, 나머지 import 는 그 다음 — sc.boot 규약)
# ---------------------------------------------------------------------------
print("=" * 70)
print("Phase 1 스파이크 랩 — 부팅")
print("=" * 70)
sim_app = sc.boot(True)

import carb                                            # noqa: E402
import omni.usd                                        # noqa: E402
from pxr import UsdGeom, UsdShade, Sdf, Gf, Vt         # noqa: E402
from omni.kit.viewport.utility import (                # noqa: E402
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


# ---------------------------------------------------------------------------
# 재질 팩토리 — make_pbr 의 스파이크 확장판 (본체는 아직 안 건드린다)
# ---------------------------------------------------------------------------
def pbr(path, diff=None, nor=None, rough=None, scale_m=1.0,
        diffuse_color=None, roughness_const=None, bump=1.0,
        round_edges_radius=None, round_edges_roundness=1.0,
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
        if rough is not None:
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
    sh.CreateInput("metallic_constant", F).Set(0.0)
    # --- E1: 가짜 베벨 ---
    if round_edges_radius is not None:
        sh.CreateInput("round_edges_radius", F).Set(float(round_edges_radius))
        sh.CreateInput("round_edges_roundness", F).Set(float(round_edges_roundness))
        sh.CreateInput("round_edges_across_materials", B).Set(False)
    # --- E3: 디테일 노멀 (근접 텍셀 뭉개짐) ---
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
    """NegObsGround.mdl — 소프트 트라이플래너 + 반복파괴. TerrainGen 사용례 이식.

    OmniPBR 의 project_uvw 는 트라이플래너가 아니라 **큐빅 투영**이라
    경사면에서 축 전환 이음매가 난다 [ZZ §10.5]. 이 MDL 이 그 대체재다.
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
    sh.CreateInput("macro_amp_a", F).Set(float(macro_amp))
    sh.CreateInput("macro_wavelength_a", F).Set(float(macro_wl))
    sh.CreateInput("patch_wavelength_a", F).Set(float(patch_wl))
    sh.CreateInput("desat_bright_a", F).Set(float(desat_bright))
    sh.CreateInput("rough_noise_a", F).Set(float(rough_noise))
    sh.CreateInput("rough_noise_wavelength_a", F).Set(float(rough_noise_wl))
    sh.CreateInput("rough_floor_a", F).Set(float(rough_floor))
    sh.CreateInput("rough_mult_a", F).Set(float(rough_mult))
    sh.CreateInput("bump_factor_a", F).Set(float(bump))
    sh.CreateInput("use_blend", B).Set(False)
    sh.CreateInput("tri_dither", F).Set(float(tri_dither))
    sh.CreateInput("tri_dither_wavelength", F).Set(float(tri_dither_wl))
    sh.CreateInput("tri_weight_exp", F).Set(float(tri_weight_exp))
    for out in ("surface", "displacement", "volume"):
        mtl.CreateOutput(f"mdl:{out}", Sdf.ValueTypeNames.Token).ConnectToSource(
            sh.ConnectableAPI(), "out")
    return mtl


# ---------------------------------------------------------------------------
# 메시 유틸 — E4(subdiv) / E5(정점 변위)
# ---------------------------------------------------------------------------
def mesh_box(path, center, size, mtl=None, subdiv=None, crease_sharp=None):
    """8정점 박스 메시. subdiv="catmullClark"|"none", crease_sharp 지정 시
    12 모서리 전부에 crease 부여(날카로움 유지하며 면만 세분)."""
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
    UsdGeom.Xformable(m).AddScaleOp().Set(Gf.Vec3f(1, 1, 1))
    if mtl is not None:
        UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mtl)
    return m


def mesh_grid(path, x0, y0, x1, y1, nx, ny, z0, amp_m=0.0, mtl=None,
              seed=7, wavelengths=(0.35, 0.11)):
    """정점 변위 지면 그리드. amp_m[m] 진폭의 2옥타브 값노이즈.

    MDL displacement 는 RTX 미지원 [ZZ §2 상충4] → 정점으로 우회한다.
    노이즈는 결정적(seed 고정) — 재렌더 재현성 유지.
    """
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, nx + 1)
    ys = np.linspace(y0, y1, ny + 1)
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    ZZ = np.full_like(XX, float(z0))
    if amp_m > 0:
        for oi, wl in enumerate(wavelengths):
            # 저해상도 격자 노이즈 → 쌍선형 업샘플 (numpy 만으로 값노이즈)
            gx = max(2, int((x1 - x0) / wl) + 1)
            gy = max(2, int((y1 - y0) / wl) + 1)
            g = rng.random((gx + 1, gy + 1)) - 0.5
            fi = np.clip((XX - x0) / (x1 - x0) * gx, 0, gx - 1e-6)
            fj = np.clip((YY - y0) / (y1 - y0) * gy, 0, gy - 1e-6)
            i0, j0 = fi.astype(int), fj.astype(int)
            tx, ty = fi - i0, fj - j0
            sx, sy = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)   # smoothstep
            v = ((g[i0, j0] * (1 - sx) + g[i0 + 1, j0] * sx) * (1 - sy)
                 + (g[i0, j0 + 1] * (1 - sx) + g[i0 + 1, j0 + 1] * sx) * sy)
            ZZ += v * amp_m * (0.65 ** oi)
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
    if mtl is not None:
        UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mtl)
    return m


# ---------------------------------------------------------------------------
# 스테이지 조립 — 실험은 y 로 레인 분리 (한 번에 조명·부팅 공유)
# ---------------------------------------------------------------------------
print("[랩] 재질·기하 조립 중 ...")
TP = sc.tex_path
CONCRETE = (TP("concrete_floor", "diff"), TP("concrete_floor", "nor"),
            TP("concrete_floor", "rough"))
GRANITE = (TP("granite_dark", "diff"), TP("granite_dark", "nor"),
           TP("granite_dark", "rough"))

# 랩 바닥 (전 실험 공통) — 중립 콘크리트, OmniPBR
M_FLOOR = pbr(f"{ROOT}/Looks/Floor", *CONCRETE, scale_m=2.0)
sc.add_box(stage, f"{ROOT}/Floor", (0, 0, -0.05), (60, 60, 0.1), M_FLOOR)

LANES = {}      # 실험 → (y 중심, 뷰 리스트)

# --- E1: 가짜 베벨 스윕 ------------------------------------------------------
if want("e1"):
    y = 0.0
    radii_mm = [0.0, 2.0, 5.0, 10.0]
    for k, rmm in enumerate(radii_mm):
        x = -3.0 + k * 2.0
        m = pbr(f"{ROOT}/Looks/Bevel_{k}", *CONCRETE, scale_m=1.0,
                round_edges_radius=rmm / 1000.0)
        sc.add_box(stage, f"{ROOT}/E1_Bevel_{k}", (x, y, 0.5), (1.2, 1.2, 1.0), m)
    LANES["e1"] = dict(
        radii_mm=radii_mm,
        views={
            "e1_sweep": dict(eye=[0.0, y - 5.5, 1.35], tgt=[0.0, y, 0.55]),
            "e1_closeup_5mm": dict(eye=[1.0, y - 1.6, 1.25], tgt=[1.0, y - 0.6, 0.95]),
            "e1_grazing": dict(eye=[-4.6, y - 2.2, 0.62], tgt=[3.0, y - 0.2, 0.55]),
        })

# --- E2: NegObsGround.mdl vs OmniPBR ----------------------------------------
if want("e2"):
    y = 20.0
    # 동일 텍스처·동일 scale_m, 재질만 교체. 경사면을 포함해야 큐빅 투영의
    # 축 전환 이음매가 드러난다 → 각 패드에 15°/35° 경사 웨지 동반.
    M_A = pbr(f"{ROOT}/Looks/GndOmni", *CONCRETE, scale_m=1.0)
    M_B = ground_mdl(f"{ROOT}/Looks/GndMdl", *CONCRETE, scale_m=1.0)
    for tag, m, x in (("omni", M_A, -4.0), ("mdl", M_B, 4.0)):
        sc.add_box(stage, f"{ROOT}/E2_Pad_{tag}", (x, y, 0.01), (7.0, 7.0, 0.02), m)
        # 경사 웨지 2매 (대각 방위 — 큐빅 투영 최악 조건)
        for wi, (ang, yy) in enumerate(((15.0, y + 2.2), (35.0, y - 2.2))):
            sc._oriented_box(stage, f"{ROOT}/E2_Wedge_{tag}_{wi}",
                             (x, yy, 0.45), (3.0, 1.6, 0.12), m,
                             rotz=37.0, rotx=ang)
    LANES["e2"] = dict(views={
        "e2_ab_overview": dict(eye=[0.0, y - 9.0, 3.2], tgt=[0.0, y, 0.4]),
        "e2_grazing_omni": dict(eye=[-4.0, y - 6.0, 0.30], tgt=[-4.0, y + 1.0, 0.15]),
        "e2_grazing_mdl": dict(eye=[4.0, y - 6.0, 0.30], tgt=[4.0, y + 1.0, 0.15]),
        "e2_wedge_omni": dict(eye=[-4.0, y - 2.0, 1.5], tgt=[-4.0, y + 2.2, 0.5]),
        "e2_wedge_mdl": dict(eye=[4.0, y - 2.0, 1.5], tgt=[4.0, y + 2.2, 0.5]),
    })

# --- E3: 디테일 노멀 ---------------------------------------------------------
if want("e3"):
    y = 40.0
    M_N = pbr(f"{ROOT}/Looks/DetOff", *CONCRETE, scale_m=1.5)
    M_D = pbr(f"{ROOT}/Looks/DetOn", *CONCRETE, scale_m=1.5,
              detail_nor=TP("concrete_wall", "nor"), detail_bump=0.45,
              detail_scale_m=0.10)
    for tag, m, x in (("off", M_N, -1.6), ("on", M_D, 1.6)):
        sc.add_box(stage, f"{ROOT}/E3_Slab_{tag}", (x, y, 0.15), (2.6, 4.0, 0.3), m)
    LANES["e3"] = dict(views={
        "e3_ab_closeup": dict(eye=[0.0, y - 2.6, 0.55], tgt=[0.0, y - 0.2, 0.30]),
        "e3_ab_grazing": dict(eye=[0.0, y - 4.2, 0.34], tgt=[0.0, y + 1.5, 0.30]),
    })

# --- E4: subdiv catmullClark + crease ---------------------------------------
if want("e4"):
    y = 60.0
    M_S = pbr(f"{ROOT}/Looks/Subdiv", *GRANITE, scale_m=1.0)
    mesh_box(f"{ROOT}/E4_None", (-2.2, y, 0.6), (1.2, 1.2, 1.2), M_S, subdiv="none")
    mesh_box(f"{ROOT}/E4_CC", (0.0, y, 0.6), (1.2, 1.2, 1.2), M_S,
             subdiv="catmullClark")
    mesh_box(f"{ROOT}/E4_CC_Crease", (2.2, y, 0.6), (1.2, 1.2, 1.2), M_S,
             subdiv="catmullClark", crease_sharp=4.0)
    LANES["e4"] = dict(views={
        "e4_ab": dict(eye=[0.0, y - 5.0, 1.6], tgt=[0.0, y, 0.6]),
        "e4_closeup": dict(eye=[1.1, y - 2.0, 1.1], tgt=[1.1, y - 0.6, 0.85]),
    })

# --- E5: 정점 변위 지면 -------------------------------------------------------
if want("e5"):
    y = 80.0
    M_G = ground_mdl(f"{ROOT}/Looks/DispGnd", *CONCRETE, scale_m=1.0)
    amps_mm = [0.0, 5.0, 10.0, 20.0]
    for k, amm in enumerate(amps_mm):
        x0 = -8.0 + k * 4.2
        mesh_grid(f"{ROOT}/E5_Grid_{k}", x0, y - 1.8, x0 + 3.8, y + 1.8,
                  nx=160, ny=150, z0=0.02, amp_m=amm / 1000.0, mtl=M_G, seed=11 + k)
    LANES["e5"] = dict(amps_mm=amps_mm, views={
        "e5_sweep": dict(eye=[0.0, y - 7.5, 2.0], tgt=[0.0, y, 0.02]),
        "e5_grazing": dict(eye=[-11.0, y - 0.4, 0.18], tgt=[9.0, y + 0.2, 0.02]),
    })

print(f"[랩] 레인 {list(LANES)} 조립 완료")

# ---------------------------------------------------------------------------
# 조명 (본편과 동일 조건)
# ---------------------------------------------------------------------------
sc.setup_lighting(stage, LIGHT, SUN_AZ_OFFSET)

for _ in range(60):                                    # 에셋 로딩 워밍업
    sim_app.update()


# ---------------------------------------------------------------------------
# 렌더 모드 · 캡처
# ---------------------------------------------------------------------------
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
    for _ in range(60):                                # 캡처는 비동기
        sim_app.update()
        if os.path.isfile(fp):
            sz = os.path.getsize(fp)
            if sz > 0 and sz == prev:
                break
            prev = sz
    dt = time.time() - t0
    ok = os.path.isfile(fp) and os.path.getsize(fp) > 0
    print(f"[캡처] {os.path.basename(fp):<34} {dt:6.2f}s {'OK' if ok else 'FAIL'}")
    return dt, ok


PROFILES = []
if MODE in ("rt", "both"):
    PROFILES.append(("rt", lambda: set_rt(), 90))
if MODE in ("pt", "both"):
    # ZZ §10.3: spp=1 이라 512spp 를 512프레임에 걸쳐 누적 중 → 8프레임 수렴 설정
    PROFILES.append(("ptfast", lambda: set_pt(64, spp=16, subframes=8), 8))

for tag, lane in LANES.items():
    out_dir = os.path.join(OUT_ROOT, f"spike_{tag}")
    os.makedirs(out_dir, exist_ok=True)
    for pname, setter, warm in PROFILES:
        setter()
        for _ in range(10):
            sim_app.update()
        for vname, v in lane["views"].items():
            fp = os.path.join(out_dir, f"{pname}_{vname}.png")
            dt, ok = capture(v, fp, warm)
            RESULTS["experiments"].setdefault(tag, []).append(
                dict(profile=pname, view=vname, file=fp, sec=round(dt, 2), ok=ok))

# ---------------------------------------------------------------------------
# E6/E7 — 렌더 예산 실측 (같은 뷰를 4개 프로파일로)
# ---------------------------------------------------------------------------
if want("e6") or want("e7"):
    bench_lane = LANES.get("e2") or next(iter(LANES.values()), None)
    if bench_lane is None:
        note("E6/E7: 벤치할 레인이 없어 생략(--only 로 e2 이상 포함 필요)")
    else:
        bview = next(iter(bench_lane["views"].values()))
        out_dir = os.path.join(OUT_ROOT, "spike_budget")
        os.makedirs(out_dir, exist_ok=True)
        BENCH = [
            ("pt512_legacy", lambda: set_pt(512, spp=1, subframes=1), 572),
            ("ptfast_16_64_8", lambda: set_pt(64, spp=16, subframes=8), 8),
            ("rt_warm90", lambda: set_rt(), 90),
            ("rt_warm32", lambda: set_rt(), 32),
        ]
        for bname, setter, warm in BENCH:
            setter()
            for _ in range(10):
                sim_app.update()
            secs = []
            for rep in range(2):                       # 2회 평균(첫 회 캐시 편향)
                fp = os.path.join(out_dir, f"{bname}_rep{rep}.png")
                dt, ok = capture(bview, fp, warm)
                secs.append(dt)
            RESULTS["timing"][bname] = dict(
                warmup=warm, sec_per_cut=round(min(secs), 2),
                reps=[round(s, 2) for s in secs])
            print(f"[예산] {bname:<16} {min(secs):6.2f} s/컷 (warmup={warm})")

# ---------------------------------------------------------------------------
# 마무리
# ---------------------------------------------------------------------------
rp = os.path.join(OUT_ROOT, "spike_results.json")
with open(rp, "w") as f:
    json.dump(RESULTS, f, indent=2, ensure_ascii=False)
print(f"\n[결과] {rp}")
for n in RESULTS["notes"]:
    print(f"  - {n}")
sim_app.close()
