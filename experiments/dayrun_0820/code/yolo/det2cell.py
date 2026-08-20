#!/usr/bin/env python3
"""Detection -> polar-cell mapping (DAYRUN_BRIEF_0820 Phase 5.4).

Turns ultralytics detection txt files into a `per_frame.csv` byte-compatible with
`eval_polar.write_per_frame`, so `eval_polar --per-frame-a` and `twin_analysis`
consume the YOLO arm with no change at all.

----------------------------------------------------------------------------
MAPPING RULE (the brief's rule, verbatim as pseudocode)
----------------------------------------------------------------------------

    for each frame F with camera cam = (h_rel, yaw, pitch, roll, hfov):
        prob[c] = 0 for every cell c of the gridspec
        for each detection (box, conf) of F with conf >= tau_conf:

            # 1. the bottom edge of the box, in continuous full-res pixels
            x0, x1 = (box.xc -+ box.w/2) * W          # W, H = 1920, 1080
            y_b    = (box.yc + box.h/2) * H
            pts_px = [(x0, y_b), (x1, y_b), ((x0 + x1)/2, y_b)]   # 2 ends + centre

            # 2. ground-project each of them with the LABELER camera model
            #    (labeler.cam_basis / labeler.focal_px -- the inverse of
            #     labeler.project, so this is the same optics the GT was built
            #     with, not a second model)
            for (u, v) in pts_px:
                xn  = (u - W/2) / f_px ;  yn = (v - H/2) / f_px
                dir = xn*right + yn*(-up) + fwd
                if dir.z >= 0:  continue              # at or above the horizon
                t   = (cam.ground_z - eye.z) / dir.z  # == -h_rel / dir.z
                if t <= 0:      continue
                P   = eye + t*dir                     # the plane z = cam.ground_z

            # 3. (azimuth, range) of P about the eye, then the cell
                az, rng = labeler.polar_cells(P.x, P.y, eye, cam.yaw, grid)
                cell    = band(rng)*n_sectors + sector(az)   # -1 = outside grid

            # 4. the detection CLAIMS the SET of cells its bottom-edge points
            #    fell into (deduped; cell == -1 dropped)
                claimed |= {cell}

            # 5. frame-level cell prediction = union over detections, scored by
            #    the strongest detection that claimed the cell
            for c in claimed:
                prob[c] = max(prob[c], conf)

        gt[c] = manifest.polar_gt[c]        # unchanged, same grid, same labels
        emit row (frame_id, scene_id, tier, toggle_state, prob[...], gt[...])

Frames with no detection file, or no detection above tau_conf, emit an all-zero
probability row -- they are still rows, because the false-alarm and twin
denominators must count them.

----------------------------------------------------------------------------
KNOWN PROPERTIES OF THE RULE (report these, do not silently "fix" them)
----------------------------------------------------------------------------
(a) 3 points per box means a detection claims at most 3 cells, while the frame's
    GT routinely spans 8-15 cells.  Cell recall is therefore capped far below 1
    by the rule itself, independently of how good the detector is.  `--bottom-
    samples N` (N > 3) relaxes this and is reported as a sweep, not as the
    headline.
(b) The amodal box includes the drop INTERIOR, whose lowest image row sits below
    the lip; ground-projecting that row onto the plane z = ground_z lands NEARER
    than the true lip.  The mapping is therefore biased toward near bands.  It
    is the brief's rule and is kept as specified; the bias is the reason a YOLO
    row can look near-band-heavy next to the polar heads.
(c) The eye's absolute (x, y) is never needed: the ray, the plane offset
    (ground_z - eye.z) = -h_rel, and the azimuth/range of P *about the eye* all
    depend on h_rel/yaw/pitch/roll/hfov alone.  `common.synth_eye` places the
    eye at the origin of its own ground frame for exactly this reason -- which
    is what lets the mapping run off the manifest's `cam` block, which carries no
    `eye`.
(d) H-tier recall is expected to be ~0: a visibility-trained detector cannot fire
    on a hazard with zero visible pixels.  A NONZERO H recall is a mapping leak
    to investigate, not a win.

Run with PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="".
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DAYRUN, LB, cells_of_points, ground_project, load_grid,  # noqa: E402
                    synth_eye)


def frame_id_of_stem(stem):
    """'on__scene04__L0__s20260819__0000' -> 'on/scene04/L0__s20260819__0000.png'.

    Scene ids never contain '__' and arms are 'on'/'off', so a maxsplit-2 split is
    unambiguous even though the cut filename itself is full of '__'."""
    arm, scene, fn = stem.split("__", 2)
    return f"{arm}/{scene}/{fn}.png"


def read_pred_dir(d):
    """{frame_id -> [(cls, xc, yc, w, h, conf), ...]} from ultralytics save_txt output.

    ultralytics writes one txt per image THAT HAS DETECTIONS; a missing file means
    zero detections, never an error.  `save_conf=True` appends the confidence as a
    6th field -- without it the file has 5 and every detection is scored 1.0, which
    would silently destroy the threshold sweep, so that case fails loudly.
    """
    out = {}
    if not os.path.isdir(d):
        raise SystemExit(f"[fatal] --pred-labels {d} is not a directory")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"):
            continue
        rows = []
        for ln in open(os.path.join(d, fn)):
            p = ln.split()
            if len(p) == 5:
                raise SystemExit(f"[fatal] {fn}: 5 fields per row -- predictions were written "
                                 f"without save_conf=True, so no confidence exists. Re-run "
                                 f"predict with save_txt=True save_conf=True.")
            if len(p) < 6:
                continue
            rows.append((int(float(p[0])), *[float(x) for x in p[1:6]]))
        out[frame_id_of_stem(os.path.splitext(fn)[0])] = rows
    return out


def oracle_preds(bboxes_json):
    """The amodal GT boxes, dressed as conf-1.0 detections (mapping-rule ceiling)."""
    doc = json.load(open(bboxes_json))
    return {fid: [(0, b["xc"], b["yc"], b["w"], b["h"], 1.0) for b in v["boxes"]]
            for fid, v in doc["frames"].items() if v["boxes"]}


def claim_cells(cam, box, spec, n_bottom=3):
    """One detection -> (set of cell ids, list of (az-cell, range) debug tuples).

    `box` = (xc, yc, w, h) normalised.  See the module docstring for the rule.
    """
    W, H = LB.W_IMG, LB.H_IMG
    xc, yc, w, h = box
    x0 = float(np.clip((xc - w / 2.0) * W, 0.0, W - 1e-6))
    x1 = float(np.clip((xc + w / 2.0) * W, 0.0, W - 1e-6))
    yb = float(np.clip((yc + h / 2.0) * H, 0.0, H - 1e-6))
    if n_bottom <= 3:
        px = np.array([x0, x1, 0.5 * (x0 + x1)][:max(n_bottom, 1)])
    else:                                     # sweep variant: even samples, ends included
        px = np.linspace(x0, x1, n_bottom)
    py = np.full(px.shape, yb)
    eye, gz = synth_eye(cam)
    P, hit = ground_project(cam, eye, gz, px, py)
    cid, rng = cells_of_points(P, eye, cam["yaw"], spec)
    keep = hit & (cid >= 0)
    return set(int(c) for c in cid[keep]), list(zip(cid.tolist(), rng.round(3).tolist(),
                                                    hit.tolist()))


def build_rows(frames, preds, spec, ncell, tau, n_bottom):
    rows, stat = [], dict(frames=len(frames), frames_with_pred=0, dets_total=0, dets_kept=0,
                          claims=0, claims_outside_grid=0, cells_fired=0)
    for f in frames:
        fid = f["frame_id"]
        cam = f["cam"]
        prob = np.zeros(ncell)
        dets = preds.get(fid, [])
        if dets:
            stat["frames_with_pred"] += 1
        for _cls, xc, yc, w, h, conf in dets:
            stat["dets_total"] += 1
            if conf < tau:
                continue
            stat["dets_kept"] += 1
            cells, dbg = claim_cells(cam, (xc, yc, w, h), spec, n_bottom)
            stat["claims"] += len(cells)
            stat["claims_outside_grid"] += sum(1 for c, _r, hi in dbg if hi and c < 0)
            for c in cells:
                prob[c] = max(prob[c], conf)
        stat["cells_fired"] += int((prob > 0).sum())
        rows.append((fid, f["scene_id"], f["tier"], f["toggle_state"], prob,
                     np.asarray(f["polar_gt"], float)))
    return rows, stat


def write_per_frame(rows, path, cell_ids):
    """Byte-compatible with eval_polar.write_per_frame (header is the cell-id authority)."""
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["frame_id", "scene_id", "tier", "toggle_state"]
                   + [f"p_{c}" for c in cell_ids] + [f"g_{c}" for c in cell_ids])
        for fid, sid, tier, tog, prob, gt in rows:
            w.writerow([fid, sid, tier, tog] + [f"{v:.6f}" for v in prob]
                       + [int(v) for v in gt])


def select_frames(manifest, split, subset):
    man = json.load(open(manifest))
    keep = None
    if split:
        sp = json.load(open(split))
        if subset not in sp:
            raise SystemExit(f"[fatal] subset {subset!r} not in {split} (have {list(sp)})")
        keep = set(sp[subset])
    fr = [f for f in man["frames"] if keep is None or f["scene_id"] in keep]
    if not fr:
        raise SystemExit(f"[fatal] no manifest frames for subset {subset!r}")
    return man, fr


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred-labels", default=None,
                    help="ultralytics predict '.../labels' dir (save_txt=True save_conf=True)")
    ap.add_argument("--oracle-boxes", default=None,
                    help="DIAGNOSTIC: use the amodal GT boxes of this bboxes.json as if they "
                         "were perfect detections (conf 1.0). Measures the CEILING of the "
                         "mapping rule itself -- what a flawless detector could score. Never a "
                         "reported model number.")
    ap.add_argument("--manifest", default=os.path.join(DAYRUN, "dataset_manifest_v2.json"))
    ap.add_argument("--split", default=os.path.join(DAYRUN, "split_v2.json"))
    ap.add_argument("--subset", default="test")
    ap.add_argument("--grid", default=None)
    ap.add_argument("--conf", type=float, default=0.25, help="headline confidence threshold")
    ap.add_argument("--conf-sweep", default="",
                    help="extra thresholds, e.g. 0.1,0.2,0.3,0.4,0.5 -> <out>/conf_<t>/per_frame.csv")
    ap.add_argument("--bottom-samples", type=int, default=3,
                    help="points on the bottom edge (3 = the brief's rule: 2 ends + centre)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--unit-check", action="store_true",
                    help="run the synthetic-bbox unit check and exit (no --pred-labels needed)")
    a = ap.parse_args(argv)

    grid, spec, gpath = load_grid(a.grid)
    if a.unit_check:
        return unit_check(grid, spec, gpath)
    if not ((a.pred_labels or a.oracle_boxes) and a.out):
        ap.error("--pred-labels (or --oracle-boxes) and --out are required "
                 "unless --unit-check is given")

    man, frames = select_frames(a.manifest, a.split, a.subset)
    preds = (oracle_preds(a.oracle_boxes) if a.oracle_boxes else read_pred_dir(a.pred_labels))
    unknown = sorted(set(preds) - {f["frame_id"] for f in frames})
    os.makedirs(a.out, exist_ok=True)

    summary = {}
    for tau, outdir in [(a.conf, a.out)] + [(float(t), os.path.join(a.out, f"conf_{float(t):g}"))
                                            for t in a.conf_sweep.split(",") if t.strip()]:
        os.makedirs(outdir, exist_ok=True)
        rows, stat = build_rows(frames, preds, spec, grid.n_cells, tau, a.bottom_samples)
        write_per_frame(rows, os.path.join(outdir, "per_frame.csv"), grid.cell_ids)
        stat["tau_conf"] = tau
        summary[f"{tau:g}"] = stat
        print(f"[det2cell] tau={tau:g} frames={stat['frames']} with_pred={stat['frames_with_pred']} "
              f"dets={stat['dets_total']}->{stat['dets_kept']} claims={stat['claims']} "
              f"outside_grid={stat['claims_outside_grid']} cells_fired={stat['cells_fired']} "
              f"-> {os.path.join(outdir, 'per_frame.csv')}")

    with open(os.path.join(a.out, "det2cell.json"), "w") as f:
        json.dump(dict(created=time.strftime("%Y-%m-%dT%H:%M:%S"),
                       pred_labels=os.path.abspath(a.pred_labels) if a.pred_labels else None,
                       oracle_boxes=(os.path.abspath(a.oracle_boxes)
                                     if a.oracle_boxes else None),
                       manifest=os.path.abspath(a.manifest), split=os.path.abspath(a.split),
                       subset=a.subset, grid=gpath, grid_version=grid.version,
                       cell_ids=list(grid.cell_ids), bottom_samples=a.bottom_samples,
                       rule="bottom-edge endpoints + bottom-centre -> ray x plane z=cam.ground_z "
                            "-> (az, range) -> cell; detection claims the SET; frame prob = max "
                            "conf over detections claiming the cell",
                       unmatched_pred_files=unknown[:20], n_unmatched=len(unknown),
                       by_tau=summary), f, indent=1)
    if unknown:
        print(f"[det2cell] WARN {len(unknown)} prediction files are not frames of subset "
              f"{a.subset!r} (ignored): {unknown[:3]}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------- #
# unit check -- synthetic bbox with a hand-computed expected cell set
# --------------------------------------------------------------------------- #
def unit_check(grid, spec, gpath):
    """Three assertions, all with answers worked out from gridspec_v1.json by hand.

    gridspec_v1: sector_edges_deg = [31.1, 18.66, 6.22, -6.22, -18.66, -31.1] (descending,
    +az = image LEFT), names A..E; band_edges_m = [0, 2, 5, 8, 12], names 1/2/3a/3b;
    cell = band*5 + sector.  So a ground point at (az = +20 deg, range = 3.0 m) is
    sector A (index 0, since +20 lies in [18.66, 31.1)) and band 2 (index 1, since
    3.0 lies in [2, 5)) -> cell 1*5 + 0 = 5 -> id 'A2'; (az = -20, r = 3.0) -> sector E
    (index 4) -> cell 9 -> 'E2'.
    """
    ok = True
    cam = dict(yaw=0.0, pitch=-10.0, roll=0.0, hfov=62.2, h_rel=1.0)
    eye, gz = synth_eye(cam)

    # ---- 1. ground_project is the exact inverse of LB.project on the ground plane
    rng = np.random.default_rng(0)
    az = rng.uniform(-30, 30, 400)
    rr = rng.uniform(0.8, 11.5, 400)
    P = np.stack([eye[0] + rr * np.cos(np.radians(az)),
                  eye[1] + rr * np.sin(np.radians(az)),
                  np.full(400, gz)], 1)
    px, py, zc, inb = LB.project(P, eye, cam)
    Q, hit = ground_project(cam, eye, gz, px, py)
    sel = inb & (zc > 0.05)
    err = float(np.abs(Q[sel] - P[sel]).max()) if sel.any() else float("inf")
    ok &= bool(sel.sum() > 50 and err < 1e-9)
    print(f"[unit] pixel->ground round trip on {int(sel.sum())} in-frame points: "
          f"max |dP| = {err:.3e} m   [{'ok' if err < 1e-9 else 'XX'}]")

    # ---- 2. synthetic bbox: bottom edge endpoints at (+20, 3.0 m) and (-20, 3.0 m)
    tgt = np.array([[eye[0] + 3.0 * np.cos(np.radians(+20)),
                     eye[1] + 3.0 * np.sin(np.radians(+20)), gz],
                    [eye[0] + 3.0 * np.cos(np.radians(-20)),
                     eye[1] + 3.0 * np.sin(np.radians(-20)), gz]])
    tp, tq, tz, tin = LB.project(tgt, eye, cam)
    exp_cells, _ = cells_of_points(tgt, eye, cam["yaw"], spec)
    want_lr = {5, 9}
    print(f"[unit] endpoint targets  az=+20/-20 deg, r=3.0 m -> pixels "
          f"({tp[0]:.1f},{tq[0]:.1f}) / ({tp[1]:.1f},{tq[1]:.1f})   cells "
          f"{[grid.cell_ids[c] for c in exp_cells]} = {set(exp_cells.tolist())} "
          f"[{'ok' if set(exp_cells.tolist()) == want_lr else 'XX'} expected {{A2, E2}} = {want_lr}]")
    ok &= set(exp_cells.tolist()) == want_lr
    ok &= bool(tin.all() and abs(tq[0] - tq[1]) < 1e-6)   # same image row, as a bbox edge must be

    # a bbox whose BOTTOM edge is that row; the endpoints are px[0] (left in world +az
    # = image LEFT, i.e. the SMALLER pixel column) and px[1]
    x0, x1 = sorted((float(tp[0]), float(tp[1])))
    yb = float(tq[0])
    box = ((x0 + x1) / 2.0 / LB.W_IMG, (yb - 100) / LB.H_IMG,   # any top edge above it
           (x1 - x0) / LB.W_IMG, 2 * 100.0 / LB.H_IMG)
    got, dbg = claim_cells(cam, box, spec, 3)
    ctr_cell = dbg[2][0]
    want = want_lr | ({int(ctr_cell)} if ctr_cell >= 0 else set())
    print(f"[unit] synthetic bbox (xc,yc,w,h)=({box[0]:.4f},{box[1]:.4f},{box[2]:.4f},"
          f"{box[3]:.4f}) claims {sorted(grid.cell_ids[c] for c in got)} = {sorted(got)}   "
          f"[{'ok' if got == want else 'XX'} expected {sorted(want)}; centre point -> "
          f"{grid.cell_ids[ctr_cell] if ctr_cell >= 0 else 'outside'} at r="
          f"{dbg[2][1]:.3f} m]")
    ok &= got == want

    # ---- 3. a bbox whose bottom edge is above the horizon claims nothing
    hi = ((x0 + x1) / 2.0 / LB.W_IMG, 0.02, (x1 - x0) / LB.W_IMG, 0.04)
    got_hi, _ = claim_cells(cam, hi, spec, 3)
    print(f"[unit] bbox above the horizon claims {sorted(got_hi)}   "
          f"[{'ok' if not got_hi else 'XX'} expected empty]")
    ok &= not got_hi

    # ---- 4. CSV parity with eval_polar.write_per_frame / read_per_frame
    #      write_per_frame emits  frame_id, scene_id, tier, toggle_state, p_<cell>*, g_<cell>*
    #      with `cells = gridspec.load(grid).cell_ids` -- the SAME call this file makes, so the
    #      header is verified against the contract rather than against a copied literal.
    import tempfile
    want_hdr = (["frame_id", "scene_id", "tier", "toggle_state"]
                + [f"p_{c}" for c in grid.cell_ids] + [f"g_{c}" for c in grid.cell_ids])
    z = np.zeros(grid.n_cells)
    z[7] = 0.42
    g = np.zeros(grid.n_cells)
    g[7] = g[12] = 1
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "per_frame.csv")
        write_per_frame([("on/scene04/x.png", "scene04", "V", "on", z, g),
                         ("off/scene04/x.png", "scene04", "off", "off", z * 0, g * 0)],
                        p, grid.cell_ids)
        with open(p) as fh:
            rd = csv.DictReader(fh)
            hdr = list(rd.fieldnames)
            rows = list(rd)
        cells = [c[2:] for c in hdr if c.startswith("p_")]     # read_per_frame's own inference
        good = (hdr == want_hdr and cells == list(grid.cell_ids) and len(rows) == 2
                and abs(float(rows[0]["p_C2"]) - 0.42) < 1e-9 and int(rows[0]["g_C3a"]) == 1)
    ok &= good
    print(f"[unit] per_frame.csv header == eval_polar contract ({len(want_hdr)} cols, "
          f"{len(grid.cell_ids)} cells inferred from the header)   "
          f"[{'ok' if good else 'XX'}]")

    print(f"[unit] grid {grid.version} ({gpath}) -- {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
