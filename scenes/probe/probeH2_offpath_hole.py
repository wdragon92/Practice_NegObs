# -*- coding: utf-8 -*-
"""
probeH2_offpath_hole.py — hole-type zero-shot probe, scene 2 of 3 (Isaac Sim 4.5)

Type   : HOLE, off the walked line — a 0.80 x 0.80 m open service pit set to ONE
         side of the corridor, with the corridor itself left completely walkable.
Spec   : Docs/campaign/OVERNIGHT_BRIEF_0820_v1.md §4 C1 composition (2)
         "중거리 hole — 경로 한쪽에 치우쳐 인접 섹터가 비도록 배치(통로 보존 구도):
          정답 섹터 발화와 함께 **인접 빈 섹터의 오발화율**을 별도 보고"
Shared : probe_common.py (twin contract + builders) · scene_common.py

EVALUATION ONLY. These frames must never enter training (brief C1).

HAZARD
------
Opening  x [+0.50, +1.30] · y [+1.05, +1.85]   = 0.80 x 0.80 m
Depth    0.55 m  (pit floor top z = -0.55; threshold is 0.30)
Toggle   SCENE_CONFIG["hazard_hole"]  (True = void, False = flush paving patch)

THE COMPOSITION THIS SCENE EXISTS FOR
-------------------------------------
The corridor is the strip |y| <= 1.0. The pit's nearest edge is y = +1.05, so
**the walked line is hazard-free in every frame of both arms** and a correct
model has to light up a lateral sector while leaving the sector in front of the
walker dark. That asymmetry is the measurement: alongside the recall on the
answer sector, the probe reports the firing rate on the *adjacent hazard-free
sectors of the same band*, which is a false-alarm number no corpus scene can
produce (every corpus hazard spans the walk axis).

The lateral offset y_c = +1.45 m is not a guess. Angular position depends on
range, so a fixed offset drifts toward the centre sector as the camera backs
off; y_c was swept over 1.25…2.05 m against the eight FROZEN camera draws
(`vk.sample_camera("probeH2", i, 20260822)`) and 1.45 maximises the number of
cuts whose positive set sits off-centre while keeping every sample inside the
12 m grid. Resulting per-cut cells (labeller convention A = image-left = +az):

    cut  d       yaw      range        cells                 dominant sector
    0    2.902   -0.47    3.44-4.41    A2,B2                 A
    1    9.100   +5.26    9.67-10.58   C3b                   C   (worst case)
    2   10.112   +2.47   10.65-11.55   B3b,C3b               B
    3    4.436   -7.42    4.94-5.82    B2,A3a,B3a            B
    4    5.637   +4.10    6.35-7.35    B3a                   B   (single cell!)
    5    3.470   -1.13    4.11-5.13    A2,B2,A3a             A
    6    3.917   -1.07    4.46-5.41    A2,B2,B3a             B
    7    2.609  +13.23    3.40-4.47    A2,B2,C2              A

Seven of eight cuts put the hazard off the centre sector; cut 1 at 9.7 m is the
honest exception — a 1.45 m offset subtends only 8.6 deg at that range, which is
inside sector C. That is geometry, not a defect, and it is reported rather than
engineered away (widening the offset to fix cut 1 pushes cuts 4-6 out to sector
A, where only ONE adjacent sector exists and the false-firing measurement gets
weaker on both sides).

Cut 4 is the prize: a SINGLE positive cell (B3a) with A3a and C3a both empty.

EXPECTED TIERS
--------------
`wall_exposed` (grazing-ray fall over the near lip by the far lip) is 0.03-0.24 m
on the eight cuts — positive everywhere, but well under the 0.55 m depth, so the
pit floor is never in view. Expect **E-dominant (rim + a sliver of far wall)
with V on the two closest cuts (0 and 7)**; a 0.80 m opening at 6-10 m is a few
dozen pixels, so some far cuts may label H.

STATUTORY DRESSING
------------------
None at the pit. See probeH1's header: under the 08-05 doctrine a guard IS a
drop cue, and this probe is about whether *hole context* alone carries. The
kerb / bollards / planters / facade are present in BOTH arms.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python probeH2_offpath_hole.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python probeH2_offpath_hole.py
Smoke early exit (CPU):   NEGOBS_SMOKE=1  python probeH2_offpath_hole.py
Hazard-off arm:           NEGOBS_SCENE_CONFIG='{"hazard_hole": false}' ...

Coordinates: Z-up, m, travel axis +X, cameras at x = -d looking toward +X.
"""

import os
import json
import datetime

import scene_common as sc
import probe_common as pc


# ===========================================================================
# [A] SCENE_CONFIG — standard 7 keys, geometry toggle = `hazard_hole`
# ===========================================================================
SCENE_CONFIG = {
    "hazard_hole":        True,
    "cue_railing":        False,  # the pit stays unguarded in both arms
    "cue_tactile":        False,  # key reserved
    "cue_material_break": True,
    "cue_nosing":         False,
    "cue_sign":           False,
    "cue_scene_dressing": True,   # kerb · bollards · planters · facade (BOTH arms)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    paving=dict(rect=(-20.0, -14.0, 26.0, 14.0), z_top=0.0, thick=0.22),

    # THE HOLE — offset to +y, corridor |y| <= 1.0 preserved.
    opening=dict(x0=0.50, y0=1.05, x1=1.30, y1=1.85),
    depth=0.55,

    surround=dict(z_top=-0.03, thick=1.0, half=60.0, overlap=0.06),

    dressing=dict(
        # The corridor is READ as a corridor: a paving-band change at y = +-1.0
        # would be a cue correlated with the pit's side, so instead the corridor
        # is marked symmetrically by kerbs at +-3.2 m — far outside the pit and
        # identical on both sides, so nothing in the dressing points at +y.
        kerbs=[dict(y=-3.20, x0=-16.0, x1=18.0),
               dict(y=3.20, x0=-16.0, x1=18.0)],
        bollards=dict(y=-3.95, xs=[-5.0, -3.5, -2.0, -0.5, 1.0, 2.5, 4.0]),
        planters=[dict(tag="A", rect=(6.0, -6.4, 8.2, -4.2), top=0.55),
                  dict(tag="B", rect=(9.4, 4.4, 11.6, 6.6), top=0.55)],
        facade=dict(x_face=24.0, y0=-16.0, y1=16.0, h=8.0, t=0.6),
        # Spoil on the pit's own side, in BOTH arms. Present in the off arm it
        # is a decoy: a model that fires on "loose earth beside the path" rather
        # than on the hole will show up as off-arm false alarm, which is the
        # C2/N3 dressing caveat measured instead of assumed.
        spoil=dict(cx=2.35, cy=1.60, sx=0.80, sy=0.62, sz=0.28),
    ),

    material=dict(
        scale=dict(concrete_floor=1.2, concrete_wall=2.0, stone_flag=1.1,
                   granite_dark=1.0, dirt_park=2.0, gravel=0.9),
        paving_tint=(0.86, 0.85, 0.83),
        pit_wall_tint=(0.60, 0.59, 0.57),
        pit_floor_tint=(0.50, 0.49, 0.47),
        facade_tint=(0.80, 0.79, 0.77),
        planter_tint=(0.78, 0.77, 0.74),
        bollard_color=(0.55, 0.56, 0.58), bollard_metallic=0.55,
        bollard_rough=0.40,
    ),

    light=pc.probe_light(),
    SUN_AZ_OFFSET=152.0,
    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    pc.deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    pc.deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [C] path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "probeH2")

ASSET_ROLES = ["concrete_floor", "concrete_wall", "stone_flag", "granite_dark",
               "dirt_park", "gravel", "hdri", "mdl"]

CORRIDOR_HALF_WIDTH = 1.00      # quoted by the corridor self-check below


def opening_rect():
    o = PARAMS["opening"]
    return (o["x0"], o["y0"], o["x1"], o["y1"])


def build_views():
    o = PARAMS["opening"]
    cy = (o["y0"] + o["y1"]) / 2.0
    return pc.views_for(
        0.0,
        approach=([-4.0, 0.0, 0.90], [o["x1"] + 0.4, cy, -0.25]),
        brink=([-0.4, cy, 1.55], [o["x1"], cy, -0.55]),
        graze=([-6.0, -0.30, 0.35], [4.0, 0.6, 0.02]),
        overview=([-5.0, -4.6, 3.4], [1.0, 1.2, -0.45]))


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach (h0.9 d4)      — 개구가 **경로 밖 한쪽**에 있고 정면 통로는 비어 보이는가
 2. 통로 보존               — |y|<=1.0 스트립을 걸어 지나갈 수 있는가 (개구 최근접 y=+1.05)
 3. brink                   — 피트 내부가 어둡되 완전 0이 아닌가 (PT 8바운스)
 4. 대칭 드레싱             — 연석/볼라드가 +y 쪽을 가리키지 않는가 (단서 누수 방지)
 5. 트윈                    — hazard_hole=false 로 포장이 완전히 평평한지"""


# ===========================================================================
# [D] main
# ===========================================================================
def main():
    audit = pc.twin_audit(opening_rect(), PARAMS["depth"])
    pc.print_twin_audit("probeH2", audit)
    o = PARAMS["opening"]
    if o["y0"] <= CORRIDOR_HALF_WIDTH:
        raise AssertionError(
            f"[corridor] opening near edge y={o['y0']:.2f} intrudes into the "
            f"preserved corridor |y| <= {CORRIDOR_HALF_WIDTH:.2f}; this scene's "
            f"whole measurement (adjacent hazard-free sector firing) needs the "
            f"walked line clean.")
    print(f"[corridor] preserved |y| <= {CORRIDOR_HALF_WIDTH:.2f} m · opening "
          f"near edge y={o['y0']:+.2f} · clearance "
          f"{o['y0'] - CORRIDOR_HALF_WIDTH:.2f} m")
    print(f"[arm] hazard_hole={SCENE_CONFIG['hazard_hole']} "
          f"-> {'pit liner + floor (void)' if SCENE_CONFIG['hazard_hole'] else 'flush paving patch (no drop)'}")

    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return

    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode)

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
    ROOT = "/World/ProbeH2"
    UsdGeom.Xform.Define(stage, ROOT)

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl, rotY=rotY,
                               collider=col)

    def SPH(path, center, scale3, mtl=None):
        return sc.add_sphere(stage, path, center, scale3, mtl)

    def PBR(path, *a, **k):
        return sc.make_pbr(stage, path, *a, **k)

    def setup_materials():
        s = mp["scale"]
        M = {}
        M["paving"] = PBR(f"{ROOT}/Looks/Paving",
                          sc.tex_path("concrete_floor", "diff"),
                          sc.tex_path("concrete_floor", "nor"),
                          sc.tex_path("concrete_floor", "rough"),
                          s["concrete_floor"], tint=mp["paving_tint"])
        M["pit_wall"] = PBR(f"{ROOT}/Looks/PitWall",
                            sc.tex_path("concrete_wall", "diff"),
                            sc.tex_path("concrete_wall", "nor"),
                            sc.tex_path("concrete_wall", "rough"),
                            s["concrete_wall"], tint=mp["pit_wall_tint"])
        M["pit_floor"] = PBR(f"{ROOT}/Looks/PitFloor",
                             sc.tex_path("gravel", "diff"),
                             sc.tex_path("gravel", "nor"),
                             sc.tex_path("gravel", "rough"),
                             s["gravel"], tint=mp["pit_floor_tint"])
        if not cfg["cue_material_break"]:
            M["pit_wall"] = M["paving"]
            M["pit_floor"] = M["paving"]
        M["ground"] = PBR(f"{ROOT}/Looks/Ground",
                          sc.tex_path("dirt_park", "diff"),
                          sc.tex_path("dirt_park", "nor"),
                          sc.tex_path("dirt_park", "rough"), s["dirt_park"])
        M["kerb"] = PBR(f"{ROOT}/Looks/Kerb",
                        sc.tex_path("granite_dark", "diff"),
                        sc.tex_path("granite_dark", "nor"),
                        sc.tex_path("granite_dark", "rough"),
                        s["granite_dark"])
        M["facade"] = PBR(f"{ROOT}/Looks/Facade",
                          sc.tex_path("concrete_wall", "diff"),
                          sc.tex_path("concrete_wall", "nor"),
                          sc.tex_path("concrete_wall", "rough"),
                          s["concrete_wall"], tint=mp["facade_tint"])
        M["planter"] = PBR(f"{ROOT}/Looks/Planter",
                           sc.tex_path("stone_flag", "diff"),
                           sc.tex_path("stone_flag", "nor"),
                           sc.tex_path("stone_flag", "rough"),
                           s["stone_flag"], tint=mp["planter_tint"])
        M["soil"] = PBR(f"{ROOT}/Looks/Soil",
                        sc.tex_path("dirt_park", "diff"),
                        sc.tex_path("dirt_park", "nor"),
                        sc.tex_path("dirt_park", "rough"), s["dirt_park"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        return M

    def build_ground(M):
        pv = PARAMS["paving"]
        sc.skin_exclude(f"{ROOT}/Paving_W", f"{ROOT}/Paving_E",
                        f"{ROOT}/Paving_S", f"{ROOT}/Paving_N",
                        f"{ROOT}/Fill_Patch")
        for name, c, s in pc.paving_boxes(tuple(pv["rect"]), opening_rect(),
                                          pv["z_top"], pv["thick"]):
            BOX(f"{ROOT}/{name}", c, s, M["paving"], col=True)
        su = PARAMS["surround"]
        for name, c, s in pc.surround_boxes(tuple(pv["rect"]), su["z_top"],
                                            su["thick"], su["half"],
                                            su["overlap"]):
            BOX(f"{ROOT}/{name}", c, s, M["ground"], col=True)

    def build_hazard(M):
        if cfg["hazard_hole"]:
            for name, c, s, role in pc.pit_boxes(opening_rect(),
                                                 PARAMS["depth"],
                                                 PARAMS["paving"]["z_top"],
                                                 PARAMS["paving"]["thick"]):
                BOX(f"{ROOT}/{name}", c, s,
                    M["pit_floor"] if role == "floor" else M["pit_wall"],
                    col=True)
            return 5
        name, c, s = pc.fill_patch_box(opening_rect(),
                                       PARAMS["paving"]["z_top"],
                                       PARAMS["paving"]["thick"])
        BOX(f"{ROOT}/{name}", c, s, M["paving"], col=True)
        return 1

    def build_dressing(M):
        d = PARAMS["dressing"]
        for k in d["kerbs"]:
            pc.build_kerb_line(BOX, ROOT, M["kerb"], k["y"], k["x0"], k["x1"])
        b = d["bollards"]
        pc.build_bollard_row(CYL, ROOT, M["bollard"], b["xs"], b["y"])
        for p in d["planters"]:
            pc.build_planter(BOX, ROOT, p["tag"], tuple(p["rect"]), p["top"],
                             M["planter"], M["soil"])
        f = d["facade"]
        pc.build_facade_wall(BOX, ROOT, M["facade"], f["x_face"], f["y0"],
                             f["y1"], f["h"], f["t"])
        sp = d["spoil"]
        SPH(f"{ROOT}/Spoil", (sp["cx"], sp["cy"], sp["sz"] - 0.09),
            (sp["sx"], sp["sy"], sp["sz"]), M["soil"])

    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_ground(M)
    n_arm = build_hazard(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    print(f"[기하] 개구 {o['x1'] - o['x0']:.2f} x {o['y1'] - o['y0']:.2f} m · "
          f"낙차 {PARAMS['depth']:.2f} m · 횡방향 중심 y="
          f"{(o['y0'] + o['y1']) / 2.0:+.2f} · 팔별 프림 {n_arm}개")
    for tag, d_, h_ in (("cut0", 2.902, 0.995), ("cut4", 5.637, 1.028),
                        ("cut1", 9.100, 0.408)):
        print(pc.sight_report(tag, opening_rect(), PARAMS["depth"], h_, d_))

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

    def on_key(event, *args):
        if event.type != carb.input.KeyboardEventType.KEY_PRESS:
            return True
        if event.input == K.P:
            cur = settings.get("/rtx/rendermode")
            set_render_mode("RaytracedLighting" if cur == "PathTracing"
                            else "PathTracing")
            print(f"[렌더] {settings.get('/rtx/rendermode')}")
        elif event.input == K.C:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fp = os.path.join(LOOKCHECK_DIR, f"probeH2_{ts}.png")
            capture_viewport_to_file(get_active_viewport(), file_path=fp)
            print(f"[캡처] {fp}")
        elif event.input in (K.LEFT_BRACKET, K.RIGHT_BRACKET):
            dome_user_rot[0] += (-rot_step if event.input == K.LEFT_BRACKET
                                 else rot_step)
            apply_dome_rot(dome_user_rot[0])
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        return True

    keyboard_sub = input_iface.subscribe_to_keyboard_events(
        appwindow.get_keyboard(), on_key)

    print("=" * 64)
    print(BANNER)
    print("=" * 64)

    while simulation_app.is_running():
        simulation_app.update()

    input_iface.unsubscribe_to_keyboard_events(appwindow.get_keyboard(),
                                               keyboard_sub)
    simulation_app.close()


if __name__ == "__main__":
    main()
