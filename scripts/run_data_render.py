#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data-render driver — scene x lighting condition x random camera.

    scenes (outer, one Isaac process each)
      └─ lighting conditions (inner, ONE boot, runtime HDRI swap)
           └─ camera samples (innermost)

That nesting is the structural decision spec §6.3 made and SP-4 measured:
`t_swap` = 1.4 s against a 30 s process-split threshold, and SP-2 measured the
end-to-end saving of keeping conditions inside one boot at **3.29x** (693 cuts:
44.2 min in-process vs 145.2 min as 7 separate rounds). Conditions outside the
camera loop, not inside, so the sky is swapped `N_light - 1` times per scene
instead of once per cut.

Two modes in one file so the in-process half cannot drift from the driver half:

    --plan                 print the plan + budget, render nothing
    (default)              drive: one subprocess per scene
    --scene-proc ...       the in-process half (invoked by the driver)

Output goes to `dataset/<run>/<split>/<scene>/` — a tree `regression_check.py`
cannot reach, because it is only ever pointed at `--scenes 'look_check/scene*'`
(spec D1/B2). Nothing is ever written into a `look_check/<scene>/` directory.

usage:
  python3 scripts/run_data_render.py --plan --scenes sceneN1,scene02 \\
      --conds L0,L7,L5 --cams 8
  bash  scripts/rounds/run_260730_data_mini.sh          # the validated wrapper
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import variation_kit as vk                                        # noqa: E402

ALL_SCENES = sorted(vk.AZ_LEDGER)


# ===========================================================================
# scene file resolution
# ===========================================================================
def scene_files():
    out = {}
    for sub in ("main", "batch1"):
        for f in sorted(glob.glob(os.path.join(REPO, "scenes", sub,
                                               "scene*.py"))):
            b = os.path.basename(f)
            if b.startswith("scene_common"):
                continue
            out[b.split("_")[0]] = (f, sub)
    return out


SCENE_FILES = scene_files()


# ===========================================================================
# plan + budget
# ===========================================================================
def build_plan(scenes, conds, n_cam, base_seed):
    """(pairs, refused). A (scene, cond) pair the ledger forbids is REFUSED with
    its reason and recorded — never silently swapped for a different condition,
    because a silent substitution is how a condition distribution stops being
    independent of the label (spec B6)."""
    pairs, refused = [], []
    for s in scenes:
        for c in conds:
            ok, why = vk.condition_allowed(s, c, role=vk.ROLE_DATA)
            (pairs if ok else refused).append(
                dict(scene=s, cond=c, n=n_cam) if ok
                else dict(scene=s, cond=c, reason=why))
    return pairs, refused


def print_budget(pairs, n_cam, n_scene):
    n_cut = sum(p["n"] for p in pairs)
    n_light = max(1, len({p["cond"] for p in pairs}))
    t_render = n_cut * vk.T_CUT_DATA * (1.0 + vk.R_REJECT_MEASURED)
    t_boot = n_scene * vk.T_BOOT
    t_sky = sum(max(0, len([1 for p in pairs if p["scene"] == s]) - 1)
                for s in {p["scene"] for p in pairs}) * vk.T_SWAP
    tot = t_render + t_boot + t_sky
    print(f"\n[budget]  measured constants: t_cut {vk.T_CUT_DATA} s "
          f"(spec assumed 0.7) · t_boot {vk.T_BOOT} s · t_swap {vk.T_SWAP} s · "
          f"r_reject {vk.R_REJECT_MEASURED}")
    print(f"          {n_cut} cuts · {n_scene} scenes · {n_light} conditions "
          f"· {n_cam} cameras")
    print(f"          render {t_render / 60:.1f} min + boot {t_boot / 60:.1f} min"
          f" + sky {t_sky / 60:.2f} min = {tot / 60:.1f} min "
          f"({tot / 3600:.2f} h), overhead "
          f"{100 * (t_boot + t_sky) / max(1e-9, tot):.0f} %")
    return tot


# ===========================================================================
# driver
# ===========================================================================
def drive(args):
    vk.assert_role_gate()      # will pass: we set role=data below
    run = args.run
    root = vk.data_root(run)
    os.makedirs(root, exist_ok=True)
    scenes = [s.strip() for s in args.scenes.split(",") if s.strip()]
    conds = [c.strip() for c in args.conds.split(",") if c.strip()]
    for s in scenes:
        vk.ledger(s)
        if s not in SCENE_FILES:
            raise SystemExit(f"[data] no scene file for {s!r}")
    for c in conds:
        if c not in vk.CONDITIONS:
            raise SystemExit(f"[data] unknown condition {c!r} "
                             f"(have {list(vk.CONDITIONS)})")

    pairs, refused = build_plan(scenes, conds, args.cams, args.seed)
    print(f"=== data run {run} ===")
    print(f"scenes {scenes}\nconds  {conds}\ncams   {args.cams} "
          f"· seed {args.seed}")
    for r in refused:
        print(f"[refused] {r['scene']} x {r['cond']}: {r['reason']}")
    for s in scenes:
        print(f"  {s:10s} split={vk.split_of(s):5s} "
              f"class={vk.ledger(s)['cls']:2s} "
              f"daz_data={vk.ledger(s)['daz_data']:.0f} "
              f"conds={[p['cond'] for p in pairs if p['scene'] == s]}")
    print_budget(pairs, args.cams, len({p["scene"] for p in pairs}))
    if args.plan:
        return 0

    # --- pre-flight: every lookfix derivative must already exist -----------
    # SP-4 §3.4: the first `ensure_noon_lookfix` call for a new sky costs
    # 1.97-2.00 s of CPU and writes an 18 MB EXR. Inside a run that is a silent
    # stall on the first cut of each condition, so it happens here instead.
    pre = prepare_assets(sorted({p["cond"] for p in pairs}))
    if pre:
        print(f"[assets] {pre}")

    manifest_path = os.path.join(root, "manifest.json")
    mf = _load_manifest(manifest_path)
    mf.setdefault("run", run)
    mf.setdefault("started", datetime.datetime.now().isoformat(timespec="seconds"))
    mf["seed"] = args.seed
    mf["cams"] = args.cams
    mf["refused"] = refused
    mf["git_head"] = _git("rev-parse", "--short", "HEAD")
    mf["git_branch"] = _git("rev-parse", "--abbrev-ref", "HEAD")
    mf.setdefault("scenes", {})
    _save_manifest(manifest_path, mf)

    t_all = time.time()
    for s in scenes:
        my = [p["cond"] for p in pairs if p["scene"] == s]
        if not my:
            continue
        done = mf["scenes"].get(s, {}).get("done_conds", [])
        todo = [c for c in my if c not in done] if args.resume else my
        if not todo:
            print(f"[skip] {s} — all {len(my)} conditions already done")
            continue
        f, sub = SCENE_FILES[s]
        out_dir = os.path.join(root, vk.split_of(s), s)
        os.makedirs(out_dir, exist_ok=True)
        env = dict(os.environ)
        env.update(
            NEGOBS_RENDER_ROLE="data",
            NEGOBS_SEED=str(args.seed),
            NEGOBS_LIGHT_COND=",".join(todo),
            NEGOBS_CAM_MODE="random",
            NEGOBS_CAM_N=str(args.cams),
            # The judge render arm, unchanged, so a data cut and a judge cut of
            # the same scene differ only in what this round varies.
            NEGOBS_CAPTURE="1", NEGOBS_CAPTURE_MODE="pt",
            NEGOBS_PT_FAST="1", NEGOBS_LOOK_V1="1",
            NEGOBS_DETAIL_SCALE="2", NEGOBS_DETAIL_ROUGH_GAIN="0",
            PYTHONUNBUFFERED="1",
        )
        cmd = [sys.executable, os.path.abspath(__file__), "--scene-proc",
               f, s, out_dir, ",".join(todo), str(args.cams), str(args.seed)]
        print(f"\n[render] {s} ({sub}) -> {out_dir}\n         conds {todo}",
              flush=True)
        t0 = time.time()
        rc = subprocess.run(cmd, env=env, cwd=REPO).returncode
        dt = time.time() - t0
        rec = _read_scene_json(out_dir)
        n = len(rec.get("cuts", []))
        mf["scenes"][s] = dict(
            split=vk.split_of(s), out=os.path.relpath(out_dir, REPO),
            sec=round(dt, 1), exit=rc, cuts=n,
            done_conds=sorted(set(done) | set(todo)) if rc == 0 else done,
            sec_per_cut=round(dt / n, 3) if n else None)
        _save_manifest(manifest_path, mf)
        print(f"[render] {s} exit={rc} cuts={n} {dt:.0f}s "
              f"({dt / max(1, n):.2f} s/cut)", flush=True)

    tot = time.time() - t_all
    n_cut = sum(v.get("cuts", 0) for v in mf["scenes"].values())
    mf["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    mf["total_sec"] = round(tot, 1)
    mf["total_cuts"] = n_cut
    mf["measured_t_cut"] = round(tot / n_cut, 3) if n_cut else None
    _save_manifest(manifest_path, mf)
    print(f"\n=== {run}: {n_cut} cuts in {tot / 60:.1f} min "
          f"(t_cut {mf['measured_t_cut']} s vs SP-3's {vk.T_CUT_DATA} s) ===")
    return 0


def prepare_assets(conds):
    """Generate every lookfix derivative the run will need, up front."""
    sys.path.insert(0, REPO)
    import scene_common as sc
    made = []
    for cid in conds:
        c = vk.CONDITIONS[cid]
        src = os.path.join(REPO, "assets", c["hdri"])
        if not os.path.isfile(src):
            raise SystemExit(
                f"[data] condition {cid} needs assets/{c['hdri']}, which is "
                f"absent. Procure it: python assets/download_sky.py --ladder")
        if c["lookfix"]:
            out = sc.ensure_noon_lookfix(src)
            made.append(f"{cid}:{os.path.basename(out)}")
    return " ".join(made)


def _git(*a):
    try:
        return subprocess.run(["git", "-C", REPO, *a], capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return ""


def _load_manifest(p):
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_manifest(p, mf):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(mf, f, ensure_ascii=False, indent=1)


def _read_scene_json(out_dir):
    p = os.path.join(out_dir, "variation.json")
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


# ===========================================================================
# in-process half — monkey-patches, then runs the scene file untouched
# ===========================================================================
def scene_proc(scene_file, scene_key, out_dir, conds, n_cam, base_seed):
    """Runs inside Isaac. Patches three `scene_common` entry points and then
    executes the scene file under `runpy` with `run_name="__main__"`, so no scene
    file is modified and no scene file needs to know this exists.

    The patched points and why each one:
      grid_views      — only to LEARN the scene's `gy` (walk axis). The lateral
                        camera offset is defined relative to it, and it differs
                        per scene (scene01 -2.75, scene04 0.0).
      plan_ground     — only to CAPTURE the ground plan, so `frame_budget` can be
                        reused as an advisory near-field read (see below).
      setup_lighting  — only to capture the returned `LightingControl`.
      capture_pipeline— replaced by the condition x camera loop.
    """
    import math
    import runpy
    scene_dir = os.path.dirname(os.path.abspath(scene_file))
    sys.path.insert(0, scene_dir)
    import scene_common as sc
    try:
        import ground_kit as gk
    except Exception:
        gk = None

    cond_ids = [c for c in conds.split(",") if c]
    n_cam = int(n_cam)
    base_seed = int(base_seed)
    role = vk.assert_role_gate()
    if role != vk.ROLE_DATA:
        raise SystemExit(f"[data] scene-proc requires role=data, got {role}")
    for cid in cond_ids:
        if vk.CONDITIONS[cid]["pt_only"] \
                and os.environ.get("NEGOBS_CAPTURE_MODE") != "pt":
            raise SystemExit(
                f"[data] condition {cid} is PT-only (a sunless dome under RT is "
                f"flat light — sceneC1:239), but NEGOBS_CAPTURE_MODE="
                f"{os.environ.get('NEGOBS_CAPTURE_MODE')!r}")

    _key = scene_key
    hold = {"gy": 0.0, "plan": None}
    _orig_grid = sc.grid_views
    _orig_setup = sc.setup_lighting

    def _grid(gy, *a, **k):
        hold["gy"] = float(gy)
        return _orig_grid(gy, *a, **k)

    def _setup(stage, lp, off, scene_key=None):
        # `scene_key` is closed over, not read from a global: the scene files call
        # this with three positional args and never pass it.
        ctl = _orig_setup(stage, lp, off, scene_key=scene_key or _key)
        hold["ctl"] = ctl
        hold["stage"] = stage
        hold["light0"] = {k: (list(v) if isinstance(v, (list, tuple)) else v)
                          for k, v in lp.items()}
        return ctl

    if gk is not None:
        _orig_plan = gk.plan_ground

        def _plan(*a, **k):
            p = _orig_plan(*a, **k)
            hold["plan"] = p
            return p
        gk.plan_ground = _plan

    def _capture(sim_app, views, out_dir_default, set_render_mode_fn,
                 look_from_fn):
        import carb
        from pxr import Gf, Sdf, UsdGeom
        from omni.kit.viewport.utility import (get_active_viewport,
                                               capture_viewport_to_file)
        ctl = hold.get("ctl")
        if ctl is None:
            raise SystemExit("[data] setup_lighting was never called")
        stage = hold["stage"]
        gy = hold["gy"]

        pre = vk.AabbPrefilter(stage)
        print(f"[data] AABB world {pre.n} prims · gy {gy}", flush=True)

        # --- self-authored camera (spec D3, SP-7 conventions) -------------
        CAM = "/World/DataCam"
        cam = UsdGeom.Camera.Define(stage, CAM)
        cam.CreateHorizontalApertureAttr(vk.APERTURE)
        cam.CreateVerticalApertureAttr(vk.APERTURE * vk.RES_H / vk.RES_W)
        cam.CreateClippingRangeAttr(Gf.Vec2f(0.01, 1000.0))
        # ONE matrix op, not rotateXYZ — SP-7: removes every rotation-order
        # question, measured roll error <= 0.005 deg, hFOV error <= 0.047 deg.
        c_m = UsdGeom.Xformable(cam.GetPrim()).AddTransformOp()
        vp = get_active_viewport()
        was = str(vp.camera_path)
        vp.camera_path = Sdf.Path(CAM)
        print(f"[data] viewport camera {was} -> {vp.camera_path}", flush=True)

        set_render_mode_fn("PathTracing")
        st = carb.settings.get_settings()
        st.set("/rtx/pathtracing/spp", sc.PT_FAST["spp"])
        st.set("/rtx/pathtracing/totalSpp", sc.PT_FAST["total_spp"])
        st.set("/app/renderer/rtSubframes", sc.PT_FAST["subframes"])
        for _ in range(40):
            sim_app.update()

        def cap(fp):
            """Robust capture. The 40-update poll `capture_pipeline` uses is too
            small for a loop that re-authors the camera matrix AND focalLength
            every cut: in SP-3 it reported 35 of 200 captures failed when all 35
            files had in fact been written moments later (spike §6.7). The budget
            is raised and a settle is guaranteed before polling, and `ok=False`
            here means ABSENT, not "not yet stable"."""
            capture_viewport_to_file(vp, file_path=fp)
            for _ in range(6):
                sim_app.update()
            prev = -1
            for _ in range(150):
                sim_app.update()
                if os.path.isfile(fp):
                    sz = os.path.getsize(fp)
                    if sz > 0 and sz == prev:
                        return True
                    prev = sz
            return os.path.isfile(fp)

        os.makedirs(out_dir, exist_ok=True)
        rec_path = os.path.join(out_dir, "variation.json")
        prev_rec = _read_scene_json(out_dir)
        cuts = {c["file"]: c for c in prev_rec.get("cuts", [])}

        t_run = time.time()
        for cid in cond_ids:
            c = ctl.apply_cond(cid)
            print(f"[data] {scene_key} cond {cid} "
                  f"dome {c['dome_intensity']} sun {c['sun_intensity']} "
                  f"elev {c['sun_elev']} angle {c['sun_angle_deg']} "
                  f"evc {c['ev_comp']:+.2f}", flush=True)
            for i in range(n_cam):
                s = vk.sample_camera(scene_key, i, base_seed, gy=gy)
                d_az = vk.sample_daz(scene_key, cid, i, base_seed,
                                     role=vk.ROLE_DATA)
                ctl(d_az)
                # Ground-relative height: `grid_views` uses ABSOLUTE eye z, which
                # buries the camera in the 7 descending scenes. The ground is
                # found per sample instead (spec §3.3 CAM-3).
                gz = pre.ground_z(-s["d"], s["y"])
                eye = (-s["d"], s["y"], gz + s["h_rel"])
                fname = f"{cid}__s{base_seed}__{i:04d}.png"
                fp = os.path.join(out_dir, fname)
                if fname in cuts and os.path.isfile(fp) \
                        and cuts[fname].get("ok"):
                    continue                        # resumable
                st1 = pre.check(eye, s["yaw"], s["pitch"], s["hfov"])
                rows = vk.look_at_rows(eye, s["yaw"], s["pitch"], s["roll"])
                c_m.Set(Gf.Matrix4d(*[v for r in rows for v in r]))
                cam.GetFocalLengthAttr().Set(vk.focal_for_hfov(s["hfov"]))
                for _ in range(sc.PT_FAST["warmup"]):
                    sim_app.update()
                ok = cap(fp)
                # flat_near is a JUDGE filter: on the data channel it would throw
                # away the hardest 2 % of near-range samples for a reason imported
                # from a render-failure detector (SP-3 §4.3 rider 2).
                img = (vk.image_filter(fp, flat_near=False)
                       if os.path.isfile(fp) else None)
                fb = _frame_budget_advice(gk, hold["plan"], s, s["y"])
                cuts[fname] = dict(
                    file=fname, scene=scene_key, cond=cid, seed=base_seed,
                    idx=i, ok=bool(ok),
                    cam=dict(eye=[round(v, 4) for v in eye], ground_z=round(gz, 4),
                             d=s["d"], h_rel=s["h_rel"], yaw=s["yaw"],
                             pitch=s["pitch"], roll=s["roll"], hfov=s["hfov"],
                             focal=round(vk.focal_for_hfov(s["hfov"]), 5),
                             aperture=vk.APERTURE, tier=s["tier"]),
                    light=dict(cond=cid, hdri=c["hdri"], lookfix=c["lookfix"],
                               dome_intensity=c["dome_intensity"],
                               sun_intensity=c["sun_intensity"],
                               sun_elev=c["sun_elev"],
                               sun_angle_deg=c["sun_angle_deg"],
                               hdri_sun_rotz_offset=c["hdri_sun_rotz_offset"],
                               sun_az_offset=ctl.sun_az_offset, d_az=d_az,
                               dome_rot=round(
                                   float(ctl.lp["noon_dome_rot"])
                                   + ctl.sun_az_offset + d_az, 3)),
                    expo=dict(ev_comp=c["ev_comp"],
                              filmIso=round(100.0 * 2.0 ** c["ev_comp"], 2),
                              fNumber=5.0, tonemap_op=6),
                    render=dict(mode="pt", total_spp=sc.PT_FAST["total_spp"],
                                warmup=sc.PT_FAST["warmup"]),
                    stage1=st1, img=img, frame_budget=fb)
                if (i + 1) % 8 == 0 or i + 1 == n_cam:
                    _write_scene_json(rec_path, scene_key, base_seed, gy,
                                      cond_ids, cuts, t_run,
                                      hold.get("light0"))
                    print(f"[data] {scene_key} {cid} {i + 1}/{n_cam} "
                          f"({time.time() - t_run:.0f}s)", flush=True)
        ctl.apply_cond("L0")
        _write_scene_json(rec_path, scene_key, base_seed, gy, cond_ids, cuts,
                          t_run, hold.get("light0"))
        del math

    sc.grid_views = _grid
    sc.setup_lighting = _setup
    sc.capture_pipeline = _capture
    sys.argv = [scene_file]
    runpy.run_path(scene_file, run_name="__main__")


def _frame_budget_advice(gk, plan, s, gy):
    """Reuse `ground_kit.frame_budget` as an ADVISORY near-field read.

    Where a scene has a ground plan, `frame_budget` already decides B1-B12 —
    element pixel occupancy, occlusion and GT rule violations — without
    rendering, at a given camera height and distance. Feeding it the sampled
    (h, d, gy) gives a free analytic answer to "is there any legible ground
    content in this frame". It is recorded, NOT enforced: its gates are
    calibrated for the h0.3 presets, and SP-3's one observed
    prefilter/image disagreement went the image's way, so the image filter stays
    the authority.
    """
    if gk is None or plan is None:
        return None
    try:
        b = gk.frame_budget(plan, h=s["h_rel"], dists=(s["d"],), gy=gy)  # gy = the sampled lateral y
        g = b.get("gates", {})
        return dict(hard_fail=[k for k, v in g.items()
                               if v.get("hard") and not v.get("pass")],
                    soft_fail=[k for k, v in g.items()
                               if not v.get("hard") and not v.get("pass")])
    except Exception as e:
        return dict(error=str(e)[:120])


def _write_scene_json(path, scene, seed, gy, conds, cuts, t0, light0):
    ok = [c for c in cuts.values() if c.get("ok")]
    rej = [c for c in cuts.values()
           if c.get("img") and c["img"].get("reject")]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dict(
            scene=scene, seed=seed, gy=gy, conds=conds,
            split=vk.split_of(scene), ledger=vk.ledger(scene),
            scene_light_baseline=light0,
            n=len(cuts), n_ok=len(ok), n_rejected=len(rej),
            r_reject=round(len(rej) / max(1, len(cuts)), 4),
            sec=round(time.time() - t0, 1),
            sec_per_cut=round((time.time() - t0) / max(1, len(cuts)), 3),
            cuts=sorted(cuts.values(), key=lambda c: (c["cond"], c["idx"]))),
            f, ensure_ascii=False, indent=1)


# ===========================================================================
def main(argv):
    if argv and argv[0] == "--scene-proc":
        return scene_proc(*argv[1:])
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default="260730_data_mini",
                    help="run stamp, <yymmdd>_<wave>_<purpose>")
    ap.add_argument("--scenes", default=",".join(ALL_SCENES))
    ap.add_argument("--conds", default="L0")
    ap.add_argument("--cams", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260730)
    ap.add_argument("--plan", action="store_true",
                    help="print plan and budget, render nothing")
    ap.add_argument("--resume", action="store_true", default=True)
    ap.add_argument("--no-resume", dest="resume", action="store_false")
    return drive(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
