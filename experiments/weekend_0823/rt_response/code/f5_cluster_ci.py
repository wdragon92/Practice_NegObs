"""F5 — SCENE-CLUSTER BOOTSTRAP (D35 / R2 §4.2, F3).

`mainrun_0819/code/bootstrap.py` gets the pairing exactly right (one shared resample
index across both arms) but resamples FRAMES i.i.d.  Test frames are clustered by
scene — one scene contributes up to 72 frames that are the same geometry under
different lighting and camera cuts — so a frame bootstrap measures within-scene
variation and says nothing about generalisation to another scene.

This script re-derives the CIs with the scene as the resampling unit, using a NEW
function in an isolated path (the canonical `bootstrap.py` is not modified).

  * FA (off arm, 7 test scenes): cluster CI reported — enough clusters to resample.
  * H (2 scenes) / E (1 scene): cluster CI is NOT reportable.  The script prints the
    degenerate interval to show why, and emits the per-scene values that replace it.
  * aux-vs-base paired cell_f1: recomputed under cluster resampling, both arms
    sharing the cluster draw.

Outputs: f5_cluster_ci.json, F5_CLUSTER_CI.md
"""
import csv
import json
import os
import numpy as np
from common_rt import BASE, MODELS, SEEDS, RUNS

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
N_BOOT = 10000
SEED = 42
TAU = 0.5


def load_dump(path):
    rows = list(csv.DictReader(open(path)))
    cells = [k[2:] for k in rows[0] if k.startswith("p_")]
    return dict(
        frame_id=[r["frame_id"] for r in rows],
        scene=np.array([r["scene_id"] for r in rows]),
        tier=np.array([r["tier"] for r in rows]),
        toggle=np.array([r["toggle_state"] for r in rows]),
        P=np.array([[float(r["p_" + c]) for c in cells] for r in rows]),
        G=np.array([[float(r["g_" + c]) for c in cells] for r in rows]))


def stats(d, idx, tau=TAU):
    P, G = d["P"][idx], d["G"][idx]
    tier, tog = d["tier"][idx], d["toggle"][idx]
    pred, pos = P >= tau, G > 0.5
    on, off = tog == "on", tog == "off"
    haz = on & pos.any(1)
    det = (pred & pos).any(1)
    tp = float((pred & pos).sum()); fp = float((pred & ~pos).sum())
    fn = float((~pred & pos).sum())
    r = lambda a, b: float(a) / float(b) if b > 0 else float("nan")  # noqa: E731
    out = {"cell_f1": r(2 * tp, 2 * tp + fp + fn),
           "cell_precision": r(tp, tp + fp), "cell_recall": r(tp, tp + fn),
           "frame_fa_off": r(pred[off].any(1).sum(), off.sum()),
           "cell_fpr_off": r((pred[off] & ~pos[off]).sum(), (~pos[off]).sum()),
           "frame_det_rate": r(det[haz].sum(), haz.sum())}
    for t in ("V", "E", "H"):
        s = haz & (tier == t)
        out[f"frame_recall_{t}"] = r(det[s].sum(), s.sum())
        out[f"cell_recall_{t}"] = r((pred[s] & pos[s]).sum(), pos[s].sum())
    return out


def cluster_index_map(scenes):
    uni = sorted(set(scenes.tolist()))
    return uni, [np.nonzero(scenes == u)[0] for u in uni]


def ci_frame(d, keys, n_boot=N_BOOT, seed=SEED, alpha=0.05, sub=None):
    """The published rule: i.i.d. frame resampling."""
    rng = np.random.default_rng(seed)
    idx0 = np.arange(len(d["scene"])) if sub is None else sub
    n = len(idx0)
    draws = {k: [] for k in keys}
    for _ in range(n_boot):
        s = stats(d, idx0[rng.integers(0, n, n)])
        for k in keys:
            draws[k].append(s[k])
    return summarise(stats(d, idx0), draws, keys, alpha)


def ci_cluster(d, keys, n_boot=N_BOOT, seed=SEED, alpha=0.05, sub=None):
    """Scene as the resampling unit."""
    rng = np.random.default_rng(seed)
    idx0 = np.arange(len(d["scene"])) if sub is None else sub
    _uni, groups = cluster_index_map(d["scene"][idx0])
    groups = [idx0[g] for g in groups]
    k_cl = len(groups)
    draws = {k: [] for k in keys}
    for _ in range(n_boot):
        pick = rng.integers(0, k_cl, k_cl)
        idx = np.concatenate([groups[j] for j in pick])
        s = stats(d, idx)
        for k in keys:
            draws[k].append(s[k])
    r = summarise(stats(d, idx0), draws, keys, alpha)
    for k in r:
        r[k]["n_clusters"] = k_cl
    return r


def summarise(point, draws, keys, alpha):
    out = {}
    for k in keys:
        v = np.asarray(draws[k], float)
        v = v[np.isfinite(v)]
        lo, hi = (float(np.percentile(v, 100 * alpha / 2)),
                  float(np.percentile(v, 100 * (1 - alpha / 2)))) if v.size else (np.nan, np.nan)
        out[k] = {"point": float(point[k]), "lo": lo, "hi": hi, "width": hi - lo,
                  "n_valid": int(v.size)}
    return out


res = {"n_boot": N_BOOT, "tau": TAU, "provenance": {
    "input": "experiments/dayrun_0820/runs/v2/*/eval_test/per_frame.csv",
    "canonical_bootstrap": "experiments/mainrun_0819/code/bootstrap.py (NOT modified; "
                           "the cluster function lives only in this isolated script)",
    "clusters": "scene_id.  test = 7 scenes; off arm spans all 7; H spans 2 (scene14, "
                "scene15); E spans 1 (scene18).",
}, "fa": {}, "tier_clusters": {}, "aux": {}}

# ---------------------------------------------------------------- 1. FA, all 9 runs
for run in RUNS:
    d = load_dump(os.path.join(BASE, run, "eval_test", "per_frame.csv"))
    f = ci_frame(d, ["frame_fa_off", "cell_fpr_off", "cell_f1", "frame_det_rate"])
    c = ci_cluster(d, ["frame_fa_off", "cell_fpr_off", "cell_f1", "frame_det_rate"])
    res["fa"][run] = {"frame_iid": f, "scene_cluster": c,
                      "width_ratio": {k: (c[k]["width"] / f[k]["width"])
                                      if f[k]["width"] > 0 else float("nan") for k in f}}

# ---------------------------------------------------------------- 2. H / E cluster counts
d0 = load_dump(os.path.join(BASE, "rgb_s42", "eval_test", "per_frame.csv"))
for tier in ("V", "E", "H"):
    sel = np.nonzero((d0["toggle"] == "on") & (d0["tier"] == tier))[0]
    uni = sorted(set(d0["scene"][sel].tolist()))
    res["tier_clusters"][tier] = {
        "n_frames": int(len(sel)), "n_clusters": len(uni),
        "per_scene_n": {u: int((d0["scene"][sel] == u).sum()) for u in uni},
        "ci_reportable": len(uni) >= 5}

# degenerate H interval, shown to justify the withdrawal
res["H_degenerate_demo"] = {}
for run in RUNS:
    d = load_dump(os.path.join(BASE, run, "eval_test", "per_frame.csv"))
    sub = np.nonzero((d["toggle"] == "on") & (d["tier"] == "H"))[0]
    f = ci_frame(d, ["frame_recall_H"], sub=sub)["frame_recall_H"]
    c = ci_cluster(d, ["frame_recall_H"], sub=sub)["frame_recall_H"]
    per_scene = {}
    for sc in ("scene14", "scene15"):
        s2 = np.nonzero((d["toggle"] == "on") & (d["tier"] == "H") & (d["scene"] == sc))[0]
        per_scene[sc] = {"n": int(len(s2)), "recall": stats(d, s2)["frame_recall_H"]}
        s3 = np.nonzero((d["toggle"] == "off") & (d["scene"] == sc))[0]
        per_scene[sc]["off_fa"] = stats(d, s3)["frame_fa_off"]
    res["H_degenerate_demo"][run] = {"frame_iid": f, "scene_cluster_2": c,
                                     "per_scene": per_scene}

# ---------------------------------------------------------------- 3. aux vs base, paired
base = load_dump(os.path.join(BASE, "rgb_s42", "eval_test", "per_frame.csv"))
aux = load_dump(os.path.join(BASE, "rgb_s42_aux", "eval_test", "per_frame.csv"))
assert base["frame_id"] == aux["frame_id"], "aux/base dumps are not row-aligned"
AUX_KEYS = ["cell_f1", "cell_precision", "cell_recall", "frame_fa_off", "cell_fpr_off",
            "frame_recall_H", "cell_recall_H", "frame_recall_E", "cell_recall_E",
            "frame_recall_V", "frame_det_rate"]
# metrics whose support lives in a single scene: a cluster bootstrap cannot move them,
# so their "CI" is degenerate and must be reported as withdrawn, not as significant
SINGLE_CLUSTER = {"frame_recall_E", "cell_recall_E"}


def paired(mode, n_boot=N_BOOT, seed=SEED, alpha=0.05):
    rng = np.random.default_rng(seed)
    n = len(base["scene"])
    _uni, groups = cluster_index_map(base["scene"])
    k_cl = len(groups)
    pa, pb = stats(aux, np.arange(n)), stats(base, np.arange(n))
    draws = {k: [] for k in AUX_KEYS}
    for _ in range(n_boot):
        idx = (rng.integers(0, n, n) if mode == "frame"
               else np.concatenate([groups[j] for j in rng.integers(0, k_cl, k_cl)]))
        a, b = stats(aux, idx), stats(base, idx)
        for k in AUX_KEYS:
            draws[k].append(a[k] - b[k])
    out = {}
    for k in AUX_KEYS:
        v = np.asarray(draws[k], float); v = v[np.isfinite(v)]
        lo, hi = float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))
        out[k] = {"aux": pa[k], "base": pb[k], "diff": pa[k] - pb[k], "lo": lo, "hi": hi,
                  "width": hi - lo, "excludes_zero": bool(lo > 0 or hi < 0)}
    return out


res["aux"]["frame_iid"] = paired("frame")
res["aux"]["scene_cluster"] = paired("cluster")
res["aux"]["n_clusters"] = len(set(base["scene"].tolist()))

json.dump(res, open(os.path.join(OUT, "f5_cluster_ci.json"), "w"), indent=1)


def f(x, nd=4):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


L = []
L.append("# F5 — Scene-cluster bootstrap CIs (RED-TEAM RESPONSE, D35 / R2 §4.2)\n")
L.append("Generated by `rt_response/code/f5_cluster_ci.py` · CPU · 10 000 resamples · "
         "the canonical `mainrun_0819/code/bootstrap.py` is **not modified**; the cluster "
         "function exists only in this isolated script (append-only rule).\n")
L.append("Resampling unit = `scene_id`.  test = 7 scenes.  A scene contributes up to 72 frames "
         "that are the same geometry under different lighting and camera cuts, so a frame "
         "bootstrap measures within-scene variation only.\n")

L.append("\n## 1. Off-arm false alarm — cluster CI is reportable (7 clusters)\n")
L.append("| run | FA | frame-i.i.d. CI | width | **scene-cluster CI** | width | ratio |")
L.append("|---|---|---|---|---|---|---|")
for run in RUNS:
    a = res["fa"][run]["frame_iid"]["frame_fa_off"]
    b = res["fa"][run]["scene_cluster"]["frame_fa_off"]
    L.append("| %s | %s | [%s, %s] | %s | **[%s, %s]** | %s | **×%.1f** |" % (
        run, f(a["point"], 3), f(a["lo"], 3), f(a["hi"], 3), f(a["width"], 3),
        f(b["lo"], 3), f(b["hi"], 3), f(b["width"], 3),
        res["fa"][run]["width_ratio"]["frame_fa_off"]))

L.append("\n**R2 §4.2 verification** (the three rows R2 published):\n")
L.append("| run | R2 frame CI | recomputed | R2 cluster CI | recomputed | R2 ratio | recomputed |")
L.append("|---|---|---|---|---|---|---|")
R2P = {"rgb_s42": ("[0.328, 0.422]", "[0.162, 0.643]", 5.2),
       "rgb_s44": ("[0.184, 0.262]", "[0.056, 0.471]", 5.3),
       "depth_s42": ("[0.032, 0.074]", "[0.012, 0.125]", 2.7)}
for run, (fa_, ca_, ra_) in R2P.items():
    a = res["fa"][run]["frame_iid"]["frame_fa_off"]
    b = res["fa"][run]["scene_cluster"]["frame_fa_off"]
    L.append("| %s | %s | [%s, %s] | %s | [%s, %s] | ×%.1f | ×%.1f |" % (
        run, fa_, f(a["lo"], 3), f(a["hi"], 3), ca_, f(b["lo"], 3), f(b["hi"], 3),
        ra_, res["fa"][run]["width_ratio"]["frame_fa_off"]))

L.append("\n**Other all-frame metrics under cluster resampling** (same 7 clusters):\n")
L.append("| run | cell_f1 frame CI | cell_f1 cluster CI | ratio | det_rate frame CI | "
         "det_rate cluster CI | ratio |")
L.append("|---|---|---|---|---|---|---|")
for run in RUNS:
    a1 = res["fa"][run]["frame_iid"]["cell_f1"]; b1 = res["fa"][run]["scene_cluster"]["cell_f1"]
    a2 = res["fa"][run]["frame_iid"]["frame_det_rate"]
    b2 = res["fa"][run]["scene_cluster"]["frame_det_rate"]
    L.append("| %s | [%s, %s] | [%s, %s] | ×%.1f | [%s, %s] | [%s, %s] | ×%.1f |" % (
        run, f(a1["lo"], 3), f(a1["hi"], 3), f(b1["lo"], 3), f(b1["hi"], 3),
        res["fa"][run]["width_ratio"]["cell_f1"],
        f(a2["lo"], 3), f(a2["hi"], 3), f(b2["lo"], 3), f(b2["hi"], 3),
        res["fa"][run]["width_ratio"]["frame_det_rate"]))

L.append("\n## 2. H and E — the CI is withdrawn, not widened\n")
L.append("| tier | n frames | n scene clusters | scenes | CI reportable |")
L.append("|---|---|---|---|---|")
for t in ("V", "E", "H"):
    c = res["tier_clusters"][t]
    L.append("| %s | %d | **%d** | %s | %s |" % (
        t, c["n_frames"], c["n_clusters"],
        " · ".join(f"{k} {v}" for k, v in c["per_scene_n"].items()),
        "yes" if c["ci_reportable"] else "**no**"))
L.append("\nWith 2 clusters the cluster bootstrap draws only 3 distinct multisets "
         "({14,14},{14,15},{15,15}), so the interval it returns is an artefact of that "
         "enumeration, not an inference.  Shown once, to be replaced by the per-scene values:\n")
L.append("| run | H recall (pooled) | frame-i.i.d. CI | degenerate 2-cluster CI | "
         "scene14 recall (n=60) | scene14 off-FA | scene15 recall (n=36) | scene15 off-FA |")
L.append("|---|---|---|---|---|---|---|---|")
for run in RUNS:
    e = res["H_degenerate_demo"][run]
    a, c = e["frame_iid"], e["scene_cluster_2"]
    p14, p15 = e["per_scene"]["scene14"], e["per_scene"]["scene15"]
    L.append("| %s | %s | [%s, %s] | [%s, %s] | %s | %s | %s | %s |" % (
        run, f(a["point"], 3), f(a["lo"], 3), f(a["hi"], 3), f(c["lo"], 3), f(c["hi"], 3),
        f(p14["recall"], 3), f(p14["off_fa"], 3), f(p15["recall"], 3), f(p15["off_fa"], 3)))

L.append("\n## 3. The auxiliary pixel-loss cell_f1 CI — does it survive clustering?\n")
L.append("Paired aux − base on rgb seed 42, the same 816 rows, one resample draw shared by both "
         "arms (the pairing discipline of `bootstrap.py` is preserved; only the unit changes).\n")
L.append("| metric | aux | base | Δ | frame-i.i.d. 95 % CI | excl. 0 | scene-cluster 95 % CI | "
         "excl. 0 | width × | verdict |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for k in AUX_KEYS:
    a = res["aux"]["frame_iid"][k]
    b = res["aux"]["scene_cluster"][k]
    if k in SINGLE_CLUSTER:
        verdict = "**degenerate** — support is 1 scene (scene18); withdraw the CI"
        excl = "n/a"
    elif a["excludes_zero"] and not b["excludes_zero"]:
        verdict = "**significance does not survive clustering**"
        excl = "**no**"
    elif b["excludes_zero"]:
        verdict = "survives"
        excl = "yes"
    else:
        verdict = "was not significant either way"
        excl = "no"
    L.append("| %s | %s | %s | %+.4f | [%s, %s] | %s | [%s, %s] | %s | ×%.1f | %s |" % (
        k, f(a["aux"]), f(a["base"]), a["diff"], f(a["lo"]), f(a["hi"]),
        "yes" if a["excludes_zero"] else "no", f(b["lo"]), f(b["hi"]), excl,
        b["width"] / a["width"] if a["width"] > 0 else float("nan"), verdict))

open(os.path.join(OUT, "F5_CLUSTER_CI.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
