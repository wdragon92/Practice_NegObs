"""Evaluate the polar hazard-grid head -> per_frame.csv + metrics.json + METRICS_SECTION.md.

Paper table = stratified recall by evidence tier (V/E/H) + false-alarm rate on hazard-off frames,
with percentile-bootstrap CIs (bootstrap.py) and an optional paired --compare against a second arm.
tau_star is ALWAYS fitted on the val subset, never on test.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

import numpy as np
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bootstrap as BS  # noqa: E402
import model_factory  # noqa: E402
from polar_dataset import BAND_OF, CELL_IDS, IMG_SIZE, N_CELLS, PolarGridDataset  # noqa: E402
from train_polar import guard_gpu_free  # noqa: E402

TIERS = ["V", "E", "H"]
BAND_ARR = np.asarray(BAND_OF)
HEADLINE = (["cell_f1", "cell_recall", "cell_precision"]
            + [f"frame_recall_{t}" for t in TIERS] + [f"cell_recall_{t}" for t in TIERS]
            + [f"band{b}_cell_recall" for b in (1, 2, 3)]
            + ["frame_fa_off", "cell_fpr_off", "cell_fpr_on_neg"])


# ------------------------------------------------------------------ inference / io
@torch.no_grad()
def infer(ckpt_path, manifest, split, subset, input_mode, img_size, batch, workers, device):
    ds = PolarGridDataset(manifest, split, subset, input_mode, train_aug=False, img_size=img_size)
    dl = DataLoader(ds, batch_size=batch, shuffle=False, num_workers=workers,
                    pin_memory=(device.type == "cuda"))
    model = model_factory.build(input_mode, encoder_weights=None).to(device)
    # map_location="cpu" is mandatory (a GPU-side RNG ByteTensor broke resume in the campaign)
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model.load_state_dict(ck["state_dict"] if "state_dict" in ck else ck)
    model.eval()
    fid, sid, tier, tog, P, G = [], [], [], [], [], []
    for x, y, m in dl:
        P.append(torch.sigmoid(model(x.to(device))).cpu().numpy())
        G.append(y.numpy())
        fid += list(m["frame_id"]); sid += list(m["scene_id"])
        tier += list(m["tier"]); tog += list(m["toggle_state"])
    return dict(frame_id=fid, scene_id=sid, tier=np.array(tier), toggle=np.array(tog),
                probs=np.concatenate(P).astype(np.float64), gt=np.concatenate(G).astype(np.float64))


def write_per_frame(d, path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frame_id", "scene_id", "tier", "toggle_state"]
                   + [f"p_{c}" for c in CELL_IDS] + [f"g_{c}" for c in CELL_IDS])
        for i in range(len(d["frame_id"])):
            w.writerow([d["frame_id"][i], d["scene_id"][i], d["tier"][i], d["toggle"][i]]
                       + [f"{v:.6f}" for v in d["probs"][i]]
                       + [int(v) for v in d["gt"][i]])


def read_per_frame(path):
    fid, sid, tier, tog, P, G = [], [], [], [], [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            fid.append(r["frame_id"]); sid.append(r["scene_id"])
            tier.append(r["tier"]); tog.append(r["toggle_state"])
            P.append([float(r[f"p_{c}"]) for c in CELL_IDS])
            G.append([float(r[f"g_{c}"]) for c in CELL_IDS])
    return dict(frame_id=fid, scene_id=sid, tier=np.array(tier), toggle=np.array(tog),
                probs=np.asarray(P, float), gt=np.asarray(G, float))


# ------------------------------------------------------------------ metrics
def _ratio(a, b):
    return float(a) / float(b) if b > 0 else float("nan")


def bundle(d, tau, idx=None):
    """All headline metrics on the frames selected by idx (default: all)."""
    idx = np.arange(len(d["frame_id"])) if idx is None else np.asarray(idx)
    prob, gt = d["probs"][idx], d["gt"][idx]
    tier, tog = d["tier"][idx], d["toggle"][idx]
    pred, pos = prob >= tau, gt > 0.5
    on, off = tog == "on", tog == "off"
    haz = on & pos.any(1)                      # hazard-on frames carrying >=1 GT-positive cell
    out = {}

    tp = float((pred & pos).sum()); fp = float((pred & ~pos).sum())
    fn = float((~pred & pos).sum())
    out["cell_f1"] = _ratio(2 * tp, 2 * tp + fp + fn)
    out["cell_recall"] = _ratio(tp, tp + fn)
    out["cell_precision"] = _ratio(tp, tp + fp)

    detected = (pred & pos).any(1)             # frame counts as detected if ANY GT-positive cell fires
    for t in TIERS:
        s = haz & (tier == t)
        out[f"frame_recall_{t}"] = _ratio(detected[s].sum(), s.sum())
        out[f"cell_recall_{t}"] = _ratio((pred[s] & pos[s]).sum(), pos[s].sum())
    for b in (1, 2, 3):
        m = BAND_ARR == (b - 1)
        ph, gh = pred[haz][:, m], pos[haz][:, m]
        out[f"band{b}_cell_recall"] = _ratio((ph & gh).sum(), gh.sum())

    out["frame_fa_off"] = _ratio(pred[off].any(1).sum(), off.sum())
    out["cell_fpr_off"] = _ratio((pred[off] & ~pos[off]).sum(), (~pos[off]).sum())
    out["cell_fpr_on_neg"] = _ratio((pred[on] & ~pos[on]).sum(), (~pos[on]).sum())
    return out


def counts(d):
    t, g = d["tier"], d["gt"] > 0.5
    on, off = d["toggle"] == "on", d["toggle"] == "off"
    c = dict(n_frames=len(t), n_on=int(on.sum()), n_off=int(off.sum()),
             n_hazard_frames=int((on & g.any(1)).sum()),
             n_scenes=len(set(d["scene_id"])), n_pos_cells=int(g.sum()))
    for k in TIERS:
        c[f"n_{k}"] = int(((t == k) & on & g.any(1)).sum())
    return c


def fit_tau_star(d, grid=None):
    grid = np.arange(0.05, 0.96, 0.01) if grid is None else np.asarray(grid)
    f1 = [bundle(d, float(t))["cell_f1"] for t in grid]
    f1 = np.nan_to_num(np.asarray(f1), nan=-1.0)
    return float(grid[int(np.argmax(f1))]), float(f1.max())


# ------------------------------------------------------------------ report
def _fmt(v, nd=4):
    return "n/a" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.{nd}f}"


def _ci_row(name, ci):
    c = ci.get(name)
    return f"{_fmt(c['point'])} [{_fmt(c['lo'])}, {_fmt(c['hi'])}]" if c else "n/a"


def write_markdown(path, M):
    L = ["# METRICS_SECTION — polar hazard grid", "",
         f"arm: **{M['input_mode']}** · subset: **{M['subset']}** · ckpt: `{M['ckpt']}`",
         f"tau_op = {M['tau_op']} · tau_star = {M['tau_star']} (fitted on **val**, "
         f"val cell-F1 {_fmt(M.get('tau_star_val_f1'))}) · bootstrap {M['n_boot']}x seed {M['seed']}", ""]
    c = M["counts"]
    L += ["## 0. Subset composition", "",
          "| frames | on | off | hazard-on | V | E | H | scenes | pos cells |", "|" + "---|" * 9,
          f"| {c['n_frames']} | {c['n_on']} | {c['n_off']} | {c['n_hazard_frames']} | "
          f"{c['n_V']} | {c['n_E']} | {c['n_H']} | {c['n_scenes']} | {c['n_pos_cells']} |", ""]

    for lbl, key in (("tau_op = %s" % M["tau_op"], "op"), ("tau_star = %s" % M["tau_star"], "star")):
        ci = M["ci"][key]
        L += [f"## 1{'ab'[key=='star']}. Stratified recall by evidence tier @ {lbl}", "",
              "| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |", "|---|---|---|---|"]
        for t in TIERS:
            L.append(f"| {t} | {_ci_row(f'frame_recall_{t}', ci)} | "
                     f"{_ci_row(f'cell_recall_{t}', ci)} | {c['n_' + t]} |")
        L += ["", "| false alarms | value [95% CI] |", "|---|---|",
              f"| frame-FA rate (off frames) | {_ci_row('frame_fa_off', ci)} |",
              f"| cell FPR (off frames) | {_ci_row('cell_fpr_off', ci)} |",
              f"| cell FPR (negative cells of on frames) | {_ci_row('cell_fpr_on_neg', ci)} |", "",
              "| distance band | cell recall [95% CI] |", "|---|---|",
              f"| 1 near | {_ci_row('band1_cell_recall', ci)} |",
              f"| 2 mid | {_ci_row('band2_cell_recall', ci)} |",
              f"| 3 far | {_ci_row('band3_cell_recall', ci)} |", "",
              "| overall | value [95% CI] |", "|---|---|",
              f"| cell F1 | {_ci_row('cell_f1', ci)} |",
              f"| cell recall | {_ci_row('cell_recall', ci)} |",
              f"| cell precision | {_ci_row('cell_precision', ci)} |", ""]

    taus = sorted(M["sweep"], key=float)
    L += ["## 2. Threshold sweep", "",
          "| metric | " + " | ".join(f"tau={t}" for t in taus) + " |", "|" + "---|" * (len(taus) + 1)]
    for k in HEADLINE:
        L.append(f"| {k} | " + " | ".join(_fmt(M["sweep"][t][k]) for t in taus) + " |")
    L.append("")

    if M.get("compare"):
        cm = M["compare"]
        L += [f"## 3. Paired comparison (A = this arm, B = `{cm['b_csv']}`)", "",
              f"{cm['n_common']} common frames · paired percentile bootstrap "
              f"{M['n_boot']}x seed {M['seed']} · threshold {cm['tau']}", "",
              "| metric | A | B | A−B [95% CI] | CI excludes 0 |", "|---|---|---|---|---|"]
        for k in HEADLINE:
            r = cm["diff"].get(k)
            if r:
                L.append(f"| {k} | {_fmt(r['a'])} | {_fmt(r['b'])} | "
                         f"{_fmt(r['diff'])} [{_fmt(r['lo'])}, {_fmt(r['hi'])}] | "
                         f"{'yes' if r['excludes_zero'] else 'no'} |")
        L.append("")
    with open(path, "w") as f:
        f.write("\n".join(L))


# ------------------------------------------------------------------ main
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", default=None, help="required unless --per-frame-a is given")
    p.add_argument("--split", default=None, help="required unless --per-frame-a is given")
    p.add_argument("--subset", default="test")
    p.add_argument("--ckpt", default=None, help="omit only if --per-frame-a is given")
    p.add_argument("--input", choices=["rgb", "depth"], default="rgb")
    p.add_argument("--out", required=True)
    p.add_argument("--tau-op", type=float, default=0.5)
    p.add_argument("--tau-star", default="auto", help="'auto' (fit on val) or a float")
    p.add_argument("--tau-sweep", default="0.3,0.5,0.7")
    p.add_argument("--compare", default=None, help="second per_frame.csv (e.g. the depth arm)")
    p.add_argument("--per-frame-a", default=None, help="reuse an existing per_frame.csv, skip inference")
    p.add_argument("--n-boot", type=int, default=BS.N_BOOT)
    p.add_argument("--seed", type=int, default=BS.SEED)
    p.add_argument("--batch", type=int, default=8)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--img-size", type=int, default=IMG_SIZE, help=argparse.SUPPRESS)
    a = p.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    dev = torch.device(guard_gpu_free())
    if dev.type == "cuda" and not torch.cuda.is_available():
        dev = torch.device("cpu")

    if a.per_frame_a:
        d = read_per_frame(a.per_frame_a)
    else:
        if not (a.ckpt and a.manifest and a.split):
            p.error("--ckpt, --manifest and --split are required unless --per-frame-a is given")
        d = infer(a.ckpt, a.manifest, a.split, a.subset, a.input, a.img_size, a.batch, a.workers, dev)
    pf = os.path.join(a.out, "per_frame.csv")
    write_per_frame(d, pf)

    tau_star_f1 = None
    if str(a.tau_star).lower() == "auto":
        if a.ckpt and a.manifest and a.split:
            dv = infer(a.ckpt, a.manifest, a.split, "val", a.input, a.img_size, a.batch, a.workers, dev)
            tau_star, tau_star_f1 = fit_tau_star(dv)
            write_per_frame(dv, os.path.join(a.out, "per_frame_val.csv"))
        else:
            tau_star = a.tau_op
            print("[warn] --tau-star auto needs --ckpt (val fit); falling back to tau_op")
    else:
        tau_star = float(a.tau_star)

    n = len(d["frame_id"])
    M = dict(input_mode=a.input, subset=a.subset, ckpt=a.ckpt or a.per_frame_a, tau_op=a.tau_op,
             tau_star=round(float(tau_star), 4), tau_star_val_f1=tau_star_f1,
             n_boot=a.n_boot, seed=a.seed, counts=counts(d), per_frame_csv=pf,
             point=dict(op=bundle(d, a.tau_op), star=bundle(d, tau_star)),
             ci=dict(op=BS.bootstrap_ci(lambda i: bundle(d, a.tau_op, i), n, a.n_boot, a.seed),
                     star=BS.bootstrap_ci(lambda i: bundle(d, tau_star, i), n, a.n_boot, a.seed)),
             sweep={t: bundle(d, float(t)) for t in a.tau_sweep.split(",")})

    if a.compare:
        b = read_per_frame(a.compare)
        bi = {f: i for i, f in enumerate(b["frame_id"])}
        pairs = [(i, bi[f]) for i, f in enumerate(d["frame_id"]) if f in bi]
        if not pairs:
            print("[warn] --compare: no common frame_id, skipping")
        else:
            ia, ib = np.array([x[0] for x in pairs]), np.array([x[1] for x in pairs])
            fa = lambda k: bundle(d, a.tau_op, ia[k])   # noqa: E731  shared resample index k
            fb = lambda k: bundle(b, a.tau_op, ib[k])   # noqa: E731
            M["compare"] = dict(b_csv=a.compare, n_common=len(pairs), tau=a.tau_op,
                                diff=BS.paired_diff_ci(fa, fb, len(pairs), a.n_boot, a.seed))

    with open(os.path.join(a.out, "metrics.json"), "w") as f:
        json.dump(M, f, indent=2)
    write_markdown(os.path.join(a.out, "METRICS_SECTION.md"), M)
    o = M["point"]["op"]
    print(f"[eval] n={n} tau_op={a.tau_op} tau*={M['tau_star']} | cell_f1={_fmt(o['cell_f1'])} "
          f"recall V/E/H={_fmt(o['frame_recall_V'],3)}/{_fmt(o['frame_recall_E'],3)}/"
          f"{_fmt(o['frame_recall_H'],3)} frame_FA_off={_fmt(o['frame_fa_off'],3)} -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
