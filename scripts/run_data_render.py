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
            # [GT-113 W2] The standing NEGOBS_DETAIL_SCALE=2 override is removed:
            # it silently nullified GT-108's per-class det_scale in every render.
            # The class/family table now carries in-band values itself; the env
            # knob is an A/B sweep arm only. (ROUGH_GAIN=0 was the default anyway.)
            NEGOBS_CAPTURE="1", NEGOBS_CAPTURE_MODE="pt",
            NEGOBS_PT_FAST="1", NEGOBS_LOOK_V1="1",
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
    mf["total_cuts"] = n_cut
    # Per-INVOCATION, and named so. A resumed run's wall time divided by the
    # cumulative cut count is a meaningless number (the first resume of this
    # round produced "0.703 s/cut" for a 51 s pass over 8 new cuts); the honest
    # per-cut figures are the per-scene ones, which the checker reports.
    mf.setdefault("invocations", []).append(dict(
        finished=mf["finished"], sec=round(tot, 1),
        scenes=[s for s in scenes if s in mf["scenes"]],
        cuts_after=n_cut))
    mf["total_sec"] = round(sum(i["sec"] for i in mf["invocations"]), 1)
    mf["t_cut_per_scene"] = {k: v.get("sec_per_cut")
                             for k, v in mf["scenes"].items()}
    _save_manifest(manifest_path, mf)
    print(f"\n=== {run}: {n_cut} cuts total, this pass {tot / 60:.1f} min · "
          f"per-scene s/cut {mf['t_cut_per_scene']} "
          f"vs SP-3's {vk.T_CUT_DATA} s ===")
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

        # Opt-in depth sidecar (spec D4). Attached HERE — after the camera is
        # bound, before the render-settings block below — so that block
        # re-asserts /rtx/pathtracing/* over anything the render product
        # disturbed. Unset NEGOBS_DATA_SIDECARS => `depth_ann is None` and every
        # branch guarded by it below is dead.
        sidecars = _sidecars_on()
        depth_ann, depth_rp = (_depth_attach(CAM, sim_app) if sidecars
                               else (None, None))
        # Opt-in ID-mask sidecar (v3 P-5). Rides the render product the depth
        # annotator already made — a second render product would double the
        # post-render cost for no gain. `None` unless NEGOBS_SEG_SIDECAR=1.
        seg_ann = _seg_attach(depth_rp, sim_app) if sidecars else None

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
        if sidecars:
            # Once per scene process: geometry does not move between cuts, and
            # the hazard arm is fixed for the whole process (spec D5).
            try:
                # the scene module's own globals: _capture's caller is the
                # scene file's main(), see _scene_oracle
                try:
                    _ns = sys._getframe(1).f_globals
                except Exception:
                    _ns = None
                _heightmap_write(pre, out_dir, scene_key, _ns)
            except Exception as e:
                print(f"[sidecar] heightmap FAILED — {type(e).__name__}: "
                      f"{str(e)[:200]}", flush=True)
        rec_path = os.path.join(out_dir, "variation.json")
        prev_rec = _read_scene_json(out_dir)
        cuts = {c["file"]: c for c in prev_rec.get("cuts", [])}

        # Opt-in camera-band override (D19 (1), boost rounds). `None` unless
        # NEGOBS_CAM_BAND_OVERRIDE is set, and then `_camband_redraw` below is
        # never called — see the section at the bottom of this file.
        camband = _camband_resolve(scene_key)

        t_run = time.time()
        for cid in cond_ids:
            c = ctl.apply_cond(cid)
            print(f"[data] {scene_key} cond {cid} "
                  f"dome {c['dome_intensity']} sun {c['sun_intensity']} "
                  f"elev {c['sun_elev']} angle {c['sun_angle_deg']} "
                  f"evc {c['ev_comp']:+.2f}", flush=True)
            for i in range(n_cam):
                s = vk.sample_camera(scene_key, i, base_seed, gy=gy)
                if camband is not None:
                    s = _camband_redraw(s, camband, scene_key, i, base_seed)
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
                        and cuts[fname].get("ok") \
                        and (depth_ann is None
                             or (cuts[fname].get("depth")
                                 and os.path.isfile(os.path.join(
                                     out_dir, cuts[fname]["depth"])))):
                    continue                        # resumable
                st1 = pre.check(eye, s["yaw"], s["pitch"], s["hfov"])
                rows = vk.look_at_rows(eye, s["yaw"], s["pitch"], s["roll"])
                c_m.Set(Gf.Matrix4d(*[v for r in rows for v in r]))
                cam.GetFocalLengthAttr().Set(vk.focal_for_hfov(s["hfov"]))
                for _ in range(sc.PT_FAST["warmup"]):
                    sim_app.update()
                ok = cap(fp)
                # Depth AFTER the RGB capture returns: `cap` has already waited
                # for the PathTracing accumulation to settle, so this is the
                # depth of the frame that was written, not of the frame before.
                depth_name, depth_how = None, None
                if depth_ann is not None and ok:
                    arr, depth_how = _depth_fetch(depth_ann, sim_app,
                                                  sc.PT_FAST["subframes"])
                    if arr is not None:
                        depth_name = _depth_write(arr, fp)
                    else:
                        print(f"[sidecar] {fname}: no depth ({depth_how})",
                              flush=True)
                seg_name, seg_how, seg_n = None, None, None
                if seg_ann is not None and ok:
                    sarr, smap, seg_how = _seg_fetch(seg_ann, sim_app,
                                                     sc.PT_FAST["subframes"])
                    if sarr is not None:
                        seg_name, seg_n = _seg_write(sarr, smap, fp)
                    else:
                        print(f"[sidecar] {fname}: no idseg ({seg_how})",
                              flush=True)
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
                if depth_name:
                    cuts[fname]["depth"] = depth_name
                    cuts[fname]["depth_fetch"] = depth_how
                if seg_name:
                    cuts[fname]["idseg"] = seg_name
                    cuts[fname]["idseg_fetch"] = seg_how
                    cuts[fname]["idseg_n_ids"] = seg_n
                if (i + 1) % 8 == 0 or i + 1 == n_cam:
                    _write_scene_json(rec_path, scene_key, base_seed, gy,
                                      cond_ids, cuts, t_run,
                                      hold.get("light0"))
                    print(f"[data] {scene_key} {cid} {i + 1}/{n_cam} "
                          f"({time.time() - t_run:.0f}s)", flush=True)
        ctl.apply_cond("L0")
        _write_scene_json(rec_path, scene_key, base_seed, gy, cond_ids, cuts,
                          t_run, hold.get("light0"))
        if seg_ann is not None:
            _seg_detach(seg_ann, sim_app)
        if depth_ann is not None:
            _depth_detach(depth_ann, depth_rp, sim_app)
            # Hard exit, sidecar arm ONLY. Measured on the 08-19 probe: with a
            # replicator render product alive, Kit's plugin unload faults
            # ("omni.syntheticdata.plugin Failed to acquire interface
            # omni::graph::core::INode while unloading all plugins") and the
            # subprocess dies with SIGSEGV *after* every artefact is already on
            # disk. Detaching the annotator and destroying the render product
            # first (above) does not prevent it. That -11 is not cosmetic:
            # `drive()` only advances `done_conds` when the subprocess returned
            # 0 (:202), so the round would lose its scene-level resume and every
            # scene would read as a failure in the manifest.
            #
            # Nothing is skipped by exiting here. variation.json and every
            # sidecar are already written; and the scene's own
            # `simulation_app.close()` after `capture_pipeline` has ALREADY been
            # unreachable at this HEAD, because the `del math` below raises
            # UnboundLocalError (`math` is imported in `scene_proc`, so `del`
            # makes it a local of `_capture` that is never assigned). That
            # pre-existing defect is left exactly as it is — it fires in the
            # default path too, harmlessly, and a render night is not when to
            # change the default path.
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(0)
        del math

    sc.grid_views = _grid
    sc.setup_lighting = _setup
    sc.capture_pipeline = _capture
    sys.argv = [scene_file]
    runpy.run_path(scene_file, run_name="__main__")


# ===========================================================================
# opt-in camera band override — NEGOBS_CAM_BAND_OVERRIDE (D19 (1), boost rounds)
# ===========================================================================
# NOTHING in this section changes a default round. With the variable unset,
# `_camband_resolve` returns None on its first statement, `_camband_redraw` is
# never called, and every camera is byte-for-byte what `vk.sample_camera`
# produced. Same discipline as the sidecar section below.
#
# WHY. The 08-19 corpus draws d LogU[1.2, 12] and h U[0.25, 1.90] across the
# whole band, so the corners that generate occluded (H) and rim-only (E) frames
# are sampled thinly — test ended with H 21 / E 9. D19 (1) declares two biased
# bands for the additive boost rounds:
#     H-boost  {"d_min":6,"d_max":12,"h_min":0.25,"h_max":1.0}   far + low
#     E-boost  {"d_min":6,"d_max":12,"h_min":1.2,"h_max":1.9}    far + high
# Only the keys PRESENT in the JSON are overridden; an absent key keeps its
# `vk.CAM_DIST` value. The DISTRIBUTION FAMILY is unchanged — d stays
# log-uniform, h stays uniform (`variation_kit.py:615-617`) — and
# pitch / yaw / roll / hfov / yoff are never touched at all.
#
# WHICH RNG STREAM. The redraw uses its own stream, `vk.rng(scene, "camband",
# idx, seed)`, not the "cam" stream `sample_camera` already consumed. Two
# consequences, both wanted:
#   * yaw / pitch / roll / hfov / y for cut i are the SAME numbers the unbiased
#     sampler drew for that cut, so d and h are the only axes that moved;
#   * the stream is a pure function of (scene, idx, seed) exactly like every
#     other derived stream (`variation_kit.py:121-137`), so the hazard-on and
#     hazard-off arms of a boost round stay exact twins (D2's whole point).
#
# CAM-2. `vk.CAM2_SCENES` (scene02, scene15, sceneD4, scene11) carry a
# STRUCTURAL h <= `vk.CAM2_H_MAX` = 1.20 ceiling (`variation_kit.py:592-595`) —
# above it the camera is inside geometry. The requested h band is INTERSECTED
# with that ceiling and can never be pushed past it. If the intersection comes
# out empty or degenerate — which is exactly what E-boost [1.2, 1.9] does to a
# CAM-2 scene — the CAP WINS: the scene falls back to its capped base h band
# and prints a line saying the boost there is distance-only. A silent
# ceiling-break or a silent zero-width band would both be worse.
#
# REJECTION LOGIC IS UNTOUCHED. The override only changes the numbers in `s`;
# `pre.ground_z`, `pre.check` (stage 1) and `vk.image_filter` (stage 2) all run
# afterwards on the overridden eye exactly as before.
CAMBAND_ENV = "NEGOBS_CAM_BAND_OVERRIDE"
CAMBAND_KEYS = ("d_min", "d_max", "h_min", "h_max")
# metres. A band narrower than this is treated as empty: 24 cuts at one fixed
# height is not a sample, it is a constant.
CAMBAND_MIN_WIDTH = 0.01


def _camband_resolve(scene_key):
    """Effective `(d_lo, d_hi, h_lo, h_hi)` for this scene, or None when the
    override is absent. Prints one line per scene process. Raises SystemExit on
    a malformed spec — a boost round must fail loudly, never fall back to the
    default band while still writing into a directory named `*_boost_*`."""
    raw = os.environ.get(CAMBAND_ENV)
    if not raw:
        return None
    try:
        ov = json.loads(raw)
        if not isinstance(ov, dict):
            raise ValueError("not a JSON object")
        unknown = sorted(k for k in ov if k not in CAMBAND_KEYS)
        if unknown:
            raise ValueError(f"unknown key(s) {unknown}; "
                             f"expected any of {list(CAMBAND_KEYS)}")
        ov = {k: float(v) for k, v in ov.items()}
    except Exception as e:
        raise SystemExit(f"[camband] {CAMBAND_ENV}={raw!r} is not usable — "
                         f"{type(e).__name__}: {e}")

    b_d_lo, b_d_hi = vk.CAM_DIST["d"]
    b_h_lo, b_h_hi = vk.CAM_DIST["h"]
    cap = vk.CAM2_H_MAX if scene_key in vk.CAM2_SCENES else None
    if cap is not None:                       # the tier ceiling, as sampled
        b_h_hi = min(b_h_hi, cap)

    d_lo = ov.get("d_min", b_d_lo)
    d_hi = ov.get("d_max", b_d_hi)
    r_h_lo = ov.get("h_min", b_h_lo)
    r_h_hi = ov.get("h_max", b_h_hi)

    if cap is None:
        h_lo, h_hi = r_h_lo, r_h_hi
    else:
        i_lo, i_hi = max(r_h_lo, vk.CAM_DIST["h"][0]), min(r_h_hi, cap)
        if i_hi - i_lo < CAMBAND_MIN_WIDTH:
            print(f"[camband] {scene_key}: CAM-2 CEILING WINS — requested h "
                  f"[{r_h_lo:.3f}, {r_h_hi:.3f}] intersected with the tier band "
                  f"[{vk.CAM_DIST['h'][0]:.2f}, {cap:.2f}] is empty/degenerate. "
                  f"Falling back to [{b_h_lo:.2f}, {b_h_hi:.2f}]; this scene's "
                  f"boost is DISTANCE-ONLY.", flush=True)
            h_lo, h_hi = b_h_lo, b_h_hi
        else:
            if (i_lo, i_hi) != (r_h_lo, r_h_hi):
                print(f"[camband] {scene_key}: CAM-2 intersect — requested h "
                      f"[{r_h_lo:.3f}, {r_h_hi:.3f}] clipped to "
                      f"[{i_lo:.3f}, {i_hi:.3f}] (cap {cap:.2f}).", flush=True)
            h_lo, h_hi = i_lo, i_hi

    if not (0.0 < d_lo < d_hi) or not (0.0 < h_lo < h_hi):
        raise SystemExit(f"[camband] {scene_key}: refusing an inverted or "
                         f"non-positive band — d [{d_lo}, {d_hi}] "
                         f"h [{h_lo}, {h_hi}]")
    print(f"[camband] {scene_key}: d LogU[{d_lo:.3f}, {d_hi:.3f}] · "
          f"h U[{h_lo:.3f}, {h_hi:.3f}]  (tier band was d [{b_d_lo}, {b_d_hi}] "
          f"h [{b_h_lo}, {b_h_hi}]); pitch/yaw/roll/hfov/yoff unchanged.",
          flush=True)
    return (d_lo, d_hi, h_lo, h_hi)


def _camband_redraw(s, band, scene_key, idx, base_seed):
    """Return a copy of one camera sample with ONLY `d` and `h_rel` redrawn
    inside `band`, from the independent "camband" stream. Same distribution
    families and same rounding as `variation_kit.py:615-617`."""
    import math as _m                     # `_capture` deletes its own `math`
    d_lo, d_hi, h_lo, h_hi = band
    r = vk.rng(scene_key, "camband", idx, base_seed)
    out = dict(s)
    out["d"] = round(_m.exp(r.uniform(_m.log(d_lo), _m.log(d_hi))), 4)
    out["h_rel"] = round(r.uniform(h_lo, h_hi), 4)
    return out


# ===========================================================================
# opt-in sidecars — NEGOBS_DATA_SIDECARS=1 (spec D4 depth, D5 heightmap)
# ===========================================================================
# NOTHING in this section runs unless NEGOBS_DATA_SIDECARS == "1". With the
# variable unset no function below is ever called, no module below is ever
# imported, and the render path is the pre-patch driver unchanged. Every import
# these helpers need is done INSIDE the helper, so a broken/absent replicator
# cannot break a default round at import time.
SIDECAR_ENV = "NEGOBS_DATA_SIDECARS"
# `distance_to_image_plane` = orthogonal distance to the image plane (the "Z
# depth" a pinhole reprojection wants), NOT `distance_to_camera`, which is
# radial range. See experiments/mainrun_0819/CAM_CONVENTION.md §5.
DEPTH_ANNOTATOR = "distance_to_image_plane"
# Per-scene height field: x in [-2, 14], y in [-8, 8], 0.05 m, z[y_idx, x_idx].
HM_X0, HM_Y0, HM_STEP, HM_NX, HM_NY = -2.0, -8.0, 0.05, 321, 321
HM_SPAN, HM_MARCH, HM_EPS = 14.0, 0.10, 0.005
HM_BUDGET_S = 420.0
# Scenes whose walked surface is an annular-sector mesh (scene_common.py:2250
# `_annular_sector_mesh` / :2789 `build_arc_steps`). The world AABB of a 36..52
# deg arc at r ~ 15 is a ~20 x 12 m box (Docs/reports/w3_s08_v1.md:219-221), so
# `AabbPrefilter.ground_z` reads far too high over them. Each of these scene
# modules carries its own exact oracle and it is used to correct the AABB read:
#   "solid_at"  — `_solid_at(x, y, z) -> name|None`, marched DOWNWARDS from the
#                 AABB top at the same 0.10 m step the scenes' own sight-line
#                 checks use (scene08_sunken_plaza.py:1376-1378), then bisected.
#   "height_xy" — a direct 2.5-D surface function `f(x, y) -> z`.
SIDECAR_ORACLES = {
    "scene06": ("_solid_at", "solid_at"),      # scene06:1036
    "scene08": ("_solid_at", "solid_at"),      # scene08:1068
    "scene11": ("_solid_at", "solid_at"),      # scene11:988
    "scene12": ("_solid_at", "solid_at"),      # scene12:998
    "scene19": ("_solid_at", "solid_at"),      # scene19:937
    # scene07 exposes BOTH `path_z(x)` (:782, the corridor centre profile only)
    # and `ground_z(x, y)` (:794, the same profile plus the north cut slope and
    # the south terrace). The 2-D one is a strict superset of the 1-D one, so it
    # is what gets used; `oracle` in the meta records which.
    "scene07": ("ground_z", "height_xy"),
}


def _sidecars_on():
    return os.environ.get(SIDECAR_ENV) == "1"


def _depth_attach(cam_path, sim_app):
    """Replicator render product + depth annotator on the driver's OWN camera.

    Returns the annotator, or None (round then simply has no depth sidecars —
    an absent annotator must never abort a render night).

    Called BEFORE the `/rtx/pathtracing/*` block in `_capture`, so that block
    re-asserts every render setting a render product may have disturbed
    (SPEC_EXTRACTED.md (e), risk (i)).
    """
    try:
        import omni.kit.app
        mgr = omni.kit.app.get_app().get_extension_manager()
        if not mgr.is_extension_enabled("omni.replicator.core"):
            mgr.set_extension_enabled_immediate("omni.replicator.core", True)
            for _ in range(10):
                sim_app.update()
        import omni.replicator.core as rep
        rp = rep.create.render_product(cam_path, (vk.RES_W, vk.RES_H))
        ann = rep.AnnotatorRegistry.get_annotator(DEPTH_ANNOTATOR)
        ann.attach(rp)
        for _ in range(10):
            sim_app.update()
        print(f"[sidecar] depth {DEPTH_ANNOTATOR} attached to {cam_path} "
              f"{vk.RES_W}x{vk.RES_H}", flush=True)
        return ann, rp
    except Exception as e:
        print(f"[sidecar] depth annotator UNAVAILABLE — "
              f"{type(e).__name__}: {str(e)[:200]}", flush=True)
        return None, None


def _depth_detach(ann, rp, sim_app):
    """Tear the annotator and its render product down BEFORE Isaac unloads its
    plugins.

    Measured on the 08-19 patch probe: without this the replicator /
    omni.syntheticdata teardown order faults and the scene subprocess exits
    -11 (SIGSEGV) after every artefact is already safely on disk. That exit
    code is not cosmetic — `run_data_render.py` only advances `done_conds` when
    the subprocess returned 0, so a -11 silently costs the round its
    scene-level resume and makes every scene look like a failure in the
    manifest.
    """
    for tag, fn in (("detach", lambda: ann.detach()),
                    ("destroy", lambda: rp.destroy())):
        try:
            fn()
        except Exception as e:
            print(f"[sidecar] depth {tag} failed: {type(e).__name__}: "
                  f"{str(e)[:120]}", flush=True)
    for _ in range(5):
        sim_app.update()
    print("[sidecar] depth annotator torn down", flush=True)


def _depth_fetch(ann, sim_app, subframes):
    """(array|None, how). Fetched only AFTER `cap()` has returned, so the depth
    belongs to the same converged PathTracing frame as the PNG.

    PT accumulation means the first fetch of a freshly attached annotator can
    come back empty or all-zero; the escalation below is tried in order and the
    step that worked is recorded per cut as `depth_fetch`, so the round says on
    disk what it actually needed.
    """
    import numpy as np
    plan = (("t0", 0), ("t1", 1), ("t4", 4), ("orch", -1))
    for how, ticks in plan:
        if ticks > 0:
            for _ in range(ticks):
                sim_app.update()
        elif ticks < 0:
            try:
                import omni.replicator.core as rep
                rep.orchestrator.step(rt_subframes=int(subframes))
            except Exception as e:
                print(f"[sidecar] orchestrator.step failed: {e}", flush=True)
                return None, "fail"
        try:
            a = ann.get_data()
        except Exception as e:
            print(f"[sidecar] depth get_data failed: {e}", flush=True)
            return None, "fail"
        a = np.asarray(a)
        if a.ndim == 3:
            a = a[..., 0]
        if a.shape == (vk.RES_H, vk.RES_W) and np.any(a != 0):
            return a, how
    return None, "empty"


def _depth_write(a, fp_png):
    """`<png stem>.depth.npy`, float16 metres, +inf where nothing was hit.

    float16 is 4 MB/cut instead of 8 and its 2^-10 relative step is ~1 cm at
    10 m — an order below the 0.30 m hazard threshold. Non-finite (sky) stays
    non-finite; anything beyond float16 range (65504 m) is sky by any reading
    and lands on +inf too. A `.npy` sidecar is deliberately not a `.png`:
    `check_data_run.py:256-261` fails a round on any orphan PNG.
    """
    import numpy as np
    out = os.path.splitext(fp_png)[0] + ".depth.npy"
    a = np.asarray(a, np.float32)
    a = np.where(np.isfinite(a), a, np.float32(np.inf))
    with np.errstate(over="ignore", invalid="ignore"):
        a16 = a.astype(np.float16)
    np.save(out, a16)
    return os.path.basename(out)


# ===========================================================================
# opt-in ID-mask sidecar — NEGOBS_SEG_SIDECAR=1  (v3 P-5, DZ §12-5 + D58 (1)(b))
# ===========================================================================
# NOTHING in this section runs unless NEGOBS_SEG_SIDECAR == "1" AND the depth
# sidecar already built a render product. With the variable unset `_seg_attach`
# returns None on its first statement and every branch guarded by it is dead —
# same discipline as the depth section above.
#
# WHY instance_id AND NOT semantic_segmentation. `semantic_segmentation` and
# `instance_segmentation` return "only semantically labelled entities"
# (omni.replicator.core 1.11.35 annotators_default.py:1110, :1200), and this
# repo's 46 scene files author ZERO `Semantics` prims — so both would come back
# all-background until a scene-wide tagging pass exists.
# `instance_id_segmentation` needs no semantics at all: it returns the RENDERER
# instance id per pixel plus `idToLabels = {id: prim_path}`. Prim paths are
# exactly what CUE_COVERAGE.md §2.2 already enumerated per (scene, cue_*)
# toggle — `{ROOT}/Rail/Post_{i}`, `{ROOT}/Nosing`, `{ROOT}/StairWall_{tag}/*` —
# so a prim-path prefix match turns this mask into (a) the cue mask that §12-5's
# threshold k counts and (b) the occluder-vs-drop-rim ownership map that D58's
# edge-ownership gate needs. No new authoring in 46 scene files.
SEG_ENV = "NEGOBS_SEG_SIDECAR"
SEG_ANNOTATOR = "instance_id_segmentation"


def _seg_on():
    return os.environ.get(SEG_ENV) == "1"


def _seg_attach(rp, sim_app):
    """Attach the id-mask annotator to the depth sidecar's OWN render product.

    Returns the annotator, or None (the round then simply has no id masks — an
    absent annotator must never abort a render night, same rule as depth).
    """
    if not _seg_on():
        return None
    if rp is None:
        print(f"[sidecar] {SEG_ENV}=1 but there is no render product "
              f"(NEGOBS_DATA_SIDECARS off, or the depth attach failed) — "
              f"id masks skipped", flush=True)
        return None
    try:
        import omni.replicator.core as rep
        ann = rep.AnnotatorRegistry.get_annotator(SEG_ANNOTATOR)
        ann.attach(rp)
        for _ in range(10):
            sim_app.update()
        print(f"[sidecar] idseg {SEG_ANNOTATOR} attached (shares the depth "
              f"render product)", flush=True)
        return ann
    except Exception as e:
        print(f"[sidecar] idseg annotator UNAVAILABLE — "
              f"{type(e).__name__}: {str(e)[:200]}", flush=True)
        return None


def _seg_detach(ann, sim_app):
    """Detach BEFORE `_depth_detach` destroys the shared render product."""
    try:
        ann.detach()
    except Exception as e:
        print(f"[sidecar] idseg detach failed: {type(e).__name__}: "
              f"{str(e)[:120]}", flush=True)
    for _ in range(3):
        sim_app.update()
    print("[sidecar] idseg annotator torn down", flush=True)


def _seg_fetch(ann, sim_app, subframes):
    """(array|None, idToLabels|None, how). Same escalation ladder as
    `_depth_fetch`, and called at the same point — after `cap()` returned — so
    the mask belongs to the frame that was written.

    `get_data()` on this annotator returns either a bare array or
    `{"data": ndarray, "info": {"idToLabels": {...}}}` depending on the node
    build; both shapes are accepted rather than assumed.
    """
    import numpy as np
    plan = (("t0", 0), ("t1", 1), ("t4", 4), ("orch", -1))
    for how, ticks in plan:
        if ticks > 0:
            for _ in range(ticks):
                sim_app.update()
        elif ticks < 0:
            try:
                import omni.replicator.core as rep
                rep.orchestrator.step(rt_subframes=int(subframes))
            except Exception as e:
                print(f"[sidecar] idseg orchestrator.step failed: {e}",
                      flush=True)
                return None, None, "fail"
        try:
            raw = ann.get_data()
        except Exception as e:
            print(f"[sidecar] idseg get_data failed: {e}", flush=True)
            return None, None, "fail"
        info = None
        if isinstance(raw, dict):
            info = raw.get("info") or {}
            raw = raw.get("data")
        a = np.asarray(raw)
        if a.ndim == 3:
            a = a[..., 0]
        if a.shape == (vk.RES_H, vk.RES_W) and int(a.max()) > 0:
            id2l = None
            if isinstance(info, dict):
                id2l = info.get("idToLabels") or info.get("idToPrims")
            return a, id2l, how
    return None, None, "empty"


def _seg_write(a, id2l, fp_png):
    """(`<png stem>.idseg.npz` basename, n_ids). uint16 where it fits, else
    uint32, compressed — an id map is huge flat regions and deflates ~40x.

    `.npz` and not `.png` deliberately: `check_data_run.py:256-261` fails a
    round on any orphan PNG, exactly as the depth sidecar's own note says.
    The id->prim_path table rides INSIDE the npz as a json string, so a mask can
    never get separated from the table that decodes it.
    """
    import numpy as np
    out = os.path.splitext(fp_png)[0] + ".idseg.npz"
    a = np.asarray(a)
    ids = np.unique(a)
    a = a.astype(np.uint16 if int(ids.max()) < 65535 else np.uint32)
    np.savez_compressed(
        out, idseg=a,
        idToLabels=np.array(json.dumps(id2l or {}, ensure_ascii=False)),
        annotator=np.array(SEG_ANNOTATOR))
    return os.path.basename(out), int(ids.size)


def _aabb_grid(pre, xs, ys, top=60.0):
    """(Z, info) — `AabbPrefilter.ground_z` over the whole grid, NaN = no hit.

    The per-cell call costs ~134 us at 3000 prims, i.e. ~14 s for 321x321 per
    scene per arm. The downward ray from z=top over axis-aligned boxes reduces
    exactly to `max(hi_z)` over the boxes whose XY footprint contains the cell,
    so it is computed box-major instead — and then VERIFIED against
    `pre.ground_z` itself on a lattice of sample cells. If they ever disagree
    the fast result is thrown away and the authority's own loop is run.
    """
    import numpy as np
    X, Y = np.meshgrid(xs, ys)                     # (ny, nx)
    Z = np.full(X.shape, np.nan)
    lo, hi = pre.lo, pre.hi
    for k in range(lo.shape[0]):
        if lo[k, 2] >= top:
            continue
        m = ((X >= lo[k, 0]) & (X <= hi[k, 0])
             & (Y >= lo[k, 1]) & (Y <= hi[k, 1]))
        if not m.any():
            continue
        v = min(float(hi[k, 2]), top)
        cur = Z[m]
        Z[m] = np.where(np.isnan(cur), v, np.maximum(cur, v))
    bad, worst = 0, 0.0
    probes = [(j, i) for j in range(0, len(ys), 17)
              for i in range(0, len(xs), 17)]
    for j, i in probes:
        a = pre.ground_z(float(xs[i]), float(ys[j]), top=top,
                         default=float("nan"))
        b = float(Z[j, i])
        if (a != a) != (b != b):
            bad += 1
        elif a == a:
            worst = max(worst, abs(a - b))
    if bad or worst > 1e-9:
        print(f"[sidecar] box-major grid disagrees with ground_z "
              f"({bad} nan-mismatch, worst {worst:.3g}) — using the per-cell "
              f"loop", flush=True)
        for j in range(len(ys)):
            for i in range(len(xs)):
                Z[j, i] = pre.ground_z(float(xs[i]), float(ys[j]), top=top,
                                       default=float("nan"))
        return Z, dict(mode="ground_z_loop", verified=len(probes))
    return Z, dict(mode="box_major", verified=len(probes),
                   worst_abs=round(worst, 12))


def _scene_oracle(scene_key, ns=None):
    """(name, mode, callable) pulled off the running scene module.

    `ns` is the scene module's own `__dict__`, taken in `_capture` from its
    caller's frame — `capture_pipeline` is monkey-patched onto `scene_common`,
    so `_capture`'s caller IS the scene file's `main()` and its `f_globals` are
    the scene module's globals. That is exact and does not depend on any
    import machinery. The `sys.modules["__main__"]` fallback covers the same
    ground a second way: `runpy.run_path(..., run_name="__main__")` installs the
    scene file there for the duration of the run.
    """
    spec = SIDECAR_ORACLES.get(scene_key)
    if not spec:
        return None, None, None
    name, mode = spec
    fn = (ns or {}).get(name)
    if not callable(fn):
        fn = getattr(sys.modules.get("__main__"), name, None)
    if not callable(fn):
        print(f"[sidecar] {scene_key}: oracle {name!r} absent from the scene "
              f"module — keeping the raw AABB heightmap", flush=True)
        return None, None, None
    return name, mode, fn


def _oracle_correct(Z, xs, ys, fn, mode, t0):
    """(Z, n_fallback, timed_out). Correct the AABB read where the scene has an
    exact oracle. NaN cells stay NaN: the oracles answer for EVERY (x, y),
    including outside the scene, so the AABB mask is what says where the scene
    is. `max(hi_z)` over the containing boxes is an upper bound on the true
    surface, so the march is always downwards from it.
    """
    n_fb = 0
    ny, nx = Z.shape
    for j in range(ny):
        y = float(ys[j])
        if time.time() - t0 > HM_BUDGET_S:
            return Z, n_fb, True
        for i in range(nx):
            z0 = float(Z[j, i])
            if z0 != z0:
                continue
            x = float(xs[i])
            if mode == "height_xy":
                try:
                    Z[j, i] = float(fn(x, y))
                except Exception:
                    n_fb += 1
                continue
            z = z0 - HM_EPS
            try:
                if fn(x, y, z) is not None:
                    continue                # the AABB was already exact here
                prev, hit = z, None
                z -= HM_MARCH
                while z >= z0 - HM_SPAN:
                    if fn(x, y, z) is not None:
                        hit = z
                        break
                    prev, z = z, z - HM_MARCH
            except Exception:
                n_fb += 1
                continue
            if hit is None:
                n_fb += 1                   # nothing under it: keep the AABB
                continue
            hz, lz = prev, hit
            for _ in range(6):
                mid = 0.5 * (hz + lz)
                if fn(x, y, mid) is not None:
                    lz = mid
                else:
                    hz = mid
            Z[j, i] = lz
    return Z, n_fb, False


def _heightmap_write(pre, out_dir, scene_key, ns=None):
    """`heightmap.npy` (float32, z[y_idx, x_idx], NaN = no hit) +
    `heightmap_meta.json`. Once per scene process, after assembly, before the
    cut loop — the geometry does not move between cuts."""
    import numpy as np
    t0 = time.time()
    xs = HM_X0 + HM_STEP * np.arange(HM_NX)
    ys = HM_Y0 + HM_STEP * np.arange(HM_NY)
    Z, info = _aabb_grid(pre, xs, ys)
    raw = Z.copy()
    name, mode, fn = _scene_oracle(scene_key, ns)
    n_fb, timed_out = 0, False
    if fn is not None:
        Z, n_fb, timed_out = _oracle_correct(Z, xs, ys, fn, mode, t0)
        if timed_out:
            print(f"[sidecar] {scene_key}: oracle pass exceeded "
                  f"{HM_BUDGET_S:.0f} s — reverting to the raw AABB grid",
                  flush=True)
            Z, name, mode = raw, None, None
    fin = np.isfinite(Z)
    d = Z[fin] - raw[fin] if name else np.zeros(1)
    np.save(os.path.join(out_dir, "heightmap.npy"), Z.astype(np.float32))
    meta = dict(
        x0=HM_X0, y0=HM_Y0, step=HM_STEP, nx=HM_NX, ny=HM_NY,
        order="z[y_idx,x_idx]",
        # Stated outright because it is the easy mistake: cameras stand at
        # x = -d with d up to 12 m, so most camera FEET are OUTSIDE this grid.
        # `cam.ground_z` in the cut record is the camera's own reference ground;
        # do not index the heightmap for it (a negative index wraps silently).
        x_range=[HM_X0, round(HM_X0 + HM_STEP * (HM_NX - 1), 6)],
        y_range=[HM_Y0, round(HM_Y0 + HM_STEP * (HM_NY - 1), 6)],
        solid_at_used=bool(name and mode == "solid_at"),
        oracle=(f"{name}(x,y,z)" if mode == "solid_at"
                else f"{name}(x,y)" if name else None),
        scene=scene_key,
        arm_config=os.environ.get("NEGOBS_SCENE_CONFIG") or None,
        nodata="NaN",
        source="variation_kit.AabbPrefilter.ground_z(top=60.0)",
        aabb_grid=info, n_prims=pre.n,
        oracle_mode=mode, oracle_fallback_cells=int(n_fb),
        oracle_timed_out=bool(timed_out),
        oracle_max_drop=(round(float(-d.min()), 4) if name and d.size else 0.0),
        n_finite=int(fin.sum()), n_total=int(Z.size),
        z_min=(round(float(Z[fin].min()), 4) if fin.any() else None),
        z_max=(round(float(Z[fin].max()), 4) if fin.any() else None),
        sec=round(time.time() - t0, 2),
    )
    with open(os.path.join(out_dir, "heightmap_meta.json"), "w",
              encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(f"[sidecar] heightmap {scene_key}: {meta['n_finite']}/{meta['n_total']}"
          f" cells, z {meta['z_min']}..{meta['z_max']}, oracle {meta['oracle']}"
          f", {meta['sec']:.1f} s", flush=True)
    return meta


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
