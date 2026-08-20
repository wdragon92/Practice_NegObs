"""Evaluate the polar hazard-grid head -> per_frame.csv + metrics.json + METRICS_SECTION.md.

Paper table = stratified recall by evidence tier (V/E/H) + false-alarm rate on hazard-off frames,
with percentile-bootstrap CIs (bootstrap.py) and an optional paired --compare against a second arm.
tau_star is ALWAYS fitted on the val subset, never on test.

RECIPE v2 additions (0820, brief Phase 4/7):
  * --grid: every band loop is driven by the gridspec (3 bands on V0, 4 on V1). Default v0.
  * frame_det_rate: fraction of hazard frames (any tier) where SOME GT-positive cell fires —
    the V0<->V1 continuity metric, since it does not depend on how the range axis is cut.
  * per-band false alarms (band<i>_cell_fpr_off) next to the per-band recalls.
  * the per_frame.csv header is now the authority on cell ids: read_per_frame infers them, so an
    old 15-cell CSV still parses under a 20-cell default and a mismatch fails loudly.
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
import gridspec  # noqa: E402
import model_factory  # noqa: E402
from polar_dataset import IMG_SIZE, PolarGridDataset  # noqa: E402
from train_polar import guard_gpu_free  # noqa: E402

TIERS = ["V", "E", "H"]


def headline_keys(grid):
    return (["cell_f1", "cell_recall", "cell_precision", "frame_det_rate"]
            + [f"frame_recall_{t}" for t in TIERS] + [f"cell_recall_{t}" for t in TIERS]
            + [f"band{b + 1}_cell_recall" for b in range(grid.n_bands)]
            + [f"band{b + 1}_cell_fpr_off" for b in range(grid.n_bands)]
            + ["frame_fa_off", "cell_fpr_off", "cell_fpr_on_neg"])


# ------------------------------------------------------------------ inference / io
@torch.no_grad()
def infer(ckpt_path, manifest, split, subset, input_mode, img_size, batch, workers, device,
          grid=None):
    grid = gridspec.load(grid)
    ds = PolarGridDataset(manifest, split, subset, input_mode, train_aug=False, img_size=img_size,
                          grid=grid)
    dl = DataLoader(ds, batch_size=batch, shuffle=False, num_workers=workers,
                    pin_memory=(device.type == "cuda"))
    model = model_factory.build(input_mode, encoder_weights=None, classes=grid.n_cells).to(device)
    # map_location="cpu" is mandatory (a GPU-side RNG ByteTensor broke resume in the campaign)
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    if isinstance(ck, dict) and ck.get("n_cells") not in (None, grid.n_cells):
        raise SystemExit(f"[fatal] checkpoint was trained on {ck['n_cells']} cells "
                         f"({ck.get('grid_version')}) but --grid says {grid.n_cells} "
                         f"({grid.version}) -- wrong --grid or wrong --ckpt")
    model.load_state_dict(ck["state_dict"] if "state_dict" in ck else ck)
    model.eval()
    fid, sid, tier, tog, P, G = [], [], [], [], [], []
    for x, y, m in dl:
        P.append(torch.sigmoid(model(x.to(device))).cpu().numpy())
        G.append(y.numpy())
        fid += list(m["frame_id"]); sid += list(m["scene_id"])
        tier += list(m["tier"]); tog += list(m["toggle_state"])
    return dict(frame_id=fid, scene_id=sid, tier=np.array(tier), toggle=np.array(tog),
                probs=np.concatenate(P).astype(np.float64), gt=np.concatenate(G).astype(np.float64),
                cell_ids=list(grid.cell_ids))


def write_per_frame(d, path, grid=None):
    cells = d.get("cell_ids") or gridspec.load(grid).cell_ids
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frame_id", "scene_id", "tier", "toggle_state"]
                   + [f"p_{c}" for c in cells] + [f"g_{c}" for c in cells])
        for i in range(len(d["frame_id"])):
            w.writerow([d["frame_id"][i], d["scene_id"][i], d["tier"][i], d["toggle"][i]]
                       + [f"{v:.6f}" for v in d["probs"][i]]
                       + [int(v) for v in d["gt"][i]])


def read_per_frame(path, grid=None):
    """Cell ids come from the CSV header (the file is self-describing). If a grid is given the
    two must agree -- a silent 15-vs-20 mix-up would produce a plausible, wrong table."""
    fid, sid, tier, tog, P, G = [], [], [], [], [], []
    with open(path) as f:
        rd = csv.DictReader(f)
        cells = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        if not cells:
            raise ValueError(f"{path}: no p_<cell> columns")
        if grid is not None:
            g = gridspec.load(grid)
            if list(g.cell_ids) != cells:
                raise SystemExit(f"[fatal] {os.path.basename(path)} carries {len(cells)} cells "
                                 f"{cells[:3]}...{cells[-1]} but --grid {g.version} expects "
                                 f"{g.n_cells} {g.cell_ids[:3]}...{g.cell_ids[-1]}")
        for r in rd:
            fid.append(r["frame_id"]); sid.append(r["scene_id"])
            tier.append(r["tier"]); tog.append(r["toggle_state"])
            P.append([float(r[f"p_{c}"]) for c in cells])
            G.append([float(r[f"g_{c}"]) for c in cells])
    return dict(frame_id=fid, scene_id=sid, tier=np.array(tier), toggle=np.array(tog),
                probs=np.asarray(P, float), gt=np.asarray(G, float), cell_ids=cells)


# ------------------------------------------------------------------ metrics
def _ratio(a, b):
    return float(a) / float(b) if b > 0 else float("nan")


def bundle(d, tau, idx=None, grid=None):
    """All headline metrics on the frames selected by idx (default: all)."""
    g = gridspec.load(grid)
    band_arr = np.asarray(g.band_of)
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
    # V0<->V1 continuity metric: independent of how the range axis is cut into bands
    out["frame_det_rate"] = _ratio(detected[haz].sum(), haz.sum())
    for t in TIERS:
        s = haz & (tier == t)
        out[f"frame_recall_{t}"] = _ratio(detected[s].sum(), s.sum())
        out[f"cell_recall_{t}"] = _ratio((pred[s] & pos[s]).sum(), pos[s].sum())
    for b in range(g.n_bands):
        m = band_arr == b
        ph, gh = pred[haz][:, m], pos[haz][:, m]
        out[f"band{b + 1}_cell_recall"] = _ratio((ph & gh).sum(), gh.sum())
        po, go = pred[off][:, m], pos[off][:, m]
        out[f"band{b + 1}_cell_fpr_off"] = _ratio((po & ~go).sum(), (~go).sum())

    out["frame_fa_off"] = _ratio(pred[off].any(1).sum(), off.sum())
    out["cell_fpr_off"] = _ratio((pred[off] & ~pos[off]).sum(), (~pos[off]).sum())
    out["cell_fpr_on_neg"] = _ratio((pred[on] & ~pos[on]).sum(), (~pos[on]).sum())
    return out


def counts(d):
    t, g = d["tier"], d["gt"] > 0.5
    on, off = d["toggle"] == "on", d["toggle"] == "off"
    c = dict(n_frames=len(t), n_on=int(on.sum()), n_off=int(off.sum()),
             n_hazard_frames=int((on & g.any(1)).sum()),
             n_scenes=len(set(d["scene_id"])), n_pos_cells=int(g.sum()),
             n_cells=int(d["gt"].shape[1]))
    for k in TIERS:
        c[f"n_{k}"] = int(((t == k) & on & g.any(1)).sum())
    return c


def fit_tau_star(d, grid=None, tgrid=None):
    tgrid = np.arange(0.05, 0.96, 0.01) if tgrid is None else np.asarray(tgrid)
    f1 = [bundle(d, float(t), grid=grid)["cell_f1"] for t in tgrid]
    f1 = np.nan_to_num(np.asarray(f1), nan=-1.0)
    return float(tgrid[int(np.argmax(f1))]), float(f1.max())


# ------------------------------------------------------------------ report
def _fmt(v, nd=4):
    return "n/a" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.{nd}f}"


def _ci_row(name, ci):
    c = ci.get(name)
    return f"{_fmt(c['point'])} [{_fmt(c['lo'])}, {_fmt(c['hi'])}]" if c else "n/a"


def write_markdown(path, M, grid):
    L = ["# METRICS_SECTION — polar hazard grid", "",
         f"arm: **{M['input_mode']}** · subset: **{M['subset']}** · ckpt: `{M['ckpt']}`",
         f"grid: **{grid.version}** ({grid.n_bands} bands x {grid.n_sectors} sectors = "
         f"{grid.n_cells} cells, edges {grid.band_edges_m} m)",
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
        L += [f"| **any tier (frame detection rate)** | {_ci_row('frame_det_rate', ci)} | — | "
              f"{c['n_hazard_frames']} |", "",
              "> frame detection rate = fraction of hazard frames where ANY GT-positive cell "
              "fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change "
              "it, so V0 and V1 numbers are directly comparable on this row.", "",
              "| false alarms | value [95% CI] |", "|---|---|",
              f"| frame-FA rate (off frames) | {_ci_row('frame_fa_off', ci)} |",
              f"| cell FPR (off frames) | {_ci_row('cell_fpr_off', ci)} |",
              f"| cell FPR (negative cells of on frames) | {_ci_row('cell_fpr_on_neg', ci)} |", "",
              "| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |",
              "|---|---|---|"]
        for b in range(grid.n_bands):
            lo, hi = grid.band_range(b)
            L.append(f"| {grid.band_names[b]} [{lo:g},{hi:g}) m | "
                     f"{_ci_row(f'band{b + 1}_cell_recall', ci)} | "
                     f"{_ci_row(f'band{b + 1}_cell_fpr_off', ci)} |")
        L += ["", "| overall | value [95% CI] |", "|---|---|",
              f"| cell F1 | {_ci_row('cell_f1', ci)} |",
              f"| cell recall | {_ci_row('cell_recall', ci)} |",
              f"| cell precision | {_ci_row('cell_precision', ci)} |", ""]

    taus = sorted(M["sweep"], key=float)
    keys = headline_keys(grid)
    L += ["## 2. Threshold sweep", "",
          "| metric | " + " | ".join(f"tau={t}" for t in taus) + " |", "|" + "---|" * (len(taus) + 1)]
    for k in keys:
        L.append(f"| {k} | " + " | ".join(_fmt(M["sweep"][t][k]) for t in taus) + " |")
    L.append("")

    if M.get("compare"):
        cm = M["compare"]
        L += [f"## 3. Paired comparison (A = this arm, B = `{cm['b_csv']}`)", "",
              f"{cm['n_common']} common frames · paired percentile bootstrap "
              f"{M['n_boot']}x seed {M['seed']} · threshold {cm['tau']}", "",
              "| metric | A | B | A−B [95% CI] | CI excludes 0 |", "|---|---|---|---|---|"]
        for k in keys:
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
    gridspec.add_grid_arg(p)
    a = p.parse_args(argv)
    grid = gridspec.from_args(a)
    os.makedirs(a.out, exist_ok=True)
    dev = torch.device(guard_gpu_free())
    if dev.type == "cuda" and not torch.cuda.is_available():
        dev = torch.device("cpu")
    print(f"[grid] {grid.summary()}")

    if a.per_frame_a:
        d = read_per_frame(a.per_frame_a, grid)
    else:
        if not (a.ckpt and a.manifest and a.split):
            p.error("--ckpt, --manifest and --split are required unless --per-frame-a is given")
        d = infer(a.ckpt, a.manifest, a.split, a.subset, a.input, a.img_size, a.batch, a.workers,
                  dev, grid)
    pf = os.path.join(a.out, "per_frame.csv")
    write_per_frame(d, pf, grid)

    tau_star_f1 = None
    if str(a.tau_star).lower() == "auto":
        if a.ckpt and a.manifest and a.split:
            dv = infer(a.ckpt, a.manifest, a.split, "val", a.input, a.img_size, a.batch,
                       a.workers, dev, grid)
            tau_star, tau_star_f1 = fit_tau_star(dv, grid)
            write_per_frame(dv, os.path.join(a.out, "per_frame_val.csv"), grid)
        else:
            tau_star = a.tau_op
            print("[warn] --tau-star auto needs --ckpt (val fit); falling back to tau_op")
    else:
        tau_star = float(a.tau_star)

    n = len(d["frame_id"])
    M = dict(input_mode=a.input, subset=a.subset, ckpt=a.ckpt or a.per_frame_a, tau_op=a.tau_op,
             tau_star=round(float(tau_star), 4), tau_star_val_f1=tau_star_f1,
             n_boot=a.n_boot, seed=a.seed, counts=counts(d), per_frame_csv=pf,
             grid=grid.as_dict(),
             point=dict(op=bundle(d, a.tau_op, grid=grid), star=bundle(d, tau_star, grid=grid)),
             ci=dict(op=BS.bootstrap_ci(lambda i: bundle(d, a.tau_op, i, grid), n, a.n_boot, a.seed),
                     star=BS.bootstrap_ci(lambda i: bundle(d, tau_star, i, grid), n, a.n_boot,
                                          a.seed)),
             sweep={t: bundle(d, float(t), grid=grid) for t in a.tau_sweep.split(",")})

    if a.compare:
        b = read_per_frame(a.compare, grid)
        bi = {f: i for i, f in enumerate(b["frame_id"])}
        pairs = [(i, bi[f]) for i, f in enumerate(d["frame_id"]) if f in bi]
        if not pairs:
            print("[warn] --compare: no common frame_id, skipping")
        else:
            ia, ib = np.array([x[0] for x in pairs]), np.array([x[1] for x in pairs])
            fa = lambda k: bundle(d, a.tau_op, ia[k], grid)   # noqa: E731  shared resample index k
            fb = lambda k: bundle(b, a.tau_op, ib[k], grid)   # noqa: E731
            M["compare"] = dict(b_csv=a.compare, n_common=len(pairs), tau=a.tau_op,
                                diff=BS.paired_diff_ci(fa, fb, len(pairs), a.n_boot, a.seed))

    with open(os.path.join(a.out, "metrics.json"), "w") as f:
        json.dump(M, f, indent=2)
    write_markdown(os.path.join(a.out, "METRICS_SECTION.md"), M, grid)
    o = M["point"]["op"]
    print(f"[eval] n={n} cells={grid.n_cells} tau_op={a.tau_op} tau*={M['tau_star']} | "
          f"cell_f1={_fmt(o['cell_f1'])} det={_fmt(o['frame_det_rate'],3)} "
          f"recall V/E/H={_fmt(o['frame_recall_V'],3)}/{_fmt(o['frame_recall_E'],3)}/"
          f"{_fmt(o['frame_recall_H'],3)} frame_FA_off={_fmt(o['frame_fa_off'],3)} -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
