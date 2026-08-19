#!/usr/bin/env python3
"""End-to-end test on analytically ray-cast synthetic round pairs.

Fixture 1 (legacy, 15 checks -- unchanged):
  World: flat ground z=0, rectangular pit x in [0,4], y in [-1,3], floor z=-1.
  Camera: eye (-3,0,1.5), yaw 0, pitch -10, roll 0, hfov 62.2.
  Cut 0000 = clear view.  Cut 0001 = same pose, a 2 m wall baked at x=-0.5 in the
  DEPTH ONLY (the heightmap is unchanged) -> the drop becomes hidden.

Fixture 2 (D10 footprint v2):
  sceneN4     -- ramp falling 1.0 m over 8 m, NO step anywhere.  The twin-diff
                 footprint is large, the STEP GATE must erase it completely.
  synthstairs -- 0.15 m risers on 0.3 m treads: every single riser is below the
                 0.3 m hazard threshold, yet the run falls 0.5 m per metre, so
                 the gate must KEEP the flight (the counter-case to the ramp).
  synthslope  -- walkable ground descending 0.2 m over 4 m (and on past the
                 hazard), then a 1.0 m vertical pit.  The pit must stay labelled
                 while the sloped walkway must not enter the footprint -- the
                 exact case where the v0 `cam.ground_z` reference produced false
                 positives on the far walkway.
Every fixture gives the off arm the same world minus the pit / ramp / stairs.

Fixture 3 (D14 preservation + PROVISIONAL-HOLD):
  the ramp above doubles as the preservation proof -- `polar_gt` all zero while
  `polar_gt_pregate` is non-zero and `gate_excluded.n > 0` -- and the stairs as
  its counter-case (nothing excluded, pregate == polar_gt).
  sceneD1     -- a batch-1 drop scene whose twin arms are identical, so the
                 hazard-ON arm carries zero positives: gates.py must HOLD it
                 (hold_scenes.json + banner) instead of failing G2, and
                 make_split.py --exclude-scenes must keep it out of every split
                 with its PROOF checks still green.
"""
import json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
from labeler import cam_basis, focal_px, polar_cells, W_IMG, H_IMG

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
PIT = (0.0, 4.0, -1.0, 3.0, -1.0)          # x0,x1,y0,y1,floor_z
CAM = dict(eye=[-3.0, 0.0, 1.5], ground_z=0.0, d=3.0, h_rel=1.5, yaw=0.0,
           pitch=-10.0, roll=0.0, hfov=62.2, focal=17.37, aperture=20.955, tier="CAM-1")
EXPECT_GT = [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0]
X0, Y0, ST, N = -2.0, -8.0, 0.05, 321


def render_depth(cam, pit, wall=None):
    """Analytic z-depth (distance_to_image_plane).  Ray dirs are built with a
    unit component along the optical axis, so the ray parameter IS the z-depth."""
    r, u, f = cam_basis(cam["yaw"], cam["pitch"], cam["roll"])
    fx = focal_px(cam["hfov"])
    e = np.asarray(cam["eye"], float)
    UN, VN = np.meshgrid((np.arange(W_IMG) + 0.5 - W_IMG / 2) / fx,
                         (np.arange(H_IMG) + 0.5 - H_IMG / 2) / fx)
    D = UN[..., None] * r + VN[..., None] * (-u) + f
    dx, dy, dz = D[..., 0], D[..., 1], D[..., 2]
    best = np.full((H_IMG, W_IMG), np.inf)

    def upd(t, valid):
        np.minimum(best, np.where(valid & (t > 1e-6) & np.isfinite(t), t, np.inf), out=best)

    def safe(v):
        return np.where(np.abs(v) < 1e-12, 1e-12, v)

    if pit:
        x0, x1, y0, y1, pz = pit
        t = (0.0 - e[2]) / safe(dz)
        X, Y = e[0] + t * dx, e[1] + t * dy
        upd(t, ~((X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)))     # ground, pit cut out
        t = (pz - e[2]) / safe(dz)
        X, Y = e[0] + t * dx, e[1] + t * dy
        upd(t, (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1))        # pit floor
        for ax, val, lo, hi in ((0, x0, y0, y1), (0, x1, y0, y1),
                                (1, y0, x0, x1), (1, y1, x0, x1)):   # 4 pit walls
            d_ = dx if ax == 0 else dy
            t = (val - e[ax]) / safe(d_)
            o = e[1] + t * dy if ax == 0 else e[0] + t * dx
            upd(t, (o >= lo) & (o <= hi) & (e[2] + t * dz >= pz) & (e[2] + t * dz <= 0.0))
    else:
        upd((0.0 - e[2]) / safe(dz), np.ones_like(dz, bool))
    if wall:
        wx, wh = wall
        t = (wx - e[0]) / safe(dx)
        Z = e[2] + t * dz
        upd(t, (Z >= 0.0) & (Z <= wh))
    best[~np.isfinite(best)] = np.nan
    return best.astype(np.float16)


def heightmap(pit):
    X, Y = np.meshgrid(X0 + np.arange(N) * ST, Y0 + np.arange(N) * ST)
    z = np.zeros((N, N), np.float32)
    if pit:
        x0, x1, y0, y1, pz = pit
        z[(X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)] = pz
    return z


def write_arm(root, arm, pit):
    d = os.path.join(root, f"260819_synth_{arm}", "train", "synthpit")
    os.makedirs(d, exist_ok=True)
    np.save(os.path.join(d, "heightmap.npy"), heightmap(pit))
    json.dump(dict(x0=X0, y0=Y0, step=ST, shape=[N, N], nan="no-hit"),
              open(os.path.join(d, "heightmap_meta.json"), "w"))
    cuts = []
    for i, wall in enumerate((None, (-0.5, 2.0))):
        fn = f"L0__s20260819__{i:04d}.png"
        Image.fromarray(np.full((270, 480, 3), 110, np.uint8)).save(os.path.join(d, fn))
        np.save(os.path.join(d, fn[:-4] + ".depth.npy"), render_depth(CAM, pit, wall))
        cuts.append(dict(file=fn, scene="synthpit", cond="L0", seed=20260819, idx=i,
                         ok=True, cam=dict(CAM), stage1=dict(ground_below=True)))
    json.dump(dict(scene="synthpit", seed=20260819, gy=0.0, conds=["L0"], split="train",
                   n=2, n_ok=2, cuts=cuts), open(os.path.join(d, "variation.json"), "w"))
    return os.path.join(root, f"260819_synth_{arm}")


# --------------------------------------------------------------------------- #
# fixture 2 -- slope-robustness worlds (D10)
# --------------------------------------------------------------------------- #
RAMP_K, RAMP_LEN = 0.125, 8.0        # 1.0 m of fall over 8 m of run, no step
SLOPE_K = 0.05                       # 0.2 m of fall over 4 m of walkway
SPIT = (4.0, 8.0, -1.0, 3.0, -1.2)   # x0,x1,y0,y1,floor_z of the vertical pit
FAR_WALKWAY_CELL = 14                # band 3 x sector E: sloped walkway only,
#                                      the pit never reaches that azimuth


def _safe(v):
    return np.where(np.abs(v) < 1e-12, 1e-12, v)


def plane_z(a, b, keep):
    """Surface z = a*x + b, existing only where keep(X, Y)."""
    def s(e, dx, dy, dz):
        t = (a * e[0] + b - e[2]) / _safe(dz - a * dx)
        return t, keep(e[0] + t * dx, e[1] + t * dy)
    return s


def wall_at(axis, val, lo, hi, z_lo, z_hi):
    """Vertical face on x=val (axis 0) or y=val (axis 1), spanning the other
    horizontal coord in [lo,hi] and z in [z_lo, z_hi(X,Y)]."""
    def s(e, dx, dy, dz):
        t = (val - e[axis]) / _safe(dx if axis == 0 else dy)
        X, Y, Z = e[0] + t * dx, e[1] + t * dy, e[2] + t * dz
        o = Y if axis == 0 else X
        return t, (o >= lo) & (o <= hi) & (Z >= z_lo) & (Z <= z_hi(X, Y))
    return s


def render_surfaces(cam, surfaces):
    """Analytic z-depth of the nearest surface hit (same convention as above)."""
    r, u, f = cam_basis(cam["yaw"], cam["pitch"], cam["roll"])
    fx = focal_px(cam["hfov"])
    e = np.asarray(cam["eye"], float)
    UN, VN = np.meshgrid((np.arange(W_IMG) + 0.5 - W_IMG / 2) / fx,
                         (np.arange(H_IMG) + 0.5 - H_IMG / 2) / fx)
    D = UN[..., None] * r + VN[..., None] * (-u) + f
    dx, dy, dz = D[..., 0], D[..., 1], D[..., 2]
    best = np.full((H_IMG, W_IMG), np.inf)
    for s in surfaces:
        t, valid = s(e, dx, dy, dz)
        np.minimum(best, np.where(valid & (t > 1e-6) & np.isfinite(t), t, np.inf), out=best)
    best[~np.isfinite(best)] = np.nan
    return best.astype(np.float16)


def grid_xy():
    return np.meshgrid(X0 + np.arange(N) * ST, Y0 + np.arange(N) * ST)


def ramp_world(on):
    """(heightmap, surfaces) for the gradual-ramp scene."""
    X, _ = grid_xy()
    if not on:
        return np.zeros((N, N), np.float32), [plane_z(0.0, 0.0, lambda a, b: np.ones_like(a, bool))]
    z = np.where(X <= 0.0, 0.0,
                 np.where(X <= RAMP_LEN, -RAMP_K * X, -RAMP_K * RAMP_LEN))
    return z.astype(np.float32), [
        plane_z(0.0, 0.0, lambda a, b: a <= 0.0),
        plane_z(-RAMP_K, 0.0, lambda a, b: (a > 0.0) & (a <= RAMP_LEN)),
        plane_z(0.0, -RAMP_K * RAMP_LEN, lambda a, b: a > RAMP_LEN)]


def slope_world(on):
    """(heightmap, surfaces) for the sloped approach + vertical pit scene."""
    X, Y = grid_xy()
    px0, px1, py0, py1, pz = SPIT
    ground = np.where(X <= 0.0, 0.0, -SLOPE_K * X)
    inpit = (X >= px0) & (X <= px1) & (Y >= py0) & (Y <= py1)
    gz = lambda a, b: np.where(a <= 0.0, 0.0, -SLOPE_K * a)     # noqa: E731
    pit_xy = lambda a, b: (a >= px0) & (a <= px1) & (b >= py0) & (b <= py1)  # noqa: E731
    surf = [plane_z(0.0, 0.0, lambda a, b: (a <= 0.0) & ~pit_xy(a, b)),
            plane_z(-SLOPE_K, 0.0, lambda a, b: (a > 0.0) & ~pit_xy(a, b))]
    if not on:
        return ground.astype(np.float32), surf
    z = np.where(inpit, pz, ground)
    surf = surf + [
        plane_z(0.0, pz, pit_xy),
        wall_at(0, px0, py0, py1, pz, gz), wall_at(0, px1, py0, py1, pz, gz),
        wall_at(1, py0, px0, px1, pz, gz), wall_at(1, py1, px0, px1, pz, gz)]
    return z.astype(np.float32), surf


STAIR_X, TREAD, RISER, NSTEP = 4.0, 0.3, 0.15, 6      # 0.9 m of fall over 1.8 m


def stairs_world(on):
    """(heightmap, surfaces) for a flight of stairs: each riser (0.15 m) is far
    below the 0.3 m hazard threshold, but the run falls 0.5 m per metre, so the
    step gate must KEEP it -- the counter-case to the ramp."""
    X, _ = grid_xy()
    flat = [plane_z(0.0, 0.0, lambda a, b: np.ones_like(a, bool))]
    if not on:
        return np.zeros((N, N), np.float32), flat
    k = np.floor((X - STAIR_X) / TREAD)
    z = np.where(X <= STAIR_X, 0.0, -RISER * np.minimum(k + 1, NSTEP))
    surf = [plane_z(0.0, 0.0, lambda a, b: a <= STAIR_X),
            plane_z(0.0, -RISER * NSTEP,
                    lambda a, b: a > STAIR_X + TREAD * NSTEP)]
    for i in range(NSTEP):
        lo, hi = STAIR_X + TREAD * i, STAIR_X + TREAD * (i + 1)
        surf.append(plane_z(0.0, -RISER * (i + 1),
                            lambda a, b, lo=lo, hi=hi: (a > lo) & (a <= hi)))
        surf.append(wall_at(0, lo, -100.0, 100.0, -RISER * (i + 1),
                            lambda a, b, t=-RISER * i: np.full_like(a, t)))
    return z.astype(np.float32), surf


def write_v2_scene(root, arm, scene, hm, surfaces):
    d = os.path.join(root, f"260819_synthv2_{arm}", "train", scene)
    os.makedirs(d, exist_ok=True)
    np.save(os.path.join(d, "heightmap.npy"), hm)
    json.dump(dict(x0=X0, y0=Y0, step=ST, shape=[N, N], nan="no-hit"),
              open(os.path.join(d, "heightmap_meta.json"), "w"))
    fn = "L0__s20260819__0000.png"
    Image.fromarray(np.full((270, 480, 3), 110, np.uint8)).save(os.path.join(d, fn))
    np.save(os.path.join(d, fn[:-4] + ".depth.npy"), render_surfaces(CAM, surfaces))
    cuts = [dict(file=fn, scene=scene, cond="L0", seed=20260819, idx=0, ok=True,
                 cam=dict(CAM), stage1=dict(ground_below=True))]
    json.dump(dict(scene=scene, seed=20260819, gy=0.0, conds=["L0"], split="train",
                   n=1, n_ok=1, cuts=cuts), open(os.path.join(d, "variation.json"), "w"))
    return os.path.join(root, f"260819_synthv2_{arm}")


def v0_rule_gt(hm_on, grid):
    """polar GT the RETIRED v0 rule would have produced (footprint measured
    against the cut's own cam.ground_z instead of the off-arm surface)."""
    XX, YY = grid_xy()
    cell, _ = polar_cells(XX, YY, np.asarray(CAM["eye"], float), CAM["yaw"], grid)
    fp = np.isfinite(hm_on) & ((CAM["ground_z"] - hm_on) >= grid["hazard_depth_m"])
    fc = cell[fp]
    gt = np.zeros(grid["n_bands"] * grid["n_sectors"], int)
    gt[np.unique(fc[fc >= 0])] = 1
    return gt, int(fp.sum())


def run(*args):
    env = dict(os.environ, PYTHONNOUSERSITE="1", PYTHONPATH=HERE)
    p = subprocess.run([PY] + list(args), cwd=HERE, env=env,
                       capture_output=True, text=True)
    if p.returncode:
        print(p.stdout + p.stderr)
    return p


def legacy_fixture(ok):
    root = tempfile.mkdtemp(prefix="negobs_synth_")
    on = write_arm(root, "on", PIT)
    off = write_arm(root, "off", None)
    lab_p = os.path.join(root, "annotations", "labels_v0.json")
    man_p = os.path.join(root, "dataset_manifest_v1.json")

    r = run("labeler.py", "--on-round", on, "--off-round", off,
            "--grid", os.path.join(HERE, "gridspec_v0.json"), "--out", lab_p)
    assert r.returncode == 0, "labeler.py failed"
    L = json.load(open(lab_p))["frames"]
    a = L["on/synthpit/L0__s20260819__0000.png"]
    b = L["on/synthpit/L0__s20260819__0001.png"]
    o = L["off/synthpit/L0__s20260819__0000.png"]

    def chk(name, cond, extra=""):
        ok.append(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {extra}")

    chk("polar_gt == hand-computed [band2/3 x sectors A-D]",
        a["polar_gt"] == EXPECT_GT, f"got {a['polar_gt']}")
    chk("clear cut: int_px > 0", a["raw_vis"]["int_px"] > 0, f"int_px={a['raw_vis']['int_px']}")
    chk("clear cut: edge_ratio ~1", (a["raw_vis"]["edge_ratio"] or 0) >= 0.90,
        f"edge_ratio={a['raw_vis']['edge_ratio']} proj={a['raw_vis']['edge_projected']}")
    chk("clear cut: tier V at tau_int=50", a["tier_matrix"]["i50_e0.05"] == "V",
        f"strict={a['tier_strict']}")
    chk("walled cut: int_px == 0", b["raw_vis"]["int_px"] == 0, f"int_px={b['raw_vis']['int_px']}")
    chk("walled cut: edge_visible == 0", b["raw_vis"]["edge_visible"] == 0,
        f"edge_visible={b['raw_vis']['edge_visible']}/{b['raw_vis']['edge_projected']}")
    chk("walled cut: tier H (strict)", b["tier_strict"] == "H", f"got {b['tier_strict']}")
    chk("walled cut: H under every tau combo",
        set(b["tier_matrix"].values()) == {"H"})
    chk("off arm: polar_gt all zero (computed, not hardcoded)",
        sum(o["polar_gt"]) == 0 and o["tier_strict"] == "off")
    chk("off arm: same pose -> twin verified", len(json.load(open(lab_p))["warnings"]) == 0)
    chk("void stats zero on a hole-free heightmap", a["void_stats"]["void_total"] == 0)

    r = run("build_manifest.py", "--labels", lab_p, "--on-round", on,
            "--off-round", off, "--out", man_p)
    chk("build_manifest.py runs", r.returncode == 0)
    M = json.load(open(man_p))
    chk("manifest: 4 frames, abs paths, grid tagged",
        len(M["frames"]) == 4 and all(os.path.isabs(f["rgb"]) for f in M["frames"])
        and M["meta"]["grid_version"] == "PROVISIONAL-GRID-V0")

    r = run("gates.py", "--manifest", man_p, "--labels", lab_p,
            "--out", os.path.join(root, "GATES_REPORT.md"),
            "--audit-dir", os.path.join(root, "audit_samples"), "--n-audit", "4")
    chk("gates.py runs and writes overlays", r.returncode == 0
        and len([f for f in os.listdir(os.path.join(root, "audit_samples"))
                 if f.endswith(".png")]) >= 3)
    for ln in open(os.path.join(root, "GATES_REPORT.md")):
        if ln.startswith(("## G", "**")):
            print("    " + ln.rstrip())

    # cut 0001 has a wall baked into its depth only (no real round has that), so
    # the camera-convention probe is run on the clean cut.
    r = run("verify_reprojection.py", "--scene-dir",
            os.path.join(on, "train", "synthpit"), "--n", "1")
    print("\n".join("    " + x for x in r.stdout.strip().splitlines()))
    chk("verify_reprojection.py: synthetic cut passes < 0.10 m", r.returncode == 0)
    print("\nNOTE G5 on this fixture: a 1.0 m vertical pit seen from 3 m at h=1.5 m casts a\n"
          "     2 m view shadow, so the GT-positive band-2 cells at the lip hold no visible\n"
          "     below-ground surface. Sub-target G5 here is geometry, not a code fault.")
    print(f"\nfixture: {root}")
    return root


def slope_fixture(ok):
    """D10 footprint-v2 fixtures: gradual ramp (must vanish) + sloped approach
    to a real pit (pit must survive, walkway must stay clean)."""
    root = tempfile.mkdtemp(prefix="negobs_synthv2_")
    hm_ramp_on, s_ramp_on = ramp_world(True)
    hm_ramp_off, s_ramp_off = ramp_world(False)
    hm_slope_on, s_slope_on = slope_world(True)
    hm_slope_off, s_slope_off = slope_world(False)
    hm_st_on, s_st_on = stairs_world(True)
    hm_st_off, s_st_off = stairs_world(False)
    write_v2_scene(root, "on", "sceneN4", hm_ramp_on, s_ramp_on)
    write_v2_scene(root, "on", "synthstairs", hm_st_on, s_st_on)
    on = write_v2_scene(root, "on", "synthslope", hm_slope_on, s_slope_on)
    write_v2_scene(root, "off", "sceneN4", hm_ramp_off, s_ramp_off)
    write_v2_scene(root, "off", "synthstairs", hm_st_off, s_st_off)
    off = write_v2_scene(root, "off", "synthslope", hm_slope_off, s_slope_off)
    lab_p = os.path.join(root, "annotations", "labels_v0.json")
    man_p = os.path.join(root, "dataset_manifest_v1.json")
    grid = json.load(open(os.path.join(HERE, "gridspec_v0.json")))

    r = run("labeler.py", "--on-round", on, "--off-round", off,
            "--grid", os.path.join(HERE, "gridspec_v0.json"), "--out", lab_p)
    assert r.returncode == 0, "labeler.py failed on the v2 fixtures"
    LAB = json.load(open(lab_p))
    L = LAB["frames"]
    ramp = L["on/sceneN4/L0__s20260819__0000.png"]
    slope = L["on/synthslope/L0__s20260819__0000.png"]
    slope_off = L["off/synthslope/L0__s20260819__0000.png"]
    stairs = L["on/synthstairs/L0__s20260819__0000.png"]

    def chk(name, cond, extra=""):
        ok.append(bool(cond))
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {extra}")

    print("\n--- fixture 2a: gradual ramp (sceneN4 hard negative, D10 step gate) ---")
    fr = ramp["footprint"]
    n_changed_ramp = int((hm_ramp_on != hm_ramp_off).sum())
    chk("ramp: twin diff DOES build a footprint before the gate",
        fr["cells_raw"] > 0 and fr["comps_raw"] > 0,
        f"cells_raw={fr['cells_raw']} comps_raw={fr['comps_raw']} "
        f"(changed cells={n_changed_ramp})")
    chk("ramp: step gate erases every component",
        fr["cells_kept"] == 0 and fr["comps_kept"] == 0,
        f"cells_kept={fr['cells_kept']} comps_kept={fr['comps_kept']} "
        f"boundary {fr['boundary_pass']}/{fr['boundary_cells']} passing")
    chk("ramp: polar GT all zero -> hard negative stays negative",
        sum(ramp["polar_gt"]) == 0 and ramp["raw_vis"]["int_px"] == 0,
        f"gt={''.join(map(str, ramp['polar_gt']))} int_px={ramp['raw_vis']['int_px']}")
    # ---- D14 preservation proof ------------------------------------------
    pre, ge = ramp["polar_gt_pregate"], ramp["gate_excluded"]
    chk("ramp D14: pregate GT is NON-zero while trained GT is zero "
        "(the gate's work is preserved, not erased)",
        sum(pre) > 0 and sum(ramp["polar_gt"]) == 0 and ge["n"] > 0,
        f"pregate={''.join(map(str, pre))} gate_excluded.n={ge['n']}")
    chk("ramp D14: gate_excluded lists exactly the cells pregate-positive but "
        "not trained-positive",
        ge["cells"] == [i for i, v in enumerate(pre)
                        if v and not ramp["polar_gt"][i]] and ge["n"] == len(ge["cells"]),
        f"cells={ge['cells']}")
    chk("ramp D14: scene ledger exposes the excluded heightmap cells",
        ramp["footprint"]["hm_cells_excluded"] == fr["cells_raw"] - fr["cells_kept"]
        and ramp["footprint"]["hm_cells_excluded"] > 0,
        f"hm_cells_excluded={ramp['footprint']['hm_cells_excluded']}")
    gt0_ramp, n0_ramp = v0_rule_gt(hm_ramp_on, grid)
    chk("ramp: the retired v0 rule WOULD have fired here (gate earns its keep)",
        gt0_ramp.sum() > 0 and n0_ramp > 0,
        f"v0 cells={n0_ramp} v0 gt={''.join(map(str, gt0_ramp))}")

    print(f"\n--- fixture 2b: stairs ({RISER} m risers, {TREAD} m treads) ---")
    ft = stairs["footprint"]
    chk("stairs: sub-threshold risers still clear the step gate",
        ft["cells_raw"] > 0 and ft["cells_kept"] == ft["cells_raw"]
        and ft["comps_kept"] == ft["comps_raw"] >= 1,
        f"cells {ft['cells_raw']}->{ft['cells_kept']} comps "
        f"{ft['comps_raw']}->{ft['comps_kept']} boundary "
        f"{ft['boundary_pass']}/{ft['boundary_cells']}")
    chk("stairs: labelled positive and directly seen",
        sum(stairs["polar_gt"]) > 0 and stairs["tier_strict"] == "V",
        f"gt={''.join(map(str, stairs['polar_gt']))} tier={stairs['tier_strict']} "
        f"int_px={stairs['raw_vis']['int_px']}")
    chk("stairs D14: nothing excluded -> gate_excluded.n == 0 and pregate == polar_gt",
        stairs["gate_excluded"]["n"] == 0 and stairs["gate_excluded"]["cells"] == []
        and stairs["polar_gt_pregate"] == stairs["polar_gt"],
        f"n={stairs['gate_excluded']['n']} "
        f"pregate={''.join(map(str, stairs['polar_gt_pregate']))} "
        f"gt={''.join(map(str, stairs['polar_gt']))}")

    print("\n--- fixture 2c: sloped approach + 1.0 m vertical pit ---")
    fs = slope["footprint"]
    n_changed = int((hm_slope_on != hm_slope_off).sum())
    chk("slope: footprint == exactly the cells the hazard toggle changed (the pit)",
        fs["cells_raw"] == n_changed and fs["cells_kept"] == n_changed,
        f"raw={fs['cells_raw']} kept={fs['cells_kept']} changed={n_changed}")
    chk("slope: pit survives the step gate as one component",
        fs["comps_raw"] == 1 and fs["comps_kept"] == 1,
        f"comps {fs['comps_raw']}->{fs['comps_kept']}")
    chk("slope: pit is labelled and directly seen (tier V)",
        sum(slope["polar_gt"]) > 0 and slope["tier_strict"] == "V",
        f"gt={''.join(map(str, slope['polar_gt']))} tier={slope['tier_strict']} "
        f"int_px={slope['raw_vis']['int_px']}")
    gt0, n0 = v0_rule_gt(hm_slope_on, grid)
    chk("slope: v0 rule swept the far walkway into the footprint",
        n0 > n_changed and gt0[FAR_WALKWAY_CELL] == 1,
        f"v0 cells={n0} vs v2 {n_changed}; v0 gt={''.join(map(str, gt0))}")
    chk("slope: v2 rule leaves the sloped walkway clean (cell "
        f"{FAR_WALKWAY_CELL} = band3/sector E)",
        slope["polar_gt"][FAR_WALKWAY_CELL] == 0,
        f"v2 gt={''.join(map(str, slope['polar_gt']))}")
    chk("slope: int_px references z_off, not cam.ground_z "
        "(no fallback pixels on a void-free twin)",
        slope["raw_vis"]["int_px_fallback"] == 0 and slope["raw_vis"]["int_px"] > 0,
        f"int_px={slope['raw_vis']['int_px']} fallback={slope['raw_vis']['int_px_fallback']}")
    chk("slope: off arm stays empty (twin diff is identically zero)",
        sum(slope_off["polar_gt"]) == 0 and slope_off["footprint"]["cells_raw"] == 0)
    chk("slope D14: a fully-kept component excludes nothing (pregate == polar_gt)",
        slope["polar_gt_pregate"] == slope["polar_gt"]
        and slope["gate_excluded"]["n"] == 0
        and slope["footprint"]["hm_cells_excluded"] == 0,
        f"pregate={''.join(map(str, slope['polar_gt_pregate']))} "
        f"n={slope['gate_excluded']['n']}")
    chk("labels carry the D10/D11 provenance",
        LAB["meta"]["footprint"] == "v2-diff-stepgate"
        and LAB["meta"]["gt_source"] == "derived-heightmapdiff-gridv0-PROVISIONAL"
        and LAB["meta"]["interior_margin_m"] == 0.15
        and LAB["meta"]["rim_tol_m"] == 0.35 and LAB["meta"]["lip_max_pts"] == 200,
        str(LAB["meta"]))

    print("\n--- fixture 2d: gates.py D12 reporting ---")
    r = run("build_manifest.py", "--labels", lab_p, "--on-round", on,
            "--off-round", off, "--out", man_p)
    chk("build_manifest.py runs on the v2 fixtures", r.returncode == 0)
    M = json.load(open(man_p))
    chk("manifest gt_source bumped to the twin-diff string",
        M["meta"]["gt_source"] == "derived-heightmapdiff-gridv0-PROVISIONAL"
        and M["meta"]["footprint"] == "v2-diff-stepgate", str(M["meta"]["gt_source"]))
    mf = {f["frame_id"]: f for f in M["frames"]}
    mramp = mf["on/sceneN4/L0__s20260819__0000.png"]
    chk("manifest D14: every frame carries polar_gt_pregate + gate_excluded, "
        "passed through unaltered",
        all("polar_gt_pregate" in f and "gate_excluded" in f for f in M["frames"])
        and mramp["polar_gt_pregate"] == ramp["polar_gt_pregate"]
        and mramp["gate_excluded"] == ramp["gate_excluded"],
        f"ramp frame pregate={''.join(map(str, mramp['polar_gt_pregate']))} "
        f"excluded n={mramp['gate_excluded']['n']}")
    chk("manifest D14: meta.gate_policy states the train-on-gated contract",
        M["meta"].get("gate_policy") == "train-on-gated; pregate preserved per D14",
        str(M["meta"].get("gate_policy")))
    rep_p = os.path.join(root, "GATES_REPORT.md")
    r = run("gates.py", "--manifest", man_p, "--labels", lab_p, "--out", rep_p,
            "--audit-dir", os.path.join(root, "audit_samples"), "--n-audit", "4")
    rep = open(rep_p).read() if os.path.isfile(rep_p) else ""
    chk("gates.py runs on the v2 fixtures", r.returncode == 0)
    n4_line = [l for l in rep.splitlines() if l.startswith("| sceneN4 |") and "|" in l]
    chk("GATES_REPORT lists sceneN4 in the slope sanity table and it reads OK",
        any(l.strip().endswith("OK |") for l in n4_line), " / ".join(n4_line[-1:]))
    chk("GATES_REPORT carries the per-scene footprint table",
        "footprint v2 per-scene summary" in rep
        and "| synthslope | on |" in rep, "")
    chk("GATES_REPORT warns when the far-E quota cannot be met",
        "**WARNING** only 0 frame(s)" in rep,
        [l for l in rep.splitlines() if l.startswith("**WARNING**")][:1])
    ex_rows = [l for l in rep.splitlines() if l.startswith("| sceneN4 | on |")]
    ex_cols = [c.strip() for c in ex_rows[-1].split("|")] if ex_rows else []
    chk("GATES_REPORT carries the STEP-GATE EXCLUSIONS (D14) table and the ramp row "
        "shows cells excluded at both granularities",
        "## STEP-GATE EXCLUSIONS (D14)" in rep and len(ex_cols) >= 8
        and int(ex_cols[5]) > 0 and ex_cols[6] == "1/1" and int(ex_cols[7]) > 0,
        " ".join(ex_rows[-1:]))
    hold_p = os.path.join(root, "annotations", "hold_scenes.json")
    chk("hold_scenes.json is always written; no D1-D4 scene here so it is []",
        os.path.isfile(hold_p) and json.load(open(hold_p)) == [],
        f"{hold_p} -> {open(hold_p).read().strip() if os.path.isfile(hold_p) else 'MISSING'}")
    for ln in rep.splitlines():
        if ln.startswith(("## ", "| sceneN", "| synth", "**WARNING**", "D12 far-E",
                          "PROVISIONAL-HOLD")):
            print("    " + ln.rstrip())
    print(f"\nfixture: {root}")
    return root


MAKE_SPLIT = os.path.join(os.path.dirname(HERE), "make_split.py")


def hold_fixture(ok):
    """D14(4) hold path: sceneD1's twin arms are identical, so its hazard-ON arm has
    zero positive frames.  That is NOT a designed hard negative (it is not one of
    N1-N5), so gates.py must hold the scene out of every split -- banner at the top
    of the report + machine-readable hold_scenes.json -- rather than fail G2 on it."""
    root = tempfile.mkdtemp(prefix="negobs_hold_")
    hm_flat, s_flat = ramp_world(False)          # flat ground, identical twin arms
    on = write_v2_scene(root, "on", "sceneD1", hm_flat, s_flat)
    off = write_v2_scene(root, "off", "sceneD1", hm_flat, s_flat)
    lab_p = os.path.join(root, "annotations", "labels_v0.json")
    man_p = os.path.join(root, "dataset_manifest_v1.json")
    rep_p = os.path.join(root, "GATES_REPORT.md")
    hold_p = os.path.join(root, "annotations", "hold_scenes.json")

    def chk(name, cond, extra=""):
        ok.append(bool(cond))
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {extra}")

    print("\n--- fixture 3: PROVISIONAL-HOLD (D14 ④) ---")
    r = run("labeler.py", "--on-round", on, "--off-round", off,
            "--grid", os.path.join(HERE, "gridspec_v0.json"), "--out", lab_p)
    assert r.returncode == 0, "labeler.py failed on the hold fixture"
    d1 = json.load(open(lab_p))["frames"]["on/sceneD1/L0__s20260819__0000.png"]
    chk("hold fixture: sceneD1 on-arm is all-negative before AND after the gate "
        "(so it is a G2 zero-positive scene, not a gate victim)",
        sum(d1["polar_gt"]) == 0 and sum(d1["polar_gt_pregate"]) == 0
        and d1["gate_excluded"]["n"] == 0)
    r = run("build_manifest.py", "--labels", lab_p, "--on-round", on,
            "--off-round", off, "--out", man_p)
    assert r.returncode == 0, "build_manifest.py failed on the hold fixture"
    r = run("gates.py", "--manifest", man_p, "--labels", lab_p, "--out", rep_p,
            "--audit-dir", os.path.join(root, "audit_samples"), "--n-audit", "2")
    chk("gates.py runs on the hold fixture", r.returncode == 0)
    rep = open(rep_p).read() if os.path.isfile(rep_p) else ""
    head = rep.splitlines()[:14]
    chk("hold: sceneD1 written to hold_scenes.json",
        os.path.isfile(hold_p) and json.load(open(hold_p)) == ["sceneD1"],
        open(hold_p).read().strip() if os.path.isfile(hold_p) else "MISSING")
    chk("hold: PROVISIONAL-HOLD banner sits at the TOP of GATES_REPORT and names the scene",
        any("PROVISIONAL-HOLD" in l for l in head)
        and any("`sceneD1`" in l for l in head),
        " / ".join(l for l in head if "PROVISIONAL-HOLD" in l)[:120])
    chk("hold: G2 reports the hold instead of failing on it, and the plain "
        "zero-positive list stays empty",
        any(l.startswith("## G2") and "PASS" in l and "PROVISIONAL-HOLD" in l
            for l in rep.splitlines())
        and "on-arm scenes with ZERO positive frames: none" in rep,
        " / ".join(l for l in rep.splitlines() if l.startswith("## G2")))
    for ln in rep.splitlines()[:14]:
        if ln.strip():
            print("    " + ln.rstrip())
    print(f"\nfixture: {root}")
    return hold_p


def split_fixture(ok, hold_p):
    """D14(4) make_split integration: the held scene must land in NO split while
    every PROOF check stays green (they are expressed against the eligible pool)."""
    root = tempfile.mkdtemp(prefix="negobs_split_")
    man_p = os.path.join(root, "dataset_manifest_v1.json")
    out_p = os.path.join(root, "split_v1.json")
    rep_p = os.path.join(root, "SPLIT_PROPOSAL.md")
    scenes = [f"scene{i:02d}" for i in range(1, 29)] + ["sceneN3", "sceneD1"]
    held = json.load(open(hold_p))
    frames = []
    for i, s in enumerate(scenes):
        neg = s in held or s == "sceneN3"
        for j in range(2):
            gt = [0] * 15
            if not neg:
                gt[(i + j) % 15] = 1
            frames.append(dict(frame_id=f"on/{s}/{j:04d}.png", scene_id=s, round="r_on",
                               toggle_state="on", tier=("H" if (i % 3 == 0 and j == 0)
                                                        else "V" if j == 0 else "E"),
                               polar_gt=gt))
            frames.append(dict(frame_id=f"off/{s}/{j:04d}.png", scene_id=s, round="r_off",
                               toggle_state="off", tier="off", polar_gt=[0] * 15))
    json.dump(dict(meta=dict(note="synthetic split fixture"), frames=frames),
              open(man_p, "w"))

    def chk(name, cond, extra=""):
        ok.append(bool(cond))
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {extra}")

    print("\n--- fixture 4: make_split --exclude-scenes (D14 ④) ---")
    r = run(MAKE_SPLIT, "--manifest", man_p, "--out", out_p, "--report", rep_p,
            "--exclude-scenes", "@" + hold_p, "--trials", "4000")
    sp = json.load(open(out_p)) if os.path.isfile(out_p) else {}
    rep = open(rep_p).read() if os.path.isfile(rep_p) else ""
    chk("make_split: every PROOF passes with a scene held out (exit 0)",
        r.returncode == 0, (r.stdout or "").strip().splitlines()[-1:])
    chk("make_split: the held scene is in NO split (train/val/test all clean)",
        all("sceneD1" not in sp.get(k, []) for k in ("train", "val", "test"))
        and sp.get("hold") == ["sceneD1"]
        and len(sp.get("train", [])) + len(sp.get("val", [])) + len(sp.get("test", []))
        == len(scenes) - 1,
        f"train={len(sp.get('train', []))} val={len(sp.get('val', []))} "
        f"test={len(sp.get('test', []))} hold={sp.get('hold')}")
    chk("SPLIT_PROPOSAL lists it under PROVISIONAL-HOLD (아침 결재 대상) and marks the "
        "per-scene row HOLD",
        "## PROVISIONAL-HOLD (아침 결재 대상)" in rep
        and "| sceneD1 | 4 |" in rep and "| sceneD1 | **HOLD** |" in rep
        and "PROOF-10" in rep,
        [l for l in rep.splitlines() if l.startswith("PROOF-10")][:1])
    for ln in (r.stdout or "").splitlines():
        if ln.startswith(("PROOF-1 ", "PROOF-3", "PROOF-4", "PROOF-6", "PROOF-10", "[split]")):
            print("    " + ln.rstrip())
    print(f"\nfixture: {root}")
    return root


def main():
    ok_legacy, ok_v2, ok_hold = [], [], []
    legacy_fixture(ok_legacy)
    slope_fixture(ok_v2)
    hold_p = hold_fixture(ok_hold)
    split_fixture(ok_hold, hold_p)
    print(f"\nRESULT legacy fixture : {sum(ok_legacy)}/{len(ok_legacy)} checks passed")
    print(f"RESULT footprint v2   : {sum(ok_v2)}/{len(ok_v2)} checks passed")
    print(f"RESULT D14 hold/split : {sum(ok_hold)}/{len(ok_hold)} checks passed")
    ok = ok_legacy + ok_v2 + ok_hold
    print(f"RESULT: {sum(ok)}/{len(ok)} checks passed")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
