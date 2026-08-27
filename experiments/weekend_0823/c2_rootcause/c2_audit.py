#!/usr/bin/env python3
"""WEEKEND 0823 / CPU-3 -- systematic difference audit of `sceneC2` against the other test scenes.

Brief: `Docs/campaign/WEEKEND_BRIEF_0823.md` sec 6.3.  Question: why is `sceneC2` the outlier
scene -- 76.1 % of the Depth arm's off-arm cell fires (DIAG_V2 sec 3.1), the "16 mm read as a
2.24 m drop" hallucination (DIAG_V1 sec 3.2), and FA 0.681 under the dressing-preserving OFF arm
(CTRL_TABLE sec 1)?

Read-only over frozen artefacts.  Writes ONLY into this directory.  CPU, `env_seg`.
NO SCENE IS EDITED by this script.

    PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="" python c2_audit.py
"""
from __future__ import annotations

import csv
import glob
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import round_dir_or_flat   # noqa: E402
DR = os.path.join(REPO, "experiments/dayrun_0820")
RUNS = os.path.join(DR, "runs/v2")
OUT = os.path.dirname(os.path.abspath(__file__))

SECT = ["A", "B", "C", "D", "E"]
BN = ["1", "2", "3a", "3b"]
CELLS = [f"{s}{b}" for b in BN for s in SECT]
MODELS = ("rgb", "depth", "b2")
SEEDS = (42, 43, 44)
TAU = 0.5
DEPTH_CLIP_M = 10.0          # polar_dataset.py -- what the Depth model actually sees

MANIFEST = json.load(open(os.path.join(DR, "dataset_manifest_v2_full.json")))
SPLIT = json.load(open(os.path.join(DR, "split_v2_full.json")))
FRAMES = MANIFEST["frames"]
TEST = sorted(SPLIT["test"])
REP: dict = {}


# --------------------------------------------------------------------------- #
# 1. sampling census -- how many DISTINCT inputs does each arm really have?
# --------------------------------------------------------------------------- #
def census():
    out = {}
    for sc in TEST:
        for arm in ("on", "off"):
            fr = [f for f in FRAMES if f["scene_id"] == sc and f["toggle_state"] == arm]
            conds = sorted({f["cond"] for f in fr})
            rounds = sorted({f["round"] for f in fr})
            # a Depth input is fully determined by the camera pose: light changes RGB only.
            poses = {(f["round"], round(f["cam"]["d"], 4), round(f["cam"]["h_rel"], 4),
                      round(f["cam"]["yaw"], 4), round(f["cam"]["pitch"], 4)) for f in fr}
            out[f"{sc}_{arm}"] = dict(n_frames=len(fr), conds=conds, n_conds=len(conds),
                                      rounds=rounds, n_rounds=len(rounds),
                                      n_distinct_camera_poses=len(poses))
    return out


def depth_hash_check(scene, arm="off"):
    """Verify empirically that depth sidecars are byte-identical across light conditions."""
    fr = [f for f in FRAMES if f["scene_id"] == scene and f["toggle_state"] == arm]
    h = {}
    for f in fr:
        k = hashlib.md5(np.load(f["depth"]).tobytes()).hexdigest()
        h.setdefault(k, []).append(f["cond"])
    return dict(n_frames=len(fr), n_distinct_depth_maps=len(h),
                replicates=sorted({len(v) for v in h.values()}))


# --------------------------------------------------------------------------- #
# 2. per-frame off-arm firing, localised to the camera pose
# --------------------------------------------------------------------------- #
def read_pf(model, seed):
    rows = {}
    with open(os.path.join(RUNS, f"{model}_s{seed}/eval_test/per_frame.csv")) as fh:
        for r in csv.DictReader(fh):
            rows[r["frame_id"]] = dict(
                scene=r["scene_id"], toggle=r["toggle_state"],
                p=np.array([float(r[f"p_{c}"]) for c in CELLS]))
    return rows


PF = {(m, s): read_pf(m, s) for m in MODELS for s in SEEDS}
FBYID = {f["frame_id"]: f for f in FRAMES}


def fa_by_pose():
    """Off-arm false alarms per scene, counted at the CAMERA POSE level as well as per frame."""
    out = {}
    for m in MODELS:
        for sc in TEST:
            per_seed = []
            for s in SEEDS:
                fired_frames, fired_poses, all_poses, cells = 0, set(), set(), 0
                for fid, row in PF[(m, s)].items():
                    if row["scene"] != sc or row["toggle"] != "off":
                        continue
                    f = FBYID[fid]
                    pose = (f["round"], round(f["cam"]["d"], 4), round(f["cam"]["h_rel"], 4),
                            round(f["cam"]["yaw"], 4), round(f["cam"]["pitch"], 4))
                    all_poses.add(pose)
                    n = int((row["p"] >= TAU).sum())
                    cells += n
                    if n:
                        fired_frames += 1
                        fired_poses.add(pose)
                per_seed.append(dict(frames_fired=fired_frames, cells=cells,
                                     poses_fired=len(fired_poses), poses_total=len(all_poses)))
            out[f"{m}_{sc}"] = dict(
                per_seed=per_seed,
                mean_frame_FA=float(np.mean([x["frames_fired"] for x in per_seed])
                                    / max(1, len([1 for fid, r in PF[(m, 42)].items()
                                                  if r["scene"] == sc and r["toggle"] == "off"]))),
                poses_fired_per_seed=[x["poses_fired"] for x in per_seed],
                poses_total=per_seed[0]["poses_total"],
                cells_per_seed=[x["cells"] for x in per_seed])
    # share of each model's total off-arm cell fires
    for m in MODELS:
        tot = [sum(out[f"{m}_{sc}"]["cells_per_seed"][i] for sc in TEST) for i in range(3)]
        for sc in TEST:
            c = out[f"{m}_{sc}"]["cells_per_seed"]
            out[f"{m}_{sc}"]["cell_share_3seed"] = float(
                np.mean([c[i] / tot[i] if tot[i] else 0.0 for i in range(3)]))
    return out


# --------------------------------------------------------------------------- #
# 3. depth-sidecar statistics, per scene x arm (what the Depth model sees)
# --------------------------------------------------------------------------- #
BAND_EDGES = [0.0, 2.0, 5.0, 8.0, 12.0]


def depth_stats_frame(path):
    d = np.load(path).astype(np.float32)
    fin = np.isfinite(d)
    v = d[fin]
    clipped = np.clip(np.nan_to_num(d, nan=DEPTH_CLIP_M, posinf=DEPTH_CLIP_M,
                                    neginf=0.0), 0.0, DEPTH_CLIP_M)
    st = dict(
        finite_frac=float(fin.mean()),
        inf_frac=float((~fin).mean()),
        p05=float(np.percentile(v, 5)), p25=float(np.percentile(v, 25)),
        p50=float(np.percentile(v, 50)), p75=float(np.percentile(v, 75)),
        p95=float(np.percentile(v, 95)),
        max_finite=float(v.max()), min_finite=float(v.min()),
        # what the network sees after clip+normalise
        sat_frac=float((clipped >= DEPTH_CLIP_M - 1e-6).mean()),
        mean_norm=float((clipped / DEPTH_CLIP_M).mean()),
        std_norm=float((clipped / DEPTH_CLIP_M).std()),
    )
    for i in range(4):
        lo, hi = BAND_EDGES[i], BAND_EDGES[i + 1]
        st[f"frac_band{BN[i]}"] = float(((d >= lo) & (d < hi)).mean())
    # vertical structure: how fast depth grows down->up the image (a receding ground plane
    # has a smooth monotone ramp; walls/objects break it).  Measured on the clipped map.
    g = np.abs(np.diff(clipped[::8, ::8], axis=0))
    st["vgrad_mean"] = float(g.mean())
    st["vgrad_p99"] = float(np.percentile(g, 99))
    # horizontal texture -- a bare plane has almost none
    gh = np.abs(np.diff(clipped[::8, ::8], axis=1))
    st["hgrad_mean"] = float(gh.mean())
    return st


def depth_stats():
    out = {}
    per_frame = []
    for sc in TEST:
        for arm in ("on", "off"):
            fr = [f for f in FRAMES if f["scene_id"] == sc and f["toggle_state"] == arm]
            # one frame per DISTINCT depth map (light replicates carry identical depth)
            seen, keep = set(), []
            for f in fr:
                pose = (f["round"], round(f["cam"]["d"], 4), round(f["cam"]["h_rel"], 4),
                        round(f["cam"]["yaw"], 4), round(f["cam"]["pitch"], 4))
                if pose in seen:
                    continue
                seen.add(pose)
                keep.append(f)
            acc = []
            for f in keep:
                st = depth_stats_frame(f["depth"])
                st.update(scene=sc, arm=arm, frame_id=f["frame_id"], cond=f["cond"],
                          round=f["round"], d=f["cam"]["d"], h_rel=f["cam"]["h_rel"],
                          pitch=f["cam"]["pitch"], yaw=f["cam"]["yaw"])
                acc.append(st)
                per_frame.append(st)
            keys = [k for k in acc[0] if isinstance(acc[0][k], float)]
            out[f"{sc}_{arm}"] = dict(n_distinct=len(acc),
                                      **{k: float(np.mean([a[k] for a in acc])) for k in keys})
    with open(os.path.join(OUT, "c2_depth_stats_perframe.csv"), "w", newline="") as fh:
        cols = ["scene", "arm", "frame_id", "cond", "round", "d", "h_rel", "pitch", "yaw"] + \
               [k for k in per_frame[0] if k not in
                ("scene", "arm", "frame_id", "cond", "round", "d", "h_rel", "pitch", "yaw")]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in per_frame:
            w.writerow(r)
    return out, per_frame


# --------------------------------------------------------------------------- #
# 4. does a depth FEATURE separate the firing off-frames, across ALL test scenes?
# --------------------------------------------------------------------------- #
def feature_discrimination(per_frame):
    """For the Depth model: compare depth-map features of off-arm poses that fire vs those that
    do not, pooled over all 7 test scenes.  If a scene-independent feature separates them, the
    C2 concentration is a *geometry/render* property; if only the scene id does, it is identity."""
    idx = {(r["scene"], r["frame_id"]): r for r in per_frame if r["arm"] == "off"}
    feats = [k for k in next(iter(idx.values())) if isinstance(next(iter(idx.values()))[k], float)
             and k not in ("d", "h_rel", "pitch", "yaw")]
    out = {}
    for m in ("depth", "rgb"):
        fire, quiet = [], []
        for (sc, fid), r in idx.items():
            n = int(np.mean([(PF[(m, s)][fid]["p"] >= TAU).sum() for s in SEEDS]))
            (fire if n > 0 else quiet).append(r)
        res = {}
        for k in feats:
            a = np.array([r[k] for r in fire], float)
            b = np.array([r[k] for r in quiet], float)
            if a.size and b.size:
                pooled = np.sqrt((a.var(ddof=1) * (a.size - 1) + b.var(ddof=1) * (b.size - 1))
                                 / max(1, a.size + b.size - 2)) if a.size > 1 and b.size > 1 else np.nan
                res[k] = dict(fire_mean=float(a.mean()), quiet_mean=float(b.mean()),
                              cohen_d=float((a.mean() - b.mean()) / pooled) if pooled else float("nan"))
        out[m] = dict(n_fire_poses=len(fire), n_quiet_poses=len(quiet),
                      fire_scene_mix={sc: sum(1 for r in fire if r["scene"] == sc) for sc in TEST},
                      features=dict(sorted(res.items(),
                                           key=lambda kv: -abs(kv[1]["cohen_d"]
                                                               if np.isfinite(kv[1]["cohen_d"]) else 0))))
    return out


# --------------------------------------------------------------------------- #
# 5. scene composition: prims, materials/MDL roles, dressing calls
# --------------------------------------------------------------------------- #
SCENE_FILES = {}
for p in glob.glob(os.path.join(REPO, "scenes/*/scene*.py")):
    b = os.path.basename(p)
    m = re.match(r"(scene[0-9A-Z]+[0-9]*)_", b)
    if m:
        SCENE_FILES.setdefault(m.group(1), []).append(p)


def heightmap_meta():
    out = {}
    for arm in ("260819_main_on", "260819_main_off", "260820_ctrloff"):
        for p in glob.glob(os.path.join(round_dir_or_flat(arm),
                                        "*", "*", "heightmap_meta.json")):
            m = json.load(open(p))
            out.setdefault(m["scene"], {})[arm] = dict(
                n_prims=m.get("n_prims"), z_min=m.get("z_min"), z_max=m.get("z_max"),
                arm_config=m.get("arm_config"),
                finite_frac=round(m.get("n_finite", 0) / max(m.get("n_total", 1), 1), 4))
    return out


DRESS_PAT = re.compile(r"\b(build_(leaf\w*|scatter\w*|litter\w*|debris\w*|planter\w*|prop\w*|"
                       r"tree|hedge|shrub|grass|turf|flower\w*|pot\w*|bench|bollard|sign\w*|"
                       r"cue\w*|railing|handrail|warning\w*|mural|puddle|snow\w*|moss\w*))\s*\(")
CUE_PAT = re.compile(r"\bcue_[a-z_]+")
MDL_PAT = re.compile(r"(?:TEX|LOOK_ROLE|sc\.TEX)\[[\"']([a-z0-9_]+)[\"']\]|"
                     r"role\s*=\s*[\"']([a-z_]+)[\"']|bind_\w*\(\s*[^,]+,\s*[\"']([a-z0-9_]+)[\"']")


def source_audit():
    out = {}
    for sc, paths in SCENE_FILES.items():
        p = sorted(paths)[-1]
        src = open(p, encoding="utf-8", errors="replace").read()
        code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
        dress = {}
        for m in DRESS_PAT.finditer(code):
            dress[m.group(1)] = dress.get(m.group(1), 0) + 1
        cues = sorted(set(CUE_PAT.findall(code)))
        mats = set()
        for m in MDL_PAT.finditer(code):
            mats.update(x for x in m.groups() if x)
        out[sc] = dict(path=os.path.relpath(p, REPO), n_lines=len(src.splitlines()),
                       dressing_calls=dict(sorted(dress.items(), key=lambda kv: -kv[1])),
                       n_dressing_call_sites=int(sum(dress.values())),
                       cue_toggles=cues, materials_referenced=sorted(mats))
    return out


def camera_audit():
    out = {}
    for sc in TEST + ["sceneC1", "sceneC4", "sceneN3"]:
        fr = [f for f in FRAMES if f["scene_id"] == sc and f["toggle_state"] == "on"]
        if not fr:
            continue
        h = np.array([f["cam"]["h_rel"] for f in fr])
        d = np.array([f["cam"]["d"] for f in fr])
        out[sc] = dict(n_on_frames=len(fr),
                       conds=sorted({f["cond"] for f in fr}),
                       rounds=sorted({f["round"] for f in fr}),
                       h_min=float(h.min()), h_max=float(h.max()), h_mean=float(h.mean()),
                       frac_h_below_0p6=float((h < 0.6).mean()),
                       d_min=float(d.min()), d_max=float(d.max()), d_mean=float(d.mean()),
                       tiers={t: sum(1 for f in fr if f["tier"] == t)
                              for t in sorted({f["tier"] for f in fr})})
    return out


# --------------------------------------------------------------------------- #
CTRL = os.path.join(REPO, "experiments/nightrun_0820/ctrl_dressing")


def _pf(path):
    out = {}
    with open(path) as fh:
        for r in csv.DictReader(fh):
            out[r["frame_id"]] = dict(scene=r["scene_id"],
                                      p=np.array([float(r[f"p_{c}"]) for c in CELLS]))
    return out


def ctrl_arm_audit():
    """Old OFF (hazard+dressing removed) vs new OFF (`keep_dressing`, hazard only) for BOTH
    arms, localised to camera pose and to light condition.  `eval_*_depth_*` is the GPU-1
    output of WEEKEND_BRIEF sec 5.1; RGB is the CTRL_TABLE.md source."""
    out = {}
    for model, tag in (("rgb", ""), ("depth", "_depth")):
        for arm in ("old", "new"):
            for sc in ("sceneC2", "sceneN3"):
                per_seed = []
                for s in SEEDS:
                    p = os.path.join(CTRL, f"eval_{arm}{tag}_s{s}/per_frame_off.csv")
                    if not os.path.exists(p):
                        per_seed.append(None)
                        continue
                    rows = {k: v for k, v in _pf(p).items() if v["scene"] == sc}
                    fired, cells, poses_f, poses, by_cond = 0, 0, set(), set(), {}
                    for fid, r in rows.items():
                        cam = os.path.basename(fid).split("__")[-1][:4]
                        cond = os.path.basename(fid).split("__")[0]
                        n = int((r["p"] >= TAU).sum())
                        cells += n
                        poses.add(cam)
                        by_cond.setdefault(cond, []).append(n > 0)
                        if n:
                            fired += 1
                            poses_f.add(cam)
                    per_seed.append(dict(n=len(rows), fa_frame=fired / max(1, len(rows)),
                                         cells_per_frame=cells / max(1, len(rows)),
                                         poses_fired=sorted(poses_f), n_poses=len(poses),
                                         fa_by_cond={k: float(np.mean(v))
                                                     for k, v in sorted(by_cond.items())}))
                ok = [x for x in per_seed if x]
                out[f"{model}_{arm}off_{sc}"] = dict(
                    per_seed=per_seed,
                    fa_frame_3seed=float(np.mean([x["fa_frame"] for x in ok])) if ok else None,
                    fa_frame_halfrange=float((max(x["fa_frame"] for x in ok)
                                              - min(x["fa_frame"] for x in ok)) / 2) if ok else None,
                    poses_fired_union=sorted({c for x in ok for c in x["poses_fired"]}),
                    poses_fired_per_seed=[len(x["poses_fired"]) for x in ok])
            # twin delta
            for sc in ("sceneC2", "sceneN3"):
                vals = []
                for s in SEEDS:
                    p = os.path.join(CTRL, f"twin_{arm}{tag}_s{s}/twin_pairs.csv")
                    if not os.path.exists(p):
                        continue
                    v = [float(r["delta_frame"]) for r in csv.DictReader(open(p))
                         if r["scene_id"] == sc and r["kept"] == "True"
                         and r["delta_frame"] not in ("", "nan")]
                    if v:
                        vals.append(float(np.mean(v)))
                if vals:
                    out[f"{model}_{arm}off_{sc}_twin_dframe"] = dict(
                        seeds=vals, mean=float(np.mean(vals)),
                        half_range=float((max(vals) - min(vals)) / 2))
    # dressing share of the response, per model  (1 - new/old)
    for model in ("rgb", "depth"):
        a = out.get(f"{model}_oldoff_sceneC2_twin_dframe")
        b = out.get(f"{model}_newoff_sceneC2_twin_dframe")
        if a and b:
            out[f"{model}_sceneC2_dressing_share_of_response"] = float(1 - b["mean"] / a["mean"])
    # QC: the on-arm rows and the old-off rows must reproduce the frozen v2 eval exactly
    qc = {}
    for model, tag in (("rgb", ""), ("depth", "_depth")):
        for s in SEEDS:
            ref = _pf(os.path.join(RUNS, f"{model}_s{s}/eval_test/per_frame.csv"))
            devs = []
            for arm in ("old", "new"):
                p = os.path.join(CTRL, f"eval_{arm}{tag}_s{s}/per_frame_on.csv")
                if os.path.exists(p):
                    devs += [float(np.abs(v["p"] - ref[k]["p"]).max())
                             for k, v in _pf(p).items() if k in ref]
            p = os.path.join(CTRL, f"eval_old{tag}_s{s}/per_frame_off.csv")
            if os.path.exists(p):
                devs += [float(np.abs(v["p"] - ref[k]["p"]).max())
                         for k, v in _pf(p).items() if k in ref]
            qc[f"{model}_s{s}_max_abs_dp_vs_frozen"] = max(devs) if devs else None
            qc[f"{model}_s{s}_n_rows_checked"] = len(devs)
    out["qc"] = qc
    return out


def c2_cond_split():
    """sceneC2 off-arm FA split by light condition on the frozen v2 test eval.
    Discriminates the 'out-of-distribution illumination' hypothesis: L2 is absent from
    training entirely, L3 appears in 16 train frames, L7 is fully in-distribution."""
    out = {"train_frames_by_cond": {}, "cond_scene_map": {}}
    tr = set(SPLIT["train"])
    for f in FRAMES:
        if f["scene_id"] in tr:
            out["train_frames_by_cond"][f["cond"]] = out["train_frames_by_cond"].get(f["cond"], 0) + 1
    for f in FRAMES:
        out["cond_scene_map"].setdefault(f["cond"], set()).add(f["scene_id"])
    out["cond_scene_map"] = {k: sorted(v) for k, v in sorted(out["cond_scene_map"].items())}
    for m in MODELS:
        acc = {}
        for s in SEEDS:
            for fid, r in PF[(m, s)].items():
                if r["scene"] != "sceneC2" or r["toggle"] != "off":
                    continue
                cond = os.path.basename(fid).split("__")[0]
                acc.setdefault((cond, s), []).append(int((r["p"] >= TAU).sum()) > 0)
        conds = sorted({c for c, _ in acc})
        out[m] = {c: dict(per_seed=[float(np.mean(acc[(c, s)])) for s in SEEDS],
                          mean=float(np.mean([np.mean(acc[(c, s)]) for s in SEEDS])))
                  for c in conds}
    return out


def _rank(x):
    x = np.asarray(x, float)
    o = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[o[j + 1]] == x[o[i]]:
            j += 1
        r[o[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return r


def _pearson(a, b):
    a = np.asarray(a, float) - np.mean(a)
    b = np.asarray(b, float) - np.mean(b)
    d = np.sqrt(float((a * a).sum()) * float((b * b).sum()))
    return float((a * b).sum() / d) if d > 0 else float("nan")


def _spearman(a, b, n_perm=20000, seed=42):
    ra, rb = _rank(a), _rank(b)
    rho = _pearson(ra, rb)
    rng = np.random.default_rng(seed)
    hits = sum(1 for _ in range(n_perm)
               if abs(_pearson(rng.permutation(ra), rb)) >= abs(rho) - 1e-12)
    return rho, (hits + 1) / (n_perm + 1)


def farband_starvation(per_frame):
    """Discriminator #2 for hypothesis H2: does far-band PIXEL SHARE predict far-cell firing
    across all 136 distinct OFF-arm inputs, or only in the extreme tail?"""
    off = [r for r in per_frame if r["arm"] == "off"]
    out = {}
    for m in MODELS:
        far, y, sc = [], [], []
        for r in off:
            fid = r["frame_id"]
            p = np.mean([PF[(m, s)][fid]["p"] for s in SEEDS], axis=0)
            far.append(r["frac_band3a"] + r["frac_band3b"])
            y.append(float(p[10:20].max()))       # the ten far cells (bands 3a + 3b)
            sc.append(r["scene"])
        rho, pv = _spearman(far, y)
        order = np.argsort(far)
        groups = {"bottom10": order[:10], "rank11_30": order[10:30],
                  "rank31_105": order[30:105], "top31": order[105:]}
        out[m] = dict(n=len(far), spearman_rho=rho, perm_p=pv,
                      group_means={k: dict(n=len(v),
                                           mean_max_far_p=float(np.mean([y[i] for i in v])),
                                           n_over_tau=int(sum(y[i] >= TAU for i in v)),
                                           scenes={s: int(sum(1 for i in v if sc[i] == s))
                                                   for s in TEST if any(sc[i] == s for i in v)})
                                   for k, v in groups.items()},
                      bottom10=[dict(scene=sc[i], frame_id=off[i]["frame_id"],
                                     far_share=far[i], max_far_p=y[i]) for i in order[:10]])
    return out


def main():
    REP["purpose"] = ("CPU-3 / WEEKEND_BRIEF_0823 sec 6.3 -- systematic difference audit of "
                      "sceneC2 vs the other test scenes.  No scene edited.")
    REP["tau"] = TAU
    REP["depth_clip_m"] = DEPTH_CLIP_M
    REP["test_scenes"] = TEST
    REP["census"] = census()
    REP["depth_hash_check"] = {sc: depth_hash_check(sc) for sc in ("sceneC2", "sceneN3", "scene05")}
    REP["fa_by_pose"] = fa_by_pose()
    ds, pf = depth_stats()
    REP["depth_stats"] = ds
    REP["feature_discrimination"] = feature_discrimination(pf)
    REP["farband_starvation"] = farband_starvation(pf)
    REP["heightmap_meta"] = heightmap_meta()
    REP["source_audit"] = source_audit()
    REP["camera_audit"] = camera_audit()
    REP["ctrl_arm_audit"] = ctrl_arm_audit()
    REP["c2_cond_split"] = c2_cond_split()
    with open(os.path.join(OUT, "c2_audit_numbers.json"), "w") as fh:
        json.dump(REP, fh, indent=1, default=float)
    return REP


if __name__ == "__main__":
    R = main()
    print("wrote", os.path.join(OUT, "c2_audit_numbers.json"))
