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
import re
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
MIN_PAIRED_H = 10                 # PREREG sec.4.5-3
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
G7_BANNER = []


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


LABEL_SETS = ("lineage", "twin")


def load_labels(stem, arm, scene=None, lset="lineage"):
    """Label file for one (label set, round stem, arm, scene).

    A2 FIX (D49-2 / R4 F5).  This used to look for `<stem>_<arm>.json`, a name the
    labeller has never written: `eval_cueoff.sh` phase 1 emits
    `<set>__<stem>_<arm>__<scene>.json`.  The lookup therefore missed EVERY label
    file, so G2's polar_gt clause, G4 and G5 reported "labels absent -- skipped"
    and would have kept reporting it however often the battery was re-run.  R4
    read that as a 27-minute timing race; it is a path bug, and the timing is
    incidental.  The old name is still accepted so nothing that used it breaks.
    """
    if scene is not None:
        p = os.path.join(LABELS, f"{lset}__{stem}_{arm}__{scene}.json")
        if os.path.isfile(p):
            return json.load(open(p))
        return None
    p = os.path.join(LABELS, f"{stem}_{arm}.json")
    if not os.path.isfile(p):
        return None
    return json.load(open(p))


def paired_h_frames(la, lb, scene):
    """frame ids that are strict-H in BOTH arms (the JUDGED population, sec.4.2)."""
    out = []
    for fid, fa in la["frames"].items():
        if not fid.startswith("on/") or f"/{scene}/" not in fid:
            continue
        fb = lb["frames"].get(fid)
        if fb is None:
            continue
        if fa.get("tier_strict") == "H" and fb.get("tier_strict") == "H":
            out.append(fid)
    return sorted(out)


# --------------------------------------------------------------------------- gates
DECLARED_TS = re.compile(r"(20\d\d-\d\d-\d\dT\d\d:\d\d(?::\d\d)?)\+09:00")
A2_STEMS = ("260823_cueoff_s20fix",)     # rounds registered by AMENDMENT A2


def _declared_times():
    """(t_original, t_a2) as epoch seconds, parsed from the document's own header
    lines, plus the file mtime.

    Why not just the mtime any more (A2-12).  Until AMENDMENT A2 was appended, the
    mtime WAS the registration time and this gate was a clean mechanical proof that
    no artifact predated it.  Appending A2 -- which is legitimately post-hoc, and
    which had to go next to the document it amends -- moved the mtime to 07:42,
    later than the 05:01 renders of the original rounds, so the naive comparison
    would now FAIL on artifacts that are in fact perfectly in order.  Rewriting the
    mtime back with `touch -d` would make the number say what we want it to say,
    which is the one thing a provenance gate must never do.  Instead the gate reads
    the two timestamps the document DECLARES, checks each round against the one
    that registered it, and states plainly that the mtime form of the proof is no
    longer available for the pre-A2 rounds.
    """
    txt = open(PREREG, encoding="utf-8").read()
    ts = DECLARED_TS.findall(txt)

    def to_epoch(s):
        if len(s) == 16:
            s += ":00"
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").timestamp()
    t0 = to_epoch(ts[0]) if ts else None
    i_a2 = txt.find("AMENDMENT A2")
    t_a2 = None
    if i_a2 >= 0:
        m = DECLARED_TS.search(txt, i_a2)
        if m:
            t_a2 = to_epoch(m.group(1))
    return t0, t_a2, os.path.getmtime(PREREG)


def g_prereg(R):
    print("\n[G_PREREG] pre-registration predates every rendered artifact")
    if not os.path.isfile(PREREG):
        return fail("G_PREREG", f"{PREREG} does not exist")
    t0, t_a2, t_mtime = _declared_times()
    if t0 is None:
        return fail("G_PREREG", "no declared timestamp in PREREG_CUEOFF.md header")
    if t_a2 is not None:
        note("G_PREREG A2-12: PREREG_CUEOFF.md carries a POST-HOC amendment (A2, "
             f"declared {datetime.datetime.fromtimestamp(t_a2):%F %T}), so its mtime "
             f"({datetime.datetime.fromtimestamp(t_mtime):%F %T}) is later than the "
             f"pre-A2 renders and is NO LONGER a usable registration time. This gate "
             f"now compares against the timestamps the document DECLARES, and the "
             f"mtime-based form of the proof is not available for the pre-A2 rounds. "
             f"Independent corroboration on record: red-team R4 verified the "
             f"03:55 prereg / 05:01 render ordering before A2 existed. "
             f"PREREG_HASHES.json freezes the file from here on.")
    bad, n, n_a2 = [], 0, 0
    for (stem, arm), scenes in sorted(R.items()):
        t_ref = t_a2 if (stem in A2_STEMS and t_a2 is not None) else t0
        which = "A2" if t_ref is t_a2 and stem in A2_STEMS else "original"
        for sc, d in sorted(scenes.items()):
            for f in glob.glob(os.path.join(d, "*.png")):
                n += 1
                if which == "A2":
                    n_a2 += 1
                if os.path.getmtime(f) < t_ref:
                    bad.append((os.path.relpath(f, REPO), which))
    if not n:
        return note("G_PREREG: no rendered PNG yet -- vacuously satisfied so far")
    if bad:
        return fail("G_PREREG",
                    f"{len(bad)} artifact(s) PREDATE the registration that covers "
                    f"them -- the registration is not a registration. "
                    f"e.g. {bad[:3]}")
    ok("G_PREREG", f"{n} rendered frames all postdate their registration "
                   f"({n - n_a2} vs the original "
                   f"{datetime.datetime.fromtimestamp(t0):%F %T}"
                   + (f", {n_a2} vs AMENDMENT A2 "
                      f"{datetime.datetime.fromtimestamp(t_a2):%F %T}"
                      if t_a2 is not None else "") + ")")
    # freeze the document from here on, the way G6 freezes the checkpoints
    p = os.path.join(AUDIT, "PREREG_HASHES.json")
    cur = dict(sha256=sha256(PREREG), mtime=round(t_mtime, 3),
               bytes=os.path.getsize(PREREG),
               declared_original=datetime.datetime.fromtimestamp(t0).isoformat(),
               declared_a2=(datetime.datetime.fromtimestamp(t_a2).isoformat()
                            if t_a2 else None))
    if not os.path.isfile(p):
        json.dump(dict(recorded=datetime.datetime.now().isoformat(timespec="seconds"),
                       note="Recorded AFTER amendment A2. It certifies the document "
                            "from this moment on and says nothing about earlier edits.",
                       prereg=cur), open(p, "w"), indent=1)
        note(f"G_PREREG: PREREG sha256 recorded (first run) -> {os.path.basename(p)}")
    else:
        old = json.load(open(p))["prereg"]
        if old["sha256"] != cur["sha256"]:
            fail("G_PREREG", "PREREG_CUEOFF.md CHANGED since the snapshot in "
                             "PREREG_HASHES.json -- an amendment that is not "
                             "declared in the file is not an amendment.")


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
    """G2, at the three scopes A2 separates (D49-2).

    scope 1  heightmap.npy sha256          — global, what the 8 logged FAILs used
    scope 2  polar_gt, ALL on-frames       — scene scope
    scope 3  polar_gt, PAIRED-H frames     — the JUDGED population, which is the
                                             only population PREREG sec.4.5-2 can
                                             actually void, because sec.4.2 judges
                                             on paired-H frames and nothing else
    A global heightmap difference is reported as a BREACH-GLOBAL and then
    adjudicated at scopes 2-3 instead of being inherited from one sibling case
    (the D44 over-generalisation R4 F4 caught).
    """
    print("\n[G2] hazard geometry invariant (heightmap hash · polar_gt scene · "
          "polar_gt judged)")
    for (stem, arm), scenes in sorted(R.items()):
        partner = GEOM_PARTNER.get(arm)
        if not partner or (stem, partner) not in R:
            continue
        for sc, d in sorted(scenes.items()):
            ref = R[(stem, partner)].get(sc)
            if not ref:
                continue
            ha = os.path.join(d, "heightmap.npy")
            hb = os.path.join(ref, "heightmap.npy")
            tag = f"{stem} {sc} {arm} vs {partner}"
            hm_differs = None
            if os.path.isfile(ha) and os.path.isfile(hb):
                hm_differs = sha256(ha) != sha256(hb)
                if hm_differs:
                    fail("G2-hash", f"{tag}: heightmap.npy differs -- clause 2 of "
                                    f"G2 FAILS at global scope. Adjudicated "
                                    f"per-case below and in G2_ADJUDICATION.csv "
                                    f"(D49-2); NOT inherited from a sibling case. "
                                    f"The material question is the polar_gt clause "
                                    f"on the judged population, printed next.")
                else:
                    ok("G2", f"{tag}: heightmap.npy sha256 identical")
            else:
                note(f"G2: {tag}: heightmap.npy missing on one side")
            for lset in LABEL_SETS:
                la = load_labels(stem, arm, sc, lset)
                lb = load_labels(stem, partner, sc, lset)
                if la is None or lb is None:
                    note(f"G2: {tag} [{lset}]: labels absent -- polar_gt deferred")
                    continue
                allf = [f"on/{sc}/{fn}" for fn in sorted(cuts_of(d))]
                diff = [f for f in allf
                        if f in la["frames"] and f in lb["frames"]
                        and la["frames"][f]["polar_gt"] != lb["frames"][f]["polar_gt"]]
                pair = paired_h_frames(lb, la, sc)          # lb = arm A side
                dpair = [f for f in pair
                         if la["frames"][f]["polar_gt"] != lb["frames"][f]["polar_gt"]]
                if dpair:
                    fail("G2", f"{tag} [{lset}]: polar_gt differs on "
                               f"{len(dpair)}/{len(pair)} PAIRED-H frames "
                               f"{[os.path.basename(x) for x in dpair[:3]]} -- the "
                               f"judged population is scored on two different "
                               f"sheets. PREREG sec.4.5-2 VOIDS this pair.")
                elif diff:
                    note(f"G2 SCENE-SCOPE ONLY: {tag} [{lset}]: polar_gt differs on "
                         f"{len(diff)}/{len(allf)} frames "
                         f"{[os.path.basename(x) for x in diff[:3]]}, but 0 of the "
                         f"{len(pair)} PAIRED-H frames. The differing frames are "
                         f"outside the judged population; the paired comparison "
                         f"stands, the scene-level footprint claim does not.")
                else:
                    ok("G2", f"{tag} [{lset}]: polar_gt byte-identical on all "
                             f"{len(allf)} frames (paired-H {len(pair)})")


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
    """G4 = the obligation PREREG sec.4.2 nails down: re-derive the tier PER ARM and
    report the H->E migration count.  Runs per label set, because the two sets
    tier the same frames differently (scene12's on arm is V in `twin`, H in
    `lineage`), and `tier migration | none` printed with no gate behind it was
    exactly R4 F5's complaint."""
    print("\n[G4] 5-category tier re-derivation per arm + H->E migration")
    rows = []
    for lset in LABEL_SETS:
        table = {}
        for (stem, arm), scenes in sorted(R.items()):
            for sc in sorted(scenes):
                lab = load_labels(stem, arm, sc, lset)
                if lab is None:
                    note(f"G4 [{lset}]: labels for {stem}_{arm}/{sc} absent -- skipped")
                    continue
                c = collections.Counter()
                for fid, f in lab["frames"].items():
                    if f"/{sc}/" not in fid or not fid.startswith("on/"):
                        continue
                    c[f.get("tier_strict", "?")] += 1
                table[(stem, sc, arm)] = c
                line = (f"{lset:8s} {stem:15s} {sc:8s} {arm:2s}: " + " · ".join(
                    f"{t} {c.get(t, 0)}" for t in TIERS5))
                rows.append(line)
                ok("G4", line)
        for (stem, sc, arm) in sorted(table):
            if arm == "A" or (stem, sc, "A") not in table:
                continue
            la = load_labels(stem, arm, sc, lset)
            lb = load_labels(stem, "A", sc, lset)
            if la is None or lb is None:
                continue
            mig = collections.Counter()
            for fid, f in lb["frames"].items():
                if f"/{sc}/" not in fid or not fid.startswith("on/"):
                    continue
                g = la["frames"].get(fid)
                if g is None:
                    continue
                t0, t1 = f.get("tier_strict"), g.get("tier_strict")
                if t0 != t1:
                    mig[f"{t0}->{t1}"] += 1
            ph = len(paired_h_frames(lb, la, sc))
            msg = (f"{lset:8s} {stem:15s} {sc:8s} A->{arm:2s}: paired-H {ph}"
                   + (f" · migrations {dict(mig)}" if mig else " · no tier movement"))
            rows.append(msg)
            if mig.get("H->E"):
                note(f"G4 {msg}  -> {mig['H->E']} H->E frames EXCLUDED from the "
                     f"primary readout and reported (CUEOFF_CANDIDATES sec.5-4)")
            else:
                ok("G4", msg)
            if arm in ("B1", "B2", "P") and ph < MIN_PAIRED_H:
                fail("G4", f"[{lset}] {stem} {sc} A/{arm}: paired-H {ph} < "
                           f"{MIN_PAIRED_H} -- PREREG sec.4.5-3 VOIDS this "
                           f"scene-arm (verdict blocks included, not only table rows)")
    return rows


def g5_armC(R):
    print("\n[G5] arm C carries an all-zero polar_gt on every frame")
    for lset in LABEL_SETS:
        for (stem, arm), scenes in sorted(R.items()):
            if arm != "C":
                continue
            for sc in sorted(scenes):
                lab = load_labels(stem, arm, sc, lset)
                if lab is None:
                    note(f"G5 [{lset}]: labels for {stem}_C/{sc} absent -- skipped")
                    continue
                bad = [fid for fid, f in lab["frames"].items()
                       if f"/{sc}/" in fid and fid.startswith("on/")
                       and sum(f["polar_gt"]) > 0]
                n = sum(1 for fid in lab["frames"]
                        if f"/{sc}/" in fid and fid.startswith("on/"))
                if bad:
                    fail("G5", f"[{lset}] {stem} {sc} C: {len(bad)}/{n} frames carry a "
                               f"POSITIVE polar_gt -- the hazard-off surgery left a "
                               f"drop, or the heightmap oracle re-imposed the ON "
                               f"profile. {bad[:3]}")
                elif lset == "twin":
                    note(f"G5 VACUOUS: {lset} {stem} {sc} C: {n}/{n} all-zero GT, but "
                         f"in the `twin` set arm C IS the reference surface, so 0 is "
                         f"constitutive and carries no information (R4 F5).")
                else:
                    ok("G5", f"[{lset}] {stem} {sc} C: {n}/{n} frames all-zero GT "
                             f"-- the hand-patched `_solid_at` (PREREG sec.6.1) did "
                             f"NOT leave a hazard behind")


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
    banner = []
    for lf, sc, src, srco, cr, md in rows:
        arm = lf.rsplit("__", 1)[0].rsplit("_", 1)[-1]
        small = cr is not None and cr < 1000
        # arm C has no hazard: an empty footprint there is the definition of the
        # arm, not a defect.  Separating the two is the whole point of A1.2-3 --
        # the v1 gate lumped 6 constitutive zeros in with the real degeneracy and
        # made the banner unreadable.
        kind = ("BY-DESIGN (hazard-off arm)" if (small and arm == "C")
                else "DEGENERATE" if small else "")
        tagtxt = f" <-- {kind}" if kind else ""
        print(f"  {lf[:52]:52s} {sc:9s} {str(src):6s} {str(srco):8s} "
              f"{str(cr):>10s} {str(md):>9s}{tagtxt}")
        if kind == "DEGENERATE":
            banner.append(f"{lf} ({sc}) cells_raw={cr}")
            note(f"G7 DEGENERATE FOOTPRINT: {lf} / {sc} cells_raw={cr} "
                 f"max_diff={md} -- every recall number for this scene-set is "
                 f"scored against that sliver and MUST carry the caveat "
                 f"(PREREG A1.1). Not a stop condition: the degeneracy is a "
                 f"finding, not a bug in this run.")
    # ---- boost-lineage degeneracy accounting (D49-2 / A1.1) ------------------
    #   The same scene labelled from the two references is the cleanest possible
    #   measurement of how much the missing `fuse_heightmap.py` step costs.
    pair = {}
    for lf, sc, src, srco, cr, md in rows:
        lset, rest = lf.split("__", 1)
        stem_arm = rest.rsplit("__", 1)[0]
        pair.setdefault((stem_arm, sc), {})[lset] = cr
    acct = []
    for (sa, sc), d in sorted(pair.items()):
        if "lineage" in d and "twin" in d and d["lineage"] != d["twin"]:
            r = (d["twin"] / d["lineage"]) if d["lineage"] else float("inf")
            acct.append(f"{sa} {sc}: lineage {d['lineage']} vs twin {d['twin']} "
                        f"cells ({r:.0f}x)")
    if acct:
        note("G7 BOOST-LINEAGE DEGENERACY ACCOUNTING (A1.1): the `lineage` "
             "reference is the boost round, which never ran fuse_heightmap.py; "
             "the `twin` reference is arm C of this round, which did. Where they "
             "disagree, the lineage footprint is the degenerate one: "
             + " · ".join(acct))
    G7_BANNER.extend(banner)
    ok("G7", f"{len(rows)} scene-arm footprints tabled · "
             f"{len(banner)} DEGENERATE (non-C)")


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
    # A2: the default output is NO LONGER GATES_CUEOFF.md.  That file is the
    # preserved v1 record, and an `--out`-less run of this script destroyed the
    # original once already (see its provenance notice).  A tool must not be able
    # to overwrite the record it is superseding by being run with no arguments.
    ap.add_argument("--out", default=os.path.join(AUDIT, "GATES_CUEOFF_v2.md"))
    a = ap.parse_args()

    if os.path.basename(a.out) == "GATES_CUEOFF.md":
        print("[fatal] refusing to write GATES_CUEOFF.md: it is the preserved v1 "
              "record (see its provenance notice). Use --out GATES_CUEOFF_v2.md.")
        return 2
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
    tier_rows = []
    if a.stage in ("post", "all"):
        g2_geometry(R)
        tier_rows = g4_tiers(R)
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
        if G7_BANNER:
            f.write("> ## DEGENERATE FOOTPRINT BANNER (PREREG A1.2-3)\n>\n"
                    "> Every recall number computed against the following "
                    "scene-labelset pairs is scored on a footprint sliver, not on "
                    "the hazard:\n>\n")
            for b in G7_BANNER:
                f.write(f"> - `{b}`\n")
            f.write(">\n")
        if FAILS:
            f.write("## Failures\n\n")
            for g, m in FAILS:
                f.write(f"- **{g}** — {m}\n")
            f.write("\n")
        if pose_detail:
            f.write("## G3 pose strata (per scene x arm)\n\n```\n")
            f.write("\n".join(pose_detail) + "\n```\n\n")
        if tier_rows:
            f.write("## G4 tier re-derivation + migration (per label set)\n\n```\n")
            f.write("\n".join(tier_rows) + "\n```\n\n")
        if NOTES:
            f.write("## Notes\n\n")
            for m in NOTES:
                f.write(f"- {m}\n")
    print(f"-> {a.out}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
