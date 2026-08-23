#!/usr/bin/env python3
"""
CPU-2 / FA CENSUS  --  step 3: family classification + the report's five tables.

Reads   experiments/v3_0823/fa_events_raw.csv   (step 1)
        experiments/v3_0823/cell_photometry.csv (step 2)
        experiments/v3_0823/code/scene_knowledge.json (curated, step 2b)
Writes  experiments/v3_0823/fa_events.csv       (events + family flags + method)
        experiments/v3_0823/logs/fa_census_tables.json  (every table, machine form)

FAMILY RULES -- fixed here, once, and printed in the report header.
5 families, multi-membership allowed (D54 ruling, FA_REALITY.md:29-35).

  경계칸형 BOUNDARY   mechanical  band == '3b' (outermost) OR sector in {A,E}
                                  sub-flags kept apart: bnd_band / bnd_sector / corner
  조명형   LIGHTING    heuristic   cell lum_median < 0.60 * frame lum_median
                                  (needs n_px > 0; sensitivity at 0.50 / 0.70)
  대리선형 SURROGATE   heuristic   cell line_frac >= P90 of visible test-core cells.
                                  On OFF there is no drop anywhere, so a coherent
                                  ground-crossing line IS a surrogate by
                                  construction.  On ON_NEG the real lip can bleed
                                  in, so the flag additionally requires the cell
                                  to be non-adjacent to every GT-positive cell of
                                  that frame; adjacent ones get method
                                  'heuristic-weak' and are counted separately.
  지형통계형 TERRAIN   heuristic   unseen (n_px == 0 -> fired on a cell with no
                                  visible content at all: pure prior) OR
                                  prior-saturated (this (model,scene,stratum,cell)
                                  fires on >= 80 % of that scene's frames)
                                  OR scene-knowledge terrain-prior overlay
  장식형   DECORATIVE  manual      (scene, cell-region) overlay from scene
                                  composition notes -- see scene_knowledge.json
"""
import csv
import json
import os
import sys
from collections import defaultdict, Counter
from itertools import combinations

import numpy as np

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
OUT = os.path.join(ROOT, "experiments/v3_0823")
MANIFEST = os.path.join(ROOT, "experiments/dayrun_0820/dataset_manifest_v2_full.json")
GRIDSPEC = os.path.join(ROOT, "experiments/mainrun_0819/code/labeling/gridspec_v1.json")
KNOW = os.path.join(OUT, "code/scene_knowledge.json")

LIGHT_RATIO = 0.60
LIGHT_SENS = (0.50, 0.70)
SAT_RATE = 0.80
MODELS = ["rgb", "depth", "b2"]
SEEDS = [42, 43, 44]

G = json.load(open(GRIDSPEC))
NS = G["n_sectors"]
BANDS = G["band_names"]
SECTORS = G["sector_names"]
CELL_IDS = [f"{s}{b}" for b in BANDS for s in SECTORS]
BI = {b: i for i, b in enumerate(BANDS)}
SI = {s: i for i, s in enumerate(SECTORS)}
EDGE_SECTORS = {SECTORS[0], SECTORS[-1]}          # A, E
OUTER_BAND = BANDS[-1]                            # 3b


def adjacent(c1, c2):
    """4-neighbourhood on the (band, sector) lattice; identity counts as adjacent."""
    b1, s1 = BI[c1[1:]], SI[c1[0]]
    b2, s2 = BI[c2[1:]], SI[c2[0]]
    return abs(b1 - b2) + abs(s1 - s2) <= 1


def main():
    # ---------- inputs -------------------------------------------------------
    man = {f["frame_id"]: f for f in json.load(open(MANIFEST))["frames"]}
    photo = {}
    for r in csv.DictReader(open(os.path.join(OUT, "cell_photometry.csv"))):
        photo[(r["frame_id"], r["cell"])] = r
    know = json.load(open(KNOW)) if os.path.exists(KNOW) else {"scenes": {}}

    vis_lf = [float(r["line_frac"]) for r in photo.values()
              if int(r["n_px"]) > 0 and r["line_frac"] != ""]
    LINE_P90 = float(np.percentile(vis_lf, 90))
    LINE_P75 = float(np.percentile(vis_lf, 75))
    LINE_P95 = float(np.percentile(vis_lf, 95))

    ev = list(csv.DictReader(open(os.path.join(OUT, "fa_events_raw.csv"))))
    for e in ev:
        e["seed"] = int(e["seed"])

    # GT-positive cells per on-arm frame (for the SURROGATE bleed guard)
    gtpos = {}
    for fid, f in man.items():
        gtpos[fid] = {CELL_IDS[i] for i, v in enumerate(f["polar_gt"]) if v}

    # ---------- prior-saturation: fire rate per (model,scene,stratum,cell) ----
    # denominator = frames of that scene in that stratum, per model (seed-pooled
    # majority), so a cell that is on regardless of content shows up as ~1.0
    frames_of = defaultdict(set)                   # (scene,stratum) -> frames
    pf = os.path.join(ROOT, "experiments/dayrun_0820/runs/v2/rgb_s42/eval_test/per_frame.csv")
    test_rows = list(csv.DictReader(open(pf)))
    for r in test_rows:
        strat = "OFF" if r["toggle_state"] == "off" else "ON_NEG"
        frames_of[(r["scene_id"], strat)].add(r["frame_id"])

    # majority (>=2/3 seeds) event set per model
    cnt_ms = defaultdict(Counter)                  # model -> (frame,cell) -> nseeds
    for e in ev:
        cnt_ms[e["model"]][(e["frame_id"], e["cell"])] += 1
    major = {m: {k for k, v in c.items() if v >= 2} for m, c in cnt_ms.items()}

    fire = defaultdict(int)                        # (model,scene,strat,cell)->n frames
    for m, s in major.items():
        for fid, cell in s:
            r = man[fid]
            strat = "OFF" if r["toggle_state"] == "off" else "ON_NEG"
            fire[(m, r["scene_id"], strat, cell)] += 1
    satur = set()
    for k, n in fire.items():
        m, sc, strat, cell = k
        den = len(frames_of[(sc, strat)])
        if den and n / den >= SAT_RATE:
            satur.add(k)

    # ---------- classify -----------------------------------------------------
    out = []
    for e in ev:
        cell, band, sector = e["cell"], e["band"], e["sector"]
        fid, sc, strat = e["frame_id"], e["scene_id"], e["stratum"]
        ph = photo.get((fid, cell), {})
        n_px = int(ph.get("n_px", 0) or 0)
        unseen = n_px == 0

        bnd_band = band == OUTER_BAND
        bnd_sector = sector in EDGE_SECTORS
        f_boundary = bnd_band or bnd_sector

        lum = ph.get("lum_median", "")
        fl = ph.get("frame_lum_median_all", "")
        ratio = (float(lum) / float(fl)) if (lum and fl and float(fl) > 0) else None
        f_light = bool(ratio is not None and ratio < LIGHT_RATIO)
        f_light_50 = bool(ratio is not None and ratio < LIGHT_SENS[0])
        f_light_70 = bool(ratio is not None and ratio < LIGHT_SENS[1])

        lf = ph.get("line_frac", "")
        lfv = float(lf) if lf else None
        line_hit = bool(lfv is not None and lfv >= LINE_P90)
        bleed = strat == "ON_NEG" and any(adjacent(cell, p) for p in gtpos.get(fid, ()))
        f_surrog = line_hit and not bleed
        f_surrog_weak = line_hit and bleed

        k = know.get("scenes", {}).get(sc, {})
        # 장식형: only where an installed object is localisable to a (sector, band)
        # region.  Scene-wide dressing is metadata, never a flag -- see
        # scene_knowledge.json "_scoping_rule".
        f_deco = any(sector in reg.get("sectors", []) and band in reg.get("bands", [])
                     for reg in k.get("decorative_regions", []))
        terr_scene = False          # left to the mechanical rule by design
        f_terr = unseen or ((e["model"], sc, strat, cell) in satur)

        fams = []
        if f_deco:
            fams.append("장식형")
        if f_terr:
            fams.append("지형통계형")
        if f_light:
            fams.append("조명형")
        if f_surrog:
            fams.append("대리선형")
        if f_boundary:
            fams.append("경계칸형")

        methods = []
        if f_boundary:
            methods.append("mechanical")
        if f_terr and unseen:
            methods.append("mechanical")
        if f_light or (f_terr and not unseen) or f_surrog:
            methods.append("heuristic")
        if f_deco or terr_scene:
            methods.append("manual")
        method = "+".join(sorted(set(methods))) or "unclassified"

        out.append(dict(
            **{k2: e[k2] for k2 in ("model", "seed", "run", "stratum", "frame_id",
                                    "scene_id", "tier", "cell", "cell_idx",
                                    "sector", "band", "score", "cell_int_px")},
            n_px=n_px, unseen=int(unseen),
            lum_ratio=(round(ratio, 4) if ratio is not None else ""),
            line_frac=(round(lfv, 4) if lfv is not None else ""),
            fam_decorative=int(f_deco), fam_terrain=int(f_terr),
            fam_lighting=int(f_light), fam_surrogate=int(f_surrog),
            fam_boundary=int(f_boundary),
            bnd_band=int(bnd_band), bnd_sector=int(bnd_sector),
            bnd_corner=int(bnd_band and bnd_sector),
            surrogate_weak=int(f_surrog_weak),
            light_50=int(f_light_50), light_70=int(f_light_70),
            prior_saturated=int((e["model"], sc, strat, cell) in satur),
            n_families=len(fams), families="|".join(fams), method=method,
        ))

    with open(os.path.join(OUT, "fa_events.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    # ---------- tables -------------------------------------------------------
    T = {"params": dict(LIGHT_RATIO=LIGHT_RATIO, LIGHT_SENS=list(LIGHT_SENS),
                        LINE_P90=round(LINE_P90, 4), LINE_P75=round(LINE_P75, 4),
                        LINE_P95=round(LINE_P95, 4), SAT_RATE=SAT_RATE,
                        outer_band=OUTER_BAND, edge_sectors=sorted(EDGE_SECTORS))}
    recon = json.load(open(os.path.join(OUT, "logs/fa_recount.json")))

    # T1 volume
    t1 = {}
    for m in MODELS:
        for s in SEEDS:
            run = f"{m}_s{s}"
            off = [e for e in out if e["run"] == run and e["stratum"] == "OFF"]
            on = [e for e in out if e["run"] == run and e["stratum"] == "ON_NEG"]
            nif = [e for e in on if e["tier"] == "none_in_fov"]
            rc = recon[run]
            t1[run] = dict(
                off_events=len(off), off_frames_fired=rc["n_off_fired_frames"],
                frame_fa_off=rc["recount_frame_fa_off"],
                pub_frame_fa_off=rc["pub_frame_fa_off"],
                match=rc["match_frame_fa_off"] and rc["match_cell_fpr_off"]
                and rc["match_cell_fpr_on_neg"],
                cell_fpr_off=rc["recount_cell_fpr_off"],
                on_neg_events=len(on), cell_fpr_on_neg=rc["recount_cell_fpr_on_neg"],
                on_neg_none_in_fov=len(nif),
                none_in_fov_share=len(nif) / len(on) if on else 0.0,
            )
    T["t1_volume"] = t1
    T["denominators"] = dict(off_cells=8160, off_frames=408,
                             on_neg_cells=recon["rgb_s42"]["n_on_neg_cells"],
                             on_frames=408,
                             none_in_fov_frames=81,
                             none_in_fov_cells=81 * 20)

    # T2 seed persistence  (unit = (frame,cell), per model, per stratum)
    t2 = {}
    for m in MODELS:
        for strat in ("OFF", "ON_NEG"):
            c = Counter((e["frame_id"], e["cell"]) for e in out
                        if e["model"] == m and e["stratum"] == strat)
            n = len(c)
            d = Counter(c.values())
            t2[f"{m}|{strat}"] = dict(
                distinct=n, n1=d[1], n2=d[2], n3=d[3],
                share_ge2=(d[2] + d[3]) / n if n else 0.0,
                share_3=d[3] / n if n else 0.0,
                events=sum(c.values()),
                event_weighted_share_ge2=(sum(v for v in c.values() if v >= 2)
                                          / sum(c.values())) if n else 0.0,
            )
    T["t2_persistence"] = t2

    # T3 family census  (per model, seed-pooled events; and on majority sets)
    fam_keys = ["fam_decorative", "fam_terrain", "fam_lighting",
                "fam_surrogate", "fam_boundary"]
    t3 = {}
    for m in MODELS + ["ALL"]:
        for strat in ("OFF", "ON_NEG"):
            sel = [e for e in out if e["stratum"] == strat
                   and (m == "ALL" or e["model"] == m)]
            n = len(sel)
            row = {k: sum(e[k] for e in sel) for k in fam_keys}
            row.update(n=n,
                       unclassified=sum(1 for e in sel if e["n_families"] == 0),
                       multi=sum(1 for e in sel if e["n_families"] >= 2),
                       mean_families=(sum(e["n_families"] for e in sel) / n) if n else 0,
                       bnd_band=sum(e["bnd_band"] for e in sel),
                       bnd_sector=sum(e["bnd_sector"] for e in sel),
                       bnd_corner=sum(e["bnd_corner"] for e in sel),
                       surrogate_weak=sum(e["surrogate_weak"] for e in sel),
                       light_50=sum(e["light_50"] for e in sel),
                       light_70=sum(e["light_70"] for e in sel),
                       unseen=sum(e["unseen"] for e in sel),
                       prior_saturated=sum(e["prior_saturated"] for e in sel))
            t3[f"{m}|{strat}"] = row
    T["t3_family"] = t3

    # ---- family LIFT: family share among FA events vs among at-risk cells ----
    # Without this a family count is uninterpretable: 55 % of the grid is
    # "boundary" by the registered rule, so 55 % of FAs being boundary means
    # nothing.  Lift = P(family | FA) / P(family | at-risk cell).
    risk = {"OFF": [], "ON_NEG": []}
    for r in test_rows:
        fid = r["frame_id"]
        strat = "OFF" if r["toggle_state"] == "off" else "ON_NEG"
        pos = gtpos[fid]
        for cell in CELL_IDS:
            if strat != "OFF" and cell in pos:
                continue
            ph = photo.get((fid, cell), {})
            n_px = int(ph.get("n_px", 0) or 0)
            lum, fl = ph.get("lum_median", ""), ph.get("frame_lum_median_all", "")
            ratio = (float(lum) / float(fl)) if (lum and fl and float(fl) > 0) else None
            lf = ph.get("line_frac", "")
            lfv = float(lf) if lf else None
            bleed = strat == "ON_NEG" and any(adjacent(cell, p) for p in pos)
            risk[strat].append(dict(
                boundary=(cell[1:] == OUTER_BAND or cell[0] in EDGE_SECTORS),
                bnd_band=(cell[1:] == OUTER_BAND), bnd_sector=(cell[0] in EDGE_SECTORS),
                lighting=bool(ratio is not None and ratio < LIGHT_RATIO),
                surrogate=bool(lfv is not None and lfv >= LINE_P90 and not bleed),
                unseen=(n_px == 0)))
    t3l = {}
    for strat in ("OFF", "ON_NEG"):
        R = risk[strat]
        nR = len(R)
        sel = [e for e in out if e["stratum"] == strat]
        nE = len(sel)
        for name, ekey, rkey in (("경계칸형(등록 union)", "fam_boundary", "boundary"),
                                 ("  ├ 반경(3b)", "bnd_band", "bnd_band"),
                                 ("  └ 방위(A/E)", "bnd_sector", "bnd_sector"),
                                 ("조명형", "fam_lighting", "lighting"),
                                 ("대리선형", "fam_surrogate", "surrogate"),
                                 ("지형통계형(unseen만)", "unseen", "unseen")):
            pe = sum(e[ekey] for e in sel) / nE if nE else 0.0
            pr = sum(1 for r in R if r[rkey]) / nR if nR else 0.0
            t3l[f"{strat}|{name}"] = dict(
                n_fa=sum(e[ekey] for e in sel), p_fa=pe,
                n_risk=sum(1 for r in R if r[rkey]), p_risk=pr,
                lift=(pe / pr) if pr else None)
    T["t3_lift"] = t3l
    T["t3_risk_denom"] = {k: len(v) for k, v in risk.items()}

    # family co-occurrence (ALL events)
    co = {}
    for a, b in combinations(fam_keys, 2):
        co[f"{a}&{b}"] = sum(1 for e in out if e[a] and e[b])
    T["t3_cooccurrence"] = co

    # T4 inter-model overlap on seed-majority sets, overall and per family
    key = {}
    for m in MODELS:
        for strat in ("OFF", "ON_NEG"):
            c = Counter((e["frame_id"], e["cell"]) for e in out
                        if e["model"] == m and e["stratum"] == strat)
            key[(m, strat)] = {k for k, v in c.items() if v >= 2}
    fam_key = {}
    for m in MODELS:
        for strat in ("OFF", "ON_NEG"):
            for fk in fam_keys:
                c = Counter((e["frame_id"], e["cell"]) for e in out
                            if e["model"] == m and e["stratum"] == strat and e[fk])
                fam_key[(m, strat, fk)] = {k for k, v in c.items() if v >= 2}

    def jac(a, b):
        u = len(a | b)
        return dict(a=len(a), b=len(b), inter=len(a & b), union=u,
                    jaccard=(len(a & b) / u) if u else 0.0,
                    ovl_min=(len(a & b) / min(len(a), len(b))) if min(len(a), len(b)) else 0.0)

    t4 = {}
    for strat in ("OFF", "ON_NEG"):
        for a, b in combinations(MODELS, 2):
            t4[f"{a}~{b}|{strat}|ALL"] = jac(key[(a, strat)], key[(b, strat)])
            for fk in fam_keys:
                t4[f"{a}~{b}|{strat}|{fk}"] = jac(fam_key[(a, strat, fk)],
                                                  fam_key[(b, strat, fk)])
        tri = key[("rgb", strat)] & key[("depth", strat)] & key[("b2", strat)]
        uni = key[("rgb", strat)] | key[("depth", strat)] | key[("b2", strat)]
        t4[f"TRIPLE|{strat}"] = dict(all3=len(tri), union=len(uni),
                                     share=len(tri) / len(uni) if uni else 0.0,
                                     exactly1=sum(1 for k in uni if sum(
                                         k in key[(m, strat)] for m in MODELS) == 1),
                                     exactly2=sum(1 for k in uni if sum(
                                         k in key[(m, strat)] for m in MODELS) == 2))
    T["t4_overlap"] = t4

    # T5 scene x cell concentration
    t5 = {}
    for strat in ("OFF", "ON_NEG"):
        c = Counter((e["scene_id"], e["cell"]) for e in out if e["stratum"] == strat)
        tot = sum(c.values())
        rows = []
        for (sc, cell), n in c.most_common(25):
            sel = [e for e in out if e["stratum"] == strat
                   and e["scene_id"] == sc and e["cell"] == cell]
            den = len(frames_of[(sc, strat)]) * 9      # 9 runs
            fams = Counter()
            for e in sel:
                for f in e["families"].split("|"):
                    if f:
                        fams[f] += 1
            rows.append(dict(scene=sc, cell=cell, n=n, share=n / tot,
                             rate_over_run_frames=n / den if den else 0.0,
                             models=sorted({e["model"] for e in sel}),
                             nif=sum(1 for e in sel if e["tier"] == "none_in_fov"),
                             fams=dict(fams.most_common())))
        t5[strat] = dict(total=tot, top=rows)
    T["t5_scene_cell"] = t5

    # ---------- exposure denominators ---------------------------------------
    # A raw count is not comparable across cells: on the ON_NEG stratum a cell is
    # only "at risk" on frames where its GT is 0, and cells differ a lot in how
    # often that happens.  expo[(strat,cell)] = number of GT-negative
    # cell-instances of that cell id, times 9 runs.
    expo = Counter()
    for r in test_rows:
        fid = r["frame_id"]
        strat = "OFF" if r["toggle_state"] == "off" else "ON_NEG"
        pos = gtpos[fid]
        for cell in CELL_IDS:
            if strat == "OFF" or cell not in pos:
                expo[(strat, cell)] += 9
    T["exposure"] = {f"{s}|{c}": n for (s, c), n in sorted(expo.items())}

    # scene totals + per-band/sector marginals, with exposure-normalised rates
    T["marginals"] = {}
    for strat in ("OFF", "ON_NEG"):
        sel = [e for e in out if e["stratum"] == strat]
        n_all = len(sel)
        cellc = Counter(e["cell"] for e in sel)
        tot_expo = sum(expo[(strat, c)] for c in CELL_IDS)
        cell_rate = {c: dict(n=cellc.get(c, 0), expo=expo[(strat, c)],
                             rate=cellc.get(c, 0) / expo[(strat, c)]
                             if expo[(strat, c)] else 0.0)
                     for c in CELL_IDS}
        # band / sector lift = share of events / share of exposure
        def lift(getter, keys):
            o = {}
            for k in keys:
                ce = sum(cellc.get(c, 0) for c in CELL_IDS if getter(c) == k)
                ex = sum(expo[(strat, c)] for c in CELL_IDS if getter(c) == k)
                o[k] = dict(n=ce, expo=ex, rate=ce / ex if ex else 0.0,
                            share_events=ce / n_all if n_all else 0.0,
                            share_expo=ex / tot_expo if tot_expo else 0.0,
                            lift=((ce / n_all) / (ex / tot_expo))
                            if n_all and ex else 0.0)
            return o
        T["marginals"][strat] = dict(
            scene=dict(Counter(e["scene_id"] for e in sel).most_common()),
            band=lift(lambda c: c[1:], BANDS),
            sector=lift(lambda c: c[0], SECTORS),
            boundary_union=lift(
                lambda c: "edge" if (c[1:] == OUTER_BAND or c[0] in EDGE_SECTORS)
                else "interior", ["edge", "interior"]),
            tier=dict(Counter(e["tier"] for e in sel).most_common()),
            cell=cell_rate)

    json.dump(T, open(os.path.join(OUT, "logs/fa_census_tables.json"), "w"),
              indent=2, ensure_ascii=False)
    print(json.dumps(T["params"], ensure_ascii=False))
    print("events", len(out), "-> fa_events.csv ; tables -> logs/fa_census_tables.json")
    print("T2 persistence:", json.dumps({k: round(v["share_ge2"], 3)
                                         for k, v in t2.items()}))
    print("T4 triple:", json.dumps({k: v for k, v in t4.items() if k.startswith("TRIPLE")}))


if __name__ == "__main__":
    sys.exit(main())
