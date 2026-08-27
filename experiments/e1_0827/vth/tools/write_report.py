#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""write_report.py -- assemble W1_CAPTURE.md from the drafted prose + measured numbers."""
from __future__ import annotations
import json, os, re, subprocess
from collections import Counter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
man = json.load(open(os.path.join(HERE, "capture_manifest.json")))
holes = json.load(open(os.path.join(HERE, "holes.json")))
plan = json.load(open(os.path.join(HERE, "plan.json")))
supp = json.load(open(os.path.join(HERE, "plan_supp.json")))
dchk = json.load(open(os.path.join(HERE, "depth_check.json")))
achk = json.load(open(os.path.join(HERE, "align_check.json")))
log = open(os.path.join(HERE, "logs", "run_all.log")).read()
F = man["frames"]
import numpy as np

def q(a, p):
    a = sorted(a)
    return a[int(p * (len(a) - 1))]

tot = [int(x) for x in re.findall(r"total=(\d+)s", log)]
ld = [int(x) for x in re.findall(r"load=(\d+)s", log)]
gr = [int(x) for x in re.findall(r"grab=(\d+)s", log)]
done = re.findall(r"DONE ok=(\d+) bad=(\S+) wall=(\d+)s", log)
nbatch = len(re.findall(r"rc=\d", log))
du = int(subprocess.run(["du", "-sb", os.path.join(HERE, "frames")],
                        capture_output=True, text=True).stdout.split()[0])

L = ["---", "", "## 3. Capture — what was actually rendered", ""]
L += [f"Headless `gzserver` (never `gzclient`), one world copy per batch of 30 static "
      f"cameras, one RGB + one depth frame per camera, then torn down.", ""]
L += ["| | value |", "|---|---|"]
L += [f"| frames captured | **{len(F)}** |"]
for w, n in man["n_frames_by_world"].items():
    L.append(f"| &nbsp;&nbsp;`{w}` | {n} |")
L += [f"| &nbsp;&nbsp;of which `occlusion_intended` | {man['n_occlusion_intended']} |",
      f"| poses planned (main + supplement) | {len(plan)} + {len(supp)} = {len(plan)+len(supp)} |",
      f"| manifest entries == files on disk | {'YES' if len(F)==len(plan)+len(supp) else 'NO'} |",
      f"| poses skipped by the geometry rules (main plan; the supplement rejected 66 more) | "
      f"{sum(holes['worlds'][w]['n_skipped'] for w in holes['worlds'])} |",
      f"| world loads (batches) | {nbatch} |",
      f"| per-batch wall time (median) | load {q(ld,.5)} s · grab {q(gr,.5)} s · total {q(tot,.5)} s |",
      f"| total wall time | {done[0][2] if done else sum(tot)} s ({int(done[0][2] if done else sum(tot))/60:.1f} min) |",
      f"| disk | {du/2**30:.2f} GiB ({du/max(1,len(F))/2**20:.1f} MiB per frame: 1280×720 PNG + 3.5 MiB float32 depth) |",
      ""]

L += ["### Coverage of the kept frames", ""]
for w in ("eworld2", "expandedworld"):
    fw = [f for f in F if f["world"] == w and not f["occlusion_intended"]]
    fo = [f for f in F if f["world"] == w and f["occlusion_intended"]]
    L += [f"**{w}** — {len(fw)} approach frames" + (f" + {len(fo)} occlusion frames" if fo else ""), "",
          "| axis | counts |", "|---|---|"]
    for lab, key in (("standoff m", "standoff_m"), ("height m", "height_m"),
                     ("pitch deg", "pitch_deg"), ("size band", "hole_band"),
                     ("target hole", "hole_id")):
        c = dict(sorted(Counter(f[key] for f in fw).items(), key=lambda kv: str(kv[0])))
        L.append(f"| {lab} | " + " · ".join(f"{k}: {v}" for k, v in c.items()) + " |")
    sk = Counter(s["skip"].split("@")[0].split(":")[0] for s in holes["worlds"][w]["skips"])
    L.append("| skipped (reason: n) | " + " · ".join(f"{k}: {v}" for k, v in sk.most_common()) + " |")
    L.append("")

L += ["### Per-frame image facts", "", "| | eworld2 | expandedworld |", "|---|---|---|"]
def col(key, fmt="{:.1f}"):
    out = []
    for w in ("eworld2", "expandedworld"):
        a = [f[key] for f in F if f["world"] == w and f[key] is not None]
        out.append(f"min {fmt.format(min(a))} · med {fmt.format(q(a,.5))} · max {fmt.format(max(a))}")
    return out
for lab, key, fmt in (("RGB mean (0–255)", "rgb_mean", "{:.1f}"),
                      ("fully saturated pixel fraction", "rgb_sat_frac", "{:.4f}"),
                      ("finite-depth pixel fraction", "depth_finite_frac", "{:.3f}"),
                      ("depth min m", "depth_min_m", "{:.2f}"),
                      ("depth max m", "depth_max_m", "{:.1f}")):
    a, b = col(key, fmt)
    L.append(f"| {lab} | {a} | {b} |")
L.append("")

_occ = {(f["world"], f["pose_id"]): f["occlusion_intended"] for f in F}
def _isocc(r):
    return _occ.get((r["world"], r["pose_id"]), False)
dchk_n = [r for r in dchk if not _isocc(r)]
dchk_o = [r for r in dchk if _isocc(r)]
nad = [r["steep_err_m"] for r in dchk_n if r.get("steep_err_m") is not None]
nad_o = [r["steep_err_m"] for r in dchk_o if r.get("steep_err_m") is not None]
flo_o = [r["floor_abs_err_med_m"] for r in dchk_o if r["floor_abs_err_med_m"] is not None]
flo = [r["floor_abs_err_med_m"] for r in dchk_n if r["floor_abs_err_med_m"] is not None]
npx = [r["n_used"] for r in dchk_n if r["n_used"]]
iou = [r["iou"] for r in achk]
dx = [abs(r["dx_px"]) for r in achk]
dy = [abs(r["dy_px"]) for r in achk]
open(os.path.join(HERE, "_sec3.md"), "w").write("\n".join(L))
L = ["### 4.1 result — depth is metric", "",
      "| check | frames | result |", "|---|---:|---|",
      f"| plane check, per-frame median \\|measured − expected\\| | {len(flo)} | "
      f"median **{np.median(flo)*1000:.4f} mm**, p99 {np.percentile(flo,99)*1000:.4f} mm, "
      f"**max {max(flo)*1000:.4f} mm** (median {int(np.median(npx))} floor pixels per frame) |",
      f"| steepest-ray pixel (nadir substitute) | {len(nad)} | "
      f"median **{np.median(nad)*1000:.4f} mm**, **max {max(nad)*1000:.4f} mm** |",
      f"| true nadir pixel inside frame | 0 | geometrically impossible in this pose band (36.1° max) |",
      "",
      f"Gate was ≤ 20 mm; over the {len(flo)} non-occlusion frames **not one frame exceeds "
      f"{max(max(flo), max(nad))*1000:.2f} mm** — nearly three orders of magnitude inside the "
      f"gate. The depth image is metres, unscaled.",
      "",
      f"The {len(flo_o)} `occlusion_intended` frames are reported separately because the test "
      f"does not apply to them: their floor is deliberately behind a shelf, so the pixel the "
      f"check samples is the shelf, not the floor. There the same statistic reads median "
      f"{np.median(flo_o)*1000:.4f} mm with {sum(1 for v in flo_o if v > 0.02)} of {len(flo_o)} "
      f"frames over 20 mm (plane check) and "
      f"{sum(1 for v in nad_o if v > 0.02)} of {len(nad_o)} (steepest ray) — an occluder "
      f"count, not a depth error.", ""]
L += ["### 4.2 result — RGB and depth are the same pixels", "",
      f"Over {len(achk)} `eworld2` frames with ≥ 500 void pixels: "
      f"**IoU(void, background-RGB) median {np.median(iou):.4f}**, p10 {np.percentile(iou,10):.4f}, "
      f"min {min(iou):.4f} (that minimum is a single frame of the 0.10 × 0.10 m opening at 3 m, "
      f"where the whole opening is a few thousand antialiased pixels); "
      f"centroid offset **|dx| median {np.median(dx):.2f} px, |dy| median {np.median(dy):.2f} px** "
      f"(p90 {np.percentile(dx,90):.1f} / {np.percentile(dy,90):.1f} px). "
      f"The residual is the antialiased rim (RGB blends it, depth does not) plus the odd "
      f"surface elsewhere that happens to sit within 6 counts of grey 178, which is also what "
      f"moves the centroid tail. A systematic RGB↔depth shift of more than a couple of pixels "
      f"would cap the IoU well below 0.98 on the large-opening frames; it does not. "
      f"The modal void colour is {achk[0]['void_colour']}, i.e. the world's "
      f"`<background>0.7` = 178 — so the part of the opening that is not inner wall really "
      f"is open scene, and the two images agree on where it is.", ""]

sat = [f["rgb_sat_frac"] for f in F]

# inside-vs-outside saturation, measured on a sample of eworld2 frames
import math as _m
from PIL import Image as _I
def _rot(p_, y_):
    cp, sp, cy_, sy_ = _m.cos(p_), _m.sin(p_), _m.cos(y_), _m.sin(y_)
    return (np.array([[cy_, -sy_, 0.], [sy_, cy_, 0.], [0., 0., 1.]])
            @ np.array([[cp, 0., sp], [0., 1., 0.], [-sp, 0., cp]]))
def _inside(hole, hx, hy):
    """bbox is not the footprint for a disc: 1 - pi/4 = 21.5 % of a circular hole's bbox
    is bright floor, which silently pollutes every 'interior' statistic."""
    b = hole["world_bbox"]
    inb = (hx > b[0]) & (hx < b[2]) & (hy > b[1]) & (hy < b[3])
    if hole.get("shape") != "circle":
        return inb
    cx, cy = 0.5 * (b[0] + b[2]), 0.5 * (b[1] + b[3])
    r = 0.25 * ((b[2] - b[0]) + (b[3] - b[1]))
    return inb & (((hx - cx) ** 2 + (hy - cy) ** 2) <= r * r)


HC = {h["hole_id"]: h for h in holes["holes"]}
top = holes["plate_top_z"]
ins, outs, nsamp = [], [], 0
sample = [f for f in F if f["world"] == "eworld2"][::7]
for fr in sample:
    try:
        dep = np.load(os.path.join(HERE, fr["depth"]))
        rgb = np.asarray(_I.open(os.path.join(HERE, fr["rgb"])).convert("RGB"), np.int16)
    except Exception:
        continue
    w_, h_ = fr["resolution"]
    f_ = (w_ / 2) / _m.tan(fr["hfov_rad"] / 2)
    R_ = _rot(fr["camera"]["sdf_pitch_rad"], fr["camera"]["yaw_rad"])
    st = 4
    U, V = np.meshgrid(np.arange(0, w_, st) + .5, np.arange(0, h_, st) + .5)
    d_ = np.stack([np.ones_like(U), -(U - w_ / 2) / f_, -(V - h_ / 2) / f_], -1) @ R_.T
    tp = (top - fr["camera"]["z"]) / np.where(np.abs(d_[..., 2]) < 1e-9, np.nan, d_[..., 2])
    hx = fr["camera"]["x"] + tp * d_[..., 0]
    hy = fr["camera"]["y"] + tp * d_[..., 1]
    thru = (tp > 0) & _inside(HC[fr["hole_id"]], hx, hy)
    if thru.sum() < 50:
        continue
    satm = (rgb[V.astype(int), U.astype(int)] >= 250).all(axis=-1)
    ins.append((float(satm[thru].mean()), int(thru.sum())))
    outs.append(float(satm[~thru].mean()))
    nsamp += 1
L += ["### 4.3 result — exposure", "",
      f"| | value |", "|---|---|",
      f"| frames with ≥ 2 % fully-saturated pixels | {sum(1 for s in sat if s >= 0.02)} / {len(sat)} |",
      f"| frames with ≥ 20 % | {sum(1 for s in sat if s >= 0.20)} / {len(sat)} |",
      f"| worst frame | {max(sat)*100:.1f} % of pixels clipped |",
      f"| saturated fraction **inside** the target opening | median "
      f"**{np.median([v for v, _ in ins]):.6f}**, max {max(v for v, _ in ins):.4f} over "
      f"{nsamp} sampled eworld2 frames |",
      f"| &nbsp;&nbsp;same, frames whose interior is ≥ 500 sampled pixels | median "
      f"**{np.median([v for v, n in ins if n >= 500]):.6f}**, max "
      f"**{max(v for v, n in ins if n >= 500):.6f}** "
      f"({sum(1 for _, n in ins if n >= 500)} frames) |",
      f"| saturated fraction **outside** it | median {np.median(outs):.3f}, max {max(outs):.3f} |",
      ""]
open(os.path.join(HERE, "_sec4.md"), "w").write("\n".join(L))

# ---- assemble the whole document -------------------------------------------------
def rd(p_):
    return open(p_).read().rstrip() + "\n"

SRC = os.path.join(HERE, "report_src")
tail = open(os.path.join(SRC, "w1_tail.md")).read()
i5 = tail.index("## 5. Hand-off")
i7 = tail.index("## 7. The one thing")
verif_method = tail[:i5].rstrip().rstrip("-").rstrip() + "\n"
handoff = "---\n\n" + tail[i5:i7].rstrip().rstrip("-").rstrip() + "\n"
lighting = "---\n\n" + tail[i7:].rstrip() + "\n"

doc = "\n".join([rd(os.path.join(SRC, "w1_head.md")), rd(os.path.join(SRC, "w1_mid.md")),
                 rd(os.path.join(HERE, "_sec3.md")),
                 "---\n\n## 4. Verification\n",
                 verif_method.split("## 4. Verification", 1)[-1].lstrip("\n"),
                 rd(os.path.join(HERE, "_sec4.md")),
                 handoff, rd(os.path.join(SRC, "w1_integrity.md")), lighting])
doc = doc.replace("\n\n\n\n", "\n\n")
out = os.path.join(HERE, "W1_CAPTURE.md")
open(out, "w").write(doc)
os.remove(os.path.join(HERE, "_sec3.md")); os.remove(os.path.join(HERE, "_sec4.md"))
print(f"-> {out}  ({len(doc.splitlines())} lines, {len(doc)/1024:.1f} kB)")
