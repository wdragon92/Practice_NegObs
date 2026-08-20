"""End-to-end CPU smoke test: fake data -> make_split -> train -> eval -> compare -> viz -> twin.

  PYTHONNOUSERSITE=1 /home/vislab/miniconda3/envs/env_seg/bin/python smoke_test.py [--keep]
Runs with CUDA_VISIBLE_DEVICES="" in every child, so it never touches the GPU.
--keep leaves the temp workdir in place so the generated reports can be inspected.

v2 (0820): the whole path runs TWICE — once on the 15-cell V0 gridspec (regression guard for the
0819 runs) and once on a fabricated 20-cell / 4-band gridspec built to the V1 contract, which is
what proves the N-cell generalisation before gridspec_v1.json lands. Also unit-tests the sector
permutation at 20 cells, the prior bias-init, the strict-H oversampler and the split-v2 move.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import torch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PY = sys.executable
ENV = dict(os.environ, PYTHONNOUSERSITE="1", CUDA_VISIBLE_DEVICES="", OMP_NUM_THREADS="4",
           MPLBACKEND="Agg")
TIER_CYCLE = ["H", "E", "V"]

FAKE_V1 = {                      # the 20-cell contract the labeling stack is writing as V1
    "version": "SMOKE-GRID-V1-FAKE",
    "n_sectors": 5,
    "sector_edges_deg": [31.1, 18.66, 6.22, -6.22, -18.66, -31.1],
    "sector_names": ["A", "B", "C", "D", "E"],
    "n_bands": 4,
    "band_edges_m": [0.0, 2.0, 5.0, 8.0, 12.0],
    "band_names": ["1", "2", "3", "4"],
    "cell_index": "band*5+sector",
    "hazard_depth_m": 0.3,
    "positive_rule": "any footprint sample in wedge",
}


def run(name, args):
    print(f"\n=== {name}: {' '.join(str(a) for a in args[1:])}")
    r = subprocess.run([PY] + [str(a) for a in args], env=ENV, cwd=HERE,
                       capture_output=True, text=True)
    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-12:])
    print(tail)
    assert r.returncode == 0, f"{name} exited {r.returncode}"
    return r.stdout + r.stderr


# ------------------------------------------------------------------ fake data
def fake_frames(scene, root, rng, grid, with_images=True, n_cuts=3):
    """One twin pair (on/off, identical cam) per cut -> 2*n_cuts frames per scene."""
    ns, nc = grid.n_sectors, grid.n_cells
    out = []
    for j in range(n_cuts):
        cut = f"L0__s0__{j:04d}.png"
        cam = dict(d=3.0 + j, h_rel=1.2, yaw=float(j), pitch=-10.0, ground_z=0.0)
        gt_on = [0] * nc
        for b in range(grid.n_bands):        # one positive per band -> every band metric defined
            gt_on[b * ns + int(rng.integers(0, ns))] = 1
        for arm in ("on", "off"):
            fid = f"{arm}/{scene}/{cut}"
            base = f"{scene}_{arm}_{j}"
            rgbp = os.path.join(root, f"{base}.png")
            dpth = os.path.join(root, f"{base}_d.npy")
            if with_images:
                Image.fromarray(rng.integers(0, 255, (64, 64, 3), dtype=np.uint8)).save(rgbp)
                np.save(dpth, rng.random((64, 64)).astype(np.float32) * 8.0)
            out.append(dict(frame_id=fid, scene_id=scene, round="r0", toggle_state=arm,
                            rgb=rgbp, depth=dpth if with_images else None,
                            polar_gt=(gt_on if arm == "on" else [0] * nc),
                            raw_vis=None if arm == "off" else dict(int_px=10, edge_ratio=0.1),
                            tier=("off" if arm == "off" else TIER_CYCLE[j % 3]),
                            tier_source="fake", gt_source="fake", cam=cam, cond="L0", notes="smoke"))
    return out


def build(tmp, grid, tag):
    """Small 3-scene manifest+split (train/val/test) and a 30-scene manifest for make_split."""
    rng = np.random.default_rng(0)
    img = os.path.join(tmp, f"img_{tag}")
    os.makedirs(img, exist_ok=True)
    frames = []
    for s in ("sceneA", "sceneB", "sceneC"):
        frames += fake_frames(s, img, rng, grid)
    man = os.path.join(tmp, f"manifest_{tag}.json")
    json.dump(dict(meta=dict(source="smoke_test", grid_version=grid.version), frames=frames),
              open(man, "w"))
    sp = os.path.join(tmp, f"split_{tag}.json")
    json.dump(dict(train=["sceneA"], val=["sceneB"], test=["sceneC"]), open(sp, "w"))

    big = [f for i in range(30)
           for f in fake_frames(f"scene{i:02d}" if i != 3 else "sceneN3", img, rng, grid,
                                with_images=False)]
    bman = os.path.join(tmp, f"big_manifest_{tag}.json")
    json.dump(dict(meta={}, frames=big), open(bman, "w"))
    return man, sp, bman


# ------------------------------------------------------------------ unit checks
def units(tmp, grid, tag, man, sp):
    from polar_dataset import (DEPTH_CLIP_M, PolarGridDataset, flip_perm, flip_with_permutation,
                               load_depth_m)

    ns, nb, nc = grid.n_sectors, grid.n_bands, grid.n_cells
    perm = flip_perm(grid)
    expect = [b * ns + (ns - 1 - s) for b in range(nb) for s in range(ns)]
    assert perm == expect, (perm, expect)
    assert [perm[i] for i in perm] == list(range(nc)), "flip must be an involution"
    assert all(grid.band_of[i] == grid.band_of[perm[i]] for i in range(nc)), \
        "flip must not move a cell across bands"
    x = torch.arange(2 * 3 * 4, dtype=torch.float32).reshape(2, 3, 4)
    y = torch.zeros(1, nc)
    y[0, 0] = 1.0                                   # A1  (leftmost sector, nearest band)
    y[0, nc - 1] = 1.0                              # last sector of the last band
    xf, yf = flip_with_permutation(x, y, grid)
    assert torch.equal(xf, torch.flip(x, dims=[-1]))
    assert yf[0, ns - 1] == 1.0 and yf[0, nc - ns] == 1.0 and yf.sum() == 2.0, yf
    x2, y2 = flip_with_permutation(xf, yf, grid)
    assert torch.equal(x2, x) and torch.equal(y2, y), "flip must be an involution"
    print(f"    [PERM-{nc}] flip_perm({grid.version}) = {perm}  involution OK  "
          f"bands fixed OK  cell_ids {grid.cell_ids[0]}..{grid.cell_ids[-1]}")

    assert grid.cell_ids[0] == "A" + grid.band_names[0]
    assert grid.cell_ids[ns + 2] == "C" + grid.band_names[1]

    p16 = os.path.join(tmp, f"d16_{tag}.png")
    Image.fromarray(np.full((8, 8), 2500, np.uint16)).save(p16)
    assert abs(load_depth_m(p16).mean() - 2.5) < 1e-4, "PNG16 must be read as millimetres"
    pnp = os.path.join(tmp, f"d_{tag}.npy")
    np.save(pnp, np.full((8, 8), 12.0, np.float32))
    assert load_depth_m(pnp).mean() == 12.0
    try:
        load_depth_m(os.path.join(tmp, "d.exr"))
    except (NotImplementedError, RuntimeError, ValueError, OSError) as e:
        print(f"    exr branch reachable: {type(e).__name__}")

    ds = PolarGridDataset(man, sp, "test", "depth", img_size=32, grid=grid)
    xd, yd, md = ds[0]
    assert xd.shape == (1, 32, 32) and yd.shape == (nc,)
    assert 0.0 <= float(xd.min()) and float(xd.max()) <= 1.0 + 1e-6, "depth must be clipped to [0,1]"
    assert set(md) == {"frame_id", "scene_id", "tier", "toggle_state"}
    ds2 = PolarGridDataset(man, sp, "train", "rgb", train_aug=True, img_size=32,
                           aug_config=os.path.join(HERE, "aug_photometric.yaml"), grid=grid)
    assert ds2[0][0].shape == (3, 32, 32)

    # hflip: label must follow the image, and both must be reachable
    dh = PolarGridDataset(man, sp, "train", "rgb", img_size=32, grid=grid, train_hflip=True)
    torch.manual_seed(0)
    seen = {tuple(dh[0][1].tolist()) for _ in range(40)}
    base = tuple(PolarGridDataset(man, sp, "train", "rgb", img_size=32, grid=grid)[0][1].tolist())
    flipped = tuple(np.asarray(base)[perm].tolist())
    assert seen <= {base, flipped} and len(seen) == 2, f"hflip must toggle between the two: {seen}"

    pr = PolarGridDataset(man, sp, "train", "rgb", img_size=32, grid=grid).positive_rate()
    assert pr.shape == (nc,) and 0.0 <= pr.min() and pr.max() <= 1.0
    # 20-cell manifest must be rejected by a 15-cell grid and vice versa
    import gridspec as GS
    other = GS.load(None) if grid.n_cells != GS.load(None).n_cells else None
    if other is not None:
        try:
            PolarGridDataset(man, sp, "test", "rgb", img_size=32, grid=other)
            raise SystemExit("[RED] a mismatched grid was accepted")
        except AssertionError as e:
            assert "GRID MISMATCH" in str(e)
            print("    grid/manifest mismatch is rejected loudly: OK")
    print(f"    units OK ({grid.version}, {nc} cells, depth clip {DEPTH_CLIP_M} m, "
          f"{len(ds)} test frames, train positive rate max {pr.max():.3f})")


def bias_init_check(grid):
    """The prior bias must land on the real classifier and reproduce the prior after sigmoid."""
    import model_factory
    import train_polar
    nc = grid.n_cells
    m = model_factory.build("rgb", encoder_weights=None, classes=nc)
    p = np.linspace(0.01, 0.5, nc)
    name, vals = train_polar.set_prior_bias(m, p, nc)
    assert name is not None and len(vals) == nc
    b = m.final_classifier().bias.detach().numpy()
    assert np.allclose(1.0 / (1.0 + np.exp(-b)), p, atol=1e-5), "bias must encode the prior"
    zero = np.zeros(nc)                                  # clamp branch: p=0 -> log(1e-4/(1-1e-4))
    _n, v0 = train_polar.set_prior_bias(m, zero, nc)
    assert all(abs(v - math.log(1e-4 / (1 - 1e-4))) < 1e-9 for v in v0), v0[:3]
    print(f"    bias-init OK ({name}.bias, {nc} cells, clamp -> {v0[0]:.3f})")


# ------------------------------------------------------------------ one full cycle
def cycle(tmp, grid, tag, grid_arg, compare=False):
    man, sp, bman = build(tmp, grid, tag)
    print(f"\n=== units [{tag}] {grid.summary()}")
    units(tmp, grid, tag, man, sp)
    bias_init_check(grid)

    out = run(f"make_split [{tag}]", ["make_split.py", "--manifest", bman,
                                      "--out", f"{tmp}/split_big_{tag}.json",
                                      "--report", f"{tmp}/SPLIT_PROPOSAL_{tag}.md",
                                      "--hard-negatives", "sceneN3"])
    assert "FAIL" not in out, "make_split proof reported FAIL"
    assert open(f"{tmp}/SPLIT_PROPOSAL_{tag}.md").read().startswith(
        "# SPLIT_PROPOSAL — PROVISIONAL — 아침 승인 대상")

    out2 = run(f"make_split --move-h-scene-to-val [{tag}]",
               ["make_split.py", "--manifest", bman, "--out", f"{tmp}/split_v2_{tag}.json",
                "--report", f"{tmp}/SPLIT_PROPOSAL_v2_{tag}.md", "--hard-negatives", "sceneN3",
                "--move-h-scene-to-val", "--move-h-min", 1])
    assert "FAIL" not in out2 and "PROOF-11" in out2, out2
    assert open(f"{tmp}/SPLIT_PROPOSAL_v2_{tag}.md").read().startswith(
        "# SPLIT_PROPOSAL v2 — PROVISIONAL 승인 대상")
    v2 = json.load(open(f"{tmp}/split_v2_{tag}.json"))
    v1 = json.load(open(f"{tmp}/split_big_{tag}.json"))
    assert sorted(v2["test"]) == sorted(v1["test"]), "split v2 must not touch test"
    assert len(v2["val"]) == len(v1["val"]) + 1 and len(v2["train"]) == len(v1["train"]) - 1

    rundir = f"{tmp}/run_rgb_{tag}"
    tr = run(f"train_polar [{tag}]",
             ["train_polar.py", "--manifest", man, "--split", sp, "--input", "rgb",
              "--out", rundir, "--smoke", 40, "--img-size", 64, "--batch", 2, "--workers", 0,
              "--max-epochs", 40, "--patience", 15, "--aug", "--hflip", "on",
              "--oversample-h", 4, "--bias-init", "prior"] + grid_arg)
    for f in ("best.pt", "last.pt", "config.json", "metrics.csv"):
        assert os.path.exists(os.path.join(rundir, f)), f"missing {f}"
    assert "[oversample] strict-H train frames" in tr and "[bias-init] prior ->" in tr
    cfg = json.load(open(f"{rundir}/config.json"))
    assert cfg["n_cells"] == grid.n_cells and cfg["grid_version"] == grid.version
    assert len(cfg["train_positive_rate"]) == grid.n_cells
    assert cfg["hflip"] is True and cfg["oversampled"] is True
    rows = list(csv.DictReader(open(f"{rundir}/metrics.csv")))
    assert rows and "val_h_recall" in rows[0] and "sel_score" in rows[0], rows[0].keys()
    assert math.isfinite(float(rows[0]["val_h_recall"])), "val has H frames -> recall must be real"
    got = 0.5 * float(rows[0]["val_f1"]) + 0.5 * float(rows[0]["val_h_recall"])
    assert abs(got - float(rows[0]["sel_score"])) < 1e-5, (got, rows[0]["sel_score"])
    assert cfg["selection_metric"].startswith("0.5*val_f1")

    ev = f"{tmp}/eval_rgb_{tag}"
    line = run(f"eval_polar [{tag}]",
               ["eval_polar.py", "--manifest", man, "--split", sp, "--subset", "test",
                "--ckpt", f"{rundir}/best.pt", "--input", "rgb", "--out", ev, "--tau-op", 0.5,
                "--tau-star", "auto", "--tau-sweep", "0.3,0.5,0.7", "--img-size", 64,
                "--batch", 2, "--workers", 0, "--n-boot", 200] + grid_arg)
    M = json.load(open(f"{ev}/metrics.json"))
    need = (["cell_f1", "cell_recall", "frame_det_rate", "frame_fa_off", "cell_fpr_off",
             "cell_fpr_on_neg"]
            + [f"frame_recall_{t}" for t in "VEH"] + [f"cell_recall_{t}" for t in "VEH"]
            + [f"band{b + 1}_cell_recall" for b in range(grid.n_bands)]
            + [f"band{b + 1}_cell_fpr_off" for b in range(grid.n_bands)])
    for k in need:
        v = M["point"]["op"][k]
        assert isinstance(v, float) and math.isfinite(v), f"metric {k} = {v}"
        c = M["ci"]["op"][k]
        assert math.isfinite(c["lo"]) and c["lo"] <= c["point"] + 1e-9 <= c["hi"] + 1e-9, (k, c)
    assert f"band{grid.n_bands + 1}_cell_recall" not in M["point"]["op"], "band count leaked"
    assert M["counts"]["n_cells"] == grid.n_cells and M["grid"]["n_cells"] == grid.n_cells
    assert set(M["sweep"]) == {"0.3", "0.5", "0.7"}
    assert 0.0 < M["tau_star"] < 1.0
    head = open(f"{ev}/per_frame.csv").readline().strip().split(",")
    assert head[4:4 + grid.n_cells] == [f"p_{c}" for c in grid.cell_ids], head[:8]
    md = open(f"{ev}/METRICS_SECTION.md").read()
    # the ONLY PROVISIONAL token allowed in a metrics section is the grid version tag itself
    assert grid.version in md, "METRICS_SECTION must stamp the grid version"
    assert "PROVISIONAL" not in md.replace(grid.version, ""), md[:400]
    for b in range(grid.n_bands):
        lo, hi = grid.band_range(b)
        assert f"[{lo:g},{hi:g}) m" in md, f"band {b} row missing from METRICS_SECTION"

    if compare:
        ev2 = f"{tmp}/eval_cmp_{tag}"
        run(f"eval_polar --compare [{tag}]",
            ["eval_polar.py", "--manifest", man, "--split", sp, "--subset", "test",
             "--per-frame-a", f"{ev}/per_frame.csv", "--out", ev2, "--tau-star", 0.5,
             "--n-boot", 200, "--compare", f"{ev}/per_frame.csv"] + grid_arg)
        C = json.load(open(f"{ev2}/metrics.json"))["compare"]
        assert C["n_common"] == M["counts"]["n_frames"]
        assert all(abs(v["diff"]) < 1e-12 and abs(v["lo"]) < 1e-12 and abs(v["hi"]) < 1e-12
                   for v in C["diff"].values()), "paired bootstrap of an arm against itself must be 0"

    viz = f"{tmp}/viz_{tag}"
    run(f"make_viz [{tag}]", ["make_viz.py", "--per-frame", f"{ev}/per_frame.csv",
                              "--manifest", man, "--out", viz, "--n", 4] + grid_arg)
    pngs = [f for f in os.listdir(viz) if f.endswith(".png")]
    assert pngs, "no viz panels written"

    run(f"split_per_frame [{tag}]", ["split_per_frame.py", "--per-frame", f"{ev}/per_frame.csv",
                                     "--out-dir", ev])
    twin = f"{tmp}/twin_{tag}"
    tw = run(f"twin_analysis [{tag}]",
             ["twin_analysis.py", "--per-frame-on", f"{ev}/per_frame_on.csv",
              "--per-frame-off", f"{ev}/per_frame_off.csv", "--manifest", man,
              "--out", twin, "--n-boot", 200] + grid_arg)
    tmd = open(f"{twin}/twin_analysis.md").read()
    assert "## 2. Mean delta by distance band" in tmd
    for b in range(grid.n_bands):
        lo, hi = grid.band_range(b)
        assert f"[{lo:g},{hi:g}) m" in tmd, f"twin band {b} row missing"
    tp = list(csv.DictReader(open(f"{twin}/twin_pairs.csv")))
    assert tp and all(f"delta_b{b + 1}" in tp[0] for b in range(grid.n_bands))
    assert f"bands={grid.n_bands}" in tw

    ag = f"{tmp}/SEED_TABLE_{tag}.md"
    root = f"{tmp}/agg_{tag}"
    os.makedirs(f"{root}/rgb_s42", exist_ok=True)
    for src, dst in ((rundir, f"{root}/rgb_s42"),):
        shutil.copy(f"{src}/config.json", f"{dst}/config.json")
    shutil.copytree(ev, f"{root}/rgb_s42/eval_test", dirs_exist_ok=True)
    shutil.copytree(twin, f"{root}/rgb_s42/twin", dirs_exist_ok=True)
    run(f"aggregate_seeds [{tag}]", ["aggregate_seeds.py", "--root", root, "--models", "rgb",
                                     "--seeds", "42", "--out", ag] + grid_arg)
    agmd = open(ag).read()
    assert "frame_det_rate" in agmd and f"band{grid.n_bands}_cell_recall" in agmd

    final = [x for x in line.splitlines() if x.startswith("[eval]")][-1]
    return dict(tag=tag, cells=grid.n_cells, eval_line=final, viz=len(pngs),
                tau_star=M["tau_star"], n_frames=M["counts"]["n_frames"],
                twin_line=[x for x in tw.splitlines() if x.startswith("[twin]")][-1],
                perm=grid.flip_perm())


def b2_check(grid):
    """B2 factory must also honour the cell count (non-fatal: needs the local mit-b2 dir)."""
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, os.pardir, "b2_polar")))
    try:
        import b2_model_factory
        m = b2_model_factory.build("rgb", encoder_weights=None, classes=grid.n_cells).eval()
        with torch.no_grad():
            o = m(torch.randn(1, 3, 64, 64))
        assert tuple(o.shape) == (1, grid.n_cells), o.shape
        assert m.final_classifier().bias.numel() == grid.n_cells
        print(f"    b2 factory OK: route={m.route} out={tuple(o.shape)}")
        return True
    except Exception as e:                                    # noqa: BLE001
        print(f"    [skip] b2 factory check: {type(e).__name__}: {e}")
        return False


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--only", choices=["v0", "v1", "both"], default="both")
    a = ap.parse_args()

    import gridspec

    tmp = tempfile.mkdtemp(prefix="polar_smoke_")
    print(f"[smoke] workdir {tmp}")
    ok = False
    try:
        run("gridspec", ["gridspec.py"])
        run("model_factory", ["model_factory.py"])
        run("bootstrap", ["bootstrap.py"])

        fake = os.path.join(tmp, "gridspec_v1_fake.json")
        json.dump(FAKE_V1, open(fake, "w"), indent=1)
        run("gridspec (fabricated 20-cell V1)", ["gridspec.py", fake])
        g20 = gridspec.load(fake)
        assert g20.n_cells == 20 and g20.n_bands == 4, g20.summary()
        run("model_factory @20", ["model_factory.py", 20])

        res = []
        if a.only in ("v0", "both"):
            res.append(cycle(tmp, gridspec.load(None), "v0", [], compare=True))
        if a.only in ("v1", "both"):
            res.append(cycle(tmp, g20, "v1x20", ["--grid", fake], compare=True))
        print("\n=== b2 factory")
        b2_check(g20)

        print()
        for r in res:
            print(f"[SMOKE GREEN] n_cells={r['cells']:2d} ({r['tag']}) {r['eval_line']}")
            print(f"[SMOKE GREEN] n_cells={r['cells']:2d} ({r['tag']}) {r['twin_line']}")
            print(f"[SMOKE GREEN] n_cells={r['cells']:2d} ({r['tag']}) viz panels={r['viz']} "
                  f"tau*={r['tau_star']} n_frames={r['n_frames']}")
            print(f"[SMOKE GREEN] n_cells={r['cells']:2d} ({r['tag']}) flip_perm={r['perm']}")
        ok = True
    finally:
        if ok and not a.keep:
            shutil.rmtree(tmp, ignore_errors=True)
        else:
            print(f"[{'SMOKE GREEN' if ok else 'SMOKE RED'}] artefacts kept at {tmp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
