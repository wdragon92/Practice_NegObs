#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gates_cueoff.py — the CUE-OFF gate battery (PREREG_CUEOFF.md sec.5).

Runs on CPU only.  Every gate is fail-loud and every failure is printed with the
frames that caused it, because "the gate passed" is worth nothing if the gate
cannot say what it looked at.

    G_PREREG  the pre-registration file predates every rendered artifact
    G0        arm A of the ISOLATED COPY reproduces the lineage corpus round
              (cam 8 keys identical) -- proves the copy is not the intervention
    G1        the 1-frame smoke of each ported scene landed, and its ground_z
              matches the canonical on-arm  (see run_cueoff.sh --smoke)
    G2        hazard geometry invariant: polar_gt BYTE-identical A vs B1/B2/P,
              heightmap.npy sha256 identical
    G3        pose identity across arms, 8 keys, reported in 3 strata
              pose_exact (<1e-6) / pose_tol (<=0.02 m) / pose_fail (>0.02 m)
    G4        5-category tier re-derivation per arm + H->E migration count
    G5        arm C carries an all-zero polar_gt on every frame
    G6        the frozen checkpoints were not touched

Usage
    # before the labeller (only needs variation.json)
    python3 gates_cueoff.py --stage pre
    # after the labeller
    python3 gates_cueoff.py --stage post
    python3 gates_cueoff.py --stage all --out GATES_CUEOFF.md
"""
import argparse
import collections
import datetime
import glob
import hashlib
import json
import os
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
AUDIT = os.path.join(REPO, "experiments/weekend_0823/cue_audit")
LABELS = os.path.join(AUDIT, "labels")
PREREG = os.path.join(AUDIT, "PREREG_CUEOFF.md")
CKPT_GLOB = os.path.join(REPO, "experiments/dayrun_0820/runs/v2/*_s4?/best.pt")

ARMS = ["A", "B2", "B1", "P", "C"]
# arm -> which arm it must be geometry-identical to (None = no partner)
GEOM_PARTNER = {"B2": "A", "B1": "A", "P": "A"}
CAM_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov", "ground_z")
TOL_EXACT = 1e-6
TOL_TOL = 0.02                    # metres -- the `pose_tol` stratum ceiling
TIERS5 = ("V", "E", "H", "H_weak", "none_in_fov")

# round stem -> (scene, lineage corpus round for G0)
LINEAGE = {
    ("260823_cueoff", "scene12"): "260820_boost_e_on",
    ("260823_cueoff", "scene17"): "260820_boost_h_on",
    ("260823_cueoff", "scene20"): "260820_boost_e2_on",
    ("260823_cueoff2", "scene12"): "260820_boost_e2_on",
    ("260823_cueoff3", "scene17"): "260819_main_on",
}

FAILS = []
NOTES = []


def fail(gate, msg):
    FAILS.append((gate, msg))
    print(f"  [FAIL] {gate}: {msg}")


def ok(gate, msg):
    print(f"  [ok]   {gate}: {msg}")


def note(msg):
    NOTES.append(msg)
    print(f"  [note] {msg}")


# --------------------------------------------------------------------------- io
def sha256(path, cap=None):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
            if cap and h.block_size and f.tell() > cap:
                break
    return h.hexdigest()


def round_dirs(prefix):
    """{(stem, arm): {scene: dir}} for every rendered CUE-OFF round on disk."""
    out = {}
    for d in sorted(glob.glob(os.path.join(REPO, "dataset", prefix + "*"))):
        base = os.path.basename(d)
        if "_" not in base:
            continue
        stem, arm = base.rsplit("_", 1)
        if arm not in ARMS:
            continue
        scenes = {}
        for v in sorted(glob.glob(os.path.join(d, "*", "*", "variation.json"))):
            scenes[os.path.basename(os.path.dirname(v))] = os.path.dirname(v)
        if scenes:
            out[(stem, arm)] = scenes
    return out


def cuts_of(sdir):
    v = json.load(open(os.path.join(sdir, "variation.json")))
    cu = v["cuts"]
    return {c["file"]: c for c in (cu.values() if isinstance(cu, dict) else cu)}


def load_labels(stem, arm):
    p = os.path.join(LABELS, f"{stem}_{arm}.json")
    if not os.path.isfile(p):
        return None
    return json.load(open(p))


# --------------------------------------------------------------------------- gates
def g_prereg(R):
    print("\n[G_PREREG] pre-registration predates every rendered artifact")
    if not os.path.isfile(PREREG):
        return fail("G_PREREG", f"{PREREG} does not exist")
    t_pre = os.path.getmtime(PREREG)
    newest_older = []
    n = 0
    for (stem, arm), scenes in R.items():
        for sc, d in scenes.items():
            for f in glob.glob(os.path.join(d, "*.png")):
                n += 1
                if os.path.getmtime(f) < t_pre:
                    newest_older.append(os.path.relpath(f, REPO))
    if not n:
        return note("G_PREREG: no rendered PNG yet -- vacuously satisfied so far "
                    f"(PREREG mtime {datetime.datetime.fromtimestamp(t_pre)})")
    if newest_older:
        return fail("G_PREREG",
                    f"{len(newest_older)} artifact(s) PREDATE the prereg -- the "
                    f"registration is not a registration. e.g. {newest_older[:3]}")
    ok("G_PREREG", f"{n} rendered frames, all newer than PREREG "
                   f"({datetime.datetime.fromtimestamp(t_pre):%Y-%m-%d %H:%M:%S})")


def g0_lineage(R):
    print("\n[G0] arm A of the isolated copy reproduces the lineage corpus round")
    got = False
    for (stem, arm), scenes in sorted(R.items()):
        if arm != "A":
            continue
        for sc, d in sorted(scenes.items()):
            ref_round = LINEAGE.get((stem, sc))
            if not ref_round:
                note(f"G0: no lineage mapping for {stem}/{sc} -- skipped")
                continue
            ref = glob.glob(os.path.join(REPO, "dataset", ref_round, "*", sc,
                                         "variation.json"))
            if not ref:
                note(f"G0: lineage round {ref_round}/{sc} absent -- skipped")
                continue
            got = True
            a, b = cuts_of(d), cuts_of(os.path.dirname(ref[0]))
            miss = sorted(set(b) - set(a))
            bad = []
            for fn in sorted(set(a) & set(b)):
                ca, cb = a[fn]["cam"], b[fn]["cam"]
                dv = max([abs(float(ca[k]) - float(cb[k])) for k in CAM_KEYS]
                         + [abs(float(ca["eye"][i]) - float(cb["eye"][i]))
                            for i in range(3)])
                if dv > TOL_EXACT:
                    bad.append((fn, round(dv, 8)))
            png_same = 0
            for fn in sorted(set(a) & set(b))[:8]:
                pa = os.path.join(d, fn)
                pb = os.path.join(os.path.dirname(ref[0]), fn)
                if os.path.isfile(pa) and os.path.isfile(pb) \
                        and sha256(pa) == sha256(pb):
                    png_same += 1
            tag = f"{stem}/{sc} vs {ref_round}"
            if miss:
                fail("G0", f"{tag}: {len(miss)} lineage cuts missing from arm A "
                           f"{miss[:3]}")
            if bad:
                fail("G0", f"{tag}: {len(bad)} cut(s) differ in camera "
                           f"(max |d| {max(x[1] for x in bad)}) {bad[:3]}")
            else:
                ok("G0", f"{tag}: {len(set(a) & set(b))} cuts, all 10 camera "
                         f"values identical to 1e-6 · PNG byte-identical "
                         f"{png_same}/8 sampled (bonus, not a condition)")
    if not got:
        note("G0: nothing to compare yet")


def g1_smoke(R):
    print("\n[G1] 1-frame real-render smoke of each ported scene (arm C)")
    p = os.path.join(AUDIT, "SMOKE_CUEOFF.json")
    if not os.path.isfile(p):
        return note("G1: SMOKE_CUEOFF.json absent -- run `run_cueoff.sh --smoke`")
    sm = json.load(open(p))
    for sc, rec in sorted(sm.get("scenes", {}).items()):
        if rec.get("rc") != 0 or not rec.get("cuts"):
            fail("G1", f"{sc}: smoke rc={rec.get('rc')} cuts={rec.get('cuts')}")
            continue
        dz = rec.get("ground_z_delta")
        if dz is None:
            note(f"G1: {sc} rendered but no canonical ground_z to compare")
        elif abs(dz) > TOL_EXACT:
            fail("G1", f"{sc}: arm-C ground_z moved {dz:+.6f} m vs the canonical "
                       f"on arm -- the D17/D30 datum trap. STOP.")
        else:
            ok("G1", f"{sc}: arm C rendered {rec['cuts']} cut(s) in "
                     f"{rec.get('sec', '?')} s · ground_z delta {dz:+.6f} m")


def g2_geometry(R):
    print("\n[G2] hazard geometry invariant (polar_gt byte-identical, heightmap hash)")
    for (stem, arm), scenes in sorted(R.items()):
        partner = GEOM_PARTNER.get(arm)
        if not partner or (stem, partner) not in R:
            continue
        la, lb = load_labels(stem, arm), load_labels(stem, partner)
        for sc, d in sorted(scenes.items()):
            ref = R[(stem, partner)].get(sc)
            if not ref:
                continue
            ha = os.path.join(d, "heightmap.npy")
            hb = os.path.join(ref, "heightmap.npy")
            tag = f"{stem} {sc} {arm} vs {partner}"
            if os.path.isfile(ha) and os.path.isfile(hb):
                if sha256(ha) != sha256(hb):
                    fail("G2", f"{tag}: heightmap.npy differs -- a cue_* toggle "
                               f"moved the hazard geometry. REGULATION BREACH.")
                else:
                    ok("G2", f"{tag}: heightmap.npy sha256 identical")
            else:
                note(f"G2: {tag}: heightmap.npy missing on one side")
            if la is None or lb is None:
                note(f"G2: {tag}: labels absent -- polar_gt check deferred")
                continue
            diff = []
            for fn in sorted(cuts_of(d)):
                ka, kb = f"on/{sc}/{fn}", f"on/{sc}/{fn}"
                fa, fb = la["frames"].get(ka), lb["frames"].get(kb)
                if fa is None or fb is None:
                    continue
                if fa["polar_gt"] != fb["polar_gt"]:
                    diff.append(fn)
            if diff:
                fail("G2", f"{tag}: polar_gt differs on {len(diff)} frame(s) "
                           f"{diff[:3]} -- the hazard is NOT invariant across the "
                           f"cue toggle; the arms are not comparable.")
            else:
                ok("G2", f"{tag}: polar_gt byte-identical on all "
                         f"{len(cuts_of(d))} frames")


def g3_pose(R):
    print("\n[G3] pose identity across arms (8 keys + eye, 3 strata)")
    strata = collections.Counter()
    detail = []
    for (stem, arm), scenes in sorted(R.items()):
        if arm == "A" or (stem, "A") not in R:
            continue
        for sc, d in sorted(scenes.items()):
            ref = R[(stem, "A")].get(sc)
            if not ref:
                continue
            a, b = cuts_of(d), cuts_of(ref)
            per = collections.Counter()
            worst = (0.0, None, None)
            for fn in sorted(set(a) & set(b)):
                ca, cb = a[fn]["cam"], b[fn]["cam"]
                dd = {k: abs(float(ca[k]) - float(cb[k])) for k in CAM_KEYS}
                for i, ax in enumerate("xyz"):
                    dd["eye_" + ax] = abs(float(ca["eye"][i]) - float(cb["eye"][i]))
                mk = max(dd, key=dd.get)
                dv = dd[mk]
                lvl = ("pose_exact" if dv < TOL_EXACT else
                       "pose_tol" if dv <= TOL_TOL else "pose_fail")
                per[lvl] += 1
                strata[lvl] += 1
                if dv > worst[0]:
                    worst = (dv, fn, mk)
            n = sum(per.values())
            viol = per["pose_tol"] + per["pose_fail"]
            line = (f"{stem} {sc} {arm}: exact {per['pose_exact']}/{n} · tol "
                    f"{per['pose_tol']} · FAIL {per['pose_fail']}"
                    + (f" · worst |{worst[2]}| {worst[0]:.6f} on {worst[1]}"
                       if worst[1] else ""))
            detail.append(line)
            if per["pose_fail"]:
                fail("G3", line + "  -> ground_z moved > 20 mm; investigate before use")
            elif viol and n and viol / n > 0.25:
                fail("G3", line + f"  -> {viol}/{n} = {100*viol/n:.0f}% > 25%; "
                                  f"PREREG sec.4.5-1 voids this scene-arm")
            elif viol:
                note(line + "  -> declared TOL stratum (PREREG sec.5.1); primary "
                            "readout runs on pose_exact only")
            else:
                ok("G3", line)
    if strata:
        print(f"  strata total: {dict(strata)}")
    return detail


def g4_tiers(R):
    print("\n[G4] 5-category tier re-derivation per arm + H->E migration")
    table = {}
    for (stem, arm), scenes in sorted(R.items()):
        lab = load_labels(stem, arm)
        if lab is None:
            note(f"G4: labels for {stem}_{arm} absent -- skipped")
            continue
        for sc in sorted(scenes):
            c = collections.Counter()
            for fid, f in lab["frames"].items():
                if f"/{sc}/" not in fid:
                    continue
                c[f.get("tier_strict", "?")] += 1
            table[(stem, sc, arm)] = c
            ok("G4", f"{stem} {sc} {arm}: " + " · ".join(
                f"{t} {c.get(t, 0)}" for t in TIERS5)
                + (f" · other {sum(v for k, v in c.items() if k not in TIERS5)}"
                   if any(k not in TIERS5 for k in c) else ""))
    # migration, frame by frame
    for (stem, sc, arm), _ in sorted(table.items()):
        if arm == "A" or (stem, sc, "A") not in table:
            continue
        la, lb = load_labels(stem, arm), load_labels(stem, "A")
        if la is None or lb is None:
            continue
        mig = collections.Counter()
        for fid, f in lb["frames"].items():
            if f"/{sc}/" not in fid:
                continue
            g = la["frames"].get(fid)
            if g is None:
                continue
            t0, t1 = f.get("tier_strict"), g.get("tier_strict")
            if t0 != t1:
                mig[f"{t0}->{t1}"] += 1
        paired_h = sum(1 for fid, f in lb["frames"].items()
                       if f"/{sc}/" in fid and f.get("tier_strict") == "H"
                       and (la["frames"].get(fid) or {}).get("tier_strict") == "H")
        msg = (f"{stem} {sc} A->{arm}: paired-H {paired_h}"
               + (f" · migrations {dict(mig)}" if mig else " · no tier movement"))
        if mig.get("H->E"):
            note(f"G4 {msg}  -> {mig['H->E']} H->E frames EXCLUDED from the "
                 f"primary readout and reported (CUEOFF_CANDIDATES sec.5-4)")
        else:
            ok("G4", msg)
        if arm in ("B1", "B2", "P") and paired_h < 10:
            fail("G4", f"{stem} {sc} A/{arm}: paired-H {paired_h} < 10 -- "
                       f"PREREG sec.4.5-3 voids this scene-arm")


def g5_armC(R):
    print("\n[G5] arm C carries an all-zero polar_gt on every frame")
    for (stem, arm), scenes in sorted(R.items()):
        if arm != "C":
            continue
        lab = load_labels(stem, arm)
        if lab is None:
            note(f"G5: labels for {stem}_C absent -- skipped")
            continue
        for sc in sorted(scenes):
            bad = [fid for fid, f in lab["frames"].items()
                   if f"/{sc}/" in fid and sum(f["polar_gt"]) > 0]
            n = sum(1 for fid in lab["frames"] if f"/{sc}/" in fid)
            if bad:
                fail("G5", f"{stem} {sc} C: {len(bad)}/{n} frames carry a POSITIVE "
                           f"polar_gt -- the hazard-off surgery left a drop, or the "
                           f"heightmap oracle re-imposed the ON profile. {bad[:3]}")
            else:
                ok("G5", f"{stem} {sc} C: {n}/{n} frames all-zero GT")


def g7_footprint(R):
    """PREREG amendment A1.2-(3): footprint sanity, print-only, never auto-stop.

    The twin-difference footprint is what polar_gt is CUT OUT OF, so a scene whose
    `cells_raw` has collapsed is a scene whose recall is measuring a sliver.  The
    shipped corpus already has one (scene12 in the boost rounds: 50 cells, because
    SIDECAR_ORACLES applies scene12's hazard-blind `_solid_at` to the hazard-OFF
    arm too and the twin difference cancels).  This gate does not fix that -- it
    refuses to let it stay invisible.
    """
    print("\n[G7] footprint sanity (cells_raw per scene x arm x label set)")
    rows = []
    for p in sorted(glob.glob(os.path.join(LABELS, "*.json"))):
        try:
            lab = json.load(open(p))
        except Exception as e:
            note(f"G7: {os.path.basename(p)} unreadable ({e})")
            continue
        for s in lab.get("scene_footprint", []):
            if not s.get("scene") or s.get("arm") != "on":
                continue
            rows.append((os.path.basename(p)[:-5], s["scene"],
                         s.get("hm_source"), s.get("hm_source_off"),
                         s.get("cells_raw"), s.get("max_diff")))
    if not rows:
        return note("G7: no label file yet -- run eval_cueoff.sh phase 1")
    print(f"  {'label file':52s} {'scene':9s} {'src':6s} {'src_off':8s} "
          f"{'cells_raw':>10s} {'max_diff':>9s}")
    for lf, sc, src, srco, cr, md in rows:
        deg = " <-- DEGENERATE" if (cr is not None and cr < 1000) else ""
        print(f"  {lf[:52]:52s} {sc:9s} {str(src):6s} {str(srco):8s} "
              f"{str(cr):>10s} {str(md):>9s}{deg}")
        if deg:
            note(f"G7 DEGENERATE FOOTPRINT: {lf} / {sc} cells_raw={cr} "
                 f"max_diff={md} -- every recall number for this scene-set is "
                 f"scored against that sliver and MUST carry the caveat "
                 f"(PREREG A1.1). Not a stop condition: the degeneracy is a "
                 f"finding, not a bug in this run.")
    ok("G7", f"{len(rows)} scene-arm footprints tabled")


def g6_ckpt():
    print("\n[G6] frozen checkpoints untouched")
    p = os.path.join(AUDIT, "CKPT_HASHES.json")
    cur = {}
    for f in sorted(glob.glob(CKPT_GLOB)):
        cur[os.path.relpath(f, REPO)] = dict(
            sha256=sha256(f), mtime=round(os.path.getmtime(f), 3),
            bytes=os.path.getsize(f))
    if not cur:
        return fail("G6", f"no checkpoint matched {CKPT_GLOB}")
    if not os.path.isfile(p):
        json.dump(dict(recorded=datetime.datetime.now().isoformat(timespec="seconds"),
                       ckpts=cur), open(p, "w"), indent=1)
        return ok("G6", f"{len(cur)} checkpoint hashes RECORDED (first run) -> "
                        f"{os.path.relpath(p, REPO)}")
    old = json.load(open(p))["ckpts"]
    moved = [k for k in cur if k in old and cur[k]["sha256"] != old[k]["sha256"]]
    if moved:
        fail("G6", f"{len(moved)} checkpoint(s) CHANGED since the snapshot: {moved}")
    else:
        ok("G6", f"{len(cur)} checkpoints unchanged since "
                 f"{json.load(open(p))['recorded']}")


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["pre", "post", "all"], default="all")
    ap.add_argument("--prefix", default="260823_cueoff")
    ap.add_argument("--out", default=os.path.join(AUDIT, "GATES_CUEOFF.md"))
    a = ap.parse_args()

    R = round_dirs(a.prefix)
    print(f"=== gates_cueoff · {datetime.datetime.now():%F %T} ===")
    print(f"rounds found: {sorted(k[0] + '_' + k[1] for k in R)}")
    if not R:
        print("[note] no CUE-OFF round on disk yet -- only G_PREREG and G6 apply")

    g_prereg(R)
    g6_ckpt()
    if a.stage in ("pre", "all"):
        g0_lineage(R)
        g1_smoke(R)
        pose_detail = g3_pose(R)
    else:
        pose_detail = []
    if a.stage in ("post", "all"):
        g2_geometry(R)
        g4_tiers(R)
        g5_armC(R)
        g7_footprint(R)

    print("\n=== SUMMARY ===")
    if FAILS:
        print(f"FAIL {len(FAILS)}:")
        for g, m in FAILS:
            print(f"  - [{g}] {m}")
    else:
        print("all gates PASS")
    if NOTES:
        print(f"notes {len(NOTES)}")

    with open(a.out, "w") as f:
        f.write(f"# GATES_CUEOFF — {datetime.datetime.now():%F %T}\n\n")
        f.write(f"stage `{a.stage}` · rounds "
                f"`{sorted(k[0] + '_' + k[1] for k in R)}`\n\n")
        f.write(f"**{'FAIL ' + str(len(FAILS)) if FAILS else 'ALL GATES PASS'}**\n\n")
        if FAILS:
            f.write("## Failures\n\n")
            for g, m in FAILS:
                f.write(f"- **{g}** — {m}\n")
            f.write("\n")
        if pose_detail:
            f.write("## G3 pose strata (per scene x arm)\n\n```\n")
            f.write("\n".join(pose_detail) + "\n```\n\n")
        if NOTES:
            f.write("## Notes\n\n")
            for m in NOTES:
                f.write(f"- {m}\n")
    print(f"-> {a.out}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
