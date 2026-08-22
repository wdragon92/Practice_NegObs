#!/usr/bin/env python3
"""Fold the per-frame infer_photo --json dumps into one CSV + the GAZEBO_TRACK read-out tables.

infer_photo already writes `cell_ids` + `probs` per frame, so nothing was added to the frozen
tool -- this only collects.  Read-out rules were fixed in capture_plan.md §4 before capture.

    python3 tools/collect_csv.py            # writes out/gazebo_zeroshot.csv, prints tables
"""
import csv
import glob
import json
import os
import statistics as st

GZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONDIR = os.path.join(GZ, "out", "json")
CSVOUT = os.path.join(GZ, "out", "gazebo_zeroshot.csv")

MODELS = ["rgb_s42", "rgb_s43", "rgb_s44", "b2_s42", "b2_s43", "b2_s44"]
PAIRS = [("gz_drop1", "V"), ("gz_drop2", "V"), ("gz_drop3", "H"), ("gz_drop4", "V/E")]
NEG_VIEWS = ["extra_h0.3_d1.2", "preset_h0.3_d2", "preset_h0.3_d5", "preset_h0.3_d10",
             "preset_h0.9_d2", "preset_h0.9_d5", "preset_h0.9_d10"]
RS_VIEWS = ["rs_h0.125_d2", "rs_h0.125_d5"]
# worlds/README.md §2: the band the lip falls into for each view
EXPECT_BAND = {"extra_h0.3_d1.2": "1", "preset_h0.3_d2": "2", "preset_h0.3_d5": "3a",
               "preset_h0.3_d10": "3b", "preset_h0.9_d2": "2", "preset_h0.9_d5": "3a",
               "preset_h0.9_d10": "3b", "rs_h0.125_d2": "2", "rs_h0.125_d5": "3a"}
# worlds/README.md §8: per-view predicted tier, per world
TIER = {
    "gz_drop1": {v: "V" for v in NEG_VIEWS + RS_VIEWS},
    "gz_drop2": {v: "V" for v in NEG_VIEWS + RS_VIEWS},
    "gz_drop3": {v: "H" for v in NEG_VIEWS + RS_VIEWS},
    "gz_drop4": {**{v: "V" for v in NEG_VIEWS + RS_VIEWS},
                 "preset_h0.3_d10": "E", "preset_h0.9_d10": "E", "rs_h0.125_d5": "E"},
}
TAU = 0.5


def band_of(cell):
    return cell[1:]


def load():
    rows = {}
    for p in sorted(glob.glob(os.path.join(JSONDIR, "*.json"))):
        model, world, view = os.path.basename(p)[:-5].split("__")
        d = json.load(open(p))
        probs, ids = d["probs"], d["cell_ids"]
        top = max(range(len(probs)), key=lambda i: probs[i])
        rows[(model, world, view)] = dict(
            model=model, world=world, view=view,
            arm="ctrl" if world.endswith("_ctrl") else "hazard",
            base=world.replace("_ctrl", ""),
            tier_pred=TIER[world.replace("_ctrl", "")][view] if not world.endswith("_ctrl") else "ctrl",
            expect_band=EXPECT_BAND[view],
            max_prob=max(probs), mean_prob=sum(probs) / len(probs),
            top_cell=ids[top], top_band=band_of(ids[top]), top_sector=ids[top][0],
            band_hit=int(band_of(ids[top]) == EXPECT_BAND[view]),
            fired=int(max(probs) >= TAU),
            n_fired=sum(1 for v in probs if v >= TAU),
            cells={i: v for i, v in zip(ids, probs)})
    return rows


def write_csv(rows):
    ids = sorted(next(iter(rows.values()))["cells"].keys())
    cols = ["model", "world", "base", "arm", "view", "tier_pred", "expect_band", "max_prob",
            "mean_prob", "top_cell", "top_band", "top_sector", "band_hit", "fired", "n_fired"]
    os.makedirs(os.path.dirname(CSVOUT), exist_ok=True)
    with open(CSVOUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols + ids)
        for k in sorted(rows):
            r = rows[k]
            w.writerow([r[c] if not isinstance(r[c], float) else round(r[c], 6) for c in cols]
                       + [round(r["cells"][i], 6) for i in ids])
    print(f"[collect] {CSVOUT}  ({len(rows)} rows x {len(cols) + len(ids)} cols)")


def fmt(xs):
    if not xs:
        return "  --  "
    return (f"{st.mean(xs):.3f} [{min(xs):.3f}-{max(xs):.3f}]"
            if len(xs) > 1 else f"{xs[0]:.3f}")


def table_firing(rows, views, label):
    print(f"\n### firing rate at tau={TAU} and frame max-prob -- {label} ({len(views)} views/world)")
    print(f"{'world':<10} {'tier':<5} {'model':<8} {'HAZ fire':>9} {'CTL fire':>9} "
          f"{'HAZ maxp mean[min-max]':>26} {'CTL maxp mean':>14} {'twin d mean':>12} {'d>0':>5}")
    for base, tierlab in PAIRS:
        for m in MODELS:
            h = [rows[(m, base, v)] for v in views]
            c = [rows[(m, base + "_ctrl", v)] for v in views]
            dh = [a["max_prob"] - b["max_prob"] for a, b in zip(h, c)]
            print(f"{base:<10} {tierlab:<5} {m:<8} "
                  f"{sum(x['fired'] for x in h)}/{len(h):<7} "
                  f"{sum(x['fired'] for x in c)}/{len(c):<7} "
                  f"{fmt([x['max_prob'] for x in h]):>26} "
                  f"{st.mean([x['max_prob'] for x in c]):>14.3f} "
                  f"{st.mean(dh):>+12.3f} {sum(1 for d in dh if d > 0)}/{len(dh)}")


def table_band(rows, views):
    print(f"\n### 1st read-out (qualitative): does the top cell land in the band the lip falls in?")
    print(f"{'world':<10} {'model':<8} {'HAZ band-hit':>13} {'CTL band-hit':>13}  top bands (hazard, per view)")
    for base, _ in PAIRS:
        for m in MODELS:
            h = [rows[(m, base, v)] for v in views]
            c = [rows[(m, base + "_ctrl", v)] for v in views]
            print(f"{base:<10} {m:<8} {sum(x['band_hit'] for x in h)}/{len(h):<11} "
                  f"{sum(x['band_hit'] for x in c)}/{len(c):<11}  "
                  + " ".join(f"{x['top_band']}" for x in h))


def table_ladder(rows, views):
    print("\n### 4th read-out (tier ladder): mean frame max-prob, hazard arm, same cameras")
    print("    pre-registered expectation  p(drop2) >= p(drop1) > p(drop4) > p(drop3)")
    print(f"{'model':<8}" + "".join(f"{b:>11}" for b, _ in PAIRS) + "   order holds?")
    for m in MODELS:
        mu = {b: st.mean([rows[(m, b, v)]["max_prob"] for v in views]) for b, _ in PAIRS}
        ok = mu["gz_drop2"] >= mu["gz_drop1"] > mu["gz_drop4"] > mu["gz_drop3"]
        print(f"{m:<8}" + "".join(f"{mu[b]:>11.3f}" for b, _ in PAIRS)
              + f"   {'yes' if ok else 'NO'}")


def table_drop3(rows, views):
    print("\n### gz_drop3 -- CUE-ONLY firing (hazard fully occluded; both arms are cue-only probes)")
    print("    compare: CUE-OFF arm C false-alarm rate, rgb 1.000 / b2 1.000 / depth 0.333 (24 frames)")
    print(f"{'model':<8} {'HAZ fired':>10} {'CTL fired':>10} {'pooled FA':>10} "
          f"{'mean maxp':>10} {'mean #cells fired':>18}")
    for m in MODELS:
        h = [rows[(m, "gz_drop3", v)] for v in views]
        c = [rows[(m, "gz_drop3_ctrl", v)] for v in views]
        allr = h + c
        print(f"{m:<8} {sum(x['fired'] for x in h)}/{len(h):<8} "
              f"{sum(x['fired'] for x in c)}/{len(c):<8} "
              f"{sum(x['fired'] for x in allr) / len(allr):>10.3f} "
              f"{st.mean([x['max_prob'] for x in allr]):>10.3f} "
              f"{st.mean([x['n_fired'] for x in allr]):>18.2f}")


def table_drop4E(rows):
    print("\n### gz_drop4 E cuts -- RAW, 2 presets only, no statistics (worlds/README §8.5)")
    print(f"{'view':<18} {'model':<8} {'HAZ maxp':>9} {'HAZ top':>8} {'CTL maxp':>9} "
          f"{'CTL top':>8} {'twin d':>8}")
    for v in ["preset_h0.3_d10", "preset_h0.9_d10"]:
        for m in MODELS:
            h, c = rows[(m, "gz_drop4", v)], rows[(m, "gz_drop4_ctrl", v)]
            print(f"{v:<18} {m:<8} {h['max_prob']:>9.3f} {h['top_cell']:>8} "
                  f"{c['max_prob']:>9.3f} {c['top_cell']:>8} "
                  f"{h['max_prob'] - c['max_prob']:>+8.3f}")


def table_asym(rows, views):
    print("\n### 3rd read-out (asymmetry): gz_drop2 has a railing on +Y (image RIGHT) only.")
    print("    sector A = image-left ... E = image-right.  mean prob per sector, hazard arm.")
    print(f"{'model':<8}" + "".join(f"{s:>9}" for s in "ABCDE") + "    argmax sector")
    for m in MODELS:
        mu = {}
        for s in "ABCDE":
            vals = [rows[(m, "gz_drop2", v)]["cells"][c]
                    for v in views for c in rows[(m, "gz_drop2", v)]["cells"] if c[0] == s]
            mu[s] = st.mean(vals)
        print(f"{m:<8}" + "".join(f"{mu[s]:>9.3f}" for s in "ABCDE")
              + f"    {max(mu, key=mu.get)}")


def table_headline(rows, views):
    print("\n### HEADLINE -- pooled over the 4 hazard worlds x 7 negobs presets (28 frames/arm)")
    print(f"{'model':<8} {'HAZ fire':>9} {'CTL fire':>9} {'HAZ maxp':>9} {'CTL maxp':>9} "
          f"{'twin delta':>11} {'in-sim twin d (v2)':>19}")
    insim = {"rgb": 0.314, "b2": 0.234}          # runs/v2/SEED_TABLE.md sec.2, mean over seeds
    for m in MODELS:
        h = [rows[(m, b, v)] for b, _ in PAIRS for v in views]
        c = [rows[(m, b + "_ctrl", v)] for b, _ in PAIRS for v in views]
        d = [a["max_prob"] - z["max_prob"] for a, z in zip(h, c)]
        print(f"{m:<8} {sum(x['fired'] for x in h) / len(h):>9.3f} "
              f"{sum(x['fired'] for x in c) / len(c):>9.3f} "
              f"{st.mean([x['max_prob'] for x in h]):>9.3f} "
              f"{st.mean([x['max_prob'] for x in c]):>9.3f} "
              f"{st.mean(d):>+11.3f} {insim[m.split('_')[0]]:>19.3f}")


def main():
    rows = load()
    write_csv(rows)
    table_headline(rows, NEG_VIEWS)
    table_firing(rows, NEG_VIEWS, "7 negobs presets (h0.3 / h0.9), rs_* excluded")
    table_band(rows, NEG_VIEWS)
    table_ladder(rows, NEG_VIEWS)
    table_drop3(rows, NEG_VIEWS)
    table_drop4E(rows)
    table_asym(rows, NEG_VIEWS)
    table_firing(rows, RS_VIEWS, "rs_h0.125 (robot RealSense height) -- NOT in the headline")


if __name__ == "__main__":
    main()
