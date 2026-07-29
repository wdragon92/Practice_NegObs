#!/usr/bin/env python3
"""Phase 1 "verification day" — spike lab exercising the realism ingredients
for real (v2 split-face).

Runs the Phase 1 experiments of `Docs/briefs/realism_brief_v1.md` in **a single
boot**.

## Why v1 was redesigned into v2 (supervisor, after the first render)
v1 placed a separate object per experiment at a different position and shot
each with a different camera. As a result (1) half the frame was sky, so flat%
was contaminated by the sky, and (2) the A/B pair differed in lighting,
viewpoint and distance, so nothing was controlled. v2 changes two things:

1. **split-face**: A and B are laid out by **splitting one continuous surface
   in half**. With the seam at frame centre, a single shot contains both
   conditions, so lighting, viewpoint, distance and material scale are fully
   controlled. Any visible difference is the material difference alone.
2. **ground-filling framing**: diagnostic views are framed so the sky is zero.
   Only then do `scripts/imgstats.py`'s flat%/slope reflect surface
   microstructure alone. Distances cover both the primary judging viewpoint
   (h0.3 robot view) and a close view (0.5~1.2 m).

## Experiments
  E1 bevel   : `round_edges_radius` 0/1/2/5/10/20 mm     [ZZ §2 conflict 4 — unverified]
  E2 ground  : `NegObsGround.mdl` vs OmniPBR **split-face** [ZZ §1 decisive finding]
  E3 detail  : `detail_normalmap_texture` split-face      [ZZ §2 — verified locally]
  E4 subdiv  : `catmullClark` + crease                    [ZZ §6 T0-2 — unverified]
  E5 disp    : vertex-displacement grid 0/5/10/20 mm      [MDL displacement unsupported on RTX]
  **E9 stack : full-stack prediction experiment (outside the brief — supervisor addition)**
      P0 current production recipe (flat box + OmniPBR) / P1 +NegObsGround /
      P2 +vertex-displaced mesh / P3 +detail normal (OmniPBR family)
      -> **measures during Phase 1** whether the Phase 2 gate can be passed.
      All are shot at the same size and view, so flat%/slope compare directly.
  E6/E7 budget : measured s/cut for the revised PT settings vs PT 512 vs RT90 vs RT32

Run (always via a script that includes the cd — background shells reset cwd):
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

# Character-for-character the same lighting as the main 21 scenes (scene01 §5)
# — the controlled variable for A/B
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
# Material factories
# ===========================================================================
def pbr(path, diff=None, nor=None, rough=None, scale_m=1.0,
        diffuse_color=None, roughness_const=None, bump=1.0,
        round_edges_radius=None, round_edges_roundness=1.0,
        round_edges_across=False,
        detail_nor=None, detail_bump=None, detail_scale_m=None):
    """OmniPBR — same convention as sc.make_pbr, plus bevel / detail-normal args."""
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
    """NegObsGround.mdl — soft triplanar + tiling breakup (ported from the
    TerrainGen use case).

    OmniPBR's project_uvw is not triplanar but a **cubic projection**, so
    slopes show an axis-switch seam [ZZ §10.5]. This MDL replaces it.
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
# Mesh utilities
# ===========================================================================
def mesh_box(path, center, size, mtl=None, subdiv=None, crease_sharp=None):
    """8-vertex box mesh. If crease_sharp is given, all 12 edges get a crease."""
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
    """Low-resolution lattice of random values -> smoothstep bilinear
    interpolation (value noise using numpy alone)."""
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
    """Vertex-displaced ground grid. 3-octave value noise of amplitude amp_m [m].

    MDL displacement is unsupported on RTX [ZZ §2 conflict 4] -> work around it
    with vertices. The noise is deterministic (fixed seed) to keep re-renders
    reproducible.
    With smooth_normals=True the vertex normals are computed directly by finite
    differences and written out (without them Hydra draws face normals, giving
    a faceted low-poly look).
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
# Stage assembly
# ===========================================================================
print("[랩] 재질·기하 조립 중 ...")
TP = sc.tex_path
CONCRETE = (TP("concrete_floor", "diff"), TP("concrete_floor", "nor"),
            TP("concrete_floor", "rough"))
GRANITE = (TP("granite_dark", "diff"), TP("granite_dark", "nor"),
           TP("granite_dark", "rough"))
PAVING = (TP("paving_interlock", "diff"), TP("paving_interlock", "nor"),
          TP("paving_interlock", "rough"))

# Lab floor — v1 was 60x60, so the y=60 and y=80 lanes fell off it. Widened to 240.
M_FLOOR = pbr(f"{ROOT}/Looks/Floor", *CONCRETE, scale_m=2.0)
sc.add_box(stage, f"{ROOT}/Floor", (0, 60, -0.06), (240, 240, 0.1), M_FLOOR)

LANES = {}


def lane(tag, y, views, **extra):
    LANES[tag] = dict(y=y, views=views, **extra)


# --- E1: fake bevel ----------------------------------------------------------
# Cast the visibility conditions wide: place two rows at once, (1) rough
# concrete (the on-site material) and (2) smooth granite (roughness 0.22 — the
# condition where a highlight forms), and view both from (3) close range
# (0.5 m) and (4) robot-view distance (2 m). If it is invisible under every
# condition, that is grounds for ruling it unsupported.
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
        # whole-row view (every radius at once)
        "e1_row_concrete": dict(eye=[0.0, y + 7.5, 2.2], tgt=[0.0, y + 1.4, 0.7]),
        "e1_row_granite": dict(eye=[0.0, y - 7.5, 2.2], tgt=[0.0, y - 1.4, 0.7]),
        # close 0.6 m — top edge on the frame's centre horizon (0 mm vs 20 mm)
        "e1_near_0mm_gran": dict(eye=[-7.0, y - 2.9, 1.05], tgt=[-7.0, y - 2.2, 0.88]),
        "e1_near_20mm_gran": dict(eye=[7.0, y - 2.9, 1.05], tgt=[7.0, y - 2.2, 0.88]),
        "e1_near_5mm_conc": dict(eye=[1.4, y + 2.9, 1.05], tgt=[1.4, y + 2.2, 0.88]),
        # robot-view distance (2 m), vertical edge — the condition seen in real scenes
        "e1_robot_vedge_0": dict(eye=[-8.6, y - 3.4, 0.30], tgt=[-7.4, y - 2.0, 0.45]),
        "e1_robot_vedge_20": dict(eye=[5.4, y - 3.4, 0.30], tgt=[6.6, y - 2.0, 0.45]),
    })

# --- E2: NegObsGround.mdl vs OmniPBR — split-face ----------------------------
# Split the same plane / same slope in half at x=0: left OmniPBR, right
# NegObsGround. One shot holds both conditions, so lighting, viewpoint and
# scale are fully controlled.
if want("e2"):
    y = 30.0
    M_OMNI = pbr(f"{ROOT}/Looks/GndOmni", *CONCRETE, scale_m=1.0)
    M_MDL = ground_mdl(f"{ROOT}/Looks/GndMdl", *CONCRETE, scale_m=1.0)
    for side, m, xc in (("omni", M_OMNI, -3.0), ("mdl", M_MDL, 3.0)):
        # flat half (6 x 14)
        sc.add_box(stage, f"{ROOT}/E2_Flat_{side}", (xc, y, 0.01),
                   (6.0, 14.0, 0.02), m)
        # slope half — worst case for cubic projection (diagonal bearing + steep grade)
        sc._oriented_box(stage, f"{ROOT}/E2_Ramp_{side}", (xc, y + 10.0, 1.10),
                         (6.0, 5.0, 0.25), m, rotz=0.0, rotx=38.0)
    lane("e2", y, views={
        # seam at frame centre, ground-filling (zero sky)
        "e2_split_robot": dict(eye=[0.0, y - 6.2, 0.30], tgt=[0.0, y + 1.0, 0.02]),
        "e2_split_near": dict(eye=[0.0, y - 1.6, 0.55], tgt=[0.0, y + 0.6, 0.02]),
        "e2_split_top": dict(eye=[0.0, y - 3.0, 3.4], tgt=[0.0, y + 0.5, 0.02]),
        "e2_ramp_split": dict(eye=[0.0, y + 5.6, 1.35], tgt=[0.0, y + 9.6, 1.15]),
        "e2_ramp_grazing": dict(eye=[0.0, y + 6.4, 0.42], tgt=[0.0, y + 10.5, 1.30]),
    })

# --- E3: detail normal — split-face -----------------------------------------
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

# --- E5: vertex-displacement grid --------------------------------------------
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
        # grazing angle — fine relief only reads here (same condition as the h0.3 robot view)
        "e5_grazing_0mm": dict(eye=[-6.9, y - 3.0, 0.16], tgt=[-6.9, y + 2.0, 0.02]),
        "e5_grazing_10mm": dict(eye=[2.3, y - 3.0, 0.16], tgt=[2.3, y + 2.0, 0.02]),
        "e5_grazing_20mm": dict(eye=[6.9, y - 3.0, 0.16], tgt=[6.9, y + 2.0, 0.02]),
    })

# --- E9: full-stack prediction experiment (outside the brief — supervisor addition) ---
# Measure now whether the Phase 2 gate ("flat<8 / slope -2.0~-2.2") is passable.
# Four pads are shot at the same size and camera offset so the numbers compare
# directly.
#   P0 current production recipe : flat box + OmniPBR (world cubic)
#   P1 + NegObsGround            : flat box + soft triplanar, tiling breakup
#   P2 + vertex displacement     : displaced mesh (10 mm) + NegObsGround
#   P3 + detail normal           : displaced mesh (10 mm) + OmniPBR + detail normal
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
        # ground-filling, h0.3 robot view (identical to the primary judging condition)
        v[f"e9_{tag}_robot"] = dict(eye=[xc, y - 5.4, 0.30], tgt=[xc, y + 1.5, 0.02])
        # ground-filling, close 0.8 m
        v[f"e9_{tag}_near"] = dict(eye=[xc, y - 1.5, 0.60], tgt=[xc, y + 0.6, 0.02])
    lane("e9", y, pads=[t for t, _ in PADS], views=v)

# --- E10: calibrating what texture_scale means (supervisor addition) ---------
# OmniPBR (cubic) and NegObsGround (triplanar) may not produce the same tile
# size for the same texture_scale value. Getting this wrong is a **global
# regression** that throws off tile scale across every ground surface, so no
# guessing — measure it directly.
# Lay strongly periodic interlocking paving on the left and right at the same
# scale_m and shoot a **near-orthographic top-down view** to compare pixel
# periods.
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
        # nearly straight down — minimizes perspective distortion (for period measurement)
        "e10_cal_omni": dict(eye=[-4.0, y - 0.01, 6.0], tgt=[-4.0, y, 0.02]),
        "e10_cal_mdl": dict(eye=[4.0, y - 0.01, 6.0], tgt=[4.0, y, 0.02]),
    })

print(f"[랩] 레인 {list(LANES)} 조립 완료")

sc.setup_lighting(stage, LIGHT, SUN_AZ_OFFSET)
for _ in range(90):
    sim_app.update()


# ===========================================================================
# Render modes and capture
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
    # ZZ §10.3: with spp=1, 512spp accumulates over 512 frames -> settings that
    # converge in 8 frames instead
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
# E6/E7 — measured render budget
# ===========================================================================
if BENCH:
    ln = LANES.get("e9") or LANES.get("e2") or next(iter(LANES.values()), None)
    if ln is None:
        note("E6/E7: 벤치할 레인이 없다 — --only 에 e9 또는 e2 를 포함할 것")
    else:
        # The bench view must be a **high-variance view**. A low-variance view
        # such as flat ground plus sky converges to the same image at any spp,
        # making "equal image quality" trivially true (this is why pt512 and
        # ptfast came out bit-identical in the first bench).
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
            for rep in range(2):                       # min of 2 runs (removes cache bias)
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
