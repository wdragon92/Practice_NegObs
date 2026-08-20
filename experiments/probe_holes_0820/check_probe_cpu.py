#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_probe_cpu.py — everything about the C1 hole probe that can be proved
without a GPU. Run this before asking for the lock.

    unset PYTHONPATH VIRTUAL_ENV; conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python3 experiments/probe_holes_0820/check_probe_cpu.py

Nine checks, each printed PASS/FAIL with the number it turned on:

  1  scene discovery      the shim finds all three probe files
  2  ledger admissibility L0/L5/L7 allowed on all three, no substitutions
  3  SPLIT GUARD          the 33 corpus scenes keep their split, byte for byte
  4  smoke gate           all 3 scenes x both arms exit 0 with no traceback
  5  twin contract        arm-varying prims stay below the paving and east of
                          the camera strip
  6  composition          the frozen camera draws land where the scene headers
                          say they do (band 1 on H1, off-centre on H2, hidden
                          on H3)
  7  bash -n              run_probe.sh parses
  8  --plan               the driver prints a plan and a budget
  9  adjacency metric     `eval_probe.adjacent_sector_firing` on a synthetic
                          per_frame gives the answer computed by hand

Exit 0 only if every check passes.
"""
from __future__ import annotations

import csv
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCENE_DIR = os.path.join(REPO, "scenes", "probe")
GRID_JSON = os.path.join(REPO, "experiments", "mainrun_0819", "code",
                         "labeling", "gridspec_v1.json")
SEED = 20260822
CONDS = ("L0", "L5", "L7")
SCENES = ("probeH1", "probeH2", "probeH3")

sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

OK = [True]


def chk(tag, cond, msg=""):
    OK[0] = OK[0] and bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))
    return bool(cond)


def head(n, t):
    print(f"\n[{n}] {t}")
    print("-" * 74)


# --------------------------------------------------------------------------
def main():
    import probe_driver
    import variation_kit as vk

    head(1, "scene discovery")
    rdr = probe_driver.install()
    for s in SCENES:
        f = rdr.SCENE_FILES.get(s)
        chk(f"{s} resolved", f is not None and os.path.isfile(f[0]),
            f"{os.path.relpath(f[0], REPO)}" if f else "MISSING")
    chk("run_data_render.scene_files() alone would NOT find them",
        all(s not in rdr.scene_files() for s in SCENES),
        "confirms the shim is load-bearing (glob is scenes/{main,batch1}/scene*.py)")

    head(2, "ledger admissibility")
    for s in SCENES:
        L = vk.ledger(s)
        chk(f"{s} class {L['cls']} daz_data {L['daz_data']:.0f}",
            L["cls"] == "C'" and L["daz_data"] == 35.0)
        for c in CONDS:
            ok, why = vk.condition_allowed(s, c, role=vk.ROLE_DATA)
            chk(f"  {s} x {c}", ok, why or "allowed, no substitution needed")

    head(3, "SPLIT GUARD — the corpus must not move")
    # Recompute the frozen map the way a clean process would, and compare.
    import importlib
    import subprocess as sp
    ref = sp.run([sys.executable, "-c",
                  "import sys; sys.path.insert(0, %r);"
                  "import variation_kit as vk, json;"
                  "print(json.dumps(vk.split_map(0)))" % REPO],
                 capture_output=True, text=True)
    base = json.loads(ref.stdout)
    chk("clean process reports 33 corpus scenes", len(base) == 33, str(len(base)))
    moved = [s for s, v in base.items() if vk.split_of(s) != v]
    chk("0 corpus scenes moved after the probe injection", not moved,
        f"moved: {sorted(moved)}" if moved else "33/33 identical")
    chk("probe scenes get their own split",
        all(vk.split_of(s) == "probe" for s in SCENES))
    # And show what a SOURCE edit would have cost, so the choice is documented.
    probe = sp.run([sys.executable, "-c",
                    "import sys; sys.path.insert(0, %r);"
                    "import variation_kit as vk, json;"
                    "b=dict(vk.split_map(0));"
                    "[vk.AZ_LEDGER.__setitem__(s, vk._ledger_row(s,\"C'\",35.0,False,'p'))"
                    " for s in ('probeH1','probeH2','probeH3')];"
                    "vk._SPLIT_CACHE.clear();"
                    "print(json.dumps(sorted(s for s in b if b[s]!=vk.split_map(0)[s])))"
                    % REPO], capture_output=True, text=True)
    would_move = json.loads(probe.stdout)
    chk("a SOURCE-level ledger edit would have moved corpus scenes",
        len(would_move) > 0,
        f"{len(would_move)} of 33 would move: {would_move} "
        f"-> this is why the rows are injected at runtime")

    head(4, "NEGOBS_SMOKE=1 gate, all scenes x both arms")
    env = dict(os.environ)
    env.update(PYTHONNOUSERSITE="1", NEGOBS_RENDER_ROLE="data", NEGOBS_SMOKE="1")
    env.pop("PYTHONPATH", None)
    for s in SCENES:
        f = rdr.SCENE_FILES[s][0]
        for arm, cfg in (("on", '{"hazard_hole": true}'),
                         ("off", '{"hazard_hole": false}')):
            e = dict(env, NEGOBS_SCENE_CONFIG=cfg)
            r = subprocess.run([sys.executable, os.path.basename(f)],
                               cwd=SCENE_DIR, env=e, capture_output=True,
                               text=True, timeout=300)
            body = r.stdout + r.stderr
            chk(f"{s} {arm}: exit {r.returncode}, SMOKE_OK, no traceback",
                r.returncode == 0 and "SMOKE_OK" in r.stdout
                and "Traceback" not in body,
                (body.strip().splitlines() or ["<no output>"])[-1][:110])

    head(5, "twin contract")
    sys.path.insert(0, SCENE_DIR)
    import probe_common as pc
    for s, opening, depth in (
            ("probeH1", (-0.50, -0.45, 0.70, 0.45), 0.60),
            ("probeH2", (0.50, 1.05, 1.30, 1.85), 0.55),
            ("probeH3", (1.00, -0.55, 2.00, 0.55), 0.60)):
        a = pc.twin_audit(opening, depth)
        chk(f"{s} heightmap diff {a['hm_diff']:.2f} m >= 0.30", a["hm_diff"] >= 0.30)
        chk(f"{s} highest ON prim {a['on_prim_top_max']:+.3f} < paving 0.000",
            a["on_prim_top_max"] < 0.0)
        chk(f"{s} westmost arm prim {a['westmost_arm_prim']:+.3f} east of "
            f"the closest possible camera x=-1.20",
            a["westmost_arm_prim"] > -1.20,
            f"margin {a['westmost_arm_prim'] + 1.20:.3f} m")

    head(6, "composition against the FROZEN camera draws")
    grid = json.load(open(GRID_JSON))
    comp = {}
    for s, opening in (("probeH1", (-0.50, -0.45, 0.70, 0.45)),
                       ("probeH2", (0.50, 1.05, 1.30, 1.85)),
                       ("probeH3", (1.00, -0.55, 2.00, 0.55))):
        comp[s] = [cells_for(opening, vk.sample_camera(s, i, SEED, gy=0.0), grid)
                   for i in range(8)]
        empty = [i for i, (c, _o) in enumerate(comp[s]) if not c]
        chk(f"{s}: every cut has >=1 GT-positive cell", not empty,
            f"empty cuts {empty}" if empty else "8/8 inside the 12 m grid")

    b1 = [i for i, (c, _o) in enumerate(comp["probeH1"])
          if any(x // 5 == 0 for x in c)]
    chk("probeH1 reaches band 1", len(b1) >= 2,
        f"cuts {b1} -> {len(b1) * len(CONDS)} band-1 frames per arm "
        f"(band 1 is the weakest band; only draws with d < 2.5 m can reach it)")

    offc = []
    for i, (c, _o) in enumerate(comp["probeH2"]):
        hist = {}
        for x in c:
            hist[x % 5] = hist.get(x % 5, 0) + 1
        offc.append(max(hist, key=hist.get) != 2)     # 2 == sector C == centre
    chk("probeH2 sits off the centre sector on >=6 of 8 cuts",
        sum(offc) >= 6, f"{sum(offc)}/8 off-centre "
                        f"(centre cuts: {[i for i, v in enumerate(offc) if not v]})")

    occ = probe_h3_occlusion()
    chk("probeH3 hidden on all 8 frozen draws", all(o[4] for o in occ),
        f"binding cut {min((o for o in occ if o[3] != math.inf), key=lambda o: o[3])[0]}"
        f", margin "
        f"{min(o[3] for o in occ if o[3] != math.inf) - 2.00:.2f} m")

    head(7, "run_probe.sh syntax")
    sh = os.path.join(HERE, "run_probe.sh")
    r = subprocess.run(["bash", "-n", sh], capture_output=True, text=True)
    chk("bash -n run_probe.sh", r.returncode == 0, r.stderr.strip()[:160])

    head(8, "driver --plan")
    r = subprocess.run(
        [sys.executable, os.path.join(HERE, "probe_driver.py"), "--plan",
         "--run", "260821_probe_on", "--scenes", ",".join(SCENES),
         "--conds", ",".join(CONDS), "--cams", "8", "--seed", str(SEED)],
        cwd=REPO, capture_output=True, text=True,
        env=dict(os.environ, PYTHONNOUSERSITE="1"))
    chk("--plan exits 0", r.returncode == 0, r.stderr.strip()[:160])
    chk("--plan refuses nothing", "[refused]" not in r.stdout,
        "all 3 scenes x 3 conditions admissible")
    chk("--plan prints a budget", "[budget]" in r.stdout,
        [ln for ln in r.stdout.splitlines() if "cuts ·" in ln][:1])

    head(9, "adjacent hazard-free sector metric")
    chk("synthetic per_frame gives the hand-computed answer", adjacency_selftest())

    print("\n" + "=" * 74)
    print("check_probe_cpu: " + ("ALL PASS" if OK[0] else "FAILURES ABOVE"))
    print("=" * 74)
    return 0 if OK[0] else 1


# --------------------------------------------------------------------------
def cells_for(rect, s, grid, step=0.05):
    """`labeler.polar_cells`, reimplemented on the opening rectangle only."""
    x0, y0, x1, y1 = rect
    yaw = s["yaw"]
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    asc = grid["sector_edges_deg"][::-1]
    bed = grid["band_edges_m"]
    ns, nb = grid["n_sectors"], grid["n_bands"]
    out, outside = set(), 0
    n_x = int(round((x1 - x0) / step)) + 1
    n_y = int(round((y1 - y0) / step)) + 1
    for ix in range(n_x):
        for iy in range(n_y):
            dx = (x0 + ix * step) - (-s["d"])
            dy = (y0 + iy * step) - s["y"]
            xc, yc = dx * cy + dy * sy, -dx * sy + dy * cy
            az = math.degrees(math.atan2(yc, xc))
            rng = math.hypot(xc, yc)
            k = max((j for j, e in enumerate(asc) if az >= e), default=-1)
            b = max((j for j, e in enumerate(bed) if rng >= e), default=-1)
            if 0 <= k < ns and 0 <= b < nb:
                out.add(b * ns + (ns - 1 - k))
            else:
                outside += 1
    return out, outside


def probe_h3_occlusion():
    sys.path.insert(0, SCENE_DIR)
    import importlib
    m = importlib.import_module("probeH3_hidden_hole")
    return m.occlusion_audit()[0]


def adjacency_selftest():
    """Hand-computed case, 20 cells, 5 sectors x 4 bands, cell = band*5+sector.

    One ON frame whose GT is {B2} = band index 1, sector index 1 -> cell 6.
    Adjacent (band 1, sector 0 and 2) = cells 5 (A2) and 7 (C2).
    Far      (band 1, sector 3 and 4) = cells 8 (D2) and 9 (E2).
    Probabilities: fire A2 only. Expect adj 1/2, adj frame 1/1, far 0/2.
    """
    sys.path.insert(0, HERE)
    import gridspec                                   # via CODE on sys.path
    import eval_probe as ep
    g = gridspec.load(GRID_JSON)
    ids = g.cell_ids
    p = {c: 0.0 for c in ids}
    gt = {c: 0 for c in ids}
    gt["B2"] = 1
    p["B2"] = 0.9
    p["A2"] = 0.8                                     # adjacent, fires
    p["D2"] = 0.1                                     # far, does not
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "per_frame.csv")
        with open(fp, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["frame_id", "scene_id", "tier", "toggle_state"]
                       + [f"p_{c}" for c in ids] + [f"g_{c}" for c in ids])
            w.writerow(["on/probeH2/x.png", "probeH2", "E", "on"]
                       + [f"{p[c]:.6f}" for c in ids] + [gt[c] for c in ids])
        d = ep.adjacent_sector_firing(fp, g, "probeH2")
    want = dict(n_frames=1, adj_cells=2, adj_fired=1, adj_cell_rate=0.5,
                adj_frame_rate=1.0, far_cells=2, far_fired=0, far_cell_rate=0.0)
    bad = {k: (d.get(k), v) for k, v in want.items() if d.get(k) != v}
    if bad:
        print(f"      got {d}\n      mismatch {bad}")
    return not bad


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(REPO, "experiments", "mainrun_0819", "code"))
    sys.exit(main())
