#!/usr/bin/env python3
"""Measured dump of RTX settings + subdiv confirmation experiment.

Phase 1 follow-up. H_rtx_capability_verification.md drew its conclusions from
source and binary evidence; this script pins down, by measurement, the subset
of those conclusions that **depends on runtime defaults**.

  (1) Dump the `/rtx` and `/app/renderer` setting trees to JSON (settles the
      argument over what the defaults actually are).
  (2) Subdiv confirmation: render the same catmullClark box at refinementLevel
      0/2/4.
      - If the image does not change -> no subdivision actually happened, and
        the "rounding" seen in E4 was **smooth normal shading** (the Phase 1
        report's E4 verdict then needs correcting).
      - If it does change -> subdivision is real and requires refinementLevel
        to be turned on.

Run: bash run_p1_probe.sh
"""
import os
import sys
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

import scene_common as sc                              # noqa: E402

OUT = os.path.join(_ROOT, "look_check", "spike_probe")
os.makedirs(OUT, exist_ok=True)

sim_app = sc.boot(True)

import carb                                            # noqa: E402
import omni.usd                                        # noqa: E402
from pxr import UsdGeom, UsdShade, Sdf, Gf              # noqa: E402
from omni.kit.viewport.utility import (                 # noqa: E402
    get_active_viewport, capture_viewport_to_file)
from isaacsim.core.utils.viewports import set_camera_view  # noqa: E402

stage = omni.usd.get_context().get_stage()
settings = carb.settings.get_settings()

# ---------------------------------------------------------------------------
# (1) Settings dump
# ---------------------------------------------------------------------------
KEYS = [
    "/rtx/rendermode",
    "/rtx/pathtracing/spp", "/rtx/pathtracing/totalSpp",
    "/rtx/pathtracing/maxBounces",
    "/rtx/pathtracing/optixDenoiser/enabled",
    "/rtx/post/dlss/execMode", "/rtx/post/aa/op",
    "/rtx/post/tonemap/op", "/rtx/post/tonemap/filmIso",
    "/rtx/post/tonemap/cameraShutter", "/rtx/post/tonemap/fNumber",
    "/rtx/post/tonemap/whitePoint",
    "/rtx/hydra/subdivision/refinementLevel",
    "/rtx/hydra/subdivision/adaptiveRefinement",
    "/rtx/hydra/TBNFrameMode",
    "/rtx/displacement/enabled", "/rtx/displacement/maxSubdiv",
    "/rtx/domeLight/upperLowerStrategy",
    "/app/renderer/rtSubframes",
    "/app/renderer/skipWhileMinimized",
]
dump = {}
for k in KEYS:
    try:
        dump[k] = settings.get(k)
    except Exception as e:
        dump[k] = f"<error {e}>"
print("=" * 70)
print("① RTX 설정 실측")
print("=" * 70)
for k, v in dump.items():
    print(f"  {k:48} = {v!r}")

# ---------------------------------------------------------------------------
# (2) Subdiv confirmation experiment
# ---------------------------------------------------------------------------
ROOT = "/World/Probe"
UsdGeom.Xform.Define(stage, ROOT)


def pbr(path, diff, nor, rough, scale_m=1.0, roughness_const=None):
    mtl = UsdShade.Material.Define(stage, path)
    sh = UsdShade.Shader.Define(stage, path + "/Shader")
    sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
    sh.SetSourceAsset(Sdf.AssetPath(sc.OMNIPBR_PATH), "mdl")
    sh.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
    F, A, B, F2 = (Sdf.ValueTypeNames.Float, Sdf.ValueTypeNames.Asset,
                   Sdf.ValueTypeNames.Bool, Sdf.ValueTypeNames.Float2)

    def tex(n, p, cs):
        i = sh.CreateInput(n, A)
        i.Set(p)
        try:
            i.GetAttr().SetColorSpace(cs)
        except Exception:
            pass

    tex("diffuse_texture", diff, "auto")
    tex("normalmap_texture", nor, "raw")
    sh.CreateInput("project_uvw", B).Set(True)
    sh.CreateInput("world_or_object", B).Set(True)
    s = 1.0 / scale_m
    sh.CreateInput("texture_scale", F2).Set(Gf.Vec2f(s, s))
    if roughness_const is not None:
        sh.CreateInput("reflection_roughness_constant", F).Set(roughness_const)
    for out in ("surface", "displacement", "volume"):
        mtl.CreateOutput(f"mdl:{out}", Sdf.ValueTypeNames.Token).ConnectToSource(
            sh.ConnectableAPI(), "out")
    return mtl


TP = sc.tex_path
M = pbr(f"{ROOT}/Looks/G", TP("granite_dark", "diff"), TP("granite_dark", "nor"),
        None, 1.0, roughness_const=0.25)
MF = pbr(f"{ROOT}/Looks/F", TP("concrete_floor", "diff"),
         TP("concrete_floor", "nor"), None, 2.0)
sc.add_box(stage, f"{ROOT}/Floor", (0, 0, -0.06), (60, 60, 0.1), MF)


def box_mesh(path, cx, subdiv, crease=None):
    m = UsdGeom.Mesh.Define(stage, path)
    h = 0.6
    pts = [(-h, -h, -h), (h, -h, -h), (h, h, -h), (-h, h, -h),
           (-h, -h, h), (h, -h, h), (h, h, h), (-h, h, h)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    m.CreatePointsAttr([Gf.Vec3f(*p) for p in pts])
    m.CreateFaceVertexCountsAttr([4] * 6)
    m.CreateFaceVertexIndicesAttr([i for f in faces for i in f])
    m.CreateExtentAttr([Gf.Vec3f(-h, -h, -h), Gf.Vec3f(h, h, h)])
    m.CreateSubdivisionSchemeAttr(subdiv)
    if crease is not None:
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
                 (0, 4), (1, 5), (2, 6), (3, 7)]
        m.CreateCreaseIndicesAttr([i for e in edges for i in e])
        m.CreateCreaseLengthsAttr([2] * len(edges))
        m.CreateCreaseSharpnessesAttr([float(crease)] * len(edges))
    UsdGeom.Xformable(m).AddTranslateOp().Set(Gf.Vec3d(cx, 0, 0.62))
    UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(M)
    return m


box_mesh(f"{ROOT}/None", -2.0, "none")
box_mesh(f"{ROOT}/CC", 0.0, "catmullClark")
box_mesh(f"{ROOT}/CC_Crease", 2.0, "catmullClark", crease=10.0)

sc.setup_lighting(stage, dict(
    hdri=sc.DEFAULT_HDRI, dome_intensity=1000.0, noon_dome_rot=-110.0,
    noon_sun_enable=True, noon_sun_elev=49.79, noon_sun_intensity=2450.0,
    noon_sun_color=(1.0, 0.969, 0.935), hdri_sun_rotz_offset=233.5), 0.0)

for _ in range(90):
    sim_app.update()

settings.set("/rtx/rendermode", "RaytracedLighting")
set_camera_view(eye=[0.0, -4.2, 1.35], target=[0.0, 0.0, 0.62])

print("\n" + "=" * 70)
print("② subdiv 확정 — refinementLevel 스윕")
print("=" * 70)
for lvl in (0, 1, 2, 4):
    settings.set("/rtx/hydra/subdivision/refinementLevel", int(lvl))
    for _ in range(120):
        sim_app.update()
    fp = os.path.join(OUT, f"rt_subdiv_refine{lvl}.png")
    capture_viewport_to_file(get_active_viewport(), file_path=fp)
    prev = -1
    for _ in range(60):
        sim_app.update()
        if os.path.isfile(fp):
            s = os.path.getsize(fp)
            if s > 0 and s == prev:
                break
            prev = s
    print(f"  refinementLevel={lvl} → {os.path.basename(fp)} "
          f"({os.path.getsize(fp)} B)")
    dump[f"_probe_refine{lvl}_bytes"] = os.path.getsize(fp)

with open(os.path.join(OUT, "rtx_settings.json"), "w") as f:
    json.dump(dump, f, indent=2, ensure_ascii=False)
print(f"\n[결과] {os.path.join(OUT, 'rtx_settings.json')}")
sim_app.close()
