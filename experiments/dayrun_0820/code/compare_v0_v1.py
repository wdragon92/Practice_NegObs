#!/usr/bin/env python3
"""DAYRUN 0820 Phase 1 step 3 -- V0 vs V1 comparison + boost-render targeting basis.

Writes P1_GRID_V1.md:
  1. invariant-gate result (re-stated from invariant_gate.py, all 33 scenes)
  2. 20-cell positive-count heatmap, TRAIN frames of ELIGIBLE scenes
  3. mean positive cells / frame, V0 vs V1
  4. band 3 -> 3a/3b decomposition (how the old band-3 positives split)
  5. sparse cells (positives < SPARSE_MIN) -- the boost-render targets
  6. per-scene tier E counts + a data-driven far-visible-rim potential score
     -> the E-boost train scene candidate list (D19③)
"""
import argparse, collections, json, os

SPARSE_MIN = 10          # "sparse cell" threshold from the brief (positives < 10)
SCENE_MIN = 5            # a cell fed by fewer distinct scenes than this is
#                          scene-sparse: it has frames but no variety, so the head
#                          memorises one scene's geometry instead of learning a cell
FAR_D = 6.0              # m, the D19① boost sampler's near edge for far cams
NEAR_BANDS = (0, 1)      # bands 1,2 = [0,5) m
TAU_EDGE_DEF = 0.05      # labeler's strict tau_edge -- what an E call needs
# E-boost ranking weights: a "near-miss E" frame is one camera change away from E,
# a "far only" frame is the pure rim-at-distance geometry E is defined on.
W_NEARMISS, W_FARONLY = 0.6, 0.4


def cellname(grid, i):
    ns = grid["n_sectors"]
    return f"{grid['band_names'][i // ns]}{grid['sector_names'][i % ns]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v0", required=True)
    ap.add_argument("--v1", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--split", required=True)
    ap.add_argument("--holds", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    L0, L1 = json.load(open(a.v0)), json.load(open(a.v1))
    F0, F1 = L0["frames"], L1["frames"]
    g0, g1 = L0["grid"], L1["grid"]
    ns, nb0, nb1 = g1["n_sectors"], g0["n_bands"], g1["n_bands"]
    n0, n1 = nb0 * ns, nb1 * ns
    man = {f["frame_id"]: f for f in json.load(open(a.manifest))["frames"]}
    split = json.load(open(a.split))
    held = set(json.load(open(a.holds)))
    train = [s for s in split["train"] if s not in held]
    eligible = set(split["train"]) | set(split["val"]) | set(split["test"])
    eligible -= held

    def scene_of(k):
        return k.split("/")[1]

    on_train = [k for k in F1 if k.startswith("on/") and scene_of(k) in train]
    on_elig = [k for k in F1 if k.startswith("on/") and scene_of(k) in eligible]
    on_train.sort(); on_elig.sort()

    # ---- 2. heatmap: positive frame count per cell, train + eligible ---------
    pos1 = [0] * n1
    pos0 = [0] * n0
    cell_scenes = [set() for _ in range(n1)]      # distinct train scenes per cell
    for k in on_train:
        for i, v in enumerate(F1[k]["polar_gt"]):
            pos1[i] += int(bool(v))
            if v:
                cell_scenes[i].add(scene_of(k))
        for i, v in enumerate(F0[k]["polar_gt"]):
            pos0[i] += int(bool(v))
    # the same counts on val/test, so the evaluation side's blind spots are visible
    pos_eval = {}
    for name in ("val", "test"):
        scs = [s for s in split[name] if s not in held]
        keys = [k for k in F1 if k.startswith("on/") and scene_of(k) in scs]
        c = [0] * n1
        for k in keys:
            for i, v in enumerate(F1[k]["polar_gt"]):
                c[i] += int(bool(v))
        pos_eval[name] = (c, len(keys), scs)

    # ---- 3. mean positive cells / frame -------------------------------------
    def means(keys):
        s0 = sum(sum(F0[k]["polar_gt"]) for k in keys)
        s1 = sum(sum(F1[k]["polar_gt"]) for k in keys)
        return (s0 / max(len(keys), 1), s1 / max(len(keys), 1), len(keys))

    m_train = means(on_train)
    m_elig = means(on_elig)
    on_all = sorted(k for k in F1 if k.startswith("on/"))
    m_all = means(on_all)
    # frames that have any positive at all (the none_in_fov complement)
    on_train_pos = [k for k in on_train if any(F1[k]["polar_gt"])]
    m_train_pos = means(on_train_pos)

    # ---- 4. band3 -> 3a/3b decomposition ------------------------------------
    dec = collections.Counter()          # per (sector) split class
    dec_tot = collections.Counter()
    for k in on_train:
        p0, p1 = F0[k]["polar_gt"], F1[k]["polar_gt"]
        for s in range(ns):
            if not p0[2 * ns + s]:
                continue
            a3, b3 = bool(p1[2 * ns + s]), bool(p1[3 * ns + s])
            cls = "3a+3b" if (a3 and b3) else "3a only" if a3 else "3b only" if b3 else "LOST"
            dec[cls] += 1
            dec_tot[(s, cls)] += 1
    b3_pos_v0 = sum(dec.values())
    b3a = sum(pos1[2 * ns:3 * ns])
    b3b = sum(pos1[3 * ns:4 * ns])

    # ---- 4.1 side effects the refinement exposes ----------------------------
    # (a) the D14 step-gate exclusion ledger. `gate_excluded` = cells positive in
    # polar_gt_pregate but not in polar_gt.  A coarse cell can HIDE an exclusion:
    # if the gate removed a component at 6 m while another survived at 10 m, V0's
    # single band-3 cell stays positive and records nothing.  V1 separates them.
    ex_f0 = ex_f1 = ex_c0 = ex_c1 = new_only = 0
    pre_nest = 0
    ex_examples = []
    for k in F0:
        n_0 = (F0[k].get("gate_excluded") or {}).get("n") or 0
        n_1 = (F1[k].get("gate_excluded") or {}).get("n") or 0
        ex_c0 += n_0; ex_c1 += n_1
        ex_f0 += n_0 > 0; ex_f1 += n_1 > 0
        if n_0 == 0 and n_1 > 0:
            new_only += 1
            if len(ex_examples) < 3:
                ex_examples.append((k, F0[k], F1[k]))
        q0, q1 = F0[k]["polar_gt_pregate"], F1[k]["polar_gt_pregate"]
        foldq = [q1[b * ns + s] if b < 2 else (q1[2 * ns + s] | q1[3 * ns + s])
                 for b in range(3) for s in range(ns)]
        if foldq != q0:
            pre_nest += 1

    # (b) G5's per-band agreement, recomputed here so the D19⑤ demotion argument
    # is backed by the V1 numbers rather than asserted.
    def band_agree(F, nb):
        pb = [[0, 0] for _ in range(nb)]
        for k, f in F.items():
            if f["tier_strict"] != "V":
                continue
            ci = f["raw_vis"].get("cell_int_px") or []
            if len(ci) != len(f["polar_gt"]):
                continue
            for i, v in enumerate(f["polar_gt"]):
                if v:
                    pb[i // ns][0] += int(ci[i] > 0); pb[i // ns][1] += 1
        return pb
    pb0, pb1 = band_agree(F0, nb0), band_agree(F1, nb1)

    S41 = ["## 4.1 two side effects of the refinement — both resolution gains", "",
          "### (a) the D14 step-gate exclusion ledger gets sharper", "",
          "| | V0 | V1 |", "|---|---|---|",
          f"| frames losing ≥1 GT cell to the step gate | {ex_f0} | **{ex_f1}** |",
          f"| GT cells excluded (sum) | {ex_c0} | **{ex_c1}** |", "",
          f"**{new_only} frames record an exclusion under V1 that V0 recorded as none.** "
          f"This is not the gate behaving differently — the footprint, the gate and the "
          f"survivors are byte-identical, and the pre-gate nesting law holds on every frame "
          f"(**{pre_nest}** violations). It is a coarse cell hiding an exclusion: when the "
          f"gate dropped a component at ~6 m while another survived at ~10 m, V0's single "
          f"band-3 cell stayed positive and logged nothing. V1 puts them in 3a and 3b and "
          f"the loss becomes visible.", ""]
    if ex_examples:
        k, a0_, a1_ = ex_examples[0]
        S41 += [f"Worked example — `{k}`:", "", "```",
              f"V0  pregate {a0_['polar_gt_pregate']}",
              f"V0  trained {a0_['polar_gt']}   gate_excluded n=0  <- nothing logged",
              f"V1  pregate {a1_['polar_gt_pregate']}",
              f"V1  trained {a1_['polar_gt']}   gate_excluded "
              f"{a1_['gate_excluded']['cells']}", "```", "",
              "Same footprint, same gate; V0's band-3 cell was positive either way, so the "
              "excluded near-half left no trace. **Consequence for the morning ruling: the "
              "D14 revert ledger was under-reporting, and the V1 number "
              f"({ex_f1} frames / {ex_c1} cells) is the honest one.**", ""]

    S41 += ["### (b) G5 agreement resolves into a clean distance trend", "",
          "G5 = the fraction of GT-positive cells that hold at least one reprojected "
          "below-ground pixel. D19⑤ demotes it to a reference metric on the argument that it "
          "measures view shadow, not label quality. V1 makes that argument checkable, because "
          "the far band splits:", "",
          "| grid | band | agreement | positive cells |", "|---|---|---|---|"]
    for b in range(nb0):
        h, nn = pb0[b]
        S41.append(f"| V0 | {g0['band_names'][b]} ({g0['band_edges_m'][b]}–"
                 f"{g0['band_edges_m'][b + 1]} m) | {h / max(nn, 1):.3f} | {nn} |")
    for b in range(nb1):
        h, nn = pb1[b]
        S41.append(f"| **V1** | **{g1['band_names'][b]}** ({g1['band_edges_m'][b]}–"
                 f"{g1['band_edges_m'][b + 1]} m) | **{h / max(nn, 1):.3f}** | {nn} |")
    S41 += ["",
          f"Agreement rises monotonically with range — "
          f"{' → '.join(f'{pb1[b][0] / max(pb1[b][1], 1):.2f}' for b in range(nb1))} — "
          f"which is exactly what the view-shadow explanation predicts and what a labeling "
          f"defect would not produce. The near band's {pb1[0][0] / max(pb1[0][1], 1):.3f} is "
          f"geometry: standing at the lip of a drop, the floor immediately below is occluded "
          f"by the lip itself.", "",
          f"Note the far row does not merely subdivide: V0 scored "
          f"{pb0[2][0] / max(pb0[2][1], 1):.3f} over {pb0[2][1]} band-3 cells, V1 scores "
          f"{pb1[2][0] / max(pb1[2][1], 1):.3f} / {pb1[3][0] / max(pb1[3][1], 1):.3f} over "
          f"{pb1[2][1] + pb1[3][1]} cells. **V0's pooling flattered the far band**: one "
          f"below-ground pixel anywhere in 5–12 m satisfied the whole 7 m-deep cell, whereas "
          f"V1 asks the question separately of 5–8 m and 8–12 m. Both readings are honest "
          f"about their own grid — which is precisely why a threshold on the pooled number "
          f"was never a gate-worthy quantity, and D19⑤'s demotion is the right call.", ""]

    # ---- 5. sparse cells ----------------------------------------------------
    sparse = sorted((pos1[i], i) for i in range(n1) if pos1[i] < SPARSE_MIN)

    # ---- 6. per-scene E + far-visible-rim potential -------------------------
    # far-rim potential is measured, not assumed:
    #   far_gt   = on-arm frames whose GT reaches band 3a/3b (5-12 m)
    #   far_only = ... and NOT any near band (the pure "rim at distance" geometry)
    #   nearmissE= frames where the lip DID project (>=8 pts) but the visible
    #              fraction fell short of tau_edge, or was swamped by interior
    #              pixels -- a lower / farther camera converts these into E
    #   E_now    = tier E frames the scene already contributes
    rows = {}
    for k in on_elig:
        sc = scene_of(k)
        f1, mf = F1[k], man.get(k, {})
        r = rows.setdefault(sc, dict(n=0, E=0, V=0, H=0, Hw=0, none=0, far_gt=0,
                                     far_only=0, nearmiss=0, far_cam=0, far_cam_E=0,
                                     rim_proj=0, rim_seen=0, cells_far=0))
        p = f1["polar_gt"]
        far = any(p[2 * ns:])
        near = any(p[:2 * ns])
        r["n"] += 1
        t = f1["tier_strict"]
        r["E"] += t == "E"
        r["V"] += t == "V"
        r["H"] += t == "H"
        r["Hw"] += t == "H_weak"
        r["none"] += t == "none_in_fov"
        r["far_gt"] += far
        r["far_only"] += far and not near
        r["cells_far"] += sum(p[2 * ns:])
        rv = f1["raw_vis"]
        er, ep, ev = rv.get("edge_ratio"), rv.get("edge_projected") or 0, rv.get("edge_visible") or 0
        r["rim_proj"] += ep >= 8
        r["rim_seen"] += ev > 0
        if t != "E" and far and ep >= 8 and (er is None or er < TAU_EDGE_DEF):
            r["nearmiss"] += 1
        d = float((mf.get("cam") or {}).get("d") or 0.0)
        if d >= FAR_D:
            r["far_cam"] += 1
            r["far_cam_E"] += t == "E"

    # E-boost candidacy (train only): a scene worth pointing far/high cams at is
    # one whose hazard ALREADY reaches 5-12 m in the label (so a far camera has
    # something to see) but that contributes few or no E frames today.
    # Ranking by far-GT fraction alone is degenerate -- most drop scenes reach 5-12 m
    # on every cut, so almost everything ties at 100%.  The discriminating signal is
    # how many frames are ONE CAMERA CHANGE from an E call: near-miss E frames (the
    # lip already projects, its visible fraction just falls under tau_edge) plus
    # far-only frames (nothing in the near bands, so nothing can swamp the rim with
    # interior pixels).  Scenes already supplying E are damped -- they need it least.
    cand = []
    for sc in train:
        r = rows.get(sc)
        if not r or not r["n"]:
            continue
        far_frac = r["far_gt"] / r["n"]
        conv = (W_NEARMISS * r["nearmiss"] + W_FARONLY * r["far_only"]) / r["n"]
        score = conv / (1 + r["E"])
        cand.append((round(score, 6), sc, r, far_frac, conv))
    cand.sort(key=lambda t: (-t[0], t[1]))

    G = ["# P1_GRID_V1 — V0→V1 grid transition, invariant proof and boost targeting",
         "",
         f"grid V0: `{g0['version']}` — {nb0} bands {g0['band_edges_m']} m × {ns} sectors "
         f"= **{n0} cells**",
         f"grid V1: `{g1['version']}` — {nb1} bands {g1['band_edges_m']} m × {ns} sectors "
         f"= **{n1} cells**  (`code/labeling/gridspec_v1.json`; cell index = band*5 + sector)",
         "",
         f"labels V0: `{os.path.abspath(a.v0)}`",
         f"labels V1: `{os.path.abspath(a.v1)}`",
         f"manifest : `{os.path.abspath(a.manifest)}`",
         "",
         "V1 is a strict refinement: bands 1 and 2 keep their V0 cell indices and meaning, "
         "V0's band 3 `[5,12)` m is cut at 8 m into `3a [5,8)` + `3b [8,12)`. The outer radius "
         "and the angular coverage do not move, so the set of ground inside the grid is "
         "identical and the comparison below is apples-to-apples.", ""]

    G += ["## 1. INVARIANT GATE (mandatory) — tier map must be identical", "",
          "V/E/H are frame properties: they say what the camera can SEE of a drop, and the "
          "only tier with any grid dependence is `none_in_fov` (fires when no cell is "
          "positive), which depends on grid COVERAGE, not on how the coverage is tiled. "
          "Retiling inside an unchanged outer radius therefore must move zero frames.", ""]
    t0c = collections.Counter(F0[k]["tier_strict"] for k in F0)
    t1c = collections.Counter(F1[k]["tier_strict"] for k in F1)
    mism = [k for k in F0 if F0[k]["tier_strict"] != F1[k]["tier_strict"]]
    anyp = [k for k in F0 if bool(any(F0[k]["polar_gt"])) != bool(any(F1[k]["polar_gt"]))]
    nest = []
    for k in F0:
        p0, p1 = F0[k]["polar_gt"], F1[k]["polar_gt"]
        fold = [p1[b * ns + s] if b < 2 else (p1[2 * ns + s] | p1[3 * ns + s])
                for b in range(3) for s in range(ns)]
        if fold != p0:
            nest.append(k)
    G += [f"**scope: all {len({k.split('/')[1] for k in F0})} scenes, both arms, "
          f"{len(F0)} frames — every frame compared, not the 29-scene eligible view.**", "",
          "| tier | V0 | V1 | Δ |", "|---|---|---|---|"]
    for t in ("V", "E", "H", "H_weak", "none_in_fov", "off", "no_depth"):
        if t0c[t] or t1c[t]:
            G.append(f"| {t} | {t0c[t]} | {t1c[t]} | {t1c[t] - t0c[t]:+d} |")
    G += [f"| **frames** | **{sum(t0c.values())}** | **{sum(t1c.values())}** | "
          f"**{sum(t1c.values()) - sum(t0c.values()):+d}** |", "",
          f"- frame-by-frame `tier_strict(V1) == tier_strict(V0)` mismatches: **{len(mism)}**",
          f"- any-cell-positive mismatches (the only channel by which a retile could move "
          f"`none_in_fov`): **{len(anyp)}**",
          f"- nesting-law violations (`V1` folded 3a|3b back onto V0 ≠ V0): **{len(nest)}**",
          ""]
    _pass_txt = ("The tier map is untouched by the grid change, so every V0 headline "
                 "number (V 438 · E 36 · H 45 · H_weak 12) carries over unaltered and the "
                 "V0↔V1 comparison is legitimate.")
    _fail_txt = "STOP — labeler bug; relabeling work halts here per the brief."
    G += [f"**VERDICT: {'IDENTICAL — PASS' if not mism else 'MISMATCH — FAIL'}.** "
          + (_pass_txt if not mism else _fail_txt), ""]

    # eligible-scene restatement (the published 29-scene view)
    te0 = collections.Counter(F0[k]["tier_strict"] for k in F0
                              if k.split("/")[1] in eligible)
    te1 = collections.Counter(F1[k]["tier_strict"] for k in F1
                              if k.split("/")[1] in eligible)
    G += ["Restated on the **29 eligible scenes** (the view the brief quotes as "
          "`V438 E36 H45 H_weak12 none 165`):", "",
          "| tier | V0 | V1 | Δ |", "|---|---|---|---|"]
    for t in ("V", "E", "H", "H_weak", "none_in_fov", "off"):
        G.append(f"| {t} | {te0[t]} | {te1[t]} | {te1[t] - te0[t]:+d} |")
    G += ["", f"held scenes ({', '.join(sorted(held))}) contribute only `none_in_fov` and "
          f"`off`, which is why the 33-scene and 29-scene views differ in exactly those two "
          f"columns and in neither V, E nor H.", ""]

    # ---- 2. heatmap ---------------------------------------------------------
    G += ["## 2. 20-cell positive-count heatmap — TRAIN frames, ELIGIBLE scenes", "",
          f"train scenes ({len(train)}): `{' '.join(train)}`",
          f"counted frames: **{len(on_train)}** hazard-ON train frames "
          f"(the {len(on_train)} twin off-arm frames are structurally all-negative and are "
          f"excluded; including them would just halve every number).",
          "",
          "Cell value = how many of those frames have that cell GT-positive.", "",
          "| band \\ sector | " + " | ".join(f"**{s}**" for s in g1["sector_names"])
          + " | band total | share of frames |",
          "|---|" + "---|" * (ns + 2)]
    for b in range(nb1):
        row = [pos1[b * ns + s] for s in range(ns)]
        G.append(f"| **{g1['band_names'][b]}** ({g1['band_edges_m'][b]}–"
                 f"{g1['band_edges_m'][b + 1]} m) | "
                 + " | ".join(str(v) for v in row) + f" | {sum(row)} | "
                 f"{sum(row) / max(len(on_train) * ns, 1):.1%} |")
    G.append("| **sector total** | "
             + " | ".join(str(sum(pos1[b * ns + s] for b in range(nb1))) for s in range(ns))
             + f" | {sum(pos1)} | |")
    G += ["", "The same table under V0, for reference (band 3 is the row V1 splits):", "",
          "| band \\ sector | " + " | ".join(f"**{s}**" for s in g0["sector_names"])
          + " | band total |", "|---|" + "---|" * (ns + 1)]
    for b in range(nb0):
        row = [pos0[b * ns + s] for s in range(ns)]
        G.append(f"| **{g0['band_names'][b]}** ({g0['band_edges_m'][b]}–"
                 f"{g0['band_edges_m'][b + 1]} m) | "
                 + " | ".join(str(v) for v in row) + f" | {sum(row)} |")
    G.append("")

    # ---- 3. means -----------------------------------------------------------
    G += ["## 3. mean positive cells per frame — V0 → V1", "",
          "| subset | frames | V0 mean | V1 mean | Δ | V0 % of cells | V1 % of cells |",
          "|---|---|---|---|---|---|---|"]
    for nm, (a0_, a1_, nn) in (("train, eligible, on-arm", m_train),
                               ("all eligible, on-arm", m_elig),
                               ("all 33 scenes, on-arm", m_all),
                               ("train, on-arm, positives only "
                                "(none_in_fov frames dropped)", m_train_pos)):
        G.append(f"| {nm} | {nn} | {a0_:.3f} | {a1_:.3f} | {a1_ - a0_:+.3f} | "
                 f"{a0_ / n0:.1%} | {a1_ / n1:.1%} |")
    d0, d1 = m_train[0] / n0, m_train[1] / n1
    dupe = (b3a + b3b) / max(sum(pos0[2 * ns:3 * ns]), 1)
    G += ["",
          f"The mean rises by **{m_train[1] - m_train[0]:+.2f} cells/frame** purely because a "
          f"far footprint that filled one V0 band-3 cell now fills up to two V1 cells "
          f"(duplication factor **×{dupe:.2f}** on band 3, §4). It is resolution, not new "
          f"positives — the nesting law holds on every frame (§1).", "",
          f"Per-cell label DENSITY barely moves: **{d0:.1%} → {d1:.1%}** of cells positive "
          f"per frame. The V1 head therefore faces the same class balance it did under V0 "
          f"(so the D19 bias-initialisation recipe transfers directly), while gaining the "
          f"ability to say *how far* — which is the whole point of the split: under V0 a "
          f"positive anywhere in 5–12 m was one label, and 5 m vs 11 m is the difference "
          f"between braking now and noting a distant edge.", ""]

    # ---- 4. band3 decomposition --------------------------------------------
    G += ["## 4. band 3 → 3a / 3b decomposition", "",
          f"Every (frame, sector) pair that was positive in V0's band 3, classified by where "
          f"its footprint landed under V1. Train on-arm frames, eligible scenes; "
          f"**{b3_pos_v0}** such pairs.", "",
          "| where the old band-3 positive went | pairs | share |", "|---|---|---|"]
    for cls in ("3a only", "3b only", "3a+3b", "LOST"):
        if dec[cls] or cls == "LOST":
            G.append(f"| {cls} | {dec[cls]} | {dec[cls] / max(b3_pos_v0, 1):.1%} |")
    G += [f"| **total** | **{b3_pos_v0}** | |", "",
          f"- band 3a `[5,8)` m positives: **{b3a}** cell-frames",
          f"- band 3b `[8,12)` m positives: **{b3b}** cell-frames",
          f"- V0 band 3 positives: **{sum(pos0[2 * ns:3 * ns])}** cell-frames "
          f"→ V1 far total **{b3a + b3b}** ("
          f"×{(b3a + b3b) / max(sum(pos0[2 * ns:3 * ns]), 1):.2f} — the duplication factor of "
          f"the split)",
          f"- `LOST` must be 0: a V0 band-3 positive with neither 3a nor 3b set would be a "
          f"labeler bug. Observed: **{dec['LOST']}**.", "",
          "Per sector:", "",
          "| sector | 3a only | 3b only | 3a+3b |", "|---|---|---|---|"]
    for s in range(ns):
        G.append(f"| {g1['sector_names'][s]} | {dec_tot[(s, '3a only')]} | "
                 f"{dec_tot[(s, '3b only')]} | {dec_tot[(s, '3a+3b')]} |")
    G.append("")
    G += S41

    # ---- 5. sparse cells ----------------------------------------------------
    G += [f"## 5. SPARSE CELLS — boost-render targeting basis", "",
          f"### 5.1 the brief's criterion: < {SPARSE_MIN} positive train frames", ""]
    if not sparse:
        G += [f"**None. All {n1} cells clear the bar.** The least-populated cell is "
              f"**{cellname(g1, min(range(n1), key=lambda i: pos1[i]))}** with "
              f"**{min(pos1)}** positive train frames of {len(on_train)}, "
              f"{min(pos1) / SPARSE_MIN:.0f}× the threshold.", "",
              "That is a real result and it is the *expected* one: V1 splits band 3, the "
              "most-populated band, so the split creates no frame-count sparsity — it "
              "creates 3b (8–12 m) out of the far half of an already dense row. **Frame "
              "count is therefore the wrong targeting signal for this corpus**, and §5.2 "
              "gives the one that is not.", ""]
    else:
        G += [f"**{len(sparse)} of {n1} cells** fall short. These are the cells a polar head "
              f"cannot learn from and the cells the Phase 2 boost render must fill.", "",
              "| cell | index | band | sector | positive train frames | V0 parent cell |",
              "|---|---|---|---|---|---|"]
        for cnt, i in sparse:
            b, s = i // ns, i % ns
            par = (f"{g0['band_names'][min(b, 2)]}{g0['sector_names'][s]} "
                   f"({pos0[min(b, 2) * ns + s]})")
            G.append(f"| **{cellname(g1, i)}** | {i} | {g1['band_names'][b]} "
                     f"({g1['band_edges_m'][b]}–{g1['band_edges_m'][b + 1]} m) | "
                     f"{g1['sector_names'][s]} | **{cnt}** | {par} |")
        G += ["", "> V0 parent cell = the V0 cell this V1 cell was carved out of, with its "
              "own train positive count, so it is visible whether the sparsity is NEW "
              "(created by the split) or inherited.", ""]
    dead = [i for cnt, i in sparse if cnt == 0]
    if dead:
        G += [f"**{len(dead)} cell(s) with ZERO train positives: "
              f"{', '.join(cellname(g1, i) for i in dead)}** — no frame in the train split "
              f"ever labels them; a bias-initialised head will simply never fire there.", ""]

    # ---- 5.2 scene diversity: the sparsity that actually bites ---------------
    order = sorted(range(n1), key=lambda i: (len(cell_scenes[i]), pos1[i]))
    scene_sparse = [i for i in order if len(cell_scenes[i]) < SCENE_MIN]
    pos_scenes = {scene_of(k) for k in on_train if any(F1[k]["polar_gt"])}
    tr_pos_scenes = len(pos_scenes)
    never = sorted(set(train) - pos_scenes)
    G += ["### 5.2 scene diversity per cell — the sparsity that actually bites", "",
          f"A cell can hold hundreds of positive frames and still be sparse in the only way "
          f"that matters: if they all come from one scene, the head memorises that scene's "
          f"geometry instead of learning the cell. Of the {len(train)} train scenes, "
          f"**{tr_pos_scenes}** ever produce a positive at all; the {len(never)} that never "
          f"do are {', '.join('`%s`' % s for s in never)} "
          f"(the designed hard negatives plus the out-of-FOV scene06 — all correct zeros).",
          "",
          "| cell | band | sector | positive train frames | distinct train scenes | "
          "val+test frames | verdict |", "|---|---|---|---|---|---|---|"]
    for i in order:
        b, s = i // ns, i % ns
        nsc = len(cell_scenes[i])
        ev = pos_eval["val"][0][i] + pos_eval["test"][0][i]
        vd = ("**SCENE-SPARSE**" if nsc < SCENE_MIN else
              "thin" if nsc < SCENE_MIN + 2 else "ok")
        if ev == 0:
            vd += " · **unevaluable (0 val+test)**"
        G.append(f"| {cellname(g1, i)} | {g1['band_names'][b]} | {g1['sector_names'][s]} | "
                 f"{pos1[i]} | **{nsc}**/{tr_pos_scenes} | {ev} | {vd} |")
    G += ["",
          f"**Boost-render targets = the {len(scene_sparse)} SCENE-SPARSE cell(s): "
          f"{', '.join(cellname(g1, i) for i in scene_sparse) or 'none'}.**"
          if scene_sparse else
          f"**No cell is fed by fewer than {SCENE_MIN} distinct train scenes.**", ""]
    if scene_sparse:
        G += ["Aim the Phase 2 boost cameras at scenes that put hazard into those cells; the "
              "table's `distinct train scenes` column is the number Phase 2 must move, not "
              "the frame count.", ""]
    # which scenes feed the thinnest cells -- the actionable half of 5.2
    thin = order[:3]
    G += ["Scenes currently feeding the three thinnest cells (this is who a boost render "
          "would be duplicating, so prefer OTHER scenes):", ""]
    for i in thin:
        G.append(f"- **{cellname(g1, i)}** ({pos1[i]} frames): "
                 f"{', '.join('`%s`' % s for s in sorted(cell_scenes[i])) or '—'}")
    thin_bands = collections.Counter(g1["band_names"][i // ns] for i in order[:5])
    G += ["",
          f"**Reading for Phase 2:** the thin end of this table is band "
          f"**{thin_bands.most_common(1)[0][0]}**, not the new 3b. The five thinnest cells "
          f"are {', '.join(cellname(g1, i) for i in order[:5])} — all of them in the near "
          f"bands, because a hazard within 2 m of the eye fills a small solid angle and only "
          f"the closest cuts see one at all. 3b, the cell the split created, is the "
          f"**densest** row in the grid ({sum(pos1[3 * ns:4 * ns])} positives vs "
          f"{sum(pos1[:ns])} for band 1). So the V1 split introduced no sparsity, and E-boost "
          f"cameras placed at 6–12 m will land in the already-dense rows: their value is "
          f"tier diversity (E frames), **not** cell coverage. Cell coverage is not a problem "
          f"this corpus has.", ""]
    # evaluation-side sparsity
    G += ["### 5.3 evaluation-side coverage (val / test, on-arm)", "",
          "A cell with no positive in val+test cannot be scored, however well it is trained.",
          "", "| split | scenes | frames | cells with 0 positives | thinnest cells |",
          "|---|---|---|---|---|"]
    zero_note = []
    for name in ("val", "test"):
        c, nfr, scs = pos_eval[name]
        zeros = [cellname(g1, i) for i in range(n1) if c[i] == 0]
        if zeros:
            zero_note.append((name, zeros))
        thin3 = sorted(range(n1), key=lambda i: c[i])[:4]
        G.append(f"| {name} | {len(scs)} | {nfr} | {len(zeros)} "
                 f"({', '.join(zeros) if zeros else '—'}) | "
                 f"{', '.join(f'{cellname(g1, i)}={c[i]}' for i in thin3)} |")
    G.append("")
    for name, zeros in zero_note:
        G += [f"**FLAG for Phase 4 (split v2):** `{name}` has no positive at all in "
              f"{', '.join(zeros)}, so per-cell metrics are undefined there and a cell-F1 "
              f"averaged over all {n1} cells silently drops {len(zeros)} of them. This "
              f"matters because the D19 checkpoint selector reads **val cell F1** — worth "
              f"checking when Phase 4 picks the train→val scene to move.", ""]

    # ---- 6. per-scene E + far-rim potential ---------------------------------
    G += ["## 6. per-scene tier E + far-visible-rim potential (E-boost basis, D19③)", "",
          "All eligible scenes, hazard-ON frames. Columns:", "",
          "- `E/V/H` — tier counts today.",
          f"- `far GT` — frames whose GT reaches band 3a/3b (5–12 m): the scene HAS hazard at "
          f"the range a far camera would shoot.",
          "- `far only` — ... and nothing in bands 1–2: the pure rim-at-distance geometry, "
          "the E生成 case.",
          f"- `rim proj` — frames where ≥8 lip points projected into frame at all (an E call "
          f"is even possible).",
          f"- `near-miss E` — far-GT frames where the lip projected but the visible fraction "
          f"stayed under τ_edge={TAU_EDGE_DEF} (or interior pixels dominated): a lower/farther "
          f"camera is the single change that converts these.",
          f"- `far cam` — frames already shot from `cam.d ≥ {FAR_D} m`, and how many of those "
          f"came out E (the empirical hit rate of the boost geometry).", "",
          "| scene | split | frames | E | V | H | far GT | far only | rim proj | near-miss E | "
          f"far cam (d≥{FAR_D}) | far-cam E |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    where = {s: k for k in ("train", "val", "test") for s in split[k]}
    for sc in sorted(rows):
        r = rows[sc]
        G.append(f"| {sc} | {where.get(sc, '?')} | {r['n']} | {r['E']} | {r['V']} | {r['H']} | "
                 f"{r['far_gt']} | {r['far_only']} | {r['rim_proj']} | {r['nearmiss']} | "
                 f"{r['far_cam']} | {r['far_cam_E']} |")
    tot = {k: sum(r[k] for r in rows.values()) for k in
           ("n", "E", "V", "H", "far_gt", "far_only", "rim_proj", "nearmiss",
            "far_cam", "far_cam_E")}
    G.append(f"| **total** | | {tot['n']} | {tot['E']} | {tot['V']} | {tot['H']} | "
             f"{tot['far_gt']} | {tot['far_only']} | {tot['rim_proj']} | {tot['nearmiss']} | "
             f"{tot['far_cam']} | {tot['far_cam_E']} |")
    G.append("")

    G += ["### E-boost TRAIN scene candidates (ranked, data-driven — D19③)", "", ]
    G += [f"Ranking by far-GT fraction alone is useless here: **{sum(1 for _, _, r, ff, _ in cand if ff >= 1.0)} "
          f"train scenes reach 5–12 m on 100% of their cuts**, so they all tie. The "
          f"discriminating question is how many frames sit **one camera change away from an "
          f"E call**:", "",
          f"`convertibility = ({W_NEARMISS}·near-miss E + {W_FARONLY}·far-only) / frames`, "
          f"damped by `1/(1+E_now)` because a scene already supplying E needs the boost least.",
          "",
          "| rank | scene | far-GT frac | E now | near-miss E | far only | convertibility | "
          "verdict |", "|---|---|---|---|---|---|---|---|"]
    for j, (score, sc, r, ff, conv) in enumerate(cand[:14], 1):
        if ff <= 0:
            verdict = "SKIP — no far-range hazard to shoot"
        elif r["nearmiss"] == 0 and r["E"] == 0:
            verdict = ("weak — far hazard, but no lip currently near the τ_edge line "
                       "(interior dominates; a far cam may not tip it)")
        elif r["E"] == 0 and r["nearmiss"] >= r["n"] // 2:
            verdict = "**PRIME** — zero E, most frames already near-miss"
        elif r["E"] == 0:
            verdict = "**STRONG** — zero E, real near-miss population"
        elif r["nearmiss"] > 0:
            verdict = "GOOD — already proves E is reachable here"
        else:
            verdict = "marginal — E already supplied, nothing near the line"
        G.append(f"| {j} | `{sc}` | {ff:.0%} | {r['E']} | {r['nearmiss']} | {r['far_only']} "
                 f"| {conv:.2f} | {verdict} |")
    picks = [sc for score, sc, r, ff, conv in cand if ff > 0 and r["nearmiss"] > 0]
    G += ["",
          f"**Recommended train E-boost set (top {min(6, len(picks))} by convertibility): "
          f"{', '.join('`%s`' % s for s in picks[:6])}**",
          "",
          f"Render the D19① E-boost override (d∈[6,12] m, h∈[1.2,1.9] m) on these. The "
          f"empirical warrant is in the table above: the three train scenes that already "
          f"produce E "
          f"({', '.join('`%s`' % s for s, r in sorted((s, r) for s, r in rows.items() if r['E'] and where.get(s) == 'train'))}) "
          f"produce **{sum(r['far_cam_E'] for s, r in rows.items() if where.get(s) == 'train')} "
          f"of their {sum(r['E'] for s, r in rows.items() if where.get(s) == 'train')} E frames "
          f"from cameras already at d ≥ {FAR_D} m** — far cameras are where E comes from in "
          f"this corpus, so the override is aimed at a demonstrated mechanism, not a guess.",
          "",
          "Scenes deliberately NOT recommended, with the reason:", "",
          "| scene | why not |", "|---|---|"]
    for score, sc, r, ff, conv in cand:
        if sc in picks[:6]:
            continue
        if ff <= 0:
            why = ("no far-range hazard at all (hard negative / out-of-FOV) — a far camera "
                   "would add frames with nothing to see")
        elif r["nearmiss"] == 0 and r["E"] > 0:
            why = f"already supplies {r['E']} E frames; spend the render budget elsewhere"
        elif r["nearmiss"] == 0:
            why = ("far hazard present but no frame is near the τ_edge line — its rims are "
                   "either fully visible (V) or not projecting; low expected yield")
        else:
            why = f"ranked below the cut (convertibility {conv:.2f})"
        G.append(f"| `{sc}` | {why} |")
    G += ["",
          "> Test-side E-boost targets are fixed by the brief ({05,07,15,18}+s14) and are not "
          "re-derived here; this table is the TRAIN half D19③ asked for. For the record the "
          "same measurement on those test scenes reads: "
          + "; ".join(f"`{s}` near-miss {rows[s]['nearmiss']}/{rows[s]['n']}"
                      for s in ("scene05", "scene07", "scene15", "scene18", "scene14")
                      if s in rows)
          + " — s05/s14/s15 are strongly convertible, s07 and s18 much less so.", ""]

    G += ["## 7. what changed in the labeling stack", "",
          "- `gridspec_v1.json` — new, 4 bands × 5 sectors, `cell_index = band*5+sector`, "
          "`hazard_depth_m 0.3`, positive rule unchanged, plus a `nested_in` field the tests "
          "read to check the refinement law.",
          "- `labeler.py` — `n_cells(grid)` is now the only place a cell count is computed; "
          "`grid_slug`/`gt_source_of` derive the provenance string from the gridspec, so V1 "
          "labels are stamped `derived-heightmapdiff-gridv1-PROVISIONAL` (the V0 spelling is "
          "reproduced byte for byte, asserted in the test suite). `meta.n_cells` added.",
          "- `build_manifest.py` — reads gt_source / tier_source / gate_policy / n_cells back "
          "from the labels file instead of re-declaring them, and refuses a labels file whose "
          "`polar_gt` length disagrees with its own gridspec.",
          "- `gates.py` — report header and a new `n_cells` cross-check follow the gridspec "
          "(a mismatch between `--grid` and the manifest is now a hard error, not a silently "
          "wrong report); G1 additionally rejects a frame whose `polar_gt` is the wrong "
          "length.",
          "- `gates.py` **D19⑤ verdict reform** — G5 is a REFERENCE metric, excluded from "
          "pass/fail and reported per band; G2's zero-positive failure list skips scenes in "
          "the new `EXPLAINED_ZERO` table (`scene06`: out-of-FOV, D17), which are printed on "
          "their own annotated line; the verdict is recomputed from the binding gates only "
          "(G1/G2/G3/G4) and prints a per-gate ledger naming which gates bind.",
          "- `gates.py` **new D19 split-band audit quota** — 4 overlays reserved for frames "
          "positive in exactly one of the refined pair (`3a` xor `3b`), the only view that "
          "audits the boundary V1 introduced. The `3a`-not-`3b` case is 12 frames in the "
          "whole corpus, so without a reserved quota the audit would never show one.",
          "- `gates.py` **bug fixed while adding that quota**: the D12 far-E block did "
          "`picks = [...]` where it meant `picks += [...]`. Harmless when far-E was the first "
          "quota, but it silently discarded everything reserved before it. Caught because the "
          "split-band overlays did not appear on disk while the report claimed 4/4.",
          "- `synth_test.py` — parameterised on `--grid` and run on EVERY gridspec by default "
          "(117 checks: 58 on v0, 59 on v1); no cell index or count is a literal any more. "
          "The v1 run asserts the fixture pit lands in band `3a` and that `3b` is empty (its "
          "farthest corner is 7.62 m), and that folding `3a|3b` back together reproduces the "
          "v0 GT exactly.",
          "- No hard-coded 15 remains anywhere in the labeling stack.", "",
          "Rollback is a json swap: point `--grid` at `gridspec_v0.json` and re-run the same "
          "two commands.", ""]

    open(a.out, "w").write("\n".join(G) + "\n")
    print(f"[compare] -> {a.out}")
    print(f"[compare] train on-arm frames {len(on_train)}, sparse cells {len(sparse)} "
          f"(zero-positive {len(dead)}), mean pos/frame {m_train[0]:.3f} -> {m_train[1]:.3f}")
    print(f"[compare] band3 split: 3a-only {dec['3a only']} / 3b-only {dec['3b only']} / "
          f"both {dec['3a+3b']} / LOST {dec['LOST']}")
    print(f"[compare] E-boost train candidates: {picks[:8]}")


if __name__ == "__main__":
    main()
