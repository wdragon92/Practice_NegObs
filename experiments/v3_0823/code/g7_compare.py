#!/usr/bin/env python3
"""G7 repair, step 4 — before/after tier ledger + the s12-artefact gate.

BEFORE = experiments/dayrun_0820/annotations/labels_boost_{h,e,e2}.json (frozen)
AFTER  = experiments/v3_0823/annotations/labels_boost_{e,e2}_g7fix.json
         (boost_h has no fused-instrument scene, so BEFORE == AFTER by definition
          and the frozen file is carried over unchanged)
"""
import json, os, sys, collections

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
OLD = os.path.join(REPO, "experiments/dayrun_0820/annotations")
NEW = os.path.join(REPO, "experiments/v3_0823/annotations")
TIERS = ["V", "E", "H", "H_weak", "none_in_fov", "off"]
SPLIT = json.load(open(os.path.join(REPO, "experiments/dayrun_0820/split_v2_full.json")))
SPLIT_OF = {s: k for k, v in SPLIT.items() for s in v}


def load(p):
    return json.load(open(p))


def tiercount(L):
    c = collections.Counter()
    for k, v in L["frames"].items():
        arm, scene, _ = k.split("/", 2)
        c[(scene, arm, v["tier_strict"])] += 1
    return c


def fp_of(L):
    return {(r["scene"], r["arm"]): r for r in L["scene_footprint"]}


def main():
    rows, migr, gate_rows = [], [], []
    for band in ("e", "e2"):
        O = load(os.path.join(OLD, f"labels_boost_{band}.json"))
        N = load(os.path.join(NEW, f"labels_boost_{band}_g7fix.json"))
        co, cn = tiercount(O), tiercount(N)
        fo, fn = fp_of(O), fp_of(N)
        scenes = sorted({s for s, a, t in co})
        for sc in scenes:
            for arm in ("on", "off"):
                bo = {t: co[(sc, arm, t)] for t in TIERS if co[(sc, arm, t)]}
                bn = {t: cn[(sc, arm, t)] for t in TIERS if cn[(sc, arm, t)]}
                ro, rn = fo.get((sc, arm), {}), fn.get((sc, arm), {})
                rows.append(dict(band=band, scene=sc, arm=arm,
                                 split=SPLIT_OF.get(sc, "?"),
                                 before=bo, after=bn, changed=(bo != bn),
                                 hm_before=f"{ro.get('hm_source')}/{ro.get('hm_source_off')}",
                                 hm_after=f"{rn.get('hm_source')}/{rn.get('hm_source_off')}",
                                 raw_before=ro.get("cells_raw"), raw_after=rn.get("cells_raw"),
                                 kept_before=ro.get("cells_kept_max"), kept_after=rn.get("cells_kept_max"),
                                 md_before=ro.get("max_diff"), md_after=rn.get("max_diff")))
        # per-frame migrations
        mm = collections.Counter()
        for k in O["frames"]:
            a, b = O["frames"][k]["tier_strict"], N["frames"][k]["tier_strict"]
            if a != b:
                mm[(k.split("/")[1], f"{a}->{b}")] += 1
        for (sc, t), n in sorted(mm.items()):
            migr.append((band, sc, t, n))
        # gate: strict-H frames whose hazard visibly contributes pixels
        for k, v in N["frames"].items():
            if v["tier_strict"] != "H":
                continue
            rv = v["raw_vis"]
            if rv["int_px"] > 0 or rv["edge_visible"] > 0 or rv["int_px_fallback"] > 0:
                gate_rows.append((band, k, rv["int_px"], rv["edge_visible"], rv["int_px_fallback"]))
    json.dump(dict(rows=rows, migrations=migr, gate_violations=gate_rows),
              open(os.path.join(REPO, "experiments/v3_0823/logs/g7_compare.json"), "w"), indent=1)

    print("### scene x arm — footprint + tier, BEFORE -> AFTER  (rows that changed)\n")
    hdr = f"{'band':4s} {'scene':8s} {'arm':4s} {'split':5s} {'hm before':12s} {'hm after':12s} {'raw b':>7s} {'raw a':>7s} {'kept b':>7s} {'kept a':>7s} {'maxdiff b':>9s} {'maxdiff a':>9s}"
    print(hdr); print("-" * len(hdr))
    for r in rows:
        if not r["changed"] and r["raw_before"] == r["raw_after"]:
            continue
        print(f"{r['band']:4s} {r['scene']:8s} {r['arm']:4s} {r['split']:5s} "
              f"{r['hm_before']:12s} {r['hm_after']:12s} {str(r['raw_before']):>7s} {str(r['raw_after']):>7s} "
              f"{str(r['kept_before']):>7s} {str(r['kept_after']):>7s} {str(r['md_before']):>9s} {str(r['md_after']):>9s}")
        print(f"       tiers  BEFORE {r['before']}   AFTER {r['after']}")
    n_same = sum(1 for r in rows if not r["changed"] and r["raw_before"] == r["raw_after"])
    print(f"\nunchanged scene-arms (control): {n_same} / {len(rows)}")
    print("\n### per-frame tier migrations")
    for band, sc, t, n in migr:
        print(f"  boost_{band:2s} {sc:8s} {t:22s} {n}")
    print(f"\n### GATE  strict-H frames with visible hazard pixels (must be 0): {len(gate_rows)}")
    for g in gate_rows[:20]:
        print("   ", g)


if __name__ == "__main__":
    main()
