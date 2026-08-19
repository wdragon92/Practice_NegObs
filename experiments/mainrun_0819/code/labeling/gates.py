#!/usr/bin/env python3
"""G1-G5 acceptance gates + tau sensitivity table + stratified audit overlays.

D14 adds two things: a STEP-GATE EXCLUSIONS ledger (what the D10 gate removed, in
heightmap cells and in polar GT cells) and the PROVISIONAL-HOLD list -- batch-1
non-stair drop scenes that come out all-negative are held out of every split
rather than failing G2, and are written to `annotations/hold_scenes.json` for
`make_split.py --exclude-scenes`.

D17 adds a second source for that same list: `--extra-holds`, by default
`annotations/extra_holds.json`, a hand-written JSON array of scene ids whose
hazard-ON labels are suspected WRONG rather than merely zero.  It is an input, not
a measurement -- no gate here can see a mislabel -- so it is merged into the
written hold list and tagged in the banner, and, like a D14 hold, it takes its
scenes out of G2's zero-positive failure list because a scene that is in no split
cannot contaminate one.  `--extra-holds none` ignores the default file.
"""
import argparse, collections, json, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
from labeler import project, TAU_INT, TAU_EDGE

REQ = ("frame_id", "scene_id", "round", "toggle_state", "rgb", "polar_gt",
       "polar_gt_pregate", "gate_excluded",
       "raw_vis", "tier", "tier_source", "gt_source", "cam", "cond", "notes")
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- D12 audit stratification ------------------------------------------------
FAR_E_QUOTA = 4        # overlays that must be tier E seen from far away
FAR_E_D = 8.0          # m, cam.d above which a cut counts as "far"
RESCUE_PER_SCENE = 2   # on-arm overlays reserved per depth-fusion-rescued scene
# ---- D10 slope-scene sanity: which scenes must end up with no footprint -------
RAMP_SCENES = ("sceneN4",)                 # gradual ramp -> 0 AFTER the step gate
FLAT_NEG_SCENES = ("sceneN1", "sceneN2", "sceneN3", "sceneN5")   # 0 already RAW
NEG_SCENES = set(RAMP_SCENES) | set(FLAT_NEG_SCENES)   # zero GT is the DESIGN here
# ---- D14(4) PROVISIONAL-HOLD candidates --------------------------------------
# The batch-1 non-stair drops (D13's verification duty).  If the step gate zeroes
# one of these on the hazard-ON arm it is a suspected over-exclusion, not a
# design outcome: the scene is HELD OUT of every split until the morning ruling
# instead of contaminating test with a possibly-wrong all-negative scene.
HOLD_CANDIDATES = ("sceneD1", "sceneD2", "sceneD3", "sceneD4")
HOLD_BASENAME = "hold_scenes.json"

# ---- D17 EXTRA holds ---------------------------------------------------------
# A second, hand-written hold list for scenes whose hazard-ON labels are suspected
# WRONG rather than merely zero -- the D17 mislabel risk (a toggle that moves the
# camera's own ground plane, or a near boundary outside the fused coverage, both
# of which teach "this edge is safe").  It is an INPUT, not a measurement: gates.py
# cannot detect a mislabel, so the judgement is recorded in a file and merged into
# the same PROVISIONAL-HOLD list the D14 rule produces.  Held scenes leave every
# split, so, exactly as under D14(4), they no longer fail G2 on zero positives --
# a scene that is not in the dataset cannot contaminate it.
EXTRA_HOLD_BASENAME = "extra_holds.json"
EXTRA_HOLD_TAG = "(D17 mislabel-risk)"

# ---- D15(3) documented drop per scene ----------------------------------------
# Verbatim from the corpus design table, `Docs/reports/dropoff_cue_matrix_v1.md`
# section 1.2 ("씬 키 (낙차 유형·낙차량)"), one row per scene.  The value taken is
# the row's HEADLINE (bold) drop; where the same row names a second drop the
# alternative reading is carried in DOC_DROP_ALT so a scene is not called a
# mismatch for measuring the other feature the row describes.  The N-scenes are
# hard negatives and have no row -- zero is their design, not a defect.
DOC_SRC = "Docs/reports/dropoff_cue_matrix_v1.md §1.2"
DOC_DROP = {
    "scene01": 0.60, "scene02": 3.38, "scene03": 3.20, "scene04": 1.45,
    "scene05": 0.398, "scene06": 5.005, "scene07": 4.20, "scene08": 4.50,
    "scene09": 5.50, "scene10": 6.60, "scene11": 5.505, "scene12": 1.80,
    "scene13": 3.96, "scene14": 6.00, "scene15": 4.25, "scene16": 3.00,
    "scene17": 3.20, "scene18": 2.56, "scene19": 1.80, "scene20": 2.10,
    "scene21": 2.70, "sceneC1": 2.04, "sceneC2": 2.24, "sceneC4": 2.10,
    "sceneD1": 1.20, "sceneD2": 3.00, "sceneD3": 0.80, "sceneD4": 1.15,
}
DOC_DROP_ALT = {
    "scene05": (1.60, "보울 립 0.398 m 위에 무대 −1.2/−1.6 m"),
    "scene07": (6.00, "24단 4.2 m + 남측 옹벽 1.8 m 연속 낙차"),
    "scene10": (2.30, "무가드 30° 사면 −2.3 m"),
    "scene12": (1.36, "데크단 8단 1.36 m"),
    "scene16": (0.15, "도로 연석 0.15 m"),
    "scene19": (1.95, "하부 테라스 −1.95 m"),
}
DOC_BAND = (0.50, 1.50)     # D15(3) acceptance band on measured / documented


def wedge_world(b, s, grid, eye, yaw, z, n=14):
    lo = max(grid["band_edges_m"][b], 0.05)
    hi = grid["band_edges_m"][b + 1]
    a1, a2 = grid["sector_edges_deg"][s], grid["sector_edges_deg"][s + 1]
    th = np.radians(np.linspace(a1, a2, n) + yaw)
    p = [np.stack([eye[0] + hi * np.cos(th), eye[1] + hi * np.sin(th),
                   np.full(n, z)], 1),
         np.stack([eye[0] + lo * np.cos(th[::-1]), eye[1] + lo * np.sin(th[::-1]),
                   np.full(n, z)], 1)]
    return np.concatenate(p, 0)


_VCACHE = {}


def eye_of(fr):
    """Exact eye: the manifest cam dict omits lateral y, so read it back from the
    scene's variation.json (the rgb path locates the scene dir)."""
    d = os.path.dirname(fr["rgb"])
    if d not in _VCACHE:
        v = json.load(open(os.path.join(d, "variation.json")))
        cu = v["cuts"]
        _VCACHE[d] = {c["file"]: c["cam"]["eye"]
                      for c in (cu.values() if isinstance(cu, dict) else cu)}
    e = _VCACHE[d].get(os.path.basename(fr["rgb"]))
    c = fr["cam"]
    return np.array(e if e else [-c["d"], 0.0, c["ground_z"] + c["h_rel"]], float)


def draw_overlay(fr, grid, out_png):
    cam = fr["cam"]
    eye = eye_of(fr)
    z = cam["ground_z"]
    try:
        img = np.asarray(Image.open(fr["rgb"]).convert("RGB"))
    except Exception:
        img = np.zeros((1080, 1920, 3), np.uint8)
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=110)
    ax.imshow(img, extent=(0, 1920, 1080, 0))
    ax.set_xlim(0, 1920); ax.set_ylim(1080, 0); ax.axis("off")
    ns = grid["n_sectors"]
    for b in range(grid["n_bands"]):
        for s in range(ns):
            P = wedge_world(b, s, grid, eye, cam["yaw"], z)
            px, py, zc, _ = project(P, eye, cam)
            if not np.all(zc > 0.05):
                continue
            xy = np.stack([np.clip(px, -4000, 6000), np.clip(py, -4000, 6000)], 1)
            pos = fr["polar_gt"][b * ns + s]
            ax.add_patch(Polygon(xy, closed=True, fill=pos == 1,
                                 facecolor="#e8413c" if pos else "none", alpha=0.35,
                                 edgecolor="#25e0d0" if pos else "#ffd400",
                                 lw=1.6 if pos else 0.9))
            c = xy.mean(0)
            if 0 < c[0] < 1920 and 0 < c[1] < 1080:
                ax.text(c[0], c[1], f"{grid['band_names'][b]}{grid['sector_names'][s]}",
                        color="w", fontsize=7, ha="center", va="center")
    rv = fr["raw_vis"]
    ax.set_title(f"{fr['frame_id']}  |  tier={fr['tier']}  int_px={rv['int_px']}  "
                 f"edge_ratio={rv['edge_ratio']}  proj={rv['edge_projected']}  "
                 f"gt={''.join(str(v) for v in fr['polar_gt'])}", fontsize=8)
    fig.tight_layout(); fig.savefig(out_png, bbox_inches="tight"); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit-dir", required=True)
    ap.add_argument("--labels", default="")
    ap.add_argument("--grid", default=os.path.join(HERE, "gridspec_v0.json"))
    ap.add_argument("--n-audit", type=int, default=30)
    ap.add_argument("--hold-out", default="",
                    help="D14 PROVISIONAL-HOLD scene list (JSON array). Default: "
                         "<manifest dir>/annotations/" + HOLD_BASENAME
                         + ". Always written, empty list included.")
    ap.add_argument("--extra-holds", default="",
                    help="D17 extra hold list to MERGE into the written hold list: "
                         "a JSON array of scene ids, or a comma-separated list, or "
                         "'none' to ignore the default file. Default: "
                         "<manifest dir>/annotations/" + EXTRA_HOLD_BASENAME
                         + " when that file exists.")
    a = ap.parse_args()

    man = json.load(open(a.manifest))
    frames = man["frames"]
    grid = json.load(open(a.grid))
    lab_p = a.labels or os.path.join(os.path.dirname(os.path.abspath(a.manifest)),
                                     "annotations", "labels_v0.json")
    lab = json.load(open(lab_p)) if os.path.isfile(lab_p) else None

    # ---- D17 extra holds: read BEFORE G2, they change what G2 may fail on ----
    ann_dir = os.path.join(os.path.dirname(os.path.abspath(a.manifest)), "annotations")
    xh_src, xh_raw = "", []
    if a.extra_holds.strip().lower() != "none":
        xp = a.extra_holds or os.path.join(ann_dir, EXTRA_HOLD_BASENAME)
        if a.extra_holds and not os.path.isfile(xp):     # inline comma list
            xh_raw, xh_src = [s.strip() for s in a.extra_holds.split(",") if s.strip()], "argument"
        elif os.path.isfile(xp):
            xh_raw, xh_src = json.load(open(xp)), os.path.abspath(xp)
            if not isinstance(xh_raw, list):
                raise SystemExit(f"[gates] {xp} must hold a JSON array of scene ids")
            xh_raw = [str(s) for s in xh_raw]
    known = {f["scene_id"] for f in frames}
    extra_hold = sorted({s for s in xh_raw if s in known})
    xh_unknown = sorted({s for s in xh_raw if s not in known})

    L = ["# GATES_REPORT — PROVISIONAL-GRID-V0",
         f"\nmanifest: `{os.path.abspath(a.manifest)}`  ({len(frames)} frames)",
         f"grid: `{grid['version']}`  gt_source: `{man['meta']['gt_source']}`  "
         f"tier_source: `{man['meta']['tier_source']}`",
         f"footprint: `{man['meta'].get('footprint', '?')}`  "
         f"cam convention: `{man['meta'].get('cam_convention_source')}`",
         f"gate policy: `{man['meta'].get('gate_policy', '?')}`", ""]
    hdr_end = len(L)          # D14 hold banner is spliced in here, above G1
    ok_all = True

    # ---- G1 required fields -------------------------------------------------
    excl = []
    for f in frames:
        miss = [k for k in REQ if k not in f or f[k] is None and k != "depth"]
        if miss:
            excl.append((f.get("frame_id", "?"), miss))
        elif not os.path.isfile(f["rgb"]):
            excl.append((f["frame_id"], ["rgb-file-missing"]))
    ok_all &= not excl
    L += [f"## G1 required fields — {'PASS' if not excl else 'FAIL'}",
          f"excluded frames: {len(excl)}"]
    L += [f"- `{i}` missing {m}" for i, m in excl[:40]] + [""]

    # ---- G2 off-arm zero + on-arm coverage ---------------------------------
    viol = [f for f in frames if f["toggle_state"] == "off" and any(f["polar_gt"])]
    bad_sc = sorted({f["scene_id"] for f in viol})
    on_sc = collections.defaultdict(int)
    for f in frames:
        if f["toggle_state"] == "on":
            on_sc[f["scene_id"]] += int(any(f["polar_gt"]))
    # N1-N5 are hard negatives by construction (D9 note 4 / D10): zero on-arm
    # footprint is the DESIGNED outcome there, not a labeling failure.  Under the
    # retired v0 footprint sceneN4's ramp used to score positive and hid inside
    # this gate; v2 zeroes it, so it is listed apart instead of failing G2.
    zero_all = sorted(s for s, n in on_sc.items() if n == 0 and s not in NEG_SCENES)
    zero_neg = sorted(s for s, n in on_sc.items() if n == 0 and s in NEG_SCENES)
    # D14(4): a batch-1 non-stair drop at zero is HELD, not failed -- holding it
    # out of every split already removes the contamination G2 guards against, and
    # the adopt/revert call is the morning's.  Every OTHER zero-positive scene
    # still fails G2 exactly as before.
    hold_auto = [s for s in zero_all if s in HOLD_CANDIDATES]
    # D17: the hand-written extra list joins the SAME hold, whether or not the
    # scene is zero-positive -- the reason there is a suspected wrong label, not a
    # missing one.  Merged here so a held scene is out of G2's zero list too.
    hold_x = [s for s in extra_hold if s not in hold_auto]
    hold = hold_auto + hold_x
    zero_sc = [s for s in zero_all if s not in hold]
    g2 = not viol and not zero_sc
    ok_all &= g2
    L += [f"## G2 toggle sanity — {'PASS' if g2 else 'FAIL'}"
          + (f" (with {len(hold)} scene(s) on PROVISIONAL-HOLD)" if hold else ""),
          f"off-arm frames with residual footprint: {len(viol)} "
          f"(scenes flagged: {bad_sc or 'none'})"]
    if lab:
        for f in viol[:20]:
            L.append(f"- `{f['frame_id']}` cell_counts="
                     f"{lab['frames'][f['frame_id']]['cell_counts']}")
    L += [f"on-arm scenes with ZERO positive frames: {zero_sc or 'none'}",
          f"hard-negative scenes at zero (expected, excluded from the gate): "
          f"{zero_neg or 'none'}",
          f"PROVISIONAL-HOLD scenes at zero (D14(4), held out of every split "
          f"instead of failing the gate): {hold_auto or 'none'}",
          f"PROVISIONAL-HOLD scenes added by hand {EXTRA_HOLD_TAG}, held out of "
          f"every split for the same reason: {hold_x or 'none'}",
          "> residual off-arm footprint = the hazard toggle left geometry behind; "
          "REPORTED, nothing deleted.", ""]

    # ---- footprint v2 per-scene summary (D10 / D12 morning slope view) ------
    L += ["## footprint v2 per-scene summary (D10 twin-diff + step gate)", ""]
    sf = (lab or {}).get("scene_footprint")
    if not sf:
        L += ["_labels file has no `scene_footprint` block (pass --labels from a "
              "footprint-v2 labeler run)._", ""]
    else:
        L += ["| scene | arm | comps raw | comps kept | fp cells raw | fp cells kept "
              "| max diff (m) | void on/off |", "|---|---|---|---|---|---|---|---|"]
        for r in sorted(sf, key=lambda r: (r.get("scene") or "", r.get("arm") or "")):
            if "cells_raw" not in r:
                L.append(f"| {r.get('scene')} | {r.get('arm')} | — | — | — | — | — | "
                         f"ERROR {r.get('error', '?')} |")
                continue
            rng = (lambda lo, hi: str(hi) if lo == hi else f"{lo}–{hi}")
            L.append(f"| {r['scene']} | {r['arm']} | {r['comps_raw']} | "
                     f"{rng(r['comps_kept_min'], r['comps_kept_max'])} | "
                     f"{r['cells_raw']} | "
                     f"{rng(r['cells_kept_min'], r['cells_kept_max'])} | "
                     f"{r['max_diff']} | {r['void_total']}/{r['void_off_total']} |")
        L += ["> comps/cells kept are given as min–max over the scene's cuts: the step "
              "gate reads the near boundary, which is camera-dependent. Raw columns are "
              "camera-independent scene geometry.", ""]

        # explicit hard-negative sanity list
        idx = {(r.get("scene"), r.get("arm")): r for r in sf}
        L += ["### slope / illusion hard-negative check", "",
              "| scene | expectation | observed | verdict |", "|---|---|---|---|"]
        for sc in RAMP_SCENES:
            r = idx.get((sc, "on"))
            if r is None:
                L.append(f"| {sc} | 0 cells AFTER step gate | not in this run | ABSENT |")
                continue
            bad = r["cells_kept_max"] > 0 or r["comps_kept_max"] > 0
            L.append(f"| {sc} | 0 cells AFTER step gate | raw {r['cells_raw']} cells / "
                     f"{r['comps_raw']} comps -> kept {r['cells_kept_max']} cells / "
                     f"{r['comps_kept_max']} comps | "
                     f"{'**FLAG — ramp survived the gate**' if bad else 'OK'} |")
        for sc in FLAT_NEG_SCENES:
            r = idx.get((sc, "on"))
            if r is None:
                L.append(f"| {sc} | 0 cells RAW | not in this run | ABSENT |")
                continue
            bad = r["cells_raw"] > 0
            L.append(f"| {sc} | 0 cells RAW | raw {r['cells_raw']} cells / "
                     f"{r['comps_raw']} comps (max diff {r['max_diff']}) | "
                     f"{'**FLAG — twin arms differ in geometry**' if bad else 'OK'} |")
        L += ["> FLAG lines are REPORTED, not fatal: they say the twin-diff footprint "
              "disagrees with the hard-negative design, which is a morning judgement "
              "call (re-render vs. re-tune the step gate), not an automatic reject.", ""]

    # ---- STEP-GATE EXCLUSIONS (D14) ----------------------------------------
    # What the D10 step gate removed, at both granularities: heightmap cells
    # (scene geometry, from the labeler's per-scene footprint stats) and polar GT
    # cells (per frame, from `gate_excluded`).  Nothing here is a gate: it is the
    # ledger the morning ruling reads before adopting or reverting the gate.
    sfi = {(r.get("scene"), r.get("arm")): r for r in (sf or [])}
    fx = collections.defaultdict(lambda: [0, 0, 0])      # n_frames, n_excl, sum
    for f in frames:
        k = (f["scene_id"], f["toggle_state"])
        ge = f.get("gate_excluded") or {}
        n = int(ge.get("n") or 0)
        fx[k][0] += 1
        fx[k][1] += int(n > 0)
        fx[k][2] += n
    L += ["## STEP-GATE EXCLUSIONS (D14)", "",
          "| scene | arm | hm cells raw | hm cells kept | hm cells excluded | "
          "frames w/ gate_excluded | excluded GT cells (sum) |",
          "|---|---|---|---|---|---|---|"]
    span = (lambda lo, hi: str(hi) if lo == hi else f"{lo}–{hi}")   # noqa: E731
    tot_fr, tot_gt = 0, 0
    for k in sorted(fx):
        n_fr, n_ex, s_ex = fx[k]
        tot_fr += n_ex; tot_gt += s_ex
        r = sfi.get(k)
        if r and "cells_raw" in r:
            hm = [str(r["cells_raw"]),
                  span(r["cells_kept_min"], r["cells_kept_max"]),
                  span(r.get("hm_cells_excluded_min",
                             r["cells_raw"] - r["cells_kept_max"]),
                       r.get("hm_cells_excluded_max",
                             r["cells_raw"] - r["cells_kept_min"]))]
        else:
            hm = ["—", "—", "—"]
        L.append(f"| {k[0]} | {k[1]} | {hm[0]} | {hm[1]} | {hm[2]} | "
                 f"{n_ex}/{n_fr} | {s_ex} |")
    L += [f"| **total** | | | | | **{tot_fr}/{len(frames)}** | **{tot_gt}** |", "",
          "> hm cells kept/excluded are min–max over the scene's cuts (the gate reads the "
          "camera-facing near boundary, so it is per-cut); raw is camera-independent. "
          "`gate_excluded` = polar cells positive in `polar_gt_pregate` but not in the "
          "trained `polar_gt`. Per D14 the pre-gate label is preserved on every frame, so "
          "reverting the gate is a field swap (`polar_gt` <-> `polar_gt_pregate`), not a "
          "re-derivation.", ""]

    # ---- G3 strict-H distribution ------------------------------------------
    per = collections.defaultdict(collections.Counter)
    for f in frames:
        per[f["scene_id"]][f["tier"]] += 1
    tot = collections.Counter(f["tier"] for f in frames)
    nH = tot.get("H", 0)
    ok_all &= nH > 0
    L += [f"## G3 strict-H distribution — {'PASS' if nH else 'FAIL (no H frames)'}",
          f"totals: {dict(tot)}", "", "| scene | H | H_weak | V | E | none_in_fov | off |",
          "|---|---|---|---|---|---|---|"]
    for s in sorted(per):
        c = per[s]
        L.append(f"| {s} | {c['H']} | {c['H_weak']} | {c['V']} | {c['E']} | "
                 f"{c['none_in_fov']} | {c['off']} |")
    L.append("")

    # ---- G5 V-tier cross-check ---------------------------------------------
    ns = grid["n_sectors"]
    ag, per_band = [], collections.defaultdict(lambda: [0, 0])
    for f in frames:
        if f["tier"] != "V":
            continue
        ci = f["raw_vis"].get("cell_int_px") or []
        pos = [i for i, v in enumerate(f["polar_gt"]) if v]
        if pos and len(ci) == len(f["polar_gt"]):
            ag.append(sum(1 for i in pos if ci[i] > 0) / len(pos))
            for i in pos:
                per_band[i // ns][0] += int(ci[i] > 0); per_band[i // ns][1] += 1
    mean_ag = float(np.mean(ag)) if ag else float("nan")
    g5 = bool(ag) and mean_ag >= 0.80
    ok_all &= g5
    L += [f"## G5 V-tier depth/GT agreement — {'PASS' if g5 else 'FAIL/NA'}",
          f"V frames scored: {len(ag)}   mean agreement: {mean_ag:.3f}  (target >= 0.80)",
          "> fraction of GT-positive cells holding >=1 reprojected below-ground pixel.", "",
          "| band | agreement | positive cells |", "|---|---|---|"]
    for b in sorted(per_band):
        h, n = per_band[b]
        L.append(f"| {grid['band_names'][b]} ({grid['band_edges_m'][b]}-"
                 f"{grid['band_edges_m'][b + 1]} m) | {h / n:.3f} | {n} |")
    L += ["> A near band scoring low is expected geometry, not a labeling fault: a drop's "
          "floor right behind the lip sits in the camera's view shadow, so its cell is "
          "GT-positive with no visible below-ground surface. Judge the 0.80 target on the "
          "far bands, or re-cut the target, before treating G5 as a data defect.", ""]

    # ---- tau sensitivity ----------------------------------------------------
    L += ["## tau sensitivity (tier distribution, on-arm frames)", "",
          "| tau_int | tau_edge | V | E | H | H_weak | none_in_fov |", "|---|---|---|---|---|---|---|"]
    if lab:
        onf = [v for k, v in lab["frames"].items() if k.startswith("on/")]
        for ti in TAU_INT:
            for te in TAU_EDGE:
                c = collections.Counter(v["tier_matrix"][f"i{ti}_e{te}"] for v in onf)
                L.append(f"| {ti} | {te} | {c['V']} | {c['E']} | {c['H']} | "
                         f"{c['H_weak']} | {c['none_in_fov']} |")
    else:
        L.append("| — | — | labels_v0.json not found; pass --labels | | | | |")
    L.append("")

    # ---- G4 audit overlays --------------------------------------------------
    os.makedirs(os.path.abspath(a.audit_dir), exist_ok=True)
    by = collections.defaultdict(list)
    for f in frames:
        by[f["tier"]].append(f)

    # D12 quota FIRST: far-away E frames are the ones the morning audit needs most
    # (an E call at cam.d > 8 m is where the lip-visibility rule is weakest).
    far = [f for f in by["E"] if float(f["cam"].get("d") or 0.0) > FAR_E_D]
    far.sort(key=lambda f: f["frame_id"])
    picks = []
    if far:
        sel = sorted(set(np.linspace(0, len(far) - 1,
                                     min(FAR_E_QUOTA, len(far))).astype(int).tolist()))
        picks = [far[i] for i in sel]
    taken = {f["frame_id"] for f in picks}
    for t in list(by):
        by[t] = [f for f in by[t] if f["frame_id"] not in taken]
    far_short = len(picks) < FAR_E_QUOTA

    # Rescue quota: a scene whose heightmap came from depth fusion is measured by
    # an instrument that did not exist when the rest of the corpus was labelled,
    # so its overlays are the ones the morning most needs to eyeball.  Reserved
    # here, before the round-robin, or the median-of-tier fill never reaches them.
    rescued = sorted({r["scene"] for r in (sf or []) if r.get("hm_source") == "fused"
                      or r.get("hm_source_off") == "fused"})
    n_rescue = 0
    for sc in rescued:
        cand = sorted((f for f in frames
                       if f["scene_id"] == sc and f["toggle_state"] == "on"
                       and f["frame_id"] not in taken),
                      key=lambda f: f["frame_id"])
        if not cand:
            continue
        sel = sorted(set(np.linspace(0, len(cand) - 1,
                                     min(RESCUE_PER_SCENE, len(cand))).astype(int).tolist()))
        for i in sel:
            picks.append(cand[i]); taken.add(cand[i]["frame_id"]); n_rescue += 1
    for t in list(by):
        by[t] = [f for f in by[t] if f["frame_id"] not in taken]

    order = [t for t in ("V", "E", "H", "off", "H_weak", "none_in_fov", "no_depth") if by[t]]
    i = 0
    while len(picks) < a.n_audit and order:
        t = order[i % len(order)]
        if by[t]:
            picks.append(by[t].pop(len(by[t]) // 2))
        else:
            order.remove(t); i -= 1
        i += 1
    written = []
    for f in picks:
        p = os.path.join(a.audit_dir, f["frame_id"].replace("/", "__") + ".overlay.png")
        try:
            draw_overlay(f, grid, p); written.append(p)
        except Exception as e:
            L.append(f"- overlay FAILED {f['frame_id']}: {type(e).__name__}: {e}")
    # the sample is the whole point of the directory, so a leftover overlay from an
    # earlier derivation is a wrong label sitting next to the right ones -- clear it
    keep = {os.path.abspath(p) for p in written}
    stale = [os.path.join(a.audit_dir, b) for b in sorted(os.listdir(a.audit_dir))
             if b.endswith(".overlay.png")
             and os.path.abspath(os.path.join(a.audit_dir, b)) not in keep]
    for p in stale:
        os.remove(p)
    n_far_written = sum(1 for f in picks
                        if f["tier"] == "E" and float(f["cam"].get("d") or 0.0) > FAR_E_D)
    L += [f"## G4 audit overlays — {len(written)}/{a.n_audit} written",
          f"dir: `{os.path.abspath(a.audit_dir)}`",
          f"tier mix: {dict(collections.Counter(f['tier'] for f in picks))}",
          f"D12 far-E quota (tier E and cam.d > {FAR_E_D} m): "
          f"{n_far_written}/{FAR_E_QUOTA}",
          f"depth-fusion rescue quota (on-arm frames of {rescued or 'no'} rescued "
          f"scene(s), {RESCUE_PER_SCENE} each): {n_rescue}",
          f"stale overlays from earlier derivations removed: {len(stale)}"]
    if far_short:
        L.append(f"**WARNING** only {len(far)} frame(s) in the whole labeled set are "
                 f"tier E with cam.d > {FAR_E_D} m — the D12 quota of {FAR_E_QUOTA} "
                 f"cannot be met; all of them were taken.")
    L.append("")
    ok_all &= len(written) > 0

    # ---- D15(3) measured max_diff vs the documented drop --------------------
    # REPORT ONLY.  Per D14 the automatic hold list stays D-scene-only, so a main
    # scene that disagrees with its design table is written down for the morning,
    # never silently pulled out of the split.
    L += ["## max_diff vs documented drop (D15)", "",
          f"documented drop = `{DOC_SRC}` headline value per scene; measured = the "
          f"on-arm twin-diff `max_diff` of this run; source = which heightmap "
          f"instrument the on-arm map came from (`aabb` = top-down "
          f"`AabbPrefilter.ground_z`, `fused` = `fuse_heightmap.py` depth fusion).",
          f"band = measured / documented within "
          f"[{DOC_BAND[0]:.0%}, {DOC_BAND[1]:.0%}].", "",
          "| scene | documented drop (m) | measured max_diff (m) | ratio | source "
          "(on/off) | verdict |", "|---|---|---|---|---|---|"]
    sfi_on = {r.get("scene"): r for r in (sf or []) if r.get("arm") == "on"}
    sfi_off = {r.get("scene"): r for r in (sf or []) if r.get("arm") == "off"}
    d15_mismatch, d15_broken = [], []
    for sc in sorted(DOC_DROP):
        r = sfi_on.get(sc)
        doc = DOC_DROP[sc]
        if r is None or r.get("max_diff") is None:
            L.append(f"| {sc} | {doc} | — | — | — | ABSENT (not in this run) |")
            continue
        md = float(r["max_diff"])
        src = f"{r.get('hm_source', '?')}/{sfi_off.get(sc, {}).get('hm_source', '?')}"
        ratio = md / doc if doc else float("nan")
        alt = DOC_DROP_ALT.get(sc)
        alt_ratio = (md / alt[0]) if alt else None
        note = ""
        if sc in hold_x:
            verdict = f"HOLD {EXTRA_HOLD_TAG} — held out of every split"
        elif sc in hold_auto:
            verdict = "HOLD (D14④ — held out of every split)"
        elif sc in zero_sc:
            verdict = "**BROKEN — on-arm zero positives**"; d15_broken.append(sc)
        elif DOC_BAND[0] <= ratio <= DOC_BAND[1]:
            verdict = "OK"
        elif alt_ratio is not None and DOC_BAND[0] <= alt_ratio <= DOC_BAND[1]:
            verdict = f"OK on the row's other drop ({alt[0]} m, {alt_ratio:.2f}×) — {alt[1]}"
        else:
            verdict = ("**MISMATCH — measured %s the documented drop**"
                       % ("far exceeds" if ratio > DOC_BAND[1] else "far under"))
            d15_mismatch.append((sc, doc, md, ratio)); note = ""
        if alt and "other drop" not in verdict:
            note = f" _(row also lists {alt[0]} m: {alt_ratio:.2f}×)_"
        L.append(f"| {sc} | {doc} | {md} | {ratio:.2f}× | {src} | {verdict}{note} |")
    L += ["> N-scenes (sceneN1–N5) are hard negatives with no design-table drop and "
          "are omitted: zero IS their expected measurement (see the hard-negative "
          "check above).", ""]
    if d15_mismatch:
        L += ["**FOR THE MORNING — main scenes outside the band, NOT held (D14: the "
              "automatic hold list stays D-scene-only):**", ""]
        for sc, doc, md, ratio in d15_mismatch:
            L.append(f"- `{sc}` — documented {doc} m, measured {md} m ({ratio:.2f}×). "
                     f"Its frames stay in train/val/test; decide whether to re-measure, "
                     f"re-render, or accept the design table as the stale side.")
        L.append("")
    if d15_broken:
        L += [f"**Still measuring zero on the hazard arm after the depth-fusion "
              f"rescue: {', '.join('`%s`' % s for s in d15_broken)}** — these fail G2 "
              f"above and are reported, not auto-held (D14).", ""]

    L += ["## VERDICT", f"**{'ALL GATES PASS' if ok_all else 'GATE FAILURE — see above'}**", ""]

    # ---- D14(4) PROVISIONAL-HOLD: banner at the very top + machine-readable --
    hold_p = os.path.abspath(a.hold_out or os.path.join(
        os.path.dirname(os.path.abspath(a.manifest)), "annotations", HOLD_BASENAME))
    os.makedirs(os.path.dirname(hold_p), exist_ok=True)
    json.dump(hold, open(hold_p, "w"), indent=1)
    if hold:
        tag = (lambda s: f"`{s}` {EXTRA_HOLD_TAG}" if s in hold_x else f"`{s}`")
        ban = ["## ⛔ PROVISIONAL-HOLD — 아침 결재 대상 (D14④ + D17)", "",
               f"**{len(hold)} scene(s) HELD OUT of train/val/test: "
               f"{', '.join(tag(s) for s in hold)}**", ""]
        if hold_auto:
            ban += [f"D14④ ({', '.join('`%s`' % s for s in hold_auto)}) — batch-1 "
                    "non-stair drop scene(s) whose hazard-ON arm carries ZERO positive "
                    "frames after the D10 step gate: a suspected over-exclusion, not a "
                    "designed hard negative. Held so a possibly-wrong all-negative scene "
                    "cannot distort the headline test metric; the adopt/revert ruling is "
                    "the morning's."]
        if hold_x:
            ban += [f"D17 mislabel-risk ({', '.join('`%s`' % s for s in hold_x)}) — "
                    "hand-listed scene(s) whose hazard-ON labels are suspected WRONG, not "
                    "merely absent; training on them would teach that a real edge is safe. "
                    "This list is an input, not a measurement — gates.py cannot detect a "
                    f"mislabel. Source: `{xh_src or 'none'}`."]
            if xh_unknown:
                ban += [f"**WARNING** — {len(xh_unknown)} id(s) in that file match no scene "
                        f"in this manifest and were IGNORED: "
                        f"{', '.join('`%s`' % s for s in xh_unknown)}."]
        ban += [f"Machine-readable: `{hold_p}`  →  "
                f"`make_split.py --exclude-scenes @{hold_p}`",
                "Reverting the gate needs no re-derivation: swap `polar_gt` <-> "
                "`polar_gt_pregate` (see STEP-GATE EXCLUSIONS below).", ""]
    else:
        ban = [f"PROVISIONAL-HOLD (D14④ + D17): none — `{hold_p}` = `[]`, every scene is "
               f"eligible for the split.", ""]
    L[hdr_end:hdr_end] = ban

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w").write("\n".join(L) + "\n")
    print(f"[gates] {'PASS' if ok_all else 'FAIL'} -> {a.out} ({len(written)} overlays, "
          f"far-E {n_far_written}/{FAR_E_QUOTA}"
          f"{' WARNING-short' if far_short else ''})")
    print(f"[gates] step-gate exclusions (D14): {tot_fr}/{len(frames)} frames lost >=1 GT "
          f"cell, {tot_gt} GT cells total")
    print(f"[gates] PROVISIONAL-HOLD: {hold or 'none'} -> {hold_p} "
          f"(D14④ {hold_auto or 'none'} + D17 extra {hold_x or 'none'}"
          f"{', ignored unknown ids ' + str(xh_unknown) if xh_unknown else ''})")


if __name__ == "__main__":
    main()
