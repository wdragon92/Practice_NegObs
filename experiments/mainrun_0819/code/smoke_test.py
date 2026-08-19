"""End-to-end CPU smoke test: fake data -> make_split -> train -> eval -> compare -> viz.

  PYTHONNOUSERSITE=1 /home/vislab/miniconda3/envs/env_seg/bin/python smoke_test.py [--keep]
Runs with CUDA_VISIBLE_DEVICES="" in every child, so it never touches the GPU.
--keep leaves the temp workdir in place so the generated reports can be inspected.
"""
from __future__ import annotations

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


def run(name, args):
    print(f"\n=== {name}: {' '.join(str(a) for a in args[1:])}")
    r = subprocess.run([PY] + [str(a) for a in args], env=ENV, cwd=HERE,
                       capture_output=True, text=True)
    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-12:])
    print(tail)
    assert r.returncode == 0, f"{name} exited {r.returncode}"
    return r.stdout + r.stderr


# ------------------------------------------------------------------ fake data
def fake_frames(scene, root, rng, with_images=True, n_on=3):
    out = []
    for j in range(n_on + 1):
        off = j == n_on
        fid = f"{scene}_f{j}"
        rgbp = os.path.join(root, f"{fid}.png")
        if with_images:
            Image.fromarray(rng.integers(0, 255, (64, 64, 3), dtype=np.uint8)).save(rgbp)
            np.save(os.path.join(root, f"{fid}_d.npy"),
                    rng.random((64, 64)).astype(np.float32) * 8.0)
        gt = [0] * 15
        if not off:
            for b in range(3):                    # one positive per band -> all band metrics defined
                gt[b * 5 + int(rng.integers(0, 5))] = 1
        out.append(dict(frame_id=fid, scene_id=scene, round="r0",
                        toggle_state="off" if off else "on", rgb=rgbp,
                        depth=os.path.join(root, f"{fid}_d.npy") if with_images else None,
                        polar_gt=gt, raw_vis=None if off else dict(int_px=10, edge_ratio=0.1),
                        tier="off" if off else TIER_CYCLE[j % 3], tier_source="fake",
                        gt_source="fake", cam=dict(d=3.0, h_rel=1.2, yaw=0.0, pitch=-10.0),
                        notes="smoke"))
    return out


def build(tmp):
    rng = np.random.default_rng(0)
    img = os.path.join(tmp, "img")
    os.makedirs(img, exist_ok=True)
    frames = []
    for s in ("sceneA", "sceneB", "sceneC"):
        frames += fake_frames(s, img, rng)
    man = os.path.join(tmp, "dataset_manifest_v1.json")
    json.dump(dict(meta=dict(source="smoke_test"), frames=frames), open(man, "w"))
    sp = os.path.join(tmp, "split_v1.json")
    json.dump(dict(train=["sceneA"], val=["sceneB"], test=["sceneC"]), open(sp, "w"))

    big = [f for i in range(30)
           for f in fake_frames(f"scene{i:02d}" if i != 3 else "sceneN3", img, rng,
                                with_images=False, n_on=3)]
    bman = os.path.join(tmp, "big_manifest.json")
    json.dump(dict(meta={}, frames=big), open(bman, "w"))
    return man, sp, bman


# ------------------------------------------------------------------ unit checks
def units(tmp):
    from polar_dataset import (CELL_IDS, DEPTH_CLIP_M, PolarGridDataset, flip_perm,
                               flip_with_permutation, load_depth_m)
    assert CELL_IDS[0] == "A1" and CELL_IDS[4] == "E1" and CELL_IDS[7] == "C2" and CELL_IDS[14] == "E3"
    assert flip_perm() == [4, 3, 2, 1, 0, 9, 8, 7, 6, 5, 14, 13, 12, 11, 10]
    x = torch.arange(2 * 3 * 4, dtype=torch.float32).reshape(2, 3, 4)
    y = torch.tensor([[1.0, 0, 0, 0, 0] + [0] * 5 + [0, 0, 0, 0, 1]])
    xf, yf = flip_with_permutation(x, y)
    assert torch.equal(xf, torch.flip(x, dims=[-1]))
    assert yf.tolist() == [[0, 0, 0, 0, 1] + [0] * 5 + [1, 0, 0, 0, 0]]
    x2, y2 = flip_with_permutation(xf, yf)
    assert torch.equal(x2, x) and torch.equal(y2, y), "flip must be an involution"

    p16 = os.path.join(tmp, "d16.png")
    Image.fromarray(np.full((8, 8), 2500, np.uint16)).save(p16)
    assert abs(load_depth_m(p16).mean() - 2.5) < 1e-4, "PNG16 must be read as millimetres"
    pnp = os.path.join(tmp, "d.npy")
    np.save(pnp, np.full((8, 8), 12.0, np.float32))
    assert load_depth_m(pnp).mean() == 12.0
    try:
        load_depth_m(os.path.join(tmp, "d.exr"))
    except (NotImplementedError, RuntimeError, ValueError, OSError) as e:
        print(f"    exr branch reachable: {type(e).__name__}")

    ds = PolarGridDataset(os.path.join(tmp, "dataset_manifest_v1.json"),
                          os.path.join(tmp, "split_v1.json"), "test", "depth", img_size=32)
    xd, yd, md = ds[0]
    assert xd.shape == (1, 32, 32) and yd.shape == (15,)
    assert 0.0 <= float(xd.min()) and float(xd.max()) <= 1.0 + 1e-6, "depth must be clipped to [0,1]"
    assert set(md) == {"frame_id", "scene_id", "tier", "toggle_state"}
    ds2 = PolarGridDataset(os.path.join(tmp, "dataset_manifest_v1.json"),
                           os.path.join(tmp, "split_v1.json"), "train", "rgb",
                           train_aug=True, img_size=32,
                           aug_config=os.path.join(HERE, "aug_photometric.yaml"))
    assert ds2[0][0].shape == (3, 32, 32)
    print(f"    units OK (depth clip {DEPTH_CLIP_M} m, {len(ds)} test frames)")


# ------------------------------------------------------------------ main
def main():
    tmp = tempfile.mkdtemp(prefix="polar_smoke_")
    print(f"[smoke] workdir {tmp}")
    ok = False
    try:
        man, sp, bman = build(tmp)
        print("\n=== units")
        units(tmp)
        run("model_factory", ["model_factory.py"])
        run("bootstrap", ["bootstrap.py"])

        out = run("make_split", ["make_split.py", "--manifest", bman,
                                 "--out", f"{tmp}/split_big.json",
                                 "--report", f"{tmp}/SPLIT_PROPOSAL.md",
                                 "--hard-negatives", "sceneN3"])
        assert "FAIL" not in out, "make_split proof reported FAIL"
        assert open(f"{tmp}/SPLIT_PROPOSAL.md").read().startswith(
            "# SPLIT_PROPOSAL — PROVISIONAL — 아침 승인 대상")

        rundir = f"{tmp}/run_rgb"
        run("train_polar", ["train_polar.py", "--manifest", man, "--split", sp, "--input", "rgb",
                            "--out", rundir, "--smoke", 50, "--img-size", 64, "--batch", 2,
                            "--workers", 0, "--max-epochs", 40, "--patience", 15, "--aug"])
        for f in ("best.pt", "last.pt", "config.json", "metrics.csv"):
            assert os.path.exists(os.path.join(rundir, f)), f"missing {f}"

        ev = f"{tmp}/eval_rgb"
        line = run("eval_polar", ["eval_polar.py", "--manifest", man, "--split", sp,
                                  "--subset", "test", "--ckpt", f"{rundir}/best.pt",
                                  "--input", "rgb", "--out", ev, "--tau-op", 0.5,
                                  "--tau-star", "auto", "--tau-sweep", "0.3,0.5,0.7",
                                  "--img-size", 64, "--batch", 2, "--workers", 0, "--n-boot", 200])
        M = json.load(open(f"{ev}/metrics.json"))
        need = (["cell_f1", "cell_recall", "frame_fa_off", "cell_fpr_off", "cell_fpr_on_neg"]
                + [f"frame_recall_{t}" for t in "VEH"] + [f"cell_recall_{t}" for t in "VEH"]
                + [f"band{b}_cell_recall" for b in (1, 2, 3)])
        for k in need:
            v = M["point"]["op"][k]
            assert isinstance(v, float) and math.isfinite(v), f"metric {k} = {v}"
            c = M["ci"]["op"][k]
            assert math.isfinite(c["lo"]) and c["lo"] <= c["point"] + 1e-9 <= c["hi"] + 1e-9, (k, c)
        assert set(M["sweep"]) == {"0.3", "0.5", "0.7"}
        assert 0.0 < M["tau_star"] < 1.0
        assert os.path.exists(f"{ev}/METRICS_SECTION.md")
        assert "PROVISIONAL" not in open(f"{ev}/METRICS_SECTION.md").read()

        ev2 = f"{tmp}/eval_cmp"
        run("eval_polar --compare", ["eval_polar.py", "--manifest", man, "--split", sp,
                                     "--subset", "test", "--per-frame-a", f"{ev}/per_frame.csv",
                                     "--out", ev2, "--tau-star", 0.5, "--n-boot", 200,
                                     "--compare", f"{ev}/per_frame.csv"])
        C = json.load(open(f"{ev2}/metrics.json"))["compare"]
        assert C["n_common"] == M["counts"]["n_frames"]
        assert all(abs(v["diff"]) < 1e-12 and abs(v["lo"]) < 1e-12 and abs(v["hi"]) < 1e-12
                   for v in C["diff"].values()), "paired bootstrap of an arm against itself must be 0"

        viz = f"{tmp}/viz"
        run("make_viz", ["make_viz.py", "--per-frame", f"{ev}/per_frame.csv", "--manifest", man,
                         "--out", viz, "--n", 4])
        pngs = [f for f in os.listdir(viz) if f.endswith(".png")]
        assert pngs, "no viz panels written"

        import argparse
        import train_oversample
        from polar_dataset import PolarGridDataset
        s = train_oversample.make_sampler(
            PolarGridDataset(man, sp, "train", "rgb", img_size=32),
            argparse.Namespace(oversample_strict_h=4.0))
        assert s is not None and len(s) == 4, "oversample sampler self-check"

        final = [x for x in line.splitlines() if x.startswith("[eval]")][-1]
        print(f"\n[SMOKE GREEN] {final}")
        print(f"[SMOKE GREEN] viz panels={len(pngs)} tau*={M['tau_star']} "
              f"n_frames={M['counts']['n_frames']}")
        ok = True
    finally:
        if ok and "--keep" not in sys.argv:
            shutil.rmtree(tmp, ignore_errors=True)
        else:
            print(f"[{'SMOKE GREEN' if ok else 'SMOKE RED'}] artefacts kept at {tmp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
