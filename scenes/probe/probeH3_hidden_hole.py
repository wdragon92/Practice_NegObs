# -*- coding: utf-8 -*-
"""
probeH3_hidden_hole.py — hole-type zero-shot probe, scene 3 of 3 (Isaac Sim 4.5)

Type   : HOLE behind a low occluder — the H-tier composition. A 1.00 x 1.10 m
         open service pit sits immediately behind a 0.80 m raised planter wall,
         so BOTH the pit interior AND its rim are out of sight from every camera
         the frozen sampler draws.
Spec   : Docs/experiment/OVERNIGHT_BRIEF_0820_v1.md §4 C1 composition (3)
         "**가림막 뒤 hole (H 성립 구도) >= 1**", depth >= 0.5 m
Shared : probe_common.py (twin contract + builders) · scene_common.py

EVALUATION ONLY. These frames must never enter training (brief C1).

WHY THIS SCENE IS THE POINT OF THE WHOLE PROBE
----------------------------------------------
The paper's headline claim is the H tier: a drop with ZERO contributing pixels
is still predictable from context. Every H frame in the frozen corpus comes from
a STAIR or an EDGE. If the frozen v2 checkpoints keep any H recall on a HOLE
they have never seen, the claim generalises across drop type; if H recall
collapses to 0 here while V/E survive on probeH1/H2, the claim is type-bound and
that is a finding worth the night on its own. Either result is reportable, which
is why this file is written to make H the DEFAULT tier rather than a lucky
by-product.

HAZARD
------
Occluder planter  x [+0.20, +0.60] · y [-1.80, +1.80] · top z = +0.80
Opening           x [+1.00, +2.00] · y [-0.55, +0.55]  = 1.00 x 1.10 m
Depth             0.60 m  (>= the 0.50 m the brief asks for; threshold is 0.30)
Toggle            SCENE_CONFIG["hazard_hole"]  (True = void, False = flush patch)

THE OCCLUSION IS COMPUTED, NOT HOPED FOR
----------------------------------------
The limiting sight ray grazes the planter's FAR top edge (x = 0.60, z = 0.80)
and lands on the paving at

    x_reveal = 0.60 + 0.80 * (0.60 + d) / (h - 0.80)      [h > 0.80]

Ground between the planter and `x_reveal` is invisible. The hole is hidden when
`x_reveal >= 2.00` (its far lip). Against the eight FROZEN draws
`vk.sample_camera("probeH3", i, 20260822)`:

    cut  d        h       x_reveal   hidden?  margin to the far lip
    0    3.229    0.552   -          YES      eye BELOW the planter top
    1    2.647    1.016   12.64      YES      10.64 m
    2   10.377    1.211   21.97      YES      19.97 m
    3    8.089    1.762    7.83      YES       5.83 m
    4    1.273    1.101    5.58      YES       3.58 m
    5   10.163    0.817  498.31      YES     496.31 m
    6    1.512    1.761    2.36      YES       0.36 m   <- the binding cut
    7    2.119    0.315   -          YES      eye BELOW the planter top

8 of 8 hidden. Cut 6 (close AND tall, the worst case a random sampler can
produce here) is what set the planter height: at 0.75 m it clears by only
0.17 m, at 0.80 m by 0.36 m. 0.80 m is the top of the brief's 0.6-0.8 m band and
still a real planter dimension, so it is what the file uses.

Laterally the planter spans y +-1.80 against a hole of y +-0.55, so no ray from
any drawn camera reaches the hole around the planter's ends (worst case, cut 4:
the ray to the far corner crosses the planter plane at y = 0.20, 1.60 m inside
the end).

The hole is also inside the grid on all eight cuts: the two farthest cameras
(cuts 2 and 5, d ~ 10.2-10.4) put the hole centre at 11.4-11.9 m, inside the
12 m outer band edge, so no cut degenerates to an empty label vector.

STATUTORY DRESSING — the one railing line in the probe set
----------------------------------------------------------
`cue_railing` exists here and is **OFF by default**. A 0.80 m planter beside a
walked route is exactly where a real site fits a railing, so the toggle is
offered; but it is not fitted in the round, for the reason the 08-05 doctrine
states — a guard IS a drop cue, and a railing standing between the camera and an
invisible pit would let a model score H recall by detecting the railing. When it
IS switched on it guards the PLANTER edge (y = -1.95, west of the pit) and never
rings the opening, and it is authored identically in both arms.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python probeH3_hidden_hole.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python probeH3_hidden_hole.py
Smoke early exit (CPU):   NEGOBS_SMOKE=1  python probeH3_hidden_hole.py
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
    "cue_railing":        False,  # offered, NOT fitted — see the header
    "cue_tactile":        False,
    "cue_material_break": True,
    "cue_nosing":         False,
    "cue_sign":           False,
    "cue_scene_dressing": True,   # planter · kerb · bollards · facade (BOTH arms)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    paving=dict(rect=(-20.0, -14.0, 26.0, 14.0), z_top=0.0, thick=0.22),

    # THE HOLE — behind the planter.
    opening=dict(x0=1.00, y0=-0.55, x1=2.00, y1=0.55),
    depth=0.60,

    # THE OCCLUDER. `top` 0.80 is load-bearing (cut 6, see the header) and
    # `x1` 0.60 is the edge the grazing ray is computed against.
    occluder=dict(x0=0.20, y0=-1.80, x1=0.60, y1=1.80, top=0.80),

    surround=dict(z_top=-0.03, thick=1.0, half=60.0, overlap=0.06),

    dressing=dict(
        kerbs=[dict(y=-3.40, x0=-16.0, x1=18.0),
               dict(y=3.40, x0=-16.0, x1=18.0)],
        bollards=dict(y=-4.10, xs=[-6.0, -4.5, -3.0, -1.5, 0.0, 1.5, 3.0]),
        planters=[dict(tag="A", rect=(5.4, -6.8, 7.6, -4.6), top=0.55),
                  dict(tag="B", rect=(8.8, 4.8, 11.0, 7.0), top=0.55)],
        facade=dict(x_face=24.0, y0=-16.0, y1=16.0, h=8.0, t=0.6),
        # Spoil BEHIND the planter, so it is hidden by the same occluder that
        # hides the pit and cannot leak the answer over the top.
        spoil=dict(cx=2.85, cy=-1.15, sx=0.72, sy=0.55, sz=0.24),
    ),

    # Fitted only when cue_railing is True (never in the 0821 round).
    railing=dict(y=-1.95, x0=-0.60, x1=1.40, rail_h=1.10, n_post=5),

    material=dict(
        scale=dict(concrete_floor=1.2, concrete_wall=2.0, stone_flag=1.1,
                   granite_dark=1.0, dirt_park=2.0, gravel=0.9),
        paving_tint=(0.86, 0.85, 0.83),
        pit_wall_tint=(0.60, 0.59, 0.57),
        pit_floor_tint=(0.50, 0.49, 0.47),
        facade_tint=(0.80, 0.79, 0.77),
        planter_tint=(0.78, 0.77, 0.74),
        occluder_tint=(0.74, 0.73, 0.70),
        bollard_color=(0.55, 0.56, 0.58), bollard_metallic=0.55,
        bollard_rough=0.40,
        rail_color=(0.62, 0.63, 0.65), rail_metallic=0.55, rail_rough=0.40,
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "probeH3")

ASSET_ROLES = ["concrete_floor", "concrete_wall", "stone_flag", "granite_dark",
               "dirt_park", "gravel", "hdri", "mdl"]

# The eight frozen draws this scene's occlusion claim is verified against.
# (d, h) only — the rest of each sample does not enter the ray computation.
FROZEN_CAMS = [(3.229, 0.552), (2.647, 1.016), (10.377, 1.211), (8.089, 1.762),
               (1.273, 1.101), (10.163, 0.817), (1.512, 1.761), (2.119, 0.315)]


def opening_rect():
    o = PARAMS["opening"]
    return (o["x0"], o["y0"], o["x1"], o["y1"])


def occluder_edge():
    """(x_far_top_edge, height) — the pair the grazing-ray formula uses."""
    oc = PARAMS["occluder"]
    return (oc["x1"], oc["top"])


def occlusion_audit():
    """Prove tier H for every frozen draw, on CPU, before the boot.

    Returns (rows, n_hidden). Raises if any drawn camera can see the opening:
    a probeH3 whose hole is visible is not a probeH3, and rendering it would
    burn GPU minutes on a scene that answers a different question.
    """
    x_occ, h_occ = occluder_edge()
    ox0, _y0, ox1, _y1 = opening_rect()
    if ox0 <= x_occ:
        raise AssertionError(f"[occl] opening near lip {ox0} is not east of the "
                             f"occluder far face {x_occ}")
    rows, n_hidden = [], 0
    for i, (d, h) in enumerate(FROZEN_CAMS):
        if h <= h_occ:
            rows.append((i, d, h, float("inf"), True))
            n_hidden += 1
            continue
        x_rev = x_occ + h_occ * (x_occ + d) / (h - h_occ)
        hid = x_rev >= ox1
        n_hidden += int(hid)
        rows.append((i, d, h, x_rev, hid))
    if n_hidden < len(FROZEN_CAMS):
        bad = [r[0] for r in rows if not r[4]]
        raise AssertionError(
            f"[occl] cuts {bad} would SEE the opening — the H composition this "
            f"scene exists for is broken. Raise occluder['top'] or move the "
            f"opening west; both are one PARAMS edit and both change the "
            f"numbers quoted in this file's header, so update the header too.")
    return rows, n_hidden


def build_views():
    o = PARAMS["opening"]
    oc = PARAMS["occluder"]
    return pc.views_for(
        0.0,
        # The named cuts deliberately DO NOT cheat: `approach` is a walking eye
        # that sees only the planter, which is the H frame a reviewer should
        # look at. `brink` is the only view that peers in, and it exists so the
        # pit can be verified to be there at all.
        approach=([-4.0, 0.0, 0.90], [oc["x1"] + 0.6, 0.0, 0.30]),
        brink=([o["x0"] - 0.30, 0.0, 1.75], [o["x1"], 0.05, -0.60]),
        graze=([-6.0, -0.25, 0.35], [3.0, 0.05, 0.05]),
        overview=([-4.8, -5.0, 3.6], [1.5, 0.2, -0.35]))


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach (h0.9 d4)      — **개구도 림도 안 보이는가** (H 성립: 화분벽만 보여야 함)
 2. graze (h0.35)           — 저시점에서도 개구가 완전히 가려지는가
 3. brink                   — 화분벽을 넘겨다보면 피트가 실제로 거기 있는가 (존재 확인용)
 4. 측면 누출               — 화분벽 끝(|y|=1.80) 밖으로 개구가 새어 보이지 않는가
 5. 트윈                    — hazard_hole=false 로 포장이 완전히 평평한지 (화분벽은 그대로)"""


# ===========================================================================
# [D] main
# ===========================================================================
def main():
    audit = pc.twin_audit(opening_rect(), PARAMS["depth"])
    pc.print_twin_audit("probeH3", audit)
    rows, n_hidden = occlusion_audit()
    x_occ, h_occ = occluder_edge()
    print(f"[occl] planter far top edge x={x_occ:.2f} z={h_occ:.2f} · opening "
          f"far lip x={opening_rect()[2]:.2f} · {n_hidden}/{len(rows)} frozen "
          f"draws HIDDEN (tier H by construction)")
    worst = min((r for r in rows if r[3] != float("inf")),
                key=lambda r: r[3], default=None)
    if worst:
        print(f"[occl] binding cut {worst[0]} (d={worst[1]:.3f} h={worst[2]:.3f}): "
              f"x_reveal {worst[3]:.2f} vs far lip {opening_rect()[2]:.2f} "
              f"-> margin {worst[3] - opening_rect()[2]:.2f} m")
    print(f"[arm] hazard_hole={SCENE_CONFIG['hazard_hole']} "
          f"-> {'pit liner + floor (void)' if SCENE_CONFIG['hazard_hole'] else 'flush paving patch (no drop)'} "
          f"· cue_railing={SCENE_CONFIG['cue_railing']}")

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
    ROOT = "/World/ProbeH3"
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
        M["occluder"] = PBR(f"{ROOT}/Looks/Occluder",
                            sc.tex_path("stone_flag", "diff"),
                            sc.tex_path("stone_flag", "nor"),
                            sc.tex_path("stone_flag", "rough"),
                            s["stone_flag"], tint=mp["occluder_tint"])
        M["soil"] = PBR(f"{ROOT}/Looks/Soil",
                        sc.tex_path("dirt_park", "diff"),
                        sc.tex_path("dirt_park", "nor"),
                        sc.tex_path("dirt_park", "rough"), s["dirt_park"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
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

    def build_occluder(M):
        """The cue carrier. Authored in BOTH arms and never touched by the
        toggle — it is scene furniture, not a hazard marker."""
        oc = PARAMS["occluder"]
        pc.build_planter(BOX, ROOT, "Screen",
                         (oc["x0"], oc["y0"], oc["x1"], oc["y1"]), oc["top"],
                         M["occluder"], M["soil"])

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
        SPH(f"{ROOT}/Spoil", (sp["cx"], sp["cy"], sp["sz"] - 0.08),
            (sp["sx"], sp["sy"], sp["sz"]), M["soil"])
        if cfg["cue_railing"]:
            r = PARAMS["railing"]
            pc.build_railing_run(BOX, CYL, ROOT, "Planter", r["y"], r["x0"],
                                 r["x1"], M["rail"], rail_h=r["rail_h"],
                                 n_post=int(r["n_post"]))

    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_ground(M)
    build_occluder(M)
    n_arm = build_hazard(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    o = PARAMS["opening"]
    oc = PARAMS["occluder"]
    print(f"[기하] 개구 {o['x1'] - o['x0']:.2f} x {o['y1'] - o['y0']:.2f} m · "
          f"낙차 {PARAMS['depth']:.2f} m · 가림막 x[{oc['x0']:.2f},{oc['x1']:.2f}] "
          f"y[{oc['y0']:.2f},{oc['y1']:.2f}] 높이 {oc['top']:.2f} m · "
          f"간극 {o['x0'] - oc['x1']:.2f} m · 팔별 프림 {n_arm}개")
    for i, d_, h_, x_rev, hid in rows:
        print(f"[occl] cut{i} d={d_:6.3f} h={h_:5.3f} x_reveal="
              f"{'  inf' if x_rev == float('inf') else f'{x_rev:6.2f}'} "
              f"-> {'HIDDEN' if hid else 'VISIBLE'}")

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
            fp = os.path.join(LOOKCHECK_DIR, f"probeH3_{ts}.png")
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
