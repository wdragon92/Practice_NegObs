#!/usr/bin/env python3
"""curate_panels_0830.py — PART A of the panel track.

Curates 24 v2-scope qualitative panels into submission_0830/panels/, closing
INDEX.md section 4 "누락위험 1" (the 119 v2 run panels are blocked from the public
repo by .gitignore:17  **/runs/**/*.png).

COPY / DOWNSCALE ONLY — no composite is invented.  Anything the paper needs that
has no existing artefact is recorded as a gap row in PANELS.md section 4, never
fabricated.  CPU only, no GPU, no git.

    PYTHONNOUSERSITE=1 python3 experiments/v3_0823/code/curate_panels_0830.py

The canonical selection list is PANELS.md section 3; SEL below must match it.
"""
import csv, json, os, re, shutil, sys
from PIL import Image

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
DST  = os.path.join(ROOT, "submission_0830/panels")
V2   = os.path.join(ROOT, "experiments/dayrun_0820/runs/v2")
GZ   = os.path.join(ROOT, "experiments/weekend_0823/gazebo/out/panels")
EVAL = os.path.join(ROOT, "experiments/v3_0823/eval_v2corr")
MAXPX = 1600
os.makedirs(DST, exist_ok=True)

# (dst_name, src_abs)
SEL = []
def v2(run, fn, name):
    SEL.append((name, os.path.join(V2, run, "viz", fn)))

# --- RGB ---------------------------------------------------------------
v2("rgb_s42",  "hitH_01_on__scene14__L5__s20260819__0006.png.png",             "hitmiss_scene14_rgb-s42_hit.png")
v2("rgb_s42",  "missH_01_on__scene14__L5__s20260820__0006.png::boost_h.png",   "hitmiss_scene14_rgb-s42_miss.png")
v2("rgb_s43",  "hitH_02_on__scene14__L5__s20260819__0000.png.png",             "hitmiss_scene14_rgb-s43_hit.png")
v2("rgb_s43",  "missH_03_on__scene15__L4__s20260820__0000.png::boost_h.png",   "hitmiss_scene15_rgb-s43_miss.png")
v2("rgb_s44",  "hitH_04_on__scene14__L5__s20260819__0000.png.png",             "hitmiss_scene14_rgb-s44_hit.png")
v2("rgb_s44",  "missH_02_on__scene14__L5__s20260820__0006.png::boost_h.png",   "hitmiss_scene14_rgb-s44_miss.png")
# --- Depth -------------------------------------------------------------
v2("depth_s42","hitH_02_on__scene14__L5__s20260820__0004.png::boost_h.png",    "hitmiss_scene14_depth-s42_hit.png")
v2("depth_s42","missH_02_on__scene15__L4__s20260820__0001.png::boost_h.png",   "hitmiss_scene15_depth-s42_miss.png")
v2("depth_s43","hitH_02_on__scene14__L5__s20260819__0003.png.png",             "hitmiss_scene14_depth-s43_hit.png")
v2("depth_s43","missH_04_on__scene14__L0__s20260820__0001.png::boost_h.png",   "hitmiss_scene14_depth-s43_miss.png")
v2("depth_s44","hitH_02_on__scene14__L5__s20260819__0000.png.png",             "hitmiss_scene14_depth-s44_hit.png")
v2("depth_s44","missH_02_on__scene14__L5__s20260820__0007.png::boost_h.png",   "hitmiss_scene14_depth-s44_miss.png")
# --- B2 ----------------------------------------------------------------
v2("b2_s42",   "hitH_04_on__scene14__L5__s20260819__0001.png.png",             "hitmiss_scene14_b2-s42_hit.png")
v2("b2_s42",   "missH_04_on__scene14__L5__s20260820__0006.png::boost_h.png",   "hitmiss_scene14_b2-s42_miss.png")
v2("b2_s43",   "hitH_01_on__scene15__L4__s20260820__0000.png::boost_h.png",    "hitmiss_scene15_b2-s43_hit.png")
v2("b2_s43",   "missH_03_on__scene14__L7__s20260820__0006.png::boost_h.png",   "hitmiss_scene14_b2-s43_miss.png")
v2("b2_s44",   "hitH_02_on__scene14__L5__s20260820__0007.png::boost_h.png",    "hitmiss_scene14_b2-s44_hit.png")
v2("b2_s44",   "missH_04_on__scene15__L0__s20260820__0000.png::boost_h.png",   "hitmiss_scene15_b2-s44_miss.png")
# --- aux (amodal head) -------------------------------------------------
v2("rgb_s42_aux","hitH_02_on__scene14__L5__s20260819__0003.png.png",           "hitmiss_scene14_rgbaux-s42_hit.png")
# --- off-arm false alarms ----------------------------------------------
v2("rgb_s42",  "fa_off_02_off__scene15__L4__s20260819__0003.png.png",          "faoff_scene15_rgb-s42_arm.png")
v2("depth_s42","fa_off_01_off__sceneC2__L2__s20260819__0005.png.png",          "faoff_sceneC2_depth-s42_arm.png")
v2("b2_s42",   "fa_off_01_off__scene05__L5__s20260819__0006.png.png",          "faoff_scene05_b2-s42_arm.png")
# --- Gazebo before/after ------------------------------------------------
SEL.append(("gazebo_drop1ctrl_rgb-s42_arm.png", os.path.join(GZ, "rgb_s42__gz_drop1_ctrl__preset_h0.3_d2.png")))
SEL.append(("gazebo_drop1_rgb-s42_arm.png",     os.path.join(GZ, "rgb_s42__gz_drop1__preset_h0.3_d2.png")))

# ---------------------------------------------------------------- metrics
CELLS = [f"{s}{b}" for b in ("1", "2", "3a", "3b") for s in "ABCDE"]

def frame_id_of(fn):
    m = re.match(r"^(fa_off|hitH|missH)_\d\d_(.*)\.png$", fn)
    if not m:
        return None
    rest = m.group(2)
    parts = rest.split("__")
    if len(parts) < 4:
        return None
    arm, scene = parts[0], parts[1]
    return f"{arm}/{scene}/" + "__".join(parts[2:])

RESCORED = {f"{m}_s{s}" for m in ("rgb", "depth", "b2") for s in (42, 43, 44)}
_cache = {}
def lookup(run, fid):
    """Per-frame row for `fid`.

    Main-table runs come from the corrected-GT rescore (`eval_v2corr/`).  The
    aux ablation run was never rescored (it is not one of the 9 main-table runs,
    SEED_TABLE.md section 5), so it is read from its own published dump — valid
    for an H-tier cut because V2_RESCORE.md section 2 measured the H rows to be
    byte-identical across the two GTs.
    """
    if run not in _cache:
        rows = {}
        base = (os.path.join(EVAL, run) if run in RESCORED
                else os.path.join(V2, run, "eval_test"))
        for tag in ("on", "off"):
            p = os.path.join(base, f"per_frame_{tag}.csv")
            if os.path.exists(p):
                for r in csv.DictReader(open(p)):
                    rows[r["frame_id"]] = r
        _cache[run] = rows
    return _cache[run].get(fid)

meta = []
total = 0
for name, src in SEL:
    assert os.path.exists(src), src
    im = Image.open(src)
    w, h = im.size
    if max(w, h) > MAXPX:
        s = MAXPX / max(w, h)
        im = im.convert("RGB").resize((round(w * s), round(h * s)), Image.LANCZOS)
        im.save(os.path.join(DST, name), optimize=True)
        note = f"downscale {w}x{h}->{im.size[0]}x{im.size[1]}"
    else:
        shutil.copy2(src, os.path.join(DST, name))
        note = f"copy {w}x{h}"
    sz = os.path.getsize(os.path.join(DST, name))
    total += sz

    fid = frame_id_of(os.path.basename(src))
    run = os.path.basename(os.path.dirname(os.path.dirname(src)))
    maxp = npos = nfire = tier = None
    if fid:
        r = lookup(run, fid)
        if r:
            ps = [float(r["p_" + c]) for c in CELLS]
            gs = [int(r["g_" + c]) for c in CELLS]
            maxp, npos, nfire, tier = max(ps), sum(gs), sum(p >= .5 for p in ps), r["tier"]
    meta.append(dict(name=name, src=os.path.relpath(src, ROOT), bytes=sz, note=note,
                     frame_id=fid, run=run, tier=tier, max_p=maxp, n_gt=npos, n_fire=nfire))

print(f"{len(SEL)} images, {total/1e6:.2f} MB")
for m in meta:
    print(f"  {m['name']:44s} {m['bytes']/1024:7.0f} KB  tier={m['tier']} "
          f"maxp={m['max_p'] if m['max_p'] is None else round(m['max_p'],3)} "
          f"gt={m['n_gt']} fire={m['n_fire']}  {m['note']}")
