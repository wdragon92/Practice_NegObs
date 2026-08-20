"""Train the polar hazard-grid head. One arm per run (--input rgb | depth).

RECIPE v2 (0820, brief Phase 4 — all three models share it):
  * --grid          N-cell generalisation; default = gridspec_v0.json (15 cells) so pre-0820 runs
                    reproduce. The V1 runs pass --grid gridspec_v1.json (20 cells).
  * checkpoint selection = 0.5*val_cell_F1(tau) + 0.5*val_H_frame_recall  (`sel_score`), and
                    early stopping keys on it. val_H_frame_recall = fraction of val frames with
                    tier=='H' (and >=1 GT-positive cell) for which SOME GT-positive cell is
                    predicted at tau. Zero H frames in val -> fall back to val F1 + loud warning.
  * --bias-init prior|zero (default prior): the final classifier bias starts at the per-cell
                    log-odds of the TRAIN positive rate, so epoch 1 already predicts the prior
                    instead of spending epochs walking the bias down from 0.
  * --hflip on|off (default on): horizontal flip p=0.5 with the sector permutation (D8 helper,
                    generalised to n bands: sectors reversed inside each band, band order kept).
  * --oversample-h K (default 1.0 = off): strict-H train frames drawn K times more often
                    (WeightedRandomSampler, epoch length unchanged) — folded in from the
                    train_oversample.py prototype.

AUX PIXEL LOSS (0820 brief Phase 6, OPTIONAL, default OFF — omit the flag and this file behaves
exactly as it did for the v2 queue, down to the metrics.csv header and the config.json key set):
  * --aux-mask-dir DIR  turns it on: the train dataset also yields the frame's amodal mask
                    (annotations/amodal/<stem>.png, missing file = empty mask) and the model is
                    built with model_factory use_mask_head=True, so smp.Unet's dense output is
                    kept instead of discarded.
  * --aux-lambda L (default 0.5):  loss = BCE(cell_logits, y) + L * BCE(mask_logits, mask).
                    Both terms are logged per epoch as train_loss_cell / train_loss_aux (extra
                    trailing columns, aux runs only); `train_loss` stays the total, i.e. the
                    quantity actually minimised.
  * VALIDATION AND CHECKPOINT SELECTION STAY CELL-ONLY, deliberately: sel_score must remain
                    numerically comparable with the v2 runs this ablation is measured against.
                    Adding L*BCE_pixel to val_loss would change which epoch wins and turn a
                    one-variable ablation (does the pixel signal help H recall / FA / twin delta?)
                    into a two-variable one. The pixel head is a training-time regulariser only;
                    nothing downstream (eval_polar, twin_analysis, infer_photo) reads it, and the
                    checkpoint's state_dict is byte-compatible with the plain logits-only model.

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
import math
import os
import random
import subprocess
import sys
import time

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, WeightedRandomSampler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gridspec  # noqa: E402
import model_factory  # noqa: E402
from polar_dataset import IMG_SIZE, PolarGridDataset, load_aug_config  # noqa: E402

MIN_FREE_MB = 6144
EXIT_GPU_BUSY = 202
PRIOR_CLAMP = (1e-4, 1.0 - 1e-4)


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
    p.add_argument("--hflip", choices=["on", "off"], default="on",
                   help="[v2] hflip + sector permutation, p=0.5 (both arms). Default ON.")
    p.add_argument("--oversample-h", type=float, default=1.0, metavar="K",
                   help="[v2] draw strict-H train frames K times more often (1.0 = off; v2 uses 4)")
    p.add_argument("--bias-init", choices=["prior", "zero"], default="prior",
                   help="[v2] final-classifier bias = per-cell log-odds of the train positive rate")
    p.add_argument("--tau", type=float, default=0.5,
                   help="threshold for val cell-F1 and val H frame-recall (selection score)")
    p.add_argument("--aux-mask-dir", default=None, metavar="DIR",
                   help="[phase6, OFF unless given] amodal-mask PNG dir -> add a pixel BCE term")
    p.add_argument("--aux-lambda", type=float, default=0.5, metavar="L",
                   help="[phase6] weight of the pixel BCE (ignored without --aux-mask-dir)")
    p.add_argument("--smoke", type=int, default=0, help="stop after N optimizer steps, save, exit 0")
    p.add_argument("--img-size", type=int, default=IMG_SIZE, help=argparse.SUPPRESS)
    gridspec.add_grid_arg(p)
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


# ------------------------------------------------------------------ v2: oversample
def is_strict_h(rec):
    """strict-H == tier 'H' on the hazard-ON arm with >=1 GT-positive cell (make_split's rule)."""
    return (rec.get("tier") == "H" and rec.get("toggle_state") != "off"
            and any(int(v) for v in rec["polar_gt"]))


def make_sampler(ds, args):
    """--oversample-h K -> WeightedRandomSampler (epoch length unchanged so 'epoch' stays
    comparable across arms). None => plain shuffle. train_oversample.py is now a thin wrapper."""
    k = float(getattr(args, "oversample_h", None) or getattr(args, "oversample_strict_h", 1.0) or 1.0)
    if k <= 1.0:
        return None
    w = [k if is_strict_h(r) else 1.0 for r in ds.items]
    n_h = sum(1 for x in w if x > 1.0)
    print(f"[oversample] strict-H train frames {n_h}/{len(w)} weighted x{k:g} "
          f"(expected share {n_h * k / (n_h * k + (len(w) - n_h)):.3f} vs {n_h / len(w):.3f})")
    if n_h == 0:
        print("[oversample] WARNING: no strict-H frame in train -> sampler is a no-op")
        return None
    return WeightedRandomSampler(torch.as_tensor(w, dtype=torch.double), num_samples=len(w),
                                 replacement=True)


# ------------------------------------------------------------------ v2: bias prior
def find_final_classifier(model, n_cells):
    """The last Linear/Conv2d whose output width == n_cells, preferring a 'classif*' name.

    Covers both stacks: smp aux head -> net.classification_head[3] (Linear(512,C)); B2 route A ->
    net.classifier (Linear(512,C)); B2 route B -> net.decode_head.classifier (Conv2d(768,C,1))."""
    fn = getattr(model, "final_classifier", None)
    if callable(fn):
        m = fn()
        if m is not None and getattr(m, "bias", None) is not None:
            return m
    named, pref = [], []
    for name, m in model.named_modules():
        out = getattr(m, "out_features", None) or getattr(m, "out_channels", None)
        if out == n_cells and getattr(m, "bias", None) is not None:
            named.append((name, m))
            if "classif" in name.lower():
                pref.append((name, m))
    pick = (pref or named)
    return pick[-1][1] if pick else None


def set_prior_bias(model, prior, n_cells, clamp=PRIOR_CLAMP):
    """bias <- log(p/(1-p)) per cell. Returns (module_name, bias_list) or (None, None)."""
    p = np.clip(np.asarray(prior, dtype=np.float64), clamp[0], clamp[1])
    b = np.log(p / (1.0 - p))
    mod = find_final_classifier(model, n_cells)
    if mod is None or getattr(mod, "bias", None) is None:
        print("[bias-init] WARNING: no final classifier with a bias found -> left at default",
              file=sys.stderr)
        return None, None
    with torch.no_grad():
        mod.bias.copy_(torch.as_tensor(b, dtype=mod.bias.dtype, device=mod.bias.device)
                       .reshape(mod.bias.shape))
    name = type(mod).__name__
    print(f"[bias-init] prior -> {name}.bias  p[min/med/max]="
          f"{p.min():.4f}/{np.median(p):.4f}/{p.max():.4f}  bias[min/max]={b.min():.3f}/{b.max():.3f}")
    return name, [float(x) for x in b]


# ------------------------------------------------------------------ metrics
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


def h_frame_recall(prob, gt, tier, tau):
    """(recall, n) over frames with tier=='H' carrying >=1 GT-positive cell: ANY hit counts."""
    tier = np.asarray(tier)
    pos = gt > 0.5
    sel = (tier == "H") & pos.any(1)
    n = int(sel.sum())
    if n == 0:
        return float("nan"), 0
    det = ((prob >= tau) & pos)[sel].any(1)
    return float(det.mean()), n


@torch.no_grad()
def evaluate(model, loader, device, crit, tau):
    model.eval()
    tot, n = 0.0, 0
    P, G, T = [], [], []
    for x, y, m in loader:                # val is ALWAYS cell-only (no aux_mask_dir) -> 3-tuple
        x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
        logits = model(x)
        if isinstance(logits, tuple):     # use_mask_head model: drop the dense output here
            logits = logits[0]
        tot += float(crit(logits, y)) * x.size(0)
        n += x.size(0)
        P.append(torch.sigmoid(logits).cpu().numpy())
        G.append(y.cpu().numpy())
        T += list(m["tier"])
    prob, gt = np.concatenate(P), np.concatenate(G)
    f1, rec, fpr = cell_stats(prob, gt, tau)
    hrec, n_h = h_frame_recall(prob, gt, T, tau)
    return dict(loss=tot / max(n, 1), f1=f1, recall=rec, fpr=fpr, h_recall=hrec, n_h=n_h)


def selection_score(f1, h_recall):
    """0.5*val cell F1 + 0.5*val H frame recall; falls back to F1 when val has no H frame."""
    if h_recall is None or not math.isfinite(h_recall):
        return f1, True
    return 0.5 * f1 + 0.5 * h_recall, False


def main(argv=None, parser=None):
    args = (parser or build_argparser()).parse_args(argv)
    grid = gridspec.from_args(args)
    device = torch.device(guard_gpu_free())
    if device.type == "cuda" and not torch.cuda.is_available():
        device = torch.device("cpu")
    set_seed(args.seed)
    os.makedirs(args.out, exist_ok=True)
    print(f"[grid] {grid.summary()}  <- {grid.path}")

    aug_cfg = load_aug_config(args.aug_config)
    hflip = args.hflip == "on"
    aux_on = bool(args.aux_mask_dir)          # phase 6; everything below is a no-op when False
    dtr = PolarGridDataset(args.manifest, args.split, "train", args.input,
                           train_aug=args.aug, img_size=args.img_size, aug_config=aug_cfg,
                           seed=args.seed, grid=grid, train_hflip=hflip,
                           aux_mask_dir=args.aux_mask_dir)
    dva = PolarGridDataset(args.manifest, args.split, "val", args.input,
                           train_aug=False, img_size=args.img_size, seed=args.seed, grid=grid)
    sampler = make_sampler(dtr, args)
    common = dict(num_workers=args.workers, pin_memory=(device.type == "cuda"),
                  persistent_workers=args.workers > 0)
    ltr = DataLoader(dtr, batch_size=args.batch, shuffle=(sampler is None), sampler=sampler,
                     drop_last=True, **common)
    lva = DataLoader(dva, batch_size=args.batch, shuffle=False, drop_last=False, **common)
    if len(ltr) == 0:
        print("[fatal] 0 train batches (drop_last=True and len(train) < batch)", file=sys.stderr)
        sys.exit(1)

    n_val_h = sum(1 for r in dva.items if is_strict_h(r))
    if n_val_h == 0:
        print("\n" + "!" * 78 + f"\n!! val carries ZERO tier-H frames -> the selection score falls "
              f"back to val cell-F1 alone.\n!! Checkpoint selection is then BLIND to H recall, "
              f"which is the headline metric.\n!! Fix: make_split.py --move-h-scene-to-val "
              f"(split v2).  split={args.split}\n" + "!" * 78 + "\n", file=sys.stderr)
    else:
        print(f"[sel] val strict-H frames: {n_val_h} -> sel_score = 0.5*val_f1 + 0.5*val_h_recall")

    # the kwarg is passed ONLY when aux is on: b2_polar's _FactoryProxy forwards **kw to
    # b2_model_factory.build, which has no use_mask_head (and phase 6 is RGB-U-Net-only).
    try:
        model = model_factory.build(args.input, classes=grid.n_cells,
                                    **({"use_mask_head": True} if aux_on else {})).to(device)
    except TypeError as e:
        if not aux_on:
            raise
        raise SystemExit(f"[fatal] --aux-mask-dir needs a factory that accepts use_mask_head; "
                         f"{getattr(model_factory, '__name__', model_factory)} refused it ({e}). "
                         f"Phase 6 is the RGB U-Net (code/model_factory.py) only.")
    if aux_on:
        print(f"[aux] pixel BCE ON  lambda={args.aux_lambda:g}  masks {dtr.n_aux_found} found / "
              f"{dtr.n_aux_missing} missing-as-empty of {len(dtr)} train frames  "
              f"dir={args.aux_mask_dir}")
    prior = dtr.positive_rate()
    bias_mod, bias_vals = (None, None)
    if args.bias_init == "prior":
        bias_mod, bias_vals = set_prior_bias(model, prior, grid.n_cells)
    crit = nn.BCEWithLogitsLoss()
    crit_aux = nn.BCEWithLogitsLoss()
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    if args.lr_schedule == "linear":
        sched = torch.optim.lr_scheduler.LambdaLR(
            opt, lambda e: max(0.0, 1.0 - e / max(args.max_epochs, 1)))
    else:
        sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda e: 1.0)

    cfg = dict(vars(args), device=device.type, n_train=len(dtr), n_val=len(dva),
               n_cells=grid.n_cells, grid_version=grid.version, grid_path=grid.path,
               cell_ids=grid.cell_ids, encoder="resnet34-unet-aux",
               params_m=round(sum(p.numel() for p in model.parameters()) / 1e6, 3),
               dropped_no_depth=dtr.n_dropped_no_depth + dva.n_dropped_no_depth,
               recipe="v2", hflip=hflip, oversampled=sampler is not None,
               train_positive_rate=[round(float(x), 6) for x in prior],
               bias_init_module=bias_mod, bias_init_values=bias_vals,
               n_val_strict_h=n_val_h, selection_metric=(
                   "val_f1 (FALLBACK: val has no H frame)" if n_val_h == 0
                   else "0.5*val_f1 + 0.5*val_h_frame_recall"))
    if aux_on:
        cfg.update(aux_enabled=True, aux_masks_found=dtr.n_aux_found,
                   aux_masks_missing_as_empty=dtr.n_aux_missing,
                   aux_loss="BCE(cell_logits,y) + aux_lambda*BCE(mask_logits,mask)",
                   aux_val_note="val/selection stay CELL-ONLY (comparability with the v2 runs)")
    else:                 # keep a non-aux config.json key-for-key identical to the v2 queue's
        cfg.pop("aux_mask_dir", None)
        cfg.pop("aux_lambda", None)
    with open(os.path.join(args.out, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"[cfg] {args.input} train={len(dtr)} val={len(dva)} batches/ep={len(ltr)} "
          f"cells={grid.n_cells} hflip={hflip} oversample={args.oversample_h:g} "
          f"bias={args.bias_init} dev={device.type}"
          + (f" aux={args.aux_lambda:g}" if aux_on else ""))

    mcsv = open(os.path.join(args.out, "metrics.csv"), "w", newline="")
    wr = csv.writer(mcsv)
    wr.writerow(["epoch", "train_loss", "val_loss", "val_f1", "val_recall", "val_fpr",
                 "lr", "sec", "val_h_recall", "sel_score"]
                + (["train_loss_cell", "train_loss_aux"] if aux_on else []))
    best, best_ep, bad, steps = -1.0, -1, 0, 0
    best_parts = dict(val_f1=float("nan"), val_h_recall=float("nan"))
    stop_reason = "max_epochs"

    for ep in range(1, args.max_epochs + 1):
        t0 = time.time()
        model.train()
        run, run_cell, run_aux, seen = 0.0, 0.0, 0.0, 0
        for batch in ltr:
            x, y, _m, mk = (batch if aux_on else (*batch, None))
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            if aux_on:
                logits, mask_logits = model(x)
                l_cell = crit(logits, y)
                l_aux = crit_aux(mask_logits, mk.to(device, non_blocking=True))
                loss = l_cell + args.aux_lambda * l_aux
                run_cell += float(l_cell) * x.size(0)
                run_aux += float(l_aux) * x.size(0)
            else:
                loss = crit(model(x), y)
            loss.backward()
            opt.step()
            run += float(loss) * x.size(0)
            seen += x.size(0)
            steps += 1
            if args.smoke and steps >= args.smoke:
                break
        tr_loss = run / max(seen, 1)
        tr_cell, tr_aux = run_cell / max(seen, 1), run_aux / max(seen, 1)
        va = evaluate(model, lva, device, crit, args.tau)
        sel, _fallback = selection_score(va["f1"], va["h_recall"])
        lr_now = opt.param_groups[0]["lr"]
        sched.step()
        sec = time.time() - t0
        ok_h = math.isfinite(va["h_recall"])
        hr_csv = f"{va['h_recall']:.6f}" if ok_h else "nan"
        hr_txt = f"{va['h_recall']:.4f}" if ok_h else " n/a  "
        wr.writerow([ep, f"{tr_loss:.6f}", f"{va['loss']:.6f}", f"{va['f1']:.6f}",
                     f"{va['recall']:.6f}", f"{va['fpr']:.6f}", f"{lr_now:.3e}", f"{sec:.2f}",
                     hr_csv, f"{sel:.6f}"]
                    + ([f"{tr_cell:.6f}", f"{tr_aux:.6f}"] if aux_on else []))
        mcsv.flush()
        print(f"ep {ep:3d} train_loss {tr_loss:.4f} "
              + (f"(cell {tr_cell:.4f} + {args.aux_lambda:g}*aux {tr_aux:.4f}) " if aux_on else "")
              + f"val_loss {va['loss']:.4f} "
              f"val_f1 {va['f1']:.4f} val_rec {va['recall']:.4f} val_fpr {va['fpr']:.4f} "
              f"val_h_rec {hr_txt} sel {sel:.4f} lr {lr_now:.2e} {sec:.1f}s")

        ck = dict(state_dict=model.state_dict(), config=cfg, epoch=ep, val_f1=va["f1"],
                  val_h_recall=va["h_recall"], sel_score=sel, grid_version=grid.version,
                  n_cells=grid.n_cells)
        torch.save(ck, os.path.join(args.out, "last.pt"))
        if sel > best:
            best, best_ep, bad = sel, ep, 0
            best_parts = dict(val_f1=va["f1"], val_h_recall=va["h_recall"])
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
    jnum = lambda v: (None if v is None or not math.isfinite(v) else float(v))  # noqa: E731
    cfg.update(best_sel_score=jnum(best), best_epoch=best_ep, stop_reason=stop_reason, steps=steps,
               best_val_f1=jnum(best_parts["val_f1"]),
               best_val_h_recall=jnum(best_parts["val_h_recall"]),   # null, not NaN: keep it jq-able
               selection_fallback_to_f1=bool(n_val_h == 0))
    with open(os.path.join(args.out, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)
    if not os.path.exists(os.path.join(args.out, "best.pt")):
        torch.save(dict(state_dict=model.state_dict(), config=cfg, epoch=0, sel_score=best,
                        grid_version=grid.version, n_cells=grid.n_cells),
                   os.path.join(args.out, "best.pt"))
    print(f"[done] {stop_reason} best_sel={best:.4f} (val_f1={best_parts['val_f1']:.4f} "
          f"val_h_recall={best_parts['val_h_recall']:.4f}) @ep{best_ep} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
