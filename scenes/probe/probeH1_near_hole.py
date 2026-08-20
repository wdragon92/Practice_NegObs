# -*- coding: utf-8 -*-
"""
probeH1_near_hole.py — hole-type zero-shot probe, scene 1 of 3 (Isaac Sim 4.5)

Type   : HOLE — an open service pit in flat paving, surrounded by ground on all
         four sides. Not a stair, not an edge: the drop has no run of nosings
         and no linear lip to follow.
Spec   : Docs/experiment/OVERNIGHT_BRIEF_0820_v1.md §4 C1 composition (1)
         "근거리 노출 hole (V/E — band1이 최약 밴드이므로 근거리 1구도 필수)"
Shared : probe_common.py (twin contract + builders) · scene_common.py
Family : sceneD2_floor_opening.py is the nearest corpus relative (a floor
         opening IS a hole); this file is its localised, shallow, outdoor cousin.

EVALUATION ONLY. These frames must never enter training (brief C1).

HAZARD
------
Opening  x [-0.50, +0.70] · y [-0.45, +0.45]   = 1.20 (walk axis) x 0.90 m
Depth    0.60 m  (pit floor top z = -0.60; threshold is 0.30)
Toggle   SCENE_CONFIG["hazard_hole"]
           True  -> 4 liner walls + floor plate, the opening is a void
           False -> ONE flush paving patch fills the opening; z = 0.000 again

WHY THE NEAR LIP IS AT x = -0.50 AND NOT AT THE USUAL x = 0
-----------------------------------------------------------
The repository convention puts the drop start edge at x = 0. This file breaks it
by 0.50 m, deliberately, and the reason is the one thing the brief asks this
scene for: **band 1 ([0, 2) m) is the weakest band** and the probe has to reach
it. Cameras stand at x = -d with d drawn LogU[1.2, 12] from a FROZEN stream
(`vk.sample_camera(scene, i, 20260822)`), so the composition is not a matter of
taste — it is arithmetic over eight known draws:

    cut  d       h      near-lip range   band 1 reached?
    0    3.609   1.082  4.11             no
    1    2.407   0.781  1.91             YES  (A1,B1,C1 + A2,B2,C2)
    2    1.378   0.990  0.88             YES  (B1,C1,D1,E1 + B2,C2,D2)
    3    3.956   1.595  3.46             no
    4    4.449   0.810  3.95             no
    5    3.313   1.277  2.81             no
    6    7.632   0.648  7.13             no
    7    3.022   1.863  2.52             no

With the lip at x = 0 only cut 2 reaches band 1 (3 frames per arm across the
three conditions). At x = -0.50 cuts 1 AND 2 reach it — 6 frames per arm, 12
across the pair. Nothing else in the repository keys off the x = 0 convention
(the labeller measures the twin heightmap difference, not an assumed edge), so
the cost of the deviation is this paragraph and the gain is double the evidence
in the band the brief singles out.

EXPECTED TIERS (computed, not hoped for)
----------------------------------------
`wall_exposed` = the fall of the grazing ray over the near lip by the time it
reaches the far lip. > 0 means interior surface is in frame, so tier V is
reachable; >= 0.60 means the pit floor itself is:

    cut 0 0.42 · cut 1 0.49 · cut 2 1.35 · cut 3 0.55 · cut 4 0.25
    cut 5 0.54 · cut 6 0.11 · cut 7 0.89

All eight are > 0, so the expected tier distribution is **V-dominant with E on
the far/low cuts (4 and 6)**; H is not expected here and this scene is not the
place to look for it — probeH3 is.

STATUTORY DRESSING
------------------
Minimal and deliberately absent at the pit: no railing, no cones, no hatched
paint around the opening. An unguarded opening is the hazard, and under the
08-05 doctrine a guard IS a drop cue — fitting one would hand the model the
answer and destroy the point of a zero-shot probe. The dressing that IS here
(kerb, bollard row well off-axis, facade, planters) exists in BOTH arms, so it
cannot contribute to the twin delta.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python probeH1_near_hole.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python probeH1_near_hole.py
Smoke early exit (CPU):   NEGOBS_SMOKE=1  python probeH1_near_hole.py
Hazard-off arm:           NEGOBS_SCENE_CONFIG='{"hazard_hole": false}' ...

Coordinates: Z-up, m, travel axis +X, cameras at x = -d looking toward +X.
"""

import os
import json
import datetime

import scene_common as sc
import probe_common as pc


# ===========================================================================
# [A] SCENE_CONFIG — the standard 7 keys.
#     The geometry toggle is `hazard_hole`, NOT `hazard_stairs`: there is no
#     stair here and the render_configs files for these three scenes are
#     written fresh (experiments/probe_holes_0820/render_configs/), so nothing
#     inherits the corpus's `hazard_stairs` spelling by accident. A blanket
#     `{"hazard_stairs": false}` handed to this file would be silently ignored
#     by `deep_update` and would leave the hazard ON — which is exactly the
#     failure mode dayrun_0820/render_configs/README.md warns about, so the
#     probe round's config files are per-scene and named after this key.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_hole":        True,   # False -> flush paving patch, no drop anywhere
    "cue_railing":        False,  # never fitted here (see STATUTORY DRESSING)
    "cue_tactile":        False,  # not applicable to a works pit — key reserved
    "cue_material_break": True,   # False -> pit surfaces take the paving material
    "cue_nosing":         False,  # no warning paint ring — unguarded is the point
    "cue_sign":           False,  # not implemented — key reserved
    "cue_scene_dressing": True,   # kerb · bollards · planters · facade (BOTH arms)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # Paved plaza. Reaches x = -20 so that even a d = 12 m camera (x = -12)
    # stands on paving and `AabbPrefilter.ground_z` returns 0.0 for it.
    paving=dict(rect=(-20.0, -14.0, 26.0, 14.0), z_top=0.0, thick=0.22),

    # THE HOLE. See the header for why the near lip is at -0.50.
    opening=dict(x0=-0.50, y0=-0.45, x1=0.70, y1=0.45),
    depth=0.60,

    # Surrounding ground, 3 cm below the paving — walking continuity is kept
    # (a 0.03 m step is not a negative obstacle at a 0.30 m threshold).
    surround=dict(z_top=-0.03, thick=1.0, half=60.0, overlap=0.06),

    # Dressing, identical in both arms.
    dressing=dict(
        # Kerb runs well outside every hazard sight wedge (|y| >= 3.4).
        kerbs=[dict(y=-3.60, x0=-16.0, x1=18.0),
               dict(y=3.60, x0=-16.0, x1=18.0)],
        # Bollards on the far side of the kerb: they line the plaza edge, they
        # do not ring the pit.
        bollards=dict(y=4.30, xs=[-6.0, -4.5, -3.0, -1.5, 0.0, 1.5, 3.0]),
        planters=[dict(tag="A", rect=(4.2, -6.6, 6.4, -4.4), top=0.55),
                  dict(tag="B", rect=(7.6, 4.6, 9.8, 6.8), top=0.55)],
        facade=dict(x_face=24.0, y0=-16.0, y1=16.0, h=8.0, t=0.6),
        # Spoil from the excavation, kept OUTSIDE the sight wedge of every cut
        # and — this is the part that matters — present in BOTH arms. A spoil
        # heap that appeared only with the hazard would be the C2/N3 defect.
        spoil=dict(cx=3.4, cy=-2.6, sx=0.95, sy=0.70, sz=0.34),
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
    # Sun mapping world az ~ 33.5 + offset. 152.0 is sceneD2's: shadows fall
    # nearly along +X so the paving reads crisp and the pit reads relatively
    # blacker without going to 0 (a 0.60 m pit at 49.79 deg sun altitude has its
    # own floor lit from x_lip + 0.51 m onward, so "dark but not zero" is
    # geometric, not a material trick).
    SUN_AZ_OFFSET=152.0,

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


# --- env overrides (repo convention; the render driver uses the second one) ---
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "probeH1")

ASSET_ROLES = ["concrete_floor", "concrete_wall", "stone_flag", "granite_dark",
               "dirt_park", "gravel", "hdri", "mdl"]


def opening_rect():
    o = PARAMS["opening"]
    return (o["x0"], o["y0"], o["x1"], o["y1"])


def build_views():
    """`grid_views(gy=0)` plus four named cuts.

    Calling `sc.grid_views` is mandatory: `run_data_render.scene_proc` patches
    it to learn the walk axis. gy = 0 — the approach is head-on to the pit.
    """
    o = PARAMS["opening"]
    return pc.views_for(
        0.0,
        approach=([-3.0, 0.0, 0.90], [o["x1"] + 0.4, 0.0, -0.30]),
        brink=([-1.6, 0.0, 1.55], [o["x1"], 0.10, -0.60]),
        graze=([-6.0, -0.25, 0.35], [3.0, 0.05, 0.02]),
        overview=([-4.6, -4.4, 3.2], [0.6, 0.3, -0.5]))


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach/preset_h0.9_d2 — 1.20x0.90 개구가 '검은 사각형'이 아니라 '구덩이'로 읽히는가
 2. brink                   — 피트 내부(벽면/바닥)가 어둡되 **완전 0이 아닌가** (PT 8바운스)
 3. graze (h0.35)           — 저시점에서 개구가 납작해지며 은닉되는가
 4. 보행 연속성             — 포장 z=0.00 연속, 개구 우회 가능, 주변 지면 단차 0.03
 5. 트윈                    — hazard_hole=false 로 다시 띄워 포장이 완전히 평평한지"""


# ===========================================================================
# [D] main
# ===========================================================================
def main():
    # ---- CPU twin audit, BEFORE anything else -----------------------------
    # Deliberately above the smoke gate so `NEGOBS_SMOKE=1` (GT-89's pre-boot
    # gate) actually PROVES something instead of only proving that the file
    # parses. Both arms run it: it is a property of the geometry, not of the
    # toggle.
    audit = pc.twin_audit(opening_rect(), PARAMS["depth"])
    pc.print_twin_audit("probeH1", audit)
    print(f"[arm] hazard_hole={SCENE_CONFIG['hazard_hole']} "
          f"-> {'pit liner + floor (void)' if SCENE_CONFIG['hazard_hole'] else 'flush paving patch (no drop)'}")

    # [GT-89] SMOKE gate — early exit BEFORE the Isaac boot (no GPU, no GUI).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return

    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = False
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
    ROOT = "/World/ProbeH1"
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

    # -------------------------------------------------------------------
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
            # Contrast-removed control: the pit takes the paving material, so
            # the only remaining cue is geometry.
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

    # -------------------------------------------------------------------
    def build_ground(M):
        """Paving (4 boxes around the opening) + surround ring.

        `skin_exclude` is registered BEFORE the boxes are authored: the
        displacement skin would put a few millimetres of relief on the top face,
        and while that is identical in both arms for the four paving boxes, the
        OFF arm's fill patch is a different prim and would take a different draw.
        Excluding all of them makes the walked surface exactly z = 0.000 in both
        arms, which is what turns the labeller's twin difference over the
        opening into an auditable `0.000 - (-0.600) = 0.600`.
        """
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
        """The ONLY arm-varying geometry in this file."""
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
        SPH(f"{ROOT}/Spoil", (sp["cx"], sp["cy"], sp["sz"] - 0.10),
            (sp["sx"], sp["sy"], sp["sz"]), M["soil"])

    # ── assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_ground(M)
    n_arm = build_hazard(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── geometry self-check (printed so a supervisor can re-derive it) ──
    o = PARAMS["opening"]
    print(f"[기하] 개구 {o['x1'] - o['x0']:.2f}(진행축) x {o['y1'] - o['y0']:.2f}(폭) m · "
          f"낙차 {PARAMS['depth']:.2f} m · 근접 립 x={o['x0']:+.2f} · "
          f"팔별 프림 {n_arm}개")
    for tag, d_, h_ in (("cut1", 2.407, 0.781), ("cut2", 1.378, 0.990),
                        ("cut6", 7.632, 0.648)):
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
            fp = os.path.join(LOOKCHECK_DIR, f"probeH1_{ts}.png")
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
