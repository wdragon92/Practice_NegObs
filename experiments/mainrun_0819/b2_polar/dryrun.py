"""CPU dry run for the SegFormer-B2 polar arm. No GPU, no real data, no network.

    CUDA_VISIBLE_DEVICES="" PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 \
      /home/vislab/miniconda3/envs/env_seg/bin/python dryrun.py

Part 1 — optimisation loop: build the model on CPU, fabricate 2 batches of random
         [4,3,512,512] images + random n_cells-dim multi-hot targets (--grid selects
         the gridspec: 15 cells on V0, 20 on V1), run forward + backward +
         AdamW step twice, assert the loss is finite at both steps, report params and per-step
         wall time.
Part 2 — interface compatibility: fabricate a 4-frame manifest + split in a tempdir (same
         schema code/smoke_test.py uses) and pull a batch through ../code/polar_dataset.py's
         PolarGridDataset + a DataLoader into the model, exactly as train_polar.py does.

Exit 0 = GREEN. Any assertion failure = RED.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.abspath(os.path.join(HERE, os.pardir, "code"))
for _p in (CODE, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import b2_model_factory  # noqa: E402
import gridspec  # noqa: E402
from polar_dataset import IMG_SIZE, PolarGridDataset  # noqa: E402

GRID = gridspec.load(None)          # `python dryrun.py --grid gridspec_v1.json` swaps this
N_CELLS = GRID.n_cells
BATCH = 4
STEPS = 2
LR = 6e-5


def banner(msg):
    print(f"\n=== {msg}")


# --------------------------------------------------------------------- part 1
def opt_loop(route=None):
    banner(f"part 1: build + {STEPS} forward/backward/step on CPU (route={route or 'auto'})")
    torch.manual_seed(0)
    t0 = time.time()
    model = b2_model_factory.build("rgb", force_route=route, classes=N_CELLS)
    build_s = time.time() - t0
    n_par = sum(p.numel() for p in model.parameters())
    n_tr = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"    route      : {model.route}")
    print(f"    ckpt       : {b2_model_factory.LOCAL_MIT_B2}")
    print(f"    params     : {n_par / 1e6:.3f} M ({n_tr / 1e6:.3f} M trainable)")
    print(f"    build time : {build_s:.2f} s")

    crit = nn.BCEWithLogitsLoss()
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.0)
    model.train()

    g = torch.Generator().manual_seed(1)
    losses, times = [], []
    for step in range(1, STEPS + 1):
        x = torch.randn(BATCH, 3, IMG_SIZE, IMG_SIZE, generator=g)
        y = (torch.rand(BATCH, N_CELLS, generator=g) > 0.7).float()
        t = time.time()
        opt.zero_grad(set_to_none=True)
        logits = model(x)
        assert logits.shape == (BATCH, N_CELLS), f"logits {tuple(logits.shape)} != ({BATCH},{N_CELLS})"
        loss = crit(logits, y)
        loss.backward()
        gnorm = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1e9))
        opt.step()
        dt = time.time() - t
        lv = float(loss)
        assert np.isfinite(lv), f"step {step}: non-finite loss {lv}"
        assert np.isfinite(gnorm), f"step {step}: non-finite grad norm {gnorm}"
        losses.append(lv)
        times.append(dt)
        print(f"    step {step}: loss {lv:.6f}  grad_norm {gnorm:.3f}  "
              f"logits{tuple(logits.shape)}  {dt:.2f} s")

    assert losses[1] != losses[0], "loss identical across steps -> optimizer did not move weights"
    print(f"    per-step   : {np.mean(times):.2f} s mean over {STEPS} steps "
          f"(CPU, batch {BATCH} @ {IMG_SIZE}^2, fp32)")
    print("    [ok] finite loss at both steps, weights moved")
    return dict(params_m=n_par / 1e6, losses=losses, times=times, route=model.route)


# --------------------------------------------------------------------- part 2
TIERS = ["L", "M", "H"]


def fake_manifest(tmp, n_scenes=2, n_per=2):
    """4 frames total, same record schema as code/smoke_test.py fake_frames()."""
    rng = np.random.default_rng(0)
    img = os.path.join(tmp, "img")
    os.makedirs(img, exist_ok=True)
    frames = []
    for si in range(n_scenes):
        scene = f"dryscene{si}"
        for j in range(n_per):
            off = j == n_per - 1
            fid = f"{scene}_f{j}"
            rgbp = os.path.join(img, f"{fid}.png")
            Image.fromarray(rng.integers(0, 255, (96, 128, 3), dtype=np.uint8)).save(rgbp)
            dpath = os.path.join(img, f"{fid}_d.npy")
            np.save(dpath, rng.random((96, 128)).astype(np.float32) * 8.0)
            gt = [0] * N_CELLS
            if not off:
                for b in range(GRID.n_bands):
                    gt[b * GRID.n_sectors + int(rng.integers(0, GRID.n_sectors))] = 1
            frames.append(dict(
                frame_id=fid, scene_id=scene, round="r0",
                toggle_state="off" if off else "on", rgb=rgbp, depth=dpath, polar_gt=gt,
                raw_vis=None if off else dict(int_px=10, edge_ratio=0.1),
                tier="off" if off else TIERS[j % 3], tier_source="fake", gt_source="fake",
                cam=dict(d=3.0, h_rel=1.2, yaw=0.0, pitch=-10.0), notes="b2 dryrun"))
    man = os.path.join(tmp, "dataset_manifest_v1.json")
    with open(man, "w") as f:
        json.dump(dict(meta=dict(source="b2_dryrun"), frames=frames), f)
    sp = os.path.join(tmp, "split_v1.json")
    with open(sp, "w") as f:
        json.dump(dict(train=["dryscene0"], val=["dryscene1"], test=[]), f)
    return man, sp, len(frames)


def dataset_interface(model_route=None):
    banner("part 2: ../code/polar_dataset.py interface against a fabricated 4-frame manifest")
    with tempfile.TemporaryDirectory(prefix="b2_dryrun_") as tmp:
        man, sp, n = fake_manifest(tmp)
        print(f"    tempdir    : {tmp} ({n} frames, 2 scenes)")

        ds = PolarGridDataset(man, sp, "train", "rgb", train_aug=False, img_size=IMG_SIZE, grid=GRID)
        x, y, meta = ds[0]
        assert x.shape == (3, IMG_SIZE, IMG_SIZE), x.shape
        assert y.shape == (N_CELLS,) and y.dtype == torch.float32, (y.shape, y.dtype)
        assert set(meta) == {"frame_id", "scene_id", "tier", "toggle_state"}, set(meta)
        print(f"    item       : x{tuple(x.shape)} {x.dtype} y{tuple(y.shape)} "
              f"meta_keys={sorted(meta)}")
        print(f"    normalise  : x mean {float(x.mean()):+.3f} std {float(x.std()):.3f} "
              f"(ImageNet-normalised, matches mit-b2 preprocessor_config)")

        dsv = PolarGridDataset(man, sp, "val", "rgb", train_aug=False, img_size=IMG_SIZE, grid=GRID)
        ld = DataLoader(ds, batch_size=2, shuffle=False, num_workers=0, drop_last=False)
        xb, yb, mb = next(iter(ld))
        assert xb.shape == (2, 3, IMG_SIZE, IMG_SIZE), xb.shape
        assert yb.shape == (2, N_CELLS), yb.shape

        model = b2_model_factory.build("rgb", force_route=model_route, classes=N_CELLS).eval()
        with torch.no_grad():
            out = model(xb)
            loss = nn.BCEWithLogitsLoss()(out, yb)
        assert out.shape == (2, N_CELLS), out.shape
        assert np.isfinite(float(loss)), float(loss)
        print(f"    loader->model: batch x{tuple(xb.shape)} -> logits{tuple(out.shape)} "
              f"BCE {float(loss):.6f}  (train={len(ds)} val={len(dsv)})")

        # depth arm parity (1ch -> expanded to 3ch inside the wrapper)
        dsd = PolarGridDataset(man, sp, "train", "depth", train_aug=False, img_size=IMG_SIZE, grid=GRID)
        xd, _, _ = dsd[0]
        assert xd.shape == (1, IMG_SIZE, IMG_SIZE), xd.shape
        md = b2_model_factory.build("depth", force_route=model_route, classes=N_CELLS).eval()
        with torch.no_grad():
            od = md(xd[None])
        assert od.shape == (1, N_CELLS), od.shape
        print(f"    depth arm  : x{tuple(xd.shape)} -> logits{tuple(od.shape)} "
              f"(1ch expanded to 3ch in B2PolarNet.forward)")
        print("    [ok] PolarGridDataset <-> b2_model_factory interfaces match")


def main():
    global GRID, N_CELLS
    if "--grid" in sys.argv:
        GRID = gridspec.load(sys.argv[sys.argv.index("--grid") + 1])
        N_CELLS = GRID.n_cells
    print(f"[dryrun] grid {GRID.summary()}")
    if os.environ.get("CUDA_VISIBLE_DEVICES", None) != "":
        print("[dryrun] WARNING: CUDA_VISIBLE_DEVICES is not '' — forcing CPU anyway", file=sys.stderr)
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
    torch.set_num_threads(min(8, os.cpu_count() or 4))
    print(f"[dryrun] torch {torch.__version__} cuda_available={torch.cuda.is_available()} "
          f"threads={torch.get_num_threads()}")
    r = opt_loop()
    dataset_interface()
    banner("GREEN")
    print(f"    params {r['params_m']:.3f} M | route {r['route']} | "
          f"losses {r['losses'][0]:.6f} -> {r['losses'][1]:.6f} | "
          f"per-step {np.mean(r['times']):.2f} s CPU (batch {BATCH} @ {IMG_SIZE}^2)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
