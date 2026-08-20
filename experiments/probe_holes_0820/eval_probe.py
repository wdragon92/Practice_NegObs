#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval_probe.py — zero-shot evaluation driver for the C1 hole probe.

Three steps, selected by `--step`, all of them reusing the frozen mainrun_0819
tooling rather than reimplementing it:

  split   write `split_probe.json` — every probe scene in ONE subset, so
          `eval_polar --subset probe` scores all 144 frames together.
  tiers   the V / E / H distribution table the brief asks for, straight off the
          probe manifest, per scene and per condition.
  eval    the nine FROZEN v2 checkpoints (rgb / depth / b2 x seeds 42 / 43 / 44)
          run over the probe manifest, plus twin analysis, plus four
          representative panels each, plus the two probe-specific tables:
            - the per-scene zero-shot recall / FA / twin-delta table, and
            - probeH2's ADJACENT HAZARD-FREE SECTOR firing rate, which the brief
              asks for by name and which no existing script computes.

NOTHING IN THIS FILE TRAINS. Checkpoints are read-only inputs (brief C1:
"훈련 편입 절대 금지 — 평가 전용"). There is no optimiser, no backward pass and
no write into any `runs/` directory.

WHY A ONE-SUBSET SPLIT
----------------------
`make_split.py` exists to build a scene-unit train/val/test division with a
proof report. There is nothing to divide here: the probe is 3 scenes evaluated
by 9 checkpoints that have already been trained and frozen elsewhere, so every
frame belongs to the same evaluation set. Writing `{"probe": [...3 scenes...]}`
and passing `--subset probe` is the smallest thing that makes `PolarGridDataset`
yield all of them. `train` / `val` / `test` are left EMPTY on purpose: an empty
`val` makes `--tau-star auto` impossible, which is exactly right, because tau_op
is FROZEN at 0.5 by absolute rule 3 and re-fitting it on probe data would be a
new hyper-parameter search the brief forbids.

Run everything with PYTHONNOUSERSITE=1 (this machine's ~/.local shadows env_seg).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MAIN = os.path.join(REPO, "experiments", "mainrun_0819")
CODE = os.path.join(MAIN, "code")
B2 = os.path.join(MAIN, "b2_polar")
sys.path.insert(0, CODE)

# The nine frozen v2 checkpoints. Paths, not a search: a probe that silently
# picked up `mainrun_0819/runs/rgb_s42` (recipe v1) would report a v1 number
# under a v2 heading.
CKPT_ROOT = os.path.join(REPO, "experiments", "dayrun_0820", "runs", "v2")
MODELS = ("rgb", "depth", "b2")
SEEDS = (42, 43, 44)
TAU_OP = 0.5                       # FROZEN (absolute rule 3). Never fitted here.
PROBE_SUBSET = "probe"
PROBE_SCENES = ("probeH1", "probeH2", "probeH3")
# The scene whose measurement is "did it fire in the hazard-free sector next
# door" — see probeH2_offpath_hole.py's header.
OFFPATH_SCENE = "probeH2"


def _run(cmd, log=None, dry=False, env=None):
    line = " ".join(str(c) for c in cmd)
    if dry:
        print(f"  [dry] {line}")
        return 0
    print(f"  [run] {line[:150]}", flush=True)
    t0 = time.time()
    with open(log, "a") if log else open(os.devnull, "w") as fh:
        rc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT,
                            env=env or env_for()).returncode
    print(f"        rc={rc} {time.time() - t0:.0f}s", flush=True)
    return rc


def pybin():
    return "/home/vislab/miniconda3/envs/env_seg/bin/python"


def env_for(cpu=False, b2=False):
    e = dict(os.environ)
    e.update(PYTHONNOUSERSITE="1", PYTHONUNBUFFERED="1", OMP_NUM_THREADS="8")
    if b2:
        e["HF_HUB_OFFLINE"] = "1"          # the b2 factory must not reach out
    if cpu:
        e["CUDA_VISIBLE_DEVICES"] = ""     # `train_polar.guard_gpu_free` -> cpu
    return e


# ===========================================================================
# step: split
# ===========================================================================
def step_split(a):
    man = json.load(open(a.manifest))
    scenes = sorted({f["scene_id"] for f in man["frames"]})
    unknown = [s for s in scenes if not s.startswith("probe")]
    if unknown:
        raise SystemExit(f"[split] the probe manifest carries non-probe scenes "
                         f"{unknown}. That would evaluate corpus frames under a "
                         f"probe heading — refusing.")
    split = {"train": [], "val": [], "test": [], PROBE_SUBSET: scenes}
    with open(a.split, "w") as f:
        json.dump(split, f, indent=1)
    print(f"[split] {len(scenes)} scene(s) -> subset '{PROBE_SUBSET}' "
          f"({len(man['frames'])} frames) -> {a.split}")
    print(f"[split] train/val/test are EMPTY on purpose: tau_op stays frozen at "
          f"{TAU_OP} and nothing may be fitted on probe data.")
    return 0


# ===========================================================================
# step: tiers
# ===========================================================================
def step_tiers(a):
    man = json.load(open(a.manifest))
    frames = man["frames"]
    rows = {}
    for f in frames:
        key = (f["scene_id"], f["toggle_state"], f.get("cond") or "?")
        r = rows.setdefault(key, dict(n=0, V=0, E=0, H=0, other=0, pos=0))
        r["n"] += 1
        t = f.get("tier")
        r[t if t in ("V", "E", "H") else "other"] += 1
        if any(v > 0.5 for v in f["polar_gt"]):
            r["pos"] += 1

    out = ["# TIER_TABLE — C1 hole probe, label distribution",
           "",
           f"manifest: `{os.path.relpath(a.manifest, REPO)}` · grid "
           f"**{man['meta']['grid_version']}** ({man['meta']['n_cells']} cells) · "
           f"rounds {man['meta']['rounds']} · seed {man['meta'].get('seed')}",
           "",
           "Tier is a property of the HAZARD-ON frame (V = interior pixels visible, "
           "E = rim only, H = the drop contributes no pixel at all). Off-arm rows "
           "carry no hazard and are listed only so the pair is visibly complete.",
           "",
           "| scene | arm | cond | frames | GT-positive | V | E | H | other |",
           "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for key in sorted(rows):
        s, arm, cond = key
        r = rows[key]
        out.append(f"| {s} | {arm} | {cond} | {r['n']} | {r['pos']} | "
                   f"{r['V']} | {r['E']} | {r['H']} | {r['other']} |")

    tot = {}
    for (s, arm, _c), r in rows.items():
        t = tot.setdefault((s, arm), dict(n=0, V=0, E=0, H=0, other=0, pos=0))
        for k in t:
            t[k] += r[k]
    out += ["", "## per scene-arm", "",
            "| scene | arm | frames | GT-positive | V | E | H | other |",
            "|---|---|---:|---:|---:|---:|---:|---:|"]
    for key in sorted(tot):
        r = tot[key]
        out.append(f"| {key[0]} | {key[1]} | {r['n']} | {r['pos']} | {r['V']} | "
                   f"{r['E']} | {r['H']} | {r['other']} |")

    out += ["", "## what to look at first", "",
            "* **probeH3 should be almost entirely H.** Its occlusion is computed "
            "for all eight frozen camera draws (see the scene header); an E or V "
            "row there means the render disagrees with the geometry and the "
            "occlusion audit needs re-reading before any recall number is quoted.",
            "* **probeH1 should be V-dominant** and should carry band-1 positives "
            "on cuts 1 and 2 of every condition (6 frames per arm).",
            "* **A GT-positive count below the frame count on an ON row** means "
            "some cut put the hole outside the 12 m grid; those frames are "
            "negatives, not misses, and `frame_recall_*` already excludes them.",
            ""]
    open(a.out, "w").write("\n".join(out))
    print(f"[tiers] {len(frames)} frames -> {a.out}")
    for k in sorted(tot):
        r = tot[k]
        print(f"  {k[0]:9s} {k[1]:3s} n={r['n']:3d} pos={r['pos']:3d} "
              f"V={r['V']:3d} E={r['E']:3d} H={r['H']:3d} other={r['other']:3d}")
    return 0


# ===========================================================================
# step: eval
# ===========================================================================
def ckpt_path(model, seed):
    return os.path.join(CKPT_ROOT, f"{model}_s{seed}", "best.pt")


def step_eval(a):
    missing = [ckpt_path(m, s) for m in MODELS for s in SEEDS
               if not os.path.isfile(ckpt_path(m, s))]
    if missing and not a.dry_run:
        raise SystemExit("[eval] frozen checkpoint(s) absent:\n  "
                         + "\n  ".join(missing))

    os.makedirs(a.out, exist_ok=True)
    results = {}
    for model in MODELS:
        for seed in SEEDS:
            tag = f"{model}_s{seed}"
            ev = os.path.join(a.out, tag)
            os.makedirs(ev, exist_ok=True)
            script = (os.path.join(B2, "eval_b2_polar.py") if model == "b2"
                      else os.path.join(CODE, "eval_polar.py"))
            inp = "rgb" if model in ("rgb", "b2") else "depth"
            cmd = [pybin(), script,
                   "--manifest", a.manifest, "--split", a.split,
                   "--subset", PROBE_SUBSET, "--input", inp,
                   "--ckpt", ckpt_path(model, seed), "--out", ev,
                   # tau_op AND tau_star are both pinned: `--tau-star auto`
                   # would try to fit on `val`, which is deliberately empty.
                   "--tau-op", str(TAU_OP), "--tau-star", str(TAU_OP),
                   "--tau-sweep", "0.3,0.5,0.7",
                   "--n-boot", str(a.n_boot), "--grid", a.grid]
            print(f"[eval] {tag} (zero shot, frozen ckpt, nothing trains)")
            genv = env_for(cpu=a.cpu, b2=(model == "b2"))
            rc = _run(cmd, a.log, a.dry_run, genv)
            if rc:
                results[tag] = dict(error=f"eval rc={rc}")
                continue

            cenv = env_for(cpu=True)          # the post-steps are numpy only
            pf = os.path.join(ev, "per_frame.csv")
            _run([pybin(), os.path.join(CODE, "split_per_frame.py"),
                  "--per-frame", pf, "--out-dir", ev], a.log, a.dry_run, cenv)
            # `--tol 1e-6` is the DEFAULT, i.e. "identical within float noise",
            # and it is stated explicitly to make the point: the D20 pairing
            # tolerance of 0.15 m — the one nightrun B5 is re-checking because
            # it lets pairs through whose ground_z actually moved — is NOT used
            # here and must not be needed, because these scenes are built so the
            # toggle cannot move ground_z under a camera at all. If this run
            # reports excluded pairs, that is a finding about the scenes and
            # goes in the report; it does not get fixed by widening the tol.
            _run([pybin(), os.path.join(CODE, "twin_analysis.py"),
                  "--per-frame-on", os.path.join(ev, "per_frame_on.csv"),
                  "--per-frame-off", os.path.join(ev, "per_frame_off.csv"),
                  "--manifest", a.manifest, "--out", os.path.join(ev, "twin"),
                  "--n-boot", str(a.n_boot), "--grid", a.grid, "--tol", "1e-6"],
                 a.log, a.dry_run, cenv)
            _run([pybin(), os.path.join(CODE, "make_viz.py"),
                  "--per-frame", pf, "--manifest", a.manifest,
                  "--out", os.path.join(ev, "viz"), "--n", "4",
                  "--grid", a.grid], a.log, a.dry_run, cenv)
            if not a.dry_run:
                results[tag] = collect(ev, a.manifest, a.grid)

    if a.dry_run:
        print("[eval] dry run — no table written")
        return 0
    write_table(a.table, results, a.manifest, a.grid)
    print(f"[eval] table -> {a.table}")
    return 0


def collect(ev, manifest, grid_path):
    """Per-checkpoint numbers: the eval's own metrics.json, the twin markdown,
    and the two probe-specific measurements computed here."""
    import gridspec
    out = {}
    mj = os.path.join(ev, "metrics.json")
    if os.path.isfile(mj):
        out["metrics"] = json.load(open(mj))
    tw = os.path.join(ev, "twin", "twin_analysis.md")
    out["twin_md"] = os.path.relpath(tw, REPO) if os.path.isfile(tw) else None
    pf = os.path.join(ev, "per_frame.csv")
    if os.path.isfile(pf):
        g = gridspec.load(grid_path)
        out["per_scene"] = per_scene_rates(pf, g)
        out["adjacent"] = adjacent_sector_firing(pf, g, OFFPATH_SCENE)
    return out


def _read_pf(path):
    rows = []
    with open(path) as f:
        rd = csv.DictReader(f)
        cells = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        for r in rd:
            rows.append(dict(
                frame_id=r["frame_id"], scene=r["scene_id"], tier=r["tier"],
                arm=r["toggle_state"],
                p=[float(r[f"p_{c}"]) for c in cells],
                g=[float(r[f"g_{c}"]) for c in cells]))
    return rows, cells


def per_scene_rates(pf, g):
    """Frame recall by tier and off-arm frame FA, per probe scene, at tau_op."""
    rows, _cells = _read_pf(pf)
    out = {}
    for s in PROBE_SCENES:
        sel = [r for r in rows if r["scene"] == s]
        if not sel:
            continue
        on = [r for r in sel if r["arm"] == "on"]
        off = [r for r in sel if r["arm"] == "off"]
        haz = [r for r in on if any(v > 0.5 for v in r["g"])]
        d = dict(n=len(sel), n_on=len(on), n_off=len(off), n_haz=len(haz))
        det = [r for r in haz
               if any(p >= TAU_OP and gv > 0.5 for p, gv in zip(r["p"], r["g"]))]
        d["frame_recall"] = round(len(det) / len(haz), 4) if haz else None
        for t in ("V", "E", "H"):
            sub = [r for r in haz if r["tier"] == t]
            hit = [r for r in sub
                   if any(p >= TAU_OP and gv > 0.5
                          for p, gv in zip(r["p"], r["g"]))]
            d[f"recall_{t}"] = round(len(hit) / len(sub), 4) if sub else None
            d[f"n_{t}"] = len(sub)
        fa = [r for r in off if any(p >= TAU_OP for p in r["p"])]
        d["frame_fa_off"] = round(len(fa) / len(off), 4) if off else None
        out[s] = d
    return out


def adjacent_sector_firing(pf, g, scene):
    """probeH2's headline: the false-firing rate on hazard-free sectors ADJACENT
    to the answer sector, within the same band.

    The brief asks for this by name ("인접 빈 섹터의 오발화율 별도 보고") and no
    existing script produces it, because no corpus scene has a hazard that
    occupies one lateral sector while leaving its neighbours clean.

    Definition, per hazard-ON frame:
      answer cells  = cells with GT = 1
      answer band   = the set of bands those cells fall in
      adjacent set  = cells in an answer band whose sector is +-1 from an answer
                      sector AND whose own GT is 0
      fired         = p >= tau_op on an adjacent cell
    Reported as cell-level rate and frame-level rate. `far_set` is the same
    measurement on cells >= 2 sectors away, as the contrast: an adjacent-only
    excess is spatial blur, an equal rate everywhere is a scene-level prior.
    """
    rows, cells = _read_pf(pf)
    sel = [r for r in rows if r["scene"] == scene and r["arm"] == "on"]
    n_adj = n_adj_fire = n_far = n_far_fire = 0
    n_frames = n_frames_fire = 0
    ns = g.n_sectors
    for r in sel:
        pos = [i for i, v in enumerate(r["g"]) if v > 0.5]
        if not pos:
            continue
        # Adjacency is resolved WITHIN each answer band, never across bands: a
        # hazard positive at (band 2, sector B) says nothing about which sectors
        # of band 3a are its neighbours, and pooling the sector sets across
        # bands would classify a genuinely distant cell as adjacent.
        secs_by_band = {}
        for i in pos:
            secs_by_band.setdefault(g.band_of[i], set()).add(g.sector_of[i])
        adj, far = [], []
        for i in range(g.n_cells):
            b = g.band_of[i]
            if r["g"][i] > 0.5 or b not in secs_by_band:
                continue
            dmin = min(abs(g.sector_of[i] - s) for s in secs_by_band[b])
            (adj if dmin == 1 else far).append(i)      # dmin == 0 is impossible
        fired = [i for i in adj if r["p"][i] >= TAU_OP]
        n_adj += len(adj); n_adj_fire += len(fired)
        n_far += len(far)
        n_far_fire += sum(1 for i in far if r["p"][i] >= TAU_OP)
        n_frames += 1
        n_frames_fire += int(bool(fired))
    if not n_frames:
        return None
    return dict(
        scene=scene, n_frames=n_frames, n_sectors=ns,
        adj_cells=n_adj, adj_fired=n_adj_fire,
        adj_cell_rate=round(n_adj_fire / n_adj, 4) if n_adj else None,
        adj_frame_rate=round(n_frames_fire / n_frames, 4),
        far_cells=n_far, far_fired=n_far_fire,
        far_cell_rate=round(n_far_fire / n_far, 4) if n_far else None)


def _f(v, nd=3):
    return "n/a" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def write_table(path, results, manifest, grid_path):
    man = json.load(open(manifest))
    L = ["# PROBE_TABLE — C1 hole-type zero-shot probe",
         "",
         "**Evaluation only. Nothing here trained, and no probe frame may ever "
         "enter training** (OVERNIGHT_BRIEF_0820 §4 C1).",
         "",
         f"* manifest `{os.path.relpath(manifest, REPO)}` — "
         f"{len(man['frames'])} frames, grid **{man['meta']['grid_version']}** "
         f"({man['meta']['n_cells']} cells), rounds {man['meta']['rounds']}",
         f"* checkpoints: the nine FROZEN recipe-v2 runs under "
         f"`{os.path.relpath(CKPT_ROOT, REPO)}` (rgb/depth/b2 x seeds 42/43/44)",
         f"* tau_op = **{TAU_OP}**, frozen by absolute rule 3 and NOT re-fitted "
         f"on probe data (`val` is deliberately empty in `split_probe.json`)",
         "",
         "## 1. headline — all probe frames as one subset",
         "",
         "| ckpt | n frames | cell F1 | frame det | recall V | recall E | "
         "recall H | frame FA (off) | cell FPR (off) |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for tag in sorted(results):
        r = results[tag]
        if "error" in r:
            L.append(f"| {tag} | ERROR: {r['error']} | | | | | | | |")
            continue
        # eval_polar's metrics.json nests the point estimates under
        # point.op (tau_op) and point.star (tau*); both taus are 0.5 here.
        mj = r.get("metrics") or {}
        m = ((mj.get("point") or {}).get("op")) or {}
        c = mj.get("counts") or {}
        L.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            tag, c.get("n_frames", "?"),
            _f(m.get("cell_f1")), _f(m.get("frame_det_rate")),
            _f(m.get("frame_recall_V")), _f(m.get("frame_recall_E")),
            _f(m.get("frame_recall_H")), _f(m.get("frame_fa_off")),
            _f(m.get("cell_fpr_off"))))

    L += ["", "## 2. per scene (tau_op = %.2f)" % TAU_OP, "",
          "| ckpt | scene | n(on/off) | hazard frames | frame recall | "
          "V | E | H | frame FA (off) |",
          "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for tag in sorted(results):
        for s, d in (results[tag].get("per_scene") or {}).items():
            L.append("| {} | {} | {}/{} | {} | {} | {} ({}) | {} ({}) | {} ({}) | {} |"
                     .format(tag, s, d["n_on"], d["n_off"], d["n_haz"],
                             _f(d["frame_recall"]), _f(d["recall_V"]), d["n_V"],
                             _f(d["recall_E"]), d["n_E"], _f(d["recall_H"]),
                             d["n_H"], _f(d["frame_fa_off"])))

    L += ["", f"## 3. {OFFPATH_SCENE} — adjacent hazard-free sector firing", "",
          "The corridor-preserving composition: the hazard sits in ONE lateral "
          "sector and the sectors beside it, in the same band, carry no hazard. "
          "`adjacent` = one sector away, `far` = two or more. An adjacent rate "
          "far above the far rate is angular blur around a correct answer; an "
          "equal rate is a scene-level prior firing.",
          "",
          "| ckpt | frames | adj cells | adj fired | adj cell rate | "
          "adj frame rate | far cell rate |",
          "|---|---:|---:|---:|---:|---:|---:|"]
    for tag in sorted(results):
        d = results[tag].get("adjacent")
        if not d:
            L.append(f"| {tag} | n/a | | | | | |")
            continue
        L.append("| {} | {} | {} | {} | {} | {} | {} |".format(
            tag, d["n_frames"], d["adj_cells"], d["adj_fired"],
            _f(d["adj_cell_rate"]), _f(d["adj_frame_rate"]),
            _f(d["far_cell_rate"])))

    L += ["", "## 4. twin analysis", "",
          "One `twin_analysis.md` per checkpoint, run at the DEFAULT pose "
          "tolerance `--tol 1e-6` (identical within float noise). The D20 "
          "rescue tolerance of 0.15 m — the one nightrun B5 is re-checking, "
          "because it admits pairs whose `ground_z` genuinely moved — is NOT "
          "used and must not be needed: these scenes are built so the hazard "
          "toggle cannot move `ground_z` under any camera "
          "(`probe_common.twin_audit`, asserted pre-boot in both arms). If a "
          "run reports excluded pairs, that is a finding about the scenes and "
          "goes in the report; it does not get fixed by widening the tolerance.",
          ""]
    for tag in sorted(results):
        L.append(f"* `{tag}` -> `{results[tag].get('twin_md') or 'MISSING'}`")

    L += ["", "## 5. how to read a null result", "",
          "A collapse of H recall on **probeH3** while V/E survive on probeH1/H2 "
          "is not a failed probe: it is the finding that the H-tier claim is "
          "drop-TYPE bound, and it belongs in the paper's limitations. A "
          "collapse everywhere including V says the checkpoints are scene-bound "
          "rather than type-bound. Both are Tier-3 outcomes under the brief's "
          "acceptance rule ('렌더까지만 되고 평가가 실패해도, 산출물과 원인이 "
          "기록되면 Tier3 성립').", ""]
    open(path, "w").write("\n".join(L))
    json.dump(results, open(os.path.splitext(path)[0] + ".json", "w"), indent=1)


# ===========================================================================
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--step", required=True,
                   choices=["split", "tiers", "eval"])
    p.add_argument("--manifest", default=os.path.join(
        HERE, "dataset_manifest_probe.json"))
    p.add_argument("--split", default=os.path.join(HERE, "split_probe.json"))
    p.add_argument("--out", default=os.path.join(HERE, "eval"))
    p.add_argument("--table", default=os.path.join(HERE, "PROBE_TABLE.md"))
    p.add_argument("--grid", default="gridspec_v1.json")
    p.add_argument("--n-boot", type=int, default=10000)
    p.add_argument("--log", default=os.path.join(HERE, "logs", "probe.log"))
    p.add_argument("--cpu", action="store_true",
                   help="force the evals onto CPU (CUDA_VISIBLE_DEVICES='')")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)
    if a.cpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.makedirs(os.path.dirname(os.path.abspath(a.log)), exist_ok=True)
    return {"split": step_split, "tiers": step_tiers, "eval": step_eval}[a.step](a)


if __name__ == "__main__":
    sys.exit(main())
