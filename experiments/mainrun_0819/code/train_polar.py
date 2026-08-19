"""Train the polar hazard-grid head. One arm per run (--input rgb | depth).

Launch (the CALLER holds the GPU lock; -o is mandatory, see HARNESS_NOTES §1):
  flock -o -w 55 -E 201 /tmp/negobs_gpu.lock nice -n 5 \
    env PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=8 \
    /home/vislab/miniconda3/envs/env_seg/bin/python train_polar.py --input rgb ...
Inside python we only add the second guard: nvidia-smi free-mem >= 6 GB before touching torch.cuda,
else exit 202.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import subprocess
import sys
import time

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_factory  # noqa: E402
from polar_dataset import IMG_SIZE, N_CELLS, PolarGridDataset, load_aug_config  # noqa: E402

MIN_FREE_MB = 6144
EXIT_GPU_BUSY = 202


def build_argparser(desc=__doc__):
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("--manifest", required=True)
    p.add_argument("--split", required=True)
    p.add_argument("--input", choices=["rgb", "depth"], required=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", required=True, help="RUNDIR")
    p.add_argument("--max-epochs", type=int, default=150)
    p.add_argument("--patience", type=int, default=15)
    p.add_argument("--batch", type=int, default=8)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--weight-decay", type=float, default=0.0)  # harness run_experiment.py:247
    p.add_argument("--lr-schedule", choices=["linear", "const"], default="linear",
                   help="linear = decay to 0 over max-epochs, no warmup (harness convention)")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--aug", action="store_true", help="photometric-only train aug (RGB arm)")
    p.add_argument("--aug-config", default=None, help="aug_photometric.yaml (RESERVE, default off)")
    p.add_argument("--tau", type=float, default=0.5, help="threshold for the val cell-F1 stopper")
    p.add_argument("--smoke", type=int, default=0, help="stop after N optimizer steps, save, exit 0")
    p.add_argument("--img-size", type=int, default=IMG_SIZE, help=argparse.SUPPRESS)
    return p


def guard_gpu_free(min_free_mb=MIN_FREE_MB):
    """Pre-CUDA guard. Returns 'cuda' or 'cpu'; exits 202 if a GPU exists but is too full."""
    if os.environ.get("CUDA_VISIBLE_DEVICES", None) == "":
        print("[guard] CUDA_VISIBLE_DEVICES='' -> CPU run")
        return "cpu"
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=30)
        free = [int(x.strip()) for x in r.stdout.splitlines() if x.strip()]
    except Exception as e:
        print(f"[guard] nvidia-smi unavailable ({e}) -> CPU run")
        return "cpu"
    if not free:
        print("[guard] no GPU reported -> CPU run")
        return "cpu"
    if max(free) < min_free_mb:
        print(f"[guard] only {max(free)} MB free (< {min_free_mb} MB) -> abort", file=sys.stderr)
        sys.exit(EXIT_GPU_BUSY)
    print(f"[guard] {max(free)} MB free -> cuda")
    return "cuda"


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def make_sampler(ds, args):
    """Hook: train_oversample.py replaces this. None => plain shuffle."""
    return None


def cell_stats(prob, gt, tau):
    pred = prob >= tau
    pos = gt > 0.5
    tp = float((pred & pos).sum())
    fp = float((pred & ~pos).sum())
    fn = float((~pred & pos).sum())
    tn = float((~pred & ~pos).sum())
    f1 = 2 * tp / max(2 * tp + fp + fn, 1e-9)
    rec = tp / max(tp + fn, 1e-9)
    fpr = fp / max(fp + tn, 1e-9)
    return f1, rec, fpr


@torch.no_grad()
def evaluate(model, loader, device, crit, tau):
    model.eval()
    tot, n = 0.0, 0
    P, G = [], []
    for x, y, _m in loader:
        x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
        logits = model(x)
        tot += float(crit(logits, y)) * x.size(0)
        n += x.size(0)
        P.append(torch.sigmoid(logits).cpu().numpy())
        G.append(y.cpu().numpy())
    prob, gt = np.concatenate(P), np.concatenate(G)
    f1, rec, fpr = cell_stats(prob, gt, tau)
    return dict(loss=tot / max(n, 1), f1=f1, recall=rec, fpr=fpr)


def main(argv=None, parser=None):
    args = (parser or build_argparser()).parse_args(argv)
    device = torch.device(guard_gpu_free())
    if device.type == "cuda" and not torch.cuda.is_available():
        device = torch.device("cpu")
    set_seed(args.seed)
    os.makedirs(args.out, exist_ok=True)

    aug_cfg = load_aug_config(args.aug_config)
    dtr = PolarGridDataset(args.manifest, args.split, "train", args.input,
                           train_aug=args.aug, img_size=args.img_size, aug_config=aug_cfg,
                           seed=args.seed)
    dva = PolarGridDataset(args.manifest, args.split, "val", args.input,
                           train_aug=False, img_size=args.img_size, seed=args.seed)
    sampler = make_sampler(dtr, args)
    common = dict(num_workers=args.workers, pin_memory=(device.type == "cuda"),
                  persistent_workers=args.workers > 0)
    ltr = DataLoader(dtr, batch_size=args.batch, shuffle=(sampler is None), sampler=sampler,
                     drop_last=True, **common)
    lva = DataLoader(dva, batch_size=args.batch, shuffle=False, drop_last=False, **common)
    if len(ltr) == 0:
        print("[fatal] 0 train batches (drop_last=True and len(train) < batch)", file=sys.stderr)
        sys.exit(1)

    model = model_factory.build(args.input).to(device)
    crit = nn.BCEWithLogitsLoss()
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    if args.lr_schedule == "linear":
        sched = torch.optim.lr_scheduler.LambdaLR(
            opt, lambda e: max(0.0, 1.0 - e / max(args.max_epochs, 1)))
    else:
        sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda e: 1.0)

    cfg = dict(vars(args), device=device.type, n_train=len(dtr), n_val=len(dva),
               n_cells=N_CELLS, encoder="resnet34-unet-aux",
               params_m=round(sum(p.numel() for p in model.parameters()) / 1e6, 3),
               dropped_no_depth=dtr.n_dropped_no_depth + dva.n_dropped_no_depth)
    with open(os.path.join(args.out, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"[cfg] {args.input} train={len(dtr)} val={len(dva)} batches/ep={len(ltr)} dev={device.type}")

    mcsv = open(os.path.join(args.out, "metrics.csv"), "w", newline="")
    wr = csv.writer(mcsv)
    wr.writerow(["epoch", "train_loss", "val_loss", "val_f1", "val_recall", "val_fpr", "lr", "sec"])
    best, best_ep, bad, steps = -1.0, -1, 0, 0
    stop_reason = "max_epochs"

    for ep in range(1, args.max_epochs + 1):
        t0 = time.time()
        model.train()
        run, seen = 0.0, 0
        for x, y, _m in ltr:
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            loss = crit(model(x), y)
            loss.backward()
            opt.step()
            run += float(loss) * x.size(0)
            seen += x.size(0)
            steps += 1
            if args.smoke and steps >= args.smoke:
                break
        tr_loss = run / max(seen, 1)
        va = evaluate(model, lva, device, crit, args.tau)
        lr_now = opt.param_groups[0]["lr"]
        sched.step()
        sec = time.time() - t0
        wr.writerow([ep, f"{tr_loss:.6f}", f"{va['loss']:.6f}", f"{va['f1']:.6f}",
                     f"{va['recall']:.6f}", f"{va['fpr']:.6f}", f"{lr_now:.3e}", f"{sec:.2f}"])
        mcsv.flush()
        print(f"ep {ep:3d} train_loss {tr_loss:.4f} val_loss {va['loss']:.4f} "
              f"val_f1 {va['f1']:.4f} val_rec {va['recall']:.4f} val_fpr {va['fpr']:.4f} "
              f"lr {lr_now:.2e} {sec:.1f}s")

        ck = dict(state_dict=model.state_dict(), config=cfg, epoch=ep, val_f1=va["f1"])
        torch.save(ck, os.path.join(args.out, "last.pt"))
        if va["f1"] > best:
            best, best_ep, bad = va["f1"], ep, 0
            torch.save(ck, os.path.join(args.out, "best.pt"))
        else:
            bad += 1
            if bad >= args.patience:
                stop_reason = f"early_stop@{ep}"
                break
        if args.smoke and steps >= args.smoke:
            stop_reason = "smoke"
            break

    mcsv.close()
    cfg.update(best_val_f1=best, best_epoch=best_ep, stop_reason=stop_reason, steps=steps)
    with open(os.path.join(args.out, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)
    if not os.path.exists(os.path.join(args.out, "best.pt")):
        torch.save(dict(state_dict=model.state_dict(), config=cfg, epoch=0, val_f1=best),
                   os.path.join(args.out, "best.pt"))
    print(f"[done] {stop_reason} best_val_f1={best:.4f} @ep{best_ep} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
