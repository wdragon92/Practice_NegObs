"""V2S ADOPTION CHECK — folding channel, D34 pre-registered inequalities, native benefit.

READ-ONLY over frozen V1 (`experiments/dayrun_0820/runs/v2/*`) and V2S
(`experiments/weekend_0823/v2s/runs/*`) dumps.  Writes only under
`experiments/weekend_0823/v2s/` (V2S_ADOPTION.md, v2s_adoption.json, adoption_package/).

FOLDING LAW (gridspec_v2s.json): V1_cell(b*5+s) == V2S_cell(b*10+2s) OR V2S_cell(b*10+2s+1).
  p_fold[b*5+s] = max(p[b*10+2s], p[b*10+2s+1])        (sector-pair MAX)
  g_fold[b*5+s] = g[b*10+2s] OR g[b*10+2s+1]           (sector-pair OR)
The GT fold is a HARD SANITY GATE: it must equal the V1 per_frame GT byte-for-byte,
frame by frame, cell by cell, on every one of the 9 runs.  Any mismatch aborts.

D34 judgement runs on the FOLDED channel: d = V2S_fold - V1, per metric per model,
requires  mean_s d >= -0.05  AND  min_s d >= -0.10  AND  paired-bootstrap CI_lo >= -0.05.

Run with PYTHONNOUSERSITE=1 (this machine's ~/.local shadows env_seg).  CPU only.
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
V1_BASE = os.path.join(REPO, "experiments/dayrun_0820/runs/v2")
V2S_BASE = os.path.join(REPO, "experiments/weekend_0823/v2s/runs")
OUT_DIR = os.path.join(REPO, "experiments/weekend_0823/v2s")
GRID_V1 = os.path.join(REPO, "experiments/mainrun_0819/code/labeling/gridspec_v1.json")
GRID_V2S = os.path.join(REPO, "experiments/mainrun_0819/code/labeling/gridspec_v2s.json")

MODELS = ("rgb", "depth", "b2")
SEEDS = (42, 43, 44)
TAU = 0.5
N_BOOT = 10000
BOOT_SEED = 42
NAN = float("nan")

g1 = json.load(open(GRID_V1))
g2 = json.load(open(GRID_V2S))
NS1, NS2, NB = g1["n_sectors"], g2["n_sectors"], g1["n_bands"]
assert g1["band_edges_m"] == g2["band_edges_m"] and g1["band_names"] == g2["band_names"]
CELLS1 = [g1["sector_names"][i % NS1] + g1["band_names"][i // NS1] for i in range(NS1 * NB)]
CELLS2 = [g2["sector_names"][i % NS2] + g2["band_names"][i // NS2] for i in range(NS2 * NB)]
BAND1 = np.array([i // NS1 for i in range(NS1 * NB)])
BAND2 = np.array([i // NS2 for i in range(NS2 * NB)])
SEC1 = np.array([i % NS1 for i in range(NS1 * NB)])
SEC2 = np.array([i % NS2 for i in range(NS2 * NB)])
# sector centres in degrees (edges are DESCENDING azimuth)
CTR1 = np.array([(g1["sector_edges_deg"][i] + g1["sector_edges_deg"][i + 1]) / 2 for i in range(NS1)])
CTR2 = np.array([(g2["sector_edges_deg"][i] + g2["sector_edges_deg"][i + 1]) / 2 for i in range(NS2)])
W1 = abs(CTR1[0] - CTR1[1])     # 12.44 deg
W2 = abs(CTR2[0] - CTR2[1])     # 6.22 deg
# fold index: for folded cell f = b*5+s, the two native columns
FOLD_IDX = np.array([[b * NS2 + 2 * s, b * NS2 + 2 * s + 1]
                     for b in range(NB) for s in range(NS1)])


# --------------------------------------------------------------------------- io
def load_pf(path, cells):
    fid, sid, tier, tog, P, G = [], [], [], [], [], []
    with open(path) as f:
        rd = csv.DictReader(f)
        got = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        if got != cells:
            raise SystemExit(f"[fatal] {path}: cell columns {got[:3]}..{got[-1]} != expected "
                             f"{cells[:3]}..{cells[-1]}")
        for r in rd:
            fid.append(r["frame_id"]); sid.append(r["scene_id"])
            tier.append(r["tier"]); tog.append(r["toggle_state"])
            P.append([float(r["p_" + c]) for c in cells])
            G.append([float(r["g_" + c]) for c in cells])
    return dict(frame_id=fid, scene_id=np.array(sid), tier=np.array(tier), toggle=np.array(tog),
                probs=np.asarray(P, float), gt=np.asarray(G, float) > 0.5)


def fold(d):
    """40-cell dump -> 20-cell folded channel (probs by sector-pair MAX, gt by OR)."""
    p, g = d["probs"], d["gt"]
    return dict(d, probs=p[:, FOLD_IDX].max(axis=2), gt=g[:, FOLD_IDX].any(axis=2),
                native_probs=p, native_gt=g)


def load_twin_pairs(base, run):
    path = os.path.join(base, run, "twin", "twin_pairs.csv")
    return list(csv.DictReader(open(path)))


# ---------------------------------------------------------------- metric kernel
def frame_recall_H(d, idxH, tau=TAU):
    """(pred & gt).any over the given H-frame row indices."""
    p, g = d["probs"][idxH], d["gt"][idxH]
    return float(((p >= tau) & g).any(1).mean()) if len(idxH) else NAN


def frame_fa_off(d, idxOff, tau=TAU):
    return float((d["probs"][idxOff] >= tau).any(1).mean()) if len(idxOff) else NAN


def twin_deltas(d, pairs, row_of):
    """delta_score per kept pair, on this dump's channel.  NaN where the ON frame has no GT cell.

    delta_score = max(p_on over ON-frame GT-positive cells) - max(p_off over the SAME cells)
    (identical definition to code/twin_analysis.py, evaluated on the folded channel)."""
    out = []
    for pr in pairs:
        ion = row_of.get(("on", pr["scene_id"], pr["cut"]))
        ioff = row_of.get(("off", pr["scene_id"], pr["cut"]))
        if ion is None or ioff is None:
            out.append(NAN); continue
        pos = d["gt"][ion]
        if not pos.any():
            out.append(NAN); continue
        out.append(float(d["probs"][ion][pos].max()) - float(d["probs"][ioff][pos].max()))
    return np.asarray(out, float)


def nanmean(v):
    v = np.asarray(v, float)
    return float(np.nanmean(v)) if np.isfinite(v).any() else NAN


# ------------------------------------------------------------- native benefit
def loc_error_deg(probs, gt, on_rows, band_of, sec_of, centres):
    """Sector-localisation error, degrees, per ON-frame carrying GT.

    Within the GT BAND ROWS (bands that hold >=1 GT cell) take the argmax-prob cell;
    the error is the angular distance from that cell's sector centre to the nearest
    GT-positive sector centre (GT-positive cells restricted to the same band rows)."""
    errs = []
    for i in on_rows:
        g = gt[i]
        if not g.any():
            continue
        bands = np.unique(band_of[g])
        m = np.isin(band_of, bands)
        j = int(np.argmax(np.where(m, probs[i], -np.inf)))
        s_hat = centres[sec_of[j]]
        s_gt = centres[sec_of[g & m]]
        errs.append(float(np.abs(s_gt - s_hat).min()))
    return np.asarray(errs, float)


def corridor_ff(probs, gt, on_rows, band_of, sec_of, step, tau=TAU):
    """Adjacent-empty-sector false-fire rate.

    Over ON frames carrying GT: cells that are GT-NEGATIVE and sit exactly `step`
    sector indices away (same band) from a GT-positive cell.  Rate = fraction firing."""
    num = den = 0
    for i in on_rows:
        g = gt[i]
        if not g.any():
            continue
        adj = np.zeros(len(g), bool)
        for k in np.flatnonzero(g):
            for dlt in (-step, step):
                s2 = sec_of[k] + dlt
                if 0 <= s2 < sec_of.max() + 1:
                    hit = (band_of == band_of[k]) & (sec_of == s2)
                    adj |= hit
        adj &= ~g
        den += int(adj.sum())
        num += int(((probs[i] >= tau) & adj).sum())
    return (num / den if den else NAN), den


# -------------------------------------------------------------- FA-matched lens
def tau_for_fa_exact(off_max, target):
    n = len(off_max)
    s = np.sort(off_max)[::-1]
    k = int(np.floor(target * n + 1e-9))
    if k >= n:
        return 0.0, 1.0
    tau = float(np.nextafter(s[k], np.inf))
    return tau, float((off_max >= tau).mean())


# ===========================================================================
def main():
    report = {"tau_op": TAU, "n_boot": N_BOOT, "boot_seed": BOOT_SEED,
              "grid_v1": g1["version"], "grid_v2s": g2["version"],
              "fold_gate": {}, "per_run": {}, "d34": {}, "native": {},
              "val_gate": {}, "pathology": {}, "fa_matched": {}, "corridor": {}}

    D1, D2F, D2N, TW = {}, {}, {}, {}
    gate_fail = []
    for m in MODELS:
        for s in SEEDS:
            run = f"{m}_s{s}"
            d1 = load_pf(os.path.join(V1_BASE, run, "eval_test", "per_frame.csv"), CELLS1)
            d2 = load_pf(os.path.join(V2S_BASE, run, "eval_test", "per_frame.csv"), CELLS2)
            if d1["frame_id"] != d2["frame_id"]:
                raise SystemExit(f"[fatal] {run}: frame_id order differs between V1 and V2S")
            if not (d1["tier"] == d2["tier"]).all() or not (d1["toggle"] == d2["toggle"]).all():
                raise SystemExit(f"[fatal] {run}: tier/toggle differ between V1 and V2S")
            d2f = fold(d2)
            mism = int((d2f["gt"] != d1["gt"]).sum())
            bad_frames = int((d2f["gt"] != d1["gt"]).any(1).sum())
            report["fold_gate"][run] = {"cell_mismatches": mism, "frames_with_mismatch": bad_frames,
                                        "n_frames": len(d1["frame_id"]),
                                        "n_pos_cells_v1": int(d1["gt"].sum()),
                                        "n_pos_cells_v2s_folded": int(d2f["gt"].sum()),
                                        "n_pos_cells_v2s_native": int(d2["gt"].sum())}
            if mism:
                gate_fail.append(run)
            D1[run], D2F[run], D2N[run] = d1, d2f, d2
            TW[run] = {"v1": load_twin_pairs(V1_BASE, run), "v2s": load_twin_pairs(V2S_BASE, run)}

    report["fold_gate"]["VERDICT"] = "FAIL: " + ",".join(gate_fail) if gate_fail else "PASS"
    if gate_fail:
        print(json.dumps(report["fold_gate"], indent=1))
        raise SystemExit("[fatal] GT fold gate FAILED — no adoption arithmetic is meaningful.")

    # ---- shared row-index sets (identical across runs: same frames, same order)
    ref = D1[f"{MODELS[0]}_s{SEEDS[0]}"]
    tier, tog = ref["tier"], ref["toggle"]
    haz = (tog == "on") & ref["gt"].any(1)
    idxH = np.flatnonzero(haz & (tier == "H"))
    idxOff = np.flatnonzero(tog == "off")
    idxOn = np.flatnonzero(tog == "on")
    row_of = {tuple(f.split("/", 2)): i for i, f in enumerate(ref["frame_id"])}
    report["counts"] = {"n_frames": len(tier), "n_H": len(idxH), "n_off": len(idxOff),
                        "n_on": len(idxOn)}

    # ---- kept twin pairs: V1's kept set is the reference (D34: "same kept-pair set as V1")
    kept_ref = [r for r in TW[f"{MODELS[0]}_s{SEEDS[0]}"]["v1"] if r["kept"].strip().lower() == "true"]
    kept_key = [(r["scene_id"], r["cut"]) for r in kept_ref]
    same_kept = {}
    for run in TW:
        for arm in ("v1", "v2s"):
            k = [(r["scene_id"], r["cut"]) for r in TW[run][arm] if r["kept"].strip().lower() == "true"]
            same_kept[f"{run}:{arm}"] = (k == kept_key)
    report["twin_kept_set"] = {"n_kept_pairs_v1_reference": len(kept_key),
                               "all_runs_identical_kept_set": all(same_kept.values()),
                               "mismatching": [k for k, v in same_kept.items() if not v]}

    # ---- per-run headline on the three D34 metrics
    for run in D1:
        d1, d2f = D1[run], D2F[run]
        t1 = twin_deltas(d1, kept_ref, row_of)
        t2 = twin_deltas(d2f, kept_ref, row_of)
        report["per_run"][run] = {
            "v1": {"frame_recall_H": frame_recall_H(d1, idxH),
                   "frame_fa_off": frame_fa_off(d1, idxOff),
                   "twin_delta": nanmean(t1),
                   "n_twin_valid": int(np.isfinite(t1).sum())},
            "v2s_fold": {"frame_recall_H": frame_recall_H(d2f, idxH),
                         "frame_fa_off": frame_fa_off(d2f, idxOff),
                         "twin_delta": nanmean(t2),
                         "n_twin_valid": int(np.isfinite(t2).sum())},
            "v2s_native": {"frame_recall_H": frame_recall_H(D2N[run], idxH),
                           "frame_fa_off": frame_fa_off(D2N[run], idxOff),
                           "twin_delta": nanmean(twin_deltas(D2N[run], kept_ref, row_of))},
        }

    # ---- D34 inequalities, 3 metrics x 3 models
    # ORIENTATION.  D34 is written "d = V2S_fold - V1 ... d >= -0.05" and its stated purpose is
    # 헤드라인 무악화 (no headline degradation).  H recall and twin delta are higher-is-better, so
    # the raw difference already points the right way.  frame_fa_off is LOWER-is-better: taken
    # literally, an FA *improvement* of 0.15 would read as d = -0.15 and FAIL the inequality it was
    # written to protect.  Both readings are reported; SIGN gives the orientation-corrected one
    # (worse = negative for every metric), which is the reading the text's purpose demands.
    SIGN = {"frame_recall_H": +1, "frame_fa_off": -1, "twin_delta": +1}
    METRICS = ("frame_recall_H", "frame_fa_off", "twin_delta")
    for metric in METRICS:
        for m in MODELS:
            runs = [f"{m}_s{s}" for s in SEEDS]
            ds = [report["per_run"][r]["v2s_fold"][metric] - report["per_run"][r]["v1"][metric]
                  for r in runs]
            mean_d, min_d = float(np.mean(ds)), float(np.min(ds))

            # paired bootstrap: ONE resample index per iteration, shared by V1 and V2S and
            # by all three seeds; statistic = seed-mean of (V2S_fold - V1).
            if metric == "twin_delta":
                A = np.array([twin_deltas(D2F[r], kept_ref, row_of) for r in runs])
                B = np.array([twin_deltas(D1[r], kept_ref, row_of) for r in runs])
                n = A.shape[1]

                def stat(idx, A=A, B=B):
                    return float(np.mean([nanmean(A[k][idx]) - nanmean(B[k][idx])
                                          for k in range(A.shape[0])]))
            else:
                rows = idxH if metric == "frame_recall_H" else idxOff
                if metric == "frame_recall_H":
                    A = np.array([((D2F[r]["probs"][rows] >= TAU) & D2F[r]["gt"][rows]).any(1)
                                  for r in runs], float)
                    B = np.array([((D1[r]["probs"][rows] >= TAU) & D1[r]["gt"][rows]).any(1)
                                  for r in runs], float)
                else:
                    A = np.array([(D2F[r]["probs"][rows] >= TAU).any(1) for r in runs], float)
                    B = np.array([(D1[r]["probs"][rows] >= TAU).any(1) for r in runs], float)
                n = A.shape[1]

                def stat(idx, A=A, B=B):
                    return float(np.mean(A[:, idx].mean(1) - B[:, idx].mean(1)))

            rng = np.random.default_rng(BOOT_SEED)
            draws = np.empty(N_BOOT)
            for b in range(N_BOOT):
                draws[b] = stat(rng.integers(0, n, n))
            lo, hi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
            sg = SIGN[metric]
            o_mean, o_min = sg * mean_d, (min(sg * x for x in ds))
            o_lo = lo if sg > 0 else -hi
            report["d34"][f"{metric}|{m}"] = {
                "per_seed_d": ds, "mean_d": mean_d, "min_d": min_d,
                "ci_lo": lo, "ci_hi": hi, "n_units": int(n), "sign": sg,
                "unit": "twin pair" if metric == "twin_delta" else
                        ("H frame" if metric == "frame_recall_H" else "off frame"),
                # literal reading (raw difference, no orientation)
                "literal": {"pass_mean": bool(mean_d >= -0.05), "pass_min": bool(min_d >= -0.10),
                            "pass_ci": bool(lo >= -0.05),
                            "PASS": bool(mean_d >= -0.05 and min_d >= -0.10 and lo >= -0.05)},
                # orientation-corrected reading (worse = negative for every metric)
                "oriented_mean_d": o_mean, "oriented_min_d": o_min, "oriented_ci_lo": o_lo,
                "pass_mean": bool(o_mean >= -0.05), "pass_min": bool(o_min >= -0.10),
                "pass_ci": bool(o_lo >= -0.05),
                "PASS": bool(o_mean >= -0.05 and o_min >= -0.10 and o_lo >= -0.05)}

    # ---- native benefit: sector-localisation error
    for m in MODELS:
        per_seed = []
        for s in SEEDS:
            run = f"{m}_s{s}"
            e1 = loc_error_deg(D1[run]["probs"], D1[run]["gt"], idxOn, BAND1, SEC1, CTR1)
            e2 = loc_error_deg(D2N[run]["native_probs"] if "native_probs" in D2N[run]
                               else D2N[run]["probs"], D2N[run]["gt"], idxOn, BAND2, SEC2, CTR2)
            med1, med2 = float(np.median(e1)), float(np.median(e2))
            per_seed.append({
                "seed": s, "n_frames": int(len(e1)),
                "v1_median_deg": med1, "v2s_median_deg": med2,
                "v1_mean_deg": float(e1.mean()), "v2s_mean_deg": float(e2.mean()),
                "v1_p75_deg": float(np.percentile(e1, 75)), "v2s_p75_deg": float(np.percentile(e2, 75)),
                "v1_frac_zero": float((e1 == 0).mean()), "v2s_frac_zero": float((e2 == 0).mean()),
                "target_0.80xV1": 0.80 * med1, "pass": bool(med2 <= 0.80 * med1 + 1e-12)})
        n_pass = sum(1 for r in per_seed if r["pass"])
        # A median of 0.000 on BOTH grids makes "V2S median <= 0.80 x V1 median" the tautology
        # 0 <= 0.  Flag it: a pass earned this way is VACUOUS and must not be quoted as evidence.
        vac = all(r["v1_median_deg"] == 0.0 and r["v2s_median_deg"] == 0.0 for r in per_seed)
        n_mean_better = sum(1 for r in per_seed if r["v2s_mean_deg"] < r["v1_mean_deg"])
        report["native"][m] = {"per_seed": per_seed, "n_seeds_pass": n_pass,
                               "PASS": bool(n_pass >= 2), "vacuous": bool(vac),
                               "n_seeds_mean_better": n_mean_better,
                               "n_seeds_frac_zero_better": sum(
                                   1 for r in per_seed if r["v2s_frac_zero"] > r["v1_frac_zero"])}

    # ---- native benefit, supplementary: is the COARSE (V1-sector) localisation preserved?
    #      V2S argmax sector -> its V1 parent sector, scored against the V1 GT sector set.
    #      A rise here would mean the finer grid bought resolution by losing coarse accuracy.
    PARENT = np.array([s // 2 for s in range(NS2)])
    for m in MODELS:
        rows = []
        for s in SEEDS:
            run = f"{m}_s{s}"
            e1 = loc_error_deg(D1[run]["probs"], D1[run]["gt"], idxOn, BAND1, SEC1, CTR1)
            e2c = loc_error_deg(D2N[run]["probs"], D2N[run]["gt"], idxOn, BAND2,
                                PARENT[SEC2], CTR1)
            rows.append({"seed": s, "v1_mean_deg": float(e1.mean()),
                         "v2s_coarse_mean_deg": float(e2c.mean()),
                         "v1_frac_zero": float((e1 == 0).mean()),
                         "v2s_coarse_frac_zero": float((e2c == 0).mean())})
        report["native"][m]["coarse_check"] = rows

    # ---- cell-level comparison (criterion 2 material): V1 vs V2S-folded vs V2S-native
    report["cell_level"] = {}
    for m in MODELS:
        rows = []
        for s in SEEDS:
            run = f"{m}_s{s}"
            e = {}
            for tag, d in (("v1", D1[run]), ("v2s_fold", D2F[run]), ("v2s_native", D2N[run])):
                p, g = d["probs"] >= TAU, d["gt"]
                tp, fp = float((p & g).sum()), float((p & ~g).sum())
                fn = float((~p & g).sum())
                off = d["toggle"] == "off"
                e[tag] = {"cell_f1": 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else NAN,
                          "cell_recall": tp / (tp + fn) if (tp + fn) else NAN,
                          "cell_precision": tp / (tp + fp) if (tp + fp) else NAN,
                          "cell_fpr_off": float(((d["probs"][off] >= TAU) & ~g[off]).sum())
                                          / float((~g[off]).sum())}
            rows.append({"seed": s, **e})
        report["cell_level"][m] = {
            "per_seed": rows,
            "mean_cell_f1": {t: float(np.mean([r[t]["cell_f1"] for r in rows]))
                             for t in ("v1", "v2s_fold", "v2s_native")},
            "mean_cell_fpr_off": {t: float(np.mean([r[t]["cell_fpr_off"] for r in rows]))
                                  for t in ("v1", "v2s_fold", "v2s_native")}}

    # ---- native benefit, lateral scenes (val-only: sceneD3.  scene10=train, sceneD4=HOLD)
    lat = {}
    for m in MODELS:
        rows = []
        for s in SEEDS:
            run = f"{m}_s{s}"
            v1v = load_pf(os.path.join(V1_BASE, run, "eval_test", "per_frame_val.csv"), CELLS1)
            v2v = load_pf(os.path.join(V2S_BASE, run, "eval_test", "per_frame_val.csv"), CELLS2)
            sel = np.flatnonzero((v1v["toggle"] == "on") & (v1v["scene_id"] == "sceneD3"))
            if not len(sel):
                continue
            e1 = loc_error_deg(v1v["probs"], v1v["gt"], sel, BAND1, SEC1, CTR1)
            e2 = loc_error_deg(v2v["probs"], v2v["gt"], sel, BAND2, SEC2, CTR2)
            if not len(e1):
                continue
            rows.append({"seed": s, "n_frames": int(len(e1)),
                         "v1_median_deg": float(np.median(e1)), "v2s_median_deg": float(np.median(e2)),
                         "v1_mean_deg": float(e1.mean()), "v2s_mean_deg": float(e2.mean())})
        lat[m] = rows
    report["native_lateral_sceneD3_val"] = lat

    # ---- corridor preservation
    for m in MODELS:
        rows = []
        for s in SEEDS:
            run = f"{m}_s{s}"
            r1, n1 = corridor_ff(D1[run]["probs"], D1[run]["gt"], idxOn, BAND1, SEC1, 1)
            r2a, n2a = corridor_ff(D2N[run]["probs"], D2N[run]["gt"], idxOn, BAND2, SEC2, 1)
            r2b, n2b = corridor_ff(D2N[run]["probs"], D2N[run]["gt"], idxOn, BAND2, SEC2, 2)
            r2f, n2f = corridor_ff(D2F[run]["probs"], D2F[run]["gt"], idxOn, BAND1, SEC1, 1)
            rows.append({"seed": s,
                         "v1_adj_1step_12.44deg": r1, "n_v1": n1,
                         "v2s_native_adj_1step_6.22deg": r2a, "n_v2s_1": n2a,
                         "v2s_native_adj_2step_12.44deg": r2b, "n_v2s_2": n2b,
                         "v2s_folded_adj_1step_12.44deg": r2f, "n_v2s_fold": n2f})
        report["corridor"][m] = {"per_seed": rows,
                                 "mean_v1": float(np.mean([r["v1_adj_1step_12.44deg"] for r in rows])),
                                 "mean_v2s_native_1step": float(np.mean([r["v2s_native_adj_1step_6.22deg"] for r in rows])),
                                 "mean_v2s_native_2step": float(np.mean([r["v2s_native_adj_2step_12.44deg"] for r in rows])),
                                 "mean_v2s_folded": float(np.mean([r["v2s_folded_adj_1step_12.44deg"] for r in rows]))}

    # ---- val positivity gate (GT columns are run-independent; verified across all 9)
    vv = load_pf(os.path.join(V2S_BASE, "rgb_s42", "eval_test", "per_frame_val.csv"), CELLS2)
    for m in MODELS:
        for s in SEEDS:
            o = load_pf(os.path.join(V2S_BASE, f"{m}_s{s}", "eval_test", "per_frame_val.csv"), CELLS2)
            if not (o["gt"] == vv["gt"]).all():
                raise SystemExit("[fatal] val GT differs across V2S runs")
    cnt2 = vv["gt"].sum(0).astype(int)
    v1v = load_pf(os.path.join(V1_BASE, "rgb_s42", "eval_test", "per_frame_val.csv"), CELLS1)
    cnt1 = v1v["gt"].sum(0).astype(int)
    viol = [{"cell": CELLS2[i], "n_pos": int(cnt2[i])} for i in range(len(CELLS2)) if cnt2[i] < 3]
    report["val_gate"] = {
        "n_val_frames": len(vv["frame_id"]),
        "v2s_counts": {CELLS2[i]: int(cnt2[i]) for i in range(len(CELLS2))},
        "v1_counts": {CELLS1[i]: int(cnt1[i]) for i in range(len(CELLS1))},
        "violators": viol, "n_violators": len(viol),
        "v1_violators": [{"cell": CELLS1[i], "n_pos": int(cnt1[i])}
                         for i in range(len(CELLS1)) if cnt1[i] < 3],
        "PASS": bool(len(viol) == 0)}

    # ---- training pathology (criterion 3)
    for base, tag in ((V1_BASE, "v1"), (V2S_BASE, "v2s")):
        report["pathology"][tag] = {}
        for m in MODELS:
            for s in SEEDS:
                run = f"{m}_s{s}"
                cfg = json.load(open(os.path.join(base, run, "config.json")))
                rows = list(csv.DictReader(open(os.path.join(base, run, "metrics.csv"))))
                sel = [float(r["sel_score"]) for r in rows]
                f1 = [float(r["val_f1"]) for r in rows]
                hr = [float(r["val_h_recall"]) for r in rows]
                be = int(cfg["best_epoch"])
                report["pathology"][tag][run] = {
                    "best_epoch": be, "n_epochs": len(rows),
                    "stop_reason": cfg.get("stop_reason"),
                    "best_sel": float(cfg.get("best_sel_score", NAN)),
                    "sel_ep1": sel[0], "sel_ep2": sel[1] if len(sel) > 1 else NAN,
                    "sel_max": float(max(sel)), "sel_argmax_epoch": int(np.argmax(sel)) + 1,
                    "val_f1_ep1": f1[0], "val_h_recall_ep1": hr[0],
                    "sel_first5": sel[:5],
                    "ep1_collapse": bool(be == 1),
                    "selection_fallback_to_f1": bool(cfg.get("selection_fallback_to_f1", False))}
        report["pathology"][tag]["n_ep1_collapse"] = sum(
            1 for k, v in report["pathology"][tag].items()
            if isinstance(v, dict) and v.get("ep1_collapse"))

    # ---- R1-F1 lens: FA-matched H recall, V1 vs V2S-fold
    for target in (0.10, 0.20):
        for m in MODELS:
            rows = []
            for s in SEEDS:
                run = f"{m}_s{s}"
                out = {"seed": s}
                for tag, d in (("v1", D1[run]), ("v2s_fold", D2F[run])):
                    off_max = d["probs"][idxOff].max(1)
                    t, fa = tau_for_fa_exact(off_max, target)
                    out[tag] = {"tau": t, "achieved_fa": fa,
                                "H": frame_recall_H(d, idxH, t)}
                out["dH"] = out["v2s_fold"]["H"] - out["v1"]["H"]
                rows.append(out)
            report["fa_matched"][f"{target}|{m}"] = {
                "per_seed": rows,
                "mean_v1_H": float(np.mean([r["v1"]["H"] for r in rows])),
                "mean_v2s_H": float(np.mean([r["v2s_fold"]["H"] for r in rows])),
                "mean_dH": float(np.mean([r["dH"] for r in rows]))}

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "v2s_adoption.json"), "w") as f:
        json.dump(report, f, indent=1)
    print(json.dumps({"fold_gate": report["fold_gate"]["VERDICT"],
                      "twin_kept": report["twin_kept_set"],
                      "counts": report["counts"],
                      "d34_cells_passing": sum(v["PASS"] for v in report["d34"].values()),
                      "val_gate": report["val_gate"]["PASS"],
                      "ep1_collapse_v2s": report["pathology"]["v2s"]["n_ep1_collapse"]}, indent=1))
    return report


# --------------------------------------------------------------- adoption package
def emit_package(report):
    """산출-선행 package.  Written ONLY on --emit-package, i.e. only if 승용 rules the track
    adopt-eligible at gate (4).  Producing it unasked would itself read as an adoption signal."""
    pkg = os.path.join(OUT_DIR, "adoption_package")
    os.makedirs(pkg, exist_ok=True)
    import shutil
    shutil.copy(os.path.join(V2S_BASE, "SEED_TABLE.md"),
                os.path.join(pkg, "SEED_TABLE_v2s_basis.md"))
    pr, cl = report["per_run"], report["cell_level"]

    def ms(vals):
        return f"{np.mean(vals):.4f} ±{(max(vals) - min(vals)) / 2:.4f}"
    L = ["# V2S 채택 산출-선행 package", "",
         "생성 조건: `fold_check.py --emit-package` (승용이 게이트 ④에서 채택 적격을 선언한 경우에만).",
         "판정 근거는 `../V2S_ADOPTION.md`, 원수치는 `../v2s_adoption.json`.", "",
         "## 1. 헤드라인 — 폴딩 채널(20칸 등가) 기준, tau=0.5", "",
         "| model | frame_recall_H | frame_fa_off | twin delta |", "|---|---|---|---|"]
    for m in MODELS:
        rs = [f"{m}_s{s}" for s in SEEDS]
        L.append(f"| {m} | {ms([pr[r]['v2s_fold']['frame_recall_H'] for r in rs])} | "
                 f"{ms([pr[r]['v2s_fold']['frame_fa_off'] for r in rs])} | "
                 f"{ms([pr[r]['v2s_fold']['twin_delta'] for r in rs])} |")
    L += ["", "## 2. 폴딩 vs 네이티브 vs V1 대조", "",
          "| model | 채널 | H recall | FA off | twin delta | cell F1 |", "|---|---|---|---|---|---|"]
    for m in MODELS:
        rs = [f"{m}_s{s}" for s in SEEDS]
        for tag, lbl in (("v1", "V1 20칸"), ("v2s_fold", "V2S 폴딩"), ("v2s_native", "V2S 네이티브")):
            f1 = ms([r[tag]["cell_f1"] for r in cl[m]["per_seed"]])
            L.append(f"| {m} | {lbl} | {ms([pr[r][tag]['frame_recall_H'] for r in rs])} | "
                     f"{ms([pr[r][tag]['frame_fa_off'] for r in rs])} | "
                     f"{ms([pr[r][tag]['twin_delta'] for r in rs])} | {f1} |")
    L += ["", "## 3. 함께 가야 하는 캐비앗", "",
          "- 프레임 FA는 폴딩 불변(§1.1) — 폴딩·네이티브 FA 열이 같은 것은 정상이다.",
          "- 네이티브 국소화 이득은 **공허 통과**였다(중앙값 0 대 0). 채택하더라도 "
          "\"각 분해능이 국소화를 개선했다\"고 쓸 근거는 이 데이터에 없다.",
          "- test 7씬에 측방 위험 씬이 0개다(D3=val · D4=HOLD · s10=train). "
          "측방 주장은 분할 재설계 없이는 불가.",
          "- V1 seed k와 V2S seed k는 라벨이 달라 독립 추첨이다. 시드 불확실성은 "
          "프레임 부트스트랩 CI에 들어 있지 않다.", ""]
    open(os.path.join(pkg, "HEADLINE_V2S_BASIS.md"), "w").write("\n".join(L))
    print(f"[emit-package] wrote {pkg}/ (SEED_TABLE_v2s_basis.md, HEADLINE_V2S_BASIS.md)")


if __name__ == "__main__":
    rep = main()
    if "--emit-package" in sys.argv:
        emit_package(rep)
